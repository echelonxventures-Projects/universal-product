/* LUXORA Platform — coupon domain routes (moved from lib/routes/offer.js; _registry/business-domains.json).
   Each handler answers one route of the coupon domain: the code a shopper applies at the cart,
   and the staff surface that issues, generates and voids them. What it needs from the shared HTTP
   kit (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "coupon", routes(kit) {
  const { CFG, T, actor, all, bad, cartPayload, get, json, logAction, ownerFor, requireAdmin, run, sec, shopperCall } = kit;
  const coupons = () => require("../coupons.js");

  /* a shopper applies a code at the cart — or removes the one they had */
  function apiCoupon(req, res, url, s, body) {
    if (!sec.policy().provisioning.couponsAllowed) return bad(res, "Promo codes are disabled by platform policy", 403);
    if (!CFG(s).features.coupons) return bad(res, "Promo codes are disabled for this store", 403);
    const code = String(body.code || "").trim().toUpperCase();
    if (code) {
      const v = coupons().validate(T(s), code, s.user_id ? ownerFor(s) : "");
      if (!v.ok) return bad(res, v.reason || "Invalid or expired promo code", 404);
    }
    run("UPDATE tenant_state SET coupon=? WHERE sid=? AND tenant_id=?", code, s.sid, T(s));
    s.coupon = code;
    logAction(s, code ? "coupon.apply" : "coupon.remove", "coupon", code);
    json(res, 200, cartPayload(s));
  }
  /* staff: the store's codes and what they were worth */
  function apiCouponsList(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { coupons: coupons().list(T(s)), redemptions: coupons().redemptions(T(s)) });
  }
  /* staff issue one code */
  function apiCouponCreate(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const r = coupons().issue(T(s), Object.assign({}, body, { count: 1 }));
    if (r.error) return bad(res, r.error, r.code || 400);
    logAction(s, "coupon.create", "coupon", r.code, { kind: body.kind, funder: body.funder }, req);
    json(res, 200, { ok: true, code: r.code, id: Number((get("SELECT id FROM coupons WHERE tenant_id=? AND code=?", T(s), r.code) || {}).id || 0) });
  }
  /* staff generate a batch of codes */
  function apiCouponGenerate(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const r = coupons().issue(T(s), Object.assign({}, body, { count: Math.min(1000, Math.max(1, Number(body.count) || 1)), prefix: body.prefix || "CPN" }));
    if (r.error) return bad(res, r.error, r.code || 400);
    logAction(s, "coupon.generate", "coupon", r.batch, { count: r.count }, req);
    json(res, 200, { ok: true, batch: r.batch, count: r.count, codes: r.codes });
  }
  /* staff void one code */
  function apiCouponVoid(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    const r = run("UPDATE coupons SET status='revoked' WHERE id=? AND tenant_id=?", Number(id), T(s)); if (!r.changes) return bad(res, "Not found", 404);
    logAction(s, "coupon.void", "coupon", id); json(res, 200, { ok: true });
  }
  /* the redemption ledger's performance */
  function apiCouponsAnalytics(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, Object.assign({ redemptions: coupons().redemptions(T(s)) }, coupons().analytics(T(s))));
  }

  return [
    ["POST /api/coupon", apiCoupon],
    ["GET /api/offers/coupons", apiCouponsList],
    ["POST /api/offers/coupons", apiCouponCreate],
    ["POST /api/offers/coupons/generate", apiCouponGenerate],
    ["DELETE /api/offers/coupons/:id", (r, re, u, s, b, p) => apiCouponVoid(r, re, u, s, b, p)],
    ["GET /api/offers/analytics", apiCouponsAnalytics]
  ];
} };
