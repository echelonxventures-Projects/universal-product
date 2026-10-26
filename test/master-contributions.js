/* Contributions to the platform master (GLOBAL_MASTER.md §3, P28): a platform proposes, the global
   platform reviews every proposal and places what it approves — applied to the master, as a new
   entity, or as an addendum for the platforms and places it names — and what a platform sees is the
   master with its addenda, cut to the attributes its permission shows. Review before or after is
   the permission's. */
"use strict";
const path = require("path");
const fs = require("fs");
const os = require("os");
const TMP = path.join(os.tmpdir(), "mcontrib-" + process.pid + ".db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
process.env.LX_DB = TMP;
const silence = console.log; console.log = () => { };
require("../lib/db.js");
console.log = silence;
const M = require("../lib/platform-master.js");
const MP = require("../lib/master-permissions.js");
const C = require("../lib/master-contributions.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const throws = (fn, re, n) => { try { fn(); ok(false, n, "did not throw"); } catch (e) { ok(re.test(e.message), n, e.message); } };

const A = MP.storeHolder(1), B = MP.storeHolder(2);
const ind = M.children(M.children(null)[0].uid)[0];
const cat = M.children(ind.uid)[0];
const kind = M.vocabulary(M.ROLES.itemKinds).find(t => t.plain).kind;
const item = M.createItem({ kind, at: [cat.key], title: { en: "Master item" }, description: { en: "As the master says" } }, "platform");
const title = (h, ref) => { const v = C.view(h, ref, { lang: "en" }); return v ? v.attributes.title : null; };
const before = M.vocabulary(M.ROLES.reviews).find(t => t.effectiveOnApproval).name;
const after = M.vocabulary(M.ROLES.reviews).find(t => !t.effectiveOnApproval).name;

console.log("master contributions — a platform needs a permission to propose");
throws(() => C.propose(A, { action: "modify", target: item, patch: { title: { en: "Local" } } }, "store-a"), /Not permitted/, "with no permission, nothing can be proposed");
MP.grant({ holder: A, scope: [ind.key], actions: ["select"] }, "platform");
throws(() => C.propose(A, { action: "modify", target: item, patch: { title: { en: "Local" } } }, "store-a"), /does not allow modify/, "a permission to list does not let a platform modify");
MP.grant({ holder: A, scope: [ind.key], actions: ["modify", "overlay", "add", "retire"], review: before }, "platform");
MP.grant({ holder: B, scope: [ind.key], actions: ["select", "overlay"], review: after, visible: ["colour"] }, "platform");

console.log("master contributions — reviewed before: nothing changes until approval");
const c1 = C.propose(A, { action: "modify", target: item, patch: { title: { en: "Better title" } } }, "store-a");
ok(c1.awaiting && title(A, item) === "Master item" && title(B, item) === "Master item", "a proposal awaits review and changes nothing yet");
throws(() => C.review(c1.uid, { action: "approve", placement: "apply" }, "store-a"), /someone other than its author/, "its author cannot review it");
throws(() => C.review(c1.uid, { action: "reject" }, "platform"), /Say why/, "a rejection says why");
throws(() => C.review(c1.uid, { action: "approve", placement: "nowhere" }, "platform"), /Say where it lands/, "an approval says where it lands");
const r1 = C.review(c1.uid, { action: "approve", placement: "apply" }, "platform");
ok(r1.status === "approved" && title(A, item) === "Better title" && title(B, item) === "Better title", "applied to the master, every platform sees it");
ok(require("../lib/kernel.js").history(item).length >= 2, "the master keeps the version it replaced");
throws(() => C.review(c1.uid, { action: "approve", placement: "apply" }, "platform"), /already been decided/, "a contribution is decided once");

console.log("master contributions — an addendum changes nothing for anyone else");
const c2 = C.propose(A, { action: "overlay", target: item, patch: { title: { en: "Store A's name" } } }, "store-a");
C.review(c2.uid, { action: "approve", placement: "addendum" }, "platform");
ok(title(A, item) === "Store A's name" && title(B, item) === "Better title", "an addendum for one platform shows there only");
ok(M.node(item, { lang: "en" }).attributes.title === "Better title", "and the master itself is unchanged");

console.log("master contributions — reviewed after: at once, for its platform only, until the review");
const c3 = C.propose(B, { action: "overlay", target: item, patch: { title: { en: "Store B's name" } } }, "store-b");
ok(title(B, item) === "Store B's name" && title(A, item) === "Store A's name", "it holds at once for the proposing platform, and only there");
C.review(c3.uid, { action: "reject", reason: "Names stay as the brand registers them" }, "platform");
ok(title(B, item) === "Better title" && C.read(c3.uid).reason, "a rejection withdraws it, and the platform reads why");

console.log("master contributions — additions, new entities and retirements");
const c4 = C.propose(A, { action: "add", proposal: { kind, at: [cat.key], title: { en: "Proposed by store A" } } }, "store-a");
ok(!M.items({ under: cat.key }).some(n => n.attributes.title && n.attributes.title.en === "Proposed by store A"), "an addition reviewed before is not in the master yet");
const r4 = C.review(c4.uid, { action: "approve", placement: "apply" }, "platform");
ok(M.node(r4.result, { lang: "en" }).attributes.title === "Proposed by store A", "approved, the addition joins the master");
const c5 = C.propose(A, { action: "modify", target: item, patch: { title: { en: "A variant of it" } } }, "store-a");
const r5 = C.review(c5.uid, { action: "approve", placement: "new" }, "platform");
ok(r5.result !== item && M.node(r5.result, { lang: "en" }).attributes.title === "A variant of it" && M.node(item, { lang: "en" }).attributes.title === "Better title", "placed as new, it is a new entity beside the one proposed on");
const c6 = C.propose(A, { action: "retire", target: r5.result }, "store-a");
throws(() => C.review(c6.uid, { action: "approve", placement: "new" }, "platform"), /cannot land as new/, "a retirement cannot land as a new entity");
C.review(c6.uid, { action: "approve", placement: "addendum", holders: [A] }, "platform");
ok(C.view(A, r5.result) === null && C.view(B, r5.result) !== null, "a retirement as an addendum hides it for the platforms named, and only them");
const c7 = C.propose(A, { action: "overlay", target: item, patch: { title: { en: "x" } } }, "store-a");
C.withdraw(A, c7.uid, "store-a");
ok(C.read(c7.uid).status === "withdrawn" && !C.read(c7.uid).awaiting, "a platform may withdraw its own proposal");
ok(C.list({ holder: A }).length === 6 && C.list({ awaiting: true }).length === 0, "the review queue lists every contribution, and what awaits review");

console.log("master contributions — a platform sees the attributes its permission shows");
M.setFacts(item, { colour: "teal", material: "oak" }, null, "platform");
const vb = C.view(B, item);
ok(vb.attributes.facts.colour === "teal" && vb.attributes.facts.material === undefined, "facts outside the visible list are cut", vb.attributes.facts);
ok(C.view(A, item).attributes.facts.material === "oak", "a permission with no list sees every fact");

for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
