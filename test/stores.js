/* Stores on the kernel (P09): a store is a node of the store kind; the places it serves are a
   relationship of their own, each with a time window, so a store serves a set of places — any
   mix of countries and subdivisions — instead of embedding one country. Its jurisdiction is a
   Party setting naming one of them, and every reader (settings, tax, billing, modules, the
   offer engine's context) answers the store's country from it. */
"use strict";
const path = require("path");
const fs = require("fs");
const os = require("os");
const TMP = path.join(os.tmpdir(), "stores-" + process.pid + ".db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
process.env.LX_DB = TMP;
const silence = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = silence;
const K = require("../lib/kernel.js");
const C = require("../lib/kernel-context.js");
const LC = require("../lib/kernel-lifecycle.js");
const P = require("../lib/places.js");
const S = require("../lib/stores.js");
const settings = require("../lib/settings.js");
const SEED = require("../lib/seed/stores.json");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const threw = fn => { try { fn(); return null; } catch (e) { return e; } };

console.log("stores — every store is on the kernel");
const tenants = db.all("SELECT id, name, uid FROM tenants ORDER BY id");
ok(tenants.length > 0 && tenants.every(t => K.resolveIdentifier(SEED.master.scheme, String(t.id), {})), "every store is a node, known by its store id", tenants.length);
const t1 = tenants[0].id;
const n1 = K.resolveIdentifier(SEED.master.scheme, String(t1), {});
ok(!tenants[0].uid || n1 === String(tenants[0].uid).toLowerCase(), "a store keeps its universal ID as its node's");
ok(tenants.every(t => S.served(t.id).includes(S.jurisdiction(t.id))), "every store serves its jurisdiction");
const colGone = () => !P.hasColumn("country", "tenants");
ok(colGone(), "a fresh install's store row has no country column");
const evs = db.get("SELECT COUNT(*) AS n FROM k_events").n;
const warm = S.importStores();
ok(warm.created === 0 && warm.jurisdictions === 0 && db.get("SELECT COUNT(*) AS n FROM k_events").n === evs, "a warm import writes nothing", warm);

console.log("stores — a store serves a set of places");
const countries = db.all("SELECT code FROM countries WHERE active=1 ORDER BY position").map(r => r.code);
const home = S.jurisdiction(t1);
const other = countries.find(c => c !== home);
const sub = db.get("SELECT code FROM subdivisions WHERE country_code=? LIMIT 1", other);
const beforeServe = new Date().toISOString();
while (new Date().toISOString() === beforeServe) { /* the serve starts after this instant */ }
ok(S.serve(t1, other) === true && S.serve(t1, other) === false, "serving a place is recorded once; again is a no-op");
if (sub) ok(S.serve(t1, sub.code) && S.served(t1).includes(sub.code), "a store serves a subdivision as readily as a country");
ok(S.served(t1).includes(other) && S.served(t1).includes(home), "the store serves its jurisdiction and the places it added", S.served(t1));
ok(!S.served(t1, { at: beforeServe }).includes(other), "what it served before is kept, by time");
ok(S.serving(other).includes(t1), "a place answers which stores serve it");
if (sub) ok(S.serving(other).includes(t1) && S.serving(sub.code).includes(t1), "a store serving a subdivision serves within its country");
const e = threw(() => S.unserve(t1, home));
ok(e && /jurisdiction/.test(e.message) && S.served(t1).includes(home), "a store cannot stop serving its jurisdiction");
ok(S.unserve(t1, other) === true && !S.served(t1).includes(other), "a store stops serving a place");
ok(threw(() => S.serve(t1, "NOWHERE-99")), "a place nobody declared is refused");

console.log("stores — the jurisdiction answers the store's country everywhere");
const next = countries.find(c => c !== home && c !== other);
const cfgBefore = settings.load(t1).commerce.country;
ok(cfgBefore === home, "a store's settings carry its jurisdiction's country", cfgBefore);
settings.save(t1, { commerce: { ...settings.load(t1).commerce, country: next } });
ok(S.jurisdiction(t1) === next && settings.load(t1).commerce.country === next, "saving the store's country moves its jurisdiction on the kernel");
const savedRow = JSON.parse((db.get("SELECT value FROM settings WHERE tenant_id=? AND key='commerce'", t1) || { value: "{}" }).value);
ok(!("country" in savedRow), "and the settings row keeps no copy of it", savedRow.country);
ok(require("../lib/tax.js").configFor(t1).country === next, "the tax engine reads the jurisdiction");
ok(require("../lib/global.js").getTenantCountry(t1) === next, "the global console reads the jurisdiction");
ok(require("../lib/rules.js").platformFacts(t1).country === next, "the applicability rules' country fact is the jurisdiction");
ok(S.served(t1).includes(next) && S.served(t1).includes(home), "a store moving its jurisdiction serves the new place and keeps the old");
ok(C.assignedAt(SEED.jurisdiction.name, { scope: n1 }) === P.byCode(next), "the jurisdiction is a setting at the store's node naming a place");
ok(db.all("SELECT value FROM k_assignments WHERE setting=? AND scope=? AND rec_to IS NOT NULL", SEED.jurisdiction.name, n1).length > 0, "the earlier jurisdiction stays on record");
if (sub) {
  require("../lib/global.js").setTenantCountry(t1, sub.code);
  ok(S.jurisdiction(t1) === sub.code && S.country(t1) === other && settings.load(t1).commerce.country === other, "a jurisdiction may be a subdivision: the store's country is the one it lies in");
}
ok(!require("../lib/global.js").setTenantCountry(t1, "ZZ-NOPE").ok, "a jurisdiction that is no place is refused");

console.log("stores — a store that leaves");
const tNew = Number(db.run("INSERT INTO tenants(slug,name,domain) VALUES('leaver','Leaver','leaver.localhost')").lastInsertRowid);
S.setJurisdiction(tNew, home);
const nNew = K.resolveIdentifier(SEED.master.scheme, String(tNew), {});
S.withdraw(tNew, () => db.run("DELETE FROM tenants WHERE id=?", tNew));
ok(LC.nodeState(nNew) === K.SEED.lifecycle.nodeStates.archived && !S.serving(home).includes(tNew), "a deleted store's node is archived and it no longer serves anything");
ok(K.history(nNew).length > 0 && K.verifyEvents().ok, "its history stays in an intact log");

console.log("stores — an install from before the place tree");
db.run("ALTER TABLE tenants ADD COLUMN country TEXT");
const tOld = Number(db.run("INSERT INTO tenants(slug,name,domain,country) VALUES('oldstore','Old Store','old.localhost',?)", other).lastInsertRowid);
const tSaved = Number(db.run("INSERT INTO tenants(slug,name,domain,country) VALUES('savedstore','Saved Store','saved.localhost',?)", home).lastInsertRowid);
db.run("INSERT INTO settings(tenant_id,key,value) VALUES(?,?,?)", tSaved, "commerce", JSON.stringify({ country: next }));
ok(S.jurisdiction(tOld) === other, "before the import, a store answers what its row said");
const imp = S.importStores();
ok(imp.created === 2 && imp.jurisdictions === 2, "the import brings both stores onto the kernel", imp);
ok(S.jurisdiction(tOld) === other && S.jurisdiction(tSaved) === next, "its jurisdiction is what its storefront showed (saved settings), else its row's column");
db.run("UPDATE tenants SET country=? WHERE id=?", next, tOld);
ok(S.jurisdiction(tOld) === other, "once on the kernel, the legacy column is never read");

for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
