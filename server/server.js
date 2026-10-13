// Statický web EasyForLife: easyforlife.cz (čeština) a easyforlife.eu (angličtina + další jazyky).
// Kořen webu podle hostu z dist/routes.json, www → bez www, přesměrování starých adres, gzip, 404 podle webu.
const http = require("http"), https = require("https"), fs = require("fs"), path = require("path"), zlib = require("zlib"), crypto = require("crypto");
const DIST = path.join(__dirname, "dist");
const routes = JSON.parse(fs.readFileSync(path.join(DIST, "routes.json"), "utf8"));
const TYPES = { ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8", ".xml": "application/xml", ".txt": "text/plain; charset=utf-8", ".svg": "image/svg+xml",
  ".png": "image/png", ".webp": "image/webp", ".jpg": "image/jpeg", ".ico": "image/x-icon" };
const COMPRESS = new Set([".html", ".css", ".js", ".json", ".xml", ".txt", ".svg"]);

// Soubory s vlastní politikou: živý katalog appek (CORS, hodina cache).
const SPECIAL = { "catalog.json": { "access-control-allow-origin": "*", "cache-control": "public, max-age=3600" } };

function send(req, res, file, status = 200) {
  const ext = path.extname(file);
  let body = fs.readFileSync(file);
  const etag = 'W/"' + crypto.createHash("sha1").update(body).digest("base64url").slice(0, 20) + '"';
  const headers = { "content-type": TYPES[ext] || "application/octet-stream",
    "cache-control": ext === ".html" || ext === ".xml" ? "public, max-age=300" : "public, max-age=86400",
    "x-content-type-options": "nosniff", "referrer-policy": "strict-origin-when-cross-origin", vary: "accept-encoding", etag,
    ...(SPECIAL[path.basename(file)] || {}) };
  if (status === 200 && req.headers["if-none-match"] === etag) { res.writeHead(304, headers); return res.end(); }
  if (COMPRESS.has(ext) && /\bgzip\b/.test(req.headers["accept-encoding"] || "")) { body = zlib.gzipSync(body); headers["content-encoding"] = "gzip"; }
  res.writeHead(status, headers);
  res.end(req.method === "HEAD" ? undefined : body);
}
// Malé servery za cestou (vlastní Fly app, bez nové domény): easyforlife.cz/darecky/… → Dárečky (oslavy).
const UPSTREAMS = { "/darecky": process.env.DARECKY_URL || "https://darecky.fly.dev" };
const HOP = new Set(["connection", "keep-alive", "transfer-encoding", "upgrade", "proxy-connection", "te", "trailer", "host"]);
function proxy(req, res, upstream) {
  const target = new URL(req.url, upstream);
  const headers = {};
  for (const [k, v] of Object.entries(req.headers)) if (!HOP.has(k) && !k.startsWith("fly-") && !k.startsWith("x-efl-")) headers[k] = v;
  headers["x-forwarded-host"] = req.headers.host || "";
  headers["x-efl-client-ip"] = req.headers["fly-client-ip"] || req.socket.remoteAddress || "";
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
// Palec nahoru/dolů ze stránek podpory: anonymně (stránka, jazyk, hlas), bez IP a cookies – jen řádek do logu (fly logs | grep feedback).
const VOTES = {};
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
      }
    } catch {}
    res.writeHead(204); res.end();
  });
}
const redirect = (res, to, code = 301) => { res.writeHead(code, { location: to, "cache-control": "public, max-age=3600" }); res.end(); };

http.createServer((req, res) => {
  const host = (req.headers.host || "").split(":")[0].toLowerCase();
  const url = new URL(req.url, "http://x");
  if (url.pathname === "/healthz") { res.writeHead(200); return res.end("ok"); }
  if (url.pathname === "/api/feedback" && req.method === "POST") return feedback(req, res);
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
