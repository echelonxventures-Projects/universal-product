/* LUXORA Platform — service fees: what a store adds to an order when its rules say.

   A fee is a store's rule row: an amount and/or a share of the order, charged when its conditions
   hold — the order is under an amount (a small-order fee), the store's local hour is in a window
   (a late-night fee), always (a service or packing fee) — and waived where the rule says (for a
   member, or when an offer already makes shipping free). Whether a fee is taxed is the rule's.
   The cart and checkout add the fees to the order's total and keep them on the order.
   Capability: service_fees. */
"use strict";

const db = () => require("./db.js");
const caps = () => require("./capabilities.js");
const fail = (msg, status) => Object.assign(new Error(msg), { status: status || 400 });
const r2 = n => +Number(n || 0).toFixed(2);
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };

const on = tid => caps().on(Number(tid), "service_fees");
function params(tid) {
  if (!on(tid)) throw fail("Service fees are not available in this store", 403);
  return caps().cap(Number(tid), "service_fees");
}

/* ---------- the store's fee rules ---------- */
const CODE_RE = /^[a-z0-9][a-z0-9_-]{0,39}$/;
function rules(tid) { return db().all("SELECT * FROM order_charge_rules WHERE tenant_id=? ORDER BY position, id", Number(tid)).map(r => ({ ...r, active: !!r.active, taxable: !!r.taxable, waive_for_members: !!r.waive_for_members, waive_with_free_shipping: !!r.waive_with_free_shipping })); }
function saveRule(tid, input) {
  params(tid);
  const i = input || {};
  const code = String(i.code || "").trim().toLowerCase();
  if (!CODE_RE.test(code)) throw fail("A fee needs a short code: lowercase letters, digits, - or _");
  const name = String(i.name || "").trim().slice(0, 80);
  if (!name) throw fail("A fee needs a name the shopper reads");
  const amount = Math.max(0, r2(i.amount)), percent = Math.max(0, Math.min(100, Number(i.percent) || 0));
  if (!amount && !percent) throw fail("A fee is an amount, a share of the order, or both");
  const hour = v => (v === "" || v == null ? null : Math.max(0, Math.min(23, Math.floor(Number(v)))));
  const vals = [code, name, amount, percent, i.below_amount === "" || i.below_amount == null ? null : Math.max(0, r2(i.below_amount)), hour(i.from_hour), hour(i.to_hour),
    i.waive_for_members ? 1 : 0, i.waive_with_free_shipping ? 1 : 0, i.taxable ? 1 : 0, i.active === false || i.active === 0 ? 0 : 1, Math.floor(Number(i.position) || 0)];
  const ex = db().get("SELECT id FROM order_charge_rules WHERE tenant_id=? AND code=?", Number(tid), code);
  if (ex) db().run("UPDATE order_charge_rules SET code=?,name=?,amount=?,percent=?,below_amount=?,from_hour=?,to_hour=?,waive_for_members=?,waive_with_free_shipping=?,taxable=?,active=?,position=? WHERE id=?", ...vals, ex.id);
  else db().run("INSERT INTO order_charge_rules(tenant_id,code,name,amount,percent,below_amount,from_hour,to_hour,waive_for_members,waive_with_free_shipping,taxable,active,position) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", Number(tid), ...vals);
  return rules(tid).find(r => r.code === code);
}
function removeRule(tid, code) {
  params(tid);
  if (!db().run("DELETE FROM order_charge_rules WHERE tenant_id=? AND code=?", Number(tid), String(code)).changes) throw fail("Unknown fee", 404);
  return { ok: true };
}

/* ---------- what an order is charged ---------- */
function localHour(tid) {
  let zone = null; try { zone = require("./time.js").zoneOfStore(Number(tid)); } catch (e) { zone = null; }
  try { return Number(new Intl.DateTimeFormat("en-US", { hour: "numeric", hourCycle: "h23", timeZone: zone || undefined }).format(new Date())); } catch (e) { return new Date().getUTCHours(); }
}
const inWindow = (h, from, to) => from == null || to == null ? true : from <= to ? h >= from && h < to : h >= from || h < to;
const member = (tid, owner) => { try { return !!require("./recurring.js").membershipOf(Number(tid), owner); } catch (e) { return false; } };
/* the fees on a bag: { lines: [{ code, name, amount, taxable }], total, taxable } */
function forBag(tid, owner, o) {
  if (!on(tid)) return { lines: [], total: 0, taxable: 0 };
  const net = Number(o.net) || 0;
  if (!(net > 0)) return { lines: [], total: 0, taxable: 0 };
  const h = localHour(tid), isMember = member(tid, owner);
  const lines = [];
  for (const r of rules(tid)) {
    if (!r.active) continue;
    if (r.below_amount != null && net >= r.below_amount) continue;
    if (!inWindow(h, r.from_hour, r.to_hour)) continue;
    if (r.waive_for_members && isMember) continue;
    if (r.waive_with_free_shipping && o.freeShip) continue;
    const amount = r2(r.amount + net * r.percent / 100);
    if (amount > 0) lines.push({ code: r.code, name: r.name, amount, taxable: r.taxable });
  }
  return { lines, total: r2(lines.reduce((n, l) => n + l.amount, 0)), taxable: r2(lines.filter(l => l.taxable).reduce((n, l) => n + l.amount, 0)) };
}

module.exports = { on, rules, saveRule, removeRule, forBag };
