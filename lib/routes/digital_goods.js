/* LUXORA Platform — digital_goods domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the digital_goods domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "digital_goods", routes(kit) {
  const { T, actor, byOf, deliv, ownerFor, requireAdmin, requireStaff, shopperCall, signedIn } = kit;

  function apiDeliverableKinds(req, res, url, s) { shopperCall(res, () => ({ kinds: deliv().kinds() })); }
  function apiDeliverablesMine(req, res, url, s) { if (signedIn(s, res, "see what your orders delivered")) shopperCall(res, () => ({ deliverables: deliv().mine(T(s), ownerFor(s)) })); }
  function apiDeliverableStep(req, res, url, s, body, id) { if (signedIn(s, res, "record progress")) shopperCall(res, () => ({ deliverable: deliv().step(T(s), ownerFor(s), id) })); }
  function apiAdminDeliverables(req, res, url, s, body, kind) { if (requireStaff(s, res)) shopperCall(res, () => deliv().forStaff(T(s), kind)); }
  function apiAdminDeliverablePool(req, res, url, s, body, kind) { if (requireAdmin(s, res)) shopperCall(res, () => deliv().stock(T(s), kind, body.product_id, body.codes)); }
  function apiAdminDeliverableUpload(req, res, url, s, body, id) { if (requireStaff(s, res)) shopperCall(res, () => ({ deliverable: deliv().upload(T(s), id, body.value, byOf(s) || actor(s)[0]) })); }

  return [
    ["GET /api/deliverable-kinds", apiDeliverableKinds],
    ["GET /api/deliverables", apiDeliverablesMine],
    ["POST /api/deliverables/:id/step", (r, re, u, s, b, p) => apiDeliverableStep(r, re, u, s, b, p)],
    ["GET /api/admin/deliverables/:kind", (r, re, u, s, b, p) => apiAdminDeliverables(r, re, u, s, b, p)],
    ["POST /api/admin/deliverables/:kind/pool", (r, re, u, s, b, p) => apiAdminDeliverablePool(r, re, u, s, b, p)],
    ["POST /api/admin/deliverables/item/:id", (r, re, u, s, b, p) => apiAdminDeliverableUpload(r, re, u, s, b, p)]
  ];
} };
