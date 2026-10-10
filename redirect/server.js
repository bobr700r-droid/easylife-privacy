// easyforlife.cz (+ www) → 301 na https://easyforlife.eu se zachováním cesty a query.
const http = require("http");
const TARGET = process.env.REDIRECT_TO || "https://easyforlife.eu";
http.createServer((req, res) => {
  if (req.url === "/healthz") { res.writeHead(200, { "content-type": "text/plain" }); return res.end("ok"); }
  res.writeHead(301, { location: TARGET + req.url, "cache-control": "public, max-age=86400" });
  res.end();
}).listen(process.env.PORT || 8080);
