/* fitment: which vehicles a part fits. The shopper keeps their vehicles; a part that lists fitments says
   whether it fits theirs. */
"use strict";
const F = () => require("../features.js"), K = "fitment";
const low = x => String(x || "").trim().toLowerCase();
const fits = (r, v) => low(r.make) === low(v.make) && (!r.model || low(r.model) === low(v.model)) && Number(v.year) >= Number(r.from_year || 0) && Number(v.year) <= Number(r.to_year || 9999);
const forProduct = (tid, id) => F().rows(tid, K).filter(r => r.product_id === id);
const garage = (tid, owner) => owner ? F().records(tid, K, { owner, state: "vehicle" }) : [];
module.exports = {
  check: r => { if (r.from_year && r.to_year && r.to_year < r.from_year) throw F().fail("The years run upwards"); },
  block: ({ tid, owner, product }) => { const rs = forProduct(tid, product.id); if (!rs.length) return null; const g = garage(tid, owner); return { title: g.length ? (g.some(v => rs.some(r => fits(r, v))) ? "✓ Fits your vehicle" : "✗ Does not fit your vehicle") : "Fits", rows: rs.slice(0, 40).map(r => [r.make + " " + (r.model || "all models"), (r.from_year || "") + "–" + (r.to_year || "")]) }; },
  actions: {
    add: ({ tid, owner, body }) => { const v = { make: String(body.make || "").trim().slice(0, 40), model: String(body.model || "").trim().slice(0, 60), year: Number(body.year) }; if (!v.make || !Number.isInteger(v.year) || v.year < 1900 || v.year > 2100) throw F().fail("Give the make and the year"); if (garage(tid, owner).length >= 20) throw F().fail("You have kept 20 vehicles"); F().record(tid, K, { owner, about: low(v.make), state: "vehicle", data: v }); return { ok: true, vehicles: garage(tid, owner) }; },
    remove: ({ tid, owner, body }) => { const r = garage(tid, owner).find(x => x.id === Number(body.id)); if (!r) throw F().fail("Not found", 404); F().forget(tid, K, r.id); return { ok: true }; }
  },
  open: ({ tid, query }) => ({ products: [...new Set(F().rows(tid, K).filter(r => fits(r, { make: query.make, model: query.model, year: query.year })).map(r => r.product_id))] }),
  mine: ({ tid, owner }) => garage(tid, owner).map(v => ({ text: v.make + " " + v.model + " " + v.year, actions: [{ label: "Remove", path: "/features/" + K + "/remove", body: { id: v.id } }] }))
};
