/* Context continuity · the knowledge store.
   --------------------------------------------------------------------------
   Loads the AUTHORED continuity knowledge (PROJECT-CONTEXT/knowledge/*.json),
   validates every record against its schema and the lifecycle registry, and
   exposes one node table keyed by stable id.

   Knowledge Once: the 93 UCOS artifacts are NOT copied in. They are owned by
   _registry/manifest.json and imported here read-only through an adapter, so the
   manifest stays their only owner and a change there is seen here immediately.

   load(root) never throws on bad knowledge — it returns diagnostics, so verify
   can report every broken invariant at once with its remedy. */
"use strict";

const fs = require("fs");
const path = require("path");
const U = require("./util");
const { validate } = require("./schema");

const KNOWLEDGE_FILES = {
  source: "sources.json",
  requirement: "requirements.json",
  decision: "decisions.json",
  constraint: "constraints.json",
  artifact: "artifacts.json",
  issue: "issues.json",
  task: "tasks.json",
  context: "contexts.json"
};

function diag(level, code, message, extra) { return Object.assign({ level, code, message }, extra || {}); }

function dirs(root) {
  const base = path.join(root, U.CONTEXT_DIR);
  return {
    base,
    knowledge: path.join(base, "knowledge"),
    schemas: path.join(base, "schemas"),
    contexts: path.join(base, "contexts"),
    taskPacks: path.join(base, "task-packs"),
    handoffs: path.join(base, "handoffs"),
    receipts: path.join(base, "receipts"),
    verification: path.join(base, "verification")
  };
}

/* the UCOS manifest adapter: registry-owned artifacts as read-only nodes */
function importRegistryArtifacts(root, diags) {
  const rel = "_registry/manifest.json";
  if (!U.exists(root, rel)) return [];
  let M;
  try { M = U.readJSON(U.safeJoin(root, rel)); } catch (e) { diags.push(diag("error", "registry-manifest-unreadable", rel + ": " + e.message)); return []; }
  const files = {};
  for (const c of M.categories || []) {
    let names = [];
    try { names = fs.readdirSync(U.safeJoin(root, c.path)); } catch (e) { }
    for (const n of names) { const m = /^(UCOS-[A-Z]+-\d+)-.*\.md$/.exec(n); if (m) files[m[1]] = c.path + "/" + n; }
  }
  return (M.artifacts || []).map(a => ({
    id: a.id, title: a.title, type: "generated", owner: rel, authority: "derived",
    path: files[a.id], derivedFrom: [], lifecycle: a.status === "generated" ? "derived" : "proposed",
    access: "public", tags: ["ucos-artifact", "cat:" + a.cat], imported: true
  }));
}

function load(root, opts) {
  opts = opts || {};
  const D = dirs(root);
  const diags = [];
  const read = (abs, label) => {
    try { return U.readJSON(abs); } catch (e) { diags.push(diag("error", "unreadable", label + ": " + e.message, { remedy: "fix the JSON syntax in " + label })); return null; }
  };
  const config = read(path.join(D.schemas, "config.json"), "schemas/config.json") || { budgets: { defaultPackBytes: 24000, minimumAgentBytes: 6000, bootstrapBytes: 12000 }, hygiene: {}, generated: { views: [] }, sourceScope: { categories: [] }, archive: {} };
  const lifecycle = read(path.join(D.schemas, "lifecycle.json"), "schemas/lifecycle.json") || { states: {}, transitions: [] };
  const relations = read(path.join(D.schemas, "relations.json"), "schemas/relations.json") || { relations: {} };
  const kschema = read(path.join(D.schemas, "knowledge.schema.json"), "schemas/knowledge.schema.json");
  const schemaFiles = ["config.json", "lifecycle.json", "relations.json", "knowledge.schema.json", "handoff.schema.json", "receipt.schema.json"];
  const schemaHashes = {};
  for (const f of schemaFiles) { try { schemaHashes[f] = U.sha256(fs.readFileSync(path.join(D.schemas, f))); } catch (e) { schemaHashes[f] = null; } }

  const nodes = new Map();
  const add = (kind, rec, file) => {
    if (!rec || typeof rec.id !== "string") { diags.push(diag("error", "record-without-id", file + ": a record has no id")); return; }
    if (nodes.has(rec.id)) {
      diags.push(diag("error", "duplicate-id", "id " + rec.id + " is declared in both " + nodes.get(rec.id).file + " and " + file, { id: rec.id, remedy: "one canonical owner per id — remove or rename one declaration" }));
      return;
    }
    nodes.set(rec.id, { id: rec.id, kind, rec, file });
  };

  for (const kind of Object.keys(KNOWLEDGE_FILES)) {
    const file = "knowledge/" + KNOWLEDGE_FILES[kind];
    const abs = path.join(D.knowledge, KNOWLEDGE_FILES[kind]);
    if (!fs.existsSync(abs)) { diags.push(diag("error", "knowledge-file-missing", file + " is missing", { remedy: "restore it from git (git checkout -- PROJECT-CONTEXT/" + file + ")" })); continue; }
    const doc = read(abs, file);
    if (!doc) continue;
    if (kschema) {
      for (const e of validate(kschema, doc)) diags.push(diag("error", "schema", file + " " + e));
      if (doc.kind !== kind) diags.push(diag("error", "schema", file + " declares kind '" + doc.kind + "', expected '" + kind + "'"));
      const def = kschema.definitions[kind];
      (doc.records || []).forEach((r, i) => {
        for (const e of validate(def, r, kschema, (r && r.id) || (file + "[" + i + "]"))) diags.push(diag("error", "schema", file + " " + e, { id: r && r.id }));
      });
    }
    for (const r of doc.records || []) add(kind, r, file);
  }
  for (const a of importRegistryArtifacts(root, diags)) add("artifact", a, "_registry/manifest.json");

  /* lifecycle values come from the registry, never from an enum in code */
  for (const n of nodes.values()) {
    if (n.rec.lifecycle && !lifecycle.states[n.rec.lifecycle]) {
      diags.push(diag("error", "lifecycle-unknown", n.id + " has lifecycle '" + n.rec.lifecycle + "' which is not in schemas/lifecycle.json", { id: n.id }));
    }
  }

  let state = null;
  const stateAbs = path.join(D.knowledge, "state.json");
  if (fs.existsSync(stateAbs)) state = read(stateAbs, "knowledge/state.json");
  else diags.push(diag("error", "knowledge-file-missing", "knowledge/state.json is missing"));
  if (state && (!state.asOf || !Array.isArray(state.facts))) diags.push(diag("error", "schema", "knowledge/state.json needs 'asOf' and a 'facts' array"));

  const coverageAbs = path.join(D.knowledge, "coverage.json");
  const coverage = fs.existsSync(coverageAbs) ? read(coverageAbs, "knowledge/coverage.json") : { classifications: [] };

  /* per-node content hash. An artifact's hash includes its file bytes, so editing a
     file a pack depends on invalidates that pack exactly as editing its record does. */
  for (const n of nodes.values()) {
    let fileHash = null;
    if (n.kind === "artifact" && n.rec.path) {
      try { fileHash = U.sha256(U.readRel(root, n.rec.path)); } catch (e) { fileHash = "MISSING"; }
    }
    n.fileHash = fileHash;
    n.hash = U.hashOf({ rec: n.rec, file: fileHash });
  }

  const active = id => { const n = nodes.get(id); return !!(n && lifecycle.states[n.rec.lifecycle] && lifecycle.states[n.rec.lifecycle].active); };
  return { root, dirs: D, config, lifecycle, relations, schemaHashes, kschema, nodes, state, coverage, diags, active, of: kind => [...nodes.values()].filter(n => n.kind === kind).sort(U.byId) };
}

/* write one knowledge file back, deterministically (used by lifecycle transitions,
   handoffs and imports — the only code paths that mutate authored knowledge) */
function saveKind(root, kind, mutate) {
  const D = dirs(root);
  const abs = path.join(D.knowledge, KNOWLEDGE_FILES[kind]);
  const doc = U.readJSON(abs);
  mutate(doc.records, doc);
  doc.records.sort(U.byId);
  fs.writeFileSync(abs, JSON.stringify(doc, null, 2) + "\n");
  return doc;
}

module.exports = { load, saveKind, dirs, KNOWLEDGE_FILES, diag };
