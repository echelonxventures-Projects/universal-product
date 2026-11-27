/* LUXORA Platform — rows kept on the kernel by one engine (P24).

   A table whose rows are business records — a return, a payment — is declared once in
   lib/seed/row-records.json: the kind its rows are, the facts recorded as versions in time, and the row
   it belongs to. Each row is a node in its store's namespace with the row's own universal ID; its
   facts are versions, so how it stood at any instant is answerable (a payment's refunded amount over
   time is its refund history); the row it belongs to is a relationship. Personal data is never a
   fact here.

   Every write goes through change() (or changeWhere() for a write that touches many rows): the row
   and its record in one transaction. A new table on the master is a new entry, not new code. */
"use strict";

const db = () => require("./db.js");
const K = require("./kernel.js");
const LC = require("./kernel-lifecycle.js");
const SEED = require("./seed/row-records.json");
const NS = tid => require("./master-permissions.js").storeHolder(tid);
const S = () => K.SEED.lifecycle.nodeStates;
const fail = (msg, status) => { const e = new Error(msg); e.status = status || 400; throw e; };
/* a wrapped write returns what it wrote; one that returns the database itself was wrapped around the
   wrong call (db() instead of db().run(…)), and its record would be taken before the write */
const wrote = out => { if (out && typeof out === "object" && typeof out.run === "function" && typeof out.get === "function") throw new Error("A recorded write must wrap the statement, not the database: () => db().run(…)"); return out; };
const refused = out => !!out && typeof out === "object" && Object.prototype.hasOwnProperty.call(out, "error") && !!out.error;
const spec = name => SEED.records[name] || fail("No such record: " + name);
const TYPES = { text: "text", number: "number" };

const ready = new Set();
function declare(name) {
  if (ready.has(name)) return;
  const sp = spec(name);
  K.ensureTables(); LC.ensureTables(); require("./order-records.js").declare(); /* orders, people and products first */
  /* a kind may extend one the master already has (a company is an organisation): it declares only
     the facts its parent kind does not already have, and never redefines the parent */
  const base = sp.kind.extends ? K.kindOf(sp.kind.extends, "platform") : null;
  if (sp.kind.extends && !base) fail(sp.kind.kind + " extends " + sp.kind.extends + ", which the master does not have");
  const inherited = new Set(base ? base.attributes.map(a => a.key) : []);
  const attributes = Object.entries(sp.facts).filter(([key]) => !inherited.has(key)).map(([key, type]) => ({ key, type: TYPES[type], label: key }));
  const k = K.kindOf(sp.kind.kind, "platform");
  const has = new Set(k ? k.attributes.map(a => a.key) : []);
  if (!k || Object.keys(sp.facts).some(f => !has.has(f))) K.defineKind({ kind: sp.kind.kind, owner: sp.owner, label: sp.kind.label, ...(base ? { extends: sp.kind.extends } : { root: true }), parents: sp.kind.parents, schemes: [], attributes, namespace: "platform" }, SEED.actor);
  const b = sp.belongsTo;
  if (b && !K.hierarchyOf(b.hierarchy, "platform")) K.defineHierarchy({ hierarchy: b.hierarchy, owner: "Relationship", label: b.label, namespace: "platform" }, SEED.actor);
  ready.add(name);
}
function factsOf(sp, row) {
  const out = {};
  for (const [k, type] of Object.entries(sp.facts)) { const v = row[k]; if (v === undefined || v === null || v === "") continue; out[k] = type === "number" ? Number(v) : String(v); }
  return out;
}
const nodeOf = row => (row && row.uid && K.internal.nodeRow(row.uid)) ? row.uid : null;
function parentOf(sp, row) {
  const b = sp.belongsTo; if (!b) return null;
  /* the person an owner column names ("t1:u:5"); a guest has none */
  if (b.owner) {
    const m = /:u:(\d+)$/.exec(String(row[b.owner] || ""));
    const u = m && db().get("SELECT uid FROM users WHERE id=? AND tenant_id=?", Number(m[1]), Number(row.tenant_id));
    return u && u.uid && K.internal.nodeRow(u.uid) ? u.uid : null;
  }
  if (row[b.column] == null) return null;
  const p = db().get(`SELECT uid FROM ${b.table} WHERE id=?`, row[b.column]);
  return p && p.uid && K.internal.nodeRow(p.uid) ? p.uid : null;
}
/* what else follows a record's changes (the books post from payments and invoices): each listener
   is told the row and its facts before and after, inside the same transaction */
const listeners = {};
const on = (name, fn) => { spec(name); (listeners[name] = listeners[name] || []).push(fn); };
function record(name, row, actor) {
  const sp = spec(name);
  let uid = nodeOf(row);
  const f = factsOf(sp, row);
  const before = uid ? { ...(K.attributes(uid) || {}) } : {};
  const out = recordOnly(name, sp, row, uid, f, actor);
  for (const fn of listeners[name] || []) fn({ name, row: db().get(`SELECT * FROM ${sp.table} WHERE id=?`, row.id) || row, before, after: f, uid: out });
  return out;
}
function recordOnly(name, sp, row, uid, f, actor) {
  if (!uid) {
    uid = K.createNode(sp.kind.kind, { namespace: NS(row.tenant_id), uid: row.uid && !K.internal.nodeRow(row.uid) ? row.uid : undefined, attributes: f }, actor);
    if (row.uid !== uid) db().run(`UPDATE ${sp.table} SET uid=? WHERE id=?`, uid, row.id);
    const p = parentOf(sp, row);
    if (p) K.place(sp.belongsTo.hierarchy, uid, p, { namespace: "platform" }, actor);
  } else {
    const cur = K.attributes(uid) || {};
    const diff = Object.fromEntries(Object.entries(f).filter(([k, v]) => cur[k] !== v));
    if (Object.keys(diff).length) K.record(uid, diff, {}, actor);
    if (sp.belongsTo) follow(sp, row, uid, actor);
  }
  return uid;
}
/* the row it belongs to changed (a project given to its company): the old placement ends and the new
   one begins, so where it sat before stays answerable; a link cleared ends it */
function follow(sp, row, uid, actor) {
  const h = sp.belongsTo.hierarchy, o = { namespace: "platform" };
  const now = K.parents(h, uid, o), want = parentOf(sp, row);
  const cleared = !sp.belongsTo.owner && (row[sp.belongsTo.column] == null || row[sp.belongsTo.column] === "");
  if (want ? now.length === 1 && now[0] === want : !(cleared && now.length)) return;
  for (const p of now) K.endPlacement(h, uid, p, null, o, actor);
  if (want) K.place(h, uid, want, o, actor);
}
/* a write of named rows: the rows and their records in one transaction */
function change(name, ids, writeRow, actor) {
  return K.internal.tx(() => {
    declare(name);
    const out = wrote(writeRow());
    if (refused(out)) return out;
    for (const id of [].concat(ids)) { const row = db().get(`SELECT * FROM ${spec(name).table} WHERE id=?`, Number(id)); if (row) record(name, row, actor || SEED.actor); }
    return out;
  });
}
/* an insert: the new row (the write's lastInsertRowid) and its record in one transaction */
function created(name, writeRow, actor) {
  return K.internal.tx(() => {
    declare(name);
    const out = wrote(writeRow());
    const id = out && out.lastInsertRowid != null ? Number(out.lastInsertRowid) : null;
    const row = id != null && db().get(`SELECT * FROM ${spec(name).table} WHERE id=?`, id);
    if (row) record(name, row, actor || SEED.actor);
    return out;
  });
}
/* a write that touches every row a condition picks */
function changeWhere(name, where, args, writeRow, actor) {
  return K.internal.tx(() => {
    declare(name);
    const ids = db().all(`SELECT id FROM ${spec(name).table} WHERE ${where}`, ...(args || [])).map(r => r.id);
    const out = wrote(writeRow());
    if (refused(out)) return out;
    for (const id of ids) { const row = db().get(`SELECT * FROM ${spec(name).table} WHERE id=?`, id); if (row) record(name, row, actor || SEED.actor); }
    return out;
  });
}
/* rows about to be deleted outright: their records are archived, so history stays */
function removing(name, where, args, actor) {
  declare(name);
  for (const r of db().all(`SELECT uid FROM ${spec(name).table} WHERE ${where}`, ...(args || []))) {
    const uid = nodeOf(r); if (uid && LC.nodeState(uid) !== S().archived) LC.archive(uid, actor || SEED.actor);
  }
}
/* rows the kernel has never seen, for every declared table; a warm pass writes nothing */
function importRows() {
  return K.internal.tx(() => {
    let n = 0;
    for (const name of Object.keys(SEED.records)) {
      declare(name);
      for (const r of db().all(`SELECT * FROM ${spec(name).table} ORDER BY id`)) if (!nodeOf(r)) { record(name, r, SEED.importActor); n++; }
    }
    return n;
  });
}
function at(name, id, o) {
  const sp = spec(name), r = db().get(`SELECT uid FROM ${sp.table} WHERE id=?`, Number(id)), uid = nodeOf(r);
  if (!uid) return null;
  return { uid, ...(K.attributes(uid, o) || {}), belongsTo: sp.belongsTo ? K.parents(sp.belongsTo.hierarchy, uid, { namespace: "platform" })[0] || null : null };
}
/* the values one fact has had, oldest first */
function history(name, id, fact) {
  const uid = nodeOf(db().get(`SELECT uid FROM ${spec(name).table} WHERE id=?`, Number(id)));
  if (!uid) return [];
  const out = [];
  for (const v of K.history(uid).filter(x => x.recordedTo == null)) if (!out.length || out[out.length - 1].value !== v.attributes[fact]) out.push({ from: v.validFrom, value: v.attributes[fact] });
  return out;
}
/* the records that belong to a row (an order's returns, its payments) */
const of = (name, parentUid) => { declare(name); return K.children(spec(name).belongsTo.hierarchy, parentUid, { namespace: "platform" }); };
module.exports = { declare, on, change, created, changeWhere, removing, importRows, at, history, of, SEED };
