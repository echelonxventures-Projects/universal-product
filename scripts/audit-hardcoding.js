/* LUXORA Platform — hard-coding audit.

   The constitution allows only kernel concepts (Entity, Registry, Context, Policy, Rule,
   Decision, State, Event, Identity, Time…) in code; every business vocabulary must come from a
   registry. This script finds where code still names that vocabulary.

   The vocabulary is not guessed: the script boots the platform on a throwaway database and
   reads what the registries actually hold — provider ids, countries, currencies, capability
   keys, platform kinds, roles, and the key of every registry list entry. Each literal in the
   code that equals one of those is classified by how it is used:

     branch     logic decides on it (=== / !== / case / includes / startsWith / a capability or
                module looked up by name)                                  → highest impact
     fallback   a default the code falls back to (|| "x", ?? "x", = "x")
     seed       a seed row written in code (key: "x" / id: "x" inside a constant)
     other      any other mention

   Usage: node scripts/audit-hardcoding.js [--json out.json] [--md out.md] */
"use strict";
const fs = require("fs");
const path = require("path");
const os = require("os");

const ROOT = path.join(__dirname, "..");
const TMP = path.join(os.tmpdir(), "hcaudit-" + process.pid + ".db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
process.env.LX_DB = TMP;
const silence = console.log; console.log = () => { };
const db = require(path.join(ROOT, "lib", "db.js"));
console.log = silence;

const arg = k => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : null; };
const J = v => { try { return JSON.parse(v); } catch (e) { return null; } };

/* ---------- the vocabulary, from the registries ---------- */
const vocab = new Map();   /* literal → Set(category) */
const add = (lit, cat) => { const k = String(lit == null ? "" : lit); if (!k) return; if (!vocab.has(k)) vocab.set(k, new Set()); vocab.get(k).add(cat); };
for (const r of db.all("SELECT id, kind FROM provider_defs")) add(r.id, "provider:" + r.kind);
for (const r of require(path.join(ROOT, "lib", "registry.js")).countries()) { add(r.code, "country"); add(r.currency, "currency"); }
for (const r of db.all("SELECT code FROM currencies")) add(r.code, "currency");
for (const r of db.all("SELECT key FROM platform_capabilities")) add(r.key, "capability");
try { for (const m of db.all("SELECT manifest FROM modules")) for (const c of (J(m.manifest) || {}).capabilities || []) add(c, "module-capability"); } catch (e) { }
for (const r of db.all("SELECT name, items FROM meta_lists")) {
  const items = J(r.items);
  const each = Array.isArray(items) ? items : (items && typeof items === "object" ? Object.keys(items) : []);
  for (const it of each) {
    const k = it && typeof it === "object" ? it.key : it;
    /* a status / state / transition list is a state machine's vocabulary */
    const cat = r.name === "deployModes" ? "platform-kind" : /(Statuses|States|Transitions|lifecycle)$/i.test(r.name) ? "state:" + r.name : "registry:" + r.name;
    if (typeof k === "string") add(k, cat);
  }
}
try { for (const r of require(path.join(ROOT, "lib", "authz.js")).STORE_ROLES) add(r.key, "role"); } catch (e) { }
/* words that are also the language of the code itself — never business vocabulary */
const KERNEL = new Set(["id", "key", "name", "label", "type", "kind", "value", "values", "status", "active", "inactive", "enabled", "disabled",
  "all", "any", "none", "default", "true", "false", "null", "yes", "no", "on", "off", "ok", "error", "read", "write", "admin", "platform", "store",
  "GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "object", "string", "number", "boolean", "function", "undefined", "array", "json", "text", "date",
  "select", "multi", "money", "bool", "file", "image", "email", "phone", "url", "code", "tenant", "user", "users", "owner", "self", "system",
  "live", "sandbox", "test", "draft", "published", "pending", "open", "closed", "new", "in", "out", "up", "down", "min", "max", "sum", "count",
  "asc", "desc", "and", "or", "not", "eq", "gt", "lt", "gte", "lte", "has", "exists", "list", "item", "items", "data", "meta", "config", "settings",
  "production", "development", "staging", "web", "api", "app", "info", "warn", "success", "failed", "queued", "done", "ready", "start", "end", "from", "to", "at", "by", "of", "for", "per"]);

/* ---------- the code ---------- */
const FILES = ["server.js"].concat(fs.readdirSync(path.join(ROOT, "lib")).filter(f => f.endsWith(".js")).map(f => "lib/" + f))
  .concat(fs.readdirSync(path.join(ROOT, "public", "js")).filter(f => f.endsWith(".js")).map(f => "public/js/" + f));
const stripComments = src => src.replace(/\/\*[\s\S]*?\*\//g, m => m.replace(/[^\n]/g, " ")).replace(/(^|[^:"'`\\])\/\/[^\n]*/g, (m, p) => p + " ".repeat(m.length - p.length));
const LIT = /(["'])((?:(?!\1)[^\\\n]){1,60})\1/g;
function classify(line, lit) {
  const q = lit.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const L = "[\"']" + q + "[\"']";
  /* a console view / nav key that happens to share a vocabulary word */
  if (new RegExp("\\b(view|tab|v|goipTab|section)\\s*===\\s*" + L).test(line)) return "route";
  /* an engine looking up the capability it IS (its identity — the same shape as a binding point) */
  if (new RegExp("(\\.cap|\\.on|hasCap|capability)\\(\\s*[^,()]+,\\s*" + L + "\\s*\\)").test(line)) return "identity";
  if (new RegExp("(===|!==|==|!=)\\s*" + L + "|" + L + "\\s*(===|!==|==|!=)|case\\s+" + L + "|\\.(includes|startsWith|endsWith|indexOf)\\(\\s*" + L + "|(hasCap|\\.on|\\.cap|params|capability|cap)\\([^)]*,\\s*" + L).test(line)) return "branch";
  if (new RegExp("(\\|\\||\\?\\?)\\s*" + L + "|[^=!<>]=\\s*" + L + "\\s*[;,)]").test(line)) return "fallback";
  if (new RegExp("\\b(key|id|provider|code|kind)\\s*:\\s*" + L).test(line)) return "seed";
  return "other";
}
const hits = [];
for (const f of FILES) {
  const src = stripComments(fs.readFileSync(path.join(ROOT, f), "utf8"));
  const lines = src.split("\n");
  lines.forEach((line, i) => {
    let m; LIT.lastIndex = 0;
    while ((m = LIT.exec(line))) {
      const lit = m[2];
      if (KERNEL.has(lit) || lit.length < 2 || !vocab.has(lit)) continue;
      hits.push({ file: f, line: i + 1, literal: lit, categories: [...vocab.get(lit)], use: classify(line, lit), text: line.trim().slice(0, 160) });
    }
  });
}
/* seed-sized constants: a top-level `const X = [` / `{` block of 20+ lines of literal data */
const seeds = [];
for (const f of FILES.filter(f => f.startsWith("lib/"))) {
  const lines = fs.readFileSync(path.join(ROOT, f), "utf8").split("\n");
  for (let i = 0; i < lines.length; i++) {
    const m = /^const ([A-Z][A-Z0-9_]+)\s*=\s*([\[{])\s*$|^const ([A-Z][A-Z0-9_]+)\s*=\s*([\[{]).*$/.exec(lines[i]);
    if (!m) continue;
    const name = m[1] || m[3];
    let depth = 0, j = i;
    for (; j < lines.length; j++) { for (const ch of lines[j]) { if (ch === "[" || ch === "{") depth++; else if (ch === "]" || ch === "}") depth--; } if (depth <= 0) break; }
    if (j - i + 1 >= 20) seeds.push({ file: f, line: i + 1, name, lines: j - i + 1 });
    i = j;
  }
}

/* ---------- report ---------- */
const by = (xs, f) => xs.reduce((o, x) => { const k = f(x); (o[k] = o[k] || []).push(x); return o; }, {});
const USES = ["branch", "identity", "route", "fallback", "seed", "other"];
/* the most telling category when a value belongs to several vocabularies */
const RANK = ["provider", "country", "currency", "platform-kind", "role", "capability", "module-capability", "state", "registry"];
const catOf = h => { const cs = h.categories.map(c => c.split(":")[0]); return RANK.find(r => cs.includes(r)) || cs[0]; };
const summary = { files: FILES.length, vocabulary: vocab.size, literals: hits.length, byUse: Object.fromEntries(USES.map(u => [u, hits.filter(h => h.use === u).length])),
  seedConstants: { count: seeds.length, lines: seeds.reduce((n, s) => n + s.lines, 0) } };
const byFile = Object.entries(by(hits.filter(h => h.use === "branch" || h.use === "fallback"), h => h.file)).map(([f, xs]) => ({ file: f, branch: xs.filter(x => x.use === "branch").length, fallback: xs.filter(x => x.use === "fallback").length })).sort((a, b) => (b.branch * 3 + b.fallback) - (a.branch * 3 + a.fallback));
const byCat = Object.entries(by(hits.filter(h => h.use === "branch"), catOf)).map(([c, xs]) => ({ category: c, branch: xs.length, distinct: new Set(xs.map(x => x.literal)).size })).sort((a, b) => b.branch - a.branch);
const topLits = Object.entries(by(hits.filter(h => h.use === "branch"), h => h.literal)).map(([l, xs]) => ({ literal: l, category: xs[0].categories.join(", "), branch: xs.length, files: [...new Set(xs.map(x => x.file))].length })).sort((a, b) => b.branch - a.branch);

const jsonOut = arg("--json"), mdOut = arg("--md");
if (jsonOut) fs.writeFileSync(jsonOut, JSON.stringify({ generated: new Date().toISOString(), summary, byFile, byCategory: byCat, topLiterals: topLits, seedConstants: seeds, hits }, null, 1));
const md = [];
md.push("# Hard-coding audit", "", "Generated by `node scripts/audit-hardcoding.js` on " + new Date().toISOString().slice(0, 10) + ". The vocabulary (" + vocab.size + " values) is read from the seeded registries, so it grows as the registries do.", "");
md.push("| | Count |", "|---|---:|", "| Files scanned | " + summary.files + " |", "| Registry values named in code | " + summary.literals + " |",
  "| — logic decides on them (branch) | " + summary.byUse.branch + " |", "| — an engine naming the capability it is (identity) | " + summary.byUse.identity + " |", "| — console view keys (route) | " + summary.byUse.route + " |", "| — defaults / fallbacks | " + summary.byUse.fallback + " |", "| — seed rows written in code | " + summary.byUse.seed + " |", "| — other mentions | " + summary.byUse.other + " |",
  "| Seed-sized constants (20+ lines) | " + seeds.length + " (" + summary.seedConstants.lines + " lines) |", "");
md.push("## Logic deciding on a named value, by vocabulary", "", "| Vocabulary | Branches | Distinct values |", "|---|---:|---:|", ...byCat.map(c => `| ${c.category} | ${c.branch} | ${c.distinct} |`), "");
md.push("## Files, ranked (branches weigh 3×, fallbacks 1×)", "", "| File | Branches | Fallbacks |", "|---|---:|---:|", ...byFile.slice(0, 30).map(f => `| \`${f.file}\` | ${f.branch} | ${f.fallback} |`), "");
md.push("## Most-branched-on values", "", "| Value | Vocabulary | Branches | Files |", "|---|---|---:|---:|", ...topLits.slice(0, 40).map(t => `| \`${t.literal}\` | ${t.category} | ${t.branch} | ${t.files} |`), "");
md.push("## Seed data still written as code", "", "| Constant | File | Lines |", "|---|---|---:|", ...seeds.sort((a, b) => b.lines - a.lines).slice(0, 40).map(s => `| \`${s.name}\` | \`${s.file}:${s.line}\` | ${s.lines} |`), "");
md.push("## Every branch", "", "| Where | Value | Vocabulary | Code |", "|---|---|---|---|", ...hits.filter(h => h.use === "branch").map(h => `| \`${h.file}:${h.line}\` | \`${h.literal}\` | ${h.categories.join(", ")} | \`${h.text.replace(/\|/g, "\\|").replace(/`/g, "'")}\` |`), "");
if (mdOut) fs.writeFileSync(mdOut, md.join("\n"));
console.log(JSON.stringify({ summary, byCategory: byCat.slice(0, 12), topFiles: byFile.slice(0, 12) }, null, 1));
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
process.exit(0);
