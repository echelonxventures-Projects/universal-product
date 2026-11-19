/* LUXORA Platform — price_discovery domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the price_discovery domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "price_discovery", routes(kit) {
  const { T, auctionView, auctions, engineFail, json, logAction, negotiation, offerView, offers, ownerFor, requireAdmin, requireStaff, shopperCall, signedIn, toBase } = kit;

  /* price offers */
  function apiOffersMine(req, res, url, s) {
    if (!signedIn(s, res, "make offers")) return;
    shopperCall(res, () => ({ offers: negotiation.mine(T(s), ownerFor(s)).map(o => offerView(s, o)), received: negotiation.received(T(s), ownerFor(s)).map(o => offerView(s, o)) }));
  }
  function apiOfferMake(req, res, url, s, body) { if (signedIn(s, res, "make offers")) shopperCall(res, () => ({ offer: offerView(s, negotiation.make(T(s), ownerFor(s), { ...body, amount: toBase(s, body.amount) })) })); }
  function apiOfferRespond(req, res, url, s, body, id) {
    if (!signedIn(s, res, "answer offers")) return;
    shopperCall(res, () => ({ offer: offerView(s, negotiation.respond(T(s), { owner: ownerFor(s) }, id, String(body.action || ""), { amount: body.amount != null ? toBase(s, body.amount) : undefined })) }));
  }
  function apiAdminOffers(req, res, url, s) { if (requireStaff(s, res)) shopperCall(res, () => ({ offers: negotiation.received(T(s), "").map(o => offerView(s, o)) })); }
  function apiAdminOfferRespond(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try { const o = negotiation.respond(T(s), { owner: "", staff: true }, id, String(body.action || ""), { amount: body.amount != null ? toBase(s, body.amount) : undefined }); logAction(s, "offer." + String(body.action || ""), "price_offer", id, { status: o.status }, req); json(res, 200, { offer: offerView(s, o) }); }
    catch (e) { engineFail(res, e); }
  }
  /* auctions */
  function apiAuctions(req, res, url, s) { shopperCall(res, () => { auctions.tick(T(s)); return { auctions: auctions.list(T(s), s.user_id ? ownerFor(s) : null, url.searchParams.get("tag") || "").map(a => auctionView(s, a)) }; }); }
  function apiAuctionsMine(req, res, url, s) { if (signedIn(s, res, "see your auctions")) shopperCall(res, () => { auctions.tick(T(s)); return { auctions: auctions.mine(T(s), ownerFor(s)).map(a => auctionView(s, a)) }; }); }
  function apiAuctionCreate(req, res, url, s, body) {
    if (!signedIn(s, res, "auction your listing")) return;
    shopperCall(res, () => ({ auction: auctionView(s, auctions.create(T(s), { owner: ownerFor(s) }, { ...body, start_price: toBase(s, body.start_price), reserve_price: body.reserve_price ? toBase(s, body.reserve_price) : null, buy_now_price: body.buy_now_price ? toBase(s, body.buy_now_price) : null })) }));
  }
  function apiAuctionBid(req, res, url, s, body, id) { if (signedIn(s, res, "bid")) shopperCall(res, () => { auctions.tick(T(s)); return { auction: auctionView(s, auctions.bid(T(s), ownerFor(s), id, toBase(s, body.max_amount))) }; }); }
  function apiAuctionBuyNow(req, res, url, s, body, id) { if (signedIn(s, res, "buy")) shopperCall(res, () => ({ auction: auctionView(s, auctions.buyNow(T(s), ownerFor(s), id)) })); }
  function apiAuctionCancel(req, res, url, s, body, id) { if (signedIn(s, res, "cancel")) shopperCall(res, () => ({ auction: auctionView(s, auctions.cancel(T(s), { owner: ownerFor(s) }, id)) })); }
  function apiAdminAuctions(req, res, url, s) { if (requireStaff(s, res)) shopperCall(res, () => { auctions.tick(T(s)); return { auctions: auctions.list(T(s), null).map(a => auctionView(s, a)) }; }); }
  function apiAdminAuctionCreate(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    try { const a = auctions.create(T(s), { owner: "", staff: true }, { ...body, start_price: toBase(s, body.start_price), reserve_price: body.reserve_price ? toBase(s, body.reserve_price) : null, buy_now_price: body.buy_now_price ? toBase(s, body.buy_now_price) : null });
      logAction(s, "auction.create", "auction", a.id, { product: a.product && a.product.id }, req); json(res, 200, { auction: auctionView(s, a) }); } catch (e) { engineFail(res, e); }
  }
  function apiAdminAuctionCancel(req, res, url, s, body, id) { if (requireAdmin(s, res)) shopperCall(res, () => ({ auction: auctionView(s, auctions.cancel(T(s), { owner: "", staff: true }, id)) })); }
  function apiAdminAuctionTick(req, res, url, s) { if (requireAdmin(s, res)) shopperCall(res, () => auctions.tick(T(s))); }

  return [
    ["GET /api/price-offers", apiOffersMine],
    ["POST /api/price-offers", apiOfferMake],
    ["POST /api/price-offers/:id", (r, re, u, s, b, p) => apiOfferRespond(r, re, u, s, b, p)],
    ["GET /api/auctions", apiAuctions],
    ["GET /api/auctions/mine", apiAuctionsMine],
    ["POST /api/auctions", apiAuctionCreate],
    ["POST /api/auctions/:id/bid", (r, re, u, s, b, p) => apiAuctionBid(r, re, u, s, b, p)],
    ["POST /api/auctions/:id/buy-now", (r, re, u, s, b, p) => apiAuctionBuyNow(r, re, u, s, b, p)],
    ["POST /api/auctions/:id/cancel", (r, re, u, s, b, p) => apiAuctionCancel(r, re, u, s, b, p)],
    ["GET /api/admin/price-offers", apiAdminOffers],
    ["POST /api/admin/price-offers/:id", (r, re, u, s, b, p) => apiAdminOfferRespond(r, re, u, s, b, p)],
    ["GET /api/admin/auctions", apiAdminAuctions],
    ["POST /api/admin/auctions", apiAdminAuctionCreate],
    ["POST /api/admin/auctions/tick", apiAdminAuctionTick],
    ["POST /api/admin/auctions/:id/cancel", (r, re, u, s, b, p) => apiAdminAuctionCancel(r, re, u, s, b, p)]
  ];
} };
