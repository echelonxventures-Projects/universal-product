/* LUXORA Platform — ai domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the ai domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "ai", routes(kit) {
  const { CFG, T, actor, ai, all, authz, bad, billing, emitEvent, get, isAdmin, json, logAction, offers, ownerFor, queueNow, registry, requireAdmin, requirePlatform, requireSection, run, sec, settings } = kit;

  /* ---- the knowledge base, the assistant and the MCP server (lib/rag.js, lib/assistant.js, lib/mcp.js) ----
     who is acting: a platform administrator, a store staff member by their role key (Store console →
     Team), or a shopper; experts and tool grants are decided on that */
  const rag = () => require("../rag.js"), asst = () => require("../assistant.js"), mcp = () => require("../mcp.js");
  const roleKeys = s => { try { return authz.roles("store", T(s)).map(r => r.key); } catch (e) { return []; } };
  function who(s) {
    if (s.platform_admin) return { platform: true, name: "platform administrator" };
    if (s.user_id && isAdmin(s)) { const u = get("SELECT name, email, staff_role FROM users WHERE id=? AND tenant_id=?", s.user_id, T(s)) || {}; return { roleKey: u.staff_role || "owner", name: u.name || u.email }; }
    return { owner: ownerFor(s), name: s.user_id ? "customer " + s.user_id : "visitor" };
  }
  const done = (res, fn, status) => { try { const out = fn(); if (out && typeof out.then === "function") return out.then(v => json(res, status || 200, v)).catch(e => bad(res, e.message, e.status || 400)); json(res, status || 200, out); } catch (e) { bad(res, e.message, e.status || 400); } };
  const staffWrite = (s, res) => requireAdmin(s, res) && requireSection(s, res, "ai", "write");
  const staffRead = (s, res) => requireAdmin(s, res) && requireSection(s, res, "ai", "read");
  /* the store's knowledge collections and their modes */
  function apiKbCollections(req, res, url, s) { if (staffRead(s, res)) done(res, () => ({ collections: rag().collections(T(s)), modes: rag().MODES, roles: roleKeys(s) })); }
  /* creates or changes a collection: its label, mode, expert roles and thresholds */
  function apiKbCollectionPut(req, res, url, s, body, key) { if (staffWrite(s, res)) done(res, () => { const c = rag().saveCollection(T(s), key, body, roleKeys(s)); logAction(s, "kb.collection", "kb_collection", c.key, { mode: c.mode, expertRoles: c.expertRoles }, req); return { collection: c }; }); }
  /* a collection's entries, optionally of one status */
  function apiKbEntries(req, res, url, s, body, key) { if (staffRead(s, res)) done(res, () => ({ entries: rag().entries(T(s), key, url.searchParams.get("status") || null) })); }
  /* adds an entry: an expert's is approved, anyone else's waits for review */
  function apiKbEntryAdd(req, res, url, s, body, key) { if (staffWrite(s, res)) done(res, () => { const e = rag().addEntry(T(s), key, body, who(s)); logAction(s, "kb.entry.add", "kb_entry", e.id, { status: e.status }, req); return { entry: e }; }); }
  /* revises an entry: an expert's revision lands as a new version, anyone else's becomes a proposal */
  function apiKbEntryPut(req, res, url, s, body, id) { if (staffWrite(s, res)) done(res, () => { const r = rag().revise(T(s), id, { title: body.title, body: body.body, tags: body.tags }, who(s), body.reason); logAction(s, "kb.entry.revise", "kb_entry", Number(id), { proposed: r.proposed }, req); return r; }); }
  /* an expert approves, rejects or retires an entry */
  function apiKbEntryReview(req, res, url, s, body, id) { if (staffWrite(s, res)) done(res, () => { const e = rag().review(T(s), id, body && body.decision, who(s), body && body.reason); logAction(s, "kb.entry.review", "kb_entry", Number(id), { decision: body.decision }, req); return { entry: e }; }); }
  /* an expert restores an earlier version of an entry */
  function apiKbEntryRollback(req, res, url, s, body, id) { if (staffWrite(s, res)) done(res, () => { const e = rag().rollback(T(s), id, body && body.version, who(s)); logAction(s, "kb.entry.rollback", "kb_entry", Number(id), { version: body.version }, req); return { entry: e }; }); }
  /* every version of an entry, with who changed it and why */
  function apiKbEntryHistory(req, res, url, s, body, id) { if (staffRead(s, res)) done(res, () => ({ versions: rag().history(T(s), id) })); }
  /* the revisions waiting in a collection (from staff, the AI or feedback) */
  function apiKbProposals(req, res, url, s, body, key) { if (staffRead(s, res)) done(res, () => ({ proposals: rag().proposals(T(s), key) })); }
  /* an expert approves or rejects a proposed revision */
  function apiKbProposalDecide(req, res, url, s, body, id) { if (staffWrite(s, res)) done(res, () => { const r = rag().decideProposal(T(s), id, body && body.decision, who(s)); logAction(s, "kb.proposal", "kb_proposal", Number(id), { decision: body.decision }, req); return r; }); }
  /* a staff member confirms a proposal (in auto-evolving mode, enough confirmations let it go live) */
  function apiKbProposalConfirm(req, res, url, s, body, id) { if (staffWrite(s, res)) done(res, () => rag().confirmProposal(T(s), id)); }
  /* the AI drafts an entry for an expert's review, where the collection's mode allows it */
  function apiKbDraft(req, res, url, s, body, key) { if (staffWrite(s, res)) done(res, () => asst().draft(T(s), key, body, who(s)).then(e => { logAction(s, "kb.entry.draft", "kb_entry", e.id, {}, req); return { entry: e }; })); }
  /* searches a collection's approved entries by question and tags — anyone the store serves */
  function apiKbSearch(req, res, url, s, body, key) { done(res, () => ({ entries: rag().search(T(s), key, { q: url.searchParams.get("q") || "", tags: (url.searchParams.get("tags") || "").split(",").filter(Boolean), limit: Number(url.searchParams.get("limit")) || undefined }) })); }
  /* the store's assistant profiles (apps) */
  function apiAssistantProfiles(req, res, url, s) { if (staffRead(s, res)) done(res, () => ({ profiles: asst().profiles(T(s)), tools: mcp().TOOLS.map(t => ({ name: t.name, title: t.title, audience: t.audience })) })); }
  /* changes a profile: persona, collections, tools, hand-off, disclaimer, model and effort */
  function apiAssistantProfilePut(req, res, url, s, body, key) { if (staffWrite(s, res)) done(res, () => { const p = asst().saveProfile(T(s), key, body); logAction(s, "assistant.profile", "assistant_profile", p.key, {}, req); return { profile: p }; }); }
  /* asks one of the store's assistants (the store switches the AI assistant on in Capabilities) */
  function apiAssistantAsk(req, res, url, s, body, key) {
    if (!require("../capabilities.js").on(T(s), "ai_assistant")) return bad(res, "This store has no AI assistant (Store console → Capabilities → AI assistant)", 404);
    done(res, () => asst().ask(T(s), key, body, who(s)));
  }
  /* a person rates or corrects an answer */
  function apiAssistantRate(req, res, url, s, body, id) { done(res, () => asst().rate(T(s), id, body, who(s))); }
  /* the store's MCP access keys: each acts as one store role */
  function apiMcpKeys(req, res, url, s) { if (staffRead(s, res)) done(res, () => ({ keys: mcp().keys(T(s)), roles: roleKeys(s) })); }
  /* issues a key for a role (shown once) */
  function apiMcpKeyIssue(req, res, url, s, body) {
    if (!staffWrite(s, res)) return;
    const role = String((body && body.role) || ""); if (!roleKeys(s).includes(role)) return bad(res, "role must be one of the store's roles: " + roleKeys(s).join(", "));
    const k = mcp().issueKey(T(s), body.name, role, who(s).name); logAction(s, "mcp.key.issue", "mcp_key", null, { role, name: body.name }, req); json(res, 200, k);
  }
  /* revokes a key */
  function apiMcpKeyRevoke(req, res, url, s, body, id) { if (staffWrite(s, res)) { const ok = mcp().revokeKey(T(s), id); logAction(s, "mcp.key.revoke", "mcp_key", Number(id), {}, req); json(res, ok ? 200 : 404, ok ? { ok } : { error: "Not found" }); } }
  /* the MCP server: JSON-RPC 2.0. A Bearer MCP key acts as its role in its own store; otherwise the
     caller is whoever the session is (a staff role, or a shopper) */
  function apiMcp(req, res, url, s, body) {
    const bearer = String(req.headers.authorization || "").replace(/^Bearer\s+/i, "");
    let ctx;
    if (bearer) { const k = mcp().byKey(bearer); if (!k) return json(res, 401, { jsonrpc: "2.0", id: null, error: { code: -32001, message: "Invalid or revoked MCP key" } }); ctx = { tenantId: k.tenant_id, roleKey: k.role_key }; }
    else { const w = who(s); ctx = { tenantId: T(s), roleKey: w.roleKey, platform: !!w.platform }; }
    const out = mcp().handle(ctx, body);
    if (out === null) { res.writeHead(202); return res.end(); }
    json(res, 200, out);
  }


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
    /* a masked (or omitted) value on save keeps the stored one — re-saving the screen used to erase every key */
    const prior = {};
    for (const r of all("SELECT provider_id, config FROM tenant_gateways WHERE tenant_id=? AND provider_id LIKE 'ai:%'", t)) { try { prior[r.provider_id] = JSON.parse(r.config || "{}"); } catch (e) { prior[r.provider_id] = {}; } }
    run("DELETE FROM tenant_gateways WHERE tenant_id=? AND provider_id LIKE 'ai:%'", t);
    /* only AI providers — this route used to plant any provider id (payment, shipping) */
    const aiIds = new Set((require("../ai.js").AI_PROVIDERS || []).map(p => "ai:" + p.id));
    const ids = Object.keys(body || {}).map(k => k.startsWith("ai:") ? k : "ai:" + k);
    const badId = ids.find(k => !aiIds.has(k));
    if (badId) return bad(res, "Unknown AI provider: " + badId, 400);
    body = Object.fromEntries(Object.entries(body || {}).map(([k, v]) => [k.startsWith("ai:") ? k : "ai:" + k, v]));
    ids.forEach((id, i) => {
      const cfg = Object.assign({}, prior[id] || {});
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
    ["GET /api/kb/collections", apiKbCollections],
    ["PUT /api/kb/collections/:key", (r, re, u, s, b, p) => apiKbCollectionPut(r, re, u, s, b, p)],
    ["GET /api/kb/:key/entries", (r, re, u, s, b, p) => apiKbEntries(r, re, u, s, b, p)],
    ["POST /api/kb/:key/entries", (r, re, u, s, b, p) => apiKbEntryAdd(r, re, u, s, b, p)],
    ["GET /api/kb/:key/proposals", (r, re, u, s, b, p) => apiKbProposals(r, re, u, s, b, p)],
    ["POST /api/kb/:key/draft", (r, re, u, s, b, p) => apiKbDraft(r, re, u, s, b, p)],
    ["GET /api/kb/:key/search", (r, re, u, s, b, p) => apiKbSearch(r, re, u, s, b, p)],
    ["PUT /api/kb/entries/:id", (r, re, u, s, b, p) => apiKbEntryPut(r, re, u, s, b, p)],
    ["POST /api/kb/entries/:id/review", (r, re, u, s, b, p) => apiKbEntryReview(r, re, u, s, b, p)],
    ["POST /api/kb/entries/:id/rollback", (r, re, u, s, b, p) => apiKbEntryRollback(r, re, u, s, b, p)],
    ["GET /api/kb/entries/:id/history", (r, re, u, s, b, p) => apiKbEntryHistory(r, re, u, s, b, p)],
    ["POST /api/kb/proposals/:id/decide", (r, re, u, s, b, p) => apiKbProposalDecide(r, re, u, s, b, p)],
    ["POST /api/kb/proposals/:id/confirm", (r, re, u, s, b, p) => apiKbProposalConfirm(r, re, u, s, b, p)],
    ["GET /api/assistant/profiles", apiAssistantProfiles],
    ["PUT /api/assistant/profiles/:key", (r, re, u, s, b, p) => apiAssistantProfilePut(r, re, u, s, b, p)],
    ["POST /api/assistant/:key/ask", (r, re, u, s, b, p) => apiAssistantAsk(r, re, u, s, b, p)],
    ["POST /api/assistant/turns/:id/rate", (r, re, u, s, b, p) => apiAssistantRate(r, re, u, s, b, p)],
    ["GET /api/admin/mcp-keys", apiMcpKeys],
    ["POST /api/admin/mcp-keys", apiMcpKeyIssue],
    ["DELETE /api/admin/mcp-keys/:id", (r, re, u, s, b, p) => apiMcpKeyRevoke(r, re, u, s, b, p)],
    ["POST /api/mcp", apiMcp],
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
