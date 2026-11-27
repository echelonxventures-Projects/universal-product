/* LUXORA Platform — purchasing domain routes (lib/purchasing.js; _registry/business-domains.json).
   Orders to suppliers, goods received against them and suppliers' bills. Every route belongs to the
   store's purchasing section (the Finance role holds it): a read grant lists, a write grant acts. */
"use strict";

module.exports = { domain: "purchasing", routes(kit) {
  const { T, actor, bad, json, logAction, requireAdmin } = kit;
  const P = () => require("../purchasing.js");
  const answer = (s, res, fn) => { if (!requireAdmin(s, res)) return; try { fn(); } catch (e) { bad(res, e.message, e.status || 400); } };
  const q = (url, k) => url.searchParams.get(k) || "";

  /* The store's purchase orders, newest first, each with its supplier; `status` and `supplier_id` narrow them. */
  function apiPurchaseOrders(req, res, url, s) { answer(s, res, () => json(res, 200, { orders: P().orders(T(s), { status: q(url, "status"), supplier_id: q(url, "supplier_id") }) })); }
  /* One purchase order: its lines (ordered, received, still to come), its receipts, its bills, and the value received and not yet billed. */
  function apiPurchaseOrder(req, res, url, s, body, id) { answer(s, res, () => json(res, 200, { order: P().order(T(s), id) })); }
  /* Drafts a purchase order: `supplier_id`, `warehouse_id`, an approved `request_id` if it fills one, `currency` (the supplier's by default) and `lines` of `{ product_id, sku_id, qty, unit_cost }`. */
  function apiPurchaseOrderCreate(req, res, url, s, body) { answer(s, res, () => { const o = P().createOrder(T(s), body || {}, actor(s)); logAction(s, "purchasing.order", "purchase_order", o.ref, { total: o.total }); json(res, 200, { order: o }); }); }
  /* Sends a drafted order to the supplier; a purchase request it fills becomes ordered. */
  function apiPurchaseOrderSend(req, res, url, s, body, id) { answer(s, res, () => { const o = P().send(T(s), id, actor(s)); logAction(s, "purchasing.send", "purchase_order", o.ref, {}); json(res, 200, { order: o }); }); }
  /* Cancels an order nothing has been received against. */
  function apiPurchaseOrderCancel(req, res, url, s, body, id) { answer(s, res, () => { const o = P().cancel(T(s), id); logAction(s, "purchasing.cancel", "purchase_order", o.ref, {}); json(res, 200, { order: o }); }); }
  /* Closes an order: what has not arrived will not be received. */
  function apiPurchaseOrderClose(req, res, url, s, body, id) { answer(s, res, () => { const o = P().close(T(s), id); logAction(s, "purchasing.close", "purchase_order", o.ref, {}); json(res, 200, { order: o }); }); }
  /* Records goods received against an order: `warehouse_id` and `lines` of `{ line_id, qty, lot, batch, expiry }`. The stock counts and the warehouse batch go up, and the books record the stock as received and not yet billed. */
  function apiPurchaseReceive(req, res, url, s, body, id) { answer(s, res, () => { const g = P().receive(T(s), id, body || {}, actor(s)); logAction(s, "purchasing.receive", "goods_receipt", g.ref, { value: g.value }); json(res, 200, { receipt: g }); }); }
  /* The store's supplier bills, newest first; `status` narrows them. */
  function apiSupplierBills(req, res, url, s) { answer(s, res, () => json(res, 200, { bills: P().bills(T(s), { status: q(url, "status") }) })); }
  /* Records a supplier's bill against an order: `po_id`, `supplier_ref` (their invoice number, once per supplier), `net`, `tax`, `due_at`. Matched against what was received and not yet billed: within the tolerance it is approved and owed; beyond it, held. */
  function apiSupplierBillCreate(req, res, url, s, body) { answer(s, res, () => { const b = P().bill(T(s), body || {}, actor(s)); logAction(s, "purchasing.bill", "supplier_bill", b.ref, { net: b.net, status: b.status }); json(res, 200, { bill: b }); }); }
  /* Releases a held bill with a `reason`: it is approved and owed, its difference a purchase price difference. */
  function apiSupplierBillRelease(req, res, url, s, body, id) { answer(s, res, () => { const b = P().release(T(s), id, actor(s), (body || {}).reason); logAction(s, "purchasing.release", "supplier_bill", b.ref, { reason: (body || {}).reason }); json(res, 200, { bill: b }); }); }
  /* Marks an approved bill paid: the books clear what is owed from the bank. */
  function apiSupplierBillPay(req, res, url, s, body, id) { answer(s, res, () => { const b = P().pay(T(s), id); logAction(s, "purchasing.pay", "supplier_bill", b.ref, { gross: b.gross }); json(res, 200, { bill: b }); }); }
  /* Voids a bill; an approved one's entry is undone in the books. */
  function apiSupplierBillVoid(req, res, url, s, body, id) { answer(s, res, () => { const b = P().voidBill(T(s), id); logAction(s, "purchasing.void", "supplier_bill", b.ref, {}); json(res, 200, { bill: b }); }); }
  /* What is owed to each supplier, by how overdue it is. */
  function apiPayables(req, res, url, s) { answer(s, res, () => json(res, 200, { payables: P().payables(T(s)) })); }

  return [
    ["GET /api/admin/purchasing/orders", apiPurchaseOrders],
    ["POST /api/admin/purchasing/orders", apiPurchaseOrderCreate],
    ["GET /api/admin/purchasing/orders/:id", (r, re, u, s, b, p) => apiPurchaseOrder(r, re, u, s, b, p)],
    ["POST /api/admin/purchasing/orders/:id/send", (r, re, u, s, b, p) => apiPurchaseOrderSend(r, re, u, s, b, p)],
    ["POST /api/admin/purchasing/orders/:id/cancel", (r, re, u, s, b, p) => apiPurchaseOrderCancel(r, re, u, s, b, p)],
    ["POST /api/admin/purchasing/orders/:id/close", (r, re, u, s, b, p) => apiPurchaseOrderClose(r, re, u, s, b, p)],
    ["POST /api/admin/purchasing/orders/:id/receive", (r, re, u, s, b, p) => apiPurchaseReceive(r, re, u, s, b, p)],
    ["GET /api/admin/purchasing/bills", apiSupplierBills],
    ["POST /api/admin/purchasing/bills", apiSupplierBillCreate],
    ["POST /api/admin/purchasing/bills/:id/release", (r, re, u, s, b, p) => apiSupplierBillRelease(r, re, u, s, b, p)],
    ["POST /api/admin/purchasing/bills/:id/pay", (r, re, u, s, b, p) => apiSupplierBillPay(r, re, u, s, b, p)],
    ["POST /api/admin/purchasing/bills/:id/void", (r, re, u, s, b, p) => apiSupplierBillVoid(r, re, u, s, b, p)],
    ["GET /api/admin/purchasing/payables", apiPayables]
  ];
} };
