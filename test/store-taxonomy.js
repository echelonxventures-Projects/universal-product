/* A store's category tree is a read model of the platform master (GLOBAL_MASTER.md §6): the master's
   taxonomy under the industries it sells in, its own categories in its own namespace, its approved
   addenda over them. Rows keep their ids across rebuilds; an older store's rows are linked to the
   master once; nothing edits the table. */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os");
const TMP = path.join(os.tmpdir(), "stax-" + process.pid + ".db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
process.env.LX_DB = TMP;
const silence = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = silence;
const M = require("../lib/platform-master.js");
const ST = require("../lib/store-taxonomy.js");
const MP = require("../lib/master-permissions.js");
const C = require("../lib/master-contributions.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const rows = t => db.all("SELECT * FROM taxonomy WHERE tenant_id=? AND active=1", t);

console.log("store taxonomy — a read model of the master");
const t = 1;
const inds = ST.industriesOf(t);
const ind = inds[0];
const indRow = rows(t).find(r => r.key === ind);
ok(indRow && indRow.node_uid === M.uidOf(ind), "each row is a master node, keyed by it");
const cats = M.children(ind);
ok(cats.every(c => rows(t).some(r => r.node_uid === c.uid && r.parent_id === indRow.id)), "the store has the master's categories under its industries");
const before = rows(t).map(r => r.id).sort().join();
ST.sync(t);
ok(rows(t).map(r => r.id).sort().join() === before, "rebuilding keeps every row's id (products stay filed)");
ok(db.get("SELECT COUNT(*) c FROM products WHERE tenant_id=? AND node_id IS NOT NULL", t).c > 0, "the store's products are filed under master categories");

console.log("store taxonomy — the store's own categories");
ST.save(t, null, { name: "Store-only shelf", level: "category", parent_id: indRow.id }, "store-admin");
const mine = rows(t).find(r => r.name === "Store-only shelf");
ok(mine && require("../lib/kernel.js").internal.nodeRow(mine.node_uid).namespace === MP.storeHolder(t), "a store's own category lives in its own namespace on the master");
ok(!rows(2).some(r => r.name === "Store-only shelf"), "and no other store sees it");
ST.save(t, mine.id, { name: "Renamed shelf" }, "store-admin");
ok(rows(t).find(r => r.id === mine.id).name === "Renamed shelf", "the store renames its own category directly");
ST.remove(t, mine.id, "store-admin");
ok(!rows(t).some(r => r.id === mine.id), "and removes it (the row is kept inactive)");

console.log("store taxonomy — a master category is changed by contribution");
const cat = cats[0];
const catRow = rows(t).find(r => r.node_uid === cat.uid);
let refused = null; try { ST.save(t, catRow.id, { name: "Local name" }, "store-admin"); } catch (e) { refused = e.message; }
ok(/Not permitted|does not allow/.test(refused || ""), "without a permission, a store cannot propose a change to a master category", refused);
MP.grant({ holder: MP.storeHolder(t), scope: [ind], objects: ["classification"], actions: ["overlay"], review: M.vocabulary(M.ROLES.reviews).find(r => !r.effectiveOnApproval).name }, "platform");
ST.save(t, catRow.id, { name: "Local name" }, "store-admin");
ok(rows(t).find(r => r.id === catRow.id).name === "Local name" && C.list({ holder: MP.storeHolder(t), awaiting: true }).length === 1, "reviewed after: the local name shows for this store at once, and awaits review");
ok(rows(2).find(r => r.node_uid === cat.uid) === undefined || rows(2).find(r => r.node_uid === cat.uid).name !== "Local name", "no other store sees it");

console.log("store taxonomy — an older store's rows are linked once");
const t9 = Number(db.run("INSERT INTO tenants(slug,name,domain,status,mode,industries,profile) VALUES('legacy-tax','Legacy','legacy-tax.localhost','active','marketplace','[]','{}')").lastInsertRowid);
const a = Number(db.run("INSERT INTO taxonomy(tenant_id,level,key,name,position) VALUES(?,?,?,?,0)", t9, "industry", ind, "Old industry name").lastInsertRowid);
db.run("INSERT INTO taxonomy(tenant_id,parent_id,level,key,name,position) VALUES(?,?,?,?,?,0)", t9, a, "category", ind + ".old-shelf", "A shelf the master lacks");
db.run("INSERT INTO taxonomy(tenant_id,parent_id,level,key,name,position) VALUES(?,?,?,?,?,0)", t9, a, "category", ind + ".x", require("../lib/kernel.js").text(cats[0].attributes.title, "en"));
ok(ST.adopt(t9) === 3, "every older row is linked");
const linked = db.all("SELECT * FROM taxonomy WHERE tenant_id=?", t9);
ok(linked.find(r => r.id === a).node_uid === M.uidOf(ind), "an industry by its key");
ok(linked.find(r => r.key === ind + ".x").node_uid === cats[0].uid, "a category by its name under its parent");
ok(require("../lib/kernel.js").internal.nodeRow(linked.find(r => r.key === ind + ".old-shelf").node_uid).namespace === MP.storeHolder(t9), "one the master lacks becomes the store's own");

for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
