/* LUXORA Platform — storefront domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the storefront domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "storefront", routes(kit) {
  const { CFG, J, T, all, bad, caps, commerceOf, json, kindBrief, logAction, mods, money2, registry, requireAdmin, requirePlatform, requireStaff, run, settings, themes } = kit;

  function apiConfig(req, res, url, s) {
    const c = CFG(s); const cm = commerceOf(s);
    /* the language this answer is in (lib/expression.js): the shopper's choice, their browser's,
       the store's locale's, else the source language */
    const E = require("../expression.js");
    const lang = E.pick(req, url, cm.locale);
    /* the universal theme cascade: product → dept → tenant → platform, then the store's
       own settings.theme. The storefront receives one resolved skin, whatever scope it
       was assigned at. */
    const themeResolved = themes.resolve({ tenantId: T(s) }) || null;
    json(res, 200, {
      tenant: { id: s.tenant.id, slug: s.tenant.slug, name: s.tenant.name, mode: s.tenant.mode, kind: kindBrief(s.tenant), industries: J(s.tenant.industries, []) },
      brand: c.brand, theme: themeResolved ? { ...c.theme, ...themeResolved.vars, __theme: themeResolved } : c.theme,
      commerce: { ...cm, freeShipThreshold: money2(cm, c.commerce.freeShipThreshold), shipFee: money2(cm, c.commerce.shipFee) }, features: c.features, copy: E.copyFor(lang.lang, settings.DEFAULTS.copy, E.savedCopy(T(s)), cm.locale), lang: lang.lang, dir: E.direction(lang.lang), languages: E.available().map(l => ({ key: l.key, native: l.native, direction: l.direction })),
      geo: { countries: registry.countries().filter(c => c.active !== 0), taxModes: registry.taxModes(), currencies: registry.currencies(), subdivisions: registry.subdivisionsFor(cm.country) },
      capabilities: [...mods.caps(T(s))].filter(c => mods.hasCap(T(s), c)), gates: require("../gates.js").all(T(s)),
      /* the shopper-facing atoms (catalog rows marked shopper) and whether each is on here, so
         the storefront offers lists, alerts, pickup points and sponsored results only where they work */
      atoms: Object.fromEntries(caps.CATALOG.filter(a => a.shopper).map(a => [a.key, caps.on(T(s), a.key)])),
      departments: all("SELECT key,label,icon FROM departments WHERE tenant_id=? AND active=1 ORDER BY position", T(s)),
      brands: all("SELECT key,label,icon,logo,country FROM brands WHERE tenant_id=? AND active=1 ORDER BY position", T(s)),
      home: {
        banners: all("SELECT id,title,subtitle,cta,hue,dept FROM home_banners WHERE tenant_id=? AND active=1 ORDER BY position", T(s)),
        cards: all("SELECT id,title,dept,tiles FROM home_cards WHERE tenant_id=? AND active=1 ORDER BY position", T(s)).map(r => ({ ...r, tiles: JSON.parse(r.tiles || "[]") }))
      }
    });
  }
  /* ---------- universal theming API ----------
     Themes are data: presets are read, assigned at any scope, and created from any hue.
     Reads are open to a logged-in merchant (they need to see their own skin); writes
     to presets and assignments are platform-owned, because a theme dresses the store. */
  function apiThemes(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    json(res, 200, { presets: themes.presets(), assignments: themes.assignments() });
  }
  function apiThemeResolve(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    const ctx = { tenantId: T(s), dept: url.searchParams.get("dept"), productId: url.searchParams.get("product_id") };
    const t = themes.resolve(ctx);
    json(res, 200, { theme: t, via: t && t.via, fallback: !t });
  }
  function apiThemeAssign(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    const scope = String(body && body.scope || "").trim();
    const scopeKey = String(body && body.scope_key != null ? body.scope_key : (body.scope === "tenant" ? T(s) : "")).trim();
    const themeKey = String(body && body.theme_key || "").trim();
    if (!["platform", "tenant", "dept", "product"].includes(scope)) return bad(res, "scope must be platform | tenant | dept | product", 400);
    if (!scopeKey) return bad(res, "scope_key required", 400);
    if (!themeKey) return bad(res, "theme_key required", 400);
    const out = themes.assign(scope, scopeKey, themeKey);
    logAction(s, "theme.assign", "theme", scope + ":" + scopeKey, out, req);
    json(res, out.ok ? 200 : 409, out);
  }
  function apiThemeUnassign(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    const out = themes.unassign(String(body && body.scope || "").trim(), String(body && body.scope_key != null ? body.scope_key : "").trim());
    logAction(s, "theme.unassign", "theme", body && body.scope, out, req);
    json(res, 200, out);
  }
  /* explore the generative space: any hue → a complete theme, without committing.
     This is the "unlimited" primitive — the gallery is finite, the hue space is not */
  function apiThemePreview(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    const raw = url.searchParams.get("hue");
    if (raw === null || raw === "") return bad(res, "hue (0-359) required", 400);
    const hue = Number(raw);
    if (!isFinite(hue)) return bad(res, "hue (0-359) required", 400);
    json(res, 200, themes.previewHue(hue, !/0|false|no/i.test(url.searchParams.get("light") || "")));
  }
  /* name a hue-generated theme and keep it forever — the registry's growth path */
  function apiThemeCreate(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    const out = themes.createFromHue(body && body.key, body && body.name, body && body.hue,
      { dark: body && body.dark, mood: body && body.mood, radius: body && body.radius, radiusBtn: body && body.radiusBtn });
    logAction(s, "theme.create", "theme", out.key, out, req);
    json(res, out.ok ? 200 : 409, out);
  }
  function apiAdminBanners(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { banners: all("SELECT * FROM home_banners WHERE tenant_id=? ORDER BY position", T(s)) });
  }
  function apiAdminBannerSave(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    if (!body.title) return bad(res, "Title required");
    const t = T(s);
    const vals = [String(body.title), String(body.subtitle || ""), String(body.cta || "Discover"), Number(body.hue) || 210, String(body.dept || ""), body.active === 0 ? 0 : 1, Number(body.position) || 0];
    if (id) run("UPDATE home_banners SET title=?,subtitle=?,cta=?,hue=?,dept=?,active=?,position=? WHERE id=? AND tenant_id=?", ...vals, Number(id), t);
    else run("INSERT INTO home_banners(tenant_id,title,subtitle,cta,hue,dept,active,position) VALUES(?,?,?,?,?,?,?,?)", t, ...vals);
    logAction(s, "banner.save", "home_banner", id || "new");
    json(res, 200, { banners: all("SELECT * FROM home_banners WHERE tenant_id=? ORDER BY position", t) });
  }
  function apiAdminBannerDelete(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    run("DELETE FROM home_banners WHERE id=? AND tenant_id=?", Number(id), T(s));
    logAction(s, "banner.delete", "home_banner", id);
    json(res, 200, { ok: true });
  }
  function apiAdminCards(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { cards: all("SELECT * FROM home_cards WHERE tenant_id=? ORDER BY position", T(s)) });
  }
  function apiAdminCardSave(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    const t = T(s);
    if (!body.title || !body.dept) return bad(res, "Title and department required");
    const tiles = Array.isArray(body.tiles) ? JSON.stringify(body.tiles.slice(0, 4)) : "[]";
    const vals = [String(body.title), String(body.dept), tiles, body.active === 0 ? 0 : 1, Number(body.position) || 0];
    if (id) run("UPDATE home_cards SET title=?,dept=?,tiles=?,active=?,position=? WHERE id=? AND tenant_id=?", ...vals, Number(id), t);
    else run("INSERT INTO home_cards(tenant_id,title,dept,tiles,active,position) VALUES(?,?,?,?,?,?)", t, ...vals);
    logAction(s, "card.save", "home_card", id || "new");
    json(res, 200, { cards: all("SELECT * FROM home_cards WHERE tenant_id=? ORDER BY position", t) });
  }
  function apiAdminCardDelete(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    run("DELETE FROM home_cards WHERE id=? AND tenant_id=?", Number(id), T(s));
    logAction(s, "card.delete", "home_card", id);
    json(res, 200, { ok: true });
  }

  return [
    ["GET /api/config", apiConfig],
    ["GET /api/themes", apiThemes],
    ["GET /api/themes/resolve", apiThemeResolve],
    ["GET /api/themes/preview", apiThemePreview],
    ["POST /api/themes/assign", apiThemeAssign],
    ["POST /api/themes/unassign", apiThemeUnassign],
    ["POST /api/themes", apiThemeCreate],
    ["GET /api/admin/banners", apiAdminBanners],
    ["POST /api/admin/banners", (r, re, u, s, b, p) => apiAdminBannerSave(r, re, u, s, b, p)],
    ["PUT /api/admin/banners/:id", (r, re, u, s, b, p) => apiAdminBannerSave(r, re, u, s, b, p)],
    ["DELETE /api/admin/banners/:id", (r, re, u, s, b, p) => apiAdminBannerDelete(r, re, u, s, b, p)],
    ["GET /api/admin/cards", apiAdminCards],
    ["POST /api/admin/cards", (r, re, u, s, b, p) => apiAdminCardSave(r, re, u, s, b, p)],
    ["PUT /api/admin/cards/:id", (r, re, u, s, b, p) => apiAdminCardSave(r, re, u, s, b, p)],
    ["DELETE /api/admin/cards/:id", (r, re, u, s, b, p) => apiAdminCardDelete(r, re, u, s, b, p)]
  ];
} };
