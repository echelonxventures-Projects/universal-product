/* LUXORA Platform — SQLite → PostgreSQL migration (B-full foundation).
   `plan()` reads the live SQLite schema + rows and emits a deterministic list of translated DDL +
   parameterized INSERT statements (unit-testable, no server). `apply()` runs them through the async
   Postgres wire client. uid columns become native `gen_random_uuid()` defaults (the SQLite triggers
   are engine-specific). This is the copy/mirror step of a cutover; the request path then runs on the
   synchronous Postgres bridge (LX_DB_DRIVER=postgres — see lib/pgbridge.js / lib/db.js). */
"use strict";

const sqlmod = require("./sql.js");

let _db = null; const db = () => _db || (_db = require("./db.js"));

function _ddlToPg(create) {
  let s = create;
  s = s.replace(/\)\s*$/, ")");
  s = s.replace(/\bINTEGER PRIMARY KEY AUTOINCREMENT\b/gi, "BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY");
  s = s.replace(/\bINTEGER PRIMARY KEY\b/gi, "BIGINT PRIMARY KEY");
  s = s.replace(/\bINTEGER\b/gi, "BIGINT").replace(/\bREAL\b/gi, "DOUBLE PRECISION");
  s = s.replace(/DEFAULT \(?\(?\s*datetime\('now'\)\s*\)?\)?/gi, "DEFAULT to_char(now(), 'YYYY-MM-DD HH24:MI:SS')");
  s = s.replace(/\bdatetime\('now'\)/gi, "to_char(now(), 'YYYY-MM-DD HH24:MI:SS')");
  s = sqlmod.toPg(s, { noParams: true }).replace(/AUTOINCREMENT/gi, "");
  return s;
}

/* FK-aware DDL order: a table's REFERENCES targets must be created first (cycles break arbitrarily). */
function topoSort(tables) {
  const byName = {}; for (const t of tables) byName[t.name] = t;
  const deps = {}; for (const t of tables) deps[t.name] = [...new Set([...String(t.sql).matchAll(/REFERENCES\s+"?(\w+)"?/gi)].map(m => m[1]))].filter(d => d !== t.name && byName[d]);
  const out = [], seen = {}, stack = {};
  const visit = n => { if (seen[n] || stack[n]) return; stack[n] = 1; for (const d of deps[n] || []) visit(d); stack[n] = 0; seen[n] = 1; out.push(byName[n]); };
  for (const t of tables) visit(t.name);
  return out;
}

/* translate a SQLite CREATE TABLE: dialect + the uid trigger → native gen_random_uuid() default */
function ddlToPg(sql) {
  let create = _ddlToPg(sql);
  if (/\buid\b/i.test(sql)) {
    create = create.replace(/\buid\s+(BIGINT|TEXT)(?!\s+DEFAULT)/gi, "uid TEXT DEFAULT gen_random_uuid()");
    if (!/gen_random_uuid/i.test(create)) create = create.replace(/\)\s*$/, ",\n  uid TEXT DEFAULT gen_random_uuid()\n)");
  }
  return create;
}

function plan() {
  /* The migration always reads the SQLite SOURCE file, even when the server is already running
     on Postgres (the live handle is then the bridge, which has no sqlite_master). */
  const { DatabaseSync } = require("node:sqlite");
  /* L5: detecting the bridge by "has prepare() but no LX_DB_DRIVER" opened a SECOND
     DatabaseSync on the same file whenever LX_DB_DRIVER was exported explicitly, and only worked
     by accident of the trailing env clause. Branch on the real driver flag instead. */
  const owned = !require("./db.js").USE_PG;
  const D = owned ? new DatabaseSync(db().DB_PATH) : db().db;
  try {
    const tables = D.prepare("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND sql IS NOT NULL ORDER BY tbl_name").all();
    /* H4: indexes were never planned — 72 of them (62 UNIQUE) silently vanished, dropping every
       hot-path index and every ux_* uniqueness constraint. Plan them separately and emit the
       CREATE INDEX statements AFTER the data load (far faster than maintaining them during the
       inserts). Partial-index WHERE clauses survive verbatim; inline PK/UNIQUE constraints are
       already part of CREATE TABLE and are intentionally excluded (sql IS NOT NULL filters
       auto-indexes). */
    const idx = D.prepare("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL ORDER BY tbl_name, name").all();
    const stmts = [];
    for (const t of topoSort(tables)) {
      stmts.push({ kind: "ddl", table: t.name, sql: ddlToPg(t.sql) });
      const rows = D.prepare(`SELECT * FROM "${t.name}"`).all();
      for (const r of rows) {
        const cols = Object.keys(r).filter(c => c !== "rowid");
        const placeholders = cols.map((_, i) => "$" + (i + 1));
        const params = cols.map(c => r[c]);
        const over = cols.includes("id") ? "OVERRIDING SYSTEM VALUE " : "";
        stmts.push({ kind: "data", table: t.name, sql: `INSERT INTO "${t.name}" (${cols.map(c => `"${c}"`).join(",")}) ${over}VALUES (${placeholders.join(",")})`, params });
      }
    }
    for (const ix of idx) stmts.push({ kind: "index", table: ix.tbl_name, sql: ddlToPg(ix.sql) });
    return stmts;
  } finally { if (owned) D.close(); }
}

function summary(stmts) {
  const byTable = {};
  for (const s of stmts) { if (s.kind === "ddl") { byTable[s.table] = byTable[s.table] || { ddl: false, rows: 0 }; byTable[s.table].ddl = true; } else { byTable[s.table] = byTable[s.table] || { ddl: false, rows: 0 }; byTable[s.table].rows++; } }
  return { tables: Object.keys(byTable).length, statements: stmts.length, dataStatements: stmts.filter(s => s.kind === "data").length, byTable };
}

async function apply(stmts, conn, onProgress) {
  const pg = require("./pg.js");
  /* M1: the old loop opened a fresh TCP connection (connect + auth + query + close) per
     statement — 3,909 round trips for a real migration, with no transaction, so a mid-run
     failure left a half-migrated database and no way to roll back. Run the whole load on ONE
     connection inside a single transaction: it is atomic, and the reconnect overhead is gone. */
  const out = { ok: 0, failed: [] };
  const c = conn || { connectionString: process.env.LX_PG_URL };
  try { await pg.queryP(c, "BEGIN", []); }
  catch (e) { out.failed.push({ table: "-", error: "could not begin transaction: " + e.message }); return out; }
  for (let i = 0; i < stmts.length; i++) {
    const s = stmts[i];
    try { const r = await pg.queryP(c, s.sql, s.params || []); if (r && r.error) out.failed.push({ table: s.table, error: r.error }); else out.ok++; }
    catch (e) { out.failed.push({ table: s.table, error: e.message }); }
    if (onProgress && i % 200 === 0) onProgress(i, stmts.length);
  }
  /* Identity columns are inserted with OVERRIDING SYSTEM VALUE, which leaves the backing
     sequence at its start (1). Advance it past the copied rows so the first runtime INSERT
     (which omits id) does not collide with an existing primary key. */
  for (const t of new Set(stmts.filter(s => s.kind === "ddl" && /GENERATED\s+ALWAYS\s+AS\s+IDENTITY/i.test(s.sql)).map(s => s.table))) {
    const sql = `SELECT setval(pg_get_serial_sequence('"${t}"','id'), COALESCE((SELECT MAX(id) FROM "${t}"), 0) + 1, false)`;
    try { const r = await pg.queryP(c, sql, []); if (r && r.error) out.failed.push({ table: t, error: r.error }); else out.ok++; }
    catch (e) { out.failed.push({ table: t, error: e.message }); }
  }
  /* commit only when nothing failed; otherwise roll the whole load back so the target DB is
     left clean rather than half-migrated (and a retry is safe). */
  if (out.failed.length === 0) { try { await pg.queryP(c, "COMMIT", []); } catch (e) { out.failed.push({ table: "-", error: "commit failed: " + e.message }); } }
  else { try { await pg.queryP(c, "ROLLBACK", []); } catch (e) { } out.ok = 0; }
  return out;
}

module.exports = { plan, summary, apply, topoSort, ddlToPg, _ddlToPg };
