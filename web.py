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
CONTACT = "info@luksafoto.cz"  # kontakt podpory, dokud easyforlife.eu nemá vlastní e-mail
SUPPORT = "podpora"           # /podpora/ = Support URL pro App Store
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
  "hero_hl": ["zjednoduší život", "life easier", "zjednodušia život", "leichter", "más fácil", "ułatwiają życie"],
  "count": ["{n} appek pro iPhone a pořád přibývají", "{n} iPhone apps and counting", "{n} aplikácií pre iPhone a stále pribúdajú",
            "{n} iPhone-Apps und es werden mehr", "{n} apps para iPhone y contando", "{n} aplikacji na iPhone’a i wciąż przybywa"],
  "cta_apps": ["Prohlédnout appky", "Explore the apps", "Pozrieť aplikácie", "Apps entdecken", "Ver las apps", "Zobacz aplikacje"],
  "wall": ["Jedna rodina. Žádné účty. Žádné reklamy.", "One family. No accounts. No ads.", "Jedna rodina. Žiadne účty. Žiadne reklamy.",
           "Eine Familie. Keine Konten. Keine Werbung.", "Una familia. Sin cuentas. Sin anuncios.", "Jedna rodzina. Bez kont. Bez reklam."],
  "support": ["Podpora", "Support", "Podpora", "Support", "Soporte", "Wsparcie"],
  "support_title": ["Podpora a kontakt", "Support and contact", "Podpora a kontakt", "Support und Kontakt", "Soporte y contacto", "Wsparcie i kontakt"],
  "support_lead": ["Něco nefunguje, máš nápad nebo dotaz k některé appce EasyLife? Napiš nám, odpovídáme obvykle do pár dní.",
                   "Something not working, got an idea or a question about an EasyLife app? Write to us – we usually reply within a few days.",
                   "Niečo nefunguje, máš nápad alebo otázku k niektorej aplikácii EasyLife? Napíš nám, odpovedáme zvyčajne do pár dní.",
                   "Funktioniert etwas nicht, hast du eine Idee oder eine Frage zu einer EasyLife-App? Schreib uns – wir antworten meist innerhalb weniger Tage.",
                   "¿Algo no funciona, tienes una idea o una pregunta sobre una app de EasyLife? Escríbenos; solemos responder en pocos días.",
                   "Coś nie działa, masz pomysł albo pytanie o aplikację EasyLife? Napisz do nas – zwykle odpowiadamy w ciągu kilku dni."],
  "support_mail": ["Napsat e-mail", "Send an email", "Napísať e-mail", "E-Mail schreiben", "Enviar un correo", "Napisz e-mail"],
  "support_hint": ["Uveď prosím název appky, model iPhonu a verzi iOS. U chyby pomůže i snímek obrazovky.",
                   "Please mention the app name, your iPhone model and iOS version. For bugs, a screenshot helps too.",
                   "Uveď prosím názov aplikácie, model iPhonu a verziu iOS. Pri chybe pomôže aj snímka obrazovky.",
                   "Bitte nenne den App-Namen, dein iPhone-Modell und die iOS-Version. Bei Fehlern hilft auch ein Screenshot.",
                   "Indica el nombre de la app, tu modelo de iPhone y la versión de iOS. Si es un error, una captura de pantalla ayuda.",
                   "Podaj nazwę aplikacji, model iPhone’a i wersję iOS. Przy błędzie pomoże też zrzut ekranu."],
  "faq_title": ["Časté otázky", "FAQ", "Časté otázky", "Häufige Fragen", "Preguntas frecuentes", "Częste pytania"],
  "faq": [
    [("Potřebuju účet nebo registraci?", "Ne. Appky EasyLife fungují bez registrace a přihlašování. Jedinou výjimkou je Cestovníček, který účet používá kvůli synchronizaci s webem."),
     ("Kde jsou moje data?", "V tvém iPhonu, a pokud appka synchronizuje, v tvém soukromém iCloudu. My k nim přístup nemáme. Podrobnosti najdeš v zásadách ochrany soukromí každé appky."),
     ("Jak přenesu data na nový iPhone?", "Appky se synchronizací přes iCloud si data přenesou samy, když se na novém iPhonu přihlásíš stejným Apple ID. Ostatní data se přenesou se zálohou iPhonu."),
     ("Jak svá data smažu?", "Smazáním appky se smažou data v zařízení. Data v iCloudu smažeš v Nastavení → tvoje jméno → iCloud → Spravovat úložiště."),
     ("Jak se dostanu do beta verze?", "Některé appky jsou zatím v beta testu přes TestFlight. Napiš nám e-mail a pošleme ti pozvánku."),
     ("Mám nápad na novou funkci", "Sem s ním! Napiš nám e-mail – nápady od uživatelů čteme všechny.")],
    [("Do I need an account?", "No. EasyLife apps work without sign-up or login. The only exception is Cestovníček, which uses an account to sync with the web."),
     ("Where is my data?", "On your iPhone and, if the app syncs, in your private iCloud. We have no access to it. Each app’s privacy policy has the details."),
     ("How do I move my data to a new iPhone?", "Apps that sync via iCloud move your data automatically when you sign in with the same Apple ID. Everything else comes over with your iPhone backup."),
     ("How do I delete my data?", "Deleting the app removes the data on your device. Data in iCloud can be deleted in Settings → your name → iCloud → Manage Storage."),
     ("How do I join a beta?", "Some apps are still in beta testing on TestFlight. Send us an email and we’ll invite you."),
     ("I have an idea for a feature", "Great! Send us an email – we read every suggestion.")],
    [("Potrebujem účet alebo registráciu?", "Nie. Aplikácie EasyLife fungujú bez registrácie a prihlasovania. Jedinou výnimkou je Cestovníček, ktorý účet používa kvôli synchronizácii s webom."),
     ("Kde sú moje dáta?", "V tvojom iPhone a ak aplikácia synchronizuje, v tvojom súkromnom iCloude. My k nim prístup nemáme. Podrobnosti nájdeš v zásadách ochrany súkromia každej aplikácie."),
     ("Ako prenesiem dáta do nového iPhonu?", "Aplikácie so synchronizáciou cez iCloud si dáta prenesú samy, keď sa na novom iPhone prihlásiš rovnakým Apple ID. Ostatné dáta sa prenesú so zálohou iPhonu."),
     ("Ako svoje dáta zmažem?", "Zmazaním aplikácie sa zmažú dáta v zariadení. Dáta v iCloude zmažeš v Nastaveniach → tvoje meno → iCloud → Spravovať úložisko."),
     ("Ako sa dostanem do beta verzie?", "Niektoré aplikácie sú zatiaľ v beta teste cez TestFlight. Napíš nám e-mail a pošleme ti pozvánku."),
     ("Mám nápad na novú funkciu", "Sem s ním! Napíš nám e-mail – nápady od používateľov čítame všetky.")],
    [("Brauche ich ein Konto?", "Nein. EasyLife-Apps funktionieren ohne Registrierung und Login. Einzige Ausnahme ist Cestovníček, das ein Konto für die Synchronisierung mit dem Web nutzt."),
     ("Wo sind meine Daten?", "Auf deinem iPhone und, wenn die App synchronisiert, in deiner privaten iCloud. Wir haben keinen Zugriff darauf. Details stehen in der Datenschutzerklärung jeder App."),
     ("Wie übertrage ich meine Daten auf ein neues iPhone?", "Apps mit iCloud-Synchronisierung übernehmen deine Daten automatisch, wenn du dich mit derselben Apple-ID anmeldest. Alles andere kommt mit dem iPhone-Backup mit."),
     ("Wie lösche ich meine Daten?", "Wenn du die App löschst, werden die Daten auf dem Gerät gelöscht. Daten in iCloud löschst du unter Einstellungen → dein Name → iCloud → Speicher verwalten."),
     ("Wie komme ich in eine Beta?", "Einige Apps sind noch in der Beta-Phase über TestFlight. Schreib uns eine E-Mail und wir laden dich ein."),
     ("Ich habe eine Idee für eine Funktion", "Her damit! Schreib uns eine E-Mail – wir lesen jeden Vorschlag.")],
    [("¿Necesito una cuenta?", "No. Las apps de EasyLife funcionan sin registro ni inicio de sesión. La única excepción es Cestovníček, que usa una cuenta para sincronizarse con la web."),
     ("¿Dónde están mis datos?", "En tu iPhone y, si la app sincroniza, en tu iCloud privado. Nosotros no tenemos acceso. La política de privacidad de cada app tiene los detalles."),
     ("¿Cómo paso mis datos a un iPhone nuevo?", "Las apps que sincronizan por iCloud traen tus datos solas al iniciar sesión con el mismo Apple ID. El resto se transfiere con la copia de seguridad del iPhone."),
     ("¿Cómo borro mis datos?", "Al eliminar la app se borran los datos del dispositivo. Los datos de iCloud se borran en Ajustes → tu nombre → iCloud → Gestionar almacenamiento."),
     ("¿Cómo me apunto a una beta?", "Algunas apps están aún en fase beta en TestFlight. Escríbenos un correo y te enviaremos una invitación."),
     ("Tengo una idea para una función", "¡Cuéntanosla! Escríbenos un correo: leemos todas las sugerencias.")],
    [("Czy potrzebuję konta?", "Nie. Aplikacje EasyLife działają bez rejestracji i logowania. Jedynym wyjątkiem jest Cestovníček, który używa konta do synchronizacji z wersją webową."),
     ("Gdzie są moje dane?", "Na twoim iPhonie, a jeśli aplikacja synchronizuje, w twoim prywatnym iCloud. My nie mamy do nich dostępu. Szczegóły znajdziesz w polityce prywatności każdej aplikacji."),
     ("Jak przenieść dane na nowego iPhone’a?", "Aplikacje synchronizujące przez iCloud przeniosą dane same, gdy zalogujesz się tym samym Apple ID. Resztę przeniesie kopia zapasowa iPhone’a."),
     ("Jak usunąć swoje dane?", "Usunięcie aplikacji kasuje dane w urządzeniu. Dane w iCloud usuniesz w Ustawieniach → twoje imię → iCloud → Zarządzaj pamięcią."),
     ("Jak dołączyć do wersji beta?", "Niektóre aplikacje są jeszcze w fazie beta w TestFlight. Napisz do nas e-mail, a wyślemy zaproszenie."),
     ("Mam pomysł na nową funkcję", "Śmiało! Napisz do nas e-mail – czytamy wszystkie propozycje.")]],
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
.bento{display:grid;grid-template-columns:repeat(4,1fr);grid-auto-rows:212px;grid-auto-flow:dense;gap:16px}
.tile{--lift:0px;position:relative;display:flex;flex-direction:column;justify-content:flex-end;gap:6px;padding:20px;border-radius:30px;overflow:hidden;isolation:isolate;
background:linear-gradient(155deg,color-mix(in oklab,var(--c) 26%,var(--surface)),color-mix(in oklab,var(--c) 7%,var(--surface)) 70%);border:1px solid color-mix(in oklab,var(--c) 22%,var(--line));
box-shadow:var(--shadow);transform:perspective(900px) rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg)) translateY(var(--lift));transition:transform .25s ease,box-shadow .25s}
.tile:hover{--lift:-6px}
@media (prefers-color-scheme:dark){.tile{background:linear-gradient(155deg,color-mix(in oklab,var(--c) 40%,var(--surface)),color-mix(in oklab,var(--c) 12%,var(--surface)) 75%)}.tile .ghost-icon{opacity:.22}}
.tile .app-icon{position:absolute;top:18px;left:18px;width:64px;height:64px;transition:transform .45s cubic-bezier(.3,1.7,.5,1)}
.tile:hover .app-icon{transform:rotate(-10deg) scale(1.12)}
.tile .ghost-icon{position:absolute;right:-18%;bottom:-22%;width:70%;max-width:340px;aspect-ratio:1;border-radius:23%;opacity:.16;transform:rotate(18deg);z-index:-1;filter:saturate(1.3);transition:transform .8s ease}
.tile:hover .ghost-icon{transform:rotate(8deg) scale(1.06)}
.tile h3{font:800 1.3rem/1.1 var(--display);letter-spacing:-.02em;margin:0}.tile h3 a{text-decoration:none}
.tile h3 a::after{content:"";position:absolute;inset:0;z-index:1}
.tile p{margin:0;color:var(--muted);font-size:.93rem;line-height:1.38;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.tile .status{position:absolute;top:18px;right:18px}
.tile .priv{position:relative;z-index:2;align-self:flex-start;font-size:.8rem;font-weight:700;color:var(--muted);text-decoration:none;margin-top:2px}.tile .priv:hover{color:var(--ink);text-decoration:underline}
.t-big{grid-column:span 2;grid-row:span 2;padding:28px}
.t-big .app-icon{width:132px;height:132px;top:28px;left:28px}
.t-big h3{font-size:clamp(1.8rem,3vw,2.6rem)}.t-big p{font-size:1.08rem;-webkit-line-clamp:3}
.t-wide{grid-column:span 2}.t-wide .ghost-icon{width:44%;right:-6%;bottom:-40%}
.chip{display:inline-flex;align-items:center;gap:6px;border-radius:999px;padding:5px 11px;font-weight:800;font-size:.76rem;background:var(--surface);color:var(--ink);box-shadow:0 2px 8px -4px rgb(0 0 0/.3)}
.chip.tf::before{content:"";width:7px;height:7px;border-radius:50%;background:var(--green)}
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
.ico{flex:none}.chip .short{display:none}
html{overflow-x:hidden}
.fly-layer.small .fly{--k:.8}
.hero::after,.app-top::after,.page-top::after{content:"";position:absolute;left:0;right:0;bottom:0;height:140px;background:linear-gradient(rgb(0 0 0/0),var(--bg));z-index:0;pointer-events:none}
@media (max-width:980px){.bento{grid-template-columns:repeat(2,1fr)}.stickers{grid-template-columns:repeat(2,1fr)}}
@media (max-width:820px){.app-head{grid-template-columns:1fr}.hero-icon{grid-row:1;justify-self:start;width:150px}.features li,.features li:nth-child(-n+2){grid-column:span 6}
.fly{--k:.56}.fly.side,.fly-layer.small{display:none}.hero{padding:210px 0 170px;min-height:0}.wall{height:340px}}
@media (max-width:560px){.bento{grid-auto-rows:196px;gap:12px}.t-big{grid-row:span 1;padding:18px}.t-big .app-icon{width:72px;height:72px;top:16px;left:16px}.t-big h3{font-size:1.6rem}.t-big p{-webkit-line-clamp:2;font-size:.95rem}
.tile:not(.t-big) .chip .long{display:none}.tile:not(.t-big) .chip .short{display:inline}.tile{padding:16px;border-radius:24px}
.tile .app-icon{width:52px;height:52px;top:14px;left:14px}.tile .status{top:14px;right:12px}.tile h3{font-size:1.1rem}.tile p{font-size:.86rem}
.stickers{grid-template-columns:1fr}.nav>a{display:none}.marquee{margin-bottom:56px}.marquee.two{margin-top:-80px}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}.js .rv{opacity:1;transform:none}html{scroll-behavior:auto}}
"""

def head_script(lang, slug):
    """Výběr jazyka: uložená volba, jinak jazyk prohlížeče. Přesměrovává jen z výchozí (české) verze."""
    js = "document.documentElement.className+=' js';"
    if lang == "cs":
        js += ("(function(){var L=" + json.dumps(LANGS) + ",s,p=" + json.dumps(slug or "") + ";"
               "try{s=localStorage.getItem('lang')}catch(e){}"
               "if(!s){var n=navigator.languages||[navigator.language||'cs'];s='en';"
               "for(var i=0;i<n.length;i++){var c=String(n[i]).slice(0,2).toLowerCase();if(L.indexOf(c)>=0){s=c;break}}}"
               "if(s!=='cs'&&L.indexOf(s)>0)location.replace((p?'../':'')+s+'/'+(p?p+'/':'')+location.hash)})();")
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
document.querySelectorAll('.tile').forEach(function(t){t.addEventListener('pointermove',function(e){if(e.pointerType!=='mouse')return;var r=t.getBoundingClientRect();
t.style.setProperty('--rx',((e.clientY-r.top)/r.height-.5)*-7+'deg');t.style.setProperty('--ry',((e.clientX-r.left)/r.width-.5)*7+'deg')});
t.addEventListener('pointerleave',function(){t.style.removeProperty('--rx');t.style.removeProperty('--ry')})})
})();
</script>"""

def page(lang, slug, title, desc, body, operator, relative=True):
    alts = "".join(f'<link rel="alternate" hreflang="{l}" href="{BASE}{url(l, slug)}">' for l in LANGS)
    alts += f'<link rel="alternate" hreflang="x-default" href="{BASE}{url("cs", slug)}">'
    langs = "".join(f'<a href="{url(l, slug)}" hreflang="{l}" lang="{l}" title="{LANG_NAMES[l]}"'
                    f'{" aria-current=\"true\"" if l == lang else ""}>{l.upper()}</a>' for l in LANGS)
    pol = f'/soukromi.html{"" if lang in ("cs", "sk") else "#en"}'
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
<meta name="theme-color" content="#fbfaf6" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#0d0e11" media="(prefers-color-scheme: dark)">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600..800&amp;display=swap">
<link rel="stylesheet" href="/site.css"></head>
<body><a class="skip" href="#main">{t("skip", lang)}</a>
<div class="wrap"><header class="top"><a class="brand" href="{url(lang)}">{LOGO}EasyLife</a>
<nav class="nav"><a href="{url(lang)}#apps">{t("apps", lang)}</a><a href="{url(lang, SUPPORT)}">{t("support", lang)}</a>
<span class="langs" aria-label="{t("lang", lang)}">{langs}</span></nav></header></div>
<main id="main">{body}</main>
<footer><div class="wrap row"><div><a class="brand" href="{url(lang)}">{LOGO}EasyLife</a><p>{t("made", lang)}</p>
<p>{t("operator", lang)}: {esc(operator[0 if lang in ("cs", "sk") else 1])}</p></div>
<p><a href="{url(lang, SUPPORT)}">{t("support", lang)}</a> · <a href="{pol}">{t("policy", lang)}</a></p></div></footer>
{FOOT_SCRIPT}</body></html>
"""
    # Relativní odkazy, aby web fungoval i na bobr700r-droid.github.io/easylife-privacy/ (než začne platit doména).
    if relative:
        r = "../" * ((lang != "cs") + (slug is not None)) or "./"
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

    def has_icon(self, a):
        return (self.out / "icons" / f"{a['id']}.webp").exists()

    def icon_first(self):
        return [a for a in self.apps if self.has_icon(a)] + [a for a in self.apps if not self.has_icon(a)]

    def status(self, a, lang):
        if a.get("store"):
            return f'<a class="btn" style="--c:{self.color(a)}" href="{esc(a["store"])}">{t("get", lang)}</a>'
        tf = a["site"].get("status") == "testflight"
        return (f'<span class="chip {"tf" if tf else "soon"}"><span class="long">{t("testflight" if tf else "soon", lang)}</span>'
                f'<span class="short">{"Beta" if tf else t("soon", lang)}</span></span>')

    def tile(self, a, lang, size, k):
        big = '<img class="ghost-icon" src="/icons/{}.webp" alt="" loading="lazy">'.format(a["id"]) if self.has_icon(a) and size != "t-n" else ""
        return (f'<article class="tile {size} rv" style="--c:{self.color(a)};--rd:{k * 60}ms">{big}{self.app_icon(a, 132 if size == "t-big" else 64)}'
                f'<div class="status">{self.status(a, lang)}</div>'
                f'<h3><a href="{url(lang, a["id"])}">{esc(a["name"])}</a></h3><p>{esc(a["tagline"][lang])}</p>{self.privacy_link(a, lang, "priv")}</article>')

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

    def family_apps(self, fid):
        return [a for a in self.apps if a["family"] == fid]

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
        pc = [("user-x", "var(--blue)", "-3deg"), ("eye-off", "var(--pink)", "2deg"), ("lock", "var(--green)", "-1.5deg")]
        pills = "".join(f'<li style="--pc:{c};--pr:{r}">{icon(n)}{t("pills", lang)[k]}</li>' for k, (n, c, r) in enumerate(pc))
        h = t("hero", lang).replace(t("hero_hl", lang), f'<span class="hl">{t("hero_hl", lang)}</span>')
        fly = self.fly_icons(self.icon_first()).replace("{u}", url(lang))
        fams = ""
        for fid, f in self.families.items():
            apps = self.family_apps(fid)
            if not apps:
                continue
            fams += (f'<div class="family" id="{fid}"><h3 class="fam-title rv" style="--fc:{FAMILY_COLORS.get(fid, "#555")}">{icon(fid)}{esc(f["name"][lang])}<small>{len(apps)}</small></h3>'
                     f'{self.bento(apps, lang)}</div>')
        sc = [("user-x", "var(--blue)", "-2deg"), ("eye-off", "var(--pink)", "1.5deg"), ("lock", "var(--green)", "-1deg"), ("link", "var(--orange)", "2deg")]
        prin = "".join(f'<div class="sticker rv" style="--sc:{c};--sr:{r};--rd:{k * 90}ms">{icon(n)}<h3>{esc(hd)}</h3><p>{esc(p)}</p></div>'
                       for k, ((n, c, r), (hd, p)) in enumerate(zip(sc, T["principles"][i])))
        order = self.icon_first()
        wall = "".join(self.app_icon(a, 120) for a in (order * 7)[:96])
        body = (f'<section class="hero" data-par><div class="blobs"><i></i><i></i><i></i></div><div class="fly-layer" aria-hidden="true">{fly}</div>'
                f'<div class="wrap hero-in"><p class="kicker"><span class="dot"></span>{t("count", lang).format(n=len(self.apps))}</p>'
                f'<h1>{h}</h1><p class="lead">{t("lead", lang)}</p><ul class="pills">{pills}</ul>'
                f'<a class="btn big" href="#apps">{t("cta_apps", lang)} <span>↓</span></a></div></section>'
                + '<div class="mq-wrap">' + self.marquee(order, lang) + self.marquee(order[::-1], lang, "two") + "</div>" +
                f'<section id="apps"><div class="wrap"><div class="sec-head rv"><h2>{t("apps", lang)}</h2><p>{t("apps_lead", lang)}</p></div>{fams}</div></section>'
                f'<section><div class="wrap"><div class="sec-head rv"><h2>{t("how", lang)}</h2></div><div class="stickers">{prin}</div></div></section>'
                f'<section><div class="wrap"><div class="wall rv"><div class="wall-grid" aria-hidden="true">{wall}</div>'
                f'<div class="wall-text"><h2>{t("wall", lang)}</h2></div></div></div></section>')
        return page(lang, None, t("title", lang), t("lead", lang), body, self.operator)

    def support(self, lang):
        i = LANGS.index(lang)
        mail = f"mailto:{CONTACT}?subject=EasyLife"
        faq = "".join(f'<details class="faq rv"><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in T["faq"][i])
        body = (f'<section class="page-top"><div class="blobs"><i></i><i></i><i></i></div><div class="wrap"><div class="detail">'
                f'<h1>{t("support_title", lang)}</h1><p class="lead">{t("support_lead", lang)}</p>'
                f'<p class="actions"><a class="btn big" href="{mail}">{t("support_mail", lang)} <span>→</span></a><a class="ghost" href="{mail}">{CONTACT}</a></p>'
                f'<p class="note">{icon("check")}<span>{t("support_hint", lang)}</span></p></div></div></section>'
                f'<div class="wrap"><div class="detail"><h2 class="sub">{t("faq_title", lang)}</h2>{faq}'
                f'<p class="note">{icon("shield")}<span><a href="/soukromi.html{"" if lang in ("cs", "sk") else "#en"}">{t("policy", lang)}</a></span></p></div></div>')
        return page(lang, SUPPORT, f'{t("support_title", lang)} | EasyLife', t("support_lead", lang), body, self.operator)

    def detail(self, a, lang):
        s, c, fam = a["site"], self.color(a), self.families[a["family"]]
        fc = FAMILY_COLORS.get(a["family"], c)
        desc = "".join(f"<p>{esc(p)}</p>" for p in (s.get("description", {}).get(lang) or []))
        feats = s.get("features", {}).get(lang) or []
        web = f'<a class="ghost" href="{esc(s["web"])}">{esc(s["web"].split("//")[-1].rstrip("/"))} ↗</a>' if s.get("web") else ""
        others = [o for o in self.family_apps(a["family"]) if o["id"] != a["id"]]
        flyers = [o for o in others + [o for o in self.icon_first() if o not in others and o is not a] if self.has_icon(o)]
        fly = self.fly_icons(flyers[:6], FLY_DETAIL).replace("{u}", "/" if lang == "cs" else f"/{lang}/")
        p = self.privacy_link(a, lang, "")
        note = (f'{icon("shield")}<span>{p.replace(">" + t("privacy", lang) + "<", ">" + t("policy", lang) + t("policy_lang", lang) + "<")}</span>'
                if p else f'{icon("shield")}<span>{t("policy_soon", lang)}</span>')
        body = (f'<section class="app-top" style="--c:{c}" data-par><div class="blobs"><i></i><i></i><i></i></div>'
                f'<div class="fly-layer small" aria-hidden="true">{fly}</div><div class="wrap">'
                f'<a class="back" href="{url(lang)}#{a["family"]}">{icon("arrow-left")}{t("back", lang)}</a>'
                f'<div class="app-head"><div><a class="fam-chip" style="--fc:{fc}" href="{url(lang)}#{a["family"]}">{icon(a["family"])}{esc(fam["name"][lang])}</a>'
                f'<h1>{esc(a["name"])}</h1><p class="tag">{esc(a["tagline"][lang])}</p><div class="actions">{self.status(a, lang)}{web}</div></div>'
                f'<div class="hero-icon">{self.app_icon(a, 300).replace(" loading=\"lazy\"", "")}</div></div></div></section>')
        body += f'<div class="wrap" style="--c:{c}"><article class="detail"><div class="desc rv">{desc}</div>'
        if feats:
            body += f'<h2 class="sub rv">{t("features", lang)}</h2><ul class="features">' + "".join(
                f'<li class="rv" style="--rd:{k * 70}ms">{esc(x)}</li>' for k, x in enumerate(feats)) + "</ul>"
        shots = a.get("shots") or []
        if shots:
            body += f'<h2 class="sub rv">{t("shots", lang)}</h2><div class="shots">' + "".join(
                f'<img src="/shots/{a["id"]}/{esc(x)}" alt="" loading="lazy" width="250" height="544">' for x in shots) + "</div>"
        links = [(self.by_id[l["app"]], l["text"][lang]) for l in s.get("links", []) if l["app"] in self.by_id]
        if links:
            body += f'<h2 class="sub rv">{t("works_with", lang)}</h2><div class="links">' + "".join(
                f'<div class="link-row rv">{self.app_icon(o, 54)}<div><a href="{url(lang, o["id"])}"><b>{esc(o["name"])}</b></a><span>{esc(txt)}</span></div></div>'
                for o, txt in links) + "</div>"
        body += f'<p class="note">{note}</p>'
        if not a.get("store"):
            body += f'<p class="note">{icon("check")}<span>{t("tf_note" if s.get("status") == "testflight" else "dev_note", lang)}</span></p>'
        body += "</article></div>"
        if others:
            body += (f'<section><div class="wrap"><div class="sec-head rv"><h2>{t("family_more", lang).format(f=esc(fam["name"][lang]))}</h2></div>'
                     f'{self.bento(others, lang, featured=len(others) > 2)}</div></section>')
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
            self.write(f"{pre}{SUPPORT}/index.html", self.support(lang))
            urls.append(url(lang, SUPPORT))
            urls.append(url(lang))
            for a in self.apps:
                self.write(f"{pre}{a['id']}/index.html", self.detail(a, lang))
                urls.append(url(lang, a["id"]))
        # Smazat stránky appek, které z katalogu zmizely nebo jsou skryté.
        keep = {a["id"] for a in self.apps} | set(LANGS) | {"icons", "shots", SUPPORT}
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
