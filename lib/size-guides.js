/* LUXORA Platform — size guides: the table of measurements that helps a shopper choose a size.

   A guide is a table for an item, a brand or a department; an item shows the one that names it, else
   its brand's, else its department's. Capability: size_guides. */
"use strict";

const db = () => require("./db.js");
const caps = () => require("./capabilities.js");
const fail = (msg, status) => Object.assign(new Error(msg), { status: status || 400 });
const J = v => { try { return JSON.parse(v || "[]"); } catch (e) { return []; } };
const on = tid => caps().on(Number(tid), "size_guides");
/* what a guide may be for, most particular first, and the item's column it is matched on */
const FOR = [["item", "id"], ["brand", "brand"], ["dept", "dept"]];
const present = g => ({ ...g, rows: J(g.rows) });
const list = tid => db().all("SELECT * FROM size_guides WHERE tenant_id=? ORDER BY name", Number(tid)).map(present);
/* rows typed as lines of comma-separated cells; the first is the heading, and every row is as wide */
function parse(text) {
  const rows = String(text || "").split(/\r?\n/).map(l => l.split(",").map(c => c.trim().slice(0, 40))).filter(r => r.some(Boolean));
  if (rows.length < 2) throw fail("A guide needs a heading row and at least one size");
  if (rows.length > 60 || rows[0].length > 12) throw fail("A guide is at most 60 rows of 12 columns");
  if (rows.some(r => r.length !== rows[0].length)) throw fail("Every row needs the same number of columns as the heading");
  return rows;
}
function save(tid, input) {
  if (!on(tid)) throw fail("Size guides are not available in this store", 403);
  const i = input || {}, name = String(i.name || "").trim().slice(0, 80), scope = FOR.find(f => f[0] === i.scope), target = String(i.target || "").trim().slice(0, 80);
  if (!name) throw fail("A guide needs a name");
  if (!scope || !target) throw fail("Say which item, brand or department the guide is for");
  const rows = JSON.stringify(Array.isArray(i.rows) ? parse(i.rows.map(r => r.join(",")).join("\n")) : parse(i.rows)), note = String(i.note || "").trim().slice(0, 500);
  if (i.id) { if (!db().run("UPDATE size_guides SET name=?,scope=?,target=?,rows=?,note=? WHERE id=? AND tenant_id=?", name, scope[0], target, rows, note, Number(i.id), Number(tid)).changes) throw fail("Guide not found", 404); }
  else db().run("INSERT INTO size_guides(name,scope,target,rows,note,tenant_id) VALUES(?,?,?,?,?,?)", name, scope[0], target, rows, note, Number(tid));
  return list(tid);
}
function remove(tid, id) { if (!db().run("DELETE FROM size_guides WHERE id=? AND tenant_id=?", Number(id), Number(tid)).changes) throw fail("Guide not found", 404); return list(tid); }
function forProduct(tid, productId) {
  if (!on(tid)) return null;
  const p = db().get("SELECT id, brand, dept FROM products WHERE tenant_id=? AND id=?", Number(tid), String(productId));
  if (!p) return null;
  for (const [scope, col] of FOR) { const g = db().get("SELECT * FROM size_guides WHERE tenant_id=? AND scope=? AND lower(target)=lower(?) ORDER BY id DESC LIMIT 1", Number(tid), scope, String(p[col] || "")); if (g) { const x = present(g); return { name: x.name, rows: x.rows, note: x.note }; } }
  return null;
}
module.exports = { on, list, save, remove, forProduct, SCOPES: FOR.map(f => f[0]) };
