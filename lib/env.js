/* LUXORA Platform — Environment & Feature-Flag registry (all configuration, no code).
   An "environment" is a named bundle of runtime driver choices + connection params + feature
   flags + tenant routing (dev, staging, eu-west-prod, ...). Operators can define UNLIMITED
   environments, activate one (applies its drivers to the live runtime), and import/export them as
   JSON — a machine or a human sets the whole runtime topology by data. Feature flags are a second
   data registry resolved per tenant with percentage rollout, consumed by surfaces.

   Honesty note: this makes *configuration* unbounded and portable; it does not by itself lift the
   one true scale ceiling — the synchronous web path still reads/writes SQLite until the separate
   async-DB migration (see README). Environment selection is orthogonal to that limit.

   Storage: platform_settings.environments / .env_flags / .env_active. Secrets in env params are
   sealed with the L5 envelope (AAD = env|concern|key) and redacted on read. */
"use strict";

let _db = null, _sec = null, _config = null;
const db = () => _db || (_db = require("./db.js"));
const sec = () => _sec || (_sec = require("./security.js"));
const config = () => _config || (_config = require("./config.js"));
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };
const nowIso = () => new Date().toISOString();

function getK(key, d) { try { const r = db().get("SELECT value FROM platform_settings WHERE key=?", key); return r ? J(r.value, d) : d; } catch (e) { return d; } }
function setK(key, val) { db().run("INSERT INTO platform_settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", key, JSON.stringify(val)); }

const isSecret = (concern, driver, k) => ((config().DRIVER_FIELDS[driver] || []).find(f => f.key === k) || {}).secret;

/* seal secret params, leave non-secrets plain */
function sealParams(envName, runtimeObj) {
  const out = {};
  for (const [concern, cfg] of Object.entries(runtimeObj || {})) {
    const params = Object.assign({}, cfg.params || {});
    for (const k of Object.keys(params)) if (isSecret(concern, cfg.driver, k) && params[k] && !String(params[k]).startsWith("lux.v1.")) params[k] = sec().encryptSecret(String(params[k]), envName + "|" + concern + "|" + k);
    out[concern] = { driver: cfg.driver, params };
  }
  return out;
}
function unsealParams(runtimeObj) {
  const out = {};
  for (const [concern, cfg] of Object.entries(runtimeObj || {})) {
    const params = Object.assign({}, cfg.params || {});
    for (const k of Object.keys(params)) if (isSecret(concern, cfg.driver, k) && params[k]) { try { params[k] = sec().decryptSecret(String(params[k]), concern); } catch (e) { params[k] = ""; } }
    out[concern] = { driver: cfg.driver, params };
  }
  return out;
}
function redactParams(runtimeObj) {
  const out = {};
  for (const [concern, cfg] of Object.entries(runtimeObj || {})) {
    const params = Object.assign({}, cfg.params || {});
    for (const k of Object.keys(params)) if (isSecret(concern, cfg.driver, k) && params[k]) params[k] = "••••";
    out[concern] = { driver: cfg.driver, params: Object.keys(params).length ? params : undefined };
  }
  return out;
}

function list() {
  const envs = getK("environments", {}); const flags = getK("env_flags", {}); const active = getK("env_active", null);
  return Object.entries(envs).map(([name, e]) => ({ name, label: e.label || name, region: e.region || null, tenants: e.tenants || [], note: e.note || "", flags: Object.keys(flags).filter(f => (flags[f].envs || []).includes(name)), runtime: redactParams(e.runtime || {}), created_at: e.created_at, updated_at: e.updated_at, active: name === active }));
}
function get(name) { const e = getK("environments", {})[name]; if (!e) return null; return { name, ...e, runtime: redactParams(e.runtime || {}) }; }

function validate(runtimeObj) {
  const catalog = config().RUNTIME_CATALOG;
  for (const [concern, cfg] of Object.entries(runtimeObj || {})) {
    if (!catalog[concern]) throw new Error("Unknown concern " + concern);
    if (!catalog[concern].drivers.includes(cfg.driver)) throw new Error("Driver " + cfg.driver + " not allowed for " + concern);
  }
}

function upsert(name, body) {
  name = String(name || "").trim().toLowerCase().replace(/[^a-z0-9_-]/g, "");
  if (!name) throw new Error("environment name required");
  const envs = getK("environments", {}); const prev = envs[name] || {};
  validate(body.runtime || {});
  const merged = Object.assign({}, prev.runtime || {}, body.runtime || {});
  const e = {
    label: body.label || prev.label || name, region: body.region != null ? body.region : prev.region, tenants: body.tenants != null ? [].concat(body.tenants).map(Number) : (prev.tenants || []),
    note: body.note != null ? body.note : prev.note, runtime: sealParams(name, merged), created_at: prev.created_at || nowIso(), updated_at: nowIso()
  };
  envs[name] = e; setK("environments", envs);
  return get(name);
}
function remove(name) { const envs = getK("environments", {}); delete envs[name]; setK("environments", envs); const a = getK("env_active", null); if (a === name) setK("env_active", null); return { ok: true }; }

/* applying an environment writes its runtime into the live runtime (single source of truth) */
function activate(name) {
  const e = getK("environments", {})[name]; if (!e) throw new Error("Unknown environment");
  config().saveRuntime(unsealParams(e.runtime || {}));
  setK("env_active", name);
  return { ok: true, active: name, runtime: config().runtime() };
}

/* effective environment for a tenant: explicit tenant routing → default env; else base runtime */
function forTenant(tenantId) {
  const envs = getK("environments", {}); const active = getK("env_active", null);
  for (const [n, e] of Object.entries(envs)) if ((e.tenants || []).includes(Number(tenantId))) return n;
  return active;
}

/* boot: if LX_ENV names a registered environment, activate it (one var selects a whole topology) */
function boot() { const n = process.env.LX_ENV; if (!n) return; try { if (getK("environments", {})[n]) activate(n); } catch (e) { console.error("env boot:", e.message); } }

/* ---- feature flags (data), resolved per tenant with percentage rollout ---- */
function flags() { return getK("env_flags", {}); }
function setFlag(name, body) {
  name = String(name || "").trim(); if (!name) throw new Error("flag name required");
  const f = flags(); const prev = f[name] || {};
  f[name] = { description: body.description != null ? body.description : prev.description || "", default: body.default != null ? !!body.default : !!prev.default, rollout: Number(body.rollout != null ? body.rollout : (prev.rollout || 0)), envs: body.envs != null ? [].concat(body.envs) : (prev.envs || []) };
  setK("env_flags", f); return { name, ...f[name] };
}
function delFlag(name) { const f = flags(); delete f[name]; setK("env_flags", f); return { ok: true }; }
function flagOn(name, tenantId, env) {
  const def = flags()[name]; if (!def) return false;
  if (def.envs && def.envs.length) { const e = env || forTenant(tenantId) || "base"; if (!def.envs.includes(e)) return false; }
  if (def.rollout >= 100) return true; if (def.rollout <= 0) return !!def.default;
  const h = parseInt(require("crypto").createHash("sha1").update(name + ":" + (tenantId || 0)).digest("hex").slice(0, 6), 16);
  return (h % 100) < def.rollout;
}
function resolveFlags(tenantId) { const f = flags(); const env = forTenant(tenantId); const out = {}; for (const k of Object.keys(f)) out[k] = flagOn(k, tenantId, env); return { env, flags: out }; }

function exportAll() { const envs = getK("environments", {}); const safe = {}; for (const [n, e] of Object.entries(envs)) { const rt = {}; for (const [c, cfg] of Object.entries(e.runtime || {})) { const p = Object.assign({}, cfg.params || {}); for (const k of Object.keys(p)) if (isSecret(c, cfg.driver, k) && p[k]) p[k] = null; rt[c] = { driver: cfg.driver, params: p }; } safe[n] = { label: e.label, region: e.region, tenants: e.tenants, note: e.note, runtime: rt }; } return { version: 1, exported_at: nowIso(), active: getK("env_active", null), environments: safe, flags: getK("env_flags", {}) }; }
function importAll(bundle, { activate = false } = {}) {
  const envs = getK("environments", {});
  for (const [n, e] of Object.entries((bundle && bundle.environments) || {})) { try { validate(e.runtime || {}); envs[n] = { label: e.label, region: e.region, tenants: e.tenants || [], note: e.note, runtime: sealParams(n, e.runtime || {}), created_at: nowIso(), updated_at: nowIso() }; } catch (err) { /* skip invalid, keep others */ } }
  setK("environments", envs);
  if (bundle && bundle.flags) setK("env_flags", bundle.flags);
  if (activate && bundle && bundle.active && envs[bundle.active]) try { activate2(bundle.active); } catch (e) { }
  return { ok: true, imported: Object.keys((bundle && bundle.environments) || {}).length };
}
function activate2(n) { const e = getK("environments", {})[n]; config().saveRuntime(unsealParams(e.runtime || {})); setK("env_active", n); }

function describe() { return { concerns: Object.keys(config().RUNTIME_CATALOG), catalog: config().RUNTIME_CATALOG }; }

module.exports = { list, get, upsert, remove, activate, forTenant, boot, flags, setFlag, delFlag, flagOn, resolveFlags, exportAll, importAll, describe, J };
