/* LUXORA Platform — engagement domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the engagement domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "engagement", routes(kit) {
  const { CFG, T, alertView, alerts, all, bad, cartPayload, commerceOf, compareRow, get, json, listView, lists, ownerFor, run, shopperCall, shopperName, signedIn } = kit;

  function apiSavedAdd(req, res, url, s, body) {
    if (!CFG(s).features.saveForLater) return bad(res, "Save for later is disabled", 403);
    const owner = ownerFor(s);
    run("INSERT OR IGNORE INTO saved_items(owner,product_id) VALUES(?,?)", owner, body.id);
    run("DELETE FROM cart_items WHERE owner=? AND product_id=?", owner, body.id);
    json(res, 200, cartPayload(s));
  }
  function apiSavedDel(req, res, url, s, body, id) {
    run("DELETE FROM saved_items WHERE owner=? AND product_id=?", ownerFor(s), id);
    json(res, 200, cartPayload(s));
  }
  function apiSavedMove(req, res, url, s, body, id) {
    const owner = ownerFor(s);
    run("DELETE FROM saved_items WHERE owner=? AND product_id=?", owner, id);
    const ex = get("SELECT qty FROM cart_items WHERE owner=? AND product_id=?", owner, id);
    if (ex) run("UPDATE cart_items SET qty=qty+1 WHERE owner=? AND product_id=?", owner, id);
    else run("INSERT INTO cart_items(owner,product_id,qty) VALUES(?,?,1)", owner, id);
    json(res, 200, cartPayload(s));
  }
  function apiViewed(req, res, url, s, body) {
    const owner = ownerFor(s);
    /* what was viewed with what is learnt before the view is written; a view from a shelf is that shelf's click (lib/recommendations.js) */
    const R = require("../recommendations.js");
    try { R.learnView(T(s), owner, body.id); if (body.rf) R.clicked(T(s), owner, body.id, String(body.rf)); } catch (e) { console.error("recommendations view:", e.message); }
    run("INSERT OR REPLACE INTO view_history(owner,product_id,seen_at) VALUES(?,?,datetime('now'))", owner, body.id);
    const ids = all("SELECT product_id FROM view_history WHERE owner=? ORDER BY seen_at DESC LIMIT 12", owner).map(r => r.product_id);
    /* L8: the ids came from the DB, but interpolating them into SQL contradicts the "parameterized
       SQL only" rule and is exactly the shape that becomes an injection later — bind them. */
    if (ids.length) {
      const marks = ids.map(() => "?").join(",");
      run(`DELETE FROM view_history WHERE owner=? AND product_id NOT IN (${marks})`, owner, ...ids);
    }
    json(res, 200, { ok: true, viewed: ids });
  }
  function apiCompare(req, res, url, s) {
    const row = compareRow(T(s), ownerFor(s));
    const ids = JSON.parse(row.product_ids || "[]");
    const products = ids.length ? all(`SELECT * FROM products WHERE tenant_id=? AND id IN (${ids.map(() => "?").join(",")}) AND deleted_at IS NULL`, T(s), ...ids) : [];
    json(res, 200, { ids, products });
  }
  function apiCompareAdd(req, res, url, s, body) {
    const row = compareRow(T(s), ownerFor(s));
    const ids = JSON.parse(row.product_ids || "[]");
    const id = String(body.product_id || body.id || "");
    if (id && !ids.includes(id) && ids.length < 4) ids.push(id);
    run("UPDATE compare_lists SET product_ids=? WHERE id=?", JSON.stringify(ids), row.id);
    json(res, 200, { ids });
  }
  function apiCompareRemove(req, res, url, s, body) {
    const row = compareRow(T(s), ownerFor(s));
    const ids = JSON.parse(row.product_ids || "[]").filter(x => x !== String(body.product_id || body.id));
    run("UPDATE compare_lists SET product_ids=? WHERE id=?", JSON.stringify(ids), row.id);
    json(res, 200, { ids });
  }
  function apiLists(req, res, url, s) { if (signedIn(s, res, "keep lists")) shopperCall(res, () => ({ lists: lists.mine(T(s), ownerFor(s)), ...lists.vocabulary() })); }
  function apiListCreate(req, res, url, s, body) { if (signedIn(s, res, "keep lists")) shopperCall(res, () => ({ list: listView(s, lists.create(T(s), ownerFor(s), shopperName(s), body)) })); }
  function apiListGet(req, res, url, s, body, id) { if (signedIn(s, res, "keep lists")) shopperCall(res, () => ({ list: listView(s, lists.get(T(s), ownerFor(s), id)), ...lists.vocabulary() })); }
  function apiListUpdate(req, res, url, s, body, id) { if (signedIn(s, res, "keep lists")) shopperCall(res, () => ({ list: listView(s, lists.update(T(s), ownerFor(s), id, body)) })); }
  function apiListDelete(req, res, url, s, body, id) { if (signedIn(s, res, "keep lists")) shopperCall(res, () => lists.remove(T(s), ownerFor(s), id)); }
  function apiListItemAdd(req, res, url, s, body, id) { if (signedIn(s, res, "keep lists")) shopperCall(res, () => ({ list: listView(s, lists.addItem(T(s), ownerFor(s), id, body)) })); }
  function apiListItemUpdate(req, res, url, s, body, id) { if (signedIn(s, res, "keep lists")) shopperCall(res, () => ({ list: listView(s, lists.updateItem(T(s), ownerFor(s), id, body)) })); }
  function apiListItemDelete(req, res, url, s, body, id) { if (signedIn(s, res, "keep lists")) shopperCall(res, () => ({ list: listView(s, lists.removeItem(T(s), ownerFor(s), id)) })); }
  function apiSharedList(req, res, url, s, body, token) { shopperCall(res, () => ({ list: listView(s, lists.shared(T(s), token)) })); }
  function apiSharedListPurchased(req, res, url, s, body, token) { shopperCall(res, () => ({ list: listView(s, lists.markPurchased(T(s), token, body.item_id, body.qty)) })); }
  function apiListsFind(req, res, url, s) { shopperCall(res, () => ({ lists: lists.findable(T(s), url.searchParams.get("q") || "") })); }
  function apiAlerts(req, res, url, s) {
    if (signedIn(s, res, "set alerts")) shopperCall(res, () => ({ alerts: alerts.mine(T(s), ownerFor(s)).map(w => alertView(s, w)), kinds: alerts.kinds(T(s), url.searchParams.get("product") || "") }));
  }
  function apiAlertCreate(req, res, url, s, body) {
    if (!signedIn(s, res, "set alerts")) return;
    const cm = commerceOf(s);
    const target = Number(body.target_price) > 0 ? Number(body.target_price) / (Number(cm.fx) || 1) : null;
    shopperCall(res, () => ({ alert: alertView(s, alerts.watch(T(s), ownerFor(s), { ...body, target_price: target })) }));
  }
  function apiAlertDelete(req, res, url, s, body, id) { if (signedIn(s, res, "set alerts")) shopperCall(res, () => ({ alert: alertView(s, alerts.cancel(T(s), ownerFor(s), id)) })); }

  return [
    ["GET /api/compare", apiCompare],
    ["POST /api/compare", apiCompareAdd],
    ["POST /api/compare/remove", apiCompareRemove],
    ["GET /api/lists", apiLists],
    ["POST /api/lists", apiListCreate],
    ["GET /api/lists/find", apiListsFind],
    ["GET /api/lists/:id", (r, re, u, s, b, p) => apiListGet(r, re, u, s, b, p)],
    ["PUT /api/lists/:id", (r, re, u, s, b, p) => apiListUpdate(r, re, u, s, b, p)],
    ["DELETE /api/lists/:id", (r, re, u, s, b, p) => apiListDelete(r, re, u, s, b, p)],
    ["POST /api/lists/:id/items", (r, re, u, s, b, p) => apiListItemAdd(r, re, u, s, b, p)],
    ["PUT /api/list-items/:id", (r, re, u, s, b, p) => apiListItemUpdate(r, re, u, s, b, p)],
    ["DELETE /api/list-items/:id", (r, re, u, s, b, p) => apiListItemDelete(r, re, u, s, b, p)],
    ["GET /api/shared-lists/:token", (r, re, u, s, b, p) => apiSharedList(r, re, u, s, b, p)],
    ["POST /api/shared-lists/:token/purchased", (r, re, u, s, b, p) => apiSharedListPurchased(r, re, u, s, b, p)],
    ["GET /api/alerts", apiAlerts],
    ["POST /api/alerts", apiAlertCreate],
    ["DELETE /api/alerts/:id", (r, re, u, s, b, p) => apiAlertDelete(r, re, u, s, b, p)],
    ["POST /api/saved", apiSavedAdd],
    ["DELETE /api/saved/:id", (r, re, u, s, b, p) => apiSavedDel(r, re, u, s, b, p)],
    ["POST /api/saved/:id/move", (r, re, u, s, b, p) => apiSavedMove(r, re, u, s, b, p)],
    ["POST /api/viewed", apiViewed]
  ];
} };
