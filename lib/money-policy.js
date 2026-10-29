/* LUXORA Platform — the governed money policy (PR-049).
   How money is rounded is a policy, not code: a platform rule and per-currency rules, kept as a
   kernel node whose attributes are versioned in the kernel's bitemporal k_versions, and changed
   only through the kernel's change lifecycle. lib/money.js asks this module which rule applies.

   The policy (lib/seed/money-policy.json declares it):
     VERSION    one row of k_versions: the rules, the valid time they apply in and the recorded
                time they were believed in. Its reference (`money-policy:<row id>`) is written
                on every money row of the payment spine (lib/money-store.js, money_policy), so
                any order, payment, invoice or refund says which rules it was computed under
     SEED       the first version is seeded from lib/seed/money.json, so a fresh install
                applies exactly the rule it always did. Before it exists (the first boot, before
                the kernel is up) the seed file is the policy and rows record `money-policy:seed`
     CHANGE     a kernel change of one `record` operation: drafted, validated (a dry run),
                previewed (the same dry run, rounding sample amounts under the current and the
                proposed rules, leaving nothing behind), approved by someone other than its
                author, published, and rolled back. A change records the version it was drafted
                against; if the policy has moved on since, it is refused and drafted again
     VALIDATION a policy is data only — a rule from lib/money.js MODES per currency the master
                knows, and a note. Nothing in it is evaluated. An invalid or missing policy is
                refused, never replaced by a guess
   Effective time is valid time: a change may take effect later than it is published (its
   `validFrom`), never earlier, so no past calculation is reinterpreted. Domain: Currency. */
"use strict";

const SEED = require("./seed/money-policy.json");
const BASE = require("./seed/money.json");

const K = () => require("./kernel.js");
const L = () => require("./kernel-lifecycle.js");
const D = () => require("./db.js");
const M = () => require("./money.js");
const fail = (m, status, code) => Object.assign(new Error(m), { status: status || 400, code: code || "money_policy_invalid" });
const FIELDS = SEED.attributes.map(a => a.key);
const SEED_REF = SEED.ref + ":" + SEED.seedRef;

/* ============================== the kernel declarations ============================== */
/* the policy's kind: its attributes from the seed, the rounding rule one of lib/money.js MODES */
function kindSpec() {
  const modes = [...M().MODES];
  return {
    namespace: SEED.namespace, kind: SEED.kind, owner: SEED.owner, label: SEED.label, root: true, schemes: [SEED.scheme],
    attributes: SEED.attributes.map(a => a.key === "rounding" ? { ...a, constraints: { ...(a.constraints || {}), oneOf: modes } } : a)
  };
}
const signature = attrs => JSON.stringify(attrs.map(a => [a.key, a.type, !!a.required, a.constraints || {}]));
function nodeUid() {
  K().ensureTables();
  const r = D().get("SELECT node FROM k_identifiers WHERE scheme=? AND value=? AND rec_to IS NULL ORDER BY id LIMIT 1", SEED.scheme, SEED.key);
  return r ? r.node : null;
}
/* declares the kind and seeds the first version, once; a changed declaration is redeclared */
function ensure() {
  const k = K();
  L().ensureTables();
  const want = kindSpec(), cur = k.kindOf(SEED.kind, SEED.namespace);
  if (!cur || signature(cur.attributes) !== signature(want.attributes.map(a => ({ ...a, constraints: a.constraints || {} })))) k.defineKind(want, SEED.actor);
  if (!nodeUid()) {
    const first = check({ rounding: BASE.rounding, currencies: BASE.currencies || {} });
    k.createNode(SEED.kind, { namespace: SEED.namespace, attributes: first, identifiers: { [SEED.scheme]: SEED.key } }, SEED.actor);
  }
  invalidate();
  return nodeUid();
}

/* ============================== validation ============================== */
/* a policy is a record of declared fields only; every rule is a named rounding rule and every
   currency one the master knows. Returns the clean policy, its currencies in code order */
function check(p) {
  if (!p || typeof p !== "object" || Array.isArray(p)) throw fail("A money policy is a record of " + FIELDS.join(", "));
  for (const key of Object.keys(p)) if (!FIELDS.includes(key)) throw fail("A money policy has no field " + key);
  const modes = M().MODES;
  const rule = (v, where) => { if (typeof v !== "string" || !modes.has(v)) throw fail(`${where}: the rounding rule is one of ${[...modes].join(", ")}, not ${JSON.stringify(v)}`); return v; };
  const out = { rounding: rule(p.rounding, "The platform") };
  const cs = p.currencies == null ? {} : p.currencies;
  if (typeof cs !== "object" || Array.isArray(cs)) throw fail("currencies is a record: { <currency code>: { rounding } }");
  out.currencies = {};
  for (const code of Object.keys(cs).sort()) {
    let known;
    try { known = M().currencyOf(code); } catch (e) { throw fail("Unknown currency in the policy: " + code, 400, "currency_unknown"); }
    if (known.code !== code) throw fail(`A currency is named by its code as the master spells it: ${known.code}, not ${code}`);
    const c = cs[code];
    if (!c || typeof c !== "object" || Array.isArray(c)) throw fail(code + ": a currency's policy is a record: { rounding }");
    for (const key of Object.keys(c)) if (!SEED.currencyKeys.includes(key)) throw fail(code + ": a currency's policy has no field " + key);
    out.currencies[code] = { rounding: rule(c.rounding, code) };
  }
  if (p.note != null) {
    if (typeof p.note !== "string") throw fail("note is text");
    const max = (SEED.attributes.find(a => a.key === "note").constraints || {}).maxLength;
    if (max && p.note.length > max) throw fail(`note is at most ${max} characters`);
    if (p.note.trim()) out.note = p.note.trim();
  }
  return out;
}

/* ============================== reading ============================== */
const refOf = id => SEED.ref + ":" + id;
function view(r) {
  const a = JSON.parse(r.attrs || "{}");
  return { ref: refOf(r.id), version: r.id, source: "kernel", rounding: a.rounding, currencies: a.currencies || {}, note: a.note || null,
    validFrom: r.valid_from, validTo: r.valid_to, recordedFrom: r.rec_from, recordedTo: r.rec_to };
}
const seedView = () => ({ ref: SEED_REF, version: null, source: "seed", rounding: BASE.rounding, currencies: BASE.currencies || {}, note: null, validFrom: null, validTo: null, recordedFrom: null, recordedTo: null });
/* the database is still loading (lib/db.js seeds rows before it exports): the kernel cannot be
   asked yet, and the seed file is the policy */
const dbReady = () => typeof D().writes === "function";
function read(o) {
  if (!dbReady()) return seedView();
  const uid = nodeUid();
  if (!uid) return seedView();
  const I = K().internal;
  const b = I.believed(I.recordedSeq(o.recorded)), v = I.validAt(I.instant(o.at, "at") || I.nowIso());
  const r = D().get(`SELECT * FROM k_versions WHERE node=? AND ${b.sql} AND ${v.sql}`, uid, ...b.args, ...v.args);
  /* the node exists but no version applies at that moment: there is no policy then, and nothing
     is assumed in its place */
  if (!r) throw fail("No money policy applies at " + (o.at || "this moment"), 409, "money_policy_missing");
  const p = view(r);
  check({ rounding: p.rounding, currencies: p.currencies });
  return p;
}
/* the policy in force now is kept until the next write through lib/db.js or the moment it (or
   the next scheduled version) changes, so an edit is never served stale */
let cache = null;
function invalidate() { cache = null; }
function nextChange(now) {
  const uid = nodeUid();
  const r = uid && D().get("SELECT MIN(valid_from) AS t FROM k_versions WHERE node=? AND rec_to IS NULL AND valid_from>?", uid, now);
  return r && r.t ? r.t : null;
}
function active(o) {
  o = o || {};
  if (o.at != null || o.recorded != null || !dbReady()) return read(o);
  const now = new Date().toISOString();
  if (cache && cache.writes === D().writes() && (!cache.until || now < cache.until)) return cache.policy;
  const policy = read({});
  const ends = [policy.validTo, policy.source === "kernel" ? nextChange(now) : null].filter(Boolean).sort();
  cache = { writes: D().writes(), until: ends[0] || null, policy };
  return policy;
}
/* the rule for a currency under the policy in force: its own, else the platform's */
function ruleFor(code, policy) {
  const p = policy || active();
  const c = code ? String(code).toUpperCase() : "";
  return (p.currencies && p.currencies[c] && p.currencies[c].rounding) || p.rounding;
}
const ref = () => active().ref;
/* a version by the reference a money row recorded — kept even after it was superseded or rolled back */
function lookup(reference) {
  const s = String(reference || "");
  if (s === SEED_REF) return seedView();
  const m = new RegExp("^" + SEED.ref + ":(\\d+)$").exec(s);
  const uid = nodeUid();
  const r = m && uid ? D().get("SELECT * FROM k_versions WHERE id=? AND node=?", Number(m[1]), uid) : null;
  if (!r) throw fail("Unknown money policy version: " + s, 404, "money_policy_unknown");
  return view(r);
}
/* every version ever recorded (superseded and rolled back ones included), newest first, with
   the moment it was recorded */
function history() {
  const uid = nodeUid();
  if (!uid) return [];
  return D().all("SELECT v.*, e.at AS recorded_at, e.actor AS recorded_by FROM k_versions v LEFT JOIN k_events e ON e.seq=v.rec_from WHERE v.node=? ORDER BY v.rec_from DESC, v.valid_from DESC", uid)
    .map(r => ({ ...view(r), recordedAt: r.recorded_at, recordedBy: r.recorded_by, current: r.rec_to == null }));
}

/* ============================== changes ============================== */
/* the version a change is drafted against: the last recording of the policy. A publish, a
   rollback or another change moves it */
function baseSeq() {
  const r = D().get("SELECT MAX(rec_from) AS s FROM k_versions WHERE node=? AND rec_to IS NULL", nodeUid());
  return r && r.s != null ? r.s : null;
}
const ownOp = c => c && c.ops.length === 1 && c.ops[0].op === "record" && c.ops[0].args[0] === nodeUid();
function decorate(c) {
  const [, patch, w] = c.ops[0].args;
  return { ...c, proposed: { rounding: patch.rounding, currencies: patch.currencies || {}, note: patch.note || null }, validFrom: (w && w.validFrom) || null, basedOn: w ? w.basedOn : null };
}
function own(id) {
  let c; try { c = L().change(id); } catch (e) { throw fail("Unknown money policy change: " + id, 404, "money_policy_unknown"); }
  if (!ownOp(c)) throw fail("Change " + id + " is not a money policy change", 404, "money_policy_unknown");
  return decorate(c);
}
function fresh(c) {
  if (c.basedOn !== baseSeq()) throw fail("The money policy has changed since change " + c.id + " was drafted; draft it again", 409, "money_policy_stale");
}
function notPast(validFrom, what) {
  if (validFrom && validFrom <= new Date().toISOString()) throw fail(`A money policy takes effect now or later; ${what} ${validFrom} has passed`, 409, "money_policy_past");
}
/* the semantic checks a change must still pass when it moves: its rules (a currency may have left
   the master since), its base and its effective time */
function recheck(c) { check({ rounding: c.proposed.rounding, currencies: c.proposed.currencies, ...(c.proposed.note ? { note: c.proposed.note } : {}) }); fresh(c); notPast(c.validFrom, "its effective time"); }

/* draft({ policy: { rounding, currencies, note }, title, validFrom }) — the whole policy, stated */
function propose(input, actor) {
  const uid = ensure();
  const i = input || {};
  const clean = check(i.policy);
  const I = K().internal;
  const validFrom = I.instant(i.validFrom, "validFrom");
  notPast(validFrom, "validFrom");
  const title = String(i.title || "").trim().slice(0, SEED.titleMax) || SEED.label;
  const patch = { rounding: clean.rounding, currencies: clean.currencies, note: clean.note || null };
  const id = L().draft({ namespace: SEED.namespace, title, ops: [{ op: "record", args: [uid, patch, { ...(validFrom ? { validFrom } : {}), basedOn: baseSeq() }] }] }, actor);
  return own(id);
}
function validate(id, actor) {
  const c = own(id);
  recheck(c);
  try { return { report: L().validate(id, actor), change: own(id) }; } finally { invalidate(); }
}
/* the change applied in a dry run that is always undone: the proposed version as the kernel would
   record it, and each sample amount rounded in each currency under the current and the proposed
   rules. Nothing is written — no version, no event, no money row */
function preview(id, o, actor) {
  const c = own(id);
  recheck(c);
  o = o || {};
  const samples = (Array.isArray(o.samples) && o.samples.length ? o.samples : SEED.samples).slice(0, 50).map(String);
  for (const s of samples) { try { M().parse(s); } catch (e) { throw fail("Not an amount: " + s); } }
  const current = active();
  const at = c.validFrom || null;
  let proposed;
  try {
    proposed = L().preview(id, () => read({ at: at || undefined }), actor);
  } finally { invalidate(); }
  if (!proposed.ok) throw fail("The change does not apply: " + proposed.error, 409, "money_policy_invalid");
  const p = proposed.result;
  const platformCurrency = require("./defaults.js").platformCurrency();
  const asked = Array.isArray(o.currencies) ? o.currencies.map(x => String(x).toUpperCase()) : [];
  const codes = [...new Set([platformCurrency, ...Object.keys(current.currencies || {}), ...Object.keys(p.currencies || {}), ...asked].filter(Boolean))].sort();
  const rows = [];
  for (const code of codes) {
    let decimals; try { decimals = M().decimalsOf(code); } catch (e) { throw fail("Unknown currency: " + code, 400, "currency_unknown"); }
    const was = ruleFor(code, current), will = ruleFor(code, p);
    for (const amount of samples) {
      const before = M().format(M().toMinorBig(amount, decimals, was), decimals), after = M().format(M().toMinorBig(amount, decimals, will), decimals);
      rows.push({ currency: code, decimals, amount, current: { rule: was, result: before }, proposed: { rule: will, result: after }, changed: before !== after });
    }
  }
  return { change: c, current, proposed: { ...p, ref: null, version: null }, effectiveFrom: at, rows, changed: rows.filter(r => r.changed).length };
}
function approve(id, actor, grants) {
  const c = own(id);
  recheck(c);
  try { return own(L().approve(id, actor, grants).id); } finally { invalidate(); }
}
/* published at once; the rules apply from the change's validFrom (now when it named none). The
   base is checked inside the same transaction as the write, so two changes drafted against one
   version cannot both land */
function publish(id, actor) {
  const c = own(id);
  if (c.state !== K().SEED.lifecycle.approved) throw fail("Only an approved change is published; this one is " + c.state, 409, "money_policy_state");
  recheck(c);
  try {
    K().internal.tx(() => { fresh(own(id)); L().publish(id, {}, actor); });
  } finally { invalidate(); }
  return { change: own(id), policy: active() };
}
function rollback(id, actor) {
  own(id);
  try { L().rollback(id, actor); } finally { invalidate(); }
  return { change: own(id), policy: active() };
}
function discard(id, actor) { own(id); try { return own(L().discard(id, actor).id); } finally { invalidate(); } }
function changes() {
  if (!nodeUid()) return [];
  return L().changes().filter(ownOp).map(decorate);
}
/* what the administration screen shows */
function overview() {
  ensure();
  return { policy: active(), history: history(), changes: changes(), modes: [...M().MODES], samples: SEED.samples, base: baseSeq(), states: K().SEED.lifecycle };
}

module.exports = { SEED, ensure, check, active, ruleFor, ref, lookup, history, changes, overview, propose, validate, preview, approve, publish, rollback, discard, invalidate };
