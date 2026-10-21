/* The Universal Wallet (lib/wallet.js), on the kernel: definitions as entities refining one another
   to any depth, settings resolved by context and time, wallets as entities under their definition
   and holder, the holder sealed and found by a blind index, and the balanced immutable ledger —
   its index replayed from the hash-chained log. */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os");
const TMP = path.join(os.tmpdir(), "wallet-" + process.pid + ".db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
process.env.LX_DB = TMP;
const silence = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = silence;
const W = require("../lib/wallet.js");
const K = require("../lib/kernel.js");
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

console.log("wallet — definitions are entities that refine one another, to any depth");
const root = W.definition("wallet"), main = W.definition("main");
ok(root && main && main.parent === "wallet" && !root.spec.openable && main.spec.openable, "the seed's definitions sit under a root that cannot be opened itself");
ok(main.spec.policy.hold_minutes === root.spec.policy.hold_minutes && main.spec.policy.hold_minutes > 0, "a child inherits what it does not state (hold expiry from the root)");
const travel = W.define({ key: "travel", parent: "purpose", name: { en: "Travel wallet", fr: "Portefeuille voyage" }, settings: { max_balance: 1000 } }, "test");
const trip = W.define({ key: "travel.trip", parent: "travel", name: { en: "Trip" }, settings: { max_per_owner: 2 } }, "test");
ok(travel.parent === "purpose" && trip.parent === "travel", "a sub-sub-definition sits under the one it refines");
ok(trip.spec.classes.join() === W.definition("purpose").spec.classes.join() && trip.spec.policy.max_balance === 1000 && trip.spec.policy.max_per_owner === 2,
  "and resolves each setting from the nearest definition stating it — two, three levels up", trip.spec);
const seqBefore = db.get("SELECT MAX(seq) s FROM k_events").s;
W.define({ key: "travel", parent: "purpose", name: { en: "Travel wallet", fr: "Portefeuille voyage" }, settings: { max_balance: 1000 } }, "test");
ok(db.get("SELECT MAX(seq) s FROM k_events").s === seqBefore, "an unchanged declaration writes nothing");
throws(() => W.define({ key: "odd", name: { en: "Odd" }, settings: { classes: ["no_such_class"] } }), /value classes/, "a definition holds only classes Value declares");
throws(() => W.define({ key: "odd", name: { en: "Odd" }, settings: { operations: ["teleport"] } }), /Unknown operation/, "and allows only declared operations");
throws(() => W.define({ key: "odd", name: { en: "Odd" }, settings: { colour: "red" } }), /Unknown setting/, "and states only declared settings");

console.log("wallet — a store configures a definition in its own namespace");
W.define({ key: "travel.trip", settings: { max_balance: 300 } }, "store", { namespace: "tenant:" + T });
ok(W.definition("travel.trip", T).spec.policy.max_balance === 300 && W.definition("travel.trip").spec.policy.max_balance === 1000, "the store's value holds in the store; the platform's stays the platform's");
throws(() => W.define({ key: "nowhere", name: { en: "No" } }, "store", { namespace: "tenant:" + T }), /Unknown definition/, "a store configures definitions, it does not invent them");

console.log("wallet — wallets are entities under their definition and their holder");
const mainW = W.walletFor(T, A, money);
const t1 = W.open(T, A, { definition: "travel.trip", name: "Summer" }, A);
const t2 = W.open(T, A, { definition: "travel.trip", name: "Summer" }, A);
ok(t1.id !== t2.id && t1.name === t2.name && /^[0-9a-f-]{36}$/.test(t1.id), "two wallets may share a name and stay two entities");
throws(() => W.open(T, A, { definition: "travel.trip" }, A), /No more/, "the cap resolved for the definition holds");
throws(() => W.open(T, A, { definition: "wallet" }, A), /not opened directly/, "a definition that is not openable is refined, not opened");
throws(() => W.open(T, A, { definition: "main" }, A), /No more/, "one main wallet per unit");
const pts = db.get("SELECT code FROM currencies WHERE class='loyalty'");
if (pts) throws(() => W.open(T, A, { definition: "travel.trip", unit: pts.code }, A), /does not hold/, "a wallet holds only units its definition's classes allow");
ok(W.walletsOf(T, A).length === 3 && W.walletsOf(T, B).length === 0, "an owner's wallets are the holder's children; another owner has none");
W.rename(T, A, t1.id, { name: "Holiday" }, A);
W.rename(T, A, t1.id, { name: "Vacances", lang: "fr" }, A);
W.rename(T, A, t1.id, { name: "Getaway", alias: true }, A);
const nm = W.names(t1.id);
ok(nm.some(n => n.name === "Summer") && nm.some(n => n.name === "Holiday") && nm.some(n => n.lang === "fr" && n.name === "Vacances"), "every name it has had, in every language, is kept in time", nm);
ok(W.balances(T, A, t1.id).aliases.some(a => a.name === "Getaway"), "aliases ride beside the name");
throws(() => W.rename(T, B, t1.id, { name: "Mine" }, B), /not found/, "only the holder renames it");

console.log("wallet — the holder is sealed and found by a blind index");
const raw = db.all("SELECT v.attrs FROM k_versions v JOIN k_nodes n ON n.uid=v.node WHERE n.kind IN ('value.wallet','party.holder')").map(r => r.attrs).join(" ");
ok(raw.length > 0 && !raw.includes(A) && /lux\.v1\./.test(raw), "the owner never sits readable in the store (sealed, AES-256-GCM)");
const ids = db.all("SELECT value FROM k_identifiers WHERE scheme='party.holder.key'").map(r => r.value);
ok(ids.length >= 1 && ids.every(v => /^[0-9a-f]{64}$/.test(v)) && !ids.some(v => v.includes("shopper")), "a holder is indexed by a keyed digest, not by who it is");
ok(W.balances(T, A, t1.id).owner === A, "yet the holder's own calls read it back");

console.log("wallet — the ledger balances, cannot be edited, and replays from the log");
const dep = W.post(T, { op: "deposit", wallet: mainW.id, amount: "100.00", idem: "dep-1", actor: "test" });
ok(dep.wallet.posted === 100 && dep.journal.postings.length === 2 && dep.journal.postings.reduce((s, p) => s + p.amount, 0) === 0, "a deposit is two postings that sum to zero");
const again = W.post(T, { op: "deposit", wallet: mainW.id, amount: "100.00", idem: "dep-1", actor: "test" });
ok(again.replayed && again.journal.id === dep.journal.id && again.wallet.posted === 100, "the same key returns the first outcome, once");
throws(() => W.post(T, { op: "deposit", wallet: mainW.id, amount: "5.00", idem: "dep-1" }), /different request/, "the same key for another request is refused");
throws(() => db.run("UPDATE ledger_postings SET amount=amount+1"), /immutable/, "a posting cannot be changed");
throws(() => db.run("DELETE FROM ledger_journals"), /immutable/, "nor a journal removed");
throws(() => W.post(T, { op: "redeem", wallet: mainW.id, amount: "100.01" }), /Not enough/, "a spend beyond what is available is refused, not clamped");
throws(() => W.post(T, { op: "adjust", wallet: mainW.id, amount: "-5" }), /Say why/, "an adjustment needs a reason");

console.log("wallet — settings apply by context");
throws(() => W.post(T, { op: "deposit", wallet: t1.id, amount: "1" }), /does not allow/, "an operation the definition chain does not allow is refused");
const tr = W.transfer(T, { owner: A, from: mainW.id, to: t1.id, amount: "30", idem: "tr-1", actor: A });
ok(tr.from.posted === 70 && tr.to.posted === 30, "a transfer moves value between one owner's wallets");
W.post(T, { op: "deposit", wallet: mainW.id, amount: "500", idem: "dep-2" });
throws(() => W.transfer(T, { owner: A, from: mainW.id, to: t1.id, amount: "271" }), /Not enough|at most/, "the store's own maximum for its trips holds (300)");
throws(() => W.transfer(T, { owner: B, from: mainW.id, to: t1.id, amount: "1" }), /not found/, "no one moves another's value");
const rev = W.reverse(T, tr.journal.id, "staff", "test correction");
ok(rev.reverses === tr.journal.id && W.balances(T, A, t1.id).posted === 0, "a reversal mirrors the journal and is linked to it");
throws(() => W.reverse(T, tr.journal.id, "staff", "twice"), /already reversed/, "a journal is reversed once");

console.log("wallet — holds keep value until spent or released");
const h = W.hold(T, { owner: A, wallet: mainW.id, amount: "560", purpose: "order", idem: "h-1" });
ok(W.balances(T, A, mainW.id).available === 40 && h.expires_at, "a hold keeps value out of available, and lapses by the resolved expiry");
throws(() => W.post(T, { op: "redeem", wallet: mainW.id, amount: "41" }), /Not enough/, "what a hold keeps cannot be spent elsewhere");
const c1 = W.capture(T, A, h.id, "25", "order:1", A);
ok(c1.hold.keeps && c1.hold.captured === 25 && c1.wallet.posted === 575 && c1.wallet.reserved === 535, "a part capture spends that part and keeps the rest", c1.wallet);
throws(() => W.capture(T, A, h.id, "536", "order:1", A), /no more than/, "a capture cannot exceed what remains");
ok(!W.release(T, A, h.id, A).keeps && W.balances(T, A, mainW.id).available === 575, "a release gives back what was kept");
ok(db.get("SELECT COUNT(*) n FROM k_events WHERE type='value.hold.moved'").n >= 3, "every move of a hold is an event");

console.log("wallet — a wallet's life");
throws(() => W.move(T, t2.id, "suspend", "staff", ""), /Say why/, "a move needs a reason");
W.move(T, t2.id, "restrict", "staff", "review");
throws(() => W.transfer(T, { owner: A, from: t2.id, to: t1.id, amount: "1" }), /restricted|Not enough/i, "a restricted wallet sends nothing");
throws(() => W.move(T, mainW.id, "close", "staff", "asked"), /holds nothing/, "a wallet with value cannot be closed");
ok(W.move(T, t2.id, "close", "staff", "asked").state.key === "closed", "an empty wallet closes, and stays on record");
ok(K.history(t2.id).length >= 3, "its states are versions in time");

console.log("wallet — the single-balance callers ride on it");
offers.credit(T, B, 20, "refund", "r1");
ok(require("../lib/modules.js").walletBalance(T, B) === 20 && W.walletsOf(T, B).length === 1, "a credit lands in the owner's default wallet, and the old balance reads it");
throws(() => offers.debit(T, B, 25, "redeem", "x"), /Not enough/, "a debit beyond the balance is refused");
offers.debit(T, B, 5, "redeem", "x");
ok(require("../lib/modules.js").walletBalance(T, B) === 15, "a debit within it is spent");
W.chooseDefault(T, "purpose", "store");
ok(W.definitions(T).find(d => d.key === "purpose").spec.default, "a store chooses its own default definition");
W.chooseDefault(T, "main", "store");
const v = W.verify(T);
ok(v.journals > 5 && !v.unbalanced.length && !v.drift.length && v.chain.ok, "every journal balances, the index replays from the log, the chain holds", v);

for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
