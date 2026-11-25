/* refill reminders: an item that runs out is remembered — the shopper is told before it does, and may stop it */
"use strict";
const F = () => require("../features.js"), db = () => require("../db.js"), K = "refill_reminders";
const of = (tid, p) => F().rows(tid, K).find(r => F().names(r, p));
module.exports = {
  moved: ({ tid, order, to }) => {
    if (!require("../states.js").is("order", to, "fulfilled") || F().records(tid, K, { about: order.num }).length) return;
    const lead = Number(F().params(tid, K).days_before) || 0;
    for (const i of db().all("SELECT product_id, SUM(qty) q FROM order_items WHERE order_id=? GROUP BY product_id", order.id)) { const p = db().get("SELECT id, title, brand, dept FROM products WHERE tenant_id=? AND id=?", Number(tid), i.product_id), r = p && of(tid, p); if (r) F().record(tid, K, { owner: order.owner, about: order.num, state: "waiting", data: { product_id: p.id, title: p.title, on: new Date(Date.now() + Math.max(1, r.days * i.q - lead) * 864e5).toISOString().slice(0, 10), email: order.email || "" } }); }
  },
  sweep: ({ tid }) => { for (const r of F().records(tid, K, { state: "waiting", limit: 5000 })) if (r.on <= F().today() && F().change(tid, K, r.id, "waiting", "told")) require("../tell.js").tell(tid, r.owner, "back_in_stock", "Time to refill " + r.title, "You may be about to run out.", "product.html?id=" + encodeURIComponent(r.product_id), { to: r.email }); },
  actions: { stop: ({ tid, owner, body }) => { const r = F().records(tid, K, { owner, id: Number(body.id) })[0]; if (!r || !F().change(tid, K, r.id, "waiting", "stopped")) throw F().fail("Not found", 404); return { ok: true }; } },
  mine: ({ tid, owner }) => F().records(tid, K, { owner, state: "waiting" }).map(r => ({ text: r.title + " · reminder on " + r.on, actions: [{ label: "Stop", path: "/features/" + K + "/stop", body: { id: r.id } }] }))
};
