/* LUXORA Platform — returns: what a shopper sends back from an order, and what they get for it.

   A return is checked against the order it comes from: the item was bought, was handed over, has
   not already come back, and is inside the store's return period. Reaching the state that means
   refunded gives the money back first (lib/refunds.js) and the item to the shelf (lib/stock.js); a
   refund that cannot be sent leaves the return where it was. What each state means is asked of the
   `return` machine by tag. */
"use strict";

const db = () => require("./db.js");
const states = require("./states.js");
const refunds = require("./refunds.js");
const stock = require("./stock.js");
const { orderOf, returnable } = require("./orders.js");
const tell = (...a) => require("./tell.js").tell(...a);
const fail = (msg, status) => Object.assign(new Error(msg), { status: status || 400 });
const r2 = n => +Number(n || 0).toFixed(2);

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
  const days = Number(require("./settings.js").load(tid).commerce.returnDays);
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
    if (o.restock !== false) stock.giveBack(tid, order.id, ret.product_id, ret.qty * stock.perUnit(tid, order.id, ret.product_id));
    tell(tid, order.owner, "return_update", "Return " + ret.ref + " refunded", r2(money.sent + money.wallet) + " " + (order.currency || "") + " has been refunded for your return.", "orders.html", { to: order.email });
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
  if (order) tell(tid, order.owner, "return_update", "Return " + ret.ref + ": " + states.display("return", to).label, "Your return " + ret.ref + " is now: " + states.display("return", to).label + ".", "orders.html", { to: order.email });
  return { ok: true };
}

/* what was decided about the item, kept on the return */
function note(tid, id, value) { db().run("UPDATE returns SET note=? WHERE id=? AND tenant_id=?", JSON.stringify(value || {}), Number(id), Number(tid)); }

/* the generic record editor moves a return through the same door */
require("./entity.js").mover("ret", async (tid, row, to, opts) => setReturn(tid, row, to, opts));

module.exports = { requestReturn, setReturn, remaining, worth, note };
