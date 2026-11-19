/* LUXORA Platform — supply domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the supply domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "supply", routes(kit) {
  const { CFG, T, bad, json, logAction, planning, requireAdmin } = kit;

  /* ---------------- supply-chain planning ---------------- */
  function apiAdminPlanList(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    const c = CFG(s);
    if (!c.features.planning) return bad(res, "Supply-chain planning is disabled", 403);
    json(res, 200, {
      replenishments: planning.listReplenishments(T(s), {
        status: url.searchParams.get("status") || "",
        priority: url.searchParams.get("priority") || "",
        product_id: url.searchParams.get("product_id") || "",
        q: url.searchParams.get("q") || ""
      }),
      stats: planning.summary(T(s)), statuses: planning.STATUSES, priorities: planning.PRIORITIES
    });
  }
  function apiAdminPlanRun(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    if (!CFG(s).features.planning) return bad(res, "Supply-chain planning is disabled", 403);
    const written = planning.runPlan(T(s));
    logAction(s, "planning.run", "replenishment", written.length, { skus: written.length });
    json(res, 200, { planned: written.length, stats: planning.summary(T(s)) });
  }
  function apiAdminPlanStatus(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    if (!CFG(s).features.planning) return bad(res, "Supply-chain planning is disabled", 403);
    try {
      const r = planning.setStatus(T(s), id, String(body.status || ""), body.po_ref);
      logAction(s, "planning.status", "replenishment", id, { status: body.status });
      json(res, 200, { replenishment: r });
    } catch (e) { bad(res, e.message, 400); }
  }
  function apiAdminPlanApproveAll(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    if (!CFG(s).features.planning) return bad(res, "Supply-chain planning is disabled", 403);
    const approved = planning.approveAll(T(s));
    logAction(s, "planning.approveAll", "replenishment", approved.length, { approved: approved.length });
    json(res, 200, { approved: approved.length, stats: planning.summary(T(s)) });
  }
  function apiAdminPlanPos(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    if (!CFG(s).features.planning) return bad(res, "Supply-chain planning is disabled", 403);
    json(res, 200, { purchaseOrders: planning.purchaseOrders(T(s)) });
  }

  return [
    ["GET /api/admin/planning", apiAdminPlanList],
    ["POST /api/admin/planning/run", apiAdminPlanRun],
    ["PUT /api/admin/planning/:id", (r, re, u, s, b, p) => apiAdminPlanStatus(r, re, u, s, b, p)],
    ["POST /api/admin/planning/approve-all", apiAdminPlanApproveAll],
    ["GET /api/admin/planning/pos", apiAdminPlanPos]
  ];
} };
