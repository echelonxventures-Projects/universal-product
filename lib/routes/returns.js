/* LUXORA Platform — returns domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the returns domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "returns", routes(kit) {
  const { T, all, bad, get, json, logAction, logistics, ownerFor, requireAdmin, run, states } = kit;

  function apiReturnDisposition(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try {
      const r = logistics.returnDisposition(T(s), Number(id), String(body.disposition), body.extra || {});
      logAction(s, "logistics.return.disposition", "return", r.id, { disposition: body.disposition });
      json(res, 200, { return: r });
    } catch (e) { bad(res, e.message); }
  }
  function apiReturnCreate(req, res, url, s, body) {
    const o = get("SELECT * FROM orders WHERE num=? AND owner=?", String(body.order_num || ""), ownerFor(s));
    if (!o) return bad(res, "Order not found", 404);
    const ref = "RET-" + (2000 + get("SELECT COUNT(*) c FROM returns WHERE tenant_id=?", T(s)).c + 1);
    run("INSERT INTO returns(tenant_id,ref,order_id,product_id,qty,reason,status) VALUES(?,?,?,?,?,?,?)",
      T(s), ref, o.id, String(body.product_id || ""), Number(body.qty) || 1, String(body.reason || ""), states.initial("return"));
    logAction(s, "return.create", "return", ref, { order: o.num });
    json(res, 200, { ok: true, ref });
  }
  function apiAdminReturns(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { returns: all("SELECT r.*, o.num order_num FROM returns r LEFT JOIN orders o ON o.id=r.order_id WHERE r.tenant_id=? ORDER BY r.created_at DESC", T(s)) });
  }
  function apiAdminReturnUpdate(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    if (!states.has("return", body.status)) return bad(res, "Invalid status");
    const r = get("SELECT * FROM returns WHERE id=? AND tenant_id=?", Number(id), T(s));
    if (!r) return bad(res, "Unknown return", 404);
    /* the machine runs claw_back_offers where the transition's row names it */
    const { patch } = states.apply("return", { tenantId: T(s), from: r.status, to: body.status, row: r });
    run("UPDATE returns SET " + Object.keys(patch).map(k => k + "=?").join(", ") + " WHERE id=? AND tenant_id=?", ...Object.values(patch), Number(id), T(s));
    logAction(s, "return.update", "return", id, { status: body.status });
    json(res, 200, { ok: true });
  }

  return [
    ["POST /api/returns", apiReturnCreate],
    ["PUT /api/admin/returns/:id/disposition", (r, re, u, s, b, p) => apiReturnDisposition(r, re, u, s, b, p)],
    ["GET /api/admin/returns", apiAdminReturns],
    ["PUT /api/admin/returns/:id", (r, re, u, s, b, p) => apiAdminReturnUpdate(r, re, u, s, b, p)]
  ];
} };
