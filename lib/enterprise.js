/* LUXORA Platform — enterprise ops layer (everything OFF-by-default, all config/placeholders).
   This module wires the seven "production" capabilities as pure DATA + endpoints. Nothing is enabled
   unless you write its platform_settings row (or env), so SQLite/single-node installs are unaffected:

     1. db cutover       — dual-engine status + apply/verify + a safe switch (config db=postgres)
     2. PSP validation   — per-gateway "would-call" preview + verified inbound webhooks (mock/sandbox)
     3. SSO/SAML + SCIM  — per-store SSO connection + a token-scoped SCIM 2.0 endpoint for staff sync
     4. multi-region     — region/edge/CDN config; asset URLs rebase to the CDN when set
     5. observability     — Prometheus /metrics from metrics + DB gauges; health; JSON logs
     6. domain depth     — product feeds (Google/Meta Shopping), warehouse transfers, tax remittance
     7. (CI is a repo file, not code here)

   External requirements are "fill-in-the-blank": URLs, keys, secrets, IdP metadata, endpoints,
   regions — all stored as data (platform_settings / provider specs / per-store connection rows),
   never hard-coded. Placeholder values ship disabled so nothing silently activates. */
"use strict";

const crypto = require("crypto");
let _db = null, _pg = null, _cfg = null, _migrate = null, _events = null, _rbac = null;
const db = () => _db || (_db = require("./db.js"));
const pg = () => _pg || (_pg = require("./pg.js"));
const cfg = () => _cfg || (_cfg = require("./config.js"));
const migrate = () => _migrate || (_migrate = require("./migrate.js"));
const events = () => _events || (_events = require("./events.js"));
const rbac = () => _rbac || (_rbac = require("./rbac.js"));
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };
const platGet = (k, d) => { try { const r = db().get("SELECT value FROM platform_settings WHERE key=?", k); return r ? J(r.value, d) : d; } catch (e) { return d; } };
const platSet = (k, v) => db().run("INSERT INTO platform_settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", k, JSON.stringify(v));

/* =========== 1 · DB CUTOVER =========== */
function dbStatus() {
  const c = cfg(); const driver = c.driverOf("db"); const pgs = c.get("db").params || {};
  const pgUrl = pgs.url || process.env.LX_PG_URL || "";
  const m = platGet("db_mode", { mode: "sqlite", lastVerify: null, lastApply: null });
  /* Never return the connection string itself: it carries the DB password, and the config
     schema already classifies this exact value as secret. Report the connectable parts only. */
  /* H7: the REQUESTED driver (config) is not the driver this process is actually using — the
     bridge is selected once at boot from env (lib/db.js). Reporting the requested one as if it
     were live let an operator believe a cutover happened while the process still reads/writes
     SQLite. Report both, and whether a restart is needed to apply the change. */
  const effective = require("./db.js").USE_PG ? "postgres" : "sqlite";
  return {
    enabled: !!pgUrl || driver === "postgres", driver, effectiveDriver: effective,
    restartRequired: driver !== effective,
    pgHost: (() => { try { return pgUrl ? new URL(pgUrl).hostname : null; } catch (e) { return null; } })(),
    pgDatabase: (() => { try { const u = new URL(pgUrl); return (u.pathname || "/").replace(/^\//, "") || null; } catch (e) { return null; } })(),
    pgConfigured: !!pgUrl, mode: m.mode, lastApply: m.lastApply, lastVerify: m.lastVerify
  };
}
async function dbPing() { if (!dbStatus().pgConfigured) return { ok: false, error: "postgres not configured (set Platform → Runtime → db=postgres + connection string)" }; const r = await pg().query({ connectionString: (cfg().get("db").params || {}).url || process.env.LX_PG_URL || "", host: "127.0.0.1" }, "SELECT 1"); return { ok: !!(r && r.ok), error: r && r.error }; }
async function dbApply(dryRun) {
  const st = dbStatus(); if (!st.pgConfigured) return { ok: false, error: "postgres not configured" };
  const plan = migrate().plan(); const url = (cfg().get("db").params || {}).url || process.env.LX_PG_URL;
  if (dryRun) return { ok: true, dryRun: true, statements: plan.length, ddl: plan.filter(s => s.kind === "ddl").length, data: plan.filter(s => s.kind === "data").length };
  const r = await migrate().apply(plan, { connectionString: url });
  /* `r.ok` is a statement COUNT, not a boolean — Object.assign below would let a numeric
     truthy ok read as success even when hundreds of statements failed. Report a real boolean
     and only mark the cutover done when nothing failed. */
  const failed = r.failed || [];
  const out = { ok: failed.length === 0, applied: r.ok, failed };
  platSet("db_mode", Object.assign(platGet("db_mode", {}), { mode: failed.length === 0 ? "migrated" : "partial", lastApply: new Date().toISOString() }));
  return out;
}
function dbSwitch(driver, mode) {
  const c = cfg();
  if (driver && !c.RUNTIME_CATALOG.db.drivers.includes(driver)) return { ok: false, error: "unknown driver" };
  c.saveRuntime({ db: { driver, params: c.get("db").params } });
  /* H7: writing the config does NOT move the live connection — the bridge is chosen at boot
   * (lib/db.js reads env once). Say so plainly so an operator doesn't read "switched" as "live". */
  const effective = require("./db.js").USE_PG ? "postgres" : "sqlite";
  platSet("db_mode", Object.assign(platGet("db_mode", {}), { mode: mode || "sqlite", lastSwitch: new Date().toISOString() }));
  return { ok: true, mode: mode || driver, requested: driver, effectiveDriver: effective, restartRequired: driver !== effective };
}

/* =========== 2 · PSP GATEWAY VALIDATION + INBOUND WEBHOOKS =========== */
/* The gateway config read here is the SESSION's tenant's own row — never a hardcoded store.
   A platform-wide preview would paint one tenant's gateway credentials into another store's
   console, which is exactly the L10 isolation the tenancy model exists to prevent. Missing
   config is fine: the preview shows the would-call shape with placeholder credentials. */
function gatewayPreview(providerId, tenantId, gw) {
  const spec = gw && gw.spec ? (typeof gw.spec === "string" ? J(gw.spec, {}) : gw.spec) : (db().get("SELECT spec FROM provider_defs WHERE id=? AND kind='payment'", providerId) || {}).spec;
  const s = typeof spec === "string" ? J(spec, null) : spec;
  if (!s || !s.url) return { ok: false, error: "no spec" };
  const row = tenantId ? db().get("SELECT config FROM tenant_gateways WHERE tenant_id=? AND provider_id=?", tenantId, providerId) : null;
  const params = row ? J(row.config, {}) : {};
  /* a merchant may override the provider's default endpoint from its own gateway config
     (a sandbox/region URL); the preview then shows the call THIS store would actually make */
  const base = params.url || params.endpoint || s.url;
  const url = base.replace(/\{\{([^}]+)\}\}/g, (_, k) => "{" + k + "}"); // template tokens preserved as placeholders
  return { ok: true, provider: providerId, method: s.method || "POST", url, headers: (s.auth && s.auth.type) ? { [s.auth.header || "Authorization"]: "‹" + s.auth.type + " credentials›" } : {}, body: s.body || {} };
}
/* inbound provider notification → verify HMAC + persist */
function inboundWebhook(provider, rawBody, signature) {
  const rec = platGet("inbound_webhook", { provider: "stripe", secret: "", header: "stripe-signature" }) || {};
  const cfgSecret = (rec && typeof rec[provider] === "object" && rec[provider].secret) || (provider === rec.provider ? rec.secret : "");
  const sec = cfgSecret || rec.secret || "";
  const sigOk = sec ? events().verify(sec, rawBody, signature) : false;
  try { db().run("INSERT INTO webhook_deliveries(tenant_id,webhook_id,event,subject_uid,payload,status,attempts,created_at) VALUES(?,?,?,?,?,?,?,datetime('now'))", 0, 0, provider + ".inbound", null, rawBody.slice(0, 4000), sigOk ? "ok" : "failed", 0); } catch (e) { }
  try { db().run("INSERT INTO inbound_events(tenant_id,provider,event,payload,signature_ok,created_at) VALUES(?,?,?,?,?,datetime('now'))", 0, provider, rawBody.slice(0, 4000), sigOk ? 1 : 0); } catch (e) { }
  return { ok: true, signatureOk: sigOk };
}

/* =========== 3 · SSO / SAML + SCIM =========== */
function ssoConnection(tenantId) { const r = db().get("SELECT * FROM sso_connections WHERE tenant_id=?", tenantId); if (!r) return null; return { enabled: !!r.enabled, provider: r.provider, entityId: r.entity_id, ssoUrl: r.sso_url, certPresent: !!r.cert, domains: J(r.domains, []), mode: r.mode || "saml", issuer: r.issuer, clientId: r.client_id, redirectUri: r.redirect_uri, scope: r.scope, autoProvision: !!r.auto_provision, defaultRole: r.default_role }; }
function ssoFull(tenantId) { return db().get("SELECT * FROM sso_connections WHERE tenant_id=?", tenantId); }
function setSso(tenantId, b) { db().run(`INSERT INTO sso_connections(tenant_id,provider,entity_id,sso_url,cert,enabled,domains,mode,issuer,client_id,client_secret,redirect_uri,scope,auto_provision,default_role)
   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(tenant_id) DO UPDATE SET provider=excluded.provider, entity_id=excluded.entity_id, sso_url=excluded.sso_url, cert=excluded.cert, enabled=excluded.enabled, domains=excluded.domains, mode=excluded.mode, issuer=excluded.issuer, client_id=excluded.client_id, client_secret=excluded.client_secret, redirect_uri=excluded.redirect_uri, scope=excluded.scope, auto_provision=excluded.auto_provision, default_role=excluded.default_role, updated_at=datetime('now')`,
    tenantId, b.provider || "okta", b.entityId || "", b.ssoUrl || "", b.cert || "", b.enabled ? 1 : 0, JSON.stringify(b.domains || []), b.mode || "saml", b.issuer || "", b.clientId || "", b.clientSecret || "", b.redirectUri || "", b.scope || "openid email profile", b.autoProvision ? 1 : 0, b.defaultRole || "manager"); return { ok: true }; }
function ssoStart(tenantId, email) {
  const c = ssoConnection(tenantId); if (!c || !c.enabled || !(c.issuer || c.ssoUrl)) return { ok: false, error: "SSO not enabled for this store" };
  const dom = (email || "").split("@")[1] || ""; if (c.domains.length && !c.domains.includes(dom)) return { ok: false, error: "Email domain not SSO-enabled" };
  const state = crypto.randomBytes(8).toString("hex"), nonce = crypto.randomBytes(8).toString("hex");
  try { db().run("INSERT INTO sso_states(state,tenant_id,nonce) VALUES(?,?,?)", state, tenantId, nonce); } catch (e) { }
  if (c.mode === "oidc" && c.issuer && c.clientId) {
    const u = c.issuer.replace(/\/$/, "") + "/authorize?response_type=code&client_id=" + encodeURIComponent(c.clientId) + "&redirect_uri=" + encodeURIComponent(c.redirectUri || "") + "&scope=" + encodeURIComponent(c.scope || "openid email") + "&state=" + state + "&nonce=" + nonce;
    return { ok: true, mode: "oidc", redirectUrl: u, state };
  }
  return { ok: true, mode: "saml", redirectUrl: (c.ssoUrl || "") + "?SAMLRequest=‹encoded›&RelayState=" + state, relayState: state };
}
function _b64u(s) { return Buffer.from(String(s).replace(/-/g, "+").replace(/_/g, "/"), "base64").toString("utf8"); }
/* REAL id_token validation (RS256 public-key PEM / JWK, or HS256 shared secret). */
function verifyIdToken(idToken, opts) {
  opts = opts || {};
  try {
    const [h, p, s] = String(idToken || "").split("."); if (!h || !p || !s) return { ok: false, error: "malformed token" };
    const header = J(_b64u(h), null), claims = J(_b64u(p), null); if (!header || !claims) return { ok: false, error: "bad json" };
    const input = h + "." + p, sig = Buffer.from(s.replace(/-/g, "+").replace(/_/g, "/"), "base64");
    let valid = false;
    if (header.alg === "HS256") { if (!opts.secret) return { ok: false, error: "no secret" }; const exp = crypto.createHmac("sha256", opts.secret).update(input).digest(); valid = exp.length === sig.length && crypto.timingSafeEqual(exp, sig); }
    else if (header.alg === "RS256") { if (!opts.publicKey) return { ok: false, error: "no public key" }; const v = crypto.createVerify("RSA-SHA256"); v.update(input); try { valid = v.verify(opts.publicKey, sig); } catch (e) { return { ok: false, error: "key error" }; } }
    else return { ok: false, error: "alg " + header.alg + " unsupported" };
    if (!valid) return { ok: false, error: "signature invalid" };
    const now = Math.floor(Date.now() / 1000);
    if (claims.exp && claims.exp < now) return { ok: false, error: "token expired" };
    if (opts.iss && claims.iss !== opts.iss) return { ok: false, error: "issuer mismatch" };
    if (opts.aud && claims.aud !== opts.aud) return { ok: false, error: "audience mismatch" };
    if (opts.nonce && claims.nonce && claims.nonce !== opts.nonce) return { ok: false, error: "nonce mismatch" };
    return { ok: true, claims };
  } catch (e) { return { ok: false, error: e.message }; }
}
/* complete SSO: validate id_token, then resolve/provision the store-admin user */
function oidcComplete(tenantId, idToken, state) {
  const c = ssoFull(tenantId); if (!c || !c.enabled) return { ok: false, error: "SSO disabled" };
  const st = state ? db().get("SELECT nonce FROM sso_states WHERE state=?", state) : null;
  const v = verifyIdToken(idToken, { publicKey: c.cert || "", secret: c.client_secret || "", iss: c.issuer, aud: c.client_id, nonce: st && st.nonce });
  if (!v.ok) return { ok: false, error: v.error };
  const email = String(v.claims.email || v.claims.preferred_username || v.claims.sub || "").toLowerCase(); if (!email) return { ok: false, error: "no subject/email" };
  const domains = J(c.domains, []); if (domains.length && !domains.includes(email.split("@")[1])) return { ok: false, error: "Email domain not SSO-enabled" };
  let u = db().get("SELECT id,disabled FROM users WHERE tenant_id=? AND email=?", tenantId, email);
  if (!u && c.auto_provision) { const id = db().newUser(tenantId, email, email, crypto.randomBytes(12).toString("hex"), "admin"); db().run("UPDATE users SET staff_role=? WHERE id=?", c.default_role || "manager", id); u = { id, disabled: 0 }; }
  if (!u) return { ok: false, error: "No account — enable SCIM or auto-provision" };
  if (u.disabled) return { ok: false, error: "account disabled" };
  return { ok: true, userId: u.id, email };
}
/* SCIM token (per tenant, hashed at rest) */
function scimTokens(tenantId) { return db().all("SELECT id, label, prefix, created_at FROM scim_tokens WHERE tenant_id=? ORDER BY id DESC", tenantId); }
function createScim(tenantId, label) { const token = "sc_" + crypto.randomBytes(20).toString("hex"); const h = crypto.createHash("sha256").update(token).digest("hex"); const r = db().run("INSERT INTO scim_tokens(tenant_id,token_hash,label,prefix) VALUES(?,?,?,?)", tenantId, h, String(label || "default"), token.slice(0, 10)); return { id: Number(r.lastInsertRowid), token }; }
function scimAuth(tenantId, bearer) { if (!bearer) return false; const h = crypto.createHash("sha256").update(String(bearer)).digest("hex"); return !!db().get("SELECT id FROM scim_tokens WHERE tenant_id=? AND token_hash=?", tenantId, h); }
/* SCIM users resource backed by our staff users + RBAC */
async function scimList(tenantId) { const staff = db().all("SELECT id,name,email,staff_role,disabled FROM users WHERE tenant_id=? AND role='admin'", tenantId); return { Resources: staff.map(u => ({ schemas: ["urn:ietf:params:scim:schemas:core:2.0:User"], id: String(u.id), userName: u.email, name: { givenName: u.name }, active: !u.disabled, roles: [{ value: u.staff_role || "owner" }] })), totalResults: staff.length }; }
async function scimCreate(tenantId, u) { const rb = rbac(); const email = String(u.userName || "").toLowerCase(); const role = (u.roles && u.roles[0] && u.roles[0].value) || "manager"; if (!email) return { error: "userName required" }; const existing = db().get("SELECT id FROM users WHERE tenant_id=? AND email=?", tenantId, email);
  if (existing) { db().run("UPDATE users SET staff_role=?, disabled=0 WHERE id=?", role, existing.id); return { id: existing.id, existed: true }; }
  const pw = "SCIM!" + crypto.randomBytes(6).toString("hex");
  const id = db().newUser(tenantId, (u.name && u.name.givenName) || email, email, pw, "admin");
  db().run("UPDATE users SET staff_role=? WHERE id=?", role, id); return { id: Number(id), password: pw }; }

/* =========== 4 · MULTI-REGION + EDGE/CDN =========== */
function regionConfig() { return platGet("regions", { list: [{ key: "global", label: "Global (default)" }, { key: "eu-west", label: "EU West" }, { key: "us-east", label: "US East" }, { key: "ap-south", label: "Asia South" }], cdn: "" }); }
function setRegions(b) { platSet("regions", b); return { ok: true }; }
function tenantRegion(tenantId) { try { return (db().get("SELECT region FROM tenants WHERE id=?", tenantId) || {}).region || "global"; } catch (e) { return "global"; } }
function assetUrl(tenantId, path) { const reg = regionConfig(); const cdn = reg.cdn || ""; if (!cdn) return path; return String(cdn).replace(/\/$/, "") + "/" + String(path).replace(/^\//, ""); }

/* =========== 5 · OBSERVABILITY =========== */
function promMetrics(snap) {
  const t = snap.totals || {}; const out = [];
  out.push("# HELP luxora_http_requests_total Total HTTP requests"); out.push("# TYPE luxora_http_requests_total counter"); out.push("luxora_http_requests_total " + (t.req || 0));
  out.push("# HELP luxora_http_errors_total Total error responses"); out.push("# TYPE luxora_http_errors_total counter"); out.push("luxora_http_errors_total " + (t.err || 0));
  out.push("# HELP luxora_http_duration_ms_avg Average handler duration"); out.push("# TYPE luxora_http_duration_ms_avg gauge"); out.push("luxora_http_duration_ms_avg " + (t.avgMs || 0));
  (snap.series || []).slice(-3).forEach(s => { out.push("# HELP luxora_http_requests Recent per-minute requests"); out.push("# TYPE luxora_http_requests gauge"); out.push("luxora_http_requests{minute=\"" + s.t + "\"} " + (s.req || 0)); });
  (snap.endpoints || []).slice(0, 10).forEach(e => { out.push("luxora_http_endpoint_requests{endpoint=\"" + e.endpoint + "\"} " + e.count); });
  try { const g = db().get("SELECT COUNT(*) c, COALESCE(SUM(total),0) s FROM orders WHERE created_at > date('now','-1 day')"); out.push("# TYPE luxora_orders_24h gauge"); out.push("luxora_orders_24h " + g.c); out.push("luxora_revenue_24h " + Number(g.s).toFixed(2)); } catch (e) { }
  try { out.push(require("./ucos-monitor.js").promMetrics("luxora_ucos")); } catch (e) { }
  return out.join("\n") + "\n";
}
function healthz() { const d = dbStatus(); return { ok: true, driver: d.driver, pg: d.pgConfigured, mode: d.mode, tenants: db().get("SELECT COUNT(*) c FROM tenants").c, ts: new Date().toISOString() }; }

/* =========== 6 · DOMAIN DEPTH: feeds, transfers, remittance =========== */
function productFeed(tenantId, slug, fmt) {
  const rows = db().all("SELECT id,title,brand,dept,price,list_price,stock,keywords,media FROM products WHERE tenant_id=? AND lifecycle='published' AND deleted_at IS NULL ORDER BY position LIMIT 500", tenantId)
    .map(r => ({ ...r, media: J(r.media, []) }));
  const base = (platGet("feed_base_url", { baseUrl: "" }).baseUrl || ("https://" + slug + ".example")) .replace(/\/$/, "");
  if (fmt === "csv") return { type: "text/csv", body: ["id,title,brand,dept,price,availability,url"].concat(rows.map(r => [r.id, `"${r.title.replace(/"/g, '""')}"`, `"${r.brand}"`, r.dept, r.price, Number(r.stock) > 0 ? "in_stock" : "out_of_stock", `${base}/product.html?id=${encodeURIComponent(r.id)}`].join(","))).join("\n") };
  const xml = rows.map(r => `<item><g:id>${esc(r.id)}</g:id><title>${esc(r.title)}</title><description>${esc(r.keywords || r.title)}</description><g:price>${r.price} USD</g:price><link>${esc(base)}/product.html?id=${encodeURIComponent(r.id)}</link><g:availability>${Number(r.stock) > 0 ? "in stock" : "out of stock"}</g:availability><image:link>${esc((r.media[0] || {}).url || base + "/static.png")}</image:link></item>`).join("\n");
  return { type: "application/rss+xml", body: `<?xml version="1.0"?><rss version="2.0" xmlns:g="http://base.google.com/ns/1.0"><channel><title>${esc(slug)} feed</title><link>${esc(base)}</link>\n${xml}\n</channel></rss>` };
}
function stockTransfer(tenantId, b) {
  const from = Number(b.from_warehouse), to = Number(b.to_warehouse), qty = Number(b.qty) || 0, sku = Number(b.sku_id);
  if (!from || !to || from === to || qty <= 0) return { ok: false, error: "from/to warehouse and qty required" };
  const src = db().get("SELECT qty FROM inventory WHERE tenant_id=? AND warehouse_id=? AND sku_id=?", tenantId, from, sku); if (!src || src.qty < qty) return { ok: false, error: "insufficient stock" };
  db().run("UPDATE inventory SET qty=qty-? WHERE tenant_id=? AND warehouse_id=? AND sku_id=?", qty, tenantId, from, sku);
  const tgt = db().get("SELECT id FROM inventory WHERE tenant_id=? AND warehouse_id=? AND sku_id=?", tenantId, to, sku);
  if (tgt) db().run("UPDATE inventory SET qty=qty+? WHERE id=?", qty, tgt.id); else db().run("INSERT INTO inventory(tenant_id,sku_id,warehouse_id,qty,reserved) VALUES(?,?,?,?,0)", tenantId, sku, to, qty);
  const id = db().run("INSERT INTO stock_transfers(tenant_id,from_warehouse,to_warehouse,sku_id,qty,status,reference,note) VALUES(?,?,?,?,?,?,?,?)", tenantId, from, to, sku, qty, "completed", b.reference || "", b.note || "").lastInsertRowid;
  return { ok: true, id: Number(id) };
}
function taxReport(tenantId, period) { const p = period || new Date().toISOString().slice(0, 7); const r = db().get("SELECT COALESCE(SUM(tax),0) tax FROM orders WHERE tenant_id=? AND strftime('%Y-%m', created_at)=?", tenantId, p); const t = db().get("SELECT COALESCE(SUM(sub),0) sub FROM orders WHERE tenant_id=? AND strftime('%Y-%m', created_at)=?", tenantId, p); return { period: p, taxable: Number(t.sub || 0).toFixed(2), taxCollected: Number(r.tax || 0).toFixed(2), currency: "USD" }; }

function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }

module.exports = { dbStatus, dbPing, dbApply, dbSwitch, gatewayPreview, inboundWebhook, ssoConnection, ssoFull, setSso, ssoStart, verifyIdToken, oidcComplete, scimTokens, createScim, scimAuth, scimList, scimCreate, regionConfig, setRegions, tenantRegion, assetUrl, promMetrics, healthz, productFeed, stockTransfer, taxReport };
