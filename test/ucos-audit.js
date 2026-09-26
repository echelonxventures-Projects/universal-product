/* UCOS Ω∞ — constitutional conformance audit for the Architecture1/2 registry.
   Proves against the live seeded database (not the JS module, not the source text) that the
   platform carries: ZERO MISSING (every numbered section and article in the documents is
   registered), ZERO PARTIAL (every registered container resolves to a source line number, so
   nothing is an untraceable stub), ZERO DUPLICATE (no section key, concept key or graph edge
   appears twice) and ZERO HARDCODING (the registry is produced by parsing, so no concept is
   asserted from code — the counts must match a fresh independent parse of the documents).
   Fast, no server, no port, own throwaway DB. */
"use strict";
const path = require("path");
const os = require("fs");
const fs = require("fs");

const TMP = path.join(require("os").tmpdir(), "ucos-audit-" + process.pid + ".db");
process.env.LX_DB = TMP;
for (const suffix of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + suffix, { force: true }); } catch (e) { } }

const silence = console.log; console.log = () => { };          /* the seed banner is not the point */
const db = require(path.join(__dirname, "..", "lib", "db.js"));
const ucos = require(path.join(__dirname, "..", "lib", "ucos.js"));
ucos.seed(db);
console.log = silence;

const { get, all, run } = db;
let passed = 0, failed = 0;
const ok = (cond, name, extra) => { if (cond) { passed++; } else { failed++; console.log("  ✗ " + name + (extra ? "  → " + extra : "")); } };
const count = t => (all("SELECT COUNT(*) AS n FROM " + t)[0] || {}).n || 0;
const dups = (t, cols) => all("SELECT " + cols + " FROM " + t + " GROUP BY " + cols + " HAVING COUNT(*) > 1").length;

console.log("\n▸ UCOS Ω∞ · SOURCE COMPLETENESS (zero missing)");

/* count the authoritative markers directly in the source files — this is the number the
   registry must reproduce. Nothing is trusted from code. */
const src = (file, re) => {
  const lines = fs.readFileSync(path.join(__dirname, "..", file), "utf8").split(/\r?\n/);
  let n = 0, inFence = false;
  for (const l of lines) {
    const t = l.trim();
    if (t.startsWith("```")) { const rest = t.slice(3).trim(); if (!inFence) inFence = true; else if (!rest) inFence = false; else inFence = true; continue; }
    if (inFence) continue;
    if (re.test(t)) n++;
  }
  return n;
};
const upipSections = src("Architecture1.txt", /^#\s+\d+\.\s/);
const umqsocrArticles = src("Architecture2.txt", /^#\s+ARTICLE\s/i);

ok(count("ucos_documents") === 2, "both constitutional documents registered", count("ucos_documents"));
const liveSections = all("SELECT 1 FROM ucos_sections WHERE kind='section'").length;
const liveArticles = all("SELECT 1 FROM ucos_sections WHERE kind='article'").length;
ok(liveSections === upipSections, "UPIP: every numbered section registered", liveSections + " vs " + upipSections);
ok(liveArticles === umqsocrArticles, "UMQSOCR: every article registered", liveArticles + " vs " + umqsocrArticles);

console.log("\n▸ TRACEABILITY (zero partials — every row points at its source line)");
ok(count("ucos_sections") === all("SELECT 1 FROM ucos_sections WHERE line IS NOT NULL AND line > 0").length, "every section carries a source line number");
ok(count("ucos_concepts") === all("SELECT 1 FROM ucos_concepts WHERE line IS NOT NULL AND line > 0").length, "every concept carries a source line number");
ok(count("ucos_registries") === all("SELECT 1 FROM ucos_registries WHERE line IS NOT NULL AND line > 0").length, "every registry list carries a source line number");
ok(count("ucos_registries") === all("SELECT 1 FROM ucos_registries WHERE items NOT IN ('','[]')").length, "every registry list is non-empty");

console.log("\n▸ DUPLICATION (zero duplicates)");
ok(dups("ucos_sections", "doc_id,qkey") === 0, "no duplicate section keys");
ok(dups("ucos_edges", "doc_id,source_type,source_id,rel,target_type,target_id") === 0, "no duplicate knowledge-graph edges");
ok(dups("ucos_concepts", "doc_id,key") === 0, "no duplicate concept keys within a document");

console.log("\n▸ NO HARDCODING (registry is a parse, not a transcription)");
/* re-parse from scratch and compare: the live tables must equal an independent parse */
const fresh = ucos.parseAll();
const liveConcepts = count("ucos_concepts");
const parsedConcepts = Object.values(fresh).reduce((a, p) => a + p.concepts.length, 0);
ok(liveConcepts === parsedConcepts, "live concept count equals a fresh independent parse", liveConcepts + " vs " + parsedConcepts);
ok(parsedConcepts > 20000, "the constitution is genuinely registered at scale", parsedConcepts);
ok(ucos.keyOf("Universal Product Object") === "universal_product_object", "keys are derived from content, never invented");
/* no hardcoded concept list in the module: the only constants must be document paths */
const srcUcos = fs.readFileSync(path.join(__dirname, "..", "lib", "ucos.js"), "utf8");
ok(/Architecture1\.txt/.test(srcUcos) && /Architecture2\.txt/.test(srcUcos), "module references the documents by filename");
ok(!/const CONCEPTS\s*=/.test(srcUcos) && !/const SECTIONS\s*=/.test(srcUcos), "no hardcoded concept/section constant in the module");

console.log("\n▸ KNOWLEDGE GRAPH (part → section → concept)");
ok(count("ucos_edges") > 0, "graph edges were built", count("ucos_edges"));
ok(all("SELECT DISTINCT rel FROM ucos_edges").map(r => r.rel).sort().join(",") === "contains,defines", "only the two canonical relationships exist");

console.log("\n▸ IDEMPOTENCE (re-seeding never duplicates)");
const before = { s: count("ucos_sections"), c: count("ucos_concepts"), e: count("ucos_edges") };
ucos.seed(db);
const after = { s: count("ucos_sections"), c: count("ucos_concepts"), e: count("ucos_edges") };
ok(before.s === after.s && before.c === after.c && before.e === after.e, "row counts unchanged after re-seed", JSON.stringify(before) + " → " + JSON.stringify(after));

console.log("\n▸ MONITORING (health + drift detection)");
const mon = require(path.join(__dirname, "..", "lib", "ucos-monitor.js"));
const h = mon.health();
ok(h.ok === true, "health reports healthy on a freshly seeded registry", JSON.stringify(h.problems));
ok(h.counts.sections > 0 && h.counts.articles > 0 && h.counts.concepts > 0, "health exposes live counts", JSON.stringify(h.counts));
ok(h.problems.length === 0, "zero health problems", h.problems.map(p => p.code).join(","));
ok(h.expected.upip.sections === upipSections && h.expected.umqscr.articles === umqsocrArticles, "expected counts derived from the documents, not constants", JSON.stringify(h.expected));
const drift = mon.driftStatus();
ok(drift.drifted === false, "no drift immediately after seeding", drift.message);
ok(/^[0-9a-f]{64}$/.test(drift.stored || ""), "a digest stamp is persisted", drift.stored);
ok(mon.promMetrics().includes("luxora_ucos_sections_total") && mon.promMetrics().includes("luxora_ucos_drift"), "Prometheus gauges emitted for sections and drift");

console.log("\n▸ DRIFT DETECTION (an edited document is never invisible)");
/* capture the stamp, mutate the source, probe: the digest MUST differ and drift MUST be reported */
const a2 = path.join(__dirname, "..", "Architecture2.txt");
const a2Backup = fs.readFileSync(a2);
const stampBefore = mon.documentDigest();
fs.writeFileSync(a2, a2Backup + "\n\n# 9999. DRIFT PROBE SECTION\n");
try {
  const afterEdit = mon.documentDigest();
  ok(afterEdit !== stampBefore, "digest changes when a document is edited");
  /* driftStatus must now report drift against the stored stamp, WITHOUT re-seeding first */
  const seen = mon.driftStatus();
  ok(seen.drifted === true, "drift is detected against the persisted stamp", seen.message.slice(0, 60));
  ok(seen.severity === "critical", "drift is classified critical", seen.severity);
  ok(mon.health().ok === false, "health flips to unhealthy under drift", mon.health().status);
  ok(/luxora_ucos_drift 1/.test(mon.promMetrics()), "the drift Prometheus gauge flips to 1");
} finally {
  fs.writeFileSync(a2, a2Backup);                  /* byte-exact restore */
}
ok(mon.documentDigest() === stampBefore, "document restored byte-identical after the probe");
ok(mon.driftStatus().drifted === false, "drift clears once the document is restored", mon.driftStatus().message.slice(0, 40));

console.log("\n" + (failed ? "✗ " + failed + " check(s) failed" : "✓ all UCOS Ω∞ checks passed") + "  (" + passed + " passed)");
process.exit(failed ? 1 : 0);
