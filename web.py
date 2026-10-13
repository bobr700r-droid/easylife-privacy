"""Generuje web EasyForLife z EasyLife/catalog.json a site/apps/<id>.json.

Dvě verze: easyforlife.cz = čeština, easyforlife.eu = angličtina (kořen) a další jazyky (/sk/, /de/, /es/, /pl/).
Dokud .eu nemíří na Fly (EU_LIVE), běží všechny jazyky na .cz pod /<lang>/. Výstup: dist/cz a dist/eu
(servíruje Fly app easyforlife-redirect, server/server.js podle hostu). docs/ (GitHub Pages) drží jen
zásady soukromí /<slug>.html a obrázky; ostatní stránky tam jen přesměrují na novou adresu.

Volá se z build.py: web.build(OUT, APPS, EXTERNAL, OPERATOR). Stránky soukromí (/<slug>.html) generuje build.py,
tady se jen odkazují. Obsah detailů appek je v site/apps/<id>.json (popis, funkce, propojení, stav), texty
webu ve slovníku T. Ikony se kopírují z <App>/…/AppIcon.appiconset do docs/icons/ (sips + cwebp),
favicon a OG obrázek kreslí site/art.swift (jen když chybí; vynutit: python3 build.py --art).
"""
import html, json, math, os, pathlib, shutil, socket, subprocess, sys, zlib
sys.path.insert(0, str(pathlib.Path(__file__).parent / "site"))
import eco  # site/eco.py – jak spolu appky spolupracují

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent                      # EasyLife aplikace/
CATALOG = ROOT / "EasyLife" / "catalog.json"
CONTENT = HERE / "site" / "apps"
CZ, EU = "https://easyforlife.cz", "https://easyforlife.eu"
FLY_IPV4 = "66.241.124.47"  # Fly app easyforlife-redirect
DIST = HERE / "dist"

def _eu_live():
    """easyforlife.eu běží, když míří na Fly app (nebo EU_LIVE=1/0 v prostředí)."""
    if os.environ.get("EU_LIVE") in ("0", "1"):
        return os.environ["EU_LIVE"] == "1"
    try:
        return FLY_IPV4 in {i[4][0] for i in socket.getaddrinfo("easyforlife.eu", 443, socket.AF_INET)}
    except OSError:
        return False
EU_LIVE = _eu_live()
LANGS = ["cs", "en", "sk", "de", "es", "pl"]
LANG_NAMES = {"cs": "Čeština", "en": "English", "sk": "Slovenčina", "de": "Deutsch", "es": "Español", "pl": "Polski"}
# Appky, které na webu nemají být vůbec. Omezení na jazyky bere web z pole `locales` v katalogu (Kulturník jen cs).
HIDDEN = set()
# Složka appky, když se nejmenuje jako id v katalogu.
FOLDERS = {"kulturnik": "Vyrazime", "easylife": "EasyForLifeHub", "cestovnicek": "Cestovnicek/apple"}
CONTACT = "info@luksafoto.cz"  # kontakt podpory, dokud easyforlife.eu nemá vlastní e-mail
FAMILY_COLORS = {"easylife": "#2563eb", "cestovani": "#2563eb", "foto": "#e8731c", "domacnost": "#0f9a62", "volny-cas": "#8b46d9",
                 "navigace": "#0e9aa7", "zdravi": "#e8457a", "kancelar": "#6366f1", "firmy": "#d9480f"}
WORK = ["kancelar", "firmy"]  # rodiny v sekci „Pro práci“ (tmavý blok na konci)
PLATFORMS = {"iOS": "iPhone", "watchOS": "Apple Watch", "macOS": "Mac", "web": "Web", "CarPlay": "CarPlay"}

T = {
  "title": ['EasyForLife – appky, které ulehčují život', 'EasyForLife – apps that make life easier', 'EasyForLife – appky, ktoré uľahčujú život', 'EasyForLife – Apps, die das Leben leichter machen', 'EasyForLife – apps que facilitan la vida', 'EasyForLife – aplikacje, które ułatwiają życie'],
  "hero": ['Appky, které ti ulehčí život', 'Apps that make life easier', 'Appky, ktoré ti uľahčia život', 'Apps, die dir das Leben leichter machen', 'Apps que te hacen la vida más fácil', 'Aplikacje, które ułatwiają życie'],
  "lead": ['EasyForLife je rodina aplikací pro iPhone, Mac a web. Malé appky pro každý den bez registrace a bez reklam – a vedle nich navigace, zdraví, kancelář a profesionální nástroje pro firmy.', 'EasyForLife is a family of apps for iPhone, Mac and the web. Small everyday apps with no sign-up and no ads – plus navigation, health, office tools and professional software for businesses.', 'EasyForLife je rodina aplikácií pre iPhone, Mac a web. Malé appky na každý deň bez registrácie a bez reklám – a vedľa nich navigácia, zdravie, kancelária a profesionálne nástroje pre firmy.', 'EasyForLife ist eine Familie von Apps für iPhone, Mac und Web. Kleine Alltags-Apps ohne Registrierung und ohne Werbung – dazu Navigation, Gesundheit, Büro und Profi-Tools für Unternehmen.', 'EasyForLife es una familia de apps para iPhone, Mac y web. Pequeñas apps para el día a día sin registro ni anuncios, y junto a ellas navegación, salud, oficina y herramientas profesionales para empresas.', 'EasyForLife to rodzina aplikacji na iPhone’a, Maca i przeglądarkę. Małe aplikacje na co dzień bez rejestracji i reklam – a obok nich nawigacja, zdrowie, biuro i profesjonalne narzędzia dla firm.'],
  "pills": [['Bez reklam a sledování', 'Malé appky bez registrace', 'iPhone, Mac i web'], ['No ads, no tracking', 'Small apps, no sign-up', 'iPhone, Mac and web'], ['Bez reklám a sledovania', 'Malé appky bez registrácie', 'iPhone, Mac aj web'], ['Ohne Werbung und Tracking', 'Kleine Apps ohne Konto', 'iPhone, Mac und Web'], ['Sin anuncios ni rastreo', 'Apps pequeñas sin registro', 'iPhone, Mac y web'], ['Bez reklam i śledzenia', 'Małe aplikacje bez rejestracji', 'iPhone, Mac i web']],
  "apps": ["Aplikace", "Apps", "Aplikácie", "Apps", "Apps", "Aplikacje"],
  "apps_lead": ['Malé appky pro každý den, navigace a zdraví. Appky z jedné rodiny se navzájem doplňují.', 'Small everyday apps, navigation and health. Apps in the same family complement each other.', 'Malé appky na každý deň, navigácia a zdravie. Aplikácie z jednej rodiny sa navzájom dopĺňajú.', 'Kleine Alltags-Apps, Navigation und Gesundheit. Apps einer Familie ergänzen sich gegenseitig.', 'Pequeñas apps para el día a día, navegación y salud. Las apps de una misma familia se complementan.', 'Małe aplikacje na co dzień, nawigacja i zdrowie. Aplikacje z jednej rodziny uzupełniają się nawzajem.'],
  "how": ["Jak to děláme", "How we build them", "Ako to robíme", "Unsere Prinzipien", "Cómo las hacemos", "Jak je tworzymy"],
  "principles": [[('Účet jen tam, kde dává smysl', 'Malé appky stáhneš a používáš bez registrace. Účet chtějí jen služby, které synchronizují s webem nebo slouží firmám.'), ('Žádné reklamy ani sledování', 'Appky neobsahují reklamy ani reklamní sledování a nikomu neprodávají, co v nich děláš.'), ('Tvoje data jsou tvoje', 'Malé appky drží data v telefonu, případně v tvém soukromém iCloudu. Služby s účtem data nikomu neprodávají ani nesdílejí pro reklamu.'), ('Samostatné, ale propojené', 'Každá appka funguje sama. Když máš víc appek z jedné rodiny, umí si podat ruku.')], [('Accounts only where they make sense', 'Small apps work right away with no sign-up. Only services that sync with the web or serve businesses need an account.'), ('No ads, no tracking', 'The apps contain no ads or ad tracking and never sell what you do in them.'), ('Your data is yours', 'Small apps keep data on your phone or in your private iCloud. Services with accounts never sell your data or share it for advertising.'), ('Independent, yet connected', 'Every app works on its own. Use several from one family and they work hand in hand.')], [('Účet len tam, kde dáva zmysel', 'Malé appky stiahneš a používaš bez registrácie. Účet chcú len služby, ktoré synchronizujú s webom alebo slúžia firmám.'), ('Žiadne reklamy ani sledovanie', 'Aplikácie neobsahujú reklamy ani reklamné sledovanie a nikomu nepredávajú, čo v nich robíš.'), ('Tvoje dáta sú tvoje', 'Malé appky držia dáta v telefóne, prípadne v tvojom súkromnom iCloude. Služby s účtom dáta nikomu nepredávajú ani nezdieľajú na reklamu.'), ('Samostatné, ale prepojené', 'Každá aplikácia funguje sama. Keď máš viac aplikácií z jednej rodiny, vedia si podať ruku.')], [('Konto nur, wo es sinnvoll ist', 'Kleine Apps funktionieren sofort ohne Registrierung. Ein Konto brauchen nur Dienste mit Web-Synchronisierung oder für Unternehmen.'), ('Keine Werbung, kein Tracking', 'Die Apps enthalten weder Werbung noch Werbe-Tracking und verkaufen nicht, was du darin tust.'), ('Deine Daten gehören dir', 'Kleine Apps speichern Daten auf deinem iPhone oder in deiner privaten iCloud. Dienste mit Konto verkaufen deine Daten nie und teilen sie nicht für Werbung.'), ('Eigenständig und doch verbunden', 'Jede App funktioniert für sich. Nutzt du mehrere aus einer Familie, arbeiten sie Hand in Hand.')], [('Cuenta solo cuando tiene sentido', 'Las apps pequeñas funcionan sin registro. Solo piden cuenta los servicios que se sincronizan con la web o están pensados para empresas.'), ('Sin anuncios ni rastreo', 'Las apps no tienen anuncios ni rastreo publicitario y nunca venden lo que haces en ellas.'), ('Tus datos son tuyos', 'Las apps pequeñas guardan los datos en tu teléfono o en tu iCloud privado. Los servicios con cuenta nunca venden tus datos ni los comparten para publicidad.'), ('Independientes, pero conectadas', 'Cada app funciona por sí sola. Si usas varias de una misma familia, se echan una mano.')], [('Konto tylko tam, gdzie ma sens', 'Małe aplikacje działają od razu bez rejestracji. Konta wymagają tylko usługi synchronizowane z przeglądarką lub przeznaczone dla firm.'), ('Bez reklam i śledzenia', 'Aplikacje nie mają reklam ani śledzenia reklamowego i nikomu nie sprzedają tego, co w nich robisz.'), ('Twoje dane są twoje', 'Małe aplikacje trzymają dane w telefonie lub w twoim prywatnym iCloud. Usługi z kontem nigdy nie sprzedają danych ani nie udostępniają ich do reklam.'), ('Niezależne, ale połączone', 'Każda aplikacja działa samodzielnie. Jeśli używasz kilku z jednej rodziny, współpracują ze sobą.')]],
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
  "hero_hl": ['ulehčí život', 'life easier', 'uľahčia život', 'leichter', 'más fácil', 'ułatwiają życie'],
  "count": ['{n} aplikací pro iPhone, Mac a web', '{n} apps for iPhone, Mac and web', '{n} aplikácií pre iPhone, Mac a web', '{n} Apps für iPhone, Mac und Web', '{n} apps para iPhone, Mac y web', '{n} aplikacji na iPhone’a, Maca i web'],
  "cta_apps": ["Prohlédnout appky", "Explore the apps", "Pozrieť aplikácie", "Apps entdecken", "Ver las apps", "Zobacz aplikacje"],
  "wall": ['Jedna rodina. Míň starostí.', 'One family. Fewer worries.', 'Jedna rodina. Menej starostí.', 'Eine Familie. Weniger Sorgen.', 'Una familia. Menos preocupaciones.', 'Jedna rodzina. Mniej zmartwień.'],
  "soon_short": ["Brzy", "Soon", "Čoskoro", "Bald", "Pronto", "Wkrótce"],
  "nf": ["Tahle stránka neexistuje. Možná se přestěhovala – zkus úvodní stránku.", "This page doesn’t exist. It may have moved – try the home page.",
         "Táto stránka neexistuje. Možno sa presťahovala – skús úvodnú stránku.", "Diese Seite gibt es nicht. Vielleicht ist sie umgezogen – versuch die Startseite.",
         "Esta página no existe. Puede que se haya movido: prueba la página de inicio.", "Ta strona nie istnieje. Może została przeniesiona – spróbuj strony głównej."],
  "solo": ["{a} funguje i sama – propojení je bonus.", "{a} works on its own too – connections are a bonus.", "{a} funguje aj sama – prepojenie je bonus.",
           "{a} funktioniert auch allein – die Verbindungen sind ein Bonus.", "{a} también funciona sola; las conexiones son un extra.", "{a} działa też samodzielnie – połączenia to bonus."],
  "start": ["Začni tady", "Start here", "Začni tu", "Starte hier", "Empieza aquí", "Zacznij tutaj"],
  "hub_more": ["Více o Hubu", "More about Hub", "Viac o Hube", "Mehr über den Hub", "Más sobre Hub", "Więcej o Hubie"],
  "today": ["Dnes a tento týden", "Today and this week", "Dnes a tento týždeň", "Heute und diese Woche", "Hoy y esta semana", "Dziś i w tym tygodniu"],
  "eco_title": ["Jak spolu appky spolupracují", "How the apps work together", "Ako spolu appky spolupracujú", "Wie die Apps zusammenarbeiten", "Cómo colaboran las apps", "Jak aplikacje ze sobą współpracują"],
  "eco_lead": ["Každá appka funguje i sama – propojení je bonus. Když jich máš víc, podají si ruku: jedna otevře druhou přesně tam, kde ji potřebuješ, a data přitom zůstávají v telefonu.",
               "Every app works on its own – connections are a bonus. Have several and they lend each other a hand: one opens the other exactly where you need it, while your data stays on your phone.",
               "Každá appka funguje aj sama – prepojenie je bonus. Keď ich máš viac, podajú si ruku: jedna otvorí druhú presne tam, kde ju potrebuješ, a dáta pritom zostávajú v telefóne.",
               "Jede App funktioniert für sich – die Verbindung ist ein Bonus. Hast du mehrere, helfen sie sich: Eine öffnet die andere genau dort, wo du sie brauchst, und die Daten bleiben auf deinem iPhone.",
               "Cada app funciona por sí sola; la conexión es un extra. Si tienes varias, se echan una mano: una abre la otra justo donde la necesitas y los datos se quedan en tu teléfono.",
               "Każda aplikacja działa samodzielnie – połączenia to bonus. Gdy masz ich kilka, pomagają sobie: jedna otwiera drugą dokładnie tam, gdzie trzeba, a dane zostają w telefonie."],
  "eco_hint": ["Najeď nebo klepni na appku a uvidíš, s kým spolupracuje.", "Hover or tap an app to see what it connects with.", "Prejdi alebo ťukni na appku a uvidíš, s kým spolupracuje.",
               "Fahre über eine App oder tippe darauf, um ihre Verbindungen zu sehen.", "Pasa el ratón o toca una app para ver con cuáles se conecta.", "Najedź lub stuknij aplikację, by zobaczyć jej połączenia."],
  "eco_hub": ["A EasyForLife Hub ukáže termíny ze všech appek na jednom místě.", "And EasyForLife Hub shows what’s coming up from all apps in one place.",
              "A EasyForLife Hub ukáže termíny zo všetkých appiek na jednom mieste.", "Und der EasyForLife Hub zeigt Termine aus allen Apps an einem Ort.",
              "Y EasyForLife Hub muestra lo pendiente de todas las apps en un solo lugar.", "A EasyForLife Hub pokaże terminy ze wszystkich aplikacji w jednym miejscu."],
  "support": ["Podpora", "Support", "Podpora", "Support", "Soporte", "Wsparcie"],
  "support_title": ["Podpora a kontakt", "Support and contact", "Podpora a kontakt", "Support und Kontakt", "Soporte y contacto", "Wsparcie i kontakt"],
  "support_lead": ["Něco nefunguje, máš nápad nebo dotaz k některé appce EasyForLife? Napiš nám, odpovídáme obvykle do pár dní.",
                   "Something not working, got an idea or a question about an EasyForLife app? Write to us – we usually reply within a few days.",
                   "Niečo nefunguje, máš nápad alebo otázku k niektorej aplikácii EasyForLife? Napíš nám, odpovedáme zvyčajne do pár dní.",
                   "Funktioniert etwas nicht, hast du eine Idee oder eine Frage zu einer EasyForLife-App? Schreib uns – wir antworten meist innerhalb weniger Tage.",
                   "¿Algo no funciona, tienes una idea o una pregunta sobre una app de EasyForLife? Escríbenos; solemos responder en pocos días.",
                   "Coś nie działa, masz pomysł albo pytanie o aplikację EasyForLife? Napisz do nas – zwykle odpowiadamy w ciągu kilku dni."],
  "support_mail": ["Napsat e-mail", "Send an email", "Napísať e-mail", "E-Mail schreiben", "Enviar un correo", "Napisz e-mail"],
  "support_hint": ["Uveď prosím název appky, model iPhonu a verzi iOS. U chyby pomůže i snímek obrazovky.",
                   "Please mention the app name, your iPhone model and iOS version. For bugs, a screenshot helps too.",
                   "Uveď prosím názov aplikácie, model iPhonu a verziu iOS. Pri chybe pomôže aj snímka obrazovky.",
                   "Bitte nenne den App-Namen, dein iPhone-Modell und die iOS-Version. Bei Fehlern hilft auch ein Screenshot.",
                   "Indica el nombre de la app, tu modelo de iPhone y la versión de iOS. Si es un error, una captura de pantalla ayuda.",
                   "Podaj nazwę aplikacji, model iPhone’a i wersję iOS. Przy błędzie pomoże też zrzut ekranu."],
  "faq_title": ["Časté otázky", "FAQ", "Časté otázky", "Häufige Fragen", "Preguntas frecuentes", "Częste pytania"],
  "faq": [
    [('Potřebuju účet nebo registraci?', 'Malé appky pro každý den ne. Účet potřebují jen služby s webovou verzí a nástroje pro firmy – u každé appky to uvidíš na štítku „S účtem“ nebo „Účet volitelný“.'),
     ("Kde jsou moje data?", "V tvém iPhonu, a pokud appka synchronizuje, v tvém soukromém iCloudu. My k nim přístup nemáme. Podrobnosti najdeš v zásadách ochrany soukromí každé appky."),
     ("Jak přenesu data na nový iPhone?", "Appky se synchronizací přes iCloud si data přenesou samy, když se na novém iPhonu přihlásíš stejným Apple ID. Ostatní data se přenesou se zálohou iPhonu."),
     ("Jak svá data smažu?", "Smazáním appky se smažou data v zařízení. Data v iCloudu smažeš v Nastavení → tvoje jméno → iCloud → Spravovat úložiště."),
     ("Jak se dostanu do beta verze?", "Některé appky jsou zatím v beta testu přes TestFlight. Napiš nám e-mail a pošleme ti pozvánku."),
     ("Mám nápad na novou funkci", "Sem s ním! Napiš nám e-mail – nápady od uživatelů čteme všechny.")],
    [('Do I need an account?', 'Not for the small everyday apps. Only services with a web version and business tools need an account – each app shows an “Account” or “Account optional” label.'),
     ("Where is my data?", "On your iPhone and, if the app syncs, in your private iCloud. We have no access to it. Each app’s privacy policy has the details."),
     ("How do I move my data to a new iPhone?", "Apps that sync via iCloud move your data automatically when you sign in with the same Apple ID. Everything else comes over with your iPhone backup."),
     ("How do I delete my data?", "Deleting the app removes the data on your device. Data in iCloud can be deleted in Settings → your name → iCloud → Manage Storage."),
     ("How do I join a beta?", "Some apps are still in beta testing on TestFlight. Send us an email and we’ll invite you."),
     ("I have an idea for a feature", "Great! Send us an email – we read every suggestion.")],
    [('Potrebujem účet alebo registráciu?', 'Malé appky na každý deň nie. Účet potrebujú len služby s webovou verziou a nástroje pre firmy – pri každej aplikácii to uvidíš na štítku „S účtom“ alebo „Účet voliteľný“.'),
     ("Kde sú moje dáta?", "V tvojom iPhone a ak aplikácia synchronizuje, v tvojom súkromnom iCloude. My k nim prístup nemáme. Podrobnosti nájdeš v zásadách ochrany súkromia každej aplikácie."),
     ("Ako prenesiem dáta do nového iPhonu?", "Aplikácie so synchronizáciou cez iCloud si dáta prenesú samy, keď sa na novom iPhone prihlásiš rovnakým Apple ID. Ostatné dáta sa prenesú so zálohou iPhonu."),
     ("Ako svoje dáta zmažem?", "Zmazaním aplikácie sa zmažú dáta v zariadení. Dáta v iCloude zmažeš v Nastaveniach → tvoje meno → iCloud → Spravovať úložisko."),
     ("Ako sa dostanem do beta verzie?", "Niektoré aplikácie sú zatiaľ v beta teste cez TestFlight. Napíš nám e-mail a pošleme ti pozvánku."),
     ("Mám nápad na novú funkciu", "Sem s ním! Napíš nám e-mail – nápady od používateľov čítame všetky.")],
    [('Brauche ich ein Konto?', 'Für die kleinen Alltags-Apps nicht. Ein Konto brauchen nur Dienste mit Web-Version und Business-Tools – jede App zeigt das mit „Mit Konto“ oder „Konto optional“.'),
     ("Wo sind meine Daten?", "Auf deinem iPhone und, wenn die App synchronisiert, in deiner privaten iCloud. Wir haben keinen Zugriff darauf. Details stehen in der Datenschutzerklärung jeder App."),
     ("Wie übertrage ich meine Daten auf ein neues iPhone?", "Apps mit iCloud-Synchronisierung übernehmen deine Daten automatisch, wenn du dich mit derselben Apple-ID anmeldest. Alles andere kommt mit dem iPhone-Backup mit."),
     ("Wie lösche ich meine Daten?", "Wenn du die App löschst, werden die Daten auf dem Gerät gelöscht. Daten in iCloud löschst du unter Einstellungen → dein Name → iCloud → Speicher verwalten."),
     ("Wie komme ich in eine Beta?", "Einige Apps sind noch in der Beta-Phase über TestFlight. Schreib uns eine E-Mail und wir laden dich ein."),
     ("Ich habe eine Idee für eine Funktion", "Her damit! Schreib uns eine E-Mail – wir lesen jeden Vorschlag.")],
    [('¿Necesito una cuenta?', 'Para las apps pequeñas del día a día, no. Solo los servicios con versión web y las herramientas para empresas necesitan cuenta; cada app lo indica con «Con cuenta» o «Cuenta opcional».'),
     ("¿Dónde están mis datos?", "En tu iPhone y, si la app sincroniza, en tu iCloud privado. Nosotros no tenemos acceso. La política de privacidad de cada app tiene los detalles."),
     ("¿Cómo paso mis datos a un iPhone nuevo?", "Las apps que sincronizan por iCloud traen tus datos solas al iniciar sesión con el mismo Apple ID. El resto se transfiere con la copia de seguridad del iPhone."),
     ("¿Cómo borro mis datos?", "Al eliminar la app se borran los datos del dispositivo. Los datos de iCloud se borran en Ajustes → tu nombre → iCloud → Gestionar almacenamiento."),
     ("¿Cómo me apunto a una beta?", "Algunas apps están aún en fase beta en TestFlight. Escríbenos un correo y te enviaremos una invitación."),
     ("Tengo una idea para una función", "¡Cuéntanosla! Escríbenos un correo: leemos todas las sugerencias.")],
    [('Czy potrzebuję konta?', 'Do małych aplikacji na co dzień nie. Konta wymagają tylko usługi z wersją webową i narzędzia dla firm – każda aplikacja ma etykietę „Z kontem” lub „Konto opcjonalne”.'),
     ("Gdzie są moje dane?", "Na twoim iPhonie, a jeśli aplikacja synchronizuje, w twoim prywatnym iCloud. My nie mamy do nich dostępu. Szczegóły znajdziesz w polityce prywatności każdej aplikacji."),
     ("Jak przenieść dane na nowego iPhone’a?", "Aplikacje synchronizujące przez iCloud przeniosą dane same, gdy zalogujesz się tym samym Apple ID. Resztę przeniesie kopia zapasowa iPhone’a."),
     ("Jak usunąć swoje dane?", "Usunięcie aplikacji kasuje dane w urządzeniu. Dane w iCloud usuniesz w Ustawieniach → twoje imię → iCloud → Zarządzaj pamięcią."),
     ("Jak dołączyć do wersji beta?", "Niektóre aplikacje są jeszcze w fazie beta w TestFlight. Napisz do nas e-mail, a wyślemy zaproszenie."),
     ("Mam pomysł na nową funkcję", "Śmiało! Napisz do nas e-mail – czytamy wszystkie propozycje.")]],
  "skip": ["Přejít na obsah", "Skip to content", "Prejsť na obsah", "Zum Inhalt", "Ir al contenido", "Przejdź do treści"],  "work": ['Pro práci', 'For work', 'Pre prácu', 'Für die Arbeit', 'Para el trabajo', 'Do pracy'],
  "projects": ["Další projekty", "Other projects", "Ďalšie projekty", "Weitere Projekte", "Otros proyectos", "Inne projekty"],
  "projects_lead": ["Samostatné projekty pod značkou EasyForLife – s vlastním webem, vlastním obchodním modelem a vlastními zásadami. Do rodinného předplatného EasyForLife nepatří.",
                    "Separate projects under the EasyForLife brand – with their own website, their own business model and their own policies. They are not part of the EasyForLife family subscription.",
                    "Samostatné projekty pod značkou EasyForLife – s vlastným webom, vlastným obchodným modelom a vlastnými zásadami. Do rodinného predplatného EasyForLife nepatria.",
                    "Eigenständige Projekte unter der Marke EasyForLife – mit eigener Website, eigenem Geschäftsmodell und eigenen Richtlinien. Sie gehören nicht zum EasyForLife-Familienabo.",
                    "Proyectos independientes bajo la marca EasyForLife, con su propia web, su propio modelo de negocio y sus propias políticas. No forman parte de la suscripción familiar de EasyForLife.",
                    "Osobne projekty pod marką EasyForLife – z własną stroną, własnym modelem biznesowym i własnymi zasadami. Nie należą do rodzinnej subskrypcji EasyForLife."],
  "separate": ["Samostatný projekt", "Separate project", "Samostatný projekt", "Eigenständiges Projekt", "Proyecto independiente", "Osobny projekt"],
  "one_time": ["Jednorázový nákup plné verze, ne předplatné. Během testování je vše zdarma.",
               "One-time purchase of the full version, not a subscription. Everything is free during testing.",
               "Jednorazový nákup plnej verzie, nie predplatné. Počas testovania je všetko zadarmo.",
               "Einmalkauf der Vollversion, kein Abo. Während der Testphase ist alles kostenlos.",
               "Compra única de la versión completa, sin suscripción. Durante las pruebas todo es gratis.",
               "Jednorazowy zakup pełnej wersji, bez subskrypcji. W trakcie testów wszystko jest bezpłatne."],
  "own_terms": ["Vlastní zásady soukromí a podmínky má na svém webu", "It has its own privacy policy and terms on its website", "Vlastné zásady súkromia a podmienky má na svojom webe",
                "Eigene Datenschutzerklärung und Bedingungen auf der eigenen Website", "Tiene su propia política de privacidad y condiciones en su web", "Własna polityka prywatności i warunki na jej stronie"],
  "work_lead": ['Kancelář a profesionální nástroje pro firmy: faktury, e-maily, zakázky a klienti. Na webu i v telefonu, s vlastním účtem.', 'Office tools and professional software for businesses: invoices, email, jobs and clients. On the web and on your phone, with your own account.', 'Kancelária a profesionálne nástroje pre firmy: faktúry, e-maily, zákazky a klienti. Na webe aj v telefóne, s vlastným účtom.', 'Büro-Tools und Profi-Software für Unternehmen: Rechnungen, E-Mails, Aufträge und Kunden. Im Web und auf dem iPhone, mit eigenem Konto.', 'Herramientas de oficina y software profesional para empresas: facturas, correo, encargos y clientes. En la web y en el móvil, con tu propia cuenta.', 'Narzędzia biurowe i profesjonalne oprogramowanie dla firm: faktury, poczta, zlecenia i klienci. W przeglądarce i w telefonie, z własnym kontem.'],
  "acc_req": ['S účtem', 'Account', 'S účtom', 'Mit Konto', 'Con cuenta', 'Z kontem'],
  "acc_opt": ['Účet volitelný', 'Account optional', 'Účet voliteľný', 'Konto optional', 'Cuenta opcional', 'Konto opcjonalne'],
  "open_web": ['Otevřít web', 'Open web app', 'Otvoriť web', 'Web-App öffnen', 'Abrir la web', 'Otwórz w przeglądarce'],
  "platforms": ['Platformy', 'Platforms', 'Platformy', 'Plattformen', 'Plataformas', 'Platformy']
}

def t(key, lang):
    return T[key][LANGS.index(lang)]

COPYRIGHT = "© 2026 Lukáš Ochrana"
VERSION = "1.1"  # verze webu – zvýšit při každém nasazení (TOKENY.md, Verze)
# Podmínky užití – licence (13. 10. 2026), ve všech 6 jazycích (sk/de/es/pl a zdravotní sekce doplněny při auditu Lékárničky).
TERMS = {
  "cs": ("Podmínky užití", "Licence a autorská práva k aplikacím EasyForLife.", [
    ("Autorská práva", "Aplikace EasyForLife, jejich zdrojový kód, grafika, texty a názvy jsou autorským dílem. Autorská práva k nim i jejich názvy náleží Lukáši Ochranovi."),
    ("Licence", "Stažením aplikace získáváte nevýhradní a nepřenosnou licenci užívat ji pro svou osobní potřebu na zařízeních, která vlastníte nebo ovládáte, v rozsahu podmínek App Store (Standard EULA společnosti Apple)."),
    ("Co není dovoleno", "Bez předchozího písemného souhlasu autora není dovoleno aplikace ani jejich části kopírovat, upravovat, překládat, zpětně analyzovat (reverse engineering), dekompilovat, dále šířit, pronajímat ani jinak zpřístupňovat třetím osobám – vždy v mezích, které připouští české právo a právo EU (výjimky, které zákon výslovně dovoluje, zůstávají zachovány)."),
    ("Práva spotřebitele", "Tyto podmínky neomezují práva, která vám jako spotřebiteli náleží podle českého práva a práva EU a která nelze smluvně vyloučit."),
    ("Kontakt", "Dotazy k licenci posílejte na " + CONTACT + ". Všechna práva, která nejsou výslovně udělena, zůstávají vyhrazena."),
  ]),
  "en": ("Terms of Use", "Licence and copyright of EasyForLife apps.", [
    ("Copyright", "EasyForLife apps, including their source code, graphics, texts and names, are works protected by copyright. The copyright and the app names belong to Lukáš Ochrana."),
    ("Licence", "By downloading an app you receive a non-exclusive, non-transferable licence to use it for your personal purposes on devices you own or control, within the App Store terms (Apple's Standard EULA)."),
    ("What is not permitted", "Without the author's prior written consent you may not copy, modify, translate, reverse engineer, decompile, redistribute, rent or otherwise make available the apps or any part of them to third parties – always to the extent permitted by Czech and EU law (exceptions expressly allowed by law remain unaffected)."),
    ("Consumer rights", "These terms do not limit any rights you have as a consumer under Czech and EU law that cannot be excluded by contract."),
    ("Contact", "Send questions about the licence to " + CONTACT + ". All rights not expressly granted are reserved."),
  ]),
}

# Zdravotní upozornění (13. 10. 2026, audit Lékárničky) – sekce v podmínkách ve všech 6 jazycích.
HEALTH_TERMS = {
  "cs": ("Zdravotní aplikace nejsou lékařská rada", "Lékárnička, Pohodička, Fitko a další aplikace EasyForLife se zdravotní tematikou nejsou zdravotnickým prostředkem a nenahrazují lékaře, lékárníka ani jiného odborníka. Nedávají lékařské rady ani doporučení k léčbě či dávkování – jen ukládají záznamy a připomínají to, co si uživatel sám zadá. Za zadané údaje a rozhodnutí o léčbě odpovídá uživatel; vždy se řiďte pokyny lékaře a příbalovým letákem. V naléhavém případě volejte 112."),
  "en": ("Health apps are not medical advice", "Lékárnička (Medicine Cabinet), Pohodička, Fitko and other EasyForLife apps related to health are not medical devices and do not replace a doctor, pharmacist or other professional. They give no medical advice or recommendations on treatment or dosage – they only store records and remind you of what you entered yourself. You are responsible for the data you enter and for decisions about treatment; always follow your doctor's instructions and the package leaflet. In an emergency, call 112."),
  "sk": ("Zdravotné aplikácie nie sú lekárska rada", "Lékárnička, Pohodička, Fitko a ďalšie aplikácie EasyForLife so zdravotnou tematikou nie sú zdravotníckou pomôckou a nenahrádzajú lekára, lekárnika ani iného odborníka. Nedávajú lekárske rady ani odporúčania k liečbe či dávkovaniu – iba ukladajú záznamy a pripomínajú to, čo si používateľ sám zadá. Za zadané údaje a rozhodnutia o liečbe zodpovedá používateľ; vždy sa riaďte pokynmi lekára a príbalovým letákom. V naliehavom prípade volajte 112."),
  "de": ("Gesundheits-Apps sind keine ärztliche Beratung", "Lékárnička (Hausapotheke), Pohodička, Fitko und andere EasyForLife-Apps mit Gesundheitsbezug sind keine Medizinprodukte und ersetzen weder Arzt noch Apotheker oder andere Fachleute. Sie geben keine medizinischen Ratschläge oder Empfehlungen zu Behandlung oder Dosierung – sie speichern nur Einträge und erinnern an das, was Sie selbst eingegeben haben. Für die eingegebenen Daten und Behandlungsentscheidungen sind Sie verantwortlich; folgen Sie stets den Anweisungen Ihres Arztes und der Packungsbeilage. Im Notfall wählen Sie 112."),
  "es": ("Las apps de salud no son consejo médico", "Lékárnička (Botiquín), Pohodička, Fitko y otras apps de EasyForLife relacionadas con la salud no son productos sanitarios y no sustituyen a un médico, farmacéutico u otro profesional. No dan consejos médicos ni recomendaciones de tratamiento o dosis: solo guardan registros y recuerdan lo que el usuario ha introducido. El usuario es responsable de los datos introducidos y de las decisiones sobre su tratamiento; siga siempre las indicaciones de su médico y el prospecto. En caso de emergencia, llame al 112."),
  "pl": ("Aplikacje zdrowotne nie są poradą medyczną", "Lékárnička (Apteczka), Pohodička, Fitko i inne aplikacje EasyForLife o tematyce zdrowotnej nie są wyrobem medycznym i nie zastępują lekarza, farmaceuty ani innego specjalisty. Nie udzielają porad medycznych ani zaleceń dotyczących leczenia czy dawkowania – jedynie zapisują wpisy i przypominają o tym, co użytkownik sam wprowadził. Za wprowadzone dane i decyzje o leczeniu odpowiada użytkownik; zawsze stosuj się do zaleceń lekarza i ulotki. W nagłym wypadku dzwoń pod 112."),
}

TERMS["sk"] = ("Podmienky používania", "Licencia a autorské práva k aplikáciám EasyForLife.", [
    ("Autorské práva", "Aplikácie EasyForLife, ich zdrojový kód, grafika, texty a názvy sú autorským dielom. Autorské práva k nim aj ich názvy patria Lukášovi Ochranovi."),
    ("Licencia", "Stiahnutím aplikácie získavate nevýhradnú a neprenosnú licenciu používať ju pre svoju osobnú potrebu na zariadeniach, ktoré vlastníte alebo ovládate, v rozsahu podmienok App Store (Standard EULA spoločnosti Apple)."),
    ("Čo nie je dovolené", "Bez predchádzajúceho písomného súhlasu autora nie je dovolené aplikácie ani ich časti kopírovať, upravovať, prekladať, spätne analyzovať (reverse engineering), dekompilovať, ďalej šíriť, prenajímať ani inak sprístupňovať tretím osobám – vždy v medziach, ktoré pripúšťa české právo a právo EÚ (výnimky, ktoré zákon výslovne dovoľuje, zostávajú zachované)."),
    ("Práva spotrebiteľa", "Tieto podmienky neobmedzujú práva, ktoré vám ako spotrebiteľovi patria podľa českého práva a práva EÚ a ktoré nemožno zmluvne vylúčiť."),
    ("Kontakt", "Otázky k licencii posielajte na " + CONTACT + ". Všetky práva, ktoré nie sú výslovne udelené, zostávajú vyhradené."),
])
TERMS["de"] = ("Nutzungsbedingungen", "Lizenz und Urheberrecht der EasyForLife-Apps.", [
    ("Urheberrecht", "Die EasyForLife-Apps einschließlich Quellcode, Grafiken, Texten und Namen sind urheberrechtlich geschützte Werke. Das Urheberrecht und die App-Namen gehören Lukáš Ochrana."),
    ("Lizenz", "Mit dem Herunterladen einer App erhalten Sie eine nicht ausschließliche, nicht übertragbare Lizenz, sie für persönliche Zwecke auf Geräten zu nutzen, die Sie besitzen oder kontrollieren, im Rahmen der App-Store-Bedingungen (Standard-EULA von Apple)."),
    ("Was nicht erlaubt ist", "Ohne vorherige schriftliche Zustimmung des Autors dürfen die Apps oder Teile davon nicht kopiert, verändert, übersetzt, zurückentwickelt (Reverse Engineering), dekompiliert, weiterverbreitet, vermietet oder Dritten auf andere Weise zugänglich gemacht werden – stets im Rahmen des tschechischen und des EU-Rechts (gesetzlich ausdrücklich erlaubte Ausnahmen bleiben unberührt)."),
    ("Verbraucherrechte", "Diese Bedingungen schränken keine Rechte ein, die Ihnen als Verbraucher nach tschechischem und EU-Recht zustehen und vertraglich nicht ausgeschlossen werden können."),
    ("Kontakt", "Fragen zur Lizenz senden Sie bitte an " + CONTACT + ". Alle nicht ausdrücklich gewährten Rechte bleiben vorbehalten."),
])
TERMS["es"] = ("Condiciones de uso", "Licencia y derechos de autor de las apps de EasyForLife.", [
    ("Derechos de autor", "Las apps de EasyForLife, incluidos su código fuente, gráficos, textos y nombres, son obras protegidas por derechos de autor. Los derechos de autor y los nombres de las apps pertenecen a Lukáš Ochrana."),
    ("Licencia", "Al descargar una app obtienes una licencia no exclusiva e intransferible para usarla con fines personales en dispositivos que posees o controlas, dentro de las condiciones del App Store (EULA estándar de Apple)."),
    ("Lo que no está permitido", "Sin el consentimiento previo por escrito del autor no se permite copiar, modificar, traducir, aplicar ingeniería inversa, descompilar, redistribuir, alquilar ni poner a disposición de terceros las apps o partes de ellas, siempre dentro de lo que permite el derecho checo y de la UE (se mantienen las excepciones expresamente permitidas por la ley)."),
    ("Derechos del consumidor", "Estas condiciones no limitan los derechos que te corresponden como consumidor según el derecho checo y de la UE y que no pueden excluirse por contrato."),
    ("Contacto", "Envía tus preguntas sobre la licencia a " + CONTACT + ". Se reservan todos los derechos no concedidos expresamente."),
])
TERMS["pl"] = ("Warunki korzystania", "Licencja i prawa autorskie do aplikacji EasyForLife.", [
    ("Prawa autorskie", "Aplikacje EasyForLife, w tym ich kod źródłowy, grafika, teksty i nazwy, są utworami chronionymi prawem autorskim. Prawa autorskie i nazwy aplikacji należą do Lukáša Ochrany."),
    ("Licencja", "Pobierając aplikację, otrzymujesz niewyłączną i niezbywalną licencję na korzystanie z niej do celów osobistych na urządzeniach, które posiadasz lub kontrolujesz, w zakresie warunków App Store (Standard EULA firmy Apple)."),
    ("Czego nie wolno", "Bez uprzedniej pisemnej zgody autora nie wolno kopiować, modyfikować, tłumaczyć, poddawać inżynierii wstecznej, dekompilować, dalej rozpowszechniać, wynajmować ani w inny sposób udostępniać aplikacji lub ich części osobom trzecim – zawsze w granicach dopuszczalnych przez prawo czeskie i prawo UE (wyjątki wyraźnie dozwolone przez prawo pozostają nienaruszone)."),
    ("Prawa konsumenta", "Niniejsze warunki nie ograniczają praw przysługujących Ci jako konsumentowi na mocy prawa czeskiego i prawa UE, których nie można wyłączyć umową."),
    ("Kontakt", "Pytania dotyczące licencji wysyłaj na " + CONTACT + ". Wszelkie prawa, które nie zostały wyraźnie przyznane, są zastrzeżone."),
])
for _l, _h in HEALTH_TERMS.items():
    TERMS[_l][2].insert(3, _h)

def terms_slug(lang):
    """Adresa podmínek: /podminky/ (cs, sk), jinak /terms/ – odkaz z appek: https://easyforlife.cz/podminky/"""
    return "podminky" if lang in ("cs", "sk") else "terms"

def esc(s):
    return html.escape(s, quote=True)

def site_of(lang):
    """Na kterém webu jazyk běží: cz (čeština, dokud .eu neběží i ostatní), nebo eu."""
    return "cz" if lang == "cs" or not EU_LIVE else "eu"

def prefix(lang):
    return "" if lang == "cs" or (EU_LIVE and lang == "en") else f"/{lang}"

def host(lang):
    return CZ if site_of(lang) == "cz" else EU

def sup(lang):
    """Adresa podpory: /podpora/ (cs, sk), jinak /support/ – Support URL pro App Store."""
    return "podpora" if lang in ("cs", "sk") else "support"

def url(lang, slug=None):
    """Cesta v rámci webu daného jazyka."""
    p = prefix(lang)
    return f"{p}/{slug}/" if slug else f"{p}/"

def full(lang, slug=None):
    return host(lang) + url(lang, slug)

def _sl(slug, lang):
    return slug.get(lang) if isinstance(slug, dict) else slug

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
  "navigace": '<path d="M3 6.5 9 4l6 2.5L21 4v13.5L15 20l-6-2.5L3 20z"/><path d="M9 4v13.5M15 6.5V20"/>',
  "zdravi": '<path d="M12 20s-7.5-4.6-9-9.4C2 7.3 4.2 4.5 7.3 4.5c1.9 0 3.4 1 4.7 2.7 1.3-1.7 2.8-2.7 4.7-2.7 3.1 0 5.3 2.8 4.3 6.1-1.5 4.8-9 9.4-9 9.4z"/><path d="M6.5 12h2.5l1.5-2.5 2 5 1.5-2.5h3.5"/>',
  "kancelar": '<path d="M3 13.5 5.5 5h13l2.5 8.5V19a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/><path d="M3 13.5h5l1 2.5h6l1-2.5h5"/>',
  "firmy": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2M3 13h18"/>',
  "easylife": '<rect x="3" y="3" width="8" height="8" rx="2.5"/><rect x="13" y="3" width="8" height="8" rx="2.5"/><rect x="3" y="13" width="8" height="8" rx="2.5"/><circle cx="17" cy="17" r="4"/>',
  "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.8 3.5 5.8 3.5 9s-1 6.2-3.5 9c-2.5-2.8-3.5-5.8-3.5-9s1-6.2 3.5-9z"/>',
  "shield": '<path d="M12 22s8-3.5 8-10V5l-8-3-8 3v7c0 6.5 8 10 8 10z"/>',
}

def icon(name, cls="ico"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS.get(name, ICONS["easylife"])}</svg>'

LOGO = ('<svg class="logo" viewBox="0 0 32 32" aria-hidden="true"><rect x="2" y="2" width="13" height="13" rx="4" fill="#2563eb"/>'
        '<rect x="17" y="2" width="13" height="13" rx="4" fill="#e8731c"/><rect x="2" y="17" width="13" height="13" rx="4" fill="#0f9a62"/>'
        '<rect x="17" y="17" width="13" height="13" rx="6.5" fill="#8b46d9"/></svg>')

CSS = """
:root{--bg:#fbfaf6;--surface:#fff;--surface2:#f1efe9;--ink:#141518;--muted:#5c636d;--line:#e6e2d9;--shadow:0 2px 4px rgb(20 20 30/.05),0 18px 40px -18px rgb(20 20 30/.28);
--font:-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
--display:"Bricolage Grotesque",-apple-system,BlinkMacSystemFont,"SF Pro Display","Segoe UI",Roboto,sans-serif;
--blue:#2563eb;--orange:#f0761f;--green:#10a36a;--purple:#8b46d9;--pink:#e8457a;--yellow:#f5b829;color-scheme:light}
@media (prefers-color-scheme:dark){:root{--bg:#0d0e11;--surface:#17181c;--surface2:#212228;--ink:#f1f2f4;--muted:#a3a9b3;--line:#2a2c33;--shadow:0 2px 4px rgb(0 0 0/.3),0 20px 44px -18px rgb(0 0 0/.7);color-scheme:dark}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.55 var(--font);-webkit-font-smoothing:antialiased;overflow-x:hidden}
a{color:inherit}img{max-width:100%;display:block}
.wrap{max-width:76rem;margin:0 auto;padding:0 20px;position:relative}
.skip{position:absolute;left:-999px}.skip:focus{left:16px;top:12px;background:var(--surface);padding:8px 14px;border-radius:10px;z-index:99}
/* hlavička */
.top{position:relative;z-index:5;display:flex;align-items:center;justify-content:space-between;gap:12px 20px;flex-wrap:wrap;padding:18px 0}
.brand{display:flex;align-items:center;gap:10px;text-decoration:none;font:800 1.35rem/1 var(--display);letter-spacing:-.02em}
.logo{width:34px;height:34px;transition:transform .5s cubic-bezier(.3,1.6,.5,1)}.brand:hover .logo{transform:rotate(90deg)}
.nav{display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.nav>a{font-weight:700;font-size:.92rem;text-decoration:none;padding:7px 12px;border-radius:999px}.nav>a:hover{background:var(--surface2)}
.langs{display:flex;gap:2px;font-size:.74rem;font-weight:700;letter-spacing:.04em;background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:3px}
.langs a{padding:5px 8px;border-radius:999px;text-decoration:none;color:var(--muted)}
.langs a:hover{color:var(--ink)}.langs a[aria-current]{color:#fff;background:var(--ink)}
@media (prefers-color-scheme:dark){.langs a[aria-current]{color:var(--bg)}}
/* barevné skvrny v pozadí */
.blobs{position:absolute;inset:0;overflow:hidden;pointer-events:none;z-index:0}
.blobs i{position:absolute;width:46vmax;height:46vmax;border-radius:50%;filter:blur(70px);opacity:.32;animation:drift 22s ease-in-out infinite alternate}
.blobs i:nth-child(1){background:var(--b1,var(--blue));left:-14vmax;top:-18vmax}
.blobs i:nth-child(2){background:var(--b2,var(--orange));right:-16vmax;top:-6vmax;animation-delay:-7s;animation-duration:26s}
.blobs i:nth-child(3){background:var(--b3,var(--purple));left:28%;bottom:-30vmax;animation-delay:-13s;animation-duration:30s}
@media (prefers-color-scheme:dark){.blobs i{opacity:.22}}
@keyframes drift{0%{transform:translate(0,0) scale(1)}50%{transform:translate(6vmax,4vmax) scale(1.12)}100%{transform:translate(-4vmax,7vmax) scale(.94)}}
/* hero s létajícími ikonami */
.hero{position:relative;min-height:min(94vh,900px);display:grid;place-items:center;margin-top:-76px;padding:120px 0 90px;overflow:hidden;isolation:isolate}
.fly-layer{position:absolute;inset:80px 0 0;z-index:1}
.fly{position:absolute;left:var(--x);top:var(--y);width:calc(var(--s) * var(--k,1));transform:translate3d(calc(var(--mx,0) * var(--d) * -46px),calc(var(--my,0) * var(--d) * -46px + var(--sy,0) * var(--d) * -.35px),0);will-change:transform}
.pop{display:block;animation:pop .9s cubic-bezier(.2,1.5,.4,1) both;animation-delay:calc(var(--i) * 70ms + .1s)}
.fly img,.fly .mark{width:100%;height:auto;aspect-ratio:1;border-radius:23%;box-shadow:var(--shadow);animation:bob var(--t,7s) ease-in-out var(--del,0s) infinite;transform:rotate(var(--r));transition:filter .2s}
.fly a{display:block;border-radius:23%;transition:transform .35s cubic-bezier(.3,1.7,.5,1)}.fly a:hover{transform:scale(1.15) rotate(-6deg)}
@keyframes bob{0%,100%{transform:translateY(0) rotate(var(--r))}50%{transform:translateY(-16px) rotate(calc(var(--r) + 5deg))}}
@keyframes pop{0%{opacity:0;transform:scale(.2) rotate(-40deg)}100%{opacity:1;transform:none}}
.hero-in{position:relative;z-index:2;text-align:center;max-width:52rem;pointer-events:none}.hero-in a,.hero-in li{pointer-events:auto}
.kicker{display:inline-flex;align-items:center;gap:8px;font-weight:700;font-size:.9rem;background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:6px 14px;margin:0 0 22px;box-shadow:var(--shadow)}
.kicker .dot{width:9px;height:9px;border-radius:50%;background:var(--green);box-shadow:0 0 0 0 var(--green);animation:ping 2s infinite}
@keyframes ping{0%{box-shadow:0 0 0 0 rgb(16 163 106/.6)}80%,100%{box-shadow:0 0 0 10px rgb(16 163 106/0)}}
h1{font:800 clamp(2.6rem,7.4vw,6rem)/.98 var(--display);letter-spacing:-.045em;margin:0 0 22px;text-wrap:balance}
.hl{background:linear-gradient(100deg,var(--blue),var(--purple),var(--pink),var(--orange),var(--green),var(--blue));background-size:300% 100%;-webkit-background-clip:text;background-clip:text;color:transparent;animation:shine 9s linear infinite;padding-right:.04em}
@keyframes shine{to{background-position:300% 0}}
.lead{font-size:clamp(1.08rem,1.7vw,1.32rem);color:var(--muted);max-width:40rem;margin:0 auto 26px;text-wrap:pretty}
.pills{display:flex;flex-wrap:wrap;justify-content:center;gap:10px;padding:0;margin:0 0 30px;list-style:none}
.pills li{display:flex;align-items:center;gap:8px;border-radius:999px;padding:9px 16px 9px 12px;font-weight:800;font-size:.95rem;color:#fff;background:var(--pc);box-shadow:0 10px 24px -12px var(--pc);transform:rotate(var(--pr));transition:transform .3s cubic-bezier(.3,1.7,.5,1)}
.pills li:hover{transform:rotate(0) scale(1.06)}.pills .ico{width:18px;height:18px}
.btn{display:inline-flex;align-items:center;gap:8px;border-radius:999px;padding:9px 18px;font-weight:800;font-size:.95rem;text-decoration:none;background:var(--c,var(--ink));color:#fff;transition:transform .25s cubic-bezier(.3,1.7,.5,1),box-shadow .25s}
.btn:hover{transform:translateY(-2px) scale(1.03)}
.btn.big{padding:15px 28px;font-size:1.08rem;background:var(--ink);color:var(--bg);box-shadow:0 14px 30px -14px rgb(0 0 0/.5)}
.btn.big span{display:inline-block;animation:nudge 1.6s ease-in-out infinite}@keyframes nudge{50%{transform:translateY(4px)}}
/* běžící pás */
.mq-wrap{overflow:hidden;padding:30px 0 10px;margin:-30px 0 0}
.marquee{position:relative;z-index:3;background:var(--ink);color:var(--bg);transform:rotate(-3deg);margin:20px -20px 60px;padding:16px 0;overflow:hidden;box-shadow:var(--shadow)}
.marquee.two{transform:rotate(2.4deg);background:var(--yellow);color:#141518;margin-top:-70px;z-index:2}
.mq{display:flex;width:max-content;animation:mq 46s linear infinite}.marquee.two .mq{animation-direction:reverse;animation-duration:54s}
.marquee:hover .mq{animation-play-state:paused}
.mq a{display:flex;align-items:center;gap:12px;padding:0 26px;text-decoration:none;font:800 clamp(1.3rem,2.6vw,2rem)/1 var(--display);letter-spacing:-.02em;white-space:nowrap}
.mq a img,.mq a .mark{width:46px;height:46px;border-radius:23%;font-size:1.2rem}
.mq a::after{content:"✦";margin-left:26px;opacity:.5;font-size:.8em}
@keyframes mq{to{transform:translateX(-50%)}}
/* sekce a rodiny */
section{position:relative;padding:20px 0 70px}
.sec-head{margin:0 0 28px}.sec-head h2{font:800 clamp(2.2rem,5.4vw,4.2rem)/1 var(--display);letter-spacing:-.04em;margin:0 0 10px}.sec-head p{margin:0;color:var(--muted);font-size:1.12rem}
.family{margin:0 0 54px;scroll-margin-top:20px}
.fam-title{display:flex;align-items:center;gap:14px;font:800 clamp(1.6rem,3.4vw,2.4rem)/1 var(--display);letter-spacing:-.03em;margin:0 0 18px}
.fam-title .ico{width:52px;height:52px;padding:12px;border-radius:16px;color:#fff;background:var(--fc);transform:rotate(-8deg);box-shadow:0 12px 24px -12px var(--fc)}
.fam-title small{font:800 .85rem var(--font);letter-spacing:0;background:var(--surface2);color:var(--muted);border-radius:999px;padding:4px 10px}
/* bento dlaždice */
.bento{display:grid;grid-template-columns:repeat(4,1fr);grid-auto-rows:minmax(212px,auto);grid-auto-flow:dense;gap:16px}
.tile{--lift:0px;position:relative;display:flex;flex-direction:column;gap:6px;padding:20px;container-type:inline-size;border-radius:30px;overflow:hidden;isolation:isolate;
background:linear-gradient(155deg,color-mix(in oklab,var(--c) 26%,var(--surface)),color-mix(in oklab,var(--c) 7%,var(--surface)) 70%);border:1px solid color-mix(in oklab,var(--c) 22%,var(--line));
box-shadow:var(--shadow);transform:perspective(900px) rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg)) translateY(var(--lift));transition:transform .25s ease,box-shadow .25s}
.tile:hover{--lift:-6px}
@media (prefers-color-scheme:dark){.tile{background:linear-gradient(155deg,color-mix(in oklab,var(--c) 40%,var(--surface)),color-mix(in oklab,var(--c) 12%,var(--surface)) 75%)}.tile .ghost-icon{opacity:.22}}
.tile-top{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:flex-start;gap:8px}
.tile-body{margin-top:auto;padding-top:14px;display:flex;flex-direction:column;gap:6px;min-width:0}
.tile .app-icon{width:64px;height:64px;transform-origin:35% 35%;transition:transform .45s cubic-bezier(.3,1.7,.5,1)}
.tile:hover .app-icon{transform:rotate(-8deg) scale(1.06)}
@container (max-width:300px){.tile .chip .long{display:none}.tile .chip .short{display:inline}}
.tile .ghost-icon{position:absolute;right:-18%;bottom:-22%;width:70%;max-width:340px;aspect-ratio:1;border-radius:23%;opacity:.16;transform:rotate(18deg);z-index:-1;filter:saturate(1.3);transition:transform .8s ease}
.tile:hover .ghost-icon{transform:rotate(8deg) scale(1.06)}
.tile h3{font:800 1.3rem/1.1 var(--display);letter-spacing:-.02em;margin:0}.tile h3 a{text-decoration:none}
.tile h3 a::after{content:"";position:absolute;inset:0;z-index:1}
.tile p{margin:0;color:var(--muted);font-size:.93rem;line-height:1.38;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.tile .status{flex:none}
.tile .priv{position:relative;z-index:2;align-self:flex-start;font-size:.8rem;font-weight:700;color:var(--muted);text-decoration:none;margin-top:2px}.tile .priv:hover{color:var(--ink);text-decoration:underline}
.t-big{grid-column:span 2;grid-row:span 2;padding:28px}
.t-big .app-icon{width:132px;height:132px}
.t-big h3{font-size:clamp(1.8rem,3vw,2.6rem)}.t-big p{font-size:1.08rem;-webkit-line-clamp:3}
.t-wide{grid-column:span 2}.t-wide .ghost-icon{width:44%;right:-6%;bottom:-40%}
.chip{display:inline-flex;align-items:center;gap:6px;border-radius:999px;padding:5px 11px;font-weight:800;font-size:.76rem;background:var(--surface);color:var(--ink);box-shadow:0 2px 8px -4px rgb(0 0 0/.3)}
.chip.tf::before{content:"";width:7px;height:7px;border-radius:50%;background:var(--green)}
.chip.sep{background:color-mix(in srgb,var(--c,#b4536b) 16%,var(--surface))}
.chip.soon::before{content:"";width:7px;height:7px;border-radius:50%;background:var(--yellow)}
.ghost{font-size:.9rem;font-weight:700;color:var(--muted);text-decoration:none;padding:6px 6px}.ghost:hover{color:var(--ink);text-decoration:underline}
.app-icon{flex:none;border-radius:23%;box-shadow:0 6px 16px -8px rgb(0 0 0/.45)}
.mark{display:grid;place-items:center;color:#fff;font:800 1.8rem var(--display);background:linear-gradient(145deg,var(--c),color-mix(in srgb,var(--c) 65%,#000))}
.t-big .mark{font-size:3.6rem}
/* principy jako samolepky */
.stickers{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}
.sticker{padding:26px 22px;border-radius:28px;color:#fff;background:var(--sc);transform:rotate(var(--sr));box-shadow:0 20px 40px -22px var(--sc);transition:transform .35s cubic-bezier(.3,1.7,.5,1)}
.sticker:hover{transform:rotate(0) scale(1.03)}
.sticker .ico{width:46px;height:46px;padding:10px;border-radius:14px;background:rgb(255 255 255/.2)}
.sticker h3{font:800 1.45rem/1.1 var(--display);letter-spacing:-.02em;margin:16px 0 8px}.sticker p{margin:0;opacity:.92;font-size:.98rem}
/* zeď ikon */
.wall{position:relative;height:440px;overflow:hidden;border-radius:40px;margin:0 0 30px;background:#0d0e11;isolation:isolate}
.wall-grid{position:absolute;left:50%;top:50%;width:170%;display:grid;grid-template-columns:repeat(12,1fr);gap:18px;transform:translate(-50%,-50%) rotate(-14deg);animation:wall 40s linear infinite}
.wall-grid img,.wall-grid .mark{width:100%;height:auto;aspect-ratio:1;border-radius:23%;opacity:.9}
@keyframes wall{from{transform:translate(-50%,-38%) rotate(-14deg)}to{transform:translate(-50%,-62%) rotate(-14deg)}}
.wall::after{content:"";position:absolute;inset:0;background:radial-gradient(ellipse at center,rgb(13 14 17/.82) 0%,rgb(13 14 17/.55) 45%,rgb(13 14 17/.1) 100%);z-index:1}
.wall-text{position:absolute;inset:0;z-index:2;display:grid;place-items:center;text-align:center;padding:20px}
.wall-text h2{font:800 clamp(2rem,5.6vw,4.4rem)/1 var(--display);letter-spacing:-.04em;color:#fff;margin:0;max-width:16ch;text-wrap:balance}
/* odhalení při scrollu */
.js .rv{opacity:0;transform:translateY(34px) scale(.98);transition:opacity .7s ease,transform .8s cubic-bezier(.2,1,.3,1);transition-delay:var(--rd,0s)}
.js .rv.in{opacity:1;transform:none}
.js .tile.rv.in{transform:perspective(900px) rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg)) translateY(var(--lift))}
.js .sticker.rv.in{transform:rotate(var(--sr))}.js .sticker.rv.in:hover{transform:rotate(0) scale(1.03)}
/* patička */
footer{position:relative;margin-top:30px;padding:40px 0 50px;color:var(--muted);font-size:.92rem;border-top:1px solid var(--line)}
footer .row{display:flex;flex-wrap:wrap;justify-content:space-between;gap:16px 30px}footer p{margin:0 0 6px}footer a{color:var(--ink);font-weight:700}
footer .brand{margin:0 0 10px}
/* detail appky */
.app-top{position:relative;margin-top:-76px;padding:110px 0 70px;overflow:hidden;isolation:isolate}
.app-top .blobs i{opacity:.4}.app-top .blobs i:nth-child(1),.app-top .blobs i:nth-child(3){background:var(--c)}
.back{position:relative;z-index:3;display:inline-flex;align-items:center;gap:6px;color:var(--ink);text-decoration:none;font-weight:800;font-size:.95rem;background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:7px 14px 7px 10px;margin:0 0 28px}
.back:hover{transform:translateX(-3px)}.back .ico{width:18px;height:18px}
.app-head{position:relative;z-index:2;display:grid;grid-template-columns:1.2fr .8fr;gap:40px;align-items:center}
.app-head h1{font-size:clamp(3rem,9vw,7rem);margin:6px 0 12px}
.app-head .tag{font-size:clamp(1.15rem,2vw,1.5rem);color:var(--muted);margin:0 0 22px;max-width:30rem}
.hero-icon{justify-self:center;width:min(300px,70vw)}
.hero-icon .app-icon{width:100%;height:auto;aspect-ratio:1;border-radius:23%;box-shadow:0 40px 80px -30px var(--c),var(--shadow);animation:bob 6s ease-in-out infinite;--r:-6deg}
.hero-icon .mark{font-size:7rem}
.fam-chip{display:inline-flex;align-items:center;gap:7px;font-size:.9rem;font-weight:800;color:#fff;background:var(--fc);border-radius:999px;padding:6px 13px 6px 10px;text-decoration:none}.fam-chip .ico{width:17px;height:17px}
.actions{position:relative;z-index:2;display:flex;flex-wrap:wrap;align-items:center;gap:10px}
.detail{max-width:56rem;padding:10px 0 30px}
.desc p{font:600 clamp(1.25rem,2.3vw,1.6rem)/1.4 var(--display);letter-spacing:-.01em;margin:0 0 18px;text-wrap:pretty}
.desc p+p{font:400 1.1rem/1.55 var(--font);color:var(--muted);letter-spacing:0}
h2.sub{font:800 clamp(1.7rem,3.4vw,2.5rem)/1.05 var(--display);letter-spacing:-.035em;margin:52px 0 20px}
.features{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(6,1fr);gap:14px;counter-reset:f}
.features li{grid-column:span 2;position:relative;counter-increment:f;padding:22px 20px 20px;border-radius:24px;font-weight:700;font-size:1.05rem;line-height:1.35;
background:linear-gradient(160deg,color-mix(in oklab,var(--c) 20%,var(--surface)),var(--surface));border:1px solid color-mix(in oklab,var(--c) 20%,var(--line));box-shadow:var(--shadow)}
.features li:nth-child(1),.features li:nth-child(2){grid-column:span 3}
.features li::before{content:counter(f,decimal-leading-zero);display:block;font:800 2.2rem/1 var(--display);color:var(--c);margin:0 0 12px;letter-spacing:-.04em}
.shots{display:flex;gap:22px;overflow-x:auto;scroll-snap-type:x mandatory;padding:10px 4px 26px}
.shots img{flex:none;width:250px;height:auto;border-radius:34px;border:7px solid var(--ink);scroll-snap-align:start;box-shadow:var(--shadow)}
.shots img:nth-child(odd){transform:rotate(-2deg)}.shots img:nth-child(even){transform:rotate(2deg) translateY(12px)}
.links{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}
.link-row{position:relative;display:flex;gap:14px;align-items:center;background:var(--surface);border:1px solid var(--line);border-radius:22px;padding:14px 16px;box-shadow:var(--shadow);transition:transform .3s cubic-bezier(.3,1.7,.5,1)}
.link-row:hover{transform:translateY(-3px) rotate(-.6deg)}
.link-row .app-icon{width:54px;height:54px}.link-row b{display:block;font:800 1.1rem var(--display)}.link-row span{color:var(--muted);font-size:.95rem}
.link-row a{text-decoration:none}.link-row a::after{content:"";position:absolute;inset:0}
.note{display:flex;gap:10px;align-items:center;color:var(--muted);font-size:.95rem;margin:18px 0 0}.note .ico{width:18px;height:18px;flex:none}
.note a{color:var(--ink);font-weight:700}
.faq{background:var(--surface);border:1px solid var(--line);border-radius:20px;padding:0 20px;margin:0 0 12px;box-shadow:var(--shadow)}
.faq summary{cursor:pointer;font:800 1.08rem var(--display);padding:18px 0}.faq p{margin:0 0 18px;color:var(--muted)}
.page-top{position:relative;margin-top:-76px;padding:120px 0 30px;overflow:hidden;isolation:isolate}.page-top h1{position:relative;z-index:2}.page-top .lead{position:relative;z-index:2;margin-left:0}
.ico{flex:none}.solo{color:var(--muted);margin:-8px 0 16px;font-weight:600}
/* Začni tady – EasyForLife Hub */
.start{padding-top:0}
.start-card{position:relative;display:grid;grid-template-columns:1.1fr .9fr;gap:40px;align-items:center;padding:clamp(24px,4vw,56px);border-radius:44px;overflow:hidden;isolation:isolate;
background:linear-gradient(var(--surface),var(--surface)) padding-box,linear-gradient(120deg,var(--blue),var(--purple),var(--pink),var(--orange),var(--green)) border-box;border:3px solid transparent;box-shadow:var(--shadow)}
.start-card::before{content:"";position:absolute;inset:0;z-index:-1;background:radial-gradient(circle at 85% 20%,color-mix(in oklab,var(--blue) 18%,transparent),transparent 55%),radial-gradient(circle at 10% 100%,color-mix(in oklab,var(--orange) 16%,transparent),transparent 50%)}
.start-card h2{font:800 clamp(2.2rem,5vw,3.8rem)/1 var(--display);letter-spacing:-.04em;margin:0 0 14px}
.start-card .lead{margin:0 0 18px;text-align:left}.start-card .kicker{margin-bottom:16px}
.ticks{list-style:none;padding:0;margin:0 0 24px;display:grid;gap:8px}.ticks li{display:flex;gap:10px;align-items:center;font-weight:700}
.ticks .ico{width:24px;height:24px;padding:4px;border-radius:50%;background:var(--green);color:#fff}
.phone{justify-self:center;width:min(330px,100%);padding:12px;border-radius:44px;background:var(--ink);box-shadow:0 40px 80px -30px rgb(37 99 235/.45),var(--shadow);transform:rotate(3deg);animation:bob 7s ease-in-out infinite;--r:3deg}
.phone-in{border-radius:34px;background:var(--bg);padding:20px 16px 18px;min-height:380px}
.phone-head{display:flex;align-items:center;gap:10px;margin:0 0 14px}.phone-head .app-icon{width:34px;height:34px}.phone-head b{font:800 1.15rem var(--display)}
.phone ul{list-style:none;padding:0;margin:0;display:grid;gap:10px}
.phone li{display:flex;align-items:center;gap:12px;background:var(--surface);border:1px solid var(--line);border-radius:18px;padding:10px 12px}
.phone li .app-icon{width:40px;height:40px}.phone li b{display:block;font-size:.95rem;line-height:1.2}.phone li small{color:var(--muted);font-size:.82rem;font-weight:600}
/* Jak spolu appky spolupracují */
.eco-grid{display:grid;grid-template-columns:1.05fr .95fr;gap:44px;align-items:center}
.eco{position:relative;aspect-ratio:1;width:100%;max-width:620px;justify-self:center}
.eco svg{position:absolute;inset:0;width:100%;height:100%;overflow:visible}
.eco path{fill:none;stroke-linecap:round;transition:opacity .25s,stroke-width .25s}
.eco .link{stroke:var(--purple);stroke-width:.45;opacity:.55;stroke-dasharray:1.6 1.2;animation:flow 3s linear infinite}
.eco .feed{stroke:var(--blue);stroke-width:.25;opacity:.3;stroke-dasharray:.6 1.4;animation:flow 4s linear infinite reverse}
@keyframes flow{to{stroke-dashoffset:-11.2}}
.eco.focus path{opacity:.07}.eco.focus path.on{opacity:1;stroke-width:.8}
.node{position:absolute;width:11%;transform:translate(-50%,-50%);transition:transform .3s cubic-bezier(.3,1.7,.5,1),opacity .25s;z-index:2}
.node .app-icon{width:100%;height:auto;aspect-ratio:1}
.node:hover,.node.on{transform:translate(-50%,-50%) scale(1.22)}.eco.focus .node:not(.on){opacity:.35}
.node.center{left:50%;top:50%;width:22%;z-index:3}.node.center .app-icon{box-shadow:0 20px 50px -14px rgb(37 99 235/.55)}
.eco-ex{list-style:none;padding:0;margin:0;display:grid;gap:12px}
.eco-ex li{display:flex;align-items:center;gap:16px;background:var(--surface);border:1px solid var(--line);border-radius:22px;padding:14px 16px;box-shadow:var(--shadow);font-weight:600;line-height:1.4}
.eco-ex .pair{flex:none;display:flex;align-items:center;gap:6px}.eco-ex .pair .app-icon{width:40px;height:40px}.eco-ex .pair i{font-style:normal;font-weight:800;color:var(--muted)}
.eco-ex .hubrow{background:linear-gradient(120deg,color-mix(in oklab,var(--blue) 14%,var(--surface)),color-mix(in oklab,var(--purple) 12%,var(--surface)))}
@media (max-width:900px){.start-card,.eco-grid{grid-template-columns:1fr}.phone{transform:none;--r:0deg}}

.logo-mark{display:grid;place-items:center;background:#fff;padding:0;aspect-ratio:1}.logo-mark .logo{width:74%;height:auto;aspect-ratio:1}
.t-hero{grid-column:1/-1}.t-hero .app-icon{width:96px;height:96px}.t-hero h3{font-size:clamp(1.6rem,3vw,2.4rem)}.t-hero p{font-size:1.05rem}
.fam-duo{display:grid;grid-template-columns:1fr 1fr;gap:0 24px}.bento.two{grid-template-columns:repeat(2,1fr)}
.t-tall{grid-row:span 2}.t-tall .app-icon{width:96px;height:96px}.t-tall h3{font-size:1.6rem}.t-tall p{-webkit-line-clamp:4}
@media (max-width:980px){.fam-duo{grid-template-columns:1fr}}
@media (max-width:560px){.t-tall{grid-row:span 1}.t-tall .app-icon{width:52px;height:52px}.t-tall h3{font-size:1.1rem}.t-tall p{-webkit-line-clamp:2}}
.tile-foot{position:relative;z-index:2;display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px;margin-top:2px}.tile-foot .priv{margin:0}
.webl{display:inline-flex;align-items:center;gap:5px;font-size:.8rem;font-weight:800;color:var(--ink);text-decoration:none}.webl:hover{text-decoration:underline}.webl .ico,.btn .ico{width:16px;height:16px}
.chip.acc{background:color-mix(in oklab,var(--c,var(--blue)) 18%,var(--surface));font-size:.72rem;padding:3px 9px;box-shadow:none}
.chip.acc::before{content:"";width:12px;height:12px;background:currentColor;-webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2.4' stroke-linecap='round'%3E%3Ccircle cx='12' cy='8' r='4'/%3E%3Cpath d='M4 21a8 8 0 0 1 16 0'/%3E%3C/svg%3E") center/contain no-repeat}
.app-head .chip.acc{font-size:.85rem;padding:6px 12px}
.plats{display:flex;flex-wrap:wrap;gap:6px;margin:16px 0 0}.plats span{font-size:.8rem;font-weight:800;letter-spacing:.02em;border:1.5px solid var(--line);border-radius:8px;padding:3px 9px;color:var(--muted)}
/* Pro práci: tmavý blok s mřížkou */
.work{--bg:#0d0e11;--surface:#181a20;--surface2:#23252d;--ink:#f1f2f4;--muted:#a3a9b3;--line:#2c2f38;color:var(--ink);background:#0d0e11;border-radius:44px;padding:56px clamp(18px,4vw,48px) 20px;position:relative;overflow:hidden;isolation:isolate;
background-image:linear-gradient(rgb(255 255 255/.045) 1px,transparent 1px),linear-gradient(90deg,rgb(255 255 255/.045) 1px,transparent 1px);background-size:44px 44px}
.work::before{content:"";position:absolute;width:60%;aspect-ratio:1;right:-20%;top:-30%;border-radius:50%;background:radial-gradient(circle,#6366f1 0%,transparent 65%);opacity:.35;z-index:-1}
.work::after{content:"";position:absolute;width:50%;aspect-ratio:1;left:-15%;bottom:-25%;border-radius:50%;background:radial-gradient(circle,#d9480f 0%,transparent 65%);opacity:.25;z-index:-1}
.work .sec-head h2{background:linear-gradient(90deg,#fff,#a5b4fc);-webkit-background-clip:text;background-clip:text;color:transparent}
.work .tile{background:linear-gradient(155deg,color-mix(in oklab,var(--c) 34%,#181a20),#14161b 75%)}.chip .short{display:none}
html{overflow-x:hidden}
.fly-layer.small .fly{--k:.8}
.hero::after,.app-top::after,.page-top::after{content:"";position:absolute;left:0;right:0;bottom:0;height:140px;background:linear-gradient(rgb(0 0 0/0),var(--bg));z-index:0;pointer-events:none}
@media (max-width:980px){.bento{grid-template-columns:repeat(2,1fr)}.stickers{grid-template-columns:repeat(2,1fr)}}
@media (max-width:820px){.app-head{grid-template-columns:1fr}.hero-icon{grid-row:1;justify-self:start;width:150px}.features li,.features li:nth-child(-n+2){grid-column:span 6}
.fly{--k:.56}.fly.side,.fly-layer.small{display:none}.hero{padding:210px 0 170px;min-height:0}.wall{height:340px}}
@media (max-width:560px){.bento{grid-auto-rows:minmax(180px,auto);gap:12px}.t-big{grid-row:span 1;padding:18px}.t-big .app-icon{width:72px;height:72px}.t-hero .app-icon{width:64px;height:64px}.t-big h3{font-size:1.6rem}.t-big p{-webkit-line-clamp:2;font-size:.95rem}
.tile:not(.t-big) .chip .long{display:none}.tile:not(.t-big) .chip .short{display:inline}.tile{padding:16px;border-radius:24px}
.tile .app-icon{width:52px;height:52px}.tile h3{font-size:1.1rem}.tile p{font-size:.86rem}
.stickers{grid-template-columns:1fr}.nav>a{display:none}.marquee{margin-bottom:56px}.marquee.two{margin-top:-80px}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}.js .rv{opacity:1;transform:none}html{scroll-behavior:auto}}
"""

def head_script(lang, targets=None):
    """Výběr jazyka: uložená volba, jinak jazyk prohlížeče. Přesměrovává jen z české verze (targets: jazyk → adresa)."""
    js = "document.documentElement.className+=' js';"
    if lang == "cs" and targets:
        js += ("(function(){var M=" + json.dumps(targets) + ",s;"
               "try{s=localStorage.getItem('lang')}catch(e){}"
               "if(!s){var n=navigator.languages||[navigator.language||'cs'];s='en';"
               "for(var i=0;i<n.length;i++){var c=String(n[i]).slice(0,2).toLowerCase();if(M[c]){s=c;break}}}"
               "if(s!=='cs'&&M[s])location.replace(M[s]+location.hash)})();")
    return f"<script>{js}</script>"

FOOT_SCRIPT = """<script>
document.querySelectorAll('.langs a').forEach(function(a){a.addEventListener('click',function(){try{localStorage.setItem('lang',a.hreflang)}catch(e){}})});
(function(){
var els=document.querySelectorAll('.rv');
if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{rootMargin:'0px 0px -6% 0px'});els.forEach(function(el){io.observe(el)})}
else els.forEach(function(el){el.classList.add('in')});
if(matchMedia('(prefers-reduced-motion: reduce)').matches)return;
var h=document.querySelector('[data-par]');
if(h){var raf=0,mx=0,my=0,tick=function(){if(raf)return;raf=requestAnimationFrame(function(){raf=0;h.style.setProperty('--mx',mx.toFixed(3));h.style.setProperty('--my',my.toFixed(3));h.style.setProperty('--sy',Math.min(scrollY,1400))})};
addEventListener('pointermove',function(e){if(e.pointerType!=='mouse')return;mx=e.clientX/innerWidth-.5;my=e.clientY/innerHeight-.5;tick()},{passive:true});addEventListener('scroll',tick,{passive:true})}
document.querySelectorAll('[data-eco]').forEach(function(e){var set=function(id){e.classList.toggle('focus',!!id);
e.querySelectorAll('path').forEach(function(p){p.classList.toggle('on',!!id&&(p.dataset.a===id||p.dataset.b===id))});
e.querySelectorAll('.node').forEach(function(n){var on=!!id&&(n.dataset.id===id||[].some.call(e.querySelectorAll('path.on'),function(p){return p.dataset.a===n.dataset.id||p.dataset.b===n.dataset.id}));n.classList.toggle('on',on)})};
e.querySelectorAll('.node').forEach(function(n){n.addEventListener('mouseenter',function(){set(n.dataset.id)});n.addEventListener('focus',function(){set(n.dataset.id)})});e.addEventListener('mouseleave',function(){set(null)})});
document.querySelectorAll('.tile').forEach(function(t){t.addEventListener('pointermove',function(e){if(e.pointerType!=='mouse')return;var r=t.getBoundingClientRect();
t.style.setProperty('--rx',((e.clientY-r.top)/r.height-.5)*-7+'deg');t.style.setProperty('--ry',((e.clientX-r.left)/r.width-.5)*7+'deg')});
t.addEventListener('pointerleave',function(){t.style.removeProperty('--rx');t.style.removeProperty('--ry')})})
})();
</script>"""

def page(lang, slug, title, desc, body, operator, relative=True, langs=None):
    """slug: None (úvod), řetězec, nebo slovník jazyk → slug; langs: jazyky, ve kterých stránka existuje."""
    langs = langs or LANGS
    here = lambda l: url(l, _sl(slug, l)) if site_of(l) == site_of(lang) else full(l, _sl(slug, l))
    alts = "".join(f'<link rel="alternate" hreflang="{l}" href="{full(l, _sl(slug, l))}">' for l in langs)
    xd = "en" if "en" in langs else langs[0]
    alts += f'<link rel="alternate" hreflang="x-default" href="{full(xd, _sl(slug, xd))}">'
    targets = {l: here(l) for l in langs}
    BASE = host(lang)
    switch = "".join(f'<a href="{here(l)}" hreflang="{l}" lang="{l}" title="{LANG_NAMES[l]}"'
                     f'{" aria-current=\"true\"" if l == lang else ""}>{l.upper()}</a>' for l in langs)
    pol = f'/soukromi.html{"" if lang in ("cs", "sk") else "#en"}'
    doc = f"""<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
{head_script(lang, targets)}<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}"><meta name="version" content="{VERSION}">
<link rel="canonical" href="{full(lang, _sl(slug, lang))}">{alts}
<meta property="og:type" content="website"><meta property="og:site_name" content="EasyForLife"><meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{full(lang, _sl(slug, lang))}">
<meta property="og:image" content="{BASE}/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="icon" href="/favicon.png" sizes="64x64" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta name="theme-color" content="#fbfaf6" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#0d0e11" media="(prefers-color-scheme: dark)">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600..800&amp;display=swap">
<link rel="stylesheet" href="/site.css?v={zlib.crc32(CSS.encode()):x}"></head>
<body><a class="skip" href="#main">{t("skip", lang)}</a>
<div class="wrap"><header class="top"><a class="brand" href="{url(lang)}">{LOGO}EasyForLife</a>
<nav class="nav"><a href="{url(lang)}#apps">{t("apps", lang)}</a><a href="{url(lang, sup(lang))}">{t("support", lang)}</a>
<span class="langs" aria-label="{t("lang", lang)}">{switch}</span></nav></header></div>
<main id="main">{body}</main>
<footer><div class="wrap row"><div><a class="brand" href="{url(lang)}">{LOGO}EasyForLife</a><p>{t("made", lang)}</p>
<p>{t("operator", lang)}: {esc(operator[0 if lang in ("cs", "sk") else 1])}</p></div>
<p><a href="{url(lang, sup(lang))}">{t("support", lang)}</a> · <a href="{pol}">{t("policy", lang)}</a> · <a href="{url(lang, terms_slug(lang))}">{TERMS[lang][0]}</a></p>
<p>{COPYRIGHT}</p></div></footer>
{FOOT_SCRIPT}</body></html>
"""
    # Relativní odkazy – web jde otevřít i ze složky (náhled) a z libovolného hostu.
    if relative:
        path = url(lang, _sl(slug, lang)).strip("/")
        r = "../" * (path.count("/") + 1 if path else 0) or "./"
        doc = doc.replace('href="/', f'href="{r}').replace('src="/', f'src="{r}')
    return doc

# Rozmístění létajících ikon v hero: x, y, velikost, natočení, hloubka (parallax), side = na mobilu skrýt
FLY = [(3, 9, 128, -12, 1.4, 0), (79, 7, 150, 10, 1.6, 0), (15, 60, 92, 10, .8, 1), (21, 80, 118, -6, 1.2, 0),
       (88, 40, 96, -14, .9, 1), (72, 68, 128, 8, 1.3, 1), (88, 83, 76, -4, .6, 0), (30, 3, 64, 14, .5, 0),
       (62, 2, 78, -10, .7, 0), (6, 86, 62, 12, .4, 0), (56, 87, 68, -8, .6, 0), (39, 91, 54, 6, .4, 0),
       (95, 18, 56, -6, .4, 1), (2, 38, 70, 6, .5, 1), (46, 0, 46, -4, .3, 0)]
# Na detailu appky jen kolem velké ikony vpravo.
FLY_DETAIL = [(60, 6, 96, -12, 1.2, 1), (92, 12, 80, 10, 1.4, 1), (56, 66, 84, 8, .9, 1), (91, 70, 104, -8, 1.3, 1),
              (76, 86, 62, 12, .6, 1), (74, -4, 58, -6, .5, 1)]

class Site:
    def __init__(self, out, privacy_apps, external, operator):
        self.out = out
        self.operator = operator
        self.cat = json.loads(CATALOG.read_text(encoding="utf-8"))
        self.families = {f["id"]: f for f in self.cat["families"]}
        self.privacy = {a["slug"]: f"/{a['slug']}.html" for a in privacy_apps}
        self.colors = {a["slug"]: a["color"] for a in privacy_apps}
        self.external = {n: u for n, u in external}
        self.all_apps = [a for a in self.cat["apps"] if a["id"] not in HIDDEN]
        self.apps = self.all_apps
        for a in self.all_apps:
            f = CONTENT / f"{a['id']}.json"
            a["site"] = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
            if a["site"].get("account"):  # ověřený stav z repa appky má přednost před katalogem
                a["account"] = a["site"]["account"]
        self.by_id = {a["id"]: a for a in self.apps}

    def use(self, lang):
        """Appky viditelné v daném jazyce (pole `locales` v katalogu, např. Kulturník jen cs)."""
        self.apps = [a for a in self.all_apps if lang in (a.get("locales") or LANGS)]
        self.by_id = {a["id"]: a for a in self.apps}

    # --- obrázky ---
    def icon_source(self, app_id):
        given = self.by_id[app_id]["site"].get("icon") if app_id in self.by_id else None
        if given:
            path = pathlib.Path(given).expanduser()
            return path if path.exists() else None
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
                subprocess.run(["sips", "-Z", "440", str(src), "--out", str(tmp)], check=True, capture_output=True)
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
        if a["id"] == "easylife" and not self.has_icon(a):  # EasyForLife Hub: ikona = logo
            return f'<span class="app-icon logo-mark" aria-hidden="true">{LOGO}</span>'
        if (self.out / "icons" / f"{a['id']}.webp").exists():
            return f'<img class="app-icon" src="{self.icon_url(a)}" width="{size}" height="{size}" alt="" loading="lazy">'
        return f'<span class="app-icon mark" style="--c:{self.color(a)}" aria-hidden="true">{esc(a["name"][0])}</span>'

    def cta(self, a, lang):
        if a.get("store"):
            return f'<a class="btn" style="--c:{self.color(a)}" href="{esc(a["store"])}">{t("get", lang)}</a>'
        return f'<span class="chip">{t("testflight" if a["site"].get("status") == "testflight" else "soon", lang)}</span>'

    def privacy_link(self, a, lang, cls="ghost"):
        href = self.privacy.get(a["id"]) or self.external.get(a["name"]) or a["site"].get("privacy") or self.own_url(a, "privacy", lang)
        if not href:
            return ""
        if href.startswith("/") and lang not in ("cs", "sk"):
            href += "#en"
        return f'<a class="{cls}" href="{href}">{t("privacy", lang)}</a>'

    def icon_url(self, a):
        """Adresa ikony s verzí podle času souboru, ať se nová ikona neschová v cache prohlížeče."""
        return f'/icons/{a["id"]}.webp?v={int((self.out / "icons" / f"{a['id']}.webp").stat().st_mtime)}'

    def has_icon(self, a):
        return (self.out / "icons" / f"{a['id']}.webp").exists()

    def icon_first(self):
        return [a for a in self.apps if self.has_icon(a)] + [a for a in self.apps if not self.has_icon(a)]

    def status(self, a, lang):
        if a.get("store"):
            return f'<a class="btn" style="--c:{self.color(a)}" href="{esc(a["store"])}">{t("get", lang)}</a>'
        st = a["site"].get("status")
        if st == "live":  # běžící webová služba – stav neukazujeme, akce je „Otevřít web“
            return ""
        tf = st == "testflight"
        return (f'<span class="chip {"tf" if tf else "soon"}"><span class="long">{t("testflight" if tf else "soon", lang)}</span>'
                f'<span class="short">{"Beta" if tf else t("soon_short", lang)}</span></span>')

    def account(self, a, lang):
        acc = a.get("account") or "none"
        if acc == "none":
            return ""
        return f'<span class="chip acc {acc}">{t("acc_req" if acc == "required" else "acc_opt", lang)}</span>'

    def sep_chip(self, a, lang):
        return f'<span class="chip sep">{t("separate", lang)}</span>' if a.get("separate") else ""

    def web_btn(self, a, lang, cls="btn"):
        w = self.own_url(a, "web", lang)
        if not w or w.rstrip("/") in (CZ, EU):
            return ""
        return f'<a class="{cls}" style="--c:{self.color(a)}" href="{esc(w)}">{icon("globe")}{t("open_web", lang)}</a>'

    def tile(self, a, lang, size, k):
        big = f'<img class="ghost-icon" src="{self.icon_url(a)}" alt="" loading="lazy">' if self.has_icon(a) and size != "t-n" else ""
        return (f'<article class="tile {size} rv" style="--c:{self.color(a)};--rd:{k * 60}ms">{big}'
                f'<div class="tile-top">{self.app_icon(a, 132 if size == "t-big" else 64)}<div class="status">{self.status(a, lang)}</div></div>'
                f'<div class="tile-body"><h3><a href="{url(lang, a["id"])}">{esc(a["name"])}</a></h3><p>{esc(a["tagline"][lang])}</p>'
                f'<div class="tile-foot">{self.sep_chip(a, lang)}{self.account(a, lang)}{self.web_btn(a, lang, "webl")}{self.privacy_link(a, lang, "priv")}</div></div></article>')

    def bento(self, apps, lang, featured=True):
        """Velikosti dlaždic tak, aby 4sloupcová mřížka vyšla bez děr: první velká, zbytek doplnit širokými."""
        sizes = ["t-big" if featured and i == 0 else "t-n" for i in range(len(apps))]
        need = -sum({"t-big": 4, "t-wide": 2, "t-n": 1}[s] for s in sizes) % 4
        normals = [i for i, s in enumerate(sizes) if s == "t-n"]
        if need == 3 and normals:
            sizes[normals[-1]] = "t-big"
        else:
            for i in normals[::-1][:need]:
                sizes[i] = "t-wide"
        return '<div class="bento">' + "".join(self.tile(a, lang, s, k) for k, (a, s) in enumerate(zip(apps, sizes))) + "</div>"

    def families_html(self, fams, lang):
        """Rodiny pod sebou; sousední malé rodiny (1–2 appky) vedle sebe, ať v mřížce nejsou díry."""
        def one(fid, f, apps, duo=False):
            grid = self.bento(apps, lang) if not duo else (
                '<div class="bento two">' + "".join(self.tile(a, lang, "t-big" if len(apps) == 1 else "t-tall", k) for k, a in enumerate(apps)) + "</div>")
            return (f'<div class="family" id="{fid}"><h3 class="fam-title rv" style="--fc:{FAMILY_COLORS.get(fid, "#555")}">{icon(fid)}{esc(f["name"][lang])}'
                    f'<small>{len(apps)}</small></h3>{grid}</div>')
        out, i = "", 0
        while i < len(fams):
            if i + 1 < len(fams) and len(fams[i][2]) <= 2 and len(fams[i + 1][2]) <= 2:
                out += f'<div class="fam-duo">{one(*fams[i], duo=True)}{one(*fams[i + 1], duo=True)}</div>'
                i += 2
            elif len(fams[i][2]) == 1:  # samotná appka v rodině (EasyForLife Hub) – dlaždice přes celou šířku
                fid, f, apps = fams[i]
                out += (f'<div class="family" id="{fid}"><h3 class="fam-title rv" style="--fc:{FAMILY_COLORS.get(fid, "#555")}">{icon(fid)}{esc(f["name"][lang])}</h3>'
                        f'<div class="bento">{self.tile(apps[0], lang, "t-hero", 0)}</div></div>')
                i += 1
            else:
                out += one(*fams[i])
                i += 1
        return out

    def partners(self, a, lang):
        """Se kterými appkami spolupracuje: eco.LINKS (oba směry), EasyForLife Hub, pak ruční odkazy z site/apps."""
        out = {}
        for x, y, txt in eco.LINKS:
            other = y if x == a["id"] else x if y == a["id"] else None
            if other in self.by_id:
                out.setdefault(other, []).append(txt[lang])
        if "easylife" in self.by_id:
            if a["id"] in eco.HUB_FEEDS:
                out.setdefault("easylife", []).append(eco.HUB_TEXT[lang].format(a=a["name"]))
            if a["id"] == "easylife":
                for f in eco.HUB_FEEDS:
                    if f in self.by_id:
                        out.setdefault(f, []).append(eco.HUB_IN[lang].format(a=self.by_id[f]["name"]))
        for l in a["site"].get("links", []):
            if l["app"] in self.by_id and l["app"] not in out:
                out[l["app"]] = [l["text"][lang]]
        return [(self.by_id[o], " ".join(txts)) for o, txts in out.items()]

    def start_here(self, lang):
        hub = self.by_id.get("easylife")
        if not hub:
            return ""
        s = hub["site"]
        desc = (s.get("description", {}).get(lang) or [hub["tagline"][lang]])[0]
        feats = "".join(f"<li>{icon('check')}{esc(x)}</li>" for x in (s.get("features", {}).get(lang) or [])[:4])
        rows = "".join(f'<li style="--rd:{k * 120 + 300}ms" class="rv">{self.app_icon(self.by_id[i], 40)}<span><b>{esc(ti[lang])}</b><small>{esc(when[lang])}</small></span></li>'
                       for k, (i, ti, when) in enumerate(eco.HUB_MOCK) if i in self.by_id)
        return (f'<section class="start"><div class="wrap"><div class="start-card rv"><div class="start-text">'
                f'<p class="kicker"><span class="dot"></span>{t("start", lang)}</p><h2>{esc(hub["name"])}</h2><p class="lead">{esc(desc)}</p>'
                f'<ul class="ticks">{feats}</ul><div class="actions"><a class="btn big" href="{url(lang, hub["id"])}">{t("hub_more", lang)} <span>→</span></a>{self.status(hub, lang)}</div></div>'
                f'<div class="phone" aria-hidden="true"><div class="phone-in"><div class="phone-head">{self.app_icon(hub, 34)}<b>{t("today", lang)}</b></div><ul>{rows}</ul></div></div>'
                f'</div></div></section>')

    def eco_section(self, lang):
        """Kruh appek s čarami propojení, uprostřed Hub; vedle příklady."""
        ids = []
        for x, y, _ in eco.LINKS:
            for i in (x, y):
                if i in self.by_id and i not in ids:
                    ids.append(i)
        ids += [i for i in eco.HUB_FEEDS if i in self.by_id and i not in ids]
        ids.sort(key=lambda i: [a["id"] for a in self.apps].index(i))
        if len(ids) < 3:
            return ""
        pos = {}
        for k, i in enumerate(ids):
            ang = -math.pi / 2 + 2 * math.pi * k / len(ids)
            pos[i] = (50 + 41 * math.cos(ang), 50 + 41 * math.sin(ang))
        hub = "easylife" in self.by_id
        lines = ""
        if hub:
            for i in eco.HUB_FEEDS:
                if i in pos:
                    x, y = pos[i]
                    lines += f'<path class="feed" data-a="{i}" data-b="easylife" d="M{x:.1f} {y:.1f} L50 50"/>'
        for x, y, _ in eco.LINKS:
            if x in pos and y in pos:
                (x1, y1), (x2, y2) = pos[x], pos[y]
                cx, cy = 50 + ((x1 + x2) / 2 - 50) * .35, 50 + ((y1 + y2) / 2 - 50) * .35
                lines += f'<path class="link" data-a="{x}" data-b="{y}" d="M{x1:.1f} {y1:.1f} Q{cx:.1f} {cy:.1f} {x2:.1f} {y2:.1f}"/>'
        nodes = "".join(f'<a class="node" data-id="{i}" href="{url(lang, i)}" style="left:{pos[i][0]:.1f}%;top:{pos[i][1]:.1f}%" title="{esc(self.by_id[i]["name"])}">'
                        f'{self.app_icon(self.by_id[i], 56)}</a>' for i in ids)
        if hub:
            nodes += f'<a class="node center" data-id="easylife" href="{url(lang, "easylife")}" title="{esc(self.by_id["easylife"]["name"])}">{self.app_icon(self.by_id["easylife"], 96)}</a>'
        txt = {(x, y): tx for x, y, tx in eco.LINKS}
        ex = "".join(f'<li class="rv" style="--rd:{k * 80}ms"><span class="pair">{self.app_icon(self.by_id[x], 40)}<i>→</i>{self.app_icon(self.by_id[y], 40)}</span><span>{esc(txt[(x, y)][lang])}</span></li>'
                     for k, (x, y) in enumerate(eco.EXAMPLES) if x in self.by_id and y in self.by_id)
        if hub:
            ex += f'<li class="rv hubrow"><span class="pair">{self.app_icon(self.by_id["easylife"], 40)}</span><span><b>{t("eco_hub", lang)}</b></span></li>'
        return (f'<section id="spoluprace"><div class="wrap"><div class="sec-head rv"><h2>{t("eco_title", lang)}</h2><p>{t("eco_lead", lang)}</p></div>'
                f'<div class="eco-grid"><div class="eco rv" data-eco><svg viewBox="0 0 100 100" aria-hidden="true">{lines}</svg>{nodes}</div>'
                f'<div><ul class="eco-ex">{ex}</ul><p class="note">{icon("link")}<span>{t("eco_hint", lang)}</span></p></div></div></div></section>')

    def family_apps(self, fid):
        """Appky rodiny; appka se může ukázat i v další rodině (`also_families` v site/apps, např. FotoDesk i ve Foto)."""
        return [a for a in self.apps if not a.get("separate") and (a["family"] == fid or fid in a["site"].get("also_families", []))]

    def own_url(self, a, key, lang):
        """Vlastní web / zásady samostatného projektu: `web`/`privacy` česky a slovensky, `webEn`/`privacyEn` jinak."""
        return a.get(key) if lang in ("cs", "sk") else (a.get(key + "En") or a.get(key))

    def projects(self, lang):
        """Samostatné projekty (`separate` v katalogu, např. Svatebníček) – mimo rodiny a rodinné předplatné."""
        apps = [a for a in self.apps if a.get("separate")]
        if not apps:
            return ""
        cards = "".join(self.tile(a, lang, "t-hero", k) for k, a in enumerate(apps))
        return (f'<section id="projekty"><div class="wrap"><div class="sec-head rv"><h2>{t("projects", lang)}</h2><p>{t("projects_lead", lang)}</p></div>'
                f'<div class="bento">{cards}</div></div></section>')

    def separate_note(self, a, lang):
        if not a.get("separate"):
            return ""
        web, priv = self.own_url(a, "web", lang), self.own_url(a, "privacy", lang)
        txt = t("one_time", lang) if a.get("pricing") == "oneTime" else ""
        terms = self.own_url(a, "terms", lang)
        links = (f' <a href="{esc(web)}">{esc(web.split("//")[-1])}</a>' if web else "") + (f' · <a href="{esc(priv)}">{t("privacy", lang)}</a>' if priv else "") \
            + (f' · <a href="{esc(terms)}">{TERMS[lang][0]}</a>' if terms else "")
        return f'<p class="note">{icon("link")}<span><b>{t("separate", lang)}.</b> {txt} {t("own_terms", lang)}:{links}</span></p>'


    def fly_icons(self, apps, layout=FLY):
        out = ""
        for i, (a, (x, y, s, r, d, side)) in enumerate(zip(apps, layout)):
            st = f"--x:{x}%;--y:{y}%;--s:{s}px;--r:{r}deg;--d:{d};--t:{6 + (i * 7) % 5}s;--del:-{(i * 13) % 7}s;--i:{i}"
            out += (f'<span class="fly{" side" if side else ""}" style="{st}"><span class="pop"><a href="{{u}}{a["id"]}/" tabindex="-1" title="{esc(a["name"])}">'
                    f'{self.app_icon(a, s).replace(" loading=\"lazy\"", "")}</a></span></span>')
        return out

    def marquee(self, apps, lang, cls=""):
        items = "".join(f'<a href="{url(lang, a["id"])}" tabindex="-1">{self.app_icon(a, 46)}{esc(a["name"])}</a>' for a in apps)
        return f'<div class="marquee {cls}" aria-hidden="true"><div class="mq">{items}{items}</div></div>'

    # --- stránky ---
    def home(self, lang):
        i = LANGS.index(lang)
        pc = [("eye-off", "var(--pink)", "-3deg"), ("user-x", "var(--blue)", "2deg"), ("globe", "var(--green)", "-1.5deg")]
        pills = "".join(f'<li style="--pc:{c};--pr:{r}">{icon(n)}{t("pills", lang)[k]}</li>' for k, (n, c, r) in enumerate(pc))
        h = t("hero", lang).replace(t("hero_hl", lang), f'<span class="hl">{t("hero_hl", lang)}</span>')
        fly = self.fly_icons(self.icon_first()).replace("{u}", url(lang))
        fams = ""
        groups = {"main": [], "work": []}
        for fid, f in self.families.items():
            apps = self.family_apps(fid)
            if apps:
                if fid == "easylife" and "easylife" in self.by_id:
                    continue
                groups["work" if fid in WORK else "main"].append((fid, f, apps))
        fams, work = self.families_html(groups["main"], lang), self.families_html(groups["work"], lang)
        sc = [("user-x", "var(--blue)", "-2deg"), ("eye-off", "var(--pink)", "1.5deg"), ("lock", "var(--green)", "-1deg"), ("link", "var(--orange)", "2deg")]
        prin = "".join(f'<div class="sticker rv" style="--sc:{c};--sr:{r};--rd:{k * 90}ms">{icon(n)}<h3>{esc(hd)}</h3><p>{esc(p)}</p></div>'
                       for k, ((n, c, r), (hd, p)) in enumerate(zip(sc, T["principles"][i])))
        order = self.icon_first()
        wall = "".join(self.app_icon(a, 120) for a in (order * 7)[:96])
        body = (f'<section class="hero" data-par><div class="blobs"><i></i><i></i><i></i></div><div class="fly-layer" aria-hidden="true">{fly}</div>'
                f'<div class="wrap hero-in"><p class="kicker"><span class="dot"></span>{t("count", lang).format(n=len([a for a in self.apps if not a.get("separate")]))}</p>'
                f'<h1>{h}</h1><p class="lead">{t("lead", lang)}</p><ul class="pills">{pills}</ul>'
                f'<a class="btn big" href="#apps">{t("cta_apps", lang)} <span>↓</span></a></div></section>'
                + '<div class="mq-wrap">' + self.marquee(order, lang) + self.marquee(order[::-1], lang, "two") + "</div>"
                + self.start_here(lang) +
                f'<section id="apps"><div class="wrap"><div class="sec-head rv"><h2>{t("apps", lang)}</h2><p>{t("apps_lead", lang)}</p></div>{fams}</div></section>'
                + self.projects(lang)
                + self.eco_section(lang)
                + (f'<section id="prace"><div class="wrap"><div class="work"><div class="sec-head rv"><h2>{t("work", lang)}</h2><p>{t("work_lead", lang)}</p></div>{work}</div></div></section>' if work else "") +
                f'<section><div class="wrap"><div class="sec-head rv"><h2>{t("how", lang)}</h2></div><div class="stickers">{prin}</div></div></section>'
                f'<section><div class="wrap"><div class="wall rv"><div class="wall-grid" aria-hidden="true">{wall}</div>'
                f'<div class="wall-text"><h2>{t("wall", lang)}</h2></div></div></div></section>')
        return page(lang, None, t("title", lang), t("lead", lang), body, self.operator)

    def support(self, lang):
        i = LANGS.index(lang)
        mail = f"mailto:{CONTACT}?subject=EasyForLife"
        faq = "".join(f'<details class="faq rv"><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in T["faq"][i])
        body = (f'<section class="page-top"><div class="blobs"><i></i><i></i><i></i></div><div class="wrap"><div class="detail">'
                f'<h1>{t("support_title", lang)}</h1><p class="lead">{t("support_lead", lang)}</p>'
                f'<p class="actions"><a class="btn big" href="{mail}">{t("support_mail", lang)} <span>→</span></a><a class="ghost" href="{mail}">{CONTACT}</a></p>'
                f'<p class="note">{icon("check")}<span>{t("support_hint", lang)}</span></p></div></div></section>'
                f'<div class="wrap"><div class="detail"><h2 class="sub">{t("faq_title", lang)}</h2>{faq}'
                f'<p class="note">{icon("shield")}<span><a href="/soukromi.html{"" if lang in ("cs", "sk") else "#en"}">{t("policy", lang)}</a></span></p></div></div>')
        return page(lang, {l: sup(l) for l in LANGS}, f'{t("support_title", lang)} | EasyForLife', t("support_lead", lang), body, self.operator)

    def terms(self, lang):
        title, lead, parts = TERMS[lang]
        secs = "".join(f'<h2 class="sub">{esc(h)}</h2><p>{esc(x)}</p>' for h, x in parts)
        body = (f'<section class="page-top"><div class="blobs"><i></i><i></i><i></i></div><div class="wrap"><div class="detail">'
                f'<h1>{esc(title)}</h1><p class="lead">{esc(lead)}</p></div></div></section>'
                f'<div class="wrap"><div class="detail">{secs}<p class="note">{icon("shield")}<span>{esc(COPYRIGHT)} · '
                f'<a href="/soukromi.html{"" if lang in ("cs", "sk") else "#en"}">{t("policy", lang)}</a></span></p></div></div>')
        return page(lang, {l: terms_slug(l) for l in LANGS}, f"{title} | EasyForLife", lead, body, self.operator)

    def detail(self, a, lang):
        s, c, fam = a["site"], self.color(a), self.families[a["family"]]
        fc = FAMILY_COLORS.get(a["family"], c)
        anchor = "projekty" if a.get("separate") else a["family"]
        fam_name = t("projects", lang) if a.get("separate") else esc(fam["name"][lang])
        desc = "".join(f"<p>{esc(p)}</p>" for p in (s.get("description", {}).get(lang) or []))
        feats = s.get("features", {}).get(lang) or []
        web = f'<a class="ghost" href="{esc(s["web"])}">{esc(s["web"].split("//")[-1].rstrip("/"))} ↗</a>' if s.get("web") else ""
        others = [] if a.get("separate") else [o for o in self.family_apps(a["family"]) if o["id"] != a["id"]]
        plats = ('<p class="plats">' + "".join(f'<span>{PLATFORMS.get(x, x)}</span>' for x in a["platforms"]) + "</p>") if a.get("platforms") else ""
        if a.get("web") and s.get("web") == a.get("web"):
            web = ""
        flyers = [o for o in others + [o for o in self.icon_first() if o not in others and o is not a] if self.has_icon(o)]
        fly = self.fly_icons(flyers[:6], FLY_DETAIL).replace("{u}", "/" if lang == "cs" else f"/{lang}/")
        p = self.privacy_link(a, lang, "")
        note = (f'{icon("shield")}<span>{p.replace(">" + t("privacy", lang) + "<", ">" + t("policy", lang) + t("policy_lang", lang) + "<")}</span>'
                if p else f'{icon("shield")}<span>{t("policy_soon", lang)}</span>')
        body = (f'<section class="app-top" style="--c:{c}" data-par><div class="blobs"><i></i><i></i><i></i></div>'
                f'<div class="fly-layer small" aria-hidden="true">{fly}</div><div class="wrap">'
                f'<a class="back" href="{url(lang)}#{anchor}">{icon("arrow-left")}{t("back", lang)}</a>'
                f'<div class="app-head"><div><a class="fam-chip" style="--fc:{fc}" href="{url(lang)}#{anchor}">{icon(a["family"])}{fam_name}</a>'
                f'<h1>{esc(a["name"])}</h1><p class="tag">{esc(a["tagline"][lang])}</p><div class="actions">{self.web_btn(a, lang)}{self.status(a, lang)}{self.sep_chip(a, lang)}{self.account(a, lang)}{web}</div>{plats}</div>'
                f'<div class="hero-icon">{self.app_icon(a, 300).replace(" loading=\"lazy\"", "")}</div></div></div></section>')
        body += f'<div class="wrap" style="--c:{c}"><article class="detail"><div class="desc rv">{desc}</div>'
        if feats:
            body += f'<h2 class="sub rv">{t("features", lang)}</h2><ul class="features">' + "".join(
                f'<li class="rv" style="--rd:{k * 70}ms">{esc(x)}</li>' for k, x in enumerate(feats)) + "</ul>"
        shots = a.get("shots") or []
        if shots:
            body += f'<h2 class="sub rv">{t("shots", lang)}</h2><div class="shots">' + "".join(
                f'<img src="/shots/{a["id"]}/{esc(x)}" alt="" loading="lazy" width="250" height="544">' for x in shots) + "</div>"
        links = self.partners(a, lang)
        if links:
            body += f'<h2 class="sub rv">{t("works_with", lang)}</h2><p class="solo">{esc(t("solo", lang).format(a=a["name"]))}</p><div class="links">' + "".join(
                f'<div class="link-row rv">{self.app_icon(o, 54)}<div><a href="{url(lang, o["id"])}"><b>{esc(o["name"])}</b></a><span>{esc(txt)}</span></div></div>'
                for o, txt in links) + "</div>"
        body += f'<p class="note">{note}</p>' + self.separate_note(a, lang)
        if not a.get("store"):
            body += f'<p class="note">{icon("check")}<span>{t("tf_note" if s.get("status") == "testflight" else "dev_note", lang)}</span></p>'
        body += "</article></div>"
        if others:
            body += (f'<section><div class="wrap"><div class="sec-head rv"><h2>{t("family_more", lang).format(f=esc(fam["name"][lang]))}</h2></div>'
                     f'{self.bento(others, lang, featured=len(others) > 2)}</div></section>')
        title = f'{a["name"]} – {a["tagline"][lang].rstrip(".")} | EasyForLife'
        return page(lang, a["id"], title, a["tagline"].get(lang, ""), body, self.operator, langs=[l for l in LANGS if l in (a.get("locales") or LANGS)])

    def write(self, rel, text, root=None):
        p = (root or self.out) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def build(self, force_art=False):
        # obrázky a styl do docs/ (sdílené), odtud se kopírují do obou webů
        self.apps, self.by_id = self.all_apps, {a["id"]: a for a in self.all_apps}
        self.copy_icons()
        self.copy_shots()
        self.art(force_art)
        (self.out / "site.css").write_text(CSS.strip() + "\n", encoding="utf-8")
        shutil.rmtree(DIST, ignore_errors=True)
        urls = {"cz": [], "eu": []}
        stubs = {}  # stará adresa v docs/ (GitHub Pages) → nová
        for lang in LANGS:
            self.use(lang)
            root = DIST / site_of(lang)
            pre = prefix(lang).lstrip("/")
            pre = pre + "/" if pre else ""
            old = "" if lang == "cs" else f"{lang}/"
            self.write(f"{pre}index.html", self.home(lang), root)
            self.write(f"{pre}{sup(lang)}/index.html", self.support(lang), root)
            self.write(f"{pre}{terms_slug(lang)}/index.html", self.terms(lang), root)
            urls[site_of(lang)] += [full(lang), full(lang, sup(lang)), full(lang, terms_slug(lang))]
            stubs[f"{old}index.html"] = full(lang)
            stubs[f"{old}podpora/index.html"] = full(lang, sup(lang))
            for a in self.apps:
                self.write(f"{pre}{a['id']}/index.html", self.detail(a, lang), root)
                urls[site_of(lang)].append(full(lang, a["id"]))
                stubs[f"{old}{a['id']}/index.html"] = full(lang, a["id"])
        assets = ["site.css", "og.png", "favicon.svg", "favicon.png", "apple-touch-icon.png", "soukromi.html"]
        assets += [p.lstrip("/") for p in self.privacy.values()]
        routes = {"hosts": {}, "redirects": []}
        for site in ("cz", "eu"):
            root = DIST / site
            if not root.exists():
                continue
            base = CZ if site == "cz" else EU
            routes["hosts"][base.split("//")[1]] = site
            for f in assets:
                if (self.out / f).exists():
                    shutil.copy2(self.out / f, root / f)
            for d in ("icons", "shots"):
                if (self.out / d).exists():
                    shutil.copytree(self.out / d, root / d)
            # Živý katalog pro appky (stahují si ho, aby nová propojení fungovala bez nového buildu)
            shutil.copy2(CATALOG, root / "catalog.json")
            urls[site] += [base + p for p in self.privacy.values()]
            self.write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                       + "".join(f"<url><loc>{u}</loc></url>\n" for u in urls[site]) + "</urlset>\n", root)
            self.write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n", root)
            l404 = "cs" if site == "cz" else "en"
            self.use(l404)
            nf = (f'<section class="page-top"><div class="wrap"><div class="detail"><h1>404</h1><p class="lead">{t("nf", l404)}</p>'
                  f'<p><a class="btn big" href="/">{t("back", l404)} <span>→</span></a></p></div></div></section>')
            self.write("404.html", page(l404, None, "404 – EasyForLife", "EasyForLife", nf, self.operator, relative=False).replace(head_script(l404, None), ""), root)
        if EU_LIVE:  # staré adresy jazyků na .cz → .eu
            routes["redirects"] += [{"host": "easyforlife.cz", "prefix": f"/{l}/", "to": EU + prefix(l) + "/"} for l in LANGS if l != "cs"]
        else:  # .eu zatím bez vlastního webu → anglická verze na .cz
            routes["redirects"].append({"host": "easyforlife.eu", "prefix": "/", "to": CZ + "/en/", "files_to": CZ + "/"})
        (DIST / "routes.json").write_text(json.dumps(routes, indent=1) + "\n", encoding="utf-8")
        # docs/ (GitHub Pages): jen zásady soukromí a obrázky, ostatní stránky přesměrují na novou adresu
        for d in list(self.out.iterdir()):
            if d.is_dir() and d.name not in ("icons", "shots"):
                shutil.rmtree(d)
        for f in ("sitemap.xml", "robots.txt", "CNAME"):
            (self.out / f).unlink(missing_ok=True)
        for rel, target in stubs.items():
            self.write(rel, f'<!doctype html><meta charset="utf-8"><title>EasyForLife</title><link rel="canonical" href="{target}">'
                            f'<meta http-equiv="refresh" content="0;url={target}"><script>location.replace({json.dumps(target)}+location.hash)</script>'
                            f'<a href="{target}">{target}</a>\n')
        self.write("404.html", (self.out / "index.html").read_text(encoding="utf-8"))
        return {k: len(v) for k, v in urls.items()} | {"eu_live": EU_LIVE}

def build(out, privacy_apps, external, operator):
    if not CATALOG.exists():
        print("web: chybí", CATALOG, "– web se negeneruje")
        return
    print("web", Site(out, privacy_apps, external, operator).build("--art" in sys.argv))
