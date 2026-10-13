

# Web EasyForLife (easyforlife.cz / .eu) a zásady soukromí – plán

Soubor zřízen 13. 10. 2026 před archivací vlákna **b8375cf3** (Build EasyLife website). Web se generuje v této složce (`build.py`, `web.py`, `site/`, `deploy.sh`), katalog appek je v `../EasyLife/catalog.json`. Repo `bobr700r-droid/easylife-privacy` (GitHub Pages ze `docs/`).

## Stav (13. 10. 2026)
- Web hotový a nasazený na Fly (app `easyforlife-redirect`, `server/server.js` vybírá web podle hostu): **easyforlife.cz** česky, **easyforlife.eu** anglicky (+ `/sk/ /de/ /es/ /pl/`); 6 jazyků, světlý/tmavý režim, favicon a OG obrázek (`site/art.swift`, `python3 build.py --art`), detail appky `/<slug>/`, zásady soukromí `/<slug>.html` (URL v ASC nesmí se rozbít, i staré `bobr700r-droid.github.io/easylife-privacy/<slug>.html`), živý katalog `https://easyforlife.cz/catalog.json` pro appky, stránka podpory `/podpora/`.
- Původní zadání 10. 10.: hlavní doména .eu, .cz 301 na .eu; později uživatel rozhodl **.cz česky a .eu anglicky** (viz README) – `EU_LIVE` přepíná podle DNS.

- (2026-10-13) Podmínky užití – licence: /podminky/ (cs, sk), /terms/ (ostatní), © 2026 Lukáš Ochrana v patičce (web.py). Čeká na nasazení (deploy.sh – build.py má cizí necommitnuté změny, deploy počká na jejich commit). Plné podmínky (vyloučení odpovědnosti, BACKLOG §5) zatím ne.
- (2026-10-13) **Svatebníček jako samostatný projekt** (zadání uživatele 13. 10.): sekce „Další projekty“ (`#projekty`) na úvodu všech jazyků, štítek „Samostatný projekt“, nepočítá se do počtu appek ani do rodin; detail `/svatebnicek/` s poznámkou o jednorázovém nákupu (během testování zdarma) a odkazy na vlastní web/zásady (cs/sk mujsvatebnicek.cz, ostatní svatebnicek.eu). Řídí se příznakem `separate` v catalog.json (`web.py`: `projects`, `separate_note`, `own_url`), obsah `site/apps/svatebnicek.json`, stav TestFlight. Svatebníček zatím nemá stránku podmínek – odkazuje se na jeho web.
- (2026-10-13) **Web 1.3**: Cestovníček – zásady (příprava na cestu, offline balíček, Sdílet → Cestovníček, Kartičky jen název+platnost, seznam appek a zápis výdajů), barva #1f6f5c (§21); Jídelník 1.1 (deník návštěv, sdílení seznamu, hlasování; sloučena větev `jidelnik-soukromi-1-1`); Vyrovnáno (poloha, zámek, připomínky, Živá aktivita, #28b87a); katalog: Lékárnička akce `travel` = `lekarnicka://cesta?od={from}&do={to}&zdroj={src}`.
- (2026-10-13) **Web 1.1** (`VERSION` ve web.py, `<meta name="version">`): Rozpočet – sekce „Sken účtenky“ (jen v telefonu, nikam se neposílá); Garážka – tankování z Navigace nasazeno; Svatebníček – podmínky užití na mujsvatebnicek.cz/podminky a svatebnicek.eu/terms, v katalogu `terms`/`termsEn`, odkaz v poznámce samostatného projektu.
- (2026-10-13) **Web 1.2** nasazen: Studium 1.2 – sekce „Přednášky s AI“ (mikrofon, přepis řeči a OCR tabule jen v zařízení, nic se neposílá ven, zvuk se nesynchronizuje), žebříček, kalendář; Kariéra – mikrofon a trénink nahlas (přepis v zařízení, nahrávka se hned maže), sken smlouvy OCR v zařízení, motivační dopis přes Apple Intelligence. Změny Cestovníčku v build.py (cizí vlákno) zůstaly necommitnuté.
- (2026-10-13) **Web 1.6**: detaily Studium/Pohodička/Kariérník/Dům a zahrada, Schema.org + hreflang v sitemap, Co je nového + RSS, 404 s hledáním, palec na podpoře.
## Otevřené zadání uživatele
- [x] 10. 10. 20:41: _(13. 10. uživatel schválil – předáno přes Vedení projektů)_ „web je strašný, má být svěží, moderní, trochu bláznivý, ikony z appek, různě velké, rozlétané dlaždice, animace“ – přepracováno (rozložení karet opraveno 11. 10.), **ověřit s uživatelem spokojenost** a dolaďovat.
- [x] 11. 10. 6:54: **FotoDesk jinou ikonu** _(13. 10. ověřeno: ikona z appky FotoDesk, family foto + alsoFamilies v katalogu, na webu ve Foto)_, předat příslušným sessions a zařadit FotoDesk do kategorie **Foto** v katalogu/webu – ověřit v `catalog.json` a na webu.
- [x] BACKLOG §6: _(Web 1.4, kolečko podle rodin)_ **kolečko propojení appek** zjednodušit (seskupit podle rodin, ať není přeplácané).
- [x] BACKLOG §5: _(Web 1.4: /podminky/ + /terms/, 6 jazyků; živě 13. 10.)_ publikovat **Podmínky užití + zásady** pro všechny appky (souhlas při prvním spuštění; maximální vyloučení odpovědnosti v mezích českého/EU práva) na easyforlife.cz.
- [x] Rozpočet: štítek _(status testflight; /rozpocet.html živě)_ „Brzy“ → TestFlight (po ASC); ASC Privacy URL `https://easyforlife.cz/rozpocet.html` + Support URL.
- [x] Nové appky do katalogu _(13. 10. doplněny detaily studium/pohoda/kariera/dumazahrada – dřív ukazovaly „Brzy“)_ a na web: Rodinka, Kuchařka, Kartičky, Rozpočet, Dům a zahrada, Studium, ~~Svatebníček~~ (hotovo 13. 10. jako samostatný projekt), Pohodička, Kariéra – stránky soukromí v `APPS` v `build.py`, detaily `site/apps/<id>.json`.
- [x] Stránky soukromí a detail pro Salónky _(živě; Kulturník zveřejněn 13. 10. – veřejná appka ČR)_ (6 jazyků), Kulturník (zatím nepublikovat).
- [x] DNS: _(easyforlife.eu živě 200; další domény jen se souhlasem uživatele)_ easyforlife.eu a ostatní domény zadává uživatel u Forpsi ručně; vždy se souhlasem.
- [x] Mainhub / Hub: _(/easylife/ živě)_ přehled `EasyForLife Hub` ve webu.
- [x] (13. 10., schválený návrh Vedení #250) _(Web 1.6: JSON-LD v detailu appky, sitemap s xhtml:link)_ Schema.org SoftwareApplication na stránkách appek a hreflang alternates i v sitemap.xml (hreflang v hlavičkách stránek už je, schema ne).
- [x] (13. 10., schválený návrh Vedení #251) _(Web 1.6: /novinky/ + /news/ a rss.xml ze `site/news.json` – při nové verzi appky doplnit)_ Stránka „Novinky / Co je nového“ (changelog appek z katalogu) a RSS.
- [x] (13. 10., schválený návrh Vedení #252) _(hotovo 13. 10.: formulář „Dejte mi vědět“ na úvodu a u appek, volba Android, Mailer double opt-in, zásady soukromi.html#newsletter)_ Registrace na seznam čekatelů/newsletter pro appky „Brzy“ přes Mailer (jen s dvojím souhlasem).
- [x] (13. 10., schválený návrh Vedení #253) _(Web 1.6: 404 s hledáním appek; palec na /podpora/ → POST /api/feedback, anonymně do logu: `fly logs | grep feedback`)_ Vlastní 404 s hledáním v katalogu (404 dnes jen text + odkaz) a měření spokojenosti na stránkách podpory (palec nahoru/dolů).

## Rozhodnutí a pravidla
- Statický web bez frameworků; generuje se z `catalog.json` (jediný zdroj pravdy) – ostatní vlákna sem přidávají zásady soukromí, jejich formát a sekce neupravovat; před commitem `git pull`.
- Commit a push webu je publikace: před prvním/většími změnami ukázat náhled a zeptat se.
- Stará URL soukromí se nesmí rozbít; web česky .cz a anglicky .eu.

## Jak pokračovat
- `cd "/Users/lukasochrana/EasyLife aplikace/Privacy" && python3 build.py` (docs + dist), `./deploy.sh` (build + `fly deploy`), katalog sync `EasyLife/sync-catalog.sh`.
- Push do GitHubu přes čistý worktree jen se svými soubory.
