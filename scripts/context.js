#!/usr/bin/env node
/* Context continuity · command line.
   --------------------------------------------------------------------------
   One entry point for every continuity operation; package.json exposes each as
   `npm run context:<command> -- <args>`. Plain text for people, --json for CI and
   agent orchestration.

   Exit codes:  0 ok (warnings may be printed — they are never "success")
                1 a correctness invariant failed
                2 the assimilation gate is blocked
                3 usage error */
"use strict";

const fs = require("fs");
const path = require("path");
const ROOT = path.resolve(process.env.CONTEXT_ROOT || path.join(__dirname, ".."));
const ctx = require(path.join(__dirname, "..", "lib", "context"));
const U = require(path.join(__dirname, "..", "lib", "context", "util.js"));
const P = require(path.join(__dirname, "..", "lib", "context", "packs.js"));
const A = require(path.join(__dirname, "..", "lib", "context", "archive.js"));
const C = require(path.join(__dirname, "..", "lib", "context", "coverage.js"));
const H = require(path.join(__dirname, "..", "lib", "context", "hygiene.js"));
const Gr = require(path.join(__dirname, "..", "lib", "context", "graph.js"));
const Pr = require(path.join(__dirname, "..", "lib", "context", "protocol.js"));

const USAGE = `usage: node scripts/context.js <command> [args]

  build [--full]                     regenerate packs, task packs and views (incremental by default)
  index                              alias of build (the master index is part of every build)
  verify [--json]                    CI gate: schema, ids, owners, graph, archive, freshness, drift, secrets
  assimilate <TASK> [--agent A] [--budget BYTES] [--write] [--json]
                                     the context gate; --write records a receipt in PROJECT-CONTEXT/receipts/
  task <TASK> [--budget BYTES] [--out DIR]
                                     print the task pack; with --out, also write the packs split at BYTES
  handoff <TASK> --from FILE.json [--agent A] [--dry-run]
                                     validate and record a durable handoff, update the task, rebuild
  query <name> [id] [--json]         graph queries (see 06-DEPENDENCY-AND-TRACEABILITY.md)
  hygiene [--json] [--write]         duplicates, near-duplicates, broken links, oversized files, knowledge hygiene
  coverage [--json] [--write]        coverage and traceability metrics with formulas
  restore-check [--dest DIR] [--keep] [--json]
                                     restore every preserved source into an isolated dir and verify checksums
  capture <repo-path> [--id SRC-…]   archive the current bytes of a repository file as a new source version
  capture-history <commit> [--id SRC-…] [--dry-run]
                                     archive the full ancestry of a commit as ctx-git-history/1 (needs a non-shallow clone)
  import <file> --id SRC-… [--category C] [--sensitivity S] [--title T] [--redact-name] [--store DIR]
                                     copy an export/attachment into the write-once store (never into git)
  transition <ID> <state> --by NAME [--approve NAME] [--superseded-by ID] [--evidence TEXT]
  consolidate --plan FILE.json --by NAME [--approve NAME]`;

function parse(argv) {
  const a = { _: [], flags: {} };
  for (let i = 0; i < argv.length; i++) {
    const x = argv[i];
    if (x.startsWith("--")) {
      const k = x.slice(2);
      const nxt = argv[i + 1];
      if (nxt === undefined || nxt.startsWith("--")) a.flags[k] = true; else { a.flags[k] = nxt; i++; }
    } else a._.push(x);
  }
  return a;
}
const args = parse(process.argv.slice(2));
const cmd = args._[0];
const F = args.flags;
const asJSON = !!F.json;
function out(obj, text) { process.stdout.write(asJSON ? JSON.stringify(obj, null, 2) + "\n" : text + (text.endsWith("\n") ? "" : "\n")); }
function die(msg, code) { process.stderr.write("✗ " + msg + "\n"); process.exit(code == null ? 3 : code); }
const fmt = d => "  " + (d.level === "error" ? "✗" : d.level === "warn" ? "!" : "·") + " [" + d.code + "] " + d.message + (d.remedy ? "\n      → " + d.remedy : "");
function writeReport(name, obj) {
  const file = path.join(ROOT, U.CONTEXT_DIR, "verification", name);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, U.pretty(obj));
  return path.relative(ROOT, file);
}

try {
  switch (cmd) {
    case "build":
    case "index": {
      const r = ctx.build(ROOT, { full: !!F.full, force: !!F.force });
      if (!r.ok) { out(r, "✗ build refused:\n" + r.errors.map(fmt).join("\n")); process.exit(1); }
      out(r, "✓ context build (" + (F.full ? "full" : "incremental") + "): " + r.packs.length + " packs, " + r.written.length + " file(s) written, " + r.removed.length + " removed\n" +
        (r.invalidated.length ? "  invalidated before build:\n" + r.invalidated.map(s => "    " + s.id + " — " + s.reason + (s.detail ? " (" + s.detail + ")" : "")).join("\n") + "\n" : "  no pack was stale\n") +
        r.written.map(f => "  wrote PROJECT-CONTEXT/" + f).join("\n"));
      break;
    }
    case "verify": {
      const r = ctx.verify(ROOT);
      const text = (r.ok ? "✓ context verify passed" : "✗ context verify FAILED") + " — " + r.errors.length + " error(s), " + r.warnings.length + " warning(s), " + r.info.length + " note(s) · " +
        r.summary.nodes + " nodes · " + r.summary.edges + " edges · " + r.summary.packs + " packs · " + r.summary.sources + " sources\n" +
        r.errors.map(fmt).join("\n") + (r.errors.length ? "\n" : "") + r.warnings.map(fmt).join("\n") + (r.warnings.length ? "\n" : "") + r.info.map(fmt).join("\n");
      out(r, text);
      process.exit(r.ok ? 0 : 1);
    }
    case "assimilate": {
      const task = args._[1] || die("assimilate needs a task id");
      const { K, G } = ctx.open(ROOT);
      const receipt = Pr.assimilate(K, G, task, { agent: F.agent, budget: F.budget ? Number(F.budget) : undefined });
      let file = null;
      if (F.write) file = Pr.writeReceipt(K, receipt);
      out(Object.assign({ file }, receipt), "Assimilation " + (receipt.verdict === "blocked" ? "✗ BLOCKED" : receipt.verdict === "pass" ? "✓ PASS" : "! PASS WITH WARNINGS") + " — " + task + " @ " + receipt.budgetBytes + " B budget\n" +
        "Reading order:\n" + receipt.readingOrder.map((u, i) => "  " + (i + 1) + ". [" + u.step + "] " + u.ref + " (" + u.bytes + " B" + (u.estimatedTokens ? ", ~" + u.estimatedTokens + " tokens est." : "") + ")").join("\n") + "\n" +
        "Requirements: " + receipt.requirements.join(", ") + "\nDecisions: " + receipt.decisions.join(", ") + "\nConstraints: " + receipt.constraints.join(", ") + "\n" +
        (receipt.gaps.length ? "Gaps:\n" + receipt.gaps.map(g => "  " + (g.severity === "block" ? "✗" : "!") + " [" + g.code + "] " + g.message).join("\n") + "\n" : "Gaps: none\n") +
        (file ? "Receipt: " + path.relative(ROOT, file) : "Receipt not written (pass --write to record it)"));
      process.exit(receipt.verdict === "blocked" ? 2 : 0);
    }
    case "task": {
      const task = args._[1] || die("task needs a task id");
      const { K, G } = ctx.open(ROOT);
      if (!K.nodes.has(task)) die("unknown task " + task, 1);
      const budget = F.budget ? Number(F.budget) : K.config.budgets.defaultPackBytes;
      const rendered = P.renderAll(K, G, { budget });
      const tp = P.renderTaskPack(K, G, task, rendered, Pr.loadHandoffs(K));
      if (F.out) {
        const dir = path.resolve(String(F.out));
        if (dir.startsWith(path.resolve(ROOT) + path.sep)) die("--out must be outside the repository (generated committed packs live in PROJECT-CONTEXT/contexts)");
        fs.mkdirSync(path.join(dir, "contexts"), { recursive: true });
        fs.writeFileSync(path.join(dir, task + ".md"), tp.body);
        for (const p of rendered.packs) for (const part of p.parts) fs.writeFileSync(path.join(dir, part.file), part.body);
      }
      out({ task, budget, body: tp.body, packs: rendered.packs.map(p => ({ id: p.json.id, status: p.json.status, parts: p.json.parts })) }, tp.body);
      break;
    }
    case "handoff": {
      const task = args._[1] || die("handoff needs a task id");
      if (!F.from) die("handoff needs --from FILE.json");
      const input = JSON.parse(fs.readFileSync(path.resolve(String(F.from)), "utf8"));
      const { K, G } = ctx.open(ROOT);
      const r = Pr.handoff(K, G, task, input, { agent: F.agent, dryRun: !!F["dry-run"] });
      if (!r.ok) { out(r, "✗ handoff rejected:\n" + r.errors.map(e => "  - " + e).join("\n")); process.exit(1); }
      if (!r.dryRun) { const b = ctx.build(ROOT); if (!b.ok) { out(b, "✗ handoff written but rebuild failed"); process.exit(1); } }
      out(r, "✓ handoff " + r.handoff.id + (r.dryRun ? " (dry run, nothing written)" : " written; task " + task + " → " + r.handoff.state + "; context rebuilt"));
      break;
    }
    case "query": {
      const name = args._[1] || die("query needs a name");
      const { K, G } = ctx.open(ROOT);
      const extra = {};
      if (name === "stale-contexts") extra.packStatus = P.status(K, G);
      if (name === "unaccounted-segments") extra.coverage = C.segmentAccounting(K);
      const Q = Gr.queries(K, G, extra);
      if (!Q[name]) die("unknown query '" + name + "'; known: " + Object.keys(Q).join(", "));
      const res = Q[name](args._[2]);
      out({ query: name, arg: args._[2] || null, results: res }, name + (args._[2] ? " " + args._[2] : "") + " → " + res.length + " result(s)\n" + res.map(x => "  " + JSON.stringify(x)).join("\n"));
      break;
    }
    case "hygiene": {
      const { K, G } = ctx.open(ROOT);
      const files = H.scan(K);
      const kn = H.knowledge(K, G);
      const report = { schema: "ctx-hygiene/1", files: files.files, exactDuplicates: files.exactDuplicates, nearDuplicates: files.nearDuplicates, brokenLinks: files.brokenLinks, oversizedActive: files.oversizedActive, oversizedAny: files.oversizedAny, knowledge: kn, proposals: H.proposals(files), policy: "findings and proposals only — nothing is deleted or merged by this command" };
      const file = F.write ? writeReport("hygiene.json", report) : null;
      out(report, "Hygiene over " + files.files + " doc files (nothing deleted or merged):\n" +
        "  exact duplicate groups " + files.exactDuplicates.length + (files.exactDuplicates.length ? ": " + files.exactDuplicates.map(g => g.join(" = ")).join("; ") : "") + "\n" +
        "  near-duplicate pairs   " + files.nearDuplicates.length + "\n" + files.nearDuplicates.map(d => "    " + d.jaccard + "  " + d.files.join("  ~  ")).join("\n") + (files.nearDuplicates.length ? "\n" : "") +
        "  broken local links     " + files.brokenLinks.length + "\n" + files.brokenLinks.slice(0, 20).map(b => "    " + b.file + ":" + b.line + " → " + b.target + " (" + b.reason + ")").join("\n") + (files.brokenLinks.length ? "\n" : "") +
        "  oversized active files " + files.oversizedActive.length + " · oversized files overall " + files.oversizedAny.length + "\n" +
        "  knowledge: duplicate statements " + kn.duplicateStatements.length + " · untracked conflicts " + kn.conflicts.filter(c => !c.trackedBy).length + " · historical-as-authority " + kn.historicalAsAuthority.length + " · superseded in active packs " + kn.supersededInActive.length + " · missing owners " + kn.missingOwner.length + " · orphans " + kn.orphans.length +
        (file ? "\n  report: " + file : ""));
      break;
    }
    case "coverage": {
      const { K, G } = ctx.open(ROOT);
      const hyg = H.scan(K);
      let restore = null;
      try { restore = U.readJSON(path.join(ROOT, U.CONTEXT_DIR, "verification", "restore-check.json")); } catch (e) { }
      const cov = C.compute(K, G, { packStatus: P.status(K, G), handoffs: Pr.loadHandoffs(K), hygiene: hyg, restore });
      const report = Object.assign({}, cov, { unaccounted: undefined });
      const file = F.write ? writeReport("coverage.json", report) : null;
      out(report, "Coverage (numerator / denominator — formula):\n" + cov.metrics.map(m => "  " + m.name.padEnd(42) + (m.percent == null ? "—" : m.percent + "%").padStart(8) + "  " + m.numerator + "/" + m.denominator + "  — " + m.formula).join("\n") +
        "\nCounts: " + JSON.stringify(Object.fromEntries(Object.entries(cov.counts).filter(([k]) => !/Ids$/.test(k)))) + (file ? "\nreport: " + file : ""));
      break;
    }
    case "restore-check": {
      const { K } = ctx.open(ROOT);
      const r = A.restoreCheck(K, { dest: F.dest ? String(F.dest) : undefined, keep: !!F.keep, store: F.store });
      if (F.write) writeReport("restore-check.json", r);
      out(r, (r.ok ? "✓" : "✗") + " restore-check: " + r.restored + " restored and re-verified in an isolated directory, " + r.unavailable + " unavailable here, " + r.skipped + " skipped (not preserved), " + r.failed + " failed; live repository untouched\n" + r.results.filter(x => x.status !== "restored").map(x => "  " + x.id + ": " + x.status + " — " + (x.detail || "")).join("\n"));
      process.exit(r.ok ? 0 : 1);
    }
    case "capture": {
      const rel = args._[1] || die("capture needs a repository path");
      const { K } = ctx.open(ROOT);
      const r = A.captureRepoFile(K, rel, { id: F.id, dryRun: !!F["dry-run"] });
      if (r.unchanged) { out(r, "· " + rel + " is already archived as " + r.id + " (identical bytes)"); break; }
      if (!F["dry-run"]) ctx.build(ROOT);
      out(r, "✓ captured " + rel + " as " + r.record.id + (r.supersedes ? " (supersedes " + r.supersedes + ")" : "") + "\n  " + r.note);
      break;
    }
    case "capture-history": {
      const commit = args._[1] || die("capture-history needs a commit");
      const { K } = ctx.open(ROOT);
      const r = A.captureGitHistory(K, commit, { id: F.id, dryRun: !!F["dry-run"] });
      if (!F["dry-run"]) ctx.build(ROOT);
      out(Object.assign({}, r, { bytes: undefined }), "✓ " + (F["dry-run"] ? "would capture " : "captured ") + r.record.id + ": " + r.record.storage.commits + " commits, " + r.record.storage.bytes + " B, sha256 " + r.record.storage.sha256.slice(0, 16) + "… (" + r.record.storage.format + ")");
      break;
    }
    case "import": {
      const file = args._[1] || die("import needs a file");
      const { K } = ctx.open(ROOT);
      const r = A.importFile(K, file, { id: F.id, category: F.category, sensitivity: F.sensitivity, title: F.title, redactName: !!F["redact-name"], store: F.store, attachmentOf: F["attachment-of"], dryRun: !!F["dry-run"] });
      if (!F["dry-run"]) ctx.build(ROOT);
      out(r, "✓ imported " + r.record.id + " (" + r.record.storage.bytes + " B, sha256 " + r.record.storage.sha256.slice(0, 16) + "…, " + r.record.sensitivity + ") into the write-once store " + path.dirname(path.dirname(path.dirname(r.stored))) + " — the bytes are NOT in git");
      break;
    }
    case "transition": {
      const id = args._[1], to = args._[2];
      if (!id || !to) die("transition needs <ID> <state>");
      if (!F.by) die("transition needs --by <name>");
      const { K } = ctx.open(ROOT);
      const r = H.transition(K, id, to, { by: String(F.by), approvedBy: F.approve ? String(F.approve) : undefined, supersededBy: F["superseded-by"] ? String(F["superseded-by"]).split(",") : undefined, evidence: F.evidence ? String(F.evidence) : undefined });
      const b = ctx.build(ROOT);
      out({ transition: r, build: b }, "✓ " + id + ": " + r.from + " → " + r.to + "; context rebuilt (" + b.written.length + " file(s))");
      break;
    }
    case "consolidate": {
      if (!F.plan) die("consolidate needs --plan FILE.json");
      const plan = JSON.parse(fs.readFileSync(path.resolve(String(F.plan)), "utf8"));
      const { K } = ctx.open(ROOT);
      const r = H.consolidate(K, plan, { by: F.by ? String(F.by) : "unknown", approvedBy: F.approve ? String(F.approve) : undefined });
      if (r.applied) ctx.build(ROOT);
      out(r, r.ok ? (r.applied ? "✓ consolidation applied: " + r.transitions.map(t => t.id + " → " + t.to).join(", ") : "· " + r.note) : "✗ consolidation refused — knowledge would be lost:\n" + r.errors.map(e => "  - " + e).join("\n"));
      process.exit(r.ok ? 0 : 1);
    }
    case "help": case undefined: case "--help":
      out({ usage: USAGE }, USAGE);
      break;
    default:
      die("unknown command '" + cmd + "'\n" + USAGE);
  }
} catch (e) {
  die(e.message, 1);
}
