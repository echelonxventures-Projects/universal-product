/* LUXORA Platform — Shopper selling: resale, classifieds and peer-to-peer marketplaces.
   Any signed-in shopper may list their own items — new, used, refurbished (the item conditions
   are the mktConditions registry) — with a price, a quantity, photos and a department. A
   listing moves through the `listing` state machine: drafted, reviewed by staff where the store
   says so, then on sale as an ordinary product the whole storefront already sells — search,
   cart, checkout, offers, auctions, messages. The shopper is registered as a seller under the
   role the capability names (a sellerRoles row), so seller health, payouts and the buy-box
   treat them like any seller.

   When an order includes a listed item, the listing counts it sold and the sale's proceeds,
   less the store's commission, are held for the holding period and then credited to the
   seller's wallet (the single wallet ledger, lib/offers.js). Capability: peer_listings. */
"use strict";

const crypto = require("crypto");
const db = () => require("./db.js");
const caps = () => require("./capabilities.js");
const reg = () => require("./parity-registries.js");
const states = require("./states.js");
const lineterms = require("./lineterms.js");
const fail = lineterms.fail;
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };

const keys = name => reg().list(name).map(x => (typeof x === "string" ? x : x.key));
const inTag = tag => { const xs = states.tagged("listing", tag); return { sql: "(" + (xs.length ? xs.map(() => "?").join(",") : "NULL") + ")", args: xs }; };
const sqlNow = () => new Date().toISOString().slice(0, 19).replace("T", " ");

function params(tid) {
  const P = caps().cap(tid, "peer_listings");
  if (!Object.keys(P).length) throw fail("Selling is not available in this store", 403);
  return P;
}
/* who sells a product: the shopper whose listing it is (their owner key), or "" — the store */
function ownerOf(tid, productId) {
  const l = db().get("SELECT owner FROM peer_listings WHERE tenant_id=? AND product_id=? ORDER BY id DESC LIMIT 1", Number(tid), String(productId || ""));
  return l ? l.owner : "";
}

/* ---------- the shopper's own listings ---------- */
function present(l, forOwner) {
  const out = { id: l.id, title: l.title, description: l.description, price: l.price, qty: l.qty, sold: l.sold, condition: l.condition, dept: l.dept,
    images: J(l.images, []), product_id: l.product_id, by: l.owner_name, state: states.display("listing", l.status), status: l.status,
    editable: states.is("listing", l.status, "editable"), on_sale: states.is("listing", l.status, "on_sale"), published_at: l.published_at };
  if (forOwner) Object.assign(out, { review_notes: l.review_notes, next: states.next("listing", l.status) });
  return out;
}
const own = (tid, owner, id) => {
  const l = db().get("SELECT * FROM peer_listings WHERE id=? AND tenant_id=? AND owner=?", Number(id), Number(tid), String(owner));
  if (!l) throw fail("Listing not found", 404);
  return l;
};
/* images are the store's own paths or https on a host the platform allows — as rich content */
function cleanImages(list) {
  const imageField = require("./richcontent.js").FIELD_TYPES.image;
  return (Array.isArray(list) ? list : String(list || "").split(/\r?\n/)).map(x => String(x).trim()).filter(Boolean).slice(0, 8)
    .map(u => imageField(u, { label: "Photo" })).filter(Boolean);
}
function fields(tid, i, cur) {
  const title = i.title != null ? String(i.title).trim().slice(0, 140) : cur.title;
  if (!title) throw fail("A listing needs a title");
  const price = i.price != null ? +Number(i.price).toFixed(2) : cur.price;
  if (!(price > 0)) throw fail("A listing needs a price above zero");
  const qty = i.qty != null ? Math.max(1, Math.min(999, Math.floor(Number(i.qty) || 1))) : cur.qty;
  const condition = i.condition != null ? String(i.condition) : cur.condition;
  if (condition && !keys("mktConditions").includes(condition)) throw fail("Unknown condition " + condition);
  const dept = i.dept != null ? String(i.dept) : cur.dept;
  if (dept && !db().get("SELECT key FROM departments WHERE tenant_id=? AND key=?", Number(tid), dept)) throw fail("Unknown department " + dept);
  return { title, description: i.description != null ? String(i.description).slice(0, 4000) : cur.description, price, qty, condition: condition || null, dept: dept || null,
    images: i.images != null ? JSON.stringify(cleanImages(i.images)) : cur.images };
}
function create(tid, owner, ownerName, input) {
  params(tid);
  const f = fields(tid, input || {}, { images: "[]" });
  const r = db().run("INSERT INTO peer_listings(tenant_id,owner,owner_name,title,description,price,qty,condition,dept,images,status) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
    Number(tid), String(owner), String(ownerName || "").slice(0, 80), f.title, f.description, f.price, f.qty, f.condition, f.dept, f.images, states.initial("listing"));
  return present(db().get("SELECT * FROM peer_listings WHERE id=?", r.lastInsertRowid), true);
}
/* editing: a listing in an editable state takes every field; one on sale takes price and
   quantity at once, and anything else sends it back for review where the store reviews */
function update(tid, owner, id, input) {
  const P = params(tid);
  const l = own(tid, owner, id);
  const i = input || {};
  const f = fields(tid, i, l);
  const D = db();
  const onSale = states.is("listing", l.status, "on_sale");
  if (!states.is("listing", l.status, "editable") && !onSale) throw fail("This listing can no longer be edited", 409);
  const changesWords = ["title", "description", "condition", "dept", "images"].some(k => i[k] != null && String(f[k]) !== String(l[k]));
  D.run("UPDATE peer_listings SET title=?, description=?, price=?, qty=?, condition=?, dept=?, images=?, updated_at=datetime('now') WHERE id=?",
    f.title, f.description, f.price, Math.max(f.qty, l.sold), f.condition, f.dept, f.images, l.id);
  let cur = D.get("SELECT * FROM peer_listings WHERE id=?", l.id);
  if (onSale && changesWords && P.require_review) cur = move(tid, cur, states.actionTarget("listing", "submit"));
  if (states.is("listing", cur.status, "on_sale")) publish(tid, cur);
  return present(D.get("SELECT * FROM peer_listings WHERE id=?", l.id), true);
}
function mine(tid, owner) { params(tid); return db().all("SELECT * FROM peer_listings WHERE tenant_id=? AND owner=? ORDER BY id DESC", Number(tid), String(owner)).map(l => present(l, true)); }

/* ---------- moving a listing ---------- */
function move(tid, l, to) {
  if (!to || !states.can("listing", l.status, to)) throw fail("A listing that is " + states.display("listing", l.status).label + " cannot be moved that way", 409);
  const mv = states.apply("listing", { tenantId: tid, from: l.status, to, row: l });
  const cols = Object.keys(mv.patch);
  db().run("UPDATE peer_listings SET " + cols.map(c => c + "=?").join(", ") + ", updated_at=datetime('now') WHERE id=?", ...cols.map(c => mv.patch[c]), l.id);
  const cur = db().get("SELECT * FROM peer_listings WHERE id=?", l.id);
  if (states.is("listing", to, "on_sale")) publish(tid, cur); else unpublish(tid, cur);
  /* publishing links the listing to its product: answer the row as it now is */
  return db().get("SELECT * FROM peer_listings WHERE id=?", l.id);
}
/* the seller submits: straight on sale where the store reviews nothing; withdraws; reopens */
function act(tid, owner, id, action) {
  const P = params(tid);
  const l = own(tid, owner, id);
  let to = states.actionTarget("listing", action);
  if (!to) throw fail("Unknown action " + action);
  if (states.is("listing", to, "on_sale") || states.is("listing", to, "decision")) throw fail("Only staff decide whether a listing goes on sale", 403);
  if (states.is("listing", to, "in_review") && !P.require_review) to = states.actionTarget("listing", "publish");
  if (states.is("listing", to, "on_sale")) {
    const live = inTag("on_sale");
    const n = db().get("SELECT COUNT(*) c FROM peer_listings WHERE tenant_id=? AND owner=? AND status IN " + live.sql, Number(tid), String(owner), ...live.args).c;
    if (n >= Number(P.max_live)) throw fail("You can have up to " + P.max_live + " listings on sale", 409);
  }
  return present(move(tid, l, to), true);
}
/* staff review: approve (on sale) or reject with notes */
function review(tid, id, action, notes) {
  params(tid);
  const l = db().get("SELECT * FROM peer_listings WHERE id=? AND tenant_id=?", Number(id), Number(tid));
  if (!l) throw fail("Listing not found", 404);
  const to = states.actionTarget("listing", action);
  if (!to) throw fail("Unknown action " + action);
  if (notes != null) db().run("UPDATE peer_listings SET review_notes=? WHERE id=?", String(notes).slice(0, 1000), l.id);
  const cur = move(tid, db().get("SELECT * FROM peer_listings WHERE id=?", l.id), to);
  require("./tell.js").tell(tid, cur.owner, "listing_update", "Your listing " + cur.title + " is " + states.display("listing", cur.status).label, String(notes || ""), "sell.html");
  return present(cur, true);
}
function all(tid) { params(tid); return db().all("SELECT * FROM peer_listings WHERE tenant_id=? ORDER BY id DESC LIMIT 300", Number(tid)).map(l => ({ ...present(l, true), owner: l.owner })); }

/* ---------- the listing as a product the store sells ---------- */
function sellerFor(tid, l) {
  const P = caps().cap(tid, "peer_listings");
  const D = db();
  const ex = D.get("SELECT id FROM sellers WHERE tenant_id=? AND owner=?", Number(tid), l.owner);
  if (ex) return ex.id;
  const roles = keys("sellerRoles");
  const role = roles.includes(String(P.seller_role || "")) ? String(P.seller_role) : roles[0];
  return Number(D.run("INSERT INTO sellers(tenant_id,name,role,owner) VALUES(?,?,?,?)", Number(tid), l.owner_name || "Seller", role, l.owner).lastInsertRowid);
}
function publish(tid, l) {
  const P = caps().cap(tid, "peer_listings");
  const D = db();
  const sellerId = l.seller_id || sellerFor(tid, l);
  const imgs = J(l.images, []);
  const media = JSON.stringify(imgs.map((u, i) => ({ kind: "image", url: u, label: i ? "Photo " + (i + 1) : "Front" })));
  const stock = Math.max(0, l.qty - l.sold);
  const attrs = JSON.stringify(l.condition ? { condition: l.condition } : {});
  if (l.product_id && D.get("SELECT id FROM products WHERE tenant_id=? AND id=?", Number(tid), l.product_id)) {
    D.run("UPDATE products SET title=?, brand=?, dept=?, price=?, stock=?, keywords=?, media=?, attrs=?, lifecycle='published', deleted_at=NULL WHERE tenant_id=? AND id=?",
      l.title, l.owner_name || "Seller", l.dept || "", l.price, stock, l.title.toLowerCase(), media, attrs, Number(tid), l.product_id);
  } else {
    const id = "LS" + crypto.randomBytes(4).toString("hex").toUpperCase();
    const pos = (D.get("SELECT COALESCE(MAX(position),0) m FROM products WHERE tenant_id=?", Number(tid)).m || 0) + 1;
    D.run("INSERT INTO products(tenant_id,id,title,brand,dept,price,stock,keywords,emoji,hue,position,media,attrs,supplier_id,source_kind,lifecycle) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,'published')",
      Number(tid), id, l.title, l.owner_name || "Seller", l.dept || "", l.price, stock, l.title.toLowerCase(), "🏷️", Math.floor(Math.random() * 360), pos, media, attrs, sellerId, String(P.source_kind || "") || null);
    if (l.description) D.run("INSERT INTO product_bullets(tenant_id,product_id,pos,text) VALUES(?,?,0,?)", Number(tid), id, String(l.description).slice(0, 500));
    D.run("UPDATE peer_listings SET product_id=?, seller_id=? WHERE id=?", id, sellerId, l.id);
  }
  try { require("./search.js").onCatalogChange(tid); } catch (e) { }
}
function unpublish(tid, l) {
  if (!l.product_id) return;
  db().run("UPDATE products SET stock=0 WHERE tenant_id=? AND id=?", Number(tid), l.product_id);
  try { require("./search.js").onCatalogChange(tid); } catch (e) { }
}

/* ---------- an order that includes listed items ---------- */
lineterms.onOrder((ctx, items) => {
  if (!caps().on(Number(ctx.tid), "peer_listings", { buyer: false })) return;
  const P = caps().cap(Number(ctx.tid), "peer_listings");
  const D = db();
  for (const it of items) {
    const l = D.get("SELECT * FROM peer_listings WHERE tenant_id=? AND product_id=?", Number(ctx.tid), String(it.product.id));
    if (!l) continue;
    const sold = Math.min(l.qty, l.sold + Number(it.qty || 1));
    D.run("UPDATE peer_listings SET sold=? WHERE id=?", sold, l.id);
    D.run("UPDATE products SET stock=? WHERE tenant_id=? AND id=?", Math.max(0, l.qty - sold), Number(ctx.tid), l.product_id);
    if (sold >= l.qty) { const to = states.actionTarget("listing", "sell_out"); if (to && states.can("listing", l.status, to)) move(ctx.tid, { ...l, sold }, to); }
    const gross = +(Number(it.unit) * Number(it.qty || 1)).toFixed(2);
    const commission = +(gross * (Number(P.commission_pct) || 0) / 100).toFixed(2);
    D.run("INSERT INTO peer_earnings(tenant_id,listing_id,owner,order_id,gross,commission,net,currency,status,release_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
      Number(ctx.tid), l.id, l.owner, ctx.orderId, gross, commission, +(gross - commission).toFixed(2), null, states.initial("peer_earning"),
      new Date(Date.now() + (Number(P.hold_days) || 0) * 864e5).toISOString().slice(0, 19).replace("T", " "));
    require("./tell.js").tell(ctx.tid, l.owner, "listing_update", "You sold " + l.title, "Order " + ctx.orderNum + " · " + it.qty + " sold. Proceeds are credited after the holding period.", "sell.html");
  }
});
/* proceeds past their holding period are credited — unless the order was voided or aborted */
function releaseDue(tid) {
  if (!caps().on(Number(tid), "peer_listings", { buyer: false })) return { credited: 0 };
  const P = caps().cap(Number(tid), "peer_listings");
  const D = db();
  const held = states.tagged("peer_earning", "held");
  if (!held.length) return { credited: 0 };
  const dead = [...new Set(states.tagged("order", "void").concat(states.tagged("order", "aborted")))];
  let n = 0;
  for (const e of D.all("SELECT * FROM peer_earnings WHERE tenant_id=? AND status IN (" + held.map(() => "?").join(",") + ") AND release_at <= ?", Number(tid), ...held, sqlNow())) {
    const o = D.get("SELECT status FROM orders WHERE id=?", e.order_id);
    const to = o && dead.includes(o.status) ? states.actionTarget("peer_earning", "void") : states.actionTarget("peer_earning", "credit");
    if (!to) continue;
    if (states.is("peer_earning", to, "success")) require("./offers.js").credit(Number(tid), e.owner, e.net, String(P.earnings_kind || ""), "listing:" + e.listing_id + ":order:" + e.order_id, e.currency, "marketplace");
    const mv = states.apply("peer_earning", { tenantId: tid, from: e.status, to, row: e });
    const cols = Object.keys(mv.patch);
    D.run("UPDATE peer_earnings SET " + cols.map(c => c + "=?").join(", ") + " WHERE id=?", ...cols.map(c => mv.patch[c]), e.id);
    n++;
  }
  return { credited: n };
}
function earnings(tid, owner) { params(tid); return db().all("SELECT * FROM peer_earnings WHERE tenant_id=? AND owner=? ORDER BY id DESC LIMIT 200", Number(tid), String(owner)).map(e => ({ ...e, state: states.display("peer_earning", e.status) })); }
function sweepAll() {
  let n = 0;
  for (const t of db().all("SELECT DISTINCT tenant_id FROM peer_earnings")) { try { n += releaseDue(t.tenant_id).credited; } catch (e) { } }
  return { credited: n };
}
function vocabulary(tid) {
  return { conditions: reg().list("mktConditions").map(x => (typeof x === "string" ? { key: x, name: x } : x)),
    departments: db().all("SELECT key, label FROM departments WHERE tenant_id=? AND active=1 ORDER BY position", Number(tid)),
    /* a move that puts a listing on sale or decides it is staff's; the rest are the seller's */
    actions: Object.entries(states.actions("listing")).map(([verb, to]) => ({ verb, to, label: states.display("listing", to).label, staff_only: states.is("listing", to, "on_sale") || states.is("listing", to, "decision") })) };
}

module.exports = { ownerOf, create, update, mine, act, review, all, releaseDue, earnings, sweepAll, vocabulary };
