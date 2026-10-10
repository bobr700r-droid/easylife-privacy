# EasyLife – web a ochrana soukromí

Web **https://easyforlife.eu** (GitHub Pages ze složky `docs/`, vlastní doména v `docs/CNAME`). Generuje se celý skriptem `python3 build.py`.

- **Zásady ochrany soukromí** appek: seznam `APPS` v `build.py` → `docs/<slug>.html` (cs/en). Tyto URL jsou v App Store Connect, neměnit. Rozcestník zásad je `docs/soukromi.html`.
- **Web** (úvod + detail `/<id>/` v 6 jazycích: cs výchozí, en, sk, de, es, pl): `web.py` z `../EasyLife/catalog.json`. Obsah detailu appky (popis, funkce, propojení, stav `testflight`/`dev`, screenshoty, barva) je v `site/apps/<id>.json`; chybí-li, ukáže se jen věta z katalogu. Skryté appky: `HIDDEN` ve `web.py`.
- Ikony se berou z `<App>/…/AppIcon.appiconset` (→ `docs/icons/<id>.webp`), screenshoty z cest v `site/apps/<id>.json` (→ `docs/shots/`). Favicon a OG obrázek kreslí `site/art.swift`; přegenerovat: `python3 build.py --art`.
- **easyforlife.cz** → 301 na easyforlife.eu: Fly.io app `easyforlife-redirect` (`redirect/`, nasazení `fly deploy --ha=false`).
