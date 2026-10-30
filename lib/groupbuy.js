/* LUXORA Platform — Group buying: a lower price when enough shoppers join.
   Staff open a campaign on a product: a group price, how many members it needs by a deadline,
   and how many it may take. A shopper joins by buying at the group price — the campaign rides
   on the bag line as its `group` term (lib/lineterms.js) — and becomes a member with that
   order. When the deadline passes, a campaign with enough members has succeeded and its orders
   go ahead; one that fell short has failed, and every member's order is cancelled and what
   they paid is refunded to their wallet. A full campaign may close early. The campaign's life
   is the `group_campaign` state machine, asked by tag (joinable, refunds_members…).
   Capability: group_buying. */
"use strict";

const db = () => require("./db.js");
const caps = () => require("./capabilities.js");
const states = require("./states.js");
const lineterms = require("./lineterms.js");
const fail = lineterms.fail;
const inTag = tag => { const xs = states.tagged("group_campaign", tag); return { sql: "(" + (xs.length ? xs.map(() => "?").join(",") : "NULL") + ")", args: xs }; };
const sqlAt = ms => new Date(ms).toISOString().slice(0, 19).replace("T", " ");
const parseT = v => { const t = new Date(String(v || "").replace(" ", "T") + (/[zZ]|[+-]\d\d:?\d\d$/.test(String(v)) ? "" : "Z")); return isNaN(t) ? null : t; };
const tell = (...a) => require("./tell.js").tell(...a);

function params(tid) {
  const P = caps().cap(tid, "group_buying");
  if (!Object.keys(P).length) throw fail("Group buying is not available in this store", 403);
  return P;
}
const members = id => db().get("SELECT COUNT(DISTINCT owner) n, COALESCE(SUM(qty),0) q FROM group_members WHERE campaign_id=? AND refunded=0", id);
function present(c, viewer) {
  const m = members(c.id);
  const p = db().get("SELECT id, title, price, emoji, hue FROM products WHERE tenant_id=? AND id=?", c.tenant_id, c.product_id);
  return { id: c.id, title: c.title, product: p || null, group_price: c.group_price, min_members: c.min_members, max_members: c.max_members, ends_at: c.ends_at,
    members: m.n, needed: Math.max(0, c.min_members - m.n), status: c.status, state: states.display("group_campaign", c.status),
    joinable: states.is("group_campaign", c.status, "joinable") && parseT(c.ends_at).getTime() > Date.now() && !(c.max_members && m.n >= c.max_members),
    joined: viewer ? !!db().get("SELECT id FROM group_members WHERE campaign_id=? AND owner=? AND refunded=0", c.id, String(viewer)) : false };
}
function write(c, to) {
  const mv = states.apply("group_campaign", { tenantId: c.tenant_id, from: c.status, to, row: c });
  const cols = Object.keys(mv.patch);
  db().run("UPDATE group_campaigns SET " + cols.map(k => k + "=?").join(", ") + " WHERE id=?", ...cols.map(k => mv.patch[k]), c.id);
  return db().get("SELECT * FROM group_campaigns WHERE id=?", c.id);
}

function create(tid, input) {
  params(tid);
  const i = input || {};
  const p = db().get("SELECT * FROM products WHERE tenant_id=? AND id=? AND lifecycle='published' AND deleted_at IS NULL", Number(tid), String(i.product_id || ""));
  if (!p) throw fail("That product is not available", 404);
  const price = +Number(i.group_price).toFixed(2);
  if (!(price > 0) || price >= Number(p.price)) throw fail("The group price must be above zero and below the product's price");
  const min = Math.max(2, Math.floor(Number(i.min_members) || 0));
  const max = i.max_members ? Math.max(min, Math.floor(Number(i.max_members))) : null;
  const ends = parseT(i.ends_at);
  if (!ends || ends.getTime() <= Date.now()) throw fail("A campaign ends in the future");
  const r = db().run("INSERT INTO group_campaigns(tenant_id,product_id,title,group_price,min_members,max_members,ends_at,status) VALUES(?,?,?,?,?,?,?,?)",
    Number(tid), p.id, String(i.title || p.title).slice(0, 140), price, min, max, sqlAt(ends), states.initial("group_campaign"));
  return present(db().get("SELECT * FROM group_campaigns WHERE id=?", r.lastInsertRowid));
}
function forProduct(tid, productId, viewer) {
  if (!caps().on(tid, "group_buying")) return null;
  const j = inTag("joinable");
  const c = db().get("SELECT * FROM group_campaigns WHERE tenant_id=? AND product_id=? AND status IN " + j.sql + " ORDER BY id DESC LIMIT 1", Number(tid), String(productId), ...j.args);
  return c ? present(c, viewer) : null;
}
function list(tid) { params(tid); return db().all("SELECT * FROM group_campaigns WHERE tenant_id=? ORDER BY id DESC LIMIT 200", Number(tid)).map(c => present(c)); }
function mine(tid, owner) {
  params(tid);
  return db().all("SELECT DISTINCT c.* FROM group_campaigns c JOIN group_members m ON m.campaign_id=c.id WHERE c.tenant_id=? AND m.owner=? ORDER BY c.id DESC", Number(tid), String(owner)).map(c => present(c, owner));
}

/* closing: on time, or early when full. A failed or cancelled campaign refunds its members. */
function close(tid, c, to) {
  const P = caps().cap(Number(tid), "group_buying");
  const done = write(c, to);
  const p = db().get("SELECT title FROM products WHERE tenant_id=? AND id=?", Number(tid), c.product_id) || {};
  const refunds = states.is("group_campaign", to, "refunds_members");
  for (const m of db().all("SELECT * FROM group_members WHERE campaign_id=? AND refunded=0", c.id)) {
    if (refunds) {
      const o = db().get("SELECT * FROM orders WHERE id=?", m.order_id);
      const cancelTo = states.tagged("order", "void").find(s => o && states.can("order", o.status, s));
      if (o && cancelTo) {
        const mv = states.apply("order", { tenantId: tid, from: o.status, to: cancelTo, row: o });
        const cols = Object.keys(mv.patch);
        db().run("UPDATE orders SET " + cols.map(k => k + "=?").join(", ") + " WHERE id=?", ...cols.map(k => mv.patch[k]), o.id);
      }
      if (m.paid > 0) require("./offers.js").credit(Number(tid), m.owner, m.paid, String((P && P.refund_kind) || ""), "group:" + c.id + ":order:" + m.order_id, null, "group_buying");
      db().run("UPDATE group_members SET refunded=1 WHERE id=?", m.id);
      tell(tid, m.owner, "group_update", "The group for " + p.title + " didn't fill", "Your order is cancelled and " + m.paid + " is back in your wallet.", "orders.html");
    } else tell(tid, m.owner, "group_update", "The group for " + p.title + " is complete", "Your order goes ahead at the group price.", "orders.html");
  }
  return present(done);
}
function cancel(tid, id) {
  params(tid);
  const c = db().get("SELECT * FROM group_campaigns WHERE id=? AND tenant_id=?", Number(id), Number(tid));
  if (!c) throw fail("Campaign not found", 404);
  const to = states.actionTarget("group_campaign", "cancel");
  if (!states.can("group_campaign", c.status, to)) throw fail("This campaign is already closed", 409);
  return close(tid, c, to);
}
function tick(tid) {
  if (!caps().on(Number(tid), "group_buying", { buyer: false })) return { closed: 0 };
  const P = caps().cap(Number(tid), "group_buying");
  const j = inTag("joinable");
  let n = 0;
  for (const c of db().all("SELECT * FROM group_campaigns WHERE tenant_id=? AND status IN " + j.sql, Number(tid), ...j.args)) {
    const m = members(c.id);
    const ended = parseT(c.ends_at).getTime() <= Date.now();
    const full = P.close_when_full && c.max_members && m.n >= c.max_members;
    if (!ended && !full) continue;
    close(tid, c, states.actionTarget("group_campaign", m.n >= c.min_members ? "succeed" : "fail"));
    n++;
  }
  return { closed: n };
}
function sweepAll() { let n = 0; for (const t of db().all("SELECT DISTINCT tenant_id FROM group_campaigns")) { try { n += tick(t.tenant_id).closed; } catch (e) { } } return { closed: n }; }

/* ---------- the line term: { id } of a campaign this shopper may join ---------- */
function joinable(ctx, value) {
  const c = db().get("SELECT * FROM group_campaigns WHERE id=? AND tenant_id=?", Number(value && typeof value === "object" ? value.id : value), Number(ctx.tid));
  if (!c || String(c.product_id) !== String(ctx.product.id)) throw fail("Unknown group for this product", 404);
  const v = present(c, ctx.owner);
  if (!v.joinable) throw fail("that group is no longer open");
  if (v.joined) throw fail("you have already joined that group");
  return c;
}
lineterms.register("group", {
  atom: "group_buying",
  clean: (ctx, value) => ({ id: joinable(ctx, value).id }),
  price: (ctx, value) => { const c = db().get("SELECT * FROM group_campaigns WHERE id=? AND tenant_id=?", Number(value.id), Number(ctx.tid)); if (!c) throw fail("that group no longer exists"); return { set: Number(c.group_price), label: "Group price" }; },
  maxQty: ctx => Number((caps().cap(ctx.tid, "group_buying") || {}).max_qty_per_member) || 1,
  place: (ctx, value) => {
    db().run("INSERT INTO group_members(tenant_id,campaign_id,owner,order_id,qty,paid) VALUES(?,?,?,?,?,?)", Number(ctx.tid), Number(value.id), String(ctx.owner), ctx.orderId, Number(ctx.qty) || 1, +(Number(ctx.unit) * (Number(ctx.qty) || 1)).toFixed(2));
    try { tick(ctx.tid); } catch (e) { }
  }
});

module.exports = { create, forProduct, list, mine, cancel, tick, sweepAll };
