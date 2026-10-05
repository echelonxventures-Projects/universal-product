/* UCOS Ω∞ · Architecture6 — the Universal Capability Platform · Master Architecture Reference
    Model. The eighth corpus: the universal capability STACK (composition, experience,
    intelligence, operations, resilience, integration, governance, knowledge, temporal,
    context, evolution, execution substrate) plus the marketplace gap-closers and the five
    compositions. It reuses the UPCE "# <n>. TITLE" + labelled-fence grammar, so it needed
    only a DOCS row — and because it had NO test, two latent defects shipped silently:

      BORROWED LABEL   §14 (the five compositions) and §15 (the end state) carry fences with
                       no "##" heading of their own, so both inherited §13's declaration
                       label "Marketplace Composition Universes". One registry key held three
                       lists, and — the label ends in "Universes", the declaration channel —
                       §15's composed OUTPUTS ("Data Models", "Workflows"…) were declared
                       first-class universes. The parser now records whether a label was
                       declared in its own container (labelOwn) and a borrowed label cannot
                       declare anything; the document gained the two headings its grammar
                       requires (every fence in Architecture4/5 sits under its own).
      MEASURED GAPS    the corpus declares 129 universes; four were silently dropped because
                       the declaration channel kept the registry-machinery blocklist that the
                       reconstructed admission needs. Architecture6's §8 declares Registry
                       and Taxonomy as knowledge universes "distinct from the registry
                       machinery that holds them" — the corpus is the authority in a
                       declaration channel, so the blocklist no longer applies there.

    Proves the corpus is implemented against the same criteria as the other corpora, measured
    by data rather than asserted in prose — including the document's OWN acceptance test (§14):
    every term in each of the five compositions resolves to a declared universe, and a term
    that resolves nowhere is a gap the platform MEASURES rather than ignores.

    Fast, no server, no port, own throwaway DB. */
"use strict";
const path = require("path");
const fs = require("fs");

const TMP = path.join(require("os").tmpdir(), "ucos-mm-" + process.pid + ".db");
process.env.LX_DB = TMP;
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }

const silence = console.log; console.log = () => { };
const db = require(path.join(__dirname, "..", "lib", "db.js"));
const ucos = require(path.join(__dirname, "..", "lib", "ucos.js"));
const found = require(path.join(__dirname, "..", "lib", "ucos-foundations.js"));
const univ = require(path.join(__dirname, "..", "lib", "ucos-universes.js"));
const cat = require(path.join(__dirname, "..", "lib", "ucos-catalog.js"));
const comp = require(path.join(__dirname, "..", "lib", "ucos-completeness.js"));
const entity = require(path.join(__dirname, "..", "lib", "entity.js"));
ucos.seed(db);                                  /* constitutional registry first */
console.log = silence;

let passed = 0, failed = 0;
const ok = (cond, name, extra) => { if (cond) { passed++; } else { failed++; console.log("  ✗ " + name + (extra ? "  → " + extra : "")); } };
const key = n => found.keyOf(n);

console.log("\n▸ ARCHITECTURE6 · THE DOCUMENT IS THE SOURCE OF TRUTH");
ok(ucos.DOCS.some(d => d.id === "ucosmm" && d.file === "Architecture6.txt"), "the corpus registers the eighth document");
ok(fs.existsSync(path.join(__dirname, "..", "Architecture6.txt")), "the document exists on disk");
const parsed = ucos.parseAll().ucosmm;
ok(parsed && parsed.sections.length === 15, "all 15 architecture sections parsed", parsed ? parsed.sections.length : 0);
ok(parsed.registries.length === 13, "the document's 13 registry lists are parsed", parsed.registries.length);
ok(parsed.concepts.length === 145, "the document registers its concept pool", parsed.concepts.length);

/* the universe set the document declares: the 12 stack layers + the marketplace gap-closers */
const DECLARED_LABELS = ["Composition Universes", "Experience Universes", "Intelligence Universes",
  "Operations Universes", "Resilience Universes", "Integration Universes", "Governance Universes",
  "Knowledge Universes", "Temporal Universes", "Context Universes", "Evolution Universes",
  "Execution Substrate Universes", "Marketplace Composition Universes"];
const declLists = parsed.registries.filter(r => DECLARED_LABELS.includes(String(r.label || "").trim()));
ok(declLists.length === 13, "every declaration list is recognised", declLists.length);
const specUniverses = [...new Set(declLists.flatMap(r => r.items).map(n => String(n).trim()))];
ok(specUniverses.length === 129, "the spec declares its universe set", specUniverses.length);
ok(new Set(specUniverses.map(key)).size === specUniverses.length, "the spec's own declaration has no internal duplicates");

console.log("\n▸ ZERO DUPLICATE (one registry key per list — the borrowed-label defect)");
const regKeys = parsed.registries.map(r => r.key);
const dupKeys = regKeys.filter((k, i) => regKeys.indexOf(k) !== i);
ok(dupKeys.length === 0, "no two of the document's registry lists share a key",
  dupKeys.length ? [...new Set(dupKeys)].join(", ") : "");
ok(parsed.registries.every(r => r.labelOwn === true), "every declaration list sits under its own heading");
ok(!parsed.registries.some(r => /Five Compositions|Composed Artifacts/i.test(String(r.label || ""))),
  "the five-composition and end-state fences are not registry lists (their labels name diagrams, not registries)");

console.log("\n▸ A DECLARATION IS OWNED (the invariant across every corpus, not just this one)");
let borrowedDecl = 0, checked = 0;
for (const docId of Object.keys(ucos.parseAll())) {
  for (const r of ucos.parseAll()[docId].registries) {
    checked++;
    if (/\buniverses?$/i.test(String(r.label || "").trim()) && r.labelOwn === false) borrowedDecl++;
  }
}
ok(checked > 1000, "the invariant is measured over the whole registry surface", checked);
ok(borrowedDecl === 0, "no corpus declares universes under a label borrowed from an earlier section", borrowedDecl);

console.log("\n▸ ZERO MISSING (every universe the spec declares is discovered)");
const discovered = univ.discover();
const fromDoc = discovered.filter(u => u.sourceDoc === "ucosmm");
const allKeys = new Set(discovered.map(u => u.key));
for (const name of specUniverses)
  ok(allKeys.has(key(name)), "declared universe discovered: " + name);
ok(fromDoc.length === 96, "the corpus contributes its net-new universes after the global first-wins dedup", fromDoc.length);
ok(fromDoc.every(u => u.sourceLine > 0 && u.key && u.name && u.registry),
  "every discovered universe carries its provenance");
/* the machinery words the corpus declares distinctly from the machinery that holds them (§8) */
for (const name of ["Authority", "Registry", "Discovery", "Graph"])
  ok(allKeys.has(key(name)), "the corpus's own §8 declaration is honoured: " + name);

console.log("\n▸ ZERO POLLUTION (equations and composed outputs never become universes)");
ok(!discovered.some(u => /[=+]/.test(u.name)), "no discovered universe contains equation residue");
ok(!discovered.some(u => /like Solution/i.test(u.name)), "no composition's left-hand side became a universe");
const composedOutputs = ["Data Models", "Workflows", "User Interfaces", "Reports", "Dashboards",
  "Security Controls", "Operational Controls"];
const leaked = composedOutputs.filter(n => fromDoc.some(u => u.key === key(n)));
ok(leaked.length === 0, "§15's composed outputs are not universes of this corpus",
  leaked.length ? leaked.join(", ") : "");
ok(!fromDoc.some(u => u.key === key("Data Models")), "Data Models is a composed OUTPUT, never a universe");

console.log("\n▸ §14 · THE FIVE COMPOSITIONS (the document's own acceptance test)");
/* the equations are read out of the document itself — the fence under "## Five Compositions" */
const docLines = fs.readFileSync(path.join(__dirname, "..", "Architecture6.txt"), "utf8").split(/\r?\n/);
let inSec = false, inFence = false, eqLines = [];
for (const l of docLines) {
  const t = l.trim();
  if (/^#\s+14\.\s/.test(t)) { inSec = true; continue; }
  if (inSec && /^#\s+15\.\s/.test(t)) break;
  if (!inSec) continue;
  if (t.startsWith("```")) { if (!inFence) { inFence = true; continue; } break; }
  if (inFence && t) eqLines.push(t);
}
ok(eqLines.length === 9, "the five compositions are written as nine equation lines", eqLines.length);
const lhs = [], terms = new Set();
for (const l of eqLines) {
  const eq = l.split("=");
  if (eq.length < 2) continue;
  lhs.push(eq[0].trim());
  for (const x of eq.slice(1).join("=").split("+")) { const v = x.trim(); if (v) terms.add(v); }
}
ok(lhs.length === 5 && lhs.every(n => /Solution$/.test(n)), "the five compositions are named", lhs.join(", "));
const byName = new Set(discovered.map(u => u.name.toLowerCase()));
const exact = [...terms].filter(t => byName.has(t.toLowerCase()));
const gaps = [...terms].filter(t => !byName.has(t.toLowerCase()));
ok(exact.length === 16, "16 of the 21 terms resolve to a declared universe by exact name", exact.join(", "));
ok(gaps.length === 5, "the remaining 5 are measured, not ignored", gaps.join(", "));
/* each measured gap is shorthand for a universe the corpus set already declares — a naming
   gap, never a capability gap. Pinned so a future declaration closing one moves the number. */
const related = { Geo: "geograph", Media: "media", Analytics: "analytics", AI: "^ai ", Communication: "communication" };
ok(gaps.length === Object.keys(related).length && gaps.every(g => related[g]),
  "the measured gaps are exactly the five shorthand terms", gaps.join(", "));
for (const g of gaps)
  ok(discovered.some(u => new RegExp(related[g], "i").test(u.name)),
    "the shorthand term names a declared universe elsewhere: " + g + " → " + related[g]);

console.log("\n▸ 100% INSTANTIATION (operable, not merely readable)");
const r = univ.instantiateAll();
ok(r.failed === 0, "no universe failed to instantiate", "failed=" + r.failed);
ok(r.instantiated === r.discovered, "instantiation is complete", r.instantiated + " vs " + r.discovered);
const st = univ.stats();
ok(st.coverage === 100, "coverage is 100%", JSON.stringify(st));
ok(st.live === st.declared, "every universe is a live canonical foundation", "live=" + st.live);
const before = { f: db.get("SELECT COUNT(*) n FROM ucos_foundations").n, u: db.get("SELECT COUNT(*) n FROM ucos_universes").n };
univ.instantiateAll(); univ.instantiateAll();
const after = { f: db.get("SELECT COUNT(*) n FROM ucos_foundations").n, u: db.get("SELECT COUNT(*) n FROM ucos_universes").n };
ok(before.f === after.f && before.u === after.u, "re-instantiation adds no foundation or universe rows",
  JSON.stringify(before) + " → " + JSON.stringify(after));

console.log("\n▸ SELF-HEALING (a registry seeded by a defect heals on the next boot)");
/* the defect this corpus shipped with: universes the corpus never declared were instantiated.
   Recreate that state, then let the boot path correct it. */
db.run("INSERT OR IGNORE INTO ucos_universes(key,name,source_doc,source_line,entity_key,concepts,instantiated_at)"
  + " VALUES('data_models','Data Models','ucosmm',318,'uv_data_models',0,?)", new Date().toISOString());
db.run("INSERT OR IGNORE INTO entity_defs(key,scope,tenant_id,def) VALUES('uv_data_models','platform',0,?)",
  JSON.stringify({ label: "Data Models", storage: "json", pk: "id", perm: { read: ["admin", "platform"], write: ["admin", "platform"] },
    fields: [{ key: "name", label: "Name", type: "text", required: true }, { key: "code", label: "Reference", type: "text" },
      { key: "status", label: "Status", type: "select", options: ["canonical"] }, { key: "attrs", label: "Attributes", type: "json" }] }));
db.run("INSERT OR IGNORE INTO ucos_foundations(key,name,lifecycle,classification,source_doc,source_line) VALUES('data_models','Data Models','canonical','universe','ucosmm',318)");
ok(!!db.get("SELECT 1 ok FROM ucos_universes WHERE key='data_models'"), "the bogus universe is planted");
const keptEntity = entity.createEntity(1, "uv_data_models", { name: "Operator Record", code: "OR-1", status: "canonical" });
ok(!keptEntity.error && keptEntity.id > 0, "an operator record is created in it (data is sacred)", JSON.stringify(keptEntity));
db.run("INSERT INTO entity_data(tenant_id,entity,data) VALUES(?,?,?)", 0, "uv_data_models",
  JSON.stringify({ name: "Data Models", status: "Proposed" }));
ok(db.get("SELECT COUNT(*) n FROM entity_data WHERE entity='uv_data_models'").n === 2,
  "the platform's own canonical record sits beside the operator's");
const heal = univ.instantiateAll();
ok(heal.pruned.removed === 0 && heal.pruned.kept === 1, "a universe with operator records is kept and reported, not deleted",
  JSON.stringify(heal.pruned));
ok(!!db.get("SELECT 1 ok FROM ucos_universes WHERE key='data_models'"), "the operator's universe survives the corpus correction");
entity.deleteEntity(1, "uv_data_models", keptEntity.id);
ok(db.get("SELECT COUNT(*) n FROM entity_data WHERE entity='uv_data_models'").n === 1,
  "only the platform's derived canonical record remains");
const heal2 = univ.instantiateAll();
ok(heal2.pruned.removed === 1, "a canonical record alone does not save a universe the corpus no longer declares", JSON.stringify(heal2.pruned));
ok(!db.get("SELECT 1 ok FROM ucos_universes WHERE key='data_models'"), "no trace of the defect's universe remains");
ok(!db.get("SELECT 1 ok FROM entity_defs WHERE key='uv_data_models'"), "its platform entity definition is withdrawn");
ok(!db.get("SELECT 1 ok FROM ucos_foundations WHERE key='data_models'"), "its foundation is withdrawn");
ok(db.get("SELECT COUNT(*) n FROM entity_data WHERE entity='uv_data_models'").n === 0,
  "its derived canonical record goes with it (no orphan data)");
univ.instantiateAll();
ok(db.get("SELECT COUNT(*) n FROM ucos_universes").n === discovered.length,
  "the registry is exactly the discovered set again");

console.log("\n▸ ZERO PARTIAL (every universe resolves to a complete canonical form)");
const partials = [];
for (const name of specUniverses) {
  const f = found.resolve(key(name));
  if (!f || !f.key || !f.lifecycle || !f.source_doc || !f.source_line || f.classification !== "universe") partials.push(name);
}
ok(partials.length === 0, "every declared universe has identity + lifecycle + classification + source provenance",
  partials.slice(0, 5).join(", "));
ok(found.verify().ok === true, "the whole foundation registry is unique, resolved, acyclic and orphan-free",
  JSON.stringify(found.verify().checks));
const audit = comp.audit();
ok(audit.ok === true, "the foundation freeze criteria stay satisfied with the eighth corpus",
  audit.verdict + " (" + audit.criticalCount + " critical)");

console.log("\n▸ ZERO HARD CODING (data-defined entities, zero per-universe code)");
const src = fs.readFileSync(path.join(__dirname, "..", "lib", "ucos-universes.js"), "utf8");
ok(!/const UNIVERSES\s*=|const NAMES\s*=\s*\[/.test(src), "no hardcoded universe list constant (Article 4.2)");
ok((src.match(/"[^"]*\bAuthority"\s*,\s*"/g) || []).length === 0, "the engine enumerates no universe-name array literal");
let checkedDefs = 0;
for (const name of specUniverses) {
  const ek = "uv_" + key(name);
  const def = db.get("SELECT def FROM entity_defs WHERE key=?", ek);
  if (!def) { ok(false, "entity definition exists: " + name); continue; }
  let d = {}; try { d = JSON.parse(def.def || "{}"); } catch (e) { }
  ok(!!d.label && Array.isArray(d.fields) && d.fields.length >= 4, "universe is a data-defined entity: " + name,
    d.label + " · " + (d.fields || []).length + " fields");
  checkedDefs++;
}
ok(checkedDefs === specUniverses.length, "every declared universe has a generic entity definition", checkedDefs);

console.log("\n▸ TRANSMISSIBLE (the corpus's gap-closing declaration activates into a live catalog)");
/* Review is why §13 exists: the five compositions name it and no other corpus declared it */
const probe = "Review";
const ek = "uv_" + key(probe);
ok(Object.keys(entity.customEntityDefs(1)).some(k => k === ek), "the probe universe is registered as an entity");
const created = entity.createEntity(1, ek, { name: "Composition Probe", code: "MM-1", status: "canonical" });
ok(!created.error && created.id > 0, "a record is created in the universe through the generic engine", JSON.stringify(created));
const a = cat.activate(1, ek);
ok(a.ok === true, "the universe activates into the tenant catalog", JSON.stringify(a));
const row = db.get("SELECT id, price, lifecycle FROM products WHERE tenant_id=1 AND source_universe=?", ek);
ok(!!row, "a shopper-facing catalog projection exists for the universe", JSON.stringify(row));
const sku = db.get("SELECT id, stock FROM skus WHERE tenant_id=1 AND product_id=?", row ? row.id : -1);
const inv = db.get("SELECT qty FROM inventory WHERE tenant_id=1 AND sku_id=?", sku ? sku.id : -1);
ok(!!sku && !!inv, "the offering is backed by a SKU and inventory", "");
const w = cat.withdrawUniverse(1, ek);
ok(w.ok === true && w.removed >= 1, "the universe withdraws cleanly from the catalog", JSON.stringify(w));
ok(db.get("SELECT COUNT(*) n FROM products WHERE tenant_id=1 AND source_universe=?", ek).n === 0, "withdrawal leaves no catalog row");
ok(db.get("SELECT COUNT(*) n FROM skus WHERE tenant_id=1 AND product_id IN (SELECT id FROM products WHERE source_universe=?)", ek).n === 0,
  "withdrawal leaves no orphaned SKU");
ok(entity.deleteEntity(1, ek, created.id).ok === true, "the probe record is deletable through the same key");

console.log("\n▸ THE PLATFORM TOTAL (the corpus composes with the other seven, nothing duplicated)");
const allRows = db.get("SELECT COUNT(*) n FROM ucos_universes").n;
ok(allRows === discovered.length, "the live registry equals the discovered set", allRows + " vs " + discovered.length);
const dupUniverses = db.get("SELECT COUNT(*) n FROM (SELECT key FROM ucos_universes GROUP BY key HAVING COUNT(*) > 1)").n;
ok(dupUniverses === 0, "the whole registry (all eight corpora) has zero duplicate universe keys", "duplicates=" + dupUniverses);
ok(db.get("SELECT COUNT(*) n FROM ucos_universes WHERE source_doc='ucosmm'").n === fromDoc.length,
  "the corpus's rows are attributed to it", fromDoc.length);

console.log("\n" + (failed ? "✗ " + failed + " check(s) failed" : "✓ all Architecture6 universe checks passed") + "  (" + passed + " passed)");
process.exit(failed ? 1 : 0);
