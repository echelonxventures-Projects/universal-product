/* LUXORA Platform — security domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the security domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "security", routes(kit) {
  const { audit, auditChainVerify, json, requirePlatform, requirePlatformSection, sec } = kit;

  function apiPlatformSecurity(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    json(res, 200, { layers: sec.scorecard({ tls: !!process.env.LUX_TLS, keyInfo: sec.keyInfo(), pepper: !!process.env.LUXORA_PEPPER }), keyInfo: sec.keyInfo(), chain: auditChainVerify(null).ok ? "intact" : "BROKEN" });
  }
  function apiPlatformKeyRotate(req, res, url, s) {
    if (!requirePlatformSection(s, res, "security", "write")) return;
    const v = sec.rotateKey();
    audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "keys.rotate", "platform", v, {});
    json(res, 200, { ok: true, version: v, keys: sec.keyInfo() });
  }

  return [
    ["GET /api/platform/security", apiPlatformSecurity],
    ["POST /api/platform/keys/rotate", apiPlatformKeyRotate]
  ];
} };
