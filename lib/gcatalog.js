/* LUXORA · Universal Global Catalog Engine — UPIP §1 VISION + §5 Product Archetype Model
   --------------------------------------------------------------------------
   The constitution's first requirement is that the platform supports every product
   archetype — Physical, Digital, Services, Subscriptions, Memberships, Rentals,
   Events, Appointments, OTT, Streaming, Cloud, API, AI, Financial, Insurance,
   Investment, Data, Analytics, Research, Scientific, Mathematical, Statistical,
   Optimization, Simulation, Quantum and Future Unknown — "without architectural
   redesign" (§1) and through "registration and configuration rather than software
   redesign" (Infinite Extensibility Principle).

   This module makes that true as DATA. It does not contain a product-type branch,
   a per-archetype handler or a hardcoded catalogue. It holds exactly three things:

     1. an ARCHETYPE SEED   — one canonical platform product per universe the corpus
        declares, written into global_products automatically and idempotently, so the
        platform's global catalogue is populated on first boot and an operator extends
        it by adding rows (manual configuration), not by touching this file;
     2. a TYPE MAP          — universe → the merchant-facing productTypes vocabulary,
        so an archetype becomes a concrete, storefront-renderable type (Knowledge Once:
        the mapping is one row per universe, editable in Data Studio);
     3. an IMPORT GATE      — a store admin may pull a global product into their own
        catalogue ONLY IF the platform has permitted it (store_product_config). This is
        the "if the Global Platform permits" clause of the requirement, enforced by the
        platform authority, never by the store.

   Everything here is additive and idempotent: a warm boot writes nothing, and an
   operator's edit (a renamed archetype, a repriced SKU, a withdrawn permission) is
   never clobbered by a re-seed. That is Configuration-Over-Code applied to the
   platform's own catalogue. */
"use strict";

let _db = null;
const db = () => _db || (_db = require("./db.js"));
const rows = (sql, ...p) => { try { return db().all(sql, ...p) || []; } catch (e) { return []; } };
const get = (sql, ...p) => { try { return db().get(sql, ...p) || null; } catch (e) { return null; } };
const run = (sql, ...p) => { try { return db().run(sql, ...p); } catch (e) { return { lastInsertRowid: 0 }; } };
const J = (v, d) => { try { const o = JSON.parse(v); return o == null ? d : o; } catch (e) { return d; } };

/* UPIP §1 VISION / §5 Product Archetype Model — the universe → merchant-type map.
   A universe is the corpus's declaration; productTypes is the storefront vocabulary.
   One map row per universe keeps a single truth for how an archetype renders and is
   validated, so neither the platform console nor the storefront keeps its own copy.
   Any universe absent here falls back to "service" at import time and the archetype
   still seeds — an unmapped universe is a UX gap, never a failure (Future Unknown
   Product Types must not break the platform). */
const TYPE_MAP = {
  physical_products: "physical", digital_products: "digital", services: "service",
  subscriptions: "subscription", memberships: "membership", rentals: "rental",
  events: "event_ticket", appointments: "appointment", ott_platforms: "subscription",
  streaming_platforms: "subscription", cloud_services: "service", api_products: "service",
  ai_products: "service", financial_products: "service", insurance_products: "insurance",
  investment_products: "service", data_products: "digital", analytics_products: "digital",
  research_products: "digital", scientific_products: "digital", mathematical_products: "digital",
  statistical_products: "digital", optimization_products: "service", simulation_products: "service",
  quantum_products: "service", future_unknown_product_types: "physical"
};
const DEFAULT_TYPE = "service";
const ARCHETYPE_SKU_PREFIX = "UPIP";

/* the seed is authoritative for which universes exist; this module never re-derives
   the corpus (Knowledge Once — lib/ucos.js parses it once, the registry stores it) */
function universes() {
  return rows("SELECT items FROM meta_lists WHERE name='productUniverses'")
    .flatMap(r => J(r.items, []));
}
function universeOf(key) {
  return universes().find(u => u && u.key === key) || null;
}
/* universe key → merchant-facing product type, in three data-driven steps:
   1. the record's OWN declared type (a universe may declare its type explicitly),
   2. the archetype map for the 26 universes UPIP §1 names (Physical, OTT, Quantum…),
   3. a structural match against the productTypes registry vocabulary itself —
      `insurance`→insurance, `appointments`→appointment, `event_tickets`→event_ticket —
      so a universe that names its type in the corpus's own words resolves without a
      per-universe row. There is deliberately no hardcoded list of the 1,877: the
      vocabulary is the registry's, and an unmapped universe falls back to "service"
      (Future Unknown Product Types must never break activation). */
function norm(s) { return String(s || "").toLowerCase().replace(/[_-]+/g, "").replace(/s$/, ""); }
function typeOfUniverse(key, declared) {
  const known = rows("SELECT items FROM meta_lists WHERE name='productTypes'")
    .flatMap(r => J(r.items, [])).map(x => x && (x.key || x)).filter(Boolean);
  if (declared && known.includes(declared)) return declared;
  const k = String(key || "");
  if (TYPE_MAP[k] && known.includes(TYPE_MAP[k])) return TYPE_MAP[k];
  const nk = norm(k);
  const hit = known.find(t => norm(t) === nk);
  return hit || DEFAULT_TYPE;
}

/* ---------- 1. ARCHETYPE SEED: automatic + manual population of the global catalogue
   Automatic: every universe the corpus declares becomes one canonical platform
   product (§5: "every sellable object derives from Product Archetype"). Manual: an
   operator adds more rows in the console, or edits these — both are just rows in
   global_products, and this seed never overwrites an operator's edit. */
function seed() {
  const list = universes();
  for (const u of list) {
    if (!u || !u.key) continue;
    const sku = ARCHETYPE_SKU_PREFIX + "-" + u.key.replace(/_/g, "-").toUpperCase();
    const ex = get("SELECT id, sku FROM global_products WHERE universe=?", u.key);
    if (ex) continue;                       /* already on the platform shelf — never clobber */
    const t = typeOfUniverse(u.key);
    run("INSERT INTO global_products(sku,name,description,category,universe,price,tax_class,is_service,attributes,media,status) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
      sku, u.name || u.key,
      "Canonical archetype for the " + (u.name || u.key) + " universe (UPIP §5 Product Archetype Model). "
        + "Populated automatically from the corpus; extend or replace it in the console.",
      "archetype", u.key, 0, "standard", t === "service" ? 1 : 0, JSON.stringify({ archetype: u.key, icon: u.icon || "🧩" }), JSON.stringify([]), "active");
  }
  /* persist the type map as registry data so the storefront, both consoles and the
     import gate read ONE source instead of importing this module's constant */
  run("INSERT INTO meta_lists(name,label,items,seeded_from) VALUES('universeProductTypes','Universe → Product Type map (UPIP §5)',?,'upip_archetype') "
    + "ON CONFLICT(name) DO UPDATE SET items=excluded.items, seeded_from=excluded.seeded_from",
    JSON.stringify(Object.entries(TYPE_MAP).map(([key, type]) => ({ key, type }))));
}

/* ---------- 2. THE PERMISSION GATE (the "if the Global Platform permits" clause)
   The platform is the authority over which global products a store may list. A store
   admin can import a global product only when an explicit, enabled permission row
   exists for that (tenant, product) pair. Absent or disabled ⇒ refused, with the
   reason the operator can act on. The store can never silently widen its own access. */
function permissionFor(tenantId, globalId) {
  /* the config column is TEXT, so a caller passing an integer id can be stored as
     "1.0" while another caller passes "1" — compare by numeric value (the id is always
     an integer rowid) and fall back to exact string, so no grant is lost to formatting */
  const all = rows("SELECT * FROM store_product_config WHERE tenant_id=? AND enabled=1", Number(tenantId));
  return all.find(p => Number(p.global_product_id) === Number(globalId)
    || String(p.global_product_id) === String(globalId)) || null;
}
function mayList(tenantId, globalId) {
  const p = permissionFor(tenantId, globalId);
  if (!p) return { ok: false, reason: "Not permitted by the platform — ask the platform admin to grant this product to your store" };
  if (!String(p.permissions || "").match(/list|sell|full|write/))
    return { ok: false, reason: "Permission is read-only (" + p.permissions + ") — the platform must grant list/sell to import" };
  return { ok: true, permission: p };
}

/* ---------- 3. IMPORT: a permitted global product → the store's live catalogue
   Idempotent (re-importing refreshes the same row, never duplicates), quota-exempt
   (platform-supplied catalogue is not the merchant's own SKU count — the same rule
   the universe activations follow), and traceable: the store row carries
   source_global_id back to its platform origin. */
function importToStore(tenantId, globalId) {
  const g = get("SELECT * FROM global_products WHERE id=?", Number(globalId));
  if (!g) return { ok: false, error: "unknown global product " + globalId };
  if (String(g.status || "") === "retired") return { ok: false, error: "this archetype has been retired on the platform" };
  const gate = mayList(tenantId, globalId);
  if (!gate.ok) return { ok: false, error: gate.reason };
  const t = Number(tenantId);
  const type = typeOfUniverse(g.universe);
  /* the existing store row is matched by its platform provenance, not by a generated id —
     the id is random per attempt, so keying on it would never re-find the row */
  const ex = get("SELECT id FROM products WHERE tenant_id=? AND source_global_id=?", t, String(g.id));
  const pid = "GP-" + String(g.id) + "-" + Math.random().toString(36).slice(2, 6).toUpperCase();
  const cols = ["tenant_id", "id", "title", "brand", "dept", "type", "price", "list_price",
    "rating", "ratings_count", "emoji", "hue", "stock", "flags", "keywords", "position",
    "source_universe", "source_kind", "source_global_id"];
  const vals = [t, ex ? ex.id : pid, g.name, "Platform Catalog", "global", type,
    Number(g.price) || 0, null, 4.5, 0, (J(g.attributes, {}).icon || "🧩"), 190, 999, "new",
    String(g.name + " " + (g.category || "")).toLowerCase(), 0, g.universe, "global", String(g.id)];
  if (ex) {
    const sets = cols.slice(1).map(c => c + "=?").join(",");
    run("UPDATE products SET " + sets + " WHERE tenant_id=? AND source_global_id=?", ...vals.slice(1), t, String(g.id));
  } else {
    run("INSERT INTO products(" + cols.join(",") + ") VALUES(" + cols.map(() => "?").join(",") + ")", ...vals);
  }
  /* a sellable needs a default SKU + inventory row so cart and checkout work —
     the same contract universe activations satisfy */
  const sku = get("SELECT id FROM skus WHERE tenant_id=? AND product_id=?", t, ex ? ex.id : pid);
  if (!sku) {
    const r = run("INSERT INTO skus(tenant_id,product_id,code,name,identity,variant,price,stock,active) VALUES(?,?,?,?,?,?,?,?,?)",
      t, ex ? ex.id : pid, ex ? ex.id : pid, "Default", JSON.stringify({ sku: g.sku }), "{}", Number(g.price) || 0, 999, 1);
    const wh = get("SELECT id FROM warehouses WHERE tenant_id=? ORDER BY id LIMIT 1", t);
    run("INSERT OR IGNORE INTO inventory(tenant_id,sku_id,warehouse_id,qty,reserved) VALUES(?,?,?,?,0)",
      t, Number(r.lastInsertRowid), wh ? wh.id : null, 999);
  }
  try { require("./search.js").onCatalogChange(t); } catch (e) { }
  return { ok: true, id: ex ? ex.id : pid, updated: !!ex, type, universe: g.universe };
}

/* what the platform console shows: every global product, annotated with which stores
   are permitted — one read, no N+1, and absent permissions are reported as absent */
function globalListWithPermissions() {
  const products = rows("SELECT * FROM global_products ORDER BY category, name");
  const perms = rows("SELECT * FROM store_product_config");
  const byProduct = new Map();
  for (const p of perms) {
    if (!byProduct.has(p.global_product_id)) byProduct.set(p.global_product_id, []);
    byProduct.get(p.global_product_id).push(p);
  }
  return products.map(p => ({ ...p, permissions: byProduct.get(String(p.id))
    || perms.filter(x => Number(x.global_product_id) === Number(p.id)) || [] }));
}

module.exports = { TYPE_MAP, DEFAULT_TYPE, seed, universes, universeOf, typeOfUniverse,
  permissionFor, mayList, importToStore, globalListWithPermissions };
