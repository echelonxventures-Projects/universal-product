/* LUXORA Platform — async dual-engine data pool (B-full foundation).
   One async facade over the data layer, driver-selected by config (`db`: sqlite|postgres):
   - sqlite: the existing synchronous DB (lib/db.js), wrapped as promises (default; no behavior change)
   - postgres: SQL is dialect-translated (lib/sql.js) and executed via the wire client (lib/pg.js)
   The synchronous request path still uses lib/db.js directly today; this pool is the target all
   data access converges onto during the cutover (see the runbook). Not wired into routes yet — it is
   the mechanism, tested in isolation, that makes B-full mechanical rather than a rewrite-by-hand. */
"use strict";

let _db = null, _cfg = null, _sql = null, _pg = null;
const db = () => _db || (_db = require("./db.js"));
const cfg = () => _cfg || (_cfg = require("./config.js"));
const sql = () => _sql || (_sql = require("./sql.js"));
const pg = () => _pg || (_pg = require("./pg.js"));

function driver() { try { return cfg().driverOf("db"); } catch (e) { return "sqlite"; } }
function _pgUrl() { const c = cfg().get("db"); return (c && c.params && c.params.url) || process.env.LX_PG_URL; }

async function all(q, ...args) {
  if (driver() === "postgres") { const r = await pg().queryP(_pgUrl(), sql().toPg(q), args); if (r && r.error) throw new Error(r.error); return (r && r.rows) || []; }
  return db().all(q, ...args);
}
async function get(q, ...args) { const rows = await all(q, ...args); return rows[0] || null; }
async function run(q, ...args) {
  if (driver() === "postgres") { const r = await pg().queryP(_pgUrl(), sql().toPg(q), args); if (r && r.error) throw new Error(r.error); return { changes: _tagCount(r && r.cmdTag), lastInsertRowid: null }; }
  return db().run(q, ...args);
}
async function exec(script) {
  if (driver() === "postgres") { for (const st of splitStatements(script)) await pg().queryP(_pgUrl(), sql().toPg(st)); return; }
  return db().exec(script);
}
function _tagCount(tag) { const m = /(\d+)\s*$/.exec(String(tag || "")); return m ? Number(m[1]) : 0; }
function splitStatements(script) { return String(script).split(/;\s*(?:\n|$)/).map(s => s.trim()).filter(Boolean); }

async function ping() { if (driver() !== "postgres") return { driver: "sqlite", ok: true }; const a = pg().adapter({ url: _pgUrl() }); return { driver: "postgres", ...(await a.ping()) }; }

module.exports = { driver, all, get, run, exec, ping, splitStatements };
