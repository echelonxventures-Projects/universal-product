/* funding goals: an item made only if enough is pledged in time. An order is a pledge; when the day
   comes and the goal is not reached, every pledge is cancelled and refunded. */
"use strict";
const F = () => require("../features.js"), db = () => require("../db.js"), K = "funding_goals";
const of = (tid, id) => F().rows(tid, K).find(r => r.product_id === id);
const over = r => r.ends <= new Date().toISOString();
function pledged(tid, r) { const dead = require("../states.js").tagged("order", "void"); return db().all("SELECT o.id, SUM(i.qty*i.price/COALESCE(NULLIF(o.fx,0),1)) v FROM orders o JOIN order_items i ON i.order_id=o.id WHERE o.tenant_id=? AND i.product_id=? AND o.status NOT IN (" + dead.map(() => "?").join(",") + ") AND o.created_at>=? GROUP BY o.id", Number(tid), r.product_id, ...dead, String(r.starts || "").slice(0, 10)); }
const total = (tid, r) => pledged(tid, r).reduce((n, x) => n + Number(x.v), 0);
module.exports = {
  check: r => { if (over(r)) throw F().fail("The last day must be in the future"); if (!r.starts) r.starts = F().today(); return r; },
  rule: ({ tid, product }) => { const r = of(tid, product.id); return r && over(r) ? { problem: "the funding for this has closed" } : null; },
  block: ({ tid, product }) => { const r = of(tid, product.id); if (!r) return null; const t = total(tid, r); return { title: "Made if it reaches its goal", text: Math.round(t / r.goal * 100) + "% of " + r.goal + " pledged by " + pledged(tid, r).length + " · ends " + r.ends.slice(0, 10) + ". If it does not, you are refunded.", progress: Math.min(1, t / r.goal) }; },
  sweep: async ({ tid }) => {
    for (const r of F().rows(tid, K).filter(over)) {
      const about = "goal:" + r.id; if (F().records(tid, K, { about }).length) continue;
      const met = total(tid, r) >= r.goal, list = pledged(tid, r);
      F().record(tid, K, { about, state: met ? "met" : "missed", data: { title: r.product_id, pledges: list.length } });
      const O = require("../orders.js");
      for (const x of list) { const o = O.orderOf(tid, x.id); if (!o) continue; if (met) require("../tell.js").tell(tid, o.owner, "order_paid", "It's happening", "The goal was reached. Your order " + o.num + " goes ahead.", "orders.html", { to: o.email }); else { try { await O.cancel(tid, o, { reason: "the funding goal was not reached", actor: "system" }); } catch (e) { console.error("funding refund " + o.num + ":", e.message); } } }
    }
  },
  staff: { list: ({ tid }) => F().rows(tid, K).map(r => ({ id: r.id, text: r.product_id + " · " + total(tid, r).toFixed(2) + " of " + r.goal + " · " + pledged(tid, r).length + " pledges", chip: over(r) ? (F().records(tid, K, { about: "goal:" + r.id })[0] || {}).state || "closing" : "open" })) }
};
