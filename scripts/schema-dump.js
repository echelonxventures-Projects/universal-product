/* LUXORA Platform — regenerate schema.sql from a fresh boot.
   schema.sql is the reference snapshot of the SQLite schema (the Postgres migration path
   and reviewers read it). It was hand-maintained and drifted 35 tables behind lib/db.js;
   it is now derived: boot the data layer against a throwaway database, dump sqlite_master.
   Usage: npm run schema   (test/security.js fails if the snapshot is stale) */
"use strict";
const fs = require("fs"), path = require("path"), os = require("os");

function dump(dbFile) {
  const { DatabaseSync } = require("node:sqlite");
  const d = new DatabaseSync(dbFile, { readOnly: true });
  const rows = d.prepare("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL AND name NOT LIKE 'sqlite_autoindex%' ORDER BY rowid").all();
  d.close();
  return rows.map(r => r.sql.trim() + ";").join("\n") + "\n";
}
function tables(sqlText) {
  return [...String(sqlText).matchAll(/CREATE TABLE (?:IF NOT EXISTS )?"?([A-Za-z0-9_]+)"?/g)].map(m => m[1]).filter(n => n !== "sqlite_sequence").sort();
}

if (require.main === module) {
  const tmp = path.join(fs.mkdtempSync(path.join(os.tmpdir(), "lx-schema-")), "schema.db");
  process.env.LX_DB = tmp;
  process.env.LX_QUIET = "1";
  require("../lib/db.js");
  try { require("../lib/registry.js"); } catch (e) { }
  const out = dump(tmp);
  fs.writeFileSync(path.join(__dirname, "..", "schema.sql"), out);
  console.log("schema.sql regenerated — " + tables(out).length + " tables");
  for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(tmp + s, { force: true }); } catch (e) { } }
  process.exit(0);
}
module.exports = { dump, tables };
