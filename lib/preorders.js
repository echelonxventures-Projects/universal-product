/* LUXORA Platform — pre-orders: selling an item before it can be sent.

   An item on pre-order has the day it ships and how many may be promised. Until that day it is
   bought from the promise, not from the shelf (lib/stock.js asks here first), the shopper is shown
   the date before they pay, and the order keeps it. When the day comes it sells from the shelf.
   Capability: preorders. */
"use strict";

const db = () => require("./db.js");
const caps = () => require("./capabilities.js");
const fail = (msg, status) => Object.assign(new Error(msg), { status: status || 400 });
/* asked for every item listed: remembered for a moment per store */
const SEEN = new Map();
function on(tid) {
  const t = Number(tid), h = SEEN.get(t);
  if (h && Date.now() - h.at < 1000) return h.v;
  const v = caps().on(t, "preorders"); SEEN.set(t, { at: Date.now(), v }); return v;
}
const today = () => new Date().toISOString().slice(0, 10);
const list = tid => db().all("SELECT r.*, p.title FROM preorders r JOIN products p ON p.tenant_id=r.tenant_id AND p.id=r.product_id WHERE r.tenant_id=? ORDER BY r.ships_on", Number(tid)).map(r => ({ ...r, left: Math.max(0, r.max_qty - r.taken), open: r.ships_on > today() }));
function save(tid, input) {
  if (!on(tid)) throw fail("Pre-orders are not available in this store", 403);
  const i = input || {}, day = String(i.ships_on || ""), max = Math.floor(Number(i.max_qty));
  if (!db().get("SELECT 1 x FROM products WHERE tenant_id=? AND id=? AND deleted_at IS NULL", Number(tid), String(i.product_id || ""))) throw fail("Unknown product", 404);
  if (!/^\d{4}-\d\d-\d\d$/.test(day) || isNaN(Date.parse(day)) || day <= today()) throw fail("Give the day it ships, in the future");
  if (!(max > 0)) throw fail("Say how many may be promised");
  db().run("INSERT INTO preorders(tenant_id,product_id,ships_on,max_qty) VALUES(?,?,?,?) ON CONFLICT(tenant_id,product_id) DO UPDATE SET ships_on=excluded.ships_on, max_qty=excluded.max_qty", Number(tid), String(i.product_id), day, max);
  return list(tid);
}
function remove(tid, productId) { if (!db().run("DELETE FROM preorders WHERE tenant_id=? AND product_id=?", Number(tid), String(productId)).changes) throw fail("Not on pre-order", 404); return list(tid); }
/* the open promise on an item, or null */
function open(tid, productId) {
  if (!on(tid)) return null;
  const r = db().get("SELECT * FROM preorders WHERE tenant_id=? AND product_id=? AND ships_on>?", Number(tid), String(productId), today());
  return r ? { ships_on: r.ships_on, left: Math.max(0, r.max_qty - r.taken) } : null;
}
/* promised: one conditional write, never past the most allowed */
const promise = (tid, productId, qty) => !!db().run("UPDATE preorders SET taken=taken+? WHERE tenant_id=? AND product_id=? AND ships_on>? AND taken+?<=max_qty", qty, Number(tid), String(productId), today(), qty).changes;
const giveBack = (tid, productId, qty) => db().run("UPDATE preorders SET taken=CASE WHEN taken>? THEN taken-? ELSE 0 END WHERE tenant_id=? AND product_id=?", qty, qty, Number(tid), String(productId));
module.exports = { on, list, save, remove, open, promise, giveBack };
