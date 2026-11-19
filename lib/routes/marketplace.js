/* LUXORA Platform — marketplace domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the marketplace domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "marketplace", routes(kit) {
  const { T, all, bad, brandreg, byOf, engineFail, get, isAdmin, json, listingView, listings, logAction, marketplace, mkt, offers, ownerFor, requireAdmin, requireStaff, rl, run, shopperCall, shopperName, shown, signedIn, toBase } = kit;

  function apiMktAdCreate(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const a = marketplace.createAd(T(s), body || {});
    logAction(s, "mkt.ad.create", "ad", a.id, { name: body.name, model: body.bid_model });
    json(res, 200, { ad: a });
  }
  function apiMktRank(req, res, url, s) {
    const surface = url.searchParams.get("surface") || "search";
    const slots = Number(url.searchParams.get("slots") || 3);
    json(res, 200, { surface, slots, ranked: marketplace.rankAds(T(s), surface, slots) });
  }
  function apiMktAttribute(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const r = marketplace.attribute(T(s), Number(body.order_id), Number(body.revenue) || 0, String(body.model || require("../defaults.js").of("mktAttribution")));
    json(res, 200, { attribution: r });
  }
  function apiMktSellerMetrics(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    const period = url.searchParams.get("period") || "";
    const sellerId = Number(url.searchParams.get("seller")) || null;
    json(res, 200, { sellers: sellerId ? [marketplace.sellerMetrics(T(s), sellerId, period)] : marketplace.allSellerMetrics(T(s), period), period });
  }
  function apiMktSettle(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const r = marketplace.settleTakeRate(T(s), Number(body.seller_id), String(body.period || ""));
    logAction(s, "mkt.settle.take_rate", "seller", body.seller_id, { period: body.period, commission: r.metrics.commission });
    json(res, 200, r);
  }
  /* ---------------- sellers / rfq / returns / settlements ---------------- */
  function apiAdminSellers(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { sellers: all("SELECT * FROM sellers WHERE tenant_id=? ORDER BY id", T(s)), roles: rl("sellerRoles") });
  }
  function apiAdminSellerSave(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    if (!body.name || !rl("sellerRoles").includes(body.role)) return bad(res, "Name and valid role required");
    if (id) run("UPDATE sellers SET name=?,role=?,email=?,status=?,commission_pct=? WHERE id=? AND tenant_id=?", String(body.name), String(body.role), String(body.email || ""), String(body.status || "active"), Number(body.commission_pct), Number(id), T(s));
    else run("INSERT INTO sellers(tenant_id,name,role,email,status,commission_pct) VALUES(?,?,?,?,?,?)", T(s), String(body.name), String(body.role), String(body.email || ""), "active", Number(body.commission_pct) || 5);
    logAction(s, "seller.save", "seller", id || body.name);
    json(res, 200, { ok: true });
  }
  function apiAdminSellerDelete(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    run("DELETE FROM sellers WHERE id=? AND tenant_id=?", Number(id), T(s));
    logAction(s, "seller.delete", "seller", id);
    json(res, 200, { ok: true });
  }
  /* ---------- Marketplace ---------- */
  function apiMktApply(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { onboarding: mkt.apply(T(s), body) }); } catch (e) { bad(res, e.message); }
  }
  function apiMktReview(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { onboarding: mkt.review(T(s), Number(id), String(body.decision || ""), s.platform_admin ? s.platform_admin.email : "admin", body.notes) }); }
    catch (e) { bad(res, e.message); }
  }
  function apiMktOffers(req, res, url, s, body, productId) {
    json(res, 200, { offers: mkt.listOffers(T(s), String(productId)), buybox: mkt.buyboxFor(T(s), String(productId)) });
  }
  function apiMktBuybox(req, res, url, s, body, productId) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, mkt.recomputeBuybox(T(s), String(productId)));
  }
  function apiMktFba(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { inbound: mkt.fbaInbound(T(s), body) }); } catch (e) { bad(res, e.message); }
  }
  function apiMktFbaReceive(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { inbound: mkt.receiveFba(T(s), Number(id)) }); } catch (e) { bad(res, e.message); }
  }
  function apiMktPerformance(req, res, url, s, body, sellerId) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { performance: mkt.computePerformance(T(s), Number(sellerId), body && body.period) }); }
    catch (e) { bad(res, e.message); }
  }
  /* a buyer opens a claim only on THEIR order, for at most what they paid; staff may open one
     on any order in the store. It used to accept any order id and any amount — freezing other
     buyers' escrow and, on a buyer-favourable resolution, crediting the invented amount. */
  function apiMktClaimOpen(req, res, url, s, body) {
    const b = body || {};
    const staff = !!(s.platform_admin || isAdmin(s));
    const order = get("SELECT id, owner, total FROM orders WHERE id=? AND tenant_id=?", Number(b.order_id) || 0, T(s));
    if (!order || (!staff && order.owner !== ownerFor(s))) return bad(res, "Order not found", 404);
    const amount = +Number(b.amount || 0).toFixed(2);
    if (!(amount > 0) || amount > +order.total) return bad(res, "Claim amount must be between 0 and the order total", 400);
    try {
      const claim = mkt.openClaim(T(s), { ...b, amount, buyer: staff && b.buyer ? String(b.buyer) : order.owner });
      logAction(s, "claim.open", "buyer_claim", claim.id, { order: body.order_id }, req);
      json(res, 200, { claim });
    } catch (e) { bad(res, e.message); }
  }
  function apiMktClaimResolve(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { claim: mkt.resolveClaim(T(s), Number(id), String(body.resolution || ""), s.platform_admin ? s.platform_admin.email : "admin") }); }
    catch (e) { bad(res, e.message); }
  }
  function apiMktSmart(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { smart: mkt.enrolSmart(T(s), body) }); } catch (e) { bad(res, e.message); }
  }
  function apiMktPortal(req, res, url, s, body, sellerId) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, mkt.sellerPortal(T(s), Number(sellerId))); } catch (e) { bad(res, e.message); }
  }
  /* the brand registry: claims of ownership, and an owner's infringement reports */
  function apiAdminBrandReg(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    shopperCall(res, () => ({ claims: brandreg.claims(T(s)), reports: brandreg.reports(T(s)), ...brandreg.vocabulary(T(s)) }));
  }
  function apiAdminBrandClaim(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    try { const c = brandreg.claim(T(s), body); logAction(s, "brand.claim", "brand_claim", c.id, { brand: c.brand }, req); json(res, 200, { claim: c }); } catch (e) { engineFail(res, e); }
  }
  function apiAdminBrandClaimAct(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try { const c = brandreg.decideClaim(T(s), id, String(body.action || ""), byOf(s), body.notes); logAction(s, "brand.claim." + String(body.action || ""), "brand_claim", id, { status: c.status }, req); json(res, 200, { claim: c }); }
    catch (e) { engineFail(res, e); }
  }
  function apiAdminBrandReport(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    try { const r = brandreg.report(T(s), body); logAction(s, "brand.report", "brand_report", r.id, { brand: r.brand, kind: r.kind }, req); json(res, 200, { report: r }); } catch (e) { engineFail(res, e); }
  }
  function apiAdminBrandReportAct(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try { const r = brandreg.decideReport(T(s), id, String(body.action || ""), byOf(s), body.outcome); logAction(s, "brand.report." + String(body.action || ""), "brand_report", id, { status: r.status, offers: r.offers_affected }, req); json(res, 200, { report: r }); }
    catch (e) { engineFail(res, e); }
  }
  /* shopper selling */
  function apiListingsMine(req, res, url, s) {
    if (!signedIn(s, res, "sell")) return;
    shopperCall(res, () => ({ listings: listings.mine(T(s), ownerFor(s)).map(l => listingView(s, l)), earnings: listings.earnings(T(s), ownerFor(s)).map(e => ({ ...e, gross: shown(s, e.gross), commission: shown(s, e.commission), net: shown(s, e.net) })), ...listings.vocabulary(T(s)) }));
  }
  function apiListingCreate(req, res, url, s, body) { if (signedIn(s, res, "sell")) shopperCall(res, () => ({ listing: listingView(s, listings.create(T(s), ownerFor(s), shopperName(s), { ...body, price: body.price != null ? toBase(s, body.price) : undefined })) })); }
  function apiListingUpdate(req, res, url, s, body, id) { if (signedIn(s, res, "sell")) shopperCall(res, () => ({ listing: listingView(s, listings.update(T(s), ownerFor(s), id, { ...body, price: body.price != null ? toBase(s, body.price) : undefined })) })); }
  function apiListingAct(req, res, url, s, body, id) { if (signedIn(s, res, "sell")) shopperCall(res, () => ({ listing: listingView(s, listings.act(T(s), ownerFor(s), id, String(body.action || ""))) })); }
  function apiAdminListings(req, res, url, s) { if (requireStaff(s, res)) shopperCall(res, () => ({ listings: listings.all(T(s)).map(l => listingView(s, l)), ...listings.vocabulary(T(s)) })); }
  function apiAdminListingReview(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try { const l = listings.review(T(s), id, String(body.action || ""), body.notes); logAction(s, "listing." + String(body.action || ""), "peer_listing", id, { status: l.status }, req); json(res, 200, { listing: listingView(s, l) }); } catch (e) { engineFail(res, e); }
  }

  return [
    ["POST /api/marketplace/onboarding", apiMktApply],
    ["POST /api/marketplace/onboarding/:id/review", (r, re, u, s, b, p) => apiMktReview(r, re, u, s, b, p)],
    ["GET /api/marketplace/offers/:productId", (r, re, u, s, b, p) => apiMktOffers(r, re, u, s, b, p)],
    ["POST /api/marketplace/buybox/:productId", (r, re, u, s, b, p) => apiMktBuybox(r, re, u, s, b, p)],
    ["POST /api/marketplace/fba", apiMktFba],
    ["POST /api/marketplace/fba/:id/receive", (r, re, u, s, b, p) => apiMktFbaReceive(r, re, u, s, b, p)],
    ["POST /api/marketplace/performance/:sellerId", (r, re, u, s, b, p) => apiMktPerformance(r, re, u, s, b, p)],
    ["POST /api/marketplace/claims", apiMktClaimOpen],
    ["POST /api/marketplace/claims/:id/resolve", (r, re, u, s, b, p) => apiMktClaimResolve(r, re, u, s, b, p)],
    ["POST /api/marketplace/smart-fulfilment", apiMktSmart],
    ["GET /api/marketplace/portal/:sellerId", (r, re, u, s, b, p) => apiMktPortal(r, re, u, s, b, p)],
    ["GET /api/admin/brand-registry", apiAdminBrandReg],
    ["POST /api/admin/brand-registry/claims", apiAdminBrandClaim],
    ["POST /api/admin/brand-registry/claims/:id", (r, re, u, s, b, p) => apiAdminBrandClaimAct(r, re, u, s, b, p)],
    ["POST /api/admin/brand-registry/reports", apiAdminBrandReport],
    ["POST /api/admin/brand-registry/reports/:id", (r, re, u, s, b, p) => apiAdminBrandReportAct(r, re, u, s, b, p)],
    ["GET /api/listings", apiListingsMine],
    ["POST /api/listings", apiListingCreate],
    ["PUT /api/listings/:id", (r, re, u, s, b, p) => apiListingUpdate(r, re, u, s, b, p)],
    ["POST /api/listings/:id/action", (r, re, u, s, b, p) => apiListingAct(r, re, u, s, b, p)],
    ["GET /api/admin/listings", apiAdminListings],
    ["POST /api/admin/listings/:id", (r, re, u, s, b, p) => apiAdminListingReview(r, re, u, s, b, p)],
    ["POST /api/admin/marketplace/ads", apiMktAdCreate],
    ["GET /api/marketplace/rank", apiMktRank],
    ["POST /api/admin/marketplace/attribute", apiMktAttribute],
    ["GET /api/admin/marketplace/metrics", apiMktSellerMetrics],
    ["POST /api/admin/marketplace/settle", apiMktSettle],
    ["GET /api/admin/sellers", apiAdminSellers],
    ["POST /api/admin/sellers", (r, re, u, s, b, p) => apiAdminSellerSave(r, re, u, s, b, p)],
    ["PUT /api/admin/sellers/:id", (r, re, u, s, b, p) => apiAdminSellerSave(r, re, u, s, b, p)],
    ["DELETE /api/admin/sellers/:id", (r, re, u, s, b, p) => apiAdminSellerDelete(r, re, u, s, b, p)]
  ];
} };
