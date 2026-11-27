/* The benchmarks the platform is measured against (lib/seed/benchmarks.json, scripts/benchmarks.js):
   every feature names evidence that can be checked, and what is present never goes down. */
"use strict";
const path = require("path");
const B = require("../lib/seed/benchmarks.json"), M = require("../scripts/benchmarks.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + JSON.stringify(x).slice(0, 300) : ""))); };
console.log("▸ BENCHMARKS");
const all = B.benchmarks.flatMap(b => b.features);
ok(B.benchmarks.length >= 5 && all.length >= 80, "marketplace, mobility, CRM, ERP and professional services are each measured", all.length);
ok(all.every(f => f.f && Array.isArray(f.e) && f.e.length && f.e.every(e => /^[ct]:[a-z_0-9]+$/.test(e) || /^f:(lib|test|scripts)\/[a-z0-9/_.-]+\.js$/.test(e))), "every feature names checkable evidence: a capability (c:), a table (t:) or an engine and its test (f:)");
ok(new Set(B.benchmarks.map(b => b.key)).size === B.benchmarks.length, "each benchmark once");
const out = M.measure(), present = out.reduce((a, b) => a + b.present, 0), missing = out.reduce((a, b) => a + b.missing, 0);
/* the ratchet: raise these as features are built, never lower them */
const FLOOR = { present: 75, missingAtMost: 4 };
ok(present >= FLOOR.present, `at least ${FLOOR.present} features are present`, present);
ok(missing <= FLOOR.missingAtMost, `at most ${FLOOR.missingAtMost} are missing`, missing);
console.log(`\n${passed} passed, ${failed} failed`); process.exit(failed ? 1 : 0);
