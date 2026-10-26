/* LUXORA Platform — group buying domain routes (moved from lib/routes/offer.js; _registry/business-domains.json).
   Each handler answers one route of the group-buy domain: the campaigns a shopper has joined, and
   the staff surface that opens, settles and cancels them. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "groupbuy", routes(kit) {
  const { T, engineFail, groupView, groupbuy, json, logAction, ownerFor, requireAdmin, requireStaff, shopperCall, signedIn, toBase } = kit;

  /* the campaigns this shopper has joined */
  function apiGroupBuysMine(req, res, url, s) { if (signedIn(s, res, "see your groups")) shopperCall(res, () => { groupbuy.tick(T(s)); return { groups: groupbuy.mine(T(s), ownerFor(s)).map(g => groupView(s, g)) }; }); }
  /* staff: every campaign of the store */
  function apiAdminGroupBuys(req, res, url, s) { if (requireStaff(s, res)) shopperCall(res, () => { groupbuy.tick(T(s)); return { groups: groupbuy.list(T(s)).map(g => groupView(s, g)) }; }); }
  /* staff open a campaign */
  function apiAdminGroupBuyCreate(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    try { const g = groupbuy.create(T(s), { ...body, group_price: toBase(s, body.group_price) }); logAction(s, "group.create", "group_campaign", g.id, { product: g.product && g.product.id }, req); json(res, 200, { group: groupView(s, g) }); } catch (e) { engineFail(res, e); }
  }
  /* staff cancel a campaign and refund its members */
  function apiAdminGroupBuyCancel(req, res, url, s, body, id) { if (requireAdmin(s, res)) shopperCall(res, () => ({ group: groupView(s, groupbuy.cancel(T(s), id)) })); }
  /* staff settle the campaigns whose deadline has passed */
  function apiAdminGroupBuyTick(req, res, url, s) { if (requireAdmin(s, res)) shopperCall(res, () => groupbuy.tick(T(s))); }

  return [
    ["GET /api/group-buys", apiGroupBuysMine],
    ["GET /api/admin/group-buys", apiAdminGroupBuys],
    ["POST /api/admin/group-buys", apiAdminGroupBuyCreate],
    ["POST /api/admin/group-buys/tick", apiAdminGroupBuyTick],
    ["POST /api/admin/group-buys/:id/cancel", (r, re, u, s, b, p) => apiAdminGroupBuyCancel(r, re, u, s, b, p)]
  ];
} };
