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
  let registerCounts = null;
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
  const partialTerms = rf.terminology.terms.filter(t => !t.canonicalName || !t.definition).length;
  const partialDomains = rf.domains.domains.filter(d => !d.name || !d.domainId || !d.category || !Array.isArray(d.owns) || !d.owns.length
    || !Array.isArray(d.responsible) || !(Array.isArray(d.notResponsible) || Array.isArray(d.mustObey))).length;
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

  /* ---------- THE REGISTER — one categorised owner for every declaration ----------
     Ownership is declared once, in domains.json: a domain's `owns` list. Every primitive
     and term must appear in exactly one such list, every domain in exactly one declared
     category, and every artifact must name an owning domain. */
  {
    const D = rf.domains, doms = D.domains, cats = D.categories || [];
    const owners = new Map();
    for (const d of doms) for (const o of d.owns || []) owners.set(o, (owners.get(o) || []).concat(d.name));
    const twice = [...owners].filter(([, v]) => v.length > 1).map(([k, v]) => k + " (" + v.join(", ") + ")");
    record(check("zero-duplicate · every primitive and term is owned by at most one domain", !twice.length, twice.slice(0, 5).join("; ")));
    const ids = keySet(doms, "domainId"), catIds = keySet(cats, "categoryId"), catNames = keySet(cats, "name");
    record(check("zero-duplicate · domain ids, category ids and category names are unique",
      ids.size === doms.length && catIds.size === cats.length && catNames.size === cats.length,
      (doms.length - ids.size) + " domain ids, " + (cats.length - catIds.size) + " category ids, " + (cats.length - catNames.size) + " category names repeated"));
    const unownedPrims = rf.primitives.primitives.filter(p => !owners.has(p.name)).map(p => p.name);
    const unownedTerms = rf.terminology.terms.filter(t => !owners.has(t.canonicalName)).map(t => t.canonicalName);
    record(check("zero-missing · every primitive and term has an owning domain",
      !unownedPrims.length && !unownedTerms.length, unownedPrims.concat(unownedTerms).slice(0, 8).join(", ")));
    const catSet = new Set(cats.map(c => c.categoryId));
    const uncategorised = doms.filter(d => !catSet.has(d.category)).map(d => d.name);
    const emptyCats = cats.filter(c => !doms.some(d => d.category === c.categoryId)).map(c => c.name);
    record(check("zero-missing · every domain sits in a declared category, and every category holds a domain",
      !uncategorised.length && !emptyCats.length, "uncategorised: " + uncategorised.join(", ") + "; empty: " + emptyCats.join(", ")));
    const domNames = new Set(doms.map(d => d.name));
    const unownedArts = rf.manifest.artifacts.filter(a => !domNames.has(a.owner)).map(a => a.id);
    record(check("zero-missing · every artifact names an owning domain", !unownedArts.length, unownedArts.slice(0, 8).join(", ")));
    const banned = new Set((rf.primitives.prohibited || []).map(x => String(x).toLowerCase()));
    const reserved = rf.terminology.terms.map(t => t.canonicalName).concat(doms.map(d => d.name)).filter(n => banned.has(String(n).toLowerCase()));
    record(check("zero-overlap · no term or domain takes a name the constitution reserves for projections", !reserved.length, reserved.join(", ")));
    /* a domain's contract is its own architecture artifact. Domains declared before their
       contract is written are counted, and the count may only fall (register-baseline.json) */
    const artById = new Map(rf.manifest.artifacts.map(a => [a.id, a]));
    const noContract = doms.filter(d => !d.contract || !artById.has(d.contract) || artById.get(d.contract).owner !== d.name).map(d => d.name);
    let allowed = Infinity;
    try { allowed = JSON.parse(require("fs").readFileSync(path.join(__dirname, "register-baseline.json"), "utf8")).domainsWithoutContract; } catch (e) { }
    record(check("zero-missing · every domain's contract is an artifact it owns (" + noContract.length + " outstanding, baseline " + allowed + ")",
      noContract.length <= allowed, noContract.join(", ")));
    /* the law register: every law stated once, sourced, and its enforcement declared. The
       count of laws not yet fully enforced may only fall (register-baseline.json) */
    const laws = D.laws || [];
    const lawIds = keySet(laws, "lawId"), lawNames = keySet(laws, "name");
    const docIds = new Set(Object.keys(P));
    const srcOk = s => { const d = String(s).split(":")[0].split(" ")[0]; return docIds.has(d) || require("fs").existsSync(path.join(ROOT, d)); };
    const partialLaws = laws.filter(l => !l.lawId || !l.name || !l.statement || !(l.sources || []).length || !["enforced", "partial", "planned"].includes(l.status)
      || (l.status !== "planned" && !(l.enforcedBy || []).length)).map(l => l.lawId || l.name);
    record(check("zero-partial · every law has a statement, a source, a status and (unless planned) its enforcement",
      lawIds.size === laws.length && lawNames.size === laws.length && !partialLaws.length, partialLaws.join(", ")));
    const unsourced = laws.flatMap(l => (l.sources || []).filter(x => !srcOk(x)).map(x => l.lawId + "→" + x));
    record(check("zero-missing · every law source is a declared document or an existing file", !unsourced.length, unsourced.slice(0, 5).join(", ")));
    const notEnforced = laws.filter(l => l.status !== "enforced").map(l => l.lawId);
    let allowedLaws = Infinity;
    try { allowedLaws = JSON.parse(require("fs").readFileSync(path.join(__dirname, "register-baseline.json"), "utf8")).lawsNotEnforced; } catch (e) { }
    record(check("zero-missing · laws not yet fully enforced (" + notEnforced.length + ", baseline " + allowedLaws + ")", notEnforced.length <= allowedLaws, notEnforced.join(", ")));

    /* the kernel: every part has one owning domain */
    const kernel = D.kernel || [];
    const badKernel = kernel.filter(k => !k.partId || !k.statement || !domNames.has(k.owner)).map(k => k.partId || k.name);
    record(check("zero-missing · every kernel part has one owning domain", keySet(kernel, "partId").size === kernel.length && !badKernel.length, badKernel.join(", ")));

    /* the code-module map: every file under the declared folders has exactly one home */
    const cb = rf.codebase || { modules: [] };
    const fs = require("fs");
    const modPaths = keySet(cb.modules, "path");
    const ownersOf = m => m.parts ? m.parts.map(p => p.owner) : [m.owner];
    const badOwner = cb.modules.filter(m => !ownersOf(m).length || ownersOf(m).some(o => !domNames.has(o))).map(m => m.path);
    record(check("zero-duplicate · every code module is mapped once, to declared domains",
      modPaths.size === cb.modules.length && !badOwner.length, (cb.modules.length - modPaths.size) + " repeated; unknown owners: " + badOwner.join(", ")));
    const onDisk = [];
    for (const pattern of cb.covers || []) {
      const [dir, glob] = pattern.includes("/") ? [pattern.slice(0, pattern.lastIndexOf("/")), pattern.slice(pattern.lastIndexOf("/") + 1)] : [".", pattern];
      const re = new RegExp("^" + glob.replace(/[.]/g, "\\.").replace(/\*/g, "[^/]*") + "$");
      let entries = [];
      try { entries = fs.readdirSync(path.join(ROOT, dir), { withFileTypes: true }); } catch (e) { }
      for (const e of entries) if (e.isFile() && re.test(e.name)) onDisk.push(dir === "." ? e.name : dir + "/" + e.name);
    }
    const unmapped = onDisk.filter(f => !modPaths.has(f));
    const vanished = cb.modules.map(m => m.path).filter(f => !onDisk.includes(f));
    record(check("zero-missing · every code file has a home, and every home is a real file",
      !unmapped.length && !vanished.length, "unmapped: " + unmapped.slice(0, 5).join(", ") + "; missing: " + vanished.slice(0, 5).join(", ")));

    /* the build path: steps name declared domains; a done step names the amendments that delivered it */
    const rm = rf.roadmap || { steps: [], decisions: [] };
    const amdIds = new Set((D.amendments || []).map(a => a.amendmentId));
    const badSteps = rm.steps.filter(st => !["done", "in-progress", "planned"].includes(st.status) || (st.domains || []).some(d => !domNames.has(d))
      || (st.status === "done" && (!(st.deliveredBy || []).length || st.deliveredBy.some(a => !amdIds.has(a))))).map(st => st.stepId);
    record(check("zero-partial · every build step names real domains, and every done step its amendments",
      keySet(rm.steps, "stepId").size === rm.steps.length && keySet(rm.decisions, "decisionId").size === rm.decisions.length && !badSteps.length, badSteps.join(", ")));

    /* the concept register: the rules name declared domains, every reviewed container names a
       declared domain (or Structural), each concept appears once, the sealed register is exactly
       a fresh derivation, and unplaced concepts and unreviewed containers may only fall */
    const cl = rf.classification || { owners: [], containers: {} };
    const ruleOwners = (cl.owners || []).map(r => r.owner).concat(cl.subjects ? [cl.subjects.owner] : []);
    const badRules = ruleOwners.filter(o => !domNames.has(o));
    const badReviews = Object.entries(cl.containers || {}).filter(([, r]) => r.owner !== "Structural" && !domNames.has(r.owner)).map(([id]) => id)
      .concat(Object.entries(cl.concepts || {}).filter(([, r]) => r.owner !== "NotAConcept" && !domNames.has(r.owner)).map(([id]) => "c:" + id));
    record(check("zero-missing · every classification rule and reviewed container names a declared domain",
      !badRules.length && !badReviews.length, badRules.concat(badReviews).slice(0, 5).join(", ")));
    const levels = new Set((cl.confidenceLevels || []).map(l => l.key));
    const badLevels = Object.entries(cl.containers || {}).concat(Object.entries(cl.concepts || {})).filter(([, r]) => !levels.has(r.confidence)).map(([id]) => id);
    record(check("zero-missing · every review uses a declared confidence level", levels.size > 0 && !badLevels.length, badLevels.slice(0, 5).join(", ")));
    const reg = payload.register;
    const regKeys = reg ? keySet(reg.rows.map(r => ({ k: r[0] })), "k") : new Map();
    record(check("zero-duplicate · every corpus concept appears once in the register", !!reg && regKeys.size === reg.rows.length, reg ? (reg.rows.length - regKeys.size) + " repeated" : "no register compiled"));
    let fresh = null;
    try { fresh = require(path.join(ROOT, "lib", "canonical.js")).classifyRegister(payload.parsed, payload.universes, rf); } catch (e) { }
    record(check("no-leakage · the sealed concept register is exactly a fresh derivation from the rules and reviews",
      !!fresh && JSON.stringify(fresh) === JSON.stringify(reg), "the register differs from a fresh derivation"));
    let base = {};
    try { base = JSON.parse(require("fs").readFileSync(path.join(__dirname, "register-baseline.json"), "utf8")); } catch (e) { }
    const unplaced = reg ? reg.counts.unplaced : Infinity;
    const unreviewed = reg ? reg.counts.containers - reg.counts.containersReviewed : Infinity;
    record(check("zero-missing · unplaced concepts (" + unplaced + ", baseline " + base.conceptsUnplaced + ") and unreviewed containers (" + unreviewed + ", baseline " + base.containersUnreviewed + ")",
      unplaced <= (base.conceptsUnplaced ?? Infinity) && unreviewed <= (base.containersUnreviewed ?? Infinity)));

    /* alignment: every part of another structure that calls itself a domain has exactly one
       register owner, and no mapping names a part that no longer exists */
    const al = rf.alignment || { systems: [] };
    const alignProblems = [];
    let aligned = 0;
    for (const sys of al.systems) {
      if (!sys.owners) continue;
      let list = null;
      try { list = JSON.parse(require("fs").readFileSync(path.join(ROOT, sys.source), "utf8"))[sys.list]; } catch (e) { }
      if (!Array.isArray(list)) { alignProblems.push(sys.system + ": source missing"); continue; }
      const keys = new Set(list.map(x => x[sys.key]));
      for (const k of keys) { if (!sys.owners[k]) alignProblems.push(sys.system + ":" + k + " unmapped"); else if (!domNames.has(sys.owners[k])) alignProblems.push(sys.system + ":" + k + " → undeclared " + sys.owners[k]); else aligned++; }
      for (const k of Object.keys(sys.owners)) if (!keys.has(k)) alignProblems.push(sys.system + ":" + k + " no longer exists");
    }
    const uniUnowned = payload.universes.filter(u => { const r = (cl.containers || {})["u:" + u.key]; return !r || (r.owner !== "Structural" && !domNames.has(r.owner)); }).map(u => u.key);
    record(check("zero-overlap · every other domain system is aligned to one register owner per part (" + aligned + " parts, " + payload.universes.length + " universes)",
      !alignProblems.length && !uniUnowned.length, alignProblems.concat(uniUnowned.map(k => "universe " + k)).slice(0, 6).join(", ")));

    /* documents: every document at the root and in _superseded/ has one registered status and
       owner; superseded ones live under _superseded/ and name what replaced them; corpus sources
       are exactly the documents the parser reads; projections name their generator */
    const dr = rf.documents || { documents: [], statuses: [] };
    const fsd = require("fs");
    const onDiskDocs = [];
    try { for (const f of fsd.readdirSync(ROOT)) if (/\.(md|txt)$/.test(f) && fsd.statSync(path.join(ROOT, f)).isFile()) onDiskDocs.push(f); } catch (e) { }
    try { for (const f of fsd.readdirSync(path.join(ROOT, "_superseded"))) if (/\.md$/.test(f)) onDiskDocs.push("_superseded/" + f); } catch (e) { }
    const docPaths = keySet(dr.documents, "path");
    const statuses = new Set(dr.statuses || []);
    const corpus = new Set(require(path.join(ROOT, "lib", "seed", "ucos.json")).DOCS.map(d => d.file).filter(f => !f.endsWith("/")));
    const docProblems = [];
    for (const f of onDiskDocs) if (!docPaths.has(f)) docProblems.push(f + " unregistered");
    for (const d of dr.documents) {
      if (!onDiskDocs.includes(d.path)) docProblems.push(d.path + " does not exist");
      if (!statuses.has(d.status) || !domNames.has(d.owner)) docProblems.push(d.path + " has an undeclared status or owner");
      if ((d.status === "superseded") !== d.path.startsWith("_superseded/")) docProblems.push(d.path + " is " + d.status + " but sits " + (d.path.startsWith("_superseded/") ? "in" : "outside") + " _superseded/");
      if (d.status === "superseded" && !d.supersededBy) docProblems.push(d.path + " names nothing that replaced it");
      if (d.status === "projection" && !d.generatedBy) docProblems.push(d.path + " names no generator");
      if ((d.status === "corpus-source") !== corpus.has(d.path)) docProblems.push(d.path + " corpus status disagrees with the parser's document list");
    }
    for (const f of corpus) if (!dr.documents.some(d => d.path === f)) docProblems.push(f + " is parsed but unregistered");
    record(check("zero-missing · every document has one registered status and owner, and sits where its status says (" + dr.documents.length + " documents)",
      docPaths.size === dr.documents.length && !docProblems.length, docProblems.slice(0, 6).join("; ")));

    /* the live API: every route has one owner; the sealed register equals a fresh derivation;
       every domain's build status follows from what it owns (code modules or live routes) */
    const api = payload.api;
    let apiFresh = null;
    try { apiFresh = require(path.join(ROOT, "lib", "canonical.js")).apiRegister(rf); } catch (e) { }
    const badApiRules = ((rf.api || {}).owners || []).filter(r => !domNames.has(r.owner)).map(r => r.pattern);
    /* an independent count of every route key in the table, so a parser that skips an entry
       form cannot pass silently */
    let keyCount = -1;
    try {
      const src = require("fs").readFileSync(path.join(ROOT, (rf.api || {}).source || "lib/api.js"), "utf8");
      const s0 = src.indexOf("const " + ((rf.api || {}).table || "routes") + " = ["), s1 = src.indexOf("function handle(", s0);
      keyCount = (src.slice(s0, s1).match(/"(GET|POST|PUT|DELETE|PATCH) \/api\//g) || []).length;
    } catch (e) { }
    const apiProblems = api ? api.unowned.slice(0, 5).concat(badApiRules) : ["no API register compiled"];
    if (api && api.routes.length !== keyCount) apiProblems.push("the register holds " + api.routes.length + " of " + keyCount + " routes in the table");
    record(check("zero-missing · every live API route has one owning domain (" + (api ? api.routes.length : 0) + " routes)",
      !!api && api.routes.length > 0 && !apiProblems.length && JSON.stringify(apiFresh) === JSON.stringify(api), apiProblems.join(", ")));
    const built = new Set(Object.keys((api || {}).counts || {}));
    for (const m of (rf.codebase || { modules: [] }).modules) for (const p of m.parts || [{ owner: m.owner }]) built.add(p.owner);
    const statusWrong = doms.filter(d => d.status !== (built.has(d.name) ? "partial" : "designed") && !(d.status === "built" && built.has(d.name))).map(d => d.name + " says " + d.status);
    record(check("zero-overlap · every domain's build status matches what it owns (designed: no code and no routes)", !statusWrong.length, statusWrong.slice(0, 6).join(", ")));

    /* the gap list: every gap has a declared owner and status; a closed gap names the
       amendment that closed it */
    const gaps = (rm.gaps || []);
    const badGaps = gaps.filter(g => !g.gapId || !g.title || !domNames.has(g.owner) || !["open", "closed"].includes(g.status)
      || (g.status === "closed" && (!g.closedBy || !amdIds.has(g.closedBy)))).map(g => g.gapId || g.title);
    record(check("zero-partial · every recorded gap has an owner and a status, and every closed gap its amendment (" + gaps.filter(g => g.status === "open").length + " open)",
      keySet(gaps, "gapId").size === gaps.length && !badGaps.length, badGaps.join(", ")));

    registerCounts = { categories: cats.length, domains: doms.length, owned: owners.size, domainsWithoutContract: noContract.length, outstanding: noContract,
      laws: laws.length, lawsNotEnforced: notEnforced.length, kernel: kernel.length, modules: cb.modules.length, steps: rm.steps.length,
      stepsDone: rm.steps.filter(st => st.status === "done").length,
      concepts: reg ? reg.counts.concepts : 0, conceptsUnplaced: unplaced, containersUnreviewed: unreviewed };
  }

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
    counts: { universes: payload.universes.length, concepts: conceptRows, documents: docs.length, sections: payload.counts.sections, registries: payload.counts.registries },
    register: registerCounts
  };
}

/* a human-readable verdict — the operator's answer to "is the registry honest?" */
function explain(report) {
  const lines = ["✗ the integrity gate FAILED " + report.fails.length + " of " + report.checked + " checks:"];
  for (const f of report.fails) lines.push("  ✗ " + f.name + (f.detail ? "  →  " + f.detail : ""));
  return lines.join("\n");
}

module.exports = { run, explain, check };
