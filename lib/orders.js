/* LUXORA Platform — an order after checkout: moving it on, cancelling it, returning what it held.

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
  const r = db().run("UPDATE orders SET " + cols.map(c => c + "=?").join(", ") + " WHERE id=? AND tenant_id=? AND status=?", ...cols.map(c => patch[c]), order.id, order.tenant_id, order.status);
  if (!r.changes) throw fail("This order has just changed — reload it", 409);
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
/* a payment that has not been taken is closed, so nothing is collected for a cancelled order */
function closePending(order) {
  const aw = states.tagged("payment", "awaiting");
  if (!aw.length) return;
  db().run("UPDATE payments SET status=? WHERE tenant_id=? AND order_id=? AND live=0 AND status IN (" + aw.map(() => "?").join(",") + ")", states.first("payment", "failure"), order.tenant_id, order.id, ...aw);
}
/* the money an order's payments still hold */
const held = order => refunds.paymentsOf(order.tenant_id, order.id).reduce((n, p) => n + refunds.left(p), 0);

async function cancel(tid, order, opts) {
  const o = opts || {};
  if (is(order, "void")) throw fail("This order is already cancelled", 409);
  if (o.byShopper && !shopperCanCancel(order)) throw fail("This order cannot be cancelled — it is already on its way. You can return it once it arrives.", 409);
  write(order, o.to || states.first("order", "aborted"));
  db().run("UPDATE orders SET cancel_reason=? WHERE id=?", String(o.reason || "cancelled").slice(0, 200), order.id);
  release(order, "order cancelled");
  closePending(order);
  const due = held(order);
  const money = due > 0 ? await refunds.refundOrder(tid, order, due, { reason: o.reason || "order cancelled", actor: o.actor }) : { sent: 0, wallet: 0, owed: [] };
  const cur = order.currency || "";
  const owed = r2(money.owed.reduce((n, x) => n + x.amount, 0));
  tell(tid, order.owner, "order_cancelled", "Order " + order.num + " cancelled",
    "Your order has been cancelled." + (money.sent > 0 ? " " + r2(money.sent) + " " + cur + " is being refunded the way you paid." : "")
    + (owed > 0 ? " The store will refund " + owed + " " + cur + " to you." : "")
    + (Number(order.gift_used) > 0 ? " What you paid from your balance is back in your wallet." : ""), "orders.html");
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
  if (states.is("order", to, "fulfilled")) db().run("UPDATE orders SET delivered_at=COALESCE(delivered_at, datetime('now')) WHERE id=?", order.id);
  if (states.is("order", to, "dispatched")) {
    const d = states.display("order", to);
    tell(tid, order.owner, "order_" + to, "Order " + order.num + ": " + d.label, "Your order " + order.num + " is now: " + d.label + ".", "orders.html");
  }
  return { ok: true };
}
/* the order's payment failed or never came: it is void and what it took goes back */
function paymentFailed(tid, order, reason) {
  if (is(order, "void")) return;
  write(order, states.first("order", "aborted"));
  release(order, reason || "payment failed");
}

/* ---------- returns ---------- */
const closedUnpaid = s => states.is("return", s, "terminal") && !states.is("return", s, "refunded");
const openReturns = () => states.vocab("return").filter(s => !closedUnpaid(s));
/* how many of an item an order holds, and how many are already being or been returned */
function remaining(order, productId) {
  const bought = Number((db().get("SELECT COALESCE(SUM(qty),0) q FROM order_items WHERE order_id=? AND product_id=?", order.id, String(productId)) || {}).q) || 0;
  const xs = openReturns();
  const back = Number((db().get("SELECT COALESCE(SUM(qty),0) q FROM returns WHERE order_id=? AND product_id=? AND status IN (" + xs.map(() => "?").join(",") + ")", order.id, String(productId), ...xs) || {}).q) || 0;
  return Math.max(0, bought - back);
}
/* what one unit's share of the order came to, after discounts and with its tax — never the delivery fee */
function worth(order, productId, qty) {
  const items = db().all("SELECT product_id, qty, price FROM order_items WHERE order_id=?", order.id);
  const total = items.reduce((n, i) => n + Number(i.price) * Number(i.qty), 0);
  const line = items.filter(i => i.product_id === String(productId));
  const units = line.reduce((n, i) => n + Number(i.qty), 0);
  if (!units || !(total > 0)) return 0;
  const value = line.reduce((n, i) => n + Number(i.price) * Number(i.qty), 0) * (Number(qty) / units);
  const paid = Math.max(0, Number(order.total) + Number(order.gift_used || 0) - Number(order.ship_fee || 0));
  return r2(paid * value / total);
}
/* the shopper asks to return items of an order: one item, or (no item named) all that is left of it */
function requestReturn(tid, order, input) {
  const i = input || {};
  if (!returnable(order)) throw fail("This order cannot be returned yet — it has not been delivered", 409);
  const days = Number(require("./settings.js").getSettings(tid).commerce.returnDays);
  if (days > 0 && Date.now() > new Date(String(order.delivered_at || order.created_at).replace(" ", "T") + "Z").getTime() + days * 864e5 + (order.delivered_at ? 0 : Number(order.eta_days || 5) * 864e5))
    throw fail("The " + days + "-day return period for this order has ended", 409);
  const ids = i.product_id ? [String(i.product_id)] : [...new Set(db().all("SELECT product_id FROM order_items WHERE order_id=?", order.id).map(x => x.product_id))];
  const out = [];
  for (const id of ids) {
    const can = remaining(order, id);
    const qty = i.product_id ? Number(i.qty == null || i.qty === "" ? 1 : i.qty) : can;
    if (!i.product_id && !can) continue;
    if (!Number.isInteger(qty) || qty < 1 || qty > can) throw fail(can > 0 ? "You can return at most " + can + " of this item" : "There is none of that item left to return on this order", 409);
    const ref = "RET-" + require("node:crypto").randomBytes(4).toString("hex").toUpperCase();
    const r = db().run("INSERT INTO returns(tenant_id,ref,order_id,product_id,qty,reason,status) VALUES(?,?,?,?,?,?,?)", Number(tid), ref, order.id, id, qty, String(i.reason || "").slice(0, 500), states.initial("return"));
    out.push({ id: Number(r.lastInsertRowid), ref, product_id: id, qty, worth: worth(order, id, qty) });
  }
  if (!out.length) throw fail("There is nothing left to return on this order", 409);
  return out;
}
/* move a return on. Reaching the state that means refunded gives the money back first: when it
   cannot be sent, the return stays where it is. */
async function setReturn(tid, ret, to, opts) {
  const o = opts || {};
  if (!states.has("return", to)) throw fail("Invalid status");
  if (to === ret.status) return { unchanged: true };
  if (states.is("return", ret.status, "terminal")) throw fail("This return is closed", 409);
  const order = ret.order_id ? orderOf(tid, ret.order_id) : null;
  const claim = (from, next) => db().run("UPDATE returns SET status=? WHERE id=? AND tenant_id=? AND status=?", next, ret.id, Number(tid), from).changes;
  let money = null;
  if (states.is("return", to, "refunded")) {
    if (!order) throw fail("This return has no order to refund", 409);
    if (!claim(ret.status, to)) throw fail("This return has just changed — reload it", 409);
    const amount = o.amount != null ? r2(o.amount) : worth(order, ret.product_id, ret.qty);
    if (!(amount >= 0)) { claim(to, ret.status); throw fail("Invalid amount"); }
    money = amount > 0 ? await refunds.refundOrder(tid, order, amount, { reason: "return " + ret.ref, actor: o.actor, key: ret.ref, credit: o.credit }) : { sent: 0, wallet: 0, owed: [] };
    if (money.owed.length) { claim(to, ret.status); throw fail("Not refunded: " + money.owed[0].reason, 502); }
    if (o.restock !== false) stock.giveBack(tid, order.id, ret.product_id, ret.qty);
    tell(tid, order.owner, "return_update", "Return " + ret.ref + " refunded", r2(money.sent + money.wallet) + " " + (order.currency || "") + " has been refunded for your return.", "orders.html");
    /* the order's offers are reversed once all of it has come back */
    const done = states.tagged("return", "refunded");
    const all = db().all("SELECT product_id, SUM(qty) q FROM order_items WHERE order_id=? GROUP BY product_id", order.id).every(x =>
      Number(db().get("SELECT COALESCE(SUM(qty),0) q FROM returns WHERE order_id=? AND product_id=? AND status IN (" + done.map(() => "?").join(",") + ")", order.id, x.product_id, ...done).q) >= Number(x.q));
    if (all) states.apply("return", { tenantId: tid, from: ret.status, to, row: ret });
    return { refunded: r2(money.sent + money.wallet) };
  }
  const { patch } = states.apply("return", { tenantId: tid, from: ret.status, to, row: ret });
  const cols = Object.keys(patch);
  db().run("UPDATE returns SET " + cols.map(c => c + "=?").join(", ") + " WHERE id=? AND tenant_id=?", ...cols.map(c => patch[c]), ret.id, Number(tid));
  if (order) tell(tid, order.owner, "return_update", "Return " + ret.ref + ": " + states.display("return", to).label, "Your return " + ret.ref + " is now: " + states.display("return", to).label + ".", "orders.html");
  return { ok: true };
}

/* the generic record editor moves these two through the same door */
const entity = require("./entity.js");
entity.mover("order", async (tid, row, to, opts) => setStatus(tid, row, to, opts));
entity.mover("ret", async (tid, row, to, opts) => setReturn(tid, row, to, opts));

module.exports = { cancel, setStatus, paymentFailed, requestReturn, setReturn, shopperCanCancel, returnable, remaining, worth, orderOf };
