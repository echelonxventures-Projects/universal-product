/* LUXORA Platform — risk domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the risk domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "risk", routes(kit) {
  const { CFG, T, bad, json, logAction, requireAdmin, risk } = kit;

  /* ---------------- risk / fraud screening ---------------- */
  function apiRiskScreen(req, res, url, s, body) {
    if (!CFG(s).features.fraudScreen) return bad(res, "Risk screening is disabled", 403);
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { event: risk.screen(T(s), body || {}) }); }
    catch (e) { bad(res, e.message, 400); }
  }
  function apiRiskBlocklist(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { email: risk.blocklist(T(s), "email"), card: risk.blocklist(T(s), "card"), address: risk.blocklist(T(s), "address"), ip: risk.blocklist(T(s), "ip") });
  }
  function apiRiskBlockAdd(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { list: risk.addBlock(T(s), String(body.kind || ""), body.value, body.note) }); }
    catch (e) { bad(res, e.message, 400); }
  }
  function apiRiskQueue(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { queue: risk.queue(T(s)), stats: risk.stats(T(s)), actions: risk.actionRows().map(r => r.key) });
  }
  function apiRiskResolve(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try {
      const ev = risk.resolve(T(s), id, String(body.decision || ""), body.note);
      logAction(s, "risk.resolve", "risk_event", id, { decision: body.decision });
      json(res, 200, { event: ev });
    } catch (e) { bad(res, e.message, 400); }
  }

  return [
    ["POST /api/admin/risk/screen", apiRiskScreen],
    ["GET /api/admin/risk/blocklist", apiRiskBlocklist],
    ["POST /api/admin/risk/blocklist", apiRiskBlockAdd],
    ["GET /api/admin/risk/queue", apiRiskQueue],
    ["PUT /api/admin/risk/:id/resolve", (r, re, u, s, b, p) => apiRiskResolve(r, re, u, s, b, p)]
  ];
} };
