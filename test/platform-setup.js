/* Configuring a platform by its setup steps (GLOBAL_MASTER.md §4, P29): every answer is its own
   setting on the kernel, effective from a minute; what has come due is applied — jurisdiction and
   places served, currency and language, the permission over what it sells, and the capabilities
   discovery derives — and what no capability provides is kept as a request the owner edits. */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os");
const TMP = path.join(os.tmpdir(), "psetup-" + process.pid + ".db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
process.env.LX_DB = TMP;
const silence = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = silence;
const M = require("../lib/platform-master.js");
const SU = require("../lib/platform-setup.js");
const MP = require("../lib/master-permissions.js");
const caps = require("../lib/capabilities.js");
const stores = require("../lib/stores.js");
const settings = require("../lib/settings.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const throws = (fn, re, n) => { try { fn(); ok(false, n, "did not throw"); } catch (e) { ok(re.test(e.message), n, e.message); } };

const tid = db.run("INSERT INTO tenants(slug,name,domain,status,mode,industries,profile) VALUES('setup-probe','Setup probe','setup-probe.localhost','active','marketplace','[]','{}')").lastInsertRowid;
const opt = step => SU.options(step).map(o => o.key);
const countries = opt("official"), langs = opt("languages"), curr = opt("currencies");
const industry = M.vocabulary(M.ROLES.itemKinds) && require("../lib/registry.js").list("industries").find(i => (M.node(i.key).attributes.requires || []).some(k => caps.catalog().some(c => c.key === k)));
const need = M.node(industry.key).attributes.requires.find(k => caps.catalog().some(c => c.key === k));

console.log("platform setup — the steps are the master's");
ok(SU.describe().length === M.vocabulary(M.ROLES.blueprintSteps).length && SU.describe().every(s => s.title), "every declared step, with its question");
ok(countries.length > 1 && langs.length > 1 && curr.length > 1 && opt("selling_model").length > 1 && opt("offerings").length > 10, "each step's options come from where it says");
throws(() => SU.answer(tid, { official: countries[0] }), /Answer/, "a required step must be answered");
throws(() => SU.answer(tid, { official: "XX-NOT-A-PLACE", languages: [langs[0]], currencies: [curr[0]], sellingModel: opt("selling_model")[0], offerings: [industry.key] }), /not an option/, "an answer must be one of the step's options");

console.log("platform setup — answers given now are applied now");
const r = SU.answer(tid, { official: countries[1], working: [countries[2]], languages: [langs[1]], currencies: [curr[1]], sellingModel: opt("selling_model")[1], offerings: [industry.key], features: [], requests: ["a_feature_nobody_built"] }, {}, "platform");
ok(r.applied && r.applied.changed.includes("official"), "the answers are applied", r.applied && r.applied.changed);
ok(stores.country(tid) === countries[1] && stores.served(tid).includes(countries[2]), "the jurisdiction and the places served follow", [stores.country(tid), stores.served(tid)]);
ok(settings.load(tid).commerce.currency === curr[1] && settings.load(tid).commerce.locale === langs[1], "and the currency and language", settings.load(tid).commerce);
ok(caps.on(Number(tid), need), "what the industry requires is switched on", need);
ok(MP.allows(MP.storeHolder(tid), M.ROLES.selectAction, industry.key).ok, "the platform's permission on the master covers what it sells");
const st = SU.state(tid);
ok(st.applied.requested.some(q => q.key === "a_feature_nobody_built"), "what no capability provides is kept as a request");
SU.setRequests(tid, ["another_request"], "platform-owner");
ok(SU.state(tid).applied.requested.some(q => q.key === "another_request") && !SU.state(tid).applied.requested.some(q => q.key === "a_feature_nobody_built"), "the platform owner edits the requests afterwards");

console.log("platform setup — declining what is only recommended");
const rec = SU.state(tid).discovery.find(f => f.available && f.class === M.vocabulary(M.ROLES.discoveryClasses).find(c => c.test === "recommends").name);
if (rec) {
  SU.answer(tid, { declined: [rec.key, need] }, { partial: true }, "platform");
  ok(!caps.on(Number(tid), rec.key) && caps.on(Number(tid), need), "a recommended capability declined goes off; a mandatory one stays on", [rec.key, need]);
}

console.log("platform setup — to the minute");
const later = new Date(Date.now() + 3 * 60 * 1000).toISOString();
const sched = SU.answer(tid, { currencies: [curr[2]] }, { at: later, partial: true }, "platform");
ok(sched.applied === null && settings.load(tid).commerce.currency === curr[1], "an answer for a later minute is not applied before then");
ok(SU.answers(tid, { at: later }).currencies[0] === curr[2] && SU.answers(tid).currencies[0] === curr[1], "each answer is answerable at any minute");
ok(new Date(sched.from).getSeconds() === 0, "times are held to the minute", sched.from);

console.log("platform setup — registration goes through the setup steps");
const api = require("../lib/api.js");
const call = (method, url, body) => { let out = {}; api.handle({ method }, { writeHead: () => { }, setHeader: () => { }, end: x => { out = JSON.parse(x); } }, new URL(url, "http://x.test"), { platform_admin: { id: 1, email: "owner@platform.test" }, tenant: { id: 1 } }, body); return out; };
const kindTerm = M.vocabulary(M.ROLES.itemKinds).find(t => !(t.fulfilment || []).some(m => (M.vocabulary(M.ROLES.fulfilmentModes).find(x => x.name === m) || {}).physical));
const reg1 = call("POST", "/api/platform/tenants", { name: "Answered", slug: "answered-probe", answers: { official: countries[1], languages: [langs[1]], currencies: [curr[1]], sellingModel: opt("selling_model")[1], offerings: [kindTerm.name] } });
ok(reg1.tenant && reg1.setup && !reg1.setup.error, "a registration that answers the steps is configured by them", reg1.setup || reg1.error);
ok(reg1.kind && reg1.kind.provision.shipping === false, "what it is provisioned with follows from its answers (nothing physical to ship)", reg1.kind && reg1.kind.provision);
ok(SU.answers(reg1.tenant.id).offerings[0] === kindTerm.name, "its answers are on the kernel");
const kinds = require("../lib/registry.js").kinds();
const withStarter = kinds.find(k => k.starter && k.starter.sellingModel && k.archetype);
const reg2 = call("POST", "/api/platform/tenants", { name: "By kind", slug: "by-kind-probe", mode: withStarter.key, country: countries[1] });
ok(reg2.tenant && !reg2.setup.error && SU.answers(reg2.tenant.id).sellingModel === withStarter.starter.sellingModel, "a registration that names a kind has the kind's starter answers, through the same steps", reg2.setup || reg2.error);
throws(() => SU.check({ official: countries[0], languages: [langs[0]], currencies: [curr[0]], sellingModel: "nope" }), /not an option/, "an answer the registration gives is checked like any other");

/* every step's options load (the platform's setup screen lists them all) */
const broken = SU.describe().map(st => { try { SU.options(st.step); return null; } catch (e) { return st.step + ": " + e.message; } }).filter(Boolean);
ok(!broken.length, "every step offers its options", broken);
/* the contribution machine the master review screen shows is found in the state catalogue */
ok(!!require("../lib/states.js").catalog()[require("../lib/platform-master.js").ROLES.contributionMachine], "the contribution machine is in the state catalogue");

for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
