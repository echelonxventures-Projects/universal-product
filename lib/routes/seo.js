/* LUXORA Platform — seo domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the seo domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "seo", routes(kit) {
  const { T, all, bad, enterprise, get, json, logAction, requireSection, requireStaff, sitemapMod } = kit;

  function apiSeoSitemap(req, res, url, s) {
    if (!require("../gates.js").on(T(s), "seo.tools")) return bad(res, require("../gates.js").message("seo.tools"), 403);
    const prods = all("SELECT id FROM products WHERE tenant_id=? AND lifecycle='published'", T(s)).map(r => `  <url><loc>/product.html?id=${r.id}</loc></url>`).join("\n");
    const deps = all("SELECT key FROM departments WHERE tenant_id=? AND active=1", T(s)).map(r => `  <url><loc>/results.html?dept=${r.key}</loc></url>`).join("\n");
    res.writeHead(200, { "Content-Type": "application/xml; charset=utf-8" });
    res.end(`<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url><loc>/</loc></url>\n${deps}\n${prods}\n</urlset>`);
  }
  function apiFeeds(req, res, url, s, body, slug) { const fmt = /csv$/i.test(String(slug)) ? "csv" : "xml"; slug = String(slug || "").replace(/\.(xml|csv)$/i, ""); const t = get("SELECT id,slug FROM tenants WHERE slug=?", slug); if (!t) return bad(res, "Unknown store", 404); const feed = enterprise.productFeed(t.id, t.slug, fmt); res.writeHead(200, { "Content-Type": feed.type + "; charset=utf-8" }); res.end(feed.body); }
  function apiSitemap(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    json(res, 200, { sitemap: sitemapMod.get(T(s)) });
  }
  function apiSitemapXML(req, res, url, s) {
    if (!require("../gates.js").on(T(s), "seo.tools")) return bad(res, require("../gates.js").message("seo.tools"), 403);
    const xml = sitemapMod.generateXML(sitemapMod.buildSitemapEntries(T(s)));
    res.writeHead(200, { 'Content-Type': 'application/xml; charset=utf-8' });
    res.end(xml);
  }
  function apiSitemapGenerate(req, res, url, s, body) {
    if (!requireStaff(s, res)) return;
    const r = sitemapMod.generate(T(s), 'xml');
    if (r.error) return bad(res, r.error, r.code || 400);
    logAction(s, "sitemap.generate", "sitemap", null, { entries: r.entries }, req);
    json(res, 200, { ok: true, generated_at: r.last_generated, entries: r.entries, chunks: r.chunks });
  }
  function apiSitemapConfig(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    json(res, 200, { config: sitemapMod.getConfig(T(s)) });
  }
  function apiSitemapConfigUpdate(req, res, url, s, body) {
    if (!requireSection(s, res, "settings", "write")) return;
    let config;
    try { config = sitemapMod.updateConfig(T(s), body || {}); } catch (e) { return bad(res, e.message, 400); }
    logAction(s, "sitemap.config", "sitemap", null, {}, req);
    json(res, 200, { ok: true, config });
  }

  return [
    ["GET /api/feeds/:slug", apiFeeds],
    ["GET /api/seo/sitemap.xml", apiSeoSitemap],
    ["GET /api/sitemap", apiSitemap],
    ["GET /api/sitemap.xml", apiSitemapXML],
    ["POST /api/sitemap/generate", apiSitemapGenerate],
    ["GET /api/sitemap/config", apiSitemapConfig],
    ["PUT /api/sitemap/config", apiSitemapConfigUpdate]
  ];
} };
