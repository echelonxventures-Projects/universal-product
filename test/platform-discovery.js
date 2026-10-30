/* Discovery (GLOBAL_MASTER.md §4, P29): from what a platform answered at setup, every capability it
   needs is classed mandatory, recommended, added or requested, with the reasons — read from what the
   master declares on taxonomy nodes, item kinds, fulfilment modes, selling models and jurisdictions'
   rules. The test reads every expectation from the seed; no kind of business is named here. */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os");
const TMP = path.join(os.tmpdir(), "pdisc-" + process.pid + ".db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
process.env.LX_DB = TMP;
const silence = console.log; console.log = () => { };
require("../lib/db.js");
console.log = silence;
const M = require("../lib/platform-master.js");
const D = require("../lib/platform-discovery.js");
const SEED = require("../lib/seed/master.json");
const caps = require("../lib/capabilities.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const throws = (fn, re, n) => { try { fn(); ok(false, n, "did not throw"); } catch (e) { ok(re.test(e.message), n, e.message); } };
const known = new Set(caps.catalog().map(c => c.key));
const CL = Object.fromEntries(M.vocabulary(M.ROLES.discoveryClasses).map(c => [c.test, c.name]));
const by = (found, key) => found.find(f => f.key === key);

console.log("discovery — an industry's requirements");
const industry = SEED.taxonomy.flatMap(d => d.children).find(i => (i.requires || []).some(k => known.has(k)));
const req = industry.requires.find(k => known.has(k));
const f1 = D.discover({ offerings: [industry.children[0].key] });
ok(by(f1, req) && by(f1, req).class === CL.requires, "selling under an industry makes what it requires mandatory — declared on the industry, holding below it", by(f1, req));
ok(by(f1, req).reasons.some(r => r.includes(industry.title.en)), "with the reason", by(f1, req).reasons);
const recd = (industry.recommends || []).find(k => known.has(k) && !industry.requires.includes(k));
if (recd) ok(by(f1, recd).class === CL.recommends, "and what it recommends recommended");
const missing = [...(industry.requires || []), ...(industry.recommends || [])].find(k => !known.has(k));
if (missing) ok(by(f1, missing).class === CL.requested && !by(f1, missing).available, "a capability no atom provides yet is requested", by(f1, missing));

console.log("discovery — kinds, fulfilment modes and selling models");
const kinds = M.vocabulary(M.ROLES.itemKinds);
const modes = M.vocabulary(M.ROLES.fulfilmentModes);
const kind = kinds.find(k => (k.fulfilment || []).some(m => (modes.find(x => x.name === m) || {}).requires && modes.find(x => x.name === m).requires.some(c => known.has(c))));
const mode = modes.find(x => kind.fulfilment.includes(x.name) && (x.requires || []).some(c => known.has(c)));
const need = mode.requires.find(c => known.has(c));
const f2 = D.discover({ offerings: [kind.name] });
ok(by(f2, need) && [CL.requires, CL.recommends].includes(by(f2, need).class), "a kind's possible fulfilment modes recommend what they need", by(f2, need));
const f3 = D.discover({ offerings: [kind.name], fulfilment: [mode.name] });
ok(by(f3, need).class === CL.requires, "a fulfilment mode the platform chooses makes what it needs mandatory", by(f3, need));
throws(() => D.discover({ fulfilment: ["no_such_mode"] }), /Unknown fulfilment mode/, "fulfilment modes come from the vocabulary");
const sm = M.vocabulary(M.ROLES.sellingModels).find(t => (t.requires || []).some(k => known.has(k)));
const smReq = sm.requires.find(k => known.has(k));
ok(by(D.discover({ sellingModel: sm.name }), smReq).class === CL.requires, "a selling model's requirements are mandatory");
throws(() => D.discover({ sellingModel: "no_such_model" }), /Unknown selling model/, "selling models come from the vocabulary");

console.log("discovery — a jurisdiction's rules");
const rule = M.vocabulary(M.ROLES.authorityRules).find(r => (r.places || []).length && (r.forNodes || []).length);
const f4 = D.discover({ official: rule.places[0], offerings: [rule.forNodes[0]] });
ok(rule.requires.every(k => by(f4, k) && by(f4, k).reasons.some(x => x.includes(rule.title.en.toLowerCase()))), "a rule of the jurisdiction where the platform trades applies to what it sells there", rule.requires.map(k => by(f4, k)));

console.log("discovery — choices and requests");
const pick = [...known][0];
const f5 = D.discover({ features: [pick], requests: ["a_capability_nobody_built"] });
ok(by(f5, pick).class === CL.added, "a capability the platform switches on with no cause is added");
ok(by(f5, "a_capability_nobody_built").class === CL.requested, "a request is requested");
const on = D.onAfter(D.discover({ offerings: [industry.children[0].key], features: [pick] }), [pick, req]);
ok(on.includes(req) && !on.includes(pick), "after discovery a mandatory capability stays on even when switched off; an optional one goes");

for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
