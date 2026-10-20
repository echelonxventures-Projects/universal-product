/* LUXORA Platform — Make an offer: price negotiation between a shopper and a seller.
   A shopper offers a price for a quantity; whoever sells the product — the store, or the
   shopper who listed it (lib/listings.js) — accepts, counters or refuses; the shopper may
   accept a counter or answer it with a new price. Whose move it is, is what the offer's state
   MEANS (awaiting_seller, awaiting_buyer, agreed…) in the `price_offer` state machine. Store
   thresholds can accept or refuse at once. An agreed price rides on the bag line as its
   `offer` term (lib/lineterms.js) — it replaces the list price for that quantity — and is
   used up when the order is placed. Capability: price_negotiation. */
"use strict";

const db = () => require("./db.js");
const caps = () => require("./capabilities.js");
const states = require("./states.js");
const lineterms = require("./lineterms.js");
const fail = lineterms.fail;
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };
const inTag = tag => { const xs = states.tagged("price_offer", tag); return { sql: "(" + (xs.length ? xs.map(() => "?").join(",") : "NULL") + ")", args: xs }; };
const sqlAt = ms => new Date(ms).toISOString().slice(0, 19).replace("T", " ");
const parseT = v => new Date(String(v || "").replace(" ", "T") + "Z");

function params(tid) {
  const P = caps().cap(tid, "price_negotiation");
  if (!Object.keys(P).length) throw fail("Offers are not available in this store", 403);
  return P;
}
const product = (tid, id) => db().get("SELECT * FROM products WHERE tenant_id=? AND id=? AND lifecycle='published' AND deleted_at IS NULL", Number(tid), String(id || ""));
const sellerOf = (tid, productId) => { try { return require("./listings.js").ownerOf(tid, productId); } catch (e) { return ""; } };
const tell = (...a) => require("./tell.js").tell(...a);

function present(o, viewer) {
  const p = db().get("SELECT id, title, price, emoji, hue FROM products WHERE tenant_id=? AND id=?", o.tenant_id, o.product_id);
  return { id: o.id, product: p || null, qty: o.qty, amount: o.amount, counter_amount: o.counter_amount, note: o.note, status: o.status,
    state: states.display("price_offer", o.status), expires_at: o.expires_at, history: J(o.history, []),
    yours: viewer != null && viewer === o.owner, agreed: states.is("price_offer", o.status, "agreed"), live: states.is("price_offer", o.status, "live"),
    awaiting_you: viewer != null && ((viewer === o.owner && states.is("price_offer", o.status, "awaiting_buyer")) || (viewer !== o.owner && states.is("price_offer", o.status, "awaiting_seller"))) };
}
function write(o, to, patch, entry) {
  const mv = states.apply("price_offer", { tenantId: o.tenant_id, from: o.status, to, row: o });
  const hist = J(o.history, []).concat([Object.assign({ at: new Date().toISOString(), to }, entry || {})]);
  const p = Object.assign({}, mv.patch, patch || {}, { history: JSON.stringify(hist) });
  const cols = Object.keys(p);
  db().run("UPDATE price_offers SET " + cols.map(c => c + "=?").join(", ") + " WHERE id=?", ...cols.map(c => p[c]), o.id);
  return db().get("SELECT * FROM price_offers WHERE id=?", o.id);
}

/* the shopper offers */
function make(tid, owner, input) {
  const P = params(tid);
  const i = input || {};
  const p = product(tid, i.product_id);
  if (!p) throw fail("That product is not available", 404);
  const seller = sellerOf(tid, p.id);
  if (seller && seller === String(owner)) throw fail("You cannot make an offer on your own listing");
  const qty = Math.max(1, Math.min(Number(p.stock) || 1, Math.floor(Number(i.qty) || 1)));
  const amount = +Number(i.amount).toFixed(2);
  if (!(amount > 0)) throw fail("Offer a price above zero");
  if (amount >= Number(p.price)) throw fail("That is the list price or more — buy it now instead");
  if (amount < Number(p.price) * Number(P.min_offer_pct) / 100) throw fail("Offers start at " + P.min_offer_pct + "% of the price");
  const live = inTag("live");
  const n = db().get("SELECT COUNT(*) c FROM price_offers WHERE tenant_id=? AND owner=? AND status IN " + live.sql, Number(tid), String(owner), ...live.args).c;
  if (n >= Number(P.max_open_per_shopper)) throw fail("You have " + n + " open offers — wait for answers first", 409);
  const r = db().run("INSERT INTO price_offers(tenant_id,product_id,owner,seller,qty,amount,note,status,history,expires_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
    Number(tid), p.id, String(owner), seller, qty, amount, String(i.note || "").slice(0, 500), states.initial("price_offer"),
    JSON.stringify([{ at: new Date().toISOString(), by: "buyer", amount }]), sqlAt(Date.now() + Number(P.expiry_hours) * 3600e3));
  let o = db().get("SELECT * FROM price_offers WHERE id=?", r.lastInsertRowid);
  /* the store's thresholds decide at once where it set them */
  const pct = amount / Number(p.price) * 100;
  if (Number(P.auto_accept_pct) > 0 && pct >= Number(P.auto_accept_pct)) o = write(o, states.actionTarget("price_offer", "accept"), { expires_at: sqlAt(Date.now() + Number(P.buy_within_hours) * 3600e3) }, { by: "rule" });
  else if (Number(P.auto_decline_pct) > 0 && pct < Number(P.auto_decline_pct)) o = write(o, states.actionTarget("price_offer", "refuse"), null, { by: "rule" });
  else if (seller) tell(tid, seller, "offer_update", "New offer on " + p.title, "Someone offers " + amount + " for " + qty + ".", "sell.html#offers");
  return present(o, String(owner));
}
/* a move by the shopper (on their own offer) or the seller (the listing's owner, or staff for
   the store's own products): whose move it is comes from the state, never from a name */
function respond(tid, actor, id, action, input) {
  const P = params(tid);
  const o = db().get("SELECT * FROM price_offers WHERE id=? AND tenant_id=?", Number(id), Number(tid));
  if (!o) throw fail("Offer not found", 404);
  const isBuyer = actor.owner === o.owner;
  const isSeller = o.seller ? actor.owner === o.seller : !!actor.staff;
  if (!isBuyer && !isSeller) throw fail("Offer not found", 404);
  const to = states.actionTarget("price_offer", action);
  if (!to || !states.can("price_offer", o.status, to)) throw fail("An offer that is " + states.display("price_offer", o.status).label + " cannot be moved that way", 409);
  if (o.expires_at && parseT(o.expires_at).getTime() < Date.now()) throw fail("This offer has expired", 409);
  /* the shopper may withdraw their own offer whenever the machine allows it */
  const withdraws = isBuyer && to === states.actionTarget("price_offer", "withdraw");
  const myTurn = (isBuyer && states.is("price_offer", o.status, "awaiting_buyer")) || (isSeller && states.is("price_offer", o.status, "awaiting_seller"));
  if (!myTurn && !withdraws) throw fail("It is not your move on this offer", 409);
  const i = input || {};
  const p = db().get("SELECT * FROM products WHERE tenant_id=? AND id=?", Number(tid), o.product_id) || {};
  let patch = { expires_at: sqlAt(Date.now() + Number(P.expiry_hours) * 3600e3) }, entry = { by: isBuyer ? "buyer" : "seller" };
  if (states.is("price_offer", to, "awaiting_buyer") || states.is("price_offer", to, "awaiting_seller")) {
    const amount = +Number(i.amount).toFixed(2);
    if (!(amount > 0) || amount >= Number(p.price)) throw fail("Name a price above zero and below the list price");
    patch = Object.assign(patch, isBuyer ? { amount } : { counter_amount: amount });
    entry.amount = amount;
  }
  if (states.is("price_offer", to, "agreed")) {
    /* accepting a counter agrees to the counter; accepting an offer agrees to the offer */
    if (isBuyer && o.counter_amount != null) patch.amount = o.counter_amount;
    patch.expires_at = sqlAt(Date.now() + Number(P.buy_within_hours) * 3600e3);
  }
  const cur = write(o, to, patch, entry);
  const other = isBuyer ? cur.seller : cur.owner;
  if (other) tell(tid, other, "offer_update", "Your offer on " + (p.title || "an item") + " is " + states.display("price_offer", cur.status).label, "", isBuyer ? "sell.html#offers" : "product.html?id=" + encodeURIComponent(o.product_id));
  return present(cur, actor.owner);
}
/* the shopper's offers, and those waiting on a seller (a listing's owner, or the store) */
function mine(tid, owner) { params(tid); return db().all("SELECT * FROM price_offers WHERE tenant_id=? AND owner=? ORDER BY id DESC LIMIT 200", Number(tid), String(owner)).map(o => present(o, String(owner))); }
function received(tid, sellerOwner) { params(tid); return db().all("SELECT * FROM price_offers WHERE tenant_id=? AND seller=? ORDER BY id DESC LIMIT 200", Number(tid), String(sellerOwner || "")).map(o => present(o, String(sellerOwner || ""))); }
function expireDue(tid) {
  if (!caps().on(Number(tid), "price_negotiation", { buyer: false })) return { expired: 0 };
  const live = inTag("live");
  const to = states.actionTarget("price_offer", "expire");
  const due = db().all("SELECT * FROM price_offers WHERE tenant_id=? AND status IN " + live.sql + " AND expires_at < ?", Number(tid), ...live.args, sqlAt(Date.now()));
  for (const o of due) if (to && states.can("price_offer", o.status, to)) write(o, to, null, { by: "clock" });
  return { expired: due.length };
}
function sweepAll() { let n = 0; for (const t of db().all("SELECT DISTINCT tenant_id FROM price_offers")) { try { n += expireDue(t.tenant_id).expired; } catch (e) { } } return { expired: n }; }

/* ---------- the line term: { id } of the shopper's own agreed offer ---------- */
function agreed(ctx, value) {
  const o = db().get("SELECT * FROM price_offers WHERE id=? AND tenant_id=? AND owner=?", Number(value && typeof value === "object" ? value.id : value), Number(ctx.tid), String(ctx.owner));
  if (!o || String(o.product_id) !== String(ctx.product.id)) throw fail("That offer is not yours or is for another product", 404);
  if (!states.is("price_offer", o.status, "agreed")) throw fail("that offer is " + states.display("price_offer", o.status).label);
  if (o.expires_at && parseT(o.expires_at).getTime() < Date.now()) throw fail("the agreed price has expired");
  return o;
}
lineterms.register("offer", {
  atom: "price_negotiation",
  clean: (ctx, value) => ({ id: agreed(ctx, value).id }),
  price: (ctx, value) => { const o = agreed(ctx, value); return { set: Number(o.amount), label: "Agreed price for " + o.qty }; },
  maxQty: (ctx, value) => agreed(ctx, value).qty,
  place: (ctx, value) => {
    const o = db().get("SELECT * FROM price_offers WHERE id=? AND tenant_id=?", Number(value.id), Number(ctx.tid));
    const to = states.actionTarget("price_offer", "use");
    if (o && to && states.can("price_offer", o.status, to)) write(o, to, { order_id: ctx.orderId }, { by: "order" });
  }
});

module.exports = { make, respond, mine, received, expireDue, sweepAll };
