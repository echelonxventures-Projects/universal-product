/* Stock valuation (lib/valuation.js): received goods carry their cost; what is sold or written off
   takes its cost from the layers by the store's method (fifo or average) and posts to the books;
   what comes back returns at the cost it left at; stock with no cost leaves first, at none, and is
   reported; and the layers always equal the books' inventory account to the cent. */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os");
const TMP = path.join(os.tmpdir(), "valuation-" + process.pid + ".db");
const wipe = () => { for (const s of ["", "-wal", "-shm"]) try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } };
wipe(); process.env.LX_DB = TMP;
const log = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = log;
const V = require("../lib/valuation.js"), P = require("../lib/purchasing.js"), B = require("../lib/books.js"), S = require("../lib/stock.js"), ST = require("../lib/settings.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + JSON.stringify(x).slice(0, 400) : ""))); };
const throws = (fn, re) => { try { fn(); return false; } catch (e) { return re.test(e.message) || (console.log("    (threw: " + e.message + ")"), false); } };
try {
  const t = 1, sup = db.get("SELECT * FROM suppliers WHERE tenant_id=? ORDER BY id LIMIT 1", t), cur = String(sup.currency).toUpperCase();
  const items = db.all("SELECT p.id, p.stock, (SELECT id FROM skus k WHERE k.tenant_id=p.tenant_id AND k.product_id=p.id) sku FROM products p WHERE p.tenant_id=? AND p.type='physical' AND p.deleted_at IS NULL AND p.stock>20 AND (SELECT COUNT(*) FROM skus k WHERE k.tenant_id=p.tenant_id AND k.product_id=p.id)=1 AND (SELECT stock FROM skus k WHERE k.tenant_id=p.tenant_id AND k.product_id=p.id)=p.stock ORDER BY p.id LIMIT 3", t);
  const [A, Bi, D] = items;
  const bal = code => { const tb = B.trialBalance(t).find(x => x.currency === cur); const r = tb && tb.rows.find(x => x.account === code); return r ? r.balance : 0; };
  const cogs0 = bal("5000");
  const cogs = () => +(bal("5000") - cogs0).toFixed(2);
  const order = () => Number(db.run("INSERT INTO orders(tenant_id,owner,num,name,sub,total,status,currency) VALUES(?,?,?,?,0,0,'processing',?)", t, "t1:guest", "VAL-" + Math.random().toString(36).slice(2, 8), "V", cur).lastInsertRowid);
  const buy = (item, qty, cost) => { const po = P.createOrder(t, { supplier_id: sup.id, lines: [{ product_id: item.id, qty, unit_cost: cost }] }, "t"); P.send(t, po.id); P.receive(t, po.id, { lines: [{ line_id: po.lines[0].id, qty }] }, "t"); };
  const zero = () => V.reconcile(t).every(r => Math.abs(r.difference) < 1e-9);

  console.log("▸ STOCK BEFORE VALUATION");
  ok(V.method(t) === "fifo", "a store values its stock first-in, first-out unless it chooses otherwise");
  const before = V.onHand(t);
  ok(before.unvalued.some(u => u.product_id === A.id && u.qty === A.stock), "stock counted before valuation is reported as having no cost", before.unvalued.find(u => u.product_id === A.id));
  const od = order(); S.take(t, od, [{ product_id: D.id, qty: 2 }]);
  ok(cogs() === 0 && V.orderCost(t, od)[cur] === undefined, "it leaves at no cost — never guessed at");

  console.log("▸ FIRST IN, FIRST OUT");
  ok(throws(() => V.opening(t, { product_id: A.id }), /unit cost/), "an opening valuation needs a unit cost");
  const op = V.opening(t, { product_id: A.id, unit_cost: 3, currency: cur }, "accountant");
  ok(op.qty === A.stock && op.value === A.stock * 3 && !V.onHand(t).unvalued.some(u => u.product_id === A.id), "the stock on hand is given its opening cost", op);
  ok(throws(() => V.opening(t, { product_id: A.id, unit_cost: 3, currency: cur }), /already has a cost/), "once");
  buy(A, 10, 4); buy(A, 10, 6);
  const o1 = order(); S.take(t, o1, [{ product_id: A.id, qty: A.stock + 8 }]);
  ok(cogs() === A.stock * 3 + 32 && V.orderCost(t, o1)[cur] === A.stock * 3 + 32, "selling all the opening stock and 8 more: the oldest costs first", [cogs(), A.stock * 3 + 32]);
  const o2 = order(); S.take(t, o2, [{ product_id: A.id, qty: 4 }]);
  ok(cogs() === A.stock * 3 + 52, "4 more: the last 2 at 4, then 2 at 6", cogs());
  S.giveBack(t, o2, A.id, 1);
  ok(cogs() === A.stock * 3 + 46 && V.orderCost(t, o2)[cur] === 14, "one comes back: at the 6 it left at", [cogs(), V.orderCost(t, o2)]);
  ok(V.onHand(t).items.filter(i => i.product_id === A.id).reduce((s, i) => s + i.qty, 0) === 9 && zero(), "9 are on hand at their cost, and the layers equal the books' inventory", V.reconcile(t));

  console.log("▸ WRITTEN OFF");
  const wo0 = bal("6400"), row = db.get("SELECT id, qty FROM inventory WHERE sku_id=? AND qty>0 ORDER BY qty DESC LIMIT 1", A.sku);
  S.writeOff(t, row.id);
  ok(bal("6400") > wo0 && zero(), "writing stock off posts its cost as stock written off", [bal("6400") - wo0]);

  console.log("▸ WEIGHTED AVERAGE");
  ok(throws(() => V.setMethod(t, "lifo"), /one of: fifo, average/), "only a declared method is chosen");
  const own0 = db.get("SELECT value FROM settings WHERE tenant_id=? AND key='commerce'", t);
  V.setMethod(t, "average");
  const own1 = JSON.parse(db.get("SELECT value FROM settings WHERE tenant_id=? AND key='commerce'", t).value);
  ok(Object.keys(own1).length === Object.keys(own0 ? JSON.parse(own0.value) : {}).filter(k => k !== "stockValuation").length + 1, "choosing it saves only that choice, not a copy of every default", Object.keys(own1));
  ok(V.method(t) === "average", "a store chooses the average method");
  V.opening(t, { product_id: Bi.id, unit_cost: 5, currency: cur });
  buy(Bi, 2, 10);
  const c0 = cogs(), o3 = order(); S.take(t, o3, [{ product_id: Bi.id, qty: 4 }]);
  const avg = (Bi.stock * 5 + 20) / (Bi.stock + 2);
  ok(Math.abs((cogs() - c0) - +(avg * 4).toFixed(2)) <= 0.01, "each unit leaves at the weighted average of what is on hand", [cogs() - c0, avg * 4]);
  const items3 = V.onHand(t).items.filter(i => i.product_id === Bi.id);
  ok(items3.length === 1 && Math.abs(items3[0].unit_cost - avg) < 0.01, "what is left carries that one cost", items3);
  ok(zero(), "the layers still equal the books to the cent", V.reconcile(t));

  console.log("▸ NOTHING IS LOST");
  const h = B.health(t), tb = B.trialBalance(t).find(x => x.currency === cur);
  ok(!h.unbalanced.length && !h.drift.length && Math.abs(tb.debit - tb.credit) < 1e-6, "every entry balances and matches the log");
  ok(S.giveBack(t, o2, A.id, 5) === 3 && zero(), "giving back more than is out returns only what is out (3), each at its cost");
  const n0 = B.entries(t, { limit: 1000 }).length;
  ok(S.giveBack(t, o2, A.id, 1) === 0 && B.entries(t, { limit: 1000 }).length === n0, "and then nothing more moves");
} catch (e) { failed++; console.log("  ✗ threw: " + e.stack); }
finally { wipe(); console.log(`\n${passed} passed, ${failed} failed`); process.exit(failed ? 1 : 0); }
