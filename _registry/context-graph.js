/* UCOS Ω∞ · the context graph — every artifact registered, every relationship typed.
   --------------------------------------------------------------------------
   The context continuity system is a PROJECTION, exactly like the 93 artifacts
   project.js writes: its truth is authored once in _registry/context.json and
   everything else (nodes, edges, packs, manifest, map) is derived from that file
   plus the repository's own canonical sources. This module owns the derivation of
   the GRAPH; context-packs.js owns its projection into bounded packs; context.js
   is the command line over both.

   Nothing in here names a repository artifact. Which files exist comes from git
   (or a directory walk when there is no .git), which class a file belongs to
   comes from the spec's ordered class rules, and which relationships exist comes
   from the spec's authored edges plus the extractors the spec switches on — each
   extractor reads a canonical source (a require graph, the UCOS manifest, the
   compile's input arrays, the CI test script, the handoff records) rather than a
   copy of it. A file no class claims is an error, not a silent omission.

   Pure and deterministic: discover() → build() → validate() read the working tree
   and return plain data, sorted, with no timestamps, so two runs over unchanged
   inputs are byte-identical. */
"use strict";

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const { execFileSync } = require("child_process");

const SPEC_SCHEMA = "ucos.context.spec.v1";
const SPEC_PATH = "_registry/context.json";

/* ============================ small, pure helpers ============================ */
const sha256 = buf => crypto.createHash("sha256").update(buf).digest("hex");
const byKey = k => (a, b) => (a[k] < b[k] ? -1 : a[k] > b[k] ? 1 : 0);
const cmp = (a, b) => (a < b ? -1 : a > b ? 1 : 0);
const toPosix = p => p.split(path.sep).join("/");

/* a glob is the only path language the spec speaks: ** crosses directories,
   * and ? never do, [..] is a character class, everything else is literal */
const globCache = new Map();
function globToRe(g) {
  if (globCache.has(g)) return globCache.get(g);
  let re = "";
  for (let i = 0; i < g.length; i++) {
    const c = g[i];
    if (c === "*" && g[i + 1] === "*") {
      if (g[i + 2] === "/") { re += "(?:.*/)?"; i += 2; } else { re += ".*"; i += 1; }
    } else if (c === "*") re += "[^/]*";
    else if (c === "?") re += "[^/]";
    else if (c === "[" && g.indexOf("]", i + 1) > i + 1) { const j = g.indexOf("]", i + 1); re += "[" + g.slice(i + 1, j).replace(/\\/g, "\\\\") + "]"; i = j; }
    else re += c.replace(/[.+^${}()|[\]\\]/g, "\\$&");
  }
  const out = new RegExp("^" + re + "$");
  globCache.set(g, out);
  return out;
}
const matchAny = (p, globs) => [].concat(globs || []).some(g => globToRe(g).test(p));

/* ============================ the spec ============================ */
function loadSpec(root) {
  const file = path.join(root, SPEC_PATH);
  let raw;
  try { raw = fs.readFileSync(file, "utf8"); } catch (e) { throw new Error("context: no spec at " + SPEC_PATH + " — the context registry is missing"); }
  let spec;
  try { spec = JSON.parse(raw); } catch (e) { throw new Error("context: " + SPEC_PATH + " is not valid JSON: " + e.message); }
  const problems = specProblems(spec);
  if (problems.length) throw new Error("context: " + SPEC_PATH + " is invalid:\n  - " + problems.join("\n  - "));
  return spec;
}

/* structural validation of the authored spec — refuse to derive anything from a
   spec that cannot be read unambiguously (fail closed) */
function specProblems(s) {
  const p = [];
  if (!s || typeof s !== "object") return ["spec is not an object"];
  if (s.schema !== SPEC_SCHEMA) p.push("schema must be '" + SPEC_SCHEMA + "' (got '" + s.schema + "')");
  for (const k of ["authorityLevels", "edgeTypes", "classes", "units", "sequences"]) if (!Array.isArray(s[k]) || !s[k].length) p.push(k + " must be a non-empty array");
  if (!s.output || typeof s.output.dir !== "string") p.push("output.dir is required");
  if (!s.budgets || !(s.budgets.packChars > 0)) p.push("budgets.packChars must be a positive number");
  const levels = new Set((s.authorityLevels || []).map(a => a.id));
  for (const c of s.classes || []) {
    if (!c.id || !c.match) p.push("class " + JSON.stringify(c.id) + " needs id and match");
    if (c.authority && !levels.has(c.authority)) p.push("class " + c.id + " names unknown authority level '" + c.authority + "'");
  }
  for (const c of s.virtualClasses || []) if (c.authority && !levels.has(c.authority)) p.push("virtual class " + c.id + " names unknown authority level '" + c.authority + "'");
  const ids = new Set();
  for (const u of s.units || []) { if (!u.id) p.push("a unit has no id"); if (ids.has(u.id)) p.push("duplicate unit id " + u.id); ids.add(u.id); }
  for (const e of s.edgeTypes || []) if (!e.id || !["to", "from", null].includes(e.prereq === undefined ? null : e.prereq)) p.push("edge type " + e.id + " needs prereq 'to' | 'from' | null");
  return p;
}

/* ============================ discovery ============================ */
function git(root, args) {
  try { return execFileSync("git", args, { cwd: root, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"], maxBuffer: 64 << 20 }).trim(); }
  catch (e) { return null; }
}

/* the file universe: git's view when there is a repository (tracked + untracked,
   minus ignored — so per-deployment secrets and build output never register),
   a deterministic walk otherwise (fixtures). Generated output is never an input. */
function listFiles(root, spec) {
  const exclude = [].concat(spec.exclude || [], spec.output.dir + "/**");
  let files = null;
  const useGit = spec.discovery && spec.discovery.useGit !== false && fs.existsSync(path.join(root, ".git"));
  if (useGit) {
    const out = git(root, ["ls-files", "-co", "--exclude-standard", "-z"]);
    if (out != null) files = out.split("\0").filter(Boolean);
  }
  if (!files) {
    files = [];
    (function walk(dir) {
      for (const e of fs.readdirSync(path.join(root, dir), { withFileTypes: true }).sort((a, b) => cmp(a.name, b.name))) {
        const rel = dir ? dir + "/" + e.name : e.name;
        if (e.name === ".git" || e.name === "node_modules") continue;
        if (e.isDirectory()) walk(rel); else if (e.isFile()) files.push(rel);
      }
    })("");
  }
  return [...new Set(files.map(toPosix))]
    .filter(f => !matchAny(f, exclude))
    .filter(f => { try { return fs.statSync(path.join(root, f)).isFile(); } catch (e) { return false; } })
    .sort(cmp);
}

/* the title and navigational summary of a file are EXTRACTED, never written: the
   first heading / leading comment / registry name. They are navigation, labelled
   as such in every pack, and always point at the source. */
function extractTitle(rel, text) {
  if (text == null) return null;
  const ext = path.extname(rel);
  if (ext === ".md") {
    const lines = text.split("\n").filter(l => /^#\s+/.test(l)).slice(0, 2).map(l => l.replace(/^#\s+/, "").trim());
    const t = lines.find(l => !/^\[SUPERSEDED/.test(l)) || lines[0];
    return t ? t.slice(0, 140) : null;
  }
  if (ext === ".json") {
    try { const j = JSON.parse(text); return String(j.canonicalName || j.registryId || j.name || j.title || "").slice(0, 140) || null; } catch (e) { return null; }
  }
  if (ext === ".js" || ext === ".mjs" || ext === ".cjs") {
    const m = text.match(/^(?:#![^\n]*\n)?\s*\/\*+\s*([^\n]*)/);
    if (m && m[1].trim()) return m[1].replace(/\*\/.*$/, "").trim().slice(0, 140);
    const c = text.match(/^(?:#![^\n]*\n)?(?:\s*(?:'use strict'|"use strict");?\s*)?\s*\/\/\s*([^\n]+)/);
    return c ? c[1].trim().slice(0, 140) : null;
  }
  const first = text.split("\n").map(l => l.trim()).find(l => l && !/^[#;]?\s*$/.test(l));
  return first ? first.replace(/^#+\s*/, "").slice(0, 140) : null;
}

function extractSummary(rel, text, secretRes) {
  if (text == null) return null;
  const ext = path.extname(rel);
  let s = null;
  if (ext === ".md") {
    const paras = text.split(/\n\s*\n/).map(p => p.trim()).filter(p => p && !/^(#|---|```|\||<!--|>\s*\*\*Status)/.test(p) && !/^\*\*Version/.test(p));
    s = paras[0] || null;
  } else if (ext === ".js") {
    const m = text.match(/\/\*+([\s\S]*?)\*\//);
    if (m) s = m[1].split("\n").map(l => l.replace(/^\s*\*?\s?/, "")).slice(1).join(" ").replace(/-{6,}/g, " ");
  } else if (ext === ".json") {
    try { const j = JSON.parse(text); s = j.description || j.law || j.note || null; } catch (e) { }
  }
  if (!s) return null;
  s = String(s).replace(/\s+/g, " ").trim();
  if (secretRes.some(r => r.test(s))) return null;   /* a summary never carries anything secret-shaped */
  return s.length > 280 ? s.slice(0, 277).replace(/\s+\S*$/, "") + " …" : s;
}

function classify(rel, spec) {
  for (const c of spec.classes) if (matchAny(rel, c.match) && !matchAny(rel, c.except)) return c;
  return null;
}

function authorityRank(spec, id) { const i = spec.authorityLevels.findIndex(a => a.id === id); return i < 0 ? 99 : i; }

/* ============================ the build ============================ */
function readJSON(root, rel) { try { return JSON.parse(fs.readFileSync(path.join(root, rel), "utf8")); } catch (e) { return null; } }

function build(root, spec, opts) {
  opts = opts || {};
  spec = spec || loadSpec(root);
  const secretRes = (spec.security && spec.security.secretPatterns || []).map(s => new RegExp(s, "i"));
  const findings = [];
  const find = (severity, code, subject, message) => findings.push({ severity, code, subject, message });

  const files = listFiles(root, spec);
  const nodes = new Map();
  const byPath = new Map();
  const ucosManifest = spec.sources && spec.sources.ucosManifest ? readJSON(root, spec.sources.ucosManifest) : null;
  const ucosArt = new Map(((ucosManifest || {}).artifacts || []).map(a => [a.id, a]));

  for (const rel of files) {
    if (matchAny(rel, spec.security && spec.security.denyPaths)) { find("error", "SECRET_PATH", rel, "a secret-shaped path is visible to the context system — it must be gitignored or excluded, never registered"); continue; }
    const cls = classify(rel, spec);
    const buf = fs.readFileSync(path.join(root, rel));
    const text = /\.(md|js|json|txt|yml|yaml|sql|sh|html|css|service)$/.test(rel) || !path.extname(rel) ? buf.toString("utf8") : null;
    if (!cls) { find("error", "UNREGISTERED_FILE", rel, "no class in " + SPEC_PATH + " claims this file — register it (classes[].match) or exclude it"); continue; }
    let id = "file:" + rel, title = extractTitle(rel, text), extra = {};
    if (cls.idFrom === "ucos-artifact") {
      const m = path.basename(rel).match(/^(UCOS-[A-Z]+-\d{6})-/);
      if (!m || !ucosArt.has(m[1])) { find("error", "UNKNOWN_CANONICAL_ID", rel, "file name carries no artifact id declared in " + spec.sources.ucosManifest); }
      else { id = m[1]; const a = ucosArt.get(m[1]); title = a.title; extra = { category: a.cat, version: ucosManifest.version }; }
    }
    if (nodes.has(id)) { find("error", "DUPLICATE_ID", id, "two files claim the same canonical id: " + nodes.get(id).path + " and " + rel); continue; }
    let lifecycle = cls.lifecycle || null;
    const head = text ? text.slice(0, 600) : "";
    for (const sm of spec.statusMarkers || []) if (new RegExp(sm.pattern, "m").test(head)) { lifecycle = sm.lifecycle; break; }
    const n = {
      id, path: rel, class: cls.id, kind: cls.kind, authority: cls.authority, lifecycle, owner: cls.owner || null, status: "present",
      digest: sha256(buf), bytes: buf.length, lines: text == null ? null : text.split("\n").length,
      title: title || rel, summary: extractSummary(rel, text, secretRes), generatedBy: cls.generatedBy || null,
      domains: cls.domains || [], mandatory: cls.mandatory !== false, virtual: false, ...extra
    };
    nodes.set(id, n); byPath.set(rel, n);
  }

  /* every artifact the UCOS manifest declares must exist as a file — a declaration
     with no substance is a missing target */
  if (ucosManifest) for (const a of ucosManifest.artifacts || []) if (!nodes.has(a.id)) find("error", "MISSING_ARTIFACT", a.id, "declared in " + spec.sources.ucosManifest + " but no file carries it");

  /* virtual nodes: constraints, decisions, conflicts — authored once, in the spec */
  const vclass = new Map((spec.virtualClasses || []).map(c => [c.id, c]));
  const addVirtual = (id, clsId, fields) => {
    const c = vclass.get(clsId) || { id: clsId, kind: "authored", authority: null };
    if (nodes.has(id)) { find("error", "DUPLICATE_ID", id, "a virtual node reuses an existing id"); return null; }
    const n = { id, path: fields.path || null, class: clsId, kind: c.kind, authority: c.authority, lifecycle: fields.lifecycle || c.lifecycle || null, owner: c.owner || null, status: fields.status || "active", digest: fields.digest || null, bytes: null, lines: null, title: fields.title, summary: fields.summary || null, generatedBy: null, domains: c.domains || [], mandatory: c.mandatory !== false, virtual: true, data: fields.data || null };
    nodes.set(id, n);
    return n;
  };
  for (const c of spec.constraints || []) addVirtual(c.id, "constraint", { title: c.title, summary: c.quote, data: c, digest: sha256(JSON.stringify(c)) });
  for (const d of spec.decisions || []) addVirtual(d.id, "decision", { title: d.title, summary: d.statement, status: d.status, data: d, digest: sha256(JSON.stringify(d)) });
  for (const c of spec.conflicts || []) addVirtual(c.id, "conflict", { title: c.title, summary: c.statement, status: c.status, data: c, digest: sha256(JSON.stringify(c)) });

  /* ---------- edges ---------- */
  const edgeTypes = new Map(spec.edgeTypes.map(e => [e.id, e]));
  const edges = [];
  const seen = new Set();
  const dangling = [];
  const addEdge = (from, type, to, origin) => {
    if (!edgeTypes.has(type)) { find("error", "UNKNOWN_EDGE_TYPE", from + " " + type, "edge type '" + type + "' is not declared in edgeTypes"); return; }
    if (!nodes.has(from) || !nodes.has(to)) { dangling.push({ from, type, to, origin }); return; }
    if (from === to) return;
    const k = from + "\u0000" + type + "\u0000" + to;
    if (seen.has(k)) return;
    seen.add(k);
    edges.push({ from, type, to, origin });
  };
  const resolveRef = ref => {
    if (nodes.has(ref)) return ref;
    if (byPath.has(ref)) return byPath.get(ref).id;
    return ref;   /* left unresolved — reported as a dangling reference */
  };

  const ctx = { root, spec, nodes, byPath, addEdge, addVirtual, resolveRef, find, readJSON: rel => readJSON(root, rel), secretRes };
  for (const x of spec.extractors || []) {
    const fn = EXTRACTORS[x.type];
    if (!fn) { find("error", "UNKNOWN_EXTRACTOR", x.type, "the spec switches on an extractor this engine does not implement"); continue; }
    fn(ctx, x);
  }
  for (const e of spec.edges || []) addEdge(resolveRef(e.from), e.type, resolveRef(e.to), "authored");
  for (const r of spec.edgeRules || []) {
    const froms = select(nodes, edges, r.from), tos = select(nodes, edges, r.to);
    for (const f of froms) for (const t of tos) addEdge(f.id, r.type, t.id, "rule:" + r.id);
  }
  /* constraints, decisions and conflicts attach to what they govern through selectors */
  for (const c of spec.constraints || []) for (const t of select(nodes, edges, c.appliesTo)) addEdge(c.id, "constrains", t.id, "constraint:" + c.id);
  for (const d of spec.decisions || []) for (const t of select(nodes, edges, d.governs)) addEdge(d.id, "constrains", t.id, "decision:" + d.id);
  for (const c of spec.conflicts || []) for (const t of select(nodes, edges, c.between)) addEdge(c.id, "conflicts-with", t.id, "conflict:" + c.id);
  for (const d of spec.decisions || []) for (const s of d.supersedes || []) addEdge(d.id, "supersedes", resolveRef(s), "decision:" + d.id);
  /* a supersession record names the successor(s); the edge points successor → old */
  for (const s of spec.supersessions || []) {
    const old = resolveRef(s.artifact);
    const succ = select(nodes, edges, s.successors);
    if (!succ.length) find("error", "SUPERSESSION_NO_SUCCESSOR", s.id, "successors select nothing");
    for (const t of succ) addEdge(t.id, "supersedes", old, "supersession:" + s.id);
  }

  /* a dangling reference is an error unless an OPEN conflict acknowledges it by
     subject — then it stays visible (warning) but does not block, because the
     conflict record is where its resolution is tracked */
  const acks = new Map();
  for (const c of spec.conflicts || []) if (c.status !== "resolved") for (const a of c.acknowledges || []) acks.set(a.code + "\u0000" + a.subject, c.id);
  for (const d of dangling) {
    const missing = nodes.has(d.from) ? d.to : d.from;
    const ack = acks.get("DANGLING_EDGE\u0000" + missing);
    if (ack) find("warning", "DANGLING_EDGE", missing, d.from + " —" + d.type + "→ " + d.to + " (" + d.origin + ") does not resolve; acknowledged by open conflict " + ack);
    else find("error", "DANGLING_EDGE", missing, d.from + " —" + d.type + "→ " + d.to + " (" + d.origin + ") does not resolve to a registered artifact");
  }

  edges.sort((a, b) => cmp(a.from, b.from) || cmp(a.type, b.type) || cmp(a.to, b.to) || cmp(a.origin, b.origin));
  const graph = { root, spec, nodes, edges, findings, edgeTypes, byPath };
  graph.out = new Map(); graph.in = new Map();
  for (const n of nodes.keys()) { graph.out.set(n, []); graph.in.set(n, []); }
  for (const e of edges) { graph.out.get(e.from).push(e); graph.in.get(e.to).push(e); }
  return graph;
}

/* ============================ selectors ============================ */
/* the one way the spec refers to a set of nodes — by class, category, path glob,
   explicit id, or as the targets of an edge from a named node. Never by position. */
function select(nodes, edges, sel) {
  if (!sel) return [];
  const sels = Array.isArray(sel) ? sel : [sel];
  const out = new Map();
  for (const s of sels) {
    if (typeof s === "string") { if (nodes.has(s)) out.set(s, nodes.get(s)); else for (const n of nodes.values()) if (n.path === s) out.set(n.id, n); continue; }
    let targets = null;
    if (s.edgeFrom) targets = new Set(edges.filter(e => e.from === s.edgeFrom.node && (!s.edgeFrom.type || e.type === s.edgeFrom.type)).map(e => e.to));
    for (const n of nodes.values()) {
      if (s.class && ![].concat(s.class).includes(n.class)) continue;
      if (s.notClass && [].concat(s.notClass).includes(n.class)) continue;
      if (s.category && ![].concat(s.category).includes(n.category)) continue;
      if (s.notCategory && [].concat(s.notCategory).includes(n.category)) continue;
      if (s.ids && !s.ids.includes(n.id)) continue;
      if (s.pathGlob && !(n.path && matchAny(n.path, s.pathGlob))) continue;
      if (targets && !targets.has(n.id)) continue;
      out.set(n.id, n);
    }
  }
  return [...out.values()].sort(byKey("id"));
}

/* ============================ a lexical mask for JavaScript ============================ */
/* blank out comments and the CONTENTS of string, template and regex literals (same
   length, so offsets survive) — a require() inside a string or a comment is text,
   not a dependency. Returns the masked source; callers read literal values from
   the original at the same offsets. */
function maskJS(src) {
  const out = src.split("");
  let i = 0, prev = "";
  const blank = (a, b) => { for (let k = a; k < b; k++) if (out[k] !== "\n") out[k] = " "; };
  while (i < src.length) {
    const c = src[i], d = src[i + 1];
    if (c === "/" && d === "/") { const e = src.indexOf("\n", i); const end = e < 0 ? src.length : e; blank(i, end); i = end; continue; }
    if (c === "/" && d === "*") { const e = src.indexOf("*/", i + 2); const end = e < 0 ? src.length : e + 2; blank(i, end); i = end; continue; }
    if (c === "'" || c === '"' || c === "`") {
      let j = i + 1;
      while (j < src.length && src[j] !== c) { if (src[j] === "\\") j++; else if (c !== "`" && src[j] === "\n") break; j++; }
      blank(i + 1, j); i = j + 1; prev = c; continue;
    }
    if (c === "/" && (prev === "" || "(,=:[!&|?{};+-*%<>~^".includes(prev))) {
      let j = i + 1, cls = false;
      while (j < src.length && src[j] !== "\n" && (cls || src[j] !== "/")) { if (src[j] === "\\") j++; else if (src[j] === "[") cls = true; else if (src[j] === "]") cls = false; j++; }
      blank(i + 1, j); i = j + 1; prev = "/"; continue;
    }
    if (!/\s/.test(c)) prev = c;
    i++;
  }
  return out.join("");
}

/* ============================ extractors ============================ */
/* each reads ONE canonical source for relationships it already declares. */
const EXTRACTORS = {
  /* CommonJS requires — literal relative paths and the path.join(ROOT|__dirname, …)
     shape this codebase uses. A literal relative require that does not resolve is
     a broken reference; a computed one the extractor cannot evaluate is skipped. */
  "js-require"(ctx, x) {
    for (const n of ctx.nodes.values()) {
      if (n.virtual || !/\.(c|m)?js$/.test(n.path) || (x.classes && !x.classes.includes(n.class))) continue;
      const text = fs.readFileSync(path.join(ctx.root, n.path), "utf8");
      const masked = maskJS(text);
      const lit = (start, end) => text.slice(start, end);   /* a literal's value, read from the original */
      const dir = path.posix.dirname(n.path);
      const targets = new Set();
      for (const m of masked.matchAll(/require\(\s*(["'])( *)\1\s*\)/g)) {
        const q = m.index + m[0].indexOf(m[1]) + 1;
        const v = lit(q, q + m[2].length);
        if (/^\.{1,2}\//.test(v)) targets.add(path.posix.normalize(dir + "/" + v));
      }
      for (const m of masked.matchAll(/require\(\s*path\.(?:join|resolve)\(\s*([A-Za-z_]+)\s*((?:,\s*["'] *["']\s*)+)\)\s*\)/g)) {
        const off = m.index + m[0].indexOf(m[2]);
        const parts = [...m[2].matchAll(/(["'])( *)\1/g)].map(p => lit(off + p.index + 1, off + p.index + 1 + p[2].length));
        const base = m[1] === "__dirname" ? dir : (x.rootIdentifiers || ["ROOT"]).includes(m[1]) ? "" : null;
        if (base == null) continue;
        targets.add(path.posix.normalize((base ? base + "/" : "") + parts.join("/")));
      }
      for (let t of targets) {
        if (t.startsWith("../")) continue;   /* outside the repository */
        const cand = [t, t + ".js", t + "/index.js"].find(c => ctx.byPath.has(c));
        if (cand) ctx.addEdge(n.id, "depends-on", ctx.byPath.get(cand).id, "extractor:js-require");
        else ctx.addEdge(n.id, "depends-on", t, "extractor:js-require");
      }
    }
  },

  /* the registry → document projection: every projected artifact is derived from
     the registry files the generator loads (read from the generator's own load()
     calls, never listed here) and from the one content block its route names. */
  "ucos-projection"(ctx, x) {
    const gen = ctx.byPath.get(x.generator);
    if (!gen) { ctx.find("error", "MISSING_GENERATOR", x.generator, "the projection generator is not registered"); return; }
    const src = fs.readFileSync(path.join(ctx.root, x.generator), "utf8");
    const loaded = [...src.matchAll(/load\(\s*['"]([^'"]+\.json)['"]\s*\)/g)].map(m => path.posix.join(path.posix.dirname(x.generator), m[1]));
    const contentRe = globToRe(x.contentFileGlob);
    const common = loaded.filter(f => !contentRe.test(f));
    const cm = ctx.readJSON(x.contentMap) || {};
    const mapping = cm.mapping || cm.map || {};
    for (const n of ctx.nodes.values()) {
      if (n.class !== x.artifactClass) continue;
      ctx.addEdge(n.id, "derived-from", gen.id, "extractor:ucos-projection");
      for (const f of common) ctx.addEdge(n.id, "derived-from", ctx.resolveRef(f), "extractor:ucos-projection");
      const route = mapping[n.id];
      if (!route) { ctx.find("error", "MISSING_CONTENT_ROUTE", n.id, "no route in " + x.contentMap); continue; }
      ctx.addEdge(n.id, "derived-from", ctx.resolveRef(x.contentFileGlob.replace("*", route.src)), "extractor:ucos-projection");
    }
  },

  /* the runtime compile: the derived (uncommitted, per-deployment sealed) registry
     is derived from exactly the files the compiler's own input arrays name */
  "js-array-inputs"(ctx, x) {
    const text = (() => { try { return fs.readFileSync(path.join(ctx.root, x.file), "utf8"); } catch (e) { return null; } })();
    if (text == null) { ctx.find("error", "MISSING_TARGET", x.file, "the compile input declaration file is missing"); return; }
    const d = x.derived;
    ctx.addVirtual(d.id, d.class, { title: d.title, summary: d.summary, path: d.path, status: d.status, data: { declaredIn: x.file } });
    let count = 0;
    for (const arr of x.arrays) {
      const m = text.match(new RegExp("const\\s+" + arr + "\\s*=\\s*\\[([\\s\\S]*?)\\]"));
      if (!m) { ctx.find("error", "EXTRACTION_FAILED", x.file + "#" + arr, "array " + arr + " not found — the extractor cannot prove what the compile reads"); continue; }
      for (const s of m[1].matchAll(/["']([^"']+)["']/g)) { ctx.addEdge(d.id, "derived-from", ctx.resolveRef(s[1]), "extractor:js-array-inputs"); count++; }
    }
    ctx.addEdge(d.id, "derived-from", ctx.resolveRef(x.file), "extractor:js-array-inputs");
    if (!count) ctx.find("error", "EXTRACTION_FAILED", x.file, "no compile inputs extracted");
  },

  /* the CI test script: which test files CI executes, and therefore which modules
     are verified by which tests. A test CI never runs is a warning. */
  "npm-test-script"(ctx, x) {
    const pkg = ctx.readJSON(x.packageJson);
    const script = pkg && pkg.scripts && pkg.scripts[x.script];
    if (!script) { ctx.find("error", "MISSING_TARGET", x.packageJson + "#scripts." + x.script, "the CI test script is missing"); return; }
    const run = new Set([...script.matchAll(/node\s+(?!--check)([^\s&|;]+\.js)/g)].map(m => m[1]));
    const checked = new Set([...script.matchAll(/node\s+--check\s+([^\s&|;]+)/g)].map(m => m[1]));
    const pkgNode = ctx.byPath.get(x.packageJson);
    for (const f of run) {
      const t = ctx.byPath.get(f);
      if (!t) { ctx.addEdge(pkgNode ? pkgNode.id : x.packageJson, "verified-by", f, "extractor:npm-test-script"); continue; }
      t.ciGated = true;
    }
    for (const f of checked) { const t = ctx.byPath.get(f); if (t) t.syntaxChecked = true; else ctx.addEdge(pkgNode ? pkgNode.id : x.packageJson, "verified-by", f, "extractor:npm-test-script"); }
    for (const n of ctx.nodes.values()) {
      if (n.class !== x.testClass) continue;
      if (!n.ciGated && !matchAny(n.path, x.helpers || [])) ctx.find("warning", "TEST_NOT_IN_CI", n.path, "a test file the CI script never runs — it cannot guard anything");
    }
  },

  /* the handoff records: each is a node; a task's records chain (continues /
     hands-off-to), and each names the prerequisites a resumer must load */
  "handoff-records"(ctx, x) {
    const recs = [...ctx.nodes.values()].filter(n => n.class === x.recordClass).sort(byKey("path"));
    const byTask = new Map();
    for (const n of recs) {
      let r = null;
      try { r = JSON.parse(fs.readFileSync(path.join(ctx.root, n.path), "utf8")); } catch (e) { ctx.find("error", "HANDOFF_INVALID", n.path, "not valid JSON"); continue; }
      n.data = { taskId: r.taskId, seq: r.seq, status: r.status, nextAction: r.resume && r.resume.nextAction };
      n.title = "Handoff " + r.taskId + " #" + r.seq + " (" + r.status + ")";
      n.summary = r.objective ? String(r.objective).slice(0, 280) : null;
      if (!byTask.has(r.taskId)) byTask.set(r.taskId, []);
      byTask.get(r.taskId).push({ n, r });
      for (const p of (r.resume && r.resume.prerequisites) || []) ctx.addEdge(n.id, "requires", ctx.resolveRef(p), "handoff:" + r.taskId);
    }
    for (const list of byTask.values()) {
      list.sort((a, b) => a.r.seq - b.r.seq);
      /* each record must be complete, and record N must carry the digest of record
         N-1 — an edited or deleted past record breaks the chain */
      list.forEach((x, i) => {
        const prev = i ? list[i - 1].n.digest : null;
        for (const pr of handoffProblems(x.r, prev, i + 1, ctx.secretRes)) ctx.find("error", "HANDOFF_INVALID", x.n.path, pr);
        const want = path.posix.join(path.posix.dirname(x.n.path), String(x.r.seq).padStart(4, "0") + ".json");
        if (x.n.path !== want || path.posix.basename(path.posix.dirname(x.n.path)) !== x.r.taskId) ctx.find("error", "HANDOFF_INVALID", x.n.path, "must live at <handoffs>/" + x.r.taskId + "/" + String(x.r.seq).padStart(4, "0") + ".json");
      });
      /* only the latest record of an unfinished task is current working context;
         every earlier record, and a completed task's last one, is evidence */
      list.forEach((x, i) => { x.n.lifecycle = i === list.length - 1 && x.r.status !== "completed" ? "active-operational" : "historical-evidence"; });
      for (let i = 1; i < list.length; i++) {
        ctx.addEdge(list[i].n.id, "continues", list[i - 1].n.id, "handoff:" + list[i].r.taskId);
        ctx.addEdge(list[i - 1].n.id, "hands-off-to", list[i].n.id, "handoff:" + list[i].r.taskId);
      }
    }
  }
};

/* ============================ handoff records ============================ */
const HANDOFF_SCHEMA = "ucos.context.handoff.v1";
const HANDOFF_STATUSES = ["in-progress", "interrupted", "blocked", "completed"];
/* what makes a record resumable by an agent that never saw the conversation */
function handoffProblems(r, prevDigest, expectSeq, secretRes) {
  const p = [];
  const need = (cond, msg) => { if (!cond) p.push(msg); };
  need(r && r.schema === HANDOFF_SCHEMA, "schema must be " + HANDOFF_SCHEMA);
  if (!r) return p;
  need(/^[A-Z][A-Z0-9-]{2,63}$/.test(r.taskId || ""), "taskId must match ^[A-Z][A-Z0-9-]{2,63}$");
  need(r.seq === expectSeq, "seq must be " + expectSeq + " (records are contiguous)");
  need((r.previousDigest || null) === (prevDigest || null), "previousDigest must equal the sha256 of record " + (expectSeq - 1) + " (hash chain broken)");
  need(HANDOFF_STATUSES.includes(r.status), "status must be one of " + HANDOFF_STATUSES.join(", "));
  need(typeof r.objective === "string" && r.objective.trim().length >= 10, "objective is required");
  need(r.authority && typeof r.authority.instruction === "string" && r.authority.instruction.trim(), "authority.instruction is required (who authorized the work)");
  const v = r.verified || {};
  need(v.revisions && /^[0-9a-f]{7,40}$/.test(v.revisions.start || "") && /^[0-9a-f]{7,40}$/.test(v.revisions.end || ""), "verified.revisions.start/end must be commit ids");
  need(Array.isArray(v.changedFiles), "verified.changedFiles must be a list (tool-produced)");
  need(Array.isArray(v.commands), "verified.commands must be a list (tool-produced; may be empty)");
  const a = r.asserted || {};
  for (const k of ["decisions", "results", "failures", "limitations", "risks", "unresolved", "notDone"]) need(Array.isArray(a[k]), "asserted." + k + " must be a list (empty means 'none', stated explicitly)");
  need(r.context && Array.isArray(r.context.packsUsed) && r.context.packsUsed.length, "context.packsUsed must name the packs the work relied on");
  need(r.resume && typeof r.resume.nextAction === "string" && r.resume.nextAction.trim().length >= 10, "resume.nextAction is required — the exact next step");
  need(r.resume && Array.isArray(r.resume.prerequisites), "resume.prerequisites must be a list of ids or paths");
  const text = JSON.stringify(r);
  for (const re of secretRes || []) if (re.test(text)) p.push("contains a secret-shaped string (" + re.source + ")");
  return p;
}

/* ============================ traversal ============================ */
/* normalize an edge to "prerequisite → dependent" using its type's declared
   direction; edges whose type has no prerequisite direction are not traversed */
function prereqOf(graph, e) {
  const t = graph.edgeTypes.get(e.type);
  if (!t || !t.prereq) return null;
  return t.prereq === "to" ? { pre: e.to, dep: e.from, closure: t.closure } : { pre: e.from, dep: e.to, closure: t.closure };
}

/* the prerequisite closure of a set of start nodes. Iterative and visited-set
   bounded, so legitimate cycles cannot loop. `level`: "mandatory" follows only
   mandatory edge types; "relevant" follows both. */
function closure(graph, starts, level) {
  const want = level === "relevant" ? new Set(["mandatory", "relevant"]) : new Set(["mandatory"]);
  const pres = new Map();   /* dep → [{pre, edge}] */
  for (const e of graph.edges) {
    const p = prereqOf(graph, e);
    if (!p || !want.has(p.closure)) continue;
    if (!pres.has(p.dep)) pres.set(p.dep, []);
    pres.get(p.dep).push({ pre: p.pre, edge: e });
  }
  const seen = new Set(), via = new Map();
  const stack = [...starts].sort().reverse();
  while (stack.length) {
    const id = stack.pop();
    if (seen.has(id)) continue;
    seen.add(id);
    for (const { pre, edge } of (pres.get(id) || []).slice().sort((a, b) => cmp(a.pre, b.pre))) {
      if (!seen.has(pre)) { if (!via.has(pre)) via.set(pre, edge); stack.push(pre); }
    }
  }
  return { ids: seen, via, pres };
}

/* the reverse: everything whose prerequisites (transitively) include a start —
   the downstream impact of a change. verified-by is followed one hop so the
   tests guarding an artifact are always named. */
function impact(graph, starts) {
  const deps = new Map();
  for (const e of graph.edges) {
    const p = prereqOf(graph, e);
    if (!p) continue;
    if (!deps.has(p.pre)) deps.set(p.pre, []);
    deps.get(p.pre).push(p.dep);
  }
  const seen = new Set(), stack = [...starts];
  while (stack.length) {
    const id = stack.pop();
    if (seen.has(id)) continue;
    seen.add(id);
    for (const d of deps.get(id) || []) if (!seen.has(d)) stack.push(d);
  }
  const tests = new Set();
  for (const id of seen) for (const e of graph.out.get(id) || []) if (e.type === "verified-by") tests.add(e.to);
  return { ids: seen, tests };
}

/* Tarjan's SCC over a node set and a successor function — iterative, so a deep
   graph cannot blow the stack */
function scc(ids, succ) {
  let index = 0;
  const idx = new Map(), low = new Map(), on = new Set(), st = [], out = [];
  for (const root of ids) {
    if (idx.has(root)) continue;
    const work = [[root, 0]];
    idx.set(root, index); low.set(root, index); index++; st.push(root); on.add(root);
    while (work.length) {
      const top = work[work.length - 1];
      const [v, i] = top;
      const ss = succ(v);
      if (i < ss.length) {
        top[1]++;
        const w = ss[i];
        if (!idx.has(w)) { idx.set(w, index); low.set(w, index); index++; st.push(w); on.add(w); work.push([w, 0]); }
        else if (on.has(w)) low.set(v, Math.min(low.get(v), idx.get(w)));
      } else {
        work.pop();
        if (work.length) { const u = work[work.length - 1][0]; low.set(u, Math.min(low.get(u), low.get(v))); }
        if (low.get(v) === idx.get(v)) {
          const comp = [];
          let w;
          do { w = st.pop(); on.delete(w); comp.push(w); } while (w !== v);
          out.push(comp.sort());
        }
      }
    }
  }
  return out;
}

/* order a node set prerequisites-first. Cycles collapse to one position (members
   by id); ties break by a caller rank then id — fully deterministic. */
function orderPrereqFirst(graph, ids, rank) {
  rank = rank || (() => 0);
  const set = new Set(ids);
  const succ = new Map([...set].map(i => [i, []]));
  for (const e of graph.edges) {
    const p = prereqOf(graph, e);
    if (!p || !set.has(p.pre) || !set.has(p.dep)) continue;
    succ.get(p.pre).push(p.dep);
  }
  for (const v of succ.values()) v.sort();
  const comps = scc([...set].sort(), v => succ.get(v));
  const compOf = new Map();
  comps.forEach((c, i) => c.forEach(n => compOf.set(n, i)));
  const indeg = new Map(comps.map((c, i) => [i, 0]));
  const csucc = new Map(comps.map((c, i) => [i, new Set()]));
  for (const [v, ws] of succ) for (const w of ws) { const a = compOf.get(v), b = compOf.get(w); if (a !== b && !csucc.get(a).has(b)) { csucc.get(a).add(b); indeg.set(b, indeg.get(b) + 1); } }
  const key = i => { const c = comps[i]; return [Math.min(...c.map(rank)), c[0]]; };
  const ready = [...indeg].filter(([, d]) => !d).map(([i]) => i);
  const out = [];
  const pick = () => { ready.sort((a, b) => { const ka = key(a), kb = key(b); return ka[0] - kb[0] || cmp(ka[1], kb[1]); }); return ready.shift(); };
  while (ready.length) {
    const i = pick();
    out.push(...comps[i]);
    for (const j of csucc.get(i)) { indeg.set(j, indeg.get(j) - 1); if (!indeg.get(j)) ready.push(j); }
  }
  return { order: out, cycles: comps.filter(c => c.length > 1) };
}

/* ============================ validation ============================ */
function validate(graph) {
  const { spec, nodes, edges } = graph;
  const f = graph.findings.slice();
  const find = (severity, code, subject, message) => f.push({ severity, code, subject, message });

  /* constraints are VERBATIM: the quote must still be in its source, or the pack
     would be carrying a law the source no longer states (provenance broken) */
  for (const c of spec.constraints || []) {
    const src = graph.byPath.get(c.source);
    if (!src) { find("error", "CONSTRAINT_SOURCE_MISSING", c.id, "source " + c.source + " is not a registered artifact"); continue; }
    let text = fs.readFileSync(path.join(graph.root || process.cwd(), c.source), "utf8");
    if (/\.json$/.test(c.source)) { try { const leaves = []; (function walk(v) { if (typeof v === "string") leaves.push(v); else if (v && typeof v === "object") for (const k of Object.keys(v)) walk(v[k]); })(JSON.parse(text)); text = leaves.join("\n"); } catch (e) { } }
    const norm = s => String(s).replace(/\*\*/g, "").replace(/\s+/g, " ").trim();
    if (!norm(text).includes(norm(c.quote))) find("error", "CONSTRAINT_QUOTE_MISSING", c.id, "the quoted text is no longer present in " + c.source + " — re-quote it or retire the constraint");
  }

  /* illegal cycles: over the acyclic edge types (normalized to prerequisite order)
     a cycle means no valid reading order exists. Legitimate cycles are declared. */
  const strict = new Set(spec.edgeTypes.filter(t => t.acyclic).map(t => t.id));
  const succ = new Map();
  for (const e of edges) {
    if (!strict.has(e.type)) continue;
    const p = prereqOf(graph, e);
    if (!p) continue;
    if (!succ.has(p.pre)) succ.set(p.pre, []);
    succ.get(p.pre).push(p.dep);
  }
  const allowed = (spec.allowedCycles || []).map(a => new Set(a.members));
  for (const comp of scc([...succ.keys()].sort(), v => succ.get(v) || [])) {
    if (comp.length < 2) continue;
    if (allowed.some(a => comp.every(m => a.has(m)))) { find("info", "ALLOWED_CYCLE", comp.join(" ↔ "), "declared legitimate in allowedCycles"); continue; }
    find("error", "ILLEGAL_CYCLE", comp.join(" ↔ "), "a cycle over acyclic edge types (" + [...strict].join(", ") + ") — no prerequisite order exists");
  }
  const loose = edges.filter(e => graph.edgeTypes.get(e.type) && !graph.edgeTypes.get(e.type).acyclic && e.type === "depends-on");
  const lsucc = new Map();
  for (const e of loose) { if (!lsucc.has(e.to)) lsucc.set(e.to, []); lsucc.get(e.to).push(e.from); }
  const lc = scc([...lsucc.keys()].sort(), v => lsucc.get(v) || []).filter(c => c.length > 1);
  if (lc.length) find("info", "DEPENDENCY_CYCLES", lc.length + " cycle(s)", "depends-on cycles are legitimate (CommonJS) and collapse to one reading position: " + lc.map(c => c.length + " nodes").join(", "));

  /* conflicting authority: two artifacts at the same authority level both claiming
     to DEFINE one target, with no open conflict recording it */
  const definers = new Map();
  for (const e of edges) if (e.type === "defines") { if (!definers.has(e.to)) definers.set(e.to, []); definers.get(e.to).push(e.from); }
  const conflictPairs = new Set();
  for (const e of edges) if (e.type === "conflicts-with") conflictPairs.add(e.to);
  for (const [t, ds] of definers) {
    if (ds.length < 2) continue;
    const ranks = ds.map(d => authorityRankOf(graph, d));
    const top = Math.min(...ranks);
    if (ranks.filter(r => r === top).length > 1 && !ds.some(d => conflictPairs.has(d))) find("error", "CONFLICTING_AUTHORITY", t, "defined by " + ds.join(", ") + " at the same authority level, and no conflict records it");
  }

  /* every node carries a declared lifecycle and an owner */
  const lifecycles = new Set((spec.lifecycles || []).map(l => l.id));
  for (const n of nodes.values()) {
    if (!lifecycles.has(n.lifecycle)) find("error", "UNKNOWN_LIFECYCLE", n.id, "lifecycle '" + n.lifecycle + "' is not one of lifecycles[]");
    if (!n.owner) find("error", "NO_OWNER", n.id, "no owner is declared for this artifact's class");
  }

  /* supersession is explicit, one-way, and fully recorded: every superseded
     artifact names its successor, effective revision, reason, the disposition of
     its unique information, the migration of references and whether it must be
     retained (§15.6) */
  const records = new Map((spec.supersessions || []).map(s => [graph.byPath.has(s.artifact) ? graph.byPath.get(s.artifact).id : s.artifact, s]));
  for (const s of spec.supersessions || []) {
    for (const k of ["artifact", "successors", "effective", "reason", "disposition", "referenceMigration", "retention"]) if (!s[k] || (Array.isArray(s[k]) && !s[k].length)) find("error", "SUPERSESSION_INCOMPLETE", s.id, "missing " + k);
    const id = graph.byPath.has(s.artifact) ? graph.byPath.get(s.artifact).id : s.artifact;
    if (!nodes.has(id)) find("error", "SUPERSESSION_UNKNOWN_ARTIFACT", s.id, s.artifact + " is not registered");
    else if (!["superseded", "historical-evidence", "retired"].includes(nodes.get(id).lifecycle)) find("error", "SUPERSEDED_STILL_ACTIVE", id, "has a supersession record (" + s.id + ") but its lifecycle is " + nodes.get(id).lifecycle);
  }
  for (const n of nodes.values()) if (n.lifecycle === "superseded" && !records.has(n.id)) find("error", "SUPERSESSION_UNRECORDED", n.id, "marked superseded but no supersessions[] record names its successor, reason and disposition");

  /* open conflicts are always reported — never silent */
  for (const c of spec.conflicts || []) if (c.status !== "resolved") find("warning", "OPEN_CONFLICT", c.id, c.title);

  return sortFindings(f);
}
function authorityRankOf(graph, id) { const n = graph.nodes.get(id); return n ? authorityRank(graph.spec, n.authority) : 99; }
function sortFindings(f) {
  const sev = { error: 0, warning: 1, info: 2 };
  return f.sort((a, b) => sev[a.severity] - sev[b.severity] || cmp(a.code, b.code) || cmp(String(a.subject), String(b.subject)) || cmp(a.message, b.message));
}

module.exports = {
  SPEC_PATH, SPEC_SCHEMA, loadSpec, specProblems, listFiles, build, validate, select, closure, impact,
  orderPrereqFirst, scc, prereqOf, git, sha256, maskJS, handoffProblems, HANDOFF_SCHEMA, HANDOFF_STATUSES, globToRe, matchAny, authorityRank, cmp, byKey, EXTRACTORS
};
