/* UCOS Ω∞ · authz — THE ONE AUTHORIZATION ENGINE
   ---------------------------------------------------------------------------
   There used to be two engines with two vocabularies: lib/rbac.js for the store
   console (staff roles, per-tenant) and lib/prbac.js for the platform console
   (operator roles, global). Two engines meant two places a grant could be
   mis-scoped, two seeds to keep alive, and — the defect that made this file
   necessary — two grant surfaces that SHARE THIRTY SECTION KEYS. "orders",
   "dash", "settings", "audit" exist on BOTH surfaces and mean different things
   on each. A single merged surface would have collided silently: a store
   manager's "orders" grant would have opened the platform's global order view,
   or the reverse.

   So one engine, TWO NAMESPACED SURFACES. A grant is a scoped pair:

       store:orders        — a tenant-scoped capability (this store's orders)
       platform:gorders    — a platform capability (every store's orders)

   The scope is the security boundary, and it is now a string in the grant
   itself, not a function of which file the check happened to live in. One
   resolver reads one identity and answers one question for either surface.

   THE IDENTITY. An identity is whatever the session holds — a store staff
   member, a platform operator, or (once the consoles merge) one person who is
   both. Each authority contributes its own grants to one combined map:

       { "store:orders": "write", "platform:tenants": "read", ... }

   An authority never grants outside its own surface: a store role can only
   ever produce store:* grants, a platform role only platform:*. That is the
   invariant that makes it safe for one person to hold both — the merge stops
   at the grant map, so a store manager who is also an operator carries two
   scoped capabilities, never one blended one.

   BACKWARD COMPATIBILITY IS THE CONTRACT. lib/rbac.js and lib/prbac.js remain
   and re-export this engine with their original call shapes, so every existing
   call site, test and stored meta_lists row keeps resolving exactly as before.
   The stored role rows (staffRoles, platformRoles) are unchanged data; only
   the resolver that reads them is unified. Nothing is migrated, nothing is
   re-seeded, and an operator's edited role set is as durable as it was. */

"use strict";

let _db = null;
const db = () => _db || (_db = require("./db.js"));
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };

/* ---------- the entity → section map ----------
   Declared before the surfaces because the store surface must be CLOSED under
   it: a dataset reached through the generic entity router authorises against
   the console section that governs it, and a composed capability's cp_* records
   authorise against "compose". A section the router can reach but the surface
   omits is a dataset even an owner's '*' cannot open, so the surface is built
   from this map as well as from the nav. */
const KEY_SECTION = { product: "products", brand: "brands", sku: "skus", inventory: "skus", warehouse: "skus", serialized: "serialized", variant_group: "skus", compliance: "compliance", localization: "localizations", order: "orders", ret: "returns", rfq: "rfqs", seller: "sellers", settlement: "settlements", contract: "contracts", tender: "tenders", supplier: "suppliers", product_supplier: "suppliers", promotion: "offers", customer: "orders", review: "products", banner: "content", card: "content", department: "content", taxonomy: "taxonomy", attribute: "attributes", gateway: "payments", payment: "billing", tenant: "studio", plan: "studio", subscription: "studio", invoice: "billing", ai_usage: "ai", ai_task: "ai", offer: "offers", coupon: "offers", country: "studio", currency: "studio", tax_mode: "studio", provider_def: "payments", dark_store: "qcops", delivery_slot: "qcops", service_area: "qcops", store_inventory: "qcops", rider: "qcops", dispatch_run: "qcops", upi_handle: "finops", upi_collect: "finops", qr_code: "finops", payment_link: "finops", mandate: "finops", escrow_hold: "finops", split_payment: "finops", kyc_profile: "finops", bank_payout: "finops", biller: "finops", bill_payment: "finops", recharge: "finops", recharge_plan: "finops", bnpl_account: "finops", bnpl_emi: "finops", loan: "finops", insurance_policy: "finops", gift_voucher: "finops", seller_onboarding: "mktops", seller_offer: "mktops", fba_inbound: "mktops", seller_performance: "mktops", buyer_claim: "mktops", smart_fulfilment: "mktops", sponsored_creative: "mktops", trade_assurance: "tradeops", gold_supplier: "tradeops", company_verification: "tradeops", export_document: "tradeops", letter_of_credit: "tradeops", rfq_quote: "tradeops", tender_bid: "tradeops", price_list: "tradeops", price_list_item: "tradeops", gift_registry: "tradeops", notification: "orders", compare_list: "products", invoice_document: "billing", consent: "privacy", privacy_request: "privacy" };
/* ---------- configured apps: one grantable section each ----------
   Anything configured after the build — a capability composed into an application
   (cp_*), a custom entity defined in Data Studio — is a row in entity_defs, and each
   one becomes its own section, "app_<key>". It is a real grant like any nav leaf:
   an owner's '*' covers it the moment it exists, and every other role is refused
   until someone grants it in the console's Roles screen. So a new ERP, app or
   solution is never reachable through a catch-all section another role already holds.
   A store-scoped definition belongs to that store's surface only. */
const APP_PREFIX = "app_";
let _apps = { fp: null, list: [] };
function configuredApps() {
  /* configured apps live in the database: a process that never opened it (a tool or a
     test reading the static surfaces) has none, and must not open — and seed — one here */
  try { if (!require.cache[require.resolve("./db.js")]) return []; } catch (e) { return []; }
  try {
    /* the uv_* rows are the built universe registry (thousands, seeded every boot) —
       part of the build, never a configured app, and never scanned here */
    const fp = db().get("SELECT COUNT(*) n, COALESCE(MAX(rowid),0) m, COALESCE(SUM(length(def)),0) l FROM entity_defs WHERE substr(key,1,3) <> 'uv_'");
    const key = fp.n + ":" + fp.m + ":" + fp.l;
    if (_apps.fp === key) return _apps.list;
    const list = [];
    let builtIn = {};
    try { builtIn = require("./entity.js").ENTITY_DEFS || {}; } catch (e) { }
    for (const r of db().all("SELECT key, scope, tenant_id, def FROM entity_defs WHERE substr(key,1,3) <> 'uv_' ORDER BY key")) {
      /* a built-in entity (or a stored override of one) keeps its own section */
      if (!r.key || KEY_SECTION[r.key] || builtIn[r.key]) continue;
      const d = J(r.def, {});
      list.push({ key: r.key, section: APP_PREFIX + r.key, label: String(d.label || d.name || r.key), icon: String(d.icon || (d.composed ? "🧩" : "🧱")),
        composed: !!d.composed || String(r.key).startsWith("cp_"), tenant_id: r.scope === "platform" ? 0 : (Number(r.tenant_id) || 0) });
    }
    _apps = { fp: key, list };
    return list;
  } catch (e) { return []; }
}
/* the apps one store sees: the platform's own plus that store's custom definitions */
function appsFor(tenantId) {
  const t = Number(tenantId) || 0;
  return configuredApps().filter(a => !a.tenant_id || a.tenant_id === t);
}
function isAppSection(section) { return typeof section === "string" && section.startsWith(APP_PREFIX); }
function appForSection(section) { return isAppSection(section) ? configuredApps().find(a => a.section === section) || null : null; }

function sectionForEntity(key) {
  if (typeof key === "string" && configuredApps().some(a => a.key === key)) return APP_PREFIX + key;
  if (typeof key === "string" && key.startsWith("cp_")) return "compose";
  return KEY_SECTION[key] || "studio";
}

/* ---------- the two surfaces ----------
   Each is the nav leaf set of the console it governs, read from the compiled
   canonical registry so a grant and the button it lights can never drift. The
   surfaces are disjoint by construction: where they share a bare key ("orders")
   the scope prefix separates them. Fail-closed — an unreadable registry yields
   an empty surface and denies rather than granting against a stale copy.

   The STORE surface is not the raw nav leaves: the console redirects several
   leaves to one shared grant section through its NAVSEC map (promotions + goip
   → offers, structure → tenancy, sso → settings), and the surface must be
   closed under the entity router's section map too (a dataset reached through
   Data Studio authorises against a section no nav leaf names, so that section
   has to be grantable or even an owner's '*' cannot reach it). The platform
   console has no such indirection — its surface is its leaves exactly. */
const BASE_SURFACES = (() => {
  try {
    const c = require("./canonical.js").consoleSec();
    const navSec = c.adminNavSec || {};
    const store = new Set();
    for (const leaf of c.admin) store.add(navSec[leaf] || leaf);
    for (const s of Object.values(KEY_SECTION)) store.add(s);
    store.add("compose");   /* the cp_* prefix rule in sectionForEntity */
    return { store: [...store].sort(), platform: c.platform };
  } catch (e) {
    console.error("authz: canonical nav unavailable — both grant surfaces are empty: " + e.message);
    return { store: [], platform: [] };
  }
})();
/* the live surfaces: the built nav's sections plus every configured app's section, read
   at call time so an app composed a second ago is grantable now */
const SURFACES = {
  get store() { return BASE_SURFACES.store.concat(configuredApps().map(a => a.section)); },
  get platform() { return BASE_SURFACES.platform.concat(configuredApps().map(a => a.section)); }
};
const SCOPE_OF = { store: "store", platform: "platform" };
const isScope = s => s === "store" || s === "platform";

/* ---------- the tenant is what it is: section fitness ----------
    A store section is not universal: sellers, RFQs and trade ops belong to a
    marketplace, not a single-brand D2C; serial tracking belongs to electronics and
    jewellery, not to services. The fitness of each section is declared next to the
    store nav (NAVFIT) and harvested into the compiled registry, so what a console
    offers a tenant is data about the tenant rather than a hardcoded menu. An
    unparseable or missing map fails OPEN — fitness narrows the surface, it is never
    the reason a section exists, so losing it must not widen or shrink anything. */
const NAVFIT = (() => {
  try { return require("./canonical.js").consoleSec().adminNavFit || {}; }
  catch (e) { return {}; }
})();
function tenantFit(tenantId) {
  if (tenantId == null) return null;
  try {
    const r = db().get("SELECT mode, industries FROM tenants WHERE id=?", Number(tenantId));
    if (!r) return null;
    return { mode: String(r.mode || ""), industries: J(r.industries, []) };
  } catch (e) { return null; }
}
function sectionFits(section, fit) {
  const f = NAVFIT[section];
  if (!fit || !f) return true;
  if (Array.isArray(f.modes) && fit.mode && !f.modes.includes(fit.mode)) return false;
  const inds = fit.industries || [];
  if (!inds.length) return true;                 /* a tenant with no industries is universal — every vertical */
  if (Array.isArray(f.industries) && !f.industries.some(k => inds.includes(k))) return false;
  if (Array.isArray(f.notIndustries) && f.notIndustries.some(k => inds.includes(k))) return false;
  return true;
}

/* ---------- the console surface is a shadow of the composition ----------
   A store console section is granted by the individual capability that governs it —
   never by a bundle someone buys. Each ATOM in the capability catalog declares the
   section(s) it lights (capabilities.SECTIONS), and the tenant's live composition
   decides which are on: buy_box lights Marketplace & Marketplace Ops, rfq_bidding lights
   RFQs, instant_delivery lights Quick-commerce Ops. Buying one capability turns on its
   engine AND its nav leaf; nothing is ever granted as a package. A section no atom names
   is a vertical fact about the tenant (NAVFIT above) — serial tracking belongs to
   jewellery, replenishment to physical stock; no engine owns those, so the tenant's own
   profile governs them instead. */
function capabilitySections() {
  const out = new Map();                        /* section -> the atoms that light it */
  try {
    for (const c of require("./capabilities.js").catalog())
      for (const s of (c.sections || [])) {
        if (!out.has(s)) out.set(s, []);
        out.get(s).push(c.key);
      }
  } catch (e) { /* an unreadable catalog answers "no atom owns a section" — a cold boot */ }
  return out;
}
/* the atoms this tenant switched on AND the platform still allows. Both halves are
   load-bearing: a capability disabled platform-wide must not light a leaf even for a
   tenant that still holds it (the gate never widens). One read of each registry. */
function tenantAtoms(tenantId) {
  const out = new Set();
  try {
    const platformOn = new Set(require("./capabilities.js").catalog().filter(c => c.enabled).map(c => c.key));
    for (const r of db().all("SELECT capability FROM capability_values WHERE tenant_id=? AND enabled=1", Number(tenantId) || 0))
      if (platformOn.has(r.capability)) out.add(r.capability);
  } catch (e) { }
  return out;
}
/* the one question the grant filter asks of a section: is it granted to this tenant?
   An atom-owned section answers to the composition (any of its atoms on); every other
   section answers to the tenant's own profile through NAVFIT. The two sources never
   overlap: an atom-owned section is vertical-free, and a NAVFIT section names no atom. */
function sectionGranted(section, fit, tenantId, secCaps, atoms) {
  const owners = (secCaps || capabilitySections()).get(section);
  /* tenantAtoms answers a Set (and a test or a future caller may hand an array) — spread
     before .some, or every atom-owned section throws instead of answering */
  if (owners) return [...(atoms || tenantAtoms(tenantId))].some(k => owners.indexOf(k) >= 0);
  return sectionFits(section, fit);
}
/* a section key carries its scope when namespaced ("platform:tenants"), and is
   unscoped when it arrives from a legacy caller or a stored role row — the
   caller's surface supplies the scope then. */
function splitKey(key) {
  const k = String(key || "");
  const i = k.indexOf(":");
  if (i < 0) return { scope: null, section: k };
  const s = k.slice(0, i);
  return isScope(s) ? { scope: s, section: k.slice(i + 1) } : { scope: null, section: k };
}
const namespaced = (scope, section) => SCOPE_OF[scope] + ":" + String(section || "");

/* ---------- the shipped role defaults ----------
   These are the in-code defaults lib/rbac.js and lib/prbac.js seeded; the rows
   in meta_lists are the truth, these are the floor a cold boot fills in. Kept
   here so one engine holds the whole vocabulary, with the per-tenant and global
   storage shapes the two engines already used. */
const STORE_ROLES = [
  { key: "owner", name: "Owner", desc: "Full control", sections: { "*": "write" } },
  { key: "manager", name: "Store Manager", desc: "Everything except team + platform settings", sections: { "*": "write", team: false, settings: "read", studio: false } },
  { key: "catalog", name: "Catalog", desc: "Products, SKUs, inventory, content, taxonomy", sections: { dash: "read", products: "write", brands: "write", skus: "write", serialized: "write", compliance: "write", localizations: "write", content: "write", taxonomy: "write", attributes: "write", analytics: "read", monitor: "read", qcops: "write" } },
  { key: "orders", name: "Order Desk", desc: "Orders, returns, RFQs", sections: { dash: "read", orders: "write", returns: "write", rfqs: "write", compliance: "read", analytics: "read", qcops: "write", tradeops: "read" } },
  { key: "marketing", name: "Growth", desc: "Offers, coupons, promotions, content, AI", sections: { dash: "read", offers: "write", content: "write", ai: "write", webhooks: "write", analytics: "read", monitor: "read", affiliate: "write" } },
  { key: "finance", name: "Finance", desc: "Billing, payments, settlements, contracts, tenders", sections: { dash: "read", billing: "write", payments: "write", settlements: "write", contracts: "write", tenders: "write", suppliers: "read", analytics: "write", audit: "read", finops: "write", tradeops: "write" } },
  { key: "support", name: "Support", desc: "Read-only across the store + act on returns + privacy requests", sections: { dash: "read", orders: "read", returns: "write", products: "read", settings: "read", analytics: "read", privacy: "write" } }
];
const PLATFORM_ROLES = [
  { key: "owner", name: "Platform Owner", desc: "Full control of the platform", sections: { "*": "write" } },
  { key: "support", name: "Support", desc: "Sell and operate stores — no platform security or billing", sections: {
      dash: "write", tenants: "write", geo: "read", providers: "read", plans: "read", subs: "read",
      modules: "read", gorders: "write", gcatalog: "read", gb2b: "read", gmarket: "read",
      gfinance: "read", gsupport: "write", gcontent: "read", ganalytics: "read", gops: "write",
      gdata: "read", gteam: "read", grisk: "read", trace: "read", monitor: "read", brands: "read",
      taxonomy: "read", gproducts: "read"
    } },
  { key: "finance", name: "Finance", desc: "Plans, subscriptions, invoices and payments oversight", sections: {
      dash: "read", plans: "write", subs: "write", invoices: "write", billing: "write", gfinance: "write",
      tenants: "read", geo: "read", audit: "read", ganalytics: "read", monitor: "read"
    } },
  { key: "catalog", name: "Catalog", desc: "Global catalog, taxonomy, brands and product oversight", sections: {
      dash: "read", gproducts: "write", gcatalog: "write", taxonomy: "write", brands: "write",
      gb2b: "read", gmarket: "read", gcontent: "read", ganalytics: "read", tenants: "read"
    } },
  { key: "auditor", name: "Auditor", desc: "Read-only everywhere; can verify the audit chain", sections: {
      dash: "read", tenants: "read", geo: "read", providers: "read", plans: "read", subs: "read",
      invoices: "read", billing: "read", modules: "read", offers: "read", gorders: "read",
      gcatalog: "read", gb2b: "read", gmarket: "read", gfinance: "read", gsupport: "read",
      gcontent: "read", ganalytics: "read", gops: "read", gdata: "read", audit: "write",
      security: "read", runtime: "read", monitor: "read", policies: "read", trace: "write",
      gteam: "read", grisk: "read", padmins: "read"
    } }
];
const STAMP = { store: "rb_v6", platform: "pb_v1" };
const ROW = { store: tenantId => (tenantId ? "staffRoles:t" + Number(tenantId) : "staffRoles"), platform: () => "platformRoles" };
const KEY_RE = /^[a-z][a-z0-9_-]{1,30}$/;

/* ---------- storage: the row a scope's roles live in ----------
   Store roles are PER-TENANT (a store may fork its own set; the shared default
   is the floor), platform roles are GLOBAL. Same table, same edited=1
   convention, different row naming — unchanged from the two engines this
   replaces. */
function seedScope(scope) {
  const row = db().get("SELECT items,edited FROM meta_lists WHERE name=?", ROW[scope](0)) || {};
  const edited = row.edited || 0;
  const def = scope === "store" ? STORE_ROLES : PLATFORM_ROLES;
  if (!row.items || (!edited && JSON.stringify(J(row.items, def)) !== JSON.stringify(def)))
    db().run("INSERT INTO meta_lists(name,label,items,edited) VALUES(?,?,?,0) ON CONFLICT(name) DO UPDATE SET items=excluded.items, edited=excluded.edited",
      ROW[scope](0), ROW[scope](0), JSON.stringify(def));
}
function seed() { seedScope("store"); seedScope("platform"); }
function roles(scope, tenantId) {
  const name = ROW[scope](scope === "store" ? (tenantId || 0) : 0);
  const row = db().get("SELECT items FROM meta_lists WHERE name=?", name) || {};
  const def = scope === "store" ? STORE_ROLES : PLATFORM_ROLES;
  if (row.items) return J(row.items, def);
  /* only the store's shared default falls back to the in-code roles; a tenant
     row that has gone missing resolves to the current default, never nothing */
  return (scope === "store" && tenantId) ? roles("store", 0) : def;
}
function role(scope, tenantId, key) {
  const t = key === undefined ? null : tenantId;
  return roles(scope, t).find(r => r.key === key) || null;
}
function saveRoles(scope, tenantId, list) {
  const name = ROW[scope](scope === "store" ? (tenantId || 0) : 0);
  const label = scope === "store" ? (tenantId ? "staffRoles · store " + Number(tenantId) : "staffRoles") : "platformRoles";
  db().run("INSERT INTO meta_lists(name,label,items,edited) VALUES(?,?,?,1)"
    + " ON CONFLICT(name) DO UPDATE SET items=excluded.items, edited=1", name, label, JSON.stringify(list));
}
function validateRole(scope, role) {
  const errs = [];
  const key = String((role || {}).key || "").trim();
  if (!KEY_RE.test(key)) errs.push("key must be 2-31 chars, start with a letter, and use only a-z, 0-9, _ or -");
  const name = String((role || {}).name || "").trim();
  if (!name) errs.push("a role name is required");
  const secs = (role || {}).sections && typeof (role || {}).sections === "object" ? (role || {}).sections : {};
  for (const [k, v] of Object.entries(secs)) {
    if (k !== "*" && !SURFACES[scope].includes(k)) {
      /* an app deleted since the role was granted it: forget the grant, don't block the save */
      if (isAppSection(k)) { delete secs[k]; continue; }
      errs.push("unknown section: " + k);
    }
    if (!["write", "read", false].includes(v)) errs.push("grant for '" + k + "' must be write, read or off");
  }
  return { errs, key, name, secs };
}
function upsertRole(scope, tenantId, role) {
  const v = validateRole(scope, role);
  if (v.errs.length) return { ok: false, fails: v.errs };
  const list = roles(scope, tenantId);
  const rec = { key: v.key, name: v.name, desc: String((role || {}).desc || "").slice(0, 200), sections: v.secs };
  const i = list.findIndex(r => r.key === v.key);
  if (i < 0) list.push(rec); else list[i] = rec;
  saveRoles(scope, tenantId, list);
  return { ok: true, role: rec };
}
function deleteRole(scope, tenantId, key) {
  const k = String(key || "");
  if (k === "owner") return { ok: false, fails: ["the owner role cannot be deleted — it is the default full-access role"] };
  if (!role(scope, tenantId, k)) return { ok: false, fails: ["no such role: " + k] };
  /* a role still held blocks the delete: store roles by this store's staff,
     platform roles by any operator */
  const held = scope === "store"
    ? (tenantId ? db().all("SELECT id FROM users WHERE staff_role=? AND tenant_id=?", k, Number(tenantId)) : db().all("SELECT id FROM users WHERE staff_role=?", k))
    : db().all("SELECT id FROM platform_admins WHERE role=?", k);
  if (held.length) return { ok: false, fails: ["reassign the " + held.length + (scope === "store" ? " staff member(s)" : " operator(s)") + " holding this role first"] };
  saveRoles(scope, tenantId, roles(scope, tenantId).filter(r => r.key !== k));
  return { ok: true };
}
function hasOwnSet(tenantId) { return !!db().get("SELECT 1 ok FROM meta_lists WHERE name=?", ROW.store(Number(tenantId) || 0)); }
function resetToDefault(tenantId) {
  if (!tenantId) return { ok: false, fails: ["the shared default set cannot be reset"] };
  db().run("DELETE FROM meta_lists WHERE name=?", ROW.store(Number(tenantId)));
  return { ok: true };
}

/* ---------- expansion ----------
   '*' expands to the surface OF THE SCOPE IT IS WRITTEN IN — a store owner's
   '*' grants every store:* section and never a platform one. This is the line
   that keeps the two surfaces from blending: the wildcard is scoped, not
   global, so merging the engines cannot merge the capabilities. */
function expandScope(scope, sections) {
  const out = {};
  if (sections["*"]) {
    for (const s of SURFACES[scope]) out[s] = sections["*"];
    if (sections["*"] === "write") Object.keys(out).forEach(k => out[k] = "write");
  }
  for (const s of Object.keys(sections)) if (s !== "*") out[s] = sections[s];
  return out;
}
/* legacy expand() had one surface; the facades call this with their scope */
function expand(sections, scope) { return expandScope(scope || "store", sections || {}); }

/* ---------- the resolvers: one identity → one combined grant map ----------
   An authority is what the session proved: a store staff row ({role:'admin',
   staff_role, perms, tenant_id}) or a platform operator row ({role, perms}).
   Each resolves against ITS OWN scope only, and the results are namespaced on
   the way out, so a caller asking for "store:orders" and one asking for
   "platform:gorders" are reading two different keys of one map. */
/* a configured app is granted explicitly: the owner's '*' reaches it, but any other
   role's wildcard ("everything except…") does not — that role gets an app only when
   someone names it in the console's Roles screen */
function onlyOwnerInherits(sec, r, roleKey) {
  if (roleKey === "owner") return sec;
  const named = (r && r.sections) || {};
  for (const k of Object.keys(sec)) if (isAppSection(k) && !(k in named)) delete sec[k];
  return sec;
}
function storeGrants(user, tenantId) {
  if (!user || user.role !== "admin") return {};
  const sr = user.staff_role || "owner";
  const tid = tenantId != null ? tenantId : (user.tenant_id != null ? user.tenant_id : null);
  const r = role("store", tid, sr);
  const sec = onlyOwnerInherits(r ? expandScope("store", r.sections) : expandScope("store", { "*": "write" }), r, sr);
  const override = J(user.perms, {});
  for (const k of Object.keys(override)) sec[k] = override[k];   /* per-user add/remove */
  /* the intersection with what this tenant IS and HOLDS: a role may name any section, but
     the tenant's composition (the atoms it switched on) and its own profile decide whether
     it is granted at all. An atom-owned section is lit by its capability; every other
     section is governed by the tenant's mode and industries. Dropping an unlit or unfit
     section here hides it in both consoles (their navs key off the allowed list) and
     refuses it at the API — for an owner exactly as for staff. */
  const fit = tenantFit(tid);
  const secCaps = capabilitySections();
  const atoms = tenantAtoms(tid);
  const out = {};
  const mine = new Set(appsFor(tid).map(a => a.section));
  for (const k of Object.keys(sec)) {
    if (isAppSection(k)) { if (mine.has(k)) out[namespaced("store", k)] = sec[k]; continue; }
    if (sectionGranted(k, fit, tid, secCaps, atoms)) out[namespaced("store", k)] = sec[k];
  }
  return out;
}
function platformGrants(admin) {
  if (!admin) return {};
  const r = role("platform", 0, admin.role || "owner");
  const sec = onlyOwnerInherits(r ? expandScope("platform", r.sections) : expandScope("platform", { "*": "write" }), r, admin.role || "owner");
  const override = J(admin.perms, {});
  for (const k of Object.keys(override)) sec[k] = override[k];
  const out = {};
  const platformApps = new Set(configuredApps().filter(a => !a.tenant_id).map(a => a.section));
  for (const k of Object.keys(sec)) {
    if (isAppSection(k) && !platformApps.has(k)) continue;
    out[namespaced("platform", k)] = sec[k];
  }
  return out;
}
/* an identity holds whichever authorities the session proved. The unified shape
   is { store?: userRow, platform?: adminRow, tenantId? }; the two legacy shapes
   pass a bare row — a store user (carries staff_role / role:'admin' / tenant_id)
   or a platform operator (a role with no tenant). Either is recognized, and an
   authority never grants outside its own surface.
   An EMPTY identity has no authorities and therefore no grants — it is not a
   platform owner. (platformGrants(null) still yields owner for the prbac
   facade's own callers, where null means "the seeded owner, role unset"; the
   unified resolver must not inherit that default, or every store customer would
   carry the whole platform surface.) */
function isStoreRow(i) { return !!(i && (i.staff_role !== undefined || i.tenant_id !== undefined || i.role === "admin")); }
function isPlatformRow(i) { return !!(i && i.role !== undefined && !isStoreRow(i)); }
function grant(ident) {
  const i = ident || {};
  if (i.store || i.platform)
    return { ...storeGrants(i.store, i.tenantId), ...platformGrants(i.platform) };
  if (isStoreRow(i)) return storeGrants(i, i.tenant_id);
  if (isPlatformRow(i)) return platformGrants(i);
  return {};
}
/* the single question. Scope may come namespaced in the key ("platform:tenants")
   or explicitly (canScope(ident, "platform", "tenants")); either resolves the
   same grant. A bare key with no explicit scope resolves against the surface
   the caller names, so a legacy ask can never cross scopes by accident. */
function can(ident, key, section, mode) {
  const g = grant(ident);
  const sp = splitKey(key);
  const full = sp.scope ? namespaced(sp.scope, sp.section) : namespaced(section || "store", key);
  const have = g[full];
  if (!have || have === false) return false;
  return mode === "write" ? have === "write" : true;
}
/* explicit scope form — the shape the merged console and the unified guards use */
function canScope(ident, scope, section, mode) {
  const g = grant(ident);
  const have = g[namespaced(scope, section)];
  if (!have || have === false) return false;
  return mode === "write" ? have === "write" : true;
}
function allowedSections(ident, scope) {
  const g = grant(ident);
  const pre = scope ? namespaced(scope, "") : "";
  return Object.keys(g).filter(k => g[k] && (!pre || k.startsWith(pre))).map(k => pre ? k.slice(pre.length) : k);
}
/* does this identity hold ANY grant in a scope — the platform console's entry gate */
function hasScope(ident, scope) { return Object.keys(grant(ident)).some(k => k.startsWith(namespaced(scope, ""))); }

/* ---------- the platform route → section map ----------
   A platform route prefix resolves to the platform section that governs it, so
   generic endpoints authorize against the same grants the nav advertises. */
const ROUTE_SECTION = {
  tenants: "tenants", "tenants/setup": "tenants",
  geo: "geo", "global/country": "geo", "global/currency": "geo", fx: "geo",
  providers: "providers", "global/provider": "providers", "custom-providers": "providers",
  plans: "plans", "global/plan": "plans", subs: "subs", subscriptions: "subs",
  invoices: "invoices", billing: "billing", usage: "billing",
  modules: "modules",
  goip: "goip",
  admins: "padmins",
  audit: "audit", chain: "audit",
  security: "security", keys: "security",
  runtime: "runtime", db: "runtime", environments: "runtime", regions: "runtime", flags: "runtime",
  identity: "identity", "identity-templates": "identity",
  monitor: "monitor", metrics: "monitor",
  policies: "policies",
  themes: "themes",
  dashboards: "dash", reports: "dash",
  roles: "roles", "roles/staff": "roles",
  users: "users",
  fanout: "gops", data: "gdata",
  gproducts: "gproducts", "global-products": "gproducts",
  revenue: "ganalytics",
  /* every platform write route is classified (route audit 2026-10): an unmapped write used to
     fall back to "dash", which the support role holds, so it could rewrite the security
     policy, import environments, change any store's plan or edit the global schema */
  capabilities: "capabilities", "purge-expired": "security", config: "security",
  "meta/entity-def": "definitions", "entity-types": "definitions", "tenant-entities": "definitions",
  "tenant-fields": "definitions", attributes: "definitions", "entity-attributes": "definitions",
  ucii: "ucii", ucos: "ucos", "store-product-config": "gproducts",
  "global/tenant": "tenants",
  compose: "compose", branding: "branding", "branding-permissions": "branding",
  "admin/identity-provider-types": "identity",
  queue: "runtime", "environments-import": "runtime", "environments-export": "runtime",
  shipping: "providers", fanout: "gops"
};
/* the finer splits a two-segment prefix can't express */
const ROUTE_SECTION_EXACT = {
  "global/tenant/country": "geo", "global/tenant/currency": "geo",
  "global/tenant/provider": "providers", "global/tenant/plan": "subs"
};
/* an unmapped route reads as the dashboard, but WRITES fail closed to "settings" — a section
   only the owner holds — so a new write route is never silently open to restricted roles */
function sectionForRoute(path, mode) {
  const p = String(path || "").replace(/^\/?api\/(platform\/)?/, "").replace(/[?].*$/, "");
  const dm = /^data\/([^/]+)/.exec(p);
  if (dm) { let k = dm[1]; try { k = decodeURIComponent(k); } catch (e) { } if (configuredApps().some(a => a.key === k && !a.tenant_id)) return APP_PREFIX + k; }
  const three = p.split("/").slice(0, 3).join("/");
  if (ROUTE_SECTION_EXACT[three]) return ROUTE_SECTION_EXACT[three];
  const two = p.split("/").slice(0, 2).join("/");
  if (ROUTE_SECTION[two]) return ROUTE_SECTION[two];
  const seg = p.split("/")[0];
  if (ROUTE_SECTION[seg]) return ROUTE_SECTION[seg];
  return mode === "write" ? "settings" : "dash";
}

module.exports = {
  SURFACES, STAMP, SCOPE_OF,
  seed, seedScope, roles, role, saveRoles, validateRole, upsertRole, deleteRole,
  hasOwnSet, resetToDefault,
  expand, expandScope,
  storeGrants, platformGrants, grant,
  can, canScope, allowedSections, hasScope,
  sectionForEntity, sectionForRoute, KEY_SECTION, ROUTE_SECTION,
  configuredApps, appsFor, isAppSection, appForSection, APP_PREFIX,
  namespaced, splitKey, isScope, J,
  sectionFits, tenantFit,
  capabilitySections, tenantAtoms, sectionGranted,
  STORE_ROLES, PLATFORM_ROLES
};
