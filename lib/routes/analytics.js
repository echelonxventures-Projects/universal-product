/* LUXORA Platform — analytics domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the analytics domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "analytics", routes(kit) {
  const { T, all, bad, dashboards, entity, get, json, logAction, ownsDashboard, planFor, requireAdmin, requireStaff, run, stIn } = kit;

  /* the entity vocabulary a widget may point at, so the console's picker is derived from
     the engine itself (native entities + every corpus universe) rather than maintained */
  function apiDashboardEntities(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    const ents = entity.allEntities(T(s));
    json(res, 200, { entities: Object.keys(ents).map(k => ({ key: k, label: ents[k].label || k, icon: ents[k].icon || "🧩",
      storage: ents[k].storage === "json" ? "json" : "table", platformOnly: !!ents[k].platformOnly,
      fields: (ents[k].fields || []).map(f => ({ key: f.key, label: f.label, type: f.type, col: f.col || f.key })) })),
      metrics: dashboards.METRICS, kinds: dashboards.KINDS, types: dashboards.DASHBOARD_TYPES });
  }
  function apiDashboards(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    json(res, 200, { dashboards: dashboards.list(T(s), { platform: !!s.platform_admin, includeInactive: !!s.platform_admin }) });
  }
  function apiDashboardRender(req, res, url, s, body, key) {
    if (!requireStaff(s, res)) return;
    /* audience is enforced inside render(): a platform-audience board metrics across
       tenants, so only a platform session may render it — by key as well as in the list */
    const out = dashboards.render(T(s), key, s.user_id || null, !!s.platform_admin);
    if (out.error) return bad(res, out.error, out.error.indexOf("unknown") === 0 ? 404 : 403);
    json(res, 200, out);
  }
  function apiDashboardSave(req, res, url, s, body, key) {
    if (!requireStaff(s, res)) return;
    const b = body || {};
    const row = { name: String(b.name || "Untitled dashboard").slice(0, 120), type: String(b.type || require("../defaults.js").of("dashboardTypes")).slice(0, 40),
      audience: ["admin", "platform", "all"].includes(b.audience) ? b.audience : "admin",
      description: String(b.description || "").slice(0, 500), active: b.active === false ? 0 : 1,
      position: Number(b.position) || 0 };
    if (key && /^\d+$/.test(key)) {
      /* S7: the UPDATE was scoped only by id, so a store admin could rename or
         deactivate another store's dashboard (or a platform template) by number.
         Ownership is exactly what the read path already enforces. */
      const own = get("SELECT tenant_id FROM dashboards WHERE id=?", Number(key));
      if (!own) return bad(res, "unknown dashboard " + key, 404);
      const isPlatformRow = own.tenant_id === null || own.tenant_id === undefined;
      if (!isPlatformRow ? Number(own.tenant_id) !== T(s) : !s.platform_admin)
        return bad(res, "That dashboard belongs to another store", 403);
      run("UPDATE dashboards SET name=?,type=?,audience=?,description=?,active=?,position=? WHERE id=?", row.name, row.type, row.audience, row.description, row.active, row.position, Number(key));
      logAction(s, "dashboard.update", "dashboard", key, row, req);
      json(res, 200, { ok: true, id: Number(key) });
    } else {
      const k = String(key || b.key || "dash-" + Date.now()).replace(/[^a-z0-9-]+/g, "-").slice(0, 60);
      const r = run("INSERT INTO dashboards(tenant_id,key,name,type,audience,description,active,position) VALUES(?,?,?,?,?,?,?,?)",
        s.platform_admin && b.audience === "platform" ? null : T(s), k, row.name, row.type, row.audience, row.description, row.active, row.position);
      logAction(s, "dashboard.create", "dashboard", k, row, req);
      json(res, 200, { ok: true, id: Number(r.lastInsertRowid), key: k });
    }
  }
  function apiDashboardDelete(req, res, url, s, body, key) {
    if (!requireStaff(s, res)) return;
    const d = dashboards.getDashboard(T(s), key);
    if (!d) return bad(res, "unknown dashboard " + key, 404);
    if (!ownsDashboard(s, d)) return bad(res, "That dashboard belongs to another store", 403);
    run("DELETE FROM dashboard_widgets WHERE dashboard_id=?", d.id);
    run("DELETE FROM dashboard_prefs WHERE dashboard_id=?", d.id);
    run("DELETE FROM dashboards WHERE id=?", d.id);
    logAction(s, "dashboard.delete", "dashboard", key, {}, req);
    json(res, 200, { ok: true });
  }
  /* a widget is added/edited as a row — the console never computes, only declares */
  function apiWidgetSave(req, res, url, s, body, key) {
    if (!requireStaff(s, res)) return;
    const b = body || {};
    const d = dashboards.getDashboard(T(s), key);
    if (!d) return bad(res, "unknown dashboard " + key, 404);
    if (!ownsDashboard(s, d)) return bad(res, "That dashboard belongs to another store", 403);
    const edef = entity.allEntities(T(s))[String(b.entity || "order")];
    if (edef && edef.storage !== "json" && edef.table && (edef.platformOnly || edef.noTenant) && !s.platform_admin) return bad(res, "That entity is platform-wide — only the platform console can chart it", 403);
    const row = { kind: dashboards.KINDS.includes(b.kind) ? b.kind : "kpi",
      label: String(b.label || "Widget").slice(0, 120), entity: String(b.entity || "order").slice(0, 80),
      metric: dashboards.METRICS.includes(b.metric) ? b.metric : "count",
      column: String(b.column || "").slice(0, 60), dimension: String(b.dimension || "").slice(0, 60),
      ord: b.ord === "asc" ? "asc" : "desc", lim: Math.min(200, Math.max(1, Number(b.lim) || 10)),
      filter: JSON.stringify(b.filter && typeof b.filter === "object" ? b.filter : {}),
      position: Number(b.position) || 0, span: Math.min(6, Math.max(1, Number(b.span) || 3)) };
    if (b.id) {
      run("UPDATE dashboard_widgets SET kind=?,label=?,entity=?,metric=?,\"column\"=?,dimension=?,ord=?,lim=?,filter=?,position=?,span=? WHERE id=? AND dashboard_id=?",
        row.kind, row.label, row.entity, row.metric, row.column || null, row.dimension || null, row.ord, row.lim, row.filter, row.position, row.span, Number(b.id), d.id);
      logAction(s, "dashboard.widget.update", "dashboard_widget", b.id, row, req);
      json(res, 200, { ok: true, id: Number(b.id) });
    } else {
      const r = run("INSERT INTO dashboard_widgets(dashboard_id,kind,label,entity,metric,\"column\",dimension,ord,lim,filter,position,span) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
        d.id, row.kind, row.label, row.entity, row.metric, row.column || null, row.dimension || null, row.ord, row.lim, row.filter, row.position, row.span);
      logAction(s, "dashboard.widget.add", "dashboard_widget", r.lastInsertRowid, row, req);
      json(res, 200, { ok: true, id: Number(r.lastInsertRowid) });
    }
  }
  function apiWidgetDelete(req, res, url, s, body, key) {
    if (!requireStaff(s, res)) return;
    const wid = Number(url.searchParams.get("widget_id"));
    if (!wid) return bad(res, "widget_id required", 400);
    const d = dashboards.getDashboard(T(s), key);
    if (!d) return bad(res, "unknown dashboard " + key, 404);
    if (!ownsDashboard(s, d)) return bad(res, "That dashboard belongs to another store", 403);
    run("DELETE FROM dashboard_widgets WHERE id=? AND dashboard_id=?", wid, d.id);
    run("DELETE FROM dashboard_prefs WHERE widget_id=?", wid);
    logAction(s, "dashboard.widget.delete", "dashboard_widget", wid, {}, req);
    json(res, 200, { ok: true });
  }
  /* §1439 Personalization: the operator's own view of a shared dashboard */
  function apiDashboardPref(req, res, url, s, body, key) {
    if (!requireStaff(s, res)) return;
    const d = dashboards.getDashboard(T(s), key);
    if (!d) return bad(res, "unknown dashboard " + key, 404);
    const b = body || {};
    dashboards.setPref(T(s), s.user_id || 0, d.id, Number(b.widget_id), { hidden: !!b.hidden, position: b.position });
    json(res, 200, { ok: true });
  }
  /* §395 Reporting Engine */
  function apiReports(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    dashboards.runDue(T(s));            /* opportunistic: scheduled reports run when read */
    json(res, 200, { reports: dashboards.reportsFor(T(s), !!s.platform_admin) });
  }
  function apiReportRun(req, res, url, s, body, key) {
    if (!requireStaff(s, res)) return;
    const out = dashboards.runReport(T(s), key);
    if (out.error) return bad(res, out.error, 400);
    logAction(s, "report.run", "report", key, { kind: out.report && out.report.kind }, req);
    json(res, 200, out);
  }
  function apiReportSave(req, res, url, s, body, key) {
    if (!requireStaff(s, res)) return;
    const b = body || {};
    /* a metric alias names a result column — a plain identifier only (it reaches SQL) */
    const badAlias = (Array.isArray(b.metrics) ? b.metrics : []).find(m => m && m.alias != null && m.alias !== "" && !dashboards.validAlias(m.alias));
    if (badAlias) return bad(res, "Metric alias must be a plain identifier (letters, digits, underscore): " + String(badAlias.alias).slice(0, 40), 400);
    const row = { name: String(b.name || "Untitled report").slice(0, 120), kind: String(b.kind || require("../defaults.js").of("dashboardTypes")).slice(0, 40),
      entity: String(b.entity || "order").slice(0, 80), metrics: JSON.stringify(Array.isArray(b.metrics) ? b.metrics : []),
      dimensions: JSON.stringify(Array.isArray(b.dimensions) ? b.dimensions : []), filter: JSON.stringify(b.filter && typeof b.filter === "object" ? b.filter : {}),
      schedule: ["manual", "daily", "weekly", "monthly"].includes(b.schedule) ? b.schedule : "manual",
      format: ["table", "csv", "json"].includes(b.format) ? b.format : "table", active: b.active === false ? 0 : 1 };
    if (key && /^\d+$/.test(key)) {
      /* S7: same cross-tenant write on reports — scope the UPDATE to a row the
         caller actually owns (a platform template row needs a platform admin) */
      const own = get("SELECT tenant_id FROM reports WHERE id=?", Number(key));
      if (!own) return bad(res, "unknown report " + key, 404);
      const isPlatformRow = own.tenant_id === null || own.tenant_id === undefined;
      if (!isPlatformRow ? Number(own.tenant_id) !== T(s) : !s.platform_admin)
        return bad(res, "That report belongs to another store", 403);
      run("UPDATE reports SET name=?,kind=?,entity=?,metrics=?,dimensions=?,filter=?,schedule=?,format=?,active=? WHERE id=?",
        row.name, row.kind, row.entity, row.metrics, row.dimensions, row.filter, row.schedule, row.format, row.active, Number(key));
      logAction(s, "report.update", "report", key, row, req);
      json(res, 200, { ok: true, id: Number(key) });
    } else {
      const k = String(key || b.key || "rep-" + Date.now()).replace(/[^a-z0-9-]+/g, "-").slice(0, 60);
      const r = run("INSERT INTO reports(tenant_id,key,name,kind,entity,metrics,dimensions,filter,schedule,format,active,position) VALUES(?,?,?,?,?,?,?,?,?,?,?,0)",
        s.platform_admin && b.audience === "platform" ? null : T(s), k, row.name, row.kind, row.entity, row.metrics, row.dimensions, row.filter, row.schedule, row.format, row.active);
      logAction(s, "report.create", "report", k, row, req);
      json(res, 200, { ok: true, id: Number(r.lastInsertRowid), key: k });
    }
  }
  function apiReportDelete(req, res, url, s, body, key) {
    if (!requireStaff(s, res)) return;
    const col = /^\d+$/.test(String(key)) ? "id" : "key";
    /* S7: the DELETE was unscoped — any store admin could remove another store's
       report (or a platform template) by id or key. Verify ownership first, the
       same way apiDashboardDelete does through getDashboard(). */
    const own = get("SELECT tenant_id FROM reports WHERE " + col + "=?", col === "id" ? Number(key) : String(key));
    if (!own) return bad(res, "unknown report " + key, 404);
    const isPlatformRow = own.tenant_id === null || own.tenant_id === undefined;
    if (!isPlatformRow ? Number(own.tenant_id) !== T(s) : !s.platform_admin)
      return bad(res, "That report belongs to another store", 403);
    run("DELETE FROM reports WHERE " + col + "=?", col === "id" ? Number(key) : String(key));
    logAction(s, "report.delete", "report", key, {}, req);
    json(res, 200, { ok: true });
  }
  /* ================= STORE ADMIN ================= */
  function apiAdminStats(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    const t = T(s);
    const revenue = get("SELECT COALESCE(SUM(total),0) t FROM orders WHERE tenant_id=?", t).t;
    const orders = get("SELECT COUNT(*) c FROM orders WHERE tenant_id=?", t).c;
    const op = stIn("order", "open");
    const pending = get("SELECT COUNT(*) c FROM orders WHERE tenant_id=? AND status IN " + op.sql, t, ...op.args).c;
    const customers = get("SELECT COUNT(*) c FROM users WHERE tenant_id=? AND role='customer'", t).c;
    const products = get("SELECT COUNT(*) c FROM products WHERE tenant_id=?", t).c;
    const lowStock = all("SELECT id,title,brand,stock FROM products WHERE tenant_id=? AND stock<=10 ORDER BY stock ASC LIMIT 8", t);
    const recent = all("SELECT id,num,name,total,status,created_at FROM orders WHERE tenant_id=? ORDER BY created_at DESC LIMIT 8", t);
    const daily = all("SELECT date(created_at) d, COALESCE(SUM(total),0) t FROM orders WHERE tenant_id=? AND created_at >= datetime('now','-13 days') GROUP BY date(created_at) ORDER BY d", t);
    const topDepts = all("SELECT p.dept, SUM(oi.qty*oi.price) rev FROM order_items oi JOIN orders o ON o.id=oi.order_id AND o.tenant_id=? JOIN products p ON p.tenant_id=o.tenant_id AND p.id=oi.product_id GROUP BY p.dept ORDER BY rev DESC LIMIT 6", t);
    const payments = all("SELECT gateway, COUNT(*) c, COALESCE(SUM(amount),0) amt, COALESCE(SUM(fee),0) fee FROM payments WHERE tenant_id=? GROUP BY gateway", t);
    json(res, 200, { revenue, orders, pending, customers, products, lowStock, recent, daily, topDepts, payments, plan: planFor(t) });
  }
  function apiAdminAnalytics(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    const t = T(s);
    const byDay = all("SELECT date(created_at) d, COUNT(*) orders, COALESCE(SUM(total),0) revenue FROM orders WHERE tenant_id=? AND created_at>=datetime('now','-30 days') GROUP BY d ORDER BY d", t);
    const topProducts = all("SELECT oi.product_id, p.title, p.emoji, SUM(oi.qty) units, SUM(oi.qty*oi.price) rev FROM order_items oi JOIN orders o ON o.id=oi.order_id AND o.tenant_id=? JOIN products p ON p.tenant_id=o.tenant_id AND p.id=oi.product_id GROUP BY oi.product_id, p.title, p.emoji ORDER BY rev DESC LIMIT 8", t);
    const byIndustry = all("SELECT tx.name industry, SUM(oi.qty*oi.price) rev FROM order_items oi JOIN orders o ON o.id=oi.order_id AND o.tenant_id=? JOIN products p ON p.tenant_id=o.tenant_id AND p.id=oi.product_id JOIN taxonomy tx ON tx.id=p.node_id GROUP BY tx.name ORDER BY rev DESC", t);
    const byType = all("SELECT type, COUNT(*) c FROM products WHERE tenant_id=? GROUP BY type", t);
    const invValue = get("SELECT COALESCE(SUM(i.qty*s.price),0) v FROM inventory i JOIN skus s ON s.id=i.sku_id AND s.tenant_id=i.tenant_id WHERE i.tenant_id=?", t).v;
    const funnel = { views: get("SELECT COUNT(*) c FROM view_history WHERE owner LIKE 't' || ? || ':%'", String(t)).c, carts: get("SELECT COUNT(DISTINCT owner) c FROM cart_items WHERE owner LIKE 't' || ? || ':%'", String(t)).c, orders: get("SELECT COUNT(*) c FROM orders WHERE tenant_id=?", t).c };
    json(res, 200, { byDay, topProducts, byIndustry, byType, invValue, funnel, lowStock: all("SELECT id,title,stock FROM products WHERE tenant_id=? AND stock<=10 ORDER BY stock LIMIT 10", t) });
  }

  return [
    ["GET /api/dashboards/entities", apiDashboardEntities],
    ["GET /api/dashboards", apiDashboards],
    ["GET /api/dashboards/:key", apiDashboardRender],
    ["POST /api/dashboards/:key", (r, re, u, s, b, p) => apiDashboardSave(r, re, u, s, b, p)],
    ["PUT /api/dashboards/:key", (r, re, u, s, b, p) => apiDashboardSave(r, re, u, s, b, p)],
    ["DELETE /api/dashboards/:key", apiDashboardDelete],
    ["POST /api/dashboards/:key/widgets", (r, re, u, s, b, p) => apiWidgetSave(r, re, u, s, b, p)],
    ["DELETE /api/dashboards/:key/widgets", apiWidgetDelete],
    ["POST /api/dashboards/:key/prefs", (r, re, u, s, b, p) => apiDashboardPref(r, re, u, s, b, p)],
    ["GET /api/reports", apiReports],
    ["GET /api/reports/:key/run", (r, re, u, s, b, p) => apiReportRun(r, re, u, s, b, p)],
    ["POST /api/reports/:key", (r, re, u, s, b, p) => apiReportSave(r, re, u, s, b, p)],
    ["PUT /api/reports/:key", (r, re, u, s, b, p) => apiReportSave(r, re, u, s, b, p)],
    ["DELETE /api/reports/:key", apiReportDelete],
    ["GET /api/admin/stats", apiAdminStats],
    ["GET /api/admin/analytics", apiAdminAnalytics]
  ];
} };
