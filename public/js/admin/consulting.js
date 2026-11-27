/* LUXORA Platform — the consulting domain's store-console screen (lib/consulting.js; _registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope. Projects and how they are billed,
   timesheets a week at a time, approvals, expense claims, invoices to clients, proposals, the
   resource plan and utilisation — all from /api/admin/consulting. */
"use strict";

let csTab = "overview", csOpen = null, csSheet = null, csRows = [], csDefs = {};
const csAmt = (n, c) => { try { return new Intl.NumberFormat(undefined, { style: "currency", currency: c }).format(+n || 0); } catch (e) { return (+n || 0).toFixed(2) + " " + esc(c || ""); } };
/* each action's needs (a reason, a field, another route) come with the overview (lib/seed/consulting.json actions) */
const csActs = (kind, x) => (x.actions || []).filter(a => !(csDefs[a] || {}).hidden).map(a => `<button class="p-btn sm${(csDefs[a] || {}).primary ? " primary" : ""}" data-cs-act="${kind}:${x.id}:${a}">${esc(a)}</button>`).join(" ");
async function vConsulting() {
  const on = k => csTab === k ? " primary" : "";
  const head = `<div class="a-head"><h2>⏱️ Consulting</h2><p class="a-sub">Projects for your clients and how each is billed, timesheets a week at a time, expense claims, invoices billed by time, proposals, and who is booked on what.</p></div>
    <div style="display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap">
      <button class="p-btn sm${on("overview")}" data-cs-tab="overview">Projects</button><button class="p-btn sm${on("timesheets")}" data-cs-tab="timesheets">Timesheets</button>
      <button class="p-btn sm${on("approvals")}" data-cs-tab="approvals">Approvals</button><button class="p-btn sm${on("expenses")}" data-cs-tab="expenses">Expenses</button>
      <button class="p-btn sm${on("invoices")}" data-cs-tab="invoices">Invoices</button><button class="p-btn sm${on("proposals")}" data-cs-tab="proposals">Proposals</button>
      <button class="p-btn sm${on("plan")}" data-cs-tab="plan">Plan</button><button class="p-btn sm${on("utilisation")}" data-cs-tab="utilisation">Utilisation</button></div>`;
  const o = await api("/admin/consulting");
  window.__csProjects = o.projects; csDefs = o.actions || {};
  return head + await ({ overview: csProjects, projectView: csProject, timesheets: csTimesheets, approvals: csApprovals, expenses: csExpenses, invoices: csInvoices, invoiceView: csInvoice, proposals: csProposals, plan: csPlan, utilisation: csUtil }[csTab] || csProjects)(o);
}
const csPeople = o => o.people.map(p => `<option value="${p.id}">${esc(p.name)}</option>`).join("");
const csProjOpts = (o, filter) => o.projects.filter(p => p.open && (!filter || filter(p))).map(p => `<option value="${p.id}">${esc(p.code)} · ${esc(p.name)}</option>`).join("");
async function csProjects(o) {
  const w = o.waiting;
  return `<div class="a-card"><h3>Waiting</h3><p class="a-sub"><span class="a-chip">${w.timesheets} timesheets to approve</span> <span class="a-chip">${w.claims} expense claims to approve</span> <span class="a-chip">${w.invoices} draft invoices</span> <span class="a-chip">${w.proposals} proposals awaiting an answer</span></p></div>
    <div class="a-card"><h3>Projects</h3>${coTbl(["project", "client", "billing", "hours", "ready to bill", "invoiced", "paid", ""], o.projects, p => [`<code>${esc(p.code)}</code> ${esc(p.name)} ${coBadge(p.status)}`, esc(p.company || "—"), esc(p.billingLabel),
      `${p.hours} h`, p.billed ? csAmt(p.unbilledTime + p.unbilledExpenses, p.currency) : "—", csAmt(p.invoiced, p.currency), csAmt(p.paid, p.currency), `<button class="p-btn sm" data-cs-project="${p.id}">Open</button>`], "No projects yet. Add one under Business Operations → Projects, or win a proposal.")}</div>
    <div class="a-card"><h3>What clients owe</h3>${coTbl(["client", "current", "1–30 days late", "31–60", "over 60", "total"], o.receivables, r => [esc(r.company || "—"), csAmt(r.current, r.currency), csAmt(r.d1_30, r.currency), csAmt(r.d31_60, r.currency), csAmt(r.d60plus, r.currency), `<b>${csAmt(r.total, r.currency)}</b>`], "Nothing owed.")}</div>
    <div class="a-card"><h3>People and rates</h3>${coTbl(["person", "billed at", "costs", "hours a week", ""], o.people, p => [esc(p.name), `<input type="number" min="0" step="0.01" value="${p.bill_rate}" data-cs-pf="${p.id}:bill_rate" style="width:90px">`,
      `<input type="number" min="0" step="0.01" value="${p.cost_rate}" data-cs-pf="${p.id}:cost_rate" style="width:90px">`, `<input type="number" min="0" max="168" step="0.5" value="${p.capacity}" data-cs-pf="${p.id}:capacity_hours" style="width:80px">`,
      `<button class="p-btn sm" data-cs-person="${p.id}">Save</button>`], "No people yet. Add them under Business Operations → HR.")}</div>`;
}
async function csProject(o) {
  const [{ project: p, unbilled: u }, cos] = await Promise.all([api("/admin/consulting/projects/" + csOpen), api("/admin/crm/companies").catch(() => ({ companies: [] }))]);
  return `<div class="a-card"><h3><code>${esc(p.code)}</code> ${esc(p.name)} ${coBadge(p.status)}</h3><p class="a-sub">${esc(p.company || "No client yet")} · ${esc(p.billingLabel)} · ${p.hours} h logged · cost ${csAmt(p.cost, p.currency)} · expenses ${csAmt(p.expenses, p.currency)} · invoiced ${csAmt(p.invoiced, p.currency)} · paid ${csAmt(p.paid, p.currency)}</p></div>
    <div class="a-card"><h3>How it is billed</h3><div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end">
      <label><span>Billing</span><select id="csPB">${o.billing.map(b => `<option value="${b.key}"${b.key === p.billing ? " selected" : ""}>${esc(b.label)}</option>`).join("")}</select></label>
      <label><span>Client</span><select id="csPC"><option value="">—</option>${cos.companies.map(c => `<option value="${c.id}"${c.id === p.company_id ? " selected" : ""}>${esc(c.name)}</option>`).join("")}</select></label>
      <label><span>Currency</span><input id="csPCur" value="${esc(p.currency)}" maxlength="8" style="width:80px"></label><label><span>Rate an hour</span><input id="csPR" type="number" min="0" step="0.01" value="${p.bill_rate}" style="width:100px"></label>
      <label><span>Tax %</span><input id="csPT" type="number" min="0" max="100" step="0.01" value="${p.tax_pct}" style="width:80px"></label><label><span>Budget or fixed fee</span><input id="csPBu" type="number" min="0" step="0.01" value="${p.budget}" style="width:120px"></label>
      <button class="p-btn sm primary" id="csPGo">Save</button></div>
      <p class="a-sub">A person's rate on this project:</p><div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end"><label><span>Person</span><select id="csRP">${csPeople(o)}</select></label><label><span>Rate</span><input id="csRR" type="number" min="0" step="0.01" style="width:100px"></label><button class="p-btn sm" id="csRGo">Set rate</button></div>
      ${coTbl(["person", "rate", ""], p.rates, r => [esc(r.name), csAmt(r.rate, p.currency), `<button class="p-btn sm" data-cs-unrate="${r.employee_id}">Remove</button>`], "Everyone is billed at the project's rate, or their own.")}</div>
    ${p.billed ? `<div class="a-card"><h3>Ready to bill</h3><p class="a-sub">${u.time.length} time entries · ${p.unbilledHours} h · ${csAmt(p.unbilledTime, p.currency)}; ${u.expenses.length} expenses · ${csAmt(p.unbilledExpenses, p.currency)}${u.otherCurrency.length ? ` · ${u.otherCurrency.length} expenses in another currency are not billed here` : ""}${p.byInstalment ? ` · ${csAmt(p.fixedLeft, p.currency)} of the fixed fee left to bill` : ""}</p>
      <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end"><label><span>Up to</span><input id="csIT" type="date"></label>
      ${p.byInstalment ? `<label><span>Instalment</span><input id="csIF" type="number" min="0" step="0.01" style="width:120px"></label><label><span>For</span><input id="csIFD" maxlength="200" placeholder="Milestone 1"></label>` : ""}
      <button class="p-btn sm primary" id="csIGo">Draft an invoice</button></div></div>` : ""}`;
}
async function csTimesheets(o) {
  const r = await api("/admin/consulting/timesheets");
  let open = "";
  if (csSheet) {
    const t = csSheet, edit = t.actions.includes("save");
    const days = t.days.map((d, i) => `<option value="${d}">${["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][i]} ${d.slice(5)}</option>`).join("");
    const rows = csRows.map((e, i) => edit ? `<tr><td><select data-cs-row="${i}:project_id">${o.projects.filter(p => p.open).map(p => `<option value="${p.id}"${p.id === e.project_id ? " selected" : ""}>${esc(p.code)}</option>`).join("")}</select></td>
        <td><select data-cs-row="${i}:date">${t.days.map(d => `<option value="${d}"${d === e.date ? " selected" : ""}>${d.slice(5)}</option>`).join("")}</select></td>
        <td><input type="number" min="0" max="24" step="0.25" value="${e.hours}" data-cs-row="${i}:hours" style="width:70px"></td><td><input type="checkbox" data-cs-row="${i}:billable"${e.billable ? " checked" : ""}></td>
        <td><input value="${esc(e.note || "")}" maxlength="500" data-cs-row="${i}:note"></td><td><button class="p-btn sm" data-cs-drop="${i}">Remove</button></td></tr>`
      : `<tr><td>${esc(e.project_code)}</td><td>${esc(e.date)}</td><td>${e.hours}</td><td>${e.billable ? "yes" : "no"}</td><td>${esc(e.note || "")}</td><td></td></tr>`).join("");
    open = `<div class="a-card"><h3>${esc(t.person)} · week of ${esc(t.week)} ${coBadge(t.status)}</h3><p class="a-sub">${t.hours} h, ${t.billable_hours} billable · ${t.perDay.map((h, i) => `${["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][i]} ${h}`).join(" · ")}${t.rejected_reason ? ` · <b>Sent back:</b> ${esc(t.rejected_reason)}` : ""}</p>
      <div style="overflow-x:auto"><table class="a-tbl"><thead><tr><th>project</th><th>day</th><th>hours</th><th>billable</th><th>note</th><th></th></tr></thead><tbody>${rows || '<tr><td colspan="6" class="a-sub">No time yet.</td></tr>'}</tbody></table></div>
      ${edit ? `<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px;align-items:flex-end"><label><span>Project</span><select id="csNP">${csProjOpts(o)}</select></label><label><span>Day</span><select id="csND">${days}</select></label>
        <label><span>Hours</span><input id="csNH" type="number" min="0" max="24" step="0.25" style="width:70px"></label><button class="p-btn sm" id="csNGo">Add</button><button class="p-btn sm" id="csSave">Save the week</button></div>` : ""}
      <div style="margin-top:8px">${csActs("timesheets", t)}</div></div>`;
  }
  return `<div class="a-card"><h3>Open a week</h3><div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end"><label><span>Person</span><select id="csTP">${o.me ? `<option value="${o.me.id}">${esc(o.me.name)}</option>` : ""}${csPeople(o)}</select></label>
      <label><span>Any day of the week</span><input id="csTW" type="date"></label><button class="p-btn sm primary" id="csTGo">Open</button></div></div>${open}
    <div class="a-card"><h3>Timesheets</h3>${coTbl(["person", "week", "hours", "billable", "status", ""], r.timesheets, x => [esc(x.person), esc(x.week), x.hours, x.billable_hours, coBadge(x.status), `<button class="p-btn sm" data-cs-sheet="${x.id}">Open</button>`], "No timesheets yet.")}</div>`;
}
async function csApprovals() {
  const [s, c] = await Promise.all([api("/admin/consulting/timesheets?status=submitted"), api("/admin/consulting/expenses?status=submitted")]);
  return `<div class="a-card"><h3>Timesheets to approve</h3><p class="a-sub">Approve a week someone else submitted: its hours are priced at each person's rate and added to their projects.</p>${coTbl(["person", "week", "hours", "billable", "submitted by", ""], s.timesheets, x => [esc(x.person), esc(x.week), x.hours, x.billable_hours, esc(x.submitted_by || "—"), `<button class="p-btn sm" data-cs-sheet="${x.id}">Open</button> ${csActs("timesheets", x)}`], "Nothing to approve.")}</div>
    <div class="a-card"><h3>Expense claims to approve</h3>${coTbl(["claim", "person", "project", "what", "amount", ""], c.claims, x => [`<code>${esc(x.ref)}</code>`, esc(x.person), esc(x.project || "—"), esc(x.description), csAmt(x.amount, x.currency), csActs("expenses", x)], "Nothing to approve.")}</div>`;
}
async function csExpenses(o) {
  const r = await api("/admin/consulting/expenses");
  return `<div class="a-card"><h3>New expense claim</h3><div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end">
      <label><span>Person</span><select id="csEP">${o.me ? `<option value="${o.me.id}">${esc(o.me.name)}</option>` : ""}${csPeople(o)}</select></label><label><span>Project</span><select id="csEPr"><option value="">—</option>${csProjOpts(o)}</select></label>
      <label><span>Date</span><input id="csED" type="date"></label><label><span>Category</span><select id="csEC">${o.categories.map(c => `<option value="${c.key}">${esc(c.label)}</option>`).join("")}</select></label>
      <label><span>What it was</span><input id="csEW" maxlength="300"></label><label><span>Amount</span><input id="csEA" type="number" min="0" step="0.01" style="width:100px"></label><label><span>Currency</span><input id="csECur" maxlength="8" style="width:70px"></label>
      <label><span>Receipt no.</span><input id="csER" maxlength="200"></label><label><span>Bill to the client</span><input id="csEB" type="checkbox"></label><button class="p-btn sm primary" id="csEGo">Save as draft</button></div></div>
    <div class="a-card"><h3>Expense claims</h3>${coTbl(["claim", "person", "project", "what", "amount", "billed on", "status", ""], r.claims, x => [`<code>${esc(x.ref)}</code>`, esc(x.person), esc(x.project || "—"), esc(x.description) + (x.rejected_reason ? `<div class="a-sub">Sent back: ${esc(x.rejected_reason)}</div>` : ""), csAmt(x.amount, x.currency), x.billable ? (x.invoice_id ? "invoiced" : "yes") : "no", coBadge(x.status), csActs("expenses", x)], "No claims yet.")}</div>`;
}
async function csInvoices() {
  const r = await api("/admin/consulting/invoices");
  return `<div class="a-card"><h3>Invoices to clients</h3><p class="a-sub">Draft one from a project: open it under Projects.</p>${coTbl(["invoice", "client", "project", "total", "due", "status", ""], r.invoices, v => [`<code>${esc(v.ref)}</code>`, esc(v.company || "—"), esc(v.project), csAmt(v.gross, v.currency), esc(v.due_at || "—"), coBadge(v.status), `<button class="p-btn sm" data-cs-invoice="${v.id}">Open</button>`], "No invoices yet.")}</div>`;
}
async function csInvoice() {
  const { invoice: v } = await api("/admin/consulting/invoices/" + csOpen);
  return `<div class="a-card"><h3><code>${esc(v.ref)}</code> ${coBadge(v.status)}</h3><p class="a-sub">${esc(v.company ? v.company.name : "—")} · ${esc(v.project.code)} ${esc(v.project.name)}${v.due_at ? " · due " + esc(v.due_at) : ""}${v.sent_to ? " · sent to " + esc(v.sent_to) : ""}${v.void_reason ? " · voided: " + esc(v.void_reason) : ""}</p>
    ${coTbl(["", "line", "qty", "rate", "amount"], v.lines, l => [esc(l.kind), esc(l.description), l.qty, csAmt(l.rate, v.currency), csAmt(l.amount, v.currency)], "")}
    <p style="text-align:right">Fees ${csAmt(v.fees, v.currency)} · Expenses ${csAmt(v.expenses, v.currency)} · Tax (${v.tax_pct}%) ${csAmt(v.tax, v.currency)} · <b>Total ${csAmt(v.gross, v.currency)}</b></p>
    <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end">${v.actions.some(a => (csDefs[a] || {}).field) ? `<label><span>Email it to</span><input id="csF" type="email" maxlength="200"></label>` : ""}${csActs("invoices", v)}<button class="p-btn sm" id="csPrint">Print or save as PDF</button></div></div>`;
}
async function csProposals(o) {
  const [r, d] = await Promise.all([api("/admin/consulting/proposals"), api("/admin/crm/pipeline").catch(() => ({ stages: [] }))]);
  const deals = d.stages.flatMap(s => s.deals);
  return `<div class="a-card"><h3>New proposal</h3><div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end">
      <label><span>From deal</span><select id="csQD"><option value="">—</option>${deals.map(x => `<option value="${x.id}">${esc(x.ref)} · ${esc(x.title)}</option>`).join("")}</select></label>
      <label><span>Title</span><input id="csQT" maxlength="160" placeholder="The deal's title"></label><label><span>Billing</span><select id="csQB">${o.billing.filter(b => b.key !== "non_billable").map(b => `<option value="${b.key}">${esc(b.label)}</option>`).join("")}</select></label>
      <label><span>Tax %</span><input id="csQX" type="number" min="0" max="100" step="0.01" value="0" style="width:70px"></label><label><span>Valid until</span><input id="csQV" type="date"></label></div>
      <label style="display:block;margin-top:8px"><span>Introduction</span><textarea id="csQI" rows="3" maxlength="4000" style="width:100%"></textarea></label>
      <p class="a-sub">One line each: kind | what | quantity | rate — for example: time | Senior consultant | 40 | 150</p><textarea id="csQL" rows="4" style="width:100%" placeholder="time | Senior consultant | 40 | 150"></textarea>
      <button class="p-btn sm primary" id="csQGo" style="margin-top:8px">Save as draft</button></div>
    <div class="a-card"><h3>Proposals</h3>${coTbl(["proposal", "client", "total", "valid until", "status", ""], r.proposals, p => [`<code>${esc(p.ref)}</code> ${esc(p.title)}`, esc(p.company || "—"), csAmt(p.total, p.currency), esc(p.valid_until || "—"), coBadge(p.status), csActs("proposals", p)], "No proposals yet.")}</div>`;
}
async function csPlan(o) {
  const r = await api("/admin/consulting/plan");
  return `<div class="a-card"><h3>Book someone onto a project</h3><div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end"><label><span>Person</span><select id="csAP">${csPeople(o)}</select></label>
      <label><span>Project</span><select id="csAPr">${r.projects.map(p => `<option value="${p.id}">${esc(p.code)} · ${esc(p.name)}</option>`).join("")}</select></label><label><span>Week</span><select id="csAW">${r.weeks.map(w => `<option value="${w}">${w}</option>`).join("")}</select></label>
      <label><span>Hours</span><input id="csAH" type="number" min="0" max="168" step="0.5" style="width:80px"></label><button class="p-btn sm primary" id="csAGo">Book</button></div><p class="a-sub">Book 0 hours to take a booking off.</p></div>
    <div class="a-card"><h3>The plan</h3><div style="overflow-x:auto"><table class="a-tbl"><thead><tr><th>person</th>${r.weeks.map(w => `<th>${esc(w.slice(5))}</th>`).join("")}</tr></thead><tbody>
      ${r.people.map(p => `<tr><td>${esc(p.name)}<div class="a-sub">${p.capacity} h a week</div></td>${p.weeks.map(w => `<td${w.over ? ' style="background:rgba(220,38,38,.12)"' : ""}><b>${w.planned}</b>${w.over ? " ⚠" : ""}<div class="a-sub">${w.items.map(i => `${esc(i.code)} ${i.hours}`).join(" · ") || "free"}</div></td>`).join("")}</tr>`).join("") || `<tr><td class="a-sub">No people yet.</td></tr>`}</tbody></table></div></div>`;
}
async function csUtil() {
  const r = await api("/admin/consulting/utilisation");
  return `<div class="a-card"><h3>Utilisation · ${esc(r.from)} to ${esc(r.to)}</h3><p class="a-sub">Billable hours against each person's capacity over ${r.weeks} weeks, beside what was planned and logged.</p>
    ${coTbl(["person", "capacity", "planned", "logged", "billable", "utilisation"], r.people, p => [esc(p.name), `${p.capacity} h`, `${p.planned} h · ${p.plannedPct}%`, `${p.logged} h · ${p.loggedPct}%`, `${p.billable} h`, `<b>${p.utilisation}%</b>`], "No people yet.")}</div>`;
}
function wireConsulting() {
  const go = async (fn, msg) => { try { await fn(); if (msg) toast(msg); render(); } catch (e) { toast(e.message); } };
  const on = (sel, fn) => document.querySelectorAll(sel).forEach(fn);
  const v = id => { const e = $(id); return e ? e.value : ""; };
  on("[data-cs-tab]", b => b.onclick = () => { csTab = b.dataset.csTab; csOpen = null; render(); });
  on("[data-cs-project]", b => b.onclick = () => { csTab = "projectView"; csOpen = b.dataset.csProject; render(); });
  on("[data-cs-invoice]", b => b.onclick = () => { csTab = "invoiceView"; csOpen = b.dataset.csInvoice; render(); });
  const openSheet = async id => { const r = await api("/admin/consulting/timesheets/" + id); csSheet = r.timesheet; csRows = csSheet.entries.map(e => ({ ...e })); csTab = "timesheets"; };
  on("[data-cs-sheet]", b => b.onclick = () => go(() => openSheet(b.dataset.csSheet)));
  on("[data-cs-person]", b => b.onclick = () => { const id = b.dataset.csPerson, body = {};
    document.querySelectorAll(`[data-cs-pf^="${id}:"]`).forEach(i => { body[i.dataset.csPf.split(":")[1]] = i.value === "" ? null : Number(i.value); });
    go(() => api("/admin/consulting/people/" + id, "PUT", body), "Saved"); });
  on("[data-cs-act]", b => b.onclick = () => {
    const [kind, id, act] = b.dataset.csAct.split(":"), d = csDefs[act] || {}, body = { ...(d.body || {}) };
    if (d.ask) { const why = prompt(d.ask); if (why === null || (!why && !d.optional)) return; body.reason = why; }
    if (d.field) body[d.field] = v("#csF");
    go(async () => {
      const r = await api(`/admin/consulting/${kind}/${id}/${d.route || act}`, "POST", body);
      if (r.timesheet && csSheet && csSheet.id === r.timesheet.id) { csSheet = r.timesheet; csRows = csSheet.entries.map(e => ({ ...e })); }
      if (d.link && r.link) prompt("The client's link — copy it to send it yourself:", r.link);
    }, "Done");
  });
  const tg = $("#csTGo"); if (tg) tg.onclick = () => go(async () => { const r = await api("/admin/consulting/timesheets", "POST", { employee_id: Number(v("#csTP")), week: v("#csTW") || undefined }); await openSheet(r.timesheet.id); });
  on("[data-cs-row]", i => i.onchange = () => { const [n, k] = i.dataset.csRow.split(":"); csRows[n][k] = k === "billable" ? i.checked : k === "project_id" || k === "hours" ? Number(i.value) : i.value; });
  on("[data-cs-drop]", b => b.onclick = () => { csRows.splice(Number(b.dataset.csDrop), 1); render(); });
  const ng = $("#csNGo"); if (ng) ng.onclick = () => { const pid = Number(v("#csNP")), h = Number(v("#csNH")); if (!pid || !(h > 0)) return toast("Choose a project and the hours");
    const p = (window.__csProjects || []).find(x => x.id === pid); csRows.push({ project_id: pid, date: v("#csND"), hours: h, billable: p ? !!p.byHour : false, note: "" }); render(); };
  const sv = $("#csSave"); if (sv) sv.onclick = () => go(async () => { const r = await api("/admin/consulting/timesheets/" + csSheet.id, "PUT", { entries: csRows.map(e => ({ project_id: e.project_id, task_id: e.task_id || undefined, date: e.date, hours: e.hours, billable: !!e.billable, note: e.note })) }); csSheet = r.timesheet; csRows = csSheet.entries.map(e => ({ ...e })); }, "Saved");
  const eg = $("#csEGo"); if (eg) eg.onclick = () => go(() => api("/admin/consulting/expenses", "POST", { employee_id: Number(v("#csEP")), project_id: Number(v("#csEPr")) || undefined, date: v("#csED") || undefined, category: v("#csEC"), description: v("#csEW"), amount: Number(v("#csEA")), currency: v("#csECur") || undefined, receipt_ref: v("#csER"), billable: $("#csEB").checked }), "Saved as draft");
  const pg = $("#csPGo"); if (pg) pg.onclick = () => go(() => api("/admin/consulting/projects/" + csOpen, "PUT", { billing: v("#csPB"), company_id: Number(v("#csPC")) || null, currency: v("#csPCur"), bill_rate: Number(v("#csPR")), tax_pct: Number(v("#csPT")), budget: Number(v("#csPBu")) }), "Saved");
  const rg = $("#csRGo"); if (rg) rg.onclick = () => go(() => api("/admin/consulting/projects/" + csOpen, "PUT", { rates: [{ employee_id: Number(v("#csRP")), rate: Number(v("#csRR")) }] }), "Rate set");
  on("[data-cs-unrate]", b => b.onclick = () => go(() => api("/admin/consulting/projects/" + csOpen, "PUT", { rates: [{ employee_id: Number(b.dataset.csUnrate), rate: null }] }), "Removed"));
  const ig = $("#csIGo"); if (ig) ig.onclick = () => go(async () => { const f = $("#csIF"); const r = await api("/admin/consulting/invoices", "POST", { project_id: Number(csOpen), through: v("#csIT") || undefined, fixed_amount: f && f.value ? Number(f.value) : undefined, fixed_description: v("#csIFD") }); csTab = "invoiceView"; csOpen = r.invoice.id; }, "Invoice drafted");
  const pr = $("#csPrint"); if (pr) pr.onclick = () => window.print();
  const qg = $("#csQGo"); if (qg) qg.onclick = () => go(() => api("/admin/consulting/proposals", "POST", { deal_id: Number(v("#csQD")) || undefined, title: v("#csQT") || undefined, billing: v("#csQB"), tax_pct: Number(v("#csQX")), valid_until: v("#csQV") || undefined, intro: v("#csQI"),
    lines: v("#csQL").split("\n").map(l => l.split("|").map(x => x.trim())).filter(x => x[0]).map(([kind, description, qty, rate]) => ({ kind, description, qty: Number(qty) || 1, rate: Number(rate) })) }), "Saved as draft");
  const ag = $("#csAGo"); if (ag) ag.onclick = () => go(async () => { const r = await api("/admin/consulting/plan", "PUT", { employee_id: Number(v("#csAP")), project_id: Number(v("#csAPr")), week: v("#csAW"), hours: Number(v("#csAH")) }); if (r.booking.over) toast(`Booked past capacity: ${r.booking.planned} of ${r.booking.capacity} h`); }, "Booked");
}
screen("consulting", { render: async () => { const html = await vConsulting(); return html; }, wire: wireConsulting });
