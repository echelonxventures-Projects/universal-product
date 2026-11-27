/* LUXORA Platform — consultancy and professional services (owner Operations).

   The work a store's people do for its clients, and how it is billed. A project (projects) is done
   for a company (crm_companies) and billed by time and materials, at a fixed fee in instalments,
   or not at all. Each person keeps one timesheet a week (timesheets, time_entries) against
   projects and their tasks; it is submitted, then approved or sent back by someone else — on
   approval the hours are priced at the person's rate on that project and their cost, the tasks'
   logged hours and the project's spend go up, and nothing about the week changes after.
   Expenses are claimed (expense_claims), approved — the books owe the person — and paid back,
   and may be billed on to the client. An invoice to a client (client_invoices) is drafted from a
   project's approved, unbilled time and expenses, or a fixed-fee instalment: each entry is claimed
   by the invoice as it is drafted, so it is billed once even when two people draft at once, and a
   voided invoice gives it back. Issuing posts what the client owes; payment clears it (lib/books.js).

   A proposal (proposals) is drafted from a deal (crm_deals), sent to the client with a private link
   (public/proposal.html), and answered there or recorded by staff; accepted, it starts the project
   and wins the deal. The resource plan (resource_allocations) books people's weeks onto projects;
   utilisation sets what was planned and logged against each person's capacity.

   Projects, timesheets, claims, client invoices and proposals are records on the master
   (lib/seed/row-records.json), each moving through its state machine (lib/seed/states.json);
   what a day's work was, who did it and who answered stay in the tables. Policy is data
   (lib/seed/consulting.json). */
"use strict";

const crypto = require("crypto");
const db = () => require("./db.js");
const K = require("./kernel.js");
const RR = () => require("./row-records.js");
const OPS = () => require("./operations.js");
const states = require("./states.js");
const SEED = require("./seed/consulting.json");
const M = SEED.machines, R = SEED.records;
/* the line kinds an invoice is made of, by what each is (lib/seed/consulting.json lineKinds) */
const KIND = Object.fromEntries(["hourly", "instalment", "expense"].map(f => [f, Object.keys(SEED.lineKinds).find(k => SEED.lineKinds[k][f])]));
const billed = m => !!(m.byHour || m.byInstalment || m.expenses);
const fail = (msg, status, code) => { const e = new Error(msg); e.status = status || 400; if (code) e.code = code; throw e; };
const N = Number;
const r2 = n => +Number(n || 0).toFixed(2);
const str = (v, n) => String(v == null ? "" : v).trim().slice(0, n || 200);
const tx = fn => K.internal.tx(fn);
const ph = xs => "(" + (xs.length ? xs.map(() => "?").join(",") : "NULL") + ")";
const tagged = (m, s, t) => !!s && states.has(m, s) && states.is(m, s, t);
const inTag = (m, ...tags) => [...new Set(tags.flatMap(t => states.tagged(m, t)))];
const today = () => new Date().toISOString().slice(0, 10);
const isDate = d => /^\d{4}-\d{2}-\d{2}$/.test(String(d || "")) && !isNaN(Date.parse(d + "T00:00:00Z"));
const addDays = (d, n) => { const x = new Date(d + "T00:00:00Z"); x.setUTCDate(x.getUTCDate() + n); return x.toISOString().slice(0, 10); };
/* the Monday a date's week starts on */
function weekOf(d) {
  const day = d || today();
  if (!isDate(day)) fail("A date is written YYYY-MM-DD");
  const x = new Date(day + "T00:00:00Z"); x.setUTCDate(x.getUTCDate() - ((x.getUTCDay() + 6) % 7));
  return x.toISOString().slice(0, 10);
}
const policy = tid => { const own = require("./settings.js").get(N(tid), "consulting") || {}; return { selfApproval: own.selfApproval != null ? !!own.selfApproval : SEED.selfApproval }; };
const currencyOf = (tid, c) => { const u = str(c || require("./defaults.js").currency(N(tid)), 8).toUpperCase(); require("./wallet.js").unitOf(u); return u; };
function nextRef(tid, record, table) {
  const n = db().get(`SELECT COUNT(*) c FROM ${table} WHERE tenant_id=?`, N(tid)).c + 1;
  return `${SEED.refs[record]}-${N(tid)}-${String(n).padStart(5, "0")}`;
}
/* a record moves only as its machine allows; the state's stamps come with it */
function move(record, table, row, to, extra) {
  const { patch } = states.apply(record, { tenantId: row.tenant_id, from: row.status, to, row });
  const all = { ...patch, ...(extra || {}) }, cols = Object.keys(all);
  RR().change(record, row.id, () => {
    const r = db().run(`UPDATE ${table} SET ${cols.map(c => c + "=?").join(", ")} WHERE id=? AND status=?`, ...cols.map(c => all[c]), row.id, row.status);
    if (!r.changes) fail("This has just changed — reload it", 409);
    return r;
  });
  return db().get(`SELECT * FROM ${table} WHERE id=?`, row.id);
}
const by = actor => str(actor, 120);
/* whoever submitted a timesheet or a claim, or the person it is for, does not approve it — unless the store allows it */
function mayApprove(tid, row, person, actor) {
  if (policy(tid).selfApproval) return;
  const a = by(actor).toLowerCase();
  if (!a) fail("Say who approves", 403);
  if (a === String(row.submitted_by || "").toLowerCase() || (person.email && a === String(person.email).toLowerCase()))
    fail("Someone other than the person who submitted it approves it", 403, "self_approval");
}

/* ============================== people and projects ============================== */
const personRow = (tid, id) => db().get("SELECT * FROM employees WHERE id=? AND tenant_id=?", N(id), N(tid)) || fail("No such person", 404);
const capacityOf = p => p.capacity_hours != null ? N(p.capacity_hours) : SEED.defaultCapacityHours;
function people(tid) {
  const cur = states.tagged("employee", "current");
  return db().all(`SELECT id, code, name, email, department, designation, status, bill_rate, cost_rate, capacity_hours FROM employees WHERE tenant_id=? AND status IN ${ph(cur)} ORDER BY name`, N(tid), ...cur)
    .map(p => ({ ...p, capacity: capacityOf(p) }));
}
/* the person a member of staff is, by their email */
const meOf = (tid, email) => email ? db().get("SELECT id, name FROM employees WHERE tenant_id=? AND lower(email)=lower(?)", N(tid), str(email)) : null;
/* { bill_rate, cost_rate, capacity_hours } */
function setPerson(tid, id, input) {
  const p = personRow(tid, id), i = input || {}, set = {};
  for (const k of ["bill_rate", "cost_rate"]) if (i[k] !== undefined) { const v = r2(i[k]); if (!(v >= 0)) fail("A rate is zero or more"); set[k] = v; }
  if (i.capacity_hours !== undefined) {
    if (i.capacity_hours === null || i.capacity_hours === "") set.capacity_hours = null;
    else { const v = r2(i.capacity_hours); if (!(v >= 0 && v <= 168)) fail("A week holds 0 to 168 hours"); set.capacity_hours = v; }
  }
  const k = Object.keys(set);
  if (Object.keys(set).length) OPS().setPersonFields(N(tid), p.id, set);
  return people(tid).find(x => x.id === p.id) || personRow(tid, id);
}

const projectRow = (tid, id) => db().get("SELECT * FROM projects WHERE id=? AND tenant_id=?", N(id), N(tid)) || fail("No such project", 404);
const modelOf = p => SEED.billing[p.billing] || SEED.billing.non_billable;
const projCurrency = p => p.currency || require("./defaults.js").currency(p.tenant_id);
const open = p => !(states.has(M.project, p.status) && states.is(M.project, p.status, "terminal"));
/* how a project is billed: { billing, company_id, currency, bill_rate, tax_pct, rates: [{ employee_id, rate | null }] } */
function setProject(tid, id, input) {
  const p = projectRow(tid, id), i = input || {}, set = {};
  if (i.billing !== undefined) { if (!SEED.billing[i.billing]) fail("A project is billed one of: " + Object.keys(SEED.billing).join(", ")); set.billing = i.billing; }
  if (i.company_id !== undefined) {
    if (i.company_id) { const c = db().get("SELECT id, name FROM crm_companies WHERE id=? AND tenant_id=? AND deleted_at IS NULL", N(i.company_id), N(tid)) || fail("No such company", 404); set.company_id = c.id; set.client = c.name; }
    else set.company_id = null;
  }
  if (i.currency !== undefined) {
    const c = currencyOf(tid, i.currency);
    if (c !== projCurrency(p) && db().get("SELECT 1 FROM client_invoices WHERE project_id=? LIMIT 1", p.id)) fail("This project already has invoices in " + projCurrency(p), 409);
    set.currency = c;
  }
  if (i.bill_rate !== undefined) { const v = r2(i.bill_rate); if (!(v >= 0)) fail("A rate is zero or more"); set.bill_rate = v; }
  if (i.tax_pct !== undefined) { const v = N(i.tax_pct); if (!(v >= 0 && v <= 100)) fail("Tax is 0 to 100 percent"); set.tax_pct = r2(v); }
  if (i.budget !== undefined) { const v = r2(i.budget); if (!(v >= 0)) fail("A budget is zero or more"); set.budget = v; }
  return tx(() => {
    OPS().setProjectFields(N(tid), p.id, set);
    for (const r of Array.isArray(i.rates) ? i.rates : []) {
      personRow(tid, r.employee_id);
      if (r.rate === null || r.rate === "" || r.rate === undefined) db().run("DELETE FROM project_rates WHERE project_id=? AND employee_id=?", p.id, N(r.employee_id));
      else { const v = r2(r.rate); if (!(v >= 0)) fail("A rate is zero or more");
        db().run("INSERT INTO project_rates(tenant_id, project_id, employee_id, rate) VALUES(?,?,?,?) ON CONFLICT(project_id, employee_id) DO UPDATE SET rate=excluded.rate", N(tid), p.id, N(r.employee_id), v); }
    }
    return project(tid, p.id);
  });
}
/* the rate an hour of a person's time on a project is billed at: the project's own rate for them, the project's rate, their own */
function rateFor(p, person) {
  const own = db().get("SELECT rate FROM project_rates WHERE project_id=? AND employee_id=?", p.id, person.id);
  if (own) return N(own.rate);
  return N(p.bill_rate) > 0 ? N(p.bill_rate) : N(person.bill_rate) || 0;
}
function costFor(tid, person) {
  if (N(person.cost_rate) > 0) return N(person.cost_rate);
  const c = require("./capabilities.js").cap(N(tid), "projects");
  return N(c && c.internal_cost_per_hour) || 0;
}
const approvedSheets = () => states.tagged(M.timesheet, "approved");
const loggedSheets = () => inTag(M.timesheet, "pending", "approved");
const claimApproved = () => states.tagged(M.expense, "approved");
const billedInv = () => states.tagged(M.invoice, "billed");
/* one project with how it is billed and where its money stands */
function project(tid, id) {
  const p = projectRow(tid, id), t = N(tid), cur = projCurrency(p);
  const ap = approvedSheets(), done = billedInv();
  const time = db().get(`SELECT COALESCE(SUM(e.hours),0) h, COALESCE(SUM(CASE WHEN e.billable=1 THEN e.hours ELSE 0 END),0) bh,
      COALESCE(SUM(CASE WHEN e.billable=1 AND e.invoice_id IS NULL THEN e.hours ELSE 0 END),0) uh, COALESCE(SUM(CASE WHEN e.billable=1 AND e.invoice_id IS NULL THEN e.hours*e.rate ELSE 0 END),0) ua,
      COALESCE(SUM(e.hours*e.cost_rate),0) cost
      FROM time_entries e JOIN timesheets s ON s.id=e.timesheet_id WHERE e.tenant_id=? AND e.project_id=? AND s.status IN ${ph(ap)}`, t, p.id, ...ap);
  const exp = db().get(`SELECT COALESCE(SUM(amount),0) a, COALESCE(SUM(CASE WHEN billable=1 AND invoice_id IS NULL AND currency=? THEN amount ELSE 0 END),0) ub FROM expense_claims WHERE tenant_id=? AND project_id=? AND status IN ${ph(claimApproved())}`, cur, t, p.id, ...claimApproved());
  const inv = db().get(`SELECT COALESCE(SUM(gross),0) g, COALESCE(SUM(CASE WHEN status IN ${ph(states.tagged(M.invoice, "success"))} THEN gross ELSE 0 END),0) paid FROM client_invoices WHERE project_id=? AND status IN ${ph(done)}`, ...states.tagged(M.invoice, "success"), p.id, ...done);
  const company = p.company_id ? (db().get("SELECT name FROM crm_companies WHERE id=?", p.company_id) || {}).name : null;
  const m = modelOf(p);
  return { ...p, company, currency: cur, billingLabel: m.label, byHour: m.byHour, byInstalment: m.byInstalment, billsExpenses: m.expenses, billed: billed(m), open: open(p),
    rates: db().all("SELECT r.employee_id, e.name, r.rate FROM project_rates r JOIN employees e ON e.id=r.employee_id WHERE r.project_id=? ORDER BY e.name", p.id),
    hours: r2(time.h), billableHours: r2(time.bh), unbilledHours: r2(time.uh), unbilledTime: r2(time.ua), cost: r2(time.cost),
    expenses: r2(exp.a), unbilledExpenses: r2(exp.ub), invoiced: r2(inv.g), paid: r2(inv.paid), fixedBilled: fixedBilled(p), fixedLeft: m.byInstalment ? r2(N(p.budget) - fixedBilled(p)) : 0 };
}
function fixedBilled(p) {
  const live = db().all("SELECT id FROM client_invoices WHERE project_id=? AND status NOT IN " + ph(states.tagged(M.invoice, "void")), p.id, ...states.tagged(M.invoice, "void")).map(r => r.id);
  return r2(live.length ? db().get(`SELECT COALESCE(SUM(amount),0) a FROM client_invoice_lines WHERE kind=? AND invoice_id IN ${ph(live)}`, KIND.instalment, ...live).a : 0);
}
function projects(tid) {
  return db().all("SELECT id FROM projects WHERE tenant_id=? ORDER BY status, code LIMIT 300", N(tid)).map(r => project(tid, r.id));
}

/* ============================== timesheets ============================== */
const sheetRow = (tid, id) => db().get("SELECT * FROM timesheets WHERE id=? AND tenant_id=?", N(id), N(tid)) || fail("No such timesheet", 404);
function sheetActions(s) {
  const m = M.timesheet, out = [];
  if (tagged(m, s.status, "editable")) out.push("save", "submit");
  if (tagged(m, s.status, "pending")) out.push("approve", "reject");
  if (tagged(m, s.status, "rejected")) out.push("reopen");
  return out;
}
/* a person's timesheet for a week, opened if they have none: { employee_id, week } */
function openSheet(tid, input) {
  const i = input || {}, p = personRow(tid, i.employee_id), week = weekOf(i.week);
  const ex = db().get("SELECT id FROM timesheets WHERE tenant_id=? AND employee_id=? AND week=?", N(tid), p.id, week);
  if (ex) return sheet(tid, ex.id);
  const r = RR().created(R.timesheet, () => db().run("INSERT INTO timesheets(tenant_id, ref, employee_id, week, status) VALUES(?,?,?,?,?)",
    N(tid), nextRef(tid, R.timesheet, "timesheets"), p.id, week, states.initial(M.timesheet)));
  return sheet(tid, N(r.lastInsertRowid));
}
function sheet(tid, id) {
  const s = sheetRow(tid, id), p = personRow(tid, s.employee_id);
  const entries = db().all(`SELECT e.*, p.code project_code, p.name project_name, t.title task FROM time_entries e JOIN projects p ON p.id=e.project_id LEFT JOIN tasks t ON t.id=e.task_id
     WHERE e.timesheet_id=? ORDER BY e.date, e.id`, s.id);
  const days = [0, 1, 2, 3, 4, 5, 6].map(n => addDays(s.week, n));
  return { ...s, person: p.name, capacity: capacityOf(p), days, perDay: days.map(d => r2(entries.filter(e => e.date === d).reduce((a, e) => a + e.hours, 0))), entries, actions: sheetActions(s) };
}
/* the week's entries, replaced as a whole while it is a draft: [{ project_id, task_id?, date, hours, billable?, note? }] */
function saveEntries(tid, id, list) {
  const s = sheetRow(tid, id);
  if (!tagged(M.timesheet, s.status, "editable")) fail("Only a draft timesheet is changed", 409);
  if (!Array.isArray(list)) fail("Send the week's entries as a list");
  if (list.length > 200) fail("A week holds at most 200 entries");
  const end = addDays(s.week, 6), perDay = {};
  const rows = list.map(raw => {
    const e = raw || {}, p = projectRow(tid, e.project_id), date = str(e.date, 10), hours = r2(e.hours);
    if (!open(p)) fail(p.code + " is closed: time is not logged on it", 409);
    if (!isDate(date) || date < s.week || date > end) fail("Each entry is a day of the week of " + s.week);
    if (!(hours > 0 && hours <= SEED.maxHoursPerDay)) fail("An entry is more than 0 and at most " + SEED.maxHoursPerDay + " hours");
    perDay[date] = r2((perDay[date] || 0) + hours);
    if (perDay[date] > SEED.maxHoursPerDay) fail(date + " holds more than " + SEED.maxHoursPerDay + " hours");
    if (e.task_id && !db().get("SELECT id FROM tasks WHERE id=? AND tenant_id=? AND project_id=?", N(e.task_id), N(tid), p.id)) fail("That task is not on " + p.code);
    const m = modelOf(p), billable = e.billable === undefined ? m.billable : !!e.billable;
    if (billable && !m.byHour) fail(p.code + " is " + m.label.toLowerCase() + ": its time is not billed by the hour");
    return { project_id: p.id, task_id: e.task_id ? N(e.task_id) : null, date, hours, billable: billable ? 1 : 0, note: str(e.note, 500) };
  });
  return tx(() => {
    db().run("DELETE FROM time_entries WHERE timesheet_id=?", s.id);
    for (const r of rows) db().run("INSERT INTO time_entries(tenant_id, timesheet_id, employee_id, project_id, task_id, date, hours, billable, note) VALUES(?,?,?,?,?,?,?,?,?)",
      N(tid), s.id, s.employee_id, r.project_id, r.task_id, r.date, r.hours, r.billable, r.note);
    const hours = r2(rows.reduce((a, r) => a + r.hours, 0)), billable = r2(rows.filter(r => r.billable).reduce((a, r) => a + r.hours, 0));
    RR().change(R.timesheet, s.id, () => db().run("UPDATE timesheets SET hours=?, billable_hours=? WHERE id=?", hours, billable, s.id));
    return sheet(tid, s.id);
  });
}
function submitSheet(tid, id, actor) {
  const s = sheetRow(tid, id);
  if (!tagged(M.timesheet, s.status, "editable")) fail("Only a draft timesheet is submitted", 409);
  if (!db().get("SELECT 1 FROM time_entries WHERE timesheet_id=? LIMIT 1", s.id)) fail("Log some time before submitting the week");
  move(M.timesheet, "timesheets", s, states.first(M.timesheet, "pending"), { submitted_by: by(actor), rejected_reason: "" });
  return sheet(tid, s.id);
}
/* approved: each hour is priced at the person's rate on its project and their cost, and adds to its task and its project */
function approveSheet(tid, id, actor) {
  const s = sheetRow(tid, id), person = personRow(tid, s.employee_id);
  if (!tagged(M.timesheet, s.status, "pending")) fail("Only a submitted timesheet is approved", 409);
  mayApprove(tid, s, person, actor);
  return tx(() => {
    const entries = db().all("SELECT * FROM time_entries WHERE timesheet_id=?", s.id), cost = costFor(tid, person), spent = {}, logged = {};
    for (const e of entries) {
      const p = projectRow(tid, e.project_id), rate = e.billable ? rateFor(p, person) : 0;
      db().run("UPDATE time_entries SET rate=?, cost_rate=?, currency=? WHERE id=?", rate, cost, projCurrency(p), e.id);
      spent[p.id] = r2((spent[p.id] || 0) + e.hours * cost);
      if (e.task_id) logged[e.task_id] = r2((logged[e.task_id] || 0) + e.hours);
    }
    for (const [task, h] of Object.entries(logged)) OPS().addLogged(N(tid), N(task), h);
    for (const [pid, v] of Object.entries(spent)) OPS().addSpent(N(tid), N(pid), v);
    move(M.timesheet, "timesheets", s, states.first(M.timesheet, "approved"), { approved_by: by(actor) });
    return sheet(tid, s.id);
  });
}
function rejectSheet(tid, id, actor, reason) {
  const s = sheetRow(tid, id);
  if (!str(reason)) fail("Say what needs changing");
  if (!tagged(M.timesheet, s.status, "pending")) fail("Only a submitted timesheet is sent back", 409);
  move(M.timesheet, "timesheets", s, states.first(M.timesheet, "rejected"), { rejected_reason: str(reason, 500), approved_by: by(actor) });
  return sheet(tid, s.id);
}
function reopenSheet(tid, id) {
  const s = sheetRow(tid, id);
  if (!tagged(M.timesheet, s.status, "rejected")) fail("Only a timesheet sent back is reopened", 409);
  move(M.timesheet, "timesheets", s, states.first(M.timesheet, "editable"));
  return sheet(tid, s.id);
}
function sheets(tid, f) {
  const o = f || {};
  return db().all(`SELECT s.*, e.name person FROM timesheets s JOIN employees e ON e.id=s.employee_id WHERE s.tenant_id=? AND (?='' OR s.status=?) AND (?=0 OR s.employee_id=?) AND (?='' OR s.week=?)
     ORDER BY s.week DESC, e.name LIMIT 300`, N(tid), str(o.status), str(o.status), N(o.employee_id) || 0, N(o.employee_id) || 0, str(o.week), str(o.week)).map(s => ({ ...s, actions: sheetActions(s) }));
}

/* ============================== expense claims ============================== */
const claimRow = (tid, id) => db().get("SELECT * FROM expense_claims WHERE id=? AND tenant_id=?", N(id), N(tid)) || fail("No such expense claim", 404);
function claimActions(c) {
  const m = M.expense, out = [];
  if (tagged(m, c.status, "editable")) out.push("save", "submit");
  if (tagged(m, c.status, "pending")) out.push("approve", "reject");
  if (tagged(m, c.status, "rejected")) out.push("reopen");
  if (tagged(m, c.status, "payable")) out.push("reimburse");
  return out;
}
/* { id?, employee_id, project_id?, date, category, description, amount, currency?, billable?, receipt_ref? } */
function saveClaim(tid, input) {
  const i = input || {}, t = N(tid);
  const ex = i.id ? claimRow(t, i.id) : null;
  if (ex && !tagged(M.expense, ex.status, "editable")) fail("Only a draft claim is changed", 409);
  const person = personRow(t, i.employee_id || (ex && ex.employee_id));
  const p = i.project_id ? projectRow(t, i.project_id) : null;
  if (p && !open(p)) fail(p.code + " is closed", 409);
  const date = str(i.date || today(), 10); if (!isDate(date)) fail("A date is written YYYY-MM-DD");
  if (date > today()) fail("An expense is claimed once it is spent");
  if (!SEED.expenseCategories.some(c => c.key === i.category)) fail("A claim is one of: " + SEED.expenseCategories.map(c => c.key).join(", "));
  const description = str(i.description, 300); if (!description) fail("Say what the expense was");
  const amount = r2(i.amount); if (!(amount > 0)) fail("A claim is for more than zero");
  const currency = currencyOf(t, i.currency || (p && projCurrency(p)));
  const billable = !!i.billable;
  if (billable && !(p && modelOf(p).expenses)) fail("Only an expense on a project billed to its client is billed on");
  const cols = { employee_id: person.id, project_id: p ? p.id : null, date, category: i.category, description, amount, currency, billable: billable ? 1 : 0, receipt_ref: str(i.receipt_ref, 200) };
  const k = Object.keys(cols);
  if (ex) { RR().change(R.expense, ex.id, () => db().run(`UPDATE expense_claims SET ${k.map(x => x + "=?").join(", ")} WHERE id=?`, ...k.map(x => cols[x]), ex.id)); return claim(t, ex.id); }
  const r = RR().created(R.expense, () => db().run(`INSERT INTO expense_claims(tenant_id, ref, status, ${k.join(",")}) VALUES(?,?,?,${k.map(() => "?").join(",")})`,
    t, nextRef(t, R.expense, "expense_claims"), states.initial(M.expense), ...k.map(x => cols[x])));
  return claim(t, N(r.lastInsertRowid));
}
function claim(tid, id) {
  const c = claimRow(tid, id);
  return { ...c, person: (personRow(tid, c.employee_id) || {}).name, project: c.project_id ? projectRow(tid, c.project_id).code : null, actions: claimActions(c) };
}
function submitClaim(tid, id, actor) {
  const c = claimRow(tid, id);
  if (!tagged(M.expense, c.status, "editable")) fail("Only a draft claim is submitted", 409);
  move(M.expense, "expense_claims", c, states.first(M.expense, "pending"), { submitted_by: by(actor), rejected_reason: "" });
  return claim(tid, id);
}
/* approved: the books owe the person (lib/books.js), and the project's spend goes up */
function approveClaim(tid, id, actor) {
  const c = claimRow(tid, id);
  if (!tagged(M.expense, c.status, "pending")) fail("Only a submitted claim is approved", 409);
  mayApprove(tid, c, personRow(tid, c.employee_id), actor);
  return tx(() => {
    if (c.project_id) OPS().addSpent(N(tid), c.project_id, c.amount);
    move(M.expense, "expense_claims", c, states.first(M.expense, "payable"), { approved_by: by(actor) });
    return claim(tid, id);
  });
}
function rejectClaim(tid, id, actor, reason) {
  const c = claimRow(tid, id);
  if (!str(reason)) fail("Say why the claim is sent back");
  if (!tagged(M.expense, c.status, "pending")) fail("Only a submitted claim is sent back", 409);
  move(M.expense, "expense_claims", c, states.first(M.expense, "rejected"), { rejected_reason: str(reason, 500), approved_by: by(actor) });
  return claim(tid, id);
}
function reopenClaim(tid, id) {
  const c = claimRow(tid, id);
  if (!tagged(M.expense, c.status, "rejected")) fail("Only a claim sent back is reopened", 409);
  move(M.expense, "expense_claims", c, states.first(M.expense, "editable"));
  return claim(tid, id);
}
/* paid back to the person: the books clear what was owed from the bank */
function reimburse(tid, id) {
  const c = claimRow(tid, id);
  if (!tagged(M.expense, c.status, "payable")) fail("Only an approved claim not yet paid back is paid", 409);
  move(M.expense, "expense_claims", c, states.first(M.expense, "success"));
  return claim(tid, id);
}
function claims(tid, f) {
  const o = f || {};
  return db().all(`SELECT c.*, e.name person, p.code project FROM expense_claims c JOIN employees e ON e.id=c.employee_id LEFT JOIN projects p ON p.id=c.project_id
     WHERE c.tenant_id=? AND (?='' OR c.status=?) AND (?=0 OR c.employee_id=?) AND (?=0 OR c.project_id=?) ORDER BY c.id DESC LIMIT 300`,
    N(tid), str(o.status), str(o.status), N(o.employee_id) || 0, N(o.employee_id) || 0, N(o.project_id) || 0, N(o.project_id) || 0).map(c => ({ ...c, actions: claimActions(c) }));
}

/* ============================== invoices to clients ============================== */
const invoiceRow = (tid, id) => db().get("SELECT * FROM client_invoices WHERE id=? AND tenant_id=?", N(id), N(tid)) || fail("No such invoice", 404);
function invoiceActions(v) {
  const m = M.invoice, out = [];
  if (tagged(m, v.status, "editable")) out.push("issue", "void");
  if (tagged(m, v.status, "receivable")) out.push("pay", "void");
  return out;
}
/* what a project has that is ready to bill up to a day: approved billable time not yet on an invoice, and approved billable expenses in its currency */
function unbilled(tid, projectId, through) {
  const p = projectRow(tid, projectId), cur = projCurrency(p), upto = through ? str(through, 10) : today();
  if (!isDate(upto)) fail("A date is written YYYY-MM-DD");
  const m = modelOf(p), ap = approvedSheets(), ca = claimApproved();
  const time = m.byHour ? db().all(`SELECT e.*, emp.name person FROM time_entries e JOIN timesheets s ON s.id=e.timesheet_id JOIN employees emp ON emp.id=e.employee_id
     WHERE e.tenant_id=? AND e.project_id=? AND e.billable=1 AND e.invoice_id IS NULL AND s.status IN ${ph(ap)} AND e.date<=? ORDER BY e.date, e.id`, N(tid), p.id, ...ap, upto) : [];
  const exp = m.expenses ? db().all(`SELECT * FROM expense_claims WHERE tenant_id=? AND project_id=? AND billable=1 AND invoice_id IS NULL AND status IN ${ph(ca)} AND date<=? ORDER BY date, id`, N(tid), p.id, ...ca, upto) : [];
  return { project: p, currency: cur, through: upto, time, expenses: exp.filter(c => c.currency === cur), otherCurrency: exp.filter(c => c.currency !== cur) };
}
/* a draft invoice for a project: { project_id, through?, fixed_amount?, fixed_description?, time?: false, expenses?: false, tax_pct?, note? } */
function draftInvoice(tid, input, actor) {
  const i = input || {}, t = N(tid), u = unbilled(t, i.project_id, i.through), p = u.project, m = modelOf(p);
  if (!billed(m)) fail(p.code + " is not billed to a client", 409);
  if (!p.company_id) fail("Say which company " + p.code + " is for before billing it", 409);
  const lines = [], timeIds = [], claimIds = [];
  if (i.time !== false) {
    const groups = {};
    for (const e of u.time) { const k = e.employee_id + "|" + e.rate; (groups[k] = groups[k] || { person: e.person, rate: N(e.rate), hours: 0 }).hours = r2(groups[k].hours + e.hours); timeIds.push(e.id); }
    for (const g of Object.values(groups)) lines.push({ kind: KIND.hourly, description: `${g.person} — ${g.hours} h`, qty: g.hours, rate: g.rate, amount: r2(g.hours * g.rate) });
  }
  if (i.fixed_amount !== undefined && i.fixed_amount !== null && i.fixed_amount !== "") {
    if (!m.byInstalment) fail(p.code + " is billed by time, not by fixed instalments");
    const a = r2(i.fixed_amount), left = r2(N(p.budget) - fixedBilled(p));
    if (!(a > 0)) fail("An instalment is more than zero");
    if (N(p.budget) > 0 && a > left) fail(`Only ${left} ${u.currency} of the fixed fee is left to bill`, 409, "over_fee");
    lines.push({ kind: KIND.instalment, description: str(i.fixed_description, 200) || "Fixed fee instalment", qty: 1, rate: a, amount: a });
  }
  if (i.expenses !== false) for (const c of u.expenses) {
    const cat = (SEED.expenseCategories.find(x => x.key === c.category) || { label: c.category }).label;
    lines.push({ kind: KIND.expense, description: `${cat}: ${c.description} (${c.date})`, qty: 1, rate: c.amount, amount: c.amount }); claimIds.push(c.id);
  }
  if (!lines.length) fail("Nothing on " + p.code + " is ready to bill", 409, "nothing_to_bill");
  const fees = r2(lines.filter(l => l.kind !== KIND.expense).reduce((a, l) => a + l.amount, 0)), expenses = r2(lines.filter(l => l.kind === KIND.expense).reduce((a, l) => a + l.amount, 0));
  const taxPct = i.tax_pct !== undefined && i.tax_pct !== "" ? N(i.tax_pct) : N(p.tax_pct);
  if (!(taxPct >= 0 && taxPct <= 100)) fail("Tax is 0 to 100 percent");
  const tax = r2((fees + expenses) * taxPct / 100);
  return tx(() => {
    const r = RR().created(R.invoice, () => db().run("INSERT INTO client_invoices(tenant_id, ref, project_id, company_id, currency, period_to, fees, expenses, tax_pct, tax, gross, status, note, created_by) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
      t, nextRef(t, R.invoice, "client_invoices"), p.id, p.company_id, u.currency, u.through, fees, expenses, r2(taxPct), tax, r2(fees + expenses + tax), states.initial(M.invoice), str(i.note, 1000), by(actor)));
    const id = N(r.lastInsertRowid);
    /* each entry is claimed by this invoice only if no other has it: a second draft at the same moment finds it taken */
    if (timeIds.length && db().run(`UPDATE time_entries SET invoice_id=? WHERE id IN ${ph(timeIds)} AND invoice_id IS NULL`, id, ...timeIds).changes !== timeIds.length)
      fail("Some of this time was billed a moment ago — draft the invoice again", 409, "already_billed");
    if (claimIds.length) RR().changeWhere(R.expense, `id IN ${ph(claimIds)}`, claimIds, () => {
      const w = db().run(`UPDATE expense_claims SET invoice_id=? WHERE id IN ${ph(claimIds)} AND invoice_id IS NULL`, id, ...claimIds);
      if (w.changes !== claimIds.length) fail("Some of these expenses were billed a moment ago — draft the invoice again", 409, "already_billed");
      return w;
    });
    for (const l of lines) db().run("INSERT INTO client_invoice_lines(invoice_id, kind, description, qty, rate, amount) VALUES(?,?,?,?,?,?)", id, l.kind, l.description, l.qty, l.rate, l.amount);
    return invoice(t, id);
  });
}
function invoice(tid, id) {
  const v = invoiceRow(tid, id), p = projectRow(tid, v.project_id);
  const company = v.company_id ? db().get("SELECT name, tax_id, country FROM crm_companies WHERE id=?", v.company_id) : null;
  return { ...v, project: { id: p.id, code: p.code, name: p.name }, company, store: (db().get("SELECT name FROM tenants WHERE id=?", N(tid)) || {}).name,
    lines: db().all("SELECT kind, description, qty, rate, amount FROM client_invoice_lines WHERE invoice_id=? ORDER BY id", v.id), actions: invoiceActions(v) };
}
function invoiceText(v) {
  const m = n => `${Number(n).toFixed(2)} ${v.currency}`;
  return [`Invoice ${v.ref} from ${v.store}`, `For ${v.company ? v.company.name : ""} — ${v.project.code} ${v.project.name}`, `Issued ${String(v.issued_at || "").slice(0, 10)}, due ${v.due_at || ""}`, "",
    ...v.lines.map(l => `${l.description}: ${m(l.amount)}`), "", `Fees ${m(v.fees)}`, `Expenses ${m(v.expenses)}`, `Tax (${v.tax_pct}%) ${m(v.tax)}`, `Total due ${m(v.gross)}`].join("\n");
}
/* issued: the client owes it (lib/books.js); with `send_to`, it is emailed there */
async function issueInvoice(tid, id, input) {
  const v = invoiceRow(tid, id), i = input || {}, to = str(i.send_to, 200).toLowerCase();
  if (!tagged(M.invoice, v.status, "editable")) fail("Only a draft invoice is issued", 409);
  if (to && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(to)) fail("That email does not look right");
  move(M.invoice, "client_invoices", v, states.first(M.invoice, "receivable"), { due_at: addDays(today(), SEED.invoiceTermsDays), sent_to: to });
  const out = invoice(tid, id);
  let emailed = false;
  if (to) { const r = await require("./mailer.js").send({ tenantId: N(tid), channel: "email", to, subject: `Invoice ${out.ref} from ${out.store}`, text: invoiceText(out), kind: R.invoice }); emailed = !!(r && r.sent); }
  return { ...out, emailed };
}
function payInvoice(tid, id) {
  const v = invoiceRow(tid, id);
  if (!tagged(M.invoice, v.status, "receivable")) fail("Only an issued, unpaid invoice is paid", 409);
  move(M.invoice, "client_invoices", v, states.first(M.invoice, "success"));
  return invoice(tid, id);
}
/* voided: an issued invoice's entry is undone in the books, and its time and expenses are ready to bill again */
function voidInvoice(tid, id, reason) {
  const v = invoiceRow(tid, id);
  if (tagged(M.invoice, v.status, "receivable") && !str(reason)) fail("Say why an issued invoice is voided");
  return tx(() => {
    move(M.invoice, "client_invoices", v, states.first(M.invoice, "void"), { void_reason: str(reason, 300) });
    db().run("UPDATE time_entries SET invoice_id=NULL WHERE invoice_id=?", v.id);
    RR().changeWhere(R.expense, "invoice_id=?", [v.id], () => db().run("UPDATE expense_claims SET invoice_id=NULL WHERE invoice_id=?", v.id));
    return invoice(tid, id);
  });
}
function invoices(tid, f) {
  const o = f || {};
  return db().all(`SELECT v.*, p.code project, c.name company FROM client_invoices v JOIN projects p ON p.id=v.project_id LEFT JOIN crm_companies c ON c.id=v.company_id
     WHERE v.tenant_id=? AND (?='' OR v.status=?) AND (?=0 OR v.project_id=?) ORDER BY v.id DESC LIMIT 300`, N(tid), str(o.status), str(o.status), N(o.project_id) || 0, N(o.project_id) || 0)
    .map(v => ({ ...v, actions: invoiceActions(v) }));
}
/* what each client owes, by how overdue it is */
function receivables(tid) {
  const t = today(), due = states.tagged(M.invoice, "receivable");
  const rows = db().all(`SELECT v.*, c.name company FROM client_invoices v LEFT JOIN crm_companies c ON c.id=v.company_id WHERE v.tenant_id=? AND v.status IN ${ph(due)}`, N(tid), ...due);
  const out = {};
  for (const v of rows) {
    const k = v.company + "|" + v.currency, late = v.due_at && v.due_at < t ? Math.floor((Date.parse(t) - Date.parse(v.due_at)) / 86400e3) : 0;
    const x = out[k] = out[k] || { company: v.company, currency: v.currency, current: 0, d1_30: 0, d31_60: 0, d60plus: 0, total: 0 };
    const b = late <= 0 ? "current" : late <= 30 ? "d1_30" : late <= 60 ? "d31_60" : "d60plus";
    x[b] = r2(x[b] + v.gross); x.total = r2(x.total + v.gross);
  }
  return Object.values(out);
}

/* ============================== proposals ============================== */
const proposalRow = (tid, id) => db().get("SELECT * FROM proposals WHERE id=? AND tenant_id=?", N(id), N(tid)) || fail("No such proposal", 404);
function proposalActions(p) {
  const m = M.proposal, out = [];
  if (tagged(m, p.status, "editable")) out.push("save", "send", "withdraw");
  if (tagged(m, p.status, "awaiting")) out.push("accept", "decline", "withdraw");
  if (tagged(m, p.status, "closed")) out.push("redraft");
  return out;
}
const linesOf = p => { try { return JSON.parse(p.lines || "[]"); } catch (e) { return []; } };
/* { id?, deal_id?, company_id?, contact_id?, title, intro?, currency?, billing?, lines: [{ kind, description, qty, rate }], tax_pct?, valid_until? } */
function saveProposal(tid, input, actor) {
  const i = input || {}, t = N(tid), ex = i.id ? proposalRow(t, i.id) : null;
  if (ex && !tagged(M.proposal, ex.status, "editable")) fail("Only a draft proposal is changed", 409);
  const deal = i.deal_id ? db().get("SELECT * FROM crm_deals WHERE id=? AND tenant_id=?", N(i.deal_id), t) || fail("No such deal", 404) : null;
  const companyId = i.company_id ? N(i.company_id) : deal ? deal.company_id : ex ? ex.company_id : null;
  if (companyId && !db().get("SELECT id FROM crm_companies WHERE id=? AND tenant_id=? AND deleted_at IS NULL", companyId, t)) fail("No such company", 404);
  const contactId = i.contact_id ? N(i.contact_id) : deal ? deal.contact_id : ex ? ex.contact_id : null;
  if (contactId && !db().get("SELECT id FROM crm_contacts WHERE id=? AND tenant_id=? AND deleted_at IS NULL", contactId, t)) fail("No such contact", 404);
  const title = str(i.title || (deal && deal.title), 160); if (!title) fail("Name the proposal");
  const billing = i.billing || (ex && ex.billing) || SEED.defaultProposalBilling;
  if (!SEED.billing[billing] || !billed(SEED.billing[billing])) fail("A proposal is for work billed " + Object.keys(SEED.billing).filter(k => billed(SEED.billing[k])).join(" or "));
  const currency = currencyOf(t, i.currency || (deal && deal.currency) || (ex && ex.currency));
  if (!Array.isArray(i.lines) || !i.lines.length) fail("A proposal has at least one line");
  if (i.lines.length > 100) fail("A proposal has at most 100 lines");
  const lines = i.lines.map(raw => {
    const l = raw || {};
    if (!SEED.lineKinds[l.kind]) fail("A line is one of: " + Object.keys(SEED.lineKinds).join(", "));
    const description = str(l.description, 300); if (!description) fail("Say what each line is");
    const qty = r2(l.qty === undefined ? 1 : l.qty), rate = r2(l.rate);
    if (!(qty > 0)) fail("A line's quantity is more than zero");
    if (!(rate >= 0)) fail("A line's rate is zero or more");
    return { kind: l.kind, description, qty, rate, amount: r2(qty * rate) };
  });
  const taxPct = N(i.tax_pct || 0); if (!(taxPct >= 0 && taxPct <= 100)) fail("Tax is 0 to 100 percent");
  const validUntil = i.valid_until ? str(i.valid_until, 10) : null;
  if (validUntil && (!isDate(validUntil) || validUntil < today())) fail("A proposal is valid until today or later");
  const net = r2(lines.reduce((a, l) => a + l.amount, 0)), tax = r2(net * taxPct / 100);
  const cols = { deal_id: deal ? deal.id : ex ? ex.deal_id : null, company_id: companyId, contact_id: contactId, title, intro: str(i.intro, 4000), currency, billing, lines: JSON.stringify(lines), net, tax_pct: r2(taxPct), tax, total: r2(net + tax), valid_until: validUntil };
  const k = Object.keys(cols);
  if (ex) { RR().change(R.proposal, ex.id, () => db().run(`UPDATE proposals SET ${k.map(x => x + "=?").join(", ")} WHERE id=?`, ...k.map(x => cols[x]), ex.id)); return proposal(t, ex.id); }
  const r = RR().created(R.proposal, () => db().run(`INSERT INTO proposals(tenant_id, ref, status, created_by, ${k.join(",")}) VALUES(?,?,?,?,${k.map(() => "?").join(",")})`,
    t, nextRef(t, R.proposal, "proposals"), states.initial(M.proposal), by(actor), ...k.map(x => cols[x])));
  return proposal(t, N(r.lastInsertRowid));
}
function proposal(tid, id) {
  const p = proposalRow(tid, id);
  const nm = (table, col) => col ? (db().get(`SELECT name FROM ${table} WHERE id=?`, col) || {}).name : null;
  return { ...p, token: undefined, lines: linesOf(p), company: nm("crm_companies", p.company_id), contact: nm("crm_contacts", p.contact_id),
    deal: p.deal_id ? (db().get("SELECT ref, title, status FROM crm_deals WHERE id=?", p.deal_id) || null) : null, actions: proposalActions(p) };
}
const linkFor = (tid, p, base) => base ? base + encodeURIComponent(p.token) : require("./tell.js").address(N(tid), "proposal.html?t=" + p.token);
/* sent to the client with a private link (`link_base` + the token), emailed to `to` or the contact; the deal moves to the stage proposals are in */
async function sendProposal(tid, id, input, actor) {
  const p = proposalRow(tid, id), i = input || {};
  if (!tagged(M.proposal, p.status, "editable")) fail("Only a draft proposal is sent", 409);
  const validUntil = p.valid_until || addDays(today(), SEED.proposalValidDays);
  if (validUntil < today()) fail("Its valid-until date has passed: change it first", 409);
  const contact = p.contact_id ? db().get("SELECT email FROM crm_contacts WHERE id=?", p.contact_id) : null;
  const to = str(i.to || (contact && contact.email), 200).toLowerCase();
  if (to && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(to)) fail("That email does not look right");
  const token = crypto.randomBytes(24).toString("hex");
  move(M.proposal, "proposals", p, states.first(M.proposal, "awaiting"), { token, valid_until: validUntil, sent_to: to });
  const sent = proposalRow(tid, id), link = linkFor(tid, sent, i.link_base);
  if (sent.deal_id) {
    const d = db().get("SELECT status, stage FROM crm_deals WHERE id=?", sent.deal_id), C = require("./crm.js");
    if (d && tagged(M.deal, d.status, "open") && C.stages(tid).some(s => s.key === SEED.dealStageOnSend) && d.stage !== SEED.dealStageOnSend) C.updateDeal(tid, sent.deal_id, { stage: SEED.dealStageOnSend });
  }
  let emailed = false;
  if (to) {
    const store = (db().get("SELECT name FROM tenants WHERE id=?", N(tid)) || {}).name || "";
    const r = await require("./mailer.js").send({ tenantId: N(tid), channel: "email", to, subject: `Proposal from ${store}: ${sent.title}`,
      text: `${store} has sent you a proposal: ${sent.title}.\n\nTotal ${sent.total.toFixed(2)} ${sent.currency}, valid until ${sent.valid_until}.\n\nRead it and answer here: ${link}`, kind: R.proposal });
    emailed = !!(r && r.sent);
  }
  return { proposal: proposal(tid, id), link, emailed };
}
/* a sent proposal past its date is expired, and can no longer be answered */
function expireIfDue(p) {
  if (tagged(M.proposal, p.status, "awaiting") && p.valid_until && p.valid_until < today()) { move(M.proposal, "proposals", p, states.first(M.proposal, "expired")); return true; }
  return false;
}
const byToken = token => /^[a-f0-9]{48}$/.test(String(token || "")) ? db().get("SELECT * FROM proposals WHERE token=?", String(token)) : null;
/* what the client sees from their link */
function publicView(token) {
  let p = byToken(token); if (!p) return null;
  if (expireIfDue(p)) p = byToken(token);
  const store = (db().get("SELECT name FROM tenants WHERE id=?", p.tenant_id) || {}).name;
  const company = p.company_id ? (db().get("SELECT name FROM crm_companies WHERE id=?", p.company_id) || {}).name : null;
  return { store, ref: p.ref, title: p.title, intro: p.intro, company, currency: p.currency, billing: SEED.billing[p.billing].label, lines: linesOf(p).map(l => ({ ...l, kind: SEED.lineKinds[l.kind].label })),
    net: p.net, tax_pct: p.tax_pct, tax: p.tax, total: p.total, valid_until: p.valid_until, status: p.status, answerable: tagged(M.proposal, p.status, "awaiting"),
    accepted: tagged(M.proposal, p.status, "accepted"), answered_at: p.answered_at,
    endNote: (Object.entries(SEED.endNotes).find(([tag]) => tagged(M.proposal, p.status, tag)) || [])[1] || null };
}
/* accepted: the project starts — for the proposal's company, billed its way, its budget the proposal's value — and the deal is won */
function accept(p, who) {
  const t = p.tenant_id, lines = linesOf(p), O = require("./operations.js");
  const company = p.company_id ? db().get("SELECT name FROM crm_companies WHERE id=?", p.company_id) : null;
  const pr = O.upsertProject(t, { name: p.title, client: company ? company.name : "", budget: p.net, start_date: today(), status: states.first(M.project, "running") });
  const firstTime = lines.find(l => SEED.lineKinds[l.kind] && SEED.lineKinds[l.kind].hourly);
  O.setProjectFields(t, pr.id, { company_id: p.company_id, deal_id: p.deal_id, proposal_id: p.id, billing: p.billing, currency: p.currency, bill_rate: firstTime ? firstTime.rate : 0, tax_pct: p.tax_pct });
  move(M.proposal, "proposals", p, states.first(M.proposal, "accepted"), { answered_by: str(who, 120), project_id: pr.id });
  if (p.deal_id) {
    const d = db().get("SELECT status, currency FROM crm_deals WHERE id=?", p.deal_id), C = require("./crm.js");
    if (d && tagged(M.deal, d.status, "open")) { if (d.currency === p.currency) C.updateDeal(t, p.deal_id, { amount: p.net }); C.closeDeal(t, p.deal_id, true); }
  }
  return pr.id;
}
function decide(p, yes, who, reason) {
  if (!tagged(M.proposal, p.status, "awaiting")) fail(tagged(M.proposal, p.status, "answered") ? "This proposal has already been answered" : "This proposal is not open for an answer", 409);
  if (expireIfDue(p)) fail("This proposal expired on " + p.valid_until, 409, "expired");
  return tx(() => {
    if (yes) accept(p, who);
    else move(M.proposal, "proposals", p, states.first(M.proposal, "declined"), { answered_by: str(who, 120), decline_reason: str(reason, 500) });
    return db().get("SELECT * FROM proposals WHERE id=?", p.id);
  });
}
/* the client's answer from their link: { accept, name, reason? } — accepting needs their name */
function answerByClient(token, input) {
  const i = input || {}, p = byToken(token) || fail("This link is not valid", 404);
  const name = str(i.name, 120);
  if (i.accept && !name) fail("Type your name to accept");
  decide(p, !!i.accept, name ? "client: " + name : "client", i.reason);
  return publicView(token);
}
/* an answer the client gave another way (on a call, by email), recorded by staff */
function recordAnswer(tid, id, input, actor) {
  const i = input || {};
  decide(proposalRow(tid, id), !!i.accept, "staff: " + by(actor), i.reason);
  return proposal(tid, id);
}
function withdraw(tid, id) {
  const p = proposalRow(tid, id);
  if (!tagged(M.proposal, p.status, "editable") && !tagged(M.proposal, p.status, "awaiting")) fail("Only a draft or sent proposal is withdrawn", 409);
  move(M.proposal, "proposals", p, states.first(M.proposal, "withdrawn"));
  return proposal(tid, id);
}
/* a declined, expired or withdrawn proposal becomes a draft again; its old link stops working */
function redraft(tid, id) {
  const p = proposalRow(tid, id);
  if (!tagged(M.proposal, p.status, "closed")) fail("Only a declined, expired or withdrawn proposal is redrafted", 409);
  move(M.proposal, "proposals", p, states.first(M.proposal, "editable"), { token: null, valid_until: null, decline_reason: "" });
  return proposal(tid, id);
}
function proposals(tid, f) {
  const o = f || {};
  return db().all(`SELECT p.id, p.ref, p.title, p.currency, p.net, p.total, p.status, p.valid_until, p.sent_at, p.answered_at, p.deal_id, p.project_id, c.name company FROM proposals p LEFT JOIN crm_companies c ON c.id=p.company_id
     WHERE p.tenant_id=? AND (?='' OR p.status=?) AND (?=0 OR p.deal_id=?) ORDER BY p.id DESC LIMIT 300`, N(tid), str(o.status), str(o.status), N(o.deal_id) || 0, N(o.deal_id) || 0)
    .map(p => ({ ...p, actions: proposalActions(p) }));
}
/* sent proposals past their date, in every store, are marked expired */
function sweepAll() {
  const aw = states.tagged(M.proposal, "awaiting");
  let n = 0;
  for (const p of db().all(`SELECT * FROM proposals WHERE status IN ${ph(aw)} AND valid_until < ?`, ...aw, today())) { try { if (expireIfDue(p)) n++; } catch (e) { /* answered a moment ago */ } }
  return n;
}

/* ============================== the resource plan ============================== */
/* { employee_id, project_id, week, hours } — 0 hours takes the booking off */
function allocate(tid, input) {
  const i = input || {}, person = personRow(tid, i.employee_id), p = projectRow(tid, i.project_id), week = weekOf(i.week);
  if (i.week && week !== i.week) fail("A week is given by its Monday: " + week);
  const hours = r2(i.hours);
  if (!(hours >= 0 && hours <= 168)) fail("A week holds 0 to 168 hours");
  if (hours > 0 && !open(p)) fail(p.code + " is closed", 409);
  if (hours === 0) db().run("DELETE FROM resource_allocations WHERE tenant_id=? AND employee_id=? AND project_id=? AND week=?", N(tid), person.id, p.id, week);
  else db().run("INSERT INTO resource_allocations(tenant_id, employee_id, project_id, week, hours) VALUES(?,?,?,?,?) ON CONFLICT(tenant_id, employee_id, project_id, week) DO UPDATE SET hours=excluded.hours", N(tid), person.id, p.id, week, hours);
  const planned = r2(db().get("SELECT COALESCE(SUM(hours),0) h FROM resource_allocations WHERE tenant_id=? AND employee_id=? AND week=?", N(tid), person.id, week).h);
  const cap = r2(Math.max(0, capacityOf(person) - require("./leave.js").hoursOff(tid, person.id, week, addDays(week, 6), capacityOf(person))));
  return { employee_id: person.id, week, planned, capacity: cap, over: planned > cap };
}
/* who is booked on what, week by week, against their capacity: { from?, weeks? } */
function plan(tid, f) {
  const o = f || {}, start = weekOf(o.from), n = Math.min(Math.max(N(o.weeks) || SEED.planWeeks, 1), 26);
  const weeks = Array.from({ length: n }, (_, k) => addDays(start, k * 7)), end = weeks[weeks.length - 1];
  const rows = db().all(`SELECT a.employee_id, a.project_id, a.week, a.hours, p.code FROM resource_allocations a JOIN projects p ON p.id=a.project_id WHERE a.tenant_id=? AND a.week BETWEEN ? AND ?`, N(tid), start, end);
  /* approved leave comes off the week's capacity (lib/leave.js) */
  const L = require("./leave.js");
  return { weeks, people: people(tid).map(p => ({ id: p.id, name: p.name, capacity: p.capacity, weeks: weeks.map(w => {
      const items = rows.filter(r => r.employee_id === p.id && r.week === w).map(r => ({ project_id: r.project_id, code: r.code, hours: r.hours }));
      const planned = r2(items.reduce((a, x) => a + x.hours, 0)), away = L.hoursOff(tid, p.id, w, addDays(w, 6), p.capacity), cap = r2(Math.max(0, p.capacity - away));
      return { week: w, planned, items, away, capacity: cap, over: planned > cap, free: r2(Math.max(0, cap - planned)) };
    }) })),
    projects: db().all("SELECT id, code, name, status FROM projects WHERE tenant_id=? ORDER BY code", N(tid)).filter(open).map(p => ({ id: p.id, code: p.code, name: p.name })) };
}
/* each person's capacity over a span, set against what was planned, logged and billable: { from?, to? } */
function utilisation(tid, f) {
  const o = f || {}, to = o.to ? str(o.to, 10) : today(), from = o.from ? str(o.from, 10) : addDays(weekOf(to), -21);
  if (!isDate(from) || !isDate(to) || from > to) fail("Give a span from one day to a later one");
  const w0 = weekOf(from), w1 = weekOf(to), weeks = Math.round((Date.parse(w1) - Date.parse(w0)) / (7 * 86400e3)) + 1, lg = loggedSheets();
  const logged = db().all(`SELECT e.employee_id, SUM(e.hours) h, SUM(CASE WHEN e.billable=1 THEN e.hours ELSE 0 END) b FROM time_entries e JOIN timesheets s ON s.id=e.timesheet_id
     WHERE e.tenant_id=? AND s.status IN ${ph(lg)} AND e.date BETWEEN ? AND ? GROUP BY e.employee_id`, N(tid), ...lg, from, to);
  const planned = db().all("SELECT employee_id, SUM(hours) h FROM resource_allocations WHERE tenant_id=? AND week BETWEEN ? AND ? GROUP BY employee_id", N(tid), w0, w1);
  const pct = (a, b) => b > 0 ? +(a * 100 / b).toFixed(1) : 0;
  return { from, to, weeks, people: people(tid).map(p => {
    const l = logged.find(x => x.employee_id === p.id) || { h: 0, b: 0 }, pl = planned.find(x => x.employee_id === p.id) || { h: 0 };
    const away = require("./leave.js").hoursOff(tid, p.id, w0, addDays(w1, 6), p.capacity), cap = r2(Math.max(0, p.capacity * weeks - away));
    return { id: p.id, name: p.name, capacity: cap, away, planned: r2(pl.h), logged: r2(l.h), billable: r2(l.b), plannedPct: pct(pl.h, cap), loggedPct: pct(l.h, cap), utilisation: pct(l.b, cap) };
  }) };
}

/* ============================== the overview ============================== */
function overview(tid) {
  const t = N(tid);
  const count = (table, m, tag) => db().get(`SELECT COUNT(*) n FROM ${table} WHERE tenant_id=? AND status IN ${ph(states.tagged(m, tag))}`, t, ...states.tagged(m, tag)).n;
  return { actions: SEED.actions, projects: projects(t), waiting: { timesheets: count("timesheets", M.timesheet, "pending"), claims: count("expense_claims", M.expense, "pending"), proposals: count("proposals", M.proposal, "awaiting"), invoices: count("client_invoices", M.invoice, "editable") },
    receivables: receivables(t), people: people(t), billing: Object.entries(SEED.billing).map(([key, b]) => ({ key, label: b.label })), categories: SEED.expenseCategories, lineKinds: Object.entries(SEED.lineKinds).map(([key, l]) => ({ key, label: l.label })) };
}

module.exports = { weekOf, people, meOf, setPerson, project, projects, setProject, openSheet, sheet, saveEntries, submitSheet, approveSheet, rejectSheet, reopenSheet, sheets,
  saveClaim, claim, submitClaim, approveClaim, rejectClaim, reopenClaim, reimburse, claims, unbilled, draftInvoice, invoice, issueInvoice, payInvoice, voidInvoice, invoices, receivables,
  saveProposal, proposal, sendProposal, publicView, answerByClient, recordAnswer, withdraw, redraft, proposals, sweepAll, allocate, plan, utilisation, overview, SEED };
