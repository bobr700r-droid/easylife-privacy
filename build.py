"""Generuje statické stránky se zásadami ochrany soukromí pro EasyLife aplikace (GitHub Pages)."""
import html, pathlib

OUT = pathlib.Path(__file__).parent / "docs"
UPDATED = ("10. října 2026", "October 10, 2026")
OPERATOR = ("Lukáš Ochrana, IČ 76420515, Rápošov 9, 284 01 Kutná Hora",
            "Lukáš Ochrana, Company ID 76420515, Rápošov 9, 284 01 Kutná Hora, Czech Republic")

APPS = [
  dict(slug="smenarna", name="Směnárna", mark="Kč", color="#0b7d70",
    tagline=("Převodník měn podle kurzů ČNB s kalkulačkou, mincovníkem a výdaji z cest.",
             "Currency converter with Czech National Bank rates, calculator, cash counter and trip expenses."),
    summary=("Směnárna nesbírá žádné osobní údaje. Nemá účty, reklamy ani analytiku. Vše, co zapíšeš, zůstává v tvém zařízení.",
             "Směnárna collects no personal data. There are no accounts, ads or analytics. Everything you enter stays on your device."),
    sections=[
      (("Co aplikace ukládá", "What the app stores"),
       ("Oblíbené měny, výpočty, pokladny v mincovníku, cesty a výdaje, upozornění na kurz a poslední stažené kurzy. Data jsou jen v iPhonu (a v Apple Watch, pokud aplikaci používáš i tam) a smazáním aplikace se smažou.",
        "Favourite currencies, calculations, cash-counter wallets, trips and expenses, rate alerts and the latest downloaded rates. Data stays on your iPhone (and Apple Watch if you use the app there) and is deleted with the app.")),
      (("Síť", "Network"),
       ("Aplikace stahuje veřejné kurzy z rozhraní České národní banky (<code>api.cnb.cz</code>). Požadavky neobsahují žádné údaje o tobě.",
        "The app downloads public exchange rates from the Czech National Bank API (<code>api.cnb.cz</code>). Requests contain no information about you.")),
      (("Oprávnění", "Permissions"),
       ("<b>Oznámení</b> jen pro upozornění na kurz, který sis nastavil. <b>Face ID</b> odemyká zamčené pokladny; ověření provádí iOS a aplikace k biometrickým údajům nemá přístup. <b>Siri a Zkratky</b> zpracovává Apple podle svých zásad.",
        "<b>Notifications</b> only for rate alerts you set. <b>Face ID</b> unlocks locked wallets; iOS performs the check and the app never sees biometric data. <b>Siri and Shortcuts</b> are processed by Apple under its own policy.")),
    ]),
  dict(slug="fotoplan", name="Fotoplan", mark="☀", color="#c2671a",
    tagline=("Plánovač fotografování: slunce, měsíc, zlatá a modrá hodinka, oblačnost.",
             "Photo planner: sun, moon, golden and blue hour, cloud cover."),
    summary=("Fotoplan nemá účty, reklamy ani analytiku. Poloha se používá jen k výpočtům a k předpovědi počasí a nikde se neukládá.",
             "Fotoplan has no accounts, ads or analytics. Location is used only for calculations and the weather forecast and is never stored by us."),
    sections=[
      (("Poloha", "Location"),
       ("S tvým svolením aplikace jednou zjistí tvou polohu (jen při používání), aby spočítala časy slunce a měsíce. Poloha se drží jen v paměti a neukládá se.",
        "With your permission the app reads your location once (only while in use) to calculate sun and moon times. It is kept in memory only and never saved.")),
      (("Předpověď oblačnosti", "Cloud forecast"),
       ("Pro předpověď se souřadnice vybraného místa odesílají službě <a href=\"https://open-meteo.com\">Open-Meteo</a> (<code>api.open-meteo.com</code>). Neposílají se žádné identifikátory ani jiné údaje.",
        "For the forecast, the coordinates of the selected place are sent to <a href=\"https://open-meteo.com\">Open-Meteo</a> (<code>api.open-meteo.com</code>). No identifiers or other data are sent.")),
      (("Mapy Apple", "Apple Maps"),
       ("Mapa, vyhledávání míst a zjištění názvu místa využívají služby Apple (MapKit). Hledaný text a souřadnice zpracovává Apple podle svých zásad.",
        "The map, place search and place names use Apple services (MapKit). Search text and coordinates are processed by Apple under its own policy.")),
      (("Kamera", "Camera"),
       ("Kamera slouží jen k živému zobrazení dráhy slunce a měsíce na obloze. Nic se nenahrává ani neukládá.",
        "The camera only shows the sun and moon paths over the live view. Nothing is recorded or saved.")),
      (("Co aplikace ukládá", "What the app stores"),
       ("Uložená místa (název a souřadnice) a nastavení. Jen v zařízení; smazáním aplikace se smažou.",
        "Saved places (name and coordinates) and settings. Only on your device; deleted with the app.")),
    ]),
  dict(slug="vyrovnano", name="Vyrovnáno", mark="⇄", color="#3b5bdb",
    tagline=("Společné výdaje ve skupinách a kdo komu kolik dluží.",
             "Shared expenses in groups and who owes whom."),
    summary=("Vyrovnáno nemá vlastní server, účty, reklamy ani analytiku. Data jsou v tvém zařízení a v tvém iCloudu; sdílená skupina je vidět jen lidem, které do ní pozveš.",
             "Vyrovnáno has no server of its own, no accounts, ads or analytics. Data lives on your device and in your iCloud; a shared group is visible only to people you invite."),
    sections=[
      (("Co aplikace ukládá", "What the app stores"),
       ("Skupiny, členy (jméno, volitelně číslo účtu pro QR Platbu), výdaje a převody, poznámky, fotky účtenek a tvé jméno pro zobrazení.",
        "Groups, members (name, optionally a bank account for QR payments), expenses and transfers, notes, receipt photos and your display name.")),
      (("iCloud a sdílení skupin", "iCloud and shared groups"),
       ("Pokud je zapnutá synchronizace, data se ukládají do tvého iCloudu (Apple CloudKit). Když skupinu sdílíš, všichni pozvaní ji mohou číst a upravovat celou – včetně jmen, čísel účtů, poznámek a fotek účtenek – a vidí iCloud jméno ostatních účastníků. Synchronizaci lze vypnout; aplikace pak funguje jen v zařízení. My k datům v iCloudu přístup nemáme.",
        "If sync is on, data is stored in your iCloud (Apple CloudKit). When you share a group, everyone invited can read and edit all of it, including names, bank accounts, notes and receipt photos, and can see the other participants’ iCloud names. Sync can be turned off so the app works on-device only. We have no access to data in iCloud.")),
      (("Kurzy měn", "Exchange rates"),
       ("Pro přepočet měn se službě <a href=\"https://frankfurter.dev\">Frankfurter</a> (<code>api.frankfurter.dev</code>, kurzy ECB) posílají jen kódy měn a datum.",
        "For currency conversion only currency codes and a date are sent to <a href=\"https://frankfurter.dev\">Frankfurter</a> (<code>api.frankfurter.dev</code>, ECB rates).")),
      (("Kamera, fotky a účtenky", "Camera, photos and receipts"),
       ("Kamera a fotky slouží jen k přiložení nebo naskenování účtenky a QR kódu. Rozpoznání textu a položek účtenky probíhá přímo v zařízení (Apple Vision a Apple Intelligence), nic se kvůli tomu neodesílá.",
        "The camera and photos are used only to attach or scan a receipt or QR code. Text and item recognition runs on-device (Apple Vision and Apple Intelligence); nothing is sent for it.")),
      (("Oznámení", "Notifications"),
       ("Oznámení o nových výdajích od ostatních ve sdílené skupině. Doručuje je Apple (iCloud a APNs).",
        "Notifications about new expenses from others in a shared group, delivered by Apple (iCloud and APNs).")),
    ]),
  dict(slug="salonky", name="Salonky", mark="✈", color="#7048e8",
    tagline=("Karty do letištních salonků, návštěvy a sledování letů.",
             "Airport lounge cards, visits and flight tracking."),
    summary=("Salonky nemají účty, reklamy ani analytiku. Karty, palubenky a návštěvy zůstávají v zařízení. Kvůli upozorněním na změny letu se na náš server posílá jen nezbytné minimum o letu.",
             "Salonky has no accounts, ads or analytics. Cards, boarding passes and visits stay on your device. For flight-change alerts only the minimum flight details are sent to our server."),
    sections=[
      (("Co zůstává v zařízení", "What stays on your device"),
       ("Karty do salonků (název, číslo karty, držitel, vstupy), návštěvy, adresář salonků a palubenky včetně jména cestujícího, rezervačního kódu a čárového kódu. Nikam se neodesílají.",
        "Lounge cards (name, card number, holder, entries), visits, the lounge directory and boarding passes including passenger name, booking reference and barcode. None of this is sent anywhere.")),
      (("Sledování letů", "Flight tracking"),
       ("Když zapneš sledování letu, aplikace pošle na náš server (Fly.io, Frankfurt, EU): číslo letu, datum, letiště odletu a příletu, plánovaný čas, sedadlo, jazyk oznámení a anonymní tokeny pro doručení oznámení a Live Activity. Server podle čísla letu zjišťuje stav u služby FlightAware AeroAPI (USA) a posílá oznámení přes Apple. Záznam se sám smaže 2 dny po přistání nebo zrušení letu, nebo hned, když let v aplikaci smažeš. Jméno ani rezervační kód se na server neposílají.",
        "When you track a flight, the app sends to our server (Fly.io, Frankfurt, EU): flight number, date, departure and arrival airports, scheduled time, seat, notification language and anonymous tokens for notifications and Live Activities. The server looks up the status by flight number with FlightAware AeroAPI (USA) and sends notifications via Apple. The record deletes itself 2 days after landing or cancellation, or immediately when you delete the flight in the app. Your name and booking reference are never sent.")),
      (("Kamera a fotky", "Camera and photos"),
       ("Kamera a výběr fotek slouží jen k načtení čárového kódu palubenky. Rozpoznání probíhá v zařízení.",
        "The camera and photo picker are used only to read a boarding-pass barcode. Recognition runs on-device.")),
      (("Mapy Apple a oznámení", "Apple Maps and notifications"),
       ("Vyhledávání letišť a salonků používá Apple MapKit. Oznámení (připomínky vstupů, změny letu) doručuje Apple.",
        "Airport and lounge search uses Apple MapKit. Notifications (entry reminders, flight changes) are delivered by Apple.")),
    ]),
]

EXTERNAL = [("Kulturník", "https://vyrazime.luksafoto.cz/soukromi")]

COMMON = [
  (("Sdílení dat", "Data sharing"),
   ("Data neprodáváme ani nesdílíme pro reklamu nebo sledování. Obsah opustí aplikaci jinak jen tehdy, když ho sám odešleš tlačítkem Sdílet.",
    "We never sell data or share it for advertising or tracking. Content otherwise leaves the app only when you send it yourself with the Share button.")),
  (("TestFlight", "TestFlight"),
   ("Při testování přes TestFlight může Apple předat vývojáři zpětnou vazbu, kterou sám odešleš, a anonymní hlášení o pádech podle nastavení tvého zařízení.",
    "During TestFlight testing, Apple may pass on feedback you choose to send and anonymous crash reports according to your device settings.")),
  (("Tvoje práva a kontakt", "Your rights and contact"),
   ("Data uložená v zařízení smažeš smazáním aplikace. Provozovatel: {op}. Dotazy posílej přes zpětnou vazbu v TestFlightu nebo na kontakt uvedený u aplikace v App Storu.",
    "Data stored on your device is deleted when you delete the app. Operator: {op}. Send questions via TestFlight feedback or the contact listed for the app in the App Store.")),
]

CSS = """
:root{--bg:#f4f6f5;--surface:#fff;--ink:#16211f;--muted:#5d6b68;--line:#dbe3e0;--accent:#0b7d70;
--display:"Fraunces",Georgia,serif;--body:"Source Sans 3",-apple-system,"Segoe UI",Roboto,sans-serif}
@media (prefers-color-scheme:dark){:root{--bg:#0e1716;--surface:#152220;--ink:#e4eeec;--muted:#9fb1ad;--line:#26393a;color-scheme:dark}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.6 var(--body)}
.wrap{max-width:42rem;margin:0 auto;padding:40px 20px 64px}
header{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:16px;margin-bottom:28px}
.brand{display:flex;align-items:center;gap:12px;text-decoration:none;color:inherit}
.mark{width:44px;height:44px;border-radius:12px;display:grid;place-items:center;color:#fff;font:600 18px var(--display)}
.brand b{font:600 1.35rem var(--display)}
.lang{display:flex;gap:4px;background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:4px}
.lang button{border:0;background:none;color:var(--muted);font:600 .8rem var(--body);letter-spacing:.05em;padding:6px 14px;border-radius:999px;cursor:pointer}
.lang button[aria-pressed=true]{background:var(--accent);color:#fff}
h1{font:600 clamp(1.8rem,5vw,2.4rem)/1.15 var(--display);margin:0 0 6px;text-wrap:balance}
.meta{color:var(--muted);font-size:.9rem;margin:0 0 24px}
.summary{background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:12px;padding:16px 18px;margin-bottom:28px}
h2{font:600 1.15rem var(--display);margin:26px 0 6px}
p{margin:0 0 10px}code{font-size:.88em;background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:1px 6px;overflow-wrap:anywhere}
a{color:var(--accent)}footer{margin-top:40px;padding-top:16px;border-top:1px solid var(--line);color:var(--muted);font-size:.9rem}
ul.apps{list-style:none;padding:0;display:grid;gap:12px}ul.apps a{display:flex;gap:14px;align-items:center;background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:14px 16px;text-decoration:none;color:inherit}
ul.apps small{display:block;color:var(--muted)}
[hidden]{display:none!important}
"""

SCRIPT = """<script>
(function(){var b=document.querySelectorAll('.lang button'),a=document.querySelectorAll('[data-lang]');
function show(l){a.forEach(function(e){e.hidden=e.dataset.lang!==l});b.forEach(function(e){e.setAttribute('aria-pressed',String(e.dataset.for===l))});document.documentElement.lang=l}
b.forEach(function(e){e.addEventListener('click',function(){show(e.dataset.for)})});
var n=(navigator.language||'cs').toLowerCase();show(location.hash==='#en'?'en':location.hash==='#cs'?'cs':(n.indexOf('cs')===0||n.indexOf('sk')===0)?'cs':'en')})();
</script>"""

def page(title, inner, color="#0b7d70", mark="E", brand="EasyLife", home="index.html"):
    return f"""<!doctype html><html lang="cs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600&family=Source+Sans+3:wght@400;600&display=swap">
<style>{CSS}:root{{--accent:{color}}}</style></head><body><div class="wrap">
<header><a class="brand" href="{home}"><span class="mark" style="background:{color}">{mark}</span><b>{html.escape(brand)}</b></a>
<div class="lang" role="group" aria-label="Jazyk / Language"><button type="button" data-for="cs" aria-pressed="true">ČESKY</button><button type="button" data-for="en" aria-pressed="false">ENGLISH</button></div></header>
{inner}<footer>EasyLife · <a href="index.html">všechny aplikace / all apps</a></footer></div>{SCRIPT}</body></html>"""

def app_page(app):
    parts = []
    for i, lang in enumerate(("cs", "en")):
        h1 = ("Zásady ochrany soukromí", "Privacy Policy")[i]
        upd = ("Platné od ", "Effective ")[i] + UPDATED[i]
        body = "".join(f"<h2>{t[i]}</h2><p>{x[i]}</p>" for t, x in app["sections"])
        body += "".join(f"<h2>{t[i]}</h2><p>{x[i].format(op=OPERATOR[i])}</p>" for t, x in COMMON)
        parts.append(f'<article data-lang="{lang}"{" hidden" if lang=="en" else ""}><h1>{h1}</h1><p class="meta">{app["name"]} · {upd}</p>'
                     f'<div class="summary">{app["summary"][i]}</div>{body}</article>')
    return page(f"{app['name']} – soukromí", "".join(parts), app["color"], app["mark"], app["name"])

def index():
    parts = []
    for i, lang in enumerate(("cs", "en")):
        items = "".join(f'<li><a href="{a["slug"]}.html"><span class="mark" style="background:{a["color"]}">{a["mark"]}</span><span><b>{a["name"]}</b><small>{a["tagline"][i]}</small></span></a></li>' for a in APPS)
        items += "".join(f'<li><a href="{u}"><span class="mark" style="background:#555">K</span><span><b>{n}</b><small>{("Zásady na webu aplikace","Policy on the app’s website")[i]}</small></span></a></li>' for n, u in EXTERNAL)
        parts.append(f'<article data-lang="{lang}"{" hidden" if lang=="en" else ""}><h1>{("Ochrana soukromí","Privacy")[i]}</h1>'
                     f'<p class="meta">{("Zásady ochrany soukromí aplikací EasyLife.","Privacy policies of the EasyLife apps.")[i]}</p><ul class="apps">{items}</ul></article>')
    return page("EasyLife – soukromí", "".join(parts))

OUT.mkdir(exist_ok=True)
(OUT / "index.html").write_text(index(), encoding="utf-8")
for app in APPS:
    (OUT / f"{app['slug']}.html").write_text(app_page(app), encoding="utf-8")
(OUT / ".nojekyll").write_text("")
print("ok", [a["slug"] for a in APPS])
