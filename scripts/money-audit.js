/* LUXORA Platform — money inventory (PR-016).
   Two halves, written to docs/money-inventory.generated.md (`node scripts/money-audit.js --md`):
     1. every REAL column of the schema (schema.sql), classified by its meaning — money amount,
        unit price / monetary rate, exchange rate, quantity, percentage or ratio, measurement —
        from scripts/money-inventory.json, the reviewed classification. A REAL column the
        classification does not name is reported as UNKNOWN: it must be classified, never assumed
     2. every place code rounds or scales a number (toFixed, Math.round/floor/ceil, × or ÷ a
        power of ten), found by a tokenizer — strings, comments, regular expressions and template
        text are removed first, so a match is code, not prose — and classified by the identifiers
        around it (money words vs measurement words)
   `--check` exits 1 when a column is unclassified or when a payment-spine module (the
   classification's `spineModules`) rounds money outside lib/money.js. */
"use strict";
const fs = require("fs"), path = require("path");
const ROOT = path.join(__dirname, "..");
const CLASS = require("./money-inventory.json");

/* ---------- a JS tokenizer good enough to tell code from text ---------- */
function codeOnly(src) {
  let out = "", i = 0, prev = "";
  const n = src.length;
  const regexAllowed = () => /[(,=:[!&|?{};+\-*%<>~^]$|^$|\b(return|typeof|case|do|else|in|of|new|delete|void|throw|yield|await)$/.test(prev.trimEnd());
  while (i < n) {
    const c = src[i], d = src[i + 1];
    if (c === "/" && d === "/") { while (i < n && src[i] !== "\n") i++; continue; }
    if (c === "/" && d === "*") { const e = src.indexOf("*/", i + 2); const chunk = src.slice(i, e < 0 ? n : e + 2); out += chunk.replace(/[^\n]/g, " "); i = e < 0 ? n : e + 2; continue; }
    if (c === "'" || c === '"') { let j = i + 1; while (j < n && src[j] !== c) { if (src[j] === "\\") j++; j++; } out += c + " ".repeat(Math.max(0, j - i - 1)) + c; i = j + 1; prev = "x"; continue; }
    if (c === "`") {
      let j = i + 1; out += "`";
      while (j < n && src[j] !== "`") {
        if (src[j] === "\\") { out += "  "; j += 2; continue; }
        if (src[j] === "$" && src[j + 1] === "{") {
          let depth = 1, k = j + 2; while (k < n && depth) { if (src[k] === "{") depth++; else if (src[k] === "}") depth--; k++; }
          out += "${" + codeOnly(src.slice(j + 2, k - 1)) + "}"; j = k; continue;
        }
        out += src[j] === "\n" ? "\n" : " "; j++;
      }
      out += "`"; i = j + 1; prev = "x"; continue;
    }
    if (c === "/" && regexAllowed()) {
      let j = i + 1, cls = false;
      while (j < n && (cls || src[j] !== "/") && src[j] !== "\n") { if (src[j] === "\\") j++; else if (src[j] === "[") cls = true; else if (src[j] === "]") cls = false; j++; }
      if (src[j] === "/") { j++; while (/[a-z]/i.test(src[j] || "")) j++; out += " ".repeat(j - i); i = j; prev = "x"; continue; }
    }
    out += c; if (!/\s/.test(c)) prev = (prev + c).slice(-12); i++;
  }
  return out;
}

const MONEY = new RegExp("\\b(" + CLASS.codeWords.money.join("|") + ")", "i");
const MEASURE = new RegExp("\\b(" + CLASS.codeWords.measure.join("|") + ")", "i");
const PATTERNS = [
  { kind: "toFixed", re: /\.toFixed\s*\(\s*(\d*)\s*\)/g },
  { kind: "Math.round", re: /\bMath\.(round|floor|ceil|trunc)\s*\(/g },
  { kind: "× or ÷ 100/1000", re: /[*/]\s*(100|1000|1e2|1e3)\b(?!\s*[.\d])/g }
];
function scanFile(rel) {
  const src = fs.readFileSync(path.join(ROOT, rel), "utf8"), code = codeOnly(src);
  const lines = code.split("\n"), real = src.split("\n");
  const hits = [];
  lines.forEach((ln, i) => {
    for (const p of PATTERNS) {
      p.re.lastIndex = 0; let m;
      while ((m = p.re.exec(ln))) {
        /* the expression the call rounds: the code on the line up to the match */
        const ctx = ln.slice(Math.max(0, m.index - 160), m.index + m[0].length + 40);
        const money = MONEY.test(ctx), measure = MEASURE.test(ctx);
        hits.push({ file: rel, line: i + 1, kind: p.kind, digits: m[1], cls: money && !measure ? "money" : measure && !money ? "measurement" : money && measure ? "mixed" : "other", text: real[i].trim().slice(0, 160) });
      }
    }
  });
  return hits;
}
function walk(dir, out) {
  for (const e of fs.readdirSync(path.join(ROOT, dir), { withFileTypes: true })) {
    const rel = path.join(dir, e.name);
    if (e.isDirectory()) { if (!/node_modules|vendor/.test(rel)) walk(rel, out); }
    else if (/\.js$/.test(e.name)) out.push(rel);
  }
  return out;
}

/* ---------- the schema's REAL columns ---------- */
function realColumns() {
  const sql = fs.readFileSync(path.join(ROOT, "schema.sql"), "utf8");
  const out = [];
  for (const m of sql.matchAll(/CREATE TABLE "?(\w+)"? \(([\s\S]*?)\);\n/g)) {
    const body = m[2].replace(/\/\*[\s\S]*?\*\//g, "");
    for (const c of body.matchAll(/(?:^|[(,\s])"?(\w+)"?\s+REAL\b/g)) out.push({ table: m[1], column: c[1] });
  }
  return out;
}
function classify(col) {
  const key = col.table + "." + col.column;
  if (CLASS.columns[key]) return CLASS.columns[key];
  for (const r of CLASS.rules) if (new RegExp(r.match).test(key)) return { class: r.class, scope: r.scope || "", note: r.note || "", rule: r.match };
  return { class: "unknown", scope: "", note: "not classified" };
}

function run() {
  const cols = realColumns().map(c => ({ ...c, ...classify(c) }));
  const files = [...walk("lib", []), ...walk("public/js", []), "server.js"].filter(f => fs.existsSync(path.join(ROOT, f)));
  const hits = files.flatMap(scanFile);
  const spine = new Set(CLASS.spineModules);
  const spineMoney = hits.filter(h => spine.has(h.file) && h.cls === "money" && h.kind !== "× or ÷ 100/1000");
  return { cols, hits, spineMoney, files: files.length };
}
function md(r) {
  const by = (xs, k) => xs.reduce((a, x) => { (a[x[k]] = a[x[k]] || []).push(x); return a; }, {});
  const L = [];
  L.push("# Money inventory (generated)", "", "> Generated by `node scripts/money-audit.js --md` from `schema.sql`, the code and `scripts/money-inventory.json` (the reviewed classification). Do not edit by hand.", "");
  L.push("## 1. REAL columns by meaning", "");
  const cc = by(r.cols, "class");
  L.push("| Class | Columns |", "|---|---|");
  for (const k of Object.keys(cc).sort()) L.push(`| ${k} | ${cc[k].length} |`);
  L.push("", "Total REAL columns: " + r.cols.length + ".", "");
  for (const k of ["money", "unit_price", "exchange_rate", "unknown"]) {
    if (!cc[k]) continue;
    L.push("### " + k, "", "| Column | Scope | Note |", "|---|---|---|");
    for (const c of cc[k]) L.push(`| \`${c.table}.${c.column}\` | ${c.scope || ""} | ${String(c.note || "").replace(/\|/g, "\\|")} |`);
    L.push("");
  }
  L.push("Quantity, percentage/ratio and measurement columns are listed in `scripts/money-inventory.json`; they are not money and are not migrated.", "");
  L.push("## 2. Rounding and scaling sites in code", "", "Files scanned: " + r.files + ". A site is classed by the identifiers around it: `money` (money words only), `measurement`, `mixed` (both — read it), `other`.", "");
  const hk = by(r.hits, "cls");
  L.push("| Class | toFixed | Math.round/floor/ceil | × or ÷ 100/1000 |", "|---|---|---|---|");
  for (const k of ["money", "mixed", "measurement", "other"]) { const xs = hk[k] || []; L.push(`| ${k} | ${xs.filter(x => x.kind === "toFixed").length} | ${xs.filter(x => x.kind === "Math.round").length} | ${xs.filter(x => x.kind === "× or ÷ 100/1000").length} |`); }
  L.push("", "`toFixed(2)` sites in total: " + r.hits.filter(h => h.kind === "toFixed" && h.digits === "2").length + ".", "");
  L.push("### By file (money and mixed sites)", "", "| File | money | mixed | spine module |", "|---|---|---|---|");
  const spine = new Set(CLASS.spineModules);
  const bf = by(r.hits.filter(h => h.cls === "money" || h.cls === "mixed"), "file");
  for (const f of Object.keys(bf).sort((a, b) => bf[b].length - bf[a].length)) L.push(`| \`${f}\` | ${bf[f].filter(x => x.cls === "money").length} | ${bf[f].filter(x => x.cls === "mixed").length} | ${spine.has(f) ? "yes" : ""} |`);
  L.push("", "### Payment-spine modules: money rounded outside lib/money.js", "");
  if (!r.spineMoney.length) L.push("None.");
  else { L.push("| Site | Kind | Code |", "|---|---|---|"); for (const h of r.spineMoney) L.push(`| \`${h.file}:${h.line}\` | ${h.kind} | \`${h.text.replace(/\|/g, "\\|").replace(/`/g, "'")}\` |`); }
  L.push("");
  return L.join("\n");
}

if (require.main === module) {
  const r = run();
  if (process.argv.includes("--md")) { fs.writeFileSync(path.join(ROOT, "docs", "money-inventory.generated.md"), md(r)); console.log("docs/money-inventory.generated.md written"); }
  const unknown = r.cols.filter(c => c.class === "unknown");
  console.log(`REAL columns ${r.cols.length} (${unknown.length} unclassified) · rounding sites ${r.hits.length} (money ${r.hits.filter(h => h.cls === "money").length}, mixed ${r.hits.filter(h => h.cls === "mixed").length}) · spine money sites outside lib/money.js ${r.spineMoney.length}`);
  if (process.argv.includes("--check")) {
    for (const c of unknown) console.log("  unclassified REAL column: " + c.table + "." + c.column);
    for (const h of r.spineMoney) console.log("  spine money rounding: " + h.file + ":" + h.line + "  " + h.text);
    process.exit(unknown.length || r.spineMoney.length ? 1 : 0);
  }
}
module.exports = { run, codeOnly, realColumns, classify, scanFile };
