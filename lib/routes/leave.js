/* LUXORA Platform — leave domain routes (lib/leave.js; _registry/business-domains.json).
   Leave requests, balances and the calendar, under the store's leave section (the People and
   Delivery roles hold it): a read grant lists, a write grant asks and decides. */
"use strict";

module.exports = { domain: "leave", routes(kit) {
  const { T, actor, bad, json, logAction, requireAdmin } = kit;
  const L = () => require("../leave.js");
  const answer = (s, res, fn) => { if (!requireAdmin(s, res)) return; try { fn(); } catch (e) { bad(res, e.message, e.status || 400); } };
  const q = (url, k) => url.searchParams.get(k) || "";
  const who = s => { const a = actor(s); return Array.isArray(a) ? String(a[2] || a[1] || "") : String(a || ""); };
  const B = b => b || {};

  /* Leave requests, latest first; `status`, `employee_id` and `from` (still running on or after a day) narrow them; with the kinds of leave and the working days. */
  function apiLeave(req, res, url, s) { answer(s, res, () => json(res, 200, { requests: L().requests(T(s), { status: q(url, "status"), employee_id: q(url, "employee_id"), from: q(url, "from") }), types: L().types(T(s)), workingDays: L().workingDays(T(s)) })); }
  /* Asks for leave: `employee_id`, `type`, `from_date`, `to_date`, `half_day`, `reason`. Refused when it overlaps another request or asks for more than is left. */
  function apiLeaveRequest(req, res, url, s, body) { answer(s, res, () => { const r = L().request(T(s), B(body), who(s)); logAction(s, "leave.request", "leave_request", r.ref, { days: r.days }); json(res, 200, { request: r }); }); }
  /* Approves a request — not by the person it is for or whoever asked: each working day shows in attendance, paid or unpaid. */
  function apiLeaveApprove(req, res, url, s, body, id) { answer(s, res, () => { const r = L().approve(T(s), id, who(s), B(body).note); logAction(s, "leave.approve", "leave_request", r.ref, {}); json(res, 200, { request: r }); }); }
  /* Turns a request down with a `note` saying why. */
  function apiLeaveReject(req, res, url, s, body, id) { answer(s, res, () => { const r = L().reject(T(s), id, who(s), B(body).note); logAction(s, "leave.reject", "leave_request", r.ref, {}); json(res, 200, { request: r }); }); }
  /* Cancels a request not yet decided, or approved leave not yet started: its days come back. */
  function apiLeaveCancel(req, res, url, s, body, id) { answer(s, res, () => { const r = L().cancel(T(s), id); logAction(s, "leave.cancel", "leave_request", r.ref, {}); json(res, 200, { request: r }); }); }
  /* A person's leave for a `year`: each kind's entitlement, what is carried in, taken, waiting and left. */
  function apiLeaveBalance(req, res, url, s, body, id) { answer(s, res, () => json(res, 200, { balance: L().balance(T(s), id, q(url, "year")) })); }
  /* Sets a person's own allowance of a kind for a year: `year`, `type`, `days` (null removes it). */
  function apiLeaveAllowance(req, res, url, s, body, id) { answer(s, res, () => { const b = B(body); json(res, 200, { balance: L().setAllowance(T(s), id, b.year, b.type, b.days) }); }); }
  /* Who is away on each working day from `from` to `to`. */
  function apiLeaveCalendar(req, res, url, s) { answer(s, res, () => json(res, 200, { calendar: L().calendar(T(s), q(url, "from"), q(url, "to")) })); }

  return [
    ["GET /api/admin/leave", apiLeave],
    ["POST /api/admin/leave", apiLeaveRequest],
    ["POST /api/admin/leave/:id/approve", (r, re, u, s, b, p) => apiLeaveApprove(r, re, u, s, b, p)],
    ["POST /api/admin/leave/:id/reject", (r, re, u, s, b, p) => apiLeaveReject(r, re, u, s, b, p)],
    ["POST /api/admin/leave/:id/cancel", (r, re, u, s, b, p) => apiLeaveCancel(r, re, u, s, b, p)],
    ["GET /api/admin/leave/people/:id", (r, re, u, s, b, p) => apiLeaveBalance(r, re, u, s, b, p)],
    ["PUT /api/admin/leave/people/:id", (r, re, u, s, b, p) => apiLeaveAllowance(r, re, u, s, b, p)],
    ["GET /api/admin/leave/calendar", apiLeaveCalendar]
  ];
} };
