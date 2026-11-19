/* LUXORA Platform — product_options domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the product_options domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "product_options", routes(kit) {
  const { T, engineFail, json, logAction, options, ownerFor, requireAdmin, requireStaff, shopperCall } = kit;

  /* options */
  function apiAdminOptions(req, res, url, s) { if (requireStaff(s, res)) shopperCall(res, () => ({ groups: options.groups(T(s), url.searchParams.get("section") || ""), attached: options.attachedTo(T(s)), ...options.vocabulary(T(s)) })); }
  function apiAdminOptionSave(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    try { const g = options.saveGroup(T(s), body); logAction(s, "options.group.save", "option_group", g.id, { code: g.code }, req); json(res, 200, { group: g }); } catch (e) { engineFail(res, e); }
  }
  function apiAdminOptionDelete(req, res, url, s, body, id) { if (requireAdmin(s, res)) shopperCall(res, () => options.removeGroup(T(s), id)); }
  function apiAdminOptionAttach(req, res, url, s, body, pid) { if (requireAdmin(s, res)) shopperCall(res, () => ({ groups: options.attach(T(s), pid, body.groups) })); }
  /* what chosen options leave to be done: visits to schedule, plans in force, proofs to send */
  function apiAdminOptionFollowUps(req, res, url, s) { if (requireStaff(s, res)) shopperCall(res, () => ({ followUps: options.followUps(T(s), { orderId: url.searchParams.get("order"), section: url.searchParams.get("section") || "" }), ...options.vocabulary(T(s)) })); }
  function apiAdminOptionFollowUpMove(req, res, url, s, body, id) { if (requireStaff(s, res)) shopperCall(res, () => ({ followUp: options.moveFollowUp(T(s), id, body.action, body) })); }
  /* every kind of option group, each its own feature with its own section */
  function apiOptionKinds(req, res, url, s) { shopperCall(res, () => ({ kinds: options.vocabulary().kinds })); }
  function apiOptionFollowUpsMine(req, res, url, s) { shopperCall(res, () => ({ followUps: options.followUps(T(s), { owner: ownerFor(s) }), ...options.vocabulary(T(s)) })); }
  function apiOptionFollowUpAnswer(req, res, url, s, body, id) { shopperCall(res, () => ({ followUp: options.moveFollowUp(T(s), id, body.action, { note: body.note }, ownerFor(s)) })); }

  return [
    ["GET /api/admin/options", apiAdminOptions],
    ["POST /api/admin/options", apiAdminOptionSave],
    ["DELETE /api/admin/options/:id", (r, re, u, s, b, p) => apiAdminOptionDelete(r, re, u, s, b, p)],
    ["PUT /api/admin/options/products/:pid", (r, re, u, s, b, p) => apiAdminOptionAttach(r, re, u, s, b, p)],
    ["GET /api/admin/options/follow-ups", apiAdminOptionFollowUps],
    ["POST /api/admin/options/follow-ups/:id", (r, re, u, s, b, p) => apiAdminOptionFollowUpMove(r, re, u, s, b, p)],
    ["GET /api/options/follow-ups", apiOptionFollowUpsMine],
    ["GET /api/options/kinds", apiOptionKinds],
    ["POST /api/options/follow-ups/:id", (r, re, u, s, b, p) => apiOptionFollowUpAnswer(r, re, u, s, b, p)]
  ];
} };
