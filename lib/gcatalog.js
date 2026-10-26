/* LUXORA · the global catalogue — the platform master as the platform console and the store
   import see it (GLOBAL_MASTER.md, P27).

   The catalogue owns no truth. Every global product is an item of the platform master
   (lib/platform-master.js): its kind, its place in the trade taxonomy, its product universe, its
   codes, its title and description, its media, its lifecycle and the store-facing profile the
   platform authors. This module only projects an item into the record the console edits and the
   import copies, and writes such a record back as master writes:

     sku          → the item's code under the sku scheme
     name, description → its multilingual title and description, in the source language
     category     → where it sits in the trade taxonomy (a taxonomy key)
     universe     → where it sits among the product universes the constitution declares
     type         → the item kind the universe sells as (data on the kinds vocabulary)
     status       → its lifecycle term
     price, tax_class, attributes, profile → the profile the platform authors for stores

   An install that predates the master kept these rows in a table of their own; seed() moves
   every row onto the master once — keeping its code, its place and its profile, re-pointing the
   store permissions and imported products that named it — and drops the table.

   A store may list a global product only when the platform has permitted it: a permission on
   the master (lib/master-permissions.js) that allows it to select the item. That gate is the
   platform's authority, never the store's. */
"use strict";

let _db = null;
const db = () => _db || (_db = require("./db.js"));
const M = () => require("./platform-master.js");
const MP = () => require("./master-permissions.js");
const K = () => require("./kernel.js");
const J = (v, d) => { try { const o = typeof v === "string" ? JSON.parse(v) : v; return o == null ? d : o; } catch (e) { return d; } };
const fail = (msg, status) => { const e = new Error(msg); e.status = status || 400; throw e; };
/* the scheme a seller's own code is held under (the master names it by role) */
const SKU_ROLE = () => M().ROLES.sellerCode;
const lang = () => require("./expression.js").SEED.sourceLanguage;
const text = v => v == null ? "" : String(K().text(v, lang()) || "");

/* ---------- universes and the kind each sells as ---------- */
function universes() { return require("./registry.js").list("productUniverses") || []; }
function universeOf(key) { return universes().find(u => u && u.key === key) || null; }
/* a key names a declared universe exactly, or by the same words (singular or plural, any
   separator) — a corpus entity named "insurance_product" is the "insurance_products" universe */
const words = k => String(k || "").toLowerCase().split(/[^a-z0-9]+/).filter(Boolean).map(w => w.replace(/s$/, "")).join(" ");
function resolveUniverse(key) {
  const u = universes();
  return (u.find(x => x && x.key === key) || u.find(x => x && words(x.key) === words(key)) || {}).key || String(key || "");
}
/* universe → the item kind's name (its productTypes key): data on the master's kinds vocabulary.
   A key that is no declared universe but has the words of a kind's name ("Insurance") is that kind */
function typeOfUniverse(key) {
  const u = resolveUniverse(key);
  if (universes().some(x => x && x.key === u)) return M().kindForUniverse(u).name;
  const named = M().vocabulary(M().ROLES.itemKinds).find(t => words(t.name) === words(key));
  return named ? named.name : M().kindForUniverse(u).name;
}
/* every declared universe with the kind it sells as — what the console's type column reads */
function universeTypes() { return universes().map(u => ({ key: u.key, type: typeOfUniverse(u.key) })); }

/* ---------- projection: a master item as a catalogue record ---------- */
/* a master item as a record; for a holder, as that holder sees it (its addenda over the master,
   the attributes its permission shows) — null when it does not see it */
function project(uid, holder) {
  const n = holder ? require("./master-contributions.js").view(holder, uid) : M().node(uid);
  if (!n) return null;
  const prof = { ...(n.attributes.profile || {}) };
  const { price, tax_class, attributes } = prof;
  delete prof.price; delete prof.tax_class; delete prof.attributes;
  const universe = M().universeOf(n.uid);
  const placed = K().placementsOf(M().TRADE, n.uid, { namespace: M().NAMESPACE }).filter(Boolean);
  const life = M().lifecycleTerm(n.attributes.lifecycle) || {};
  const type = universe ? typeOfUniverse(universe) : (M().vocabulary(M().ROLES.itemKinds).find(t => t.kind === n.kind) || {}).name;
  const kindTerm = M().vocabulary(M().ROLES.itemKinds).find(t => t.name === type) || {};
  return {
    id: n.uid, sku: n.identifiers[SKU_ROLE()] || "", name: text(n.attributes.title), description: text(n.attributes.description),
    category: placed.length ? M().keyOf(placed[0]) : "", universe, type, kind: n.kind,
    is_service: kindTerm.service ? 1 : 0, price: Number(price) || 0, tax_class: tax_class || "", attributes: attributes || {},
    media: n.attributes.media || [], profile: prof, status: life.name || "", retired: !!life.retired
  };
}
function list(filter) {
  const f = filter || {};
  return M().items(f.category ? { under: f.category } : {}).map(n => project(n.uid))
    .filter(p => (!f.status || p.status === f.status) && (!f.universe || p.universe === f.universe))
    .sort((a, b) => a.category.localeCompare(b.category) || a.name.localeCompare(b.name));
}
const find = ref => { const uid = M().uidOf(ref) || K().resolveIdentifier(SKU_ROLE(), String(ref || "")); return uid ? project(uid) : null; };

/* ---------- writing a catalogue record back as master writes ---------- */
function put(rec, ref, actor) {
  const r = rec || {};
  const sku = String(r.sku || "").trim(), name = String(r.name || "").trim();
  if (!sku || !name) fail("sku and name required");
  const holder = K().resolveIdentifier(SKU_ROLE(), sku);
  const universe = r.universe && universeOf(r.universe) ? r.universe : null;
  const at = r.category && M().uidOf(r.category) ? [r.category] : [];
  const profile = { ...(r.profile || {}), price: Number(r.price) || 0, tax_class: r.tax_class || "", attributes: r.attributes || {} };
  const L = lang();
  const fields = { title: { [L]: name }, description: r.description ? { [L]: String(r.description) } : null, media: r.media || [], profile, lifecycle: r.status || undefined };
  if (!ref) {
    if (holder) fail("SKU " + sku + " is already used by another global product", 409);
    return M().createItem({ kind: M().vocabulary(M().ROLES.itemKinds).find(t => t.name === typeOfUniverse(universe || "")).kind,
      at, universe: universe || undefined, identifiers: { [SKU_ROLE()]: sku }, ...fields, lifecycle: r.status || M().vocabulary(M().ROLES.lifecycle).find(t => t.default).name }, actor);
  }
  const cur = find(ref);
  if (!cur) fail("Unknown global product", 404);
  if (holder && holder !== cur.id) fail("SKU " + sku + " is already used by another global product", 409);
  K().internal.tx(() => {
    if (cur.sku !== sku) {
      if (cur.sku) K().endIdentifier(cur.id, SKU_ROLE(), cur.sku, null, actor);
      K().assignIdentifier(cur.id, SKU_ROLE(), sku, {}, actor);
    }
    M().update(cur.id, { ...fields, lifecycle: r.status || cur.status }, actor);
    M().move(cur.id, { at, universe: universe || null }, actor);
  });
  return cur.id;
}
/* removing a global product retires it: hidden from every listing, its history kept */
function remove(ref, actor) {
  const cur = find(ref);
  if (!cur) fail("Unknown global product", 404);
  const retired = M().vocabulary(M().ROLES.lifecycle).find(t => t.retired);
  M().update(cur.id, { lifecycle: retired.name }, actor);
  require("./kernel-lifecycle.js").archive(cur.id, actor);
  return cur.id;
}

/* ---------- an install that predates the master: its table moves onto the master once ---------- */
function legacyTable(name) {
  const D = db();
  const rows = D.USE_PG
    ? D.all("SELECT table_name AS name FROM information_schema.tables WHERE table_name=?", name)
    : D.all("SELECT name FROM sqlite_master WHERE type='table' AND name=?", name);
  return rows.length > 0;
}
const legacy = { products: "global_products", access: "store_product_config" };
function seed() {
  const moved = moveLegacy();
  /* store access an older install kept as rows becomes permissions (after the move re-pointed them) */
  MP().adoptLegacy();
  return moved;
}
function moveLegacy() {
  if (!legacyTable(legacy.products)) return 0;
  const D = db();
  let moved = 0;
  K().internal.tx(() => {
    for (const g of D.all("SELECT * FROM global_products ORDER BY id")) {
      const prof = J(g.profile, {});
      const uid = K().resolveIdentifier(SKU_ROLE(), g.sku) || put({ sku: g.sku, name: g.name, description: g.description, category: g.category, universe: g.universe,
        price: g.price, tax_class: g.tax_class, attributes: J(g.attributes, {}), media: J(g.media, []), profile: prof, status: g.status }, null, "migration");
      /* what named the row by its old number now names the item */
      if (legacyTable(legacy.access))
        D.run("UPDATE store_product_config SET global_product_id=? WHERE CAST(global_product_id AS INTEGER)=? AND global_product_id NOT LIKE '%-%'", uid, Number(g.id));
      D.run("UPDATE products SET source_global_id=? WHERE source_global_id=?", uid, String(g.id));
      if (M().lifecycleTerm(g.status) && M().lifecycleTerm(g.status).retired) require("./kernel-lifecycle.js").archive(uid, "migration");
      moved++;
    }
    D.run("DROP TABLE global_products");
    D.run("DELETE FROM meta_lists WHERE name='universeProductTypes'");
  });
  return moved;
}

/* ---------- the permission gate (the "if the Global Platform permits" clause) ---------- */
/* the store's access level on an item, as the console shows it (null: none) */
function permissionFor(tenantId, globalId) {
  const h = MP().storeHolder(tenantId);
  const row = MP().accessOn(globalId).find(a => a.holder === h);
  return row ? { tenant_id: Number(tenantId), global_product_id: String(globalId), permissions: row.level, permission: row.permission } : null;
}
/* may the store list the item: a permission that lets it select the item (an item-scoped one,
   or one over a category, an industry or a universe the item sits in) */
function mayList(tenantId, globalId) {
  const h = MP().storeHolder(tenantId);
  const r = MP().allows(h, M().ROLES.selectAction, globalId);
  if (r.ok) return { ok: true, permission: r.permission };
  const seen = MP().allows(h, M().ROLES.viewAction, globalId);
  return { ok: false, reason: seen.ok ? "Permission is read-only — the platform must let your store list it to import" : "Not permitted by the platform — ask the platform admin to grant this product to your store" };
}

/* ---------- import: a permitted global product → the store's live catalogue ----------
   Idempotent (re-importing refreshes the same row), and traceable: the store row carries
   source_global_id back to the master item. The platform owns the DEFINITION, refreshed on
   every re-import; the store owns its OPERATIONS (stock, ratings, lifecycle, position, its own
   sales copy), seeded once and never rewritten. */
function importToStore(tenantId, globalId) {
  const g0 = find(globalId);
  if (!g0) return { ok: false, error: "unknown global product " + globalId };
  /* the store receives the item as it sees it: the master with the addenda that apply to it */
  const g = project(g0.id, MP().storeHolder(tenantId)) || g0;
  if (g.retired) return { ok: false, error: "this product has been retired on the platform" };
  const gate = mayList(tenantId, g.id);
  if (!gate.ok) return { ok: false, error: gate.reason };
  const t = Number(tenantId);
  const D = db();
  const prof = g.profile, attrs = g.attributes;
  const ex = D.get("SELECT id FROM products WHERE tenant_id=? AND source_global_id=?", t, g.id);
  /* what an imported product starts with where the platform authored nothing (platform policy) */
  const base = require("./security.js").policy().provisioning.importedProduct || {};
  const pid = "GP-" + g.sku.replace(/[^A-Za-z0-9]/g, "").slice(0, 24) + "-" + Math.random().toString(36).slice(2, 6).toUpperCase();
  const def = {
    title: g.name,
    brand: String(prof.brand || base.brand || "").slice(0, 120),
    dept: String(prof.dept || g.category || "").slice(0, 64),
    price: g.price,
    list_price: prof.list != null && prof.list !== "" ? Number(prof.list) : null,
    keywords: String(prof.keywords || (g.name + " " + g.category + " " + g.sku)).toLowerCase().slice(0, 2000),
    flags: String(prof.flags || base.flags || ""),
    emoji: String(prof.emoji || attrs.icon || base.emoji || "").slice(0, 8),
    hue: Number(prof.hue) || Number(base.hue) || 0,
    type: g.type,
    identity: JSON.stringify({ sku: g.sku }),
    attrs: JSON.stringify(attrs),
    media: JSON.stringify(g.media),
    vertical: JSON.stringify(prof.vertical || {}),
    seo: JSON.stringify(prof.seo || {}),
    tax_rule: JSON.stringify(Object.assign({ class: g.tax_class || require("./defaults.js").of("taxClasses") }, prof.tax_rule || {})),
    geo_rules: JSON.stringify(prof.geo_rules || []),
    pricing_rules: JSON.stringify(prof.pricing_rules || {}),
    logistics: JSON.stringify(prof.logistics || {}),
    packaging: JSON.stringify(prof.packaging || []),
    uom: JSON.stringify(prof.uom || {}),
    docs: JSON.stringify(prof.docs || []),
    source_universe: g.universe, source_kind: "global", source_global_id: g.id,
  };
  if (ex) {
    D.run("UPDATE products SET " + Object.keys(def).map(c => c + "=?").join(",") + " WHERE tenant_id=? AND id=?", ...Object.values(def), t, ex.id);
  } else {
    D.run("INSERT INTO products(tenant_id,id,stock,rating,ratings_count,priority,deal_pct,position,lifecycle," + Object.keys(def).join(",") + ") VALUES(?,?,?,?,?,?,?,?,?" + ",?".repeat(Object.keys(def).length) + ")",
      t, pid, Number(base.stock) || 0, Number(base.rating) || 0, 0, 0, 0, 0, base.lifecycle, ...Object.values(def));
    if (g.description) D.run("INSERT OR IGNORE INTO product_bullets(tenant_id,product_id,pos,text) VALUES(?,?,?,?)", t, pid, 0, g.description.slice(0, 300));
  }
  const id = ex ? ex.id : pid;
  if (!D.get("SELECT id FROM skus WHERE tenant_id=? AND product_id=?", t, id)) {
    const r = D.run("INSERT INTO skus(tenant_id,product_id,code,name,identity,variant,price,stock,active) VALUES(?,?,?,?,?,?,?,?,?)",
      t, id, id, "", JSON.stringify({ sku: g.sku }), "{}", g.price, Number(base.stock) || 0, 1);
    const wh = D.get("SELECT id FROM warehouses WHERE tenant_id=? ORDER BY id LIMIT 1", t);
    D.run("INSERT OR IGNORE INTO inventory(tenant_id,sku_id,warehouse_id,qty,reserved) VALUES(?,?,?,?,0)", t, Number(r.lastInsertRowid), wh ? wh.id : null, Number(base.stock) || 0);
  }
  try { require("./search.js").onCatalogChange(t); } catch (e) { }
  return { ok: true, id, updated: !!ex, type: g.type, universe: g.universe };
}

/* what the platform console shows: every global product with the stores permitted to list it */
function globalListWithPermissions(filter) {
  const tenantOf = h => Number(String(h).split(":")[1]);
  return list(filter).map(p => ({ ...p, permissions: MP().accessOn(p.id).filter(a => a.level).map(a => ({ tenant_id: tenantOf(a.holder), global_product_id: p.id, permissions: a.level })) }));
}

module.exports = { seed, universes, universeOf, typeOfUniverse, universeTypes, project, list, find, put, remove,
  permissionFor, mayList, importToStore, globalListWithPermissions };
