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
/* a stand-in session for the write-path checks (only .email is read by the annotation layer) */
const s0 = { email: "audit@luxora.shop" };
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
/* every document's container grammar is declared in ucos.DOCS; recount each one independently
   here (the registry is trusted for nothing) and let the assertions scale with the corpus.
   A registry document declares its containers in JSON, not text, so its recount reads the
   same JSON source files the runtime parses — never the seeded tables. */
const regMod = require(path.join(__dirname, "..", "lib", "ucos-registry.js"));
const expected = ucos.DOCS.map(d => ({
  id: d.id, kind: d.container,
  count: d.registry ? regMod.parseRegistry().sections.length : src(d.file, d.marker)
}));

ok(count("ucos_documents") === ucos.DOCS.length, "every constitutional document registered", count("ucos_documents") + " vs " + ucos.DOCS.length);
for (const e of expected) {
  const live = all("SELECT 1 FROM ucos_sections WHERE doc_id=? AND kind=?", e.id, e.kind).length;
  ok(live === e.count, e.id + ": every " + e.kind + " registered", live + " vs " + e.count);
}

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
/* no hardcoded concept list in the module: the documents it parses are its seed file
   (lib/seed/ucos.json), named by filename there and nowhere else */
const srcUcos = fs.readFileSync(path.join(__dirname, "..", "lib", "seed", "ucos.json"), "utf8");
ok(ucos.DOCS.every(d => srcUcos.includes(JSON.stringify(d.file))), "the seed file references every document by filename", ucos.DOCS.map(d => d.file).join(","));
const modUcos = fs.readFileSync(path.join(__dirname, "..", "lib", "ucos.js"), "utf8");
ok(!/const CONCEPTS\s*=/.test(modUcos) && !/const SECTIONS\s*=/.test(modUcos), "no hardcoded concept/section constant in the module");

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
ok(h.expected !== null && expected.every(e => { const x = h.expected[e.id]; return x && x.kind === e.kind && x.count === e.count; }), "expected counts derived from the documents, not constants", JSON.stringify(h.expected));
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

console.log("\n▸ WRITE PATH (annotations without mutating the documents)");
/* the annotation layer must key to canonical targets only, and must survive a re-parse */
const ann = ucos.annotations(db, "upip", "concept", "identity", 10, 0);
ok(Array.isArray(ann.rows), "annotations are read as a page", JSON.stringify(ann).slice(0, 40));
const made = ucos.addAnnotation(db, { email: "audit@luxora.shop" }, "upip", "concept", "identity", "Audit probe note", true);
ok(made.ok === true, "an annotation attaches to a real concept", JSON.stringify(made));
const listed = ucos.annotations(db, "upip", "concept", "identity", 10, 0);
ok(listed.total >= 1 && listed.rows[0].pin === 1, "the annotation is stored and pinned", "total=" + listed.total);
ok(listed.rows[0].created_by === "audit@luxora.shop", "the author is recorded", listed.rows[0].created_by);
/* guard: no annotation may be created against a target the registry does not contain */
const bogus = ucos.addAnnotation(db, s0, "upip", "concept", "no_such_concept_zzz", "should be refused", false);
ok(bogus.ok === false, "an annotation on a non-existent target is refused", JSON.stringify(bogus));
ok(/not present/.test(bogus.error), "the refusal names the missing target", bogus.error);
ok(ucos.addAnnotation(db, s0, "upip", "concept", "identity", "", false).ok === false, "an empty note is refused");
ok(ucos.addAnnotation(db, s0, "upip", "concept", "identity", "x".repeat(4001), false).ok === false, "an over-long note is refused");
ok(ucos.orphanedAnnotations(db).length === 0, "no orphaned annotations while targets exist", JSON.stringify(ucos.orphanedAnnotations(db)));
/* annotations survive a re-parse because they are keyed, not transcribed */
ucos.seed(db);
ok(ucos.annotations(db, "upip", "concept", "identity", 10, 0).total >= 1, "the annotation survives a re-parse", "total=" + ucos.annotations(db, "upip", "concept", "identity", 10, 0).total);
const aid = listed.rows[0].id;
ok(ucos.updateAnnotation(db, s0, aid, "revised note", false).ok === true, "an annotation can be edited");
ok(ucos.annotations(db, "upip", "concept", "identity", 10, 0).rows[0].note === "revised note", "the edit persisted");
ok(ucos.deleteAnnotation(db, s0, aid).ok === true, "an annotation can be deleted");
ok(ucos.deleteAnnotation(db, s0, aid).ok === false, "deleting twice is reported as not-found");
ok(ucos.annotations(db, "upip", "concept", "identity", 10, 0).total === 0, "all test annotations cleaned up");

console.log("\n▸ FOUNDATION COMPLETENESS (the corpus's own freeze criteria, executable)");
const comp = require(path.join(__dirname, "..", "lib", "ucos-completeness.js"));
const audit = comp.audit();
ok(Array.isArray(audit.criteria) && audit.criteria.length === 5, "the five 17AH.7 criteria are evaluated", JSON.stringify(audit.criteria.map(c => c.kind)));
ok(audit.criteria.every(c => typeof c.satisfied === "boolean"), "every criterion reports a boolean verdict", "");
ok(comp.dependencyGaps().length === 0, "no unresolved dependency gaps — every referenced document exists", "count=" + comp.dependencyGaps().length);
ok(comp.separationGaps().length === 0, "no unresolved separation gaps", "count=" + comp.separationGaps().length);
ok(comp.orderingGaps().length === 0, "no unresolved ordering gaps", "count=" + comp.orderingGaps().length);
/* DOC-008 regression: its articles carried DOC-009's id because docMeta was shared by reference */
const idx = comp.masterIndex();
ok(idx.totals.unattributed === 0, "every article attributes to a declared document", "unattributed=" + idx.totals.unattributed);
const d8 = idx.documents.find(d => d.docId === "UMQSOCR-DOC-008");
ok(!!d8 && d8.articles === 20, "UMQSOCR-DOC-008 is present with its own 20 articles (docMeta-alias regression)", d8 ? "articles=" + d8.articles : "MISSING");
const d9 = idx.documents.find(d => d.docId === "UMQSOCR-DOC-009");
ok(!!d9 && d9.articles === 20, "UMQSOCR-DOC-009 owns exactly 20 (not the leaked 40)", d9 ? "articles=" + d9.articles : "MISSING");
ok(idx.documents.length >= 24, "the master index enumerates the corpus's declared documents", "documents=" + idx.documents.length);
const corpusArticles = expected.filter(e => e.kind === "article").reduce((a, e) => a + e.count, 0);
ok(idx.totals.articles === corpusArticles, "the index accounts for every article in the corpus", "articles=" + idx.totals.articles + " vs " + corpusArticles);
/* each UCOS document block must surface as its own indexed document — the index is keyed by
   declared document, not by source file, so a new constitution must not vanish into "(unattributed)" */
const ucosDeclared = src("Architecture3.txt", /^#\s+DOCUMENT\s*$/);
const ucosIndexed = idx.documents.filter(d => /^UCOS-DOC-/.test(String(d.docId))).length;
ok(ucosIndexed === ucosDeclared, "every UCOS document block appears in the master index", ucosIndexed + " vs " + ucosDeclared);

/* ---------- NEGATIVE TESTS ----------
   A green audit is meaningless if the criteria cannot see a real violation, so each is probed
   with a synthetic conflict and the registry restored byte-exact afterwards. */
console.log("\n▸ COMPLETENESS DETECTOR (the criteria must still bite)");
const probeName = "Authority Probe Measurement";
const probeRows = [
  ["umqscr", "ap1", probeName, "section", "c_probe_a", "DOC-A", 1, 1],
  ["umqscr", "ap2", probeName, "section", "c_probe_b", "DOC-B", 1, 2]
];
db.run("DELETE FROM ucos_concepts WHERE name=?", probeName);
probeRows.forEach(r => db.run("INSERT INTO ucos_concepts(doc_id,key,name,container_kind,container_key,container_name,part_no,line) VALUES(?,?,?,?,?,?,?,?)", ...r));
try {
  ok(comp.authorityGaps().some(g => g.concept === probeName), "authority flags the same concept owned twice in one family", "gaps=" + comp.authorityGaps().length);
  const during = comp.audit();
  ok(during.ok === false, "the freeze verdict flips to unsatisfied under a real conflict", during.verdict.slice(0, 40));
  ok(during.criteria.some(c => c.kind === "authority" && !c.satisfied), "the authority criterion reports itself unsatisfied");
} finally {
  db.run("DELETE FROM ucos_concepts WHERE name=?", probeName);
}
ok(comp.audit().ok === true, "the registry returns to a freezable state once the probe is removed");
ok(comp.authorityGaps().length === 0, "no authority gaps remain after cleanup", "count=" + comp.authorityGaps().length);

console.log("\n" + (failed ? "✗ " + failed + " check(s) failed" : "✓ all UCOS Ω∞ checks passed") + "  (" + passed + " passed)");
process.exit(failed ? 1 : 0);
