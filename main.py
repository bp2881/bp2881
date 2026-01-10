import requests
import matplotlib.pyplot as plt
import seaborn as sns
from os import getenv
from dotenv import load_dotenv
import numpy as np
from matplotlib.patches import FancyBboxPatch

# Set style
plt.style.use('default')

load_dotenv()
USERNAME = getenv("GITHUB_USER")
TOKEN = getenv("GITHUB_TOKEN") 
EXCLUDE = ["JavaScript", "Hack"]  
#MERGE = {"Jupyter Notebook": "Python"}  
TOP_N = 8

# Language color mapping for popular languages
LANG_COLORS = {
    'Python': '#3776ab',
    'JavaScript': '#f1e05a',
    'C++': '#f34b7d',
    'C': '#555555',
    'PHP': '#4f5d95',
    'HTML': '#e34c26',
    'CSS': '#563d7c',
    'Shell': '#89e051',
    'R': '#198ce7',
    'TypeScript': '#2b7489',
    'Java': '#b07219',
    'Go': '#00ADD8',
    'Rust': '#dea584',
}

def get_language_color(lang, index):
    if lang in LANG_COLORS:
        return LANG_COLORS[lang]
    else:
        colors = sns.color_palette("husl", TOP_N)
        return colors[index % len(colors)]

# Fetch repositories
repos_url = f"https://api.github.com/users/{USERNAME}/repos"
headers = {"Authorization": f"token {TOKEN}"}
repos = requests.get(repos_url, headers=headers).json()

lang_stats = {}
for repo in repos:
    langs = requests.get(repo["languages_url"], headers=headers).json()
    for lang, bytes_of_code in langs.items():
        if lang in EXCLUDE:
            continue
        #lang = MERGE.get(lang, lang)  
        lang_stats[lang] = lang_stats.get(lang, 0) + bytes_of_code

sorted_langs = sorted(lang_stats.items(), key=lambda x: x[1], reverse=True)[:TOP_N]

labels = [lang for lang, _ in sorted_langs]
sizes = [val for _, val in sorted_langs]

total = sum(sizes)
percentages = [round((s / total) * 100, 2) for s in sizes]

# Create figure with Material Dark theme
fig, ax = plt.subplots(figsize=(14, 8), dpi=100)

# GitHub dark theme colors
bg_color = '#0d1117'  # GitHub dark background
surface_color = '#161b22'  # GitHub surface color
text_primary = '#e6edf3'
text_secondary = '#7d8590'

fig.patch.set_facecolor(bg_color)
ax.set_facecolor(bg_color)

colors = [get_language_color(lang, i) for i, lang in enumerate(labels)]

bar_height = 0.65
max_percentage = max(percentages)

for idx, (label, percentage, color) in enumerate(zip(labels[::-1], percentages[::-1], colors[::-1])):
    y_pos = idx
    
    # Main bar - no shadows
    bar = FancyBboxPatch(
        (0, y_pos - bar_height/2),
        percentage,
        bar_height,
        boxstyle="round,pad=0.01",
        facecolor=color,
        edgecolor='none',
        alpha=0.9,
        zorder=2
    )
    ax.add_patch(bar)
    
    # Percentage text
    text_color = 'white' if percentage > 15 else text_primary
    text_x = percentage - 1.5 if percentage > 15 else percentage + 1.5
    text_ha = 'right' if percentage > 15 else 'left'
    
    ax.text(text_x, y_pos, f'{percentage:.1f}%',
            va='center', ha=text_ha, fontsize=12, fontweight='500',
            color=text_color, zorder=3)

ax.set_xlim(-1, max_percentage * 1.12)
ax.set_ylim(-0.8, len(labels) - 0.2)

if max_percentage <= 20:
    tick_interval = 5
elif max_percentage <= 50:
    tick_interval = 10
else:
    tick_interval = 20

xticks = np.arange(0, max_percentage * 1.12, tick_interval)
ax.set_xticks(xticks)
ax.set_xticklabels([f'{int(x)}%' for x in xticks], 
                    fontsize=10, color=text_secondary)
ax.set_yticks(range(len(labels)))
ax.set_yticklabels(labels[::-1], fontsize=12, fontweight='500', color=text_primary)

for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(colors=text_secondary, width=0, length=0, left=False)
ax.grid(axis='x', alpha=0.08, linestyle='-', linewidth=1, color='#30363d', zorder=0)

ax.set_xlabel('Code Distribution (%)', fontsize=12, color=text_secondary, fontweight='500', labelpad=10)
ax.set_ylabel('Language', fontsize=12, color=text_secondary, fontweight='500', labelpad=10)

# Title card - no shadow
title_card = FancyBboxPatch(
    (0.15, 0.94), 0.7, 0.07,
    boxstyle="round,pad=0.01",
    transform=fig.transFigure,
    facecolor=surface_color,
    edgecolor='#30363d',
    linewidth=1,
    alpha=1,
    zorder=100
)
fig.patches.append(title_card)

fig.text(0.5, 0.985, 'Top Programming Languages',
         fontsize=18, fontweight='500', color=text_primary,
         ha='center', va='top', zorder=101)

plt.tight_layout()
plt.subplots_adjust(top=0.91)
plt.savefig("./src/github_stats.png", dpi=300, bbox_inches='tight', 
            facecolor=bg_color, edgecolor='none')


# ------------------- BEGIN: Optimized GitHub activity rings -------------------

import datetime as _dt
import math as _math

def _parse_commit_iso(iso_str):
    return _dt.datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%SZ")

def fetch_commit_stats(username, headers, repos_list):
    commit_days = set()
    total_commits = 0
    last_commit_dt = None
    last_repo = None

    today = _dt.date.today()
    streak_cutoff = today - _dt.timedelta(days=400)  # safety window

    for repo in repos_list:
        # Skip unnecessary repos
        if repo.get("fork") or repo.get("archived") or repo.get("disabled"):
            continue

        owner = repo["owner"]["login"]
        repo_name = repo["name"]
        commits_url = f"https://api.github.com/repos/{owner}/{repo_name}/commits"

        page = 1
        while True:
            params = {"author": username, "per_page": 100, "page": page}
            r = requests.get(commits_url, headers=headers, params=params)
            if r.status_code != 200:
                break

            commits = r.json()
            if not commits:
                break

            stop_repo = False
            for c in commits:
                try:
                    dt = _parse_commit_iso(c["commit"]["author"]["date"])
                except Exception:
                    continue

                commit_date = dt.date()
                if commit_date < streak_cutoff:
                    stop_repo = True
                    break

                commit_days.add(commit_date)
                total_commits += 1

                if last_commit_dt is None or dt > last_commit_dt:
                    last_commit_dt = dt
                    last_repo = repo_name

            if stop_repo or len(commits) < 100:
                break

            page += 1

    return total_commits, commit_days, last_commit_dt, last_repo

def compute_streaks_from_days(days_set):
    if not days_set:
        return 0, 0

    today = _dt.date.today()

    # current streak
    cur = 0
    d = today
    while d in days_set:
        cur += 1
        d -= _dt.timedelta(days=1)

    # max streak
    sorted_days = sorted(days_set)
    max_streak = run = 1
    for i in range(1, len(sorted_days)):
        if (sorted_days[i] - sorted_days[i - 1]).days == 1:
            run += 1
            max_streak = max(max_streak, run)
        else:
            run = 1

    return cur, max_streak

# Fetch + compute
total_commits, commit_days, last_commit_dt, last_repo = fetch_commit_stats(
    USERNAME, headers, repos
)

current_streak, max_streak = compute_streaks_from_days(commit_days)

last_commit_str = (
    last_commit_dt.strftime("%Y-%m-%d %H:%M UTC")
    if last_commit_dt else "No commits"
)
last_repo_str = last_repo or "—"

# ------------------- Visualization -------------------

fig2, axs = plt.subplots(1, 3, figsize=(14, 5), dpi=100, facecolor=bg_color)
plt.subplots_adjust(wspace=0.35)

def draw_donut(ax, value, label, scale_max, color):
    shown = min(value, scale_max)
    remainder = max(scale_max - shown, 0.0)

    ax.pie(
        [shown, remainder],
        startangle=90,
        counterclock=False,
        wedgeprops=dict(width=0.36, edgecolor='none'),
        colors=[color, surface_color],
        normalize=True
    )

    ax.text(0, 0.1, f"{value}", fontsize=20, fontweight='700',
            color=text_primary, ha='center')
    ax.text(0, -0.2, label, fontsize=11,
            color=text_secondary, ha='center')

    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_facecolor(bg_color)

ring_colors = [
    get_language_color('Python', 0),
    get_language_color('TypeScript', 1),
    get_language_color('Go', 2)
]

streak_scale = max(max_streak, 30, current_streak)
draw_donut(axs[0], current_streak, "Current streak (days)", streak_scale, ring_colors[0])
draw_donut(axs[1], max_streak, "Longest streak (days)", streak_scale, ring_colors[1])

if total_commits > 0:
    mag = 10 ** int(_math.floor(_math.log10(total_commits)))
    commit_scale = mag if total_commits <= mag else mag * 10
else:
    commit_scale = 1

draw_donut(axs[2], total_commits, "Total commits", commit_scale, ring_colors[2])

fig2.text(
    0.5, 0.08,
    f"Last commit: {last_repo_str} • {last_commit_str}",
    ha='center', fontsize=11, color=text_primary
)

title_card2 = FancyBboxPatch(
    (0.12, 0.95), 0.76, 0.06,
    boxstyle="round,pad=0.01",
    transform=fig2.transFigure,
    facecolor=surface_color,
    edgecolor='#30363d',
    linewidth=1
)
fig2.patches.append(title_card2)

fig2.text(
    0.5, 0.987, "GitHub Activity Summary",
    fontsize=16, fontweight='600',
    color=text_primary, ha='center', va='top'
)

plt.savefig(
    "./src/github_activity.png",
    dpi=300, bbox_inches='tight',
    facecolor=bg_color, edgecolor='none'
)
plt.close(fig2)

# ------------------- END: Optimized GitHub activity rings -------------------
