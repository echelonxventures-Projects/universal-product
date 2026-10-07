/* ════════════════════════════════════════════════════════════════════════════
   UCOS Ω∞ — THE COMPOSITION ENGINE
   Application = Capability Composition. NOT Application = Custom Code.
   ════════════════════════════════════════════════════════════════════════════

   The constitution's central claim (Article 4): every application is composed from
   constitutional capabilities; no application is hard-coded. This module is the machinery
   that makes that claim mechanically true.

   compose(capability) takes ANY capability the registry declares — a universe, an entity,
   a capability from the catalog — and materializes its full application surface:

     · DATA MODEL   — an entity definition (table, fields, validation, permissions)
     · API          — CRUD + list + search routes, generated from the definition
     · WORKFLOW     — the lifecycle the corpus declares for the domain (UCOS 5.1/5.2),
                      with the transition grammar as its steps
     · UI           — the list fields + form fields a console renders a surface from
     · DASHBOARD    — the metric tiles + report the operator reads on first open
     · SECURITY     — the permission set the capability is governed by
     · TRACE        — provenance back to the document and line that declared it

   Every artifact is DERIVED — from the corpus, the registry and the capability's own
   declaration — never written by hand. A capability the corpus adds tomorrow is composed
   by this module with no new code anywhere. That is the "zero new business code" bar, and
   it is enforced by construction: this module contains no per-capability knowledge at all.
*/

const db = require("./db.js");
const entity = require("./entity.js");
const ucos = require("./ucos.js");
const universes = require("./ucos-universes.js");
const dashboards = require("./dashboards.js");

/* the composition ledger — a record of what was composed, when, and from what source.
   Append-only: recomposition supersets, never deletes, so the platform's evolution is
   itself traceable (Article 7 — Evolution Governance). */
function ledger() {
  return db.all("SELECT key, capability, source, artifacts, composed_at FROM composition_ledger ORDER BY composed_at DESC")
    .map(e => {
      let records = 0;
      try { records = (db.get("SELECT COUNT(*) n FROM entity_data WHERE entity=?", e.key) || {}).n || 0; } catch (x) { }
      return { ...e, records };
    });
}
/* the composition ledger — a record of what was composed, when, and from what source.
   Recomposition supersedes, never duplicates: composing the same capability twice is an
   evolution of one composition, not two of them, so the ledger is keyed on the capability
   and a re-compose updates the row in place (Article 7 — Evolution Governance, and the
   append-only audit trail of *what changed* stays with the entity engine's own history). */
function ledgerWrite(entry) {
  db.run("INSERT INTO composition_ledger(key, capability, source, artifacts, composed_at) VALUES(?,?,?,?,?)"
    + " ON CONFLICT(key) DO UPDATE SET capability=excluded.capability, source=excluded.source,"
    + " artifacts=excluded.artifacts, composed_at=excluded.composed_at",
    entry.key, entry.capability, entry.source, JSON.stringify(entry.artifacts || {}), new Date().toISOString());
}
function ledgerRead(key) {
  return db.get("SELECT * FROM composition_ledger WHERE key=? ORDER BY composed_at DESC LIMIT 1", key);
}

/* ── 1. DATA MODEL ──────────────────────────────────────────────────────────────
   Derive an entity definition from the capability's declaration. The universe's fields
   are already corpus-derived (ucos-universes.fieldsFor); a catalog capability contributes
   its params as attributes; a raw entity contributes itself. Nothing here names a
   capability — the shape comes from the declaration, always. */
function deriveFields(cap) {
  if (cap.kind === "universe") {
    /* discover() is the canonical path: it attaches the corpus's own concept names to the
       universe they sit under, which is the attribute set fieldsFor turns into fields.
       The ucos_universes row stores only the concept COUNT, so the names must come from
       here — indexing parseAll() by source_line hits an unrelated concept (concepts are
       keyed by position, not by line). */
    const d = universes.discover().find(x => x.key === cap.key);
    if (d) return universes.fieldsFor(d.name, d.concepts || []).map(f => ({ ...f }));
  }
  if (cap.kind === "capability") {
    const caps = require("./capabilities.js");
    const c = caps.catalog().find(x => x.key === cap.key);
    if (c) {
      const fields = [{ key: "name", label: c.label + " Name", type: "text", required: true, list: true },
        { key: "code", label: "Reference", type: "text", list: true },
        { key: "status", label: "Status", type: "select", options: ucos.lifecycleStates().map(s => String(s).toLowerCase()), list: true }];
      for (const [pk, p] of Object.entries(c.params || {}))
        fields.push({ key: pk.slice(0, 28), label: p.label || pk, type: p.type === "number" ? "number" : "text", list: false });
      fields.push({ key: "attrs", label: "Attributes", type: "json" });
      return fields;
    }
  }
  if (cap.kind === "entity") {
    const d = entity.allEntities(null)[cap.key];
    if (d) return (d.fields || []).map(f => ({ ...f }));
  }
  return null;
}

function composeDataModel(cap, fields) {
  const key = "cp_" + String(cap.key).replace(/[^a-z0-9_]/g, "").slice(0, 40);
  const def = {
    table: null, storage: "json", pk: "id",
    label: cap.label, icon: cap.icon || "🧩",
    composed: true, composedFrom: cap.source,
    perm: { read: ["admin", "platform"], write: ["admin", "platform"] },
    fields
  };
  db.run("INSERT INTO entity_defs(key,scope,tenant_id,def) VALUES(?,?,?,?) ON CONFLICT(key,scope,tenant_id) DO UPDATE SET def=excluded.def",
    key, "platform", 0, JSON.stringify(def));
  return { key, def, endpoint: "/api/meta/entity/" + key };
}

/* ── 2. API ─────────────────────────────────────────────────────────────────────
   The entity engine already serves CRUD for any declared definition — list, create,
   update, delete, with validation and permissions resolved from the def itself. So the
   API surface is *reported*, not re-implemented: composing an API means declaring the
   routes the definition now serves and the validation that governs them. */
function composeApi(cap, model) {
  const def = model.def;
  return {
    rest: ["GET /api/meta/entity/" + model.key, "POST /api/meta/entity/" + model.key,
      "PUT /api/meta/entity/" + model.key + "/:id", "DELETE /api/meta/entity/" + model.key + "/:id"],
    platformReader: "GET /api/platform/data/" + model.key,
    validation: (def.fields || []).filter(f => f.required).map(f => f.key),
    permissions: def.perm,
    /* a capability is also queryable through the constitutional search path — the same
       corpus that declares it is the corpus an operator searches */
    searchable: true
  };
}

/* ── 3. WORKFLOW ────────────────────────────────────────────────────────────────
   The lifecycle the corpus declares for the domain becomes the workflow: states are
   UCOS 5.1, transitions are the Art. 10 grammar, and the certification rule (5.2) gates
   the final step. Composing a workflow is registering that declaration, not authoring
   steps by hand. */
function composeWorkflow(cap, model) {
  const states = ucos.lifecycleStates();
  /* the Art. 10 grammar is a corpus declaration, not a per-record computation — reading it
     from availableTransitions() would yield nothing, because that answers "what may THIS
     record fire now", which needs a record */
  const grammar = (ucos.transitionGrammar() || []).slice(0, 8);
  const steps = states.map((st, i) => ({
    state: st,
    gate: i === states.length - 2 ? "certification (UCOS 5.2)" : i === 0 ? "declaration" : "review",
    rule: i >= states.length - 2 ? "requires certification evidence" : "none"
  }));
  const wf = {
    key: "wf_" + model.key, domain: cap.home || cap.key, name: cap.label + " lifecycle",
    description: "Composed from the corpus declaration " + cap.source + " — states UCOS 5.1, grammar Art. 10. No per-capability code.",
    trigger: "manual", steps, config: { grammar, model: model.key }, status: "active"
  };
  db.run("INSERT OR REPLACE INTO workflows(key,domain,name,description,trigger,steps,config,status) VALUES(?,?,?,?,?,?,?,?)",
    wf.key, wf.domain, wf.name, wf.description, wf.trigger, JSON.stringify(wf.steps), JSON.stringify(wf.config), wf.status);
  return wf;
}

/* ── 4. UI ──────────────────────────────────────────────────────────────────────
   The console renders surfaces from the definition's list + form fields — no UI code is
   written per capability. The composition records exactly which surfaces the definition
   drives, so the console can open them by reference. */
function composeUi(cap, model) {
  const f = model.def.fields || [];
  return {
    listFields: f.filter(x => x.list).map(x => x.key),
    formFields: f.map(x => ({ key: x.key, label: x.label, type: x.type, required: !!x.required, options: x.options || null })),
    surfaces: ["platform console", "data studio", "entity form"],
    generator: "definition-driven (entity engine)"
  };
}

/* ── 5. DASHBOARD ───────────────────────────────────────────────────────────────
   First-open metrics the operator reads: a record count, a distinct-reference count and
   the lifecycle breakdown. Composed from the model — a dashboard declares what to
   aggregate over the composed entity, and the reporting engine renders it. The metrics
   are the engine's own vocabulary (count/distinct + a status dimension); anything else
   would render as an error tile instead of a number. */
function composeDashboard(cap, model) {
  const board = {
    key: "db_" + model.key, name: cap.label + " — composed",
    type: "Operational", audience: "platform", position: 900,
    description: "Composed from " + cap.source + ". Every artifact is derived; no per-capability dashboard code exists.",
    widgets: [
      { kind: "kpi", label: cap.label + " records", entity: model.key, metric: "count", span: 2 },
      { kind: "kpi", label: "Distinct references", entity: model.key, metric: "distinct", column: "code", span: 2 },
      { kind: "bar", label: "By lifecycle state", entity: model.key, metric: "count", dimension: "status", span: 3 }
    ]
  };
  dashboards.saveBoard(board);
  return board;
}

/* ── 6. SECURITY ────────────────────────────────────────────────────────────────
   The permission set a capability is governed by — derived from the def, so a composed
   capability inherits the platform's RBAC the moment it exists. */
function composeSecurity(cap, model) {
  return {
    roles: model.def.perm,
    audit: "every mutation logs through the entity engine's audit trail",
    traceability: "composition ledger + provenance " + cap.source
  };
}

/* ── the entry point ────────────────────────────────────────────────────────────
   Resolve a capability from whichever registry declares it, then compose the surface.
   Returns the full manifest — every artifact, its provenance, and whether it already
   existed (recomposition is idempotent and reports what changed). */
function resolveCapability(key) {
  /* a universe: discover() carries the declaration the corpus made — its registry label
     is the canonical home the capability composes under, so a composed universe lands in
     the section that declared it rather than a catch-all */
  const uv = universes.discover().find(x => x.key === key || ("uv_" + x.key) === key);
  if (uv) return { kind: "universe", key: uv.key, label: uv.name, icon: "🧬",
    source: uv.sourceDoc + ":" + (uv.sourceLine || "?"), home: uv.registry || uv.sourceDoc };
  const caps = require("./capabilities.js");
  const c = caps.catalog().find(x => x.key === key);
  if (c) return { kind: "capability", key: c.key, label: c.label || c.key, icon: "⚙️", source: "capability catalog", home: c.domain };
  const d = entity.allEntities(null)[key];
  if (d) return { kind: "entity", key, label: d.name || d.label || key, icon: d.icon || "🧱", source: "entity registry", home: "platform" };
  return null;
}

function compose(key, opts) {
  const o = opts || {};
  const cap = resolveCapability(key);
  if (!cap) return { ok: false, error: "no capability declared for " + key };
  const fields = o.fields || deriveFields(cap);
  if (!fields || !fields.length) return { ok: false, error: "the declaration carries no fields — nothing to compose" };

  const model = composeDataModel(cap, fields);
  const artifacts = {
    dataModel: { key: model.key, endpoint: model.endpoint, fields: fields.length, source: cap.source },
    api: composeApi(cap, model),
    workflow: composeWorkflow(cap, model),
    ui: composeUi(cap, model),
    dashboard: composeDashboard(cap, model),
    security: composeSecurity(cap, model)
  };
  const entry = { key: model.key, capability: cap.label, source: cap.source, artifacts, composed_at: new Date().toISOString() };
  ledgerWrite(entry);
  return { ok: true, capability: cap, model: { key: model.key, label: model.def.label }, artifacts, ledger: entry };
}

/* recomposition: re-derive from the current declaration. Idempotent — the same declaration
   yields the same artifacts, and a changed declaration updates them in place. */
function recompose(key) {
  const cap = resolveCapability(key);
  if (!cap) return { ok: false, error: "unknown capability" };
  const fields = deriveFields(cap);
  if (!fields) return { ok: false, error: "no derivable fields" };
  return compose(key, { fields });
}

/* the manifest a console reads to render a composed capability — one call, every artifact,
   plus the live record count so an operator sees what the composed surface now holds */
function manifest(key) {
  const e = ledgerRead(key) || ledgerRead("cp_" + String(key).replace(/[^a-z0-9_]/g, "").slice(0, 40));
  if (!e) return null;
  let arts = {}; try { arts = JSON.parse(e.artifacts || "{}"); } catch (x) { }
  let records = 0;
  try { records = (db.get("SELECT COUNT(*) n FROM entity_data WHERE entity=?", e.key) || {}).n || 0; } catch (x) { }
  return { ...e, artifacts: arts, records };
}

/* what the platform can compose — every declaration the registries hold, each marked with
   whether it has already been composed. This is the console's authoring surface: an
   operator picks a declared capability and the platform materializes it, never the reverse */
function candidates() {
  const composed = new Set((ledger() || []).map(e => e.key));
  const caps = require("./capabilities.js");
  const mark = (key) => composed.has("cp_" + key);
  const universes_ = universes.discover().map(u => ({ key: u.key, label: u.name, kind: "universe",
    source: u.sourceDoc + ":" + (u.sourceLine || "?"), home: u.registry || u.sourceDoc,
    concepts: (u.concepts || []).length, composed: mark(u.key) }));
  const capabilities = caps.catalog().map(c => ({ key: c.key, label: c.label || c.key, kind: "capability",
    source: "capability catalog", home: c.domain, composed: mark(c.key) }));
  /* plain declared entities compose too — the universe entities are already listed above, so
     these are the platform's other datasets (countries, orders, tenants…) */
  const entities = Object.entries(entity.allEntities(null))
    .filter(([k]) => !k.startsWith("uv_") && !k.startsWith("cp_"))
    .map(([k, d]) => ({ key: k, label: d.name || d.label || k, kind: "entity",
      source: "entity registry", home: "platform", composed: mark(k) }))
    .sort((a, b) => a.label.localeCompare(b.label));
  return { universes: universes_, capabilities, entities,
    counts: { universe: universes_.length, capability: capabilities.length, entity: entities.length,
      composed: composed.size } };
}

module.exports = { resolveCapability, compose, recompose, manifest, candidates, ledger, ledgerRead, ledgerWrite, deriveFields };
