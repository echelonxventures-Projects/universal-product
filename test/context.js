/* Context continuity · the proof.
   --------------------------------------------------------------------------
   Proves the continuity system end to end. The live repository is only ever READ;
   every mutation happens in a disposable copy (tracked + unignored files + .git).

     §A  the committed knowledge — valid, deterministic, bounded, traceable
     §B  invalidation — a change stales exactly its dependants; incremental = full
     §C  integrity failures — corrupted / missing / stale packs, archive tamper,
         broken refs, cycles, untracked conflicts, historical-as-authority
     §D  hygiene safety — lifecycle approval, consolidation never loses an item
     §E  protocol — receipts, budgets (small agents), handoffs that refuse
         unevidenced claims
     §F  archive — private import outside git, write-once, restore isolation
     §G  fresh agent — no conversation history: from AGENTS.md alone, recover the
         task, rules, decisions, blockers, next action and verification, then hand off

   Fast (no server, no port, no DB). */
"use strict";

const fs = require("fs");
const os = require("os");
const path = require("path");
const cp = require("child_process");

const ROOT = path.resolve(__dirname, "..");
const ctx = require(path.join(ROOT, "lib", "context"));
const U = require(path.join(ROOT, "lib", "context", "util.js"));
const S = require(path.join(ROOT, "lib", "context", "store.js"));
const Gr = require(path.join(ROOT, "lib", "context", "graph.js"));
const P = require(path.join(ROOT, "lib", "context", "packs.js"));
const A = require(path.join(ROOT, "lib", "context", "archive.js"));
const C = require(path.join(ROOT, "lib", "context", "coverage.js"));
const H = require(path.join(ROOT, "lib", "context", "hygiene.js"));
const Pr = require(path.join(ROOT, "lib", "context", "protocol.js"));

let pass = 0, fail = 0;
const ok = (cond, msg, detail) => { if (cond) { pass++; } else { fail++; console.log("  ✗ " + msg + (detail ? "\n      " + String(detail).slice(0, 600) : "")); } };
const section = t => console.log("\n" + t);
const TMP = fs.mkdtempSync(path.join(os.tmpdir(), "ctx-test-"));
process.on("exit", () => { try { fs.rmSync(TMP, { recursive: true, force: true }); } catch (e) { } });

/* ---------- sandboxes: a byte copy of the repository, git included ---------- */
let base = null;
function sandbox(name) {
  if (!base) {
    base = path.join(TMP, "base");
    const files = U.gitText(ROOT, ["ls-files", "-co", "--exclude-standard", "-z"]).split("\0").filter(Boolean);
    for (const f of files) {
      const src = path.join(ROOT, f);
      if (!fs.existsSync(src) || !fs.statSync(src).isFile()) continue;
      fs.mkdirSync(path.dirname(path.join(base, f)), { recursive: true });
      fs.copyFileSync(src, path.join(base, f));
    }
    fs.cpSync(path.join(ROOT, ".git"), path.join(base, ".git"), { recursive: true });
  }
  const dir = path.join(TMP, name);
  fs.cpSync(base, dir, { recursive: true });
  return dir;
}
const kpath = (root, kind) => path.join(root, "PROJECT-CONTEXT", "knowledge", S.KNOWLEDGE_FILES[kind]);
function editKind(root, kind, fn) { const p = kpath(root, kind); const d = JSON.parse(fs.readFileSync(p, "utf8")); fn(d.records, d); fs.writeFileSync(p, JSON.stringify(d, null, 2) + "\n"); }
const statusOf = root => { const { K, G } = ctx.open(root); return new Map(P.status(K, G).map(s => [s.id, s])); };
const codes = r => r.errors.map(e => e.code);
function cli(root, args, env) {
  const r = cp.spawnSync(process.execPath, [path.join(root, "scripts", "context.js")].concat(args), { cwd: root, encoding: "utf8", env: Object.assign({}, process.env, env || {}), maxBuffer: 64 << 20 });
  return { code: r.status, out: r.stdout, err: r.stderr };
}
function generatedSnapshot(root) {
  const { K } = ctx.open(root);
  const out = {};
  for (const d of ["contexts", "task-packs"]) for (const f of fs.readdirSync(path.join(K.dirs.base, d))) out[d + "/" + f] = fs.readFileSync(path.join(K.dirs.base, d, f), "utf8");
  for (const v of K.config.generated.views) out[v] = fs.readFileSync(path.join(K.dirs.base, v), "utf8");
  return out;
}

/* ===================================================================== §A */
section("§A the committed knowledge");
{
  const v = ctx.verify(ROOT);
  ok(v.ok, "context:verify passes on the repository", codes(v).join(", ") + " " + v.errors.slice(0, 3).map(e => e.message).join(" | "));
  const { K, G } = ctx.open(ROOT);
  ok(K.diags.filter(d => d.level === "error").length === 0, "knowledge loads with no schema/id/lifecycle errors");
  ok(G.diags.length === 0, "graph has no broken references, kind violations or cycles", G.diags.map(d => d.message).join(" | "));

  /* determinism: same knowledge → same bytes, and = what is on disk */
  const r1 = ctx.renderOutputs(K, G).out, r2 = ctx.renderOutputs(S.load(ROOT), Gr.build(S.load(ROOT))).out;
  ok(JSON.stringify(r1) === JSON.stringify(r2), "two renders over unchanged knowledge are byte-identical");
  const disk = generatedSnapshot(ROOT);
  ok(Object.keys(r1).every(f => disk[f] === r1[f]) && Object.keys(disk).every(f => f in r1), "on-disk generated files equal a fresh render (no drift)");
  ok(!Object.values(r1).some(b => /\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(b)), "generated files carry no wall-clock timestamps");

  /* Knowledge Once: UCOS artifacts imported, not copied; generated output never an input */
  const M = U.readJSON(path.join(ROOT, "_registry", "manifest.json"));
  const imported = K.of("artifact").filter(n => n.rec.imported);
  ok(imported.length === M.artifacts.length, "all " + M.artifacts.length + " UCOS artifacts are imported read-only from _registry/manifest.json", imported.length);
  const knowledgeText = Object.values(S.KNOWLEDGE_FILES).map(f => fs.readFileSync(path.join(K.dirs.knowledge, f), "utf8")).join("");
  ok(!/"id":\s*"UCOS-[A-Z]+-\d+"/.test(knowledgeText), "no UCOS artifact is re-declared in PROJECT-CONTEXT/knowledge");
  ok(K.of("artifact").every(n => !n.rec.path || !/^PROJECT-CONTEXT\/(contexts|task-packs|\d\d-)/.test(n.rec.path)), "no generated file is registered as an input artifact");
  ok(K.of("requirement").concat(K.of("constraint"), K.of("artifact")).filter(n => !n.rec.imported).every(n => K.nodes.has(n.rec.owner) || U.exists(ROOT, n.rec.owner)), "every requirement, constraint and artifact owner resolves");

  /* packs: bounded, mandatory knowledge in part 1, estimates labelled */
  const rendered = P.renderAll(K, G);
  for (const p of rendered.packs) {
    const j = p.json;
    ok(j.status === "ok", j.id + " fits its budget with nothing excluded (status " + j.status + ")");
    ok(j.parts.every(x => x.bytes <= j.budgetBytes), j.id + " every part ≤ " + j.budgetBytes + " B");
    const part1 = p.parts[0].body;
    ok(j.mandatory.every(id => part1.includes(id)), j.id + " carries every mandatory id in part 1");
    ok(j.secretFindings.length === 0, j.id + " has no credential patterns");
  }
  ok(U.estimateTokens(3000) === 1000 && /estimate/i.test(fs.readFileSync(path.join(ROOT, "lib/context/util.js"), "utf8")), "token figures are a labelled 3 B/token estimate");

  /* queries */
  const Q = Gr.queries(K, G, { packStatus: P.status(K, G), coverage: C.segmentAccounting(K) });
  for (const q of Object.keys(Q)) { let threw = null; try { Q[q]("TASK-CTX-0001"); } catch (e) { threw = e; } ok(!threw, "query " + q + " runs", threw && threw.message); }
  ok(Q["tests-for"]("REQ-CTX-PACKS").some(x => x.id === "ART-TEST-CONTEXT"), "tests-for REQ-CTX-PACKS finds test/context.js");
  ok(Q["prerequisites"]("CTX-CONTINUITY-SYSTEM").some(x => x.id === "CTX-BOOTSTRAP"), "prerequisites are transitive (CTX-CONTINUITY-SYSTEM → … → CTX-BOOTSTRAP)");
  ok(Q["affected-by"]("SRC-REPOSITORY-INDEX").some(x => x.id === "CST-KNOWLEDGE-ONCE") && Q["affected-by"]("SRC-REPOSITORY-INDEX").some(x => x.kind === "context"), "affected-by a source reaches the constraints derived from it and the packs that include them");
  ok(Q["requirements-lacking-verification"]().length === 0, "every active requirement has a verifying artifact");

  /* coverage formulas */
  const cov = C.compute(K, G, { packStatus: P.status(K, G), handoffs: Pr.loadHandoffs(K) });
  ok(cov.metrics.every(m => typeof m.numerator === "number" && typeof m.denominator === "number" && m.formula.length > 20), "every coverage metric publishes numerator, denominator and formula");
  const inv = cov.metrics.find(m => m.name === "source-inventory-preserved");
  const notPreserved = K.of("source").filter(n => n.rec.preservation !== "preserved").length;
  ok(notPreserved >= 2 && inv.numerator === K.of("source").length - notPreserved, "missing / inaccessible / not-retained sources are never counted as preserved", JSON.stringify(inv));
  ok(cov.metrics.find(m => m.name === "segment-representation").numerator > 0, "represented segments are computed from record citations");

  /* entry points */
  const agents = fs.readFileSync(path.join(ROOT, "AGENTS.md"), "utf8");
  ok(Buffer.byteLength(agents) < 6000 && (agents.match(/^\d+\. \*\*/gm) || []).length === 10, "AGENTS.md is under 6 KB with the ten protocol steps");
  ok(/AGENTS\.md/.test(fs.readFileSync(path.join(ROOT, "CLAUDE.md"), "utf8")) && fs.statSync(path.join(ROOT, "CLAUDE.md")).size < 600, "CLAUDE.md is a thin pointer to AGENTS.md");

  /* secret scan + path safety */
  ok(U.findSecrets("key = '" + ["sk", "live", "abcdefgh12345"].join("_") + "'").length > 0 && U.findSecrets("-----BEGIN RSA " + "PRIVATE KEY-----").length > 0 && U.findSecrets("nothing to see").length === 0, "secret scanner detects credential patterns and passes clean text");
  let t1 = null, t2 = null;
  try { U.safeJoin(ROOT, "../etc/passwd"); } catch (e) { t1 = e; }
  try { U.safeJoin(ROOT, "/etc/passwd"); } catch (e) { t2 = e; }
  ok(t1 && t2, "record paths cannot escape the repository (relative or absolute)");

  /* the gate passes on the committed tree */
  const rc = Pr.assimilate(K, G, "TASK-CTX-0001", { agent: "test" });
  ok(rc.verdict !== "blocked", "assimilation of TASK-CTX-0001 passes on the repository", JSON.stringify(rc.gaps.filter(g => g.severity === "block")));
  ok(rc.gaps.some(g => g.code === "decision-unapproved"), "…and surfaces the unapproved (proposed) decisions as warnings, not as settled");
}

/* ===================================================================== §B */
section("§B invalidation and refresh");
{
  const root = sandbox("inval");
  const before = generatedSnapshot(root);
  editKind(root, "requirement", recs => { recs.find(r => r.id === "REQ-CTX-PACKS").statement += " (amended)"; });
  let st = statusOf(root);
  ok(!st.get("CTX-CONTINUITY-SYSTEM").fresh && st.get("CTX-CONTINUITY-SYSTEM").changed.includes("REQ-CTX-PACKS"), "changing a requirement stales the pack that includes it, naming the changed input", JSON.stringify(st.get("CTX-CONTINUITY-SYSTEM")));
  ok(["CTX-BOOTSTRAP", "CTX-GOVERNANCE", "CTX-PLATFORM-QUALITY", "CTX-CONTINUITY-DESIGN"].every(id => st.get(id).fresh), "…and leaves unrelated packs fresh");
  const v = ctx.verify(root);
  ok(!v.ok && codes(v).includes("pack-stale") && codes(v).includes("generated-drift"), "verify fails on a stale pack and on generated-output drift", codes(v).join(","));
  const { K, G } = ctx.open(root);
  ok(Pr.assimilate(K, G, "TASK-CTX-0001", { agent: "t" }).gaps.some(g => g.code === "pack-stale" && g.severity === "block"), "a stale pack cannot pass the assimilation gate");
  const b = ctx.build(root);
  ok(b.ok && b.written.includes("contexts/CTX-CONTINUITY-SYSTEM.md") && !b.written.includes("contexts/CTX-PLATFORM-QUALITY.md") && !b.written.includes("contexts/CTX-BOOTSTRAP.md"), "incremental build rewrites only the affected outputs", b.written.join(", "));
  ok(ctx.verify(root).ok, "after the rebuild, verify passes again");

  /* incremental == full */
  const full = path.join(TMP, "inval-full"); fs.cpSync(root, full, { recursive: true });
  ctx.build(full, { full: true });
  const a1 = generatedSnapshot(root), a2 = generatedSnapshot(full);
  ok(JSON.stringify(a1) === JSON.stringify(a2), "full rebuild and incremental rebuild agree byte for byte");
  ok(a1["contexts/CTX-PLATFORM-QUALITY.md"] === before["contexts/CTX-PLATFORM-QUALITY.md"], "an untouched pack is byte-identical before and after");

  /* decision change → dependants (through prerequisites) */
  editKind(root, "decision", recs => { recs.find(r => r.id === "DEC-CTX-BYTE-BUDGETS").rationale += " Reviewed."; });
  st = statusOf(root);
  ok(!st.get("CTX-CONTINUITY-DESIGN").fresh && !st.get("CTX-CONTINUITY-SYSTEM").fresh, "changing a decision stales its pack and the packs that depend on it");
  ok(st.get("CTX-BOOTSTRAP").fresh && st.get("CTX-EVIDENCE-ARCHIVE").fresh && st.get("CTX-PLATFORM-QUALITY").fresh, "…but not packs that neither include nor depend on it");
  ctx.build(root);

  /* artifact file change → packs including that artifact */
  fs.appendFileSync(path.join(root, "AGENTS.md"), "\n");
  st = statusOf(root);
  ok(!st.get("CTX-BOOTSTRAP").fresh && st.get("CTX-BOOTSTRAP").changed.includes("ART-AGENTS-MD"), "editing an included artifact's file stales the pack (file hash is an input)");
  ctx.build(root);

  /* schema change → everything */
  const cfgp = path.join(root, "PROJECT-CONTEXT", "schemas", "relations.json");
  fs.writeFileSync(cfgp, fs.readFileSync(cfgp, "utf8").replace('"version": 1', '"version": 2'));
  st = statusOf(root);
  ok([...st.values()].every(s => !s.fresh), "changing a schema/registry stales every pack");
  ctx.build(root);

  /* unrelated repository change → nothing */
  fs.appendFileSync(path.join(root, "FLOWS.md"), "\nunrelated edit\n");
  st = statusOf(root);
  ok([...st.values()].every(s => s.fresh), "an unrelated file change invalidates no pack");
}

/* ===================================================================== §C */
section("§C integrity failures are detected, never papered over");
{
  let root = sandbox("corrupt");
  const f = path.join(root, "PROJECT-CONTEXT", "contexts", "CTX-GOVERNANCE.md");
  fs.writeFileSync(f, fs.readFileSync(f, "utf8").replace("Knowledge Once", "Knowledge Twice"));
  let st = statusOf(root);
  ok(st.get("CTX-GOVERNANCE").reason === "corrupted", "a hand-edited pack is detected as corrupted (sha256 mismatch)");
  ok(codes(ctx.verify(root)).includes("pack-corrupted"), "verify reports the corruption");
  fs.rmSync(path.join(root, "PROJECT-CONTEXT", "contexts", "CTX-BOOTSTRAP.json"));
  st = statusOf(root);
  ok(st.get("CTX-BOOTSTRAP").reason === "missing", "a missing pack is detected");
  let { K, G } = ctx.open(root);
  ok(Pr.assimilate(K, G, "TASK-CTX-0001", { agent: "t" }).verdict === "blocked", "missing or corrupted packs block assimilation");

  /* archive tamper */
  root = sandbox("tamper");
  editKind(root, "source", recs => { const r = recs.find(x => x.id === "SRC-ARCH-6"); r.storage.sha256 = "0".repeat(64); });
  let v = ctx.verify(root);
  ok(codes(v).includes("archive-checksum-mismatch"), "a manifest checksum that no longer matches the archived bytes is an error");
  root = sandbox("live-diverged");
  fs.appendFileSync(path.join(root, "UCOS-REPOSITORY-INDEX.md"), "\nlocal edit\n");
  ({ K } = ctx.open(root));
  const r = A.verifyAll(K).results.find(x => x.id === "SRC-REPOSITORY-INDEX");
  ok(r.status === "live-diverged" && r.level === "warn", "editing a live source keeps the archived version verifiable (from git) and warns to capture the new version", JSON.stringify(r));
  const cap = A.captureRepoFile(K, "UCOS-REPOSITORY-INDEX.md", { now: "2026-10-22T00:00:00Z" });
  ({ K } = ctx.open(root));
  ok(cap.supersedes === "SRC-REPOSITORY-INDEX" && K.nodes.get(cap.record.id) && K.nodes.get("SRC-REPOSITORY-INDEX").rec.supersededBy.includes(cap.record.id), "capture archives the new bytes as a NEW source superseding the old (the original is never overwritten)");
  ok(A.verifyAll(K).results.find(x => x.id === "SRC-REPOSITORY-INDEX").status === "verified", "the superseded original still verifies from git's object store");

  /* duplicate ids, broken references, cycles */
  root = sandbox("graph");
  editKind(root, "source", recs => { recs.push(Object.assign({}, recs[0])); });
  ok(codes(ctx.verify(root)).includes("duplicate-id"), "a duplicate source id is rejected");
  root = sandbox("graph2");
  editKind(root, "requirement", recs => {
    recs.find(x => x.id === "REQ-CTX-GRAPH").dependsOn = ["REQ-CTX-PACKS", "REQ-DOES-NOT-EXIST"];
    recs.find(x => x.id === "REQ-CTX-PACKS").dependsOn = ["REQ-CTX-GRAPH"];
  });
  v = ctx.verify(root);
  ok(codes(v).includes("broken-reference"), "a reference to a missing id is a broken-reference error");
  ok(codes(v).includes("cycle") && v.errors.find(e => e.code === "cycle").message.includes("→"), "a depends-on cycle is reported with its path");
  ok(ctx.build(root).ok === false, "the build refuses to generate from invalid knowledge (fail closed)");

  /* conflicts */
  root = sandbox("conflict");
  editKind(root, "requirement", recs => { recs.find(x => x.id === "REQ-CTX-HYGIENE").conflictsWith = ["REQ-CTX-ARCHIVE"]; });
  ok(codes(ctx.verify(root)).includes("untracked-conflict"), "a conflicts-with edge without a conflict issue is an error (it could be read as settled)");
  editKind(root, "issue", recs => recs.push({ id: "ISS-TEST-CONFLICT", kind: "conflict", title: "test conflict", statement: "hygiene and archive disagree", status: "open", severity: "high", affects: ["REQ-CTX-HYGIENE", "REQ-CTX-ARCHIVE"], blocks: ["TASK-CTX-0001"], lifecycle: "canonical-active" }));
  ctx.build(root);
  v = ctx.verify(root);
  ok(!codes(v).includes("untracked-conflict"), "a tracked conflict is accepted by verify");
  ({ K, G } = ctx.open(root));
  const rc = Pr.assimilate(K, G, "TASK-CTX-0001", { agent: "t" });
  ok(rc.verdict === "blocked" && rc.gaps.some(g => g.code === "open-conflict"), "an open conflict blocking the task blocks assimilation");
  ok(fs.readFileSync(path.join(root, "PROJECT-CONTEXT", "contexts", "CTX-CONTINUITY-SYSTEM.md"), "utf8").includes("ISS-TEST-CONFLICT"), "the conflict is surfaced in the affected pack's uncertainty section");

  /* historical evidence used as authority */
  root = sandbox("historical");
  editKind(root, "constraint", recs => { recs.find(x => x.id === "CST-ZERO-HARDCODING").owner = "_superseded/UCRS-Zero-Hardcoding-Constitution.original.md"; });
  ok(codes(ctx.verify(root)).includes("historical-as-authority"), "historical evidence (_superseded/) used as an owner is an error");
}

/* ===================================================================== §D */
section("§D hygiene safety: lifecycle and consolidation");
{
  const root = sandbox("hygiene");
  let { K, G } = ctx.open(root);
  const scan = H.scan(K);
  ok(scan.nearDuplicates.some(d => d.files.some(f => f.startsWith("_superseded/"))), "near-duplicate detection finds the superseded originals vs their successors");
  const statusBefore = U.gitText(root, ["status", "--porcelain"]);
  H.scan(K); H.knowledge(K, G);
  ok(U.gitText(root, ["status", "--porcelain"]) === statusBefore, "hygiene scanning changes nothing in the tree");

  let e1 = null; try { H.transition(K, "REQ-CTX-CI", "superseded", { by: "t", supersededBy: ["REQ-CTX-VERIFICATION"] }); } catch (e) { e1 = e; }
  ok(e1 && /requires approval/.test(e1.message), "a destructive transition without approval is refused");
  let e2 = null; try { H.transition(K, "REQ-CTX-CI", "derived", { by: "t" }); } catch (e) { e2 = e; }
  ok(e2 && /not allowed/.test(e2.message), "a transition the lifecycle registry does not allow is refused");
  let e3 = null; try { H.transition(K, "UCOS-CON-000001", "retired", { by: "t", approvedBy: "x" }); } catch (e) { e3 = e; }
  ok(e3 && /owned by/.test(e3.message), "imported UCOS artifacts cannot be transitioned here (their owner is the registry)");

  /* consolidation: two overlapping requirements */
  editKind(root, "requirement", recs => {
    const base = recs.find(x => x.id === "REQ-CTX-CI");
    recs.push(Object.assign(JSON.parse(JSON.stringify(base)), { id: "REQ-CTX-CI-DUP", title: "CI dup", statement: "CI validates generated-output drift.", acceptance: ["The CI workflow runs context:verify and the context test.", "CI fails on drift."], sources: [{ ref: "SRC-README", segment: "S0003" }] }));
  });
  ({ K, G } = ctx.open(root));
  const lossy = { id: "PLAN-1", sources: ["REQ-CTX-CI-DUP"], destination: "REQ-CTX-CI", mapping: [
    { from: "REQ-CTX-CI-DUP", item: "statement", to: "REQ-CTX-CI" },
    { from: "REQ-CTX-CI-DUP", item: "acceptance[0]", to: "REQ-CTX-CI" }] };
  let res = H.consolidate(K, lossy, { by: "t", approvedBy: "owner" });
  ok(!res.ok && res.errors.some(e => /unmapped unique item REQ-CTX-CI-DUP.acceptance\[1\]/.test(e)) && res.errors.some(e => /sources\[0\]/.test(e)), "a plan that leaves an item unmapped is refused", res.errors.join(" | "));
  ok(!res.ok && res.errors.some(e => /does not contain it/.test(e)), "a plan that maps text the destination lacks is refused (knowledge would be lost)");
  editKind(root, "requirement", recs => {
    const d = recs.find(x => x.id === "REQ-CTX-CI");
    d.acceptance.push("CI fails on drift."); d.statement += " CI validates generated-output drift."; d.sources.push({ ref: "SRC-README", segment: "S0003" });
  });
  ({ K, G } = ctx.open(root));
  const complete = { id: "PLAN-2", sources: ["REQ-CTX-CI-DUP"], destination: "REQ-CTX-CI", mapping: ["statement", "acceptance[0]", "acceptance[1]", "sources[0]"].map(item => ({ from: "REQ-CTX-CI-DUP", item, to: "REQ-CTX-CI" })) };
  res = H.consolidate(K, complete, { by: "t" });
  ok(res.ok && !res.applied, "a complete plan without an approver is validated but not applied");
  res = H.consolidate(K, complete, { by: "t", approvedBy: "owner", now: "2026-10-22T00:00:00Z" });
  ({ K, G } = ctx.open(root));
  const dup = K.nodes.get("REQ-CTX-CI-DUP");
  ok(res.applied && dup && dup.rec.lifecycle === "superseded" && dup.rec.supersededBy.includes("REQ-CTX-CI"), "an approved complete plan supersedes the source record");
  ok(dup.rec.history.some(h => h.approvedBy === "owner" && h.to === "superseded") && dup.rec.statement, "the superseded record keeps its content and a history entry naming the approver (recoverable)");
  ok(!K.active("REQ-CTX-CI-DUP"), "superseded knowledge is no longer active authority");
}

/* ===================================================================== §E */
section("§E protocol: budgets, receipts, handoffs");
{
  const root = sandbox("protocol");
  let { K, G } = ctx.open(root);
  /* budgets: a small agent */
  const small = P.renderAll(K, G, { budget: 6000 });
  const sys = small.packs.find(p => p.json.id === "CTX-EVIDENCE-ARCHIVE").json;
  ok(sys.parts.length > 1 && sys.parts.slice(1).every(x => x.bytes <= 6000), "at a 6000-byte budget a large pack splits into linked parts within budget");
  const sysPack = small.packs.find(p => p.json.id === "CTX-EVIDENCE-ARCHIVE");
  ok(sys.mandatory.every(id => sysPack.parts[0].body.includes(id)), "every mandatory item stays in part 1 after the split");
  const over = small.packs.find(p => p.json.status === "mandatory-over-budget");
  ok(!!over && over.parts[0].body.length > 0 && over.json.mandatory.every(id => over.parts[0].body.includes(id)), "when the mandatory block cannot fit, the pack is still emitted whole and flagged — nothing mandatory is dropped");
  const tiny = Pr.assimilate(K, G, "TASK-CTX-0001", { agent: "small", budget: 6000 });
  ok(tiny.verdict === "blocked" && tiny.gaps.some(g => g.code === "over-budget"), "the gate blocks (instead of passing) when essential knowledge cannot fit the agent's budget");
  const okBudget = Pr.assimilate(K, G, "TASK-CTX-0003", { agent: "small", budget: 20000 });
  ok(okBudget.verdict !== "blocked" && okBudget.readingOrder.every(u => u.step === "supplementary" || u.bytes <= 20000), "a 20 KB agent can assimilate a task whose packs fit, with every required unit within budget", JSON.stringify(okBudget.gaps));

  /* receipts */
  const rc = Pr.assimilate(K, G, "TASK-CTX-0001", { agent: "tester" });
  const file = Pr.writeReceipt(K, rc);
  const rec = U.readJSON(file);
  ok(rec.schema === "ctx-receipt/1" && rec.packs.length >= 4 && rec.packs.every(p => p.fingerprint.length === 64) && rec.requirements.includes("REQ-CTX-PACKS"), "the receipt records packs with fingerprints, mandatory requirements and the verdict");
  ok(rec.repository.head && rec.acceptance.length && rec.scope.length && rec.exclusions.length, "the receipt records HEAD, acceptance criteria, scope and exclusions");
  ok(Pr.assimilate(K, G, "TASK-NOPE", { agent: "t" }).verdict === "blocked", "an unknown task blocks");

  /* handoffs */
  let h = Pr.handoff(K, G, "TASK-CTX-0001", { agent: "t", completed: [{ claim: "x", evidence: "y" }], tests: [{ command: "node test/context.js", result: "passed" }], nextAction: "next" }, { dryRun: true });
  ok(!h.ok && h.errors.some(e => /marked passed without exitCode 0/.test(e)), "a handoff claiming a passed test without exit code and observed output is rejected");
  h = Pr.handoff(K, G, "TASK-CTX-0001", { agent: "t", state: "done", notCompleted: ["something"], nextAction: "n" }, { dryRun: true });
  ok(!h.ok && h.errors.some(e => /state 'done' with notCompleted/.test(e)), "a handoff claiming done with incomplete work is rejected");
  h = Pr.handoff(K, G, "TASK-CTX-0001", { agent: "t", completed: [{ claim: "x" }], nextAction: "n" }, { dryRun: true });
  ok(!h.ok, "a completed claim without evidence fails the handoff schema");
  h = Pr.handoff(K, G, "TASK-CTX-0001", { agent: "tester", completed: [{ claim: "added a test", evidence: "test/context.js §E" }], notCompleted: ["owner approval"], tests: [{ command: "node test/context.js", result: "passed", exitCode: 0, observed: "all passed" }], nextAction: "ask the owner to approve DEC-CTX-*" }, { now: "2026-10-22T12:00:00Z" });
  ok(h.ok && fs.existsSync(h.file), "a valid handoff is written", (h.errors || []).join(" | "));
  ctx.build(root);
  ({ K, G } = ctx.open(root));
  ok(K.nodes.get("TASK-CTX-0001").rec.nextAction === "ask the owner to approve DEC-CTX-*" && K.nodes.get("TASK-CTX-0001").rec.history.some(x => /handoff HO-CTX-0001-/.test(x.change)), "the handoff updates the task's next action and history");
  ok(fs.readFileSync(path.join(root, "PROJECT-CONTEXT", "08-SESSION-LEDGER.md"), "utf8").includes(h.handoff.id) && fs.readFileSync(path.join(root, "PROJECT-CONTEXT", "task-packs", "TASK-CTX-0001.md"), "utf8").includes(h.handoff.id), "the session ledger and the task pack point at the new handoff");
  ok(ctx.verify(root).ok, "verify passes after a handoff and rebuild", codes(ctx.verify(root)).join(","));
  fs.writeFileSync(path.join(root, "PROJECT-CONTEXT", "handoffs", "HO-CTX-0001-099.json"), JSON.stringify({ schema: "ctx-handoff/1", id: "HO-CTX-0001-099", task: "TASK-CTX-0001" }));
  ok(codes(ctx.verify(root)).includes("handoff-invalid"), "an incomplete handoff on disk fails verification");
}

/* ===================================================================== §F */
section("§F archive: private import, write-once store, isolated restore");
{
  const root = sandbox("archive");
  const store = path.join(TMP, "private-store");
  const exp = path.join(TMP, "export.md");
  fs.writeFileSync(exp, "# Synthetic conversation export\n\n## Turn 1\nuser asks for a feature\n\n## Turn 2\nagent answers\n");
  /* commit the sandbox so "what changed" is exactly what the import changed */
  cp.execFileSync("git", ["-c", "user.name=ctx-test", "-c", "user.email=ctx-test@invalid", "add", "-A"], { cwd: root });
  cp.execFileSync("git", ["-c", "user.name=ctx-test", "-c", "user.email=ctx-test@invalid", "commit", "-qm", "sandbox baseline", "--no-verify", "--allow-empty"], { cwd: root });
  let { K } = ctx.open(root);
  const imp = A.importFile(K, exp, { id: "SRC-TEST-EXPORT", store, sensitivity: "private", now: "2026-10-22T00:00:00Z" });
  ok(fs.existsSync(imp.stored) && !imp.stored.startsWith(root), "an import lands in the store outside the repository");
  ok((fs.statSync(imp.stored).mode & 0o222) === 0, "store objects are written read-only (write-once)");
  const changed = U.gitText(root, ["status", "--porcelain", "--untracked-files=all"]).split("\n").filter(Boolean);
  ok(changed.length === 1 && /PROJECT-CONTEXT\/knowledge\/sources\.json$/.test(changed[0]), "only the manifest metadata changes in git; the export's bytes are not in the repository", changed.join(" | "));
  let dupErr = null; ({ K } = ctx.open(root)); try { A.importFile(K, exp, { id: "SRC-TEST-EXPORT", store }); } catch (e) { dupErr = e; }
  ok(dupErr && /already exists/.test(dupErr.message), "a source id is never reused");
  const link = path.join(TMP, "link.md"); fs.symlinkSync(exp, link);
  let symErr = null; try { A.importFile(K, link, { id: "SRC-TEST-LINK", store }); } catch (e) { symErr = e; }
  ok(symErr && /symlinks are refused/.test(symErr.message), "symlinked imports are refused");
  ({ K } = ctx.open(root));
  let r = A.verifyAll(K, { store }).results.find(x => x.id === "SRC-TEST-EXPORT");
  ok(r.status === "verified", "with the store reachable, the private source verifies by sha256");
  r = A.verifyAll(K, { store: path.join(TMP, "no-store") }).results.find(x => x.id === "SRC-TEST-EXPORT");
  ok(r.level === "warn" && r.status === "store-unavailable", "without the store (e.g. CI), it is a warning — not a silent pass, not a false failure");
  const n = K.nodes.get("SRC-TEST-EXPORT");
  ok(A.segments(n, A.bytesOf(K, n, { store }).buf).length === 3, "segment boundaries are computed over the archived bytes");
  fs.chmodSync(imp.stored, 0o600); fs.writeFileSync(imp.stored, "tampered");
  r = A.verifyAll(K, { store }).results.find(x => x.id === "SRC-TEST-EXPORT");
  ok(r.status === "checksum-mismatch" && r.level === "error", "a tampered store object is detected");
  fs.writeFileSync(imp.stored, fs.readFileSync(exp));

  /* restore into an isolated destination, live repository untouched */
  const before = U.gitText(ROOT, ["status", "--porcelain"]);
  ({ K } = ctx.open(ROOT));
  const rs = A.restoreCheck(K, {});
  ok(rs.ok && rs.failed === 0 && rs.restored === K.of("source").filter(x => x.rec.preservation === "preserved").length, "restore-check restores and re-verifies every preserved repository source", JSON.stringify(rs.results.filter(x => x.status !== "restored")));
  ok(U.gitText(ROOT, ["status", "--porcelain"]) === before, "restore-check leaves the live repository untouched");
  let inside = null; try { A.restoreCheck(K, { dest: path.join(ROOT, "PROJECT-CONTEXT", "x") }); } catch (e) { inside = e; }
  ok(inside && /outside the repository/.test(inside.message), "restore into the live repository is refused");
  ({ K } = ctx.open(root));
  const rs2 = A.restoreCheck(K, { store });
  ok(rs2.ok && rs2.results.find(x => x.id === "SRC-TEST-EXPORT").status === "restored", "restore-check also restores private store objects when the store is available");
}

/* ===================================================================== §G */
section("§G fresh agent: no conversation history, repository files only");
{
  const root = sandbox("fresh");
  /* 1. the only thing a fresh agent is told: the repository. It finds the entry point. */
  const entry = fs.readFileSync(path.join(root, "AGENTS.md"), "utf8");
  const idx = /`(PROJECT-CONTEXT\/00-MASTER-INDEX\.md)`/.exec(entry);
  ok(!!idx, "AGENTS.md names the master index");
  /* 2. verify, as instructed */
  let r = cli(root, ["verify", "--json"]);
  ok(r.code === 0 && JSON.parse(r.out).ok, "step 2 — `context verify` exits 0", r.err + r.out.slice(0, 400));
  /* 3. the master index's task table names the task and its pack */
  const master = fs.readFileSync(path.join(root, idx[1]), "utf8");
  const row = master.split("\n").find(l => l.includes("[TASK-CTX-0001]"));
  ok(row && /task-packs\/TASK-CTX-0001\.md/.test(row), "step 4 — the master index resolves the task to its task pack");
  /* 4. the gate, at a mid-size budget; load ONLY what it lists */
  r = cli(root, ["assimilate", "TASK-CTX-0001", "--agent", "fresh-agent", "--budget", "24000", "--write", "--json"]);
  const receipt = JSON.parse(r.out);
  ok(r.code === 0 && receipt.verdict !== "blocked" && receipt.file, "step 5 — the gate passes and writes a receipt", JSON.stringify(receipt.gaps));
  const loaded = receipt.readingOrder.filter(u => u.step !== "supplementary").map(u => fs.readFileSync(path.join(root, u.ref.split(" ")[0]), "utf8")).join("\n");
  ok(receipt.readingOrder.filter(u => u.step !== "supplementary").every(u => u.bytes <= 24000), "every unit the agent must read fits its budget");
  /* 5. from that text alone, recover what continuing requires */
  ok(/CST-KNOWLEDGE-ONCE/.test(loaded) && /CST-EVIDENCE-BEFORE-CLAIMS/.test(loaded) && /CST-AUTHORIZED-SIDE-EFFECTS/.test(loaded), "recovers the governing constraints");
  ok(/\*\*in-progress\*\*/.test(loaded) && /Next action: \*\*/.test(loaded), "recovers the task state and the exact next action");
  ok(/DEC-CTX-LOCATION/.test(loaded) && /Status: \*\*proposed\*\*/.test(loaded), "recovers the relevant decisions and that they are only proposed");
  ok(/ISS-CTX-DECISIONS-UNAPPROVED/.test(loaded) && /ISS-MASTER-PROMPT-NOT-ARCHIVED/.test(loaded), "recovers open issues and recovery limits");
  ok(/`npm run context:verify`/.test(loaded) && /`node test\/context\.js`/.test(loaded), "recovers the required verification commands");
  ok(/\[verified\]/.test(loaded) && /\[unverified\]/.test(loaded), "can tell verified facts from unverified ones");
  ok(/Excluded:|Must not change/.test(loaded) && /No push, PR or deployment/.test(loaded), "recovers what must not be changed");
  ok(/CTX-BOOTSTRAP/.test(loaded) && receipt.readingOrder[0].step === "master-index", "follows the documented reading order (index → task pack → bootstrap → prerequisites)");
  /* 6. a small agent is told the truth, not given a false pass */
  r = cli(root, ["assimilate", "TASK-CTX-0001", "--agent", "tiny", "--budget", "4000", "--json"]);
  ok(r.code === 2 && JSON.parse(r.out).gaps.some(g => g.code === "over-budget"), "a 4 KB agent is BLOCKED with the reason (exit 2), not handed a partial context as complete");
  /* 7. stale context is refused */
  editKind(root, "decision", recs => { recs.find(x => x.id === "DEC-CTX-LOCATION").selected += " (edited)"; });
  r = cli(root, ["assimilate", "TASK-CTX-0001", "--agent", "fresh-agent", "--json"]);
  ok(r.code === 2 && JSON.parse(r.out).gaps.some(g => g.code === "pack-stale"), "after an unbuilt knowledge change the fresh agent is blocked as stale");
  r = cli(root, ["build"]);
  ok(r.code === 0, "`context build` refreshes it");
  /* 8. the fresh agent hands off */
  const hf = path.join(TMP, "handoff.json");
  fs.writeFileSync(hf, JSON.stringify({ agent: "fresh-agent", completed: [{ claim: "recovered context with no prior conversation", evidence: receipt.file }], notCompleted: ["remaining owner approvals"], unverified: [], tests: [{ command: "npm run context:verify", result: "passed", exitCode: 0, observed: "context verify passed" }], nextAction: "Ask the owner to review DEC-CTX-* (TASK-CTX-0002)." }));
  r = cli(root, ["handoff", "TASK-CTX-0001", "--from", hf]);
  ok(r.code === 0, "step 10 — the fresh agent records a valid handoff", r.err + r.out);
  r = cli(root, ["verify"]);
  ok(r.code === 0, "and the repository verifies afterwards", r.out.slice(0, 600));
  /* exit codes */
  ok(cli(root, ["nonsense"]).code === 3, "usage errors exit 3");
}

/* ===================================================================== §H */
section("§H audit hardening: nothing mandatory is optional, nothing is claimed unmeasured");
{
  /* 1. classification: open issues of any severity, security/privacy constraints and
        dependencies of mandatory items are mandatory */
  let root = sandbox("mand");
  editKind(root, "issue", recs => recs.push({ id: "ISS-TEST-LOW", kind: "question", title: "a low open question", statement: "minor uncertainty that must still be seen", status: "open", severity: "low", affects: ["REQ-CTX-PACKS"], lifecycle: "canonical-active" }));
  editKind(root, "constraint", recs => recs.push({ id: "CST-TEST-SEC", title: "non-critical security rule", statement: "a security rule not flagged critical", class: "security", owner: "PROJECT-CONTEXT/knowledge/constraints.json", scope: "scoped", critical: false, sources: [{ ref: "SRC-README", segment: "S0003" }], lifecycle: "canonical-active" }));
  editKind(root, "requirement", recs => {
    const base = recs.find(x => x.id === "REQ-CTX-CI");
    recs.push(Object.assign(JSON.parse(JSON.stringify(base)), { id: "REQ-TEST-LOWDEP", title: "low-priority dependency", statement: "a low-priority requirement a critical one depends on", priority: "low", dependsOn: [] }));
    recs.find(x => x.id === "REQ-CTX-PACKS").dependsOn = ["REQ-TEST-LOWDEP"];
  });
  editKind(root, "context", recs => { recs.find(x => x.id === "CTX-CONTINUITY-SYSTEM").include.constraints = ["CST-TEST-SEC"]; });
  let { K, G } = ctx.open(root);
  let rendered = P.renderAll(K, G, { budget: 9000 });
  let pk = rendered.packs.find(p => p.json.id === "CTX-CONTINUITY-SYSTEM");
  for (const id of ["ISS-TEST-LOW", "CST-TEST-SEC", "REQ-TEST-LOWDEP"]) ok(pk.json.mandatory.includes(id) && pk.parts[0].body.includes(id), id + " is mandatory and stays in part 1 under a tight budget");
  ok(pk.json.excluded.length === 0 && pk.parts.slice(1).every(x => !/ISS-TEST-LOW|CST-TEST-SEC|REQ-TEST-LOWDEP/.test(x.body)), "…and appears in no supplementary part");

  /* 2. an oversized block: knowledge blocks the gate, an artifact only warns */
  root = sandbox("oversize");
  const huge = "x".repeat(30000);
  editKind(root, "requirement", recs => {
    const base = recs.find(x => x.id === "REQ-CTX-CI");
    recs.push(Object.assign(JSON.parse(JSON.stringify(base)), { id: "REQ-TEST-HUGE", title: "huge low requirement", statement: "huge " + huge, priority: "low", implementedBy: [], verifiedBy: ["ART-TEST-CONTEXT"] }));
  });
  editKind(root, "context", recs => { recs.find(x => x.id === "CTX-PLATFORM-QUALITY").include.requirements = ["REQ-TEST-HUGE"]; });
  ctx.build(root);
  ({ K, G } = ctx.open(root));
  const pq = U.readJSON(path.join(root, "PROJECT-CONTEXT", "contexts", "CTX-PLATFORM-QUALITY.json"));
  ok(pq.status === "incomplete" && pq.excluded.some(e => e.id === "REQ-TEST-HUGE" && e.kind === "requirement"), "an oversized non-mandatory block is excluded AND recorded with its reason, never silently dropped");
  ok(fs.readFileSync(path.join(root, "PROJECT-CONTEXT", "contexts", "CTX-PLATFORM-QUALITY.md"), "utf8").includes("REQ-TEST-HUGE: a single block of"), "the exclusion is written into the pack itself");
  ok(codes(ctx.verify(root)).length === 0 && ctx.verify(root).warnings.some(w => w.code === "pack-incomplete"), "verify reports the incomplete pack as a warning");
  const gate = Pr.assimilate(K, G, "TASK-SEC-0001", { agent: "t" });
  ok(gate.verdict === "blocked" && gate.gaps.some(g => g.code === "knowledge-excluded" && /REQ-TEST-HUGE/.test(g.message)), "the gate BLOCKS when knowledge (not just an artifact) could not fit");

  /* 3. traceability and entry-point consistency are CI failures */
  root = sandbox("trace");
  editKind(root, "requirement", recs => { recs.find(x => x.id === "REQ-CTX-HANDOFF").verifiedBy = []; });
  ctx.build(root, { force: true });
  ok(codes(ctx.verify(root)).includes("requirement-unverified"), "a critical requirement without a verifying test fails verify");
  root = sandbox("entry");
  fs.appendFileSync(path.join(root, "AGENTS.md"), "\nRun `npm run context:does-not-exist` and read `PROJECT-CONTEXT/99-NOPE.md`.\n");
  ctx.build(root);
  const ev = codes(ctx.verify(root));
  ok(ev.includes("entry-point-command") && ev.includes("entry-point-path"), "an entry point citing a missing command or file fails verify");

  /* 4. receipts state the cumulative reading load honestly */
  ({ K, G } = ctx.open(ROOT));
  const rc = Pr.assimilate(K, G, "TASK-CTX-0002", { agent: "t", budget: 12000 });
  ok(rc.totalRequiredBytes > 12000 && rc.gaps.some(g => g.code === "sequential-reading"), "when required reading exceeds one window the receipt says so (sequential reading), not 'fits'");

  /* 5. restore isolation is measured, not asserted */
  const rs = A.restoreCheck(K, {});
  ok(rs.liveRepositoryTouched === false && rs.ok, "restore-check measures git status before/after (untouched)");
}

/* ===================================================================== §I */
section("§I fresh agent at a deliberately small budget (12 000 B ≈ 4k tokens, estimated)");
{
  const root = sandbox("fresh-small");
  const B = "12000";
  const entry = fs.readFileSync(path.join(root, "AGENTS.md"), "utf8");
  ok(/PROJECT-CONTEXT\/00-MASTER-INDEX\.md/.test(entry) && Buffer.byteLength(entry) <= Number(B), "the entry point itself fits the small window");
  const master = fs.readFileSync(path.join(root, "PROJECT-CONTEXT", "00-MASTER-INDEX.md"), "utf8");
  ok(Buffer.byteLength(master) <= Number(B) && master.includes("[TASK-CTX-0002]"), "the master index fits the window and lists the task");
  const r = cli(root, ["assimilate", "TASK-CTX-0002", "--agent", "small-agent", "--budget", B, "--write", "--json"]);
  const rc = JSON.parse(r.out);
  ok(r.code === 0 && rc.verdict !== "blocked", "a 12 KB agent passes the gate for TASK-CTX-0002", JSON.stringify(rc.gaps.filter(g => g.severity === "block")));
  const units = rc.readingOrder.filter(u => u.step !== "supplementary");
  ok(units.every(u => u.bytes <= Number(B)), "every required unit fits the 12 KB window (read one at a time)");
  /* read unit by unit — never more than one window — and keep only what each must yield */
  const found = {};
  for (const u of units) {
    const t = fs.readFileSync(path.join(root, u.ref.split(" ")[0]), "utf8");
    if (/^# TASK-CTX-0002/m.test(t)) { found.task = true; found.state = /\*\*planned\*\*/.test(t); found.next = /Next action: \*\*Owner reads/.test(t); found.dep = /## Depends on\n\n- TASK-CTX-0001/.test(t); found.tests = /`npm run context:verify`/.test(t); }
    if (/CST-KNOWLEDGE-ONCE/.test(t) && /CST-AUTHORIZED-SIDE-EFFECTS/.test(t)) found.rules = true;
    if (/DEC-CTX-LOCATION/.test(t) && /Status: \*\*proposed\*\*/.test(t)) found.decisions = true;
    if (/ISS-CTX-DECISIONS-UNAPPROVED/.test(t)) found.blocker = true;
    if (/\[verified\]/.test(t) && /\[unverified\]/.test(t)) found.facts = true;
  }
  ok(found.task && found.state, "finds the current task and its actual state (planned)");
  ok(found.dep && rc.prerequisites.includes("TASK-CTX-0001") && rc.gaps.some(g => g.code === "prerequisite-open"), "finds its dependency (TASK-CTX-0001) and that it is still open");
  ok(found.rules, "finds the governing constraints");
  ok(found.decisions && found.blocker, "finds the decisions under review and the approval issue");
  ok(found.next && found.tests, "finds the exact next action and the required verification");
  ok(found.facts, "separates verified facts from unverified ones");
  const tiny = cli(root, ["assimilate", "TASK-CTX-0002", "--agent", "tiny", "--budget", "8000", "--json"]);
  ok(tiny.code === 2 && JSON.parse(tiny.out).gaps.some(g => g.code === "over-budget"), "below the bootstrap's size (8 KB) the gate blocks with the reason instead of a partial pass");
}

/* ===================================================================== */
const total = pass + fail;
console.log("\ncontext continuity: " + pass + "/" + total + " passed" + (fail ? " — " + fail + " FAILED" : ""));
process.exit(fail ? 1 : 0);
