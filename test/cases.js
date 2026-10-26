/* Cases (lib/cases.js): anything someone asks a store to decide — every kind a caseKinds row
   declaring what it is about, what is asked, its state machine and what approval does. */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os");
const TMP = path.join(os.tmpdir(), "cases-" + process.pid + ".db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
process.env.LX_DB = TMP;
const silence = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = silence;
const CS = require("../lib/cases.js");
const caps = require("../lib/capabilities.js");
const lineterms = require("../lib/lineterms.js");
const reg = require("../lib/parity-registries.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const throws = (fn, re, n) => { try { fn(); ok(false, n, "did not throw"); } catch (e) { ok(re.test(e.message), n, e.message); } };
const T = 1, who = "shopper:test";
const KINDS = reg.list("caseKinds");
const kindWith = f => KINDS.find(f);
const product = db.get("SELECT * FROM products WHERE tenant_id=? AND lifecycle='published' LIMIT 1", T);
const fill = k => Object.fromEntries((k.fields || []).filter(f => f.required).map(f => [f.key, { url: "https://example.com/x", number: 10, date: "2026-01-01", text: "value" }[f.type]]));

console.log("cases — a kind is taken only where its capability is on");
const wallet = kindWith(k => k.effect && k.effect.wallet);
throws(() => CS.open(T, who, { kind: wallet.key, subject_id: product.id, fields: fill(wallet) }, "shopper"), /does not take/, "a store with the capability off takes no such case");
for (const k of KINDS) caps.enable(T, k.atom);
ok(CS.kinds(T).length === KINDS.length, "with it on, the kind is taken");

console.log("cases — opening checks what the kind asks");
throws(() => CS.open(T, who, { kind: wallet.key, subject_id: product.id, fields: {} }, "shopper"), /required/, "a required field must be given");
throws(() => CS.open(T, who, { kind: wallet.key, subject_id: "nope", fields: fill(wallet) }, "shopper"), /Say which/, "its subject must exist");
const c1 = CS.open(T, who, { kind: wallet.key, subject_id: product.id, fields: fill(wallet) }, "shopper");
ok(c1.open && c1.state.key, "a case opens");

console.log("cases — deciding does what the kind declares");
throws(() => CS.move(T, c1.id, "approve", {}, "staff"), /amount/, "an approval that pays names its amount");
const before = (db.get("SELECT balance FROM wallets WHERE tenant_id=? AND owner=?", T, who) || { balance: 0 }).balance;
const a1 = CS.move(T, c1.id, "approve", { amount: 7.5 }, "staff");
ok(!a1.open && Number(a1.amount) === 7.5, "approved with its amount");
ok(Math.abs(db.get("SELECT balance FROM wallets WHERE tenant_id=? AND owner=?", T, who).balance - before - 7.5) < 0.01, "a wallet effect credits the opener");
throws(() => CS.move(T, c1.id, "approve", { amount: 1 }, "staff"), /cannot be done/, "a decided case is decided once");
const c2 = CS.open(T, who, { kind: wallet.key, subject_id: product.id, fields: fill(wallet) }, "shopper");
throws(() => CS.move(T, c2.id, "reject", {}, "staff"), /Say why/, "a rejection says why");
ok(CS.withdraw(T, who, c2.id).state.key && !CS.list(T, { owner: who }).find(c => c.id === c2.id).open, "the opener may withdraw an open case");

console.log("cases — a kind that gates buying");
const gate = kindWith(k => k.gates);
db.run("UPDATE products SET attrs=? WHERE tenant_id=? AND id=?", JSON.stringify({ [gate.gates.attr]: gate.gates.equals }), T, product.id);
const gated = db.get("SELECT * FROM products WHERE tenant_id=? AND id=?", T, product.id);
throws(() => CS.checkGates(T, who, gated, {}), /needs/, "a product the kind gates cannot be bought without its case");
const g1 = CS.open(T, who, { kind: gate.key, fields: fill(gate) }, "shopper");
throws(() => lineterms.clean({ tid: T, owner: who, product: gated, qty: 1 }, { case: { id: g1.id } }), /not approved/, "an unapproved case does not open the gate");
CS.move(T, g1.id, "approve", {}, "pharmacist");
const terms = lineterms.clean({ tid: T, owner: who, product: gated, qty: 1 }, { case: { id: g1.id } });
let gateErr = null; try { CS.checkGates(T, who, gated, terms); } catch (e) { gateErr = e.message; }
ok(!gateErr && CS.validFor(T, who, gate.key)[0].valid_until, "an approved case on the line opens it, for the time the kind declares", gateErr);
throws(() => lineterms.clean({ tid: T, owner: "someone:else", product: gated, qty: 1 }, { case: { id: g1.id } }), /not yours/, "only its opener may use it");

console.log("cases — a credit taken off a bag line, once");
const credit = kindWith(k => k.effect && k.effect.line_credit);
const t1 = CS.open(T, who, { kind: credit.key, fields: fill(credit) }, "shopper");
CS.move(T, t1.id, "approve", { amount: 20 }, "staff");
const plain = db.get("SELECT * FROM products WHERE tenant_id=? AND id<>? AND lifecycle='published' LIMIT 1", T, product.id);
const lt = lineterms.priceLine({ tid: T, owner: who, product: plain, qty: 1 }, lineterms.clean({ tid: T, owner: who, product: plain, qty: 1 }, { case: { id: t1.id } }), plain.price);
ok(Math.abs(lt.unit - (plain.price - 20)) < 0.01 && lt.maxQty === 1, "its value comes off one item", lt);
lineterms.place({ tid: T, owner: who, orderId: 999 }, [{ product: plain, qty: 1, terms: { case: { id: t1.id } } }]);
throws(() => lineterms.clean({ tid: T, owner: who, product: plain, qty: 1 }, { case: { id: t1.id } }), /not approved|used/, "and only once");

console.log("cases — a kind may live by its own machine");
const own = kindWith(k => k.machine && k.machine !== "case");
const l1 = CS.open(T, who, { kind: own.key, subject_id: product.id, fields: fill(own) }, "shopper");
ok(l1.state.key === require("../lib/states.js").initial(own.machine), "it starts in its machine's first state");
ok(CS.vocabulary(T).actions.some(a => a.machine === own.machine), "and the console is given its actions");

for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
