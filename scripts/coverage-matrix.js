/* The coverage matrix (GLOBAL_MASTER.md §8, roadmap P31): every type of platform in the master's
   platform_types vocabulary is configured from its setup answers alone, and discovery reports what
   it would still need that no capability provides. Prints one line per type; exits 1 while any type
   leaves something requested, so it is the gate the phase-9 engines are built against.
   Usage: node scripts/coverage-matrix.js [--json] */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os");
const TMP = path.join(os.tmpdir(), "coverage-" + process.pid + ".db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
process.env.LX_DB = TMP;
const silence = console.log; console.log = () => { };
require(path.join(__dirname, "..", "lib", "db.js"));
console.log = silence;
const M = require(path.join(__dirname, "..", "lib", "platform-master.js"));
const D = require(path.join(__dirname, "..", "lib", "platform-discovery.js"));
const SU = require(path.join(__dirname, "..", "lib", "platform-setup.js"));
const out = [];
for (const t of M.vocabulary(M.ROLES.platformTypes)) {
  let found = [], error = null;
  try { SU.check({ official: SU.options("official")[0].key, languages: [SU.options("languages")[0].key], currencies: [SU.options("currencies")[0].key], ...t.answers }); found = D.discover(t.answers); }
  catch (e) { error = e.message; }
  out.push({ type: t.name, title: t.title.en, requested: found.filter(f => !f.available).map(f => f.key), on: found.filter(f => f.available).length, error });
}
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
if (process.argv.includes("--json")) console.log(JSON.stringify(out, null, 1));
else for (const r of out) console.log((r.error ? "✗ " : r.requested.length ? "· " : "✓ ") + r.title.padEnd(42) + (r.error ? r.error : r.requested.length ? r.requested.length + " to build: " + r.requested.join(", ") : r.on + " capabilities, nothing requested"));
const open = out.filter(r => r.error || r.requested.length);
console.log(`\n${out.length - open.length} of ${out.length} types fully covered`);
process.exit(open.length ? 1 : 0);
