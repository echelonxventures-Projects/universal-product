/* LUXORA Platform — Substitutions: what happens when an item is unavailable at picking.
   For each line, the shopper chooses a policy — a substitutionPolicies row declaring whether
   it allows a substitute at all, whether one is applied without asking, and whether the shopper
   names the item — and it rides on the bag line as its `substitute` term (lib/lineterms.js).
   At picking, staff either propose a substitute or mark the line unavailable. A proposal the
   policy accepts on its own is applied at once; otherwise the shopper accepts or rejects it.
   A cheaper substitute refunds the difference to the shopper's wallet; a dearer one is charged
   only where the store allows it; a rejected substitute or an unavailable line is refunded.
   Every decision is the `substitution` state machine. Capability: substitutions. */
"use strict";

const db = () => require("./db.js");
const caps = () => require("./capabilities.js");
const reg = () => require("./parity-registries.js");
const states = require("./states.js");
const lineterms = require("./lineterms.js");
const fail = lineterms.fail;
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };
const rows = name => reg().list(name).map(x => (typeof x === "string" ? { key: x, name: x } : x)).filter(x => x && x.key);
const policyOf = key => rows("substitutionPolicies").find(r => r.key === String(key == null ? "" : key)) || null;
const tell = (...a) => require("./tell.js").tell(...a);

function params(tid) {
  const P = caps().cap(tid, "substitutions");
  if (!Object.keys(P).length) throw fail("Substitutions are not available in this store", 403);
  return P;
}
const product = (tid, id) => db().get("SELECT * FROM products WHERE tenant_id=? AND id=? AND lifecycle='published' AND deleted_at IS NULL", Number(tid), String(id || ""));

/* ---------- the line term: { policy, product_id? } ---------- */
lineterms.register("substitute", {
  atom: "substitutions",
  clean: (ctx, value) => {
    const v = value && typeof value === "object" ? value : { policy: value };
    const pol = policyOf(v.policy);
    if (!pol) throw fail("Unknown substitution choice");
    if (!pol.needs_item) return { policy: pol.key };
    const sub = product(ctx.tid, v.product_id);
    if (!sub || sub.id === ctx.product.id) throw fail("Name another available item to substitute");
    return { policy: pol.key, product_id: sub.id };
  },
  price: (ctx, value) => {
    const pol = policyOf(value.policy);
    const sub = value.product_id ? db().get("SELECT title FROM products WHERE tenant_id=? AND id=?", Number(ctx.tid), value.product_id) : null;
    return { label: "If unavailable: " + (pol ? pol.name : value.policy) + (sub ? " — " + sub.title : "") };
  }
});

/* ---------- picking ---------- */
function lineOf(tid, orderId, productId) {
  const it = db().get("SELECT oi.*, o.owner, o.num, o.fx FROM order_items oi JOIN orders o ON o.id=oi.order_id WHERE o.id=? AND o.tenant_id=? AND oi.product_id=?", Number(orderId), Number(tid), String(productId));
  if (!it) throw fail("That item is not on this order", 404);
  const t = J(it.terms, {});
  const pref = (t.values || {}).substitute || null;
  return { ...it, pref, policy: pref ? policyOf(pref.policy) : (rows("substitutionPolicies").find(r => r.default) || null) };
}
function present(s) { return { ...s, state: states.display("substitution", s.status), next: states.next("substitution", s.status), awaiting: states.is("substitution", s.status, "awaiting_shopper") }; }
function write(s, to, patch) {
  const mv = states.apply("substitution", { tenantId: s.tenant_id, from: s.status, to, row: s });
  const p = Object.assign({}, mv.patch, patch || {});
  const cols = Object.keys(p);
  db().run("UPDATE order_substitutions SET " + cols.map(k => k + "=?").join(", ") + " WHERE id=?", ...cols.map(k => p[k]), s.id);
  return db().get("SELECT * FROM order_substitutions WHERE id=?", s.id);
}
/* the money side of a decision: a refund to the shopper's wallet, recorded on the row. Order
   lines are priced in the currency the shopper paid in; the wallet holds the store's base
   currency, so the refund is converted back by the order's own rate */
function settle(tid, s, line, refund) {
  const P = caps().cap(Number(tid), "substitutions");
  const base = +(refund / (Number(line.fx) || 1)).toFixed(2);
  if (base > 0) require("./offers.js").credit(Number(tid), line.owner, base, String((P && P.refund_kind) || ""), "substitution:" + s.id + ":order:" + line.order_id, null, "substitutions");
  return refund;
}
/* staff, at picking: the order's lines with each shopper's choice */
function forOrder(tid, orderId) {
  params(tid);
  const o = db().get("SELECT id, num FROM orders WHERE id=? AND tenant_id=?", Number(orderId), Number(tid));
  if (!o) throw fail("Order not found", 404);
  const lines = db().all("SELECT product_id, qty, price, terms FROM order_items WHERE order_id=?", o.id).map(it => {
    const pref = (J(it.terms, {}).values || {}).substitute || null;
    const p = db().get("SELECT title FROM products WHERE tenant_id=? AND id=?", Number(tid), it.product_id) || {};
    return { product_id: it.product_id, title: p.title, qty: it.qty, price: it.price, preference: pref, policy: pref ? policyOf(pref.policy) : null };
  });
  return { order: o, lines, substitutions: db().all("SELECT * FROM order_substitutions WHERE tenant_id=? AND order_id=? ORDER BY id", Number(tid), o.id).map(present) };
}
/* propose a substitute for a line — applied at once where the shopper's policy says so */
function propose(tid, orderId, productId, input) {
  const P = params(tid);
  const line = lineOf(tid, orderId, productId);
  const pol = line.policy;
  if (!pol || !pol.allows) throw fail("The shopper asked not to substitute this item — mark it unavailable instead", 409);
  const i = input || {};
  const subId = pol.needs_item && line.pref ? line.pref.product_id : i.substitute_id;
  const sub = product(tid, subId);
  if (!sub) throw fail("Name an available substitute", 404);
  const qty = Math.max(1, Math.min(line.qty, Math.floor(Number(i.qty) || line.qty)));
  const subUnit = +Number(i.substitute_unit != null ? i.substitute_unit : sub.price).toFixed(2);
  const r = db().run("INSERT INTO order_substitutions(tenant_id,order_id,product_id,substitute_id,qty,original_unit,substitute_unit,status) VALUES(?,?,?,?,?,?,?,?)",
    Number(tid), line.order_id, line.product_id, sub.id, qty, Number(line.price), subUnit, states.initial("substitution"));
  let s = db().get("SELECT * FROM order_substitutions WHERE id=?", r.lastInsertRowid);
  if (pol.auto_accept) s = apply(tid, s, line, P);
  else tell(tid, line.owner, "substitution", "A substitute for your order " + line.num, sub.title + " instead of an unavailable item — accept or reject it in Your Orders.", "orders.html");
  return present(s);
}
function apply(tid, s, line, P) {
  const diff = +((Number(s.original_unit) - Number(s.substitute_unit)) * s.qty).toFixed(2);
  const refund = diff > 0 ? diff : 0;
  if (diff < 0 && !P.charge_more) s.substitute_unit = s.original_unit;
  settle(tid, s, line, refund);
  return write(s, states.actionTarget("substitution", "apply"), { refund });
}
/* the line cannot be picked and the shopper wants no substitute (or rejected one): refund it */
function unavailable(tid, orderId, productId) {
  params(tid);
  const line = lineOf(tid, orderId, productId);
  const r = db().run("INSERT INTO order_substitutions(tenant_id,order_id,product_id,qty,original_unit,status) VALUES(?,?,?,?,?,?)",
    Number(tid), line.order_id, line.product_id, line.qty, Number(line.price), states.initial("substitution"));
  const s = db().get("SELECT * FROM order_substitutions WHERE id=?", r.lastInsertRowid);
  const refund = settle(tid, s, line, +(Number(line.price) * line.qty).toFixed(2));
  tell(tid, line.owner, "substitution", "An item on order " + line.num + " was unavailable", refund + " is back in your wallet.", "orders.html");
  return present(write(s, states.actionTarget("substitution", "refund"), { refund }));
}
/* the shopper answers a proposal on their own order */
function decide(tid, owner, id, action) {
  const P = params(tid);
  const s = db().get("SELECT * FROM order_substitutions WHERE id=? AND tenant_id=?", Number(id), Number(tid));
  if (!s) throw fail("Substitution not found", 404);
  const line = lineOf(tid, s.order_id, s.product_id);
  if (line.owner !== String(owner)) throw fail("Substitution not found", 404);
  if (!states.is("substitution", s.status, "awaiting_shopper")) throw fail("This substitution has already been decided", 409);
  const to = states.actionTarget("substitution", action);
  if (!to || !states.can("substitution", s.status, to)) throw fail("Accept or reject the substitute");
  if (states.is("substitution", to, "success")) return present(apply(tid, s, line, P));
  const rej = write(s, to);
  const refund = settle(tid, rej, line, +(Number(rej.original_unit) * rej.qty).toFixed(2));
  return present(write(rej, states.actionTarget("substitution", "refund"), { refund }));
}
function mine(tid, owner) {
  params(tid);
  return db().all("SELECT s.* FROM order_substitutions s JOIN orders o ON o.id=s.order_id WHERE s.tenant_id=? AND o.owner=? ORDER BY s.id DESC LIMIT 200", Number(tid), String(owner)).map(present);
}
function vocabulary() {
  return { policies: rows("substitutionPolicies"),
    actions: Object.entries(states.actions("substitution")).map(([verb, to]) => ({ verb, to, label: states.display("substitution", to).label })) };
}

module.exports = { forOrder, propose, unavailable, decide, mine, vocabulary };
