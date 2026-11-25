/* supplier direct: items a supplier sends itself. Their part of an order goes to the supplier at once;
   the order ships when every supplier has sent theirs. */
"use strict";
const F = () => require("../features.js"), db = () => require("../db.js");
const rowFor = (tid, p) => F().rows(tid, "supplier_direct").find(r => F().names(r, p));
module.exports = {
  check: r => { if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(r.email)) throw F().fail("The supplier's email is not valid"); },
  block: ({ tid, product }) => { const r = rowFor(tid, product); return r && { title: "Sent by our supplier", text: "Leaves in about " + r.days + " days" }; },
  delivery: ({ tid, items }) => ({ days: Math.max(0, ...(items || []).map(i => (rowFor(tid, { id: i.product.id, brand: i.product.b, dept: i.product.d }) || {}).days || 0)) }),
  placed: ({ tid, owner, order, items }) => {
    const by = new Map();
    for (const i of items) { const r = rowFor(tid, { id: i.product.id, brand: i.product.b, dept: i.product.d }); if (r) by.set(r.id, { r, lines: ((by.get(r.id) || {}).lines || []).concat({ id: i.product.id, title: i.product.t, qty: i.qty }) }); }
    for (const { r, lines } of by.values()) {
      F().record(tid, "supplier_direct", { owner, about: order.num, state: "sent", data: { order_id: order.id, supplier: r.name, email: r.email, lines } });
      require("../mailer.js").deliver({ tenantId: Number(tid), channel: "email", to: r.email, kind: "supplier_order", subject: "Order " + order.num + " to send", text: "Please send to:\n" + [order.name, order.address, order.city, order.state, order.zip].filter(Boolean).join("\n") + "\n\n" + lines.map(l => l.qty + " × " + l.title + " (" + l.id + ")").join("\n") });
    }
  },
  staff: {
    list: ({ tid }) => F().records(tid, "supplier_direct").map(r => ({ id: r.id, text: r.about + " · " + r.supplier + " · " + r.lines.map(l => l.qty + " × " + l.title).join(", ") + (r.tracking ? " · " + r.tracking : ""), chip: r.state, actions: r.state === "sent" ? [{ key: "shipped", label: "Supplier has sent it", ask: "Tracking number" }, { key: "refused", label: "Supplier can't" }] : [] })),
    actions: {
      shipped: async ({ tid, id, body, actor }) => {
        const r = F().records(tid, "supplier_direct", { id })[0];
        if (!r || !F().change(tid, "supplier_direct", r.id, "sent", "shipped", { tracking: String(body.value || "").slice(0, 80) })) throw F().fail("Already answered", 409);
        const O = require("../orders.js"), o = O.orderOf(tid, r.order_id), st = require("../states.js"), all = db().all("SELECT product_id FROM order_items WHERE order_id=?", r.order_id).map(x => x.product_id), got = F().records(tid, "supplier_direct", { about: r.about, state: "shipped" }).flatMap(x => x.lines.map(l => l.id));
        if (o && all.every(x => got.includes(x)) && st.is("order", o.status, "shippable")) await O.setStatus(tid, o, st.first("order", "in_transit"), { actor });
        return { ok: true };
      },
      refused: ({ tid, id }) => { if (!F().change(tid, "supplier_direct", id, "sent", "refused")) throw F().fail("Already answered", 409); return { ok: true }; }
    }
  }
};
