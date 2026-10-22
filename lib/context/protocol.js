/* Context continuity · the agent protocol: assimilation gate + durable handoff.
   --------------------------------------------------------------------------
   assimilate() is the gate every agent passes before changing code or canonical
   knowledge. It does the checking a small agent cannot do in its head — pack
   freshness, prerequisite availability, unresolved conflicts, the byte budget —
   and returns a receipt: which context was loaded, what is missing, the verdict.
   A receipt is evidence of LOADING, not proof of understanding.

   The gate fails closed: a stale or missing pack, a broken knowledge invariant,
   an open conflict that blocks the task, or a mandatory block that cannot fit the
   agent's budget is a 'blocked' verdict — never a pass with a footnote.

   handoff() writes the record a fresh agent continues from. Completed claims
   must carry evidence; a test "passed" only if its command and observed result
   are recorded. Plans are not progress, and the schema keeps them apart. */
"use strict";

const fs = require("fs");
const path = require("path");
const U = require("./util");
const P = require("./packs");
const Gr = require("./graph");
const { validate } = require("./schema");
const { saveKind } = require("./store");

function loadHandoffs(K) {
  let files = [];
  try { files = fs.readdirSync(K.dirs.handoffs).filter(f => /^HO-.*\.json$/.test(f)).sort(); } catch (e) { }
  let schema = null;
  try { schema = U.readJSON(path.join(K.dirs.schemas, "handoff.schema.json")); } catch (e) { }
  return files.map(f => {
    let h = null, errors = [];
    try { h = U.readJSON(path.join(K.dirs.handoffs, f)); } catch (e) { return { id: f.replace(/\.json$/, ""), file: f, valid: false, errors: ["unreadable: " + e.message] }; }
    if (schema) errors = validate(schema, h);
    if (h.id + ".json" !== f) errors.push("file name does not match id");
    return Object.assign({}, h, { file: f, valid: errors.length === 0, errors });
  });
}

function assimilate(K, G, taskId, opts) {
  opts = opts || {};
  const budget = opts.budget || K.config.budgets.defaultPackBytes;
  const checks = [], gaps = [];
  const check = (name, ok, detail) => { checks.push({ name, ok: !!ok, detail: detail || "" }); return ok; };
  const gap = (severity, code, message) => gaps.push({ severity, code, message });

  const repo = U.repoState(K.root);
  check("repository identified", repo.git, repo.git ? repo.branch + " @ " + String(repo.head).slice(0, 12) + (repo.dirty ? " (dirty: " + repo.status.length + " paths)" : " (clean)") : "not a git checkout");
  if (!repo.git) gap("warn", "no-git", "not a git checkout — HEAD and working-tree state are unknown");

  const kErr = K.diags.filter(d => d.level === "error"), gErr = G.diags.filter(d => d.level === "error");
  if (!check("knowledge valid", !kErr.length, kErr.length ? kErr.length + " error(s): " + kErr.slice(0, 3).map(d => d.message).join(" | ") : "")) gap("block", "knowledge-invalid", "the knowledge store has " + kErr.length + " error(s); run `npm run context:verify`");
  if (!check("graph valid", !gErr.length, gErr.length ? gErr.slice(0, 3).map(d => d.message).join(" | ") : G.edges.length + " edges")) gap("block", "graph-invalid", "the traceability graph has " + gErr.length + " error(s)");

  const masterIdx = path.join(K.dirs.base, "00-MASTER-INDEX.md");
  if (!check("master index present", fs.existsSync(masterIdx), "PROJECT-CONTEXT/00-MASTER-INDEX.md")) gap("block", "no-master-index", "PROJECT-CONTEXT/00-MASTER-INDEX.md is missing; run `npm run context:build`");

  const t = K.nodes.get(taskId);
  const receipt = {
    schema: "ctx-receipt/1",
    id: "RCPT-" + taskId.replace(/^TASK-/, "") + "-" + (opts.seq || "000"),
    createdAt: opts.now || new Date().toISOString(),
    agent: opts.agent || "unidentified-agent",
    task: taskId,
    repository: { branch: repo.branch, head: repo.head, dirty: repo.dirty },
    verdict: "blocked", budgetBytes: budget, readingOrder: [], packs: [], requirements: [], decisions: [], constraints: [], prerequisites: [], gaps, acceptance: [], scope: [], exclusions: [], checks
  };
  if (!check("task resolved", t && t.kind === "task", t ? t.rec.title : "no task " + taskId)) {
    gap("block", "unknown-task", "task " + taskId + " is not in knowledge/tasks.json — the task must be recorded before work starts");
    return finish(receipt);
  }
  const r = t.rec;
  if (["done", "abandoned"].includes(r.state)) gap("warn", "task-closed", "task state is '" + r.state + "' — confirm with the owner before reopening");
  receipt.acceptance = r.acceptance.slice(); receipt.scope = r.scope.slice(); receipt.exclusions = (r.exclusions || []).slice();

  /* the packs the task needs, prerequisites included, in dependency order */
  const rendered = opts.rendered || P.renderAll(K, G);
  const freshness = new Map(P.status(K, G, rendered).map(s => [s.id, s]));
  const needed = new Set();
  for (const c of r.contexts || []) {
    if (!K.nodes.has(c)) { gap("block", "missing-context", "task names context " + c + " which does not exist"); continue; }
    needed.add(c);
    for (const p of Gr.closure(G, c, ["depends-on"])) if ((K.nodes.get(p) || {}).kind === "context") needed.add(p);
  }
  for (const n of K.of("context")) if (n.rec.bootstrap && K.active(n.id)) needed.add(n.id);
  const order = rendered.order.filter(id => needed.has(id));
  for (const id of needed) if (!order.includes(id)) gap("block", "inactive-context", "context " + id + " is required but not active");

  /* at the agent's budget, re-split deterministically (in memory) */
  const atBudget = budget === K.config.budgets.defaultPackBytes ? rendered : P.renderAll(K, G, { budget });
  const taskPack = P.renderTaskPack(K, G, taskId, rendered, loadHandoffs(K));
  receipt.readingOrder.push({ step: "master-index", ref: "PROJECT-CONTEXT/00-MASTER-INDEX.md", bytes: fs.existsSync(masterIdx) ? fs.statSync(masterIdx).size : 0 });
  receipt.readingOrder.push({ step: "task-pack", ref: "PROJECT-CONTEXT/" + taskPack.file, bytes: U.byteLen(taskPack.body) });
  for (const id of order) {
    const f = freshness.get(id) || { fresh: false, reason: "missing" };
    const p = atBudget.packs.find(x => x.json.id === id).json;
    receipt.packs.push({ id, fingerprint: p.depFingerprint, fresh: !!f.fresh });
    if (!f.fresh) gap("block", "pack-" + f.reason, "pack " + id + " is " + f.reason + (f.detail ? " (" + f.detail + ")" : "") + " — run `npm run context:build` and commit the result");
    if (p.status === "mandatory-over-budget") gap("block", "over-budget", "pack " + id + ": its mandatory block (" + p.parts[0].bytes + " B) does not fit the " + budget + "-byte budget; essential knowledge cannot be loaded at this budget");
    if (p.status === "incomplete") gap("warn", "pack-incomplete", "pack " + id + " excludes " + p.excluded.length + " oversized non-mandatory block(s): " + p.excluded.map(e => e.id).join(", "));
    if (p.missing.length) gap("block", "missing-reference", "pack " + id + " references missing records: " + p.missing.join(", "));
    p.parts.forEach((part, i) => receipt.readingOrder.push({ step: i === 0 ? (id === order[0] ? "mandatory-bootstrap" : "pack") : "supplementary", ref: "PROJECT-CONTEXT/" + part.file + (budget !== K.config.budgets.defaultPackBytes ? " @" + budget : ""), bytes: part.bytes, estimatedTokens: part.estimatedTokens }));
    for (const m of p.mandatory) {
      const n = K.nodes.get(m);
      if (!n) continue;
      if (n.kind === "requirement" && !receipt.requirements.includes(m)) receipt.requirements.push(m);
      if (n.kind === "decision" && !receipt.decisions.includes(m)) receipt.decisions.push(m);
      if (n.kind === "constraint" && !receipt.constraints.includes(m)) receipt.constraints.push(m);
    }
  }
  for (const u of receipt.readingOrder) if (u.bytes > budget && u.step !== "supplementary") gap("block", "unit-over-budget", u.ref + " is " + u.bytes + " B, over the " + budget + "-byte budget");
  check("packs fresh", receipt.packs.every(p => p.fresh), receipt.packs.filter(p => !p.fresh).map(p => p.id).join(", "));
  for (const req of r.requirements || []) if (!receipt.requirements.includes(req)) receipt.requirements.push(req);
  for (const d of r.decisions || []) if (!receipt.decisions.includes(d)) receipt.decisions.push(d);
  for (const c of r.constraints || []) if (!receipt.constraints.includes(c)) receipt.constraints.push(c);
  receipt.requirements.sort(); receipt.decisions.sort(); receipt.constraints.sort();

  /* prerequisites of the task itself */
  for (const p of Gr.closure(G, taskId, ["depends-on"])) {
    const n = K.nodes.get(p);
    receipt.prerequisites.push(p);
    if (!n) gap("block", "missing-prerequisite", "prerequisite " + p + " does not exist");
    else if (n.kind === "task" && n.rec.state !== "done") gap("warn", "prerequisite-open", "prerequisite task " + p + " is '" + n.rec.state + "'");
    else if (n.kind !== "task" && n.kind !== "context" && !K.active(p)) gap("block", "prerequisite-inactive", "prerequisite " + p + " is " + n.rec.lifecycle);
  }
  check("prerequisites available", !gaps.some(g => /prerequisite/.test(g.code) && g.severity === "block"), receipt.prerequisites.join(", "));

  /* conflicts and blockers */
  for (const e of G.in(taskId)) {
    if (e.rel !== "blocks") continue;
    const n = K.nodes.get(e.from);
    if (n && n.kind === "issue" && n.rec.status === "open") gap(n.rec.kind === "conflict" || n.rec.severity === "critical" ? "block" : "warn", "open-" + n.rec.kind, n.id + ": " + n.rec.title);
  }
  const scopeIds = new Set(receipt.requirements.concat(receipt.decisions, receipt.constraints));
  for (const n of K.of("issue")) {
    if (n.rec.status !== "open" || n.rec.kind !== "conflict") continue;
    if ((n.rec.affects || []).some(a => scopeIds.has(a)) && !(n.rec.blocks || []).includes(taskId)) gap("warn", "conflict-in-scope", n.id + " (unresolved conflict) affects " + (n.rec.affects || []).filter(a => scopeIds.has(a)).join(", ") + " — do not treat either side as settled");
  }
  for (const d of receipt.decisions) { const n = K.nodes.get(d); if (n && n.rec.status === "proposed") gap("warn", "decision-unapproved", d + " is proposed, not owner-approved"); }
  for (const id of receipt.requirements) {
    const n = K.nodes.get(id);
    for (const s of (n && n.rec.sources) || []) { const src = K.nodes.get(s.ref); if (src && src.kind === "source" && src.rec.preservation !== "preserved") gap("warn", "source-" + src.rec.preservation, id + " cites " + src.id + ", which is " + src.rec.preservation + " — its original wording cannot be re-checked"); }
  }
  const hos = loadHandoffs(K).filter(h => h.task === taskId);
  if (hos.length) {
    const last = hos[hos.length - 1];
    receipt.readingOrder.splice(2, 0, { step: "latest-handoff", ref: "PROJECT-CONTEXT/handoffs/" + last.file, bytes: Buffer.byteLength(JSON.stringify(last)) });
    if (!last.valid) gap("block", "handoff-invalid", "latest handoff " + last.id + " fails its schema: " + last.errors.slice(0, 2).join("; "));
  }
  return finish(receipt);
}

function finish(receipt) {
  const blocked = receipt.gaps.some(g => g.severity === "block");
  receipt.verdict = blocked ? "blocked" : receipt.gaps.length ? "pass-with-warnings" : "pass";
  return receipt;
}

function writeReceipt(K, receipt) {
  fs.mkdirSync(K.dirs.receipts, { recursive: true });
  const base = "RCPT-" + receipt.task.replace(/^TASK-/, "");
  const n = fs.readdirSync(K.dirs.receipts).filter(f => f.startsWith(base + "-")).length + 1;
  receipt.id = base + "-" + String(n).padStart(3, "0");
  const schema = U.readJSON(path.join(K.dirs.schemas, "receipt.schema.json"));
  const errs = validate(schema, receipt);
  if (errs.length) throw new Error("receipt fails its own schema: " + errs.join("; "));
  const file = path.join(K.dirs.receipts, receipt.id + ".json");
  fs.writeFileSync(file, U.pretty(receipt), { flag: "wx" });
  return file;
}

/* ---------- handoff ---------- */
function handoff(K, G, taskId, input, opts) {
  opts = opts || {};
  const t = K.nodes.get(taskId);
  if (!t || t.kind !== "task") throw new Error("unknown task " + taskId);
  const existing = loadHandoffs(K).filter(h => h.task === taskId);
  const seq = String(existing.length + 1).padStart(3, "0");
  const repo = U.repoState(K.root);
  const rendered = P.renderAll(K, G);
  const fresh = new Map(P.status(K, G, rendered).map(s => [s.id, s]));
  const packs = (input.contextPacks || (t.rec.contexts || []).map(id => ({ id, fingerprint: (fresh.get(id) || {}).fingerprint || "MISSING" })));
  const h = {
    schema: "ctx-handoff/1",
    id: "HO-" + taskId.replace(/^TASK-/, "") + "-" + seq,
    task: taskId,
    createdAt: opts.now || new Date().toISOString(),
    agent: input.agent || opts.agent || "unidentified-agent",
    repository: { branch: repo.branch, head: repo.head, upstream: repo.upstream, dirty: repo.dirty, status: repo.status },
    objective: input.objective || t.rec.objective,
    state: input.state || t.rec.state,
    completed: input.completed || [],
    notCompleted: input.notCompleted || [],
    unverified: input.unverified || [],
    regressions: input.regressions || [],
    mustNotChange: input.mustNotChange || (t.rec.exclusions || []),
    prerequisites: input.prerequisites || Gr.closure(G, taskId, ["depends-on"]),
    filesInspected: input.filesInspected || [],
    filesChanged: input.filesChanged || [],
    commands: input.commands || [],
    tests: input.tests || [],
    blockers: input.blockers || [],
    nextAction: input.nextAction || "",
    verification: input.verification || t.rec.verification,
    contextPacks: packs,
    receipt: input.receipt,
    previous: existing.length ? existing[existing.length - 1].id : null
  };
  if (h.receipt === undefined) delete h.receipt;
  const schema = U.readJSON(path.join(K.dirs.schemas, "handoff.schema.json"));
  const errors = validate(schema, h);
  /* semantic rules beyond the schema: no unevidenced "passed", no plan-as-progress */
  for (const x of h.tests) if (x.result === "passed" && (x.exitCode !== 0 || !x.observed)) errors.push("test '" + x.command + "' is marked passed without exitCode 0 and an observed result");
  if (h.state === "done" && h.notCompleted.length) errors.push("state 'done' with notCompleted items — record the task as in-progress or move the items to a new task");
  if (h.state === "done" && h.tests.some(x => x.result === "failed" && !x.preExisting)) errors.push("state 'done' with a newly failing test");
  if (errors.length) return { ok: false, errors, handoff: h };
  if (opts.dryRun) return { ok: true, handoff: h, dryRun: true };
  fs.mkdirSync(K.dirs.handoffs, { recursive: true });
  fs.writeFileSync(path.join(K.dirs.handoffs, h.id + ".json"), U.pretty(h), { flag: "wx" });
  saveKind(K.root, "task", recs => {
    const r = recs.find(x => x.id === taskId);
    const from = r.state;
    r.state = h.state; r.nextAction = h.nextAction;
    r.history = (r.history || []).concat({ at: h.createdAt, change: "handoff " + h.id, from, to: h.state, by: h.agent, evidence: "PROJECT-CONTEXT/handoffs/" + h.id + ".json" });
  });
  return { ok: true, handoff: h, file: path.join(K.dirs.handoffs, h.id + ".json") };
}

module.exports = { assimilate, writeReceipt, handoff, loadHandoffs };
