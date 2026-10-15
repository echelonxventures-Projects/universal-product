/* LUXORA Platform — runtime configuration spine.
   Every infra choice (cache, queue, storage, rate-limit backend, session, outbound mode) is
   resolved here from DATA ONLY: safe in-process defaults → editable `platform_settings.runtime`
   (Platform → Runtime) → env override. lib/adapters.js implements the selectable backends, so
   switching a concern to Redis/S3/a worker/HTTP hook is a config change, not a code change.
   The DB is intentionally kept as the SQLite default with an interface-isolated seam (see db.js
   run/all/get); `db` is exposed here as a configured concern so the shape is uniform, but only
   the sqlite driver is wired (selecting postgres reports "not provisioned" rather than lying). */
"use strict";

let _db = null;
const db = () => _db || (_db = require("./db.js"));
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };

/* The catalog of configurable concerns + their selectable drivers (drives the Runtime UI +
   validation). Add a driver here and implement it in adapters.js — nothing else hard-codes them. */
const RUNTIME_CATALOG = {
  cache: { label: "Settings / object cache", default: "memory", drivers: ["memory", "redis"] },
  queue: { label: "Job queue (AI, exports, bulk)", default: "inline", drivers: ["inline", "redis", "webhook"] },
  storage: { label: "File / export storage", default: "local", drivers: ["local", "s3", "webhook"] },
  ratelimit: { label: "Rate-limit / lockout store", default: "memory", drivers: ["memory", "redis"] },
  session: { label: "Session backend", default: "db", drivers: ["db", "token"] },
  outbound: { label: "Payments / notifications / AI", default: "auto", drivers: ["auto", "offline", "live"] },
  db: { label: "Primary datastore", default: "sqlite", drivers: ["sqlite", "postgres"], note: "postgres drives async surfaces (workers/exports/reports); the synchronous web path stays on sqlite until the async migration" }
};

/* per-driver connection params the operator may set (secrets are sealed like gateway creds) */
const DRIVER_FIELDS = {
  redis: [{ key: "url", label: "Redis URL (redis://host:port)", secret: true }],
  s3: [{ key: "bucket", label: "Bucket" }, { key: "region", label: "Region" }, { key: "accessKey", label: "Access key" }, { key: "secretKey", label: "Secret key", secret: true }, { key: "endpoint", label: "Endpoint (optional, S3-compat)" }],
  webhook: [{ key: "url", label: "Webhook URL" }, { key: "secret", label: "Bearer secret", secret: true }],
  postgres: [{ key: "url", label: "Connection string (postgres://user:pass@host:5432/db)", secret: true }]
};

const ENV = {
  cache: process.env.LX_CACHE, queue: process.env.LX_QUEUE, storage: process.env.LX_STORAGE,
  ratelimit: process.env.LX_RATELIMIT, session: process.env.LX_SESSION, outbound: process.env.LX_OUTBOUND, db: process.env.LX_DB_DRIVER,
  redisUrl: process.env.LX_REDIS_URL, s3Bucket: process.env.LX_S3_BUCKET, s3Region: process.env.LX_S3_REGION,
  s3Access: process.env.LX_S3_ACCESS, s3Secret: process.env.LX_S3_SECRET, s3Endpoint: process.env.LX_S3_ENDPOINT,
  hookUrl: process.env.LX_WEBHOOK_URL, hookSecret: process.env.LX_WEBHOOK_SECRET, pgUrl: process.env.LX_PG_URL
};

const DEFAULTS = {}; for (const k of Object.keys(RUNTIME_CATALOG)) DEFAULTS[k] = { driver: RUNTIME_CATALOG[k].default };

function loadRaw() {
  let saved = {};
  try { const r = db().get("SELECT value FROM platform_settings WHERE key='runtime'"); if (r) saved = J(r.value, {}); } catch (e) { }
  return saved;
}
/* merged view: default → stored → env */
function runtime() {
  const saved = loadRaw(); const out = {};
  for (const concern of Object.keys(RUNTIME_CATALOG)) {
    const d = RUNTIME_CATALOG[concern];
    const s = saved[concern] || {};
    const envDriver = ENV[concern];
    const driver = envDriver || s.driver || d.default;
    const params = Object.assign({}, DRIVER_PARAMS(driver, s));
    for (const [k, val] of Object.entries(ENV_PARAMS(driver))) if (val) params[k] = val; // env overrides only when set
    /* L7: `db` is a CONCERN, not a driver — the db concern's drivers are sqlite/postgres, so
       comparing the driver name to "db" never matched. sqlite needs no params (its path is env),
       and the postgres url lives in params, so gate on the real driver names. */
    const driverless = driver === "memory" || driver === "inline" || driver === "local" || driver === "db" || driver === "sqlite" || driver === "auto";
    out[concern] = { driver, params: driverless ? undefined : (params && Object.keys(params).filter(k => params[k] != null).length ? Object.fromEntries(Object.entries(params).filter(([, v]) => v != null)) : undefined), options: d.drivers, label: d.label, default: d.default };
  }
  if (ENV.LX_OFFLINE === "1" || process.env.LX_OFFLINE === "1") out.outbound.driver = "offline";
  return out;
}
function get(concern) { return runtime()[concern] || { driver: (RUNTIME_CATALOG[concern] || {}).default || "memory" }; }
function driverOf(concern) { return get(concern).driver; }

/* connection params carry credentials (postgres/redis urls embed a password; S3 keys; bearer
   secrets). The console never receives them in clear: secret-looking params are masked on the
   way out, and a masked value sent back on save keeps the stored one. */
const SECRET_PARAM = /url|uri|dsn|secret|password|passwd|token|key|credential|auth/i;
const MASK = "••••";
function maskValue(v) { const t = String(v == null ? "" : v); return t ? MASK + (t.length > 8 ? t.slice(-4) : "") : ""; }
function redactRuntime(rt) {
  const out = {};
  for (const [c, cfg] of Object.entries(rt || {})) {
    const params = cfg && cfg.params ? Object.fromEntries(Object.entries(cfg.params).map(([k, v]) => [k, SECRET_PARAM.test(k) && v ? maskValue(v) : v])) : cfg && cfg.params;
    out[c] = { ...cfg, params };
  }
  return out;
}
function saveRuntime(patch) {
  const D = db(); const cur = loadRaw();
  for (const [c, v] of Object.entries(patch || {})) {
    if (!RUNTIME_CATALOG[c]) continue;
    const allowed = RUNTIME_CATALOG[c].drivers;
    const driver = (typeof v === "string" ? v : v.driver);
    if (!allowed.includes(driver)) throw new Error(`Unknown driver "${driver}" for ${c} (allowed: ${allowed.join(", ")})`);
    const prev = (cur[c] && cur[c].params) || {};
    const incoming = (v && v.params) || null;
    const params = incoming ? Object.fromEntries(Object.entries(incoming).map(([k, val]) => [k, typeof val === "string" && val.startsWith(MASK) ? prev[k] : val])) : prev;
    cur[c] = { driver, params };
  }
  D.run("INSERT INTO platform_settings(key,value) VALUES('runtime',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", JSON.stringify(cur));
  return cur;
}

function DRIVER_PARAMS(driver, stored) { return (stored && stored.params) || {}; }
function ENV_PARAMS(driver) {
  if (driver === "redis") return { url: ENV.redisUrl };
  if (driver === "s3") return { bucket: ENV.s3Bucket, region: ENV.s3Region, accessKey: ENV.s3Access, secretKey: ENV.s3Secret, endpoint: ENV.s3Endpoint };
  if (driver === "webhook") return { url: ENV.hookUrl, secret: ENV.hookSecret };
  if (driver === "postgres") return { url: ENV.pgUrl };
  return {};
}

/* health: which backends are actually reachable right now (used by Runtime screen + tests).
   Adapters are injected so config doesn't hard-depend on them (avoids require cycle). */
function describe() { return { catalog: RUNTIME_CATALOG, driverFields: DRIVER_FIELDS, env: Object.keys(ENV) }; }

module.exports = { redactRuntime, RUNTIME_CATALOG, DRIVER_FIELDS, runtime, get, driverOf, saveRuntime, describe, J };
