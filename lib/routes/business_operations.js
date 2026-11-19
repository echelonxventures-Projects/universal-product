/* LUXORA Platform — business_operations domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the business_operations domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "business_operations", routes(kit) {
  const { T, all, bad, json, logAction, operations, opsOn, requireAdmin, run, stIs } = kit;

  function apiOpsGet(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    const q = k => url.searchParams.get(k) || "";
    const out = { stats: {}, employees: [], attendance: [], requests: [], workOrders: [], projects: [], tasks: [], approvals: [], payroll: [] };
    if (opsOn(s, "workforce")) {
      out.employees = operations.listEmployees(T(s), { status: q("estatus"), department: q("dept"), q: q("q") });
      out.attendance = operations.attendanceSummary(T(s), q("from"), q("to"));
      out.payroll = all("SELECT * FROM payroll_runs WHERE tenant_id=? ORDER BY id DESC LIMIT 24", T(s));
      out.stats.payroll = operations.payrollSummary(T(s));
    }
    if (opsOn(s, "procurement")) {
      out.requests = operations.listRequests(T(s), { status: q("prstatus"), q: q("q") });
      out.stats.procurement = { open: out.requests.filter(r => !stIs("purchase_request", r.status, "terminal")).length };
    }
    if (opsOn(s, "manufacturing")) {
      out.workOrders = operations.listWorkOrders(T(s), { status: q("wostatus"), q: q("q") });
      out.stats.manufacturing = { open: out.workOrders.filter(w => !["done", "scrapped"].includes(w.status)).length };
    }
    if (opsOn(s, "projects")) {
      out.projects = operations.listProjects(T(s), { status: q("pstatus"), q: q("q") });
      out.tasks = operations.listTasks(T(s), q("project_id"));
      out.approvals = operations.listApprovals(T(s), { status: q("astatus"), kind: q("akind") });
      out.stats.projects = { active: out.projects.filter(p => stIs("project", p.status, "running")).length };
    }
    json(res, 200, out);
  }
  function apiOpsEmployee(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    if (!opsOn(s, "workforce")) return bad(res, "HRMS & payroll is not enabled for this store", 403);
    try {
      const e = operations.upsertEmployee(T(s), body);
      logAction(s, "ops.employee.save", "employee", e.id, { code: e.code });
      json(res, 200, { employee: e });
    } catch (e2) { bad(res, e2.message, 400); }
  }
  function apiOpsAttendance(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    if (!opsOn(s, "workforce")) return bad(res, "HRMS & payroll is not enabled for this store", 403);
    try {
      const a = operations.markAttendance(T(s), body.employee_id, String(body.date || ""), String(body.status || "present"), body.check_in, body.check_out);
      json(res, 200, { attendance: a });
    } catch (e2) { bad(res, e2.message, 400); }
  }
  function apiOpsPayrollRun(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    if (!opsOn(s, "workforce")) return bad(res, "HRMS & payroll is not enabled for this store", 403);
    try {
      const period = String(body.period || new Date().toISOString().slice(0, 7));
      const r = operations.runPayroll(T(s), period);
      logAction(s, "ops.payroll.run", "payroll_run", r.id, { period: r.period, headcount: r.headcount });
      json(res, 200, { run: r });
    } catch (e2) { bad(res, e2.message, 400); }
  }
  function apiOpsPayrollStatus(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    if (!opsOn(s, "workforce")) return bad(res, "HRMS & payroll is not enabled for this store", 403);
    try {
      const r = operations.setPayrollStatus(T(s), id, String(body.status || ""));
      logAction(s, "ops.payroll.status", "payroll_run", id, { status: body.status });
      json(res, 200, { run: r });
    } catch (e2) { bad(res, e2.message, 400); }
  }
  function apiOpsRequest(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    if (!opsOn(s, "procurement")) return bad(res, "Procurement is not enabled for this store", 403);
    try {
      const r = operations.upsertRequest(T(s), body);
      logAction(s, "ops.pr.save", "purchase_request", r.id, { ref: r.ref });
      json(res, 200, { request: r });
    } catch (e2) { bad(res, e2.message, 400); }
  }
  function apiOpsRequestAdvance(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    if (!opsOn(s, "procurement")) return bad(res, "Procurement is not enabled for this store", 403);
    try {
      const r = operations.advanceRequest(T(s), id, String(body.status || ""), s.email || s.name || "console");
      logAction(s, "ops.pr.advance", "purchase_request", id, { status: body.status });
      json(res, 200, { request: r });
    } catch (e2) { bad(res, e2.message, 400); }
  }
  function apiOpsWorkOrder(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    if (!opsOn(s, "manufacturing")) return bad(res, "Manufacturing is not enabled for this store", 403);
    try {
      const w = operations.upsertWorkOrder(T(s), body);
      logAction(s, "ops.wo.save", "work_order", w.id, { ref: w.ref });
      json(res, 200, { workOrder: w });
    } catch (e2) { bad(res, e2.message, 400); }
  }
  function apiOpsWorkOrderComplete(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    if (!opsOn(s, "manufacturing")) return bad(res, "Manufacturing is not enabled for this store", 403);
    try {
      const r = operations.completeWorkOrder(T(s), id);
      logAction(s, "ops.wo.complete", "work_order", id, r);
      json(res, 200, r);
    } catch (e2) { bad(res, e2.message, 400); }
  }
  function apiOpsProject(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    if (!opsOn(s, "projects")) return bad(res, "Projects is not enabled for this store", 403);
    try {
      const p = operations.upsertProject(T(s), body);
      logAction(s, "ops.project.save", "project", p.id, { code: p.code });
      json(res, 200, { project: p });
    } catch (e2) { bad(res, e2.message, 400); }
  }
  function apiOpsTask(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    if (!opsOn(s, "projects")) return bad(res, "Projects is not enabled for this store", 403);
    try {
      const t = operations.upsertTask(T(s), body);
      logAction(s, "ops.task.save", "task", t.id, { title: t.title });
      json(res, 200, { task: t });
    } catch (e2) { bad(res, e2.message, 400); }
  }
  function apiOpsTime(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    if (!opsOn(s, "projects")) return bad(res, "Projects is not enabled for this store", 403);
    try {
      json(res, 200, { task: operations.logTime(T(s), id, body.hours) });
    } catch (e2) { bad(res, e2.message, 400); }
  }
  function apiOpsApprovalDecide(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    if (!opsOn(s, "projects")) return bad(res, "Projects is not enabled for this store", 403);
    try {
      const a = operations.decideApproval(T(s), id, String(body.status || ""), s.email || s.name || "console", body.note);
      logAction(s, "ops.approval.decide", "approval", id, { status: body.status });
      json(res, 200, { approval: a });
    } catch (e2) { bad(res, e2.message, 400); }
  }

  return [
    ["GET /api/admin/operations", apiOpsGet],
    ["POST /api/admin/ops/employees", apiOpsEmployee],
    ["POST /api/admin/ops/attendance", apiOpsAttendance],
    ["POST /api/admin/ops/payroll/run", apiOpsPayrollRun],
    ["PUT /api/admin/ops/payroll/:id", (r, re, u, s, b, p) => apiOpsPayrollStatus(r, re, u, s, b, p)],
    ["POST /api/admin/ops/requests", apiOpsRequest],
    ["PUT /api/admin/ops/requests/:id", (r, re, u, s, b, p) => apiOpsRequestAdvance(r, re, u, s, b, p)],
    ["POST /api/admin/ops/work-orders", apiOpsWorkOrder],
    ["POST /api/admin/ops/work-orders/:id/complete", (r, re, u, s, b, p) => apiOpsWorkOrderComplete(r, re, u, s, b, p)],
    ["POST /api/admin/ops/projects", apiOpsProject],
    ["POST /api/admin/ops/tasks", apiOpsTask],
    ["POST /api/admin/ops/tasks/:id/time", (r, re, u, s, b, p) => apiOpsTime(r, re, u, s, b, p)],
    ["PUT /api/admin/ops/approvals/:id", (r, re, u, s, b, p) => apiOpsApprovalDecide(r, re, u, s, b, p)]
  ];
} };
