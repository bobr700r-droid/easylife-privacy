# EasyForLife – web a ochrana soukromí

Web **https://easyforlife.cz** (čeština) a **https://easyforlife.eu** (angličtina v kořeni, další jazyky pod `/sk/`, `/de/`, `/es/`, `/pl/`).
Dokud easyforlife.eu nemíří na Fly, běží všechny jazyky na .cz pod `/<lang>/` (přepíná se samo podle DNS, `EU_LIVE` ve `web.py`).

- **Generování:** `python3 build.py` → zásady soukromí do `docs/` + web do `dist/cz` a `dist/eu` (`web.py`, z `../EasyLife/catalog.json` a `site/apps/<id>.json`).
- **Nasazení webu:** `./deploy.sh` (build + `fly deploy`, Fly app `easyforlife-redirect`, `server/server.js` vybírá web podle hostu, `dist/routes.json`).
- **Zásady soukromí** appek: seznam `APPS` v `build.py` → `/<slug>.html` na obou doménách i na GitHub Pages (`docs/`, staré adresy z App Store Connect `bobr700r-droid.github.io/easylife-privacy/<slug>.html` dál fungují). Ostatní stránky na GitHub Pages jen přesměrují na novou adresu.
- **Obsah:** detail appky `site/apps/<id>.json` (popis, funkce, stav `testflight`/`dev`/`live`, účet, zásady, ikona), propojení appek `site/eco.py`, texty webu slovník `T` ve `web.py`. Appka s `locales` v katalogu se ukáže jen v těch jazycích (Kulturník jen cs).
- Ikony se berou z `<App>/…/AppIcon.appiconset` (→ `docs/icons/`), favicon a OG obrázek kreslí `site/art.swift` (`python3 build.py --art`).
