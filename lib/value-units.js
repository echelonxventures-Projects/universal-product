/* LUXORA Platform — units of value on the kernel (P10, owner Value).

   Every unit of value — a currency, a credit, points — is a node of the value.unit kind
   (lib/seed/value.json kernel), known by its code, under its class in the value.classes hierarchy.
   A row of Value's table is the node's read model: every write — the console's, global.js, the
   registry's, a rate feed's — goes through here, the kernel first and the row in the same
   transaction. A rename or a new rate is a new version with the old one kept; a switched-off unit
   is hidden, a deleted one archived. A unit a store trades in can be neither: whoever uses it moves
   to another first. The boot pass only imports rows the kernel has never seen. */
"use strict";

const all = (...a) => require("./db.js").all(...a);
const get = (...a) => require("./db.js").get(...a);
const run = (...a) => require("./db.js").run(...a);
const K = require("./kernel.js");
const LC = require("./kernel-lifecycle.js");
const VALUE = require("./seed/value.json");
const M = VALUE.kernel;
const NS = M.namespace, H = M.hierarchy.hierarchy, SCHEME = M.scheme;
const REFUSED = Symbol("refused");
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const refuse = msg => { const e = new Error(msg); e.status = 400; throw e; };
const upper = c => String(c || "").toUpperCase();
const uidOf = code => K.resolveIdentifier(SCHEME, upper(code)) || null;

function declare() {
  K.ensureTables(); LC.ensureTables();
  for (const d of M.kinds) {
    const k = K.kindOf(d.kind, NS);
    if (!k || k.owner !== d.owner || !same(k.attributes.map(a => a.key), d.attributes.map(a => a.key)) || !same(k.schemes, d.schemes)) K.defineKind({ ...d, namespace: NS }, M.actor);
  }
  if (!K.hierarchyOf(H, NS)) K.defineHierarchy({ ...M.hierarchy, namespace: NS }, M.actor);
}
/* the class a unit is under: its node, made the first time a unit is in it */
function classNode(key) {
  const k = key || VALUE.defaultClass;
  const found = K.nodes(M.classKind, NS).find(u => (K.attributes(u) || {}).key === k);
  if (found) return found;
  const decl = require("./registry.js").valueClasses().find(c => c && c.key === k) || { key: k, name: k };
  const uid = K.createNode(M.classKind, { namespace: NS, attributes: { key: k, name: decl.name || k } }, M.actor);
  K.place(H, uid, null, { namespace: NS }, M.actor);
  return uid;
}
/* the facts of a row (or of the part of one being written) that the kernel holds */
function factsOf(row) {
  const out = {};
  if (row.name !== undefined) out.name = String(row.name);
  if (row.symbol !== undefined) out.symbol = String(row.symbol);
  if (row.decimals !== undefined && row.decimals !== null && row.decimals !== "") out.decimals = Number(row.decimals);
  if (row.usd !== undefined && row.usd !== null && row.usd !== "") out.rate = Number(row.usd);
  if (row.settleable !== undefined && row.settleable !== null) out.settleable = !(row.settleable === false || row.settleable === 0 || row.settleable === "0");
  return out;
}
const off = v => v === false || v === 0 || v === "0" || v === "false";
/* the stores that trade in a unit now: the one they chose, else their country's */
function usedBy(code) {
  const c = upper(code), settings = require("./settings.js"), reg = require("./registry.js");
  return all("SELECT id, name FROM tenants ORDER BY id").filter(t => {
    const m = settings.load(t.id).commerce || {}, own = m.currency && reg.currency(m.currency);
    const co = own ? null : reg.country(m.country);
    return upper(own ? own.code : co && co.currency) === c;
  });
}
function guard(code, doing) {
  const users = usedBy(code);
  if (users.length) refuse(`${upper(code)} cannot be ${doing}: ${users.map(u => u.name).join(", ")} ${users.length > 1 ? "trade" : "trades"} in it. Give ${users.length > 1 ? "them" : "it"} another currency first.`);
}
function setListed(uid, on, actor) {
  const st = LC.nodeState(uid), S = K.SEED.lifecycle.nodeStates;
  if (on && st !== S.initial) LC.unhide(uid, actor);
  if (!on && st === S.initial) LC.hide(uid, actor);
}
/* the node of a row, imported when the kernel has never seen it */
function importRow(r, actor) {
  const uid = K.createNode(M.kind, { namespace: NS, uid: r.uid && !K.internal.nodeRow(r.uid) ? r.uid : undefined, attributes: factsOf(r), identifiers: { [SCHEME]: upper(r.code) } }, actor);
  K.place(H, uid, classNode(r.class), { namespace: NS }, actor);
  if (off(r.active)) setListed(uid, false, actor);
  if (r.uid !== uid) run("UPDATE currencies SET uid=? WHERE code=?", uid, r.code);
  return uid;
}
/* a unit's facts, class and state as a write asks for them */
function put(code, row, actor) {
  const uid = uidOf(code), facts = factsOf(row);
  if (!uid) return importRow({ ...row, code: upper(code), uid: undefined }, actor);
  if (row.active !== undefined && off(row.active) && LC.nodeState(uid) === K.SEED.lifecycle.nodeStates.initial) guard(code, "switched off");
  const cur = K.attributes(uid) || {}, diff = Object.fromEntries(Object.entries(facts).filter(([k, v]) => !same(cur[k], v)));
  if (Object.keys(diff).length) K.record(uid, diff, {}, actor);
  if (row.class !== undefined) {
    const to = classNode(row.class), at = K.parents(H, uid, { namespace: NS });
    if (!at.includes(to)) { for (const p of at) K.endPlacement(H, uid, p, null, { namespace: NS }, actor); K.place(H, uid, to, { namespace: NS }, actor); }
  }
  if (row.active !== undefined && row.active !== null) setListed(uid, !off(row.active), actor);
  return uid;
}
/* the write path every writer of a unit's row goes through (lib/entity.js WRITERS) */
function through(removing, key, row, code, writeRow) {
  try {
    return K.internal.tx(() => {
      declare();
      if (removing) { guard(code, "deleted"); }
      else put(code, row || {}, M.actor);
      const out = writeRow();
      if (out && out.error) throw Object.assign(new Error(out.error), { [REFUSED]: out });
      const uid = uidOf(code);
      if (uid && removing) { K.endIdentifier(uid, SCHEME, upper(code), null, M.actor); LC.archive(uid, M.actor); }
      else if (uid) run("UPDATE currencies SET uid=? WHERE code=?", uid, upper(code));
      return out;
    });
  } catch (e) {
    if (e[REFUSED]) return e[REFUSED];
    if (e.status === 400) return { error: e.message };
    throw e;
  }
}
/* a rate, effective from now; the one before it stays on record */
function setRate(code, usd) {
  const out = through(false, "currency", { usd }, code, () => { run("UPDATE currencies SET usd=? WHERE code=?", usd, upper(code)); return { ok: true }; });
  if (out && out.error) refuse(out.error);
  return out;
}
/* rows the kernel has never seen; a warm pass writes nothing */
function importRows() {
  return K.internal.tx(() => {
    declare();
    let n = 0;
    for (const r of all("SELECT * FROM currencies ORDER BY position, code")) if (!uidOf(r.code)) { importRow(r, M.importActor); n++; }
    return n;
  });
}
/* a unit as it stood at an instant, and how it came to be */
function at(code, o) {
  const uid = uidOf(code); if (!uid) return null;
  return { uid, code: upper(code), listed: LC.nodeState(uid) === K.SEED.lifecycle.nodeStates.initial, ...K.attributes(uid, o) };
}
module.exports = { declare, importRows, through, setRate, usedBy, uidOf, at, KIND: M.kind, HIERARCHY: H, NAMESPACE: NS };
