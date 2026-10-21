/* LUXORA Platform — the Universal Wallet, on the kernel.

   Everything a wallet is comes from the kernel (lib/seed/wallet.json declares it):
     ENTITY        a wallet is a node of the wallet kind in its store's namespace; a definition is a
                   node of the definition kind; a holder is a node of the holder kind
     SUB-ENTITY    a definition sits under the definition it refines in the definitions hierarchy,
                   to any depth, and a wallet sits under its definition — so a wallet is a sub-…-
                   sub-entity of every definition above it
     CONTEXT       every setting (value classes, operations, overdraft, maximum balance, wallets
                   per owner, hold expiry, the default definition) is a kernel setting assigned at a
                   definition node — or at a wallet, or across a namespace — and resolved from the
                   wallet up through its definitions, the store's namespace before the platform's.
                   A definition states only what differs from the one above it
     TEMPORAL      names, aliases, state and settings are versions with valid and recorded time:
                   a rename keeps every past name; a setting answers as of any moment, as believed
                   at any moment, and each journal records the event it was posted at
     RELATIONSHIP  the holding hierarchy places a holder's wallets under it; the holder's identity
                   is a sealed (encrypted) attribute, found by a keyed blind index, never stored
                   readable
     REGISTRY      operations, system accounts, machines and value classes are declared data

   Value moves only as JOURNALS: two or more postings in exact minor units that sum to zero per
   unit, against a wallet's account and a system account. A journal is one event in the kernel's
   hash-chained log; the ledger tables are its index (posted rows cannot be updated or deleted)
   and verify() replays the log against them. Corrections are linked reversals, once. Every
   mutating call takes an idempotency key: the same key and request return the first outcome, a
   different request is refused. Balances are projections: posted, reserved by holds, available.
   HOLDS keep value until spent in full or in part, released or expired (`wallet_hold` machine);
   a wallet's life is the `wallet` machine. The single-balance `wallets` table is the projection
   older readers use (the default wallet's posted balance), written only here. Domain: Value. */
"use strict";

const crypto = require("crypto");
const { run, get, all } = require("./db.js");
const states = require("./states.js");
const SEED = require("./seed/wallet.json");

const K = () => require("./kernel.js");
const C = () => require("./kernel-context.js");
const tx = fn => K().internal.tx(fn);
const fail = (msg, status, code) => Object.assign(new Error(msg), { status: status || 400, code: code || "" });
const nowSql = () => new Date().toISOString().slice(0, 19).replace("T", " ");
const reg = () => require("./registry.js");
const KEY = SEED.keys, SET = SEED.settingKeys, EVT = SEED.events;
const M = SEED.machines.wallet, H = SEED.machines.hold;
const PLATFORM = SEED.namespace;
const tenantNs = tid => KEY.tenantNamespace + ":" + Number(tid);
/* the language a name is written in when the caller names none: the platform's source language */
const sourceLang = () => require("./expression.js").SEED.sourceLanguage;
const nameText = (n, lang) => K().text(n, lang || sourceLang()) || "";

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

/* ============================== the kernel declarations ============================== */
const ops = () => SEED.operations;
const opOf = key => ops().find(o => o.key === key) || null;
const classesOf = () => reg().list(require("./seed/value.json").classList).map(x => (typeof x === "string" ? x : x.key));
function declare() {
  const k = K(), c = C();
  c.ensureTables();
  for (const d of SEED.kinds) {
    const cur = k.kindOf(d.kind, PLATFORM);
    const want = JSON.stringify({ a: d.attributes.map(a => [a.key, a.type, !!a.required, !!a.sensitive]), p: d.parents || null, s: d.schemes || [] });
    const have = cur ? JSON.stringify({ a: cur.attributes.filter(a => d.attributes.some(x => x.key === a.key)).map(a => [a.key, a.type, !!a.required, !!a.sensitive]), p: d.parents ? cur.parents : null, s: d.schemes ? cur.schemes : [] }) : "";
    if (want !== have) k.defineKind({ ...d, namespace: PLATFORM }, "wallet.seed");
  }
  for (const h of SEED.hierarchies) if (!k.hierarchyOf(h.hierarchy, PLATFORM)) k.defineHierarchy({ ...h, namespace: PLATFORM }, "wallet.seed");
  for (const s of SEED.settings) if (!c.settingOf(s.name, PLATFORM)) c.declareSetting({ ...s, namespace: PLATFORM }, "wallet.seed");
  for (const [name, value] of Object.entries(SEED.namespaceSettings)) if (c.assignedAt(name, { namespace: PLATFORM }) === undefined) c.assign(name, value, { namespace: PLATFORM }, "wallet.seed");
}

/* ============================== settings, resolved by context ============================== */
/* a setting at a node: from that node up the definitions hierarchy, the store's namespace first */
function setting(name, node, tid, o) {
  const r = C().resolve(SET[name] || name, { context: { [KEY.definitions]: node }, namespaces: tid != null ? [tenantNs(tid), PLATFORM] : [PLATFORM], at: o && o.at, recorded: o && o.recorded });
  return r.resolved ? r.value : undefined;
}
/* every setting at a node, as one spec */
function spec(node, tid, o) {
  const v = n => setting(n, node, tid, o);
  return { openable: !!v("openable"), classes: v("classes") || [], operations: v("operations") || [],
    policy: { overdraft: Number(v("overdraft")) || 0, max_balance: Number(v("max_balance")) || 0, max_per_owner: Number(v("max_per_owner")) || 0, hold_minutes: Number(v("hold_minutes")) || 0 } };
}
/* the store's default definition (a namespace setting: a store may choose its own) */
function defaultKey(tid) {
  const r = C().resolve(SET.default_definition, { namespaces: tid != null ? [tenantNs(tid), PLATFORM] : [PLATFORM] });
  return r.resolved ? r.value : undefined;
}

/* ============================== definitions ============================== */
const defNode = key => K().resolveIdentifier(KEY.definitionScheme, String(key || ""));
function definitionAt(uid, tid) {
  if (!uid) return null;
  const a = K().attributes(uid);
  const key = K().identifiers(uid)[KEY.definitionScheme] || uid;
  const up = K().parents(KEY.definitions, uid);
  const parentKey = up.length ? K().identifiers(up[0])[KEY.definitionScheme] || null : null;
  return { uid, key, parent: parentKey, spec: { name: a.name, aliases: a.aliases || {}, ...spec(uid, tid), default: key === defaultKey(tid) } };
}
function definition(key, tid) { return definitionAt(defNode(key), tid); }
function definitions(tid) {
  return K().nodes(KEY.definitionKind, PLATFORM).map(n => definitionAt(typeof n === "string" ? n : n.uid, tid)).filter(Boolean);
}
/* declare a definition: a node under the one it refines; only the settings it states are assigned
   (the rest it inherits). Unchanged values write nothing; a changed one is a new version in time.
   o.namespace: a store's own assignments over the platform's (its configuration of a definition) */
function define(input, actor, o) {
  declare();
  const i = input || {};
  const space = (o && o.namespace) || PLATFORM;
  const key = String(i.key || "");
  if (!/^[a-z][a-z0-9_.-]{0,63}$/.test(key)) throw fail("A definition needs a key: lowercase letters, digits, _ . -");
  const legacy = { ...(i.policy ? { overdraft: i.policy.overdraft, max_balance: i.policy.max_balance, max_per_owner: i.policy.max_per_owner != null ? i.policy.max_per_owner : i.policy.max_wallets_per_owner, hold_minutes: i.policy.hold_minutes } : {}), ...(i.classes ? { classes: i.classes } : {}), ...(i.operations ? { operations: i.operations } : {}) };
  const settings = Object.fromEntries(Object.entries({ ...legacy, ...(i.settings || {}) }).filter(([, v]) => v !== undefined));
  for (const k of Object.keys(settings)) if (!SET[k] || k === "default_definition") throw fail("Unknown setting: " + k);
  if (settings.classes) { const known = classesOf(); if (settings.classes.some(c => !known.includes(c))) throw fail("A definition holds value classes Value declares: " + known.join(", ")); }
  if (settings.operations) { const allowed = [...ops().map(x => x.key), "hold"]; const bad = settings.operations.filter(x => !allowed.includes(x)); if (bad.length) throw fail("Unknown operation: " + bad.join(", ")); }
  return tx(() => {
    let uid = defNode(key);
    if (space === PLATFORM) {
      const names = i.name && typeof i.name === "object" ? i.name : null;
      if (!uid) {
        if (!names || !Object.values(names).some(v => String(v || "").trim())) throw fail("A definition needs a name");
        const parent = i.parent ? defNode(i.parent) : null;
        if (i.parent && !parent) throw fail("Unknown definition to refine: " + i.parent, 404, "definition_unknown");
        uid = K().createNode(KEY.definitionKind, { namespace: PLATFORM, attributes: { name: names, ...(i.aliases ? { aliases: i.aliases } : {}) }, identifiers: { [KEY.definitionScheme]: key } }, actor);
        K().place(KEY.definitions, uid, parent, { namespace: PLATFORM }, actor);
      } else {
        const a = K().attributes(uid), patch = {};
        if (names && JSON.stringify(a.name) !== JSON.stringify(names)) patch.name = names;
        if (i.aliases && JSON.stringify(a.aliases || {}) !== JSON.stringify(i.aliases)) patch.aliases = i.aliases;
        if (Object.keys(patch).length) K().record(uid, patch, {}, actor);
      }
    } else if (!uid) throw fail("Unknown definition: " + key, 404, "definition_unknown");
    for (const [k, v] of Object.entries(settings)) {
      const have = C().assignedAt(SET[k], { namespace: space, scope: uid });
      if (JSON.stringify(have) !== JSON.stringify(v)) C().assign(SET[k], v, { namespace: space, scope: uid }, actor);
    }
    return definitionAt(uid, space === PLATFORM ? null : Number(String(space).split(":")[1]));
  });
}
/* the store chooses its default definition (a setting across its namespace) */
function chooseDefault(tid, key, actor) {
  if (!defNode(key)) throw fail("Unknown definition: " + key, 404, "definition_unknown");
  return C().assign(SET.default_definition, String(key), { namespace: tenantNs(tid) }, actor);
}
function seed() {
  declare();
  for (const d of SEED.definitions) define(d, "wallet.seed");
}

/* ============================== holders ============================== */
/* a holder is found by a blind index of the store and owner; the owner itself is sealed */
const holderKey = (tid, owner) => require("./security.js").blindIndex(String(owner), tenantNs(tid) + "/" + KEY.holderKind);
function holderOf(tid, owner, create, actor) {
  const ix = holderKey(tid, owner);
  const uid = K().resolveIdentifier(KEY.holderScheme, ix);
  if (uid || !create) return uid;
  const h = K().createNode(KEY.holderKind, { namespace: tenantNs(tid), attributes: { owner: String(owner), tenant: Number(tid) }, identifiers: { [KEY.holderScheme]: ix } }, actor);
  K().place(KEY.holding, h, null, { namespace: tenantNs(tid) }, actor);
  return h;
}

/* ============================== wallets ============================== */
const isWallet = uid => { try { return K().internal.kindForNode(uid).k.lineage.includes(KEY.walletKind); } catch (e) { return false; } };
function walletRow(id) {
  if (!id || !isWallet(String(id))) return null;
  const a = K().attributes(String(id));
  const def = K().parents(KEY.definitions, String(id))[0] || null;
  return { id: String(id), tenant_id: Number(a.tenant), owner: a.owner, unit: a.unit, status: a.status, name: a.name, aliases: a.aliases || {}, closed_at: a.closed_at || null, definition: def };
}
function present(w, lang) {
  if (!w) return null;
  const d = definitionAt(w.definition, w.tenant_id) || { key: null, spec: {} };
  const u = unitOf(w.unit);
  const b = balanceMinor(w.id);
  return { id: w.id, owner: w.owner, unit: w.unit, decimals: u.decimals, name: nameText(w.name, lang),
    aliases: Object.entries(w.aliases || {}).flatMap(([lg, xs]) => [].concat(xs).map(name => ({ lang: lg, name }))),
    definition: { key: d.key, name: d.spec.name }, state: states.display(M, w.status),
    posted: toMajor(b.posted, u.decimals), reserved: toMajor(b.reserved, u.decimals), available: toMajor(b.available, u.decimals) };
}
/* a wallet the caller owns (staff pass owner null to act on any wallet of the store) */
function own(tid, owner, id) {
  const w = walletRow(id);
  if (!w || w.tenant_id !== Number(tid) || (owner != null && w.owner !== String(owner))) throw fail("Wallet not found", 404, "wallet_unknown");
  return w;
}
function walletIdsOf(tid, owner) {
  const h = holderOf(tid, owner, false);
  return h ? K().children(KEY.holding, h, { namespace: tenantNs(tid) }).filter(isWallet) : [];
}
function walletsOf(tid, owner, lang) { return walletIdsOf(tid, owner).map(walletRow).filter(Boolean).map(w => present(w, lang)); }
/* open a wallet of a definition in a unit, named as the owner likes */
function open(tid, owner, input, actor) {
  const i = input || {};
  const key = i.definition || defaultKey(tid);
  const d = definition(key, tid);
  if (!d) throw fail("Unknown wallet definition: " + key, 404, "definition_unknown");
  if (!d.spec.openable) throw fail(nameText(d.spec.name) + " is not opened directly — choose one of the definitions under it", 400, "definition_abstract");
  const u = unitOf(i.unit || require("./defaults.js").currency(tid));
  if (!d.spec.classes.includes(u.class)) throw fail(nameText(d.spec.name) + " does not hold " + u.name, 400, "unit_incompatible");
  const cap = d.spec.policy.max_per_owner;
  const closed = states.first(M, "closed");
  if (cap && walletIdsOf(tid, owner).map(walletRow).filter(w => w.definition === d.uid && w.unit === u.code && w.status !== closed).length >= cap)
    throw fail("No more of these may be opened in " + u.name + ": " + nameText(d.spec.name), 409, "wallet_cap");
  return tx(() => {
    const holder = holderOf(tid, owner, true, actor || owner);
    const name = String(i.name || "").trim().slice(0, 80);
    const lang = String(i.lang || sourceLang());
    const id = K().createNode(KEY.walletKind, { namespace: tenantNs(tid), attributes: { name: name ? { [lang]: name } : d.spec.name, unit: u.code, status: states.initial(M), tenant: Number(tid), owner: String(owner) } }, String(actor || owner));
    K().place(KEY.definitions, id, d.uid, { namespace: tenantNs(tid) }, String(actor || owner));
    K().place(KEY.holding, id, holder, { namespace: tenantNs(tid) }, String(actor || owner));
    run("INSERT INTO ledger_accounts(tenant_id,wallet_id,unit) VALUES(?,?,?)", Number(tid), id, u.code);
    K().append(EVT.opened, { namespace: tenantNs(tid), subject: id, actor: String(actor || owner), payload: { definition: d.key, unit: u.code } });
    return present(walletRow(id), lang);
  });
}
/* rename (or set an alias): a new version of the attribute — identity, balances and history stay */
function rename(tid, owner, id, input, actor) {
  const w = own(tid, owner, id);
  const i = input || {};
  const name = String(i.name || "").trim().slice(0, 80);
  if (!name) throw fail("Give the wallet a name");
  const lang = String(i.lang || sourceLang());
  return tx(() => {
    if (i.alias) K().record(w.id, { aliases: { ...(w.aliases || {}), [lang]: [...new Set([].concat((w.aliases || {})[lang] || [], name))] } }, {}, String(actor || owner));
    else K().record(w.id, { name: { ...(w.name || {}), [lang]: name } }, {}, String(actor || owner));
    K().append(EVT.renamed, { namespace: tenantNs(tid), subject: w.id, actor: String(actor || owner), payload: { lang, alias: !!i.alias } });
    return present(walletRow(w.id), lang);
  });
}
/* every name a wallet has had, with when it held */
function names(id) {
  if (!isWallet(String(id))) return [];
  const out = [];
  for (const v of K().history(String(id))) for (const [lang, name] of Object.entries((v.attributes || {}).name || {}))
    if (!out.some(x => x.lang === lang && x.name === name)) out.push({ lang, name, alias: 0, valid_from: v.validFrom, recorded: v.recordedFrom });
  return out;
}
/* a wallet's life: staff restrict, suspend, reactivate or close it — moves are the machine's */
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
    K().record(w.id, { status: to, ...(mv.patch.closed_at ? { closed_at: String(mv.patch.closed_at) } : {}) }, {}, String(actor || ""));
    K().append(EVT.moved, { namespace: tenantNs(tid), subject: w.id, actor: String(actor || ""), payload: { from: w.status, to, reason: String(reason) } });
    return present(walletRow(w.id));
  });
}
/* a wallet's own spec: its settings resolved from it up through its definitions */
const walletSpec = (w, o) => spec(w.id, w.tenant_id, o);

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
function balances(tid, owner, id, lang) { return present(own(tid, owner, id), lang); }
/* the posted balance an owner holds in a unit, over all their wallets of it */
function balanceOf(tid, owner, unit) {
  const code = String(unit).toUpperCase(), u = unitOf(code);
  return toMajor(walletIdsOf(tid, owner).map(walletRow).filter(w => w.unit === code).reduce((s, w) => s + balanceMinor(w.id).posted, 0), u.decimals);
}

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
/* write a balanced journal: lines [{ account, amount }] in minor units of one or more units; the
   event is written first, so the hash-chained log is the record and the tables its index */
function write(tid, j, lines) {
  const sums = {};
  for (const l of lines) { if (!Number.isSafeInteger(l.amount) || l.amount === 0) throw fail("A posting is a whole, non-zero minor amount"); sums[l.unit] = (sums[l.unit] || 0) + l.amount; }
  if (Object.values(sums).some(s => s !== 0)) throw fail("A journal must balance in every unit", 500, "journal_unbalanced");
  const seq = K().append(EVT.journal, { namespace: tenantNs(tid), subject: j.ref || null, actor: j.actor, payload: { tenant: Number(tid), op: j.op, ref: j.ref || "", reverses: j.reverses || null, lines: lines.map(l => [l.account, l.unit, l.amount]) } });
  const r = run("INSERT INTO ledger_journals(tenant_id,op,ref,idem_key,request_hash,actor,reason,reverses,event_seq) VALUES(?,?,?,?,?,?,?,?,?)",
    Number(tid), j.op, String(j.ref || ""), j.idem ? String(j.idem) : null, j.request_hash || "", String(j.actor || "system"), String(j.reason || ""), j.reverses || null, seq);
  for (const l of lines) run("INSERT INTO ledger_postings(journal_id,account_id,unit,amount) VALUES(?,?,?,?)", r.lastInsertRowid, l.account, l.unit, l.amount);
  return Number(r.lastInsertRowid);
}
/* the projection older readers use: the owner's default wallet in the store's money */
function project(w) {
  if (!w.definition || w.definition !== defNode(defaultKey(w.tenant_id))) return;
  const u = unitOf(w.unit);
  run(`INSERT INTO wallets(tenant_id,owner,balance,updated_at) VALUES(?,?,?,datetime('now'))
       ON CONFLICT(tenant_id,owner) DO UPDATE SET balance=excluded.balance, updated_at=datetime('now')`, w.tenant_id, w.owner, toMajor(balanceMinor(w.id).posted, u.decimals));
}
/* the statement line older readers show */
function statementLine(w, op, minor, ref, channel, actor) {
  const u = unitOf(w.unit);
  run("INSERT INTO wallet_entries(tenant_id,owner,currency,kind,amount,balance_after,ref,channel,actor) VALUES(?,?,?,?,?,?,?,?,?)",
    w.tenant_id, w.owner, w.unit, op, toMajor(minor, u.decimals), toMajor(balanceMinor(w.id).posted, u.decimals), String(ref || ""), String(channel || ""), String(actor || "system"));
}
function canOperate(w, op) {
  if (!states.is(M, w.status, "operates") && !(states.is(M, w.status, "receives") && (opOf(op) || {}).direction === "in")) throw fail("This wallet is " + states.display(M, w.status).label.toLowerCase(), 409, "wallet_state");
  const s = walletSpec(w);
  if (!s.operations.includes(op)) throw fail(nameText(w.name) + " does not allow " + ((opOf(op) || {}).name || op).toLowerCase(), 403, "operation_not_allowed");
  return s;
}
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
    const s = canOperate(w, op.key);
    const b = balanceMinor(w.id);
    if (dir === "out" && b.available + toMinor(s.policy.overdraft, u.decimals) < abs) throw fail("Not enough available in this wallet", 402, "insufficient_available");
    if (dir === "in" && s.policy.max_balance && b.posted + abs > toMinor(s.policy.max_balance, u.decimals)) throw fail("This wallet may hold at most " + s.policy.max_balance, 409, "max_balance");
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
    const sa = canOperate(a, "transfer"), sb = canOperate(b, "transfer");
    if (balanceMinor(a.id).available + toMinor(sa.policy.overdraft, u.decimals) < minor) throw fail("Not enough available in this wallet", 402, "insufficient_available");
    /* what the receiving wallet's resolved maximum allows */
    if (sb.policy.max_balance && balanceMinor(b.id).posted + minor > toMinor(sb.policy.max_balance, u.decimals)) throw fail("That wallet may hold at most " + sb.policy.max_balance, 409, "max_balance");
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
    const s = canOperate(w, "hold");
    /* a hold whose caller names no expiry lapses after the wallet's hold_minutes */
    const expires = i.expires_at || (s.policy.hold_minutes ? new Date(Date.now() + s.policy.hold_minutes * 60000).toISOString().slice(0, 19).replace("T", " ") : null);
    if (balanceMinor(w.id).available + toMinor(s.policy.overdraft, u.decimals) < minor) throw fail("Not enough available in this wallet", 402, "insufficient_available");
    const r = run("INSERT INTO wallet_holds(wallet_id,amount,purpose,ref,idem_key,expires_at,status) VALUES(?,?,?,?,?,?,?)",
      w.id, minor, String(i.purpose || "").slice(0, 120), String(i.ref || ""), i.idem ? String(i.idem) : null, expires, states.initial(H));
    K().append(EVT.hold, { namespace: tenantNs(tid), subject: w.id, actor: String(i.actor || ""), payload: { hold: Number(r.lastInsertRowid), to: states.initial(H), amount: minor, expires } });
    return presentHold(get("SELECT * FROM wallet_holds WHERE id=?", r.lastInsertRowid));
  });
}
function presentHold(h) {
  const w = walletRow(h.wallet_id), u = unitOf(w.unit);
  return { ...h, amount: toMajor(h.amount, u.decimals), captured: toMajor(h.captured, u.decimals), remaining: toMajor(h.amount - h.captured, u.decimals), state: states.display(H, h.status), keeps: states.is(H, h.status, "keeps") };
}
/* every move of a hold is an event before it is a row */
function holdMove(h, action, patch, actor) {
  const to = states.actionTarget(H, action);
  if (!to || !states.can(H, h.status, to)) throw fail("That cannot be done to this hold now", 409, "hold_state");
  const w = walletRow(h.wallet_id);
  const mv = states.apply(H, { tenantId: w.tenant_id, from: h.status, to, row: h });
  const p = { ...mv.patch, ...(patch || {}) };
  K().append(EVT.hold, { namespace: tenantNs(w.tenant_id), subject: h.wallet_id, actor: String(actor || ""), payload: { hold: h.id, from: h.status, to, ...(patch || {}) } });
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
    const after = holdMove(h, captured === h.amount ? "capture" : "capture_part", { captured }, actor);
    const out = post(tid, { op: defaultOp("out"), wallet: w.id, amount: toMajor(minor, u.decimals), ref: ref || h.ref, idem: "hold:" + h.id + ":" + captured, actor });
    return { hold: presentHold(after), journal: out.journal, wallet: out.wallet };
  });
}
function release(tid, owner, id, actor) {
  return tx(() => { const h = holdOf(tid, owner, id); return presentHold(holdMove(h, "release", null, actor)); });
}
/* holds past their expiry stop keeping */
function sweepAll() {
  let n = 0;
  for (const h of all("SELECT * FROM wallet_holds WHERE expires_at IS NOT NULL AND expires_at<?", nowSql())) {
    if (!states.is(H, h.status, "keeps")) continue;
    try { holdMove(h, "expire", null, "sweep"); n++; } catch (e) { console.error("hold sweep:", e.message); }
  }
  return n;
}
function holds(tid, owner, id) { const w = own(tid, owner, id); return all("SELECT * FROM wallet_holds WHERE wallet_id=? ORDER BY id DESC LIMIT 200", w.id).map(presentHold); }

/* ============================== the older single-balance callers ============================== */
/* the owner's wallet in a unit for an operation: the store's default definition for it, else the
   first openable definition whose classes hold the unit and that allows the operation — opened
   on first use */
function walletFor(tid, owner, unit, op) {
  const u = unitOf(unit || require("./defaults.js").currency(tid));
  const fits = d => d && d.spec.openable && d.spec.classes.includes(u.class) && (!op || d.spec.operations.includes(op));
  const d = [definition(defaultKey(tid), tid), ...definitions(tid)].find(fits);
  if (!d) throw fail("No wallet definition holds " + u.name, 409, "definition_missing");
  const closed = states.first(M, "closed");
  const w = walletIdsOf(tid, owner).map(walletRow).find(x => x.definition === d.uid && x.unit === u.code && x.status !== closed);
  return w || walletRow(open(tid, owner, { definition: d.key, unit: u.code }, "system").id);
}
/* verification: every journal balances in every unit, the event chain holds, and the ledger
   index matches the log — each account's balance replayed from the journal events */
function verify(tid) {
  const bad = all(`SELECT j.id FROM ledger_journals j JOIN ledger_postings p ON p.journal_id=j.id WHERE j.tenant_id=? GROUP BY j.id, p.unit HAVING SUM(p.amount)<>0`, Number(tid)).map(r => r.id);
  const fromLog = {};
  for (const e of all("SELECT payload FROM k_events WHERE type=? AND namespace=?", EVT.journal, tenantNs(tid)))
    for (const [acc, , amt] of (JSON.parse(e.payload).lines || [])) fromLog[acc] = (fromLog[acc] || 0) + Number(amt);
  const fromIndex = Object.fromEntries(all("SELECT p.account_id a, SUM(p.amount) s FROM ledger_postings p JOIN ledger_journals j ON j.id=p.journal_id WHERE j.tenant_id=? GROUP BY p.account_id", Number(tid)).map(r => [r.a, Number(r.s)]));
  const drift = [...new Set([...Object.keys(fromLog), ...Object.keys(fromIndex)])].filter(a => (fromLog[a] || 0) !== (fromIndex[a] || 0)).map(Number);
  return { journals: get("SELECT COUNT(*) n FROM ledger_journals WHERE tenant_id=?", Number(tid)).n, unbalanced: bad, drift, chain: K().verifyEvents() };
}
/* the single-balance wallets become default wallets, each with an opening journal (once) */
function migrate() {
  let n = port();
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
/* wallets kept in the first slice's own tables move onto the kernel (once): a node per wallet,
   its account and holds re-pointed, the tables then dropped */
function port() {
  const has = t => { try { return !!get("SELECT name FROM sqlite_master WHERE type='table' AND name=?", t); } catch (e) { return false; } };
  if (!has("wallet_instances")) return 0;
  let n = 0;
  for (const w of all("SELECT * FROM wallet_instances")) {
    try {
      tx(() => {
        const nm = (get("SELECT name, lang FROM wallet_names WHERE wallet_id=? AND alias=0 AND valid_to IS NULL ORDER BY id DESC LIMIT 1", w.id) || {});
        const d = defNode(w.definition_key) || defNode(defaultKey(w.tenant_id));
        const holder = holderOf(w.tenant_id, w.owner, true, "port");
        const id = K().createNode(KEY.walletKind, { namespace: tenantNs(w.tenant_id), attributes: { name: nm.name ? { [nm.lang || sourceLang()]: nm.name } : (definitionAt(d, w.tenant_id) || { spec: {} }).spec.name, unit: w.unit, status: w.status, tenant: Number(w.tenant_id), owner: w.owner } }, "port");
        K().place(KEY.definitions, id, d, { namespace: tenantNs(w.tenant_id) }, "port");
        K().place(KEY.holding, id, holder, { namespace: tenantNs(w.tenant_id) }, "port");
        run("UPDATE ledger_accounts SET wallet_id=? WHERE wallet_id=?", id, w.id);
        run("UPDATE wallet_holds SET wallet_id=? WHERE wallet_id=?", id, w.id);
        K().append(EVT.ported, { namespace: tenantNs(w.tenant_id), subject: id, actor: "port", payload: { from: w.id } });
      });
      n++;
    } catch (e) { console.error("wallet port:", w.id, e.message); }
  }
  if (!get("SELECT COUNT(*) n FROM ledger_accounts WHERE wallet_id IN (SELECT id FROM wallet_instances)").n) for (const t of ["wallet_names", "wallet_instances", "wallet_definitions"]) run("DROP TABLE IF EXISTS " + t);
  return n;
}
function vocabulary() {
  return { operations: ops(), systemAccounts: SEED.systemAccounts, classes: classesOf(), settings: SEED.settings.map(s => ({ name: s.name, type: s.type, label: s.label })),
    walletActions: Object.entries(states.actions(M)).map(([verb, to]) => ({ verb, to, label: states.display(M, to).label })),
    holdActions: Object.entries(states.actions(H)).map(([verb, to]) => ({ verb, to, label: states.display(H, to).label })) };
}
/* the operation a signed movement posts under when its caller names none: the one the seed marks */
const defaultOp = dir => (ops().find(o => o[dir === "in" ? "default_in" : "default_out"]) || {}).key;

module.exports = { defaultOp, seed, migrate, define, chooseDefault, definition, definitions, open, rename, names, walletsOf, move, balances, balanceOf, post, transfer, reverse, statement,
  hold, capture, release, holds, sweepAll, walletFor, verify, journal, vocabulary, toMinor, toMajor, unitOf };
