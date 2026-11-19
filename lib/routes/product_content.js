/* LUXORA Platform — product_content domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the product_content domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "product_content", routes(kit) {
  const { T, all, byOf, engineFail, json, logAction, requireAdmin, requireStaff, richcontent, shopperCall } = kit;

  /* rich product content (staff author on a brand's behalf, and review) */
  function apiAdminRich(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    shopperCall(res, () => ({ content: richcontent.list(T(s), { tag: url.searchParams.get("tag") || "", product_id: url.searchParams.get("product") || "" }), ...richcontent.vocabulary(),
      sellers: all("SELECT id, name FROM sellers WHERE tenant_id=? ORDER BY name", T(s)) }));
  }
  function apiAdminRichSave(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    try { const r = richcontent.save(T(s), body, byOf(s)); logAction(s, "rich_content.save", "rich_content", r.id, { product: r.product_id, version: r.version }, req); json(res, 200, { content: r }); }
    catch (e) { engineFail(res, e); }
  }
  function apiAdminRichAct(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try { const r = richcontent.act(T(s), id, String(body.action || ""), byOf(s), body.notes); logAction(s, "rich_content." + String(body.action || ""), "rich_content", id, { status: r.status }, req); json(res, 200, { content: r }); }
    catch (e) { engineFail(res, e); }
  }

  return [
    ["GET /api/admin/rich-content", apiAdminRich],
    ["POST /api/admin/rich-content", apiAdminRichSave],
    ["POST /api/admin/rich-content/:id", (r, re, u, s, b, p) => apiAdminRichAct(r, re, u, s, b, p)]
  ];
} };
