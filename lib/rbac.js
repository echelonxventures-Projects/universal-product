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

const SECTIONS = ["dash", "products", "skus", "orders", "returns", "rfqs", "sellers", "settlements", "contracts", "tenders", "suppliers", "serialized", "compliance", "localizations", "offers", "content", "taxonomy", "attributes", "payments", "modules", "settings", "billing", "analytics", "audit", "monitor", "studio", "ai", "webhooks", "trash", "team"];

const ROLES = [
  { key: "owner", name: "Owner", desc: "Full control", sections: { "*": "write" } },
  { key: "manager", name: "Store Manager", desc: "Everything except team + platform settings", sections: { "*": "write", team: false, settings: "read", studio: false } },
  { key: "catalog", name: "Catalog", desc: "Products, SKUs, inventory, content, taxonomy", sections: { dash: "read", products: "write", skus: "write", serialized: "write", variant_groups: "write", compliance: "write", localizations: "write", content: "write", taxonomy: "write", attributes: "write", analytics: "read", monitor: "read" } },
  { key: "orders", name: "Order Desk", desc: "Orders, returns, RFQs", sections: { dash: "read", orders: "write", returns: "write", rfqs: "write", compliance: "read", analytics: "read" } },
  { key: "marketing", name: "Growth", desc: "Offers, coupons, promotions, content, AI", sections: { dash: "read", offers: "write", content: "write", promotions: "write", ai: "write", webhooks: "write", analytics: "read", monitor: "read" } },
  { key: "finance", name: "Finance", desc: "Billing, payments, settlements, contracts, tenders", sections: { dash: "read", billing: "write", payments: "write", settlements: "write", contracts: "write", tenders: "write", suppliers: "read", analytics: "write", audit: "read" } },
  { key: "support", name: "Support", desc: "Read-only across the store + act on returns", sections: { dash: "read", orders: "read", returns: "write", products: "read", customers: "read", settings: "read", analytics: "read" } }
];

function seed() { db().run("INSERT OR IGNORE INTO meta_lists(name,label,items) VALUES('staffRoles','staffRoles',?)", JSON.stringify(ROLES)); }
function roles() { return J((db().get("SELECT items FROM meta_lists WHERE name='staffRoles'") || {}).items, ROLES); }
function role(key) { return roles().find(r => r.key === key) || null; }

/* expand a sections grant map (supports '*') */
function expand(sections) {
  const out = {};
  if (sections["*"]) { for (const s of SECTIONS) out[s] = sections["*"]; if (sections["*"] === "write") Object.keys(out).forEach(k => out[k] = "write"); }
  for (const s of Object.keys(sections)) if (s !== "*") out[s] = sections[s];
  return out;
}
function grant(user) {
  // user: { role, staff_role, perms(json) }
  if (!user || user.role !== "admin") return {};
  const sr = user.staff_role || "owner";
  const r = role(sr);
  let sec = r ? expand(r.sections) : expand({ "*": "write" });
  const override = J(user.perms, {});
  for (const k of Object.keys(override)) sec[k] = override[k]; // per-user add/remove
  return sec;
}
function allowedSections(user) { const g = grant(user); return Object.keys(g).filter(k => g[k]); }
function can(user, section, mode) { const g = grant(user); const have = g[section]; if (!have) return false; return mode === "write" ? have === "write" : true; }

/* map an entity key (Data Studio / generic CRUD) → console section */
const KEY_SECTION = { product: "products", sku: "skus", inventory: "skus", warehouse: "skus", serialized: "serialized", variant_group: "skus", compliance: "compliance", localization: "localizations", order: "orders", ret: "returns", rfq: "rfqs", seller: "sellers", settlement: "settlements", contract: "contracts", tender: "tenders", supplier: "suppliers", product_supplier: "suppliers", promotion: "offers", customer: "orders", review: "products", banner: "content", card: "content", department: "content", taxonomy: "taxonomy", attribute: "attributes", gateway: "payments", payment: "billing", tenant: "studio", plan: "studio", subscription: "studio", invoice: "billing", ai_usage: "ai", ai_task: "ai", offer: "offers", coupon: "offers", country: "studio", currency: "studio", tax_mode: "studio", provider_def: "payments" };
function sectionForEntity(key) { return KEY_SECTION[key] || "studio"; }

module.exports = { SECTIONS, ROLES, seed, roles, role, grant, allowedSections, can, sectionForEntity, KEY_SECTION, J };
