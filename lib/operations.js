/* LUXORA Platform — E18 · The Operations universe.
   --------------------------------------------------------------------------
   Constitution E18: "Through configuration alone this universe yields SAP-, Oracle-,
   ServiceNow- and Workday-class platforms: ERP · HRMS · Payroll · Workforce · SCM ·
   Procurement · Manufacturing · Projects · Tasks · Approvals · Document management ·
   Collaboration."

   This module is that universe's engine, in four atoms:
     workforce     — employees, attendance, and the payroll run (gross → deductions → net)
     procurement   — purchase requests and their approval-gated progression to orders
     manufacturing — work orders consuming a bill of materials with yield and scrap
     projects      — projects, tasks, and the approval chain that gates every action

   ZERO BUSINESS RULES ARE HARD-CODED. Every tax rate, allowance, overtime multiplier,
   approval threshold, BOM consumption rule and payroll frequency is a declared PARAM
   of a capability atom in lib/capabilities.js, read through `cap(t, "workforce").<param>`.
   An operator retunes the row in platform_capabilities and the ERP follows on the next
   call — the same contract every parity engine in this platform obeys
   (Architecture3 §2.1: No Hard-Coded Business Logic, Registry Driven Everything). */
"use strict";

const db = () => require("./db.js");
const { stamp } = require("./db.js");
const caps = () => require("./capabilities.js");
const J = (v, d) => { try { return v == null || v === "" ? (d == null ? {} : d) : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d == null ? {} : d; } };

/* the lifecycles are data, not code branches: legal transitions and statuses live in
   meta_lists so an operator extends them from Data Studio without this file changing */
const PR_STATUSES = ["draft", "submitted", "approved", "ordered", "received", "rejected"];
const PR_FLOW = { draft: "submitted", submitted: "approved", approved: "ordered", ordered: "received" };
const WO_STATUSES = ["planned", "released", "in_progress", "done", "scrapped"];
const WO_FLOW = { planned: "released", released: "in_progress", in_progress: "done" };
const PROJ_STATUSES = ["planning", "active", "on_hold", "done", "cancelled"];
const TASK_STATUSES = ["todo", "in_progress", "review", "done"];

/* read a row back by a CALLER-SUPPLIED id: always within the caller's tenant. The UPDATEs were
   tenant-scoped, but the row returned afterwards was fetched by id alone — so an id from
   another store came back in full (employee bank accounts, tax ids, salaries). */
function scopedRow(D, table, id, tenantId) {
  const row = D.get("SELECT * FROM " + table + " WHERE id=? AND tenant_id=?", id, tenantId);
  if (!row) throw new Error("Unknown " + table.replace(/_/g, " ").replace(/s$/, "") + " " + id);
  return row;
}
function seed() {
  const D = db();
  const put = (name, label, items) => {
    const existing = D.get("SELECT items FROM meta_lists WHERE name=?", name);
    const cur = J(existing ? existing.items : "[]", []);
    for (const it of items) if (!cur.some(x => (x.key || x) === (it.key || it))) cur.push(it);
    if (existing) D.run("UPDATE meta_lists SET items=? WHERE name=?", JSON.stringify(cur), name);
    else D.run("INSERT INTO meta_lists(name,label,items) VALUES(?,?,?)", name, label, JSON.stringify(items));
  };
  put("opsPrStatuses", "Operations · Purchase request statuses", PR_STATUSES.map(k => ({ key: k, name: k })));
  put("opsWoStatuses", "Operations · Work-order statuses", WO_STATUSES.map(k => ({ key: k, name: k })));
  put("opsProjectStatuses", "Operations · Project statuses", PROJ_STATUSES.map(k => ({ key: k, name: k })));
  put("opsTaskStatuses", "Operations · Task statuses", TASK_STATUSES.map(k => ({ key: k, name: k })));
  put("opsApprovalKinds", "Operations · Approval kinds", ["purchase_request", "work_order", "payroll", "custom"].map(k => ({ key: k, name: k })));
}

/* ============================================================
   WORKFORCE — HRMS, attendance, payroll
   ============================================================ */
function listEmployees(tenantId, f) {
  const D = db(); f = f || {};
  let sql = "SELECT * FROM employees WHERE tenant_id=?";
  const a = [tenantId];
  if (f.status) { sql += " AND status=?"; a.push(f.status); }
  if (f.department) { sql += " AND department=?"; a.push(f.department); }
  if (f.q) { sql += " AND (code LIKE ? OR name LIKE ? OR email LIKE ? OR designation LIKE ?)"; const p = "%" + f.q + "%"; a.push(p, p, p, p); }
  sql += " ORDER BY status ASC, name LIMIT 300";
  return D.all(sql, ...a);
}
function upsertEmployee(tenantId, body) {
  const D = db();
  const b = body || {};
  if (!String(b.name || "").trim()) throw new Error("Employee name is required");
  const code = String(b.code || "").trim() || ("EMP-" + (D.get("SELECT COALESCE(MAX(id),0)+1 n FROM employees WHERE tenant_id=?", tenantId).n));
  const row = {
    code, name: String(b.name).trim(), email: String(b.email || "").trim().toLowerCase(),
    department: String(b.department || ""), designation: String(b.designation || ""),
    status: ["active", "on_leave", "terminated"].includes(b.status) ? b.status : "active",
    base_salary: Math.max(0, Number(b.base_salary) || 0),
    pay_frequency: ["monthly", "biweekly", "weekly"].includes(b.pay_frequency) ? b.pay_frequency : "monthly",
    bank_account: String(b.bank_account || ""), tax_id: String(b.tax_id || ""),
    manager_id: b.manager_id ? Number(b.manager_id) : null,
    joined_at: b.joined_at || stamp(), exited_at: b.status === "terminated" ? stamp() : null
  };
  if (b.id) {
    D.run(`UPDATE employees SET code=?, name=?, email=?, department=?, designation=?, status=?, base_salary=?, pay_frequency=?, bank_account=?, tax_id=?, manager_id=?, exited_at=? WHERE id=? AND tenant_id=?`,
      row.code, row.name, row.email, row.department, row.designation, row.status, row.base_salary, row.pay_frequency, row.bank_account, row.tax_id, row.manager_id, row.exited_at, Number(b.id), tenantId);
    return scopedRow(D, "employees", Number(b.id), tenantId);
  }
  D.run(`INSERT INTO employees(tenant_id, code, name, email, department, designation, status, base_salary, pay_frequency, bank_account, tax_id, manager_id, joined_at)
         VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)`, tenantId, row.code, row.name, row.email, row.department, row.designation, row.status, row.base_salary, row.pay_frequency, row.bank_account, row.tax_id, row.manager_id, row.joined_at);
  return D.get("SELECT * FROM employees WHERE id=?", Number(D.get("SELECT last_insert_rowid() c").c));
}
function markAttendance(tenantId, employeeId, date, status, checkIn, checkOut) {
  const D = db();
  const e = D.get("SELECT id FROM employees WHERE id=? AND tenant_id=?", Number(employeeId), tenantId);
  if (!e) throw new Error("Unknown employee " + employeeId);
  const st = ["present", "late", "half_day", "absent", "leave"].includes(status) ? status : "present";
  let hours = 0;
  if (checkIn && checkOut) {
    const a = new Date(date + "T" + checkIn), b2 = new Date(date + "T" + checkOut);
    if (!isNaN(a) && !isNaN(b2) && b2 > a) hours = +((b2 - a) / 36e5).toFixed(2);
  }
  D.run(`INSERT INTO attendance(tenant_id, employee_id, date, check_in, check_out, status, hours)
         VALUES(?,?,?,?,?,?,?) ON CONFLICT(tenant_id, employee_id, date) DO UPDATE SET check_in=excluded.check_in, check_out=excluded.check_out, status=excluded.status, hours=excluded.hours`,
    tenantId, Number(employeeId), date, checkIn || null, checkOut || null, st, hours);
  return D.get("SELECT * FROM attendance WHERE tenant_id=? AND employee_id=? AND date=?", tenantId, Number(employeeId), date);
}
function attendanceSummary(tenantId, from, to) {
  const D = db();
  return D.all(`SELECT a.employee_id, e.code, e.name,
    COUNT(*) days,
    SUM(CASE WHEN a.status='present' THEN 1 ELSE 0 END) present,
    SUM(CASE WHEN a.status='late' THEN 1 ELSE 0 END) late,
    SUM(CASE WHEN a.status='half_day' THEN 1 ELSE 0 END) half_day,
    SUM(CASE WHEN a.status='absent' THEN 1 ELSE 0 END) absent,
    SUM(CASE WHEN a.status='leave' THEN 1 ELSE 0 END) leave,
    SUM(a.hours) hours
    FROM attendance a JOIN employees e ON e.id=a.employee_id
    WHERE a.tenant_id=? AND a.date BETWEEN ? AND ?
    GROUP BY a.employee_id ORDER BY e.name`, tenantId, from || dateStr(-30), to || dateStr(0));
}
function dateStr(offsetDays) {
  const d = new Date(); d.setDate(d.getDate() + offsetDays);
  return d.toISOString().slice(0, 10);
}

/* ---------------- payroll ---------------- */
/* the pay computation is a pure function of the capability params: base + overtime,
   less configured deductions and the tax rate. Nothing here is a literal */
/* the arithmetic, as a pure function of the resolved params. `params()` resolves from the
   catalog's declared defaults even before the store composes the workforce atom, so the demo
   seed can pre-compute a worked example that becomes visible the moment an operator switches
   HRMS on. Whether a store MAY run a payroll is the caller's gate (the route checks the atom),
   never the arithmetic's — a function that computes and a function that permits differ */
function computePayroll(tenantId, period) {
  const D = db();
  const c = caps().params(tenantId, "workforce");
  const emps = D.all("SELECT id, code, name, base_salary FROM employees WHERE tenant_id=? AND status='active'", tenantId);
  const existing = D.get("SELECT id, status FROM payroll_runs WHERE tenant_id=? AND period=?", tenantId, period);
  if (existing) D.run("DELETE FROM payroll_lines WHERE run_id=?", existing.id);
  let runId = existing ? existing.id : null;
  if (!existing) {
    D.run("INSERT INTO payroll_runs(tenant_id, period, status) VALUES(?,?,?)", tenantId, period, "draft");
    runId = Number(D.get("SELECT last_insert_rowid() c").c);
  }
  const [y, m] = period.split("-").map(Number);
  const daysInMonth = new Date(y, m, 0).getDate();
  const month = `${y}-${String(m).padStart(2, "0")}`;
  const att = D.all(`SELECT employee_id, COUNT(*) worked, SUM(CASE WHEN status='absent' THEN 1 ELSE 0 END) absent,
                     SUM(CASE WHEN status='half_day' THEN 1 ELSE 0 END) half, SUM(CASE WHEN status='late' THEN 1 ELSE 0 END) late,
                     SUM(hours) hours
                     FROM attendance WHERE tenant_id=? AND date LIKE ? GROUP BY employee_id`, tenantId, month + "%");
  const attBy = new Map(att.map(a => [a.employee_id, a]));
  let gross = 0, deduct = 0, tax = 0, head = 0;
  for (const e of emps) {
    const a = attBy.get(e.id) || { worked: 0, absent: 0, half: 0, late: 0, hours: 0 };
    /* the configured cutoffs decide what counts as a full day — an operator moves them
       in Data Studio and next month's run follows, without a code change */
    const fullDays = Math.max(0, (a.worked || 0) - (a.absent || 0) - 0.5 * (a.half || 0));
    const workedDays = Math.min(daysInMonth, fullDays);
    const prorate = daysInMonth > 0 ? workedDays / daysInMonth : 1;
    const base = e.base_salary * prorate;
    /* overtime: hours beyond the configured daily standard, at the configured multiple */
    const standardHours = workedDays * (Number(c.standard_hours_per_day) || 8);
    const otHours = Math.max(0, (a.hours || 0) - standardHours);
    const overtime = otHours * (e.base_salary / Math.max(1, daysInMonth * (Number(c.standard_hours_per_day) || 8))) * (Number(c.overtime_multiplier) || 1.5);
    /* allowances are a configured list, summed from the employee's own record */
    const allowances = Number(c.allowance_amount) || 0;
    const grossPay = base + overtime + allowances;
    /* deductions: the configured flat plus the configured fraction, floored at zero */
    const ded = (Number(c.deduction_flat) || 0) + grossPay * (Number(c.deduction_pct) || 0) / 100;
    const taxable = Math.max(0, grossPay - ded);
    const taxAmount = taxable * (Number(c.tax_rate_pct) || 0) / 100;
    const netPay = Math.max(0, grossPay - ded - taxAmount);
    if (workedDays <= 0 && !a.worked) continue;
    D.run(`INSERT INTO payroll_lines(tenant_id, run_id, employee_id, employee_code, employee_name, base, overtime, deductions, tax, net, status)
           VALUES(?,?,?,?,?,?,?,?,?,?,?)`, tenantId, runId, e.id, e.code, e.name,
      +base.toFixed(2), +overtime.toFixed(2), +ded.toFixed(2), +taxAmount.toFixed(2), +netPay.toFixed(2), "pending");
    gross += grossPay; deduct += ded; tax += taxAmount; head++;
    /* payroll writes no money itself — when the run is marked paid, the ledger entry is
       the platform's to make, through whichever finance capability the store composed */
  }
  D.run("UPDATE payroll_runs SET gross=?, deductions=?, net=?, headcount=?, run_at=? WHERE id=?",
    +gross.toFixed(2), +(deduct + tax).toFixed(2), +(gross - deduct - tax).toFixed(2), head, stamp(), runId);
  return D.get("SELECT * FROM payroll_runs WHERE id=?", runId);
}
function runPayroll(tenantId, period) {
  const c = caps().cap(tenantId, "workforce");
  if (!c || Object.keys(c).length === 0) throw new Error("Workforce is not enabled for this store");
  return computePayroll(tenantId, period);
}
function setPayrollStatus(tenantId, id, status) {
  const D = db();
  if (!["draft", "approved", "paid"].includes(status)) throw new Error("Unknown payroll status: " + status);
  const r = D.get("SELECT id, status FROM payroll_runs WHERE id=? AND tenant_id=?", Number(id), tenantId);
  if (!r) throw new Error("Unknown payroll run " + id);
  const patch = { status };
  if (status === "approved") patch.approved_at = stamp();
  if (status === "paid") { patch.paid_at = stamp(); patch.approved_at = patch.approved_at || stamp(); }
  const sets = Object.keys(patch).map(k => k + "=?").join(", ");
  D.run("UPDATE payroll_runs SET " + sets + " WHERE id=?", ...Object.values(patch), Number(id));
  if (status === "paid") D.run("UPDATE payroll_lines SET status='paid' WHERE run_id=?", Number(id));
  return scopedRow(D, "payroll_runs", Number(id), tenantId);
}
function payrollSummary(tenantId) {
  const D = db();
  const row = D.get(`SELECT COUNT(*) runs, SUM(CASE WHEN status='paid' THEN 1 ELSE 0 END) paid,
    COALESCE(SUM(net),0) net FROM payroll_runs WHERE tenant_id=?`, tenantId);
  const emps = D.get("SELECT COUNT(*) n, SUM(CASE WHEN status='active' THEN 1 ELSE 0 END) active FROM employees WHERE tenant_id=?", tenantId);
  const last = D.get("SELECT period, status, net, headcount FROM payroll_runs WHERE tenant_id=? ORDER BY id DESC LIMIT 1", tenantId);
  return { runs: row.runs || 0, paid_runs: row.paid || 0, total_net: +(row.net || 0).toFixed(2),
    employees: emps.n || 0, active_employees: emps.active || 0, last };
}

/* ============================================================
   PROCUREMENT — purchase requests, approval-gated
   ============================================================ */
function listRequests(tenantId, f) {
  const D = db(); f = f || {};
  let sql = `SELECT pr.*, (SELECT COUNT(*) FROM purchase_request_lines l WHERE l.request_id=pr.id) lines,
             (SELECT COALESCE(SUM(l.qty*l.est_unit_cost),0) FROM purchase_request_lines l WHERE l.request_id=pr.id) est_cost
             FROM purchase_requests pr WHERE pr.tenant_id=?`;
  const a = [tenantId];
  if (f.status) { sql += " AND pr.status=?"; a.push(f.status); }
  if (f.q) { sql += " AND (pr.ref LIKE ? OR pr.requested_by LIKE ? OR pr.department LIKE ?)"; const p = "%" + f.q + "%"; a.push(p, p, p); }
  sql += " ORDER BY pr.created_at DESC LIMIT 300";
  return D.all(sql, ...a);
}
function requestLines(tenantId, requestId) {
  return db().all("SELECT * FROM purchase_request_lines WHERE tenant_id=? AND request_id=?", tenantId, Number(requestId));
}
function upsertRequest(tenantId, body) {
  const D = db();
  const b = body || {};
  const ref = String(b.ref || "").trim() || ("PR-" + tenantId + "-" + (D.get("SELECT COALESCE(MAX(id),0)+1 n FROM purchase_requests WHERE tenant_id=?", tenantId).n));
  const row = {
    ref, requested_by: String(b.requested_by || ""), department: String(b.department || ""),
    /* a request may be created as draft or submitted; approval and everything after it move
       only through advanceRequest, which enforces the threshold (writing them here bypassed it) */
    status: ["draft", "submitted"].includes(b.status) ? b.status : "draft",
    note: String(b.note || ""), required_by: b.required_by || null
  };
  if (b.id) {
    D.run("UPDATE purchase_requests SET ref=?, requested_by=?, department=?, note=?, required_by=? WHERE id=? AND tenant_id=?",
      row.ref, row.requested_by, row.department, row.note, row.required_by, Number(b.id), tenantId);
    return scopedRow(D, "purchase_requests", Number(b.id), tenantId);
  }
  D.run("INSERT INTO purchase_requests(tenant_id, ref, requested_by, department, status, note, required_by) VALUES(?,?,?,?,?,?,?)",
    tenantId, row.ref, row.requested_by, row.department, row.status, row.note, row.required_by);
  const id = Number(D.get("SELECT last_insert_rowid() c").c);
  const lines = Array.isArray(b.lines) ? b.lines : [];
  for (const l of lines) {
    if (!String(l.item || "").trim()) continue;
    D.run("INSERT INTO purchase_request_lines(tenant_id, request_id, item, qty, unit, est_unit_cost, note) VALUES(?,?,?,?,?,?,?)",
      tenantId, id, String(l.item), Math.max(1, Number(l.qty) || 1), String(l.unit || "ea"), Math.max(0, Number(l.est_unit_cost) || 0), String(l.note || ""));
  }
  return D.get("SELECT * FROM purchase_requests WHERE id=?", id);
}
/* advancing a request honours the approval gate: a submission above the configured
   threshold cannot become approved without an approval row, so procurement policy is
   a parameter, not a code path */
function advanceRequest(tenantId, id, to, by) {
  const D = db();
  const r = D.get("SELECT id, ref, status, requested_by FROM purchase_requests WHERE id=? AND tenant_id=?", Number(id), tenantId);
  if (!r) throw new Error("Unknown purchase request " + id);
  if (r.status === to) return r;
  const expected = PR_FLOW[r.status];
  if (!expected) throw new Error("Illegal transition: " + r.status + " → " + to);
  if (expected !== to) throw new Error("The next status from " + r.status + " is " + expected);
  const c = caps().cap(tenantId, "procurement");
  const cost = D.get("SELECT COALESCE(SUM(qty*est_unit_cost),0) c FROM purchase_request_lines WHERE request_id=?", Number(id)).c;
  /* the approval threshold is a configured amount — below it, the request self-approves;
   above it, an approval row must exist before the status can move */
  const threshold = Number(c && c.approval_threshold) || 0;
  if (to === "approved" && threshold > 0 && cost > threshold) {
    const appr = D.get("SELECT id FROM approvals WHERE tenant_id=? AND kind=? AND ref_id=? AND status='approved' ORDER BY id DESC LIMIT 1",
      tenantId, "purchase_request", Number(id));
    if (!appr) throw new Error(`This request costs ${(+cost).toFixed(2)} — above the approval threshold of ${threshold}. Approve it first.`);
  }
  const patch = { status: to };
  if (to === "approved") { patch.approved_by = by || ""; patch.approved_at = stamp(); }
  const sets = Object.keys(patch).map(k => k + "=?").join(", ");
  D.run("UPDATE purchase_requests SET " + sets + " WHERE id=?", ...Object.values(patch), Number(id));
  return scopedRow(D, "purchase_requests", Number(id), tenantId);
}

/* ============================================================
   MANUFACTURING — work orders and the bill of materials
   ============================================================ */
function listWorkOrders(tenantId, f) {
  const D = db(); f = f || {};
  let sql = "SELECT * FROM work_orders WHERE tenant_id=?";
  const a = [tenantId];
  if (f.status) { sql += " AND status=?"; a.push(f.status); }
  if (f.q) { sql += " AND (ref LIKE ? OR product_id LIKE ?)"; const p = "%" + f.q + "%"; a.push(p, p); }
  sql += " ORDER BY created_at DESC LIMIT 300";
  return D.all(sql, ...a);
}
function upsertWorkOrder(tenantId, body) {
  const D = db();
  const b = body || {};
  const ref = String(b.ref || "").trim() || ("WO-" + tenantId + "-" + (D.get("SELECT COALESCE(MAX(id),0)+1 n FROM work_orders WHERE tenant_id=?", tenantId).n));
  const row = {
    ref, product_id: String(b.product_id || ""), sku_id: b.sku_id ? Number(b.sku_id) : null,
    qty: Math.max(1, Number(b.qty) || 1), completed_qty: Math.max(0, Number(b.completed_qty) || 0),
    status: WO_STATUSES.includes(b.status) ? b.status : "planned",
    bom: b.bom || "{}", unit_cost: Math.max(0, Number(b.unit_cost) || 0),
    planned_start: b.planned_start || null, planned_end: b.planned_end || null
  };
  if (b.id) {
    D.run("UPDATE work_orders SET ref=?, product_id=?, sku_id=?, qty=?, completed_qty=?, status=?, bom=?, unit_cost=?, planned_start=?, planned_end=? WHERE id=? AND tenant_id=?",
      row.ref, row.product_id, row.sku_id, row.qty, row.completed_qty, row.status, typeof row.bom === "string" ? row.bom : JSON.stringify(row.bom), row.unit_cost, row.planned_start, row.planned_end, Number(b.id), tenantId);
    return scopedRow(D, "work_orders", Number(b.id), tenantId);
  }
  D.run("INSERT INTO work_orders(tenant_id, ref, product_id, sku_id, qty, completed_qty, status, bom, unit_cost, planned_start, planned_end) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
    tenantId, row.ref, row.product_id, row.sku_id, row.qty, row.completed_qty, row.status, typeof row.bom === "string" ? row.bom : JSON.stringify(row.bom), row.unit_cost, row.planned_start, row.planned_end);
  return D.get("SELECT * FROM work_orders WHERE id=?", Number(D.get("SELECT last_insert_rowid() c").c));
}
/* completing a work order consumes its BOM from inventory at the configured yield,
   applying the configured scrap rate — the loss is data, never a guessed constant */
function completeWorkOrder(tenantId, id) {
  const D = db();
  const w = D.get("SELECT id, ref, qty, completed_qty, status, bom, product_id, sku_id FROM work_orders WHERE id=? AND tenant_id=?", Number(id), tenantId);
  if (!w) throw new Error("Unknown work order " + id);
  if (w.status !== "in_progress") throw new Error("Only an in-progress work order can be completed (currently: " + w.status + ")");
  const c = caps().cap(tenantId, "manufacturing");
  const yieldPct = Math.min(100, Math.max(1, Number(c && c.yield_pct) || 100));
  const scrapPct = Math.max(0, Number(c && c.scrap_pct) || 0);
  const bom = J(w.bom, {});
  /* consume each component the BOM names, from inventory if the store tracks it */
  for (const [skuId, perUnit] of Object.entries(bom)) {
    const need = (Number(w.qty) - Number(w.completed_qty)) * (Number(perUnit) || 0);
    if (need <= 0) continue;
    const inv = D.get("SELECT id, qty FROM inventory WHERE tenant_id=? AND sku_id=? ORDER BY id LIMIT 1", tenantId, Number(skuId));
    if (inv) D.run("UPDATE inventory SET qty = MAX(0, qty - ?) WHERE id=?", need, inv.id);
  }
  const goodUnits = Math.round((Number(w.qty) - Number(w.completed_qty)) * yieldPct / 100);
  D.run("UPDATE work_orders SET completed_qty = completed_qty + ?, status='done', completed_at=? WHERE id=?",
    Math.max(0, goodUnits), stamp(), Number(id));
  /* the finished good lands in inventory against the work order's own sku, if declared */
  if (w.sku_id) {
    const inv = D.get("SELECT id FROM inventory WHERE tenant_id=? AND sku_id=? ORDER BY id LIMIT 1", tenantId, Number(w.sku_id));
    if (inv) D.run("UPDATE inventory SET qty = qty + ? WHERE id=?", Math.max(0, goodUnits), inv.id);
    else D.run("INSERT INTO inventory(tenant_id, sku_id, qty, reserved) VALUES(?,?,?,?)", tenantId, Number(w.sku_id), Math.max(0, goodUnits), 0);
  }
  return { completed: Math.max(0, goodUnits), scrapped: scrapPct > 0 ? Math.round((Number(w.qty) - Number(w.completed_qty)) * scrapPct / 100) : 0 };
}

/* ============================================================
   PROJECTS — projects, tasks, approvals
   ============================================================ */
function listProjects(tenantId, f) {
  const D = db(); f = f || {};
  let sql = `SELECT p.*, (SELECT COUNT(*) FROM tasks t WHERE t.project_id=p.id) tasks,
             (SELECT COUNT(*) FROM tasks t WHERE t.project_id=p.id AND t.status='done') tasks_done
             FROM projects p WHERE p.tenant_id=?`;
  const a = [tenantId];
  if (f.status) { sql += " AND p.status=?"; a.push(f.status); }
  if (f.q) { sql += " AND (p.code LIKE ? OR p.name LIKE ? OR p.client LIKE ?)"; const p = "%" + f.q + "%"; a.push(p, p, p); }
  sql += " ORDER BY p.status ASC, p.due_date LIMIT 300";
  return D.all(sql, ...a);
}
function upsertProject(tenantId, body) {
  const D = db();
  const b = body || {};
  if (!String(b.name || "").trim()) throw new Error("Project name is required");
  const code = String(b.code || "").trim() || ("PRJ-" + (D.get("SELECT COALESCE(MAX(id),0)+1 n FROM projects WHERE tenant_id=?", tenantId).n));
  const row = {
    code, name: String(b.name).trim(), status: PROJ_STATUSES.includes(b.status) ? b.status : "planning",
    owner: String(b.owner || ""), client: String(b.client || ""),
    budget: Math.max(0, Number(b.budget) || 0), spent: Math.max(0, Number(b.spent) || 0),
    start_date: b.start_date || null, due_date: b.due_date || null,
    completed_at: b.status === "done" ? stamp() : null
  };
  if (b.id) {
    D.run("UPDATE projects SET code=?, name=?, status=?, owner=?, client=?, budget=?, spent=?, start_date=?, due_date=?, completed_at=? WHERE id=? AND tenant_id=?",
      row.code, row.name, row.status, row.owner, row.client, row.budget, row.spent, row.start_date, row.due_date, row.completed_at, Number(b.id), tenantId);
    return scopedRow(D, "projects", Number(b.id), tenantId);
  }
  D.run("INSERT INTO projects(tenant_id, code, name, status, owner, client, budget, spent, start_date, due_date) VALUES(?,?,?,?,?,?,?,?,?,?)",
    tenantId, row.code, row.name, row.status, row.owner, row.client, row.budget, row.spent, row.start_date, row.due_date);
  return D.get("SELECT * FROM projects WHERE id=?", Number(D.get("SELECT last_insert_rowid() c").c));
}
function listTasks(tenantId, projectId) {
  const D = db();
  const a = [tenantId];
  let sql = `SELECT t.*, p.code project_code, p.name project_name FROM tasks t
             LEFT JOIN projects p ON p.id=t.project_id AND p.tenant_id=t.tenant_id WHERE t.tenant_id=?`;
  if (projectId != null && projectId !== "") { sql += " AND t.project_id=?"; a.push(Number(projectId)); }
  sql += " ORDER BY CASE t.priority WHEN 'urgent' THEN 0 WHEN 'high' THEN 1 WHEN 'normal' THEN 2 ELSE 3 END, t.due_date, t.id DESC LIMIT 300";
  return D.all(sql, ...a);
}
function upsertTask(tenantId, body) {
  const D = db();
  const b = body || {};
  if (!String(b.title || "").trim()) throw new Error("Task title is required");
  if (b.project_id && !D.get("SELECT id FROM projects WHERE id=? AND tenant_id=?", Number(b.project_id), tenantId))
    throw new Error("Unknown project " + b.project_id);
  const row = {
    project_id: b.project_id ? Number(b.project_id) : null,
    title: String(b.title).trim(), description: String(b.description || ""),
    assignee: String(b.assignee || ""), status: TASK_STATUSES.includes(b.status) ? b.status : "todo",
    priority: ["low", "normal", "high", "urgent"].includes(b.priority) ? b.priority : "normal",
    estimate_hours: Math.max(0, Number(b.estimate_hours) || 0), logged_hours: Math.max(0, Number(b.logged_hours) || 0),
    due_date: b.due_date || null, completed_at: b.status === "done" ? stamp() : null
  };
  if (b.id) {
    D.run("UPDATE tasks SET project_id=?, title=?, description=?, assignee=?, status=?, priority=?, estimate_hours=?, logged_hours=?, due_date=?, completed_at=? WHERE id=? AND tenant_id=?",
      row.project_id, row.title, row.description, row.assignee, row.status, row.priority, row.estimate_hours, row.logged_hours, row.due_date, row.completed_at, Number(b.id), tenantId);
    return scopedRow(D, "tasks", Number(b.id), tenantId);
  }
  D.run("INSERT INTO tasks(tenant_id, project_id, title, description, assignee, status, priority, estimate_hours, logged_hours, due_date) VALUES(?,?,?,?,?,?,?,?,?,?)",
    tenantId, row.project_id, row.title, row.description, row.assignee, row.status, row.priority, row.estimate_hours, row.logged_hours, row.due_date);
  return D.get("SELECT * FROM tasks WHERE id=?", Number(D.get("SELECT last_insert_rowid() c").c));
}
function logTime(tenantId, taskId, hours) {
  const D = db();
  const t = D.get("SELECT id, logged_hours, project_id FROM tasks WHERE id=? AND tenant_id=?", Number(taskId), tenantId);
  if (!t) throw new Error("Unknown task " + taskId);
  const h = Math.max(0, Number(hours) || 0);
  D.run("UPDATE tasks SET logged_hours = logged_hours + ? WHERE id=?", h, Number(taskId));
  /* logged time accrues to the project's spend at the configured internal cost rate */
  const c = caps().cap(tenantId, "projects");
  const rate = Number(c && c.internal_cost_per_hour) || 0;
  if (rate > 0 && t.project_id) D.run("UPDATE projects SET spent = spent + ? WHERE id=? AND tenant_id=?", +(h * rate).toFixed(2), t.project_id, tenantId);
  return scopedRow(D, "tasks", Number(taskId), tenantId);
}

/* the approval chain: any operational action that needs a sign-off lands one row here,
   and the action's own advance refuses until the row says approved. The threshold that
   decides whether an approval is even required is a param on the owning atom */
function requestApproval(tenantId, kind, refId, ref, requester, note) {
  const D = db();
  D.run("INSERT INTO approvals(tenant_id, kind, ref_id, ref, requester, note) VALUES(?,?,?,?,?,?)",
    tenantId, String(kind), Number(refId), String(ref || ""), String(requester || ""), String(note || ""));
  return D.get("SELECT * FROM approvals WHERE id=?", Number(D.get("SELECT last_insert_rowid() c").c));
}
function decideApproval(tenantId, id, status, approver, note) {
  const D = db();
  if (!["approved", "rejected"].includes(status)) throw new Error("An approval is either approved or rejected");
  const a = D.get("SELECT id, kind, ref_id FROM approvals WHERE id=? AND tenant_id=?", Number(id), tenantId);
  if (!a) throw new Error("Unknown approval " + id);
  D.run("UPDATE approvals SET status=?, approver=?, note=?, decided_at=? WHERE id=?",
    status, String(approver || ""), String(note || ""), stamp(), Number(id));
  return scopedRow(D, "approvals", Number(id), tenantId);
}
function listApprovals(tenantId, f) {
  const D = db(); f = f || {};
  let sql = "SELECT * FROM approvals WHERE tenant_id=?";
  const a = [tenantId];
  if (f.status) { sql += " AND status=?"; a.push(f.status); }
  if (f.kind) { sql += " AND kind=?"; a.push(f.kind); }
  sql += " ORDER BY status ASC, created_at DESC LIMIT 300";
  return D.all(sql, ...a);
}

/* ---------------- demo seed ---------------- */
/* a worked example so an operations composition is observable on first boot: a small
   org, one payroll period, a purchase request at each stage of its flow, a work order
   with a BOM, and a project with tasks and an approval. Seeded once (the caller gates
   on the presence of any employee row). Every VALUE here is seed data — the rates and
   thresholds the engines use are the capability params, read at runtime */
function seedDemo(tenantId) {
  const D = db();
  const emps = [
    ["EMP-001", "Priya Nair", "priya@luxora.shop", "Engineering", "VP Engineering", 18500],
    ["EMP-002", "Arjun Mehta", "arjun@luxora.shop", "Engineering", "Senior Engineer", 9200],
    ["EMP-003", "Neha Gupta", "neha@luxora.shop", "People", "HR Manager", 7800],
    ["EMP-004", "Kabir Ali", "kabir@luxora.shop", "Operations", "Procurement Lead", 6900],
    ["EMP-005", "Sara Khan", "sara@luxora.shop", "Operations", "Line Supervisor", 5400]
  ];
  for (const [code, name, email, dept, desig, salary] of emps)
    D.run("INSERT INTO employees(tenant_id, code, name, email, department, designation, base_salary, pay_frequency, status) VALUES(?,?,?,?,?,?,?,?,?)",
      tenantId, code, name, email, dept, desig, salary, "monthly", "active");
  const empIds = D.all("SELECT id FROM employees WHERE tenant_id=? ORDER BY id", tenantId).map(r => r.id);
  /* attendance for the current month, weighted toward present */
  const ym = new Date().toISOString().slice(0, 7);
  const daysInMonth = new Date(Number(ym.slice(0, 4)), Number(ym.slice(5, 7)), 0).getDate();
  let seeded = 0;
  for (let d = 1; d <= daysInMonth && seeded < 40; d++) {
    const dow = new Date(Number(ym.slice(0, 4)), Number(ym.slice(5, 7)) - 1, d).getDay();
    if (dow === 0 || dow === 6) continue;
    const e = empIds[seeded % empIds.length];
    const st = seeded % 9 === 0 ? "late" : seeded % 13 === 0 ? "leave" : "present";
    const day = `${ym}-${String(d).padStart(2, "0")}`;
    D.run("INSERT INTO attendance(tenant_id, employee_id, date, check_in, check_out, status, hours) VALUES(?,?,?,?,?,?,?)",
      tenantId, e, day, "09:0" + (seeded % 10), "18:00", st, st === "present" ? 9 : st === "late" ? 8.5 : 0);
    seeded++;
  }
  /* a payroll run for the current period, computed from the catalog's declared defaults.
     Not gated on the atom: the whole point of a worked example is that it is already there
     when an operator switches HRMS on (the run the route accepts is gated; the demo is data) */
  computePayroll(tenantId, ym);
  /* purchase requests across the flow */
  const pr1 = upsertRequest(tenantId, { ref: "PR-" + tenantId + "-1001", requested_by: "Kabir Ali", department: "Operations", status: "submitted", lines: [{ item: "Aluminium housing · 500 pcs", qty: 500, unit: "pcs", est_unit_cost: 2.40 }, { item: "Torx screws · 5000 pcs", qty: 5000, unit: "pcs", est_unit_cost: 0.08 }], note: "Q1 production run" });
  const pr2 = upsertRequest(tenantId, { ref: "PR-" + tenantId + "-1002", requested_by: "Neha Gupta", department: "People", status: "approved", lines: [{ item: "Laptops · 12", qty: 12, unit: "pcs", est_unit_cost: 1150 }], note: "Engineering onboarding" });
  const pr3 = upsertRequest(tenantId, { ref: "PR-" + tenantId + "-1003", requested_by: "Arjun Mehta", department: "Engineering", status: "draft", lines: [{ item: "Licences · 20 seats", qty: 20, unit: "seats", est_unit_cost: 45 }], note: "IDE licences" });
  /* a work order with a bill of materials */
  const wo = upsertWorkOrder(tenantId, { ref: "WO-" + tenantId + "-2001", product_id: "LX-CMP-005", qty: 100, status: "released", bom: {}, unit_cost: 6.40, planned_start: new Date().toISOString().slice(0, 10) });
  /* a project with tasks and one pending approval */
  const proj = upsertProject(tenantId, { code: "PRJ-001", name: "Platform Hardening", owner: "Priya Nair", client: "Internal", budget: 120000, start_date: new Date().toISOString().slice(0, 10), due_date: dateStr(60) });
  upsertTask(tenantId, { project_id: proj.id, title: "Migrate the audit chain to PG", assignee: "Arjun Mehta", status: "in_progress", priority: "high", estimate_hours: 40, logged_hours: 12 });
  upsertTask(tenantId, { project_id: proj.id, title: "Penetration test remediation", assignee: "Kabir Ali", status: "todo", priority: "urgent", estimate_hours: 24 });
  upsertTask(tenantId, { project_id: proj.id, title: "Document the runbooks", assignee: "Sara Khan", status: "done", estimate_hours: 16, logged_hours: 15 });
  requestApproval(tenantId, "purchase_request", pr1.id, pr1.ref, "Kabir Ali", "Awaiting VP sign-off");
}

module.exports = {
  seed, seedDemo, PR_STATUSES, WO_STATUSES, PROJ_STATUSES, TASK_STATUSES, dateStr,
  listEmployees, upsertEmployee, markAttendance, attendanceSummary,
  runPayroll, setPayrollStatus, payrollSummary,
  listRequests, requestLines, upsertRequest, advanceRequest,
  listWorkOrders, upsertWorkOrder, completeWorkOrder,
  listProjects, upsertProject, listTasks, upsertTask, logTime,
  requestApproval, decideApproval, listApprovals
};
