/* LUXORA Platform — what a store offers, on the kernel (P24, owner Offering).

   Every product of a store is an offering: a node of the offering.listing kind in the store's
   namespace (lib/seed/offerings.json) whose universal ID is its products row's. What makes the
   offer — its title, brand, department, kind, price, list price and lifecycle — are versions of
   that node, so a product's price history is answerable at any instant. A product removed (soft
   deleted) is hidden, one deleted outright archived; history stays either way.

   Every write of a product goes through change(): the row is written and the offering recorded in
   one transaction, so neither holds without the other. Stock counts and display details are not
   the offer and are not recorded. The boot pass only imports products the kernel has never seen. */
"use strict";

const db = () => require("./db.js");
const K = require("./kernel.js");
const LC = require("./kernel-lifecycle.js");
const SEED = require("./seed/offerings.json");
const NS = tid => require("./master-permissions.js").storeHolder(tid);
const FACTS = Object.entries(SEED.facts);
const S = () => K.SEED.lifecycle.nodeStates;

let declared = false;
function declare() {
  if (declared) return;
  K.ensureTables(); LC.ensureTables();
  const k = K.kindOf(SEED.kind.kind, "platform");
  if (!k || k.attributes.length !== SEED.kind.attributes.length) K.defineKind({ ...SEED.kind, namespace: "platform" }, SEED.actor);
  declared = true;
}
/* the offer's facts from a products row */
function factsOf(row) {
  const out = {};
  for (const [k, type] of FACTS) {
    const v = row[k];
    if (v === undefined || v === null || v === "") continue;
    out[k] = type === "number" ? Number(v) : String(v);
  }
  if (!out.title) out.title = String(row.id);
  return out;
}
/* did a write refuse? Only its own error field says so (a write may return anything, even a module) */
const refused = out => !!out && typeof out === "object" && Object.prototype.hasOwnProperty.call(out, "error") && !!out.error;
const nodeOf = row => (row && row.uid && K.internal.nodeRow(row.uid)) ? row.uid : null;
function setListed(uid, on, actor) {
  const st = LC.nodeState(uid);
  if (on && st === S().hidden) LC.unhide(uid, actor);
  if (!on && st === S().initial) LC.hide(uid, actor);
}
/* the kernel follows the row: created when new, a version where a fact changed, hidden while removed */
function record(row, actor) {
  let uid = nodeOf(row);
  const f = factsOf(row);
  if (!uid) {
    uid = K.createNode(SEED.kind.kind, { namespace: NS(row.tenant_id), uid: row.uid && !K.internal.nodeRow(row.uid) ? row.uid : undefined, attributes: f }, actor);
    if (row.uid !== uid) db().run("UPDATE products SET uid=? WHERE tenant_id=? AND id=?", uid, row.tenant_id, row.id);
  } else {
    const cur = K.attributes(uid) || {};
    const diff = Object.fromEntries(Object.entries(f).filter(([k, v]) => cur[k] !== v));
    for (const [k] of FACTS) if (cur[k] !== undefined && f[k] === undefined) diff[k] = null;
    if (Object.keys(diff).length) K.record(uid, diff, {}, actor);
  }
  setListed(uid, !row.deleted_at, actor);
  return uid;
}
/* every write of a product: the row and its offering in one transaction */
function change(tid, id, writeRow, actor) {
  return K.internal.tx(() => {
    declare();
    const out = writeRow();
    if (refused(out)) return out;
    const ids = [].concat(id);
    for (const one of ids) { const row = db().get("SELECT * FROM products WHERE tenant_id=? AND id=?", Number(tid), String(one)); if (row) record(row, actor || SEED.actor); }
    return out;
  });
}
/* products about to be deleted outright: their offerings are archived first, so history stays */
function removing(tid, where, args, actor) {
  declare();
  for (const r of db().all(`SELECT uid FROM products WHERE tenant_id=? AND ${where}`, Number(tid), ...(args || []))) {
    const uid = nodeOf(r);
    if (uid && LC.nodeState(uid) !== S().archived) LC.archive(uid, actor || SEED.actor);
  }
}
/* the write path of the product entity's generic editor (lib/entity.js WRITERS) */
function through(isRemoving, key, row, id, writeRow) {
  try {
    return K.internal.tx(() => {
      declare();
      const tid = row && row.tenant_id != null ? row.tenant_id : (db().get("SELECT tenant_id FROM products WHERE id=?", String(id)) || {}).tenant_id;
      if (isRemoving) { if (tid != null) removing(tid, "id=?", [String(id)]); return writeRow(); }
      const out = writeRow();
      const pid = id != null ? id : out && out.id;
      const r = pid != null && db().get("SELECT * FROM products WHERE id=?" + (tid != null ? " AND tenant_id=?" : ""), String(pid), ...(tid != null ? [tid] : []));
      if (r && !refused(out)) record(r, SEED.actor);
      return out;
    });
  } catch (e) { if (e.status === 400) return { error: e.message }; throw e; }
}
/* products the kernel has never seen; a warm pass writes nothing */
function importRows() {
  return K.internal.tx(() => {
    declare();
    let n = 0;
    for (const r of db().all("SELECT * FROM products ORDER BY tenant_id, id")) if (!nodeOf(r)) { record(r, SEED.importActor); n++; }
    return n;
  });
}
/* an offering as it stood at an instant: its facts, and whether it was on sale */
function at(tid, id, o) {
  const r = db().get("SELECT uid FROM products WHERE tenant_id=? AND id=?", Number(tid), String(id)), uid = nodeOf(r);
  return uid ? { uid, listed: LC.nodeState(uid) === S().initial, ...(K.attributes(uid, o) || {}) } : null;
}
/* the prices an offering has had, oldest first */
function priceHistory(tid, id) {
  const r = db().get("SELECT uid FROM products WHERE tenant_id=? AND id=?", Number(tid), String(id)), uid = nodeOf(r);
  if (!uid) return [];
  return K.history(uid).filter(v => v.recordedTo == null).map(v => ({ from: v.validFrom, to: v.validTo, price: v.attributes.price, list_price: v.attributes.list_price }));
}
module.exports = { declare, change, removing, through, importRows, at, priceHistory, SEED };
