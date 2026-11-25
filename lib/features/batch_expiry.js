/* batch expiry: stock kept by batch, each with its expiry. What has expired, or soon will, is not sold;
   the batch that expires first leaves first (lib/stock.js asks for the order). */
"use strict";
const F = () => require("../features.js"), db = () => require("../db.js"), K = "batch_expiry";
const cutoff = days => new Date(Date.now() + days * 864e5).toISOString().slice(0, 10);
const dated = (tid, skuId) => db().all("SELECT id, qty, batch, expiry FROM inventory WHERE tenant_id=? AND sku_id=? AND expiry IS NOT NULL AND expiry<>'' ORDER BY expiry", Number(tid), Number(skuId));
const days = (tid, p) => { let d = Number(F().params(tid, K).min_days) || 0; if (F().on(tid, "freshness_windows")) for (const r of F().rows(tid, "freshness_windows")) if (F().names(r, p)) d = Math.max(d, r.days); return d; };
const skus = (tid, id) => db().all("SELECT id FROM skus WHERE tenant_id=? AND product_id=? AND active=1", Number(tid), id);
/* how many of a variant may be sold, or null where it is not kept by batch */
function sellable(tid, p, skuId) { const b = dated(tid, skuId); if (!b.length) return null; const c = cutoff(days(tid, p)); return b.filter(x => x.expiry > c).reduce((n, x) => n + Math.max(0, x.qty), 0); }
const full = (tid, p) => p.dept !== undefined ? p : db().get("SELECT id, brand, dept FROM products WHERE tenant_id=? AND id=?", Number(tid), p.id) || p;
module.exports = {
  sellable, cutoff, days,
  rule: ({ tid, product, sku }) => { const p = full(tid, product), ids = sku ? [sku] : skus(tid, p.id).map(x => x.id); const ns = ids.map(i => sellable(tid, p, i)).filter(x => x != null); if (!ns.length) return null; const n = ns.reduce((a, b) => a + b, 0); return n > 0 ? { maxQty: n } : { problem: "none is fresh enough to send" }; },
  staff: { list: ({ tid }) => db().all("SELECT i.id, i.qty, i.batch, i.expiry, s.product_id, p.title FROM inventory i JOIN skus s ON s.id=i.sku_id JOIN products p ON p.tenant_id=i.tenant_id AND p.id=s.product_id WHERE i.tenant_id=? AND i.expiry<>'' AND i.qty>0 AND i.expiry<=? ORDER BY i.expiry LIMIT 200", Number(tid), cutoff(60)).map(r => ({ id: r.id, text: r.title + " · batch " + (r.batch || "—") + " · " + r.qty + " left", chip: (r.expiry <= F().today() ? "expired " : "expires ") + r.expiry, actions: [{ key: "writeoff", label: "Write off" }] })),
    actions: { writeoff: ({ tid, id }) => { const r = db().get("SELECT * FROM inventory WHERE id=? AND tenant_id=?", Number(id), Number(tid)); if (!r || !(r.qty > 0)) throw F().fail("Nothing to write off", 404); return require("../stock.js").writeOff(tid, r.id); } } }
};
