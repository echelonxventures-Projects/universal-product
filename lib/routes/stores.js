/* LUXORA Platform — stores domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the stores domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "stores", routes(kit) {
  const { T, bad, get, json, requireAdmin, setupStatus } = kit;

  /* the store's own view of its setup checklist — the same steps the platform sees (setupStatus) */
  function apiAdminSetup(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    const st = setupStatus(get("SELECT * FROM tenants WHERE id=?", T(s)));
    if (!st) return bad(res, "Unknown store", 404);
    json(res, 200, { steps: st.steps, done: st.done, total: st.total, available: st.available });
  }

  return [
    ["GET /api/admin/setup", apiAdminSetup]
  ];
} };
