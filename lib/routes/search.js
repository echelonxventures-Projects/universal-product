/* LUXORA Platform — search domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the search domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "search", routes(kit) {
  const { DEMO_DEFAULT_PASSWORDS, T, all, bad, buildSearch, commerceOf, firstMatching, get, hintsAllowed, json, ownerFor, platSetting, search, storeView, verifyPlatformAdminAsync, verifyUserAsync } = kit;

  /* ---- Search & Discovery (faceted + typo-tolerant + recommendation) ---- */
  function apiSearch(req, res, url, s) {
    const f = {
      q: url.searchParams.get("q") || "",
      sort: url.searchParams.get("sort") || "relevance",
      page: url.searchParams.get("page") || "1",
      limit: url.searchParams.get("limit") || "20",
      facets: {}
    };
    for (const k of ["dept", "type", "brand", "pmin", "pmax", "rating"]) if (url.searchParams.get(k)) f.facets[k] = url.searchParams.get(k);
    json(res, 200, search.search(T(s), f));
  }
  function apiSuggest(req, res, url, s) {
    json(res, 200, { prefix: url.searchParams.get("prefix") || "", items: search.suggest(T(s), url.searchParams.get("prefix") || "", Number(url.searchParams.get("limit") || 10)) });
  }
  function apiRecommend(req, res, url, s) {
    json(res, 200, { anchor: url.searchParams.get("anchor") || "", owner: s.user_id ? ownerFor(s) : "", items: search.recommend(T(s), { anchor: url.searchParams.get("anchor") || "", owner: s.user_id ? ownerFor(s) : "", limit: Number(url.searchParams.get("limit") || 12) }) });
  }
  async function apiPlatformHint(req, res) {
    if (!hintsAllowed()) return json(res, 200, { demo: false });
    const h = platSetting("demo_hint", { enabled: true, platformEmail: "platform@luxora.shop" });
    const email = String(h.platformEmail || "");
    const pw = await firstMatching(DEMO_DEFAULT_PASSWORDS, c => verifyPlatformAdminAsync(email, c));
    if (!pw) return json(res, 200, { demo: false });
    json(res, 200, { demo: true, email, password: pw });
  }
  async function apiHint(req, res, url, s) {
    if (!hintsAllowed()) return json(res, 200, { demo: false });
    const adm = get("SELECT email FROM users WHERE tenant_id=? AND role='admin' ORDER BY id LIMIT 1", T(s));
    if (!adm) return json(res, 200, { demo: true, email: null });
    const pw = await firstMatching(DEMO_DEFAULT_PASSWORDS, c => verifyUserAsync(T(s), adm.email, c));
    /* the admin's address is shown only alongside a still-default password — a store whose
       admin has set their own password is not advertising who administers it */
    if (!pw) return json(res, 200, { demo: false });
    json(res, 200, { demo: true, email: adm.email, password: pw, store: s.tenant.slug });
  }
  function apiReco(req, res, url, s, body, id) {
    if (!require("../gates.js").on(T(s), "reco.engine")) return bad(res, require("../gates.js").message("reco.engine"), 403);
    let rows = all(`SELECT DISTINCT p.* FROM order_items oi
      JOIN order_items oi2 ON oi.order_id = oi2.order_id
      JOIN orders o ON o.id = oi.order_id AND o.tenant_id = ?
      JOIN products p ON p.tenant_id = o.tenant_id AND p.id = oi2.product_id
      WHERE oi.product_id = ? AND oi2.product_id != ? AND p.lifecycle='published' LIMIT 12`, T(s), id, id);
    if (rows.length < 4) {
      const cur = get("SELECT dept FROM products WHERE tenant_id=? AND id=?", T(s), id);
      rows = all("SELECT * FROM products WHERE tenant_id=? AND dept=? AND id!=? AND lifecycle='published' ORDER BY ratings_count DESC LIMIT 12", T(s), cur ? cur.dept : "", id);
    }
    const cm = commerceOf(s);
    json(res, 200, { items: rows.map(r => storeView({ ...r, about: [] }, cm)) });
  }
  function apiFacets(req, res, url, s) {
    if (!require("../gates.js").on(T(s), "listing.tools")) return bad(res, require("../gates.js").message("listing.tools"), 403);
    const { sql, args } = buildSearch(s, url);
    const rows = all(`SELECT brand, dept, price FROM products WHERE ${sql}`, ...args);
    const brands = {}, depts = {}; const buckets = { "0-25": 0, "25-50": 0, "50-100": 0, "100-250": 0, "250+": 0 };
    for (const r of rows) {
      brands[r.brand] = (brands[r.brand] || 0) + 1; depts[r.dept] = (depts[r.dept] || 0) + 1;
      const k = r.price < 25 ? "0-25" : r.price < 50 ? "25-50" : r.price < 100 ? "50-100" : r.price < 250 ? "100-250" : "250+";
      buckets[k]++;
    }
    json(res, 200, { brands: Object.entries(brands).sort((a, b) => b[1] - a[1]).slice(0, 20).map(([k, v]) => ({ brand: k, count: v })), depts: Object.entries(depts).map(([k, v]) => ({ dept: k, count: v })), price: Object.entries(buckets).map(([k, v]) => ({ range: k, count: v })) });
  }

  return [
    ["GET /api/platform/hint", apiPlatformHint],
    ["GET /api/hint", apiHint],
    ["GET /api/search", apiSearch],
    ["GET /api/suggest", apiSuggest],
    ["GET /api/recommend", apiRecommend],
    ["GET /api/reco/:id", (r, re, u, s, b, p) => apiReco(r, re, u, s, b, p)],
    ["GET /api/facets", apiFacets]
  ];
} };
