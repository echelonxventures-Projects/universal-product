/* UCOS Ω∞ · the context continuity system — every invariant, proven on fixtures and on the repository.
   --------------------------------------------------------------------------
   §A  the repository itself: valid, fresh, deterministic, bounded, every pack
       pointing at real sources, every sequence complete with an END marker
   §B  registration and references: unregistered files, dangling references,
       acknowledged conflicts, duplicate ids, illegal and allowed cycles
   §C  traversal: mandatory prerequisites discovered and ordered, small-agent
       retrieval bounded, historical material never in a default bootstrap
   §D  packs: splitting never truncates, an unsplittable line is reported,
       secrets never reach a pack
   §E  maintenance: a source change makes exactly the right packs stale, build
       --affected regenerates only predicted packs, unaffected packs stay
       byte-identical, stale context fails the check
   §F  lifecycle and supersession: unrecorded supersession is an error, a recorded
       one becomes an explicit edge
   §G  bootstrap receipts: REFUSE on missing / stale-copy packs, ASSIMILATED when
       complete
   §H  handoffs: append-only hash chain, tamper detected, a FRESH process resumes
       from repository state alone
   §I  hygiene: near-duplicates, deprecated references, generator drift, ratchet

   No server, no port, no database. Fixtures are throw-away git repositories. */
"use strict";
const fs = require("fs");
const os = require("os");
const path = require("path");
const { spawnSync, execFileSync } = require("child_process");

const ROOT = path.resolve(__dirname, "..");
const G = require(path.join(ROOT, "_registry", "context-graph.js"));
const P = require(path.join(ROOT, "_registry", "context-packs.js"));
const H = require(path.join(ROOT, "_registry", "context-hygiene.js"));
const C = require(path.join(ROOT, "_registry", "context.js"));
const CLI = path.join(ROOT, "_registry", "context.js");

let passed = 0, failed = 0;
function ok(c, n, x) { if (c) { passed++; console.log("  ✓ " + n); } else { failed++; console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)).slice(0, 600) : "")); } }
const errs = (gen, code) => gen.findings.filter(f => f.severity === "error" && (!code || f.code === code));
const TMP = fs.mkdtempSync(path.join(os.tmpdir(), "ctx-test-"));
process.on("exit", () => { if (process.env.CTX_KEEP) return console.log("fixtures kept in " + TMP); try { fs.rmSync(TMP, { recursive: true, force: true }); } catch (e) { } });

/* ---------- a minimal fixture repository ---------- */
let fx = 0;
function baseSpec(over) {
  return Object.assign({
    schema: "ucos.context.spec.v1", registryId: "FIXTURE", output: { dir: "_context" }, discovery: { useGit: true },
    exclude: [], security: { denyPaths: [".env", "**/*.pem"], secretPatterns: ["\\bAKIA[0-9A-Z]{16}\\b"] },
    budgets: { packChars: 6000, reserveChars: 2000, bootstrapChars: 20000 }, primarySequence: "full",
    lifecycles: ["active-canonical", "active-operational", "derived", "consolidatable", "superseded", "historical-evidence", "retired"].map(id => ({ id })),
    authorityLevels: [{ id: "governance" }, { id: "implementation" }, { id: "verification" }, { id: "docs" }, { id: "historical" }, { id: "agent-note" }],
    edgeTypes: [
      { id: "requires", prereq: "to", closure: "mandatory", acyclic: true },
      { id: "must-read-before", prereq: "from", closure: "mandatory", acyclic: true },
      { id: "constrains", prereq: "from", closure: "mandatory", acyclic: true },
      { id: "derived-from", prereq: "to", closure: "mandatory", acyclic: true },
      { id: "continues", prereq: "to", closure: "mandatory", acyclic: true },
      { id: "hands-off-to", prereq: "from", closure: "mandatory", acyclic: true },
      { id: "depends-on", prereq: "to", closure: "relevant", acyclic: false },
      { id: "verified-by", prereq: null, closure: null },
      { id: "supersedes", prereq: null, closure: null, acyclic: true },
      { id: "conflicts-with", prereq: null, closure: null }
    ],
    statusMarkers: [{ pattern: "^# \\[SUPERSEDED", lifecycle: "superseded" }],
    classes: [
      { id: "protocol", match: ["AGENTS.md", "_registry/context.json"], kind: "authoritative", authority: "governance", lifecycle: "active-canonical", owner: "owner" },
      { id: "handoff", match: ["_registry/handoffs/**/*.json"], kind: "agent-note", authority: "agent-note", lifecycle: "active-operational", owner: "agent" },
      { id: "code", match: ["lib/**/*.js", "gen.js"], kind: "authoritative", authority: "implementation", lifecycle: "active-operational", owner: "eng" },
      { id: "test", match: ["test/**"], kind: "verification", authority: "verification", lifecycle: "active-operational", owner: "eng" },
      { id: "generated", match: ["out/**"], kind: "derived", authority: "implementation", lifecycle: "derived", owner: "eng" },
      { id: "history", match: ["old/**"], kind: "historical", authority: "historical", lifecycle: "historical-evidence", owner: "owner" },
      { id: "doc", match: ["*.md", "docs/**", "package.json", ".gitignore"], kind: "explanatory", authority: "docs", lifecycle: "active-operational", owner: "eng" }
    ],
    virtualClasses: [{ id: "constraint", kind: "authoritative", authority: "governance", lifecycle: "active-canonical", owner: "owner" }, { id: "decision", kind: "authoritative", authority: "governance", lifecycle: "active-canonical", owner: "owner" }, { id: "conflict", kind: "authoritative", authority: "governance", lifecycle: "active-operational", owner: "owner" }],
    extractors: [{ type: "js-require" }, { type: "npm-test-script", packageJson: "package.json", script: "test", testClass: "test" }, { type: "handoff-records", recordClass: "handoff" }],
    edges: [{ from: "AGENTS.md", type: "must-read-before", to: "docs/guide.md" }],
    constraints: [{ id: "LAW-X", title: "Rule X", source: "AGENTS.md", quote: "Always do X.", appliesTo: [{ class: "code" }] }],
    decisions: [], conflicts: [], supersessions: [],
    hygiene: { textClasses: ["doc", "history"], duplicateMinParagraphChars: 40, nearDuplicateRatio: 0.9, nearDuplicateMinLineChars: 10, derivedChecks: [], thresholds: {} },
    bootstrap: { alwaysLoad: ["orientation"], taskLifecycles: ["active-canonical", "active-operational", "derived"] },
    units: [
      { id: "orientation", title: "Orientation", purpose: "p", scope: "s", tags: ["gov"], select: [{ class: ["protocol", "constraint", "decision", "conflict"] }] },
      { id: "code", title: "Code", purpose: "p", scope: "s", tags: ["rt"], prerequisites: ["orientation"], select: [{ class: "code" }] },
      { id: "docs", title: "Docs", purpose: "p", scope: "s", tags: ["docs"], select: [{ class: ["doc", "test", "generated"] }] },
      { id: "history", title: "History", purpose: "p", scope: "s", tags: ["trace"], optional: true, select: [{ class: "history" }] },
      { id: "handoffs", title: "Handoffs", purpose: "p", scope: "s", tags: ["trace"], optional: true, select: [{ class: "handoff" }] }
    ],
    sequences: [
      { id: "full", units: ["orientation", "code", "docs", "history", "handoffs"] },
      { id: "dependency-first", computed: "dependency-first", base: "full", purpose: "d" },
      { id: "domain:", computed: "by-tag", base: "full", prefix: "domain:", purpose: "{tag}" },
      { id: "resume", units: ["orientation", "handoffs"] }
    ]
  }, over || {});
}
function makeRepo(files, spec, opts) {
  const dir = path.join(TMP, "fx" + (++fx));
  const all = Object.assign({
    "AGENTS.md": "# Agents\n\nAlways do X.\n",
    "docs/guide.md": "# Guide\n\nHow the fixture works, explained at length for navigation.\n",
    "lib/a.js": "/* module a */\nrequire('./b');\n",
    "lib/b.js": "/* module b */\nrequire('./c.js');\n",
    "lib/c.js": "/* module c */\nmodule.exports = 1;\n",
    "test/t.js": "/* test */\nrequire('../lib/a.js');\n",
    "package.json": JSON.stringify({ scripts: { test: "node test/t.js" } }),
    ".gitignore": "_registry/handoffs/IGNORED/\n"
  }, files || {});
  for (const [rel, text] of Object.entries(all)) { if (text == null) continue; fs.mkdirSync(path.dirname(path.join(dir, rel)), { recursive: true }); fs.writeFileSync(path.join(dir, rel), text); }
  fs.mkdirSync(path.join(dir, "_registry"), { recursive: true });
  fs.writeFileSync(path.join(dir, "_registry", "context.json"), JSON.stringify(spec || baseSpec(), null, 1));
  if (!opts || opts.git !== false) {
    const g = a => execFileSync("git", a, { cwd: dir, stdio: "ignore" });
    g(["init", "-q"]); g(["config", "user.email", "t@example.invalid"]); g(["config", "user.name", "t"]); g(["config", "commit.gpgsign", "false"]);
    g(["add", "-A"]); g(["commit", "-qm", "fixture"]);
  }
  return dir;
}
const write = (dir, rel, text) => { fs.mkdirSync(path.dirname(path.join(dir, rel)), { recursive: true }); fs.writeFileSync(path.join(dir, rel), text); };
const cli = (dir, args, input) => spawnSync(process.execPath, [CLI].concat(args), { cwd: dir, env: Object.assign({}, process.env, { CONTEXT_ROOT: dir }), encoding: "utf8", input });
const gitIn = (dir, a) => execFileSync("git", a, { cwd: dir, encoding: "utf8" }).trim();

/* ======================================================================= */
console.log("\n▸ §A THE REPOSITORY — valid, fresh, deterministic, bounded, complete");
const real = P.generate(ROOT);
{
  ok(!errs(real).length, "the repository's context graph has no integrity errors", errs(real).slice(0, 5));
  const st = C.staleness(ROOT, real);
  ok(st.fresh, "the committed _context/ matches a fresh generation (not stale)", { stale: st.stale, missing: st.missing, extra: st.extra, changed: st.changed.slice(0, 10) });
  const again = P.generate(ROOT);
  const diff = [...real.files].filter(([k, v]) => again.files.get(k) !== v).map(([k]) => k);
  ok(!diff.length && real.files.size === again.files.size, "regeneration over unchanged inputs is byte-identical (" + real.files.size + " files)", diff);
  ok(real.packs.every(p => p.text.length <= real.spec.budgets.packChars), "every pack is within the budget (" + real.spec.budgets.packChars + " chars)");
  const files = new Set([...real.graph.nodes.values()].filter(n => !n.virtual).map(n => n.path));
  const badSrc = real.packs.flatMap(p => p.members.filter(id => { const n = real.graph.nodes.get(id); return !n || (!n.virtual && !fs.existsSync(path.join(ROOT, n.path))); }));
  ok(!badSrc.length && files.size > 200, "every pack member resolves to a registered artifact whose source exists (" + files.size + " files)", badSrc);
  const m = JSON.parse(fs.readFileSync(path.join(ROOT, "_context", "manifest.json"), "utf8"));
  let seqOk = true, why = "";
  for (const s of m.sequences) {
    if (s.count !== s.packs.length || s.end !== "END:" + s.id || G.sha256(JSON.stringify(s.packs)) !== s.digest) { seqOk = false; why = s.id; }
    for (const id of s.packs) if (!m.packs.find(p => p.id === id) || !fs.existsSync(path.join(ROOT, m.packs.find(p => p.id === id).file))) { seqOk = false; why = s.id + ":" + id; }
  }
  ok(seqOk, "every sequence in the manifest is complete: count, END marker, digest, and every pack file exists", why);
  const full = m.sequences.find(s => s.id === "full");
  const allUnitsWithMembers = m.units.filter(u => u.members).every(u => u.packs.every(p => full.packs.includes(p)));
  ok(allUnitsWithMembers && full.packs.length === m.packs.length, "the full sequence reaches every pack (" + full.packs.length + ")");
  /* prev/next links in each pack agree with the manifest order */
  let linkOk = true;
  for (let i = 0; i < full.packs.length; i++) {
    const p = real.packById.get(full.packs[i]);
    const pos = p.positions.find(x => x.sequence === "full");
    if (pos.prev !== (full.packs[i - 1] || null) || pos.next !== (full.packs[i + 1] || null)) linkOk = false;
  }
  const last = real.packById.get(full.packs[full.packs.length - 1]).text;
  ok(linkOk && last.includes("END OF SEQUENCE `full`") && !/\| \d+ \/ \d+ \|/.test(last), "next/previous links derive from the sequence; the last pack carries an explicit END marker");
  const covered = new Set(real.packs.flatMap(p => p.members));
  ok([...real.graph.nodes.values()].every(n => covered.has(n.id)), "every registered node (" + real.graph.nodes.size + ") appears in exactly one pack");
  ok([...real.graph.nodes.values()].every(n => n.lifecycle && n.owner), "every registered node carries a lifecycle and an owner");
}

console.log("\n▸ §B REGISTRATION AND REFERENCES");
{
  const d = makeRepo({ "stray.bin": "x" });
  const g = P.generate(d);
  ok(errs(g, "UNREGISTERED_FILE").some(f => f.subject === "stray.bin"), "a file no class claims is an UNREGISTERED_FILE error");
  const spec = baseSpec();
  spec.edges.push({ from: "lib/a.js", type: "requires", to: "lib/missing.js" });
  const g2 = P.generate(makeRepo({}, spec));
  ok(errs(g2, "DANGLING_EDGE").some(f => f.subject === "lib/missing.js"), "a reference to a missing artifact is a DANGLING_EDGE error");
  spec.conflicts.push({ id: "CNF-T", title: "known", status: "open", statement: "s", between: ["lib/a.js"], acknowledges: [{ code: "DANGLING_EDGE", subject: "lib/missing.js" }] });
  const g3 = P.generate(makeRepo({}, spec));
  ok(!errs(g3, "DANGLING_EDGE").length && g3.findings.some(f => f.code === "DANGLING_EDGE" && f.severity === "warning"), "an open conflict that acknowledges it keeps it visible (warning) without blocking");
  ok(g3.graph.edges.some(e => e.type === "conflicts-with" && e.from === "CNF-T" && e.to === "file:lib/a.js"), "the conflict is an explicit conflicts-with edge");
  const s4 = baseSpec(); s4.decisions.push({ id: "LAW-X", title: "dup", status: "accepted", authority: "a", statement: "s", governs: [] });
  ok(errs(P.generate(makeRepo({}, s4)), "DUPLICATE_ID").length === 1, "a duplicate identifier is detected");
  const s5 = baseSpec(); s5.edges.push({ from: "lib/a.js", type: "requires", to: "lib/b.js" }, { from: "lib/b.js", type: "requires", to: "lib/a.js" });
  ok(errs(P.generate(makeRepo({}, s5)), "ILLEGAL_CYCLE").length === 1, "a cycle over acyclic edge types is ILLEGAL_CYCLE");
  s5.allowedCycles = [{ members: ["file:lib/a.js", "file:lib/b.js"], reason: "mutual" }];
  const g6 = P.generate(makeRepo({}, s5));
  ok(!errs(g6, "ILLEGAL_CYCLE").length && g6.findings.some(f => f.code === "ALLOWED_CYCLE"), "a declared legitimate cycle is reported, not refused");
  const cl = G.closure(g6.graph, ["file:lib/a.js"], "mandatory");
  ok(cl.ids.has("file:lib/b.js") && cl.ids.size >= 2, "traversal over a legitimate cycle terminates");
  const s7 = baseSpec(); s7.constraints[0].quote = "Never stated anywhere.";
  ok(errs(P.generate(makeRepo({}, s7)), "CONSTRAINT_QUOTE_MISSING").length === 1, "a constraint whose quote left its source is CONSTRAINT_QUOTE_MISSING (provenance broken)");
  const s8 = baseSpec(); s8.edges.push({ from: "lib/a.js", type: "frobnicates", to: "lib/b.js" });
  ok(errs(P.generate(makeRepo({}, s8)), "UNKNOWN_EDGE_TYPE").length === 1, "an undeclared edge type is rejected");
  const d9 = makeRepo({ ".env": "X=1" }, null);
  ok(errs(P.generate(d9), "SECRET_PATH").length === 1, "a visible secret-shaped path is refused, never registered");
  let threw = false; try { G.loadSpec(makeRepo({}, { schema: "nope" }, { git: false })); } catch (e) { threw = /invalid/.test(e.message); }
  ok(threw, "an invalid spec fails closed with an explanation");
  ok(errs(P.generate(makeRepo({ "lib/a.js": "require('./nowhere');\n" })), "DANGLING_EDGE").some(f => f.subject === "lib/nowhere"), "a literal require of a missing module is a broken reference");
}

console.log("\n▸ §C TRAVERSAL — prerequisites, small-agent retrieval, bootstrap scope");
{
  const spec = baseSpec();
  spec.edges.push({ from: "lib/a.js", type: "requires", to: "lib/b.js" }, { from: "lib/b.js", type: "requires", to: "lib/c.js" });
  const d = makeRepo({}, spec);
  const g = P.generate(d);
  const p = C.plan(g, "lib/a.js");
  const order = p.mandatory;
  ok(order.includes("file:lib/c.js") && order.indexOf("file:lib/c.js") < order.indexOf("file:lib/b.js") && order.indexOf("file:lib/b.js") < order.indexOf("file:lib/a.js"), "transitive mandatory prerequisites are discovered and ordered prerequisites-first", order);
  ok(order.includes("LAW-X") && order.indexOf("LAW-X") < order.indexOf("file:lib/a.js"), "constraints that bind the target are prerequisites of it");
  ok(p.packs[0] === "orientation/1", "the task plan starts with the always-loaded orientation pack");
  /* the repository: a task resolves to a few bounded packs, never the whole repository */
  const rp = C.plan(real, "lib/authz.js");
  const chars = rp.packs.reduce((s, id) => s + real.packById.get(id).text.length, 0);
  const repoBytes = [...real.graph.nodes.values()].filter(n => !n.virtual).reduce((s, n) => s + n.bytes, 0);
  ok(rp.packs.length < real.packs.length / 4 && chars < repoBytes / 50, "a small-agent task on lib/authz.js loads " + rp.packs.length + "/" + real.packs.length + " packs (" + chars + " chars of " + repoBytes + " repository bytes)");
  const st = C.stages(real, rp.packs, real.spec.budgets.packChars);
  ok(st.every(s => s.reduce((a, id) => a + real.packById.get(id).text.length, 0) <= real.spec.budgets.packChars), "staging with a window of one pack budget keeps every stage within the window (" + st.length + " stages)");
  const always = new Set(real.spec.bootstrap.alwaysLoad);
  const bootMembers = real.packs.filter(x => always.has(x.unit)).flatMap(x => x.members).map(id => real.graph.nodes.get(id));
  ok(bootMembers.every(n => !["historical-evidence", "superseded", "retired"].includes(n.lifecycle)), "the default bootstrap contains no historical or superseded artifact");
  const hist = real.packs.filter(x => x.unit === "history");
  ok(hist.length && hist.every(x => x.text.includes("HISTORICAL / SUPERSEDED content")), "historical packs carry an explicit not-a-requirement banner");
  const im = G.impact(real.graph, [real.graph.byPath.get("_registry/content-core.json").id]);
  ok([...im.ids].filter(id => real.graph.nodes.get(id).class === "projected-artifact").length > 10 && im.ids.has("derived:_registry/canonical.lxr"), "reverse traversal: a registry content file reaches its projected artifacts and the sealed runtime registry");
}

console.log("\n▸ §D PACKS — splitting without truncation, oversize reported, secrets refused");
{
  const big = "# Big\n\n" + Array.from({ length: 400 }, (_, i) => "line " + i + " of the big document").join("\n") + "\n";
  const spec = baseSpec({ budgets: { packChars: 2600, reserveChars: 1600, bootstrapChars: 20000 } });
  const many = {};
  for (let i = 0; i < 30; i++) many["lib/m" + String(i).padStart(2, "0") + ".js"] = "/* module " + i + " with a reasonably descriptive leading comment */\nmodule.exports = " + i + ";\n";
  const d = makeRepo(Object.assign({ "docs/big.md": big }, many), spec);
  const g = P.generate(d);
  const code = g.unitPacks.get("code");
  ok(code.length > 1, "a unit larger than the budget splits into " + code.length + " packs");
  const listed = new Set(code.flatMap(p => p.members));
  ok(g.assignment.members.get("code").every(id => listed.has(id)), "every member of a split unit is listed in one of its parts — nothing dropped");
  ok(code.every((p, i) => p.text.includes("part " + (i + 1) + " of " + code.length)), "every part states its position and the part count");
  const s2 = baseSpec({ budgets: { packChars: 2600, reserveChars: 1600, bootstrapChars: 20000 } });
  s2.constraints.push({ id: "LONG", title: "long", source: "docs/long.md", quote: "L".repeat(3000), appliesTo: [] });
  const g2 = P.generate(makeRepo({ "docs/long.md": "# Long\n\n" + "L".repeat(3000) + "\n" }, s2));
  const lps = g2.packs.filter(p => p.members.includes("LONG"));
  ok(errs(g2, "OVERSIZE_LINE").length && errs(g2, "OVERSIZE_PACK").length && lps.some(p => p.text.includes("L".repeat(3000))), "an unsplittable line is reported as an error and emitted whole — never truncated");
  ok(lps.length > 1 && lps.slice(1).every(p => /continued: chunk/.test(p.text)), "a block split across parts labels every continuation chunk");
  const key = "AKIA" + "ABCDEFGHIJKLMNOP";
  const s3 = baseSpec(); s3.constraints.push({ id: "LEAK", title: "leak", source: "docs/leak.md", quote: key, appliesTo: [] });
  ok(errs(P.generate(makeRepo({ "docs/leak.md": "# Leak\n\n" + key + "\n" }, s3)), "SECRET_CONTENT").length >= 1, "a secret-shaped string that reaches a pack is a SECRET_CONTENT error");
  const g4 = P.generate(makeRepo({ "docs/leak.md": "# Doc\n\nThe key is " + key + " for testing.\n" }));
  ok(!errs(g4, "SECRET_CONTENT").length && !g4.packs.some(p => p.text.includes(key)), "extracted summaries drop secret-shaped text instead of projecting it");
}

console.log("\n▸ §E MAINTENANCE — invalidation, incremental regeneration, stale detection");
{
  const spec = baseSpec();
  spec.edges.push({ from: "lib/a.js", type: "requires", to: "lib/b.js" });
  const d = makeRepo({}, spec);
  ok(cli(d, ["build"]).status === 0, "build writes the generated context");
  let parsed = null; try { parsed = JSON.parse(fs.readFileSync(path.join(d, "_context/manifest.json"), "utf8")); } catch (e) { }
  ok(parsed && parsed.nodes.length === P.generate(d).graph.nodes.size, "the manifest is valid JSON listing every node (also for sequences declared without optional fields)");
  gitIn(d, ["add", "-A"]); gitIn(d, ["commit", "-qm", "context"]);
  const before = new Map(P.generate(d).files);
  ok(cli(d, ["check", "--no-hygiene"]).status === 0, "check passes on a fresh build");
  write(d, "lib/b.js", "/* module b, changed */\nrequire('./c.js');\n");
  const chk = cli(d, ["check", "--no-hygiene"]);
  ok(chk.status === 1 && /stale/.test(chk.stdout) && /file:lib\/b\.js/.test(chk.stdout), "a changed source fails check and names the source that moved", chk.stdout);
  const st = cli(d, ["stale"]);
  ok(st.status === 1 && /~ file:lib\/b\.js/.test(st.stdout), "stale lists the changed source and the stale packs");
  const b = cli(d, ["build", "--affected"]);
  ok(b.status === 0 && /all within the prediction/.test(b.stdout), "build --affected: every regenerated pack was predicted by reverse traversal", b.stdout);
  const after = P.generate(d).files;
  const changed = [...after.keys()].filter(k => before.get(k) !== after.get(k));
  ok(changed.includes("_context/packs/code--1.md"), "the pack describing the changed source and its dependent (a requires b) changed");
  ok(before.get("_context/packs/docs--1.md") === after.get("_context/packs/docs--1.md") && before.get("_context/packs/orientation--1.md") === after.get("_context/packs/orientation--1.md"), "packs unrelated to the change are byte-identical");
  ok(cli(d, ["check", "--no-hygiene"]).status === 0, "after the rebuild the check passes again");
  fs.unlinkSync(path.join(d, "_context/packs/docs--1.md"));
  ok(/missing\s+_context\/packs\/docs--1\.md/.test(cli(d, ["stale"]).stdout), "a deleted pack is detected as missing");
  cli(d, ["build"]);
  write(d, "_context/packs/ghost--1.md", "x");
  ok(/orphaned _context\/packs\/ghost--1\.md/.test(cli(d, ["stale"]).stdout), "an orphaned pack file is detected");
  cli(d, ["build"]);
  ok(!fs.existsSync(path.join(d, "_context/packs/ghost--1.md")), "build removes orphaned pack files");
  write(d, "lib/new.js", "/* new */\n");
  const bn = cli(d, ["build", "--affected"]);
  ok(bn.status === 0 && /1 added/.test(bn.stdout), "an added artifact is registered and regenerated incrementally", bn.stdout);
  /* a NEW pack (the empty optional history unit gains a member) must not ripple
     through every other pack: only its sequence neighbours change */
  const pre = new Map(P.generate(d).files);
  write(d, "old/note.md", "# Old note\n\nkept for audit\n");
  const bh = cli(d, ["build", "--affected"]);
  const post = P.generate(d).files;
  ok(bh.status === 0 && /all within the prediction/.test(bh.stdout), "adding a pack regenerates only predicted packs", bh.stdout);
  ok(post.has("_context/packs/history--1.md") && pre.get("_context/packs/orientation--1.md") === post.get("_context/packs/orientation--1.md") && pre.get("_context/packs/code--1.md") === post.get("_context/packs/code--1.md"), "packs that are not neighbours of the new pack stay byte-identical");
  write(d, "AGENTS.md", "# Agents\n\nNever do X.\n");
  const bq = cli(d, ["build"]);
  ok(bq.status === 1 && /CONSTRAINT_QUOTE_MISSING/.test(bq.stdout), "build refuses to generate when a source change invalidates a binding quote (fail closed)");
}

console.log("\n▸ §F LIFECYCLE AND SUPERSESSION");
{
  const files = { "docs/old.md": "# [SUPERSEDED]\n\nReplaced by the guide.\n" };
  const g = P.generate(makeRepo(files));
  ok(errs(g, "SUPERSESSION_UNRECORDED").length === 1, "a superseded artifact without a supersession record is an error");
  const spec = baseSpec();
  spec.supersessions.push({ id: "SUP-T", artifact: "docs/old.md", successors: ["docs/guide.md"], effective: "r1", reason: "merged", disposition: "all content now in the guide", referenceMigration: "none", retention: "not required" });
  const g2 = P.generate(makeRepo(files, spec));
  ok(!errs(g2).length && g2.graph.edges.some(e => e.type === "supersedes" && e.from === "file:docs/guide.md" && e.to === "file:docs/old.md"), "a recorded supersession becomes an explicit successor → old edge");
  ok(g2.packs.some(p => p.text.includes("**superseded** (SUP-T")), "the pack shows the successor, reason, disposition and retention");
  delete spec.supersessions[0].disposition;
  ok(errs(P.generate(makeRepo(files, spec)), "SUPERSESSION_INCOMPLETE").length === 1, "an incomplete supersession record is an error");
  const s3 = baseSpec(); s3.supersessions.push({ id: "SUP-A", artifact: "docs/guide.md", successors: ["AGENTS.md"], effective: "r", reason: "r", disposition: "d", referenceMigration: "m", retention: "r" });
  ok(errs(P.generate(makeRepo({}, s3)), "SUPERSEDED_STILL_ACTIVE").length === 1, "a supersession record on an artifact still classed active is an error");
}

console.log("\n▸ §G BOOTSTRAP RECEIPTS");
{
  const d = makeRepo();
  cli(d, ["build"]); gitIn(d, ["add", "-A"]); gitIn(d, ["commit", "-qm", "ctx"]);
  const plan = cli(d, ["bootstrap", "--task", "lib/a.js", "--json"]);
  const r = JSON.parse(plan.stdout);
  ok(plan.status === 0 && r.status === "READY" && r.repository.commit && r.registry.fresh, "bootstrap identifies the repository, verifies the manifest and returns READY with a plan");
  const ids = r.plan.flatMap(s => s.packs.map(p => p.id));
  ok(ids.includes("orientation/1") && ids.includes("code/1") && r.governing.includes("LAW-X"), "the plan lists the packs and the governing constraints for the task");
  const miss = cli(d, ["bootstrap", "--task", "lib/a.js", "--loaded", "orientation/1"]);
  ok(miss.status === 2 && /REFUSE/.test(miss.stdout) && /not loaded: code\/1/.test(miss.stdout), "a receipt missing a mandatory pack is REFUSE and names what is missing", miss.stdout);
  const wrong = cli(d, ["bootstrap", "--task", "lib/a.js", "--loaded", ids.map(id => id + "@000000000000").join(",")]);
  ok(wrong.status === 2 && /do not match/.test(wrong.stdout), "a receipt claiming a stale copy (digest mismatch) is REFUSE");
  const good = cli(d, ["bootstrap", "--task", "lib/a.js", "--json", "--loaded", r.plan.flatMap(s => s.packs.map(p => p.id + "@" + p.digest)).join(",")]);
  ok(good.status === 0 && JSON.parse(good.stdout).status === "ASSIMILATED", "a complete receipt is ASSIMILATED");
  write(d, "lib/c.js", "/* changed */\n");
  const stale = cli(d, ["bootstrap", "--task", "lib/a.js"]);
  ok(stale.status === 2 && /stale/.test(stale.stdout), "bootstrap refuses when the generated context is stale");
}

console.log("\n▸ §H HANDOFFS — append-only, hash-chained, resumable by a fresh process");
{
  const d = makeRepo();
  cli(d, ["build"]); gitIn(d, ["add", "-A"]); gitIn(d, ["commit", "-qm", "ctx"]);
  const start = gitIn(d, ["rev-parse", "HEAD"]);
  write(d, "lib/c.js", "/* module c v2 */\nmodule.exports = 2;\n");
  cli(d, ["build"]); gitIn(d, ["add", "-A"]); gitIn(d, ["commit", "-qm", "work"]);
  const draft = { objective: "Change module c to export two", status: "interrupted", authority: { instruction: "fixture owner request", governedBy: ["LAW-X"] }, context: { packsUsed: ["orientation/1", "code/1"], sourcesUsed: ["lib/c.js"] }, asserted: { decisions: [], results: ["c exports 2"], failures: [], limitations: [], risks: [], unresolved: ["b is untested"], notDone: ["tests for b"] }, resume: { prerequisites: ["lib/b.js"], nextAction: "Write a test for lib/b.js and run it" }, references: {} };
  const draftFile = path.join(TMP, "draft-" + fx + ".json");
  fs.writeFileSync(draftFile, JSON.stringify(draft));
  const tmpl = JSON.parse(cli(d, ["handoff", "--template"]).stdout);
  ok(tmpl.resume && tmpl.asserted && Array.isArray(tmpl.asserted.notDone), "the handoff template separates asserted claims from the resume contract");
  const bad = Object.assign({}, draft, { resume: { prerequisites: [], nextAction: "" } });
  const badFile = path.join(TMP, "bad-" + fx + ".json");
  fs.writeFileSync(badFile, JSON.stringify(bad));
  const hb = cli(d, ["handoff", "--task", "TASK-1", "--draft", badFile, "--start", start]);
  ok(hb.status === 1 && /nextAction/.test(hb.stdout) && !fs.existsSync(path.join(d, "_registry/handoffs/TASK-1")), "an incomplete handoff is rejected and nothing is written");
  const h1 = cli(d, ["handoff", "--task", "TASK-1", "--draft", draftFile, "--start", start, "--verify", "node test/t.js"]);
  ok(h1.status === 0 && fs.existsSync(path.join(d, "_registry/handoffs/TASK-1/0001.json")), "a complete handoff is appended and the context regenerated", h1.stdout);
  const rec = JSON.parse(fs.readFileSync(path.join(d, "_registry/handoffs/TASK-1/0001.json"), "utf8"));
  ok(rec.verified.revisions.start === start && rec.verified.changedFiles.some(f => f.path === "lib/c.js") && rec.verified.commands[0].exitCode === 0, "verified facts (revisions, changed files, command exit codes) are tool-produced");
  gitIn(d, ["add", "-A"]); gitIn(d, ["commit", "-qm", "handoff"]);
  /* a FRESH process, no shared state, no conversation: only the repository */
  const res = cli(d, ["resume", "TASK-1"]);
  ok(res.status === 0 && /READY/.test(res.stdout) && /Write a test for lib\/b\.js/.test(res.stdout) && /b is untested/.test(res.stdout) && /code\/1/.test(res.stdout), "a fresh process resumes from repository state alone: objective, unresolved items, next action, packs to load", res.stdout);
  const draft2 = path.join(TMP, "draft2-" + fx + ".json");
  fs.writeFileSync(draft2, JSON.stringify(Object.assign({}, draft, { status: "completed", resume: { prerequisites: [], nextAction: "Nothing further; task complete" } })));
  const h2 = cli(d, ["handoff", "--task", "TASK-1", "--draft", draft2, "--start", start]);
  const r2 = JSON.parse(fs.readFileSync(path.join(d, "_registry/handoffs/TASK-1/0002.json"), "utf8"));
  ok(h2.status === 0 && r2.previousDigest === G.sha256(fs.readFileSync(path.join(d, "_registry/handoffs/TASK-1/0001.json"))), "the second record chains to the first by digest");
  const g = P.generate(d);
  ok(g.graph.edges.some(e => e.type === "continues" && e.to.endsWith("0001.json")) && g.graph.nodes.get("file:_registry/handoffs/TASK-1/0001.json").lifecycle === "historical-evidence", "records are linked (continues / hands-off-to); superseded records become historical evidence");
  const f1 = path.join(d, "_registry/handoffs/TASK-1/0001.json");
  fs.writeFileSync(f1, fs.readFileSync(f1, "utf8").replace("c exports 2", "c exports 3"));
  const tampered = cli(d, ["resume", "TASK-1"]);
  ok(tampered.status === 2 && /hash chain broken/.test(tampered.stdout), "editing a past record breaks the chain: resume refuses", tampered.stdout);
  ok(errs(P.generate(d), "HANDOFF_INVALID").length >= 1, "and validation reports HANDOFF_INVALID");
  ok(cli(d, ["resume", "NOPE"]).status === 2, "resuming a task with no records refuses");
}

console.log("\n▸ §I HYGIENE — duplication, deprecated references, drift, ratchet");
{
  const body = Array.from({ length: 20 }, (_, i) => "Requirement " + i + " is stated here in full sentence form.").join("\n");
  const spec = baseSpec();
  spec.supersessions.push({ id: "SUP-H", artifact: "docs/old.md", successors: ["docs/guide.md"], effective: "r", reason: "r", disposition: "d", referenceMigration: "m", retention: "r" });
  spec.hygiene.derivedChecks.push({ id: "DRV-T", generator: "gen.js", copy: ["gen.js", "out/**"], outputs: { class: "generated" } });
  spec.hygiene.thresholds = { nearDuplicatePairs: 0 };
  const d = makeRepo({
    "docs/one.md": "# One\n\n" + body + "\n", "docs/two.md": "# Two\n\n" + body + "\nOne extra line that only two has.\n",
    "docs/old.md": "# [SUPERSEDED]\n\nold\n", "docs/uses-old.md": "# Uses\n\nSee old.md for details.\n",
    "gen.js": "require('fs').writeFileSync(require('path').join(__dirname,'out','o.md'),'fresh\\n');\n", "out/o.md": "stale\n"
  }, spec);
  const gen = P.generate(d);
  const h = H.analyze(d, gen, {});
  ok(h.nearDuplicates.some(p => [p.a, p.b].sort().join() === "file:docs/one.md,file:docs/two.md"), "near-duplicate documents are detected (line-level)");
  ok(h.plan.some(p => p.category === "near-duplicate" && p.authorization), "the plan proposes consolidation and marks it as needing authorization");
  ok(h.deprecatedReferences.some(r => r.from === "file:docs/uses-old.md" && r.to === "file:docs/old.md"), "a reference from active text to a superseded artifact is found");
  ok(h.metrics.derivedDrift === 1 && h.plan.some(p => p.category === "derived-drift"), "a generated artifact that drifted from its generator is detected");
  ok(fs.readFileSync(path.join(d, "out/o.md"), "utf8") === "stale\n", "the drift check never writes into the repository");
  ok(h.findings.some(f => f.code === "HYGIENE_REGRESSION" && f.subject === "nearDuplicatePairs"), "a metric above its ratchet threshold is a regression");
  ok(fs.existsSync(path.join(d, "docs/two.md")) && fs.existsSync(path.join(d, "docs/old.md")), "hygiene deletes nothing");
  const rh = H.analyze(ROOT, real, {});
  ok(!rh.findings.length, "the repository meets every ratchet threshold", rh.ratchet.filter(r => r.verdict === "regression"));
  ok(rh.metrics.derivedDrift === 93 && rh.plan[0].category === "derived-drift", "the repository's known projection drift (CNF-001) is measured, not hidden, and ranked first");
  const search = cli(ROOT, ["search", "Master-Architecture"]);
  ok(/\[(SUPERSEDED|HISTORICAL-EVIDENCE) — not an active requirement\]/.test(search.stdout), "search labels superseded/historical results so they are never mistaken for requirements");
}

console.log("\n" + (failed ? "✗" : "✓") + " context: " + passed + " passed, " + failed + " failed");
process.exitCode = failed ? 1 : 0;
