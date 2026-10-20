/* LUXORA Platform — Product options: modifiers, add-ons and personalisation.
   An option group (a size, a crust, extra toppings, an engraving) is defined once and attached
   to any number of products. A group either offers values to choose from — each with its own
   price change — or takes the shopper's own text; what a kind of group does is its optionKinds
   registry row (`takes_text`). How many values a shopper must or may choose are the group's
   min and max. The shopper's choice rides on the bag line as its `options` term
   (lib/lineterms.js), adds its price changes to the line, and is kept on the order line, so a
   meal, a made-to-order item or a personalised gift is one product with options — not a
   product per combination. Capability: product_options. */
"use strict";

const db = () => require("./db.js");
const caps = () => require("./capabilities.js");
const reg = () => require("./parity-registries.js");
const lineterms = require("./lineterms.js");
const fail = lineterms.fail;

const rows = name => reg().list(name).map(x => (typeof x === "string" ? { key: x, name: x } : x)).filter(x => x && x.key);
const kindOf = key => rows("optionKinds").find(r => r.key === String(key == null ? "" : key)) || null;
const CODE_RE = /^[a-z0-9][a-z0-9_-]{0,39}$/;
const num = (v, d) => (v === "" || v == null || !isFinite(Number(v)) ? d : Number(v));

function params(tid) {
  const P = caps().cap(tid, "product_options");
  if (!Object.keys(P).length) throw fail("Product options are not available in this store", 403);
  return P;
}

/* ---------- groups and their values ---------- */
function present(g) {
  const values = db().all("SELECT * FROM option_values WHERE group_id=? ORDER BY position, id", g.id);
  return { ...g, kind_row: kindOf(g.kind), values };
}
function groups(tid) { return db().all("SELECT * FROM option_groups WHERE tenant_id=? ORDER BY position, name", Number(tid)).map(present); }
function saveGroup(tid, input) {
  const P = params(tid);
  const i = input || {};
  const D = db();
  const code = String(i.code || "").trim().toLowerCase();
  if (!CODE_RE.test(code)) throw fail("A group needs a short code: lowercase letters, digits, - or _");
  const name = String(i.name || "").trim().slice(0, 80);
  if (!name) throw fail("A group needs a name");
  const kind = kindOf(i.kind) || rows("optionKinds").find(r => r.default) || rows("optionKinds")[0];
  if (!kind) throw fail("No kinds of option group are configured");
  const minSel = Math.max(0, Math.floor(num(i.min_select, 0)));
  const maxSel = Math.max(minSel || 1, Math.floor(num(i.max_select, 1)));
  const maxLen = Math.max(1, Math.min(500, Math.floor(num(i.max_length, P.max_text_length))));
  const clash = D.get("SELECT id FROM option_groups WHERE tenant_id=? AND code=?", Number(tid), code);
  let id = Number(i.id) || null;
  if (id && !D.get("SELECT id FROM option_groups WHERE id=? AND tenant_id=?", id, Number(tid))) throw fail("Option group not found", 404);
  if (clash && clash.id !== id) throw fail("Another group already uses the code " + code, 409);
  const vals = [name, kind.key, minSel, maxSel, maxLen, Math.floor(num(i.position, 0)), i.active === false || i.active === 0 ? 0 : 1];
  if (id) D.run("UPDATE option_groups SET code=?, name=?, kind=?, min_select=?, max_select=?, max_length=?, position=?, active=? WHERE id=?", code, ...vals, id);
  else id = Number(D.run("INSERT INTO option_groups(tenant_id,code,name,kind,min_select,max_select,max_length,position,active) VALUES(?,?,?,?,?,?,?,?,?)", Number(tid), code, ...vals).lastInsertRowid);
  /* values are upserted by code; a value left out is switched off (orders that chose it keep its name) */
  if (Array.isArray(i.values) && !kind.takes_text) {
    const seen = new Set();
    i.values.forEach((v, pos) => {
      const vc = String(v.code || "").trim().toLowerCase();
      if (!CODE_RE.test(vc)) throw fail("Each value needs a short code: lowercase letters, digits, - or _");
      if (seen.has(vc)) throw fail("Two values use the code " + vc);
      seen.add(vc);
      const vn = String(v.name || "").trim().slice(0, 80) || vc;
      const delta = +num(v.price_delta, 0).toFixed(4);
      const ex = D.get("SELECT id FROM option_values WHERE group_id=? AND code=?", id, vc);
      if (ex) D.run("UPDATE option_values SET name=?, price_delta=?, position=?, active=1 WHERE id=?", vn, delta, pos, ex.id);
      else D.run("INSERT INTO option_values(tenant_id,group_id,code,name,price_delta,position,active) VALUES(?,?,?,?,?,?,1)", Number(tid), id, vc, vn, delta, pos);
    });
    for (const v of D.all("SELECT id, code FROM option_values WHERE group_id=?", id)) if (!seen.has(v.code)) D.run("UPDATE option_values SET active=0 WHERE id=?", v.id);
  }
  return present(D.get("SELECT * FROM option_groups WHERE id=?", id));
}
function removeGroup(tid, id) {
  params(tid);
  const D = db();
  const g = D.get("SELECT * FROM option_groups WHERE id=? AND tenant_id=?", Number(id), Number(tid));
  if (!g) throw fail("Option group not found", 404);
  D.run("DELETE FROM product_option_groups WHERE tenant_id=? AND group_id=?", Number(tid), g.id);
  D.run("DELETE FROM option_values WHERE group_id=?", g.id);
  D.run("DELETE FROM option_groups WHERE id=?", g.id);
  return { ok: true };
}
/* which groups a product offers, in order — replacing what it had */
function attach(tid, productId, groupIds) {
  params(tid);
  const D = db();
  if (!D.get("SELECT id FROM products WHERE tenant_id=? AND id=?", Number(tid), String(productId))) throw fail("Unknown product", 404);
  const ids = (Array.isArray(groupIds) ? groupIds : []).map(Number).filter(Boolean);
  for (const gid of ids) if (!D.get("SELECT id FROM option_groups WHERE id=? AND tenant_id=?", gid, Number(tid))) throw fail("Unknown option group " + gid, 404);
  D.run("DELETE FROM product_option_groups WHERE tenant_id=? AND product_id=?", Number(tid), String(productId));
  ids.forEach((gid, pos) => D.run("INSERT INTO product_option_groups(tenant_id,product_id,group_id,position) VALUES(?,?,?,?)", Number(tid), String(productId), gid, pos));
  return forProduct(tid, productId, true);
}
/* what the product page offers: the attached, active groups and their active values */
function forProduct(tid, productId, all) {
  if (!caps().on(tid, "product_options")) return [];
  return db().all("SELECT g.* FROM product_option_groups pg JOIN option_groups g ON g.id=pg.group_id WHERE pg.tenant_id=? AND pg.product_id=?" + (all ? "" : " AND g.active=1") + " ORDER BY pg.position",
    Number(tid), String(productId)).map(present).map(g => ({ ...g, values: all ? g.values : g.values.filter(v => v.active) }));
}
function attachedTo(tid) {
  return db().all("SELECT pg.product_id, pg.group_id, p.title FROM product_option_groups pg LEFT JOIN products p ON p.tenant_id=pg.tenant_id AND p.id=pg.product_id WHERE pg.tenant_id=? ORDER BY pg.product_id, pg.position", Number(tid));
}

/* ---------- the line term ---------- */
/* a choice: { <group code>: [<value code>…] } for a list, or { <group code>: "<text>" } */
function cleanChoice(ctx, value) {
  const P = params(ctx.tid);
  const offered = forProduct(ctx.tid, ctx.product.id);
  const v = value && typeof value === "object" && !Array.isArray(value) ? value : {};
  for (const k of Object.keys(v)) if (!offered.some(g => g.code === k)) throw fail("This product has no option " + k);
  const out = {};
  for (const g of offered) {
    const raw = v[g.code];
    if (g.kind_row && g.kind_row.takes_text) {
      const t = String(raw == null ? "" : raw).replace(/[\u0000-\u001F]/g, "").trim();
      if (!t) { if (g.min_select > 0) throw fail(g.name + " is required"); continue; }
      const max = Math.min(Number(g.max_length) || Number(P.max_text_length), Number(P.max_text_length) || 500);
      if (t.length > max) throw fail(g.name + ": at most " + max + " characters");
      out[g.code] = t;
      continue;
    }
    const picks = [...new Set((Array.isArray(raw) ? raw : raw == null || raw === "" ? [] : [raw]).map(String))];
    for (const c of picks) if (!g.values.some(x => x.code === c)) throw fail(g.name + ": no choice " + c);
    if (picks.length < g.min_select) throw fail(g.name + ": choose " + (g.min_select === 1 ? "one" : "at least " + g.min_select));
    if (picks.length > g.max_select) throw fail(g.name + ": choose at most " + g.max_select);
    if (picks.length) out[g.code] = picks;
  }
  for (const g of offered) if (g.min_select > 0 && out[g.code] == null) throw fail(g.name + " is required");
  return Object.keys(out).length ? out : null;
}
function priceChoice(ctx, value) {
  const offered = forProduct(ctx.tid, ctx.product.id, true);
  let add = 0;
  const parts = [];
  for (const [code, picked] of Object.entries(value || {})) {
    const g = offered.find(x => x.code === code);
    if (!g) throw fail("an option on this line was withdrawn");
    if (typeof picked === "string") { parts.push(g.name + ": “" + picked + "”"); continue; }
    const names = [];
    for (const c of picked) {
      const val = g.values.find(x => x.code === c);
      if (!val || !val.active) throw fail(g.name + ": " + c + " is no longer offered");
      add += Number(val.price_delta) || 0;
      names.push(val.name);
    }
    parts.push(g.name + ": " + names.join(", "));
  }
  return { add, label: parts.join(" · ") };
}
lineterms.register("options", { atom: "product_options", clean: cleanChoice, price: priceChoice });

function vocabulary() { return { kinds: rows("optionKinds") }; }

module.exports = { groups, saveGroup, removeGroup, attach, forProduct, attachedTo, vocabulary };
