/* Every artifact belongs to exactly one business domain (_registry/business-domains.json,
   scripts/domain-map.js), and the debts of mixing only shrink:
     · no artifact unowned, none owned twice, no claim naming nothing — always
     · console groups that mix domains, routes still kept in the shared route file, store
       screens still kept in the shared console script, and domains whose documentation is
       incomplete — each at most its recorded baseline (_registry/business-baseline.json), which
       is lowered as the work lands (node test/domain-map.js --update) */
"use strict";
const fs = require("fs"), path = require("path");
const { map } = require("../scripts/domain-map.js");
const docs = require("../scripts/domain-docs.js");
const BASE = path.join(__dirname, "..", "_registry", "business-baseline.json");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + JSON.stringify(x).slice(0, 600) : ""))); };

const m = map();
console.log("▸ EVERY ARTIFACT HAS EXACTLY ONE BUSINESS DOMAIN");
for (const [kind, v] of Object.entries(m.kinds)) {
  ok(!v.unowned.length, `${kind}: none unowned (${v.total})`, v.unowned);
  ok(!v.double.length, `${kind}: none owned twice`, v.double);
  ok(!v.stale.length, `${kind}: no claim names what does not exist`, v.stale);
}

console.log("▸ THE DOCUMENTATION IS GENERATED FROM WHAT IS BUILT, AND CURRENT");
const stale = Object.entries(docs.generate()).filter(([f, t]) => { const p = path.join(__dirname, "..", f); return !fs.existsSync(p) || fs.readFileSync(p, "utf8") !== t; }).map(([f]) => f);
ok(!stale.length, "every domain's documentation and every manual matches the code (node scripts/domain-docs.js)", stale.slice(0, 8));

console.log("▸ NO ROUTE ANSWERS A REQUEST BECAUSE OF WHERE IT SITS");
const ov = require("../scripts/domain-map.js").overlaps();
ok(ov.every(o => o.sameFile), "routes one request could match sit in one file", ov.filter(o => !o.sameFile));
ok(ov.every(o => o.ordered), "and the more literal route comes first", ov.filter(o => !o.ordered));

/* the debts, measured */
const shared = f => fs.readFileSync(path.join(__dirname, "..", f), "utf8");
const debts = {
  mixedConsoleGroups: m.mixedGroups.length,
  routesInSharedFile: [...shared("lib/api.js").matchAll(/\["(GET|POST|PUT|PATCH|DELETE) \/api\//g)].length,
  screensInSharedScript: [...shared("public/js/admin.js").split("const NAVFLAT")[0].matchAll(/\["([a-z_]+)", "/g)].length,
  domainsUndocumented: docs.completeness().filter(d => d.missing.length).length,
  routesUndescribed: docs.undescribedRoutes()
};
console.log("▸ THE DEBTS OF MIXING ONLY SHRINK");
if (process.argv.includes("--update")) { fs.writeFileSync(BASE, JSON.stringify(debts, null, 1) + "\n"); console.log("  baseline written", debts); }
const base = fs.existsSync(BASE) ? JSON.parse(fs.readFileSync(BASE, "utf8")) : debts;
for (const [k, v] of Object.entries(debts)) {
  ok(v <= base[k], `${k}: ${v} (baseline ${base[k]})`);
  if (v < base[k]) console.log(`  ↓ ${k} below its baseline — run node test/domain-map.js --update to hold the lower count`);
}
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
