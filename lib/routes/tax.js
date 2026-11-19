/* LUXORA Platform — tax domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the tax domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "tax", routes(kit) {
  const { CFG, T, bad, enterprise, json, requireAdmin, taxmod } = kit;

  function apiAdminTaxConfig(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    const cfg = taxmod.configFor(T(s));
    const q = (url.searchParams.get("country") && url.searchParams.get("number")) ? taxmod.validateNumber(url.searchParams.get("country"), url.searchParams.get("number")) : null;
    json(res, 200, { country: cfg.country, rule: cfg.rule, classes: cfg.classes, storeRate: (CFG(s).commerce || {}).taxRate, taxNumber: q });
  }
  function apiAdminTaxQuote(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, taxmod.quote({ tenantId: T(s), country: body.country, lines: (body.lines || []).map(l => ({ id: l.id, class: l.class, amount: Number(l.amount) || 0, tax_rule: l.tax_rule || {} })), buyerVat: body.vatId, inclusive: !!body.inclusive })); } catch (e) { return bad(res, e.message); }
  }
  function apiTaxReport(req, res, url, s) { if (!requireAdmin(s, res)) return; json(res, 200, enterprise.taxReport(T(s), url.searchParams.get("period"))); }

  return [
    ["GET /api/admin/tax/report", apiTaxReport],
    ["GET /api/admin/tax", apiAdminTaxConfig],
    ["POST /api/admin/tax/quote", apiAdminTaxQuote]
  ];
} };
