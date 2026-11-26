/* LUXORA Platform — refunds: giving back money an order took, in whole or in part.

   Money goes back the way it came: through the gateway for a live payment, recorded for one that
   was simulated or settled offline, and to the shopper's wallet for what they paid from a balance.
   Each refund is a row (payment_refunds). The amount is claimed on the payment before the gateway
   is asked — two refunds can never together exceed what was paid — and released when the gateway
   refuses, so the row says what is still owed and staff can send it again. */
"use strict";

const db = () => require("./db.js");
const states = require("./states.js");
const connect = () => require("./connect.js");
const fail = (msg, status) => Object.assign(new Error(msg), { status: status || 400 });
const r2 = n => +Number(n || 0).toFixed(4);
const tagged = tag => { const xs = states.tagged("payment", tag); return { sql: "(" + (xs.length ? xs.map(() => "?").join(",") : "NULL") + ")", args: xs }; };

const left = p => Math.max(0, r2(Number(p.amount) - Number(p.refunded || 0)));
const paymentsOf = (tid, orderId) => { const rf = tagged("refundable"); return db().all("SELECT * FROM payments WHERE tenant_id=? AND order_id=? AND status IN " + rf.sql + " ORDER BY id", Number(tid), Number(orderId), ...rf.args); };

function credentials(tid, gateway) {
  const row = db().get("SELECT config FROM tenant_gateways WHERE tenant_id=? AND provider_id=?", Number(tid), String(gateway));
  return row ? require("./security.js").unsealConfig(Number(tid), String(gateway), row.config || "{}") : null;
}
/* refund `amount` of a payment (all that is left when omitted). `manual` records one already made
   in the gateway's own dashboard. */
async function refund(tid, payment, amount, opts) {
  const o = opts || {}, D = db();
  const p = D.get("SELECT * FROM payments WHERE id=? AND tenant_id=?", Number(payment.id), Number(tid));
  if (!p) throw fail("Unknown payment", 404);
  if (!states.is("payment", p.status, "refundable")) throw fail("Only captured payments can be refunded");
  const amt = amount == null ? left(p) : r2(amount);
  if (!(amt > 0)) throw fail("There is nothing left to refund on this payment", 409);
  const rf = tagged("refundable");
  const claim = require("./row-records.js").change("payment", p.id, () => D.run("UPDATE payments SET refunded=COALESCE(refunded,0)+? WHERE id=? AND COALESCE(refunded,0)+?<=amount+0.0001 AND status IN " + rf.sql, amt, p.id, amt, ...rf.args));
  if (!claim.changes) throw fail("A refund cannot be more than what is left of the payment (" + left(p) + " " + (p.currency || "") + ")", 409);
  const rowId = Number(D.run("INSERT INTO payment_refunds(tenant_id,payment_id,order_id,amount,currency,reason,actor,done) VALUES(?,?,?,?,?,?,?,0)",
    p.tenant_id, p.id, p.order_id, amt, p.currency || "", String(o.reason || "").slice(0, 200), String(o.actor || "").slice(0, 120)).lastInsertRowid);
  const refuse = (msg, status) => {
    require("./row-records.js").change("payment", p.id, () => D.run("UPDATE payments SET refunded=MAX(0,COALESCE(refunded,0)-?) WHERE id=?", amt, p.id));
    D.run("UPDATE payment_refunds SET error=? WHERE id=?", String(msg).slice(0, 300), rowId);
    return Object.assign(fail(msg, status), { refundId: rowId });
  };
  let out = null;
  if (p.live && !o.manual) {
    const cfg = credentials(tid, p.gateway);
    if (!cfg || !p.provider_payment_id) throw refuse("This payment can't be refunded through " + p.gateway + " from here — refund it in the gateway's dashboard, then record it with manual: true", 409);
    const r = await connect().refund({ provider: p.gateway, config: cfg, paymentId: p.provider_payment_id, amount: amt, currency: p.currency, idempotency: "refund-" + rowId });
    if (!r.live) throw refuse("Refund not sent (" + (r.reason || "gateway offline") + ")", 503);
    if (!r.ok || states.has("payment", r.status) && states.is("payment", r.status, "failure")) throw refuse("The gateway refused the refund: " + (r.error || r.status), 502);
    out = { id: r.id, status: r.status };
  }
  D.run("UPDATE payment_refunds SET done=1, gateway_ref=? WHERE id=?", out ? String(out.id || "") : "", rowId);
  const now = D.get("SELECT * FROM payments WHERE id=?", p.id);
  if (left(now) <= 0.0001) require("./row-records.js").change("payment", p.id, () => D.run("UPDATE payments SET status=? WHERE id=? AND status IN " + rf.sql, states.first("payment", "reversed"), p.id, ...rf.args));
  return { id: rowId, amount: amt, gateway: out, full: left(now) <= 0.0001 };
}
/* give back `amount` of an order, in the order's own currency: from its payments first, the rest to
   the shopper's wallet, where what they spent from a balance came from. What could not be sent is
   returned as `owed` with its reason — never reported as refunded. */
/* wallets are in the store's own currency: an amount of the order is converted back at the order's own rate */
function toWallet(tid, order, amount, o) {
  const base = +(Number(amount) / (Number(order.fx) || 1)).toFixed(2);
  if (base > 0) require("./offers.js").credit(Number(tid), order.owner, base, "refund", "refund:order:" + order.num + ":" + (o.key || "part"), null, "checkout");
}
async function refundOrder(tid, order, amount, opts) {
  const o = opts || {};
  let need = r2(amount), sent = 0, wallet = 0; const owed = [];
  for (const p of paymentsOf(tid, order.id)) {
    if (need <= 0.0001) break;
    const n = Math.min(need, left(p));
    if (!(n > 0)) continue;
    need = r2(need - n);
    try {
      await refund(tid, p, n, o.credit ? { ...o, manual: true } : o);
      if (o.credit) { toWallet(tid, order, n, o); wallet = r2(wallet + n); } else sent = r2(sent + n);
    }
    catch (e) { if (!e.status) console.error("refund:", e.message); owed.push({ payment: p.id, amount: n, reason: e.message }); }
  }
  const spent = r2(Number(order.gift_used || 0) - Number(order.gift_returned || 0));
  if (need > 0.0001 && spent > 0) {
    const n = r2(Math.min(need, spent));
    toWallet(tid, order, n, o); wallet = r2(wallet + n);
    require("./orders.js").giftReturned(order.id, n);
  }
  return { sent, wallet, owed };
}
/* a payment that has not been taken is closed, so nothing is collected for a cancelled order */
function closePending(order) {
  const aw = states.tagged("payment", "awaiting");
  if (!aw.length) return;
  require("./row-records.js").changeWhere("payment", "tenant_id=? AND order_id=?", [order.tenant_id, order.id], () => db().run("UPDATE payments SET status=? WHERE tenant_id=? AND order_id=? AND live=0 AND status IN (" + aw.map(() => "?").join(",") + ")", states.first("payment", "failure"), order.tenant_id, order.id, ...aw));
}
const listFor = (tid, orderId) => db().all("SELECT * FROM payment_refunds WHERE tenant_id=? AND order_id=? ORDER BY id", Number(tid), Number(orderId));
/* refunds that were promised but not sent, for staff to send again */
const owing = tid => db().all("SELECT r.*, o.num order_num, p.gateway FROM payment_refunds r JOIN payments p ON p.id=r.payment_id LEFT JOIN orders o ON o.id=r.order_id WHERE r.tenant_id=? AND r.done=0 AND COALESCE(p.refunded,0)<p.amount AND o.status IN (" + states.tagged("order", "void").map(() => "?").join(",") + ") ORDER BY r.id DESC LIMIT 200", Number(tid), ...states.tagged("order", "void"));

module.exports = { closePending, refund, refundOrder, left, paymentsOf, listFor, owing };
