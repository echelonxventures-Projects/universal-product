/* UCOS Ω∞ · context hygiene — measure duplication, drift and decay; propose, never destroy.
   --------------------------------------------------------------------------
   Context is not an accumulation target. This module measures what makes the
   context harder to use than it needs to be — duplicate files and paragraphs,
   near-duplicate documents, references to superseded artifacts, generated
   artifacts that drifted from their generator, artifacts with no owner, unresolved
   supersessions, bootstrap size and navigation depth — and turns each measurement
   into evidence plus a PROPOSED disposition.

   It is deterministic (hashes and exact set arithmetic, no model judgement) and
   strictly advisory: it reads the working tree and a throw-away copy, and writes
   nothing in the repository. Destructive or authority-changing dispositions are
   always marked as needing the owner's authorization (DEC-CTX-006).

   Metric thresholds are a RATCHET seeded from the observed baseline: a metric
   above its threshold is a regression that fails `context.js check`; a metric
   below it is reported so the threshold can be lowered. A metric listed in
   hygiene.ceilings (bootstrap size) is a budget, not a ratchet — tightening it
   would push governance out of the bootstrap. No target is invented that would
   delete meaningful information to reduce a count. */
"use strict";

const fs = require("fs");
const os = require("os");
const path = require("path");
const { execFileSync } = require("child_process");
const G = require("./context-graph.js");

const norm = s => s.toLowerCase().replace(/[`*_>#|\-]+/g, " ").replace(/\s+/g, " ").trim();

function paragraphs(text, min) {
  return text.split(/\n\s*\n/).map(norm).filter(p => p.length >= min);
}

/* run a generator against a throw-away copy of exactly the files it reads and
   compare what it would write with what is committed */
function derivedDrift(root, gen, check) {
  const t0 = Date.now();
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "ctx-drift-"));
  try {
    const nodes = [...gen.graph.nodes.values()].filter(n => !n.virtual && G.matchAny(n.path, check.copy));
    for (const n of nodes) {
      const dst = path.join(tmp, n.path);
      fs.mkdirSync(path.dirname(dst), { recursive: true });
      fs.copyFileSync(path.join(root, n.path), dst);
    }
    let ran = true, error = null;
    try { execFileSync(process.execPath, [path.join(tmp, check.generator)], { cwd: tmp, stdio: "ignore", timeout: 120000 }); }
    catch (e) { ran = false; error = e.message.split("\n")[0]; }
    const outputs = G.select(gen.graph.nodes, gen.graph.edges, check.outputs);
    const drifted = [];
    if (ran) for (const n of outputs) {
      let fresh = null;
      try { fresh = fs.readFileSync(path.join(tmp, n.path)); } catch (e) { }
      if (!fresh || G.sha256(fresh) !== n.digest) drifted.push(n.id);
    }
    return { id: check.id, generator: check.generator, conflict: check.conflict || null, ran, error, outputs: outputs.length, drifted, ms: Date.now() - t0 };
  } finally { fs.rmSync(tmp, { recursive: true, force: true }); }
}

function analyze(root, gen, opts) {
  opts = opts || {};
  const t0 = Date.now();
  const { graph, spec } = gen;
  const H = spec.hygiene || {};
  const nodes = [...graph.nodes.values()];
  const files = nodes.filter(n => !n.virtual);
  const active = n => /^active-/.test(n.lifecycle);
  const isText = n => n.lines != null;
  const findings = [];
  const plan = [];
  let bytesRead = 0;
  const readText = n => { const t = fs.readFileSync(path.join(root, n.path), "utf8"); bytesRead += t.length; return t; };
  const dependents = id => G.impact(graph, [id]).ids.size - 1;

  /* 1. exact duplicate files */
  const byDigest = new Map();
  for (const n of files) if (n.bytes > 0) { if (!byDigest.has(n.digest)) byDigest.set(n.digest, []); byDigest.get(n.digest).push(n); }
  const exactDupes = [...byDigest.values()].filter(g => g.length > 1).map(g => g.map(n => n.id).sort());
  for (const g of exactDupes) plan.push({ priority: 2, category: "exact-duplicate", subjects: g, evidence: "identical bytes (sha256)", proposal: "keep the highest-authority copy as canonical; turn the others into references or retire them", authorization: true });

  /* 2. duplicate paragraphs (authored text only: a template repeated across
        generated artifacts has one source, so it is not Knowledge-Once drift) */
  const min = H.duplicateMinParagraphChars || 160;
  const textNodes = files.filter(n => isText(n) && (H.textClasses || []).includes(n.class));
  const paraSets = new Map();
  const paraOwners = new Map();
  for (const n of textNodes) {
    const ps = [...new Set(paragraphs(readText(n), min).map(G.sha256))];
    paraSets.set(n.id, new Set(ps));
    for (const h of ps) { if (!paraOwners.has(h)) paraOwners.set(h, []); paraOwners.get(h).push(n.id); }
  }
  const groups = [...paraOwners.entries()].filter(([, o]) => o.length > 1);
  const authoredGroups = groups.filter(([, o]) => o.filter(id => graph.nodes.get(id).kind !== "derived").length > 1);
  const derivedOnlyGroups = groups.length - authoredGroups.length;
  /* aggregate authored duplication by document pair so the plan is readable */
  const pairCount = new Map();
  for (const [, o] of authoredGroups) {
    const a = o.filter(id => graph.nodes.get(id).kind !== "derived").sort();
    for (let i = 0; i < a.length; i++) for (let j = i + 1; j < a.length; j++) { const k = a[i] + "\u0000" + a[j]; pairCount.set(k, (pairCount.get(k) || 0) + 1); }
  }

  /* 3. near-duplicate documents: most of the smaller one's distinct lines recur in
        the other. Line-level, so short-line documents are compared as fairly as prose. */
  const ratio = H.nearDuplicateRatio || 0.9;
  const minLine = H.nearDuplicateMinLineChars || 24;
  const lineSets = new Map(), lineOwners = new Map();
  for (const n of textNodes.filter(n => n.kind !== "derived")) {
    const ls = new Set(fs.readFileSync(path.join(root, n.path), "utf8").split("\n").map(norm).filter(l => l.length >= minLine).map(G.sha256));
    lineSets.set(n.id, ls);
    for (const h of ls) { if (!lineOwners.has(h)) lineOwners.set(h, []); lineOwners.get(h).push(n.id); }
  }
  const linePairs = new Map();
  for (const o of lineOwners.values()) {
    if (o.length < 2 || o.length > 8) continue;   /* a line in many files is boilerplate, not duplication */
    const a = o.slice().sort();
    for (let i = 0; i < a.length; i++) for (let j = i + 1; j < a.length; j++) { const k = a[i] + "\u0000" + a[j]; linePairs.set(k, (linePairs.get(k) || 0) + 1); }
  }
  const near = [];
  for (const [k, shared] of linePairs) {
    const [a, b] = k.split("\u0000");
    const small = Math.min(lineSets.get(a).size, lineSets.get(b).size);
    const r = shared / Math.max(1, small);
    if (small >= 10 && r >= ratio) near.push({ a, b, shared, ratio: Math.round(r * 1000) / 1000 });
  }
  near.sort((x, y) => y.ratio - x.ratio || G.cmp(x.a, y.a));
  for (const p of near) {
    const na = graph.nodes.get(p.a), nb = graph.nodes.get(p.b);
    const keep = G.authorityRank(spec, na.authority) <= G.authorityRank(spec, nb.authority) && /^active-|superseded/.test(na.lifecycle) ? na : nb;
    const other = keep === na ? nb : na;
    plan.push({ priority: 2, category: "near-duplicate", subjects: [keep.id, other.id], evidence: p.shared + " shared distinct lines, " + Math.round(p.ratio * 100) + "% of the smaller document", proposal: "consolidate into " + keep.id + "; mark " + other.id + " consolidatable → retired once its unique lines (if any) are migrated; version control keeps the history", impact: dependents(other.id), authorization: true });
  }
  const topPairs = [...pairCount.entries()].filter(([k]) => !near.some(p => p.a + "\u0000" + p.b === k)).sort((x, y) => y[1] - x[1] || G.cmp(x[0], y[0])).slice(0, opts.top || 10);
  for (const [k, c] of topPairs) { const [a, b] = k.split("\u0000"); plan.push({ priority: 3, category: "repeated-explanation", subjects: [a, b], evidence: c + " paragraph(s) of ≥" + min + " chars appear verbatim in both", proposal: "keep the explanation in the higher-authority document; replace the repeat with a reference", authorization: true }); }

  /* 4. references to superseded / retired artifacts from active text */
  const deprecated = nodes.filter(n => !n.virtual && (n.lifecycle === "superseded" || n.lifecycle === "retired"));
  const conflictSubjects = new Set(graph.edges.filter(e => e.type === "conflicts-with").map(e => e.to));
  const depRefs = [];
  for (const n of files.filter(n => active(n) && isText(n) && n.class !== "context-registry")) {
    const text = fs.readFileSync(path.join(root, n.path), "utf8");
    for (const d of deprecated) {
      const name = path.basename(d.path);
      if (n.id === d.id || !text.includes(name)) continue;
      depRefs.push({ from: n.id, to: d.id, acknowledged: conflictSubjects.has(n.id) || conflictSubjects.has(d.id) });
    }
  }
  for (const r of depRefs.filter(r => !r.acknowledged)) plan.push({ priority: 2, category: "deprecated-reference", subjects: [r.from, r.to], evidence: r.from + " names superseded " + r.to, proposal: "point the reference at the successor recorded in supersessions[]", authorization: false });

  /* 5. generated artifacts that drifted from their generator */
  const drift = opts.noDerived ? [] : (H.derivedChecks || []).map(c => derivedDrift(root, gen, c));
  for (const d of drift) if (!d.ran || d.drifted.length) plan.push({ priority: 1, category: "derived-drift", subjects: [d.generator], evidence: d.ran ? d.drifted.length + " of " + d.outputs + " outputs differ from a fresh run" : "generator failed: " + d.error, proposal: d.conflict ? "resolve " + d.conflict + " (regenerate in its own reviewed change, or fix the generator)" : "regenerate and commit", authorization: true });

  /* 6. open conflicts are cleanup items with the highest priority */
  for (const c of spec.conflicts || []) if (c.status !== "resolved") plan.push({ priority: c.severity === "high" ? 1 : 2, category: "open-conflict", subjects: [c.id], evidence: c.statement, proposal: c.proposedResolution || c.decisionNeeded, authorization: true });

  /* 7. unreferenced active artifacts — informational: many are leaves by nature */
  const unreferenced = files.filter(n => active(n) && !(graph.out.get(n.id) || []).length && !(graph.in.get(n.id) || []).length).map(n => n.id);

  /* ---------- metrics ---------- */
  const code = c => gen.findings.filter(f => f.code === c && f.severity === "error").length;
  const always = new Set((spec.bootstrap || {}).alwaysLoad || []);
  const bootstrapChars = gen.packs.filter(p => always.has(p.unit)).reduce((a, p) => a + p.text.length, 0);
  /* navigation steps: hops along unit prerequisite links from the always-loaded units */
  const unitPre = new Map(gen.manifest.units.map(u => [u.id, u.prerequisites]));
  const depth = new Map();
  const depthOf = (id, seen) => {
    if (depth.has(id)) return depth.get(id);
    if (always.has(id)) return 1;
    if (seen.has(id)) return 1;
    seen.add(id);
    const d = 1 + Math.max(1, ...(unitPre.get(id) || []).map(p => depthOf(p, seen)));
    depth.set(id, d);
    return d;
  };
  const navSteps = Math.max(0, ...gen.manifest.units.filter(u => u.members).map(u => depthOf(u.id, new Set())));
  const handoffs = files.filter(n => n.class === "handoff-record");
  const badHandoffs = new Set(gen.findings.filter(f => f.code === "HANDOFF_INVALID").map(f => f.subject));
  const metrics = {
    competingDefinitions: code("CONFLICTING_AUTHORITY"),
    openSourceOfTruthConflicts: (spec.conflicts || []).filter(c => c.status !== "resolved").length,
    exactDuplicateFiles: exactDupes.reduce((a, g) => a + g.length - 1, 0),
    nearDuplicatePairs: near.length,
    duplicateParagraphGroups: authoredGroups.length,
    derivedDrift: drift.reduce((a, d) => a + (d.ran ? d.drifted.length : d.outputs), 0),
    brokenReferences: code("DANGLING_EDGE") + code("CONSTRAINT_QUOTE_MISSING") + code("MISSING_ARTIFACT"),
    orphanedActiveArtifacts: code("ORPHAN_ARTIFACT"),
    ownerlessActiveArtifacts: code("NO_OWNER"),
    unresolvedSupersessions: code("SUPERSESSION_UNRECORDED") + code("SUPERSESSION_INCOMPLETE") + code("SUPERSEDED_STILL_ACTIVE"),
    bootstrapChars,
    maxNavigationSteps: navSteps,
    unresumableHandoffs: handoffs.filter(n => badHandoffs.has(n.path)).length
  };
  const info = {
    handoffs: handoffs.length,
    resumablePercent: handoffs.length ? Math.round(100 * (handoffs.length - metrics.unresumableHandoffs) / handoffs.length) : 100,
    derivedOnlyParagraphGroups: derivedOnlyGroups,
    deprecatedReferences: depRefs.length,
    acknowledgedDeprecatedReferences: depRefs.filter(r => r.acknowledged).length,
    unreferencedActiveArtifacts: unreferenced.length,
    archiveBytes: files.filter(n => n.lifecycle === "historical-evidence" || n.lifecycle === "superseded").reduce((a, n) => a + n.bytes, 0),
    workingBytes: files.filter(n => active(n)).reduce((a, n) => a + n.bytes, 0),
    bytesRead,
    ms: Date.now() - t0,
    driftChecks: drift.map(d => ({ id: d.id, ran: d.ran, outputs: d.outputs, drifted: d.drifted.length, ms: d.ms }))
  };
  const thresholds = H.thresholds || {};
  const ratchet = [];
  for (const k of Object.keys(metrics)) {
    if (!(k in thresholds)) continue;
    if (opts.noDerived && k === "derivedDrift") continue;
    if (metrics[k] > thresholds[k]) { ratchet.push({ metric: k, value: metrics[k], threshold: thresholds[k], verdict: "regression" }); findings.push({ severity: "error", code: "HYGIENE_REGRESSION", subject: k, message: metrics[k] + " exceeds the ratchet threshold " + thresholds[k] }); }
    else if (metrics[k] < thresholds[k] && !(H.ceilings || []).includes(k)) ratchet.push({ metric: k, value: metrics[k], threshold: thresholds[k], verdict: "improved — lower the threshold to " + metrics[k] });
  }
  plan.sort((a, b) => a.priority - b.priority || G.cmp(a.category, b.category) || G.cmp(a.subjects.join(), b.subjects.join()));
  plan.forEach((p, i) => { p.id = "HYG-" + String(i + 1).padStart(3, "0"); });
  return { metrics, info, thresholds, ratchet, findings, plan, nearDuplicates: near, deprecatedReferences: depRefs, unreferenced, drift };
}

module.exports = { analyze, derivedDrift, paragraphs };
