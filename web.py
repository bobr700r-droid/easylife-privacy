"""Generuje web EasyLife (easyforlife.eu) z EasyLife/catalog.json a site/apps/<id>.json.

Volá se z build.py: web.build(OUT, APPS, EXTERNAL, OPERATOR). Stránky soukromí (/<slug>.html) generuje build.py,
tady se jen odkazují. Obsah detailů appek je v site/apps/<id>.json (popis, funkce, propojení, stav), texty
webu ve slovníku T. Ikony se kopírují z <App>/…/AppIcon.appiconset do docs/icons/ (sips + cwebp),
favicon a OG obrázek kreslí site/art.swift (jen když chybí; vynutit: python3 build.py --art).
"""
import html, json, os, pathlib, shutil, socket, subprocess, sys

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent                      # EasyLife aplikace/
CATALOG = ROOT / "EasyLife" / "catalog.json"
CONTENT = HERE / "site" / "apps"
DOMAIN = "easyforlife.eu"
BASE = f"https://{DOMAIN}"
LANGS = ["cs", "en", "sk", "de", "es", "pl"]
LANG_NAMES = {"cs": "Čeština", "en": "English", "sk": "Slovenčina", "de": "Deutsch", "es": "Español", "pl": "Polski"}
# Appky, které na webu zatím nemají být (Kulturník zatím k veřejnosti nemíří).
HIDDEN = {"kulturnik"}
# Složka appky, když se nejmenuje jako id v katalogu.
FOLDERS = {"kulturnik": "Vyrazime", "cestovnicek": "Cestovnicek/apple"}
FAMILY_COLORS = {"cestovani": "#2563eb", "foto": "#e8731c", "domacnost": "#0f9a62", "volny-cas": "#8b46d9"}

T = {
  "title": ["EasyLife – malé appky, které zjednodušují život", "EasyLife – small apps that make life easier",
            "EasyLife – malé appky, ktoré zjednodušujú život", "EasyLife – kleine Apps, die das Leben leichter machen",
            "EasyLife – pequeñas apps que facilitan la vida", "EasyLife – małe aplikacje, które ułatwiają życie"],
  "hero": ["Malé appky, které ti zjednoduší život", "Small apps that make life easier",
           "Malé appky, ktoré ti zjednodušia život", "Kleine Apps, die dir das Leben leichter machen",
           "Pequeñas apps que te hacen la vida más fácil", "Małe aplikacje, które ułatwiają życie"],
  "lead": ["EasyLife je rodina malých aplikací pro iPhone. Každá dělá jednu věc pořádně – bez registrace, bez reklam a tvoje data zůstávají u tebe.",
           "EasyLife is a family of small iPhone apps. Each one does one thing well – no sign-up, no ads, and your data stays with you.",
           "EasyLife je rodina malých aplikácií pre iPhone. Každá robí jednu vec poriadne – bez registrácie, bez reklám a tvoje dáta zostávajú u teba.",
           "EasyLife ist eine Familie kleiner iPhone-Apps. Jede macht eine Sache richtig gut – ohne Registrierung, ohne Werbung, und deine Daten bleiben bei dir.",
           "EasyLife es una familia de pequeñas apps para iPhone. Cada una hace una cosa bien: sin registro, sin anuncios y tus datos se quedan contigo.",
           "EasyLife to rodzina małych aplikacji na iPhone’a. Każda robi jedną rzecz porządnie – bez rejestracji, bez reklam, a twoje dane zostają u ciebie."],
  "pills": [["Bez registrace", "Bez reklam", "Data zůstávají u tebe"], ["No sign-up", "No ads", "Your data stays with you"],
            ["Bez registrácie", "Bez reklám", "Dáta zostávajú u teba"], ["Ohne Registrierung", "Ohne Werbung", "Deine Daten bleiben bei dir"],
            ["Sin registro", "Sin anuncios", "Tus datos se quedan contigo"], ["Bez rejestracji", "Bez reklam", "Dane zostają u ciebie"]],
  "apps": ["Aplikace", "Apps", "Aplikácie", "Apps", "Apps", "Aplikacje"],
  "apps_lead": ["Seřazené do rodin. Appky z jedné rodiny se navzájem doplňují.", "Grouped into families. Apps in the same family complement each other.",
                "Zoradené do rodín. Aplikácie z jednej rodiny sa navzájom dopĺňajú.", "In Familien sortiert. Apps einer Familie ergänzen sich gegenseitig.",
                "Agrupadas en familias. Las apps de una misma familia se complementan.", "Pogrupowane w rodziny. Aplikacje z jednej rodziny uzupełniają się nawzajem."],
  "how": ["Jak to děláme", "How we build them", "Ako to robíme", "Unsere Prinzipien", "Cómo las hacemos", "Jak je tworzymy"],
  "principles": [
    [("Žádné účty", "Stáhneš a používáš. Žádné přihlašování, žádné e-maily, žádná hesla."),
     ("Žádné reklamy ani sledování", "Appky neobsahují reklamy ani analytiku a nikomu neprodávají, co v nich děláš."),
     ("Tvoje data jsou tvoje", "Všechno je v telefonu, případně v tvém soukromém iCloudu. My k tomu přístup nemáme."),
     ("Samostatné, ale propojené", "Každá appka funguje sama. Když máš víc appek z jedné rodiny, umí si podat ruku.")],
    [("No accounts", "Download and go. No logins, no emails, no passwords."),
     ("No ads, no tracking", "The apps contain no ads or analytics and never sell what you do in them."),
     ("Your data is yours", "Everything stays on your phone or in your private iCloud. We have no access to it."),
     ("Independent, yet connected", "Every app works on its own. Use several from one family and they work hand in hand.")],
    [("Žiadne účty", "Stiahneš a používaš. Žiadne prihlasovanie, e-maily ani heslá."),
     ("Žiadne reklamy ani sledovanie", "Aplikácie neobsahujú reklamy ani analytiku a nikomu nepredávajú, čo v nich robíš."),
     ("Tvoje dáta sú tvoje", "Všetko je v telefóne, prípadne v tvojom súkromnom iCloude. My k tomu prístup nemáme."),
     ("Samostatné, ale prepojené", "Každá aplikácia funguje sama. Keď máš viac aplikácií z jednej rodiny, vedia si podať ruku.")],
    [("Keine Konten", "Laden und loslegen. Kein Login, keine E-Mails, keine Passwörter."),
     ("Keine Werbung, kein Tracking", "Die Apps enthalten weder Werbung noch Analyse-Tools und verkaufen nicht, was du darin tust."),
     ("Deine Daten gehören dir", "Alles bleibt auf deinem iPhone oder in deiner privaten iCloud. Wir haben keinen Zugriff darauf."),
     ("Eigenständig und doch verbunden", "Jede App funktioniert für sich. Nutzt du mehrere aus einer Familie, arbeiten sie Hand in Hand.")],
    [("Sin cuentas", "Descarga y listo. Sin inicios de sesión, sin correos, sin contraseñas."),
     ("Sin anuncios ni rastreo", "Las apps no tienen anuncios ni analítica y nunca venden lo que haces en ellas."),
     ("Tus datos son tuyos", "Todo se queda en tu teléfono o en tu iCloud privado. Nosotros no tenemos acceso."),
     ("Independientes, pero conectadas", "Cada app funciona por sí sola. Si usas varias de una misma familia, se echan una mano.")],
    [("Bez kont", "Pobierasz i korzystasz. Bez logowania, e-maili i haseł."),
     ("Bez reklam i śledzenia", "Aplikacje nie mają reklam ani analityki i nikomu nie sprzedają tego, co w nich robisz."),
     ("Twoje dane są twoje", "Wszystko zostaje w telefonie lub w twoim prywatnym iCloud. My nie mamy do tego dostępu."),
     ("Niezależne, ale połączone", "Każda aplikacja działa samodzielnie. Jeśli używasz kilku z jednej rodziny, współpracują ze sobą.")]],
  "get": ["Získat", "Get", "Získať", "Laden", "Obtener", "Pobierz"],
  "soon": ["Brzy", "Coming soon", "Čoskoro", "Bald verfügbar", "Próximamente", "Wkrótce"],
  "testflight": ["Beta na TestFlightu", "Beta on TestFlight", "Beta na TestFlighte", "Beta über TestFlight", "Beta en TestFlight", "Beta w TestFlight"],
  "tf_note": ["Aplikace je v beta testu přes TestFlight.", "The app is in beta testing on TestFlight.", "Aplikácia je v beta teste cez TestFlight.",
              "Die App ist in der Beta-Phase über TestFlight.", "La app está en fase beta en TestFlight.", "Aplikacja jest w fazie beta w TestFlight."],
  "dev_note": ["Na aplikaci se pracuje, brzy ji vydáme.", "This app is in development and coming soon.", "Na aplikácii sa pracuje, čoskoro ju vydáme.",
               "An der App wird gearbeitet – sie kommt bald.", "Estamos trabajando en esta app; llegará pronto.", "Aplikacja jest w przygotowaniu i wkrótce się pojawi."],
  "more": ["Více", "Details", "Viac", "Mehr", "Más", "Więcej"],
  "privacy": ["Soukromí", "Privacy", "Súkromie", "Datenschutz", "Privacidad", "Prywatność"],
  "policy": ["Zásady ochrany soukromí", "Privacy Policy", "Zásady ochrany súkromia", "Datenschutzerklärung", "Política de privacidad", "Polityka prywatności"],
  "policy_lang": ["", "", " (v češtine)", " (auf Englisch)", " (en inglés)", " (po angielsku)"],
  "policy_soon": ["Zásady ochrany soukromí zveřejníme s první verzí.", "The privacy policy will be published with the first release.",
                  "Zásady ochrany súkromia zverejníme s prvou verziou.", "Die Datenschutzerklärung erscheint mit der ersten Version.",
                  "La política de privacidad se publicará con la primera versión.", "Polityka prywatności zostanie opublikowana wraz z pierwszą wersją."],
  "features": ["Hlavní funkce", "Key features", "Hlavné funkcie", "Wichtigste Funktionen", "Funciones principales", "Najważniejsze funkcje"],
  "works_with": ["Spolupracuje s", "Works with", "Spolupracuje s", "Arbeitet zusammen mit", "Funciona con", "Współpracuje z"],
  "family_more": ["Další z rodiny {f}", "More from {f}", "Ďalšie z rodiny {f}", "Mehr aus „{f}“", "Más de «{f}»", "Więcej z rodziny „{f}”"],
  "shots": ["Ukázky", "Screenshots", "Ukážky", "Screenshots", "Capturas", "Zrzuty ekranu"],
  "back": ["Všechny aplikace", "All apps", "Všetky aplikácie", "Alle Apps", "Todas las apps", "Wszystkie aplikacje"],
  "operator": ["Provozovatel", "Operator", "Prevádzkovateľ", "Betreiber", "Responsable", "Operator"],
  "made": ["Malé appky pro iPhone, vyrobené v Česku.", "Small iPhone apps, made in Czechia.", "Malé aplikácie pre iPhone, vyrobené v Česku.",
           "Kleine iPhone-Apps, gemacht in Tschechien.", "Pequeñas apps para iPhone, hechas en Chequia.", "Małe aplikacje na iPhone’a, stworzone w Czechach."],
  "lang": ["Jazyk", "Language", "Jazyk", "Sprache", "Idioma", "Język"],
  "skip": ["Přejít na obsah", "Skip to content", "Prejsť na obsah", "Zum Inhalt", "Ir al contenido", "Przejdź do treści"],
}

def t(key, lang):
    return T[key][LANGS.index(lang)]

def esc(s):
    return html.escape(s, quote=True)

def url(lang, slug=None):
    p = "" if lang == "cs" else f"/{lang}"
    return f"{p}/{slug}/" if slug else f"{p}/"

ICONS = {  # 24×24, stroke = currentColor
  "cestovani": '<path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/>',
  "foto": '<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3.5"/>',
  "domacnost": '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V20a1 1 0 0 0 1 1h4v-6h4v6h4a1 1 0 0 0 1-1V9.5"/>',
  "volny-cas": '<path d="M2 4.5h10v5a5 5 0 0 1-10 0z"/><path d="M5 8h.01M9 8h.01M5 11.5a2.5 2.5 0 0 0 4 0"/><path d="M12 9.5h10v5a5 5 0 0 1-10 0"/><path d="M15 13h.01M19 13h.01M15 17.5a2.5 2.5 0 0 1 4 0"/>',
  "user-x": '<circle cx="9" cy="8" r="4"/><path d="M2 21a7 7 0 0 1 14 0"/><path d="m17 8 5 5M22 8l-5 5"/>',
  "eye-off": '<path d="M9.9 4.2A10 10 0 0 1 12 4c7 0 10 8 10 8a17 17 0 0 1-2.2 3.4M6.6 6.6A17 17 0 0 0 2 12s3 8 10 8a9.7 9.7 0 0 0 5.4-1.6"/><path d="M9.9 9.9a3 3 0 0 0 4.2 4.2"/><path d="m2 2 20 20"/>',
  "lock": '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
  "link": '<path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7"/><path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7"/>',
  "check": '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
  "arrow-left": '<path d="M19 12H5M11 18l-6-6 6-6"/>',
  "shield": '<path d="M12 22s8-3.5 8-10V5l-8-3-8 3v7c0 6.5 8 10 8 10z"/>',
}

def icon(name, cls="ico"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>'

LOGO = ('<svg class="logo" viewBox="0 0 32 32" aria-hidden="true"><rect x="2" y="2" width="13" height="13" rx="4" fill="#2563eb"/>'
        '<rect x="17" y="2" width="13" height="13" rx="4" fill="#e8731c"/><rect x="2" y="17" width="13" height="13" rx="4" fill="#0f9a62"/>'
        '<rect x="17" y="17" width="13" height="13" rx="6.5" fill="#8b46d9"/></svg>')

CSS = """
:root{--bg:#f7f6f2;--surface:#fff;--surface2:#efede7;--ink:#17191c;--muted:#5f6670;--line:#e2dfd7;--accent:#2563eb;--shadow:0 1px 2px rgb(20 20 30/.05),0 8px 24px -12px rgb(20 20 30/.18);
--font:-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;--display:-apple-system,BlinkMacSystemFont,"SF Pro Display","Segoe UI",Roboto,sans-serif;color-scheme:light}
@media (prefers-color-scheme:dark){:root{--bg:#111214;--surface:#1b1c20;--surface2:#24252a;--ink:#eceef1;--muted:#a1a7b0;--line:#2e3036;--shadow:0 1px 2px rgb(0 0 0/.3),0 10px 30px -14px rgb(0 0 0/.6);color-scheme:dark}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.55 var(--font);-webkit-font-smoothing:antialiased}
a{color:inherit}img{max-width:100%;display:block}
.wrap{max-width:72rem;margin:0 auto;padding:0 20px}
.skip{position:absolute;left:-999px}.skip:focus{left:16px;top:12px;background:var(--surface);padding:8px 14px;border-radius:10px;z-index:9}
.top{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:18px 0}
.brand{display:flex;align-items:center;gap:10px;text-decoration:none;font:700 1.2rem/1 var(--display);letter-spacing:-.01em}
.logo{width:30px;height:30px}
.langs{display:flex;flex-wrap:wrap;gap:2px;font-size:.78rem;font-weight:600;letter-spacing:.04em}
.langs a{padding:5px 8px;border-radius:8px;text-decoration:none;color:var(--muted)}
.langs a:hover{color:var(--ink);background:var(--surface2)}.langs a[aria-current]{color:var(--ink);background:var(--surface);box-shadow:inset 0 0 0 1px var(--line)}
.hero{display:grid;grid-template-columns:1.15fr .85fr;gap:48px;align-items:center;padding:56px 0 72px}
h1{font:800 clamp(2.3rem,5.6vw,3.9rem)/1.04 var(--display);letter-spacing:-.035em;margin:0 0 20px;text-wrap:balance}
.lead{font-size:clamp(1.08rem,1.6vw,1.25rem);color:var(--muted);max-width:36rem;margin:0 0 26px}
.pills{display:flex;flex-wrap:wrap;gap:8px;padding:0;margin:0;list-style:none}
.pills li{display:flex;align-items:center;gap:7px;background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:7px 14px 7px 10px;font-weight:600;font-size:.92rem}
.pills .ico{width:17px;height:17px;color:#0f9a62}
.collage{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;padding:12px}
.collage img,.collage span{width:100%;height:auto;aspect-ratio:1;border-radius:23%;box-shadow:var(--shadow)}
.collage>*:nth-child(odd){transform:translateY(14px) rotate(-3deg)}.collage>*:nth-child(3n){transform:rotate(4deg)}
section{padding:8px 0 48px}
.sec-head{margin:0 0 22px}.sec-head h2{font:800 clamp(1.7rem,3.4vw,2.3rem)/1.1 var(--display);letter-spacing:-.025em;margin:0 0 6px}.sec-head p{margin:0;color:var(--muted)}
.family{margin:0 0 36px}
.fam-title{display:flex;align-items:center;gap:10px;font:700 1.2rem var(--display);margin:0 0 14px}
.fam-title .ico{width:34px;height:34px;padding:7px;border-radius:10px;color:#fff;background:var(--fc)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:14px}
.card{position:relative;display:flex;flex-direction:column;gap:14px;background:var(--surface);border:1px solid var(--line);border-radius:20px;padding:18px;box-shadow:var(--shadow);transition:transform .15s ease}
.card:hover{transform:translateY(-2px)}
.card-top{display:flex;gap:14px;align-items:flex-start}
.app-icon{flex:none;width:60px;height:60px;border-radius:23%;box-shadow:0 0 0 1px rgb(0 0 0/.06)}
.mark{display:grid;place-items:center;color:#fff;font:800 1.5rem var(--display);background:linear-gradient(145deg,var(--c),color-mix(in srgb,var(--c) 70%,#000))}
.card h3{font:700 1.1rem/1.25 var(--display);margin:2px 0 4px}.card h3 a{text-decoration:none}
.card h3 a::after{content:"";position:absolute;inset:0;border-radius:20px}
.card p{margin:0;color:var(--muted);font-size:.95rem;line-height:1.45}
.actions{position:relative;z-index:1;display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-top:auto}
.btn{display:inline-flex;align-items:center;gap:6px;border-radius:999px;padding:7px 16px;font-weight:700;font-size:.9rem;text-decoration:none;background:var(--c,var(--accent));color:#fff}
.btn:hover{filter:brightness(1.08)}
.chip{display:inline-flex;align-items:center;border-radius:999px;padding:6px 13px;font-weight:600;font-size:.85rem;background:var(--surface2);color:var(--muted)}
.ghost{font-size:.85rem;font-weight:600;color:var(--muted);text-decoration:none;padding:6px 6px}.ghost:hover{color:var(--ink);text-decoration:underline}
.principles{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}
.principle{background:var(--surface);border:1px solid var(--line);border-radius:20px;padding:20px}
.principle .ico{width:40px;height:40px;padding:9px;border-radius:12px;background:var(--surface2)}
.principle h3{font:700 1.05rem var(--display);margin:14px 0 6px}.principle p{margin:0;color:var(--muted);font-size:.95rem}
footer{border-top:1px solid var(--line);margin-top:24px;padding:28px 0 44px;color:var(--muted);font-size:.9rem}
footer .row{display:flex;flex-wrap:wrap;justify-content:space-between;gap:12px 24px}footer p{margin:0 0 6px}footer a{color:var(--ink)}
.back{display:inline-flex;align-items:center;gap:6px;color:var(--muted);text-decoration:none;font-weight:600;font-size:.95rem;margin:8px 0 0}.back:hover{color:var(--ink)}.back .ico{width:18px;height:18px}
.detail{max-width:50rem;padding:28px 0 32px}
.app-hero{display:flex;gap:24px;align-items:center;margin:0 0 30px}
.app-hero .app-icon{width:118px;height:118px;box-shadow:var(--shadow)}.app-hero .mark{font-size:3rem}
.app-hero h1{font-size:clamp(2.1rem,5vw,3.1rem);margin:0 0 6px}
.app-hero .tag{font-size:1.15rem;color:var(--muted);margin:0 0 14px}
.fam-chip{display:inline-flex;align-items:center;gap:6px;font-size:.85rem;font-weight:600;color:var(--c);margin:0 0 8px;text-decoration:none}.fam-chip .ico{width:16px;height:16px}
.desc p{font-size:1.1rem;margin:0 0 14px}
h2.sub{font:800 1.4rem var(--display);letter-spacing:-.015em;margin:34px 0 14px}
.features{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:10px}
.features li{display:flex;gap:10px;align-items:flex-start;background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:12px 14px}
.features .ico{flex:none;width:22px;height:22px;padding:3px;border-radius:50%;background:var(--c);color:#fff;margin-top:1px}
.shots{display:flex;gap:14px;overflow-x:auto;scroll-snap-type:x mandatory;padding:4px 2px 14px}
.shots img{flex:none;width:230px;height:auto;border-radius:22px;border:1px solid var(--line);scroll-snap-align:start}
.links{display:grid;gap:10px}
.link-row{position:relative;display:flex;gap:14px;align-items:center;background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:12px 14px}
.link-row .app-icon{width:48px;height:48px}.link-row b{display:block}.link-row span{color:var(--muted);font-size:.95rem}
.link-row a{text-decoration:none}.link-row a::after{content:"";position:absolute;inset:0}
.note{display:flex;gap:10px;align-items:center;color:var(--muted);font-size:.95rem;margin:16px 0 0}.note .ico{width:18px;height:18px;flex:none}
.note a{color:var(--ink)}
@media (max-width:820px){.hero{grid-template-columns:1fr;gap:28px;padding:28px 0 44px}.collage{grid-template-columns:repeat(6,1fr);gap:10px;padding:0}}
@media (max-width:520px){.top{flex-direction:column;align-items:flex-start;gap:10px}.app-hero{flex-direction:column;align-items:flex-start;gap:16px}.app-hero .app-icon{width:92px;height:92px}.collage{grid-template-columns:repeat(4,1fr)}.collage>*:nth-child(n+9){display:none}}
@media (prefers-reduced-motion:reduce){.card{transition:none}.card:hover{transform:none}}
"""

def head_script(lang, slug):
    """Výběr jazyka: uložená volba, jinak jazyk prohlížeče. Přesměrovává jen z výchozí (české) verze."""
    if lang != "cs":
        return ""
    return ("<script>(function(){var L=" + json.dumps(LANGS) + ",s,p=" + json.dumps(slug or "") + ";"
            "try{s=localStorage.getItem('lang')}catch(e){}"
            "if(!s){var n=navigator.languages||[navigator.language||'cs'];s='en';"
            "for(var i=0;i<n.length;i++){var c=String(n[i]).slice(0,2).toLowerCase();if(L.indexOf(c)>=0){s=c;break}}}"
            "if(s!=='cs'&&L.indexOf(s)>0)location.replace((p?'../':'')+s+'/'+(p?p+'/':'')+location.hash)})()</script>")

FOOT_SCRIPT = ("<script>document.querySelectorAll('.langs a').forEach(function(a){a.addEventListener('click',function(){"
               "try{localStorage.setItem('lang',a.hreflang)}catch(e){}})})</script>")

def page(lang, slug, title, desc, body, operator, relative=True):
    alts = "".join(f'<link rel="alternate" hreflang="{l}" href="{BASE}{url(l, slug)}">' for l in LANGS)
    alts += f'<link rel="alternate" hreflang="x-default" href="{BASE}{url("cs", slug)}">'
    langs = "".join(f'<a href="{url(l, slug)}" hreflang="{l}" lang="{l}" title="{LANG_NAMES[l]}"'
                    f'{" aria-current=\"true\"" if l == lang else ""}>{l.upper()}</a>' for l in LANGS)
    doc = f"""<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
{head_script(lang, slug)}<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{BASE}{url(lang, slug)}">{alts}
<meta property="og:type" content="website"><meta property="og:site_name" content="EasyLife"><meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{BASE}{url(lang, slug)}">
<meta property="og:image" content="{BASE}/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="icon" href="/favicon.png" sizes="64x64" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta name="theme-color" content="#f7f6f2" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#111214" media="(prefers-color-scheme: dark)">
<link rel="stylesheet" href="/site.css"></head>
<body><a class="skip" href="#main">{t("skip", lang)}</a>
<div class="wrap"><header class="top"><a class="brand" href="{url(lang)}">{LOGO}EasyLife</a>
<nav class="langs" aria-label="{t("lang", lang)}">{langs}</nav></header>
<main id="main">{body}</main>
<footer><div class="row"><div><p><b>EasyLife</b> · {t("made", lang)}</p><p>{t("operator", lang)}: {esc(operator[0 if lang in ("cs", "sk") else 1])}</p></div>
<p><a href="/soukromi.html{"" if lang in ("cs", "sk") else "#en"}">{t("policy", lang)}</a></p></div></footer></div>
{FOOT_SCRIPT}</body></html>
"""
    # Relativní odkazy, aby web fungoval i na bobr700r-droid.github.io/easylife-privacy/ (než začne platit doména).
    if relative:
        r = "../" * ((lang != "cs") + (slug is not None)) or "./"
        doc = doc.replace('href="/', f'href="{r}').replace('src="/', f'src="{r}')
    return doc

class Site:
    def __init__(self, out, privacy_apps, external, operator):
        self.out = out
        self.operator = operator
        self.cat = json.loads(CATALOG.read_text(encoding="utf-8"))
        self.families = {f["id"]: f for f in self.cat["families"]}
        self.privacy = {a["slug"]: f"/{a['slug']}.html" for a in privacy_apps}
        self.colors = {a["slug"]: a["color"] for a in privacy_apps}
        self.external = {n: u for n, u in external}
        self.apps = [a for a in self.cat["apps"] if a["id"] not in HIDDEN]
        for a in self.apps:
            f = CONTENT / f"{a['id']}.json"
            a["site"] = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
        self.by_id = {a["id"]: a for a in self.apps}

    # --- obrázky ---
    def icon_source(self, app_id):
        folder = ROOT / FOLDERS.get(app_id, "")
        if app_id not in FOLDERS:
            folder = next((d for d in ROOT.iterdir() if d.is_dir() and d.name.lower() == app_id), None)
        if not folder or not folder.exists():
            return None
        skip = {"DerivedData", "build", "Watch", "node_modules", ".git", "Tests", "server", "Server"}
        for dirpath, dirs, files in os.walk(folder):
            dirs[:] = [d for d in dirs if d not in skip]
            if dirpath.endswith("AppIcon.appiconset"):
                pngs = sorted(f for f in files if f.endswith(".png") and "dark" not in f.lower() and "tint" not in f.lower())
                if pngs:
                    return pathlib.Path(dirpath) / pngs[0]
        return None

    def copy_icons(self):
        d = self.out / "icons"
        d.mkdir(exist_ok=True)
        tmp = d / "_tmp.png"
        for a in self.apps:
            src, dst = self.icon_source(a["id"]), d / f"{a['id']}.webp"
            if src and (not dst.exists() or src.stat().st_mtime > dst.stat().st_mtime):
                subprocess.run(["sips", "-Z", "240", str(src), "--out", str(tmp)], check=True, capture_output=True)
                subprocess.run(["cwebp", "-quiet", "-q", "86", str(tmp), "-o", str(dst)], check=True)
        tmp.unlink(missing_ok=True)

    def copy_shots(self):
        for a in self.apps:
            names = []
            for rel in a["site"].get("screenshots") or []:
                src, dst = ROOT / rel, self.out / "shots" / a["id"] / (pathlib.Path(rel).stem + ".webp")
                if src.exists() and (not dst.exists() or src.stat().st_mtime > dst.stat().st_mtime):
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    tmp = dst.with_suffix(".png")
                    subprocess.run(["sips", "-Z", "920", str(src), "--out", str(tmp)], check=True, capture_output=True)
                    subprocess.run(["cwebp", "-quiet", "-q", "80", str(tmp), "-o", str(dst)], check=True)
                    tmp.unlink()
                if dst.exists():
                    names.append(dst.name)
            a["shots"] = names

    def art(self, force):
        need = [self.out / n for n in ("og.png", "apple-touch-icon.png", "favicon.png")]
        if force or not all(p.exists() for p in need):
            icons = [str(self.out / "icons" / f"{a['id']}.webp") for a in self.apps if (self.out / "icons" / f"{a['id']}.webp").exists()]
            subprocess.run(["swift", str(HERE / "site" / "art.swift"), str(self.out), *icons], check=True)
        (self.out / "favicon.svg").write_text(LOGO.replace('class="logo" ', 'xmlns="http://www.w3.org/2000/svg" '), encoding="utf-8")

    # --- kousky stránek ---
    def color(self, a):
        return a["site"].get("color") or self.colors.get(a["id"]) or FAMILY_COLORS.get(a["family"], "#2563eb")

    def app_icon(self, a, size=60):
        if (self.out / "icons" / f"{a['id']}.webp").exists():
            return f'<img class="app-icon" src="/icons/{a["id"]}.webp" width="{size}" height="{size}" alt="" loading="lazy">'
        return f'<span class="app-icon mark" style="--c:{self.color(a)}" aria-hidden="true">{esc(a["name"][0])}</span>'

    def cta(self, a, lang):
        if a.get("store"):
            return f'<a class="btn" style="--c:{self.color(a)}" href="{esc(a["store"])}">{t("get", lang)}</a>'
        return f'<span class="chip">{t("testflight" if a["site"].get("status") == "testflight" else "soon", lang)}</span>'

    def privacy_link(self, a, lang, cls="ghost"):
        href = self.privacy.get(a["id"]) or self.external.get(a["name"])
        if not href:
            return ""
        if href.startswith("/") and lang not in ("cs", "sk"):
            href += "#en"
        return f'<a class="{cls}" href="{href}">{t("privacy", lang)}</a>'

    def card(self, a, lang):
        return (f'<article class="card"><div class="card-top">{self.app_icon(a)}<div><h3><a href="{url(lang, a["id"])}">{esc(a["name"])}</a></h3>'
                f'<p>{esc(a["tagline"][lang])}</p></div></div><div class="actions">{self.cta(a, lang)}{self.privacy_link(a, lang)}</div></article>')

    def family_apps(self, fid):
        return [a for a in self.apps if a["family"] == fid]

    # --- stránky ---
    def home(self, lang):
        i = LANGS.index(lang)
        checks = [("user-x", 0), ("eye-off", 1), ("lock", 2)]
        pills = "".join(f'<li>{icon(n)}{t("pills", lang)[k]}</li>' for n, k in checks)
        with_icon = [a for a in self.apps if (self.out / "icons" / f"{a['id']}.webp").exists()]
        collage = "".join(self.app_icon(a, 96).replace(' loading="lazy"', "") for a in (with_icon + [a for a in self.apps if a not in with_icon])[:12])
        fams = ""
        for fid, f in self.families.items():
            apps = self.family_apps(fid)
            if not apps:
                continue
            fams += (f'<div class="family" id="{fid}"><h3 class="fam-title" style="--fc:{FAMILY_COLORS.get(fid, "#555")}">{icon(fid)}{esc(f["name"][lang])}</h3>'
                     f'<div class="grid">{"".join(self.card(a, lang) for a in apps)}</div></div>')
        prin = "".join(f'<div class="principle">{icon(n)}<h3>{esc(h)}</h3><p>{esc(p)}</p></div>'
                       for n, (h, p) in zip(("user-x", "eye-off", "lock", "link"), T["principles"][i]))
        body = (f'<div class="hero"><div><h1>{t("hero", lang)}</h1><p class="lead">{t("lead", lang)}</p><ul class="pills">{pills}</ul></div>'
                f'<div class="collage" aria-hidden="true">{collage}</div></div>'
                f'<section id="apps"><div class="sec-head"><h2>{t("apps", lang)}</h2><p>{t("apps_lead", lang)}</p></div>{fams}</section>'
                f'<section><div class="sec-head"><h2>{t("how", lang)}</h2></div><div class="principles">{prin}</div></section>')
        return page(lang, None, t("title", lang), t("lead", lang), body, self.operator)

    def detail(self, a, lang):
        s, c, fam = a["site"], self.color(a), self.families[a["family"]]
        fc = FAMILY_COLORS.get(a["family"], c)
        desc = "".join(f"<p>{esc(p)}</p>" for p in (s.get("description", {}).get(lang) or []))
        feats = s.get("features", {}).get(lang) or []
        web = f'<a class="ghost" href="{esc(s["web"])}">{esc(s["web"].split("//")[-1].rstrip("/"))} ↗</a>' if s.get("web") else ""
        body = f'<a class="back" href="{url(lang)}#{a["family"]}">{icon("arrow-left")}{t("back", lang)}</a><article class="detail" style="--c:{c}">'
        body += (f'<div class="app-hero">{self.app_icon(a, 118).replace(" loading=\"lazy\"", "")}<div>'
                 f'<a class="fam-chip" style="--c:{fc}" href="{url(lang)}#{a["family"]}">{icon(a["family"])}{esc(fam["name"][lang])}</a>'
                 f'<h1>{esc(a["name"])}</h1><p class="tag">{esc(a["tagline"][lang])}</p><div class="actions">{self.cta(a, lang)}{web}</div></div></div>')
        body += f'<div class="desc">{desc}</div>'
        if feats:
            body += f'<h2 class="sub">{t("features", lang)}</h2><ul class="features">' + "".join(f"<li>{icon('check')}<span>{esc(x)}</span></li>" for x in feats) + "</ul>"
        shots = a.get("shots") or []
        if shots:
            body += f'<h2 class="sub">{t("shots", lang)}</h2><div class="shots">' + "".join(
                f'<img src="/shots/{a["id"]}/{esc(x)}" alt="" loading="lazy" width="230" height="500">' for x in shots) + "</div>"
        links = [(self.by_id[l["app"]], l["text"][lang]) for l in s.get("links", []) if l["app"] in self.by_id]
        if links:
            body += f'<h2 class="sub">{t("works_with", lang)}</h2><div class="links">' + "".join(
                f'<div class="link-row">{self.app_icon(o, 48)}<div><a href="{url(lang, o["id"])}"><b>{esc(o["name"])}</b></a><span>{esc(txt)}</span></div></div>'
                for o, txt in links) + "</div>"
        p = self.privacy_link(a, lang, "")
        note = (f'{icon("shield")}<span>{p.replace(">" + t("privacy", lang) + "<", ">" + t("policy", lang) + t("policy_lang", lang) + "<")}</span>'
                if p else f'{icon("shield")}<span>{t("policy_soon", lang)}</span>')
        body += f'<p class="note">{note}</p>'
        if not a.get("store"):
            body += f'<p class="note">{icon("check")}<span>{t("tf_note" if s.get("status") == "testflight" else "dev_note", lang)}</span></p>'
        body += "</article>"
        others = [o for o in self.family_apps(a["family"]) if o["id"] != a["id"]]
        if others:
            body += (f'<section><div class="sec-head"><h2>{t("family_more", lang).format(f=esc(fam["name"][lang]))}</h2></div>'
                     f'<div class="grid">{"".join(self.card(o, lang) for o in others)}</div></section>')
        title = f'{a["name"]} – {a["tagline"][lang].rstrip(".")} | EasyLife'
        return page(lang, a["id"], title, a["tagline"][lang], body, self.operator)

    def write(self, rel, text):
        p = self.out / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def build(self, force_art=False):
        self.copy_icons()
        self.copy_shots()
        self.art(force_art)
        (self.out / "site.css").write_text(CSS.strip() + "\n", encoding="utf-8")
        urls = []
        for lang in LANGS:
            pre = "" if lang == "cs" else f"{lang}/"
            self.write(f"{pre}index.html", self.home(lang))
            urls.append(url(lang))
            for a in self.apps:
                self.write(f"{pre}{a['id']}/index.html", self.detail(a, lang))
                urls.append(url(lang, a["id"]))
        # Smazat stránky appek, které z katalogu zmizely nebo jsou skryté.
        keep = {a["id"] for a in self.apps} | set(LANGS) | {"icons", "shots"}
        for lang in LANGS:
            base = self.out if lang == "cs" else self.out / lang
            for d in base.iterdir():
                if d.is_dir() and d.name not in keep and (d / "index.html").exists():
                    shutil.rmtree(d)
        urls += [p for p in self.privacy.values()]
        self.write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                   + "".join(f"<url><loc>{BASE}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
        self.write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
        # CNAME až když DNS domény míří na GitHub Pages – jinak by staré github.io adresy zásad (App Store Connect)
        # přesměrovaly na doménu, která ještě nefunguje.
        try:
            ips = {i[4][0] for i in socket.getaddrinfo(DOMAIN, 443, socket.AF_INET)}
        except OSError:
            ips = set()
        if ips and all(ip.startswith("185.199.") for ip in ips):
            self.write("CNAME", DOMAIN + "\n")
        elif not (self.out / "CNAME").exists():
            print(f"web: {DOMAIN} ještě nemíří na GitHub Pages – docs/CNAME se nezapisuje")
        nf = ('<div class="detail"><h1>Stránka nenalezena</h1><p class="lead">Tahle stránka neexistuje. · This page doesn’t exist.</p>'
              f'<p><a class="btn" href="/">{t("back", "cs")} · {t("back", "en")}</a></p></div>')
        self.write("404.html", page("cs", None, "404 – EasyLife", "EasyLife", nf, self.operator, relative=False).replace(head_script("cs", None), ""))
        return [a["id"] for a in self.apps]

def build(out, privacy_apps, external, operator):
    if not CATALOG.exists():
        print("web: chybí", CATALOG, "– web se negeneruje")
        return
    print("web", Site(out, privacy_apps, external, operator).build("--art" in sys.argv))
