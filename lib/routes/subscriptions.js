/* LUXORA Platform — subscriptions domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the subscriptions domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "subscriptions", routes(kit) {
  const { CFG, T, all, bad, get, governance, isAdmin, json, logAction, ownerFor, recurring, requireAdmin } = kit;

  /* ---------------- Subscribe & Save ---------------- */
  function apiSubCreate(req, res, url, s, body) {
    if (!CFG(s).features.subscribeSave) return bad(res, "Subscribe & Save is disabled", 403);
    const pid = String(body.product_id || "");
    if (!get("SELECT id FROM products WHERE tenant_id=? AND id=?", T(s), pid)) return bad(res, "Unknown product", 404);
    const disc = Number(CFG(s).retention && CFG(s).retention.subDiscount) || 10;
    const sched = recurring.createSchedule(T(s), { owner: ownerFor(s), product_id: pid, sku_id: body.sku_id, qty: body.qty, frequency_days: body.frequency_days, discount_pct: disc, start_at: body.start_at });
    logAction(s, "subscription.create", "recurring_schedule", sched.id, { product: pid, freq: sched.frequency_days });
    json(res, 200, { schedule: sched, discount_pct: disc });
  }
  function apiSubList(req, res, url, s) {
    if (!CFG(s).features.subscribeSave) return bad(res, "Subscribe & Save is disabled", 403);
    json(res, 200, { schedules: recurring.listSchedules(T(s), ownerFor(s)) });
  }
  function apiSubControl(req, res, url, s, body, id) {
    if (!CFG(s).features.subscribeSave) return bad(res, "Subscribe & Save is disabled", 403);
    try {
      /* a customer controls only their own schedule; staff may act on any in their store */
      const sc = recurring.controlSchedule(T(s), Number(id), String(body.action || ""), (s.platform_admin || isAdmin(s)) ? null : ownerFor(s));
      logAction(s, "subscription." + body.action, "recurring_schedule", id);
      json(res, 200, { schedule: sc });
    } catch (e) { bad(res, e.message, 400); }
  }
  function apiAdminRecurring(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    const due = recurring.dueSchedules(T(s));
    json(res, 200, {
      schedules: all("SELECT s.*, p.title product_title FROM recurring_schedules s LEFT JOIN products p ON p.tenant_id=s.tenant_id AND p.id=s.product_id WHERE s.tenant_id=? ORDER BY s.id DESC LIMIT 200", T(s)),
      due: due.length, statuses: recurring.SCHED_STATUSES, frequencies: recurring.FREQUENCIES
    });
  }
  function apiAdminRecurringProcess(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    const due = recurring.dueSchedules(T(s));
    const processed = [];
    for (const sc of due) {
      try { processed.push({ id: sc.id, ok: true, ref: recurring.processCycle(T(s), sc.id, "RUN-" + new Date().toISOString().slice(0, 10)).cycles_completed }); }
      catch (e) { processed.push({ id: sc.id, ok: false, error: e.message }); }
    }
    logAction(s, "subscription.process", "recurring_schedule", processed.length, { processed: processed.length });
    json(res, 200, { processed, remaining: recurring.dueSchedules(T(s)).length });
  }
  /* ---------------- membership ---------------- */
  function apiMembershipGet(req, res, url, s) {
    json(res, 200, { membership: recurring.membershipOf(T(s), ownerFor(s)), tiers: recurring.tiers() });
  }
  function apiMembershipSubscribe(req, res, url, s, body) {
    if (!CFG(s).features.membership) return bad(res, "Membership program is disabled", 403);
    try {
      const m = recurring.subscribeMembership(T(s), ownerFor(s), String(body.tier || ""));
      logAction(s, "membership.subscribe", "membership", m.tier, { tier: body.tier });
      json(res, 200, { membership: m });
    } catch (e) { bad(res, e.message, 400); }
  }
  function apiMembershipCancel(req, res, url, s) {
    if (!CFG(s).features.membership) return bad(res, "Membership program is disabled", 403);
    json(res, 200, { membership: recurring.cancelMembership(T(s), ownerFor(s)) });
  }
  function apiAdminMemberships(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { memberships: recurring.listMemberships(T(s)), tiers: recurring.tiers() });
  }
  function apiRetentionGet(req, res, url, s) { if (!requireAdmin(s, res)) return; json(res, 200, { retention: governance.getRetention(T(s)), defaults: governance.defaultRetention(), soft: [...governance.SOFT] }); }
  function apiRetentionPut(req, res, url, s, body) { if (!requireAdmin(s, res)) return; governance.setRetention(T(s), body || {}); logAction(s, "governance.retention", "governance", null, { changed: Object.keys(body || {}).join(",") }, req); json(res, 200, { ok: true, retention: governance.getRetention(T(s)) }); }

  return [
    ["GET /api/admin/retention", apiRetentionGet],
    ["PUT /api/admin/retention", apiRetentionPut],
    ["POST /api/subscriptions", apiSubCreate],
    ["GET /api/subscriptions", apiSubList],
    ["PUT /api/subscriptions/:id", (r, re, u, s, b, p) => apiSubControl(r, re, u, s, b, p)],
    ["GET /api/admin/recurring", apiAdminRecurring],
    ["POST /api/admin/recurring/process", apiAdminRecurringProcess],
    ["GET /api/membership", apiMembershipGet],
    ["POST /api/membership/subscribe", apiMembershipSubscribe],
    ["POST /api/membership/cancel", apiMembershipCancel],
    ["GET /api/admin/memberships", apiAdminMemberships]
  ];
} };
