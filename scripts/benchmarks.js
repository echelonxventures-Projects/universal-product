/* How the platform stands against the products it is measured against (lib/seed/benchmarks.json):
   each feature's evidence — a capability, a table — is checked against the code, so a feature is
   present, partial (built, with a stated gap) or missing. Prints one block per benchmark.
   Usage: node scripts/benchmarks.js [--json] */
"use strict";
const fs = require("fs"), path = require("path");
const ROOT = path.join(__dirname, "..");
const B = require(path.join(ROOT, "lib", "seed", "benchmarks.json"));
const CAPS = new Set(require(path.join(ROOT, "lib", "seed", "capabilities.json")).CATALOG.map(c => c.key));
const TABLES = new Set([...fs.readFileSync(path.join(ROOT, "schema.sql"), "utf8").matchAll(/CREATE TABLE (?:IF NOT EXISTS )?([a-z_0-9]+)/g)].map(m => m[1]));
const has = e => e.startsWith("c:") ? CAPS.has(e.slice(2)) : e.startsWith("t:") ? TABLES.has(e.slice(2)) : e.startsWith("f:") ? fs.existsSync(path.join(ROOT, e.slice(2))) : false;
function measure() {
  return B.benchmarks.map(b => {
    const features = b.features.map(x => {
      const absent = x.e.filter(e => !has(e));
      const status = absent.length === x.e.length ? "missing" : absent.length ? "partial" : x.gap ? "partial" : "present";
      return { feature: x.f, status, absent, gap: x.gap || (absent.length ? x.gapIfMissing || null : null) };
    });
    const n = s => features.filter(f => f.status === s).length;
    return { key: b.key, title: b.title, present: n("present"), partial: n("partial"), missing: n("missing"), total: features.length, features };
  });
}
module.exports = { measure, has };
if (require.main === module) {
  const out = measure();
  if (process.argv.includes("--json")) { console.log(JSON.stringify(out, null, 1)); process.exit(0); }
  const mark = { present: "✓", partial: "◐", missing: "✗" };
  for (const b of out) {
    console.log(`\n${b.title} — ${b.present} present, ${b.partial} partial, ${b.missing} missing of ${b.total}`);
    for (const f of b.features) if (f.status !== "present") console.log(`  ${mark[f.status]} ${f.feature}${f.gap ? " — " + f.gap : ""}`);
  }
  const all = out.reduce((a, b) => ({ p: a.p + b.present, h: a.h + b.partial, m: a.m + b.missing, t: a.t + b.total }), { p: 0, h: 0, m: 0, t: 0 });
  console.log(`\nAll: ${all.p} present, ${all.h} partial, ${all.m} missing of ${all.t}`);
}
