// Statický web EasyForLife: easyforlife.cz (čeština) a easyforlife.eu (angličtina + další jazyky).
// Kořen webu podle hostu z dist/routes.json, www → bez www, přesměrování starých adres, gzip, 404 podle webu.
const http = require("http"), fs = require("fs"), path = require("path"), zlib = require("zlib");
const DIST = path.join(__dirname, "dist");
const routes = JSON.parse(fs.readFileSync(path.join(DIST, "routes.json"), "utf8"));
const TYPES = { ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8",
  ".json": "application/json", ".xml": "application/xml", ".txt": "text/plain; charset=utf-8", ".svg": "image/svg+xml",
  ".png": "image/png", ".webp": "image/webp", ".jpg": "image/jpeg", ".ico": "image/x-icon" };
const COMPRESS = new Set([".html", ".css", ".js", ".json", ".xml", ".txt", ".svg"]);

function send(req, res, file, status = 200) {
  const ext = path.extname(file);
  const headers = { "content-type": TYPES[ext] || "application/octet-stream",
    "cache-control": ext === ".html" || ext === ".xml" ? "public, max-age=300" : "public, max-age=86400",
    "x-content-type-options": "nosniff", "referrer-policy": "strict-origin-when-cross-origin", vary: "accept-encoding" };
  let body = fs.readFileSync(file);
  if (COMPRESS.has(ext) && /\bgzip\b/.test(req.headers["accept-encoding"] || "")) { body = zlib.gzipSync(body); headers["content-encoding"] = "gzip"; }
  res.writeHead(status, headers);
  res.end(req.method === "HEAD" ? undefined : body);
}
const redirect = (res, to, code = 301) => { res.writeHead(code, { location: to, "cache-control": "public, max-age=3600" }); res.end(); };

http.createServer((req, res) => {
  const host = (req.headers.host || "").split(":")[0].toLowerCase();
  const url = new URL(req.url, "http://x");
  if (url.pathname === "/healthz") { res.writeHead(200); return res.end("ok"); }
  if (host.startsWith("www.")) return redirect(res, `https://${host.slice(4)}${req.url}`);
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
