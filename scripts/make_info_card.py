import calendar
import html
import json
import os
import urllib.request
from datetime import datetime


def find_project_root():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [script_dir, os.getcwd(), os.path.abspath(os.path.join(script_dir, ".."))]
    for candidate in candidates:
        if os.path.isdir(candidate):
            if os.path.isdir(os.path.join(candidate, "scripts")) and os.path.isfile(os.path.join(candidate, "README.md")):
                return os.path.abspath(candidate)
    return os.path.abspath(os.path.join(script_dir, ".."))


ROOT = find_project_root()
OUT = os.environ.get("INFO_CARD_OUTPUT") or os.path.join(ROOT, "info-card.svg")
STATIC = os.environ.get("STATIC", "1").lower() not in {"0", "false", "no", "off"}
USERNAME = os.environ.get("GH_PROFILE_USER", "Darpan-Maurya")
CONTRIBUTIONS_PATH = os.path.join(ROOT, "data", "contributions.json")

# --- Dynamic Inputs (Passed from orchestrator or defaults) ---
BIRTH_DATE = datetime(2004, 3, 20)


def format_int(value):
    return f"{int(value):,}"


def env_value(name):
    value = os.environ.get(name)
    return value.strip() if value and value.strip() else None


def read_contribution_data():
    try:
        with open(CONTRIBUTIONS_PATH) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError, TypeError):
        return {}


def github_request(url):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "profile-readme-bot/1.0",
    }
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp), resp.headers


def fetch_repo_count():
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        url = "https://api.github.com/user/repos?affiliation=owner&per_page=100&type=all"
        count = 0
        while url:
            data, headers = github_request(url)
            count += len(data)
            link = headers.get("Link", "")
            next_url = None
            for part in link.split(","):
                if 'rel="next"' in part:
                    next_url = part[part.find("<") + 1:part.find(">")]
                    break
            url = next_url
        return count

    data, _ = github_request(f"https://api.github.com/users/{USERNAME}")
    return data.get("public_repos")


def contribution_stat(key, default=0):
    return CONTRIBUTION_DATA.get(key, default)


CONTRIBUTION_DATA = read_contribution_data()
try:
    REPO_COUNT = fetch_repo_count()
except (OSError, json.JSONDecodeError, TypeError):
    REPO_COUNT = None

GH_REPOS = env_value("GH_STAT_REPOS") or format_int(REPO_COUNT or 42)
GH_CONTRIBS = (
    env_value("GH_STAT_CONTRIBS")
    or env_value("GH_STAT_COMMITS")
    or format_int(contribution_stat("total_contributions"))
)
GH_LOC = env_value("GH_STAT_LOC") or "~250k"


def calculate_age_formatted():
    now = datetime.now()
    years = now.year - BIRTH_DATE.year
    months = now.month - BIRTH_DATE.month
    days = now.day - BIRTH_DATE.day
    if days < 0:
        months -= 1
        prev_month = now.month - 1 if now.month > 1 else 12
        prev_year = now.year if now.month > 1 else now.year - 1
        days += calendar.monthrange(prev_year, prev_month)[1]
    if months < 0:
        years -= 1
        months += 12
    return f"{years}y {months}m {days}d"

W, H = 480, 440
PAD = 20
TITLEBAR_H = 30
KEY_X, VAL_X, LINE_H = PAD, PAD + 92, 20.5

BG, BG2, FRAME = "#0d1117", "#111722", "#30363d"
MUTED, INK, KEY = "#7d8590", "#c9d1d9", "#ffa657"
SECTION, GREEN, ACCENT = "#58a6ff", "#3fb950", "#22d3ee"

HOST = "@darpan"
AGE_STRING = calculate_age_formatted()

ROWS = [
    ("host",),
    ("kv", "Now", "Seeking role @ Company"),
    ("kv", "Uptime", f"({AGE_STRING})"),
    ("kv", "Edu", "CSE & ML-Hons, IIIT Pune '26"),
    ("gap",),
    ("sec", "Contact"),
    ("kv", "Email", "darpanmaurya2003@gmail.com"),
    ("kv", "Linkedin", "linkedin.com/in/darpan-maurya"),
    ("kv", "Portfolio", "portfolio-5dzp.onrender.com"),
    ("gap",),
    ("sec", "Stack"),
    ("kv", "Frontend", "React, Next.js, TypeScript"),
    ("kv", "Backend", "Node, Python (Flask, FastAPI)"),
    ("kv", "AI / ML", "LangChain, PyTorch, Gemini"),
    ("kv", "Cloud", "AWS, Docker"),
    ("gap",),
    ("sec", "GitHub Stats"),
    ("kv", "Repos", f"{GH_REPOS} Total"),
    ("kv", "Contribs", f"{GH_CONTRIBS} (Past Year)"),
    ("kv", "LOC", f"{GH_LOC} lines"),
    ("gap",),
]

def esc(s): return html.escape(s)
def wrap_link(content, url):
    if url.startswith("http"):
        return f'<a href="{url}" target="_blank" style="cursor:pointer">{content}</a>'
    return content

def rise(inner, i):
    if STATIC: return f"<g>{inner}</g>"
    delay = 0.15 + i * 0.05
    return (f'<g opacity="0" transform="translate(0,5)">{inner}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.4s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" '
            f'begin="{delay:.2f}s" dur="0.4s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/></g>')

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="monospace">',
    '<style>text { fill: #c9d1d9; font-size: 12.5px; } .key { fill: #ffa657; font-weight: 700; } .sec { fill: #58a6ff; font-weight: 700; } a:hover text { fill: #22d3ee !important; text-decoration: underline; }</style>',
    '<defs><linearGradient id="ibg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#111722"/><stop offset="1" stop-color="#0d1117"/></linearGradient></defs>',
    f'<rect width="{W}" height="{H}" rx="12" fill="url(#ibg)"/>',
    f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}"/>',
    f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>'
]
for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
parts.append(f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" text-anchor="middle">{esc(HOST)}@github: ~$ neofetch</text>')

y = TITLEBAR_H + 30
for i, row in enumerate(ROWS):
    kind = row[0]
    if kind == "gap": y += LINE_H * 0.5; continue
    if kind == "host":
        inner = f'<text x="{KEY_X}" y="{y}" font-size="14" font-weight="700"><tspan fill="{GREEN}">{esc(HOST)}</tspan><tspan fill="{MUTED}">@</tspan><tspan fill="{ACCENT}">github</tspan></text>'
    elif kind == "sec":
        inner = f'<text x="{KEY_X}" y="{y}" fill="{SECTION}" font-size="12.5" font-weight="700">— {esc(row[1])}</text>'
    elif kind == "kv":
        val_text = f'<text x="{VAL_X}" y="{y}">{esc(row[2])}</text>'
        val_field = wrap_link(val_text, row[2])
        inner = f'<text x="{KEY_X}" y="{y}" fill="{KEY}" font-size="12.5" font-weight="700">{esc(row[1])}</text><text x="{VAL_X}" y="{y}" fill="{INK}" font-size="12.5">{esc(row[2])}</text>'
    elif kind == "bul":
        inner = f'<circle cx="{KEY_X+3}" cy="{y-4}" r="2.5" fill="{GREEN}"/><text x="{KEY_X+14}" y="{y}" fill="{INK}" font-size="12.5">{esc(row[1])}</text>'
    parts.append(rise(inner, i))
    y += LINE_H

parts.append("</svg>")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f: f.write("".join(parts))
print(f"Updated info card saved to {OUT}. Stats: {GH_REPOS} repos, {GH_CONTRIBS} yearly contributions.")
