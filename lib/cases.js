/* LUXORA Platform — cases: anything someone asks a store to look at and decide.

   A price-match claim, a prescription to verify, a practitioner's credentials, an enquiry about a
   property or a vehicle, a trade-in to value — each is a CASE of a kind. A kind is a caseKinds
   registry row, and everything a kind does is declared on it:
     atom        the capability that must be on for the store to take such cases
     subject     what a case is about: a product, an order, or nothing
     fields      what the opener fills in ({ key, label, type, required }); documents ride as URLs
     opens       who opens one: the shopper, a seller, or staff
     effect      what approval does, as flags: `amount` (the decision names an amount), `wallet`
                 (it is credited to the opener's wallet, under `ledger_kind`), `valid_days` (the
                 approval holds that long), `line_credit` (the opener takes it once, off a bag line,
                 through the `case` line term)
     gates       a product fact that makes buying the product need an approved case of this kind
                 (a prescription for a product whose attrs say prescription_required)
     machine     the state machine a case of the kind lives by (asked by tag: open, decided, …)
   Nothing here names a kind. A new kind of case — a warranty claim, a return inspection, a
   licence check — is a registry row and, if it needs one, a capability atom. */
"use strict";

const db = () => require("./db.js");
const caps = () => require("./capabilities.js");
const reg = () => require("./parity-registries.js");
const states = require("./states.js");
const lineterms = require("./lineterms.js");
const fail = lineterms.fail;
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };
const rows = name => reg().list(name).map(x => (typeof x === "string" ? { key: x, name: x } : x)).filter(x => x && x.key);
const kindOf = key => rows("caseKinds").find(r => r.key === String(key == null ? "" : key)) || null;
const sqlNow = () => new Date().toISOString().slice(0, 19).replace("T", " ");
const sqlIn = days => new Date(Date.now() + Number(days) * 86400000).toISOString().slice(0, 19).replace("T", " ");
const tell = (...a) => require("./tell.js").tell(...a);

/* the kinds a store takes: those whose capability is on */
function kinds(tid) { return rows("caseKinds").filter(k => !k.atom || caps().on(Number(tid), k.atom)); }
function kindFor(tid, key) {
  const k = kindOf(key);
  if (!k) throw fail("Unknown kind of case: " + key);
  if (k.atom && !caps().on(Number(tid), k.atom)) throw fail("This store does not take " + k.name.toLowerCase(), 403);
  return k;
}
/* every kind names the machine its cases live by */
const machine = k => k.machine || (() => { throw fail("Kind " + k.key + " names no state machine"); })();
const subjectOf = key => rows("caseSubjects").find(r => r.key === key) || null;
function present(c) {
  const k = kindOf(c.kind) || {};
  const m = machine(k);
  return { ...c, fields: J(c.fields, {}), docs: J(c.docs, []), kind_row: k, state: states.display(m, c.status), next: states.next(m, c.status),
    open: states.is(m, c.status, "open"), valid: states.is(m, c.status, "success") && (!c.valid_until || c.valid_until > sqlNow()) && !c.used_order };
}

/* ---------- opening ---------- */
const typeOk = { text: v => typeof v === "string", number: v => isFinite(Number(v)), date: v => !isNaN(new Date(v).getTime()), url: v => /^https?:\/\//i.test(String(v)), bool: v => typeof v === "boolean" };
function open(tid, opener, input, role) {
  const i = input || {};
  const k = kindFor(tid, i.kind);
  if (k.opens && !k.opens.includes(role)) throw fail("A " + k.name.toLowerCase() + " is not opened that way", 403);
  let subjectId = null;
  if (k.subject) {
    subjectId = String(i.subject_id || "");
    /* how a subject is found is its caseSubjects row's lookup */
    const sub = subjectOf(k.subject);
    const LOOKUPS = { product: () => db().get("SELECT id FROM products WHERE tenant_id=? AND id=?", Number(tid), subjectId), order: () => db().get("SELECT id FROM orders WHERE tenant_id=? AND (num=? OR id=?) AND owner=?", Number(tid), subjectId, Number(subjectId) || -1, String(opener)) };
    if (!sub || !LOOKUPS[sub.lookup] || !LOOKUPS[sub.lookup]()) throw fail("Say which " + ((sub && sub.name) || k.subject).toLowerCase() + " this is about", 404);
  }
  const f = {};
  for (const d of k.fields || []) {
    const v = (i.fields || {})[d.key];
    if (v == null || v === "") { if (d.required) throw fail(d.label + " is required"); continue; }
    if (typeOk[d.type] && !typeOk[d.type](v)) throw fail(d.label + " is not a valid " + d.type);
    f[d.key] = typeof v === "string" ? v.slice(0, 2000) : v;
  }
  const docs = (Array.isArray(i.docs) ? i.docs : []).map(String).filter(u => /^https?:\/\//i.test(u)).slice(0, 10);
  const r = db().run("INSERT INTO cases(tenant_id,kind,subject_type,subject_id,owner,fields,docs,status) VALUES(?,?,?,?,?,?,?,?)",
    Number(tid), k.key, k.subject || "", subjectId, String(opener), JSON.stringify(f), JSON.stringify(docs), states.initial(machine(k)));
  return present(db().get("SELECT * FROM cases WHERE id=?", r.lastInsertRowid));
}

/* ---------- deciding ---------- */
function move(tid, id, action, input, actor) {
  const c = db().get("SELECT * FROM cases WHERE id=? AND tenant_id=?", Number(id), Number(tid));
  if (!c) throw fail("Case not found", 404);
  const k = kindFor(tid, c.kind), m = machine(k);
  const to = states.actionTarget(m, action);
  if (!to || !states.can(m, c.status, to)) throw fail("That cannot be done to this case now", 409);
  const i = input || {};
  const success = states.is(m, to, "success");
  const amount = success && k.effect && k.effect.amount ? +Number(i.amount).toFixed(2) : null;
  if (success && k.effect && k.effect.amount && !(amount > 0)) throw fail("Say the amount it is approved for");
  if (!success && states.is(m, to, "decision") && !String(i.reason || "").trim()) throw fail("Say why");
  const mv = states.apply(m, { tenantId: tid, from: c.status, to, row: c });
  const patch = { ...mv.patch, decided_by: String(actor || ""), reason: String(i.reason || "").slice(0, 500),
    ...(amount != null ? { amount } : {}), ...(success && k.effect && k.effect.valid_days ? { valid_until: sqlIn(k.effect.valid_days) } : {}) };
  const cols = Object.keys(patch);
  db().run("UPDATE cases SET " + cols.map(x => x + "=?").join(", ") + " WHERE id=?", ...cols.map(x => patch[x]), c.id);
  /* a wallet effect credits the opener now; a line credit is taken later, off a bag line */
  if (success && k.effect && k.effect.wallet && amount > 0) require("./offers.js").credit(c.tenant_id, c.owner, amount, String(k.effect.ledger_kind || ""), "case:" + c.id, null, "cases");
  tell(tid, c.owner, "case", k.name + ": " + states.display(m, to).label, i.reason || "", "account.html");
  return present(db().get("SELECT * FROM cases WHERE id=?", c.id));
}
/* the opener withdraws their own open case */
function withdraw(tid, owner, id) {
  const c = db().get("SELECT * FROM cases WHERE id=? AND tenant_id=? AND owner=?", Number(id), Number(tid), String(owner));
  if (!c) throw fail("Case not found", 404);
  return move(tid, id, "withdraw", {}, owner);
}
function list(tid, o) {
  o = o || {};
  const ks = kinds(tid).map(k => k.key);
  if (!ks.length) return [];
  return db().all(`SELECT * FROM cases WHERE tenant_id=? AND kind IN (${ks.map(() => "?").join(",")})` + (o.kind ? " AND kind=?" : "") + (o.owner ? " AND owner=?" : "") + " ORDER BY id DESC LIMIT 300",
    Number(tid), ...ks, ...(o.kind ? [o.kind] : []), ...(o.owner ? [String(o.owner)] : [])).map(present);
}
/* the opener's approved, still-valid cases of a kind (about a subject, if given) */
function validFor(tid, owner, kind, subjectId) {
  return list(tid, { kind, owner }).filter(c => c.valid && (!subjectId || !c.subject_id || c.subject_id === String(subjectId)));
}

/* ---------- buying: a product a kind gates needs a valid case; a line credit rides as a term ---------- */
/* the kinds whose declared gate this product's facts meet */
function gatesFor(tid, product) {
  const attrs = J(product.attrs, {});
  return kinds(tid).filter(k => k.gates && attrs[k.gates.attr] === (k.gates.equals != null ? k.gates.equals : true));
}
/* the `case` line term: { id } of an approved case — a gate it satisfies, or a credit it carries */
lineterms.register("case", {
  clean: (ctx, value) => {
    const id = Number(value && typeof value === "object" ? value.id : value);
    const c = db().get("SELECT * FROM cases WHERE id=? AND tenant_id=? AND owner=?", id, Number(ctx.tid), String(ctx.owner || ""));
    if (!c) throw fail("That case is not yours");
    const p = present(c);
    if (!p.valid) throw fail("That case is not approved, or has lapsed");
    if (p.subject_id && (subjectOf(p.subject_type) || {}).line_item && p.subject_id !== ctx.product.id) throw fail("That case is about another item");
    if (c.used_order && lineCredit(p)) throw fail("That credit has been used");
    return { id };
  },
  price: (ctx, value) => {
    const p = present(db().get("SELECT * FROM cases WHERE id=?", Number(value.id)));
    if (!p.valid) throw fail("the case on this line is no longer valid");
    const credit = lineCredit(p) ? -Number(p.amount || 0) : 0;
    return { add: credit, label: p.kind_row.name + (credit ? " (" + credit.toFixed(2) + ")" : "") };
  },
  maxQty: (ctx, value) => lineCredit(present(db().get("SELECT * FROM cases WHERE id=?", Number(value.id)))) ? 1 : Infinity,
  /* a line credit is taken once: the order that took it is recorded on the case */
  place: (ctx, value) => { const p = present(db().get("SELECT * FROM cases WHERE id=?", Number(value.id))); if (lineCredit(p)) db().run("UPDATE cases SET used_order=? WHERE id=?", Number(ctx.orderId), p.id); }
});
const lineCredit = p => !!(p.kind_row.effect && p.kind_row.effect.line_credit);
/* a product a kind gates cannot go in the bag without a valid case of that kind on its line */
function checkGates(tid, owner, product, terms) {
  for (const k of gatesFor(tid, product)) {
    const t = terms && terms.case;
    const ok = t && (() => { const c = db().get("SELECT * FROM cases WHERE id=? AND owner=?", Number(t.id), String(owner || "")); return c && present(c).valid && c.kind === k.key; })();
    if (!ok) throw fail(product.title + " needs " + k.name.toLowerCase() + " — open one and add it to the item", 403);
  }
}

function vocabulary(tid) {
  return { kinds: kinds(tid), actions: [...new Set(kinds(tid).map(machine))].flatMap(m => Object.entries(states.actions(m)).map(([verb, to]) => ({ machine: m, verb, to, label: states.display(m, to).label }))) };
}

/* the console section a case is decided from: its kind's */
function sectionOf(id) { return (kindOf((db().get("SELECT kind FROM cases WHERE id=?", Number(id)) || {}).kind) || {}).section; }

module.exports = { kinds, open, move, withdraw, list, validFor, gatesFor, checkGates, vocabulary, sectionOf };
