/* large item delivery: what is too big for an ordinary parcel — the shopper chooses how it is brought in */
"use strict";
const F = () => require("../features.js"), db = () => require("../db.js"), K = "large_item_delivery";
const J = v => { try { return typeof v === "string" ? JSON.parse(v || "{}") : v || {}; } catch (e) { return {}; } };
const classes = tid => String(F().params(tid, K).classes || "").split(/[\s,]+/).filter(Boolean);
const large = (tid, id) => { const p = db().get("SELECT logistics FROM products WHERE tenant_id=? AND id=?", Number(tid), id); return !!p && classes(tid).includes(J(p.logistics).shippingClass); };
module.exports = {
  open: ({ tid, query }) => ({ needed: String(query.products || "").split(",").some(id => large(tid, id)), options: F().rows(tid, K).map(r => ({ id: r.id, name: r.name, fee: r.fee, note: r.note })) }),
  delivery: ({ tid, items, body }) => { if (!(items || []).some(i => large(tid, i.product.id))) return null; const rs = F().rows(tid, K); if (!rs.length) return null; const r = rs.find(x => x.id === Number((body || {}).large_option)); if (!r) return body && body.final ? { problem: "Choose how your large item is delivered" } : null; return { fee: r.fee, days: r.days }; },
  placed: ({ tid, owner, order, body }) => { const r = F().rows(tid, K).find(x => x.id === Number((body || {}).large_option)); if (r) F().record(tid, K, { owner, about: order.num, state: "chosen", data: { option: r.name } }); },
  block: ({ tid, product }) => large(tid, product.id) ? { title: "Large item delivery", rows: F().rows(tid, K).map(r => [r.name, r.note || ""]) } : null,
  mine: ({ tid, owner }) => F().records(tid, K, { owner }).map(r => ({ text: "Order " + r.about, chip: r.option })),
  staff: { list: ({ tid }) => F().records(tid, K).map(r => ({ id: r.id, text: r.about, chip: r.option })) }
};
