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
const zlib = require("zlib");
const { run, get, all, masterTenant } = require("./lib/db.js");
const api = require("./lib/api.js");
const metrics = require("./lib/metrics.js");
const sec = require("./lib/security.js");
sec.initDb({ get, run, all });
const idem = require("./lib/idempotency.js");
const mfa = require("./lib/mfa.js");
require("./lib/modules.js").ensureBaselines();
try { require("./lib/identity.js").ensureIdentityTemplates(); } catch (e) { console.error("identity templates seed:", e.message); }
try { require("./lib/env.js").boot(); } catch (e) { console.error("env boot:", e.message); }

const PORT = Number(process.env.PORT || 8787);
const PUB = path.join(__dirname, "public");
const DAY = 86400;
const MIME = {
  ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
  ".js": "application/javascript; charset=utf-8", ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".ico": "image/x-icon", ".txt": "text/plain; charset=utf-8",
  ".webp": "image/webp", ".avif": "image/avif", ".gif": "image/gif", ".woff2": "font/woff2", ".mp4": "video/mp4", ".pdf": "application/pdf", ".webmanifest": "application/manifest+json; charset=utf-8"
};

/* L1 transport */
const TLS = sec.tlsReady();
const IS_TLS = !!TLS;
/* headers are policy-driven and computed per request (L1) */
/* L9 supply chain: SRI hashes computed fresh per request (see sec.applySri) so edited assets never ship stale integrity */
/* L8 abuse control */
const authLimiter = sec.RateLimiter(() => sec.policy().authPerMin, () => sec.policy().authPerMin / 60);
const registerLimiter = sec.RateLimiter(() => sec.policy().registerPerHour, () => sec.policy().registerPerHour / 3600);
const apiLimiter = sec.RateLimiter(() => sec.policy().apiPerMin, () => sec.policy().apiPerMin / 60);

function parseCookies(str) {
  const out = {};
  (str || "").split(";").forEach(c => { const i = c.indexOf("="); if (i > 0) { const v = c.slice(i + 1).trim(); try { out[c.slice(0, i).trim()] = decodeURIComponent(v); } catch (e) { out[c.slice(0, i).trim()] = v; } } });
  return out;
}

/* Which store a request is for: the store its host is the address of (lib/store-domains.js), else the
   one ?store= or the cookie names, else the master's own deployment — the deployment the platform
   itself is — never a peer the operator provisioned. */
function resolveTenant(req, url, cookies) {
  return require("./lib/store-domains.js").storeFor(req.headers.host)
    || (url.searchParams.get("store") && get("SELECT * FROM tenants WHERE slug=?", url.searchParams.get("store")))
    || (cookies.store && get("SELECT * FROM tenants WHERE slug=?", cookies.store))
    || masterTenant() || null;
}

/* a visitor's session exists only once they come back with its cookie (or change something): the
   first page of every crawler would otherwise leave a row behind for a month. The id is signed, so
   only one this server gave out is ever taken up; its CSRF token follows from it. */
const sidSig = r => sec.blindIndex(r, "session.sid").slice(0, 24);
const newSid = () => { const r = crypto.randomBytes(24).toString("hex"); return r + "." + sidSig(r); };
const ours = sid => { const m = /^([0-9a-f]{48})\.([0-9a-f]{24})$/.exec(sid || ""); return !!m && crypto.timingSafeEqual(Buffer.from(m[2]), Buffer.from(sidSig(m[1]))); };
const csrfOf = sid => sec.blindIndex(sid, "session.csrf").slice(0, 32);
function getSession(req, res, url, cookies) {
  const tenant = resolveTenant(req, url, cookies);
  if (!tenant) return null;
  let sid = cookies.azs;
  let s = sid && get("SELECT * FROM sessions WHERE sid=? AND expires_at > datetime('now')", sid);
  let stored = !!s;
  if (!s) {
    const returning = ours(sid);
    if (!returning) sid = newSid();
    if (returning || !["GET", "HEAD"].includes(req.method)) {
      run("INSERT OR IGNORE INTO sessions(sid, expires_at, csrf) VALUES(?, datetime('now','+30 days'), ?)", sid, csrfOf(sid));
      s = get("SELECT * FROM sessions WHERE sid=? AND expires_at > datetime('now')", sid);
      stored = !!s;
    }
    if (!s) s = { sid, user_id: null, csrf: csrfOf(sid) };
    res.appendHeader("Set-Cookie", `azs=${sid}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${30 * DAY}${sec.httpsRequest(req) ? "; Secure" : ""}`);
  }
  const st = get("SELECT * FROM tenant_state WHERE sid=? AND tenant_id=?", sid, tenant.id) || { zip: "98109", gift_balance: 0 };
  if (stored && !get("SELECT sid FROM tenant_state WHERE sid=? AND tenant_id=?", sid, tenant.id)) run("INSERT INTO tenant_state(sid,tenant_id) VALUES(?,?)", sid, tenant.id);
  let userTenantOk = true;
  if (s.user_id) {
    const u = get("SELECT tenant_id FROM users WHERE id=?", s.user_id);
    if (!u || u.tenant_id !== tenant.id) userTenantOk = false;
  }
  const session = { sid, user_id: userTenantOk ? s.user_id : null, mfa_at: s.mfa_at || null, device: cookies[sec.DEVICE_COOKIE] || "", tenant, zip: st.zip, gift_balance: st.gift_balance, coupon: st.coupon || "", csrf: s.csrf };
  if (cookies.azp) {
    const ps = get("SELECT * FROM platform_sessions WHERE ptid=? AND expires_at > datetime('now')", cookies.azp);
    if (ps) {
      session.ptid = ps.ptid;
      const pa = get("SELECT id,name,email,role,perms FROM platform_admins WHERE id=?", ps.admin_id);
      /* until the second factor is confirmed (or set up, where required) the session carries no platform authority */
      const st = pa ? mfa.state("platform", pa.id, ps.mfa_at) : "ok";
      if (st === "ok") session.platform_admin = pa; else session.platform_pending = { ...pa, mfa: st };
    }
  }
  return session;
}

function safeJoin(root, urlPath) {
  let dec; try { dec = decodeURIComponent(urlPath.split("?")[0]); } catch (e) { return null; }
  const p = path.normalize(path.join(root, dec));
  return p === root || p.startsWith(root + path.sep) ? p : null;
}
function serveStatic(req, res, pathname, url) {
  let file = safeJoin(PUB, pathname);
  if (!file) return notFound(res);
  if (pathname === "/" || pathname === "") file = path.join(PUB, "index.html");
  if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, "index.html");
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) return notFound(res);
  const ext = path.extname(file).toLowerCase();
  const st = fs.statSync(file);
  /* an address that carries the file's own version (?v=, written by applySri) never changes */
  const versioned = /^[A-Za-z0-9]{6,}$/.test(url.searchParams.get("v") || "") && ext !== ".html";
  const base = { "Content-Type": MIME[ext] || "application/octet-stream", "Cache-Control": ext === ".html" ? "no-cache" : versioned ? "public, max-age=31536000, immutable" : "public, max-age=3600" };
  if (ext === ".html") {
    fs.readFile(file, (err, buf) => {
      if (err) { res.writeHead(500, base); return res.end(); }
      let html = buf.toString("utf8");
      const t = resolveTenant(req, url, parseCookies(req.headers.cookie));
      const host = String(req.headers.host || "").replace(/[^A-Za-z0-9.:[\]-]/g, "");
      try { html = require("./lib/page-meta.js").page(html, t, pathname || "/", url.searchParams, host ? (sec.httpsRequest(req) ? "https://" : "http://") + host : ""); } catch (e) { console.error("page meta:", e.message); }
      send(req, res, base, Buffer.from(sec.applySri(html, PUB)), null);
    });
    return;
  }
  if (ext === ".js" || ext === ".css" || ext === ".svg" || ext === ".txt") {
    fs.readFile(file, (err, buf) => { if (err) { res.writeHead(500, base); return res.end(); } send(req, res, base, buf, file + ":" + st.mtimeMs + ":" + st.size); });
    return;
  }
  res.writeHead(200, { ...base, "Content-Length": st.size });
  if (req.method === "HEAD") return res.end();
  fs.createReadStream(file).on("error", () => res.destroy()).pipe(res);
}
/* text, with a tag the browser can ask about again (304) and compressed where it accepts that; a
   file's compressed form is kept for as long as the file is unchanged */
const PACKED = new Map();
function send(req, res, headers, buf, key) {
  const etag = '"' + crypto.createHash("sha256").update(buf).digest("base64url").slice(0, 22) + '"';
  const h = { ...headers, ETag: etag, Vary: "Accept-Encoding" };
  if (String(req.headers["if-none-match"] || "").split(",").some(x => x.trim().replace(/^W\//, "") === etag)) { res.writeHead(304, h); return res.end(); }
  const accept = String(req.headers["accept-encoding"] || "");
  const enc = buf.length < 1024 ? null : /\bbr\b/.test(accept) ? "br" : /\bgzip\b/.test(accept) ? "gzip" : null;
  const out = (body, e) => { res.writeHead(200, { ...h, ...(e ? { "Content-Encoding": e } : {}), "Content-Length": body.length }); res.end(req.method === "HEAD" ? undefined : body); };
  if (!enc) return out(buf);
  const k = key && key + ":" + enc, hit = k && PACKED.get(k);
  if (hit) return out(hit, enc);
  const done = (err, body) => { if (err) return out(buf); if (k) { if (PACKED.size > 400) PACKED.delete(PACKED.keys().next().value); PACKED.set(k, body); } out(body, enc); };
  if (enc === "br") zlib.brotliCompress(buf, { params: { [zlib.constants.BROTLI_PARAM_QUALITY]: key ? 9 : 4 } }, done); else zlib.gzip(buf, { level: 6 }, done);
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
   throttle all users as one. LX_TRUST_PROXY is how many trusted proxies sit in
   front (1 for one, 2 for a CDN before it); without it the header is attacker-controlled and ignored. */
function clientIpOf(req) {
  const hops = sec.trustedHops();
  if (hops) {
    /* each trusted proxy appends the address it saw; whatever stands before those was written by the client */
    const xff = String(req.headers["x-forwarded-for"] || "").split(",").map(x => x.trim()).filter(Boolean);
    if (xff.length) return xff[Math.max(0, xff.length - hops)];
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
  for (const [k, v] of Object.entries(sec.securityHeaders(sec.httpsRequest(req)))) res.setHeader(k, v);
  res.setHeader("X-Request-Id", req.__trace); res.setHeader("X-Trace-Id", req.__trace);
  res.setHeader("Access-Control-Expose-Headers", "X-Request-Id, X-Trace-Id");
  if (sec.httpsRequest(req) && sec.policy().hsts) res.setHeader("Strict-Transport-Security", "max-age=31536000; includeSubDomains");
  res.on("finish", () => {
    const tenant = res.__tenantId || 0;
    require("./lib/ops-alerts.js").note(res.statusCode, req.method + " " + url.pathname, req.__trace);
    metrics.record(tenant, req.method, url.pathname, res.statusCode, Date.now() - t0);
    if (process.env.LX_LOG === "json") console.log(JSON.stringify({ ts: new Date().toISOString(), lvl: res.statusCode >= 500 ? "error" : "info", trace: req.__trace, tenant, method: req.method, path: url.pathname, status: res.statusCode, ms: Date.now() - t0 }));
    else console.log(`${req.method.padEnd(6)} [t${tenant}] ${url.pathname.padEnd(34)} ${res.statusCode} ${Date.now() - t0}ms ${req.__trace ? "#" + String(req.__trace).slice(0, 8) : ""}`);
  });
  try {
    if (url.pathname.startsWith("/api/")) {
      if (!apiLimiter(clientIp)) { res.writeHead(429, { "Content-Type": "application/json", "Retry-After": "5" }); return res.end(JSON.stringify({ error: "Rate limit exceeded" })); }
      if (req.method === "POST" && url.pathname === "/api/auth/register" && !registerLimiter(clientIp + ":reg")) { res.writeHead(429, { "Content-Type": "application/json", "Retry-After": "60" }); return res.end(JSON.stringify({ error: "Too many new accounts from this network — try again later" })); }
      if (/^\/api\/(auth|platform)\/login/.test(url.pathname) && !authLimiter(clientIp + ":auth")) { res.writeHead(429, { "Content-Type": "application/json", "Retry-After": "30" }); return res.end(JSON.stringify({ error: "Too many authentication attempts — slow down" })); }
      if (req.method === "POST" && /^\/api\/(auth\/(password|mfa|email|sso)|platform\/mfa)/.test(url.pathname) && !authLimiter(clientIp + ":prove")) { res.writeHead(429, { "Content-Type": "application/json", "Retry-After": "30" }); return res.end(JSON.stringify({ error: "Too many authentication attempts — slow down" })); }
      const origin = req.headers.origin || req.headers.referer;
      if (["POST", "PUT", "DELETE"].includes(req.method) && origin) {
        let oh; try { oh = new URL(origin).host; } catch (e) { oh = ""; }
        if (oh && oh !== req.headers.host) { res.writeHead(403, { "Content-Type": "application/json" }); return res.end(JSON.stringify({ error: "Cross-origin mutation rejected" })); }
      }
      const session = getSession(req, res, url, cookies);
      if (url.searchParams.get("store") && SLUG_RE.test(url.searchParams.get("store"))) {
        const cur = res.getHeader("Set-Cookie");
        const arr = cur ? (Array.isArray(cur) ? cur : [cur]) : [];
        arr.push(`store=${url.searchParams.get("store")}; Path=/; Max-Age=${365 * DAY}; SameSite=Lax${sec.httpsRequest(req) ? "; Secure" : ""}`);
        res.setHeader("Set-Cookie", arr);
      }
      if (!session) return api.bad(res, "No store configured", 500);
      res.__tenantId = session.tenant.id;
      if (!sec.checkTenant(session.tenant.id)) { res.writeHead(429, { "Content-Type": "application/json", "Retry-After": "5" }); return res.end(JSON.stringify({ error: "Rate limit exceeded for your store" })); }
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
      res.appendHeader("Set-Cookie", `azc=${session.csrf}; Path=/; SameSite=Lax; Max-Age=2592000${sec.httpsRequest(req) ? "; Secure" : ""}`);
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
    /* crawlers: robots.txt keeps them out of the API, the consoles and the private shopper
       pages, and points at the store's sitemap. Every store has a basic sitemap, free (owner
       decision, 2026-11-21): search engines must be able to find its products. The SEO
       module keeps its tools — the sitemap settings, generation and /api/seo/sitemap.xml. */
    if (url.pathname === "/robots.txt" || url.pathname === "/sitemap.xml") {
      const t = resolveTenant(req, url, cookies);
      if (url.pathname === "/sitemap.xml") {
        if (!t) { res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" }); return res.end("Not found"); }
        const sm = require("./lib/sitemap.js");
        res.writeHead(200, { "Content-Type": "application/xml; charset=utf-8", "Cache-Control": "public, max-age=3600" });
        return res.end(sm.generateXML(sm.buildSitemapEntries(t.id)));
      }
      const host = String(req.headers.host || "").replace(/[^A-Za-z0-9.:[\]-]/g, "");
      const lines = ["User-agent: *", "Allow: /",
        ...["/api/", "/console.html", "/admin.html", "/platform.html", "/registry.html", "/session.html", "/cart.html", "/checkout.html", "/orders.html", "/messages.html", "/reset.html"].map(p => "Disallow: " + p)];
      if (t && host) lines.push("", "Sitemap: " + (sec.httpsRequest(req) ? "https" : "http") + "://" + host + "/sitemap.xml");
      res.writeHead(200, { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "public, max-age=3600" });
      return res.end(lines.join("\n") + "\n");
    }
    /* asked by the TLS proxy before it requests a certificate: only for an address that is ours */
    if (url.pathname === "/tls-allowed") {
      const d = String(url.searchParams.get("domain") || ""), m = masterTenant();
      const SD = require("./lib/store-domains.js");
      res.writeHead(d && (SD.storeFor(d) || (m && SD.clean(m.domain) === SD.clean(d))) ? 200 : 404, { "Cache-Control": "no-store" });
      return res.end();
    }
    /* the store as an app a phone or desktop can install */
    if (url.pathname === "/manifest.webmanifest") {
      const t = resolveTenant(req, url, cookies);
      if (!t) { res.writeHead(404); return res.end(); }
      return send(req, res, { "Content-Type": MIME[".webmanifest"], "Cache-Control": "public, max-age=3600" }, Buffer.from(JSON.stringify(require("./lib/page-meta.js").manifest(t))), null);
    }
    /* readiness, for a load balancer or orchestrator: 200 only while this process can serve —
       the database answers, the master deployment exists and no shutdown has begun (a draining
       instance answers 503 so traffic moves away before it closes). /healthz is liveness only. */
    if (url.pathname === "/readyz") {
      let ready = !shuttingDown, why = shuttingDown ? "shutting down" : null;
      if (ready) { try { get("SELECT 1 x"); if (!masterTenant()) { ready = false; why = "no master deployment"; } } catch (e) { ready = false; why = "database unavailable"; } }
      res.writeHead(ready ? 200 : 503, { "Content-Type": "application/json", "Cache-Control": "no-store" });
      return res.end(JSON.stringify(ready ? { ready: true } : { ready: false, reason: why }));
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
        || (() => { const ps = cookies.azp && get("SELECT admin_id, mfa_at FROM platform_sessions WHERE ptid=? AND expires_at > datetime('now')", cookies.azp); return !!ps && mfa.state("platform", ps.admin_id, ps.mfa_at) === "ok"; })();
      if (!authed) { res.writeHead(401, { "Content-Type": "text/plain", "WWW-Authenticate": 'Bearer realm="luxora-metrics"' }); return res.end("Unauthorized"); }
      const body = require("./lib/enterprise.js").promMetrics(metrics.snapshot(null));
      res.writeHead(200, { "Content-Type": "text/plain; version=0.0.4" });
      return res.end(body);
    }
    /* the unified console's bundles, wrapped server-side (lib/bundle.js) so the browser
       never has to eval fetched source */
    const pm = /^\/js\/plain\/(store|platform)\.js$/.exec(url.pathname);
    if (pm) {
      return send(req, res, { "Content-Type": "application/javascript; charset=utf-8", "Cache-Control": "no-cache" }, Buffer.from(require("./lib/bundle.js").plain(pm[1], PUB) || ""), null);
    }
    const bm = /^\/js\/bundle\/(store|platform)\.js$/.exec(url.pathname);
    if (bm) {
      return send(req, res, { "Content-Type": "application/javascript; charset=utf-8", "Cache-Control": "no-cache" }, Buffer.from(require("./lib/bundle.js").wrap(bm[1], PUB) || ""), null);
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
    if (url.searchParams.get("store") && SLUG_RE.test(url.searchParams.get("store"))) res.appendHeader("Set-Cookie", `store=${url.searchParams.get("store")}; Path=/; Max-Age=${365 * DAY}; SameSite=Lax${sec.httpsRequest(req) ? "; Secure" : ""}`);
    serveStatic(req, res, url.pathname, url);
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
  const seededDefault = (row, password, context) => {
    if (!row || !row.salt || !row.hash) return true;
    try {
      const ver = row.kdf_version || "v1";
      return sec.kdfVerify(password, row.salt, row.hash, ver, ver === "v1" ? "" : context);
    } catch (e) { return true; }
  };
  const platformEmail = String(process.env.PLATFORM_EMAIL || "platform@luxora.shop").toLowerCase();
  const adminEmail = String(process.env.ADMIN_EMAIL || "admin@luxora.shop").toLowerCase();
  const platform = get("SELECT * FROM platform_admins WHERE email=?", platformEmail);
  const master = masterTenant();
  const admin = master && get("SELECT * FROM users WHERE tenant_id=? AND email=?", master.id, adminEmail);
  if (seededDefault(platform, "platform123", "pa:" + platformEmail)) weak.push(["PLATFORM_PASSWORD", platformEmail, "platform123"]);
  if (seededDefault(admin, "admin123", adminEmail)) weak.push(["ADMIN_PASSWORD", adminEmail, "admin123"]);
  if (!weak.length) return;
  console.error("\n" + "=".repeat(78));
  console.error("REFUSING TO START IN PRODUCTION WITH SEED-DEFAULT CREDENTIALS");
  console.error("=".repeat(78));
  for (const [env, email, pw] of weak)
    console.error(`  ${email} still boots with the documented default "${pw}".`);
  console.error("  Set the environment variables and restart:");
  for (const [env] of weak) console.error(`    ${env}=<a strong password>`);
  console.error("  (rotate the stored passwords in Platform → Administration and Store → Team;\n"
    + "   setting an environment variable alone does not change an existing account.)");
  console.error("=".repeat(78) + "\n");
  process.exit(1);
}
prodCredentialGuard();
/* sign-in codes, magic links and password resets reach a signed-out person only by email/SMS:
   with no platform transport, any store that hasn't set its own can't recover an account */
if (process.env.NODE_ENV === "production" && !require("./lib/mailer.js").transportFor(0, "email"))
  console.warn("  ⚠️  No email sender on the platform's own store (Store console → Payments → Email & SMS senders) — password resets and sign-in codes are only delivered for stores with their own live sender.");

let shuttingDown = false;
/* stop taking connections, let what is under way finish, then go (a container is given 30 s) */
const DRAIN_MS = Number(process.env.LX_DRAIN_MS) || 20000;
function shutdown(sig) {
  if (shuttingDown) return; shuttingDown = true;
  console.log(`\n${sig} — closing`); sec.persistState();
  listenServer.close(() => process.exit(0));
  if (listenServer.closeIdleConnections) listenServer.closeIdleConnections();
  setTimeout(() => process.exit(0), DRAIN_MS).unref();
}
/* a stray rejected promise in an async handler must not take the process down (Node
   >= 15 exits on unhandled rejections); log it with enough context to fix the source */
/* expired idempotency keys are swept hourly (they were only ever deleted lazily on lookup) */
setInterval(() => { try { idem.purge(); } catch (e) { } }, 3600 * 1000).unref();
/* what has expired is cleared, and proven store addresses are looked up again */
setInterval(() => {
  try { require("./lib/session-sweep.js").sweep(); } catch (e) { console.error("session sweep:", e.message); }
  try { require("./lib/ops-alerts.js").checkBackups(); } catch (e) { }
  require("./lib/store-domains.js").recheck().catch(e => console.error("domain check:", e.message));
}, 3600 * 1000).unref();
/* live payments whose webhook never came are looked up with their gateway on a cadence */
require("./lib/api.js").startPaymentSweep();
/* shoppers' alerts are re-checked (prices also move by imports and rules, not only edits) and
   pickup parcels past their holding time expire, on the platform policy's cadence */
(function shopperSweep() {
  const mins = Number(sec.policy().shopperSweepMinutes);
  const t = setTimeout(() => {
    /* each engine with a clock: alerts re-checked, pickup parcels and booking holds expired,
       offers expired, auctions opened and closed, group buys settled, sellers' proceeds released */
    if (mins > 0) for (const m of ["alerts", "pickup", "bookings", "negotiation", "auctions", "groupbuy", "listings", "trials", "options", "wallet", "giftcards"]) { try { require("./lib/" + m + ".js").sweepAll(); } catch (e) { } }
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
  ██╗     ██╗   ██╗██╗  ██╗ ██████╗ ██████╗  █████╗
  ██║     ██║   ██║╚██╗██╔╝██╔═══██╗██╔══██╗██╔══██╗
  ██║     ██║   ██║ ╚███╔╝ ██║   ██║██████╔╝███████║
  ██║     ██║   ██║ ██╔██╗ ██║   ██║██╔══██╗██╔══██║
  ███████╗╚██████╔╝██╔╝ ██╗╚██████╔╝██║  ██║██║  ██║
  ╚══════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
   P L A T F O R M  ·  the master global platform, configured into any platform  ·  🛡 10-layer security${IS_TLS ? " (TLS ON)" : " (HTTP — set LUX_TLS=1 for HTTPS)"}

   🏬 Master:      http${IS_TLS ? "s" : ""}://${(master || { slug: "luxora" }).slug}.localhost:${PORT} (the master's own deployment${fixtures.length ? `, +${fixtures.length} fixture${fixtures.length > 1 ? "s" : ""}` : ""})
   🌐 Console:    http${IS_TLS ? "s" : ""}://localhost:${PORT}/console.html    (${process.env.NODE_ENV === "production" ? "credentials configured by the deployment" : "platform@luxora.shop / platform123 · store admin admin@luxora.shop / admin123"})
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
