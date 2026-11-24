"""Sekce Pro firmy (/firmy/…): nabídka služeb EasyForLife. Zatím jen čeština; angličtina = doplnit "en" do textů a LANGS_FIRMY."""
import html, json

LANGS_FIRMY = ["cs"]
FORM_ACTION = "/api/poptavka"  # TODO: endpoint na serveru → Mailer (e-mail Lukášovi + potvrzení zákazníkovi), zatím neexistuje
SLUGS = {  # id → {jazyk: slug}
    "index": {"cs": "firmy", "en": "business"},
    "weby": {"cs": "firmy/weby", "en": "business/websites"},
    "aplikace": {"cs": "firmy/aplikace", "en": "business/apps"},
    "fotografove": {"cs": "firmy/fotografove", "en": "business/photographers"},
    "naklady": {"cs": "firmy/naklady", "en": "business/costs"},
    "crm": {"cs": "firmy/crm", "en": "business/crm"},
}
UI = {
    "nav": {"cs": "Pro firmy", "en": "For business"},
    "ask": {"cs": "Nezávazná poptávka", "en": "Get a quote"},
    "all": {"cs": "Všechny služby", "en": "All services"},
    "more": {"cs": "Více", "en": "More"},
    "month": {"cs": "/měs.", "en": "/mo"},
}

def esc(s):
    return html.escape(s, quote=True)

def tx(d, lang):
    return d.get(lang) or d["cs"] if isinstance(d, dict) else d

def kc(n):
    return f"{n:,}".replace(",", " ") + " Kč"

# Služby – pořadí = pořadí v podnabídce a na rozcestníku
SERVICES = [
    dict(id="weby", c="#2563eb", ico="globe", price="od 7 900 Kč",
         name={"cs": "Weby a e-shopy"},
         short={"cs": "Web nebo e-shop na míru za pevnou cenu. Návrh do 48 hodin, hotovo do 7 dní."}),
    dict(id="aplikace", c="#8b46d9", ico="phone", price="po konzultaci",
         name={"cs": "Aplikace na míru"},
         short={"cs": "Aplikace pro iPhone, iPad a Mac – pro vaše zákazníky i pro provoz firmy."}),
    dict(id="fotografove", c="#e8731c", ico="camera", price="1 490 Kč/měs.",
         name={"cs": "Pro fotografy"},
         short={"cs": "Portfolio web napojený na FotoDesk: rezervace, smlouvy, faktury a galerie."}),
    dict(id="naklady", c="#10a36a", ico="chart", price="od 490 Kč/měs.",
         name={"cs": "Přehled firemních nákladů"},
         short={"cs": "Přijaté faktury, výdaje, závazky a bankovní pohyby na jednom místě."}),
    dict(id="crm", c="#e8457a", ico="people", price="od 490 Kč/měs.",
         name={"cs": "CRMDesk"},
         short={"cs": "CRM pro firmy s oborovými šablonami – zákazníci, zakázky a obchod přehledně."}),
]
SVC = {s["id"]: s for s in SERVICES}

ICO = {  # 24×24, stroke
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18"/>',
    "phone": '<rect x="6" y="2.5" width="12" height="19" rx="3"/><path d="M10.5 18.5h3"/>',
    "camera": '<path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/>',
    "chart": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    "people": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c.8-4 3.4-6 6.5-6s5.7 2 6.5 6"/><path d="M16 4.5a3.5 3.5 0 0 1 0 7M18 14c2 .7 3.2 2.6 3.6 6"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
}

def ico(name, cls="fi"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICO[name]}</svg>'

class Pages:
    def __init__(self, url, mail):
        self.url, self.mail = url, mail  # web.url(lang, slug), kontakt pro náhradní e-mail

    def u(self, lang, pid, anchor=""):
        return self.url(lang, SLUGS[pid][lang]) + anchor

    def subnav(self, lang, cur):
        items = [("index", tx(UI["all"], lang))] + [(s["id"], tx(s["name"], lang)) for s in SERVICES]
        return ('<nav class="fm-sub" aria-label="' + tx(UI["nav"], lang) + '">' + "".join(
            f'<a href="{self.u(lang, i)}"{" aria-current=\"page\"" if i == cur else ""}>{esc(n)}</a>' for i, n in items) + "</nav>")

    def hero(self, lang, cur, c, kicker, h1, lead, cta):
        return (f'<section class="fm-hero" style="--c:{c}" data-par><div class="blobs"><i></i><i></i><i></i></div><div class="wrap">'
                f'{self.subnav(lang, cur)}<p class="kicker"><span class="dot"></span>{esc(kicker)}</p>'
                f'<h1>{h1}</h1><p class="lead">{esc(lead)}</p><div class="fm-cta">{cta}</div></div></section>')

    def ask_btn(self, lang, sid="", label=None):
        q = f"?sluzba={sid}" if sid else ""
        return f'<a class="btn big" href="{self.u(lang, "index")}{q}#poptavka">{esc(label or tx(UI["ask"], lang))} {ico("arrow")}</a>'

    def checks(self, items):
        return '<ul class="fm-check">' + "".join(f'<li class="rv" style="--rd:{k * 50}ms">{ico("check")}<span>{esc(x)}</span></li>' for k, x in enumerate(items)) + "</ul>"

    def price_cards(self, cards):
        out = '<div class="fm-prices">'
        for k, (name, price, per, desc, items, top, btn) in enumerate(cards):
            out += (f'<article class="fm-price rv{" hot" if top else ""}" style="--rd:{k * 80}ms">' + ('<i class="fm-tag">Nejčastější volba</i>' if top else "")
                    + f'<h3>{esc(name)}</h3><p class="muted">{esc(desc)}</p><div class="fm-num">{price}<small>{esc(per)}</small></div>'
                    + self.checks(items) + btn + "</article>")
        return out + "</div>"

    def steps(self, steps):
        return '<ol class="fm-steps">' + "".join(
            f'<li class="rv" style="--rd:{k * 70}ms"><b>{k + 1}</b><h3>{esc(h)}</h3><p>{esc(p)}</p></li>' for k, (h, p) in enumerate(steps)) + "</ol>"

    def band(self, lang, sid, h, p):
        return (f'<section><div class="wrap"><div class="fm-band rv" style="--c:{SVC[sid]["c"] if sid else "#2563eb"}"><div><h2>{esc(h)}</h2><p>{esc(p)}</p></div>'
                f'{self.ask_btn(lang, sid)}</div></div></section>')

    def sec(self, h, p, inner, sid=""):
        return (f'<section{f" id={chr(34)}{sid}{chr(34)} class={chr(34)}fm-anchor{chr(34)}" if sid else ""}><div class="wrap"><div class="sec-head rv"><h2>{esc(h)}</h2>' + (f"<p>{esc(p)}</p>" if p else "")
                + f"</div>{inner}</div></section>")

    # ---------- stránky ----------
    def index(self, lang):
        tiles = '<div class="fm-tiles">' + "".join(
            f'<a class="fm-tile rv" style="--c:{s["c"]};--rd:{k * 70}ms" href="{self.u(lang, s["id"])}">{ico(s["ico"], "fi big")}'
            f'<h3>{esc(tx(s["name"], lang))}</h3><p>{esc(tx(s["short"], lang))}</p><span class="fm-tp"><b>{esc(s["price"])}</b>{ico("arrow")}</span></a>'
            for k, s in enumerate(SERVICES)) + "</div>"
        why = self.checks(["Jeden dodavatel pro web, aplikaci, fakturaci i CRM – vše na sebe navazuje",
                           "Pevná cena předem, cokoli navíc vždy nejdřív naceníme",
                           "Provoz na vlastních serverech v České republice",
                           "Stejný vývojář jako celá rodina aplikací EasyForLife"])
        body = self.hero(lang, "index", "#2563eb", "Služby pro firmy a živnostníky",
                         'Weby, aplikace a&nbsp;<span class="hl">přehled o&nbsp;penězích</span> pro vaši firmu',
                         "Navrhneme, postavíme a spravujeme. Od webové vizitky přes e-shop a aplikace na míru až po přehled nákladů a CRM.",
                         self.ask_btn(lang) + f'<a class="ghost" href="#sluzby">Prohlédnout služby</a>')
        body += f'<section id="sluzby"><div class="wrap">{tiles}</div></section>'
        body += self.sec("Proč s námi", None, why)
        body += self.sec("Jak to probíhá", None, self.steps([
            ("Poptávka", "Vyplníte krátký formulář níže nebo napíšete e-mail."),
            ("Návrh do 48 h", "Pošleme návrh řešení a přesnou cenu."),
            ("Záloha 50 %", "Po schválení návrhu se pouštíme do práce."),
            ("Realizace", "Průběžně uvidíte, jak práce postupuje; 2 kola úprav v ceně."),
            ("Spuštění a správa", "Předáme přístupy a o provoz se můžeme starat dál.")]))
        body += self.form(lang)
        return ("Pro firmy – weby, aplikace, náklady a CRM | EasyForLife",
                "Weby, e-shopy, aplikace na míru, přehled firemních nákladů a CRM pro firmy a živnostníky. Pevné ceny, nezávazná poptávka.", body)

    def form(self, lang):
        opts = "".join(f'<option value="{s["id"]}">{esc(tx(s["name"], lang))}</option>' for s in SERVICES)
        return f"""<section id="poptavka" class="fm-form-sec"><div class="wrap"><div class="fm-form-grid">
<div class="rv"><h2 class="fm-h2">Nezávazná poptávka</h2><p class="muted">Napište, co potřebujete. Ozveme se do dvou pracovních dnů s návrhem a cenou. Poptávka vás k ničemu nezavazuje.</p>
<p class="muted small">Údaje z formuláře použijeme jen k odpovědi na vaši poptávku.</p></div>
<form class="fm-form rv" data-action="{FORM_ACTION}" data-mail="{self.mail}" data-ok="Děkujeme, poptávka je odeslaná. Ozveme se do dvou pracovních dnů." data-err="Odeslání se nepovedlo. Napište nám prosím e-mailem na ">
<label>Jméno<input name="jmeno" required autocomplete="name"></label>
<label>Firma<input name="firma" autocomplete="organization"></label>
<label>E-mail<input name="email" type="email" required autocomplete="email"></label>
<label>Telefon<input name="telefon" type="tel" autocomplete="tel" placeholder="+420"></label>
<label class="wide">O co máte zájem<select name="sluzba">{opts}<option value="jine">Jiné / zatím nevím</option></select></label>
<label class="wide">Co potřebujete<textarea name="zprava" rows="4" placeholder="Obor, současný web nebo systém, představa o termínu…"></textarea></label>
<input name="website" tabindex="-1" autocomplete="off" class="hp" aria-hidden="true">
<div class="wide fm-send"><button type="submit">Odeslat poptávku</button><p class="fm-msg" role="status" hidden></p></div>
</form></div></div></section>"""

    def weby(self, lang):
        b = lambda sid: self.ask_btn(lang, "weby", "Poptat")
        cards = [("Vizitka", "7 900", " Kč", "Jedna stránka, která o vás řekne to podstatné.",
                  ["1 stránka na míru", "Mobil, tablet i počítač", "Kontakty, mapa, odkazy na sítě", "Rychlé načítání"], False, b("")),
                 ("Firma", "14 900", " Kč", "Plnohodnotný web pro firmu, živnost i službu.",
                  ["Až 5 stránek", "SEO základ (titulky, popisy, mapa webu)", "Poptávkový formulář", "Mapa a otevírací doba"], True, b("")),
                 ("E-shop", "<small>od </small>29 900", " Kč", "Prodej online s košíkem a objednávkami.",
                  ["Katalog, košík, objednávky", "Platby kartou i převodem", "Napojení dopravců", "Napojení na fakturaci"], False, b(""))]
        body = self.hero(lang, "weby", SVC["weby"]["c"], "Weby a e-shopy",
                         'Web, který pro vás <span class="hl">pracuje</span>. Hotový do 7 dní.',
                         "Pevná cena předem, návrh do 48 hodin, bez skrytých poplatků. Navrhneme, postavíme a postaráme se o provoz.",
                         self.ask_btn(lang, "weby") + '<a class="ghost" href="#cenik">Ceník</a>')
        body += f'<section id="cenik"><div class="wrap">{self.price_cards(cards)}' + (
            '<div class="fm-line rv"><div><h3>Správa a hosting</h3><p class="muted">Hosting, zálohy, SSL certifikát, drobné úpravy textů a dohled nad během webu.</p></div>'
            '<div class="fm-num">490<small> Kč/měs.</small></div></div>'
            '<p class="note">Ceny jsou pevné za uvedený rozsah. Cokoli nad rámec balíčku vždy naceníme předem.</p></div></section>')
        body += self.sec("Jak to probíhá", None, self.steps([
            ("Poptávka", "Vyplníte krátký formulář."), ("Návrh do 48 h", "Pošleme návrh vzhledu a přesnou cenu."),
            ("Záloha 50 %", "Po schválení návrhu začínáme."), ("Web do 7 dní", "Dvě kola úprav v ceně."),
            ("Spuštění", "Web běží na vaší doméně, předáme přístupy.")]))
        work = [("E-shop", "motobaterie.cz", "https://motobaterie.cz", "Platby, doprava, fakturace"),
                ("Webová aplikace", "cestovnik.eu", "https://cestovnik.eu", "Plánovač cest"),
                ("Web + aplikace", "mujsvatebnicek.cz", "https://mujsvatebnicek.cz", "Plánování svatby"),
                ("Systém pro fotografy", "fotodesk.cz", "https://fotodesk.cz", "Galerie, rezervace, smlouvy, faktury")]
        body += self.sec("Projekty, které jsme postavili", "Vlastní projekty v provozu – podívejte se, jak fungují.",
                         '<div class="fm-work">' + "".join(f'<a class="rv" href="{h}" target="_blank" rel="noopener"><small>{esc(k)}</small><h3>{esc(n)} ↗</h3><span>{esc(d)}</span></a>'
                                                           for k, n, h, d in work) + "</div>")
        body += self.band(lang, "weby", "Máte představu o novém webu?", "Napište pár vět – do 48 hodin dostanete návrh a cenu.")
        return ("Weby a e-shopy pro firmy – pevná cena, hotovo do 7 dní | EasyForLife",
                "Web Vizitka 7 900 Kč, Firma 14 900 Kč, e-shop od 29 900 Kč, správa 490 Kč/měs. Návrh do 48 hodin.", body)

    def aplikace(self, lang):
        body = self.hero(lang, "aplikace", SVC["aplikace"]["c"], "iPhone · iPad · Mac · web",
                         'Aplikace <span class="hl">na míru</span> pro vaše zákazníky i provoz firmy',
                         "Nativní aplikace pro Apple zařízení a webové aplikace napojené na vaše systémy. Cenu stanovíme po krátké konzultaci podle rozsahu.",
                         self.ask_btn(lang, "aplikace", "Probrat aplikaci"))
        body += self.sec("Co umíme dodat", None, self.checks([
            "Aplikace pro zákazníky i interní provoz firmy", "Synchronizace přes iCloud nebo vlastní server",
            "Widgety, upozornění, Apple Watch", "Napojení na web, e-shop, fakturaci a CRM",
            "Vydání v App Store nebo interní distribuce", "Údržba a nové verze po spuštění"]))
        body += self.sec("Jak vzniká aplikace", None, self.steps([
            ("Konzultace", "Probereme, co má aplikace řešit a pro koho je."), ("Návrh a cena", "Pošleme rozsah, náhled obrazovek a cenu."),
            ("Vývoj po částech", "Průběžně testujete hotové části přes TestFlight."), ("Vydání", "Aplikace vyjde v App Store nebo ve firmě."),
            ("Péče", "Aktualizace na nové verze systémů a další rozvoj.")]))
        body += (f'<section><div class="wrap"><div class="fm-line rv"><div><h3>Rodina aplikací EasyForLife</h3><p class="muted">Desítky vlastních aplikací pro domácnost, rodinu a práci – stejným způsobem postavíme i tu vaši.</p></div>'
                 f'<a class="btn" href="{self.url(lang)}#apps">Prohlédnout aplikace</a></div></div></section>')
        body += self.band(lang, "aplikace", "Máte nápad na aplikaci?", "Popište ho pár větami – ozveme se s termínem konzultace.")
        return ("Aplikace na míru pro iPhone, iPad a Mac | EasyForLife",
                "Aplikace na míru pro firmy: iPhone, iPad, Mac i web, napojení na vaše systémy. Cena po konzultaci.", body)

    def fotografove(self, lang):
        btn = self.ask_btn(lang, "fotografove", "Chci web pro fotografa")
        cards = [("Web + FotoDesk", "1 490", " Kč/měs.", "Vše v jednom měsíčním paušálu.",
                  ["Portfolio web na vaší doméně", "Galerie pro klienty", "Online rezervace termínů", "Smlouvy a faktury z FotoDesku", "Hosting a správa v ceně"], True, btn),
                 ("Jednorázově", "7 900", " Kč", "Web zaplatíte jednou, FotoDesk Standard zvlášť za 490 Kč/měs.",
                  ["Portfolio web na vaší doméně", "Napojení na FotoDesk", "FotoDesk Standard 490 Kč/měs.", "Správa webu volitelně 490 Kč/měs."], False, self.ask_btn(lang, "fotografove", "Poptat"))]
        body = self.hero(lang, "fotografove", SVC["fotografove"]["c"], "Pro fotografy",
                         'Web a <span class="hl">FotoDesk</span> – klient od rezervace po galerii',
                         "Portfolio web napojený na FotoDesk: klient si vybere termín, podepíše smlouvu, zaplatí a dostane galerii. Vše na jednom místě a pod vaší značkou.",
                         btn + '<a class="ghost" href="#cenik">Ceník</a>')
        flow = ["Rezervace", "Smlouva", "Záloha", "Focení", "Galerie", "Faktura"]
        body += ('<section><div class="wrap"><div class="fm-flow rv">' + "".join(
            f'<span style="--rd:{k * 120}ms"><b>{k + 1}</b>{esc(x)}</span>' for k, x in enumerate(flow)) + "</div></div></section>")
        body += f'<section id="cenik"><div class="wrap">{self.price_cards(cards)}</div></section>'
        body += (f'<section><div class="wrap"><div class="fm-line rv"><div><h3>FotoDesk</h3><p class="muted">Systém pro fotografy: galerie, rezervace, smlouvy a faktury.</p></div>'
                 f'<a class="btn" href="https://fotodesk.cz" target="_blank" rel="noopener">fotodesk.cz ↗</a></div></div></section>')
        body += self.band(lang, "fotografove", "Chcete web, který si na sebe vydělá?", "Pošlete odkaz na současné portfolio – navrhneme, jak ho napojit na FotoDesk.")
        return ("Web pro fotografy s FotoDeskem – 1 490 Kč/měs. | EasyForLife",
                "Portfolio web napojený na FotoDesk: rezervace, smlouvy, faktury a galerie. 1 490 Kč/měs. nebo web 7 900 Kč + FotoDesk Standard.", body)

    def naklady(self, lang):
        btn = self.ask_btn(lang, "naklady", "Chci přehled nákladů")
        # ukázka přehledu bez čísel – jen tvar
        bars = [("Materiál", 92), ("Služby", 70), ("Nájem a energie", 54), ("Doprava", 38), ("Software", 24)]
        demo = ('<div class="fm-demo" aria-hidden="true"><div class="fm-demo-h"><b>Kam tečou peníze</b><span>Ukázka</span></div>'
                + "".join(f'<div class="fm-bar"><span>{esc(n)}</span><i style="--w:{w}%;--rd:{k * 90}ms"></i></div>' for k, (n, w) in enumerate(bars))
                + '<div class="fm-demo-h"><b>Rozpočet projektu</b><span>čerpání vs. plán</span></div><div class="fm-gauge"><i style="--w:68%"></i></div></div>')
        hero = (f'<section class="fm-hero" style="--c:{SVC["naklady"]["c"]}" data-par><div class="blobs"><i></i><i></i><i></i></div><div class="wrap">{self.subnav(lang, "naklady")}'
                f'<div class="fm-split"><div><p class="kicker"><span class="dot"></span>Přehled firemních nákladů</p>'
                f'<h1>Víte, <span class="hl">kam tečou</span> peníze vaší firmy?</h1>'
                f'<p class="lead">Přijaté faktury, výdaje, závazky a pohyby na účtech na jednom místě. Postaveno na Fakturantu – fakturaci, kterou sami používáme.</p>'
                f'<div class="fm-cta">{btn}<a class="ghost" href="#cenik">Ceník</a></div></div>{demo}</div></div></section>')
        now = [("Přijaté faktury z e-mailu", "Faktury přeposlané e-mailem čekají ve schránce Ke zpracování; ISDOC se načte sám, fotku nebo PDF přečte AI."),
               ("Výdaje po kategoriích", "Průvodce nákladem: dodavatel z ARES, kategorie s daňovou uznatelností, DPH po sazbách, příloha dokladu."),
               ("Bankovní pohyby", "Napojení Fio a dalších bank přes PSD2, import výpisů; platby se samy spárují s doklady."),
               ("Závazky a cashflow", "Co a kdy budete platit: nezaplacené náklady, opakované platby a daně v předpovědi na 30, 60 a 90 dní."),
               ("Kontrola dodavatelů", "Před úhradou upozorní na nespolehlivého plátce DPH nebo nezveřejněný bankovní účet."),
               ("Pro účetní", "Export ISDOC a CSV, měsíční balíček dokladů účetní e-mailem."),
               ("Více uživatelů", "Práva po agendách (číst / upravovat), dvoufázové ověření, historie změn.")]
        soon = [("Rozpočty projektů a středisek", "Rozpočet na projekt, oddělení nebo zakázku a jeho čerpání oproti plánu s upozorněním."),
                ("Kam tečou peníze", "Přehled po kategoriích a top dodavatelé se srovnáním s minulým obdobím."),
                ("Schvalování výdajů", "Výdaj nad limit čeká na schválení – i z mobilu."),
                ("Zaměstnanecké výdaje", "Zaměstnanec vyfotí účtenku, vy schválíte a proplatíte.")]
        feat = lambda items, cls: f'<div class="fm-feats {cls}">' + "".join(
            f'<article class="rv" style="--rd:{k * 60}ms"><h3>{esc(h)}</h3><p>{esc(p)}</p></article>' for k, (h, p) in enumerate(items)) + "</div>"
        body = hero
        body += self.sec("Co umí už dnes", "Funkce, které Fakturant má a používá se v provozu.", feat(now, ""))
        body += self.sec("Připravujeme", "Na těchto funkcích pracujeme. Napište nám, které potřebujete nejvíc – podle zájmu určíme pořadí.", feat(soon, "soon"))
        cards = [("Start", "490", " Kč/měs.", "Pro menší firmu, až 3 uživatelé.",
                  ["Přijaté faktury a výdaje", "Doklady z e-mailu", "Napojení banky", "Závazky a cashflow", "Export pro účetní"], False, self.ask_btn(lang, "naklady", "Poptat Start")),
                 ("Firma", "990", " Kč/měs.", "Pro týmy, až 10 uživatelů.",
                  ["Vše ze Startu", "Rozpočty projektů a středisek (připravujeme)", "Schvalování výdajů (připravujeme)", "Zaměstnanecké výdaje (připravujeme)"], True, self.ask_btn(lang, "naklady", "Poptat Firmu"))]
        body += self.sec("Ceník", "Cena za firmu, ne za uživatele. Napojení na váš účetní systém nebo provoz na vlastním serveru naceníme na míru.",
                         self.price_cards(cards), "cenik")
        body += self.band(lang, "naklady", "Chcete mít náklady pod kontrolou?", "Ukážeme vám Přehled nákladů na krátké online schůzce.")
        return ("Přehled firemních nákladů – faktury, výdaje, rozpočty | EasyForLife",
                "Přijaté faktury, výdaje, závazky, rozpočty a bankovní pohyby firmy na jednom místě. Postaveno na Fakturantu, od 490 Kč/měs.", body)

    def crm(self, lang):
        btn = self.ask_btn(lang, "crm", "Mám zájem o CRMDesk")
        body = self.hero(lang, "crm", SVC["crm"]["c"], "CRMDesk",
                         'CRM, které <span class="hl">mluví vaším oborem</span>',
                         "Zákazníci, zakázky, obchodní případy a úkoly přehledně na jednom místě. Oborové šablony nastaví CRM pro váš typ firmy hned při založení.",
                         btn + '<a class="ghost" href="https://crmdesk.cz" target="_blank" rel="noopener">crmdesk.cz ↗</a>')
        body += self.sec("Co CRMDesk nabízí", None, self.checks([
            "37 oborových šablon – pole, fáze a seznamy připravené pro váš obor", "Zákazníci, kontakty a historie komunikace",
            "Zakázky a obchodní případy", "Úkoly a připomínky pro tým", "Napojení na fakturaci a přehled nákladů"]))
        cards = [("Start", "—", "", "Cenu upřesníme při spuštění.", ["Základ CRM pro začátek"], False, self.ask_btn(lang, "crm", "Mám zájem")),
                 ("Business", "490", " Kč/měs.", "Pro běžnou firmu.", ["Oborové šablony", "Zákazníci, zakázky, úkoly"], True, self.ask_btn(lang, "crm", "Mám zájem")),
                 ("Pro", "990", " Kč/měs.", "Pro větší týmy.", ["Vše z Business", "Rozšířené možnosti pro tým"], False, self.ask_btn(lang, "crm", "Mám zájem"))]
        body += self.sec("Ceník", "CRMDesk je před spuštěním. Zájemce zařadíme mezi první uživatele.", self.price_cards(cards))
        body += self.band(lang, "crm", "Chcete CRMDesk mezi prvními?", "Napište obor a velikost týmu – připravíme šablonu na míru.")
        return ("CRMDesk – CRM pro firmy s oborovými šablonami | EasyForLife",
                "CRMDesk: zákazníci, zakázky a obchod přehledně, 37 oborových šablon. Business 490 Kč/měs., Pro 990 Kč/měs.", body)

    def all(self, lang):
        """[(id, slug, title, desc, body)]"""
        out = []
        for pid in SLUGS:
            title, desc, body = getattr(self, pid)(lang)
            c = SVC[pid]["c"] if pid in SVC else "#2563eb"
            out.append((pid, SLUGS[pid], title, desc, f'<div class="fm" style="--c:{c}">{body}</div>' + (SCRIPT if pid == "index" else "")))
        return out

SCRIPT = """<script>(function(){
var f=document.querySelector('.fm-form');if(!f)return;var s=new URLSearchParams(location.search).get('sluzba');
if(s&&f.sluzba.querySelector('option[value="'+s+'"]'))f.sluzba.value=s;
f.addEventListener('submit',function(e){e.preventDefault();var b=f.querySelector('button'),m=f.querySelector('.fm-msg'),t=b.textContent;
b.disabled=true;b.textContent='Odesílám…';m.hidden=true;m.className='fm-msg';
fetch(f.dataset.action,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(Object.fromEntries(new FormData(f)))})
.then(function(r){return r.ok}).catch(function(){return false}).then(function(ok){m.hidden=false;
if(ok){m.textContent=f.dataset.ok;m.classList.add('ok');f.reset();b.textContent='Odesláno ✓';setTimeout(function(){b.textContent=t;b.disabled=false},4000)}
else{m.innerHTML='';m.append(f.dataset.err);var a=document.createElement('a');a.href='mailto:'+f.dataset.mail;a.textContent=f.dataset.mail;m.append(a);m.classList.add('err');b.textContent=t;b.disabled=false}})})})();</script>"""

CSS = """
/* sekce Pro firmy */
.fm-hero{position:relative;margin-top:-76px;padding:104px 0 60px;overflow:hidden;isolation:isolate}
.fm-hero .blobs i:nth-child(1),.fm-hero .blobs i:nth-child(3){background:var(--c)}
.fm-hero .wrap{z-index:2}.fm-hero h1{font-size:clamp(2.3rem,6vw,4.8rem);max-width:15em}.fm-hero .lead{margin:0 0 26px;max-width:42rem}
.fm-sub{display:flex;gap:6px;overflow-x:auto;scrollbar-width:none;margin:0 -20px 34px;padding:4px 20px}.fm-sub::-webkit-scrollbar{display:none}
.fm-sub a{flex:none;font-weight:800;font-size:.88rem;text-decoration:none;padding:8px 14px;border-radius:999px;background:var(--surface);border:1px solid var(--line);transition:background .2s,color .2s,transform .25s cubic-bezier(.3,1.7,.5,1)}
.fm-sub a:hover{transform:translateY(-2px)}.fm-sub a[aria-current]{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.fm-cta{display:flex;flex-wrap:wrap;align-items:center;gap:12px 18px}.fm-cta .ghost{font-size:1rem}
.btn .fi{width:18px;height:18px;transition:transform .25s}.btn:hover .fi{transform:translateX(4px)}
.fm-split{display:grid;grid-template-columns:1.15fr .85fr;gap:40px;align-items:center}
.fm-tiles{display:grid;grid-template-columns:repeat(6,1fr);gap:16px}
.fm-tile{grid-column:span 2;position:relative;display:flex;flex-direction:column;gap:8px;padding:24px;border-radius:28px;text-decoration:none;overflow:hidden;
background:linear-gradient(155deg,color-mix(in oklab,var(--c) 24%,var(--surface)),var(--surface) 70%);border:1px solid color-mix(in oklab,var(--c) 22%,var(--line));box-shadow:var(--shadow);
transition:transform .35s cubic-bezier(.3,1.5,.5,1),box-shadow .35s}
.fm-tile:nth-child(-n+2){grid-column:span 3}.fm-tile:hover{transform:translateY(-6px)}
.fm-tile h3{font:800 1.45rem/1.1 var(--display);letter-spacing:-.02em;margin:8px 0 0}.fm-tile p{margin:0;color:var(--muted);font-size:.97rem}
.fi{width:22px;height:22px;flex:none}.fi.big{width:52px;height:52px;padding:12px;border-radius:16px;color:#fff;background:var(--c);transform:rotate(-6deg);box-shadow:0 12px 24px -12px var(--c);transition:transform .45s cubic-bezier(.3,1.7,.5,1)}
.fm-tile:hover .fi.big{transform:rotate(4deg) scale(1.08)}
.fm-tp{margin-top:auto;padding-top:12px;display:flex;justify-content:space-between;align-items:center;font-size:.95rem}.fm-tp .fi{transition:transform .25s}.fm-tile:hover .fm-tp .fi{transform:translateX(5px)}
.fm-check{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,260px),1fr));gap:10px 22px}
.fm-check li{display:flex;gap:10px;align-items:flex-start;font-weight:600}.fm-check .fi{color:var(--c,var(--green));margin-top:2px}
.fm-prices{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,270px),1fr));gap:16px;align-items:stretch}
.fm-price{position:relative;display:flex;flex-direction:column;gap:12px;padding:26px;border-radius:28px;background:var(--surface);border:1px solid var(--line);box-shadow:var(--shadow);transition:transform .35s cubic-bezier(.3,1.5,.5,1)}
.fm-price:hover{transform:translateY(-4px)}.fm-price.hot{border:2px solid var(--c,var(--blue))}
.fm-price h3{font:800 1.5rem var(--display);margin:0}.fm-price p{margin:0}.fm-price .fm-check{grid-template-columns:1fr;gap:8px;font-size:.95rem;margin-bottom:6px}
.fm-price .btn{margin-top:auto;align-self:flex-start;padding:12px 20px;font-size:.98rem}
.fm-price:not(.hot) .btn{background:var(--surface2);color:var(--ink);box-shadow:none}
.fm-tag{position:absolute;top:-13px;left:22px;font:800 .75rem var(--font);font-style:normal;color:#fff;background:var(--c,var(--blue));border-radius:999px;padding:5px 12px}
.fm-num{font:800 clamp(2rem,4vw,2.6rem)/1 var(--display);letter-spacing:-.03em}.fm-num small{font:700 .95rem var(--font);color:var(--muted);letter-spacing:0}
.muted{color:var(--muted)}.small{font-size:.88rem}
.fm-line{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:14px 24px;margin:16px 0 0;padding:22px 26px;border-radius:24px;background:var(--surface2)}
.fm-line h3{font:800 1.3rem var(--display);margin:0 0 4px}.fm-line p{margin:0}
.fm-steps{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(5,1fr);gap:14px;counter-reset:s}
.fm-steps li{padding:20px;border-radius:24px;background:var(--surface);border:1px solid var(--line)}
.fm-steps b{display:grid;place-items:center;width:38px;height:38px;border-radius:12px;background:var(--c,var(--ink));color:#fff;font:800 1.1rem var(--display);transform:rotate(-6deg)}
.fm-steps h3{font:800 1.12rem var(--display);margin:14px 0 4px}.fm-steps p{margin:0;color:var(--muted);font-size:.93rem}
.fm-work{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,230px),1fr));gap:14px}
.fm-work a{display:flex;flex-direction:column;gap:4px;padding:20px;border-radius:22px;background:var(--surface);border:1px solid var(--line);text-decoration:none;transition:transform .3s cubic-bezier(.3,1.5,.5,1)}
.fm-work a:hover{transform:translateY(-4px)}.fm-work small{color:var(--muted);font-weight:700}.fm-work h3{font:800 1.2rem var(--display);margin:0}.fm-work span{color:var(--muted);font-size:.93rem}
.fm-band{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:20px;padding:34px;border-radius:32px;color:#fff;
background:linear-gradient(120deg,color-mix(in oklab,var(--c) 88%,#000),color-mix(in oklab,var(--c) 60%,#141518));box-shadow:0 30px 60px -30px var(--c)}
.fm-band h2{font:800 clamp(1.6rem,3.4vw,2.4rem)/1.05 var(--display);letter-spacing:-.03em;margin:0 0 6px}.fm-band p{margin:0;opacity:.88}
.fm-band .btn.big{background:#fff;color:#141518}
.fm-feats{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,250px),1fr));gap:14px}
.fm-feats article{padding:22px;border-radius:24px;background:var(--surface);border:1px solid var(--line);box-shadow:var(--shadow)}
.fm-feats.soon article{background:transparent;border-style:dashed;box-shadow:none}
.fm-feats.soon h3::after{content:"připravujeme";margin-left:8px;vertical-align:2px;font:800 .68rem var(--font);color:#141518;background:var(--yellow);border-radius:999px;padding:3px 8px}
.fm-feats h3{font:800 1.12rem/1.2 var(--display);margin:0 0 6px}.fm-feats p{margin:0;color:var(--muted);font-size:.94rem}
.fm-demo{padding:24px;border-radius:28px;background:var(--surface);border:1px solid var(--line);box-shadow:var(--shadow);transform:rotate(1.5deg);animation:fmIn .9s cubic-bezier(.2,1.3,.4,1) both .2s}
.fm-demo-h{display:flex;justify-content:space-between;align-items:baseline;margin:0 0 12px;font-size:.95rem}.fm-demo-h+.fm-bar{margin-top:0}.fm-demo-h span{color:var(--muted);font-size:.8rem;font-weight:700}
.fm-bar{display:grid;grid-template-columns:8.5em 1fr;gap:10px;align-items:center;margin:0 0 10px;font-size:.85rem;font-weight:600}
.fm-bar i,.fm-gauge i{display:block;height:12px;border-radius:99px;background:linear-gradient(90deg,var(--c),color-mix(in oklab,var(--c) 55%,var(--blue)));width:var(--w);transform-origin:left;animation:fmGrow 1.1s cubic-bezier(.2,1,.3,1) both;animation-delay:calc(var(--rd,0ms) + .5s)}
.fm-demo-h:nth-of-type(2){margin-top:20px}
.fm-gauge{height:16px;border-radius:99px;background:var(--surface2);overflow:hidden}.fm-gauge i{height:16px;animation-delay:1.1s}
@keyframes fmGrow{from{transform:scaleX(0)}}@keyframes fmIn{from{opacity:0;transform:translateY(30px) rotate(6deg)}}
.fm-flow{display:flex;flex-wrap:wrap;gap:10px;justify-content:center}
.fm-flow span{display:flex;align-items:center;gap:8px;padding:10px 16px 10px 10px;border-radius:999px;background:var(--surface);border:1px solid var(--line);font-weight:800;box-shadow:var(--shadow)}
.fm-flow b{display:grid;place-items:center;width:28px;height:28px;border-radius:50%;background:var(--orange);color:#fff;font-size:.85rem}
.fm-form-sec{scroll-margin-top:10px}.fm-h2{font:800 clamp(2rem,4.6vw,3.4rem)/1 var(--display);letter-spacing:-.04em;margin:0 0 12px}
.fm-form-grid{display:grid;grid-template-columns:.8fr 1.2fr;gap:34px;align-items:start}
.fm-form{display:grid;grid-template-columns:1fr 1fr;gap:14px;padding:26px;border-radius:28px;background:var(--surface);border:1px solid var(--line);box-shadow:var(--shadow)}
.fm-form label{display:flex;flex-direction:column;gap:6px;font-weight:700;font-size:.9rem;min-width:0}.fm-form .wide{grid-column:1/-1}
.fm-form input,.fm-form select,.fm-form textarea{font:inherit;font-weight:400;padding:12px 14px;border-radius:14px;border:1px solid var(--line);background:var(--bg);color:var(--ink);width:100%;transition:border-color .2s,box-shadow .2s}
.fm-form input:focus,.fm-form select:focus,.fm-form textarea:focus{outline:0;border-color:var(--blue);box-shadow:0 0 0 4px color-mix(in srgb,var(--blue) 22%,transparent)}
.fm-form .hp{position:absolute;left:-9999px;width:1px;height:1px}
.fm-send{display:flex;flex-wrap:wrap;align-items:center;gap:12px}
.fm-send button{font:inherit;font-weight:800;border:0;border-radius:999px;padding:14px 26px;background:var(--ink);color:var(--bg);cursor:pointer;transition:transform .25s cubic-bezier(.3,1.7,.5,1),opacity .2s}
.fm-send button:hover{transform:translateY(-2px)}.fm-send button:disabled{opacity:.6;cursor:default;transform:none}
.fm-msg{margin:0;font-weight:700;animation:fmIn .4s ease both}.fm-msg.ok{color:var(--green)}.fm-msg.err{color:#d93a3a}.fm-msg a{margin-left:4px}
.fm-anchor{scroll-margin-top:10px}.fm-hero+section{padding-top:44px}
@media (max-width:980px){.fm-steps{grid-template-columns:repeat(2,1fr)}.fm-tile,.fm-tile:nth-child(-n+2){grid-column:span 3}.fm-split,.fm-form-grid{grid-template-columns:1fr}.fm-demo{transform:none}}
@media (max-width:600px){.fm-tile,.fm-tile:nth-child(-n+2){grid-column:1/-1}.fm-steps{grid-template-columns:1fr}.fm-form{grid-template-columns:1fr;padding:18px}.fm-band{padding:24px}.fm-hero{padding-top:96px}}
"""
