/* dated delivery: a gift that arrives on its day, with a message */
"use strict";
const F = () => require("../features.js"), K = "dated_delivery";
function day(tid, v) { const P = F().params(tid, K), d = Date.parse(v), ahead = (d - Date.parse(F().today())) / 864e5; if (!/^\d{4}-\d\d-\d\d$/.test(v) || isNaN(d)) return null; return ahead >= Number(P.min_days) && ahead <= Number(P.days_ahead) ? v : null; }
module.exports = {
  open: ({ tid }) => { const P = F().params(tid, K), at = n => new Date(Date.now() + n * 864e5).toISOString().slice(0, 10); return { from: at(Number(P.min_days)), to: at(Number(P.days_ahead)) }; },
  delivery: ({ tid, body }) => (body || {}).deliver_on && !day(tid, String(body.deliver_on)) ? { problem: "We can't deliver on that day — choose another" } : null,
  placed: ({ tid, owner, order, body }) => { const b = body || {}; if (b.deliver_on || b.gift_note) F().record(tid, K, { owner, about: order.num, state: "planned", data: { on: day(tid, String(b.deliver_on || "")), note: String(b.gift_note || "").slice(0, 300) } }); },
  mine: ({ tid, owner }) => F().records(tid, K, { owner }).map(r => ({ text: "Order " + r.about + (r.note ? " · “" + r.note + "”" : ""), chip: r.on || "" })),
  staff: { list: ({ tid }) => F().records(tid, K).sort((a, b) => ((a.on || "9") < (b.on || "9") ? -1 : 1)).map(r => ({ id: r.id, text: r.about + (r.note ? " · “" + r.note + "”" : ""), chip: r.on || "any day" })) }
};
