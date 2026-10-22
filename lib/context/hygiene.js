/* Context continuity · hygiene, lifecycle transitions and safe consolidation.
   --------------------------------------------------------------------------
   Hygiene FINDS clutter and PROPOSES consolidation. It never deletes, and never
   merges on its own: old, long, similar or unused is not the same as redundant.

   A lifecycle change goes through transition(), which enforces the registry in
   schemas/lifecycle.json (allowed edges, required fields, approval) and appends
   to the record's history — so every retirement is traceable and reversible
   (the prior state is in history and in git).

   consolidate() applies a consolidation PLAN only when every unique item of
   every source record (statement, each acceptance criterion, each source ref,
   rationale) is mapped to a destination that actually contains it, or is
   explicitly retained with a reason — and only with a named approver. */
"use strict";

const fs = require("fs");
const path = require("path");
const U = require("./util");
const { saveKind } = require("./store");

/* ---------- file-level scan ---------- */
function listFiles(K) {
  const cfg = K.config.hygiene || {};
  const exts = cfg.scan && cfg.scan.extensions || [".md", ".txt"];
  const excl = (cfg.scan && cfg.scan.exclude || []).map(e => path.join(K.root, e));
  let files = [];
  const tracked = U.gitText(K.root, ["ls-files", "-z"]);
  if (tracked != null) files = tracked.split("\0").filter(Boolean);
  else {
    (function walk(d) {
      for (const e of fs.readdirSync(d, { withFileTypes: true })) {
        const p = path.join(d, e.name);
        if (e.isDirectory()) { if (!excl.includes(p) && e.name !== ".git" && e.name !== "node_modules") walk(p); }
        else files.push(path.relative(K.root, p));
      }
    })(K.root);
  }
  return files.filter(f => exts.includes(path.extname(f)) && !excl.some(x => path.join(K.root, f).startsWith(x + path.sep)) && fs.existsSync(path.join(K.root, f))).sort();
}

function shingles(text, k) {
  const words = text.toLowerCase().replace(/[^a-z0-9\s]/g, " ").split(/\s+/).filter(Boolean);
  const set = new Set();
  for (let i = 0; i + k <= words.length; i++) set.add(U.sha256(words.slice(i, i + k).join(" ")).slice(0, 12));
  return set;
}
function jaccard(a, b) {
  if (!a.size || !b.size) return 0;
  let inter = 0;
  const [s, l] = a.size < b.size ? [a, b] : [b, a];
  for (const x of s) if (l.has(x)) inter++;
  return inter / (a.size + b.size - inter);
}

function scan(K) {
  const cfg = K.config.hygiene || {};
  const files = listFiles(K);
  const info = files.map(f => { const buf = fs.readFileSync(path.join(K.root, f)); return { file: f, bytes: buf.length, sha: U.sha256(buf), text: buf.toString("utf8") }; });

  /* exact duplicates */
  const bySha = new Map();
  for (const i of info) { if (!bySha.has(i.sha)) bySha.set(i.sha, []); bySha.get(i.sha).push(i.file); }
  const exactDuplicates = [...bySha.values()].filter(v => v.length > 1);

  /* near duplicates (word-shingle Jaccard), size-ratio pre-filter */
  const min = cfg.nearDuplicateMinBytes || 1500, th = cfg.nearDuplicateJaccard || 0.6, k = cfg.shingle || 8;
  const cand = info.filter(i => i.bytes >= min && i.bytes <= 400000);
  const sh = new Map(cand.map(i => [i.file, shingles(i.text, k)]));
  const nearDuplicates = [];
  for (let a = 0; a < cand.length; a++) for (let b = a + 1; b < cand.length; b++) {
    const x = cand[a], y = cand[b];
    if (x.sha === y.sha) continue;
    if (Math.min(x.bytes, y.bytes) / Math.max(x.bytes, y.bytes) < 0.4) continue;
    const j = jaccard(sh.get(x.file), sh.get(y.file));
    if (j >= th) nearDuplicates.push({ files: [x.file, y.file], jaccard: Math.round(j * 1000) / 1000 });
  }

  /* broken local markdown links */
  const brokenLinks = [];
  const linkRe = /\]\(([^)\s]+)\)/g;
  for (const i of info) {
    if (!i.file.endsWith(".md")) continue;
    let fence = false;
    i.text.split("\n").forEach((line, ln) => {
      if (/^\s*```/.test(line)) { fence = !fence; return; }
      if (fence) return;
      let m;
      linkRe.lastIndex = 0;
      while ((m = linkRe.exec(line))) {
        let target = m[1].split("#")[0];
        if (!target || /^[a-z][a-z0-9+.-]*:/i.test(target) || target.startsWith("<")) continue;
        try { target = decodeURIComponent(target); } catch (e) { }
        const abs = path.resolve(path.join(K.root, path.dirname(i.file)), target);
        if (!abs.startsWith(path.resolve(K.root))) { brokenLinks.push({ file: i.file, line: ln + 1, target: m[1], reason: "escapes repository" }); continue; }
        if (!fs.existsSync(abs)) brokenLinks.push({ file: i.file, line: ln + 1, target: m[1], reason: "target does not exist" });
      }
    });
  }

  /* oversized files on the ACTIVE read path (entry points, active artifacts, packs) */
  const limit = cfg.oversizedActiveBytes || 60000;
  const activePaths = new Set(["AGENTS.md", "CLAUDE.md"]);
  for (const n of K.of("artifact")) if (!n.rec.imported && K.active(n.id) && n.rec.path && n.rec.type !== "code" && n.rec.type !== "test") activePaths.add(n.rec.path);
  const oversizedActive = info.filter(i => activePaths.has(i.file) && i.bytes > limit).map(i => ({ file: i.file, bytes: i.bytes, limit }));
  const oversizedAny = info.filter(i => i.bytes > limit).map(i => ({ file: i.file, bytes: i.bytes }));

  return { files: info.length, exactDuplicates, nearDuplicates, brokenLinks, oversizedActive, oversizedAny };
}

/* ---------- knowledge-level hygiene ---------- */
function knowledge(K, G) {
  const out = { duplicateStatements: [], conflicts: [], historicalAsAuthority: [], supersededInActive: [], missingOwner: [], orphans: [], obsolete: [] };
  const norm = s => String(s || "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
  const seen = new Map();
  for (const n of K.nodes.values()) {
    if (n.rec.imported || !K.active(n.id)) continue;
    const s = norm(n.rec.statement);
    if (s.length < 20) continue;
    if (seen.has(s)) out.duplicateStatements.push({ ids: [seen.get(s), n.id] }); else seen.set(s, n.id);
  }
  for (const e of G.edges) if (e.rel === "conflicts-with") {
    const resolved = K.of("issue").some(i => i.rec.kind === "conflict" && i.rec.status === "resolved" && (i.rec.affects || []).includes(e.from) && (i.rec.affects || []).includes(e.to));
    const tracked = K.of("issue").some(i => i.rec.kind === "conflict" && i.rec.status === "open" && (i.rec.affects || []).includes(e.from) && (i.rec.affects || []).includes(e.to));
    if (!resolved) out.conflicts.push({ between: [e.from, e.to], trackedBy: tracked ? "open conflict issue" : null, problem: tracked ? null : "conflicts-with edge has no conflict issue — it could be silently treated as settled" });
  }
  for (const n of K.nodes.values()) {
    if (n.rec.imported || !K.active(n.id)) continue;
    const owner = n.rec.owner;
    if (owner) {
      const o = K.nodes.get(owner);
      if ((o && o.kind === "source" && o.rec.lifecycle === "historical-evidence") || /^_superseded\//.test(owner)) out.historicalAsAuthority.push({ id: n.id, owner });
      if (o && ["superseded", "retired"].includes(o.rec.lifecycle)) out.obsolete.push({ id: n.id, owner, ownerLifecycle: o.rec.lifecycle });
    }
    for (const s of n.rec.supersededBy || []) if (K.active(n.id) && n.kind !== "source") out.obsolete.push({ id: n.id, problem: "active but names supersededBy " + s });
  }
  const Q = require("./graph").queries(K, G);
  out.supersededInActive = Q["superseded-in-active-contexts"]();
  out.missingOwner = Q["active-without-owner"]();
  const referenced = new Set(); for (const e of G.edges) { referenced.add(e.from); referenced.add(e.to); }
  out.orphans = K.of("artifact").filter(n => !n.rec.imported && K.active(n.id) && !referenced.has(n.id)).map(n => n.id);
  return out;
}

function proposals(fileScan) {
  return fileScan.nearDuplicates.map((d, i) => ({
    id: "CONSOLIDATE-" + String(i + 1).padStart(3, "0"),
    files: d.files, jaccard: d.jaccard,
    action: "review", automated: false,
    steps: ["compare meaning, authority, scope and exceptions of both files", "map every unique statement to one canonical owner", "record retained-separately items with a reason", "transition the replaced artifact to superseded (requires approval)", "rebuild contexts and re-run context:verify"]
  }));
}

/* ---------- lifecycle transitions ---------- */
function transition(K, id, to, opts) {
  opts = opts || {};
  const n = K.nodes.get(id);
  if (!n) throw new Error("no record " + id);
  if (n.rec.imported) throw new Error(id + " is owned by " + n.rec.owner + " — change it there, not here");
  const from = n.rec.lifecycle;
  if (!K.lifecycle.states[to]) throw new Error("unknown lifecycle state '" + to + "'");
  const t = (K.lifecycle.transitions || []).find(x => x.from === from && x.to === to);
  if (!t) throw new Error("transition " + from + " → " + to + " is not allowed by schemas/lifecycle.json");
  if (t.requiresApproval && !opts.approvedBy) throw new Error("transition " + from + " → " + to + " requires approval: pass --approve <name> (destructive or authority-changing)");
  for (const f of t.requires || []) if (f === "supersededBy" && !(opts.supersededBy && opts.supersededBy.length)) throw new Error("transition to " + to + " requires --superseded-by <id>");
  for (const s of opts.supersededBy || []) if (!K.nodes.has(s)) throw new Error("superseding record " + s + " does not exist");
  const entry = { at: opts.now || new Date().toISOString(), change: "lifecycle", from, to, by: opts.by || "unknown" };
  if (opts.approvedBy) entry.approvedBy = opts.approvedBy;
  if (opts.evidence) entry.evidence = opts.evidence;
  if (opts.dryRun) return { id, from, to, entry, dryRun: true };
  saveKind(K.root, n.kind, recs => {
    const r = recs.find(x => x.id === id);
    r.lifecycle = to;
    if (opts.supersededBy) r.supersededBy = U.uniqSorted((r.supersededBy || []).concat(opts.supersededBy));
    if (n.kind !== "source") r.history = (r.history || []).concat(entry);
  });
  return { id, from, to, entry };
}

/* ---------- consolidation ---------- */
function itemsOf(rec) {
  const items = [];
  if (rec.statement) items.push({ item: "statement", text: rec.statement });
  (rec.acceptance || []).forEach((a, i) => items.push({ item: "acceptance[" + i + "]", text: a }));
  if (rec.rationale) items.push({ item: "rationale", text: rec.rationale });
  (rec.sources || []).forEach((s, i) => items.push({ item: "sources[" + i + "]", ref: s.ref + (s.segment ? "#" + s.segment : "") }));
  return items;
}
function destinationHas(dest, it) {
  if (it.ref) return (dest.sources || []).some(s => s.ref + (s.segment ? "#" + s.segment : "") === it.ref);
  const hay = [dest.statement, dest.rationale].concat(dest.acceptance || []).join("\n").toLowerCase().replace(/\s+/g, " ");
  return hay.includes(it.text.toLowerCase().replace(/\s+/g, " "));
}
function checkPlan(K, plan) {
  const errors = [];
  const dest = K.nodes.get(plan.destination);
  if (!dest) errors.push("destination " + plan.destination + " does not exist");
  for (const sid of plan.sources || []) {
    const s = K.nodes.get(sid);
    if (!s) { errors.push("source record " + sid + " does not exist"); continue; }
    if (dest && s.kind !== dest.kind) errors.push(sid + " is a " + s.kind + ", destination is a " + dest.kind + " — consolidate like with like");
    for (const it of itemsOf(s.rec)) {
      const m = (plan.mapping || []).find(x => x.from === sid && x.item === it.item);
      if (!m) { errors.push("unmapped unique item " + sid + "." + it.item + " — every item must be mapped or retained"); continue; }
      if (m.to === "retain") { if (!m.reason) errors.push(sid + "." + it.item + " retained without a reason"); continue; }
      if (m.to !== plan.destination) { errors.push(sid + "." + it.item + " mapped to " + m.to + ", not the plan destination"); continue; }
      if (dest && !destinationHas(dest.rec, it)) errors.push(sid + "." + it.item + " is mapped to " + plan.destination + " but the destination does not contain it — knowledge would be lost");
    }
    const retained = (plan.mapping || []).some(x => x.from === sid && x.to === "retain");
    if (retained) errors.push(sid + " has retained items, so it cannot be superseded as a whole — split the retained items into their own record first");
  }
  return errors;
}
function consolidate(K, plan, opts) {
  opts = opts || {};
  const errors = checkPlan(K, plan);
  if (errors.length) return { ok: false, applied: false, errors };
  if (!opts.approvedBy) return { ok: true, applied: false, errors: [], note: "plan is complete and safe; applying it supersedes records and needs --approve <name>" };
  const applied = [];
  for (const sid of plan.sources) {
    const n = K.nodes.get(sid);
    let to = "superseded";
    if (!K.lifecycle.transitions.some(t => t.from === n.rec.lifecycle && t.to === to)) {
      transition(K, sid, "consolidation-candidate", { by: opts.by, now: opts.now });
      n.rec.lifecycle = "consolidation-candidate";
    }
    applied.push(transition(K, sid, to, { by: opts.by, approvedBy: opts.approvedBy, supersededBy: [plan.destination], evidence: "consolidation plan " + (plan.id || "unnamed"), now: opts.now }));
  }
  return { ok: true, applied: true, transitions: applied };
}

module.exports = { scan, knowledge, proposals, transition, consolidate, checkPlan, listFiles };
