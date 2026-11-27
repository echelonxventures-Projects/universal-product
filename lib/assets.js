/* LUXORA Platform — fixed assets and depreciation (owner Value).

   What a store owns and uses for years (fixed_assets): a computer, a van, a machine. Buying one puts
   its cost on the books (lib/books.js), paid from the bank or owed to a supplier. From the month it
   comes into service it depreciates month by month — straight line, or declining balance switching
   to straight line when that charges more — never below its residual value; each month is posted
   once (depreciation_entries), when the month ends (the platform's sweep), or when staff run it up to
   a month. Selling or writing it off depreciates it to that month, takes its cost and depreciation
   off the books, and posts the gain or loss. The schedule shows every month of its life, posted or to
   come. An asset is a record on the master (lib/seed/row-records.json) moving through its machine;
   categories, methods and accounts are data (lib/seed/assets.json). */
"use strict";

const db = () => require("./db.js");
const K = require("./kernel.js");
const RR = () => require("./row-records.js");
const states = require("./states.js");
const SEED = require("./seed/assets.json");
const M = SEED.machine, R = SEED.record, A = SEED.accounts;
const B = () => require("./books.js"), W = () => require("./wallet.js");
const fail = (msg, status, code) => { const e = new Error(msg); e.status = status || 400; if (code) e.code = code; throw e; };
const N = Number;
const r2 = n => +Number(n || 0).toFixed(2);
const str = (v, n) => String(v == null ? "" : v).trim().slice(0, n || 200);
const tx = fn => K.internal.tx(fn);
const ph = xs => "(" + (xs.length ? xs.map(() => "?").join(",") : "NULL") + ")";
const tagged = (s, t) => !!s && states.has(M, s) && states.is(M, s, t);
const today = () => new Date().toISOString().slice(0, 10);
const thisMonth = () => today().slice(0, 7);
const isDate = d => /^\d{4}-\d{2}-\d{2}$/.test(String(d || "")) && !isNaN(Date.parse(d + "T00:00:00Z"));
const isMonth = m => /^\d{4}-(0[1-9]|1[0-2])$/.test(String(m || ""));
const nextMonth = m => { const [y, mo] = m.split("-").map(N); return mo === 12 ? `${y + 1}-01` : `${y}-${String(mo + 1).padStart(2, "0")}`; };
const prevMonth = m => { const [y, mo] = m.split("-").map(N); return mo === 1 ? `${y - 1}-12` : `${y}-${String(mo - 1).padStart(2, "0")}`; };
const monthsBetween = (a, b) => { const [y1, m1] = a.split("-").map(N), [y2, m2] = b.split("-").map(N); return (y2 - y1) * 12 + (m2 - m1); };
const minor = (v, unit) => Math.round(N(v || 0) * Math.pow(10, W().unitOf(unit).decimals));
const row = (tid, id) => db().get("SELECT * FROM fixed_assets WHERE id=? AND tenant_id=?", N(id), N(tid)) || fail("No such asset", 404);
const nextRef = tid => `${SEED.ref}-${N(tid)}-${String(db().get("SELECT COUNT(*) c FROM fixed_assets WHERE tenant_id=?", N(tid)).c + 1).padStart(5, "0")}`;
/* an entry on the books, in major units: lines [{ account, debit | credit }] */
function post(tid, unit, lines, op, ref, memo, idem, actor) {
  return B().post(N(tid), { unit, op, ref, memo, idem, lines: lines.filter(l => (l.debit || l.credit)).map(l => ({ account: l.account, debit: minor(l.debit, unit), credit: minor(l.credit, unit) })) }, actor || "assets");
}

/* the charge for the k-th month of an asset's life (0 first), given what is depreciated so far */
function charge(a, k, accumulated) {
  const left = r2(a.cost - a.residual - accumulated);
  if (left <= 0 || k >= a.life_months) return 0;
  if (k === a.life_months - 1) return left;
  const sl = r2((a.cost - a.residual - accumulated) / (a.life_months - k));
  const m = SEED.methods[a.method] || {};
  const amount = m.factor ? Math.max(r2((a.cost - accumulated) * m.factor / a.life_months), sl) : r2((a.cost - a.residual) / a.life_months);
  return r2(Math.min(left, amount));
}
/* { name, category, cost, residual?, life_months?, method?, acquired_on?, in_service?, paid_from?, supplier_id?, currency?, serial?, location? } — its cost goes on the books */
function register(tid, input, actor) {
  const i = input || {}, t = N(tid);
  const name = str(i.name, 160); if (!name) fail("Name the asset");
  const cat = SEED.categories.find(c => c.key === i.category) || fail("An asset is one of: " + SEED.categories.map(c => c.key).join(", "));
  const method = i.method || Object.keys(SEED.methods)[0];
  if (!SEED.methods[method]) fail("Depreciation is one of: " + Object.keys(SEED.methods).join(", "));
  const cost = r2(i.cost); if (!(cost > 0)) fail("An asset costs more than zero");
  const residual = r2(i.residual || 0); if (!(residual >= 0 && residual < cost)) fail("The residual value is zero or more and less than the cost");
  const life = i.life_months ? N(i.life_months) : cat.lifeMonths;
  if (!(Number.isInteger(life) && life >= 1 && life <= 1200)) fail("A useful life is 1 to 1200 whole months");
  const acquired = str(i.acquired_on || today(), 10), inService = str(i.in_service || acquired, 10);
  if (!isDate(acquired) || !isDate(inService)) fail("Dates are written YYYY-MM-DD");
  if (acquired > today()) fail("An asset is registered once it is bought");
  if (inService < acquired) fail("An asset comes into service on or after the day it is bought");
  const paid = SEED.paidFrom[i.paid_from || Object.keys(SEED.paidFrom)[0]] || fail("An asset is " + Object.keys(SEED.paidFrom).join(" or "));
  const paidKey = i.paid_from || Object.keys(SEED.paidFrom)[0];
  if (i.supplier_id && !db().get("SELECT id FROM suppliers WHERE id=? AND tenant_id=?", N(i.supplier_id), t)) fail("No such supplier", 404);
  const currency = str(i.currency || require("./defaults.js").currency(t), 8).toUpperCase(); W().unitOf(currency);
  return tx(() => {
    const w = RR().created(R, () => db().run(`INSERT INTO fixed_assets(tenant_id, ref, name, category, method, currency, cost, residual, life_months, acquired_on, in_service, paid_from, supplier_id, serial, location, status, created_by)
      VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`, t, nextRef(t), name, cat.key, method, currency, cost, residual, life, acquired, inService.slice(0, 7), paidKey, i.supplier_id ? N(i.supplier_id) : null,
      str(i.serial, 120), str(i.location, 120), states.initial(M), str(actor, 120)));
    const a = row(t, N(w.lastInsertRowid));
    post(t, currency, [{ account: A.cost, debit: cost }, { account: paid.account, credit: cost }], "asset_bought", a.uid, "Bought " + a.ref + " " + name, "assets:bought:" + a.uid, actor);
    return view(t, a.id);
  });
}
/* each month not yet posted, up to `through`, for one asset */
function depreciateOne(tid, a, through, actor) {
  if (!tagged(a.status, "depreciating")) return 0;
  let period = a.last_period ? nextMonth(a.last_period) : a.in_service, acc = N(a.accumulated), n = 0;
  return tx(() => {
    while (period <= through) {
      const k = monthsBetween(a.in_service, period), amount = charge(a, k, acc);
      if (amount <= 0) break;
      if (db().get("SELECT 1 FROM depreciation_entries WHERE asset_id=? AND period=?", a.id, period)) fail("This month was posted a moment ago — reload", 409);
      const j = post(tid, a.currency, [{ account: A.depreciation, debit: amount }, { account: A.accumulated, credit: amount }], "asset_depreciation", a.uid, `Depreciation ${period} ${a.ref}`, `assets:dep:${a.uid}:${period}`, actor);
      db().run("INSERT INTO depreciation_entries(tenant_id, asset_id, period, amount, journal_id) VALUES(?,?,?,?,?)", N(tid), a.id, period, amount, j || null);
      acc = r2(acc + amount); n++;
      const p = period;
      RR().change(R, a.id, () => db().run("UPDATE fixed_assets SET accumulated=?, last_period=? WHERE id=?", acc, p, a.id));
      period = nextMonth(period);
    }
    return n;
  });
}
/* every asset of a store depreciated up to a month (by default the last one that has ended) */
function depreciate(tid, through, actor) {
  const upTo = through || prevMonth(thisMonth());
  if (!isMonth(upTo)) fail("A month is written YYYY-MM");
  if (upTo > thisMonth()) fail("A month is depreciated once it has begun");
  const st = states.tagged(M, "depreciating");
  let months = 0, assets = 0;
  for (const a of db().all(`SELECT * FROM fixed_assets WHERE tenant_id=? AND status IN ${ph(st)} AND in_service<=? ORDER BY id`, N(tid), ...st, upTo)) {
    const n = depreciateOne(tid, a, upTo, actor); if (n) { months += n; assets++; }
  }
  return { through: upTo, assets, months };
}
/* sold (`proceeds`) or written off on a day: depreciated to that month, cost and depreciation off the books, the difference a gain or loss */
function dispose(tid, id, input, actor) {
  const i = input || {}, a0 = row(tid, id);
  if (!tagged(a0.status, "in_use")) fail("This asset is already gone", 409);
  const date = str(i.date || today(), 10);
  if (!isDate(date) || date > today()) fail("An asset is disposed of on a day that has come");
  if (date < a0.acquired_on) fail("An asset is disposed of after it is bought");
  const proceeds = r2(i.proceeds || 0); if (!(proceeds >= 0)) fail("Proceeds are zero or more");
  const writeOff = !!i.write_off;
  if (writeOff && proceeds) fail("A write-off has no proceeds");
  if (!str(i.reason)) fail("Say why it is " + (writeOff ? "written off" : "sold"));
  return tx(() => {
    if (date.slice(0, 7) >= a0.in_service) depreciateOne(tid, a0, date.slice(0, 7), actor);
    const a = row(tid, id), book = r2(a.cost - a.accumulated), gain = r2(proceeds - book);
    post(tid, a.currency, [{ account: A.cash, debit: proceeds }, { account: A.accumulated, debit: a.accumulated }, { account: A.cost, credit: a.cost },
      gain > 0 ? { account: A.disposal, credit: gain } : { account: A.disposal, debit: -gain }], "asset_disposed", a.uid, (writeOff ? "Wrote off " : "Sold ") + a.ref, "assets:gone:" + a.uid, actor);
    const to = states.first(M, writeOff ? "gone" : "sold"), { patch } = states.apply(M, { tenantId: N(tid), from: a.status, to, row: a });
    const all = { ...patch, disposal_date: date, proceeds, disposal_reason: str(i.reason, 300) }, cols = Object.keys(all);
    RR().change(R, a.id, () => { const w = db().run(`UPDATE fixed_assets SET ${cols.map(c => c + "=?").join(", ")} WHERE id=? AND status=?`, ...cols.map(c => all[c]), a.id, a.status); if (!w.changes) fail("This has just changed — reload it", 409); return w; });
    return { ...view(tid, id), gain };
  });
}
/* every month of an asset's life: what it charges, what is left, and whether it is posted */
function schedule(tid, id) {
  const a = row(tid, id), posted = new Map(db().all("SELECT period, amount FROM depreciation_entries WHERE asset_id=? ORDER BY period", a.id).map(e => [e.period, e.amount]));
  const out = []; let acc = 0, period = a.in_service;
  for (let k = 0; k < a.life_months; k++) {
    const amount = posted.has(period) ? posted.get(period) : tagged(a.status, "depreciating") ? charge(a, k, acc) : 0;
    if (amount <= 0 && !posted.has(period)) break;
    acc = r2(acc + amount);
    out.push({ period, amount, accumulated: acc, book: r2(a.cost - acc), posted: posted.has(period) });
    period = nextMonth(period);
  }
  return out;
}
function view(tid, id) {
  const a = row(tid, id), c = SEED.categories.find(x => x.key === a.category) || { label: a.category };
  return { ...a, categoryLabel: c.label, methodLabel: (SEED.methods[a.method] || { label: a.method }).label, book: r2(a.cost - a.accumulated), inUse: tagged(a.status, "in_use") };
}
function register_(tid, f) {
  const o = f || {};
  return db().all("SELECT id FROM fixed_assets WHERE tenant_id=? AND (?='' OR category=?) AND (?='' OR status=?) ORDER BY id DESC LIMIT 500", N(tid), str(o.category), str(o.category), str(o.status), str(o.status)).map(r => view(tid, r.id));
}
/* the register's totals by category and currency: cost, depreciation to date, book value */
function totals(tid) {
  const use = states.tagged(M, "in_use");
  return db().all(`SELECT category, currency, COUNT(*) n, SUM(cost) cost, SUM(accumulated) accumulated FROM fixed_assets WHERE tenant_id=? AND status IN ${ph(use)} GROUP BY category, currency ORDER BY category`, N(tid), ...use)
    .map(r => ({ ...r, label: (SEED.categories.find(c => c.key === r.category) || { label: r.category }).label, cost: r2(r.cost), accumulated: r2(r.accumulated), book: r2(r.cost - r.accumulated) }));
}
/* when a month ends, every store's assets are depreciated through it */
function sweepAll() {
  const st = states.tagged(M, "depreciating"), upTo = prevMonth(thisMonth());
  let n = 0;
  for (const t of db().all(`SELECT DISTINCT tenant_id FROM fixed_assets WHERE status IN ${ph(st)} AND (last_period IS NULL OR last_period<?)`, ...st, upTo)) {
    try { n += depreciate(t.tenant_id, upTo, "assets").months; } catch (e) { console.error("assets: depreciation for store " + t.tenant_id + ": " + e.message); }
  }
  return n;
}
module.exports = { register, depreciate, dispose, schedule, view, list: register_, totals, sweepAll, charge, SEED };
