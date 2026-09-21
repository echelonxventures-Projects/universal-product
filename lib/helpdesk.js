/* LUXORA Platform — Customer Service helpdesk.
   Tickets raised by customers (storefront or inbound email/webhook), an agent queue with
   assignment, priorities and statuses, SLA timers (first-response + resolution targets),
   internal notes vs public replies, and CSAT ratings collected on close. Priorities, statuses
   and reasons are meta_lists registries (hdPriorities, hdStatuses, hdReasons) — editable from
   Data Studio, no code. Feature-gated by settings.features.helpdesk. */
"use strict";

const db = () => require("./db.js");
const J = (v, d) => { try { return v == null || v === "" ? (d == null ? {} : d) : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d == null ? {} : d; } };

const STATUSES = ["new", "open", "pending", "resolved", "closed"];
const PRIORITIES = ["low", "normal", "high", "urgent"];
const REASONS = ["order", "delivery", "returns", "payment", "product", "account", "other"];
/* SLA targets in hours per priority: first response, resolution */
const SLA = { low: [24, 96], normal: [8, 48], high: [4, 24], urgent: [1, 8] };
const CSAT_SCALE = 5;

function seed() {
  const D = db();
  const put = (name, label, items) => {
    const existing = D.get("SELECT items FROM meta_lists WHERE name=?", name);
    const cur = J(existing ? existing.items : "[]", []);
    for (const it of items) if (!cur.some(x => (x.key || x) === (it.key || it))) cur.push(it);
    if (existing) D.run("UPDATE meta_lists SET items=? WHERE name=?", JSON.stringify(cur), name);
    else D.run("INSERT INTO meta_lists(name,label,items) VALUES(?,?,?)", name, label, JSON.stringify(items));
  };
  put("hdStatuses", "Helpdesk · Ticket statuses", STATUSES.map(k => ({ key: k, name: k })));
  put("hdPriorities", "Helpdesk · Priorities", PRIORITIES.map(k => ({ key: k, name: k, sla_response: SLA[k][0], sla_resolution: SLA[k][1] })));
  put("hdReasons", "Helpdesk · Contact reasons", REASONS.map(k => ({ key: k, name: k })));
}

/* Timestamps are stored in SQLite's datetime() shape ('YYYY-MM-DD HH:MM:SS', UTC, space
   separator) to match the rest of the platform — see the note in recurring.js. */
const stamp = require("./db.js").stamp;
const now = () => stamp();
const hoursFromNow = h => stamp(new Date(Date.now() + h * 3600e3));

/* ---------------- ticket lifecycle ---------------- */
function openTicket(tenantId, input) {
  const D = db();
  const priority = PRIORITIES.includes(input.priority) ? input.priority : "normal";
  const reason = REASONS.includes(input.reason) ? input.reason : "other";
  const [respH, resH] = SLA[priority];
  const r = D.run("INSERT INTO tickets(tenant_id,ref,subject,reason,priority,status,owner_name,owner_email,owner,order_ref,product_id,body,sla_response,sla_resolution) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
    tenantId, nextRef(D, tenantId), String(input.subject || "Support request").slice(0, 200), reason, priority, "new",
    String(input.name || "A customer").slice(0, 80), String(input.email || "").slice(0, 200), String(input.owner || ""),
    String(input.order_ref || "").slice(0, 60), String(input.product_id || "").slice(0, 80),
    String(input.body || "").slice(0, 4000), hoursFromNow(respH), hoursFromNow(resH));
  note(D, tenantId, Number(r.lastInsertRowid), "customer", String(input.name || "Customer"), input.body, "public");
  return ticketById(D, tenantId, Number(r.lastInsertRowid));
}

function nextRef(D, tenantId) {
  const row = D.get("SELECT COUNT(*) c FROM tickets WHERE tenant_id=?", tenantId);
  return "CASE-" + tenantId + "-" + String(10000 + (row ? row.c : 0) + 1);
}

function note(D, tenantId, ticketId, role, author, body, visibility) {
  const r = D.run("INSERT INTO ticket_notes(tenant_id,ticket_id,role,author,body,visibility) VALUES(?,?,?,?,?,?)",
    tenantId, ticketId, role, String(author || "Agent").slice(0, 80), String(body || "").slice(0, 4000), visibility === "internal" ? "internal" : "public");
  return D.get("SELECT * FROM ticket_notes WHERE id=?", Number(r.lastInsertRowid));
}

function transition(D, tenantId, ticketId, status, assignee) {
  if (!STATUSES.includes(status)) throw new Error("Unknown ticket status: " + status);
  const t = ticketById(D, tenantId, ticketId);
  if (!t) throw new Error("Unknown ticket " + ticketId);
  const patch = { status };
  if (status !== "new" && !t.first_response_at) patch.first_response_at = now();
  if ((status === "resolved" || status === "closed") && !t.resolved_at) patch.resolved_at = now();
  if (assignee !== undefined) patch.assignee = assignee || null;
  const sets = Object.keys(patch).map(k => k + "=?").join(", ");
  D.run("UPDATE tickets SET " + sets + " WHERE id=? AND tenant_id=?", ...Object.values(patch), ticketId, tenantId);
  return ticketById(D, tenantId, ticketId);
}

function reply(tenantId, ticketId, author, body, internal, role) {
  const D = db();
  const t = ticketById(D, tenantId, ticketId);
  if (!t) throw new Error("Unknown ticket " + ticketId);
  const vis = internal ? "internal" : "public";
  const n = note(D, tenantId, ticketId, role || "agent", author, body, vis);
  /* a public agent reply counts as first response; keep the case moving */
  if (!internal && !t.first_response_at) transition(D, tenantId, ticketId, t.status === "new" ? "open" : t.status);
  else if (!internal && t.status === "pending") transition(D, tenantId, ticketId, "open");
  return n;
}

function rateCsat(tenantId, ticketId, score, comment) {
  const D = db();
  const s = Math.max(1, Math.min(CSAT_SCALE, Number(score) || 0));
  if (!s) throw new Error("CSAT score required");
  const t = ticketById(D, tenantId, ticketId);
  if (!t) throw new Error("Unknown ticket " + ticketId);
  D.run("UPDATE tickets SET csat=?, csat_comment=? WHERE id=? AND tenant_id=?", s, String(comment || "").slice(0, 500), ticketId, tenantId);
  return ticketById(D, tenantId, ticketId);
}

/* ---------------- reads ---------------- */
function ticketById(D, tenantId, id) {
  const t = D.get("SELECT * FROM tickets WHERE id=? AND tenant_id=?", Number(id), tenantId);
  if (!t) return null;
  t.notes = D.all("SELECT id,role,author,body,visibility,created_at FROM ticket_notes WHERE ticket_id=? ORDER BY id", t.id);
  return t;
}

function listTickets(tenantId, f) {
  const D = db(); f = f || {};
  let sql = "SELECT id,ref,subject,reason,priority,status,assignee,owner_name,owner_email,order_ref,csat,first_response_at,resolved_at,sla_response,sla_resolution,created_at FROM tickets WHERE tenant_id=?";
  const a = [tenantId];
  if (f.status) { sql += " AND status=?"; a.push(f.status); }
  if (f.assignee) { sql += " AND assignee=?"; a.push(f.assignee); }
  if (f.owner) { sql += " AND owner=?"; a.push(f.owner); }
  if (f.reason) { sql += " AND reason=?"; a.push(f.reason); }
  sql += " ORDER BY CASE priority WHEN 'urgent' THEN 0 WHEN 'high' THEN 1 WHEN 'normal' THEN 2 ELSE 3 END, created_at DESC LIMIT 200";
  return D.all(sql, ...a);
}

/* SLA health: overdue first-response or overdue resolution vs the per-priority targets */
function slaHealth(tenantId) {
  const D = db();
  const open = D.all("SELECT id,ref,priority,status,sla_response,sla_resolution,first_response_at,resolved_at,created_at FROM tickets WHERE tenant_id=? AND status NOT IN ('resolved','closed')", tenantId);
  const breach = t => {
    const overdue = (due, done) => done ? null : (new Date(due) < new Date() ? (done ? "response" : (new Date(due) < new Date() ? "response" : null)) : null);
    const r = overdue(t.sla_response, t.first_response_at);
    const m = overdue(t.sla_resolution, t.resolved_at);
    return r || m || null;
  };
  return open.map(t => ({ id: t.id, ref: t.ref, priority: t.priority, status: t.status, breach: breach(t) }));
}

/* agent performance: ticket counts + avg CSAT + avg first-response hours */
function agentStats(tenantId) {
  const D = db();
  const rows = D.all("SELECT assignee, COUNT(*) n, AVG(CASE WHEN csat>0 THEN csat END) csat, SUM(CASE WHEN first_response_at IS NOT NULL THEN 1 ELSE 0 END) responded FROM tickets WHERE tenant_id=? GROUP BY assignee", tenantId);
  return rows.map(r => ({ assignee: r.assignee || "unassigned", tickets: r.n, csat: r.csat ? +(+r.csat).toFixed(2) : null, responded: r.responded }));
}

module.exports = {
  seed, STATUSES, PRIORITIES, REASONS, SLA, CSAT_SCALE,
  openTicket, transition, reply, rateCsat, note,
  ticketById, listTickets, slaHealth, agentStats
};
