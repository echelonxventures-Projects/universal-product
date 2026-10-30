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

console.log("store taxonomy — a store's tree is synced as sets, in one transaction (PR-043)");
{
  const K = require("../lib/kernel.js");
  ok(JSON.stringify(K.snapshot(() => ST.desired(t))) === JSON.stringify(ST.desired(t)), "read in one kernel snapshot, the tree is the one read node by node");
  /* statements reach SQLite through the handle's prepare: counted on the instance, then removed */
  let stmts = 0;
  db.db.prepare = function (q) { stmts++; return Object.getPrototypeOf(this).prepare.call(this, q); };
  const nRows = db.get("SELECT COUNT(*) AS c FROM taxonomy WHERE tenant_id=?", t).c;
  const w0 = db.writes(); stmts = 0; ST.sync(t);
  const syncStmts = stmts, syncWrites = db.writes() - w0;
  delete db.db.prepare;
  /* before, every node cost dozens of statements (38,796 for this tree): one round trip each on Postgres */
  ok(syncStmts * 4 < nRows, "a sync reads the master as sets: far fewer statements than the tree has rows", { statements: syncStmts, rows: nRows });
  ok(syncWrites === 0, "a sync with nothing to change writes nothing", syncWrites);
  /* a sync that fails part-way: five rows drifted, the third repair fails */
  const drift = db.all("SELECT id, name FROM taxonomy WHERE tenant_id=? AND active=1 AND node_uid IS NOT NULL ORDER BY id LIMIT 5", t);
  for (const r of drift) db.run("UPDATE taxonomy SET name=? WHERE id=?", r.name + " (drifted)", r.id);
  const names = () => drift.map(r => db.get("SELECT name FROM taxonomy WHERE id=?", r.id).name);
  const realRun = db.run; let n = 0, threw = null;
  db.run = (q, ...a) => { if (/^UPDATE taxonomy SET parent_id/.test(q) && ++n === 3) throw new Error("injected failure"); return realRun(q, ...a); };
  try { ST.sync(t); } catch (e) { threw = e.message; } finally { db.run = realRun; }
  ok(threw === "injected failure" && names().every(x => / \(drifted\)$/.test(x)), "a sync that fails part-way leaves the tree as it was", { threw, names: names() });
  ok(ST.sync(t) === drift.length && names().join() === drift.map(r => r.name).join(), "the next sync completes it");
  ok(ST.sync(t) === 0, "and a sync after that changes nothing");
  /* each store's tree holds the master's nodes and its own, never another store's */
  ST.sync(2);
  const nsOf = uid => K.internal.nodeRow(uid).namespace;
  ok([t, 2].every(x => db.all("SELECT node_uid FROM taxonomy WHERE tenant_id=? AND node_uid IS NOT NULL", x).every(r => [M.NAMESPACE, MP.storeHolder(x)].includes(nsOf(r.node_uid)))), "no store's tree holds another store's categories");
  ok(db.get("SELECT COUNT(*) AS c FROM (SELECT tenant_id, node_uid FROM taxonomy WHERE node_uid IS NOT NULL GROUP BY tenant_id, node_uid HAVING COUNT(*) > 1) d").c === 0, "a node has one row per store");
}

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
