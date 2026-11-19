/* LUXORA Platform — currency domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the currency domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "currency", routes(kit) {
  const { all, applyRates, audit, bad, fxRate, httpGetJson, json, meta, platGet, platSet, registry, requirePlatform, requirePlatformSection, rl } = kit;

  function apiFxConvert(req, res, url, s) {
    const from = (url.searchParams.get("from") || "").toUpperCase(), to = (url.searchParams.get("to") || "").toUpperCase();
    const amount = Number(url.searchParams.get("amount") != null ? url.searchParams.get("amount") : 1);
    const r = fxRate(from, to);
    if (!r) return bad(res, "Unknown currency pair — both codes must exist in the currencies registry", 404);
    json(res, 200, { from, to, amount, rate: r.rate, result: +(amount * r.rate).toFixed(r.to.decimals), decimals: r.to.decimals, asOf: new Date().toISOString() });
  }
  function apiPlatformFx(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    const fxs = rl("fxSources").length ? rl("fxSources") : meta.FX_SOURCES;
    json(res, 200, { currencies: registry.currencies(), sources: fxs, provider: platGet("fx_provider", { provider: (fxs.find(x => x.default) || fxs[0] || {}).key, url: "" }), history: all("SELECT * FROM fx_rates ORDER BY id DESC LIMIT 60"), lastSync: platGet("fx_last_sync", null) });
  }
  function apiPlatformFxRates(req, res, url, s, body) {
    if (!requirePlatformSection(s, res, "geo", "write")) return;
    if (!body || typeof body.rates !== "object") return bad(res, "rates object required, e.g. { \"EUR\": 1.08 }");
    const r = applyRates(body.rates, "manual", body.note, s);
    json(res, 200, { ...r, currencies: registry.currencies() });
  }
  function apiPlatformFxProvider(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    const fxs = rl("fxSources").length ? rl("fxSources") : meta.FX_SOURCES;
    const src = fxs.find(x => x.key === body.provider) || fxs.find(x => x.default) || fxs[0] || {};
    const provider = src.key;
    if (src.fetches && !/^https?:\/\//.test(String(body.url || ""))) return bad(res, (src.name || provider) + " needs an http(s) URL");
    platSet("fx_provider", { provider, url: String(body.url || "").slice(0, 300) });
    audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "fx.provider", "fx", provider, { url: String(body.url || "") });
    json(res, 200, { ok: true, provider: { provider, url: String(body.url || "") } });
  }
  async function apiPlatformFxSync(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    const fxs = rl("fxSources").length ? rl("fxSources") : meta.FX_SOURCES;
    const cfg = platGet("fx_provider", { provider: (fxs.find(x => x.default) || fxs[0] || {}).key, url: "" });
    if (!(fxs.find(x => x.key === cfg.provider) || {}).fetches || !cfg.url) return bad(res, "No feed provider configured — set it under FX feed first");
    try {
      const data = await httpGetJson(cfg.url);
      const rates = (data && data.rates) || data;
      if (!rates || typeof rates !== "object" || Array.isArray(rates)) return bad(res, "Feed JSON must be {CODE: usdValue} or {rates:{…}}");
      rates.USD = 1;
      const r = applyRates(rates, "feed", cfg.url, s);
      const stamp = new Date().toISOString();
      platSet("fx_last_sync", { at: stamp, applied: r.applied, skipped: r.skipped });
      json(res, 200, { ok: true, ...r, at: stamp });
    } catch (e) { bad(res, e.message, 502); }
  }

  return [
    ["GET /api/fx", apiFxConvert],
    ["GET /api/platform/fx", apiPlatformFx],
    ["POST /api/platform/fx/rates", apiPlatformFxRates],
    ["PUT /api/platform/fx/provider", apiPlatformFxProvider],
    ["POST /api/platform/fx/sync", (r, re, u, s, b) => apiPlatformFxSync(r, re, u, s)]
  ];
} };
