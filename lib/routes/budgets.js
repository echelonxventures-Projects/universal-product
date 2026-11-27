/* LUXORA Platform — budgets domain routes (lib/budgets.js; _registry/business-domains.json).
   A year's plan per account of the books and how the books compare, under the store's budgets
   section (the Finance role holds it). */
"use strict";

module.exports = { domain: "budgets", routes(kit) {
  const { T, actor, bad, json, logAction, requireAdmin } = kit;
  const BU = () => require("../budgets.js");
  const answer = (s, res, fn) => { if (!requireAdmin(s, res)) return; try { fn(); } catch (e) { bad(res, e.message, e.status || 400); } };
  const who = s => { const a = actor(s); return Array.isArray(a) ? String(a[2] || a[1] || "") : String(a || ""); };

  /* The store's budgets, latest year first, and the accounts a budget can plan. */
  function apiBudgets(req, res, url, s) { answer(s, res, () => json(res, 200, { budgets: BU().list(T(s)), accounts: BU().plannable(T(s)).map(a => ({ code: a.code, name: a.name, type: a.type })) })); }
  /* Drafts a budget: `name`, `year`, `currency`. */
  function apiBudgetCreate(req, res, url, s, body) { answer(s, res, () => { const b = BU().create(T(s), body || {}, who(s)); logAction(s, "budgets.create", "budget", b.ref, { year: b.year }); json(res, 200, { budget: b }); }); }
  /* One budget with its lines, account by account and month by month. */
  function apiBudget(req, res, url, s, body, id) { answer(s, res, () => json(res, 200, { budget: BU().view(T(s), id) })); }
  /* Sets a draft's `lines`: `{ account, month, amount }`, or `{ account, annual }` spread evenly; 0 clears a month. */
  function apiBudgetLines(req, res, url, s, body, id) { answer(s, res, () => json(res, 200, { budget: BU().setLines(T(s), id, (body || {}).lines) })); }
  /* Fills a draft from a `year` of the books' actual figures, raised by `uplift_pct`. */
  function apiBudgetFromActuals(req, res, url, s, body, id) { answer(s, res, () => json(res, 200, { budget: BU().fromActuals(T(s), id, body || {}) })); }
  /* Approves a draft: one approved budget per year and currency. */
  function apiBudgetApprove(req, res, url, s, body, id) { answer(s, res, () => { const b = BU().approve(T(s), id, who(s)); logAction(s, "budgets.approve", "budget", b.ref, { total: b.total }); json(res, 200, { budget: b }); }); }
  /* Reopens an approved budget as a draft. */
  function apiBudgetReopen(req, res, url, s, body, id) { answer(s, res, () => json(res, 200, { budget: BU().reopen(T(s), id) })); }
  /* Closes an approved budget. */
  function apiBudgetClose(req, res, url, s, body, id) { answer(s, res, () => json(res, 200, { budget: BU().close(T(s), id) })); }
  /* The budget against the books through a month (`through`, 1–12): each account month by month and to date, its variance, and whether it is off plan. */
  function apiBudgetReport(req, res, url, s, body, id) { answer(s, res, () => json(res, 200, BU().report(T(s), id, { through: url.searchParams.get("through") }))); }

  return [
    ["GET /api/admin/budgets", apiBudgets],
    ["POST /api/admin/budgets", apiBudgetCreate],
    ["GET /api/admin/budgets/:id", (r, re, u, s, b, p) => apiBudget(r, re, u, s, b, p)],
    ["PUT /api/admin/budgets/:id/lines", (r, re, u, s, b, p) => apiBudgetLines(r, re, u, s, b, p)],
    ["POST /api/admin/budgets/:id/from-actuals", (r, re, u, s, b, p) => apiBudgetFromActuals(r, re, u, s, b, p)],
    ["POST /api/admin/budgets/:id/approve", (r, re, u, s, b, p) => apiBudgetApprove(r, re, u, s, b, p)],
    ["POST /api/admin/budgets/:id/reopen", (r, re, u, s, b, p) => apiBudgetReopen(r, re, u, s, b, p)],
    ["POST /api/admin/budgets/:id/close", (r, re, u, s, b, p) => apiBudgetClose(r, re, u, s, b, p)],
    ["GET /api/admin/budgets/:id/report", (r, re, u, s, b, p) => apiBudgetReport(r, re, u, s, b, p)]
  ];
} };
