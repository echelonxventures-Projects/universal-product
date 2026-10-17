/* LUXORA Platform — seed data lives in lib/seed/*.json, not in JavaScript.
   The registries are seeded from those files; engine code holds only the kernel: handler and
   implementation tables, route wiring, the UID table list. This gate fails if a seed-sized
   literal (20+ lines of data) reappears in lib/, unless it is a declared kernel table. */
"use strict";
const fs = require("fs");
const path = require("path");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const LIB = path.join(__dirname, "..", "lib");
/* modules below may boot the database: never the developer's own */
const TMP = path.join(require("os").tmpdir(), "seeds-" + process.pid + ".db");
process.env.LX_DB = TMP;

/* kernel tables: code (implementations, wiring), not business data */
const KERNEL = {
  "goip.js": ["IMPL", "GOIP_HANDLERS", "INTEL", "REGISTRIES"],
  "authz.js": ["ROUTE_SECTION"], "api.js": ["STORE_ROUTE_SECTION"], "uid.js": ["TABLES"], "rules.js": ["PROVIDERS"]
};

console.log("▸ SEED FILES ARE DATA");
const seeds = fs.readdirSync(path.join(LIB, "seed")).filter(f => f.endsWith(".json"));
let parsed = 0;
for (const f of seeds) { try { JSON.parse(fs.readFileSync(path.join(LIB, "seed", f), "utf8")); parsed++; } catch (e) { ok(false, f + " parses", e.message); } }
ok(parsed === seeds.length && seeds.length >= 10, "every seed file parses (" + seeds.length + " files)");

console.log("▸ THE GATE: NO SEED-SIZED LITERAL IN ENGINE CODE");
const found = [];
for (const f of fs.readdirSync(LIB).filter(f => f.endsWith(".js"))) {
  const lines = fs.readFileSync(path.join(LIB, f), "utf8").split("\n");
  for (let i = 0; i < lines.length; i++) {
    const m = /^const ([A-Z][A-Z0-9_]+)\s*=\s*[\[{]/.exec(lines[i]);
    if (!m) continue;
    let depth = 0, j = i, inCom = false, inStr = null;
    for (; j < lines.length; j++) {
      const L = lines[j]; if (inStr !== "`") inStr = null;
      for (let k = 0; k < L.length; k++) {
        const ch = L[k], nx = L[k + 1];
        if (inCom) { if (ch === "*" && nx === "/") { inCom = false; k++; } continue; }
        if (inStr) { if (ch === "\\") { k++; continue; } if (ch === inStr) inStr = null; continue; }
        if (ch === "/" && nx === "/") break;
        if (ch === "/" && nx === "*") { inCom = true; k++; continue; }
        if (ch === '"' || ch === "'" || ch === "`") { inStr = ch; continue; }
        if ("[{(".includes(ch)) depth++; else if ("]})".includes(ch)) depth--;
      }
      if (depth <= 0) break;
    }
    if (j - i + 1 >= 20 && !(KERNEL[f] || []).includes(m[1])) found.push(f + ":" + (i + 1) + " " + m[1] + " (" + (j - i + 1) + " lines)");
    i = j;
  }
}
ok(found.length === 0, "no business seed literal of 20+ lines remains in lib/", found);

console.log("▸ THE MOVED CONSTANTS LOAD FROM THEIR SEED FILES");
const caps = require("../lib/capabilities.js"), meta = require("../lib/meta.js"), settings = require("../lib/settings.js");
const capSeed = JSON.parse(fs.readFileSync(path.join(LIB, "seed", "capabilities.json"), "utf8"));
ok(Array.isArray(capSeed.CATALOG) && capSeed.CATALOG.length > 50 && caps.catalog ? true : false, "the capability catalog is a seed file");
ok(meta.INDUSTRIES.length > 10 && settings.DEFAULTS.brand, "industries and settings defaults load from their seed files");

for (const x of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + x, { force: true }); } catch (e) { } }
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
