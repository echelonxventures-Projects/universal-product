/* LUXORA Platform — an order after checkout: moving it on and cancelling it.

   Every way an order's status changes (the shopper's own cancel, the order screens, the generic
   record editor, a failed payment) comes through here, so the same things always follow. An order
   that becomes void gives its stock back, reverses its offers, returns what was spent from a
   balance and refunds what was paid; a void order never comes back to life. What each state means
   is asked of the `order` machine by tag, never by name. */
"use strict";

const db = () => require("./db.js");
const states = require("./states.js");
const refunds = require("./refunds.js");
const stock = require("./stock.js");
const tell = (...a) => require("./tell.js").tell(...a);
const fail = (msg, status) => Object.assign(new Error(msg), { status: status || 400 });
const r2 = n => +Number(n || 0).toFixed(2);

const is = (o, tag) => states.has("order", o.status) && states.is("order", o.status, tag);
const orderOf = (tid, id) => db().get("SELECT * FROM orders WHERE id=? AND tenant_id=?", Number(id), Number(tid));
/* may the shopper still cancel it themselves: it may be cancelled, and it has not been handed over */
const shopperCanCancel = o => is(o, "cancellable") && !is(o, "dispatched");
/* may something in it be returned: it was handed over and is not void */
const returnable = o => is(o, "dispatched") && !is(o, "void");
function write(order, to) {
  const { patch } = states.apply("order", { tenantId: order.tenant_id, from: order.status, to, row: order });
  const cols = Object.keys(patch);
  /* the row and the order's record on the kernel in one transaction (lib/order-records.js) */
  require("./order-records.js").change(order.id, () => {
    const r = db().run("UPDATE orders SET " + cols.map(c => c + "=?").join(", ") + " WHERE id=? AND tenant_id=? AND status=?", ...cols.map(c => patch[c]), order.id, order.tenant_id, order.status);
    if (!r.changes) throw fail("This order has just changed — reload it", 409);
  });
  require("./features.js").moved({ tid: order.tenant_id, order, to });
}
/* what checkout took besides money: the shelf, the balance, the offers */
function release(order, reason) {
  stock.giveBack(order.tenant_id, order.id);
  if (Number(order.gift_used) > 0 && !(Number(order.gift_returned) > 0)) {
    try {
      const back = require("./wallet.js").giveBackOrder(order.tenant_id, order.owner, "order:" + order.num, reason);
      if (back.length) db().run("UPDATE orders SET gift_returned=gift_used WHERE id=?", order.id);
    } catch (e) { console.error("gift give-back:", e.message); }
  }
  try { require("./offers.js").reverseRedemption(order.tenant_id, { order_id: order.id, order_num: order.num }); } catch (e) { console.error("offer reversal:", e.message); }
}
/* the money an order's payments still hold */
const held = order => refunds.paymentsOf(order.tenant_id, order.id).reduce((n, p) => n + refunds.left(p), 0);

async function cancel(tid, order, opts) {
  const o = opts || {};
  if (is(order, "void")) throw fail("This order is already cancelled", 409);
  if (o.byShopper && !shopperCanCancel(order)) throw fail("This order cannot be cancelled — it is already on its way. You can return it once it arrives.", 409);
  write(order, o.to || states.first("order", "aborted"));
  require("./order-records.js").change(order.id, () => db().run("UPDATE orders SET cancel_reason=? WHERE id=?", String(o.reason || "").slice(0, 200), order.id));
  release(order, "order cancelled");
  refunds.closePending(order);
  const due = held(order);
  const money = due > 0 ? await refunds.refundOrder(tid, order, due, { reason: o.reason || "order cancelled", actor: o.actor }) : { sent: 0, wallet: 0, owed: [] };
  const cur = order.currency || "";
  const owed = r2(money.owed.reduce((n, x) => n + x.amount, 0));
  const L = require("./letters.js"), amt = n => (n > 0 ? r2(n) + " " + cur : "");
  const w = L.write("order_cancelled", L.langOf(tid, { owner: order.owner, order }), { num: order.num, sent: amt(money.sent), owed: amt(owed), balance: amt(Number(order.gift_used)) });
  tell(tid, order.owner, "order_cancelled", w.subject, w.text, "orders.html", { to: order.email });
  if (owed > 0 && o.notify) o.notify("Refund owed for " + order.num, owed + " " + cur + " — " + money.owed[0].reason);
  return { refunded: r2(money.sent), owed, reasons: money.owed.map(x => x.reason) };
}
/* move an order on; a move to a void state is a cancellation, with everything that follows */
async function setStatus(tid, order, to, opts) {
  if (!states.has("order", to)) throw fail("Invalid status");
  if (to === order.status) return { unchanged: true };
  if (is(order, "void")) throw fail("A cancelled order cannot be reopened — its stock and money have gone back", 409);
  if (states.is("order", to, "void")) return cancel(tid, order, { ...(opts || {}), to });
  if (is(order, "awaiting_payment") && !(opts || {}).force) throw fail("This order is still waiting for its payment", 409);
  write(order, to);
  if (states.is("order", to, "fulfilled")) require("./order-records.js").change(order.id, () => db().run("UPDATE orders SET delivered_at=COALESCE(delivered_at, datetime('now')) WHERE id=?", order.id));
  if (states.is("order", to, "dispatched")) {
    const d = states.display("order", to);
    const L = require("./letters.js"), w = L.write("order_moved", L.langOf(tid, { owner: order.owner, order }), { num: order.num, state: d.label });
    tell(tid, order.owner, "order_" + to, w.subject, w.text, "orders.html", { to: order.email });
  }
  return { ok: true };
}
/* the order's payment failed or never came: it is void and what it took goes back */
function paymentFailed(tid, order, reason) {
  if (is(order, "void")) return;
  write(order, states.first("order", "aborted"));
  release(order, reason || "payment failed");
}

/* an amount spent from a balance on this order has gone back to the shopper's wallet */
function giftReturned(orderId, amount) { db().run("UPDATE orders SET gift_returned=COALESCE(gift_returned,0)+? WHERE id=?", amount, Number(orderId)); }

/* the generic record editor moves an order through the same door */
const entity = require("./entity.js");
entity.mover("order", async (tid, row, to, opts) => setStatus(tid, row, to, opts));

module.exports = { cancel, setStatus, paymentFailed, giftReturned, shopperCanCancel, returnable, orderOf };
