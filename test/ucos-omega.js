/* UCOS Ω∞ · the markdown corpora — Omega (UCOSO) and the requirements reference (UCOSU).
    --------------------------------------------------------------------------
    The first four corpora are fenced-text architectures; these two are the
    consolidated references, and each needed a NEW grammar the parser had none:
      UCOSO  a MARKDOWN document — no fences at all. Its structure lives in tables,
             and its universe declaration is the §9.2 "Universe Index" (78 universes).
      UCOSU  a PDF-derived TEXT document — no fences, no tables. Its containers are
             lettered headings, its content is labelled bullet lists, and its universes
             are declared by the headings themselves ("Identity Universe"), after a
             leading table of contents that must not be parsed as content.

    Proves both are implemented against the same criteria as the other corpora,
    measured by data rather than asserted in prose:

      ZERO MISSING      every universe each document declares is discovered
      ZERO DUPLICATE    no universe key appears twice; re-instantiation adds nothing
      ZERO PARTIAL      every universe resolves to a foundation with a canonical
                        identity, a lifecycle, a source document and line
      CANONICAL NAMES   a declaration's gloss and subtitle are commentary, never the
                        identity — "Spatial Existence (Geography)" → "Spatial Existence"
      DECLARATION       the corpus's own declaration channel admits registry words
                        ("Identity", "Security", "Evolution") that the reconstructed
                        admission would block — the channel, not the blocklist, decides
      TRANSMISSIBLE     a universe from each corpus activates into a live catalog

    Fast, no server, no port, own throwaway DB. */
"use strict";
const path = require("path");
const fs = require("fs");

const TMP = path.join(require("os").tmpdir(), "ucos-omega-" + process.pid + ".db");
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

console.log("\n▸ THE DOCUMENTS ARE THE SOURCE OF TRUTH");
const dO = ucos.DOCS.find(d => d.id === "ucoso"), dU = ucos.DOCS.find(d => d.id === "ucosu");
ok(!!dO && dO.file === "UCOS_Omega_Constitutional_Architecture_v1.0.md", "the corpus registers Omega");
ok(!!dU && dU.file === "UCOS-Universal-Capability-Operating-System.md", "the corpus registers the requirements reference");
ok(fs.existsSync(path.join(__dirname, "..", dO.file)) && fs.existsSync(path.join(__dirname, "..", dU.file)),
  "both documents exist on disk");
ok(!!dO.tables && !!dO.declare, "Omega is declared as a table corpus with a declaration channel");
ok(!!dU.lists && !!dU.bodyStart, "the requirements reference is declared as a list corpus with a body boundary");

/* ---------- OMEGA: the markdown-table grammar ---------- */
console.log("\n▸ OMEGA · the table grammar turns markdown into registries");
const parsed = ucos.parseAll();
const po = parsed.ucoso, pu = parsed.ucosu;
ok(po.sections.length === 28, "all 28 numbered ## containers parsed", po.sections.length);
ok(po.registries.length > 60, "the document's tables are parsed as registry lists", po.registries.length);
ok(po.concepts.length > 3000, "the table cells register a substantial concept pool", po.concepts.length);
/* the declaration table: §9.2. Its label is a ### heading — the table grammar takes its
   label from the nearest heading at ANY level, or the index would be anonymous */
const index = po.registries.find(r => /^9\.2 Universe Index$/i.test(String(r.label || "").trim()));
ok(!!index, "the §9.2 Universe Index table is parsed");
ok(!!index && index.items.length === 78, "the index declares all 78 universes", index ? index.items.length : 0);
ok(po.registries.some(r => /^U\d+ ·/.test(String(r.label || "").trim())),
  "a per-universe card is parsed as a registry list");
ok(po.concepts.every(c => c.line > 0), "every Omega concept carries its source line");

/* ---------- OMEGA: ZERO MISSING, with canonical names ---------- */
console.log("\n▸ OMEGA · ZERO MISSING (the index's 78 universes, canonically named)");
/* the canonical set, derived from the parse — never trusted from code. The name is the
   engine's own canonicalizer (declarationName): the gloss and subtitle are stripped */
const specNames = index.items.map(i => univ.declarationName(i)).filter(Boolean);
ok(specNames.length === 78, "every index row canonicalizes to a name", specNames.length);
ok(new Set(specNames.map(key)).size === 78, "no two index universes canonicalize to the same key");
const discovered = univ.discover();
for (const nm of specNames)
  ok(discovered.some(u => u.key === key(nm)), "index universe discovered: " + nm);
/* the documented transformations, pinned as spec — a gloss or subtitle is commentary on
   the name, never part of the identity */
ok(univ.declarationName("Spatial Existence (Geography)") === "Spatial Existence", "a parenthetical gloss is dropped");
ok(univ.declarationName("Physical Systems (IoT, Edge & Robotics)") === "Physical Systems", "a gloss with commas is dropped");
ok(univ.declarationName("Intelligence (AI)") === "Intelligence", "an abbreviation gloss is dropped");
ok(univ.declarationName("Temporal Universe — the Constitutional Owner of Time") === "Temporal Universe",
  "an em-dash subtitle is dropped");
ok(univ.declarationName("Commerce Object (Product & Service)") === "Commerce Object", "an ampersand gloss is dropped");

/* ---------- OMEGA: the declaration channel, not the blocklist, decides ---------- */
console.log("\n▸ OMEGA · the declaration channel admits what reconstruction would refuse");
/* "Identity", "Security" and "Evolution" are registry-vocabulary words — the admission
   that keeps them out of RECONSTRUCTED lists must not reach a declaration channel, or the
   index's own universes would go missing. The blocklist's verdict is measured first, so
   the assertion is that the channel overrides a real rejection, not a vacuous one */
for (const nm of ["Identity", "Security", "Evolution", "Compliance"]) {
  ok(!univ.isUniverse(nm), "the reconstructed admission rejects the registry word " + nm);
  ok(discovered.some(u => u.key === key(nm)), "the declaration channel admits " + nm + " as a universe");
}
ok(!univ.isUniverse("Commerce Object (Product & Service)"), "reconstruction rejects the glossed form itself");
ok(discovered.some(u => u.key === key("Commerce Object")), "the channel admits the canonical name behind the gloss");

/* ---------- UCOSU: the lettered-heading grammar ---------- */
console.log("\n▸ REQUIREMENTS REFERENCE · headings are containers, and the TOC is not content");
ok(pu.sections.length === 220, "all 220 heading registrations parsed", pu.sections.length);
const distinct = new Set(pu.sections.map(s => s.name));
ok(distinct.size === 110, "110 real sections, each registered twice — once in the table of contents, once in the body",
  distinct.size);
ok(pu.registries.length > 30, "the document's labelled lists are parsed as registries", pu.registries.length);
ok(pu.concepts.length > 1000, "the lists register a substantial concept pool", pu.concepts.length);
/* bodyStart: the TOC repeats the body's headings, so a corpus that parsed it would double
   its content and mis-attribute every line. Content is extracted from the body onward only */
const bodyLine = (() => {
  const lines = fs.readFileSync(path.join(__dirname, "..", dU.file), "utf8").split("\n");
  for (let i = 0; i < lines.length; i++) if (dU.bodyStart.test(lines[i].trim())) return i + 1;
  return 0;
})();
ok(bodyLine > 0, "the document declares a body boundary");
ok(pu.concepts.every(c => c.line >= bodyLine), "no concept is extracted from the table of contents",
  pu.concepts.filter(c => c.line < bodyLine).length + " leaked");
ok(pu.concepts.length > 0, "the body's lists are extracted", pu.concepts.length);

/* ---------- UCOSU: the heading is the declaration ---------- */
console.log("\n▸ REQUIREMENTS REFERENCE · a heading declares its universe (ZERO MISSING)");
/* the universe declarations are the section headings themselves — matched by the corpus's
   own `declare` vocabulary, so which headings declare is data in the DOCS row */
const headDecl = ["Identity Universe", "Geography and Spatial Existence Universe", "Data Universe",
  "Workflow Universe", "Event Universe", "Universal Runtime Fabric", "Universal Composition Substrate",
  "Universal Generation Engine", "Universal Certification Engine", "Automation and Autonomy Layer",
  "Global Product and Service Intelligence Network", "Universal Commerce Object Universe"];
for (const nm of headDecl)
  ok(discovered.some(u => u.key === key(nm)), "heading-declared universe discovered: " + nm);
/* the heading carries a subtitle; the universe is the name before it */
ok(pu.sections.some(s => s.name.startsWith("Temporal Universe —")), "a heading carries its subtitle");
ok(discovered.some(u => u.key === key("Temporal Universe")), "the subtitle is not part of the identity");

/* ---------- both corpora: 100% INSTANTIATION ---------- */
console.log("\n▸ 100% INSTANTIATION (operable, not merely readable)");
const r = univ.instantiateAll();
ok(r.failed === 0, "no universe failed to instantiate", "failed=" + r.failed);
ok(r.instantiated === r.discovered, "instantiation is complete", r.instantiated + " vs " + r.discovered);
const st = univ.stats();
ok(st.coverage === 100, "coverage is 100%", JSON.stringify(st));
ok(st.live === st.declared, "every universe is a live canonical foundation", "live=" + st.live);

/* ---------- ZERO DUPLICATE ---------- */
console.log("\n▸ ZERO DUPLICATE (idempotent — re-running never multiplies)");
const before = { f: db.get("SELECT COUNT(*) n FROM ucos_foundations").n, u: db.get("SELECT COUNT(*) n FROM ucos_universes").n };
univ.instantiateAll(); univ.instantiateAll();
const after = { f: db.get("SELECT COUNT(*) n FROM ucos_foundations").n, u: db.get("SELECT COUNT(*) n FROM ucos_universes").n };
ok(before.f === after.f && before.u === after.u, "re-instantiation adds no foundation or universe rows",
  JSON.stringify(before) + " → " + JSON.stringify(after));
ok(db.get("SELECT COUNT(*) n FROM (SELECT key FROM ucos_universes GROUP BY key HAVING COUNT(*) > 1)").n === 0,
  "the whole registry has zero duplicate universe keys");
/* the consolidated corpora re-state universes the earlier corpora already declared (Omega's
   "Pricing" is Architecture5's "Pricing"): one universe, one key, one foundation — the
   registry de-duplicates by key, so the restatement is absorbed, not multiplied */
ok(new Set(discovered.map(u => u.key)).size === discovered.length, "the discovered set itself has no duplicate key");

/* ---------- ZERO PARTIAL ---------- */
console.log("\n▸ ZERO PARTIAL (every universe resolves to a complete canonical form)");
const partials = [];
for (const nm of specNames.concat(headDecl)) {
  const f = found.resolve(key(nm));
  if (!f || !f.key || !f.lifecycle || !f.source_doc || !f.source_line || f.classification !== "universe") partials.push(nm);
}
ok(partials.length === 0, "every declared universe has identity + lifecycle + classification + source provenance",
  partials.slice(0, 5).join(", "));
ok(found.verify().ok === true, "the whole foundation registry is unique, resolved, acyclic and orphan-free",
  JSON.stringify(found.verify().checks));
const audit = comp.audit();
ok(audit.ok === true, "the foundation freeze criteria stay satisfied with both corpora",
  audit.verdict + " (" + audit.criticalCount + " critical)");

/* ---------- 100% CONFIGURABLE ---------- */
console.log("\n▸ 100% CONFIGURABLE (data-defined entities, zero per-universe code)");
const src = fs.readFileSync(path.join(__dirname, "..", "lib", "ucos-universes.js"), "utf8");
ok(!/const UNIVERSES\s*=|const NAMES\s*=\s*\[/.test(src), "no hardcoded universe list constant (Article 4.2)");
let checkedDefs = 0;
for (const nm of ["Platform Studio", "Constitution & Authority", "Universal Runtime Fabric", "Identity Universe"]) {
  const ek = "uv_" + key(nm);
  const def = db.get("SELECT def FROM entity_defs WHERE key=?", ek);
  if (!def) { ok(false, "entity definition exists: " + nm); continue; }
  let d = {}; try { d = JSON.parse(def.def || "{}"); } catch (e) { }
  ok(!!d.label && Array.isArray(d.fields) && d.fields.length >= 4, "universe is a data-defined entity: " + nm,
    d.label + " · " + (d.fields || []).length + " fields");
  checkedDefs++;
}
ok(checkedDefs === 4, "every probe universe has a generic entity definition");
ok(Object.keys(entity.customEntityDefs(1)).some(k => k === "uv_" + key("Universal Runtime Fabric")),
  "a requirements-reference universe is exposed by the generic entity engine");
ok(Object.keys(entity.customEntityDefs(1)).some(k => k === "uv_" + key("Platform Studio")),
  "an Omega universe is exposed by the generic entity engine");

/* ---------- TRANSMISSIBLE ---------- */
console.log("\n▸ TRANSMISSIBLE (a universe from each corpus activates into a live catalog)");
const probes = [{ name: "Platform Studio", doc: "Omega" }, { name: "Universal Runtime Fabric", doc: "the requirements reference" }];
for (const p of probes) {
  const ek = "uv_" + key(p.name);
  ok(Object.keys(entity.customEntityDefs(1)).some(k => k === ek), "the " + p.doc + " probe is registered as an entity");
  const created = entity.createEntity(1, ek, { name: p.name + " Probe", code: "PR-1", status: "canonical" });
  ok(!created.error && created.id > 0, "a record is created in the " + p.doc + " universe", JSON.stringify(created));
  const a = cat.activate(1, ek);
  ok(a.ok === true, "the " + p.doc + " universe activates", JSON.stringify(a));
  const row = db.get("SELECT id, price, lifecycle FROM products WHERE tenant_id=1 AND source_universe=?", ek);
  ok(!!row, "a shopper-facing catalog projection exists", JSON.stringify(row));
  const sku = db.get("SELECT id, stock FROM skus WHERE tenant_id=1 AND product_id=?", row ? row.id : -1);
  const inv = db.get("SELECT qty FROM inventory WHERE tenant_id=1 AND sku_id=?", sku ? sku.id : -1);
  ok(!!sku && !!inv, "the offering is backed by a SKU and inventory", "");
  const w = cat.withdrawUniverse(1, ek);
  ok(w.ok === true && w.removed >= 1, "the " + p.doc + " universe withdraws cleanly", JSON.stringify(w));
  ok(db.get("SELECT COUNT(*) n FROM products WHERE tenant_id=1 AND source_universe=?", ek).n === 0, "withdrawal leaves no catalog row");
  ok(db.get("SELECT COUNT(*) n FROM skus WHERE product_id IN (SELECT id FROM products WHERE source_universe=?)", ek).n === 0,
    "withdrawal leaves no orphaned SKU");
  ok(entity.deleteEntity(1, ek, created.id).ok === true, "the probe record is deletable through the same key");
}

console.log("\n▸ THE PLATFORM TOTAL (the corpora compose, nothing duplicated)");
const allRows = db.get("SELECT COUNT(*) n FROM ucos_universes").n;
ok(allRows === discovered.length, "the live registry equals the discovered set", allRows + " vs " + discovered.length);
ok(ucos.DOCS.length >= 7, "the registry now carries every corpus", ucos.DOCS.map(d => d.code).join(","));

console.log("\n" + (failed ? "✗ " + failed + " check(s) failed" : "✓ all markdown-corpus checks passed") + "  (" + passed + " passed)");
process.exit(failed ? 1 : 0);
