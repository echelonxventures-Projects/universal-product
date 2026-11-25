/* cold chain: items that must stay cold go only by carriers that keep them so, and their temperature on
   the way is recorded; a reading outside the range is raised at once */
"use strict";
const F = () => require("../features.js"), db = () => require("../db.js"), K = "cold_chain";
const J = v => { try { return typeof v === "string" ? JSON.parse(v || "{}") : v || {}; } catch (e) { return {}; } };
const cold = (tid, p) => F().rows(tid, K).find(r => F().names(r, { id: p.id, brand: p.brand || p.b, dept: p.dept || p.d })) || null;
const carriers = tid => String(F().params(tid, K).carriers || "").split(/[\s,]+/).filter(Boolean);
const items = (tid, id) => db().all("SELECT product_id FROM order_items WHERE order_id=?", id).map(i => db().get("SELECT id, brand, dept FROM products WHERE tenant_id=? AND id=?", Number(tid), i.product_id)).filter(Boolean).map(p => cold(tid, p)).filter(Boolean);
module.exports = {
  check: r => { if (r.max_c < r.min_c) throw F().fail("The range runs upwards"); },
  delivery: ({ tid, items: its, body, carrier }) => { if (!(its || []).some(i => cold(tid, i.product))) return null; const ok = carriers(tid); if (ok.length && carrier && !ok.includes(carrier)) return { problem: "Something in your bag must stay cold — choose " + ok.join(" or ") }; return { fee: Number(F().params(tid, K).fee) || 0 }; },
  block: ({ tid, product }) => { const r = cold(tid, product); return r && { title: "Kept cold", text: r.min_c + "°C to " + r.max_c + "°C all the way to you" }; },
  placed: ({ tid, owner, order }) => { const c = items(tid, order.id); if (c.length) F().record(tid, K, { owner, about: order.num, state: "cold", data: { order_id: order.id, min: Math.max(...c.map(x => x.min_c)), max: Math.min(...c.map(x => x.max_c)), readings: [] } }); },
  mine: ({ tid, owner }) => F().records(tid, K, { owner }).filter(r => r.readings.length).map(r => ({ text: "Order " + r.about + " · last reading " + r.readings[r.readings.length - 1].c + "°C", chip: r.state === "warm" ? "out of range" : "kept cold" })),
  staff: {
    list: ({ tid }) => F().records(tid, K).map(r => ({ id: r.id, text: r.about + " · " + r.min + " to " + r.max + "°C · " + (r.readings.map(x => x.c).join(", ") || "no readings"), chip: r.state, actions: [{ key: "reading", label: "Add reading", ask: "°C" }] })),
    actions: { reading: ({ tid, id, body }) => { const r = F().records(tid, K, { id })[0], c = Number(body.value); if (!r) throw F().fail("Not found", 404); if (body.value === "" || !isFinite(c) || c < -100 || c > 100) throw F().fail("Give the temperature in °C"); const bad = c < r.min || c > r.max; if (!F().change(tid, K, r.id, r.state, bad ? "warm" : r.state, { readings: r.readings.concat({ at: new Date().toISOString(), c }) })) throw F().fail("Try again", 409); if (bad) require("../events.js").emit(Number(tid), "cold_chain.breach", { order: r.about, c }); return { ok: true, outOfRange: bad }; } }
  }
};
