/* LUXORA Platform — offer domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the offer domain; what it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "offer", routes(kit) {
  const { CFG, J, T, actor, all, audit, bad, by, cartPayload, commerceOf, engineFail, entity, fintech, get, goip, isAdmin, json, logAction, meta, mods, offers, ownerFor, registry, requireAdmin, requirePlatform, requireStaff, rl, rules, run, sec, shopperCall, signedIn, stIs, toBase } = kit;

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
  function apiPlatformOffers(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    const global = all("SELECT * FROM offers WHERE tenant_id=0 ORDER BY id DESC").map(mapOffer);
    const period = new Date().toISOString().slice(0, 7);
    json(res, 200, {
      global, stats: offers.stats(), redemptions: require("../coupons.js").redemptions(0, 200),
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
    const out = goip.widget(T(s), { distribution: url.searchParams.get("channel") || undefined, channel: url.searchParams.get("exchange_channel") || require("../defaults.js").of("offerChannels"), currency: commerceOf(s).currency });
    if (out.error) return bad(res, out.error, out.code || 404);
    if (url.searchParams.get("embed") === "1") { res.writeHead(200, { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" }); return res.end(out.html); }
    json(res, 200, out);
  }

  return [
    ["GET /api/offers", apiOffersList],
    ["POST /api/offers", (r, re, u, s, b) => apiOfferSave(r, re, u, s, b, null)],
    ["PUT /api/offers/:id", (r, re, u, s, b, p) => apiOfferSave(r, re, u, s, b, p)],
    ["DELETE /api/offers/:id", (r, re, u, s, b, p) => apiOfferDelete(r, re, u, s, b, p)],
    ["POST /api/offers/preview", apiOffersPreview],
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
