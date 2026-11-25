/* LUXORA Platform — an item's own count, and its variant's: the catalog's columns, changed only here.
   Lowering is one conditional write per row, so a count never goes below zero however many shoppers
   ask at once; the caller (lib/stock.js) runs it inside its transaction. */
"use strict";

const db = () => require("./db.js");

/* false when there is not enough; the caller's transaction then takes back what was lowered */
function lower(tid, productId, skuId, qty) {
  const D = db();
  if (skuId && !D.run("UPDATE skus SET stock=stock-? WHERE id=? AND tenant_id=? AND stock>=?", qty, skuId, tid, qty).changes) return false;
  return !!D.run("UPDATE products SET stock=stock-? WHERE tenant_id=? AND id=? AND stock>=?", qty, tid, productId, qty).changes;
}
function raise(tid, productId, skuId, qty) {
  const D = db();
  D.run("UPDATE products SET stock=stock+? WHERE tenant_id=? AND id=?", qty, tid, productId);
  if (skuId) D.run("UPDATE skus SET stock=stock+? WHERE id=? AND tenant_id=?", qty, skuId, tid);
}
function writeOff(tid, productId, skuId, qty) {
  const D = db();
  D.run("UPDATE products SET stock=CASE WHEN stock>? THEN stock-? ELSE 0 END WHERE tenant_id=? AND id=?", qty, qty, tid, productId);
  if (skuId) D.run("UPDATE skus SET stock=CASE WHEN stock>? THEN stock-? ELSE 0 END WHERE id=? AND tenant_id=?", qty, qty, skuId, tid);
}
module.exports = { writeOff, lower, raise };
