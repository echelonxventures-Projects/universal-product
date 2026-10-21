/* LUXORA Platform — tips: what a shopper adds for whoever serves them.

   A tip is the shopper's own choice among the amounts the capability offers, or their own amount
   up to its limit, kept with their bag until the order takes it; the cart and checkout add it to
   the order's total and keep it on the order. Capability: tips. */
"use strict";

const db = () => require("./db.js");
const caps = () => require("./capabilities.js");
const fail = (msg, status) => Object.assign(new Error(msg), { status: status || 400 });
const r2 = n => +Number(n || 0).toFixed(2);

const on = tid => caps().on(Number(tid), "tips");
function params(tid) {
  if (!on(tid)) throw fail("This store does not take tips", 403);
  return caps().cap(Number(tid), "tips");
}
/* the amounts the store offers (a comma-separated param) */
const choices = P => String(P.choices || "").split(",").map(x => Number(x.trim())).filter(x => x > 0);
function tipOf(tid, owner) { if (!on(tid)) return 0; const r = db().get("SELECT amount FROM bag_tips WHERE tenant_id=? AND owner=?", Number(tid), String(owner)); return r ? Number(r.amount) : 0; }
function setTip(tid, owner, amount) {
  const P = params(tid);
  const a = r2(amount);
  if (a < 0 || a > Number(P.max)) throw fail("A tip is between 0 and " + P.max);
  if (a === 0) db().run("DELETE FROM bag_tips WHERE tenant_id=? AND owner=?", Number(tid), String(owner));
  else db().run("INSERT INTO bag_tips(tenant_id,owner,amount) VALUES(?,?,?) ON CONFLICT(tenant_id,owner) DO UPDATE SET amount=excluded.amount", Number(tid), String(owner), a);
  return { tip: a, choices: choices(P) };
}
/* the tip on a bag as an order line: { lines, total } */
function forBag(tid, owner) {
  const a = tipOf(tid, owner);
  return a > 0 ? { lines: [{ code: "", name: String(params(tid).label || ""), amount: a, taxable: false }], total: a } : { lines: [], total: 0 };
}
/* once an order has taken it, the tip is spent */
function taken(tid, owner) { db().run("DELETE FROM bag_tips WHERE tenant_id=? AND owner=?", Number(tid), String(owner)); }
function vocabulary(tid) { const P = on(tid) ? params(tid) : {}; return { on: on(tid), choices: choices(P), max: P.max || 0, label: P.label || "" }; }

module.exports = { on, tipOf, setTip, forBag, taken, vocabulary };
