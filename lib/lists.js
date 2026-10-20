/* LUXORA Platform — Shopper lists: wish lists, shopping lists, idea lists.
   A signed-in shopper keeps any number of named lists of products. What a kind of list IS
   (its starting visibility, whether people it is shared with may mark a gift bought) and what
   a visibility MEANS (reachable by its link? listed for anyone to find?) are rows of the
   listKinds and listVisibilities registries, so a new kind of list — a baby list, a classroom
   list — is a Data Studio row, never code. How many lists and items a shopper may keep, and
   whether sharing or public lists are allowed at all, are the wish_lists capability's params.
   Gift registries (an event, a date, a shipping address) keep their own engine; a list is the
   lighter, everyday shape. */
"use strict";

const crypto = require("crypto");
const db = () => require("./db.js");
const caps = () => require("./capabilities.js");
const reg = () => require("./parity-registries.js");
const fail = (msg, status) => Object.assign(new Error(msg), { status: status || 400 });

/* a registry as object rows, a row by key, and its flagged default */
const rows = name => reg().list(name).map(x => (typeof x === "string" ? { key: x, name: x } : x)).filter(x => x && x.key);
const rowOf = (name, key) => rows(name).find(r => r.key === String(key == null ? "" : key)) || null;
const firstOf = name => { const r = rows(name); return r.find(x => x.default) || r[0] || null; };

function params(tid) {
  const P = caps().cap(tid, "wish_lists");
  if (!Object.keys(P).length) throw fail("Lists are not available in this store", 403);
  return P;
}
/* the visibility a shopper asked for, if this store allows it */
function visibilityFor(P, want, kind) {
  const v = rowOf("listVisibilities", want) || rowOf("listVisibilities", kind && kind.default_visibility) || firstOf("listVisibilities");
  if (!v) throw fail("No list visibilities are configured");
  if (v.shared && !P.allow_sharing) throw fail("Sharing lists is turned off in this store", 403);
  if (v.listed && !P.allow_public) throw fail("Public lists are turned off in this store", 403);
  return v;
}
const product = (tid, id) => db().get("SELECT * FROM products WHERE tenant_id=? AND id=? AND lifecycle='published' AND deleted_at IS NULL", Number(tid), String(id || ""));
const ownList = (tid, owner, id) => {
  const l = db().get("SELECT * FROM shopper_lists WHERE id=? AND tenant_id=? AND owner=?", Number(id), Number(tid), String(owner));
  if (!l) throw fail("List not found", 404);
  return l;
};
/* what a viewer sees of a list: its kind's and visibility's own rows ride along, so the page
   renders labels and decides what a viewer may do from the registry, never from a name */
function view(l, withItems, forOwner) {
  const D = db();
  const out = { id: l.id, name: l.name, kind: rowOf("listKinds", l.kind) || { key: l.kind, name: l.kind }, visibility: rowOf("listVisibilities", l.visibility) || { key: l.visibility, name: l.visibility },
    by: l.owner_name || "", created_at: l.created_at, updated_at: l.updated_at,
    count: D.get("SELECT COUNT(*) c FROM shopper_list_items WHERE list_id=?", l.id).c };
  if (forOwner) Object.assign(out, { token: l.token, notes: l.notes });
  if (withItems) out.items = itemsOf(l);
  return out;
}
function itemsOf(l) {
  const ranks = Object.fromEntries(rows("listPriorities").map(r => [r.key, Number(r.rank) || 0]));
  return db().all("SELECT * FROM shopper_list_items WHERE list_id=? ORDER BY added_at", l.id).map(it => {
    const p = product(l.tenant_id, it.product_id);
    return { id: it.id, product_id: it.product_id, qty: it.qty, purchased: it.purchased, note: it.note, added_at: it.added_at,
      priority: rowOf("listPriorities", it.priority) || null, rank: ranks[it.priority] || 0,
      price_added: it.price_added, product: p || null };
  }).sort((a, b) => b.rank - a.rank);
}

/* ---------- the owner's lists ---------- */
function mine(tid, owner) {
  params(tid);
  return db().all("SELECT * FROM shopper_lists WHERE tenant_id=? AND owner=? ORDER BY id", Number(tid), String(owner)).map(l => view(l, false, true));
}
function create(tid, owner, ownerName, input) {
  const P = params(tid);
  const i = input || {};
  const name = String(i.name || "").trim().slice(0, 80);
  if (!name) throw fail("A list needs a name");
  const n = db().get("SELECT COUNT(*) c FROM shopper_lists WHERE tenant_id=? AND owner=?", Number(tid), String(owner)).c;
  if (n >= Number(P.max_lists)) throw fail("You can keep up to " + P.max_lists + " lists");
  const kind = rowOf("listKinds", i.kind) || firstOf("listKinds");
  if (!kind) throw fail("No kinds of list are configured");
  const vis = visibilityFor(P, i.visibility, kind);
  const r = db().run("INSERT INTO shopper_lists(tenant_id,owner,owner_name,kind,name,visibility,token,notes) VALUES(?,?,?,?,?,?,?,?)",
    Number(tid), String(owner), String(ownerName || "").slice(0, 80), kind.key, name, vis.key, crypto.randomBytes(16).toString("hex"), String(i.notes || "").slice(0, 500));
  return get(tid, owner, r.lastInsertRowid);
}
function update(tid, owner, id, patch) {
  const P = params(tid);
  const l = ownList(tid, owner, id);
  const p = patch || {};
  const name = p.name != null ? String(p.name).trim().slice(0, 80) : l.name;
  if (!name) throw fail("A list needs a name");
  const vis = p.visibility != null ? visibilityFor(P, p.visibility, null).key : l.visibility;
  /* a new link: whoever held the old one loses access */
  const token = p.new_link ? crypto.randomBytes(16).toString("hex") : l.token;
  db().run("UPDATE shopper_lists SET name=?, visibility=?, notes=?, token=?, updated_at=datetime('now') WHERE id=?",
    name, vis, p.notes != null ? String(p.notes).slice(0, 500) : l.notes, token, l.id);
  return get(tid, owner, l.id);
}
function remove(tid, owner, id) {
  params(tid);
  const l = ownList(tid, owner, id);
  db().run("DELETE FROM shopper_list_items WHERE list_id=?", l.id);
  db().run("DELETE FROM shopper_lists WHERE id=?", l.id);
  return { ok: true };
}
function get(tid, owner, id) { params(tid); return view(ownList(tid, owner, id), true, true); }
/* which of the owner's lists hold this product (the product page's "in your list") */
function holding(tid, owner, productId) {
  if (!caps().on(tid, "wish_lists")) return [];
  return db().all("SELECT l.id, l.name FROM shopper_list_items i JOIN shopper_lists l ON l.id=i.list_id WHERE l.tenant_id=? AND l.owner=? AND i.product_id=?",
    Number(tid), String(owner), String(productId));
}

/* ---------- items ---------- */
function addItem(tid, owner, listId, input) {
  const P = params(tid);
  const l = ownList(tid, owner, listId);
  const i = input || {};
  const p = product(tid, i.product_id);
  if (!p) throw fail("That product is not available", 404);
  const D = db();
  const ex = D.get("SELECT * FROM shopper_list_items WHERE list_id=? AND product_id=?", l.id, p.id);
  const priority = rowOf("listPriorities", i.priority) || (ex ? rowOf("listPriorities", ex.priority) : null) || firstOf("listPriorities");
  const qty = Math.max(1, Math.min(999, Math.floor(Number(i.qty) || (ex ? ex.qty : 1))));
  if (ex) D.run("UPDATE shopper_list_items SET qty=?, priority=?, note=? WHERE id=?", qty, priority ? priority.key : null, i.note != null ? String(i.note).slice(0, 300) : ex.note, ex.id);
  else {
    const n = D.get("SELECT COUNT(*) c FROM shopper_list_items WHERE list_id=?", l.id).c;
    if (n >= Number(P.max_items)) throw fail("A list can hold up to " + P.max_items + " items");
    D.run("INSERT INTO shopper_list_items(tenant_id,list_id,product_id,qty,priority,note,price_added) VALUES(?,?,?,?,?,?,?)",
      Number(tid), l.id, p.id, qty, priority ? priority.key : null, String(i.note || "").slice(0, 300), Number(p.price) || 0);
  }
  D.run("UPDATE shopper_lists SET updated_at=datetime('now') WHERE id=?", l.id);
  return get(tid, owner, l.id);
}
const ownItem = (tid, owner, itemId) => {
  const it = db().get("SELECT i.*, l.owner FROM shopper_list_items i JOIN shopper_lists l ON l.id=i.list_id WHERE i.id=? AND l.tenant_id=? AND l.owner=?", Number(itemId), Number(tid), String(owner));
  if (!it) throw fail("Item not found", 404);
  return it;
};
function updateItem(tid, owner, itemId, patch) {
  params(tid);
  const it = ownItem(tid, owner, itemId);
  const p = patch || {};
  const D = db();
  /* moving to another of the owner's lists: merge into a line already holding the product */
  if (p.list_id != null && Number(p.list_id) !== it.list_id) {
    const to = ownList(tid, owner, p.list_id);
    const there = D.get("SELECT id FROM shopper_list_items WHERE list_id=? AND product_id=?", to.id, it.product_id);
    if (there) D.run("DELETE FROM shopper_list_items WHERE id=?", it.id);
    else D.run("UPDATE shopper_list_items SET list_id=? WHERE id=?", to.id, it.id);
    return get(tid, owner, to.id);
  }
  const priority = p.priority != null ? (rowOf("listPriorities", p.priority) || null) : rowOf("listPriorities", it.priority);
  if (p.priority != null && !priority) throw fail("Unknown priority");
  D.run("UPDATE shopper_list_items SET qty=?, priority=?, note=? WHERE id=?",
    p.qty != null ? Math.max(1, Math.min(999, Math.floor(Number(p.qty) || 1))) : it.qty, priority ? priority.key : null,
    p.note != null ? String(p.note).slice(0, 300) : it.note, it.id);
  return get(tid, owner, it.list_id);
}
function removeItem(tid, owner, itemId) {
  params(tid);
  const it = ownItem(tid, owner, itemId);
  db().run("DELETE FROM shopper_list_items WHERE id=?", it.id);
  return get(tid, owner, it.list_id);
}

/* ---------- lists other people see ---------- */
/* by its link: only a list whose visibility row says it is shared answers */
function shared(tid, token) {
  params(tid);
  const l = db().get("SELECT * FROM shopper_lists WHERE tenant_id=? AND token=?", Number(tid), String(token || ""));
  const vis = l ? rowOf("listVisibilities", l.visibility) : null;
  if (!l || !vis || !vis.shared) throw fail("This list is private or no longer exists", 404);
  return view(l, true, false);
}
/* someone the list is shared with bought a gift: only where the list's kind allows it */
function markPurchased(tid, token, itemId, qty) {
  params(tid);
  const l = db().get("SELECT * FROM shopper_lists WHERE tenant_id=? AND token=?", Number(tid), String(token || ""));
  const vis = l ? rowOf("listVisibilities", l.visibility) : null;
  if (!l || !vis || !vis.shared) throw fail("This list is private or no longer exists", 404);
  const kind = rowOf("listKinds", l.kind);
  if (!kind || !kind.gifting) throw fail("Purchases are not tracked on this kind of list", 403);
  const it = db().get("SELECT * FROM shopper_list_items WHERE id=? AND list_id=?", Number(itemId), l.id);
  if (!it) throw fail("Item not found", 404);
  const n = Math.max(1, Math.floor(Number(qty) || 1));
  db().run("UPDATE shopper_list_items SET purchased=? WHERE id=?", Math.min(it.qty, it.purchased + n), it.id);
  return view(l, true, false);
}
/* lists their owners made findable (a visibility row marked listed) */
function findable(tid, q) {
  params(tid);
  const listed = rows("listVisibilities").filter(v => v.listed).map(v => v.key);
  if (!listed.length) return [];
  const term = "%" + String(q || "").trim().toLowerCase().slice(0, 60) + "%";
  return db().all("SELECT * FROM shopper_lists WHERE tenant_id=? AND visibility IN (" + listed.map(() => "?").join(",") + ") AND (lower(name) LIKE ? OR lower(owner_name) LIKE ?) ORDER BY updated_at DESC, id DESC LIMIT 50",
    Number(tid), ...listed, term, term).map(l => ({ ...view(l, false, false), token: l.token }));
}

/* the vocabulary the storefront renders its pickers from */
function vocabulary() { return { kinds: rows("listKinds"), visibilities: rows("listVisibilities"), priorities: rows("listPriorities") }; }

module.exports = { mine, create, update, remove, get, holding, addItem, updateItem, removeItem, shared, markPurchased, findable, vocabulary };
