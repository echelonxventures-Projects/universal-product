/* LUXORA Platform — technology governance (lib/technology.js, PR-053).
   On a throwaway database:
     · the registry imports the declaration: the baseline resolves exactly what CI ran on
       2ff2b4a, and the lock it gives is the committed technology.lock.json, byte for byte, twice
     · a new category, a new source and a new adapter are registered at run time, and their
       releases are kernel nodes of the same kind — no new kind, no new table, no core change
     · discovery records facts only: a newly reported release is never approved, never resolved,
       and never changes the lock; untrusted, malformed, oversized, polluting, off-contract and
       tampered entries are refused, each held with its reason in the kernel's event log
     · evaluation is computed and recorded: a release without its evidence is compatible, not
       verified; a production use refuses a runtime a security release has superseded
     · approval and activation are kernel changes: refused without the approve grant, refused
       when the approver is the author, refused while unverified; published, the release is
       active; a resolution cannot name what is not approved
     · deprecation and replacement keep the history, and a rollback restores the state before
     · the repository gate: an undeclared assumption, a violation class, an exception without
       an approval and a stale entry fail; a declared technical minimum does not; the CI
       workflow, the Dockerfile and the engine range are validated against the lock
     · an artifact is verified by its recorded digest; the runtime check reads the lock
   And the money policy's changes and the technology changes never mix. */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os"), crypto = require("crypto");
const { spawnSync } = require("child_process");
const ROOT = path.join(__dirname, "..");
const DB = path.join(__dirname, "technology.db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
Object.assign(process.env, { LX_DB: DB, LX_TEST: "1", LX_QUIET: "1" });
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)).slice(0, 900) : ""))); };
const throws = (fn, re, n) => { try { fn(); ok(false, n, "did not throw"); } catch (e) { ok(re.test(e.message) || re.test(e.code || ""), n, (e.code || "") + " " + e.message); } };

const quiet = console.log; console.log = () => { };
const D = require("../lib/db.js");
console.log = quiet;
const T = require("../lib/technology.js");
const S = require("../lib/technology-scan.js");
const AD = require("../lib/technology-adapters.js");
const K = require("../lib/kernel.js");
const SEED = T.SEED;
const GRANT = [K.SEED.lifecycle.approvePermission];
const count = (sql, ...a) => D.get(sql, ...a).n;

console.log("▸ THE BASELINE AND THE LOCK");
T.ensure();
const lockFile = fs.readFileSync(path.join(ROOT, SEED.lock), "utf8");
const first = T.lockText(), again = T.lockText();
ok(first === again, "the lock is deterministic: the same registry gives the same bytes");
ok(first === lockFile, "the committed technology.lock.json is what the registry resolves (no drift)");
const lock = JSON.parse(first);
ok(J(lock.resolutions["ci.test"].releases.map(r => r.key)) === J(["node@22.13.1", "node@22.23.4", "node@24.22.1"]), "ci.test resolves the three runtimes CI ran on 2ff2b4a", lock.resolutions["ci.test"].releases.map(r => r.key));
ok(lock.ci.test.find(l => l.primary).release === "node@22.23.4" && lock.ci.node === "22.23.4", "the primary lane and the browser/postgres runtime are derived from the production image's runtime");
ok(lock.constraints["platform.runtime"].floor === "22.13.0", "the runtime floor is derived from the capabilities required (node:sqlite since 22.13.0)");
ok(/@sha256:[0-9a-f]{64}$/.test(lock.ci.postgres) && /@sha256:[0-9a-f]{64}$/.test(lock.ci.container), "images resolve to digests, not floating tags");
ok(Object.values(lock.ci.actions).every(a => /@[0-9a-f]{40}$/.test(a)), "actions resolve to commits");
ok(lock.resolutions["ci.test"].releases.every(r => r.artifacts.every(a => a.platform === "linux-x64" && /^[0-9a-f]{64}$/.test(a.sha256)) && r.evidence.length >= 2), "each resolved lane carries its artifact digest and two CI evidence records");
function J(v) { return JSON.stringify(v); }

console.log("▸ DISCOVERY IS NOT APPROVAL");
const n26 = T.release("node@26.13.0");
ok(n26 && n26.state === "compatible", "node@26.13.0, reported by the release index, is compatible — not verified, not approved", n26 && n26.state);
ok(!lock.resolutions["ci.test"].releases.some(r => r.key === "node@26.13.0") && lock.ci.test.some(l => l.release === "node@26.13.0" && l.evaluation), "it is an evaluation lane, not a resolved one");
const n2214 = T.release("node@22.14.0");
ok(n2214 && n2214.state === "under-evaluation" && n2214.evaluation.checks.some(c => c.check === "integrity" && !c.ok), "a release with no artifact digest stays under evaluation", n2214 && n2214.state);
ok(T.release("node@22.13.1").evaluation.uses[0].advisory.some(a => /engine ranges/.test(a.check) && /jsdom/.test(a.detail)), "the development tooling's narrower engine ranges are recorded against 22.13.1 as a finding");

console.log("▸ A NEW CATEGORY, SOURCE AND ADAPTER USE THE SAME CORE");
const kindsBefore = count("SELECT COUNT(*) AS n FROM k_kinds WHERE rec_to IS NULL");
const tablesBefore = count("SELECT COUNT(*) AS n FROM sqlite_master WHERE type='table'");
T.defineCategory({ key: "inference-accelerator", label: "Inference accelerator", scheme: "dotted",
  contract: { integrity: "required", attributes: [{ key: "precision", type: "list", required: true }, { key: "memoryGb", type: "number" }] } }, "test.author");
T.registerScheme("calendar", { valid: v => /^\d{4}\.\d{2}$/.test(v), compare: (a, b) => a < b ? -1 : a > b ? 1 : 0, line: v => v.slice(0, 4), satisfies: (v, r) => v >= r.replace(/^>=/, "") });
T.defineCategory({ key: "signal-codec", label: "A category with its own version scheme", scheme: "calendar" }, "test.author");
AD.register("vendor-feed", { discover: p => p.map(x => ({ item: "accel-x", version: x.v, artifacts: [{ name: x.file, sha256: x.sha }], metadata: x.meta })) });
T.registerSource({ key: "accel-feed", protocol: "vendor-feed", trust: "authoritative", location: "https://accel.invalid/releases.json" });
T.defineItem({ key: "accel-x", category: "inference-accelerator", label: "Accelerator X", sources: ["accel-feed"] }, "test.author");
const sha = crypto.createHash("sha256").update("artifact bytes").digest("hex");
const ing = T.ingest("accel-feed", { entries: [{ v: "1.2.0", file: "accel-1.2.0.bin", sha, meta: { precision: ["fp8", "int4"], memoryGb: 96 } }], fetchedAt: "2026-10-29T00:00:00Z", payloadSha256: sha });
ok(ing.accepted.length === 1 && T.release("accel-x@1.2.0").state === "discovered", "a release of a category the core never named is ingested and discovered", ing);
ok(count("SELECT COUNT(*) AS n FROM k_kinds WHERE rec_to IS NULL") === kindsBefore && count("SELECT COUNT(*) AS n FROM sqlite_master WHERE type='table'") === tablesBefore, "no new kernel kind and no new table: categories are nodes of one kind");
ok(D.get("SELECT kind FROM k_nodes WHERE uid=?", T.release("accel-x@1.2.0").uid).kind === SEED.kinds.release.kind, "its release is a node of the same release kind every technology uses");
const ev = T.evaluate("accel-x@1.2.0");
ok(ev.state === "compatible" && !["approved", "active"].includes(T.release("accel-x@1.2.0").state), "evaluated, it is compatible with its contract — still not approved", ev.state);
ok(T.lockText() === first, "the lock is unchanged by discovery and evaluation");
/* a second package ecosystem: its resolution introduces library items under another name, and the
   licence policy and the engine ranges apply to them as they do to the first — by category, not name */
AD.register("other-resolution", { discover: p => p.map(x => ({ item: "pkg:" + x.name, version: x.v, newItem: { key: "pkg:" + x.name, category: "library", label: x.name, sources: ["other-lock"] },
  artifacts: [{ name: x.name, sha256: sha }], metadata: { scope: "runtime", licence: x.licence, engines: { node: x.engines } } })) });
T.registerSource({ key: "other-lock", protocol: "other-resolution", trust: "generated-resolution", category: "library" });
T.ingest("other-lock", { entries: [{ name: "closed-lib", v: "1.0.0", licence: "LicenseRef-Proprietary", engines: ">=0" }, { name: "open-lib", v: "2.0.0", licence: "MIT", engines: ">=99" }] });
const closed = T.evaluate("pkg:closed-lib@1.0.0");
ok(closed.state === "rejected" && closed.checks.some(c => c.check === "licence" && !c.ok), "a library of another ecosystem with a licence the policy does not allow is rejected", closed.checks);
ok(T.evaluate("node@26.13.0").uses.find(u => u.use === "ci.test").checks.some(c => /engine ranges/.test(c.check) && !c.ok && /pkg:open-lib/.test(c.detail)), "and its engine range counts against a runtime like any other runtime library");
/* both are removed from the runtime scope again so the baseline's verdicts below are unaffected */
for (const k of ["pkg:closed-lib@1.0.0", "pkg:open-lib@2.0.0"]) K.record(T.release(k).uid, { metadata: { scope: "development", licence: "MIT" } }, {}, "test.author");
T.evaluate("node@26.13.0");
throws(() => T.defineCategory({ key: "x-thing", scheme: "no-such-scheme" }), /version scheme/, "a category names a registered version scheme");
throws(() => T.registerSource({ key: "nowhere", protocol: "no-adapter", trust: "authoritative" }), /No adapter/, "a source needs an adapter for its protocol");

console.log("▸ UNTRUSTED OR INVALID METADATA IS REFUSED, WITH A REASON");
throws(() => T.ingest("no-such-source", { entries: [] }), /Unknown source/, "an undeclared source is refused");
T.registerSource({ key: "gossip", protocol: "vendor-feed", trust: "untrusted" });
throws(() => T.ingest("gossip", { entries: [] }), /not trusted/, "a source at an untrusted level reports nothing");
T.registerSource({ key: "accel-mirror", protocol: "vendor-feed", trust: "authoritative" });
const bad1 = T.ingest("accel-mirror", { entries: [{ v: "1.3.0", file: "a.bin", sha, meta: { precision: ["fp8"] } }] });
ok(bad1.rejected.length === 1 && /not allowed to report/.test(bad1.rejected[0].reason), "a source the item does not list may not report its releases", bad1.rejected);
const bad = T.ingest("accel-feed", { entries: [
  { v: "not a version", file: "a.bin", sha, meta: { precision: ["fp8"] } },
  { v: "1.4.0", file: "a.bin", sha: "abc", meta: { precision: ["fp8"] } },
  { v: "1.5.0", file: "a.bin", sha, meta: { precision: ["fp8"], wattage: 700 } },
  { v: "1.6.0", file: "a.bin", sha, meta: { precision: "fp8" } },
  { v: "1.7.0", file: "a.bin", sha, meta: JSON.parse('{"precision":["fp8"],"x-note":{"__proto__":{"polluted":true}}}') },
  { v: "1.8.0", file: "a.bin", sha, meta: { precision: ["fp8"], "x-blob": "y".repeat(70000) } },
  { v: "1.2.0", file: "accel-1.2.0.bin", sha: "0".repeat(64), meta: { precision: ["fp8"] } }
] });
const why = bad.rejected.map(r => r.reason).join(" | ");
ok(bad.accepted.length === 0 && bad.rejected.length === 7, "all seven bad entries are refused, none recorded", bad);
ok(/not a dotted version/.test(why) && /not a valid digest/.test(why) && /declares no metadata wattage/.test(why) && /must be list/.test(why) && /forbidden key __proto__/.test(why) && /larger than/.test(why) && /changed its sha256/.test(why),
  "each for its reason: version, digest, off-contract field, wrong type, prototype pollution, size, tampered artifact", why);
ok(({}).polluted === undefined, "nothing was polluted");
ok(bad.rejected.find(r => /changed its sha256/.test(r.reason)).code === "technology_tampered" && T.release("accel-x@1.2.0").artifacts[0].sha256 === sha, "a changed digest for a known artifact is tampering, and the recorded digest stands");
const held = T.rejections(50).filter(r => r.source === "accel-feed");
ok(held.length >= 7 && held.every(r => r.reason && r.seq), "the refusals are held in the kernel's hash-chained event log with their reasons");
ok(K.verifyEvents().ok !== false, "the event log still verifies");
ok(AD.protocols().includes("release-index") && typeof AD.adapter("release-index").fetch === "function", "the release-index adapter can fetch");
(async () => {
  let refused = null;
  try { await AD.adapter("release-index").fetch({ location: "http://127.0.0.1:1/index.json" }); } catch (e) { refused = e.message; }
  ok(/https sources only/.test(refused || ""), "discovery reads https sources only — no plain-http or internal endpoint", refused);
  try { await AD.adapter("checksum-list").fetch({ location: "https://x.invalid/v{version}/S" }, { versions: ["../../etc"] }); refused = null; } catch (e) { refused = e.message; }
  ok(/Not a release version/.test(refused || ""), "a version substituted into a source's location is validated first", refused);
  rest();
})();

function rest() {
  console.log("▸ EVALUATION IS RECORDED AND AUDITABLE");
  const h = T.history("release", "node@26.13.0");
  ok(h.some(v => v.attributes.state === "discovered") && h.some(v => v.attributes.state === "compatible") && h.every(v => v.recordedBy), "the release's path (discovered → candidate → compatible) is in k_versions with who recorded each step", h.map(v => v.attributes.state + ":" + v.recordedBy));
  const rep = T.release("node@26.13.0").evaluation;
  ok(rep.checks.length >= 4 && rep.uses[0].checks.some(c => /node:sqlite/.test(c.check) && c.ok) && rep.uses[0].evidence.some(e => e.kind === "ci-suite" && !e.ok), "the report says what passed and what is missing (the CI suite evidence)", rep.uses[0]);

  console.log("▸ APPROVAL AND ACTIVATION ARE GOVERNED");
  throws(() => T.proposeResolution("ci.test", ["node@22.13.1", "node@22.23.4", "node@24.22.1", "node@26.13.0"], {}, "test.author"), /technology_state|only an approved/i, "a resolution cannot name a release that is not approved");
  throws(() => T.proposeTransition("node@26.13.0", "approved", {}, "test.author"), /Only a verified/, "an unverified release cannot be proposed for approval");
  T.addEvidence("node@26.13.0", { kind: "ci-suite", outcome: "pass", ref: "test evidence: a passing run", commit: "0".repeat(40) }, "test.ci");
  ok(T.evaluate("node@26.13.0").state === "verified", "with the evidence its use requires, evaluation moves it to verified — and no further");
  const c = T.proposeTransition("node@26.13.0", "approved", { reason: "verified for ci.test" }, "test.author");
  ok(c.state === "draft" && T.release("node@26.13.0").state === "verified", "the approval is a drafted kernel change; nothing moved yet");
  throws(() => T.approve(c.id, "test.approver", []), /permission/, "approving needs the approve grant");
  throws(() => T.approve(c.id, "test.author", GRANT), /other than its author/, "the author cannot approve their own change");
  throws(() => T.publish(c.id, "test.approver"), /Only an approved change/, "an unapproved change cannot be published");
  T.approve(c.id, "test.approver", GRANT); T.publish(c.id, "test.approver");
  ok(T.release("node@26.13.0").state === "approved", "approved by someone else and published, the release is approved");
  const r1 = T.proposeResolution("ci.test", ["node@22.13.1", "node@22.23.4", "node@24.22.1", "node@26.13.0"], { reason: "add the 26 line" }, "test.author");
  T.approve(r1.id, "test.approver", GRANT); T.publish(r1.id, "test.approver");
  ok(T.release("node@26.13.0").state === "active" && T.resolution("ci.test").releases.length === 4, "resolving it is one change: the resolution and the release's activation together");
  ok(!T.lanes("ci.test").some(r => r.key === "node@26.13.0"), "a resolved release is no longer an evaluation lane");
  T.rollback(r1.id, "test.approver");
  ok(T.release("node@26.13.0").state === "approved" && T.resolution("ci.test").releases.length === 3, "rolling the resolution back restores both the resolution and the release's state");
  /* a production use refuses a runtime a later security release superseded */
  T.ingest("container-registry", { entries: [{ repository: "node", tag: "22.13.1-alpine", digest: "sha256:" + "1".repeat(64), provides: { node: "22.13.1" } }] });
  const img = T.evaluate("node-image@22.13.1-alpine");
  const dv = img.uses.find(u => u.use === "deploy.container");
  ok(dv && !dv.compatible && dv.checks.some(x => x.check === "advisories" && !x.ok && /superseded-by-security-release/.test(x.detail)), "an image carrying 22.13.1 is not compatible with the production use (security advisory)", dv);
  ok(img.uses.find(u => u.use === "deploy.container").checks.find(x => x.check === "advisories").detail.includes("node@22.13.1"), "the advisory names the runtime the image carries");
  throws(() => T.proposeTransition("node-image@22.13.1-alpine", "approved", {}, "test.author"), /cannot go from under-evaluation to approved/, "and it cannot be approved (it never got past evaluation)");
  /* stale: two changes drafted against one state cannot both land */
  const s1 = T.proposeTransition("node@24.22.1", "deprecated", { reason: "a" }, "test.author");
  const s2 = T.proposeTransition("node@24.22.1", "prohibited", { reason: "b" }, "test.author");
  T.approve(s1.id, "test.approver", GRANT); T.publish(s1.id, "test.approver");
  throws(() => T.approve(s2.id, "test.approver", GRANT), /technology_stale|moved on|cannot go/, "a change drafted against a state that has moved on is refused");
  T.rollback(s1.id, "test.approver");

  console.log("▸ DEPRECATION AND REPLACEMENT KEEP HISTORY AND ROLLBACK");
  T.addEvidence("node@24.22.2", { kind: "ci-suite", outcome: "pass", ref: "test evidence: 24.22.2", commit: "0".repeat(40) }, "test.ci");
  T.evaluate("node@24.22.2");
  const a2 = T.proposeTransition("node@24.22.2", "approved", { reason: "replacement" }, "test.author"); T.approve(a2.id, "test.approver", GRANT); T.publish(a2.id, "test.approver");
  const dep = T.proposeTransition("node@24.22.1", "deprecated", { reason: "replaced by the next patch release", replacedBy: "node@24.22.2" }, "test.author");
  T.approve(dep.id, "test.approver", GRANT); T.publish(dep.id, "test.approver");
  ok(T.release("node@24.22.1").state === "deprecated" && T.release("node@24.22.1").replaced_by === "node@24.22.2", "deprecated, naming its replacement");
  ok(T.proposals().some(p => p.kind === "replace" && p.release === "node@24.22.1" && /24\.22\.2/.test(p.detail)), "a resolved deprecated release is proposed for replacement");
  const rep2 = T.proposeResolution("ci.test", ["node@22.13.1", "node@22.23.4", "node@24.22.2"], { reason: "replace 24.22.1" }, "test.author");
  T.approve(rep2.id, "test.approver", GRANT); T.publish(rep2.id, "test.approver");
  ok(J(T.resolution("ci.test").releases.map(r => r.key)) === J(["node@22.13.1", "node@22.23.4", "node@24.22.2"]), "the replacement is resolved");
  const hist = T.history("resolution", "ci.test");
  ok(hist.some(v => !v.current && v.attributes.releases.some(r => r.key === "node@24.22.1")) && hist.some(v => v.current && v.attributes.releases.some(r => r.key === "node@24.22.2")), "the resolution's history keeps the superseded version beside the current one");
  T.rollback(rep2.id, "test.approver"); T.rollback(dep.id, "test.approver");
  ok(T.resolution("ci.test").releases.some(r => r.key === "node@24.22.1") && T.release("node@24.22.1").state === "active", "rolled back in order, the replaced release is resolved and active again");
  ok(T.history("release", "node@24.22.1").some(v => v.attributes.state === "deprecated" && !v.current), "and its deprecation is still in the history, closed");
  const auto = T.autoPropose("technology.cycle");
  ok(auto.length >= 1 && auto.every(p => T.changes().find(c => c.id === p.drafted).state === "draft"), "the governance cycle drafts the ready upgrades — and leaves them for approval", auto);

  console.log("▸ THE MONEY POLICY'S CHANGES AND THE TECHNOLOGY CHANGES NEVER MIX");
  const MP = require("../lib/money-policy.js");
  const m = MP.propose({ policy: { rounding: "half-even" }, title: "test" }, "test.author");
  ok(!T.changes().some(c => c.id === m.id) && MP.changes().every(x => !T.changes().some(c => c.id === x.id)), "neither lists the other's changes");
  MP.discard(m.id, "test.author");

  console.log("▸ THE REPOSITORY GATE");
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "tech-gate-"));
  const put = (f, t) => { fs.mkdirSync(path.dirname(path.join(tmp, f)), { recursive: true }); fs.writeFileSync(path.join(tmp, f), t); };
  put("lib/a.js", 'const { DatabaseSync } = require("node:sqlite");\n/* require("node:test") in a comment is not an assumption */\n');
  put("Dockerfile", "# FROM nothing\nFROM node:22.23.4-alpine@sha256:" + "f".repeat(64) + "\n");
  const decl = { scan: SEED.scan, classes: SEED.classes, bootstrap: SEED.bootstrap, inventory: [
    { id: "X-1", detector: "module", tokens: ["node:sqlite"], files: ["**"], class: "technical-constraint", why: "the floor" },
    { id: "X-2", detector: "container-base", tokens: ["node:22.23.4-alpine@sha256:" + "f".repeat(64)], files: ["Dockerfile"], class: "consumes-resolution", why: "validated" }] };
  let g = S.gate(S.scan(tmp, decl), decl);
  ok(!g.errors.length, "a declared technical minimum and a validated base image raise nothing (commented-out text is not a finding)", g.errors);
  put("lib/b.js", "const t = " + "require" + '("node:test");\n');   /* split, or this file would be the finding */
  put("docker-compose.yml", "services:\n  q:\n    image: queue:latest\n");
  g = S.gate(S.scan(tmp, decl), decl);
  ok(g.errors.some(e => /undeclared.*node:test/.test(e)) && g.errors.some(e => /undeclared.*queue:latest/.test(e)), "a new module and a new image are undeclared assumptions", g.errors);
  put("lib/deep/er/c.mjs", "const v = " + "require" + '("node:vm");\n');
  ok(S.gate(S.scan(tmp, decl), decl).errors.some(e => /undeclared technology assumption: lib\/deep\/er\/c\.mjs:1 module "node:vm"/.test(e)), "a script in any directory, of any JavaScript extension, is scanned");
  fs.rmSync(path.join(tmp, "lib/deep"), { recursive: true, force: true });
  decl.inventory.push({ id: "X-3", detector: "module", tokens: ["node:test"], files: ["lib/b.js"], class: "unjustified-hardcoding", why: "to remove" });
  decl.inventory.push({ id: "X-4", detector: "container-image", tokens: ["queue:latest"], files: ["docker-compose.yml"], class: "documented-exception", why: "a demo" });
  g = S.gate(S.scan(tmp, decl), decl);
  ok(g.errors.some(e => /unjustified-hardcoding \(X-3\) — fix it/.test(e)) && g.errors.some(e => /X-4: a documented-exception needs a recorded approval/.test(e)), "declaring it does not excuse a violation, and an exception needs its approval", g.errors);
  decl.inventory[2].class = "technical-constraint";
  decl.inventory[3].approval = { by: "owner", at: "2026-10-29", reason: "demo compose file" };
  decl.inventory.push({ id: "X-5", detector: "module", tokens: ["node:gone"], files: ["**"], class: "technical-constraint", why: "was used once" });
  g = S.gate(S.scan(tmp, decl), decl);
  ok(g.errors.length === 1 && /X-5: stale/.test(g.errors[0]), "an approved exception passes; an entry nothing matches is stale", g.errors);
  ok(!S.gate(S.scan(ROOT, SEED), SEED).errors.length, "the repository itself passes the gate");
  /* consumers that cannot read the lock */
  put("package.json", JSON.stringify({ engines: { node: ">=22" } }));
  put(".github/workflows/ci.yml", fs.readFileSync(path.join(ROOT, ".github/workflows/ci.yml"), "utf8").replace("node-version: ${{ needs.resolve.outputs.node }}", "node-version: 22").replace(/actions\/checkout@[0-9a-f]{40}/, "actions/checkout@v5"));
  const cons = S.consumers(tmp, lock, SEED);
  ok(cons.some(e => /engines.node is >=22/.test(e)) && cons.some(e => /node-version 22 is written/.test(e)) && cons.some(e => /uses actions\/checkout@v5/.test(e)) && cons.some(e => /Dockerfile: FROM/.test(e)), "a literal runtime, a floating action, a different base image and a different engine range are drift", cons);
  ok(!S.consumers(ROOT, lock, SEED).length, "the repository's own workflow, Dockerfile and package.json agree with the lock");
  fs.rmSync(tmp, { recursive: true, force: true });

  console.log("▸ ARTIFACTS AND THE RUNTIME ARE VERIFIABLE");
  const art = path.join(os.tmpdir(), "tech-art-" + process.pid);
  fs.writeFileSync(art, "artifact bytes");
  ok(T.verifyArtifact("accel-x@1.2.0", "accel-1.2.0.bin", art).ok, "an artifact matching its recorded digest verifies");
  fs.writeFileSync(art, "artifact bytes, altered");
  ok(!T.verifyArtifact("accel-x@1.2.0", "accel-1.2.0.bin", art).ok, "an altered artifact does not");
  fs.rmSync(art, { force: true });
  const here = "node@" + process.versions.node, inLock = lock.ci.test.some(l => l.release === here);
  const vr = spawnSync(process.execPath, [path.join(ROOT, "scripts", "technology.js"), "verify-runtime", here], { encoding: "utf8" });
  ok(vr.status === (inLock ? 0 : 1), `verify-runtime ${here}: ${inLock ? "a resolved lane passes" : "not a resolved lane, refused"}`, vr.stdout + vr.stderr);
  const vx = spawnSync(process.execPath, [path.join(ROOT, "scripts", "technology.js"), "verify-runtime", "node@0.0.1"], { encoding: "utf8" });
  ok(vx.status === 1, "a release the lock does not resolve is refused");

  for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
  console.log(`\n${passed} passed, ${failed} failed`);
  process.exit(failed ? 1 : 0);
}
