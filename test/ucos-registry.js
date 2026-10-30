/* UCOS Ω∞ · the frozen registry as a runtime corpus source.
   --------------------------------------------------------------------------
   Before lib/ucos-registry.js, `_registry/*.json` was a PARALLEL source of
   truth: `_registry/project.js` projected 93 markdown artifacts from it while
   the runtime derived everything from the corpora, and neither world knew the
   other existed — a Law 002 (Knowledge Once) violation hiding in plain sight.

   This proves the unification: the registry is now a first-class corpus
   document (DOCS row `ureg`), parsed by the same contract, seeded through the
   same path, discovered by the same walk and instantiated by the same engine.
   The artifacts stop being markdown nothing reads and become live universes;
   the primitives become platform vocabulary; the cross-source overlap stops
   being silent and becomes measured.

     LAW 002   one definition per concept — the registry's own artifacts do
               not duplicate corpus universes, and the 2 that share a key with
               a corpus universe resolve to ONE row (first-wins, provenance kept)
     LAW 003   projection — primitives/terms/domains are registered concepts;
               the artifacts are their live projections
     LAW 001   zero hardcoding — the module holds no concept names; everything
               is read from the registry files
   Fast, no server, no port, own throwaway DB. */
"use strict";
const path = require("path");
const fs = require("fs");

const TMP = path.join(require("os").tmpdir(), "ucos-reg-" + process.pid + ".db");
process.env.LX_DB = TMP;
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }

const silence = console.log; console.log = () => { };
const db = require(path.join(__dirname, "..", "lib", "db.js"));
const ucos = require(path.join(__dirname, "..", "lib", "ucos.js"));
const found = require(path.join(__dirname, "..", "lib", "ucos-foundations.js"));
const univ = require(path.join(__dirname, "..", "lib", "ucos-universes.js"));
const reg = require(path.join(__dirname, "..", "lib", "ucos-registry.js"));
const entity = require(path.join(__dirname, "..", "lib", "entity.js"));
ucos.seed(db);
console.log = silence;

let passed = 0, failed = 0;
const ok = (cond, name, extra) => { if (cond) { passed++; } else { failed++; console.log("  ✗ " + name + (extra ? "  → " + extra : "")); } };
const key = found.keyOf;

console.log("\n▸ THE REGISTRY IS A CORPUS DOCUMENT (one parse contract, one seed path)");
const P = ucos.parseAll();
ok(!!P.ureg, "the registry parses as a corpus document");
ok(P.ureg && P.ureg.sections.length >= 4, "it declares its four registries as sections", P.ureg && P.ureg.sections.length);
ok(P.ureg && P.ureg.concepts.length > 100, "its primitives/terms/domains/artifacts register as concepts", P.ureg && P.ureg.concepts.length);
ok(P.ureg && P.ureg.registries.some(r => r.label === "Frozen Primitives"), "the frozen-primitives registry list is present");
ok(P.ureg && P.ureg.registries.some(r => r.label === "Canonical Terms"), "the canonical-terms registry list is present");
ok(P.ureg && P.ureg.registries.some(r => r.label === "Domain Ownership"), "the domain-ownership registry list is present");
ok(P.ureg && P.ureg.registries.some(r => r.label === "Declared Artifacts"), "the artifact declaration list is present");
/* the corpus sees it too — the registry is no longer a parallel source */
ok(ucos.manifest().documents.some(d => d.id === "ureg"), "the registry appears in the corpus manifest");

console.log("\n▸ LAW 001 — ZERO HARD CODING (the module holds no concept names)");
const src = fs.readFileSync(path.join(__dirname, "..", "lib", "ucos-registry.js"), "utf8");
ok(!/const (PRIMITIVES|NAMES|CONCEPTS)\s*=\s*\[/.test(src), "no hardcoded concept or primitive list");
ok(!/"(?:Identity|Knowledge|Trust|Policy|Time)"\s*,\s*"/.test(src), "the module enumerates no primitive names");
/* every concept the registry emits must be traceable to a JSON file, never to a literal */
const declared = reg.primitives().map(p => p.name)
  .concat(reg.terms().map(t => t.canonicalName))
  .concat(reg.domains().map(d => d.name))
  .concat(reg.artifacts().map(a => a.title));
ok(declared.length > 100, "the registry declares a substantial concept set", declared.length);
const fromParse = P.ureg.concepts.map(c => c.name);
for (const name of ["Identity", "Knowledge", "Trust", "Policy", "Time", "Constitutional Foundation", "Identity Architecture"]) {
  const inRegistry = declared.some(n => n === name);
  const inParse = fromParse.some(n => n === name);
  ok(inRegistry === inParse, "the parse and the registry agree on: " + name, inRegistry + " vs " + inParse);
}

console.log("\n▸ THE 93 ARTIFACTS ARE LIVE ENGINES, NOT MARKDOWN (Law 003 projection)");
const arts = reg.artifacts();
ok(arts.length === 111, "the manifest declares 111 artifacts (93, the 17 domain contracts of AMD-0002 and Party's of AMD-0004)", arts.length);
const artKeys = new Set(arts.map(a => key(a.title)));
const discovered = univ.discover();
const artUniverses = discovered.filter(u => u.sourceDoc === "ureg");
/* 2 artifacts share a key with a corpus universe (Agent Runtime, Agent Governance) and
   resolve first-wins to the CORPUS row — Knowledge Once, provenance kept — so the honest
   count of ureg-sourced universes is 93 minus the collisions, and the artifact's universe
   exists either way. Asserting all 93 came from ureg would contradict the overlap section
   below, which proves the two collisions resolve to one row. */
const collisions = arts.filter(a => { const u = discovered.find(x => x.key === key(a.title)); return u && u.sourceDoc !== "ureg"; });
ok(artUniverses.length === arts.length - collisions.length, "every artifact is discovered as a universe (the colliding ones resolve first-wins to the corpus)",
  artUniverses.length + " ureg-sourced + " + collisions.length + " corpus-resolved = " + arts.length);
ok(arts.every(a => discovered.some(u => u.key === key(a.title))), "no artifact is left without a universe");
ok(artUniverses.every(u => u.sourceLine > 0), "every artifact universe carries its provenance line");
const r = univ.instantiateAll();
ok(r.failed === 0, "no artifact failed to instantiate", "failed=" + r.failed);
const defs = entity.customEntityDefs(1);
let rich = 0;
for (const a of arts) {
  const ek = "uv_" + key(a.title);
  const def = db.get("SELECT def FROM entity_defs WHERE key=?", ek);
  if (!def) { ok(false, "artifact has a live entity definition: " + a.title); continue; }
  let d = {}; try { d = JSON.parse(def.def || "{}"); } catch (e) { }
  ok(!!d.label && Array.isArray(d.fields) && d.fields.length >= 4, "artifact is a data-defined entity: " + a.title,
    d.label + " · " + (d.fields || []).length + " fields");
  if ((d.fields || []).length > 4) rich++;
}
ok(rich === arts.length, "every artifact's fields are derived from its own content block (not a generic shell)",
  rich + " of " + arts.length);

console.log("\n▸ OPERABILITY (an artifact universe works through the generic engine)");
const probe = "Identity Architecture";
const ek = "uv_" + key(probe);
ok(Object.keys(defs).some(k => k === ek), "the Identity artifact is exposed by the generic entity engine");
const created = entity.createEntity(1, ek, { name: "Regional Identity Service", code: "IDN-REGION-1", status: "canonical" });
ok(!created.error && created.id > 0, "a record can be created in an artifact universe", JSON.stringify(created));
const listed = entity.listEntities(1, ek);
ok(Array.isArray(listed) && listed.some(x => x.name === "Regional Identity Service"), "the record is readable through the generic API");
ok(!!defs[ek] && defs[ek].fields.some(f => f.key === "ontology" || f.key === "taxonomy"), "the artifact's own declared sections are its entity fields");

console.log("\n▸ LAW 002 — ZERO DUPLICATE (one definition per concept, measured in the runtime)");
/* the registry's own artifacts must not create second rows for concepts a
   corpus already owns; the 2 that collide resolve first-wins to the corpus */
const dupKeys = arts.map(a => key(a.title)).filter(k => discovered.filter(u => u.key === k).length > 1);
ok(dupKeys.length === 0, "no artifact creates a duplicate universe key", dupKeys.join(", "));
ok(found.verify().ok === true, "the whole foundation registry stays unique, resolved, acyclic and orphan-free",
  JSON.stringify(found.verify().checks));
ok(db.get("SELECT COUNT(*) n FROM ucos_universes").n === discovered.length,
  "the live registry equals the discovered set exactly");
/* idempotence: re-running never multiplies */
const before = { f: db.get("SELECT COUNT(*) n FROM ucos_foundations").n, u: db.get("SELECT COUNT(*) n FROM ucos_universes").n };
univ.instantiateAll(); univ.instantiateAll();
const after = { f: db.get("SELECT COUNT(*) n FROM ucos_foundations").n, u: db.get("SELECT COUNT(*) n FROM ucos_universes").n };
ok(before.f === after.f && before.u === after.u, "re-instantiation adds no foundation or universe rows",
  JSON.stringify(before) + " → " + JSON.stringify(after));

console.log("\n▸ THE OVERLAP IS MEASURED, NOT SILENT (Law 002's real test)");
/* The doc-side audit cannot see the corpora; this does. A registry concept whose
   key a corpus also declares as a universe is the same name at two layers — not a
   defect, but it MUST be visible, because a silent overlap is how Knowledge Once
   actually breaks. The 2 artifact collisions must resolve to the corpus's row. */
const ov = reg.overlap();
ok(ov.overlapCount > 0, "the cross-source overlap is reported, never hidden", "n=" + ov.overlapCount);
ok(ov.overlap.every(o => o.registryName && o.universeName && o.sourceDoc), "every overlap names both definitions and the corpus source");
for (const name of ["Agent Runtime", "Agent Governance"]) {
  const hit = ov.overlap.find(o => o.universeName === name);
  ok(!!hit, "the colliding artifact is reported: " + name);
  if (hit) {
    const f = found.resolve(key(name));
    ok(!!f && f.classification === "universe", "the collision resolves to ONE foundation (first-wins, the corpus keeps it)",
      f && f.source_doc);
  }
}
/* the primitives that collide with corpus universes stay live either way */
for (const name of ["Identity", "Knowledge", "Time"]) {
  ok(ov.overlap.some(o => o.key === key(name) && o.kind === "primitive"), "a frozen primitive that a corpus also projects is reported: " + name);
  ok(!!found.resolve(key(name)), "the primitive resolves to a real foundation in the runtime: " + name);
}

console.log("\n▸ THE VOCABULARIES ARE PLATFORM VOCABULARY (meta_lists)");
const lists = reg.seedLists(db);
ok(lists.constitutionalPrimitives === 27, "all 27 frozen primitives seeded as a registry list", lists.constitutionalPrimitives);
ok(lists.canonicalTerms > 0, "the canonical terms are seeded", lists.canonicalTerms);
ok(lists.constitutionalDomains > 0, "the domains are seeded", lists.constitutionalDomains);
const row = db.get("SELECT items FROM meta_lists WHERE name='constitutionalPrimitives'");
let arr = []; try { arr = JSON.parse(row.items || "[]"); } catch (e) { }
ok(arr.length === 27, "the primitive list round-trips through the registry store", arr.length);
ok(arr.every(p => p.key && p.name), "every seeded primitive carries a key and a name");
ok(arr.some(p => p.frozen === true), "the frozen flag survives the seeding (an amendment is visible)");
/* additive: an operator's addition survives a re-seed. The operator edits the EXISTING
   list (meta_lists.name is UNIQUE — there is one row per vocabulary), so the simulation is
   an UPDATE carrying an extra item, not a second INSERT. */
db.run("UPDATE meta_lists SET items=?, seeded_from='operator' WHERE name='constitutionalPrimitives'"
  , JSON.stringify(arr.concat([{ key: "operator_primitive", name: "Operator Primitive" }])));
reg.seedLists(db);
const after2 = db.get("SELECT items FROM meta_lists WHERE name='constitutionalPrimitives'");
let arr2 = []; try { arr2 = JSON.parse(after2.items || "[]"); } catch (e) { }
ok(arr2.some(p => p.key === "operator_primitive"), "an operator's primitive survives a registry re-seed (the list is additive)");

console.log("\n▸ WARM BOOT (the digest gate keeps a boot cheap)");
const d1 = ucos.digest(db);
const skipped = ucos.seed(db);
ok(!!skipped.skipped, "an unchanged registry skips the re-seed on a warm boot");
ok(ucos.digest(db) === d1, "the digest is stable across processes for unchanged files");
ok(db.get("SELECT COUNT(*) n FROM ucos_documents WHERE doc_id='ureg'").n === 1, "the registry has exactly one document row");

console.log("\n" + (failed === 0
  ? "✓ all UCOS registry checks passed  (" + passed + " passed)"
  : "✗ " + failed + " FAILED (" + passed + " passed)"));
if (failed) process.exit(1);
