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

const SECTIONS = ["dash", "products", "brands", "skus", "orders", "returns", "rfqs", "sellers", "settlements", "contracts", "tenders", "suppliers", "serialized", "compliance", "localizations", "offers", "content", "taxonomy", "attributes", "payments", "modules", "settings", "billing", "analytics", "audit", "monitor", "studio", "ai", "webhooks", "trash", "team", "qcops", "finops", "mktops", "tradeops", "affiliate", "sitemap", "shipping"];

const ROLES = [
  { key: "owner", name: "Owner", desc: "Full control", sections: { "*": "write" } },
  { key: "manager", name: "Store Manager", desc: "Everything except team + platform settings", sections: { "*": "write", team: false, settings: "read", studio: false } },
  { key: "catalog", name: "Catalog", desc: "Products, SKUs, inventory, content, taxonomy", sections: { dash: "read", products: "write", brands: "write", skus: "write", serialized: "write", variant_groups: "write", compliance: "write", localizations: "write", content: "write", taxonomy: "write", attributes: "write", analytics: "read", monitor: "read", qcops: "write" } },
  { key: "orders", name: "Order Desk", desc: "Orders, returns, RFQs", sections: { dash: "read", orders: "write", returns: "write", rfqs: "write", compliance: "read", analytics: "read", qcops: "write", tradeops: "read" } },
  { key: "marketing", name: "Growth", desc: "Offers, coupons, promotions, content, AI", sections: { dash: "read", offers: "write", content: "write", promotions: "write", ai: "write", webhooks: "write", analytics: "read", monitor: "read", affiliate: "write" } },
  { key: "finance", name: "Finance", desc: "Billing, payments, settlements, contracts, tenders", sections: { dash: "read", billing: "write", payments: "write", settlements: "write", contracts: "write", tenders: "write", suppliers: "read", analytics: "write", audit: "read", finops: "write", tradeops: "write" } },
  { key: "support", name: "Support", desc: "Read-only across the store + act on returns", sections: { dash: "read", orders: "read", returns: "write", products: "read", customers: "read", settings: "read", analytics: "read" } }
];

/* revisioned self-heal: a role row nobody has edited follows the in-code ROLES
   when the stamp moves (so a new section or role ships without a code-bound DB
   reset); an operator's edit is stamped and never clobbered thereafter. */
const RBAC_STAMP = "rb_v2";
function seed() {
  const row = db().get("SELECT items,edited FROM meta_lists WHERE name='staffRoles'") || {};
  const edited = row.edited || 0;
  const current = J(row.items, ROLES);
  const sameShape = JSON.stringify(current) === JSON.stringify(ROLES);
  if (!row.items || (!edited && !sameShape))
    db().run("INSERT INTO meta_lists(name,label,items,edited) VALUES('staffRoles','staffRoles',?,0) ON CONFLICT(name) DO UPDATE SET items=excluded.items, edited=excluded.edited", JSON.stringify(ROLES));
}
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
const KEY_SECTION = { product: "products", brand: "brands", sku: "skus", inventory: "skus", warehouse: "skus", serialized: "serialized", variant_group: "skus", compliance: "compliance", localization: "localizations", order: "orders", ret: "returns", rfq: "rfqs", seller: "sellers", settlement: "settlements", contract: "contracts", tender: "tenders", supplier: "suppliers", product_supplier: "suppliers", promotion: "offers", customer: "orders", review: "products", banner: "content", card: "content", department: "content", taxonomy: "taxonomy", attribute: "attributes", gateway: "payments", payment: "billing", tenant: "studio", plan: "studio", subscription: "studio", invoice: "billing", ai_usage: "ai", ai_task: "ai", offer: "offers", coupon: "offers", country: "studio", currency: "studio", tax_mode: "studio", provider_def: "payments", dark_store: "qcops", delivery_slot: "qcops", service_area: "qcops", store_inventory: "qcops", rider: "qcops", dispatch_run: "qcops", upi_handle: "finops", upi_collect: "finops", qr_code: "finops", payment_link: "finops", mandate: "finops", escrow_hold: "finops", split_payment: "finops", kyc_profile: "finops", bank_payout: "finops", biller: "finops", bill_payment: "finops", recharge: "finops", recharge_plan: "finops", bnpl_account: "finops", bnpl_emi: "finops", loan: "finops", insurance_policy: "finops", gift_voucher: "finops", seller_onboarding: "mktops", seller_offer: "mktops", fba_inbound: "mktops", seller_performance: "mktops", buyer_claim: "mktops", smart_fulfilment: "mktops", sponsored_creative: "mktops", trade_assurance: "tradeops", gold_supplier: "tradeops", company_verification: "tradeops", export_document: "tradeops", letter_of_credit: "tradeops", rfq_quote: "tradeops", tender_bid: "tradeops", price_list: "tradeops", price_list_item: "tradeops", gift_registry: "tradeops", notification: "orders", compare_list: "products", invoice_document: "billing" };
function sectionForEntity(key) { return KEY_SECTION[key] || "studio"; }

module.exports = { SECTIONS, ROLES, seed, roles, role, grant, allowedSections, can, sectionForEntity, KEY_SECTION, J };
