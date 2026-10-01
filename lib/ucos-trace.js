/* UCOS Ω∞ · traceability — every corpus declaration → its runtime artifact.
   --------------------------------------------------------------------------
   The corpora declare 24,000+ concepts; the platform implements them through a
   small set of GENERIC engines (registry, foundation, entity, catalog). This
   module is the map between the two: for any key it reports every runtime
   artifact the declaration resolves to — registry concepts with document+line
   provenance, its foundation, its universe and live entity, its catalog
   projections, and the API routes and console views that expose it.

   Nothing is hardcoded: the artifact set is read from live tables, and the route
   and console surfaces are read from the modules themselves, so the map stays
   correct as either side grows. This is the answer to "where is §X implemented?" */
"use strict";

let _db = null;
const db = () => _db || (_db = require("./db.js"));
const rows = (sql, ...p) => { try { return db().all(sql, ...p) || []; } catch (e) { return []; } };
const get = (sql, ...p) => { try { return db().get(sql, ...p) || null; } catch (e) { return null; } };
const keyOf = t => String(t || "").normalize("NFKD").replace(/[\u0300-\u036f]/g, "")
  .replace(/[Ω∞]/g, "").replace(/[^a-z0-9]+/gi, " ").trim().toLowerCase().replace(/\s+/g, "_").replace(/^_+|_+$/g, "").slice(0, 120);

/* the API surface, read from the router itself (never a second copy) */
function apiRoutes() {
  try { const api = require("./api.js"); return api.routeKeys ? api.routeKeys() : []; } catch (e) { return []; }
}
/* the console surface: the platform console's nav sections (public/js/platform.js
   is the only front-end that renders the constitution). Derived by scanning its
   nav array rather than keeping a list here */
function consoleViews() {
  try {
    const fs = require("fs"), path = require("path");
    const src = fs.readFileSync(path.join(__dirname, "..", "public", "js", "platform.js"), "utf8");
    const out = [];
    const re = /\[\s*"([a-z][a-z0-9-]*)"\s*,\s*"([^"]+)"/g;
    let m;
    while ((m = re.exec(src)) && out.length < 200) out.push({ view: m[1], label: m[2] });
    return out;
  } catch (e) { return []; }
}

/* ---------- trace one key through every layer ----------
   Accepts a universe key ("uv_insurance"), a foundation key ("insurance"), a
   concept name ("Insurance") or a section name. Returns what exists, and — as
   importantly — what does not, so a gap is a reportable fact rather than silence. */
function trace(name) {
  const k = keyOf(name);
  const ek = k.startsWith("uv_") ? k : "uv_" + k;
  const concepts = rows("SELECT DISTINCT key, name, doc_id, line, container_kind, container_name FROM ucos_concepts WHERE key=? ORDER BY doc_id, line", k);
  const foundation = get("SELECT key,name,universe,lifecycle,governance,classification,source_doc,source_line,created_at FROM ucos_foundations WHERE key=?", k);
  const universe = get("SELECT key,name,source_doc,source_line,entity_key,concepts,instantiated_at FROM ucos_universes WHERE key=? OR entity_key=?", k, ek);
  const def = universe ? get("SELECT key, def FROM entity_defs WHERE key=?", universe.entity_key) : null;
  let defObj = null; if (def) { try { defObj = JSON.parse(def.def || "{}"); } catch (e) { } }
  const records = universe ? rows("SELECT COUNT(*) n FROM entity_data WHERE entity=?", universe.entity_key)[0] || { n: 0 } : { n: 0 };
  const projections = universe ? rows("SELECT tenant_id, id, title, price, lifecycle FROM products WHERE source_universe=? ORDER BY tenant_id, id", universe.entity_key) : [];
  /* routes that name this key specifically — the generic /ucos namespace is not a
     per-concept artifact, so matching it would inflate every trace. The key must
     bound a whole path segment (or the tail of one, as in "uv_<key>"): a bare
     substring test makes "agi" hit "magic" and "aging", and reports a universe as
     route-wired when no route actually names it */
  const kEsc = k.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const segRe = k ? new RegExp("(^|[/_.-])" + kEsc + "([/_.-]|$)", "i") : null;
  const routes = segRe ? apiRoutes().filter(r => segRe.test(r.path)) : [];
  const views = consoleViews().filter(v => /ucos|univers|found|studio|gproduct/i.test(v.view));
  /* the constitution console is a GLOBAL surface (it renders the whole corpus), so it
     only counts as reached when the key actually resolves somewhere — otherwise a
     nonsense key would report as "partially wired" just because the console exists */
  const resolves = concepts.length > 0 || !!foundation || !!universe || !!def;

  const layers = [
    { layer: "registry concept", present: concepts.length > 0, n: concepts.length, artifacts: concepts.slice(0, 12).map(c => ({ doc: c.doc_id, line: c.line, container: c.container_name })) },
    { layer: "foundation", present: !!foundation, n: foundation ? 1 : 0, artifacts: foundation ? [{ key: foundation.key, lifecycle: foundation.lifecycle, source: foundation.source_doc + ":" + foundation.source_line }] : [] },
    { layer: "universe", present: !!universe, n: universe ? 1 : 0, artifacts: universe ? [{ key: universe.key, name: universe.name, source: universe.source_doc + ":" + universe.source_line }] : [] },
    { layer: "live entity", present: !!def, n: def ? 1 : 0, artifacts: def ? [{ key: def.key, label: defObj && defObj.label, fields: (defObj && defObj.fields || []).length }] : [] },
    { layer: "records", present: records.n > 0, n: records.n, artifacts: [] },
    { layer: "catalog projection", present: projections.length > 0, n: projections.length, artifacts: projections.slice(0, 12) },
    { layer: "api routes", present: routes.length > 0, n: routes.length, artifacts: routes.slice(0, 20) },
    { layer: "console views", present: resolves && views.length > 0, n: views.length, artifacts: views }
  ];
  const reached = layers.filter(l => l.present).length;
  /* an absent per-universe route is not a gap — Article 4.2 forbids per-universe code,
     so a resolved universe is served by the GENERIC entity and catalog APIs. Say so,
     instead of presenting the design as an omission. */
  const genericServed = !routes.length && !!universe;
  return { query: name, key: k, entityKey: ek, reached, layers,
    verdict: reached === layers.length ? "fully wired — declared, registered, instantiated, transactable, exposed"
      : reached === 0 ? "not found in the corpus — no declaration matches this key"
        : "partially wired (" + reached + "/" + layers.length + " layers)"
          + (genericServed ? " — no per-universe route exists by design (Article 4.2): the generic entity and catalog APIs serve this universe" : "") };
}

/* ---------- the corpus→runtime matrix: implementation coverage at a glance ----------
   Per source document: how many concepts it declares, how many resolve to a
   foundation / universe / live entity, and the derived coverage. This is the
   measurable, honest answer to "how much of the constitution is implemented?" */
function matrix() {
  const docs = rows("SELECT doc_id, file, code, name, parts, sections, articles, concepts, registries FROM ucos_documents ORDER BY doc_id");
  const totalConcepts = (get("SELECT COUNT(*) n FROM ucos_concepts") || {}).n || 0;
  const foundations = (get("SELECT COUNT(*) n FROM ucos_foundations") || {}).n || 0;
  const universes = (get("SELECT COUNT(*) n FROM ucos_universes") || {}).n || 0;
  const entities = (get("SELECT COUNT(*) n FROM entity_defs WHERE key LIKE 'uv_%'") || {}).n || 0;
  const records = (get("SELECT COUNT(*) n FROM entity_data WHERE entity LIKE 'uv_%'") || {}).n || 0;
  const projections = (get("SELECT COUNT(*) n FROM products WHERE source_kind='universe'") || {}).n || 0;
  const perDoc = docs.map(d => {
    const c = rows("SELECT COUNT(*) n FROM ucos_concepts WHERE doc_id=?", d.doc_id)[0] || { n: 0 };
    const f = rows("SELECT COUNT(*) n FROM ucos_foundations WHERE source_doc=?", d.doc_id)[0] || { n: 0 };
    const u = rows("SELECT COUNT(*) n FROM ucos_universes WHERE source_doc=?", d.doc_id)[0] || { n: 0 };
    return { doc: d.code, file: d.file, name: d.name, concepts: c.n, foundations: f.n, universes: u.n,
      conceptCoverage: c.n ? Math.round(f.n / c.n * 100) : 0 };
  });
  return {
    corpus: { documents: docs.length, concepts: totalConcepts, registries: docs.reduce((a, d) => a + d.registries, 0) },
    implementation: { foundations, universes, liveEntities: entities, records, catalogProjections: projections },
    engine: "generic: one registry + one foundation engine + one entity engine + one catalog bridge serve every declaration (zero per-universe code, Article 4.2)",
    perDocument: perDoc,
    notes: [
      "concepts are DATA by design (Configuration-Over-Code): most are implemented by being registered, editable and queryable, not by code branches",
      "universes are the OPERABLE unit: every one is a foundation + a live entity, so the entire corpus is creatable/readable/validatable generically",
      "catalog projections are the ACTIVATION layer: a universe is shopper-transactable once activated (0 by default; see /api/ucos/catalog/activate)"
    ]
  };
}

module.exports = { trace, matrix, consoleViews };
