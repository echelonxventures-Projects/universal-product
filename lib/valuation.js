/* LUXORA Platform — stock valuation (owner Value).

   What each unit on hand cost is kept as cost layers: goods received from a supplier add a layer at
   the order's price (lib/purchasing.js); stock on hand that never had a cost is given one by an
   opening valuation. A unit that leaves — sold, or written off — takes its cost from the layers by
   the store's method (lib/seed/valuation.json; settings commerce.stockValuation): the oldest first
   (fifo), or the weighted average (the layers are evened out first). That cost posts to the books:
   cost of goods sold against inventory, or stock written off; a unit that comes back (a cancelled
   order, a returned item) goes back into a layer at the cost it left at, and the books reverse.

   Layers hold their value in whole minor units, so the sum of the layers is the books' inventory
   account to the cent (reconcile()). A unit with no cost — stock counted before valuation began —
   is the oldest stock: it leaves first, at no cost, and is reported — never guessed at. */
"use strict";

const db = () => require("./db.js");
const K = require("./kernel.js");
const SEED = require("./seed/valuation.json");
const B = () => require("./books.js");
const W = () => require("./wallet.js");
const fail = (msg, status) => { const e = new Error(msg); e.status = status || 400; throw e; };
const N = Number;
const tx = fn => K.internal.tx(fn);
const dec = unit => W().unitOf(unit).decimals;
const toMinor = (v, unit) => Math.round(N(v) * Math.pow(10, dec(unit)));
const toMajor = (m, unit) => +(m / Math.pow(10, dec(unit))).toFixed(dec(unit));
const A = SEED.accounts;

function method(tid) {
  const m = String(require("./settings.js").get(N(tid), "commerce.stockValuation") || SEED.methods[0]);
  return SEED.methods.includes(m) ? m : SEED.methods[0];
}
const skuSql = "COALESCE(sku_id,0)=COALESCE(?,0)";
/* an item's cost is kept on its variant: the one named, else the item's only active one */
function variant(tid, productId, skuId) {
  if (skuId) return N(skuId);
  const only = db().all("SELECT id FROM skus WHERE tenant_id=? AND product_id=? AND active=1 ORDER BY id LIMIT 2", N(tid), String(productId));
  return only.length === 1 ? only[0].id : null;
}
const open = (tid, productId, skuId) => db().all(`SELECT * FROM cost_layers WHERE tenant_id=? AND product_id=? AND ${skuSql} AND remaining>0 ORDER BY id`, N(tid), String(productId), skuId || null);
/* average: every open layer of the item, per currency, is given the same unit cost; the value is shared
   out in whole minor units, the last layer taking the remainder, so the total never moves */
function even(tid, productId, skuId) {
  const by = {};
  for (const l of open(tid, productId, skuId)) (by[l.currency] = by[l.currency] || []).push(l);
  for (const ls of Object.values(by)) {
    if (ls.length < 2) continue;
    const q = ls.reduce((s, l) => s + l.remaining, 0), v = ls.reduce((s, l) => s + l.value_minor, 0);
    let left = v;
    ls.forEach((l, i) => { const share = i === ls.length - 1 ? left : Math.round(v * l.remaining / q); left -= share; db().run("UPDATE cost_layers SET value_minor=? WHERE id=?", share, l.id); });
  }
}
function post(tid, unit, debit, credit, minor, op, ref, idem) {
  if (!minor) return;
  B().post(tid, { unit, lines: [{ account: debit, debit: minor }, { account: credit, credit: minor }], op, ref: ref || "", memo: SEED.labels[op], idem });
}

/* goods arriving with a cost: a new layer (the books already posted the receipt) */
function receive(tid, o0) {
  const o = { ...o0, sku_id: variant(tid, o0.product_id, o0.sku_id) }, qty = N(o.qty);
  if (!(qty > 0)) return null;
  const unit = String(o.currency).toUpperCase();
  return tx(() => {
    db().run("INSERT INTO cost_layers(tenant_id,product_id,sku_id,currency,qty,remaining,value_minor,source,ref) VALUES(?,?,?,?,?,?,?,?,?)",
      N(tid), String(o.product_id), o.sku_id || null, unit, qty, qty, toMinor(N(o.unit_cost) * qty, unit), o.source || "receipt", String(o.ref || ""));
    const id = N(db().get("SELECT last_insert_rowid() id").id);
    if (method(tid) === SEED.methods[1]) even(tid, o.product_id, o.sku_id);
    return id;
  });
}
/* units leaving: { product_id, sku_id, qty, kind: cogs | write_off, move_id?, ref? } — each takes its cost from the layers */
function issue(tid, o0) {
  const t = N(tid), o = { ...o0, sku_id: variant(tid, o0.product_id, o0.sku_id) }, kind = o.kind || "cogs";
  let left = N(o.qty);
  if (!(left > 0)) return { value: {}, unvalued: 0 };
  return tx(() => {
    if (method(t) === SEED.methods[1]) even(t, o.product_id, o.sku_id);
    const value = {};
    /* units with no cost were on hand before valuation began: they are the oldest, so they leave
       first, at no cost, and are counted (the count has already been lowered by what left) */
    const now = o.sku_id ? db().get("SELECT stock FROM skus WHERE id=?", N(o.sku_id)) : db().get("SELECT stock FROM products WHERE tenant_id=? AND id=?", t, String(o.product_id));
    const after = Math.max(0, N((now || {}).stock) || 0);
    const layered = db().get(`SELECT COALESCE(SUM(remaining),0) q FROM cost_layers WHERE tenant_id=? AND product_id=? AND ${skuSql}`, t, String(o.product_id), o.sku_id || null).q;
    const bare = Math.min(left, Math.max(0, after + left - layered));
    if (bare > 0) { db().run("INSERT INTO cost_issues(tenant_id,layer_id,move_id,kind,product_id,sku_id,currency,qty,value_minor,ref) VALUES(?,NULL,?,?,?,?,NULL,?,0,?)", t, o.move_id || null, kind, String(o.product_id), o.sku_id || null, bare, String(o.ref || "")); left -= bare; }
    const unvalued = bare;
    for (const l of open(t, o.product_id, o.sku_id)) {
      if (left <= 0) break;
      const n = Math.min(left, l.remaining), v = n === l.remaining ? l.value_minor : Math.round(l.value_minor * n / l.remaining);
      db().run("UPDATE cost_layers SET remaining=remaining-?, value_minor=value_minor-? WHERE id=?", n, v, l.id);
      db().run("INSERT INTO cost_issues(tenant_id,layer_id,move_id,kind,product_id,sku_id,currency,qty,value_minor,ref) VALUES(?,?,?,?,?,?,?,?,?,?)", t, l.id, o.move_id || null, kind, String(o.product_id), o.sku_id || null, l.currency, n, v, String(o.ref || ""));
      value[l.currency] = (value[l.currency] || 0) + v; left -= n;
    }
    /* more left than the counts and layers hold (a count edited by hand): those, too, leave at no cost */
    if (left > 0) db().run("INSERT INTO cost_issues(tenant_id,layer_id,move_id,kind,product_id,sku_id,currency,qty,value_minor,ref) VALUES(?,NULL,?,?,?,?,NULL,?,0,?)", t, o.move_id || null, kind, String(o.product_id), o.sku_id || null, left, String(o.ref || ""));
    const key = o.move_id ? "move:" + o.move_id : "seq:" + K.lastSeq();
    for (const [unit, v] of Object.entries(value)) post(t, unit, kind === "write_off" ? A.writeOff : A.cogs, A.inventory, v, kind, o.ref, `valuation:${kind}:${key}:${unit}`);
    return { value: Object.fromEntries(Object.entries(value).map(([u, v]) => [u, toMajor(v, u)])), unvalued: unvalued + left };
  });
}
/* units of a stock move coming back: into a layer at the cost they left at, newest issue first */
function restore(tid, moveId, qty) {
  const t = N(tid);
  let left = N(qty);
  return tx(() => {
    const back = {};
    for (const i of db().all("SELECT * FROM cost_issues WHERE tenant_id=? AND move_id=? AND returned<qty ORDER BY id DESC", t, N(moveId))) {
      if (left <= 0) break;
      const n = Math.min(left, i.qty - i.returned);
      db().run("UPDATE cost_issues SET returned=returned+? WHERE id=?", n, i.id);
      left -= n;
      if (!i.layer_id) continue;
      const v = Math.round(i.value_minor * n / i.qty);
      db().run("INSERT INTO cost_layers(tenant_id,product_id,sku_id,currency,qty,remaining,value_minor,source,ref) VALUES(?,?,?,?,?,?,?,?,?)", t, i.product_id, i.sku_id, i.currency, n, n, v, "return", i.ref);
      back[i.currency] = (back[i.currency] || 0) + v;
      if (method(t) === SEED.methods[1]) even(t, i.product_id, i.sku_id);
    }
    for (const [unit, v] of Object.entries(back)) post(t, unit, A.inventory, A.cogs, v, "cogs_back", "", `valuation:back:${moveId}:${K.lastSeq()}:${unit}`);
    return back;
  });
}
/* stock counted before valuation began gets a cost: the units of the item not in any layer */
function opening(tid, input, actor) {
  const t = N(tid), i = input || {};
  const sid = variant(t, i.product_id, i.sku_id);
  const sku = sid ? db().get("SELECT id, product_id, stock FROM skus WHERE id=? AND tenant_id=?", sid, t) : null;
  const p = db().get("SELECT id, stock FROM products WHERE tenant_id=? AND id=?", t, String(sku ? sku.product_id : i.product_id || "")) || fail("No such product", 404);
  const unit = String(i.currency || require("./defaults.js").currency(t)).toUpperCase(), cost = N(i.unit_cost);
  if (!(cost >= 0) || i.unit_cost === undefined || i.unit_cost === "") fail("Give the unit cost");
  const onHand = N(sku ? sku.stock : p.stock), layered = db().get(`SELECT COALESCE(SUM(remaining),0) q FROM cost_layers WHERE tenant_id=? AND product_id=? AND ${skuSql}`, t, p.id, sku ? sku.id : null).q;
  const qty = onHand - layered;
  if (!(qty > 0)) fail("Every unit of this item on hand already has a cost", 409);
  return tx(() => {
    const id = receive(t, { product_id: p.id, sku_id: sku ? sku.id : null, qty, unit_cost: cost, currency: unit, source: "opening", ref: "opening:" + (actor || "") });
    post(t, unit, A.inventory, A.opening, toMinor(cost * qty, unit), "opening", p.id, `valuation:opening:${id}`);
    return { layer: id, qty, value: toMajor(toMinor(cost * qty, unit), unit), currency: unit };
  });
}
/* what the stock on hand is worth, per item and currency, and what has no cost yet */
function onHand(tid) {
  const t = N(tid);
  const rows = db().all("SELECT product_id, sku_id, currency, SUM(remaining) qty, SUM(value_minor) v FROM cost_layers WHERE tenant_id=? AND remaining>0 GROUP BY product_id, sku_id, currency ORDER BY product_id", t)
    .map(r => ({ product_id: r.product_id, sku_id: r.sku_id, currency: r.currency, qty: r.qty, value: toMajor(r.v, r.currency), unit_cost: r.qty ? +(toMajor(r.v, r.currency) / r.qty).toFixed(4) : 0 }));
  const layered = {};
  for (const r of rows) layered[r.product_id + "|" + (r.sku_id || 0)] = (layered[r.product_id + "|" + (r.sku_id || 0)] || 0) + r.qty;
  const unvalued = db().all("SELECT s.product_id, s.id sku_id, s.stock FROM skus s JOIN products p ON p.tenant_id=s.tenant_id AND p.id=s.product_id WHERE s.tenant_id=? AND s.stock>0 AND p.deleted_at IS NULL", t)
    .map(s => ({ product_id: s.product_id, sku_id: s.sku_id, qty: s.stock - (layered[s.product_id + "|" + s.sku_id] || 0) })).filter(x => x.qty > 0);
  const totals = {};
  for (const r of rows) totals[r.currency] = +((totals[r.currency] || 0) + r.value).toFixed(6);
  return { method: method(t), items: rows, totals, unvalued, unvaluedUnits: unvalued.reduce((s, x) => s + x.qty, 0) };
}
/* the layers against the books' inventory account, per currency: they agree unless someone posted to inventory by hand */
function reconcile(tid) {
  const v = onHand(tid).totals, tb = B().trialBalance(tid);
  const cur = new Set([...Object.keys(v), ...tb.filter(t => t.rows.some(r => r.account === A.inventory)).map(t => t.currency)]);
  return [...cur].map(c => {
    const books = ((tb.find(t => t.currency === c) || { rows: [] }).rows.find(r => r.account === A.inventory) || { balance: 0 }).balance;
    return { currency: c, layers: v[c] || 0, books, difference: +((books) - (v[c] || 0)).toFixed(6) };
  });
}
/* what an order's goods cost, and so its gross margin */
function orderCost(tid, orderId) {
  const by = {};
  for (const r of db().all("SELECT i.currency, SUM(i.value_minor) v, SUM(i.returned * i.value_minor * 1.0 / i.qty) back FROM cost_issues i JOIN stock_moves m ON m.id=i.move_id WHERE m.tenant_id=? AND m.order_id=? AND i.currency IS NOT NULL GROUP BY i.currency", N(tid), N(orderId)))
    by[r.currency] = toMajor(Math.round(r.v - r.back), r.currency);
  return by;
}
/* the store chooses its method; what is already on hand keeps the cost it has, and from the next
   movement on units leave by the new method */
function setMethod(tid, m) {
  if (!SEED.methods.includes(String(m))) fail("A store values stock by one of: " + SEED.methods.join(", "));
  /* merged into what the store itself saved, so no default is frozen into its row */
  const row = db().get("SELECT value FROM settings WHERE tenant_id=? AND key='commerce'", N(tid));
  let own = {}; try { own = row ? JSON.parse(row.value) || {} : {}; } catch (e) { own = {}; }
  require("./settings.js").save(N(tid), { commerce: { ...own, stockValuation: String(m) } });
  return method(tid);
}
module.exports = { method, setMethod, receive, issue, restore, opening, onHand, reconcile, orderCost, SEED };
