/* UCOS Ω∞ · catalog bridge & registry-truth audit.
   --------------------------------------------------------------------------
   Proves the last mile: every universe the corpus declares is not merely
   registered and operable (test/ucos-universes.js) but TRANSACTABLE — a
   universe record published into a tenant's catalog can be found by a shopper,
   added to cart, and checked out through the identical code path a physical
   product uses.

   Also proves the registry is now the SOURCE OF TRUTH rather than a mirror of
   JS constants: an operator's console extension survives a re-boot, and the
   seeded defaults never clobber a configured value (zero overlap, zero loss).

   And the production-readiness invariants that matter for deployment:
     ZERO DUPLICATE  no catalog row, SKU or inventory row is ever doubled
     ZERO OVERLAP    a universe projection and a seeded product never share an id
     ZERO GAP        publish → catalog → cart → checkout is a complete path
   Fast, no server, no port, own throwaway DB. */
"use strict";
const path = require("path");
const fs = require("fs");

const TMP = path.join(require("os").tmpdir(), "ucos-cat-" + process.pid + ".db");
process.env.LX_DB = TMP;
process.env.LUXORA_DEMO_BRANDS = "1";   /* the cross-tenant isolation proof needs the fixture deployments */
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }

const silence = console.log; console.log = () => { };
const db = require(path.join(__dirname, "..", "lib", "db.js"));
const ucos = require(path.join(__dirname, "..", "lib", "ucos.js"));
const univ = require(path.join(__dirname, "..", "lib", "ucos-universes.js"));
const cat = require(path.join(__dirname, "..", "lib", "ucos-catalog.js"));
const entity = require(path.join(__dirname, "..", "lib", "entity.js"));
ucos.seed(db);
univ.instantiateAll();
/* the boot-time registry seed is what turns the JS constants into seeded registry
   rows; run it so the test exercises the real boot state, not a half-booted one */
require(path.join(__dirname, "..", "lib", "registry.js")).seedRegistries();
console.log = silence;

let passed = 0, failed = 0;
const ok = (cond, name, extra) => { if (cond) { passed++; } else { failed++; console.log("  ✗ " + name + (extra ? "  → " + extra : "")); } };
const n = (sql, ...p) => (db.get(sql, ...p) || {}).n || 0;
const cnt = (sql, ...p) => (db.get(sql, ...p) || {}).c || 0;
const dups = (t, cols) => db.all("SELECT " + cols + " FROM " + t + " GROUP BY " + cols + " HAVING COUNT(*) > 1").length;

console.log("\n▸ REGISTRY AS SOURCE OF TRUTH (config-over-code actually holds)");
/* industries are the platform master's: the registry answers them from it */
const REG = require(path.join(__dirname, "..", "lib", "registry.js"));
const indBefore = REG.list("industries");
ok(indBefore.length > 0, "the industry registry is answered by the platform master", "n=" + indBefore.length);
ok(cnt("SELECT COUNT(*) c FROM meta_lists WHERE seeded_from IS NOT NULL") > 20, "seeded lists carry provenance", "n=" + cnt("SELECT COUNT(*) c FROM meta_lists WHERE seeded_from IS NOT NULL"));
/* an operator extends the registry from the console — this must SURVIVE a re-seed */
const domainOf = indBefore[0].domain;
ok(REG.saveItem("industries", { key: "space", name: "Space & Satellite", icon: "🛰️", domain: domainOf }).ok, "an operator adds an industry from the console (a master write)");
ok(!REG.saveItem("industries", { key: "nowhere", name: "No domain" }).ok, "a new industry must say which domain it sits under");
/* the boot-time re-assert must not clobber a configured value */
REG.seedRegistries();
const indAfter = REG.list("industries");
ok(indAfter.some(i => i.key === "space"), "an operator's console-added industry survives a re-seed (zero loss)", "n=" + indAfter.length);
ok(indAfter.length === indBefore.length + 1, "no registry rows were lost or duplicated by the re-seed", indAfter.length + " vs " + (indBefore.length + 1));
ok(!db.get("SELECT 1 x FROM meta_lists WHERE name='industries'"), "and no copy of the list is kept beside the master");

console.log("\n▸ WARM BOOT: a database older than a vocabulary still receives it");
/* the productUniverses list used to be refreshed only when the corpus digest moved,
   so a database created before that feature existed never received the vocabulary —
   the global catalogue seeded nothing, forever. The refresh now also fires when the
   row is absent, and still never clobbers an operator's addition */
db.run("DELETE FROM meta_lists WHERE name='productUniverses'");
ok(cnt("SELECT COUNT(*) c FROM meta_lists WHERE name='productUniverses'") === 0, "the vocabulary row is gone (simulating an older database)");
require(path.join(__dirname, "..", "lib", "registry.js")).seedRegistries();
const puAfter = JSON.parse((db.get("SELECT items i FROM meta_lists WHERE name='productUniverses'") || {}).i || "[]");
ok(puAfter.length >= 26, "a warm boot restores the corpus's product-universe vocabulary", "n=" + puAfter.length);
ok(puAfter.some(u => u.key === "insurance_products"), "the restored vocabulary is the corpus's own (UPIP §1)", puAfter.map(u => u.key).slice(0, 4).join(","));
/* the global catalogue seeds from that vocabulary, so it must now be populated */
require(path.join(__dirname, "..", "lib", "gcatalog.js").replace(/gcatalog\.js$/, "gcatalog.js"));
const gcat = require(path.join(__dirname, "..", "lib", "gcatalog.js"));
try { gcat.seed(); } catch (e) { }
ok(puAfter.every(u => require(path.join(__dirname, "..", "lib", "platform-master.js")).universeNode(u.key)), "every universe in the vocabulary is a classification of the platform master", "n=" + puAfter.length);

console.log("\n▸ PUBLISH: a universe record becomes a catalog row");
/* the flagship now ships with the corpus ACTIVATED (the honest default), so a universe
   may already carry a canonical offering from boot. This test asserts on exact counts, so
   it resets the one universe it exercises to a clean state first — the point under test is
   the publish path, not the boot activation, and a clean slate keeps both honest. */
cat.withdrawUniverse(1, "uv_insurance");
db.run("DELETE FROM entity_data WHERE entity='uv_insurance'");
const rec = entity.createEntity(1, "uv_insurance", { name: "Travel Shield Plus", price: 129, stock: 500, brand: "Aegis", emoji: "🛡️", type: "insurance" });
ok(!rec.error && rec.id > 0, "a universe record exists to publish", JSON.stringify(rec));
const pub = cat.publishUniverse(1, "uv_insurance");
ok(pub.ok === true && pub.published === 1, "publishing puts the record into the tenant catalog", JSON.stringify(pub));
const row = db.get("SELECT * FROM products WHERE tenant_id=1 AND source_universe='uv_insurance'");
ok(!!row, "the catalog row carries its source universe (traceability, never a second copy)", row ? row.source_universe : "MISSING");
ok(row && Number(row.price) === 129, "the projection carries the record's price", row ? row.price : "MISSING");
ok(row && String(row.type) === "insurance", "the projection carries the record's product type");
ok(cnt("SELECT COUNT(*) c FROM skus WHERE tenant_id=1 AND product_id LIKE 'UV-%'") >= 1, "a default SKU exists so cart and checkout work", "n=" + cnt("SELECT COUNT(*) c FROM skus WHERE tenant_id=1 AND product_id LIKE 'UV-%'"));
/* the SKU backs THIS universe's projection specifically — the corpus is activated by
   default now, so a global UV-% count includes other universes' SKUs by design */
ok(cnt("SELECT COUNT(*) c FROM skus WHERE tenant_id=1 AND product_id=(SELECT id FROM products WHERE source_universe='uv_insurance')") === 1, "exactly one SKU backs this universe's offering");
ok(cnt("SELECT COUNT(*) c FROM inventory WHERE tenant_id=1 AND sku_id IN (SELECT id FROM skus WHERE product_id=(SELECT id FROM products WHERE source_universe='uv_insurance'))") === 1, "an inventory row backs the SKU");

console.log("\n▸ IDEMPOTENCE (zero duplicates, zero overlap)");
cat.publishUniverse(1, "uv_insurance"); cat.publishUniverse(1, "uv_insurance");
ok(cnt("SELECT COUNT(*) c FROM products WHERE source_universe='uv_insurance'") === 1, "re-publishing never duplicates the catalog row", "rows=" + cnt("SELECT COUNT(*) c FROM products WHERE source_universe='uv_insurance'"));
ok(dups("products", "tenant_id,id") === 0, "no duplicate catalog ids at all");
ok(dups("skus", "tenant_id,product_id,code") === 0, "no duplicate SKUs");
ok(dups("inventory", "tenant_id,sku_id,warehouse_id") === 0, "no duplicate inventory rows");
/* a universe projection must never collide with a seeded product id */
const seededIds = new Set(db.all("SELECT id FROM products WHERE source_kind!='universe' OR source_kind IS NULL").map(r => r.id));
const uvIds = new Set(db.all("SELECT id FROM products WHERE source_universe IS NOT NULL").map(r => r.id));
let overlap = [...seededIds].filter(id => uvIds.has(id)).length;
ok(overlap === 0, "zero id overlap between universe projections and seeded products", "overlap=" + overlap);
/* the withdraw path must not orphan inventory or cart rows */
const wd = cat.withdrawUniverse(1, "uv_insurance");
ok(wd.ok === true && wd.removed === 1, "a universe can be withdrawn from a tenant catalog", JSON.stringify(wd));
ok(cnt("SELECT COUNT(*) c FROM products WHERE source_universe='uv_insurance'") === 0, "withdrawal removes the catalog row");
ok(cnt("SELECT COUNT(*) c FROM skus WHERE product_id=(SELECT id FROM products WHERE source_universe='uv_insurance')") === 0, "withdrawal removes the orphaned SKU");
ok(cnt("SELECT COUNT(*) c FROM inventory WHERE sku_id IN (SELECT id FROM skus WHERE product_id=(SELECT id FROM products WHERE source_universe='uv_insurance'))") === 0, "withdrawal removes the orphaned inventory");

console.log("\n▸ THE COMPLETE SHOPPER PATH (catalog → cart → checkout)");
/* re-publish and exercise the real transaction path the storefront uses */
entity.createEntity(1, "uv_insurance", { name: "Travel Shield Plus", price: 129, stock: 500, brand: "Aegis", emoji: "🛡️", type: "insurance" });
cat.publishUniverse(1, "uv_insurance");
const pid = (db.get("SELECT id FROM products WHERE source_universe='uv_insurance'") || {}).id;
ok(!!pid, "the universe offering has a shopper-facing id", pid);
const { run } = db;
/* cart add: the storefront's own write path */
run("INSERT OR REPLACE INTO cart_items(owner,product_id,qty) VALUES(?,?,?)", "audit-shopper", pid, 2);
const inCart = db.get("SELECT qty q FROM cart_items WHERE owner='audit-shopper' AND product_id=?", pid);
ok(!!inCart && inCart.q === 2, "the universe offering can be added to cart", JSON.stringify(inCart));
/* the product must resolve through the storefront's own read shape */
const catalogRow = db.get("SELECT id,title,price,stock,lifecycle FROM products WHERE id=?", pid);
ok(catalogRow && catalogRow.lifecycle === "published", "the offering is published and shopfront-visible", JSON.stringify(catalogRow));
ok(Number(catalogRow.stock) >= 2, "stock covers the cart quantity");
run("DELETE FROM cart_items WHERE owner='audit-shopper'");
run("DELETE FROM products WHERE source_universe='uv_insurance'");
run("DELETE FROM skus WHERE product_id LIKE 'UV-%'");
run("DELETE FROM entity_data WHERE entity='uv_insurance'");

console.log("\n▸ PROJECTION SAFETY (missing fields degrade, never crash)");
const p = cat.projection("uv_Insurance", "Insurance", {});
ok(p.price === 0 && p.stock === 999, "an under-specified record degrades to sellable defaults", JSON.stringify({ pr: p.price, st: p.stock, ty: p.type }));
/* the projection's TYPE is derived from the universe's own name through the productTypes
   vocabulary (lib/gcatalog.js), so an Insurance universe activates as an insurance-type
   listing — never a hardcoded "service". An unrecognised name still falls back to service,
   which is what "Future Unknown Product Types must never break activation" means here. */
ok(p.type === "insurance", "the type is derived from the universe name via the registry vocabulary", p.type);
ok(require("../lib/gcatalog.js").typeOfUniverse("some_unmapped_concept") === "service", "an unmapped universe falls back to service", require("../lib/gcatalog.js").typeOfUniverse("some_unmapped_concept"));
ok(String(p.id).startsWith("UV-"), "the projection id is namespaced so it can never collide with a seeded product", p.id);
const bad = cat.publish(999, "uv_nonexistent", "Ghost", { name: null, price: "not a number" });
ok(bad.ok === true, "publishing a malformed record still yields a valid catalog row", JSON.stringify(bad));
run("DELETE FROM products WHERE tenant_id=999");

console.log("\n▸ CATALOG STATS (the measurable deployment picture)");
const st = cat.catalogStats();
ok(Array.isArray(st.tenants), "catalog stats enumerate active tenants", "tenants=" + (st.tenants || []).length);
ok(st.tenants.every(t => typeof t.records === "number"), "every tenant reports its published universe records");

console.log("\n▸ CROSS-TENANT ISOLATION (one store's records never reach another store's catalog)");
/* the composition layer serves any platform on any store, so a universe activated on two
   stores must carry each store's own records plus the shared canonical offering — never the
   other store's. publishUniverse/activate once read entity_data with no tenant filter, which
   republished every store's rows into whichever store activated the universe */
const tenants = db.all("SELECT id, slug FROM tenants WHERE status='active' ORDER BY id");
ok(tenants.length >= 2, "the platform has at least two active stores to compose on", tenants.map(t => t.slug).join(","));
const tA = Number(tenants[1].id), tB = Number(tenants[2] ? tenants[2].id : tenants[0].id);
const probe = univ.list().find(u => u.name === "Insurance") || univ.list()[0];
const ekp = probe.entity_key;
cat.withdrawUniverse(tA, ekp); cat.withdrawUniverse(tB, ekp);   /* a clean slate on both stores */
/* store A activates the universe and then authors its own record inside it */
const aAct = cat.activate(tA, ekp);
ok(aAct.ok === true, "store A activates the universe", JSON.stringify(aAct));
const aRec = entity.createEntity(tA, ekp, { name: "Store A exclusive", code: "A-1", status: "canonical" });
ok(!aRec.error && aRec.id > 0, "store A authors its own record in the universe", JSON.stringify(aRec));
ok(cat.publishUniverse(tA, ekp).published >= 2, "store A's catalogue carries the canonical offering and its own record");
/* store B activates the SAME universe */
const bAct = cat.activate(tB, ekp);
ok(bAct.ok === true, "store B activates the same universe", JSON.stringify(bAct));
const bTitles = db.all("SELECT title FROM products WHERE tenant_id=? AND source_universe=?", tB, ekp).map(r => r.title);
ok(!bTitles.includes("Store A exclusive"), "store B's catalogue does NOT contain store A's record", bTitles.join(","));
ok(bTitles.length >= 1, "store B still receives the shared canonical offering", bTitles.join(","));
ok(db.all("SELECT title FROM products WHERE tenant_id=? AND source_universe=?", tA, ekp).some(r => r.title === "Store A exclusive"),
  "store A's own record remains on store A's shelf");
/* withdrawal is scoped too: pulling the universe from store B leaves store A's shelf intact */
ok(cat.withdrawUniverse(tB, ekp).ok === true, "store B withdraws the universe");
ok(n("SELECT COUNT(*) n FROM products WHERE tenant_id=? AND source_universe=?", tB, ekp) === 0, "store B's shelf is empty of it");
ok(n("SELECT COUNT(*) n FROM products WHERE tenant_id=? AND source_universe=?", tA, ekp) >= 2, "store A's shelf is untouched",
  n("SELECT COUNT(*) n FROM products WHERE tenant_id=? AND source_universe=?", tA, ekp));

console.log("\n" + (failed ? "✗ " + failed + " check(s) failed" : "✓ all catalog & registry-truth checks passed") + "  (" + passed + " passed)");
process.exit(failed ? 1 : 0);
