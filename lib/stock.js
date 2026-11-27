/* LUXORA Platform — stock: what an order takes from the shelf, and what goes back.

   An item is counted when its kind (productTypes) has a fulfilment mode the fulfilmentModes
   vocabulary marks `physical` — a parcel, a shelf pickup, a printed ticket. Anything else (a
   download, a call) is never counted down.

   `take` is one transaction: every line of an order is taken, or none is. Each count is lowered
   by one write that refuses to go below zero, so two shoppers can never both take the last unit.
   What was taken is kept in stock_moves, so it goes back exactly once (`giveBack`) when the order
   is cancelled, its payment fails, or a returned item is put back on the shelf. */
"use strict";

const db = () => require("./db.js");
const reg = () => require("./registry.js");
const counts = () => require("./product-counts.js");
const valuation = () => require("./valuation.js");
const tx = fn => require("./kernel.js").internal.tx(fn);
const fail = (msg, status) => Object.assign(new Error(msg), { status: status || 409 });

/* is an item of this kind counted? */
function tracked(type) {
  const kinds = reg().list("productTypes");
  const kind = kinds.find(k => k.key === String(type || "")) || kinds.find(k => k.default) || {};
  const modes = reg().list("fulfilmentModes");
  return (kind.fulfilment || []).some(f => modes.some(m => m.key === f && m.physical));
}
/* the variant a line's count lives on: the chosen one, else the item's only one */
function variantOf(tid, productId, skuId) {
  const D = db();
  if (skuId) return D.get("SELECT id, stock FROM skus WHERE id=? AND tenant_id=?", Number(skuId), Number(tid)) || null;
  const all = D.all("SELECT id, stock FROM skus WHERE tenant_id=? AND product_id=? AND active=1 ORDER BY id LIMIT 2", Number(tid), String(productId));
  return all.length === 1 ? all[0] : null;
}
/* how many may be bought now; Infinity for what is not counted */
function available(tid, product, skuId) {
  const pre = require("./preorders.js").open(tid, product.id);
  if (pre) return pre.left;
  if (!tracked(product.type)) return Infinity;
  const p = Math.max(0, Number(product.stock) || 0);
  const v = variantOf(tid, product.id, skuId);
  return v ? Math.min(p, Math.max(0, Number(v.stock) || 0)) : p;
}
/* lines: [{ product_id, sku_id, qty }] */
function take(tid, orderId, lines) {
  const D = db(), t = Number(tid);
  return tx(() => {
    for (const l of lines) {
      const p = D.get("SELECT id, title, type FROM products WHERE tenant_id=? AND id=? AND deleted_at IS NULL", t, String(l.product_id));
      if (!p) throw fail("An item in your bag is no longer sold");
      const qty = Number(l.qty);
      if (!Number.isInteger(qty) || qty < 1) throw fail("Invalid quantity for " + p.title, 400);
      if (require("./preorders.js").open(t, p.id)) {
        if (!require("./preorders.js").promise(t, p.id, qty)) throw fail(p.title + ": no more can be pre-ordered");
        D.run("INSERT INTO stock_moves(tenant_id,order_id,product_id,sku_id,qty,returned,promised) VALUES(?,?,?,NULL,?,0,1)", t, Number(orderId), p.id, qty);
        continue;
      }
      if (!tracked(p.type)) continue;
      const short = () => { const left = available(t, D.get("SELECT * FROM products WHERE tenant_id=? AND id=?", t, p.id), l.sku_id); return fail(p.title + (left > 0 ? ": only " + left + " left" : ": sold out")); };
      const v = variantOf(t, p.id, l.sku_id);
      if (!counts().lower(t, p.id, v ? v.id : null, qty)) throw short();
      const mv = D.run("INSERT INTO stock_moves(tenant_id,order_id,product_id,sku_id,qty,returned) VALUES(?,?,?,?,?,0)", t, Number(orderId), p.id, v ? v.id : null, qty);
      if (v) shelf(t, v.id, -qty);
      /* what the units cost leaves inventory for cost of goods sold (lib/valuation.js) */
      valuation().issue(t, { product_id: p.id, sku_id: v ? v.id : null, qty, kind: "cogs", move_id: Number(mv.lastInsertRowid), ref: (D.get("SELECT uid FROM orders WHERE id=?", Number(orderId)) || {}).uid || "" });
    }
  });
}
/* how many counted steps one unit of an order's item took (an item sold by weight) */
function perUnit(tid, orderId, productId) {
  const D = db(), took = D.get("SELECT SUM(qty) q FROM stock_moves WHERE tenant_id=? AND order_id=? AND product_id=?", Number(tid), Number(orderId), String(productId)).q;
  const bought = D.get("SELECT SUM(qty) q FROM order_items WHERE order_id=? AND product_id=?", Number(orderId), String(productId)).q;
  return took && bought ? Math.max(1, Math.round(took / bought)) : 1;
}
/* stock that cannot be sold leaves the shelf and the counts */
function writeOff(tid, inventoryId) {
  const D = db(), t = Number(tid);
  return tx(() => {
    const r = D.get("SELECT i.qty, i.sku_id, s.product_id FROM inventory i JOIN skus s ON s.id=i.sku_id WHERE i.id=? AND i.tenant_id=?", Number(inventoryId), t);
    if (!r || !(r.qty > 0)) throw fail("Nothing to write off", 404);
    D.run("UPDATE inventory SET qty=0 WHERE id=?", Number(inventoryId));
    counts().writeOff(t, r.product_id, r.sku_id, r.qty);
    valuation().issue(t, { product_id: r.product_id, sku_id: r.sku_id, qty: r.qty, kind: "write_off", ref: "inventory:" + Number(inventoryId) });
    return { ok: true, qty: r.qty };
  });
}
/* the same count on the variant's warehouse rows — the batch that expires first, then the fullest; a
   row never goes below zero, and a batch that may not be sold is left */
function shelf(tid, skuId, change) {
  const D = db();
  const F = require("./features.js"), byBatch = F.on(tid, "batch_expiry") || F.on(tid, "freshness_windows");
  const p = byBatch ? D.get("SELECT p.id, p.brand, p.dept FROM skus s JOIN products p ON p.tenant_id=s.tenant_id AND p.id=s.product_id WHERE s.id=?", Number(skuId)) : null;
  const B = byBatch ? F.engines.get("batch_expiry") : null, limit = B && p ? B.cutoff(B.days(tid, p)) : "";
  const rows = D.all("SELECT id, qty, expiry FROM inventory WHERE tenant_id=? AND sku_id=? ORDER BY " + (byBatch ? "CASE WHEN expiry IS NULL OR expiry='' THEN 1 ELSE 0 END, expiry, " : "") + "qty DESC, id", Number(tid), Number(skuId)).filter(r => change > 0 || !byBatch || !r.expiry || r.expiry > limit);
  if (!rows.length) return;
  if (change > 0) { D.run("UPDATE inventory SET qty=qty+? WHERE id=?", change, rows[0].id); return; }
  let left = -change;
  for (const r of rows) {
    if (left <= 0) break;
    const n = Math.min(left, Math.max(0, Number(r.qty) || 0));
    if (n > 0) { D.run("UPDATE inventory SET qty=qty-? WHERE id=?", n, r.id); left -= n; }
  }
}
/* goods arriving at a warehouse (a supplier's delivery): the product's and variant's counts go up,
   and the warehouse row for that variant and batch (lot, batch, expiry) — a new row when the batch
   is new there */
function receive(tid, productId, skuId, warehouseId, qty, batch) {
  const D = db(), t = Number(tid), b = batch || {}, n = Number(qty);
  if (!Number.isInteger(n) || n < 1) throw fail("A whole number of at least 1 is received");
  return tx(() => {
    counts().raise(t, String(productId), skuId || null, n);
    if (!skuId) return;
    const row = D.get("SELECT id FROM inventory WHERE tenant_id=? AND sku_id=? AND warehouse_id=? AND COALESCE(lot,'')=? AND COALESCE(batch,'')=? AND COALESCE(expiry,'')=? ORDER BY id LIMIT 1",
      t, Number(skuId), Number(warehouseId), String(b.lot || ""), String(b.batch || ""), String(b.expiry || ""));
    if (row) D.run("UPDATE inventory SET qty=qty+? WHERE id=?", n, row.id);
    else D.run("INSERT INTO inventory(tenant_id,sku_id,warehouse_id,qty,reserved,lot,batch,expiry) VALUES(?,?,?,?,0,?,?,?)", t, Number(skuId), Number(warehouseId), n, String(b.lot || ""), String(b.batch || ""), String(b.expiry || ""));
  });
}
/* put back what an order took: all that is still out, or up to `qty` of one item. Returns how many. */
function giveBack(tid, orderId, productId, qty) {
  const D = db(), t = Number(tid);
  return tx(() => {
    const rows = productId == null
      ? D.all("SELECT * FROM stock_moves WHERE tenant_id=? AND order_id=? AND returned<qty ORDER BY id", t, Number(orderId))
      : D.all("SELECT * FROM stock_moves WHERE tenant_id=? AND order_id=? AND product_id=? AND returned<qty ORDER BY id", t, Number(orderId), String(productId));
    let left = qty == null ? Infinity : Math.max(0, Number(qty) || 0), back = 0;
    for (const m of rows) {
      const n = Math.min(left, m.qty - m.returned);
      if (n <= 0) break;
      if (!D.run("UPDATE stock_moves SET returned=returned+? WHERE id=? AND returned+?<=qty", n, m.id, n).changes) continue;
      if (m.promised) { require("./preorders.js").giveBack(t, m.product_id, n); left -= n; back += n; continue; }
      counts().raise(t, m.product_id, m.sku_id, n);
      if (m.sku_id) shelf(t, m.sku_id, n);
      valuation().restore(t, m.id, n);
      left -= n; back += n;
    }
    return back;
  });
}

module.exports = { perUnit, writeOff, tracked, available, take, giveBack, receive };
