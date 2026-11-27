/* LUXORA Platform — fixed assets domain routes (lib/assets.js; _registry/business-domains.json).
   The register of what a store owns, depreciation and disposal, under the store's assets section
   (the Finance role holds it). */
"use strict";

module.exports = { domain: "assets", routes(kit) {
  const { T, actor, bad, json, logAction, requireAdmin } = kit;
  const FA = () => require("../assets.js");
  const answer = (s, res, fn) => { if (!requireAdmin(s, res)) return; try { fn(); } catch (e) { bad(res, e.message, e.status || 400); } };
  const q = (url, k) => url.searchParams.get(k) || "";
  const who = s => { const a = actor(s); return Array.isArray(a) ? String(a[2] || a[1] || "") : String(a || ""); };

  /* The asset register: each asset with its cost, depreciation to date and book value; `category` and `status` narrow it; with totals by category, and the categories, methods and ways of paying. */
  function apiAssets(req, res, url, s) { answer(s, res, () => json(res, 200, { assets: FA().list(T(s), { category: q(url, "category"), status: q(url, "status") }), totals: FA().totals(T(s)), categories: FA().SEED.categories, methods: FA().SEED.methods, paidFrom: FA().SEED.paidFrom })); }
  /* Registers an asset: `name`, `category`, `cost`, `residual`, `life_months`, `method`, `acquired_on`, `in_service`, `paid_from` (bank or supplier), `supplier_id`, `currency`, `serial`, `location`. Its cost goes on the books. */
  function apiAssetRegister(req, res, url, s, body) { answer(s, res, () => { const a = FA().register(T(s), body || {}, who(s)); logAction(s, "assets.register", "fixed_asset", a.ref, { cost: a.cost }); json(res, 200, { asset: a }); }); }
  /* One asset, with every month of its depreciation, posted or to come. */
  function apiAsset(req, res, url, s, body, id) { answer(s, res, () => json(res, 200, { asset: FA().view(T(s), id), schedule: FA().schedule(T(s), id) })); }
  /* Posts depreciation for every asset up to a month (`through`, YYYY-MM; by default the last one that has ended). Each month is posted once. */
  function apiAssetsDepreciate(req, res, url, s, body) { answer(s, res, () => { const r = FA().depreciate(T(s), (body || {}).through, who(s)); logAction(s, "assets.depreciate", "fixed_asset", r.through, r); json(res, 200, r); }); }
  /* Sells (`proceeds`) or writes off (`write_off`) an asset on a `date`, saying why (`reason`): depreciated to that month, taken off the books, the gain or loss posted. */
  function apiAssetDispose(req, res, url, s, body, id) { answer(s, res, () => { const a = FA().dispose(T(s), id, body || {}, who(s)); logAction(s, "assets.dispose", "fixed_asset", a.ref, { proceeds: a.proceeds, gain: a.gain }); json(res, 200, { asset: a }); }); }

  return [
    ["GET /api/admin/assets", apiAssets],
    ["POST /api/admin/assets", apiAssetRegister],
    ["POST /api/admin/assets/depreciate", apiAssetsDepreciate],
    ["GET /api/admin/assets/:id", (r, re, u, s, b, p) => apiAsset(r, re, u, s, b, p)],
    ["POST /api/admin/assets/:id/dispose", (r, re, u, s, b, p) => apiAssetDispose(r, re, u, s, b, p)]
  ];
} };
