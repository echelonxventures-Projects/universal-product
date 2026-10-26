/* Deliverables (lib/deliverables.js): what an order hands the shopper beyond the goods — every kind
   (licence keys, lab tests, course progress) its own feature, switched on by its own capability
   and set up by that capability's params. */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os");
const TMP = path.join(os.tmpdir(), "deliverables-" + process.pid + ".db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
process.env.LX_DB = TMP;
const silence = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = silence;
const DL = require("../lib/deliverables.js");
const caps = require("../lib/capabilities.js");
const lineterms = require("../lib/lineterms.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const throws = (fn, re, n) => { try { fn(); ok(false, n, "did not throw"); } catch (e) { ok(re.test(e.message), n, e.message); } };
const T = 1, who = "shopper:test";
const KINDS = DL.kinds();
const kindWith = f => KINDS.find(f);
const pooled = kindWith(k => k.pooled), uploaded = kindWith(k => k.uploaded), access = kindWith(k => k.access);
const items = db.all("SELECT * FROM products WHERE tenant_id=? AND lifecycle='published' LIMIT 3", T);
const setFacts = (p, facts) => db.run("UPDATE products SET attrs=? WHERE id=? AND tenant_id=?", JSON.stringify(Object.assign(JSON.parse(p.attrs || "{}"), facts)), p.id, T);
let orderId = 9000;
const order = (p, qty) => { lineterms.place({ tid: T, owner: who, orderId: ++orderId, orderNum: "D" + orderId }, [{ product: p, qty: qty || 1, terms: {} }]); return orderId; };
const ofOrder = id => db.all("SELECT * FROM deliverables WHERE order_id=? ORDER BY id", id);

console.log("deliverables — every kind is its own feature");
ok(pooled && uploaded && access, "the registry declares a pooled, an uploaded and an access kind", KINDS.map(k => k.key));
ok(new Set(KINDS.map(k => k.atom)).size === KINDS.length && new Set(KINDS.map(k => k.section)).size === KINDS.length, "each names its own capability and its own section");
ok(KINDS.every(k => caps.cap(T, k.atom) !== undefined && DL.sectionOf(k.key) === k.section), "each kind's routes resolve to its own section");

const [pKey, pLab, pCourse] = items;
setFacts(pKey, { [caps.cap(T, pooled.atom).fact || "licence"]: true });
console.log("deliverables — nothing is handed over while a kind's capability is off");
const off = order(pKey);
ok(ofOrder(off).length === 0, "an order of the item delivers nothing");
throws(() => DL.forStaff(T, pooled.key), /not available/, "and the kind's screen is closed");

console.log("deliverables — a pooled kind (" + pooled.name + ")");
caps.enable(T, pooled.atom, { low_stock: 2 });
const P1 = caps.cap(T, pooled.atom);
setFacts(pKey, { [P1.fact]: true });
throws(() => DL.stock(T, uploaded.key, pKey.id, ["X"]), /not available/, "another kind that is off cannot be stocked");
const st = DL.stock(T, pooled.key, pKey.id, "K-1\nK-2\nK-3\nK-1");
ok(st.added === 3 && st.left === 3, "codes are pooled once each", st);
const o1 = order(pKey, 2);
const got = ofOrder(o1);
ok(got.length === 2 && got.every(d => d.value && d.delivered_at), "one code per unit is handed over at once", got.map(d => d.value));
ok(DL.left(T, pKey.id) === 1, "and taken from the pool");
ok(db.get("SELECT COUNT(*) n FROM notifications WHERE tenant_id=? AND kind='deliverable' AND title LIKE '%low%'", T).n >= 1, "staff are told when a pool runs below the kind's low_stock");
const o2 = order(pKey, 2);
const short = ofOrder(o2);
ok(short.filter(d => d.value).length === 1 && short.filter(d => !d.value).length === 1, "an empty pool leaves the rest awaited");
const handed = DL.upload(T, short.find(d => !d.value).id, "K-HAND", "staff");
ok(handed.delivered && handed.value === "K-HAND", "staff hand over a code by hand");
const screen = DL.forStaff(T, pooled.key);
ok(screen.kind.key === pooled.key && screen.deliverables.every(d => d.kind === pooled.key) && screen.pools.length === 1, "its screen shows only its own, with its pool");

console.log("deliverables — an uploaded kind (" + uploaded.name + ")");
caps.enable(T, uploaded.atom, { due_days: 0 });
setFacts(pLab, { [caps.cap(T, uploaded.atom).fact]: true });
const o3 = order(pLab);
const lab = ofOrder(o3)[0];
ok(lab && !lab.value && !lab.delivered_at, "it is awaited");
throws(() => DL.upload(T, lab.id, "just text", "staff"), /link/, "a report must be a link");
const done = DL.upload(T, lab.id, "https://example.com/report.pdf", "staff");
ok(done.delivered && done.value.endsWith("report.pdf"), "staff upload the report");
ok(db.get("SELECT COUNT(*) n FROM notifications WHERE tenant_id=? AND owner=? AND kind='deliverable'", T, who).n >= 1, "and the shopper is told");

console.log("deliverables — an access kind (" + access.name + ")");
caps.enable(T, access.atom);
const P3 = caps.cap(T, access.atom);
setFacts(pCourse, { [P3.fact]: true, [P3.steps_fact]: 2 });
const o4 = order(pCourse);
const course = ofOrder(o4)[0];
ok(course && course.delivered_at && course.steps_total === 2 && course.value === P3.access_url.replace("{id}", course.id), "access is granted at once, with its lessons counted", course);
throws(() => DL.upload(T, course.id, "https://x", "staff"), /granted/, "access is not uploaded");
DL.step(T, who, course.id); const fin = DL.step(T, who, course.id); const over = DL.step(T, who, course.id);
ok(fin.steps_done === 2 && over.steps_done === 2, "the shopper counts lessons up to the total");
throws(() => DL.step(T, "someone:else", course.id), /not found/, "only its owner counts them");

console.log("deliverables — the shopper sees only what is on");
ok(DL.mine(T, who).length === 6, "every delivered kind", DL.mine(T, who).length);
caps.disable(T, uploaded.atom);
ok(!DL.mine(T, who).some(d => d.kind === uploaded.key), "and not a kind switched off");

for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
