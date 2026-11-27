/* LUXORA Platform — purchasing (owner Commerce).

   An order to a supplier (purchase_orders), the goods received against it (goods_receipts) and the
   supplier's bill (supplier_bills). Each is a record on the master (lib/seed/row-records.json) and
   moves through its declared state machine (lib/seed/states.json). Receiving puts the goods in the
   warehouse — the product's and variant's counts and the batch's shelf row — and the books post
   the stock against what is received but not yet billed (lib/books.js). A bill is matched against
   that: within the tolerance it is approved and owed; beyond it, it is held until released with a
   reason. A purchase order made from an approved purchase request moves the request to ordered,
   and to received when everything has come in. Policy is data (lib/seed/purchasing.json). */
"use strict";

const db = () => require("./db.js");
const K = require("./kernel.js");
const RR = () => require("./row-records.js");
const states = require("./states.js");
const SEED = require("./seed/purchasing.json");
const fail = (msg, status, code) => { const e = new Error(msg); e.status = status || 400; if (code) e.code = code; throw e; };
const r2 = n => +Number(n || 0).toFixed(2);
const tx = fn => K.internal.tx(fn);
const N = Number;
const M = SEED.machines;

function nextRef(tid, record, table) {
  const n = db().get(`SELECT COUNT(*) c FROM ${table} WHERE tenant_id=?`, N(tid)).c + 1;
  return `${SEED.refs[record]}-${N(tid)}-${String(n).padStart(5, "0")}`;
}
const supplierOf = (tid, id) => db().get("SELECT * FROM suppliers WHERE id=? AND tenant_id=?", N(id), N(tid)) || fail("No such supplier", 404);
const poRow = (tid, id) => db().get("SELECT * FROM purchase_orders WHERE id=? AND tenant_id=?", N(id), N(tid)) || fail("No such purchase order", 404);
const linesOf = poId => db().all("SELECT * FROM purchase_order_lines WHERE po_id=? ORDER BY id", N(poId));
/* a record moves only as its machine allows; the state's stamps (sent_at, paid_at…) come with it */
function move(record, table, row, to, extra) {
  const { patch } = states.apply(record, { tenantId: row.tenant_id, from: row.status, to, row });
  const all = { ...patch, ...(extra || {}) }, cols = Object.keys(all);
  RR().change(record, row.id, () => {
    const r = db().run(`UPDATE ${table} SET ${cols.map(c => c + "=?").join(", ")} WHERE id=? AND status=?`, ...cols.map(c => all[c]), row.id, row.status);
    if (!r.changes) fail("This has just changed — reload it", 409);
    return r;
  });
  return db().get(`SELECT * FROM ${table} WHERE id=?`, row.id);
}

/* what may be done next to a record, from its state's tags (lib/seed/states.json): the screen offers
   only these */
const tagged = (m, s, t) => states.has(m, s) && states.is(m, s, t);
function orderActions(po, hasReceipts, outstanding) {
  const m = M.order, s = po.status, out = [];
  if (tagged(m, s, "editable")) out.push("send", "cancel");
  if (tagged(m, s, "receivable") && outstanding) out.push("receive");
  if ((tagged(m, s, "receivable") || tagged(m, s, "success")) && hasReceipts) out.push("close");
  if (tagged(m, s, "receivable") && !hasReceipts) out.push("cancel");
  return out;
}
function billActions(b) {
  const m = M.bill, s = b.status, out = [];
  if (tagged(m, s, "held")) out.push("release", "void");
  if (tagged(m, s, "payable")) out.push("pay", "void");
  return out;
}
/* ============================== purchase orders ============================== */
/* { supplier_id, warehouse_id?, request_id?, currency?, expected_at?, note?, lines: [{ product_id, sku_id?, qty, unit_cost }] } */
function createOrder(tid, input, actor) {
  const i = input || {}, sup = supplierOf(tid, i.supplier_id), t = N(tid);
  const lines = (i.lines || []).map(l => {
    const p = db().get("SELECT id FROM products WHERE tenant_id=? AND id=? AND deleted_at IS NULL", t, String(l.product_id || ""));
    if (!p) fail("No such product: " + l.product_id);
    const qty = N(l.qty), cost = r2(l.unit_cost);
    if (!Number.isInteger(qty) || qty < 1) fail("Each line orders a whole number of at least 1");
    if (!(cost >= 0)) fail("Each line has a unit cost of zero or more");
    let sku = l.sku_id ? db().get("SELECT id FROM skus WHERE id=? AND tenant_id=? AND product_id=?", N(l.sku_id), t, p.id) : null;
    if (l.sku_id && !sku) fail("That variant is not of " + p.id);
    if (!sku) { const only = db().all("SELECT id FROM skus WHERE tenant_id=? AND product_id=? AND active=1 ORDER BY id LIMIT 2", t, p.id); if (only.length === 1) sku = only[0]; }
    return { product_id: p.id, sku_id: sku ? sku.id : null, qty, unit_cost: cost };
  });
  if (!lines.length) fail("An order needs at least one line");
  if (i.warehouse_id && !db().get("SELECT id FROM warehouses WHERE id=? AND tenant_id=? AND deleted_at IS NULL", N(i.warehouse_id), t)) fail("No such warehouse");
  if (i.request_id) {
    const pr = db().get("SELECT * FROM purchase_requests WHERE id=? AND tenant_id=?", N(i.request_id), t) || fail("No such purchase request", 404);
    if (!states.is(M.request, pr.status, "approved")) fail("Only an approved purchase request is ordered", 409);
  }
  const currency = String(i.currency || sup.currency || require("./defaults.js").currency(t)).toUpperCase();
  require("./wallet.js").unitOf(currency);
  const total = r2(lines.reduce((s, l) => s + l.qty * l.unit_cost, 0));
  return tx(() => {
    const r = RR().created(M.order, () => db().run("INSERT INTO purchase_orders(tenant_id,ref,supplier_id,warehouse_id,request_id,currency,status,total,expected_at,note,created_by) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
      t, nextRef(t, M.order, "purchase_orders"), sup.id, i.warehouse_id ? N(i.warehouse_id) : null, i.request_id ? N(i.request_id) : null, currency, states.initial(M.order), total,
      i.expected_at || null, String(i.note || "").slice(0, 500), String(actor || "")));
    const id = N(r.lastInsertRowid);
    for (const l of lines) db().run("INSERT INTO purchase_order_lines(tenant_id,po_id,product_id,sku_id,qty,unit_cost) VALUES(?,?,?,?,?,?)", t, id, l.product_id, l.sku_id, l.qty, l.unit_cost);
    return order(t, id);
  });
}
function order(tid, id) {
  const po = poRow(tid, id);
  const lines = linesOf(po.id).map(l => ({ ...l, outstanding: l.qty - l.received }));
  const receipts = db().all("SELECT * FROM goods_receipts WHERE po_id=? ORDER BY id", po.id);
  const bills = db().all("SELECT * FROM supplier_bills WHERE po_id=? ORDER BY id", po.id);
  const unbilled = unbilledValue(po.id), billable = unbilled > 0 && !tagged(M.order, po.status, "void");
  return { ...po, supplier: supplierOf(tid, po.supplier_id).name, lines, receipts, bills: bills.map(b => ({ ...b, actions: billActions(b) })), unbilled,
    actions: orderActions(po, receipts.length > 0, lines.some(l => l.outstanding > 0)).concat(billable ? ["bill"] : []) };
}
function orders(tid, f) {
  const o = f || {};
  return db().all(`SELECT po.*, s.name supplier FROM purchase_orders po JOIN suppliers s ON s.id=po.supplier_id WHERE po.tenant_id=? AND (?='' OR po.status=?) AND (?=0 OR po.supplier_id=?) ORDER BY po.id DESC LIMIT 300`,
    N(tid), o.status || "", o.status || "", N(o.supplier_id) || 0, N(o.supplier_id) || 0);
}
function send(tid, id, actor) {
  const po = poRow(tid, id);
  return tx(() => {
    const out = move(M.order, "purchase_orders", po, states.first(M.order, "receivable"));
    if (po.request_id) { const pr = db().get("SELECT status FROM purchase_requests WHERE id=?", po.request_id); if (pr && states.is(M.request, pr.status, "approved") && !states.is(M.request, pr.status, "placed")) require("./operations.js").advanceRequest(N(tid), po.request_id, states.first(M.request, "placed"), actor); }
    return out;
  });
}
function cancel(tid, id) {
  const po = poRow(tid, id);
  if (db().get("SELECT 1 FROM goods_receipts WHERE po_id=? LIMIT 1", po.id)) fail("Goods have been received against this order: close it instead", 409);
  return move(M.order, "purchase_orders", po, states.first(M.order, "void"));
}
function close(tid, id) {
  const po = poRow(tid, id);
  return move(M.order, "purchase_orders", po, states.first(M.order, "terminal"));
}

/* ============================== goods receipt ============================== */
/* { warehouse_id?, note?, lines: [{ line_id, qty, lot?, batch?, expiry? }] } */
function receive(tid, id, input, actor) {
  const i = input || {}, t = N(tid), po = poRow(t, id);
  if (!states.is(M.order, po.status, "receivable")) fail("Goods are received only against a sent purchase order", 409);
  const wh = N(i.warehouse_id || po.warehouse_id) || (db().get("SELECT id FROM warehouses WHERE tenant_id=? AND active=1 AND deleted_at IS NULL ORDER BY id LIMIT 1", t) || {}).id;
  if (!wh || !db().get("SELECT id FROM warehouses WHERE id=? AND tenant_id=?", wh, t)) fail("Say which warehouse the goods arrived at");
  const byId = Object.fromEntries(linesOf(po.id).map(l => [l.id, l]));
  const got = (i.lines || []).filter(l => N(l.qty) > 0).map(l => {
    const pl = byId[N(l.line_id)] || fail("That line is not on this order: " + l.line_id);
    const qty = N(l.qty);
    if (!Number.isInteger(qty)) fail("Quantities are whole numbers");
    if (qty > pl.qty - pl.received) fail(`Only ${pl.qty - pl.received} of ${pl.product_id} are still to come`, 409);
    return { pl, qty, lot: String(l.lot || ""), batch: String(l.batch || ""), expiry: String(l.expiry || "") };
  });
  if (!got.length) fail("Nothing was received");
  return tx(() => {
    const value = r2(got.reduce((s, g) => s + g.qty * g.pl.unit_cost, 0));
    const r = RR().created(M.receipt, () => db().run("INSERT INTO goods_receipts(tenant_id,ref,po_id,warehouse_id,currency,value,status,note,received_by) VALUES(?,?,?,?,?,?,?,?,?)",
      t, nextRef(t, M.receipt, "goods_receipts"), po.id, wh, po.currency, value, states.initial(M.receipt), String(i.note || "").slice(0, 500), String(actor || "")));
    const rid = N(r.lastInsertRowid);
    for (const g of got) {
      db().run("INSERT INTO goods_receipt_lines(tenant_id,receipt_id,po_line_id,product_id,sku_id,qty,unit_cost,lot,batch,expiry) VALUES(?,?,?,?,?,?,?,?,?,?)", t, rid, g.pl.id, g.pl.product_id, g.pl.sku_id, g.qty, g.pl.unit_cost, g.lot, g.batch, g.expiry);
      db().run("UPDATE purchase_order_lines SET received=received+? WHERE id=?", g.qty, g.pl.id);
      require("./stock.js").receive(t, g.pl.product_id, g.pl.sku_id, wh, g.qty, { lot: g.lot, batch: g.batch, expiry: g.expiry });
      /* the units arrive with the order's price as their cost (lib/valuation.js) */
      require("./valuation.js").receive(t, { product_id: g.pl.product_id, sku_id: g.pl.sku_id, qty: g.qty, unit_cost: g.pl.unit_cost, currency: po.currency, ref: "receipt:" + rid });
    }
    const left = linesOf(po.id).some(l => l.received < l.qty);
    const to = states.first(M.order, left ? "partial" : "success");
    move(M.order, "purchase_orders", poRow(t, po.id), to);
    if (!left && po.request_id) { const pr = db().get("SELECT status FROM purchase_requests WHERE id=?", po.request_id); if (pr && states.is(M.request, pr.status, "placed")) require("./operations.js").advanceRequest(t, po.request_id, states.first(M.request, "success"), actor); }
    return receipt(t, rid);
  });
}
function receipt(tid, id) {
  const g = db().get("SELECT * FROM goods_receipts WHERE id=? AND tenant_id=?", N(id), N(tid)) || fail("No such receipt", 404);
  return { ...g, lines: db().all("SELECT * FROM goods_receipt_lines WHERE receipt_id=? ORDER BY id", g.id) };
}

/* ============================== supplier bills ============================== */
/* what has been received on an order and not yet billed, at the order's prices */
function unbilledValue(poId) {
  const received = db().get("SELECT COALESCE(SUM(received*unit_cost),0) v FROM purchase_order_lines WHERE po_id=?", N(poId)).v;
  const billed = db().get("SELECT COALESCE(SUM(matched),0) v FROM supplier_bills WHERE po_id=? AND status IN (" + states.tagged(M.bill, "approved").concat(states.tagged(M.bill, "held")).map(() => "?").join(",") + ")",
    N(poId), ...states.tagged(M.bill, "approved"), ...states.tagged(M.bill, "held")).v;
  return r2(received - billed);
}
/* { po_id, supplier_ref, net, tax?, due_at? } — matched against what was received and not yet billed */
function bill(tid, input, actor) {
  const i = input || {}, t = N(tid), po = poRow(t, i.po_id);
  if (states.is(M.order, po.status, "void")) fail("This order was cancelled", 409);
  const sup = supplierOf(t, po.supplier_id);
  const supplierRef = String(i.supplier_ref || "").trim();
  if (!supplierRef) fail("Give the supplier's own invoice number");
  if (db().get("SELECT ref FROM supplier_bills WHERE tenant_id=? AND supplier_id=? AND supplier_ref=?", t, sup.id, supplierRef)) fail("This supplier's invoice " + supplierRef + " is already recorded", 409, "bill_duplicate");
  const net = r2(i.net), tax = r2(i.tax || 0);
  if (!(net > 0) || tax < 0) fail("A bill has a net amount above zero and tax of zero or more");
  const open = unbilledValue(po.id);
  if (!(open > 0)) fail("Nothing received on this order is waiting to be billed", 409);
  const matched = Math.min(net, open), variance = r2(net - matched);
  const over = Math.abs(variance) > open * SEED.matchTolerancePct / 100 + 0.005;
  const status = over ? states.first(M.bill, "held") : states.first(M.bill, "approved");
  const days = SEED.paymentTermsDays[sup.payment_terms] != null ? SEED.paymentTermsDays[sup.payment_terms] : 30;
  const due = i.due_at || new Date(Date.now() + days * 86400e3).toISOString().slice(0, 10);
  return tx(() => {
    const r = RR().created(M.bill, () => db().run("INSERT INTO supplier_bills(tenant_id,ref,supplier_id,po_id,supplier_ref,currency,net,tax,gross,matched,variance,status,hold_reason,due_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
      t, nextRef(t, M.bill, "supplier_bills"), sup.id, po.id, supplierRef, po.currency, net, tax, r2(net + tax), r2(matched), variance, status,
      over ? `Billed ${net} against ${open} received and not yet billed (more than ${SEED.matchTolerancePct}% apart)` : "", due));
    return billRow(t, N(r.lastInsertRowid));
  });
}
const billRow = (tid, id) => db().get("SELECT * FROM supplier_bills WHERE id=? AND tenant_id=?", N(id), N(tid)) || fail("No such bill", 404);
function release(tid, id, actor, reason) {
  if (!String(reason || "").trim()) fail("Say why the bill is approved despite the difference");
  const b = billRow(tid, id);
  if (!states.is(M.bill, b.status, "held")) fail("Only a held bill is released", 409);
  return move(M.bill, "supplier_bills", b, states.first(M.bill, "approved"), { released_by: String(actor || "").slice(0, 120), hold_reason: b.hold_reason + " — released: " + String(reason).slice(0, 300) });
}
function pay(tid, id) {
  const b = billRow(tid, id);
  if (!states.is(M.bill, b.status, "payable")) fail("Only an approved, unpaid bill is paid", 409);
  return move(M.bill, "supplier_bills", b, states.first(M.bill, "success"));
}
function voidBill(tid, id) {
  const b = billRow(tid, id);
  return move(M.bill, "supplier_bills", b, states.first(M.bill, "void"));
}
function bills(tid, f) {
  const o = f || {};
  return db().all(`SELECT b.*, s.name supplier, po.ref po_ref FROM supplier_bills b JOIN suppliers s ON s.id=b.supplier_id LEFT JOIN purchase_orders po ON po.id=b.po_id
     WHERE b.tenant_id=? AND (?='' OR b.status=?) ORDER BY b.id DESC LIMIT 300`, N(tid), o.status || "", o.status || "").map(b => ({ ...b, actions: billActions(b) }));
}
/* what is owed to each supplier, by how overdue it is */
function payables(tid) {
  const today = new Date().toISOString().slice(0, 10), pay = states.tagged(M.bill, "payable");
  const rows = db().all(`SELECT b.*, s.name supplier FROM supplier_bills b JOIN suppliers s ON s.id=b.supplier_id WHERE b.tenant_id=? AND b.status IN (${pay.map(() => "?").join(",")})`, N(tid), ...pay);
  const by = {};
  for (const b of rows) {
    const k = b.supplier + "|" + b.currency, late = b.due_at && b.due_at < today ? Math.floor((Date.parse(today) - Date.parse(b.due_at)) / 86400e3) : 0;
    const x = by[k] = by[k] || { supplier: b.supplier, currency: b.currency, current: 0, d1_30: 0, d31_60: 0, d60plus: 0, total: 0 };
    const bucket = late <= 0 ? "current" : late <= 30 ? "d1_30" : late <= 60 ? "d31_60" : "d60plus";
    x[bucket] = r2(x[bucket] + b.gross); x.total = r2(x.total + b.gross);
  }
  return Object.values(by);
}
module.exports = { createOrder, order, orders, send, cancel, close, receive, receipt, bill, release, pay, voidBill, bills, payables, unbilledValue, SEED };
