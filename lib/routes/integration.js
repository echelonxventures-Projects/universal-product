/* LUXORA Platform — integration domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the integration domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "integration", routes(kit) {
  const { CFG, T, ai, all, applyGatewayEvent, audit, bad, cartPayload, commerceOf, connect, enterprise, events, gatewaySecrets, get, globalmod, json, logAction, money2, outboundOffline, permittedCarriers, permittedGateways, registry, requireAdmin, requirePlatform, rl, ruleCtx, run } = kit;

  function apiProviders(req, res, url, s) {
    const c = CFG(s);
    const country = registry.countryProfile(c.commerce.country);
    const cm2 = commerceOf(s);
    const q = k => url.searchParams.get(k);
    const amount = q("amount") != null && q("amount") !== "" && isFinite(Number(q("amount"))) ? Number(q("amount")) : (cartPayload(s).items.length ? +cartPayload(s).items.reduce((n, x) => n + x.unitBase * x.qty, 0).toFixed(2) : undefined);
    const rctx = ruleCtx(s, "checkout.gateways", { amount });
    const gws = permittedGateways(s, rctx).map(g => ({ id: g.id, name: g.name, emoji: g.emoji, methods: g.methods, feePct: g.feePct, mode: g.mode, primary: g.is_primary }));
    json(res, 200, {
      country: { code: country.code, name: country.name, currency: country.currency, symbol: country.symbol, locale: country.locale },
      gateways: gws, carriers: permittedCarriers(s, rctx).map(x => ({ id: x.id, name: x.name, emoji: x.emoji, eta: x.eta, baseFee: x.baseFee != null ? money2(cm2, x.baseFee) : undefined, freeOver: x.freeOver, primary: x.is_primary })),
      tax: { mode: commerceOf(s).taxMode, rate: commerceOf(s).taxRate }, taxModes: registry.taxModes()
    });
  }
  function apiAdminCustomProviders(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { providers: all("SELECT * FROM custom_providers WHERE scope='tenant' AND tenant_id=?", T(s)) });
  }
  function apiAdminCustomProviderAdd(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const m = body.manifest;
    if (!m || !m.id || !m.name) return bad(res, "Manifest needs id and name");
    const kind = rl("providerKinds").includes(body.kind) ? body.kind : "payment";
    run("INSERT INTO custom_providers(scope,tenant_id,kind,manifest) VALUES('tenant',?,?,?)", T(s), kind, JSON.stringify(m));
    logAction(s, "provider.add", "custom_provider", m.id, { kind });
    json(res, 200, { ok: true });
  }
  function apiAdminCustomProviderDelete(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    run("DELETE FROM custom_providers WHERE id=? AND scope='tenant' AND tenant_id=?", Number(id), T(s));
    json(res, 200, { ok: true });
  }
  function apiPlatformCustomProviders(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    json(res, 200, {
      builtIn: { payment: registry.providerDefs("payment"), shipping: registry.providerDefs("shipping"), notification: registry.providerDefs("notification"), tax: registry.taxModes(), ai: registry.providerDefs("ai") },
      countries: registry.countries(), availability: all("SELECT * FROM provider_availability ORDER BY provider_id"),
      custom: all("SELECT * FROM custom_providers WHERE scope='platform'")
    });
  }
  function apiPlatformCustomProviderAdd(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    const m = body.manifest && typeof body.manifest === "object" ? { ...body.manifest } : null;
    if (!m || !m.id || !m.name) return bad(res, "Manifest needs id and name");
    if (!/^[a-z0-9][a-z0-9_-]{1,63}$/i.test(String(m.id))) return bad(res, "Manifest id must be 2-64 letters, numbers, underscores or hyphens", 422);
    const kind = rl("providerKinds").includes(body.kind) ? body.kind : "payment";
    let integration = m.spec;
    if (typeof integration === "string") { try { integration = JSON.parse(integration); } catch (e) { return bad(res, "Integration spec must be valid JSON", 422); } }
    if (["payment", "notification", "marketing"].includes(kind)) {
      const error = require("../spec.js").validate(integration);
      if (error) return bad(res, "Integration spec: " + error, 422);
      m.spec = integration;
    } else if (integration != null) {
      const error = require("../spec.js").validate(integration);
      if (error) return bad(res, "Integration spec: " + error, 422);
      m.spec = integration;
    }
    const manifestJson = JSON.stringify(m);
    const existing = all("SELECT id,manifest FROM custom_providers WHERE scope='platform' AND kind=?", kind).find(row => { try { return JSON.parse(row.manifest || "{}").id === m.id; } catch (e) { return false; } });
    let customId = existing && existing.id;
    if (existing) run("UPDATE custom_providers SET manifest=? WHERE id=?", manifestJson, existing.id);
    else { const inserted = run("INSERT INTO custom_providers(scope,kind,manifest) VALUES('platform',?,?)", kind, manifestJson); customId = Number(inserted.lastInsertRowid); }
    try {
      run(`INSERT INTO provider_defs(id,kind,name,emoji,description,methods,fee_pct,fee_fixed,fields,spec,base_fee,position,enabled,global) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,1,?)
           ON CONFLICT(id,kind) DO UPDATE SET name=excluded.name,emoji=excluded.emoji,description=excluded.description,methods=excluded.methods,fee_pct=excluded.fee_pct,fee_fixed=excluded.fee_fixed,fields=excluded.fields,spec=excluded.spec,enabled=1,global=excluded.global`,
        String(m.id), kind, String(m.name), String(m.emoji || "🔌"), String(m.desc || ""), JSON.stringify(m.methods || []), Number(m.feePct) || 0, Number(m.feeFixed) || 0, JSON.stringify(m.fields || []), JSON.stringify(m.spec || {}), Number(m.baseFee) || 0, 900, (m.countries || []).includes("*") ? 1 : 0);
      const codes = (m.countries || []).includes("*") ? all("SELECT code FROM countries").map(c => c.code) : (m.countries || []);
      for (const cc of codes) run("INSERT OR IGNORE INTO provider_availability(provider_id,country_code) VALUES(?,?)", String(m.id), cc);
      /* a manifest that names every country ("*") is a worldwide provider, so provisioning
         ranks a country's own providers ahead of it */
      if ((m.countries || []).includes("*")) run("UPDATE provider_defs SET global=1 WHERE id=? AND kind=?", String(m.id), kind);
    } catch (e) { console.error("provider_defs sync:", e.message); }
    audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "provider.add", "custom_provider", m.id, { kind });
    json(res, 200, { ok: true, id: customId });
  }
  function apiPlatformCustomProviderDelete(req, res, url, s, body, id) {
    if (!requirePlatform(s, res)) return;
    const row = get("SELECT id,kind,manifest FROM custom_providers WHERE id=? AND scope='platform'", Number(id));
    if (!row) return bad(res, "Provider not found", 404);
    let manifest = {}; try { manifest = JSON.parse(row.manifest || "{}"); } catch (e) { }
    const providerId = String(manifest.id || "");
    run("DELETE FROM custom_providers WHERE id=? AND scope='platform'", Number(id));
    if (providerId) {
      run("DELETE FROM tenant_gateways WHERE provider_id=?", globalmod.gatewayId(row.kind, providerId));
      run("DELETE FROM provider_availability WHERE provider_id=?", providerId);
      run("DELETE FROM provider_defs WHERE id=? AND kind=?", providerId, row.kind);
    }
    audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "provider.delete", "custom_provider", providerId || row.id, { kind: row.kind });
    json(res, 200, { ok: true });
  }
  /* ---------- webhooks (outbound events) + universal entity metadata (tags/notes via global uid) ---------- */
  function apiWebhooksList(req, res, url, s) { if (!requireAdmin(s, res)) return; json(res, 200, Object.assign({ events: events.webhookEvents() }, events.list(T(s)))); }
  function apiWebhookCreate(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const urlErr = events.validateUrl(body.url);
    if (urlErr) return bad(res, urlErr, 400);
    const id = events.create(T(s), body); logAction(s, "webhook.create", "webhook", id, { url: body.url, events: body.events }, req);
    json(res, 200, { ok: true, id });
  }
  function apiWebhookUpdate(req, res, url, s, body, id) { if (!requireAdmin(s, res)) return; if (body && body.url != null) { const urlErr = events.validateUrl(body.url); if (urlErr) return bad(res, urlErr, 400); } if (!events.update(Number(id), T(s), body)) return bad(res, "Not found", 404); logAction(s, "webhook.update", "webhook", id, {}, req); json(res, 200, { ok: true }); }
  function apiWebhookDelete(req, res, url, s, body, id) { if (!requireAdmin(s, res)) return; if (!events.remove(Number(id), T(s))) return bad(res, "Not found", 404); logAction(s, "webhook.delete", "webhook", id); json(res, 200, { ok: true }); }
  function apiWebhookTest(req, res, url, s, body, id) {
    return (async () => {
      if (!requireAdmin(s, res)) return;
      /* the test delivers ONE fixed event to THIS webhook only — it used to fan a caller-named,
         signed event out to every subscriber and create a new wildcard webhook on each call */
      const w = get("SELECT id FROM webhooks WHERE id=? AND tenant_id=?", Number(id), T(s));
      if (!w) return bad(res, "Unknown webhook", 404);
      const d = run("INSERT INTO webhook_deliveries(tenant_id,webhook_id,event,subject_uid,payload,status,attempts,created_at) VALUES(?,?,?,?,?,'pending',0,datetime('now'))",
        T(s), w.id, "store.test", null, JSON.stringify({ event: "store.test", data: { message: "LUXORA webhook test", at: new Date().toISOString() } }));
      const resu = await events.deliver(Number(d.lastInsertRowid));
      json(res, 200, { ok: true, delivery: Number(d.lastInsertRowid), result: resu });
    })();
  }
  function apiWebhookDrain(req, res, url, s, body) { return (async () => { if (!requireAdmin(s, res)) return; json(res, 200, await events.drain(T(s), Number(body && body.batch) || 25)); })(); }
  /* the signature is checked over the RAW request bytes (server.js keeps them on req.rawBody)
     — re-serializing the parsed JSON changes whitespace/key order and can never match what
     the provider signed. A bad signature is a 401, so the sender sees the failure. */
  /* A payment provider's webhook. The store's own gateway signing secret (Console → Payments,
     "Webhook signing secret") is tried first and confines the event to that store's payments;
     the platform's inbound secret is the fallback for a platform-operated account. How the
     signature is checked is the provider spec's `webhook.signature` (an HMAC over the body or
     URL + body, or the provider's own verify call); a spec that declares none uses the
     platform's scheme (`sha256=` / Stripe's `t=,v1=`). Only a verified event moves money
     state, and replays are no-ops. */
  async function apiInboundWebhook(req, res, url, s, body, provider) {
    const raw = typeof req.rawBody === "string" ? req.rawBody : JSON.stringify(body || {});
    const pid = String(provider || "");
    const specDef = connect.specFor(pid, "payment");
    const sigDef = specDef && specDef.webhook && specDef.webhook.signature || null;
    const headers = {}; for (const [k, v] of Object.entries(req.headers || {})) headers[k.toLowerCase()] = Array.isArray(v) ? v[0] : v;
    const sig = sigDef && sigDef.header ? headers[String(sigDef.header).toLowerCase()] || "" : (headers["x-lux-signature"] || "");
    let evt = null; try { evt = JSON.parse(raw); } catch (e) { }
    const hookUrl = cfg => (cfg && cfg.webhookUrl) || ((headers["x-forwarded-proto"] || (req.socket && req.socket.encrypted ? "https" : "http")) + "://" + (headers["x-forwarded-host"] || headers.host || "") + req.url);
    const verify = async (secret, cfg) => {
      if (sigDef && sigDef.api) {
        if (!cfg || outboundOffline() || !evt) return false;
        try { return await require("../spec.js").verifyByApi(sigDef, { config: cfg, extra: { headers, event: evt } }, connect.request); } catch (e) { return false; }
      }
      const h = require("../spec.js").verifyHmac(sigDef, secret, raw, headers, hookUrl(cfg));
      return h === null ? (secret ? enterprise.verifyInbound(secret, raw, sig) : false) : h;
    };
    let scope = null;
    const storeCfg = s && s.tenant ? gatewaySecrets(T(s), pid) : null;
    if (storeCfg && storeCfg.cfg && (storeCfg.cfg.webhookSecret || (sigDef && sigDef.api)) && await verify(storeCfg.cfg.webhookSecret, storeCfg.cfg)) scope = T(s);
    let r;
    if (scope) r = { ok: true, signatureOk: true, scope: "store" };
    else { r = enterprise.inboundWebhook(pid, raw, sig, sigDef && !sigDef.api ? (secret => require("../spec.js").verifyHmac(sigDef, secret, raw, headers, hookUrl(null))) : null); if (r.ok) scope = "platform"; }
    if (!r.ok) return json(res, 401, r);
    const e = evt ? require("../spec.js").webhookEvent(specDef, evt) : null;
    r.applied = !evt ? { ok: false, reason: "unparseable" } : (!e || !e.ref) ? { ok: true, ignored: true } : await applyGatewayEvent(scope === "platform" ? null : scope, pid, e, "webhook");
    json(res, 200, r);
  }

  return [
    ["GET /api/providers", apiProviders],
    ["GET /api/admin/custom-providers", apiAdminCustomProviders],
    ["POST /api/admin/custom-providers", apiAdminCustomProviderAdd],
    ["DELETE /api/admin/custom-providers/:id", (r, re, u, s, b, p) => apiAdminCustomProviderDelete(r, re, u, s, b, p)],
    ["POST /api/webhooks/inbound/:provider", (r, re, u, s, b, p) => apiInboundWebhook(r, re, u, s, b, p)],
    ["GET /api/admin/webhooks", apiWebhooksList],
    ["POST /api/admin/webhooks", apiWebhookCreate],
    ["PUT /api/admin/webhooks/:id", (r, re, u, s, b, p) => apiWebhookUpdate(r, re, u, s, b, p)],
    ["DELETE /api/admin/webhooks/:id", (r, re, u, s, b, p) => apiWebhookDelete(r, re, u, s, b, p)],
    ["POST /api/admin/webhooks/:id/test", (r, re, u, s, b, p) => apiWebhookTest(r, re, u, s, b, p)],
    ["POST /api/admin/webhooks/drain", apiWebhookDrain],
    ["GET /api/platform/custom-providers", apiPlatformCustomProviders],
    ["POST /api/platform/custom-providers", apiPlatformCustomProviderAdd],
    ["DELETE /api/platform/custom-providers/:id", (r, re, u, s, b, p) => apiPlatformCustomProviderDelete(r, re, u, s, b, p)]
  ];
} };
