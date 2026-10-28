/* LUXORA Platform — money at rest (lib/money-store.js, PR-016).
   A database from before the money migration — its money columns removed, so it has exactly the
   shape an existing install has — is filled with the values a REAL column really holds (exact
   amounts, float residue, more decimals than the currency has, no currency, an unknown currency,
   text), then booted on this code:
     · every amount that can be converted exactly is, and the rest are quarantined with their
       source value kept and the candidates listed — nothing is guessed
     · a migration killed part-way leaves nothing behind, and the next boot completes it with the
       same result; a finished migration is never re-run
     · the database refuses a row whose projection disagrees with its minor units
     · a quarantined amount is resolved by an operator, and only then is the row usable
     · refunds: partial, full, idempotent, never above what was captured — also when two server
       processes race for the last of a payment */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os");
const { spawnSync, spawn } = require("child_process");
const { DatabaseSync } = require("node:sqlite");
const ROOT = path.join(__dirname, "..");
const DIR = fs.mkdtempSync(path.join(os.tmpdir(), "money-store-"));
const LEGACY = path.join(DIR, "legacy.db"), CRASH = path.join(DIR, "crash.db");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const throws = (fn, re, n) => { try { fn(); ok(false, n, "did not throw"); } catch (e) { ok(re.test(e.message) || re.test(e.code || ""), n, e.message); } };
const SPEC = require("../lib/seed/money.json").store;
const env = (db, extra) => Object.assign({}, process.env, { LX_TEST: "1", LX_DB: db }, extra || {});
/* one boot of the platform on a database, in its own process */
const boot = (db, extra) => spawnSync(process.execPath, ["-e", "require('./lib/db.js')"], { cwd: ROOT, env: env(db, extra), encoding: "utf8", timeout: 300000 });
const copy = (a, b) => { for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(b + s, { force: true }); } catch (e) { } } const d = new DatabaseSync(a); d.exec("PRAGMA wal_checkpoint(TRUNCATE)"); d.close(); fs.copyFileSync(a, b); };

(async () => {
  console.log("money store — a database from before the migration");
  const first = boot(LEGACY);
  ok(first.status === 0, "a fresh install boots", (first.stderr || "").slice(-400));
  let D = new DatabaseSync(LEGACY);
  /* back to the shape an existing install has: no guard, no money columns, no money tables */
  for (const t of D.prepare("SELECT name FROM sqlite_master WHERE type='trigger' AND name LIKE 'money%'").all()) D.exec("DROP TRIGGER " + t.name);
  for (const t of SPEC.tables) {
    const cols = [...t.amounts.map(c => c + "_minor"), "money_scale", "money_state", ...(t.refunds ? ["refunded_minor"] : []), ...(t.addCurrency ? ["currency"] : [])];
    for (const c of cols) D.exec(`ALTER TABLE ${t.table} DROP COLUMN ${c}`);
  }
  for (const t of ["money_migrations", "money_quarantine", "refunds"]) D.exec("DROP TABLE " + t);
  const has = (t, c) => D.prepare(`PRAGMA table_info(${t})`).all().some(x => x.name === c);
  ok(!has("orders", "total_minor") && !has("payments", "refunded_minor") && !has("order_items", "currency"), "the money columns are gone, as on an install from before");
  const tid = D.prepare("SELECT id FROM tenants ORDER BY id LIMIT 1").get().id;
  const order = (num, cur, sub, total) => Number(D.prepare("INSERT INTO orders(tenant_id,owner,num,sub,ship_fee,gift_used,tax,total,currency,status) VALUES(?,?,?,?,0,0,0,?,?, 'delivered')").run(tid, "t" + tid + ":g:legacy", num, sub, total, cur).lastInsertRowid);
  const ids = {
    exact: order("L-EXACT", "USD", 10.1, 10.1),
    noise: order("L-NOISE", "USD", 0.1 + 0.2, 0.1 + 0.2),
    excess: order("L-EXCESS", "USD", 10.235, 10.235),
    nocur: order("L-NOCUR", "", 49, 49),
    unknown: order("L-QQQ", "QQQ", 5, 5),
    kwd: order("L-KWD", "KWD", 12.345, 12.345),
    jpy: order("L-JPY", "JPY", 1500, 1500)
  };
  D.prepare("INSERT INTO order_items(order_id,product_id,qty,price) VALUES(?,?,?,?)").run(ids.kwd, "P-1", 1, 12.345);
  D.prepare("INSERT INTO order_items(order_id,product_id,qty,price) VALUES(?,?,?,?)").run(ids.excess, "P-2", 1, 10.235);
  const pay = (oid, amount, fee, cur) => Number(D.prepare("INSERT INTO payments(tenant_id,kind,order_id,gateway,method,amount,currency,fee,status,txn_ref) VALUES(?,?,?,?,?,?,?,?,?,?)").run(tid, "order", oid, "legacy", "card", amount, cur, fee, "captured", "lg_" + oid).lastInsertRowid);
  const pays = { exact: pay(ids.exact, 10.1, 0.59, "USD"), nocur: pay(ids.nocur, 49, 0, null) };
  D.prepare("INSERT INTO invoices(tenant_id,number,amount,currency,status) VALUES(?,?,?,?,?)").run(tid, "L-INV-TEXT", "abc", "USD", "draft");
  D.prepare("INSERT INTO settlements(tenant_id,ref,seller_id,gross,commission,net,status) VALUES(?,?,?,?,?,?,?)").run(tid, "L-STL", null, 100, 5, 95, "paid");
  const before = Object.fromEntries(Object.entries(ids).map(([k, id]) => [k, D.prepare("SELECT total FROM orders WHERE id=?").get(id).total]));
  D.close();
  copy(LEGACY, CRASH);

  console.log("\nmoney store — the migration, killed part-way");
  const killed = boot(CRASH, { LX_MONEY_CRASH_AFTER: "payments" });
  ok(killed.signal === "SIGKILL", "the process died inside the migration's transaction", { signal: killed.signal, status: killed.status });
  D = new DatabaseSync(CRASH);
  const m0 = D.prepare("SELECT status FROM money_migrations").all();
  ok(!m0.some(r => r.status === "done"), "the migration is not recorded as done", m0);
  ok(D.prepare("SELECT COUNT(*) c FROM orders WHERE money_scale IS NOT NULL").get().c === 0 && D.prepare("SELECT COUNT(*) c FROM money_quarantine").get().c === 0, "nothing it converted is left behind: the transaction rolled back");
  ok(D.prepare("SELECT COUNT(*) c FROM sqlite_master WHERE type='trigger' AND name LIKE 'money%'").get().c === 0, "no guard was installed");
  D.close();
  const resumed = boot(CRASH);
  ok(resumed.status === 0, "the next boot runs the migration again and completes", (resumed.stderr || "").slice(-400));

  console.log("\nmoney store — the migration");
  const up = boot(LEGACY);
  ok(up.status === 0, "an existing install boots on this code and migrates", (up.stderr || "").slice(-600));
  D = new DatabaseSync(LEGACY);
  const mig = D.prepare("SELECT * FROM money_migrations WHERE version=?").get(SPEC.migration);
  ok(mig && mig.status === "done", "migration " + SPEC.migration + " is recorded as done", mig);
  const rep = JSON.parse(mig.report);
  ok(rep.orders.normalizedAmounts >= 1 && rep.orders.quarantined === 3, "the report counts what was converted, normalized and quarantined", rep.orders);
  const O = id => D.prepare("SELECT * FROM orders WHERE id=?").get(id);
  ok(O(ids.exact).total_minor === 1010 && O(ids.exact).money_scale === 2 && O(ids.exact).money_state === null, "10.1 USD is exactly 1010 minor units at scale 2");
  ok(O(ids.kwd).total_minor === 12345 && O(ids.kwd).money_scale === 3, "12.345 KWD is 12345 minor units at the three decimals the master gives KWD");
  ok(O(ids.jpy).total_minor === 1500 && O(ids.jpy).money_scale === 0, "1500 JPY is 1500 at scale 0");
  const qn = D.prepare("SELECT * FROM money_quarantine WHERE table_name='orders' AND row_key=? AND column_name='total'").get(String(ids.noise));
  ok(O(ids.noise).total_minor === 30 && qn && qn.status === "normalized" && qn.source_value === "0.30000000000000004", "float residue 0.30000000000000004 becomes 30, and the conversion is recorded for audit", qn);
  const qx = D.prepare("SELECT * FROM money_quarantine WHERE table_name='orders' AND row_key=? AND column_name='total'").get(String(ids.excess));
  const cand = JSON.parse(qx.candidates);
  ok(O(ids.excess).money_state === "quarantined" && O(ids.excess).total_minor === null && qx.status === "open" && qx.reason === "excess_precision" && qx.source_value === "10.235", "10.235 of a two-decimal currency is quarantined, not rounded", qx);
  ok(cand["half-up"] === 1024 && cand["half-even"] === 1024 && cand.down === 1023 && cand.rule === "half-up", "its candidates are listed for the operator (half-up 1024, half-even 1024, down 1023)", cand);
  ok(O(ids.excess).total === before.excess && O(ids.nocur).total === before.nocur, "a quarantined row keeps its source values");
  ok(O(ids.noise).total === 0.3 && before.noise === 0.30000000000000004, "a normalized amount's projection is rewritten to the exact 0.3; its source stays in the quarantine record");
  ok(O(ids.nocur).money_state === "quarantined" && D.prepare("SELECT reason FROM money_quarantine WHERE row_key=? AND table_name='orders' LIMIT 1").get(String(ids.nocur)).reason === "currency_missing", "an order with no currency is quarantined — no currency is inferred");
  ok(O(ids.unknown).money_state === "quarantined" && D.prepare("SELECT reason FROM money_quarantine WHERE row_key=? AND table_name='orders' LIMIT 1").get(String(ids.unknown)).reason === "currency_unknown", "an order in a currency the master does not know is quarantined");
  const kitem = D.prepare("SELECT * FROM order_items WHERE order_id=?").get(ids.kwd);
  ok(kitem.currency === "KWD" && kitem.price_minor === 12345 && kitem.money_scale === 3, "an order line takes its currency from its order");
  ok(D.prepare("SELECT * FROM payments WHERE id=?").get(pays.exact).amount_minor === 1010 && D.prepare("SELECT * FROM payments WHERE id=?").get(pays.exact).fee_minor === 59, "a payment's amount and fee are exact");
  ok(D.prepare("SELECT money_state FROM payments WHERE id=?").get(pays.nocur).money_state === "quarantined", "a payment recorded without a currency is quarantined (payments were once labelled with the wrong currency, PR-028)");
  ok(D.prepare("SELECT money_state FROM invoices WHERE number='L-INV-TEXT'").get().money_state === "quarantined" && D.prepare("SELECT reason FROM money_quarantine WHERE table_name='invoices'").get().reason === "not_a_number", "text in a money column is quarantined as not a number");
  ok(D.prepare("SELECT money_state FROM settlements WHERE ref='L-STL'").get().money_state === "quarantined", "a settlement that never recorded its currency is quarantined");
  const C = new DatabaseSync(CRASH);
  const same = Object.values(ids).every(id => JSON.stringify(C.prepare("SELECT total_minor, money_scale, money_state FROM orders WHERE id=?").get(id)) === JSON.stringify(D.prepare("SELECT total_minor, money_scale, money_state FROM orders WHERE id=?").get(id)));
  ok(same && C.prepare("SELECT COUNT(*) c FROM money_quarantine").get().c === D.prepare("SELECT COUNT(*) c FROM money_quarantine").get().c, "the interrupted-then-resumed migration reached exactly the same result");
  C.close();

  console.log("\nmoney store — the guard");
  throws(() => D.prepare("UPDATE orders SET total = 10.11 WHERE id=?").run(ids.exact), /money_projection/, "a projection that disagrees with its minor units is refused by the database");
  throws(() => D.prepare("UPDATE orders SET total_minor = 1011 WHERE id=?").run(ids.exact), /money_projection/, "minor units changed without their projection are refused");
  throws(() => D.prepare("INSERT INTO payments(tenant_id,kind,gateway,amount,currency,status) VALUES(?,?,?,?,?,?)").run(tid, "order", "x", 1.5, "USD", "captured"), /money_projection/, "a payment written the old way (REAL only) is refused");
  throws(() => D.prepare("UPDATE payments SET refunded_minor = 1011 WHERE id=?").run(pays.exact), /money_projection/, "a refunded total above the captured amount is refused");
  D.prepare("UPDATE orders SET total = 1011 * 1.0 / 100, total_minor = 1011 WHERE id=?").run(ids.exact);
  ok(O(ids.exact).total === 10.11, "a consistent change is accepted");
  const qBefore = D.prepare("SELECT COUNT(*) c FROM money_quarantine").get().c;
  D.close();
  const again = boot(LEGACY);
  D = new DatabaseSync(LEGACY);
  ok(again.status === 0 && D.prepare("SELECT started_at FROM money_migrations").get().started_at === mig.started_at && D.prepare("SELECT COUNT(*) c FROM money_quarantine").get().c === qBefore, "a finished migration is not run again on the next boot");
  D.close();

  console.log("\nmoney store — resolving a quarantined amount, and refunds (in this process)");
  process.env.LX_TEST = "1"; process.env.LX_DB = LEGACY;
  const silence = console.log; console.log = () => { };
  const db = require("../lib/db.js");
  console.log = silence;
  const MS = require("../lib/money-store.js"), M = require("../lib/money.js"), R = require("../lib/refunds.js");
  let v = MS.verify();
  ok(v.ok && v.tables.orders.mismatched === 0 && v.tables.orders.unconverted === 0, "verify(): every converted amount's projection equals its minor units", v.tables.orders);
  ok(v.openQuarantine >= 7, "verify() reports the open quarantine", v.openQuarantine);
  const oxq = db.all("SELECT * FROM money_quarantine WHERE table_name='orders' AND row_key=? AND status='open' ORDER BY column_name", String(ids.excess));
  throws(() => MS.amountOf("orders", db.get("SELECT * FROM orders WHERE id=?", ids.excess), "total"), /under review/, "a quarantined row's amounts cannot be used");
  throws(() => MS.resolve(oxq[0].id, { minor: 1024 }), /who decided/, "a resolution names who decided it");
  for (const q of oxq) MS.resolve(q.id, { minor: 1024, by: "test-operator", note: "half-up per the policy" });
  const ox = db.get("SELECT * FROM orders WHERE id=?", ids.excess);
  ok(ox.money_state === null && ox.total_minor === 1024 && ox.total === 10.24 && db.get("SELECT source_value FROM money_quarantine WHERE id=?", oxq[0].id).source_value === "10.235", "resolved: the row is released at 10.24, the source 10.235 is kept in the quarantine record", ox);
  const nq = db.all("SELECT * FROM money_quarantine WHERE table_name='orders' AND row_key=? AND status='open'", String(ids.nocur));
  throws(() => MS.resolve(nq[0].id, { minor: 4900, by: "op" }), /needs its currency/, "an amount with no currency is resolved only with the currency stated");
  for (const q of nq) MS.resolve(q.id, { minor: q.column_name === "sub" || q.column_name === "total" ? 4900 : 0, currency: "USD", by: "op" });
  ok(db.get("SELECT money_state, currency FROM orders WHERE id=?", ids.nocur).currency === "USD" && db.get("SELECT money_state FROM orders WHERE id=?", ids.nocur).money_state === null, "with its currency stated, it is released");

  /* refunds on a captured payment of 100.00 */
  const pid = Number(MS.insert("payments", { tenant_id: tid, kind: "order", gateway: "legacy", method: "card", status: "captured", txn_ref: "rf_1", live: 0 }, "USD", { amount: "100.00", fee: "0" }).lastInsertRowid);
  const P = () => db.get("SELECT * FROM payments WHERE id=?", pid);
  const fail0 = async (fn, re, n) => { try { await fn(); ok(false, n, "did not refuse"); } catch (e) { ok(re.test(e.message) || re.test(e.code || ""), n, e.message); } };
  const fail = async (o, re, n) => { try { await R.refund(P(), o); ok(false, n, "did not refuse"); } catch (e) { ok(re.test(e.message) || re.test(e.code || ""), n, e.message); } };
  await fail({ amount: "30.00" }, /idempotency/, "a partial refund needs an idempotency key");
  await fail({ amount: "30.001", idem: "k0" }, /decimal/, "more decimals than the currency has are refused");
  await fail({ amount: "0", idem: "k0" }, /positive/, "a zero refund is refused");
  await fail({ amount: "-5", idem: "k0" }, /positive/, "a negative refund is refused");
  await fail({ amount: "5", currency: "EUR", idem: "k0" }, /not EUR/, "a refund in another currency is refused");
  const r1 = await R.refund(P(), { amount: "30.00", idem: "k1" });
  ok(r1.refund.amount_minor === 3000 && P().refunded_minor === 3000 && P().status === "captured" && r1.refundable.amount === "70.00", "a partial refund of 30.00 leaves 70.00 refundable and the payment captured", r1.refundable);
  const r1b = await R.refund(P(), { amount: "30.00", idem: "k1" });
  ok(r1b.replay && P().refunded_minor === 3000, "the same request again (same key) is not refunded twice");
  await fail({ amount: "31.00", idem: "k1" }, /different refund/, "the same key for a different amount is refused");
  await fail({ amount: "70.01", idem: "k2" }, /still refundable/, "a refund above what is left (70.00) is refused");
  /* a provider call that fails gives the reservation back; one with no answer keeps it */
  const live = () => ({ ...P(), live: 1 });
  await fail0(() => R.refund(live(), { amount: "10.00", idem: "k2b", refundAt: async () => ({ live: true, ok: true, status: "refunded" }) }), /whole payments only/, "part of a live payment is refused when its provider connector sends no amount");
  await (async () => { try { await R.refund(live(), { amount: "10.00", idem: "k3", partialAtProvider: true, refundAt: async () => ({ live: true, ok: false, error: "declined" }) }); } catch (e) { } })();
  ok(P().refunded_minor === 3000 && db.get("SELECT status FROM refunds WHERE idem_key='k3'").status === "failed", "a refund the provider refuses reserves nothing");
  const unk = await R.refund(live(), { amount: "10.00", idem: "k4", partialAtProvider: true, refundAt: async () => { throw new Error("socket hang up"); } });
  ok(unk.unknown && P().refunded_minor === 4000 && db.get("SELECT status FROM refunds WHERE idem_key='k4'").status === "unknown", "a provider call with no answer is neither refunded nor released: kept as unknown, still reserved", unk.refund && unk.refund.status);
  const r2 = await R.refund(P(), { amount: "60.00", idem: "k5" });
  ok(r2.refundable.amount === "0.00" && P().refunded_minor === 10000 && !r2.full && P().status === "captured", "with a refund still unknown, the payment is not reversed even when nothing is left to refund");
  const k4 = R.resolve(db.get("SELECT * FROM refunds WHERE idem_key='k4'"), require("../lib/states.js").first("refund", "success"), { by: "test-operator", note: "the provider's dashboard shows it" });
  ok(k4.refund.status === "succeeded" && k4.full, "an operator resolves the unknown refund as succeeded; with nothing left, the payment is reversed", k4.refund.status);
  ok(MS.verify().refundLedgerDrift === 0, "payments.refunded_minor equals the sum of its reserved refunds");
  await fail({ amount: "0.01", idem: "k6" }, /not_refundable|Only captured/, "a reversed payment refunds nothing more");

  /* two server processes race for the last 60.00 of a payment of 100.00 */
  const pid2 = Number(MS.insert("payments", { tenant_id: tid, kind: "order", gateway: "legacy", method: "card", status: "captured", txn_ref: "rf_2", live: 0 }, "USD", { amount: "100.00", fee: "0" }).lastInsertRowid);
  const racer = key => new Promise(resolve => {
    const c = spawn(process.execPath, ["-e", `const l=console.log;console.log=()=>{};require('./lib/db.js');console.log=l;const p=require('./lib/db.js').get('SELECT * FROM payments WHERE id=?',${pid2});require('./lib/refunds.js').refund(p,{amount:'60.00',idem:'${key}'}).then(r=>{console.log('OK '+r.refund.amount_minor);process.exit(0)},e=>{console.log('NO '+e.code);process.exit(0)})`], { cwd: ROOT, env: env(LEGACY), stdio: ["ignore", "pipe", "pipe"] });
    let out = ""; c.stdout.on("data", d => { out += d; }); c.on("exit", () => resolve(out.trim()));
  });
  const race = await Promise.all([racer("race-a"), racer("race-b")]);
  const won = race.filter(x => x.startsWith("OK")).length, lost = race.filter(x => /^NO exceeds_refundable/.test(x)).length;
  ok(won === 1 && lost === 1 && db.get("SELECT refunded_minor FROM payments WHERE id=?", pid2).refunded_minor === 6000, "two processes refunding 60.00 of 100.00 at once: one succeeds, the other is refused", race);
  /* reconciliation: a statement line matches only the payment's exact amount */
  const fin = require("../lib/fin.js");
  const rb = fin.reconcile(tid, { lines: [{ ref: "rf_2", amount: "99.99" }, { ref: "rf_2", amount: 100 }, { ref: "rf_2", amount: "100.00", currency: "EUR" }, { ref: "nope", amount: 1 }], source: "bank" });
  const rl = db.all("SELECT status FROM recon_lines WHERE batch_id=? ORDER BY id", rb.id).map(r => r.status);
  ok(JSON.stringify(rl) === '["amount_mismatch","matched","amount_mismatch","unmatched"]' && rb.status === "open" && rb.matched === 1, "a bank line for 99.99 against a 100.00 payment is a mismatch, not a match; another currency too", rl);

  /* an invoice is exact in its currency and its lines add up to it */
  const billing = require("../lib/billing.js");
  const inv = billing.issueInvoice(tid, { tax: false, note: "test" });
  const lines = db.all("SELECT amount_minor FROM invoice_lines WHERE invoice_id=?", inv.id);
  const irow = db.get("SELECT * FROM invoices WHERE id=?", inv.id);
  ok(irow.amount_minor === lines.reduce((n, l) => n + l.amount_minor, 0) && irow.currency === inv.currency && inv.money.amount.minor === String(irow.amount_minor), "an invoice's lines sum exactly to its amount, in its own currency", { inv: irow.amount_minor, lines });

  v = MS.verify();
  ok(v.ok && v.refundLedgerDrift === 0, "after all of it, verify() is clean", v.ok ? "" : v);

  try { fs.rmSync(DIR, { recursive: true, force: true }); } catch (e) { }
  console.log(`\n${passed} passed, ${failed} failed`);
  process.exit(failed ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
