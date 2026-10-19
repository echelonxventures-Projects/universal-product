/* Places on the kernel (P09): every country and subdivision is a node of the place kind in one
   place tree, with its code as an identifier and its row's universal ID as its own. Every write —
   seeding, repair, console, global.js — goes to the kernel first, in the same transaction as the
   row: a rename is a new version with the old one kept, a switched-off country is hidden, a
   re-parented subdivision moves, a deleted one is archived. The boot pass only imports rows the
   kernel has never seen; a warm pass writes nothing. Nothing is invented above the countries. */
"use strict";
const path = require("path");
const fs = require("fs");
const os = require("os");
const TMP = path.join(os.tmpdir(), "places-" + process.pid + ".db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
process.env.LX_DB = TMP;
const silence = console.log; console.log = () => { };
const db = require("../lib/db.js");
require("../lib/registry.js");
console.log = silence;
const K = require("../lib/kernel.js");
const LC = require("../lib/kernel-lifecycle.js");
const P = require("../lib/places.js");
const globalmod = require("../lib/global.js");
const entity = require("../lib/entity.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };

console.log("places — the master is on the kernel");
const countries = db.all("SELECT code, name, uid, active FROM countries");
const subs = db.all("SELECT rowid AS id, code, country_code, parent_id, name FROM subdivisions");
const placeNodes = K.nodes("place", "platform", { includeHidden: true });
ok(placeNodes.length === countries.length + subs.length, "one node per country and per subdivision", { nodes: placeNodes.length, rows: countries.length + subs.length });
ok(countries.every(c => P.country(c.code)), "every country resolves by its code");
ok(subs.every(s => P.subdivision(s.code)), "every subdivision resolves by its code");
const withUid = countries.filter(c => /^[0-9a-f-]{36}$/i.test(c.uid || ""));
ok(withUid.length > 0 && withUid.every(c => P.country(c.code) === c.uid.toLowerCase()), "a country keeps its universal ID as its node's");
const tops = K.children(P.HIERARCHY, null, { includeHidden: true });
ok(tops.length === countries.length && countries.every(c => tops.includes(P.country(c.code))), "countries are the top of the place tree; nothing is invented above them");
const nested = subs.find(s => s.parent_id);
if (nested) {
  const parent = subs.find(s => s.id === nested.parent_id);
  ok(K.parents(P.HIERARCHY, P.subdivision(nested.code)).join() === P.subdivision(parent.code), "a subdivision sits under its parent subdivision, to any depth");
}
const flat = subs.find(s => !s.parent_id);
ok(K.parents(P.HIERARCHY, P.subdivision(flat.code)).join() === P.country(flat.country_code), "a first-level subdivision sits under its country");
ok(K.attributes(P.country(countries[0].code)).name === countries[0].name, "a place's name is its attribute");

const MS = require("../lib/seed/places.json").master;
const createdBy = actor => db.get("SELECT COUNT(*) AS n FROM k_events WHERE type=? AND actor=?", K.SEED.events.nodeCreated, actor).n;
ok(createdBy(MS.actor) === countries.length + subs.length && createdBy(MS.importActor) === 0, "a fresh install seeds every place through Geo's write path; nothing needs importing", { write: createdBy(MS.actor), import: createdBy(MS.importActor) });

console.log("places — the kernel is the record; the boot pass only imports");
const evs = db.get("SELECT COUNT(*) AS n FROM k_events").n;
const again = P.importRows();
ok(db.get("SELECT COUNT(*) AS n FROM k_events").n === evs && Object.values(again).every(v => v === 0), "a warm pass writes nothing", again);
const raw = countries[1];
db.run("UPDATE countries SET name='Raw Write' WHERE code=?", raw.code);
P.importRows();
ok(K.attributes(P.country(raw.code)).name === raw.name, "a write that bypasses the write path does not reach an existing place");
db.run("UPDATE countries SET name=? WHERE code=?", raw.name, raw.code);
const legacyParent = subs.find(s => !s.parent_id);
db.run("INSERT INTO subdivisions(code,country_code,name,level,parent_id,position,active) VALUES('ZZ-LEGACY',?,?,?,?,999,1)", legacyParent.country_code, "Legacy", "district", legacyParent.id);
ok(!P.subdivision("ZZ-LEGACY"), "a row from before the place tree has no place");
const imported = P.importRows();
ok(imported.created === 1 && createdBy(MS.importActor) === 1 && K.parents(P.HIERARCHY, P.subdivision("ZZ-LEGACY")).join() === P.subdivision(legacyParent.code), "the boot pass imports it, under its parent", imported);
entity.deleteEntity(0, "subdivision", "ZZ-LEGACY");

console.log("places — every write reaches the place tree");
const cc = countries.find(c => c.active === 1).code;
const node = P.country(cc);
const oldName = K.attributes(node).name;
globalmod.updateCountry(cc, { name: oldName + " (renamed)" });
ok(K.attributes(node).name === oldName + " (renamed)", "a rename in the master reaches the place tree");
ok(K.history(node).some(h => h.attributes.name === oldName && h.recordedTo != null), "and the old name is kept in its history");
globalmod.disableCountry(cc);
ok(LC.nodeState(node) === "hidden" && !K.children(P.HIERARCHY, null).includes(node), "a switched-off country is hidden from listings");
globalmod.enableCountry(cc);
ok(LC.nodeState(node) === "active", "and shown again when switched back on");
const mover = subs.find(s => !s.parent_id && subs.some(o => o.country_code === s.country_code && o.code !== s.code && !o.parent_id));
const newParent = subs.find(o => o.country_code === mover.country_code && o.code !== mover.code && !o.parent_id);
const beforeMove = new Date().toISOString();
while (new Date().toISOString() === beforeMove) { /* the move must start after this instant */ }
const moved = entity.updateEntity(0, "subdivision", mover.code, { parent_id: newParent.id });
ok(!moved.error, "a re-parent in the console is accepted", moved.error);
ok(K.parents(P.HIERARCHY, P.subdivision(mover.code)).join() === P.subdivision(newParent.code), "a re-parented subdivision moves in the tree");
ok(K.parents(P.HIERARCHY, P.subdivision(mover.code), { at: beforeMove }).join() === P.country(mover.country_code), "and where it sat before is kept");
const gone = db.all("SELECT code FROM subdivisions WHERE parent_id IS NULL AND code NOT IN (SELECT s.code FROM subdivisions s JOIN subdivisions c ON c.parent_id = s.rowid)").find(s => s.code !== newParent.code);
const goneNode = P.subdivision(gone.code);
entity.deleteEntity(0, "subdivision", gone.code);
ok(LC.nodeState(goneNode) === "archived" && K.history(goneNode).length > 0 && !db.get("SELECT 1 AS x FROM subdivisions WHERE code=?", gone.code), "a deleted subdivision's place is archived, never erased");
ok(K.verifyEvents().ok, "every write is in the hash-chained log");

console.log("places — currency and locale are settings at the place, not columns of it (LAW-008)");
const C = require("../lib/kernel-context.js");
const registry = require("../lib/registry.js");
const cIN = db.get("SELECT code, currency, locale FROM countries WHERE active=1 ORDER BY position LIMIT 1");
const nIN = P.country(cIN.code);
ok(C.assignedAt("value.currency", { scope: nIN }) === cIN.currency && C.assignedAt("expression.locale", { scope: nIN }) === cIN.locale, "a country's currency and locale are assigned at its node");
const sub = db.get("SELECT code FROM subdivisions WHERE country_code=? LIMIT 1", cIN.code);
if (sub) {
  ok(P.facts(sub.code).currency === cIN.currency, "a subdivision resolves its country's currency, nearest up the tree");
  C.assign("expression.locale", "xx-TEST", { scope: P.subdivision(sub.code) }, "test");
  ok(P.facts(sub.code).locale === "xx-TEST" && P.facts(cIN.code).locale === cIN.locale, "a setting assigned at a subdivision applies there and below, not to its country");
}
const cur = db.get("SELECT code, symbol, decimals FROM currencies WHERE code<>? AND active=1 LIMIT 1", cIN.currency);
globalmod.updateCountry(cIN.code, { currency: cur.code });
const co = registry.country(cIN.code);
ok(co.currency === cur.code && C.assignedAt("value.currency", { scope: nIN }) === cur.code, "changing the master's currency changes the assignment the readers resolve");
ok(co.symbol === cur.symbol && co.decimals === cur.decimals, "a country's money symbol and decimals are its currency's, from Value's master");
ok(db.all("SELECT value FROM k_assignments WHERE setting='value.currency' AND scope=? AND rec_to IS NOT NULL", nIN).some(r => JSON.parse(r.value) === cIN.currency), "the earlier currency stays on record, superseded, not overwritten");
const tr = require("../lib/tax.js").ruleFor(cIN.code);
const prof = registry.countryProfile(cIN.code);
ok(tr ? prof.tax.mode === tr.mode && prof.tax.rate === tr.standard : prof.tax === null, "a country profile's tax is the tax engine's rule, not a column of the country");

console.log("places — every write goes to the kernel first, in the same transaction as the row");
const cur2 = db.get("SELECT code FROM currencies WHERE active=1 LIMIT 1").code;
const made = entity.createEntity(0, "country", { code: "QZ", name: "Testland", currency: cur2, symbol: "¤", locale: "en-QZ", decimals: 2, active: true });
const qz = P.country("QZ");
ok(made.id === "QZ" && qz && K.attributes(qz).name === "Testland", "creating a country in the console creates its place on the kernel");
ok(db.get("SELECT uid FROM countries WHERE code='QZ'").uid === qz, "the row carries its place's universal ID");
ok(C.assignedAt("expression.locale", { scope: qz }) === "en-QZ", "its settings are assigned at its place");
const evQ = db.get("SELECT COUNT(*) AS n FROM k_events").n;
const dup = entity.createEntity(0, "country", { code: "QZ", name: "Testland again", currency: cur2, symbol: "¤", locale: "en-QZ", decimals: 2 });
ok(dup.error && K.attributes(qz).name === "Testland" && db.get("SELECT COUNT(*) AS n FROM k_events").n === evQ, "a write the row refuses leaves the kernel untouched");
const orphan = entity.createEntity(0, "subdivision", { code: "QQ-01", country_code: "QQ", name: "Nowhere", level: "region" });
ok(orphan.error && !db.get("SELECT 1 AS x FROM subdivisions WHERE code='QQ-01'"), "a write the kernel refuses never reaches the row");
const sd = entity.createEntity(0, "subdivision", { code: "QZ-01", country_code: "QZ", name: "North", level: "region" });
ok(!sd.error && K.parents(P.HIERARCHY, P.subdivision("QZ-01")).join() === qz, "a subdivision created in the console sits under its country on the kernel");
entity.updateEntity(0, "country", "QZ", { name: "Testland Renamed" });
ok(K.attributes(qz).name === "Testland Renamed", "an edit in the console is recorded on the kernel");
const qz1 = P.subdivision("QZ-01");
/* the platform's delete path: derived provider links go, the country is withdrawn, then deleted */
db.run("DELETE FROM provider_availability WHERE country_code='QZ'");
registry.withdrawCountry("QZ");
ok(LC.nodeState(qz1) === "archived" && !db.get("SELECT 1 AS x FROM subdivisions WHERE code='QZ-01'"), "withdrawing a country archives its subdivisions' places with the rows");
entity.deleteEntity(0, "country", "QZ");
ok(LC.nodeState(qz) === "archived" && !db.get("SELECT 1 AS x FROM countries WHERE code='QZ'"), "deleting a country archives its place and removes the row");
ok(K.history(qz).length > 0 && K.verifyEvents().ok, "the archived place keeps its history in an intact log");
console.log("  (" + placeNodes.length + " places on the kernel)");

for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
