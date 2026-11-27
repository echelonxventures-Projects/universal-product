/* LUXORA Platform — budgets (owner Value).

   A store's plan for a year (budgets): for each income and expense account of its books
   (lib/books.js), what it expects month by month, in one currency (budget_lines). A line is set
   month by month or as a year's amount spread evenly, and a draft can start from a year's actual
   figures with an uplift. A budget is approved — one approved budget per year and currency — and
   reopened or closed. Against it the books' actual figures show month by month and to date: an
   expense above, or income below, what was planned by more than the tolerance is flagged, and
   anything spent on an account with no budget is shown too. A budget is a record on the master
   (lib/seed/row-records.json) moving through its machine; policy is data (lib/seed/budgets.json). */
"use strict";

const db = () => require("./db.js");
const K = require("./kernel.js");
const RR = () => require("./row-records.js");
const states = require("./states.js");
const SEED = require("./seed/budgets.json");
const M = SEED.machine, R = SEED.record;
const B = () => require("./books.js");
const fail = (msg, status, code) => { const e = new Error(msg); e.status = status || 400; if (code) e.code = code; throw e; };
const N = Number;
const r2 = n => +Number(n || 0).toFixed(2);
const str = (v, n) => String(v == null ? "" : v).trim().slice(0, n || 200);
const tx = fn => K.internal.tx(fn);
const ph = xs => "(" + (xs.length ? xs.map(() => "?").join(",") : "NULL") + ")";
const tagged = (s, t) => !!s && states.has(M, s) && states.is(M, s, t);
const MONTHS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
const mm = (y, m) => `${y}-${String(m).padStart(2, "0")}-01`;
const after = (y, m) => m === 12 ? mm(y + 1, 1) : mm(y, m + 1);
const row = (tid, id) => db().get("SELECT * FROM budgets WHERE id=? AND tenant_id=?", N(id), N(tid)) || fail("No such budget", 404);
const nextRef = tid => `${SEED.ref}-${N(tid)}-${String(db().get("SELECT COUNT(*) c FROM budgets WHERE tenant_id=?", N(tid)).c + 1).padStart(5, "0")}`;
/* the accounts a budget plans: those on the profit and loss, not groups */
function plannable(tid) {
  const pl = Object.entries(B().SEED.types).filter(([, d]) => d.statement === "profit").map(([k]) => k);
  return B().accounts(tid).filter(a => !a.group && pl.includes(a.type));
}
const normalOf = type => B().SEED.types[type].normal;
function move(b, to, extra) {
  const { patch } = states.apply(M, { tenantId: b.tenant_id, from: b.status, to, row: b });
  const all = { ...patch, ...(extra || {}) }, cols = Object.keys(all);
  RR().change(R, b.id, () => { const w = db().run(`UPDATE budgets SET ${cols.map(c => c + "=?").join(", ")} WHERE id=? AND status=?`, ...cols.map(c => all[c]), b.id, b.status); if (!w.changes) fail("This has just changed — reload it", 409); return w; });
}
const totalOf = id => r2(db().get("SELECT COALESCE(SUM(amount),0) t FROM budget_lines WHERE budget_id=?", id).t);

/* { name, year, currency? } */
function create(tid, input, actor) {
  const i = input || {}, t = N(tid), name = str(i.name, 160), year = N(i.year);
  if (!name) fail("Name the budget");
  if (!(Number.isInteger(year) && year >= 2000 && year <= 2100)) fail("Say which year");
  const currency = str(i.currency || require("./defaults.js").currency(t), 8).toUpperCase(); require("./wallet.js").unitOf(currency);
  const w = RR().created(R, () => db().run("INSERT INTO budgets(tenant_id, ref, name, year, currency, status, note, created_by) VALUES(?,?,?,?,?,?,?,?)",
    t, nextRef(t), name, year, currency, states.initial(M), str(i.note, 1000), str(actor, 120)));
  return view(t, N(w.lastInsertRowid));
}
/* lines [{ account, month, amount } | { account, annual }] — an annual amount is spread evenly, the remainder in the last month; 0 clears a month */
function setLines(tid, id, lines) {
  const b = row(tid, id);
  if (!tagged(b.status, "editable")) fail("Only a draft budget is changed", 409);
  if (!Array.isArray(lines) || !lines.length) fail("Send the lines to set");
  const ok = new Map(plannable(tid).map(a => [a.code, a]));
  const cells = [];
  for (const raw of lines) {
    const l = raw || {}, code = str(l.account, 40);
    if (!ok.has(code)) fail("A budget plans the income and expense accounts of the books; " + code + " is not one");
    if (l.annual !== undefined) {
      const total = r2(l.annual); if (!(total >= 0)) fail("A budget is zero or more");
      const each = r2(Math.floor(total * 100 / 12) / 100);
      MONTHS.forEach(m => cells.push([code, m, m === 12 ? r2(total - each * 11) : each]));
    } else {
      const m = N(l.month), a = r2(l.amount);
      if (!MONTHS.includes(m)) fail("A month is 1 to 12");
      if (!(a >= 0)) fail("A budget is zero or more");
      cells.push([code, m, a]);
    }
  }
  return tx(() => {
    for (const [code, m, a] of cells) {
      if (a === 0) db().run("DELETE FROM budget_lines WHERE budget_id=? AND account=? AND month=?", b.id, code, m);
      else db().run("INSERT INTO budget_lines(budget_id, account, month, amount) VALUES(?,?,?,?) ON CONFLICT(budget_id, account, month) DO UPDATE SET amount=excluded.amount", b.id, code, m, a);
    }
    RR().change(R, b.id, () => db().run("UPDATE budgets SET total=? WHERE id=?", totalOf(b.id), b.id));
    return view(tid, id);
  });
}
/* what the books show for an account in each month of a year, in the budget's currency (normal side positive) */
function actuals(tid, year, currency) {
  const out = {};
  for (const m of MONTHS) {
    const tb = B().trialBalance(N(tid), { from: mm(year, m), to: after(year, m), currency }).find(x => x.currency === currency);
    for (const r of tb ? tb.rows : []) (out[r.account] = out[r.account] || {})[m] = r2(r.balance);
  }
  return out;
}
/* a draft filled from a year's actual figures, raised by `uplift_pct` */
function fromActuals(tid, id, input) {
  const b = row(tid, id), i = input || {}, year = N(i.year || b.year - 1), up = N(i.uplift_pct || 0);
  if (!(up >= -100 && up <= 1000)) fail("An uplift is -100 to 1000 percent");
  const act = actuals(tid, year, b.currency), ok = new Set(plannable(tid).map(a => a.code)), lines = [];
  for (const [code, months] of Object.entries(act)) if (ok.has(code)) for (const [m, v] of Object.entries(months)) if (v > 0) lines.push({ account: code, month: N(m), amount: r2(v * (1 + up / 100)) });
  if (!lines.length) fail("The books show nothing for " + year + " in " + b.currency, 409);
  return setLines(tid, id, lines);
}
function approve(tid, id, actor) {
  const b = row(tid, id);
  if (!tagged(b.status, "editable")) fail("Only a draft budget is approved", 409);
  if (!totalOf(b.id)) fail("A budget plans something before it is approved");
  const live = states.tagged(M, "live"), other = db().get(`SELECT ref FROM budgets WHERE tenant_id=? AND year=? AND currency=? AND status IN ${ph(live)} AND id<>?`, N(tid), b.year, b.currency, ...live, b.id);
  if (other) fail(other.ref + " is already the approved budget for " + b.year + " in " + b.currency, 409, "one_approved");
  move(b, states.first(M, "approved"), { approved_by: str(actor, 120) });
  return view(tid, id);
}
function reopen(tid, id) { const b = row(tid, id); if (!tagged(b.status, "live")) fail("Only an approved budget is reopened", 409); move(b, states.first(M, "editable"), { approved_by: "", approved_at: null }); return view(tid, id); }
function close(tid, id) { const b = row(tid, id); if (!tagged(b.status, "live")) fail("Only an approved budget is closed", 409); move(b, states.first(M, "closed")); return view(tid, id); }
function view(tid, id) {
  const b = row(tid, id);
  const lines = db().all("SELECT account, month, amount FROM budget_lines WHERE budget_id=? ORDER BY account, month", b.id);
  const names = new Map(B().accounts(tid).map(a => [a.code, a.name]));
  const by = {};
  for (const l of lines) (by[l.account] = by[l.account] || { account: l.account, name: names.get(l.account) || l.account, months: Object.fromEntries(MONTHS.map(m => [m, 0])), total: 0 }).months[l.month] = l.amount;
  for (const x of Object.values(by)) x.total = r2(Object.values(x.months).reduce((s, v) => s + v, 0));
  return { ...b, total: totalOf(b.id), lines: Object.values(by), editable: tagged(b.status, "editable"), live: tagged(b.status, "live") };
}
function list(tid) { return db().all("SELECT id FROM budgets WHERE tenant_id=? ORDER BY year DESC, id DESC LIMIT 200", N(tid)).map(r => view(tid, r.id)); }
/* budget against the books, month by month and to date (through month `through`, 1–12): each account's variance, and whether it is off plan */
function report(tid, id, f) {
  const b = view(tid, id), o = f || {}, now = new Date();
  const through = N(o.through) || (b.year < now.getUTCFullYear() ? 12 : b.year > now.getUTCFullYear() ? 0 : now.getUTCMonth() + 1);
  if (!(through >= 0 && through <= 12)) fail("Through a month, 1 to 12");
  const act = actuals(tid, b.year, b.currency), chart = new Map(B().accounts(tid).map(a => [a.code, a])), tol = N(SEED.tolerancePct) / 100;
  const codes = [...new Set([...b.lines.map(l => l.account), ...Object.keys(act).filter(c => plannable(tid).some(a => a.code === c))])];
  const rows = codes.map(code => {
    const a = chart.get(code) || { name: code, type: "expense" }, line = b.lines.find(l => l.account === code), income = normalOf(a.type) === SEED.earns;
    const months = MONTHS.map(m => { const bud = line ? line.months[m] : 0, act_ = (act[code] || {})[m] || 0; return { month: m, budget: bud, actual: act_, variance: r2(act_ - bud) }; });
    const upto = months.filter(m => m.month <= through), budget = r2(upto.reduce((s, m) => s + m.budget, 0)), actual = r2(upto.reduce((s, m) => s + m.actual, 0));
    const year = line ? line.total : 0;
    /* off plan: spending above, or income below, what was planned to date by more than the tolerance */
    const off = !line ? actual !== 0 : income ? actual < budget * (1 - tol) : actual > budget * (1 + tol);
    return { account: code, name: a.name, type: a.type, income, budgeted: !!line, year, budget, actual, variance: r2(actual - budget), usedPct: budget ? +(actual * 100 / budget).toFixed(1) : null, off, months };
  });
  const sum = (xs, k) => r2(xs.reduce((s, r) => s + r[k], 0));
  const inc = rows.filter(r => r.income), exp = rows.filter(r => !r.income);
  return { budget: { id: b.id, ref: b.ref, name: b.name, year: b.year, currency: b.currency, status: b.status }, through, tolerancePct: SEED.tolerancePct, rows,
    totals: { income: { budget: sum(inc, "budget"), actual: sum(inc, "actual") }, expense: { budget: sum(exp, "budget"), actual: sum(exp, "actual") },
      profit: { budget: r2(sum(inc, "budget") - sum(exp, "budget")), actual: r2(sum(inc, "actual") - sum(exp, "actual")) } },
    off: rows.filter(r => r.off).map(r => r.account) };
}
module.exports = { plannable, create, setLines, fromActuals, approve, reopen, close, view, list, report, SEED };
