#!/usr/bin/env python3
"""Jednorázově: veřejná repa <appka>-releases a vydání .dmg z ~/Desktop/Instalačky pro appky, které na GitHubu ještě nejsou.
Web je ukáže sám po dalším nasazení (waitRelease v site/downloads.json). Znovu spuštěné přeskočí, co už existuje.
Použití: scripts/vydat-mac-dmg.py <pracovní složka>"""
import base64, datetime, hashlib, json, os, shutil, subprocess, sys

OWNER = "bobr700r-droid"
SRC = os.path.expanduser("~/Desktop/Instalačky/")
APPS = [  # název, verze, repo, soubor, architektura, minimální macOS
    ("Animátor", "0.2.2", "animator-releases", "Animator", "universal", "15.0"),
    ("Podkres", "0.9.1", "podkres-releases", "Podkres", "universal", "15.0"),
    ("Plakátník", "0.10.0", "plakatnik-releases", "Plakatnik", "universal", "15.0"),
    ("Tiskárník", "0.5.0", "tiskarnik-releases", "Tiskarnik", "universal", "15.0"),
    ("Kanclík", "0.8.5", "kanclik-releases", "Kanclik", "universal", "15.0"),
    ("Dosah", "0.7.1", "dosah-mac-releases", "Dosah", "arm64", "14.0"),
]

def gh(*a, ok=False):
    r = subprocess.run(("gh",) + a, capture_output=True, text=True)
    if r.returncode and not ok:
        sys.exit(f"Selhalo gh {' '.join(a[:3])}: {r.stderr[:300]}")
    return r.returncode == 0

work = sys.argv[1]
for name, ver, repo, file, arch, mn in APPS:
    full = f"{OWNER}/{repo}"
    if gh("release", "view", f"v{ver}", "--repo", full, ok=True):
        print("už je", repo)
        continue
    src = f"{SRC}{name} {ver}.dmg"
    check = subprocess.run(["spctl", "-a", "-vv", "-t", "open", "--context", "context:primary-signature", src], capture_output=True, text=True)
    if "Notarized Developer ID" not in check.stderr:
        sys.exit(f"Není notarizované: {src}")
    d = f"{work}/{file}"
    os.makedirs(d, exist_ok=True)
    dmg = f"{d}/{file}.dmg"
    shutil.copyfile(src, dmg)
    data = open(dmg, "rb").read()
    with open(f"{d}/latest.json", "w", encoding="utf-8") as f:
        json.dump({"app": name, "platform": "macos", "version": ver,
                   "url": f"https://github.com/{full}/releases/download/v{ver}/{file}.dmg",
                   "sha256": hashlib.sha256(data).hexdigest(), "size": len(data), "minimumSystemVersion": mn, "arch": arch,
                   "published": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}, f, ensure_ascii=False, indent=1)
    if not gh("repo", "view", full, ok=True):
        gh("repo", "create", full, "--public", "--description", f"{name} – vydání")
        readme = f"# {name} – vydání\n\nDeveloper ID verze {name} pro Mac. © 2026 Lukáš Ochrana\n"
        gh("api", "-X", "PUT", f"repos/{full}/contents/README.md", "-f", "message=README", "-f", "content=" + base64.b64encode(readme.encode()).decode())
    gh("release", "create", f"v{ver}", "--repo", full, "--title", f"{name} {ver}", "--latest",
       "--notes", f"{name} {ver} pro macOS {mn} a novější. Podepsáno a notarizováno (Developer ID LUKÁŠ OCHRANA, 525327VFX8).", dmg, f"{d}/latest.json")
    print("vydáno", repo)
