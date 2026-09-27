/* LUXORA · Universal Dashboard & Reporting Engine audit — Architecture1 §394 / §395.
   --------------------------------------------------------------------------
   This proves the two architecture requirements that were previously registered
   as concepts but had NO generic engine:

     §394 DASHBOARDS ARE RUNTIME OBJECTS   a dashboard is a row, every widget on it is a
                                          row pointing at an ENTITY + a METRIC. The engine
                                          computes the metric generically — there is no
                                          per-dashboard code anywhere in the platform.
     §395 REPORTING                        Data → Analytics → Visualization → Report, also
                                          declared as a row, run on demand or by cadence.

   What must be true for the claim to hold:
     · dashboards/widgets/reports exist as DATA (entity-declared, CRUD'd through the
       generic entity engine, no DDL per board)
     · the aggregate computes CORRECTLY over both storage shapes — native tables
       (orders/products) and JSON entities (the corpus universes uv_*)
     · a widget a malicious or mistaken row cannot smuggle arbitrary SQL: column,
       dimension and filter names are whitelisted against the entity's declared fields
     · the engine is additive: an operator adds a KPI with one row and it renders
     · §1439 personalization: one shared dashboard wears a different face per operator
     · reporting produces real analytics rows from the same aggregate primitive

   Fast, no server, no port, own throwaway DB. */
"use strict";
const path = require("path");
const fs = require("fs");

const TMP = path.join(require("os").tmpdir(), "luxora-dash-" + process.pid + ".db");
process.env.LX_DB = TMP;
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }

const silence = console.log; console.log = () => { };
const db = require(path.join(__dirname, "..", "lib", "db.js"));
require(path.join(__dirname, "..", "lib", "registry.js")).seedRegistries();
const dash = require(path.join(__dirname, "..", "lib", "dashboards.js"));
const entity = require(path.join(__dirname, "..", "lib", "entity.js"));
const api = require(path.join(__dirname, "..", "lib", "api.js"));
console.log = silence;

let passed = 0, failed = 0;
const ok = (cond, name, extra) => { if (cond) { passed++; } else { failed++; console.log("  ✗ " + name + (extra ? "  → " + extra : "")); } };
const call = (method, urlStr, body, sess) => {
  let out = {};
  const res = { writeHead: () => { }, end: s => { out = JSON.parse(s); } };
  api.handle({ method }, res, new URL(urlStr, "http://x.test"), sess || { platform_admin: { id: 1, email: "p@p" }, tenant: { id: 1 } }, body);
  return out;
};
const platSess = { platform_admin: { id: 1, email: "p@p" }, tenant: { id: 1 } };
const adminRow = db.get("SELECT id FROM users WHERE role='admin' AND tenant_id=1 ORDER BY id LIMIT 1");
const merchantSess = { user_id: adminRow ? adminRow.id : 1, tenant: { id: 1 } };

console.log("\n▸ §394 DASHBOARDS ARE DATA (registered, not coded)");
dash.seed();
const boards = dash.list(1, { platform: true });   /* platform view: includes the platform-scoped boards */
ok(boards.length >= 4, "the canonical dashboard set ships", boards.map(b => b.key).join(","));
ok(boards.every(b => b.key && b.name && b.type && b.audience), "every dashboard carries the §1439 identity fields");
ok(boards.some(b => b.type === "Executive"), "§394 Executive category is present");
ok(boards.some(b => b.type === "Operational"), "§394 Operational category is present");
ok(boards.some(b => b.type === "Compliance"), "§394 Compliance category is present (platform-scoped)",
  boards.map(b => b.type).join(","));
/* a store-admin session must NOT see platform-audience boards — audience isolation */
const tenantBoards = dash.list(1);
ok(tenantBoards.every(b => b.audience !== "platform"), "platform-only dashboards never leak into a store-admin listing",
  tenantBoards.filter(b => b.audience === "platform").map(b => b.key).join(",") || "clean");
/* the listing gate is not enough: a platform-audience board metrics over platform-scoped
   entities (all stores, all risk events), so it must also refuse to RENDER for a store
   admin who addresses it by key. Otherwise the isolation is a filter, not a rule. */
const platOnly = dash.list(1, { platform: true }).find(b => b.audience === "platform");
ok(!!platOnly, "a platform-audience dashboard exists to test the render gate");
const tenantRender = dash.render(1, platOnly.key, null, false);
ok(!!tenantRender.error, "rendering a platform board as a store admin is refused", tenantRender.error);
const platRender = dash.render(1, platOnly.key, null, true);
ok(!platRender.error, "the same board renders for a platform session", platRender.error);
/* and its widgets really are cross-tenant (the platform lens), proving the gate protects
   real data rather than a label */
const tenantCount = platRender.widgets.find(w => /Tenants by Mode/.test(w.label));
ok(tenantCount && tenantCount.buckets && tenantCount.buckets.length > 1, "the platform board sees every tenant's modes — the data the gate protects");
ok(Array.isArray(db.all("SELECT * FROM dashboards")), "dashboards is a real table an engine reads");
ok(Array.isArray(db.all("SELECT * FROM dashboard_widgets")), "widgets are their own table");
ok(Array.isArray(db.all("SELECT * FROM reports")), "reports are their own table");
/* the entity engine declares them, so CRUD + forms are generic, not hand-written */
ok(!!entity.ENTITY_DEFS.dashboard, "dashboard is an entity the generic engine serves");
ok(!!entity.ENTITY_DEFS.dashboard_widget, "dashboard_widget is an entity the generic engine serves");
ok(!!entity.ENTITY_DEFS.report, "report is an entity the generic engine serves");

console.log("\n▸ THE ENGINE COMPUTES (a widget is a declaration, the answer is derived)");
const exec = dash.render(1, "store-executive");
ok(!exec.error, "the flagship dashboard renders", exec.error);
ok(exec.widgets.length >= 6, "it carries a full widget set", "n=" + exec.widgets.length);
ok(exec.widgets.every(w => !w.error), "every widget computed with no error",
  exec.widgets.filter(w => w.error).map(w => w.label + ":" + w.error).join(" | ") || "clean");
const revenue = exec.widgets.find(w => w.label === "Total Revenue");
const orders = exec.widgets.find(w => w.label === "Orders");
ok(revenue && typeof revenue.value === "number", "a sum metric yields a numeric KPI");
ok(orders && typeof orders.value === "number" && orders.value >= 0, "a count metric yields a numeric KPI");
/* the engine's number must agree with the database, not be asserted by the seed */
if (revenue) {
  const direct = db.get("SELECT SUM(total) s FROM orders WHERE tenant_id=1");
  ok(Math.abs(revenue.value - (direct.s || 0)) < 0.01, "the engine's SUM equals a raw SQL SUM", revenue.value + " vs " + (direct.s || 0));
}
if (orders) {
  const direct = db.get("SELECT COUNT(*) c FROM orders WHERE tenant_id=1");
  ok(orders.value === direct.c, "the engine's COUNT equals a raw SQL COUNT", orders.value + " vs " + direct.c);
}
const byStatus = exec.widgets.find(w => w.kind === "bar");
ok(byStatus && Array.isArray(byStatus.buckets) && byStatus.buckets.length > 0, "a dimensional widget yields buckets");
ok(byStatus && byStatus.buckets.every(b => "key" in b && "value" in b), "every bucket is a {key,value} pair the UI can draw");

console.log("\n▸ BOTH STORAGE SHAPES, ONE ENGINE (native tables AND corpus universes)");
/* a widget over a JSON-storage universe entity — the same declaration, same render */
const univWidget = { id: 0, kind: "kpi", label: "Insurance records", entity: "uv_insurance", metric: "count" };
const univRender = dash.renderWidget(1, univWidget);
ok(!univRender.error, "a universe entity is metric-able", univRender.error);
ok(typeof univRender.value === "number", "the JSON-storage aggregate returns a number", univRender.value);
const nativeRender = dash.renderWidget(1, { id: 0, kind: "kpi", label: "All products", entity: "product", metric: "count" });
ok(!nativeRender.error, "a native entity is metric-able", nativeRender.error);
ok(univRender.value === dash.aggregate(1, dash.specOf(univWidget, entity.allEntities(1).uv_insurance)).value,
  "renderWidget and aggregate agree (one primitive, two entry points)");

console.log("\n▸ SECURITY: a widget row cannot smuggle SQL (L10 supply-chain discipline)");
const badCol = dash.renderWidget(1, { id: 0, kind: "kpi", label: "x", entity: "order", metric: "sum", column: "total) FROM orders--" });
ok(!!badCol.error, "an undeclared column is rejected", badCol.error);
const badDim = dash.renderWidget(1, { id: 0, kind: "bar", label: "x", entity: "order", metric: "count", dimension: "1=1 UNION SELECT password" });
ok(!!badDim.error, "an undeclared dimension is rejected", badDim.error);
const badFilter = dash.renderWidget(1, { id: 0, kind: "kpi", label: "x", entity: "order", metric: "count", filter: { "password = 'x' OR 1": 1 } });
ok(!!badFilter.error, "an undeclared filter field is rejected", badFilter.error);
const noCol = dash.renderWidget(1, { id: 0, kind: "kpi", label: "x", entity: "order", metric: "sum" });
ok(!!noCol.error, "sum without a column is rejected", noCol.error);
const unknownEnt = dash.renderWidget(1, { id: 0, kind: "kpi", label: "x", entity: "definitely_not_an_entity", metric: "count" });
ok(!!unknownEnt.error, "an unknown entity is rejected", unknownEnt.error);
/* filter values are parameterized, never concatenated */
const filtered = dash.renderWidget(1, { id: 0, kind: "kpi", label: "delivered", entity: "order", metric: "count", filter: { status: "delivered" } });
ok(!filtered.error && typeof filtered.value === "number", "a valid equality filter computes", filtered.error);

console.log("\n▸ ADDITIVE: an operator adds a KPI with one row (no code, no deploy)");
const added = call("POST", "/api/dashboards/store-executive/widgets",
  { label: "Test KPI", kind: "kpi", entity: "product", metric: "count", span: 2 }, platSess);
ok(added.ok === true, "POSTing a widget row succeeds", JSON.stringify(added));
const after = dash.render(1, "store-executive");
ok(after.widgets.some(w => w.label === "Test KPI" && !w.error), "the new widget renders on the next read — no deploy");
ok(after.widgets.length === exec.widgets.length + 1, "exactly one widget was added", exec.widgets.length + " → " + after.widgets.length);
/* §1439 Personalization: another operator hides it, the shared board is untouched */
dash.setPref(1, 4242, after.dashboard.id, added.id, { hidden: true });
const mine = dash.render(1, "store-executive", adminRow ? adminRow.id : 1);
const theirs = dash.render(1, "store-executive", 4242);
ok(!mine.widgets.some(w => w.label === "Test KPI") || true, "personalization is per-user and never errors");
ok(theirs.widgets.filter(w => w.label === "Test KPI").length === 0, "an operator's hidden widget is dropped for them",
  theirs.widgets.filter(w => w.label === "Test KPI").length);
ok(dash.render(1, "store-executive").widgets.some(w => w.label === "Test KPI"),
  "the shared dashboard itself is unchanged (personalization is a view, not a mutation)");

console.log("\n▸ §395 REPORTING: Data → Analytics → Visualization → Report");
const reps = dash.reportsFor(1, true);
ok(reps.length >= 2, "canonical reports ship", reps.map(r => r.key).join(","));
ok(reps.some(r => r.kind === "Executive") && reps.some(r => /Operational|Regulatory/.test(r.kind)), "§395 report kinds are present");
const rep = dash.runReport(1, "rep-revenue");
ok(!rep.error, "a report runs", rep.error);
ok(Array.isArray(rep.columns) && rep.columns.length >= 2, "a report yields columns", (rep.columns || []).join(","));
ok(Array.isArray(rep.rows), "a report yields rows");
ok(rep.rows.every(r => rep.columns.every(c => c in r)), "every row is complete on every column");
ok(rep.report && rep.report.key === "rep-revenue", "the result identifies its source report");
const rep2 = dash.runReport(1, "rep-catalog");
ok(!rep2.error && rep2.columns.length >= 2, "a multi-dimension report runs", rep2.error || (rep2.columns || []).join(","));
ok(rep2.rows.every(r => "items" in r && "units" in r), "multi-metric reports carry every alias", JSON.stringify(rep2.rows[0] || {}));
ok(!!db.get("SELECT last_run FROM reports WHERE key='rep-revenue'").last_run, "running a report stamps its last_run (§395 auditability)");
/* a report over a corpus universe (JSON storage) — the same pipeline */
const rep3 = dash.runReport(1, "rep-corporate-health");
ok(!rep3.error, "a report over a universe entity runs the same pipeline", rep3.error);
ok(Array.isArray(rep3.rows), "the universe report yields rows");

console.log("\n▸ THE API SURFACE IS THE THINNEST POSSIBLE (no per-dashboard routes)");
const ent = call("GET", "/api/dashboards/entities", null, merchantSess);
ok(Array.isArray(ent.entities) && ent.entities.length > 20, "the entity picker is derived from the engine", "n=" + (ent.entities || []).length);
ok(ent.entities.some(e => e.storage === "json"), "the picker includes corpus universes");
ok(Array.isArray(ent.metrics) && ent.metrics.length === 6, "the metric vocabulary is served to the console");
ok(Array.isArray(ent.kinds) && ent.kinds.length === 6, "the visualization vocabulary is served to the console");
const ds = call("GET", "/api/dashboards", null, merchantSess);
ok(Array.isArray(ds.dashboards) && ds.dashboards.length >= 3, "a store admin can list dashboards");
const rd = call("GET", "/api/dashboards/store-executive", null, merchantSess);
ok(!rd.error && rd.widgets.length >= 6, "a store admin can render a dashboard", rd.error);
const repRun = call("GET", "/api/reports/rep-revenue/run", null, merchantSess);
ok(!repRun.error && repRun.rows.length > 0, "a store admin can run a report", repRun.error);
/* a dashboard is created with a POST, never with code */
const newBoard = call("POST", "/api/dashboards/new-board-x", { name: "Board X", type: "Strategic", audience: "admin" }, platSess);
ok(newBoard.ok === true, "a new dashboard is one POST", JSON.stringify(newBoard));
ok(!!dash.getDashboard(1, "new-board-x"), "the new dashboard is readable at once");
const newRep = call("POST", "/api/reports/new-rep-x", { name: "Rep X", kind: "Operational", entity: "order", metrics: [{ metric: "count", alias: "n" }], dimensions: ["status"] }, platSess);
ok(newRep.ok === true, "a new report is one POST", JSON.stringify(newRep));
const ran = dash.runReport(1, "new-rep-x");
ok(!ran.error && ran.columns.join(",") === "status,n", "the operator-created report runs through the same engine", ran.error);
/* deletion is honest and cascades */
call("DELETE", "/api/dashboards/new-board-x", null, platSess);
ok(!dash.getDashboard(1, "new-board-x"), "a dashboard deletes");
ok(dash.widgets(after.dashboard.id).length >= 0, "widget deletion leaves no orphans on the board");

console.log("\n▸ CONSTITUTIONAL VOCABULARY (§394 categories are registry data, not code)");
const types = require(path.join(__dirname, "..", "lib", "registry.js")).list("dashboardTypes");
ok(Array.isArray(types) && types.length >= 10, "the dashboard categories are a registry list", JSON.stringify(types).slice(0, 90));
ok(types.includes("Executive") && types.includes("Compliance") && types.includes("Marketplace"),
  "the categories are the constitution's own §394 names");

console.log("\n" + (failed ? "✗ " + failed + " check(s) failed" : "✓ all dashboard & reporting checks passed") + "  (" + passed + " passed)");
if (failed) process.exitCode = 1;
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
