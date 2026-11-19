/* LUXORA Platform — health domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the health domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "health", routes(kit) {
  const { T, ownerFor, records, requireStaff, shopperCall, signedIn } = kit;

  function apiVault(req, res, url, s) { if (signedIn(s, res, "open your records")) shopperCall(res, () => records().vault(T(s), ownerFor(s))); }
  function apiVaultKeep(req, res, url, s, body) { if (signedIn(s, res, "keep a record")) shopperCall(res, () => ({ record: records().keep(T(s), ownerFor(s), body) })); }
  function apiVaultShare(req, res, url, s, body) { if (signedIn(s, res, "share a record")) shopperCall(res, () => ({ share: records().share(T(s), ownerFor(s), body) })); }
  function apiVaultUnshare(req, res, url, s, body, id) { if (signedIn(s, res, "stop sharing")) shopperCall(res, () => records().unshare(T(s), ownerFor(s), id)); }
  /* what a party has been shown (staff read what shoppers shared with the store) */
  function apiAdminRecordsShared(req, res, url, s) { if (requireStaff(s, res)) shopperCall(res, () => ({ shared: records().sharedWith(T(s), url.searchParams.get("party") || "") })); }

  return [
    ["GET /api/health-records", apiVault],
    ["POST /api/health-records", apiVaultKeep],
    ["POST /api/health-records/shares", apiVaultShare],
    ["DELETE /api/health-records/shares/:id", (r, re, u, s, b, p) => apiVaultUnshare(r, re, u, s, b, p)],
    ["GET /api/admin/health-records/shared", apiAdminRecordsShared]
  ];
} };
