/* A store's books (lib/books.js): the chart of accounts on the kernel, entries on the platform's one
   ledger posted by the same writes checkout, refunds and billing make, and the reports read from
   them — trial balance, profit and loss, balance sheet — which must agree with each other. */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os");
const TMP = path.join(os.tmpdir(), "books-" + process.pid + ".db");
const wipe = () => { for (const s of ["", "-wal", "-shm"]) try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } };
wipe(); process.env.LX_DB = TMP;
const log = console.log, err = console.error; console.log = () => { };
const db = require("../lib/db.js");
console.log = log;
const K = require("../lib/kernel.js"), B = require("../lib/books.js"), RR = require("../lib/row-records.js"), OR = require("../lib/order-records.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + JSON.stringify(x).slice(0, 400) : ""))); };
const throws = (fn, re) => { try { fn(); return false; } catch (e) { return re.test(e.message); } };
const rejects = async (p, re) => { try { await p; return false; } catch (e) { return re.test(e.message); } };
const row = (tb, code) => (tb.rows || []).find(r => r.account === code) || { debit: 0, credit: 0, balance: 0 };
(async () => {
  try {
    const t1 = db.get("SELECT id FROM tenants ORDER BY id LIMIT 1").id, t2 = (db.get("SELECT id FROM tenants WHERE id<>? ORDER BY id LIMIT 1", t1) || { id: t1 + 1000 }).id;
    const cur = require("../lib/defaults.js").currency(t1);
    /* the books start from what existed before them */
    const at0 = B.trialBalance(t1).find(t => t.currency === cur) || { rows: [] };
    const base = code => row(at0, code);

    console.log("▸ THE CHART OF ACCOUNTS");
    const chart = B.accounts(t1);
    ok(B.SEED.chart.every(a => chart.some(c => c.code === a.code && c.type === a.type)), "every store starts from the platform's chart", chart.length);
    ok(chart.filter(a => a.parent === "4").map(a => a.code).join() === "4000,4100,4200,4900" && K.internal.nodeRow(chart.find(a => a.code === "4000").uid).kind === "books.account", "each account is on the kernel, under its group");
    const mine = B.define(t1, { code: "6150", name: "Couriers", parent: "6" }, "test");
    ok(mine.type === "expense" && mine.own && B.accounts(t1).some(a => a.code === "6150") && !B.accounts(t2).some(a => a.code === "6150"), "a store adds its own account, taking its group's type; other stores do not see it");
    ok(throws(() => B.define(t1, { code: "6150", name: "Again", parent: "6" }), /already exists/) && throws(() => B.define(t1, { code: "4000", name: "Sales again", parent: "4" }), /already exists/), "an account code is not used twice");

    console.log("▸ A SALE POSTS ITSELF");
    const oid = Number(db.run(`INSERT INTO orders(tenant_id,owner,num,name,sub,ship_fee,gift_used,tax,total,status,currency) VALUES(?,?,?,?,100,10,0,11,121,'processing',?)`, t1, "t" + t1 + ":guest", "BOOKS-1", "Test", cur).lastInsertRowid);
    OR.change(oid, () => null);
    const pr = RR.created("payment", () => db.run("INSERT INTO payments(tenant_id,kind,order_id,gateway,method,amount,currency,fee,status,txn_ref,live) VALUES(?,?,?,?,?,?,?,?,?,?,0)", t1, "order", oid, "cod", "cod", 121, cur, 3, "captured", "BK-1"));
    const pid = Number(pr.lastInsertRowid), puid = db.get("SELECT uid FROM payments WHERE id=?", pid).uid;
    const d = code => { const tb = B.trialBalance(t1).find(t => t.currency === cur); const r = row(tb, code), b0 = base(code); return { debit: +(r.debit - b0.debit).toFixed(2), credit: +(r.credit - b0.credit).toFixed(2) }; };
    ok(d("1200").debit === 121 && d("4000").credit === 100 && d("4100").credit === 10 && d("2200").credit === 11, "captured: owed by the gateway, sales, delivery and tax collected", [d("1200"), d("4000"), d("4100"), d("2200")]);
    ok(d("6100").debit === 3 && d("1200").credit === 3, "and the gateway's fee");
    ok(B.entries(t1, { ref: puid }).every(e => e.lines.reduce((s, l) => s + l.debit - l.credit, 0) === 0 || Math.abs(e.lines.reduce((s, l) => s + l.debit - l.credit, 0)) < 1e-9), "every entry balances");
    const n0 = B.entries(t1, { ref: puid }).length;
    RR.change("payment", pid, () => db.run("UPDATE payments SET txn_ref=? WHERE id=?", "BK-1b", pid));
    ok(B.entries(t1, { ref: puid }).length === n0 && B.importRows() === 0, "a change that is not a money event, or a second pass, posts nothing");

    console.log("▸ A REFUND POSTS ITSELF");
    await require("../lib/refunds.js").refund(t1, { id: pid }, 60.5, { reason: "half back", actor: "test" });
    ok(d("4900").debit === 55 && d("2200").debit === 5.5 && d("1200").credit === 63.5, "half refunded: refunds given, the tax on it given back, less owed by the gateway", [d("4900"), d("2200"), d("1200")]);

    console.log("▸ THE REPORTS AGREE");
    const tb = B.trialBalance(t1).find(t => t.currency === cur);
    ok(Math.abs(tb.debit - tb.credit) < 1e-6, "the trial balance balances", [tb.debit, tb.credit]);
    const pl = B.profitAndLoss(t1).find(p => p.currency === cur), bs = B.balanceSheet(t1).find(b => b.currency === cur);
    ok(Math.abs(bs.totalAssets - bs.totalLiabilitiesAndEquity) < 1e-6, "the balance sheet balances: assets are what is owed plus equity and earnings", [bs.totalAssets, bs.totalLiabilitiesAndEquity]);
    ok(Math.abs(bs.earnings - pl.profit) < 1e-6, "its earnings are the profit and loss's profit", [bs.earnings, pl.profit]);
    const l1200 = B.ledger(t1, "1200").filter(x => x.ref === puid);
    ok(l1200.map(x => x.op).join() === "sale,gateway_fee,refund", "an account's ledger lists what moved it, in order", l1200.map(x => x.op));

    console.log("▸ AN ACCOUNTANT'S ENTRIES");
    ok(throws(() => B.manual(t1, { memo: "x", lines: [{ account: "1000", debit: 10 }, { account: "1200", credit: 9 }] }), /must be equal/), "an entry that does not balance is refused");
    ok(throws(() => B.manual(t1, { memo: "x", lines: [{ account: "1", debit: 10 }, { account: "1200", credit: 10 }] }), /is a group/), "nor is posting to a group");
    ok(throws(() => B.manual(t1, { lines: [{ account: "1000", debit: 10 }, { account: "1200", credit: 10 }] }), /Say what/), "an entry says what it is for");
    ok(throws(() => B.manual(t2, { memo: "x", lines: [{ account: "6150", debit: 1 }, { account: "1000", credit: 1 }] }), /No account 6150/), "another store cannot post to this store's own account");
    const settle = B.manual(t1, { memo: "Gateway settled to the bank", lines: [{ account: "1000", debit: 57.5 }, { account: "1200", credit: 57.5 }] }, "accountant");
    ok(settle.lines.length === 2 && d("1000").debit === 57.5, "a balanced entry is posted");
    const back = B.reverse(t1, settle.id, "accountant", "wrong day");
    ok(back.reverses === settle.id && d("1000").credit === 57.5, "and corrected only by a reversal that says why");
    ok(throws(() => B.reverse(t1, settle.id, "accountant", "again"), /already reversed/) && throws(() => B.reverse(t1, back.id, "accountant", "x"), /not itself reversed/), "once");
    ok(throws(() => db.run("UPDATE ledger_postings SET amount=1 WHERE journal_id=?", settle.id), /immutable/), "a posted entry cannot be edited");
    const saleEntry = B.entries(t1, { ref: puid }).find(e => e.op === "sale");
    ok(!saleEntry.reversible && throws(() => B.reverse(t1, saleEntry.id, "accountant", "x"), /corrected by the event/), "what a sale posted is not reversed by hand: a refund undoes it");

    console.log("▸ BILLS FROM THE PLATFORM");
    require("../lib/billing.js").issueInvoice(t1, { lines: [{ kind: "usage", description: "Books test", qty: 1, unit_amount: 20, amount: 20 }], note: "books-test" });
    const inv = db.get("SELECT * FROM invoices WHERE note='books-test'"), unit = String(inv.currency).toUpperCase();
    const di = code => { const t = B.trialBalance(t1).find(x => x.currency === unit); return row(t, code); };
    const fee0 = di("6200").debit;
    ok(fee0 >= Number(inv.amount) && di("2000").credit >= Number(inv.amount), "an invoice to the store is a platform fee it owes", [inv.amount, di("6200"), di("2000")]);
    RR.change("invoice", inv.id, () => db.run("UPDATE invoices SET status='paid', paid_at=datetime('now') WHERE id=?", inv.id));
    ok(di("2000").debit >= Number(inv.amount) && di("1000").credit >= Number(inv.amount), "paying it clears what is owed from the bank");

    console.log("▸ NOTHING IS LOST");
    console.error = () => { };
    const bad = RR.created("payment", () => db.run("INSERT INTO payments(tenant_id,kind,order_id,gateway,method,amount,currency,fee,status,txn_ref,live) VALUES(?,?,?,?,?,?,?,?,?,?,0)", t1, "order", oid, "cod", "cod", 5, "ZZZ", 0, "captured", "BK-ZZZ"));
    console.error = err;
    const buid = db.get("SELECT uid FROM payments WHERE id=?", Number(bad.lastInsertRowid)).uid;
    const h = B.health(t1);
    ok(db.get("SELECT status FROM payments WHERE id=?", Number(bad.lastInsertRowid)).status === "captured" && h.missing.includes(buid) && h.unposted.some(u => u.uid === buid), "a payment the books cannot post (an unknown currency) still goes through, and is reported", h.unposted);
    ok(!h.unbalanced.length && !h.drift.length && h.chain.ok !== false, "every entry balances and matches the hash-chained log", { unbalanced: h.unbalanced, drift: h.drift, chain: h.chain });
  } catch (e) { failed++; console.log("  ✗ threw: " + e.stack); }
  finally { wipe(); console.log(`\n${passed} passed, ${failed} failed`); process.exit(failed ? 1 : 0); }
})();
