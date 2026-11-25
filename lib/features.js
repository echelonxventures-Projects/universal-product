/* LUXORA Platform — shopper features: the frame every feature of a store stands in.

   A feature is declared (lib/seed/features.json): the capability that switches it on, the console
   screen that sets it up, and the fields of the rows a store keeps for it. Its engine
   (lib/features/<key>.js) is found in the folder, never listed, and says only what it does at the
   points the platform asks:
     price     ({tid, owner, product, qty, unit})      a lower unit price, and why
     rule      ({tid, owner, product, qty, terms})     what stops a line, or the most of it
     charges   ({tid, owner, net, items, body})        what an order adds, or takes off
     payment   ({tid, body, gateway, net})             what the gateway is also told
     delivery  ({tid, owner, items, body})             what stops a delivery, what it adds, days
     block     ({tid, owner, product})                 what the item's page says
     placed    ({tid, owner, order, items, body})      an order was placed
     moved     ({tid, order, to})                      an order moved on
     mine      ({tid, owner})                          what a shopper sees of it on their account
     open      ({tid, owner, query})                   what it shows anyone
     actions   { name: ({tid, owner, body, notify}) }  what a shopper may do
     staff     { list({tid}), actions: { name: ({tid, id, body, actor}) } }
     term      a line term (lib/lineterms.js)
     sweep     ({tid})                                 what its clock does
   A feature that is off is never asked. */
"use strict";

const fs = require("fs"), path = require("path");
const db = () => require("./db.js");
const caps = () => require("./capabilities.js");
const lineterms = require("./lineterms.js");
const fail = lineterms.fail;
const SEED = require("./seed/features.json").FEATURES;
const DIR = path.join(__dirname, "features");
const J = (v, d) => { try { return v ? JSON.parse(v) : d; } catch (e) { return d; } };
const defs = new Map(SEED.map(f => [f.key, f]));
const engines = new Map();
/* asked for every line and item shown: remembered for a moment per store and feature */
const SEEN = new Map();
function on(tid, key) {
  const k = Number(tid) + ":" + key, h = SEEN.get(k);
  if (h && Date.now() - h.at < 1000) return h.v;
  const d = defs.get(key), v = !!d && caps().on(Number(tid), d.atom || key);
  if (SEEN.size > 5000) SEEN.clear();
  SEEN.set(k, { at: Date.now(), v }); return v;
}
const params = (tid, key) => caps().cap(Number(tid), (defs.get(key) || {}).atom || key) || {};
function need(tid, key) { const d = defs.get(key); if (!d) throw fail("Unknown feature", 404); if (!on(tid, key)) throw fail(d.title + " is not available in this store", 403); return d; }

/* ---------- the store's rows, each field as its declaration says ---------- */
const today = () => new Date().toISOString().slice(0, 10);
const CHECK = {
  text: v => String(v).trim().slice(0, 400), textarea: v => String(v).trim().slice(0, 20000),
  number: v => { const n = Number(v); if (!isFinite(n)) throw 0; return n; }, int: v => { const n = Number(v); if (!Number.isInteger(n)) throw 0; return n; },
  bool: v => v === true || v === 1 || v === "1" || v === "true" || v === "on",
  date: v => { if (!/^\d{4}-\d\d-\d\d$/.test(v) || isNaN(Date.parse(v))) throw 0; return v; },
  datetime: v => { const d = new Date(v); if (isNaN(d)) throw 0; return d.toISOString(); },
  time: v => { if (!/^([01]\d|2[0-3]):[0-5]\d$/.test(v)) throw 0; return v; },
  weekday: v => { const n = Number(v); if (!Number.isInteger(n) || n < 0 || n > 6) throw 0; return n; },
  url: v => { if (!/^https:\/\/[^\s]+$/.test(v)) throw 0; return String(v).slice(0, 500); },
  product: (v, tid) => { if (!db().get("SELECT 1 x FROM products WHERE tenant_id=? AND id=? AND deleted_at IS NULL", Number(tid), String(v))) throw 0; return String(v); },
  choice: (v, tid, f) => { if (!f.options.includes(String(v))) throw 0; return String(v); }
};
function read(tid, d, input) {
  const out = {};
  for (const f of d.fields || []) {
    const v = (input || {})[f.key];
    if (v == null || v === "") { if (f.required) throw fail(f.label + " is needed"); out[f.key] = f.default != null ? f.default : null; continue; }
    let x; try { x = CHECK[f.type](v, tid, f); } catch (e) { throw fail(f.label + " is not valid"); }
    if (typeof x === "number" && ((f.min != null && x < f.min) || (f.max != null && x > f.max))) throw fail(f.label + " is out of range");
    out[f.key] = x;
  }
  const e = engines.get(d.key);
  return e && e.check ? (e.check(out, tid) || out) : out;
}
const present = r => ({ id: r.id, ...J(r.data, {}) });
/* rows are read on every line priced: kept for a moment, dropped when one is written */
const ROWS = new Map();
function rows(tid, key) {
  const k = Number(tid) + ":" + key, h = ROWS.get(k);
  if (h && Date.now() - h.at < 1000) return h.v;
  const v = db().all("SELECT * FROM feature_rows WHERE tenant_id=? AND feature=? ORDER BY id", Number(tid), key).map(present);
  if (ROWS.size > 2000) ROWS.clear();
  ROWS.set(k, { at: Date.now(), v }); return v;
}
const bust = (tid, key) => { ROWS.delete(Number(tid) + ":" + key); SEEN.delete(Number(tid) + ":" + key); };
function save(tid, key, input) {
  const d = need(tid, key), data = JSON.stringify(read(tid, d, input));
  if (input && input.id) { if (!db().run("UPDATE feature_rows SET data=? WHERE id=? AND tenant_id=? AND feature=?", data, Number(input.id), Number(tid), key).changes) throw fail("Not found", 404); }
  else db().run("INSERT INTO feature_rows(tenant_id,feature,data) VALUES(?,?,?)", Number(tid), key, data);
  bust(tid, key); return rows(tid, key);
}
function remove(tid, key, id) { if (!db().run("DELETE FROM feature_rows WHERE id=? AND tenant_id=? AND feature=?", Number(id), Number(tid), key).changes) throw fail("Not found", 404); bust(tid, key); return rows(tid, key); }
/* a feature's records (what shoppers and staff make of it): an owner, what it is about, and its data */
function record(tid, key, o) { return Number(db().run("INSERT INTO feature_records(tenant_id,feature,owner,about,state,data) VALUES(?,?,?,?,?,?)", Number(tid), key, String(o.owner || ""), String(o.about || ""), String(o.state || ""), JSON.stringify(o.data || {})).lastInsertRowid); }
const rec = r => r && ({ id: r.id, owner: r.owner, about: r.about, state: r.state, at: r.created_at, ...J(r.data, {}) });
function records(tid, key, w) {
  const where = ["tenant_id=?", "feature=?"], args = [Number(tid), key];
  for (const c of ["owner", "about", "state", "id"]) if (w && w[c] != null) { where.push(c + "=?"); args.push(c === "id" ? Number(w[c]) : String(w[c])); }
  return db().all("SELECT * FROM feature_records WHERE " + where.join(" AND ") + " ORDER BY id DESC LIMIT " + (Number((w || {}).limit) || 300), ...args).map(rec);
}
/* moves a record on from the state it is in: false when someone else has moved it already */
function change(tid, key, id, from, to, data) {
  const r = db().get("SELECT * FROM feature_records WHERE id=? AND tenant_id=? AND feature=?", Number(id), Number(tid), key);
  if (!r || (from != null && r.state !== from)) return false;
  return !!db().run("UPDATE feature_records SET state=?, data=? WHERE id=? AND state=?", to, JSON.stringify({ ...J(r.data, {}), ...(data || {}) }), r.id, r.state).changes;
}
const forget = (tid, key, id) => db().run("DELETE FROM feature_records WHERE id=? AND tenant_id=? AND feature=?", Number(id), Number(tid), key);

/* ---------- the engines ---------- */
for (const f of fs.readdirSync(DIR).filter(x => x.endsWith(".js")).sort()) {
  const key = f.replace(/\.js$/, ""), e = require("./features/" + f);
  engines.set(key, e);
  if (e.term) lineterms.register(e.term.key, { atom: (defs.get(key) || {}).atom || key, ...e.term });
}
const ask = (tid, what) => [...engines].filter(([k, e]) => e[what] && on(tid, k)).map(([k, e]) => [k, e]);
/* the lowest price any feature gives this line, and what it is called */
function price(ctx) {
  let best = { unit: ctx.unit, label: "" };
  for (const [, e] of ask(ctx.tid, "price")) { const p = e.price(ctx); if (p && p.unit >= 0 && p.unit < best.unit) best = p; }
  return best;
}
function rule(ctx) {
  const out = { problems: [], maxQty: Infinity };
  for (const [, e] of ask(ctx.tid, "rule")) { const r = e.rule(ctx); if (!r) continue; if (r.problem) out.problems.push(r.problem); if (r.maxQty != null) out.maxQty = Math.min(out.maxQty, r.maxQty); }
  return out;
}
function charges(ctx) { return ask(ctx.tid, "charges").flatMap(([k, e]) => (e.charges(ctx) || []).map(l => ({ taxable: false, code: k, ...l, amount: +Number(l.amount).toFixed(2) }))).filter(l => l.amount); }
function delivery(ctx) {
  const out = { fee: 0, days: 0, free: false, problem: null };
  for (const [, e] of ask(ctx.tid, "delivery")) { const r = e.delivery(ctx); if (!r) continue; out.fee += Number(r.fee || 0); out.days = Math.max(out.days, Number(r.days || 0)); out.free = out.free || !!r.free; out.problem = out.problem || r.problem || null; }
  return out;
}
/* what a feature adds to the request the gateway is sent */
const payment = ctx => Object.assign({}, ...ask(ctx.tid, "payment").map(([, e]) => e.payment(ctx) || {}));
const blocks = ctx => ask(ctx.tid, "block").map(([k, e]) => { const b = e.block(ctx); return b && { key: k, icon: defs.get(k).icon, ...b }; }).filter(Boolean);
/* what follows an order never stops it: one that fails is logged with its feature's name */
function tellAll(what, ctx) { for (const [k, e] of ask(ctx.tid, what)) { try { e[what](ctx); } catch (x) { console.error("feature " + k + " " + what + ":", x.message); } } }
const placed = ctx => tellAll("placed", ctx), moved = ctx => tellAll("moved", ctx);
const mine = ctx => ask(ctx.tid, "mine").map(([k, e]) => ({ key: k, title: defs.get(k).icon + " " + defs.get(k).title, rows: e.mine(ctx) || [] })).filter(x => x.rows.length);
const open = (key, ctx) => { need(ctx.tid, key); const e = engines.get(key); if (!e || !e.open) throw fail("Nothing to show", 404); return e.open(ctx); };
function act(key, action, ctx) { need(ctx.tid, key); const e = engines.get(key), fn = e && e.actions && Object.hasOwn(e.actions, action) && e.actions[action]; if (!fn) throw fail("Unknown action", 404); return fn(ctx); }
function staffAct(key, action, ctx) { need(ctx.tid, key); const e = engines.get(key), fn = e && e.staff && e.staff.actions && Object.hasOwn(e.staff.actions, action) && e.staff.actions[action]; if (!fn) throw fail("Unknown action", 404); return fn(ctx); }
const staffList = (tid, key) => { const e = engines.get(key); return e && e.staff && e.staff.list ? e.staff.list({ tid }) : []; };
async function sweepAll() {
  for (const [k, e] of engines) if (e.sweep) for (const t of db().all("SELECT id FROM tenants")) if (on(t.id, k)) { try { await e.sweep({ tid: t.id }); } catch (x) { console.error("feature " + k + " sweep:", x.message); } }
}
/* does a row name this item: the item itself, its brand or its department, or everything */
const names = (row, p) => !row.target || row.target === "*" || [p.id, p.brand, p.dept].some(x => String(x || "").toLowerCase() === String(row.target).toLowerCase());

module.exports = { defs, on, params, need, rows, save, remove, record, records, change, forget, price, rule, charges, delivery, payment, blocks, placed, moved, mine, open, act, staffAct, staffList, sweepAll, names, today, fail, engines };
