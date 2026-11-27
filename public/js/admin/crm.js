/* LUXORA Platform — the CRM domain's store-console screen (lib/crm.js; _registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope. The pipeline board, companies
   and contacts, the agenda, the forecast, and one view of a customer — all from /api/admin/crm. */
"use strict";

let crmTab = "pipeline", crmOpen = null;
async function vCrm() {
  const on = k => crmTab === k ? " primary" : "";
  const head = `<div class="a-head"><h2>🤝 CRM</h2><p class="a-sub">Companies and the people there, deals through your pipeline, what was done and what is next — and one view of each customer.</p></div>
    <div style="display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap"><button class="p-btn sm${on("pipeline")}" data-crm-tab="pipeline">Pipeline</button><button class="p-btn sm${on("companies")}" data-crm-tab="companies">Companies</button>
      <button class="p-btn sm${on("contacts")}" data-crm-tab="contacts">Contacts</button><button class="p-btn sm${on("agenda")}" data-crm-tab="agenda">Agenda</button><button class="p-btn sm${on("forecast")}" data-crm-tab="forecast">Forecast</button></div>`;
  return head + (await ({ pipeline: crmPipeline, companies: crmCompanies, contacts: crmContacts, agenda: crmAgenda, forecast: crmForecast, person: crmPerson, company: crmCompany, deal: crmDealView }[crmTab] || crmPipeline)());
}
const crmKinds = ["call", "meeting", "email", "task", "note"];
function crmActivityForm(attr) {
  return `<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px" data-crm-actform ${attr}>
    <label><span>Kind</span><select data-f="kind">${crmKinds.map(k => `<option value="${k}">${esc(k)}</option>`).join("")}</select></label>
    <label><span>Subject</span><input data-f="subject" maxlength="200"></label><label><span>Notes</span><input data-f="body" maxlength="4000"></label>
    <label><span>Due</span><input data-f="due_at" type="date"></label><button class="p-btn sm" data-crm-act-add>Record</button></div>`;
}
function crmTimeline(list) {
  return coTbl(["", "what", "due", "done", ""], list, a => [esc(a.kind), esc(a.subject) + (a.body ? `<div class="a-sub">${esc(a.body)}</div>` : ""), esc(a.due_at || "—"), a.done_at ? esc(a.done_at) + (a.outcome ? ` · ${esc(a.outcome)}` : "") : "—",
    a.done_at ? "" : `<button class="p-btn sm" data-crm-act-done="${a.id}">Done</button>`], "Nothing recorded yet.");
}
async function crmPipeline() {
  const [b, cos] = await Promise.all([api("/admin/crm/pipeline"), api("/admin/crm/companies")]);
  const stageOpts = b.stages.map(s => `<option value="${esc(s.key)}">${esc(s.label)}</option>`).join("");
  const card = d => `<div class="a-card" style="margin:6px 0;padding:8px"><b>${esc(d.title)}</b><div class="a-sub">${esc(d.company || "—")} · ${money(d.amount)} ${esc(d.currency)} · ${esc(d.expected_close || "no date")}</div>
    <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:6px"><select data-crm-stage="${d.id}">${b.stages.map(s => `<option value="${esc(s.key)}"${s.key === d.stage ? " selected" : ""}>${esc(s.label)}</option>`).join("")}</select>
    <button class="p-btn sm primary" data-crm-won="${d.id}">Won</button><button class="p-btn sm" data-crm-lost="${d.id}">Lost</button><button class="p-btn sm" data-crm-deal="${d.id}" data-crm-view="deal">Open</button></div></div>`;
  return `<div class="a-card"><h3>New deal</h3><div style="display:flex;gap:8px;flex-wrap:wrap">
      <label><span>Title</span><input id="crmDT" maxlength="160"></label><label><span>Company</span><select id="crmDC"><option value="">—</option>${cos.companies.map(c => `<option value="${c.id}">${esc(c.name)}</option>`).join("")}</select></label>
      <label><span>Amount</span><input id="crmDA" type="number" step="0.01" min="0"></label><label><span>Stage</span><select id="crmDS">${stageOpts}</select></label>
      <label><span>Expected close</span><input id="crmDE" type="date"></label><button class="p-btn sm primary" id="crmDGo">Open deal</button></div></div>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px">${b.stages.map(s => `<div class="a-card"><h3>${esc(s.label)} · ${s.probability}%</h3>
      <p class="a-sub">${s.deals.length} · ${money(s.deals.reduce((x, d) => x + d.amount, 0))}</p>${s.deals.map(card).join("") || '<p class="a-sub">—</p>'}</div>`).join("")}</div>
    <div class="a-card"><h3>Won and lost</h3>${coTbl(["deal", "company", "amount", "closed", "", ""], b.won.concat(b.lost), d => [esc(d.title), esc(d.company || "—"), `${money(d.amount)} ${esc(d.currency)}`, esc(d.closed_at || ""), coBadge(d.status) + (d.lost_reason ? `<div class="a-sub">${esc(d.lost_reason)}</div>` : ""), `<button class="p-btn sm" data-crm-deal="${d.id}" data-crm-view="deal">Open</button>`], "Nothing closed yet.")}</div>`;
}
async function crmCompanies() {
  const r = await api("/admin/crm/companies");
  return `<div class="a-card"><h3>New company</h3><div style="display:flex;gap:8px;flex-wrap:wrap"><label><span>Name</span><input id="crmCN" maxlength="160"></label>
      <label><span>Website domain</span><input id="crmCD" maxlength="120"></label><label><span>Industry</span><input id="crmCI" maxlength="80"></label><label><span>Country</span><input id="crmCC" maxlength="2" style="width:60px"></label>
      <button class="p-btn sm primary" id="crmCGo">Add company</button></div></div>
    <div class="a-card"><h3>Companies</h3>${coTbl(["company", "domain", "industry", "contacts", "deals", ""], r.companies, c => [esc(c.name), esc(c.domain || "—"), esc(c.industry || "—"), c.contacts, c.deals, `<button class="p-btn sm" data-crm-company="${c.id}" data-crm-view="company">Open</button>`], "No companies yet.")}</div>`;
}
async function crmCompany() {
  const { company: c } = await api("/admin/crm/companies/" + crmOpen);
  return `<div class="a-card"><h3>${esc(c.name)}</h3><p class="a-sub">${esc([c.domain, c.industry, c.country].filter(Boolean).join(" · "))}</p></div>
    <div class="a-card"><h3>People</h3>${coTbl(["name", "title", "email", ""], c.contacts, x => [esc(x.name), esc(x.title || "—"), esc(x.email || "—"), x.user_id ? `<button class="p-btn sm" data-crm-person="${x.user_id}" data-crm-view="person">Customer view</button>` : ""], "No contacts yet.")}</div>
    <div class="a-card"><h3>Deals</h3>${coTbl(["deal", "amount", "stage", "", ""], c.deals, d => [esc(d.title), `${money(d.amount)} ${esc(d.currency)}`, esc(d.stage), coBadge(d.status), `<button class="p-btn sm" data-crm-deal="${d.id}" data-crm-view="deal">Open</button>`], "No deals yet.")}</div>
    <div class="a-card"><h3>Timeline</h3>${crmTimeline(c.activities)}${crmActivityForm(`data-company="${c.id}"`)}</div>`;
}
async function crmContacts() {
  const [r, cos] = await Promise.all([api("/admin/crm/contacts"), api("/admin/crm/companies")]);
  return `<div class="a-card"><h3>New contact</h3><div style="display:flex;gap:8px;flex-wrap:wrap"><label><span>Name</span><input id="crmPN" maxlength="120"></label>
      <label><span>Email</span><input id="crmPE" type="email" maxlength="200"></label><label><span>Phone</span><input id="crmPP" maxlength="40"></label><label><span>Job title</span><input id="crmPT" maxlength="120"></label>
      <label><span>Company</span><select id="crmPC"><option value="">—</option>${cos.companies.map(c => `<option value="${c.id}">${esc(c.name)}</option>`).join("")}</select></label>
      <button class="p-btn sm primary" id="crmPGo">Add contact</button></div></div>
    <div class="a-card"><h3>Contacts</h3>${coTbl(["name", "company", "title", "email", ""], r.contacts, x => [esc(x.name), esc(x.company || "—"), esc(x.title || "—"), esc(x.email || "—"), x.user_id ? `<button class="p-btn sm" data-crm-person="${x.user_id}" data-crm-view="person">Customer view</button>` : ""], "No contacts yet.")}</div>`;
}
async function crmAgenda() {
  const r = await api("/admin/crm/agenda");
  return `<div class="a-card"><h3>To do</h3>${coTbl(["", "what", "deal", "contact", "due", "who", ""], r.agenda, a => [esc(a.kind), esc(a.subject), esc(a.deal_ref || "—"), esc(a.contact || "—"), esc(a.due_at || "—"), esc(a.owner_staff || "—"), `<button class="p-btn sm" data-crm-act-done="${a.id}">Done</button>`], "Nothing to do.")}</div>`;
}
async function crmForecast() {
  const r = await api("/admin/crm/forecast");
  return `<div class="a-card"><h3>Forecast</h3>${coTbl(["month", "open deals", "pipeline", "weighted", "won"], r.forecast, f => [esc(f.month || "no date"), f.deals, `${money(f.pipeline)} ${esc(f.currency)}`, `${money(f.weighted)} ${esc(f.currency)}`, `${money(f.won)} ${esc(f.currency)}`], "No deals yet.")}</div>`;
}
async function crmDealView() {
  const { deal: d } = await api("/admin/crm/deals/" + crmOpen);
  return `<div class="a-card"><h3>${esc(d.ref)} · ${esc(d.title)} ${coBadge(d.status)}</h3><p class="a-sub">${esc(d.company || "—")} · ${esc(d.contact || "—")} · ${money(d.amount)} ${esc(d.currency)} · ${esc(d.stageLabel)} · ${d.probability}%</p>
    ${d.open ? "" : `<button class="p-btn sm" data-crm-reopen="${d.id}">Reopen</button>`}</div>
    <div class="a-card"><h3>Timeline</h3>${crmTimeline(d.activities)}${crmActivityForm(`data-deal="${d.id}"`)}</div>`;
}
async function crmPerson() {
  const p = await api("/admin/crm/people/" + crmOpen);
  return `<div class="a-card"><h3>${esc(p.person.name || p.person.email)}</h3><p class="a-sub">${esc(p.person.email)} · since ${esc(p.person.since)}</p>
      <p class="a-sub">${p.spent.map(x => `<span class="a-chip">${money(x.net)} ${esc(x.currency)} spent</span>`).join(" ")} ${p.segments.map(x => `<span class="a-chip">${esc(x)}</span>`).join(" ")} ${p.wallet.map(w => `<span class="a-chip">${esc(w.name)} ${money(w.balance)} ${esc(w.unit)}</span>`).join(" ")}</p></div>
    <div class="a-card"><h3>Orders</h3>${coTbl(["order", "status", "total", "placed"], p.orders, o => [esc(o.num), coBadge(o.status), `${money(o.total)} ${esc(o.currency || "")}`, esc(o.created_at)], "No orders.")}</div>
    <div class="a-card"><h3>Returns and support</h3>${coTbl(["", "ref", "status", "when"], p.returns.map(r => ({ ...r, what: "return" })).concat(p.cases.map(c => ({ ...c, what: "case" }))), x => [esc(x.what), esc(x.ref), coBadge(x.status), esc(x.created_at)], "None.")}</div>
    <div class="a-card"><h3>Deals</h3>${coTbl(["deal", "amount", "stage", ""], p.deals, d => [esc(d.title), `${money(d.amount)} ${esc(d.currency)}`, esc(d.stage), coBadge(d.status)], "No deals.")}</div>
    <div class="a-card"><h3>Activities</h3>${crmTimeline(p.activities)}</div>`;
}
function wireCrm() {
  const go = async (fn, msg) => { try { await fn(); if (msg) toast(msg); render(); } catch (e) { toast(e.message); } };
  const on = (sel, fn) => document.querySelectorAll(sel).forEach(fn);
  on("[data-crm-tab]", b => b.onclick = () => { crmTab = b.dataset.crmTab; crmOpen = null; render(); });
  on("[data-crm-company]", b => b.onclick = () => { crmTab = b.dataset.crmView; crmOpen = b.dataset.crmCompany; render(); });
  on("[data-crm-person]", b => b.onclick = () => { crmTab = b.dataset.crmView; crmOpen = b.dataset.crmPerson; render(); });
  on("[data-crm-deal]", b => b.onclick = () => { crmTab = b.dataset.crmView; crmOpen = b.dataset.crmDeal; render(); });
  on("[data-crm-stage]", s => s.onchange = () => go(() => api("/admin/crm/deals/" + s.dataset.crmStage, "PUT", { stage: s.value }), "Moved"));
  on("[data-crm-won]", b => b.onclick = () => go(() => api("/admin/crm/deals/" + b.dataset.crmWon + "/won", "POST", {}), "Won"));
  on("[data-crm-lost]", b => b.onclick = () => { const reason = prompt("Why was it lost?"); if (reason) go(() => api("/admin/crm/deals/" + b.dataset.crmLost + "/lost", "POST", { reason }), "Lost"); });
  on("[data-crm-reopen]", b => b.onclick = () => go(() => api("/admin/crm/deals/" + b.dataset.crmReopen + "/reopen", "POST", {}), "Reopened"));
  on("[data-crm-act-done]", b => b.onclick = () => go(() => api("/admin/crm/activities/" + b.dataset.crmActDone + "/done", "POST", { outcome: prompt("Outcome?") || "" }), "Done"));
  on("[data-crm-act-add]", b => b.onclick = () => { const f = b.closest("[data-crm-actform]"), v = k => f.querySelector(`[data-f="${k}"]`).value;
    go(() => api("/admin/crm/activities", "POST", { kind: v("kind"), subject: v("subject"), body: v("body"), due_at: v("due_at") || null, done: !v("due_at"), deal_id: f.dataset.deal ? Number(f.dataset.deal) : undefined, company_id: f.dataset.company ? Number(f.dataset.company) : undefined }), "Recorded"); });
  const dg = $("#crmDGo"); if (dg) dg.onclick = () => go(() => api("/admin/crm/deals", "POST", { title: $("#crmDT").value, company_id: Number($("#crmDC").value) || undefined, amount: Number($("#crmDA").value), stage: $("#crmDS").value, expected_close: $("#crmDE").value || null }), "Deal opened");
  const cg = $("#crmCGo"); if (cg) cg.onclick = () => go(() => api("/admin/crm/companies", "POST", { name: $("#crmCN").value, domain: $("#crmCD").value, industry: $("#crmCI").value, country: $("#crmCC").value }), "Company added");
  const pg = $("#crmPGo"); if (pg) pg.onclick = () => go(() => api("/admin/crm/contacts", "POST", { name: $("#crmPN").value, email: $("#crmPE").value, phone: $("#crmPP").value, title: $("#crmPT").value, company_id: Number($("#crmPC").value) || undefined }), "Contact added");
}
screen("crm", { render: async () => await vCrm(), wire: wireCrm });
