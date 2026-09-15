/* LUXORA Platform — SQLite → PostgreSQL migration (B-full foundation).
   `plan()` reads the live SQLite schema + rows and emits a deterministic list of translated DDL +
   parameterized INSERT statements (unit-testable, no server). `apply()` runs them through the async
   Postgres wire client. uid columns become native `gen_random_uuid()` defaults (the SQLite triggers
   are engine-specific). This is the copy/mirror step of a cutover; the request-path async flip is the
   remaining phase (runbook in FLOWS §25). */
"use strict";

const sqlmod = require("./sql.js");

let _db = null; const db = () => _db || (_db = require("./db.js"));

function _ddlToPg(create) {
  let s = create;
  s = s.replace(/\)\s*$/, ")");
  s = s.replace(/\bINTEGER PRIMARY KEY AUTOINCREMENT\b/gi, "BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY");
  s = s.replace(/\bINTEGER PRIMARY KEY\b/gi, "BIGINT PRIMARY KEY");
  s = s.replace(/\bINTEGER\b/gi, "BIGINT").replace(/\bREAL\b/gi, "DOUBLE PRECISION");
  s = s.replace(/DEFAULT \(?\(?\s*datetime\('now'\)\s*\)?\)?/gi, "DEFAULT now()");
  s = s.replace(/\bdatetime\('now'\)/gi, "now()");
  s = sqlmod.toPg(s, { noParams: true }).replace(/AUTOINCREMENT/gi, "");
  return s;
}

function plan() {
  const D = db().db; // raw DatabaseSync
  const tables = D.prepare("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND sql IS NOT NULL ORDER BY tbl_name").all();
  const stmts = [];
  for (const t of tables) {
    let create = _ddlToPg(t.sql);
    if (/uid BIGINT|, uid |uid TEXT| uid /.test(t.sql) || /\buid\b/i.test(t.sql)) {
      // ensure uid column exists with a native default
      create = create.replace(/\buid BIGINT\b/gi, "uid TEXT DEFAULT gen_random_uuid()");
      if (!/\buid\b/i.test(create)) create = create.replace(/\)\s*$/, ",\n  uid TEXT DEFAULT gen_random_uuid()\n)");
    }
    stmts.push({ kind: "ddl", table: t.name, sql: create });
    const rows = D.prepare(`SELECT * FROM "${t.name}"`).all();
    for (const r of rows) {
      const cols = Object.keys(r).filter(c => c !== "rowid");
      const placeholders = cols.map((_, i) => "$" + (i + 1));
      const params = cols.map(c => r[c]);
      const over = cols.includes("id") ? " OVERRIDING SYSTEM VALUE" : "";
      stmts.push({ kind: "data", table: t.name, sql: `INSERT INTO "${t.name}" (${cols.map(c => `"${c}"`).join(",")}) VALUES (${placeholders.join(",")})${over}`, params });
    }
  }
  return stmts;
}

function summary(stmts) {
  const byTable = {};
  for (const s of stmts) { if (s.kind === "ddl") { byTable[s.table] = byTable[s.table] || { ddl: false, rows: 0 }; byTable[s.table].ddl = true; } else { byTable[s.table] = byTable[s.table] || { ddl: false, rows: 0 }; byTable[s.table].rows++; } }
  return { tables: Object.keys(byTable).length, statements: stmts.length, dataStatements: stmts.filter(s => s.kind === "data").length, byTable };
}

async function apply(stmts, conn, onProgress) {
  const pg = require("./pg.js"); const out = { ok: 0, failed: [] };
  for (let i = 0; i < stmts.length; i++) {
    const s = stmts[i];
    try { const r = await pg.queryP(conn, s.sql, s.params || []); if (r && r.error) out.failed.push({ table: s.table, error: r.error }); else out.ok++; }
    catch (e) { out.failed.push({ table: s.table, error: e.message }); }
    if (onProgress && i % 200 === 0) onProgress(i, stmts.length);
  }
  return out;
}

module.exports = { plan, summary, apply, _ddlToPg };
