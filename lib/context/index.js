/* Context continuity · build and verify.
   --------------------------------------------------------------------------
   build()   knowledge → packs, task packs, views. Renders everything in memory
             (cheap, deterministic) and writes only files whose bytes changed, so
             an unchanged input leaves its outputs untouched; reports which packs
             were stale and why. full:true deletes the generated outputs first —
             the two modes must agree byte for byte (tested).
   verify()  the CI gate. Re-derives everything and compares with what is on
             disk: schema, ids, owners, graph, lifecycle, archive checksums, pack
             freshness, generated-output drift, secrets, handoffs. Errors fail;
             warnings are reported as warnings, never as success. */
"use strict";

const fs = require("fs");
const path = require("path");
const U = require("./util");
const S = require("./store");
const Gr = require("./graph");
const P = require("./packs");
const A = require("./archive");
const C = require("./coverage");
const H = require("./hygiene");
const V = require("./views");
const Pr = require("./protocol");

function open(root) {
  const K = S.load(root);
  const G = Gr.build(K);
  return { K, G };
}

/* everything the build would write, as { relPath(under PROJECT-CONTEXT) → body } */
function renderOutputs(K, G) {
  const rendered = P.renderAll(K, G);
  const out = {};
  for (const p of rendered.packs) {
    for (const part of p.parts) out[part.file] = part.body;
    out["contexts/" + p.json.id + ".json"] = U.pretty(p.json);
  }
  out["contexts/index.json"] = U.pretty(P.indexJSON(K, rendered));
  const handoffs = Pr.loadHandoffs(K);
  for (const t of K.of("task")) { const tp = P.renderTaskPack(K, G, t.id, rendered, handoffs); out[tp.file] = tp.body; }
  const packStatus = rendered.packs.map(p => ({ id: p.json.id, fresh: true }));
  const coverage = C.compute(K, G, { packStatus, handoffs, archiveOpts: { offlineStore: true } });
  const views = V.render(K, G, { rendered, coverage, handoffs });
  for (const f of Object.keys(views)) out[f] = views[f];
  return { out, rendered, coverage };
}

function generatedOnDisk(K) {
  const files = [];
  for (const d of ["contexts", "task-packs"]) {
    let names = [];
    try { names = fs.readdirSync(path.join(K.dirs.base, d)); } catch (e) { }
    for (const n of names) if (/\.(md|json)$/.test(n)) files.push(d + "/" + n);
  }
  for (const v of K.config.generated.views || []) if (fs.existsSync(path.join(K.dirs.base, v))) files.push(v);
  return files.sort();
}

function build(root, opts) {
  opts = opts || {};
  const { K, G } = open(root);
  const errors = K.diags.concat(G.diags).filter(d => d.level === "error");
  if (errors.length && !opts.force) return { ok: false, errors, written: [], removed: [] };
  const before = P.status(K, G);
  const { out, rendered } = renderOutputs(K, G);
  const removed = [];
  if (opts.full) for (const f of generatedOnDisk(K)) { fs.rmSync(path.join(K.dirs.base, f)); removed.push(f); }
  const written = [];
  for (const f of Object.keys(out).sort()) if (U.writeIfChanged(path.join(K.dirs.base, f), out[f])) written.push(f);
  /* generated files no knowledge produces any more are derived output — remove them (git keeps history) */
  for (const f of generatedOnDisk(K)) if (!(f in out)) { fs.rmSync(path.join(K.dirs.base, f)); removed.push(f); }
  const secrets = Object.keys(out).flatMap(f => U.findSecrets(out[f]).map(h => f + ": " + h));
  return {
    ok: secrets.length === 0,
    errors: secrets.map(s => S.diag("error", "secret-in-output", "possible credential in generated output " + s, { remedy: "remove the secret from the knowledge record it came from" })),
    invalidated: before.filter(s => !s.fresh).map(s => ({ id: s.id, reason: s.reason, detail: s.detail })),
    written, removed: removed.filter((f, i, a) => a.indexOf(f) === i && !written.includes(f)),
    packs: rendered.packs.map(p => ({ id: p.json.id, status: p.json.status, parts: p.json.parts.map(x => x.bytes) }))
  };
}

function verify(root, opts) {
  opts = opts || {};
  const { K, G } = open(root);
  const errors = [], warnings = [], info = [];
  const put = d => (d.level === "error" ? errors : d.level === "warn" ? warnings : info).push(d);
  K.diags.forEach(put); G.diags.forEach(put);

  /* lifecycle registry is itself consistent */
  for (const t of K.lifecycle.transitions || []) for (const s of [t.from, t.to]) if (!K.lifecycle.states[s]) put(S.diag("error", "lifecycle-registry", "transition references unknown state '" + s + "'"));

  /* archive integrity */
  const archive = A.verifyAll(K, opts);
  for (const r of archive.results) {
    if (r.level === "error") put(S.diag("error", "archive-" + r.status, r.id + ": " + r.detail, { id: r.id, remedy: "restore the original bytes or record the source as missing/corrupted — never silently re-hash" }));
    else if (r.level === "warn") put(S.diag("warn", "archive-" + r.status, r.id + ": " + r.detail, { id: r.id }));
  }
  /* append-only identity: a recorded checksum is never silently recalculated */
  for (const p of A.identityAudit(K)) put(S.diag("error", "source-identity-rewritten", p.id + ": storage identity (kind/format/commit/blob/sha256/bytes/commits) changed in " + p.where + " since it was first committed in " + p.since + (p.now ? " — was " + JSON.stringify(p.was) + ", now " + JSON.stringify(p.now) : ""), { id: p.id, remedy: "restore the original identity; a re-captured or changed source is a NEW source id (npm run context:capture / capture-history)" }));
  for (const d of archive.duplicateBytes) put(S.diag("warn", "archive-duplicate-bytes", "the same bytes are archived under several ids: " + d.join(", ")));

  /* knowledge hygiene invariants that are correctness-critical */
  const kh = H.knowledge(K, G);
  for (const c of kh.conflicts) if (!c.trackedBy) put(S.diag("error", "untracked-conflict", c.between.join(" ⟷ ") + ": " + c.problem, { remedy: "open an issue of kind 'conflict' that affects both ids" }));
  for (const x of kh.historicalAsAuthority) put(S.diag("error", "historical-as-authority", x.id + " names historical evidence '" + x.owner + "' as its owner", { id: x.id, remedy: "point owner at the canonical source; cite the historical one in sources" }));
  for (const x of kh.supersededInActive) put(S.diag("error", "superseded-in-active-context", x.context + " includes " + x.id + " (" + x.lifecycle + ")", { remedy: "include the superseding record instead" }));
  for (const x of kh.missingOwner) put(S.diag("error", "missing-owner", x.id + " has owner '" + x.owner + "' which resolves to neither a record nor a repository file", { id: x.id }));
  for (const x of kh.obsolete) put(S.diag("error", "obsolete-authority", x.id + ": " + (x.problem || "owner " + x.owner + " is " + x.ownerLifecycle), { id: x.id }));
  for (const x of kh.duplicateStatements) put(S.diag("warn", "duplicate-statement", "identical statements: " + x.ids.join(", ")));
  for (const id of kh.orphans) put(S.diag("warn", "orphan-artifact", id + " is active but nothing references it"));

  const seg = C.segmentAccounting(K, opts);
  for (const d of seg.dangling) put(S.diag("error", "dangling-segment", d.ref + " cited by " + d.by.join(", ") + " does not exist in the archived source"));

  /* packs: fresh, intact, no orphans */
  const ro = renderOutputs(K, G);
  const st = P.status(K, G, ro.rendered);
  for (const s of st) if (!s.fresh) put(S.diag("error", "pack-" + s.reason, s.id + ": " + s.detail, { id: s.id, remedy: "npm run context:build (then commit the regenerated files)" }));
  for (const p of ro.rendered.packs) {
    if (p.json.status === "mandatory-over-budget") put(S.diag("warn", "pack-over-budget", p.json.id + ": mandatory block " + p.json.parts[0].bytes + " B exceeds its " + p.json.budgetBytes + " B budget"));
    if (p.json.status === "incomplete") put(S.diag("warn", "pack-incomplete", p.json.id + " excludes " + p.json.excluded.map(e => e.id).join(", ")));
    if (p.json.missing.length) put(S.diag("error", "pack-missing-reference", p.json.id + " references missing " + p.json.missing.join(", ")));
  }

  /* generated-output drift (byte comparison) */
  for (const f of Object.keys(ro.out).sort()) {
    let cur = null;
    try { cur = fs.readFileSync(path.join(K.dirs.base, f), "utf8"); } catch (e) { }
    if (cur !== ro.out[f]) put(S.diag("error", "generated-drift", "PROJECT-CONTEXT/" + f + (cur == null ? " is missing" : " differs from what the knowledge generates"), { remedy: "npm run context:build — never hand-edit generated files" }));
  }
  for (const f of generatedOnDisk(K)) if (!(f in ro.out)) put(S.diag("error", "generated-orphan", "PROJECT-CONTEXT/" + f + " is not produced by any knowledge", { remedy: "npm run context:build removes it" }));
  for (const f of Object.keys(ro.out)) for (const h of U.findSecrets(ro.out[f])) put(S.diag("error", "secret-in-output", "possible credential (" + h + ") in PROJECT-CONTEXT/" + f));

  /* handoffs and receipts */
  for (const h of Pr.loadHandoffs(K)) if (!h.valid) put(S.diag("error", "handoff-invalid", h.file + ": " + h.errors.join("; ")));
  for (const t of K.of("task")) if (t.rec.state === "in-progress" && !Pr.loadHandoffs(K).some(h => h.task === t.id)) put(S.diag("warn", "task-without-handoff", t.id + " is in progress with no handoff recorded"));

  /* informational */
  const Q = Gr.queries(K, G);
  /* traceability: a critical/high requirement without executable verification fails;
     a lower one, or one without an implementing artifact, is a warning */
  for (const x of Q["requirements-lacking-verification"]()) {
    const n = K.nodes.get(x.id);
    const hard = ["critical", "high"].includes(n.rec.priority) && n.rec.lifecycle === "canonical-active";
    put(S.diag(hard ? "error" : "warn", "requirement-unverified", x.id + " (" + n.rec.priority + ") has no 'verifies' edge", { id: x.id, remedy: "add the verifying test artifact to verifiedBy" }));
  }
  for (const x of Q["requirements-lacking-implementation"]()) put(S.diag("warn", "requirement-unimplemented", x.id + " has no 'implements' edge", { id: x.id }));

  /* entry points must agree with the tooling they point at */
  for (const ep of ["AGENTS.md", "CLAUDE.md"]) {
    if (!U.exists(root, ep)) { put(S.diag("error", "entry-point-missing", ep + " is missing")); continue; }
    const text = U.readRel(root, ep).toString("utf8");
    let scripts = {};
    try { scripts = U.readJSON(path.join(root, "package.json")).scripts || {}; } catch (e) { }
    for (const m of text.matchAll(/npm run ([a-z][\w:-]*)/g)) if (!scripts[m[1]]) put(S.diag("error", "entry-point-command", ep + " cites `npm run " + m[1] + "`, which package.json does not define"));
    for (const m of text.matchAll(/`(PROJECT-CONTEXT\/[^`<>*\s]+\.md)`/g)) if (!U.exists(root, m[1])) put(S.diag("error", "entry-point-path", ep + " cites " + m[1] + ", which does not exist"));
  }
  for (const x of Q["tasks-blocked-by-decisions"]()) put(S.diag("info", "task-blocked", x.task + ": unapproved decisions " + (x.unapprovedDecisions.join(", ") || "none") + "; open blockers " + (x.openBlockers.join(", ") || "none")));
  if (seg.unaccounted.length) put(S.diag("info", "segments-unaccounted", seg.unaccounted.length + " in-scope source segment(s) are unprocessed/ambiguous (see context:coverage)"));

  return { ok: errors.length === 0, errors, warnings, info, summary: { nodes: K.nodes.size, edges: G.edges.length, packs: ro.rendered.packs.length, sources: K.of("source").length, generatedFiles: Object.keys(ro.out).length } };
}

module.exports = { open, build, verify, renderOutputs };
