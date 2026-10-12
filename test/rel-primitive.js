/* relationship primitive regression: the typed store owns the edge; the product
   table is a derived projection, written first from the primitive and withdrawn
   with it. Fast, no server, throwaway DB. */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os");
const TMP = path.join(os.tmpdir(), "luxora-rel-" + process.pid + ".db");
process.env.LX_DB = TMP;
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
const silence = console.log; console.log = () => { };
const db = require(path.join(__dirname, "..", "lib", "db.js"));
const registry = require(path.join(__dirname, "..", "lib", "registry.js"));
require(path.join(__dirname, "..", "lib", "registry.js")).seedRegistries();
console.log = silence;

let passed = 0, failed = 0;
const ok = (c, n, x) => { if (c) passed++; else { failed++; console.log("  ✗ " + n + (x ? " → " + x : "")); } };
const one = (sql, ...p) => { try { const r = db.all(sql, ...p) || []; return r.length ? r[0] : null; } catch (e) { return null; } };
const has = (sql, ...p) => !!one(sql, ...p);

const tid = (one("SELECT id FROM tenants WHERE slug='luxora'") || {}).id;
ok(tid != null, "a tenant exists to own product edges");

const seedRels = db.all("SELECT * FROM relationships").length;
const seedLinks = db.all("SELECT * FROM links WHERE from_entity='product' AND to_entity='product'").length;
ok(seedRels > 0, "the seed materialised product relationship rows", seedRels);
ok(seedLinks > 0, "the seed wrote the PRIMITIVE edges (not just the projection)", seedLinks);

const pByUid = new Map(db.all("SELECT uid, id, tenant_id FROM products WHERE uid IS NOT NULL").map(r => [r.uid, r]));
let unbacked = 0;
for (const r of db.all("SELECT * FROM relationships")) {
  const f = [...pByUid.values()].find(p => p.tenant_id === r.tenant_id && p.id === r.from_id);
  const t = [...pByUid.values()].find(p => p.tenant_id === r.tenant_id && p.id === r.to_id);
  if (!f || !t) { unbacked++; continue; }
  if (!has("SELECT 1 FROM links WHERE type=? AND from_uid=? AND to_uid=?", r.type, f.uid, t.uid)) unbacked++;
}
ok(unbacked === 0, "every projection row is backed by a primitive edge", unbacked + " unbacked");

const before = db.all("SELECT * FROM relationships").length;
const r1 = registry.reconcileLinks();
const after = db.all("SELECT * FROM relationships").length;
ok(after === before, "reconciling a warm DB adds no projection rows", before + " -> " + after);
ok(r1.inserted === 0, "reconcile reports zero inserts on a warm DB", JSON.stringify(r1));

const A = "VR-FURN-01", B = "VR-HARD-01";
const uidA = (one("SELECT uid FROM products WHERE tenant_id=? AND id=?", tid, A) || {}).uid;
const uidB = (one("SELECT uid FROM products WHERE tenant_id=? AND id=?", tid, B) || {}).uid;
ok(!!uidA && !!uidB, "both products have universal ids");
db.addLink(tid, "compatible", "product", uidA, "product", uidB, { via: "test" });
ok(has("SELECT 1 FROM links WHERE type='compatible' AND from_uid=? AND to_uid=?", uidA, uidB), "the edge was written to the PRIMITIVE");
ok(!has("SELECT 1 FROM relationships WHERE tenant_id=? AND from_id=? AND to_id=? AND type='compatible'", tid, A, B), "the projection does not yet exist (derive-on-demand)");
const r2 = registry.reconcileLinks();
ok(has("SELECT 1 FROM relationships WHERE tenant_id=? AND from_id=? AND to_id=? AND type='compatible'", tid, A, B), "reconcile derived the projection from the primitive");
ok(r2.inserted >= 1, "reconcile reports the insert", JSON.stringify(r2));

db.run("DELETE FROM links WHERE type='compatible' AND from_uid=? AND to_uid=?", uidA, uidB);
const r3 = registry.reconcileLinks();
ok(!has("SELECT 1 FROM relationships WHERE tenant_id=? AND from_id=? AND to_id=? AND type='compatible'", tid, A, B), "deleting the primitive withdrew the projection");
ok(r3.withdrawn >= 1, "reconcile reports the withdrawal", JSON.stringify(r3));

const goipBefore = db.all("SELECT * FROM links WHERE NOT (from_entity='product' AND to_entity='product')").length;
registry.reconcileLinks();
const goipAfter = db.all("SELECT * FROM links WHERE NOT (from_entity='product' AND to_entity='product')").length;
ok(goipBefore === goipAfter, "non-product edges (GOIP attribution graph) are untouched", goipBefore + " -> " + goipAfter);

const entity = require(path.join(__dirname, "..", "lib", "entity.js"));
const def = entity.allEntities(0).link;
ok(!!def, "the link primitive is a registered entity");
ok(def && def.noTenant && def.platformOnly, "it is platform-level master data — no store scoping", def && JSON.stringify({ noTenant: def.noTenant, platformOnly: def.platformOnly }));
ok(def && def.table === "links", "it is backed by the typed links table", def && def.table);

console.log("\n" + (failed ? "✗ " + failed + " FAILED, " + passed + " passed" : "✓ ALL GREEN — " + passed + " passed, 0 failed"));
if (failed) process.exitCode = 1;
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
