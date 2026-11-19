/* LUXORA Platform — audit domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the audit domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "audit", routes(kit) {
  const { T, all, auditChainVerify, bad, governance, json, logAction, queueNow, requireAdmin, requirePlatform } = kit;

  function apiAdminAudit(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { entries: all("SELECT * FROM audit_log WHERE tenant_id=? ORDER BY created_at DESC LIMIT 200", T(s)) });
  }
  function apiPlatformChainVerify(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    const tid = url.searchParams.get("tenant");
    json(res, 200, tid ? auditChainVerify(Number(tid)) : auditChainVerify(null));
  }
  function apiAdminChainVerify(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, auditChainVerify(T(s)));
  }
  function apiPlatformAudit(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    const t = url.searchParams.get("tenant");
    const rows = t ? all("SELECT * FROM audit_log WHERE tenant_id=? ORDER BY created_at DESC LIMIT 300", Number(t)) : all("SELECT * FROM audit_log ORDER BY created_at DESC LIMIT 300");
    json(res, 200, { entries: rows });
  }
  /* ---------- governance: trash, restore, purge, retention ---------- */
  function apiTrashList(req, res, url, s) { if (!requireAdmin(s, res)) return; json(res, 200, { counts: governance.counts(T(s)), items: governance.listTrash(T(s), 100), retention: governance.getRetention(T(s)) }); }
  function apiTrashRestore(req, res, url, s, body, key, id) {
    if (!requireAdmin(s, res)) return;
    const r = governance.restore(T(s), key, id); if (r.error) return bad(res, r.error, r.code || 400);
    logAction(s, key + ".restore", key, id, {}, req); json(res, 200, { ok: true });
  }
  function apiTrashPurge(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return; const r = governance.purge(T(s)); logAction(s, "governance.purge", "governance", null, { purged: r.purged }, req); json(res, 200, r);
  }
  function apiAdminPurgeExpired(req, res, url, s) { if (!requirePlatform(s, res)) return; let total = {}; for (const t of all("SELECT id FROM tenants")) { const r = governance.purge(t.id); Object.assign(total, r.purged); } logAction(s, "governance.purge_all", "governance", null, { purged: total }, req); json(res, 200, { ok: true, purged: total }); }
  function apiAdminExport(req, res, url, s, body, kind) {
    return (async () => {
      if (!requireAdmin(s, res)) return;
      if (!["products", "orders", "ai_usage", "serialized", "offers"].includes(kind)) return bad(res, "Unknown export kind");
      const r = await queueNow().push({ type: "export", tenantId: T(s), kind });
      json(res, 200, { ok: true, mode: r.mode || "inline", result: r.out || null, queued: !r.ran });
    })();
  }

  return [
    ["GET /api/admin/trash", apiTrashList],
    ["POST /api/admin/trash/:key/:id/restore", (r, re, u, s, b, p, i) => apiTrashRestore(r, re, u, s, b, p, i)],
    ["POST /api/admin/trash/purge", apiTrashPurge],
    ["POST /api/platform/purge-expired", apiAdminPurgeExpired],
    ["GET /api/admin/audit", apiAdminAudit],
    ["POST /api/admin/export/:kind", (r, re, u, s, b, p) => apiAdminExport(r, re, u, s, b, p)],
    ["GET /api/platform/chain/verify", apiPlatformChainVerify],
    ["GET /api/admin/chain/verify", apiAdminChainVerify],
    ["GET /api/platform/audit", apiPlatformAudit]
  ];
} };
