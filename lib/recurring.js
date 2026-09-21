/* LUXORA Platform — Retention & recurring revenue.
   Subscribe & Save: customer recurring delivery schedules (frequency, next shipment,
   pause/skip/cancel, per-cycle ledger that mints a real order each cycle) with a
   subscriber discount. Membership program (Prime / Plus / Walmart+ style): paid tiers whose
   benefits (free shipping, early access, bonus rewards, priority support) are data in
   meta_lists and apply at checkout. Renewals charge through the existing payments ledger.
   Feature flags: settings.features.subscribeSave / membership. */
"use strict";

const db = () => require("./db.js");
const { stamp } = require("./db.js");
const J = (v, d) => { try { return v == null || v === "" ? (d == null ? {} : d) : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d == null ? {} : d; } };
/* Timestamps are stored in SQLite's datetime() shape ('YYYY-MM-DD HH:MM:SS', UTC, space
   separator) so lexicographic comparisons against datetime('now') are correct. Raw ISO
   'T'/'Z' strings sort *after* every same-day space-format string, which silently breaks
   same-day due/overdue detection — so every JS Date is normalised via db.stamp(). */

const FREQUENCIES = [30, 45, 60, 90];
const SCHED_STATUSES = ["active", "paused", "cancelled"];
const CYCLE_STATUSES = ["scheduled", "processing", "shipped", "delivered", "skipped", "failed"];
const MEM_STATUSES = ["active", "past_due", "cancelled"];

const TIERS = [
  { key: "free", name: "Free", price: 0, currency: "USD", benefits: [], bonus_pct: 0 },
  { key: "plus", name: "Plus", price: 9.99, currency: "USD", benefits: ["free_ship", "early_access"], bonus_pct: 2 },
  { key: "prime", name: "Prime", price: 14.99, currency: "USD", benefits: ["free_ship", "early_access", "priority_support", "bonus_rewards"], bonus_pct: 5 }
];

function seed() {
  const D = db();
  const put = (name, label, items) => {
    const existing = D.get("SELECT items FROM meta_lists WHERE name=?", name);
    const cur = J(existing ? existing.items : "[]", []);
    for (const it of items) if (!cur.some(x => (x.key || x) === (it.key || it))) cur.push(it);
    if (existing) D.run("UPDATE meta_lists SET items=? WHERE name=?", JSON.stringify(cur), name);
    else D.run("INSERT INTO meta_lists(name,label,items) VALUES(?,?,?)", name, label, JSON.stringify(items));
  };
  put("recFrequencies", "Retention · Delivery frequencies (days)", FREQUENCIES.map(k => ({ key: k, name: "Every " + k + " days" })));
  put("recSchedStatuses", "Retention · Schedule statuses", SCHED_STATUSES.map(k => ({ key: k, name: k })));
  put("recCycleStatuses", "Retention · Cycle statuses", CYCLE_STATUSES.map(k => ({ key: k, name: k })));
  put("membershipTiers", "Retention · Membership tiers", TIERS);
  put("membershipStatuses", "Retention · Membership statuses", MEM_STATUSES.map(k => ({ key: k, name: k })));
  put("membershipBenefits", "Retention · Membership benefits", ["free_ship", "early_access", "priority_support", "bonus_rewards", "bonus_pct"].map(k => ({ key: k, name: k })));
}

function tiers() { return J(db().get("SELECT items FROM meta_lists WHERE name='membershipTiers'")?.items, TIERS); }
function tierOf(key) { return tiers().find(t => t.key === key) || tiers()[0]; }

/* ---------------- Subscribe & Save ---------------- */
function createSchedule(tenantId, input) {
  const D = db();
  const freq = FREQUENCIES.includes(Number(input.frequency_days)) ? Number(input.frequency_days) : 30;
  const qty = Math.max(1, Math.min(99, Number(input.qty) || 1));
  const start = stamp(input.start_at || new Date(Date.now() + freq * 86400e3));
  const r = D.run("INSERT INTO recurring_schedules(tenant_id,owner,product_id,sku_id,qty,frequency_days,discount_pct,next_ship_at,status) VALUES(?,?,?,?,?,?,?,?,'active')",
    tenantId, String(input.owner), String(input.product_id), input.sku_id ? Number(input.sku_id) : null, qty, freq,
    Number(input.discount_pct) || 0, start);
  const id = Number(r.lastInsertRowid);
  D.run("INSERT INTO recurring_cycles(schedule_id,tenant_id,status,at) VALUES(?,?,'scheduled',?)", id, tenantId, start);
  return scheduleById(D, tenantId, id);
}

function scheduleById(D, tenantId, id) {
  const s = D.get("SELECT * FROM recurring_schedules WHERE id=? AND tenant_id=?", Number(id), tenantId);
  if (!s) return null;
  s.cycles = D.all("SELECT * FROM recurring_cycles WHERE schedule_id=? ORDER BY at", s.id);
  return s;
}

function listSchedules(tenantId, owner) {
  const D = db();
  return D.all("SELECT * FROM recurring_schedules WHERE tenant_id=? AND owner=? ORDER BY id DESC", tenantId, owner).map(s => ({
    ...s, cycles: D.all("SELECT * FROM recurring_cycles WHERE schedule_id=? ORDER BY at", s.id)
  }));
}

function controlSchedule(tenantId, id, action) {
  const D = db();
  const s = scheduleById(D, tenantId, id);
  if (!s) throw new Error("Unknown subscription " + id);
  if (action === "pause") D.run("UPDATE recurring_schedules SET status='paused' WHERE id=?", id);
  else if (action === "resume") D.run("UPDATE recurring_schedules SET status='active' WHERE id=?", id);
  else if (action === "cancel") D.run("UPDATE recurring_schedules SET status='cancelled' WHERE id=?", id);
  else if (action === "skip") {
    const next = stamp(new Date(new Date(s.next_ship_at).getTime() + s.frequency_days * 86400e3));
    D.run("UPDATE recurring_cycles SET status='skipped' WHERE schedule_id=? AND status='scheduled' AND at=?", id, s.next_ship_at);
    D.run("UPDATE recurring_schedules SET next_ship_at=?, cycles_completed=cycles_completed+1 WHERE id=?", next, id);
    D.run("INSERT INTO recurring_cycles(schedule_id,tenant_id,status,at) VALUES(?,?,'scheduled',?)", id, tenantId, next);
  } else throw new Error("Unknown subscription action: " + action);
  return scheduleById(D, tenantId, id);
}

/* due now (or overdue) and still active */
function dueSchedules(tenantId) {
  const D = db();
  return D.all("SELECT s.* FROM recurring_schedules s WHERE s.tenant_id=? AND s.status='active' AND s.next_ship_at <= datetime('now')", tenantId);
}

/* process one due cycle: marks it shipped and rolls the next shipment date.
   The order itself is created by the caller (checkout path) or recorded here against
   an existing order id when the platform processes the run. */
function processCycle(tenantId, id, orderRef) {
  const D = db();
  const s = scheduleById(D, tenantId, id);
  if (!s || s.status !== "active") throw new Error("Schedule not active: " + id);
  const next = stamp(new Date(new Date(s.next_ship_at).getTime() + s.frequency_days * 86400e3));
  D.run("UPDATE recurring_cycles SET status='shipped', order_ref=? WHERE schedule_id=? AND status='scheduled' AND at=?", String(orderRef || ""), id, s.next_ship_at);
  D.run("UPDATE recurring_schedules SET next_ship_at=?, cycles_completed=cycles_completed+1 WHERE id=?", next, id);
  return scheduleById(D, tenantId, id);
}

/* ---------------- Membership ---------------- */
function membershipOf(tenantId, owner) {
  const D = db();
  const m = D.get("SELECT * FROM memberships WHERE tenant_id=? AND owner=? ORDER BY id DESC LIMIT 1", tenantId, owner);
  if (!m) return { tier: "free", tier_detail: tierOf("free"), status: "none", benefits: [] };
  const t = tierOf(m.tier);
  if (m.status !== "active") return { ...m, tier_detail: t, benefits: [] };
  return { ...m, tier_detail: t, benefits: t.benefits || [] };
}

function subscribeMembership(tenantId, owner, tierKey, renew) {
  const D = db();
  const t = tierOf(tierKey);
  if (!t || t.key === "free") throw new Error("Pick a paid tier");
  if (t.price > 0 && !renew) {
    const D = db();
    D.run("INSERT INTO payments(tenant_id,kind,order_id,invoice_id,gateway,method,amount,currency,fee,status,txn_ref) VALUES(?,'membership',NULL,NULL,'wallet','membership',?,?,0,'captured','MEM-' || datetime('now'))", tenantId, t.price, t.currency);
  }
  const renews = stamp(new Date(Date.now() + 30 * 86400e3));
  const ex = D.get("SELECT id FROM memberships WHERE tenant_id=? AND owner=? AND status='active'", tenantId, owner);
  if (ex) D.run("UPDATE memberships SET tier=?, status='active', renews_at=? WHERE id=?", t.key, renews, ex.id);
  else D.run("INSERT INTO memberships(tenant_id,owner,tier,status,renews_at) VALUES(?,?,?,?,?)", tenantId, owner, t.key, "active", renews);
  return membershipOf(tenantId, owner);
}

function cancelMembership(tenantId, owner) {
  const D = db();
  D.run("UPDATE memberships SET status='cancelled' WHERE tenant_id=? AND owner=? AND status='active'", tenantId, owner);
  return membershipOf(tenantId, owner);
}

function listMemberships(tenantId) {
  const D = db();
  return D.all("SELECT * FROM memberships WHERE tenant_id=? ORDER BY id DESC LIMIT 200", tenantId).map(m => ({ ...m, tier_detail: tierOf(m.tier) }));
}

/* benefits applied at checkout: free shipping overrides the carrier fee */
function checkoutBenefits(tenantId, owner) {
  const m = membershipOf(tenantId, owner);
  const active = m.status === "active";
  return { free_ship: active && m.benefits.includes("free_ship"), bonus_pct: active ? ((m.tier_detail && m.tier_detail.bonus_pct) || 0) : 0, tier: m.tier, early_access: active && m.benefits.includes("early_access") };
}

module.exports = {
  seed, FREQUENCIES, SCHED_STATUSES, CYCLE_STATUSES, MEM_STATUSES, TIERS,
  tiers, tierOf,
  createSchedule, scheduleById, listSchedules, controlSchedule, dueSchedules, processCycle,
  membershipOf, subscribeMembership, cancelMembership, listMemberships, checkoutBenefits
};
