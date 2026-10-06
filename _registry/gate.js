/* UCOS Ω∞ · the integrity gate — the five criteria, proven not claimed.
   --------------------------------------------------------------------------
   The mandate is Zero Duplicate · Zero Partial · Zero Overlap · Zero Missing ·
   No Leakage over the single source of truth. Asserting it in prose proves
   nothing; this gate makes each criterion an executable check over the COMPILED
   registry, so a compile that violates any of them is refused before it ships a
   seal, and an operator can re-verify the seal at any time.

   The strongest check here is the last: the compiled registry must be EXACTLY a
   parse of the sources — nothing invented (leakage), nothing dropped (partial).
   A byte-level comparison against a fresh, independent parse is the only proof
   that holds when the compiler itself is what changed.

   run(payload) is pure: it takes the compiled registry and returns
   { ok, checked, passed, fails:[...] }. No DB, no boot — the boot-time parity
   checks (does the live registry equal the compiled one?) live in the test. */
"use strict";

const path = require("path");
const ROOT = path.resolve(__dirname, "..");

function check(name, ok, detail) { return { name, ok: !!ok, detail: detail || null }; }

/* every key a class declares, once */
function keySet(rows, field) {
  const m = new Map();
  for (const r of rows) {
    const k = r[field];
    if (!k) continue;
    if (!m.has(k)) m.set(k, 0);
    m.set(k, m.get(k) + 1);
  }
  return m;
}

function run(payload) {
  const fails = [];
  const checks = [];
  const record = c => { checks.push(c); if (!c.ok) fails.push(c); };

  const P = payload.parsed;
  const docs = Object.keys(P);
  const conceptRows = docs.reduce((a, d) => a + P[d].concepts.length, 0);

  /* ---------- ZERO DUPLICATE — one identity per declaration ---------- */
  const ukeys = keySet(payload.universes, "key");
  record(check("zero-duplicate · universe keys are unique",
    ukeys.size === payload.universes.length,
    payload.universes.length - ukeys.size + " repeated keys"));
  /* concepts are per-document content with provenance: the same term discussed in
     eleven documents is eleven rows, not eleven identities. Identity is keyed by
     (document, key) — a duplicate THERE is a real duplication. */
  let conceptDupes = 0;
  for (const d of docs) {
    const seen = new Set();
    for (const c of P[d].concepts) { if (seen.has(c.key)) conceptDupes++; else seen.add(c.key); }
  }
  record(check("zero-duplicate · concept (document, key) pairs are unique", conceptDupes === 0, conceptDupes + " repeated (doc,key) pairs"));
  const rf = payload.registryFiles;
  const primKeys = keySet(rf.primitives.primitives, "name");
  const termKeys = keySet(rf.terminology.terms, "canonicalName");
  const domKeys = keySet(rf.domains.domains, "name");
  const artKeys = keySet(rf.manifest.artifacts, "title");
  record(check("zero-duplicate · atom classes are unique within themselves",
    primKeys.size === rf.primitives.primitives.length && termKeys.size === rf.terminology.terms.length
    && domKeys.size === rf.domains.domains.length && artKeys.size === rf.manifest.artifacts.length,
    "primitives " + (rf.primitives.primitives.length - primKeys.size) + ", terms "
    + (rf.terminology.terms.length - termKeys.size) + ", domains " + (rf.domains.domains.length - domKeys.size)
    + ", artifacts " + (rf.manifest.artifacts.length - artKeys.size)));

  /* ---------- ZERO PARTIAL — every declaration is complete ---------- */
  const partialUniverses = payload.universes.filter(u => !u.key || !u.name || !u.sourceDoc || !u.sourceLine).length;
  record(check("zero-partial · every universe carries key, name and provenance (doc + line)",
    partialUniverses === 0, partialUniverses + " universes incomplete"));
  const partialDocs = docs.filter(d => !Array.isArray(P[d].parts) || !Array.isArray(P[d].sections)
    || !Array.isArray(P[d].articles) || !Array.isArray(P[d].concepts) || !Array.isArray(P[d].registries)
    || !P[d].meta || P[d].meta.lines == null).length;
  record(check("zero-partial · every document parse is structurally complete", partialDocs === 0, partialDocs + " documents incomplete"));
  const partialTerms = rf.terminology.terms.filter(t => !t.canonicalName || !t.ownerDomain).length;
  const partialDomains = rf.domains.domains.filter(d => !d.name || !Array.isArray(d.owns)).length;
  const partialArts = rf.manifest.artifacts.filter(a => !a.id || !a.title).length;
  record(check("zero-partial · every atom carries its required fields",
    partialTerms + partialDomains + partialArts === 0,
    "terms " + partialTerms + ", domains " + partialDomains + ", artifacts " + partialArts));
  const vocabEmpty = ["productUniverses", "lifecycleStates", "transitionGrammar"].filter(v => !(payload.vocabularies[v] || []).length);
  record(check("zero-partial · every vocabulary the corpus declares is present", !vocabEmpty.length, "empty: " + vocabEmpty.join(", ")));

  /* ---------- ZERO OVERLAP — collisions resolved, never silent ---------- */
  /* a registry atom (primitive/term/domain) that a corpus also declares as a
     universe is one identity in two aspects: the atom is the stored vocabulary,
     the universe is its projection. The overlap must be MEASURED and every
     colliding key must resolve to exactly one universe row. */
  const atomKeys = new Set([...primKeys.keys(), ...termKeys.keys(), ...domKeys.keys(), ...artKeys.keys()].map(k => String(k).toLowerCase().replace(/[^a-z0-9]+/g, "_")));
  const overlapped = payload.universes.filter(u => atomKeys.has(u.key));
  const overlapResolved = overlapped.every(u => ukeys.get(u.key) === 1);
  record(check("zero-overlap · every atom/universe collision is measured and resolves to one identity",
    overlapResolved, overlapped.length + " collisions, " + overlapped.filter(u => ukeys.get(u.key) !== 1).length + " unresolved"));
  /* the storefront vocabulary and the constitutional registry are two universe
     stores that used to never meet; the compiled registry carries both, so their
     collisions are visible instead of duplicated */
  const prodKeys = new Set(payload.vocabularies.productUniverses.map(v => v.key));
  const vocabCollisions = payload.universes.filter(u => prodKeys.has(u.key)).map(u => u.key);
  record(check("zero-overlap · storefront vocabulary collisions with the constitutional registry are recorded",
    vocabCollisions.every(k => ukeys.get(k) === 1), vocabCollisions.join(", ") || "none"));

  /* ---------- ZERO MISSING — every reference resolves ---------- */
  /* an artifact's content route must point at a block that exists, or the artifact
     is a declaration with no substance */
  const cm = rf.contentMap;
  let missingRoutes = 0;
  for (const a of rf.manifest.artifacts) {
    const route = cm.map[a.id];
    if (!route) { missingRoutes++; continue; }
    const block = (cm.blocks[route.src] || {})[route.key];
    if (!block) missingRoutes++;
  }
  record(check("zero-missing · every artifact's content route resolves to a block",
    missingRoutes === 0, missingRoutes + " unresolved routes"));
  /* a domain's `owns` list points at primitives — a dangling ownership claim is a
     declaration referencing something that does not exist */
  const allNames = new Set([...primKeys.keys(), ...termKeys.keys()].map(k => String(k).toLowerCase().replace(/[^a-z0-9]+/g, "_")));
  const danglingOwns = rf.domains.domains.flatMap(d => (d.owns || []).filter(o => !allNames.has(String(o).toLowerCase().replace(/[^a-z0-9]+/g, "_"))).map(o => d.name + "→" + o));
  record(check("zero-missing · every domain ownership target resolves to a declared atom",
    !danglingOwns.length, danglingOwns.slice(0, 5).join(", ")));
  /* the console's grant surface must cover every view the nav renders — a view whose
     section the surface omits is a button an operator can never authorise, and a '*'
     grant can never light up. The surface the engines actually consult
     (rbac.SECTIONS / prbac.SECTIONS) is compared against the nav HERE, so a regression
     to a hand-maintained list is caught by the gate itself, not only by a test.
     The store surface resolves each leaf through NAVSEC (promotions → offers,
     structure → tenancy, sso → settings) and is closed under the entity router, so it
     is a superset of the resolved nav sections; the platform console has no
     indirection and its surface is its leaves exactly. */
  const rb = require(path.join(ROOT, "lib", "rbac.js"));
  const pb = require(path.join(ROOT, "lib", "prbac.js"));
  const navSec = payload.console.adminNavSec || {};
  const adminUngranted = payload.console.admin.map(k => navSec[k] || k).filter(s => !rb.SECTIONS.includes(s));
  record(check("zero-missing · the store grant surface covers every section the store nav requests",
    !adminUngranted.length, adminUngranted.slice(0, 5).join(", ") + " ungranted"));
  const platUngranted = payload.console.platform.filter(s => !pb.SECTIONS.includes(s));
  record(check("zero-missing · the platform grant surface covers every section the platform nav requests",
    !platUngranted.length, platUngranted.slice(0, 5).join(", ") + " ungranted"));

  /* ---------- NO LEAKAGE — the compiled registry is exactly the sources ---------- */
  /* the compiler is the one thing standing between the sources and the seal, so
     the gate re-derives the parse INDEPENDENTLY and compares. A compiled registry
     that differs from a fresh parse either invented a declaration (leakage) or
     dropped one (partial) — both are refused here. */
  let exact = true, diffWhy = "";
  try {
    const fresh = require(path.join(ROOT, "lib", "ucos.js")).parseSources();
    if (JSON.stringify(fresh) !== JSON.stringify(P)) { exact = false; diffWhy = "the compiled parse differs from a fresh parse of the sources"; }
  } catch (e) { exact = false; diffWhy = "the sources would not re-parse: " + e.message; }
  record(check("no-leakage · the compiled parse is byte-identical to a fresh parse of the sources", exact, diffWhy));
  let navExact = true, navWhy = "";
  try {
    const nav = require(path.join(ROOT, "lib", "canonical.js")).consoleSections();
    if (JSON.stringify(nav) !== JSON.stringify(payload.console)) { navExact = false; navWhy = "the compiled console surface differs from the navs"; }
  } catch (e) { navExact = false; navWhy = "the navs would not extract: " + e.message; }
  record(check("no-leakage · the compiled console surface is exactly what the navs render", navExact, navWhy));

  return {
    ok: !fails.length,
    checked: checks.length,
    passed: checks.length - fails.length,
    fails,
    counts: { universes: payload.universes.length, concepts: conceptRows, documents: docs.length, sections: payload.counts.sections, registries: payload.counts.registries }
  };
}

/* a human-readable verdict — the operator's answer to "is the registry honest?" */
function explain(report) {
  const lines = ["✗ the integrity gate FAILED " + report.fails.length + " of " + report.checked + " checks:"];
  for (const f of report.fails) lines.push("  ✗ " + f.name + (f.detail ? "  →  " + f.detail : ""));
  return lines.join("\n");
}

module.exports = { run, explain, check };
