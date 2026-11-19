/* LUXORA Platform — advertising domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the advertising domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "advertising", routes(kit) {
  const { AD_EVENT_KINDS, T, bad, commerceOf, get, isAdmin, json, marketplace, requireStaff, rl, storeView } = kit;

  /* ---- Marketplace & Seller ecosystem (ads · bidding · attribution · take-rate) ---- */
  /* the full ad book (bids, budgets, spend) is staff data; shoppers see ads through ranking */
  function apiMktAds(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    const f = {}; if (url.searchParams.get("status")) f.status = url.searchParams.get("status"); if (url.searchParams.get("seller")) f.seller_id = url.searchParams.get("seller");
    json(res, 200, { ads: marketplace.listAds(T(s), f), bid_models: marketplace.BID_MODELS, surfaces: marketplace.AD_SURFACES });
  }
  function apiMktEvent(req, res, url, s, body, adId) {
    if (!s.user_id) return bad(res, "Sign in required", 401);
    /* which ad events a shopper may report is declared on the adEventKinds rows */
    const kinds = Array.isArray(rl("adEventKinds")) && rl("adEventKinds").length ? rl("adEventKinds") : AD_EVENT_KINDS;
    const self = kinds.filter(k => k.self_reported).map(k => k.key);
    const kind = String(body.kind || self[0] || "");
    if (!self.includes(kind) && !(s.platform_admin || isAdmin(s))) return bad(res, "Only " + self.join(" / ") + " events can be reported", 400);
    const ref = "u" + s.user_id + ":" + new Date().toISOString().slice(0, 10);
    const dup = get("SELECT id FROM ad_events WHERE tenant_id=? AND ad_id=? AND kind=? AND ref=?", T(s), Number(adId), kind, ref);
    if (dup) return json(res, 200, { event_id: dup.id, duplicate: true });
    const ev = marketplace.recordEvent(T(s), Number(adId), kind, (s.platform_admin || isAdmin(s)) && body.ref ? String(body.ref) : ref);
    json(res, 200, { event_id: ev });
  }
  /* sponsored results: the auction's winners for a surface (and a search), as product cards */
  function apiSponsored(req, res, url, s) {
    const cm = commerceOf(s);
    const surface = url.searchParams.get("surface") || require("../defaults.js").of("mktSurfaces");
    const exclude = String(url.searchParams.get("exclude") || "").split(",").filter(Boolean);
    const out = marketplace.sponsored(T(s), surface, { q: url.searchParams.get("q") || "", slots: Number(url.searchParams.get("slots")) || 0, exclude,
      viewer: s.user_id ? "u" + s.user_id : "s" + s.sid });
    json(res, 200, { label: out.label, items: out.items.map(it => ({ ad: it.ad, position: it.position, product: storeView({ ...it.product, about: [] }, cm) })) });
  }

  return [
    ["GET /api/marketplace/sponsored", apiSponsored],
    ["GET /api/marketplace/ads", apiMktAds],
    ["POST /api/marketplace/ads/:id/event", (r, re, u, s, b, p) => apiMktEvent(r, re, u, s, b, p)]
  ];
} };
