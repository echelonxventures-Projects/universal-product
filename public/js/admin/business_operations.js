/* LUXORA Platform — the business_operations domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

/* ========== E18 · the operations universe (ERP · HRMS · procurement · manufacturing · projects)
   The console renders only what lib/operations.js answered: every tax rate, overtime
   multiple, approval threshold, yield and cost rate is a capability param, not a
   literal in this file. */
async function vOpsHR() {
  const d = await api("/admin/operations", {});
  const st = (d.stats || {}).payroll || {};
  const chip = s => `<span class="a-chip">${esc(s)}</span>`;
  return `<div class="a-head"><h2>🧑‍💼 People &amp; Payroll</h2><p class="a-sub">Employees, attendance and the payroll run. Overtime, allowances, deductions and tax are the store's own <code>workforce</code> params — a run is recomputed from them, never from a hard-coded rate. Attendance statuses and payroll statuses are Data Studio lists (<code>opsTaskStatuses</code> shape: editable, not code).</p></div>
  <div class="a-cards">
    <div class="a-card"><h3>Headcount</h3>
      <div class="a-stats">${[["Employees", st.employees || 0], ["Active", st.active_employees || 0], ["Payroll runs", st.runs || 0], ["Paid", st.paid_runs || 0], ["Last net", (st.last ? (+st.last.net).toFixed(0) : "—")]].map(([k, v]) => `<div><b>${v}</b><span>${k}</span></div>`).join("")}</div>
      <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap"><button class="btn-yellow" data-act="ops-new-employee">＋ Add employee</button><button class="btn-white" data-act="ops-payroll-run">▶ Run this month's payroll</button></div></div>
    <div class="a-card"><h3>Payroll runs</h3>
      <div class="a-tablewrap"><table class="a-table"><thead><tr><th>period</th><th>headcount</th><th>gross</th><th>deductions</th><th>net</th><th>status</th><th></th></tr></thead>
      <tbody>${(d.payroll || []).map(p => `<tr><td><code>${esc(p.period)}</code></td><td>${p.headcount}</td><td>${(+p.gross).toFixed(2)}</td><td>${(+p.deductions).toFixed(2)}</td><td><b>${(+p.net).toFixed(2)}</b></td><td>${chip(p.status)}</td>
      <td>${smIs("payroll_run", p.status, "can:approve") || smIs("payroll_run", p.status, "can:pay") ? `<button class="btn-white sm" data-act="ops-payroll-status" data-id="${p.id}" data-to="${esc(smAction("payroll_run", smIs("payroll_run", p.status, "can:approve") ? "approve" : "pay"))}">${smIs("payroll_run", p.status, "can:approve") ? "Approve" : "Mark paid"}</button>` : ""}</td></tr>`).join("") || `<tr><td colspan="7">No payroll runs yet.</td></tr>`}</tbody></table></div></div>
  </div>
  <div class="a-card"><h3>Employees</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>code</th><th>name</th><th>department</th><th>designation</th><th>salary</th><th>state</th></tr></thead>
    <tbody>${(d.employees || []).map(e => `<tr><td><code>${esc(e.code)}</code></td><td>${esc(e.name)}${e.email ? `<div class="a-sub">${esc(e.email)}</div>` : ""}</td><td>${esc(e.department || "—")}</td><td>${esc(e.designation || "—")}</td><td>${(+e.base_salary).toFixed(0)}</td><td>${chip(e.status)}</td></tr>`).join("") || `<tr><td colspan="6">No employees yet — add one above.</td></tr>`}</tbody></table></div></div>`;
}
async function vOpsMfg() {
  const d = await api("/admin/operations", {});
  const chip = s => `<span class="a-chip">${esc(s)}</span>`;
  return `<div class="a-head"><h2>🏭 Manufacturing</h2><p class="a-sub">Work orders and their bills of materials. Completion consumes the BOM and posts the finished good at the configured <code>yield_pct</code> with the configured <code>scrap_pct</code> loss — the yields are params, never guesses. Statuses are the Data Studio list <code>opsWoStatuses</code>.</p></div>
  <div class="a-cards">
    <div class="a-card"><h3>Work orders</h3>
      <div class="a-stats">${[["Open", (d.stats || {}).manufacturing ? (d.stats.manufacturing.open || 0) : 0], ["Shown", (d.workOrders || []).length]].map(([k, v]) => `<div><b>${v}</b><span>${k}</span></div>`).join("")}</div>
      <div style="margin-top:10px"><button class="btn-yellow" data-act="ops-new-wo">＋ New work order</button></div></div>
  </div>
  <div class="a-card"><h3>Work orders</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>ref</th><th>product</th><th>qty</th><th>completed</th><th>unit cost</th><th>status</th><th></th></tr></thead>
    <tbody>${(d.workOrders || []).map(w => `<tr>
      <td><code>${esc(w.ref)}</code></td><td>${esc(w.product_id || "—")}</td><td>${w.qty}</td><td>${w.completed_qty}</td>
      <td>${(+w.unit_cost).toFixed(2)}</td><td>${chip(w.status)}</td>
      <td>${smIs("work_order", w.status, "completable") ? `<button class="btn-white sm" data-act="ops-wo-complete" data-id="${w.id}">Complete</button>` : ""}</td>
    </tr>`).join("") || `<tr><td colspan="7">No work orders yet.</td></tr>`}</tbody></table></div></div>`;
}
async function vOpsProj() {
  const d = await api("/admin/operations", {});
  const chip = s => `<span class="a-chip">${esc(s)}</span>`;
  const st = (d.stats || {}).projects || {};
  return `<div class="a-head"><h2>📐 Projects &amp; Approvals</h2><p class="a-sub">Projects, tasks and the approval chain. Logged hours accrue to a project's spend at the configured <code>internal_cost_per_hour</code> — the rate is a param, so the same timesheet costs what the store says it costs. Approval kinds are the Data Studio list <code>opsApprovalKinds</code>.</p></div>
  <div class="a-cards">
    <div class="a-card"><h3>Portfolio</h3>
      <div class="a-stats">${[["Active projects", st.active || 0], ["Projects", (d.projects || []).length], ["Tasks", (d.tasks || []).length], ["Pending approvals", (d.approvals || []).filter(a => a.status === "pending").length]].map(([k, v]) => `<div><b>${v}</b><span>${k}</span></div>`).join("")}</div>
      <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap"><button class="btn-yellow" data-act="ops-new-project">＋ New project</button><button class="btn-white" data-act="ops-new-task">＋ New task</button></div></div>
    <div class="a-card"><h3>Approvals</h3>
      <div class="a-tablewrap"><table class="a-table"><thead><tr><th>kind</th><th>ref</th><th>requester</th><th>approver</th><th>status</th><th></th></tr></thead>
      <tbody>${(d.approvals || []).map(a => `<tr><td>${chip(a.kind)}</td><td><code>${esc(a.ref || a.ref_id)}</code></td><td>${esc(a.requester || "—")}</td><td>${esc(a.approver || "—")}</td><td>${chip(a.status)}</td>
      <td>${a.status === "pending" ? `<button class="btn-white sm" data-act="ops-appr" data-id="${a.id}" data-to="approved">Approve</button> <button class="btn-white sm" data-act="ops-appr" data-id="${a.id}" data-to="rejected">Reject</button>` : ""}</td></tr>`).join("") || `<tr><td colspan="6">No approvals pending.</td></tr>`}</tbody></table></div></div>
  </div>
  <div class="a-card"><h3>Projects</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>code</th><th>name</th><th>owner</th><th>budget</th><th>spent</th><th>tasks</th><th>status</th></tr></thead>
    <tbody>${(d.projects || []).map(p => `<tr><td><code>${esc(p.code)}</code></td><td>${esc(p.name)}</td><td>${esc(p.owner || "—")}</td><td>${(+p.budget).toFixed(0)}</td><td>${(+p.spent).toFixed(0)}</td><td>${p.tasks_done}/${p.tasks}</td><td>${chip(p.status)}</td></tr>`).join("") || `<tr><td colspan="7">No projects yet.</td></tr>`}</tbody></table></div></div>
  <div class="a-card"><h3>Tasks</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>title</th><th>project</th><th>assignee</th><th>est</th><th>logged</th><th>due</th><th>priority</th><th>status</th><th></th></tr></thead>
    <tbody>${(d.tasks || []).map(t => `<tr><td>${esc(t.title)}</td><td>${esc(t.project_code || "—")}</td><td>${esc(t.assignee || "—")}</td><td>${t.estimate_hours}h</td><td>${t.logged_hours}h</td><td>${esc(t.due_date || "—")}</td><td>${chip(t.priority)}</td><td>${chip(t.status)}</td>
    <td>${t.status !== "done" ? `<button class="btn-white sm" data-act="ops-task-done" data-id="${t.id}">Done</button> <button class="btn-white sm" data-act="ops-task-time" data-id="${t.id}">Log time</button>` : ""}</td></tr>`).join("") || `<tr><td colspan="9">No tasks yet.</td></tr>`}</tbody></table></div></div>`;
}

screen("ops_hr", { render: async () => await vOpsHR() });
screen("ops_mfg", { render: async () => await vOpsMfg() });
screen("ops_proj", { render: async () => await vOpsProj() });
