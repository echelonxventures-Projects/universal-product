/* LUXORA Platform — RBAC: staff roles + per-section permissions (all DATA, not code).
   The store has two enforced scopes today (customer, store admin). A store admin can be an OWNER
   (everything) or a STAFF member whose access is a named ROLE from `staffRoles` (meta_lists) —
   each role grants a subset of console sections as read/write — optionally overridden per user.
   Everything is editable in the console (data); adding a role or re-scoping one needs no code.

   Sections mirror the store-console nav keys. A '*' grant means all sections.
   Backward-safe: role='admin' with staff_role unset or 'owner' => full access (unchanged). */
"use strict";

let _db = null; const db = () => _db || (_db = require("./db.js"));
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };

const SECTIONS = ["dash", "products", "brands", "skus", "orders", "returns", "rfqs", "sellers", "settlements", "contracts", "tenders", "suppliers", "serialized", "compliance", "privacy", "tenancy", "compose", "localizations", "offers", "content", "taxonomy", "attributes", "payments", "modules", "settings", "billing", "analytics", "audit", "monitor", "studio", "ai", "webhooks", "trash", "team", "qcops", "finops", "mktops", "tradeops", "affiliate", "sitemap", "shipping"];

const ROLES = [
  { key: "owner", name: "Owner", desc: "Full control", sections: { "*": "write" } },
  { key: "manager", name: "Store Manager", desc: "Everything except team + platform settings", sections: { "*": "write", team: false, settings: "read", studio: false } },
  { key: "catalog", name: "Catalog", desc: "Products, SKUs, inventory, content, taxonomy", sections: { dash: "read", products: "write", brands: "write", skus: "write", serialized: "write", variant_groups: "write", compliance: "write", localizations: "write", content: "write", taxonomy: "write", attributes: "write", analytics: "read", monitor: "read", qcops: "write" } },
  { key: "orders", name: "Order Desk", desc: "Orders, returns, RFQs", sections: { dash: "read", orders: "write", returns: "write", rfqs: "write", compliance: "read", analytics: "read", qcops: "write", tradeops: "read" } },
  { key: "marketing", name: "Growth", desc: "Offers, coupons, promotions, content, AI", sections: { dash: "read", offers: "write", content: "write", promotions: "write", ai: "write", webhooks: "write", analytics: "read", monitor: "read", affiliate: "write" } },
  { key: "finance", name: "Finance", desc: "Billing, payments, settlements, contracts, tenders", sections: { dash: "read", billing: "write", payments: "write", settlements: "write", contracts: "write", tenders: "write", suppliers: "read", analytics: "write", audit: "read", finops: "write", tradeops: "write" } },
  { key: "support", name: "Support", desc: "Read-only across the store + act on returns + privacy requests", sections: { dash: "read", orders: "read", returns: "write", products: "read", customers: "read", settings: "read", analytics: "read", privacy: "write" } }
];

/* revisioned self-heal: a role row nobody has edited follows the in-code ROLES
   when the stamp moves (so a new section or role ships without a code-bound DB
   reset); an operator's edit is stamped `edited=1` and never clobbered thereafter. */
const RBAC_STAMP = "rb_v6";   /* v6: per-tenant role sets (staffRoles:t<id> overrides) */
function seed() {
  const row = db().get("SELECT items,edited FROM meta_lists WHERE name='staffRoles'") || {};
  const edited = row.edited || 0;
  const current = J(row.items, ROLES);
  const sameShape = JSON.stringify(current) === JSON.stringify(ROLES);
  if (!row.items || (!edited && !sameShape))
    db().run("INSERT INTO meta_lists(name,label,items,edited) VALUES('staffRoles','staffRoles',?,0) ON CONFLICT(name) DO UPDATE SET items=excluded.items, edited=excluded.edited", JSON.stringify(ROLES));
}
/* per-tenant role sets: a store may define its own roles, stored as
   'staffRoles:t<tenantId>'. A store with no row of its own inherits the shared
   default ('staffRoles'), so nothing changes for existing stores until an operator
   deliberately forks that store's set. tenantId 0/null names the shared default. */
const rowName = tenantId => (tenantId ? "staffRoles:t" + Number(tenantId) : "staffRoles");
function roles(tenantId) {
  const name = rowName(tenantId);
  const row = db().get("SELECT items FROM meta_lists WHERE name=?", name) || {};
  if (row.items) return J(row.items, ROLES);
  /* only the shared default falls back to the in-code ROLES; a tenant row that has
     gone missing resolves to the current default rather than to nothing */
  return tenantId ? roles(0) : ROLES;
}
function role(tenantId, key) {
  const t = key === undefined ? null : tenantId;   /* a missing key never matches; keep the old single-arg misuse honest */
  return roles(t).find(r => r.key === key) || null;
}

/* ---------- role management — roles are DATA, so an operator defines and re-scopes
   them from the console; no code ships for a new role. Every write stamps edited=1,
   which the seed's self-heal honours forever: the shipped ROLES array is a DEFAULT,
   never an overwrite of an operator's intent.
   Guards: a key is a stable slug; a grant names a real section (or '*') with one of the
   three access values; 'owner' is never deletable — it is the backward-safe default a
   staff member with no role set falls back to, and deleting it would orphan every row
   that resolves to full access.
   Tenant semantics: saving for a store writes that store's own row. The effective list
   (roles(tenantId)) already includes the inherited default, so the first edit to a
   store FORKS the whole set — the store keeps every role it had and diverges from
   there, instead of starting empty. ---------- */
const KEY_RE = /^[a-z][a-z0-9_-]{1,30}$/;
function saveRoles(tenantId, list) {
  const name = rowName(tenantId);
  const label = tenantId ? ("staffRoles · store " + Number(tenantId)) : "staffRoles";
  db().run("INSERT INTO meta_lists(name,label,items,edited) VALUES(?,?,?,1)"
    + " ON CONFLICT(name) DO UPDATE SET items=excluded.items, edited=1", name, label, JSON.stringify(list));
}
function validateRole(role, sections) {
  const errs = [];
  const key = String((role || {}).key || "").trim();
  if (!KEY_RE.test(key)) errs.push("key must be 2-31 chars, start with a letter, and use only a-z, 0-9, _ or -");
  const name = String((role || {}).name || "").trim();
  if (!name) errs.push("a role name is required");
  const secs = (role || {}).sections && typeof (role || {}).sections === "object" ? (role || {}).sections : {};
  for (const [k, v] of Object.entries(secs)) {
    if (k !== "*" && !sections.includes(k)) errs.push("unknown section: " + k);
    if (!["write", "read", false].includes(v)) errs.push("grant for '" + k + "' must be write, read or off");
  }
  return { errs, key, name, secs };
}
/* create or replace a role by key. An existing role with the same key is overwritten in
   full — the editor sends the whole grant map, so partial merges would silently keep
   revoked grants the operator just cleared */
function upsertRole(tenantId, role) {
  const v = validateRole(role, SECTIONS);
  if (v.errs.length) return { ok: false, fails: v.errs };
  const list = roles(tenantId);
  const rec = { key: v.key, name: v.name, desc: String((role || {}).desc || "").slice(0, 200), sections: v.secs };
  const i = list.findIndex(r => r.key === v.key);
  if (i < 0) list.push(rec); else list[i] = rec;
  saveRoles(tenantId, list);
  return { ok: true, role: rec };
}
function deleteRole(tenantId, key) {
  const k = String(key || "");
  if (k === "owner") return { ok: false, fails: ["the owner role cannot be deleted — it is the default full-access role"] };
  if (!role(tenantId, k)) return { ok: false, fails: ["no such role: " + k] };
  /* a role held on THIS store blocks the delete; another store's role set is irrelevant
     (and may not even define this key) */
  const held = tenantId
    ? db().all("SELECT id FROM users WHERE staff_role=? AND tenant_id=?", k, Number(tenantId))
    : db().all("SELECT id FROM users WHERE staff_role=?", k);
  if (held.length) return { ok: false, fails: ["reassign the " + held.length + " staff member(s) holding this role first"] };
  saveRoles(tenantId, roles(tenantId).filter(r => r.key !== k));
  return { ok: true };
}
/* does a store have its own role set, or is it still inheriting the shared default? */
function hasOwnSet(tenantId) {
  return !!db().get("SELECT 1 ok FROM meta_lists WHERE name=?", rowName(tenantId));
}
/* a store that has forked its set can re-merge into the shared default; the shared
   default itself is the seed row and is never dropped here */
function resetToDefault(tenantId) {
  if (!tenantId) return { ok: false, fails: ["the shared default set cannot be reset"] };
  db().run("DELETE FROM meta_lists WHERE name=?", rowName(tenantId));
  return { ok: true };
}

/* expand a sections grant map (supports '*') */
function expand(sections) {
  const out = {};
  if (sections["*"]) { for (const s of SECTIONS) out[s] = sections["*"]; if (sections["*"] === "write") Object.keys(out).forEach(k => out[k] = "write"); }
  for (const s of Object.keys(sections)) if (s !== "*") out[s] = sections[s];
  return out;
}
/* grant() resolves a staff member's effective section map. The tenant is what makes a
   role mean what THIS store says it means: 'manager' can be scoped differently on every
   store, so the store the user belongs to is the store whose role set we read. It is
   taken from the explicit argument when the caller already knows the session's store
   (the API passes it — the same request's tenant), and otherwise from the user row
   itself, so the pure-function callers (expand-only tests) still resolve correctly.
   A user row carrying tenant_id is therefore self-describing: the grant follows the
   account, not the caller's whim. */
function grant(user, tenantId) {
  // user: { role, staff_role, perms(json), tenant_id? }
  if (!user || user.role !== "admin") return {};
  const sr = user.staff_role || "owner";
  const tid = tenantId != null ? tenantId : (user.tenant_id != null ? user.tenant_id : null);
  const r = role(tid, sr);
  let sec = r ? expand(r.sections) : expand({ "*": "write" });
  const override = J(user.perms, {});
  for (const k of Object.keys(override)) sec[k] = override[k]; // per-user add/remove
  return sec;
}
function allowedSections(user, tenantId) { const g = grant(user, tenantId); return Object.keys(g).filter(k => g[k]); }
function can(user, section, mode, tenantId) { const g = grant(user, tenantId); const have = g[section]; if (!have) return false; return mode === "write" ? have === "write" : true; }

/* map an entity key (Data Studio / generic CRUD) → console section */
const KEY_SECTION = { product: "products", brand: "brands", sku: "skus", inventory: "skus", warehouse: "skus", serialized: "serialized", variant_group: "skus", compliance: "compliance", localization: "localizations", order: "orders", ret: "returns", rfq: "rfqs", seller: "sellers", settlement: "settlements", contract: "contracts", tender: "tenders", supplier: "suppliers", product_supplier: "suppliers", promotion: "offers", customer: "orders", review: "products", banner: "content", card: "content", department: "content", taxonomy: "taxonomy", attribute: "attributes", gateway: "payments", payment: "billing", tenant: "studio", plan: "studio", subscription: "studio", invoice: "billing", ai_usage: "ai", ai_task: "ai", offer: "offers", coupon: "offers", country: "studio", currency: "studio", tax_mode: "studio", provider_def: "payments", dark_store: "qcops", delivery_slot: "qcops", service_area: "qcops", store_inventory: "qcops", rider: "qcops", dispatch_run: "qcops", upi_handle: "finops", upi_collect: "finops", qr_code: "finops", payment_link: "finops", mandate: "finops", escrow_hold: "finops", split_payment: "finops", kyc_profile: "finops", bank_payout: "finops", biller: "finops", bill_payment: "finops", recharge: "finops", recharge_plan: "finops", bnpl_account: "finops", bnpl_emi: "finops", loan: "finops", insurance_policy: "finops", gift_voucher: "finops", seller_onboarding: "mktops", seller_offer: "mktops", fba_inbound: "mktops", seller_performance: "mktops", buyer_claim: "mktops", smart_fulfilment: "mktops", sponsored_creative: "mktops", trade_assurance: "tradeops", gold_supplier: "tradeops", company_verification: "tradeops", export_document: "tradeops", letter_of_credit: "tradeops", rfq_quote: "tradeops", tender_bid: "tradeops", price_list: "tradeops", price_list_item: "tradeops", gift_registry: "tradeops", notification: "orders", compare_list: "products", invoice_document: "billing", consent: "privacy", privacy_request: "privacy" };
function sectionForEntity(key) {
  /* a composed capability's records (cp_*) authorize against the composition section —
     the composition engine mints these keys, so the map is a prefix rule, not a lookup */
  if (typeof key === "string" && key.startsWith("cp_")) return "compose";
  return KEY_SECTION[key] || "studio";
}

module.exports = { SECTIONS, ROLES, seed, roles, role, upsertRole, deleteRole, grant, allowedSections, can, expand, sectionForEntity, KEY_SECTION, hasOwnSet, resetToDefault, J };
