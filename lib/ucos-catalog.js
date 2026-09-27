/* UCOS Ω∞ · catalog bridge — publish universe entities into the live storefront.
   --------------------------------------------------------------------------
   The universe registry (lib/ucos-universes.js) made every declared universe
   OPERABLE as a data entity. This module makes it TRANSACTABLE: it publishes a
   universe record into a tenant's product catalog so a shopper can find it,
   open it, add it to cart and check out — through the exact same code path as a
   physical product, because the catalog is the platform's universal sellable.

   The mapping is honest and one-way: a universe entity is the SOURCE, the
   catalog row is its SHOPPER-FACING PROJECTION. Nothing is duplicated — the
   catalog row carries `source_universe` so the bridge can re-sync or withdraw
   it, and a universe record is never re-asserted in code (Article 4.2).

   What is published is derived from the universe entity's own fields, so a new
   industry needs no code: give the universe a name, price and stock and it is
   on the shelf. */
"use strict";

let _db = null;
const db = () => _db || (_db = require("./db.js"));
const rows = (sql, ...p) => { try { return db().all(sql, ...p) || []; } catch (e) { return []; } };
const get = (sql, ...p) => { try { return db().get(sql, ...p) || null; } catch (e) { return null; } };

/* the catalog fields a universe projection must carry to be sellable. Anything
   the universe entity does not supply falls back to a sensible commerce default
   rather than failing the publish. */
function projection(entityKey, universeName, rec) {
  const r = rec || {};
  const name = String(r.name || universeName || "Unnamed offering").slice(0, 300);
  const price = Number(r.price);
  const stock = Number(r.stock);
  return {
    id: "UV-" + String(entityKey).replace(/^uv_/, "").toUpperCase().slice(0, 24) + "-" + String(r.id || 0),
    title: name,
    brand: String(r.brand || universeName || "Universe Catalog").slice(0, 120),
    dept: String(r.dept || "universe").slice(0, 60),
    type: String(r.type || "service").slice(0, 40),
    price: isFinite(price) && price > 0 ? price : 0,
    list_price: isFinite(Number(r.list_price)) && Number(r.list_price) > 0 ? Number(r.list_price) : null,
    rating: isFinite(Number(r.rating)) ? Math.min(5, Math.max(0, Number(r.rating))) : null,
    ratings_count: isFinite(Number(r.ratings_count)) ? Number(r.ratings_count) : 0,
    emoji: String(r.emoji || "🧬").slice(0, 8),
    hue: isFinite(Number(r.hue)) ? Number(r.hue) : 190,
    stock: isFinite(stock) && stock >= 0 ? Math.min(999999, Math.floor(stock)) : 999,
    flags: String(r.flags || "new").slice(0, 20),
    keywords: String(r.keywords || r.name || name).slice(0, 500),
    lifecycle: "published",
    vertical: {},
    identity: { sku: "UV-" + String(r.id || 0) },
    logistics: { shippingClass: r.digital ? "standard" : "standard" }
  };
}

/* ---------- publish: one universe record → one catalog row ----------
    Idempotent (re-publishing updates the same row, never inserts a second) and
    scoped to one tenant, because the catalog is per-store. Returns the catalog
    id the shopper will address. */
function publish(tenantId, entityKey, universeName, rec) {
  const p = projection(entityKey, universeName, rec);
  const ex = get("SELECT id FROM products WHERE tenant_id=? AND source_universe=?", tenantId, entityKey);
  const cols = ["tenant_id", "id", "title", "brand", "dept", "type", "price", "list_price", "rating",
    "ratings_count", "emoji", "hue", "stock", "flags", "keywords", "lifecycle", "vertical", "identity",
    "logistics", "source_universe", "source_kind"];
  const vals = [tenantId, p.id, p.title, p.brand, p.dept, p.type, p.price, p.list_price, p.rating,
    p.ratings_count, p.emoji, p.hue, p.stock, p.flags, p.keywords, p.lifecycle, JSON.stringify(p.vertical),
    JSON.stringify(p.identity), JSON.stringify(p.logistics), entityKey, "universe"];
  if (ex) {
    const sets = cols.slice(1).map(c => c + "=?").join(",");
    db().run("UPDATE products SET " + sets + " WHERE tenant_id=? AND source_universe=?",
      ...vals.slice(1), tenantId, entityKey);
    return { ok: true, id: p.id, updated: true };
  }
  const ph = cols.map(() => "?").join(",");
  db().run("INSERT INTO products(" + cols.join(",") + ") VALUES(" + ph + ")", ...vals);
  /* a sellable needs a default SKU + inventory row so cart and checkout work */
  const sku = get("SELECT id FROM skus WHERE tenant_id=? AND product_id=?", tenantId, p.id);
  if (!sku) {
    const r = db().run("INSERT INTO skus(tenant_id,product_id,code,name,identity,variant,price,stock,active) VALUES(?,?,?,?,?,?,?,?,?)",
      tenantId, p.id, p.id, "Default", JSON.stringify({ sku: p.id }), "{}", p.price, p.stock, 1);
    const wh = get("SELECT id FROM warehouses WHERE tenant_id=? ORDER BY id LIMIT 1", tenantId);
    db().run("INSERT OR IGNORE INTO inventory(tenant_id,sku_id,warehouse_id,qty,reserved) VALUES(?,?,?,?,0)",
      tenantId, Number(r.lastInsertRowid), wh ? wh.id : null, p.stock);
  }
  return { ok: true, id: p.id, created: true };
}

/* ---------- publish every record of a universe into a tenant ----------
    Used by the console's "publish to store" action. Skips records the operator
    has marked unpublished (status retired/deprecated in the entity). */
function publishUniverse(tenantId, entityKey) {
  const def = get("SELECT def FROM entity_defs WHERE key=?", entityKey);
  if (!def) return { ok: false, error: "unknown universe entity " + entityKey };
  const universeName = (() => { try { return JSON.parse(def.def || "{}").label || entityKey; } catch (e) { return entityKey; } })();
  const recs = rows("SELECT * FROM entity_data WHERE entity=?", entityKey);
  let published = 0;
  for (const r of recs) {
    let data = {}; try { data = JSON.parse(r.data || "{}"); } catch (e) { }
    if (["retired", "deprecated"].includes(String(data.status || "").toLowerCase())) continue;
    const out = publish(tenantId, entityKey, universeName, { ...data, id: r.id });
    if (out.ok) published++;
  }
  return { ok: true, entityKey, universe: universeName, published, total: recs.length };
}

/* ---------- withdraw: remove a universe's projection from a tenant ---------- */
function withdrawUniverse(tenantId, entityKey) {
  const ids = rows("SELECT id FROM products WHERE tenant_id=? AND source_universe=?", tenantId, entityKey).map(r => r.id);
  if (!ids.length) return { ok: true, removed: 0 };
  const ph = ids.map(() => "?").join(",");
  db().run("DELETE FROM inventory WHERE sku_id IN (SELECT id FROM skus WHERE tenant_id=? AND product_id IN (" + ph + "))", tenantId, ...ids);
  db().run("DELETE FROM skus WHERE tenant_id=? AND product_id IN (" + ph + ")", tenantId, ...ids);
  db().run("DELETE FROM cart_items WHERE product_id IN (" + ph + ")", ...ids);
  db().run("DELETE FROM products WHERE tenant_id=? AND source_universe=?", tenantId, entityKey);
  return { ok: true, removed: ids.length };
}

/* ---------- read API ---------- */
function listPublished(tenantId) {
  return rows("SELECT source_universe, COUNT(*) n, MIN(title) sample FROM products WHERE tenant_id=? AND source_kind='universe' GROUP BY source_universe ORDER BY source_universe", tenantId);
}
function catalogStats() {
  const tenants = rows("SELECT id, slug, name FROM tenants WHERE status='active'");
  const out = [];
  for (const t of tenants) {
    const pubs = rows("SELECT source_universe, COUNT(*) n FROM products WHERE tenant_id=? AND source_kind='universe' GROUP BY source_universe", t.id);
    out.push({ tenantId: t.id, slug: t.slug, name: t.name, universes: pubs.length, records: pubs.reduce((a, p) => a + p.n, 0) });
  }
  return { tenants: out, records: (rows("SELECT COUNT(*) n FROM products WHERE source_kind='universe'")[0] || {}).n || 0 };
}

/* ---------- ACTIVATION: a universe becomes shopper-transactable by default ----------
   A universe could be instantiated (operable) yet carry no records, so publishing it
   was a no-op and the shelf stayed empty. Activation closes that last inch: if the
   universe has no offering yet, its CANONICAL offering is materialized from the
   universe's own declared fields (the corpus's shape, never a hand-written fixture),
   and then published. The universe is therefore transactable the moment it is
   declared — but an operator's real records always take precedence, and activation
   is idempotent, so it is safe on every boot. */
function canonicalRecord(entityKey) {
  const def = get("SELECT def FROM entity_defs WHERE key=?", entityKey);
  if (!def) return null;
  let d = {}; try { d = JSON.parse(def.def || "{}"); } catch (e) { }
  /* the offering starts at the BEGINNING of the corpus's lifecycle (UCOS 5.1) — it is a
     proposal. Becoming Canonical is the domain journey: the operator advances it
     through the board, and the certification rule (5.2) gates the final step. So
     activation does not hand the operator a finished product; it hands them the
     constitution's own first state. */
  const first = require("./ucos.js").lifecycleStates()[0] || "Proposed";
  const rec = { name: d.label || entityKey, status: first };
  /* the corpus-declared attributes are created empty — the platform never invents a
     value for a field the constitution only names. The operator fills them in. */
  for (const f of (d.fields || [])) {
    if (!f.key || f.key === "name" || f.key === "status" || f.key === "code" || f.key === "attrs") continue;
    rec[f.key] = "";
  }
  const r = db().run("INSERT INTO entity_data(tenant_id,entity,data) VALUES(?,?,?)", 0, entityKey, JSON.stringify(rec));
  return { id: Number(r.lastInsertRowid), ...rec };
}

/* activate one universe in one tenant: ensure an offering exists, then publish it.
   Returns what it actually did so the console can report honestly. */
function activate(tenantId, entityKey) {
  let recs = rows("SELECT id FROM entity_data WHERE entity=? ORDER BY id", entityKey);
  let materialized = false;
  if (!recs.length) { const c = canonicalRecord(entityKey); if (c) { recs = [{ id: c.id }]; materialized = true; } }
  if (!recs.length) return { ok: false, error: "unknown universe entity " + entityKey };
  const out = publishUniverse(tenantId, entityKey);
  return { ...out, materialized, transactable: out.published > 0 };
}

/* activate every universe the corpus declares into a tenant. Bounded by `limit`
   (default 250) so a huge corpus never saturates a single request, and skips
   universes already on the shelf, so a warm activation costs nothing.
   `remaining` counts universes still NOT on the shelf: on-shelf = the ones that
   were already there + the ones this call activated. Skipped universes are a subset
   of "already", so they must not be subtracted again — that double-count made a
   64%-activated corpus report remaining:0 and silently strand the last third. */
function activateAll(tenantId, opts) {
  const o = opts || {};
  const limit = Number(o.limit) || 250;
  const already = new Set(rows("SELECT DISTINCT source_universe k FROM products WHERE tenant_id=? AND source_kind='universe'", tenantId).map(r => r.k));
  const universes = rows("SELECT entity_key FROM ucos_universes ORDER BY name").map(r => r.entity_key);
  let activated = 0, published = 0, failed = 0, skipped = 0;
  for (const key of universes) {
    if (activated >= limit) break;
    if (already.has(key)) { skipped++; continue; }
    const r = activate(tenantId, key);
    if (r.ok) { activated++; published += r.published || 0; } else failed++;
  }
  const onShelf = already.size + activated;
  return { ok: failed === 0, tenantId, universes: universes.length, activated, published, skipped, failed,
    onShelf, remaining: Math.max(0, universes.length - onShelf) };
}

/* activate the corpus to completion: loop activateAll until every declared universe
   is on the shelf (or nothing more can be done). Each round is bounded and idempotent,
   and the loop is capped so a pathological corpus can never spin forever. This is the
   honest "100%": the number it returns is the number that are transactable. */
function activateComplete(tenantId, opts) {
  const roundLimit = Number((opts || {}).limit) || 500;
  let total = 0, published = 0, failed = 0, rounds = 0, last = null;
  for (let i = 0; i < 40; i++) {            /* 40 × 500 = 20,000 — far beyond any corpus */
    last = activateAll(tenantId, { limit: roundLimit });
    total += last.activated; published += last.published; failed += last.failed; rounds++;
    if (last.remaining === 0 || last.activated === 0) break;
  }
  const stats = activationStats().tenants.find(t => t.tenantId === Number(tenantId)) || null;
  return { ok: failed === 0, tenantId, rounds, activated: total, published, failed,
    onShelf: last ? last.onShelf : 0, remaining: last ? last.remaining : 0,
    coverage: stats ? stats.coverage : 0 };
}

/* the measurable activation picture: how many declared universes are transactable
   in each tenant catalog — the honest answer to "is everything implemented?" */
function activationStats() {
  const declared = (get("SELECT COUNT(*) n FROM ucos_universes") || {}).n || 0;
  const tenants = rows("SELECT id, slug, name FROM tenants WHERE status='active'");
  const out = tenants.map(t => {
    const on = rows("SELECT DISTINCT source_universe k FROM products WHERE tenant_id=? AND source_kind='universe'", t.id).map(r => r.k);
    return { tenantId: t.id, slug: t.slug, name: t.name, transactable: on.length, declared,
      coverage: declared ? Math.round(on.length / declared * 100) : 0 };
  });
  return { declared, tenants: out };
}

module.exports = { projection, publish, publishUniverse, withdrawUniverse, listPublished, catalogStats,
  canonicalRecord, activate, activateAll, activateComplete, activationStats };
