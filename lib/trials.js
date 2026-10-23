/* LUXORA Platform — try and buy: take it home, pay for what you keep.

   A shopper puts an item in the bag "on trial" — the `trial` line term — where the store allows
   it (items whose facts declare the trial attribute the capability names, or every item when it
   names none). The line costs only the capability's deposit share at checkout. The order leaves a
   trial: within the window the shopper keeps the item (the rest of its price is charged to their
   wallet) or returns it (the deposit comes back, and the return is the store's to collect). When
   the window closes, what was not returned is kept. A trial's life is the `trial` state machine,
   asked by tag (open, kept, returned). Capability: try_and_buy. */
"use strict";

const db = () => require("./db.js");
const caps = () => require("./capabilities.js");
const states = require("./states.js");
const lineterms = require("./lineterms.js");
const fail = lineterms.fail;
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };
const r2 = n => +Number(n || 0).toFixed(2);
const sqlIn = days => new Date(Date.now() + Number(days) * 86400000).toISOString().slice(0, 19).replace("T", " ");
const sqlNow = () => new Date().toISOString().slice(0, 19).replace("T", " ");
const tell = (...a) => require("./tell.js").tell(...a);

function params(tid) {
  const P = caps().cap(Number(tid), "try_and_buy");
  if (!Object.keys(P).length) throw fail("Try and buy is not available in this store", 403);
  return P;
}
/* may this item go on trial: the capability names the fact that allows it, or allows every item */
function allowed(tid, product) {
  const P = params(tid);
  return !P.allow_attr || !!J(product.attrs, {})[P.allow_attr];
}

/* the line term: { on: true } — the line costs the deposit share of its price now */
lineterms.register("trial", {
  atom: "try_and_buy",
  clean: (ctx, value) => {
    if (!value) return null;
    if (!ctx.signedIn && ctx.signedIn !== undefined) throw fail("Sign in to try before you buy", 401);
    if (!allowed(ctx.tid, ctx.product)) throw fail("This item cannot be tried before buying");
    return { on: true };
  },
  price: (ctx) => {
    const P = params(ctx.tid);
    /* the deposit share replaces the price now; the rest is charged when the item is kept */
    return { set: r2(Number(ctx.product.price) * Number(P.deposit_percent) / 100), label: "On trial · pay " + P.deposit_percent + "% now, the rest if you keep it" };
  },
  maxQty: (ctx) => Number(params(ctx.tid).max_qty) || 1,
  place: (ctx) => {
    const P = params(ctx.tid);
    /* the product's own price (what reaches an order hook is the storefront's view of it) */
    const unit = Number((db().get("SELECT price FROM products WHERE tenant_id=? AND id=?", Number(ctx.tid), ctx.product.id) || {}).price), deposit = r2(unit * Number(P.deposit_percent) / 100);
    db().run("INSERT INTO trials(tenant_id,order_id,product_id,owner,qty,unit,deposit,ends_at,status) VALUES(?,?,?,?,?,?,?,?,?)",
      Number(ctx.tid), Number(ctx.orderId), ctx.product.id, String(ctx.owner || ""), Number(ctx.qty) || 1, unit, deposit, sqlIn(P.window_days), states.initial("trial"));
  }
});

function present(t) { return { ...t, state: states.display("trial", t.status), next: states.next("trial", t.status), open: states.is("trial", t.status, "open") }; }
function write(t, action, patch) {
  const to = states.actionTarget("trial", action);
  if (!to || !states.can("trial", t.status, to)) throw fail("This trial has already been decided", 409);
  const mv = states.apply("trial", { tenantId: t.tenant_id, from: t.status, to, row: t });
  const p = { ...mv.patch, ...(patch || {}) };
  const cols = Object.keys(p);
  db().run("UPDATE trials SET " + cols.map(c => c + "=?").join(", ") + " WHERE id=?", ...cols.map(c => p[c]), t.id);
  return present(db().get("SELECT * FROM trials WHERE id=?", t.id));
}
/* keeping: the rest of the price is charged to the shopper's wallet */
function keep(t, auto) {
  const P = params(t.tenant_id);
  const rest = r2((t.unit - t.deposit) * t.qty);
  if (rest > 0) require("./offers.js").debit(t.tenant_id, t.owner, rest, String(P.ledger_kind || ""), "trial:" + t.id, null, "try_and_buy");
  const out = write(t, auto ? "lapse" : "keep", { charged: rest });
  tell(t.tenant_id, t.owner, "trial", auto ? "Your trial ended — the item is yours" : "You kept your item", rest ? rest + " charged" : "", "orders.html");
  return out;
}
/* returning: the deposit comes back */
function giveBack(t) {
  const P = params(t.tenant_id);
  const back = r2(t.deposit * t.qty);
  if (back > 0) require("./offers.js").credit(t.tenant_id, t.owner, back, String(P.refund_kind || ""), "trial:" + t.id, null, "try_and_buy");
  return write(t, "return", { refunded: back });
}
function decide(tid, owner, id, action) {
  params(tid);
  const t = db().get("SELECT * FROM trials WHERE id=? AND tenant_id=? AND owner=?", Number(id), Number(tid), String(owner));
  if (!t) throw fail("Trial not found", 404);
  if (!states.is("trial", t.status, "open")) throw fail("This trial has already been decided", 409);
  const to = states.actionTarget("trial", action);
  if (!to) throw fail("Keep it or return it");
  return states.is("trial", to, "kept") ? keep(t, false) : giveBack(t);
}
/* a closed window keeps what was not returned */
function sweepAll() {
  let n = 0;
  for (const t of db().all("SELECT * FROM trials WHERE ends_at<?", sqlNow())) {
    if (!states.is("trial", t.status, "open") || !caps().on(t.tenant_id, "try_and_buy")) continue;
    /* a keep the shopper's wallet cannot pay stays open (the rest is not given away); they are told once */
    try { keep(t, true); n++; } catch (e) {
      if (e.code === "insufficient_available") { if (!t.notified_short) { db().run("UPDATE trials SET notified_short=1 WHERE id=?", t.id); tell(t.tenant_id, t.owner, "trial", "Top up to keep your item", "The rest of the price could not be taken from your wallet — top up or return the item.", "orders.html"); } }
      else console.error("trial sweep:", e.message);
    }
  }
  return n;
}
function mine(tid, owner) { params(tid); return db().all("SELECT * FROM trials WHERE tenant_id=? AND owner=? ORDER BY id DESC LIMIT 200", Number(tid), String(owner)).map(present); }
function all(tid) { params(tid); return db().all("SELECT * FROM trials WHERE tenant_id=? ORDER BY id DESC LIMIT 300", Number(tid)).map(present); }
/* what a shopper may do with a trial: the actions into states tagged by_shopper */
function vocabulary() { return { actions: Object.entries(states.actions("trial")).filter(([, to]) => states.is("trial", to, "by_shopper")).map(([verb, to]) => ({ verb, to, label: states.display("trial", to).label })) }; }

module.exports = { allowed, decide, sweepAll, mine, all, vocabulary };
