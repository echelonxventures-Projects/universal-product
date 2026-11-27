/* Purchasing (lib/purchasing.js): an order to a supplier, the goods received against it into a
   warehouse batch, and the supplier's bill matched against what was received — each on the master,
   each moving through its state machine, and each posting to the store's books. */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os");
const TMP = path.join(os.tmpdir(), "purchasing-" + process.pid + ".db");
const wipe = () => { for (const s of ["", "-wal", "-shm"]) try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } };
wipe(); process.env.LX_DB = TMP;
const log = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = log;
const K = require("../lib/kernel.js"), P = require("../lib/purchasing.js"), B = require("../lib/books.js"), RR = require("../lib/row-records.js"), OPS = require("../lib/operations.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + JSON.stringify(x).slice(0, 400) : ""))); };
const throws = (fn, re) => { try { fn(); return false; } catch (e) { return re.test(e.message) || (console.log("    (threw: " + e.message + ")"), false); } };
try {
  const t = 1, sup = db.get("SELECT * FROM suppliers WHERE tenant_id=? ORDER BY id LIMIT 1", t);
  const [A, Bp] = db.all("SELECT p.id, (SELECT id FROM skus k WHERE k.tenant_id=p.tenant_id AND k.product_id=p.id) sku FROM products p WHERE p.tenant_id=? AND p.type='physical' AND p.deleted_at IS NULL AND (SELECT COUNT(*) FROM skus k WHERE k.tenant_id=p.tenant_id AND k.product_id=p.id)=1 ORDER BY p.id LIMIT 2", t);
  const wh = db.get("SELECT id FROM warehouses WHERE tenant_id=? ORDER BY id DESC LIMIT 1", t).id;
  const count = p => [db.get("SELECT stock s FROM products WHERE tenant_id=? AND id=?", t, p.id).s, db.get("SELECT stock s FROM skus WHERE id=?", p.sku).s, db.get("SELECT COALESCE(SUM(qty),0) s FROM inventory WHERE sku_id=?", p.sku).s];
  const cur = String(sup.currency).toUpperCase();
  const bal = code => { const tb = B.trialBalance(t).find(x => x.currency === cur); const r = tb && tb.rows.find(x => x.account === code); return r ? r.balance : 0; };
  const [inv0, grni0, ap0, var0, tax0, bank0] = ["1300", "2050", "2000", "5100", "1400", "1000"].map(bal);
  const d = (code, b0) => +(bal(code) - b0).toFixed(2);

  console.log("▸ A PURCHASE ORDER");
  ok(throws(() => P.createOrder(t, { supplier_id: sup.id, lines: [] }), /at least one line/) && throws(() => P.createOrder(t, { supplier_id: sup.id, lines: [{ product_id: A.id, qty: 0, unit_cost: 5 }] }), /whole number/), "an order needs lines of a whole quantity");
  const pr = db.get("SELECT id, status FROM purchase_requests WHERE tenant_id=? AND status='submitted'", t);
  ok(throws(() => P.createOrder(t, { supplier_id: sup.id, request_id: pr.id, lines: [{ product_id: A.id, qty: 1, unit_cost: 1 }] }), /approved purchase request/), "only an approved purchase request is ordered");
  db.run("INSERT INTO approvals(tenant_id,kind,ref_id,ref,requester,status,approver) VALUES(?,?,?,?,?,?,?)", t, "purchase_request", pr.id, "PR", "test", "approved", "test");
  try { OPS.advanceRequest(t, pr.id, "approved", "test"); } catch (e) { db.run("UPDATE purchase_requests SET status='approved' WHERE id=?", pr.id); }
  const po = P.createOrder(t, { supplier_id: sup.id, warehouse_id: wh, request_id: pr.id, lines: [{ product_id: A.id, qty: 10, unit_cost: 4 }, { product_id: Bp.id, qty: 5, unit_cost: 10 }] }, "buyer");
  ok(po.status === "draft" && po.total === 90 && po.lines.length === 2 && po.lines[0].sku_id === A.sku && po.currency === cur, "it is drafted at the supplier's currency, with each line's variant", po);
  ok(K.internal.nodeRow(po.uid).kind === "supply.purchase_order", "it is on the master");
  ok(throws(() => P.receive(t, po.id, { lines: [{ line_id: po.lines[0].id, qty: 1 }] }), /sent purchase order/), "nothing is received before it is sent");
  P.send(t, po.id, "buyer");
  ok(P.order(t, po.id).status === "sent" && P.order(t, po.id).sent_at && db.get("SELECT status FROM purchase_requests WHERE id=?", pr.id).status === "ordered", "sent: stamped, and its purchase request is now ordered");

  console.log("▸ GOODS RECEIVED");
  const a0 = count(A);
  ok(throws(() => P.receive(t, po.id, { lines: [{ line_id: po.lines[0].id, qty: 11 }] }), /still to come/), "no more is received than was ordered");
  const g1 = P.receive(t, po.id, { warehouse_id: wh, lines: [{ line_id: po.lines[0].id, qty: 6, lot: "L-1", expiry: "2027-06-30" }] }, "dock");
  const a1 = count(A);
  ok(a1.every((v, i) => v === a0[i] + 6), "6 arrive: the product, its variant and the warehouse all count them", [a0, a1]);
  ok(db.get("SELECT qty FROM inventory WHERE sku_id=? AND warehouse_id=? AND lot='L-1' AND expiry='2027-06-30'", A.sku, wh).qty === 6, "in their own batch at the warehouse, with lot and expiry");
  ok(P.order(t, po.id).status === "partly_received" && g1.value === 24 && RR.at("goods_receipt", g1.id).belongsTo === po.uid, "the order is partly received; the receipt is on the master, under the order");
  ok(d("1300", inv0) === 24 && d("2050", grni0) === 24, "the books: stock up 24, owed for goods not yet billed up 24", [d("1300", inv0), d("2050", grni0)]);

  console.log("▸ THE SUPPLIER'S BILL, MATCHED");
  const b1 = P.bill(t, { po_id: po.id, supplier_ref: "SUP-1001", net: 24, tax: 2.4 }, "ap");
  ok(b1.status === "open" && b1.matched === 24 && b1.variance === 0 && b1.gross === 26.4 && b1.due_at, "a bill that matches what was received is approved and owed, due by the supplier's terms", b1);
  ok(d("2050", grni0) === 0 && d("2000", ap0) === 26.4 && d("1400", tax0) === 2.4, "the books: received-not-billed cleared, owed to the supplier with its tax to reclaim", [d("2050", grni0), d("2000", ap0), d("1400", tax0)]);
  ok(throws(() => P.bill(t, { po_id: po.id, supplier_ref: "SUP-1001", net: 1 }), /already recorded/), "the same supplier invoice is not recorded twice");
  ok(throws(() => P.bill(t, { po_id: po.id, supplier_ref: "SUP-1002", net: 5 }), /waiting to be billed/), "nor billed for what has not arrived");

  console.log("▸ THE REST ARRIVES, AND A BILL THAT DOES NOT MATCH");
  P.receive(t, po.id, { lines: [{ line_id: po.lines[0].id, qty: 4 }, { line_id: po.lines[1].id, qty: 5 }] }, "dock");
  ok(P.order(t, po.id).status === "received" && db.get("SELECT status FROM purchase_requests WHERE id=?", pr.id).status === "received", "everything is in: the order is received, and so is its request");
  const b2 = P.bill(t, { po_id: po.id, supplier_ref: "SUP-1002", net: 70 }, "ap");
  ok(b2.status === "held" && b2.matched === 66 && b2.variance === 4 && /more than 2% apart/.test(b2.hold_reason), "billed 70 for 66 received: held, with the reason", b2);
  ok(d("2000", ap0) === 26.4, "a held bill is not yet owed in the books");
  ok(throws(() => P.pay(t, b2.id), /approved, unpaid/), "nor can it be paid");
  ok(throws(() => P.release(t, b2.id, "ap", ""), /Say why/), "releasing it needs a reason");
  P.release(t, b2.id, "controller", "freight agreed by phone");
  ok(d("2000", ap0) === 96.4 && d("5100", var0) === 4 && d("2050", grni0) === 0, "released: owed, with the 4 as a purchase price difference", [d("2000", ap0), d("5100", var0), d("2050", grni0)]);

  console.log("▸ PAID, VOIDED, AND THE TOTALS");
  P.pay(t, b1.id);
  ok(d("1000", bank0) === -26.4 && d("2000", ap0) === 70 && P.bills(t).find(b => b.id === b1.id).paid_at, "paying a bill clears what is owed from the bank");
  const ages = P.payables(t).find(x => x.supplier === sup.name);
  ok(ages && ages.total === 70 && ages.current === 70, "what is owed to the supplier, by age", ages);
  P.voidBill(t, b2.id);
  ok(d("2000", ap0) === 0 && d("5100", var0) === 0 && d("2050", grni0) === 66, "voiding an approved bill undoes its entry: the goods are again received-not-billed", [d("2000", ap0), d("5100", var0), d("2050", grni0)]);
  ok(RR.history("supplier_bill", b2.id, "status").map(h => h.value).join() === "held,open,void", "the bill's history: held, released, voided");
  const tb = B.trialBalance(t).find(x => x.currency === cur), h = B.health(t);
  ok(Math.abs(tb.debit - tb.credit) < 1e-6 && !h.missing.length && !h.unbalanced.length && !h.drift.length, "the books balance, every receipt and bill is in them, and they match the log", { tb: [tb.debit, tb.credit], h });
  ok(P.order(t, po.id).actions.join() === "close,bill" && P.bills(t).find(b => b.id === b1.id).actions.length === 0, "the screen is offered only what each state allows: close it, or bill what the voided bill left unbilled", P.order(t, po.id).actions);
  ok(throws(() => P.cancel(t, po.id), /close it instead/), "an order with receipts is closed, not cancelled");
  P.close(t, po.id);
  ok(P.order(t, po.id).status === "closed" && P.order(t, po.id).closed_at, "and closed");
} catch (e) { failed++; console.log("  ✗ threw: " + e.stack); }
finally { wipe(); console.log(`\n${passed} passed, ${failed} failed`); process.exit(failed ? 1 : 0); }
