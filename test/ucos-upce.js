/* UCOS Ω∞ · Architecture4 — the Universal Industry · Product · Service · Commerce Universe.
   --------------------------------------------------------------------------
   Proves the fourth corpus is implemented in the Global Platform against the four
   stated criteria, measured by data rather than asserted in prose:

     ZERO MISSING      every universe the document declares is discovered,
                       instantiated and operable (coverage 100%)
     ZERO DUPLICATE    no universe key appears twice; re-instantiation adds nothing
     ZERO PARTIAL      every instantiated universe resolves to a foundation with a
                       canonical identity, a lifecycle, a source document and line
     ZERO OVERLAP      the 70 universes are disjoint from the three existing corpora
                       and from each other — no key is shared with any other universe
     100% CONFIGURABLE every universe is a data-defined entity (zero per-universe code);
                       its fields are derived from the document's own registry lists
     DEEPLINKABLE      every universe is addressable by a stable key that resolves
                       through resolve(), the generic entity engine and the foundation

   Fast, no server, no port, own throwaway DB. */
"use strict";
const path = require("path");
const fs = require("fs");

const TMP = path.join(require("os").tmpdir(), "ucos-upce-" + process.pid + ".db");
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
const key = n => found.keyOf(n);

/* the spec's own declaration, as the number the registry must reproduce — nothing is
   trusted from code: the document is parsed, and the parse is the authority */
const FOUNDATION = ["Universal Identity Universe", "Universal Registry Universe", "Universal Schema Universe",
  "Universal Metadata Universe", "Universal Ontology Universe", "Universal Taxonomy Universe",
  "Universal Classification Universe", "Universal Context Universe", "Universal Relationship Universe",
  "Universal Knowledge Universe", "Universal Governance Universe", "Universal Security Universe",
  "Universal Compliance Universe", "Universal Audit Universe", "Universal Risk Universe",
  "Universal Workflow Universe", "Universal Automation Universe", "Universal Search Universe",
  "Universal Analytics Universe", "Universal AI Universe", "Universal Observability Universe",
  "Universal Entitlement Universe", "Universal Distribution Universe", "Universal Digital Twin Universe"];
const BUSINESS = ["Industry Universe", "Product Universe", "Service Universe", "Brand Universe",
  "Manufacturer Universe", "Supplier Universe", "Distributor Universe", "Partner Universe",
  "Customer Universe", "Store Universe", "Marketplace Universe", "Channel Universe", "Catalog Universe",
  "Pricing Universe", "Inventory Universe", "Procurement Universe", "Supply Chain Universe",
  "Logistics Universe", "Fulfillment Universe", "Order Universe", "Quote Universe", "Contract Universe",
  "Subscription Universe", "Offer Universe", "Promotion Universe", "Campaign Universe", "Tax Universe",
  "Finance Universe", "Accounting Universe", "Billing Universe", "Revenue Universe",
  "Settlement Universe", "Payment Universe"];
const DECLARED = ["Attribute Universe", "Variant Universe", "Nomenclature & Localization Universe",
  "Media Universe", "Temporal Universe", "Commercial Universe", "Order to Cash Universe",
  "Source to Pay Universe", "Offer Promotion Campaign Universe", "Acquisition & Synchronization Universe",
  "Search & Discovery Universe", "AI Universe", "Entitlement & Distribution Universe"];
const SPEC = FOUNDATION.concat(BUSINESS).concat(DECLARED);

console.log("\n▸ ARCHITECTURE4 · THE DOCUMENT IS THE SOURCE OF TRUTH");
ok(ucos.DOCS.some(d => d.id === "upce" && d.file === "Architecture4.txt"), "the corpus registers the fourth document");
ok(fs.existsSync(path.join(__dirname, "..", "Architecture4.txt")), "the document exists on disk");
const parsed = ucos.parseAll().upce;
ok(parsed && parsed.sections.length === 22, "all 22 universe sections parsed", parsed ? parsed.sections.length : 0);
ok(parsed.registries.length >= 36, "the document's registry lists are parsed", parsed.registries.length);
ok(parsed.concepts.length > 400, "the document registers a substantial concept pool", parsed.concepts.length);

console.log("\n▸ ZERO MISSING (every universe the spec declares is discovered)");
const discovered = univ.discover();
const fromDoc = discovered.filter(u => u.sourceDoc === "upce");
ok(fromDoc.length === SPEC.length, "discovered exactly the declared universe set", fromDoc.length + " vs " + SPEC.length);
for (const name of SPEC)
  ok(fromDoc.some(u => u.key === key(name)), "declared universe discovered: " + name);
ok(fromDoc.every(u => u.sourceLine > 0), "every discovered universe carries its source line");
ok(fromDoc.every(u => u.key && u.name && u.registry), "every discovered universe carries its declaring registry label");

console.log("\n▸ ZERO OVERLAP (disjoint from the three existing corpora and from itself)");
const others = discovered.filter(u => u.sourceDoc !== "upce").map(u => u.key);
const newKeys = fromDoc.map(u => u.key);
ok(new Set(newKeys).size === newKeys.length, "no two declared universes share a key");
const shared = newKeys.filter(k => others.includes(k));
ok(shared.length === 0, "no declared universe duplicates an existing corpus universe",
  shared.length ? shared.slice(0, 5).join(", ") : "");
ok(!newKeys.includes(key("Business")) && !newKeys.includes(key("Declared")) && !newKeys.includes(key("Foundation")),
  "the declaration list labels themselves are not admitted as universes");
ok(!fromDoc.some(u => /^(Segment|Family|Class)$/i.test(u.name)), "hierarchy levels are attributes, not overlapping universes");

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
ok(db.get("SELECT COUNT(*) n FROM ucos_foundations WHERE key IN (" + newKeys.map(() => "?").join(",") + ")", ...newKeys).n === SPEC.length,
  "exactly one foundation row per declared universe");

console.log("\n▸ ZERO PARTIAL (every universe resolves to a complete canonical form)");
const partials = [];
for (const name of SPEC) {
  const f = found.resolve(key(name));
  if (!f || !f.key || !f.lifecycle || !f.source_doc || !f.source_line || f.classification !== "universe") partials.push(name);
}
ok(partials.length === 0, "every universe has identity + lifecycle + classification + source provenance",
  partials.slice(0, 5).join(", "));
ok(found.verify().ok === true, "the whole foundation registry is unique, resolved, acyclic and orphan-free",
  JSON.stringify(found.verify().checks));

console.log("\n▸ 100% CONFIGURABLE (data-defined entities, zero per-universe code)");
const src = fs.readFileSync(path.join(__dirname, "..", "lib", "ucos-universes.js"), "utf8");
ok(!/const UNIVERSES\s*=|const NAMES\s*=\s*\[/.test(src), "no hardcoded universe list constant (Article 4.2)");
/* a hardcoded universe set would have to appear as an array literal of universe-name
   strings; a comment may name one example, but never enumerate them */
ok((src.match(/"[^"]*\bUniverse"\s*,\s*"/g) || []).length === 0, "the engine enumerates no universe-name array literal");
for (const name of SPEC) {
  const ek = "uv_" + key(name);
  const def = db.get("SELECT def FROM entity_defs WHERE key=?", ek);
  if (!def) { ok(false, "entity definition exists: " + name); continue; }
  let d = {}; try { d = JSON.parse(def.def || "{}"); } catch (e) { }
  ok(!!d.label && Array.isArray(d.fields) && d.fields.length >= 4, "universe is a data-defined entity: " + name,
    d.label + " · " + (d.fields || []).length + " fields");
}
ok(Object.keys(entity.customEntityDefs(1)).some(k => k === "uv_" + key("Industry Universe")),
  "a declared universe is exposed by the generic entity engine");

console.log("\n▸ DEEPLINKABLE (a stable key resolves through every layer)");
const probe = "Order to Cash Universe";                       /* the stopword-named declaration */
const f = found.resolve(key(probe));
ok(!!f && f.key === key(probe), "the stopword-named universe resolves by key in the foundation registry", f ? f.key : "MISSING");
ok(f && f.classification === "universe", "the resolved foundation carries its universe classification");
const ek = "uv_" + key(probe);
const created = entity.createEntity(1, ek, { name: "Flow Audit Probe", code: "O2C-1", status: "canonical" });
ok(!created.error && created.id > 0, "a record can be created in the universe through the generic engine", JSON.stringify(created));
const listed = entity.listEntities(1, ek);
ok(Array.isArray(listed) && listed.some(x => x.name === "Flow Audit Probe"), "the record is readable back through the same key");
ok(entity.deleteEntity(1, ek, created.id).ok === true, "the record is deletable through the same key");
ok(!entity.listEntities(1, ek).some(x => x.name === "Flow Audit Probe"), "the deletion took effect — the key is a live handle");
/* the traverse API reaches the universe from the registry's own graph vocabulary */
const tr = found.traverse(key("Industry Universe"), "foundation", 2);
ok(tr.graph === "foundation" && Array.isArray(tr.edges), "a universe is addressable through the graph vocabulary");

console.log("\n" + (failed ? "✗ " + failed + " check(s) failed" : "✓ all Architecture4 universe checks passed") + "  (" + passed + " passed)");
process.exit(failed ? 1 : 0);
