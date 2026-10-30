/* LUXORA Platform — Bookings: appointments, rentals, stays and experiences.
   A bookable product names the resources that deliver it (a stylist, a room, a vehicle, a
   venue — bookingResourceKinds rows) and how it is booked: a bookingModes row names the engine
   it runs — `slots` (fixed-length appointments on a step) or `days` (a range of days or
   nights). Each resource keeps weekly hours in its own time zone (the store's by default,
   resolved by the Time domain) and a capacity.

   A shopper first HOLDS what they chose; the hold rides on the bag line as its `booking` term
   (lib/lineterms.js) and is confirmed when the order is placed. Holds that are never paid
   expire. Every booking's life is the `booking` state machine, asked by tag (occupies,
   holding, expirable, attendable…), never by a state's name. Capability: bookings. */
"use strict";

const crypto = require("crypto");
const db = () => require("./db.js");
const caps = () => require("./capabilities.js");
const reg = () => require("./parity-registries.js");
const states = require("./states.js");
const lineterms = require("./lineterms.js");
const fail = lineterms.fail;

const rows = name => reg().list(name).map(x => (typeof x === "string" ? { key: x, name: x } : x)).filter(x => x && x.key);
const rowOf = (name, key) => rows(name).find(r => r.key === String(key == null ? "" : key)) || null;
const inTag = tag => { const xs = states.tagged("booking", tag); return { sql: "(" + (xs.length ? xs.map(() => "?").join(",") : "NULL") + ")", args: xs }; };
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };
const CODE_RE = /^[a-z0-9][a-z0-9_-]{0,39}$/;
const iso = d => new Date(d).toISOString().slice(0, 19).replace("T", " ");
const parseT = v => { const t = new Date(String(v || "").replace(" ", "T") + (/[zZ]|[+-]\d\d:?\d\d$/.test(String(v)) ? "" : "Z")); return isNaN(t) ? null : t; };

function params(tid) {
  const P = caps().cap(tid, "bookings");
  if (!Object.keys(P).length) throw fail("Bookings are not available in this store", 403);
  return P;
}

/* ---------- time in a resource's own zone ---------- */
/* minutes the zone is ahead of UTC at an instant (0 for a zone the host's clock does not know) */
function offsetMin(zone, at) {
  try {
    const p = Object.fromEntries(new Intl.DateTimeFormat("en-US", { timeZone: zone, hourCycle: "h23", year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit" })
      .formatToParts(at).map(x => [x.type, x.value]));
    return (Date.UTC(+p.year, +p.month - 1, +p.day, +p.hour, +p.minute, +p.second) - at.getTime()) / 60000;
  } catch (e) { return 0; }
}
/* the instant a local date and minute-of-day in a zone is */
function atLocal(zone, date, minutes) {
  const [y, m, d] = String(date).split("-").map(Number);
  const guess = Date.UTC(y, m - 1, d, 0, minutes);
  let t = guess - offsetMin(zone, new Date(guess)) * 60000;
  t = guess - offsetMin(zone, new Date(t)) * 60000;
  return new Date(t);
}
const weekday = date => { const [y, m, d] = String(date).split("-").map(Number); return new Date(Date.UTC(y, m - 1, d)).getUTCDay(); };
const addDays = (date, n) => { const [y, m, d] = String(date).split("-").map(Number); return new Date(Date.UTC(y, m - 1, d + n)).toISOString().slice(0, 10); };
const toMin = hm => { const [h, m] = String(hm || "0:0").split(":").map(Number); return (h || 0) * 60 + (m || 0); };
const DATE_RE = /^\d{4}-\d{2}-\d{2}$/;
const dayNum = date => { const [y, m, d] = String(date).split("-").map(Number); return Date.UTC(y, m - 1, d) / 864e5; };
function zoneOf(tid, r) {
  if (r && r.tz) return r.tz;
  try { return require("./time.js").zoneOfStore(Number(tid)); } catch (e) { return "UTC"; }
}
function label(tid, b, r) {
  const zone = zoneOf(tid, r);
  const f = (d, o) => { try { return new Intl.DateTimeFormat("en-GB", Object.assign({ timeZone: zone }, o)).format(d); } catch (e) { return iso(d); } };
  const s = parseT(b.starts_at), e = parseT(b.ends_at);
  const same = f(s, { year: "numeric", month: "2-digit", day: "2-digit" }) === f(e, { year: "numeric", month: "2-digit", day: "2-digit" });
  const when = same ? f(s, { weekday: "short", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" }) + "–" + f(e, { hour: "2-digit", minute: "2-digit" })
    : f(s, { weekday: "short", day: "numeric", month: "short" }) + " → " + f(e, { weekday: "short", day: "numeric", month: "short" });
  return when + (r ? " · " + r.name : "");
}

/* ---------- resources ---------- */
function presentResource(r) { return { ...r, hours: J(r.hours, {}), kind_row: rowOf("bookingResourceKinds", r.kind) }; }
function resources(tid) { return db().all("SELECT * FROM booking_resources WHERE tenant_id=? ORDER BY active DESC, name", Number(tid)).map(presentResource); }
/* weekly hours: { "<weekday 0–6>": [["09:00","17:00"], …] } in the resource's zone */
function cleanHours(h) {
  const v = J(h, {}) || {};
  const out = {};
  for (const [k, ranges] of Object.entries(v)) {
    if (!/^[0-6]$/.test(k)) throw fail("Hours are keyed by weekday 0 (Sunday) to 6");
    out[k] = (Array.isArray(ranges) ? ranges : []).map(x => {
      const a = String(x[0] || ""), b = String(x[1] || "");
      if (!/^\d{1,2}:\d{2}$/.test(a) || !/^\d{1,2}:\d{2}$/.test(b) || toMin(b) <= toMin(a) || toMin(b) > 1440) throw fail("Each opening is [\"HH:MM\",\"HH:MM\"], ending after it starts");
      return [a, b];
    });
  }
  return out;
}
function saveResource(tid, input) {
  params(tid);
  const i = input || {};
  const D = db();
  const code = String(i.code || "").trim().toLowerCase();
  if (!CODE_RE.test(code)) throw fail("A resource needs a short code: lowercase letters, digits, - or _");
  const name = String(i.name || "").trim().slice(0, 120);
  if (!name) throw fail("A resource needs a name");
  const kind = rowOf("bookingResourceKinds", i.kind) || rows("bookingResourceKinds").find(r => r.default) || rows("bookingResourceKinds")[0];
  if (!kind) throw fail("No kinds of resource are configured");
  const tz = String(i.tz || "").trim();
  if (tz) { try { new Intl.DateTimeFormat("en-US", { timeZone: tz }); } catch (e) { throw fail("Unknown time zone " + tz); } }
  const vals = [code, name, kind.key, Math.max(1, Math.floor(Number(i.capacity) || 1)), tz || null, JSON.stringify(cleanHours(i.hours)), i.active === false || i.active === 0 ? 0 : 1];
  const clash = D.get("SELECT id FROM booking_resources WHERE tenant_id=? AND code=?", Number(tid), code);
  if (i.id) {
    if (!D.get("SELECT id FROM booking_resources WHERE id=? AND tenant_id=?", Number(i.id), Number(tid))) throw fail("Resource not found", 404);
    if (clash && clash.id !== Number(i.id)) throw fail("Another resource already uses the code " + code, 409);
    D.run("UPDATE booking_resources SET code=?, name=?, kind=?, capacity=?, tz=?, hours=?, active=? WHERE id=?", ...vals, Number(i.id));
    return presentResource(D.get("SELECT * FROM booking_resources WHERE id=?", Number(i.id)));
  }
  if (clash) throw fail("Another resource already uses the code " + code, 409);
  const r = D.run("INSERT INTO booking_resources(code,name,kind,capacity,tz,hours,active,tenant_id) VALUES(?,?,?,?,?,?,?,?)", ...vals, Number(tid));
  return presentResource(D.get("SELECT * FROM booking_resources WHERE id=?", r.lastInsertRowid));
}

/* ---------- how a product is booked ---------- */
function configOf(tid, productId) {
  const c = db().get("SELECT * FROM product_bookings WHERE tenant_id=? AND product_id=?", Number(tid), String(productId));
  if (!c) return null;
  const ids = J(c.resource_ids, []);
  const res = ids.map(id => db().get("SELECT * FROM booking_resources WHERE id=? AND tenant_id=? AND active=1", Number(id), Number(tid))).filter(Boolean).map(presentResource);
  return { ...c, resource_ids: ids, resources: res, mode_row: rowOf("bookingModes", c.mode) };
}
function configure(tid, productId, input) {
  const P = params(tid);
  const i = input || {};
  const D = db();
  if (!D.get("SELECT id FROM products WHERE tenant_id=? AND id=?", Number(tid), String(productId))) throw fail("Unknown product", 404);
  const mode = rowOf("bookingModes", i.mode) || rows("bookingModes").find(r => r.default) || rows("bookingModes")[0];
  if (!mode || !ENGINES[mode.engine]) throw fail("Unknown booking mode");
  const ids = (Array.isArray(i.resource_ids) ? i.resource_ids : []).map(Number).filter(Boolean);
  if (!ids.length) throw fail("Name at least one resource that delivers it");
  for (const id of ids) if (!D.get("SELECT id FROM booking_resources WHERE id=? AND tenant_id=?", id, Number(tid))) throw fail("Unknown resource " + id, 404);
  const n = (v, d, lo, hi) => Math.max(lo, Math.min(hi, Math.floor(Number(v) || d)));
  const vals = [mode.key, JSON.stringify(ids), n(i.duration_min, 60, 5, 1440), n(i.step_min, Number(i.duration_min) || 60, 5, 1440), n(i.buffer_min, 0, 0, 720),
    n(i.lead_hours, 0, 0, 8760), n(i.horizon_days, Number(P.max_horizon_days), 1, Number(P.max_horizon_days) || 365), n(i.min_units, 1, 1, 365), n(i.max_units, 30, 1, 365)];
  D.run("INSERT INTO product_bookings(tenant_id,product_id,mode,resource_ids,duration_min,step_min,buffer_min,lead_hours,horizon_days,min_units,max_units) VALUES(?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(tenant_id,product_id) DO UPDATE SET mode=excluded.mode, resource_ids=excluded.resource_ids, duration_min=excluded.duration_min, step_min=excluded.step_min, buffer_min=excluded.buffer_min, lead_hours=excluded.lead_hours, horizon_days=excluded.horizon_days, min_units=excluded.min_units, max_units=excluded.max_units",
    Number(tid), String(productId), ...vals);
  return configOf(tid, productId);
}
function unconfigure(tid, productId) { params(tid); db().run("DELETE FROM product_bookings WHERE tenant_id=? AND product_id=?", Number(tid), String(productId)); return { ok: true }; }

/* how many bookings occupy a resource across an interval (live holds and confirmed ones) */
function occupied(tid, resourceId, start, end, exceptId) {
  const oc = inTag("occupies");
  const now = iso(Date.now());
  return db().get("SELECT COALESCE(SUM(qty),0) n FROM bookings WHERE tenant_id=? AND resource_id=? AND status IN " + oc.sql +
    " AND starts_at < ? AND ends_at > ? AND (hold_until IS NULL OR hold_until > ? OR status NOT IN " + inTag("holding").sql + ")" + (exceptId ? " AND id<>?" : ""),
    Number(tid), Number(resourceId), ...oc.args, iso(end), iso(start), now, ...inTag("holding").args, ...(exceptId ? [Number(exceptId)] : [])).n;
}

/* ---------- the two engines a booking mode may name ---------- */
/* appointments: fixed-length slots on a step, inside each resource's opening hours */
function slotsAvailability(tid, cfg, q) {
  const date = String(q.date || "");
  if (!DATE_RE.test(date)) throw fail("Name a date (YYYY-MM-DD)");
  const out = [], now = Date.now() + cfg.lead_hours * 3600e3, last = Date.now() + cfg.horizon_days * 864e5;
  for (const r of cfg.resources) {
    const zone = zoneOf(tid, r);
    for (const [a, b] of (r.hours[String(weekday(date))] || [])) {
      for (let m = toMin(a); m + cfg.duration_min <= toMin(b); m += cfg.step_min) {
        const s = atLocal(zone, date, m), e = new Date(s.getTime() + cfg.duration_min * 60000);
        if (s.getTime() < now || s.getTime() > last) continue;
        const busy = occupied(tid, r.id, s, new Date(e.getTime() + cfg.buffer_min * 60000));
        if (busy < r.capacity) out.push({ resource_id: r.id, resource: r.name, start: s.toISOString(), end: e.toISOString(), left: r.capacity - busy });
      }
    }
  }
  return out.sort((x, y) => x.start.localeCompare(y.start));
}
function slotsSpan(tid, cfg, r, q) {
  const s = parseT(q.start); if (!s) throw fail("Name the slot's start");
  const zone = zoneOf(tid, r);
  const local = new Date(s.getTime() + offsetMin(zone, s) * 60000).toISOString();
  const date = local.slice(0, 10), m = toMin(local.slice(11, 16));
  const open = (r.hours[String(weekday(date))] || []).some(([a, b]) => m >= toMin(a) && m + cfg.duration_min <= toMin(b) && (m - toMin(a)) % cfg.step_min === 0);
  if (!open) throw fail("That time is not one of the offered slots");
  return { start: s, end: new Date(s.getTime() + cfg.duration_min * 60000), units: 1, busyEnd: new Date(s.getTime() + (cfg.duration_min + cfg.buffer_min) * 60000) };
}
/* stays and rentals: a range of days, each of which the resource must be open on */
function daysAvailability(tid, cfg, q) {
  const from = String(q.from || q.date || ""), to = String(q.to || "");
  if (!DATE_RE.test(from)) throw fail("Name the first day (YYYY-MM-DD)");
  const out = [];
  for (const r of cfg.resources) {
    const span = daysSpan(tid, cfg, r, { from, to: DATE_RE.test(to) ? to : addDays(from, cfg.min_units) }, true);
    if (!span) continue;
    const busy = occupied(tid, r.id, span.start, span.end);
    if (busy < r.capacity) out.push({ resource_id: r.id, resource: r.name, start: span.start.toISOString(), end: span.end.toISOString(), units: span.units, left: r.capacity - busy });
  }
  return out;
}
function daysSpan(tid, cfg, r, q, quiet) {
  const from = String(q.from || ""), to = String(q.to || "");
  const bail = msg => { if (quiet) return null; throw fail(msg); };
  if (!DATE_RE.test(from) || !DATE_RE.test(to)) return bail("Name the first and last day (YYYY-MM-DD)");
  const units = Math.round(dayNum(to) - dayNum(from));
  if (units < cfg.min_units || units > cfg.max_units) return bail("Book between " + cfg.min_units + " and " + cfg.max_units + " days");
  for (let d = 0; d < units; d++) if (!(r.hours[String(weekday(addDays(from, d)))] || []).length) return bail(r.name + " is closed on " + addDays(from, d));
  const zone = zoneOf(tid, r);
  const first = r.hours[String(weekday(from))][0], lastDay = addDays(from, units - 1);
  const start = atLocal(zone, from, toMin(first[0])), end = atLocal(zone, addDays(lastDay, 1), toMin(first[0]));
  if (start.getTime() < Date.now() + cfg.lead_hours * 3600e3) return bail("That start is too soon");
  if (start.getTime() > Date.now() + cfg.horizon_days * 864e5) return bail("That start is too far ahead");
  return { start, end, units, busyEnd: end };
}
/* a slot is priced once; a day range is priced per day */
const ENGINES = { slots: { availability: slotsAvailability, span: slotsSpan, unitPrice: price => price }, days: { availability: daysAvailability, span: daysSpan, unitPrice: (price, units) => price * units, ranged: true } };
function engineOf(cfg) { const e = cfg && cfg.mode_row && ENGINES[cfg.mode_row.engine]; if (!e) throw fail("This product's booking mode is not one this store can run"); return e; }

/* what the product page offers */
function offer(tid, productId) {
  if (!caps().on(tid, "bookings")) return null;
  const cfg = configOf(tid, productId);
  if (!cfg || !cfg.resources.length || !cfg.mode_row) return null;
  return { mode: cfg.mode_row, ranged: !!ENGINES[cfg.mode_row.engine].ranged, duration_min: cfg.duration_min, min_units: cfg.min_units, max_units: cfg.max_units, horizon_days: cfg.horizon_days,
    resources: cfg.resources.map(r => ({ id: r.id, name: r.name, kind: r.kind_row })) };
}
function availability(tid, productId, q) {
  params(tid);
  const cfg = configOf(tid, productId);
  if (!cfg || !cfg.resources.length) throw fail("This product is not bookable", 404);
  const e = engineOf(cfg);
  const only = q && q.resource_id ? Number(q.resource_id) : null;
  return e.availability(tid, only ? { ...cfg, resources: cfg.resources.filter(r => r.id === only) } : cfg, q || {});
}

/* ---------- holding, confirming, attending ---------- */
function present(b) {
  const r = db().get("SELECT * FROM booking_resources WHERE id=?", b.resource_id);
  return { ...b, resource: r ? { id: r.id, name: r.name } : null, label: label(b.tenant_id, b, r ? presentResource(r) : null), state: states.display("booking", b.status), next: states.next("booking", b.status), cancellable: states.is("booking", b.status, "cancellable") };
}
function hold(tid, owner, input) {
  const P = params(tid);
  const i = input || {};
  const cfg = configOf(tid, i.product_id);
  if (!cfg || !cfg.resources.length) throw fail("This product is not bookable", 404);
  const e = engineOf(cfg);
  const qty = Math.max(1, Math.floor(Number(i.qty) || 1));
  const candidates = i.resource_id ? cfg.resources.filter(r => r.id === Number(i.resource_id)) : cfg.resources;
  if (!candidates.length) throw fail("Unknown resource for this product", 404);
  let chosen = null, span = null, lastErr = null;
  for (const r of candidates) {
    try {
      const sp = e.span(tid, cfg, r, i);
      if (occupied(tid, r.id, sp.start, sp.busyEnd) + qty <= r.capacity) { chosen = r; span = sp; break; }
      lastErr = fail("That time is fully booked", 409);
    } catch (x) { if (!x.status) throw x; lastErr = x; }
  }
  if (!chosen) throw lastErr || fail("That time is fully booked", 409);
  const ref = "BK-" + Date.now().toString(36).toUpperCase().slice(-6) + crypto.randomBytes(2).toString("hex").toUpperCase();
  const r = db().run("INSERT INTO bookings(tenant_id,ref,product_id,resource_id,owner,starts_at,ends_at,units,qty,status,hold_until) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
    Number(tid), ref, String(i.product_id), chosen.id, String(owner), iso(span.start), iso(span.busyEnd), span.units, qty, states.initial("booking"),
    iso(Date.now() + Math.max(1, Number(P.hold_minutes) || 15) * 60000));
  return present(db().get("SELECT * FROM bookings WHERE id=?", r.lastInsertRowid));
}
function move(tid, b, to, extra) {
  const mv = states.apply("booking", { tenantId: tid, from: b.status, to, row: b });
  const patch = Object.assign({}, mv.patch, extra || {});
  const cols = Object.keys(patch);
  db().run("UPDATE bookings SET " + cols.map(c => c + "=?").join(", ") + " WHERE id=?", ...cols.map(c => patch[c]), b.id);
  return db().get("SELECT * FROM bookings WHERE id=?", b.id);
}
function mine(tid, owner) { params(tid); return db().all("SELECT * FROM bookings WHERE tenant_id=? AND owner=? ORDER BY starts_at DESC LIMIT 200", Number(tid), String(owner)).map(present); }
/* the shopper cancels — before the store's cut-off */
function cancelMine(tid, owner, id) {
  const P = params(tid);
  const b = db().get("SELECT * FROM bookings WHERE id=? AND tenant_id=? AND owner=?", Number(id), Number(tid), String(owner));
  if (!b) throw fail("Booking not found", 404);
  if (!states.is("booking", b.status, "cancellable")) throw fail("This booking can no longer be cancelled", 409);
  if (parseT(b.starts_at).getTime() - Date.now() < Number(P.cancel_cutoff_hours) * 3600e3 && !states.is("booking", b.status, "holding")) throw fail("Bookings can be cancelled up to " + P.cancel_cutoff_hours + " hours before they start", 409);
  return present(move(tid, b, states.actionTarget("booking", "cancel")));
}
/* staff move a booking by one of the machine's verbs */
function act(tid, id, action) {
  params(tid);
  const b = db().get("SELECT * FROM bookings WHERE id=? AND tenant_id=?", Number(id), Number(tid));
  if (!b) throw fail("Booking not found", 404);
  const to = states.actionTarget("booking", action);
  if (!to) throw fail("Unknown booking action: " + action);
  if (!states.can("booking", b.status, to)) throw fail("A booking that is " + states.display("booking", b.status).label + " cannot be moved that way", 409);
  return present(move(tid, b, to));
}
function list(tid, f) {
  const q = f || {};
  const where = ["tenant_id=?"], args = [Number(tid)];
  if (q.resource_id) { where.push("resource_id=?"); args.push(Number(q.resource_id)); }
  if (q.from) { where.push("ends_at >= ?"); args.push(String(q.from)); }
  if (q.to) { where.push("starts_at <= ?"); args.push(String(q.to)); }
  return db().all("SELECT * FROM bookings WHERE " + where.join(" AND ") + " ORDER BY starts_at LIMIT 500", ...args).map(present);
}
function expireDue(tid) {
  if (!caps().on(Number(tid), "bookings", { buyer: false })) return { expired: 0 };
  const ex = inTag("expirable");
  const to = states.actionTarget("booking", "expire");
  const due = db().all("SELECT * FROM bookings WHERE tenant_id=? AND status IN " + ex.sql + " AND hold_until IS NOT NULL AND hold_until < ?", Number(tid), ...ex.args, iso(Date.now()));
  for (const b of due) if (to && states.can("booking", b.status, to)) move(tid, b, to);
  return { expired: due.length };
}
function sweepAll() {
  const ex = inTag("expirable");
  let n = 0;
  for (const t of db().all("SELECT DISTINCT tenant_id FROM bookings WHERE status IN " + ex.sql, ...ex.args)) { try { n += expireDue(t.tenant_id).expired; } catch (e) { } }
  return { expired: n };
}

/* ---------- the line term: { id } of the shopper's own live hold ---------- */
function liveHold(ctx, value) {
  const id = Number(value && typeof value === "object" ? value.id : value);
  const b = db().get("SELECT * FROM bookings WHERE id=? AND tenant_id=? AND owner=?", id, Number(ctx.tid), String(ctx.owner));
  if (!b || String(b.product_id) !== String(ctx.product.id)) throw fail("That booking is not yours or is for another product", 404);
  if (!states.is("booking", b.status, "holding")) throw fail("that booking is " + states.display("booking", b.status).label);
  if (b.hold_until && parseT(b.hold_until).getTime() < Date.now()) throw fail("the hold on that time has lapsed — choose it again");
  return b;
}
lineterms.register("booking", {
  atom: "bookings",
  clean: (ctx, value) => ({ id: liveHold(ctx, value).id }),
  price: (ctx, value) => {
    const b = liveHold(ctx, value);
    const cfg = configOf(ctx.tid, ctx.product.id);
    const r = db().get("SELECT * FROM booking_resources WHERE id=?", b.resource_id);
    return { set: engineOf(cfg).unitPrice(Number(ctx.product.price), b.units) * b.qty, label: label(ctx.tid, b, r ? presentResource(r) : null) };
  },
  maxQty: () => 1,
  place: (ctx, value) => {
    const b = db().get("SELECT * FROM bookings WHERE id=? AND tenant_id=?", Number(value.id), Number(ctx.tid));
    const to = states.actionTarget("booking", "confirm");
    if (b && to && states.can("booking", b.status, to)) move(ctx.tid, b, to, { order_id: ctx.orderId, hold_until: null });
  }
});

function vocabulary() {
  return { resourceKinds: rows("bookingResourceKinds"), modes: rows("bookingModes").filter(m => ENGINES[m.engine]),
    actions: Object.entries(states.actions("booking")).map(([verb, to]) => ({ verb, to, label: states.display("booking", to).label })) };
}

module.exports = { ENGINES, resources, saveResource, configure, unconfigure, configOf, offer, availability, hold, mine, cancelMine, act, list, expireDue, sweepAll, vocabulary };
