import requests
import matplotlib.pyplot as plt
import seaborn as sns
from os import getenv
from dotenv import load_dotenv
import numpy as np

# Set style
plt.style.use('dark_background')
sns.set_palette("husl")

load_dotenv()
USERNAME = getenv("GITHUB_USER")
TOKEN = getenv("GITHUB_TOKEN") 
EXCLUDE = ["JavaScript", "Hack"]  
MERGE = {"Jupyter Notebook": "Python"}  
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
        lang = MERGE.get(lang, lang)  
        lang_stats[lang] = lang_stats.get(lang, 0) + bytes_of_code

sorted_langs = sorted(lang_stats.items(), key=lambda x: x[1], reverse=True)[:TOP_N]

labels = [lang for lang, _ in sorted_langs]
sizes = [val for _, val in sorted_langs]

total = sum(sizes)
percentages = [round((s / total) * 100, 2) for s in sizes]

# Increased figure size for better spacing
fig, ax = plt.subplots(figsize=(14, 9))

colors = [get_language_color(lang, i) for i, lang in enumerate(labels)]
bars = ax.barh(labels[::-1], percentages[::-1], 
               color=colors[::-1], alpha=0.9, 
               edgecolor='white', linewidth=0.8, height=0.7)

# Customized text on bars
for bar, percentage in zip(bars, percentages[::-1]):
    width = bar.get_width()
    ax.text(width + 0.5, bar.get_y() + bar.get_height()/2,
            f'{percentage:.1f}%', 
            va='center', ha='left', 
            fontsize=12, fontweight='bold',
            color='white')

max_percentage = max(percentages)
ax.set_xlim(0, max_percentage * 1.15)

if max_percentage <= 20:
    tick_interval = 5
elif max_percentage <= 50:
    tick_interval = 10
else:
    tick_interval = 20

xticks = np.arange(0, max_percentage * 1.15, tick_interval)
ax.set_xticks(xticks)
ax.set_xticklabels([f'{int(x)}%' for x in xticks])

# Styling bar chart
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('gray')
ax.spines['bottom'].set_color('gray')
ax.tick_params(colors='white', labelsize=13)
ax.grid(axis='x', alpha=0.3, linestyle='--', linewidth=0.8)

# Add x-axis label for clarity
ax.set_xlabel('Code Percentage (%)', fontsize=14, color='white', fontweight='bold')

fig.suptitle('Top Programming Languages', 
             fontsize=24, fontweight='bold', color='white', y=0.95)

fig.patch.set_facecolor('#0d1117') 

plt.tight_layout()
plt.subplots_adjust(top=0.88, bottom=0.12, left=0.15, right=0.92)

plt.savefig("./src/github_stats.png", 
            dpi=300, bbox_inches='tight', 
            facecolor='#0d1117', edgecolor='none')

plt.show()