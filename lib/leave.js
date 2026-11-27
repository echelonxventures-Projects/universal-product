/* LUXORA Platform — leave (owner Operations).

   Time away a store's people ask for (leave_requests): a kind of leave (lib/seed/leave.json, or
   the store's own in settings leave.types), from one day to another, counted in working days.
   Each kind gives a number of days a year — a person's own allowance for a year overrides it
   (leave_allowances) — and carries some of what is left into the next year; unpaid leave has no
   limit. A request is refused when it overlaps one already asked for, or asks for more than is
   left. Someone other than the person it is for, or whoever asked, approves it or turns it down
   with a reason; approved, each of its days shows in attendance — paid leave as leave, unpaid as
   absent — so payroll pays or deducts it, and the resource plan takes it off the person's capacity
   (lib/consulting.js). Leave not yet started can be cancelled, and its days come back.

   A request is a record on the master (lib/seed/row-records.json) moving through its machine
   (lib/seed/states.json); why it was asked for stays in the table. */
"use strict";

const db = () => require("./db.js");
const K = require("./kernel.js");
const RR = () => require("./row-records.js");
const states = require("./states.js");
const SEED = require("./seed/leave.json");
const M = SEED.machine, R = SEED.record;
const fail = (msg, status, code) => { const e = new Error(msg); e.status = status || 400; if (code) e.code = code; throw e; };
const N = Number;
const r2 = n => +Number(n || 0).toFixed(2);
const str = (v, n) => String(v == null ? "" : v).trim().slice(0, n || 200);
const tx = fn => K.internal.tx(fn);
const ph = xs => "(" + (xs.length ? xs.map(() => "?").join(",") : "NULL") + ")";
const tagged = (s, t) => !!s && states.has(M, s) && states.is(M, s, t);
const today = () => new Date().toISOString().slice(0, 10);
const isDate = d => /^\d{4}-\d{2}-\d{2}$/.test(String(d || "")) && !isNaN(Date.parse(d + "T00:00:00Z"));
const addDays = (d, n) => { const x = new Date(d + "T00:00:00Z"); x.setUTCDate(x.getUTCDate() + n); return x.toISOString().slice(0, 10); };
const own = tid => require("./settings.js").get(N(tid), "leave") || {};
const types = tid => { const t = own(tid).types; return Array.isArray(t) && t.length ? t : SEED.types; };
const workingDays = tid => { const w = own(tid).workingDays; return Array.isArray(w) && w.length ? w.map(N) : SEED.workingDays; };
const typeOf = (tid, key) => types(tid).find(t => t.key === String(key)) || fail("Leave is one of: " + types(tid).map(t => t.key).join(", "));
const personRow = (tid, id) => db().get("SELECT * FROM employees WHERE id=? AND tenant_id=?", N(id), N(tid)) || fail("No such person", 404);
const by = a => str(a, 120);

/* the working days from one date to another, inclusive */
function daysIn(tid, from, to) {
  const w = new Set(workingDays(tid)), out = [];
  for (let d = from; d <= to; d = addDays(d, 1)) if (w.has(new Date(d + "T00:00:00Z").getUTCDay())) out.push(d);
  return out;
}
const yearSpan = y => [y + "-01-01", y + "-12-31"];
/* how many days of a request fall in a year */
function daysOfIn(tid, r, year) {
  const [a, b] = yearSpan(year), from = r.from_date > a ? r.from_date : a, to = r.to_date < b ? r.to_date : b;
  if (from > to) return 0;
  return r.half_day ? 0.5 : daysIn(tid, from, to).length;
}
/* what a person is entitled to of a kind in a year: their own allowance, else the kind's (null: no limit) */
function entitled(tid, empId, year, t) {
  const a = db().get("SELECT days FROM leave_allowances WHERE tenant_id=? AND employee_id=? AND year=? AND type=?", N(tid), N(empId), N(year), t.key);
  return a ? N(a.days) : t.daysPerYear == null ? null : N(t.daysPerYear);
}
function used(tid, empId, year, typeKey, tag, except) {
  const st = states.tagged(M, tag), [a, b] = yearSpan(year);
  return r2(db().all(`SELECT * FROM leave_requests WHERE tenant_id=? AND employee_id=? AND type=? AND status IN ${ph(st)} AND from_date<=? AND to_date>=? AND id<>?`,
    N(tid), N(empId), typeKey, ...st, b, a, N(except) || 0).reduce((s, r) => s + daysOfIn(tid, r, year), 0));
}
/* each kind of leave for a person in a year: entitled, carried in, taken, waiting for approval, left */
function balance(tid, empId, year, except) {
  personRow(tid, empId);
  const y = N(year) || N(today().slice(0, 4));
  return types(tid).map(t => {
    const ent = entitled(tid, empId, y, t);
    if (ent == null) return { type: t.key, label: t.label, paid: !!t.paid, limited: false, entitled: null, carried: 0, taken: used(tid, empId, y, t.key, "taken", except), pending: used(tid, empId, y, t.key, "pending", except), left: null };
    const prev = entitled(tid, empId, y - 1, t);
    const carried = N(t.carryOver) > 0 && prev != null ? Math.min(N(t.carryOver), Math.max(0, prev - used(tid, empId, y - 1, t.key, "taken", except))) : 0;
    const taken = used(tid, empId, y, t.key, "taken", except), pending = used(tid, empId, y, t.key, "pending", except);
    return { type: t.key, label: t.label, paid: !!t.paid, limited: true, entitled: ent, carried, taken, pending, left: r2(ent + carried - taken - pending) };
  });
}
/* there is room for a request in every year it touches */
function room(tid, r, except) {
  const t = typeOf(tid, r.type);
  for (let y = N(r.from_date.slice(0, 4)); y <= N(r.to_date.slice(0, 4)); y++) {
    const b = balance(tid, r.employee_id, y, except).find(x => x.type === t.key);
    const need = daysOfIn(tid, r, y);
    if (b.limited && need > b.left) fail(`Only ${b.left} days of ${t.label.toLowerCase()} are left in ${y}; this asks for ${need}`, 409, "not_enough_leave");
  }
}
function overlaps(tid, r, except) {
  const st = states.tagged(M, "counts");
  return db().get(`SELECT ref FROM leave_requests WHERE tenant_id=? AND employee_id=? AND status IN ${ph(st)} AND from_date<=? AND to_date>=? AND id<>?`, N(tid), N(r.employee_id), ...st, r.to_date, r.from_date, N(except) || 0);
}
const nextRef = tid => `${SEED.ref}-${N(tid)}-${String(db().get("SELECT COUNT(*) c FROM leave_requests WHERE tenant_id=?", N(tid)).c + 1).padStart(5, "0")}`;
const row = (tid, id) => db().get("SELECT * FROM leave_requests WHERE id=? AND tenant_id=?", N(id), N(tid)) || fail("No such leave request", 404);
function actions(r) {
  const out = [];
  if (tagged(r.status, "pending")) out.push("approve", "reject", "cancel");
  if (tagged(r.status, "approved") && r.from_date > today()) out.push("cancel");
  return out;
}
function view(tid, id) {
  const r = row(tid, id), t = types(tid).find(x => x.key === r.type) || { label: r.type };
  return { ...r, person: personRow(tid, r.employee_id).name, label: t.label, paid: !!t.paid, actions: actions(r) };
}
function move(r, to, extra) {
  const { patch } = states.apply(M, { tenantId: r.tenant_id, from: r.status, to, row: r });
  const all = { ...patch, ...(extra || {}) }, cols = Object.keys(all);
  RR().change(R, r.id, () => {
    const w = db().run(`UPDATE leave_requests SET ${cols.map(c => c + "=?").join(", ")} WHERE id=? AND status=?`, ...cols.map(c => all[c]), r.id, r.status);
    if (!w.changes) fail("This has just changed — reload it", 409);
    return w;
  });
}

/* { employee_id, type, from_date, to_date?, half_day?, reason? } */
function request(tid, input, actor) {
  const i = input || {}, t = N(tid), p = personRow(t, i.employee_id), ty = typeOf(t, i.type);
  const from = str(i.from_date, 10), to = str(i.to_date || i.from_date, 10);
  if (!isDate(from) || !isDate(to)) fail("Dates are written YYYY-MM-DD");
  if (to < from) fail("Leave ends on or after the day it starts");
  const half = i.half_day ? 1 : 0;
  if (half && from !== to) fail("Half a day is one day");
  const r = { employee_id: p.id, type: ty.key, from_date: from, to_date: to, half_day: half };
  const days = half ? 0.5 : daysIn(t, from, to).length;
  if (!days) fail("Those dates hold no working days");
  if (days > SEED.maxDaysPerRequest) fail("One request is at most " + SEED.maxDaysPerRequest + " working days");
  const clash = overlaps(t, r);
  if (clash) fail("This overlaps " + clash.ref, 409, "overlap");
  room(t, r);
  const w = RR().created(R, () => db().run("INSERT INTO leave_requests(tenant_id, ref, employee_id, type, from_date, to_date, half_day, days, reason, status, submitted_by) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
    t, nextRef(t), p.id, ty.key, from, to, half, days, str(i.reason, 500), states.initial(M), by(actor)));
  return view(t, N(w.lastInsertRowid));
}
/* whoever asked, or the person it is for, does not decide it */
function mayDecide(r, actor) {
  const a = by(actor).toLowerCase(), p = db().get("SELECT email FROM employees WHERE id=?", r.employee_id) || {};
  if (!a) fail("Say who decides", 403);
  if (a === String(r.submitted_by || "").toLowerCase() || (p.email && a === String(p.email).toLowerCase())) fail("Someone other than the person it is for, or who asked, decides it", 403, "self_approval");
}
/* approved: each working day shows in attendance as the kind says — paid leave as leave, unpaid as absent */
function approve(tid, id, actor, note) {
  const r = row(tid, id);
  if (!tagged(r.status, "pending")) fail("Only a request waiting for a decision is approved", 409);
  mayDecide(r, actor);
  room(tid, r, r.id);
  const t = typeOf(tid, r.type), O = require("./operations.js");
  return tx(() => {
    move(r, states.first(M, "approved"), { decided_by: by(actor), decision_note: str(note, 500) });
    for (const d of r.half_day ? [r.from_date] : daysIn(tid, r.from_date, r.to_date)) O.markAttendance(N(tid), r.employee_id, d, t.attendance);
    return view(tid, id);
  });
}
function reject(tid, id, actor, note) {
  const r = row(tid, id);
  if (!str(note)) fail("Say why it is turned down");
  if (!tagged(r.status, "pending")) fail("Only a request waiting for a decision is turned down", 409);
  mayDecide(r, actor);
  move(r, states.first(M, "rejected"), { decided_by: by(actor), decision_note: str(note, 500) });
  return view(tid, id);
}
/* withdrawn before it is decided, or before it starts: its attendance days are cleared and its days come back */
function cancel(tid, id) {
  const r = row(tid, id);
  if (!actions(r).includes("cancel")) fail(tagged(r.status, "approved") ? "Leave that has started is not cancelled" : "This request cannot be cancelled", 409);
  const t = typeOf(tid, r.type), was = tagged(r.status, "approved");
  return tx(() => {
    move(r, states.first(M, "cancelled"));
    if (was) for (const d of r.half_day ? [r.from_date] : daysIn(tid, r.from_date, r.to_date))
      db().run("DELETE FROM attendance WHERE tenant_id=? AND employee_id=? AND date=? AND status=? AND check_in IS NULL", N(tid), r.employee_id, d, t.attendance);
    return view(tid, id);
  });
}
function requests(tid, f) {
  const o = f || {};
  return db().all(`SELECT l.*, e.name person FROM leave_requests l JOIN employees e ON e.id=l.employee_id WHERE l.tenant_id=? AND (?='' OR l.status=?) AND (?=0 OR l.employee_id=?)
     AND (?='' OR l.to_date>=?) ORDER BY l.from_date DESC LIMIT 300`, N(tid), str(o.status), str(o.status), N(o.employee_id) || 0, N(o.employee_id) || 0, str(o.from), str(o.from))
    .map(r => ({ ...r, label: (types(tid).find(t => t.key === r.type) || { label: r.type }).label, actions: actions(r) }));
}
/* who is away on each working day from one date to another */
function calendar(tid, from, to) {
  const a = isDate(from) ? from : today(), b = isDate(to) ? to : addDays(a, 27), st = states.tagged(M, "counts");
  const rows = db().all(`SELECT l.*, e.name person FROM leave_requests l JOIN employees e ON e.id=l.employee_id WHERE l.tenant_id=? AND l.status IN ${ph(st)} AND l.from_date<=? AND l.to_date>=?`, N(tid), ...st, b, a);
  return daysIn(tid, a, b).map(d => ({ date: d, away: rows.filter(r => r.from_date <= d && r.to_date >= d).map(r => ({ person: r.person, type: r.type, approved: tagged(r.status, "approved"), half: !!r.half_day })) }));
}
/* a person's own allowance of a kind for a year (null removes it) */
function setAllowance(tid, empId, year, type, days) {
  personRow(tid, empId); const t = typeOf(tid, type), y = N(year);
  if (!(y >= 2000 && y <= 2100)) fail("Say which year");
  if (days === null || days === "") db().run("DELETE FROM leave_allowances WHERE tenant_id=? AND employee_id=? AND year=? AND type=?", N(tid), N(empId), y, t.key);
  else { const d = r2(days); if (!(d >= 0 && d <= 366)) fail("An allowance is 0 to 366 days");
    db().run("INSERT INTO leave_allowances(tenant_id, employee_id, year, type, days) VALUES(?,?,?,?,?) ON CONFLICT(tenant_id, employee_id, year, type) DO UPDATE SET days=excluded.days", N(tid), N(empId), y, t.key, d); }
  return balance(tid, empId, y);
}
/* the hours of approved leave a person has from one date to another, at a weekly capacity (lib/consulting.js) */
function hoursOff(tid, empId, from, to, weekly) {
  const st = states.tagged(M, "approved"), perDay = N(weekly) / Math.max(1, workingDays(tid).length);
  const rows = db().all(`SELECT * FROM leave_requests WHERE tenant_id=? AND employee_id=? AND status IN ${ph(st)} AND from_date<=? AND to_date>=?`, N(tid), N(empId), ...st, to, from);
  let days = 0;
  for (const r of rows) { const a = r.from_date > from ? r.from_date : from, b = r.to_date < to ? r.to_date : to; days += r.half_day ? 0.5 : daysIn(tid, a, b).length; }
  return r2(days * perDay);
}
module.exports = { types, workingDays, daysIn, balance, request, approve, reject, cancel, requests, view, calendar, setAllowance, hoursOff, SEED };
