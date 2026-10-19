/* LUXORA Platform - REST API: multi-tenant, pluggable providers, billing, audit, monitoring */
"use strict";

const crypto = require("crypto");
const { verifyUserAsync, verifyPlatformAdminAsync, newUserAsync, setUserPasswordAsync, passwordReusedAsync, run, get, all, newUser, verifyUser, newPlatformAdmin, verifyPlatformAdmin, hashPasswordFor, ownerFor, masterTenant, tenantState, setTenantState, audit, seedTenantCatalog, seedTenantDepartments, seedTenantBrands, seedTenantHome, seedMeta, seedTaxonomy, DB_PATH, USE_PG, DEPT_TO_INDUSTRY } = require("./db.js");
const settings = require("./settings.js");
const registry = require("./registry.js");
const mods = require("./modules.js");
const sec = require("./security.js");
const branding = require("./branding.js");
const policies = require("./policies.js");
const ai = require("./ai.js");
const offers = require("./offers.js");
const goip = require("./goip.js");
const connect = require("./connect.js");
const mailer = require("./mailer.js");
const rtconfig = require("./config.js");
const adapters = require("./adapters.js");
const env = require("./env.js");
const taxmod = require("./tax.js");
const billing = require("./billing.js");
const events = require("./events.js");
const governance = require("./governance.js");
const rbac = require("./rbac.js");
const prbac = require("./prbac.js");
const authz = require("./authz.js");
const dbpool = require("./dbpool.js");
const migrate = require("./migrate.js");
const enterprise = require("./enterprise.js");
const search = require("./search.js");
const logistics = require("./logistics.js");
const fin = require("./fin.js");
const marketplace = require("./marketplace.js");
const ugc = require("./ugc.js");
const helpdesk = require("./helpdesk.js");
const recurring = require("./recurring.js");
const risk = require("./risk.js");
const experiments = require("./experiments.js");
const planning = require("./planning.js");
const mobility = require("./mobility.js");
const operations = require("./operations.js");
const globalmod = require("./global.js");
/* the commerce layer: quick-commerce, fintech rails, marketplace/seller
   and B2B trust/trade — every domain configured via lib/capabilities.js */
const qcommerce = require("./qcommerce.js");
const fintech = require("./fintech.js");
const mkt = require("./marketplace-ext.js");
const trade = require("./trade.js");
const compliance = require("./compliance.js");
const tenancy = require("./tenancy.js");
const compose = require("./compose.js");
const ucos = require("./ucos.js");
const ucosMon = require("./ucos-monitor.js");
const ucosComp = require("./ucos-completeness.js");
const ucosFound = require("./ucos-foundations.js");
const ucosUniv = require("./ucos-universes.js");
const ucosCat = require("./ucos-catalog.js");
const { auditChainVerify, passwordReused, setUserPassword } = require("./db.js");
const fs = require("fs");
const zlib = require("zlib");

function json(res, code, obj) {
  res.writeHead(code, { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" });
  res.end(JSON.stringify(obj));
}
function bad(res, msg, code) { json(res, code || 400, { error: msg }); }

const CFG = s => settings.forBuyer(s.tenant.id);
const T = s => s.tenant.id;
/* a disabled staff account is not an administrator — the flag used to be ignored here, so a
   removed employee kept full access through the session they already held */
function isAdmin(s) {
  if (!s.user_id) return false;
  const u = get("SELECT role, disabled FROM users WHERE id=? AND tenant_id=?", s.user_id, T(s));
  return !!(u && u.role === "admin" && !u.disabled);
}
/* ---------- store RBAC on every store-admin route ----------
   requireAdmin used to admit EVERY staff role to every store write — a read-only "support"
   role could refund payments, delete customers and swap gateways. A store route now
   authorizes against the section it belongs to, with the staff member's role resolved from
   the store's role set (declared sections + per-user overrides). Fitness (which features the
   store has lit) narrows the console, not authorization, so an owner is never locked out of
   an unlit section. Unmapped writes fail closed to "settings". */
const STORE_ROUTE_SECTION = {
  qc: "qcops", fintech: "finops", wallet: "finops", "admin/fin": "finops",
  marketplace: "marketplace", "admin/marketplace": "marketplace", trade: "tradeops",
  themes: "settings", capabilities: "modules", modules: "modules", dashboards: "analytics", reports: "analytics",
  "admin/stats": "analytics", "admin/analytics": "analytics",
  "admin/trash": "trash", "admin/retention": "retention", "admin/recurring": "retention", "admin/memberships": "retention",
  "admin/roles": "team", "admin/staff": "team", "admin/users": "team", "admin/scim": "team",
  tenant: "settings", tenancy: "tenancy", ucii: "studio", ucos: "studio", "admin/export": "studio", "admin/entity-meta": "studio",
  shipments: "logistics", "admin/shipments": "logistics", "admin/warehouses": "logistics",
  "admin/sla": "helpdesk", "admin/helpdesk": "helpdesk", helpdesk: "helpdesk",
  "admin/returns": "returns", reviews: "ugc", "admin/reviews": "ugc", "admin/ugc": "ugc", qna: "ugc", "admin/qna": "ugc",
  "admin/risk": "risk", "admin/experiments": "experiments", "admin/planning": "planning",
  "admin/operations": "planning", "admin/ops": "planning", "admin/mobility": "rides",
  "admin/products": "products", "admin/attributes": "products", "admin/relationships": "products",
  "admin/taxonomy": "taxonomy", "admin/skus": "skus", "admin/inventory": "skus", "admin/transfers": "skus",
  "admin/serialized": "serialized",
  "admin/promotions": "offers", offers: "offers", goip: "offers", marketing: "offers",
  "admin/sellers": "sellers", "admin/rfqs": "rfqs", "admin/settlements": "settlements",
  "admin/contracts": "contracts", "admin/tenders": "tenders", "admin/tax": "finance",
  "admin/orders": "orders", "admin/compliance": "compliance", "admin/privacy": "privacy",
  "admin/gateways": "payments", "admin/gateway": "payments", "admin/payments": "payments",
  "admin/ai-gateways": "ai", ai: "ai", "admin/billing": "billing", billing: "billing",
  "admin/audit": "audit", "admin/chain": "audit", "admin/monitor": "monitor", "admin/entity-usage": "monitor",
  "admin/mode": "settings", "admin/settings": "settings", "admin/departments": "settings", "admin/banners": "content",
  "admin/cards": "content", "admin/custom-providers": "settings", "admin/sso": "settings",
  "admin/identity-provider-types": "settings", "admin/identity-providers": "settings", "admin/identity-settings": "settings",
  env: "settings", affiliate: "affiliate", sitemap: "sitemap", shipping: "shipping", "admin/webhooks": "webhooks"
};
/* routes every staff member may use on their OWN account */
const STORE_ROUTE_SELF = new Set(["admin/account"]);
function storeRouteSection(pathname) {
  const p = String(pathname || "").replace(/^\/api\//, "");
  const parts = p.split("/");
  const two = parts.slice(0, 2).join("/");
  if (STORE_ROUTE_SELF.has(two)) return null;
  return STORE_ROUTE_SECTION[two] || STORE_ROUTE_SECTION[parts[0]] || undefined;
}
function staffGrant(s, section) {
  const u = get("SELECT staff_role, perms FROM users WHERE id=? AND tenant_id=?", s.user_id, T(s));
  if (!u) return null;
  const r = authz.role("store", T(s), u.staff_role || "owner");
  const sec = authz.expandScope("store", r ? r.sections : { "*": "write" });
  let perms = {}; try { perms = JSON.parse(u.perms || "{}") || {}; } catch (e) { perms = {}; }
  for (const k of Object.keys(perms)) sec[k] = perms[k];
  return sec[section] || null;
}
function storeRoleAllows(s, res) {
  const r = s.__route;
  if (!r) return true;
  const write = r.method !== "GET" && r.method !== "HEAD";
  let section = storeRouteSection(r.pathname);
  if (section === null) return true;
  if (section === undefined) { if (!write) return true; section = "settings"; }
  const have = staffGrant(s, section);
  if (have && (!write || have === "write")) return true;
  bad(res, "Your role does not grant access to " + section + (write ? " (write)" : ""), 403);
  return false;
}
function requireAdmin(s, res) {
  if (!isAdmin(s)) { bad(res, "Store administrator access required", 403); return false; }
  return storeRoleAllows(s, res);
}
function _userRow(s) { return s.user_id ? get("SELECT id,role,staff_role,perms FROM users WHERE id=? AND tenant_id=?", s.user_id, T(s)) : null; }
/* a platform admin acting on a store's surface is authorized by THEIR platform role, never
   waved through: `if (s.platform_admin) return true` let a read-only auditor rewrite any
   store's sign-in providers and log in as its owner. Each store section maps to the platform
   section that governs it ("operate stores" = tenants; money routing = providers); a caller
   can name a stricter one (identity writes use the platform "identity" section). */
const STORE_TO_PLATFORM_SECTION = { payments: "providers" };
function requireSection(s, res, section, mode, platformSection) {
  if (s.platform_admin) {
    const ps = platformSection || STORE_TO_PLATFORM_SECTION[section] || "tenants";
    if (prbac.can(s.platform_admin, ps, mode || "read")) return true;
    bad(res, "Your platform role does not grant access to " + ps + (mode === "write" ? " (write)" : ""), 403);
    return false;
  }
  if (!isAdmin(s)) { bad(res, "Store administrator access required", 403); return false; }
  /* the grant is resolved against THIS store's own role set (rbac.grant takes the
     tenant), so a store that re-scopes a role sees the re-scope the moment it is
     saved — never the shared default the platform ships */
  if (!rbac.can(_userRow(s), section, mode || "read", T(s))) { bad(res, "Your role does not grant access to " + section + (mode === "write" ? " (write)" : ""), 403); return false; }
  return true;
}
function requireStore(s, res) { if (!s || !s.tenant) { bad(res, "Store access required", 403); return false; } return true; }
/* every platform handler passes through here. A READ needs only a platform session; a
   WRITE is also authorized against the platform section its route belongs to (the same
   mapping the console nav advertises), so a restricted platform role cannot write through
   one of the many handlers that only ever asked "is this a platform admin?". */
function requirePlatform(s, res) {
  if (!s.platform_admin) { bad(res, "Platform access required", 403); return false; }
  const r = s.__route;
  if (r && r.method !== "GET" && r.method !== "HEAD") {
    const section = prbac.sectionForRoute(r.pathname, "write");
    if (!prbac.can(s.platform_admin, section, "write")) {
      bad(res, "Your platform role does not grant access to " + section + " (write)", 403);
      return false;
    }
  }
  return true;
}
/* store staff OR a platform admin. A platform admin READS any store (the console fans store
   reads out across deployments); a platform WRITE through a store route is authorized by the
   caller's platform role — the section the route belongs to (offers → goffers, fintech →
   gfinance, …), or "tenants" (operate stores) when the route is store-only. It used to accept
   any platform role, read-only auditors included, for every store write. */
function requireStaff(s, res, platformSection) {
  if (s.platform_admin) {
    const r = s.__route;
    if (!r || r.method === "GET" || r.method === "HEAD") return true;
    let ps = platformSection;
    if (!ps) { const mapped = prbac.sectionForRoute(r.pathname, "read"); ps = mapped === "dash" ? "tenants" : mapped; }
    if (prbac.can(s.platform_admin, ps, "write")) return true;
    bad(res, "Your platform role does not grant access to " + ps + " (write)", 403); return false;
  }
  if (isAdmin(s)) return storeRoleAllows(s, res);
  bad(res, "Store administrator access required", 403); return false;
}
/* the platform console's own RBAC. An admin's role + per-user perms resolve to a
   section grant; this is the gate every platform write (and gated read) passes
   through. Mirrors requireSection for stores, with the same error voice. */
function requirePlatformSection(s, res, section, mode) {
  /* an explicit section check is authoritative — it does not also pass the route mapping */
  if (!s.platform_admin) { bad(res, "Platform access required", 403); return false; }
  if (!prbac.can(s.platform_admin, section, mode || "read")) {
    bad(res, "Your platform role does not grant access to " + section + (mode === "write" ? " (write)" : ""), 403);
    return false;
  }
  return true;
}
/* authorize a routed platform request by mapping its path to a console section.
   The owner bypasses nothing here — the mapping is the same one the nav advertises,
   so an API call and its console button can never disagree. */
function requirePlatformRoute(s, res, url, mode) {
  const section = prbac.sectionForRoute(url.pathname, mode);
  if (!requirePlatformSection(s, res, section, mode)) return false;
  return true;
}
function actor(s) {
  if (s.platform_admin) return ["platform", s.platform_admin.id, s.platform_admin.email];
  if (s.user_id) { const u = get("SELECT name,email,role FROM users WHERE id=?", s.user_id); return [u && u.role === "admin" ? "admin" : "customer", s.user_id, u ? u.email : ""]; }
  return ["guest", null, s.sid];
}
function ipOf(req) { return (req && (req.__ip || (req.socket && req.socket.remoteAddress))) || ""; }
function logAction(s, action, entity, entityId, meta, req) {
  const [type, id, name] = actor(s);
  audit(T(s), type, id, name, action, entity, entityId, meta || {}, ipOf(req), (s && s.trace) || (req && req.__trace));
}
function emitEvent(tenantId, event, data, uid) { try { events.emit(tenantId, event, data, { uid }); } catch (e) { console.error("emit:", e.message); } }

/* ---------------- provider registry (built-in + custom manifests) ---------------- */
function customProviders(tenantId, kind) {
  const rows = all("SELECT manifest FROM custom_providers WHERE kind=? AND (scope='platform' OR (scope='tenant' AND tenant_id=?))", kind, tenantId);
  return rows.map(r => { try { return JSON.parse(r.manifest); } catch (e) { return null; } }).filter(Boolean);
}
function paymentRegistry(tenantId) { return [...customProviders(tenantId, "payment"), ...registry.providerDefs("payment")]; }
function commerceOf(s) {
  const c = CFG(s); const co = registry.country(c.commerce.country);
  const baseCur = registry.currency(co.currency) || { code: co.currency, symbol: co.symbol, decimals: co.decimals != null ? co.decimals : 2, usd: 1 };
  const want = c.commerce.currency ? registry.currency(c.commerce.currency) : null;
  const cur = want || baseCur;
  const fx = cur.code === baseCur.code ? 1 : registry.fxTo(baseCur.code, cur.code);
  /* a store that has not chosen its own tax inherits its JURISDICTION'S rule from the tax
     engine — not a column on the country master. Tax owns tax; the country owns geography.
     Reading co.tax_mode/co.tax_rate here would make the country row a second source of truth
     that silently drifts against taxRules the moment an operator edits one of them */
  const dflt = taxmod.defaultRateFor(co.code);
  return { ...c.commerce, country: co.code, currency: cur.code, symbol: cur.symbol, decimals: cur.decimals, fx, baseCurrency: baseCur.code, locale: c.commerce.locale || co.locale, taxMode: c.commerce.taxMode || dflt.mode, taxRate: (c.commerce.taxRate == null ? dflt.rate : c.commerce.taxRate) };
}
function money2(cm, n) { return n == null ? null : +(n * cm.fx).toFixed(cm.decimals); }
function storeView(p, cm) {
  const o = publicProduct(p);
  const pr = { ...o.pricing_rules };
  if (pr.tiers) pr.tiers = pr.tiers.map(t => ({ ...t, price: money2(cm, t.price) }));
  if (pr.bundle_price) pr.bundle_price = money2(cm, pr.bundle_price);
  return { ...o, p: money2(cm, o.p), l: o.l != null ? money2(cm, o.l) : null, pricing_rules: pr };
}
function enabledGateways(tenantId) {
  const reg = paymentRegistry(tenantId);
  return all("SELECT * FROM tenant_gateways WHERE tenant_id=? AND provider_id NOT LIKE 'ship:%' AND provider_id NOT LIKE 'notify:%' AND enabled=1 ORDER BY is_primary DESC, position", tenantId)
    .map(g => { const p = reg.find(x => x.id === g.provider_id); return p ? { ...p, mode: g.mode, is_primary: !!g.is_primary, configured: true } : null; })
    .filter(Boolean);
}
function enabledCarriers(tenantId) {
  return all("SELECT * FROM tenant_gateways WHERE tenant_id=? AND provider_id LIKE 'ship:%' AND enabled=1 ORDER BY is_primary DESC, position", tenantId)
    .map(g => { const id = g.provider_id.slice(5); const p = registry.providerDefs("shipping").find(x => x.id === id) || customProviders(tenantId, "shipping").find(x => x.id === id); return p ? { ...p, is_primary: !!g.is_primary } : null; })
    .filter(Boolean);
}
/* ---- the applicability rules at the points a choice is made (lib/rules.js) ----
   each choice is a named binding point; its registry row says what it decides and which
   facts it sets. The buyer's own facts (a country they state as context.country, their
   segments, channel…) come from the request; a rule's params override the engine's defaults
   through the subject type's declared parameter map. */
function ruleCtx(s, point, extra) { return rules.at(point, T(s), extra || {}); }
function permittedGateways(s, ctx) {
  /* the provider × country availability relation, then the rules */
  const list = enabledGateways(T(s)).filter(g => registry.supports(g.id, ctx.country));
  return rules.filterAt("checkout.gateways", list, ctx).map(({ it, d }) => {
    const g = rules.applyParams("checkout.gateways", it, d.params);
    g.methods = (it.methods || []).filter(m => rules.permitsAt("checkout.methods", m, ctx));
    g.rule = { verdict: d.verdict, priority: d.priority };
    /* a gateway whose every method a rule removed has nothing left to offer */
    return (it.methods || []).length && !g.methods.length ? null : g;
  }).filter(Boolean);
}
function permittedCarriers(s, ctx) {
  return rules.filterAt("checkout.carriers", enabledCarriers(T(s)), ctx).map(({ it, d }) => rules.applyParams("checkout.carriers", it, d.params));
}
function enabledNotifiers(tenantId) {
  return all("SELECT * FROM tenant_gateways WHERE tenant_id=? AND provider_id LIKE 'notify:%' AND enabled=1 ORDER BY position", tenantId)
    .map(g => { const id = g.provider_id.slice(7); const p = registry.providerDefs("notification").find(x => x.id === id) || customProviders(tenantId, "notification").find(x => x.id === id); return p || null; })
    .filter(Boolean);
}
function simulateGateway(gw, amount) {
  const ref = `${gw.id}_sim_${crypto.randomBytes(7).toString("hex")}`;
  const fee = +((amount * (gw.feePct || 0) / 100 + (gw.feeFixed || 0)).toFixed(2));
  /* a gateway whose methods are settled offline (the offlinePaymentMethods registry) is
     pending until the money is recorded; every other one captures */
  const offline = registry.list("offlinePaymentMethods").map(m => typeof m === "string" ? m : m.key);
  const pending = (gw.methods || []).some(m => offline.includes(m));
  return { ref, fee, status: states.first("payment", pending ? "held" : "settled") };
}
function gatewaySecrets(tenantId, providerId) {
  const row = get("SELECT mode, config FROM tenant_gateways WHERE tenant_id=? AND provider_id=?", tenantId, providerId);
  if (!row) return null;
  let cfg = {}; try { cfg = JSON.parse(row.config || "{}"); } catch (e) { }
  cfg = sec.unsealConfig(tenantId, providerId, JSON.stringify(cfg));
  return { mode: row.mode, cfg };
}
/* Settle a payment. Real gateway only when outbound mode ≠ offline and the store's gateway is
   `live` + has credentials; otherwise the simulated path (identical to before). Outbound mode
   is a Runtime config (auto|offline|live) — no code. */
function outboundOffline() { return rtconfig.driverOf("outbound") === "offline" || process.env.LX_OFFLINE === "1"; }
/* simulated settlement is a development/sandbox convenience: refused in production unless the
   operator opts in explicitly */
function simulatedSettlementAllowed() {
  return process.env.NODE_ENV !== "production" || process.env.LX_ALLOW_SIMULATED_PAYMENTS === "1";
}
async function settlePayment(tenantId, gw, amount, currency, idempotency, extra) {
  const fee = +((amount * (gw.feePct || 0) / 100 + (gw.feeFixed || 0)).toFixed(2));
  const live = !outboundOffline() && gw.mode === "live" ? gatewaySecrets(tenantId, gw.id) : null;
  if (live && live.cfg && Object.keys(live.cfg).length) {
    const r = await connect.pay({ provider: gw.id, config: live.cfg, amount, currency, idempotency, extra: extra || {} });
    if (r.live && r.ok) return { ref: r.id || `${gw.id}_${Date.now()}`, fee, status: stIs("payment", r.status, "settled") ? r.status : states.first("payment", "held"), live: true, redirect: r.redirect || null };
    if (r.live && !r.ok) return { ref: "failed_" + crypto.randomBytes(6).toString("hex"), fee: 0, status: states.first("payment", "failure"), live: true, error: r.error };
  }
  const sim = simulateGateway(gw, amount); sim.fee = fee; return sim;
}
function notify(tenantId, subject, body, to) {
  const offline = outboundOffline();
  const rows = all("SELECT * FROM tenant_gateways WHERE tenant_id=? AND provider_id LIKE 'notify:%' AND enabled=1 AND mode='live' ORDER BY position", tenantId);
  const nctx = rules.at("notify.send", tenantId);
  for (const g of rows) {
    const id = g.provider_id.slice(7);
    if (!rules.permitsAt("notify.send", id, nctx)) continue;
    if (offline || mailer.isLocal(id)) { console.log(`  ✉️  [${id}${offline ? "·offline" : ""}] ${subject} — ${body}`); audit(tenantId, "system", null, "notifier", "notify.sent", "notification", id, { subject, channel: id, offline: !!offline }); continue; }
    let cfg = {}; try { cfg = JSON.parse(g.config || "{}"); } catch (e) { }
    cfg = sec.unsealConfig(tenantId, "notify:" + id, JSON.stringify(cfg));
    audit(tenantId, "system", null, "notifier", "notify.sent", "notification", id, { subject, channel: id });
    const k = mailer.kernelOf(id);
    if (k) { k.send(cfg, { to: to || cfg.to, subject, text: body, via: id }).catch(e => audit(tenantId, "system", null, "notifier", "notify.failed", "notification", id, { subject, error: e.message })); continue; }
    connect.notify({ provider: id, config: cfg, subject, text: body, to: to || cfg.to }).then(r => {
      if (r.live && !r.ok) audit(tenantId, "system", null, "notifier", "notify.failed", "notification", id, { subject, error: r.error });
    }).catch(() => { });
  }
}

/* ---------------- public config & providers ---------------- */
function apiStores(req, res) {
  const op = stIn("tenant", "operating");
  json(res, 200, { stores: all("SELECT slug,name,domain FROM tenants WHERE status IN " + op.sql + " ORDER BY id", ...op.args) });
}
function apiConfig(req, res, url, s) {
  const c = CFG(s); const cm = commerceOf(s);
  /* the universal theme cascade: product → dept → tenant → platform, then the store's
     own settings.theme. The storefront receives one resolved skin, whatever scope it
     was assigned at. */
  const themeResolved = themes.resolve({ tenantId: T(s) }) || null;
  json(res, 200, {
    tenant: { id: s.tenant.id, slug: s.tenant.slug, name: s.tenant.name, mode: s.tenant.mode, kind: kindBrief(s.tenant), industries: J(s.tenant.industries, []) },
    brand: c.brand, theme: themeResolved ? { ...c.theme, ...themeResolved.vars, __theme: themeResolved } : c.theme,
    commerce: { ...cm, freeShipThreshold: money2(cm, c.commerce.freeShipThreshold), shipFee: money2(cm, c.commerce.shipFee), giftAmounts: (c.commerce.giftAmounts || []).map(x => money2(cm, x)), giftMax: money2(cm, c.commerce.giftMax) }, features: c.features, copy: c.copy,
    geo: { countries: registry.countries().filter(c => c.active !== 0), taxModes: registry.taxModes(), currencies: registry.currencies(), subdivisions: registry.subdivisionsFor(cm.country) },
    capabilities: [...mods.caps(T(s))].filter(c => mods.hasCap(T(s), c)), gates: require("./gates.js").all(T(s)),
    departments: all("SELECT key,label,icon FROM departments WHERE tenant_id=? AND active=1 ORDER BY position", T(s)),
    brands: all("SELECT key,label,icon,logo,country FROM brands WHERE tenant_id=? AND active=1 ORDER BY position", T(s)),
    home: {
      banners: all("SELECT id,title,subtitle,cta,hue,dept FROM home_banners WHERE tenant_id=? AND active=1 ORDER BY position", T(s)),
      cards: all("SELECT id,title,dept,tiles FROM home_cards WHERE tenant_id=? AND active=1 ORDER BY position", T(s)).map(r => ({ ...r, tiles: JSON.parse(r.tiles || "[]") }))
    }
  });
}

/* ---------- universal theming API ----------
   Themes are data: presets are read, assigned at any scope, and created from any hue.
   Reads are open to a logged-in merchant (they need to see their own skin); writes
   to presets and assignments are platform-owned, because a theme dresses the store. */
function apiThemes(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  json(res, 200, { presets: themes.presets(), assignments: themes.assignments() });
}
function apiThemeResolve(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  const ctx = { tenantId: T(s), dept: url.searchParams.get("dept"), productId: url.searchParams.get("product_id") };
  const t = themes.resolve(ctx);
  json(res, 200, { theme: t, via: t && t.via, fallback: !t });
}
function apiThemeAssign(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  const scope = String(body && body.scope || "").trim();
  const scopeKey = String(body && body.scope_key != null ? body.scope_key : (body.scope === "tenant" ? T(s) : "")).trim();
  const themeKey = String(body && body.theme_key || "").trim();
  if (!["platform", "tenant", "dept", "product"].includes(scope)) return bad(res, "scope must be platform | tenant | dept | product", 400);
  if (!scopeKey) return bad(res, "scope_key required", 400);
  if (!themeKey) return bad(res, "theme_key required", 400);
  const out = themes.assign(scope, scopeKey, themeKey);
  logAction(s, "theme.assign", "theme", scope + ":" + scopeKey, out, req);
  json(res, out.ok ? 200 : 409, out);
}
function apiThemeUnassign(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  const out = themes.unassign(String(body && body.scope || "").trim(), String(body && body.scope_key != null ? body.scope_key : "").trim());
  logAction(s, "theme.unassign", "theme", body && body.scope, out, req);
  json(res, 200, out);
}
/* explore the generative space: any hue → a complete theme, without committing.
   This is the "unlimited" primitive — the gallery is finite, the hue space is not */
function apiThemePreview(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  const raw = url.searchParams.get("hue");
  if (raw === null || raw === "") return bad(res, "hue (0-359) required", 400);
  const hue = Number(raw);
  if (!isFinite(hue)) return bad(res, "hue (0-359) required", 400);
  json(res, 200, themes.previewHue(hue, !/0|false|no/i.test(url.searchParams.get("light") || "")));
}
/* name a hue-generated theme and keep it forever — the registry's growth path */
function apiThemeCreate(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  const out = themes.createFromHue(body && body.key, body && body.name, body && body.hue,
    { dark: body && body.dark, mood: body && body.mood, radius: body && body.radius, radiusBtn: body && body.radiusBtn });
  logAction(s, "theme.create", "theme", out.key, out, req);
  json(res, out.ok ? 200 : 409, out);
}

/* ---------- UNIVERSAL DASHBOARD & REPORTING ENGINE (Architecture1 §394/§395) ----------
   Dashboards and reports are DATA: the routes below are the thinnest possible CRUD +
   render surface over lib/dashboards.js. There is deliberately no per-dashboard route —
   a new dashboard is a row, not an endpoint, which is what §394 declares. */
const dashboards = require("./dashboards.js");
/* the entity vocabulary a widget may point at, so the console's picker is derived from
   the engine itself (native entities + every corpus universe) rather than maintained */
function apiDashboardEntities(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  const ents = entity.allEntities(T(s));
  json(res, 200, { entities: Object.keys(ents).map(k => ({ key: k, label: ents[k].label || k, icon: ents[k].icon || "🧩",
    storage: ents[k].storage === "json" ? "json" : "table", platformOnly: !!ents[k].platformOnly,
    fields: (ents[k].fields || []).map(f => ({ key: f.key, label: f.label, type: f.type, col: f.col || f.key })) })),
    metrics: dashboards.METRICS, kinds: dashboards.KINDS, types: dashboards.DASHBOARD_TYPES });
}
function apiDashboards(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  json(res, 200, { dashboards: dashboards.list(T(s), { platform: !!s.platform_admin, includeInactive: !!s.platform_admin }) });
}
function apiDashboardRender(req, res, url, s, body, key) {
  if (!requireStaff(s, res)) return;
  /* audience is enforced inside render(): a platform-audience board metrics across
     tenants, so only a platform session may render it — by key as well as in the list */
  const out = dashboards.render(T(s), key, s.user_id || null, !!s.platform_admin);
  if (out.error) return bad(res, out.error, out.error.indexOf("unknown") === 0 ? 404 : 403);
  json(res, 200, out);
}
function apiDashboardSave(req, res, url, s, body, key) {
  if (!requireStaff(s, res)) return;
  const b = body || {};
  const row = { name: String(b.name || "Untitled dashboard").slice(0, 120), type: String(b.type || require("./defaults.js").of("dashboardTypes")).slice(0, 40),
    audience: ["admin", "platform", "all"].includes(b.audience) ? b.audience : "admin",
    description: String(b.description || "").slice(0, 500), active: b.active === false ? 0 : 1,
    position: Number(b.position) || 0 };
  if (key && /^\d+$/.test(key)) {
    /* S7: the UPDATE was scoped only by id, so a store admin could rename or
       deactivate another store's dashboard (or a platform template) by number.
       Ownership is exactly what the read path already enforces. */
    const own = get("SELECT tenant_id FROM dashboards WHERE id=?", Number(key));
    if (!own) return bad(res, "unknown dashboard " + key, 404);
    const isPlatformRow = own.tenant_id === null || own.tenant_id === undefined;
    if (!isPlatformRow ? Number(own.tenant_id) !== T(s) : !s.platform_admin)
      return bad(res, "That dashboard belongs to another store", 403);
    run("UPDATE dashboards SET name=?,type=?,audience=?,description=?,active=?,position=? WHERE id=?", row.name, row.type, row.audience, row.description, row.active, row.position, Number(key));
    logAction(s, "dashboard.update", "dashboard", key, row, req);
    json(res, 200, { ok: true, id: Number(key) });
  } else {
    const k = String(key || b.key || "dash-" + Date.now()).replace(/[^a-z0-9-]+/g, "-").slice(0, 60);
    const r = run("INSERT INTO dashboards(tenant_id,key,name,type,audience,description,active,position) VALUES(?,?,?,?,?,?,?,?)",
      s.platform_admin && b.audience === "platform" ? null : T(s), k, row.name, row.type, row.audience, row.description, row.active, row.position);
    logAction(s, "dashboard.create", "dashboard", k, row, req);
    json(res, 200, { ok: true, id: Number(r.lastInsertRowid), key: k });
  }
}
/* changing a board (deleting it, or its widgets) requires OWNING it: this store's own board,
   or — for a platform template (tenant_id NULL) — a platform admin. Reading is wider (shared
   'all' boards are visible to every store), but visible was being treated as writable. */
function ownsDashboard(s, d) {
  return d.tenant_id == null ? !!s.platform_admin : Number(d.tenant_id) === T(s);
}
function apiDashboardDelete(req, res, url, s, body, key) {
  if (!requireStaff(s, res)) return;
  const d = dashboards.getDashboard(T(s), key);
  if (!d) return bad(res, "unknown dashboard " + key, 404);
  if (!ownsDashboard(s, d)) return bad(res, "That dashboard belongs to another store", 403);
  run("DELETE FROM dashboard_widgets WHERE dashboard_id=?", d.id);
  run("DELETE FROM dashboard_prefs WHERE dashboard_id=?", d.id);
  run("DELETE FROM dashboards WHERE id=?", d.id);
  logAction(s, "dashboard.delete", "dashboard", key, {}, req);
  json(res, 200, { ok: true });
}
/* a widget is added/edited as a row — the console never computes, only declares */
function apiWidgetSave(req, res, url, s, body, key) {
  if (!requireStaff(s, res)) return;
  const b = body || {};
  const d = dashboards.getDashboard(T(s), key);
  if (!d) return bad(res, "unknown dashboard " + key, 404);
  if (!ownsDashboard(s, d)) return bad(res, "That dashboard belongs to another store", 403);
  const edef = entity.allEntities(T(s))[String(b.entity || "order")];
  if (edef && edef.storage !== "json" && edef.table && (edef.platformOnly || edef.noTenant) && !s.platform_admin) return bad(res, "That entity is platform-wide — only the platform console can chart it", 403);
  const row = { kind: dashboards.KINDS.includes(b.kind) ? b.kind : "kpi",
    label: String(b.label || "Widget").slice(0, 120), entity: String(b.entity || "order").slice(0, 80),
    metric: dashboards.METRICS.includes(b.metric) ? b.metric : "count",
    column: String(b.column || "").slice(0, 60), dimension: String(b.dimension || "").slice(0, 60),
    ord: b.ord === "asc" ? "asc" : "desc", lim: Math.min(200, Math.max(1, Number(b.lim) || 10)),
    filter: JSON.stringify(b.filter && typeof b.filter === "object" ? b.filter : {}),
    position: Number(b.position) || 0, span: Math.min(6, Math.max(1, Number(b.span) || 3)) };
  if (b.id) {
    run("UPDATE dashboard_widgets SET kind=?,label=?,entity=?,metric=?,column=?,dimension=?,ord=?,lim=?,filter=?,position=?,span=? WHERE id=? AND dashboard_id=?",
      row.kind, row.label, row.entity, row.metric, row.column || null, row.dimension || null, row.ord, row.lim, row.filter, row.position, row.span, Number(b.id), d.id);
    logAction(s, "dashboard.widget.update", "dashboard_widget", b.id, row, req);
    json(res, 200, { ok: true, id: Number(b.id) });
  } else {
    const r = run("INSERT INTO dashboard_widgets(dashboard_id,kind,label,entity,metric,column,dimension,ord,lim,filter,position,span) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
      d.id, row.kind, row.label, row.entity, row.metric, row.column || null, row.dimension || null, row.ord, row.lim, row.filter, row.position, row.span);
    logAction(s, "dashboard.widget.add", "dashboard_widget", r.lastInsertRowid, row, req);
    json(res, 200, { ok: true, id: Number(r.lastInsertRowid) });
  }
}
function apiWidgetDelete(req, res, url, s, body, key) {
  if (!requireStaff(s, res)) return;
  const wid = Number(url.searchParams.get("widget_id"));
  if (!wid) return bad(res, "widget_id required", 400);
  const d = dashboards.getDashboard(T(s), key);
  if (!d) return bad(res, "unknown dashboard " + key, 404);
  if (!ownsDashboard(s, d)) return bad(res, "That dashboard belongs to another store", 403);
  run("DELETE FROM dashboard_widgets WHERE id=? AND dashboard_id=?", wid, d.id);
  run("DELETE FROM dashboard_prefs WHERE widget_id=?", wid);
  logAction(s, "dashboard.widget.delete", "dashboard_widget", wid, {}, req);
  json(res, 200, { ok: true });
}
/* §1439 Personalization: the operator's own view of a shared dashboard */
function apiDashboardPref(req, res, url, s, body, key) {
  if (!requireStaff(s, res)) return;
  const d = dashboards.getDashboard(T(s), key);
  if (!d) return bad(res, "unknown dashboard " + key, 404);
  const b = body || {};
  dashboards.setPref(T(s), s.user_id || 0, d.id, Number(b.widget_id), { hidden: !!b.hidden, position: b.position });
  json(res, 200, { ok: true });
}
/* §395 Reporting Engine */
function apiReports(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  dashboards.runDue(T(s));            /* opportunistic: scheduled reports run when read */
  json(res, 200, { reports: dashboards.reportsFor(T(s), !!s.platform_admin) });
}
function apiReportRun(req, res, url, s, body, key) {
  if (!requireStaff(s, res)) return;
  const out = dashboards.runReport(T(s), key);
  if (out.error) return bad(res, out.error, 400);
  logAction(s, "report.run", "report", key, { kind: out.report && out.report.kind }, req);
  json(res, 200, out);
}
function apiReportSave(req, res, url, s, body, key) {
  if (!requireStaff(s, res)) return;
  const b = body || {};
  /* a metric alias names a result column — a plain identifier only (it reaches SQL) */
  const badAlias = (Array.isArray(b.metrics) ? b.metrics : []).find(m => m && m.alias != null && m.alias !== "" && !dashboards.validAlias(m.alias));
  if (badAlias) return bad(res, "Metric alias must be a plain identifier (letters, digits, underscore): " + String(badAlias.alias).slice(0, 40), 400);
  const row = { name: String(b.name || "Untitled report").slice(0, 120), kind: String(b.kind || require("./defaults.js").of("dashboardTypes")).slice(0, 40),
    entity: String(b.entity || "order").slice(0, 80), metrics: JSON.stringify(Array.isArray(b.metrics) ? b.metrics : []),
    dimensions: JSON.stringify(Array.isArray(b.dimensions) ? b.dimensions : []), filter: JSON.stringify(b.filter && typeof b.filter === "object" ? b.filter : {}),
    schedule: ["manual", "daily", "weekly", "monthly"].includes(b.schedule) ? b.schedule : "manual",
    format: ["table", "csv", "json"].includes(b.format) ? b.format : "table", active: b.active === false ? 0 : 1 };
  if (key && /^\d+$/.test(key)) {
    /* S7: same cross-tenant write on reports — scope the UPDATE to a row the
       caller actually owns (a platform template row needs a platform admin) */
    const own = get("SELECT tenant_id FROM reports WHERE id=?", Number(key));
    if (!own) return bad(res, "unknown report " + key, 404);
    const isPlatformRow = own.tenant_id === null || own.tenant_id === undefined;
    if (!isPlatformRow ? Number(own.tenant_id) !== T(s) : !s.platform_admin)
      return bad(res, "That report belongs to another store", 403);
    run("UPDATE reports SET name=?,kind=?,entity=?,metrics=?,dimensions=?,filter=?,schedule=?,format=?,active=? WHERE id=?",
      row.name, row.kind, row.entity, row.metrics, row.dimensions, row.filter, row.schedule, row.format, row.active, Number(key));
    logAction(s, "report.update", "report", key, row, req);
    json(res, 200, { ok: true, id: Number(key) });
  } else {
    const k = String(key || b.key || "rep-" + Date.now()).replace(/[^a-z0-9-]+/g, "-").slice(0, 60);
    const r = run("INSERT INTO reports(tenant_id,key,name,kind,entity,metrics,dimensions,filter,schedule,format,active,position) VALUES(?,?,?,?,?,?,?,?,?,?,?,0)",
      s.platform_admin && b.audience === "platform" ? null : T(s), k, row.name, row.kind, row.entity, row.metrics, row.dimensions, row.filter, row.schedule, row.format, row.active);
    logAction(s, "report.create", "report", k, row, req);
    json(res, 200, { ok: true, id: Number(r.lastInsertRowid), key: k });
  }
}
function apiReportDelete(req, res, url, s, body, key) {
  if (!requireStaff(s, res)) return;
  const col = /^\d+$/.test(String(key)) ? "id" : "key";
  /* S7: the DELETE was unscoped — any store admin could remove another store's
     report (or a platform template) by id or key. Verify ownership first, the
     same way apiDashboardDelete does through getDashboard(). */
  const own = get("SELECT tenant_id FROM reports WHERE " + col + "=?", col === "id" ? Number(key) : String(key));
  if (!own) return bad(res, "unknown report " + key, 404);
  const isPlatformRow = own.tenant_id === null || own.tenant_id === undefined;
  if (!isPlatformRow ? Number(own.tenant_id) !== T(s) : !s.platform_admin)
    return bad(res, "That report belongs to another store", 403);
  run("DELETE FROM reports WHERE " + col + "=?", col === "id" ? Number(key) : String(key));
  logAction(s, "report.delete", "report", key, {}, req);
  json(res, 200, { ok: true });
}
function apiProviders(req, res, url, s) {
  const c = CFG(s);
  const country = registry.countryProfile(c.commerce.country);
  const cm2 = commerceOf(s);
  const q = k => url.searchParams.get(k);
  const amount = q("amount") != null && q("amount") !== "" && isFinite(Number(q("amount"))) ? Number(q("amount")) : (cartPayload(s).items.length ? +cartPayload(s).items.reduce((n, x) => n + x.unitBase * x.qty, 0).toFixed(2) : undefined);
  const rctx = ruleCtx(s, "checkout.gateways", { amount });
  const gws = permittedGateways(s, rctx).map(g => ({ id: g.id, name: g.name, emoji: g.emoji, methods: g.methods, feePct: g.feePct, mode: g.mode, primary: g.is_primary }));
  json(res, 200, {
    country: { code: country.code, name: country.name, currency: country.currency, symbol: country.symbol, locale: country.locale },
    gateways: gws, carriers: permittedCarriers(s, rctx).map(x => ({ id: x.id, name: x.name, emoji: x.emoji, eta: x.eta, baseFee: x.baseFee != null ? money2(cm2, x.baseFee) : undefined, freeOver: x.freeOver, primary: x.is_primary })),
    tax: { mode: commerceOf(s).taxMode, rate: commerceOf(s).taxRate }, taxModes: registry.taxModes()
  });
}

/* ---------------- session ---------------- */
function apiSession(req, res, url, s) {
  const owner = ownerFor(s);
  const cart = all("SELECT product_id, qty FROM cart_items WHERE owner=?", owner);
  const sub = cart.reduce((n, c) => { const p = get("SELECT price FROM products WHERE tenant_id=? AND id=?", T(s), c.product_id); return p ? n + p.price * c.qty : n; }, 0);
  const urow = s.user_id ? get("SELECT id,name,email,role,staff_role,perms FROM users WHERE id=? AND tenant_id=?", s.user_id, T(s)) : null;
  json(res, 200, {
    user: urow,
    allowedSections: s.platform_admin ? ["*"] : (urow ? rbac.allowedSections(urow, T(s)) : []),
    zip: s.zip, gift: require("./gates.js").on(T(s), "checkout.wallet") ? mods.walletBalance(T(s), mods.ownerFor(s)) : 0, coupon: s.coupon || "", capabilities: [...mods.caps(T(s))].filter(c => mods.hasCap(T(s), c)), gates: require("./gates.js").all(T(s)),
    cartCount: cart.reduce((n, c) => n + c.qty, 0), cartSubtotal: sub,
    saved: all("SELECT product_id FROM saved_items WHERE owner=?", owner).map(r => r.product_id),
    viewed: all("SELECT product_id FROM view_history WHERE owner=? ORDER BY seen_at DESC LIMIT 12", owner).map(r => r.product_id)
  });
}
function apiCoupon(req, res, url, s, body) {
  if (!sec.policy().provisioning.couponsAllowed) return bad(res, "Promo codes are disabled by platform policy", 403);
  if (!CFG(s).features.coupons) return bad(res, "Promo codes are disabled for this store", 403);
  const code = String(body.code || "").trim().toUpperCase();
  if (code) {
    const v = offers.validateCoupon(T(s), code, s.user_id ? ownerFor(s) : "");
    if (!v.ok) return bad(res, v.reason || "Invalid or expired promo code", 404);
  }
  run("UPDATE tenant_state SET coupon=? WHERE sid=? AND tenant_id=?", code, s.sid, T(s));
  s.coupon = code;
  logAction(s, code ? "coupon.apply" : "coupon.remove", "coupon", code);
  json(res, 200, cartPayload(s));
}
function apiZip(req, res, url, s, body) {
  const zip = String(body.zip || "").trim().slice(0, 12);
  if (!zip) return bad(res, "Location required");
  setTenantState(s.sid, T(s), { zip }); s.zip = zip;
  /* the quick-commerce promise is resolved on every location set so the storefront
     can show "delivery in N minutes" or fall back to standard days */
  const qc = qcommerce.promise(T(s), zip, body.lat != null ? +body.lat : null, body.lng != null ? +body.lng : null);
  json(res, 200, { ok: true, zip, quickCommerce: qc });
}

/* ---------------- auth ---------------- */
/* every passwordless path (OTP, TOTP, magic link, biometric, SSO/OIDC callback) proves the
   claim the same way and then does exactly the same things: bind the store session
   to the account, fold the anonymous cart/wallet into it, and audit. One helper, so a new
   method cannot drift from the password path's accounting.
   The unified console holds BOTH authorities on one client — a store sign-in no longer
   drops a platform session. The scopes stay separated because authz namespaces every
   grant (a store role yields store:* only), so carrying both is two scoped capabilities,
   never one blended one. */
/* the session id changes whenever its privilege does (sign-in, sign-out). A sid an
   attacker planted before sign-in (a sibling tenant subdomain can set a parent-domain
   cookie) must not become an authenticated session. The row, its per-store state and any
   anonymous carts/wallets other stores hold for it move to the new id; the old id is gone. */
function isTls(req) { return !!(req && req.socket && req.socket.encrypted); }
function rotateSession(req, res, s) {
  const old = s.sid;
  if (!old || !get("SELECT sid FROM sessions WHERE sid=?", old)) return;
  const sid = crypto.randomBytes(24).toString("hex");
  run("UPDATE sessions SET sid=? WHERE sid=?", sid, old);
  const states = all("SELECT tenant_id FROM tenant_state WHERE sid=?", old);
  run("UPDATE tenant_state SET sid=? WHERE sid=?", sid, old);
  for (const st of states) {
    const from = "t" + st.tenant_id + ":s:" + old, to = "t" + st.tenant_id + ":s:" + sid;
    try { mergeOwner(from, to); } catch (e) { }
    try { mods.walletMerge(from, to); } catch (e) { }
  }
  s.sid = sid;
  /* when this session last PROVED who it is — sensitive changes (adding a sign-in credential)
     require it to be recent */
  run("UPDATE sessions SET auth_at = CASE WHEN user_id IS NOT NULL THEN datetime('now') ELSE NULL END WHERE sid=?", sid);
  res.appendHeader("Set-Cookie", `azs=${sid}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${30 * 86400}${isTls(req) ? "; Secure" : ""}`);
}
function establishSession(req, res, s, userId, action, detail) {
  run("UPDATE sessions SET user_id=? WHERE sid=?", userId, s.sid);
  s.user_id = userId;
  run("UPDATE users SET last_login=datetime('now') WHERE id=?", userId);
  mergeOwner("t" + T(s) + ":s:" + s.sid, "t" + T(s) + ":u:" + userId);
  try { mods.walletMerge("t" + T(s) + ":s:" + s.sid, "t" + T(s) + ":u:" + userId); } catch (e) { }
  rotateSession(req, res, s);
  logAction(s, action, "user", userId, detail || {}, req);
}
/* request-path credential work runs on the thread pool (await …Async): a synchronous scrypt
   here stalled the whole server for every anonymous registration / login / hint request */
async function apiRegister(req, res, url, s, body) {
  const name = String(body.name || "").trim().slice(0, 60);
  const email = String(body.email || "").trim().toLowerCase();
  const password = String(body.password || "");
  if (!name || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return bad(res, "Please enter a valid name and email");
  const perr = sec.checkPassword(password, email);
  if (perr) return bad(res, perr);
  if (get("SELECT id FROM users WHERE tenant_id=? AND email=?", T(s), email)) return bad(res, "That email already has an account", 409);
  const uid = await newUserAsync(T(s), name, email, password, "customer");
  mergeOwner("t" + T(s) + ":s:" + s.sid, "t" + T(s) + ":u:" + uid);
  mods.walletMerge("t" + T(s) + ":s:" + s.sid, "t" + T(s) + ":u:" + uid);
  run("UPDATE sessions SET user_id=? WHERE sid=?", uid, s.sid);
  s.user_id = uid;
  rotateSession(req, res, s);
  logAction(s, "auth.register", "user", uid, { email });
  json(res, 200, { ok: true, user: { id: uid, name, email, role: "customer" } });
}
async function apiLogin(req, res, url, s, body) {
  const email = String(body.email || "").trim();
  const lock = sec.lockState(email);
  if (lock.locked) return bad(res, "Account temporarily locked after failed attempts — retry in " + lock.retryAfterSec + "s", 423);
  const u = await verifyUserAsync(T(s), email, String(body.password || ""));
  /* one answer for every failure. The old messages told an anonymous caller whether the
     email existed, which store it belonged to, whether it was a platform account — and
     printed the store admin's own email address. */
  if (!u) { sec.noteLoginFail(email); logAction(s, "auth.login_failed", "user", null, { email }, req);
    return bad(res, "Invalid email or password for " + s.tenant.name + " (accounts belong to one store — add ?store=slug to switch)", 401);
  }
  sec.noteLoginOk(email);
  if (u.disabled) return bad(res, "This account has been disabled by a store owner", 403);
  /* a sign-in method is subject to the applicability rules for customers (a platform's own
     staff are never locked out of their console by a customer-facing rule) */
  if (!rules.exempt("login.password", u.role)) { const d = rules.decideAt("login.password", undefined, rules.at("login.password", T(s))); if (!d.ok) return bad(res, "This sign-in method is not available here — " + d.reasons.join("; "), 403); }
  /* the unified console holds both authorities at once: a store sign-in binds the
     store user without dropping a platform session this client may also hold. The
     scopes cannot blend — authz namespaces each authority's grants */
  run("UPDATE users SET last_login=datetime('now') WHERE id=?", u.id);
  mergeOwner("t" + T(s) + ":s:" + s.sid, "t" + T(s) + ":u:" + u.id);
  mods.walletMerge("t" + T(s) + ":s:" + s.sid, "t" + T(s) + ":u:" + u.id);
  run("UPDATE sessions SET user_id=? WHERE sid=?", u.id, s.sid);
  s.user_id = u.id;
  rotateSession(req, res, s);
  logAction(s, "auth.login", "user", u.id, { email: u.email });
  json(res, 200, { ok: true, user: { id: u.id, name: u.name, email: u.email, role: u.role, staff_role: u.staff_role || "owner" } });
}
/* the address a person is sent back to (a reset link, a payment return page). Never taken
   from the request's Host header in production — a forged Host would mail a victim a link
   to an attacker's site carrying their reset token. LX_PUBLIC_URL (the platform's address,
   the store chosen by ?store=) wins; else the store's own domain; only outside production
   does the request's own origin stand in, so local development works. */
function publicOrigin(req, s) {
  const base = String(process.env.LX_PUBLIC_URL || "").replace(/\/+$/, "");
  if (base) return { origin: base, storeQuery: "store=" + encodeURIComponent(s.tenant.slug) };
  const dom = String(s.tenant.domain || "").replace(/^https?:\/\//, "").replace(/\/+$/, "");
  if (process.env.NODE_ENV === "production") return dom ? { origin: "https://" + dom, storeQuery: "" } : null;
  const host = String(req && req.headers && req.headers.host || "").toLowerCase();
  const name = host.replace(/:\d+$/, "");
  if (!/^[a-z0-9.-]+(:\d+)?$/.test(host) || !(name === "localhost" || name === "127.0.0.1" || name.endsWith(".localhost") || (dom && name === dom.toLowerCase()))) return null;
  return { origin: (isTls(req) ? "https://" : "http://") + host, storeQuery: "store=" + encodeURIComponent(s.tenant.slug) };
}
function publicLink(req, s, page, params) {
  const o = publicOrigin(req, s); if (!o) return null;
  const q = [o.storeQuery].concat(Object.keys(params || {}).map(k => k + "=" + encodeURIComponent(params[k]))).filter(Boolean).join("&");
  return o.origin + "/" + page + (q ? "?" + q : "");
}
const RESET_TTL_MIN = 30;
const sha256hex = v => crypto.createHash("sha256").update(String(v)).digest("hex");
/* "forgot password" answers the same whether or not the account exists, so it cannot be
   used to discover who shops here. At most three links per account per 15 minutes; a new
   link retires the older ones. */
function apiPasswordForgot(req, res, url, s, body) {
  if (!requireStore(s, res)) return;
  const email = String(body.email || "").trim().toLowerCase();
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return bad(res, "Please enter a valid email", 400);
  const answer = { ok: true, message: "If an account exists for that email, a reset link is on its way. It expires in " + RESET_TTL_MIN + " minutes." };
  const u = get("SELECT id, email, name, disabled FROM users WHERE tenant_id=? AND email=?", T(s), email);
  if (!u || u.disabled) { logAction(s, "auth.password_forgot", "user", null, { known: false }, req); return json(res, 200, answer); }
  const recent = get("SELECT COUNT(*) c FROM password_resets WHERE user_id=? AND created_at > datetime('now','-15 minutes')", u.id).c;
  if (recent >= 3) { logAction(s, "auth.password_forgot", "user", u.id, { throttled: true }, req); return json(res, 200, answer); }
  const token = crypto.randomBytes(32).toString("hex");
  run("UPDATE password_resets SET used_at=datetime('now') WHERE user_id=? AND used_at IS NULL", u.id);
  run("INSERT INTO password_resets(tenant_id,user_id,token_hash,expires_at,ip) VALUES(?,?,?,?,?)", T(s), u.id, sha256hex(token), Date.now() + RESET_TTL_MIN * 60000, ipOf(req));
  const link = publicLink(req, s, "reset.html", { token });
  require("./mailer.js").deliver({ tenantId: T(s), channel: "email", to: u.email, kind: "password_reset",
    subject: "Reset your " + s.tenant.name + " password",
    text: "Someone asked to reset the password for " + u.email + ".\n\n"
      + (link ? "Choose a new password here: " + link : "Your reset code is " + token + " — enter it on the store's reset page.")
      + "\n\nThe link expires in " + RESET_TTL_MIN + " minutes and works once. If this wasn't you, ignore this email; your password has not changed." });
  logAction(s, "auth.password_forgot", "user", u.id, { sent: true }, req);
  json(res, 200, answer);
}
/* a reset proves control of the mailbox, so it ends every session the account holds (the
   reason for a reset is often that someone else is signed in) and clears the lockout */
async function apiPasswordReset(req, res, url, s, body) {
  if (!requireStore(s, res)) return;
  const token = String(body.token || "").trim();
  const password = String(body.password || "");
  const row = /^[0-9a-f]{64}$/.test(token) ? get("SELECT * FROM password_resets WHERE token_hash=? AND tenant_id=?", sha256hex(token), T(s)) : null;
  if (!row || row.used_at || row.expires_at < Date.now()) return bad(res, "This reset link is invalid or has expired — request a new one", 400);
  const u = get("SELECT id, email, disabled FROM users WHERE id=? AND tenant_id=?", row.user_id, T(s));
  if (!u || u.disabled) return bad(res, "This reset link is invalid or has expired — request a new one", 400);
  const perr = sec.checkPassword(password, u.email);
  if (perr) return bad(res, perr, 422);
  if ((await verifyUserAsync(T(s), u.email, password)) || (await passwordReusedAsync(T(s), u.email, password))) return bad(res, "You cannot reuse a previous password", 422);
  /* claim the token before the slow hash, so two concurrent submissions cannot both win */
  const claimed = run("UPDATE password_resets SET used_at=datetime('now') WHERE id=? AND used_at IS NULL", row.id);
  if (!claimed.changes) return bad(res, "This reset link is invalid or has expired — request a new one", 400);
  await setUserPasswordAsync(u.id, password, u.email);
  run("UPDATE sessions SET user_id=NULL WHERE user_id=?", u.id);
  if (s.user_id === u.id) s.user_id = null;
  sec.noteLoginOk(u.email);
  try { sec.noteLoginOk("otp:" + T(s) + ":" + u.email); } catch (e) { }
  logAction(s, "auth.password_reset", "user", u.id, {}, req);
  require("./mailer.js").deliver({ tenantId: T(s), channel: "email", to: u.email, kind: "password_changed",
    subject: "Your " + s.tenant.name + " password was changed",
    text: "The password for " + u.email + " was just reset, and every device signed in to the account was signed out.\n\nIf this wasn't you, reset it again straight away and contact the store." });
  json(res, 200, { ok: true });
}
function apiLogout(req, res, url, s) {
  run("UPDATE sessions SET user_id=NULL WHERE sid=?", s.sid);
  s.user_id = null;
  rotateSession(req, res, s);
  json(res, 200, { ok: true });
}
function apiTokenExchange(req, res, url, s, body) {
  const t = get("SELECT * FROM tokens WHERE token=? AND expires_at > datetime('now')", String(body.token || ""));
  if (!t) return bad(res, "Invalid or expired token", 401);
  if (t.tenant_id !== T(s)) return bad(res, "Token issued for a different store", 403);
  run("DELETE FROM tokens WHERE token=?", t.token);
  run("UPDATE sessions SET user_id=? WHERE sid=?", t.user_id, s.sid);
  s.user_id = t.user_id;
  rotateSession(req, res, s);
  const u = get("SELECT id,name,email,role FROM users WHERE id=?", t.user_id);
  json(res, 200, { ok: true, user: u });
}

/* ---------------- identity ---------------- */
function apiIdentityProvidersGet(req, res, url, s) {
  /* provider configs carry client ids/secrets — staff only (the sign-in menu a shopper
     needs is GET /api/auth/methods) */
  if (!requireSection(s, res, "settings", "read", "identity")) return;
  const identity = require("./identity.js");
  json(res, 200, { providers: identity.getIdentityProviders(T(s)) });
}
function apiIdentityProvidersPut(req, res, url, s, body) {
  if (!requireSection(s, res, "settings", "write", "identity")) return;
  const identity = require("./identity.js");
  json(res, 200, identity.upsertIdentityProvider(T(s), body));
}
function apiIdentityProviderDelete(req, res, url, s) {
  if (!requireSection(s, res, "settings", "write", "identity")) return;
  const identity = require("./identity.js");
  const id = url.pathname.match(/\/identity-providers\/([^/]+)$/)?.[1];
  if (!id) return bad(res, "Provider ID required", 400);
  json(res, 200, identity.deleteIdentityProvider(T(s), id));
}
function apiIdentitySettingsGet(req, res, url, s) {
  if (!requireSection(s, res, "settings", "read", "identity")) return;
  const identity = require("./identity.js");
  json(res, 200, { settings: identity.getIdentitySettings(T(s)) });
}
function apiIdentitySettingsPut(req, res, url, s, body) {
  if (!requireSection(s, res, "settings", "write", "identity")) return;
  const identity = require("./identity.js");
  json(res, 200, identity.setIdentitySettings(T(s), body));
}
function apiLoginInit(req, res, url, s, body) {
  if (!requireStore(s, res)) return;
  /* email/method must arrive as strings — node:sqlite raises a TypeError when asked to
     bind undefined, which turned a malformed client request into a 500. */
  if (!body.email || !body.method) return bad(res, 'email and method required', 400);
  const identity = require("./identity.js");
  /* opts are the caller's INTENT (register vs sign-in) and display hints, never security
     parameters — ttl/length/channel come from the store's provider row */
  const opts = { register: !!body.register, base_url: String(body.base_url || ""), state: String(body.state || "") };
  json(res, 200, identity.initiateLogin(T(s), String(body.email), String(body.method), opts));
}
/* the callback every external authority (SSO/OIDC/OAuth/directory) returns the user to.
   The state resolves the provider this login belongs to; the id_token is verified by the
   platform's single verifier, and the account is created when the provider allows it. */
function apiLoginCallback(req, res, url, s, body) {
  if (!requireStore(s, res)) return;
  const identity = require("./identity.js");
  const idToken = String(body.id_token || body.access_token || body.token || "");
  if (!idToken) return bad(res, "id_token is required", 400);
  const r = identity.completeExternal(T(s), idToken, body.state ? String(body.state) : null);
  if (!r.ok) return bad(res, r.error, 401);
  establishSession(req, res, s, r.userId, "auth.external_login", { email: r.email, method: "external" });
  json(res, 200, { ok: true, user: r.user, provisioned: !!r.provisioned });
}
function apiAuthMethods(req, res, url, s) {
  if (!requireStore(s, res)) return;
  const identity = require("./identity.js");
  json(res, 200, { methods: identity.enabledMethods(T(s)), settings: { passwordEnabled: identity.getIdentitySettings(T(s)).login.passwordEnabled !== false } });
}
function apiLoginOtpVerify(req, res, url, s, body) {
  if (!requireStore(s, res)) return;
  const identity = require("./identity.js");
  /* code and authenticator logins share the password path's lockout: a 6-digit code (and a
     TOTP's ±1 window) is guessable without one */
  const lockKey = "otp:" + T(s) + ":" + String(body.email || "").toLowerCase();
  const lock = sec.lockState(lockKey);
  if (lock.locked) return bad(res, "Too many attempts — retry in " + lock.retryAfterSec + "s", 423);
  const user = get("SELECT id FROM users WHERE email=? AND tenant_id=?", String(body.email || "").toLowerCase(), T(s));
  if (!user) { sec.noteLoginFail(lockKey); return bad(res, "User not found", 404); }
  const result = identity.verifyOTP(T(s), user.id, body.email, body.otp);
  if (!result.ok) sec.noteLoginFail(lockKey); else sec.noteLoginOk(lockKey);
  if (result.ok) establishSession(req, res, s, user.id, "auth.otp_login", { email: body.email, method: result.method || "code" });
  json(res, 200, result);
}
function apiLoginMagicLinkVerify(req, res, url, s, body) {
  if (!requireStore(s, res)) return;
  const identity = require("./identity.js");
  const user = get("SELECT id FROM users WHERE email=? AND tenant_id=?", String(body.email || "").toLowerCase(), T(s));
  if (!user) return bad(res, "User not found", 404);
  const result = identity.verifyMagicLink(user.id, body.token);
  if (result.ok) establishSession(req, res, s, user.id, "auth.magic_link_login", { email: body.email });
  json(res, 200, result);
}
function apiLoginBiometricVerify(req, res, url, s, body) {
  if (!requireStore(s, res)) return;
  const identity = require("./identity.js");
  const user = get("SELECT id FROM users WHERE email=? AND tenant_id=?", String(body.email || "").toLowerCase(), T(s));
  if (!user) return bad(res, "User not found", 404);
  const result = identity.verifyBiometric(user.id, body.challenge, body.assertion);
  if (result.ok) establishSession(req, res, s, user.id, "auth.biometric_login", { email: body.email });
  json(res, 200, result);
}
/* enrol a WebAuthn credential on the signed-in account. Called twice by a console:
   once with no body to mint the challenge the authenticator signs, then with the
   attestation + clientDataJSON. The attestation is VERIFIED server-side (challenge,
   origin and, for packed/u2f, the certificate signature) before any key is bound —
   an account can never gain a credential by asserting it has one. */
function apiBiometricRegister(req, res, url, s, body) {
  if (!requireStore(s, res)) return;
  const identity = require("./identity.js");
  const user = s.user_id ? get("SELECT id, tenant_id FROM users WHERE id=?", s.user_id) : null;
  if (!user) return bad(res, "Not authenticated", 401);
  if (body && body.attestation) {
    json(res, 200, identity.registerBiometric(user.id, body.attestation, body.challenge,
      { tenantId: user.tenant_id, clientDataJSON: body.clientDataJSON, origin: body.origin || null }));
    return;
  }
  json(res, 200, identity.biometricChallenge(user.id, user.tenant_id));
}
function apiIdentityMethodsGet(req, res, url, s) {
  if (!requireStore(s, res)) return;
  const identity = require("./identity.js");
  const user = s.user_id ? get("SELECT id FROM users WHERE id=?", s.user_id) : null;
  if (!user) return bad(res, "Not authenticated", 401);
  json(res, 200, { methods: identity.getUserIdentityMethods(user.id) });
}
async function apiIdentityMethodsLink(req, res, url, s, body) {
  if (!requireStore(s, res)) return;
  const identity = require("./identity.js");
  const user = s.user_id ? get("SELECT id FROM users WHERE id=?", s.user_id) : null;
  if (!user) return bad(res, "Not authenticated", 401);
  /* a passkey is enrolled only through the attested biometric flow, never linked as a bare row */
  if (/webauthn|passkey|biometric/i.test(String(body.method_type || ""))) return bad(res, "Passkeys are enrolled through the biometric registration flow", 400);
  /* adding a sign-in credential (an authenticator, a phone, another email) is a takeover path
     for a stolen session: it needs a sign-in within the last 10 minutes, or the current password */
  const fresh = get("SELECT 1 ok FROM sessions WHERE sid=? AND auth_at IS NOT NULL AND auth_at > datetime('now','-10 minutes')", s.sid);
  const full = get("SELECT email FROM users WHERE id=?", user.id);
  if (!fresh && !(body.current_password && full && (await verifyUserAsync(T(s), full.email, String(body.current_password)))))
    return bad(res, "Please sign in again (or confirm your current password) to add a sign-in method", 401);
  json(res, 200, identity.linkIdentityMethod(user.id, body.method_type, body.identifier, body.metadata, body.is_primary));
}
function apiIdentityMethodsUnlink(req, res, url, s) {
  if (!requireStore(s, res)) return;
  const identity = require("./identity.js");
  const user = s.user_id ? get("SELECT id FROM users WHERE id=?", s.user_id) : null;
  if (!user) return bad(res, "Not authenticated", 401);
  const methodId = url.pathname.match(/\/identity-methods\/([^/]+)$/)?.[1];
  if (!methodId) return bad(res, "Method ID required", 400);
  json(res, 200, identity.unlinkIdentityMethod(user.id, methodId));
}
function apiIdentityMethodsSetPrimary(req, res, url, s) {
  if (!requireStore(s, res)) return;
  const identity = require("./identity.js");
  const user = s.user_id ? get("SELECT id FROM users WHERE id=?", s.user_id) : null;
  if (!user) return bad(res, "Not authenticated", 401);
  const methodId = url.pathname.match(/\/identity-methods\/([^/]+)$/)?.[1];
  if (!methodId) return bad(res, "Method ID required", 400);
  json(res, 200, identity.setPrimaryMethod(user.id, methodId));
}

function mergeOwner(from, to) {
  if (from === to) return;
  for (const t of ["cart_items", "saved_items", "view_history"]) {
    const rows = all(`SELECT * FROM ${t} WHERE owner=?`, from);
    for (const r of rows) {
      if (t === "cart_items") {
        const ex = get("SELECT qty FROM cart_items WHERE owner=? AND product_id=?", to, r.product_id);
        if (ex) run("UPDATE cart_items SET qty = qty + ? WHERE owner=? AND product_id=?", r.qty, to, r.product_id);
        else run("INSERT INTO cart_items(owner, product_id, qty) VALUES(?,?,?)", to, r.product_id, r.qty);
      } else run(`INSERT OR IGNORE INTO ${t}(owner, product_id) VALUES(?,?)`, to, r.product_id);
    }
    run(`DELETE FROM ${t} WHERE owner=?`, from);
  }
}

/* ---------------- products / search ---------------- */
/* the storefront's sort orders are a registry list (productSortOrders): each row orders by
   product columns ({ field, dir }) or by a flag the product carries ({ flag, dir }); the row
   marked default applies when none is named. Only identifier-shaped names reach SQL. */
const SORT_ORDERS = require("./meta.js").SORT_ORDERS;
function sortClause(sort) {
  const l = rl("productSortOrders"); const rows = Array.isArray(l) && l.length ? l : SORT_ORDERS;
  const row = rows.find(r => r.key === String(sort || "")) || rows.find(r => r.default) || rows[0];
  const id = v => /^[A-Za-z_][A-Za-z0-9_]{0,40}$/.test(String(v || ""));
  const dir = d => (String(d).toUpperCase() === "ASC" ? "ASC" : "DESC");
  const parts = (row && row.order || []).map(o => o.field && id(o.field) ? o.field + " " + dir(o.dir) : o.flag && id(o.flag) ? "flags LIKE '%" + o.flag + "%' " + dir(o.dir) : null).filter(Boolean);
  return parts.length ? parts.join(", ") : "position DESC";
}
function buildSearch(s, url) {
  const c = CFG(s);
  const q = (url.searchParams.get("q") || "").trim().toLowerCase();
  let dept = url.searchParams.get("dept") || "all";
  const valid = all("SELECT key FROM departments WHERE tenant_id=? AND active=1", T(s)).map(r => r.key);
  if (dept !== "all" && !valid.includes(dept)) dept = "all";
  const rating = Math.min(5, Number(url.searchParams.get("rating") || 0));
  const pmin = Number(url.searchParams.get("pmin") || 0);
  const pmax = Number(url.searchParams.get("pmax") || 0);
  const prio = url.searchParams.get("prio") === "1";
  const deal = url.searchParams.get("deal") === "1" && c.features.deals;
  const where = ["tenant_id=?", "lifecycle='published'", "deleted_at IS NULL"], args = [T(s)];
  const node = url.searchParams.get("node");
  if (node) { where.push("node_id IN (" + nodeDescendants(T(s), node).map(() => "?").join(",") + ")"); args.push(...nodeDescendants(T(s), node)); }
  const ptype = url.searchParams.get("type");
  if (ptype) { where.push("type = ?"); args.push(ptype); }
  if (dept !== "all") { where.push("dept = ?"); args.push(dept); }
  if (rating) { where.push("rating >= ?"); args.push(rating); }
  if (pmin) { where.push("price >= ?"); args.push(pmin); }
  if (pmax) { where.push("price <= ?"); args.push(pmax); }
  if (prio) where.push("priority = 1");
  if (deal) where.push("deal_pct >= 10");
  if (q) for (const t of q.split(/\s+/).filter(Boolean)) {
    where.push("(lower(title) LIKE ? OR lower(brand) LIKE ? OR lower(keywords) LIKE ?)");
    args.push(`%${t}%`, `%${t}%`, `%${t}%`);
  }
  return { sql: where.join(" AND "), args, q, dept };
}
function publicProduct(p) {
  return {
    id: p.id, t: p.title, b: p.brand, d: p.dept, p: p.price, l: p.list_price, r: p.rating, c: p.ratings_count,
    e: p.emoji, h: p.hue, pr: !!p.priority, st: p.stock, fl: p.flags || "", kw: p.keywords, about: p.about || [],
    type: p.type || require("./defaults.js").of("productTypes"), node_id: p.node_id || null,
    identity: J(p.identity), attrs: J(p.attrs), vertical: J(p.vertical), media: J(p.media, []),
    seo: J(p.seo), pricing_rules: J(p.pricing_rules), logistics: J(p.logistics), tax_rule: J(p.tax_rule), uom: J(p.uom), packaging: J(p.packaging, [])
  };
}
function apiProducts(req, res, url, s) {
  const c = CFG(s);
  const { sql, args, dept, q } = buildSearch(s, url);
  const sort = url.searchParams.get("sort") || require("./defaults.js").of("productSortOrders");
  const per = Math.max(1, Math.min(200, Math.floor(Number(url.searchParams.get("limit") || url.searchParams.get("per") || c.commerce.perPage)) || 24));
  const page = Math.max(1, Number(url.searchParams.get("page") || 1));
  const total = get(`SELECT COUNT(*) c FROM products WHERE ${sql}`, ...args).c;
  const rows = all(`SELECT * FROM products WHERE ${sql} ORDER BY ${sortClause(sort)} LIMIT ? OFFSET ?`, ...args, per, (page - 1) * per);
  const cm = commerceOf(s);
  const items = rows.map(r => storeView({ ...r, about: [] }, cm));
  const noDept = new URL(url); noDept.searchParams.set("dept", "all");
  const facet = buildSearch(s, noDept);
  const deptCounts = {};
  all(`SELECT dept, COUNT(*) c FROM products WHERE ${facet.sql} GROUP BY dept`, ...facet.args).forEach(r => { deptCounts[r.dept] = (deptCounts[r.dept] || 0) + r.c; });
  json(res, 200, { q, dept, total, page, per, pages: Math.max(1, Math.ceil(total / per)), items, deptCounts });
}
/* ---- Search & Discovery (faceted + typo-tolerant + recommendation) ---- */
function apiSearch(req, res, url, s) {
  const f = {
    q: url.searchParams.get("q") || "",
    sort: url.searchParams.get("sort") || "relevance",
    page: url.searchParams.get("page") || "1",
    limit: url.searchParams.get("limit") || "20",
    facets: {}
  };
  for (const k of ["dept", "type", "brand", "pmin", "pmax", "rating"]) if (url.searchParams.get(k)) f.facets[k] = url.searchParams.get(k);
  json(res, 200, search.search(T(s), f));
}
function apiSuggest(req, res, url, s) {
  json(res, 200, { prefix: url.searchParams.get("prefix") || "", items: search.suggest(T(s), url.searchParams.get("prefix") || "", Number(url.searchParams.get("limit") || 10)) });
}
function apiRecommend(req, res, url, s) {
  json(res, 200, { anchor: url.searchParams.get("anchor") || "", owner: s.user_id ? ownerFor(s) : "", items: search.recommend(T(s), { anchor: url.searchParams.get("anchor") || "", owner: s.user_id ? ownerFor(s) : "", limit: Number(url.searchParams.get("limit") || 12) }) });
}
/* ---- Logistics & Supply-chain (fulfilment · tracking · 3PL · returns) ---- */
function apiShipments(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  const f = {}; if (url.searchParams.get("status")) f.status = url.searchParams.get("status"); if (url.searchParams.get("order")) f.order_id = url.searchParams.get("order");
  json(res, 200, { shipments: logistics.list(T(s), f), statuses: logistics.STATUSES });
}
function apiShipment(req, res, url, s, body, id) {
  if (!requireStaff(s, res)) return;
  const sh = logistics.track(T(s), Number(id));
  if (!sh) return bad(res, "Unknown shipment", 404);
  json(res, 200, { shipment: sh });
}
function apiShipmentCreate(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  const sh = logistics.createShipment(t, Number(body.order_id) || 0, String(body.carrier || ""), Number(body.warehouse_id) || null, body.meta || {});
  logAction(s, "logistics.shipment.create", "shipment", sh.id, { order: body.order_id, carrier: body.carrier });
  json(res, 200, { shipment: logistics.track(t, sh.id) });
}
function apiShipmentStatus(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  try {
    const sh = logistics.transition(T(s), Number(id), String(body.status), body);
    logAction(s, "logistics.shipment.transition", "shipment", sh.id, { to: body.status });
    json(res, 200, { shipment: logistics.track(T(s), sh.id) });
  } catch (e) { bad(res, e.message); }
}
function apiWarehouseRoute(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, logistics.route(T(s), Number(body.warehouse_id) || url.searchParams.get("warehouse_id") || null));
}
function apiSlaBreaches(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { breaches: logistics.slaBreaches(T(s), Number(url.searchParams.get("days") || 3)) });
}
function apiReturnDisposition(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  try {
    const r = logistics.returnDisposition(T(s), Number(id), String(body.disposition), body.extra || {});
    logAction(s, "logistics.return.disposition", "return", r.id, { disposition: body.disposition });
    json(res, 200, { return: r });
  } catch (e) { bad(res, e.message); }
}
function apiCarriers(req, res, url, s) {
  json(res, 200, { carriers: logistics.carriers(T(s)) });
}
/* ---- Payments & Financial services (disputes · retries · payouts · reconciliation · FX ledger) ---- */
function apiFinDisputes(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  const f = {}; if (url.searchParams.get("state")) f.state = url.searchParams.get("state");
  json(res, 200, { disputes: fin.disputes(T(s), f), states: require("./states.js").vocab("dispute") });
}
function apiFinDisputeOpen(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const d = fin.openDispute(T(s), body || {});
  logAction(s, "fin.dispute.open", "dispute", d.id, { payment: body.payment_id, amount: body.amount });
  json(res, 200, { dispute: fin.disputes(T(s), { state: d.state }).find(x => x.id === d.id) });
}
function apiFinDisputeStatus(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  try {
    const d = fin.transitionDispute(T(s), Number(id), String(body.state), body);
    logAction(s, "fin.dispute.transition", "dispute", d.id, { to: body.state });
    json(res, 200, { dispute: d });
  } catch (e) { bad(res, e.message); }
}
function apiFinRetry(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const p = fin.retry(T(s), Number(id), true);
  if (!p) return bad(res, "Unknown payment", 404);
  json(res, 200, { payment: p, attempts: fin.attempts(T(s), p.id) });
}
function apiFinPayouts(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  const t = T(s);
  const rows = all("SELECT * FROM payouts WHERE tenant_id=? ORDER BY id DESC LIMIT 200", t);
  json(res, 200, { payouts: rows.map(p => ({ ...p, items: fin.payoutItems(t, p.id).length })), kinds: fin.PAYOUT_KINDS });
}
function apiFinPayoutOpen(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const p = fin.openPayout(T(s), body.seller_id, body.kind, body.period, body.items || []);
  logAction(s, "fin.payout.open", "payout", p.id, { seller: body.seller_id, gross: p.gross });
  json(res, 200, { payout: p });
}
function apiFinPayoutDisburse(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  try {
    const p = fin.disbursePayout(T(s), Number(id));
    logAction(s, "fin.payout.disburse", "payout", p.id, { net: p.net });
    json(res, 200, { payout: p });
  } catch (e) { bad(res, e.message); }
}
function apiFinReconcile(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const b = fin.reconcile(T(s), body || {});
  logAction(s, "fin.recon.run", "recon", b.id, { lines: b.lines, unmatched: b.unmatched });
  json(res, 200, { batch: b, lines: fin.reconLines(T(s), b.id) });
}
/* a caller reads their OWN ledger; naming another owner (?owner=) is a staff action — a guest
   could read any customer's or seller's wallet history */
function apiFinLedger(req, res, url, s) {
  const staff = !!(s.platform_admin || isAdmin(s));
  const owner = staff && url.searchParams.get("owner") ? url.searchParams.get("owner") : ownerFor(s);
  const to = url.searchParams.get("to") || null;
  json(res, 200, { owner, entries: to ? fin.ledgerFx(T(s), owner, to) : fin.ledger(T(s), owner) });
}
/* ---- Marketplace & Seller ecosystem (ads · bidding · attribution · take-rate) ---- */
/* the full ad book (bids, budgets, spend) is staff data; shoppers see ads through ranking */
function apiMktAds(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  const f = {}; if (url.searchParams.get("status")) f.status = url.searchParams.get("status"); if (url.searchParams.get("seller")) f.seller_id = url.searchParams.get("seller");
  json(res, 200, { ads: marketplace.listAds(T(s), f), bid_models: marketplace.BID_MODELS, surfaces: marketplace.AD_SURFACES });
}
function apiMktAdCreate(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const a = marketplace.createAd(T(s), body || {});
  logAction(s, "mkt.ad.create", "ad", a.id, { name: body.name, model: body.bid_model });
  json(res, 200, { ad: a });
}
function apiMktRank(req, res, url, s) {
  const surface = url.searchParams.get("surface") || "search";
  const slots = Number(url.searchParams.get("slots") || 3);
  json(res, 200, { surface, slots, ranked: marketplace.rankAds(T(s), surface, slots) });
}
/* a shopper may only report a CLICK, once per ad per day — conversions are billed from the
   order pipeline, never declared by the client, and repeated clicks were billed every time */
const AD_EVENT_KINDS = require("./meta.js").AD_EVENT_KINDS;
function apiMktEvent(req, res, url, s, body, adId) {
  if (!s.user_id) return bad(res, "Sign in required", 401);
  /* which ad events a shopper may report is declared on the adEventKinds rows */
  const kinds = Array.isArray(rl("adEventKinds")) && rl("adEventKinds").length ? rl("adEventKinds") : AD_EVENT_KINDS;
  const self = kinds.filter(k => k.self_reported).map(k => k.key);
  const kind = String(body.kind || self[0] || "");
  if (!self.includes(kind) && !(s.platform_admin || isAdmin(s))) return bad(res, "Only " + self.join(" / ") + " events can be reported", 400);
  const ref = "u" + s.user_id + ":" + new Date().toISOString().slice(0, 10);
  const dup = get("SELECT id FROM ad_events WHERE tenant_id=? AND ad_id=? AND kind=? AND ref=?", T(s), Number(adId), kind, ref);
  if (dup) return json(res, 200, { event_id: dup.id, duplicate: true });
  const ev = marketplace.recordEvent(T(s), Number(adId), kind, (s.platform_admin || isAdmin(s)) && body.ref ? String(body.ref) : ref);
  json(res, 200, { event_id: ev });
}
function apiMktAttribute(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const r = marketplace.attribute(T(s), Number(body.order_id), Number(body.revenue) || 0, String(body.model || require("./defaults.js").of("mktAttribution")));
  json(res, 200, { attribution: r });
}
function apiMktSellerMetrics(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const period = url.searchParams.get("period") || "";
  const sellerId = Number(url.searchParams.get("seller")) || null;
  json(res, 200, { sellers: sellerId ? [marketplace.sellerMetrics(T(s), sellerId, period)] : marketplace.allSellerMetrics(T(s), period), period });
}
function apiMktSettle(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const r = marketplace.settleTakeRate(T(s), Number(body.seller_id), String(body.period || ""));
  logAction(s, "mkt.settle.take_rate", "seller", body.seller_id, { period: body.period, commission: r.metrics.commission });
  json(res, 200, r);
}
function apiProduct(req, res, url, s, body, id) {
  const c = CFG(s);
  const p = get("SELECT * FROM products WHERE tenant_id=? AND id=? AND lifecycle='published' AND deleted_at IS NULL", T(s), id);
  if (!p) return bad(res, "Product not found", 404);
  p.about = all("SELECT text FROM product_bullets WHERE tenant_id=? AND product_id=? ORDER BY pos", T(s), id).map(r => r.text);
  const revs = c.features.reviews ? ugc.listReviews(T(s), id) : [];
  const questions = c.features.qna ? ugc.listQuestions(T(s), id) : [];
  const ugcSummary = c.features.reviews || c.features.qna ? ugc.productUgc(T(s), id) : { reviews: 0, avg: 0, questions: 0 };
  const cm = commerceOf(s);
  const related = all("SELECT * FROM products WHERE tenant_id=? AND dept=? AND id!=? AND lifecycle='published' ORDER BY position LIMIT 12", T(s), p.dept, id).map(r => storeView({ ...r, about: [] }, cm));
  const skus = all("SELECT * FROM skus WHERE tenant_id=? AND product_id=? AND active=1", T(s), id).map(k => ({ ...k, identity: J(k.identity), variant: J(k.variant) }));
  const rels = all("SELECT * FROM relationships WHERE tenant_id=? AND from_id=?", T(s), id).map(r => ({ type: r.type, to: get("SELECT id,title,price,emoji,hue,stock,type FROM products WHERE tenant_id=? AND id=? AND lifecycle='published'", T(s), r.to_id) })).filter(r => r.to);
  const hist = r => { const five = Math.min(92, Math.max(45, Math.round((r - 3) * 30 + 40))); const four = Math.round((100 - five) * 0.5); const three = Math.round((100 - five - four) * 0.5); const two = Math.round((100 - five - four - three) * 0.5); return { 5: five, 4: four, 3: three, 2: two, 1: 100 - five - four - three - two }; };
  const node0 = p.node_id ? get("SELECT key FROM taxonomy WHERE id=?", p.node_id) : null;
  const ivk = (node0 ? String(node0.key) : "").split(".")[0] || (DEPT_TO_INDUSTRY || {})[p.dept] || p.dept;
  const prof = (rl("verticalTypeOf") || {})[ivk] || {}; const vctx = rl("verticalContexts") || {};
  /* the context dimensions are the registry's own keys, not the three the platform shipped
     with — an operator adding a dimension (a new context group in Data Studio) renders here
     and at checkout with no code change. A dimension the vertical's profile doesn't name
     degrades to empty rather than erroring; payment stays a set, tax/invoice a single key */
  const contexts = {};
  for (const g of Object.keys(vctx)) {
    if (!(g in prof)) { contexts[g] = []; continue; }
    const pv = prof[g];
    contexts[g] = (vctx[g] || []).filter(x => Array.isArray(pv) ? pv.includes(x.key) : x.key === pv);
  }
  /* localization + compliance + serialization + variant groups (universal model) */
  const locale = url.searchParams.get("locale") || cm.locale;
  const locRow = get("SELECT * FROM localizations WHERE tenant_id=? AND entity='product' AND ref_id=? AND locale=? AND active=1", T(s), id, locale);
  let pView = p, localized = false;
  if (locRow) {
    localized = true; pView = { ...p };
    if (locRow.name) pView.title = locRow.name;
    const bl = J(locRow.bullets, null); if (Array.isArray(bl) && bl.length) pView.about = bl;
    if (locRow.description) pView.seo = JSON.stringify({ ...J(pView.seo, {}), description: locRow.description });
  }
  const compliance = all("SELECT kind,code,issuer,jurisdiction,status,valid_from,valid_to,doc_media FROM compliance_records WHERE tenant_id=? AND scope='product' AND ref_id=? ORDER BY status,valid_to", T(s), id);
  const serRows = all("SELECT status, COUNT(*) n FROM serialized_items WHERE tenant_id=? AND product_id=? GROUP BY status", T(s), id);
  const serialized = serRows.length ? { total: serRows.reduce((n, r) => n + r.n, 0), by_status: serRows.reduce((o, r) => (o[r.status] = r.n, o), {}) } : null;
  const variant_groups = all("SELECT * FROM variant_groups WHERE tenant_id=? AND product_id=? AND active=1 ORDER BY position,id", T(s), id)
    .map(g => ({ id: g.id, name: g.name, axis: g.axis, attr_key: g.attr_key, options: all("SELECT id,code,name,price,stock,variant FROM skus WHERE tenant_id=? AND group_id=? AND active=1 ORDER BY id", T(s), g.id).map(k => ({ ...k, variant: J(k.variant, {}) })) }));
  const supplier_links = all("SELECT ps.id, ps.supplier_id, ps.supplier_sku, ps.price, ps.lead_days, ps.moq, ps.is_primary, ps.status, s.name supplier_name, s.party_role, s.country FROM product_suppliers ps JOIN suppliers s ON s.id=ps.supplier_id WHERE ps.tenant_id=? AND ps.product_id=? ORDER BY ps.is_primary DESC, ps.price ASC", T(s), id);
  const supplier = supplier_links.find(l => l.is_primary) || supplier_links[0] || null;
  const metaRow = get("SELECT tags, meta FROM entity_meta WHERE tenant_id=? AND entity='product' AND (ref_uid=? OR ref_uid=?)", T(s), p.uid || "", id);
  const tags = metaRow ? J(metaRow.tags, []) : [];
  const buyerEmail = s.user_id ? ((get("SELECT email FROM users WHERE id=?", s.user_id) || {}).email || "") : "";
  const buyerContract = contractPriceFor(T(s), buyerEmail, id, Number.MAX_SAFE_INTEGER);
  json(res, 200, { product: publicProduct(pView), histogram: hist(pView.rating), contexts, industry: ivk || null, reviews: revs.map(rv => ({ id: rv.id, name: rv.name, r: rv.rating, title: rv.title, body: rv.body, verified: !!rv.verified, date: rv.created_at, state: rv.state, helpful: rv.votes_helpful, votes: rv.votes_total, media: rv.media, replies: rv.replies })), questions, ugc: ugcSummary, related, fbt: related.slice(0, 3), skus, relationships: rels, node: p.node_id ? get("SELECT id,name,level FROM taxonomy WHERE id=?", p.node_id) : null, locale, localized, compliance, serialized, variant_groups, supplier: supplier || null, supplier_links, tags, contract_price: buyerContract != null ? money2(cm, buyerContract) : null });
}

/* ---------------- cart ---------------- */
function logisticsSurcharge(s, lines) {
  if (!require("./gates.js").on(T(s), "checkout.logistics_guard")) return 0;
  const cfg = mods.moduleConfig(T(s), "logistics-guard");
  /* each shipping class that costs extra declares the setting that prices it; a cart pays each
     class's surcharge once */
  const classes = (rl("shippingClasses") || []).filter(c => c && typeof c === "object" && c.surcharge);
  let fee = 0;
  for (const c of classes) if (lines.some(i => (i.logistics || {}).shippingClass === c.key)) fee += cfg[c.surcharge] != null ? Number(cfg[c.surcharge]) : Number(c.surcharge_default) || 0;
  return +fee.toFixed(2);
}
function computeTax(s, c, lines, goodsBase, otherTaxable) {
  return taxmod.computeLegacy({ perLine: require("./gates.js").on(T(s), "checkout.tax_per_line"), taxRate: c.commerce.taxRate, lines, goodsBase, otherTaxable });
}
function cartPayload(s) {
  const cm = commerceOf(s); const c = { ...CFG(s), commerce: cm };
  const owner = ownerFor(s);
  const buyerEmail = s.user_id ? ((get("SELECT email FROM users WHERE id=?", s.user_id) || {}).email || "") : "";
  const rows = all("SELECT product_id, qty, sku_id FROM cart_items WHERE owner=? ORDER BY added_at", owner);
  const items = []; let sub = 0, count = 0; const lines = []; const promoItems = [];
  for (const r of rows) {
    const p = get("SELECT * FROM products WHERE tenant_id=? AND id=?", T(s), r.product_id);
    if (!p) continue;
    p.about = all("SELECT text FROM product_bullets WHERE tenant_id=? AND product_id=? ORDER BY pos", T(s), p.id).map(x => x.text);
    const sku = r.sku_id ? get("SELECT id, code, name, price FROM skus WHERE id=? AND tenant_id=? AND active=1", r.sku_id, T(s)) : null;
    const cp = buyerEmail ? contractPriceFor(T(s), buyerEmail, p.id, r.qty) : null;
    const unit = cp != null ? cp : (sku && sku.price != null ? Number(sku.price) : effectivePrice(p, r.qty));
    items.push({ product: storeView(p, c.commerce), qty: r.qty, sku_id: sku ? sku.id : null, sku: sku ? { id: sku.id, code: sku.code, name: sku.name } : null, unit: money2(c.commerce, unit), unitBase: unit });
    lines.push({ unitBase: unit, qty: r.qty, logistics: J(p.logistics), tax_rule: J(p.tax_rule) });
    promoItems.push({ product: publicProduct(p), qty: r.qty });
    sub += unit * r.qty; count += r.qty;
  }
  const saved = all("SELECT product_id FROM saved_items WHERE owner=? ORDER BY added_at", owner)
    .map(r => { const p = get("SELECT * FROM products WHERE tenant_id=? AND id=?", T(s), r.product_id); if (!p) return null; p.about = []; return storeView(p, c.commerce); }).filter(Boolean);
  const promo = applyPromos(T(s), promoItems, s.coupon, { owner, currency: c.commerce.currency });
  /* an applied offer reports whether it grants free shipping (its type's handler decides) */
  const freeShip = promo.applied.some(a => a.freeShip);
  const afterPromo = Math.max(0, sub - promo.discount);
  const shipFee = afterPromo >= c.commerce.freeShipThreshold || freeShip ? 0 : (afterPromo > 0 ? c.commerce.shipFee : 0);
  const wBal = require("./gates.js").on(T(s), "checkout.wallet") ? mods.walletBalance(T(s), owner) : 0;
  const surcharge = logisticsSurcharge(s, lines);
  const gift = Math.min(wBal, afterPromo + shipFee + surcharge);
  const tax = computeTax(s, c, lines, afterPromo, shipFee + surcharge - gift);
  const total = +(afterPromo + shipFee + surcharge + tax - gift).toFixed(2);
  const m = c.commerce;
  return { items, saved, count, subBase: sub, sub: money2(m, sub), discountBase: promo.discount, discount: money2(m, promo.discount), creditsEarned: promo.credits || 0, redemptions: promo.redemptions || [], shipBase: shipFee, surchargeBase: surcharge, giftBase: gift, taxBase: tax, totalBase: total, promos: promo.applied, couponsOpen: !!(c.features && c.features.coupons) && !!sec.policy().provisioning.couponsAllowed, shipFee: money2(m, shipFee), gift: money2(m, gift), tax: money2(m, tax), total: money2(m, total), qualifies: afterPromo >= c.commerce.freeShipThreshold || freeShip, currency: { code: m.currency, symbol: m.symbol, decimals: m.decimals, fx: m.fx, base: m.baseCurrency, threshold: c.commerce.freeShipThreshold } };
}
function apiCartGet(req, res, url, s) { json(res, 200, cartPayload(s)); }
function apiCartAdd(req, res, url, s, body) {
  const c = CFG(s);
  /* only a published, live product can be added (an unpublished or trashed one could be bought) */
  const p = get("SELECT id, stock FROM products WHERE tenant_id=? AND id=? AND lifecycle='published' AND deleted_at IS NULL", T(s), body.id);
  if (!p) return bad(res, "Unknown product", 404);
  if (p.stock <= 0) return bad(res, "Item is sold out");
  let skuId = null;
  if (body.sku_id != null && body.sku_id !== "") { const sk = get("SELECT id FROM skus WHERE id=? AND product_id=? AND tenant_id=? AND active=1", Number(body.sku_id), p.id, T(s)); if (!sk) return bad(res, "Unknown variant for this product"); skuId = sk.id; }
  const owner = ownerFor(s);
  const qty = Math.max(1, Math.min(c.commerce.cartMaxQty, Number(body.qty) || 1));
  const ex = get("SELECT qty FROM cart_items WHERE owner=? AND product_id=?", owner, p.id);
  if (ex) run("UPDATE cart_items SET qty=?, sku_id=? WHERE owner=? AND product_id=?", Math.min(c.commerce.cartMaxQty, ex.qty + qty), skuId, owner, p.id);
  else run("INSERT INTO cart_items(owner,product_id,qty,sku_id) VALUES(?,?,?,?)", owner, p.id, qty, skuId);
  json(res, 200, cartPayload(s));
}
function apiCartPut(req, res, url, s, body) {
  const c = CFG(s);
  const owner = ownerFor(s);
  const qty = Number(body.qty);
  if (!(qty >= 1 && qty <= c.commerce.cartMaxQty)) return bad(res, "Invalid quantity");
  run("UPDATE cart_items SET qty=? WHERE owner=? AND product_id=?", qty, owner, body.id);
  json(res, 200, cartPayload(s));
}
function apiCartDel(req, res, url, s, body, id) {
  run("DELETE FROM cart_items WHERE owner=? AND product_id=?", ownerFor(s), id);
  json(res, 200, cartPayload(s));
}
function apiSavedAdd(req, res, url, s, body) {
  if (!CFG(s).features.saveForLater) return bad(res, "Save for later is disabled", 403);
  const owner = ownerFor(s);
  run("INSERT OR IGNORE INTO saved_items(owner,product_id) VALUES(?,?)", owner, body.id);
  run("DELETE FROM cart_items WHERE owner=? AND product_id=?", owner, body.id);
  json(res, 200, cartPayload(s));
}
function apiSavedDel(req, res, url, s, body, id) {
  run("DELETE FROM saved_items WHERE owner=? AND product_id=?", ownerFor(s), id);
  json(res, 200, cartPayload(s));
}
function apiSavedMove(req, res, url, s, body, id) {
  const owner = ownerFor(s);
  run("DELETE FROM saved_items WHERE owner=? AND product_id=?", owner, id);
  const ex = get("SELECT qty FROM cart_items WHERE owner=? AND product_id=?", owner, id);
  if (ex) run("UPDATE cart_items SET qty=qty+1 WHERE owner=? AND product_id=?", owner, id);
  else run("INSERT INTO cart_items(owner,product_id,qty) VALUES(?,?,1)", owner, id);
  json(res, 200, cartPayload(s));
}

/* ---------------- checkout (gateway-aware) ---------------- */
function planFor(tenantId) {
  const sub = get("SELECT p.* FROM subscriptions s JOIN plans p ON p.id=s.plan_id WHERE s.tenant_id=? AND s.status IN " + stIn("plan_subscription", "current").sql + " ORDER BY s.id DESC", tenantId, ...stIn("plan_subscription", "current").args);
  return sub || get("SELECT name, max_products, max_orders_month FROM plans ORDER BY position LIMIT 1") || { name: "none", max_products: 999999, max_orders_month: 999999 };
}
/* ---- what shipping costs: the store's fixed fee, or a live carrier rate ----
   commerce.shipRates = "live" prices the parcel with the connected carrier account from the
   store's ship-from address to the shopper's; anything else (or a carrier that cannot rate
   this address) charges the carrier's base fee / the store's flat fee. Free-shipping rules
   (threshold, a free-ship promotion, a membership perk) apply to either. */
function itemWeightKg(tid, productId, fallbackKg) {
  const p = get("SELECT attrs, vertical FROM products WHERE tenant_id=? AND id=?", tid, productId) || {};
  const a = J(p.attrs, {}), v = J(p.vertical, {});
  const kg = Number(a.weight_kg) || Number(v.weight_kg) || (Number(v.weight_g) ? Number(v.weight_g) / 1000 : 0) || (Number(a.weight_g) ? Number(a.weight_g) / 1000 : 0);
  return kg > 0 ? kg : fallbackKg;
}
const RATE_CACHE = new Map();
async function liveRates(tid, from, to, oz) {
  const key = tid + "|" + JSON.stringify(to) + "|" + oz;
  const hit = RATE_CACHE.get(key);
  if (hit && Date.now() - hit.at < 10 * 60000) return hit.q;
  const q = await shippingMod.getQuote(tid, { from, to, parcel: { weight_oz: oz } });
  if (!q.error) { RATE_CACHE.set(key, { at: Date.now(), q }); if (RATE_CACHE.size > 500) RATE_CACHE.delete(RATE_CACHE.keys().next().value); }
  return q;
}
async function shippingFor(s, c, cart, body) {
  const b = body || {};
  const subBase0 = +cart.items.reduce((n, x) => n + x.unitBase * x.qty, 0).toFixed(2);
  const cctx = ruleCtx(s, "checkout.carriers", { amount: subBase0 });
  const carriers = permittedCarriers(s, cctx);
  /* no carrier chosen → the store's own primary carrier (enabledCarriers is primary-first) */
  let carrier = b.carrier && carriers.some(x => x.id === String(b.carrier)) ? String(b.carrier) : (carriers[0] ? carriers[0].id : "");
  const carrierObj = carriers.find(x => x.id === carrier);
  const memBenefits = CFG(s).features.membership ? recurring.checkoutBenefits(T(s), ownerFor(s)) : { effects: [], bonus_pct: 0 };
  const free = !!(cart.qualifies || cart.promos.some(a => a.freeShip) || (memBenefits.effects || []).includes("free_shipping"));
  let shipBase = carrierObj ? (carrierObj.baseFee || c.commerce.shipFee) : c.commerce.shipFee;
  let eta = carrierObj && carrierObj.eta ? carrierObj.eta[1] : c.commerce.daysStandard;
  const out = { carrier, source: "fixed", rate: null, rates: [], shipmentId: null, note: null };
  const cm = c.commerce;
  const dest = { name: String(b.name || "").trim(), street1: String(b.address || "").trim(), city: String(b.city || "").trim(), state: String(b.state || "").trim(), zip: String(b.zip || "").trim(), country: String(cctx.country || cm.country || "").toUpperCase() };
  if (cm.shipRates === "live" && dest.street1 && dest.city && dest.zip) {
    const perItem = Number(cm.parcelWeightKg) > 0 ? Number(cm.parcelWeightKg) : settings.DEFAULTS.commerce.parcelWeightKg;
    const kg = cart.items.reduce((n, x) => n + itemWeightKg(T(s), x.product.id, perItem) * x.qty, 0);
    const oz = Math.min(2400, Math.max(0.1, +(kg * 35.274).toFixed(1)));
    const q = await liveRates(T(s), cm.shipFrom, dest, oz);
    if (q.error) out.note = q.error;
    else if (q.rates && q.rates.length) {
      const base = cm.baseCurrency;
      const rates = q.rates.map(r => ({ ...r, priceBase: +(r.price * (r.currency && base && r.currency !== base ? registry.fxTo(r.currency, base) : 1)).toFixed(2) }));
      const named = x => carrierObj && [carrierObj.id, carrierObj.name].some(n => String(n || "").toLowerCase() === String(x.carrier || "").toLowerCase());
      const pick = (b.rate_id && rates.find(x => x.id === String(b.rate_id))) || rates.filter(named).sort((x, y) => x.priceBase - y.priceBase)[0] || rates.slice().sort((x, y) => x.priceBase - y.priceBase)[0];
      shipBase = pick.priceBase; if (pick.days) eta = pick.days;
      const own = named(pick) ? carrierObj : carriers.find(x => [x.id, x.name].some(n => String(n || "").toLowerCase() === String(pick.carrier || "").toLowerCase()));
      carrier = own ? own.id : String(pick.carrier || "").toLowerCase();
      Object.assign(out, { carrier, source: "live", rate: pick, rates, shipmentId: q.shipment_id });
    } else out.note = "The carrier returned no rates for this address";
  }
  out.shipBase = free ? 0 : +Number(shipBase || 0).toFixed(2);
  out.eta = eta; out.free = free;
  return out;
}
function checkoutTotals(s, c, cart, shipFee) {
  const lines = cart.items.map(x => ({ unitBase: x.unitBase, qty: x.qty, logistics: x.product.logistics, tax_rule: x.product.tax_rule }));
  const subBase = +lines.reduce((n, l) => n + l.unitBase * l.qty, 0).toFixed(2);
  const netBase = +(subBase - (cart.discountBase || 0)).toFixed(2);
  const surcharge = logisticsSurcharge(s, lines);
  const wBal = require("./gates.js").on(T(s), "checkout.wallet") ? mods.walletBalance(T(s), ownerFor(s)) : 0;
  const giftUsed = Math.min(wBal, netBase + shipFee + surcharge);
  const tax = computeTax(s, c, lines, netBase, shipFee + surcharge - giftUsed);
  const total = +(netBase + shipFee + surcharge + tax - giftUsed).toFixed(2);
  return { lines, subBase, netBase, surcharge, giftUsed, tax, total };
}
/* the checkout page's summary, priced by the same code checkout charges with */
async function apiCheckoutQuote(req, res, url, s, body) {
  const c = { ...CFG(s), commerce: commerceOf(s) };
  const cart = cartPayload(s);
  if (!cart.items.length) return bad(res, "Bag is empty", 400);
  const ship = await shippingFor(s, c, cart, body || {});
  const t = checkoutTotals(s, c, cart, ship.shipBase);
  const m = c.commerce;
  json(res, 200, { carrier: ship.carrier, source: ship.source, note: ship.note, free: ship.free, eta: ship.eta,
    rate_id: ship.rate ? ship.rate.id : null,
    rates: ship.rates.map(r => ({ id: r.id, carrier: r.carrier, service: r.service, days: r.days, price: money2(m, r.priceBase) })),
    shipFee: money2(m, ship.shipBase), surcharge: money2(m, t.surcharge), gift: money2(m, t.giftUsed), tax: money2(m, t.tax), total: money2(m, t.total) });
}
/* one checkout per buyer at a time. The wallet balance and the cart are read before the
   (awaited) payment and written after it, so two concurrent checkouts both spent the same
   balance and the same cart. The lock serialises them; the wallet is also decremented
   relative to its current value rather than set to a stale absolute one. */
const CHECKOUT_LOCKS = new Set();
async function apiCheckout(req, res, url, s, body) {
  const key = T(s) + "|" + ownerFor(s);
  if (CHECKOUT_LOCKS.has(key)) return bad(res, "A checkout is already in progress for this bag", 409);
  CHECKOUT_LOCKS.add(key);
  try { return await apiCheckoutOnce(req, res, url, s, body); }
  finally { CHECKOUT_LOCKS.delete(key); }
}
async function apiCheckoutOnce(req, res, url, s, body) {
  const c = { ...CFG(s), commerce: commerceOf(s) };
  const cart = cartPayload(s);
  if (!cart.items.length) return bad(res, "Bag is empty", 400);
  if (require("./gates.js").setting(T(s), "checkout.login_required") === true && !s.user_id)
    return bad(res, require("./gates.js").message("checkout.login_required"), 403);
  const name = String(body.name || "").trim(), address = String(body.address || "").trim(), city = String(body.city || "").trim();
  if (!name || !address || !city) return bad(res, "Shipping address is incomplete", 422);
  const plan = planFor(T(s));
  const monthOrders = get("SELECT COUNT(*) c FROM orders WHERE tenant_id=? AND created_at >= date('now','start of month')", T(s)).c;
  if (monthOrders >= plan.max_orders_month) return bad(res, "Monthly order limit reached on the " + plan.name + " plan — upgrade to continue selling", 402);
  const gwId = String(body.gateway || "");
  const ship = await shippingFor(s, c, cart, body);
  const carrier = ship.carrier, shipFee = ship.shipBase, eta = ship.eta;
  const { netBase, surcharge, giftUsed, tax, total } = checkoutTotals(s, c, cart, shipFee);
  /* the gateway and method are decided with the whole context — the buyer's country, the
     service, the amount actually charged — so an amount-scoped rule (cash only under a limit)
     holds at the moment of payment, not just on the page that listed the options */
  const rctx = ruleCtx(s, "checkout.gateways", { amount: total });
  const svc = rules.decideAt("checkout.service", undefined, ruleCtx(s, "checkout.service", { amount: total }));
  if (!svc.ok) return bad(res, "This service is not available here — " + svc.reasons.join("; "), 403);
  const gw = permittedGateways(s, rctx).find(g => g.id === gwId);
  if (!gw) {
    const why = enabledGateways(T(s)).some(g => g.id === gwId) ? rules.decideAt("checkout.gateways", gwId, rctx).reasons.join("; ") : "";
    return bad(res, "Select a valid payment method available in your jurisdiction" + (why ? " — " + why : ""), 422);
  }
  const method = String(body.method || (gw.methods || ["card"])[0]);
  if (gw.methods && gw.methods.length && !gw.methods.includes(method)) return bad(res, "The payment method " + method + " is not available for this payment — " + rules.decideAt("checkout.methods", method, rctx).reasons.join("; "), 422);
  const num = `112-${Math.floor(1000000 + Math.random() * 8999999)}-${Math.floor(1000000 + Math.random() * 8999999)}`;
  const netSub = netBase;
  const m = c.commerce;
  const r = run(`INSERT INTO orders(tenant_id,owner,num,name,address,city,state,zip,ship_option,pay_method,sub,ship_fee,gift_used,tax,total,eta_days,status,currency,fx)
                 VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,'processing',?,?)`,
    T(s), ownerFor(s), num, name, address, city, String(body.state || ""), String(body.zip || s.zip), carrier, gw.id, money2(m, netSub), money2(m, shipFee), money2(m, giftUsed), money2(m, tax), money2(m, total), eta, m.currency, m.fx);
  const oid = Number(r.lastInsertRowid);
  /* a live rate the shopper paid for stays attached to the order, so staff buy that label */
  if (ship.rate && ship.shipmentId) run("UPDATE shipping_quotes SET order_id=? WHERE tenant_id=? AND shipment_ref=? AND order_id IS NULL", oid, T(s), String(ship.shipmentId));
  /* risk screening before payment capture: block refuses the order, hold lets it through for review */
  if (CFG(s).features.fraudScreen) {
    const u0 = s.user_id ? get("SELECT id, created_at FROM users WHERE id=? AND tenant_id=?", s.user_id, T(s)) : null;
    const ageDays = u0 ? (Date.now() - new Date(String(u0.created_at).replace(" ", "T")).getTime()) / 86400e3 : 999;
    const r0 = risk.screen(T(s), {
      owner: ownerFor(s), ip: ipOf(req), email: (s.user_id ? (get("SELECT email FROM users WHERE id=?", s.user_id) || {}).email : ""),
      amount: total, card: body.card || (gw.id + ":" + method), address: `${name}, ${address}, ${city} ${body.zip || ""}`,
      account_age_days: ageDays, bill_country: CFG(s).commerce.country.toUpperCase(), ship_country: CFG(s).commerce.country.toUpperCase(),
      ref: num
    });
    if (risk.effectOf(r0.decision) === "block") {
      run("DELETE FROM order_items WHERE order_id=?", oid);
      run("DELETE FROM orders WHERE id=?", oid);
      logAction(s, "risk.block", "risk_event", r0.id, { score: r0.score });
      return bad(res, "This order was blocked by our risk system. Please contact support if this is a mistake (ref " + r0.id + ")", 403);
    }
    if (risk.effectOf(r0.decision) === "hold") logAction(s, "risk.hold", "risk_event", r0.id, { score: r0.score });
    s.__risk = { id: r0.id, score: r0.score, decision: r0.decision };
  }
  for (const it of cart.items) run("INSERT INTO order_items(order_id,product_id,qty,price,sku_id) VALUES(?,?,?,?,?)", oid, it.product.id, it.qty, it.sku_id ? it.unit : it.product.p, it.sku_id || null);
  const sim = await settlePayment(T(s), gw, total, c.commerce.currency, num,
    { returnUrl: publicLink(req, s, "orders.html", { paid: num }) || "", cancelUrl: publicLink(req, s, "checkout.html", { cancelled: num }) || "" });
  run("INSERT INTO payments(tenant_id,kind,order_id,gateway,method,amount,currency,fee,status,txn_ref,live) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
    T(s), "order", oid, gw.id, method, total, c.commerce.currency, sim.fee, sim.status, sim.ref, sim.live ? 1 : 0);
  if (stIs("payment", sim.status, "failure")) { run("UPDATE orders SET status=? WHERE id=?", states.first("order", "aborted"), oid); return bad(res, "Payment was declined by the gateway: " + (sim.error || "declined"), 402); }
  /* a live payment not yet confirmed (the shopper still has to complete it on the provider's
     page, or the provider reports it pending): the order waits for the provider's webhook
     before anyone fulfils it */
  const awaitingPayment = !!(sim.live && stIs("payment", sim.status, "awaiting"));
  if (awaitingPayment) run("UPDATE orders SET status=? WHERE id=?", states.first("order", "awaiting_payment"), oid);
  const vtOf = rl("verticalTypeOf") || {}; const vctx = rl("verticalContexts") || {};
  /* the dimensions are declared by the registry (the keys of verticalContexts), so a context
     group an operator adds in Data Studio participates in checkout validation with no code
     change. Ordering by the registry's own key order keeps the verdict stable across boots. */
  const dims = Object.keys(vctx);
  const allow = {};
  const explicit = body.contexts || {}; const cErrs = [];
  for (const it of cart.items) {
    const node = it.product.node_id ? get("SELECT key FROM taxonomy WHERE id=?", it.product.node_id) : null;
    const ivk = (node ? String(node.key) : "").split(".")[0] || (DEPT_TO_INDUSTRY || {})[it.product.d] || it.product.d;
    const prof = vtOf[ivk] || {};
    const sets = {};
    for (const g of dims) { const pv = prof[g]; sets[g] = new Set(Array.isArray(pv) ? pv : (pv ? [pv] : [])); }
    for (const g of dims) {
      if (!sets[g].size) continue;
      allow[g] = !(g in allow) ? sets[g] : new Set([...allow[g]].filter(x => sets[g].has(x)));
      const want = String(explicit[g] || "");
      if (want && !sets[g].has(want)) cErrs.push(it.product.t.slice(0, 30) + ": " + g + " context " + want + " not valid for " + (ivk || "general"));
      if (want) { const def = (vctx[g] || []).find(x => x.key === want); if (def && def.type !== g) cErrs.push("context kind mismatch"); }
    }
  }
  const contexts = {};
  for (const g of dims) {
    const want = String(explicit[g] || "");
    if (want) contexts[g] = [want];
    else if (allow[g] && allow[g].size) contexts[g] = [[...allow[g]].sort()[0]];
  }
  if (cErrs.length) return bad(res, [...new Set(cErrs)].slice(0, 3).join("; "), 422);
  run("UPDATE orders SET contexts=? WHERE id=?", JSON.stringify(contexts), oid);
  run("DELETE FROM cart_items WHERE owner=?", ownerFor(s));
  run("UPDATE tenant_state SET coupon='' WHERE sid=? AND tenant_id=?", s.sid, T(s)); s.coupon = "";
  if (giftUsed > 0) mods.walletAdd(T(s), ownerFor(s), -giftUsed);
  try { offers.redeem({ tenantId: T(s), owner: ownerFor(s), channel: require("./defaults.js").of("offerChannels"), currency: c.commerce.currency }, { credits: cart.creditsEarned || 0, redemptions: cart.redemptions || [] }, { order_id: oid, order_num: num }); } catch (e) { console.error("offer redeem:", e.message); }
  logAction(s, "checkout.complete", "order", num, { gateway: gw.id, method, total, txn: sim.ref }, req);
  notify(T(s), `New order ${num}`, `${name} — ${total} ${c.commerce.currency} via ${gw.name}`);
  if (s.user_id) {
    const buyer = get("SELECT email FROM users WHERE id=? AND tenant_id=?", s.user_id, T(s));
    if (buyer && buyer.email) require("./mailer.js").deliver({ tenantId: T(s), channel: "email", to: buyer.email, kind: "order_confirmation",
      subject: `Order ${num} confirmed — ${s.tenant.name}`,
      text: `Thanks for your order, ${name}.\n\nOrder ${num}\nTotal: ${money2(m, total)} ${m.currency}\nPayment: ${gw.name} (${sim.status})\nShipping to: ${name}, ${address}, ${city}\nEstimated delivery: ${eta} days\n\n${cart.items.map(x => `${x.qty} × ${x.product.t}`).join("\n")}` });
  }
  try { run("UPDATE orders SET trace_id=? WHERE id=?", s.trace || null, oid); } catch (e) { }
  emitEvent(T(s), "order.created", { num, total: money2(m, total), currency: m.currency }, num);
  if (stIs("payment", sim.status, "settled")) emitEvent(T(s), "order.paid", { num, total: money2(m, total), txn_ref: sim.ref, gateway: gw.id }, num);
  json(res, 200, { order: { num, total: money2(m, total), currency: m.currency, fx: m.fx, sub: money2(m, netSub), discount: money2(m, cart.discountBase || 0), surcharge: money2(m, surcharge), promos: cart.promos, shipFee: money2(m, shipFee), shipping: { source: ship.source, carrier, service: ship.rate ? ship.rate.service : null, rate_id: ship.rate ? ship.rate.id : null }, tax: money2(m, tax), gift_used: money2(m, giftUsed), eta, contexts, gateway: gw.id, gateway_name: gw.name, txn_ref: sim.ref, payment_status: sim.status, payment_redirect: awaitingPayment && sim.redirect ? sim.redirect : null, date: new Date().toISOString(), addr: `${name}, ${address}, ${city}`, items: cart.items.map(x => ({ id: x.product.id, qty: x.qty, price: x.unit })) } });
}
function apiOrders(req, res, url, s) {
  const orders = all("SELECT * FROM orders WHERE owner=? ORDER BY created_at DESC", ownerFor(s));
  for (const o of orders) {
    o.items = all("SELECT product_id id, qty, price FROM order_items WHERE order_id=?", o.id).map(it => {
      const p = get("SELECT * FROM products WHERE tenant_id=? AND id=?", T(s), it.id);
      return { id: it.id, qty: it.qty, price: it.price, product: p ? publicProduct({ ...p, about: [] }) : null };
    });
    const pay = get("SELECT gateway, txn_ref, status FROM payments WHERE tenant_id=? AND order_id=?", T(s), o.id);
    if (pay) o.payment = pay;
    /* how the order shows is the machine's: its state's label, icon and tone — and an order
       past its delivery estimate that is neither void nor already fulfilled shows as the
       fulfilled state does */
    const late = Date.now() > new Date(String(o.created_at).replace(" ", "T")).getTime() + (o.eta_days || 5) * 864e5;
    o.display = states.display("order", !stIs("order", o.status, "void") && late && !stIs("order", o.status, "fulfilled") ? states.first("order", "fulfilled") : o.status);
  }
  json(res, 200, { orders });
}

/* ---------------- reviews / gifts / viewed ---------------- */
function apiReviewAdd(req, res, url, s, body, id) {
  if (!CFG(s).features.reviews) return bad(res, "Reviews are disabled", 403);
  if (!get("SELECT id FROM products WHERE tenant_id=? AND id=?", T(s), id)) return bad(res, "Unknown product", 404);
  const r = Math.max(1, Math.min(5, Number(body.rating) || 5));
  const name = s.user_id ? get("SELECT name FROM users WHERE id=?", s.user_id).name : "A customer";
  const media = CFG(s).ugc.reviewMedia && Array.isArray(body.media) ? body.media.slice(0, 5) : [];
  const out = ugc.addReview(T(s), id, ownerFor(s), name, { rating: r, title: body.title, body: body.body, media }, !!CFG(s).ugc.moderation);
  logAction(s, "review.create", "review", out.id, { rating: r, state: out.state });
  json(res, 200, { ok: true, id: out.id, state: out.state, moderated: !!CFG(s).ugc.moderation });
}
function apiReviewVote(req, res, url, s, body, id) {
  if (!CFG(s).features.reviews) return bad(res, "Reviews are disabled", 403);
  try {
    const v = ugc.vote(T(s), "review", id, ownerFor(s), String(body.dir || "up") === "down" ? "down" : "up");
    json(res, 200, v);
  } catch (e) { bad(res, e.message, 404); }
}
function apiReviewReply(req, res, url, s, body, id) {
  if (!CFG(s).ugc.reviewReplies) return bad(res, "Review replies are disabled", 403);
  if (!requireAdmin(s, res)) return;
  const a = actor(s);
  try { json(res, 200, { reply: ugc.replyReview(T(s), id, a[2] || "Store", s.platform_admin ? "platform" : "admin", body.body) }); }
  catch (e) { bad(res, e.message, 404); }
}
function apiReviewModerate(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  try {
    const rv = ugc.setReviewState(T(s), id, String(body.state || ""));
    logAction(s, "review.moderate", "review", id, { state: body.state });
    json(res, 200, { review: rv });
  } catch (e) { bad(res, e.message, 400); }
}
/* ---------------- Q&A ---------------- */
function apiQnaAsk(req, res, url, s, body, id) {
  if (!CFG(s).features.qna) return bad(res, "Questions & Answers are disabled", 403);
  if (!get("SELECT id FROM products WHERE tenant_id=? AND id=?", T(s), id)) return bad(res, "Unknown product", 404);
  const name = s.user_id ? get("SELECT name FROM users WHERE id=?", s.user_id).name : "A customer";
  const q = ugc.askQuestion(T(s), id, ownerFor(s), name, body.body || body.question, !!CFG(s).ugc.moderation);
  logAction(s, "qna.ask", "question", q.id, { product: id });
  json(res, 200, { ok: true, ...q, moderated: !!CFG(s).ugc.moderation });
}
function apiQnaAnswer(req, res, url, s, body, id) {
  if (!CFG(s).features.qna) return bad(res, "Questions & Answers are disabled", 403);
  const a = actor(s);
  /* a guest's actor name is their session id — never publish it; and a guest is a customer,
     not a "seller" badge */
  const role = s.platform_admin ? "platform" : (isAdmin(s) ? "admin" : "customer");
  const author = a[0] === "guest" ? "A customer" : (a[2] || "A customer");
  try {
    const an = ugc.answerQuestion(T(s), id, ownerFor(s), author, role, body.body, !!CFG(s).ugc.moderation);
    logAction(s, "qna.answer", "answer", an.id, { question: id });
    json(res, 200, { ok: true, ...an, moderated: !!CFG(s).ugc.moderation });
  } catch (e) { bad(res, e.message, 404); }
}
function apiQnaVote(req, res, url, s, body, id) {
  if (!CFG(s).features.qna) return bad(res, "Questions & Answers are disabled", 403);
  const entity = String(url.searchParams.get("kind") || "question") === "answer" ? "answer" : "question";
  try { json(res, 200, ugc.vote(T(s), entity, id, ownerFor(s), String(body.dir || "up") === "down" ? "down" : "up")); }
  catch (e) { bad(res, e.message, 404); }
}
function apiQnaModerate(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const kind = String(url.searchParams.get("kind") || "question") === "answer" ? "answer" : "question";
  try { json(res, 200, { row: ugc.setQnaState(T(s), kind, id, String(body.state || "")) }); }
  catch (e) { bad(res, e.message, 400); }
}

/* ---------------- support helpdesk ---------------- */
function apiSupportCreate(req, res, url, s, body) {
  if (!CFG(s).features.customerService) return bad(res, "Customer service is disabled", 403);
  const name = s.user_id ? (get("SELECT name FROM users WHERE id=?", s.user_id) || {}).name : String(body.name || "");
  const email = s.user_id ? (get("SELECT email FROM users WHERE id=?", s.user_id) || {}).email : String(body.email || "");
  if (!String(name || "").trim() || !String(email || "").trim()) return bad(res, "Name and email are required to open a case", 422);
  const t = helpdesk.openTicket(T(s), { name, email, owner: ownerFor(s), subject: body.subject, reason: body.reason, priority: body.priority, order_ref: body.order_ref, product_id: body.product_id, body: body.body });
  logAction(s, "support.ticket.create", "ticket", t.ref, { subject: t.subject });
  json(res, 200, { ticket: t });
}
function apiSupportList(req, res, url, s) {
  if (!CFG(s).features.customerService) return bad(res, "Customer service is disabled", 403);
  json(res, 200, { tickets: helpdesk.listTickets(T(s), { owner: ownerFor(s) }) });
}
function apiSupportGet(req, res, url, s, body, id) {
  if (!CFG(s).features.customerService) return bad(res, "Customer service is disabled", 403);
  const t = helpdesk.ticketById(require("./db.js"), T(s), Number(id));
  if (!t || t.owner !== ownerFor(s)) return bad(res, "Case not found", 404);
  /* customers never see internal notes */
  json(res, 200, { ticket: { ...t, notes: t.notes.filter(n => n.visibility !== "internal") } });
}
function apiSupportReply(req, res, url, s, body, id) {
  if (!CFG(s).features.customerService) return bad(res, "Customer service is disabled", 403);
  try {
    const t = helpdesk.ticketById(require("./db.js"), T(s), Number(id));
    if (!t || t.owner !== ownerFor(s)) return bad(res, "Case not found", 404);
    if (t.status === "closed") return bad(res, "This case is closed", 409);
    const n = helpdesk.reply(T(s), Number(id), t.owner_name, body.body, false, "customer");
    helpdesk.transition(require("./db.js"), T(s), Number(id), "pending");
    json(res, 200, { note: n });
  } catch (e) { bad(res, e.message, 400); }
}
function apiSupportCsat(req, res, url, s, body, id) {
  if (!CFG(s).features.customerService) return bad(res, "Customer service is disabled", 403);
  try {
    const t = helpdesk.ticketById(require("./db.js"), T(s), Number(id));
    if (!t || t.owner !== ownerFor(s)) return bad(res, "Case not found", 404);
    json(res, 200, { ticket: helpdesk.rateCsat(T(s), Number(id), body.score, body.comment) });
  } catch (e) { bad(res, e.message, 400); }
}
function apiAdminHdList(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { tickets: helpdesk.listTickets(T(s), { status: url.searchParams.get("status") || "", assignee: url.searchParams.get("assignee") || "" }), statuses: helpdesk.STATUSES, priorities: helpdesk.PRIORITIES });
}
function apiAdminHdGet(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const t = helpdesk.ticketById(require("./db.js"), T(s), Number(id));
  if (!t) return bad(res, "Case not found", 404);
  json(res, 200, { ticket: t });
}
function apiAdminHdUpdate(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  try {
    const D = require("./db.js");
    const t = helpdesk.transition(D, T(s), Number(id), String(body.status || "open"), body.assignee === undefined ? undefined : String(body.assignee || ""));
    if (body.priority) D.run("UPDATE tickets SET priority=? WHERE id=? AND tenant_id=?", String(body.priority), Number(id), T(s));
    logAction(s, "support.ticket.update", "ticket", t.ref, { status: t.status, assignee: t.assignee });
    json(res, 200, { ticket: helpdesk.ticketById(D, T(s), Number(id)) });
  } catch (e) { bad(res, e.message, 400); }
}
function apiAdminHdReply(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const a = actor(s);
  try {
    const n = helpdesk.reply(T(s), Number(id), a[2] || "Support", body.body, !!body.internal, s.platform_admin ? "platform" : "agent");
    logAction(s, "support.ticket.reply", "ticket", Number(id), { internal: !!body.internal });
    json(res, 200, { note: n });
  } catch (e) { bad(res, e.message, 400); }
}
function apiAdminHdSla(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { health: helpdesk.slaHealth(T(s)), agents: helpdesk.agentStats(T(s)) });
}

/* ---------------- address book ---------------- */
function apiAddressList(req, res, url, s) {
  json(res, 200, { addresses: all("SELECT * FROM addresses WHERE tenant_id=? AND owner=? ORDER BY is_default DESC, id", T(s), ownerFor(s)) });
}
function apiAddressSave(req, res, url, s, body, id) {
  const name = String(body.name || "").trim(), address = String(body.address || "").trim(), city = String(body.city || "").trim();
  if (!name || !address || !city) return bad(res, "Name, address and city are required", 422);
  const label = String(body.label || "Home").slice(0, 40);
  const isDefault = body.is_default ? 1 : 0;
  if (isDefault) run("UPDATE addresses SET is_default=0 WHERE tenant_id=? AND owner=?", T(s), ownerFor(s));
  if (id) {
    const ex = get("SELECT id FROM addresses WHERE id=? AND tenant_id=? AND owner=?", Number(id), T(s), ownerFor(s));
    if (!ex) return bad(res, "Address not found", 404);
    run("UPDATE addresses SET label=?,name=?,address=?,city=?,state=?,zip=?,country=?,phone=?,is_default=? WHERE id=?",
      label, name, address, city, String(body.state || "").slice(0, 60), String(body.zip || "").slice(0, 20),
      String(body.country || "").slice(0, 2).toUpperCase(), String(body.phone || "").slice(0, 30), isDefault, Number(id));
  } else {
    run("INSERT INTO addresses(tenant_id,owner,label,name,address,city,state,zip,country,phone,is_default) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
      T(s), ownerFor(s), label, name, address, city, String(body.state || "").slice(0, 60), String(body.zip || "").slice(0, 20),
      String(body.country || "").slice(0, 2).toUpperCase(), String(body.phone || "").slice(0, 30), isDefault);
  }
  json(res, 200, { addresses: all("SELECT * FROM addresses WHERE tenant_id=? AND owner=? ORDER BY is_default DESC, id", T(s), ownerFor(s)) });
}
function apiAddressDel(req, res, url, s, body, id) {
  run("DELETE FROM addresses WHERE id=? AND tenant_id=? AND owner=?", Number(id), T(s), ownerFor(s));
  json(res, 200, { ok: true });
}

/* ---------------- Subscribe & Save ---------------- */
function apiSubCreate(req, res, url, s, body) {
  if (!CFG(s).features.subscribeSave) return bad(res, "Subscribe & Save is disabled", 403);
  const pid = String(body.product_id || "");
  if (!get("SELECT id FROM products WHERE tenant_id=? AND id=?", T(s), pid)) return bad(res, "Unknown product", 404);
  const disc = Number(CFG(s).retention && CFG(s).retention.subDiscount) || 10;
  const sched = recurring.createSchedule(T(s), { owner: ownerFor(s), product_id: pid, sku_id: body.sku_id, qty: body.qty, frequency_days: body.frequency_days, discount_pct: disc, start_at: body.start_at });
  logAction(s, "subscription.create", "recurring_schedule", sched.id, { product: pid, freq: sched.frequency_days });
  json(res, 200, { schedule: sched, discount_pct: disc });
}
function apiSubList(req, res, url, s) {
  if (!CFG(s).features.subscribeSave) return bad(res, "Subscribe & Save is disabled", 403);
  json(res, 200, { schedules: recurring.listSchedules(T(s), ownerFor(s)) });
}
function apiSubControl(req, res, url, s, body, id) {
  if (!CFG(s).features.subscribeSave) return bad(res, "Subscribe & Save is disabled", 403);
  try {
    /* a customer controls only their own schedule; staff may act on any in their store */
    const sc = recurring.controlSchedule(T(s), Number(id), String(body.action || ""), (s.platform_admin || isAdmin(s)) ? null : ownerFor(s));
    logAction(s, "subscription." + body.action, "recurring_schedule", id);
    json(res, 200, { schedule: sc });
  } catch (e) { bad(res, e.message, 400); }
}
function apiAdminRecurring(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const due = recurring.dueSchedules(T(s));
  json(res, 200, {
    schedules: all("SELECT s.*, p.title product_title FROM recurring_schedules s LEFT JOIN products p ON p.tenant_id=s.tenant_id AND p.id=s.product_id WHERE s.tenant_id=? ORDER BY s.id DESC LIMIT 200", T(s)),
    due: due.length, statuses: recurring.SCHED_STATUSES, frequencies: recurring.FREQUENCIES
  });
}
function apiAdminRecurringProcess(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const due = recurring.dueSchedules(T(s));
  const processed = [];
  for (const sc of due) {
    try { processed.push({ id: sc.id, ok: true, ref: recurring.processCycle(T(s), sc.id, "RUN-" + new Date().toISOString().slice(0, 10)).cycles_completed }); }
    catch (e) { processed.push({ id: sc.id, ok: false, error: e.message }); }
  }
  logAction(s, "subscription.process", "recurring_schedule", processed.length, { processed: processed.length });
  json(res, 200, { processed, remaining: recurring.dueSchedules(T(s)).length });
}

/* ---------------- membership ---------------- */
function apiMembershipGet(req, res, url, s) {
  json(res, 200, { membership: recurring.membershipOf(T(s), ownerFor(s)), tiers: recurring.tiers() });
}
function apiMembershipSubscribe(req, res, url, s, body) {
  if (!CFG(s).features.membership) return bad(res, "Membership program is disabled", 403);
  try {
    const m = recurring.subscribeMembership(T(s), ownerFor(s), String(body.tier || ""));
    logAction(s, "membership.subscribe", "membership", m.tier, { tier: body.tier });
    json(res, 200, { membership: m });
  } catch (e) { bad(res, e.message, 400); }
}
function apiMembershipCancel(req, res, url, s) {
  if (!CFG(s).features.membership) return bad(res, "Membership program is disabled", 403);
  json(res, 200, { membership: recurring.cancelMembership(T(s), ownerFor(s)) });
}
function apiAdminMemberships(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { memberships: recurring.listMemberships(T(s)), tiers: recurring.tiers() });
}

/* ---------------- risk / fraud screening ---------------- */
function apiRiskScreen(req, res, url, s, body) {
  if (!CFG(s).features.fraudScreen) return bad(res, "Risk screening is disabled", 403);
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { event: risk.screen(T(s), body || {}) }); }
  catch (e) { bad(res, e.message, 400); }
}
function apiRiskBlocklist(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { email: risk.blocklist(T(s), "email"), card: risk.blocklist(T(s), "card"), address: risk.blocklist(T(s), "address"), ip: risk.blocklist(T(s), "ip") });
}
function apiRiskBlockAdd(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { list: risk.addBlock(T(s), String(body.kind || ""), body.value, body.note) }); }
  catch (e) { bad(res, e.message, 400); }
}
function apiRiskQueue(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { queue: risk.queue(T(s)), stats: risk.stats(T(s)), actions: risk.actionRows().map(r => r.key) });
}
function apiRiskResolve(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  try {
    const ev = risk.resolve(T(s), id, String(body.decision || ""), body.note);
    logAction(s, "risk.resolve", "risk_event", id, { decision: body.decision });
    json(res, 200, { event: ev });
  } catch (e) { bad(res, e.message, 400); }
}

/* ---------------- compliance & privacy (regulations as data) ---------------- */
function apiAdminComplianceStatus(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, compliance.evaluate(T(s)));
}
function apiAdminComplianceCatalog(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { regulations: compliance.catalog(), controls: compliance.controlsFor(T(s)) });
}
function apiAdminComplianceControl(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const out = compliance.setControl(T(s), String(body.regulation || ""), String(body.control_id || ""),
    String(body.status || ""), body.evidence, s.platform_admin ? ("platform:" + s.platform_admin.email) : ("admin:" + s.user_id));
  logAction(s, "compliance.control", "compliance_controls", body.regulation + ":" + body.control_id, out, req);
  json(res, out.ok ? 200 : 400, out);
}
function apiAdminComplianceEvidence(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { evidence: compliance.evidenceFor(T(s), url.searchParams.get("regulation"), url.searchParams.get("control_id")) });
}
/* the data subject's own consent record — the customer reads and edits their own
   lawful-basis state; an admin may act on behalf of a subject by email */
/* a data subject reads and changes ONLY their own consent; acting on someone else's record
   (`subject=`) is a staff action — it was open to anyone */
function consentSubject(s, requested) {
  if (requested && requested !== ownerFor(s) && !(s.platform_admin || isAdmin(s))) return null;
  return requested || ownerFor(s);
}
function apiConsentGet(req, res, url, s) {
  const asked = url.searchParams.get("subject");
  const subject = consentSubject(s, asked);
  if (asked && !subject) return bad(res, "You can only view your own consent", 403);
  if (!subject) return bad(res, "no subject in session", 401);
  json(res, 200, { subject, purposes: compliance.consentOf(T(s), subject) });
}
function apiConsentSet(req, res, url, s, body) {
  const asked = body && body.subject;
  const subject = consentSubject(s, asked);
  if (asked && !subject) return bad(res, "You can only change your own consent", 403);
  if (!subject) return bad(res, "no subject in session", 401);
  const out = compliance.grantConsent(T(s), subject, String(body.purpose || ""), {
    status: body.status, source: "api", ip: ipOf(req)
  });
  if (out.ok) logAction(s, "consent." + (stIs("consent", body.status, "withdrawal") ? "withdraw" : "grant"), "consent", subject + ":" + body.purpose, out, req);
  json(res, out.ok ? 200 : 400, out);
}
/* a data subject opens a rights request themselves (storefront) or an operator opens one */
function apiPrivacyRequestOpen(req, res, url, s, body) {
  const subject = (body && body.subject) || ownerFor(s);
  if (!subject) return bad(res, "no subject in session", 401);
  const out = compliance.openRequest(T(s), subject, String(body.kind || require("./defaults.js").of("privacyRequestKinds")), { actor: s.platform_admin ? "platform" : (ownerFor(s) || "subject") });
  json(res, out.ok ? 200 : 400, out);
}
function apiAdminPrivacyRequests(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { requests: compliance.requestsFor(T(s)), states: compliance.REQUEST_STATES, kinds: compliance.REQUEST_KINDS });
}
function apiAdminPrivacyRequestTransition(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const out = compliance.transitionRequest(T(s), String(id), String(body.status || ""), s.platform_admin ? ("platform:" + s.platform_admin.email) : ("admin:" + s.user_id), body.detail);
  logAction(s, "privacy.request", "privacy_requests", id, out, req);
  json(res, out.ok ? 200 : (out.code === 404 ? 404 : 409), out);
}
function apiAdminPrivacyRequestEvents(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  /* the request must belong to this store — events were read by request id alone */
  json(res, 200, { events: all("SELECT e.* FROM privacy_request_events e JOIN privacy_requests r ON CAST(r.id AS TEXT)=CAST(e.request_id AS TEXT) WHERE e.request_id=? AND r.tenant_id=? ORDER BY e.id", String(id), T(s)) });
}

/* ---------------- tenancy hierarchy (org → BU → brand → store → channel) ----------------
   Every node is data; the materialized path makes a subtree one LIKE away and the tree is
   the config cascade. Reads + writes are store-admin scoped to the session's own tenant, so
   an operator reorganises their own business and the platform sees the same shape via the
   generic cross-store reader. */
function apiTenancyTree(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const t = tenancy.tree(T(s)) || tenancy.root(T(s));
  json(res, 200, { tree: t, kinds: tenancy.KINDS });
}
function apiTenancyList(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { nodes: tenancy.list(T(s)) });
}
function apiTenancyCreate(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const out = tenancy.create(T(s), body || {});
  if (out.error) return bad(res, out.error, out.status || 400);
  logAction(s, "tenancy.create", "tenancy_node", out.path, out, req);
  json(res, 201, out);
}
function apiTenancyUpdate(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const out = tenancy.update(T(s), Number(id), body || {});
  if (out.error) return bad(res, out.error, out.status || 400);
  logAction(s, "tenancy.update", "tenancy_node", out.path, out, req);
  json(res, 200, out);
}
function apiTenancyDelete(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const out = tenancy.del(T(s), Number(id));
  if (out.error) return bad(res, out.error, out.status || 400);
  logAction(s, "tenancy.delete", "tenancy_node", id, out, req);
  json(res, 200, out);
}
/* resolve one config key up the cascade (Store → Brand → BU → Org → Tenant, deepest wins);
   the console's inspector shows an operator exactly which node a value came from */
function apiTenancyResolve(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const key = url.searchParams.get("key") || "";
  const node = tenancy.byId(T(s), Number(id)) || tenancy.root(T(s));
  if (!node) return bad(res, "no such node", 404);
  const chain = tenancy.chain(T(s), node.id);
  const perNode = chain.map(n => ({ id: n.id, path: n.path, kind: n.kind, value: key ? tenancy.getConfig(T(s), n.id, key) : n.config }));
  json(res, 200, { node, key, resolved: tenancy.resolve(T(s), node.id, key || null), chain: perNode });
}
function apiTenancyConfigSet(req, res, url, s, body, id, key) {
  if (!requireAdmin(s, res)) return;
  const out = tenancy.setConfig(T(s), Number(id), String(key || url.searchParams.get("key") || ""), body == null ? {} : body);
  if (out.error) return bad(res, out.error, out.status || 400);
  logAction(s, "tenancy.config", "tenancy_node", id, { key }, req);
  json(res, 200, out);
}

/* ---------------- the composition engine (Application = Capability Composition) ----------------
   The constitution's central claim made mechanical: compose() takes ANY declared capability
   and materializes its full application surface — data model, API, workflow, UI, dashboard,
   security — with no per-capability code. This surface is the platform's build tool: reads
   are open to a platform operator, and only a platform operator composes, because a composed
   capability becomes platform-wide machinery the moment it exists. */
function apiComposeCandidates(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  json(res, 200, compose.candidates());
}
function apiComposeManifest(req, res, url, s, body, key) {
  if (!requirePlatform(s, res)) return;
  const m = compose.manifest(String(key || ""));
  if (!m) return bad(res, "nothing composed for " + key, 404);
  json(res, 200, m);
}
function apiComposeLedger(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  json(res, 200, { ledger: compose.ledger() });
}
function apiCompose(req, res, url, s, body, key) {
  if (!requirePlatform(s, res)) return;
  const out = compose.compose(String(key || ""), body || {});
  if (!out.ok) return bad(res, out.error, 400);
  logAction(s, "compose.create", "composition", out.model.key, { capability: out.capability.label, source: out.capability.source }, req);
  json(res, 201, out);
}
function apiRecompose(req, res, url, s, body, key) {
  if (!requirePlatform(s, res)) return;
  const out = compose.recompose(String(key || ""));
  if (!out.ok) return bad(res, out.error, 400);
  logAction(s, "compose.recompose", "composition", out.model.key, { capability: out.capability.label }, req);
  json(res, 200, out);
}

/* ---------------- experimentation ---------------- */
function apiExpAssign(req, res, url, s, body, id) {
  if (!CFG(s).features.experiments) return bad(res, "Experiments are disabled", 403);
  const v = experiments.assign(T(s), String(id), ownerFor(s));
  json(res, 200, { variant: v });
}
function apiExpConvert(req, res, url, s, body, id) {
  if (!CFG(s).features.experiments) return bad(res, "Experiments are disabled", 403);
  json(res, 200, experiments.convert(T(s), String(id), ownerFor(s), body && body.value) || { ok: false });
}
function apiAdminExpList(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { experiments: experiments.listExperiments(T(s)), statuses: experiments.STATUSES });
}
function apiAdminExpCreate(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { experiment: experiments.createExperiment(T(s), body) }); }
  catch (e) { bad(res, e.message, 400); }
}
function apiAdminExpStatus(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { experiment: experiments.setStatus(T(s), id, String(body.status || "")) }); }
  catch (e) { bad(res, e.message, 400); }
}
function apiAdminExpResults(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const r = experiments.results(T(s), id);
  if (!r) return bad(res, "Experiment not found", 404);
  json(res, 200, r);
}

/* ---------------- supply-chain planning ---------------- */
function apiAdminPlanList(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const c = CFG(s);
  if (!c.features.planning) return bad(res, "Supply-chain planning is disabled", 403);
  json(res, 200, {
    replenishments: planning.listReplenishments(T(s), {
      status: url.searchParams.get("status") || "",
      priority: url.searchParams.get("priority") || "",
      product_id: url.searchParams.get("product_id") || "",
      q: url.searchParams.get("q") || ""
    }),
    stats: planning.summary(T(s)), statuses: planning.STATUSES, priorities: planning.PRIORITIES
  });
}
function apiAdminPlanRun(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  if (!CFG(s).features.planning) return bad(res, "Supply-chain planning is disabled", 403);
  const written = planning.runPlan(T(s));
  logAction(s, "planning.run", "replenishment", written.length, { skus: written.length });
  json(res, 200, { planned: written.length, stats: planning.summary(T(s)) });
}
function apiAdminPlanStatus(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  if (!CFG(s).features.planning) return bad(res, "Supply-chain planning is disabled", 403);
  try {
    const r = planning.setStatus(T(s), id, String(body.status || ""), body.po_ref);
    logAction(s, "planning.status", "replenishment", id, { status: body.status });
    json(res, 200, { replenishment: r });
  } catch (e) { bad(res, e.message, 400); }
}
function apiAdminPlanApproveAll(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  if (!CFG(s).features.planning) return bad(res, "Supply-chain planning is disabled", 403);
  const approved = planning.approveAll(T(s));
  logAction(s, "planning.approveAll", "replenishment", approved.length, { approved: approved.length });
  json(res, 200, { approved: approved.length, stats: planning.summary(T(s)) });
}
function apiAdminPlanPos(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  if (!CFG(s).features.planning) return bad(res, "Supply-chain planning is disabled", 403);
  json(res, 200, { purchaseOrders: planning.purchaseOrders(T(s)) });
}

/* ---------------- E17 · the mobility universe ---------------- */
/* The gate is the capability atom, never a settings flag: `cap(t,"ride_hailing")`
   answers {} when the atom is off, so the whole surface refuses at once. Every value
   an operator tunes is a param the engine already read — no handler here carries a
   rate, a radius or a fee (Architecture3 §2.1). */
function mobOn(s, key) {
  const c = caps.cap(T(s), key);
  return c && Object.keys(c).length ? c : null;
}
function apiMobilityGet(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  if (!mobOn(s, "ride_hailing")) return bad(res, "Ride hailing is not enabled for this store", 403);
  json(res, 200, {
    rides: mobility.listRides(T(s), {
      status: url.searchParams.get("status") || "",
      driver_id: url.searchParams.get("driver_id") || "",
      q: url.searchParams.get("q") || ""
    }),
    drivers: mobility.listDrivers(T(s), {
      status: url.searchParams.get("dstatus") || "",
      vehicle_kind: url.searchParams.get("kind") || ""
    }),
    zones: mobility.listZones(T(s)),
    vehicles: mobility.listVehicles(T(s)),
    stats: mobility.summary(T(s)),
    statuses: require("./states.js").vocab("ride"), vehicleKinds: mobility.vehicleKinds()
  });
}
function apiMobilityRide(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  if (!mobOn(s, "ride_hailing")) return bad(res, "Ride hailing is not enabled for this store", 403);
  try {
    const r = mobility.requestRide(T(s), body.rider, body.rider_phone, body.pickup, body.dropoff,
      body.vehicle_kind, body.payment_method, body.pickup_lat != null ? Number(body.pickup_lat) : null,
      body.pickup_lng != null ? Number(body.pickup_lng) : null);
    logAction(s, "mobility.ride.request", "ride", r.id, { ref: r.ref });
    json(res, 200, { ride: r });
  } catch (e) { bad(res, e.message, 400); }
}
function apiMobilityRideStatus(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  if (!mobOn(s, "ride_hailing")) return bad(res, "Ride hailing is not enabled for this store", 403);
  try {
    const r = mobility.updateRide(T(s), id, String(body.status || ""), body.note || "");
    logAction(s, "mobility.ride.status", "ride", id, { status: body.status });
    json(res, 200, { ride: r });
  } catch (e) { bad(res, e.message, 400); }
}
function apiMobilityRate(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  if (!mobOn(s, "ride_hailing")) return bad(res, "Ride hailing is not enabled for this store", 403);
  try {
    json(res, 200, mobility.rateRide(T(s), id, body.rating));
  } catch (e) { bad(res, e.message, 400); }
}
function apiMobilityDriver(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  if (!mobOn(s, "fleet_management")) return bad(res, "Fleet management is not enabled for this store", 403);
  try {
    const d = mobility.upsertDriver(T(s), body);
    logAction(s, "mobility.driver.save", "driver", d.id, { name: d.name });
    json(res, 200, { driver: d });
  } catch (e) { bad(res, e.message, 400); }
}
function apiMobilityDriverToggle(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  if (!mobOn(s, "fleet_management")) return bad(res, "Fleet management is not enabled for this store", 403);
  try {
    json(res, 200, { driver: mobility.toggleDriver(T(s), id, body.online !== false && body.online !== 0) });
  } catch (e) { bad(res, e.message, 400); }
}
function apiMobilityDriverDeactivate(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  if (!mobOn(s, "fleet_management")) return bad(res, "Fleet management is not enabled for this store", 403);
  try {
    logAction(s, "mobility.driver.deactivate", "driver", id, {});
    json(res, 200, mobility.deactivateDriver(T(s), id));
  } catch (e) { bad(res, e.message, 400); }
}
function apiMobilityVehicle(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  if (!mobOn(s, "fleet_management")) return bad(res, "Fleet management is not enabled for this store", 403);
  try {
    const v = mobility.upsertVehicle(T(s), body);
    logAction(s, "mobility.vehicle.save", "vehicle", v.id, { plate: v.plate });
    json(res, 200, { vehicle: v });
  } catch (e) { bad(res, e.message, 400); }
}
function apiMobilityZone(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  if (!mobOn(s, "dynamic_pricing")) return bad(res, "Dynamic pricing is not enabled for this store", 403);
  try {
    const z = mobility.upsertZone(T(s), body);
    logAction(s, "mobility.zone.save", "surge_zone", z.id, { name: z.name });
    json(res, 200, { zone: z });
  } catch (e) { bad(res, e.message, 400); }
}

/* ---------------- E18 · the operations universe ---------------- */
/* The gate is always the capability atom. Each handler answers 403 until the store
   composes the atom, and every value the engine used is a param it already read —
   no tax rate, threshold, yield or cost rate lives in this file. */
function opsOn(s, key) {
  const c = caps.cap(T(s), key);
  return c && Object.keys(c).length ? c : null;
}
function apiOpsGet(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const q = k => url.searchParams.get(k) || "";
  const out = { stats: {}, employees: [], attendance: [], requests: [], workOrders: [], projects: [], tasks: [], approvals: [], payroll: [] };
  if (opsOn(s, "workforce")) {
    out.employees = operations.listEmployees(T(s), { status: q("estatus"), department: q("dept"), q: q("q") });
    out.attendance = operations.attendanceSummary(T(s), q("from"), q("to"));
    out.payroll = all("SELECT * FROM payroll_runs WHERE tenant_id=? ORDER BY id DESC LIMIT 24", T(s));
    out.stats.payroll = operations.payrollSummary(T(s));
  }
  if (opsOn(s, "procurement")) {
    out.requests = operations.listRequests(T(s), { status: q("prstatus"), q: q("q") });
    out.stats.procurement = { open: out.requests.filter(r => !stIs("purchase_request", r.status, "terminal")).length };
  }
  if (opsOn(s, "manufacturing")) {
    out.workOrders = operations.listWorkOrders(T(s), { status: q("wostatus"), q: q("q") });
    out.stats.manufacturing = { open: out.workOrders.filter(w => !["done", "scrapped"].includes(w.status)).length };
  }
  if (opsOn(s, "projects")) {
    out.projects = operations.listProjects(T(s), { status: q("pstatus"), q: q("q") });
    out.tasks = operations.listTasks(T(s), q("project_id"));
    out.approvals = operations.listApprovals(T(s), { status: q("astatus"), kind: q("akind") });
    out.stats.projects = { active: out.projects.filter(p => stIs("project", p.status, "running")).length };
  }
  json(res, 200, out);
}
function apiOpsEmployee(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  if (!opsOn(s, "workforce")) return bad(res, "HRMS & payroll is not enabled for this store", 403);
  try {
    const e = operations.upsertEmployee(T(s), body);
    logAction(s, "ops.employee.save", "employee", e.id, { code: e.code });
    json(res, 200, { employee: e });
  } catch (e2) { bad(res, e2.message, 400); }
}
function apiOpsAttendance(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  if (!opsOn(s, "workforce")) return bad(res, "HRMS & payroll is not enabled for this store", 403);
  try {
    const a = operations.markAttendance(T(s), body.employee_id, String(body.date || ""), String(body.status || "present"), body.check_in, body.check_out);
    json(res, 200, { attendance: a });
  } catch (e2) { bad(res, e2.message, 400); }
}
function apiOpsPayrollRun(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  if (!opsOn(s, "workforce")) return bad(res, "HRMS & payroll is not enabled for this store", 403);
  try {
    const period = String(body.period || new Date().toISOString().slice(0, 7));
    const r = operations.runPayroll(T(s), period);
    logAction(s, "ops.payroll.run", "payroll_run", r.id, { period: r.period, headcount: r.headcount });
    json(res, 200, { run: r });
  } catch (e2) { bad(res, e2.message, 400); }
}
function apiOpsPayrollStatus(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  if (!opsOn(s, "workforce")) return bad(res, "HRMS & payroll is not enabled for this store", 403);
  try {
    const r = operations.setPayrollStatus(T(s), id, String(body.status || ""));
    logAction(s, "ops.payroll.status", "payroll_run", id, { status: body.status });
    json(res, 200, { run: r });
  } catch (e2) { bad(res, e2.message, 400); }
}
function apiOpsRequest(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  if (!opsOn(s, "procurement")) return bad(res, "Procurement is not enabled for this store", 403);
  try {
    const r = operations.upsertRequest(T(s), body);
    logAction(s, "ops.pr.save", "purchase_request", r.id, { ref: r.ref });
    json(res, 200, { request: r });
  } catch (e2) { bad(res, e2.message, 400); }
}
function apiOpsRequestAdvance(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  if (!opsOn(s, "procurement")) return bad(res, "Procurement is not enabled for this store", 403);
  try {
    const r = operations.advanceRequest(T(s), id, String(body.status || ""), s.email || s.name || "console");
    logAction(s, "ops.pr.advance", "purchase_request", id, { status: body.status });
    json(res, 200, { request: r });
  } catch (e2) { bad(res, e2.message, 400); }
}
function apiOpsWorkOrder(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  if (!opsOn(s, "manufacturing")) return bad(res, "Manufacturing is not enabled for this store", 403);
  try {
    const w = operations.upsertWorkOrder(T(s), body);
    logAction(s, "ops.wo.save", "work_order", w.id, { ref: w.ref });
    json(res, 200, { workOrder: w });
  } catch (e2) { bad(res, e2.message, 400); }
}
function apiOpsWorkOrderComplete(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  if (!opsOn(s, "manufacturing")) return bad(res, "Manufacturing is not enabled for this store", 403);
  try {
    const r = operations.completeWorkOrder(T(s), id);
    logAction(s, "ops.wo.complete", "work_order", id, r);
    json(res, 200, r);
  } catch (e2) { bad(res, e2.message, 400); }
}
function apiOpsProject(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  if (!opsOn(s, "projects")) return bad(res, "Projects is not enabled for this store", 403);
  try {
    const p = operations.upsertProject(T(s), body);
    logAction(s, "ops.project.save", "project", p.id, { code: p.code });
    json(res, 200, { project: p });
  } catch (e2) { bad(res, e2.message, 400); }
}
function apiOpsTask(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  if (!opsOn(s, "projects")) return bad(res, "Projects is not enabled for this store", 403);
  try {
    const t = operations.upsertTask(T(s), body);
    logAction(s, "ops.task.save", "task", t.id, { title: t.title });
    json(res, 200, { task: t });
  } catch (e2) { bad(res, e2.message, 400); }
}
function apiOpsTime(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  if (!opsOn(s, "projects")) return bad(res, "Projects is not enabled for this store", 403);
  try {
    json(res, 200, { task: operations.logTime(T(s), id, body.hours) });
  } catch (e2) { bad(res, e2.message, 400); }
}
function apiOpsApprovalDecide(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  if (!opsOn(s, "projects")) return bad(res, "Projects is not enabled for this store", 403);
  try {
    const a = operations.decideApproval(T(s), id, String(body.status || ""), s.email || s.name || "console", body.note);
    logAction(s, "ops.approval.decide", "approval", id, { status: body.status });
    json(res, 200, { approval: a });
  } catch (e2) { bad(res, e2.message, 400); }
}
/* S4: this used to credit body.amount without ever looking at a code — a
   customer could top up their own wallet indefinitely. Redeem goes through the
   same validation the fintech voucher path uses: the code must resolve to an
   issued row for this tenant, and marking it redeemed is what authorises the
   credit. */
function apiGiftAdd(req, res, url, s, body) {
  const c = CFG(s);
  if (!c.features.giftCards) return bad(res, "Gift cards are disabled", 403);
  if (!require("./gates.js").on(T(s), "checkout.wallet")) return bad(res, require("./gates.js").message("checkout.wallet"), 403);
  if (!body.code) return bad(res, "A gift card code is required", 400);
  try {
    const voucher = fintech.redeemVoucher(T(s), String(body.code || "").trim(), mods.ownerFor(s));
    json(res, 200, { ok: true, voucher, balance: mods.walletBalance(T(s), mods.ownerFor(s)) });
  } catch (e) { bad(res, e.message, 400); }
}
function apiViewed(req, res, url, s, body) {
  const owner = ownerFor(s);
  run("INSERT OR REPLACE INTO view_history(owner,product_id,seen_at) VALUES(?,?,datetime('now'))", owner, body.id);
  const ids = all("SELECT product_id FROM view_history WHERE owner=? ORDER BY seen_at DESC LIMIT 12", owner).map(r => r.product_id);
  /* L8: the ids came from the DB, but interpolating them into SQL contradicts the "parameterized
     SQL only" rule and is exactly the shape that becomes an injection later — bind them. */
  if (ids.length) {
    const marks = ids.map(() => "?").join(",");
    run(`DELETE FROM view_history WHERE owner=? AND product_id NOT IN (${marks})`, owner, ...ids);
  }
  json(res, 200, { ok: true, viewed: ids });
}

/* ================= DEMO HINTS (data-driven, no hardcoded creds; password shown only if it verifies) ================= */
function platSetting(key, dflt) { try { const r = get("SELECT value FROM platform_settings WHERE key=?", key); return r ? J(r.value, dflt) : dflt; } catch (e) { return dflt; } }
/* login-screen demo hints. They reveal a password ONLY when an account still uses one of the
   published seed defaults (which the README already documents), never a password an operator
   chose, and never in production — where the prod credential guard has already forced real
   passwords and a hint has nothing legitimate to show. */
const DEMO_DEFAULT_PASSWORDS = ["platform123", "admin123", "aurum123", "velora123", "demo123"];
function hintsAllowed() {
  return process.env.NODE_ENV !== "production" && sec.policy().demoHints && platSetting("demo_hint", { enabled: true }).enabled;
}
async function firstMatching(cands, check) { for (const c of cands) if (await check(c)) return c; return null; }
async function apiPlatformHint(req, res) {
  if (!hintsAllowed()) return json(res, 200, { demo: false });
  const h = platSetting("demo_hint", { enabled: true, platformEmail: "platform@luxora.shop" });
  const email = String(h.platformEmail || "");
  const pw = await firstMatching(DEMO_DEFAULT_PASSWORDS, c => verifyPlatformAdminAsync(email, c));
  if (!pw) return json(res, 200, { demo: false });
  json(res, 200, { demo: true, email, password: pw });
}
async function apiHint(req, res, url, s) {
  if (!hintsAllowed()) return json(res, 200, { demo: false });
  const adm = get("SELECT email FROM users WHERE tenant_id=? AND role='admin' ORDER BY id LIMIT 1", T(s));
  if (!adm) return json(res, 200, { demo: true, email: null });
  const pw = await firstMatching(DEMO_DEFAULT_PASSWORDS, c => verifyUserAsync(T(s), adm.email, c));
  /* the admin's address is shown only alongside a still-default password — a store whose
     admin has set their own password is not advertising who administers it */
  if (!pw) return json(res, 200, { demo: false });
  json(res, 200, { demo: true, email: adm.email, password: pw, store: s.tenant.slug });
}

/* ================= MODULE MARKETPLACE (everything is a product) ================= */
/* store-facing marketplace: the store itself purchases modules */
function apiMarket(req, res, url, s) {
  const modules = all("SELECT id,name,category,summary,price,manifest,status FROM modules WHERE status IN " + stIn("module", "listed").sql + " ORDER BY position", ...stIn("module", "listed").args).map(m => ({ id: m.id, name: m.name, category: m.category, summary: m.summary, price: m.price, capabilities: (J(m.manifest, {}).capabilities || []), fields: (J(m.manifest, {}).fields || []) }));
  json(res, 200, { modules, installed: mods.installed(T(s)).map(m => ({ id: m.module_id, capabilities: (m.manifest.capabilities || []), config: m.config })) });
}
function apiModulePurchase(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const m = mods.moduleRow(String(body.module_id || ""));
  if (!m || !stIs("module", m.status, "listed")) return bad(res, "Unknown module", 404);
  let invoice = null;
  const was = (mods.installedRow(T(s), m.id) || {}).status === "installed";
  if (!was && m.price > 0) {
    const number = "MOD-" + (1000 + get("SELECT COUNT(*) c FROM invoices").c + 1);
    /* the module is billed on account: an OPEN invoice the store owes (dunning applies). It
       used to be written as already paid, with a fabricated captured payment. */
    run("INSERT INTO invoices(tenant_id,number,period_start,period_end,amount,currency,status,note) VALUES(?,?,date('now'),date('now'),?,?,'draft',?)", T(s), number, m.price, m.currency || require("./defaults.js").platformCurrency(), "Module: " + m.name);
    invoice = number;
  }
  mods.applyModule(T(s), m, body.config || {});
  logAction(s, "module.purchase", "tenant_module", T(s) + ":" + m.id, { invoice }, req);
  json(res, 200, { ok: true, invoice });
}
function apiModuleRelease(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const m = mods.moduleRow(String(body.module_id || "")); if (!m) return bad(res, "Unknown module", 404);
  /* the module that provides the wallet point cannot be released while the point is live */
  if (require("./gates.js").on(T(s), "checkout.wallet") && require("./gates.js").provides(m, "checkout.wallet")) return bad(res, require("./gates.js").row("checkout.wallet").live_state || require("./gates.js").message("checkout.wallet"), 409);
  mods.unapplyModule(T(s), m);
  logAction(s, "module.release", "tenant_module", T(s) + ":" + m.id, {}, req);
  json(res, 200, { ok: true });
}

function apiPlatformModules(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const modules = all("SELECT * FROM modules ORDER BY position").map(m => ({ ...m, manifest: J(m.manifest, {}) }));
  const installs = all("SELECT tenant_id, module_id, status, config, installed_at FROM tenant_modules");
  json(res, 200, { modules, installs, tenants: all("SELECT id, slug, name FROM tenants ORDER BY id") });
}
function apiModuleInstall(req, res, url, s, body, id) {
  if (!requirePlatformSection(s, res, "modules", "write")) return;
  const m = mods.moduleRow(id);
  if (!m || !stIs("module", m.status, "listed")) return bad(res, "Unknown module", 404);
  const tid = Number(body.tenant_id);
  if (!get("SELECT id FROM tenants WHERE id=?", tid)) return bad(res, "Unknown store", 404);
  let invoice = null;
  const wasInstalled = (mods.installedRow(tid, id) || {}).status === "installed";
  if (!wasInstalled && m.price > 0) {
    const number = "MOD-" + (1000 + get("SELECT COUNT(*) c FROM invoices").c + 1);
    const r = run("INSERT INTO invoices(tenant_id,number,period_start,period_end,amount,currency,status,paid_at,note) VALUES(?,?,date('now'),date('now'),?,?,'paid',datetime('now'),?)",
      tid, number, m.price, m.currency || require("./defaults.js").platformCurrency(), `Module: ${m.name}`);
    run("INSERT INTO payments(tenant_id,kind,invoice_id,gateway,method,amount,currency,fee,status,txn_ref) VALUES(?,?,?,?,?,?,?,?,?,?)",
      tid, "module", Number(r.lastInsertRowid), "platform-billing", "invoice", m.price, m.currency || require("./defaults.js").platformCurrency(), 0, "captured", `mod_sim_${crypto.randomBytes(6).toString("hex")}`);
    invoice = number;
  }
  const cfg = Object.assign({}, body.config || {});
  mods.applyModule(tid, m, cfg);
  audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "module.install", "tenant_module", `${tid}:${id}`, { invoice }, ipOf(req));
  json(res, 200, { ok: true, module: id, invoice });
}
function apiModuleUninstall(req, res, url, s, body, id) {
  if (!requirePlatformSection(s, res, "modules", "write")) return;
  const m = mods.moduleRow(id); if (!m) return bad(res, "Unknown module", 404);
  mods.unapplyModule(Number(body.tenant_id), m);
  audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "module.uninstall", "tenant_module", `${body.tenant_id}:${id}`, {}, ipOf(req));
  json(res, 200, { ok: true });
}
function apiModuleConfigure(req, res, url, s, body, id) {
  if (!requirePlatformSection(s, res, "modules", "write")) return;
  const m = mods.moduleRow(id); if (!m) return bad(res, "Unknown module", 404);
  const tid = Number(body.tenant_id);
  run("UPDATE tenant_modules SET config=? WHERE tenant_id=? AND module_id=?", JSON.stringify(body.config || {}), tid, id);
  mods.applyModule(tid, m, body.config || {});
  audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "module.configure", "tenant_module", `${tid}:${id}`, { config: Object.keys(body.config || {}) }, ipOf(req));
  json(res, 200, { ok: true });
}
function apiStoreModules(req, res, url, s) {
  json(res, 200, { installed: mods.installed(T(s)).map(m => ({ id: m.module_id, name: m.name, category: m.category, capabilities: (m.manifest.capabilities || []), config: m.config, installed_at: m.installed_at })), capabilities: [...mods.caps(T(s))].filter(c => mods.hasCap(T(s), c)), gates: require("./gates.js").all(T(s)) });
}
function apiSeoSitemap(req, res, url, s) {
  if (!require("./gates.js").on(T(s), "seo.tools")) return bad(res, require("./gates.js").message("seo.tools"), 403);
  const prods = all("SELECT id FROM products WHERE tenant_id=? AND lifecycle='published'", T(s)).map(r => `  <url><loc>/product.html?id=${r.id}</loc></url>`).join("\n");
  const deps = all("SELECT key FROM departments WHERE tenant_id=? AND active=1", T(s)).map(r => `  <url><loc>/results.html?dept=${r.key}</loc></url>`).join("\n");
  res.writeHead(200, { "Content-Type": "application/xml; charset=utf-8" });
  res.end(`<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url><loc>/</loc></url>\n${deps}\n${prods}\n</urlset>`);
}
function apiReco(req, res, url, s, body, id) {
  if (!require("./gates.js").on(T(s), "reco.engine")) return bad(res, require("./gates.js").message("reco.engine"), 403);
  let rows = all(`SELECT DISTINCT p.* FROM order_items oi
    JOIN order_items oi2 ON oi.order_id = oi2.order_id
    JOIN orders o ON o.id = oi.order_id AND o.tenant_id = ?
    JOIN products p ON p.tenant_id = o.tenant_id AND p.id = oi2.product_id
    WHERE oi.product_id = ? AND oi2.product_id != ? AND p.lifecycle='published' LIMIT 12`, T(s), id, id);
  if (rows.length < 4) {
    const cur = get("SELECT dept FROM products WHERE tenant_id=? AND id=?", T(s), id);
    rows = all("SELECT * FROM products WHERE tenant_id=? AND dept=? AND id!=? AND lifecycle='published' ORDER BY ratings_count DESC LIMIT 12", T(s), cur ? cur.dept : "", id);
  }
  const cm = commerceOf(s);
  json(res, 200, { items: rows.map(r => storeView({ ...r, about: [] }, cm)) });
}
function apiFacets(req, res, url, s) {
  if (!require("./gates.js").on(T(s), "listing.tools")) return bad(res, require("./gates.js").message("listing.tools"), 403);
  const { sql, args } = buildSearch(s, url);
  const rows = all(`SELECT brand, dept, price FROM products WHERE ${sql}`, ...args);
  const brands = {}, depts = {}; const buckets = { "0-25": 0, "25-50": 0, "50-100": 0, "100-250": 0, "250+": 0 };
  for (const r of rows) {
    brands[r.brand] = (brands[r.brand] || 0) + 1; depts[r.dept] = (depts[r.dept] || 0) + 1;
    const k = r.price < 25 ? "0-25" : r.price < 50 ? "25-50" : r.price < 100 ? "50-100" : r.price < 250 ? "100-250" : "250+";
    buckets[k]++;
  }
  json(res, 200, { brands: Object.entries(brands).sort((a, b) => b[1] - a[1]).slice(0, 20).map(([k, v]) => ({ brand: k, count: v })), depts: Object.entries(depts).map(([k, v]) => ({ dept: k, count: v })), price: Object.entries(buckets).map(([k, v]) => ({ range: k, count: v })) });
}
function apiBillingPay(req, res, url, s, body, id) {
  return (async () => {
  if (!requireAdmin(s, res)) return;
  if (!require("./gates.js").on(T(s), "billing.self_pay")) return bad(res, require("./gates.js").message("billing.self_pay"), 403);
  const inv = get("SELECT * FROM invoices WHERE id=? AND tenant_id=?", Number(id), T(s));
  if (!inv) return bad(res, "Unknown invoice", 404);
  if (stIs("invoice", inv.status, "success")) return bad(res, "Invoice already paid");
  const gws = enabledGateways(T(s));
  const g = gws.find(x => x.id === String(body.gateway || "")) || gws[0];
  if (!g) return bad(res, "No payment gateway configured", 422);
  const sim = await settlePayment(T(s), g, inv.amount, inv.currency || require("./defaults.js").currency(T(s)), inv.number);
  if (stIs("payment", sim.status, "failure")) return bad(res, "Payment declined: " + (sim.error || "gateway error"), 402);
  /* a platform invoice is settled by a REAL capture — a simulated/sandbox gateway can't mark
     money owed to the platform as paid (allowed outside production for development) */
  if (!sim.live && !simulatedSettlementAllowed()) return bad(res, "A live payment gateway is required to pay this invoice", 402);
  if (!stIs("payment", sim.status, "settled")) return bad(res, "Payment is pending — the invoice is marked paid once the capture completes", 202);
  invoicePaid(inv);
  run("INSERT INTO payments(tenant_id,kind,invoice_id,gateway,method,amount,currency,fee,status,txn_ref) VALUES(?,?,?,?,?,?,?,?,?,?)",
    T(s), "invoice", inv.id, g.id, (g.methods || ["card"])[0], inv.amount, inv.currency || require("./defaults.js").currency(T(s)), sim.fee, sim.status, sim.ref);
  logAction(s, "invoice.pay", "invoice", inv.number, { gateway: g.id, live: !!sim.live }, req);
  json(res, 200, { ok: true, number: inv.number });
  })();
}

/* ================= FX / CONVERSIONS ================= */
function platGet(key, dflt) { try { const r = get("SELECT value FROM platform_settings WHERE key=?", key); return r ? J(r.value, dflt) : dflt; } catch (e) { return dflt; } }
function platSet(key, val) { run("INSERT INTO platform_settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", key, JSON.stringify(val)); }
function fxRate(from, to) {
  const f = registry.currency(from), t = registry.currency(to);
  if (!f || !t) return null;
  return { from: f, to: t, rate: +((f.usd || 1) / (t.usd || 1)).toFixed(8) };
}
function applyRates(rates, source, note, s) {
  const applied = [], skipped = [];
  for (const [code, usd] of Object.entries(rates || {})) {
    const c = registry.currency(code);
    if (!c) { skipped.push(code); continue; }
    const v = Number(usd);
    if (!(v > 0)) { skipped.push(code); continue; }
    run("UPDATE currencies SET usd=? WHERE code=?", v, c.code);
    run("INSERT INTO fx_rates(currency,usd,source,note) VALUES(?,?,?,?)", c.code, v, source, String(note || "").slice(0, 120));
    applied.push(c.code);
  }
  if (s && s.platform_admin) audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "fx." + source, "currency", applied.join(","), { skipped });
  return { applied, skipped };
}
function httpGetJson(url) {
  return new Promise((resolve, reject) => {
    let u; try { u = new URL(url); } catch (e) { return reject(new Error("Invalid feed URL")); }
    if (!/^https?:$/.test(u.protocol)) return reject(new Error("Feed URL must be http(s)"));
    const lib = u.protocol === "https:" ? require("https") : require("http");
    const req = lib.get(url, res => {
      if (res.statusCode !== 200) { res.resume(); return reject(new Error("Feed returned HTTP " + res.statusCode)); }
      let data = "", len = 0;
      res.on("data", c => { len += c.length; if (len > 1e6) { req.destroy(); return reject(new Error("Feed too large")); } data += c; });
      res.on("end", () => { try { resolve(JSON.parse(data)); } catch (e) { reject(new Error("Feed is not valid JSON")); } });
    });
    req.on("error", e => reject(new Error("Feed fetch failed: " + e.message)));
    req.setTimeout(8000, () => req.destroy(new Error("Feed timeout")));
  });
}
function apiFxConvert(req, res, url, s) {
  const from = (url.searchParams.get("from") || "").toUpperCase(), to = (url.searchParams.get("to") || "").toUpperCase();
  const amount = Number(url.searchParams.get("amount") != null ? url.searchParams.get("amount") : 1);
  const r = fxRate(from, to);
  if (!r) return bad(res, "Unknown currency pair — both codes must exist in the currencies registry", 404);
  json(res, 200, { from, to, amount, rate: r.rate, result: +(amount * r.rate).toFixed(r.to.decimals), decimals: r.to.decimals, asOf: new Date().toISOString() });
}
function apiPlatformFx(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const fxs = rl("fxSources").length ? rl("fxSources") : meta.FX_SOURCES;
  json(res, 200, { currencies: registry.currencies(), sources: fxs, provider: platGet("fx_provider", { provider: (fxs.find(x => x.default) || fxs[0] || {}).key, url: "" }), history: all("SELECT * FROM fx_rates ORDER BY id DESC LIMIT 60"), lastSync: platGet("fx_last_sync", null) });
}
function apiPlatformFxRates(req, res, url, s, body) {
  if (!requirePlatformSection(s, res, "geo", "write")) return;
  if (!body || typeof body.rates !== "object") return bad(res, "rates object required, e.g. { \"EUR\": 1.08 }");
  const r = applyRates(body.rates, "manual", body.note, s);
  json(res, 200, { ...r, currencies: registry.currencies() });
}
function apiPlatformFxProvider(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  const fxs = rl("fxSources").length ? rl("fxSources") : meta.FX_SOURCES;
  const src = fxs.find(x => x.key === body.provider) || fxs.find(x => x.default) || fxs[0] || {};
  const provider = src.key;
  if (src.fetches && !/^https?:\/\//.test(String(body.url || ""))) return bad(res, (src.name || provider) + " needs an http(s) URL");
  platSet("fx_provider", { provider, url: String(body.url || "").slice(0, 300) });
  audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "fx.provider", "fx", provider, { url: String(body.url || "") });
  json(res, 200, { ok: true, provider: { provider, url: String(body.url || "") } });
}
async function apiPlatformFxSync(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const fxs = rl("fxSources").length ? rl("fxSources") : meta.FX_SOURCES;
  const cfg = platGet("fx_provider", { provider: (fxs.find(x => x.default) || fxs[0] || {}).key, url: "" });
  if (!(fxs.find(x => x.key === cfg.provider) || {}).fetches || !cfg.url) return bad(res, "No feed provider configured — set it under FX feed first");
  try {
    const data = await httpGetJson(cfg.url);
    const rates = (data && data.rates) || data;
    if (!rates || typeof rates !== "object" || Array.isArray(rates)) return bad(res, "Feed JSON must be {CODE: usdValue} or {rates:{…}}");
    rates.USD = 1;
    const r = applyRates(rates, "feed", cfg.url, s);
    const stamp = new Date().toISOString();
    platSet("fx_last_sync", { at: stamp, applied: r.applied, skipped: r.skipped });
    json(res, 200, { ok: true, ...r, at: stamp });
  } catch (e) { bad(res, e.message, 502); }
}

/* ================= STORE ADMIN ================= */
function apiAdminStats(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  const revenue = get("SELECT COALESCE(SUM(total),0) t FROM orders WHERE tenant_id=?", t).t;
  const orders = get("SELECT COUNT(*) c FROM orders WHERE tenant_id=?", t).c;
  const op = stIn("order", "open");
  const pending = get("SELECT COUNT(*) c FROM orders WHERE tenant_id=? AND status IN " + op.sql, t, ...op.args).c;
  const customers = get("SELECT COUNT(*) c FROM users WHERE tenant_id=? AND role='customer'", t).c;
  const products = get("SELECT COUNT(*) c FROM products WHERE tenant_id=?", t).c;
  const lowStock = all("SELECT id,title,brand,stock FROM products WHERE tenant_id=? AND stock<=10 ORDER BY stock ASC LIMIT 8", t);
  const recent = all("SELECT id,num,name,total,status,created_at FROM orders WHERE tenant_id=? ORDER BY created_at DESC LIMIT 8", t);
  const daily = all("SELECT date(created_at) d, COALESCE(SUM(total),0) t FROM orders WHERE tenant_id=? AND created_at >= datetime('now','-13 days') GROUP BY date(created_at) ORDER BY d", t);
  const topDepts = all("SELECT p.dept, SUM(oi.qty*oi.price) rev FROM order_items oi JOIN orders o ON o.id=oi.order_id AND o.tenant_id=? JOIN products p ON p.tenant_id=o.tenant_id AND p.id=oi.product_id GROUP BY p.dept ORDER BY rev DESC LIMIT 6", t);
  const payments = all("SELECT gateway, COUNT(*) c, COALESCE(SUM(amount),0) amt, COALESCE(SUM(fee),0) fee FROM payments WHERE tenant_id=? GROUP BY gateway", t);
  json(res, 200, { revenue, orders, pending, customers, products, lowStock, recent, daily, topDepts, payments, plan: planFor(t) });
}
function apiAdminProducts(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const q = (url.searchParams.get("q") || "").toLowerCase();
  let rows = all("SELECT * FROM products WHERE tenant_id=? ORDER BY position", T(s));
  if (q) rows = rows.filter(r => (r.title + " " + r.brand + " " + r.id).toLowerCase().includes(q));
  json(res, 200, { products: rows });
}
function writeBullets(tenantId, pid, arr) {
  run("DELETE FROM product_bullets WHERE tenant_id=? AND product_id=?", tenantId, pid);
  (arr || []).forEach((t, i) => run("INSERT INTO product_bullets(tenant_id,product_id,pos,text) VALUES(?,?,?,?)", tenantId, pid, i, String(t).slice(0, 300)));
}
/* a product's type must be one the registry declares. The 23 seeded types (physical,
   service, subscription, insurance, appointment…) plus anything an operator adds from
   the console are the vocabulary; an unrecognised type is refused with the valid set
   rather than silently filed as physical — otherwise "add a service" stores a good and
   nobody can tell. */
function resolveProductType(type, existing) {
  const t = String(type || "").trim();
  if (!t) return existing || require("./defaults.js").of("productTypes");
  const known = registry.list("productTypes").map(p => p.key);
  if (!known.includes(t)) return { error: "Unknown product type '" + t + "'. Registered types: " + known.join(", ") };
  return t;
}

function apiAdminProductCreate(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  const plan = planFor(t);
   /* the plan quota governs the merchant's OWN catalogue. Universes activated from the
      corpus AND products imported from the platform's global catalogue are
      platform-supplied offerings (the flagship ships with the whole corpus activated by
      default; a store may list a global product only when the platform permits it), so
      neither may consume the tenant's quota — otherwise a store on a Growth plan could
      not add a single product of its own while platform supply was on its shelf. */
   const count = get("SELECT COUNT(*) c FROM products WHERE tenant_id=? AND (source_kind IS NULL OR source_kind NOT IN ('universe','global'))", t).c;
  if (count >= plan.max_products) return bad(res, `Plan limit reached (${plan.name}: ${plan.max_products} products). Upgrade to add more.`, 402);
  const title = String(body.title || "").trim(), brand = String(body.brand || "").trim(), dept = String(body.dept || "").trim();
  const price = Number(body.price);
  if (!title || !brand || !(price > 0)) return bad(res, "Title, brand and price are required");
  const ptype = resolveProductType(body.type);
  if (ptype.error) return bad(res, ptype.error, 400);
  const id = "LX" + crypto.randomBytes(4).toString("hex").toUpperCase();
  const list = Number(body.list) > price ? Number(body.list) : null;
  const pos = get("SELECT COALESCE(MAX(position),0) m FROM products WHERE tenant_id=?", t).m + 1;
  run(`INSERT INTO products(tenant_id,id,title,brand,dept,type,price,list_price,rating,ratings_count,emoji,hue,priority,stock,flags,keywords,deal_pct,position)
       VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`,
    t, id, title, brand, dept, ptype, price, list, Math.min(5, Math.max(0, Number(body.rating) || 4.5)), Math.max(0, Number(body.count) || 0),
    String(body.emoji || "🛍️").slice(0, 4), Math.floor(Math.random() * 360), body.priority ? 1 : 0, Math.max(0, Number(body.stock) || 0),
    String(body.flags || ""), String(body.keywords || title.toLowerCase()), list ? Math.round((1 - price / list) * 100) : 0, pos);
  writeBullets(t, id, body.about);
  search.onCatalogChange(t);
  logAction(s, "product.create", "product", id, { title, price, type: ptype });
  json(res, 200, { product: get("SELECT * FROM products WHERE tenant_id=? AND id=?", t, id) });
}
function apiAdminProductUpdate(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  const p = get("SELECT * FROM products WHERE tenant_id=? AND id=?", t, id);
  if (!p) return bad(res, "Unknown product", 404);
  const price = body.price != null ? Number(body.price) : p.price;
  const list = body.list != null ? (Number(body.list) > price ? Number(body.list) : null) : p.list_price;
  const ptype = resolveProductType(body.type, p.type);
  if (ptype.error) return bad(res, ptype.error, 400);
  run(`UPDATE products SET title=?, brand=?, dept=?, type=?, price=?, list_price=?, rating=?, ratings_count=?, emoji=?, hue=?, priority=?, stock=?, flags=?, keywords=?, deal_pct=? WHERE tenant_id=? AND id=?`,
    body.title != null ? String(body.title).trim() : p.title, body.brand != null ? String(body.brand).trim() : p.brand,
    body.dept != null ? String(body.dept) : p.dept, ptype, price, list,
    body.rating != null ? Math.min(5, Math.max(0, Number(body.rating))) : p.rating,
    body.count != null ? Math.max(0, Number(body.count)) : p.ratings_count,
    body.emoji != null ? String(body.emoji).slice(0, 4) : p.emoji,
    body.hue != null ? Number(body.hue) % 360 : p.hue,
    body.priority != null ? (body.priority ? 1 : 0) : p.priority,
    body.stock != null ? Math.max(0, Number(body.stock)) : p.stock,
    body.flags != null ? String(body.flags) : p.flags,
    body.keywords != null ? String(body.keywords) : p.keywords,
    list ? Math.round((1 - price / list) * 100) : 0, t, id);
  if (body.about) writeBullets(t, id, body.about);
  search.onCatalogChange(t);
  logAction(s, "product.update", "product", id, { fields: Object.keys(body) });
  json(res, 200, { product: get("SELECT * FROM products WHERE tenant_id=? AND id=?", t, id) });
}
function apiAdminProductDelete(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  if (!get("SELECT id FROM products WHERE tenant_id=? AND id=?", t, id)) return bad(res, "Unknown product", 404);
  run("DELETE FROM products WHERE tenant_id=? AND id=?", t, id);
  run("DELETE FROM product_bullets WHERE tenant_id=? AND product_id=?", t, id);
  run("DELETE FROM reviews WHERE tenant_id=? AND product_id=?", t, id);
  search.onCatalogChange(t);
  logAction(s, "product.delete", "product", id);
  json(res, 200, { ok: true });
}
function apiAdminOrders(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  const orders = all("SELECT * FROM orders WHERE tenant_id=? ORDER BY created_at DESC LIMIT 200", t);
  for (const o of orders) {
    o.items = all("SELECT product_id id, qty, price FROM order_items WHERE order_id=?", o.id).map(it => {
      const p = get("SELECT title,brand,emoji,hue FROM products WHERE tenant_id=? AND id=?", t, it.id);
      return { id: it.id, qty: it.qty, price: it.price, product: p || null };
    });
    const pay = get("SELECT gateway, method, txn_ref, status, fee FROM payments WHERE tenant_id=? AND order_id=?", t, o.id);
    if (pay) o.payment = pay;
  }
  json(res, 200, { orders });
}
function apiAdminOrderStatus(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const allowed = ["processing", "shipped", "delivered", "cancelled"];
  if (!allowed.includes(body.status)) return bad(res, "Invalid status");
  const r = run("UPDATE orders SET status=? WHERE id=? AND tenant_id=?", body.status, Number(id), T(s));
  if (!r.changes) return bad(res, "Unknown order", 404);
  logAction(s, "order.status", "order", id, { status: body.status });
  json(res, 200, { ok: true });
}
function apiAdminUsers(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  json(res, 200, { users: all(`SELECT id,name,email,role,created_at,(SELECT COUNT(*) FROM orders o WHERE o.owner='t${t}:u:'||users.id) orders,(SELECT COALESCE(SUM(total),0) FROM orders o WHERE o.owner='t${t}:u:'||users.id) spend FROM users WHERE tenant_id=? ORDER BY created_at DESC`, t) });
}
function apiAdminUserDelete(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const u = get("SELECT * FROM users WHERE id=? AND tenant_id=?", Number(id), T(s));
  if (!u) return bad(res, "Unknown user", 404);
  if (u.role === "admin") return bad(res, "Store admins cannot be deleted here");
  run("DELETE FROM users WHERE id=?", u.id);
  run("DELETE FROM cart_items WHERE owner=?", `t${T(s)}:u:${u.id}`);
  run("UPDATE sessions SET user_id=NULL WHERE user_id=?", u.id);
  logAction(s, "user.delete", "user", id, { email: u.email });
  json(res, 200, { ok: true });
}
function apiAdminReviews(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { reviews: all(`SELECT rv.id, rv.product_id, rv.name, rv.rating, rv.title, rv.body, rv.verified, rv.state, rv.votes_helpful, rv.votes_total, rv.created_at, p.title product_title FROM reviews rv LEFT JOIN products p ON p.tenant_id=rv.tenant_id AND p.id=rv.product_id WHERE rv.tenant_id=? ORDER BY rv.created_at DESC LIMIT 100`, T(s)) });
}
function apiAdminUgcQueue(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const q = ugc.moderationQueue(T(s));
  json(res, 200, { ...q, pending: q.reviews.length + q.questions.length + q.answers.length, states: ugc.STATES });
}
function apiAdminReviewDelete(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  run("DELETE FROM reviews WHERE id=? AND tenant_id=?", Number(id), T(s));
  logAction(s, "review.delete", "review", id);
  json(res, 200, { ok: true });
}
function apiAdminSettingsGet(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { settings: CFG(s), defaults: settings.DEFAULTS, countries: registry.countries(), taxModes: registry.taxModes(), currencies: registry.currencies() });
}
function apiAdminSettingsPut(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  if (!requireSection(s, res, "settings", "write")) return;
  if (body.commerce) for (const k of ["currency", "symbol", "locale", "taxMode", "taxRate", "decimals"]) if (body.commerce[k] === "" || body.commerce[k] == null) body.commerce[k] = null;
  if (body.commerce && body.commerce.currency && !registry.currency(body.commerce.currency)) return bad(res, "Unknown currency — pick from the currencies registry (Geo console)");
  if (body.commerce && body.commerce.country && !require("./places.js").byCode(body.commerce.country)) return bad(res, "Unknown place — a store's jurisdiction is a country or subdivision in the Geo registry");
  if (body.commerce && "shipRates" in body.commerce && !["fixed", "live"].includes(body.commerce.shipRates)) return bad(res, "shipRates is fixed or live");
  if (body.commerce && "parcelWeightKg" in body.commerce && !(Number(body.commerce.parcelWeightKg) > 0 && Number(body.commerce.parcelWeightKg) <= 1000)) return bad(res, "parcelWeightKg must be above 0 and at most 1000");
  if (body.commerce && "shipFrom" in body.commerce) {
    const sf = cleanShipFrom(body.commerce.shipFrom);
    if (sf.error) return bad(res, sf.error);
    /* an address is replaced whole, never merged with a previous one */
    body.commerce.shipFrom = sf.value;
  }
  if (body.features) {
    const pol = sec.policy().provisioning;
    /* an atom the platform policy must allow names its policy flag on its catalogue row */
    for (const [k, v] of Object.entries(body.features)) { const no = v === true && require("./capabilities.js").policyRefusal(k, pol); if (no) return bad(res, no, 403); }
    /* the storefront atoms own their own rows now — route the writes through the
       composition and persist only what is not an atom on the settings row */
    const leftover = caps.applyFeatures(T(s), body.features);
    if (Object.keys(leftover).length) settings.save(T(s), { features: leftover });
    else if (body.features && Object.keys(body.features).length) settings.save(T(s), { features: caps.leftoverFeatures(T(s)) });
  }
  if (body.commerce && body.commerce.currency && !sec.policy().provisioning.currencyOverridesAllowed) {
    const co = registry.country(CFG(s).commerce.country);
    if (body.commerce.currency !== co.currency) return bad(res, "Currency overrides are disabled by platform policy (allow under Platform → Provisioning)", 403);
  }
  const cur0 = CFG(s);
  const merged = {};
  for (const [k, v] of Object.entries(body || {})) merged[k] = settings.deepMerge(cur0[k], v);
  if (body.commerce && "shipFrom" in body.commerce) merged.commerce.shipFrom = body.commerce.shipFrom;
  settings.save(T(s), merged);
  logAction(s, "settings.update", "settings", T(s), { sections: Object.keys(body || {}) });
  json(res, 200, { settings: CFG(s) });
}
function apiAdminSettingsReset(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  if (!requireSection(s, res, "settings", "write")) return;
  settings.reset(T(s));
  logAction(s, "settings.reset", "settings", T(s));
  json(res, 200, { settings: CFG(s) });
}
function apiAdminDepartments(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { departments: all("SELECT * FROM departments WHERE tenant_id=? ORDER BY position", T(s)) });
}
function apiAdminDeptSave(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  const key = String(body.key || "").trim().toLowerCase().replace(/[^a-z0-9_]/g, "");
  if (!key || !body.label) return bad(res, "Key and label required");
  const ex = get("SELECT key FROM departments WHERE tenant_id=? AND key=?", t, key);
  if (ex) run("UPDATE departments SET label=?, icon=?, active=?, position=? WHERE tenant_id=? AND key=?", String(body.label), String(body.icon || "🏷️"), body.active === 0 ? 0 : 1, Number(body.position) || 0, t, key);
  else run("INSERT INTO departments(tenant_id,key,label,icon,active,position) VALUES(?,?,?,?,?,?)", t, key, String(body.label), String(body.icon || "🏷️"), body.active === 0 ? 0 : 1, get("SELECT COALESCE(MAX(position),0) m FROM departments WHERE tenant_id=?", t).m + 1);
  logAction(s, "department.save", "department", key);
  json(res, 200, { departments: all("SELECT * FROM departments WHERE tenant_id=? ORDER BY position", t) });
}
function apiAdminDeptDelete(req, res, url, s, body, key) {
  if (!requireAdmin(s, res)) return;
  if (get("SELECT COUNT(*) c FROM products WHERE tenant_id=? AND dept=?", T(s), key).c > 0) return bad(res, "Department still has products — move them first");
  run("DELETE FROM departments WHERE tenant_id=? AND key=?", T(s), key);
  logAction(s, "department.delete", "department", key);
  json(res, 200, { ok: true });
}
function apiAdminBanners(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { banners: all("SELECT * FROM home_banners WHERE tenant_id=? ORDER BY position", T(s)) });
}
function apiAdminBannerSave(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  if (!body.title) return bad(res, "Title required");
  const t = T(s);
  const vals = [String(body.title), String(body.subtitle || ""), String(body.cta || "Discover"), Number(body.hue) || 210, String(body.dept || ""), body.active === 0 ? 0 : 1, Number(body.position) || 0];
  if (id) run("UPDATE home_banners SET title=?,subtitle=?,cta=?,hue=?,dept=?,active=?,position=? WHERE id=? AND tenant_id=?", ...vals, Number(id), t);
  else run("INSERT INTO home_banners(tenant_id,title,subtitle,cta,hue,dept,active,position) VALUES(?,?,?,?,?,?,?,?)", t, ...vals);
  logAction(s, "banner.save", "home_banner", id || "new");
  json(res, 200, { banners: all("SELECT * FROM home_banners WHERE tenant_id=? ORDER BY position", t) });
}
function apiAdminBannerDelete(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  run("DELETE FROM home_banners WHERE id=? AND tenant_id=?", Number(id), T(s));
  logAction(s, "banner.delete", "home_banner", id);
  json(res, 200, { ok: true });
}
function apiAdminCards(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { cards: all("SELECT * FROM home_cards WHERE tenant_id=? ORDER BY position", T(s)) });
}
function apiAdminCardSave(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  if (!body.title || !body.dept) return bad(res, "Title and department required");
  const tiles = Array.isArray(body.tiles) ? JSON.stringify(body.tiles.slice(0, 4)) : "[]";
  const vals = [String(body.title), String(body.dept), tiles, body.active === 0 ? 0 : 1, Number(body.position) || 0];
  if (id) run("UPDATE home_cards SET title=?,dept=?,tiles=?,active=?,position=? WHERE id=? AND tenant_id=?", ...vals, Number(id), t);
  else run("INSERT INTO home_cards(tenant_id,title,dept,tiles,active,position) VALUES(?,?,?,?,?,?)", t, ...vals);
  logAction(s, "card.save", "home_card", id || "new");
  json(res, 200, { cards: all("SELECT * FROM home_cards WHERE tenant_id=? ORDER BY position", t) });
}
function apiAdminCardDelete(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  run("DELETE FROM home_cards WHERE id=? AND tenant_id=?", Number(id), T(s));
  logAction(s, "card.delete", "home_card", id);
  json(res, 200, { ok: true });
}
async function apiAdminAccount(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const u = get("SELECT * FROM users WHERE id=?", s.user_id);
  /* changing the sign-in password or email proves the current password first — a hijacked
     session must not be able to lock the owner out */
  if ((body.password || body.email) && !(await verifyUserAsync(T(s), u.email, String(body.current_password || ""))))
    return bad(res, "Your current password is required to change your password or email", 403);
  if (body.password) {
    const perr = sec.checkPassword(String(body.password), u.email);
    if (perr) return bad(res, perr);
    if (await passwordReusedAsync(T(s), u.email, String(body.password))) return bad(res, "You cannot reuse a previous password", 422);
    await setUserPasswordAsync(u.id, String(body.password), u.email);
    logAction(s, "account.password", "user", u.id, { upgraded: true });
  }
  if (body.email) {
    const email = String(body.email).trim().toLowerCase();
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return bad(res, "Invalid email");
    if (get("SELECT id FROM users WHERE tenant_id=? AND email=? AND id!=?", T(s), email, u.id)) return bad(res, "Email already in use", 409);
    run("UPDATE users SET email=? WHERE id=?", email, u.id);
    logAction(s, "account.email", "user", u.id, { email });
  }
  json(res, 200, { ok: true });
}

/* ---------------- store: gateways / payments / billing / audit / monitor ---------------- */
function maskConfig(g) {
  const cfg = { ...(g.config || {}) };
  return cfg;
}
function apiAdminGateways(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  const c = CFG(s);
  const country = registry.countryProfile(CFG(s).commerce.country);
  const reg = paymentRegistry(t);
  const rows = all("SELECT * FROM tenant_gateways WHERE tenant_id=? AND provider_id NOT LIKE 'ship:%' AND provider_id NOT LIKE 'notify:%' ORDER BY position", t);
  const known = new Set(rows.map(r => r.provider_id));
  const list = rows.map(r => {
    const p = reg.find(x => x.id === r.provider_id) || { id: r.provider_id, name: r.provider_id, emoji: "🔌", methods: ["card"], feePct: 0, fields: [] };
    let cfg = {}; try { cfg = JSON.parse(r.config || "{}"); } catch (e) { }
    cfg = sec.unsealConfig(t, r.provider_id, JSON.stringify(cfg));
    const masked = {};
    for (const [k, v] of Object.entries(cfg)) masked[k] = (p.fields || []).some(f => f.key === k && f.secret) ? (v ? "••••" + String(v).slice(-4) : "") : v;
    return { id: p.id, name: p.name, emoji: p.emoji, desc: p.desc, methods: p.methods, feePct: p.feePct, feeFixed: p.feeFixed, fields: p.fields, enabled: !!r.enabled, primary: !!r.is_primary, mode: r.mode, config: masked, available: registry.supports(p.id, country.code) };
  });
  for (const p of reg) if (!known.has(p.id) && registry.supports(p.id, country.code))
    list.push({ id: p.id, name: p.name, emoji: p.emoji, desc: p.desc, methods: p.methods, feePct: p.feePct, feeFixed: p.feeFixed, fields: p.fields, enabled: false, primary: false, mode: "sandbox", config: {}, available: true });
  json(res, 200, { gateways: list, country: { code: country.code, name: country.name, currency: country.currency }, carriers: enabledCarriers(t), notifiers: enabledNotifiers(t).map(n => ({ id: n.id, name: n.name, emoji: n.emoji })) });
}
function apiAdminGatewaysPut(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  if (!requireSection(s, res, "payments", "write")) return;
  const t = T(s);
  const list = Array.isArray(body.gateways) ? body.gateways : [];
  /* the console only ever holds masked secrets; a masked (or omitted) value on save keeps
     the stored one — deleting and re-inserting the list used to drop every key on re-save */
  const prior = {};
  for (const r of all("SELECT provider_id, config FROM tenant_gateways WHERE tenant_id=? AND provider_id NOT LIKE 'ship:%' AND provider_id NOT LIKE 'notify:%'", t)) { try { prior[r.provider_id] = JSON.parse(r.config || "{}"); } catch (e) { prior[r.provider_id] = {}; } }
  run("DELETE FROM tenant_gateways WHERE tenant_id=? AND provider_id NOT LIKE 'ship:%' AND provider_id NOT LIKE 'notify:%'", t);
  list.forEach((g, i) => {
    const cfg = {};
    const was = prior[String(g.id)] || {};
    for (const [k, v] of Object.entries(was)) if (!(g.config && k in g.config && g.config[k] !== "" && !String(g.config[k]).startsWith("••••"))) cfg[k] = v;
    for (const [k, v] of Object.entries(g.config || {})) if (v && !String(v).startsWith("••••") && !String(v).startsWith("lux.v1.")) cfg[k] = sec.encryptSecret(v, T(s) + "|" + g.id + "|" + k);
    const defP = paymentRegistry(t).find(x => x.id === g.id) || { fields: [] };
  const secretKeys = (defP.fields || []).filter(f => f.secret).map(f => f.key);
  for (const k of secretKeys) if (cfg[k] && !String(cfg[k]).startsWith("lux.v1.")) cfg[k] = sec.encryptSecret(cfg[k], t + "|" + g.id + "|" + k);
  run("INSERT INTO tenant_gateways(tenant_id,provider_id,enabled,is_primary,mode,config,position) VALUES(?,?,?,?,?,?,?)",
    t, String(g.id), g.enabled ? 1 : 0, g.primary ? 1 : 0, g.mode === "live" ? "live" : "sandbox", JSON.stringify(cfg), i);
  });
  logAction(s, "gateways.update", "gateway", null, { count: list.length });
  json(res, 200, { ok: true });
}
function apiAdminGatewayTest(req, res, url, s, body, id) {
  return (async () => {
  if (!requireAdmin(s, res)) return;
  const gw = paymentRegistry(T(s)).find(x => x.id === id);
  if (!gw) return bad(res, "Unknown gateway", 404);
  const row = get("SELECT * FROM tenant_gateways WHERE tenant_id=? AND provider_id=?", T(s), id);
  let cfg = sec.unsealConfig(T(s), id, (row && row.config) || "{}");
  const missing = (gw.fields || []).filter(f => !cfg[f.key] || String(cfg[f.key]).startsWith("••••"));
  const ok = missing.length === 0;
  let detail = "";
  if (ok && row.mode === "live") {
    const ping = await connect.ping({ provider: id, config: cfg });
    if (ping.live && !ping.ok) return json(res, 200, { ok: false, message: `Live verification failed: ${ping.error}` });
    detail = ping.live ? " live verified" : "";
  }
  logAction(s, "gateway.test", "gateway", id, { ok, mode: row && row.mode });
  json(res, 200, { ok, message: ok ? `✓ ${gw.name} ${row.mode === "live" ? "live" + detail : "sandbox"} connection verified` : `Missing credentials: ${missing.map(m => m.label).join(", ")}` });
  })();
}
function apiAdminAiGateways(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  const premProviders = require("./ai.js").AI_PROVIDERS || [];
  const rows = all("SELECT * FROM tenant_gateways WHERE tenant_id=? AND provider_id LIKE 'ai:%' ORDER BY position", t);
  const list = rows.map(r => {
    const p = premProviders.find(p => p.id === r.provider_id.replace("ai:", "")) || { id: r.provider_id, name: r.provider_id, emoji: "🔌", fields: [] };
    let cfg = {}; try { cfg = JSON.parse(r.config || "{}"); } catch (e) { }
    cfg = sec.unsealConfig(t, r.provider_id, JSON.stringify(cfg));
    const masked = {};
    for (const [k, v] of Object.entries(cfg)) masked[k] = (p.fields || []).some(f => f.key === k && f.secret) ? (v ? "••••" + String(v).slice(-4) : "") : v;
    return { id: p.id, name: p.name, emoji: p.emoji, desc: p.desc, fields: p.fields, enabled: !!r.enabled, mode: r.mode, config: masked };
  });
  for (const p of premProviders) {
    const id = "ai:" + p.id;
    if (!rows.find(r => r.provider_id === id))
      list.push({ id: p.id, name: p.name, emoji: p.emoji, desc: p.desc, fields: p.fields, enabled: false, mode: "sandbox", config: {} });
  }
  json(res, 200, { gateways: list });
}
function apiAdminAiGatewaysPut(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  if (!requireSection(s, res, "ai", "write")) return;
  const t = T(s);
  run("DELETE FROM tenant_gateways WHERE tenant_id=? AND provider_id LIKE 'ai:%'", t);
  /* only AI providers — this route used to plant any provider id (payment, shipping) */
  const aiIds = new Set((require("./ai.js").AI_PROVIDERS || []).map(p => "ai:" + p.id));
  const ids = Object.keys(body || {}).map(k => k.startsWith("ai:") ? k : "ai:" + k);
  const badId = ids.find(k => !aiIds.has(k));
  if (badId) return bad(res, "Unknown AI provider: " + badId, 400);
  body = Object.fromEntries(Object.entries(body || {}).map(([k, v]) => [k.startsWith("ai:") ? k : "ai:" + k, v]));
  ids.forEach((id, i) => {
    const cfg = {};
    for (const [k, v] of Object.entries(body[id] || {})) if (v && !String(v).startsWith("••••") && !String(v).startsWith("lux.v1.")) cfg[k] = sec.encryptSecret(v, t + "|" + id + "|" + k);
    run("INSERT INTO tenant_gateways(tenant_id,provider_id,enabled,is_primary,mode,config,position) VALUES(?,?,?,?,?,?,?)",
      t, id, 1, 0, "sandbox", JSON.stringify(cfg), i);
  });
  logAction(s, "ai_gateways.update", "ai_provider", null, { count: ids.length });
  json(res, 200, { ok: true });
}
function apiAdminAiGatewayTest(req, res, url, s, body, id) {
  return (async () => {
  if (!requireAdmin(s, res)) return;
  const row = get("SELECT * FROM tenant_gateways WHERE tenant_id=? AND provider_id=?", T(s), id);
  let cfg = sec.unsealConfig(T(s), id, (row && row.config) || "{}");
  const premProviders = require("./ai.js").AI_PROVIDERS || [];
  const p = premProviders.find(p => p.id === id.replace("ai:", "")) || { fields: [] };
  const missing = (p.fields || []).filter(f => !cfg[f.key] || String(cfg[f.key]).startsWith("••••"));
  const ok = missing.length === 0;
  logAction(s, "ai_gateway.test", "ai_provider", id, { ok });
  json(res, 200, { ok, message: ok ? `✓ ${p.name} sandbox connection verified` : `Missing credentials: ${missing.map(m => m.label).join(", ")}` });
  })();
}
function apiAdminPayments(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  /* each row says what can be done with it: a live pending payment can be checked with its
     gateway, one settled offline (the offlinePaymentMethods registry) recorded as received */
  const offline = registry.list("offlinePaymentMethods").map(m => typeof m === "string" ? m : m.key);
  const rows = all("SELECT p.*, o.num order_num, o.status order_status FROM payments p LEFT JOIN orders o ON o.id=p.order_id WHERE p.tenant_id=? ORDER BY p.created_at DESC, p.id DESC LIMIT 200", T(s));
  json(res, 200, { payments: rows.map(p => ({ ...p, offline: !p.live && offline.includes(String(p.method)) })) });
}
async function apiAdminPaymentRefund(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const p = get("SELECT * FROM payments WHERE id=? AND tenant_id=?", Number(id), T(s));
  if (!p) return bad(res, "Unknown payment", 404);
  if (!stIs("payment", p.status, "refundable")) return bad(res, "Only captured payments can be refunded");
  /* money taken by a real gateway goes back through that gateway; only a simulated (or an
     explicitly manual, refunded-elsewhere) payment is marked refunded without a call */
  let gatewayRefund = null;
  if (p.live && !body.manual) {
    const live = gatewaySecrets(T(s), p.gateway);
    if (!live || !p.provider_payment_id) return bad(res, "This payment can't be refunded through " + p.gateway + " from here — refund it in the gateway's dashboard, then record it with manual: true", 409);
    const r = await connect.refund({ provider: p.gateway, config: live.cfg, paymentId: p.provider_payment_id, amount: p.amount, currency: p.currency, idempotency: "refund-" + p.id });
    if (!r.live) return bad(res, "Refund not sent (" + (r.reason || "gateway offline") + ")", 503);
    if (!r.ok || stIs("payment", r.status, "failure")) return bad(res, "The gateway refused the refund: " + (r.error || r.status), 502);
    gatewayRefund = { id: r.id, status: r.status };
  }
  const rf = stIn("payment", "refundable");
  const claim = run("UPDATE payments SET status=? WHERE id=? AND status IN " + rf.sql, states.first("payment", "reversed"), p.id, ...rf.args);
  if (!claim.changes) return bad(res, "Only captured payments can be refunded", 409);
  let claw = null; if (p.order_id) { const ord = get("SELECT num FROM orders WHERE id=?", p.order_id); try { claw = offers.reverseRedemption(T(s), { order_id: p.order_id, order_num: ord && ord.num }); } catch (e) { console.error("clawback:", e.message); } }
  logAction(s, "payment.refund", "payment", p.id, { amount: p.amount, gateway: p.gateway, clawback: claw && claw.voided, gateway_refund: gatewayRefund, manual: !!(p.live && body.manual) });
  if (p.order_id) { const onum = (get("SELECT num FROM orders WHERE id=?", p.order_id) || {}).num; emitEvent(T(s), "order.refunded", { payment_id: p.id, amount: p.amount, num: onum }, onum); }
  json(res, 200, { ok: true, clawback: claw && claw.voided || 0, gateway_refund: gatewayRefund });
}
function apiAdminBilling(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  json(res, 200, {
    subscription: get(`SELECT s.status, s.started_at, s.renews_at, p.name plan, p.price_month, p.currency, p.max_products, p.max_orders_month FROM subscriptions s JOIN plans p ON p.id=s.plan_id WHERE s.tenant_id=? ORDER BY s.id DESC`, t) || null,
    invoices: all("SELECT * FROM invoices WHERE tenant_id=? ORDER BY issued_at DESC", t),
    usage: { products: get("SELECT COUNT(*) c FROM products WHERE tenant_id=? AND (source_kind!='universe' OR source_kind IS NULL)", t).c,
      activatedUniverses: get("SELECT COUNT(DISTINCT source_universe) c FROM products WHERE tenant_id=? AND source_kind='universe'", t).c,
      ordersMonth: get("SELECT COUNT(*) c FROM orders WHERE tenant_id=? AND created_at >= date('now','start of month')", t).c }
  });
}
function apiAdminAudit(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { entries: all("SELECT * FROM audit_log WHERE tenant_id=? ORDER BY created_at DESC LIMIT 200", T(s)) });
}
function apiAdminEntityUsage(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { usage: all("SELECT * FROM entity_usage WHERE tenant_id=? ORDER BY at DESC", T(s)) });
}
function apiAdminMonitor(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  /* live per-tenant traffic from the accumulator every request feeds
     (lib/metrics.js) — the console's Monitor view reads totals, the 30-minute
     series and the per-endpoint table from this one snapshot. Read as the
     module singleton rather than a positional argument: the dispatcher hands
     route params before it, so a route with no :param would otherwise receive
     undefined here, and every caller (server.js, a test driving api.handle)
     shares the one accumulator the module's header documents */
  json(res, 200, require("./metrics.js").snapshot(T(s)));
}
function apiAdminCustomProviders(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { providers: all("SELECT * FROM custom_providers WHERE scope='tenant' AND tenant_id=?", T(s)) });
}
function apiAdminCustomProviderAdd(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const m = body.manifest;
  if (!m || !m.id || !m.name) return bad(res, "Manifest needs id and name");
  const kind = rl("providerKinds").includes(body.kind) ? body.kind : "payment";
  run("INSERT INTO custom_providers(scope,tenant_id,kind,manifest) VALUES('tenant',?,?,?)", T(s), kind, JSON.stringify(m));
  logAction(s, "provider.add", "custom_provider", m.id, { kind });
  json(res, 200, { ok: true });
}
function apiAdminCustomProviderDelete(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  run("DELETE FROM custom_providers WHERE id=? AND scope='tenant' AND tenant_id=?", Number(id), T(s));
  json(res, 200, { ok: true });
}

/* ================= SECURITY: scorecard · chain · keys (L6/L7) ================= */
const POLICY_KEYS = ["paymentReconcileMinutes", "minPasswordLength", "requireLetterDigit", "blockCommon", "lockoutThreshold", "lockoutBaseSec", "lockoutCapSec", "authPerMin", "apiPerMin", "csrfEnabled", "hsts", "demoHints", "cspInlineStyles"];
function apiPlatformConfigGet(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  json(res, 200, { policy: sec.policy(), defaults: sec.DEFAULT_POLICY, provisionedAt: platGet("provisioned_at", null), pepperConfigured: !!process.env.LUXORA_PEPPER, tlsBoot: process.env.LUX_TLS === "1", keyInfo: sec.keyInfo() });
}
function apiPlatformConfigPut(req, res, url, s, body) {
  /* the global security policy (CSRF, lockout, password rules, KDF cost) is the security section */
  if (!requirePlatformSection(s, res, "security", "write")) return;
  const patch = {};
  for (const k of POLICY_KEYS) if (body[k] !== undefined) patch[k] = body[k];
  /* KDF cost is clamped: too low weakens every hash, too high turns each login into a DoS */
  const clamp = (v, lo, hi, d) => { const n = Math.floor(Number(v)); return n >= lo && n <= hi ? n : d; };
  if (patch.paymentReconcileMinutes !== undefined) {
    const n = Math.floor(Number(patch.paymentReconcileMinutes));
    if (!(n >= 0 && n <= 1440)) return bad(res, "paymentReconcileMinutes must be a whole number from 0 to 1440");
    patch.paymentReconcileMinutes = n;
  }
  if (body.kdfV2) patch.kdfV2 = { logN: clamp(body.kdfV2.logN, 14, 20, 17), r: clamp(body.kdfV2.r, 8, 16, 8), p: clamp(body.kdfV2.p, 1, 4, 2) };
  /* new-store defaults: each key sent is validated and merged; a key not sent keeps its
     value (a partial update must never reset the rest). Modes and providers must exist
     in their registries; an empty provider means "none" */
  if (body.provisioning && typeof body.provisioning === "object") {
    const bp = body.provisioning, pv = {};
    const has = k => bp[k] !== undefined;
    for (const k of ["seedCatalogByDefault", "sandboxGatewaysByDefault", "currencyOverridesAllowed", "couponsAllowed", "fiscalContextsAllowed", "globalOffersAllowed"]) if (has(k)) pv[k] = !!bp[k];
    if (has("defaultPlanId")) {
      if (!get("SELECT id FROM plans WHERE id=?", Number(bp.defaultPlanId))) return bad(res, "Unknown plan");
      pv.defaultPlanId = Number(bp.defaultPlanId);
    }
    if (has("defaultCountry")) {
      const cc = String(bp.defaultCountry || "").toUpperCase();
      if (!get("SELECT code FROM countries WHERE code=?", cc)) return bad(res, "Unknown country: " + bp.defaultCountry);
      pv.defaultCountry = cc;
    }
    if (has("defaultMode")) {
      if (!rl("deployModes").some(m => m.key === bp.defaultMode)) return bad(res, "Unknown deploy mode: " + bp.defaultMode);
      pv.defaultMode = String(bp.defaultMode);
    }
    for (const [k, kind] of [["cashGateway", "payment"], ["houseShipping", "shipping"]]) if (has(k)) {
      const v = String(bp[k] || "").trim();
      if (v && !registry.providerDefs(kind).some(x => (x.id || x.key) === v)) return bad(res, "Unknown " + kind + " provider: " + v);
      pv[k] = v;
    }
    for (const [k, lo, hi] of [["paymentGatewaysPerStore", 0, 20], ["carriersPerStore", 0, 20], ["shipDaysPriority", 0, 365], ["shipDaysStandard", 0, 365]]) if (has(k)) {
      const n = Math.floor(Number(bp[k]));
      if (!(n >= lo && n <= hi)) return bad(res, k + " must be a whole number from " + lo + " to " + hi);
      pv[k] = n;
    }
    patch.provisioning = pv;
  }
  const first = !platGet("provisioned_at", null);
  const p = sec.setPolicy(patch);
  if (first) run("INSERT INTO platform_settings(key,value) VALUES('provisioned_at',?)", JSON.stringify(new Date().toISOString()));
  logAction(s, "platform.provision", "policy", first ? "initial" : "update", { changed: Object.keys(patch).join(",") }, req);
  json(res, 200, { policy: p, provisionedAt: platGet("provisioned_at", null) });
}
function apiPlatformSecurity(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  json(res, 200, { layers: sec.scorecard({ tls: !!process.env.LUX_TLS, keyInfo: sec.keyInfo(), pepper: !!process.env.LUXORA_PEPPER }), keyInfo: sec.keyInfo(), chain: auditChainVerify(null).ok ? "intact" : "BROKEN" });
}
function apiPlatformChainVerify(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const tid = url.searchParams.get("tenant");
  json(res, 200, tid ? auditChainVerify(Number(tid)) : auditChainVerify(null));
}
function apiPlatformKeyRotate(req, res, url, s) {
  if (!requirePlatformSection(s, res, "security", "write")) return;
  const v = sec.rotateKey();
  audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "keys.rotate", "platform", v, {});
  json(res, 200, { ok: true, version: v, keys: sec.keyInfo() });
}
function apiAdminChainVerify(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, auditChainVerify(T(s)));
}

/* ================= PLATFORM ================= */
async function apiPlatformLogin(req, res, url, s, body) {
  const email = String(body.email || "").trim();
  const lock = sec.lockState(email);
  if (lock.locked) return bad(res, "Account temporarily locked — retry in " + lock.retryAfterSec + "s", 423);
  const a = await verifyPlatformAdminAsync(email, String(body.password || ""));
  if (!a) { sec.noteLoginFail(email);
    return bad(res, "Invalid platform credentials", 401);
  }
  const ptid = crypto.randomBytes(20).toString("hex");
  run("INSERT INTO platform_sessions(ptid, admin_id, expires_at) VALUES(?,?,datetime('now','+12 hours'))", ptid, a.id);
  /* the mirror image of the store path: a platform sign-in no longer drops the
     client's store-user binding. One identity may hold both authorities; each
     stays scoped to its own surface */
  res.appendHeader("Set-Cookie", `azp=${ptid}; Path=/; HttpOnly; SameSite=Lax; Max-Age=43200${isTls(req) ? "; Secure" : ""}`);
  sec.noteLoginOk(email);
  audit(null, "platform", a.id, a.email, "platform.login", "platform", null, {});
  json(res, 200, { ok: true, admin: { id: a.id, name: a.name, email: a.email } });
}
function apiPlatformLogout(req, res, url, s) {
  if (s.ptid) run("DELETE FROM platform_sessions WHERE ptid=?", s.ptid);
  res.setHeader("Set-Cookie", "azp=; Path=/; Max-Age=0");
  json(res, 200, { ok: true });
}
function apiPlatformMe(req, res, url, s) {
  json(res, 200, { admin: s.platform_admin, allowed: prbac.allowedSections(s.platform_admin), money: require("./defaults.js").platformMoney() });
}

/* THE UNIFIED IDENTITY — one call answers "who is signed in, and what may they
   do, across both scopes". This is what the merged console boots against: it
   learns its store authority and its platform authority in a single round trip,
   with every grant namespaced by scope, so the nav can render one tree whose
   leaves carry their own surface.
   A client holding only a store session sees store grants; only a platform
   session sees platform grants; both sees both — never blended, because authz
   keeps the surfaces disjoint. */
/* the sections a role screen may offer: the built surface plus the configured apps that
   belong to this scope (a store sees the platform's apps and its own, never another
   store's), each app labelled so the screen can name it */
function storeSections(tid) {
  const mine = new Set(authz.appsFor(tid).map(a => a.section));
  return rbac.SECTIONS.filter(k => !authz.isAppSection(k) || mine.has(k));
}
function platformSections() {
  const plat = new Set(authz.configuredApps().filter(a => !a.tenant_id).map(a => a.section));
  return prbac.SECTIONS.filter(k => !authz.isAppSection(k) || plat.has(k));
}
const appInfo = a => ({ key: a.key, section: a.section, label: a.label, icon: a.icon, composed: a.composed });
function apiAuthMe(req, res, url, s) {
  const urow = s.user_id ? get("SELECT id,name,email,role,staff_role,perms,tenant_id FROM users WHERE id=?", s.user_id) : null;
  const storeUser = urow && urow.role === "admin" ? urow : null;
  const identity = { store: storeUser, platform: s.platform_admin || null, tenantId: T(s) };
  json(res, 200, {
    ok: true,
    /* how platform amounts are shown (the platform's currency and locale) */
    money: require("./defaults.js").platformMoney(),
    user: s.user_id ? get("SELECT id,name,email,role FROM users WHERE id=?", s.user_id) : null,
    admin: s.platform_admin || null,
    tenant: s.tenant ? { id: s.tenant.id, slug: s.tenant.slug, name: s.tenant.name, kind: kindBrief(s.tenant) } : null,
    identity,
    /* the combined grant map, scope-namespaced: { "store:orders": "write", ... } */
    grants: authz.grant(identity),
    /* and per-scope allowance lists for the consoles' existing canSee() shapes */
    allowedSections: storeUser ? rbac.allowedSections(storeUser, T(s)) : [],
    platformAllowed: s.platform_admin ? prbac.allowedSections(s.platform_admin) : [],
    hasStore: !!storeUser, hasPlatform: !!s.platform_admin,
    /* the configured apps each scope may open — the console lists them in its nav */
    apps: {
      store: storeUser ? (() => { const al = rbac.allowedSections(storeUser, T(s)); return authz.appsFor(T(s)).filter(a => al.includes(a.section)).map(appInfo); })() : [],
      platform: s.platform_admin ? (() => { const al = prbac.allowedSections(s.platform_admin); return authz.configuredApps().filter(a => !a.tenant_id && al.includes(a.section)).map(appInfo); })() : []
    }
  });
}

/* ────────────────────────────────────────────────────────────────
   PLATFORM ADMIN ACCOUNTS — the console's own user base.

   The seed creates exactly one platform owner, and for the whole
   history of this build that was the *only* way to get a platform
   account: newPlatformAdmin() was called solely by the seed. So a
   second operator — a support admin, a second owner — had to be
   created by hand in SQLite, which is impossible in practice
   because the credentials are scrypt(v2) + peppered and the pepper
   context ("pa:" + email) is baked into the hash.

   This is the CRUD surface that fixes it. Platform-only, audited on
   the global hash-chained log, and it reuses the *same* primitives
   the seed and the login path use — newPlatformAdmin / hashPasswordFor
   / checkPassword — so a created account signs in at /platform.html
   with no second code path and no divergent hashing.
   ──────────────────────────────────────────────────────────────── */
function apiPlatformAdmins(req, res, url, s, body) {
  if (!requirePlatformSection(s, res, "padmins", "read")) return;
  if (req.method === "GET") {
    const admins = all("SELECT id,name,email,role,kdf_version,created_at FROM platform_admins ORDER BY id").map(a => ({
      ...a,
      you: a.id === (s.platform_admin && s.platform_admin.id)
    }));
    return json(res, 200, { admins, roles: prbac.roles(), sections: platformSections(), apps: authz.configuredApps().filter(a => !a.tenant_id).map(appInfo) });
  }
  if (req.method === "POST") {
    if (!requirePlatformSection(s, res, "padmins", "write")) return;
    const name = String(body.name || "").trim();
    const email = String(body.email || "").trim().toLowerCase();
    const pw = String(body.password || "");
    const role = String(body.role || "support");
    if (name.length < 2) return bad(res, "Name must be at least 2 characters");
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return bad(res, "A valid email is required");
    if (get("SELECT id FROM platform_admins WHERE email=?", email)) return bad(res, "That email is already a platform admin", 409);
    /* the store login and the platform login refuse each other's accounts
       (see apiPlatformLogin + the store login), so an email that already
       belongs to a store console can never become a platform account */
    if (get("SELECT id FROM users WHERE email=? LIMIT 1", email)) return bad(res, "That email is already a store-console account — use a different address", 409);
    const pol = sec.checkPassword(pw, email);
    if (pol) return bad(res, pol);
    if (!prbac.role(role)) return bad(res, "Unknown platform role");
    const id = newPlatformAdmin(name, email, pw);
    run("UPDATE platform_admins SET role=? WHERE id=?", role, id);
    audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "platform_admin.create", "platform_admin", id, { name, email, role }, ipOf(req), s.trace);
    return json(res, 200, { ok: true, id });
  }
  return bad(res, "Method not allowed", 405);
}
function apiPlatformAdminUpdate(req, res, url, s, body, id) {
  if (!requirePlatformSection(s, res, "padmins", "write")) return;
  const aid = Number(id);
  const a = get("SELECT id,name,email,role FROM platform_admins WHERE id=?", aid);
  if (!a) return bad(res, "Platform admin not found", 404);
  const name = String(body.name || "").trim();
  const email = String(body.email || "").trim().toLowerCase();
  if (name.length < 2) return bad(res, "Name must be at least 2 characters");
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return bad(res, "A valid email is required");
  if (email !== a.email) {
    if (get("SELECT id FROM platform_admins WHERE email=?", email)) return bad(res, "That email is already a platform admin", 409);
    if (get("SELECT id FROM users WHERE email=? LIMIT 1", email)) return bad(res, "That email is already a store-console account", 409);
  }
  const pw = body.password != null ? String(body.password) : "";
  if (pw) {
    const pol = sec.checkPassword(pw, email);
    if (pol) return bad(res, pol);
  }
  /* role + per-user override layer, on the same contract as store staff roles */
  const role = body.role != null ? String(body.role) : a.role;
  if (role && !prbac.role(role)) return bad(res, "Unknown platform role");
  const perms = body.perms != null ? JSON.stringify(body.perms) : null;
  if (name !== a.name || email !== a.email) run("UPDATE platform_admins SET name=?, email=? WHERE id=?", name, email, aid);
  if (role !== a.role) run("UPDATE platform_admins SET role=? WHERE id=?", role || null, aid);
  if (perms) run("UPDATE platform_admins SET perms=? WHERE id=?", perms, aid);
  if (pw) {
    /* re-hash exactly as the seed does; the pepper context is the NEW email,
       so a rename and a reset in one call still leaves a verifiable credential */
    const salt = sec.newSalt(); const ver = sec.currentKdf();
    run("UPDATE platform_admins SET salt=?, hash=?, kdf_version=? WHERE id=?", salt, hashPasswordFor(pw, salt, ver, "pa:" + email), ver, aid);
    /* a password change invalidates every platform session this operator holds */
    run("DELETE FROM platform_sessions WHERE admin_id=?", aid);
  }
  audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "platform_admin.update", "platform_admin", aid,
    { name, email, renamed: email !== a.email, password_reset: !!pw, role: role || null, perms_changed: !!perms }, ipOf(req), s.trace);
  return json(res, 200, { ok: true });
}
function apiPlatformAdminDelete(req, res, url, s, body, id) {
  if (!requirePlatformSection(s, res, "padmins", "write")) return;
  const aid = Number(id);
  if (aid === Number(s.platform_admin.id)) return bad(res, "You cannot delete your own account");
  const a = get("SELECT id,email FROM platform_admins WHERE id=?", aid);
  if (!a) return bad(res, "Platform admin not found", 404);
  /* the platform must always keep one operator — the same guard the store
     console applies to its own staff (apiStaffDelete) */
  if (get("SELECT COUNT(*) c FROM platform_admins").c <= 1) return bad(res, "The platform must keep at least one admin");
  run("DELETE FROM platform_sessions WHERE admin_id=?", aid);
  run("DELETE FROM platform_admins WHERE id=?", aid);
  audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "platform_admin.delete", "platform_admin", aid, { email: a.email }, ipOf(req), s.trace);
  return json(res, 200, { ok: true });
}
/* the platform role catalog + the caller's own grants — the console reads this to
   filter its nav and to render the role picker. Owner-only writes stay open to every
   admin so a role can never lock the console's own user management. */
function apiPlatformRoles(req, res, url, s) {
  if (!requirePlatformSection(s, res, "padmins", "read")) return;
  json(res, 200, { roles: prbac.roles(), sections: platformSections(), apps: authz.configuredApps().filter(a => !a.tenant_id).map(appInfo), me: { admin: s.platform_admin, allowed: prbac.allowedSections(s.platform_admin) } });
}
/* ---------- role management ----------
   Both grant surfaces the platform enforces are DATA in meta_lists, so defining a role
   and its rights is a console operation, never a deploy. One pair of handlers per
   surface, sharing a shape: the platform surface ('roles') governs this console's own
   operators (prbac); the staff surface ('roles/staff') governs every store's team
   (rbac). Both write through the engines, which validate against that surface's own
   section list and stamp the row edited so the seed's self-heal never reverts an
   operator's intent. Gated on roles:write — reading is the padmins read grant the
   console already needed, writing the roles themselves is a distinct trust. */
function apiPlatformRoleSave(req, res, url, s, body) {
  if (!requirePlatformSection(s, res, "roles", "write")) return;
  const r = prbac.upsertRole(body || {});
  if (!r.ok) return bad(res, (r.fails || []).join("; "), 400);
  logAction(s, "platform.role.save", "role", r.role.key, { name: r.role.name });
  json(res, 200, { ok: true, role: r.role, roles: prbac.roles() });
}
function apiPlatformRoleDelete(req, res, url, s, body, key) {
  if (!requirePlatformSection(s, res, "roles", "write")) return;
  const r = prbac.deleteRole(key);
  if (!r.ok) return bad(res, (r.fails || []).join("; "), 400);
  logAction(s, "platform.role.delete", "role", key, {});
  json(res, 200, { ok: true, roles: prbac.roles() });
}
/* the store-staff surface. Each store may carry its OWN role set (rbac 'staffRoles:t<id>'),
   so the platform console edits the set the selected store actually enforces: name a store
   in the body to fork/edit that store's set, or omit it to edit the shared default every
   un-forked store inherits. rbac.upsertRole takes (tenantId, role) — the store first, the
   role second — and the first save to a store forks the full inherited set, so a store
   never starts empty. */
function apiStaffRoleSave(req, res, url, s, body) {
  if (!requirePlatformSection(s, res, "roles", "write")) return;
  const tid = body && body.tenant_id ? Number(body.tenant_id) : 0;
  if (tid && !get("SELECT id FROM tenants WHERE id=?", tid)) return bad(res, "Unknown store", 400);
  const r = rbac.upsertRole(tid, body || {});
  if (!r.ok) return bad(res, (r.fails || []).join("; "), 400);
  logAction(s, "platform.role.save", tid ? "staffRole:t" + tid : "staffRole", r.role.key, { name: r.role.name, tenant_id: tid || null });
  json(res, 200, { ok: true, role: r.role, roles: rbac.roles(tid), tenant_id: tid || null, ownSet: tid ? true : false });
}
function apiStaffRoleDelete(req, res, url, s, body, key) {
  if (!requirePlatformSection(s, res, "roles", "write")) return;
  const tid = body && body.tenant_id ? Number(body.tenant_id) : 0;
  if (tid && !get("SELECT id FROM tenants WHERE id=?", tid)) return bad(res, "Unknown store", 400);
  const r = rbac.deleteRole(tid, key);
  if (!r.ok) return bad(res, (r.fails || []).join("; "), 400);
  logAction(s, "platform.role.delete", tid ? "staffRole:t" + tid : "staffRole", key, { tenant_id: tid || null });
  json(res, 200, { ok: true, roles: rbac.roles(tid) });
}
/* ---------- user creation ----------
   An account belongs to exactly one store (UNIQUE(tenant_id,email)), so the platform
   console creates one INTO a chosen store — the store picker is the domain the role is
   scoped against. A store admin's authority is a staff role from the store surface
   (rbac); a customer carries none. The password runs through the same policy the
   storefront signup enforces, so a platform-created account is never a weak back door,
   and an omitted password is generated server-side and shown once. */
function apiPlatformUserCreate(req, res, url, s, body) {
  if (!requirePlatformSection(s, res, "users", "write")) return;
  const tid = Number(body.tenant_id);
  if (!get("SELECT id FROM tenants WHERE id=?", tid)) return bad(res, "Choose the store this user belongs to", 400);
  const name = String(body.name || "").trim();
  const email = String(body.email || "").toLowerCase().trim();
  if (!name || !email) return bad(res, "Name and email are required", 400);
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return bad(res, "That email address is not valid", 400);
  const role = body.role === "admin" ? "admin" : "customer";
  const staffRole = role === "admin" ? String(body.staff_role || require("./defaults.js").of("staffRoles")) : null;
  if (staffRole && rbac.role(tid, staffRole) === null) return bad(res, "Unknown staff role: " + staffRole, 400);
  if (get("SELECT id FROM users WHERE tenant_id=? AND email=?", tid, email))
    return bad(res, "That email already has an account on this store", 409);
  const pw = String(body.password || crypto.randomBytes(9).toString("hex"));
  const policyErr = sec.checkPassword(pw, email);
  if (policyErr) return bad(res, policyErr, 400);
  const id = newUser(tid, name, email, pw, role);
  if (staffRole) run("UPDATE users SET staff_role=? WHERE id=?", staffRole, id);
  logAction(s, "platform.user.create", "user", id, { email, tenant_id: tid, role, staff_role: staffRole }, req);
  json(res, 200, { ok: true, id, generated: body.password ? undefined : pw });
}
/* a store's place facts, from the kernel (lib/stores.js): its jurisdiction, the country it lies
   in, and every place it serves — never a column of its row */
function storeFacts(tid) {
  const st = require("./stores.js");
  return { country: st.country(tid), jurisdiction: st.jurisdiction(tid), places: st.served(tid) };
}
function apiPlatformTenants(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const tenants = all(`SELECT t.*, (SELECT COUNT(*) FROM products p WHERE p.tenant_id=t.id) products, (SELECT COUNT(*) FROM orders o WHERE o.tenant_id=t.id) orders,
    (SELECT COALESCE(SUM(o.total),0) FROM orders o WHERE o.tenant_id=t.id) gmv,
    (SELECT p.name FROM subscriptions s JOIN plans p ON p.id=s.plan_id WHERE s.tenant_id=t.id ORDER BY s.id DESC) plan,
    (SELECT s.status FROM subscriptions s WHERE s.tenant_id=t.id ORDER BY s.id DESC) sub_status
    FROM tenants t ORDER BY t.id`);
  const ks = Object.fromEntries(registry.kinds().map(k => [k.key, k]));
  tenants.forEach(t => { Object.assign(t, storeFacts(t.id)); t.profile = J(t.profile, {}); const k = ks[t.mode]; t.kind = k ? { key: k.key, name: k.name, noun: k.noun } : { key: t.mode, name: t.mode, noun: registry.KIND_DEFAULTS.noun }; });
  /* what each platform's state means, so the console labels suspend / resume by meaning */
  tenants.forEach(t => { t.operating = stIs("tenant", t.status, "operating"); });
  json(res, 200, { tenants });
}
/* PLATFORM KINDS — the kinds of platform the operator can launch, any number of each.
   A kind is a deployModes registry row (lib/registry.js normKind); this surface adds what
   the console needs to edit one: how many platforms of each kind exist, the blends a kind
   can start from, and the console sections a kind can include — named as the menu names
   them, with the capabilities that own the rest. */
/* ---------------- applicability rules (lib/rules.js) ----------------
   the platform owner's layer bounds every platform; each platform narrows its own. The
   vocabularies (subject types, dimensions, services, segments, channels, banks, country
   groups) are registry rows — the console offers whatever they hold. */
function apiPlatformRules(req, res, url, s) {
  if (!requirePlatformSection(s, res, "applicability", "read")) return;
  json(res, 200, { schema: rules.schema(), rules: rules.listRules(null), platformRules: all("SELECT tenant_id, COUNT(*) n FROM applicability_rules WHERE tenant_id IS NOT NULL GROUP BY tenant_id") });
}
function apiPlatformRuleSave(req, res, url, s, body) {
  if (!requirePlatformSection(s, res, "applicability", "write")) return;
  const r = rules.save(body && body.rule || {}, null, s.platform_admin.email);
  if (r.error) return bad(res, r.error, r.status || 400);
  audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "rule.save", "applicability_rule", r.rule.id, { summary: r.rule.summary });
  json(res, 200, r);
}
function apiPlatformRuleDelete(req, res, url, s, body, id) {
  if (!requirePlatformSection(s, res, "applicability", "write")) return;
  const r = rules.remove(id, null);
  if (r.error) return bad(res, r.error, r.status || 400);
  audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "rule.delete", "applicability_rule", Number(id), {});
  json(res, 200, r);
}
function apiPlatformRuleExplain(req, res, url, s, body) {
  if (!requirePlatformSection(s, res, "applicability", "read")) return;
  const type = String(body && body.type || "");
  if (!rules.schema().subjectTypes.some(t => t.key === type)) return bad(res, "Unknown subject type " + type, 400);
  const ctx = rules.explainContext(null, body && body.context);
  json(res, 200, { context: ctx, results: rules.explain(type, ctx) });
}
function apiAdminRules(req, res, url, s) {
  if (!requireSection(s, res, "applicability", "read", "applicability")) return;
  /* the platform rules that can reach this platform, and an editor without the dimensions
     that name a platform's identity (a platform narrows itself only) */
  json(res, 200, { schema: rules.schema({ tenant: true }), rules: rules.listRules(T(s)), inherited: rules.inheritedBy(T(s)), members: rules.members(T(s)), platform: rules.platformFacts(T(s)) });
}
/* what a rule can name, per subject type — enumerated by the type's registered source */
function apiPlatformRuleSubjects(req, res, url, s) {
  if (!requirePlatformSection(s, res, "applicability", "read")) return;
  json(res, 200, { subjects: rules.subjects(String(url.searchParams.get("type") || ""), null) });
}
function apiAdminRuleSubjects(req, res, url, s) {
  if (!requireSection(s, res, "applicability", "read", "applicability")) return;
  json(res, 200, { subjects: rules.subjects(String(url.searchParams.get("type") || ""), T(s)) });
}
function apiAdminRuleSave(req, res, url, s, body) {
  if (!requireSection(s, res, "applicability", "write", "applicability")) return;
  const r = rules.save(body && body.rule || {}, T(s), actor(s)[2]);
  if (r.error) return bad(res, r.error, r.status || 400);
  logAction(s, "rule.save", "applicability_rule", r.rule.id, { summary: r.rule.summary }, req);
  json(res, 200, r);
}
function apiAdminRuleDelete(req, res, url, s, body, id) {
  if (!requireSection(s, res, "applicability", "write", "applicability")) return;
  const r = rules.remove(id, T(s));
  if (r.error) return bad(res, r.error, r.status || 400);
  logAction(s, "rule.delete", "applicability_rule", Number(id), {}, req);
  json(res, 200, r);
}
function apiAdminRuleExplain(req, res, url, s, body) {
  if (!requireSection(s, res, "applicability", "read", "applicability")) return;
  const type = String(body && body.type || "");
  if (!rules.schema().subjectTypes.some(t => t.key === type)) return bad(res, "Unknown subject type " + type, 400);
  const ctx = rules.explainContext(T(s), body && body.context, { tenant: true });
  json(res, 200, { context: ctx, results: rules.explain(type, ctx) });
}
/* hand-assigned segment memberships, by the customer's email or their owner id */
function apiAdminSegmentMemberAdd(req, res, url, s, body) {
  if (!requireSection(s, res, "applicability", "write", "applicability")) return;
  let owner = String(body && body.owner || "").trim();
  const email = String(body && body.email || "").trim().toLowerCase();
  if (email) { const u = get("SELECT id FROM users WHERE tenant_id=? AND lower(email)=?", T(s), email); if (!u) return bad(res, "No customer with that email on this platform", 404); owner = `t${T(s)}:u:${u.id}`; }
  if (!owner.startsWith("t" + T(s) + ":")) return bad(res, "owner must belong to this platform", 400);
  const r = rules.addMember(T(s), owner, body && body.segment);
  if (r.error) return bad(res, r.error, 400);
  logAction(s, "segment.member.add", "segment", String(body.segment), { owner }, req);
  json(res, 200, { ok: true, members: rules.members(T(s)) });
}
function apiAdminSegmentMemberDelete(req, res, url, s, body, id) {
  if (!requireSection(s, res, "applicability", "write", "applicability")) return;
  rules.removeMember(T(s), id);
  json(res, 200, { ok: true, members: rules.members(T(s)) });
}
/* the one question any engine, integration or page — today's or tomorrow's — can ask:
   may <type>/<id> be used in this request's context (plus anything the caller adds)? A
   shopper learns the verdict; console callers also see the reasons. */
function apiRulesCheck(req, res, url, s, body) {
  const b = body || {};
  const type = String(b.type || ""), id = String(b.id || "");
  if (!type || !id) return bad(res, "type and id required", 400);
  if (!rules.schema().subjectTypes.some(t => t.key === type)) return bad(res, "Unknown subject type " + type, 400);
  /* the caller may state only what a request may state (never a platform's identity, never
     a computed fact such as its own segments) */
  const d = rules.decide(type, id, rules.context(T(s), rules.requestFacts(b.context)));
  const staff = s.platform_admin || isAdmin(s);
  json(res, 200, staff ? d : { ok: d.ok, verdict: d.verdict });
}
function apiPlatformKinds(req, res, url, s) {
  if (!requirePlatformSection(s, res, "tenants", "read")) return;
  const counts = Object.fromEntries(all("SELECT mode, COUNT(*) n FROM tenants GROUP BY mode").map(r => [r.mode, r.n]));
  const presets = all("SELECT key,label,description FROM capability_presets ORDER BY label");
  const labels = (() => { try { return require("./canonical.js").consoleSec().adminLabels || {}; } catch (e) { return {}; } })();
  const navSec = (() => { try { return require("./canonical.js").consoleSec().adminNavSec || {}; } catch (e) { return {}; } })();
  const owners = authz.capabilitySections();
  const byKey = {};
  for (const [leaf, label] of Object.entries(labels)) { const k = navSec[leaf] || leaf; (byKey[k] = byKey[k] || []).push(label); }
  const sections = authz.SURFACES.store.filter(k => !/^app_/.test(k)).map(k => ({ key: k, label: (byKey[k] || [k]).join(" · "), capabilities: owners.get(k) || [] }));
  json(res, 200, { kinds: registry.kinds().map(k => ({ ...k, platforms: counts[k.key] || 0 })), presets, sections, defaults: registry.KIND_DEFAULTS });
}
function apiPlatformKindSave(req, res, url, s, body) {
  if (!requirePlatformSection(s, res, "tenants", "write")) return;
  const it = body && body.kind;
  if (!it || typeof it !== "object") return bad(res, "kind required", 400);
  const sections = it.sections == null ? null : (Array.isArray(it.sections) ? [...new Set(it.sections.map(String))] : it.sections);
  /* a section a capability owns is never on a kind's list — the capability decides it */
  const owned = authz.capabilitySections();
  const item = { key: String(it.key || "").trim(), name: String(it.name || "").trim().slice(0, 60), desc: String(it.desc || "").trim().slice(0, 200),
    needsIndustries: !!it.needsIndustries, noun: String(it.noun || "").trim().slice(0, 30) || registry.KIND_DEFAULTS.noun,
    nounPlural: String(it.nounPlural || "").trim().slice(0, 30) || registry.KIND_DEFAULTS.nounPlural, archetype: String(it.archetype || "").trim(),
    provision: it.provision && typeof it.provision === "object" ? Object.fromEntries(Object.keys(registry.KIND_DEFAULTS.provision).map(k => [k, it.provision[k] !== false])) : registry.KIND_DEFAULTS.provision,
    sections: Array.isArray(sections) ? sections.filter(k => !owned.has(k)) : sections };
  const r = registry.saveItem("deployModes", item);
  if (!r.ok) return bad(res, r.error, 400);
  audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "kind.save", "kind", item.key, { name: item.name, archetype: item.archetype });
  json(res, 200, { kind: registry.kind(item.key) });
}
function apiPlatformKindDelete(req, res, url, s, body, key) {
  if (!requirePlatformSection(s, res, "tenants", "write")) return;
  const r = registry.deleteItem("deployModes", decodeURIComponent(String(key || "")));
  if (!r.ok) return bad(res, r.error, 409);
  audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "kind.delete", "kind", r.key, {});
  json(res, 200, { ok: true });
}
/* Setup-wizard progress: one store, every step marked done or pending. Powers the
   "what's left" checklist after (or during) launch. */
function apiPlatformTenantSetup(req, res, url, s, body, id) {
  if (!requirePlatform(s, res)) return;
  const row = get("SELECT * FROM tenants WHERE id=?", Number(id));
  if (!row) return bad(res, "Unknown tenant", 404);
  const t = { ...row, ...storeFacts(row.id) };
  const c = settings.load(t.id);
  const prof = J(t.profile, {});
  const payGw = all("SELECT provider_id FROM tenant_gateways WHERE tenant_id=? AND provider_id NOT LIKE 'ship:%' AND provider_id NOT LIKE 'notify:%'", t.id).map(r => r.provider_id);
  const shipGw = all("SELECT provider_id FROM tenant_gateways WHERE tenant_id=? AND provider_id LIKE 'ship:%'", t.id).map(r => r.provider_id.replace(/^ship:/, ""));
  const products = get("SELECT COUNT(*) n FROM products WHERE tenant_id=?", t.id).n;
  const sub = get("SELECT plan_id FROM subscriptions WHERE tenant_id=? ORDER BY id DESC LIMIT 1", t.id);
  const taxSet = c.commerce.taxMode != null || c.commerce.taxRate != null;
  const ships = registry.providersFor("shipping", t.country).map(x => x.id);
  const kd = registry.kind(t.mode) || registry.normKind({ key: t.mode });
  const atoms = get("SELECT COUNT(*) n FROM capability_values WHERE tenant_id=? AND enabled=1", t.id).n;
  const steps = [
    { key: "identity", label: "Identity & branding", done: !!(t.name && t.slug && c.brand && c.brand.tagline && c.brand.tagline !== settings.DEFAULTS.brand.tagline), note: t.name },
    { key: "owner", label: "Owner / admin account", done: !!(prof.ownerEmail || get("SELECT 1 ok FROM users WHERE tenant_id=? AND role='admin'", t.id)), note: prof.ownerEmail || "—" },
    { key: "jurisdiction", label: "Jurisdiction & legal identity", done: !!(t.country && prof.legalName), note: t.country },
    { key: "tax", label: "Tax configuration", done: taxSet, note: c.commerce.taxMode ? c.commerce.taxMode : (c.commerce.taxRate != null ? String((c.commerce.taxRate * 100).toFixed(1)) + "%" : "country default") },
    { key: "payments", label: "Payment gateways", done: payGw.length > 0, note: payGw.length ? payGw.join(", ") : "none enabled" },
    { key: "shipping", label: "Shipping & delivery", done: shipGw.length > 0 && c.commerce.freeShipThreshold > 0, note: shipGw.length ? shipGw.join(", ") + " · free over " + c.commerce.freeShipThreshold : "none" },
    { key: "catalogue", label: "Catalogue seeded", done: products > 0, note: products + " products" },
    { key: "features", label: "Shopper features chosen", done: !!(c.features && (c.features.reviews || c.features.deals || c.features.membership || c.features.subscribeSave)), note: c.features ? Object.entries(c.features).filter(([, v]) => v).map(([k]) => k).slice(0, 5).join(", ") : "—" },
    { key: "capabilities", label: "Capabilities composed", done: atoms > 0, note: atoms + " switched on" },
    { key: "plan", label: "Subscription plan", done: !!sub, note: sub ? "plan #" + sub.plan_id : "no plan" }
  /* a step the platform's kind is not provisioned for is not a step for it — a ride-hailing
     operator ships nothing and has no shopfront to fill */
  ].filter(x => !STEP_NEEDS[x.key] || kd.provision[STEP_NEEDS[x.key]]);
  json(res, 200, { tenant: { ...t, profile: prof }, kind: { key: kd.key, name: kd.name, noun: kd.noun, provision: kd.provision }, settings: { brand: c.brand, theme: c.theme, commerce: c.commerce, features: c.features }, gateways: { pay: payGw, ship: shipGw }, steps, done: steps.filter(x => x.done).length, total: steps.length, available: { shipping: ships, payments: registry.providersFor("payment", t.country).map(p => p.id) } });
}
/* what the consoles need to name a platform by its kind ("Operator console", "Company settings") */
function kindBrief(t) {
  const k = t && registry.kind(String(t.mode || ""));
  return k ? { key: k.key, name: k.name, noun: k.noun, nounPlural: k.nounPlural, storefront: k.provision.storefront } : null;
}
/* which provisioning switch a setup step depends on (steps not named apply to every kind) */
const STEP_NEEDS = { payments: "payments", shipping: "shipping", catalogue: "storefront", features: "storefront" };
/* a deploy mode is a registry row: the named one when it exists, else the platform's
   configured default, else the registry's first — never a literal */
function deployModeOr(want) {
  const modes = rl("deployModes");
  const has = k => modes.some(m => m.key === k);
  if (has(want)) return want;
  const dflt = sec.policy().provisioning.defaultMode;
  return has(dflt) ? dflt : (modes[0] ? modes[0].key : "marketplace");
}
/* whether a mode requires industries is the mode row's own flag; a row saved before the
   flag existed takes the shipped default for its key, and an operator's mode without it
   requires none */
function modeNeedsIndustries(key) {
  const row = rl("deployModes").find(m => m.key === key);
  if (row && row.needsIndustries != null) return !!row.needsIndustries;
  const seed = require("./meta.js").DEPLOY_MODES.find(m => m.key === key);
  return !!(seed && seed.needsIndustries);
}
function tenantPayload(body) {
  /* shared validation+normalization for create & update — jurisdiction, taxation, categories, owner, gateways, plan */
  const j = body.jurisdiction || {};
  const country = registry.country(String(j.country || body.country || sec.defaultCountry()).toUpperCase());
  const industries = (Array.isArray(body.industries) ? body.industries : []).filter(k => registry.list("industries").some(i => i.key === k));
  const mode = deployModeOr(body.mode);
  let owner = body.owner || null;
  if (!owner && (body.ownerEmail || body.adminEmail)) owner = { name: body.ownerName || body.adminName || "Store Admin", email: body.ownerEmail || body.adminEmail, password: body.ownerPassword || body.adminPassword, phone: body.ownerPhone || "" };
  const tax = body.tax || null;
  const gateways = Array.isArray(body.gateways) && body.gateways.length ? body.gateways : null;
  const planId = body.plan_id != null ? Number(body.plan_id) : null;
  return { j, country, industries, mode, owner, tax, gateways, planId };
}
function applyCountryAndTax(tid, country, tax) {
  const c = settings.load(tid);
  const wantMode = tax && tax.mode ? String(tax.mode) : null;
  const taxMode = wantMode && get("SELECT key FROM tax_modes WHERE key=?", wantMode) ? wantMode : (tax && tax.mode ? null : null);
  const over = !!(tax && (tax.mode || (tax.rate != null && tax.rate !== "")));
  const taxRate = over && tax.rate != null && tax.rate !== "" ? Number(tax.rate) : null;
  /* the country is the store's jurisdiction on the kernel; settings.save moves it there */
  settings.save(tid, { commerce: { ...c.commerce, country: country.code, currency: null, symbol: null, locale: null, decimals: null, taxMode: taxMode, taxRate: taxRate } });
}
function provisionGateways(tid, country, gateways, opts) {
  const o = opts || {};
  /* how many of the country's gateways a store starts with, and which cash and house
     providers ride along, are platform policy (Provisioning → New-store defaults) */
  const prov = sec.policy().provisioning;
  const nPay = Math.max(0, Number(prov.paymentGatewaysPerStore) || 0), cash = String(prov.cashGateway || "").trim();
  const nShip = Math.max(0, Number(prov.carriersPerStore) || 0), house = String(prov.houseShipping || "").trim();
  /* a country's own providers come before the worldwide ones (provider_defs.global), so an
     Indian platform starts with Razorpay and UPI rather than the first global gateways in
     the list; then the applicability rules decide for this platform — a denied provider is
     never provisioned and a preferred one is provisioned first */
  /* the platform's own row (kind, country…) is the context; a re-provision after a country
     change must not read a cached one */
  rules.bust();
  const rctx = rules.at("provision.gateways", tid, { buyer: false });
  const ranked = (kind, point) => {
    const glob = new Set(all("SELECT id FROM provider_defs WHERE kind=? AND global=1", kind).map(r => r.id));
    const list = registry.providersFor(kind, country.code).map((p, i) => ({ p, i })).sort((a, b) => (glob.has(a.p.id) ? 1 : 0) - (glob.has(b.p.id) ? 1 : 0) || a.i - b.i).map(x => x.p);
    return rules.filterAt(point, list, rctx).map(x => x.it);
  };
  let pays = gateways ? gateways.filter(p => registry.supports(p, country.code)) : ranked("payment", "provision.gateways").filter(p => p.id !== cash).slice(0, nPay).map(p => p.id).concat(cash && rules.permitsAt("provision.gateways", cash, rctx) ? [cash] : []);
  pays = [...new Set(pays)];
  if (!pays.length && cash) pays = [cash];
  /* a kind that takes no payments, or ships nothing, is provisioned with none */
  if (o.payments === false) pays = [];
  run("DELETE FROM tenant_gateways WHERE tenant_id=? AND provider_id NOT LIKE 'ship:%' AND provider_id NOT LIKE 'notify:%'", tid);
  const gmode = sec.policy().provisioning.sandboxGatewaysByDefault ? "sandbox" : "live";
  pays.forEach((p, i) => run("INSERT INTO tenant_gateways(tenant_id,provider_id,is_primary,mode,config,position) VALUES(?,?,?,?,'{}',?)", tid, p, i === 0 ? 1 : 0, gmode, i));
  /* the setup wizard may name its carriers explicitly; otherwise the country's first
     two real carriers ride along with house shipping. */
  const availShip = registry.providersFor("shipping", country.code);
  /* a carrier the store runs itself declares `in_house` on its spec; the "real" carriers are the rest */
  const inHouse = new Set(all("SELECT id, spec FROM provider_defs WHERE kind='shipping'").filter(r => { try { return !!JSON.parse(r.spec || "{}").in_house; } catch (e) { return false; } }).map(r => r.id));
  let shipIds = Array.isArray(o.shipping) ? o.shipping.filter(x => availShip.some(s => s.id === x)) : ranked("shipping", "provision.carriers").filter(x => !inHouse.has(x.id)).slice(0, nShip).map(x => x.id);
  shipIds = [...new Set((house ? [house] : []).concat(shipIds))];
  if (o.shipping === false) shipIds = [];
  run("DELETE FROM tenant_gateways WHERE tenant_id=? AND provider_id LIKE 'ship:%'", tid);
  shipIds.forEach((x, i) => run("INSERT INTO tenant_gateways(tenant_id,provider_id,is_primary,mode,config,position) VALUES(?,?,?,'live','{}',?)", tid, "ship:" + x, i === 0 ? 1 : 0, i));
  return pays;
}
function apiPlatformTenantCreate(req, res, url, s, body) {
  if (!requirePlatformSection(s, res, "tenants", "write")) return;
  
  // Enhanced branding & config
  const branding = {
    name: String(body.brand?.name || body.name || "Store"),
    logo: body.brand?.logo || null,
    tagline: body.brand?.tagline || body.tagline || "A new storefront on LUXORA Platform",
    colors: JSON.stringify(body.brand?.colors || {})
  };
  
  const slug = String(body.slug || "").trim().toLowerCase().replace(/[^a-z0-9-]/g, "-").slice(0, 30);
  if (!slug || !body.name) return bad(res, "Store name and slug are required");
  if (get("SELECT id FROM tenants WHERE slug=?", slug)) return bad(res, "Slug already taken", 409);
  const p = tenantPayload(body);
  if (!p.country) return bad(res, "Pick a valid jurisdiction country — available: " + registry.countries().map(c => c.code).join(", "));
  if (modeNeedsIndustries(p.mode) && !p.industries.length) return bad(res, "Select at least one industry (product categories) for a " + p.mode + " store");
  if (p.owner && p.owner.email) {
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(p.owner.email) || String(p.owner.name || "").trim().length < 2)
      return bad(res, "Owner needs a full name and a valid email");
    /* the owner's password meets the platform's own credential policy, like every other */
    const weak = sec.checkPassword(String(p.owner.password || ""), p.owner.email);
    if (weak) return bad(res, "Owner password: " + weak);
  }
  const prov = sec.policy().provisioning;
  /* the kind of platform this is: its own row says what it starts with and what it is
     provisioned with, so a ride-hailing operator is not set up as a shop */
  const kd = registry.kind(p.mode) || registry.normKind({ key: p.mode });
  if (body.seedCatalog == null) body.seedCatalog = kd.provision.storefront ? prov.seedCatalogByDefault : false;
  const planId = p.planId || prov.defaultPlanId;
  if (!get("SELECT id FROM plans WHERE id=?", planId)) return bad(res, "Unknown plan");
  /* the registration composes a whole platform, not a shell: an archetype writes the
     store's capability rows in one call. Validated BEFORE any write so an unknown
     archetype never leaves a half-created tenant behind. */
  /* a registration that names no archetype takes its kind's starting blend; an explicit
     empty choice ("" / null) means none — composed by hand afterwards */
  const arch = body.archetype !== undefined ? (String(body.archetype == null ? "" : body.archetype).trim() || null) : (kd.archetype || null);
  if (arch && !get("SELECT key FROM capability_presets WHERE key=?", arch))
    return bad(res, "Unknown archetype: " + arch + (body.archetype === undefined ? " (the starting blend of the " + kd.name + " kind)" : "") + " — available: " + all("SELECT key FROM capability_presets ORDER BY key").map(r => r.key).join(", "), 400);
  /* identity is chosen in the same pass, from the same kind of registry: an unknown
     template id is refused before any write, and an omitted choice resolves to the
     registry's own default — so a platform is never registered without a deliberate,
     complete authentication policy. */
  const identity = require("./identity.js");
  let idTemplate = body.identity_template ? Number(body.identity_template) : null;
  if (idTemplate && !get("SELECT id FROM platform_identity_templates WHERE id=?", idTemplate))
    return bad(res, "Unknown identity template", 400);
  if (!idTemplate) {
    const dflt = identity.defaultIdentityTemplate();
    if (dflt) idTemplate = dflt.id;
  }
  const profile = {
    legalName: String(p.j.legalName || body.name).slice(0, 80), taxId: String(p.j.taxId || "").slice(0, 40),
    registrationAddress: String(p.j.registrationAddress || "").slice(0, 160), state: String(p.j.state || ""),
    ownerName: p.owner ? String(p.owner.name || "").trim() : "", ownerEmail: p.owner ? String(p.owner.email || "").toLowerCase() : "", ownerPhone: p.owner ? String(p.owner.phone || "") : "",
    locale: String(body.language || body.locale || "").slice(0, 10)
  };
  const r = run("INSERT INTO tenants(slug,name,domain,status,mode,industries,profile) VALUES(?,?,?,?,?,?,?)",
    slug, String(body.name).slice(0, 60), String(body.domain || slug + ".localhost"), states.initial("tenant"), p.mode, JSON.stringify(p.industries), JSON.stringify(profile));
  const tid = Number(r.lastInsertRowid);
  /* the two policy-gated features start on the composition (their atoms), not a
     settings row — the platform policy is the authority either way */
  caps.applyFeatures(tid, caps.policyFeatures(sec.policy().provisioning));
  settings.save(tid, { brand: { name: branding.name, wordmark: branding.name, logo: branding.logo, tagline: branding.tagline, colors: JSON.parse(branding.colors) } });
  applyCountryAndTax(tid, p.country, p.tax);
  if (body.shipping) {
    /* merge, never replace: applyCountryAndTax just wrote currency/tax into commerce */
    const cc = settings.load(tid).commerce;
    settings.save(tid, { commerce: { ...cc, freeShipThreshold: Number(body.shipping.freeShipThreshold) || 0, shipFee: Number(body.shipping.shipFee) || 0, daysPriority: Number(body.shipping.daysPriority) || Number(sec.policy().provisioning.shipDaysPriority) || 2, daysStandard: Number(body.shipping.daysStandard) || Number(sec.policy().provisioning.shipDaysStandard) || 5 } });
  }
  /* brand colours → theme tokens, because the storefront paints from CSS vars, and a
     theme assignment (if any) still wins over settings.theme. */
  const col = body.brand && body.brand.colors ? body.brand.colors : null;
  if (col) themes.unassign("tenant", tid);
  if (col) {
    const ct = settings.load(tid).theme;
    settings.save(tid, { theme: { ...ct, header: col.primary || ct.header, accent: col.accent || col.secondary || ct.accent } });
  }
  if (body.theme) themes.assign("tenant", tid, String(body.theme));
  if (body.features) {
    const pol = sec.policy().provisioning;
    const feats = {};
    for (const [k, v] of Object.entries(body.features)) {
      if (v && require("./capabilities.js").policyRefusal(k, pol)) continue;
      feats[k] = !!v;
    }
    /* atoms absorb the storefront keys; whatever is left stays on the settings row */
    const leftover = caps.applyFeatures(tid, feats);
    if (Object.keys(leftover).length) settings.save(tid, { features: leftover });
  }
  if (kd.provision.storefront) {
    seedTenantDepartments(tid, p.industries.length ? p.industries : null);
    seedTenantHome(tid, p.industries.length ? p.industries : null);
  }
  /* the platform's own warehouse, in its own country, before the demo seed — which only
     adds its sample warehouses to a tenant that has none */
  if (kd.provision.warehouse) run("INSERT INTO warehouses(tenant_id,name,code,country,region) VALUES(?,?,?,?,?)", tid, "Main DC-" + p.country.code, "DC-" + p.country.code, p.country.code, profile.state);
  seedMeta(tid, p.industries.length ? p.industries : null, { warehouses: false, storefront: kd.provision.storefront });
  if (body.seedCatalog) seedTenantCatalog(tid, p.industries.length ? p.industries : null,
    { size: Number(body.seedSize) || 0, price: body.seedPrice || {} });
  if (body.seedBrands || body.seedCatalog) seedTenantBrands(tid);
  // Apply the chosen identity template (the registry's default when none was named)
  let appliedIdentity = null;
  if (idTemplate) {
    const tmpl = get("SELECT id,name,config FROM platform_identity_templates WHERE id=?", idTemplate);
    if (tmpl) {
      const config = J(tmpl.config, {});
      identity.setIdentitySettings(tid, config);
      // Apply providers from template
      if (Array.isArray(config.providers)) for (const pr of config.providers) {
        try { identity.upsertIdentityProvider(tid, pr); } catch (e) { /* a bad provider row is skipped, not fatal */ }
      }
      appliedIdentity = { id: tmpl.id, name: tmpl.name, settings: identity.getIdentitySettings(tid) };
    }
  }
  const pays = provisionGateways(tid, p.country, p.gateways, { shipping: !kd.provision.shipping ? false : (Array.isArray(body.shippingCarriers) ? body.shippingCarriers : null), payments: kd.provision.payments });
  { const ln = mailer.localNotifier(); if (ln) run("INSERT INTO tenant_gateways(tenant_id,provider_id,is_primary,mode,config,position) VALUES(?, ?, 1, 'live', '{}', 0)", tid, "notify:" + ln); }
  if (p.owner && p.owner.email) newUser(tid, profile.ownerName, profile.ownerEmail, String(p.owner.password), "admin");
  run("INSERT INTO subscriptions(tenant_id,plan_id,status) VALUES(?,?,?)", tid, planId, states.initial("plan_subscription"));
  mods.ensureBaselines();
  /* the registration composition lands here: an archetype writes the store's capability
     rows in one call, explicit atoms extend or override it, and the chosen universes
     publish catalog content — so a marketplace, an ERP or a ride-hailing platform is
     registered complete, not created empty and configured one screen at a time */
  if (arch) caps.applyPreset(tid, arch);
  if (body.capabilities && typeof body.capabilities === "object") {
    for (const [key, entry] of Object.entries(body.capabilities)) {
      if (!entry || entry.enabled === false) continue;
      try { caps.enable(tid, String(key), (entry && entry.params) || {}); } catch (e) { /* an unknown atom is skipped, not fatal */ }
    }
  }
  /* catalog content: activate the chosen universes into the new store. With none named
     and an archetype chosen, the platform type picks a canonical set — a mobility store
     opens with ride-hailing and fleet content, an ERP with payroll and procurement. */
  let universeKeys = Array.isArray(body.universes) ? body.universes.map(String) : null;
  if (!universeKeys && arch && body.seedUniverses !== false) {
    const row = get("SELECT universes FROM capability_presets WHERE key=?", arch);
    universeKeys = (row && J(row.universes, [])) || [];
  }
  const activated = [];
  if (universeKeys && universeKeys.length) {
    const uc = require("./ucos-catalog.js");
    for (const key of universeKeys) {
      try { const r = uc.activate(tid, key); if (r && r.published) activated.push({ key, published: r.published }); }
      catch (e) { /* a universe that cannot activate is skipped, not fatal to registration */ }
    }
  }
  audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.create", "tenant", tid, { slug, kind: kd.key, country: p.country.code, industries: p.industries, gateways: pays, archetype: arch, identity_template: appliedIdentity ? appliedIdentity.name : null, universes: activated.map(a => a.key) });
  const t = get("SELECT * FROM tenants WHERE id=?", tid);
  json(res, 200, { tenant: { ...t, ...storeFacts(t.id), profile: J(t.profile, {}) }, kind: { key: kd.key, name: kd.name, noun: kd.noun, provision: kd.provision }, storeUrl: kd.provision.storefront ? "/index.html?store=" + slug : null, adminUrl: "/console.html?scope=store&store=" + slug, archetype: arch, identity: appliedIdentity, composition: caps.compositionOf(tid), activated: activated });
}
function apiPlatformTenantUpdate(req, res, url, s, body, id) {
  if (!requirePlatformSection(s, res, "tenants", "write")) return;
  const t = get("SELECT * FROM tenants WHERE id=?", Number(id));
  if (!t) return bad(res, "Unknown tenant", 404);
  const tid = t.id;
  if (body.name != null) run("UPDATE tenants SET name=? WHERE id=?", String(body.name).slice(0, 60), tid);
  if (body.domain != null) run("UPDATE tenants SET domain=? WHERE id=?", String(body.domain), tid);
  if (body.status != null) {
    const st = states.has("tenant", body.status) ? body.status : t.status;
    run("UPDATE tenants SET status=? WHERE id=?", st, tid);
    audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.status", "tenant", tid, { status: st });
  }
  const p = tenantPayload({ ...body, jurisdiction: body.jurisdiction || undefined });
  if (body.jurisdiction || body.tax != null || body.country) {
    if (!p.country) return bad(res, "Unknown jurisdiction country");
    applyCountryAndTax(tid, p.country, body.tax != null ? body.tax : null);
    if (body.jurisdiction) {
      const prof = J(t.profile, {});
      Object.assign(prof, { legalName: String(body.jurisdiction.legalName || prof.legalName || ""), taxId: String(body.jurisdiction.taxId != null ? body.jurisdiction.taxId : prof.taxId || ""), registrationAddress: String(body.jurisdiction.registrationAddress != null ? body.jurisdiction.registrationAddress : prof.registrationAddress || ""), state: String(body.jurisdiction.state != null ? body.jurisdiction.state : prof.state || "") });
      run("UPDATE tenants SET profile=? WHERE id=?", JSON.stringify(prof), tid);
    }
    audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.jurisdiction", "tenant", tid, { country: p.country.code, tax: body.tax || null });
  }
  if (Array.isArray(body.industries)) {
    const inds = body.industries.filter(k => registry.list("industries").some(i => i.key === k));
    run("UPDATE tenants SET industries=? WHERE id=?", JSON.stringify(inds), tid);
    inds.forEach((k, i) => { const ind = registry.list("industries").find(x => x.key === k); run("INSERT OR IGNORE INTO departments(tenant_id,key,label,icon,position) VALUES(?,?,?,?,?)", tid, k, ind.name, ind.icon, i); });
    seedTaxonomy(tid, inds);
    audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.industries", "tenant", tid, { industries: inds });
  }
  /* gateways and carriers are independent: an operator may re-pick carriers without
     touching payment providers (the wizard's shipping step does exactly that). */
  if (body.gateways || Array.isArray(body.shippingCarriers)) {
    const country = registry.country(require("./stores.js").country(tid)) || p.country;
    if (country) {
      const pays = provisionGateways(tid, country, body.gateways, { shipping: Array.isArray(body.shippingCarriers) ? body.shippingCarriers : null });
      audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.gateways", "tenant", tid, { gateways: pays });
    }
  }
  if (body.shipping) {
    const cc = settings.load(tid).commerce;
    settings.save(tid, { commerce: { ...cc, freeShipThreshold: Number(body.shipping.freeShipThreshold) || 0, shipFee: Number(body.shipping.shipFee) || 0, daysPriority: Number(body.shipping.daysPriority) || Number(sec.policy().provisioning.shipDaysPriority) || 2, daysStandard: Number(body.shipping.daysStandard) || Number(sec.policy().provisioning.shipDaysStandard) || 5 } });
    audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.shipping", "tenant", tid, { shipping: body.shipping });
  }
  const col = body.brand && body.brand.colors ? body.brand.colors : null;
  if (col) {
    themes.unassign("tenant", tid);
    const ct = settings.load(tid).theme;
    settings.save(tid, { theme: { ...ct, header: col.primary || ct.header, accent: col.accent || col.secondary || ct.accent } });
  }
  if (body.theme) { themes.assign("tenant", tid, String(body.theme)); audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.theme", "tenant", tid, { theme: body.theme }); }
  if (body.features) {
    const pol = sec.policy().provisioning;
    const feats = {};
    for (const [k, v] of Object.entries(body.features)) {
      if (v && require("./capabilities.js").policyRefusal(k, pol)) continue;
      feats[k] = !!v;
    }
    const leftover = caps.applyFeatures(tid, feats);
    if (Object.keys(leftover).length) settings.save(tid, { features: leftover });
    audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.features", "tenant", tid, { features: feats });
  }
  if (p.planId) {
    if (!get("SELECT id FROM plans WHERE id=?", p.planId)) return bad(res, "Unknown plan");
    const ex = get("SELECT id FROM subscriptions WHERE tenant_id=? ORDER BY id DESC LIMIT 1", tid);
    if (ex) run("UPDATE subscriptions SET plan_id=?, status=? WHERE id=?", p.planId, states.first("plan_subscription", "paying"), ex.id);
    else run("INSERT INTO subscriptions(tenant_id,plan_id,status) VALUES(?,?,?)", tid, p.planId, states.first("plan_subscription", "paying"));
    audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.plan", "tenant", tid, { plan_id: p.planId });
  }
  if (body.owner && body.owner.email) {
    const prof = J(get("SELECT profile FROM tenants WHERE id=?", tid).profile, {});
    const existing = get("SELECT id FROM users WHERE tenant_id=? AND role='admin' ORDER BY id LIMIT 1", tid);
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(body.owner.email)) return bad(res, "New owner needs a valid email");
    const weak = sec.checkPassword(String(body.owner.password || ""), body.owner.email);
    if (weak) return bad(res, "New owner password: " + weak);
    if (existing) {
      setUserPassword(existing.id, String(body.owner.password), body.owner.email.toLowerCase());
      run("UPDATE users SET email=?, name=? WHERE id=?", body.owner.email.toLowerCase(), String(body.owner.name || prof.ownerName || "Store Admin"), existing.id);
    } else newUser(tid, String(body.owner.name || "Store Admin"), body.owner.email, String(body.owner.password), "admin");
    prof.ownerEmail = body.owner.email.toLowerCase(); prof.ownerName = String(body.owner.name || prof.ownerName || ""); prof.ownerPhone = String(body.owner.phone || prof.ownerPhone || "");
    run("UPDATE tenants SET profile=? WHERE id=?", JSON.stringify(prof), tid);
    audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.owner", "tenant", tid, { email: prof.ownerEmail });
  }
  const out = get("SELECT * FROM tenants WHERE id=?", tid);
  json(res, 200, { tenant: { ...out, ...storeFacts(out.id), profile: J(out.profile, {}) } });
}
function apiPlatformTenantDelete(req, res, url, s, body, id) {
  if (!requirePlatformSection(s, res, "tenants", "write")) return;
  const tid = Number(id);
  const row = get("SELECT id, slug FROM tenants WHERE id=?", tid);
  if (!row) return bad(res, 'store not found', 404);
  /* Store protection is DATA, never a slug in code: an operator lists the protected stores
     in platform_settings.protectedStores and edits it at will. When that row is absent the
     platform's FIRST store is protected by structure (it is the console's own demo tenant),
     never by name — no code path depends on any particular store. */
  const list = platSetting('protectedStores', null);
  const firstId = Number((get("SELECT id FROM tenants ORDER BY id LIMIT 1") || {}).id);
  if ((list ? list.includes(row.slug) : tid === firstId))
    return bad(res, 'This store is protected from deletion. Remove its slug from platform_settings.protectedStores to proceed.');
  /* the store's node is archived on the kernel in the same transaction as its rows (lib/stores.js) */
  require("./stores.js").withdraw(tid, () => {
    for (const q of ["DELETE FROM products WHERE tenant_id=?", "DELETE FROM product_bullets WHERE tenant_id=?", "DELETE FROM departments WHERE tenant_id=?", "DELETE FROM home_banners WHERE tenant_id=?", "DELETE FROM home_cards WHERE tenant_id=?", "DELETE FROM settings WHERE tenant_id=?", "DELETE FROM tenant_gateways WHERE tenant_id=?", "DELETE FROM reviews WHERE tenant_id=?", "DELETE FROM payments WHERE tenant_id=?", "DELETE FROM invoices WHERE tenant_id=?", "DELETE FROM subscriptions WHERE tenant_id=?", "DELETE FROM users WHERE tenant_id=?", "DELETE FROM tenants WHERE id=?"]) run(q, tid);
  });
  audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.delete", "tenant", tid);
  json(res, 200, { ok: true });
}
function apiPlatformImpersonate(req, res, url, s, body, id) {
  if (!requirePlatformSection(s, res, "tenants", "write")) return;
  const tid = Number(id);
  if (!get("SELECT id FROM tenants WHERE id=?", tid)) return bad(res, "Unknown store", 404);
  let admin = get("SELECT id FROM users WHERE tenant_id=? AND role='admin' ORDER BY id LIMIT 1", tid);
  if (!admin) { const uid = newUser(tid, "Platform Impersonator", "impersonate+" + tid + "@luxora.shop", crypto.randomBytes(8).toString("hex"), "admin"); admin = { id: uid }; }
  const token = crypto.randomBytes(16).toString("hex");
  run("INSERT INTO tokens(token,tenant_id,user_id,expires_at) VALUES(?,?,?,datetime('now','+10 minutes'))", token, tid, admin.id);
  const t = get("SELECT slug FROM tenants WHERE id=?", tid);
  audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.impersonate", "tenant", tid);
  json(res, 200, { url: `/console.html?store=${t.slug}&scope=store&token=${token}` });
}
function apiPlatformPlans(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  json(res, 200, { plans: all("SELECT * FROM plans ORDER BY position") });
}
function apiPlatformPlanSave(req, res, url, s, body, id) {
  if (!requirePlatformSection(s, res, "plans", "write")) return;
  if (!body.name) return bad(res, "Name required");
  const vals = [String(body.name), Number(body.price_month) || 0, String(body.currency || require("./defaults.js").platformCurrency()), Math.max(1, Number(body.max_products) || 100), Math.max(1, Number(body.max_orders_month) || 100), Number(body.position) || 0];
  if (id) run("UPDATE plans SET name=?,price_month=?,currency=?,max_products=?,max_orders_month=?,position=? WHERE id=?", ...vals, Number(id));
  else run("INSERT INTO plans(name,price_month,currency,max_products,max_orders_month,position) VALUES(?,?,?,?,?,?)", ...vals);
  audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "plan.save", "plan", id || "new");
  json(res, 200, { plans: all("SELECT * FROM plans ORDER BY position") });
}
function apiPlatformSubscribe(req, res, url, s, body, id) {
  if (!requirePlatformSection(s, res, "subs", "write")) return;
  if (!get("SELECT id FROM tenants WHERE id=?", Number(id))) return bad(res, "Unknown store", 404);
  const plan = get("SELECT * FROM plans WHERE id=?", Number(body.plan_id));
  if (!plan) return bad(res, "Unknown plan", 404);
  const ex = get("SELECT id FROM subscriptions WHERE tenant_id=? ORDER BY id DESC LIMIT 1", Number(id));
  if (ex) run("UPDATE subscriptions SET plan_id=?, status=?, renews_at=datetime('now','+1 month') WHERE id=?", plan.id, states.first("plan_subscription", "paying"), ex.id);
  else run("INSERT INTO subscriptions(tenant_id,plan_id,status) VALUES(?,?,?)", Number(id), plan.id, states.first("plan_subscription", "paying"));
  audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "subscription.assign", "tenant", id, { plan: plan.name });
  json(res, 200, { ok: true });
}
function apiPlatformInvoices(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  json(res, 200, { invoices: all("SELECT i.*, t.slug tenant_slug, t.name tenant_name FROM invoices i JOIN tenants t ON t.id=i.tenant_id ORDER BY i.issued_at DESC") });
}
function apiPlatformInvoiceGenerate(req, res, url, s, body, id) {
  return (async () => {
  if (!requirePlatformSection(s, res, "invoices", "write")) return;
  const t = get("SELECT * FROM tenants WHERE id=?", Number(id));
  if (!t) return bad(res, "Unknown store", 404);
  const sub = get("SELECT p.* FROM subscriptions s JOIN plans p ON p.id=s.plan_id WHERE s.tenant_id=? ORDER BY s.id DESC", t.id);
  if (!sub) return bad(res, "Tenant has no subscription", 400);
  let r; try { r = billing.issueInvoice(t.id, { tax: true, note: `${sub.name} plan — monthly` }); } catch (e) { console.error("billing:", e.message); return bad(res, "Billing engine error: " + e.message, 500); }
  audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "invoice.generate", "invoice", r.number, { tenant: t.slug, amount: r.amount });
  json(res, 200, { ok: true, invoice: r });
  })();
}
function apiPlatformInvoiceRefund(req, res, url, s, body, id) {
  if (!requirePlatform(s, res)) return;
  const inv = get("SELECT * FROM invoices WHERE id=?", Number(id)); if (!inv) return bad(res, "Unknown invoice", 404);
  /* a credit note is bounded by what is left to credit on the invoice; money only goes to a
     wallet when the invoice was actually paid, and only to a wallet of the invoiced store */
  const credited = get("SELECT COALESCE(SUM(amount),0) c FROM credit_notes WHERE invoice_id=? AND status IN " + stIn("credit_note", "live").sql, inv.id, ...stIn("credit_note", "live").args).c;
  const amount = body.amount != null ? +Number(body.amount).toFixed(2) : +(inv.amount - credited).toFixed(2);
  if (!(amount > 0) || amount > +(inv.amount - credited).toFixed(2) + 1e-9) return bad(res, "Credit must be positive and at most the uncredited balance (" + (+(inv.amount - credited).toFixed(2)) + ")", 400);
  if (body.to_wallet && !stIs("invoice", inv.status, "success")) return bad(res, "Only a paid invoice can be refunded to a wallet", 400);
  const owner = body.owner ? String(body.owner) : undefined;
  if (owner && !owner.startsWith("t" + inv.tenant_id + ":")) return bad(res, "The refund wallet must belong to the invoiced store", 400);
  const r = billing.creditNote(inv.tenant_id, inv.id, amount, String(body.reason || "refund"), { to_wallet: !!body.to_wallet, owner });
  if (r.error) return bad(res, r.error);
  logAction(s, "invoice.credit_note", "invoice", inv.number, { amount: r.amount, to_wallet: !!body.to_wallet }, req);
  json(res, 200, { ok: true, credit_note: r });
}
function apiPlatformDunning(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return; const t = Number(body && body.tenant_id || 0);
  const r = billing.dunning(t); logAction(s, "billing.dunning", "billing", t || null, { actions: r.actions.length });
  json(res, 200, r);
}
function apiPlatformAging(req, res, url, s) { if (!requirePlatform(s, res)) return; json(res, 200, { aging: billing.aging(0), all: billing.list(0) }); }
function apiPlatformUsage(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  if (!body.tenant_id || !body.description) return bad(res, "tenant_id and description required");
  const id = billing.recordUsage(Number(body.tenant_id), String(body.kind || "manual"), String(body.description), Number(body.qty) || 1, Number(body.unit_amount) || 0, { currency: body.currency, ref: body.ref, period: body.period });
  logAction(s, "billing.usage", "usage_record", id, { tenant: body.tenant_id, amount: body.unit_amount });
  json(res, 200, { ok: true, id });
}
function apiAdminBillingDetail(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const data = billing.list(T(s)); data.aging = billing.aging(T(s)).buckets; data.usage = all("SELECT * FROM usage_records WHERE tenant_id=? ORDER BY id DESC LIMIT 100", T(s));
  json(res, 200, data);
}
function apiAdminTaxConfig(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const cfg = taxmod.configFor(T(s));
  const q = (url.searchParams.get("country") && url.searchParams.get("number")) ? taxmod.validateNumber(url.searchParams.get("country"), url.searchParams.get("number")) : null;
  json(res, 200, { country: cfg.country, rule: cfg.rule, classes: cfg.classes, storeRate: (CFG(s).commerce || {}).taxRate, taxNumber: q });
}
function apiAdminTaxQuote(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, taxmod.quote({ tenantId: T(s), country: body.country, lines: (body.lines || []).map(l => ({ id: l.id, class: l.class, amount: Number(l.amount) || 0, tax_rule: l.tax_rule || {} })), buyerVat: body.vatId, inclusive: !!body.inclusive })); } catch (e) { return bad(res, e.message); }
}
/* ---------- marketing / external integrations (specs are DATA: fill in the blanks) ---------- */
function marketingSpec(tenantId, id) {
  const rows = all("SELECT manifest FROM custom_providers WHERE kind='marketing' AND (scope='platform' OR (scope='tenant' AND tenant_id=?))", tenantId);
  for (const r of rows) { let m; try { m = J(r.manifest, null); } catch (e) { continue; } if (m && m.id === id && m.spec) return { spec: m.spec, fields: m.fields || [] }; }
  const def = get("SELECT spec, fields FROM provider_defs WHERE id=? AND kind='marketing'", id);
  if (def) return { spec: J(def.spec, null) || null, fields: J(def.fields, []) };
  return null;
}
function apiMarketingProviders(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const defs = registry.providerDefs("marketing").concat(customProviders(T(s), "marketing"));
  const list = defs.map(p => { const row = get("SELECT mode,config FROM tenant_gateways WHERE tenant_id=? AND provider_id=?", T(s), "marketing:" + p.id); let cfg = {}; try { cfg = J(row && row.config || "{}", {}); } catch (e) { } cfg = row ? sec.unsealConfig(T(s), "marketing:" + p.id, JSON.stringify(cfg)) : {}; const masked = {}; for (const [k, v] of Object.entries(cfg)) masked[k] = (p.fields || []).some(f => f.key === k && f.secret) ? (v ? "••••" + String(v).slice(-4) : "") : v; const sp = marketingSpec(T(s), p.id); return { id: p.id, name: p.name, emoji: p.emoji, desc: p.desc, fields: p.fields, mode: row ? row.mode : "sandbox", configured: row && Object.keys(cfg).length > 0, hasSpec: !!(sp && sp.spec), spec: sp && sp.spec, config: masked }; });
  json(res, 200, { providers: list });
}
function apiMarketingSend(req, res, url, s, body) {
  return (async () => {
    if (!requireAdmin(s, res)) return;
    const id = String(body.provider || ""); const sp = marketingSpec(T(s), id); if (!sp || !sp.spec) return bad(res, "Unknown or specless marketing provider: " + id, 404);
    { const d = rules.decideAt("marketing.send", id, rules.at("marketing.send", T(s))); if (!d.ok) return bad(res, "Marketing integration " + id + " is not available here — " + d.reasons.join("; "), 403); }
    const row = get("SELECT mode,config FROM tenant_gateways WHERE tenant_id=? AND provider_id=?", T(s), "marketing:" + id);
    let cfg = {}; try { cfg = J(row && row.config || "{}", {}); } catch (e) { } if (row) cfg = sec.unsealConfig(T(s), "marketing:" + id, JSON.stringify(cfg));
    if (!body.config && (!row || row.mode !== "live")) return json(res, 200, { ok: true, live: false, simulated: true, note: "provider not configured live — enable in Marketing & set live + credentials" });
    const r = await connect.marketing({ provider: id, spec: sp.spec, config: body.config || cfg, payload: body.payload || {}, currency: body.currency });
    logAction(s, "marketing.send", "marketing", id, { ok: !!r.ok, live: !!r.live, error: r.error }, req);
    json(res, 200, r);
  })();
}
function apiMarketingSave(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const list = Array.isArray(body.marketing) ? body.marketing : [];
  list.forEach((g, i) => { const cfg = {}; for (const [k, v] of Object.entries(g.config || {})) if (v && !String(v).startsWith("••••")) cfg[k] = sec.encryptSecret(String(v), T(s) + "|marketing:" + g.id + "|" + k); run(`INSERT INTO tenant_gateways(tenant_id,provider_id,enabled,is_primary,mode,config,position) VALUES(?,?,1,0,?,?,?)
     ON CONFLICT(tenant_id,provider_id) DO UPDATE SET enabled=1, mode=excluded.mode, config=excluded.config`, T(s), "marketing:" + g.id, g.mode === "live" ? "live" : "sandbox", JSON.stringify(cfg), i); });
  logAction(s, "marketing.save", "marketing", null, { count: list.length }, req); json(res, 200, { ok: true });
}
function apiPlatformInvoicePay(req, res, url, s, body, id) {
  return (async () => {
  if (!requirePlatform(s, res)) return;
  const inv = get("SELECT * FROM invoices WHERE id=?", Number(id));
  if (!inv) return bad(res, "Unknown invoice", 404);
  if (stIs("invoice", inv.status, "success")) return bad(res, "Already paid");
  const gwId = String(body.gateway || "");
  if (!gwId) return bad(res, "Pick the gateway the invoice is collected through", 422);
  const gw = registry.providerDefs("payment").find(p => p.id === gwId);
  if (!gw) return bad(res, "Unknown gateway", 422);
  const gs = gatewaySecrets(inv.tenant_id, gwId);
  const sim = await settlePayment(inv.tenant_id, Object.assign({}, gw, { mode: gs ? gs.mode : "sandbox" }), inv.amount, inv.currency, inv.number);
  if (stIs("payment", sim.status, "failure")) return bad(res, "Payment declined: " + (sim.error || "gateway error"), 402);
  invoicePaid(inv);
  run("INSERT INTO payments(tenant_id,kind,invoice_id,gateway,method,amount,currency,fee,status,txn_ref) VALUES(?,?,?,?,?,?,?,?,?,?)",
    inv.tenant_id, "subscription", inv.id, gw.id, "card", inv.amount, inv.currency, sim.fee, sim.status, sim.ref);
  audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "invoice.pay", "invoice", inv.number, { gateway: gw.id, txn: sim.ref, live: !!sim.live });
  json(res, 200, { ok: true, txn_ref: sim.ref });
  })();
}
function apiPlatformMonitor(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  /* the same singleton the store console's Monitor reads (lib/metrics.js) — read
     directly rather than through a positional argument, so the route's handler
     cannot be broken by the dispatcher's param ordering (see apiAdminMonitor) */
  const snap = require("./metrics.js").snapshot(null);
  const mem = process.memoryUsage();
  /* L4: under Postgres DB_PATH still points at the stale SQLite file, so "DB size" reported the
     wrong database. Ask the live server instead. */
  let dbSize = 0;
  if (USE_PG) {
    try { const r = get("SELECT pg_database_size(current_database()) s"); dbSize = (r && Number(r.s)) || 0; } catch (e) { dbSize = 0; }
  } else try { dbSize = fs.statSync(DB_PATH).size; } catch (e) { }
  snap.system = { uptimeSec: Math.floor(process.uptime()), rssMB: +(mem.rss / 1048576).toFixed(1), dbKB: +(dbSize / 1024).toFixed(0), node: process.version, driver: USE_PG ? "postgres" : "sqlite" };
  snap.tenants = all("SELECT id, slug, name, status FROM tenants ORDER BY id");
  json(res, 200, snap);
}
function apiPlatformAudit(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const t = url.searchParams.get("tenant");
  const rows = t ? all("SELECT * FROM audit_log WHERE tenant_id=? ORDER BY created_at DESC LIMIT 300", Number(t)) : all("SELECT * FROM audit_log ORDER BY created_at DESC LIMIT 300");
  json(res, 200, { entries: rows });
}
function apiPlatformRevenue(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  json(res, 200, {
    mrr: get("SELECT COALESCE(SUM(p.price_month),0) t FROM subscriptions s JOIN plans p ON p.id=s.plan_id WHERE s.status IN " + stIn("plan_subscription", "current").sql, ...stIn("plan_subscription", "current").args).t, /* plans priced in platform billing currency (USD) */
    collected: get("SELECT COALESCE(SUM(i.amount * COALESCE(c.usd,1)),0) t FROM invoices i LEFT JOIN currencies c ON c.code=i.currency WHERE i.status IN " + stIn("invoice", "success").sql, ...stIn("invoice", "success").args).t,
    outstanding: get("SELECT COALESCE(SUM(amount),0) t FROM invoices WHERE status NOT IN " + stIn("invoice", "success").sql, ...stIn("invoice", "success").args).t,
    gatewayFees: get("SELECT COALESCE(SUM(p.fee * COALESCE(c.usd,1)),0) t FROM payments p LEFT JOIN currencies c ON c.code=p.currency WHERE p.kind='order'").t,
    gmv: get("SELECT COALESCE(SUM(o.total * COALESCE(c.usd,1)),0) t FROM orders o LEFT JOIN currencies c ON c.code=o.currency").t,
    byMonth: all("SELECT strftime('%Y-%m', issued_at) m, SUM(CASE WHEN status IN " + stIn("invoice", "success").sql + " THEN amount ELSE 0 END) paid FROM invoices GROUP BY m ORDER BY m", ...stIn("invoice", "success").args)
  });
}
function apiPlatformCustomProviders(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  json(res, 200, {
    builtIn: { payment: registry.providerDefs("payment"), shipping: registry.providerDefs("shipping"), notification: registry.providerDefs("notification"), tax: registry.taxModes(), ai: registry.providerDefs("ai") },
    countries: registry.countries(), availability: all("SELECT * FROM provider_availability ORDER BY provider_id"),
    custom: all("SELECT * FROM custom_providers WHERE scope='platform'")
  });
}
function apiPlatformCustomProviderAdd(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  const m = body.manifest;
  if (!m || !m.id || !m.name) return bad(res, "Manifest needs id and name");
  const kind = rl("providerKinds").includes(body.kind) ? body.kind : "payment";
  run("INSERT INTO custom_providers(scope,kind,manifest) VALUES('platform',?,?)", kind, JSON.stringify(m));
  try {
    run(`INSERT INTO provider_defs(id,kind,name,emoji,description,methods,fee_pct,fee_fixed,fields,base_fee,position) VALUES(?,?,?,?,?,?,?,?,?,?,?)
         ON CONFLICT(id,kind) DO UPDATE SET name=excluded.name,emoji=excluded.emoji,description=excluded.description,methods=excluded.methods,fee_pct=excluded.fee_pct,fee_fixed=excluded.fee_fixed,fields=excluded.fields`,
      String(m.id), kind, String(m.name), String(m.emoji || "🔌"), String(m.desc || ""), JSON.stringify(m.methods || []), Number(m.feePct) || 0, Number(m.feeFixed) || 0, JSON.stringify(m.fields || []), Number(m.baseFee) || 0, 900);
    const codes = (m.countries || []).includes("*") ? all("SELECT code FROM countries").map(c => c.code) : (m.countries || []);
    for (const cc of codes) run("INSERT OR IGNORE INTO provider_availability(provider_id,country_code) VALUES(?,?)", String(m.id), cc);
    /* a manifest that names every country ("*") is a worldwide provider, so provisioning
       ranks a country's own providers ahead of it */
    if ((m.countries || []).includes("*")) run("UPDATE provider_defs SET global=1 WHERE id=? AND kind=?", String(m.id), kind);
  } catch (e) { console.error("provider_defs sync:", e.message); }
  audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "provider.add", "custom_provider", m.id, { kind });
  json(res, 200, { ok: true });
}
function apiPlatformCustomProviderDelete(req, res, url, s, body, id) {
  if (!requirePlatform(s, res)) return;
  run("DELETE FROM custom_providers WHERE id=? AND scope='platform'", Number(id));
  json(res, 200, { ok: true });
}

/* ================= META MODEL ================= */
const meta = require("./meta.js");
const rules = require("./rules.js");
/* orders, payments, invoices and returns are state machines (lib/states.js): this file asks
   what a state means (settled, awaiting, cancellable, shippable…) and never names one */
const states = require("./states.js");
const stIn = (machine, tag) => { const xs = states.tagged(machine, tag); return { sql: "(" + (xs.length ? xs.map(() => "?").join(",") : "NULL") + ")", args: xs }; };
const stIs = (machine, state, tag) => states.has(machine, state) && states.is(machine, state, tag);
/* an invoice moves to the state that means "paid", with the stamp that state declares */
function invoicePaid(inv) {
  const { patch } = states.apply("invoice", { tenantId: inv.tenant_id, from: inv.status, to: states.first("invoice", "success"), row: inv, force: true });
  run("UPDATE invoices SET " + Object.keys(patch).map(k => k + "=?").join(", ") + " WHERE id=?", ...Object.values(patch), inv.id);
}
/* a refunded return reverses the offer redemptions on its order */
states.handle("return", "claw_back_offers", ctx => {
  const r = ctx.row; if (!r.order_id) return;
  const ord = get("SELECT num FROM orders WHERE id=?", r.order_id);
  try { offers.reverseRedemption(ctx.tenantId, { order_id: r.order_id, order_num: ord && ord.num }); } catch (e) { console.error("clawback:", e.message); }
});
const rl = registry.list;
/* the universal theme registry — themes are data (lib/themes.js); required here so the
   config payload can carry the resolved cascade and    the theme API can serve it */
const themes = require("./themes.js");
function J(v, d) { try { return JSON.parse(v == null || v === "" ? (d || "{}") : v); } catch (e) { return d || {}; } }
function apiMeta(req, res, url, s) {
  const c = CFG(s);
  const tInds = J(s.tenant.industries, []);
  const allowed = tInds.length ? tInds : null;
  const reg = meta.registry(customProviders(T(s), "registry").reduce((o, m) => ({ ...o, ...m }), {}));
  json(res, 200, {
    /* every state machine's states (what each means, how it shows) and labelled moves, so a
       console asks by meaning instead of naming statuses */
    stateMachines: states.catalog(),
    /* the default row of each declared list and the platform currency (lib/defaults.js) */
    defaults: require("./defaults.js").all(),
    industries: allowed ? reg.industries.filter(i => allowed.includes(i.key)) : reg.industries,
    productTypes: reg.productTypes, lifecycle: rl("lifecycle"), lifecycleTransitions: rl("lifecycleTransitions"),
    relTypes: rl("relTypes"), mediaKinds: rl("mediaKinds"), packagingLevels: rl("packagingLevels"),
    uomUnits: rl("uomUnits"), uomConversions: rl("uomConversions"), sellerRoles: rl("sellerRoles"),
    promoTypes: rl("promoTypes"), identityFields: rl("identityFields"), shippingClasses: rl("shippingClasses"), contextGroups: rl("contextGroups"),
    serializedStatuses: rl("serializedStatuses"), serializedConditions: rl("serializedConditions"), variantAxes: rl("variantAxes"),
    complianceScopes: rl("complianceScopes"), complianceKinds: rl("complianceKinds"), complianceStatuses: rl("complianceStatuses"),
    supplierRoles: rl("supplierRoles"), supplierStatuses: rl("supplierStatuses"), paymentTerms: rl("paymentTerms"), incoterms: rl("incoterms"),
    localizationEntities: rl("localizationEntities"), contractStatuses: rl("contractStatuses"), tenderStatuses: rl("tenderStatuses"), linkStatuses: rl("linkStatuses"),
    providerKinds: rl("providerKinds"), aiCapabilityKeys: rl("aiCapabilityKeys"), aiCapabilities: rl("aiCapabilities"), aiPlans: rl("aiPlans"),
    offerTypes: rl("offerTypes"), offerScopes: rl("offerScopes"), offerChannels: rl("offerChannels"), offerDirections: rl("offerDirections"), offerFunders: rl("offerFunders"), couponKinds: rl("couponKinds"), stackingPolicies: rl("stackingPolicies"), offerStatuses: rl("offerStatuses"), couponStatuses: rl("couponStatuses"), walletEntryKinds: rl("walletEntryKinds"),
    verticals: reg.verticals, verticalFields: rl("verticalFields"), verticalTypes: rl("verticalTypes"), verticalContexts: rl("verticalContexts"), verticalTypeOf: rl("verticalTypeOf"),
    countries: registry.countries(), taxModes: registry.taxModes(),
    providers: { payment: registry.providerDefs("payment"), shipping: registry.providerDefs("shipping"), notification: registry.providerDefs("notification") },
    providersAi: registry.providerDefs("ai"),
    deployModes: registry.kinds(),
    tenant: { id: s.tenant.id, slug: s.tenant.slug, name: s.tenant.name, mode: s.tenant.mode, industries: J(s.tenant.industries, []) }
  });
}
/* the taxonomy levels (registry taxonomyLevels): the root a storefront browses from, and the
   levels a global product may be categorised by */
function taxLevels() { const l = rl("taxonomyLevels"); return l.length ? l : meta.TAXONOMY_LEVELS; }
function taxRoot() { const l = taxLevels(); return (l.find(x => x.root) || l[0] || {}).key; }
function apiTaxonomy(req, res, url, s) {
  const rows = all("SELECT * FROM taxonomy WHERE tenant_id=? AND active=1 ORDER BY position", T(s));
  const byParent = {};
  rows.forEach(r => { (byParent[r.parent_id || 0] = byParent[r.parent_id || 0] || []).push(r); });
  function build(pid) { return (byParent[pid] || []).map(r => ({ ...r, attrs: J(r.attrs), children: build(r.id) })); }
  json(res, 200, { tree: build(0), flat: rows, levels: taxLevels() });
}
function nodeDescendants(tenantId, id) {
  const out = [Number(id)];
  const rows = all("SELECT id,parent_id FROM taxonomy WHERE tenant_id=?", tenantId);
  let grew = true;
  while (grew) { grew = false; for (const r of rows) if (out.includes(r.parent_id) && !out.includes(r.id)) { out.push(r.id); grew = true; } }
  return out;
}
function apiAdminTaxonomy(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { nodes: all("SELECT * FROM taxonomy WHERE tenant_id=? ORDER BY level, position", T(s)) });
}
function apiAdminTaxSave(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  const level = taxLevels().some(l => l.key === body.level) ? body.level : require("./defaults.js").of("taxonomyLevels");
  if (!body.name) return bad(res, "Name required");
  const key = String(body.key || (level + "-" + Date.now().toString(36)));
  if (id) run("UPDATE taxonomy SET parent_id=?,level=?,key=?,name=?,icon=?,active=?,position=? WHERE id=? AND tenant_id=?",
    body.parent_id || null, level, key, String(body.name), String(body.icon || ""), body.active === 0 ? 0 : 1, Number(body.position) || 0, Number(id), t);
  else run("INSERT INTO taxonomy(tenant_id,parent_id,level,key,name,icon,position) VALUES(?,?,?,?,?,?,?)",
    t, body.parent_id || null, level, key, String(body.name), String(body.icon || ""), Number(body.position) || 0);
  logAction(s, "taxonomy.save", "taxonomy", id || key, { level });
  json(res, 200, { ok: true });
}
function apiAdminTaxDelete(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  if (get("SELECT COUNT(*) c FROM taxonomy WHERE tenant_id=? AND parent_id=?", T(s), Number(id)).c > 0) return bad(res, "Remove children first");
  run("UPDATE products SET node_id=NULL WHERE tenant_id=? AND node_id=?", T(s), Number(id));
  run("DELETE FROM taxonomy WHERE id=? AND tenant_id=?", Number(id), T(s));
  logAction(s, "taxonomy.delete", "taxonomy", id);
  json(res, 200, { ok: true });
}
function apiAdminAttributes(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { attributes: all("SELECT * FROM attribute_defs WHERE tenant_id=? ORDER BY position", T(s)).map(a => ({ ...a, options: J(a.options, []), validation: J(a.validation) })) });
}
function apiAdminAttrSave(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const key = String(body.key || "").trim().toLowerCase().replace(/[^a-z0-9_]/g, "");
  if (!key || !body.label) return bad(res, "Key and label required");
  const ex = get("SELECT key FROM attribute_defs WHERE tenant_id=? AND key=?", T(s), key);
  const vals = [String(body.label), String(body.grp || "General"), String(body.type || "text"), String(body.unit || ""), JSON.stringify(body.options || []), JSON.stringify(body.validation || {}), String(body.industry || ""), Number(body.position) || 0];
  if (ex) run("UPDATE attribute_defs SET label=?,grp=?,type=?,unit=?,options=?,validation=?,industry=?,position=? WHERE tenant_id=? AND key=?", ...vals, T(s), key);
  else run("INSERT INTO attribute_defs(tenant_id,key,label,grp,type,unit,options,validation,industry,position) VALUES(?,?,?,?,?,?,?,?,?,?)", T(s), key, ...vals);
  logAction(s, "attribute.save", "attribute", key);
  json(res, 200, { ok: true });
}
function apiAdminAttrDelete(req, res, url, s, body, key) {
  if (!requireAdmin(s, res)) return;
  run("DELETE FROM attribute_defs WHERE tenant_id=? AND key=?", T(s), key);
  logAction(s, "attribute.delete", "attribute", key);
  json(res, 200, { ok: true });
}
function validateAttrs(tenantId, attrs) {
  const defs = all("SELECT * FROM attribute_defs WHERE tenant_id=?", tenantId);
  const errs = [];
  for (const d of defs) {
    const v = attrs[d.key];
    if (v == null || v === "") continue;
    if (d.type === "number" && isNaN(Number(v))) errs.push(d.label + " must be a number");
    if (d.type === "select" && !J(d.options, []).includes(v)) errs.push(d.label + " invalid option");
  }
  return errs;
}
function fullProductDoc(tenantId, p) {
  const skus = all("SELECT * FROM skus WHERE tenant_id=? AND product_id=?", tenantId, p.id).map(k => ({ ...k, identity: J(k.identity), variant: J(k.variant) }));
  for (const k of skus) k.inventory = all("SELECT i.*, w.name warehouse FROM inventory i LEFT JOIN warehouses w ON w.id=i.warehouse_id WHERE i.tenant_id=? AND i.sku_id=?", tenantId, k.id).map(i => ({ ...i, serial: J(i.serial, []) }));
  const rels = all("SELECT * FROM relationships WHERE tenant_id=? AND from_id=?", tenantId, p.id).map(r => ({ ...r, to: get("SELECT id,title,price,emoji,hue,stock,type FROM products WHERE tenant_id=? AND id=?", tenantId, r.to_id) }));
  return {
    ...publicProduct(p), type: p.type, node_id: p.node_id, lifecycle: p.lifecycle,
    identity: J(p.identity), attrs: J(p.attrs), vertical: J(p.vertical), media: J(p.media, []), seo: J(p.seo),
    tax_rule: J(p.tax_rule), geo_rules: J(p.geo_rules, []), pricing_rules: J(p.pricing_rules), logistics: J(p.logistics),
    packaging: J(p.packaging, []), docs: J(p.docs, []), uom: J(p.uom), supplier_id: p.supplier_id,
    skus, relationships: rels
  };
}
function apiAdminProductGet(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const p = get("SELECT * FROM products WHERE tenant_id=? AND id=?", T(s), id);
  if (!p) return bad(res, "Unknown product", 404);
  p.about = all("SELECT text FROM product_bullets WHERE tenant_id=? AND product_id=? ORDER BY pos", T(s), id).map(r => r.text);
  json(res, 200, { product: fullProductDoc(T(s), p) });
}
function apiAdminProductSaveMeta(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  const p = get("SELECT * FROM products WHERE tenant_id=? AND id=?", t, id);
  if (!p) return bad(res, "Unknown product", 404);
  const errs = body.attrs ? validateAttrs(t, body.attrs) : [];
  if (errs.length) return bad(res, errs.join("; "));
  const set = {
    type: body.type != null && rl("productTypes").some(x => x.key === body.type) ? body.type : p.type,
    node_id: body.node_id != null ? Number(body.node_id) || null : p.node_id,
    identity: body.identity != null ? JSON.stringify(body.identity) : p.identity,
    attrs: body.attrs != null ? JSON.stringify(body.attrs) : p.attrs,
    vertical: body.vertical != null ? JSON.stringify(body.vertical) : p.vertical,
    media: body.media != null ? JSON.stringify(body.media) : p.media,
    seo: body.seo != null ? JSON.stringify(body.seo) : p.seo,
    tax_rule: body.tax_rule != null ? JSON.stringify(body.tax_rule) : p.tax_rule,
    geo_rules: body.geo_rules != null ? JSON.stringify(body.geo_rules) : p.geo_rules,
    pricing_rules: body.pricing_rules != null ? JSON.stringify(body.pricing_rules) : p.pricing_rules,
    logistics: body.logistics != null ? JSON.stringify(body.logistics) : p.logistics,
    packaging: body.packaging != null ? JSON.stringify(body.packaging) : p.packaging,
    docs: body.docs != null ? JSON.stringify(body.docs) : p.docs,
    uom: body.uom != null ? JSON.stringify(body.uom) : p.uom,
    supplier_id: body.supplier_id != null ? Number(body.supplier_id) || null : p.supplier_id
  };
  run(`UPDATE products SET type=?,node_id=?,identity=?,attrs=?,vertical=?,media=?,seo=?,tax_rule=?,geo_rules=?,pricing_rules=?,logistics=?,packaging=?,docs=?,uom=?,supplier_id=? WHERE tenant_id=? AND id=?`,
    set.type, set.node_id, set.identity, set.attrs, set.vertical, set.media, set.seo, set.tax_rule, set.geo_rules, set.pricing_rules, set.logistics, set.packaging, set.docs, set.uom, set.supplier_id, t, id);
  logAction(s, "product.meta", "product", id, { fields: Object.keys(body) });
  json(res, 200, { ok: true });
}
function apiAdminLifecycle(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const p = get("SELECT lifecycle FROM products WHERE tenant_id=? AND id=?", T(s), id);
  if (!p) return bad(res, "Unknown product", 404);
  const to = String(body.to || "");
  if (!rl("lifecycle").includes(to)) return bad(res, "Unknown state");
  if (!((rl("lifecycleTransitions")[p.lifecycle] || []).includes(to))) return bad(res, `Cannot move ${p.lifecycle} → ${to}`);
  run("UPDATE products SET lifecycle=? WHERE tenant_id=? AND id=?", to, T(s), id);
  logAction(s, "product.lifecycle", "product", id, { from: p.lifecycle, to });
  json(res, 200, { ok: true, lifecycle: to });
}
function apiAdminSkuSave(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  const pid = String(body.product_id);
  if (id) {
    run("UPDATE skus SET code=?,name=?,identity=?,variant=?,price=?,mrp=?,stock=?,active=? WHERE id=? AND tenant_id=?",
      String(body.code), String(body.name || ""), JSON.stringify(body.identity || {}), JSON.stringify(body.variant || {}),
      Number(body.price), body.mrp ? Number(body.mrp) : null, Number(body.stock) || 0, body.active === 0 ? 0 : 1, Number(id), t);
    if (body.inventory) for (const inv of body.inventory) run("INSERT INTO inventory(tenant_id,sku_id,warehouse_id,qty,reserved,lot,batch,expiry,serial) VALUES(?,?,?,?,?,?,?,?,?)",
      t, Number(id), inv.warehouse_id || null, Number(inv.qty) || 0, Number(inv.reserved) || 0, inv.lot || "", inv.batch || "", inv.expiry || "", JSON.stringify(inv.serial || []));
  } else {
    const r = run("INSERT INTO skus(tenant_id,product_id,code,name,identity,variant,price,mrp,stock) VALUES(?,?,?,?,?,?,?,?,?)",
      t, pid, String(body.code), String(body.name || ""), JSON.stringify(body.identity || {}), JSON.stringify(body.variant || {}), Number(body.price), body.mrp ? Number(body.mrp) : null, Number(body.stock) || 0);
    logAction(s, "sku.create", "sku", r.lastInsertRowid, { product: pid });
    json(res, 200, { id: Number(r.lastInsertRowid) });
    return;
  }
  logAction(s, "sku.update", "sku", id);
  json(res, 200, { ok: true });
}
function apiAdminSkuDelete(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  run("DELETE FROM skus WHERE id=? AND tenant_id=?", Number(id), T(s));
  run("DELETE FROM inventory WHERE sku_id=? AND tenant_id=?", Number(id), T(s));
  logAction(s, "sku.delete", "sku", id);
  json(res, 200, { ok: true });
}
function apiAdminInventoryPut(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  const inv = get("SELECT * FROM inventory WHERE id=? AND tenant_id=?", Number(id), t);
  if (!inv) return bad(res, "Unknown inventory row", 404);
  run("UPDATE inventory SET qty=?,reserved=?,lot=?,batch=?,expiry=?,serial=? WHERE id=?",
    Number(body.qty), Number(body.reserved) || 0, String(body.lot || ""), String(body.batch || ""), String(body.expiry || ""), JSON.stringify(body.serial || []), inv.id);
  const total = get("SELECT COALESCE(SUM(qty),0) q FROM inventory WHERE tenant_id=? AND sku_id=?", t, inv.sku_id).q;
  run("UPDATE skus SET stock=? WHERE id=?", total, inv.sku_id);
  logAction(s, "inventory.update", "inventory", id, { qty: body.qty });
  json(res, 200, { ok: true });
}
function apiAdminRelationshipAdd(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  if (!rl("relTypes").some(r => r.key === body.type)) return bad(res, "Unknown relationship type");
  if (!get("SELECT id FROM products WHERE tenant_id=? AND id=?", T(s), body.to_id)) return bad(res, "Target product unknown", 404);
  /* RELATIONSHIP OWNS RELATIONSHIP: the primitive is written first — the product projection the
     storefront reads is DERIVED from it (registry.reconcileLinks), exactly as a country's
     subdivisions are derived from the country master. Writing the projection first and mirroring
     here best-effort left the primitive optional, so an edge added from a product page existed
     only in that store's catalogue and in nothing else that relates two entities. Idempotent —
     re-adding the same edge is a no-op at the primitive, so the projection stays single too. */
  const fromUid = (get("SELECT uid FROM products WHERE tenant_id=? AND id=?", T(s), id) || {}).uid;
  const toUid = (get("SELECT uid FROM products WHERE tenant_id=? AND id=?", T(s), body.to_id) || {}).uid;
  if (!fromUid || !toUid) return bad(res, "Product universal IDs unresolved", 500);
  run("INSERT OR IGNORE INTO links(tenant_id,type,from_entity,from_uid,to_entity,to_uid,meta) VALUES(?,?,?,?,?,?,?)",
    T(s), String(body.type), "product", fromUid, "product", toUid, JSON.stringify({ via: "admin_relationship" }));
  try { require("./registry.js").reconcileLinks(); } catch (e) { console.error("link reconcile:", e.message); }
  logAction(s, "relationship.add", "relationship", id, { to: body.to_id, type: body.type });
  json(res, 200, { ok: true });
}
function apiAdminRelationshipDelete(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const row = get("SELECT * FROM relationships WHERE id=? AND tenant_id=?", Number(id), T(s));
  if (!row) return bad(res, "Unknown relationship", 404);
  /* deleting the projection row alone would leave the primitive edge behind and reconcile would
     silently restore the projection on the next pass — the removal would not stick. Removing the
     PRIMITIVE edge is what makes the delete authoritative, and reconcileLinks withdraws the
     projection with it, so the two never drift in either direction */
  const fromUid = (get("SELECT uid FROM products WHERE tenant_id=? AND id=?", T(s), row.from_id) || {}).uid;
  const toUid = (get("SELECT uid FROM products WHERE tenant_id=? AND id=?", T(s), row.to_id) || {}).uid;
  if (fromUid && toUid) run("DELETE FROM links WHERE type=? AND from_uid=? AND to_uid=?",
    row.type, fromUid, toUid);
  try { require("./registry.js").reconcileLinks(); } catch (e) { console.error("link reconcile:", e.message); }
  logAction(s, "relationship.delete", "relationship", id, { to: row.to_id, type: row.type });
  json(res, 200, { ok: true });
}
function apiAdminWarehouses(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { warehouses: all("SELECT * FROM warehouses WHERE tenant_id=?", T(s)) });
}
function apiAdminWarehouseSave(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  if (!body.name) return bad(res, "Name required");
  if (id) run("UPDATE warehouses SET name=?,code=?,country=?,region=?,active=? WHERE id=? AND tenant_id=?", String(body.name), String(body.code || ""), String(body.country || CFG(s).commerce.country), String(body.region || ""), body.active === 0 ? 0 : 1, Number(id), T(s));
  else run("INSERT INTO warehouses(tenant_id,name,code,country,region) VALUES(?,?,?,?,?)", T(s), String(body.name), String(body.code || ""), String(body.country || CFG(s).commerce.country), String(body.region || ""));
  logAction(s, "warehouse.save", "warehouse", id || "new");
  json(res, 200, { ok: true });
}

/* ---------------- promotions engine ---------------- */
function activePromos(tenantId, coupon) {
  coupon = String(coupon || "").trim().toUpperCase();
  const now = new Date().toISOString().slice(0, 10);
  return all("SELECT * FROM promotions WHERE tenant_id=? AND status IN " + stIn("promotion", "running").sql + " AND (starts IS NULL OR starts<=?) AND (ends IS NULL OR ends>=?)", tenantId, ...stIn("promotion", "running").args, now, now)
    .filter(p => !p.code || p.code.toUpperCase() === coupon)
    .map(p => ({ ...p, rules: J(p.rules), scope: J(p.scope) }));
}
function promoApplies(p, items, tenantId) {
  /* a promotion is subject to the applicability rules (country, segment, channel, amount…) */
  if (!rules.permitsAt("promotions.apply", String(p.id), rules.at("promotions.apply", tenantId, { amount: cartSubtotal(items) }))) return false;
  if (p.scope.node) {
    const ids = nodeDescendants(tenantId, get("SELECT id FROM taxonomy WHERE tenant_id=? AND key=?", tenantId, p.scope.node).id);
    if (!items.some(i => i.product.node_id && ids.includes(i.product.node_id))) return false;
  }
  if (p.scope.products && !items.some(i => p.scope.products.includes(i.product.id))) return false;
  if (p.rules.min && cartSubtotal(items) < p.rules.min) return false;
  return true;
}
function cartSubtotal(items) { return items.reduce((n, i) => n + i.product.p * i.qty, 0); }
function applyPromos(tenantId, items, coupon, opts) {
  opts = opts || {};
  const codesAllowed = sec.policy().provisioning.couponsAllowed;
  const amount = items.reduce((n, i) => n + i.product.p * i.qty, 0);
  const mapped = items.map(i => ({ id: i.product.id, dept: i.product.d, brand: i.product.b, node_id: i.product.node_id, price: i.product.p, qty: i.qty }));
  const res = offers.evaluate({ channel: require("./defaults.js").of("offerChannels"), tenantId, items: mapped, amount, coupon: codesAllowed ? coupon : "", owner: opts.owner || null, currency: opts.currency || null, allowGlobal: sec.policy().provisioning.globalOffersAllowed !== false });
  return { discount: res.discount, applied: res.applied, credits: res.credits, freeShip: res.freeShip, redemptions: res.redemptions };
}
function contractPriceFor(tenantId, buyerEmail, productId, qty) {
  if (!buyerEmail) return null;
  const today = new Date().toISOString().slice(0, 10);
  const cts = all("SELECT * FROM contracts WHERE tenant_id=? AND status IN " + stIn("contract", "in_force").sql + " AND lower(buyer_email)=?", tenantId, ...stIn("contract", "in_force").args, String(buyerEmail).toLowerCase());
  let best = null;
  for (const c of cts) {
    if (c.valid_from && c.valid_from > today) continue;
    if (c.valid_to && c.valid_to < today) continue;
    let pid = []; try { pid = JSON.parse(c.product_ids || "[]"); } catch (e) { }
    if (!pid.includes(productId) || qty < (c.min_qty || 1)) continue;
    let pr = {}; try { pr = JSON.parse(c.pricing || "{}"); } catch (e) { }
    let price = null;
    if (pr.fixed && pr.fixed[productId] != null) price = Number(pr.fixed[productId]);
    else if (Array.isArray(pr.tiers)) for (const t of pr.tiers) if ((t.product_id || t.product) === productId && qty >= (t.qty || 1)) price = Number(t.price);
    if (price != null && (best == null || price < best)) best = price;
  }
  return best;
}
function effectivePrice(p, qty) {
  const pr = J(p.pricing_rules);
  if (pr.tiers) { let price = p.price; for (const t of pr.tiers) if (qty >= t.qty) price = t.price; return price; }
  return p.price;
}
function apiPromos(req, res, url, s) {
  json(res, 200, { promotions: activePromos(T(s)).map(p => ({ id: p.id, name: p.name, type: p.type, value: p.value, code: p.code, scope: p.scope })) });
}
function apiAdminPromotions(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { promotions: all("SELECT * FROM promotions WHERE tenant_id=? ORDER BY id DESC", T(s)).map(p => ({ ...p, rules: J(p.rules), scope: J(p.scope) })) });
}
function apiAdminPromoSave(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  if (!body.name || !rl("promoTypes").some(t => t.key === body.type)) return bad(res, "Name and valid type required");
  const vals = [String(body.name), String(body.type), Number(body.value) || 0, JSON.stringify(body.rules || {}), JSON.stringify(body.scope || {}), body.starts || null, body.ends || null, body.status === "inactive" ? "inactive" : "active", String(body.code || "")];
  if (id) run("UPDATE promotions SET name=?,type=?,value=?,rules=?,scope=?,starts=?,ends=?,status=?,code=? WHERE id=? AND tenant_id=?", ...vals, Number(id), T(s));
  else run("INSERT INTO promotions(tenant_id,name,type,value,rules,scope,starts,ends,status,code) VALUES(?,?,?,?,?,?,?,?,?,?)", T(s), ...vals);
  logAction(s, "promo.save", "promotion", id || body.name);
  json(res, 200, { ok: true });
}
function apiAdminPromoDelete(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  run("DELETE FROM promotions WHERE id=? AND tenant_id=?", Number(id), T(s));
  logAction(s, "promo.delete", "promotion", id);
  json(res, 200, { ok: true });
}

/* ---------------- sellers / rfq / returns / settlements ---------------- */
function apiAdminSellers(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { sellers: all("SELECT * FROM sellers WHERE tenant_id=? ORDER BY id", T(s)), roles: rl("sellerRoles") });
}
function apiAdminSellerSave(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  if (!body.name || !rl("sellerRoles").includes(body.role)) return bad(res, "Name and valid role required");
  if (id) run("UPDATE sellers SET name=?,role=?,email=?,status=?,commission_pct=? WHERE id=? AND tenant_id=?", String(body.name), String(body.role), String(body.email || ""), String(body.status || "active"), Number(body.commission_pct), Number(id), T(s));
  else run("INSERT INTO sellers(tenant_id,name,role,email,status,commission_pct) VALUES(?,?,?,?,?,?)", T(s), String(body.name), String(body.role), String(body.email || ""), "active", Number(body.commission_pct) || 5);
  logAction(s, "seller.save", "seller", id || body.name);
  json(res, 200, { ok: true });
}
function apiAdminSellerDelete(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  run("DELETE FROM sellers WHERE id=? AND tenant_id=?", Number(id), T(s));
  logAction(s, "seller.delete", "seller", id);
  json(res, 200, { ok: true });
}
function apiRfqCreate(req, res, url, s, body) {
  const p = get("SELECT id,title FROM products WHERE tenant_id=? AND id=?", T(s), body.product_id);
  if (!p) return bad(res, "Unknown product", 404);
  const ref = "RFQ-" + (1000 + get("SELECT COUNT(*) c FROM rfqs WHERE tenant_id=?", T(s)).c + 1);
  run("INSERT INTO rfqs(tenant_id,ref,product_id,buyer_name,buyer_email,qty,target_price,currency,status) VALUES(?,?,?,?,?,?,?,?, 'open')",
    T(s), ref, p.id, String(body.buyer_name || ""), String(body.buyer_email || ""), Number(body.qty) || 1, Number(body.target_price) || 0, CFG(s).commerce.currency);
  logAction(s, "rfq.create", "rfq", ref, { product: p.id, qty: body.qty });
  notify(T(s), `New ${ref}`, `${body.buyer_name} requests ${body.qty} × ${p.title}`);
  json(res, 200, { ok: true, ref });
}
function apiAdminRfqs(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { rfqs: all("SELECT * FROM rfqs WHERE tenant_id=? ORDER BY created_at DESC", T(s)).map(r => ({ ...r, quotes: J(r.quotes, []) })) });
}
function apiAdminRfqUpdate(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const r = get("SELECT * FROM rfqs WHERE id=? AND tenant_id=?", Number(id), T(s));
  if (!r) return bad(res, "Unknown RFQ", 404);
  const quotes = J(r.quotes, []);
  if (body.quote) quotes.push({ ...body.quote, at: new Date().toISOString() });
  run("UPDATE rfqs SET status=?, quotes=? WHERE id=?", states.has("rfq", body.status) ? body.status : r.status, JSON.stringify(quotes), r.id);
  logAction(s, "rfq.update", "rfq", r.ref, { status: body.status });
  json(res, 200, { ok: true });
}
function apiReturnCreate(req, res, url, s, body) {
  const o = get("SELECT * FROM orders WHERE num=? AND owner=?", String(body.order_num || ""), ownerFor(s));
  if (!o) return bad(res, "Order not found", 404);
  const ref = "RET-" + (2000 + get("SELECT COUNT(*) c FROM returns WHERE tenant_id=?", T(s)).c + 1);
  run("INSERT INTO returns(tenant_id,ref,order_id,product_id,qty,reason,status) VALUES(?,?,?,?,?,?,?)",
    T(s), ref, o.id, String(body.product_id || ""), Number(body.qty) || 1, String(body.reason || ""), states.initial("return"));
  logAction(s, "return.create", "return", ref, { order: o.num });
  json(res, 200, { ok: true, ref });
}
function apiAdminReturns(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { returns: all("SELECT r.*, o.num order_num FROM returns r LEFT JOIN orders o ON o.id=r.order_id WHERE r.tenant_id=? ORDER BY r.created_at DESC", T(s)) });
}
function apiAdminReturnUpdate(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  if (!states.has("return", body.status)) return bad(res, "Invalid status");
  const r = get("SELECT * FROM returns WHERE id=? AND tenant_id=?", Number(id), T(s));
  if (!r) return bad(res, "Unknown return", 404);
  /* the machine runs claw_back_offers where the transition's row names it */
  const { patch } = states.apply("return", { tenantId: T(s), from: r.status, to: body.status, row: r });
  run("UPDATE returns SET " + Object.keys(patch).map(k => k + "=?").join(", ") + " WHERE id=? AND tenant_id=?", ...Object.values(patch), Number(id), T(s));
  logAction(s, "return.update", "return", id, { status: body.status });
  json(res, 200, { ok: true });
}
function apiOffersAnalytics(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const a = offers.analytics(T(s));
  const redemptions = all("SELECT * FROM coupon_redemptions WHERE tenant_id=? ORDER BY id DESC LIMIT 200", T(s));
  json(res, 200, Object.assign({ redemptions }, a));
}
function apiAdminSettlements(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { settlements: all("SELECT st.*, se.name seller FROM settlements st LEFT JOIN sellers se ON se.id=st.seller_id WHERE st.tenant_id=? ORDER BY st.id DESC", T(s)) });
}
function apiAdminSettlementGenerate(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  const period = String(body.period || new Date().toISOString().slice(0, 7));
  if (!/^\d{4}-\d{2}$/.test(period)) return bad(res, "period must be YYYY-MM", 400);
  /* gross is the LINE value (order_items carries price and qty — orders does not, so the old
     sum was NaN), over orders that actually stood; and a period settles once per seller */
  const lines = all("SELECT oi.product_id, oi.price, oi.qty FROM orders o JOIN order_items oi ON oi.order_id=o.id WHERE o.tenant_id=? AND strftime('%Y-%m', o.created_at)=? AND COALESCE(o.status,'') NOT IN ('cancelled','refunded','returned')", t, period);
  let made = 0, skipped = 0;
  const bySeller = {};
  for (const o of lines) {
    const p = get("SELECT supplier_id FROM products WHERE tenant_id=? AND id=?", t, o.product_id);
    if (!p || !p.supplier_id) continue;
    bySeller[p.supplier_id] = (bySeller[p.supplier_id] || 0) + (Number(o.price) || 0) * (Number(o.qty) || 0);
  }
  for (const [sid, gross] of Object.entries(bySeller)) {
    const seller = get("SELECT * FROM sellers WHERE id=? AND tenant_id=?", Number(sid), t);
    if (!seller) continue;
    if (get("SELECT id FROM settlements WHERE tenant_id=? AND seller_id=? AND period=?", t, seller.id, period)) { skipped++; continue; }
    const comm = +(gross * seller.commission_pct / 100).toFixed(2);
    run("INSERT INTO settlements(tenant_id,ref,seller_id,gross,commission,net,status,period) VALUES(?,?,?,?,?,?, 'pending', ?)",
      t, "STL-" + (3000 + get("SELECT COUNT(*) c FROM settlements WHERE tenant_id=?", t).c + 1), seller.id, +gross.toFixed(2), comm, +(gross - comm).toFixed(2), period);
    made++;
  }
  logAction(s, "settlement.generate", "settlement", period, { count: made });
  json(res, 200, { ok: true, generated: made, already_settled: skipped });
}
function apiAdminAnalytics(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const t = T(s);
  const byDay = all("SELECT date(created_at) d, COUNT(*) orders, COALESCE(SUM(total),0) revenue FROM orders WHERE tenant_id=? AND created_at>=datetime('now','-30 days') GROUP BY d ORDER BY d", t);
  const topProducts = all("SELECT oi.product_id, p.title, p.emoji, SUM(oi.qty) units, SUM(oi.qty*oi.price) rev FROM order_items oi JOIN orders o ON o.id=oi.order_id AND o.tenant_id=? JOIN products p ON p.tenant_id=o.tenant_id AND p.id=oi.product_id GROUP BY oi.product_id ORDER BY rev DESC LIMIT 8", t);
  const byIndustry = all("SELECT tx.name industry, SUM(oi.qty*oi.price) rev FROM order_items oi JOIN orders o ON o.id=oi.order_id AND o.tenant_id=? JOIN products p ON p.tenant_id=o.tenant_id AND p.id=oi.product_id JOIN taxonomy tx ON tx.id=p.node_id GROUP BY tx.name ORDER BY rev DESC", t);
  const byType = all("SELECT type, COUNT(*) c FROM products WHERE tenant_id=? GROUP BY type", t);
  const invValue = get("SELECT COALESCE(SUM(i.qty*s.price),0) v FROM inventory i JOIN skus s ON s.id=i.sku_id AND s.tenant_id=i.tenant_id WHERE i.tenant_id=?", t).v;
  const funnel = { views: get("SELECT COUNT(*) c FROM view_history WHERE owner LIKE 't' || ? || ':%'", String(t)).c, carts: get("SELECT COUNT(DISTINCT owner) c FROM cart_items WHERE owner LIKE 't' || ? || ':%'", String(t)).c, orders: get("SELECT COUNT(*) c FROM orders WHERE tenant_id=?", t).c };
  json(res, 200, { byDay, topProducts, byIndustry, byType, invValue, funnel, lowStock: all("SELECT id,title,stock FROM products WHERE tenant_id=? AND stock<=10 ORDER BY stock LIMIT 10", t) });
}
function apiAdminModePut(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const mode = deployModeOr(body.mode);
  const inds = Array.isArray(body.industries) ? JSON.stringify(body.industries) : "[]";
  run("UPDATE tenants SET mode=?, industries=? WHERE id=?", mode, inds, T(s));
  s.tenant.mode = mode; s.tenant.industries = inds;
  logAction(s, "tenant.mode", "tenant", T(s), { mode, industries: body.industries });
  json(res, 200, { ok: true, mode, industries: J(inds, []) });
}

/* ================= UNIVERSAL ENTITY ENGINE ================= */
const entity = require("./entity.js");
function entityPerm(s, def, write) {
  const roles = write ? (def.perm.write || []) : (def.perm.read || []);
  if (def.platformOnly) return roles.includes("platform") && !!s.platform_admin;
  if (roles.includes("platform") && s.platform_admin) return true;
  if (roles.includes("admin") && isAdmin(s)) return true;
  return false;
}
function apiEntities(req, res, url, s) {
  const defs = entity.allEntities(T(s));
  const out = {};
  for (const [k, d] of Object.entries(defs)) {
    if (!entityPerm(s, d, false)) continue;
    /* options may be an inline array OR a string naming a registry vocabulary the console
       resolves client-side ("lifecycle", "productTypes"…). The string is what the console's
       fieldInput needs to populate the select — dropping it rendered those selects EMPTY,
       and collect() then submitted "" for the field, so editing a product silently wiped
       its lifecycle (unpublishing it) and its type. Both shapes are data, both are kept */
    out[k] = { ...d, fields: d.fields.map(f => ({ ...f, options: (Array.isArray(f.options) || typeof f.options === "string") ? f.options : undefined })) };
  }
  json(res, 200, { entities: out });
}
function apiEntityList(req, res, url, s, body, key) {
  const defs = entity.allEntities(T(s));
  const def = defs[key];
  if (!def) return bad(res, "Unknown entity", 404);
  if (!entityPerm(s, def, false)) return bad(res, "Not permitted", 403);
  if (!requireSection(s, res, rbac.sectionForEntity(key), "read")) return;
  const hide = governance.isSoft(key) && url.searchParams.get("trash") !== "1";
  run("INSERT INTO entity_usage(tenant_id,entity,action,at) VALUES(?,?,?,datetime('now')) ON CONFLICT(tenant_id,entity,action) DO UPDATE SET at=datetime('now')", T(s), key, "list");
  /* pass server-side filters into the entity engine: `q` (free text) and any other
     search param (field equality). Both are whitelisted and parameterized in the engine,
     which is what makes an entity such as `sku` queryable past the browse cap once the
     corpus is activated (~2,000 SKUs on the flagship). */
  const where = {};
  for (const [k, v] of url.searchParams.entries()) if (k !== "q" && k !== "trash") where[k] = v;
  const opts = { hideDeleted: hide, q: url.searchParams.get("q") || "" };
  if (Object.keys(where).length) opts.where = where;
  json(res, 200, { entity: key, rows: entity.listEntities(T(s), key, opts) });
}
function apiEntityCreate(req, res, url, s, body, key) {
  const defs = entity.allEntities(T(s));
  const def = defs[key];
  if (!def) return bad(res, "Unknown entity", 404);
  if (!entityPerm(s, def, true)) return bad(res, "Not permitted", 403);
  if (!requireSection(s, res, rbac.sectionForEntity(key), "write")) return;
  const r = entity.createEntity(T(s), key, body || {});
  if (r.error) return bad(res, r.error);
  run("INSERT INTO entity_usage(tenant_id,entity,action,at) VALUES(?,?,?,datetime('now')) ON CONFLICT(tenant_id,entity,action) DO UPDATE SET at=datetime('now')", T(s), key, "create");
  logAction(s, key + ".create", key, r.id, body);
  json(res, 200, { ok: true, id: r.id });
}
function apiEntityUpdate(req, res, url, s, body, key, id) {
  const defs = entity.allEntities(T(s));
  const def = defs[key];
  if (!def) return bad(res, "Unknown entity", 404);
  if (!entityPerm(s, def, true)) return bad(res, "Not permitted", 403);
  if (!requireSection(s, res, rbac.sectionForEntity(key), "write")) return;
  const r = entity.updateEntity(T(s), key, id, body || {});
  if (r.error) return bad(res, r.error, r.code || 400);
  run("INSERT INTO entity_usage(tenant_id,entity,action,at) VALUES(?,?,?,datetime('now')) ON CONFLICT(tenant_id,entity,action) DO UPDATE SET at=datetime('now')", T(s), key, "update");
  logAction(s, key + ".update", key, id, body);
  json(res, 200, { ok: true });
}
function apiEntityDelete(req, res, url, s, body, key, id) {
  const defs = entity.allEntities(T(s));
  const def = defs[key];
  if (!def) return bad(res, "Unknown entity", 404);
  if (!entityPerm(s, def, true)) return bad(res, "Not permitted", 403);
  if (!requireSection(s, res, rbac.sectionForEntity(key), "write")) return;
  if (key === "currency") {
    if (require("./places.js").using("currency", String(id).toUpperCase()).length) return bad(res, "Currency is the official currency of a country entity — reassign that country first");
    if (all("SELECT value FROM settings WHERE key='commerce'").some(r => JSON.stringify(r).includes('"' + id + '"'))) return bad(res, "Currency in use by a store — switch that store's currency first");
  }
  if (governance.isSoft(key) && url.searchParams.get("hard") !== "1") {
    const t = governance.trash(T(s), key, id);
    if (t.error) return bad(res, t.error, t.code || 400);
    logAction(s, key + ".trash", key, id);
    return json(res, 200, { ok: true, trashed: true });
  }
  const r = entity.deleteEntity(T(s), key, id);
  if (r.error) return bad(res, r.error);
  logAction(s, key + ".delete", key, id);
  json(res, 200, { ok: true });
}
/* ---------- governance: trash, restore, purge, retention ---------- */
function apiTrashList(req, res, url, s) { if (!requireAdmin(s, res)) return; json(res, 200, { counts: governance.counts(T(s)), items: governance.listTrash(T(s), 100), retention: governance.getRetention(T(s)) }); }
function apiTrashRestore(req, res, url, s, body, key, id) {
  if (!requireAdmin(s, res)) return;
  const r = governance.restore(T(s), key, id); if (r.error) return bad(res, r.error, r.code || 400);
  logAction(s, key + ".restore", key, id, {}, req); json(res, 200, { ok: true });
}
function apiTrashPurge(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return; const r = governance.purge(T(s)); logAction(s, "governance.purge", "governance", null, { purged: r.purged }, req); json(res, 200, r);
}
function apiRetentionGet(req, res, url, s) { if (!requireAdmin(s, res)) return; json(res, 200, { retention: governance.getRetention(T(s)), defaults: governance.defaultRetention(), soft: [...governance.SOFT] }); }
function apiRetentionPut(req, res, url, s, body) { if (!requireAdmin(s, res)) return; governance.setRetention(T(s), body || {}); logAction(s, "governance.retention", "governance", null, { changed: Object.keys(body || {}).join(",") }, req); json(res, 200, { ok: true, retention: governance.getRetention(T(s)) }); }
function apiAdminPurgeExpired(req, res, url, s) { if (!requirePlatform(s, res)) return; let total = {}; for (const t of all("SELECT id FROM tenants")) { const r = governance.purge(t.id); Object.assign(total, r.purged); } logAction(s, "governance.purge_all", "governance", null, { purged: total }, req); json(res, 200, { ok: true, purged: total }); }
function apiEntityDefSave(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  const key = String(body.key || "").trim().toLowerCase().replace(/[^a-z0-9_]/g, "");
  if (!key || !body.label || !Array.isArray(body.fields)) return bad(res, "key, label and fields[] required");
  const def = { table: null, storage: "json", pk: "id", label: String(body.label), icon: String(body.icon || "🧬"), perm: { read: ["admin", "platform"], write: ["admin", "platform"] }, fields: body.fields };
  run("INSERT INTO entity_defs(key,scope,tenant_id,def) VALUES(?,?,?,?) ON CONFLICT(key,scope,tenant_id) DO UPDATE SET def=excluded.def",
    key, "platform", 0, JSON.stringify(def));
  logAction(s, "entity_def.save", "entity_def", key);
  json(res, 200, { ok: true });
}
 function apiEntityDefsList(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const { ENTITY_DEFS } = require("./entity.js");
  const custom = all("SELECT key, scope, tenant_id, def FROM entity_defs WHERE scope='platform'");
  const customKeys = new Set(custom.map(r => r.key));
  const builtIn = Object.entries(ENTITY_DEFS).map(([key, def]) => ({
    key, def: JSON.stringify(def), isBuiltIn: true
  }));
  const customRows = custom.map(r => ({ ...r, isBuiltIn: false }));
  json(res, 200, { rows: [...builtIn, ...customRows] });
}
 function apiEntityDefDelete(req, res, url, s, body, key) {
  if (!requirePlatform(s, res)) return;
  run("DELETE FROM entity_defs WHERE key=? AND scope='platform'", key);
  run("DELETE FROM entity_data WHERE entity=?", key);
  logAction(s, "entity_def.delete", "entity_def", key);
  json(res, 200, { ok: true });
}
 function apiEntityDefEnable(req, res, url, s, body, key) {
  if (!requirePlatform(s, res)) return;
  const tenantId = url.searchParams.get("tenant_id");
  if (!tenantId) return bad(res, "tenant_id required", 400);
  const { ENTITY_DEFS } = require("./entity.js");
  const platformDef = ENTITY_DEFS[key];
  const defStr = platformDef ? JSON.stringify(platformDef) : "{}";
  run("INSERT INTO entity_defs(key,scope,tenant_id,def) VALUES(?,?,?,?) ON CONFLICT(key,scope,tenant_id) DO UPDATE SET def=excluded.def",
    key, "tenant", Number(tenantId), defStr);
  logAction(s, "entity_def.enable", "entity_def", key);
  json(res, 200, { ok: true });
}
 function apiEntityDefDisable(req, res, url, s, body, key) {
  if (!requirePlatform(s, res)) return;
  const tenantId = url.searchParams.get("tenant_id");
  if (!tenantId) return bad(res, "tenant_id required", 400);
  run("DELETE FROM entity_defs WHERE key=? AND scope='tenant' AND tenant_id=?", key, Number(tenantId));
  logAction(s, "entity_def.disable", "entity_def", key);
  json(res, 200, { ok: true });
}
 function apiTenantEntityDefs(req, res, url, s) {
  const tenantId = T(s);
  const rows = all("SELECT key, def FROM entity_defs WHERE scope='tenant' AND tenant_id=?", tenantId);
  const out = {};
  for (const r of rows) { try { out[r.key] = JSON.parse(r.def || "{}"); } catch (e) { } }
  json(res, 200, { entities: out });
}


/* ========== Global Entity Configuration API ========== */
function apiEntityTypeList(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const entity = url.searchParams.get('entity');
  const q = entity ? 'WHERE entity=?' : '';
  const p = entity ? [entity] : [];
  json(res, 200, { types: all(`SELECT * FROM entity_types ${q} ORDER BY entity, type_key`, ...p) });
}
function apiEntityTypeCreate(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  if (!body.entity || !body.type_key || !body.label) return bad(res, 'entity, type_key, label required', 400);
  run('INSERT INTO entity_types(entity,type_key,label,icon,fields,config) VALUES(?,?,?,?,?,?)',
    body.entity, body.type_key, body.label, body.icon || '📝', JSON.stringify(body.fields || []), JSON.stringify(body.config || {}));
  logAction(s, 'entity_type.create', 'entity_type', `${body.entity}:${body.type_key}`);
  json(res, 200, { ok: true });
}
function apiEntityTypeUpdate(req, res, url, s, body, entity, type_key) {
  if (!requirePlatform(s, res)) return;
  run('UPDATE entity_types SET label=?, icon=?, fields=?, config=? WHERE entity=? AND type_key=?',
    body.label, body.icon, JSON.stringify(body.fields || []), JSON.stringify(body.config || {}), entity, type_key);
  logAction(s, 'entity_type.update', 'entity_type', `${entity}:${type_key}`);
  json(res, 200, { ok: true });
}
function apiEntityTypeDelete(req, res, url, s, body, entity, type_key) {
  if (!requirePlatform(s, res)) return;
  run('DELETE FROM entity_types WHERE entity=? AND type_key=?', entity, type_key);
  logAction(s, 'entity_type.delete', 'entity_type', `${entity}:${type_key}`);
  json(res, 200, { ok: true });
}
function apiTenantEntityList(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const tenantId = url.searchParams.get('tenant_id');
  const q = tenantId ? 'WHERE tenant_id=?' : '';
  const p = tenantId ? [tenantId] : [];
  json(res, 200, { entities: all(`SELECT * FROM tenant_entities ${q} ORDER BY entity`, ...p) });
}
function apiTenantEntityConfig(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  if (!body.tenant_id || !body.entity) return bad(res, 'tenant_id and entity required', 400);
  run('INSERT INTO tenant_entities(tenant_id,entity,enabled,requirement,custom_name,config) VALUES(?,?,?,?,?,?) ON CONFLICT(tenant_id,entity) DO UPDATE SET enabled=excluded.enabled,requirement=excluded.requirement,custom_name=excluded.custom_name,config=excluded.config',
    body.tenant_id, body.entity, body.enabled !== false ? 1 : 0, body.requirement || 'optional', body.custom_name || null, JSON.stringify(body.config || {}));
  logAction(s, 'tenant_entity.configure', 'tenant_entity', `${body.tenant_id}:${body.entity}`);
  json(res, 200, { ok: true });
}
function apiTenantFieldConfig(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  if (!body.tenant_id || !body.entity || !body.field_key) return bad(res, 'tenant_id, entity and field_key required', 400);
  run('INSERT INTO entity_field_config(tenant_id,entity,field_key,required,hidden,config) VALUES(?,?,?,?,?,?) ON CONFLICT(tenant_id,entity,field_key) DO UPDATE SET required=excluded.required,hidden=excluded.hidden,config=excluded.config',
    body.tenant_id, body.entity, body.field_key, body.required ? 1 : 0, body.hidden ? 1 : 0, JSON.stringify(body.config || {}));
  logAction(s, 'entity_field.configure', 'entity_field', `${body.tenant_id}:${body.entity}:${body.field_key}`);
  json(res, 200, { ok: true });
}
/* ---------- Global Platform: cross-tenant commerce data ----------
   One generic reader serves every entity-backed store capability. The Store Console
   reads ONE tenant through /api/meta/entity/:key; the Platform Console reads ACROSS
   stores through /api/platform/data/:key. Both resolve through the same definitions,
   the same field whitelist and the same parameterized predicates in lib/entity.js, so
   a capability's data model is defined exactly once — the platform never forks a store's
   schema, and the store never diverges from the platform.
   GET /api/platform/data enumerates the served entities so the console builds its Global
   Operations surface from live metadata rather than a hardcoded menu (zero hard-coding). */
function apiPlatformDataIndex(req, res, url, s) {
  if (!requirePlatformSection(s, res, "gdata", "read")) return;
  const defs = entity.allEntities(null);
  /* the index carries each entity's list-visible fields and pk so the console renders a
     cross-store table without a second field-definition copy anywhere (the Store Console
     reads the very same defs through /api/meta/entities). */
  /* platform-level registries (countries, currencies, tax modes, the uv_* universes…)
     are datasets too — they are what a Geography or Tenants leaf is about — so only the
     storage kind gates the index, never the scope. Excluding them made such a leaf fall
     through to the universe view and render the wrong records with no editor */
  const entities = Object.entries(defs)
    .filter(([key, def]) => def.storage === "json" || def.table)
    .map(([key, def]) => ({
      key, name: def.name || key, soft: governance.isSoft(key),
      /* a platform-level registry carries no store column; the console renders one only
         for genuinely store-scoped datasets (the same test the reader's `multi` makes) */
      tenantScoped: !(def.platformOnly || def.noTenant), pk: def.pk || "id",
      pkType: def.pkType === "text" ? "text" : "number",
      writable: (def.perm.write || []).includes("platform"),
      fields: (def.fields || []).filter(f => f.list).map(f => ({ key: f.key, label: f.label, type: f.type, ...(f.display ? { display: f.display } : {}) }))
    }))
    .sort((a, b) => a.key.localeCompare(b.key));
  const tenants = all("SELECT id, name, slug FROM tenants ORDER BY name").map(t => ({ id: t.id, name: t.name, slug: t.slug }));
  json(res, 200, { entities, tenants });
}
/* a configured app's dataset answers to the app's own grant; every other dataset to gdata */
const platformDataSection = key => (authz.configuredApps().some(a => a.key === key && !a.tenant_id) ? authz.APP_PREFIX + key : "gdata");
function apiPlatformDataList(req, res, url, s, body, key) {
  if (!requirePlatformSection(s, res, platformDataSection(key), "read")) return;
  const opts = { q: url.searchParams.get("q") || "", limit: url.searchParams.get("limit") || 500 };
  const hide = governance.isSoft(key) && url.searchParams.get("trash") !== "1";
  if (hide) opts.hideDeleted = true;
  const tenantId = url.searchParams.get("tenant_id");
  if (tenantId) opts.tenantId = tenantId;
  /* the same whitelisted, parameterized field predicates the store endpoint accepts —
     nothing arbitrary reaches SQL, and a platform query is as bounded as a store one */
  const where = {};
  for (const [k, v] of url.searchParams.entries())
    if (!["q", "trash", "tenant_id", "limit"].includes(k)) where[k] = v;
  if (Object.keys(where).length) opts.where = where;
  const rows = entity.listEntitiesGlobal(key, opts);
  if (rows === null) return bad(res, "Unknown entity", 404);
  json(res, 200, { entity: key, rows });
}
/* ---------- Global Platform: cross-tenant record writes + bulk import / export ----------
   The write mirror of the reader above, built on the SAME engine the Store Console's
   entity editor uses (lib/entity.js): the same definitions, the same validation, the same
   parameterized writes — never a second copy of a capability's schema. Two structural
   differences, the same two the reader has: (1) the target tenant is chosen by the
   request, and (2) platform-level registries (countries, currencies, the uv_* universes…)
   are written at platform scope (tenant 0) so every store inherits the row, instead of it
   being filed under whichever store the operator happened to be standing on.
   Authorization is the platform's own route guard — the section the Data Studio leaf lives
   in — so a console button and its API can never disagree about who may write a dataset. */
function platformEntityDef(key, tid) {
  return entity.allEntities(null)[key] || (tid != null ? entity.allEntities(tid)[key] : null) || null;
}
function platformWriteTenant(def, tidRaw, res) {
  if (def.platformOnly || def.noTenant) return 0;               /* a platform-level registry */
  if (def.storage === "json") return Number(tidRaw) || 0;        /* a universe: platform level unless a store is named */
  const tid = Number(tidRaw);
  if (!(tid > 0)) { bad(res, "Pick a store — this dataset is store-scoped", 400); return null; }
  return tid;
}
function apiPlatformDataDef(req, res, url, s, body, key) {
  if (!requirePlatformSection(s, res, platformDataSection(key), "read")) return;
  const def = platformEntityDef(key, null);
  if (!def || !(def.storage === "json" || def.table)) return bad(res, "Unknown entity", 404);
  json(res, 200, {
    key, name: def.name || key, label: def.label, icon: def.icon,
    pk: def.pk || "id", pkType: def.pkType === "text" ? "text" : "number",
    composite: !!def.composite, storage: def.storage,
    platformLevel: !!(def.platformOnly || def.noTenant),
    writable: (def.perm.write || []).includes("platform"),
    fields: def.fields.map(f => ({ ...f, options: (Array.isArray(f.options) || typeof f.options === "string") ? f.options : undefined }))
  });
}
function apiPlatformDataCreate(req, res, url, s, body, key) {
  if (!requirePlatformRoute(s, res, url, "write")) return;
  const tidRaw = Number((body && body.tenant_id) || url.searchParams.get("tenant_id")) || null;
  const def = platformEntityDef(key, tidRaw);
  if (!def) return bad(res, "Unknown entity", 404);
  if (!entityPerm(s, def, true)) return bad(res, "Not permitted", 403);
  const tid = platformWriteTenant(def, tidRaw, res); if (tid == null) return;
  const row = { ...(body || {}) }; if (def.storage === "json") delete row.tenant_id;  /* the target tenant is metadata of the write, not a field */
  const r = entity.createEntity(tid, key, row);
  if (r.error) return bad(res, r.error);
  logAction(s, key + ".create", key, r.id, Object.assign({ scope: tid }, row), req);
  json(res, 200, { ok: true, id: r.id });
}
function apiPlatformDataUpdate(req, res, url, s, body, key, id) {
  if (!requirePlatformRoute(s, res, url, "write")) return;
  const tidRaw = Number((body && body.tenant_id) || url.searchParams.get("tenant_id")) || null;
  const def = platformEntityDef(key, tidRaw);
  if (!def) return bad(res, "Unknown entity", 404);
  if (!entityPerm(s, def, true)) return bad(res, "Not permitted", 403);
  const tid = platformWriteTenant(def, tidRaw, res); if (tid == null) return;
  const row = { ...(body || {}) }; if (def.storage === "json") delete row.tenant_id;
  const r = entity.updateEntity(tid, key, id, row);
  if (r.error) return bad(res, r.error, r.code || 400);
  logAction(s, key + ".update", key, id, row, req);
  json(res, 200, { ok: true });
}
function apiPlatformDataDelete(req, res, url, s, body, key, id) {
  if (!requirePlatformRoute(s, res, url, "write")) return;
  const tidRaw = Number((body && body.tenant_id) || url.searchParams.get("tenant_id")) || null;
  const def = platformEntityDef(key, tidRaw);
  if (!def) return bad(res, "Unknown entity", 404);
  if (!entityPerm(s, def, true)) return bad(res, "Not permitted", 403);
  const tid = platformWriteTenant(def, tidRaw, res); if (tid == null) return;
  if (key === "currency") {
    if (require("./places.js").using("currency", String(id).toUpperCase()).length) return bad(res, "Currency is the official currency of a country entity — reassign that country first");
    if (all("SELECT value FROM settings WHERE key='commerce'").some(r => JSON.stringify(r).includes('"' + String(id) + '"'))) return bad(res, "Currency in use by a store — switch that store's currency first");
  }
  if (key === "country") {
    /* a country is the jurisdiction of stores and the availability anchor of every payment
       provider seeded for it, so the engine's raw FK refusal is replaced by the two facts
       an operator can actually act on */
    /* the stores serving it, or a place in it, are answered by the kernel (lib/stores.js) */
    if (require("./stores.js").serving(String(id).toUpperCase()).length) return bad(res, "A store serves this country — switch that store's jurisdiction and places first");
    /* the availability links to global providers are DERIVED — reconciliation materialised them
       the moment the country was created, so they are not an operator's per-provider choice.
       Blocking deletion on them would make every country undeletable. They are cleaned up here
       instead, and the exemptions an operator set for this country go with it, so removing a
       country leaves no dangling edges for reconciliation to trip over on the next boot */
    const cc = String(id).toUpperCase();
    run("DELETE FROM provider_availability WHERE country_code=?", cc);
    /* a country's subdivisions are derived from it, so they leave with it — no dangling
       jurisdiction rows (an address still pointing at a removed country's state reads its
       stored code; the master it resolved from is simply gone) */
    registry.withdrawCountry(cc);
    try {
      const exRow = get("SELECT value v FROM platform_settings WHERE key='provider_availability_exempt'");
      if (exRow) { const list = JSON.parse(exRow.v || "[]").filter(x => !x.endsWith("|" + cc)); run("INSERT INTO platform_settings(key,value) VALUES('provider_availability_exempt',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", JSON.stringify(list)); }
    } catch (e) { }
  }
  if (governance.isSoft(key) && url.searchParams.get("hard") !== "1") {
    const t = governance.trash(tid, key, id);
    if (t.error) return bad(res, t.error, t.code || 400);
    logAction(s, key + ".trash", key, id, {}, req);
    return json(res, 200, { ok: true, trashed: true });
  }
  const r = entity.deleteEntity(tid, key, id);
  if (r.error) return bad(res, r.error);
  logAction(s, key + ".delete", key, id, {}, req);
  json(res, 200, { ok: true });
}
/* a minimal RFC-4180 CSV reader: quoted fields, embedded commas/quotes and CRLF all
   survive, so a spreadsheet pasted from Excel or Numbers parses the way its author
   expects rather than splitting on every comma the cell happens to contain */
function parseCsv(text) {
  const rows = [], out = [];
  let row = [], cur = "", q = false;
  const s = String(text || "").replace(/\r\n|\r/g, "\n");
  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    if (q) { if (c === '"') { if (s[i + 1] === '"') { cur += '"'; i++; } else q = false; } else cur += c; }
    else if (c === '"') q = true;
    else if (c === ",") { row.push(cur); cur = ""; }
    else if (c === "\n") { row.push(cur); rows.push(row); row = []; cur = ""; }
    else cur += c;
  }
  if (cur !== "" || row.length) { row.push(cur); rows.push(row); }
  const head = (rows.shift() || []).map(h => String(h == null ? "" : h).trim());
  for (const r of rows) {
    if (!r.some(x => String(x == null ? "" : x).trim() !== "")) continue;   /* blank lines */
    const o = {};
    head.forEach((h, i) => { if (h) o[h] = r[i] == null ? "" : String(r[i]); });
    out.push(o);
  }
  return out;
}
/* CSV or JSON, auto-detected so the operator pastes either into one box; explicit
   shapes (rows[] / json / csv) are kept for programmatic callers */
function parseImportPayload(body) {
  if (Array.isArray(body)) return body;
  if (body && Array.isArray(body.rows)) return body.rows;
  if (body && typeof body.json === "string") { try { const v = JSON.parse(body.json); return Array.isArray(v) ? v : null; } catch (e) { return null; } }
  if (body && (typeof body.csv === "string" || typeof body.text === "string")) {
    const t = String(body.csv != null ? body.csv : body.text).trim();
    if (t[0] === "[" || t[0] === "{") { try { const v = JSON.parse(t); return Array.isArray(v) ? v : null; } catch (e) { return null; } }
    return parseCsv(t);
  }
  return null;
}
function apiPlatformDataImport(req, res, url, s, body, key) {
  if (!requirePlatformRoute(s, res, url, "write")) return;
  const tidRaw = Number((body && body.tenant_id) || url.searchParams.get("tenant_id")) || null;
  const def = platformEntityDef(key, tidRaw);
  if (!def) return bad(res, "Unknown entity", 404);
  if (!entityPerm(s, def, true)) return bad(res, "Not permitted", 403);
  const tid = platformWriteTenant(def, tidRaw, res); if (tid == null) return;
  const rows = parseImportPayload(body);
  if (!rows || !Array.isArray(rows)) return bad(res, "No records — send a JSON array, {rows:[…]}, {json:\"…\"} or {csv:\"…\"}", 400);
  if (rows.length > 5000) return bad(res, "Import is capped at 5,000 records per call — split the file", 400);
  let imported = 0; const failed = [];
  rows.forEach((raw, i) => {
    if (!raw || typeof raw !== "object" || Array.isArray(raw)) { failed.push({ index: i + 1, error: "not a record object" }); return; }
    const row = { ...raw }; if (def.storage === "json") delete row.tenant_id;
    const r = entity.createEntity(tid, key, row);
    if (r.error) failed.push({ index: i + 1, error: r.error });
    else imported++;
  });
  logAction(s, key + ".import", key, null, { imported, rejected: failed.length, scope: tid }, req);
  json(res, 200, { ok: true, imported, failed });
}
/* ---------- the export format registry ----------
   One map describes every format a dataset export can emit: a label the console shows, a
   file extension, a content type, and a renderer. A future format is one entry here and it
   surfaces in the console's export menu on its own (the menu is built from
   ?format=formats, never a second client-side list). The platform ships no binary
   dependencies by policy, so the spreadsheet and the PDF below are assembled from the
   formats' own documented text — a ZIP container is a handful of headers and a central
   directory, and a PDF is plain text with an offset table. */
function exportCell(row, col) {
  const v = row[col];
  if (v == null) return "";
  if (typeof v === "object") return JSON.stringify(v);
  return String(v);
}
function exportCols(def) {
  /* the declared fields are the columns, so an export round-trips back through the
     importer — and the pk leads, so a row keeps its identity across both */
  return [def.pk || "id"].concat((def.fields || []).map(f => f.key))
    .filter((c, i, a) => c && a.indexOf(c) === i);
}
/* a minimal ZIP writer (the container half of an .xlsx): local file headers, a central
   directory and an end-of-central-directory record, DEFLATE from zlib and CRC-32 from
   zlib.crc32. Only the entries' order and offsets matter to a reader, so the parts of the
   workbook are appended as they are built */
function zipWrite(parts) {
  const chunks = [], central = [];
  let offset = 0;
  for (const p of parts) {
    const name = Buffer.from(p.name, "utf8");
    const data = Buffer.isBuffer(p.data) ? p.data : Buffer.from(String(p.data), "utf8");
    const crc = zlib.crc32(data);
    const comp = zlib.deflateRawSync(data);
    const lh = Buffer.alloc(30);
    lh.writeUInt32LE(0x04034b50, 0);                /* local header signature */
    lh.writeUInt16LE(20, 4);                        /* version needed to extract */
    lh.writeUInt16LE(8, 8);                         /* method: DEFLATE */
    lh.writeUInt16LE(0x21, 12);                     /* DOS date: 1980-01-01 */
    lh.writeUInt32LE(crc, 14);
    lh.writeUInt32LE(comp.length, 18);
    lh.writeUInt32LE(data.length, 22);
    lh.writeUInt16LE(name.length, 26);
    chunks.push(lh, name, comp);
    const ch = Buffer.alloc(46);
    ch.writeUInt32LE(0x02014b50, 0);                /* central directory signature */
    ch.writeUInt16LE(20, 4);
    ch.writeUInt16LE(20, 6);
    ch.writeUInt16LE(8, 10);
    ch.writeUInt16LE(0x21, 14);
    ch.writeUInt32LE(crc, 16);
    ch.writeUInt32LE(comp.length, 20);
    ch.writeUInt32LE(data.length, 24);
    ch.writeUInt16LE(name.length, 28);
    ch.writeUInt32LE(offset, 42);                   /* where this entry's local header is */
    central.push(ch, name);
    offset += lh.length + name.length + comp.length;
  }
  const cd = Buffer.concat(central);
  const eocd = Buffer.alloc(22);
  eocd.writeUInt32LE(0x06054b50, 0);
  eocd.writeUInt16LE(parts.length, 10);             /* total entries */
  eocd.writeUInt32LE(cd.length, 12);
  eocd.writeUInt32LE(offset, 16);                   /* central directory offset */
  return Buffer.concat([Buffer.concat(chunks), cd, eocd]);
}
function xmlEsc(s) {
  return String(s == null ? "" : s)
    .replace(/[\x00-\x08\x0B\x0C\x0E-\x1F]/g, "")   /* illegal in XML 1.0 */
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
function xlsxColName(idx) {
  let n = idx + 1, s = "";
  while (n > 0) { const m = (n - 1) % 26; s = String.fromCharCode(65 + m) + s; n = Math.floor((n - 1) / 26); }
  return s;
}
/* an .xlsx is a zip of six small XML parts; cells carry inline strings so no shared-string
   table is needed, and a number that reads as one is written as a number so a spreadsheet
   keeps typing the column (a code like "007" stays text, a price stays numeric) */
function renderXlsx(rows, cols, title) {
  const widths = cols.map(c => {
    let w = String(c).length;
    for (let i = 0; i < Math.min(rows.length, 400); i++) w = Math.max(w, exportCell(rows[i], c).length);
    return Math.min(60, Math.max(8, Math.round(w * 1.15) + 2));
  });
  const cell = (r, c, ci, s) => {
    const ref = xlsxColName(ci) + (r + 1), v = exportCell(rows[r], c), t = v.trim();
    if (t !== "" && /^-?\d+(\.\d+)?$/.test(t))
      return `<c r="${ref}" s="${s}"><v>${xmlEsc(t)}</v></c>`;
    return `<c r="${ref}" t="inlineStr" s="${s}"><is><t xml:space="preserve">${xmlEsc(v)}</t></is></c>`;
  };
  const head = cols.map((c, i) => `<c r="${xlsxColName(i)}1" t="inlineStr" s="1"><is><t xml:space="preserve">${xmlEsc(c)}</t></is></c>`).join("");
  const body = rows.map((r, ri) => `<row r="${ri + 2}">${cols.map((c, ci) => cell(ri, c, ci, 0)).join("")}</row>`).join("");
  const parts = [
    { name: "[Content_Types].xml", data: `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/></Types>` },
    { name: "_rels/.rels", data: `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>` },
    { name: "xl/workbook.xml", data: `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="${xmlEsc(title).slice(0, 31) || "Sheet1"}" sheetId="1" r:id="rId1"/></sheets></workbook>` },
    { name: "xl/_rels/workbook.xml.rels", data: `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>` },
    { name: "xl/styles.xml", data: `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts><fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills><borders count="1"><border/></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/></cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>` },
    { name: "xl/worksheets/sheet1.xml", data: `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><cols>${cols.map((c, i) => `<col min="${i + 1}" max="${i + 1}" width="${widths[i]}" customWidth="1"/>`).join("")}</cols><sheetData><row r="1">${head}</row>${body}</sheetData></worksheet>` }
  ];
  return zipWrite(parts);
}
/* a minimal PDF: catalog, page tree, the three standard-14 fonts the layout uses, one
   content stream per page. The table is set in Courier (monospace, so the padded columns
   line up without a drawing engine) and a page breaks when the cursor reaches the foot.
   Only printable ASCII is kept — the standard fonts are single-byte, so an emoji or a
   currency glyph would corrupt the stream instead of degrading to a placeholder */
function pdfClean(s) { return String(s == null ? "" : s).replace(/[^\x20-\x7E]/g, "?").replace(/[\\()]/g, "\\$&").replace(/\r?\n/g, " "); }
function renderPdf(rows, cols, title, meta) {
  const W = 595, H = 842, ML = 40, MR = 40, MT = 40, MB = 46;
  const charW = 4.2, lineH = 9.6;                   /* Courier 7pt advance ≈ 4.2pt */
  const budget = Math.floor((W - ML - MR) / charW);
  let widths = cols.map(c => {
    let w = Math.max(3, String(c).length);
    for (let i = 0; i < Math.min(rows.length, 300); i++) w = Math.max(w, exportCell(rows[i], c).length);
    return Math.min(56, w);
  });
  const sum = widths.reduce((a, b) => a + b, 0);
  if (sum > budget) { const k = budget / sum; widths = widths.map(w => Math.max(3, Math.floor(w * k))); }
  const fit = (s, w) => { const t = pdfClean(s); return t.length > w ? t.slice(0, w) : t.padEnd(w, " "); };
  const headerLine = widths.map((w, i) => fit(cols[i], w)).join("");
  const rowLines = rows.map(r => widths.map((w, i) => fit(exportCell(r, cols[i]), w)).join(""));
  /* paginate: a title block on page 1, then rows until the foot, then the next page */
  const pages = [];
  let cur = [], y = H - MT;
  const head = (yy) => [
    `BT /F1 14 Tf ${ML} ${H - MT + 2} Td (${pdfClean(title)}) Tj ET`,
    `BT /F2 9 Tf ${ML} ${H - MT - 14} Td (${pdfClean(meta)}) Tj ET`,
    `BT /F3 7 Tf ${ML} ${yy} Td (${headerLine}) Tj ET`
  ];
  cur = head(H - MT - 34); y = H - MT - 34 - lineH;
  for (let i = 0; i < rowLines.length; i++) {
    if (y < MB) {
      pages.push(cur);
      cur = [`BT /F3 7 Tf ${ML} ${H - MT} Td (${headerLine}) Tj ET`];
      y = H - MT - lineH;
    }
    cur.push(`BT /F2 7 Tf ${ML} ${y} Td (${rowLines[i]}) Tj ET`);
    y -= lineH;
  }
  pages.push(cur);
  /* objects: 1 catalog, 2 page tree, 3-5 fonts, then page/content pairs */
  const objects = [
    "<< /Type /Catalog /Pages 2 0 R >>",
    `<< /Type /Pages /Kids [${pages.map((_, i) => (6 + i * 2) + " 0 R").join(" ")}] /Count ${pages.length} >>`,
    "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    "<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>",
    "<< /Type /Font /Subtype /Type1 /BaseFont /Courier-Bold >>"
  ];
  pages.forEach((linesArr, i) => {
    const po = 6 + i * 2, co = 7 + i * 2;
    const content = linesArr.join("\n") + `\nBT /F2 7 Tf ${ML} ${MB - 16} Td (Page ${i + 1} of ${pages.length}) Tj ET`;
    objects.push(`<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ${W} ${H}] /Resources << /Font << /F1 3 0 R /F2 4 0 R /F3 5 0 R >> >> /Contents ${co} 0 R >>`);
    objects.push(`<< /Length ${Buffer.byteLength(content, "latin1")} >>\nstream\n${content}\nendstream`);
  });
  let doc = "%PDF-1.4\n";
  const offsets = [0];
  objects.forEach((o, i) => { offsets.push(Buffer.byteLength(doc, "latin1")); doc += `${i + 1} 0 obj\n${o}\nendobj\n`; });
  const xrefAt = Buffer.byteLength(doc, "latin1");
  doc += `xref\n0 ${objects.length + 1}\n0000000000 65535 f \n`;
  for (let i = 1; i <= objects.length; i++) doc += String(offsets[i]).padStart(10, "0") + " 00000 n \n";
  doc += `trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xrefAt}\n%%EOF`;
  return Buffer.from(doc, "latin1");
}
/* the formats the export endpoint can render. Each renderer takes the filtered rows, the
   declared columns and a title, and returns the file body — adding a format is one entry */
const EXPORT_FORMATS = {
  csv: { label: "CSV (comma-separated values)", ext: "csv", ct: "text/csv; charset=utf-8", render: (rows, cols) => csvOf(rows.map(r => { const o = {}; for (const c of cols) o[c] = r[c]; return o; })) },
  json: { label: "JSON (array of records)", ext: "json", ct: "application/json; charset=utf-8", render: (rows, cols, title) => JSON.stringify({ entity: title, exported_at: new Date().toISOString(), rows }, null, 1) },
  xlsx: { label: "Excel spreadsheet (.xlsx)", ext: "xlsx", ct: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", render: (rows, cols, title) => renderXlsx(rows, cols, title) },
  pdf: { label: "PDF document", ext: "pdf", ct: "application/pdf", render: (rows, cols, title, meta) => renderPdf(rows, cols, title, meta) }
};
/* export scope: the console narrows the same filtered read four ways — everything the
   filters match, exactly the rows on screen (their primary keys are sent along, so the
   export cannot drift from what the operator is looking at), a row range, or a date window
   on one of the entity's own date-typed columns. Everything after the read is pure, so no
   scope parameter can reach SQL */
function applyExportScope(rows, def, url) {
  const sp = url.searchParams, pk = def.pk || "id";
  const ids = sp.get("ids");
  if (ids) {
    const want = new Set(String(ids).split(",").map(x => x.trim()).filter(Boolean));
    if (want.size) rows = rows.filter(r => want.has(String(r[pk] != null ? r[pk] : r.id)) || want.has(String(r.id)));
  }
  const from = Math.max(1, Number(sp.get("from")) || 0), to = Number(sp.get("to")) || 0;
  if (from > 1 || to > 0) rows = rows.slice(from - 1, to >= from ? to : undefined);
  const dcol = sp.get("date_col"), d1 = sp.get("date_from"), d2 = sp.get("date_to");
  if (dcol && (d1 || d2)) {
    const lo = d1 ? new Date(d1 + "T00:00:00") : null, hi = d2 ? new Date(d2 + "T23:59:59.999") : null;
    rows = rows.filter(r => {
      const raw = r[dcol];
      if (raw == null || raw === "") return false;
      const d = new Date(/^\d+$/.test(String(raw)) ? Number(raw) : String(raw));
      return !isNaN(d) && (!lo || d >= lo) && (!hi || d <= hi);
    });
  }
  return rows;
}
function apiPlatformDataExport(req, res, url, s, body, key) {
  if (!requirePlatformRoute(s, res, url, "read")) return;
  const def = platformEntityDef(key, null);
  if (!def) return bad(res, "Unknown entity", 404);
  /* the console's format menu is discovered, not hardcoded: ?format=formats answers the
     registry itself, so a format added above is selectable with no client change */
  const fmtParam = String(url.searchParams.get("format") || "csv").toLowerCase();
  if (fmtParam === "formats" || fmtParam === "list")
    return json(res, 200, { formats: Object.entries(EXPORT_FORMATS).map(([k, v]) => ({ key: k, label: v.label, ext: v.ext })) });
  const fmt = EXPORT_FORMATS[fmtParam] || (/json/i.test(fmtParam) ? EXPORT_FORMATS.json : EXPORT_FORMATS.csv);
  const opts = { q: url.searchParams.get("q") || "", limit: 5000 };
  const hide = governance.isSoft(key) && url.searchParams.get("trash") !== "1";
  if (hide) opts.hideDeleted = true;
  const tenantId = url.searchParams.get("tenant_id");
  if (tenantId) opts.tenantId = tenantId;
  let rows = entity.listEntitiesGlobal(key, opts);
  if (rows === null) return bad(res, "Unknown entity", 404);
  rows = applyExportScope(rows, def, url);
  const cols = exportCols(def);
  const name = String(key).replace(/[^\w.-]/g, "_");
  const out = fmt.render(rows, cols, key, `${rows.length} record${rows.length === 1 ? "" : "s"} · exported ${new Date().toISOString().slice(0, 16).replace("T", " ")} UTC`);
  res.writeHead(200, { "Content-Type": fmt.ct, "Content-Disposition": "attachment; filename=\"" + name + "." + fmt.ext + "\"" });
  res.end(Buffer.isBuffer(out) ? out : String(out));
}
/* the importer's template: the current columns of THIS dataset, with one example value per
   field derived from the field's own declaration — so an operator downloads the file the
   importer is guaranteed to accept, fills it in, and never has to discover the schema by
   trial and error. CSV and JSON shapes match the importer's auto-detection exactly */
function sampleValueFor(f) {
  const t = f.type || "text";
  if (t === "bool") return "1";
  if (t === "number") return "123";
  if (t === "money") return "99.90";
  if (t === "date") return "2026-01-31";
  if (t === "select") return (Array.isArray(f.options) && f.options.length ? String(f.options[0]) : "option");
  if (t === "multi" || t === "json") return f.type === "multi" ? "[]" : "{}";
  if (t === "textarea") return "Sample note for " + (f.label || f.key);
  if (t === "secret") return "";
  if (String(t).startsWith("ref:")) return "REF";
  return "Sample " + (f.label || f.key);
}
function apiPlatformDataSample(req, res, url, s, body, key) {
  if (!requirePlatformRoute(s, res, url, "read")) return;
  const def = platformEntityDef(key, null);
  if (!def || !(def.storage === "json" || def.table)) return bad(res, "Unknown entity", 404);
  const row = {};
  for (const f of def.fields)
    if (!f.readonly) row[f.key] = sampleValueFor(f);
  const pk = def.pk || "id";
  if (!(pk in row) && def.pkType === "text") row[pk] = "SAMPLE";
  const fmt = /json/i.test(String(url.searchParams.get("format"))) ? "json" : "csv";
  const name = String(key).replace(/[^\w.-]/g, "_") + "-sample";
  if (fmt === "json") {
    res.writeHead(200, { "Content-Type": "application/json; charset=utf-8", "Content-Disposition": "attachment; filename=\"" + name + ".json\"" });
    res.end(JSON.stringify([row], null, 1));
    return;
  }
  const cols = exportCols(def);
  res.writeHead(200, { "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": "attachment; filename=\"" + name + ".csv\"" });
  res.end(csvOf([row], cols));
}
/* ---------- Global Platform: cross-tenant fan-out executor ----------
   The composite capabilities behind the Store Console — stats, helpdesk, marketplace ads,
   finance, reviews/moderation, retention, experiments, planning, risk, logistics, tax,
   trash, audit, billing, webhooks, SSO, team — are tenant-scoped handlers that already
   encode their business logic exactly once. The platform does NOT re-implement a single
   one of them (that would duplicate the logic and the two sides would drift). Instead it
   resolves the same route from the same route table and runs it once per store under a
   scoped synthetic session, then collects the responses. One executor, one merge rule,
   every composite capability: zero duplicated logic, zero drift.
   Only read-only GET routes are eligible, and only those named in FANOUT_OK — that set is
   the security boundary and is data (a `meta_lists` row `platformFanout` overrides it, so
   an operator opens or closes a capability from Data Studio without a deploy). A store's
   own operator keeps full read+write in the Store Console; this surface is cross-store
   oversight, never a second editor (zero overlap). */
const FANOUT_DEFAULT = [
  "/api/admin/stats", "/api/admin/analytics", "/api/admin/monitor",
  "/api/admin/helpdesk/tickets", "/api/admin/helpdesk/sla",
  "/api/admin/ugc/queue", "/api/admin/reviews",
  "/api/marketplace/ads", "/api/admin/marketplace/metrics",
  "/api/admin/fin/disputes", "/api/admin/fin/payouts", "/api/admin/fin/ledger",
  "/api/admin/retention", "/api/admin/recurring", "/api/admin/memberships",
  "/api/admin/experiments",
  "/api/admin/planning", "/api/admin/planning/pos",
  "/api/admin/risk/queue", "/api/admin/risk/blocklist",
  "/api/shipments", "/api/admin/sla",
  "/api/qc/runs", "/api/qc/riders", "/api/qc/stores",
  "/api/admin/tax/report", "/api/admin/trash", "/api/admin/audit",
  "/api/admin/billing", "/api/admin/transfers", "/api/admin/payments",
  "/api/admin/webhooks", "/api/admin/sso", "/api/admin/staff", "/api/admin/roles",
  "/api/admin/gateways", "/api/admin/settings", "/api/admin/promotions", "/api/admin/users",
  "/api/affiliate/affiliates", "/api/affiliate/reports", "/api/affiliate/payouts", "/api/affiliate/networks"
];
function fanoutAllowed(path) {
  const row = get("SELECT items FROM meta_lists WHERE name='platformFanout'");
  if (row) { try { const j = JSON.parse(row.items); if (Array.isArray(j)) return j.map(String).includes(path); } catch (e) { } }
  return FANOUT_DEFAULT.includes(path);
}
function apiPlatformFanout(req, res, url, s, body, p1, p2, metrics) {
  if (!requirePlatformSection(s, res, "gops", "read")) return;
  const path = url.searchParams.get("path") || "";
  const routeKey = "GET " + path;
  const entry = routes.find(([k]) => k === routeKey);
  if (!entry || !fanoutAllowed(path)) return bad(res, "Capability not available for cross-store aggregation", 404);
  /* the query the store handler sees is the platform's own query minus the fan-out
     control params — nothing about the request is invented */
  const u2 = new URL(url.toString());
  u2.pathname = path;
  ["path", "flat", "tenant_id"].forEach(k => u2.searchParams.delete(k));
  const tid = url.searchParams.get("tenant_id");
  const tenants = tid ? all("SELECT id,name,slug FROM tenants WHERE id=? ORDER BY name", Number(tid)) : all("SELECT id,name,slug FROM tenants ORDER BY name");
  const results = [];
  for (const t of tenants) {
    /* a scoped synthetic session: the handler resolves to THIS store and sees its own
       admin, so requireAdmin/requireSection pass exactly as they would for the store's
       operator. The platform's own privileges never cross the boundary. */
    const adm = get("SELECT id FROM users WHERE tenant_id=? AND role='admin' ORDER BY id LIMIT 1", t.id);
    const cap = { code: 0, body: "" };
    const sres = { writeHead: c => { cap.code = c; }, end: b => { cap.body = String(b); } };
    const ssess = { tenant: { id: t.id }, user_id: adm ? adm.id : null, platform_admin: null, sid: s.sid, trace: s.trace };
    try {
      /* the full router call signature, metrics included — handlers such as the store
         monitor read `metrics.snapshot`, so a fan-out must look exactly like a routed
         request to the capability, not a stripped-down one */
      entry[1](req, sres, u2, ssess, {}, null, null, metrics);
      let data = null, err = null;
      try { const j = JSON.parse(cap.body); if (j && j.error) err = j.error; else data = j; } catch (e) { err = "unparsable response"; }
      results.push({ tenant_id: t.id, name: t.name, slug: t.slug, ok: !err && cap.code < 400, ...(err ? { error: err } : { data }) });
    } catch (e) { results.push({ tenant_id: t.id, name: t.name, slug: t.slug, ok: false, error: e.message }); }
  }
  /* `flat` merges the per-store payloads by one uniform rule — arrays concatenate with the
     store stamped on every object, numbers sum, other values keep the first store's — so a
     console view can render one cross-store table without knowing each payload's shape. */
  const flat = url.searchParams.get("flat") === "1";
  const merged = { capability: path.replace(/^\/api\//, ""), count: results.length, results };
  if (flat) {
    const acc = {};
    for (const r of results) {
      if (!r.ok || !r.data || typeof r.data !== "object") continue;
      for (const [k, v] of Object.entries(r.data)) {
        if (Array.isArray(v)) {
          const stamped = v.map(x => (x && typeof x === "object" && !Array.isArray(x)) ? { tenant_id: r.tenant_id, store: r.name, ...x } : x);
          acc[k] = (acc[k] || []).concat(stamped);
        } else if (typeof v === "number" && isFinite(v)) acc[k] = (acc[k] || 0) + v;
        else if (!(k in acc)) acc[k] = v;
      }
    }
    merged.merged = acc;
  }
  logAction(s, "platform.fanout", "fanout", path, { stores: results.length, flat });
  json(res, 200, merged);
}
function apiAttributeList(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  json(res, 200, { attributes: all('SELECT * FROM attribute_defs ORDER BY category, key') });
}
function apiAttributeCreate(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  if (!body.key || !body.label) return bad(res, 'key and label required', 400);
  /* the platform-global registry (tenant_id 0, like entity_defs) — attribute_defs requires
     a tenant_id, and the platform scope is the root tenant. */
  run('INSERT INTO attribute_defs(tenant_id,key,label,type,options,validation,category) VALUES(?,?,?,?,?,?,?)',
    0, body.key, body.label, body.type || 'text', JSON.stringify(body.options || []), JSON.stringify(body.validation || {}), body.category || '');
  logAction(s, 'attribute.create', 'attribute', body.key);
  json(res, 200, { ok: true });
}
function apiEntityAttributeList(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const entity = url.searchParams.get('entity');
  const q = entity ? 'WHERE entity=?' : '';
  const p = entity ? [entity] : [];
  json(res, 200, { attributes: all(`SELECT * FROM entity_attributes ${q} ORDER BY position`, ...p) });
}
function apiEntityAttributeAttach(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  if (!body.entity || !body.attribute_key) return bad(res, 'entity and attribute_key required', 400);
  run('INSERT INTO entity_attributes(entity,attribute_key,position) VALUES(?,?,?) ON CONFLICT(entity,attribute_key) DO UPDATE SET position=excluded.position',
    body.entity, body.attribute_key, body.position || 0);
  logAction(s, 'entity_attribute.attach', 'entity_attribute', `${body.entity}:${body.attribute_key}`);
  json(res, 200, { ok: true });
}
/* ---------- contracts / tenders / serialized (B2B + unit serialization) ---------- */
const newRef = pre => pre + "-" + Date.now().toString(36).toUpperCase() + crypto.randomBytes(2).toString("hex").toUpperCase();
function apiAdminContractCreate(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  if (!body.buyer_name || !body.buyer_email) return bad(res, "Buyer name and email required");
  const inc = rl("incoterms"), pt = rl("paymentTerms"), cs = rl("contractStatuses");
  const ref = newRef("CT");
  run("INSERT INTO contracts(tenant_id,ref,buyer_name,buyer_email,buyer_org,supplier_id,product_ids,currency,pricing,min_qty,incoterms,payment_terms,valid_from,valid_to,status,notes) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
    T(s), ref, String(body.buyer_name), String(body.buyer_email), String(body.buyer_org || ""), body.supplier_id ? Number(body.supplier_id) : null,
    JSON.stringify(body.product_ids || []), String(body.currency || require("./defaults.js").currency(T(s))), JSON.stringify(body.pricing || {}), Number(body.min_qty) || 1,
    inc.includes(body.incoterms) ? body.incoterms : "EXW", pt.includes(body.payment_terms) ? body.payment_terms : "net30", body.valid_from || null, body.valid_to || null,
    cs.includes(body.status) ? body.status : "active", String(body.notes || ""));
  const id = Number(get("SELECT id FROM contracts WHERE tenant_id=? AND ref=?", T(s), ref).id);
  logAction(s, "contract.create", "contract", ref);
  json(res, 200, { ok: true, id, ref });
}
function apiAdminContractStatus(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  if (!rl("contractStatuses").includes(body.status)) return bad(res, "Invalid status");
  const r = run("UPDATE contracts SET status=? WHERE id=? AND tenant_id=?", body.status, Number(id), T(s));
  if (!r.changes) return bad(res, "Not found", 404);
  logAction(s, "contract.status", "contract", id, { status: body.status });
  json(res, 200, { ok: true });
}
function apiAdminTenderCreate(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  if (!body.title) return bad(res, "Title required");
  const ref = newRef("TDR");
  run("INSERT INTO tenders(tenant_id,ref,title,buyer_org,buyer_email,description,currency,budget,open_at,close_at,status,items) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
    T(s), ref, String(body.title), String(body.buyer_org || ""), String(body.buyer_email || ""), String(body.description || ""),
    String(body.currency || require("./defaults.js").currency(T(s))), Number(body.budget) || 0, body.open_at || null, body.close_at || null, "open", JSON.stringify(body.items || []));
  const id = Number(get("SELECT id FROM tenders WHERE tenant_id=? AND ref=?", T(s), ref).id);
  logAction(s, "tender.create", "tender", ref);
  json(res, 200, { ok: true, id, ref });
}
function apiAdminTenderAward(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const t = get("SELECT * FROM tenders WHERE id=? AND tenant_id=?", Number(id), T(s));
  if (!t) return bad(res, "Unknown tender", 404);
  const items = J(t.items, []), product_ids = items.map(i => i.product_id).filter(Boolean);
  const ref = newRef("CT");
  const c = run("INSERT INTO contracts(tenant_id,ref,buyer_name,buyer_email,buyer_org,currency,product_ids,pricing,min_qty,valid_from,valid_to,status,notes) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
    T(s), ref, String(t.buyer_org || "Tender Winner"), String(t.buyer_email || ""), String(t.buyer_org || ""), String(t.currency || require("./defaults.js").currency(T(s))),
    JSON.stringify(product_ids), JSON.stringify({}), 1, t.open_at || null, t.close_at || null, "active", "Auto-generated from tender " + t.ref);
  run("UPDATE tenders SET status='awarded', awarded_seller_id=?, awarded_contract_id=? WHERE id=?", body.seller_id ? Number(body.seller_id) : null, Number(c.lastInsertRowid), t.id);
  logAction(s, "tender.award", "tender", t.ref, { contract: ref });
  json(res, 200, { ok: true, contract_ref: ref, contract_id: Number(c.lastInsertRowid) });
}
function apiAdminRfqToContract(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const r = get("SELECT * FROM rfqs WHERE id=? AND tenant_id=?", Number(id), T(s));
  if (!r) return bad(res, "Unknown RFQ", 404);
  const ref = newRef("CT"), price = Number(body.price || r.target_price || 0);
  const c = run("INSERT INTO contracts(tenant_id,ref,buyer_name,buyer_email,currency,product_ids,pricing,min_qty,valid_from,status,notes) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
    T(s), ref, String(r.buyer_name || ""), String(r.buyer_email || ""), String(r.currency || require("./defaults.js").currency(T(s))), JSON.stringify(r.product_id ? [r.product_id] : []),
    JSON.stringify(price && r.product_id ? { fixed: { [r.product_id]: price } } : {}), Number(r.qty) || 1, new Date().toISOString().slice(0, 10), "active", "Converted from " + r.ref);
  run("UPDATE rfqs SET status='accepted' WHERE id=?", r.id);
  logAction(s, "rfq.to_contract", "rfq", r.ref, { contract: ref });
  json(res, 200, { ok: true, contract_ref: ref, contract_id: Number(c.lastInsertRowid) });
}
function apiAdminSerializedBulk(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const t = T(s), pid = String(body.product_id || ""), count = Math.min(500, Math.max(1, Number(body.count) || 1));
  if (!pid) return bad(res, "product_id required");
  const p = get("SELECT * FROM products WHERE tenant_id=? AND id=?", t, pid); if (!p) return bad(res, "Unknown product", 404);
  const skuId = (get("SELECT id FROM skus WHERE tenant_id=? AND product_id=? ORDER BY id LIMIT 1", t, pid) || {}).id || null;
  const whId = (get("SELECT id FROM warehouses WHERE tenant_id=? ORDER BY id LIMIT 1", t) || {}).id || null;
  const prefix = String(body.prefix || p.id + "-SN"); let made = 0;
  for (let i = 0; i < count; i++) { const serial = prefix + "-" + Date.now().toString(36) + "-" + i; try { run("INSERT INTO serialized_items(tenant_id,product_id,sku_id,warehouse_id,serial,status,condition,purchase_date) VALUES(?,?,?,?,?,?,?,?)", t, pid, skuId, whId, serial, "in_stock", "new", new Date().toISOString().slice(0, 10)); made++; } catch (e) { } }
  logAction(s, "serialized.bulk", "serialized", pid, { count: made });
  json(res, 200, { ok: true, created: made });
}

/* ---------- AI product layer (capabilities, run, usage, tasks) ---------- */
function apiAiOverview(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { capabilities: ai.capabilities(T(s)), plan: ai.planInfo(T(s)), usage: ai.usage(T(s)), settings: CFG(s).ai || {} });
}
function apiAiRun(req, res, url, s, body, capability) {
  if (!requireAdmin(s, res)) return;
  if (!requireSection(s, res, "ai", "write")) return;
  const [type, , name] = actor(s);
  const out = ai.run(T(s), capability, body || {}, name || type);
  if (out.error) return bad(res, out.error, out.code || 400);
  let offerDiscount = 0;
  try { const d = offers.discountFor("ai", T(s), out.cost || 0, { owner: ownerFor(s), coupon: s.coupon }); if (d.discount) { offerDiscount = d.discount; out.cost = +Math.max(0, out.cost - d.discount).toFixed(4); } if (d.credits) offers.credit(T(s), ownerFor(s), d.credits, "cashback", "ai:" + capability, "USD", "ai", "ai"); } catch (e) { }
  out.offer_discount = offerDiscount;
  try { if ((out.cost || 0) > 0) billing.recordUsage(T(s), "ai", capability + " · " + out.provider, out.units, (out.cost) / Math.max(1, out.units), { currency: out.currency || require("./defaults.js").platformCurrency(), period: billing.monthOf(), ref: "ai:" + capability }); } catch (e) { }
  logAction(s, "ai.run", "ai_usage", capability, { provider: out.provider, model: out.model, units: out.units, cost: out.cost, tier: out.tier }, req);
  emitEvent(T(s), "ai.usage", { capability, provider: out.provider, units: out.units, cost: out.cost, tier: out.tier }, null);
  json(res, 200, out);
}
function apiAiUsage(req, res, url, s) { if (!requireAdmin(s, res)) return; json(res, 200, ai.usage(T(s))); }
function apiAiTasks(req, res, url, s) { if (!requireAdmin(s, res)) return; json(res, 200, { tasks: ai.tasks(T(s)) }); }
function apiAiTaskCreate(req, res, url, s, body) {
  return (async () => {
  if (!requireAdmin(s, res)) return;
  if (!(ai.capabilities(T(s)).find(c => c.key === body.capability))) return bad(res, "Unknown capability");
  const id = ai.createTask(T(s), body.capability, body.params || {}, (actor(s)[2] || actor(s)[0]));
  let ran = null; if (body.runNow) ran = await queueNow().push({ type: "ai-task", id });
  logAction(s, "ai.task.create", "ai_task", id, { capability: body.capability });
  json(res, 200, { ok: true, id, queued: !!(ran && !ran.ran), tasks: ai.tasks(T(s)) });
  })();
}
function apiAiTaskRun(req, res, url, s, body, id) { return (async () => { if (!requireAdmin(s, res)) return; if (!get("SELECT 1 ok FROM ai_tasks WHERE id=? AND tenant_id=?", Number(id), T(s))) return bad(res, "Unknown task", 404); const r = await queueNow().push({ type: "ai-task", id: Number(id) }); json(res, 200, { result: r.out, tasks: ai.tasks(T(s)) }); })(); }
function apiPlatformAi(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const tenants = all("SELECT id,slug,name FROM tenants");
  const usage = all(`SELECT ai.tenant_id, t.slug, SUM(ai.cost) cost, COUNT(*) calls FROM ai_usage ai JOIN tenants t ON t.id=ai.tenant_id GROUP BY ai.tenant_id, t.slug`);
  json(res, 200, { providers: registry.providerDefs("ai"), capabilities: ai.AI_CAPABILITIES, plans: ai.AI_PLANS, tierByTenant: tenants.map(t => ({ id: t.id, slug: t.slug, name: t.name, ...ai.tierOf(t.id) })), usage });
}

/* ---------- runtime configuration + configurable storage/queue services ---------- */
const _svc = { q: null, s: null };
function queueNow() { if (!_svc.q) _svc.q = adapters.build("queue", rtconfig.get("queue")); return _svc.q; }
function storeNow() { if (!_svc.s) _svc.s = adapters.build("storage", rtconfig.get("storage")); return _svc.s; }
function csvOf(rows, cols) {
  if (!rows.length) return "";
  cols = cols && cols.length ? cols : Object.keys(rows[0]);
  return [cols.join(",")].concat(rows.map(r => cols.map(c => {
    const v = r[c]; const s = v == null ? "" : (typeof v === "object" ? JSON.stringify(v) : String(v));
    return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  }).join(","))).join("\n");
}
function buildExport(tenantId, kind) {
  if (kind === "products") return csvOf(all("SELECT id,title,brand,dept,type,price,list_price,stock,lifecycle FROM products WHERE tenant_id=? ORDER BY id", tenantId));
  if (kind === "orders") return csvOf(all("SELECT num,name,city,status,sub,tax,total,currency,created_at FROM orders WHERE tenant_id=? ORDER BY id DESC", tenantId));
  if (kind === "ai_usage") return csvOf(all("SELECT capability,provider,tier,units,cost,created_at FROM ai_usage WHERE tenant_id=? ORDER BY id DESC", tenantId));
  if (kind === "serialized") return csvOf(all("SELECT product_id,serial,status,batch,lot,expiry,warranty_end FROM serialized_items WHERE tenant_id=? ORDER BY id", tenantId));
  if (kind === "offers") return csvOf(all("SELECT name,code,type,direction,channel,funder,value,used,status FROM offers WHERE tenant_id=? OR tenant_id=0", tenantId));
  return "";
}
/* queue + storage handlers (registered once; the queue driver decides inline vs redis vs hook) */
adapters.registerHandler("ai-task", (job) => ai.processTask(job.id));
adapters.registerHandler("export", async (job) => { const csv = buildExport(job.tenantId, job.kind); const key = `${job.tenantId}-${job.kind}-${Date.now()}.csv`; const r = await storeNow().put(key, csv, "text/csv"); return r; });

function apiAdminExport(req, res, url, s, body, kind) {
  return (async () => {
    if (!requireAdmin(s, res)) return;
    if (!["products", "orders", "ai_usage", "serialized", "offers"].includes(kind)) return bad(res, "Unknown export kind");
    const r = await queueNow().push({ type: "export", tenantId: T(s), kind });
    json(res, 200, { ok: true, mode: r.mode || "inline", result: r.out || null, queued: !r.ran });
  })();
}
function apiPlatformRuntime(req, res, url, s) {
  if (!requirePlatformSection(s, res, "runtime", "read")) return;
  const rt = rtconfig.runtime();
  const active = { cache: adapters.build("cache", rt.cache).kind, ratelimit: adapters.build("ratelimit", rt.ratelimit).kind, storage: storeNow().kind, queue: queueNow().kind };
  json(res, 200, { runtime: rtconfig.redactRuntime(rt), catalog: rtconfig.describe(), active, offline: outboundOffline() });
}
function apiPlatformRuntimePut(req, res, url, s, body) {
  if (!requirePlatformSection(s, res, "runtime", "write")) return;
  try { rtconfig.saveRuntime(body || {}); } catch (e) { return bad(res, e.message); }
  _svc.q = null; _svc.s = null; /* rebuild adapters on next use with the new drivers */
  logAction(s, "platform.runtime", "runtime", "update", { changed: Object.keys(body || {}).join(",") }, req);
  json(res, 200, { ok: true, runtime: rtconfig.redactRuntime(rtconfig.runtime()) });
}
function apiPlatformRuntimeTest(req, res, url, s, body) {
  return (async () => {
    if (!requirePlatform(s, res)) return;
    const concern = String(body && body.concern || "");
    const cfg = rtconfig.get(concern) || {};
    try {
      if (concern === "db") { if (cfg.driver !== "postgres") return json(res, 200, { concern, kind: cfg.driver, ok: true, note: "sqlite is in-process" }); return json(res, 200, Object.assign({ concern }, await adapters.build("db", cfg).ping())); }
      if (cfg.driver === "redis") { const r = await adapters.redis((cfg.params || {}).url).call(["PING"]); return json(res, 200, { concern, kind: "redis", ok: !(r && r.__error), reply: r }); }
      if (cfg.driver === "webhook") { return json(res, 200, { concern, kind: "webhook", ok: !!(cfg.params && cfg.params.url) }); }
      return json(res, 200, { concern, kind: cfg.driver, ok: true, note: "in-process driver, no remote to test" });
    } catch (e) { return json(res, 200, { concern, ok: false, error: e.message }); }
  })();
}
function apiPlatformQueueDrain(req, res, url, s, body) {
  return (async () => {
    if (!requirePlatform(s, res)) return;
    const r = await queueNow().drain(Math.min(200, Number(body && body.batch) || 50));
    /* also flush any persisted AI tasks in-process (works for inline or redis backends) */
    let done = 0; for (const t of all("SELECT id FROM tenants")) { const ts = ai.tasks(t.id).filter(x => x.status === "queued"); for (const x of ts) { ai.processTask(x.id); done++; } }
    json(res, 200, { ok: true, queue: r, aiTasksProcessed: done });
  })();
}

/* ---------- environments + feature flags (unlimited named envs, all data) ---------- */
function resetRuntimeSvc() { _svc.q = null; _svc.s = null; }
function apiEnvList(req, res, url, s) { if (!requirePlatform(s, res)) return; const e = env.list(); json(res, 200, { environments: e, active: (e.find(x => x.active) || {}).name || null }); }
function apiEnvGet(req, res, url, s, body, name) { if (!requirePlatform(s, res)) return; const e = env.get(String(name || "")); if (!e) return bad(res, "Unknown environment", 404); json(res, 200, { environment: e }); }
function apiEnvUpsert(req, res, url, s, body, name) { if (!requirePlatform(s, res)) return; try { const e = env.upsert(name || body.name, body); logAction(s, "environment.save", "environment", name || body.name, { concerns: Object.keys(body.runtime || {}).join(",") }, req); json(res, 200, { ok: true, environment: e }); } catch (e) { return bad(res, e.message); } }
function apiEnvDelete(req, res, url, s, body, name) { if (!requirePlatform(s, res)) return; env.remove(String(name || "")); logAction(s, "environment.delete", "environment", name); json(res, 200, { ok: true }); }
function apiEnvActivate(req, res, url, s, body, name) {
  return (async () => {
    if (!requirePlatform(s, res)) return;
    try { const r = env.activate(String(name || "")); resetRuntimeSvc(); logAction(s, "environment.activate", "environment", r.active, {}, req); json(res, 200, r); } catch (e) { return bad(res, e.message); }
  })();
}
function apiEnvExport(req, res, url, s) { if (!requirePlatformSection(s, res, "runtime", "read")) return; json(res, 200, { bundle: env.exportAll() }); }
function apiEnvImport(req, res, url, s, body) { if (!requirePlatformSection(s, res, "runtime", "write")) return; try { const r = env.importAll(body && body.bundle, { activate: !!(body && body.activate) }); if (body && body.activate) resetRuntimeSvc(); logAction(s, "environment.import", "environment", null, { imported: r.imported }, req); json(res, 200, r); } catch (e) { return bad(res, e.message); } }
function apiFlags(req, res, url, s) { if (!requirePlatform(s, res)) return; json(res, 200, { flags: env.flags() }); }
function apiFlagSet(req, res, url, s, body, name) { if (!requirePlatform(s, res)) return; try { json(res, 200, { ok: true, flag: env.setFlag(name || body.name, body) }); } catch (e) { return bad(res, e.message); } }
function apiFlagDelete(req, res, url, s, body, name) { if (!requirePlatform(s, res)) return; env.delFlag(String(name || "")); json(res, 200, { ok: true }); }
function apiEnvTenant(req, res, url, s) { if (!requireAdmin(s, res)) return; json(res, 200, env.resolveFlags(T(s))); }

/* ---------- central offers / coupons / wallet ledger ---------- */
function mapOffer(r) { return { ...r, scope: J(r.scope_value, {}), rules: J(r.rules, {}) }; }
function apiOffersList(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const allowGlobal = sec.policy().provisioning.globalOffersAllowed !== false;
  const rows = all(`SELECT * FROM offers WHERE tenant_id=? ${allowGlobal ? "OR tenant_id=0" : ""} ORDER BY priority DESC, id DESC`, T(s)).map(mapOffer);
  json(res, 200, { offers: rows, active: rows.filter(o => stIs("offer", o.status, "live") && (!o.starts || o.starts <= new Date().toISOString().slice(0, 10)) && (!o.ends || o.ends >= new Date().toISOString().slice(0, 10))) });
}
function apiOfferSave(req, res, url, s, body, id) {
  if (!requireStaff(s, res, "goffers")) return;
  /* every write to the value-exchange record goes through GOIP — this endpoint is the legacy shape */
  const r = goip.createExchange(T(s), Object.assign({}, body, { id: id ? Number(id) : undefined }), { platform: !!s.platform_admin, actor: actor(s)[2], id: id ? Number(id) : null });
  if (r.error) return bad(res, r.error, r.code || 400);
  logAction(s, "offer.save", "offer", id || body.name, { type: body.type, benefit: r.benefit, domain: r.domain, channel: body.channel, funder: body.funder, global: r.global }, req);
  json(res, 200, { ok: true, id: r.id, uid: r.uid, domain: r.domain, benefit: r.benefit });
}
function apiOfferDelete(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const o = get("SELECT id,tenant_id FROM offers WHERE id=?", Number(id)); if (!o) return bad(res, "Not found", 404);
  if (o.tenant_id !== T(s) && !(s.platform_admin && o.tenant_id === 0)) return bad(res, "Not permitted", 403);
  run("UPDATE offers SET status='inactive' WHERE id=?", Number(id)); logAction(s, "offer.retire", "offer", id); json(res, 200, { ok: true });
}
function apiOffersPreview(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const res2 = offers.evaluate({ channel: body.channel || require("./defaults.js").of("offerChannels"), tenantId: T(s), items: body.items || [], amount: body.amount, coupon: body.coupon, owner: body.owner || (s.user_id ? ownerFor(s) : null), currency: body.currency || commerceOf(s).currency, allowGlobal: true });
  json(res, 200, res2);
}
function apiCouponsList(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { coupons: all("SELECT * FROM coupons WHERE tenant_id=? OR tenant_id=0 ORDER BY id DESC", T(s)), redemptions: all("SELECT * FROM coupon_redemptions WHERE tenant_id=? ORDER BY id DESC LIMIT 200", T(s)) });
}
function apiCouponCreate(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const r = goip.issue(T(s), Object.assign({}, body, { count: 1 }));
  if (r.error) return bad(res, r.error, r.code || 400);
  logAction(s, "coupon.create", "coupon", r.code, { kind: body.kind, funder: body.funder }, req);
  json(res, 200, { ok: true, code: r.code, id: Number((get("SELECT id FROM coupons WHERE tenant_id=? AND code=?", T(s), r.code) || {}).id || 0) });
}
function apiCouponGenerate(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const r = goip.issue(T(s), Object.assign({}, body, { count: Math.min(1000, Math.max(1, Number(body.count) || 1)), prefix: body.prefix || "CPN" }));
  if (r.error) return bad(res, r.error, r.code || 400);
  logAction(s, "coupon.generate", "coupon", r.batch, { count: r.count }, req);
  json(res, 200, { ok: true, batch: r.batch, count: r.count, codes: r.codes });
}
function apiCouponVoid(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const r = run("UPDATE coupons SET status='revoked' WHERE id=? AND tenant_id=?", Number(id), T(s)); if (!r.changes) return bad(res, "Not found", 404);
  logAction(s, "coupon.void", "coupon", id); json(res, 200, { ok: true });
}
function apiWalletLedger(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const owner = String(url.searchParams.get("owner") || (s.user_id ? ownerFor(s) : ""));
  json(res, 200, { owner, entries: offers.ledger(T(s), owner), balance: mods.walletBalance(T(s), owner) });
}
function apiPlatformOffers(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const global = all("SELECT * FROM offers WHERE tenant_id=0 ORDER BY id DESC").map(mapOffer);
  const period = new Date().toISOString().slice(0, 7);
  json(res, 200, {
    global, stats: offers.stats(), redemptions: all("SELECT * FROM coupon_redemptions WHERE 1=1 ORDER BY id DESC LIMIT 200"),
    manifest: goip.manifest(0), coverage: goip.coverage(),
    settlements: all("SELECT * FROM goip_settlements ORDER BY id DESC LIMIT 100").map(r => ({ ...r, meta: J(r.meta, {}) })),
    budgets: goip.budgets(0, {}), treasury: goip.treasury(0), period,
    domains: all(`SELECT COALESCE(NULLIF(domain,''),'incentive') domain, COUNT(*) n FROM offers GROUP BY 1 ORDER BY n DESC`),
    benefits: all(`SELECT COALESCE(NULLIF(benefit,''),type) benefit, COUNT(*) n FROM offers GROUP BY 1 ORDER BY n DESC`),
    meters: all("SELECT kind, SUM(qty) qty, SUM(amount) amount FROM usage_records WHERE kind LIKE 'goip.%' GROUP BY kind ORDER BY amount DESC"),
    installs: all("SELECT tm.tenant_id, t.slug, tm.status FROM tenant_modules tm JOIN tenants t ON t.id=tm.tenant_id WHERE tm.module_id='goip'")
  });
}

/* ---------- GOIP Ω∞ · GLOBAL OFFER INFRASTRUCTURE PLATFORM ----------
   ONE universal entry point (POST /api/goip/:capability) plus read surfaces. Consumers speak
   capabilities — create/discover/validate/apply/redeem/settle/fund/pay/govern/audit… — and never
   learn the words coupon, cashback, reward or gift card. Access follows each capability's declared
   scope: "any" (a shopper session), "tenant" (store admin) or "platform" (super admin). */
function goipOwner(s) { return s.user_id ? ownerFor(s) : ("t" + T(s) + ":s:" + s.sid); }
function apiGoipManifest(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  json(res, 200, goip.manifest(T(s)));
}
function apiGoipRegistry(req, res, url, s, body, name) {
  if (!requireStaff(s, res)) return;
  const key = String(name || "");
  if (!Object.prototype.hasOwnProperty.call(goip.REGISTRIES, key)) return bad(res, "Unknown GOIP registry: " + key, 404);
  json(res, 200, { registry: key, items: rl(key) && (Array.isArray(rl(key)) ? rl(key).length : Object.keys(rl(key)).length) ? rl(key) : goip.REGISTRIES[key] });
}
function apiGoipCapability(req, res, url, s, body, capKey) {
  const cap = goip.capability(capKey);
  if (!cap) return bad(res, "Unknown capability: " + capKey, 404);
  if (cap.scope === "platform") { if (!requirePlatform(s, res)) return; }
  else if (cap.scope === "tenant") { if (!requireStaff(s, res, "goip")) return; }
  const input = Object.assign({}, body || {});
  /* a shopper may only ever act as themselves; admins may name any subject */
  if (!s.platform_admin && !isAdmin(s)) { input.owner = goipOwner(s); delete input.tenant_id; delete input.scope_level; }
  else if (input.owner === undefined && ["discover", "compare", "validate", "apply", "recommend"].includes(cap.key) && s.user_id) input.owner = ownerFor(s);
  if (input.currency === undefined) input.currency = commerceOf(s).currency;
  /* a platform admin may aim a capability at any store; a store admin is pinned to their own */
  const tid = (s.platform_admin && input.tenant_id != null) ? Number(input.tenant_id) : T(s);
  const out = goip.invoke(cap.key, tid, input, { platform: !!s.platform_admin, actor: actor(s)[2] || "system" });
  if (out && out.ok === false) return bad(res, out.error || "Capability failed", out.code || 400);
  if (cap.writes) logAction(s, "goip." + cap.key, "goip", (out.result && (out.result.id || out.result.batch || out.result.reference)) || cap.key, { stage: cap.stage, engine: cap.engine }, req);
  json(res, 200, out);
}
function apiGoipExchanges(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  const f = { domain: url.searchParams.get("domain") || "", benefit: url.searchParams.get("benefit") || "", channel: url.searchParams.get("channel") || "", status: url.searchParams.get("status") || "", campaign: url.searchParams.get("campaign") || "", q: url.searchParams.get("q") || "", global: url.searchParams.get("global") === "1", limit: Number(url.searchParams.get("limit")) || 200 };
  json(res, 200, { exchanges: goip.listExchanges(T(s), f) });
}
function apiGoipExchange(req, res, url, s, body, id) {
  if (!requireStaff(s, res)) return;
  const x = goip.exchange(T(s), id); if (!x) return bad(res, "Not found", 404);
  json(res, 200, { exchange: x, audit: goip.auditTrail(T(s), x.id) });
}
function apiGoipContext(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  json(res, 200, goip.resolveContext({ tenantId: T(s), owner: s.user_id ? ownerFor(s) : null, amount: Number(url.searchParams.get("amount")) || 0, currency: commerceOf(s).currency, spatial: { node: url.searchParams.get("place") || "" }, calendar: url.searchParams.get("calendar") || "" }));
}
function apiGoipTreasury(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  json(res, 200, { treasury: goip.treasury(T(s)), budgets: goip.budgets(T(s), {}), forecast: goip.forecast(T(s), { months: 3 }) });
}
function apiGoipSettlements(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  json(res, 200, { settlements: goip.settlements(T(s), { period: url.searchParams.get("period") || "", status: url.searchParams.get("status") || "" }) });
}
function apiGoipEntitlements(req, res, url, s) {
  const owner = String(url.searchParams.get("owner") || "");
  if (!isAdmin(s) && !s.platform_admin) { if (!s.user_id) return bad(res, "Sign in required", 403); return json(res, 200, { owner: ownerFor(s), entitlements: goip.entitlementsOf(T(s), ownerFor(s)) }); }
  json(res, 200, { owner, entitlements: goip.entitlementsOf(T(s), owner || (s.user_id ? ownerFor(s) : "")) });
}
function apiGoipTouchpoints(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  json(res, 200, { touchpoints: goip.touchpoints(T(s), { owner: url.searchParams.get("owner") || "", party: url.searchParams.get("party") || "" }) });
}
function apiGoipIntelligence(req, res, url, s, body, key) {
  if (!requireStaff(s, res)) return;
  const out = goip.intel(T(s), key, { objective: url.searchParams.get("objective") || "" });
  if (out && out.error) return bad(res, out.error, 404);
  json(res, 200, { intelligence: key, result: out });
}
function apiGoipFeed(req, res, url, s, body, channel) {
  const out = goip.feed(T(s), channel, { currency: commerceOf(s).currency });
  if (out.error) return bad(res, out.error, out.code || 404);
  json(res, 200, out);
}
function apiGoipWidget(req, res, url, s) {
  const out = goip.widget(T(s), { distribution: url.searchParams.get("channel") || "widget", channel: url.searchParams.get("exchange_channel") || require("./defaults.js").of("offerChannels"), currency: commerceOf(s).currency });
  if (out.error) return bad(res, out.error, out.code || 404);
  if (url.searchParams.get("embed") === "1") { res.writeHead(200, { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" }); return res.end(out.html); }
  json(res, 200, out);
}

/* ---------- webhooks (outbound events) + universal entity metadata (tags/notes via global uid) ---------- */
function apiWebhooksList(req, res, url, s) { if (!requireAdmin(s, res)) return; json(res, 200, Object.assign({ events: events.webhookEvents() }, events.list(T(s)))); }
function apiWebhookCreate(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const urlErr = events.validateUrl(body.url);
  if (urlErr) return bad(res, urlErr, 400);
  const id = events.create(T(s), body); logAction(s, "webhook.create", "webhook", id, { url: body.url, events: body.events }, req);
  json(res, 200, { ok: true, id });
}
function apiWebhookUpdate(req, res, url, s, body, id) { if (!requireAdmin(s, res)) return; if (body && body.url != null) { const urlErr = events.validateUrl(body.url); if (urlErr) return bad(res, urlErr, 400); } if (!events.update(Number(id), T(s), body)) return bad(res, "Not found", 404); logAction(s, "webhook.update", "webhook", id, {}, req); json(res, 200, { ok: true }); }
function apiWebhookDelete(req, res, url, s, body, id) { if (!requireAdmin(s, res)) return; if (!events.remove(Number(id), T(s))) return bad(res, "Not found", 404); logAction(s, "webhook.delete", "webhook", id); json(res, 200, { ok: true }); }
function apiWebhookTest(req, res, url, s, body, id) {
  return (async () => {
    if (!requireAdmin(s, res)) return;
    /* the test delivers ONE fixed event to THIS webhook only — it used to fan a caller-named,
       signed event out to every subscriber and create a new wildcard webhook on each call */
    const w = get("SELECT id FROM webhooks WHERE id=? AND tenant_id=?", Number(id), T(s));
    if (!w) return bad(res, "Unknown webhook", 404);
    const d = run("INSERT INTO webhook_deliveries(tenant_id,webhook_id,event,subject_uid,payload,status,attempts,created_at) VALUES(?,?,?,?,?,'pending',0,datetime('now'))",
      T(s), w.id, "store.test", null, JSON.stringify({ event: "store.test", data: { message: "LUXORA webhook test", at: new Date().toISOString() } }));
    const resu = await events.deliver(Number(d.lastInsertRowid));
    json(res, 200, { ok: true, delivery: Number(d.lastInsertRowid), result: resu });
  })();
}
function apiWebhookDrain(req, res, url, s, body) { return (async () => { if (!requireAdmin(s, res)) return; json(res, 200, await events.drain(T(s), Number(body && body.batch) || 25)); })(); }
function apiEntityTags(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const entity = String(url.searchParams.get("entity") || ""), uid = String(url.searchParams.get("uid") || "");
  const row = get("SELECT tags, meta, notes FROM entity_meta WHERE tenant_id=? AND entity=? AND ref_uid=?", T(s), entity, uid);
  json(res, 200, { entity, uid, tags: row ? J(row.tags, []) : [], meta: row ? J(row.meta, {}) : {}, notes: row ? row.notes : "" });
}
function apiEntityTagsSave(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const entity = String(body.entity || ""), uid = String(body.uid || ""); if (!entity || !uid) return bad(res, "entity and uid required");
  run(`INSERT INTO entity_meta(tenant_id,entity,ref_uid,tags,meta,notes,updated_at) VALUES(?,?,?,?,?,?,datetime('now'))
       ON CONFLICT(tenant_id,entity,ref_uid) DO UPDATE SET tags=excluded.tags, meta=excluded.meta, notes=excluded.notes, updated_at=datetime('now')`,
    T(s), entity, uid, JSON.stringify(body.tags || []), JSON.stringify(body.meta || {}), String(body.notes || ""));
  logAction(s, "entity_meta.save", entity, uid); json(res, 200, { ok: true });
}

/* ---------- team & roles (RBAC) ---------- */
/* the store console reads ITS OWN role set (rbac.roles(tenant)) — a store that forked
   the platform default edits what it forked, and a store that never forked reads the
   inherited default through the same call. hasOwnSet tells the console which it is
   looking at, so the "reset to platform default" control only appears when there is a
   fork to undo. */
function apiRoles(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { roles: rbac.roles(T(s)), defaultRole: require("./defaults.js").of("staffRoles"), sections: storeSections(T(s)), apps: authz.appsFor(T(s)).map(appInfo), ownSet: rbac.hasOwnSet(T(s)),
    me: { user: _userRow(s), allowed: rbac.allowedSections(_userRow(s), T(s)) } });
}
/* a store defines and re-scopes its OWN roles from its own console — the per-tenant
   fork. The first save forks the full inherited set (the store keeps every role it had
   and diverges from there), and a fork can be dissolved back to the platform default.
   Gated on team:write: scoping who on this team may do what is the team trust. */
function apiRoleSave(req, res, url, s, body) {
  if (!requireSection(s, res, "team", "write")) return;
  const r = rbac.upsertRole(T(s), body || {});
  if (!r.ok) return bad(res, (r.fails || []).join("; "), 400);
  logAction(s, "staff.role.save", "role", r.role.key, { name: r.role.name }, req);
  json(res, 200, { ok: true, role: r.role, roles: rbac.roles(T(s)), ownSet: true });
}
function apiRoleDelete(req, res, url, s, body, key) {
  if (!requireSection(s, res, "team", "write")) return;
  const r = rbac.deleteRole(T(s), key);
  if (!r.ok) return bad(res, (r.fails || []).join("; "), 400);
  logAction(s, "staff.role.delete", "role", key, {}, req);
  json(res, 200, { ok: true, roles: rbac.roles(T(s)) });
}
/* dissolve this store's fork back to the shared platform default */
function apiRoleReset(req, res, url, s) {
  if (!requireSection(s, res, "team", "write")) return;
  const r = rbac.resetToDefault(T(s));
  if (!r.ok) return bad(res, (r.fails || []).join("; "), 400);
  logAction(s, "staff.role.reset", "roles", T(s), {}, req);
  json(res, 200, { ok: true, roles: rbac.roles(T(s)), ownSet: false });
}
function apiStaffList(req, res, url, s) {
  if (!requireAdmin(s, res)) return; if (!requireSection(s, res, "team", "read")) return;
  json(res, 200, { staff: all("SELECT id,name,email,role,staff_role,disabled,last_login,created_at FROM users WHERE tenant_id=? AND role='admin' ORDER BY id", T(s)) });
}
function apiStaffCreate(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return; if (!requireSection(s, res, "team", "write")) return;
  const email = String(body.email || "").toLowerCase().trim(); if (!email || !body.name) return bad(res, "name and email required");
  if (rbac.role(T(s), body.staff_role || require("./defaults.js").of("staffRoles")) === null) return bad(res, "Unknown role");
  const existing = get("SELECT id FROM users WHERE tenant_id=? AND email=?", T(s), email);
  const pw = String(body.password || crypto.randomBytes(9).toString("hex"));
  let id;
  if (existing) { run("UPDATE users SET name=?, role='admin', staff_role=?, disabled=0 WHERE id=? AND tenant_id=?", String(body.name), body.staff_role || require("./defaults.js").of("staffRoles"), existing.id, T(s)); id = existing.id; }
  else id = newUser(T(s), String(body.name), email, pw, "admin");
  run("UPDATE users SET staff_role=? WHERE id=?", body.staff_role || require("./defaults.js").of("staffRoles"), id);
  run("UPDATE users SET perms=? WHERE id=?", JSON.stringify(body.perms || {}), id);
  logAction(s, "staff.create", "user", id, { email, role: body.staff_role || require("./defaults.js").of("staffRoles") }, req);
  json(res, 200, { ok: true, id, generated: !existing && !body.password ? pw : undefined });
}
function apiStaffUpdate(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return; if (!requireSection(s, res, "team", "write")) return;
  const u = get("SELECT id FROM users WHERE id=? AND tenant_id=? AND role='admin'", Number(id), T(s)); if (!u) return bad(res, "Not found", 404);
  if (Number(id) === Number(s.user_id) && body.disabled) return bad(res, "You cannot disable your own account");
  /* no self-promotion, and only an owner assigns or edits the owner role */
  if (Number(id) === Number(s.user_id) && (body.staff_role != null || body.perms != null)) return bad(res, "You cannot change your own role or permissions", 403);
  const me = get("SELECT staff_role FROM users WHERE id=?", s.user_id) || {};
  const target = get("SELECT staff_role FROM users WHERE id=?", u.id) || {};
  if ((me.staff_role || "owner") !== "owner" && (body.staff_role === "owner" || (target.staff_role || "owner") === "owner" || body.perms != null))
    return bad(res, "Only an owner can grant the owner role or custom permissions", 403);
  if (body.staff_role != null) { if (!rbac.role(T(s), body.staff_role)) return bad(res, "Unknown role"); run("UPDATE users SET staff_role=? WHERE id=?", body.staff_role, u.id); }
  if (body.perms != null) run("UPDATE users SET perms=? WHERE id=?", JSON.stringify(body.perms), u.id);
  if (body.disabled != null) run("UPDATE users SET disabled=? WHERE id=?", body.disabled ? 1 : 0, u.id);
  if (body.disabled) run("UPDATE sessions SET user_id=NULL WHERE user_id=?", u.id);
  logAction(s, "staff.update", "user", id, { role: body.staff_role, disabled: body.disabled }, req);
  json(res, 200, { ok: true });
}
function apiStaffDelete(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return; if (!requireSection(s, res, "team", "write")) return;
  if (Number(id) === Number(s.user_id)) return bad(res, "Cannot remove yourself");
  const admins = get("SELECT COUNT(*) c FROM users WHERE tenant_id=? AND role='admin' AND disabled=0", T(s)).c;
  if (admins <= 1) return bad(res, "A store must keep at least one active admin");
  run("UPDATE users SET disabled=1 WHERE id=? AND tenant_id=? AND role='admin'", Number(id), T(s));
  /* removal takes effect now, not when the removed person's session expires */
  run("UPDATE sessions SET user_id=NULL WHERE user_id=?", Number(id));
  logAction(s, "staff.disable", "user", id, {}, req); json(res, 200, { ok: true });
}

/* ---------- B (async dual-engine) observability ---------- */
function apiPlatformDb(req, res, url, s) {
  return (async () => {
    if (!requirePlatform(s, res)) return;
    let health = { driver: "sqlite", ok: true }; try { health = await dbpool.ping(); } catch (e) { health = { driver: dbpool.driver(), ok: false, error: e.message }; }
    let plan = null; try { plan = migrate.summary(migrate.plan()); } catch (e) { plan = { error: e.message }; }
    json(res, 200, { driver: dbpool.driver(), health, plan });
  })();
}

/* ---------- enterprise ops (DB cutover · SSO/SCIM · regions/CDN · observability · feeds/transfers/tax) ---------- */
function apiDbStatus(req, res, url, s) { if (!requirePlatform(s, res)) return; json(res, 200, enterprise.dbStatus()); }
function apiDbPing(req, res, url, s) { return (async () => { if (!requirePlatform(s, res)) return; json(res, 200, await enterprise.dbPing()); })(); }
function apiDbApply(req, res, url, s, body) { return (async () => { if (!requirePlatformSection(s, res, "runtime", "write")) return; try { json(res, 200, await enterprise.dbApply(!!(body && body.dryRun))); } catch (e) { return bad(res, e.message); } })(); }
function apiDbSwitch(req, res, url, s, body) { if (!requirePlatformSection(s, res, "runtime", "write")) return; const r = enterprise.dbSwitch(body && body.driver, body && body.mode); if (r.error) return bad(res, r.error); logAction(s, "db.switch", "runtime", null, { driver: body && body.driver, mode: body && body.mode }, req); json(res, 200, r); }
function apiGatewayPreview(req, res, url, s, body, id) { if (!requireAdmin(s, res)) return; json(res, 200, enterprise.gatewayPreview(String(id || ""), T(s))); }
/* the signature is checked over the RAW request bytes (server.js keeps them on req.rawBody)
   — re-serializing the parsed JSON changes whitespace/key order and can never match what
   the provider signed. A bad signature is a 401, so the sender sees the failure. */
/* A payment provider's webhook. The store's own gateway signing secret (Console → Payments,
   "Webhook signing secret") is tried first and confines the event to that store's payments;
   the platform's inbound secret is the fallback for a platform-operated account. How the
   signature is checked is the provider spec's `webhook.signature` (an HMAC over the body or
   URL + body, or the provider's own verify call); a spec that declares none uses the
   platform's scheme (`sha256=` / Stripe's `t=,v1=`). Only a verified event moves money
   state, and replays are no-ops. */
async function apiInboundWebhook(req, res, url, s, body, provider) {
  const raw = typeof req.rawBody === "string" ? req.rawBody : JSON.stringify(body || {});
  const pid = String(provider || "");
  const specDef = connect.specFor(pid, "payment");
  const sigDef = specDef && specDef.webhook && specDef.webhook.signature || null;
  const headers = {}; for (const [k, v] of Object.entries(req.headers || {})) headers[k.toLowerCase()] = Array.isArray(v) ? v[0] : v;
  const sig = sigDef && sigDef.header ? headers[String(sigDef.header).toLowerCase()] || "" : (headers["x-lux-signature"] || headers["stripe-signature"] || "");
  let evt = null; try { evt = JSON.parse(raw); } catch (e) { }
  const hookUrl = cfg => (cfg && cfg.webhookUrl) || ((headers["x-forwarded-proto"] || (req.socket && req.socket.encrypted ? "https" : "http")) + "://" + (headers["x-forwarded-host"] || headers.host || "") + req.url);
  const verify = async (secret, cfg) => {
    if (sigDef && sigDef.api) {
      if (!cfg || outboundOffline() || !evt) return false;
      try { return await require("./spec.js").verifyByApi(sigDef, { config: cfg, extra: { headers, event: evt } }, connect.request); } catch (e) { return false; }
    }
    const h = require("./spec.js").verifyHmac(sigDef, secret, raw, headers, hookUrl(cfg));
    return h === null ? (secret ? enterprise.verifyInbound(secret, raw, sig) : false) : h;
  };
  let scope = null;
  const storeCfg = s && s.tenant ? gatewaySecrets(T(s), pid) : null;
  if (storeCfg && storeCfg.cfg && (storeCfg.cfg.webhookSecret || (sigDef && sigDef.api)) && await verify(storeCfg.cfg.webhookSecret, storeCfg.cfg)) scope = T(s);
  let r;
  if (scope) r = { ok: true, signatureOk: true, scope: "store" };
  else { r = enterprise.inboundWebhook(pid, raw, sig, sigDef && !sigDef.api ? (secret => require("./spec.js").verifyHmac(sigDef, secret, raw, headers, hookUrl(null))) : null); if (r.ok) scope = "platform"; }
  if (!r.ok) return json(res, 401, r);
  const e = evt ? require("./spec.js").webhookEvent(specDef, evt) : null;
  r.applied = !evt ? { ok: false, reason: "unparseable" } : (!e || !e.ref) ? { ok: true, ignored: true } : await applyGatewayEvent(scope === "platform" ? null : scope, pid, e, "webhook");
  json(res, 200, r);
}
/* the payment a provider reference names: within one store when the store's own secret
   verified the event, across stores for the platform's account */
function paymentByRef(tenantId, provider, ref) {
  return tenantId ? get("SELECT * FROM payments WHERE gateway=? AND txn_ref=? AND tenant_id=?", provider, String(ref), tenantId)
    : get("SELECT * FROM payments WHERE gateway=? AND txn_ref=?", provider, String(ref));
}
async function applyGatewayEvent(tenantId, provider, e, source) {
  const p = paymentByRef(tenantId, provider, e.ref);
  if (!p) return { ok: true, ignored: true, reason: "unknown payment" };
  /* approved but not captured (an order-then-capture gateway): ask the provider, which
     captures it, and apply what it then reports */
  if (stIs("payment", e.status, "authorized")) return reconcilePayment(p, source);
  return applyPaymentStatus(p, e, provider, source);
}
/* move one pending payment to what its provider (or the merchant, for money taken offline)
   says: captured releases the order to fulfilment, failed cancels it and gives back what
   checkout took. Each transition is claimed atomically, so a webhook racing a sweep is
   applied once. */
function applyPaymentStatus(p, e, provider, source) {
  if (!stIs("payment", p.status, "awaiting")) return { ok: true, unchanged: true, status: p.status };
  const ord = p.order_id ? get("SELECT * FROM orders WHERE id=? AND tenant_id=?", p.order_id, p.tenant_id) : null;
  const spec = require("./spec.js");
  const aw = stIn("payment", "awaiting");
  if (stIs("payment", e.status, "settled")) {
    if (e.amount != null && e.amount !== "") {
      const got = e.amountUnit === "major" ? spec.minorUnits(Number(e.amount), p.currency) : Number(e.amount);
      if (got !== spec.minorUnits(p.amount, p.currency)) {
        audit(p.tenant_id, "system", null, "gateway", "payment.amount_mismatch", "payment", p.id, { expected: p.amount, got: e.amount, provider, source });
        return { ok: false, reason: "amount mismatch" };
      }
    }
    const upd = run("UPDATE payments SET status=?, provider_payment_id=COALESCE(?, provider_payment_id) WHERE id=? AND status IN " + aw.sql, e.status, e.paymentId || null, p.id, ...aw.args);
    if (!upd.changes) return { ok: true, unchanged: true };
    if (ord && stIs("order", ord.status, "awaiting_payment")) run("UPDATE orders SET status=? WHERE id=?", states.first("order", "accepted"), ord.id);
    audit(p.tenant_id, "system", null, "gateway", "payment.captured", "payment", p.id, { provider, ref: p.txn_ref, source });
    if (ord) { emitEvent(p.tenant_id, "order.paid", { num: ord.num, total: ord.total, txn_ref: p.txn_ref, gateway: provider }, ord.num); notify(p.tenant_id, `Payment received for ${ord.num}`, `${ord.total} ${ord.currency || ""} via ${provider}`); }
    return { ok: true, status: e.status };
  }
  if (stIs("payment", e.status, "failure")) {
    const upd = run("UPDATE payments SET status=? WHERE id=? AND status IN " + aw.sql, e.status, p.id, ...aw.args);
    if (!upd.changes) return { ok: true, unchanged: true };
    /* an abandoned or failed hosted payment releases what checkout took: the order is
       cancelled, store credit spent on it goes back, offer redemptions are reversed */
    if (ord && stIs("order", ord.status, "awaiting_payment")) {
      run("UPDATE orders SET status=? WHERE id=?", states.first("order", "aborted"), ord.id);
      if (ord.gift_used > 0) { try { mods.walletAdd(p.tenant_id, ord.owner, Number(ord.gift_used)); } catch (x) { } }
      try { offers.reverseRedemption(p.tenant_id, { order_id: ord.id, order_num: ord.num }); } catch (x) { }
    }
    audit(p.tenant_id, "system", null, "gateway", "payment.failed", "payment", p.id, { provider, ref: p.txn_ref, event: e.type, source });
    return { ok: true, status: e.status };
  }
  return { ok: true, unchanged: true, status: p.status };
}
/* ask the provider where a live pending payment stands (its spec's `lookup`) and apply it */
async function reconcilePayment(p, source) {
  if (!p.live) return { ok: false, reason: "not a gateway payment" };
  if (!stIs("payment", p.status, "awaiting")) return { ok: true, unchanged: true, status: p.status };
  const g = gatewaySecrets(p.tenant_id, p.gateway);
  if (!g || !g.cfg) return { ok: false, reason: "the store has no credentials for " + p.gateway };
  const r = await connect.lookup({ provider: p.gateway, config: g.cfg, ref: p.txn_ref, idempotency: "capture-" + p.id });
  if (!r.live) return { ok: false, reason: r.reason || "offline" };
  if (!r.ok) return { ok: false, reason: r.error || "the gateway refused the lookup" };
  const fresh = get("SELECT * FROM payments WHERE id=?", p.id);
  return Object.assign(applyPaymentStatus(fresh, { status: r.status, paymentId: r.paymentId, amount: r.amount, amountUnit: r.amountUnit }, p.gateway, source || "lookup"), { provider_status: r.status, captured_now: !!r.captureRan });
}
/* the safety net under webhooks: live payments still pending are looked up on a cadence
   (platform policy paymentReconcileMinutes; 0 = off). A webhook that never arrived — a
   misconfigured endpoint, an outage — still settles the order. */
let reconcileRunning = false;
async function reconcilePending(limit) {
  if (reconcileRunning || outboundOffline()) return { ran: 0 };
  reconcileRunning = true;
  try {
    const aw = stIn("payment", "awaiting");
    const rows = all("SELECT * FROM payments WHERE live=1 AND status IN " + aw.sql + " AND created_at >= datetime('now','-7 days') ORDER BY id LIMIT ?", ...aw.args, Number(limit) || 50);
    const out = [];
    for (const p of rows) { try { out.push({ id: p.id, ...(await reconcilePayment(p, "sweep")) }); } catch (e) { out.push({ id: p.id, ok: false, reason: e.message }); } }
    return { ran: rows.length, results: out };
  } finally { reconcileRunning = false; }
}
let reconcileTimer = null;
function startPaymentSweep() {
  if (reconcileTimer) return;
  const tick = () => {
    const mins = Number(sec.policy().paymentReconcileMinutes);
    reconcileTimer = setTimeout(async () => { try { if (mins > 0) await reconcilePending(50); } catch (e) { } tick(); }, Math.max(1, mins > 0 ? mins : 10) * 60000);
    if (reconcileTimer.unref) reconcileTimer.unref();
  };
  tick();
}
/* staff: ask the gateway now (live), or record money received offline (cash, a transfer) */
async function apiAdminPaymentReconcile(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  if (!requireSection(s, res, "payments", "write")) return;
  const p = get("SELECT * FROM payments WHERE id=? AND tenant_id=?", Number(id), T(s));
  if (!p) return bad(res, "Unknown payment", 404);
  if (!p.live) return bad(res, "This payment was not taken through a live gateway — record it as received if the money arrived", 409);
  const r = await reconcilePayment(p, "console");
  logAction(s, "payment.reconcile", "payment", p.id, { gateway: p.gateway, result: r.status || r.reason }, req);
  if (!r.ok && r.reason) return bad(res, "Could not check with " + p.gateway + ": " + r.reason, 502);
  json(res, 200, { ok: true, result: r, payment: get("SELECT * FROM payments WHERE id=?", p.id) });
}
function apiAdminPaymentReceived(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  if (!requireSection(s, res, "payments", "write")) return;
  const p = get("SELECT * FROM payments WHERE id=? AND tenant_id=?", Number(id), T(s));
  if (!p) return bad(res, "Unknown payment", 404);
  const offline = registry.list("offlinePaymentMethods").map(m => typeof m === "string" ? m : m.key);
  if (p.live || !offline.includes(String(p.method))) return bad(res, "Only a payment settled offline (" + offline.join(", ") + ") is recorded by hand — a gateway payment is confirmed by its gateway", 409);
  const r = applyPaymentStatus(p, { status: states.first("payment", "settled") }, p.gateway, "manual");
  if (r.unchanged) return bad(res, "This payment is already " + r.status, 409);
  logAction(s, "payment.received", "payment", p.id, { method: p.method, amount: p.amount, note: String((body && body.note) || "").slice(0, 200) }, req);
  json(res, 200, { ok: true, payment: get("SELECT * FROM payments WHERE id=?", p.id) });
}
function apiSsoGet(req, res, url, s) { if (!requireAdmin(s, res)) return; json(res, 200, { connection: enterprise.ssoConnection(T(s)) || { enabled: false } }); }
function apiSsoSet(req, res, url, s, body) { if (!requireAdmin(s, res)) return; if (!requireSection(s, res, "settings", "write")) return; json(res, 200, enterprise.setSso(T(s), body || {})); }
/* SSO always runs against the store this request is addressed to (subdomain / ?store= /
   cookie) — a body-supplied tenant_id let one store's callback sign a user into another */
function apiSsoStart(req, res, url, s, body) { const r = enterprise.ssoStart(T(s), String(body.email || "")); if (r.error) return bad(res, r.error, 400); json(res, 200, r); }
function apiSsoCallback(req, res, url, s, body) {
  return (async () => {
    const idToken = String(body.id_token || "");
    const r = enterprise.oidcComplete(T(s), idToken, body.state ? String(body.state) : null);
    if (!r.ok) return bad(res, r.error, 401);
    establishSession(req, res, s, r.userId, "auth.sso_login", { email: r.email });
    json(res, 200, { ok: true, user: { id: r.userId, email: r.email, role: r.role } });
  })();
}
function apiRegionsGet(req, res, url, s) { if (!requirePlatform(s, res)) return; json(res, 200, enterprise.regionConfig()); }
function apiRegionsSet(req, res, url, s, body) { if (!requirePlatform(s, res)) return; json(res, 200, enterprise.setRegions(body || {})); }
function apiFeeds(req, res, url, s, body, slug) { const fmt = /csv$/i.test(String(slug)) ? "csv" : "xml"; slug = String(slug || "").replace(/\.(xml|csv)$/i, ""); const t = get("SELECT id,slug FROM tenants WHERE slug=?", slug); if (!t) return bad(res, "Unknown store", 404); const feed = enterprise.productFeed(t.id, t.slug, fmt); res.writeHead(200, { "Content-Type": feed.type + "; charset=utf-8" }); res.end(feed.body); }
function apiTransfers(req, res, url, s, body) { if (!requireAdmin(s, res)) return; json(res, 200, { transfers: all("SELECT * FROM stock_transfers WHERE tenant_id=? AND deleted_at IS NULL ORDER BY id DESC LIMIT 100", T(s)) }); }
function apiTransferCreate(req, res, url, s, body) { if (!requireAdmin(s, res)) return; if (!requireSection(s, res, "skus", "write")) return; const r = enterprise.stockTransfer(T(s), body || {}); if (r.error) return bad(res, r.error, 422); logAction(s, "stock.transfer", "stock_transfer", r.id, { from: body.from_warehouse, to: body.to_warehouse, qty: body.qty }, req); json(res, 200, r); }
function apiTaxReport(req, res, url, s) { if (!requireAdmin(s, res)) return; json(res, 200, enterprise.taxReport(T(s), url.searchParams.get("period"))); }
function apiScimUsersList(req, res, url, s) { return (async () => { const t = Number(url.searchParams.get("tenant_id") || 1); const bearer = (req.headers.authorization || "").replace(/^Bearer\s+/i, ""); if (!enterprise.scimAuth(t, bearer)) return bad(res, "Invalid SCIM token", 401); json(res, 200, Object.assign({ schemas: "urn:ietf:params:scim:api:messages:2.0:ListResponse" }, await enterprise.scimList(t))); })(); }
function apiScimUserCreate(req, res, url, s, body) { return (async () => { const t = Number(url.searchParams.get("tenant_id") || (body && body._tenant) || 1); const bearer = (req.headers.authorization || "").replace(/^Bearer\s+/i, ""); if (!enterprise.scimAuth(t, bearer)) return bad(res, "Invalid SCIM token", 401); const r = await enterprise.scimCreate(t, body || {}); if (r.error) return bad(res, r.error, 400); json(res, 201, r); })(); }
function apiScimToken(req, res, url, s, body) { if (!requireAdmin(s, res)) return; const t = T(s); const r = enterprise.createScim(t, body && body.label); logAction(s, "scim.token", "scim_token", r.id, {}, req); json(res, 200, { id: r.id, token: r.token, note: "store this token now; only a hash is kept" }); }

/* ---------- global console (Countries, Currencies, Providers, Plans) ---------- */
function apiGlobalCountries(req, res, url, s) { if (!requirePlatform(s, res)) return; json(res, 200, { countries: globalmod.listCountries() }); }
function apiGlobalCountryGet(req, res, url, s) { if (!requirePlatform(s, res)) return; const code = url.searchParams.get("code"); if (!code) return bad(res, "code required", 400); json(res, 200, { country: globalmod.getCountry(code) }); }
function apiGlobalCountryPost(req, res, url, s, body) { if (!requirePlatformSection(s, res, "geo", "write")) return; if (!body || !body.code) return bad(res, "code required", 400); const r = globalmod.createCountry(body); json(res, r.ok ? 200 : 400, r); }
function apiGlobalCountryPut(req, res, url, s, body) { if (!requirePlatformSection(s, res, "geo", "write")) return; const code = url.searchParams.get("code"); if (!code || !body) return bad(res, "code and data required", 400); const r = globalmod.updateCountry(code, body); json(res, r.ok ? 200 : 400, r); }

function apiGlobalCurrencies(req, res, url, s) { if (!requirePlatform(s, res)) return; json(res, 200, { currencies: globalmod.listCurrencies() }); }
function apiGlobalCurrencyGet(req, res, url, s) { if (!requirePlatform(s, res)) return; const code = url.searchParams.get("code"); if (!code) return bad(res, "code required", 400); json(res, 200, { currency: globalmod.getCurrency(code) }); }
function apiGlobalCurrencyPost(req, res, url, s, body) { if (!requirePlatformSection(s, res, "geo", "write")) return; if (!body || !body.code) return bad(res, "code required", 400); const r = globalmod.createCurrency(body); json(res, r.ok ? 200 : 400, r); }
function apiGlobalCurrencyPut(req, res, url, s, body) { if (!requirePlatformSection(s, res, "geo", "write")) return; const code = url.searchParams.get("code"); if (!code || !body) return bad(res, "code and data required", 400); const r = globalmod.updateCurrency(code, body); json(res, r.ok ? 200 : 400, r); }

function apiGlobalProviders(req, res, url, s) { if (!requirePlatform(s, res)) return; const kind = url.searchParams.get("kind"); json(res, 200, { providers: globalmod.listProviders(kind) }); }
function apiGlobalProviderGet(req, res, url, s) { if (!requirePlatform(s, res)) return; const id = url.searchParams.get("id"); const kind = url.searchParams.get("kind"); if (!id || !kind) return bad(res, "id and kind required", 400); json(res, 200, { provider: globalmod.getProvider(id, kind) }); }
function apiGlobalProviderPost(req, res, url, s, body) { if (!requirePlatformSection(s, res, "providers", "write")) return; if (!body || !body.id || !body.kind) return bad(res, "id and kind required", 400); json(res, 200, globalmod.createProvider(body)); }
function apiGlobalProviderPut(req, res, url, s, body) { if (!requirePlatform(s, res)) return; const id = url.searchParams.get("id"); const kind = url.searchParams.get("kind"); if (!id || !kind || !body) return bad(res, "id, kind, and data required", 400); json(res, 200, globalmod.updateProvider(id, kind, body)); }
function apiGlobalProviderAvailability(req, res, url, s) { if (!requirePlatform(s, res)) return; const providerId = url.searchParams.get("provider_id"); if (!providerId) return bad(res, "provider_id required", 400); json(res, 200, { availability: globalmod.listProviderAvailability(providerId) }); }
function apiGlobalProviderEnableCountry(req, res, url, s, body) { if (!requirePlatformSection(s, res, "providers", "write")) return; const providerId = url.searchParams.get("provider_id"); const code = url.searchParams.get("code"); if (!providerId || !code) return bad(res, "provider_id and code required", 400); json(res, 200, globalmod.enableProviderInCountry(providerId, code)); }
function apiGlobalProviderDisableCountry(req, res, url, s) { if (!requirePlatformSection(s, res, "providers", "write")) return; const providerId = url.searchParams.get("provider_id"); const code = url.searchParams.get("code"); if (!providerId || !code) return bad(res, "provider_id and code required", 400); json(res, 200, globalmod.disableProviderInCountry(providerId, code)); }

function apiGlobalPlans(req, res, url, s) { if (!requirePlatform(s, res)) return; json(res, 200, { plans: globalmod.listPlans() }); }
function apiGlobalPlanGet(req, res, url, s) { if (!requirePlatform(s, res)) return; const id = url.searchParams.get("id"); if (!id) return bad(res, "id required", 400); json(res, 200, { plan: globalmod.getPlan(id) }); }
function apiGlobalPlanPost(req, res, url, s, body) { if (!requirePlatform(s, res)) return; if (!body || !body.name) return bad(res, "name required", 400); json(res, 200, globalmod.createPlan(body)); }
function apiGlobalPlanPut(req, res, url, s, body) { if (!requirePlatform(s, res)) return; const id = url.searchParams.get("id"); if (!id || !body) return bad(res, "id and data required", 400); json(res, 200, globalmod.updatePlan(id, body)); }

function apiGlobalTenantConfig(req, res, url, s) { if (!requirePlatform(s, res)) return; const tenantId = url.searchParams.get("tenant_id"); if (!tenantId) return bad(res, "tenant_id required", 400);
  json(res, 200, {
    country: globalmod.getTenantCountry(tenantId),
    currency: globalmod.getTenantCurrency(tenantId),
    providers: globalmod.getTenantProviders(tenantId),
    plan: globalmod.getTenantPlan(tenantId)
  });
}

function apiGlobalTenantCountry(req, res, url, s, body) { if (!requirePlatform(s, res)) return; const tenantId = url.searchParams.get("tenant_id"); const code = url.searchParams.get("code"); if (!tenantId || !code) return bad(res, "tenant_id and code required", 400); json(res, 200, globalmod.setTenantCountry(tenantId, code)); }
function apiGlobalTenantCurrency(req, res, url, s, body) { if (!requirePlatform(s, res)) return; const tenantId = url.searchParams.get("tenant_id"); const code = url.searchParams.get("code"); if (!tenantId || !code) return bad(res, "tenant_id and code required", 400); json(res, 200, globalmod.setTenantCurrency(tenantId, code)); }
function apiGlobalTenantProviders(req, res, url, s) { if (!requirePlatform(s, res)) return; const tenantId = url.searchParams.get("tenant_id"); const kind = url.searchParams.get("kind"); if (!tenantId) return bad(res, "tenant_id required", 400); json(res, 200, { providers: globalmod.getTenantProviders(tenantId, kind) }); }
function apiGlobalTenantProviderPost(req, res, url, s, body) { if (!requirePlatform(s, res)) return; const tenantId = url.searchParams.get("tenant_id"); const providerId = url.searchParams.get("provider_id"); const kind = url.searchParams.get("kind") || "payment"; if (!tenantId || !providerId) return bad(res, "tenant_id and provider_id required", 400); json(res, 200, globalmod.addTenantProvider(tenantId, providerId, kind, body || {})); }
function apiGlobalTenantProviderDelete(req, res, url, s) { if (!requirePlatform(s, res)) return; const tenantId = url.searchParams.get("tenant_id"); const providerId = url.searchParams.get("provider_id"); const kind = url.searchParams.get("kind") || "payment"; if (!tenantId || !providerId) return bad(res, "tenant_id and provider_id required", 400); json(res, 200, globalmod.removeTenantProvider(tenantId, providerId, kind)); }
function apiGlobalTenantPlan(req, res, url, s, body) { if (!requirePlatform(s, res)) return; const tenantId = url.searchParams.get("tenant_id"); const planId = url.searchParams.get("plan_id"); if (!tenantId || !planId) return bad(res, "tenant_id and plan_id required", 400); json(res, 200, globalmod.assignTenantPlan(tenantId, planId)); }

/* ---------- router ---------- */
/* ========== UCOS Ω∞ · constitutional registry (UPIP + UMQSOCR documents) ==========
   The Architecture documents are parsed, not transcribed: every endpoint below reads the
   canonical tables seeded by lib/ucos.js, so the platform never holds a second copy of the
   truth. Manifest/coverage are free reads (they power the console); mutations are admin-only. */
function ucosStore() { return ucos.store({ get, run, all }); }

function apiUcosManifest(req, res, url, s) {
  json(res, 200, ucos.manifest());
}
function apiUcosCoverage(req, res, url, s) {
  json(res, 200, ucos.coverage());
}
function apiUcosDocs(req, res, url, s) {
  json(res, 200, { documents: ucosStore().docs() });
}
function apiUcosParts(req, res, url, s, body, docId) {
  if (!requireStaff(s, res)) return;
  const o = ucosStore().parts(docId, url.searchParams.get("limit"), url.searchParams.get("offset"));
  json(res, 200, { doc: docId, parts: o.rows, total: o.total, limit: o.limit, offset: o.offset });
}
function apiUcosSections(req, res, url, s, body, docId) {
  if (!requireStaff(s, res)) return;
  const st = ucosStore();
  const out = st.sections(docId, url.searchParams.get("part"), url.searchParams.get("limit"), url.searchParams.get("offset"));
  json(res, 200, { doc: docId, sections: out.rows.map(function (r) { return Object.assign({}, r, { meta: J(r.meta, {}), doc_block: r.doc_block ? J(r.doc_block, {}) : null }); }), total: out.total, limit: out.limit, offset: out.offset });
}
function apiUcosConcepts(req, res, url, s, body, docId) {
  const out = ucosStore().concepts(docId, url.searchParams.get("q"), url.searchParams.get("limit"), url.searchParams.get("offset"));
  json(res, 200, { doc: docId, concepts: out.rows, total: out.total, limit: out.limit, offset: out.offset });
}
function apiUcosRegistries(req, res, url, s, body, docId) {
  if (!requireStaff(s, res)) return;
  const o = ucosStore().registries(docId, url.searchParams.get("limit"), url.searchParams.get("offset"));
  json(res, 200, { doc: docId, registries: o.rows, total: o.total, limit: o.limit, offset: o.offset });
}
function apiUcosEdges(req, res, url, s, body, docId) {
  if (!requireStaff(s, res)) return;
  const o = ucosStore().edges(docId, url.searchParams.get("source_type"), url.searchParams.get("source_id"), url.searchParams.get("limit"), url.searchParams.get("offset"));
  json(res, 200, { doc: docId, edges: o.rows, total: o.total, limit: o.limit, offset: o.offset });
}
function apiUcosNeighbours(req, res, url, s, body, docId) {
  const type = url.searchParams.get("type"), id = url.searchParams.get("id");
  if (!type || !id) return bad(res, "type and id parameters required");
  json(res, 200, Object.assign({ doc: docId }, ucosStore().neighbours(docId, type, id, url.searchParams.get("limit"))));
}
function apiUcosSearch(req, res, url, s) {
  const q = url.searchParams.get("q");
  if (!q) return bad(res, "q parameter required");
  json(res, 200, { q, results: ucos.search(q, Number(url.searchParams.get("limit")) || 50) });
}
function apiUcosReparse(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const out = ucos.seed({ get, run, all });
  logAction(s, "ucos.reparse", "ucos", "documents", out, req);
  json(res, 200, { ok: true, stats: out });
}
function apiUcosHealth(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  const h = ucosMon.health();
  const code = h.ok ? 200 : (h.status === "degraded" ? 200 : 503);
  json(res, code, h);
}
function apiUcosDrift(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  json(res, 200, Object.assign(ucosMon.driftStatus(), { log: ucosMon.driftLog() }));
}

/* ---------- foundation completeness ----------
   Executes the corpus's own FOUNDATION FREEZE CRITERIA (17AH.7) and exposes
   the master index, so "how much is left" is answered by data rather than by
   prose. The audit is read-only and derives every number from the registry. */
function apiUcosCompleteness(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  const a = ucosComp.audit();
  /* re-auditing is also how an operator LIFTS a hold: storing the fresh verdict means a
     resolved constitution unblocks constitutional writes immediately, with no restart */
  try {
    run("INSERT INTO platform_settings(key,value) VALUES('ucos_freeze',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
      JSON.stringify({ ok: a.ok, verdict: a.verdict, criticalCount: a.criticalCount, gapCount: a.gapCount, auditedAt: a.auditedAt }));
  } catch (e) { }
  json(res, a.ok ? 200 : 503, a);
}
/* 17AH.7 enforcement: while the constitution is unfreezable, the Tier-0 mutations it
   governs are refused with the gap summary. The operator resolves the gaps and re-runs
   the audit (GET /api/ucos/completeness) to lift the hold. */
function constitutionHeld(res) {
  if (!ucosComp.held()) return false;
  const st = ucosComp.freezeStatus();
  bad(res, "Constitution hold — " + (st && st.verdict || "unresolved freeze criteria") + " (" + (st && st.criticalCount || 0) + " critical gaps). Resolve them and re-run /api/ucos/completeness.", 503);
  return true;
}
function apiUcosIndex(req, res, url, s) {
  json(res, 200, ucosComp.masterIndex());
}

/* ---------- annotation CRUD (the write path) ----------
   Every mutation requires platform admin and is audit-logged; the canonical documents are never
   touched. Reads are open to store admins so a team can share context. */
function apiUcosAnnotations(req, res, url, s, body, docId) {
  if (!requireStaff(s, res)) return;
  const kind = url.searchParams.get("kind"), key = url.searchParams.get("key");
  if (!kind || !key) return bad(res, "kind and key parameters required");
  json(res, 200, ucos.annotations({ get, run, all }, docId, kind, key, url.searchParams.get("limit"), url.searchParams.get("offset")));
}
function apiUcosAnnotationCreate(req, res, url, s, body, docId) {
  if (!requirePlatform(s, res)) return;
  const out = ucos.addAnnotation({ get, run, all }, s, docId, body.kind, body.key, body.note, body.pin);
  logAction(s, "ucos.annotate", "ucos", body.kind + ":" + body.key, out, req);
  json(res, out.ok ? 200 : 400, out);
}
function apiUcosAnnotationUpdate(req, res, url, s, body, rest) {
  if (!requirePlatform(s, res)) return;
  const id = (url.pathname.split("/").pop()) || (body && body.id);
  const out = ucos.updateAnnotation({ get, run, all }, s, id, body.note, body.pin);
  logAction(s, "ucos.annotate", "ucos", "annotation:" + id, out, req);
  json(res, out.ok ? 200 : 400, out);
}
function apiUcosAnnotationDelete(req, res, url, s, body, rest) {
  if (!requirePlatform(s, res)) return;
  const id = (url.pathname.split("/").pop()) || (body && body.id);
  const out = ucos.deleteAnnotation({ get, run, all }, s, id);
  logAction(s, "ucos.annotate", "ucos", "annotation:" + id, out, req);
  json(res, out.ok ? 200 : 404, out);
}
function apiUcosAnnotationOrphans(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  json(res, 200, { orphans: ucos.orphanedAnnotations({ get, run, all }) });
}

/* ---------- UCOS Ω∞ Foundation Registry (Architecture3 Articles 2-8) ----------
   The operational half of the constitution. Reads are open to administrators so the
   console can draw the five graphs; the register/certify/deprecate mutations are
   Foundation Authority actions and require platform admin (Article 6). Every mutation
   is recorded in the append-only ledger by the module itself. */
function apiUcosFoundationsManifest(req, res, url, s) {
  json(res, 200, ucosFound.manifest());
}
function apiUcosFoundationsList(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  json(res, 200, { foundations: ucosFound.list({ universe: url.searchParams.get("universe"), lifecycle: url.searchParams.get("lifecycle") }) });
}
function apiUcosFoundationResolve(req, res, url, s, body, key) {
  if (!requireStaff(s, res)) return;
  const f = ucosFound.resolve(key);
  if (!f) return bad(res, "foundation not found", 404);
  json(res, 200, f);
}
function apiUcosFoundationTraverse(req, res, url, s, body, key) {
  if (!requireStaff(s, res)) return;
  const graph = url.searchParams.get("graph") || "dependency";
  if (!ucosFound.GRAPHS[graph]) return bad(res, "unknown graph: " + graph, 400);
  json(res, 200, ucosFound.traverse(key, graph, url.searchParams.get("depth")));
}
function apiUcosFoundationRegister(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  if (constitutionHeld(res)) return;
  const out = ucosFound.register(body.name, {
    parent: body.parent, dependencies: body.dependencies, universe: body.universe,
    lifecycle: body.lifecycle, governance: body.governance,
    sourceDoc: body.source_doc, sourceLine: body.source_line
  });
  logAction(s, "ucos.foundation.register", "ucos", out.key, out, req);
  json(res, out.ok ? 200 : 409, out);
}
function apiUcosFoundationCertify(req, res, url, s, body, key) {
  if (!requirePlatform(s, res)) return;
  if (constitutionHeld(res)) return;
  const out = ucosFound.certify(key);
  logAction(s, "ucos.foundation.certify", "ucos", key, out, req);
  json(res, out.ok ? 200 : 404, out);
}
function apiUcosFoundationDeprecate(req, res, url, s, body, key) {
  if (!requirePlatform(s, res)) return;
  if (constitutionHeld(res)) return;
  const out = ucosFound.deprecate(key, body && body.successor);
  logAction(s, "ucos.foundation.deprecate", "ucos", key, out, req);
  json(res, out.ok ? 200 : 409, out);
}
function apiUcosFoundationRetire(req, res, url, s, body, key) {
  if (!requirePlatform(s, res)) return;
  if (constitutionHeld(res)) return;
  const out = ucosFound.retire(key);
  logAction(s, "ucos.foundation.retire", "ucos", key, out, req);
  json(res, out.ok ? 200 : 409, out);
}
/* Article 3.2 / 8.2: the compliance rules are executable — this proves the registry
   is acyclic, fully resolved, unique and orphan-free at any moment */
function apiUcosFoundationsVerify(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  const v = ucosFound.verify();
  json(res, v.ok ? 200 : 503, v);
}
function apiUcosFoundationsLedger(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  json(res, 200, { events: ucosFound.ledger(url.searchParams.get("limit")) });
}

/* ---------- instantiated universes ----------
   Each universe the corpus declares is registered as a foundation AND instantiated as a
   live, data-defined entity, so the constitution is operable rather than merely readable.
   The instantiation is derived from the corpus (never hand-listed) and idempotent. */
function apiUcosUniverses(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  json(res, 200, { universes: ucosUniv.list(), stats: ucosUniv.stats() });
}
function apiUcosUniversesInstantiate(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const out = ucosUniv.instantiateAll();
  logAction(s, "ucos.universes.instantiate", "ucos", "universes", out, req);
  json(res, 200, { ok: true, ...out, stats: ucosUniv.stats() });
}
function apiUcosCoverageReport(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  json(res, 200, coverageReport());
}

/* ---------- catalog bridge: universe entities become shopper-transactable ----------
   Publishing is a platform action (it changes a tenant's live catalog); withdrawal
   too. Reads are open to store admins so a merchant can see what is on their shelf. */
function apiUcosCatalogStats(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  json(res, 200, ucosCat.catalogStats());
}
function apiUcosCatalogPublish(req, res, url, s, body, key) {
  if (!requirePlatform(s, res)) return;
  const tenantId = Number(url.searchParams.get("tenant_id") || (s.tenant && s.tenant.id));
  if (!tenantId) return bad(res, "tenant_id required", 400);
  const out = ucosCat.publishUniverse(tenantId, key);
  logAction(s, "ucos.catalog.publish", "ucos", key, out, req);
  json(res, out.ok ? 200 : 409, out);
}
function apiUcosCatalogWithdraw(req, res, url, s, body, key) {
  if (!requirePlatform(s, res)) return;
  const tenantId = Number(url.searchParams.get("tenant_id") || (s.tenant && s.tenant.id));
  if (!tenantId) return bad(res, "tenant_id required", 400);
  const out = ucosCat.withdrawUniverse(tenantId, key);
  logAction(s, "ucos.catalog.withdraw", "ucos", key, out, req);
  json(res, 200, out);
}
function apiUcosCatalogList(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  /* tenant_id= is honoured only for platform admins; a store admin sees their own store */
  const tenantId = s.platform_admin && url.searchParams.get("tenant_id") ? Number(url.searchParams.get("tenant_id")) : T(s);
  json(res, 200, { published: tenantId ? ucosCat.listPublished(tenantId) : [], stats: ucosCat.catalogStats() });
}

/* ---------- ACTIVATION: every declared universe becomes shopper-transactable ----------
   This is the "implement all" primitive: activation materializes a universe's
   canonical offering (from its own corpus-declared fields) and publishes it into a
   tenant catalog, so the whole constitution is on the shelf by default. It is a
   platform action (it writes a tenant's live catalog), bounded and idempotent. */
function apiUcosCatalogActivate(req, res, url, s, body, key) {
  if (!requirePlatform(s, res)) return;
  const tenantId = Number(url.searchParams.get("tenant_id") || (s.tenant && s.tenant.id));
  if (!tenantId) return bad(res, "tenant_id required", 400);
  /* the target must be a real store — activation writes that tenant's live catalog,
     so an invented id must be refused rather than creating orphaned catalog rows */
  if (!get("SELECT 1 ok FROM tenants WHERE id=? AND status IN " + stIn("tenant", "operating").sql, tenantId, ...stIn("tenant", "operating").args))
    return bad(res, "unknown or inactive tenant", 404);
  /* the limit is capped: a corpus of thousands must never saturate one request */
  const limit = Math.min(Number(body && body.limit) || 250, 2000);
  const out = key ? ucosCat.activate(tenantId, key) : ucosCat.activateAll(tenantId, { limit });
  logAction(s, "ucos.catalog.activate", "ucos", key || "all", out, req);
  json(res, out.ok === false ? 409 : 200, out);
}
function apiUcosActivationStats(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  json(res, 200, ucosCat.activationStats());
}

/* ---------- TRACEABILITY: where is a corpus declaration implemented? ----------
   For any key this reports every runtime layer it resolves to — registry concept,
   foundation, universe, live entity, records, catalog projection, API routes and
   console views — or honestly reports that a layer is absent. The corpus→runtime
   matrix is the measurable answer to "how much of the constitution is built?" */
const ucosTrace = require("./ucos-trace.js");
function apiUcosTrace(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  const key = url.searchParams.get("key");
  if (!key) return json(res, 200, ucosTrace.matrix());
  json(res, 200, ucosTrace.trace(key));
}
function apiUcosMatrix(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  json(res, 200, ucosTrace.matrix());
}

/* ---------- PER-DOMAIN RECORD ENGINE ----------
   Each universe is a DOMAIN: its records move through the state machine the corpus
   declares (UCOS 5.1 states, 5.2 rules, UMQSOCR Art. 10 components), and every
   transition is rule-gated and append-audited (Article 6). No universe-specific
   code — the machine is derived per domain (Article 4.2). */
const ucosDomain = require("./ucos-domain.js");
function apiUcosDomain(req, res, url, s, body, key) {
  if (!requireStaff(s, res)) return;
  const d = ucosDomain.board(key, s.platform_admin ? null : T(s));
  if (!d) return bad(res, "unknown universe " + key, 404);
  json(res, 200, d);
}
function apiUcosDomainFire(req, res, url, s, body, key) {
  if (!requireStaff(s, res)) return;
  if (constitutionHeld(res)) return;
  const rid = Number((body && body.record_id) || url.searchParams.get("record_id"));
  if (!rid) return bad(res, "record_id required", 400);
  const out = ucosDomain.fire(key, rid, { tenantId: s.platform_admin ? null : T(s), actor: s.platform_admin ? ("platform:" + s.platform_admin.email) : ("admin:" + s.user_id), detail: body && body.detail });
  logAction(s, "ucos.domain.transition", "ucos", key + "#" + rid, out, req);
  json(res, out.ok === false ? 409 : 200, out);
}
function apiUcosDomains(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  json(res, 200, { domains: ucosDomain.domains() });
}

/* the measurable answer to "is everything implemented?": universe instantiation coverage
   and concept→implementation traceability, both derived from live state */
function coverageReport() {
  const st = ucosUniv.stats();
  const docs = ucos.manifest().documents;
  return {
    universes: st,
    registry: {
      documents: docs.length,
      sections: docs.reduce((a, d) => a + d.sections, 0),
      articles: docs.reduce((a, d) => a + d.articles, 0),
      concepts: docs.reduce((a, d) => a + d.concepts, 0),
      registries: docs.reduce((a, d) => a + d.registries, 0)
    },
    foundations: ucosFound.verify().populations,
    verdict: st.coverage === 100 ? "100% of declared universes instantiated and operable" : st.coverage + "% of declared universes instantiated (" + (st.declared - st.instantiated) + " pending)",
    reportedAt: new Date().toISOString()
  };
}

/* ============================================================
   UNIVERSAL COMMERCE HANDLERS — each handler is a thin composition over
   the commerce engines (lib/qcommerce.js, lib/fintech.js,
   lib/marketplace-ext.js, lib/trade.js); validation and state come
   from registries so nothing is hardcoded here.
   ============================================================ */
/* ---------- Quick-commerce ---------- */
function apiQcPromise(req, res, url, s) {
  const zip = String(url.searchParams.get("zip") || s.zip || "");
  const lat = url.searchParams.get("lat") != null ? +url.searchParams.get("lat") : null;
  const lng = url.searchParams.get("lng") != null ? +url.searchParams.get("lng") : null;
  json(res, 200, qcommerce.promise(T(s), zip, lat, lng));
}
function apiQcStores(req, res, url, s) {
  /* riders' names and phone numbers are staff data — the public store listing omits them */
  json(res, 200, { stores: qcommerce.listStores(T(s)), riders: (s.platform_admin || isAdmin(s)) ? qcommerce.listRiders(T(s)) : undefined });
}
function apiQcSlots(req, res, url, s) {
  const storeId = Number(url.searchParams.get("store")) || null;
  const day = Number(url.searchParams.get("day")) || 0;
  json(res, 200, { slots: qcommerce.slotsFor(T(s), storeId, day) });
}
/* pinning reserves dark-store stock, so it only ever reserves what is in the CALLER'S cart, in
   whole positive quantities within the cart limit — it used to reserve any product, any
   quantity (including negative), for an anonymous caller, as often as it was called */
function apiQcPin(req, res, url, s, body) {
  if (!Array.isArray(body.items)) return bad(res, "items[] required");
  const maxQ = Number(CFG(s).commerce.cartMaxQty) || 10;
  const staff = !!(s.platform_admin || isAdmin(s));
  const items = [];
  for (const i of body.items) {
    const pid = String(i.product_id || i.id || "");
    const want = Math.floor(Number(i.qty) || 1);
    if (!(want >= 1)) return json(res, 200, { ok: false, reason: "invalid_quantity", product_id: pid });
    const inCart = get("SELECT qty FROM cart_items WHERE owner=? AND product_id=?", ownerFor(s), pid);
    if (!inCart && !staff) return json(res, 200, { ok: false, reason: "not_in_cart", product_id: pid });
    items.push({ product_id: pid, sku_id: i.sku_id ? Number(i.sku_id) : null, qty: Math.min(want, maxQ, inCart ? inCart.qty : maxQ) });
  }
  const zip = String(body.zip || s.zip || "");
  try {
    const pin = qcommerce.pinCart(T(s), items, zip, body.lat != null ? +body.lat : null, body.lng != null ? +body.lng : null);
    if (pin.ok) run("UPDATE cart_items SET store_id=? WHERE owner=?", pin.store.id, ownerFor(s));
    json(res, 200, pin);
  } catch (e) { bad(res, e.message); }
}
function apiQcReserve(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  try {
    const ok = qcommerce.reserve(T(s), Number(body.store_id), String(body.product_id), body.sku_id ? Number(body.sku_id) : null, Number(body.qty) || 1);
    json(res, 200, { ok, sellable: qcommerce.sellable(T(s), Number(body.store_id), String(body.product_id), body.sku_id ? Number(body.sku_id) : null) });
  } catch (e) { bad(res, e.message); }
}
/* dispatch runs carry the proof-of-delivery OTP — the code the rider collects from the
   customer. Listing them publicly let anyone read the code and mark any run delivered. */
function apiQcRuns(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  json(res, 200, { runs: qcommerce.listRuns(T(s), url.searchParams.get("status") || "") });
}
function apiQcRunCreate(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  try {
    const run = qcommerce.createRun(T(s), body);
    logAction(s, "qcommerce.run.create", "dispatch_run", run.id, { ref: run.ref }, req);
    json(res, 200, { run });
  } catch (e) { bad(res, e.message); }
}
function apiQcRunTransition(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  try {
    const run = qcommerce.transitionRun(T(s), Number(id), String(body.status), body);
    logAction(s, "qcommerce.run." + body.status, "dispatch_run", run.id, {}, req);
    json(res, 200, { run });
  } catch (e) { bad(res, e.message); }
}
function apiQcPod(req, res, url, s, body, id) {
  try { json(res, 200, { run: qcommerce.confirmPod(T(s), Number(id), String(body.otp || "")) }); }
  catch (e) { bad(res, e.message); }
}
function apiQcRiders(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  json(res, 200, { riders: qcommerce.listRiders(T(s)) });
}

/* ---------- Fintech ---------- */
function apiFinUpi(req, res, url, s) {
  json(res, 200, fintech.upi(T(s), ownerFor(s)));
}
function apiFinUpiAdd(req, res, url, s, body) {
  if (!body.vpa) return bad(res, "VPA required");
  json(res, 200, { handle: fintech.addUpi(T(s), ownerFor(s), String(body.vpa), body.name) });
}
function apiFinUpiCollect(req, res, url, s, body) {
  try { json(res, 200, { collect: fintech.collectUpi(T(s), ownerFor(s), String(body.payer_vpa || ""), body.amount, body.currency, body.note) }); }
  catch (e) { bad(res, e.message); }
}
function apiFinUpiSettle(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { collect: fintech.settleCollect(T(s), Number(id), body.failed ? false : true) }); }
  catch (e) { bad(res, e.message); }
}
function apiFinQrCreate(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { qr: fintech.createQr(T(s), body) }); } catch (e) { bad(res, e.message); }
}
function apiFinQrScan(req, res, url, s, body, id) {
  try { json(res, 200, { qr: fintech.scanQr(T(s), Number(id)) }); } catch (e) { bad(res, e.message); }
}
function apiFinLinkCreate(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { link: fintech.createLink(T(s), body) }); } catch (e) { bad(res, e.message); }
}
function apiFinLinkPay(req, res, url, s, body, token) {
  try { json(res, 200, { link: fintech.payLink(T(s), String(token)) }); } catch (e) { bad(res, e.message); }
}
function apiFinMandateRegister(req, res, url, s, body) {
  try { json(res, 200, { mandate: fintech.registerMandate(T(s), { ...body, owner: ownerFor(s) }) }); }
  catch (e) { bad(res, e.message); }
}
function apiFinMandateCharge(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { mandate: fintech.chargeMandate(T(s), Number(id), body.amount) }); }
  catch (e) { bad(res, e.message); }
}
function apiFinEscrowHold(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { escrow: fintech.hold(T(s), body.order_id, ownerFor(s), String(body.seller || ""), body.amount, body.currency, body.meta) }); }
  catch (e) { bad(res, e.message); }
}
function apiFinEscrowRelease(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { escrow: fintech.releaseEscrow(T(s), Number(id)) }); } catch (e) { bad(res, e.message); }
}
function apiFinEscrowDispute(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { escrow: fintech.disputeEscrow(T(s), Number(id), body.open === false ? false : true) }); }
  catch (e) { bad(res, e.message); }
}
function apiFinSplit(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { split: fintech.splitPayment(T(s), body.payment_id, body.order_id, body.amount, body.splits) }); }
  catch (e) { bad(res, e.message); }
}
function apiFinKycSubmit(req, res, url, s, body) {
  try { json(res, 200, { kyc: fintech.submitKyc(T(s), ownerFor(s), body) }); } catch (e) { bad(res, e.message); }
}
function apiFinKycVerify(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { kyc: fintech.verifyKyc(T(s), Number(id), body.level || "full", body.reject ? false : true) }); }
  catch (e) { bad(res, e.message); }
}
function apiFinPayoutQueue(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { payout: fintech.queuePayout(T(s), body) }); } catch (e) { bad(res, e.message); }
}
function apiFinPayoutProcess(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { payout: fintech.processPayout(T(s), Number(id)) }); } catch (e) { bad(res, e.message); }
}
function apiFinBillers(req, res, url, s) {
  json(res, 200, { billers: fintech.billers(T(s)) });
}
function apiFinBillPay(req, res, url, s, body) {
  try { json(res, 200, { bill: fintech.payBill(T(s), ownerFor(s), body) }); } catch (e) { bad(res, e.message); }
}
function apiFinPlans(req, res, url, s) {
  json(res, 200, { plans: fintech.plans(T(s)) });
}
function apiFinRecharge(req, res, url, s, body) {
  try { json(res, 200, { recharge: fintech.doRecharge(T(s), ownerFor(s), body) }); } catch (e) { bad(res, e.message); }
}
function apiFinTransfer(req, res, url, s, body) {
  try { json(res, 200, fintech.transfer(T(s), ownerFor(s), String(body.to || ""), body.amount, body.note)); }
  catch (e) { bad(res, e.message); }
}
function apiFinBnplOpen(req, res, url, s, body) {
  try { json(res, 200, { account: fintech.openBnpl(T(s), ownerFor(s), body) }); } catch (e) { bad(res, e.message); }
}
/* a BNPL account, its EMIs and an insurance policy belong to one owner: only that owner
   (or store staff) may spend, pay or activate them — these took a bare sequential id. */
function finOwns(s, table, id) {
  if (s.platform_admin || isAdmin(s)) return true;
  const r = get("SELECT owner FROM " + table + " WHERE id=? AND tenant_id=?", Number(id), T(s));
  return !!(r && r.owner === ownerFor(s));
}
function apiFinBnplSpend(req, res, url, s, body, id) {
  if (!finOwns(s, "bnpl_accounts", id)) return bad(res, "BNPL account not found", 404);
  try { json(res, 200, { emis: fintech.spendBnpl(T(s), Number(id), body.order_id, body.amount) }); }
  catch (e) { bad(res, e.message); }
}
/* a customer pays an installment from their wallet; staff may record an offline payment.
   It used to mark any EMI paid for free, restoring the credit line without a payment. */
function apiFinEmiPay(req, res, url, s, body, id) {
  const e = get("SELECT e.id, e.amount, e.status, a.owner FROM bnpl_emis e JOIN bnpl_accounts a ON a.id=e.account_id WHERE e.id=? AND e.tenant_id=?", Number(id), T(s));
  const staff = !!(s.platform_admin || isAdmin(s));
  if (!e || (!staff && e.owner !== ownerFor(s))) return bad(res, "EMI not found", 404);
  if (stIs("emi", e.status, "settled") || !(+e.amount > 0)) return bad(res, "EMI not payable");
  if (!staff) {
    if (mods.walletBalance(T(s), e.owner) < e.amount) return bad(res, "Insufficient wallet balance to pay this installment", 402);
    mods.walletAdd(T(s), e.owner, -e.amount);
  }
  try { json(res, 200, { emi: fintech.payEmi(T(s), Number(id)) }); }
  catch (err) { if (!staff) mods.walletAdd(T(s), e.owner, e.amount); bad(res, err.message); }
}
function apiFinLoanApply(req, res, url, s, body) {
  try { json(res, 200, { loan: fintech.applyLoan(T(s), ownerFor(s), body) }); } catch (e) { bad(res, e.message); }
}
function apiFinLoanDisburse(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { loan: fintech.disburseLoan(T(s), Number(id)) }); } catch (e) { bad(res, e.message); }
}
function apiFinInsuranceQuote(req, res, url, s, body) {
  try { json(res, 200, { policy: fintech.quoteInsurance(T(s), ownerFor(s), body) }); } catch (e) { bad(res, e.message); }
}
function apiFinInsuranceActivate(req, res, url, s, body, id) {
  if (!finOwns(s, "insurance_policies", id)) return bad(res, "Policy not found", 404);
  try { json(res, 200, { policy: fintech.activateInsurance(T(s), Number(id)) }); } catch (e) { bad(res, e.message); }
}
/* S2: issuing a voucher mints spendable wallet credit (redeemVoucher credits a
   real balance), so it is an operator action — never an anonymous one. Redeem
   stays owner-scoped: a shopper redeems a code they hold, validated against the
   issued row. The console's own gift_voucher entity is admin/platform-write with
   no module requirement (lib/entity.js), so this route matches it — the module
   gate belongs on the balance path (apiGiftAdd), not on the code-issuing one. */
function apiFinVoucherIssue(req, res, url, s, body) {
  if (!requireStaff(s, res, "gfinance")) return;
  try { json(res, 200, { voucher: fintech.issueVoucher(T(s), body) }); } catch (e) { bad(res, e.message); }
}
function apiFinVoucherRedeem(req, res, url, s, body) {
  try { json(res, 200, { voucher: fintech.redeemVoucher(T(s), String(body.code || ""), ownerFor(s)) }); }
  catch (e) { bad(res, e.message); }
}

/* ---------- Marketplace ---------- */
function apiMktApply(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { onboarding: mkt.apply(T(s), body) }); } catch (e) { bad(res, e.message); }
}
function apiMktReview(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { onboarding: mkt.review(T(s), Number(id), String(body.decision || ""), s.platform_admin ? s.platform_admin.email : "admin", body.notes) }); }
  catch (e) { bad(res, e.message); }
}
function apiMktOffers(req, res, url, s, body, productId) {
  json(res, 200, { offers: mkt.listOffers(T(s), String(productId)), buybox: mkt.buyboxFor(T(s), String(productId)) });
}
function apiMktBuybox(req, res, url, s, body, productId) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, mkt.recomputeBuybox(T(s), String(productId)));
}
function apiMktFba(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { inbound: mkt.fbaInbound(T(s), body) }); } catch (e) { bad(res, e.message); }
}
function apiMktFbaReceive(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { inbound: mkt.receiveFba(T(s), Number(id)) }); } catch (e) { bad(res, e.message); }
}
function apiMktPerformance(req, res, url, s, body, sellerId) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { performance: mkt.computePerformance(T(s), Number(sellerId), body && body.period) }); }
  catch (e) { bad(res, e.message); }
}
/* a buyer opens a claim only on THEIR order, for at most what they paid; staff may open one
   on any order in the store. It used to accept any order id and any amount — freezing other
   buyers' escrow and, on a buyer-favourable resolution, crediting the invented amount. */
function apiMktClaimOpen(req, res, url, s, body) {
  const b = body || {};
  const staff = !!(s.platform_admin || isAdmin(s));
  const order = get("SELECT id, owner, total FROM orders WHERE id=? AND tenant_id=?", Number(b.order_id) || 0, T(s));
  if (!order || (!staff && order.owner !== ownerFor(s))) return bad(res, "Order not found", 404);
  const amount = +Number(b.amount || 0).toFixed(2);
  if (!(amount > 0) || amount > +order.total) return bad(res, "Claim amount must be between 0 and the order total", 400);
  try {
    const claim = mkt.openClaim(T(s), { ...b, amount, buyer: staff && b.buyer ? String(b.buyer) : order.owner });
    logAction(s, "claim.open", "buyer_claim", claim.id, { order: body.order_id }, req);
    json(res, 200, { claim });
  } catch (e) { bad(res, e.message); }
}
function apiMktClaimResolve(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { claim: mkt.resolveClaim(T(s), Number(id), String(body.resolution || ""), s.platform_admin ? s.platform_admin.email : "admin") }); }
  catch (e) { bad(res, e.message); }
}
function apiMktSmart(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { smart: mkt.enrolSmart(T(s), body) }); } catch (e) { bad(res, e.message); }
}
function apiMktPortal(req, res, url, s, body, sellerId) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, mkt.sellerPortal(T(s), Number(sellerId))); } catch (e) { bad(res, e.message); }
}

/* ---------- B2B trust & trade ---------- */
function apiTradeAssure(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { assurance: trade.assure(T(s), body.order_id, ownerFor(s), String(body.seller || ""), body.amount, body.currency, body.milestones) }); }
  catch (e) { bad(res, e.message); }
}
function apiTradeMilestone(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { assurance: trade.advanceMilestone(T(s), Number(id), String(body.milestone || "")) }); }
  catch (e) { bad(res, e.message); }
}
/* confirming delivery releases the escrow to the seller, so only the BUYER (the owner the
   assurance — or its order — was opened for) or store staff may do it. It used to be open
   to anyone, and assurance ids are sequential. */
function apiTradeConfirm(req, res, url, s, body, id) {
  const ta = get("SELECT buyer, order_id FROM trade_assurance WHERE id=? AND tenant_id=?", Number(id), T(s));
  if (!ta) return bad(res, "Trade-assurance order not found", 404);
  const me = ownerFor(s);
  const ord = ta.order_id ? get("SELECT owner FROM orders WHERE id=? AND tenant_id=?", ta.order_id, T(s)) : null;
  const isBuyer = (ta.buyer && ta.buyer === me) || (ord && ord.owner === me);
  if (!isBuyer && !s.platform_admin && !isAdmin(s)) return bad(res, "Only the buyer can confirm delivery", 403);
  try { json(res, 200, { assurance: trade.confirmDelivery(T(s), Number(id)) }); } catch (e) { bad(res, e.message); }
}
function apiTradeDispute(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { assurance: trade.disputeAssurance(T(s), Number(id), body.open === false ? false : true) }); }
  catch (e) { bad(res, e.message); }
}
function apiTradeGold(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { gold: trade.enrolGold(T(s), body) }); } catch (e) { bad(res, e.message); }
}
function apiTradeVerifySubmit(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { verification: trade.submitVerification(T(s), body) }); } catch (e) { bad(res, e.message); }
}
function apiTradeVerifyComplete(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { verification: trade.completeVerification(T(s), Number(id), body.reject ? false : true, s.platform_admin ? s.platform_admin.email : "admin", body.badges, body.notes) }); }
  catch (e) { bad(res, e.message); }
}
function apiTradeBadges(req, res, url, s, body, supplierId) {
  json(res, 200, trade.badgesFor(T(s), Number(supplierId)));
}
function apiTradeDoc(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { doc: trade.generateDoc(T(s), body) }); } catch (e) { bad(res, e.message); }
}
function apiTradeDocGet(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  const doc = get("SELECT * FROM export_documents WHERE id=? AND tenant_id=?", Number(id), T(s));
  if (!doc) return bad(res, "Document not found", 404);
  json(res, 200, { doc });
}
function apiTradeLc(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { lc: trade.issueLc(T(s), body) }); } catch (e) { bad(res, e.message); }
}
function apiTradeLcPresent(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { lc: trade.presentLc(T(s), Number(id), body.discrepant ? false : true) }); }
  catch (e) { bad(res, e.message); }
}
function apiTradeQuote(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { quote: trade.quoteRfq(T(s), { ...body, rfq_id: Number(id) }) }); } catch (e) { bad(res, e.message); }
}
function apiTradeQuoteAccept(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { quote: trade.acceptQuote(T(s), Number(id)) }); } catch (e) { bad(res, e.message); }
}
function apiTradeBid(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { bid: trade.bid(T(s), { ...body, tender_id: Number(id) }) }); } catch (e) { bad(res, e.message); }
}
function apiTradeAward(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  try { json(res, 200, { bid: trade.awardTender(T(s), Number(id), Number(body.bid_id)) }); } catch (e) { bad(res, e.message); }
}
function apiTradePrice(req, res, url, s) {
  const productId = String(url.searchParams.get("product") || "");
  const skuId = url.searchParams.get("sku") ? Number(url.searchParams.get("sku")) : null;
  const qty = Number(url.searchParams.get("qty")) || 1;
  const segment = url.searchParams.get("segment") || "";
  if (!productId) return bad(res, "product required");
  json(res, 200, { price: trade.priceFor(T(s), productId, skuId, qty, segment) });
}
function apiTradeMoqCheck(req, res, url, s) {
  const items = url.searchParams.get("items");
  try {
    const parsed = items ? JSON.parse(items) : [];
    json(res, 200, trade.checkCartMoq(T(s), parsed));
  } catch (e) { bad(res, "Invalid items JSON"); }
}

/* ---------- Shopper experience completions ---------- */
function notifyWrite(tenantId, owner, kind, title, body, link) {
  const kinds = registry.list("shopNotifKinds").map(x => x.key || x);
  run("INSERT INTO notifications(tenant_id,owner,kind,title,body,link,read,meta) VALUES(?,?,?,?,?,?,0,'{}')",
    tenantId, String(owner || ""), kinds.includes(kind) ? kind : "order_placed", String(title || ""), String(body || ""), String(link || ""));
}
function apiNotifications(req, res, url, s) {
  const rows = all("SELECT * FROM notifications WHERE tenant_id=? AND owner=? ORDER BY id DESC LIMIT 50", T(s), ownerFor(s));
  const unread = all("SELECT COUNT(*) c FROM notifications WHERE tenant_id=? AND owner=? AND read=0", T(s), ownerFor(s))[0].c;
  json(res, 200, { notifications: rows, unread });
}
function apiNotificationsRead(req, res, url, s, body) {
  if (body.all) run("UPDATE notifications SET read=1 WHERE tenant_id=? AND owner=?", T(s), ownerFor(s));
  else if (body.id) run("UPDATE notifications SET read=1 WHERE id=? AND tenant_id=? AND owner=?", Number(body.id), T(s), ownerFor(s));
  json(res, 200, { ok: true });
}
function compareRow(tenantId, owner) {
  let row = get("SELECT * FROM compare_lists WHERE tenant_id=? AND owner=?", tenantId, owner);
  if (!row) { run("INSERT INTO compare_lists(tenant_id,owner,product_ids) VALUES(?,?, '[]')", tenantId, owner); row = get("SELECT * FROM compare_lists WHERE tenant_id=? AND owner=?", tenantId, owner); }
  return row;
}
function apiCompare(req, res, url, s) {
  const row = compareRow(T(s), ownerFor(s));
  const ids = JSON.parse(row.product_ids || "[]");
  const products = ids.length ? all(`SELECT * FROM products WHERE tenant_id=? AND id IN (${ids.map(() => "?").join(",")}) AND deleted_at IS NULL`, T(s), ...ids) : [];
  json(res, 200, { ids, products });
}
function apiCompareAdd(req, res, url, s, body) {
  const row = compareRow(T(s), ownerFor(s));
  const ids = JSON.parse(row.product_ids || "[]");
  const id = String(body.product_id || body.id || "");
  if (id && !ids.includes(id) && ids.length < 4) ids.push(id);
  run("UPDATE compare_lists SET product_ids=? WHERE id=?", JSON.stringify(ids), row.id);
  json(res, 200, { ids });
}
function apiCompareRemove(req, res, url, s, body) {
  const row = compareRow(T(s), ownerFor(s));
  const ids = JSON.parse(row.product_ids || "[]").filter(x => x !== String(body.product_id || body.id));
  run("UPDATE compare_lists SET product_ids=? WHERE id=?", JSON.stringify(ids), row.id);
  json(res, 200, { ids });
}
function apiRegistriesList(req, res, url, s) {
  const rows = s.user_id
    ? all("SELECT * FROM gift_registries WHERE tenant_id=? AND owner=? ORDER BY id DESC", T(s), ownerFor(s))
    : [];
  json(res, 200, { registries: rows });
}
function apiRegistryCreate(req, res, url, s, body) {
  if (!s.user_id) return bad(res, "Sign in to create a registry", 401);
  const name = String(body.name || "").trim();
  if (!name) return bad(res, "Registry name required");
  const events = registry.list("shopEvents").map(x => x.key || x);
  const ref = "REG-" + Date.now().toString(36).toUpperCase().slice(-6);
  const r = run("INSERT INTO gift_registries(tenant_id,ref,owner,name,event,event_date,shipping_address,notes,items,contributors,status) VALUES(?,?,?,?,?,?,?,?, '[]','[]','open')",
    T(s), ref, ownerFor(s), name, events.includes(body.event) ? body.event : "wedding",
    body.event_date || null, String(body.shipping_address || ""), String(body.notes || ""));
  json(res, 200, { registry: get("SELECT * FROM gift_registries WHERE id=?", r.lastInsertRowid) });
}
function apiRegistryItem(req, res, url, s, body, id) {
  const reg = get("SELECT * FROM gift_registries WHERE id=? AND tenant_id=? AND owner=?", Number(id), T(s), ownerFor(s));
  if (!reg) return bad(res, "Registry not found", 404);
  const items = JSON.parse(reg.items || "[]");
  const pid = String(body.product_id || "");
  if (body.remove) {
    const next = items.filter(x => x.product_id !== pid);
    run("UPDATE gift_registries SET items=? WHERE id=?", JSON.stringify(next), reg.id);
  } else if (pid && !items.some(x => x.product_id === pid)) {
    items.push({ product_id: pid, qty: Number(body.qty) || 1, purchased: 0 });
    run("UPDATE gift_registries SET items=? WHERE id=?", JSON.stringify(items), reg.id);
  }
  json(res, 200, { registry: get("SELECT * FROM gift_registries WHERE id=?", reg.id) });
}
function apiOrderCancel(req, res, url, s, body, id) {
  const o = get("SELECT * FROM orders WHERE id=? AND tenant_id=? AND owner=?", Number(id), T(s), ownerFor(s));
  if (!o) return bad(res, "Order not found", 404);
  if (!stIs("order", o.status, "cancellable")) return bad(res, "This order cannot be cancelled");
  run("UPDATE orders SET status=?, cancel_reason=? WHERE id=?", states.first("order", "aborted"), String(body.reason || "customer_cancelled"), o.id);
  notifyWrite(T(s), ownerFor(s), "order_cancelled", "Order " + o.num + " cancelled", "Your order has been cancelled. Any refund will be credited to your wallet.", "/orders.html");
  logAction(s, "order.cancel", "order", o.id, { num: o.num });
  json(res, 200, { ok: true });
}
function apiOrderInvoice(req, res, url, s, body, id) {
  const o = get("SELECT * FROM orders WHERE id=? AND tenant_id=? AND owner=?", Number(id), T(s), ownerFor(s));
  if (!o) return bad(res, "Order not found", 404);
  const items = all("SELECT * FROM order_items WHERE order_id=?", o.id);
  const body0 = items.map((it, i) => ({ line: i + 1, description: String(it.product_id), qty: it.qty, unit_price: it.price, amount: +(it.qty * it.price).toFixed(2) }));
  const kinds = registry.list("shopDocKinds").map(x => x.key || x);
  const kind = kinds.includes(body.kind) ? body.kind : "tax_invoice";
  const ref = "DOC-" + Date.now().toString(36).toUpperCase().slice(-6);
  const r = run("INSERT INTO invoice_documents(tenant_id,ref,order_id,owner,doc_kind,invoice_number,place_of_supply,gstin,pan,taxable,tax,total,currency,body,status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?, 'generated')",
    T(s), ref, o.id, ownerFor(s), kind, o.num, String(o.state || ""), "", "",
    +(o.sub - o.gift_used).toFixed(2), +o.tax.toFixed(2), +o.total.toFixed(2), String(o.currency || require("./defaults.js").currency(T(s))), JSON.stringify(body0));
  json(res, 200, { doc: get("SELECT * FROM invoice_documents WHERE id=?", r.lastInsertRowid) });
}

/* ============================================================
   THE CONFIGURATION LAYER — types, standards, quality, features and
   functionalities of any platform or service, configured as rows.
   These routes are the whole management surface: read the catalog and a
   tenant's composition, switch a capability on or off, tune one declared
   parameter, and author/apply/reuse archetypes (presets). There is no
   per-capability route and no per-platform code anywhere — a capability
   nobody has configured is simply off, and configuring it is an act of
   composition, not a deploy. (Architecture3 §2.1.) */
const caps = require("./capabilities.js");
/* a store admin composes only its own store; the platform admin may
   configure any tenant. Returns the tenant id to act on, or null to refuse */
function capTenantScope(s, body) {
  const tid = body && body.tenant_id != null ? Number(body.tenant_id) : T(s);
  if (!s.platform_admin && tid !== T(s)) return null;
  return tid;
}
/* one read renders the entire console: the catalog (what is configurable),
   the archetypes, and the selected tenant's live composition */
function apiCapabilities(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  /* a platform admin composes the master's own deployment by default — the
     deployment the platform itself is — and may read any additional deployment
     it provisioned through ?tenant_id= */
  const master = masterTenant();
  const tid = s.platform_admin && url.searchParams.get("tenant_id") ? Number(url.searchParams.get("tenant_id")) : T(s);
  /* `params` = the declared definitions (type/default/label — the form scaffolding);
     `effective` = this tenant's resolved values (defaults → preset → own overrides),
     empty while the capability is off, so the console tunes what it reads */
  /* settings_atom: the capability is also a storefront feature toggle (the console marks it) */
  const catalog = caps.catalog().map(c => ({ ...c, on: caps.on(tid, c.key), effective: caps.cap(tid, c.key), settings_atom: caps.STOREFRONT_KEYS.includes(c.key) }));
  json(res, 200, {
    catalog, presets: caps.presets(), composition: caps.compositionOf(tid), tenant_id: tid, domains: rl("capabilityDomains"),
    master_id: master && master.id,
    tenants: s.platform_admin ? (all("SELECT id, slug, name FROM tenants ORDER BY id") || [])
      .map(t => ({ ...t, master: !!(master && t.id === master.id) }))
      .sort((a, b) => (b.master ? 1 : 0) - (a.master ? 1 : 0)) : undefined
  });
}
/* platform-level: switch a capability off for every store, or retitle it */
function apiCapPlatform(req, res, url, s, body, key) {
  if (!requirePlatform(s, res)) return;
  try {
    const out = caps.setPlatform(String(key || "").trim(), { enabled: body.enabled, label: body.label, description: body.description });
    logAction(s, "capability.platform", "capability", String(key), { enabled: body.enabled }, req);
    json(res, 200, { capability: out });
  } catch (e) { bad(res, e.message, 409); }
}
/* switch a capability ON for a tenant, with optional param overrides */
function apiCapEnable(req, res, url, s, body) {
  /* S3: capTenantScope only checked WHICH tenant, never that the caller is
     staff — so an anonymous shopper could recompose any store. The read
     (apiCapabilities) already gated on admin; the writes must too. */
  if (!requireStaff(s, res)) return;
  const tid = capTenantScope(s, body);
  if (tid === null) return bad(res, "You can only configure your own store", 403);
  try {
    const out = caps.enable(tid, String(body.capability || "").trim(), body.params || {}, body.notes);
    logAction(s, "capability.enable", "capability", String(body.capability), { tenant_id: tid }, req);
    json(res, 200, out);
  } catch (e) { bad(res, e.message, 409); }
}
function apiCapDisable(req, res, url, s, body) {
  if (!requireStaff(s, res)) return;
  const tid = capTenantScope(s, body);
  if (tid === null) return bad(res, "You can only configure your own store", 403);
  const out = caps.disable(tid, String(body.capability || "").trim());
  logAction(s, "capability.disable", "capability", String(body.capability), { tenant_id: tid }, req);
  json(res, 200, out);
}
/* tune ONE declared parameter — coerced to its declared type, and refused if
   the capability or parameter is unknown to the catalog */
function apiCapParam(req, res, url, s, body) {
  if (!requireStaff(s, res)) return;
  const tid = capTenantScope(s, body);
  if (tid === null) return bad(res, "You can only configure your own store", 403);
  try {
    const out = caps.tune(tid, String(body.capability || "").trim(), String(body.param || "").trim(), body.value);
    logAction(s, "capability.param", "capability", String(body.capability) + "." + body.param, { tenant_id: tid, value: body.value }, req);
    json(res, 200, out);
  } catch (e) { bad(res, e.message, 409); }
}
/* apply a named archetype to a tenant */
function apiCapPresetApply(req, res, url, s, body) {
  if (!requireStaff(s, res)) return;
  const tid = capTenantScope(s, body);
  if (tid === null) return bad(res, "You can only configure your own store", 403);
  try {
    const out = caps.applyPreset(tid, String(body.preset || "").trim());
    logAction(s, "capability.preset.apply", "capability_preset", String(body.preset), { tenant_id: tid }, req);
    json(res, 200, out);
  } catch (e) { bad(res, e.message, 409); }
}
/* author or rewrite an archetype — a platform-owned vocabulary */
function apiCapPresetSave(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  try {
    const out = caps.savePreset(body.key, body.label, body.description, body.capabilities || {}, body.universes);
    logAction(s, "capability.preset.save", "capability_preset", String(body.key), req);
    json(res, 200, { preset: out });
  } catch (e) { bad(res, e.message, 409); }
}
function apiCapPresetDelete(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  const out = caps.removePreset(String(body.preset || "").trim());
  logAction(s, "capability.preset.delete", "capability_preset", String(body.preset), req);
  json(res, 200, out);
}
/* author a capability the seed never knew about — the open-ended catalog. This is
   what makes the platform any platform: surge pricing for mobility, creator
   payouts for video, lead scoring for a CRM, all as typed data */
function apiCapDefine(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  try {
    const out = caps.define(body.key, body.label, body.domain, body.icon, body.description, body.params || {});
    logAction(s, "capability.define", "capability", String(body.key), { domain: body.domain }, req);
    json(res, 200, { capability: out });
  } catch (e) { bad(res, e.message, 409); }
}
function apiCapUndefine(req, res, url, s, body, key) {
  if (!requirePlatform(s, res)) return;
  try {
    const out = caps.undefine(String(key || "").trim());
    logAction(s, "capability.undefine", "capability", String(key), req);
    json(res, 200, out);
  } catch (e) { bad(res, e.message, 409); }
}

const routes = [
  /* ============================================================
     UNIVERSAL COMMERCE ROUTES — one capability surface per
     domain; the heavy lifting is generic entity CRUD
     (/api/meta/entity/:key) and these handlers compose the engines.
     ============================================================ */
  /* Quick-commerce — promise, slots, pinning, dispatch */
  ["GET /api/qc/promise", apiQcPromise],
  ["GET /api/qc/stores", apiQcStores],
  ["GET /api/qc/slots", apiQcSlots],
  ["POST /api/qc/pin", apiQcPin],
  ["POST /api/qc/reserve", apiQcReserve],
  ["GET /api/qc/runs", apiQcRuns],
  ["POST /api/qc/runs", apiQcRunCreate],
  ["POST /api/qc/runs/:id", (r, re, u, s, b, p) => apiQcRunTransition(r, re, u, s, b, p)],
  ["POST /api/qc/runs/:id/pod", (r, re, u, s, b, p) => apiQcPod(r, re, u, s, b, p)],
  ["GET /api/qc/riders", apiQcRiders],
  /* Fintech — UPI, QR, links, mandates, escrow, splits, KYC,
     payouts, BBPS, recharge, P2P, BNPL, loans, insurance, vouchers */
  ["GET /api/fintech/upi", apiFinUpi],
  ["POST /api/fintech/upi", apiFinUpiAdd],
  ["POST /api/fintech/upi/collect", apiFinUpiCollect],
  ["POST /api/fintech/upi/collect/:id", (r, re, u, s, b, p) => apiFinUpiSettle(r, re, u, s, b, p)],
  ["POST /api/fintech/qr", apiFinQrCreate],
  ["POST /api/fintech/qr/:id/scan", (r, re, u, s, b, p) => apiFinQrScan(r, re, u, s, b, p)],
  ["POST /api/fintech/links", apiFinLinkCreate],
  ["POST /api/fintech/links/:token/pay", (r, re, u, s, b, p) => apiFinLinkPay(r, re, u, s, b, p)],
  ["POST /api/fintech/mandates", apiFinMandateRegister],
  ["POST /api/fintech/mandates/:id/charge", (r, re, u, s, b, p) => apiFinMandateCharge(r, re, u, s, b, p)],
  ["POST /api/fintech/escrow", apiFinEscrowHold],
  ["POST /api/fintech/escrow/:id/release", (r, re, u, s, b, p) => apiFinEscrowRelease(r, re, u, s, b, p)],
  ["POST /api/fintech/escrow/:id/dispute", (r, re, u, s, b, p) => apiFinEscrowDispute(r, re, u, s, b, p)],
  ["POST /api/fintech/splits", apiFinSplit],
  ["POST /api/fintech/kyc", apiFinKycSubmit],
  ["POST /api/fintech/kyc/:id/verify", (r, re, u, s, b, p) => apiFinKycVerify(r, re, u, s, b, p)],
  ["POST /api/fintech/payouts", apiFinPayoutQueue],
  ["POST /api/fintech/payouts/:id/process", (r, re, u, s, b, p) => apiFinPayoutProcess(r, re, u, s, b, p)],
  ["GET /api/fintech/billers", apiFinBillers],
  ["POST /api/fintech/bills", apiFinBillPay],
  ["GET /api/fintech/plans", apiFinPlans],
  ["POST /api/fintech/recharge", apiFinRecharge],
  ["POST /api/fintech/transfer", apiFinTransfer],
  ["POST /api/fintech/bnpl", apiFinBnplOpen],
  ["POST /api/fintech/bnpl/:id/spend", (r, re, u, s, b, p) => apiFinBnplSpend(r, re, u, s, b, p)],
  ["POST /api/fintech/emi/:id/pay", (r, re, u, s, b, p) => apiFinEmiPay(r, re, u, s, b, p)],
  ["POST /api/fintech/loans", apiFinLoanApply],
  ["POST /api/fintech/loans/:id/disburse", (r, re, u, s, b, p) => apiFinLoanDisburse(r, re, u, s, b, p)],
  ["POST /api/fintech/insurance", apiFinInsuranceQuote],
  ["POST /api/fintech/insurance/:id/activate", (r, re, u, s, b, p) => apiFinInsuranceActivate(r, re, u, s, b, p)],
  ["POST /api/fintech/vouchers", apiFinVoucherIssue],
  ["POST /api/fintech/vouchers/redeem", apiFinVoucherRedeem],
  /* Marketplace — onboarding, buy-box, FBA, health, claims */
  ["POST /api/marketplace/onboarding", apiMktApply],
  ["POST /api/marketplace/onboarding/:id/review", (r, re, u, s, b, p) => apiMktReview(r, re, u, s, b, p)],
  ["GET /api/marketplace/offers/:productId", (r, re, u, s, b, p) => apiMktOffers(r, re, u, s, b, p)],
  ["POST /api/marketplace/buybox/:productId", (r, re, u, s, b, p) => apiMktBuybox(r, re, u, s, b, p)],
  ["POST /api/marketplace/fba", apiMktFba],
  ["POST /api/marketplace/fba/:id/receive", (r, re, u, s, b, p) => apiMktFbaReceive(r, re, u, s, b, p)],
  ["POST /api/marketplace/performance/:sellerId", (r, re, u, s, b, p) => apiMktPerformance(r, re, u, s, b, p)],
  ["POST /api/marketplace/claims", apiMktClaimOpen],
  ["POST /api/marketplace/claims/:id/resolve", (r, re, u, s, b, p) => apiMktClaimResolve(r, re, u, s, b, p)],
  ["POST /api/marketplace/smart-fulfilment", apiMktSmart],
  ["GET /api/marketplace/portal/:sellerId", (r, re, u, s, b, p) => apiMktPortal(r, re, u, s, b, p)],
  /* B2B trust & trade */
  ["POST /api/trade/assurance", apiTradeAssure],
  ["POST /api/trade/assurance/:id/milestone", (r, re, u, s, b, p) => apiTradeMilestone(r, re, u, s, b, p)],
  ["POST /api/trade/assurance/:id/confirm", (r, re, u, s, b, p) => apiTradeConfirm(r, re, u, s, b, p)],
  ["POST /api/trade/assurance/:id/dispute", (r, re, u, s, b, p) => apiTradeDispute(r, re, u, s, b, p)],
  ["POST /api/trade/gold", apiTradeGold],
  ["POST /api/trade/verification", apiTradeVerifySubmit],
  ["POST /api/trade/verification/:id/complete", (r, re, u, s, b, p) => apiTradeVerifyComplete(r, re, u, s, b, p)],
  ["GET /api/trade/badges/:supplierId", (r, re, u, s, b, p) => apiTradeBadges(r, re, u, s, b, p)],
  ["POST /api/trade/docs", apiTradeDoc],
  ["GET /api/trade/docs/:id", (r, re, u, s, b, p) => apiTradeDocGet(r, re, u, s, b, p)],
  ["POST /api/trade/lc", apiTradeLc],
  ["POST /api/trade/lc/:id/present", (r, re, u, s, b, p) => apiTradeLcPresent(r, re, u, s, b, p)],
  ["POST /api/trade/rfq/:id/quote", (r, re, u, s, b, p) => apiTradeQuote(r, re, u, s, b, p)],
  ["POST /api/trade/quotes/:id/accept", (r, re, u, s, b, p) => apiTradeQuoteAccept(r, re, u, s, b, p)],
  ["POST /api/trade/tenders/:id/bid", (r, re, u, s, b, p) => apiTradeBid(r, re, u, s, b, p)],
  ["POST /api/trade/tenders/:id/award", (r, re, u, s, b, p) => apiTradeAward(r, re, u, s, b, p)],
  ["GET /api/trade/price", apiTradePrice],
  ["GET /api/trade/moq-check", apiTradeMoqCheck],
  /* Shopper experience completions */
  ["GET /api/notifications", apiNotifications],
  ["POST /api/notifications/read", apiNotificationsRead],
  ["GET /api/compare", apiCompare],
  ["POST /api/compare", apiCompareAdd],
  ["POST /api/compare/remove", apiCompareRemove],
  ["GET /api/registries", apiRegistriesList],
  ["POST /api/registries", apiRegistryCreate],
  ["POST /api/registries/:id/items", (r, re, u, s, b, p) => apiRegistryItem(r, re, u, s, b, p)],
  ["POST /api/orders/:id/cancel", (r, re, u, s, b, p) => apiOrderCancel(r, re, u, s, b, p)],
  ["POST /api/orders/:id/invoice", (r, re, u, s, b, p) => apiOrderInvoice(r, re, u, s, b, p)],

  ["GET /api/config", apiConfig],  /* universal theming — presets, the resolution cascade, assignments, generative hue exploration */
  ["GET /api/themes", apiThemes],
  ["GET /api/themes/resolve", apiThemeResolve],
  ["GET /api/themes/preview", apiThemePreview],
  ["POST /api/themes/assign", apiThemeAssign],
  ["POST /api/themes/unassign", apiThemeUnassign],
   ["POST /api/themes", apiThemeCreate],
  /* the configuration layer: every standard, quality, feature and functionality
     a platform or service exposes, composed per store from the console */
  ["GET /api/capabilities", apiCapabilities],
  ["POST /api/capabilities/platform/:key", (r, re, u, s, b, p) => apiCapPlatform(r, re, u, s, b, p)],
  ["POST /api/capabilities/enable", apiCapEnable],
  ["POST /api/capabilities/disable", apiCapDisable],
  ["POST /api/capabilities/param", apiCapParam],
  ["POST /api/capabilities/preset/apply", apiCapPresetApply],
  ["POST /api/capabilities/preset", apiCapPresetSave],
  ["POST /api/capabilities/preset/delete", apiCapPresetDelete],
  ["POST /api/capabilities/catalog", apiCapDefine],
  ["DELETE /api/capabilities/catalog/:key", apiCapUndefine],
  /* universal dashboard & reporting engine (Architecture1 §394/§395) */
  ["GET /api/dashboards/entities", apiDashboardEntities],
  ["GET /api/dashboards", apiDashboards],
  ["GET /api/dashboards/:key", apiDashboardRender],
  ["POST /api/dashboards/:key", (r, re, u, s, b, p) => apiDashboardSave(r, re, u, s, b, p)],
  ["PUT /api/dashboards/:key", (r, re, u, s, b, p) => apiDashboardSave(r, re, u, s, b, p)],
  ["DELETE /api/dashboards/:key", apiDashboardDelete],
  ["POST /api/dashboards/:key/widgets", (r, re, u, s, b, p) => apiWidgetSave(r, re, u, s, b, p)],
  ["DELETE /api/dashboards/:key/widgets", apiWidgetDelete],
  ["POST /api/dashboards/:key/prefs", (r, re, u, s, b, p) => apiDashboardPref(r, re, u, s, b, p)],
  ["GET /api/reports", apiReports],
  ["GET /api/reports/:key/run", (r, re, u, s, b, p) => apiReportRun(r, re, u, s, b, p)],
  ["POST /api/reports/:key", (r, re, u, s, b, p) => apiReportSave(r, re, u, s, b, p)],
  ["PUT /api/reports/:key", (r, re, u, s, b, p) => apiReportSave(r, re, u, s, b, p)],
  ["DELETE /api/reports/:key", apiReportDelete],
  ["GET /api/stores", apiStores],
  ["GET /api/providers", apiProviders],
  ["GET /api/meta", apiMeta],
  ["GET /api/meta/entities", apiEntities],
  ["GET /api/meta/entity/:key", (r, re, u, s, b, p) => apiEntityList(r, re, u, s, b, p)],
  ["GET /api/admin/trash", apiTrashList],
  ["POST /api/admin/trash/:key/:id/restore", (r, re, u, s, b, p, i) => apiTrashRestore(r, re, u, s, b, p, i)],
  ["POST /api/admin/trash/purge", apiTrashPurge],
  ["GET /api/admin/retention", apiRetentionGet],
  ["PUT /api/admin/retention", apiRetentionPut],
  ["GET /api/admin/roles", apiRoles],
  ["POST /api/admin/roles", apiRoleSave],
  ["DELETE /api/admin/roles/:key", (r, re, u, s, b, p) => apiRoleDelete(r, re, u, s, b, p)],
  ["POST /api/admin/roles/reset", apiRoleReset],
  ["GET /api/admin/staff", apiStaffList],
  ["POST /api/admin/staff", apiStaffCreate],
  ["PUT /api/admin/staff/:id", (r, re, u, s, b, p) => apiStaffUpdate(r, re, u, s, b, p)],
  ["DELETE /api/admin/staff/:id", (r, re, u, s, b, p) => apiStaffDelete(r, re, u, s, b, p)],
  ["POST /api/platform/purge-expired", apiAdminPurgeExpired],
  ["POST /api/meta/entity/:key", (r, re, u, s, b, p) => apiEntityCreate(r, re, u, s, b, p)],
  ["PUT /api/meta/entity/:key/:id", (r, re, u, s, b, p, i) => apiEntityUpdate(r, re, u, s, b, p, i)],
  ["DELETE /api/meta/entity/:key/:id", (r, re, u, s, b, p, i) => apiEntityDelete(r, re, u, s, b, p, i)],
  ["GET /api/meta/entity-def", apiEntityDefsList],
  ["POST /api/meta/entity-def", apiEntityDefSave],
  ["DELETE /api/meta/entity-def/:key", (r, re, u, s, b, p) => apiEntityDefDelete(r, re, u, s, b, p)],
  ["POST /api/meta/entity-def/:key/enable", (r, re, u, s, b, p) => apiEntityDefEnable(r, re, u, s, b, p)],
  ["POST /api/meta/entity-def/:key/disable", (r, re, u, s, b, p) => apiEntityDefDisable(r, re, u, s, b, p)],
  ["GET /api/tenant/entity-def", apiTenantEntityDefs],
  ["GET /api/ucii/capabilities", apiCapabilityList],
  ["POST /api/ucii/capabilities", apiCapabilityCreate],
  ["PUT /api/ucii/capabilities/:key", (r, re, u, s, b, p) => apiCapabilityUpdate(r, re, u, s, b, p)],
  ["GET /api/ucii/domains", apiDomainList],
  ["POST /api/ucii/domains", apiDomainCreate],
  ["GET /api/ucii/policies", apiPolicyList],
  ["POST /api/ucii/policies", apiPolicyCreate],
  ["GET /api/ucii/workflows", apiWorkflowList],
  ["POST /api/ucii/workflows", apiWorkflowCreate],
  ["DELETE /api/ucii/workflows/:key", (r, re, u, s, b, p) => apiWorkflowDelete(r, re, u, s, b, p)],
  ["GET /api/ucii/config", apiConfigGet],
  ["POST /api/ucii/config", apiConfigSet],
  ["GET /api/platform/global-products", apiGlobalProductList],
  ["GET /api/platform/universe-fields/:key", (r, re, u, s, b, p) => apiUniverseFields(r, re, u, s, b, p)],
  ["POST /api/platform/global-products", apiGlobalProductCreate],
  ["PUT /api/platform/global-products/:id", (r, re, u, s, b, p) => apiGlobalProductUpdate(r, re, u, s, b, p)],
  ["DELETE /api/platform/global-products/:id", (r, re, u, s, b, p) => apiGlobalProductDelete(r, re, u, s, b, p)],
  ["GET /api/platform/store-product-config", apiStoreProductConfig],
  ["POST /api/platform/store-product-config", apiStoreProductConfigSet],
  ["DELETE /api/platform/store-product-config/:tenant_id/:global_id", (r, re, u, s, b, p, q) => apiStoreProductConfigDelete(r, re, u, s, b, p, q)],
  ["GET /api/tenant/products", apiStoreProductPermissions],
  ["GET /api/platform/global-catalog", apiGlobalCatalog],
  ["GET /api/tenant/catalog/importable", apiStoreCatalogImportable],
  ["POST /api/tenant/catalog/import", (r, re, u, s, b, p) => apiStoreCatalogImport(r, re, u, s, b, p)],
  ["GET /api/ucii/knowledge", apiKnowledgeGraphQuery],
  ["POST /api/ucii/knowledge", apiKnowledgeGraphAdd],
  ["POST /api/ucii/usage", apiUsageRecord],
  ["GET /api/ucii/usage", apiUsageReport],
  ["GET /api/ucos/manifest", apiUcosManifest],
  ["GET /api/ucos/coverage", apiUcosCoverage],
  ["GET /api/ucos/docs", apiUcosDocs],
  ["GET /api/ucos/:doc/parts", (r, re, u, s, b, p) => apiUcosParts(r, re, u, s, b, p)],
  ["GET /api/ucos/:doc/sections", (r, re, u, s, b, p) => apiUcosSections(r, re, u, s, b, p)],
  ["GET /api/ucos/:doc/concepts", (r, re, u, s, b, p) => apiUcosConcepts(r, re, u, s, b, p)],
  ["GET /api/ucos/:doc/registries", (r, re, u, s, b, p) => apiUcosRegistries(r, re, u, s, b, p)],
  ["GET /api/ucos/:doc/edges", (r, re, u, s, b, p) => apiUcosEdges(r, re, u, s, b, p)],
  ["GET /api/ucos/:doc/neighbours", (r, re, u, s, b, p) => apiUcosNeighbours(r, re, u, s, b, p)],
  ["GET /api/ucos/search", apiUcosSearch],
  ["POST /api/ucos/reparse", apiUcosReparse],
  ["GET /api/ucos/health", apiUcosHealth],
  ["GET /api/ucos/drift", apiUcosDrift],
  ["GET /api/ucos/completeness", apiUcosCompleteness],
  ["GET /api/ucos/index", apiUcosIndex],
  ["GET /api/ucos/:doc/annotations", (r, re, u, s, b, p) => apiUcosAnnotations(r, re, u, s, b, p)],
  ["POST /api/ucos/:doc/annotations", (r, re, u, s, b, p) => apiUcosAnnotationCreate(r, re, u, s, b, p)],
  ["PUT /api/ucos/annotations/:id", (r, re, u, s, b, p) => apiUcosAnnotationUpdate(r, re, u, s, b, p)],
  ["DELETE /api/ucos/annotations/:id", (r, re, u, s, b, p) => apiUcosAnnotationDelete(r, re, u, s, b, p)],
  ["GET /api/ucos/annotations/orphans", apiUcosAnnotationOrphans],
  /* UCOS Foundation Registry — Architecture3 Articles 2-8.
     Literal paths are registered before :key so they are not swallowed by the
     parameter route (the router takes the first segment-length match). */
  ["GET /api/ucos/foundations/manifest", apiUcosFoundationsManifest],
  ["GET /api/ucos/foundations/verify", apiUcosFoundationsVerify],
  ["GET /api/ucos/foundations/ledger", apiUcosFoundationsLedger],
  ["GET /api/ucos/foundations", apiUcosFoundationsList],
  ["GET /api/ucos/foundations/:key", (r, re, u, s, b, p) => apiUcosFoundationResolve(r, re, u, s, b, p)],
  ["GET /api/ucos/foundations/:key/traverse", (r, re, u, s, b, p) => apiUcosFoundationTraverse(r, re, u, s, b, p)],
  ["POST /api/ucos/foundations", apiUcosFoundationRegister],
  ["POST /api/ucos/foundations/:key/certify", (r, re, u, s, b, p) => apiUcosFoundationCertify(r, re, u, s, b, p)],
  ["POST /api/ucos/foundations/:key/deprecate", (r, re, u, s, b, p) => apiUcosFoundationDeprecate(r, re, u, s, b, p)],
  ["POST /api/ucos/foundations/:key/retire", (r, re, u, s, b, p) => apiUcosFoundationRetire(r, re, u, s, b, p)],
  /* instantiated universes */
  ["GET /api/ucos/universes", apiUcosUniverses],
  ["POST /api/ucos/universes/instantiate", apiUcosUniversesInstantiate],
  ["GET /api/ucos/coverage-report", apiUcosCoverageReport],
  /* catalog bridge — universe entities published into a tenant's storefront */
  ["GET /api/ucos/catalog", apiUcosCatalogList],
  ["GET /api/ucos/catalog/stats", apiUcosCatalogStats],
  ["POST /api/ucos/catalog/:key/publish", (r, re, u, s, b, p) => apiUcosCatalogPublish(r, re, u, s, b, p)],
  ["POST /api/ucos/catalog/:key/withdraw", (r, re, u, s, b, p) => apiUcosCatalogWithdraw(r, re, u, s, b, p)],
  /* activation — every declared universe becomes shopper-transactable */
  ["POST /api/ucos/catalog/activate", apiUcosCatalogActivate],
  ["POST /api/ucos/catalog/:key/activate", (r, re, u, s, b, p) => apiUcosCatalogActivate(r, re, u, s, b, p)],
  ["GET /api/ucos/catalog/activation", apiUcosActivationStats],
  /* traceability — corpus declaration → runtime artifact map */
  ["GET /api/ucos/trace", apiUcosTrace],
  ["GET /api/ucos/matrix", apiUcosMatrix],
  /* per-domain record engine — each universe's corpus-declared state machine */
  ["GET /api/ucos/domains", apiUcosDomains],
  ["GET /api/ucos/domain/:key", (r, re, u, s, b, p) => apiUcosDomain(r, re, u, s, b, p)],
  ["POST /api/ucos/domain/:key/fire", (r, re, u, s, b, p) => apiUcosDomainFire(r, re, u, s, b, p)],
  ["GET /api/platform/entity-types", apiEntityTypeList],
  ["POST /api/platform/entity-types", apiEntityTypeCreate],
  ["PUT /api/platform/entity-types/:entity/:type_key", (r, re, u, s, b, p, t) => apiEntityTypeUpdate(r, re, u, s, b, p, t)],
  ["DELETE /api/platform/entity-types/:entity/:type_key", (r, re, u, s, b, p, q) => apiEntityTypeDelete(r, re, u, s, b, p, q)],
  ["GET /api/platform/tenant-entities", apiTenantEntityList],
  ["POST /api/platform/tenant-entities", apiTenantEntityConfig],
  ["POST /api/platform/tenant-fields", apiTenantFieldConfig],
  /* the Global Platform's cross-tenant commerce reader: one generic surface for every
     entity-backed store capability (products, orders, SKUs, sellers, RFQs, compliance…),
     aggregated across stores with the same definitions the Store Console uses */
  ["GET /api/platform/data", apiPlatformDataIndex],
  ["GET /api/platform/data/:key", (r, re, u, s, b, p) => apiPlatformDataList(r, re, u, s, b, p)],
  ["GET /api/platform/data/:key/def", (r, re, u, s, b, p) => apiPlatformDataDef(r, re, u, s, b, p)],
  ["GET /api/platform/data/:key/export", (r, re, u, s, b, p) => apiPlatformDataExport(r, re, u, s, b, p)],
  ["GET /api/platform/data/:key/sample", (r, re, u, s, b, p) => apiPlatformDataSample(r, re, u, s, b, p)],
  ["POST /api/platform/data/:key", (r, re, u, s, b, p) => apiPlatformDataCreate(r, re, u, s, b, p)],
  ["PUT /api/platform/data/:key/:id", (r, re, u, s, b, p, i) => apiPlatformDataUpdate(r, re, u, s, b, p, i)],
  ["DELETE /api/platform/data/:key/:id", (r, re, u, s, b, p, i) => apiPlatformDataDelete(r, re, u, s, b, p, i)],
  ["POST /api/platform/data/:key/import", (r, re, u, s, b, p) => apiPlatformDataImport(r, re, u, s, b, p)],
  /* cross-store fan-out: runs an existing read-only Store Console route once per store and
     merges — every composite capability gains a platform surface with no logic duplicated */
  ["GET /api/platform/fanout", apiPlatformFanout],
  ["GET /api/platform/attributes", apiAttributeList],
  ["POST /api/platform/attributes", apiAttributeCreate],
  ["GET /api/platform/entity-attributes", apiEntityAttributeList],
  ["POST /api/platform/entity-attributes", apiEntityAttributeAttach],
  ["GET /api/taxonomy", apiTaxonomy],
  ["GET /api/promos", apiPromos],
  ["POST /api/rfqs", apiRfqCreate],
  ["POST /api/returns", apiReturnCreate],
  ["GET /api/session", apiSession],
  ["POST /api/zip", apiZip],
  ["GET /api/fx", apiFxConvert],
  ["GET /api/platform/hint", apiPlatformHint],
  ["GET /api/hint", apiHint],
  ["GET /api/platform/fx", apiPlatformFx],
  ["POST /api/platform/fx/rates", apiPlatformFxRates],
  ["PUT /api/platform/fx/provider", apiPlatformFxProvider],
  ["POST /api/platform/fx/sync", (r, re, u, s, b) => apiPlatformFxSync(r, re, u, s)],
  ["GET /api/platform/global/countries", apiGlobalCountries],
  ["GET /api/platform/global/country", apiGlobalCountryGet],
  ["POST /api/platform/global/country", apiGlobalCountryPost],
  ["PUT /api/platform/global/country", apiGlobalCountryPut],
  ["GET /api/platform/global/currencies", apiGlobalCurrencies],
  ["GET /api/platform/global/currency", apiGlobalCurrencyGet],
  ["POST /api/platform/global/currency", apiGlobalCurrencyPost],
  ["PUT /api/platform/global/currency", apiGlobalCurrencyPut],
  ["GET /api/platform/global/providers", apiGlobalProviders],
  ["GET /api/platform/global/provider", apiGlobalProviderGet],
  ["POST /api/platform/global/provider", apiGlobalProviderPost],
  ["PUT /api/platform/global/provider", apiGlobalProviderPut],
  ["GET /api/platform/global/provider/availability", apiGlobalProviderAvailability],
  ["POST /api/platform/global/provider/enable", apiGlobalProviderEnableCountry],
  ["POST /api/platform/global/provider/disable", apiGlobalProviderDisableCountry],
  ["GET /api/platform/global/plans", apiGlobalPlans],
  ["GET /api/platform/global/plan", apiGlobalPlanGet],
  ["POST /api/platform/global/plan", apiGlobalPlanPost],
  ["PUT /api/platform/global/plan", apiGlobalPlanPut],
  ["GET /api/platform/global/tenant", apiGlobalTenantConfig],
  ["POST /api/platform/global/tenant/country", apiGlobalTenantCountry],
  ["POST /api/platform/global/tenant/currency", apiGlobalTenantCurrency],
  ["GET /api/platform/global/tenant/providers", apiGlobalTenantProviders],
  ["POST /api/platform/global/tenant/provider", apiGlobalTenantProviderPost],
  ["DELETE /api/platform/global/tenant/provider", apiGlobalTenantProviderDelete],
  ["POST /api/platform/global/tenant/plan", apiGlobalTenantPlan],
  ["POST /api/coupon", apiCoupon],
  ["POST /api/auth/register", apiRegister],
  ["POST /api/auth/login", apiLogin],
  ["POST /api/auth/logout", apiLogout],
  ["POST /api/auth/token-exchange", apiTokenExchange],
  ["GET /api/products", apiProducts],
  ["GET /api/search", apiSearch],
  ["GET /api/suggest", apiSuggest],
  ["GET /api/recommend", apiRecommend],
  ["GET /api/shipments", apiShipments],
  ["GET /api/shipments/:id", (r, re, u, s, b, p) => apiShipment(r, re, u, s, b, p)],
  ["POST /api/admin/shipments", apiShipmentCreate],
  ["PUT /api/admin/shipments/:id/status", (r, re, u, s, b, p) => apiShipmentStatus(r, re, u, s, b, p)],
  ["POST /api/admin/warehouses/route", (r, re, u, s, b) => apiWarehouseRoute(r, re, u, s, b)],
  ["GET /api/admin/sla", apiSlaBreaches],
  ["PUT /api/admin/returns/:id/disposition", (r, re, u, s, b, p) => apiReturnDisposition(r, re, u, s, b, p)],
  ["GET /api/carriers", apiCarriers],
  ["GET /api/admin/fin/disputes", apiFinDisputes],
  ["POST /api/admin/fin/disputes", apiFinDisputeOpen],
  ["PUT /api/admin/fin/disputes/:id", (r, re, u, s, b, p) => apiFinDisputeStatus(r, re, u, s, b, p)],
  ["POST /api/admin/fin/payments/:id/retry", (r, re, u, s, b, p) => apiFinRetry(r, re, u, s, b, p)],
  ["GET /api/admin/fin/payouts", apiFinPayouts],
  ["POST /api/admin/fin/payouts", apiFinPayoutOpen],
  ["POST /api/admin/fin/payouts/:id/disburse", (r, re, u, s, b, p) => apiFinPayoutDisburse(r, re, u, s, b, p)],
  ["POST /api/admin/fin/reconcile", apiFinReconcile],
  ["GET /api/admin/fin/ledger", apiFinLedger],
  ["GET /api/marketplace/ads", apiMktAds],
  ["POST /api/admin/marketplace/ads", apiMktAdCreate],
  ["GET /api/marketplace/rank", apiMktRank],
  ["POST /api/marketplace/ads/:id/event", (r, re, u, s, b, p) => apiMktEvent(r, re, u, s, b, p)],
  ["POST /api/admin/marketplace/attribute", apiMktAttribute],
  ["GET /api/admin/marketplace/metrics", apiMktSellerMetrics],
  ["POST /api/admin/marketplace/settle", apiMktSettle],
  ["GET /api/products/:id", apiProduct],
  ["GET /api/cart", apiCartGet],
  ["POST /api/cart", apiCartAdd],
  ["PUT /api/cart", apiCartPut],
  ["DELETE /api/cart/:id", (r, re, u, s, b, p) => apiCartDel(r, re, u, s, b, p)],
  ["POST /api/saved", apiSavedAdd],
  ["DELETE /api/saved/:id", (r, re, u, s, b, p) => apiSavedDel(r, re, u, s, b, p)],
  ["POST /api/saved/:id/move", (r, re, u, s, b, p) => apiSavedMove(r, re, u, s, b, p)],
  ["GET /api/orders", apiOrders],
  ["POST /api/checkout", apiCheckout],
  ["POST /api/checkout/quote", apiCheckoutQuote],
  ["POST /api/reviews/:id", (r, re, u, s, b, p) => apiReviewAdd(r, re, u, s, b, p)],
  ["POST /api/reviews/:id/vote", (r, re, u, s, b, p) => apiReviewVote(r, re, u, s, b, p)],
  ["POST /api/reviews/:id/reply", (r, re, u, s, b, p) => apiReviewReply(r, re, u, s, b, p)],
  ["PUT /api/admin/reviews/:id/moderate", (r, re, u, s, b, p) => apiReviewModerate(r, re, u, s, b, p)],
  ["GET /api/admin/ugc/queue", apiAdminUgcQueue],
  ["POST /api/qna/:id/question", (r, re, u, s, b, p) => apiQnaAsk(r, re, u, s, b, p)],
  ["POST /api/qna/question/:id/answer", (r, re, u, s, b, p) => apiQnaAnswer(r, re, u, s, b, p)],
  ["POST /api/qna/:id/vote", (r, re, u, s, b, p) => apiQnaVote(r, re, u, s, b, p)],
  ["PUT /api/admin/qna/:id/moderate", (r, re, u, s, b, p) => apiQnaModerate(r, re, u, s, b, p)],
  ["POST /api/support/tickets", apiSupportCreate],
  ["GET /api/support/tickets", apiSupportList],
  ["GET /api/support/tickets/:id", (r, re, u, s, b, p) => apiSupportGet(r, re, u, s, b, p)],
  ["POST /api/support/tickets/:id/reply", (r, re, u, s, b, p) => apiSupportReply(r, re, u, s, b, p)],
  ["POST /api/support/tickets/:id/csat", (r, re, u, s, b, p) => apiSupportCsat(r, re, u, s, b, p)],
  ["GET /api/admin/helpdesk/tickets", apiAdminHdList],
  ["GET /api/admin/helpdesk/tickets/:id", (r, re, u, s, b, p) => apiAdminHdGet(r, re, u, s, b, p)],
  ["PUT /api/admin/helpdesk/tickets/:id", (r, re, u, s, b, p) => apiAdminHdUpdate(r, re, u, s, b, p)],
  ["POST /api/admin/helpdesk/tickets/:id/reply", (r, re, u, s, b, p) => apiAdminHdReply(r, re, u, s, b, p)],
  ["GET /api/admin/helpdesk/sla", apiAdminHdSla],
  ["GET /api/addresses", apiAddressList],
  ["POST /api/addresses", apiAddressSave],
  ["PUT /api/addresses/:id", (r, re, u, s, b, p) => apiAddressSave(r, re, u, s, b, p)],
  ["DELETE /api/addresses/:id", (r, re, u, s, b, p) => apiAddressDel(r, re, u, s, b, p)],
  ["POST /api/subscriptions", apiSubCreate],
  ["GET /api/subscriptions", apiSubList],
  ["PUT /api/subscriptions/:id", (r, re, u, s, b, p) => apiSubControl(r, re, u, s, b, p)],
  ["GET /api/admin/recurring", apiAdminRecurring],
  ["POST /api/admin/recurring/process", apiAdminRecurringProcess],
  ["GET /api/membership", apiMembershipGet],
  ["POST /api/membership/subscribe", apiMembershipSubscribe],
  ["POST /api/membership/cancel", apiMembershipCancel],
  ["GET /api/admin/memberships", apiAdminMemberships],
  ["POST /api/admin/risk/screen", apiRiskScreen],
  ["GET /api/admin/risk/blocklist", apiRiskBlocklist],
  ["POST /api/admin/risk/blocklist", apiRiskBlockAdd],
  ["GET /api/admin/risk/queue", apiRiskQueue],
  ["PUT /api/admin/risk/:id/resolve", (r, re, u, s, b, p) => apiRiskResolve(r, re, u, s, b, p)],
  ["GET /api/experiments/:id/assign", (r, re, u, s, b, p) => apiExpAssign(r, re, u, s, b, p)],
  ["POST /api/experiments/:id/convert", (r, re, u, s, b, p) => apiExpConvert(r, re, u, s, b, p)],
  ["GET /api/admin/experiments", apiAdminExpList],
  ["POST /api/admin/experiments", apiAdminExpCreate],
  ["PUT /api/admin/experiments/:id/status", (r, re, u, s, b, p) => apiAdminExpStatus(r, re, u, s, b, p)],
  ["GET /api/admin/experiments/:id/results", (r, re, u, s, b, p) => apiAdminExpResults(r, re, u, s, b, p)],
  ["GET /api/admin/planning", apiAdminPlanList],
  ["POST /api/admin/planning/run", apiAdminPlanRun],
  ["PUT /api/admin/planning/:id", (r, re, u, s, b, p) => apiAdminPlanStatus(r, re, u, s, b, p)],
  ["POST /api/admin/planning/approve-all", apiAdminPlanApproveAll],
  ["GET /api/admin/planning/pos", apiAdminPlanPos],
  /* E17 · mobility — the ride-hailing / dispatch surface. Each route is gated on its
     own atom, so a store with only ride_hailing on gets the rides surface and nothing
     else, and a store with none of them refuses the whole block. */
  ["GET /api/admin/mobility", apiMobilityGet],
  ["POST /api/admin/mobility/rides", apiMobilityRide],
  ["PUT /api/admin/mobility/rides/:id", (r, re, u, s, b, p) => apiMobilityRideStatus(r, re, u, s, b, p)],
  ["POST /api/admin/mobility/rides/:id/rate", (r, re, u, s, b, p) => apiMobilityRate(r, re, u, s, b, p)],
  ["POST /api/admin/mobility/drivers", apiMobilityDriver],
  ["POST /api/admin/mobility/drivers/:id/toggle", (r, re, u, s, b, p) => apiMobilityDriverToggle(r, re, u, s, b, p)],
  ["POST /api/admin/mobility/drivers/:id/deactivate", (r, re, u, s, b, p) => apiMobilityDriverDeactivate(r, re, u, s, b, p)],
  ["POST /api/admin/mobility/vehicles", apiMobilityVehicle],
  ["POST /api/admin/mobility/zones", apiMobilityZone],
  /* E18 · operations — the ERP surface. Each route is gated on its own atom, so a
     store composing only workforce gets HRMS/payroll and nothing else. */
  ["GET /api/admin/operations", apiOpsGet],
  ["POST /api/admin/ops/employees", apiOpsEmployee],
  ["POST /api/admin/ops/attendance", apiOpsAttendance],
  ["POST /api/admin/ops/payroll/run", apiOpsPayrollRun],
  ["PUT /api/admin/ops/payroll/:id", (r, re, u, s, b, p) => apiOpsPayrollStatus(r, re, u, s, b, p)],
  ["POST /api/admin/ops/requests", apiOpsRequest],
  ["PUT /api/admin/ops/requests/:id", (r, re, u, s, b, p) => apiOpsRequestAdvance(r, re, u, s, b, p)],
  ["POST /api/admin/ops/work-orders", apiOpsWorkOrder],
  ["POST /api/admin/ops/work-orders/:id/complete", (r, re, u, s, b, p) => apiOpsWorkOrderComplete(r, re, u, s, b, p)],
  ["POST /api/admin/ops/projects", apiOpsProject],
  ["POST /api/admin/ops/tasks", apiOpsTask],
  ["POST /api/admin/ops/tasks/:id/time", (r, re, u, s, b, p) => apiOpsTime(r, re, u, s, b, p)],
  ["PUT /api/admin/ops/approvals/:id", (r, re, u, s, b, p) => apiOpsApprovalDecide(r, re, u, s, b, p)],
  ["POST /api/giftcard", apiGiftAdd],
  ["POST /api/viewed", apiViewed],
  ["GET /api/admin/stats", apiAdminStats],
  ["GET /api/admin/products", apiAdminProducts],
  ["GET /api/admin/products/:id", (r, re, u, s, b, p) => apiAdminProductGet(r, re, u, s, b, p)],
  ["POST /api/admin/products", apiAdminProductCreate],
  ["PUT /api/admin/products/:id", (r, re, u, s, b, p) => apiAdminProductUpdate(r, re, u, s, b, p)],
  ["PUT /api/admin/products/:id/meta", (r, re, u, s, b, p) => apiAdminProductSaveMeta(r, re, u, s, b, p)],
  ["POST /api/admin/products/:id/lifecycle", (r, re, u, s, b, p) => apiAdminLifecycle(r, re, u, s, b, p)],
  ["POST /api/admin/products/:id/relationships", (r, re, u, s, b, p) => apiAdminRelationshipAdd(r, re, u, s, b, p)],
  ["DELETE /api/admin/products/:id", (r, re, u, s, b, p) => apiAdminProductDelete(r, re, u, s, b, p)],
  ["GET /api/admin/taxonomy", apiAdminTaxonomy],
  ["POST /api/admin/taxonomy", (r, re, u, s, b, p) => apiAdminTaxSave(r, re, u, s, b, p)],
  ["PUT /api/admin/taxonomy/:id", (r, re, u, s, b, p) => apiAdminTaxSave(r, re, u, s, b, p)],
  ["DELETE /api/admin/taxonomy/:id", (r, re, u, s, b, p) => apiAdminTaxDelete(r, re, u, s, b, p)],
  ["GET /api/admin/attributes", apiAdminAttributes],
  ["POST /api/admin/attributes", apiAdminAttrSave],
  ["DELETE /api/admin/attributes/:key", (r, re, u, s, b, p) => apiAdminAttrDelete(r, re, u, s, b, p)],
  ["POST /api/admin/skus", (r, re, u, s, b, p) => apiAdminSkuSave(r, re, u, s, b, p)],
  ["PUT /api/admin/skus/:id", (r, re, u, s, b, p) => apiAdminSkuSave(r, re, u, s, b, p)],
  ["DELETE /api/admin/skus/:id", (r, re, u, s, b, p) => apiAdminSkuDelete(r, re, u, s, b, p)],
  ["PUT /api/admin/inventory/:id", (r, re, u, s, b, p) => apiAdminInventoryPut(r, re, u, s, b, p)],
  ["DELETE /api/admin/relationships/:id", (r, re, u, s, b, p) => apiAdminRelationshipDelete(r, re, u, s, b, p)],
  ["GET /api/admin/warehouses", apiAdminWarehouses],
  ["POST /api/admin/warehouses", (r, re, u, s, b, p) => apiAdminWarehouseSave(r, re, u, s, b, p)],
  ["PUT /api/admin/warehouses/:id", (r, re, u, s, b, p) => apiAdminWarehouseSave(r, re, u, s, b, p)],
  ["GET /api/admin/promotions", apiAdminPromotions],
  ["POST /api/admin/promotions", (r, re, u, s, b, p) => apiAdminPromoSave(r, re, u, s, b, p)],
  ["PUT /api/admin/promotions/:id", (r, re, u, s, b, p) => apiAdminPromoSave(r, re, u, s, b, p)],
  ["DELETE /api/admin/promotions/:id", (r, re, u, s, b, p) => apiAdminPromoDelete(r, re, u, s, b, p)],
  ["GET /api/admin/sellers", apiAdminSellers],
  ["POST /api/admin/sellers", (r, re, u, s, b, p) => apiAdminSellerSave(r, re, u, s, b, p)],
  ["PUT /api/admin/sellers/:id", (r, re, u, s, b, p) => apiAdminSellerSave(r, re, u, s, b, p)],
  ["DELETE /api/admin/sellers/:id", (r, re, u, s, b, p) => apiAdminSellerDelete(r, re, u, s, b, p)],
  ["GET /api/admin/rfqs", apiAdminRfqs],
  ["PUT /api/admin/rfqs/:id", (r, re, u, s, b, p) => apiAdminRfqUpdate(r, re, u, s, b, p)],
  ["GET /api/admin/returns", apiAdminReturns],
  ["PUT /api/admin/returns/:id", (r, re, u, s, b, p) => apiAdminReturnUpdate(r, re, u, s, b, p)],
  ["GET /api/admin/settlements", apiAdminSettlements],
  ["POST /api/admin/settlements/generate", apiAdminSettlementGenerate],
  ["GET /api/admin/analytics", apiAdminAnalytics],
  ["PUT /api/admin/mode", apiAdminModePut],
  ["GET /api/admin/orders", apiAdminOrders],
  ["PUT /api/admin/orders/:id/status", (r, re, u, s, b, p) => apiAdminOrderStatus(r, re, u, s, b, p)],
  ["GET /api/admin/users", apiAdminUsers],
  ["DELETE /api/admin/users/:id", (r, re, u, s, b, p) => apiAdminUserDelete(r, re, u, s, b, p)],
  ["GET /api/admin/reviews", apiAdminReviews],
  ["DELETE /api/admin/reviews/:id", (r, re, u, s, b, p) => apiAdminReviewDelete(r, re, u, s, b, p)],
  /* compliance & privacy — named regulations as data, computed verdicts, consent ledger,
     data-subject-rights workflow */
  ["GET /api/admin/compliance/status", apiAdminComplianceStatus],
  ["GET /api/admin/compliance/catalog", apiAdminComplianceCatalog],
  ["POST /api/admin/compliance/control", apiAdminComplianceControl],
  ["GET /api/admin/compliance/evidence", apiAdminComplianceEvidence],
  ["GET /api/consent", apiConsentGet],
  ["POST /api/consent", apiConsentSet],
  ["POST /api/privacy/request", apiPrivacyRequestOpen],
  ["GET /api/admin/privacy/requests", apiAdminPrivacyRequests],
  ["POST /api/admin/privacy/requests/:id", (r, re, u, s, b, p) => apiAdminPrivacyRequestTransition(r, re, u, s, b, p)],
  ["GET /api/admin/privacy/requests/:id/events", (r, re, u, s, b, p) => apiAdminPrivacyRequestEvents(r, re, u, s, b, p)],
  /* tenancy hierarchy — the tenant's own org structure (org → BU → brand → store → channel).
     Every node is data, the path is materialized, and the tree is the config cascade.
     Scoped to the session's tenant; the platform reads it via the generic cross-store reader */
  ["GET /api/tenancy/tree", apiTenancyTree],
  ["GET /api/tenancy/nodes", apiTenancyList],
  ["POST /api/tenancy/node", apiTenancyCreate],
  ["PUT /api/tenancy/node/:id", apiTenancyUpdate],
  ["DELETE /api/tenancy/node/:id", apiTenancyDelete],
  ["GET /api/tenancy/resolve/:id", apiTenancyResolve],
  ["POST /api/tenancy/config/:id/:key", apiTenancyConfigSet],
  /* the composition engine — the platform composes a declared capability into its full
     application surface (data model · API · workflow · UI · dashboard · security) with no
     per-capability code. Platform-only: composing creates platform-wide machinery */
  ["GET /api/compose/candidates", apiComposeCandidates],
  ["GET /api/compose/ledger", apiComposeLedger],
  ["GET /api/compose/:key", apiComposeManifest],
  ["POST /api/compose/:key", apiCompose],
  ["POST /api/compose/:key/recompose", apiRecompose],
  ["GET /api/admin/settings", apiAdminSettingsGet],
  ["PUT /api/admin/settings", apiAdminSettingsPut],
  ["POST /api/admin/settings/reset", apiAdminSettingsReset],
  ["GET /api/admin/departments", apiAdminDepartments],
  ["POST /api/admin/departments", apiAdminDeptSave],
  ["DELETE /api/admin/departments/:key", (r, re, u, s, b, p) => apiAdminDeptDelete(r, re, u, s, b, p)],
  ["GET /api/admin/banners", apiAdminBanners],
  ["POST /api/admin/banners", (r, re, u, s, b, p) => apiAdminBannerSave(r, re, u, s, b, p)],
  ["PUT /api/admin/banners/:id", (r, re, u, s, b, p) => apiAdminBannerSave(r, re, u, s, b, p)],
  ["DELETE /api/admin/banners/:id", (r, re, u, s, b, p) => apiAdminBannerDelete(r, re, u, s, b, p)],
  ["GET /api/admin/cards", apiAdminCards],
  ["POST /api/admin/cards", (r, re, u, s, b, p) => apiAdminCardSave(r, re, u, s, b, p)],
  ["PUT /api/admin/cards/:id", (r, re, u, s, b, p) => apiAdminCardSave(r, re, u, s, b, p)],
  ["DELETE /api/admin/cards/:id", (r, re, u, s, b, p) => apiAdminCardDelete(r, re, u, s, b, p)],
  ["PUT /api/admin/account", apiAdminAccount],
  ["GET /api/admin/gateways", apiAdminGateways],
  ["PUT /api/admin/gateways", apiAdminGatewaysPut],
  ["POST /api/admin/gateways/:id/test", (r, re, u, s, b, p) => apiAdminGatewayTest(r, re, u, s, b, p)],
  ["GET /api/admin/ai-gateways", apiAdminAiGateways],
  ["PUT /api/admin/ai-gateways", apiAdminAiGatewaysPut],
  ["POST /api/admin/ai-gateways/:id/test", (r, re, u, s, b, p) => apiAdminAiGatewayTest(r, re, u, s, b, p)],
  ["GET /api/admin/payments", apiAdminPayments],
  ["GET /api/branding", apiStoreBranding],
  ["PUT /api/branding", apiStoreBranding],
  ["GET /api/platform/branding", apiPlatformBranding],
  ["PUT /api/platform/branding", apiPlatformBranding],
  ["GET /api/platform/branding-permissions/:id", apiPlatformBrandingPerms],
  ["GET /api/platform/identity-templates", apiIdentityTemplates],  ["POST /api/platform/identity-templates", apiIdentityTemplates],
  ["DELETE /api/platform/identity-templates/:id", apiIdentityTemplates],
  ["GET /api/platform/identity-templates/:id", apiIdentityTemplate],
  ["PUT /api/platform/identity-templates/:id", apiIdentityTemplate],
  ["POST /api/platform/identity-templates/:id/apply", apiIdentityTemplateApply],
  /* platform registry authoring: every meta_lists vocabulary, auto-discovered.
     Segment counts differ, so :name/recommend and :name/:key never collide with :name */
  ["GET /api/platform/registries", apiPlatformRegistries],
  ["GET /api/platform/registries/:name", apiPlatformRegistry],
  ["POST /api/platform/registries/:name", apiPlatformRegistry],
  ["POST /api/platform/registries/:name/recommend", apiPlatformRegistryRecommend],
  ["DELETE /api/platform/registries/:name/:key", apiPlatformRegistryEntryDelete],
  ["GET /api/platform/policies", apiPlatformPolicies],
  ["GET /api/platform/policies/:category", apiPlatformPolicy],
  ["PUT /api/platform/policies/:category", apiPlatformPolicy],
  ["DELETE /api/platform/policies/:category", apiPlatformPolicy],
  ["PUT /api/platform/branding-permissions/:id", apiPlatformBrandingPerms],
  ["POST /api/admin/payments/:id/refund", (r, re, u, s, b, p) => apiAdminPaymentRefund(r, re, u, s, b, p)],
  ["POST /api/admin/payments/:id/reconcile", (r, re, u, s, b, p) => apiAdminPaymentReconcile(r, re, u, s, b, p)],
  ["POST /api/admin/payments/:id/received", (r, re, u, s, b, p) => apiAdminPaymentReceived(r, re, u, s, b, p)],
  ["GET /api/admin/billing", apiAdminBilling],
  ["GET /api/admin/audit", apiAdminAudit],
  ["GET /api/admin/entity-usage", apiAdminEntityUsage],
  ["GET /api/admin/monitor", apiAdminMonitor],
  ["GET /api/admin/custom-providers", apiAdminCustomProviders],
  ["POST /api/admin/custom-providers", apiAdminCustomProviderAdd],
  ["DELETE /api/admin/custom-providers/:id", (r, re, u, s, b, p) => apiAdminCustomProviderDelete(r, re, u, s, b, p)],
  ["POST /api/admin/contracts", apiAdminContractCreate],
  ["PUT /api/admin/contracts/:id/status", (r, re, u, s, b, p) => apiAdminContractStatus(r, re, u, s, b, p)],
  ["POST /api/admin/tenders", apiAdminTenderCreate],
  ["POST /api/admin/tenders/:id/award", (r, re, u, s, b, p) => apiAdminTenderAward(r, re, u, s, b, p)],
  ["POST /api/admin/rfqs/:id/contract", (r, re, u, s, b, p) => apiAdminRfqToContract(r, re, u, s, b, p)],
  ["POST /api/admin/serialized/bulk", apiAdminSerializedBulk],
  ["GET /api/ai", apiAiOverview],
  ["POST /api/ai/run/:capability", (r, re, u, s, b, p) => apiAiRun(r, re, u, s, b, p)],
  ["GET /api/ai/usage", apiAiUsage],
  ["GET /api/ai/tasks", apiAiTasks],
  ["POST /api/ai/tasks", apiAiTaskCreate],
  ["POST /api/ai/tasks/:id/run", (r, re, u, s, b, p) => apiAiTaskRun(r, re, u, s, b, p)],
  ["GET /api/platform/ai", apiPlatformAi],
  ["GET /api/platform/db", apiPlatformDb],
  ["POST /api/platform/db/ping", apiDbPing],
  ["POST /api/platform/db/apply", apiDbApply],
  ["POST /api/platform/db/switch", apiDbSwitch],
  ["POST /api/admin/gateway/preview/:id", (r, re, u, s, b, p) => apiGatewayPreview(r, re, u, s, b, p)],
  ["POST /api/webhooks/inbound/:provider", (r, re, u, s, b, p) => apiInboundWebhook(r, re, u, s, b, p)],
  ["GET /api/admin/sso", apiSsoGet], ["PUT /api/admin/sso", apiSsoSet], ["POST /api/auth/sso/start", apiSsoStart], ["POST /api/auth/sso/callback", apiSsoCallback],
  ["GET /api/admin/identity-providers", apiIdentityProvidersGet], ["PUT /api/admin/identity-providers", apiIdentityProvidersPut], ["DELETE /api/admin/identity-providers/:id", apiIdentityProviderDelete],
  ["GET /api/admin/identity-provider-types", apiIdentityProviderTypes],
  ["POST /api/admin/identity-provider-types", apiIdentityProviderTypeCreate],
  ["GET /api/admin/identity-settings", apiIdentitySettingsGet], ["PUT /api/admin/identity-settings", apiIdentitySettingsPut],
  ["POST /api/auth/password/forgot", apiPasswordForgot], ["POST /api/auth/password/reset", apiPasswordReset],
  ["POST /api/auth/login-init", apiLoginInit], ["POST /api/auth/login/otp", apiLoginOtpVerify], ["POST /api/auth/login/magic", apiLoginMagicLinkVerify], ["POST /api/auth/login/biometric", apiLoginBiometricVerify], ["POST /api/auth/biometric/register", apiBiometricRegister],
  ["POST /api/auth/login/callback", apiLoginCallback], ["GET /api/auth/methods", apiAuthMethods],
  ["GET /api/user/identity-methods", apiIdentityMethodsGet], ["POST /api/user/identity-methods", apiIdentityMethodsLink], ["DELETE /api/user/identity-methods/:id", apiIdentityMethodsUnlink], ["PUT /api/user/identity-methods/:id/primary", apiIdentityMethodsSetPrimary],
  ["GET /api/platform/regions", apiRegionsGet], ["PUT /api/platform/regions", apiRegionsSet],
  ["GET /api/feeds/:slug", apiFeeds],
  ["GET /api/admin/transfers", apiTransfers], ["POST /api/admin/transfers", apiTransferCreate],
  ["GET /api/admin/tax/report", apiTaxReport],
  ["GET /api/scim/Users", apiScimUsersList], ["POST /api/scim/Users", apiScimUserCreate],
  ["POST /api/admin/scim/token", apiScimToken],
  ["GET /api/offers", apiOffersList],
  ["POST /api/offers", (r, re, u, s, b) => apiOfferSave(r, re, u, s, b, null)],
  ["PUT /api/offers/:id", (r, re, u, s, b, p) => apiOfferSave(r, re, u, s, b, p)],
  ["DELETE /api/offers/:id", (r, re, u, s, b, p) => apiOfferDelete(r, re, u, s, b, p)],
  ["POST /api/offers/preview", apiOffersPreview],
  ["GET /api/offers/analytics", apiOffersAnalytics],
  ["GET /api/offers/coupons", apiCouponsList],
  ["POST /api/offers/coupons", apiCouponCreate],
  ["POST /api/offers/coupons/generate", apiCouponGenerate],
  ["DELETE /api/offers/coupons/:id", (r, re, u, s, b, p) => apiCouponVoid(r, re, u, s, b, p)],
  ["GET /api/wallet/ledger", apiWalletLedger],
  ["GET /api/platform/offers", apiPlatformOffers],
  /* GOIP Ω∞ — capability router + read surfaces */
  ["GET /api/goip", apiGoipManifest],
  ["GET /api/goip/exchanges", apiGoipExchanges],
  ["GET /api/goip/exchanges/:id", (r, re, u, s, b, p) => apiGoipExchange(r, re, u, s, b, p)],
  ["GET /api/goip/context", apiGoipContext],
  ["GET /api/goip/treasury", apiGoipTreasury],
  ["GET /api/goip/settlements", apiGoipSettlements],
  ["GET /api/goip/entitlements", apiGoipEntitlements],
  ["GET /api/goip/touchpoints", apiGoipTouchpoints],
  ["GET /api/goip/widget", apiGoipWidget],
  ["GET /api/goip/registry/:name", (r, re, u, s, b, p) => apiGoipRegistry(r, re, u, s, b, p)],
  ["GET /api/goip/intelligence/:key", (r, re, u, s, b, p) => apiGoipIntelligence(r, re, u, s, b, p)],
  ["GET /api/goip/feed/:channel", (r, re, u, s, b, p) => apiGoipFeed(r, re, u, s, b, p)],
  ["POST /api/goip/:capability", (r, re, u, s, b, p) => apiGoipCapability(r, re, u, s, b, p)],
  ["GET /api/platform/runtime", apiPlatformRuntime],
  ["PUT /api/platform/runtime", apiPlatformRuntimePut],
  ["POST /api/platform/runtime/test", apiPlatformRuntimeTest],
  ["POST /api/platform/queue/drain", apiPlatformQueueDrain],
  ["GET /api/platform/environments", apiEnvList],
  ["POST /api/platform/environments", (r, re, u, s, b, p) => apiEnvUpsert(r, re, u, s, b, (u.searchParams.get("name") || (b && b.name)))],
  ["GET /api/platform/environments/:name", (r, re, u, s, b, p) => apiEnvGet(r, re, u, s, b, p)],
  ["PUT /api/platform/environments/:name", (r, re, u, s, b, p) => apiEnvUpsert(r, re, u, s, b, p)],
  ["DELETE /api/platform/environments/:name", (r, re, u, s, b, p) => apiEnvDelete(r, re, u, s, b, p)],
  ["POST /api/platform/environments/:name/activate", (r, re, u, s, b, p) => apiEnvActivate(r, re, u, s, b, p)],
  ["GET /api/platform/environments-export", apiEnvExport],
  ["POST /api/platform/environments-import", apiEnvImport],
  ["GET /api/platform/flags", apiFlags],
  ["PUT /api/platform/flags/:name", (r, re, u, s, b, p) => apiFlagSet(r, re, u, s, b, p)],
  ["DELETE /api/platform/flags/:name", (r, re, u, s, b, p) => apiFlagDelete(r, re, u, s, b, p)],
  ["GET /api/env/tenant", apiEnvTenant],
  ["POST /api/admin/export/:kind", (r, re, u, s, b, p) => apiAdminExport(r, re, u, s, b, p)],
  ["POST /api/platform/login", apiPlatformLogin],
  ["POST /api/platform/logout", apiPlatformLogout],
  ["GET /api/platform/me", apiPlatformMe],
  ["GET /api/auth/me", apiAuthMe],
  ["GET /api/platform/security", apiPlatformSecurity],
  ["GET /api/platform/modules", apiPlatformModules],
  ["POST /api/platform/modules/:id/install", (r, re, u, s, b, p) => apiModuleInstall(r, re, u, s, b, p)],
  ["POST /api/platform/modules/:id/uninstall", (r, re, u, s, b, p) => apiModuleUninstall(r, re, u, s, b, p)],
  ["POST /api/platform/modules/:id/configure", (r, re, u, s, b, p) => apiModuleConfigure(r, re, u, s, b, p)],
  ["GET /api/modules", apiStoreModules],
  ["GET /api/market", apiMarket],
  ["POST /api/modules/purchase", apiModulePurchase],
  ["POST /api/modules/release", apiModuleRelease],
  ["GET /api/seo/sitemap.xml", apiSeoSitemap],
  ["GET /api/reco/:id", (r, re, u, s, b, p) => apiReco(r, re, u, s, b, p)],
  ["GET /api/facets", apiFacets],
  ["POST /api/billing/invoices/:id/pay", (r, re, u, s, b, p) => apiBillingPay(r, re, u, s, b, p)],
  ["GET /api/platform/config", apiPlatformConfigGet],
  ["PUT /api/platform/config", apiPlatformConfigPut],
  ["GET /api/platform/chain/verify", apiPlatformChainVerify],
  ["POST /api/platform/keys/rotate", apiPlatformKeyRotate],
  ["GET /api/admin/chain/verify", apiAdminChainVerify],
  ["GET /api/platform/tenants", apiPlatformTenants],
  ["GET /api/platform/kinds", apiPlatformKinds],
  ["POST /api/platform/kinds", apiPlatformKindSave],
  ["DELETE /api/platform/kinds/:key", (r, re, u, s, b, p) => apiPlatformKindDelete(r, re, u, s, b, p)],
  ["GET /api/platform/tenants/:id/setup", (r, re, u, s, b, p) => apiPlatformTenantSetup(r, re, u, s, b, p)],
  ["POST /api/platform/tenants", apiPlatformTenantCreate],
  ["PUT /api/platform/tenants/:id", (r, re, u, s, b, p) => apiPlatformTenantUpdate(r, re, u, s, b, p)],
  ["DELETE /api/platform/tenants/:id", (r, re, u, s, b, p) => apiPlatformTenantDelete(r, re, u, s, b, p)],
  ["POST /api/platform/tenants/:id/impersonate", (r, re, u, s, b, p) => apiPlatformImpersonate(r, re, u, s, b, p)],
  ["GET /api/platform/plans", apiPlatformPlans],
  ["POST /api/platform/plans", (r, re, u, s, b, p) => apiPlatformPlanSave(r, re, u, s, b, p)],
  ["PUT /api/platform/plans/:id", (r, re, u, s, b, p) => apiPlatformPlanSave(r, re, u, s, b, p)],
  ["POST /api/platform/tenants/:id/subscribe", (r, re, u, s, b, p) => apiPlatformSubscribe(r, re, u, s, b, p)],
  ["GET /api/platform/invoices", apiPlatformInvoices],
  ["POST /api/platform/tenants/:id/invoice", (r, re, u, s, b, p) => apiPlatformInvoiceGenerate(r, re, u, s, b, p)],
  ["POST /api/platform/invoices/:id/refund", (r, re, u, s, b, p) => apiPlatformInvoiceRefund(r, re, u, s, b, p)],
  ["POST /api/platform/billing/dunning", apiPlatformDunning],
  ["GET /api/platform/billing/aging", apiPlatformAging],
  ["POST /api/platform/usage", apiPlatformUsage],
  ["GET /api/admin/billing/detail", apiAdminBillingDetail],
  ["GET /api/admin/tax", apiAdminTaxConfig],
  ["POST /api/admin/tax/quote", apiAdminTaxQuote],
  ["GET /api/marketing/providers", apiMarketingProviders],
  ["POST /api/marketing/save", apiMarketingSave],
  ["POST /api/marketing/send", apiMarketingSend],
  ["GET /api/admin/webhooks", apiWebhooksList],
  ["POST /api/admin/webhooks", apiWebhookCreate],
  ["PUT /api/admin/webhooks/:id", (r, re, u, s, b, p) => apiWebhookUpdate(r, re, u, s, b, p)],
  ["DELETE /api/admin/webhooks/:id", (r, re, u, s, b, p) => apiWebhookDelete(r, re, u, s, b, p)],
  ["POST /api/admin/webhooks/:id/test", (r, re, u, s, b, p) => apiWebhookTest(r, re, u, s, b, p)],
  ["POST /api/admin/webhooks/drain", apiWebhookDrain],
  /* Affiliate Network */
  ["GET /api/affiliate/networks", apiAffiliateNetworks],
  ["POST /api/affiliate/networks", apiAffiliateNetworkCreate],
  ["GET /api/affiliate/affiliates", apiAffiliateList],
  ["POST /api/affiliate/affiliates", apiAffiliateCreate],
  ["GET /api/affiliate/affiliates/:id", apiAffiliateGet],
  ["PUT /api/affiliate/affiliates/:id", apiAffiliateUpdate],
  ["POST /api/affiliate/click", apiAffiliateClick],
  ["POST /api/affiliate/conversion", apiAffiliateConversion],
  ["GET /api/affiliate/conversions/:id", apiAffiliateConversionGet],
  ["POST /api/affiliate/conversions/:id/approve", apiAffiliateApprove],
  ["POST /api/affiliate/conversions/:id/reject", apiAffiliateReject],
  ["GET /api/affiliate/payouts", apiAffiliatePayouts],
  ["POST /api/affiliate/payouts", apiAffiliatePayoutCreate],
  ["POST /api/affiliate/payouts/:id/process", apiAffiliatePayoutProcess],
  ["GET /api/affiliate/reports", apiAffiliateReport],
  
  /* Sitemap (SEO) */
  ["GET /api/sitemap", apiSitemap],
  ["GET /api/sitemap.xml", apiSitemapXML],
  ["POST /api/sitemap/generate", apiSitemapGenerate],
  ["GET /api/sitemap/config", apiSitemapConfig],
  ["PUT /api/sitemap/config", apiSitemapConfigUpdate],
  
  /* Shipping & Tracking */
  ["GET /api/shipping/providers", apiShippingProviders],
  ["POST /api/shipping/providers/config", apiShippingProviderConfig],
  ["GET /api/platform/shipping/providers", apiPlatformShippingProviders],
  ["POST /api/platform/shipping/providers/:id/disconnect", (r, re, u, s, b, p) => apiPlatformShippingDisconnect(r, re, u, s, b, p)],
  ["POST /api/shipping/track", apiShippingTrack],
  ["GET /api/shipping/track/:trackingNumber", apiShippingTrackGet],
  ["POST /api/shipping/quote", apiShippingQuote],
  ["POST /api/shipping/label", apiShippingLabel],
  ["GET /api/shipping/orders/:id/labels", (r, re, u, s, b, p) => apiShippingOrderLabels(r, re, u, s, b, p)],
  ["POST /api/shipping/webhook/:provider", (r, re, u, s, b, p) => apiShippingWebhook(r, re, u, s, b, p)],
  
  /* Enhanced Helpdesk */
  ["GET /api/helpdesk/channels", apiHelpdeskChannels],
  ["POST /api/helpdesk/chat", apiHelpdeskChat],
  ["POST /api/helpdesk/sms", apiHelpdeskSMS],
  ["POST /api/helpdesk/:ticketId/message", apiHelpdeskMessage],
  ["GET /api/helpdesk/agents/status", apiHelpdeskAgentStatus],
  ["POST /api/helpdesk/agents/status", apiHelpdeskAgentStatusUpdate],
  
  ["GET /api/admin/entity-meta", apiEntityTags],
  ["PUT /api/admin/entity-meta", apiEntityTagsSave],
  ["POST /api/platform/invoices/:id/pay", (r, re, u, s, b, p) => apiPlatformInvoicePay(r, re, u, s, b, p)],
  ["GET /api/platform/monitor", apiPlatformMonitor],
  ["GET /api/platform/audit", apiPlatformAudit],
  ["GET /api/platform/admins", apiPlatformAdmins],
  ["POST /api/platform/admins", apiPlatformAdmins],
  ["PUT /api/platform/admins/:id", (r, re, u, s, b, p) => apiPlatformAdminUpdate(r, re, u, s, b, p)],
  ["DELETE /api/platform/admins/:id", (r, re, u, s, b, p) => apiPlatformAdminDelete(r, re, u, s, b, p)],
  ["GET /api/platform/roles", apiPlatformRoles],
  ["POST /api/platform/roles", apiPlatformRoleSave],
  ["DELETE /api/platform/roles/:key", (r, re, u, s, b, p) => apiPlatformRoleDelete(r, re, u, s, b, p)],
  ["POST /api/platform/roles/staff", apiStaffRoleSave],
  ["DELETE /api/platform/roles/staff/:key", (r, re, u, s, b, p) => apiStaffRoleDelete(r, re, u, s, b, p)],
  ["POST /api/platform/users", apiPlatformUserCreate],
  ["GET /api/platform/revenue", apiPlatformRevenue],
  ["GET /api/platform/custom-providers", apiPlatformCustomProviders],
  ["POST /api/platform/custom-providers", apiPlatformCustomProviderAdd],
  ["GET /api/platform/rules", apiPlatformRules],
  ["POST /api/platform/rules", apiPlatformRuleSave],
  ["POST /api/platform/rules/explain", apiPlatformRuleExplain],
  ["DELETE /api/platform/rules/:id", (r, re, u, s, b, p) => apiPlatformRuleDelete(r, re, u, s, b, p)],
  ["GET /api/admin/rules", apiAdminRules],
  ["GET /api/admin/rules/subjects", apiAdminRuleSubjects],
  ["GET /api/platform/rules/subjects", apiPlatformRuleSubjects],
  ["POST /api/admin/rules", apiAdminRuleSave],
  ["POST /api/admin/rules/explain", apiAdminRuleExplain],
  ["DELETE /api/admin/rules/:id", (r, re, u, s, b, p) => apiAdminRuleDelete(r, re, u, s, b, p)],
  ["POST /api/admin/segments/members", apiAdminSegmentMemberAdd],
  ["DELETE /api/admin/segments/members/:id", (r, re, u, s, b, p) => apiAdminSegmentMemberDelete(r, re, u, s, b, p)],
  ["POST /api/rules/check", apiRulesCheck],
  ["DELETE /api/platform/custom-providers/:id", (r, re, u, s, b, p) => apiPlatformCustomProviderDelete(r, re, u, s, b, p)]
];

function handle(req, res, url, session, body, metrics) {
  const method = req.method;
  const pathname = url.pathname.replace(/\/$/, "") || "/";
  const pathSegs = pathname.split("/").filter(Boolean);
  for (const [key, fn] of routes) {
    const [m, pattern] = key.split(" ");
    const parts = pattern.split("/").filter(Boolean);
    if (m !== method || parts.length !== pathSegs.length) continue;
    const params = [];
    let ok = true;
    for (let i = 0; i < parts.length; i++) {
      if (parts[i].startsWith(":")) params.push(decodeURIComponent(pathSegs[i] || ""));
      else if (parts[i] !== pathSegs[i]) { ok = false; break; }
    }
    if (!ok) continue;
    /* the route is known to every guard below (requirePlatform authorizes a mutation
       against the platform section the path belongs to) */
    session.__route = { method, pathname };
    /* a handler's internal error text (SQL, stack-derived messages) never reaches the
       client — it is logged with the trace id, and the client gets the id to quote.
       Async handlers return a promise: its rejection is caught here too, instead of
       escaping as an unhandled rejection. */
    const fail = (e) => {
      console.error("[" + (session.trace || "-") + "] " + method + " " + pathname + ":", e && e.stack || e);
      if (!res.headersSent) bad(res, "Server error (trace " + (session.trace || "-") + ")", 500);
    };
    /* the request is the context every applicability rule is decided in (lib/rules.js): a
       storefront call carries its buyer (segments, channel, any declared fact); a console
       call (/api/admin, /api/platform) decides for the platform alone */
    const ctxStore = { s: session, req, url, body, staff: /^\/api\/(admin|platform)(\/|$)/.test(pathname) };
    try {
      const r = rules.run(ctxStore, () => fn(req, res, url, session, body, params[0], params[1], metrics));
      if (r && typeof r.then === "function") r.catch(fail);
    } catch (e) { fail(e); }
    return true;
  }
  return false;
}

module.exports = { handle, json, bad, search, startPaymentSweep, reconcilePending,
  /* the live route table, for traceability (lib/ucos-trace.js) — never a second copy */
  routeKeys: () => routes.map(([key]) => {
    const [method, path] = key.split(" ");
    return { method, path };
  }) };

/* ========== UCII Ω∞ Registry API ========== */
// Capability Registry
function apiCapabilityList(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const category = url.searchParams.get('category');
  const q = category ? 'WHERE category=?' : '';
  const p = category ? [category] : [];
  json(res, 200, { capabilities: all(`SELECT * FROM capabilities ${q} ORDER BY category, key`, ...p) });
}
function apiCapabilityCreate(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  if (!body.key || !body.name) return bad(res, 'key and name required', 400);
  run('INSERT INTO capabilities(key,name,description,category,version,schema,config,dependencies,status) VALUES(?,?,?,?,?,?,?,?,?)',
    body.key, body.name, body.description || '', body.category || '', body.version || '1.0.0', 
    JSON.stringify(body.schema || {}), JSON.stringify(body.config || {}), JSON.stringify(body.dependencies || []), body.status || 'active');
  logAction(s, 'capability.create', 'capability', body.key);
  json(res, 200, { ok: true });
}
function apiCapabilityUpdate(req, res, url, s, body, key) {
  if (!requirePlatform(s, res)) return;
  run('UPDATE capabilities SET name=?,description=?,category=?,version=?,schema=?,config=?,dependencies=?,status=? WHERE key=?',
    body.name, body.description, body.category, body.version, JSON.stringify(body.schema || {}), 
    JSON.stringify(body.config || {}), JSON.stringify(body.dependencies || []), body.status, key);
  logAction(s, 'capability.update', 'capability', key);
  json(res, 200, { ok: true });
}

// Domain Registry
function apiDomainList(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  json(res, 200, { domains: all('SELECT * FROM domains ORDER BY key') });
}
function apiDomainCreate(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  if (!body.key || !body.name) return bad(res, 'key and name required', 400);
  run('INSERT INTO domains(key,name,description,parent,schema,policies,status) VALUES(?,?,?,?,?,?,?)',
    body.key, body.name, body.description || '', body.parent || '', JSON.stringify(body.schema || {}), JSON.stringify(body.policies || []), body.status || 'active');
  logAction(s, 'domain.create', 'domain', body.key);
  json(res, 200, { ok: true });
}

// Policy Registry
function apiPolicyList(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const domain = url.searchParams.get('domain');
  const q = domain ? 'WHERE domain=?' : '';
  const p = domain ? [domain] : [];
  json(res, 200, { policies: all(`SELECT * FROM policies ${q} ORDER BY priority`, ...p) });
}
function apiPolicyCreate(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  if (!body.key || !body.name || !body.rule) return bad(res, 'key, name, and rule required', 400);
  run('INSERT INTO policies(key,domain,name,description,type,priority,rule,context,status) VALUES(?,?,?,?,?,?,?,?,?)',
    body.key, body.domain, body.name, body.description || '', body.type || 'validation', body.priority || 0, body.rule, JSON.stringify(body.context || {}), body.status || 'active');
  logAction(s, 'policy.create', 'policy', body.key);
  json(res, 200, { ok: true });
}

// Workflow Registry
function apiWorkflowList(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const domain = url.searchParams.get('domain');
  const q = domain ? 'WHERE domain=?' : '';
  const p = domain ? [domain] : [];
  json(res, 200, { workflows: all(`SELECT * FROM workflows ${q} ORDER BY key`, ...p) });
}
function apiWorkflowCreate(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  if (!body.key || !body.domain || !body.trigger || !body.steps) return bad(res, 'key, domain, trigger, and steps required', 400);
  run('INSERT INTO workflows(key,domain,name,description,trigger,steps,config,status) VALUES(?,?,?,?,?,?,?,?)',
    body.key, body.domain, body.name || null, body.description || '', body.trigger, JSON.stringify(body.steps), JSON.stringify(body.config || {}), body.status || 'active');
  logAction(s, 'workflow.create', 'workflow', body.key);
  json(res, 200, { ok: true });
}
function apiWorkflowDelete(req, res, url, s, body, key) {
  if (!requirePlatform(s, res)) return;
  run('DELETE FROM workflows WHERE key=?', key);
  logAction(s, 'workflow.delete', 'workflow', key);
  json(res, 200, { ok: true });
}

// Config Store
function apiConfigGet(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const key = url.searchParams.get('key');
  const tenantId = url.searchParams.get('tenant_id');
  const scope = url.searchParams.get('scope') || 'platform';
  if (key) {
    const row = get('SELECT * FROM config_store WHERE key=? AND scope=? AND (tenant_id=? OR tenant_id IS NULL) ORDER BY version DESC LIMIT 1', key, scope, tenantId ? Number(tenantId) : null);
    json(res, 200, { config: row ? { ...row, value: JSON.parse(row.value || '{}') } : null });
  } else {
    const q = tenantId ? 'WHERE scope=? AND tenant_id=?' : 'WHERE scope=?';
    const p = tenantId ? [scope, Number(tenantId)] : [scope];
    const configs = all(`SELECT * FROM config_store ${q} AND active=1 ORDER BY key`, ...p);
    json(res, 200, { config: Object.fromEntries(configs.map(c => [c.key, JSON.parse(c.value || '{}')])) });
  }
}
function apiConfigSet(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  if (!body.key || !body.value) return bad(res, 'key and value required', 400);
  const scope = body.scope || 'platform';
  const tenantId = body.tenant_id || null;
  const existing = get('SELECT version FROM config_store WHERE key=? AND scope=? AND tenant_id=?', body.key, scope, tenantId);
  const version = (existing ? existing.version : 0) + 1;
  run('INSERT INTO config_store(key,value,scope,tenant_id,version,active,updated_at) VALUES(?,?,?,?,?,?,datetime(\'now\')) ON CONFLICT(key,scope,tenant_id) DO UPDATE SET value=excluded.value,version=excluded.version,updated_at=datetime(\'now\')',
    body.key, JSON.stringify(body.value), scope, tenantId, version, body.active !== false ? 1 : 0);
  logAction(s, 'config.set', 'config', body.key);
  json(res, 200, { ok: true });
}

// Knowledge Graph
function apiKnowledgeGraphQuery(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const source = url.searchParams.get('source_type');
  const sourceId = url.searchParams.get('source_id');
  const rel = url.searchParams.get('relationship');
  if (source && sourceId) {
    const q = 'WHERE source_type=? AND source_id=?' + (rel ? ' AND relationship=?' : '');
    const p = rel ? [source, Number(sourceId), rel] : [source, Number(sourceId)];
    json(res, 200, { edges: all(`SELECT * FROM knowledge_graph ${q} ORDER BY weight DESC LIMIT 100`, ...p) });
  } else {
    json(res, 200, { edges: all('SELECT * FROM knowledge_graph ORDER BY weight DESC LIMIT 100') });
  }
}
function apiKnowledgeGraphAdd(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  if (!body.source_type || !body.source_id || !body.relationship || !body.target_type || !body.target_id) return bad(res, 'source and target required', 400);
  run('INSERT INTO knowledge_graph(source_type,source_id,relationship,target_type,target_id,weight,metadata) VALUES(?,?,?,?,?,?,?)',
    body.source_type, Number(body.source_id), body.relationship, body.target_type, Number(body.target_id), body.weight || 1.0, JSON.stringify(body.metadata || {}));
  json(res, 200, { ok: true });
}

// Usage Metering
/* S10: this had no auth gate and took the tenant from the request body, so
   anyone could inject metering rows for any store — the table usage reporting
   and billing read. The tenant is the session's store, always. A platform
   operator working a store records against it too, so the gate accepts the
   platform session as well as the store's own admin. */
function apiUsageRecord(req, res, url, s, body) {
  if (!requireStaff(s, res)) return;
  const tenantId = T(s);
  run('INSERT INTO usage_events(tenant_id,entity,entity_id,event_type,quantity,unit,metadata) VALUES(?,?,?,?,?,?,?)',
    tenantId, body.entity, body.entity_id ? Number(body.entity_id) : null, body.event_type, body.quantity || 1, body.unit || 'count', JSON.stringify(body.metadata || {}));
  json(res, 200, { ok: true });
}
function apiUsageReport(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const tenantId = url.searchParams.get('tenant_id');
  const entity = url.searchParams.get('entity');
  const period = url.searchParams.get('period');
  let q = 'SELECT entity,event_type,SUM(quantity) as total,unit FROM usage_events';
  const p = [];
  if (tenantId) { q += ' WHERE tenant_id=?'; p.push(Number(tenantId)); }
  if (entity) { q += (p.length ? ' AND ' : ' WHERE ') + 'entity=?'; p.push(entity); }
  if (period) { q += (p.length ? ' AND ' : ' WHERE ') + 'strftime(\'%Y-%m\',created_at)=?'; p.push(period); }
  q += ' GROUP BY entity,event_type ORDER BY total DESC';
  json(res, 200, { usage: all(q, ...p) });
}

/* ========== Global Product Catalog API ========== */
function apiGlobalProductList(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const category = url.searchParams.get('category');
  const status = url.searchParams.get('status');
  const universe = url.searchParams.get('universe');
  let q = 'SELECT * FROM global_products';
  const p = [];
  if (category) { q += ' WHERE category=?'; p.push(category); }
  if (status) { q += (p.length ? ' AND ' : ' WHERE ') + 'status=?'; p.push(status); }
  if (universe) { q += (p.length ? ' AND ' : ' WHERE ') + 'universe=?'; p.push(universe); }
  q += ' ORDER BY category, name';
  /* the universe vocabulary the constitution declares (UPIP §1), so the console's picker
     is populated by the registry — never by a list baked into the front-end. mediaKinds,
     taxClasses and the category vocabulary ride along for the same reason: the form's
     every dropdown is registry-driven. media/attributes are TEXT columns, so they are
     parsed here — the console edits them as structured data and must never receive a JSON
     string it would then stringify again (an edit round-trip through a string silently
     wipes the field) */
  const products = all(q, ...p).map(p => {
    let media; try { media = JSON.parse(p.media || "[]"); } catch (e) { media = []; }
    if (!Array.isArray(media)) media = [];
    /* the type the store console and import path already resolve — surfaced here so the
       console's Type badge and any reader sees the derived value, never is_service alone */
    return { ...p, media, attributes: J(p.attributes, {}), profile: J(p.profile, {}), type: require("./gcatalog.js").typeOfUniverse(p.universe) };
  });
  json(res, 200, { products, universes: rl("productUniverses"), mediaKinds: rl("mediaKinds"),
    taxClasses: rl("taxClasses"), categories: platformCategories(), universeProductTypes: universeTypeList(),
    /* the console's "store catalogue details" section renders against THIS list, so the
       form can never offer a field the validator refuses — the API is the authority on
       what a platform product may carry, the console only renders it */
    profileFields: profileFields().map(f => ({ key: f.key, label: f.label, type: f.type, hint: f.hint || "" })) });
}
/* the platform-level category vocabulary for a global product. A store's taxonomy is its
   own (tenant-scoped), but the platform catalogue categorizes by industry and the
   category tree every store's taxonomy grows from — both registry data, so a global
   product's category is never free text. Industries carry an icon; taxonomy rows below
   them give the finer grain. */
function platformCategories() {
  const root = taxRoot(), lv = taxLevels().filter(l => l.platform_catalogue).map(l => l.key);
  const inds = rl("industries").map(i => ({ key: i.key, name: i.name, icon: i.icon || "🏷️", level: root }));
  if (!lv.length) return inds;
  const cats = all("SELECT DISTINCT key, name, level FROM taxonomy WHERE level IN (" + lv.map(() => "?").join(",") + ") AND active=1 AND deleted_at IS NULL ORDER BY level, name", ...lv)
    .map(c => ({ key: c.key, name: c.name, icon: "", level: c.level }));
  return inds.concat(cats);
}
/* the universe → product type map the archetype seed persists (gcatalog.js), so the
   console shows a product's type as a consequence of its universe rather than a checkbox
   an operator could set to contradict it */
function universeTypeList() { return rl("universeProductTypes"); }
/* media is structured data the storefront renders directly ({kind,label,url|emoji}), so
   the API is the last line of defence: kind must be a declared mediaKinds entry and the
   reference must be an http(s) URL or a short emoji/text token. Anything else is
   rejected rather than stored as a broken asset (L10: input is validated, never trusted) */
function validMedia(v) {
  if (!Array.isArray(v)) return [];
  const kinds = rl("mediaKinds").map(k => k.key);
  return v.map(m => {
    if (!m || typeof m !== "object" || Array.isArray(m)) return null;
    const kind = kinds.includes(m.kind) ? m.kind : "image";
    const label = String(m.label || "").slice(0, 120);
    const url = String(m.url || "");
    const ref = /^https?:\/\//i.test(url) ? url.slice(0, 2048) : "";
    const emoji = ref ? "" : String(m.emoji || "").slice(0, 16);
    if (!label && !ref && !emoji) return null;
    const out = { kind, label };
    if (ref) out.url = ref; else out.emoji = emoji;
    return out;
  }).filter(Boolean);
}
/* The platform authors the WHOLE product. A global product's `profile` carries every
   authorable field of the store product entity, and the import bridge copies them onto
   the store row — so there is no product detail a store can have that the Global Platform
   cannot set. Only fields the products ENTITY declares are accepted (the declaration is
   the single source of "what a product has"), and store-operational fields — stock,
   ratings, lifecycle, taxonomy placement, seller, provenance — are deliberately excluded:
   they describe THIS store's live instance, not the archetype. */
const PROFILE_SKIP = new Set(["uid", "id", "title", "price", "type", "node_id", "stock", "rating", "count",
  "priority", "lifecycle", "identity", "attrs", "media", "supplier_id", "source_kind", "source_universe"]);
function profileFields() {
  return entity.ENTITY_DEFS.product.fields.filter(f => !f.readonly && !PROFILE_SKIP.has(f.key));
}
function validProfile(v) {
  const out = {}, rejected = [];
  if (v == null) return { profile: out, rejected };
  if (typeof v !== "object" || Array.isArray(v)) return { profile: out, rejected: ["profile (must be an object)"] };
  for (const [k, val] of Object.entries(v)) {
    const f = profileFields().find(x => x.key === k);
    if (!f) { rejected.push(k); continue; }
    if (f.type === "json") {
      let o = val;
      if (typeof o === "string") { try { o = JSON.parse(o); } catch (e) { rejected.push(k + " (invalid JSON)"); continue; } }
      if (o === null || typeof o !== "object") { rejected.push(k + " (must be a JSON object/array)"); continue; }
      out[k] = o;
    } else if (f.type === "number" || f.type === "money") {
      if (val === "" || val == null) continue; /* an empty field is an unset field */
      const n = Number(val);
      if (!isFinite(n)) { rejected.push(k + " (not a number)"); continue; }
      out[k] = n;
    } else {
      if (val == null || val === "") continue;
      out[k] = String(val).slice(0, 2000);
    }
  }
  return { profile: out, rejected };
}
function apiGlobalProductCreate(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  if (!body.sku || !body.name) return bad(res, 'sku and name required', 400);
  const universe = validProductUniverse(body.universe);
  /* a product's type follows from its universe (universeProductTypes in gcatalog.js) —
     the store listing and the import path both derive it there, so storing a hand-toggled
     is_service would let the record contradict its own universe. The universe is the
     authority; is_service is its consequence, not an independent input */
  const isService = (rl("productTypes") || []).some(t => t && t.service && t.key === require("./gcatalog.js").typeOfUniverse(universe)) ? 1 : 0;
  const { profile, rejected } = validProfile(body.profile);
  if (rejected.length) return bad(res, "Unknown/invalid profile field(s): " + rejected.join(", "), 400);
  const r = run('INSERT INTO global_products(sku,name,description,category,universe,price,tax_class,is_service,attributes,media,profile,status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',
    body.sku, body.name, body.description || '', body.category || '', universe, body.price || 0, body.tax_class || 'standard', isService, JSON.stringify(body.attributes || {}), JSON.stringify(validMedia(body.media)), JSON.stringify(profile), body.status || 'draft');
  logAction(s, 'global_product.create', 'global_product', body.sku);
  json(res, 200, { ok: true, id: Number(r.lastInsertRowid) });
}
function apiGlobalProductUpdate(req, res, url, s, body, id) {
  if (!requirePlatform(s, res)) return;
  const gid = Number(id);
  const cur = get('SELECT sku FROM global_products WHERE id=?', gid);
  if (!cur) return bad(res, 'Unknown global product', 404);
  /* an UPDATE that re-sets the row's own sku trips SQLite's UNIQUE check mid-statement
     ("self-collision"). The id is the anchor; the sku only moves when it genuinely
     changes, and a move onto another product's sku must be reported, not silently 500. */
  const newSku = String(body.sku || "").trim();
  if (newSku && newSku !== cur.sku) {
    const taken = get('SELECT id FROM global_products WHERE sku=? AND id!=?', newSku, gid);
    if (taken) return bad(res, 'SKU ' + newSku + ' is already used by another global product', 409);
  }
  const universe = validProductUniverse(body.universe);
  /* derived from the universe, exactly as on create — an edit that moved the product to
     another universe must move its type with it, never the operator's memory of a box */
  const isService = (rl("productTypes") || []).some(t => t && t.service && t.key === require("./gcatalog.js").typeOfUniverse(universe)) ? 1 : 0;
  const { profile, rejected } = validProfile(body.profile);
  if (rejected.length) return bad(res, "Unknown/invalid profile field(s): " + rejected.join(", "), 400);
  run('UPDATE global_products SET sku=?,name=?,description=?,category=?,universe=?,price=?,tax_class=?,is_service=?,attributes=?,media=?,profile=?,status=? WHERE id=?',
    newSku || cur.sku, body.name, body.description || '', body.category || '', universe, Number(body.price) || 0, body.tax_class || 'standard', isService, JSON.stringify(body.attributes || {}), JSON.stringify(validMedia(body.media)), JSON.stringify(profile), body.status || 'draft', gid);
  logAction(s, 'global_product.update', 'global_product', newSku || cur.sku);
  json(res, 200, { ok: true });
}
/* a product's universe must be one the constitution declares, or one an operator has
   added to the registry — never an arbitrary string (Architecture3 Article 4.2: the
   vocabulary is data, but it is still the registry's data) */
function validProductUniverse(v) {
  const k = String(v || "").trim();
  if (!k) return "physical_products";
  return rl("productUniverses").some(u => u.key === k) ? k : "physical_products";
}
/* the configuration a product of THIS universe carries — the corpus's own declared
   fields, read structurally out of the universe's entity definition (the same source
   canonicalRecord() materializes a record from). This is what makes the product form
   adapt per industry: choosing "Insurance" shows insurance's declared fields, choosing
   "Streaming" shows streaming's, and no per-industry form code exists anywhere.

   The corpus declares the product-universe vocabulary (UPIP §1, e.g. "insurance_products")
   and separately instantiates every universe the corpus declares, keyed by their own container names
   ("uv_insurance_product") — the two vocabularies do not agree on keys, so the lookup is
   normalized: punctuation stripped, trailing 's' and filler words ("product", "types")
   removed. A universe with no matching entity (Subscriptions, OTT Platforms…) declares no
   extra fields and the form falls back to custom attributes — it never invents one */
function universeFieldsOf(key) {
  const FILLER = ["producttypes", "products", "product", "types"];
  const norm = s => String(s || "").toLowerCase().replace(/[^a-z0-9]/g, "");
  const variants = s => {
    const a = norm(s), b = a.replace(/s$/, "");
    const out = new Set([a, b]);
    for (const f of FILLER) { if (b.endsWith(f)) out.add(b.slice(0, -f.length)); if (a.endsWith(f)) out.add(a.slice(0, -f.length)); }
    return [...out];
  };
  const index = new Map();
  for (const r of all("SELECT key, def FROM entity_defs WHERE key LIKE 'uv_%'")) {
    let d = null; try { d = JSON.parse(r.def || "{}"); } catch (e) { }
    if (!d) continue;
    const n = (d.fields || []).filter(f => f.key && !["name", "code", "status", "attrs"].includes(f.key)).length;
    for (const nm of [r.key.slice(3), d.label]) for (const v of variants(nm)) {
      if (!index.has(v)) index.set(v, []);
      index.get(v).push({ d, n });
    }
  }
  const cands = variants(key).flatMap(v => index.get(v) || []);
  if (!cands.length) return { fields: [], universe: null };
  /* the corpus also declares bare "*_product" shells (name/code/status/attrs only) that
     collide on the same normalized name; the universe that actually DECLARES
     configuration is the one an operator wants to configure against */
  const best = cands.reduce((a, b) => (b.n > a.n ? b : a));
  return { fields: (best.d.fields || []).filter(f => f.key && !["name", "code", "status", "attrs"].includes(f.key)), universe: best.d.label || null };
}
function apiUniverseFields(req, res, url, s, body, key) {
  if (!requirePlatform(s, res)) return;
  json(res, 200, universeFieldsOf(String(key || "")));
}
function apiGlobalProductDelete(req, res, url, s, body, id) {
  if (!requirePlatform(s, res)) return;
  run('DELETE FROM global_products WHERE id=?', Number(id));
  logAction(s, 'global_product.delete', 'global_product', id);
  json(res, 200, { ok: true });
}
function apiStoreProductConfig(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const tenantId = url.searchParams.get('tenant_id');
  const globalId = url.searchParams.get('global_product_id');
  const q = tenantId ? 'WHERE tenant_id=?' : '';
  const p = tenantId ? [tenantId] : [];
  json(res, 200, { configs: all(`SELECT * FROM store_product_config ${q} ORDER BY category`, ...p) });
}
function apiStoreProductConfigSet(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  if (!body.tenant_id || !body.global_product_id) return bad(res, 'tenant_id and global_product_id required', 400);
  run('INSERT INTO store_product_config(tenant_id,global_product_id,category,permissions,enabled) VALUES(?,?,?,?,?) ON CONFLICT(tenant_id,global_product_id) DO UPDATE SET category=excluded.category,permissions=excluded.permissions,enabled=excluded.enabled',
    body.tenant_id, body.global_product_id, body.category || '', body.permissions || 'read', body.enabled !== false ? 1 : 0);
  logAction(s, 'store_product_config.set', 'store_product_config', `${body.tenant_id}:${body.global_product_id}`);
  json(res, 200, { ok: true });
}
function apiStoreProductConfigDelete(req, res, url, s, body, tenantId, globalId) {
  if (!requirePlatform(s, res)) return;
  run('DELETE FROM store_product_config WHERE tenant_id=? AND global_product_id=?', tenantId, globalId);
  logAction(s, 'store_product_config.delete', 'store_product_config', `${tenantId}:${globalId}`);
  json(res, 200, { ok: true });
}
function apiStoreProductPermissions(req, res, url, s) {
  const tenantId = T(s);
  json(res, 200, { configs: all('SELECT * FROM store_product_config WHERE tenant_id=? AND enabled=1', tenantId) });
}

/* ========== UPIP §1/§5 · Universal Global Catalog ==========
   The platform's catalogue is populated automatically (one canonical product per corpus
   universe) and manually (console rows). A store admin may pull a global product into
   their own catalogue ONLY when the platform has permitted it — the "if the Global
   Platform permits" clause, enforced by lib/gcatalog.js, never by the store. */
function apiGlobalCatalog(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  json(res, 200, { products: require("./gcatalog.js").globalListWithPermissions(), universes: rl("productUniverses") });
}
function apiStoreCatalogImport(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const gid = body && body.global_product_id;
  if (!gid) return bad(res, 'global_product_id required', 400);
  const out = require("./gcatalog.js").importToStore(T(s), gid);
  if (!out.ok) return bad(res, out.error, 403);
  logAction(s, 'product.import_global', 'product', out.id, { global_product_id: gid, universe: out.universe });
  json(res, 200, out);
}
function apiStoreCatalogImportable(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  /* the store console's "add from platform" picker: every global product, annotated with
     whether THIS store may import it and whether it already listed — absent permissions
     are reported, so the merchant knows what to request rather than guessing */
  const gcat = require("./gcatalog.js");
  const products = all('SELECT * FROM global_products ORDER BY category, name');
  const t = T(s);
  const listed = new Set(all('SELECT source_global_id FROM products WHERE tenant_id=? AND source_global_id IS NOT NULL', t).map(r => String(r.source_global_id)));
  const items = products.map(p => {
    const gate = gcat.mayList(t, p.id);
    return { id: p.id, sku: p.sku, name: p.name, universe: p.universe, category: p.category,
      price: p.price, is_service: p.is_service, status: p.status,
      type: gcat.typeOfUniverse(p.universe),
      permitted: gate.ok, reason: gate.ok ? null : gate.reason,
      listed: listed.has(String(p.id)) };
  });
  json(res, 200, { items });
}

/* ========== Affiliate Network APIs ==========
   S1: this block was entirely unauthenticated and unscoped — an anonymous
   caller could register an affiliate, attribute another tenant's order to it,
   and pay itself the commission. Every management route now passes the store's
   admin gate, every query carries the session's tenant, and the tenant comes
   from the session, never the body. The one exception is the storefront
   tracking pixel (click), which is anonymous by design and was already scoped
   by the store the request resolved to. */
function apiAffiliateNetworks(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { networks: all('SELECT * FROM affiliate_networks WHERE tenant_id=? OR tenant_id IS NULL ORDER BY id', T(s)) });
}
function apiAffiliateNetworkCreate(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  if (!body.name) return bad(res, 'name required', 400);
  const tenantId = T(s);
  const r = run('INSERT INTO affiliate_networks(name,slug,tenant_id,status,default_commission_pct,cookie_days,attribution_model) VALUES(?,?,?,?,?,?,?)',
    body.name, body.slug || body.name.toLowerCase().replace(/\s+/g, '-'), tenantId, body.status || 'active', body.default_commission_pct || 5.0, body.cookie_days || 30, body.attribution_model || require("./defaults.js").of("goipAttributionModels"));
  json(res, 200, { ok: true, id: Number(r.lastInsertRowid) });
}
function apiAffiliateList(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const networkId = url.searchParams.get('network_id');
  const status = url.searchParams.get('status');
  const search = url.searchParams.get('search');
  let q = 'SELECT * FROM affiliates WHERE tenant_id=?';
  const p = [T(s)];
  if (networkId) { q += ' AND network_id=?'; p.push(Number(networkId)); }
  if (status) { q += ' AND status=?'; p.push(status); }
  if (search) { q += ' AND (name LIKE ? OR affiliate_code LIKE ?)'; p.push('%' + search + '%', '%' + search + '%'); }
  json(res, 200, { affiliates: all(q + ' ORDER BY created_at DESC', ...p) });
}
function apiAffiliateCreate(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  if (!body.name) return bad(res, 'name required', 400);
  const tenantId = T(s);
  const code = body.affiliate_code || 'AFF-' + Math.random().toString(36).slice(2,8).toUpperCase();
  const r = run('INSERT INTO affiliates(network_id,tenant_id,name,email,status,affiliate_code,commission_type,tier) VALUES(?,?,?,?,?,?,?,?)',
    body.network_id || 1, tenantId, body.name, body.email, 'pending', code, body.commission_type || 'revenue', body.tier || 'standard');
  json(res, 200, { ok: true, id: Number(r.lastInsertRowid), code });
}
function apiAffiliateGet(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { affiliate: all('SELECT * FROM affiliates WHERE id=? AND tenant_id=?', id, T(s))[0] });
}
/* S8: body keys used to become SET clause text directly. Whitelist against the
   declared columns and scope the UPDATE to this tenant, the same way the entity
   engine whitelists its own dynamic builders. */
const AFFILIATE_COLS = ['network_id','name','email','status','affiliate_code','tracking_url','deep_link_template','commission_pct','commission_type','tier','last_activity','metadata'];
function apiAffiliateUpdate(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const updates = [];
  const p = [];
  for (const [k, v] of Object.entries(body)) {
    if (AFFILIATE_COLS.includes(k)) { updates.push(k + '=?'); p.push(v); }
  }
  if (!updates.length) return bad(res, 'no updatable fields provided', 400);
  p.push(body.id, T(s));
  run('UPDATE affiliates SET ' + updates.join(',') + ' WHERE id=? AND tenant_id=?', ...p);
  json(res, 200, { ok: true });
}
/* the storefront pixel: a shopper clicking an affiliate link. Anonymous by
   design — the click is recorded against the store the request resolved to,
   which is the only tenant it can ever be read back by */
function apiAffiliateClick(req, res, url, s, body) {
  const tenantId = T(s);
  const clickId = 'clk-' + Date.now() + '-' + Math.random().toString(36).slice(2,6);
  run('INSERT INTO affiliate_clicks(affiliate_id,network_id,tenant_id,click_id,referrer,landing_url,campaign,source,medium) VALUES(?,?,?,?,?,?,?,?,?)',
    body.affiliate_id, body.network_id || 1, tenantId, clickId, body.referrer || '', body.landing_url || '', body.campaign || '', body.source || '', body.medium || '');
  json(res, 200, { click_id: clickId });
}
/* S1: the order must be THIS tenant's order and the affiliate THIS tenant's
   affiliate — otherwise the commission is a cross-tenant transfer, and the
   returned commission was a cross-tenant revenue oracle */
function apiAffiliateConversion(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const tenantId = T(s);
  const order = all('SELECT * FROM orders WHERE id=? AND tenant_id=?', body.order_id, tenantId)[0];
  if (!order) return bad(res, 'order not found', 404);
  const aff = all('SELECT id FROM affiliates WHERE id=? AND tenant_id=?', body.affiliate_id, tenantId)[0];
  if (!aff) return bad(res, 'affiliate not found', 404);
  const commission = body.commission || (order.total * (body.commission_pct || 5) / 100);
  const r = run('INSERT INTO affiliate_conversions(affiliate_id,network_id,tenant_id,order_id,order_num,revenue,commission,commission_pct) VALUES(?,?,?,?,?,?,?,?)',
    body.affiliate_id, body.network_id || 1, tenantId, body.order_id, order.num, order.total, commission, body.commission_pct || 5);
  const convId = Number(r.lastInsertRowid);
  run('UPDATE affiliates SET balance = balance + ?, lifetime_sales = lifetime_sales + ?, lifetime_commissions = lifetime_commissions + ? WHERE id=? AND tenant_id=?',
    commission, order.total, commission, body.affiliate_id, tenantId);
  json(res, 200, { ok: true, conversion_id: convId, commission });
}
function apiAffiliateConversionGet(req, res, url, s, body, id) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { conversion: all('SELECT * FROM affiliate_conversions WHERE id=? AND tenant_id=?', id, T(s))[0] });
}
function apiAffiliateApprove(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  run('UPDATE affiliate_conversions SET status=?,approved_at=? WHERE id=? AND tenant_id=?', 'approved', new Date().toISOString(), body.id, T(s));
  json(res, 200, { ok: true });
}
function apiAffiliateReject(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  run('UPDATE affiliate_conversions SET status=?,approved_at=? WHERE id=? AND tenant_id=?', 'rejected', new Date().toISOString(), body.id, T(s));
  json(res, 200, { ok: true });
}
/* payouts carry no tenant column: scope through the affiliate they belong to,
   so one store can never see — or process — another store's payouts */
function apiAffiliatePayouts(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const affiliateId = url.searchParams.get('affiliate_id');
  const q = 'SELECT p.* FROM affiliate_payouts p JOIN affiliates a ON a.id=p.affiliate_id WHERE a.tenant_id=?';
  json(res, 200, { payouts: all(affiliateId ? q + ' AND p.affiliate_id=? ORDER BY p.created_at DESC' : q + ' ORDER BY p.created_at DESC',
    ...(affiliateId ? [T(s), Number(affiliateId)] : [T(s)])) });
}
function apiAffiliatePayoutCreate(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  if (!(body.amount >= 1)) return bad(res, 'amount must be at least 1', 400);
  const aff = all('SELECT id, network_id, balance FROM affiliates WHERE id=? AND tenant_id=?', body.affiliate_id, T(s))[0];
  if (!aff) return bad(res, 'affiliate not found', 404);
  run('INSERT INTO affiliate_payouts(affiliate_id,network_id,amount,status,method) VALUES(?,?,?,?,?)',
    aff.id, aff.network_id || 1, body.amount, 'pending', body.method || 'bank');
  json(res, 200, { ok: true });
}
function apiAffiliatePayoutProcess(req, res, url, s, body) {
  if (!requireAdmin(s, res)) return;
  const p = all('SELECT p.id FROM affiliate_payouts p JOIN affiliates a ON a.id=p.affiliate_id WHERE p.id=? AND a.tenant_id=?', body.id, T(s))[0];
  if (!p) return bad(res, 'payout not found', 404);
  run('UPDATE affiliate_payouts SET status=?,paid_at=?,transaction_ref=? WHERE id=?', 'paid', new Date().toISOString(), 'TXN-' + Date.now(), body.id);
  json(res, 200, { ok: true });
}
function apiAffiliateReport(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const networkId = url.searchParams.get('network_id') || 1;
  const summary = all('SELECT COUNT(*) as affiliates, SUM(lifetime_sales) as sales, SUM(lifetime_commissions) as commissions FROM affiliates WHERE network_id=? AND status=? AND tenant_id=?', networkId, 'active', T(s))[0];
  const topAffiliates = all('SELECT name,affiliate_code,lifetime_sales,lifetime_commissions FROM affiliates WHERE network_id=? AND status=? AND tenant_id=? ORDER BY lifetime_sales DESC LIMIT 10', networkId, 'active', T(s));
  json(res, 200, { 
    summary: { affiliates: summary.affiliates || 0, sales: summary.sales || 0, commissions: summary.commissions || 0 },
    top_affiliates: topAffiliates
  });
}

/* ========== Sitemap (SEO) APIs ========== */
/* the XML is public (search engines fetch it) but sits behind the same SEO Pro module as
   /api/seo/sitemap.xml — it used to bypass that gate. Config + generation are staff. */
const sitemapMod = require("./sitemap.js");
const shippingMod = require("./shipping.js");
function apiSitemap(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  json(res, 200, { sitemap: sitemapMod.get(T(s)) });
}
function apiSitemapXML(req, res, url, s) {
  if (!require("./gates.js").on(T(s), "seo.tools")) return bad(res, require("./gates.js").message("seo.tools"), 403);
  const xml = sitemapMod.generateXML(sitemapMod.buildSitemapEntries(T(s)));
  res.writeHead(200, { 'Content-Type': 'application/xml; charset=utf-8' });
  res.end(xml);
}
function apiSitemapGenerate(req, res, url, s, body) {
  if (!requireStaff(s, res)) return;
  const r = sitemapMod.generate(T(s), 'xml');
  if (r.error) return bad(res, r.error, r.code || 400);
  logAction(s, "sitemap.generate", "sitemap", null, { entries: r.entries }, req);
  json(res, 200, { ok: true, generated_at: r.last_generated, entries: r.entries, chunks: r.chunks });
}
function apiSitemapConfig(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  json(res, 200, { config: sitemapMod.getConfig(T(s)) });
}
function apiSitemapConfigUpdate(req, res, url, s, body) {
  if (!requireSection(s, res, "settings", "write")) return;
  let config;
  try { config = sitemapMod.updateConfig(T(s), body || {}); } catch (e) { return bad(res, e.message, 400); }
  logAction(s, "sitemap.config", "sitemap", null, {}, req);
  json(res, 200, { ok: true, config });
}

/* ========== Shipping & Tracking APIs ========== */
/* carrier provider rows are platform-wide and hold credentials: listing is staff-only and
   never returns the config; configuring is a platform write. Tracking is per store. */
function apiShippingProviders(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  json(res, 200, { providers: shippingMod.getProviders(T(s)) });
}
function apiShippingProviderConfig(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  const r = shippingMod.updateProviderConfig((body || {}).provider_id, (body || {}).config);
  if (r.error) return bad(res, r.error, r.code || 400);
  logAction(s, "shipping.provider_config", "shipping_provider", null, { provider: r.provider_id }, req);
  json(res, 200, { ok: true, provider: r });
}
/* the platform console's carrier accounts: every row, which keys are on file, and the
   public webhook address when one is configured (the console falls back to its own origin) */
function apiPlatformShippingProviders(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  const base = String(process.env.LX_PUBLIC_URL || "").replace(/\/+$/, "");
  json(res, 200, { providers: shippingMod.listProviders(), public_url: base || null });
}
function apiPlatformShippingDisconnect(req, res, url, s, body, providerId) {
  if (!requirePlatform(s, res)) return;
  const r = shippingMod.disconnectProvider(providerId);
  if (r.error) return bad(res, r.error, r.code || 400);
  logAction(s, "shipping.provider_disconnect", "shipping_provider", null, { provider: r.provider_id }, req);
  json(res, 200, { ok: true, provider: r });
}
/* a store's ship-from address is the origin of every carrier rate: only the address fields
   are kept, and the ones a carrier needs to rate a parcel are required */
const SHIP_FROM_FIELDS = ["name", "company", "street1", "street2", "city", "state", "zip", "country", "phone", "email"];
function cleanShipFrom(v) {
  if (v === null) return { value: null };
  if (!v || typeof v !== "object" || Array.isArray(v)) return { error: "shipFrom must be an address object" };
  const out = {};
  for (const k of SHIP_FROM_FIELDS) if (v[k] != null && String(v[k]).trim() !== "") out[k] = String(v[k]).trim().slice(0, 120);
  for (const k of ["street1", "city", "zip", "country"]) if (!out[k]) return { error: "Ship-from address needs " + ({ street1: "a street", city: "a city", zip: "a postal code", country: "a country" })[k] };
  out.country = out.country.toUpperCase();
  if (!/^[A-Z]{2}$/.test(out.country)) return { error: "Ship-from country must be a 2-letter code, e.g. US" };
  return { value: out };
}
function apiShippingTrack(req, res, url, s, body) {
  if (!requireStaff(s, res)) return;
  const r = shippingMod.createTracking(T(s), body || {});
  if (r.error) return bad(res, r.error, r.code || 400);
  json(res, 200, { tracking_number: r.tracking_number, tracking: r });
}
/* staff, or the customer whose order the parcel ships */
function apiShippingTrackGet(req, res, url, s, body, trackingNumber) {
  const r = shippingMod.track(T(s), trackingNumber);
  if (r.error) return bad(res, 'tracking not found', 404);
  if (!s.platform_admin && !isAdmin(s)) {
    const o = r.order_id ? get("SELECT owner FROM orders WHERE id=? AND tenant_id=?", r.order_id, T(s)) : null;
    if (!o || o.owner !== ownerFor(s)) return bad(res, 'tracking not found', 404);
  }
  json(res, 200, { tracking: r });
}
/* staff rate a parcel: origin is the store's ship-from address (settings
   commerce.shipFrom) unless the request names one; the destination is the order's own
   shipping address when an order is given */
async function apiShippingQuote(req, res, url, s, body) {
  if (!requireStaff(s, res)) return;
  const b = body || {};
  let to = b.to;
  if (!to && b.order_id != null) {
    const o = get("SELECT name, address, city, state, zip, status FROM orders WHERE id=? AND tenant_id=?", Number(b.order_id), T(s));
    if (!o) return bad(res, "Unknown order", 404);
    if (stIs("order", o.status, "not_shippable")) return bad(res, stIs("order", o.status, "aborted") ? "This order is cancelled" : "This order is not paid yet", 409);
    to = { name: o.name, street1: o.address, city: o.city, state: o.state, zip: o.zip, country: CFG(s).commerce.country.toUpperCase() };
  }
  const r = await shippingMod.getQuote(T(s), { ...b, to, from: b.from || CFG(s).commerce.shipFrom });
  if (r.error) return bad(res, r.error, r.code || 400);
  json(res, 200, r);
}
async function apiShippingLabel(req, res, url, s, body) {
  if (!requireStaff(s, res)) return;
  const r = await shippingMod.saveLabel(T(s), body || {});
  if (r.error) return bad(res, r.error, r.code || 400);
  logAction(s, "shipping.label", "order", r.order_num || null, { tracking: r.tracking_number, carrier: r.carrier, price: r.price }, req);
  if (r.order_id) {
    /* a label means the parcel is on its way: a processing order moves to shipped */
    const sh = stIn("order", "shippable");
    run("UPDATE orders SET status=? WHERE id=? AND tenant_id=? AND status IN " + sh.sql, states.first("order", "in_transit"), r.order_id, T(s), ...sh.args);
    const o = get("SELECT owner, num FROM orders WHERE id=? AND tenant_id=?", r.order_id, T(s));
    const uid = o && /^t\d+:u:(\d+)$/.exec(o.owner || "");
    const buyer = uid ? get("SELECT email FROM users WHERE id=? AND tenant_id=?", Number(uid[1]), T(s)) : null;
    if (buyer && buyer.email) require("./mailer.js").deliver({ tenantId: T(s), channel: "email", to: buyer.email, kind: "order_shipped",
      subject: `Order ${o.num} has shipped`, text: `Your order ${o.num} is on its way with ${r.carrier} (${r.service}).\nTracking number: ${r.tracking_number}` });
    emitEvent(T(s), "order.shipped", { num: o && o.num, tracking: r.tracking_number, carrier: r.carrier }, o && o.num);
  }
  json(res, 200, r);
}
/* the labels already bought for an order, so the console offers them instead of a second purchase */
function apiShippingOrderLabels(req, res, url, s, body, orderId) {
  if (!requireStaff(s, res)) return;
  const o = get("SELECT id, num, status FROM orders WHERE id=? AND tenant_id=?", Number(orderId), T(s));
  if (!o) return bad(res, "Unknown order", 404);
  json(res, 200, { order: o, labels: shippingMod.listTracking(T(s), o.id).map(t => ({ tracking_number: t.tracking_number, carrier: t.carrier_type, service: t.service_type, status: t.status, label_url: t.label_url, created_at: t.created_at })) });
}
/* carrier tracking webhooks: signature first, then the parcel advances */
function apiShippingWebhook(req, res, url, s, body, provider) {
  const raw = typeof req.rawBody === "string" ? req.rawBody : JSON.stringify(body || {});
  if (!shippingMod.verifyWebhook(provider, raw, req.headers)) return bad(res, "signature invalid", 401);
  const r = shippingMod.handleWebhook(provider, body || {});
  if (r.error) return json(res, 200, { ok: true, ignored: r.error });
  if (r.order_id && /^delivered$/.test(r.status)) emitEvent(r.tenant_id, "order.delivered", { order_id: r.order_id }, null);
  json(res, 200, { ok: true });
}

/* ========== Enhanced Helpdesk APIs ========== */
/* chat/SMS intake are customer channels (public, owned by the caller's session so the
   customer can follow the case under /api/support/tickets); replying on a case and agent
   presence are staff actions, scoped to this store. */
function apiHelpdeskChannels(req, res, url, s) {
  json(res, 200, { channels: helpdesk.CHANNELS || ['email','web','chat','sms','phone','social'] });
}
function apiHelpdeskChat(req, res, url, s, body) {
  if (!CFG(s).features.customerService) return bad(res, "Customer service is disabled", 403);
  const r = helpdesk.openChat(T(s), { ...(body || {}), owner: ownerFor(s) });
  json(res, 200, { session_id: r.session_id, ticket_id: r.ticket.id, ref: r.ticket.ref });
}
function apiHelpdeskSMS(req, res, url, s, body) {
  if (!CFG(s).features.customerService) return bad(res, "Customer service is disabled", 403);
  const r = helpdesk.openSMS(T(s), { ...(body || {}), owner: ownerFor(s) });
  json(res, 200, { ticket_id: r.ticket.id, ref: r.ticket.ref });
}
function apiHelpdeskMessage(req, res, url, s, body, ticketId) {
  if (!requireStaff(s, res)) return;
  const [, , name] = actor(s);
  let n;
  try { n = helpdesk.chatMessage(T(s), Number(ticketId), String(name || 'Agent'), String((body || {}).body || ''), !!(body || {}).internal); }
  catch (e) { return bad(res, 'Case not found', 404); }
  json(res, 200, { ok: true, note: n });
}
function apiHelpdeskAgentStatus(req, res, url, s) {
  if (!requireStaff(s, res)) return;
  json(res, 200, { agents: helpdesk.getAgentsStatus(T(s)) });
}
function apiHelpdeskAgentStatusUpdate(req, res, url, s, body) {
  if (!requireStaff(s, res)) return;
  const agent = String((body || {}).agent_id || actor(s)[2] || '');
  if (!agent) return bad(res, 'agent_id required', 400);
  try { json(res, 200, { ok: true, agent: helpdesk.setAgentStatus(T(s), agent, String((body || {}).status || '')) }); }
  catch (e) { bad(res, e.message, 400); }
}

/* ========== Branding System APIs ========== */
function apiPlatformBranding(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  body = body || {};
  if (req.method === 'GET') return json(res, 200, { branding: branding.getGlobalBranding() });
  if (req.method === 'PUT') {
    const b = body;
    if (!b.name && !b.logo && !b.colors && !b.fonts) return bad(res, 'No branding data', 400);
    return json(res, 200, { branding: branding.setGlobalBranding(b) });
  }
  return bad(res, 'Method not allowed', 405);
}
function apiPlatformBrandingPerms(req, res, url, s, body) {
  body = body || {};
  if (!requirePlatform(s, res)) return;
  const tenantId = url.pathname.match(/\/branding-permissions\/(\d+)/)?.[1];
  if (!tenantId) return bad(res, 'tenant_id required', 400);
  if (req.method === 'GET') return json(res, 200, { perms: branding.getStorePermissions(tenantId) });
  if (req.method === 'PUT') return json(res, 200, { perms: branding.setStorePermissions(tenantId, body) });
  return bad(res, 'Method not allowed', 405);
}
function apiStoreBranding(req, res, url, s, body) {
  body = body || {};
  if (!requireStore(s, res)) return;
  /* reading the effective brand is public (the storefront renders it); changing it is a
     store-settings write — the platform's permission flags limit WHICH fields a store may
     change, they never stood in for "who is asking" */
  if (req.method === 'PUT' && !requireSection(s, res, "settings", "write")) return;
  const tenantId = T(s);
  if (req.method === 'GET') {
    const b = branding.getEffectiveBranding(tenantId);
    return json(res, 200, { branding: b });
  }
  if (req.method === 'PUT') {
    const result = branding.setStoreBranding(tenantId, branding.getStorePermissions(tenantId), body);
    if (result.error) return bad(res, result.error, result.code);
    return json(res, 200, { branding: result });
  }
  return bad(res, 'Method not allowed', 405);
}

/* ========== Identity Templates APIs ========== */
function apiIdentityTemplates(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  if (req.method === 'GET') {
    const templates = all("SELECT * FROM platform_identity_templates ORDER BY is_default DESC, created_at");
    return json(res, 200, { templates });
  }
  if (req.method === 'POST') {
    const { name, description, config, is_default } = body || {};
    if (!name) return bad(res, 'name required', 400);
    const isDef = is_default ? 1 : 0;
    const id = Number(run("INSERT INTO platform_identity_templates(name,description,config,is_default) VALUES(?,?,?,?)",
      name, description || '', JSON.stringify(config || {}), isDef).lastInsertRowid);
    return json(res, 200, { ok: true, id });
  }
  if (req.method === 'DELETE') {
    const id = url.pathname.match(/\/identity-templates\/(\d+)/)?.[1];
    if (!id) return bad(res, 'id required', 400);
    run("DELETE FROM platform_identity_templates WHERE id=?", id);
    return json(res, 200, { ok: true });
  }
  return bad(res, 'Method not allowed', 405);
}
function apiIdentityTemplate(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  const id = url.pathname.match(/\/identity-templates\/(\d+)/)?.[1];
  if (!id) return bad(res, 'id required', 400);
  if (req.method === 'GET') {
    const template = get("SELECT * FROM platform_identity_templates WHERE id=?", id);
    if (!template) return bad(res, 'template not found', 404);
    return json(res, 200, { template: { ...template, config: JSON.parse(template.config || '{}') } });
  }
  if (req.method === 'PUT') {
    const { name, description, config, is_default } = body || {};
    if (!name) return bad(res, 'name required', 400);
    const isDef = is_default ? 1 : 0;
    run("UPDATE platform_identity_templates SET name=?,description=?,config=?,is_default=? WHERE id=?",
      name, description || '', JSON.stringify(config || {}), isDef, id);
    return json(res, 200, { ok: true });
  }
  return bad(res, 'Method not allowed', 405);
}

/* Apply a global identity template to ANY store — the platform console configures every
   tenant, so the target is a body parameter (validated against the tenants table), never a
   hardcoded store. Mirrors the provisioning path's apply logic exactly so the two cannot
   drift. Platform-only: writing another store's identity settings is a platform action. */
function apiIdentityTemplateApply(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  const id = url.pathname.match(/\/identity-templates\/(\d+)\/apply$/)?.[1];
  if (!id) return bad(res, 'template id required', 400);
  const tmpl = get("SELECT config FROM platform_identity_templates WHERE id=?", id);
  if (!tmpl) return bad(res, 'template not found', 404);
  const tid = Number(body && body.tenant_id);
  const t = get("SELECT id, slug FROM tenants WHERE id=?", tid);
  if (!t) return bad(res, 'unknown tenant_id', 400);
  const config = J(tmpl.config, {});
  const identity = require("./identity.js");
  const settings = identity.setIdentitySettings(tid, config);
  let providers = 0;
  if (Array.isArray(config.providers)) for (const p of config.providers) { try { identity.upsertIdentityProvider(tid, p); providers++; } catch (e) { } }
  audit(T(s) || null, 'platform', s.platform_admin.id, s.platform_admin.email, 'identity.template.apply', 'tenant', tid, { template: Number(id), providers });
  return json(res, 200, { ok: true, tenant_id: tid, slug: t.slug, settings, providers });
}

/* ========== Identity Provider Types (registry vocabulary) ========== */
function apiIdentityProviderTypes(req, res, url, s) {
  if (!requireAdmin(s, res)) return;
  const identity = require("./identity.js");
  if (req.method === 'GET') return json(res, 200, { types: identity.getProviderTypes() });
  return bad(res, 'Method not allowed', 405);
}
/* a new authentication KIND is platform vocabulary — authoring it is a platform action, and
   the console's provider-type form is the only writer. Idempotent by key. */
function apiIdentityProviderTypeCreate(req, res, url, s, body) {
  if (!requirePlatform(s, res)) return;
  const identity = require("./identity.js");
  const r = identity.createProviderType(body || {});
  if (!r.ok) return bad(res, r.error, 400);
  return json(res, 200, r);
}

/* ======================================================================
   PLATFORM REGISTRY AUTHORING — every `meta_lists` vocabulary, auto-discovered
   The surface never enumerates list names; lib/registry.js scans the table, so a
   registry created by any engine (or a future seed) is authorable here as soon as
   it exists. This is what turns "add a platform mode" into a console action: the
   registration walk, every gTable select and every engine reads the same rows.
   ====================================================================== */
function apiPlatformRegistries(req, res, url, s) {
  if (!requirePlatformSection(s, res, "registries", "read")) return;
  const registry = require("./registry.js");
  return json(res, 200, { registries: registry.listAll() });
}
function apiPlatformRegistry(req, res, url, s, body) {
  const name = decodeURIComponent(url.pathname.match(/\/registries\/([^/]+)$/)?.[1] || "");
  if (!name) return bad(res, "registry name required", 400);
  const registry = require("./registry.js");
  if (req.method === "GET") {
    if (!requirePlatformSection(s, res, "registries", "read")) return;
    const items = registry.readList(name);
    if (items === null) return bad(res, "Unknown registry", 404);
    return json(res, 200, { name, items, usage: name === "deployModes" || name === "industries" });
  }
  if (req.method === "POST") {
    /* upsert one entry, keyed */
    if (!requirePlatformSection(s, res, "registries", "write")) return;
    const item = body && body.item;
    if (!item) return bad(res, "item required", 400);
    const r = registry.saveItem(name, item);
    if (!r.ok) return bad(res, r.error, 400);
    audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "registry.entry.save", "registry", name, { key: r.key });
    return json(res, 200, r);
  }
  return bad(res, "Method not allowed", 405);
}
/* AUTO-RECOMMEND: a skeleton entry inferred from the list's own live contents, so the
   authoring form is scaffolded from data instead of a hardcoded schema */
function apiPlatformRegistryRecommend(req, res, url, s, body) {
  if (!requirePlatformSection(s, res, "registries", "read")) return;
  const name = decodeURIComponent(url.pathname.match(/\/registries\/([^/]+)\/recommend$/)?.[1] || "");
  if (!name) return bad(res, "registry name required", 400);
  const registry = require("./registry.js");
  return json(res, 200, { name, item: registry.recommend(name, String((body && body.label) || "")) });
}
function apiPlatformRegistryEntryDelete(req, res, url, s, body, name, key) {
  if (!requirePlatformSection(s, res, "registries", "write")) return;
  const registry = require("./registry.js");
  const r = registry.deleteItem(decodeURIComponent(name || ""), decodeURIComponent(key || ""));
  if (!r.ok) return bad(res, r.error, r.error && /In use/.test(r.error) ? 409 : 400);
  audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "registry.entry.delete", "registry", r.key, { list: name });
  return json(res, 200, r);
}

/* ========== Dynamic Policy Management APIs ========== */
function apiPlatformPolicies(req, res, url, s) {
  if (!requirePlatform(s, res)) return;
  if (req.method === 'GET') return json(res, 200, { policies: policies.getPolicies() });
  return bad(res, 'Method not allowed', 405);
}
function apiPlatformPolicy(req, res, url, s, body) {
  if (!requirePlatformSection(s, res, "policies", req.method === "GET" ? "read" : "write")) return;
  const category = url.pathname.match(/\/policies\/([^.]+)/)?.[1];
  if (!category) return bad(res, 'category required', 400);
  if (req.method === 'GET') return json(res, 200, { policy: policies.getPolicy(category) });
  if (req.method === 'PUT') { const result = policies.setPolicy(category, body || {}); return json(res, 200, { policy: result }); }
  if (req.method === 'DELETE') { const result = policies.deletePolicy(category); if (!result.ok) return bad(res, result.error, 404); return json(res, 200, result); }
  return bad(res, 'Method not allowed', 405);
}
