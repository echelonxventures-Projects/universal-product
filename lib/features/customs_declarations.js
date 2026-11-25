/* customs declarations: what an order going abroad contains, made from the order itself */
"use strict";
const F = () => require("../features.js"), db = () => require("../db.js");
const J = v => { try { return JSON.parse(v || "{}"); } catch (e) { return {}; } };
function make(tid, order, data) {
  const s = require("../settings.js").load(tid), items = db().all("SELECT product_id, qty, price FROM order_items WHERE order_id=?", order.id).map(i => {
    const p = db().get("SELECT title, identity, logistics FROM products WHERE tenant_id=? AND id=?", Number(tid), i.product_id) || {}, id = J(p.identity), lg = J(p.logistics);
    return { description: p.title || i.product_id, code: String(id.hs || id.hsn || ""), origin: String(id.origin || id.country_of_origin || s.commerce.country || "").toUpperCase(), qty: i.qty, unit_value: i.price, value: +(i.price * i.qty).toFixed(2), weight_kg: +((Number(lg.weightKg) || Number(s.commerce.parcelWeightKg) || 0) * i.qty).toFixed(3) };
  });
  return { order: order.num, reason: data.reason, incoterms: data.incoterms, from: { name: (s.legal || {}).businessName || s.brand.name, address: (s.legal || {}).address || "", taxId: (s.legal || {}).taxId || "", country: s.commerce.country }, to: { name: order.name, address: [order.address, order.city, order.state, order.zip].filter(Boolean).join(", "), country: data.country },
    currency: order.currency, items, value: +items.reduce((n, i) => n + i.value, 0).toFixed(2), weight_kg: +items.reduce((n, i) => n + i.weight_kg, 0).toFixed(3), missing: items.filter(i => !i.code).map(i => i.description) };
}
module.exports = {
  placed: ({ tid, owner, order, body }) => { const c = String((body || {}).country || "").toUpperCase(), P = F().params(tid, "customs_declarations"); if (c && c !== String(require("../settings.js").load(tid).commerce.country || "").toUpperCase()) F().record(tid, "customs_declarations", { owner, about: order.num, state: "draft", data: { order_id: order.id, country: c, reason: P.reason, incoterms: P.incoterms } }); },
  staff: {
    list: ({ tid }) => F().records(tid, "customs_declarations").map(r => ({ id: r.id, text: r.about + " to " + r.country, chip: r.state, actions: [{ key: "document", label: "Open" }].concat(r.state === "draft" ? [{ key: "declare", label: "Declare" }] : []) })),
    actions: {
      document: ({ tid, id }) => { const r = F().records(tid, "customs_declarations", { id })[0]; if (!r) throw F().fail("Not found", 404); return { document: r.final || make(tid, db().get("SELECT * FROM orders WHERE id=? AND tenant_id=?", r.order_id, Number(tid)), r) }; },
      declare: ({ tid, id }) => { const r = F().records(tid, "customs_declarations", { id })[0]; if (!r) throw F().fail("Not found", 404); const d = make(tid, db().get("SELECT * FROM orders WHERE id=? AND tenant_id=?", r.order_id, Number(tid)), r); if (d.missing.length) throw F().fail("These items have no customs code: " + d.missing.join(", "), 409); if (!F().change(tid, "customs_declarations", r.id, "draft", "declared", { final: d })) throw F().fail("Already declared", 409); return { document: d }; }
    }
  }
};
