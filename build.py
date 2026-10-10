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
  dict(slug="fotoplan", name="FotoPlán", mark="☀", color="#c2671a",
    tagline=("Plánovač fotografování: slunce, měsíc, zlatá a modrá hodinka, oblačnost.",
             "Photo planner: sun, moon, golden and blue hour, cloud cover."),
    summary=("FotoPlán nemá účty, reklamy ani analytiku. Poloha a uložená místa se ukládají jen v telefonu (i pro widgety) a nikam se neposílají – kromě souřadnic pro předpověď do Open-Meteo.",
             "FotoPlán has no accounts, ads or analytics. Your location and saved places are stored only on your phone (including for widgets) and are never sent anywhere, except coordinates sent to Open-Meteo for the forecast."),
    sections=[
      (("Poloha", "Location"),
       ("S tvým svolením aplikace zjistí tvou polohu (jen při používání), aby spočítala časy slunce a měsíce. Když je vybraná aktuální poloha, uloží se v telefonu (souřadnice a název místa), aby z ní mohly počítat i widgety na ploše a zamčené obrazovce.",
        "With your permission the app reads your location (only while in use) to calculate sun and moon times. When your current location is selected, it is stored on the phone (coordinates and place name) so home and lock screen widgets can use it too.")),
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
       ("Vybrané místo, uložená místa (název a souřadnice), poslední stažená předpověď oblačnosti a nastavení. Jen v zařízení; smazáním aplikace se smažou.",
        "The selected place, saved places (name and coordinates), the last downloaded cloud forecast and settings. Only on your device; deleted with the app.")),
    ]),
  dict(slug="vyrovnano", name="Vyrovnáno", mark="⇄", color="#3b5bdb",
    tagline=("Společné výdaje ve skupinách a kdo komu kolik dluží.",
             "Shared expenses in groups and who owes whom."),
    summary=("Vyrovnáno nemá vlastní server, účty, reklamy ani analytiku. Data jsou v tvém zařízení a v tvém iCloudu; sdílená skupina je vidět jen lidem, které do ní pozveš.",
             "Vyrovnáno has no server of its own, no accounts, ads or analytics. Data lives on your device and in your iCloud; a shared group is visible only to people you invite."),
    sections=[
      (("Co aplikace ukládá", "What the app stores"),
       ("Skupiny, členy (jméno, volitelně číslo účtu pro QR Platbu), výdaje a převody, poznámky, fotky účtenek, historii změn (kdo co přidal nebo upravil) a tvé jméno pro zobrazení.",
        "Groups, members (name, optionally a bank account for QR payments), expenses and transfers, notes, receipt photos, an activity log (who added or changed what) and your display name.")),
      (("iCloud a sdílení skupin", "iCloud and shared groups"),
       ("Pokud je zapnutá synchronizace, data se ukládají do tvého iCloudu (Apple CloudKit). Když skupinu sdílíš, všichni pozvaní ji mohou číst a upravovat celou – včetně jmen, čísel účtů, poznámek, fotek účtenek a historie změn – a vidí iCloud jméno ostatních účastníků. Synchronizaci lze vypnout; aplikace pak funguje jen v zařízení. My k datům v iCloudu přístup nemáme.",
        "If sync is on, data is stored in your iCloud (Apple CloudKit). When you share a group, everyone invited can read and edit all of it, including names, bank accounts, notes, receipt photos and the activity log, and can see the other participants’ iCloud names. Sync can be turned off so the app works on-device only. We have no access to data in iCloud.")),
      (("Kurzy měn", "Exchange rates"),
       ("Kurzy pro přepočet výdajů v cizí měně se stahují z České národní banky (<code>api.cnb.cz</code>) – posílá se jen datum výdaje. Měny, které ČNB nevyhlašuje, se záložně přepočtou kurzem ECB přes službu <a href=\"https://frankfurter.dev\">Frankfurter</a> (<code>api.frankfurter.dev</code>) – posílají se jen kódy měn a datum.",
        "Rates for converting foreign-currency expenses are downloaded from the Czech National Bank (<code>api.cnb.cz</code>); only the expense date is sent. For currencies the CNB doesn’t publish, the ECB rate is used as a fallback via <a href=\"https://frankfurter.dev\">Frankfurter</a> (<code>api.frankfurter.dev</code>); only currency codes and a date are sent.")),
      (("Kamera, fotky a účtenky", "Camera, photos and receipts"),
       ("Kamera a fotky slouží jen k přiložení nebo naskenování účtenky a QR kódu. Rozpoznání textu a položek účtenky probíhá přímo v zařízení (Apple Vision a Apple Intelligence), nic se kvůli tomu neodesílá.",
        "The camera and photos are used only to attach or scan a receipt or QR code. Text and item recognition runs on-device (Apple Vision and Apple Intelligence); nothing is sent for it.")),
      (("Oznámení", "Notifications"),
       ("Oznámení o nových výdajích od ostatních ve sdílené skupině. Aplikace je vytváří přímo v zařízení po synchronizaci přes iCloud; o změnách ji informuje Apple (APNs).",
        "Notifications about new expenses from others in a shared group. The app creates them on-device after syncing via iCloud; Apple (APNs) tells it about changes.")),
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
  dict(slug="jidelnik", name="Jídelník", mark="🍽", color="#e85d2e",
    tagline=("Hledání restaurací v okolí i kdekoli jinde podle hodnocení, kuchyně a služeb.",
             "Find restaurants nearby or anywhere by rating, cuisine and services."),
    summary=("Jídelník nemá účty, reklamy ani analytiku. Oblíbené podniky, navštívená místa, hodnocení a poznámky zůstávají v zařízení. Kvůli hledání se na náš server posílá jen místo, kde hledáš, a zvolené filtry.",
             "Jídelník has no accounts, ads or analytics. Favorites, visited places, ratings and notes stay on your device. For searching, only the location you search around and your filters are sent to our server."),
    sections=[
      (("Co zůstává v zařízení", "What stays on your device"),
       ("Oblíbené podniky, seznam „Chci zkusit“, vyzkoušená místa, vlastní hodnocení, poznámky, vlastní podniky včetně fotek, zapsané rezervace, nedávná místa hledání a nastavení filtrů. Neodesílají se nám – synchronizují se jen přes tvůj iCloud (viz níže).",
        "Favorite places, the “Want to try” list, tried places, your own ratings, notes, your own places including photos, noted reservations, recent search locations and filter settings. None of this is sent to us – it only syncs via your iCloud (see below).")),
      (("Fotky a kalendář", "Photos and calendar"),
       ("Fotku k vlastnímu podniku vybíráš systémovým výběrem; aplikace dostane jen tu jednu fotku a uloží ji v zařízení. Rezervaci do kalendáře přidáváš sám v systémovém formuláři – aplikace nemá přístup ke tvému kalendáři.",
        "You pick a photo for your own place with the system picker; the app only receives that one photo and stores it on your device. You add a reservation to your calendar yourself in the system form – the app has no access to your calendar.")),
      (("Hledání podniků", "Searching for places"),
       ("Při hledání aplikace pošle na náš server (Fly.io, Frankfurt, EU) souřadnice středu hledání (tvoje poloha nebo zvolené místo), okruh, hledaný text, filtry a jazyk. Server se dotáže služby Google Places (Google, USA) a výsledky krátce (nejvýš 24 hodin) drží v paměti, aby se stejné dotazy neopakovaly. Nic se neukládá k žádné identitě; server si nevede historii hledání ani polohy.",
        "When you search, the app sends to our server (Fly.io, Frankfurt, EU) the coordinates of the search centre (your location or a chosen place), the radius, search text, filters and language. The server queries Google Places (Google, USA) and keeps results in memory briefly (at most 24 hours) to avoid repeating identical queries. Nothing is tied to any identity; the server keeps no search or location history.")),
      (("Poloha", "Location"),
       ("Poloha se zjišťuje při používání aplikace na hledání podniků v okolí. Místo ní můžeš zadat libovolnou adresu; našeptávání adres zajišťuje Apple MapKit. Pokud zapneš upozornění u podniků z „Chci zkusit“, hlídá iOS v zařízení příchod k těmto místům (poloha „Vždy“) – poloha se kvůli tomu nikam neodesílá.",
        "Location is read while you use the app to find nearby places. You can enter any address instead; address suggestions are provided by Apple MapKit. If you turn on alerts for “Want to try” places, iOS watches on-device for you arriving at those places (“Always” location) – your location is not sent anywhere for this.")),
      (("iCloud a widgety", "iCloud and widgets"),
       ("Uložená místa, poznámky, vlastní podniky a rezervace se synchronizují mezi tvými zařízeními přes tvůj soukromý iCloud (Apple). My k nim přístup nemáme. Widgety čtou jen kopii těchto dat uloženou v zařízení.",
        "Saved places, notes, your own places and reservations sync between your devices via your private iCloud (Apple). We have no access to them. Widgets only read an on-device copy of this data.")),
      (("Mapy a navigace", "Maps and directions"),
       ("Mapu zobrazuje Apple MapKit. Tlačítka Trasa, Google, Web nebo Volat otevřou Mapy, Google Mapy, web podniku nebo telefon.",
        "The map is provided by Apple MapKit. The Directions, Google, Website or Call buttons open Maps, Google Maps, the place's website or the phone.")),
    ]),
  dict(slug="fototip", name="FotoTip", mark="◎", color="#6351e8",
    tagline=("Návody a tipy pro fotografy: expozice, světlo, kompozice, pózy a fotografické kalkulačky.",
             "Guides and tips for photographers: exposure, light, composition, poses and photo calculators."),
    summary=("FotoTip nesbírá žádné osobní údaje. Nemá účty, reklamy ani analytiku a funguje celý offline – všechny návody jsou přímo v aplikaci.",
             "FotoTip collects no personal data. There are no accounts, ads or analytics, and it works fully offline – all guides are built into the app."),
    sections=[
      (("Co aplikace ukládá", "What the app stores"),
       ("Přečtené návody, oblíbené položky, zaškrtnuté body v kontrolních seznamech, hodnoty v kalkulačkách a nastavení vzhledu. Jen v zařízení; smazáním aplikace se smažou.",
        "Read guides, favourites, ticked items in checklists, calculator values and the appearance setting. Only on your device; deleted with the app.")),
      (("Síť", "Network"),
       ("Aplikace se nepřipojuje k žádnému serveru. Odkazy na tuto stránku a na web Fotodesk (<code>fotodesk.luksafoto.cz</code>) jen otevřou prohlížeč; aplikace jim nic neposílá.",
        "The app does not connect to any server. Links to this page and to the Fotodesk website (<code>fotodesk.luksafoto.cz</code>) simply open your browser; the app sends them nothing.")),
      (("Sdílení", "Sharing"),
       ("Když návod sdílíš, použije se systémový panel sdílení iOS a text dostane jen ten, komu ho pošleš.",
        "When you share a guide, the iOS share sheet is used and only the recipient you choose gets the text.")),
    ]),
  dict(slug="predplatne", name="Předplatné", mark="↻", color="#0f9a62",
    tagline=("Přehled předplatných a pravidelných plateb s připomínkami.",
             "Track subscriptions and recurring payments with reminders."),
    summary=("Předplatné nemá vlastní server, účty, reklamy ani analytiku. Předplatná jsou v tvém zařízení a v tvém soukromém iCloudu.",
             "Předplatné has no server of its own, no accounts, ads or analytics. Your subscriptions live on your device and in your private iCloud."),
    sections=[
      (("Co aplikace ukládá", "What the app stores"),
       ("Předplatná a pravidelné platby, které zapíšeš: název, částku, měnu, periodu, datum platby, zkušební dobu, kategorii, popis platební karty (jen text, který zadáš – žádná čísla karet se nevyžadují), konec smlouvy a výpovědní lhůtu, sdílení, odkaz a poznámku. K tomu nastavení a poslední stažený kurzovní lístek.",
        "Subscriptions and recurring payments you enter: name, amount, currency, period, payment date, trial period, category, a payment card label (only the text you type – no card numbers are required), contract end and notice period, sharing, a link and a note. Plus settings and the last downloaded exchange-rate table.")),
      (("iCloud a widget", "iCloud and widget"),
       ("Předplatná se synchronizují mezi tvými zařízeními přes tvůj soukromý iCloud (Apple CloudKit). My k nim přístup nemáme. Widget čte jen kopii dat uloženou v zařízení.",
        "Subscriptions sync between your devices via your private iCloud (Apple CloudKit). We have no access to them. The widget only reads an on-device copy of the data.")),
      (("Kurzy měn", "Exchange rates"),
       ("Pro přepočet cizích měn aplikace stahuje veřejný kurzovní lístek České národní banky (<code>api.cnb.cz</code>). Požadavky neobsahují žádné údaje o tobě ani o tvých předplatných.",
        "To convert foreign currencies the app downloads the public exchange-rate table of the Czech National Bank (<code>api.cnb.cz</code>). Requests contain no information about you or your subscriptions.")),
      (("Oznámení", "Notifications"),
       ("Připomínky před platbou, koncem zkušební doby a výpovědní lhůtou plánuje aplikace přímo v zařízení. Nikam se neodesílají.",
        "Reminders before a payment, the end of a trial and a notice deadline are scheduled on-device. Nothing is sent anywhere.")),
      (("Volitelné propojení s vlastním serverem", "Optional connection to your own server"),
       ("Aplikace umí volitelně synchronizovat předplatná s osobním serverem Mainhub, který si provozuje sám uživatel. Ve výchozím stavu je volba skrytá a vypnutá. Po propojení (QR kód z vlastního serveru) se předplatná posílají jen na adresu toho serveru; přístupový token je uložený v Klíčence zařízení. Kamera slouží jen k naskenování tohoto QR kódu.",
        "The app can optionally sync subscriptions with a personal Mainhub server run by the user themselves. This option is hidden and off by default. Once connected (via a QR code from your own server) subscriptions are sent only to that server's address; the access token is stored in the device Keychain. The camera is used only to scan that QR code.")),
      (("Siri a Zkratky", "Siri and Shortcuts"),
       ("Pokud použiješ Siri nebo Zkratky, hlasové pokyny zpracovává Apple podle svých zásad.",
        "If you use Siri or Shortcuts, voice requests are processed by Apple under its own policy.")),
    ]),
  dict(slug="garaz", name="Garážka", mark="🚗", color="#1f6fe5",
    tagline=("Vozidla, termíny s připomínkami, náklady, spotřeba a servisní knížka.",
             "Vehicles, reminders for due dates, costs, fuel consumption and a service log."),
    summary=("Garážka nemá vlastní server, účty, reklamy ani analytiku. Vozidla, náklady a termíny jsou v tvém zařízení a v tvém soukromém iCloudu.",
             "Garážka has no server of its own, no accounts, ads or analytics. Your vehicles, costs and due dates live on your device and in your private iCloud."),
    sections=[
      (("Co aplikace ukládá", "What the app stores"),
       ("Vozidla, která zapíšeš (název, SPZ, VIN, palivo, rok výroby, stav tachometru, fotka), termíny (STK, pojištění, dálniční známky, servis…), náklady včetně tankování a nabíjení, servisní záznamy s fotkami faktur, volitelně knihu jízd (trasa, kilometry, účel) a nastavení.",
        "Vehicles you enter (name, licence plate, VIN, fuel, year, odometer, photo), due dates (inspection, insurance, vignettes, service…), costs including fuelling and charging, service records with invoice photos, optionally a trip log (route, kilometres, purpose) and settings.")),
      (("iCloud a widget", "iCloud and widget"),
       ("Data se synchronizují mezi tvými zařízeními přes tvůj soukromý iCloud (Apple CloudKit). My k nim přístup nemáme. Widget „Co mě čeká“ čte jen kopii nejbližších termínů uloženou v zařízení.",
        "Data syncs between your devices via your private iCloud (Apple CloudKit). We have no access to it. The “Coming up” widget only reads an on-device copy of the nearest due dates.")),
      (("Kamera a fotky", "Camera and photos"),
       ("Kamera a knihovna fotek slouží jen k vyfocení vozidla, faktur a účtenek (skener dokumentů běží v zařízení). Fotky se ukládají k záznamu v aplikaci a do tvého iCloudu.",
        "The camera and photo library are used only to take pictures of your vehicle, invoices and receipts (the document scanner runs on-device). Photos are stored with the record in the app and in your iCloud.")),
      (("Oznámení", "Notifications"),
       ("Připomínky termínů plánuje aplikace přímo v zařízení. Nikam se neodesílají.",
        "Reminders for due dates are scheduled on-device. Nothing is sent anywhere.")),
      (("Export", "Export"),
       ("Export do CSV a PDF vytvoří soubor v zařízení; dál ho pošleš jen ty přes systémové sdílení.",
        "CSV and PDF export creates a file on your device; it only goes further when you send it via the share sheet.")),
      (("Volitelné propojení s vlastním serverem", "Optional connection to your own server"),
       ("Aplikace umí volitelně synchronizovat vozidla, náklady a termíny s osobním serverem Mainhub, který si provozuje sám uživatel, a zobrazit z něj souhrn knihy jízd. Ve výchozím stavu je volba skrytá a vypnutá. Po propojení (QR kód z vlastního serveru) se data posílají jen na adresu toho serveru; přístupový token je uložený v Klíčence zařízení. Kamera slouží i k naskenování tohoto QR kódu.",
        "The app can optionally sync vehicles, costs and due dates with a personal Mainhub server run by the user themselves and show a trip-log summary from it. This option is hidden and off by default. Once connected (via a QR code from your own server) data is sent only to that server's address; the access token is stored in the device Keychain. The camera is also used to scan that QR code.")),
      (("Siri a Zkratky", "Siri and Shortcuts"),
       ("Pokud použiješ Siri nebo Zkratky (např. „Zapiš tankování“), hlasové pokyny zpracovává Apple podle svých zásad.",
        "If you use Siri or Shortcuts (e.g. “Log fuel”), voice requests are processed by Apple under its own policy.")),
    ]),
  dict(slug="zaruky", name="Záruky a doklady", mark="✓", color="#0e9a80",
    tagline=("Účtenky, záruky, doklady, revize a reklamace na jednom místě.",
             "Receipts, warranties, documents, inspections and claims in one place."),
    summary=("Záruky nemají vlastní server, účty, reklamy ani analytiku. Účtenky, záruky, doklady a revize jsou v tvém zařízení a v tvém soukromém iCloudu. Čtení účtenek probíhá přímo v telefonu.",
             "Záruky has no server of its own, no accounts, ads or analytics. Receipts, warranties, documents and inspections live on your device and in your private iCloud. Receipts are read on the phone itself."),
    sections=[
      (("Co aplikace ukládá", "What the app stores"),
       ("Záruky (výrobek, obchod, datum nákupu, cena, sériové číslo, kategorie, fotky účtenek a výrobků), doklady (druh, držitel, číslo dokladu, vydavatel, platnost, skeny), smlouvy a pojistky, revize a údržbu (místo, firma, kontakt, termíny, protokoly), reklamace (stav, obchod nebo servis, kontakt, popis vady, dokumenty) a nastavení.",
        "Warranties (product, shop, purchase date, price, serial number, category, photos of receipts and products), documents (type, holder, document number, issuer, validity, scans), contracts and insurance, inspections and upkeep (place, company, contact, dates, reports), claims (status, shop or service, contact, defect description, documents) and settings.")),
      (("Čísla dokladů", "Document numbers"),
       ("Čísla dokladů jsou v aplikaci skrytá a zobrazí se až po ověření Face ID, Touch ID nebo kódem zařízení. Ověření provádí iOS, aplikace k biometrickým údajům nemá přístup. V iCloudu jsou čísla uložená šifrovaně (CloudKit encrypted values).",
        "Document numbers are hidden in the app and shown only after Face ID, Touch ID or device passcode authentication. iOS performs the check; the app never sees biometric data. In iCloud the numbers are stored encrypted (CloudKit encrypted values).")),
      (("iCloud a widget", "iCloud and widget"),
       ("Data se synchronizují mezi tvými zařízeními přes tvůj soukromý iCloud (Apple CloudKit). My k nim přístup nemáme. Synchronizaci lze vypnout; aplikace pak funguje jen v zařízení. Widget „Co brzy vyprší“ čte jen kopii nejbližších termínů (název a datum) uloženou v zařízení.",
        "Data syncs between your devices via your private iCloud (Apple CloudKit). We have no access to it. Sync can be turned off so the app works on-device only. The “Expiring soon” widget only reads an on-device copy of the nearest dates (name and date).")),
      (("Kamera, fotky, soubory a čtení účtenek", "Camera, photos, files and receipt reading"),
       ("Kamera, knihovna fotek a výběr souborů slouží jen k přiložení účtenky, fotky výrobku, skenu dokladu nebo protokolu. Rozpoznání textu a vytažení údajů z účtenky (obchod, datum, cena, výrobek) probíhá přímo v zařízení pomocí Apple Vision a Apple Intelligence; nic se kvůli tomu neodesílá. Soubory, které do aplikace pošleš přes Sdílet, se uloží jen v zařízení.",
        "The camera, photo library and file picker are used only to attach a receipt, product photo, document scan or report. Text recognition and extracting details from a receipt (shop, date, price, product) run on-device using Apple Vision and Apple Intelligence; nothing is sent for it. Files you send to the app via Share are stored on the device only.")),
      (("Oznámení", "Notifications"),
       ("Upozornění na konec záruky, platnosti dokladu, výpovědní lhůty, termín revize a lhůtu reklamace plánuje aplikace přímo v zařízení. Nikam se neodesílají.",
        "Reminders for warranty ends, document expiry, notice periods, inspections and claim deadlines are scheduled on-device. Nothing is sent anywhere.")),
      (("Sdílení PDF", "PDF sharing"),
       ("Sdílení položky jako PDF vytvoří soubor v zařízení; číslo dokladu je v něm jen po ověření. Dál ho pošleš jen ty přes systémové sdílení.",
        "Sharing an item as PDF creates a file on your device; the document number is included only after authentication. It only goes further when you send it via the share sheet.")),
      (("Volitelné propojení s vlastním serverem", "Optional connection to your own server"),
       ("Aplikace umí volitelně synchronizovat záruky, doklady, revize a jejich soubory s osobním serverem Mainhub, který si provozuje sám uživatel. Ve výchozím stavu je volba skrytá a vypnutá. Po propojení (QR kód z vlastního serveru) se data posílají jen na adresu toho serveru; přístupový token je uložený v Klíčence zařízení. Kamera slouží i k naskenování tohoto QR kódu.",
        "The app can optionally sync warranties, documents, inspections and their files with a personal Mainhub server run by the user themselves. This option is hidden and off by default. Once connected (via a QR code from your own server) data is sent only to that server's address; the access token is stored in the device Keychain. The camera is also used to scan that QR code.")),
      (("Siri a Zkratky", "Siri and Shortcuts"),
       ("Pokud použiješ Siri nebo Zkratky (např. „Co brzy vyprší v Zárukách“), hlasové pokyny zpracovává Apple podle svých zásad.",
        "If you use Siri or Shortcuts (e.g. “What's expiring soon in Záruky”), voice requests are processed by Apple under its own policy.")),
    ]),
  dict(slug="lekarnicka", name="Lékárnička", mark="✚", color="#d6336c",
    tagline=("Domácí lékárnička: připomínky léků, zásoby a expirace pro celou rodinu.",
             "Home medicine cabinet: medication reminders, stock and expiry dates for the whole family."),
    summary=("Lékárnička nemá vlastní server, účty, reklamy ani analytiku. Léky, dávkování a historie užití – tedy údaje o zdraví – jsou jen v tvém zařízení a v tvém soukromém iCloudu. My k nim přístup nemáme.",
             "Lékárnička has no server of its own, no accounts, ads or analytics. Medicines, dosing schedules and intake history, i.e. health data, live only on your device and in your private iCloud. We have no access to them."),
    sections=[
      (("Co aplikace ukládá", "What the app stores"),
       ("Osoby, o které se staráš (jméno, druh, ikona), léky (název, forma, síla, zásoba, expirace, šarže, čárový kód, fotka obalu, poznámka), dávkování a připomínky a historii užití (kdy byla dávka vzata nebo vynechána). Pro widget se v zařízení ukládá kopie dnešních dávek.",
        "People you care for (name, type, icon), medicines (name, form, strength, stock, expiry, batch, barcode, package photo, note), dosing schedules and reminders, and intake history (when a dose was taken or skipped). A copy of today’s doses is stored on the device for the widget.")),
      (("iCloud", "iCloud"),
       ("Pokud máš zapnutý iCloud, data se synchronizují mezi tvými zařízeními přes tvůj soukromý iCloud (Apple CloudKit). Nikomu dalšímu se nesdílejí. Bez iCloudu aplikace funguje jen v zařízení.",
        "If you are signed in to iCloud, data syncs between your devices via your private iCloud (Apple CloudKit). It is not shared with anyone else. Without iCloud the app works on-device only.")),
      (("Kamera a fotky", "Camera and photos"),
       ("Kamera a výběr fotek slouží jen k vyfocení obalu léku. Rozpoznání textu (název, síla, expirace) a čárového kódu probíhá přímo v zařízení (Apple Vision), nic se kvůli tomu neodesílá. Uloží se jen zmenšená fotka obalu u léku.",
        "The camera and photo picker are only used to photograph a medicine package. Text recognition (name, strength, expiry) and barcode reading run on-device (Apple Vision); nothing is sent anywhere. Only a downscaled package photo is stored with the medicine.")),
      (("Apple Zdraví", "Apple Health"),
       ("Volitelně může aplikace s tvým svolením načíst seznam léků z appky Zdraví (jen ke čtení; vybíráš, které léky sdílíš). Údaje ze Zdraví se nepoužívají k reklamě ani se nikam neodesílají. Do Zdraví aplikace nic nezapisuje.",
        "Optionally, with your permission, the app can read your medications list from the Health app (read-only; you choose which medications to share). Health data is never used for advertising or sent anywhere. The app does not write anything to Health.")),
      (("Oznámení, Siri a widget", "Notifications, Siri and widget"),
       ("Připomínky dávek, zásob a expirací plánuje aplikace přímo v zařízení. Příkazy pro Siri a Zkratky zpracovává Apple podle svých zásad. Widget čte jen kopii dnešních dávek v zařízení.",
        "Dose, stock and expiry reminders are scheduled on-device. Siri and Shortcuts requests are processed by Apple under its own policy. The widget only reads an on-device copy of today’s doses.")),
      (("Zdravotní upozornění", "Medical disclaimer"),
       ("Aplikace nenahrazuje lékaře ani lékárníka a nedává rady k dávkování. Jen připomíná to, co si uživatel sám zadá.",
        "The app does not replace a doctor or pharmacist and gives no dosing advice. It only reminds you of what you enter yourself.")),
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
# Rozcestník zásad; úvodní stránku webu (index.html) generuje web.py z EasyLife/catalog.json.
(OUT / "soukromi.html").write_text(index(), encoding="utf-8")
for app in APPS:
    (OUT / f"{app['slug']}.html").write_text(app_page(app), encoding="utf-8")
(OUT / ".nojekyll").write_text("")
print("ok", [a["slug"] for a in APPS])

import web  # web easyforlife.eu – úvod a detaily appek z catalog.json, viz web.py
web.build(OUT, APPS, EXTERNAL, OPERATOR)
