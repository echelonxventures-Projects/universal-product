/* LUXORA Platform — ai domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the ai domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "ai", routes(kit) {
  const { CFG, T, actor, ai, all, bad, billing, emitEvent, get, json, logAction, offers, ownerFor, queueNow, registry, requireAdmin, requirePlatform, requireSection, run, sec, settings } = kit;

  function apiAdminAiGateways(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    const t = T(s);
    const premProviders = require("../ai.js").AI_PROVIDERS || [];
    const rows = all("SELECT * FROM tenant_gateways WHERE tenant_id=? AND provider_id LIKE 'ai:%' ORDER BY position", t);
    const list = rows.map(r => {
      const p = premProviders.find(p => p.id === r.provider_id.replace("ai:", "")) || { id: r.provider_id, name: r.provider_id, emoji: "🔌", fields: [] };
      let cfg = {}; try { cfg = JSON.parse(r.config || "{}"); } catch (e) { }
      cfg = sec.unsealConfig(t, r.provider_id, JSON.stringify(cfg));
      const masked = {};
      for (const [k, v] of Object.entries(cfg)) masked[k] = (p.fields || []).some(f => f.key === k && f.secret) ? (v ? "••••" + String(v).slice(-4) : "") : v;
      return { id: p.id, name: p.name, emoji: p.emoji, desc: p.desc, fields: p.fields, enabled: !!r.enabled, mode: r.mode, config: masked };
    });
    for (const p of premProviders) {
      const id = "ai:" + p.id;
      if (!rows.find(r => r.provider_id === id))
        list.push({ id: p.id, name: p.name, emoji: p.emoji, desc: p.desc, fields: p.fields, enabled: false, mode: "sandbox", config: {} });
    }
    json(res, 200, { gateways: list });
  }
  function apiAdminAiGatewaysPut(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    if (!requireSection(s, res, "ai", "write")) return;
    const t = T(s);
    run("DELETE FROM tenant_gateways WHERE tenant_id=? AND provider_id LIKE 'ai:%'", t);
    /* only AI providers — this route used to plant any provider id (payment, shipping) */
    const aiIds = new Set((require("../ai.js").AI_PROVIDERS || []).map(p => "ai:" + p.id));
    const ids = Object.keys(body || {}).map(k => k.startsWith("ai:") ? k : "ai:" + k);
    const badId = ids.find(k => !aiIds.has(k));
    if (badId) return bad(res, "Unknown AI provider: " + badId, 400);
    body = Object.fromEntries(Object.entries(body || {}).map(([k, v]) => [k.startsWith("ai:") ? k : "ai:" + k, v]));
    ids.forEach((id, i) => {
      const cfg = {};
      for (const [k, v] of Object.entries(body[id] || {})) if (v && !String(v).startsWith("••••") && !String(v).startsWith("lux.v1.")) cfg[k] = sec.encryptSecret(v, t + "|" + id + "|" + k);
      run("INSERT INTO tenant_gateways(tenant_id,provider_id,enabled,is_primary,mode,config,position) VALUES(?,?,?,?,?,?,?)",
        t, id, 1, 0, "sandbox", JSON.stringify(cfg), i);
    });
    logAction(s, "ai_gateways.update", "ai_provider", null, { count: ids.length });
    json(res, 200, { ok: true });
  }
  function apiAdminAiGatewayTest(req, res, url, s, body, id) {
    return (async () => {
    if (!requireAdmin(s, res)) return;
    const row = get("SELECT * FROM tenant_gateways WHERE tenant_id=? AND provider_id=?", T(s), id);
    let cfg = sec.unsealConfig(T(s), id, (row && row.config) || "{}");
    const premProviders = require("../ai.js").AI_PROVIDERS || [];
    const p = premProviders.find(p => p.id === id.replace("ai:", "")) || { fields: [] };
    const missing = (p.fields || []).filter(f => !cfg[f.key] || String(cfg[f.key]).startsWith("••••"));
    const ok = missing.length === 0;
    logAction(s, "ai_gateway.test", "ai_provider", id, { ok });
    json(res, 200, { ok, message: ok ? `✓ ${p.name} sandbox connection verified` : `Missing credentials: ${missing.map(m => m.label).join(", ")}` });
    })();
  }
  /* ---------- AI product layer (capabilities, run, usage, tasks) ---------- */
  function apiAiOverview(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { capabilities: ai.capabilities(T(s)), plan: ai.planInfo(T(s)), usage: ai.usage(T(s)), settings: CFG(s).ai || {} });
  }
  function apiAiRun(req, res, url, s, body, capability) {
    if (!requireAdmin(s, res)) return;
    if (!requireSection(s, res, "ai", "write")) return;
    const [type, , name] = actor(s);
    const out = ai.run(T(s), capability, body || {}, name || type);
    if (out.error) return bad(res, out.error, out.code || 400);
    let offerDiscount = 0;
    try { const d = offers.discountFor("ai", T(s), out.cost || 0, { owner: ownerFor(s), coupon: s.coupon }); if (d.discount) { offerDiscount = d.discount; out.cost = +Math.max(0, out.cost - d.discount).toFixed(4); } if (d.credits) offers.credit(T(s), ownerFor(s), d.credits, "cashback", "ai:" + capability, require("../defaults.js").currency(T(s)), "ai", "ai"); } catch (e) { }
    out.offer_discount = offerDiscount;
    try { if ((out.cost || 0) > 0) billing.recordUsage(T(s), "ai", capability + " · " + out.provider, out.units, (out.cost) / Math.max(1, out.units), { currency: out.currency || require("../defaults.js").platformCurrency(), period: billing.monthOf(), ref: "ai:" + capability }); } catch (e) { }
    logAction(s, "ai.run", "ai_usage", capability, { provider: out.provider, model: out.model, units: out.units, cost: out.cost, tier: out.tier }, req);
    emitEvent(T(s), "ai.usage", { capability, provider: out.provider, units: out.units, cost: out.cost, tier: out.tier }, null);
    json(res, 200, out);
  }
  function apiAiUsage(req, res, url, s) { if (!requireAdmin(s, res)) return; json(res, 200, ai.usage(T(s))); }
  function apiAiTasks(req, res, url, s) { if (!requireAdmin(s, res)) return; json(res, 200, { tasks: ai.tasks(T(s)) }); }
  function apiAiTaskCreate(req, res, url, s, body) {
    return (async () => {
    if (!requireAdmin(s, res)) return;
    if (!(ai.capabilities(T(s)).find(c => c.key === body.capability))) return bad(res, "Unknown capability");
    const id = ai.createTask(T(s), body.capability, body.params || {}, (actor(s)[2] || actor(s)[0]));
    let ran = null; if (body.runNow) ran = await queueNow().push({ type: "ai-task", id });
    logAction(s, "ai.task.create", "ai_task", id, { capability: body.capability });
    json(res, 200, { ok: true, id, queued: !!(ran && !ran.ran), tasks: ai.tasks(T(s)) });
    })();
  }
  function apiAiTaskRun(req, res, url, s, body, id) { return (async () => { if (!requireAdmin(s, res)) return; if (!get("SELECT 1 ok FROM ai_tasks WHERE id=? AND tenant_id=?", Number(id), T(s))) return bad(res, "Unknown task", 404); const r = await queueNow().push({ type: "ai-task", id: Number(id) }); json(res, 200, { result: r.out, tasks: ai.tasks(T(s)) }); })(); }
  function apiPlatformAi(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    const tenants = all("SELECT id,slug,name FROM tenants");
    const usage = all(`SELECT ai.tenant_id, t.slug, SUM(ai.cost) cost, COUNT(*) calls FROM ai_usage ai JOIN tenants t ON t.id=ai.tenant_id GROUP BY ai.tenant_id, t.slug`);
    json(res, 200, { providers: registry.providerDefs("ai"), capabilities: ai.AI_CAPABILITIES, plans: ai.AI_PLANS, tierByTenant: tenants.map(t => ({ id: t.id, slug: t.slug, name: t.name, ...ai.tierOf(t.id) })), usage });
  }

  return [
    ["GET /api/admin/ai-gateways", apiAdminAiGateways],
    ["PUT /api/admin/ai-gateways", apiAdminAiGatewaysPut],
    ["POST /api/admin/ai-gateways/:id/test", (r, re, u, s, b, p) => apiAdminAiGatewayTest(r, re, u, s, b, p)],
    ["GET /api/ai", apiAiOverview],
    ["POST /api/ai/run/:capability", (r, re, u, s, b, p) => apiAiRun(r, re, u, s, b, p)],
    ["GET /api/ai/usage", apiAiUsage],
    ["GET /api/ai/tasks", apiAiTasks],
    ["POST /api/ai/tasks", apiAiTaskCreate],
    ["POST /api/ai/tasks/:id/run", (r, re, u, s, b, p) => apiAiTaskRun(r, re, u, s, b, p)],
    ["GET /api/platform/ai", apiPlatformAi]
  ];
} };
