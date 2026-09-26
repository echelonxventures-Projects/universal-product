/* LUXORA Platform - multi-tenant HTTP(S) server with 10-layer security stack */
"use strict";

const http = require("http");
const https = require("https");
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const { run, get, all } = require("./lib/db.js");
const api = require("./lib/api.js");
const metrics = require("./lib/metrics.js");
const sec = require("./lib/security.js");
sec.initDb({ get, run, all });
const idem = require("./lib/idempotency.js");
require("./lib/modules.js").ensureBaselines();
try { require("./lib/env.js").boot(); } catch (e) { console.error("env boot:", e.message); }

const PORT = Number(process.env.PORT || 8787);
const PUB = path.join(__dirname, "public");
const DAY = 86400;
const MIME = {
  ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
  ".js": "application/javascript; charset=utf-8", ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".ico": "image/x-icon", ".txt": "text/plain; charset=utf-8"
};

/* L1 transport */
const TLS = sec.tlsReady();
const IS_TLS = !!TLS;
/* headers are policy-driven and computed per request (L1) */
/* L9 supply chain: SRI hashes computed fresh per request (see sec.applySri) so edited assets never ship stale integrity */
/* L8 abuse control */
const authLimiter = sec.RateLimiter(() => sec.policy().authPerMin, () => sec.policy().authPerMin / 60);
const apiLimiter = sec.RateLimiter(() => sec.policy().apiPerMin, () => sec.policy().apiPerMin / 60);

function parseCookies(str) {
  const out = {};
  (str || "").split(";").forEach(c => { const i = c.indexOf("="); if (i > 0) out[c.slice(0, i).trim()] = decodeURIComponent(c.slice(i + 1).trim()); });
  return out;
}

function resolveTenant(req, url, cookies) {
  const host = String(req.headers.host || "").split(":")[0].toLowerCase();
  const sub = host.includes(".") ? host.split(".")[0] : "";
  let t = (sub && sub !== "www" && get("SELECT * FROM tenants WHERE domain LIKE ? OR slug=?", sub + ".%", sub)) ||
    (url.searchParams.get("store") && get("SELECT * FROM tenants WHERE slug=?", url.searchParams.get("store"))) ||
    (cookies.store && get("SELECT * FROM tenants WHERE slug=?", cookies.store)) ||
    get("SELECT * FROM tenants WHERE slug='luxora'") ||
    get("SELECT * FROM tenants ORDER BY id LIMIT 1");
  return t || null;
}

function getSession(req, res, url, cookies) {
  const tenant = resolveTenant(req, url, cookies);
  if (!tenant) return null;
  let sid = cookies.azs;
  let s = sid && get("SELECT * FROM sessions WHERE sid=? AND expires_at > datetime('now')", sid);
  if (!s) {
    sid = crypto.randomBytes(24).toString("hex");
    run("INSERT INTO sessions(sid, expires_at) VALUES(?, datetime('now','+30 days'))", sid);
    s = get("SELECT * FROM sessions WHERE sid=?", sid);
    res.appendHeader("Set-Cookie", `azs=${sid}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${30 * DAY}${IS_TLS ? "; Secure" : ""}`);
  }
  const st = get("SELECT * FROM tenant_state WHERE sid=? AND tenant_id=?", sid, tenant.id) || { zip: "98109", gift_balance: 0 };
  if (!get("SELECT sid FROM tenant_state WHERE sid=? AND tenant_id=?", sid, tenant.id)) run("INSERT INTO tenant_state(sid,tenant_id) VALUES(?,?)", sid, tenant.id);
  let userTenantOk = true;
  if (s.user_id) {
    const u = get("SELECT tenant_id FROM users WHERE id=?", s.user_id);
    if (!u || u.tenant_id !== tenant.id) userTenantOk = false;
  }
  const session = { sid, user_id: userTenantOk ? s.user_id : null, tenant, zip: st.zip, gift_balance: st.gift_balance, coupon: st.coupon || "", csrf: s.csrf };
  if (cookies.azp) {
    const ps = get("SELECT * FROM platform_sessions WHERE ptid=? AND expires_at > datetime('now')", cookies.azp);
    if (ps) session.ptid = ps.ptid, session.platform_admin = get("SELECT id,name,email FROM platform_admins WHERE id=?", ps.admin_id);
  }
  return session;
}

function safeJoin(root, urlPath) {
  const p = path.normalize(path.join(root, decodeURIComponent(urlPath.split("?")[0])));
  return p.startsWith(root) ? p : null;
}
function serveStatic(req, res, pathname) {
  let file = safeJoin(PUB, pathname);
  if (!file) return notFound(res);
  if (pathname === "/" || pathname === "") file = path.join(PUB, "index.html");
  if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, "index.html");
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) return notFound(res);
  const ext = path.extname(file).toLowerCase();
  const base = { "Content-Type": MIME[ext] || "application/octet-stream", "Cache-Control": ext === ".html" ? "no-cache" : "public, max-age=3600" };
  if (ext === ".html") {
    fs.readFile(file, (err, buf) => {
      if (err) { res.writeHead(500, base); return res.end(); }
      const html = sec.applySri(buf.toString("utf8"), PUB);
      res.writeHead(200, base);
      res.end(html);
    });
    return;
  }
  if (ext === ".js" || ext === ".css") {
    fs.readFile(file, (err, buf) => { if (err) { res.writeHead(500, base); return res.end(); } res.writeHead(200, base); res.end(buf); });
    return;
  }
  res.writeHead(200, base);
  fs.createReadStream(file).pipe(res);
}
function notFound(res) {
  res.writeHead(404, { "Content-Type": "text/html; charset=utf-8" });
  fs.readFile(path.join(PUB, "404.html"), (err, buf) => res.end(err ? "<h1>404 Not Found</h1>" : buf));
}
function readBody(req) {
  return new Promise((resolve) => {
    let data = "", len = 0;
    req.on("data", c => { len += c.length; if (len > 1e6) { resolve(JSON.parse(data || "{}")); req.destroy(); return; } data += c; });
    req.on("end", () => { try { resolve(JSON.parse(data || "{}")); } catch (e) { resolve({}); } });
  });
}

const handler = async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host || "localhost"}`);
  const t0 = Date.now();
  const cookies = parseCookies(req.headers.cookie);
  const clientIp = (req.socket && req.socket.remoteAddress) || "";
  req.__trace = req.headers["x-request-id"] || crypto.randomUUID();
  for (const [k, v] of Object.entries(sec.securityHeaders(IS_TLS))) res.setHeader(k, v);
  res.setHeader("X-Request-Id", req.__trace); res.setHeader("X-Trace-Id", req.__trace);
  res.setHeader("Access-Control-Expose-Headers", "X-Request-Id, X-Trace-Id");
  if (IS_TLS && sec.policy().hsts) res.setHeader("Strict-Transport-Security", "max-age=31536000; includeSubDomains");
  res.on("finish", () => {
    const tenant = res.__tenantId || 0;
    metrics.record(tenant, req.method, url.pathname, res.statusCode, Date.now() - t0);
    if (process.env.LX_LOG === "json") console.log(JSON.stringify({ ts: new Date().toISOString(), lvl: res.statusCode >= 500 ? "error" : "info", trace: req.__trace, tenant, method: req.method, path: url.pathname, status: res.statusCode, ms: Date.now() - t0 }));
    else console.log(`${req.method.padEnd(6)} [t${tenant}] ${url.pathname.padEnd(34)} ${res.statusCode} ${Date.now() - t0}ms ${req.__trace ? "#" + String(req.__trace).slice(0, 8) : ""}`);
  });
  try {
    if (url.pathname.startsWith("/api/")) {
      if (!apiLimiter(clientIp)) { res.writeHead(429, { "Content-Type": "application/json", "Retry-After": "5" }); return res.end(JSON.stringify({ error: "Rate limit exceeded" })); }
      if (/^\/api\/(auth|platform)\/login/.test(url.pathname) && !authLimiter(clientIp + ":auth")) { res.writeHead(429, { "Content-Type": "application/json", "Retry-After": "30" }); return res.end(JSON.stringify({ error: "Too many authentication attempts — slow down" })); }
      const origin = req.headers.origin || req.headers.referer;
      if (["POST", "PUT", "DELETE"].includes(req.method) && origin) {
        let oh; try { oh = new URL(origin).host; } catch (e) { oh = ""; }
        if (oh && oh !== req.headers.host) { res.writeHead(403, { "Content-Type": "application/json" }); return res.end(JSON.stringify({ error: "Cross-origin mutation rejected" })); }
      }
      const session = getSession(req, res, url, cookies);
      if (url.searchParams.get("store")) {
        const cur = res.getHeader("Set-Cookie");
        const arr = cur ? (Array.isArray(cur) ? cur : [cur]) : [];
        arr.push(`store=${url.searchParams.get("store")}; Path=/; Max-Age=${365 * DAY}; SameSite=Lax${IS_TLS ? "; Secure" : ""}`);
        res.setHeader("Set-Cookie", arr);
      }
      if (!session) return api.bad(res, "No store configured", 500);
      res.__tenantId = session.tenant.id;
      /* L2: CSRF double-submit for cookie-carrying mutations */
      if (!session.csrf) {
        session.csrf = sec.csrfToken();
        run("UPDATE sessions SET csrf=? WHERE sid=?", session.csrf, session.sid);
        res.appendHeader("Set-Cookie", `azc=${session.csrf}; Path=/; SameSite=Lax; Max-Age=2592000${IS_TLS ? "; Secure" : ""}`);
      }
      if (sec.policy().csrfEnabled && ["POST", "PUT", "DELETE"].includes(req.method) && cookies.azs && !sec.csrfOk({ headers: { "x-csrf": req.headers["x-csrf"] || req.headers["x-csrf-token"] } }, session)) {
        res.writeHead(403, { "Content-Type": "application/json" }); return res.end(JSON.stringify({ error: "Missing or invalid CSRF token" }));
      }
      if (session.tenant.status === "suspended" && !session.platform_admin) return api.bad(res, "This store is suspended", 403);
      let body = {};
      if (["POST", "PUT", "DELETE"].includes(req.method)) body = await readBody(req);
      session.trace = req.__trace;
      /* idempotency: safe client retries for mutations */
      const idemKey = req.headers["idempotency-key"] || req.headers["x-idempotency-key"];
      if (idem.enabled() && idemKey && ["POST", "PUT", "DELETE"].includes(req.method)) {
        const c = idem.claim(idemKey, session.tenant.id, req.method, url.pathname, body);
        if (c.replay) { res.writeHead((c.replay.status || 200), { "Content-Type": "application/json", "X-Idempotent-Replay": "true" }); return res.end(c.replay.response || "{}"); }
        if (c.conflict) { res.writeHead(422, { "Content-Type": "application/json" }); return res.end(JSON.stringify({ error: "Idempotency key already used with a different request payload" })); }
        const _end = res.end.bind(res); const _wh = res.writeHead.bind(res); let st = res.statusCode; let cap = "";
        res.writeHead = (s, h) => { st = s || st; return _wh(s, h); };
        res.end = (chunk) => { if (chunk != null) cap += (typeof chunk === "string" ? chunk : Buffer.from(chunk).toString("utf8")); let parsed; try { parsed = JSON.parse(cap); } catch (e) { parsed = cap; } idem.store(idemKey, session.tenant.id, st, parsed); return _end(chunk); };
      }
      const handled = api.handle(req, res, url, session, body, metrics);
      if (!handled) api.bad(res, "No such API endpoint", 404);
      return;
    }
    if (req.method !== "GET" && req.method !== "HEAD") { res.writeHead(405); return res.end("Method Not Allowed"); }
    if (url.pathname === "/healthz") {
      const t = resolveTenant(req, url, cookies);
      res.writeHead(200, { "Content-Type": "application/json" });
      return res.end(JSON.stringify({ ok: true, tenant: t && t.slug, products: get("SELECT COUNT(*) c FROM products WHERE tenant_id=?", t.id).c, uptime: Math.floor(process.uptime()), tls: IS_TLS }));
    }
    if (url.pathname === "/metrics") {
      const body = require("./lib/enterprise.js").promMetrics(metrics.snapshot(null));
      res.writeHead(200, { "Content-Type": "text/plain; version=0.0.4" });
      return res.end(body);
    }
    if (url.searchParams.get("store")) res.appendHeader("Set-Cookie", `store=${url.searchParams.get("store")}; Path=/; Max-Age=${365 * DAY}; SameSite=Lax`);
    serveStatic(req, res, url.pathname);
  } catch (e) {
    console.error("FATAL", e);
    if (!res.headersSent) res.writeHead(500, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: "internal" }));
  }
};

const server = http.createServer(handler);
const listenServer = IS_TLS ? https.createServer(TLS, handler) : server;

function shutdown(sig) { console.log(`\n${sig} — closing`); sec.persistState(); server.close(() => process.exit(0)); setTimeout(() => process.exit(0), 2000); }
process.on("SIGINT", () => shutdown("SIGINT"));
process.on("SIGTERM", () => shutdown("SIGTERM"));

listenServer.listen(PORT, () => {
  const tenants = all("SELECT slug FROM tenants");
  console.log(`
  ██╗  ██╗██╗   ██╗██╗  ██╗ ██████╗ ██████╗  ██████╗  █████╗
  ██║  ██║██║   ██║██║ ██╔╝██╔═══██╗██╔══██╗██╔════╝ ██╔══██╗
  ███████║██║   ██║█████╔╝ ██║   ██║██████╔╝██║  ███╗███████║
  ██╔══██║██║   ██║██╔═██╗ ██║   ██║██╔══██╗██║   ██║██║  ██║
  ██║  ██║╚██████╔╝██║  ██╗╚██████╔╝██║  ██║╚██████╔╝██║  ██║
  ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝
  P L A T F O R M  ·  white-label multi-store commerce  ·  🛡 10-layer security${IS_TLS ? " (TLS ON)" : " (HTTP — set LUX_TLS=1 for HTTPS)"}

  🏬 Stores:      ${tenants.map(t => `http${IS_TLS ? "s" : ""}://${t.slug}.localhost:${PORT} (${t.slug})`).join("  |  ")}
  🧾 Store admin: http${IS_TLS ? "s" : ""}://localhost:${PORT}/admin.html      (admin@luxora.shop / admin123)
  🛰  Platform:   http${IS_TLS ? "s" : ""}://localhost:${PORT}/platform.html   (platform@luxora.shop / platform123)
   🔐 Scorecard:   GET /api/platform/security
`);
  /* optional multi-node Redis queue worker (config-driven; off unless queue=redis and LX_WORKER≠0) */
  try { const cfg = require("./lib/config.js"), ad = require("./lib/adapters.js");
    if (cfg.driverOf("queue") === "redis" && process.env.LX_WORKER !== "0") { const w = ad.startWorker(cfg.get("queue"), {}); if (w.active) console.log("   ⚙️  Redis queue worker: RUNNING"); }
    if (cfg.driverOf("db") === "postgres") { const a = ad.build("db", cfg.get("db")); if (a.configured) a.ping().then(r => console.log("   🐘 postgres " + (r.ok ? "reachable" : "unreachable: " + r.error))).catch(() => { }); }
  } catch (e) { }
});
