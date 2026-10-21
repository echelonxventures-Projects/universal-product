/* LUXORA Platform - multi-tenant HTTP(S) server with 10-layer security stack */
"use strict";

/* P0: node:sqlite (lib/db.js) ships unflagged only since Node 22.13 (22.5–22.12 hide it
   behind --experimental-sqlite). This guard must run BEFORE lib/db.js is required —
   otherwise the process dies at require time with a bare "Cannot find module", which
   says nothing about the fix. */
const NV = process.versions.node.split(".").map(Number);
if (NV[0] < 22 || (NV[0] === 22 && NV[1] < 13)) {
  console.error(`\nFATAL  Node ${process.versions.node} is too old — the platform needs the built-in node:sqlite module (Node >= 22.13). Rebuild on node:22-alpine or upgrade the host runtime.\n`);
  process.exit(1);
}

const http = require("http");
const https = require("https");
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const { run, get, all, masterTenant } = require("./lib/db.js");
const api = require("./lib/api.js");
const metrics = require("./lib/metrics.js");
const sec = require("./lib/security.js");
sec.initDb({ get, run, all });
const idem = require("./lib/idempotency.js");
require("./lib/modules.js").ensureBaselines();
try { require("./lib/identity.js").ensureIdentityTemplates(); } catch (e) { console.error("identity templates seed:", e.message); }
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
  (str || "").split(";").forEach(c => { const i = c.indexOf("="); if (i > 0) { const v = c.slice(i + 1).trim(); try { out[c.slice(0, i).trim()] = decodeURIComponent(v); } catch (e) { out[c.slice(0, i).trim()] = v; } } });
  return out;
}

function resolveTenant(req, url, cookies) {
  const host = String(req.headers.host || "").split(":")[0].toLowerCase();
  const sub = host.includes(".") ? host.split(".")[0] : "";
/* A bare-host request (no subdomain, no ?store=, no cookie) resolves to the
   master's own deployment — the deployment the platform itself is — never to a
   peer the operator provisioned. subdomain/?store=/cookie still address any
   deployment explicitly. */
const like = sub.replace(/[\\%_]/g, c => "\\" + c);
let t = (sub && sub !== "www" && get("SELECT * FROM tenants WHERE domain LIKE ? ESCAPE '\\' OR slug=?", like + ".%", sub)) ||
  (url.searchParams.get("store") && get("SELECT * FROM tenants WHERE slug=?", url.searchParams.get("store"))) ||
  (cookies.store && get("SELECT * FROM tenants WHERE slug=?", cookies.store)) ||
  masterTenant();
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
    if (ps) session.ptid = ps.ptid, session.platform_admin = get("SELECT id,name,email,role,perms FROM platform_admins WHERE id=?", ps.admin_id);
  }
  return session;
}

function safeJoin(root, urlPath) {
  let dec; try { dec = decodeURIComponent(urlPath.split("?")[0]); } catch (e) { return null; }
  const p = path.normalize(path.join(root, dec));
  return p === root || p.startsWith(root + path.sep) ? p : null;
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
/* a request body is capped at 1 MB. Past the cap the request is refused with 413 —
   never parsed: JSON.parse on a truncated body throws inside the stream listener, where
   nothing can catch it, and a single anonymous POST took the whole process down. The raw
   text is kept on req.rawBody, because a webhook signature is over the exact bytes the
   sender signed, never over a re-serialization of the parsed object. */
const BODY_LIMIT = 1e6;
function readBody(req) {
  return new Promise((resolve) => {
    const chunks = []; let len = 0, done = false;
    req.on("data", c => {
      if (done) return;
      len += c.length;
      if (len > BODY_LIMIT) { done = true; resolve({ tooLarge: true }); req.resume(); return; }
      chunks.push(c);
    });
    req.on("end", () => {
      if (done) return; done = true;
      const raw = Buffer.concat(chunks).toString("utf8");
      req.rawBody = raw;
      try { resolve({ body: JSON.parse(raw || "{}") }); } catch (e) { resolve({ body: {} }); }
    });
    req.on("error", () => { if (!done) { done = true; resolve({ body: {} }); } });
  });
}

/* the client address. Behind a reverse proxy (nginx, a load balancer, docker's port
   proxy) every request arrives from the proxy's own socket, so per-IP rate limits would
   throttle all users as one. LX_TRUST_PROXY=1 tells the server a trusted proxy sits in
   front and sets X-Forwarded-For; without it the header is attacker-controlled and ignored. */
function clientIpOf(req) {
  if (process.env.LX_TRUST_PROXY === "1") {
    const xff = String(req.headers["x-forwarded-for"] || "").split(",")[0].trim();
    if (xff) return xff;
  }
  return (req.socket && req.socket.remoteAddress) || "";
}
/* a store slug as it may appear in a cookie — anything else is ignored, never echoed */
const SLUG_RE = /^[a-z0-9][a-z0-9-]{0,63}$/i;

const handler = async (req, res) => {
  /* the Host header is client-supplied: a malformed one (`Host: %`) made new URL throw
     here, outside the try below, and killed the process */
  let url;
  try { url = new URL(req.url, `http://${req.headers.host || "localhost"}`); }
  catch (e) { res.writeHead(400, { "Content-Type": "text/plain" }); return res.end("Bad Request"); }
  const t0 = Date.now();
  let cookies;
  try { cookies = parseCookies(req.headers.cookie); } catch (e) { cookies = {}; }
  const clientIp = clientIpOf(req);
  req.__ip = clientIp;
  const rid = String(req.headers["x-request-id"] || "");
  req.__trace = /^[A-Za-z0-9._-]{1,128}$/.test(rid) ? rid : crypto.randomUUID();
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
      if (url.searchParams.get("store") && SLUG_RE.test(url.searchParams.get("store"))) {
        const cur = res.getHeader("Set-Cookie");
        const arr = cur ? (Array.isArray(cur) ? cur : [cur]) : [];
        arr.push(`store=${url.searchParams.get("store")}; Path=/; Max-Age=${365 * DAY}; SameSite=Lax${IS_TLS ? "; Secure" : ""}`);
        res.setHeader("Set-Cookie", arr);
      }
      if (!session) return api.bad(res, "No store configured", 500);
      res.__tenantId = session.tenant.id;
      /* L2: CSRF double-submit for cookie-carrying mutations. The azc cookie is
         re-sent on EVERY response, not just when the token is first minted: the
         console reads it from document.cookie on each POST, so a page loaded from
         a warm session that never received it would send an empty x-csrf and every
         write would 403 (the session cookie itself is HttpOnly, so it cannot serve
         as the source of the token). */
      if (!session.csrf) {
        session.csrf = sec.csrfToken();
        run("UPDATE sessions SET csrf=? WHERE sid=?", session.csrf, session.sid);
      }
      res.appendHeader("Set-Cookie", `azc=${session.csrf}; Path=/; SameSite=Lax; Max-Age=2592000${IS_TLS ? "; Secure" : ""}`);
      if (sec.policy().csrfEnabled && ["POST", "PUT", "DELETE"].includes(req.method) && cookies.azs && !sec.csrfOk({ headers: { "x-csrf": req.headers["x-csrf"] || req.headers["x-csrf-token"] } }, session)) {
        res.writeHead(403, { "Content-Type": "application/json" }); return res.end(JSON.stringify({ error: "Missing or invalid CSRF token" }));
      }
      /* a platform whose state means "blocked" (the tenant machine, lib/states.js) is closed */
      if (!session.platform_admin && require("./lib/states.js").has("tenant", session.tenant.status) && require("./lib/states.js").is("tenant", session.tenant.status, "blocked")) return api.bad(res, "This store is suspended", 403);
      let body = {};
      if (["POST", "PUT", "DELETE"].includes(req.method)) {
        const rb = await readBody(req);
        if (rb.tooLarge) { res.writeHead(413, { "Content-Type": "application/json", "Connection": "close" }); return res.end(JSON.stringify({ error: "Request body too large (limit 1 MB)" })); }
        body = rb.body;
      }
      session.trace = req.__trace;
      /* idempotency: safe client retries for mutations, scoped to the calling principal */
      const idemKey = req.headers["idempotency-key"] || req.headers["x-idempotency-key"];
      if (idem.enabled() && idemKey && ["POST", "PUT", "DELETE"].includes(req.method)) {
        const principal = session.user_id ? "u" + session.user_id : session.platform_admin ? "p" + session.platform_admin.id : "s" + session.sid;
        const c = idem.claim(String(idemKey).slice(0, 255), session.tenant.id, principal, req.method, url.pathname, body);
        if (c.replay) { res.writeHead((c.replay.status || 200), { "Content-Type": "application/json", "X-Idempotent-Replay": "true" }); return res.end(c.replay.response || "{}"); }
        if (c.conflict) { res.writeHead(422, { "Content-Type": "application/json" }); return res.end(JSON.stringify({ error: "Idempotency key already used with a different request payload" })); }
        if (c.inflight) { res.writeHead(409, { "Content-Type": "application/json", "Retry-After": "1" }); return res.end(JSON.stringify({ error: "A request with this idempotency key is still in progress" })); }
        const _end = res.end.bind(res); const _wh = res.writeHead.bind(res); let cap = "";
        res.writeHead = (...a) => _wh(...a);
        res.end = (chunk, ...rest) => { if (chunk != null && typeof chunk !== "function") cap += (typeof chunk === "string" ? chunk : Buffer.from(chunk).toString("utf8")); try { idem.store(c.skey, res.statusCode, cap); } catch (e) { console.error("idempotency store:", e.message); } return _end(chunk, ...rest); };
      }
      const handled = api.handle(req, res, url, session, body, metrics);
      if (!handled) api.bad(res, "No such API endpoint", 404);
      return;
    }
    if (req.method !== "GET" && req.method !== "HEAD") { res.writeHead(405); return res.end("Method Not Allowed"); }
    if (url.pathname === "/healthz") {
      const t = resolveTenant(req, url, cookies);
      res.writeHead(200, { "Content-Type": "application/json" });
      return res.end(JSON.stringify({ ok: true, tenant: t && t.slug, products: t ? get("SELECT COUNT(*) c FROM products WHERE tenant_id=?", t.id).c : 0, uptime: Math.floor(process.uptime()), tls: IS_TLS }));
    }
    if (url.pathname === "/metrics") {
      /* S11: this exposed platform-wide business metrics (24h orders, revenue,
         per-endpoint volumes) to anyone. Two ways in: a bearer token the
         operator sets for the scraper (LX_METRICS_TOKEN), or a live platform
         admin session — the same session the platform console holds. */
      const token = process.env.LX_METRICS_TOKEN;
      const bearer = (req.headers.authorization || "").replace(/^Bearer\s+/i, "");
      /* timingSafeEqual throws RangeError on mismatched lengths, which would escape to
         the outer handler as a 500 + FATAL log — compare only on equal-length input so
         a wrong token is a clean 401, never a crash */
      const bt = Buffer.from(bearer), tt = Buffer.from(token || "");
      const authed = (token && token.length >= 16 && bearer.length === token.length && crypto.timingSafeEqual(bt, tt))
        || (cookies.azp && get("SELECT 1 FROM platform_sessions WHERE ptid=? AND expires_at > datetime('now')", cookies.azp));
      if (!authed) { res.writeHead(401, { "Content-Type": "text/plain", "WWW-Authenticate": 'Bearer realm="luxora-metrics"' }); return res.end("Unauthorized"); }
      const body = require("./lib/enterprise.js").promMetrics(metrics.snapshot(null));
      res.writeHead(200, { "Content-Type": "text/plain; version=0.0.4" });
      return res.end(body);
    }
    /* the unified console's bundles, wrapped server-side (lib/bundle.js) so the browser
       never has to eval fetched source */
    const bm = /^\/js\/bundle\/(store|platform)\.js$/.exec(url.pathname);
    if (bm) {
      res.writeHead(200, { "Content-Type": "application/javascript; charset=utf-8", "Cache-Control": "no-cache" });
      return res.end(require("./lib/bundle.js").wrap(bm[1], PUB));
    }
    /* one console: the old store and platform pages open /console.html in their scope,
       keeping whatever the link carried (?store=, a hand-off ?token=, ?view=) */
    const legacy = { "/admin.html": "store", "/platform.html": "platform" }[url.pathname];
    if (legacy && (req.method === "GET" || req.method === "HEAD")) {
      const q = new URLSearchParams(url.search);
      if (!q.has("scope")) q.set("scope", legacy);
      res.writeHead(302, { Location: "/console.html?" + q.toString(), "Cache-Control": "no-store" });
      return res.end();
    }
    if (url.searchParams.get("store") && SLUG_RE.test(url.searchParams.get("store"))) res.appendHeader("Set-Cookie", `store=${url.searchParams.get("store")}; Path=/; Max-Age=${365 * DAY}; SameSite=Lax${IS_TLS ? "; Secure" : ""}`);
    serveStatic(req, res, url.pathname);
  } catch (e) {
    console.error("FATAL", e);
    if (!res.headersSent) res.writeHead(500, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: "internal" }));
  }
};

const server = http.createServer(handler);
const listenServer = IS_TLS ? https.createServer(TLS, handler) : server;
/* an idle keep-alive connection outlives a load balancer's idle timeout (commonly 60 s), so the
   balancer, never this server, closes it: a server that closes first races the client's next
   request on the same socket (ECONNRESET, or a 502 at the balancer). LX_KEEPALIVE_MS overrides. */
const KEEPALIVE_MS = Number(process.env.LX_KEEPALIVE_MS) || 65000;
for (const sv of new Set([server, listenServer])) { sv.keepAliveTimeout = KEEPALIVE_MS; sv.headersTimeout = KEEPALIVE_MS + 1000; }

/* P0: the seed ships documented default passwords (admin123 / platform123) so a first
   boot is observable. In production they are an open door — refuse to serve until the
   operator sets them, the same way a fresh appliance behaves. Tests and dev set
   NODE_ENV=test or leave it unset, so the guard never fires there. */
function prodCredentialGuard() {
  if (process.env.NODE_ENV !== "production") return;
  const weak = [];
  if (!process.env.PLATFORM_PASSWORD) weak.push(["PLATFORM_PASSWORD", "platform@luxora.shop", "platform123"]);
  if (!process.env.ADMIN_PASSWORD) weak.push(["ADMIN_PASSWORD", "admin@luxora.shop", "admin123"]);
  if (!weak.length) return;
  console.error("\n" + "=".repeat(78));
  console.error("REFUSING TO START IN PRODUCTION WITH SEED-DEFAULT CREDENTIALS");
  console.error("=".repeat(78));
  for (const [env, email, pw] of weak)
    console.error(`  ${email} still boots with the documented default "${pw}".`);
  console.error("  Set the environment variables and restart:");
  for (const [env] of weak) console.error(`    ${env}=<a strong password>`);
  console.error("  (a password already seeded into an existing DB is unaffected — this gate\n"
    + "   only blocks a first boot that would create the accounts with a default.)");
  console.error("=".repeat(78) + "\n");
  process.exit(1);
}
prodCredentialGuard();
/* sign-in codes, magic links and password resets reach a signed-out person only by email/SMS:
   with no platform transport, any store that hasn't set its own can't recover an account */
if (process.env.NODE_ENV === "production" && !require("./lib/mailer.js").transportFor(0, "email"))
  console.warn("  ⚠️  No platform email transport (LX_MAIL_PROVIDER / LX_SMTP_URL / LX_MAIL_FROM) — password resets and sign-in codes are only delivered for stores with their own live email gateway.");

function shutdown(sig) { console.log(`\n${sig} — closing`); sec.persistState(); listenServer.close(() => process.exit(0)); setTimeout(() => process.exit(0), 2000); }
/* a stray rejected promise in an async handler must not take the process down (Node
   >= 15 exits on unhandled rejections); log it with enough context to fix the source */
/* expired idempotency keys are swept hourly (they were only ever deleted lazily on lookup) */
setInterval(() => { try { idem.purge(); } catch (e) { } }, 3600 * 1000).unref();
/* live payments whose webhook never came are looked up with their gateway on a cadence */
require("./lib/api.js").startPaymentSweep();
/* shoppers' alerts are re-checked (prices also move by imports and rules, not only edits) and
   pickup parcels past their holding time expire, on the platform policy's cadence */
(function shopperSweep() {
  const mins = Number(sec.policy().shopperSweepMinutes);
  const t = setTimeout(() => {
    /* each engine with a clock: alerts re-checked, pickup parcels and booking holds expired,
       offers expired, auctions opened and closed, group buys settled, sellers' proceeds released */
    if (mins > 0) for (const m of ["alerts", "pickup", "bookings", "negotiation", "auctions", "groupbuy", "listings", "trials", "options"]) { try { require("./lib/" + m + ".js").sweepAll(); } catch (e) { } }
    shopperSweep();
  }, Math.max(1, mins > 0 ? mins : 15) * 60000);
  if (t.unref) t.unref();
})();
/* platform setup answers given for a later minute are applied when that minute comes */
(function setupSweep() {
  const SU = require("./lib/platform-setup.js");
  const t = setTimeout(() => { try { SU.sweepAll(); } catch (e) { console.error("setup sweep:", e.message); } setupSweep(); }, SU.resolutionMs());
  if (t.unref) t.unref();
})();
process.on("unhandledRejection", (e) => { console.error("unhandledRejection:", e && e.stack || e); });
process.on("SIGINT", () => shutdown("SIGINT"));
process.on("SIGTERM", () => shutdown("SIGTERM"));

listenServer.listen(PORT, () => {
  const tenants = all("SELECT slug FROM tenants");
  const master = masterTenant();
  const fixtures = tenants.filter(t => !master || t.slug !== master.slug);
  console.log(`
  ██╗  ██╗██╗   ██╗██╗  ██╗ ██████╗ ██████╗  ██████╗  █████╗
  ██║  ██║██║   ██║██║ ██╔╝██╔═══██╗██╔══██╗██╔════╝ ██╔══██╗
  ███████║██║   ██║█████╔╝ ██║   ██║██████╔╝██║  ███╗███████║
  ██╔══██║██║   ██║██╔═██╗ ██║   ██║██╔══██╗██║   ██║██║  ██║
  ██║  ██║╚██████╔╝██║  ██╗╚██████╔╝██║  ██║╚██████╔╝██║  ██║
  ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝
   P L A T F O R M  ·  the master global platform, configured into any platform  ·  🛡 10-layer security${IS_TLS ? " (TLS ON)" : " (HTTP — set LUX_TLS=1 for HTTPS)"}

   🏬 Master:      http${IS_TLS ? "s" : ""}://${(master || { slug: "luxora" }).slug}.localhost:${PORT} (the master's own deployment${fixtures.length ? `, +${fixtures.length} fixture${fixtures.length > 1 ? "s" : ""}` : ""})
   🌐 Console:    http${IS_TLS ? "s" : ""}://localhost:${PORT}/console.html    (platform@luxora.shop / platform123 · store admin admin@luxora.shop / admin123)
   🔐 Scorecard:   GET /api/platform/security
`);
  /* optional multi-node Redis queue worker (config-driven; off unless queue=redis and LX_WORKER≠0) */
  try { const cfg = require("./lib/config.js"), ad = require("./lib/adapters.js");
    if (cfg.driverOf("queue") === "redis" && process.env.LX_WORKER !== "0") { const w = ad.startWorker(cfg.get("queue"), {}); if (w.active) console.log("   ⚙️  Redis queue worker: RUNNING"); }
    if (cfg.driverOf("db") === "postgres") { const a = ad.build("db", cfg.get("db")); if (a.configured) a.ping().then(r => console.log("   🐘 postgres " + (r.ok ? "reachable" : "unreachable: " + r.error))).catch(() => { }); }
  } catch (e) { }

  /* queue processors. A scheduled report due in production is enqueued (lib/dashboards.js
     runDue) and executed HERE — this used to look the report up and log "generated"
     without running it, so no scheduled report ever produced output in production.
     The inline driver hands the handler the job data; Bull hands it a Job wrapping it. */
  try {
    const { processJob } = require("./lib/queue.js");
    processJob("report-run", async (job) => {
      const d = (job && job.data) || job || {};
      const r = require("./lib/dashboards.js").runReport(d.tenantId, d.reportId);
      if (r && r.error) throw new Error(r.error);
      return r;
    });
  } catch (e) { console.error("Queue processor init failed:", e.message); }
});
