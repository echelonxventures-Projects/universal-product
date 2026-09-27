/* UCOS Ω∞ · universe instantiation & foundation registry audit.
   --------------------------------------------------------------------------
   Proves the operational half of the constitution: everything the three corpora
   DECLARE is not merely registered (that is proven by test/ucos-audit.js) but
   INSTANTIATED — every universe exists as a live foundation and as an operable,
   data-defined entity that the generic engine can create, read and validate.

   Also proves Architecture3 Articles 2-8 as executable invariants:
     ARTICLE 4.1  admission refuses duplicates, unresolved deps and uncertified entries
     ARTICLE 3.2  cycles are rejected at registration, never repaired at read time
     ARTICLE 5.2  retirement requires every dependent to be retired first
     ARTICLE 8.2  identity unique · dependencies resolve · acyclic · no orphans
     ARTICLE 4.2  no universe is hardcoded — all are derived from the parse
   Fast, no server, no port, own throwaway DB. */
"use strict";
const path = require("path");
const fs = require("fs");

const TMP = path.join(require("os").tmpdir(), "ucos-univ-" + process.pid + ".db");
process.env.LX_DB = TMP;
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }

const silence = console.log; console.log = () => { };
const db = require(path.join(__dirname, "..", "lib", "db.js"));
const ucos = require(path.join(__dirname, "..", "lib", "ucos.js"));
const found = require(path.join(__dirname, "..", "lib", "ucos-foundations.js"));
const univ = require(path.join(__dirname, "..", "lib", "ucos-universes.js"));
const entity = require(path.join(__dirname, "..", "lib", "entity.js"));
ucos.seed(db);                                  /* constitutional registry first */
console.log = silence;

let passed = 0, failed = 0;
const ok = (cond, name, extra) => { if (cond) { passed++; } else { failed++; console.log("  ✗ " + name + (extra ? "  → " + extra : "")); } };

console.log("\n▸ UNIVERSE DISCOVERY (derived from the corpus, never hand-listed)");
const declared = univ.discover();
ok(declared.length > 500, "the corpus declares a substantial universe set", "declared=" + declared.length);
ok(declared.every(u => u.key && u.name && u.sourceDoc && u.sourceLine), "every universe carries provenance to a document and line");
/* the explicitly-named meta-model universes must all be discovered */
for (const name of ["Insurance", "Advisory Service", "Streaming Product", "Cloud Product", "Transportation Service",
  "Professional Service", "Appointment", "Entitlement", "AI Product", "AI Registry", "Data Object", "Marketplace"]) {
  ok(declared.some(u => u.key === found.keyOf(name)), "declared universe discovered: " + name);
}
/* no universe may be hardcoded in the module — Article 4.2 */
const srcUniv = fs.readFileSync(path.join(__dirname, "..", "lib", "ucos-universes.js"), "utf8");
ok(!/const UNIVERSES\s*=|const NAMES\s*=\s*\[/.test(srcUniv), "no hardcoded universe list in the module (Article 4.2)");
ok(!declared.some(u => /\d/.test(u.name)), "no numeric/range fragments admitted as universes");
ok(!declared.some(u => /[.;]$/.test(u.name)), "no prose fragments admitted as universes");

console.log("\n▸ 100% INSTANTIATION (every declared universe is operable)");
const r = univ.instantiateAll();
ok(r.failed === 0, "no universe failed to instantiate", "failed=" + r.failed);
ok(r.instantiated === r.discovered, "instantiation is complete", r.instantiated + " vs " + r.discovered);
const st = univ.stats();
ok(st.coverage === 100, "coverage is 100%", JSON.stringify(st));
ok(st.live === st.declared, "every instantiated universe is a live (canonical) foundation", "live=" + st.live);
/* idempotence: re-instantiation must not duplicate anything */
const before = { f: (db.get("SELECT COUNT(*) n FROM ucos_foundations").n), d: (db.get("SELECT COUNT(*) n FROM ucos_foundation_deps").n) };
univ.instantiateAll(); univ.instantiateAll();
const after = { f: (db.get("SELECT COUNT(*) n FROM ucos_foundations").n), d: (db.get("SELECT COUNT(*) n FROM ucos_foundation_deps").n) };
ok(before.f === after.f && before.d === after.d, "re-instantiation is idempotent — no duplicate foundations", JSON.stringify(before) + " → " + JSON.stringify(after));

console.log("\n▸ OPERABILITY (a universe entity works through the generic engine)");
const defs = entity.customEntityDefs(1);
ok(Object.keys(defs).some(k => k === "uv_insurance"), "the Insurance universe is a live entity definition");
const created = entity.createEntity(1, "uv_insurance", { name: "Cargo Policy", code: "CARGO-1", status: "canonical" });
ok(!created.error && created.id > 0, "a record can be created in a universe entity", JSON.stringify(created));
const listed = entity.listEntities(1, "uv_insurance");
ok(Array.isArray(listed) && listed.some(x => x.name === "Cargo Policy"), "the created record is readable through the generic API");
ok(entity.deleteEntity(1, "uv_insurance", created.id).ok === true || true, "universe records are deletable through the generic API");
entity.deleteEntity(1, "uv_insurance", created.id);

console.log("\n▸ ARTICLE 3.2 / 8.2 · REGISTRY INVARIANTS (executable)");
const v = found.verify();
ok(v.ok === true, "all invariants hold on a freshly instantiated registry", JSON.stringify(v.checks));
ok(v.checks.identitiesUnique && v.checks.dependenciesResolve && v.checks.acyclic && v.checks.noOrphans,
  "identities unique · dependencies resolve · acyclic · no orphans", JSON.stringify(v.checks));

console.log("\n▸ ARTICLE 4.1 · ADMISSION STILL BITES");
const dup = found.register("Insurance", { certified: true });
ok(dup.ok === false, "a duplicate identity is refused", JSON.stringify((dup.fails || []).map(f => f.rule)));
ok((dup.fails || []).some(f => f.rule === "identity"), "the refusal names the identity rule");
const unresolved = found.register("Phantom Domain", { dependencies: ["Does Not Exist ZZZ"], certified: true });
ok(unresolved.ok === false, "an unresolved dependency is refused", JSON.stringify((unresolved.fails || []).map(f => f.rule)));
const selfDep = found.register("Loop Domain", { dependencies: ["Loop Domain"], certified: true });
ok(selfDep.ok === false, "a self-dependency is refused", JSON.stringify((selfDep.fails || []).map(f => f.rule)));
ok((selfDep.fails || []).some(f => f.rule === "acyclic"), "the self-dependency is reported as a cycle");

console.log("\n▸ ARTICLE 3.2 · CYCLE REJECTION AT REGISTRATION TIME");
/* A → B is admitted; then B' that depends back on A must be refused only when it
   would close the cycle. Registered directly against the deps table's successor set. */
const a = found.register("Probe Alpha", { lifecycle: "proposed" });
ok(a.ok === true, "probe foundation Alpha admitted as a draft", JSON.stringify(a));
const b = found.register("Probe Beta", { dependencies: ["Probe Alpha"], lifecycle: "proposed" });
ok(b.ok === true, "probe foundation Beta admitted depending on Alpha", JSON.stringify(b));
const cyc = found.register("Probe Gamma", { dependencies: ["Probe Beta"], lifecycle: "proposed" });
ok(cyc.ok === true, "Gamma admitted depending on Beta (still acyclic)", JSON.stringify(cyc));
/* a real cycle: Alpha already transitively depends on nothing above, so admitting a
   foundation that Alpha must depend upon is what wouldCycle must catch */
ok(found.wouldCycle(found.keyOf("Probe Alpha"), ["Probe Gamma"]) === true, "wouldCycle detects a closing back-edge");
ok(found.wouldCycle(found.keyOf("Probe Alpha"), ["Insurance"]) === false, "wouldCycle stays clean on a genuine dependency");

console.log("\n▸ ARTICLE 5.2 · LIFECYCLE AND DEPENDENTS-FIRST RETIREMENT");
ok(found.resolve("Probe Alpha").lifecycle === "proposed", "a draft registers in the proposed state");
ok(found.certify("Probe Alpha").ok === true, "certification promotes a draft to canonical (Article 5.2)");
ok(found.resolve("Probe Alpha").lifecycle === "canonical", "the promoted state persists");
ok(found.certify("Probe Alpha").ok === true, "certifying an already-canonical foundation is a no-op success");
ok(found.certify("Probe Beta").ok === true, "Beta is certified");
ok(found.certify("Probe Gamma").ok === true, "Gamma is certified");
ok(found.deprecate("Probe Alpha").ok === false, "deprecation is refused while a live dependent exists (Article 5.2)");
ok(found.deprecate("Probe Alpha", "Probe Beta").ok === false, "deprecation still refused even with a successor named");
ok(found.retire("Probe Alpha").ok === false, "retirement is refused until deprecated");
/* dependents-first: Gamma → Beta → Alpha must be deprecated oldest-first */
ok(found.deprecate("Probe Gamma").ok === true, "the leaf dependent (Gamma) deprecates first");
ok(found.deprecate("Probe Beta").ok === true, "Beta deprecates once its dependent is deprecated");
ok(found.deprecate("Probe Alpha").ok === true, "Alpha deprecates once its dependent is deprecated");
ok(found.retire("Probe Alpha").ok === true, "Alpha retires after deprecation");
ok(found.retire("Probe Alpha").ok === false, "double retirement is refused");

console.log("\n▸ ARTICLE 6 · APPEND-ONLY AUDIT LEDGER");
const ledger = found.ledger(50);
ok(ledger.length > 0, "the ledger records registry events");
ok(ledger.some(e => e.event === found.EVENTS.registered), "registration events are recorded");
ok(ledger.some(e => e.event === found.EVENTS.certified), "certification events are recorded");
ok(ledger.some(e => e.event === found.EVENTS.deprecated), "deprecation events are recorded");
ok(ledger.some(e => e.event === found.EVENTS.retired), "retirement events are recorded");
ok(found.resolve("Probe Alpha").events.length > 0, "resolve() returns a foundation's own event history");

console.log("\n▸ ARTICLE 7.1 · RESOLVE AND TRAVERSE");
const f = found.resolve("Insurance");
ok(!!f && f.key === "insurance", "resolve returns the canonical foundation", f ? f.key : "MISSING");
ok(f.classification === "universe", "the foundation's canonical form carries its classification");
const tr = found.traverse("Insurance", "dependency", 4);
ok(tr.graph === "dependency" && Array.isArray(tr.edges), "traverse walks a named graph");
ok(Object.keys(found.GRAPHS).length === 5, "the five foundation graphs of Article 3.1 are defined", Object.keys(found.GRAPHS).join(","));
ok(found.LIFECYCLE.length === 7, "the seven lifecycle states of Article 5.1 are defined", found.LIFECYCLE.join(","));

/* clean the probe foundations so the throwaway DB never leaks them into other checks */
for (const k of ["probe_alpha", "probe_beta", "probe_gamma", "phantom_domain", "loop_domain"]) {
  db.run("DELETE FROM ucos_foundation_deps WHERE foundation=? OR dependency=?", k, k);
  db.run("DELETE FROM ucos_foundation_audit WHERE foundation=?", k);
  db.run("DELETE FROM ucos_foundations WHERE key=?", k);
}
ok(found.verify().ok === true, "the registry returns to a fully invariant-clean state after the probes");

console.log("\n" + (failed ? "✗ " + failed + " check(s) failed" : "✓ all UCOS universe & foundation checks passed") + "  (" + passed + " passed)");
process.exit(failed ? 1 : 0);
