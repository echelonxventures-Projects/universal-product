/* LUXORA Platform — the hard-coding audit only goes down.
   Runs scripts/audit-hardcoding.js and compares what it finds with the committed baseline
   (scripts/audit-baseline.json): every place logic branches on a registry value, every literal
   fallback to one, and every seed-sized constant left in lib/. A literal is counted per file and
   per value (line numbers move; the value does not), so the gate fails when:
     - a file branches on, or falls back to, a registry value more often than the baseline allows;
     - a seed-sized constant appears, or an allowed one grows.
   When a change removes hits, the gate passes and says so; record the lower count with
     npm run audit:baseline
   so the ratchet holds it. A registry that gains a value an existing literal happens to spell
   shows up here too — review it, then refresh the baseline if it is a word collision. */
"use strict";
const path = require("path");
const fs = require("fs");
const os = require("os");
const { execFileSync } = require("child_process");
const ROOT = path.join(__dirname, "..");
const BASELINE = path.join(ROOT, "scripts", "audit-baseline.json");
const OUT = path.join(os.tmpdir(), "audit-gate-" + process.pid + ".json");
const GATED = ["branch", "fallback"];

let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x, null, 1)) : ""))); };

function snapshot() {
  execFileSync(process.execPath, [path.join(ROOT, "scripts", "audit-hardcoding.js"), "--json", OUT], { cwd: ROOT, stdio: "ignore" });
  const a = JSON.parse(fs.readFileSync(OUT, "utf8")); fs.rmSync(OUT, { force: true });
  const snap = { summary: { ...Object.fromEntries(GATED.map(u => [u, a.summary.byUse[u]])), seedConstants: a.summary.seedConstants }, hits: {}, seedConstants: {} };
  for (const u of GATED) snap.hits[u] = {};
  for (const h of a.hits) if (GATED.includes(h.use)) { const k = h.file + " · " + h.literal; snap.hits[h.use][k] = (snap.hits[h.use][k] || 0) + 1; }
  for (const c of a.seedConstants) snap.seedConstants[c.file + " · " + c.name] = c.lines;
  for (const u of GATED) snap.hits[u] = Object.fromEntries(Object.entries(snap.hits[u]).sort());
  return snap;
}

const now = snapshot();
if (process.argv.includes("--update")) {
  fs.writeFileSync(BASELINE, JSON.stringify(now, null, 1) + "\n");
  console.log("baseline written: " + GATED.map(u => u + " " + now.summary[u]).join(", ") + ", seed constants " + now.summary.seedConstants.count);
  process.exit(0);
}
let base;
try { base = JSON.parse(fs.readFileSync(BASELINE, "utf8")); } catch (e) { console.log("  ✗ no baseline at scripts/audit-baseline.json — run npm run audit:baseline"); process.exit(1); }

console.log("▸ NO NEW BRANCH OR FALLBACK ON A REGISTRY VALUE");
for (const u of GATED) {
  const grew = Object.entries(now.hits[u]).filter(([k, n]) => n > (base.hits[u][k] || 0)).map(([k, n]) => k + " (" + (base.hits[u][k] || 0) + " → " + n + ")");
  ok(grew.length === 0, u + ": " + now.summary[u] + " (baseline " + base.summary[u] + ")", grew);
}
console.log("▸ NO NEW SEED-SIZED CONSTANT IN lib/");
const grown = Object.entries(now.seedConstants).filter(([k, n]) => n > (base.seedConstants[k] || 0)).map(([k, n]) => k + " (" + (base.seedConstants[k] || 0) + " → " + n + " lines)");
ok(grown.length === 0, "seed-sized constants: " + now.summary.seedConstants.count + " (baseline " + base.summary.seedConstants.count + ")", grown);

const lower = GATED.some(u => now.summary[u] < base.summary[u]) || now.summary.seedConstants.count < base.summary.seedConstants.count;
if (lower && !failed) console.log("  ↓ below the baseline — run npm run audit:baseline to hold the lower count");
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
