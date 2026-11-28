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
/* the shopper and brand layer: lists, price/stock alerts, pickup points, rich product
   content and the brand registry — each an atom of lib/capabilities.js */
const lists = require("./lists.js");
const alerts = require("./alerts.js");
const pickup = require("./pickup.js");
const richcontent = require("./richcontent.js");
const brandreg = require("./brandreg.js");
/* a bag line's terms (options, an agreed price, a booking…): each engine registers its own */
const lineterms = require("./lineterms.js");
/* the platform-type engines; each registers its own line term or order hook on load */
const options = require("./options.js");
const bookings = require("./bookings.js");
const listings = require("./listings.js");
const negotiation = require("./negotiation.js");
const auctions = require("./auctions.js");
const conversations = require("./conversations.js");
const groupbuy = require("./groupbuy.js");
const substitutions = require("./substitutions.js");
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
  /* a store API key is the store's staff, with its role (server.js keySession) */
  if (s.api_key) return true;
  if (!s.user_id) return false;
  const u = get("SELECT role, disabled FROM users WHERE id=? AND tenant_id=?", s.user_id, T(s));
  /* a store's staff carry their authority only once their second factor is confirmed (lib/mfa.js) */
  return !!(u && u.role === "admin" && !u.disabled) && require("./mfa.js").state("user", s.user_id, s.mfa_at) === "ok";
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
  "admin/operations": "planning", "admin/ops": "planning", "admin/mobility": "rides", "admin/trips": "trips",
  "admin/products": "products", "admin/attributes": "products", "admin/relationships": "products",
  "admin/taxonomy": "taxonomy", "admin/skus": "skus", "admin/inventory": "skus", "admin/transfers": "skus",
  "admin/serialized": "serialized",
  offers: "offers", goip: "offers", marketing: "offers",
  "admin/sellers": "sellers", "admin/rfqs": "rfqs", "admin/settlements": "settlements",
  "admin/contracts": "contracts", "admin/tenders": "tenders", "admin/tax": "finance", "admin/books": "books", "admin/purchasing": "purchasing", "admin/crm": "crm", "admin/campaigns": "campaigns", "admin/consulting": "consulting", "admin/leave": "leave", "admin/assets": "fixed_assets", "admin/budgets": "budgets", "admin/mrp": "mrp",
  "admin/orders": "orders", "admin/compliance": "compliance", "admin/privacy": "privacy",
  "admin/gateways": "payments", "admin/gateway": "payments", "admin/payments": "payments",
  "admin/ai-gateways": "ai", ai: "ai", "admin/billing": "billing", billing: "billing",
  "admin/audit": "audit", "admin/chain": "audit", "admin/monitor": "monitor", "admin/entity-usage": "monitor",
  "admin/mode": "settings", "admin/settings": "settings", "admin/departments": "settings", "admin/banners": "content",
  "admin/cards": "content", "admin/custom-providers": "settings", "admin/sso": "settings",
  "admin/identity-provider-types": "settings", "admin/identity-providers": "settings", "admin/identity-settings": "settings",
  env: "settings", affiliate: "affiliate", sitemap: "sitemap", shipping: "shipping", "admin/webhooks": "webhooks", "admin/pickup": "pickup", "admin/rich-content": "richcontent", "admin/brand-registry": "brandreg", "admin/options": "prodoptions", "admin/bookings": "bookings", "admin/price-offers": "negotiation", "admin/auctions": "auctions", "admin/listings": "listings", "admin/conversations": "conversations", "admin/group-buys": "groupbuy", "admin/substitutions": "substitutions"
};
/* routes whose third segment names a kind, resolved to the kind's section */
const STORE_ROUTE_KINDS = {
  /* /admin/deliverables/:kind/… names the kind; /admin/deliverables/item/:id the deliverable */
  "admin/deliverables": parts => require("./deliverables.js").sectionOf(parts[2], parts[3]),
  /* /admin/cases/:id names the case, whose kind names its section */
  "admin/cases": parts => require("./cases.js").sectionOf(parts[2])
};
/* routes every staff member may use on their OWN account */
const STORE_ROUTE_SELF = new Set(["admin/account"]);
function storeRouteSection(pathname) {
  const p = String(pathname || "").replace(/^\/api\//, "");
  const parts = p.split("/");
  const two = parts.slice(0, 2).join("/");
  if (STORE_ROUTE_SELF.has(two)) return null;
  /* a route that names a kind of something belongs to that kind's own section (its registry row) */
  const byKind = STORE_ROUTE_KINDS[two] && STORE_ROUTE_KINDS[two](parts);
  if (byKind) return byKind;
  return STORE_ROUTE_SECTION[two] || require("./capabilities.js").ROUTES[two] || STORE_ROUTE_SECTION[parts[0]] || undefined;
}
function staffGrant(s, section) {
  const u = s.api_key ? { staff_role: s.api_key.role_key, perms: "{}" } : get("SELECT staff_role, perms FROM users WHERE id=? AND tenant_id=?", s.user_id, T(s));
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
function _userRow(s) { if (s.api_key) return { id: null, role: "admin", staff_role: s.api_key.role_key, perms: "{}" }; return s.user_id ? get("SELECT id,role,staff_role,perms FROM users WHERE id=? AND tenant_id=?", s.user_id, T(s)) : null; }
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
  if (s.api_key) return ["apikey", s.api_key.id, "key: " + s.api_key.name];
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
  /* what any shopper pays now (a sale, a show): the price before it is shown beside it */
  const now = p.tenant_id ? features.price({ tid: p.tenant_id, owner: null, product: p, qty: 1, unit: Number(p.price) }) : { unit: Number(p.price) };
  const cut = now.unit < Number(p.price);
  return { ...o, p: money2(cm, cut ? now.unit : o.p), l: cut ? money2(cm, Math.max(o.l || 0, o.p)) : o.l != null ? money2(cm, o.l) : null, sale: cut ? now.label : undefined, pricing_rules: pr };
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
  const list = enabledGateways(T(s)).filter(g => registry.supports(g.id, ctx.country) && canSettle(T(s), g));
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
/* simulated settlement is a development/sandbox convenience: never in production (the
   LX_ALLOW_SIMULATED_PAYMENTS opt-in is gone — a live store takes money through a real gateway) */
function simulatedSettlementAllowed() {
  return process.env.NODE_ENV !== "production";
}
async function settlePayment(tenantId, gw, amount, currency, idempotency, extra) {
  const fee = +((amount * (gw.feePct || 0) / 100 + (gw.feeFixed || 0)).toFixed(2));
  const live = !outboundOffline() && gw.mode === "live" ? gatewaySecrets(tenantId, gw.id) : null;
  if (live && live.cfg && Object.keys(live.cfg).length) {
    const r = await connect.pay({ provider: gw.id, config: live.cfg, amount, currency, idempotency, extra: extra || {} });
    if (r.live && r.ok) return { ref: r.id || `${gw.id}_${Date.now()}`, fee, status: stIs("payment", r.status, "settled") ? r.status : states.first("payment", "held"), live: true, redirect: r.redirect || null };
    if (r.live && !r.ok) return { ref: "failed_" + crypto.randomBytes(6).toString("hex"), fee: 0, status: states.first("payment", "failure"), live: true, error: r.error };
  }
  /* nothing to collect (paid in full from a balance) */
  if (!(amount > 0) && !simulatedSettlementAllowed()) return { ref: "balance_" + crypto.randomBytes(7).toString("hex"), fee: 0, status: states.first("payment", "settled") };
  /* in production only money settled offline (cash, a transfer) goes without a live gateway: it
     stays pending until staff record it. A gateway with no live credentials takes no order. */
  if (!canSettle(tenantId, gw)) return { ref: "failed_" + crypto.randomBytes(6).toString("hex"), fee: 0, status: states.first("payment", "failure"), error: gw.name + " is not connected" };
  const sim = simulateGateway(gw, amount); sim.fee = fee; return sim;
}
const offlineMethods = () => registry.list("offlinePaymentMethods").map(m => typeof m === "string" ? m : m.key);
/* can this gateway take an order's money: it is settled offline, it is live with credentials on
   file, or this is not production (where it is simulated) */
function canSettle(tenantId, gw) {
  const ms = gw.methods || [], off = offlineMethods();
  if (ms.length && ms.every(m => off.includes(m))) return true;
  if (simulatedSettlementAllowed()) return true;
  if (gw.mode !== "live" || outboundOffline()) return false;
  const live = gatewaySecrets(tenantId, gw.id);
  return !!(live && live.cfg && Object.keys(live.cfg).length && connect.ready({ provider: gw.id, config: live.cfg }));
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



/* ---------- UNIVERSAL DASHBOARD & REPORTING ENGINE (Architecture1 §394/§395) ----------
   Dashboards and reports are DATA: the routes below are the thinnest possible CRUD +
   render surface over lib/dashboards.js. There is deliberately no per-dashboard route —
   a new dashboard is a row, not an endpoint, which is what §394 declares. */
const dashboards = require("./dashboards.js");
/* changing a board (deleting it, or its widgets) requires OWNING it: this store's own board,
   or — for a platform template (tenant_id NULL) — a platform admin. Reading is wider (shared
   'all' boards are visible to every store), but visible was being treated as writable. */
function ownsDashboard(s, d) {
  return d.tenant_id == null ? !!s.platform_admin : Number(d.tenant_id) === T(s);
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
function isTls(req) { return sec.httpsRequest(req); }
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
  run("UPDATE sessions SET user_id=?, mfa_at=NULL WHERE sid=?", userId, s.sid);
  s.mfa_at = null;
  s.user_id = userId;
  run("UPDATE users SET last_login=datetime('now') WHERE id=?", userId);
  mergeOwner("t" + T(s) + ":s:" + s.sid, "t" + T(s) + ":u:" + userId);
  try { mods.walletMerge("t" + T(s) + ":s:" + s.sid, "t" + T(s) + ":u:" + userId); } catch (e) { }
  rotateSession(req, res, s);
  logAction(s, action, "user", userId, detail || {}, req);
}
/* the address a person is sent back to (a reset link, a payment return page). Never taken
   from the request's Host header in production — a forged Host would mail a victim a link
   to an attacker's site carrying their reset token. The store's own domain wins; else the
   platform's own store's domain with the store chosen by ?store= (both set in the platform
   console's store form — LX_PUBLIC_URL used to carry the platform's address); only outside
   production does the request's own origin stand in, so local development works. */
const hostOf = d => String(d || "").replace(/^https?:\/\//, "").replace(/\/+$/, "");
function platformDomain() { const m = masterTenant(); return m ? hostOf(m.domain) : ""; }
function publicOrigin(req, s) {
  const dom = hostOf(s.tenant.domain);
  if (process.env.NODE_ENV === "production") {
    if (dom) return { origin: "https://" + dom, storeQuery: "" };
    const base = platformDomain();
    return base ? { origin: "https://" + base, storeQuery: "store=" + encodeURIComponent(s.tenant.slug) } : null;
  }
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
/* how many can be bought, and the day a pre-ordered one ships */
function preorderView(p) { const pre = p.tenant_id ? require("./preorders.js").open(p.tenant_id, p.id) : null; return pre ? { st: pre.left, preorder: { ships_on: pre.ships_on } } : { st: p.stock }; }
function publicProduct(p) {
  return {
    id: p.id, t: p.title, b: p.brand, d: p.dept, p: p.price, l: p.list_price, r: p.rating, c: p.ratings_count,
    ...preorderView(p),
    e: p.emoji, h: p.hue, pr: !!p.priority, fl: p.flags || "", kw: p.keywords, about: p.about || [],
    type: p.type || require("./defaults.js").of("productTypes"), node_id: p.node_id || null,
    identity: J(p.identity), attrs: J(p.attrs), vertical: J(p.vertical), media: J(p.media, []),
    seo: J(p.seo), pricing_rules: J(p.pricing_rules), logistics: J(p.logistics), tax_rule: J(p.tax_rule), uom: J(p.uom), packaging: J(p.packaging, [])
  };
}
/* a shopper may only report a CLICK, once per ad per day — conversions are billed from the
   order pipeline, never declared by the client, and repeated clicks were billed every time */
const AD_EVENT_KINDS = require("./meta.js").AD_EVENT_KINDS;

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
  const rows = all("SELECT product_id, qty, sku_id, line, terms FROM cart_items WHERE owner=? ORDER BY added_at", owner);
  const items = []; let sub = 0, count = 0; const lines = []; const promoItems = [];
  for (const r of rows) {
    const p = get("SELECT * FROM products WHERE tenant_id=? AND id=?", T(s), r.product_id);
    if (!p) continue;
    p.about = all("SELECT text FROM product_bullets WHERE tenant_id=? AND product_id=? ORDER BY pos", T(s), p.id).map(x => x.text);
    const sku = r.sku_id ? get("SELECT id, code, name, price FROM skus WHERE id=? AND tenant_id=? AND active=1", r.sku_id, T(s)) : null;
    const cp = buyerEmail ? contractPriceFor(T(s), buyerEmail, p.id, r.qty) : null;
    const listUnit = cp != null ? cp : (sku && sku.price != null ? Number(sku.price) : effectivePrice(p, r.qty));
    /* a line's terms price it (lib/lineterms.js): an agreed price replaces the list price,
       options add to it; a term that no longer holds is reported, and checkout refuses it */
    const lineTerms = J(r.terms, {});
    const lt = Object.keys(lineTerms).length ? lineterms.priceLine({ tid: T(s), owner, product: p, qty: r.qty }, lineTerms, listUnit) : { unit: listUnit, labels: [], problems: [], maxQty: Infinity };
    /* a price another term set is not changed; otherwise the lowest any feature gives */
    const ext = cp != null || lt.unit !== listUnit ? { unit: lt.unit, label: "" } : features.price({ tid: T(s), owner, product: p, qty: r.qty, unit: lt.unit });
    const unit = +ext.unit.toFixed(4);
    const fr = features.rule({ tid: T(s), owner, product: p, qty: r.qty, terms: lineTerms, sku: r.sku_id });
    const each = features.engines.get("sell_by_weight").count(T(s), p.id, lineTerms);
    /* what can still be bought: a withdrawn item, or one the shelf no longer holds, stops checkout */
    const onShelf = p.lifecycle === "published" && !p.deleted_at ? Math.floor(stock.available(T(s), p, r.sku_id) / each) : 0;
    const lineProblems = onShelf > 0 ? lt.problems.concat(fr.problems) : lt.problems.concat(fr.problems, p.lifecycle === "published" && !p.deleted_at ? "sold out" : "no longer sold");
    const most = Math.min(lt.maxQty, fr.maxQty, onShelf > 0 ? onShelf : Infinity);
    items.push({ product: storeView(p, c.commerce), qty: r.qty, sku_id: sku ? sku.id : null, sku: sku ? { id: sku.id, code: sku.code, name: sku.name } : null, unit: money2(c.commerce, unit), unitBase: unit,
      line: r.line || "", line_terms: lineTerms, term_labels: ext.label ? lt.labels.concat(ext.label) : lt.labels, each, problems: lineProblems, max_qty: isFinite(most) ? most : null });
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
  const wBal = require("./gates.js").on(T(s), "checkout.wallet") ? require("./wallet.js").checkoutAvailable(T(s), owner) : 0;
  const surcharge = logisticsSurcharge(s, lines);
  /* the store's fees (lib/fees.js) and the shopper's tip (lib/tips.js) */
  const ch = bagCharges(T(s), owner, afterPromo, freeShip, items, s.__co);
  const gift = Math.min(wBal, afterPromo + shipFee + surcharge + ch.total);
  const tax = computeTax(s, c, lines, afterPromo, shipFee + surcharge + ch.taxable - gift);
  const total = +(afterPromo + shipFee + surcharge + ch.total + tax - gift).toFixed(2);
  const m = c.commerce;
  return { items, saved, count, subBase: sub, sub: money2(m, sub), discountBase: promo.discount, discount: money2(m, promo.discount), creditsEarned: promo.credits || 0, redemptions: promo.redemptions || [], shipBase: shipFee, surchargeBase: surcharge, giftBase: gift, taxBase: tax, totalBase: total, promos: promo.applied, couponsOpen: !!(c.features && c.features.coupons) && !!sec.policy().provisioning.couponsAllowed, shipFee: money2(m, shipFee), gift: money2(m, gift), tax: money2(m, tax), total: money2(m, total), qualifies: afterPromo >= c.commerce.freeShipThreshold || freeShip, freeShip,
    charges: ch.lines.map(l => ({ ...l, amountBase: l.amount, amount: money2(m, l.amount) })), chargesBase: ch.total, tips: require("./tips.js").vocabulary(T(s)), tip: require("./tips.js").tipOf(T(s), owner),
    currency: { code: m.currency, symbol: m.symbol, decimals: m.decimals, fx: m.fx, base: m.baseCurrency, threshold: c.commerce.freeShipThreshold } };
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
  /* a pickup point instead of an address (lib/pickup.js): the point's own fee and arrival,
     never a carrier rate; free-shipping rules waive the fee where the capability says so */
  if (b.pickup_point != null && String(b.pickup_point) !== "") {
    let pq;
    try { pq = pickup.quote(T(s), b.pickup_point); }
    catch (e) { if (!e || !e.status) throw e; return Object.assign(out, { error: e.message, errorStatus: e.status, shipBase: 0, eta, free }); }
    out.shipBase = free && pq.free_shipping_applies ? 0 : +Number(pq.fee || 0).toFixed(2);
    return Object.assign(out, { carrier: "pickup:" + pq.point.code, source: "pickup", pickup: pq.point, eta: pq.eta != null ? pq.eta : eta, free: out.shipBase === 0 && free });
  }
  /* where the store delivers, and when the shopper would like it */
  const area = require("./serviceable-areas.js").check(T(s), b.zip || s.zip);
  if (!area.served && String(b.address || "").trim()) return Object.assign(out, { error: caps.cap(T(s), "serviceable_areas").message || "Not delivered there", errorStatus: 422, shipBase: 0, eta, free });
  let slot = null;
  if (b.final || b.delivery_slot) { try { slot = require("./delivery-windows.js").choose(T(s), b.delivery_slot); } catch (e) { if (!e.status) throw e; return Object.assign(out, { error: e.message, errorStatus: e.status, shipBase: 0, eta, free }); } }
  const fd = features.delivery({ tid: T(s), owner: ownerFor(s), items: cart.items, body: b, carrier });
  if (fd.problem && (b.final || String(b.address || "").trim())) return Object.assign(out, { error: fd.problem, errorStatus: 422, shipBase: 0, eta, free });
  const extra = +(Number(area.fee || 0) + (slot ? Number(slot.fee || 0) : 0) + fd.fee).toFixed(2);
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
  /* what the place and the chosen time add is charged even where delivery itself is free */
  const none = free || fd.free;
  out.shipBase = +((none ? 0 : Number(shipBase || 0)) + extra).toFixed(2);
  out.eta = eta + (Number(area.extra_days) || 0) + fd.days; out.free = none && !extra; out.slot = slot;
  return out;
}
/* what an order is charged beyond its lines: each feature's own lines (fees, a tip), summed */
function bagCharges(tid, owner, net, freeShip, items, body) {
  const parts = [require("./fees.js").forBag(tid, owner, { net, freeShip }), require("./tips.js").forBag(tid, owner), { lines: net > 0 ? features.charges({ tid, owner, net, items, body }) : [] }];
  const lines = parts.flatMap(p => p.lines);
  return { lines, total: +lines.reduce((n, l) => n + l.amount, 0).toFixed(2), taxable: +lines.filter(l => l.taxable).reduce((n, l) => n + l.amount, 0).toFixed(2) };
}
function checkoutTotals(s, c, cart, shipFee) {
  const lines = cart.items.map(x => ({ unitBase: x.unitBase, qty: x.qty, logistics: x.product.logistics, tax_rule: x.product.tax_rule }));
  const subBase = +lines.reduce((n, l) => n + l.unitBase * l.qty, 0).toFixed(2);
  const netBase = +(subBase - (cart.discountBase || 0)).toFixed(2);
  const surcharge = logisticsSurcharge(s, lines);
  const wBal = require("./gates.js").on(T(s), "checkout.wallet") ? require("./wallet.js").checkoutAvailable(T(s), ownerFor(s)) : 0;
  const ch = bagCharges(T(s), ownerFor(s), netBase, !!cart.freeShip, cart.items, s.__co);
  const giftUsed = Math.min(wBal, netBase + shipFee + surcharge + ch.total);
  const tax = computeTax(s, c, lines, netBase, shipFee + surcharge + ch.taxable - giftUsed);
  const total = +(netBase + shipFee + surcharge + ch.total + tax - giftUsed).toFixed(2);
  return { lines, subBase, netBase, surcharge, giftUsed, tax, total, charges: ch };
}
/* one checkout per buyer at a time. The wallet balance and the cart are read before the
   (awaited) payment and written after it, so two concurrent checkouts both spent the same
   balance and the same cart. The lock serialises them; the wallet is also decremented
   relative to its current value rather than set to a stale absolute one. */
const CHECKOUT_LOCKS = new Set();
async function apiCheckoutOnce(req, res, url, s, body) {
  const c = { ...CFG(s), commerce: commerceOf(s) };
  s.__co = { ...body, final: true };
  let cart;
  try { cart = cartPayload(s); } catch (e) { if (!e.status) throw e; return bad(res, e.message, e.status); }
  if (!cart.items.length) return bad(res, "Bag is empty", 400);
  /* a line whose terms no longer hold (an offer expired, a hold lapsed), or that holds more than
     its terms allow, is refused with its reason */
  const broken = cart.items.find(x => (x.problems || []).length || (x.max_qty != null && x.qty > x.max_qty));
  if (broken) return bad(res, broken.product.t + ": " + ((broken.problems || []).join("; ") || "at most " + broken.max_qty + " of this line"), 409);
  if (require("./gates.js").setting(T(s), "checkout.login_required") === true && !s.user_id)
    return bad(res, require("./gates.js").message("checkout.login_required"), 403);
  const name = String(body.name || "").trim();
  /* collecting from a pickup point needs a name, not an address — the point is the address */
  /* where the order's news goes: the account's address, else the one a guest gives */
  const guestEmail = s.user_id ? "" : String(body.email || "").trim().toLowerCase().slice(0, 200);
  if (guestEmail && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(guestEmail)) return bad(res, "Please enter a valid email", 422);
  /* a business buyer's tax number, for the invoice — checked against its country's format */
  const buyerTaxId = String(body.tax_id || "").replace(/\s+/g, "").toUpperCase().slice(0, 30);
  if (buyerTaxId && !taxmod.validateNumber(c.commerce.country, buyerTaxId).ok) return bad(res, "That tax number is not valid", 422);
  const viaPickup = body.pickup_point != null && String(body.pickup_point) !== "";
  if (!name || (!viaPickup && (!String(body.address || "").trim() || !String(body.city || "").trim()))) return bad(res, "Shipping address is incomplete", 422);
  const plan = planFor(T(s));
  const monthOrders = get("SELECT COUNT(*) c FROM orders WHERE tenant_id=? AND created_at >= date('now','start of month')", T(s)).c;
  if (monthOrders >= plan.max_orders_month) return bad(res, "Monthly order limit reached on the " + plan.name + " plan — upgrade to continue selling", 402);
  const gwId = String(body.gateway || "");
  const ship = await shippingFor(s, c, cart, { ...body, final: true });
  if (ship.error) return bad(res, ship.error, ship.errorStatus);
  const carrier = ship.carrier, shipFee = ship.shipBase, eta = ship.eta;
  const pp = ship.pickup;
  const address = pp ? pp.name + ", " + pp.address : String(body.address || "").trim();
  const city = pp ? String(pp.city || "") : String(body.city || "").trim();
  const { netBase, surcharge, giftUsed, tax, total, charges } = checkoutTotals(s, c, cart, shipFee);
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
  /* the gift balance the order spends is held before the order is written, and captured once it is */
  /* the balance the order spends is held across the checkout wallets (gift balance first, as their
     priority says) before the order is written, and captured once it is */
  let giftHolds = null;
  if (giftUsed > 0) {
    try { giftHolds = require("./wallet.js").holdForOrder(T(s), ownerFor(s), null, giftUsed, "order:" + num); }
    catch (e) { return bad(res, e.message, e.status || 402); }
  }
  const r = run(`INSERT INTO orders(tenant_id,owner,num,name,address,city,state,zip,ship_option,pay_method,sub,ship_fee,gift_used,tax,total,eta_days,status,currency,fx)
                 VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,'processing',?,?)`,
    T(s), ownerFor(s), num, name, address, city, pp ? String(pp.region || "") : String(body.state || ""), pp ? String(pp.postcode || "") : String(body.zip || s.zip), carrier, gw.id, money2(m, netSub), money2(m, shipFee), money2(m, giftUsed), money2(m, tax), money2(m, total), eta, m.currency, m.fx);
  const oid = Number(r.lastInsertRowid);
  const said = letters.heard(req, url, T(s));
  run("UPDATE orders SET lang=? WHERE id=?", said, oid);
  if (s.user_id) run("UPDATE users SET lang=? WHERE id=? AND COALESCE(lang,'')<>?", said, s.user_id, said);
  if (guestEmail) run("UPDATE orders SET email=? WHERE id=?", guestEmail, oid);
  if (body.country) run("UPDATE orders SET country=? WHERE id=?", String(body.country).toUpperCase().slice(0, 2), oid);
  if (buyerTaxId) run("UPDATE orders SET buyer_tax_id=? WHERE id=?", buyerTaxId, oid);
  /* the fees and tip this order was charged stay on it; the tip is spent */
  if (charges.lines.length) { run("UPDATE orders SET charges=? WHERE id=?", JSON.stringify(charges.lines.map(l => ({ ...l, amount: money2(m, l.amount) }))), oid); require("./tips.js").taken(T(s), ownerFor(s)); }
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
      require("./order-records.js").removing(oid);
      run("DELETE FROM orders WHERE id=?", oid);
      if (giftHolds) for (const h of giftHolds) { try { require("./wallet.js").release(T(s), ownerFor(s), h.id, ownerFor(s)); } catch (e) { console.error("hold release:", e.message); } }
      logAction(s, "risk.block", "risk_event", r0.id, { score: r0.score });
      return bad(res, "This order was blocked by our risk system. Please contact support if this is a mistake (ref " + r0.id + ")", 403);
    }
    if (risk.effectOf(r0.decision) === "hold") logAction(s, "risk.hold", "risk_event", r0.id, { score: r0.score });
    s.__risk = { id: r0.id, score: r0.score, decision: r0.decision };
  }
  for (const it of cart.items) run("INSERT INTO order_items(order_id,product_id,qty,price,sku_id,terms) VALUES(?,?,?,?,?,?)", oid, it.product.id, it.qty, it.sku_id || Object.keys(it.line_terms || {}).length ? it.unit : it.product.p, it.sku_id || null,
    JSON.stringify(Object.keys(it.line_terms || {}).length ? { values: it.line_terms, labels: it.term_labels } : {}));
  /* the order is on the kernel with its lines and its buyer (lib/order-records.js) */
  require("./order-records.js").change(oid, () => null);
  /* the shelf, before any money: what cannot be had is never charged */
  const undo = why => {
    try { orders.paymentFailed(T(s), get("SELECT * FROM orders WHERE id=?", oid), why); } catch (e) { console.error("order undo:", e.message); }
    if (giftHolds) for (const h of giftHolds) { try { require("./wallet.js").release(T(s), ownerFor(s), h.id, ownerFor(s)); } catch (e) { console.error("hold release:", e.message); } }
  };
  try { stock.take(T(s), oid, cart.items.map(it => ({ product_id: it.product.id, sku_id: it.sku_id, qty: it.qty * (it.each || 1) }))); }
  catch (e) { undo("out of stock"); if (!e.status) throw e; return bad(res, e.message, e.status); }
  if (ship.slot) { try { require("./delivery-windows.js").book(T(s), oid, ship.slot); } catch (e) { undo("delivery time taken"); if (!e.status) throw e; return bad(res, e.message, e.status); } }
  /* charged in the currency the shopper is shown: the total is kept in the store's base currency */
  const charge = money2(m, total);
  const sim = await settlePayment(T(s), gw, charge, c.commerce.currency, num,
    { returnUrl: publicLink(req, s, "orders.html", { paid: num }) || "", cancelUrl: publicLink(req, s, "checkout.html", { cancelled: num }) || "", ...features.payment({ tid: T(s), body, gateway: gw.id, net: netBase }) });
  require("./row-records.js").created("payment", () => run("INSERT INTO payments(tenant_id,kind,order_id,gateway,method,amount,currency,fee,status,txn_ref,live) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
    T(s), "order", oid, gw.id, method, charge, c.commerce.currency, sim.fee, sim.status, sim.ref, sim.live ? 1 : 0));
  if (stIs("payment", sim.status, "failure")) { undo("payment declined"); return bad(res, "Payment was declined by the gateway: " + (sim.error || "declined"), 402); }
  /* a place at the pickup point, and the one-time code the shopper collects with */
  if (pp) pickup.reserve(T(s), oid, pp.id, ownerFor(s));
  /* each termed line's engine acts on the order (a booking confirmed, an offer used…), then
     every engine's order hook (a listed item sold…) */
  lineterms.place({ tid: T(s), owner: ownerFor(s), orderId: oid, orderNum: num, currency: c.commerce.currency },
    cart.items.map(it => ({ product: it.product, qty: it.qty, unit: it.unitBase, line: it.line, terms: it.line_terms })));
  features.placed({ tid: T(s), owner: ownerFor(s), order: get("SELECT * FROM orders WHERE id=?", oid), items: cart.items, body });
  const pickedUp = pp ? pickup.forOrder(T(s), oid, ownerFor(s)) : null;
  /* a live payment not yet confirmed (the shopper still has to complete it on the provider's
     page, or the provider reports it pending): the order waits for the provider's webhook
     before anyone fulfils it */
  const awaitingPayment = !!(sim.live && stIs("payment", sim.status, "awaiting"));
  if (awaitingPayment) require("./order-records.js").change(oid, () => run("UPDATE orders SET status=? WHERE id=?", states.first("order", "awaiting_payment"), oid));
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
    const prof = vtOf[ivk] || vtOf["*"] || {};
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
  if (giftHolds) require("./wallet.js").captureOrder(T(s), giftHolds, "order:" + num, ownerFor(s));
  try { offers.redeem({ tenantId: T(s), owner: ownerFor(s), channel: require("./defaults.js").of("offerChannels"), currency: c.commerce.currency }, { credits: cart.creditsEarned || 0, redemptions: cart.redemptions || [] }, { order_id: oid, order_num: num }); } catch (e) { console.error("offer redeem:", e.message); }
  logAction(s, "checkout.complete", "order", num, { gateway: gw.id, method, total, txn: sim.ref }, req);
  notify(T(s), `New order ${num}`, `${name} — ${total} ${c.commerce.currency} via ${gw.name}`);
  {
    const buyer = s.user_id ? get("SELECT email FROM users WHERE id=? AND tenant_id=?", s.user_id, T(s)) : { email: guestEmail };
    const lang = letters.langOf(T(s), { userId: s.user_id, order: { lang: said } });
    if (buyer && buyer.email) require("./mailer.js").deliver({ tenantId: T(s), channel: "email", to: buyer.email, kind: "order_confirmation",
      ...letters.write("order_confirmation", lang, { num, store: s.tenant.name, name, total: money2(m, total) + " " + m.currency, payment: gw.name + " (" + sim.status + ")", collect: pickedUp ? address + (city ? ", " + city : "") + (pp.hours ? " (" + pp.hours + ")" : "") : "", code: pickedUp ? pickedUp.code : "", address: pickedUp ? "" : name + ", " + address + ", " + city, days: eta, items: cart.items.map(x => x.qty + " × " + x.product.t).join("\n") }) });
  }
  try { run("UPDATE orders SET trace_id=? WHERE id=?", s.trace || null, oid); } catch (e) { }
  emitEvent(T(s), "order.created", { num, total: money2(m, total), currency: m.currency }, num);
  if (stIs("payment", sim.status, "settled")) emitEvent(T(s), "order.paid", { num, total: money2(m, total), txn_ref: sim.ref, gateway: gw.id }, num);
  json(res, 200, { order: { num, total: money2(m, total), currency: m.currency, fx: m.fx, sub: money2(m, netSub), discount: money2(m, cart.discountBase || 0), surcharge: money2(m, surcharge), promos: cart.promos, shipFee: money2(m, shipFee), shipping: { source: ship.source, carrier, service: ship.rate ? ship.rate.service : null, rate_id: ship.rate ? ship.rate.id : null }, tax: money2(m, tax), gift_used: money2(m, giftUsed), eta, contexts, gateway: gw.id, gateway_name: gw.name, txn_ref: sim.ref, payment_status: sim.status, payment_redirect: awaitingPayment && sim.redirect ? sim.redirect : null, date: new Date().toISOString(), addr: `${name}, ${address}, ${city}`, pickup: pickedUp, items: cart.items.map(x => ({ id: x.product.id, qty: x.qty, price: x.unit })) } });
}







/* the data subject's own consent record — the customer reads and edits their own
   lawful-basis state; an admin may act on behalf of a subject by email */
/* a data subject reads and changes ONLY their own consent; acting on someone else's record
   (`subject=`) is a staff action — it was open to anyone */
function consentSubject(s, requested) {
  if (requested && requested !== ownerFor(s) && !(s.platform_admin || isAdmin(s))) return null;
  return requested || ownerFor(s);
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

/* ---------------- E18 · the operations universe ---------------- */
/* The gate is always the capability atom. Each handler answers 403 until the store
   composes the atom, and every value the engine used is a param it already read —
   no tax rate, threshold, yield or cost rate lives in this file. */
function opsOn(s, key) {
  const c = caps.cap(T(s), key);
  return c && Object.keys(c).length ? c : null;
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



/* ================= FX / CONVERSIONS ================= */
function platGet(key, dflt) { try { const r = get("SELECT value FROM platform_settings WHERE key=?", key); return r ? J(r.value, dflt) : dflt; } catch (e) { return dflt; } }
function platSet(key, val) { require("./settings.js").setPlatform(key, val); }
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
    require("./value-units.js").setRate(c.code, v);
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


/* ---------------- store: gateways / payments / billing / audit / monitor ---------------- */
function maskConfig(g) {
  const cfg = { ...(g.config || {}) };
  return cfg;
}

/* ================= SECURITY: scorecard · chain · keys (L6/L7) ================= */
const POLICY_KEYS = ["paymentReconcileMinutes", "shopperSweepMinutes", "cspImgHosts", "minPasswordLength", "requireLetterDigit", "blockCommon", "lockoutThreshold", "lockoutBaseSec", "lockoutCapSec", "staffMfaRequired", "registerPerHour", "authPerMin", "apiPerMin", "csrfEnabled", "hsts", "demoHints", "cspInlineStyles"];


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

/* a store's place facts, from the kernel (lib/stores.js): its jurisdiction, the country it lies
   in, and every place it serves — never a column of its row */
function storeFacts(tid) {
  const st = require("./stores.js");
  return { country: st.country(tid), jurisdiction: st.jurisdiction(tid), places: st.served(tid) };
}
/* Setup-wizard progress: one store, every step marked done or pending. Powers the
   "what's left" checklist after (or during) launch. */
/* which provisioning switch a setup step depends on (steps not named apply to every kind) */
const STEP_NEEDS = { payments: "payments", shipping: "shipping", catalogue: "storefront", features: "storefront" };
function setupStatus(row) {
  if (!row) return null;
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
  ].filter(x => !STEP_NEEDS[x.key] || (kd.provision || {})[STEP_NEEDS[x.key]]);
  return { t, prof, c, kd, payGw, shipGw, steps, done: steps.filter(x => x.done).length, total: steps.length, available: { shipping: ships, payments: registry.providersFor("payment", t.country).map(p => p.id) } };
}
/* what the consoles need to name a platform by its kind ("Operator console", "Company settings") */
function kindBrief(t) {
  const k = t && registry.kind(String(t.mode || ""));
  return k ? { key: k.key, name: k.name, noun: k.noun, nounPlural: k.nounPlural, storefront: k.provision.storefront } : null;
}
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
/* ---------- configuring a platform by its setup steps (lib/platform-setup.js) ---------- */
const SUX = () => require("./platform-setup.js");
function tenantPayload(body) {
  /* shared validation+normalization for create & update — jurisdiction, taxation, categories, owner, gateways, plan */
  const j = body.jurisdiction || {};
  /* a registration that answers the setup steps names its jurisdiction and what it sells there */
  const ans = body.answers || {};
  const country = registry.country(String(j.country || body.country || ans.official || sec.defaultCountry()).toUpperCase());
  const industries = (Array.isArray(body.industries) ? body.industries : (ans.offerings || [])).filter(k => registry.list("industries").some(i => i.key === k));
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
/* ---------- marketing / external integrations (specs are DATA: fill in the blanks) ---------- */
function marketingSpec(tenantId, id) {
  const rows = all("SELECT manifest FROM custom_providers WHERE kind='marketing' AND (scope='platform' OR (scope='tenant' AND tenant_id=?))", tenantId);
  for (const r of rows) { let m; try { m = J(r.manifest, null); } catch (e) { continue; } if (m && m.id === id && m.spec) return { spec: m.spec, fields: m.fields || [] }; }
  const def = get("SELECT spec, fields FROM provider_defs WHERE id=? AND kind='marketing'", id);
  if (def) return { spec: J(def.spec, null) || null, fields: J(def.fields, []) };
  return null;
}

/* ================= META MODEL ================= */
const meta = require("./meta.js");
const rules = require("./rules.js");
/* orders, payments, invoices and returns are state machines (lib/states.js): this file asks
   what a state means (settled, awaiting, cancellable, shippable…) and never names one */
const states = require("./states.js");
const stock = require("./stock.js");
const orders = require("./orders.js");
const returns = require("./returns.js");
const features = require("./features.js");
const letters = require("./letters.js");
const stIn = (machine, tag) => { const xs = states.tagged(machine, tag); return { sql: "(" + (xs.length ? xs.map(() => "?").join(",") : "NULL") + ")", args: xs }; };
const stIs = (machine, state, tag) => states.has(machine, state) && states.is(machine, state, tag);
/* an invoice moves to the state that means "paid", with the stamp that state declares */
function invoicePaid(inv) {
  const { patch } = states.apply("invoice", { tenantId: inv.tenant_id, from: inv.status, to: states.first("invoice", "success"), row: inv, force: true });
  require("./row-records.js").change("invoice", inv.id, () => run("UPDATE invoices SET " + Object.keys(patch).map(k => k + "=?").join(", ") + " WHERE id=?", ...Object.values(patch), inv.id));
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
/* the taxonomy levels (registry taxonomyLevels): the root a storefront browses from, and the
   levels a global product may be categorised by */
function taxLevels() { return rl("taxonomyLevels"); }
function taxRoot() { const l = taxLevels(); return (l.find(x => x.root) || l[0] || {}).key; }
/* a store's tree and attribute definitions are read models of the master: brought up to date when
   the master has moved */
const taxSeen = new Map();
function freshTaxonomy(tid) {
  const seq = (get("SELECT MAX(seq) AS s FROM k_events") || {}).s || 0;
  if (taxSeen.get(tid) === seq) return;
  require("./store-taxonomy.js").sync(tid);
  require("./store-attributes.js").sync(tid);
  taxSeen.set(tid, (get("SELECT MAX(seq) AS s FROM k_events") || {}).s || 0);
}
function nodeDescendants(tenantId, id) {
  const out = [Number(id)];
  const rows = all("SELECT id,parent_id FROM taxonomy WHERE tenant_id=?", tenantId);
  let grew = true;
  while (grew) { grew = false; for (const r of rows) if (out.includes(r.parent_id) && !out.includes(r.id)) { out.push(r.id); grew = true; } }
  return out;
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

function applyPromos(tenantId, items, coupon, opts) {
  opts = opts || {};
  const codesAllowed = sec.policy().provisioning.couponsAllowed;
  const amount = items.reduce((n, i) => n + i.product.p * i.qty, 0);
  const mapped = items.map(i => ({ id: i.product.id, dept: i.product.d, brand: i.product.b, node_id: i.product.node_id, price: i.product.p, qty: i.qty }));
  /* each offer is subject to the store's applicability rules (country, segment, channel, amount…) */
  const res = offers.evaluate({ filter: o => rules.permitsAt("offers.apply", String(o.id), rules.at("offers.apply", tenantId, { amount })), channel: require("./defaults.js").of("offerChannels"), tenantId, items: mapped, amount, coupon: codesAllowed ? coupon : "", owner: opts.owner || null, currency: opts.currency || null, allowGlobal: sec.policy().provisioning.globalOffersAllowed !== false });
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


/* ================= UNIVERSAL ENTITY ENGINE ================= */
const entity = require("./entity.js");
/* who may act on a type (or one of its fields), from the roles its definition grants per action —
   read, create, update, delete (create/update/delete fall back to `write`). A grant names roles:
   "platform" (any platform administrator), "admin" (any store staff member), or a store role key
   from the store's own role set (Store console → Team: owner, manager, support…), so a type can be
   opened to exactly the roles the operator chooses in Data Studio. Section access (requireSection)
   still applies on top. `mode` is an action, or the legacy true (write) / false (read). */
const permAction = m => m === true ? "write" : (m === false || m == null) ? "read" : String(m);
function permRoles(perm, action) { const p = perm || {}; return p[action] || (action !== "read" ? p.write : null) || []; }
function staffRoleOf(s) { if (s.api_key) return s.api_key.role_key; const u = s.user_id ? get("SELECT staff_role FROM users WHERE id=? AND tenant_id=?", s.user_id, T(s)) : null; return (u && u.staff_role) || "owner"; }
/* how a grant admits the session: "role" when it names the staff member's own role key (an explicit
   Data Studio grant — it decides on its own), "staff" when it admits all store staff (the store's
   Team sections still decide), "platform", or null */
const VIA = Object.freeze({ platform: 1, staff: 2, role: 3 });
function permVia(s, roles, platformOnly) {
  if (platformOnly) return roles.includes("platform") && !!s.platform_admin ? VIA.platform : null;
  if (s.platform_admin) return roles.includes("platform") ? VIA.platform : null;
  if (!isAdmin(s)) return null;
  if (roles.includes(staffRoleOf(s))) return VIA.role;
  return roles.includes("admin") ? VIA.staff : null;
}
const permGranted = (s, roles, platformOnly) => !!permVia(s, roles, platformOnly);
function entityPerm(s, def, mode) { return permGranted(s, permRoles(def.perm, permAction(mode)), def.platformOnly); }
/* true when the type's grant for this action names the staff member's role outright */
function entityGrantedByRole(s, def, mode) { return permVia(s, permRoles(def.perm, permAction(mode)), def.platformOnly) === VIA.role; }
/* a field with no grants of its own follows its type */
function fieldPerm(s, def, f, mode) { return !f.perm || permGranted(s, permRoles(f.perm, permAction(mode)), def.platformOnly); }


/* a configured app's dataset answers to the app's own grant; every other dataset to gdata */
const platformDataSection = key => (authz.configuredApps().some(a => a.key === key && !a.tenant_id) ? authz.APP_PREFIX + key : "gdata");
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
  csv: { label: "CSV (comma-separated values)", ext: "csv", importable: true, ct: "text/csv; charset=utf-8", render: (rows, cols) => csvOf(rows.map(r => { const o = {}; for (const c of cols) o[c] = r[c]; return o; })) },
  json: { label: "JSON (array of records)", ext: "json", importable: true, ct: "application/json; charset=utf-8", render: (rows, cols, title) => JSON.stringify({ entity: title, exported_at: new Date().toISOString(), rows }, null, 1) },
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
  "/api/admin/gateways", "/api/admin/settings", "/api/offers", "/api/admin/users",
  "/api/affiliate/affiliates", "/api/affiliate/reports", "/api/affiliate/payouts", "/api/affiliate/networks"
];
function fanoutAllowed(path) {
  const row = get("SELECT items FROM meta_lists WHERE name='platformFanout'");
  if (row) { try { const j = JSON.parse(row.items); if (Array.isArray(j)) return j.map(String).includes(path); } catch (e) { } }
  return FANOUT_DEFAULT.includes(path);
}
/* ---------- contracts / tenders / serialized (B2B + unit serialization) ---------- */
const newRef = pre => pre + "-" + Date.now().toString(36).toUpperCase() + crypto.randomBytes(2).toString("hex").toUpperCase();


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


/* ---------- environments + feature flags (unlimited named envs, all data) ---------- */
function resetRuntimeSvc() { _svc.q = null; _svc.s = null; }

/* ---------- the Universal Wallet (lib/wallet.js): the Customer Wallets module's product ---------- */
const Wal = () => require("./wallet.js");
/* the wallet routes answer only where the store has the module the checkout.wallet gate names */
function walletsOn(s, res) {
  const g = require("./gates.js");
  if (g.on(T(s), "checkout.wallet")) return true;
  bad(res, g.message("checkout.wallet"), 403); return false;
}
/* a mutating call's idempotency key: the Idempotency-Key header, else the body's */
const idemOf = (req, body) => String((req.headers && req.headers["idempotency-key"]) || (body && body.idempotency_key) || "").slice(0, 120) || null;





/* ---------- enterprise ops (DB cutover · SSO/SCIM · regions/CDN · observability · feeds/transfers/tax) ---------- */
function apiDbStatus(req, res, url, s) { if (!requirePlatform(s, res)) return; json(res, 200, enterprise.dbStatus()); }
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
    const upd = require("./row-records.js").change("payment", p.id, () => run("UPDATE payments SET status=?, provider_payment_id=COALESCE(?, provider_payment_id) WHERE id=? AND status IN " + aw.sql, e.status, e.paymentId || null, p.id, ...aw.args));
    if (!upd.changes) return { ok: true, unchanged: true };
    if (ord && stIs("order", ord.status, "awaiting_payment")) require("./order-records.js").change(ord.id, () => run("UPDATE orders SET status=? WHERE id=?", states.first("order", "accepted"), ord.id));
    audit(p.tenant_id, "system", null, "gateway", "payment.captured", "payment", p.id, { provider, ref: p.txn_ref, source });
    /* paid after the order was cancelled (the shopper finished on the provider's page): the money goes straight back */
    if (ord && stIs("order", ord.status, "void")) {
      const paid = get("SELECT * FROM payments WHERE id=?", p.id);
      require("./refunds.js").refund(p.tenant_id, paid, null, { reason: "paid after the order was cancelled", actor: "system" })
        .catch(x => notify(p.tenant_id, "Refund owed for " + ord.num, paid.amount + " " + (paid.currency || "") + " — " + x.message));
      return { ok: true, status: e.status, refunding: true };
    }
    if (ord) { emitEvent(p.tenant_id, "order.paid", { num: ord.num, total: ord.total, txn_ref: p.txn_ref, gateway: provider }, ord.num); notify(p.tenant_id, `Payment received for ${ord.num}`, `${ord.total} ${ord.currency || ""} via ${provider}`); }
    return { ok: true, status: e.status };
  }
  if (stIs("payment", e.status, "failure")) {
    const upd = require("./row-records.js").change("payment", p.id, () => run("UPDATE payments SET status=? WHERE id=? AND status IN " + aw.sql, e.status, p.id, ...aw.args));
    if (!upd.changes) return { ok: true, unchanged: true };
    /* an abandoned or failed hosted payment releases what checkout took: the order is
       cancelled, store credit spent on it goes back, offer redemptions are reversed */
    if (ord && stIs("order", ord.status, "awaiting_payment")) {
      /* its stock, what it spent from balances and its offers go back (lib/orders.js) */
      orders.paymentFailed(p.tenant_id, ord, "payment failed");
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







/* ---------- router ---------- */
/* ========== UCOS Ω∞ · constitutional registry (UPIP + UMQSOCR documents) ==========
   The Architecture documents are parsed, not transcribed: every endpoint below reads the
   canonical tables seeded by lib/ucos.js, so the platform never holds a second copy of the
   truth. Manifest/coverage are free reads (they power the console); mutations are admin-only. */
function ucosStore() { return ucos.store({ get, run, all }); }


/* 17AH.7 enforcement: while the constitution is unfreezable, the Tier-0 mutations it
   governs are refused with the gap summary. The operator resolves the gaps and re-runs
   the audit (GET /api/ucos/completeness) to lift the hold. */
function constitutionHeld(res) {
  if (!ucosComp.held()) return false;
  const st = ucosComp.freezeStatus();
  bad(res, "Constitution hold — " + (st && st.verdict || "unresolved freeze criteria") + " (" + (st && st.criticalCount || 0) + " critical gaps). Resolve them and re-run /api/ucos/completeness.", 503);
  return true;
}






/* ---------- TRACEABILITY: where is a corpus declaration implemented? ----------
   For any key this reports every runtime layer it resolves to — registry concept,
   foundation, universe, live entity, records, catalog projection, API routes and
   console views — or honestly reports that a layer is absent. The corpus→runtime
   matrix is the measurable answer to "how much of the constitution is built?" */
const ucosTrace = require("./ucos-trace.js");

/* ---------- PER-DOMAIN RECORD ENGINE ----------
   Each universe is a DOMAIN: its records move through the state machine the corpus
   declares (UCOS 5.1 states, 5.2 rules, UMQSOCR Art. 10 components), and every
   transition is rule-gated and append-audited (Article 6). No universe-specific
   code — the machine is derived per domain (Article 4.2). */
const ucosDomain = require("./ucos-domain.js");

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


/* a BNPL account, its EMIs and an insurance policy belong to one owner: only that owner
   (or store staff) may spend, pay or activate them — these took a bare sequential id. */
function finOwns(s, table, id) {
  if (s.platform_admin || isAdmin(s)) return true;
  const r = get("SELECT owner FROM " + table + " WHERE id=? AND tenant_id=?", Number(id), T(s));
  return !!(r && r.owner === ownerFor(s));
}



/* ---------- Shopper experience completions ---------- */
function notifyWrite(tenantId, owner, kind, title, body, link) {
  const kinds = registry.list("shopNotifKinds").map(x => x.key || x);
  run("INSERT INTO notifications(tenant_id,owner,kind,title,body,link,read,meta) VALUES(?,?,?,?,?,?,0,'{}')",
    tenantId, String(owner || ""), kinds.includes(kind) ? kind : "order_placed", String(title || ""), String(body || ""), String(link || ""));
}
function compareRow(tenantId, owner) {
  let row = get("SELECT * FROM compare_lists WHERE tenant_id=? AND owner=?", tenantId, owner);
  if (!row) { run("INSERT INTO compare_lists(tenant_id,owner,product_ids) VALUES(?,?, '[]')", tenantId, owner); row = get("SELECT * FROM compare_lists WHERE tenant_id=? AND owner=?", tenantId, owner); }
  return row;
}
/* ---------- Lists, alerts, pickup points, rich content, brand registry, sponsored results ----------
   Thin handlers over lib/lists.js, lib/alerts.js, lib/pickup.js, lib/richcontent.js,
   lib/brandreg.js and lib/marketplace.js: the engine decides and throws an error carrying its
   HTTP status; a handler checks who is asking and shows money in the store's currency. */
/* only an engine's own refusal (it carries a status) is told to the caller; anything else is
   rethrown to the dispatcher, which logs it and answers a 500 with a trace id */
const engineFail = (res, e) => { if (!e || !e.status) throw e; bad(res, e.message, e.status); };
function signedIn(s, res, what) { if (s.user_id) return true; bad(res, "Sign in to " + what, 401); return false; }
const shopperName = s => { const u = s.user_id ? get("SELECT name FROM users WHERE id=? AND tenant_id=?", s.user_id, T(s)) : null; return u ? u.name : ""; };
const byOf = s => actor(s)[2] || "";
/* a list's items carry store-view products, priced as the storefront prices them */
function listView(s, l) {
  const cm = commerceOf(s);
  if (l && Array.isArray(l.items)) l.items = l.items.map(it => ({ ...it, price_added: money2(cm, it.price_added), product: it.product ? storeView({ ...it.product, about: [] }, cm) : null }));
  return l;
}
function shopperCall(res, fn) { try { json(res, 200, fn()); } catch (e) { engineFail(res, e); } }

/* alerts: a target price is entered in the store's currency and kept in its base currency */
function alertView(s, w) {
  const cm = commerceOf(s);
  return { ...w, target_price: money2(cm, w.target_price), baseline_price: money2(cm, w.baseline_price), fired_price: money2(cm, w.fired_price),
    product: w.product ? { ...w.product, price: money2(cm, w.product.price) } : null };
}




/* ---------- Platform-type engines: options, bookings, offers, auctions, shopper selling,
   conversations, group buying, substitutions ----------
   Thin handlers: the engine decides; a handler checks who is asking, converts what a shopper
   types from the store's display currency to its base currency, and shows money back. */
const toBase = (s, n) => +(Number(n) / (Number(commerceOf(s).fx) || 1)).toFixed(2);
const shown = (s, n) => (n == null ? n : money2(commerceOf(s), n));
const staffActor = s => ({ owner: s.user_id ? ownerFor(s) : "", staff: !!(s.platform_admin || isAdmin(s)) });
const offerView = (s, o) => ({ ...o, amount: shown(s, o.amount), counter_amount: shown(s, o.counter_amount), product: o.product ? { ...o.product, price: shown(s, o.product.price) } : null,
  history: (o.history || []).map(h => h.amount != null ? { ...h, amount: shown(s, h.amount) } : h) });
const auctionView = (s, a) => a && ({ ...a, start_price: shown(s, a.start_price), current_price: shown(s, a.current_price), next_bid: shown(s, a.next_bid), buy_now_price: shown(s, a.buy_now_price),
  final_price: shown(s, a.final_price), product: a.product ? { ...a.product, price: shown(s, a.product.price) } : null });
const groupView = (s, g) => g && ({ ...g, group_price: shown(s, g.group_price), product: g.product ? { ...g.product, price: shown(s, g.product.price) } : null });
const optionView = (s, g) => ({ ...g, values: (g.values || []).map(v => ({ ...v, price_delta: shown(s, v.price_delta) })) });
const listingView = (s, l) => ({ ...l, price: shown(s, l.price) });
/* what a product page adds for the platform-type engines */
function productExtras(s, id) {
  const viewer = s.user_id ? ownerFor(s) : null;
  try { auctions.tick(T(s)); } catch (e) { } try { groupbuy.tick(T(s)); } catch (e) { }
  let sellerName = "";
  try { const o = listings.ownerOf(T(s), id); if (o) sellerName = require("./tell.js").nameOf(T(s), o) || "a shopper"; } catch (e) { }
  return { features: features.blocks({ tid: T(s), owner: ownerFor(s), product: get("SELECT * FROM products WHERE tenant_id=? AND id=?", T(s), id) || { id } }), options: options.forProduct(T(s), id).map(g => optionView(s, g)), booking: bookings.offer(T(s), id), auction: auctionView(s, auctions.forProduct(T(s), id, viewer)),
    group: groupView(s, groupbuy.forProduct(T(s), id, viewer)), sold_by_shopper: sellerName || null,
    trial: caps.on(T(s), "try_and_buy") && trials().allowed(T(s), get("SELECT * FROM products WHERE tenant_id=? AND id=?", T(s), id) || {}) };
}

/* deliverables (lib/deliverables.js): every kind its own feature, run from its own screen */
const deliv = () => require("./deliverables.js");
/* health records (lib/health-records.js): the shopper's own vault */
const records = () => require("./health-records.js");
/* try and buy (lib/trials.js) */
const trials = () => require("./trials.js");
/* live sessions (lib/media-sessions.js): either side joins, hands the other the handshake and ends */
const sessions = () => require("./media-sessions.js");
const sessionActor = s => ({ owner: s.user_id ? ownerFor(s) : null, staff: isAdmin(s) });
/* service fees (lib/fees.js) and tips (lib/tips.js), each its own feature */
const fees = () => require("./fees.js");
/* cases: what a shopper asks the store to decide (lib/cases.js) */
const cases = () => require("./cases.js");








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

const routes = [
  /* ============================================================
     UNIVERSAL COMMERCE ROUTES — one capability surface per
     domain; the heavy lifting is generic entity CRUD
     (/api/meta/entity/:key) and these handlers compose the engines.
     ============================================================ */
  /* Quick-commerce — promise, slots, pinning, dispatch */
  /* Fintech — UPI, QR, links, mandates, escrow, splits, KYC,
     payouts, BBPS, recharge, P2P, BNPL, loans, insurance, vouchers */
  /* Marketplace — onboarding, buy-box, FBA, health, claims */
  /* B2B trust & trade */
  /* Shopper experience completions */
  /* lists, alerts, pickup points (shopper) */
  /* pickup points, rich content, brand registry (store console) */
  /* platform-type engines (shopper) */
  /* platform-type engines (store console) */

    /* universal theming — presets, the resolution cascade, assignments, generative hue exploration */
  /* the configuration layer: every standard, quality, feature and functionality
     a platform or service exposes, composed per store from the console */
  /* universal dashboard & reporting engine (Architecture1 §394/§395) */
  /* the platform master: its tree and vocabularies, permissions on it, and the review of what platforms propose */
  /* UCOS Foundation Registry — Architecture3 Articles 2-8.
     Literal paths are registered before :key so they are not swallowed by the
     parameter route (the router takes the first segment-length match). */
  /* instantiated universes */
  /* catalog bridge — universe entities published into a tenant's storefront */
  /* activation — every declared universe becomes shopper-transactable */
  /* traceability — corpus declaration → runtime artifact map */
  /* per-domain record engine — each universe's corpus-declared state machine */
  /* the Global Platform's cross-tenant commerce reader: one generic surface for every
     entity-backed store capability (products, orders, SKUs, sellers, RFQs, compliance…),
     aggregated across stores with the same definitions the Store Console uses */
  /* cross-store fan-out: runs an existing read-only Store Console route once per store and
     merges — every composite capability gains a platform surface with no logic duplicated */
  /* E17 · mobility — the ride-hailing / dispatch surface. Each route is gated on its
     own atom, so a store with only ride_hailing on gets the rides surface and nothing
     else, and a store with none of them refuses the whole block. */
  /* E18 · operations — the ERP surface. Each route is gated on its own atom, so a
     store composing only workforce gets HRMS/payroll and nothing else. */
  /* compliance & privacy — named regulations as data, computed verdicts, consent ledger,
     data-subject-rights workflow */
  /* tenancy hierarchy — the tenant's own org structure (org → BU → brand → store → channel).
     Every node is data, the path is materialized, and the tree is the config cascade.
     Scoped to the session's tenant; the platform reads it via the generic cross-store reader */
  /* the composition engine — the platform composes a declared capability into its full
     application surface (data model · API · workflow · UI · dashboard · security) with no
     per-capability code. Platform-only: composing creates platform-wide machinery */
  /* platform registry authoring: every meta_lists vocabulary, auto-discovered.
     Segment counts differ, so :name/recommend and :name/:key never collide with :name */
  /* GOIP Ω∞ — capability router + read surfaces */
  /* configuring a platform by its setup steps: the steps and options, discovery's preview, the
     answers in force (each effective to the minute) and the owner's edit of requests */
  /* Affiliate Network */
  
  /* Sitemap (SEO) */
  
  /* Shipping & Tracking */
  
  /* Enhanced Helpdesk */
  
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
      const r = rules.run(ctxStore, () => fn(req, res, url, session, body, params[0], params[1], metrics, params[2]));
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








/* the category vocabulary for a global product: the master's trade taxonomy to the levels a
   catalogue is filed at (industries and their categories), read from the master, never typed */
function platformCategories() {
  const PM = require("./platform-master.js"), L = require("./expression.js").SEED.sourceLanguage, text = require("./kernel.js").text;
  const out = [];
  for (const d of PM.children(null)) for (const ind of PM.children(d.uid)) {
    out.push({ key: ind.key, name: text(ind.attributes.title, L), icon: ind.attributes.icon || "", level: ind.kind });
    for (const c of PM.children(ind.uid)) out.push({ key: c.key, name: text(ind.attributes.title, L) + " › " + text(c.attributes.title, L), icon: "", level: c.kind });
  }
  return out;
}
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
function globalRecord(body) {
  const { profile, rejected } = validProfile(body.profile);
  if (rejected.length) { const e = new Error("Unknown/invalid profile field(s): " + rejected.join(", ")); e.status = 400; throw e; }
  return { sku: body.sku, name: body.name, description: body.description || '', category: body.category || '', universe: validProductUniverse(body.universe),
    price: Number(body.price) || 0, tax_class: body.tax_class || '', attributes: body.attributes || {}, media: validMedia(body.media), profile, status: body.status || '' };
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
/* a store's access to a global product is a permission on the platform master, set at an
   access level (lib/master-permissions.js); these routes read and set it per store and product */
function storeAccessRows(filterTenant) {
  const gc = require("./gcatalog.js");
  return gc.globalListWithPermissions().flatMap(p => p.permissions).filter(r => filterTenant == null || r.tenant_id === Number(filterTenant))
    .map(r => ({ ...r, enabled: 1 }));
}

/* ========== the platform master: permissions, contributions, review ==========
   The global platform grants each platform permissions on the master and reviews everything a
   platform proposes (lib/master-permissions.js, lib/master-contributions.js). A store reads the
   master as it sees it and proposes through the same contribution path; it never writes the
   master directly. */
const PMX = () => require("./platform-master.js");
const MPX = () => require("./master-permissions.js");
const MCX = () => require("./master-contributions.js");
const by = s => byOf(s) || actor(s)[0];
const tryJson = (res, fn, status) => { try { json(res, status || 200, fn()); } catch (e) { bad(res, e.message, e.status || 400); } };
const storeHolderOf = s => MPX().storeHolder(T(s));


/* S8: body keys used to become SET clause text directly. Whitelist against the
   declared columns and scope the UPDATE to this tenant, the same way the entity
   engine whitelists its own dynamic builders. */
const AFFILIATE_COLS = ['network_id','name','email','status','affiliate_code','tracking_url','deep_link_template','commission_pct','commission_type','tier','last_activity','metadata'];

/* ========== Sitemap (SEO) APIs ========== */
/* the XML is public (search engines fetch it) but sits behind the same SEO Pro module as
   /api/seo/sitemap.xml — it used to bypass that gate. Config + generation are staff. */
const sitemapMod = require("./sitemap.js");
const shippingMod = require("./shipping.js");

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








/* the shared HTTP kit a domain's route file is given: the request guards, responses, store and
   actor resolution, persistence and the engines its handlers call. A domain's routes live in
   lib/routes/<domain>.js and are loaded from that folder — no list of domains here. */
const KIT = { platformDomain, letters, features, orders, returns, stock, canSettle, fieldPerm, entityGrantedByRole, AD_EVENT_KINDS, AFFILIATE_COLS, CFG, CHECKOUT_LOCKS, DB_PATH, DEMO_DEFAULT_PASSWORDS, DEPT_TO_INDUSTRY, EXPORT_FORMATS, J, MCX, MPX, PMX, POLICY_KEYS, RESET_TTL_MIN, SUX, T, USE_PG, Wal, _svc, _userRow, actor, adapters, ai, alertView, alerts, all, apiCheckoutOnce, appInfo, applyCountryAndTax, applyExportScope, applyGatewayEvent, applyPaymentStatus, applyRates, auctionView, auctions, audit, auditChainVerify, authz, bad, billing, bookings, branding, brandreg, buildSearch, by, byOf, capTenantScope, caps, cartPayload, cases, checkoutTotals, cleanShipFrom, commerceOf, compareRow, compliance, compose, connect, consentSubject, constitutionHeld, contractPriceFor, conversations, coverageReport, crypto, csvOf, customProviders, dashboards, dbpool, deliv, deployModeOr, emitEvent, enabledCarriers, enabledGateways, enabledNotifiers, engineFail, enterprise, entity, entityPerm, env, establishSession, events, experiments, exportCols, fanoutAllowed, fees, fin, finOwns, fintech, firstMatching, freshTaxonomy, fs, fullProductDoc, fxRate, gatewaySecrets, get, globalRecord, globalmod, goip, governance, groupView, groupbuy, handle, hashPasswordFor, helpdesk, hintsAllowed, httpGetJson, idemOf, invoicePaid, ipOf, isAdmin, isTls, json, kindBrief, lineterms, listView, listingView, listings, lists, logAction, logistics, mailer, marketingSpec, marketplace, masterTenant, mergeOwner, meta, migrate, mkt, mobOn, mobility, modeNeedsIndustries, mods, money2, negotiation, newPlatformAdmin, newRef, newUser, newUserAsync, notify, notifyWrite, offerView, offers, operations, opsOn, options, outboundOffline, ownerFor, ownsDashboard, parseImportPayload, passwordReusedAsync, paymentRegistry, permittedCarriers, permittedGateways, pickup, planFor, planning, platGet, platSet, platSetting, platformCategories, platformDataSection, platformEntityDef, platformSections, platformWriteTenant, policies, prbac, productExtras, profileFields, provisionGateways, publicLink, publicProduct, qcommerce, queueNow, rbac, reconcilePayment, records, recurring, registry, requireAdmin, requirePlatform, requirePlatformRoute, requirePlatformSection, requireSection, requireStaff, requireStore, resetRuntimeSvc, resolveProductType, richcontent, risk, rl, rotateSession, routes, rtconfig, ruleCtx, rules, run, sampleValueFor, search, sec, seedMeta, seedTaxonomy, seedTenantBrands, seedTenantCatalog, seedTenantDepartments, seedTenantHome, sessionActor, sessions, setTenantState, setUserPassword, setUserPasswordAsync, settings, settlePayment, setupStatus, sha256hex, shippingFor, shippingMod, shopperCall, shopperName, shown, signedIn, simulatedSettlementAllowed, sitemapMod, sortClause, stIn, stIs, states, storeAccessRows, storeFacts, storeHolderOf, storeNow, storeSections, storeView, substitutions, taxLevels, taxmod, tenancy, tenantPayload, themes, toBase, trade, trials, tryJson, ucos, ucosCat, ucosComp, ucosDomain, ucosFound, ucosMon, ucosStore, ucosTrace, ucosUniv, ugc, universeFieldsOf, validateAttrs, verifyPlatformAdminAsync, verifyUserAsync, walletsOn, writeBullets };
for (const f of require("fs").readdirSync(require("path").join(__dirname, "routes")).filter(f => f.endsWith(".js")).sort())
  routes.push(...require("./routes/" + f).routes(KIT));
/* which route answers is decided by specificity, never by which file declared it first: at the first
   segment where two patterns differ, a literal beats a :param ("/deliverables/item/:id" before
   "/deliverables/:kind/pool"). Patterns of different lengths never compete; ties keep declaration order. */
const routeRank = key => key.split(" ")[1].split("/").filter(Boolean).map(p => p.startsWith(":") ? "1" : "0").join("");
routes.splice(0, routes.length, ...routes.map((r, i) => [r, routeRank(r[0]), i]).sort((a, b) => (a[1] < b[1] ? -1 : a[1] > b[1] ? 1 : a[2] - b[2])).map(x => x[0]));
