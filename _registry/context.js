#!/usr/bin/env node
/* UCOS Ω∞ · the context command line — discover, traverse, verify, regenerate, hand off.
   --------------------------------------------------------------------------
   One entry point over context-graph.js (the registry and typed graph),
   context-packs.js (bounded packs, sequences, manifest, map) and
   context-hygiene.js (duplication, drift, metrics, cleanup plan). No network, no
   service, no dependency beyond node and (optionally) git. Every command is
   read-only except `build` (writes _context/ only) and `handoff` (appends one
   record under _registry/handoffs/ and then builds).

   Usage: node _registry/context.js <command> [args]

     bootstrap [--task T] [--window N] [--loaded a,b] [--json]   plan / receipt (exit 2 = REFUSE)
     resolve <T> [--json]        mandatory + relevant closure, governing context, packs in order
     prereqs <T>                 only the ordered mandatory prerequisites
     impact <T>                  downstream dependents, tests, packs that change or need review
     list                        every pack with size and position
     sequence [ID]               an ordered sequence with its END marker (default: full)
     next <PACK> [--sequence S]  the next pack (or END) — derived, never guessed
     open <PACK>                 print a pack
     search <QUERY>              find artifacts; historical results are labelled and ranked last
     validate                    integrity findings (exit 1 on any error)
     stale                       generated files that no longer match the repository
     build [--affected]          regenerate _context/ (only changed files are written)
     check                       validate + stale + determinism + hygiene ratchet (CI gate)
     hygiene [--json] [--no-derived]  metrics, ratchet and the prioritized cleanup plan
     handoff --template          print a draft record to fill
     handoff --task T --draft F --start REV [--verify CMD]… [--pr URL]   append a record
     resume <TASK>               resume from the latest handoff, without the conversation

   T (a target) is a node id (UCOS-CON-000004, file:lib/authz.js, LAW-002), a path
   (lib/authz.js), a unit (unit:runtime-server), a pack (runtime-server/2), or
   `changed:<base-rev>` for every file changed since a revision. */
"use strict";

const fs = require("fs");
const path = require("path");
const { execFileSync, spawnSync } = require("child_process");
const G = require("./context-graph.js");
const P = require("./context-packs.js");
const H = require("./context-hygiene.js");

const DEFAULT_ROOT = path.resolve(__dirname, "..");

/* ============================ shared ============================ */
function parseArgs(argv) {
  const a = { _: [], verify: [] };
  for (let i = 0; i < argv.length; i++) {
    const x = argv[i];
    if (x.startsWith("--")) {
      const k = x.slice(2);
      const v = argv[i + 1] && !argv[i + 1].startsWith("--") ? argv[++i] : true;
      if (k === "verify") a.verify.push(v); else a[k] = v;
    } else a._.push(x);
  }
  return a;
}

function onDiskManifest(root, spec) {
  try { return JSON.parse(fs.readFileSync(path.join(root, spec.output.dir, "manifest.json"), "utf8")); } catch (e) { return null; }
}

/* the files the generator would write vs what is on disk */
function staleness(root, gen) {
  const dir = gen.spec.output.dir;
  const stale = [], missing = [], extra = [];
  for (const [rel, text] of gen.files) {
    let cur = null;
    try { cur = fs.readFileSync(path.join(root, rel), "utf8"); } catch (e) { }
    if (cur == null) missing.push(rel); else if (cur !== text) stale.push(rel);
  }
  const packDir = path.join(root, dir, "packs");
  if (fs.existsSync(packDir)) for (const f of fs.readdirSync(packDir).sort()) { const rel = dir + "/packs/" + f; if (!gen.files.has(rel)) extra.push(rel); }
  /* which sources moved since the committed manifest — the cause, not just the symptom */
  const old = onDiskManifest(root, gen.spec);
  const oldNodes = new Map(((old && old.nodes) || []).map(n => [n.id, n.digest]));
  const changed = [], added = [], removed = [];
  for (const n of gen.graph.nodes.values()) { if (!oldNodes.has(n.id)) added.push(n.id); else if (oldNodes.get(n.id) !== n.digest) changed.push(n.id); }
  for (const id of oldNodes.keys()) if (!gen.graph.nodes.has(id)) removed.push(id);
  return { stale, missing, extra, changed, added, removed, fresh: !stale.length && !missing.length && !extra.length, old };
}

/* target → node ids */
function resolveTarget(gen, t) {
  const { graph } = gen;
  if (!t) return { ids: [], label: null };
  if (t.startsWith("changed:")) {
    const base = t.slice(8);
    const out = G.git(gen.root, ["diff", "--name-only", base]);
    if (out == null) throw new Error("cannot diff against " + base);
    const ids = out.split("\n").filter(Boolean).map(p => graph.byPath.get(p)).filter(Boolean).map(n => n.id);
    return { ids, label: "files changed since " + base };
  }
  if (t.startsWith("unit:")) { const ids = gen.assignment.members.get(t.slice(5)); if (!ids) throw new Error("no unit " + t.slice(5)); return { ids: ids.slice(), label: t }; }
  if (gen.packById.has(t)) return { ids: gen.packById.get(t).members.slice(), label: "pack " + t };
  if (graph.nodes.has(t)) return { ids: [t], label: t };
  if (graph.byPath.has(t)) return { ids: [graph.byPath.get(t).id], label: t };
  if (graph.nodes.has("file:" + t)) return { ids: ["file:" + t], label: t };
  throw new Error("target '" + t + "' is not a registered node, path, unit or pack (try `context.js search " + t + "`)");
}

const primaryIndex = gen => { const s = gen.sequences.find(x => x.id === gen.spec.primarySequence); return new Map(s.packs.map((p, i) => [p, i])); };
const packOf = (gen, id) => { const u = gen.assignment.owner.get(id); if (!u) return null; return (gen.unitPacks.get(u) || []).find(p => p.members.includes(id)) || null; };

/* the closure of a task and the ordered packs that cover it */
function plan(gen, target) {
  const { graph, spec } = gen;
  const { ids, label } = resolveTarget(gen, target);
  const mand = G.closure(graph, ids, "mandatory");
  const rel = G.closure(graph, ids, "relevant");
  const lifecycles = new Set((spec.bootstrap || {}).taskLifecycles || []);
  const pidx = primaryIndex(gen);
  const rank = id => { const p = packOf(gen, id); return p ? pidx.get(p.id) : 1e9; };
  const ordered = G.orderPrereqFirst(graph, [...mand.ids], rank).order;
  const relevantOnly = [...rel.ids].filter(id => !mand.ids.has(id)).sort((a, b) => rank(a) - rank(b) || G.cmp(a, b));
  const always = new Set((spec.bootstrap || {}).alwaysLoad || []);
  const packs = new Set();
  for (const p of gen.packs) if (always.has(p.unit)) packs.add(p.id);
  for (const id of ordered) { const p = packOf(gen, id); if (p) packs.add(p.id); }
  const packList = [...packs].sort((a, b) => pidx.get(a) - pidx.get(b));
  /* historical material reached through a mandatory edge is surfaced, never hidden,
     but labelled so it is not mistaken for a requirement */
  const historical = ordered.filter(id => !lifecycles.has(graph.nodes.get(id).lifecycle));
  const conflicts = new Set();
  for (const id of rel.ids) for (const e of graph.in.get(id) || []) if (e.type === "conflicts-with") conflicts.add(e.from);
  const governing = ordered.filter(id => ["constraint", "decision"].includes(graph.nodes.get(id).class));
  const dangling = gen.findings.filter(f => f.severity === "error" && (f.code === "DANGLING_EDGE" || f.code === "CONSTRAINT_QUOTE_MISSING") && (rel.ids.has(f.subject) || ids.some(i => f.message.includes(i))));
  return { label, starts: ids, mandatory: ordered, relevant: relevantOnly, historical, governing, conflicts: [...conflicts].sort(), packs: packList, missing: dangling };
}

function stages(gen, packIds, window) {
  const out = [];
  let cur = [], used = 0;
  for (const id of packIds) {
    const len = gen.packById.get(id).text.length;
    if (len > window) throw new Error("pack " + id + " (" + len + " chars) is larger than the window " + window + " — rebuild with a smaller budgets.packChars");
    if (used + len > window && cur.length) { out.push(cur); cur = []; used = 0; }
    cur.push(id); used += len;
  }
  if (cur.length) out.push(cur);
  return out;
}

function repoState(root) {
  const g = a => G.git(root, a);
  let remote = g(["remote", "get-url", "origin"]);
  if (remote) remote = remote.replace(/\/\/[^@/]+@/, "//");   /* never print embedded credentials */
  const status = g(["status", "--porcelain"]);
  return {
    remote: remote || null, branch: g(["rev-parse", "--abbrev-ref", "HEAD"]), commit: g(["rev-parse", "HEAD"]),
    dirty: status == null ? null : status.split("\n").filter(Boolean).length,
    contextCommit: g(["log", "-1", "--format=%h %ad", "--date=short", "--", "_context/manifest.json"]) || null
  };
}

/* ============================ commands ============================ */
const out = s => process.stdout.write(s + "\n");

function cmdBootstrap(root, a) {
  const t0 = Date.now();
  const repo = repoState(root);
  let gen;
  try { gen = P.generate(root); } catch (e) {
    out("REFUSE — the context registry cannot be read: " + e.message);
    return 2;
  }
  gen.root = root;
  const st = staleness(root, gen);
  const errors = gen.findings.filter(f => f.severity === "error");
  const window = Number(a.window) || gen.spec.budgets.bootstrapChars || 40000;
  const p = a.task ? plan(gen, a.task) : { label: null, starts: [], mandatory: [], relevant: [], historical: [], governing: [], conflicts: [], packs: gen.packs.filter(x => ((gen.spec.bootstrap || {}).alwaysLoad || []).includes(x.unit)).map(x => x.id), missing: [] };
  if (!a.task) for (const pk of p.packs) for (const id of gen.packById.get(pk).members) if (["constraint", "decision"].includes(gen.graph.nodes.get(id).class)) p.governing.push(id);
  const openConflicts = (gen.spec.conflicts || []).filter(c => c.status !== "resolved").map(c => c.id);
  const reasons = [];
  if (errors.length) reasons.push(errors.length + " registry/graph integrity error(s) — run `context.js validate`");
  if (!st.fresh) reasons.push("generated context is stale (" + (st.stale.length + st.missing.length + st.extra.length) + " file(s)) — run `context.js build` and commit _context/");
  if (p.missing.length) reasons.push(p.missing.length + " mandatory reference(s) of the task do not resolve");
  let loaded = null, missingLoads = [], wrongDigest = [];
  if (a.loaded) {
    loaded = String(a.loaded).split(",").map(s => s.trim()).filter(Boolean);
    const have = new Map(loaded.map(l => { const [id, d] = l.split("@"); return [id, d || null]; }));
    for (const id of p.packs) {
      if (!have.has(id)) { missingLoads.push(id); continue; }
      const d = have.get(id);
      if (d && !G.sha256(gen.packById.get(id).text).startsWith(d)) wrongDigest.push(id);
    }
    if (missingLoads.length) reasons.push("mandatory packs not loaded: " + missingLoads.join(", "));
    if (wrongDigest.length) reasons.push("loaded copies do not match the current packs: " + wrongDigest.join(", "));
  }
  const status = reasons.length ? "REFUSE" : loaded ? "ASSIMILATED" : "READY";
  const st2 = stages(gen, p.packs, window);
  const receipt = {
    schema: "ucos.context.receipt.v1", status, reasons,
    repository: repo,
    registry: { spec: G.SPEC_PATH, manifest: gen.spec.output.dir + "/manifest.json", inputsDigest: gen.manifest.inputsDigest, fresh: st.fresh, errors: errors.length, warnings: gen.findings.filter(f => f.severity === "warning").length },
    task: p.label, mandatory: p.mandatory.length, relevant: p.relevant.length,
    plan: st2.map((s, i) => ({ stage: i + 1, packs: s.map(id => ({ id, file: gen.packById.get(id).file, chars: gen.packById.get(id).text.length, digest: G.sha256(gen.packById.get(id).text).slice(0, 12) })) })),
    governing: p.governing, openConflicts, taskConflicts: p.conflicts, historicalInClosure: p.historical,
    sourcesOnDemand: p.mandatory.map(id => gen.graph.nodes.get(id)).filter(n => n.path && !n.virtual).map(n => n.path),
    loaded, notLoaded: missingLoads, ms: Date.now() - t0
  };
  if (a.json) { out(JSON.stringify(receipt, null, 1)); return status === "REFUSE" ? 2 : 0; }
  out("UCOS context " + (loaded ? "assimilation receipt" : "bootstrap plan") + " — " + status);
  out("  repository  " + (repo.remote || "(no remote)") + " · " + (repo.branch || "?") + " · " + (repo.commit ? repo.commit.slice(0, 12) : "?") + " · working tree " + (repo.dirty == null ? "unknown" : repo.dirty ? repo.dirty + " change(s)" : "clean"));
  out("  registry    " + G.SPEC_PATH + " · manifest " + (st.fresh ? "fresh" : "STALE") + " · inputs " + gen.manifest.inputsDigest.slice(0, 12) + " · " + errors.length + " error(s), " + receipt.registry.warnings + " warning(s)" + (repo.contextCommit ? " · context last committed " + repo.contextCommit : ""));
  out("  task        " + (p.label || "(orientation only — pass --task to resolve one)") + (p.label ? " → " + p.mandatory.length + " mandatory, " + p.relevant.length + " relevant" : ""));
  for (const s of receipt.plan) out("  stage " + s.stage + "     " + s.packs.map(x => x.id + " (" + x.chars + ")").join(", "));
  out("  governing   " + (p.governing.join(", ") || "—"));
  out("  conflicts   open: " + (openConflicts.join(", ") || "none") + (p.conflicts.length ? " · touching this task: " + p.conflicts.join(", ") : ""));
  if (p.historical.length) out("  historical  " + p.historical.join(", ") + " — evidence only, not requirements");
  if (receipt.sourcesOnDemand.length) out("  on demand   " + receipt.sourcesOnDemand.length + " source file(s) in the closure — open by path when the task needs their substance (`context.js resolve " + (a.task || "") + "`)");
  if (loaded) out("  loaded      " + loaded.length + " pack(s); not loaded: " + (missingLoads.join(", ") || "none"));
  for (const r of reasons) out("  ✗ " + r);
  if (status === "READY") out("  next        read the stage packs in order, then re-run with --loaded <ids> for the receipt");
  if (status === "REFUSE") out("  → do not begin consequential work until the reasons above are resolved");
  return status === "REFUSE" ? 2 : 0;
}

function cmdResolve(root, a, onlyPrereqs) {
  const gen = P.generate(root); gen.root = root;
  const p = plan(gen, a._[1]);
  const n = id => gen.graph.nodes.get(id);
  const line = id => { const x = n(id); const pk = packOf(gen, id); return "  " + id.padEnd(44) + " " + String(x.lifecycle).padEnd(19) + " " + (pk ? pk.id : "—"); };
  if (a.json) { out(JSON.stringify(p, null, 1)); return 0; }
  out("target: " + p.label + " (" + p.starts.length + " node(s))");
  out("\nmandatory prerequisites, in reading order (" + p.mandatory.length + "):");
  for (const id of p.mandatory) out(line(id));
  if (onlyPrereqs) return 0;
  out("\nrelevant (runtime dependencies — load when the task touches them) (" + p.relevant.length + "):");
  for (const id of p.relevant) out(line(id));
  out("\ngoverning constraints and decisions: " + (p.governing.join(", ") || "—"));
  out("open conflicts touching the closure: " + (p.conflicts.join(", ") || "none"));
  if (p.historical.length) out("historical (evidence, not requirements): " + p.historical.join(", "));
  if (p.missing.length) { out("\n✗ unresolved mandatory references:"); for (const f of p.missing) out("  " + f.code + " " + f.subject + " — " + f.message); }
  out("\npacks to load, in order (" + p.packs.length + " of " + gen.packs.length + ", " + p.packs.reduce((s, id) => s + gen.packById.get(id).text.length, 0) + " chars):");
  for (const id of p.packs) out("  " + id.padEnd(28) + " " + gen.packById.get(id).file);
  return p.missing.length ? 2 : 0;
}

function cmdImpact(root, a) {
  const gen = P.generate(root); gen.root = root;
  const { ids, label } = resolveTarget(gen, a._[1]);
  const im = G.impact(gen.graph, ids);
  const affected = predictAffected(gen, new Set(ids));
  const review = new Set([...im.ids].map(id => packOf(gen, id)).filter(Boolean).map(p => p.id));
  if (a.json) { out(JSON.stringify({ target: label, dependents: [...im.ids].filter(i => !ids.includes(i)).sort(), tests: [...im.tests].sort(), packsRegenerated: [...affected].sort(), packsToReview: [...review].sort() }, null, 1)); return 0; }
  out("impact of " + label);
  out("\ndownstream dependents (transitive, " + (im.ids.size - ids.length) + "):");
  for (const id of [...im.ids].filter(i => !ids.includes(i)).sort()) out("  " + id);
  out("\ntests that exercise them (" + im.tests.size + "): " + ([...im.tests].sort().join(", ") || "—"));
  out("\npacks whose bytes change when it changes (" + affected.size + "): " + [...affected].sort().join(", "));
  out("packs describing downstream artifacts — review for meaning (" + review.size + "): " + [...review].sort().join(", "));
  return 0;
}

/* the packs a change to `changed` node ids will regenerate: the units owning them
   and every node one edge away, plus sequence neighbours when a unit's part count
   moves. build --affected proves the generator never changes more than this. */
function predictAffected(gen, changed, old) {
  const units = new Set();
  const touch = id => { const u = gen.assignment.owner.get(id); if (u) units.add(u); };
  const oldEdges = old ? (old.edges || []) : [];
  for (const id of changed) {
    touch(id);
    for (const e of gen.graph.out.get(id) || []) touch(e.to);
    for (const e of gen.graph.in.get(id) || []) touch(e.from);
    for (const e of oldEdges) { if (e[0] === id) touch(e[2]); if (e[2] === id) touch(e[0]); }
    if (old) for (const n of old.nodes || []) if (n.id === id && n.unit && gen.unitPacks.has(n.unit)) units.add(n.unit);
  }
  /* a constraint quotes its source: the source changing changes the constraint's entry */
  for (const c of gen.spec.constraints || []) { const s = gen.graph.byPath.get(c.source); if (s && changed.has(s.id)) touch(c.id); }
  const packs = new Set();
  for (const u of units) for (const p of gen.unitPacks.get(u) || []) packs.add(p.id);
  if (old) {
    const oldUnits = new Map((old.units || []).map(u => [u.id, u.packs]));
    for (const u of units) for (const id of oldUnits.get(u) || []) packs.add(id);
    for (const u of gen.units) {
      const before = (oldUnits.get(u.id) || []).length, after = (gen.unitPacks.get(u.id) || []).length;
      if (before === after) continue;
      for (const s of gen.sequences) {
        const firstIdx = s.packs.findIndex(id => id.startsWith(u.id + "/"));
        if (firstIdx < 0) continue;
        if (firstIdx > 0) packs.add(s.packs[firstIdx - 1]);
        const lastIdx = s.packs.length - 1 - [...s.packs].reverse().findIndex(id => id.startsWith(u.id + "/"));
        if (lastIdx + 1 < s.packs.length) packs.add(s.packs[lastIdx + 1]);
        for (const id of s.packs.filter(id => id.startsWith(u.id + "/"))) packs.add(id);
      }
      for (const id of oldUnits.get(u.id) || []) packs.add(id);
    }
  }
  return packs;
}

function writeOutputs(root, gen) {
  const written = [], removed = [];
  for (const [rel, text] of gen.files) {
    const abs = path.join(root, rel);
    let cur = null;
    try { cur = fs.readFileSync(abs, "utf8"); } catch (e) { }
    if (cur === text) continue;
    fs.mkdirSync(path.dirname(abs), { recursive: true });
    fs.writeFileSync(abs, text);
    written.push(rel);
  }
  const packDir = path.join(root, gen.spec.output.dir, "packs");
  if (fs.existsSync(packDir)) for (const f of fs.readdirSync(packDir)) {
    const rel = gen.spec.output.dir + "/packs/" + f;
    if (!gen.files.has(rel)) { fs.unlinkSync(path.join(packDir, f)); removed.push(rel); }
  }
  return { written, removed };
}

function cmdBuild(root, a) {
  const t0 = Date.now();
  const gen = P.generate(root, { budget: a.budget ? Number(a.budget) : null }); gen.root = root;
  const errors = gen.findings.filter(f => f.severity === "error");
  if (errors.length && !a.force) {
    out("✗ refusing to generate from an invalid context graph (" + errors.length + " error(s)) — fix them or inspect with --force:");
    for (const f of errors.slice(0, 40)) out("  ✗ " + f.code + " " + f.subject + " — " + f.message);
    if (errors.length > 40) out("  … " + (errors.length - 40) + " more (`context.js validate`)");
    return 1;
  }
  const st = staleness(root, gen);
  let predicted = null;
  if (a.affected && st.old) predicted = predictAffected(gen, new Set([...st.changed, ...st.added, ...st.removed]), st.old);
  const w = writeOutputs(root, gen);
  out("✓ context generated in " + (Date.now() - t0) + " ms — " + gen.manifest.counts.files + " files, " + gen.manifest.counts.nodes + " nodes, " + gen.manifest.counts.edges + " edges, " + gen.manifest.counts.packs + " packs, " + gen.manifest.counts.sequences + " sequences");
  out("  sources changed since the last build: " + st.changed.length + " changed, " + st.added.length + " added, " + st.removed.length + " removed");
  out("  wrote " + w.written.length + " file(s)" + (w.written.length ? ": " + w.written.join(", ") : "") + (w.removed.length ? " · removed " + w.removed.join(", ") : ""));
  if (predicted) {
    const packOfFile = new Map([...gen.packs.map(p => [p.file, p.id]), ...((st.old.packs || []).map(p => [p.file, p.id]))]);
    const actual = [...w.written, ...w.removed].filter(f => packOfFile.has(f)).map(f => packOfFile.get(f));
    const surprise = actual.filter(id => !predicted.has(id));
    out("  invalidation: predicted " + predicted.size + " pack(s) by reverse traversal; " + actual.length + " actually changed" + (surprise.length ? "" : " — all within the prediction"));
    if (surprise.length) { out("✗ INVALIDATION_MISMATCH — packs changed that reverse traversal did not predict: " + surprise.join(", ")); return 1; }
  }
  return 0;
}

function cmdValidate(root, a) {
  const gen = P.generate(root); gen.root = root;
  const f = gen.findings;
  const show = a.all ? f : f.filter(x => x.severity !== "info");
  if (a.json) { out(JSON.stringify(f, null, 1)); return f.some(x => x.severity === "error") ? 1 : 0; }
  for (const x of show) out("  " + (x.severity === "error" ? "✗" : x.severity === "warning" ? "!" : "·") + " " + x.code + " " + x.subject + " — " + x.message);
  const e = f.filter(x => x.severity === "error").length, w = f.filter(x => x.severity === "warning").length;
  out((e ? "✗" : "✓") + " " + gen.manifest.counts.nodes + " nodes, " + gen.manifest.counts.edges + " edges, " + gen.manifest.counts.packs + " packs — " + e + " error(s), " + w + " warning(s)");
  return e ? 1 : 0;
}

function cmdStale(root) {
  const gen = P.generate(root); gen.root = root;
  const st = staleness(root, gen);
  out("sources since the committed manifest: " + st.changed.length + " changed, " + st.added.length + " added, " + st.removed.length + " removed");
  for (const id of st.changed) out("  ~ " + id);
  for (const id of st.added) out("  + " + id);
  for (const id of st.removed) out("  - " + id);
  for (const f of st.stale) out("  stale    " + f);
  for (const f of st.missing) out("  missing  " + f);
  for (const f of st.extra) out("  orphaned " + f + " (no longer generated)");
  out(st.fresh ? "✓ generated context is fresh" : "✗ generated context is stale — run `node _registry/context.js build`");
  return st.fresh ? 0 : 1;
}

function cmdCheck(root, a) {
  const t0 = Date.now();
  let ok = true;
  const gen = P.generate(root); gen.root = root;
  const errors = gen.findings.filter(f => f.severity === "error");
  out((errors.length ? "✗" : "✓") + " validate: " + gen.manifest.counts.nodes + " nodes, " + gen.manifest.counts.edges + " edges, " + errors.length + " error(s)");
  for (const f of errors) out("    ✗ " + f.code + " " + f.subject + " — " + f.message);
  if (errors.length) ok = false;
  const st = staleness(root, gen);
  out((st.fresh ? "✓" : "✗") + " fresh: " + (st.fresh ? "every generated file matches the repository" : (st.stale.length + st.missing.length + st.extra.length) + " generated file(s) stale/missing/orphaned; sources changed: " + [...st.changed, ...st.added, ...st.removed].slice(0, 12).join(", ") + " — run `node _registry/context.js build`"));
  if (!st.fresh) ok = false;
  const again = P.generate(root);
  const differs = [...gen.files].filter(([k, v]) => again.files.get(k) !== v).map(([k]) => k);
  out((differs.length ? "✗" : "✓") + " deterministic: two generations over unchanged inputs are " + (differs.length ? "DIFFERENT in " + differs.join(", ") : "byte-identical (" + gen.files.size + " files)"));
  if (differs.length) ok = false;
  const oversize = gen.packs.filter(p => p.text.length > gen.spec.budgets.packChars);
  out((oversize.length ? "✗" : "✓") + " bounded: " + gen.packs.length + " packs, largest " + Math.max(...gen.packs.map(p => p.text.length)) + " ≤ budget " + gen.spec.budgets.packChars);
  if (!a["no-hygiene"]) {
    const h = H.analyze(root, gen, { noDerived: !!a["no-derived"] });
    const reg = h.ratchet.filter(r => r.verdict === "regression");
    out((reg.length ? "✗" : "✓") + " hygiene ratchet: " + Object.keys(h.metrics).length + " metrics, " + reg.length + " regression(s)" + (reg.length ? ": " + reg.map(r => r.metric + " " + r.value + " > " + r.threshold).join(", ") : ""));
    for (const r of h.ratchet.filter(r => r.verdict !== "regression")) out("    · " + r.metric + " " + r.value + " < " + r.threshold + " (" + r.verdict + ")");
    if (reg.length) ok = false;
  }
  out((ok ? "✓ context check passed" : "✗ context check FAILED") + " in " + (Date.now() - t0) + " ms");
  return ok ? 0 : 1;
}

function cmdHygiene(root, a) {
  const gen = P.generate(root); gen.root = root;
  const h = H.analyze(root, gen, { noDerived: !!a["no-derived"], top: Number(a.top) || 10 });
  if (a.json) { out(JSON.stringify(h, null, 1)); return h.findings.some(f => f.severity === "error") ? 1 : 0; }
  out("context quality metrics (threshold = ratchet from the observed baseline):");
  for (const k of Object.keys(h.metrics)) out("  " + k.padEnd(28) + String(h.metrics[k]).padStart(8) + (k in h.thresholds ? "  ≤ " + h.thresholds[k] + (h.metrics[k] > h.thresholds[k] ? "  ✗ REGRESSION" : "") : ""));
  out("  " + "resumable handoffs".padEnd(28) + String(h.info.resumablePercent + "%").padStart(8) + "  (" + h.info.handoffs + " record(s))");
  out("  " + "working vs archive bytes".padEnd(28) + String(h.info.workingBytes).padStart(8) + " / " + h.info.archiveBytes + " (the archive never enters a default bootstrap)");
  out("  " + "analysis cost".padEnd(28) + String(h.info.ms + " ms").padStart(8) + ", " + h.info.bytesRead + " chars read" + h.info.driftChecks.map(d => "; " + d.id + " " + d.ms + " ms").join(""));
  out("\nprioritized cleanup plan (" + h.plan.length + " item(s)) — proposals only; ✋ = needs the owner's authorization:");
  for (const p of h.plan) out("  " + p.id + " P" + p.priority + " " + (p.authorization ? "✋ " : "   ") + p.category.padEnd(21) + " " + p.subjects.join(" ⇄ ") + "\n      evidence: " + p.evidence.slice(0, 300) + "\n      proposal: " + p.proposal + (p.impact != null ? "\n      impact:   " + p.impact + " downstream dependent(s)" : ""));
  return h.findings.some(f => f.severity === "error") ? 1 : 0;
}

function cmdList(root) {
  const gen = P.generate(root);
  const pidx = primaryIndex(gen);
  for (const p of gen.packs) out("  " + String(pidx.get(p.id) + 1).padStart(3) + ". " + p.id.padEnd(28) + String(p.text.length).padStart(6) + " chars  " + String(p.members.length).padStart(3) + " artifact(s)  " + p.file);
  out(gen.packs.length + " packs; budget " + gen.spec.budgets.packChars + " chars each");
  return 0;
}

function cmdSequence(root, a) {
  const gen = P.generate(root);
  const id = a._[1] || gen.spec.primarySequence;
  const s = gen.sequences.find(x => x.id === id);
  if (!s) { out("no sequence '" + id + "'; sequences: " + gen.sequences.map(x => x.id).join(", ")); return 1; }
  out("sequence " + s.id + " (" + s.kind + ") — " + (s.purpose || ""));
  s.packs.forEach((p, i) => out("  " + String(i + 1).padStart(3) + ". " + p.padEnd(28) + gen.packById.get(p).file));
  out("  ■ END:" + s.id + " — " + s.packs.length + " pack(s); manifest digest " + G.sha256(JSON.stringify(s.packs)).slice(0, 12));
  return 0;
}

function cmdNext(root, a) {
  const gen = P.generate(root);
  const id = a._[1];
  const s = gen.sequences.find(x => x.id === (a.sequence || gen.spec.primarySequence));
  if (!s) { out("no such sequence"); return 1; }
  const i = s.packs.indexOf(id);
  if (i < 0) { out("pack " + id + " is not in sequence " + s.id); return 1; }
  if (i === s.packs.length - 1) { out("■ END:" + s.id + " — " + id + " is the last of " + s.packs.length + " pack(s)"); return 0; }
  out(s.packs[i + 1] + "\t" + gen.packById.get(s.packs[i + 1]).file);
  return 0;
}

function cmdOpen(root, a) {
  const gen = P.generate(root);
  const p = gen.packById.get(a._[1]);
  if (!p) { out("no pack '" + a._[1] + "' (`context.js list`)"); return 1; }
  process.stdout.write(p.text);
  return 0;
}

function cmdSearch(root, a) {
  const gen = P.generate(root);
  const q = String(a._.slice(1).join(" ")).toLowerCase();
  if (!q) { out("usage: context.js search <query>"); return 1; }
  const live = new Set((gen.spec.bootstrap || {}).taskLifecycles || []);
  const hits = [...gen.graph.nodes.values()].filter(n => [n.id, n.path, n.title, n.summary].some(v => v && String(v).toLowerCase().includes(q)));
  hits.sort((x, y) => (live.has(x.lifecycle) ? 0 : 1) - (live.has(y.lifecycle) ? 0 : 1) || G.authorityRank(gen.spec, x.authority) - G.authorityRank(gen.spec, y.authority) || G.cmp(x.id, y.id));
  for (const n of hits) { const pk = packOf(gen, n.id); out("  " + (live.has(n.lifecycle) ? "" : "[" + n.lifecycle.toUpperCase() + " — not an active requirement] ") + n.id + "  (" + n.authority + ", " + n.lifecycle + ")  " + (pk ? pk.id : "") + "\n      " + (n.title || "")); }
  out(hits.length + " match(es)");
  return 0;
}

/* ---------- handoffs ---------- */
function handoffDir(root, task) { return path.join(root, "_registry", "handoffs", task); }
function records(root, task) {
  const dir = handoffDir(root, task);
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir).filter(f => /^\d{4}\.json$/.test(f)).sort().map(f => ({ file: path.join(dir, f), bytes: fs.readFileSync(path.join(dir, f)) }));
}

function template() {
  return {
    objective: "", status: "in-progress | interrupted | blocked | completed",
    authority: { instruction: "who asked for this work and where (issue, message, decision id)", governedBy: [] },
    context: { packsUsed: [], sourcesUsed: [] },
    asserted: { decisions: [], results: [], failures: [], limitations: [], risks: [], unresolved: [], notDone: [] },
    resume: { prerequisites: [], nextAction: "" },
    references: { pullRequest: null }
  };
}

function cmdHandoff(root, a) {
  if (a.template) { out(JSON.stringify(template(), null, 1)); return 0; }
  const task = a.task, draftPath = a.draft, start = a.start;
  if (!task || !draftPath || !start) { out("usage: context.js handoff --task T --draft F --start REV [--verify CMD]… [--pr URL]"); return 1; }
  const spec = G.loadSpec(root);
  const secretRes = (spec.security.secretPatterns || []).map(s => new RegExp(s, "i"));
  const draft = JSON.parse(fs.readFileSync(draftPath, "utf8"));
  const prev = records(root, task);
  const g = args => G.git(root, args);
  const startRev = g(["rev-parse", "--verify", start + "^{commit}"]);
  if (!startRev) { out("✗ --start " + start + " is not a commit in this repository"); return 1; }
  const end = g(["rev-parse", "HEAD"]);
  const committed = (g(["diff", "--name-status", startRev, "HEAD"]) || "").split("\n").filter(Boolean).map(l => { const [s, ...p] = l.split("\t"); return { path: p[p.length - 1], status: s, state: "committed" }; });
  const working = (g(["status", "--porcelain"]) || "").split("\n").filter(Boolean).map(l => ({ path: l.slice(3), status: l.slice(0, 2).trim(), state: "uncommitted" }));
  const scrub = s => { let t = s; for (const r of secretRes) t = t.replace(new RegExp(r.source, "gi"), "[REDACTED]"); return t; };
  const commands = [];
  for (const cmd of a.verify) {
    const t0 = Date.now();
    const r = spawnSync("sh", ["-c", cmd], { cwd: root, encoding: "utf8", maxBuffer: 256 << 20 });
    const output = (r.stdout || "") + (r.stderr || "");
    commands.push({ cmd, exitCode: r.status, ms: Date.now() - t0, outputSha256: G.sha256(output), outputTail: scrub(output.split("\n").filter(Boolean).slice(-12).join("\n")) });
    out((r.status === 0 ? "✓" : "✗") + " verified: " + cmd + " → exit " + r.status);
  }
  let manifestDigest = null;
  try { manifestDigest = G.sha256(fs.readFileSync(path.join(root, spec.output.dir, "manifest.json"))); } catch (e) { }
  const rec = {
    schema: G.HANDOFF_SCHEMA, taskId: task, seq: prev.length + 1,
    previousDigest: prev.length ? G.sha256(prev[prev.length - 1].bytes) : null,
    status: draft.status, objective: draft.objective, authority: draft.authority,
    verified: {
      note: "Produced by context.js from git and from executing each command; not agent assertions.",
      revisions: { start: startRev, end, branch: g(["rev-parse", "--abbrev-ref", "HEAD"]) },
      changedFiles: committed.concat(working),
      commands,
      contextManifestDigest: manifestDigest
    },
    asserted: draft.asserted, context: draft.context, resume: draft.resume,
    references: Object.assign({}, draft.references || {}, a.pr ? { pullRequest: a.pr } : {})
  };
  const problems = G.handoffProblems(rec, rec.previousDigest, rec.seq, secretRes);
  if (problems.length) { out("✗ handoff incomplete — nothing written:"); for (const p of problems) out("  - " + p); return 1; }
  const gen0 = P.generate(root);
  for (const p of rec.resume.prerequisites) if (!gen0.graph.nodes.has(p) && !gen0.graph.byPath.has(p) && !gen0.packById.has(p)) { out("✗ resume.prerequisites names '" + p + "', which is not a registered node, path or pack — nothing written"); return 1; }
  for (const p of rec.context.packsUsed) if (!gen0.packById.has(String(p).split("@")[0])) { out("✗ context.packsUsed names unknown pack '" + p + "' — nothing written"); return 1; }
  fs.mkdirSync(handoffDir(root, task), { recursive: true });
  const file = path.join(handoffDir(root, task), String(rec.seq).padStart(4, "0") + ".json");
  if (fs.existsSync(file)) { out("✗ " + file + " exists — records are append-only"); return 1; }
  fs.writeFileSync(file, JSON.stringify(rec, null, 1) + "\n");
  out("✓ appended " + path.relative(root, file) + " (seq " + rec.seq + ", chain " + (rec.previousDigest ? rec.previousDigest.slice(0, 12) : "genesis") + ")");
  return cmdBuild(root, {});
}

function cmdResume(root, a) {
  const task = a._[1];
  const list = records(root, task);
  if (!list.length) { out("REFUSE — no handoff records for task " + task + " under _registry/handoffs/" + task + "/"); return 2; }
  const gen = P.generate(root); gen.root = root;
  const last = JSON.parse(list[list.length - 1].bytes.toString("utf8"));
  const lastRel = path.relative(root, list[list.length - 1].file).split(path.sep).join("/");
  const chain = gen.findings.filter(f => f.code === "HANDOFF_INVALID" && f.subject.startsWith("_registry/handoffs/" + task + "/"));
  const reasons = chain.map(f => "record " + f.subject + ": " + f.message);
  const g = args => G.git(root, args);
  const end = last.verified.revisions.end;
  const known = g(["cat-file", "-e", end + "^{commit}"]) != null;
  const ancestor = known && spawnSync("git", ["merge-base", "--is-ancestor", end, "HEAD"], { cwd: root }).status === 0;
  const since = known ? (g(["rev-list", "--count", end + "..HEAD"]) || "0") : "?";
  const moved = known ? (g(["diff", "--name-only", end, "HEAD"]) || "").split("\n").filter(Boolean) : [];
  const prereqs = (last.resume.prerequisites || []).map(p => gen.packById.has(p) ? null : (gen.graph.nodes.has(p) ? p : gen.graph.byPath.has(p) ? gen.graph.byPath.get(p).id : "✗" + p));
  for (const p of prereqs) if (p && p.startsWith("✗")) reasons.push("prerequisite " + p.slice(1) + " no longer resolves");
  const ids = prereqs.filter(p => p && !p.startsWith("✗"));
  const packIds = new Set(((gen.spec.bootstrap || {}).alwaysLoad || []).flatMap(u => (gen.unitPacks.get(u) || []).map(p => p.id)));
  for (const p of last.resume.prerequisites || []) if (gen.packById.has(p)) packIds.add(p);
  const handPack = packOf(gen, gen.graph.byPath.get(lastRel) ? gen.graph.byPath.get(lastRel).id : "");
  if (handPack) packIds.add(handPack.id);
  const mand = G.closure(gen.graph, ids, "mandatory");
  for (const id of mand.ids) { const pk = packOf(gen, id); if (pk) packIds.add(pk.id); }
  const pidx = primaryIndex(gen);
  const ordered = [...packIds].sort((x, y) => pidx.get(x) - pidx.get(y));
  const touchedSince = moved.filter(f => (last.verified.changedFiles || []).some(c => c.path === f));
  out("resume " + task + " from " + lastRel + " — " + (reasons.length ? "REFUSE" : "READY"));
  out("  status      " + last.status + " · objective: " + last.objective);
  out("  authority   " + last.authority.instruction);
  out("  revisions   " + last.verified.revisions.start.slice(0, 12) + " → " + end.slice(0, 12) + " (" + last.verified.revisions.branch + ")" + (known ? " · HEAD is " + since + " commit(s) later" + (ancestor ? "" : " and does NOT descend from it") : " · end revision not in this clone"));
  if (touchedSince.length) out("  ! changed since the handoff, among the files the task touched: " + touchedSince.join(", "));
  out("  verified    " + last.verified.commands.map(c => c.cmd + " → " + c.exitCode).join("; ") + (last.verified.commands.length ? "" : "no commands were verified"));
  const A = last.asserted;
  for (const k of ["results", "failures", "limitations", "risks", "unresolved", "notDone", "decisions"]) if ((A[k] || []).length) out("  " + k.padEnd(11) + " " + A[k].map(x => typeof x === "string" ? x : JSON.stringify(x)).join(" | "));
  out("  next action " + last.resume.nextAction);
  out("  load        " + ordered.join(", "));
  for (const r of reasons) out("  ✗ " + r);
  return reasons.length ? 2 : 0;
}

/* ============================ dispatch ============================ */
function main(argv, root) {
  root = root || process.env.CONTEXT_ROOT || DEFAULT_ROOT;
  const a = parseArgs(argv);
  const cmd = a._[0];
  const table = {
    bootstrap: cmdBootstrap, resolve: (r, x) => cmdResolve(r, x, false), prereqs: (r, x) => cmdResolve(r, x, true), impact: cmdImpact,
    list: cmdList, sequence: cmdSequence, next: cmdNext, open: cmdOpen, search: cmdSearch, map: (r) => { process.stdout.write(P.generate(r).files.get(G.loadSpec(r).output.dir + "/MAP.md")); return 0; },
    validate: cmdValidate, stale: cmdStale, build: cmdBuild, check: cmdCheck, hygiene: cmdHygiene, handoff: cmdHandoff, resume: cmdResume
  };
  if (!table[cmd]) { out(fs.readFileSync(__filename, "utf8").match(/Usage:[\s\S]*?\*\//)[0].replace(/\*\/$/, "").trim()); return cmd ? 1 : 0; }
  try { return table[cmd](root, a); }
  catch (e) { out("✗ " + e.message); return 1; }
}

if (require.main === module) {
  process.stdout.on("error", e => { if (e.code === "EPIPE") process.exit(process.exitCode || 0); else throw e; });   /* `| head` is a normal reader */
  process.exitCode = main(process.argv.slice(2));
}

module.exports = { main, plan, staleness, predictAffected, resolveTarget, stages, writeOutputs };
