/* LUXORA · Universal Dashboard & Reporting Engine — Architecture1 §394 / §395.
   --------------------------------------------------------------------------
   The constitution does not ask for "some dashboards". It declares dashboards to be
   RUNTIME OBJECTS: Identity, Audience, Widgets, Metrics, Dimensions, Filters,
   Visualizations, Security, Personalization, Actions (§1439 Dashboard Meta Model) and
   types from Executive to Compliance (§394). §395 declares the reporting engine the
   same way: Data → Analytics → Visualization → Report.

   This module is the engine that makes those declarations true WITHOUT writing a
   dashboard. A dashboard is a row in `dashboards`; every widget on it is a row in
   `dashboard_widgets` that points at an ENTITY and declares a METRIC. The engine
   computes the metric from that entity's own data — it never knows what the widget is
   about. Add a KPI by inserting a row; an operator does it from the console. That is
   Configuration-Over-Code, and it is the only honest reading of §394.

   Two storage shapes are served by one aggregate function:
     · native entities (products, orders, …) → one SQL aggregate, parameterized
     · JSON entities (the corpus universes uv_*) → the same metric over decoded rows
   A widget looks identical either way, because the entity engine is the single lens.

   Security is §1439 "Security": a dashboard declares its audience; widgets compute only
   what the calling tenant may read. Personalization is §1439 "Personalization": each
   operator's widget order/visibility is a pref row, so one shared dashboard wears a
   different face per person — data, not code. */
"use strict";

let _db = null;
const db = () => _db || (_db = require("./db.js"));
const rows = (sql, ...p) => { try { return db().all(sql, ...p) || []; } catch (e) { return []; } };
const get = (sql, ...p) => { try { return db().get(sql, ...p) || null; } catch (e) { return null; } };
const run = (sql, ...p) => { try { return db().run(sql, ...p); } catch (e) { return { lastInsertRowid: 0 }; } };
const J = (v, d) => { try { const o = JSON.parse(v); return o == null ? d : o; } catch (e) { return d; } };

const METRICS = ["count", "sum", "avg", "min", "max", "distinct"];
const KINDS = ["kpi", "table", "bar", "line", "donut", "text"];
/* the dashboard/report vocabularies. Architecture1 §394 declares nine dashboard
   categories; the platform ships an extended set that also covers Strategic,
   Supplier, Customer, Security and Compliance. The extension is the platform's
   own declaration — it is NOT the corpus's, so the provenance below says so
   honestly (it previously claimed 'architecture1', which asserted a corpus
   authority the list does not have: a Law 002 lie that made the divergence from
   §394 invisible). Reconciling the platform's set with §394's nine is a corpus
   edit, now visible as a known divergence. */
const DASHBOARD_TYPES = ["Executive", "Operational", "Strategic", "Financial", "Marketplace",
  "Supplier", "Customer", "AI", "Security", "Compliance"];
/* §395 Reporting Engine: the report kinds the constitution names. */
const REPORT_KINDS = ["Scheduled", "Event", "Regulatory", "Operational", "Executive", "AI"];

/* ---------- the widget's declaration, cleaned and validated ----------
   Everything a widget can ask for is whitelisted here, so a crafted widget row can never
   smuggle arbitrary SQL into the aggregate. Column/dimension must exist on the entity's
   declared fields; metric/kind must be in the vocabularies above. */
const ALIAS_RE = /^[A-Za-z_][A-Za-z0-9_]{0,62}$/;
function validAlias(a) { return a == null || a === "" ? false : ALIAS_RE.test(String(a)); }
function resolveField(def, name) {
  if (!name) return null;
  const f = def.fields.find(x => x.key === name);
  if (!f) return null;
  return f.col || f.key;
}
function specOf(widget, def) {
  if (!def) return { error: "unknown entity " + widget.entity };
  const metric = METRICS.includes(widget.metric) ? widget.metric : "count";
  const kind = KINDS.includes(widget.kind) ? widget.kind : "kpi";
  const column = resolveField(def, widget.column);
  if (widget.column && !column) return { error: "unknown column " + widget.column };
  const dimension = resolveField(def, widget.dimension);
  if (widget.dimension && !dimension) return { error: "unknown dimension " + widget.dimension };
  if ((["sum", "avg", "min", "max", "distinct"].includes(metric)) && !column) return { error: metric + " needs a column" };
  /* a filter arrives as a JSON string from the DB or as an object from the API/tests;
     both must be normalized to an object before the whitelist check, otherwise a filter
     that failed to parse would be silently DROPPED — and a dropped filter is a filter
     that never got validated. */
  const rawFilter = widget.filter;
  const filter = !rawFilter ? {} : typeof rawFilter === "string" ? J(rawFilter, {}) : (typeof rawFilter === "object" ? rawFilter : {});
  if (Array.isArray(filter)) return { error: "filter must be an object of {field: value}" };
  const badKey = Object.keys(filter).find(k => !resolveField(def, k));
  if (badKey) return { error: "unknown filter field " + badKey };
  return { metric, kind, column, dimension, filter, def, entityKey: widget.entity,
    ord: String(widget.ord || "desc") === "asc" ? "asc" : "desc",
    lim: Math.min(200, Math.max(1, Number(widget.lim) || 10)) };
}

/* ---------- one aggregate, two storages ----------
   The result shape is deliberately uniform: { value } for a scalar, { buckets:
   [{key, value}] } for a breakdown. Every visualization is drawn from one of those two. */
function aggregate(tenantId, spec) {
  const { def } = spec;
  /* JSON entities (the corpus universes): the same metric, computed over decoded rows in
     memory. Universes are first-class entities, so a dashboard can KPI them too —
     "how many Insurance records are Canonical" is a widget, not a feature. */
  if (def.storage === "json") {
    let recs = rows("SELECT data FROM entity_data WHERE entity=?", def.table || spec.entityKey)      .map(r => J(r.data, {})).filter(r => r && typeof r === "object");
    recs = recs.filter(r => Object.entries(spec.filter).every(([k, v]) => String(r[k]) === String(v)));
    const val = (list, m, c) => {
      if (m === "count") return list.length;
      if (m === "distinct") return new Set(list.map(r => r[c])).size;
      const xs = list.map(r => Number(r[c])).filter(x => isFinite(x));
      if (!xs.length) return 0;
      if (m === "sum") return xs.reduce((a, b) => a + b, 0);
      if (m === "avg") return xs.reduce((a, b) => a + b, 0) / xs.length;
      if (m === "min") return Math.min(...xs);
      return Math.max(...xs);
    };
    if (!spec.dimension) return { value: val(recs, spec.metric, spec.column), n: recs.length };
    const groups = new Map();
    for (const r of recs) { const k = String(r[spec.dimension] == null || r[spec.dimension] === "" ? "—" : r[spec.dimension]);
      if (!groups.has(k)) groups.set(k, []); groups.get(k).push(r); }
    let buckets = [...groups.entries()].map(([key, list]) => ({ key, value: val(list, spec.metric, spec.column) }));
    buckets.sort((a, b) => spec.ord === "asc" ? a.value - b.value : b.value - a.value);
    return { buckets: buckets.slice(0, spec.lim), n: recs.length };
  }
  /* native entity: one parameterized aggregate. The tenant scope mirrors the entity
     engine's own rule (platformOnly/noTenant entities are read across stores), so a
     platform dashboard can metric over countries or tenants exactly like a store
     dashboard metrics over its orders. */
  const table = def.table;
  const args = [];
  const where = [];
  if (!def.platformOnly && !def.noTenant) { where.push("tenant_id=?"); args.push(Number(tenantId)); }
  if (!def.noTenant && def.platformOnly) { /* platform-wide: no tenant filter */ }
  for (const [k, v] of Object.entries(spec.filter)) { where.push(resolveField(def, k) + "=?"); args.push(v); }
  const whereSql = where.length ? " WHERE " + where.join(" AND ") : "";
  const agg = spec.metric === "count" ? "COUNT(*)"
    : spec.metric === "distinct" ? "COUNT(DISTINCT " + spec.column + ")"
      : spec.metric.toUpperCase() + "(" + spec.column + ")";
  if (!spec.dimension) {
    const r = get("SELECT " + agg + " v FROM " + table + whereSql, ...args);
    return { value: r ? Number(r.v) : 0 };
  }
  const sql = "SELECT " + spec.dimension + " k, " + agg + " v FROM " + table + whereSql +
    " GROUP BY " + spec.dimension + " ORDER BY v " + spec.ord.toUpperCase() + " LIMIT ?";
  let buckets = rows(sql, ...args, spec.lim).map(r => ({ key: String(r.k == null || r.k === "" ? "—" : r.k), value: Number(r.v) }));
  return { buckets, n: buckets.length };
}

/* ---------- render: a widget declaration → its computed visualization ----------
   This is §394's "Widgets + Visualizations + KPIs + Metrics + Filters" realized: the
   console receives ready-to-draw data and never re-computes a thing. */
function renderWidget(tenantId, w) {
  const entity = require("./entity.js");
  const def = entity.allEntities(tenantId)[w.entity];
  const spec = specOf(w, def);
  if (spec.error) return { id: w.id, kind: "text", label: w.label, span: w.span || 3, error: spec.error };
  try {
    const out = aggregate(tenantId, spec);
    return { id: w.id, kind: spec.kind, label: w.label, span: w.span || 3,
      entity: w.entity, metric: spec.metric, column: spec.column, dimension: spec.dimension,
      value: out.value, buckets: out.buckets, n: out.n || 0, error: null };
  } catch (e) { return { id: w.id, kind: "text", label: w.label, span: w.span || 3, error: e.message }; }
}

/* ---------- dashboards: list / get / render ----------
   A tenant sees its own dashboards plus the platform templates (audience=all or platform
   templates are shared, so a new store inherits the universal set without copying rows). */
function list(tenantId, opts) {
  const o = opts || {};
  const sql = o.platform
    ? "SELECT * FROM dashboards ORDER BY tenant_id IS NULL DESC, position, name"
    : "SELECT * FROM dashboards WHERE tenant_id=? OR (tenant_id IS NULL AND audience!='platform') ORDER BY position, name";
  const ds = o.platform ? rows(sql) : rows(sql, Number(tenantId));
  return ds.filter(d => o.includeInactive || d.active).map(d => ({ ...d, tenant: d.tenant_id }));
}
function getDashboard(tenantId, idOrKey) {
  const col = /^\d+$/.test(String(idOrKey)) ? "id" : "key";
  const d = get("SELECT * FROM dashboards WHERE " + col + "=?", col === "id" ? Number(idOrKey) : String(idOrKey));
  if (!d) return null;
  if (d.tenant_id != null && Number(d.tenant_id) !== Number(tenantId) && d.audience !== "all" && d.audience !== "platform") return null;
  return d;
}
function widgets(dashboardId) {
  return rows("SELECT * FROM dashboard_widgets WHERE dashboard_id=? ORDER BY position, id", dashboardId);
}
/* render a dashboard: widgets + the operator's personalization folded in (§1439).
   Hidden widgets are dropped and the personal order wins over the declared one.
   Audience is enforced here, not only in the listing: a platform-audience board metrics
   over platform-scoped entities (e.g. all stores), so a store admin must not be able to
   render it by guessing its key — the listing gate alone would be trivially bypassed. */
function render(tenantId, idOrKey, userId, isPlatform) {
  const d = getDashboard(tenantId, idOrKey);
  if (!d) return { error: "unknown dashboard " + idOrKey };
  if (d.audience === "platform" && !isPlatform) return { error: "platform console required for this dashboard" };
  if (d.tenant_id != null && Number(d.tenant_id) !== Number(tenantId) && d.audience !== "all") return { error: "not your dashboard" };
  let ws = widgets(d.id);
  if (userId) {
    const prefs = rows("SELECT widget_id, hidden, position FROM dashboard_prefs WHERE user_id=? AND dashboard_id=?", Number(userId), d.id);
    if (prefs.length) {
      const pm = new Map(prefs.map(p => [p.widget_id, p]));
      ws = ws.filter(w => !(pm.get(w.id) || {}).hidden)
        .map(w => ({ ...w, position: (pm.get(w.id) || {}).position != null ? pm.get(w.id).position : w.position }))
        .sort((a, b) => a.position - b.position);
    }
  }
  return { dashboard: { id: d.id, key: d.key, name: d.name, type: d.type, audience: d.audience, description: d.description },
    widgets: ws.map(w => renderWidget(tenantId, w)) };
}

/* ---------- personalization (§1439) ---------- */
function setPref(tenantId, userId, dashboardId, widgetId, patch) {
  run("INSERT INTO dashboard_prefs(tenant_id,user_id,dashboard_id,widget_id,hidden,position) VALUES(?,?,?,?,?,?) "
    + "ON CONFLICT(user_id,dashboard_id,widget_id) DO UPDATE SET hidden=excluded.hidden, position=excluded.position",
    Number(tenantId), Number(userId), Number(dashboardId), Number(widgetId),
    patch.hidden ? 1 : 0, patch.position != null ? Number(patch.position) : 9999);
  return { ok: true };
}

/* ---------- §395 REPORTING ENGINE: Data → Analytics → Visualization → Report ----------
   A report is a declaration: which entity, which metrics, which dimensions, which filter.
   Running it walks the constitution's own pipeline and returns columns + rows + a chart,
   from the same aggregate primitive a widget uses — so the engine is not duplicated. */
function runReport(tenantId, idOrKey) {
  const col = /^\d+$/.test(String(idOrKey)) ? "id" : "key";
  const r = get("SELECT * FROM reports WHERE " + col + "=?", col === "id" ? Number(idOrKey) : String(idOrKey));
  if (!r) return { error: "unknown report " + idOrKey };
  const entity = require("./entity.js");
  const def = entity.allEntities(tenantId)[r.entity];
  if (!def) return { error: "unknown entity " + r.entity, report: r };
  /* a metric's alias becomes a SQL column alias below — it was spliced in verbatim, so a
     stored alias like `x FROM users --` read any table in the database. Only a plain
     identifier is kept; anything else falls back to the generated name. */
  const metrics = J(r.metrics, []).filter(m => m && m.metric && METRICS.includes(m.metric))
    .map(m => ({ ...m, alias: validAlias(m.alias) ? m.alias : undefined }));
  const dims = (J(r.dimensions, []) || []).map(d => resolveField(def, d)).filter(Boolean);
  /* normalize the report filter the same way a widget's is normalized — a string from the
     DB row, an object from the API, both validated against the entity's declared fields */
  const rawFilter = r.filter;
  const filter = !rawFilter ? {} : typeof rawFilter === "string" ? J(rawFilter, {}) : (typeof rawFilter === "object" && !Array.isArray(rawFilter) ? rawFilter : {});
  const fBad = Object.keys(filter).find(k => !resolveField(def, k));
  if (fBad) return { error: "unknown filter field " + fBad, report: r };
  if (!metrics.length && !dims.length) return { error: "report declares no metrics and no dimensions", report: r };
  /* without metrics the report is a pure breakdown; without dimensions it is a scalar set */
  const useMetrics = metrics.length ? metrics : [{ metric: "count", column: null, alias: "count" }];
  /* one pass per dimension set is enough: the cross of dims × metrics is the report body */
  if (!dims.length) {
    const vals = {};
    for (const m of useMetrics) {
      const spec = specOf({ entity: r.entity, metric: m.metric, column: m.column, filter, kind: "kpi" }, def);
      if (spec.error) return { error: spec.error, report: r };
      vals[m.alias || (m.metric + (m.column ? "_" + m.column : ""))] = aggregate(tenantId, spec).value;
    }
    run("UPDATE reports SET last_run=CURRENT_TIMESTAMP WHERE id=?", r.id);
    return { report: { id: r.id, key: r.key, name: r.name, kind: r.kind, entity: r.entity, format: r.format },
      columns: Object.keys(vals), rows: [vals], summary: vals, generatedAt: new Date().toISOString() };
  }
  /* dimensional: buckets per dimension, each carrying every metric */
  const dimSql = dims.join(",");
  const table = def.storage === "json" ? null : def.table;
  if (table) {
    const where = [];
    const args = [];
    if (!def.platformOnly && !def.noTenant) { where.push("tenant_id=?"); args.push(Number(tenantId)); }
    for (const [k, v] of Object.entries(filter)) { where.push(resolveField(def, k) + "=?"); args.push(v); }
    const whereSql = where.length ? " WHERE " + where.join(" AND ") : "";
    const aggSql = useMetrics.map(m => (m.metric === "count" ? "COUNT(*)"
      : m.metric === "distinct" ? "COUNT(DISTINCT " + resolveField(def, m.column) + ")"
        : m.metric.toUpperCase() + "(" + resolveField(def, m.column) + ")") + " AS " + (m.alias || m.metric + "_" + (m.column || "all"))).join(",");
    const sql = "SELECT " + dimSql + ", " + aggSql + " FROM " + table + whereSql + " GROUP BY " + dimSql + " LIMIT 500";
    const rs = rows(sql, ...args);
    run("UPDATE reports SET last_run=CURRENT_TIMESTAMP WHERE id=?", r.id);
    return { report: { id: r.id, key: r.key, name: r.name, kind: r.kind, entity: r.entity, format: r.format },
      columns: [...dims, ...useMetrics.map(m => m.alias || m.metric + "_" + (m.column || "all"))],
      rows: rs.map(x => { const o = {}; for (const d of dims) o[d] = x[d]; for (const m of useMetrics) o[m.alias || m.metric + "_" + (m.column || "all")] = Number(x[m.alias || m.metric + "_" + (m.column || "all")]); return o; }),
      summary: { rows: rs.length }, generatedAt: new Date().toISOString() };
  }
  /* JSON-entity dimensional report: same shape, computed in memory */
  let recs = rows("SELECT data FROM entity_data WHERE entity=?", def.table || r.entity).map(x => J(x.data, {}));
  recs = recs.filter(x => Object.entries(filter).every(([k, v]) => String(x[k]) === String(v)));
  const keyOf = x => dims.map(d => String(x[d] == null || x[d] === "" ? "—" : x[d])).join(" · ");
  const groups = new Map();
  for (const x of recs) { const k = keyOf(x); if (!groups.has(k)) groups.set(k, []); groups.get(k).push(x); }
  const val = (list, m) => {
    if (m.metric === "count") return list.length;
    if (m.metric === "distinct") return new Set(list.map(z => z[resolveField(def, m.column)])).size;
    const xs = list.map(z => Number(z[resolveField(def, m.column)])).filter(n => isFinite(n));
    if (!xs.length) return 0;
    if (m.metric === "sum") return xs.reduce((a, b) => a + b, 0);
    if (m.metric === "avg") return xs.reduce((a, b) => a + b, 0) / xs.length;
    if (m.metric === "min") return Math.min(...xs);
    return Math.max(...xs);
  };
  const out = [...groups.entries()].map(([k, list]) => {
    const o = {}; dims.forEach((d, i) => o[d] = k.split(" · ")[i]); for (const m of useMetrics) o[m.alias || m.metric + "_" + (m.column || "all")] = val(list, m); return o;
  });
  run("UPDATE reports SET last_run=CURRENT_TIMESTAMP WHERE id=?", r.id);
  return { report: { id: r.id, key: r.key, name: r.name, kind: r.kind, entity: r.entity, format: r.format },
    columns: [...dims, ...useMetrics.map(m => m.alias || m.metric + "_" + (m.column || "all"))],
    rows: out.slice(0, 500), summary: { rows: out.length }, generatedAt: new Date().toISOString() };
}

/* a report is "due" when its schedule says so and its last run is stale (§395 Scheduled).
   The engine runs these opportunistically when reports are listed, so a scheduler is not a
   separate process to deploy — the data declares the cadence, the engine honours it. */
function isDue(r) {
  if (!r.active || r.schedule === "manual" || !REPORT_KINDS.includes(r.kind)) return false;
  if (!r.last_run) return true;
  const ms = { daily: 86400000, weekly: 7 * 86400000, monthly: 30 * 86400000 }[r.schedule];
  if (!ms) return false;
  return Date.now() - new Date(String(r.last_run).replace(" ", "T") + "Z").getTime() > ms;
}
 function runDue(tenantId) {
   const out = [];
   for (const r of rows("SELECT * FROM reports WHERE tenant_id IS NULL OR tenant_id=?", Number(tenantId))) {
     if (!isDue(r)) continue;
     // In dev mode: run synchronously; in prod: enqueue as job
     if (process.env.NODE_ENV !== "production") {
       try { const res = runReport(r.tenant_id == null ? tenantId : r.tenant_id, r.id); out.push({ key: r.key, ok: !res.error }); }
       catch (e) { out.push({ key: r.key, ok: false }); }
     } else {
       // Queue the report generation
       try {
         const { addJob } = require("./queue.js");
         addJob("report-run", { reportId: r.id, tenantId: r.tenant_id == null ? tenantId : r.tenant_id });
         out.push({ key: r.key, ok: true });
       } catch (e) { out.push({ key: r.key, ok: false }); }
     }
   }
   return out;
 }

/* ---------- seeding: the constitution's own dashboard types + a canonical set ----------
   Idempotent and never clobbers an operator's edit: the registry list is upserted, the
   dashboards/widgets/reports are INSERT OR IGNORE, so a warm boot costs nothing and a
   console change survives a restart. */
/* the write primitive a composition shares with the console: a board is declared as a
   key + widgets, and the declaration owns the board's own metadata (name, type,
   description) while the operator's widgets are seeded ONCE and never rewritten — the
   same "operator owns the row" rule the rest of the registries follow. */
function saveBoard(b) {
  const ex = get("SELECT id FROM dashboards WHERE key=?", b.key);
  const did = ex ? ex.id : Number(run("INSERT INTO dashboards(tenant_id,key,name,type,audience,description,active,position) VALUES(?,?,?,?,?,?,?,?)",
    b.tenant_id == null ? null : Number(b.tenant_id), b.key, String(b.name || "Untitled").slice(0, 120),
    String(b.type || "Operational").slice(0, 40), ["admin", "platform", "all"].includes(b.audience) ? b.audience : "admin",
    String(b.description || "").slice(0, 500), b.active === false ? 0 : 1, Number(b.position) || 0).lastInsertRowid);
  if (!did) return null;
  if (ex) {
    run("UPDATE dashboards SET name=?,type=?,audience=?,description=?,position=? WHERE id=?",
      String(b.name || "Untitled").slice(0, 120), String(b.type || "Operational").slice(0, 40),
      ["admin", "platform", "all"].includes(b.audience) ? b.audience : "admin",
      String(b.description || "").slice(0, 500), Number(b.position) || 0, did);
    return did;   /* the board follows its declaration; an operator's widgets are kept */
  }
  (b.widgets || []).filter(w => w.kind).forEach((w, i) => run(
    "INSERT INTO dashboard_widgets(dashboard_id,kind,label,entity,metric,column,dimension,ord,lim,filter,position,span) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
    did, w.kind, w.label, w.entity, w.metric || "count", w.column || null, w.dimension || null,
    w.ord || "desc", w.lim || 10, JSON.stringify(w.filter || {}), i, w.span || 3));
  return did;
}
function seed() {
  try { run("INSERT INTO meta_lists(name,label,items,seeded_from) VALUES('dashboardTypes','Dashboard Categories (platform extension of Architecture1 §394)',?,'platform_dashboards') "
    + "ON CONFLICT(name) DO UPDATE SET items=excluded.items, seeded_from=excluded.seeded_from", JSON.stringify(DASHBOARD_TYPES)); } catch (e) { }
  try { run("INSERT INTO meta_lists(name,label,items,seeded_from) VALUES('reportKinds','Report Kinds (Architecture1 §395)',?,'architecture1_report_kinds') "
    + "ON CONFLICT(name) DO UPDATE SET items=excluded.items, seeded_from=excluded.seeded_from", JSON.stringify(REPORT_KINDS)); } catch (e) { }
  /* the canonical store dashboard set — every tenant inherits it as platform templates
     (tenant_id NULL, audience all) so a new store is analytic on its first request. */
  const T = null;
  const mk = (key, name, type, audience, desc, ws) => {
    const ex = get("SELECT id FROM dashboards WHERE tenant_id IS NULL AND key=?", key);
    if (ex) return;
    const r = run("INSERT OR IGNORE INTO dashboards(tenant_id,key,name,type,audience,description,position) VALUES(?,?,?,?,?,?,?)",
      T, key, name, type, audience, desc, ws._pos || 0);
    const did = Number(r.lastInsertRowid);
    if (!did) return;
    ws.filter(w => w.kind).forEach((w, i) => run(
      "INSERT INTO dashboard_widgets(dashboard_id,kind,label,entity,metric,column,dimension,ord,lim,filter,position,span) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
      did, w.kind, w.label, w.entity, w.metric || "count", w.column || null, w.dimension || null,
      w.ord || "desc", w.lim || 10, JSON.stringify(w.filter || {}), i, w.span || 3));
  };
  mk("store-executive", "Executive Overview", "Executive", "all",
    "The store at a glance: revenue, orders, catalogue and customers (§394 Executive).",
    [{ _pos: 0 },
    { kind: "kpi", label: "Total Revenue", entity: "order", metric: "sum", column: "total", span: 2 },
    { kind: "kpi", label: "Orders", entity: "order", metric: "count", span: 2 },
    { kind: "kpi", label: "Avg Order Value", entity: "order", metric: "avg", column: "total", span: 2 },
    { kind: "kpi", label: "Products Live", entity: "product", metric: "count", filter: { lifecycle: "published" }, span: 2 },
    { kind: "kpi", label: "Customers", entity: "customer", metric: "count", span: 2 },
    { kind: "kpi", label: "Universe Offerings", entity: "product", metric: "count", filter: { source_kind: "universe" }, span: 2 },
    { kind: "bar", label: "Revenue by Status", entity: "order", metric: "sum", column: "total", dimension: "status", span: 3 },
    { kind: "donut", label: "Catalogue by Type", entity: "product", metric: "count", dimension: "type", span: 3 },
    { kind: "table", label: "Departments", entity: "product", metric: "count", dimension: "dept", span: 6 }]);
  mk("store-operational", "Operational Health", "Operational", "all",
    "Fulfilment and inventory pressure (§394 Operational).",
    [{ _pos: 1 },
    { kind: "kpi", label: "Pending Orders", entity: "order", metric: "count", filter: { status: "pending" }, span: 3 },
    { kind: "kpi", label: "Delivered", entity: "order", metric: "count", filter: { status: "delivered" }, span: 3 },
    { kind: "kpi", label: "Active SKUs", entity: "sku", metric: "count", filter: { active: 1 }, span: 3 },
    { kind: "kpi", label: "Returns", entity: "ret", metric: "count", span: 3 },
    { kind: "table", label: "Orders by Status", entity: "order", metric: "count", dimension: "status", span: 6 }]);
  mk("store-marketplace", "Marketplace & Supply", "Marketplace", "all",
    "Sellers, suppliers and the universe catalogue (§394 Marketplace + Supplier).",
    [{ _pos: 2 },
    { kind: "kpi", label: "Suppliers", entity: "supplier", metric: "count", span: 3 },
    { kind: "kpi", label: "RFQs Open", entity: "rfq", metric: "count", span: 3 },
    { kind: "kpi", label: "Contracts", entity: "contract", metric: "count", span: 3 },
    { kind: "kpi", label: "Universe Offerings", entity: "product", metric: "count", filter: { source_kind: "universe" }, span: 3 },
    { kind: "bar", label: "Insurance Records by Lifecycle", entity: "uv_insurance", metric: "count", dimension: "status", span: 6 }]);
  mk("platform-compliance", "Platform Compliance & Security", "Compliance", "platform",
    "Platform-wide integrity and registry health (§394 Compliance + Security).",
    [{ _pos: 3 },
    { kind: "kpi", label: "Risk Events", entity: "risk_event", metric: "count", span: 3 },
    { kind: "kpi", label: "Blocklist Entries", entity: "risk_block", metric: "count", span: 3 },
    { kind: "kpi", label: "Countries Seeded", entity: "country", metric: "count", span: 3 },
    { kind: "kpi", label: "Currencies Seeded", entity: "currency", metric: "count", span: 3 },
    { kind: "table", label: "Tenants by Mode", entity: "tenant", metric: "count", dimension: "mode", span: 6 }]);
  /* §395 canonical reports — platform templates (tenant_id NULL).
     SQLite treats NULLs as DISTINCT for a UNIQUE constraint but EQUAL for GROUP BY,
     so INSERT OR IGNORE alone never deduped a NULL-tenant row and every boot appended
     another copy (312 rows for 3 reports on a long-lived DB). The structural fix is the
     sentinel unique index in db.js; the pre-check here keeps the seed honest on DBs that
     predate it. */
  const mkRep = (key, name, kind, entity, metrics, dimensions, schedule, format) => {
    const ex = get("SELECT id FROM reports WHERE tenant_id IS NULL AND key=?", key);
    if (ex) return;
    run("INSERT OR IGNORE INTO reports(tenant_id,key,name,kind,entity,metrics,dimensions,filter,schedule,format,position) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
      T, key, name, kind, entity, JSON.stringify(metrics), JSON.stringify(dimensions), "{}", schedule, format, 0);
  };
  mkRep("rep-revenue", "Revenue by Status", "Executive", "order",
    [{ metric: "sum", column: "total", alias: "revenue" }, { metric: "count", alias: "orders" }], ["status"], "monthly", "table");
  mkRep("rep-catalog", "Catalogue Composition", "Operational", "product",
    [{ metric: "count", alias: "items" }, { metric: "sum", column: "stock", alias: "units" }], ["type", "dept"], "weekly", "table");
  mkRep("rep-corporate-health", "Corporate Universe Health", "Regulatory", "uv_insurance",
    [{ metric: "count", alias: "records" }], ["status"], "daily", "table");
}

/* ---------- §395 report listing (tenant sees its own + platform templates) ---------- */
function reportsFor(tenantId, platform) {
  const sql = platform
    ? "SELECT id,key,name,kind,entity,schedule,format,active,last_run,position FROM reports ORDER BY tenant_id IS NULL DESC, position, name"
    : "SELECT id,key,name,kind,entity,schedule,format,active,last_run,position FROM reports WHERE tenant_id=? OR tenant_id IS NULL ORDER BY position, name";
  return platform ? rows(sql) : rows(sql, Number(tenantId));
}

module.exports = { METRICS, KINDS, DASHBOARD_TYPES, REPORT_KINDS, saveBoard, seed, list, reportsFor, getDashboard, widgets,
  render, renderWidget, setPref, runReport, runDue, isDue, aggregate, specOf, validAlias };
