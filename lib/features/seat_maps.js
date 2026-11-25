/* seat maps: numbered places at an event. A layout is lines like "A:1-10=50" — a row, its seats and, if
   not the item's own, their price. A seat is held while it is in a bag and is one shopper's once
   ordered; a seat can be taken by only one, whatever the timing. */
"use strict";
const F = () => require("../features.js"), db = () => require("../db.js"), T = require("../lineterms.js"), K = "seat_maps";
function seats(r) { const out = []; for (const l of String(r.layout).split(/\r?\n/).map(x => x.trim()).filter(Boolean)) { const m = /^([A-Za-z0-9 ]{1,12}):(\d{1,3})-(\d{1,3})(?:=(\d+(?:\.\d+)?))?$/.exec(l); if (!m || Number(m[3]) < Number(m[2]) || out.length > 3000) throw F().fail("Not a row of seats: " + l); for (let n = Number(m[2]); n <= Number(m[3]); n++) out.push({ seat: m[1].trim() + n, row: m[1].trim(), price: m[4] ? Number(m[4]) : null }); } if (!out.length) throw F().fail("List the rows of seats"); return out; }
const of = (tid, id) => F().rows(tid, K).find(r => r.product_id === id);
const clear = (tid, id) => db().run("DELETE FROM seat_claims WHERE tenant_id=? AND product_id=? AND order_id IS NULL AND held_until < ?", Number(tid), id, Date.now());
function claim(tid, id, seat, owner) {
  clear(tid, id);
  const until = Date.now() + (Number(F().params(tid, K).hold_minutes) || 10) * 60e3;
  db().run("INSERT OR IGNORE INTO seat_claims(tenant_id,product_id,seat,owner,held_until) VALUES(?,?,?,?,?)", Number(tid), id, seat, owner, until);
  const r = db().get("SELECT * FROM seat_claims WHERE tenant_id=? AND product_id=? AND seat=?", Number(tid), id, seat);
  if (!r || r.order_id || r.owner !== owner) return false;
  db().run("UPDATE seat_claims SET held_until=? WHERE id=?", until, r.id); return true;
}
module.exports = {
  check: r => { seats(r); },
  rule: ({ tid, product, terms }) => of(tid, product.id) && !(terms || {}).seat ? { problem: "choose a seat" } : null,
  term: {
    key: "seat",
    clean: (ctx, v) => { const r = of(ctx.tid, ctx.product.id), s = r && seats(r).find(x => x.seat === String((v || {}).seat || "")); if (!s) throw T.fail("Choose a seat"); if (!claim(ctx.tid, ctx.product.id, s.seat, ctx.owner)) throw T.fail("Seat " + s.seat + " has just been taken", 409); return { seat: s.seat }; },
    price: (ctx, v) => { const r = of(ctx.tid, ctx.product.id), s = r && seats(r).find(x => x.seat === v.seat); if (!s) throw T.fail("that seat is no longer offered"); if (!claim(ctx.tid, ctx.product.id, v.seat, ctx.owner)) throw T.fail("seat " + v.seat + " was not kept — choose another"); return { ...(s.price != null ? { set: s.price } : {}), label: "Seat " + v.seat }; },
    maxQty: () => 1,
    place: (ctx, v) => { db().run("UPDATE seat_claims SET order_id=? WHERE tenant_id=? AND product_id=? AND seat=? AND owner=? AND order_id IS NULL", Number(ctx.orderId), Number(ctx.tid), ctx.product.id, v.seat, ctx.owner); }
  },
  open: ({ tid, owner, query }) => { const r = of(tid, String(query.product || "")); if (!r) return { seats: [] }; clear(tid, r.product_id); const taken = new Map(db().all("SELECT seat, owner, order_id FROM seat_claims WHERE tenant_id=? AND product_id=?", Number(tid), r.product_id).map(x => [x.seat, x])); const p = db().get("SELECT price FROM products WHERE tenant_id=? AND id=?", Number(tid), r.product_id); return { venue: r.venue, seats: seats(r).map(s => ({ ...s, price: s.price != null ? s.price : p.price, free: !taken.has(s.seat) || (!taken.get(s.seat).order_id && taken.get(s.seat).owner === owner) })) }; },
  moved: ({ order, to }) => { if (require("../states.js").is("order", to, "void")) db().run("DELETE FROM seat_claims WHERE order_id=?", order.id); },
  block: ({ tid, product }) => { const r = of(tid, product.id); return r && { title: "Choose your seat", text: r.venue || "", seats: true }; }
};
