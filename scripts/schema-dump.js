/* LUXORA Platform — regenerate schema.sql from a fresh boot.
   schema.sql is the reference snapshot of the SQLite schema (the Postgres migration path
   and reviewers read it). It is derived, never hand-written: boot the data layer and every module
   that declares its own tables against a throwaway database, dump sqlite_master, and group each
   table — with its indexes — under the business domain that owns it (_registry/business-domains.json).
   The code is the single source of truth for each table; this file is its readable projection.
   Usage: npm run schema                     writes schema.sql
          node scripts/schema-dump.js --print   writes the snapshot to stdout (test/security.js
          compares it with schema.sql, so a stale or hand-edited snapshot fails) */
"use strict";
const fs = require("fs"), path = require("path"), os = require("os");

/* the modules that declare tables of their own, and the function that declares them */
const OWN_TABLES = [
  ["kernel.js", "ensureTables"], ["kernel-shape.js", "ensureTables"], ["kernel-context.js", "ensureTables"],
  ["kernel-lifecycle.js", "ensureTables"], ["tenancy.js", "ensureTables"],
  ["affiliate.js", "seed"], ["shipping.js", "seed"], ["sitemap.js", "seed"]
];

function rowsOf(dbFile) {
  const { DatabaseSync } = require("node:sqlite");
  const d = new DatabaseSync(dbFile, { readOnly: true });
  const rows = d.prepare("SELECT type, name, tbl_name, sql FROM sqlite_master WHERE sql IS NOT NULL AND name NOT LIKE 'sqlite_autoindex%' ORDER BY rowid").all();
  d.close();
  return rows;
}
/* the snapshot: each domain's tables under its heading, in the order the boot created them */
function render(rows) {
  const cat = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "_registry", "business-domains.json"), "utf8"));
  const owner = new Map();
  for (const d of cat.domains) for (const t of d.owns.tables || []) owner.set(t, d);
  const sections = new Map();
  for (const r of rows) {
    const d = owner.get(r.tbl_name) || null;
    const k = d ? d.key : "";
    if (!sections.has(k)) sections.set(k, { d, sql: [] });
    sections.get(k).sql.push(r.sql.trim() + ";");
  }
  const order = cat.domains.map(d => d.key).filter(k => sections.has(k)).concat(sections.has("") ? [""] : []);
  return order.map(k => {
    const s = sections.get(k);
    const head = s.d ? `-- ── ${s.d.key} · ${s.d.name} ` : "-- ── no owning domain (claim these in _registry/business-domains.json) ";
    return head + "─".repeat(Math.max(4, 100 - head.length)) + "\n" + s.sql.join("\n");
  }).join("\n\n") + "\n";
}
function tables(sqlText) {
  return [...String(sqlText).matchAll(/CREATE TABLE (?:IF NOT EXISTS )?"?([A-Za-z0-9_]+)"?/g)].map(m => m[1]).filter(n => n !== "sqlite_sequence").sort();
}

if (require.main === module) {
  const tmp = path.join(fs.mkdtempSync(path.join(os.tmpdir(), "lx-schema-")), "schema.db");
  process.env.LX_DB = tmp;
  process.env.LX_QUIET = "1";
  const log = console.log; console.log = () => { }; // the boot's own messages are not the snapshot
  require("../lib/db.js");
  try { require("../lib/registry.js"); } catch (e) { }
  for (const [f, fn] of OWN_TABLES) { const m = require("../lib/" + f); if (typeof m[fn] !== "function") throw new Error("lib/" + f + " no longer exports " + fn); m[fn](); }
  console.log = log;
  const out = render(rowsOf(tmp));
  for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(tmp + s, { force: true }); } catch (e) { } }
  /* exit only once stdout has drained: a pipe is written asynchronously, and exiting at once would
     cut the snapshot off at the pipe's buffer */
  if (process.argv.includes("--print")) process.stdout.write(out, () => process.exit(0));
  else { fs.writeFileSync(path.join(__dirname, "..", "schema.sql"), out); console.log("schema.sql regenerated — " + tables(out).length + " tables"); process.exit(0); }
}
module.exports = { render, rowsOf, tables, OWN_TABLES };
