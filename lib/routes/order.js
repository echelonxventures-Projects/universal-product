/* LUXORA Platform — order domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the order domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "order", routes(kit) {
  const { notify, orders: orderFlow, returns, T, all, bad, engineFail, get, json, logAction, notifyWrite, ownerFor, pickup, publicProduct, registry, requireAdmin, requireStaff, run, shopperCall, signedIn, stIs, states, substitutions } = kit;

  function apiOrders(req, res, url, s) {
    const orders = all("SELECT * FROM orders WHERE owner=? ORDER BY created_at DESC", ownerFor(s));
    for (const o of orders) {
      o.items = all("SELECT product_id id, qty, price FROM order_items WHERE order_id=?", o.id).map(it => {
        const p = get("SELECT * FROM products WHERE tenant_id=? AND id=?", T(s), it.id);
        return { id: it.id, qty: it.qty, price: it.price, product: p ? publicProduct({ ...p, about: [] }) : null };
      });
      const pay = get("SELECT gateway, txn_ref, status FROM payments WHERE tenant_id=? AND order_id=?", T(s), o.id);
      if (pay) o.payment = pay;
      /* an order collected from a pickup point carries its point, its state and the code */
      o.pickup = pickup.forOrder(T(s), o.id, ownerFor(s));
      /* how the order shows is the machine's: its state's label, icon and tone — and an order
         past its delivery estimate that is neither void nor already fulfilled is
         late — it is never shown as delivered before it is */
      o.late = !stIs("order", o.status, "void") && !stIs("order", o.status, "fulfilled") && Date.now() > new Date(String(o.created_at).replace(" ", "T") + "Z").getTime() + (o.eta_days || 5) * 864e5;
      o.display = states.display("order", o.status);
      o.can = { cancel: orderFlow.shopperCanCancel(o), return: orderFlow.returnable(o) && o.items.some(i => returns.remaining(o, i.id) > 0) };
      o.tracking = all("SELECT tracking_number, carrier_type carrier, status FROM package_tracking WHERE tenant_id=? AND order_id=?", T(s), o.id);
      o.refunds = require("../refunds.js").listFor(T(s), o.id).filter(r => r.done).map(r => ({ amount: r.amount, currency: r.currency, at: r.created_at }));
    }
    json(res, 200, { orders });
  }
  function apiAdminOrders(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    const t = T(s);
    const orders = all("SELECT * FROM orders WHERE tenant_id=? ORDER BY created_at DESC LIMIT 200", t);
    for (const o of orders) {
      o.items = all("SELECT product_id id, qty, price FROM order_items WHERE order_id=?", o.id).map(it => {
        const p = get("SELECT title,brand,emoji,hue FROM products WHERE tenant_id=? AND id=?", t, it.id);
        return { id: it.id, qty: it.qty, price: it.price, product: p || null };
      });
      const pay = get("SELECT gateway, method, txn_ref, status, fee FROM payments WHERE tenant_id=? AND order_id=?", t, o.id);
      if (pay) o.payment = pay;
    }
    json(res, 200, { orders });
  }
  async function apiAdminOrderStatus(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    const o = orderFlow.orderOf(T(s), id);
    if (!o) return bad(res, "Unknown order", 404);
    try {
      const r = await orderFlow.setStatus(T(s), o, String(body.status || ""), { reason: body.reason, actor: s.platform_admin ? s.platform_admin.email : "user:" + s.user_id, notify: (t, x) => notify(T(s), t, x) });
      logAction(s, "order.status", "order", id, { status: body.status, refunded: r.refunded, owed: r.owed }, req);
      json(res, 200, { ok: true, ...r });
    } catch (e) { engineFail(res, e); }
  }
  /* substitutions */
  function apiSubstitutionsMine(req, res, url, s) { if (signedIn(s, res, "see substitutions")) shopperCall(res, () => ({ substitutions: substitutions.mine(T(s), ownerFor(s)), ...substitutions.vocabulary() })); }
  function apiSubstitutionDecide(req, res, url, s, body, id) { if (signedIn(s, res, "answer a substitution")) shopperCall(res, () => ({ substitution: substitutions.decide(T(s), ownerFor(s), id, String(body.action || "")) })); }
  function apiAdminSubstitutions(req, res, url, s, body, orderId) { if (requireStaff(s, res)) shopperCall(res, () => ({ ...substitutions.forOrder(T(s), orderId), ...substitutions.vocabulary() })); }
  function apiAdminSubstitutionAct(req, res, url, s, body, orderId) {
    if (!requireAdmin(s, res)) return;
    try {
      const r = body.unavailable ? substitutions.unavailable(T(s), orderId, body.product_id) : substitutions.propose(T(s), orderId, body.product_id, body);
      logAction(s, "substitution." + (body.unavailable ? "unavailable" : "propose"), "order", orderId, { product: body.product_id, status: r.status }, req);
      json(res, 200, { substitution: r });
    } catch (e) { engineFail(res, e); }
  }
  async function apiOrderCancel(req, res, url, s, body, id) {
    const o = get("SELECT * FROM orders WHERE id=? AND tenant_id=? AND owner=?", Number(id), T(s), ownerFor(s));
    if (!o) return bad(res, "Order not found", 404);
    try {
      const r = await orderFlow.cancel(T(s), o, { byShopper: true, reason: String(body.reason || "customer_cancelled"), actor: ownerFor(s), notify: (t, x) => notify(T(s), t, x) });
      logAction(s, "order.cancel", "order", o.id, { num: o.num, refunded: r.refunded, owed: r.owed }, req);
      json(res, 200, { ok: true, refunded: r.refunded, owed: r.owed });
    } catch (e) { engineFail(res, e); }
  }
  function apiOrderInvoice(req, res, url, s, body, id) {
    const o = get("SELECT * FROM orders WHERE id=? AND tenant_id=? AND owner=?", Number(id), T(s), ownerFor(s));
    if (!o) return bad(res, "Order not found", 404);
    const items = all("SELECT * FROM order_items WHERE order_id=?", o.id);
    const body0 = items.map((it, i) => ({ line: i + 1, description: String(it.product_id), qty: it.qty, unit_price: it.price, amount: +(it.qty * it.price).toFixed(2) }));
    const kinds = registry.list("shopDocKinds").map(x => x.key || x);
    const kind = kinds.includes(body.kind) ? body.kind : "tax_invoice";
    const ref = "DOC-" + Date.now().toString(36).toUpperCase().slice(-6);
    const r = run("INSERT INTO invoice_documents(tenant_id,ref,order_id,owner,doc_kind,invoice_number,place_of_supply,gstin,pan,taxable,tax,total,currency,body,status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?, 'generated')",
      T(s), ref, o.id, ownerFor(s), kind, o.num, String(o.state || ""), "", "",
      +(o.sub - o.gift_used).toFixed(2), +o.tax.toFixed(2), +o.total.toFixed(2), String(o.currency || require("../defaults.js").currency(T(s))), JSON.stringify(body0));
    json(res, 200, { doc: get("SELECT * FROM invoice_documents WHERE id=?", r.lastInsertRowid) });
  }

  return [
    ["GET /api/substitutions", apiSubstitutionsMine],
    ["POST /api/substitutions/:id", (r, re, u, s, b, p) => apiSubstitutionDecide(r, re, u, s, b, p)],
    ["GET /api/admin/substitutions/:orderId", (r, re, u, s, b, p) => apiAdminSubstitutions(r, re, u, s, b, p)],
    ["POST /api/admin/substitutions/:orderId", (r, re, u, s, b, p) => apiAdminSubstitutionAct(r, re, u, s, b, p)],
    ["POST /api/orders/:id/cancel", (r, re, u, s, b, p) => apiOrderCancel(r, re, u, s, b, p)],
    ["POST /api/orders/:id/invoice", (r, re, u, s, b, p) => apiOrderInvoice(r, re, u, s, b, p)],
    ["GET /api/orders", apiOrders],
    ["GET /api/admin/orders", apiAdminOrders],
    ["PUT /api/admin/orders/:id/status", (r, re, u, s, b, p) => apiAdminOrderStatus(r, re, u, s, b, p)]
  ];
} };
