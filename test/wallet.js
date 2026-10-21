/* The Universal Wallet (lib/wallet.js): definitions, many named wallets per owner, the balanced
   immutable ledger in exact minor units, idempotency, holds, and the single-balance callers. */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os");
const TMP = path.join(os.tmpdir(), "wallet-" + process.pid + ".db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
process.env.LX_DB = TMP;
const silence = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = silence;
const W = require("../lib/wallet.js");
const offers = require("../lib/offers.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const throws = (fn, re, n) => { try { fn(); ok(false, n, "did not throw"); } catch (e) { ok(re.test(e.message) || re.test(e.code || ""), n, e.message); } };
const T = 1, A = "shopper:a", B = "shopper:b";
const money = require("../lib/defaults.js").currency(T);

console.log("wallet — amounts are exact minor units");
ok(W.toMinor("12.34", 2) === 1234 && W.toMinor(0.1 + 0.2, 2) === 30 && W.toMinor("5", 0) === 5, "decimals become whole minor units");
throws(() => W.toMinor("1.234", 2), /decimal places/, "more decimals than the unit has are refused");
throws(() => W.toMinor("abc", 2), /Not an amount/, "and so is what is not an amount");

console.log("wallet — definitions are versioned");
const defs = W.definitions();
ok(defs.length >= 3 && defs.some(d => d.spec.default), "the seed declares definitions, one the default", defs.map(d => d.key));
const v1 = W.define({ key: "travel", name: { en: "Travel wallet", fr: "Portefeuille voyage" }, classes: ["fiat"], operations: ["transfer", "redeem", "hold"], policy: {} }, "test");
const same = W.define({ key: "travel", name: { en: "Travel wallet", fr: "Portefeuille voyage" }, classes: ["fiat"], operations: ["transfer", "redeem", "hold"], policy: {} }, "test");
const v2 = W.define({ key: "travel", name: { en: "Travel wallet" }, classes: ["fiat"], operations: ["transfer", "redeem", "hold"], policy: { max_balance: 1000 } }, "test");
ok(v1.version === 1 && same.version === 1 && v2.version === 2, "an unchanged declaration keeps its version; a change makes the next", [v1.version, same.version, v2.version]);
const early = W.open(T, "shopper:early", { definition: "travel" }, "shopper:early");
const v3 = W.define({ key: "travel", name: { en: "Travel wallet" }, classes: ["fiat"], operations: ["transfer", "redeem", "hold", "refund"], policy: { max_balance: 2000 } }, "test");
ok(W.rebind(v3, "test") >= 1 && W.balances(T, "shopper:early", early.id).definition.version === 3, "a version that only widens moves its wallets to it");
const v4 = W.define({ key: "travel", name: { en: "Travel wallet" }, classes: ["fiat"], operations: ["transfer", "redeem", "hold"], policy: { max_balance: 2000 } }, "test");
ok(W.rebind(v4, "test") === 0 && W.balances(T, "shopper:early", early.id).definition.version === 3, "a version that narrows leaves them where they are");
W.define({ key: "travel", name: { en: "Travel wallet" }, classes: ["fiat"], operations: ["transfer", "redeem", "hold"], policy: { max_balance: 1000 } }, "test");
throws(() => W.define({ key: "odd", name: { en: "Odd" }, classes: ["no_such_class"], operations: [] }), /value classes/, "a definition holds only classes Value declares");
throws(() => W.define({ key: "odd", name: { en: "Odd" }, classes: ["fiat"], operations: ["teleport"] }), /Unknown operation/, "and allows only declared operations");

console.log("wallet — many wallets per owner, names apart from identity");
const main = W.walletFor(T, A, money);
const t1 = W.open(T, A, { definition: "travel", name: "Trip" }, A);
const t2 = W.open(T, A, { definition: "travel", name: "Trip" }, A);
ok(t1.id !== t2.id && t1.name === t2.name, "two wallets may share a name and stay two wallets");
ok(t2.definition.version === 5, "a new wallet binds the open version of its definition", t2.definition.version);
throws(() => W.open(T, A, { definition: "main" }, A), /No more/, "a definition's policy caps how many an owner opens in a unit");
const pts = db.get("SELECT code FROM currencies WHERE class='loyalty' AND active=1");
if (pts) throws(() => W.open(T, A, { definition: "travel", unit: pts.code }, A), /does not hold/, "a wallet holds only units its definition's classes allow");
const rn = W.rename(T, A, t1.id, { name: "Summer trip" }, A);
ok(rn.id === t1.id && rn.name === "Summer trip" && W.names(t1.id).length === 2, "renaming keeps the identity and every past name");
W.rename(T, A, t1.id, { name: "Holiday", alias: true }, A);
ok(W.balances(T, A, t1.id).aliases.some(x => x.name === "Holiday"), "aliases ride beside the name");
throws(() => W.rename(T, B, t1.id, { name: "Mine" }, B), /not found/, "only the owner renames it");

console.log("wallet — the ledger balances and cannot be edited");
const dep = W.post(T, { op: "deposit", wallet: main.id, amount: "100.00", idem: "dep-1", actor: "test" });
ok(dep.wallet.posted === 100 && dep.journal.postings.length === 2 && dep.journal.postings.reduce((s, p) => s + p.amount, 0) === 0, "a deposit is two postings that sum to zero", dep.journal.postings);
const again = W.post(T, { op: "deposit", wallet: main.id, amount: "100.00", idem: "dep-1", actor: "test" });
ok(again.replayed && again.journal.id === dep.journal.id && again.wallet.posted === 100, "the same key returns the first outcome, once");
throws(() => W.post(T, { op: "deposit", wallet: main.id, amount: "5.00", idem: "dep-1" }), /different request/, "the same key for another request is refused");
throws(() => db.run("UPDATE ledger_postings SET amount=amount+1"), /immutable/, "a posting cannot be changed");
throws(() => db.run("DELETE FROM ledger_journals"), /immutable/, "nor a journal removed");
throws(() => W.post(T, { op: "redeem", wallet: main.id, amount: "100.01" }), /Not enough/, "a spend beyond what is available is refused, not clamped");
ok(W.balances(T, A, main.id).posted === 100, "and changes nothing");
throws(() => W.post(T, { op: "adjust", wallet: main.id, amount: "-5" }), /Say why/, "an adjustment needs a reason");

console.log("wallet — transfers and reversals");
const tr = W.transfer(T, { owner: A, from: main.id, to: t1.id, amount: "30", idem: "tr-1", actor: A });
ok(tr.from.posted === 70 && tr.to.posted === 30, "a transfer moves value between one owner's wallets");
throws(() => W.transfer(T, { owner: B, from: main.id, to: t1.id, amount: "1" }), /not found/, "no one moves another's value");
const rev = W.reverse(T, tr.journal.id, "staff", "test correction");
ok(rev.reverses === tr.journal.id && W.balances(T, A, main.id).posted === 100 && W.balances(T, A, t1.id).posted === 0, "a reversal mirrors the journal and is linked to it");
throws(() => W.reverse(T, tr.journal.id, "staff", "twice"), /already reversed/, "a journal is reversed once");

console.log("wallet — holds keep value until captured or released");
const h = W.hold(T, { owner: A, wallet: main.id, amount: "60", purpose: "order", idem: "h-1" });
ok(W.balances(T, A, main.id).available === 40 && W.balances(T, A, main.id).reserved === 60, "a hold keeps value out of available");
throws(() => W.post(T, { op: "redeem", wallet: main.id, amount: "41" }), /Not enough/, "what a hold keeps cannot be spent elsewhere");
throws(() => W.hold(T, { owner: A, wallet: main.id, amount: "41" }), /Not enough/, "nor held twice");
const c1 = W.capture(T, A, h.id, "25", "order:1", A);
ok(c1.hold.keeps && c1.hold.captured === 25 && c1.wallet.posted === 75 && c1.wallet.reserved === 35, "a part capture spends that part and keeps the rest", c1.wallet);
throws(() => W.capture(T, A, h.id, "36", "order:1", A), /no more than/, "a capture cannot exceed what remains");
const rel = W.release(T, A, h.id, A);
ok(!rel.keeps && W.balances(T, A, main.id).available === 75, "a release gives back what was kept");
throws(() => W.release(T, A, h.id, A), /cannot be done/, "and is final");

console.log("wallet — a wallet's life");
throws(() => W.move(T, t2.id, "suspend", "staff", ""), /Say why/, "a move needs a reason");
W.move(T, t2.id, "restrict", "staff", "review");
throws(() => W.transfer(T, { owner: A, from: t2.id, to: t1.id, amount: "1" }), /restricted|Not enough/i, "a restricted wallet sends nothing");
throws(() => W.move(T, main.id, "close", "staff", "asked"), /holds nothing/, "a wallet with value cannot be closed");
const cl = W.move(T, t2.id, "close", "staff", "asked");
ok(cl.state.key === "closed", "an empty wallet closes, and stays on record");

console.log("wallet — the single-balance callers ride on it");
offers.credit(T, B, 20, "refund", "r1");
ok(require("../lib/modules.js").walletBalance(T, B) === 20 && W.walletsOf(T, B).length === 1, "a credit lands in the owner's default wallet, and the old balance reads it");
throws(() => offers.debit(T, B, 25, "redeem", "x"), /Not enough/, "a debit beyond the balance is refused");
offers.debit(T, B, 5, "redeem", "x");
ok(require("../lib/modules.js").walletBalance(T, B) === 15, "a debit within it is spent");
const v = W.verify(T);
ok(v.journals > 5 && !v.unbalanced.length && v.chain.ok, "every journal balances and the event chain holds", v);

for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
