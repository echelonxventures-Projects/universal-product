/* LUXORA Platform — media sessions: live audio or video between a shopper and whoever serves them
   (a practitioner, a consultant, a tutor, a seller), and metering them by the minute.

   A session belongs to what it serves — a booking the shopper made, by default — and has two
   sides: the guest (the shopper who booked) and the host (the store, or the seller whose item was
   booked). How it is carried is the store's choice of transport: the platform's own (the two
   browsers connect directly, the platform relaying only the handshake: offers, answers and
   network candidates, read by each side in turn) or a connector registered as a media provider,
   which declares how its room links are formed — plug-and-play, as data (DEC-020). Its life is the
   `media_session` state machine: scheduled → live → ended (or missed, or cancelled).

   Charged by the minute (capability per_minute_billing, its own feature): a session's minutes are charged to the guest's wallet at
   the rate the session carries — the booked item's price per minute where its facts say it is
   priced per minute, else the capability's default rate — in the capability's increments, with a
   minimum; a guest must hold enough for the minimum before a metered session goes live. Selling
   communication itself is selling such sessions. Capability: media_sessions. */
"use strict";

const db = () => require("./db.js");
const caps = () => require("./capabilities.js");
const states = require("./states.js");
const fail = (msg, status) => Object.assign(new Error(msg), { status: status || 400 });
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };
const r2 = n => +Number(n || 0).toFixed(2);
const sqlNow = () => new Date().toISOString().slice(0, 19).replace("T", " ");
const tell = (...a) => require("./tell.js").tell(...a);

function params(tid) {
  const P = caps().cap(Number(tid), "media_sessions");
  if (!Object.keys(P).length) throw fail("Live sessions are not available in this store", 403);
  return P;
}
const metering = tid => caps().on(Number(tid), "per_minute_billing") ? caps().cap(Number(tid), "per_minute_billing") : null;

/* the transports a store may carry sessions by: the platform's own, and every connector registered
   in the Provider Registry under the capability's provider kind; a connector's room link is the
   store's room_url param, with {room} for the session's room */
function transports(P) {
  const own = { id: "", name: "The platform's own", builtin: true };
  return [own, ...db().all("SELECT id, name FROM provider_defs WHERE kind=? AND enabled=1 ORDER BY position, id", String(P.provider_kind)).map(p => ({ id: p.id, name: p.name }))];
}
const transportOf = P => transports(P).find(t => t.id === String(P.transport || "")) || transports(P)[0];

/* ---------- a session for a booking ---------- */
function forBooking(tid, bookingRef, actor) {
  const P = params(tid);
  const b = db().get("SELECT * FROM bookings WHERE tenant_id=? AND (ref=? OR id=?)", Number(tid), String(bookingRef), Number(bookingRef) || -1);
  if (!b) throw fail("Unknown booking", 404);
  if (actor && actor.owner && b.owner !== actor.owner && !actor.staff) throw fail("Unknown booking", 404);
  const ex = db().get("SELECT * FROM media_sessions WHERE tenant_id=? AND subject_type=? AND subject_id=?", Number(tid), P.subject, String(b.id));
  if (ex) return present(ex);
  let host = ""; try { host = require("./listings.js").ownerOf(tid, b.product_id) || ""; } catch (e) { host = ""; }
  /* the rate: the booked item's per-minute price where its facts say so, else the default rate */
  const p = db().get("SELECT price, attrs FROM products WHERE tenant_id=? AND id=?", Number(tid), b.product_id) || {};
  const perMinute = (J(p.attrs, {})[P.rate_basis_attr] || "") === P.rate_basis_value;
  const meter = metering(tid);
  const rate = meter ? (perMinute ? Number(p.price) : Number(meter.default_rate)) : 0;
  const t = transportOf(P);
  const room = require("crypto").randomBytes(12).toString("hex");
  const r = db().run("INSERT INTO media_sessions(tenant_id,subject_type,subject_id,guest,host,mode,transport,room,rate,status) VALUES(?,?,?,?,?,?,?,?,?,?)",
    Number(tid), P.subject, String(b.id), b.owner, host, String((J(b.terms, {}) || {}).mode || P.default_mode), t.id, room, r2(rate), states.initial("media_session"));
  return present(db().get("SELECT * FROM media_sessions WHERE id=?", r.lastInsertRowid));
}
function present(x) {
  const P = caps().cap(Number(x.tenant_id), "media_sessions");
  const t = transports(P).find(z => z.id === x.transport) || transports(P)[0];
  return { ...x, state: states.display("media_session", x.status), next: states.next("media_session", x.status), live: states.is("media_session", x.status, "live"), done: states.is("media_session", x.status, "terminal"),
    transport_name: t.name, join_url: t.builtin ? String(P.page) + "?id=" + x.id : String(P.room_url || "").replace("{room}", x.room) };
}
/* which side a caller is on: the guest, the host (the seller, or the store's staff for the store) */
function sideOf(x, actor) {
  if (actor.owner && actor.owner === x.guest) return "guest";
  if ((actor.owner && x.host && actor.owner === x.host) || (actor.staff && !x.host)) return "host";
  return null;
}
function get(tid, id, actor) {
  const x = db().get("SELECT * FROM media_sessions WHERE tenant_id=? AND id=?", Number(tid), Number(id));
  if (!x || !sideOf(x, actor)) throw fail("Session not found", 404);
  return x;
}
function move(x, action, patch) {
  const to = states.actionTarget("media_session", action);
  if (!to || !states.can("media_session", x.status, to)) throw fail("That cannot be done to this session now", 409);
  const mv = states.apply("media_session", { tenantId: x.tenant_id, from: x.status, to, row: x });
  const p = { ...mv.patch, ...(patch || {}) };
  const cols = Object.keys(p);
  db().run("UPDATE media_sessions SET " + cols.map(c => c + "=?").join(", ") + " WHERE id=?", ...cols.map(c => p[c]), x.id);
  return db().get("SELECT * FROM media_sessions WHERE id=?", x.id);
}

/* ---------- joining, the handshake, ending ---------- */
function join(tid, id, actor) {
  const P = params(tid);
  let x = get(tid, id, actor);
  const side = sideOf(x, actor);
  const meter = metering(tid);
  /* a metered session goes live only when the guest holds enough for its minimum */
  if (meter && x.rate > 0 && !x.started_at) {
    const need = r2(x.rate * Number(meter.minimum_minutes));
    const have = (db().get("SELECT balance FROM wallets WHERE tenant_id=? AND owner=?", Number(tid), x.guest) || { balance: 0 }).balance;
    if (have < need) throw fail("This session is charged by the minute: the guest needs " + need + " in their wallet to start", 402);
  }
  if (!x.started_at && states.can("media_session", x.status, states.actionTarget("media_session", "start"))) x = move(x, "start", { started_at: sqlNow() });
  return { session: present(x), side, makesOffer: side === P.offering_side, ice: J(P.ice_servers, []) };
}
/* one side hands the other an offer, an answer or a network candidate; each reads what is for it */
function signal(tid, id, actor, msg) {
  const x = get(tid, id, actor);
  if (!states.is("media_session", x.status, "live")) throw fail("The session is not live", 409);
  const m = msg || {};
  const kind = String(m.type || "");
  if (!params(tid).signal_types.split(",").map(s => s.trim()).includes(kind)) throw fail("Unknown signal: " + kind);
  const body = JSON.stringify(m.data == null ? null : m.data);
  if (body.length > 20000) throw fail("That signal is too large");
  db().run("INSERT INTO media_signals(session_id,side,type,data) VALUES(?,?,?,?)", x.id, sideOf(x, actor), kind, body);
  return { ok: true };
}
function signals(tid, id, actor, since) {
  const x = get(tid, id, actor);
  const mine = sideOf(x, actor);
  return db().all("SELECT id, type, data, created_at FROM media_signals WHERE session_id=? AND side<>? AND id>? ORDER BY id LIMIT 200", x.id, mine, Number(since) || 0)
    .map(r => ({ id: r.id, type: r.type, data: J(r.data, null), at: r.created_at }));
}
/* ending: the minutes are counted and, where metered, charged to the guest */
function end(tid, id, actor) {
  let x = get(tid, id, actor);
  if (!x.started_at) return present(move(x, "cancel"));
  const seconds = Math.max(0, Math.round((Date.now() - new Date(x.started_at.replace(" ", "T") + "Z").getTime()) / 1000));
  const meter = metering(tid);
  let charged = 0, shortfall = 0;
  if (meter && x.rate > 0) {
    const step = Math.max(1, Number(meter.increment_seconds));
    const billed = Math.max(Number(meter.minimum_minutes) * 60, Math.ceil(seconds / step) * step);
    const due = r2(billed / 60 * x.rate);
    /* what the guest's wallet holds is taken; anything beyond it is recorded as the session's shortfall, never dropped */
    const have = require("./modules.js").walletBalance(Number(tid), x.guest);
    charged = r2(Math.min(due, have));
    shortfall = r2(due - charged);
    if (charged > 0) require("./offers.js").debit(Number(tid), x.guest, charged, String(meter.ledger_kind || ""), "media_session:" + x.id, null, "media_sessions");
  }
  x = move(x, "end", { ended_at: sqlNow(), seconds, charged, shortfall });
  tell(tid, x.guest, "media_session", "Your session has ended", (seconds / 60).toFixed(1) + " minutes" + (charged ? " · " + charged + " charged" : ""), "account.html");
  return present(x);
}
function mine(tid, actor) {
  params(tid);
  return db().all("SELECT * FROM media_sessions WHERE tenant_id=? AND (guest=? OR (host<>'' AND host=?))" + (actor.staff ? " OR (tenant_id=? AND host='')" : "") + " ORDER BY id DESC LIMIT 100",
    Number(tid), String(actor.owner || ""), String(actor.owner || ""), ...(actor.staff ? [Number(tid)] : [])).map(present);
}
/* the per-minute screen: its settings and what each session was charged */
function charges(tid) {
  const meter = metering(tid);
  if (!meter) throw fail("Charging by the minute is not available in this store", 403);
  const rows = db().all("SELECT * FROM media_sessions WHERE tenant_id=? AND rate>0 ORDER BY id DESC LIMIT 300", Number(tid)).map(present);
  return { settings: meter, sessions: rows, total: r2(rows.reduce((t, x) => t + Number(x.charged || 0), 0)) };
}
function vocabulary(tid) { return { transports: transports(params(tid)), actions: Object.entries(states.actions("media_session")).map(([verb, to]) => ({ verb, to, label: states.display("media_session", to).label })) }; }

module.exports = { forBooking, join, signal, signals, end, mine, charges, transports, vocabulary };
