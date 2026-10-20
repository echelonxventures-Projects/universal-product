/* LUXORA Platform — Auctions: timed, ascending, with automatic (proxy) bidding.
   The store, or a shopper who listed the item (lib/listings.js), puts a product up between a
   start and an end, from a starting price, with an optional reserve (the lowest price it will
   sell at) and buy-it-now price. A bidder states the most they will pay; the auction bids for
   them one increment at a time — the price is always one increment above the runner-up's most,
   never above the leader's own. A bid in the last minutes extends the end, so nobody wins by
   bidding at the last second. The increment ladder and every window are the auctions
   capability's params.

   When it ends, a leader whose most meets the reserve wins; the winning price rides on the bag
   line as its `auction` term (lib/lineterms.js) and must be paid within the window. Every stage
   is the `auction` state machine, asked by tag (upcoming, accepting_bids, won…). */
"use strict";

const db = () => require("./db.js");
const caps = () => require("./capabilities.js");
const states = require("./states.js");
const lineterms = require("./lineterms.js");
const fail = lineterms.fail;
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };
const inTag = tag => { const xs = states.tagged("auction", tag); return { sql: "(" + (xs.length ? xs.map(() => "?").join(",") : "NULL") + ")", args: xs }; };
const sqlAt = ms => new Date(ms).toISOString().slice(0, 19).replace("T", " ");
const parseT = v => { const t = new Date(String(v || "").replace(" ", "T") + (/[zZ]|[+-]\d\d:?\d\d$/.test(String(v)) ? "" : "Z")); return isNaN(t) ? null : t; };
const tell = (...a) => require("./tell.js").tell(...a);
const money = n => +Number(n).toFixed(2);

function params(tid) {
  const P = caps().cap(tid, "auctions");
  if (!Object.keys(P).length) throw fail("Auctions are not available in this store", 403);
  return P;
}
/* the step above a price, from the store's ladder of [from price, step] pairs */
function step(P, price) {
  const ladder = (J(P.increments, []) || []).map(x => [Number(x[0]), Number(x[1])]).filter(x => x[1] > 0).sort((a, b) => a[0] - b[0]);
  let s = ladder.length ? ladder[0][1] : 1;
  for (const [from, inc] of ladder) if (price >= from) s = inc;
  return s;
}
const sellerOf = (tid, productId) => { try { return require("./listings.js").ownerOf(tid, productId); } catch (e) { return ""; } };

function present(a, viewer) {
  const P = caps().cap(a.tenant_id, "auctions");
  const p = db().get("SELECT id, title, price, emoji, hue FROM products WHERE tenant_id=? AND id=?", a.tenant_id, a.product_id);
  const live = states.is("auction", a.status, "accepting_bids");
  const price = a.current_price != null ? a.current_price : a.start_price;
  const next = a.leader ? money(price + step(P, price)) : a.start_price;
  return { id: a.id, product: p || null, start_price: a.start_price, current_price: a.current_price, bids: a.bids, starts_at: a.starts_at, ends_at: a.ends_at,
    status: a.status, state: states.display("auction", a.status), live, next_bid: live ? next : null,
    reserve_met: a.reserve_price == null ? true : (a.leader_max != null && a.leader_max >= a.reserve_price),
    buy_now_price: live && a.buy_now_price != null && !(P.buy_now_until_first_bid && a.bids > 0) ? a.buy_now_price : null,
    leading: viewer != null && a.leader === viewer, won: viewer != null && a.winner === viewer && states.is("auction", a.status, "awaiting_payment"),
    final_price: a.final_price, pay_by: a.pay_by, mine: viewer != null && a.seller === viewer };
}
function write(a, to, patch) {
  const mv = to ? states.apply("auction", { tenantId: a.tenant_id, from: a.status, to, row: a }).patch : {};
  const p = Object.assign({}, mv, patch || {});
  const cols = Object.keys(p);
  if (cols.length) db().run("UPDATE auctions SET " + cols.map(c => c + "=?").join(", ") + " WHERE id=?", ...cols.map(c => p[c]), a.id);
  return db().get("SELECT * FROM auctions WHERE id=?", a.id);
}

/* put a product up: the store's staff (seller "") or the shopper whose listing it is */
function create(tid, actor, input) {
  const P = params(tid);
  const i = input || {};
  const D = db();
  const p = D.get("SELECT * FROM products WHERE tenant_id=? AND id=? AND lifecycle='published' AND deleted_at IS NULL", Number(tid), String(i.product_id || ""));
  if (!p) throw fail("That product is not available", 404);
  const seller = sellerOf(tid, p.id);
  if (seller ? actor.owner !== seller : !actor.staff) throw fail("Only the product's seller can auction it", 403);
  const busy = [...states.tagged("auction", "upcoming"), ...states.tagged("auction", "accepting_bids")];
  if (busy.length && D.get("SELECT id FROM auctions WHERE tenant_id=? AND product_id=? AND status IN (" + busy.map(() => "?").join(",") + ")", Number(tid), p.id, ...busy)) throw fail("This product is already being auctioned", 409);
  const start = +Number(i.start_price).toFixed(2);
  if (!(start > 0)) throw fail("A starting price above zero is needed");
  const reserve = i.reserve_price ? +Number(i.reserve_price).toFixed(2) : null;
  const buyNow = i.buy_now_price ? +Number(i.buy_now_price).toFixed(2) : null;
  if (reserve != null && reserve < start) throw fail("The reserve cannot be below the starting price");
  if (buyNow != null && buyNow <= Math.max(start, reserve || 0)) throw fail("Buy-it-now must be above the starting price and the reserve");
  const s = i.starts_at ? parseT(i.starts_at) : new Date(), e = parseT(i.ends_at);
  if (!s || !e || e <= s) throw fail("An auction ends after it starts");
  if (e.getTime() - s.getTime() > Number(P.max_duration_days) * 864e5) throw fail("Auctions run at most " + P.max_duration_days + " days");
  const r = D.run("INSERT INTO auctions(tenant_id,product_id,seller,start_price,reserve_price,buy_now_price,starts_at,ends_at,status) VALUES(?,?,?,?,?,?,?,?,?)",
    Number(tid), p.id, seller, start, reserve, buyNow, sqlAt(s), sqlAt(e), states.initial("auction"));
  let a = D.get("SELECT * FROM auctions WHERE id=?", r.lastInsertRowid);
  if (s.getTime() <= Date.now()) a = write(a, states.actionTarget("auction", "open"));
  return present(a, actor.owner);
}

/* a bid: the most this bidder will pay. The proxy rule moves the price. */
function bid(tid, owner, id, maxAmount) {
  const P = params(tid);
  const D = db();
  let a = D.get("SELECT * FROM auctions WHERE id=? AND tenant_id=?", Number(id), Number(tid));
  if (!a) throw fail("Auction not found", 404);
  if (!states.is("auction", a.status, "accepting_bids") || parseT(a.ends_at).getTime() <= Date.now()) throw fail("This auction is not taking bids", 409);
  if (a.seller && a.seller === String(owner)) throw fail("You cannot bid on your own auction", 403);
  const max = money(maxAmount);
  const price = a.current_price != null ? a.current_price : a.start_price;
  const minimum = a.leader ? money(price + step(P, price)) : a.start_price;
  if (a.leader === String(owner)) {
    if (!(max > a.leader_max)) throw fail("You are already leading — raise your maximum above " + a.leader_max);
  } else if (!(max >= minimum)) throw fail("Bid at least " + minimum);
  D.run("INSERT INTO auction_bids(tenant_id,auction_id,owner,max_amount) VALUES(?,?,?,?)", Number(tid), a.id, String(owner), max);
  const patch = { bids: a.bids + 1 };
  let outbid = null;
  if (!a.leader) Object.assign(patch, { leader: String(owner), leader_max: max, current_price: a.start_price });
  else if (a.leader === String(owner)) patch.leader_max = max;
  else if (max > a.leader_max) {
    outbid = a.leader;
    Object.assign(patch, { leader: String(owner), leader_max: max, current_price: money(Math.min(max, a.leader_max + step(P, a.leader_max))) });
  } else {
    patch.current_price = money(Math.min(a.leader_max, max + step(P, max)));
    outbid = String(owner);
  }
  /* once the leader's most meets the reserve, the price is at least the reserve */
  const leaderMax = patch.leader_max != null ? patch.leader_max : a.leader_max;
  if (a.reserve_price != null && leaderMax >= a.reserve_price) patch.current_price = Math.max(patch.current_price != null ? patch.current_price : price, a.reserve_price);
  /* a bid near the end extends it */
  const left = parseT(a.ends_at).getTime() - Date.now();
  if (left < Number(P.anti_snipe_minutes) * 60000) patch.ends_at = sqlAt(parseT(a.ends_at).getTime() + Number(P.extend_minutes) * 60000);
  a = write(a, null, patch);
  const p = D.get("SELECT title FROM products WHERE tenant_id=? AND id=?", Number(tid), a.product_id) || {};
  if (outbid && outbid !== String(owner)) tell(tid, outbid, "auction_update", "You've been outbid on " + p.title, "The price is now " + a.current_price + ".", "product.html?id=" + encodeURIComponent(a.product_id));
  const view = present(a, String(owner));
  return { ...view, outbid: outbid === String(owner) };
}
/* buy it now: the auction ends at once, sold to this shopper at the buy-it-now price */
function buyNow(tid, owner, id) {
  const P = params(tid);
  const a = db().get("SELECT * FROM auctions WHERE id=? AND tenant_id=?", Number(id), Number(tid));
  if (!a) throw fail("Auction not found", 404);
  const v = present(a, String(owner));
  if (!v.live || v.buy_now_price == null) throw fail("Buy-it-now is not available on this auction", 409);
  if (a.seller && a.seller === String(owner)) throw fail("You cannot buy your own auction", 403);
  const done = write(a, states.actionTarget("auction", "sell"), { winner: String(owner), final_price: a.buy_now_price, current_price: a.buy_now_price, pay_by: sqlAt(Date.now() + Number(P.payment_window_hours) * 3600e3) });
  return present(done, String(owner));
}
function get(tid, id, viewer) { const a = db().get("SELECT * FROM auctions WHERE id=? AND tenant_id=?", Number(id), Number(tid)); if (!a) throw fail("Auction not found", 404); return present(a, viewer); }
/* the product page's auction, if one is upcoming or live */
function forProduct(tid, productId, viewer) {
  if (!caps().on(tid, "auctions")) return null;
  const open = [...states.tagged("auction", "upcoming"), ...states.tagged("auction", "accepting_bids"), ...states.tagged("auction", "won")];
  if (!open.length) return null;
  const a = db().get("SELECT * FROM auctions WHERE tenant_id=? AND product_id=? AND status IN (" + open.map(() => "?").join(",") + ") ORDER BY id DESC LIMIT 1", Number(tid), String(productId), ...open);
  return a ? present(a, viewer) : null;
}
function list(tid, viewer, tag) {
  params(tid);
  const t = tag ? inTag(tag) : null;
  return db().all("SELECT * FROM auctions WHERE tenant_id=?" + (t ? " AND status IN " + t.sql : "") + " ORDER BY ends_at LIMIT 200", Number(tid), ...(t ? t.args : [])).map(a => present(a, viewer));
}
function mine(tid, owner) {
  params(tid);
  return db().all("SELECT DISTINCT a.* FROM auctions a LEFT JOIN auction_bids b ON b.auction_id=a.id WHERE a.tenant_id=? AND (b.owner=? OR a.winner=? OR a.seller=?) ORDER BY a.ends_at DESC LIMIT 200",
    Number(tid), String(owner), String(owner), String(owner)).map(a => present(a, String(owner)));
}
function cancel(tid, actor, id) {
  params(tid);
  const a = db().get("SELECT * FROM auctions WHERE id=? AND tenant_id=?", Number(id), Number(tid));
  if (!a) throw fail("Auction not found", 404);
  if (a.seller ? actor.owner !== a.seller : !actor.staff) throw fail("Only the seller can cancel it", 403);
  if (a.bids > 0 && !actor.staff) throw fail("An auction with bids can only be cancelled by staff", 409);
  const to = states.actionTarget("auction", "cancel");
  if (!states.can("auction", a.status, to)) throw fail("This auction can no longer be cancelled", 409);
  return present(write(a, to), actor.owner);
}

/* the clock: upcoming auctions open, ended ones close — sold to a leader who met the reserve */
function tick(tid) {
  if (!caps().on(Number(tid), "auctions", { buyer: false })) return { opened: 0, closed: 0 };
  const P = caps().cap(Number(tid), "auctions");
  const D = db(), now = sqlAt(Date.now());
  let opened = 0, closed = 0;
  const up = inTag("upcoming");
  for (const a of D.all("SELECT * FROM auctions WHERE tenant_id=? AND status IN " + up.sql + " AND starts_at <= ?", Number(tid), ...up.args, now)) { write(a, states.actionTarget("auction", "open")); opened++; }
  const live = inTag("accepting_bids");
  for (const a of D.all("SELECT * FROM auctions WHERE tenant_id=? AND status IN " + live.sql + " AND ends_at <= ?", Number(tid), ...live.args, now)) {
    const sold = a.leader && (a.reserve_price == null || a.leader_max >= a.reserve_price);
    const p = D.get("SELECT title FROM products WHERE tenant_id=? AND id=?", Number(tid), a.product_id) || {};
    if (sold) {
      write(a, states.actionTarget("auction", "sell"), { winner: a.leader, final_price: a.current_price, pay_by: sqlAt(Date.now() + Number(P.payment_window_hours) * 3600e3) });
      tell(tid, a.leader, "auction_update", "You won " + p.title, "Pay " + a.current_price + " within " + P.payment_window_hours + " hours to keep it.", "product.html?id=" + encodeURIComponent(a.product_id));
    } else write(a, states.actionTarget("auction", "close_unsold"));
    if (a.seller) tell(tid, a.seller, "auction_update", "Your auction of " + p.title + " has ended", sold ? "Sold for " + a.current_price + "." : "It did not sell.", "sell.html");
    closed++;
  }
  /* a winner who never paid: the auction closes unsold */
  const due = inTag("awaiting_payment");
  for (const a of D.all("SELECT * FROM auctions WHERE tenant_id=? AND status IN " + due.sql + " AND pay_by < ?", Number(tid), ...due.args, now)) {
    const to = states.actionTarget("auction", "close_unsold");
    if (to && states.can("auction", a.status, to)) write(a, to);
  }
  return { opened, closed };
}
function sweepAll() { let n = 0; for (const t of db().all("SELECT DISTINCT tenant_id FROM auctions")) { try { n += tick(t.tenant_id).closed; } catch (e) { } } return { closed: n }; }

/* ---------- the line term: { id } of an auction this shopper won and has not paid ---------- */
function won(ctx, value) {
  const a = db().get("SELECT * FROM auctions WHERE id=? AND tenant_id=?", Number(value && typeof value === "object" ? value.id : value), Number(ctx.tid));
  if (!a || String(a.product_id) !== String(ctx.product.id) || a.winner !== String(ctx.owner)) throw fail("That auction was not won by you", 404);
  if (!states.is("auction", a.status, "awaiting_payment")) throw fail("that auction is " + states.display("auction", a.status).label);
  if (a.pay_by && parseT(a.pay_by).getTime() < Date.now()) throw fail("the time to pay for that auction has passed");
  return a;
}
lineterms.register("auction", {
  atom: "auctions",
  clean: (ctx, value) => ({ id: won(ctx, value).id }),
  price: (ctx, value) => ({ set: Number(won(ctx, value).final_price), label: "Winning bid" }),
  maxQty: () => 1,
  place: (ctx, value) => {
    const a = db().get("SELECT * FROM auctions WHERE id=? AND tenant_id=?", Number(value.id), Number(ctx.tid));
    const to = states.actionTarget("auction", "pay");
    if (a && to && states.can("auction", a.status, to)) write(a, to, { order_id: ctx.orderId });
  }
});

module.exports = { step, create, bid, buyNow, get, forProduct, list, mine, cancel, tick, sweepAll };
