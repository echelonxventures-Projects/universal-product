/* LUXORA Platform — delivery slots: the shopper chooses the day and hours their order arrives.

   A store's windows repeat each week (a weekday, from and to, how many deliveries fit, a fee). At
   checkout a shopper picks one of the dates the capability allows ahead, in the store's own clock;
   a window closes its cutoff before it starts and when it is full. A place is claimed by one
   conditional write as the order is placed, and freed when the order is void.
   Capability: delivery_slots. */
"use strict";

const db = () => require("./db.js");
const caps = () => require("./capabilities.js");
const states = require("./states.js");
const fail = (msg, status) => Object.assign(new Error(msg), { status: status || 400 });
const on = tid => caps().on(Number(tid), "delivery_slots");
function params(tid) { if (!on(tid)) throw fail("Delivery slots are not available in this store", 403); return caps().cap(Number(tid), "delivery_slots"); }
const TIME = /^([01]\d|2[0-3]):[0-5]\d$/, mins = t => Number(t.slice(0, 2)) * 60 + Number(t.slice(3));
const pad = n => String(n).padStart(2, "0");
const dayKey = d => d.getUTCFullYear() + "-" + pad(d.getUTCMonth() + 1) + "-" + pad(d.getUTCDate());

/* now, on the store's wall clock: its date (as a UTC midnight), and minutes into the day */
function storeNow(tid) {
  const T = require("./time.js");
  let w; try { w = T.wallClock(new Date(), T.zoneOfStore(Number(tid))); } catch (e) { const d = new Date(); w = { year: d.getUTCFullYear(), month: d.getUTCMonth() + 1, day: d.getUTCDate(), hour: d.getUTCHours(), minute: d.getUTCMinutes() }; }
  return { day: new Date(Date.UTC(w.year, w.month - 1, w.day)), minutes: w.hour * 60 + (w.minute || 0) };
}
/* ---------- the store's windows ---------- */
const windows = tid => db().all("SELECT * FROM delivery_windows WHERE tenant_id=? ORDER BY weekday, starts", Number(tid));
function save(tid, input) {
  params(tid);
  const i = input || {}, weekday = Number(i.weekday), starts = String(i.starts || ""), ends = String(i.ends || "");
  if (!Number.isInteger(weekday) || weekday < 0 || weekday > 6) throw fail("Choose a day of the week");
  if (!TIME.test(starts) || !TIME.test(ends) || mins(ends) <= mins(starts)) throw fail("A window starts and ends at times like 09:00 and 12:00");
  const v = [weekday, starts, ends, Math.max(0, Math.floor(Number(i.capacity) || 0)), Math.max(0, +Number(i.fee || 0).toFixed(2)), i.active === false || i.active === 0 ? 0 : 1];
  if (i.id) { if (!db().run("UPDATE delivery_windows SET weekday=?,starts=?,ends=?,capacity=?,fee=?,active=? WHERE id=? AND tenant_id=?", ...v, Number(i.id), Number(tid)).changes) throw fail("Window not found", 404); }
  else db().run("INSERT INTO delivery_windows(weekday,starts,ends,capacity,fee,active,tenant_id) VALUES(?,?,?,?,?,?,?)", ...v, Number(tid));
  return windows(tid);
}
function remove(tid, id) { if (!db().run("DELETE FROM delivery_windows WHERE id=? AND tenant_id=?", Number(id), Number(tid)).changes) throw fail("Window not found", 404); return windows(tid); }
/* places taken: bookings of orders that are still going ahead */
function taken(tid, windowId, date) {
  const dead = states.tagged("order", "void");
  return db().get("SELECT COUNT(*) c FROM delivery_bookings b JOIN orders o ON o.id=b.order_id WHERE b.tenant_id=? AND b.window_id=? AND b.day=? AND o.status NOT IN (" + dead.map(() => "?").join(",") + ")", Number(tid), Number(windowId), date, ...dead).c;
}
/* ---------- what a shopper may choose ---------- */
function choices(tid) {
  const P = params(tid), now = storeNow(tid), ws = windows(tid).filter(w => w.active), out = [];
  for (let ahead = 0; ahead <= Math.max(0, Math.min(60, Number(P.days_ahead) || 0)); ahead++) {
    const d = new Date(now.day.getTime() + ahead * 864e5), day = dayKey(d);
    for (const w of ws.filter(w => w.weekday === d.getUTCDay())) {
      const closes = mins(w.starts) - (Number(P.cutoff_minutes) || 0) + ahead * 1440;
      if (now.minutes >= closes) continue;
      const left = w.capacity > 0 ? w.capacity - taken(tid, w.id, day) : null;
      if (left != null && left <= 0) continue;
      out.push({ key: w.id + "@" + day, window_id: w.id, day, starts: w.starts, ends: w.ends, fee: w.fee, left });
    }
  }
  return out;
}
/* the choice a checkout sends, or null where the store asks for none */
function choose(tid, key) {
  if (!on(tid)) return null;
  const P = params(tid);
  if (!key) { if (P.required && windows(tid).some(w => w.active)) throw fail("Choose when you would like your delivery", 422); return null; }
  const c = choices(tid).find(x => x.key === String(key));
  if (!c) throw fail("That delivery time is no longer available — choose another", 409);
  return c;
}
/* a place for an order, inside the checkout's own write: refused when it has just filled up */
function book(tid, orderId, c) {
  return require("./kernel.js").internal.tx(() => {
    const w = db().get("SELECT * FROM delivery_windows WHERE id=? AND tenant_id=? AND active=1", c.window_id, Number(tid));
    if (!w || (w.capacity > 0 && taken(tid, w.id, c.day) >= w.capacity)) throw fail("That delivery time has just filled up — choose another", 409);
    db().run("INSERT INTO delivery_bookings(tenant_id,order_id,window_id,day,starts,ends,fee) VALUES(?,?,?,?,?,?,?)", Number(tid), Number(orderId), w.id, c.day, w.starts, w.ends, w.fee);
  });
}
const forOrder = (tid, orderId) => db().get("SELECT day, starts, ends FROM delivery_bookings WHERE tenant_id=? AND order_id=?", Number(tid), Number(orderId)) || null;
/* what the store delivers on a day, for staff */
function schedule(tid, day) {
  const dead = states.tagged("order", "void");
  return db().all("SELECT b.day, b.starts, b.ends, o.id order_id, o.num, o.name, o.address, o.city, o.zip, o.status FROM delivery_bookings b JOIN orders o ON o.id=b.order_id WHERE b.tenant_id=? AND b.day>=? AND o.status NOT IN (" + dead.map(() => "?").join(",") + ") ORDER BY b.day, b.starts LIMIT 300",
    Number(tid), /^\d{4}-\d\d-\d\d$/.test(day || "") ? day : dayKey(storeNow(tid).day), ...dead);
}
module.exports = { on, windows, save, remove, choices, choose, book, forOrder, schedule };
