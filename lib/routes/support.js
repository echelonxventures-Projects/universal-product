/* LUXORA Platform — support domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the support domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "support", routes(kit) {
  const { CFG, T, actor, bad, byOf, cases, engineFail, get, helpdesk, json, logAction, logistics, ownerFor, requireAdmin, requireStaff, shopperCall, signedIn } = kit;

  function apiSlaBreaches(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { breaches: logistics.slaBreaches(T(s), Number(url.searchParams.get("days") || 3)) });
  }
  /* ---------------- support helpdesk ---------------- */
  function apiSupportCreate(req, res, url, s, body) {
    if (!CFG(s).features.customerService) return bad(res, "Customer service is disabled", 403);
    const name = s.user_id ? (get("SELECT name FROM users WHERE id=?", s.user_id) || {}).name : String(body.name || "");
    const email = s.user_id ? (get("SELECT email FROM users WHERE id=?", s.user_id) || {}).email : String(body.email || "");
    if (!String(name || "").trim() || !String(email || "").trim()) return bad(res, "Name and email are required to open a case", 422);
    const t = helpdesk.openTicket(T(s), { name, email, owner: ownerFor(s), subject: body.subject, reason: body.reason, priority: body.priority, order_ref: body.order_ref, product_id: body.product_id, body: body.body });
    logAction(s, "support.ticket.create", "ticket", t.ref, { subject: t.subject });
    json(res, 200, { ticket: t });
  }
  function apiSupportList(req, res, url, s) {
    if (!CFG(s).features.customerService) return bad(res, "Customer service is disabled", 403);
    json(res, 200, { tickets: helpdesk.listTickets(T(s), { owner: ownerFor(s) }) });
  }
  function apiSupportGet(req, res, url, s, body, id) {
    if (!CFG(s).features.customerService) return bad(res, "Customer service is disabled", 403);
    const t = helpdesk.ticketById(require("../db.js"), T(s), Number(id));
    if (!t || t.owner !== ownerFor(s)) return bad(res, "Case not found", 404);
    /* customers never see internal notes */
    json(res, 200, { ticket: { ...t, notes: t.notes.filter(n => n.visibility !== "internal") } });
  }
  function apiSupportReply(req, res, url, s, body, id) {
    if (!CFG(s).features.customerService) return bad(res, "Customer service is disabled", 403);
    try {
      const t = helpdesk.ticketById(require("../db.js"), T(s), Number(id));
      if (!t || t.owner !== ownerFor(s)) return bad(res, "Case not found", 404);
      if (t.status === "closed") return bad(res, "This case is closed", 409);
      const n = helpdesk.reply(T(s), Number(id), t.owner_name, body.body, false, "customer");
      helpdesk.transition(require("../db.js"), T(s), Number(id), "pending");
      json(res, 200, { note: n });
    } catch (e) { bad(res, e.message, 400); }
  }
  function apiSupportCsat(req, res, url, s, body, id) {
    if (!CFG(s).features.customerService) return bad(res, "Customer service is disabled", 403);
    try {
      const t = helpdesk.ticketById(require("../db.js"), T(s), Number(id));
      if (!t || t.owner !== ownerFor(s)) return bad(res, "Case not found", 404);
      json(res, 200, { ticket: helpdesk.rateCsat(T(s), Number(id), body.score, body.comment) });
    } catch (e) { bad(res, e.message, 400); }
  }
  function apiAdminHdList(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { tickets: helpdesk.listTickets(T(s), { status: url.searchParams.get("status") || "", assignee: url.searchParams.get("assignee") || "" }), statuses: helpdesk.STATUSES, priorities: helpdesk.PRIORITIES });
  }
  function apiAdminHdGet(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    const t = helpdesk.ticketById(require("../db.js"), T(s), Number(id));
    if (!t) return bad(res, "Case not found", 404);
    json(res, 200, { ticket: t });
  }
  function apiAdminHdUpdate(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try {
      const D = require("../db.js");
      const t = helpdesk.transition(D, T(s), Number(id), String(body.status || "open"), body.assignee === undefined ? undefined : String(body.assignee || ""));
      if (body.priority) D.run("UPDATE tickets SET priority=? WHERE id=? AND tenant_id=?", String(body.priority), Number(id), T(s));
      logAction(s, "support.ticket.update", "ticket", t.ref, { status: t.status, assignee: t.assignee });
      json(res, 200, { ticket: helpdesk.ticketById(D, T(s), Number(id)) });
    } catch (e) { bad(res, e.message, 400); }
  }
  function apiAdminHdReply(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    const a = actor(s);
    try {
      const n = helpdesk.reply(T(s), Number(id), a[2] || "Support", body.body, !!body.internal, s.platform_admin ? "platform" : "agent");
      logAction(s, "support.ticket.reply", "ticket", Number(id), { internal: !!body.internal });
      json(res, 200, { note: n });
    } catch (e) { bad(res, e.message, 400); }
  }
  function apiAdminHdSla(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { health: helpdesk.slaHealth(T(s)), agents: helpdesk.agentStats(T(s)) });
  }
  /* every kind of case, with the section its own screen lives in */
  function apiCaseKinds(req, res, url, s) { shopperCall(res, () => ({ kinds: require("../parity-registries.js").list("caseKinds").map(k => ({ key: k.key, name: k.name, atom: k.atom, section: k.section, screen: k.screen })) })); }
  function apiCasesMine(req, res, url, s) { if (signedIn(s, res, "open a case")) shopperCall(res, () => ({ cases: cases().list(T(s), { owner: ownerFor(s) }), ...cases().vocabulary(T(s)) })); }
  function apiCaseOpen(req, res, url, s, body) { if (signedIn(s, res, "open a case")) shopperCall(res, () => ({ case: cases().open(T(s), ownerFor(s), body, "shopper") })); }
  function apiCaseWithdraw(req, res, url, s, body, id) { if (signedIn(s, res, "withdraw a case")) shopperCall(res, () => ({ case: cases().withdraw(T(s), ownerFor(s), id) })); }
  function apiAdminCases(req, res, url, s) { if (requireStaff(s, res)) shopperCall(res, () => ({ cases: cases().list(T(s), { kind: url.searchParams.get("kind") || null }), ...cases().vocabulary(T(s)) })); }
  function apiAdminCaseMove(req, res, url, s, body, id) {
    if (!requireStaff(s, res)) return;
    try { const c = cases().move(T(s), id, body.action, body, byOf(s) || actor(s)[0]); logAction(s, "case." + body.action, "case", id, { kind: c.kind }, req); json(res, 200, { case: c }); } catch (e) { engineFail(res, e); }
  }
  /* ========== Enhanced Helpdesk APIs ========== */
  /* chat/SMS intake are customer channels (public, owned by the caller's session so the
     customer can follow the case under /api/support/tickets); replying on a case and agent
     presence are staff actions, scoped to this store. */
  function apiHelpdeskChannels(req, res, url, s) {
    json(res, 200, { channels: helpdesk.CHANNELS || ['email','web','chat','sms','phone','social'] });
  }
  function apiHelpdeskChat(req, res, url, s, body) {
    if (!CFG(s).features.customerService) return bad(res, "Customer service is disabled", 403);
    const r = helpdesk.openChat(T(s), { ...(body || {}), owner: ownerFor(s) });
    json(res, 200, { session_id: r.session_id, ticket_id: r.ticket.id, ref: r.ticket.ref });
  }
  function apiHelpdeskSMS(req, res, url, s, body) {
    if (!CFG(s).features.customerService) return bad(res, "Customer service is disabled", 403);
    const r = helpdesk.openSMS(T(s), { ...(body || {}), owner: ownerFor(s) });
    json(res, 200, { ticket_id: r.ticket.id, ref: r.ticket.ref });
  }
  function apiHelpdeskMessage(req, res, url, s, body, ticketId) {
    if (!requireStaff(s, res)) return;
    const [, , name] = actor(s);
    let n;
    try { n = helpdesk.chatMessage(T(s), Number(ticketId), String(name || 'Agent'), String((body || {}).body || ''), !!(body || {}).internal); }
    catch (e) { return bad(res, 'Case not found', 404); }
    json(res, 200, { ok: true, note: n });
  }
  function apiHelpdeskAgentStatus(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    json(res, 200, { agents: helpdesk.getAgentsStatus(T(s)) });
  }
  function apiHelpdeskAgentStatusUpdate(req, res, url, s, body) {
    if (!requireStaff(s, res)) return;
    const agent = String((body || {}).agent_id || actor(s)[2] || '');
    if (!agent) return bad(res, 'agent_id required', 400);
    try { json(res, 200, { ok: true, agent: helpdesk.setAgentStatus(T(s), agent, String((body || {}).status || '')) }); }
    catch (e) { bad(res, e.message, 400); }
  }

  return [
    ["GET /api/cases", apiCasesMine],
    ["GET /api/case-kinds", apiCaseKinds],
    ["POST /api/cases", apiCaseOpen],
    ["POST /api/cases/:id/withdraw", (r, re, u, s, b, p) => apiCaseWithdraw(r, re, u, s, b, p)],
    ["GET /api/admin/cases", apiAdminCases],
    ["POST /api/admin/cases/:id", (r, re, u, s, b, p) => apiAdminCaseMove(r, re, u, s, b, p)],
    ["GET /api/admin/sla", apiSlaBreaches],
    ["POST /api/support/tickets", apiSupportCreate],
    ["GET /api/support/tickets", apiSupportList],
    ["GET /api/support/tickets/:id", (r, re, u, s, b, p) => apiSupportGet(r, re, u, s, b, p)],
    ["POST /api/support/tickets/:id/reply", (r, re, u, s, b, p) => apiSupportReply(r, re, u, s, b, p)],
    ["POST /api/support/tickets/:id/csat", (r, re, u, s, b, p) => apiSupportCsat(r, re, u, s, b, p)],
    ["GET /api/admin/helpdesk/tickets", apiAdminHdList],
    ["GET /api/admin/helpdesk/tickets/:id", (r, re, u, s, b, p) => apiAdminHdGet(r, re, u, s, b, p)],
    ["PUT /api/admin/helpdesk/tickets/:id", (r, re, u, s, b, p) => apiAdminHdUpdate(r, re, u, s, b, p)],
    ["POST /api/admin/helpdesk/tickets/:id/reply", (r, re, u, s, b, p) => apiAdminHdReply(r, re, u, s, b, p)],
    ["GET /api/admin/helpdesk/sla", apiAdminHdSla],
    ["GET /api/helpdesk/channels", apiHelpdeskChannels],
    ["POST /api/helpdesk/chat", apiHelpdeskChat],
    ["POST /api/helpdesk/sms", apiHelpdeskSMS],
    ["POST /api/helpdesk/:ticketId/message", apiHelpdeskMessage],
    ["GET /api/helpdesk/agents/status", apiHelpdeskAgentStatus],
    ["POST /api/helpdesk/agents/status", apiHelpdeskAgentStatusUpdate]
  ];
} };
