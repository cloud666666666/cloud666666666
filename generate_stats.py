#!/usr/bin/env python3
"""Generate dark tech-style GitHub stats SVGs from the GitHub API.
No third-party services. Output: stats.svg + langs.svg
"""
import json, urllib.request, sys

USER = "cloud666666666"
TOKEN = sys.argv[1] if len(sys.argv) > 1 else ""

BG = "#0a0f1a"
FG = "#dbe4f0"
ACCENT = "#00e5ff"
MUTED = "#7d8ea8"

def gh(url):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "stats-gen",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())

# ---- user stats ----
user = gh(f"https://api.github.com/users/{USER}")
repos = gh(f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed")

total_stars = sum(r.get("stargazers_count", 0) for r in repos)
public_repos = user.get("public_repos", 0)
followers = user.get("followers", 0)
following = user.get("following", 0)

# ---- language stats (top 6) ----
langs = {}
for r in repos[:50]:
    lang = r.get("language")
    if lang:
        langs[lang] = langs.get(lang, 0) + 1
top_langs = sorted(langs.items(), key=lambda x: -x[1])[:6]
max_count = top_langs[0][1] if top_langs else 1

def svg_card(w, h, content):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none">
<rect width="{w}" height="{h}" rx="12" fill="{BG}" stroke="#1e2c44"/>
{content}
</svg>'''

# ---- stats card ----
stats_items = [
    ("Repos", public_repos),
    ("Stars", total_stars),
    ("Followers", followers),
    ("Following", following),
]
col_w, x0, y0 = 100, 18, 30
rows = ""
for i, (label, val) in enumerate(stats_items):
    x = x0 + (i % 2) * col_w
    y = y0 + (i // 2) * 56
    rows += f'<text x="{x}" y="{y}" font-family="monospace" font-size="20" fill="{ACCENT}" font-weight="bold">{val}</text>'
    rows += f'<text x="{x}" y="{y+20}" font-family="monospace" font-size="11" fill="{MUTED}">{label}</text>'
stats_svg = svg_card(220, 130, rows)

# ---- langs card ----
bar_x, bar_w = 12, 90
lang_rows = ""
for i, (lang, cnt) in enumerate(top_langs):
    y = 32 + i * 22
    frac = cnt / max_count
    lang_rows += f'<text x="{bar_x}" y="{y}" font-family="monospace" font-size="11" fill="{FG}">{lang}</text>'
    lang_rows += f'<rect x="{bar_x+bar_w}" y="{y-9}" width="{140*frac}" height="8" rx="2" fill="{ACCENT}" opacity="{0.4+0.6*frac}"/>'
    lang_rows += f'<text x="{bar_x+bar_w+148}" y="{y}" font-family="monospace" font-size="10" fill="{MUTED}">{cnt}</text>'
langs_svg = svg_card(300, 30 + len(top_langs) * 22 + 8, lang_rows)

with open("stats.svg", "w") as f:
    f.write(stats_svg)
with open("langs.svg", "w") as f:
    f.write(langs_svg)
print(f"OK: repos={public_repos} stars={total_stars} followers={followers} langs={len(top_langs)}")
