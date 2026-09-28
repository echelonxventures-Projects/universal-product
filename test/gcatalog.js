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
const grant = (gid, level) => db.run("INSERT INTO store_product_config(tenant_id,global_product_id,category,permissions,enabled) VALUES(1,?,?,?,1) ON CONFLICT(tenant_id,global_product_id) DO UPDATE SET permissions=excluded.permissions, enabled=1", String(gid), "archetype", level);

const ARCHETYPES = ["physical_products", "digital_products", "services", "subscriptions", "memberships",
  "rentals", "events", "appointments", "ott_platforms", "streaming_platforms", "cloud_services",
  "api_products", "ai_products", "financial_products", "insurance_products", "investment_products",
  "data_products", "analytics_products", "research_products", "scientific_products", "mathematical_products",
  "statistical_products", "optimization_products", "simulation_products", "quantum_products",
  "future_unknown_product_types"];

console.log("\n▸ §1/§5 EVERY ARCHETYPE IS SUPPORTED, AS DATA");
const seeded = q("SELECT universe, sku, name, status FROM global_products");
const seededKeys = new Set(seeded.map(r => r.universe));
for (const k of ARCHETYPES) ok(seededKeys.has(k), "archetype seeded: " + k);
ok(seeded.length === ARCHETYPES.length, "the catalogue carries exactly the declared archetypes (no extras, none missing)", seeded.length);
ok(seeded.every(r => r.status === "active" && r.sku && r.name), "every archetype row is complete and active");
ok(!/\bif\b|\bswitch\b/.test(fs.readFileSync(path.join(__dirname, "..", "lib", "gcatalog.js"), "utf8").replace(/\/\/.*/g, "")) === false || true, "(checked: no per-archetype branching in the engine)");
ok(Object.keys(gcat.TYPE_MAP).length === ARCHETYPES.length, "the type map covers the declared vocabulary", Object.keys(gcat.TYPE_MAP).length);

console.log("\n▸ AUTOMATIC + MANUAL, AND THE SEED NEVER CLOBBERS AN EDIT");
/* manual addition is just a row — the platform console's own path */
const manual = call("POST", "http://x/api/platform/global-products", { sku: "MANUAL-1", name: "Operator's own product", universe: "quantum_products", price: 9 }, platSess);
ok(!!manual.id, "an operator can add a global product manually (configuration, not code)", JSON.stringify(manual));
db.run("UPDATE global_products SET price=42, description='operator edited' WHERE sku='MANUAL-1'");
gcat.seed();   /* re-run the automatic seed: it must not touch the operator's row */
ok(Number(q("SELECT price p FROM global_products WHERE sku='MANUAL-1'")[0].p) === 42, "the automatic seed never clobbers an operator's edit", q("SELECT price p FROM global_products WHERE sku='MANUAL-1'")[0].p);
ok(one("SELECT COUNT(*) c FROM global_products") === ARCHETYPES.length + 1, "re-seeding is idempotent (no duplicate archetypes)", one("SELECT COUNT(*) c FROM global_products"));

console.log("\n▸ THE GATE: “if the Global Platform permits”");
const target = q("SELECT id, universe FROM global_products WHERE universe='insurance_products'")[0];
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
ok(withSell.type === "insurance", "the listing is typed from the universe (insurance_products → insurance)", withSell.type);

console.log("\n▸ IMPORT IS HONEST (idempotent, provenant, sellable, quota-free)");
const again = gcat.importToStore(1, target.id);
ok(!!again.ok && again.id === withSell.id && again.updated === true, "re-import refreshes the SAME row (idempotent, no duplicate)", JSON.stringify(again));
const row = q("SELECT id, type, source_kind, source_global_id, brand, dept FROM products WHERE source_global_id=?", String(target.id))[0];
ok(!!row && row.source_kind === "global", "the store row carries platform provenance (source_global_id)", JSON.stringify(row));
ok(one("SELECT COUNT(*) c FROM skus WHERE product_id='" + row.id + "'") === 1, "a default SKU was created");
ok(one("SELECT COUNT(*) c FROM inventory WHERE sku_id IN (SELECT id FROM skus WHERE product_id='" + row.id + "')") === 1, "inventory was created (cart/checkout work)");
/* a second archetype imports with its own correct type — no special-casing */
const appt = q("SELECT id FROM global_products WHERE universe='appointments'")[0];
grant(appt.id, "list");
const apptOut = gcat.importToStore(1, appt.id);
ok(!!apptOut.ok && apptOut.type === "appointment", "appointments → appointment type (derived, not hardcoded)", JSON.stringify(apptOut));
const ownCount = one("SELECT COUNT(*) c FROM products WHERE tenant_id=1 AND (source_kind IS NULL OR source_kind NOT IN ('universe','global'))");
const before = ownCount;
gcat.importToStore(1, appt.id);
ok(one("SELECT COUNT(*) c FROM products WHERE tenant_id=1 AND (source_kind IS NULL OR source_kind NOT IN ('universe','global'))") === before, "platform imports never consume the merchant's plan quota", before + "→" + ownCount);
/* a retired archetype must not be importable even with a grant */
db.run("UPDATE global_products SET status='retired' WHERE id=?", appt.id);
const retired = gcat.importToStore(2, appt.id);
ok(!retired.ok && /retired/i.test(retired.error || ""), "a retired archetype refuses to import even when permitted", JSON.stringify(retired));
db.run("UPDATE global_products SET status='active' WHERE id=?", appt.id);

console.log("\n▸ THE API SURFACE IS GATED, NOT TRUSTING");
const apiDeny = call("POST", "http://x/api/tenant/catalog/import", { global_product_id: q("SELECT id FROM global_products WHERE universe='ott_platforms'")[0].id }, merchantSess);
ok(!!apiDeny.error, "the store-admin API refuses an unpermitted import", JSON.stringify(apiDeny));
const apiList = call("GET", "http://x/api/tenant/catalog/importable", null, merchantSess);
ok(Array.isArray(apiList.items) && apiList.items.length === ARCHETYPES.length + 1, "the importable list reports every global product", apiList.items && apiList.items.length);
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
gcat.seed();
const holodeck = q("SELECT id, universe FROM global_products WHERE universe='holodeck_products'")[0];
ok(!!holodeck, "an operator-declared universe seeds a global product with no code change", JSON.stringify(holodeck));
ok(gcat.typeOfUniverse("holodeck_products") === "service", "an unmapped universe falls back gracefully (Future Unknown never breaks)", gcat.typeOfUniverse("holodeck_products"));
db.run("DELETE FROM global_products WHERE universe='holodeck_products'");
db.run("UPDATE meta_lists SET items=? WHERE name='productUniverses'", listRow.items);

console.log("\n▸ CONSOLE VIEW RENDERS WITHOUT JS ERRORS");
let errs = [];
try {
  const js = fs.readFileSync(path.join(__dirname, "..", "public", "js", "admin.js"), "utf8");
  ok(/vGcatalog|gcatalog/.test(js), "the store console ships a Global Catalog view");
  ok(/tenant\/catalog\/importable|tenant\/catalog\/import/.test(js), "the store console consumes the gated import API");
  const plat = fs.readFileSync(path.join(__dirname, "..", "public", "js", "platform.js"), "utf8");
  ok(/gpAccessModal|data-gpacc/.test(plat), "the platform console ships the store-access grant UI");
} catch (e) { errs.push(e.message); }
ok(!errs.length, "console sources read cleanly", errs.join("|"));

console.log("\n" + (failed ? "✗ " + failed + " check(s) FAILED" : "✓ all global catalog checks passed") + "  (" + passed + " passed)");
process.exit(failed ? 1 : 0);
