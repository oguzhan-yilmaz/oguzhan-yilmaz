#!/usr/bin/env python3
"""Generate static PNG badges in assets/badges/ (served from raw.githubusercontent.com).

Fetches badge layout from shields.io, bakes to PNG at 3x so the README has
zero third-party image hosts (immune to shields.io downtime / ad blockers).
Values are baked — refresh values here and re-run, or use --live to pull
current values from shields.io first.

    python3 tools/make_badges.py [--live]
"""

import os, re, subprocess, sys, urllib.request

DEF = "style=flat-square"

# (stem, full shields.io URL — escapes: space=__, hyphen in text=--)
BADGES = [
    ("pypi-balcony-v",         "badge/pypi-balcony_v0.3.10-1e90ff"),
    ("pypi-balcony-dm",        "badge/downloads-222%2Fmo-151515"),
    ("pypi-jmespath-v",        "badge/pypi-aws--jmespath--utils_v1.1.0-1e90ff"),
    ("pypi-jmespath-dm",       "badge/downloads-4%2Fmo-151515"),
    ("pypi-ctower-v",          "badge/pypi-ctower_v0.1.0-1e90ff"),
    ("pypi-ctower-dm",         "badge/downloads-29%2Fmo-151515"),
    ("docker-hpa-prescaler",   "badge/docker_pulls-401-2496ed"),
    ("ghcr-balcony",           "badge/ghcr-balcony-1e90ff"),
    ("ghcr-balcony-tf-import", "badge/ghcr-balcony--terraform--import-1e90ff"),
    ("ghcr-argocd-backup",     "badge/ghcr-argocd--backup--s3-1e90ff"),
    ("ghcr-pycrossfade",       "badge/ghcr-pyCrossfade-1e90ff"),
    ("ghcr-steampipe",         "badge/ghcr-steampipe--powerpipe-1e90ff"),
    ("helm-auto-blackbox",     "badge/artifacthub-auto--blackbox--exporter-1fc8f3"),
    ("helm-argocd-backup",     "badge/artifacthub-argocd--backup--s3-1fc8f3"),
    ("helm-steampipe",         "badge/artifacthub-steampipe--powerpipe--kubernetes-1fc8f3"),
    ("helm-crtsh",             "badge/artifacthub-crtsh--kubernetes-1fc8f3"),
    ("helm-hpa-prescaler",     "badge/helm-hpa--prescaler--controller-1fc8f3"),
    ("linkedin",               "badge/LinkedIn-0A66C2"),
]

LIVE_ROUTES = {  # stem -> shields *route* (dynamic) used with --live
    "pypi-balcony-v":      "pypi/v/balcony",
    "pypi-balcony-dm":     "pypi/dm/balcony",
    "pypi-jmespath-v":     "pypi/v/aws-jmespath-utils",
    "pypi-jmespath-dm":    "pypi/dm/aws-jmespath-utils",
    "pypi-ctower-v":       "pypi/v/ctower",
    "pypi-ctower-dm":      "pypi/dm/ctower",
    "docker-hpa-prescaler":"docker/pulls/hepapi/hpa-prescaler-controller",
}

LOGOS = {"pypi": "pypi", "ghcr": "github", "docker": "docker", "linkedin": "linkedin"}

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=15).read()

def live_stems():
    out = {}
    for stem, route in LIVE_ROUTES.items():
        try:
            body = fetch(f"https://img.shields.io/{route}.svg").decode()
            # shields SVG carries the full "label: value" string in <title>
            title = re.search(r"<title>(.*?)</title>", body, re.S)
            if title:
                out[stem] = title.group(1).replace("&amp;", "&")
            else:
                texts = [t for t in dict.fromkeys(re.findall(r"<text[^>]*>(.*?)</text>", body)) if t.strip()]
                if texts:
                    out[stem] = texts[0] if len(texts) == 1 else f"{texts[0]}: {texts[-1]}"
        except Exception as e:
            print(f"  live fail {stem}: {e}")
    return out

def rebuild_url(stem, live_map):
    logo = next((LOGOS[k] for k in LOGOS if stem.startswith(k)), None)
    extra = f"&logo={logo}&logoColor=white" if logo else ""
    if stem in live_map:
        label, _, value = live_map[stem].partition(":")
        label = label.strip().replace("-", "--").replace(" ", "_")
        value = value.strip().replace("-", "--").replace(" ", "_")
        return f"https://img.shields.io/badge/{label}-{value}-1e90ff?{DEF}{extra}", True
    for s, spec in BADGES:
        if s == stem:
            return f"https://img.shields.io/{spec}?{DEF}{extra}", False
    return None, False

def main():
    os.makedirs("assets/badges", exist_ok=True)
    env = dict(os.environ, npm_config_cache=os.path.abspath(".npm-cache"))
    live = live_stems() if "--live" in sys.argv else {}
    fails = []
    for stem, _ in BADGES:
        url, _ = rebuild_url(stem, live)
        if not url: fails.append(stem); continue
        try:
            data = fetch(url)
        except Exception as e:
            print(f"  FETCH FAIL {stem}: {e}"); fails.append(stem); continue
        if b"<text" not in data:
            print(f"  EMPTY {stem}: {url[:70]}"); fails.append(stem); continue
        os.makedirs(".npm-cache/tmp", exist_ok=True)
        tmp = f".npm-cache/tmp/{stem}.svg"
        open(tmp, "wb").write(data)
        out = f"assets/badges/{stem}.png"
        subprocess.run(["npx", "--yes", "@resvg/resvg-js-cli", "--fit-zoom", "3", tmp, out],
                       env=env, capture_output=True, text=True)
        ok = os.path.exists(out) and os.path.getsize(out) > 0
        print(("  ok   " if ok else "  FAIL ") + f"{stem}  ({len(data)}b svg)")
        if not ok: fails.append(stem)
    print("done" + (f" — failures: {fails}" if fails else " — all good"))
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
