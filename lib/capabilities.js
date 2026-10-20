/* LUXORA Platform — The Capability Layer.
   --------------------------------------------------------------------------
   "Configure types, standards, quality, features and functionalities of any
   platform or service" — this module is that statement made literal.

   A CAPABILITY is one individually switchable, individually tunable function of
   the platform: "buy_box", "trade_assurance", "qr_pay", "instant_delivery"…
   Each ships its own set of PARAMS (a standard, a threshold, a weight, a fee),
   declared with a type and a default. The parity engines contain no business-rule
   literal whatsoever: they ask `cap()` for the value and act on the answer.

    COMPOSITION, NOT TEMPLATE. A tenant does not pick a template — it composes a
    platform capability-by-capability: a buy-box, a dispatch OTP and a UPI collect
    may all be enabled in one store while trade assurance stays off. Every preset
    below is a seeded worked example; they are rows, so an operator renames, edits
    or deletes them, or defines a brand-new archetype from the console. No engine
    knows which capabilities a tenant uses until it asks — the "platform type" IS
    the set of rows, not a code branch, and no vendor, product or brand name is
    baked into any definition: a capability declares what it does and which knobs
    tune it, never whose it is. Parity with any platform is a consequence of the
    composition, not a label.

   RESOLUTION ORDER for a parameter: tenant's own override → the preset the
   tenant is assigned (if any) → the platform default declared in this catalog.
   An unknown capability or param falls back to its declared default, and a
   capability that is not enabled answers `false` for every param — so a
   disabled capability is inert, never an error. (Architecture3 §2.1: No
   Hard-Coded Business Logic, Registry Driven Everything, Infinite
   Composability, Infinite Extensibility.) */
"use strict";
/* seed data (lib/seed/capabilities.json): data, not code — the registries are seeded from it */
const SEED_CAPABILITIES = require("./seed/capabilities.json");

const db = () => require("./db.js");
const J = (v, d) => { try { return v == null || v === "" ? (d == null ? {} : d) : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d == null ? {} : d; } };

/* ============================================================
   THE CATALOG — the platform's declaration of what is configurable.
   Every `params` entry is { type, default, label, unit? }. This is the ONLY
   place a business-rule default lives, and it is data: an operator edits the
   row in platform_capabilities and every engine follows on the next call.
   ============================================================ */
/* notes that lived in the seed literal (now lib/seed/capabilities.json): */
/* ---------- Marketplace: standards of listing trust & competition ---------- */
/* ---------- Fintech: the rails of money movement ---------- */
/* ---------- Quick-commerce: the promise engine ---------- */
/* ---------- B2B trust & trade ---------- */
/* ---------- Storefront: the shopper-facing surfaces ----------
   Formerly settings.features.* booleans. Each was a silent flag on a settings
   row; each is now an atom in the same catalog as buy_box and escrow, so a
   feature is switched and tuned exactly the way a capability is, and the grant
   engine derives the console surface it lights through the same SECTIONS map. */
/* ---------- Mobility: the ride-hailing / dispatch universe (E17) ----------
   Constitution E17: configuration alone yields Uber-, Ola-, DoorDash-, Swiggy- and
   Zomato-class platforms. The engine (lib/mobility.js) reads every value below
   through cap(); nothing about a fare, a match radius or a cancellation penalty is
   hard-coded, so an operator retunes the row and the marketplace follows. */
/* ---------- Operations: the ERP / HRMS / SCM universe (E18) ----------
   Constitution E18: configuration alone yields SAP-, Oracle-, ServiceNow- and
   Workday-class platforms. The engine (lib/operations.js) reads every value below
   through cap(); nothing about a tax rate, an overtime multiple, an approval
   threshold, a yield or an internal cost rate is hard-coded. */
const CATALOG = SEED_CAPABILITIES.CATALOG;

/* ---------- seeding: the catalog becomes rows, once, without clobbering ---------- */
/* the stamped catalog version. A row whose seeded_from differs and that nobody
   has edited follows the catalog when it changes; bump this to revise the seed. */
const CATALOG_STAMP = "cap_v6";   /* v6: the operations universe (E18) joins the catalog —
                                     workforce, procurement, manufacturing, projects. Zero
                                     hard-coded rules: every tax rate, overtime multiple,
                                     approval threshold, yield and cost rate is a param
                                     lib/operations.js reads through cap() */

/* ---------- the console surface an atom governs ----------
   A store console section is not a bundle someone buys: it is the shadow of the
   individual capabilities this tenant switched on. Each ATOM declares the nav leaves
   it lights — buy_box lights Marketplace & Marketplace Ops; rfq_bidding lights RFQs;
   instant_delivery lights Quick-commerce Ops. The grant engine (lib/authz.js) derives
   the store surface from the tenant's LIVE composition through this map, so a leaf
   appears the moment its atom is on and nothing is ever granted as a package. A section
   no atom names is governed by the tenant's own profile (NAVFIT) instead — vertical
   facts like serial tracking and replenishment, which no engine owns.
   Seeded into the catalog column; an operator's edit is the truth at runtime, with the
   declared list a floor (same rule as params — an operator may add a leaf an atom
   lights, never delete one the console would then hide while its engine still runs). */
/* notes that lived in the seed literal (now lib/seed/capabilities.json): */
/* mobility atoms (E17) — each lights its console leaf; the grant engine derives the
   store surface from the live composition, so a ride-hailing store's nav appears the
   moment the atom is on and never as a package */
/* operations atoms (E18) — the ERP surface. Each lights its own console leaf; the
   grant engine derives the store nav from the live composition, so an operator
   composing an ERP store sees exactly the atoms they switched on, never a package */
const SECTIONS = SEED_CAPABILITIES.SECTIONS;
/* the storefront atoms own no console section — a shopper-facing toggle is not a
   store-console leaf. Declared here so the grant engine never has to special-case
   the domain, and so the console's capability list can label the group. */
const STOREFRONT_KEYS = CATALOG.filter(c => c.settings_atom).map(c => c.key);
/* SEED DEFAULTS. These atoms replace settings.features.* booleans that shipped ON
   (or off) for every store. The platform-level `enabled` column is seeded to match
   the old settings default exactly, so an existing store sees no behaviour change on
   the migration — the flag moves house, it does not flip. */
const SEED_ENABLED = Object.fromEntries(CATALOG.filter(c => c.seed_enabled === false).map(c => [c.key, false]));
/* a storefront atom the platform policy must also allow names its policy flag on its row
   (`policy`, with the refusal it shows); a settings feature name maps to its atom key */
const atomKey = k => String(k).replace(/([A-Z])/g, (_, c) => "_" + c.toLowerCase());
const policyRow = k => { const c = CATALOG.find(x => x.key === atomKey(k)); return c && c.policy ? c : null; };
/* is turning this feature on refused by the platform policy? → the row's message, else null */
function policyRefusal(featureKey, policy) { const c = policyRow(featureKey); return c && !(policy || {})[c.policy] ? (c.policy_message || c.label + " is disabled by platform policy") : null; }
/* every policy-gated atom, on exactly when its policy flag allows it (a new store's start) */
function policyFeatures(policy) { const out = {}; for (const c of CATALOG.filter(x => x.policy)) out[c.key] = !!(policy || {})[c.policy]; return out; }
function seedEnabled(key) { return SEED_ENABLED[key] !== false; }

/* the section list a catalog row resolves: the atom's declared leaves ∪ the operator's
   own (authored atoms have no declaration — theirs is the whole story) */
function sectionsOf(key, row) {
  const base = row && Array.isArray(row.sections) ? row.sections : [];
  const floor = SECTIONS[key] || [];
  return [...new Set(floor.concat(base))];
}

function seed() {
  const D = db();
  const stamp = CATALOG_STAMP;
  CATALOG.forEach((c, i) => {
    const params = {};
    for (const [k, p] of Object.entries(c.params)) params[k] = { type: p.type, default: p.default, label: p.label, unit: p.unit };
    const ex = D.get("SELECT params, seeded_from, edited FROM platform_capabilities WHERE key=?", c.key);
    if (!ex) D.run("INSERT INTO platform_capabilities(key,label,domain,icon,description,params,sections,enabled,position,seeded_from) VALUES(?,?,?,?,?,?,?,?,?,?)",
      c.key, c.label, c.domain, c.icon, c.description, JSON.stringify(params), JSON.stringify(SECTIONS[c.key] || []), seedEnabled(c.key) ? 1 : 0, i, stamp);
    /* SELF-HEAL, BUT NEVER AN OVERWRITE. A row nobody has touched follows the
       catalog when the catalog changes (a new param, a revised description, a new
       section it lights) — detected by the stamped version moving on. The moment an
       operator edits a row from the console, `edited` is set and the row is theirs
       forever: the catalog may grow around it, it never clobbers the operator's tuning. */
    else if (!ex.edited && ex.seeded_from !== stamp) D.run("UPDATE platform_capabilities SET params=?, seeded_from=?, label=?, description=?, sections=? WHERE key=?",
      JSON.stringify(params), stamp, c.label, c.description, JSON.stringify(SECTIONS[c.key] || []), c.key);
  });
}

/* ---------- resolution ---------- */
function catalogRow(key) {
  const r = db().get("SELECT * FROM platform_capabilities WHERE key=?", key);
  if (!r) { const c = CATALOG.find(x => x.key === key); return c ? { key, params: c.params, sections: SECTIONS[key] || [], enabled: 1 } : null; }
  return { ...r, params: J(r.params, {}), sections: sectionsOf(key, r) };
}
function catalogKeys(domain) {
  return (domain ? CATALOG.filter(c => c.domain === domain) : CATALOG).map(c => c.key);
}
/* is the capability switched on for this tenant? A capability disabled at
   platform level, or never enabled for the tenant, is off.
   One exception, and it is deliberate: the STOREFRONT atoms replace settings
   flags that shipped ON for every store, so a tenant with no explicit row keeps
   the seed default rather than going dark. Marketplace/fintech/trade/qc atoms stay
   opt-in — absence means off — which preserves the parity layer's semantics. */
function tenantDefault(key) {
  return STOREFRONT_KEYS.indexOf(key) >= 0 && seedEnabled(key);
}
/* opts.buyer === false decides for the platform alone (a cached settings snapshot, a menu);
   otherwise the current request's buyer joins the context, so a capability scoped to a
   segment, channel or service is on for exactly those buyers (lib/rules.js) */
function on(tenantId, key, opts) {
  const cap = catalogRow(key);
  if (!cap || !cap.enabled) return false;
  const v = db().get("SELECT enabled FROM capability_values WHERE tenant_id=? AND capability=?", Number(tenantId), key);
  if (!(v ? !!v.enabled : tenantDefault(key))) return false;
  const rules = require("./rules.js");
  return rules.permitsAt("capability.on", key, rules.at("capability.on", tenantId, { buyer: !(opts && opts.buyer === false) }));
}
/* the effective parameter set for one capability + tenant:
   platform default → assigned preset → the tenant's own row */
function params(tenantId, key) {
  const cap = catalogRow(key);
  if (!cap) return {};
  const out = {};
  /* a seeded capability's catalog params are a FLOOR: an operator may add or
     retune a param, but can never accidentally delete one an engine reads
     (cap() would then answer undefined and the engine would misbehave silently).
     An operator-authored capability owns its params outright — there is no
     in-code catalog to fall back to, by design. */
  const seedCat = CATALOG.find(x => x.key === key);
  const declared = Object.assign({}, seedCat ? seedCat.params : {}, cap.params || {});
  for (const [k, p] of Object.entries(declared)) out[k] = p.default;
  const tid = Number(tenantId);
  const presetRow = db().get("SELECT preset_key FROM capability_preset_assignments WHERE tenant_id=?", tid);
  if (presetRow) {
    const preset = db().get("SELECT capabilities FROM capability_presets WHERE key=?", presetRow.preset_key);
    const entry = preset ? J(preset.capabilities, {})[key] : null;
    if (entry && entry.params) Object.assign(out, entry.params);
  }
  const mine = db().get("SELECT params FROM capability_values WHERE tenant_id=? AND capability=?", tid, key);
  if (mine) Object.assign(out, J(mine.params, {}));
  /* last: the params of the applicability rules that match this context (a fee, a limit
     for one country, segment or service), platform rules first, the platform's own after */
  try { const rules = require("./rules.js"); Object.assign(out, rules.decideAt("capability.on", key, rules.at("capability.on", tid)).params || {}); } catch (e) { }
  return out;
}
/* the single read the engines make: `cap(t, "trade_assurance").assurance_fee_pct`.
   A disabled capability answers falsy for everything, so the caller can guard
   on the same call it reads from. */
function cap(tenantId, key) {
  if (!on(tenantId, key)) return {};
  return params(tenantId, key);
}
/* the migration bridge: apply a legacy {featureKey: bool} map onto the composition.
   Each storefront atom is switched on or off for the tenant; a key that is not an
   atom is returned untouched so the caller keeps it on the settings row. This is the
   ONE write path the settings save, the onboarding wizard and tenant authoring share,
   so a feature is never written two ways. */
function applyFeatures(tenantId, feats) {
  if (!feats || typeof feats !== "object") return {};
  const leftover = {};
  for (const [k, v] of Object.entries(feats)) {
    const key = String(k).replace(/([A-Z])/g, (_, c) => "_" + c.toLowerCase());
    if (STOREFRONT_KEYS.indexOf(key) >= 0) {
      if (v) enable(tenantId, key, null, "settings.features"); else disable(tenantId, key);
    } else leftover[k] = !!v;
  }
  return leftover;
}
/* the settings row only persists keys that are NOT atoms — the atoms own their own
   rows. Reading back what a store still holds outside the catalog. */
function leftoverFeatures(tenantId) {
  const out = {};
  try {
    const row = db().get("SELECT value FROM settings WHERE tenant_id=? AND key='features'", Number(tenantId) || 1);
    const saved = row ? J(row.value, {}) : {};
    for (const k of Object.keys(saved)) {
      const key = String(k).replace(/([A-Z])/g, (_, c) => "_" + c.toLowerCase());
      if (STOREFRONT_KEYS.indexOf(key) < 0) out[k] = saved[k];
    }
  } catch (e) { }
  return out;
}

/* ---------- composition: the platform a tenant actually is ---------- */
/* the capabilities a tenant has switched on, each with its effective params —
   this object IS the tenant's platform type; there is no other definition */
function compositionOf(tenantId) {
  const tid = Number(tenantId);
  const rows = db().all("SELECT capability, enabled, params FROM capability_values WHERE tenant_id=? ORDER BY capability", tid);
  const presetRow = db().get("SELECT preset_key FROM capability_preset_assignments WHERE tenant_id=?", tid);
  const out = { tenant_id: tid, preset: presetRow ? presetRow.preset_key : null, capabilities: {} };
  for (const r of rows) {
    const cap = catalogRow(r.capability);
    if (!cap || !cap.enabled || !r.enabled) continue;
    const p = {};
    for (const [k, v] of Object.entries(cap.params || {})) p[k] = v.default;
    Object.assign(p, J(r.params, {}));
    out.capabilities[r.capability] = { enabled: true, domain: cap.domain, label: cap.label, params: p };
  }
  /* a default-on atom with no explicit row is still part of the composition —
     the platform a tenant "is" includes what it has not switched off */
  for (const key of STOREFRONT_KEYS) {
    if (out.capabilities[key]) continue;
    if (on(tenantId, key)) {
      const cap = catalogRow(key);
      const p = {};
      for (const [k, v] of Object.entries(cap.params || {})) p[k] = v.default;
      out.capabilities[key] = { enabled: true, domain: cap.domain, label: cap.label, params: p, defaulted: true };
    }
  }
  return out;
}
/* enable a capability for a tenant, with optional param overrides */
function enable(tenantId, key, overrides, notes) {
  const cap = catalogRow(key);
  if (!cap) throw new Error("Unknown capability: " + key);
  if (!cap.enabled) throw new Error("Capability is disabled at platform level: " + key);
  const p = overrides && typeof overrides === "object" ? overrides : {};
  db().run("INSERT INTO capability_values(tenant_id,capability,enabled,params,notes) VALUES(?,?,1,?,?) ON CONFLICT(tenant_id,capability) DO UPDATE SET enabled=1, params=excluded.params, notes=excluded.notes",
    Number(tenantId), key, JSON.stringify(p), String(notes || ""));
  try { require("./settings.js").bust(tenantId); } catch (e) { }
  return compositionOf(tenantId);
}
function disable(tenantId, key) {
  /* a default-on atom has no row to UPDATE — switching it off must INSERT an
     explicit enabled=0, or the tenant default keeps it alive */
  db().run("INSERT INTO capability_values(tenant_id,capability,enabled,params,notes) VALUES(?,?,0,'','') ON CONFLICT(tenant_id,capability) DO UPDATE SET enabled=0",
    Number(tenantId), key);
  try { require("./settings.js").bust(tenantId); } catch (e) { }
  return compositionOf(tenantId);
}
/* apply a named preset to a tenant: each entry becomes a capability_values row */
function applyPreset(tenantId, presetKey) {
  const D = db();
  const preset = D.get("SELECT * FROM capability_presets WHERE key=?", presetKey);
  if (!preset) throw new Error("Unknown capability preset: " + presetKey);
  const caps = J(preset.capabilities, {});
  for (const [key, entry] of Object.entries(caps)) {
    const cap = catalogRow(key);
    if (!cap) continue;
    D.run("INSERT INTO capability_values(tenant_id,capability,enabled,params) VALUES(?,?,?,?) ON CONFLICT(tenant_id,capability) DO UPDATE SET enabled=excluded.enabled, params=excluded.params",
      Number(tenantId), key, entry.enabled === false ? 0 : 1, JSON.stringify(entry.params || {}));
  }
  D.run("INSERT INTO capability_preset_assignments(tenant_id,preset_key) VALUES(?,?) ON CONFLICT(tenant_id,preset_key) DO NOTHING", Number(tenantId), presetKey);
  return compositionOf(tenantId);
}

/* ---------- presets: named, reusable blends (rows, not code) ---------- */
/* notes that lived in the seed literal (now lib/seed/capabilities.json): */
/* the list this blend shipped with before — a row still holding it exactly was never
   edited, so it follows the new list */
/* deliberately mixed: proves the platform is a composition, not a template —
   marketplace competition, quick-commerce dispatch and fintech rails in one
   store, none of it inherited from a single template */
/* E17 · the mobility universe: the constitution names Uber-, Ola-, DoorDash-, Swiggy-
   and Zomato-class platforms as configuration, not code. The four atoms are the whole
   platform — the fare, the surge, the match and the fleet — each retuned per store */
/* E18 · the operations universe: the constitution names SAP-, Oracle-, ServiceNow- and
   Workday-class platforms as configuration, not code. Registering an ERP is now a
   platform type, not an atom-by-atom build */
const PRESETS = SEED_CAPABILITIES.PRESETS;
function seedPresets() {
  const D = db();
  for (const p of PRESETS) {
    /* the declared content fills an empty slot only — an operator's edit to it is kept */
    D.run("INSERT INTO capability_presets(key,label,description,capabilities,universes) VALUES(?,?,?,?,?) ON CONFLICT(key) DO UPDATE SET label=excluded.label, description=excluded.description, universes=COALESCE(capability_presets.universes, excluded.universes)",
      p.key, p.label, p.description, JSON.stringify(p.capabilities), JSON.stringify(p.universes || []));
    if (p.universesWas) D.run("UPDATE capability_presets SET universes=? WHERE key=? AND universes=?", JSON.stringify(p.universes), p.key, JSON.stringify(p.universesWas));
    /* a blend that grew (new atoms joined it) reaches an install whose row still holds the
       blend exactly as it shipped before — an operator's edited blend is never touched */
    if (p.capabilitiesWas) D.run("UPDATE capability_presets SET capabilities=? WHERE key=? AND capabilities=?", JSON.stringify(p.capabilities), p.key, JSON.stringify(p.capabilitiesWas));
  }
}

/* ---------- the configuration surface (the console lives here) ---------- */
/* the whole catalog as the console renders it: every capability with its
   declared params, its domain and its platform switch */
function catalog() {
  return db().all("SELECT * FROM platform_capabilities ORDER BY position, key")
    .map(r => ({ ...r, params: J(r.params, {}), sections: sectionsOf(r.key, r) }));
}
/* every archetype (preset) — seeded worked examples plus the operator's own */
function presets() {
  return db().all("SELECT * FROM capability_presets ORDER BY key")
    .map(r => ({ ...r, capabilities: J(r.capabilities, {}), universes: J(r.universes, []) }));
}
/* coerce a value to the param's DECLARED type. The console's inputs arrive as
   strings; the engines expect typed values. An unknown capability or param, or a
   value that cannot be coerced, is refused — a configured standard is validated,
   never silently dropped */
function coerce(capKey, param, value) {
  const cap = catalogRow(capKey);
  if (!cap) throw new Error("Unknown capability: " + capKey);
  const def = (cap.params || {})[param];
  if (!def) throw new Error("Unknown parameter: " + param + " on " + capKey);
  const t = def.type;
  if (t === "number") { const n = Number(value); if (!isFinite(n)) throw new Error(param + " must be a number"); return n; }
  if (t === "bool") return /^(1|true|yes|on)$/i.test(String(value));
  if (t === "json") { try { return typeof value === "string" ? JSON.parse(value) : value; } catch (e) { throw new Error(param + " must be valid JSON"); } }
  return String(value);
}
/* tune ONE parameter for a tenant. The capability is enabled and the param merged
   onto the defaults — configuring a standard is the act of switching it on */
function tune(tenantId, key, param, value) {
  const v = coerce(key, param, value);
  const cur = db().get("SELECT params FROM capability_values WHERE tenant_id=? AND capability=?", Number(tenantId), key);
  const merged = { ...(cur ? J(cur.params, {}) : {}), [param]: v };
  return enable(tenantId, key, merged);
}
/* platform-level: switch a capability off for every tenant, or retitle it. Marks
   the row edited so the catalog's future revisions never clobber the decision */
function setPlatform(key, patch) {
  const cap = catalogRow(key);
  if (!cap) throw new Error("Unknown capability: " + key);
  const sets = [], vals = [];
  if (patch && patch.enabled != null) { sets.push("enabled=?"); vals.push(patch.enabled ? 1 : 0); }
  if (patch && patch.label != null) { sets.push("label=?"); vals.push(String(patch.label).trim()); }
  if (patch && patch.description != null) { sets.push("description=?"); vals.push(String(patch.description)); }
  if (!sets.length) throw new Error("nothing to update");
  sets.push("edited=1"); vals.push(key);
  db().run("UPDATE platform_capabilities SET " + sets.join(",") + " WHERE key=?", ...vals);
  /* a platform-level switch changes every tenant's derived features — drop the
     whole settings cache so no store serves a stale snapshot */
  try { require("./settings.js").bust(0); } catch (e) { }
  return catalogRow(key);
}
/* author an archetype: a named, reusable capability set. Unknown capabilities are
   dropped rather than persisted — a preset may only reference the real catalog */
function savePreset(key, label, description, capabilities, universes) {
  const k = String(key || "").trim();
  if (!k) throw new Error("preset key required");
  const clean = {};
  for (const [ck, v] of Object.entries(capabilities || {})) {
    if (!catalogRow(ck)) continue;
    clean[ck] = { enabled: !(v && v.enabled === false), params: (v && v.params) || {} };
  }
  /* the catalogue content the archetype opens a new store with: universe keys, or left
     as it was when the caller does not name any */
  const uv = Array.isArray(universes) ? [...new Set(universes.map(x => String(x).trim()).filter(x => /^[a-z0-9_]{1,80}$/.test(x)))] : null;
  db().run("INSERT INTO capability_presets(key,label,description,capabilities,universes) VALUES(?,?,?,?,?) ON CONFLICT(key) DO UPDATE SET label=excluded.label, description=excluded.description, capabilities=excluded.capabilities, universes=COALESCE(excluded.universes, capability_presets.universes)",
    k, String(label || k).trim(), String(description || ""), JSON.stringify(clean), uv ? JSON.stringify(uv) : null);
  return presets().find(p => p.key === k);
}
function removePreset(key) {
  if (!key) throw new Error("preset key required");
  db().run("DELETE FROM capability_presets WHERE key=?", String(key));
  db().run("DELETE FROM capability_preset_assignments WHERE preset_key=?", String(key));
  return { ok: true };
}

/* ---------- AUTHORING: the catalog is open-ended ----------
   This is the difference between a configurable commerce platform and a
   configurable ANY platform. The seeded catalog covers commerce domains; an
   operator extends it from the console to define a capability no release knew
   about — surge pricing for a mobility platform, creator payouts for a video
   one, lead scoring for a CRM — each with its own typed parameters. Every
   engine, form and dropdown that reads the catalog follows on the next call,
   because the catalog IS the vocabulary. */
function define(key, label, domain, icon, description, params) {
  const D = db();
  const k = String(key || "").trim();
  if (!k) throw new Error("capability key required");
  if (!String(label || "").trim()) throw new Error("capability label required");
  const decl = {};
  for (const [pk, p] of Object.entries(params || {})) {
    const t = String((p && p.type) || "text").toLowerCase();
    if (!["number", "bool", "text", "json"].includes(t))
      throw new Error("param '" + pk + "' has an unknown type '" + t + "' (number | bool | text | json)");
    decl[pk] = { type: t, default: p == null ? undefined : p.default, label: String((p && p.label) || pk), unit: p && p.unit ? String(p.unit) : undefined };
  }
  const pos = D.get("SELECT COALESCE(MAX(position), -1) + 1 p FROM platform_capabilities");
  /* seeded_from 'operator' marks a row the catalog never seeded — it is the
     operator's own, and it is the signal the console uses to offer deletion
     (a seeded row can only be disabled, never removed) */
  D.run("INSERT INTO platform_capabilities(key,label,domain,icon,description,params,enabled,position,seeded_from,edited) VALUES(?,?,?,?,?,?,1,?,?,1) ON CONFLICT(key) DO UPDATE SET label=excluded.label, domain=excluded.domain, icon=excluded.icon, description=excluded.description, params=excluded.params, edited=1",
    k, String(label).trim(), String(domain || "custom").trim(), String(icon || "▪").slice(0, 4),
    String(description || ""), JSON.stringify(decl), pos ? pos.p : 0, "operator");
  return catalogRow(k);
}
/* removing a capability: a seeded one cannot be deleted (the code that reads it
   still exists — disable it platform-wide instead); an authored one can, but
   only once no store is using it, or its composition would reference a phantom */
function undefine(key) {
  const D = db();
  const k = String(key || "").trim();
  if (!k) throw new Error("capability key required");
  if (CATALOG.some(c => c.key === k))
    throw new Error("a seeded capability cannot be deleted — switch it off platform-wide instead");
  if (D.get("SELECT 1 FROM capability_values WHERE capability=? AND enabled=1 LIMIT 1", k))
    throw new Error("a capability a store has switched on cannot be deleted — switch it off first");
  D.run("DELETE FROM capability_values WHERE capability=?", k); /* clear orphaned disabled rows */
  D.run("DELETE FROM platform_capabilities WHERE key=?", k);
  return { ok: true };
}

module.exports = {
  CATALOG, PRESETS, SECTIONS, STOREFRONT_KEYS, SEED_ENABLED, policyRefusal, policyFeatures, seed, seedPresets,
  catalogRow, catalogKeys, on, params, cap, sectionsOf, tenantDefault,
  compositionOf, enable, disable, applyPreset, applyFeatures, leftoverFeatures,
  catalog, presets, coerce, tune, setPlatform, savePreset, removePreset,
  define, undefine
};
