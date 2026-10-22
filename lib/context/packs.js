/* Context continuity · linked context packs.
   --------------------------------------------------------------------------
   A pack is a compact, task-relevant VIEW of canonical knowledge — never a
   replacement for it. Every pack:

     · is deterministic: same knowledge + config → same bytes (stable sort, stable
       ids, no wall-clock; its generatedAt is the knowledge snapshot's asOf),
     · records a dependency fingerprint over every input it was built from (the
       hash of each included record, each prerequisite pack, the schemas, the
       generator), so a change to any input makes it detectably STALE,
     · fits a byte budget WITHOUT dropping mandatory knowledge: the mandatory
       block (rules, critical requirements, decisions, open uncertainty,
       verification) is kept whole; everything else is split into linked
       subparts; whatever still cannot fit is listed as excluded, with the reason.

   If the mandatory block alone exceeds the budget the pack is still emitted whole
   and marked mandatory-over-budget, and the assimilation gate refuses it at that
   budget — the budget is never satisfied by silently dropping essential context. */
"use strict";

const fs = require("fs");
const path = require("path");
const U = require("./util");
const G_ = require("./graph");

const PACK_SCHEMA = "ctx-pack/1";
const isOpen = n => n && n.kind === "issue" && n.rec.status === "open";

/* ---------- membership: what a context spec pulls in ---------- */
/* carried: ids already in a prerequisite pack. Expansion does not pull them in again
   (the prerequisite is loaded first, so they are present); explicit includes stay. */
function members(K, G, spec, carried) {
  carried = carried || new Set();
  const inc = spec.rec.include || {};
  const set = new Set();
  for (const k of ["requirements", "decisions", "constraints", "artifacts", "issues", "sources"]) for (const id of inc[k] || []) set.add(id);
  if (inc.tags && inc.tags.length) {
    for (const n of K.nodes.values()) {
      if (n.rec.imported || ["task", "context", "source"].includes(n.kind)) continue;
      if ((n.rec.tags || []).some(t => inc.tags.includes(t))) set.add(n.id);
    }
  }
  /* expansion — knowledge a member cannot be read correctly without */
  let grew = true;
  while (grew) {
    grew = false;
    for (const id of [...set]) {
      const n = K.nodes.get(id);
      if (!n) continue;
      const add = x => { if (!set.has(x) && !carried.has(x) && K.nodes.has(x)) { set.add(x); grew = true; } };
      if (n.kind === "requirement") {
        for (const d of n.rec.dependsOn || []) add(d);
        for (const e of G.in(id)) if (e.rel === "constrains" && K.nodes.get(e.from).kind === "decision") add(e.from);
      }
      for (const e of G.in(id)) if ((e.rel === "blocks") && isOpen(K.nodes.get(e.from))) add(e.from);
      for (const n2 of K.of("issue")) if (isOpen(n2) && (n2.rec.affects || []).includes(id)) add(n2.id);
    }
  }
  /* superseded / retired records never enter a pack as authority */
  const out = { requirement: [], decision: [], constraint: [], artifact: [], issue: [], source: [], missing: [], inactive: [] };
  for (const id of [...set].sort()) {
    const n = K.nodes.get(id);
    if (!n) { out.missing.push(id); continue; }
    if (n.kind !== "source" && !K.active(id) && !(n.kind === "issue")) { out.inactive.push(id); continue; }
    if (out[n.kind]) out[n.kind].push(n);
  }
  return out;
}

function globalRules(K) {
  return K.of("constraint").filter(n => K.active(n.id) && n.rec.critical && n.rec.scope === "global");
}

/* mandatory = may never leave part 1 and never be excluded: every rule that is
   critical or protects security/privacy, every critical/high requirement, every
   decision, and EVERY open issue (unresolved uncertainty is never optional) */
function isMandatory(n) {
  if (n.kind === "constraint") return !!n.rec.critical || ["security", "privacy", "constitutional"].includes(n.rec.class);
  if (n.kind === "requirement") return n.rec.priority === "critical" || n.rec.priority === "high";
  if (n.kind === "decision") return true;
  if (n.kind === "issue") return n.rec.status === "open";
  return false;
}
/* …and whatever a mandatory item depends on is mandatory too (a dependency of a
   rule cannot be optional reading). Fixed point over depends-on within the pack. */
function mandatorySet(K, G, nodes) {
  const inPack = new Map(nodes.map(n => [n.id, n]));
  const set = new Set(nodes.filter(isMandatory).map(n => n.id));
  let grew = true;
  while (grew) {
    grew = false;
    for (const id of [...set]) for (const e of G.out(id)) if (e.rel === "depends-on" && inPack.has(e.to) && !set.has(e.to)) { set.add(e.to); grew = true; }
  }
  return set;
}

/* ---------- topological order of packs (prerequisites first, then id) ---------- */
function packOrder(K) {
  const specs = K.of("context").filter(n => K.active(n.id));
  const ids = new Set(specs.map(s => s.id));
  const done = new Set(), order = [];
  const visit = (id, stack) => {
    if (done.has(id) || stack.has(id) || !ids.has(id)) return;
    stack.add(id);
    for (const p of (K.nodes.get(id).rec.prerequisites || []).slice().sort()) visit(p, stack);
    stack.delete(id); done.add(id); order.push(id);
  };
  const boot = specs.filter(s => s.rec.bootstrap).map(s => s.id);
  for (const id of boot.concat(specs.map(s => s.id))) visit(id, new Set());
  return order;
}

/* ---------- rendering helpers: every item is an atomic block ---------- */
const srcList = refs => (refs || []).map(r => r.ref + (r.segment ? "#" + r.segment : "") + (r.locator ? " (" + r.locator + ")" : "")).join("; ") || "—";
const list = xs => (xs && xs.length) ? xs.join(", ") : "—";

function itemBlock(n) {
  const r = n.rec;
  switch (n.kind) {
    case "constraint": return "- **" + n.id + " — " + r.title + "** (" + r.class + (r.critical ? ", critical" : "") + "). " + r.statement + "\n  Owner: `" + r.owner + "` · Sources: " + srcList(r.sources) + "\n";
    case "requirement": return [
      "### " + n.id + " — " + r.title,
      "- Statement: " + r.statement,
      "- Type: " + r.type + " · Priority: " + r.priority + " · Lifecycle: " + r.lifecycle + " · Owner: `" + r.owner + "`",
      "- Acceptance: " + r.acceptance.map((a, i) => "(" + (i + 1) + ") " + a).join(" "),
      "- Verification: " + r.verification.method + ((r.verification.commands || []).length ? " — `" + r.verification.commands.join("` · `") + "`" : "") + (r.verifiedBy && r.verifiedBy.length ? " · verified by " + list(r.verifiedBy) : ""),
      "- Depends on: " + list(r.dependsOn) + " · Implemented by: " + list(r.implementedBy) + (r.conflictsWith && r.conflictsWith.length ? " · **Conflicts with: " + list(r.conflictsWith) + "**" : ""),
      "- Sources: " + srcList(r.sources),
      ""
    ].join("\n") + "\n";
    case "decision": return [
      "### " + n.id + " — " + r.statement,
      "- Status: **" + r.status + "**" + (r.provenance === "newly-proposed" ? " (newly proposed — no historical approval exists)" : "") + " · Authority: " + (r.authority || "unrecorded") + " · Decided: " + (r.decidedAt || "unrecorded"),
      "- Context: " + r.context,
      "- Selected: " + r.selected,
      "- Rationale: " + r.rationale,
      (r.rejected || []).length ? "- Rejected: " + r.rejected.map(x => x.option + " (" + x.reason + ")").join("; ") : "- Rejected alternatives: none evidenced",
      "- Affects: " + list(r.affects) + " · Sources: " + srcList(r.sources),
      ""
    ].join("\n") + "\n";
    case "issue": return "- **" + n.id + "** [" + r.kind + ", " + r.severity + ", " + r.status + "] " + r.title + ". " + r.statement + (r.evidenceNeeded ? " _Evidence needed:_ " + r.evidenceNeeded : "") + (r.blocks && r.blocks.length ? " **Blocks:** " + list(r.blocks) : "") + "\n";
    case "artifact": return "- **" + n.id + "** " + r.title + " — `" + (r.path || r.locator || "no locator") + "` · " + r.type + " · authority " + r.authority + " · " + r.lifecycle + (n.fileHash === "MISSING" ? " · **FILE MISSING**" : "") + "\n";
    case "source": return "- **" + n.id + "** " + r.title + " — " + (r.locator || r.origin) + " · " + r.category + " · preservation **" + r.preservation + "** · sensitivity " + r.sensitivity + (r.storage.sha256 ? " · sha256 `" + r.storage.sha256.slice(0, 16) + "…`" : "") + "\n";
  }
  return "- " + n.id + "\n";
}

function depFingerprint(K, spec, mem, prereqFps, budget) {
  const ids = [];
  for (const k of ["requirement", "decision", "constraint", "artifact", "issue", "source"]) for (const n of mem[k]) ids.push(n.id);
  for (const n of globalRules(K)) ids.push(n.id);
  /* state facts are inputs too, named "fact:<id>" so an invalidation report can say which */
  const facts = ((K.state && K.state.facts) || []).filter(f => (f.about || []).some(a => ids.includes(a) || a === spec.id)).map(f => ["fact:" + f.id, U.hashOf(f)]);
  const inputs = U.uniqSorted(ids).map(id => [id, K.nodes.get(id).hash]).concat(facts.sort((a, b) => a[0] < b[0] ? -1 : 1));
  return {
    inputs,
    fingerprint: U.hashOf({ spec: spec.rec, inputs, prereqFps, schemas: K.schemaHashes, generator: U.GENERATOR_VERSION, budget, missing: mem.missing, inactive: mem.inactive, asOf: K.state && K.state.asOf })
  };
}

/* render one pack at a budget → { json, parts:[{id,file,body}] } */
function renderPack(K, G, id, budget, prereqFps, carried) {
  const spec = K.nodes.get(id);
  const r = spec.rec;
  budget = budget || r.budgetBytes || K.config.budgets.defaultPackBytes;
  const mem = members(K, G, spec, carried);
  const dep = depFingerprint(K, spec, mem, prereqFps, budget);
  const asOf = (K.state && K.state.asOf) || "unknown";
  const rules = globalRules(K);
  const facts = ((K.state && K.state.facts) || []).filter(f => (f.about || []).some(a => a === id || mem.requirement.concat(mem.decision, mem.artifact, mem.issue).some(n => n.id === a)));

  const mand = [], rest = [];
  const knowledge = mem.requirement.concat(mem.decision, mem.constraint, mem.issue);
  const mset = mandatorySet(K, G, knowledge);
  for (const n of knowledge) (mset.has(n.id) ? mand : rest).push(n);
  for (const n of mem.artifact.concat(mem.source)) rest.push(n);

  const header = (partNo, total) => [
    "# " + id + " — " + r.title + (total > 1 ? " (part " + partNo + " of " + total + ")" : ""),
    "",
    "> Generated by `" + U.GENERATOR_VERSION + "` from `PROJECT-CONTEXT/knowledge/` — do not edit; change the knowledge and run `npm run context:build`.",
    "> Knowledge snapshot: " + asOf + " · Dependency fingerprint: `" + dep.fingerprint.slice(0, 16) + "` · Schema `" + PACK_SCHEMA + "`",
    ""
  ].join("\n") + "\n";

  const prereqLines = (r.prerequisites || []).map(p => "- " + p + " → `PROJECT-CONTEXT/contexts/" + p + ".md` (fingerprint `" + String(prereqFps[p] || "MISSING").slice(0, 16) + "`)");
  const sections = [];
  sections.push("## Use and scope\n\n" + r.use + "\n\n**In scope:** " + r.scope.join("; ") + "\n\n**Excluded:** " + ((r.exclusions || []).join("; ") || "nothing declared") + "\n");
  sections.push("## Reading order\n\n1. Prerequisites below (load each pack's part 1 first).\n2. Mandatory rules, then mandatory requirements and decisions in this pack.\n3. Open uncertainty — treat every item there as unsettled.\n4. Supplementary parts (if any) and source evidence only as needed.\n5. Canonical owners (the `Owner:` paths) when a statement here is not enough — they win over this pack.\n");
  sections.push("## Prerequisites and navigation\n\n" + (prereqLines.length ? prereqLines.join("\n") : "- none (this is a root pack)") +
    "\n- Previous: " + (r.previous || "—") + " · Next: " + (r.next || "—") + " · Related: " + list(r.related) + "\n" +
    "- Order is a navigation aid; the dependency truth is `npm run context:query -- prerequisites " + id + "`.\n");
  /* the bootstrap pack carries the rules in full (owner + sources); every other pack
     repeats them compactly — present in every pack, never more bytes than needed */
  const bootCarried = (r.prerequisites || []).some(p => K.nodes.get(p) && (K.nodes.get(p).rec.bootstrap || G_.closure(G, p, ["depends-on"]).some(q => K.nodes.get(q) && K.nodes.get(q).rec.bootstrap)));
  sections.push("## Mandatory rules (global, critical)\n\n" + (r.bootstrap ? rules.map(itemBlock).join("") :
    bootCarried ? rules.map(n => "- **" + n.id + "** " + n.rec.title + "\n").join("") + "\nFull statements, owners and sources: prerequisite `CTX-BOOTSTRAP` (loaded first).\n" :
    rules.map(n => "- **" + n.id + "** " + n.rec.title + ": " + n.rec.statement + "\n").join("") + "\nOwners and sources: `CTX-BOOTSTRAP` / `01-PROJECT-CONSTITUTION.md`.\n"));
  const mReq = mand.filter(n => n.kind === "requirement"), mDec = mand.filter(n => n.kind === "decision"), mCon = mand.filter(n => n.kind === "constraint" && !rules.includes(n)), mIss = mand.filter(n => n.kind === "issue");
  if (mCon.length) sections.push("## Scoped critical constraints\n\n" + mCon.map(itemBlock).join(""));
  if (mReq.length) sections.push("## Mandatory requirements\n\n" + mReq.map(itemBlock).join(""));
  if (mDec.length) sections.push("## Decisions in force\n\n" + mDec.map(itemBlock).join(""));
  sections.push("## Open uncertainty, conflicts and blockers\n\n" + (mIss.length ? mIss.map(itemBlock).join("") : "- none recorded for this scope\n") +
    (mem.missing.length ? "- **MISSING references (not loadable):** " + mem.missing.join(", ") + "\n" : "") +
    (mem.inactive.length ? "- Superseded/retired records referenced by this spec were withheld as authority: " + mem.inactive.join(", ") + "\n" : ""));
  sections.push("## Current state (facts)\n\n" + (facts.length ? facts.map(f => "- [" + f.status + "] " + f.statement + (f.evidence ? " — evidence: " + f.evidence : "")).join("\n") + "\n" : "- no state facts recorded for this scope; see `02-CURRENT-STATE.md`\n"));
  sections.push("## Verification\n\n" + ((r.verification || []).length ? r.verification.map(c => "- `" + c + "`").join("\n") : "- `npm run context:verify`") + "\n");
  const mandatoryBody = sections.join("\n");

  const recovery = "## Recovering more detail\n\nThis pack is a view. For any statement: follow its `Owner:` path (canonical), then its `Sources:` ids in `PROJECT-CONTEXT/09-ARCHIVE-MANIFEST.md` (`npm run context:restore-check` restores the archived originals to a temp dir). Query the graph instead of loading it: `npm run context:query -- affected-by <ID>` / `prerequisites <ID>` / `tests-for <ID>`.\n";

  const restBlocks = rest.map(n => ({ n, body: itemBlock(n), group: n.kind }));
  const groupTitle = { requirement: "Further requirements", issue: "Further issues (lower severity)", constraint: "Further constraints", artifact: "Artifacts", source: "Source evidence" };
  const renderRest = blocks => {
    let out = "", g = null;
    for (const b of blocks) { if (b.group !== g) { g = b.group; out += "\n## " + groupTitle[g] + "\n\n"; } out += b.body; }
    return out;
  };

  /* single part if everything fits */
  const exclusionNote = ex => "## Exclusions\n\n" + (ex.length ? ex.map(e => "- " + e.id + ": " + e.reason).join("\n") + "\n" : "- none — every member of this pack is present in full\n");
  const one = header(1, 1) + mandatoryBody + renderRest(restBlocks) + "\n" + recovery + "\n" + exclusionNote([]);
  let parts, status = "ok", excluded = [];
  if (U.byteLen(one) <= budget) {
    parts = [{ id, body: one }];
  } else {
    /* split: part 1 = mandatory block; the rest packed greedily, order preserved */
    const restParts = [];
    let cur = [];
    const partOverhead = 600;
    const fits = blocks => U.byteLen(renderRest(blocks)) + partOverhead <= budget;
    for (const b of restBlocks) {
      if (U.byteLen(b.body) + partOverhead > budget) { excluded.push({ id: b.n.id, kind: b.n.kind, reason: "a single block of " + U.byteLen(b.body) + " bytes exceeds the " + budget + "-byte budget; read it at its owner (" + (b.n.rec.owner || b.n.rec.path || b.n.rec.locator || "knowledge/" + b.n.kind + "s.json") + ")" }); continue; }
      if (cur.length && !fits(cur.concat(b))) { restParts.push(cur); cur = []; }
      cur.push(b);
    }
    if (cur.length) restParts.push(cur);
    const total = 1 + restParts.length;
    const partId = i => i === 0 ? id : id + "~" + (i + 1);
    const contents = "## Parts\n\n" + Array.from({ length: total }, (_, i) => "- " + partId(i) + " → `PROJECT-CONTEXT/contexts/" + partId(i) + ".md`" + (i === 0 ? " (mandatory — this part)" : " (supplementary)")).join("\n") + "\n\n";
    const p1 = header(1, total) + contents + mandatoryBody + "\n" + recovery + "\n" + exclusionNote(excluded);
    parts = [{ id, body: p1 }];
    restParts.forEach((blocks, i) => {
      parts.push({ id: partId(i + 1), body: header(i + 2, total) + "> Supplementary part. Mandatory knowledge is in part 1 (`" + id + "`); load it first.\n" + renderRest(blocks) + "\n" });
    });
    if (U.byteLen(p1) > budget) status = "mandatory-over-budget";
    else if (excluded.length) status = "incomplete";
  }
  for (const p of parts) p.file = "contexts/" + p.id + ".md";
  const secretHits = parts.flatMap(p => U.findSecrets(p.body).map(h => p.id + ":" + h));

  const json = {
    schema: PACK_SCHEMA,
    id, title: r.title, generator: U.GENERATOR_VERSION, generatedAt: asOf,
    budgetBytes: budget, status,
    freshness: "fresh-at-build",
    parts: parts.map(p => ({ id: p.id, file: p.file, bytes: U.byteLen(p.body), estimatedTokens: U.estimateTokens(U.byteLen(p.body)), sha256: U.sha256(p.body) })),
    mandatory: mand.map(n => n.id).concat(rules.map(n => n.id)).sort(),
    members: {
      requirements: mem.requirement.map(n => n.id), decisions: mem.decision.map(n => n.id), constraints: mem.constraint.map(n => n.id).concat(rules.map(n => n.id)).filter((v, i, a) => a.indexOf(v) === i).sort(),
      artifacts: mem.artifact.map(n => n.id), issues: mem.issue.map(n => n.id), sources: mem.source.map(n => n.id)
    },
    sourceFingerprints: mem.source.map(n => ({ id: n.id, sha256: n.rec.storage.sha256 || null })),
    prerequisites: (r.prerequisites || []).map(p => ({ id: p, fingerprint: prereqFps[p] || null })),
    excluded, missing: mem.missing, withheld: mem.inactive, secretFindings: secretHits,
    inputs: dep.inputs,
    depFingerprint: dep.fingerprint
  };
  json.contentFingerprint = U.hashOf(json.parts.map(p => p.sha256));
  return { json, parts };
}

/* build every active pack in prerequisite order (in memory) */
function renderAll(K, G, opts) {
  opts = opts || {};
  const order = packOrder(K);
  const fps = {}, out = [], carriedBy = {};
  for (const id of order) {
    const spec = K.nodes.get(id);
    const prereqFps = {};
    const carried = new Set();
    for (const p of spec.rec.prerequisites || []) {
      prereqFps[p] = fps[p] || null;
      for (const x of carriedBy[p] || []) carried.add(x);
    }
    const budget = opts.budget || spec.rec.budgetBytes || K.config.budgets.defaultPackBytes;
    const rp = renderPack(K, G, id, budget, prereqFps, carried);
    fps[id] = rp.json.depFingerprint;
    const mine = new Set(carried);
    for (const k of Object.keys(rp.json.members)) for (const x of rp.json.members[k]) mine.add(x);
    carriedBy[id] = mine;
    out.push(rp);
  }
  return { order, packs: out };
}

function indexJSON(K, rendered) {
  return {
    schema: "ctx-pack-index/1",
    generator: U.GENERATOR_VERSION,
    generatedAt: (K.state && K.state.asOf) || "unknown",
    readingOrder: rendered.order,
    packs: rendered.packs.map(p => ({ id: p.json.id, title: p.json.title, status: p.json.status, depFingerprint: p.json.depFingerprint, contentFingerprint: p.json.contentFingerprint, parts: p.json.parts.map(x => ({ id: x.id, bytes: x.bytes })) }))
  };
}

/* freshness: compare what is ON DISK with what the knowledge says it should be */
function status(K, G, rendered) {
  rendered = rendered || renderAll(K, G);
  const res = [];
  for (const p of rendered.packs) {
    const abs = path.join(K.dirs.contexts, p.json.id + ".json");
    let disk = null;
    try { disk = U.readJSON(abs); } catch (e) { }
    if (!disk) { res.push({ id: p.json.id, fresh: false, reason: "missing", detail: "no generated pack on disk" }); continue; }
    if (disk.depFingerprint !== p.json.depFingerprint) {
      const before = new Map(disk.inputs || []), changed = [];
      for (const [id, h] of p.json.inputs) if (before.get(id) !== h) changed.push(id);
      for (const id of before.keys()) if (!p.json.inputs.some(x => x[0] === id)) changed.push(id);
      res.push({ id: p.json.id, fresh: false, reason: "stale", detail: changed.length ? "changed inputs: " + U.uniqSorted(changed).join(", ") : "spec, schema, prerequisite or generator changed", changed: U.uniqSorted(changed), fingerprint: disk.depFingerprint });
      continue;
    }
    let corrupt = null;
    for (const part of disk.parts || []) {
      let body = null;
      try { body = fs.readFileSync(path.join(K.dirs.base, part.file)); } catch (e) { corrupt = part.file + " missing"; break; }
      if (U.sha256(body) !== part.sha256) { corrupt = part.file + " does not match its recorded sha256"; break; }
    }
    if (corrupt) { res.push({ id: p.json.id, fresh: false, reason: "corrupted", detail: corrupt, fingerprint: disk.depFingerprint }); continue; }
    res.push({ id: p.json.id, fresh: true, fingerprint: disk.depFingerprint, status: disk.status });
  }
  /* packs on disk whose spec no longer exists */
  let files = [];
  try { files = fs.readdirSync(K.dirs.contexts).filter(f => f.endsWith(".json") && f !== "index.json"); } catch (e) { }
  for (const f of files) { const id = f.replace(/\.json$/, ""); if (!rendered.packs.some(p => p.json.id === id)) res.push({ id, fresh: false, reason: "orphaned", detail: "generated pack has no active context spec" }); }
  return res;
}

/* ---------- task packs: the one file a task's agent starts from ---------- */
function renderTaskPack(K, G, taskId, rendered, handoffs) {
  const t = K.nodes.get(taskId);
  const r = t.rec;
  const ctxs = new Set();
  for (const c of r.contexts || []) { ctxs.add(c); for (const p of G_.closure(G, c, ["depends-on"])) if ((K.nodes.get(p) || {}).kind === "context") ctxs.add(p); }
  const order = rendered.order.filter(id => ctxs.has(id));
  const byId = new Map(rendered.packs.map(p => [p.json.id, p.json]));
  const hos = (handoffs || []).filter(h => h.task === taskId);
  const last = hos[hos.length - 1];
  const blockers = G.in(taskId).filter(e => e.rel === "blocks").map(e => K.nodes.get(e.from)).filter(isOpen);
  const unapproved = (r.decisions || []).filter(d => (K.nodes.get(d) || { rec: {} }).rec.status === "proposed");
  const one = (id) => { const n = K.nodes.get(id); if (!n) return "- " + id + " — **MISSING**"; return "- " + id + " — " + (n.rec.title || n.rec.statement) + (n.rec.status ? " [" + n.rec.status + "]" : "") + (n.rec.priority ? " [" + n.rec.priority + "]" : ""); };
  const body = [
    "# " + taskId + " — " + r.title,
    "",
    "> Task pack generated by `" + U.GENERATOR_VERSION + "` — do not edit. Knowledge snapshot " + ((K.state && K.state.asOf) || "unknown") + ".",
    "> Before changing anything run: `npm run context:assimilate -- " + taskId + " --agent <you> --write`",
    "",
    "## Objective", "", r.objective, "",
    "## State", "", "- **" + r.state + "** · authority: " + r.authority,
    "- Next action: **" + r.nextAction + "**",
    last ? "- Latest handoff: `PROJECT-CONTEXT/handoffs/" + last.id + ".json` (" + last.createdAt + ", by " + last.agent + ")" : "- No handoff recorded yet.",
    "",
    "## Scope", "", r.scope.map(s => "- " + s).join("\n"), "",
    "## Must not change / excluded", "", ((r.exclusions || []).map(s => "- " + s).join("\n") || "- nothing declared"), "",
    "## Acceptance criteria", "", r.acceptance.map((a, i) => (i + 1) + ". " + a).join("\n"), "",
    "## Verification commands", "", r.verification.map(c => "- `" + c + "`").join("\n"), "",
    "## Load these packs, in order", "", order.map((id, i) => (i + 1) + ". `PROJECT-CONTEXT/contexts/" + id + ".md` — " + byId.get(id).title + " (" + byId.get(id).parts.map(p => p.bytes + " B").join(" + ") + ")").join("\n") || "- none", "",
    "## Requirements", "", (r.requirements || []).map(one).join("\n") || "- none", "",
    "## Decisions", "", (r.decisions || []).map(one).join("\n") || "- none", "",
    unapproved.length ? "**Unapproved decisions (proposed, not owner-approved):** " + unapproved.join(", ") + "\n" : "",
    "## Blockers", "", blockers.length ? blockers.map(n => itemBlock(n)).join("") : "- none open", "",
    "## Depends on", "", (r.dependsOn || []).map(one).join("\n") || "- none", ""
  ].join("\n");
  return { id: taskId, file: "task-packs/" + taskId + ".md", body };
}

module.exports = { renderAll, renderPack, status, indexJSON, renderTaskPack, members, packOrder, isMandatory, mandatorySet, globalRules, PACK_SCHEMA };
