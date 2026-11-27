/* Consultancy (lib/consulting.js): a project done for a company and billed its way; timesheets a
   week at a time, approved by someone else and priced at the person's rate; expense claims owed and
   paid back; invoices to clients drafted from approved, unbilled time and expenses — each billed
   once — or fixed-fee instalments, posted to the books; proposals from a deal answered from the
   client's own link, starting the project and winning the deal; the resource plan and utilisation. */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os");
const TMP = path.join(os.tmpdir(), "consulting-" + process.pid + ".db");
const wipe = () => { for (const s of ["", "-wal", "-shm"]) try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } };
wipe(); process.env.LX_DB = TMP;
const log = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = log;
const K = require("../lib/kernel.js"), CS = require("../lib/consulting.js"), RR = require("../lib/row-records.js"), O = require("../lib/operations.js");
const CRM = require("../lib/crm.js"), B = require("../lib/books.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + JSON.stringify(x).slice(0, 500) : ""))); };
const throws = (fn, re) => { try { fn(); return false; } catch (e) { return re.test(e.message) || (console.log("    (threw: " + e.message + ")"), false); } };
const rejects = async (fn, re) => { try { await fn(); return false; } catch (e) { return re.test(e.message) || (console.log("    (threw: " + e.message + ")"), false); } };
(async () => {
  try {
    const t = 1, cur = require("../lib/defaults.js").currency(t);
    const bal = code => { const tb = B.trialBalance(t).find(x => x.currency === cur); const r = tb && tb.rows.find(x => x.account === code); return r ? r.balance : 0; };
    const ana = O.upsertEmployee(t, { code: "C-ANA", name: "Ana Consultant", email: "ana@studio.example" });
    const ben = O.upsertEmployee(t, { code: "C-BEN", name: "Ben Lead", email: "ben@studio.example" });
    const acme = CRM.saveCompany(t, { name: "Acme Analytics" });

    console.log("▸ A PROJECT, DONE FOR A COMPANY AND BILLED ITS WAY");
    const pr = O.upsertProject(t, { name: "Data platform review", budget: 50000, status: "active" });
    ok(K.internal.nodeRow(pr.uid) && K.internal.nodeRow(pr.uid).kind === "operations.project", "a project is a record on the master", pr.uid);
    let p = CS.setProject(t, pr.id, { billing: "time_materials", company_id: acme.id, currency: cur, bill_rate: 100, tax_pct: 10, rates: [{ employee_id: ana.id, rate: 150 }] });
    ok(p.company === "Acme Analytics" && p.client === "Acme Analytics" && p.billingLabel === "Time and materials" && p.rates.length === 1 && RR.at("project", pr.id).belongsTo === acme.uid, "given its company, it moves under the company on the master, with its billing and its own rate for a person", { ...p, at: RR.at("project", pr.id) });
    const other = CRM.saveCompany(t, { name: "Other Ltd" });
    CS.setProject(t, pr.id, { company_id: other.id });
    const before = RR.at("project", pr.id).belongsTo;
    CS.setProject(t, pr.id, { company_id: acme.id });
    ok(before === other.uid && RR.at("project", pr.id).belongsTo === acme.uid && K.parents("operations.company_projects", pr.uid, { namespace: "platform" }).length === 1, "moved to another company and back: one company at a time, each move kept in time");
    ok(throws(() => CS.setProject(t, pr.id, { billing: "barter" }), /billed one of/), "only the declared billing models");
    CS.setPerson(t, ana.id, { bill_rate: 90, cost_rate: 40, capacity_hours: 35 });
    CS.setPerson(t, ben.id, { bill_rate: 120, cost_rate: 60 });
    const task = O.upsertTask(t, { project_id: pr.id, title: "Interview the data team", estimate_hours: 20 });
    const internal = O.upsertProject(t, { name: "Internal tooling", status: "active" });

    console.log("▸ A TIMESHEET A WEEK, APPROVED BY SOMEONE ELSE");
    const week = CS.weekOf("2026-11-18");
    ok(week === "2026-11-16", "a week starts on its Monday", week);
    let ts = CS.openSheet(t, { employee_id: ana.id, week: "2026-11-18" });
    ok(ts.week === "2026-11-16" && ts.status === "draft" && ts.days.length === 7 && CS.openSheet(t, { employee_id: ana.id, week: "2026-11-20" }).id === ts.id, "one timesheet per person and week, opened on any of its days", ts);
    ok(throws(() => CS.saveEntries(t, ts.id, [{ project_id: pr.id, date: "2026-11-23", hours: 2 }]), /day of the week/), "an entry is a day of its week");
    ok(throws(() => CS.saveEntries(t, ts.id, [{ project_id: pr.id, date: "2026-11-16", hours: 14 }, { project_id: internal.id, date: "2026-11-16", hours: 11 }]), /more than 24/), "a day holds at most 24 hours");
    ok(throws(() => CS.saveEntries(t, ts.id, [{ project_id: internal.id, date: "2026-11-16", hours: 2, billable: true }]), /not billed by the hour/), "time on a project that is not billed is not billable");
    ts = CS.saveEntries(t, ts.id, [{ project_id: pr.id, task_id: task.id, date: "2026-11-16", hours: 6, note: "kick-off" }, { project_id: pr.id, date: "2026-11-17", hours: 4 }, { project_id: internal.id, date: "2026-11-17", hours: 3 }]);
    ok(ts.hours === 13 && ts.billable_hours === 10 && ts.perDay[0] === 6 && ts.perDay[1] === 7, "entries total the week; time on a billed project is billable by default", ts);
    ok(throws(() => CS.approveSheet(t, ts.id, "ben@studio.example"), /Only a submitted/), "a draft is not approved");
    CS.submitSheet(t, ts.id, "ana@studio.example");
    ok(throws(() => CS.saveEntries(t, ts.id, []), /Only a draft/), "a submitted week is not changed");
    ok(throws(() => CS.approveSheet(t, ts.id, "ana@studio.example"), /Someone other/), "the person who submitted it does not approve it");
    const spentBefore = db.get("SELECT spent FROM projects WHERE id=?", pr.id).spent;
    ts = CS.approveSheet(t, ts.id, "ben@studio.example");
    const priced = db.all("SELECT * FROM time_entries WHERE timesheet_id=? ORDER BY id", ts.id);
    ok(ts.status === "approved" && ts.approved_at && priced[0].rate === 150 && priced[2].rate === 0 && priced.every(e => e.cost_rate === 40), "approved: billable hours priced at the person's rate on the project, all at their cost", priced);
    ok(db.get("SELECT logged_hours FROM tasks WHERE id=?", task.id).logged_hours === 6 && r(db.get("SELECT spent FROM projects WHERE id=?", pr.id).spent - spentBefore) === 400, "the task's logged hours and the project's spend go up");
    ok(RR.history("timesheet", ts.id, "status").map(h => h.value).join(">") === "draft>submitted>approved", "the week's history is on the master");
    ok(!db.all("SELECT attrs FROM k_versions WHERE node=?", ts.uid).some(v => /kick-off/.test(v.attrs)), "what was done each day stays in the tables");

    let tb = CS.openSheet(t, { employee_id: ben.id, week });
    CS.saveEntries(t, tb.id, [{ project_id: pr.id, date: "2026-11-18", hours: 5 }]);
    CS.submitSheet(t, tb.id, "ben@studio.example");
    ok(throws(() => CS.rejectSheet(t, tb.id, "ana@studio.example", ""), /Say what/), "sending a week back says why");
    tb = CS.rejectSheet(t, tb.id, "ana@studio.example", "Split the hours by task");
    tb = CS.reopenSheet(t, tb.id);
    ok(tb.status === "draft" && tb.actions.includes("submit"), "a week sent back is reopened, changed and submitted again");
    CS.saveEntries(t, tb.id, [{ project_id: pr.id, date: "2026-11-18", hours: 5 }]);
    CS.submitSheet(t, tb.id, "ben@studio.example");
    CS.approveSheet(t, tb.id, "ana@studio.example");

    console.log("▸ EXPENSE CLAIMS");
    ok(throws(() => CS.saveClaim(t, { employee_id: ana.id, project_id: internal.id, category: "travel", description: "Train", amount: 50, billable: true }), /billed to its client/), "an expense is billed on only from a project billed to its client");
    ok(throws(() => CS.saveClaim(t, { employee_id: ana.id, category: "bribes", description: "x", amount: 5 }), /one of/), "only the declared categories");
    let ex = CS.saveClaim(t, { employee_id: ana.id, project_id: pr.id, date: "2026-11-17", category: "travel", description: "Train to client site", amount: 80, billable: true, receipt_ref: "R-1" });
    ok(ex.ref.startsWith("EXP-") && ex.currency === cur && ex.status === "draft" && RR.at("expense_claim", ex.id).belongsTo === pr.uid, "a claim belongs to its project on the master", ex);
    CS.submitClaim(t, ex.id, "ana@studio.example");
    ok(throws(() => CS.approveClaim(t, ex.id, "ana@studio.example"), /Someone other/), "nobody approves their own claim");
    const owed0 = bal("2100");
    ex = CS.approveClaim(t, ex.id, "ben@studio.example");
    ok(bal("6500") === 80 && bal("2100") - owed0 === 80, "approved: an expense, owed to the person", { e: bal("6500"), o: bal("2100") });
    ex = CS.reimburse(t, ex.id);
    ok(ex.status === "reimbursed" && ex.paid_at && bal("2100") === owed0, "paid back: what was owed is cleared from the bank");
    const ex2 = CS.saveClaim(t, { employee_id: ben.id, project_id: pr.id, category: "meals", description: "Team lunch", amount: 30 });
    CS.submitClaim(t, ex2.id, "ben@studio.example");
    ok(CS.rejectClaim(t, ex2.id, "ana@studio.example", "Not billable and over the limit").status === "rejected", "a claim is sent back with a reason");

    console.log("▸ INVOICES TO CLIENTS, FROM APPROVED TIME AND EXPENSES");
    p = CS.project(t, pr.id);
    ok(p.unbilledHours === 15 && p.unbilledTime === 1500 + 500 && p.unbilledExpenses === 80, "what is ready to bill: approved billable time at its rates, and billable expenses", p);
    const u = CS.unbilled(t, pr.id, "2026-11-17");
    ok(u.time.length === 2 && u.expenses.length === 1, "up to a day: only what was done by then");
    let inv = CS.draftInvoice(t, { project_id: pr.id }, "ben@studio.example");
    ok(inv.ref.startsWith("CINV-") && inv.fees === 2000 && inv.expenses === 80 && inv.tax === 208 && inv.gross === 2288 && inv.lines.length === 3, "a draft: a line per person and rate, each expense, and the project's tax", inv);
    ok(RR.at("client_invoice", inv.id).belongsTo === pr.uid && inv.company.name === "Acme Analytics", "on the master under its project, billed to its company");
    ok(throws(() => CS.draftInvoice(t, { project_id: pr.id }), /Nothing on/), "time and expenses on an invoice are not billed twice");
    ok(throws(() => CS.draftInvoice(t, { project_id: internal.id }), /not billed/), "a project that is not billed has no invoices");
    inv = CS.voidInvoice(t, inv.id, "");
    ok(inv.status === "void" && CS.project(t, pr.id).unbilledHours === 15, "a voided draft gives its time and expenses back");
    inv = CS.draftInvoice(t, { project_id: pr.id, tax_pct: 0 });
    /* a second invoice claiming the same time at the same moment finds it taken */
    const one = db.get("SELECT id FROM time_entries WHERE invoice_id=? LIMIT 1", inv.id).id;
    db.run("UPDATE time_entries SET invoice_id=NULL WHERE id=?", one);
    const realRun = db.run; let raced = false;
    db.run = (sql, ...a) => { if (!raced && /UPDATE time_entries SET invoice_id=\? WHERE id IN/.test(sql)) { raced = true; realRun("UPDATE time_entries SET invoice_id=? WHERE id=?", inv.id, one); } return realRun(sql, ...a); };
    ok(throws(() => CS.draftInvoice(t, { project_id: pr.id }), /billed a moment ago/), "two drafts at once: the second finds the time taken, and nothing is written");
    db.run = realRun;
    db.run("UPDATE time_entries SET invoice_id=? WHERE id=?", inv.id, one); /* the other draft's claim, which the refused one's rollback took with it */
    ok(db.get("SELECT COUNT(*) n FROM client_invoices WHERE project_id=?", pr.id).n === 2, "the refused draft left no invoice behind");
    inv = await CS.issueInvoice(t, inv.id, { send_to: "ap@acme.example" });
    ok(inv.status === "issued" && inv.due_at && inv.sent_to === "ap@acme.example", "issued: due in the store's terms, sent to the client", inv);
    ok(bal("1100") === 2080 && bal("4300") === 2000 && bal("4310") === 80, "the books: the client owes the fees and the expenses billed on", { ar: bal("1100"), f: bal("4300"), x: bal("4310") });
    ok(CS.receivables(t).some(r => r.company === "Acme Analytics" && r.total === 2080), "what each client owes, by age");
    ok(throws(() => CS.voidInvoice(t, inv.id, ""), /Say why/), "an issued invoice is voided only with a reason");
    const bank0 = bal("1000");
    inv = CS.payInvoice(t, inv.id);
    ok(inv.status === "paid" && bal("1100") === 0 && bal("1000") - bank0 === 2080, "paid: the bank has it and the client owes nothing");
    ok(CS.project(t, pr.id).paid === 2080 && CS.project(t, pr.id).unbilledHours === 0, "the project shows it billed and paid");

    const fx = O.upsertProject(t, { name: "Fixed audit", budget: 10000, status: "active" });
    CS.setProject(t, fx.id, { billing: "fixed", company_id: acme.id });
    const i1 = CS.draftInvoice(t, { project_id: fx.id, fixed_amount: 4000, fixed_description: "Milestone 1: discovery" });
    ok(i1.fees === 4000 && i1.lines[0].kind === "fixed", "a fixed fee is billed in instalments");
    ok(throws(() => CS.draftInvoice(t, { project_id: fx.id, fixed_amount: 7000 }), /Only 6000/), "never more than the fee left to bill");
    await CS.issueInvoice(t, i1.id, {});
    const ar0 = bal("1100");
    CS.voidInvoice(t, i1.id, "Wrong milestone");
    ok(bal("1100") === ar0 - 4000 && CS.project(t, fx.id).fixedLeft === 10000, "voiding an issued invoice undoes its entry, and its instalment can be billed again");

    console.log("▸ PROPOSALS FROM A DEAL, ANSWERED FROM THE CLIENT'S LINK");
    const contact = CRM.saveContact(t, { name: "Mia Buyer", email: "mia@acme.example", company_id: acme.id });
    const deal = CRM.openDeal(t, { title: "Analytics retainer", contact_id: contact.id, amount: 30000 });
    let pp = CS.saveProposal(t, { deal_id: deal.id, intro: "Three months of analytics support.", tax_pct: 10, lines: [{ kind: "time", description: "Senior consultant", qty: 100, rate: 150 }, { kind: "fixed", description: "Set-up", rate: 2000 }] }, "ben@studio.example");
    ok(pp.title === "Analytics retainer" && pp.company === "Acme Analytics" && pp.contact === "Mia Buyer" && pp.net === 17000 && pp.total === 18700 && RR.at("proposal", pp.id).belongsTo === deal.uid, "drafted from a deal: its company, contact and title; priced; on the master under the deal", pp);
    ok(throws(() => CS.saveProposal(t, { title: "x", lines: [] }), /at least one line/), "a proposal has lines");
    const sent = await CS.sendProposal(t, pp.id, { link_base: "https://studio.example/proposal.html?t=" }, "ben@studio.example");
    const tok = db.get("SELECT token FROM proposals WHERE id=?", pp.id).token;
    ok(sent.proposal.status === "sent" && sent.link === "https://studio.example/proposal.html?t=" + tok && !("token" in JSON.parse(JSON.stringify(sent.proposal))) && sent.proposal.valid_until, "sent with a private link, valid for the store's days; the token is never listed", sent);
    ok(CRM.deal(t, deal.id).stage === "proposal", "the deal moves to the stage proposals are in");
    const v = CS.publicView(tok);
    ok(v.answerable && v.total === 18700 && v.lines.length === 2 && v.store && !("deal_id" in v), "the client's link shows the proposal and nothing else", v);
    ok(CS.publicView("0".repeat(48)) === null && CS.publicView("bad") === null, "a wrong link shows nothing");
    ok(throws(() => CS.answerByClient(tok, { accept: true, name: "" }), /Type your name/), "accepting needs the client's name");
    const done = CS.answerByClient(tok, { accept: true, name: "Mia Buyer" });
    const after = db.get("SELECT * FROM proposals WHERE id=?", pp.id), np = db.get("SELECT * FROM projects WHERE id=?", after.project_id);
    ok(done.accepted && after.answered_by === "client: Mia Buyer" && np && np.company_id === acme.id && np.billing === "time_materials" && np.budget === 17000 && np.bill_rate === 150 && np.tax_pct === 10 && np.deal_id === deal.id, "accepted: the project starts for the company, billed the proposal's way", np);
    ok(CRM.deal(t, deal.id).status === "won" && CRM.deal(t, deal.id).amount === 17000, "and the deal is won at the proposal's value");
    ok(throws(() => CS.answerByClient(tok, { accept: false }), /already been answered/), "a proposal is answered once");
    const p2 = CS.saveProposal(t, { title: "Phase two", company_id: acme.id, lines: [{ kind: "time", description: "Analyst", qty: 10, rate: 90 }] });
    await CS.sendProposal(t, p2.id, {});
    const tok2 = db.get("SELECT token FROM proposals WHERE id=?", p2.id).token;
    db.run("UPDATE proposals SET valid_until='2026-01-01' WHERE id=?", p2.id);
    ok(throws(() => CS.answerByClient(tok2, { accept: true, name: "Mia" }), /expired/) && CS.publicView(tok2).endNote === "This proposal has expired.", "a proposal past its date expires and cannot be accepted");
    ok(CS.redraft(t, p2.id).status === "draft" && CS.publicView(tok2) === null, "redrafted, its old link stops working");
    const p3 = CS.saveProposal(t, { title: "Training", company_id: acme.id, lines: [{ kind: "fixed", description: "Workshop", rate: 1200 }] });
    await CS.sendProposal(t, p3.id, {});
    ok(CS.recordAnswer(t, p3.id, { accept: false, reason: "No budget this year" }, "ben@studio.example").status === "declined", "staff record an answer given another way");

    console.log("▸ THE RESOURCE PLAN AND UTILISATION");
    CS.allocate(t, { employee_id: ana.id, project_id: pr.id, week, hours: 25 });
    const over = CS.allocate(t, { employee_id: ana.id, project_id: internal.id, week, hours: 15 });
    ok(over.planned === 40 && over.capacity === 35 && over.over, "booking past a person's capacity shows them over", over);
    ok(throws(() => CS.allocate(t, { employee_id: ana.id, project_id: pr.id, week: "2026-11-18", hours: 5 }), /by its Monday/), "a booking is for a week, given by its Monday");
    const pl = CS.plan(t, { from: week, weeks: 2 });
    const anaRow = pl.people.find(x => x.id === ana.id);
    ok(pl.weeks.length === 2 && anaRow.weeks[0].planned === 40 && anaRow.weeks[0].items.length === 2 && anaRow.weeks[1].planned === 0, "the plan: each person's weeks, what they are booked on", anaRow);
    CS.allocate(t, { employee_id: ana.id, project_id: internal.id, week, hours: 0 });
    const ut = CS.utilisation(t, { from: week, to: "2026-11-22" });
    const ua = ut.people.find(x => x.id === ana.id);
    ok(ut.weeks === 1 && ua.capacity === 35 && ua.planned === 25 && ua.logged === 13 && ua.billable === 10 && ua.utilisation === 28.6, "utilisation: billable hours against capacity, beside what was planned and logged", ua);

    console.log("▸ THE BOOKS STAY WHOLE");
    const h = B.health(t);
    ok(!h.missing.length && !h.unbalanced.length, "every invoice and claim that should post has posted, and every entry balances", h);
    const tbal = B.trialBalance(t).find(x => x.currency === cur);
    ok(tbal && Math.abs(tbal.debit - tbal.credit) < 1e-6, "the trial balance balances");
    ok(CS.sweepAll() === 0, "the sweep has nothing left to expire");
  } catch (e) { failed++; console.log("  ✗ threw: " + e.stack); }
  console.log(`\n${passed} passed, ${failed} failed`);
  wipe();
  process.exit(failed ? 1 : 0);
})();
function r(n) { return +Number(n).toFixed(2); }
