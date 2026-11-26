/* LUXORA Platform — people on the kernel (P24, owner Party).

   Every account of a store is a person: a node of the party.person kind in the store's namespace
   (lib/seed/parties.json), whose universal ID is its users row's. Who they are — their name,
   their email (sealed), their staff role, whether they are disabled — are versions of that node,
   so what held at any moment stays answerable; the role they play (a customer, the store's staff)
   is a relationship to a term of the master's party roles. Their credentials are Security's and
   stay in the users table, which is otherwise the read model of the person.

   Every change to who a person is goes through set(): the kernel first, the row in the same
   transaction. A new account is recorded as it is created (created()), a deleted one is archived,
   and the boot pass only imports accounts the kernel has never seen. */
"use strict";

const db = () => require("./db.js");
const K = require("./kernel.js");
const LC = require("./kernel-lifecycle.js");
const SEED = require("./seed/parties.json");
const NS = tid => require("./master-permissions.js").storeHolder(tid);
const COLS = new Set(SEED.facts);
const fail = (msg, status) => { const e = new Error(msg); e.status = status || 400; throw e; };
const term = role => require("./platform-master.js").uidOf(SEED.roles[role] || SEED.roles.customer);

function declare() {
  /* the master, and the party.roles hierarchy it declares (lib/seed/screens.json) */
  K.ensureTables(); LC.ensureTables(); require("./master-view.js").ensure();
  const k = K.kindOf(SEED.kind.kind, "platform");
  if (!k || k.attributes.length !== SEED.kind.attributes.length) K.defineKind({ ...SEED.kind, namespace: "platform" }, SEED.actor);
}
/* the person's facts, as the kernel holds them, from a users row (or the part being written) */
function factsOf(row) {
  const out = {};
  if (row.name !== undefined) out.name = String(row.name || row.email || "");
  if (row.email !== undefined) out.email = String(row.email || "");
  if (row.staff_role !== undefined) out.staff_role = row.staff_role == null ? null : String(row.staff_role);
  if (row.disabled !== undefined) out.disabled = !!Number(row.disabled);
  return out;
}
const nodeOf = row => (row && row.uid && K.internal.nodeRow(row.uid)) ? row.uid : null;
function placeRole(uid, role, actor) {
  const want = term(role), at = K.parents(SEED.hierarchy, uid, { namespace: "platform" });
  if (at.length === 1 && at[0] === want) return;
  for (const p of at) K.endPlacement(SEED.hierarchy, uid, p, null, { namespace: "platform" }, actor);
  K.place(SEED.hierarchy, uid, want, { namespace: "platform" }, actor);
}
/* the person of an account the kernel has not seen: recorded with the account's own identity */
function importRow(row, actor) {
  const uid = K.createNode(SEED.kind.kind, { namespace: NS(row.tenant_id), uid: row.uid && !K.internal.nodeRow(row.uid) ? row.uid : undefined, attributes: factsOf(row) }, actor);
  placeRole(uid, row.role, actor);
  if (row.uid !== uid) db().run("UPDATE users SET uid=? WHERE id=?", uid, row.id);
  return uid;
}
/* a new account: its person is recorded at once */
function created(userId, actor) {
  return K.internal.tx(() => { declare(); const row = db().get("SELECT * FROM users WHERE id=?", Number(userId)); if (row && !nodeOf(row)) importRow(row, actor || SEED.actor); return Number(userId); });
}
/* changes who a person is: the kernel first, then the row */
function set(userId, patch, actor) {
  const p = Object.fromEntries(Object.entries(patch || {}).filter(([k]) => COLS.has(k)));
  if (!Object.keys(p).length) return;
  return K.internal.tx(() => {
    declare();
    const row = db().get("SELECT * FROM users WHERE id=?", Number(userId)) || fail("Unknown account", 404);
    const uid = nodeOf(row) || importRow(row, actor || SEED.actor);
    const cur = K.attributes(uid) || {}, f = factsOf(p);
    const diff = Object.fromEntries(Object.entries(f).filter(([k, v]) => JSON.stringify(cur[k] === undefined ? null : cur[k]) !== JSON.stringify(v)));
    if (Object.keys(diff).length) K.record(uid, diff, {}, actor || SEED.actor);
    if (p.role !== undefined) placeRole(uid, p.role, actor || SEED.actor);
    const keys = Object.keys(p);
    db().run(`UPDATE users SET ${keys.map(k => k + "=?").join(", ")} WHERE id=?`, ...keys.map(k => k === "disabled" ? (p[k] ? 1 : 0) : p[k]), Number(userId));
  });
}
/* an account deleted: its person is archived, so its history stays */
function remove(userId, actor) {
  return K.internal.tx(() => {
    declare();
    const row = db().get("SELECT uid FROM users WHERE id=?", Number(userId));
    const uid = nodeOf(row);
    if (uid && LC.nodeState(uid) !== K.SEED.lifecycle.nodeStates.archived) LC.archive(uid, actor || SEED.actor);
    db().run("DELETE FROM users WHERE id=?", Number(userId));
  });
}
/* the right to be forgotten: every person of a store with this email is archived and purged — every
   version of who they were goes; the event log keeps only that a node was purged (lib/kernel-lifecycle.js) */
function erase(tenantId, email, actor) {
  return K.internal.tx(() => {
    declare();
    let n = 0;
    for (const r of db().all("SELECT uid FROM users WHERE tenant_id=? AND email=?", Number(tenantId), String(email || "").toLowerCase())) {
      const uid = nodeOf(r); if (!uid) continue;
      if (LC.nodeState(uid) !== K.SEED.lifecycle.nodeStates.archived) LC.archive(uid, actor || SEED.actor);
      LC.purge(uid, [K.SEED.lifecycle.purgePermission], actor || SEED.actor); n++;
    }
    return n;
  });
}
/* the write path of the customer entity's generic editor (lib/entity.js WRITERS) */
function through(removing, key, row, id, writeRow) {
  try {
    return K.internal.tx(() => {
      declare();
      if (removing) { const r = db().get("SELECT uid FROM users WHERE id=?", Number(id)), uid = nodeOf(r); if (uid) LC.archive(uid, SEED.actor); return writeRow(); }
      const existing = id != null && db().get("SELECT * FROM users WHERE id=?", Number(id));
      if (existing) { const uid = nodeOf(existing) || importRow(existing, SEED.actor); const f = factsOf(row || {}); if (Object.keys(f).length) K.record(uid, f, {}, SEED.actor); if (row && row.role !== undefined) placeRole(uid, row.role, SEED.actor); }
      const out = writeRow();
      if (!existing && out && !out.error) { const r = db().get("SELECT * FROM users WHERE id=?", Number(out.id)); if (r && !nodeOf(r)) importRow(r, SEED.actor); }
      return out;
    });
  } catch (e) { if (e.status === 400) return { error: e.message }; throw e; }
}
/* accounts the kernel has never seen; a warm pass writes nothing */
function importRows() {
  return K.internal.tx(() => {
    declare();
    let n = 0;
    for (const r of db().all("SELECT * FROM users ORDER BY id")) if (!nodeOf(r)) { importRow(r, SEED.importActor); n++; }
    return n;
  });
}
/* who a person was at an instant, and the role they played */
function at(userId, o) {
  const row = db().get("SELECT uid FROM users WHERE id=?", Number(userId)), uid = nodeOf(row);
  if (!uid) return null;
  const roles = K.parents(SEED.hierarchy, uid, { namespace: "platform", at: o && o.at }).map(t => require("./platform-master.js").keyOf(t));
  return { uid, ...(K.attributes(uid, o) || {}), roles };
}
module.exports = { declare, created, set, remove, erase, through, importRows, at, SEED };
