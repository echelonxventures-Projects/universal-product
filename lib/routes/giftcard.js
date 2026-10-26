/* LUXORA Platform — gift card domain routes (moved from lib/routes/offer.js; _registry/business-domains.json).
   Each handler answers one route of the gift card domain: the cards a shopper holds, the code they
   redeem, the balance they check, and the staff surface that issues and voids them. What it needs
   from the shared HTTP kit (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "giftcard", routes(kit) {
  const { T, actor, bad, json, ownerFor, requireAdmin, requireStaff, shopperCall, signedIn } = kit;
  const cards = () => require("../giftcards.js");

  /* a shopper's gift cards — bought, given, redeemed, with their codes — the values offered, and the occasions */
  function apiGiftCardsMine(req, res, url, s) { shopperCall(res, () => ({ cards: s.user_id ? cards().mine(T(s), ownerFor(s)) : [], ...cards().vocabulary(T(s)) })); }
  /* a shopper redeems a card's code into their gift balance */
  function apiGiftCardRedeem(req, res, url, s, body) {
    if (!require("../gates.js").on(T(s), "checkout.wallet")) return bad(res, require("../gates.js").message("checkout.wallet"), 403);
    if (signedIn(s, res, "redeem a gift card")) shopperCall(res, () => cards().redeem(T(s), body.code, ownerFor(s)));
  }
  /* what a code is worth and whether it can still be redeemed — nothing about who holds it */
  function apiGiftCardCheck(req, res, url, s, body) { shopperCall(res, () => ({ card: cards().check(T(s), body.code) })); }
  /* staff: every card of the store */
  function apiAdminGiftCards(req, res, url, s) { if (requireStaff(s, res)) shopperCall(res, () => ({ cards: cards().list(T(s)), ...cards().vocabulary(T(s)) })); }
  /* staff issue a card (its code is shown once, here) */
  function apiAdminGiftCardIssue(req, res, url, s, body) { if (requireAdmin(s, res)) shopperCall(res, () => ({ card: cards().issue(T(s), { ...body, source: "issued" }, actor(s)[0]) })); }
  /* staff void a card, with a reason */
  function apiAdminGiftCardVoid(req, res, url, s, body, id) { if (requireAdmin(s, res)) shopperCall(res, () => ({ card: cards().voidCard(T(s), id, body.reason, actor(s)[0]) })); }

  return [
    ["GET /api/gift-cards", apiGiftCardsMine],
    ["POST /api/gift-cards/redeem", apiGiftCardRedeem],
    ["POST /api/gift-cards/check", apiGiftCardCheck],
    ["GET /api/admin/gift-cards", apiAdminGiftCards],
    ["POST /api/admin/gift-cards", apiAdminGiftCardIssue],
    ["POST /api/admin/gift-cards/:id/void", (r, re, u, s, b, p) => apiAdminGiftCardVoid(r, re, u, s, b, p)]
  ];
} };
