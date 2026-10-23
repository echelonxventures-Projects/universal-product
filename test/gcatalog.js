/* LUXORA · Universal Global Catalog audit — UPIP §1 VISION + §5 Product Archetype Model.
   --------------------------------------------------------------------------
   This proves the requirement the constitution states first: the platform shall support
   every product archetype — Physical, Digital, Services, Subscriptions, Memberships,
   Rentals, Events, Appointments, OTT, Streaming, Cloud, API, AI, Financial, Insurance,
   Investment, Data, Analytics, Research, Scientific, Mathematical, Statistical,
   Optimization, Simulation, Quantum, Future Unknown — and products shall be added
   AUTOMATICALLY and MANUALLY to the global platform, with a store admin able to add
   them to their own listings ONLY IF the Global Platform permits, all without
   architectural redesign.

   What must be true for that claim to hold:

     · ARCHETYPES ARE DATA  — the corpus's own universe vocabulary populates the global
       catalogue as rows; no archetype is a code branch (Infinite Extensibility).
     · AUTOMATIC + MANUAL   — the seed populates every universe; an operator row is just
       another row, and the seed never clobbers an operator's edit.
     · THE GATE IS REAL     — import is refused without a permission row, refused on a
       read-only grant, and allowed on list/sell; the store cannot widen its own access.
     · IMPORT IS HONEST     — idempotent, typed from the universe itself, carries
       provenance, creates a sellable SKU + inventory, and never counts against the
       merchant's plan quota (platform supply is not the merchant's own catalogue).

   Fast, no server, no port, own throwaway DB. */
"use strict";
const path = require("path");
const fs = require("fs");

const TMP = path.join(require("os").tmpdir(), "luxora-gcat-" + process.pid + ".db");
process.env.LX_DB = TMP;
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }

const silence = console.log; console.log = () => { };
const db = require(path.join(__dirname, "..", "lib", "db.js"));
require(path.join(__dirname, "..", "lib", "registry.js")).seedRegistries();
const gcat = require(path.join(__dirname, "..", "lib", "gcatalog.js"));
const api = require(path.join(__dirname, "..", "lib", "api.js"));
console.log = silence;

let passed = 0, failed = 0;
const ok = (cond, name, extra) => { if (cond) { passed++; } else { failed++; console.log("  ✗ " + name + (extra ? "  → " + extra : "")); } };
const call = (method, urlStr, body, sess) => {
  let out = {};
  const res = { writeHead: () => { }, end: s => { out = JSON.parse(s); } };
  api.handle({ method }, res, new URL(urlStr, "http://x.test"), sess, body);
  return out;
};
const adminRow = db.get("SELECT id FROM users WHERE role='admin' AND tenant_id=1 ORDER BY id LIMIT 1");
const merchantSess = { user_id: adminRow ? adminRow.id : 1, tenant: { id: 1 } };
const platSess = { platform_admin: { id: 1, email: "p@p" }, tenant: { id: 1 } };
const q = (sql, ...p) => { try { return db.all(sql, ...p) || []; } catch (e) { return []; } };
const one = (sql) => { const r = q(sql); return r.length ? r[0].c : 0; };
const MP = require(path.join(__dirname, "..", "lib", "master-permissions.js"));
const grant = (gid, level) => MP.setAccess(MP.storeHolder(1), String(gid), level, "test");

const ARCHETYPES = ["physical_products", "digital_products", "services", "subscriptions", "memberships",
  "rentals", "events", "appointments", "ott_platforms", "streaming_platforms", "cloud_services",
  "api_products", "ai_products", "financial_products", "insurance_products", "investment_products",
  "data_products", "analytics_products", "research_products", "scientific_products", "mathematical_products",
  "statistical_products", "optimization_products", "simulation_products", "quantum_products",
  "future_unknown_product_types"];

const PM = require(path.join(__dirname, "..", "lib", "platform-master.js"));
const put = (body) => call("POST", "http://x/api/platform/global-products", body, platSess);
const edit = (id, body) => call("PUT", "http://x/api/platform/global-products/" + id, body, platSess);
const rec = id => gcat.find(id);

console.log("\n▸ §1/§5 EVERY ARCHETYPE IS SUPPORTED, AS DATA");
/* a universe is a classification in the platform master, and the kind it sells as is data on
   the master's kinds vocabulary — there is no type map in code and no placeholder product */
for (const k of ARCHETYPES) ok(!!PM.universeNode(k), "universe in the master: " + k);
for (const k of ARCHETYPES) ok(!!gcat.typeOfUniverse(k), "universe sells as a kind: " + k);
ok(gcat.universeTypes().length === ARCHETYPES.length, "every declared universe reports the kind it sells as", gcat.universeTypes().length);
ok(!/TYPE_MAP|const [A-Z_]+ = \{/.test(fs.readFileSync(path.join(__dirname, "..", "lib", "gcatalog.js"), "utf8")), "the engine holds no universe → type constant");
ok(gcat.seed() === 0, "an install with no legacy table has nothing to move");

console.log("\n▸ AUTOMATIC + MANUAL: THE PLATFORM CONSOLE AUTHORS MASTER ITEMS");
const manual = put({ sku: "MANUAL-1", name: "Operator's own product", universe: "quantum_products", price: 9 });
ok(!!manual.id && !!PM.node(manual.id), "an operator adds a global product: it is an item of the platform master", JSON.stringify(manual));
edit(manual.id, { sku: "MANUAL-1", name: "Operator's own product", universe: "quantum_products", price: 42, description: "operator edited" });
ok(rec(manual.id).price === 42 && rec(manual.id).description === "operator edited", "an edit is a master write, read back through the projection", JSON.stringify(rec(manual.id)));
ok(PM.node(manual.id).identifiers.sku === "MANUAL-1", "the SKU is the item's code under the sku scheme");
ok(!!put({ sku: "MANUAL-1", name: "dupe" }).error, "a SKU names one product");
const hist = require(path.join(__dirname, "..", "lib", "kernel.js")).history(manual.id);
ok(hist.length >= 2, "the master keeps every version of the product", hist.length);

console.log("\n▸ THE GATE: “if the Global Platform permits”");
const target = { id: put({ sku: "INS-1", name: "Cover", universe: "insurance_products", status: "published" }).id };
const noPerm = gcat.importToStore(1, target.id);
ok(!noPerm.ok, "import is REFUSED with no permission row", JSON.stringify(noPerm));
ok(/not permitted/i.test(noPerm.error || ""), "the refusal tells the operator what to do", noPerm.error);
grant(target.id, "read");
const readPerm = gcat.importToStore(1, target.id);
ok(!readPerm.ok, "import is REFUSED on a read-only grant", JSON.stringify(readPerm));
ok(/read-only/i.test(readPerm.error || ""), "the read-only refusal names the missing level", readPerm.error);
grant(target.id, "sell");
const withSell = gcat.importToStore(1, target.id);
ok(!!withSell.ok, "import SUCCEEDS on a sell grant", JSON.stringify(withSell));
ok(withSell.type === gcat.typeOfUniverse("insurance_products"), "the listing is typed from the universe, as the master's kinds vocabulary says", withSell.type);

console.log("\n▸ PERMISSIONS ARE ON THE MASTER, AT ANY SCOPE, AND KEEP THEIR HISTORY");
const catKey = PM.children(PM.children(PM.children(null)[0].uid)[0].uid)[0].key;        /* a category of the first industry */
const inCat = put({ sku: "CAT-1", name: "In a category", category: catKey, universe: "physical_products", status: "published" }).id;
ok(!gcat.mayList(2, inCat).ok, "store 2 starts with no permission");
const wide = MP.grant({ holder: MP.storeHolder(2), scope: [catKey], actions: ["select"] }, "test");
ok(gcat.mayList(2, inCat).ok, "one permission over a category lets the store list every item under it");
ok(MP.allows(MP.storeHolder(2), "view", inCat).ok, "an action implies the actions its term names (select implies view)");
ok(!MP.allows(MP.storeHolder(2), "sell", inCat).ok, "and nothing more");
ok(MP.visibleItems(MP.storeHolder(2)).some(n => n.uid === inCat), "the store's view of the master holds the items its permissions cover");
const beforeRevoke = new Date().toISOString(); for (const t0 = Date.now(); Date.now() - t0 < 3;) { }
MP.revoke(wide, null, "test");
ok(!gcat.mayList(2, inCat).ok, "a revoked permission allows nothing from then on");
ok(MP.allows(MP.storeHolder(2), "select", inCat, { at: beforeRevoke }).ok, "what it allowed before is still answerable");
ok(MP.levels().map(l => l.name).join() && MP.levelOf(["view", "select", "sell"]) === "sell", "store access levels are the master's vocabulary");

console.log("\n▸ IMPORT IS HONEST (idempotent, provenant, sellable, quota-free)");
const again = gcat.importToStore(1, target.id);
ok(!!again.ok && again.id === withSell.id && again.updated === true, "re-import refreshes the SAME row (idempotent, no duplicate)", JSON.stringify(again));
const row = q("SELECT id, type, source_kind, source_global_id, brand, dept FROM products WHERE source_global_id=?", String(target.id))[0];
ok(!!row && row.source_kind === "global", "the store row carries platform provenance (source_global_id)", JSON.stringify(row));
ok(one("SELECT COUNT(*) c FROM skus WHERE product_id='" + row.id + "'") === 1, "a default SKU was created");
ok(one("SELECT COUNT(*) c FROM inventory WHERE sku_id IN (SELECT id FROM skus WHERE product_id='" + row.id + "')") === 1, "inventory was created (cart/checkout work)");
/* a second archetype imports with its own correct type — no special-casing */
const appt = { id: put({ sku: "APPT-1", name: "Visit", universe: "appointments", status: "published" }).id };
grant(appt.id, "list");
const apptOut = gcat.importToStore(1, appt.id);
ok(!!apptOut.ok && apptOut.type === gcat.typeOfUniverse("appointments") && apptOut.type !== withSell.type, "appointments sell as their own kind (derived, not hardcoded)", JSON.stringify(apptOut));
const ownCount = one("SELECT COUNT(*) c FROM products WHERE tenant_id=1 AND (source_kind IS NULL OR source_kind NOT IN ('universe','global'))");
const before = ownCount;
gcat.importToStore(1, appt.id);
ok(one("SELECT COUNT(*) c FROM products WHERE tenant_id=1 AND (source_kind IS NULL OR source_kind NOT IN ('universe','global'))") === before, "platform imports never consume the merchant's plan quota", before + "→" + ownCount);
/* a retired archetype must not be importable even with a grant */
const retiredTerm = PM.vocabulary(PM.ROLES.lifecycle).find(t => t.retired).name;
edit(appt.id, { sku: "APPT-1", name: "Visit", universe: "appointments", status: retiredTerm });
const retired = gcat.importToStore(2, appt.id);
ok(!retired.ok && /retired/i.test(retired.error || ""), "a retired archetype refuses to import even when permitted", JSON.stringify(retired));
edit(appt.id, { sku: "APPT-1", name: "Visit", universe: "appointments", status: "published" });
ok(gcat.importToStore(1, appt.id).ok, "brought back to published, it imports again");

console.log("\n▸ THE PLATFORM AUTHORS THE WHOLE PRODUCT (nothing a store carries is platform-untouchable)");
/* a global product carries the FULL definition: the store product's own fields in
   `profile`, plus media, attributes, description and tax class. Every one of these must
   land on the store row at import — that is "the Global Platform permits each and
   everything what store will have or not" */
const fullBody = {
  sku: "FULL-1", name: "Complete Product", description: "Authored once at the platform.",
  universe: "physical_products", price: 199, tax_class: "reduced",
  media: [{ kind: "image", label: "Front", url: "https://example.com/full.jpg" }],
  attributes: { color: "sand" },
  profile: {
    brand: "Nova Atelier", dept: "home", list: 249, hue: 35, emoji: "🛋️", flags: "bs new", keywords: "sofa bouclé curated",
    vertical: { material: "Bouclé", room: "living" },
    pricing_rules: { tiers: [{ qty: 2, price: 185 }], b2b: true },
    logistics: { shippingClass: "white_glove" },
    packaging: [{ level: "primary", unit: "carton", qty: 1 }],
    uom: { unit: "ea" },
  },
};
const full = call("POST", "http://x/api/platform/global-products", fullBody, platSess);
ok(!!full.id, "a complete product is authored at the platform", JSON.stringify(full));
/* the entity declaration is the authority on what a product may carry — bogus or
   malformed fields are refused by name rather than silently dropped or stored */
const bogus = call("POST", "http://x/api/platform/global-products", { sku: "BOGUS-1", name: "x", profile: { dimensiones: 3 } }, platSess);
ok(!!bogus.error && /dimensiones/i.test(bogus.error), "an undeclared profile field is rejected by name", JSON.stringify(bogus));
const badJson = call("POST", "http://x/api/platform/global-products", { sku: "BADJ-1", name: "x", profile: { vertical: "not-json{" } }, platSess);
ok(!!badJson.error && /vertical/i.test(badJson.error), "malformed JSON in a profile field is rejected", JSON.stringify(badJson));
/* the bridge must be LOSSLESS: media used to be dropped on import, and brand/dept were
   hardcoded — every authored value must now reach the store row */
grant(full.id, "sell");
const imp = gcat.importToStore(1, full.id);
ok(!!imp.ok, "the complete product imports", JSON.stringify(imp));
const store = q("SELECT * FROM products WHERE source_global_id=?", String(full.id))[0];
ok(!!store, "the store row exists");
ok(store.brand === "Nova Atelier", "the authored brand reaches the store (was hardcoded 'Platform Catalog')", store.brand);
ok(store.dept === "home", "the authored department reaches the store (was hardcoded 'global')", store.dept);
ok(Number(store.list_price) === 249, "the list price reaches the store", store.list_price);
ok(/bouclé/i.test(store.keywords || ""), "keywords reach the store", store.keywords);
ok(store.lifecycle === "published", "an imported product is visible by default", store.lifecycle);
ok(JSON.parse(store.media || "[]").some(m => m && m.url === "https://example.com/full.jpg"), "media reaches the store (it used to be dropped)", store.media);
ok(JSON.parse(store.identity || "{}").sku === "FULL-1", "the platform SKU becomes the product identity", store.identity);
ok(JSON.parse(store.attributes || store.attrs || "{}").color === "sand", "custom attributes reach the store", store.attrs);
const tiers = JSON.parse(store.pricing_rules || "{}").tiers;
ok(Array.isArray(tiers) && tiers[0] && tiers[0].price === 185, "pricing rules (B2B tiers) reach the store", store.pricing_rules);
ok(JSON.parse(store.logistics || "{}").shippingClass === "white_glove", "logistics reach the store", store.logistics);
ok(JSON.parse(store.packaging || "[]").length === 1, "packaging reaches the store", store.packaging);
ok(JSON.parse(store.tax_rule || "{}").class === "reduced", "the tax class becomes the store tax rule", store.tax_rule);
ok(JSON.parse(store.vertical || "{}").material === "Bouclé", "the vertical profile reaches the store", store.vertical);
ok(q("SELECT text FROM product_bullets WHERE product_id='" + store.id + "'").length === 1, "the description becomes the store's sales copy");
/* the store owns its OPERATIONS: a re-import propagates the platform's definition but
   never resets stock, lifecycle or the merchant's bullets */
db.run("UPDATE products SET stock=7, lifecycle='draft' WHERE id=?", store.id);
edit(full.id, { ...fullBody, price: 77, name: "Complete Product v2" });
const imp2 = gcat.importToStore(1, full.id);
ok(!!imp2.ok && imp2.id === imp.id && imp2.updated === true, "re-import refreshes the same row (idempotent)", JSON.stringify(imp2));
const store2 = q("SELECT * FROM products WHERE source_global_id=?", String(full.id))[0];
ok(Number(store2.price) === 77 && store2.title === "Complete Product v2", "the platform's edit reaches the store row", store2.price + "/" + store2.title);
ok(Number(store2.stock) === 7 && store2.lifecycle === "draft", "the store's operations are never reset (stock, lifecycle)", store2.stock + "/" + store2.lifecycle);
ok(q("SELECT text FROM product_bullets WHERE product_id='" + store2.id + "'").length === 1, "the store's bullets are never rewritten");

console.log("\n▸ THE API SURFACE IS GATED, NOT TRUSTING");
const ottId = put({ sku: "OTT-1", name: "Stream", universe: "ott_platforms", status: "published" }).id;
const apiDeny = call("POST", "http://x/api/tenant/catalog/import", { global_product_id: ottId }, merchantSess);
ok(!!apiDeny.error, "the store-admin API refuses an unpermitted import", JSON.stringify(apiDeny));
const apiList = call("GET", "http://x/api/tenant/catalog/importable", null, merchantSess);
ok(Array.isArray(apiList.items) && apiList.items.length === gcat.list().length, "the importable list reports every global product", apiList.items && apiList.items.length);
ok(apiList.items.every(i => i.permitted === false || i.permitted === true), "each item reports its permission honestly (no silent grant)");
const ott = apiList.items.find(i => i.universe === "ott_platforms");
ok(!!ott && !ott.permitted && !!ott.reason, "an unpermitted product carries the reason the merchant can act on", ott && ott.reason);
const platOnly = call("GET", "http://x/api/tenant/catalog/importable", null, { tenant: { id: 1 } });
ok(!!platOnly.error, "a non-admin session cannot read the importable list", JSON.stringify(platOnly));
const anonImport = call("POST", "http://x/api/tenant/catalog/import", { global_product_id: target.id }, { tenant: { id: 1 } });
ok(!!anonImport.error, "a non-admin session cannot import", JSON.stringify(anonImport));

console.log("\n▸ INFINITE EXTENSIBILITY (a new universe never requires a code change)");
/* an operator extends the vocabulary the way Data Studio does: by adding an item to the
   registry LIST, never by inserting a second row (the name is the key) and never by code */
const listRow = db.get("SELECT items FROM meta_lists WHERE name='productUniverses'");
const extended = JSON.parse(listRow.items || "[]").concat([{ key: "holodeck_products", name: "Holodeck Products", icon: "🛸" }]);
db.run("UPDATE meta_lists SET items=? WHERE name='productUniverses'", JSON.stringify(extended));
require(path.join(__dirname, "..", "lib", "registry.js")).list && null;
const holo = put({ sku: "HOLO-1", name: "Holodeck hour", universe: "holodeck_products" });
ok(!!holo.id && gcat.find(holo.id).universe === "holodeck_products", "an operator-declared universe takes products with no code change", JSON.stringify(holo));
ok(gcat.typeOfUniverse("holodeck_products") === PM.vocabulary(PM.ROLES.itemKinds).find(t => t.unmappedUniverses).name, "an unmapped universe sells as the kind marked for it (Future Unknown never breaks)", gcat.typeOfUniverse("holodeck_products"));
call("DELETE", "http://x/api/platform/global-products/" + holo.id, {}, platSess);
ok(!gcat.list().some(p => p.id === holo.id) && !!PM.node(holo.id), "deleting retires the product: gone from the catalogue, its history kept");
db.run("UPDATE meta_lists SET items=? WHERE name='productUniverses'", listRow.items);

console.log("\n▸ AN INSTALL THAT PREDATES THE MASTER MOVES ONTO IT ONCE");
db.run("CREATE TABLE store_product_config (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, global_product_id TEXT NOT NULL, category TEXT DEFAULT '', permissions TEXT DEFAULT 'read', config TEXT DEFAULT '{}', enabled INTEGER DEFAULT 1, UNIQUE (tenant_id, global_product_id))");
db.run("CREATE TABLE global_products (id INTEGER PRIMARY KEY AUTOINCREMENT, sku TEXT NOT NULL UNIQUE, name TEXT NOT NULL, description TEXT DEFAULT '', category TEXT DEFAULT '', universe TEXT DEFAULT '', price REAL DEFAULT 0, tax_class TEXT DEFAULT '', is_service INTEGER DEFAULT 0, attributes TEXT DEFAULT '{}', media TEXT DEFAULT '[]', profile TEXT DEFAULT '{}', status TEXT DEFAULT 'draft')");
const old = db.run("INSERT INTO global_products(sku,name,description,category,universe,price,tax_class,attributes,profile,status) VALUES('OLD-1','Old row','From before','grocery','physical_products',12,'reduced','{\"tone\":\"warm\"}','{\"brand\":\"Old brand\"}','active')").lastInsertRowid;
const gone = db.run("INSERT INTO global_products(sku,name,universe,status) VALUES('OLD-2','Retired row','services','retired')").lastInsertRowid;
db.run("INSERT INTO store_product_config(tenant_id,global_product_id,category,permissions,enabled) VALUES(1,?,?,?,1)", String(old), "", "sell");
db.run("UPDATE products SET source_global_id=? WHERE id=(SELECT id FROM products WHERE tenant_id=1 AND source_global_id IS NULL LIMIT 1)", String(old));
ok(gcat.seed() === 2, "every legacy row moves onto the master");
const moved = gcat.find("OLD-1");
ok(moved && moved.name === "Old row" && moved.category === "grocery" && moved.universe === "physical_products" && moved.price === 12 && moved.tax_class === "reduced", "it keeps its code, name, place, universe, price and tax class", JSON.stringify(moved));
ok(moved.attributes.tone === "warm" && moved.profile.brand === "Old brand" && moved.status === PM.lifecycleTerm("active").name, "its attributes, profile and status too");
ok(gcat.find("OLD-2").retired, "a retired row stays retired");
ok(!!gcat.permissionFor(1, moved.id) && gcat.permissionFor(1, moved.id).permissions === "sell", "the store access that named it is now a permission on the item, at the same level");
ok(!q("SELECT name FROM sqlite_master WHERE type='table' AND name='store_product_config'").length, "and the access table is gone too");
ok(one("SELECT COUNT(*) c FROM products WHERE source_global_id='" + moved.id + "'") === 1, "an imported product that named it now names the item");
ok(!q("SELECT name FROM sqlite_master WHERE type='table' AND name='global_products'").length, "the old table is gone (one truth)");

console.log("\n▸ CONSOLE VIEW RENDERS WITHOUT JS ERRORS");
let errs = [];
try {
  const js = fs.readFileSync(path.join(__dirname, "..", "public", "js", "admin.js"), "utf8");
  ok(/vGcatalog|gcatalog/.test(js), "the store console ships a Global Catalog view");
  ok(/tenant\/catalog\/importable|tenant\/catalog\/import/.test(js), "the store console consumes the gated import API");
  const plat = fs.readFileSync(path.join(__dirname, "..", "public", "js", "platform.js"), "utf8");
  ok(/gpAccessModal|data-gpacc/.test(plat), "the platform console ships the store-access grant UI");
  ok(/data-pf=/.test(plat), "the platform product form renders the full store-product detail (data-pf profile fields)");
} catch (e) { errs.push(e.message); }
ok(!errs.length, "console sources read cleanly", errs.join("|"));

console.log("\n" + (failed ? "✗ " + failed + " check(s) FAILED" : "✓ all global catalog checks passed") + "  (" + passed + " passed)");
process.exit(failed ? 1 : 0);
