/* sale events: a lower price for a time, on everything, a department, a brand or an item */
"use strict";
const F = () => require("../features.js");
const live = tid => { const now = new Date().toISOString(); return F().rows(tid, "sale_events").filter(r => r.starts <= now && r.ends > now); };
const best = (tid, p) => live(tid).filter(r => F().names(r, p)).sort((a, b) => b.percent - a.percent)[0] || null;
module.exports = {
  check: r => { if (r.ends <= r.starts) throw F().fail("It must end after it starts"); },
  price: ({ tid, product, unit }) => { const r = best(tid, product); return r && { unit: unit * (1 - r.percent / 100), label: r.name }; },
  rule: ({ tid, product }) => { const r = best(tid, product); return r && r.per_order ? { maxQty: r.per_order } : null; },
  block: ({ tid, product }) => { const r = best(tid, product); return r && { title: r.name, text: r.percent + "% off until " + new Date(r.ends).toUTCString().slice(0, 22) + (r.per_order ? " · at most " + r.per_order + " each" : "") }; }
};
