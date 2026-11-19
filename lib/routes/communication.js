/* LUXORA Platform — communication domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the communication domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "communication", routes(kit) {
  const { J, T, all, bad, connect, conversations, customProviders, get, json, logAction, marketingSpec, ownerFor, registry, requireAdmin, requireStaff, rules, run, sec, shopperCall, signedIn } = kit;

  function apiMarketingProviders(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    const defs = registry.providerDefs("marketing").concat(customProviders(T(s), "marketing"));
    const list = defs.map(p => { const row = get("SELECT mode,config FROM tenant_gateways WHERE tenant_id=? AND provider_id=?", T(s), "marketing:" + p.id); let cfg = {}; try { cfg = J(row && row.config || "{}", {}); } catch (e) { } cfg = row ? sec.unsealConfig(T(s), "marketing:" + p.id, JSON.stringify(cfg)) : {}; const masked = {}; for (const [k, v] of Object.entries(cfg)) masked[k] = (p.fields || []).some(f => f.key === k && f.secret) ? (v ? "••••" + String(v).slice(-4) : "") : v; const sp = marketingSpec(T(s), p.id); return { id: p.id, name: p.name, emoji: p.emoji, desc: p.desc, fields: p.fields, mode: row ? row.mode : "sandbox", configured: row && Object.keys(cfg).length > 0, hasSpec: !!(sp && sp.spec), spec: sp && sp.spec, config: masked }; });
    json(res, 200, { providers: list });
  }
  function apiMarketingSend(req, res, url, s, body) {
    return (async () => {
      if (!requireAdmin(s, res)) return;
      const id = String(body.provider || ""); const sp = marketingSpec(T(s), id); if (!sp || !sp.spec) return bad(res, "Unknown or specless marketing provider: " + id, 404);
      { const d = rules.decideAt("marketing.send", id, rules.at("marketing.send", T(s))); if (!d.ok) return bad(res, "Marketing integration " + id + " is not available here — " + d.reasons.join("; "), 403); }
      const row = get("SELECT mode,config FROM tenant_gateways WHERE tenant_id=? AND provider_id=?", T(s), "marketing:" + id);
      let cfg = {}; try { cfg = J(row && row.config || "{}", {}); } catch (e) { } if (row) cfg = sec.unsealConfig(T(s), "marketing:" + id, JSON.stringify(cfg));
      if (!body.config && (!row || row.mode !== "live")) return json(res, 200, { ok: true, live: false, simulated: true, note: "provider not configured live — enable in Marketing & set live + credentials" });
      const r = await connect.marketing({ provider: id, spec: sp.spec, config: body.config || cfg, payload: body.payload || {}, currency: body.currency });
      logAction(s, "marketing.send", "marketing", id, { ok: !!r.ok, live: !!r.live, error: r.error }, req);
      json(res, 200, r);
    })();
  }
  function apiMarketingSave(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const list = Array.isArray(body.marketing) ? body.marketing : [];
    list.forEach((g, i) => { const cfg = {}; for (const [k, v] of Object.entries(g.config || {})) if (v && !String(v).startsWith("••••")) cfg[k] = sec.encryptSecret(String(v), T(s) + "|marketing:" + g.id + "|" + k); run(`INSERT INTO tenant_gateways(tenant_id,provider_id,enabled,is_primary,mode,config,position) VALUES(?,?,1,0,?,?,?)
       ON CONFLICT(tenant_id,provider_id) DO UPDATE SET enabled=1, mode=excluded.mode, config=excluded.config`, T(s), "marketing:" + g.id, g.mode === "live" ? "live" : "sandbox", JSON.stringify(cfg), i); });
    logAction(s, "marketing.save", "marketing", null, { count: list.length }, req); json(res, 200, { ok: true });
  }
  function apiNotifications(req, res, url, s) {
    const rows = all("SELECT * FROM notifications WHERE tenant_id=? AND owner=? ORDER BY id DESC LIMIT 50", T(s), ownerFor(s));
    const unread = all("SELECT COUNT(*) c FROM notifications WHERE tenant_id=? AND owner=? AND read=0", T(s), ownerFor(s))[0].c;
    json(res, 200, { notifications: rows, unread });
  }
  function apiNotificationsRead(req, res, url, s, body) {
    if (body.all) run("UPDATE notifications SET read=1 WHERE tenant_id=? AND owner=?", T(s), ownerFor(s));
    else if (body.id) run("UPDATE notifications SET read=1 WHERE id=? AND tenant_id=? AND owner=?", Number(body.id), T(s), ownerFor(s));
    json(res, 200, { ok: true });
  }
  /* conversations */
  function apiConversations(req, res, url, s) { if (signedIn(s, res, "send messages")) shopperCall(res, () => ({ conversations: conversations.mine(T(s), ownerFor(s)), ...conversations.vocabulary() })); }
  function apiConversationStart(req, res, url, s, body) { if (signedIn(s, res, "send messages")) shopperCall(res, () => conversations.start(T(s), { owner: ownerFor(s) }, body)); }
  function apiConversationGet(req, res, url, s, body, id) { if (signedIn(s, res, "read messages")) shopperCall(res, () => conversations.thread(T(s), { owner: ownerFor(s) }, id)); }
  function apiConversationPost(req, res, url, s, body, id) { if (signedIn(s, res, "send messages")) shopperCall(res, () => { conversations.post(T(s), { owner: ownerFor(s) }, id, body.body); return conversations.thread(T(s), { owner: ownerFor(s) }, id); }); }
  function apiAdminConversations(req, res, url, s) { if (requireStaff(s, res)) shopperCall(res, () => ({ conversations: conversations.forStaff(T(s), url.searchParams.get("all") === "1"), ...conversations.vocabulary() })); }
  function apiAdminConversationGet(req, res, url, s, body, id) { if (requireStaff(s, res)) shopperCall(res, () => conversations.thread(T(s), { staff: true }, id)); }
  function apiAdminConversationPost(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    shopperCall(res, () => {
      if (body.action) return { conversation: conversations.act(T(s), id, String(body.action)) };
      conversations.post(T(s), { staff: true }, id, body.body);
      return conversations.thread(T(s), { staff: true }, id);
    });
  }
  function apiAdminMessageHide(req, res, url, s, body, id) { if (requireAdmin(s, res)) shopperCall(res, () => conversations.hideMessage(T(s), id, body.hidden)); }

  return [
    ["GET /api/notifications", apiNotifications],
    ["POST /api/notifications/read", apiNotificationsRead],
    ["GET /api/conversations", apiConversations],
    ["POST /api/conversations", apiConversationStart],
    ["GET /api/conversations/:id", (r, re, u, s, b, p) => apiConversationGet(r, re, u, s, b, p)],
    ["POST /api/conversations/:id", (r, re, u, s, b, p) => apiConversationPost(r, re, u, s, b, p)],
    ["GET /api/admin/conversations", apiAdminConversations],
    ["POST /api/admin/conversations/messages/:id", (r, re, u, s, b, p) => apiAdminMessageHide(r, re, u, s, b, p)],
    ["GET /api/admin/conversations/:id", (r, re, u, s, b, p) => apiAdminConversationGet(r, re, u, s, b, p)],
    ["POST /api/admin/conversations/:id", (r, re, u, s, b, p) => apiAdminConversationPost(r, re, u, s, b, p)],
    ["GET /api/marketing/providers", apiMarketingProviders],
    ["POST /api/marketing/save", apiMarketingSave],
    ["POST /api/marketing/send", apiMarketingSend]
  ];
} };
