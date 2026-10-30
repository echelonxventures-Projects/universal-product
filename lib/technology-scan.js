/* LUXORA Platform — the repository's technology assumptions, found and gated (PR-053).
   No database, no runtime beyond the floor: this reads files. The detectors, the classes and the
   inventory are data (lib/seed/technology.json → scan, classes, inventory).

     scan(root, decl)      every (file, detector, token) the detectors find, comments stripped
     gate(findings, decl)  each finding must be covered by an inventory entry; an entry whose class
                           is a violation fails (it is to be fixed, not declared); an exception
                           needs its approval recorded; an entry nothing matches any more is stale;
                           an unverified assumption is reported as a gap
     consumers(root, lock) the files that cannot read the lock are validated against it: the CI
                           workflow, the Dockerfile and package.json's engine range */
"use strict";

const fs = require("fs");
const path = require("path");

const SKIP = new Set(["node_modules", ".git", "data", "_superseded", "PROJECT-CONTEXT", "volumes", "docs"]);
function walk(root, rel, out) {
  for (const d of fs.readdirSync(path.join(root, rel), { withFileTypes: true })) {
    const p = rel ? rel + "/" + d.name : d.name;
    if (d.isDirectory()) { if (!SKIP.has(d.name)) walk(root, p, out); }
    else if (d.isFile()) out.push(p);
  }
  return out;
}
/* a glob: ** is any path, * any name part */
const globRe = g => new RegExp("^" + g.split("**").map(part => part.split("*").map(s => s.replace(/[.+?^${}()|[\]\\]/g, "\\$&")).join("[^/]*")).join(".*") + "$");
const matches = (globs, f) => [].concat(globs).some(g => globRe(g).test(f));

const stripJs = src => src.replace(/\/\*[\s\S]*?\*\//g, m => m.replace(/[^\n]/g, " ")).replace(/(^|[^:"'`\\])\/\/[^\n]*/g, (m, p) => p + " ".repeat(m.length - p.length));
const stripHash = src => src.split("\n").map((l, i) => (i === 0 && l.startsWith("#!")) ? l : l.replace(/(^|\s)#.*$/, "$1")).join("\n");
function strip(kind, file, src) {
  /* no style declared: by the file's own syntax */
  const k = kind || (/\.(js|mjs|cjs)$/.test(file) ? "js" : /\.json$/.test(file) ? "none" : "hash");
  return k === "js" ? stripJs(src) : k === "hash" ? stripHash(src) : src;
}

function scan(root, decl) {
  const files = walk(root, "", []).sort();
  const out = [];
  for (const d of decl.scan.detectors) {
    const globs = d.files === "js" ? decl.scan.js : d.files;
    for (const f of files.filter(x => matches(globs, x))) {
      const src = fs.readFileSync(path.join(root, f), "utf8");
      if (d.json) {
        let doc; try { doc = JSON.parse(src); } catch (e) { out.push({ file: f, detector: d.key, token: "(unreadable JSON)", line: 0 }); continue; }
        for (const k of d.json.split(",")) {
          const v = doc[k];
          if (!v || typeof v !== "object") continue;
          for (const [name, val] of Object.entries(v)) out.push({ file: f, detector: d.key, token: d.keys ? name : name + ":" + val, line: 0 });
        }
        continue;
      }
      const re = new RegExp(d.pattern, "gm");
      const text = strip(d.comments, f, src);
      const lines = text.split("\n");
      lines.forEach((line, i) => {
        let m; re.lastIndex = 0;
        while ((m = re.exec(line))) { out.push({ file: f, detector: d.key, token: m[1].trim(), line: i + 1 }); if (!re.global) break; }
      });
    }
  }
  return out;
}

const tokenOk = (e, t) => (e.tokens || []).includes(t) || (e.tokenPattern ? new RegExp(e.tokenPattern).test(t) : false);
function gate(findings, decl) {
  const classes = new Map(decl.classes.map(c => [c.key, c]));
  const errors = [], gaps = [], covered = new Map(decl.inventory.map(e => [e.id, 0]));
  for (const e of decl.inventory) {
    const c = classes.get(e.class);
    if (!c) errors.push(`${e.id}: unknown class ${e.class}`);
    else if (c.needsApproval && !(e.approval && e.approval.by && e.approval.at && e.approval.reason)) errors.push(`${e.id}: a ${e.class} needs a recorded approval { by, at, reason }`);
    if (!e.why) errors.push(`${e.id}: says nothing about why`);
  }
  const seen = new Set();
  for (const f of findings) {
    const id = f.file + "\u0001" + f.detector + "\u0001" + f.token;
    if (seen.has(id)) continue;
    seen.add(id);
    const hit = decl.inventory.filter(e => e.detector === f.detector && tokenOk(e, f.token) && matches(e.files, f.file));
    if (!hit.length) { errors.push(`undeclared technology assumption: ${f.file}:${f.line} ${f.detector} "${f.token}"`); continue; }
    for (const e of hit) {
      covered.set(e.id, covered.get(e.id) + 1);
      const c = classes.get(e.class) || {};
      if (c.violation) errors.push(`${f.file}:${f.line} ${f.detector} "${f.token}" is ${e.class} (${e.id}) — fix it rather than declare it`);
      if (c.gap) gaps.push({ id: e.id, file: f.file, detector: f.detector, token: f.token });
    }
  }
  for (const [id, n] of covered) if (!n) errors.push(`${id}: stale — no finding matches it any more`);
  return { errors, gaps, findings: seen.size };
}

/* ---------- consumers that cannot read the lock, validated against it ---------- */
function consumers(root, lock, decl) {
  const errors = [];
  const read = f => { try { return fs.readFileSync(path.join(root, f), "utf8"); } catch (e) { return null; } };
  /* the CI workflow: the runtime, the service image and the lanes come from the resolve job; what
     cannot be an expression (uses:, runs-on:) is exactly what the lock resolved */
  const wfFile = ".github/workflows/ci.yml", wf = read(wfFile);
  if (wf != null) {
    const text = stripHash(wf);
    const actions = new Set(Object.values(lock.ci.actions || {}));
    for (const m of text.matchAll(/uses:\s*([^\s#]+)/g)) if (!actions.has(m[1])) errors.push(`${wfFile}: uses ${m[1]}, which the lock does not resolve (${[...actions].join(", ")})`);
    for (const m of text.matchAll(/runs-on:\s*(\S+)/g)) if (m[1] !== lock.ci.runner) errors.push(`${wfFile}: runs-on ${m[1]}, the lock resolves ${lock.ci.runner}`);
    for (const m of text.matchAll(/node-version:\s*(\S[^\n]*?)\s*$/gm)) if (!/^\$\{\{\s*(matrix\.version|needs\.resolve\.outputs\.node)\s*\}\}$/.test(m[1])) errors.push(`${wfFile}: node-version ${m[1]} is written in the workflow instead of read from the lock`);
    for (const m of text.matchAll(/^\s+image:\s*(\S[^\n]*?)\s*$/gm)) if (!/^\$\{\{\s*needs\.resolve\.outputs\.[a-z_]+\s*\}\}$/.test(m[1])) errors.push(`${wfFile}: image ${m[1]} is written in the workflow instead of read from the lock`);
    for (const need of ["fromJSON(needs.resolve.outputs.test)", decl.bootstrap.ci.file, ".ci.test", ".ci.node", ".ci.postgres"])
      if (!wf.includes(need)) errors.push(`${wfFile}: the resolve job or the test matrix does not read ${need}`);
  }
  /* the Dockerfile's base is the deploy.container resolution, tag and digest */
  for (const f of ["Dockerfile"]) {
    const t = read(f); if (t == null) continue;
    for (const m of stripHash(t).matchAll(/^FROM\s+(\S+)/gm)) if (m[1] !== lock.ci.container) errors.push(`${f}: FROM ${m[1]}, the lock resolves ${lock.ci.container}`);
  }
  /* package.json's engine range is the derived runtime floor */
  const pj = read("package.json");
  if (pj != null) {
    const want = ">=" + lock.constraints["platform.runtime"].floor, have = ((JSON.parse(pj).engines) || {}).node;
    if (have !== want) errors.push(`package.json: engines.node is ${have}; the floor platform.runtime derives is ${want}`);
  }
  return errors;
}

/* the generated inventory, for people */
function markdown(findings, decl, result) {
  const classes = new Map(decl.classes.map(c => [c.key, c]));
  const md = ["# Technology assumptions — inventory", "",
    "Generated by `node scripts/technology.js inventory` from the detectors and the inventory in `lib/seed/technology.json` — do not edit by hand. Every place the repository states a technology assumption is a finding; every finding is covered by one inventory entry, classified. `node scripts/technology.js check` fails on an undeclared finding, a stale entry, an entry whose class is a violation, or an exception without a recorded approval.", "",
    `Findings: ${result.findings} · entries: ${decl.inventory.length} · gaps (unverified assumptions): ${new Set(result.gaps.map(g => g.id)).size} · errors: ${result.errors.length}`, "",
    "| Entry | Class | Detector | Tokens | Files | Governed by | Where found |", "|---|---|---|---|---|---|---|"];
  const esc = s => String(s).replace(/\|/g, "\\|");
  for (const e of decl.inventory) {
    const where = [...new Set(findings.filter(f => f.detector === e.detector && tokenOk(e, f.token) && matches(e.files, f.file)).map(f => f.file))];
    md.push(`| ${e.id} | ${(classes.get(e.class) || {}).label || e.class} | ${e.detector} | ${e.tokens.map(t => "`" + esc(t) + "`").join(", ")} | ${e.files.map(f => "`" + f + "`").join(", ")} | ${e.governedBy || "—"} | ${where.length} (${esc(where.slice(0, 4).join(", "))}${where.length > 4 ? ", …" : ""}) |`);
  }
  md.push("", "## Why each is what it is", "");
  for (const e of decl.inventory) md.push(`- **${e.id}** (${e.class}) — ${e.why}`);
  md.push("");
  return md.join("\n");
}

module.exports = { scan, gate, consumers, markdown, matches, strip };
