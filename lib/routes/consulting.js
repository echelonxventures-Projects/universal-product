/* LUXORA Platform — consulting domain routes (lib/consulting.js; _registry/business-domains.json).
   Projects billed to clients, timesheets, expense claims, invoices billed by time, proposals and the
   resource plan, under the store's consulting section (the Delivery and Finance roles hold it); and
   the two public routes a client's proposal link uses, which need no sign-in. */
"use strict";

module.exports = { domain: "consulting", routes(kit) {
  const { T, actor, bad, json, logAction, requireAdmin, publicLink } = kit;
  const CS = () => require("../consulting.js");
  const answer = async (s, res, fn) => { if (!requireAdmin(s, res)) return; try { await fn(); } catch (e) { bad(res, e.message, e.status || 400); } };
  const q = (url, k) => url.searchParams.get(k) || "";
  /* who is acting, by their email (a key by its name): approvals are refused to whoever submitted */
  const who = s => { const a = actor(s); return Array.isArray(a) ? String(a[2] || a[1] || "") : String(a || ""); };
  const B = b => b || {};

  /* The consulting overview: every project with how it is billed, what is ready to bill, invoiced and paid; what waits for approval; what clients owe; the people and their rates; and the billing models, expense categories and proposal line kinds. */
  function apiConsulting(req, res, url, s) { return answer(s, res, () => json(res, 200, { ...CS().overview(T(s)), me: CS().meOf(T(s), who(s)) })); }
  /* One project: its billing, rates, hours, cost, expenses, what is invoiced and paid, and what is ready to bill up to `through`. */
  function apiConsultingProject(req, res, url, s, body, id) { return answer(s, res, () => json(res, 200, { project: CS().project(T(s), id), unbilled: CS().unbilled(T(s), id, q(url, "through") || undefined) })); }
  /* Sets how a project is billed: `billing` (time_materials, fixed, non_billable), `company_id`, `currency`, `bill_rate`, `tax_pct`, `budget` (the fixed fee), and `rates` `[{ employee_id, rate }]` for its people (a null rate removes one). */
  function apiConsultingProjectSet(req, res, url, s, body, id) { return answer(s, res, () => { const p = CS().setProject(T(s), id, B(body)); logAction(s, "consulting.project", "project", p.code, { billing: p.billing }); json(res, 200, { project: p }); }); }
  /* Sets a person's `bill_rate`, `cost_rate` and weekly `capacity_hours`. */
  function apiConsultingPerson(req, res, url, s, body, id) { return answer(s, res, () => { const p = CS().setPerson(T(s), id, B(body)); logAction(s, "consulting.person", "employee", p.id, {}); json(res, 200, { person: p }); }); }

  /* Timesheets, newest week first; `status`, `employee_id` and `week` narrow them. */
  function apiTimesheets(req, res, url, s) { return answer(s, res, () => json(res, 200, { timesheets: CS().sheets(T(s), { status: q(url, "status"), employee_id: q(url, "employee_id"), week: q(url, "week") }) })); }
  /* Opens a person's timesheet for a week (`employee_id`, `week` — any day of it), or returns the one they have. */
  function apiTimesheetOpen(req, res, url, s, body) { return answer(s, res, () => json(res, 200, { timesheet: CS().openSheet(T(s), B(body)) })); }
  /* One timesheet: its days, its entries and what may be done next. */
  function apiTimesheet(req, res, url, s, body, id) { return answer(s, res, () => json(res, 200, { timesheet: CS().sheet(T(s), id) })); }
  /* Replaces a draft week's `entries` `[{ project_id, task_id?, date, hours, billable?, note? }]`. */
  function apiTimesheetSave(req, res, url, s, body, id) { return answer(s, res, () => json(res, 200, { timesheet: CS().saveEntries(T(s), id, B(body).entries) })); }
  /* Submits a draft week for approval. */
  function apiTimesheetSubmit(req, res, url, s, body, id) { return answer(s, res, () => { const t = CS().submitSheet(T(s), id, who(s)); logAction(s, "consulting.timesheet.submit", "timesheet", t.ref, { hours: t.hours }); json(res, 200, { timesheet: t }); }); }
  /* Approves a submitted week — not by whoever submitted it: its hours are priced at each person's rate and cost, and add to their tasks and projects. */
  function apiTimesheetApprove(req, res, url, s, body, id) { return answer(s, res, () => { const t = CS().approveSheet(T(s), id, who(s)); logAction(s, "consulting.timesheet.approve", "timesheet", t.ref, { hours: t.hours }); json(res, 200, { timesheet: t }); }); }
  /* Sends a submitted week back with a `reason`. */
  function apiTimesheetReject(req, res, url, s, body, id) { return answer(s, res, () => { const t = CS().rejectSheet(T(s), id, who(s), B(body).reason); logAction(s, "consulting.timesheet.reject", "timesheet", t.ref, { reason: B(body).reason }); json(res, 200, { timesheet: t }); }); }
  /* Reopens a week that was sent back, as a draft. */
  function apiTimesheetReopen(req, res, url, s, body, id) { return answer(s, res, () => json(res, 200, { timesheet: CS().reopenSheet(T(s), id) })); }

  /* Expense claims, newest first; `status`, `employee_id` and `project_id` narrow them. */
  function apiExpenses(req, res, url, s) { return answer(s, res, () => json(res, 200, { claims: CS().claims(T(s), { status: q(url, "status"), employee_id: q(url, "employee_id"), project_id: q(url, "project_id") }) })); }
  /* Drafts a claim, or changes a draft (`id`): `employee_id`, `project_id`, `date`, `category`, `description`, `amount`, `currency`, `billable` (billed on to the client), `receipt_ref`. */
  function apiExpenseSave(req, res, url, s, body) { return answer(s, res, () => json(res, 200, { claim: CS().saveClaim(T(s), B(body)) })); }
  /* Submits a draft claim for approval. */
  function apiExpenseSubmit(req, res, url, s, body, id) { return answer(s, res, () => { const c = CS().submitClaim(T(s), id, who(s)); logAction(s, "consulting.expense.submit", "expense_claim", c.ref, { amount: c.amount }); json(res, 200, { claim: c }); }); }
  /* Approves a submitted claim — not by whoever submitted it: the books owe it to the person. */
  function apiExpenseApprove(req, res, url, s, body, id) { return answer(s, res, () => { const c = CS().approveClaim(T(s), id, who(s)); logAction(s, "consulting.expense.approve", "expense_claim", c.ref, { amount: c.amount }); json(res, 200, { claim: c }); }); }
  /* Sends a submitted claim back with a `reason`. */
  function apiExpenseReject(req, res, url, s, body, id) { return answer(s, res, () => { const c = CS().rejectClaim(T(s), id, who(s), B(body).reason); logAction(s, "consulting.expense.reject", "expense_claim", c.ref, { reason: B(body).reason }); json(res, 200, { claim: c }); }); }
  /* Reopens a claim that was sent back, as a draft. */
  function apiExpenseReopen(req, res, url, s, body, id) { return answer(s, res, () => json(res, 200, { claim: CS().reopenClaim(T(s), id) })); }
  /* Records an approved claim as paid back to the person: the books clear it from the bank. */
  function apiExpenseReimburse(req, res, url, s, body, id) { return answer(s, res, () => { const c = CS().reimburse(T(s), id); logAction(s, "consulting.expense.reimburse", "expense_claim", c.ref, { amount: c.amount }); json(res, 200, { claim: c }); }); }

  /* Invoices to clients, newest first; `status` and `project_id` narrow them. */
  function apiClientInvoices(req, res, url, s) { return answer(s, res, () => json(res, 200, { invoices: CS().invoices(T(s), { status: q(url, "status"), project_id: q(url, "project_id") }) })); }
  /* Drafts an invoice for a project (`project_id`) from its approved, unbilled time and expenses up to `through`, or a fixed-fee instalment (`fixed_amount`, `fixed_description`); `time: false` or `expenses: false` leaves those out, `tax_pct` overrides the project's. Each entry is billed once. */
  function apiClientInvoiceDraft(req, res, url, s, body) { return answer(s, res, () => { const v = CS().draftInvoice(T(s), B(body), who(s)); logAction(s, "consulting.invoice.draft", "client_invoice", v.ref, { gross: v.gross }); json(res, 200, { invoice: v }); }); }
  /* One invoice with its lines, its project and its client. */
  function apiClientInvoice(req, res, url, s, body, id) { return answer(s, res, () => json(res, 200, { invoice: CS().invoice(T(s), id) })); }
  /* Issues a draft: the client owes it, due in the store's terms; with `send_to` it is emailed there. */
  function apiClientInvoiceIssue(req, res, url, s, body, id) { return answer(s, res, async () => { const v = await CS().issueInvoice(T(s), id, B(body)); logAction(s, "consulting.invoice.issue", "client_invoice", v.ref, { gross: v.gross, emailed: v.emailed }); json(res, 200, { invoice: v }); }); }
  /* Records an issued invoice as paid: the books move it from what the client owes to the bank. */
  function apiClientInvoicePay(req, res, url, s, body, id) { return answer(s, res, () => { const v = CS().payInvoice(T(s), id); logAction(s, "consulting.invoice.pay", "client_invoice", v.ref, { gross: v.gross }); json(res, 200, { invoice: v }); }); }
  /* Voids an invoice (an issued one with a `reason`): its entry is undone in the books and its time and expenses can be billed again. */
  function apiClientInvoiceVoid(req, res, url, s, body, id) { return answer(s, res, () => { const v = CS().voidInvoice(T(s), id, B(body).reason); logAction(s, "consulting.invoice.void", "client_invoice", v.ref, { reason: B(body).reason }); json(res, 200, { invoice: v }); }); }
  /* What each client owes, by how overdue it is. */
  function apiReceivables(req, res, url, s) { return answer(s, res, () => json(res, 200, { receivables: CS().receivables(T(s)) })); }

  /* Proposals, newest first; `status` and `deal_id` narrow them. */
  function apiProposals(req, res, url, s) { return answer(s, res, () => json(res, 200, { proposals: CS().proposals(T(s), { status: q(url, "status"), deal_id: q(url, "deal_id") }) })); }
  /* Drafts a proposal, or changes a draft (`id`): `deal_id` (its company, contact, title and currency come with it), `company_id`, `contact_id`, `title`, `intro`, `currency`, `billing`, `lines` `[{ kind: time | fixed | expense, description, qty, rate }]`, `tax_pct`, `valid_until`. */
  function apiProposalSave(req, res, url, s, body) { return answer(s, res, () => { const p = CS().saveProposal(T(s), B(body), who(s)); logAction(s, "consulting.proposal.save", "proposal", p.ref, { total: p.total }); json(res, 200, { proposal: p }); }); }
  /* One proposal with its lines, its company, contact and deal. */
  function apiProposal(req, res, url, s, body, id) { return answer(s, res, () => json(res, 200, { proposal: CS().proposal(T(s), id) })); }
  /* Sends a draft: it gets a private link for the client, is emailed to `to` or the contact, and its deal moves to the proposal stage. Returns the link. */
  function apiProposalSend(req, res, url, s, body, id) {
    return answer(s, res, async () => {
      const base = publicLink ? publicLink(req, s, "proposal.html", {}) : null;
      const r = await CS().sendProposal(T(s), id, { ...B(body), link_base: base ? base + (base.includes("?") ? "&" : "?") + "t=" : "" }, who(s));
      logAction(s, "consulting.proposal.send", "proposal", r.proposal.ref, { emailed: r.emailed }); json(res, 200, r);
    });
  }
  /* Records the client's answer given another way: `accept` true or false, and a `reason` for a decline. Accepted, the project starts and the deal is won. */
  function apiProposalAnswer(req, res, url, s, body, id) { return answer(s, res, () => { const p = CS().recordAnswer(T(s), id, B(body), who(s)); logAction(s, "consulting.proposal.answer", "proposal", p.ref, { status: p.status }); json(res, 200, { proposal: p }); }); }
  /* Withdraws a draft or sent proposal; its link stops accepting answers. */
  function apiProposalWithdraw(req, res, url, s, body, id) { return answer(s, res, () => json(res, 200, { proposal: CS().withdraw(T(s), id) })); }
  /* Makes a declined, expired or withdrawn proposal a draft again; its old link stops working. */
  function apiProposalRedraft(req, res, url, s, body, id) { return answer(s, res, () => json(res, 200, { proposal: CS().redraft(T(s), id) })); }

  /* The resource plan: who is booked on which project, week by week from `from` for `weeks`, against their capacity. */
  function apiPlan(req, res, url, s) { return answer(s, res, () => json(res, 200, CS().plan(T(s), { from: q(url, "from") || undefined, weeks: q(url, "weeks") }))); }
  /* Books a person onto a project for a week: `employee_id`, `project_id`, `week` (its Monday), `hours` (0 takes the booking off). Says whether they are now booked past their capacity. */
  function apiPlanSet(req, res, url, s, body) { return answer(s, res, () => json(res, 200, { booking: CS().allocate(T(s), B(body)) })); }
  /* Utilisation from `from` to `to`: each person's capacity against what was planned, logged and billable. */
  function apiUtilisation(req, res, url, s) { return answer(s, res, () => json(res, 200, CS().utilisation(T(s), { from: q(url, "from") || undefined, to: q(url, "to") || undefined }))); }

  /* The proposal a client's link (`t`) shows: what is offered, for how much, until when, and whether it can still be answered. Needs no sign-in. */
  function apiProposalPublic(req, res, url) {
    const v = CS().publicView(url.searchParams.get("t"));
    if (!v) return bad(res, "This link is not valid", 404);
    res.setHeader && res.setHeader("Cache-Control", "no-store");
    json(res, 200, { proposal: v });
  }
  /* The client's answer from their link: `t`, `accept` true or false, `name` (needed to accept), `reason`. Accepted, the store's project starts and its deal is won. Needs no sign-in. */
  function apiProposalPublicAnswer(req, res, url, s, body) {
    try { const b = B(body); json(res, 200, { proposal: CS().answerByClient(b.t, b) }); } catch (e) { bad(res, e.message, e.status || 400); }
  }

  return [
    ["GET /api/admin/consulting", apiConsulting],
    ["GET /api/admin/consulting/projects/:id", (r, re, u, s, b, p) => apiConsultingProject(r, re, u, s, b, p)],
    ["PUT /api/admin/consulting/projects/:id", (r, re, u, s, b, p) => apiConsultingProjectSet(r, re, u, s, b, p)],
    ["PUT /api/admin/consulting/people/:id", (r, re, u, s, b, p) => apiConsultingPerson(r, re, u, s, b, p)],
    ["GET /api/admin/consulting/timesheets", apiTimesheets],
    ["POST /api/admin/consulting/timesheets", apiTimesheetOpen],
    ["GET /api/admin/consulting/timesheets/:id", (r, re, u, s, b, p) => apiTimesheet(r, re, u, s, b, p)],
    ["PUT /api/admin/consulting/timesheets/:id", (r, re, u, s, b, p) => apiTimesheetSave(r, re, u, s, b, p)],
    ["POST /api/admin/consulting/timesheets/:id/submit", (r, re, u, s, b, p) => apiTimesheetSubmit(r, re, u, s, b, p)],
    ["POST /api/admin/consulting/timesheets/:id/approve", (r, re, u, s, b, p) => apiTimesheetApprove(r, re, u, s, b, p)],
    ["POST /api/admin/consulting/timesheets/:id/reject", (r, re, u, s, b, p) => apiTimesheetReject(r, re, u, s, b, p)],
    ["POST /api/admin/consulting/timesheets/:id/reopen", (r, re, u, s, b, p) => apiTimesheetReopen(r, re, u, s, b, p)],
    ["GET /api/admin/consulting/expenses", apiExpenses],
    ["POST /api/admin/consulting/expenses", apiExpenseSave],
    ["POST /api/admin/consulting/expenses/:id/submit", (r, re, u, s, b, p) => apiExpenseSubmit(r, re, u, s, b, p)],
    ["POST /api/admin/consulting/expenses/:id/approve", (r, re, u, s, b, p) => apiExpenseApprove(r, re, u, s, b, p)],
    ["POST /api/admin/consulting/expenses/:id/reject", (r, re, u, s, b, p) => apiExpenseReject(r, re, u, s, b, p)],
    ["POST /api/admin/consulting/expenses/:id/reopen", (r, re, u, s, b, p) => apiExpenseReopen(r, re, u, s, b, p)],
    ["POST /api/admin/consulting/expenses/:id/reimburse", (r, re, u, s, b, p) => apiExpenseReimburse(r, re, u, s, b, p)],
    ["GET /api/admin/consulting/invoices", apiClientInvoices],
    ["POST /api/admin/consulting/invoices", apiClientInvoiceDraft],
    ["GET /api/admin/consulting/invoices/:id", (r, re, u, s, b, p) => apiClientInvoice(r, re, u, s, b, p)],
    ["POST /api/admin/consulting/invoices/:id/issue", (r, re, u, s, b, p) => apiClientInvoiceIssue(r, re, u, s, b, p)],
    ["POST /api/admin/consulting/invoices/:id/pay", (r, re, u, s, b, p) => apiClientInvoicePay(r, re, u, s, b, p)],
    ["POST /api/admin/consulting/invoices/:id/void", (r, re, u, s, b, p) => apiClientInvoiceVoid(r, re, u, s, b, p)],
    ["GET /api/admin/consulting/receivables", apiReceivables],
    ["GET /api/admin/consulting/proposals", apiProposals],
    ["POST /api/admin/consulting/proposals", apiProposalSave],
    ["GET /api/admin/consulting/proposals/:id", (r, re, u, s, b, p) => apiProposal(r, re, u, s, b, p)],
    ["POST /api/admin/consulting/proposals/:id/send", (r, re, u, s, b, p) => apiProposalSend(r, re, u, s, b, p)],
    ["POST /api/admin/consulting/proposals/:id/answer", (r, re, u, s, b, p) => apiProposalAnswer(r, re, u, s, b, p)],
    ["POST /api/admin/consulting/proposals/:id/withdraw", (r, re, u, s, b, p) => apiProposalWithdraw(r, re, u, s, b, p)],
    ["POST /api/admin/consulting/proposals/:id/redraft", (r, re, u, s, b, p) => apiProposalRedraft(r, re, u, s, b, p)],
    ["GET /api/admin/consulting/plan", apiPlan],
    ["PUT /api/admin/consulting/plan", apiPlanSet],
    ["GET /api/admin/consulting/utilisation", apiUtilisation],
    ["GET /api/proposals/view", apiProposalPublic],
    ["POST /api/proposals/answer", apiProposalPublicAnswer]
  ];
} };
