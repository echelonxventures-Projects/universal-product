/* LUXORA Platform — orders on the kernel (P24, owner Commerce).

   Every order is a node of the commerce.order kind in its store's namespace (lib/seed/order-records.json),
   whose universal ID is its orders row's. What makes the deal — number, status, amounts, currency,
   why it was cancelled, when it was delivered — are versions of that node, so an order's status
   history is answerable at any instant. Its lines are recorded as they stood at checkout (the
   offering bought, how many, at what price), and the person who placed it is a relationship in the
   commerce.buyers hierarchy. The buyer's name, address and email are not copied: an order is kept
   for the law, its personal data stays in the orders table under the store's retention.

   Every write of an order's status goes through change(): the row and the record in one
   transaction. Money, stock and the status machine itself stay where they are (lib/orders.js). */
"use strict";

const db = () => require("./db.js");
const K = require("./kernel.js");
const LC = require("./kernel-lifecycle.js");
const SEED = require("./seed/order-records.json");
const NS = tid => require("./master-permissions.js").storeHolder(tid);
const H = SEED.hierarchy.hierarchy;
const FACTS = Object.entries(SEED.facts);
const S = () => K.SEED.lifecycle.nodeStates;
const refused = out => !!out && typeof out === "object" && Object.prototype.hasOwnProperty.call(out, "error") && !!out.error;

let declared = false;
function declare() {
  if (declared) return;
  K.ensureTables(); LC.ensureTables(); require("./parties.js").declare();
  const k = K.kindOf(SEED.kind.kind, "platform");
  if (!k || k.attributes.length !== SEED.kind.attributes.length) K.defineKind({ ...SEED.kind, namespace: "platform" }, SEED.actor);
  if (!K.hierarchyOf(H, "platform")) K.defineHierarchy({ ...SEED.hierarchy, namespace: "platform" }, SEED.actor);
  declared = true;
}
function factsOf(row) {
  const out = {};
  for (const [k, type] of FACTS) { const v = row[k]; if (v === undefined || v === null || v === "") continue; out[k] = type === "number" ? Number(v) : String(v); }
  if (!out.num) out.num = String(row.id);
  return out;
}
const nodeOf = row => (row && row.uid && K.internal.nodeRow(row.uid)) ? row.uid : null;
/* what was bought: each line's offering (the product's node), how many and at what price */
function linesOf(orderId) {
  return db().all("SELECT i.product_id, i.qty, i.price, p.uid FROM order_items i LEFT JOIN products p ON p.id=i.product_id AND p.tenant_id=(SELECT tenant_id FROM orders WHERE id=?) WHERE i.order_id=? ORDER BY i.rowid", Number(orderId), Number(orderId))
    .map(l => ({ offering: l.uid || null, product: String(l.product_id), qty: Number(l.qty), price: Number(l.price) }));
}
/* the person behind an order's owner ("t1:u:5"); a guest has none */
function buyerOf(row) {
  const m = /:u:(\d+)$/.exec(String(row.owner || ""));
  const u = m && db().get("SELECT uid FROM users WHERE id=? AND tenant_id=?", Number(m[1]), Number(row.tenant_id));
  return u && u.uid && K.internal.nodeRow(u.uid) ? u.uid : null;
}
function record(row, actor) {
  let uid = nodeOf(row);
  const f = factsOf(row);
  if (!uid) {
    uid = K.createNode(SEED.kind.kind, { namespace: NS(row.tenant_id), uid: row.uid && !K.internal.nodeRow(row.uid) ? row.uid : undefined, attributes: { ...f, lines: linesOf(row.id) } }, actor);
    if (row.uid !== uid) db().run("UPDATE orders SET uid=? WHERE id=?", uid, row.id);
    const who = buyerOf(row);
    if (who) K.place(H, uid, who, { namespace: "platform" }, actor);
  } else {
    const cur = K.attributes(uid) || {};
    const diff = Object.fromEntries(Object.entries(f).filter(([k, v]) => cur[k] !== v));
    if (!(cur.lines || []).length) { const l = linesOf(row.id); if (l.length) diff.lines = l; }
    if (Object.keys(diff).length) K.record(uid, diff, {}, actor);
  }
  return uid;
}
/* every write of an order: the row and its record in one transaction */
function change(ids, writeRow, actor) {
  return K.internal.tx(() => {
    declare();
    const out = writeRow();
    if (refused(out)) return out;
    for (const id of [].concat(ids)) { const row = db().get("SELECT * FROM orders WHERE id=?", Number(id)); if (row) record(row, actor || SEED.actor); }
    return out;
  });
}
/* an order about to be deleted (one refused at checkout): its record is archived */
function removing(id, actor) {
  declare();
  const uid = nodeOf(db().get("SELECT uid FROM orders WHERE id=?", Number(id)));
  if (uid && LC.nodeState(uid) !== S().archived) LC.archive(uid, actor || SEED.actor);
}
function importRows() {
  return K.internal.tx(() => {
    declare();
    let n = 0;
    for (const r of db().all("SELECT * FROM orders ORDER BY id")) if (!nodeOf(r)) { record(r, SEED.importActor); n++; }
    return n;
  });
}
function at(id, o) {
  const uid = nodeOf(db().get("SELECT uid FROM orders WHERE id=?", Number(id)));
  if (!uid) return null;
  return { uid, ...(K.attributes(uid, o) || {}), buyer: K.parents(H, uid, { namespace: "platform", at: o && o.at })[0] || null };
}
/* the statuses an order has been through, oldest first */
function statusHistory(id) {
  const uid = nodeOf(db().get("SELECT uid FROM orders WHERE id=?", Number(id)));
  if (!uid) return [];
  const out = [];
  for (const v of K.history(uid).filter(x => x.recordedTo == null)) if (!out.length || out[out.length - 1].status !== v.attributes.status) out.push({ from: v.validFrom, status: v.attributes.status });
  return out;
}
/* the orders a person has placed */
const ordersOf = personUid => { declare(); return K.children(H, personUid, { namespace: "platform" }); };
module.exports = { declare, change, removing, importRows, at, statusHistory, ordersOf, record, SEED };
