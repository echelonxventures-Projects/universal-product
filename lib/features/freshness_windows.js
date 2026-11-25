/* freshness windows: how many days of life an item still has when it arrives, promised and kept (the
   batches sold are chosen by batch_expiry, which reads these) */
"use strict";
const F = () => require("../features.js"), K = "freshness_windows";
const of = (tid, p) => F().rows(tid, K).filter(r => F().names(r, p)).sort((a, b) => b.days - a.days)[0];
module.exports = { block: ({ tid, product }) => { const r = of(tid, product); return r && { title: "Fresh for at least " + r.days + " days", text: r.note || "" }; },
  rule: ({ tid, product, sku }) => F().on(tid, "batch_expiry") ? null : require("./batch_expiry.js").rule({ tid, product, sku }) };
