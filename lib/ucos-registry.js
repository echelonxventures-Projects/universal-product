/* UCOS Ω∞ · the frozen registry as a first-class corpus source.
   --------------------------------------------------------------------------
   `_registry/*.json` is the platform's constitutional source of truth: the
   frozen primitives, the canonical terminology, the domain-ownership matrix
   and the 93-artifact manifest. Before this module it was a PARALLEL source
   of truth — `_registry/project.js` projected 93 markdown artifacts from it
   while the runtime derived everything from the corpora, and neither world
   knew the other existed. That is a Law 002 (Knowledge Once) violation: the
   same concept was defined twice, in two registries that never met.

   This module closes the gap by making the registry a CORPUS DOCUMENT — the
   same normalized shape `parseDocument()` emits (parts · sections · concepts ·
   registries), produced from JSON instead of text. One parser contract, one
   seed path, one universe-discovery walk. The registry stops being parallel
   paper and becomes the head of the same tree the corpora feed.

   What the registry declares, mapped onto the corpus's own vocabulary:
     primitives (27)  → concepts + a registry list; the frozen atoms. They are
                        NOT universes — a universe is a projection of a
                        primitive, never the primitive itself, so the two may
                        share a NAME without sharing an identity (the 19
                        collisions are the point: the registry is what makes
                        them resolvable instead of silently duplicated).
     terms (31)       → concepts + the canonical-terminology registry list.
     domains (19)     → concepts + the domain-ownership registry list.
     artifacts        → UNIVERSES — each is a live, operable entity, exactly
                        like a corpus-declared universe. This is the "engines
                        instead of markdown" half: an artifact stops being a
                        file nothing reads and becomes something the generic
                        engine can create, list and validate.

   The declaration channel is data on the DOCS row (`declare`), so a registry
   that grows a new declaration vocabulary needs a JSON key, not a code change. */
"use strict";

const fs = require("fs");
const path = require("path");
const ROOT = path.resolve(__dirname, "..");
const REG = path.join(ROOT, "_registry");

const ucos = require("./ucos.js");
const found = require("./ucos-foundations.js");

/* the registry files, in the order the manifest owns them. Missing files are
   tolerated (a corpus that ships fewer registries still parses) but reported
   in the parse meta so the console never silently under-counts.
   universes.json is deliberately absent: the universe declarations were folded
   into the canonical registry (lib/canonical.js) and this file list is the
   authored vocabulary only. */
const FILES = {
  primitives: "primitives.json",
  terminology: "terminology.json",
  domains: "domains.json",
  manifest: "manifest.json",
  codebase: "codebase.json",
  roadmap: "roadmap.json",
  classification: "classification.json"
};

/* the authored registry files, read RAW — the compile step's input. The runtime
   never reads these: it reads the compiled canonical registry through load()
   below, so the JSON is the authored input and the seal is the runtime's only
   declaration source (Law 002). */
function loadFile(name) {
  const p = path.join(REG, FILES[name]);
  try {
    const raw = fs.readFileSync(p, "utf8");
    const j = JSON.parse(raw);
    return { ok: true, json: j, bytes: raw.length, file: FILES[name] };
  } catch (e) { return { ok: false, error: e.code === "ENOENT" ? "missing" : "malformed", file: FILES[name] }; }
}
function loadContentFiles() {
  const map = {};
  try { Object.assign(map, JSON.parse(fs.readFileSync(path.join(REG, "content-map.json"), "utf8")).mapping || {}); } catch (e) { }
  const blocks = {};
  for (const [src, file] of Object.entries(CONTENT_FILES)) {
    try { blocks[src] = JSON.parse(fs.readFileSync(path.join(REG, file), "utf8")).content || {}; } catch (e) { blocks[src] = {}; }
  }
  return { map, blocks };
}
function readRegistryFiles() {
  const out = {};
  for (const name of Object.keys(FILES)) out[name] = loadFile(name).ok ? loadFile(name).json : null;
  out.contentMap = loadContentFiles();
  return out;
}

/* the RUNTIME read: the compiled canonical registry. Every accessor below resolves
   to the sealed artifact, so the platform declares what it was sealed against and
   nothing else — no second copy of the authored JSON is ever live. */
function load(name) {
  const files = require("./canonical.js").registryFiles();
  const j = files ? files[name] : null;
  if (!j) return { ok: false, error: "missing", file: FILES[name] };
  return { ok: true, json: j, file: FILES[name] };
}
function loadContentMap() {
  const cm = (require("./canonical.js").registryFiles() || {}).contentMap;
  return cm || { map: {}, blocks: {} };
}
function contentBlock(cm, artifactId) {
  const route = (cm || loadContentMap()).map[artifactId];
  if (!route) return null;
  const src = (cm || loadContentMap()).blocks[route.src];
  return src ? src[route.key] || null : null;
}

/* ---------- the registry's own universe-declaration channel ----------
   The manifest's artifacts are the declaration: each artifact IS a universe
   the platform must make operable. `declare` on the DOCS row points here, and
   discover() admits the items through isExplicitDeclaration — the same
   structural sanity every declaration channel applies, so an artifact whose
   title is prose or an id is refused rather than becoming a broken universe. */
function artifactUniverses() {
  const m = load("manifest");
  if (!m.ok) return [];
  const out = [];
  for (const a of (m.json.artifacts || [])) {
    const nm = ucos.declarationName ? ucos.declarationName(a.title) : String(a.title || "").trim();
    if (!nm || !nm.trim()) continue;
    out.push({ key: found.keyOf(nm), name: nm, artifactId: a.id, owner: a.owner || null });
  }
  return out;
}

/* the canonical registry is the SINGLE SOURCE OF TRUTH for what exists. Every
   universe is declared exactly once there; the corpora retain their concepts and
   provenance but stop being declaration sources, so a universe is added or
   retired by re-compiling — one place, one identity (Law 002).

   The compile is authoritative on the universe's own vocabulary too: each row
   carries the concepts that become its entity's derived fields, so the compile
   loses nothing and a future universe declares its fields with itself.

   Provenance is carried as the row's own sourceDoc/sourceLine — the document
   and line that first declared it — because that is what the console renders,
   what the DB column stores and what the overlap measurement distinguishes a
   corpus declaration from a registry one by. The corpora stop being
   declaration SOURCES; where a universe came from is never erased. */
function universeDeclarations() {
  return universes().map(u => ({
    key: u.key,
    name: u.name,
    sourceDoc: u.sourceDoc,
    sourceLine: u.sourceLine || null,
    concepts: Array.isArray(u.concepts) ? u.concepts.slice() : [],
    registry: u.family || null,
    provenance: { doc: u.sourceDoc, line: u.sourceLine || null, family: u.family || null }
  }));
}

/* ---------- the content blocks: each artifact's 28 declared sections ----------
   `content-map.json` routes an artifact id to a block in one of the six
   content registries; the block's keys ARE the artifact's section structure.
   Loaded lazily and tolerated when absent — a registry that ships a manifest
   without content still parses, it just yields universes with fewer derived
   fields. The console never sees a crash for a missing projection. */
const CONTENT_FILES = {
  core: "content-core.json", ext: "content-ext.json", commerce: "content-commerce.json",
  "twin-agent": "content-twin-agent.json", "runtime-data": "content-runtime-data.json",
  "sec-ops-dep-qlt": "content-sec-ops-dep-qlt.json", platform: "content-platform.json"
};
/* a content key is camelCase; the label the registry lists is the readable form
   ("dataModel" → "Data Model"), so a derived field reads like the artifact's own
   vocabulary rather than a JS identifier */
function sectionLabel(key) {
  return String(key || "").replace(/([a-z0-9])([A-Z])/g, "$1 $2").replace(/^./, c => c.toUpperCase());
}

/* ---------- parse: JSON → the corpus's normalized document shape ----------
   Deterministic and pure: the same registry bytes always yield the same
   outline, so the existing content-digest gate (`ucos.digest`) decides
   whether a re-seed is necessary, exactly as it does for a text corpus. */
function parseRegistry() {
  const parts = [], sections = [], concepts = [], registries = [];
  const meta = { lines: 0, chars: 0, missing: [], malformed: [] };

  const seenName = new Set();
  /* the registry's lists are VOCABULARY and STRUCTURE, not universe families: a primitive
     is an atom, a term is a name, a domain is an ownership scope, and an artifact's
     sections are its template — none is a projection. Only the "Declared Artifacts" list
     names universes (the declaration channel selects it). The flag is read by discovery so
     the reconstructed channel cannot promote a vocabulary word or a section label into a
     universe it was never declared to be. */
  const pushRegistry = (sec, label, items, kind) => {
    if (!items.length) return;
    const key = ucos.keyOf(label);
    const names = items.map(i => i.name);
    const noUniverses = kind !== "declaration";
    sec.registries.push({ key, label, items: names, count: names.length, line: sec.line });
    registries.push({ doc: "ureg", part: sec.partNo, container: "section", container_key: sec.key, key, label, items: names, count: names.length, line: sec.line, labelOwn: true, noUniverses });
    if (kind === "fields") {
      /* an artifact's section labels are its STRUCTURE, not concept definitions: every
         artifact carries the same constitutional section template by the corpus's own
         design, so "Certification" under every artifact is one slot per artifact named alike, not
         competing authorities for one concept. Registering them in the concept table
         handed the authority criterion 93 owners per name and 47 duplicate keys. They
         become the artifact universe's derived FIELD labels instead (discover() reads
         them off the section), while the registry list above still exposes the artifact's
         section vocabulary as browsable, traceable data. */
      sec.fieldLabels = (sec.fieldLabels || []).concat(names);
      return;
    }
    for (const it of items) {
      if (!it.name) continue;
      const k = ucos.keyOf(it.name);
      if (!k || k.length < 2) continue;
      /* one name, one concept. The registry's three vocabularies are one identity in
         three aspects — the domain says it OWNS the primitive, the term is the
         primitive's canonical name — so the same word under Frozen Primitives, Canonical
         Terms and Domain Ownership is one concept registered under its first layer, not
         three. All three registry lists above still carry it; only the concept table,
         which keys by name, keeps it once (Knowledge Once where identity lives). */
      if (seenName.has(k)) continue;
      seenName.add(k);
      const c = { key: k, name: it.name, line: sec.line, doc: "ureg", part: sec.partNo, container: "section", container_key: sec.key, container_name: sec.name };
      sec.concepts.push(c);
      concepts.push(c);
    }
  };

  let line = 1;
  const section = (no, name, label) => {
    const key = ucos.keyOf(name) || ("registry_" + no);
    const qkey = "ureg:" + key;
    const s = { qkey, no, key, name, partNo: 1, line: line++, concepts: [], registries: [], meta: {} };
    sections.push(s);
    return s;
  };

  /* part 1 — the whole registry is one part; the sections are its registries */
  parts.push({ no: 1, label: "REG", title: "Frozen Constitutional Registry", line: 1 });

  {
    const s = section(1, "Frozen Primitives");
    const m = loadFile("primitives");
    if (!m.ok) { meta.missing.push("primitives"); }
    else {
      meta.chars += m.bytes;
      pushRegistry(s, "Frozen Primitives", (m.json.primitives || []).map(p => ({ name: p.name })), "vocab");
    }
  }
  {
    const s = section(2, "Canonical Terminology");
    const m = loadFile("terminology");
    if (!m.ok) { meta.missing.push("terminology"); }
    else {
      meta.chars += m.bytes;
      pushRegistry(s, "Canonical Terms", (m.json.terms || []).map(t => ({ name: t.canonicalName })), "vocab");
    }
  }
  {
    const s = section(3, "Domain Ownership");
    const m = loadFile("domains");
    if (!m.ok) { meta.missing.push("domains"); }
    else {
      meta.chars += m.bytes;
      pushRegistry(s, "Domain Ownership", (m.json.domains || []).map(d => ({ name: d.name })), "vocab");
    }
  }
  {
    /* the categories every domain sits in — one classification, so the registry is
       browsable and searchable by category as well as by owner */
    const s = section(4, "Domain Categories");
    const m = loadFile("domains");
    if (m.ok) pushRegistry(s, "Domain Categories", (m.json.categories || []).map(c => ({ name: c.name })), "vocab");
    /* the constitution's laws and the kernel parts are declarations too: searchable by name */
    if (m.ok) pushRegistry(s, "Constitutional Laws", (m.json.laws || []).map(l => ({ name: l.name })), "vocab");
    if (m.ok) pushRegistry(s, "Kernel Parts", (m.json.kernel || []).map(k => ({ name: k.name })), "vocab");
  }
  {
    /* the manifest's artifacts — registered as concepts AND declared as
       universes (the universe declaration is separate, below, so discovery
       admits them through the same channel every corpus uses) */
    const s = section(5, "Constitutional Artifacts");
    const m = loadFile("manifest");
    if (!m.ok) { meta.missing.push("manifest"); }
    else {
      meta.chars += m.bytes;
      pushRegistry(s, "Declared Artifacts", (m.json.artifacts || []).map(a => ({ name: a.title })), "declaration");
      /* each artifact's 28-section content block is its substance — the prose a
         projected markdown file would carry, kept as DATA instead. Concepts are
         derived from the block's own section keys, so a universe's fields mirror
         the artifact's declared structure and a new section appears with no code
         change. This is what makes an artifact an ENGINE rather than a document:
         its content becomes the operable entity's derived attribute set.

         Each artifact gets its own SECTION named exactly like the artifact,
         because discovery attaches concepts to the universe whose name matches
         their container — the artifact's sections must sit under the artifact's
         own name to become that universe's derived fields. */
      const cm = loadContentFiles();
      let no = 6;
      for (const a of (m.json.artifacts || [])) {
        const block = contentBlock(cm, a.id);
        if (!block) continue;
        const keys = Object.keys(block).filter(k => String(block[k] || "").trim());
        if (!keys.length) continue;
        const as = section(no++, a.title);
        pushRegistry(as, a.title + " Sections", keys.map(k => ({ name: sectionLabel(k) })), "fields");
      }
    }
  }

  meta.lines = line;
  meta.sections = sections.length;
  meta.concepts = concepts.length;
  meta.registries = registries.length;
  return {
    doc: "ureg", file: path.join("_registry", ""), code: "UREG",
    name: "UCOS Ω∞ — Frozen Constitutional Registry (primitives · terms · domains · artifacts)",
    parts, sections, articles: [], concepts, registries, meta
  };
}

/* ---------- Law 002 measured where it matters: the runtime ----------
   The doc-side audit (`_registry/audit.js`) proves the markdown is internally
   consistent. It cannot see the corpora. This does: it reports every registry
   concept whose key a CORPUS also declares as a universe, so cross-source
   duplication is MEASURED rather than assumed absent.

   The registry's own artifact declarations are excluded — a universe the
   registry declares is the registry's projection, not a duplication of a
   corpus concept. What counts is a concept the registry declares as an ATOM
   (primitive/term/domain) that a corpus independently declares as a UNIVERSE:
   the same name at two layers. Under the unified registry these are recorded
   as one identity (the primitive is the stored atom, the universe is its
   projection), but an operator must be able to SEE the overlap, because a
   silent overlap is how Knowledge Once actually breaks. */
function overlap(parsed) {
  const P = parsed || ((require("./canonical.js").parsed() || {}).ureg) || parseRegistry();
  const names = new Set(P.concepts.map(c => c.key));
  const uni = require("./ucos-universes.js").discover();
  const hits = uni.filter(u => names.has(u.key) && u.sourceDoc !== "ureg");
  const prim = new Set(primitives().map(p => found.keyOf(p.name)));
  const trm = new Set(terms().map(t => found.keyOf(t.canonicalName)));
  const dom = new Set(domains().map(d => found.keyOf(d.name)));
  const kindOf = k => prim.has(k) ? "primitive" : trm.has(k) ? "term" : dom.has(k) ? "domain" : "artifact";
  return {
    registryConcepts: names.size,
    corpusUniverses: uni.length,
    overlap: hits.map(u => ({ key: u.key, kind: kindOf(u.key), registryName: (P.concepts.find(c => c.key === u.key) || {}).name, universeName: u.name, sourceDoc: u.sourceDoc })),
    overlapCount: hits.length,
    byKind: hits.reduce((a, u) => { const k = kindOf(u.key); a[k] = (a[k] || 0) + 1; return a; }, {})
  };
}

/* ---------- meta_lists: the registry's vocabularies become platform vocabulary ----------
   Primitives, canonical terms and domains are the constitution's own controlled
   vocabularies. Seeding them as meta_lists rows (the same store every other
   registry list uses) makes them selectable, filterable and editable wherever a
   vocabulary is consumed — an operator picks a primitive from a dropdown, and a
   new term the registry ships is readable with no code change.

   Additive merge, exactly like productUniverses: an operator's addition survives
   a registry upgrade, because the seed only re-asserts what the registry
   declares and never what it does not. */
function seedLists(Db) {
  const J = (v, d) => { try { return JSON.parse(v == null || v === "" ? (d || "[]") : v); } catch (e) { return d || []; } };
  const put = (name, declared) => {
    if (!declared.length) return;
    const ex = Db.get("SELECT items FROM meta_lists WHERE name=?", name);
    const kept = ex ? J(ex.items, []).filter(it => it && it.key && !declared.some(d => d.key === it.key)) : [];
    Db.run("INSERT INTO meta_lists(name,label,items,seeded_from) VALUES(?,?,?,'ureg') "
      + "ON CONFLICT(name) DO UPDATE SET items=excluded.items, seeded_from=excluded.seeded_from",
      name, name, JSON.stringify(declared.concat(kept)));
  };
  put("constitutionalPrimitives", primitives().map(p => ({ key: found.keyOf(p.name), name: p.name, id: p.id, owner: ownerOf(p.name), frozen: p.frozen !== false })));
  put("canonicalTerms", terms().map(t => ({ key: found.keyOf(t.canonicalName), name: t.canonicalName, termId: t.termId, ownerDomain: ownerOf(t.canonicalName) })));
  put("constitutionalCategories", categories().map(c => ({ key: found.keyOf(c.name), name: c.name, categoryId: c.categoryId, covers: c.covers })));
  put("constitutionalDomains", domains().map(d => ({ key: found.keyOf(d.name), name: d.name, domainId: d.domainId, category: d.category, owns: d.owns, contract: d.contract })));
  return {
    constitutionalPrimitives: primitives().length,
    canonicalTerms: terms().length,
    constitutionalCategories: categories().length,
    constitutionalDomains: domains().length
  };
}

/* ---------- read API ---------- */
function primitives() {
  const m = load("primitives");
  return m.ok ? (m.json.primitives || []) : [];
}
function terms() {
  const m = load("terminology");
  return m.ok ? (m.json.terms || []) : [];
}
function domains() {
  const m = load("domains");
  return m.ok ? (m.json.domains || []) : [];
}
function artifacts() {
  const m = load("manifest");
  return m.ok ? (m.json.artifacts || []) : [];
}
function categories() {
  const m = load("domains");
  return m.ok ? (m.json.categories || []) : [];
}
/* ownership is declared ONCE, by the domain that owns a primitive or term (domains.json
   `owns`). Primitives and terms carry no owner field of their own, so an owner can never
   be stated twice and disagree. */
function ownerOf(name) {
  const d = domains().find(x => (x.owns || []).includes(name));
  return d ? d.name : null;
}
/* the declared universes — the single source of truth for what exists. Every
   universe the platform operates is a row in the compiled canonical registry
   (Law 002: Knowledge Once); the corpora are provenance, never a second
   declaration. */
function universes() {
  return require("./canonical.js").universes();
}

module.exports = {
  FILES, CONTENT_FILES, load, loadFile, loadContentFiles, readRegistryFiles, parseRegistry, artifactUniverses, universeDeclarations, overlap, seedLists,
  primitives, terms, domains, artifacts, categories, ownerOf, universes, contentBlock, sectionLabel
};
