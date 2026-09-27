/* UCOS Ω∞ · Universe instantiation — every declared universe becomes operable.
   --------------------------------------------------------------------------
   The corpus declares 2,500+ universes, domains and capability meta-models
   (Engineering, Streaming, Cloud, Transportation, Insurance, Advisory, Service
   Robots, Quantitative Sciences…). Before this module they were REGISTERED —
   parsed, counted, graphed, health-checked — but not OPERABLE: you could read
   about "Insurance Product" in the console, but you could not create one.

   This module closes that gap using the corpus's own rule (Architecture3
   Article 4.2: "No hard-coded foundation. No foundation whose existence is
   asserted in code rather than in the registry"). Each universe is instantiated
   as a DATA-DEFINED ENTITY through the platform's generic meta-model engine
   (lib/entity.js): one row in entity_defs, one row in ucos_foundations, zero
   per-universe code. The universe is then live — listable, creatable,
   tenant-scoped, validated and rendered by the generic console, exactly like
   the built-in commerce entities.

   The universe's fields are DERIVED from the corpus itself: its registry lists
   supply the attributes, so the entity's shape is the corpus's shape, never a
   programmer's guess. */
"use strict";

const path = require("path");
const ROOT = path.resolve(__dirname, "..");
const ucos = require("./ucos.js");
const found = require("./ucos-foundations.js");

let _db = null;
const db = () => _db || (_db = require("./db.js"));
const rows = (sql, ...p) => { try { return db().all(sql, ...p) || []; } catch (e) { return []; } };
const get = (sql, ...p) => { try { return db().get(sql, ...p) || null; } catch (e) { return null; } };

/* the corpus writes universes with several vocabularies — "Insurance Meta Model",
   "Streaming Product Meta Model", "Transportation Service", "Advisory Services Engine".
   These patterns mark a declaration as a UNIVERSE rather than an ordinary concept and
   extract the clean name from it. A suffix is stripped ONLY when what remains is a
   substantive domain word ("Insurance" from "Insurance Meta Model"), never when the
   whole name is the domain ("Streaming Product" stays "Streaming Product"): the
   trailing-word forms are complete universe names in the corpus's own vocabulary. */
const UNIVERSE_PATTERNS = [
  /^(.*?)\s+(?:meta[- ]?model|meta model)$/i,
  /^(.*?)\s+(?:service engine|engine)$/i,
  /^(.*?)\s+(?:registry system)$/i
];
/* a registry LABEL names a universe declaration only in these shapes — the corpus
   declares "Insurance Meta Model" (the label) whose items are the universes
   (Insurance, Insurance Advisory, …). Matching the label, not every concept, is
   what keeps prose out of the registry. */
const UNIVERSE_LABEL = /(?:meta[- ]?model|service\s+engine|engine|registry\s+system|universes?|domains?|categories|hierarchy)/i;
/* ... but these labels describe the registry's own machinery or generic groupings, not
   universes — instantiating them as entities would be noise. Matched only when the
   label is PURE machinery ("Registry Meta Model"), never when a domain name leads it
   ("Streaming Product Meta Model" is a real universe declaration). */
const MACHINERY_LABEL = /^(?:universal|master|root|core|foundation|platform|registry|rule|policy|relationship|event|workflow|runtime|api|security|encryption|audit|compliance|governance|ontology|identity|kpi|key)\b/i;
/* the machinery words themselves, so a label like "Policy Registry" can be reduced to
   its non-machinery remainder when that remainder still names a domain */
const MACHINERY_WORDS = /\b(?:universal|master|root|core|foundation|platform|registry|rule|policy|relationship|event|workflow|runtime|api|security|encryption|audit|compliance|governance|ontology|identity|kpi|key|meta[- ]?model|engine|system|categories|hierarchy|domains?|universes?)\b/gi;
/* words that name a FOUNDATION of the registry rather than a universe — they describe
   the registry's own machinery, so instantiating them as entities would be noise */
const REGISTRY_MACHINERY = /^(foundation|universe|domain|primitive|capability|composition|registry|governance|evolution|dependency|graph|identity|parent|lifecycle|certification|discovery|admission|prohibition|invariant|transition|constitution|purpose|structure|scope|authority|security|api|event|data model|validation|compliance|operation|state|rule|rules|append|audit|handle|canonical form)$/i;

/* the canonical name of a declared universe: strip the meta-model/engine suffix
   so "Insurance Meta Model" → "Insurance" and the entity key is short and stable.
   The strip only applies when it leaves a meaningful remainder — "Streaming Product"
   is a complete universe name, not "Streaming" + a "Product" suffix, so names that
   are already clean pass through untouched. */
function cleanName(item) {
  let t = String(item || "").trim().replace(/\s+/g, " ").replace(/[.:;]$/, "");
  for (const re of UNIVERSE_PATTERNS) {
    const m = re.exec(t);
    if (m && m[1] && m[1].trim().length >= 3) { t = m[1].trim(); break; }
  }
  return t;
}
/* a registry item is a universe declaration when it is a short, capitalized NOUN
   PHRASE — the shape of "Insurance", "Cloud Product", "Transportation Service".
   Prose is excluded structurally: no sentence case start, no trailing period, no
   verbs/modals, no digits-as-ids, no drawing characters, no law codes. */
function isUniverse(item) {
  const t = String(item || "").trim();
  if (t.length < 3 || t.length > 42) return false;
  if (REGISTRY_MACHINERY.test(t)) return false;
  if (!/^[A-Z]/.test(t)) return false;                    /* declarations are capitalized noun phrases */
  if (/[.;,]$/.test(t)) return false;                     /* a sentence, not a name */
  if (/^\W+|["“”()\[\]{}]/.test(t)) return false;         /* punctuation / quotes / arrows */
  if (/\d/.test(t)) return false;                         /* digits mark ids, laws, ranges and stats */
  if (/\b(?:is|are|was|were|shall|must|may|will|can|of|the|a|an|and|or|in|on|by|for|to|with|that|which|this|these|those|every|each|all|when|where|if|then|as|at|from|into|its|their|his|her|we|you|they|not|no|per|via|using|based)\b/i.test(t)) return false;
  if (/UMQSOL|UMQSOI|UCOS-|UMQSOCR-DOC|~|≈|%/.test(t)) return false;  /* law codes / stats */
  if (/\s{2,}/.test(t)) return false;                     /* tree-drawing whitespace */
  if (/-/.test(t) && !/^[A-Za-z]+(?:\s+[A-Za-z]+)?$/.test(t.replace(/-/g, " "))) return false;
  if (/^[a-z]/.test(t)) return false;
  return true;
}

/* the attribute set a universe entity exposes — derived from the corpus lists that
   describe the universe, so the form is the corpus's own shape */
function fieldsFor(name, conceptNames) {
  const f = [];
  f.push({ key: "name", label: name + " Name", type: "text", required: true, list: true });
  f.push({ key: "code", label: "Reference", type: "text", list: true });
  f.push({ key: "status", label: "Status", type: "select", options: ["proposed", "drafted", "reviewed", "certified", "canonical", "deprecated", "retired"], list: true });
  /* up to 8 distinctive sibling concepts from the same universe become optional
     attributes — this is the corpus telling us what the entity should carry */
  const seen = new Set([found.keyOf(name)]);
  for (const c of conceptNames) {
    if (f.length >= 11) break;
    const k = found.keyOf(c);
    if (!k || k.length < 3 || seen.has(k)) continue;
    seen.add(k);
    f.push({ key: k.slice(0, 28), label: c, type: "text" });
  }
  f.push({ key: "attrs", label: "Attributes", type: "json" });
  return f;
}

/* ---------- discover every universe the three corpora declare ----------
    Walks the parsed registry (not the module, not the DB) and returns the set of
    declared universes with their provenance, so the instantiation is traceable
    back to the exact document and line. Deterministic: same corpus → same set.

    A universe is declared by a LABELLED LIST whose label names a meta-model /
    engine / domain family ("Insurance Meta Model"); its items are the universes.
    Grounding on those labels — not on free concepts — is what keeps prose out. */
function discover() {
  const parsed = ucos.parseAll();
  const out = new Map();
  for (const docId of Object.keys(parsed)) {
    const P = parsed[docId];
    for (const reg of P.registries) {
      const label = String(reg.label || "").trim();
      if (!UNIVERSE_LABEL.test(label)) continue;
      /* the label itself can BE the declaration: "Streaming Product Meta Model" is a
         one-item list declaring "Streaming Product". Reduce the label to its domain
         remainder and, if that remainder is a clean universe name, register it. */
      const reduced = label.replace(MACHINERY_WORDS, " ").replace(/\s+/g, " ").trim();
      const want = reduced && reduced.length >= 3 && !MACHINERY_LABEL.test(reduced) ? reduced : null;
      if (want && isUniverse(want) && !out.has(found.keyOf(cleanName(want))))
        out.set(found.keyOf(cleanName(want)), { key: found.keyOf(cleanName(want)), name: cleanName(want), sourceDoc: docId, sourceLine: reg.line, concepts: [], registry: label });
      for (const item of reg.items) {
        if (!isUniverse(item)) continue;
        const nm = cleanName(item);
        if (!nm || !isUniverse(nm)) continue;
        const k = found.keyOf(nm);
        if (!k) continue;
        if (!out.has(k)) out.set(k, { key: k, name: nm, sourceDoc: docId, sourceLine: reg.line, concepts: [], registry: label });
      }
    }
  }
  /* attach corpus concepts to the universe whose name they sit under — concepts
     become the derived attribute set of the universe's entity */
  for (const docId of Object.keys(parsed)) {
    for (const c of parsed[docId].concepts) {
      const k = found.keyOf(cleanName(c.container_name || c.name));
      const u = out.get(k);
      if (u && u.concepts.length < 40) u.concepts.push(c.name);
    }
  }
  return [...out.values()].sort((a, b) => a.name.localeCompare(b.name));
}

/* ---------- instantiate: register the foundation + create the live entity ----------
    Idempotent — re-running on every boot never duplicates a row and never rewrites
    an operator's customizations (INSERT OR IGNORE on both tables). Returns what it
    did so the boot banner and the console can report the real state. */
function instantiate(opts) {
  const universe = opts || {};
  const def = {
    table: null, storage: "json", pk: "id",
    label: universe.name,
    icon: "🧬",
    perm: { read: ["admin", "platform"], write: ["admin", "platform"] },
    fields: fieldsFor(universe.name, universe.concepts || [])
  };
  const entityKey = "uv_" + universe.key;
  /* register the foundation (admission rules apply: unique identity, resolvable parent,
     acyclic). Universes are primitives of the registry — they have no parent. */
  if (!get("SELECT 1 ok FROM ucos_foundations WHERE key=?", universe.key)) {
    const r = found.register(universe.name, {
      universe: null, lifecycle: "canonical", certified: true,
      classification: "universe", sourceDoc: universe.sourceDoc,
      sourceLine: universe.sourceLine, discovery: entityKey
    });
    if (!r.ok) return { ok: false, key: universe.key, fails: r.fails };
  }
  /* the live entity: one row in entity_defs, rendered and CRUD-ed by the generic engine */
  db().run("INSERT OR IGNORE INTO entity_defs(key,scope,tenant_id,def) VALUES(?,?,?,?)",
    entityKey, "platform", 0, JSON.stringify(def));
  db().run("INSERT OR IGNORE INTO ucos_universes(key,name,source_doc,source_line,entity_key,concepts,instantiated_at) VALUES(?,?,?,?,?,?,?)",
    universe.key, universe.name, universe.sourceDoc, universe.sourceLine || null, entityKey, universe.concepts.length, new Date().toISOString());
  return { ok: true, key: universe.key, entityKey, concepts: universe.concepts.length };
}

/* instantiate every discovered universe. Idempotent; safe on every boot. */
function instantiateAll() {
  const list = discover();
  let made = 0, failed = 0;
  for (const u of list) {
    const r = instantiate(u);
    if (r.ok) made++; else failed++;
  }
  return { discovered: list.length, instantiated: made, failed, universes: list.length };
}

/* ---------- read API ---------- */
function list() {
  return rows("SELECT u.key,u.name,u.source_doc,u.source_line,u.entity_key,u.concepts,u.instantiated_at,"
    + " (SELECT COUNT(*) FROM entity_data d WHERE d.entity=u.entity_key) AS records,"
    + " (SELECT lifecycle FROM ucos_foundations f WHERE f.key=u.key) AS lifecycle"
    + " FROM ucos_universes u ORDER BY u.name");
}
function stats() {
  const total = (rows("SELECT COUNT(*) n FROM ucos_universes")[0] || {}).n || 0;
  const live = (rows("SELECT COUNT(*) n FROM ucos_foundations WHERE lifecycle='canonical'")[0] || {}).n || 0;
  const records = (rows("SELECT COUNT(*) n FROM entity_data WHERE entity LIKE 'uv_%'")[0] || {}).n || 0;
  const expected = discover().length;
  return { declared: expected, instantiated: total, live, records, coverage: expected ? Math.round(100 * total / expected) : 0 };
}

module.exports = { discover, cleanName, isUniverse, fieldsFor, instantiate, instantiateAll, list, stats };
