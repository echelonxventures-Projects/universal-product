/* LUXORA Platform — offer domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the offer domain; what it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "offer", routes(kit) {
  const { CFG, J, T, actor, all, audit, bad, by, cartPayload, commerceOf, engineFail, entity, fintech, get, goip, groupView, groupbuy, isAdmin, json, logAction, meta, mods, offers, ownerFor, registry, requireAdmin, requirePlatform, requireStaff, rl, rules, run, sec, shopperCall, signedIn, stIn, stIs, toBase } = kit;

  function apiCoupon(req, res, url, s, body) {
    if (!sec.policy().provisioning.couponsAllowed) return bad(res, "Promo codes are disabled by platform policy", 403);
    if (!CFG(s).features.coupons) return bad(res, "Promo codes are disabled for this store", 403);
    const code = String(body.code || "").trim().toUpperCase();
    if (code) {
      const v = offers.validateCoupon(T(s), code, s.user_id ? ownerFor(s) : "");
      if (!v.ok) return bad(res, v.reason || "Invalid or expired promo code", 404);
    }
    run("UPDATE tenant_state SET coupon=? WHERE sid=? AND tenant_id=?", code, s.sid, T(s));
    s.coupon = code;
    logAction(s, code ? "coupon.apply" : "coupon.remove", "coupon", code);
    json(res, 200, cartPayload(s));
  }
  /* S4: this used to credit body.amount without ever looking at a code — a
     customer could top up their own wallet indefinitely. Redeem goes through the
     same validation the fintech voucher path uses: the code must resolve to an
     issued row for this tenant, and marking it redeemed is what authorises the
     credit. */
  function apiGiftAdd(req, res, url, s, body) {
    const c = CFG(s);
    if (!c.features.giftCards) return bad(res, "Gift cards are disabled", 403);
    if (!require("../gates.js").on(T(s), "checkout.wallet")) return bad(res, require("../gates.js").message("checkout.wallet"), 403);
    if (!body.code) return bad(res, "A gift card code is required", 400);
    try {
      const voucher = fintech.redeemVoucher(T(s), String(body.code || "").trim(), mods.ownerFor(s));
      json(res, 200, { ok: true, voucher, balance: mods.walletBalance(T(s), mods.ownerFor(s)) });
    } catch (e) { bad(res, e.message, 400); }
  }
  /* ---------------- promotions engine ---------------- */
  function activePromos(tenantId, coupon) {
    coupon = String(coupon || "").trim().toUpperCase();
    const now = new Date().toISOString().slice(0, 10);
    return all("SELECT * FROM promotions WHERE tenant_id=? AND status IN " + stIn("promotion", "running").sql + " AND (starts IS NULL OR starts<=?) AND (ends IS NULL OR ends>=?)", tenantId, ...stIn("promotion", "running").args, now, now)
      .filter(p => !p.code || p.code.toUpperCase() === coupon)
      .map(p => ({ ...p, rules: J(p.rules), scope: J(p.scope) }));
  }
  function apiPromos(req, res, url, s) {
    json(res, 200, { promotions: activePromos(T(s)).map(p => ({ id: p.id, name: p.name, type: p.type, value: p.value, code: p.code, scope: p.scope })) });
  }
  function apiAdminPromotions(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { promotions: all("SELECT * FROM promotions WHERE tenant_id=? ORDER BY id DESC", T(s)).map(p => ({ ...p, rules: J(p.rules), scope: J(p.scope) })) });
  }
  function apiAdminPromoSave(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    if (!body.name || !rl("promoTypes").some(t => t.key === body.type)) return bad(res, "Name and valid type required");
    const vals = [String(body.name), String(body.type), Number(body.value) || 0, JSON.stringify(body.rules || {}), JSON.stringify(body.scope || {}), body.starts || null, body.ends || null, body.status === "inactive" ? "inactive" : "active", String(body.code || "")];
    if (id) run("UPDATE promotions SET name=?,type=?,value=?,rules=?,scope=?,starts=?,ends=?,status=?,code=? WHERE id=? AND tenant_id=?", ...vals, Number(id), T(s));
    else run("INSERT INTO promotions(tenant_id,name,type,value,rules,scope,starts,ends,status,code) VALUES(?,?,?,?,?,?,?,?,?,?)", T(s), ...vals);
    logAction(s, "promo.save", "promotion", id || body.name);
    json(res, 200, { ok: true });
  }
  function apiAdminPromoDelete(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    run("DELETE FROM promotions WHERE id=? AND tenant_id=?", Number(id), T(s));
    logAction(s, "promo.delete", "promotion", id);
    json(res, 200, { ok: true });
  }
  function apiOffersAnalytics(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    const a = offers.analytics(T(s));
    const redemptions = all("SELECT * FROM coupon_redemptions WHERE tenant_id=? ORDER BY id DESC LIMIT 200", T(s));
    json(res, 200, Object.assign({ redemptions }, a));
  }
  /* ---------- central offers / coupons / wallet ledger ---------- */
  function mapOffer(r) { return { ...r, scope: J(r.scope_value, {}), rules: J(r.rules, {}) }; }
  function apiOffersList(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    const allowGlobal = sec.policy().provisioning.globalOffersAllowed !== false;
    const rows = all(`SELECT * FROM offers WHERE tenant_id=? ${allowGlobal ? "OR tenant_id=0" : ""} ORDER BY priority DESC, id DESC`, T(s)).map(mapOffer);
    json(res, 200, { offers: rows, active: rows.filter(o => stIs("offer", o.status, "live") && (!o.starts || o.starts <= new Date().toISOString().slice(0, 10)) && (!o.ends || o.ends >= new Date().toISOString().slice(0, 10))) });
  }
  function apiOfferSave(req, res, url, s, body, id) {
    if (!requireStaff(s, res, "goffers")) return;
    /* every write to the value-exchange record goes through GOIP — this endpoint is the legacy shape */
    const r = goip.createExchange(T(s), Object.assign({}, body, { id: id ? Number(id) : undefined }), { platform: !!s.platform_admin, actor: actor(s)[2], id: id ? Number(id) : null });
    if (r.error) return bad(res, r.error, r.code || 400);
    logAction(s, "offer.save", "offer", id || body.name, { type: body.type, benefit: r.benefit, domain: r.domain, channel: body.channel, funder: body.funder, global: r.global }, req);
    json(res, 200, { ok: true, id: r.id, uid: r.uid, domain: r.domain, benefit: r.benefit });
  }
  function apiOfferDelete(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    const o = get("SELECT id,tenant_id FROM offers WHERE id=?", Number(id)); if (!o) return bad(res, "Not found", 404);
    if (o.tenant_id !== T(s) && !(s.platform_admin && o.tenant_id === 0)) return bad(res, "Not permitted", 403);
    run("UPDATE offers SET status='inactive' WHERE id=?", Number(id)); logAction(s, "offer.retire", "offer", id); json(res, 200, { ok: true });
  }
  function apiOffersPreview(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const res2 = offers.evaluate({ channel: body.channel || require("../defaults.js").of("offerChannels"), tenantId: T(s), items: body.items || [], amount: body.amount, coupon: body.coupon, owner: body.owner || (s.user_id ? ownerFor(s) : null), currency: body.currency || commerceOf(s).currency, allowGlobal: true });
    json(res, 200, res2);
  }
  function apiCouponsList(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { coupons: all("SELECT * FROM coupons WHERE tenant_id=? OR tenant_id=0 ORDER BY id DESC", T(s)), redemptions: all("SELECT * FROM coupon_redemptions WHERE tenant_id=? ORDER BY id DESC LIMIT 200", T(s)) });
  }
  function apiCouponCreate(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const r = goip.issue(T(s), Object.assign({}, body, { count: 1 }));
    if (r.error) return bad(res, r.error, r.code || 400);
    logAction(s, "coupon.create", "coupon", r.code, { kind: body.kind, funder: body.funder }, req);
    json(res, 200, { ok: true, code: r.code, id: Number((get("SELECT id FROM coupons WHERE tenant_id=? AND code=?", T(s), r.code) || {}).id || 0) });
  }
  function apiCouponGenerate(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const r = goip.issue(T(s), Object.assign({}, body, { count: Math.min(1000, Math.max(1, Number(body.count) || 1)), prefix: body.prefix || "CPN" }));
    if (r.error) return bad(res, r.error, r.code || 400);
    logAction(s, "coupon.generate", "coupon", r.batch, { count: r.count }, req);
    json(res, 200, { ok: true, batch: r.batch, count: r.count, codes: r.codes });
  }
  function apiCouponVoid(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    const r = run("UPDATE coupons SET status='revoked' WHERE id=? AND tenant_id=?", Number(id), T(s)); if (!r.changes) return bad(res, "Not found", 404);
    logAction(s, "coupon.void", "coupon", id); json(res, 200, { ok: true });
  }
  function apiPlatformOffers(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    const global = all("SELECT * FROM offers WHERE tenant_id=0 ORDER BY id DESC").map(mapOffer);
    const period = new Date().toISOString().slice(0, 7);
    json(res, 200, {
      global, stats: offers.stats(), redemptions: all("SELECT * FROM coupon_redemptions WHERE 1=1 ORDER BY id DESC LIMIT 200"),
      manifest: goip.manifest(0), coverage: goip.coverage(),
      settlements: all("SELECT * FROM goip_settlements ORDER BY id DESC LIMIT 100").map(r => ({ ...r, meta: J(r.meta, {}) })),
      budgets: goip.budgets(0, {}), treasury: goip.treasury(0), period,
      domains: all(`SELECT COALESCE(NULLIF(domain,''),'incentive') domain, COUNT(*) n FROM offers GROUP BY 1 ORDER BY n DESC`),
      benefits: all(`SELECT COALESCE(NULLIF(benefit,''),type) benefit, COUNT(*) n FROM offers GROUP BY 1 ORDER BY n DESC`),
      meters: all("SELECT kind, SUM(qty) qty, SUM(amount) amount FROM usage_records WHERE kind LIKE 'goip.%' GROUP BY kind ORDER BY amount DESC"),
      installs: all("SELECT tm.tenant_id, t.slug, tm.status FROM tenant_modules tm JOIN tenants t ON t.id=tm.tenant_id WHERE tm.module_id='goip'")
    });
  }
  /* ---------- GOIP Ω∞ · GLOBAL OFFER INFRASTRUCTURE PLATFORM ----------
     ONE universal entry point (POST /api/goip/:capability) plus read surfaces. Consumers speak
     capabilities — create/discover/validate/apply/redeem/settle/fund/pay/govern/audit… — and never
     learn the words coupon, cashback, reward or gift card. Access follows each capability's declared
     scope: "any" (a shopper session), "tenant" (store admin) or "platform" (super admin). */
  function goipOwner(s) { return s.user_id ? ownerFor(s) : ("t" + T(s) + ":s:" + s.sid); }
  function apiGoipManifest(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    json(res, 200, goip.manifest(T(s)));
  }
  function apiGoipRegistry(req, res, url, s, body, name) {
    if (!requireStaff(s, res)) return;
    const key = String(name || "");
    if (!Object.prototype.hasOwnProperty.call(goip.REGISTRIES, key)) return bad(res, "Unknown GOIP registry: " + key, 404);
    json(res, 200, { registry: key, items: rl(key) && (Array.isArray(rl(key)) ? rl(key).length : Object.keys(rl(key)).length) ? rl(key) : goip.REGISTRIES[key] });
  }
  function apiGoipCapability(req, res, url, s, body, capKey) {
    const cap = goip.capability(capKey);
    if (!cap) return bad(res, "Unknown capability: " + capKey, 404);
    if (cap.scope === "platform") { if (!requirePlatform(s, res)) return; }
    else if (cap.scope === "tenant") { if (!requireStaff(s, res, "goip")) return; }
    const input = Object.assign({}, body || {});
    /* a shopper may only ever act as themselves; admins may name any subject */
    if (!s.platform_admin && !isAdmin(s)) { input.owner = goipOwner(s); delete input.tenant_id; delete input.scope_level; }
    else if (input.owner === undefined && ["discover", "compare", "validate", "apply", "recommend"].includes(cap.key) && s.user_id) input.owner = ownerFor(s);
    if (input.currency === undefined) input.currency = commerceOf(s).currency;
    /* a platform admin may aim a capability at any store; a store admin is pinned to their own */
    const tid = (s.platform_admin && input.tenant_id != null) ? Number(input.tenant_id) : T(s);
    const out = goip.invoke(cap.key, tid, input, { platform: !!s.platform_admin, actor: actor(s)[2] || "system" });
    if (out && out.ok === false) return bad(res, out.error || "Capability failed", out.code || 400);
    if (cap.writes) logAction(s, "goip." + cap.key, "goip", (out.result && (out.result.id || out.result.batch || out.result.reference)) || cap.key, { stage: cap.stage, engine: cap.engine }, req);
    json(res, 200, out);
  }
  function apiGoipExchanges(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    const f = { domain: url.searchParams.get("domain") || "", benefit: url.searchParams.get("benefit") || "", channel: url.searchParams.get("channel") || "", status: url.searchParams.get("status") || "", campaign: url.searchParams.get("campaign") || "", q: url.searchParams.get("q") || "", global: url.searchParams.get("global") === "1", limit: Number(url.searchParams.get("limit")) || 200 };
    json(res, 200, { exchanges: goip.listExchanges(T(s), f) });
  }
  function apiGoipExchange(req, res, url, s, body, id) {
    if (!requireStaff(s, res)) return;
    const x = goip.exchange(T(s), id); if (!x) return bad(res, "Not found", 404);
    json(res, 200, { exchange: x, audit: goip.auditTrail(T(s), x.id) });
  }
  function apiGoipContext(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    json(res, 200, goip.resolveContext({ tenantId: T(s), owner: s.user_id ? ownerFor(s) : null, amount: Number(url.searchParams.get("amount")) || 0, currency: commerceOf(s).currency, spatial: { node: url.searchParams.get("place") || "" }, calendar: url.searchParams.get("calendar") || "" }));
  }
  function apiGoipTreasury(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    json(res, 200, { treasury: goip.treasury(T(s)), budgets: goip.budgets(T(s), {}), forecast: goip.forecast(T(s), { months: 3 }) });
  }
  function apiGoipSettlements(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    json(res, 200, { settlements: goip.settlements(T(s), { period: url.searchParams.get("period") || "", status: url.searchParams.get("status") || "" }) });
  }
  function apiGoipEntitlements(req, res, url, s) {
    const owner = String(url.searchParams.get("owner") || "");
    if (!isAdmin(s) && !s.platform_admin) { if (!s.user_id) return bad(res, "Sign in required", 403); return json(res, 200, { owner: ownerFor(s), entitlements: goip.entitlementsOf(T(s), ownerFor(s)) }); }
    json(res, 200, { owner, entitlements: goip.entitlementsOf(T(s), owner || (s.user_id ? ownerFor(s) : "")) });
  }
  function apiGoipTouchpoints(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    json(res, 200, { touchpoints: goip.touchpoints(T(s), { owner: url.searchParams.get("owner") || "", party: url.searchParams.get("party") || "" }) });
  }
  function apiGoipIntelligence(req, res, url, s, body, key) {
    if (!requireStaff(s, res)) return;
    const out = goip.intel(T(s), key, { objective: url.searchParams.get("objective") || "" });
    if (out && out.error) return bad(res, out.error, 404);
    json(res, 200, { intelligence: key, result: out });
  }
  function apiGoipFeed(req, res, url, s, body, channel) {
    const out = goip.feed(T(s), channel, { currency: commerceOf(s).currency });
    if (out.error) return bad(res, out.error, out.code || 404);
    json(res, 200, out);
  }
  function apiGoipWidget(req, res, url, s) {
    const out = goip.widget(T(s), { distribution: url.searchParams.get("channel") || "widget", channel: url.searchParams.get("exchange_channel") || require("../defaults.js").of("offerChannels"), currency: commerceOf(s).currency });
    if (out.error) return bad(res, out.error, out.code || 404);
    if (url.searchParams.get("embed") === "1") { res.writeHead(200, { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" }); return res.end(out.html); }
    json(res, 200, out);
  }
  /* S2: issuing a voucher mints spendable wallet credit (redeemVoucher credits a
     real balance), so it is an operator action — never an anonymous one. Redeem
     stays owner-scoped: a shopper redeems a code they hold, validated against the
     issued row. The console's own gift_voucher entity is admin/platform-write with
     no module requirement (lib/entity.js), so this route matches it — the module
     gate belongs on the balance path (apiGiftAdd), not on the code-issuing one. */
  function apiFinVoucherIssue(req, res, url, s, body) {
    if (!requireStaff(s, res, "gfinance")) return;
    try { json(res, 200, { voucher: fintech.issueVoucher(T(s), body) }); } catch (e) { bad(res, e.message); }
  }
  function apiFinVoucherRedeem(req, res, url, s, body) {
    try { json(res, 200, { voucher: fintech.redeemVoucher(T(s), String(body.code || ""), ownerFor(s)) }); }
    catch (e) { bad(res, e.message); }
  }
  /* group buying */
  function apiGroupBuysMine(req, res, url, s) { if (signedIn(s, res, "see your groups")) shopperCall(res, () => { groupbuy.tick(T(s)); return { groups: groupbuy.mine(T(s), ownerFor(s)).map(g => groupView(s, g)) }; }); }
  function apiAdminGroupBuys(req, res, url, s) { if (requireStaff(s, res)) shopperCall(res, () => { groupbuy.tick(T(s)); return { groups: groupbuy.list(T(s)).map(g => groupView(s, g)) }; }); }
  function apiAdminGroupBuyCreate(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    try { const g = groupbuy.create(T(s), { ...body, group_price: toBase(s, body.group_price) }); logAction(s, "group.create", "group_campaign", g.id, { product: g.product && g.product.id }, req); json(res, 200, { group: groupView(s, g) }); } catch (e) { engineFail(res, e); }
  }
  function apiAdminGroupBuyCancel(req, res, url, s, body, id) { if (requireAdmin(s, res)) shopperCall(res, () => ({ group: groupView(s, groupbuy.cancel(T(s), id)) })); }
  function apiAdminGroupBuyTick(req, res, url, s) { if (requireAdmin(s, res)) shopperCall(res, () => groupbuy.tick(T(s))); }

  return [
    ["POST /api/fintech/vouchers", apiFinVoucherIssue],
    ["POST /api/fintech/vouchers/redeem", apiFinVoucherRedeem],
    ["GET /api/group-buys", apiGroupBuysMine],
    ["GET /api/admin/group-buys", apiAdminGroupBuys],
    ["POST /api/admin/group-buys", apiAdminGroupBuyCreate],
    ["POST /api/admin/group-buys/tick", apiAdminGroupBuyTick],
    ["POST /api/admin/group-buys/:id/cancel", (r, re, u, s, b, p) => apiAdminGroupBuyCancel(r, re, u, s, b, p)],
    ["GET /api/promos", apiPromos],
    ["POST /api/coupon", apiCoupon],
    ["POST /api/giftcard", apiGiftAdd],
    ["GET /api/admin/promotions", apiAdminPromotions],
    ["POST /api/admin/promotions", (r, re, u, s, b, p) => apiAdminPromoSave(r, re, u, s, b, p)],
    ["PUT /api/admin/promotions/:id", (r, re, u, s, b, p) => apiAdminPromoSave(r, re, u, s, b, p)],
    ["DELETE /api/admin/promotions/:id", (r, re, u, s, b, p) => apiAdminPromoDelete(r, re, u, s, b, p)],
    ["GET /api/offers", apiOffersList],
    ["POST /api/offers", (r, re, u, s, b) => apiOfferSave(r, re, u, s, b, null)],
    ["PUT /api/offers/:id", (r, re, u, s, b, p) => apiOfferSave(r, re, u, s, b, p)],
    ["DELETE /api/offers/:id", (r, re, u, s, b, p) => apiOfferDelete(r, re, u, s, b, p)],
    ["POST /api/offers/preview", apiOffersPreview],
    ["GET /api/offers/analytics", apiOffersAnalytics],
    ["GET /api/offers/coupons", apiCouponsList],
    ["POST /api/offers/coupons", apiCouponCreate],
    ["POST /api/offers/coupons/generate", apiCouponGenerate],
    ["DELETE /api/offers/coupons/:id", (r, re, u, s, b, p) => apiCouponVoid(r, re, u, s, b, p)],
    ["GET /api/platform/offers", apiPlatformOffers],
    ["GET /api/goip", apiGoipManifest],
    ["GET /api/goip/exchanges", apiGoipExchanges],
    ["GET /api/goip/exchanges/:id", (r, re, u, s, b, p) => apiGoipExchange(r, re, u, s, b, p)],
    ["GET /api/goip/context", apiGoipContext],
    ["GET /api/goip/treasury", apiGoipTreasury],
    ["GET /api/goip/settlements", apiGoipSettlements],
    ["GET /api/goip/entitlements", apiGoipEntitlements],
    ["GET /api/goip/touchpoints", apiGoipTouchpoints],
    ["GET /api/goip/widget", apiGoipWidget],
    ["GET /api/goip/registry/:name", (r, re, u, s, b, p) => apiGoipRegistry(r, re, u, s, b, p)],
    ["GET /api/goip/intelligence/:key", (r, re, u, s, b, p) => apiGoipIntelligence(r, re, u, s, b, p)],
    ["GET /api/goip/feed/:channel", (r, re, u, s, b, p) => apiGoipFeed(r, re, u, s, b, p)],
    ["POST /api/goip/:capability", (r, re, u, s, b, p) => apiGoipCapability(r, re, u, s, b, p)]
  ];
} };
