/* LUXORA Platform — runtime domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the runtime domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "runtime", routes(kit) {
  const { DB_PATH, T, USE_PG, _svc, adapters, ai, all, bad, dbpool, enterprise, env, fs, get, json, logAction, migrate, outboundOffline, queueNow, requireAdmin, requirePlatform, requirePlatformSection, resetRuntimeSvc, rtconfig, storeNow } = kit;

  function apiAdminMonitor(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    /* live per-tenant traffic from the accumulator every request feeds
       (lib/metrics.js) — the console's Monitor view reads totals, the 30-minute
       series and the per-endpoint table from this one snapshot. Read as the
       module singleton rather than a positional argument: the dispatcher hands
       route params before it, so a route with no :param would otherwise receive
       undefined here, and every caller (server.js, a test driving api.handle)
       shares the one accumulator the module's header documents */
    json(res, 200, require("../metrics.js").snapshot(T(s)));
  }
  function apiPlatformMonitor(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    /* the same singleton the store console's Monitor reads (lib/metrics.js) — read
       directly rather than through a positional argument, so the route's handler
       cannot be broken by the dispatcher's param ordering (see apiAdminMonitor) */
    const snap = require("../metrics.js").snapshot(null);
    const mem = process.memoryUsage();
    /* L4: under Postgres DB_PATH still points at the stale SQLite file, so "DB size" reported the
       wrong database. Ask the live server instead. */
    let dbSize = 0;
    if (USE_PG) {
      try { const r = get("SELECT pg_database_size(current_database()) s"); dbSize = (r && Number(r.s)) || 0; } catch (e) { dbSize = 0; }
    } else try { dbSize = fs.statSync(DB_PATH).size; } catch (e) { }
    snap.system = { uptimeSec: Math.floor(process.uptime()), rssMB: +(mem.rss / 1048576).toFixed(1), dbKB: +(dbSize / 1024).toFixed(0), node: process.version, driver: require("../db.js").DRIVER };
    snap.tenants = all("SELECT id, slug, name, status FROM tenants ORDER BY id");
    json(res, 200, snap);
  }
  function apiPlatformRuntime(req, res, url, s) {
    if (!requirePlatformSection(s, res, "runtime", "read")) return;
    const rt = rtconfig.runtime();
    const active = { cache: adapters.build("cache", rt.cache).kind, ratelimit: adapters.build("ratelimit", rt.ratelimit).kind, storage: storeNow().kind, queue: queueNow().kind };
    json(res, 200, { runtime: rtconfig.redactRuntime(rt), catalog: rtconfig.describe(), active, offline: outboundOffline() });
  }
  function apiPlatformRuntimePut(req, res, url, s, body) {
    if (!requirePlatformSection(s, res, "runtime", "write")) return;
    try { rtconfig.saveRuntime(body || {}); } catch (e) { return bad(res, e.message); }
    _svc.q = null; _svc.s = null; /* rebuild adapters on next use with the new drivers */
    logAction(s, "platform.runtime", "runtime", "update", { changed: Object.keys(body || {}).join(",") }, req);
    json(res, 200, { ok: true, runtime: rtconfig.redactRuntime(rtconfig.runtime()) });
  }
  function apiPlatformRuntimeTest(req, res, url, s, body) {
    return (async () => {
      if (!requirePlatform(s, res)) return;
      const concern = String(body && body.concern || "");
      const cfg = rtconfig.get(concern) || {};
      try {
        return json(res, 200, Object.assign({ concern }, await adapters.probe(concern, cfg)));
      } catch (e) { return json(res, 200, { concern, ok: false, error: e.message }); }
    })();
  }
  function apiPlatformQueueDrain(req, res, url, s, body) {
    return (async () => {
      if (!requirePlatform(s, res)) return;
      const r = await queueNow().drain(Math.min(200, Number(body && body.batch) || 50));
      /* also flush any persisted AI tasks in-process (works for inline or redis backends) */
      let done = 0; for (const t of all("SELECT id FROM tenants")) { const ts = ai.tasks(t.id).filter(x => x.status === "queued"); for (const x of ts) { ai.processTask(x.id); done++; } }
      json(res, 200, { ok: true, queue: r, aiTasksProcessed: done });
    })();
  }
  function apiEnvList(req, res, url, s) { if (!requirePlatform(s, res)) return; const e = env.list(); json(res, 200, { environments: e, active: (e.find(x => x.active) || {}).name || null }); }
  function apiEnvGet(req, res, url, s, body, name) { if (!requirePlatform(s, res)) return; const e = env.get(String(name || "")); if (!e) return bad(res, "Unknown environment", 404); json(res, 200, { environment: e }); }
  function apiEnvUpsert(req, res, url, s, body, name) { if (!requirePlatform(s, res)) return; try { const e = env.upsert(name || body.name, body); logAction(s, "environment.save", "environment", name || body.name, { concerns: Object.keys(body.runtime || {}).join(",") }, req); json(res, 200, { ok: true, environment: e }); } catch (e) { return bad(res, e.message); } }
  function apiEnvDelete(req, res, url, s, body, name) { if (!requirePlatform(s, res)) return; env.remove(String(name || "")); logAction(s, "environment.delete", "environment", name); json(res, 200, { ok: true }); }
  function apiEnvActivate(req, res, url, s, body, name) {
    return (async () => {
      if (!requirePlatform(s, res)) return;
      try { const r = env.activate(String(name || "")); resetRuntimeSvc(); logAction(s, "environment.activate", "environment", r.active, {}, req); json(res, 200, r); } catch (e) { return bad(res, e.message); }
    })();
  }
  function apiEnvExport(req, res, url, s) { if (!requirePlatformSection(s, res, "runtime", "read")) return; json(res, 200, { bundle: env.exportAll() }); }
  function apiEnvImport(req, res, url, s, body) { if (!requirePlatformSection(s, res, "runtime", "write")) return; try { const r = env.importAll(body && body.bundle, { activate: !!(body && body.activate) }); if (body && body.activate) resetRuntimeSvc(); logAction(s, "environment.import", "environment", null, { imported: r.imported }, req); json(res, 200, r); } catch (e) { return bad(res, e.message); } }
  function apiEnvTenant(req, res, url, s) { if (!requireAdmin(s, res)) return; json(res, 200, env.resolveFlags(T(s))); }
  /* ---------- B (async dual-engine) observability ---------- */
  function apiPlatformDb(req, res, url, s) {
    return (async () => {
      if (!requirePlatform(s, res)) return;
      let health = { driver: "sqlite", ok: true }; try { health = await dbpool.ping(); } catch (e) { health = { driver: dbpool.driver(), ok: false, error: e.message }; }
      let plan = null; try { plan = migrate.summary(migrate.plan()); } catch (e) { plan = { error: e.message }; }
      json(res, 200, { driver: dbpool.driver(), health, plan });
    })();
  }
  function apiDbPing(req, res, url, s) { return (async () => { if (!requirePlatform(s, res)) return; json(res, 200, await enterprise.dbPing()); })(); }
  function apiDbApply(req, res, url, s, body) { return (async () => { if (!requirePlatformSection(s, res, "runtime", "write")) return; try { json(res, 200, await enterprise.dbApply(!!(body && body.dryRun))); } catch (e) { return bad(res, e.message); } })(); }
  function apiDbSwitch(req, res, url, s, body) { if (!requirePlatformSection(s, res, "runtime", "write")) return; const r = enterprise.dbSwitch(body && body.driver, body && body.mode); if (r.error) return bad(res, r.error); logAction(s, "db.switch", "runtime", null, { driver: body && body.driver, mode: body && body.mode }, req); json(res, 200, r); }

  return [
    ["GET /api/admin/monitor", apiAdminMonitor],
    ["GET /api/platform/db", apiPlatformDb],
    ["POST /api/platform/db/ping", apiDbPing],
    ["POST /api/platform/db/apply", apiDbApply],
    ["POST /api/platform/db/switch", apiDbSwitch],
    ["GET /api/platform/runtime", apiPlatformRuntime],
    ["PUT /api/platform/runtime", apiPlatformRuntimePut],
    ["POST /api/platform/runtime/test", apiPlatformRuntimeTest],
    ["POST /api/platform/queue/drain", apiPlatformQueueDrain],
    ["GET /api/platform/environments", apiEnvList],
    ["POST /api/platform/environments", (r, re, u, s, b, p) => apiEnvUpsert(r, re, u, s, b, (u.searchParams.get("name") || (b && b.name)))],
    ["GET /api/platform/environments/:name", (r, re, u, s, b, p) => apiEnvGet(r, re, u, s, b, p)],
    ["PUT /api/platform/environments/:name", (r, re, u, s, b, p) => apiEnvUpsert(r, re, u, s, b, p)],
    ["DELETE /api/platform/environments/:name", (r, re, u, s, b, p) => apiEnvDelete(r, re, u, s, b, p)],
    ["POST /api/platform/environments/:name/activate", (r, re, u, s, b, p) => apiEnvActivate(r, re, u, s, b, p)],
    ["GET /api/platform/environments-export", apiEnvExport],
    ["POST /api/platform/environments-import", apiEnvImport],
    ["GET /api/env/tenant", apiEnvTenant],
    ["GET /api/platform/monitor", apiPlatformMonitor]
  ];
} };
