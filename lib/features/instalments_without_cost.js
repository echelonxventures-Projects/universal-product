/* instalments without cost: the shopper spreads the total over months at no interest; the store bears
   it. The plan chosen is kept on the order and sent to the gateway, which collects the instalments. */
"use strict";
const F = () => require("../features.js");
const months = r => String(r.months).split(/[\s,]+/).map(Number).filter(n => n > 1 && n <= 60);
const plans = (tid, net, gateway) => F().rows(tid, "instalments_without_cost").filter(r => (!gateway || r.gateway === gateway) && net >= Number(r.min_amount || 0)).flatMap(r => months(r).map(m => ({ gateway: r.gateway, months: m, each: +(net / m).toFixed(2) })));
module.exports = {
  check: r => { if (!months(r).length) throw F().fail("List the months, e.g. 3, 6, 9"); },
  open: ({ tid, query }) => ({ plans: plans(tid, Number(query.amount) || 0) }),
  rule: () => null,
  charges: ({ tid, net, body }) => { const n = Number((body || {}).instalments); if (n && body.final && !plans(tid, net, body.gateway).some(p => p.months === n)) throw F().fail("That instalment plan is not available for this payment", 422); return []; },
  placed: ({ tid, owner, order, body }) => { const n = Number((body || {}).instalments); if (n) F().record(tid, "instalments_without_cost", { owner, about: order.num, state: "chosen", data: { months: n, each: +(order.total / n).toFixed(2), currency: order.currency, gateway: order.pay_method } }); },
  mine: ({ tid, owner }) => F().records(tid, "instalments_without_cost", { owner }).map(r => ({ text: "Order " + r.about + " · " + r.months + " × " + r.each + " " + r.currency, chip: "no interest" })),
  staff: { list: ({ tid }) => F().records(tid, "instalments_without_cost").map(r => ({ id: r.id, text: r.about + " · " + r.months + " × " + r.each + " " + r.currency + " · " + r.gateway })) }
};
