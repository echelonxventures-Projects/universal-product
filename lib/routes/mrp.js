/* LUXORA Platform — material requirements planning routes (lib/mrp.js; _registry/business-domains.json).
   Bills of materials, the master schedule, planning runs and what they suggest, under the store's
   mrp section (the Planning role holds it). */
"use strict";

module.exports = { domain: "mrp", routes(kit) {
  const { T, actor, bad, json, logAction, requireAdmin } = kit;
  const MRP = () => require("../mrp.js");
  const answer = (s, res, fn) => { if (!requireAdmin(s, res)) return; try { fn(); } catch (e) { bad(res, e.message, e.status || 400); } };
  const who = s => { const a = actor(s); return Array.isArray(a) ? String(a[2] || a[1] || "") : String(a || ""); };

  /* Planning at a glance: the latest run and its suggestions, the master schedule, and the items with a bill of materials. */
  function apiMrp(req, res, url, s) { answer(s, res, () => json(res, 200, { ...MRP().latest(T(s)), demand: MRP().demand(T(s)), boms: MRP().boms(T(s)), actions: MRP().SEED.actions })); }
  /* An item's bill of materials, with each component's own beneath it. */
  function apiMrpBom(req, res, url, s, body, id) { answer(s, res, () => json(res, 200, { bom: MRP().bom(T(s), id) })); }
  /* Replaces an item's bill of materials: `components` `[{ component_id, qty, scrap_pct }]` (empty removes it). A component is never the item itself, or anything made from it. */
  function apiMrpBomSet(req, res, url, s, body, id) { answer(s, res, () => { const b = MRP().setBom(T(s), id, (body || {}).components); logAction(s, "mrp.bom", "product", id, { components: b.components.length }); json(res, 200, { bom: b }); }); }
  /* Sets an item's planning: `lead_days` (null takes its supplier's or the default), `safety_stock`, `min_lot`. */
  function apiMrpItem(req, res, url, s, body, id) { answer(s, res, () => json(res, 200, { item: MRP().setItem(T(s), id, body || {}) })); }
  /* Adds to the master schedule: `product_id`, `qty`, `due_date`, `note`. */
  function apiMrpDemandAdd(req, res, url, s, body) { answer(s, res, () => json(res, 200, { demand: MRP().addDemand(T(s), body || {}, who(s)) })); }
  /* Removes a line of the master schedule. */
  function apiMrpDemandRemove(req, res, url, s, body, id) { answer(s, res, () => json(res, 200, MRP().removeDemand(T(s), id))); }
  /* Runs planning over `horizon_days`: what to make and buy, how many, by when, and what is late. Supersedes what the last run suggested and nobody acted on. */
  function apiMrpRun(req, res, url, s, body) { answer(s, res, () => { const r = MRP().run(T(s), body || {}, who(s)); logAction(s, "mrp.run", "mrp_run", r.run.ref, { suggestions: r.run.suggestions, late: r.run.late }); json(res, 200, r); }); }
  /* Turns suggestions (`ids`, or every open one of the latest run) into draft purchase orders, one per supplier, and planned work orders. Each is acted on once. */
  function apiMrpConvert(req, res, url, s, body) { answer(s, res, () => { const r = MRP().convert(T(s), body || {}, who(s)); logAction(s, "mrp.convert", "mrp_run", r.run && r.run.ref, { made: r.made.map(m => m.ref) }); json(res, 200, r); }); }
  /* Dismisses one suggestion. */
  function apiMrpDismiss(req, res, url, s, body, id) { answer(s, res, () => json(res, 200, MRP().dismiss(T(s), id))); }

  return [
    ["GET /api/admin/mrp", apiMrp],
    ["GET /api/admin/mrp/boms/:id", (r, re, u, s, b, p) => apiMrpBom(r, re, u, s, b, p)],
    ["PUT /api/admin/mrp/boms/:id", (r, re, u, s, b, p) => apiMrpBomSet(r, re, u, s, b, p)],
    ["PUT /api/admin/mrp/items/:id", (r, re, u, s, b, p) => apiMrpItem(r, re, u, s, b, p)],
    ["POST /api/admin/mrp/demand", apiMrpDemandAdd],
    ["DELETE /api/admin/mrp/demand/:id", (r, re, u, s, b, p) => apiMrpDemandRemove(r, re, u, s, b, p)],
    ["POST /api/admin/mrp/run", apiMrpRun],
    ["POST /api/admin/mrp/convert", apiMrpConvert],
    ["POST /api/admin/mrp/suggestions/:id/dismiss", (r, re, u, s, b, p) => apiMrpDismiss(r, re, u, s, b, p)]
  ];
} };
