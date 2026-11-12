// Statický web EasyForLife: easyforlife.cz (čeština) a easyforlife.eu (angličtina + další jazyky).
// Kořen webu podle hostu z dist/routes.json, www → bez www, přesměrování starých adres, gzip, 404 podle webu.
const http = require("http"), https = require("https"), fs = require("fs"), path = require("path"), zlib = require("zlib"), crypto = require("crypto");
const VERSION = (() => { try { return JSON.parse(fs.readFileSync(path.join(__dirname, "dist", "version.json"), "utf8")).version; } catch { return process.env.WEB_VERSION || "dev"; } })();
const DIST = path.join(__dirname, "dist");
const routes = JSON.parse(fs.readFileSync(path.join(DIST, "routes.json"), "utf8"));
const TYPES = { ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8", ".xml": "application/xml", ".txt": "text/plain; charset=utf-8", ".svg": "image/svg+xml",
  ".png": "image/png", ".webp": "image/webp", ".jpg": "image/jpeg", ".ico": "image/x-icon",
  ".dmg": "application/x-apple-diskimage", ".zip": "application/zip" };
const COMPRESS = new Set([".html", ".css", ".js", ".json", ".xml", ".txt", ".svg"]);

// Soubory s vlastní politikou: živý katalog appek (CORS, hodina cache).
// travel-facts.json: ověřená cestovní fakta pro appky (CORS, hodina cache, ETag → 304).
const SPECIAL = { "catalog.json": { "access-control-allow-origin": "*", "cache-control": "public, max-age=3600" },
  "travel-facts.json": { "access-control-allow-origin": "*", "cache-control": "public, max-age=3600, stale-while-revalidate=86400" } };

// Bezpečnostní hlavičky (revize 12. 11. 2026): CSP bez 'unsafe-inline' pro skripty – vložené skripty stránky (generuje
// web.py/build.py) se povolí otiskem SHA-256 spočítaným tady ze souboru, takže nic jiného (podvržený skript) neproběhne.
const INLINE_SCRIPT = /<script(?![^>]*\bsrc=)(?![^>]*type="application\/(?:ld\+)?json")[^>]*>([\s\S]*?)<\/script>/gi;
const cspCache = new Map(); // etag → CSP
function cspFor(html, etag) {
  if (cspCache.has(etag)) return cspCache.get(etag);
  const hashes = new Set();
  for (const m of html.toString("utf8").matchAll(INLINE_SCRIPT)) hashes.add(`'sha256-${crypto.createHash("sha256").update(m[1], "utf8").digest("base64")}'`);
  const csp = ["default-src 'self'", `script-src 'self' ${[...hashes].join(" ")}`.trim(), "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' data: https://fonts.gstatic.com", "img-src 'self' data: https:", "connect-src 'self' https:", "media-src 'self' https:",
    "object-src 'none'", "base-uri 'self'", "form-action 'self' https:", "frame-ancestors 'none'"].join("; ");
  if (cspCache.size > 2000) cspCache.clear();
  cspCache.set(etag, csp);
  return csp;
}
const isHttps = (req) => /https/.test(String(req.headers["x-forwarded-proto"] || req.headers["cf-visitor"] || ""));

function send(req, res, file, status = 200) {
  const ext = path.extname(file);
  let body = fs.readFileSync(file);
  const etag = 'W/"' + crypto.createHash("sha1").update(body).digest("base64url").slice(0, 20) + '"';
  const headers = { "content-type": TYPES[ext] || "application/octet-stream",
    "cache-control": ext === ".html" || ext === ".xml" ? "public, max-age=300" : "public, max-age=86400",
    "x-content-type-options": "nosniff", "referrer-policy": "strict-origin-when-cross-origin", vary: "accept-encoding", etag,
    ...(ext === ".html" ? { "content-security-policy": cspFor(body, etag), "x-frame-options": "DENY" } : {}),
    ...(isHttps(req) ? { "strict-transport-security": "max-age=15552000; includeSubDomains" } : {}),
    ...(SPECIAL[path.basename(file)] || {}) };
  if (status === 200 && req.headers["if-none-match"] === etag) { res.writeHead(304, headers); return res.end(); }
  if (COMPRESS.has(ext) && /\bgzip\b/.test(req.headers["accept-encoding"] || "")) { body = zlib.gzipSync(body); headers["content-encoding"] = "gzip"; }
  res.writeHead(status, headers);
  res.end(req.method === "HEAD" ? undefined : body);
}
// Malé servery za cestou (bez nové domény): easyforlife.cz/darecky/… → Dárečky (oslavy) – kontejner nas-darecky na NASu.
const UPSTREAMS = { "/darecky": process.env.DARECKY_URL || "http://nas-darecky:8080" };
const HOP = new Set(["connection", "keep-alive", "transfer-encoding", "upgrade", "proxy-connection", "te", "trailer", "host"]);
function proxy(req, res, upstream) {
  const target = new URL(req.url, upstream);
  const headers = {};
  for (const [k, v] of Object.entries(req.headers)) if (!HOP.has(k) && !k.startsWith("fly-") && !k.startsWith("x-efl-")) headers[k] = v;
  headers["x-forwarded-host"] = req.headers.host || "";
  // IP návštěvníka pro limity Dárečků: cf-connecting-ip od Cloudflare tunelu (klient ji nepodvrhne), jinak socket
  headers["x-efl-client-ip"] = req.headers["cf-connecting-ip"] || req.socket.remoteAddress || "";
  if (process.env.PROXY_SECRET) headers["x-efl-proxy"] = process.env.PROXY_SECRET;
  const up = (target.protocol === "http:" ? http : https).request(target, { method: req.method, headers, timeout: 30000 }, (r) => {
    const out = {};
    for (const [k, v] of Object.entries(r.headers)) if (!HOP.has(k)) out[k] = v;
    res.writeHead(r.statusCode, out);
    r.pipe(res);
  });
  up.on("timeout", () => up.destroy(new Error("timeout")));
  up.on("error", () => { if (!res.headersSent) { res.writeHead(502, { "content-type": "text/plain" }); } res.end("Bad gateway"); });
  req.pipe(up);
}
// Palec nahoru/dolů ze stránek podpory: anonymně (stránka, jazyk, hlas), bez IP a cookies – řádek do /data/feedback.jsonl
// (svazek na NASu, v nočních zálohách) a do logu (docker logs nas-web | grep feedback).
const VOTES = {};
const FEEDBACK_FILE = process.env.FEEDBACK_FILE || (fs.existsSync("/data") ? "/data/feedback.jsonl" : "");
function feedback(req, res) {
  let b = "";
  req.on("data", (c) => { b += c; if (b.length > 512) req.destroy(); });
  req.on("end", () => {
    try {
      const { p, l, v } = JSON.parse(b);
      if (/^[a-z0-9-]{1,40}$/.test(p) && /^[a-z]{2}$/.test(l) && (v === 1 || v === -1)) {
        const k = `${p}/${l}`, c = (VOTES[k] ||= { up: 0, down: 0 });
        c[v > 0 ? "up" : "down"]++;
        console.log("feedback", JSON.stringify({ page: p, lang: l, vote: v, total: c }));
        if (FEEDBACK_FILE) fs.appendFile(FEEDBACK_FILE, JSON.stringify({ at: new Date().toISOString(), page: p, lang: l, vote: v }) + "\n", () => {});
      }
    } catch {}
    res.writeHead(204); res.end();
  });
}
const redirect = (res, to, code = 301) => { res.writeHead(code, { location: to, "cache-control": "public, max-age=3600" }); res.end(); };

http.createServer((req, res) => {
  const host = (req.headers.host || "").split(":")[0].toLowerCase();
  const url = new URL(req.url, "http://x");
  if (url.pathname === "/healthz") { res.writeHead(200, { "content-type": "application/json" }); return res.end(JSON.stringify({ ok: true, version: VERSION })); }
  if (url.pathname === "/api/feedback" && req.method === "POST") return feedback(req, res);
  // motokoutek.cz: dočasná stránka „Připravujeme“ (rozhodnutí z revize 12. 11. 2026), dokud e-shop neběží
  if (host === "motokoutek.cz" || host === "www.motokoutek.cz") return send(req, res, path.join(__dirname, "motokoutek.html"));
  if (host.startsWith("www.")) return redirect(res, `https://${host.slice(4)}${req.url}`);
  for (const [prefix, upstream] of Object.entries(UPSTREAMS)) {
    if (url.pathname === prefix || url.pathname.startsWith(prefix + "/")) return proxy(req, res, upstream);
  }
  for (const r of routes.redirects) {
    if (r.host === host && url.pathname.startsWith(r.prefix)) {
      const rest = url.pathname.slice(r.prefix.length);
      const to = r.files_to && path.extname(rest) ? r.files_to + rest : r.to + rest;
      return redirect(res, to + url.search, r.files_to ? 302 : 301);
    }
  }
  const site = routes.hosts[host] || "cz";
  const root = path.join(DIST, site);
  let p;
  try { p = path.normalize(path.join(root, decodeURIComponent(url.pathname))); } catch { p = root; }
  if (!p.startsWith(root)) return send(req, res, path.join(root, "404.html"), 404);
  if (fs.existsSync(p) && fs.statSync(p).isDirectory()) {
    if (!url.pathname.endsWith("/")) return redirect(res, url.pathname + "/" + url.search);
    p = path.join(p, "index.html");
  }
  if (fs.existsSync(p) && fs.statSync(p).isFile()) return send(req, res, p);
  return send(req, res, path.join(root, "404.html"), 404);
}).listen(process.env.PORT || 8080);
