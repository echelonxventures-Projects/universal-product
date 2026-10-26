/* A store's attribute definitions are a read model of the platform master: the master's definitions
   that apply where it sells, its own in its namespace, its addenda over them — in the editor's shape
   the attribute_types vocabulary gives. The platform's attribute registry is the master's. */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os");
const TMP = path.join(os.tmpdir(), "sattr-" + process.pid + ".db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
process.env.LX_DB = TMP;
const silence = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = silence;
const M = require("../lib/platform-master.js");
const SA = require("../lib/store-attributes.js");
const ST = require("../lib/store-taxonomy.js");
const MP = require("../lib/master-permissions.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const throws = (fn, re, n) => { try { fn(); ok(false, n, "did not throw"); } catch (e) { ok(re.test(e.message), n, e.message); } };
const rows = t => db.all("SELECT * FROM attribute_defs WHERE tenant_id=?", t);
const t = 1;

console.log("store attributes — the master's, where the store sells");
const inds = ST.industriesOf(t);
const applies = M.attributeSet({ at: inds });
ok(rows(t).length === applies.length && applies.every(d => rows(t).some(r => r.key === d.name && r.node_uid === d.uid)), "the store has every master definition that applies to its industries, and only those", [rows(t).length, applies.length]);
const choice = applies.find(d => d.constraints && d.constraints.oneOf);
const cr = rows(t).find(r => r.key === choice.name);
ok(JSON.parse(cr.options).join() === choice.constraints.oneOf.join() && M.vocabulary(M.ROLES.attributeTypes).find(x => x.name === cr.type).choice, "a one-of rule shows as a choice with its options");

console.log("store attributes — the store's own");
SA.save(t, { key: "shelf_life_note", label: "Shelf note", type: "text" }, "store-admin");
const mine = rows(t).find(r => r.key === "shelf_life_note");
ok(mine && require("../lib/kernel.js").internal.nodeRow(mine.node_uid).namespace === MP.storeHolder(t), "a store's own definition lives in its namespace on the master");
ok(!rows(2).some(r => r.key === "shelf_life_note"), "and no other store has it");
SA.save(t, { key: "shelf_life_note", label: "Shelf life note", type: "select", options: ["short", "long"] }, "store-admin");
ok(rows(t).find(r => r.key === "shelf_life_note").label === "Shelf life note" && JSON.parse(rows(t).find(r => r.key === "shelf_life_note").options).length === 2, "it edits its own directly");
SA.remove(t, "shelf_life_note", "store-admin");
ok(!rows(t).some(r => r.key === "shelf_life_note"), "and removes it");
throws(() => SA.save(t, { key: "x_unknown_type", label: "X", type: "hologram" }), /Unknown attribute type/, "field types come from the vocabulary");

console.log("store attributes — a master definition changes by contribution");
let refused = null; try { SA.save(t, { key: choice.name, label: "Local label", type: cr.type, options: JSON.parse(cr.options) }, "store-admin"); } catch (e) { refused = e.message; }
ok(/Not permitted|does not allow/.test(refused || ""), "without a permission a store cannot propose it", refused);

console.log("store attributes — the platform's registry is the master's");
const before = SA.platformList().length;
SA.platformCreate({ key: "probe_attr", label: "Probe", category: "Probe" }, "platform");
ok(SA.platformList().length === before + 1 && M.definitions().some(d => d.name === "probe_attr"), "a platform attribute is a master definition");
throws(() => SA.platformCreate({ key: "probe_attr", label: "Probe" }, "platform"), /already exists/, "named once");

for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
