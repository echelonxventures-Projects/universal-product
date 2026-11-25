/* consolidated shipping: an order that can leave with one the shopper already has waiting, to the same
   address, pays no delivery; staff see them as one parcel */
"use strict";
const F = () => require("../features.js"), db = () => require("../db.js"), states = () => require("../states.js");
const key = o => [o.address, o.city, o.zip].map(x => String(x || "").toLowerCase().replace(/\s+/g, " ").trim()).join("|");
function waiting(tid, owner, dest) {
  const hours = Number(F().params(tid, "consolidated_shipping").hours) || 0, ok = states().tagged("order", "shippable");
  if (!owner || !hours || !ok.length || !dest.address) return null;
  return db().all("SELECT * FROM orders WHERE tenant_id=? AND owner=? AND status IN (" + ok.map(() => "?").join(",") + ") AND created_at > datetime('now', ?) ORDER BY id", Number(tid), owner, ...ok, "-" + hours + " hours").find(o => key(o) === key(dest)) || null;
}
module.exports = {
  delivery: ({ tid, owner, body }) => waiting(tid, owner, body || {}) ? { free: true } : null,
  placed: ({ tid, owner, order }) => { const w = waiting(tid, owner, order); if (w && w.id !== order.id) { const head = (F().records(tid, "consolidated_shipping", { about: w.num })[0] || {}).with || w.num; F().record(tid, "consolidated_shipping", { owner, about: order.num, state: "together", data: { with: head } }); } },
  staff: { list: ({ tid }) => F().records(tid, "consolidated_shipping").map(r => ({ id: r.id, text: r.about + " goes with " + r.with })) }
};
