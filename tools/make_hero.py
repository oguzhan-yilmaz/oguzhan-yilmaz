#!/usr/bin/env python3
"""Generate assets/hero-terminal.svg — a static onefetch-style terminal panel.

Numbers are real (pulled from the GitHub API by hand or via:
    curl https://api.github.com/users/oguzhan-yilmaz/repos?per_page=100
). Update the data below, then re-run:  python3 tools/make_hero.py
"""

import html

# ---------- tunable data ----------
OUT = "assets/hero-terminal.svg"

LANGS = [  # (name, %, color) — aggregate over featured repos
    ("Python",       86.9, "#57a8e0"),
    ("Shell",         5.6, "#89e051"),
    ("Dockerfile",   3.2, "#3fb6f4"),
    ("Go Template",  2.8, "#1fc8f3"),
    ("Just",         1.5, "#c9d1d9"),
]

PROJECTS = [  # (name, stars, forks, lang, langcolor, blurb)
    ("pyCrossfade",       "149", "16",  "Python",      "#57a8e0", "beat-matched crossfade engine"),
    ("balcony",           "148",  "4",  "Python",      "#57a8e0", "AWS API → Terraform code"),
    ("argocd-backup-s3", " 16",   "5", "Shell",        "#89e051", "ArgoCD backup CronJob → S3"),
    ("steampipe-powerpipe-kubernetes", "15", "3", "Helm", "#1fc8f3", "Steampipe+Powerpipe on K8s"),
    ("crtsh-kubernetes",  "  5",   "1", "Go · Helm",   "#00ADD8", "cert-transparency exporter"),
]

LOGO = [  # figlet 'small' font, stacked
    r"                   _              ",
    r" ___  __ _ _  _ __| |_  __ _ _ _  ",
    r"/ _ \/ _` | || |_ / ' \/ _` | ' \ ",
    r"\___/\__, |\_,_/__|_||_\__,_|_||_|",
    r"     |___/                         ",
]
LOGO2 = [
    r"      _ _               ",
    r" _  _(_) |_ __  __ _ ___",
    r"| || | | | '  \/ _` |_ /",
    r" \_, |_|_|_|_|_\__,_/__|",
    r" |__/                   ",
]

# ---------- palette ----------
BG      = "#0a0e14"
PANEL   = "#0d1117"
BORDER  = "#1f2733"
FG      = "#c9d1d9"
DIM     = "#6e7b91"
CYAN    = "#56d4dd"
GREEN   = "#7ee787"
YELLOW  = "#ffd866"
ORANGE  = "#ffa657"
RED     = "#ff7b72"
BLUE    = "#61afef"
PURPLE  = "#bc8cff"

FS   = 13.5          # font size
CW   = FS * 0.6     # monospace advance width
LH   = FS * 1.42    # line height
PADX = 26
TITLEBAR = 36

ROWS = [
    # (kind, segments)  segment = (col, color, bold, text)
    ("prompt", [(0, GREEN, True, "oguzhan-yilmaz"), (14, DIM, False, "@"),
                (15, BLUE, True, "github"), (21, DIM, False, " ~/oguzhan-yilmaz"),
                (37, FG, False, " % "), (41, FG, False, "onefetch")]),
    ("gap", []),
    # logo block rows (left) + info block rows (right)
    ("info", [(0, CYAN, True, LOGO[0]), (38, FG, True, "oguzhan-yilmaz")]),
    ("info", [(0, CYAN, True, LOGO[1]), (38, DIM, False, "-" * 14)]),
    ("info", [(0, CYAN, True, LOGO[2]), (38, CYAN, True, "  focus "),
              (46, FG, False, "Cloud · Kubernetes · GitOps")]),
    ("info", [(0, CYAN, True, LOGO[3]), (38, CYAN, True, "  certs "),
              (46, ORANGE, False, "AWS SA Pro · AWS SA · CKA")]),
    ("info", [(0, CYAN, True, LOGO[4]), (38, CYAN, True, "  since "),
              (46, FG, False, "2016 → now")]),
    ("info", [(38, YELLOW, True, "  stars "), (46, YELLOW, False, "427"),
              (53, DIM, False, "·"), (55, FG, True, "forks "),
              (61, FG, False, "33"), (65, DIM, False, "·"),
              (67, FG, True, "repos "), (74, FG, False, "30/41")]),
    ("info", [(38, PURPLE, True, "  langs "), (46, FG, False, "Python · Shell · Go · Helm · HCL")]),
    ("gap", []),
]

# language stacked bar (60 blocks)
BARW = 60
def bar_rows():
    out, x = [], 0
    for i, (name, pct, color) in enumerate(LANGS):
        n = max(1, round(pct / 100 * BARW)) if i < len(LANGS) - 1 else BARW - x
        out.append((x, color, "█" * n))
        x += n
    return out

def legend():
    parts, col = [], 0
    for name, pct, color in LANGS:
        t = f"● {name} {pct}%"
        parts.append((col, color, False, t))
        col += len(t) + 3
    return parts

def project_rows():
    # fixed columns: name pad 32, stars, forks, lang pad 12, blurb
    out = []
    for name, st, fk, lang, lc, blurb in PROJECTS:
        out.append([
            (0,  BLUE,   True, name.ljust(30)),
            (31, YELLOW, False, f"★{st}"),
            (37, DIM,    False, "⑂" + fk),
            (43, lc,     False, lang.ljust(10)),
            (55, DIM,    False, blurb),
        ])
    return out

def tspan(col, color, bold, text):
    t = html.escape(str(text)).replace(" ", "&#160;")
    w = ' font-weight="bold"' if bold else ""
    f = ' filter="url(#glow)"' if color == CYAN and ("|" in str(text) or "_" in str(text) or "\\" in str(text) or "/" in str(text)) else ""
    return f'<tspan x="{PADX + col * CW:.1f}" fill="{color}"{w}{f}>{t}</tspan>'

def line_svg(y, segs):
    tspans = "".join(tspan(c, col, b, txt) for c, col, b, txt in segs)
    return f'  <text y="{y:.1f}" xml:space="preserve">{tspans}</text>\n'

# ---------- assemble ----------
body_rows = list(ROWS)
content = ""
y = TITLEBAR + PADX
for kind, segs in body_rows:
    if kind == "gap":
        y += LH
        continue
    content += line_svg(y, segs)
    y += LH

# languages bar + legend
bar = bar_rows()
segs = [(0, DIM, True, "langs ")] + [(6 + x, c, False, txt) for x, c, txt in bar]
content += line_svg(y, segs)
y += LH
content += line_svg(y, legend())
y += LH * 1.4

# projects
content += line_svg(y, [(0, GREEN, True, "~/projects"), (10, FG, True, ""),
                        (10, DIM, False, "── ls --top-starred")])
y += LH
content += line_svg(y, [(0, DIM, False, "─" * 84)])
y += LH
for segs in project_rows():
    content += line_svg(y, segs)
    y += LH
y += LH * 0.4
content += line_svg(y, [(0, GREEN, True, "oguzhan-yilmaz"), (14, DIM, False, "@"),
                        (15, BLUE, True, "github"), (21, DIM, False, " ~/oguzhan-yilmaz"),
                        (37, FG, False, " % "),
                        (41, FG, False, "")])
content += f'  <rect x="{PADX + 41 * CW:.1f}" y="{y - FS + 2:.1f}" width="{CW:.1f}" height="{FS + 3:.1f}" fill="{GREEN}" opacity="0.9"/>\n'

H = int(y + LH + PADX)
W = PADX * 2 + 84 * CW

scan = ""
for i in range(int(H / 4)):
    scan += f'<rect x="0" y="{i * 4}" width="{W:.0f}" height="1" fill="#000" opacity="0.10"/>'

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H}" viewBox="0 0 {W:.0f} {H}" font-family="ui-monospace, 'SF Mono', Menlo, Consolas, monospace" font-size="{FS}">
  <defs>
    <linearGradient id="tb" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#141a24"/><stop offset="1" stop-color="#0f141c"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="0" stdDeviation="2.2" flood-color="{CYAN}" flood-opacity="0.45"/>
    </filter>
  </defs>
  <rect width="{W:.0f}" height="{H}" rx="10" fill="{BG}"/>
  <rect x="0.5" y="0.5" width="{W - 1:.0f}" height="{H - 1}" rx="10" fill="none" stroke="{BORDER}"/>
  <rect width="{W:.0f}" height="{TITLEBAR}" rx="10" fill="url(#tb)"/>
  <rect x="0" y="{TITLEBAR - 8}" width="{W:.0f}" height="8" fill="url(#tb)"/>
  <line x1="0" y1="{TITLEBAR}" x2="{W:.0f}" y2="{TITLEBAR}" stroke="{BORDER}"/>
  <circle cx="22" cy="18" r="6" fill="#ff5f57"/>
  <circle cx="42" cy="18" r="6" fill="#febc2e"/>
  <circle cx="62" cy="18" r="6" fill="#28c840"/>
  <text x="{W / 2:.0f}" y="22" text-anchor="middle" fill="{DIM}" font-size="12">oguzhan-yilmaz — onefetch</text>
  <g filter="none">
{content}  </g>
  {scan}
</svg>"""

with open(OUT, "w") as f:
    f.write(svg)
print(f"wrote {OUT} ({W:.0f}x{H})")
