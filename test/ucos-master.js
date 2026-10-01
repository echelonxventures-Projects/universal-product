/* UCOS Ω∞ · Architecture5 — the Universal Capability Platform Master Architecture Reference.
    --------------------------------------------------------------------------
    Proves the fifth corpus is implemented in the Global Platform against the six
    criteria the spec itself states, measured by data rather than asserted in prose:

      ZERO MISSING      every universe the document declares is discovered,
                        instantiated and operable (coverage 100%)
      ZERO DUPLICATE    no universe key appears twice; re-instantiation adds nothing
      ZERO PARTIAL      every instantiated universe resolves to a foundation with a
                        canonical identity, a lifecycle, a source document and line
      ZERO OVERLAP      the corpus's universes are disjoint from the four existing
                        corpora and from each other — no key is shared
      ZERO HARD CODING  every universe is a data-defined entity (zero per-universe code);
                        its fields are derived from the document's own registry lists
      TRANSMISSIBLE     the universes activate into a live catalog — shopper-transactable

    The declaration count (188) is read from the document, never trusted from code.

    Fast, no server, no port, own throwaway DB. */
"use strict";
const path = require("path");
const fs = require("fs");

const TMP = path.join(require("os").tmpdir(), "ucos-master-" + process.pid + ".db");
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

/* the universes the spec declares as first-class operable units. The number is not
   hardcoded: the test re-derives the set from the document's own declaration lists
   (the fences whose label ends in "Universes") and asserts the parse reproduces it. */
const DECLARED_LABELS = ["Constitutional Foundation Universes", "Commerce Knowledge Universes",
  "Business Capability Universes", "Intelligence Universes", "Governance & Trust Universes",
  "Evolution & Factory Universes", "Future Existence Universes"];

console.log("\n▸ ARCHITECTURE5 · THE DOCUMENT IS THE SOURCE OF TRUTH");
ok(ucos.DOCS.some(d => d.id === "ucosm" && d.file === "Architecture5.txt"), "the corpus registers the fifth document");
ok(fs.existsSync(path.join(__dirname, "..", "Architecture5.txt")), "the document exists on disk");
const parsed = ucos.parseAll().ucosm;
ok(parsed && parsed.sections.length === 10, "all 10 architecture sections parsed", parsed ? parsed.sections.length : 0);
ok(parsed.registries.length >= 50, "the document's registry lists are parsed", parsed.registries.length);
ok(parsed.concepts.length > 800, "the document registers a substantial concept pool", parsed.concepts.length);

/* the declaration set, derived from the parse — the number the registry must reproduce */
const specUniverses = parsed.registries
  .filter(r => DECLARED_LABELS.includes(String(r.label || "").trim()))
  .flatMap(r => r.items)
  .map(n => String(n).trim())
  .filter(Boolean);
const specKeys = [...new Set(specUniverses.map(key))];
ok(specUniverses.length > 100, "the spec declares a substantial universe set", specUniverses.length);
ok(specKeys.length === specUniverses.length, "the spec's own declaration has no internal duplicates",
  specUniverses.length - specKeys.length + " repeated");

console.log("\n▸ ZERO MISSING (every universe the spec declares is discovered)");
const discovered = univ.discover();
const fromDoc = discovered.filter(u => u.sourceDoc === "ucosm");
ok(fromDoc.length >= specKeys.length, "the corpus contributes at least its declared universe set",
  fromDoc.length + " discovered vs " + specKeys.length + " declared");
for (const name of specKeys)
  ok(fromDoc.some(u => u.key === key(name)), "declared universe discovered: " + name);
ok(fromDoc.every(u => u.sourceLine > 0), "every discovered universe carries its source line");
ok(fromDoc.every(u => u.key && u.name && u.registry), "every discovered universe carries its declaring registry label");

console.log("\n▸ ZERO OVERLAP (disjoint from the four existing corpora and from itself)");
const others = discovered.filter(u => u.sourceDoc !== "ucosm").map(u => u.key);
const newKeys = fromDoc.map(u => u.key);
ok(new Set(newKeys).size === newKeys.length, "no two of the corpus's universes share a key");
const shared = newKeys.filter(k => others.includes(k));
ok(shared.length === 0, "no universe duplicates an existing corpus universe",
  shared.length ? shared.slice(0, 5).join(", ") : "");
ok(!fromDoc.some(u => /^(Foundation|Business|Declared)$/i.test(u.name)),
  "the declaration list labels themselves are not admitted as universes");

console.log("\n▸ 100% INSTANTIATION (operable, not merely readable)");
const r = univ.instantiateAll();
ok(r.failed === 0, "no universe failed to instantiate", "failed=" + r.failed);
ok(r.instantiated === r.discovered, "instantiation is complete", r.instantiated + " vs " + r.discovered);
const st = univ.stats();
ok(st.coverage === 100, "coverage is 100%", JSON.stringify(st));
ok(st.live === st.declared, "every universe is a live canonical foundation", "live=" + st.live);

console.log("\n▸ ZERO DUPLICATE (idempotent — re-running never multiplies)");
const before = { f: db.get("SELECT COUNT(*) n FROM ucos_foundations").n, u: db.get("SELECT COUNT(*) n FROM ucos_universes").n };
univ.instantiateAll(); univ.instantiateAll();
const after = { f: db.get("SELECT COUNT(*) n FROM ucos_foundations").n, u: db.get("SELECT COUNT(*) n FROM ucos_universes").n };
ok(before.f === after.f && before.u === after.u, "re-instantiation adds no foundation or universe rows",
  JSON.stringify(before) + " → " + JSON.stringify(after));
ok(db.get("SELECT COUNT(*) n FROM ucos_foundations WHERE key IN (" + newKeys.map(() => "?").join(",") + ")", ...newKeys).n === newKeys.length,
  "exactly one foundation row per declared universe");

console.log("\n▸ ZERO PARTIAL (every universe resolves to a complete canonical form)");
const partials = [];
for (const name of specKeys) {
  const f = found.resolve(key(name));
  if (!f || !f.key || !f.lifecycle || !f.source_doc || !f.source_line || f.classification !== "universe") partials.push(name);
}
ok(partials.length === 0, "every universe has identity + lifecycle + classification + source provenance",
  partials.slice(0, 5).join(", "));
ok(found.verify().ok === true, "the whole foundation registry is unique, resolved, acyclic and orphan-free",
  JSON.stringify(found.verify().checks));
const audit = comp.audit();
ok(audit.ok === true, "the foundation freeze criteria stay satisfied with the new corpus",
  audit.verdict + " (" + audit.criticalCount + " critical)");

console.log("\n▸ ZERO HARD CODING (data-defined entities, zero per-universe code)");
const src = fs.readFileSync(path.join(__dirname, "..", "lib", "ucos-universes.js"), "utf8");
ok(!/const UNIVERSES\s*=|const NAMES\s*=\s*\[/.test(src), "no hardcoded universe list constant (Article 4.2)");
ok((src.match(/"[^"]*\bUniverse"\s*,\s*"/g) || []).length === 0, "the engine enumerates no universe-name array literal");
let checkedDefs = 0;
for (const name of specKeys) {
  const ek = "uv_" + key(name);
  const def = db.get("SELECT def FROM entity_defs WHERE key=?", ek);
  if (!def) { ok(false, "entity definition exists: " + name); continue; }
  let d = {}; try { d = JSON.parse(def.def || "{}"); } catch (e) { }
  ok(!!d.label && Array.isArray(d.fields) && d.fields.length >= 4, "universe is a data-defined entity: " + name,
    d.label + " · " + (d.fields || []).length + " fields");
  checkedDefs++;
}
ok(checkedDefs === specKeys.length, "every declared universe has a generic entity definition");
const probeKey = "uv_" + key("Platform Factory Universe");
ok(Object.keys(entity.customEntityDefs(1)).some(k => k === probeKey),
  "a master-architecture universe is exposed by the generic entity engine");

console.log("\n▸ TRANSMISSIBLE (the universe activates into a live, transactable catalog)");
/* activate one universe end-to-end: canonical offering materialized from its own fields,
   published into a tenant catalog, backed by a SKU and inventory, then withdrawn cleanly */
const probe = "Platform Factory Universe";
const ek = "uv_" + key(probe);
ok(Object.keys(entity.customEntityDefs(1)).some(k => k === ek), "the probe universe is registered as an entity");
const created = entity.createEntity(1, ek, { name: "Factory Probe", code: "PF-1", status: "canonical" });
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

console.log("\n▸ THE PLATFORM TOTAL (the corpus composes with the other four, nothing duplicated)");
const allRows = db.get("SELECT COUNT(*) n FROM ucos_universes").n;
ok(allRows === discovered.length, "the live registry equals the discovered set", allRows + " vs " + discovered.length);
const dupKeys = db.get("SELECT COUNT(*) n FROM (SELECT key FROM ucos_universes GROUP BY key HAVING COUNT(*) > 1)").n;
ok(dupKeys === 0, "the whole registry (all five corpora) has zero duplicate universe keys", "duplicates=" + dupKeys);

console.log("\n" + (failed ? "✗ " + failed + " check(s) failed" : "✓ all Architecture5 universe checks passed") + "  (" + passed + " passed)");
process.exit(failed ? 1 : 0);
