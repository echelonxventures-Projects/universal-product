/* LUXORA Platform — the consoles render what the server declares (finding 7).
   An entity field declares its structured editor (`editor`), the column of a referenced row it
   stores (`refValue`) and how its list column shows (`display`: lead, badge); the taxonomy
   levels are the taxonomyLevels registry (its `root` is what a storefront browses from); a
   pre-selected option is the row a registry flags default. The gate below fails if a console
   branches on a field key, a taxonomy level, a currency code or a declared default again. */
"use strict";
const path = require("path");
const fs = require("fs");
const os = require("os");
const TMP = path.join(os.tmpdir(), "console-meta-" + process.pid + ".db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
process.env.LX_DB = TMP;
const silence = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = silence;
const reg = require("../lib/registry.js");
const dflt = require("../lib/defaults.js");
const { ENTITY_DEFS, PARITY_DEFS } = require("../lib/entity.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const JS = f => fs.readFileSync(path.join(__dirname, "..", "public", "js", f), "utf8").replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/[^\n]*/g, "");

try {
  const defs = { ...ENTITY_DEFS, ...PARITY_DEFS };
  const fields = Object.values(defs).flatMap(d => d.fields || []);

  console.log("▸ TAXONOMY LEVELS ARE A REGISTRY");
  const levels = reg.list("taxonomyLevels");
  ok(Array.isArray(levels) && levels.length >= 3 && levels.filter(l => l.root).length === 1, "taxonomyLevels is seeded with one root (" + (levels || []).length + " levels)");
  ok(dflt.of("taxonomyLevels") && levels.some(l => l.key === dflt.of("taxonomyLevels")), "a node saved with no level takes the flagged default: " + dflt.of("taxonomyLevels"));
  const root = levels.find(l => l.root).key;
  ok(db.get("SELECT COUNT(*) c FROM taxonomy WHERE level=?", root).c > 0, "the seeded tree's top nodes sit at the root level");

  console.log("▸ ENTITY FIELDS DECLARE HOW THE CONSOLE SHOWS THEM");
  const admin = JS("admin.js"), platform = JS("platform.js");
  const edBlock = (/const EDITORS = \{([\s\S]*?)\n\};/.exec(admin) || [])[1] || "";
  const editors = new Set([...edBlock.matchAll(/^\s*([a-z_]+):/gm)].map(m => m[1]));
  const declared = [...new Set(fields.filter(f => f.editor).map(f => f.editor))];
  ok(declared.length >= 2 && declared.every(e => editors.has(e)), "every declared editor is one the console mounts", { declared, editors: [...editors] });
  ok(fields.filter(f => f.type === "json" && (f.key === "media" || f.key === "attrs")).every(f => f.editor === f.key), "structured media and attribute fields declare their editor");
  ok(fields.filter(f => f.type === "ref:brand").every(f => f.refValue === "label"), "the product's brand field stores the brand's label (refValue)");
  const lead = Object.entries(defs).filter(([, d]) => (d.fields || []).filter(f => f.display === "lead").length > 1).map(([k]) => k);
  ok(lead.length === 0 && fields.some(f => f.display === "lead") && fields.some(f => f.display === "badge"), "each entity has at most one lead column; badge columns are declared", lead);
  const data = fs.readFileSync(path.join(__dirname, "..", "lib", "api.js"), "utf8");
  ok(/fields: \(def\.fields \|\| \[\]\)\.filter\(f => f\.list\)\.map\(f => \(\{[^}]*display/.test(data), "the platform data index serves each field's display");

  console.log("▸ THE GATE: NO CONSOLE BRANCHES ON A FIELD KEY, LEVEL, CURRENCY OR DECLARED DEFAULT");
  const codes = new Set(db.all("SELECT code FROM currencies").map(r => r.code));
  const dkeys = new Set(Object.values(require("../lib/seed/defaults.json").lists));
  const lkeys = new Set(levels.map(l => l.key));
  /* kernel: the tenant scope column every entity carries */
  const KERNEL_COLS = new Set(["tenant_id"]);
  const hits = [];
  for (const f of fs.readdirSync(path.join(__dirname, "..", "public", "js")).filter(f => f.endsWith(".js"))) {
    const src = JS(f);
    for (const m of src.matchAll(/\b(?:f|field)\.(?:key|options)\s*[!=]==\s*["']([A-Za-z_]+)["']/g)) hits.push(f + ": " + m[0]);
    for (const m of src.matchAll(/\.level\s*[!=]==\s*["']([A-Za-z_]+)["']/g)) if (lkeys.has(m[1])) hits.push(f + ": " + m[0]);
    for (const m of src.matchAll(/[!=]==\s*["']([A-Za-z_]+)["']/g)) if (codes.has(m[1]) || dkeys.has(m[1])) hits.push(f + ": " + m[0]);
    for (const m of src.matchAll(/\[([^\]]*)\]\.includes\(f\.key\)/g)) if (m[1].split(",").map(x => x.trim().replace(/["']/g, "")).some(k => k && !KERNEL_COLS.has(k))) hits.push(f + ": " + m[0]);
  }
  ok(hits.length === 0, "the consoles read declarations, not keys", [...new Set(hits)]);
  ok(!/kind=\$\{kind === /.test(JS("app.js")) && !/if \(p === "home"\)/.test(JS("app.js")), "the storefront routes by its page table and votes by each button's endpoint");
} catch (e) { failed++; console.log("  ✗ threw: " + (e && e.stack || e)); }
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
