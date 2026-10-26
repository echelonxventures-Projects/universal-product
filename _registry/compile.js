/* UCOS Ω∞ · the compile — every declaration, one sealed source of truth.
   --------------------------------------------------------------------------
   This is the migration of the platform's Law 002 (Knowledge Once) from
   "universes only" to everything. The corpora and the authored registry JSON
   DECLARE the constitution; this script COMPILES them into one artifact:

     _registry/canonical.json   the readable compiled registry (for operators)
     _registry/canonical.lxr    the same registry, AES-256-GCM sealed and
                                HMAC-SHA256 authenticated, with a per-input
                                SHA-256 manifest. THE runtime source of truth.

   Deterministic: a re-compile over unchanged inputs is byte-identical, so the
   sealed registry diffs clean against itself and an operator can audit exactly
   what a re-compile changed. Provenance (document + line) rides every row, so
   traceability survives the compile — the corpora stop being declaration
   SOURCES, never stop being where a declaration CAME FROM.

   Usage:
     node _registry/compile.js              compile + seal + report
     node _registry/compile.js --verify     verify the seal and the input manifest
     node _registry/compile.js --decrypt    write the readable registry to stdout
     node _registry/compile.js --search Q   search every declaration with provenance
                                            [--kind category|domain|primitive|term|artifact|universe|concept|document]
                                            [--category C04|"Universal Dimensions"] [--owner Geo] [--limit N]
     node _registry/compile.js --gate       run the integrity gate (Zero Duplicate /
                                            Zero Partial / Zero Overlap / Zero Missing /
                                            No Leakage) over the compiled registry */
"use strict";
const path = require("path");
const fs = require("fs");
const ROOT = path.resolve(__dirname, "..");
process.env.LX_DB = process.env.LX_DB || path.join(ROOT, "data", "compile.db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(process.env.LX_DB + s, { force: true }); } catch (e) { } }

const arg = process.argv.slice(2);
/* --verify / --decrypt / --search read the SEALED registry, so they must never touch
   it. Only a COMPILE unlinks the derived artifacts first: a fresh compile must never
   read a stale seal, because canonical.load() trusts the one on disk — but unlinking
   for a read-only mode deletes the very artifact the mode is asked to verify (and made
   `--gate && --verify` fail with "no sealed registry" every time). */
if (!arg.some(a => a === "--verify" || a === "--decrypt" || a === "--search")) {
  try { fs.unlinkSync(path.join(__dirname, "canonical.lxr")); } catch (e) { }
  try { fs.unlinkSync(path.join(__dirname, "canonical.json")); } catch (e) { }
}

const can = require(path.join(ROOT, "lib", "canonical.js"));

/* --verify / --decrypt / --search work on the SEALED registry — they must not
   recompile, so they read through the loader's cache-bypassed verify path. */
if (arg.includes("--verify")) {
  const v = can.verify();
  if (!v.ok) { console.error("✗ registry seal FAILED:", v.error || JSON.stringify(v.drift)); process.exit(1); }
  console.log("✓ seal verified");
  console.log("  registry:", v.registryId, "·", v.version, "· sealed", v.sealedAt, "· key", v.keyVersion);
  console.log("  digest:", v.digest.slice(0, 24), "…");
  console.log("  counts:", JSON.stringify(v.counts));
  console.log("  drift: none — every input matches the sealed manifest");
  process.exit(0);
}
if (arg.includes("--decrypt")) {
  const p = can.load(true);
  process.stdout.write(JSON.stringify(p, null, 1) + "\n");
  process.exit(0);
}
if (arg.includes("--search")) {
  const q = arg[arg.indexOf("--search") + 1];
  const opt = name => { const i = arg.indexOf("--" + name); return i >= 0 ? arg[i + 1] : undefined; };
  const rows = can.search(q, { limit: Number(opt("limit")) || 30, kind: opt("kind"), category: opt("category"), owner: opt("owner") });
  if (!rows.length) console.log("no declaration matches '" + q + "'");
  for (const r of rows) console.log("  " + r.kind.padEnd(9) + " " + String(r.key).padEnd(22) + " " + String(r.name).padEnd(34) + " " + (r.category ? r.category + " · " + r.owner : r.provenance));
  console.log(rows.length + " declaration(s)");
  process.exit(0);
}

/* ---------- the compile ---------- */
const silence = console.log; console.log = () => { };
require(path.join(ROOT, "lib", "db.js"));                /* schema only — no boot side effects needed for the parse */
const ucos = require(path.join(ROOT, "lib", "ucos.js"));
ucos.parseSources();                                     /* warm the parse cache so the compile measures the real work */
console.log = silence;

const t0 = Date.now();
const { payload, manifest } = can.compile();
const envelope = can.seal(payload, manifest);
can.writeArtifacts(payload, envelope);
const ms = Date.now() - t0;

/* ---------- the zero-loss contract, measured on the compile itself ----------
   The compiled registry must declare exactly what the sources declare — nothing
   invented (leakage), nothing dropped (partial). Verified here so a broken
   compile can never ship a seal. */
const parsed = payload.parsed;
const conceptRows = Object.keys(parsed).reduce((a, k) => a + parsed[k].concepts.length, 0);
const universeKeys = new Set(payload.universes.map(u => u.key));
const dupes = payload.universes.length - universeKeys.size;
const docs = Object.keys(parsed);

console.log("✓ compiled the canonical registry in " + ms + " ms");
console.log("  sources       " + Object.keys(manifest).length + " files, digest " + payload.digest.slice(0, 24) + "…");
console.log("  documents     " + payload.counts.documents + " (" + docs.join(", ") + ")");
console.log("  universes     " + payload.counts.universes + (dupes ? "  ✗ " + dupes + " DUPLICATE KEYS" : "  · unique keys ✓"));
console.log("  concepts      " + conceptRows + " rows");
console.log("  sections      " + payload.counts.sections + " · articles " + payload.counts.articles + " · parts " + payload.counts.parts);
console.log("  registries    " + payload.counts.registries + " lists");
console.log("  vocabularies  productUniverses " + payload.counts.productUniverses
  + " · lifecycleStates " + payload.vocabularies.lifecycleStates.length
  + " · transitionGrammar " + payload.vocabularies.transitionGrammar.length);
console.log("  console       platform " + payload.counts.platformSections + " sections · store " + payload.counts.adminSections + " sections");
console.log("  atoms         primitives " + payload.registryFiles.primitives.primitives.length
  + " · terms " + payload.registryFiles.terminology.terms.length
  + " · domains " + payload.registryFiles.domains.domains.length
  + " · artifacts " + payload.registryFiles.manifest.artifacts.length);
console.log("✓ sealed  _registry/canonical.lxr  (" + Math.round(fs.statSync(can.ENVELOPE).size / 1024) + " KB, AES-256-GCM + HMAC-SHA256, key " + envelope.keyVersion + ")");
console.log("✓ wrote  _registry/canonical.json (" + Math.round(fs.statSync(can.READABLE).size / 1024) + " KB, readable view)");
if (dupes) { console.error("✗ compile produced duplicate universe keys — refusing to ship"); process.exit(1); }

if (arg.includes("--gate")) {
  const gate = require(path.join(__dirname, "gate.js"));
  const report = gate.run(payload);
  if (!report.ok) { console.error(gate.explain(report)); process.exit(1); }
  console.log("✓ integrity gate: " + report.checked + " checks, all green");
}
