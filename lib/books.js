/* LUXORA Platform — a store's books (owner Value).

   The chart of accounts (lib/seed/books.json) is on the kernel: every account is a books.account
   node, placed in the books.chart hierarchy under its group; a store's own accounts live in its
   namespace. Entries are journals of the platform's ONE ledger (lib/wallet.js): they balance in
   every currency, are written to the kernel's hash-chained log first, are never edited or deleted,
   and are corrected by a linked reversal — the same engine that keeps wallets.

   Business events post themselves: a rule names a record (lib/row-records.js), the change that
   triggers it (a status moving into a tagged state, an amount changing) and the account each part
   of the amount goes to. Every automatic entry has an idempotency key, so it is posted once; a
   record whose entry could not be posted (an unknown currency) is reported by health(), never
   lost silently, and does not stop the sale.

   Reports are read from the postings: trial balance, profit and loss, balance sheet, an account's
   ledger — each per currency, over any period. */
"use strict";

const db = () => require("./db.js");
const K = require("./kernel.js");
const W = () => require("./wallet.js");
const RR = () => require("./row-records.js");
const states = () => require("./states.js");
const SEED = require("./seed/books.json");
const NS = tid => require("./master-permissions.js").storeHolder(tid);
const H = SEED.hierarchy.hierarchy;
const fail = (msg, status, code) => { const e = new Error(msg); e.status = status || 400; if (code) e.code = code; throw e; };
const KEY = code => "books:" + code;

/* ============================== the chart ============================== */
let declared = false;
function declare() {
  if (declared) return;
  K.ensureTables();
  const k = K.kindOf(SEED.kind.kind, "platform");
  if (!k || k.attributes.length !== SEED.kind.attributes.length || !k.schemes.includes(SCHEME)) K.defineKind({ ...SEED.kind, namespace: "platform" }, SEED.actor);
  if (!K.hierarchyOf(H, "platform")) K.defineHierarchy({ ...SEED.hierarchy, namespace: "platform" }, SEED.actor);
  declared = true;
}
/* an account's code is unique within the chart it belongs to: "platform/4000", "tenant:1/4010" */
const SCHEME = "books-account";
const nodeOfCode = (code, ns) => K.resolveIdentifier(SCHEME, ns + "/" + code);
function addAccount(ns, a, actor) {
  if (!SEED.types[a.type]) fail("Unknown account type: " + a.type);
  if (!/^[0-9A-Za-z.-]{1,20}$/.test(String(a.code || ""))) fail("An account code is 1–20 letters, digits, dots or dashes");
  if (!String(a.name || "").trim()) fail("Name the account");
  if (nodeOfCode(a.code, ns) || (ns !== "platform" && nodeOfCode(a.code, "platform"))) fail("Account " + a.code + " already exists", 409);
  const uid = K.createNode(SEED.kind.kind, { namespace: ns, attributes: { code: String(a.code), name: String(a.name).slice(0, 120), type: a.type, group: !!a.group } }, actor);
  K.assignIdentifier(uid, SCHEME, ns + "/" + a.code, {}, actor);
  if (a.parent) {
    const p = nodeOfCode(a.parent, ns) || nodeOfCode(a.parent, "platform");
    if (!p) fail("No group account " + a.parent);
    K.place(H, uid, p, { namespace: "platform" }, actor);
  }
  return uid;
}
function seed() {
  return K.internal.tx(() => {
    declare();
    let n = 0;
    for (const a of SEED.chart) if (!nodeOfCode(a.code, "platform")) { addAccount("platform", a, SEED.actor); n++; }
    return n;
  });
}
/* the accounts a store keeps: the platform's chart, then its own */
function accounts(tid) {
  declare();
  const mine = ["platform/", NS(tid) + "/"];
  const rows = db().all("SELECT node, value FROM k_identifiers WHERE scheme=? AND rec_to IS NULL AND valid_to IS NULL ORDER BY id", SCHEME)
    .filter(r => mine.some(m => r.value.startsWith(m))).map(r => ({ node: r.node, namespace: r.value.slice(0, r.value.lastIndexOf("/")) }));
  return rows.sort((x, y) => String((K.attributes(x.node) || {}).code) < String((K.attributes(y.node) || {}).code) ? -1 : 1).map(r => {
    const a = K.attributes(r.node) || {};
    const parent = K.parents(H, r.node, { namespace: "platform" })[0];
    return { code: a.code, name: a.name, type: a.type, group: !!a.group, own: r.namespace !== "platform", parent: parent ? (K.attributes(parent) || {}).code : null, uid: r.node };
  });
}
function account(tid, code) {
  const a = accounts(tid).find(x => x.code === String(code));
  if (!a) fail("No account " + code + " in this store's chart", 404, "account_unknown");
  if (a.group) fail("Account " + code + " is a group: post to an account under it", 400, "account_group");
  return a;
}
function define(tid, input, actor) {
  const i = input || {};
  if (!i.parent) fail("Say which group the account sits under");
  const parent = accounts(tid).find(x => x.code === String(i.parent));
  if (!parent) fail("No group account " + i.parent);
  return K.internal.tx(() => { addAccount(NS(tid), { code: i.code, name: i.name, type: parent.type, parent: parent.code }, actor || SEED.actor); return accounts(tid).find(x => x.code === String(i.code)); });
}
/* the ledger account behind a chart account in one currency */
function ledgerAccount(tid, code, unit) {
  let a = db().get("SELECT * FROM ledger_accounts WHERE tenant_id=? AND system_key=? AND unit=?", Number(tid), KEY(code), unit);
  if (!a) { db().run("INSERT INTO ledger_accounts(tenant_id,system_key,unit) VALUES(?,?,?)", Number(tid), KEY(code), unit); a = db().get("SELECT * FROM ledger_accounts WHERE tenant_id=? AND system_key=? AND unit=?", Number(tid), KEY(code), unit); }
  return a;
}

/* ============================== entries ============================== */
const minor = (amount, unit) => Math.round(Number(amount || 0) * Math.pow(10, W().unitOf(unit).decimals));
const major = (m, unit) => Number((m / Math.pow(10, W().unitOf(unit).decimals)).toFixed(W().unitOf(unit).decimals));
/* lines [{ account: code, debit?: minor, credit?: minor }] in one currency; debits are positive */
function post(tid, entry, actor) {
  const e = entry || {}, unit = String(e.unit || "").toUpperCase();
  W().unitOf(unit);
  const lines = (e.lines || []).map(l => ({ code: String(l.account), amount: (Number(l.debit) || 0) - (Number(l.credit) || 0) })).filter(l => l.amount !== 0);
  if (lines.length < 2) fail("An entry needs at least two lines");
  if (lines.some(l => !Number.isSafeInteger(l.amount))) fail("Amounts are whole minor units");
  if (lines.reduce((s, l) => s + l.amount, 0) !== 0) fail("Debits and credits must be equal", 400, "entry_unbalanced");
  if (e.idem && db().get("SELECT id FROM ledger_journals WHERE tenant_id=? AND idem_key=?", Number(tid), String(e.idem))) return null;
  return K.internal.tx(() => {
    for (const l of lines) account(tid, l.code);
    const sums = {};
    for (const l of lines) sums[l.code] = (sums[l.code] || 0) + l.amount;
    return W().writeJournal(tid, { op: "books." + (e.op || "entry"), ref: e.ref || "", idem: e.idem || null, actor: actor || SEED.actor, reason: String(e.memo || "").slice(0, 300) },
      Object.entries(sums).filter(([, a]) => a !== 0).map(([code, amount]) => ({ account: ledgerAccount(tid, code, unit).id, unit, amount })));
  });
}
/* an accountant's entry, in major units: [{ account, debit | credit }] */
function manual(tid, input, actor) {
  const i = input || {}, unit = String(i.currency || require("./defaults.js").currency(tid)).toUpperCase();
  const lines = (i.lines || []).map(l => ({ account: l.account, debit: minor(l.debit, unit), credit: minor(l.credit, unit) }));
  if (!String(i.memo || "").trim()) fail("Say what the entry is for");
  return entry(post(tid, { unit, lines, op: "manual", ref: i.ref || "", memo: i.memo }, actor));
}
function reverse(tid, id, actor, reason) {
  const j = db().get("SELECT * FROM ledger_journals WHERE id=? AND tenant_id=?", Number(id), Number(tid));
  if (!j || !String(j.op).startsWith("books.")) fail("Entry not found", 404);
  if (!SEED.reversible.includes(j.op.slice(6))) fail("This entry was posted by the business event it records: it is corrected by the event that undoes it (a refund, a reversal of the payment)", 409, "entry_automatic");
  return entry(W().reverse(tid, j.id, actor, reason).id);
}
function entry(id) {
  if (!id) return null;
  const j = db().get("SELECT * FROM ledger_journals WHERE id=?", Number(id));
  const lines = db().all("SELECT a.system_key, p.unit, p.amount FROM ledger_postings p JOIN ledger_accounts a ON a.id=p.account_id WHERE p.journal_id=? ORDER BY p.id", j.id)
    .map(p => ({ account: p.system_key.slice(6), debit: p.amount > 0 ? major(p.amount, p.unit) : 0, credit: p.amount < 0 ? major(-p.amount, p.unit) : 0, currency: p.unit }));
  const op = j.op.slice(6), reversed = !!db().get("SELECT 1 FROM ledger_journals WHERE reverses=?", j.id);
  /* only what a person posted is reversed by a person; what a sale or refund posted is corrected by the business event that undoes it */
  return { id: j.id, op, ref: j.ref, memo: j.reason, actor: j.actor, at: j.created_at, reverses: j.reverses, reversed, reversible: SEED.reversible.includes(op) && !j.reverses && !reversed, lines };
}
function entries(tid, f) {
  const o = f || {};
  return db().all(`SELECT id FROM ledger_journals WHERE tenant_id=? AND op LIKE 'books.%' AND (?='' OR created_at>=?) AND (?='' OR created_at<?) AND (?='' OR ref=?) ORDER BY id DESC LIMIT ?`,
    Number(tid), o.from || "", o.from || "", o.to || "", o.to || "", o.ref || "", o.ref || "", Math.min(Number(o.limit) || 200, 1000)).map(r => entry(r.id));
}

/* ============================== automatic postings ============================== */
/* a record's status belongs to the state machine of the record's own name (payment, invoice) */
const into = (machine, value, tag) => !!value && states().has(machine, value) && states().is(machine, value, tag);
/* the parts of an amount a rule's lines name, in minor units of the record's currency, by the
   measure the record's source declares (lib/seed/books.json sources) */
const MEASURES = {
  invoice: (row, before, after, m) => ({ invoiced: m(row.amount) }),
  receipt: (row, before, after, m) => ({ received: m(row.value) }),
  /* the matched part clears what was received; the difference to the bill's net is a price difference */
  bill: (row, before, after, m) => { const net = m(row.net), matched = m(row.matched); return { matched, variance: net - matched, tax: m(row.tax), gross: m(row.gross) }; },
  payment: (row, before, after, m) => paymentParts(row, before, after, m),
  /* an invoice to a client: its fees (time and fixed instalments), the expenses billed on, the tax and what is owed */
  client_invoice: (row, before, after, m) => ({ fees: m(row.fees), expenses: m(row.expenses), tax: m(row.tax), gross: m(row.gross) }),
  expense: (row, before, after, m) => ({ amount: m(row.amount) })
};
function parts(name, row, before, after, unit) { return MEASURES[SEED.sources[name].measure](row, before, after, v => minor(v, unit)); }
function paymentParts(row, before, after, m) {
  const o = row.order_id ? db().get("SELECT * FROM orders WHERE id=?", row.order_id) : null;
  const paid = m(row.amount), credit = o ? m(o.gift_used) : 0, gross = paid + credit;
  const share = (x, of) => of > 0 ? Math.round(x * of) : 0;
  const base = o ? Number(o.total || 0) + Number(o.gift_used || 0) : 0;
  const taxR = base > 0 ? Number(o.tax || 0) / base : 0, shipR = base > 0 ? Number(o.ship_fee || 0) / base : 0;
  const tax = share(gross, taxR), delivery = share(gross, shipR);
  const refund = m(after.refunded) - m(before.refunded || 0), refund_tax = share(refund, taxR);
  return { paid, credit_used: credit, tax, delivery, sales: gross - tax - delivery, fee: m(row.fee),
    refund, refund_tax, refund_net: refund - refund_tax, unrefunded: paid - m(row.refunded) };
}
function fires(rule, name, row, before, after) {
  if (rule.record !== name) return false;
  for (const [k, v] of Object.entries(rule.where || {})) if (String(row[k]) !== String(v)) return false;
  const w = rule.when, was = before[w.fact], now = after[w.fact];
  if (w.changes) return now !== undefined && Number(now || 0) !== Number(was || 0);
  if (w.from && !into(name, was, w.from)) return false;
  return into(name, now, w.into) && !into(name, was, w.into);
}
const unposted = [];
function observe({ name, row, before, after, uid }) {
  for (const rule of SEED.rules) {
    if (!fires(rule, name, row, before, after)) continue;
    try {
      const unit = String(row.currency || require("./defaults.js").currency(row.tenant_id)).toUpperCase();
      const p = parts(name, row, before, after, unit);
      const lines = rule.lines.map(l => ({ account: l.debit || l.credit, [l.debit ? "debit" : "credit"]: p[l.part] }));
      if (!lines.some(l => (l.debit || l.credit))) continue;
      post(row.tenant_id, { unit, lines, op: rule.key, ref: uid, memo: rule.label, idem: `books:${rule.key}:${uid}:${rule.when.changes ? K.lastSeq() : "once"}` }, SEED.actor);
    } catch (e) {
      unposted.push({ rule: rule.key, record: name, uid, error: e.message });
      console.error("books: " + rule.key + " not posted for " + uid + ": " + e.message);
    }
  }
}
/* records the books have never seen get their entries as they stand now (once) */
function importRows() {
  return K.internal.tx(() => {
    seed();
    let n = 0;
    for (const [name, src] of Object.entries(SEED.sources)) {
      for (const row of db().all(`SELECT * FROM ${src.table} ORDER BY id`)) {
        if (!row.uid || db().get("SELECT 1 FROM ledger_journals WHERE ref=? AND op LIKE 'books.%' LIMIT 1", row.uid)) continue;
        const now = { ...row };
        /* replayed as it happened: a payment that was ever captured is captured first, then its
           refunds and a lost chargeback follow, so each rule sees the change it posts */
        const everPaid = (src.everPaid || []).some(t => into(name, row.status, t));
        const first = { ...now, refunded: 0, status: everPaid ? states().first(name, src.firstState) : row.status };
        observe({ name, row, before: {}, after: first, uid: row.uid });
        if (everPaid) observe({ name, row, before: first, after: now, uid: row.uid });
        n++;
      }
    }
    return n;
  });
}

/* ============================== reports ============================== */
function balances(tid, o) {
  const f = o || {};
  const rows = db().all(`SELECT a.system_key k, p.unit u, SUM(CASE WHEN p.amount>0 THEN p.amount ELSE 0 END) d, SUM(CASE WHEN p.amount<0 THEN -p.amount ELSE 0 END) c
     FROM ledger_postings p JOIN ledger_accounts a ON a.id=p.account_id JOIN ledger_journals j ON j.id=p.journal_id
     WHERE j.tenant_id=? AND a.system_key LIKE 'books:%' AND (?='' OR j.created_at>=?) AND (?='' OR j.created_at<?) AND (?='' OR p.unit=?)
     GROUP BY a.system_key, p.unit`, Number(tid), f.from || "", f.from || "", f.to || "", f.to || "", f.currency || "", f.currency || "");
  const chart = Object.fromEntries(accounts(tid).map(a => [a.code, a]));
  return rows.map(r => { const a = chart[r.k.slice(6)]; if (!a) fail("Postings to an account no longer in the chart: " + r.k.slice(6), 500, "account_lost"); const normal = SEED.types[a.type].normal;
    return { account: a.code, name: a.name, type: a.type, currency: r.u, debit: major(r.d, r.u), credit: major(r.c, r.u), balance: major(normal === "debit" ? r.d - r.c : r.c - r.d, r.u) }; })
    .sort((a, b) => a.account < b.account ? -1 : 1);
}
const byCurrency = rows => rows.reduce((m, r) => ((m[r.currency] = m[r.currency] || []).push(r), m), {});
function trialBalance(tid, o) {
  return Object.entries(byCurrency(balances(tid, o))).map(([currency, rows]) => ({ currency, rows,
    debit: +rows.reduce((s, r) => s + r.debit, 0).toFixed(6), credit: +rows.reduce((s, r) => s + r.credit, 0).toFixed(6) }));
}
const sum = rows => +rows.reduce((s, r) => s + r.balance, 0).toFixed(6);
/* a statement's sections, each the accounts of the types that show there (lib/seed/books.json
   types[].side); a credit-normal section adds to what the debit-normal sections are set against */
function sections(rows, statement) {
  const out = {};
  for (const [t, d] of Object.entries(SEED.types)) if (d.statement === statement) out[d.side] = rows.filter(r => r.type === t);
  return out;
}
const sideTotal = (sec, normal) => +Object.entries(SEED.types).filter(([, d]) => d.normal === normal && sec[d.side]).reduce((s, [, d]) => s + sum(sec[d.side]), 0).toFixed(6);
function profitAndLoss(tid, o) {
  return Object.entries(byCurrency(balances(tid, o))).map(([currency, rows]) => {
    const sec = sections(rows, "profit"), totalIncome = sideTotal(sec, "credit"), totalExpense = sideTotal(sec, "debit");
    return { currency, ...sec, totalIncome, totalExpense, profit: +(totalIncome - totalExpense).toFixed(6) };
  });
}
function balanceSheet(tid, o) {
  const at = { to: (o || {}).at || "" };
  const pl = Object.fromEntries(profitAndLoss(tid, at).map(p => [p.currency, p.profit]));
  return Object.entries(byCurrency(balances(tid, at))).map(([currency, rows]) => {
    const sec = sections(rows, "balance"), earnings = pl[currency] || 0;
    return { currency, ...sec, earnings, totalAssets: sideTotal(sec, "debit"), totalLiabilitiesAndEquity: +(sideTotal(sec, "credit") + earnings).toFixed(6) };
  });
}
function ledger(tid, code, o) {
  account(tid, code);
  const f = o || {};
  return db().all(`SELECT j.id, j.op, j.ref, j.reason, j.created_at, p.unit, p.amount FROM ledger_postings p JOIN ledger_accounts a ON a.id=p.account_id JOIN ledger_journals j ON j.id=p.journal_id
     WHERE j.tenant_id=? AND a.system_key=? AND (?='' OR j.created_at>=?) AND (?='' OR j.created_at<?) ORDER BY j.id`, Number(tid), KEY(code), f.from || "", f.from || "", f.to || "", f.to || "")
    .map(r => ({ entry: r.id, op: r.op.slice(6), ref: r.ref, memo: r.reason, at: r.created_at, currency: r.unit, debit: r.amount > 0 ? major(r.amount, r.unit) : 0, credit: r.amount < 0 ? major(-r.amount, r.unit) : 0 }));
}
/* every payment and invoice has its entries; every entry balances and matches the log */
function health(tid) {
  const missing = [];
  for (const [name, src] of Object.entries(SEED.sources))
    for (const r of db().all(`SELECT * FROM ${src.table} WHERE tenant_id=?`, Number(tid))) {
      /* a rule that fires only from a given state (a void after approval) cannot be judged from where the row stands now */
      const should = SEED.rules.some(rule => rule.record === name && !rule.when.from && Object.entries(rule.where || {}).every(([k, v]) => String(r[k]) === String(v)) && rule.when.into && into(name, r.status, rule.when.into));
      if (should && !db().get("SELECT 1 FROM ledger_journals WHERE ref=? AND op LIKE 'books.%' LIMIT 1", r.uid)) missing.push(r.uid);
    }
  const v = W().verify(tid);
  return { missing, unposted: unposted.filter(u => missing.includes(u.uid)), unbalanced: v.unbalanced, drift: v.drift, chain: v.chain };
}

/* every record the books post from (lib/seed/books.json sources) */
for (const name of Object.keys(SEED.sources)) RR().on(name, observe);
module.exports = { declare, seed, accounts, define, post, manual, reverse, entry, entries, trialBalance, profitAndLoss, balanceSheet, ledger, health, importRows, SEED };
