/* LUXORA Platform — PLATFORM RBAC: roles for the platform console's own operators.
 *
 * The store console has had staff roles + per-section permissions since rbac.js; the
 * platform console was all-or-nothing — every platform_admins row could do everything,
 * including launching stores, rotating keys and reading every tenant's audit trail. That
 * made the platform-admin CRUD surface I added genuinely dangerous to hand out.
 *
 * This mirrors the store's conventions exactly so the two feel like one system:
 *   - roles live in meta_lists as DATA ('platformRoles'), seeded with a stamp; an
 *     operator's edit is stamped edited=1 and is never clobbered by a code update,
 *   - a role grants a map of section -> 'read' | 'write' | false, '*' expands to all,
 *   - a per-admin 'perms' JSON override layer takes precedence,
 *   - the seed owner keeps full access (role unset => owner), so nothing breaks on
 *     existing installs the moment this ships.
 *
 * Section keys are the platform console's NAV leaf keys, grouped into the capability
 * areas an operator is actually entrusted with ( provisioning, tenancy, money, ops… ).
 * Any leaf not named in a grant is hidden from that admin and refused by the API. */
"use strict";

let _db = null;
const db = () => _db || (_db = require("./db.js"));
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };

/* the grant surface. Keys are EXACTLY the platform console's NAV leaf keys
 * (public/js/platform.js), so a grant and the nav button it lights up can never
 * disagree, and '*' expands to the whole tree — the owner keeps all 12 sections. */
const SECTIONS = ["identity","identity-templates","persons","organizations","tenants","users","roles","permissions","credentials","authentication","authorization","trust","verification","kyc","kyb","identity-graph","countries","states","cities","jurisdictions","addresses","geo","geography","calendars","schedules","recurrence","appointments","reservations","time-windows","delivery-slots","availability","sla","temporal","currencies","fx","currency-universe","languages","localization","translation","cultural","gproducts","product-families","product-types","variants","attributes","specifications","bundles","collections","product-graph","product-registry","global-services","service-types","service-plans","entitlements","service-registry","gcatalog","taxonomy","categories","taxonomy-universe","brands","suppliers","vendors","manufacturers","assets","documents","media","content","knowledge-graph","ontology","semantic","canonical-registry","customers","sellers","buyers","partners","distributors","dealers","franchises","workforce","leads","opportunities","accounts","contacts","activities","pipelines","contracts","agreements","relationships","business-networks","business-organizations","catalogs","pricing","dynamic-pricing","price-lists","promotions","merchandising","goffers","loyalty","rewards","referrals","goffers-affiliates","goip","gmarket","marketplace","advertising","sponsored","gb2b","rfq","tenders","trade-assurance","letters-of-credit","cart","checkout","gorders","returns","reviews","subs","memberships","recurring-billing","plans","subs-plans","invoices","billing","gfinance","payments","settlements","escrow","gops","inventory","warehousing","procurement","stock-transfers","replenishment","fulfilment","fba","logistics","transportation","shipping","tracking","reverse-logistics","field-ops","work-orders","maintenance","dark-stores","dispatch","riders","gsupport","tickets","cases","incidents","qna","websites","mobile","kiosks","portals","gcontent","themes","branding","personalization","accessibility","ui-components","channels","notifications","email","social","ux-journeys","customer-journeys","experience-registry","ai","ai-models","agents","agent-teams","prompts","reasoning","recommendation","search-intel","personalization-intel","optimization","simulation","forecasting","digital-twins","fraud","risk-intel","knowledge-intel","autonomous-planning","autonomous-execution","autonomous-verification","learning","evolution","ganalytics","experiments","intelligence-registry","policies","standards","regulations","rules","decisions","compliance","compliance-controls","certifications","privacy","privacy-requests","erasure","grisk","risk","risk-blocks","security","controls","evidence","audit","review-governance","approvals","change-control","trace","ai-governance","agent-governance","governance-graph","capabilities","capability-tree","capability-registry","capability-composition","capability-discovery","compose","providers","modules","connectors","integrations","extensions","runtime","runtime-registry","deployment","infrastructure","apis","events","workflows","versioning","migration","deprecation","impact-analysis","self-healing","self-optimization","dash","monitor","metrics","logs","traces","alerting","reliability","health-availability","capacity","performance","health","dashboards","gdata","studio","definitions","slo","rca","diagnostics","cost","tenants-admin","companies","workspaces","environments","users-admin","roles-admin","permissions-admin","padmins","licenses","gteam","configurations","secrets","settings","feature-flags","provisioning","ucii","ucos","foundations","universes","domains","canonical-objects","canonical-schemas","canonical-relationships","canonical-events","canonical-apis","canonical-workflows","capability-graph","knowledge-graph-arch","dependency-graph","traceability-graph","reference-architecture","security-architecture","data-architecture","ai-architecture","evolution-architecture","manual","architecture"];

/* the capability areas the shipped roles are phrased in. A role names any subset of
 * SECTIONS; these aliases are only documentation of what a role intends to cover. */
const AREAS = {
  sell: ["dash", "tenants", "tenants-admin", "geo", "countries", "currencies", "fx", "providers", "gorders", "gcatalog", "gb2b", "gmarket", "gfinance", "gsupport", "gcontent", "ganalytics", "gops", "gdata", "gteam", "brands", "taxonomy", "gproducts", "monitor", "trace", "grisk"],
  money: ["plans", "subs", "invoices", "billing", "gfinance", "payments", "settlements", "escrow"],
  secure: ["security", "padmins", "policies", "runtime", "identity", "audit", "keys"]
};

/* the shipped roles. 'support' is the point of the feature: an operator who can sell
 * and look after stores but cannot rewire the platform's own security or money plumbing.
 * 'owner' is the seed role — backward-safe default when an admin has no role set. */
const ROLES = [
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

/* revisioned self-heal — same contract as rbac.js: an unedited row follows the in-code
 * ROLES when the stamp moves; an operator's edit is preserved forever. */
const PBAC_STAMP = "pb_v1";
function seed() {
  const row = db().get("SELECT items,edited FROM meta_lists WHERE name='platformRoles'") || {};
  const edited = row.edited || 0;
  const current = J(row.items, ROLES);
  const sameShape = JSON.stringify(current) === JSON.stringify(ROLES);
  if (!row.items || (!edited && !sameShape))
    db().run("INSERT INTO meta_lists(name,label,items,edited) VALUES('platformRoles','platformRoles',?,0) ON CONFLICT(name) DO UPDATE SET items=excluded.items, edited=excluded.edited", JSON.stringify(ROLES));
}
function roles() { return J((db().get("SELECT items FROM meta_lists WHERE name='platformRoles'") || {}).items, ROLES); }
function role(key) { return roles().find(r => r.key === key) || null; }

/* ---------- role management — the mirror of rbac.js for this console's own operators.
   Same contract: a write stamps edited=1 and the shipped ROLES array stays a default,
   never an overwrite. 'owner' is never deletable: it is the role an admin with no role
   set resolves to, so removing it would orphan the seed admin's full access. ---------- */
const KEY_RE = /^[a-z][a-z0-9_-]{1,30}$/;
function saveRoles(list) {
  db().run("INSERT INTO meta_lists(name,label,items,edited) VALUES('platformRoles','platformRoles',?,1)"
    + " ON CONFLICT(name) DO UPDATE SET items=excluded.items, edited=1", JSON.stringify(list));
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
function upsertRole(role) {
  const v = validateRole(role, SECTIONS);
  if (v.errs.length) return { ok: false, fails: v.errs };
  const list = roles();
  const rec = { key: v.key, name: v.name, desc: String((role || {}).desc || "").slice(0, 200), sections: v.secs };
  const i = list.findIndex(r => r.key === v.key);
  if (i < 0) list.push(rec); else list[i] = rec;
  saveRoles(list);
  return { ok: true, role: rec };
}
function deleteRole(key) {
  const k = String(key || "");
  if (k === "owner") return { ok: false, fails: ["the owner role cannot be deleted — it is the default full-access role"] };
  if (!role(k)) return { ok: false, fails: ["no such role: " + k] };
  const held = db().all("SELECT id FROM platform_admins WHERE role=?", k);
  if (held.length) return { ok: false, fails: ["reassign the " + held.length + " operator(s) holding this role first"] };
  saveRoles(roles().filter(r => r.key !== k));
  return { ok: true };
}

function expand(sections) {
  const out = {};
  if (sections["*"]) { for (const s of SECTIONS) out[s] = sections["*"]; if (sections["*"] === "write") Object.keys(out).forEach(k => out[k] = "write"); }
  for (const s of Object.keys(sections)) if (s !== "*") out[s] = sections[s];
  return out;
}
/* admin: { role } where role is the platform role key (NULL/unknown => owner, so the
 * seeded owner and any existing row keep full access on upgrade). */
function grant(admin) {
  if (!admin) return expand({ "*": "write" });
  const rk = admin.role || "owner";
  const r = role(rk);
  let sec = r ? expand(r.sections) : expand({ "*": "write" });
  const override = J(admin.perms, {});
  for (const k of Object.keys(override)) sec[k] = override[k];
  return sec;
}
function allowedSections(admin) { const g = grant(admin); return Object.keys(g).filter(k => g[k]); }
function can(admin, section, mode) {
  const g = grant(admin);
  const have = g[section];
  if (!have) return false;
  return mode === "write" ? have === "write" : true;
}

/* map a platform API route prefix -> console section, so generic endpoints authorize
 * against the same grants the nav advertises. Anything unmapped falls back to 'dash'
 * (broad read) rather than being silently open. */
const ROUTE_SECTION = {
  tenants: "tenants", "tenants/setup": "tenants",
  geo: "geo", "global/country": "geo", "global/currency": "geo", fx: "geo",
  providers: "providers", "global/provider": "providers", "custom-providers": "providers",
  plans: "plans", "global/plan": "plans", subs: "subs", subscriptions: "subs",
  invoices: "invoices", billing: "billing", usage: "billing",
  modules: "modules",
  goip: "offers",
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
  revenue: "ganalytics"
};
function sectionForRoute(path) {
  const p = String(path || "").replace(/^\/?api\/(platform\/)?/, "").replace(/[?].*$/, "");
  const seg = p.split("/")[0];
  if (ROUTE_SECTION[seg]) return ROUTE_SECTION[seg];
  const two = p.split("/").slice(0, 2).join("/");
  return ROUTE_SECTION[two] || "dash";
}

module.exports = { SECTIONS, ROLES, PBAC_STAMP, seed, roles, role, upsertRole, deleteRole, grant, allowedSections, can, expand, sectionForRoute, J };
