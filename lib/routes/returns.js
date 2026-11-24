/* LUXORA Platform — returns domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the returns domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "returns", routes(kit) {
  const { T, all, bad, engineFail, get, json, logAction, logistics, returns, ownerFor, requireAdmin, requireSection } = kit;
  const actorOf = s => s.platform_admin ? s.platform_admin.email : "user:" + s.user_id;

  async function apiReturnDisposition(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try {
      if (!requireSection(s, res, "returns", "write")) return;
      const r = await logistics.returnDisposition(T(s), Number(id), String(body.disposition), body.extra || {}, { actor: actorOf(s) });
      logAction(s, "logistics.return.disposition", "return", r.id, { disposition: body.disposition });
      json(res, 200, { return: r });
    } catch (e) { engineFail(res, e); }
  }
  function apiReturnCreate(req, res, url, s, body) {
    const o = get("SELECT * FROM orders WHERE num=? AND owner=? AND tenant_id=?", String(body.order_num || ""), ownerFor(s), T(s));
    if (!o) return bad(res, "Order not found", 404);
    try {
      const made = returns.requestReturn(T(s), o, body);
      logAction(s, "return.create", "return", made.map(r => r.ref).join(","), { order: o.num, items: made.length });
      json(res, 200, { ok: true, ref: made[0].ref, returns: made });
    } catch (e) { engineFail(res, e); }
  }
  function apiAdminReturns(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { returns: all("SELECT r.*, o.num order_num FROM returns r LEFT JOIN orders o ON o.id=r.order_id WHERE r.tenant_id=? ORDER BY r.created_at DESC", T(s)) });
  }
  async function apiAdminReturnUpdate(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    const r = get("SELECT * FROM returns WHERE id=? AND tenant_id=?", Number(id), T(s));
    if (!r) return bad(res, "Unknown return", 404);
    try {
      const out = await returns.setReturn(T(s), r, String(body.status || ""), { amount: body.amount, restock: body.restock, actor: actorOf(s) });
      logAction(s, "return.update", "return", id, { status: body.status, refunded: out.refunded }, req);
      json(res, 200, { ok: true, ...out });
    } catch (e) { engineFail(res, e); }
  }

  return [
    ["POST /api/returns", apiReturnCreate],
    ["PUT /api/admin/returns/:id/disposition", (r, re, u, s, b, p) => apiReturnDisposition(r, re, u, s, b, p)],
    ["GET /api/admin/returns", apiAdminReturns],
    ["PUT /api/admin/returns/:id", (r, re, u, s, b, p) => apiAdminReturnUpdate(r, re, u, s, b, p)]
  ];
} };
