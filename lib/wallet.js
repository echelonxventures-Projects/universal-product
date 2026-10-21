/* LUXORA Platform — the Universal Wallet: definitions, wallets, the ledger, holds.

   A wallet DEFINITION is a versioned blueprint in a namespace (lib/seed/wallet.json, and any the
   console adds): its names in any language with any aliases, the value classes it may hold
   (Value's classes), the operations it allows and its policy. A new version never changes the
   meaning of a wallet bound to an older one.

   A WALLET is an owner's instance: an immutable id, one unit of value (Value's master — a
   currency, points, credits), the definition version it binds, and names it may change at will
   (every name it has had is kept). An owner may hold any number of wallets, of one definition
   or many, with the same name or different ones — the definition's policy caps how many.

   Value moves only as JOURNALS: each is two or more POSTINGS in exact minor units that sum to
   zero per unit, against a wallet and a system account (issuance, clearing, migration,
   suspense — the seed's systemAccounts). A journal is immutable (corrected by a linked
   reversal), carries an idempotency key (the same key and request return the first outcome;
   the same key with a different request is refused) and is one event in the kernel's
   hash-chained log. A wallet's balance is a projection of its postings:
     posted     the sum of its postings
     reserved   what its active holds still keep
     available  posted − reserved (+ the definition's overdraft)
   HOLDS reserve value for a purpose and are captured (posting what is spent) or released, by
   the `wallet_hold` machine; a wallet's own life is the `wallet` machine. The single-balance
   `wallets` table is kept as the projection the older readers use (the default wallet's
   posted balance), written only here. Domain: Value. */
"use strict";

const crypto = require("crypto");
const { run, get, all } = require("./db.js");
const states = require("./states.js");
const SEED = require("./seed/wallet.json");

const K = () => require("./kernel.js");
const tx = fn => K().internal.tx(fn);
const fail = (msg, status, code) => Object.assign(new Error(msg), { status: status || 400, code: code || "" });
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };
const nowSql = () => new Date().toISOString().slice(0, 19).replace("T", " ");
const reg = () => require("./registry.js");

/* ============================== units: exact minor amounts ============================== */
/* a unit is a row of Value's master (lib/registry.js unit); its decimals fix its minor unit. A
   unit's `active` says whether stores may price in it, not whether it may be held: any registered
   unit may be held — whether it may be issued in a place is the jurisdiction gate's (slice 6) */
function unitOf(code) {
  const u = reg().unit(code);
  if (!u) throw fail("Unknown unit of value: " + code, 400, "unit_unknown");
  return u;
}
/* "12.34" → 1234 at 2 decimals, with no floating arithmetic; more decimals than the unit has is refused */
function toMinor(amount, decimals) {
  const s = typeof amount === "number" ? amount.toFixed(Math.min(20, decimals + 6)).replace(/0+$/, "").replace(/\.$/, "") : String(amount == null ? "" : amount).trim();
  const m = /^(-)?(\d+)(?:\.(\d+))?$/.exec(s);
  if (!m) throw fail("Not an amount: " + amount, 400, "amount_invalid");
  const frac = (m[3] || "").replace(/0+$/, "");
  if (frac.length > decimals) throw fail("At most " + decimals + " decimal places for this unit", 400, "amount_precision");
  const minor = BigInt(m[2]) * 10n ** BigInt(decimals) + BigInt((frac + "0".repeat(decimals)).slice(0, decimals) || "0");
  const v = Number(m[1] ? -minor : minor);
  if (!Number.isSafeInteger(v)) throw fail("Amount out of range", 400, "amount_range");
  return v;
}
const toMajor = (minor, decimals) => Number(minor) / 10 ** decimals;

/* ============================== definitions ============================== */
const ops = () => SEED.operations;
const opOf = key => ops().find(o => o.key === key) || null;
const classesOf = () => reg().list(require("./seed/value.json").classList).map(x => (typeof x === "string" ? x : x.key));
/* the open version of a definition (or a given version) */
function definition(key, version, namespace) {
  const ns = namespace || SEED.namespace;
  const r = version ? get("SELECT * FROM wallet_definitions WHERE namespace=? AND key=? AND version=?", ns, String(key), Number(version))
    : get("SELECT * FROM wallet_definitions WHERE namespace=? AND key=? AND status='active' ORDER BY version DESC LIMIT 1", ns, String(key));
  return r ? { ...r, spec: J(r.spec, {}) } : null;
}
function definitions(namespace) {
  return all("SELECT * FROM wallet_definitions WHERE namespace=? AND status='active' ORDER BY key, version DESC", namespace || SEED.namespace)
    .filter((r, i, a) => a.findIndex(x => x.key === r.key) === i).map(r => ({ ...r, spec: J(r.spec, {}) }));
}
/* declare a definition: a new version when its spec changes, the same one when it does not */
function define(input, actor) {
  const i = input || {};
  const ns = String(i.namespace || SEED.namespace);
  const key = String(i.key || "");
  if (!/^[a-z][a-z0-9_.-]{0,63}$/.test(key)) throw fail("A definition needs a key: lowercase letters, digits, _ . -");
  const names = i.name && typeof i.name === "object" ? i.name : null;
  if (!names || !Object.values(names).some(v => String(v || "").trim())) throw fail("A definition needs a name");
  const known = classesOf();
  const classes = (i.classes || []).map(String);
  if (!classes.length || classes.some(c => !known.includes(c))) throw fail("A definition holds value classes Value declares: " + known.join(", "));
  const allowed = [...ops().map(o => o.key), "hold"];
  const operations = (i.operations || []).map(String);
  if (operations.some(o => !allowed.includes(o))) throw fail("Unknown operation: " + operations.filter(o => !allowed.includes(o)).join(", "));
  const p = i.policy || {};
  const policy = { overdraft: Math.max(0, Number(p.overdraft) || 0), max_balance: Math.max(0, Number(p.max_balance) || 0), max_wallets_per_owner: Math.max(0, Math.floor(Number(p.max_wallets_per_owner) || 0)), hold_minutes: Math.max(0, Number(p.hold_minutes) || 0) };
  const spec = { name: names, aliases: i.aliases || {}, classes, operations, policy, default: !!i.default };
  const cur = definition(key, null, ns);
  if (cur && JSON.stringify(cur.spec) === JSON.stringify(spec)) return cur;
  const version = cur ? cur.version + 1 : 1;
  run("INSERT INTO wallet_definitions(namespace,key,version,spec,status,actor) VALUES(?,?,?,?,?,?)", ns, key, version, JSON.stringify(spec), "active", String(actor || "system"));
  return definition(key, version, ns);
}
function seed() {
  for (const d of SEED.definitions) rebind(define(d, "seed"), "seed");
}
/* wallets bound to an older version move to the open one only when it widens what they may do
   (every class and operation kept, no policy tightened); anything else needs its own migration */
function rebind(d, actor) {
  let n = 0;
  for (const old of all("SELECT DISTINCT definition_version v FROM wallet_instances WHERE namespace=? AND definition_key=? AND definition_version<?", d.namespace, d.key, d.version)) {
    const o = definition(d.key, old.v, d.namespace).spec, c = d.spec;
    const widens = o.classes.every(x => c.classes.includes(x)) && o.operations.every(x => c.operations.includes(x))
      && c.policy.overdraft >= o.policy.overdraft && (!c.policy.max_balance || (o.policy.max_balance && c.policy.max_balance >= o.policy.max_balance))
      && (!c.policy.max_wallets_per_owner || (o.policy.max_wallets_per_owner && c.policy.max_wallets_per_owner >= o.policy.max_wallets_per_owner))
      && (!o.policy.hold_minutes || c.policy.hold_minutes >= o.policy.hold_minutes);
    if (!widens) continue;
    n += run("UPDATE wallet_instances SET definition_version=? WHERE namespace=? AND definition_key=? AND definition_version=?", d.version, d.namespace, d.key, old.v).changes;
    K().append("value.definition.rebound", { namespace: "value", subject: d.key, actor: String(actor || ""), payload: { from: old.v, to: d.version } });
  }
  return n;
}

/* ============================== wallets ============================== */
const M = SEED.machines.wallet, H = SEED.machines.hold;
/* the language a name is written in when the caller names none: the platform's source language */
const sourceLang = () => require("./expression.js").SEED.sourceLanguage;
function walletRow(id) { return get("SELECT * FROM wallet_instances WHERE id=?", String(id)); }
function nameOf(w, lang) {
  const n = get("SELECT name FROM wallet_names WHERE wallet_id=? AND lang=? AND valid_to IS NULL AND alias=0 ORDER BY id DESC LIMIT 1", w.id, lang || sourceLang())
    || get("SELECT name FROM wallet_names WHERE wallet_id=? AND valid_to IS NULL AND alias=0 ORDER BY id DESC LIMIT 1", w.id);
  return n ? n.name : "";
}
function present(w) {
  if (!w) return null;
  const d = definition(w.definition_key, w.definition_version, w.namespace) || { spec: {} };
  const u = unitOf(w.unit);
  const b = balanceMinor(w.id);
  return { id: w.id, owner: w.owner, unit: w.unit, decimals: u.decimals, name: nameOf(w), aliases: all("SELECT lang, name FROM wallet_names WHERE wallet_id=? AND valid_to IS NULL AND alias=1", w.id),
    definition: { key: w.definition_key, version: w.definition_version, name: d.spec.name }, state: states.display(M, w.status),
    posted: toMajor(b.posted, u.decimals), reserved: toMajor(b.reserved, u.decimals), available: toMajor(b.available, u.decimals), created_at: w.created_at };
}
/* open a wallet of a definition in a unit, named as the owner likes */
function open(tid, owner, input, actor) {
  const i = input || {};
  const d = definition(i.definition || defaultDefinition().key, null, i.namespace);
  if (!d) throw fail("Unknown wallet definition: " + i.definition, 404, "definition_unknown");
  const u = unitOf(i.unit || require("./defaults.js").currency(tid));
  if (!d.spec.classes.includes(u.class)) throw fail(nameText(d.spec.name) + " does not hold " + u.name, 400, "unit_incompatible");
  const cap = d.spec.policy.max_wallets_per_owner;
  /* the cap counts an owner's open wallets of the definition in that unit */
  if (cap && get("SELECT COUNT(*) n FROM wallet_instances WHERE tenant_id=? AND owner=? AND namespace=? AND definition_key=? AND unit=? AND status<>?", Number(tid), String(owner), d.namespace, d.key, u.code, states.first(M, "closed")).n >= cap)
    throw fail("No more of these may be opened in " + u.name + ": " + nameText(d.spec.name), 409, "wallet_cap");
  const id = "wal_" + crypto.randomBytes(10).toString("hex");
  return tx(() => {
    run("INSERT INTO wallet_instances(id,tenant_id,owner,namespace,definition_key,definition_version,unit,status) VALUES(?,?,?,?,?,?,?,?)",
      id, Number(tid), String(owner), d.namespace, d.key, d.version, u.code, states.initial(M));
    const name = String(i.name || "").trim() || nameText(d.spec.name);
    run("INSERT INTO wallet_names(wallet_id,lang,name,alias,actor) VALUES(?,?,?,0,?)", id, String(i.lang || sourceLang()), name.slice(0, 80), String(actor || owner));
    run("INSERT INTO ledger_accounts(tenant_id,wallet_id,unit) VALUES(?,?,?)", Number(tid), id, u.code);
    K().append("value.wallet.opened", { namespace: "value", subject: id, actor: String(actor || owner), payload: { tenant: Number(tid), owner: String(owner), definition: d.key + "@" + d.version, unit: u.code } });
    return present(walletRow(id));
  });
}
const nameText = n => (n && (n[sourceLang()] || Object.values(n)[0])) || "";
const defaultDefinition = () => definitions().find(d => d.spec.default) || definitions()[0];
/* rename: the old name's interval closes; identity, balances and history do not change */
function rename(tid, owner, id, input, actor) {
  const w = own(tid, owner, id);
  const i = input || {};
  const name = String(i.name || "").trim().slice(0, 80);
  if (!name) throw fail("Give the wallet a name");
  const lang = String(i.lang || sourceLang());
  return tx(() => {
    run("UPDATE wallet_names SET valid_to=datetime('now') WHERE wallet_id=? AND lang=? AND alias=? AND valid_to IS NULL", w.id, lang, i.alias ? 1 : 0);
    run("INSERT INTO wallet_names(wallet_id,lang,name,alias,actor) VALUES(?,?,?,?,?)", w.id, lang, name, i.alias ? 1 : 0, String(actor || owner));
    K().append("value.wallet.renamed", { namespace: "value", subject: w.id, actor: String(actor || owner), payload: { lang, name, alias: !!i.alias } });
    return present(walletRow(w.id));
  });
}
function names(id) { return all("SELECT lang, name, alias, valid_from, valid_to FROM wallet_names WHERE wallet_id=? ORDER BY id", String(id)); }
/* a wallet the caller owns (staff pass owner null to act on any wallet of the store) */
function own(tid, owner, id) {
  const w = walletRow(id);
  if (!w || w.tenant_id !== Number(tid) || (owner != null && w.owner !== String(owner))) throw fail("Wallet not found", 404, "wallet_unknown");
  return w;
}
function walletsOf(tid, owner) { return all("SELECT * FROM wallet_instances WHERE tenant_id=? AND owner=? ORDER BY created_at, id", Number(tid), String(owner)).map(present); }
/* a wallet's life: staff restrict, suspend, reopen or close it — moves are the machine's */
function move(tid, id, action, actor, reason) {
  const w = own(tid, null, id);
  const to = states.actionTarget(M, action);
  if (!to || !states.can(M, w.status, to)) throw fail("That cannot be done to this wallet now", 409, "wallet_state");
  if (!String(reason || "").trim()) throw fail("Say why", 400, "reason_required");
  if (states.is(M, to, "closed")) {
    const b = balanceMinor(w.id);
    if (b.posted !== 0 || b.reserved !== 0) throw fail("A wallet is closed only when it holds nothing and keeps nothing", 409, "wallet_not_empty");
  }
  return tx(() => {
    const mv = states.apply(M, { tenantId: Number(tid), from: w.status, to, row: w });
    const p = { ...mv.patch };
    const cols = Object.keys(p);
    run("UPDATE wallet_instances SET " + cols.map(c => c + "=?").join(", ") + " WHERE id=?", ...cols.map(c => p[c]), w.id);
    K().append("value.wallet.moved", { namespace: "value", subject: w.id, actor: String(actor || ""), payload: { from: w.status, to, reason: String(reason) } });
    return present(walletRow(w.id));
  });
}

/* ============================== balances ============================== */
function accountOf(walletId) { return get("SELECT * FROM ledger_accounts WHERE wallet_id=?", String(walletId)); }
function systemAccount(tid, key, unit) {
  if (!SEED.systemAccounts.some(a => a.key === key)) throw fail("Unknown system account: " + key);
  let a = get("SELECT * FROM ledger_accounts WHERE tenant_id=? AND system_key=? AND unit=?", Number(tid), key, unit);
  if (!a) { run("INSERT INTO ledger_accounts(tenant_id,system_key,unit) VALUES(?,?,?)", Number(tid), key, unit); a = get("SELECT * FROM ledger_accounts WHERE tenant_id=? AND system_key=? AND unit=?", Number(tid), key, unit); }
  return a;
}
function balanceMinor(walletId) {
  const a = accountOf(walletId);
  const posted = a ? Number(get("SELECT COALESCE(SUM(amount),0) s FROM ledger_postings WHERE account_id=?", a.id).s) : 0;
  const keeps = states.tagged(H, "keeps");
  const reserved = keeps.length ? Number(get(`SELECT COALESCE(SUM(amount-captured),0) s FROM wallet_holds WHERE wallet_id=? AND status IN (${keeps.map(() => "?").join(",")})`, String(walletId), ...keeps).s) : 0;
  return { posted, reserved, available: posted - reserved };
}
function balances(tid, owner, id) { return present(own(tid, owner, id)); }

/* ============================== journals ============================== */
const hashOf = o => crypto.createHash("sha256").update(JSON.stringify(o)).digest("hex");
/* the same key returns the first outcome; the same key for a different request is refused */
function prior(tid, idem, request) {
  if (!idem) return null;
  const j = get("SELECT * FROM ledger_journals WHERE tenant_id=? AND idem_key=?", Number(tid), String(idem));
  if (!j) return null;
  if (j.request_hash !== hashOf(request)) throw fail("This idempotency key was used for a different request", 409, "idempotency_mismatch");
  return journal(j.id);
}
function journal(id) {
  const j = get("SELECT * FROM ledger_journals WHERE id=?", Number(id));
  if (!j) return null;
  return { ...j, postings: all("SELECT p.*, a.wallet_id, a.system_key FROM ledger_postings p JOIN ledger_accounts a ON a.id=p.account_id WHERE p.journal_id=? ORDER BY p.id", j.id) };
}
/* write a balanced journal: lines [{ account, amount }] in minor units of one or more units */
function write(tid, j, lines) {
  const sums = {};
  for (const l of lines) { if (!Number.isSafeInteger(l.amount) || l.amount === 0) throw fail("A posting is a whole, non-zero minor amount"); sums[l.unit] = (sums[l.unit] || 0) + l.amount; }
  if (Object.values(sums).some(s => s !== 0)) throw fail("A journal must balance in every unit", 500, "journal_unbalanced");
  const seq = K().append("value.journal.posted", { namespace: "value", subject: j.ref || null, actor: j.actor, payload: { tenant: Number(tid), op: j.op, ref: j.ref || "", lines: lines.map(l => [l.account, l.unit, l.amount]) } });
  const r = run("INSERT INTO ledger_journals(tenant_id,op,ref,idem_key,request_hash,actor,reason,reverses,event_seq) VALUES(?,?,?,?,?,?,?,?,?)",
    Number(tid), j.op, String(j.ref || ""), j.idem ? String(j.idem) : null, j.request_hash || "", String(j.actor || "system"), String(j.reason || ""), j.reverses || null, seq);
  for (const l of lines) run("INSERT INTO ledger_postings(journal_id,account_id,unit,amount) VALUES(?,?,?,?)", r.lastInsertRowid, l.account, l.unit, l.amount);
  return Number(r.lastInsertRowid);
}
/* the projection older readers use: the owner's default wallet in the store's money */
function project(w) {
  const d = defaultDefinition();
  if (!d || w.definition_key !== d.key || w.namespace !== d.namespace) return;
  const u = unitOf(w.unit);
  const posted = toMajor(balanceMinor(w.id).posted, u.decimals);
  run(`INSERT INTO wallets(tenant_id,owner,balance,updated_at) VALUES(?,?,?,datetime('now'))
       ON CONFLICT(tenant_id,owner) DO UPDATE SET balance=excluded.balance, updated_at=datetime('now')`, w.tenant_id, w.owner, posted);
}
/* the statement line older readers show */
function statementLine(w, op, minor, ref, channel, actor) {
  const u = unitOf(w.unit);
  run("INSERT INTO wallet_entries(tenant_id,owner,currency,kind,amount,balance_after,ref,channel,actor) VALUES(?,?,?,?,?,?,?,?,?)",
    w.tenant_id, w.owner, w.unit, op, toMajor(minor, u.decimals), toMajor(balanceMinor(w.id).posted, u.decimals), String(ref || ""), String(channel || ""), String(actor || "system"));
}
const canOperate = (w, op) => {
  if (!states.is(M, w.status, "operates") && !(states.is(M, w.status, "receives") && (opOf(op) || {}).direction === "in")) throw fail("This wallet is " + states.display(M, w.status).label.toLowerCase(), 409, "wallet_state");
  const d = definition(w.definition_key, w.definition_version, w.namespace);
  if (!d.spec.operations.includes(op)) throw fail(nameText(d.spec.name) + " does not allow " + ((opOf(op) || {}).name || op).toLowerCase(), 403, "operation_not_allowed");
  return d;
};
/* one operation on one wallet against its counter account: in adds, out takes (from available) */
function post(tid, input) {
  const i = input || {};
  const op = opOf(i.op);
  if (!op || op.direction === "between") throw fail("Unknown operation: " + i.op, 400, "operation_unknown");
  const w = own(tid, i.owner == null ? null : i.owner, i.wallet);
  const u = unitOf(w.unit);
  const minor = toMinor(i.amount, u.decimals);
  const dir = op.direction === "either" ? (minor < 0 ? "out" : "in") : op.direction;
  const abs = Math.abs(minor);
  if (!abs || (op.direction !== "either" && minor < 0)) throw fail("The amount must be positive", 400, "amount_invalid");
  if (op.needs_reason && !String(i.reason || "").trim()) throw fail("Say why", 400, "reason_required");
  const request = { op: op.key, wallet: w.id, amount: minor, ref: String(i.ref || "") };
  return tx(() => {
    const was = prior(tid, i.idem, request); if (was) return { journal: was, wallet: present(walletRow(w.id)), replayed: true };
    const d = canOperate(w, op.key);
    const b = balanceMinor(w.id);
    if (dir === "out" && b.available + toMinor(d.spec.policy.overdraft || 0, u.decimals) < abs) throw fail("Not enough available in this wallet", 402, "insufficient_available");
    if (dir === "in" && d.spec.policy.max_balance && b.posted + abs > toMinor(d.spec.policy.max_balance, u.decimals)) throw fail("This wallet may hold at most " + d.spec.policy.max_balance, 409, "max_balance");
    const acc = accountOf(w.id), counter = systemAccount(tid, op.counter, w.unit);
    const signed = dir === "out" ? -abs : abs;
    const id = write(tid, { op: op.key, ref: i.ref, idem: i.idem, request_hash: hashOf(request), actor: i.actor, reason: i.reason },
      [{ account: acc.id, unit: w.unit, amount: signed }, { account: counter.id, unit: w.unit, amount: -signed }]);
    project(w); statementLine(w, op.key, signed, i.ref, i.channel, i.actor);
    return { journal: journal(id), wallet: present(walletRow(w.id)) };
  });
}
/* between two wallets of one unit, each allowing transfers */
function transfer(tid, input) {
  const i = input || {};
  const a = own(tid, i.owner == null ? null : i.owner, i.from), b = own(tid, i.to_owner === undefined ? (i.owner == null ? null : i.owner) : i.to_owner, i.to);
  if (a.id === b.id) throw fail("Choose two different wallets");
  if (a.unit !== b.unit) throw fail("These wallets hold different units — that is a conversion, not a transfer", 400, "unit_mismatch");
  const u = unitOf(a.unit);
  const minor = toMinor(i.amount, u.decimals);
  if (!(minor > 0)) throw fail("The amount must be positive", 400, "amount_invalid");
  const request = { op: "transfer", from: a.id, to: b.id, amount: minor, ref: String(i.ref || "") };
  return tx(() => {
    const was = prior(tid, i.idem, request); if (was) return { journal: was, replayed: true };
    const da = canOperate(a, "transfer"); canOperate(b, "transfer");
    if (balanceMinor(a.id).available + toMinor(da.spec.policy.overdraft || 0, u.decimals) < minor) throw fail("Not enough available in this wallet", 402, "insufficient_available");
    const id = write(tid, { op: "transfer", ref: i.ref, idem: i.idem, request_hash: hashOf(request), actor: i.actor },
      [{ account: accountOf(a.id).id, unit: a.unit, amount: -minor }, { account: accountOf(b.id).id, unit: b.unit, amount: minor }]);
    project(a); project(b); statementLine(a, "transfer", -minor, i.ref, i.channel, i.actor); statementLine(b, "transfer", minor, i.ref, i.channel, i.actor);
    return { journal: journal(id), from: present(walletRow(a.id)), to: present(walletRow(b.id)) };
  });
}
/* a correction: the mirror of a journal, linked to it; a journal is reversed at most once */
function reverse(tid, journalId, actor, reason, idem) {
  if (!String(reason || "").trim()) throw fail("Say why", 400, "reason_required");
  const j = journal(journalId);
  if (!j || j.tenant_id !== Number(tid)) throw fail("Journal not found", 404, "journal_unknown");
  if (j.reverses) throw fail("A reversal is not itself reversed — post a new operation", 409, "journal_is_reversal");
  return tx(() => {
    if (get("SELECT id FROM ledger_journals WHERE reverses=?", j.id)) throw fail("This journal was already reversed", 409, "journal_reversed");
    const id = write(tid, { op: j.op, ref: j.ref, idem, request_hash: hashOf({ reverse: j.id }), actor, reason, reverses: j.id },
      j.postings.map(p => ({ account: p.account_id, unit: p.unit, amount: -p.amount })));
    for (const p of j.postings) if (p.wallet_id) { const w = walletRow(p.wallet_id); project(w); statementLine(w, j.op, -p.amount, "reversal:" + j.id, "", actor); }
    return journal(id);
  });
}
function statement(tid, owner, id, limit) {
  const w = own(tid, owner, id);
  const u = unitOf(w.unit);
  return all(`SELECT j.id, j.op, j.ref, j.reverses, j.created_at, p.amount FROM ledger_postings p JOIN ledger_journals j ON j.id=p.journal_id
    WHERE p.account_id=? ORDER BY j.id DESC LIMIT ?`, accountOf(w.id).id, Math.min(500, Number(limit) || 100))
    .map(r => ({ ...r, amount: toMajor(r.amount, u.decimals), op_name: (opOf(r.op) || {}).name || r.op }));
}

/* ============================== holds ============================== */
function hold(tid, input) {
  const i = input || {};
  const w = own(tid, i.owner == null ? null : i.owner, i.wallet);
  const u = unitOf(w.unit);
  const minor = toMinor(i.amount, u.decimals);
  if (!(minor > 0)) throw fail("The amount must be positive", 400, "amount_invalid");
  return tx(() => {
    if (i.idem) { const h = get("SELECT * FROM wallet_holds WHERE wallet_id=? AND idem_key=?", w.id, String(i.idem)); if (h) { if (h.amount !== minor) throw fail("This idempotency key was used for a different hold", 409, "idempotency_mismatch"); return presentHold(h); } }
    const d = canOperate(w, "hold");
    /* a hold whose caller names no expiry lapses after the definition's hold_minutes */
    const expires = i.expires_at || (d.spec.policy.hold_minutes ? new Date(Date.now() + d.spec.policy.hold_minutes * 60000).toISOString().slice(0, 19).replace("T", " ") : null);
    if (balanceMinor(w.id).available + toMinor(d.spec.policy.overdraft || 0, u.decimals) < minor) throw fail("Not enough available in this wallet", 402, "insufficient_available");
    const r = run("INSERT INTO wallet_holds(wallet_id,amount,purpose,ref,idem_key,expires_at,status) VALUES(?,?,?,?,?,?,?)",
      w.id, minor, String(i.purpose || "").slice(0, 120), String(i.ref || ""), i.idem ? String(i.idem) : null, expires, states.initial(H));
    K().append("value.hold.created", { namespace: "value", subject: w.id, actor: String(i.actor || ""), payload: { hold: Number(r.lastInsertRowid), amount: minor } });
    return presentHold(get("SELECT * FROM wallet_holds WHERE id=?", r.lastInsertRowid));
  });
}
function presentHold(h) {
  const w = walletRow(h.wallet_id), u = unitOf(w.unit);
  return { ...h, amount: toMajor(h.amount, u.decimals), captured: toMajor(h.captured, u.decimals), remaining: toMajor(h.amount - h.captured, u.decimals), state: states.display(H, h.status), keeps: states.is(H, h.status, "keeps") };
}
function holdMove(h, action, patch) {
  const to = states.actionTarget(H, action);
  if (!to || !states.can(H, h.status, to)) throw fail("That cannot be done to this hold now", 409, "hold_state");
  const mv = states.apply(H, { tenantId: 0, from: h.status, to, row: h });
  const p = { ...mv.patch, ...(patch || {}) };
  const cols = Object.keys(p);
  run("UPDATE wallet_holds SET " + cols.map(c => c + "=?").join(", ") + " WHERE id=?", ...cols.map(c => p[c]), h.id);
  return get("SELECT * FROM wallet_holds WHERE id=?", h.id);
}
function holdOf(tid, owner, id) {
  const h = get("SELECT * FROM wallet_holds WHERE id=?", Number(id));
  if (!h) throw fail("Hold not found", 404, "hold_unknown");
  own(tid, owner, h.wallet_id);
  return h;
}
/* capture what is spent (at most what remains): posted as a spend; the hold is captured in full or in part */
function capture(tid, owner, id, amount, ref, actor) {
  return tx(() => {
    const h = holdOf(tid, owner, id);
    if (!states.is(H, h.status, "keeps")) throw fail("This hold no longer keeps anything", 409, "hold_state");
    const w = walletRow(h.wallet_id), u = unitOf(w.unit);
    const minor = amount == null ? h.amount - h.captured : toMinor(amount, u.decimals);
    if (!(minor > 0) || minor > h.amount - h.captured) throw fail("A capture is more than nothing and no more than the hold keeps", 400, "capture_range");
    const captured = h.captured + minor;
    /* the hold stops keeping the captured part before the spend is posted from available */
    const after = holdMove(h, captured === h.amount ? "capture" : "capture_part", { captured });
    const out = post(tid, { op: "redeem", wallet: w.id, amount: toMajor(minor, u.decimals), ref: ref || h.ref, idem: "hold:" + h.id + ":" + captured, actor });
    return { hold: presentHold(after), journal: out.journal, wallet: out.wallet };
  });
}
function release(tid, owner, id, actor) {
  return tx(() => { const h = holdOf(tid, owner, id); return presentHold(holdMove(h, "release")); });
}
/* holds past their expiry stop keeping */
function sweepAll() {
  let n = 0;
  for (const h of all("SELECT * FROM wallet_holds WHERE expires_at IS NOT NULL AND expires_at<?", nowSql())) {
    if (!states.is(H, h.status, "keeps")) continue;
    try { holdMove(h, "expire"); n++; } catch (e) { console.error("hold sweep:", e.message); }
  }
  return n;
}
function holds(tid, owner, id) { const w = own(tid, owner, id); return all("SELECT * FROM wallet_holds WHERE wallet_id=? ORDER BY id DESC LIMIT 200", w.id).map(presentHold); }

/* ============================== the older single-balance callers ============================== */
/* the owner's default wallet in a unit: the default definition for money, else the first
   definition holding the unit's class that allows the operation — opened on first use */
function walletFor(tid, owner, unit, op) {
  const u = unitOf(unit || require("./defaults.js").currency(tid));
  const cls = u.class;
  const defs = definitions();
  const d = [defaultDefinition(), ...defs].find(x => x && x.spec.classes.includes(cls) && (!op || x.spec.operations.includes(op)));
  if (!d) throw fail("No wallet definition holds " + u.name, 409, "definition_missing");
  const w = get("SELECT * FROM wallet_instances WHERE tenant_id=? AND owner=? AND namespace=? AND definition_key=? AND unit=? ORDER BY created_at, id LIMIT 1", Number(tid), String(owner), d.namespace, d.key, u.code);
  return w || walletRow(open(tid, owner, { definition: d.key, namespace: d.namespace, unit: u.code }, "system").id);
}
/* verification: every journal balances in every unit, and the event chain holds */
function verify(tid) {
  const bad = all(`SELECT j.id FROM ledger_journals j JOIN ledger_postings p ON p.journal_id=j.id WHERE j.tenant_id=? GROUP BY j.id, p.unit HAVING SUM(p.amount)<>0`, Number(tid)).map(r => r.id);
  return { journals: get("SELECT COUNT(*) n FROM ledger_journals WHERE tenant_id=?", Number(tid)).n, unbalanced: bad, chain: K().verifyEvents() };
}
/* the single-balance wallets become default wallets, each with an opening journal (once) */
function migrate() {
  let n = 0;
  for (const r of all("SELECT * FROM wallets WHERE balance>0")) {
    try {
      const idem = "opening:" + r.owner;
      if (get("SELECT id FROM ledger_journals WHERE tenant_id=? AND idem_key=?", r.tenant_id, idem)) continue;
      const w = walletFor(r.tenant_id, r.owner, null, "opening");
      const u = unitOf(w.unit);
      post(r.tenant_id, { op: "opening", wallet: w.id, amount: Number(r.balance).toFixed(u.decimals), idem, actor: "migration" });
      n++;
    } catch (e) { console.error("wallet migration:", r.owner, e.message); }
  }
  return n;
}
function vocabulary() {
  return { operations: ops(), systemAccounts: SEED.systemAccounts, classes: classesOf(),
    walletActions: Object.entries(states.actions(M)).map(([verb, to]) => ({ verb, to, label: states.display(M, to).label })),
    holdActions: Object.entries(states.actions(H)).map(([verb, to]) => ({ verb, to, label: states.display(H, to).label })) };
}

/* the operation a signed movement posts under when its caller names none: the one the seed marks */
const defaultOp = dir => (ops().find(o => o[dir === "in" ? "default_in" : "default_out"]) || {}).key;

module.exports = { defaultOp, seed, rebind, migrate, define, definition, definitions, open, rename, names, walletsOf, move, balances, post, transfer, reverse, statement,
  hold, capture, release, holds, sweepAll, walletFor, verify, journal, vocabulary, toMinor, toMajor, unitOf };
