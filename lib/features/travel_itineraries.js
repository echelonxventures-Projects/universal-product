/* travel itineraries: a trip is sold by its start day and travellers, and the order carries its plan,
   day by day, from that start */
"use strict";
const F = () => require("../features.js"), T = require("../lineterms.js"), K = "travel_itineraries";
const of = (tid, id) => F().rows(tid, K).find(r => r.product_id === id);
const plan = r => String(r.days).split(/\r?\n/).map(x => x.trim()).filter(Boolean);
module.exports = {
  check: r => { if (!plan(r).length) throw F().fail("Write the plan, one line a day"); },
  rule: ({ tid, product, terms }) => of(tid, product.id) && !(terms || {}).trip ? { problem: "choose when your trip starts" } : null,
  term: {
    key: "trip",
    clean: (ctx, v) => { const r = of(ctx.tid, ctx.product.id), d = String((v || {}).starts || ""); if (!r) throw T.fail("This is not a trip"); if (!/^\d{4}-\d\d-\d\d$/.test(d) || isNaN(Date.parse(d))) throw T.fail("Choose the day your trip starts"); const ahead = (Date.parse(d) - Date.now()) / 864e5; if (ahead < Number(r.notice_days || 0)) throw T.fail("Trips start at least " + (r.notice_days || 0) + " days from now"); if (ahead > 730) throw T.fail("Choose a day within two years"); return { starts: d, travellers: String(v.travellers || "").slice(0, 300) }; },
    price: (ctx, v) => ({ label: "Starts " + v.starts + (v.travellers ? " · " + v.travellers : "") }),
    place: (ctx, v) => { const r = of(ctx.tid, ctx.product.id); if (r) F().record(ctx.tid, K, { owner: ctx.owner, about: ctx.orderNum, state: "booked", data: { title: ctx.product.t || ctx.product.title, starts: v.starts, travellers: v.travellers, days: plan(r).map((x, i) => ({ day: new Date(Date.parse(v.starts) + i * 864e5).toISOString().slice(0, 10), plan: x })) } }); }
  },
  block: ({ tid, product }) => { const r = of(tid, product.id); return r && { title: plan(r).length + "-day trip", rows: plan(r).map((x, i) => ["Day " + (i + 1), x]), term: { key: "trip", fields: [{ key: "starts", label: "Start day", type: "date" }, { key: "travellers", label: "Travellers' names" }] } }; },
  moved: ({ tid, order, to }) => { if (require("../states.js").is("order", to, "void")) for (const r of F().records(tid, K, { about: order.num, state: "booked" })) F().change(tid, K, r.id, "booked", "cancelled"); },
  mine: ({ tid, owner }) => F().records(tid, K, { owner }).map(r => ({ text: r.title + " · " + r.starts + (r.travellers ? " · " + r.travellers : ""), chip: r.state, rows: r.days.map(d => [d.day, d.plan]) })),
  staff: { list: ({ tid }) => F().records(tid, K).map(r => ({ id: r.id, text: r.about + " · " + r.title + " · starts " + r.starts + " · " + (r.travellers || ""), chip: r.state })) }
};
