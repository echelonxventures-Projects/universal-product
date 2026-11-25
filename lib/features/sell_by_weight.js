/* sell by weight: an item priced per unit of weight, bought by the amount wanted; its stock is counted
   in the smallest step it is sold by */
"use strict";
const F = () => require("../features.js"), T = require("../lineterms.js"), K = "sell_by_weight";
const of = (tid, id) => F().rows(tid, K).find(r => r.product_id === id);
const steps = (r, a) => Math.round(a / r.step);
module.exports = {
  check: r => { if (r.max < r.min) throw F().fail("The most is at least the least"); },
  rule: ({ tid, product, terms }) => of(tid, product.id) && !(terms || {}).weight ? { problem: "choose how much" } : null,
  /* how many counted steps one of this line takes from the shelf (lib/stock.js) */
  count: (tid, productId, terms) => { const r = of(tid, productId); return r && terms && terms.weight ? steps(r, Number(terms.weight.amount)) : 1; },
  term: {
    key: "weight",
    clean: (ctx, v) => { const r = of(ctx.tid, ctx.product.id), a = Number((v || {}).amount); if (!r) throw T.fail("This is not sold by weight"); if (!(a >= r.min - 1e-9 && a <= r.max + 1e-9)) throw T.fail("Choose from " + r.min + " to " + r.max + " " + r.unit); if (Math.abs(a / r.step - steps(r, a)) > 1e-6) throw T.fail("Choose in steps of " + r.step + " " + r.unit); return { amount: +(steps(r, a) * r.step).toFixed(6) }; },
    price: (ctx, v) => { const r = of(ctx.tid, ctx.product.id); if (!r) throw T.fail("no longer sold by weight"); return { set: +(Number(ctx.product.price) * Number(v.amount)).toFixed(4), label: v.amount + " " + r.unit }; }
  },
  block: ({ tid, product }) => { const r = of(tid, product.id); return r && { title: "Sold by weight", text: "Price per " + r.unit, term: { key: "weight", fields: [{ key: "amount", label: "How much (" + r.unit + ")", type: "number", min: r.min, max: r.max, step: r.step, value: r.min }] } }; }
};
