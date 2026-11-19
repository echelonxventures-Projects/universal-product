/* LUXORA Platform — experiments domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the experiments domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "experiments", routes(kit) {
  const { CFG, T, bad, experiments, json, ownerFor, requireAdmin } = kit;

  /* ---------------- experimentation ---------------- */
  function apiExpAssign(req, res, url, s, body, id) {
    if (!CFG(s).features.experiments) return bad(res, "Experiments are disabled", 403);
    const v = experiments.assign(T(s), String(id), ownerFor(s));
    json(res, 200, { variant: v });
  }
  function apiExpConvert(req, res, url, s, body, id) {
    if (!CFG(s).features.experiments) return bad(res, "Experiments are disabled", 403);
    json(res, 200, experiments.convert(T(s), String(id), ownerFor(s), body && body.value) || { ok: false });
  }
  function apiAdminExpList(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { experiments: experiments.listExperiments(T(s)), statuses: experiments.STATUSES });
  }
  function apiAdminExpCreate(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { experiment: experiments.createExperiment(T(s), body) }); }
    catch (e) { bad(res, e.message, 400); }
  }
  function apiAdminExpStatus(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { experiment: experiments.setStatus(T(s), id, String(body.status || "")) }); }
    catch (e) { bad(res, e.message, 400); }
  }
  function apiAdminExpResults(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    const r = experiments.results(T(s), id);
    if (!r) return bad(res, "Experiment not found", 404);
    json(res, 200, r);
  }

  return [
    ["GET /api/experiments/:id/assign", (r, re, u, s, b, p) => apiExpAssign(r, re, u, s, b, p)],
    ["POST /api/experiments/:id/convert", (r, re, u, s, b, p) => apiExpConvert(r, re, u, s, b, p)],
    ["GET /api/admin/experiments", apiAdminExpList],
    ["POST /api/admin/experiments", apiAdminExpCreate],
    ["PUT /api/admin/experiments/:id/status", (r, re, u, s, b, p) => apiAdminExpStatus(r, re, u, s, b, p)],
    ["GET /api/admin/experiments/:id/results", (r, re, u, s, b, p) => apiAdminExpResults(r, re, u, s, b, p)]
  ];
} };
