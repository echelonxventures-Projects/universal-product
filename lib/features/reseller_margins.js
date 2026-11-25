/* reseller margins: a signed-in reseller sells an item on at their own price. The margin is added to the
   line, and is theirs — paid to their wallet once the order is delivered. */
"use strict";
const F = () => require("../features.js"), T = require("../lineterms.js");
const most = (tid, product) => Math.max(0, Number(product.price) * Number(F().params(tid, "reseller_margins").max_percent || 0) / 100);
module.exports = {
  term: {
    key: "resale",
    clean: (ctx, v) => { const m = +Number((v || {}).margin).toFixed(2); if (!ctx.signedIn && ctx.signedIn !== undefined) throw T.fail("Sign in to resell", 401); if (!(m > 0)) throw T.fail("Say what you add"); if (m > most(ctx.tid, ctx.product) + 0.001) throw T.fail("You can add at most " + most(ctx.tid, ctx.product).toFixed(2)); return { margin: m }; },
    price: (ctx, v) => ({ add: Number(v.margin), label: "Resold · your margin " + Number(v.margin).toFixed(2) }),
    place: (ctx, v) => F().record(ctx.tid, "reseller_margins", { owner: ctx.owner, about: ctx.orderNum, state: "waiting", data: { margin: +(v.margin * ctx.qty).toFixed(2), title: ctx.product.t || ctx.product.title } })
  },
  block: ({ tid, product, owner }) => /:u:/.test(owner || "") && most(tid, product) > 0 ? { title: "Resell this", text: "Add up to " + most(tid, product).toFixed(2) + " as your margin", term: { key: "resale", field: "margin", label: "Your margin" } } : null,
  moved: ({ tid, order, to }) => {
    const st = require("../states.js");
    for (const r of F().records(tid, "reseller_margins", { about: order.num, state: "waiting" })) {
      if (st.is("order", to, "fulfilled") && F().change(tid, "reseller_margins", r.id, "waiting", "paid")) { require("../offers.js").credit(Number(tid), r.owner, r.margin, "reward", "resale:" + order.num + ":" + r.id, null, "resale"); require("../tell.js").tell(tid, r.owner, "payout_update", "Your margin is paid", r.margin + " for order " + order.num + " is in your wallet.", "orders.html"); }
      else if (st.is("order", to, "void")) F().change(tid, "reseller_margins", r.id, "waiting", "lost");
    }
  },
  mine: ({ tid, owner }) => F().records(tid, "reseller_margins", { owner }).map(r => ({ text: "Order " + r.about + " · " + (r.title || "") + " · " + r.margin, chip: { waiting: "paid on delivery", paid: "in your wallet", lost: "cancelled" }[r.state] }))
};
