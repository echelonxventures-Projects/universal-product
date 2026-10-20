/* LUXORA Platform — Pickup points & lockers.
   A store runs any number of pickup points — lockers, staffed counters, its own shops; the
   kinds are pickupKinds registry rows. At checkout a shopper may choose a point instead of a
   home address: the order is reserved a place there and given a one-time code. Staff mark the
   parcel arrived (the shopper is told), the shopper collects with the code, and a parcel left
   past its holding time expires and goes back. Every step is the pickup state machine, asked
   by tag (holding, collectable, expirable…) and never by a state's name; the fee, holding
   days, code length and lock-out are the pickup_points capability's params.

   The code is only ever shown to the order's owner (their order page and email). Staff
   lists never carry it, so collecting proves the person holds it. */
"use strict";

const crypto = require("crypto");
const db = () => require("./db.js");
const caps = () => require("./capabilities.js");
const reg = () => require("./parity-registries.js");
const states = require("./states.js");
const fail = (msg, status) => Object.assign(new Error(msg), { status: status || 400 });

const rows = name => reg().list(name).map(x => (typeof x === "string" ? { key: x, name: x } : x)).filter(x => x && x.key);
const kindOf = key => rows("pickupKinds").find(r => r.key === String(key == null ? "" : key)) || null;
const inTag = tag => { const xs = states.tagged("pickup", tag); return { sql: "(" + (xs.length ? xs.map(() => "?").join(",") : "NULL") + ")", args: xs }; };
const sqlNow = () => new Date().toISOString().slice(0, 19).replace("T", " ");

function params(tid) {
  const P = caps().cap(tid, "pickup_points");
  if (!Object.keys(P).length) throw fail("Pickup points are not available in this store", 403);
  return P;
}
const CODE_RE = /^[a-z0-9][a-z0-9_-]{0,39}$/;

/* ---------- points ---------- */
/* the places a point is holding: reservations still holding a parcel, for orders that are not
   void or aborted (an order cancelled, or whose payment failed or expired, frees its place) */
function held(tid, pointId) {
  const h = inTag("holding");
  const dead = [...new Set(states.tagged("order", "void").concat(states.tagged("order", "aborted")))];
  const notDead = dead.length ? " AND r.order_id NOT IN (SELECT id FROM orders WHERE tenant_id=r.tenant_id AND status IN (" + dead.map(() => "?").join(",") + "))" : "";
  return db().get("SELECT COUNT(*) c FROM pickup_reservations r WHERE r.tenant_id=? AND r.point_id=? AND r.status IN " + h.sql + notDead,
    Number(tid), Number(pointId), ...h.args, ...dead).c;
}
function present(p, P) {
  const used = held(p.tenant_id, p.id);
  return { ...p, kind_row: kindOf(p.kind), held: used, full: Number(p.capacity) > 0 && used >= Number(p.capacity),
    eta: p.eta_days != null ? p.eta_days : (P ? Number(P.default_eta_days) : null) };
}
/* what a shopper may choose: active points with room, nearest-looking first when they give a
   place to match (a postcode or a town) */
function available(tid, q) {
  const P = params(tid);
  const term = String(q || "").trim().toLowerCase();
  const all = db().all("SELECT * FROM pickup_points WHERE tenant_id=? AND active=1 ORDER BY name", Number(tid)).map(p => present(p, P)).filter(p => !p.full);
  if (!term) return all;
  const score = p => (String(p.postcode).toLowerCase() === term ? 3 : 0) + (String(p.postcode).toLowerCase().startsWith(term.slice(0, 3)) ? 1 : 0) + (String(p.city).toLowerCase().includes(term) ? 2 : 0) + (String(p.name + " " + p.address).toLowerCase().includes(term) ? 1 : 0);
  return all.map(p => ({ p, s: score(p) })).sort((a, b) => b.s - a.s).map(x => x.p);
}
function points(tid) {
  const P = caps().cap(tid, "pickup_points");
  return db().all("SELECT * FROM pickup_points WHERE tenant_id=? ORDER BY active DESC, name", Number(tid)).map(p => present(p, Object.keys(P).length ? P : null));
}
function savePoint(tid, input) {
  params(tid);
  const i = input || {};
  const code = String(i.code || "").trim().toLowerCase();
  if (!CODE_RE.test(code)) throw fail("A point needs a short code: lowercase letters, digits, - or _");
  const name = String(i.name || "").trim().slice(0, 120), address = String(i.address || "").trim().slice(0, 300);
  if (!name || !address) throw fail("A point needs a name and an address");
  const kind = kindOf(i.kind) || rows("pickupKinds").find(r => r.default) || rows("pickupKinds")[0];
  if (!kind) throw fail("No kinds of pickup point are configured");
  const num = (v, lo, hi) => (v === "" || v == null || !isFinite(Number(v)) ? null : Math.max(lo, Math.min(hi, Number(v))));
  const vals = [code, name, kind.key, address, String(i.city || "").slice(0, 120), String(i.region || "").slice(0, 120), String(i.postcode || "").slice(0, 20),
    num(i.lat, -90, 90), num(i.lng, -180, 180), Math.max(0, Math.floor(Number(i.capacity) || 0)), String(i.hours || "").slice(0, 300),
    num(i.eta_days, 0, 365), i.active === false || i.active === 0 ? 0 : 1];
  const D = db();
  const clash = D.get("SELECT id FROM pickup_points WHERE tenant_id=? AND code=?", Number(tid), code);
  if (i.id) {
    const ex = D.get("SELECT id FROM pickup_points WHERE id=? AND tenant_id=?", Number(i.id), Number(tid));
    if (!ex) throw fail("Pickup point not found", 404);
    if (clash && clash.id !== ex.id) throw fail("Another point already uses the code " + code, 409);
    D.run("UPDATE pickup_points SET code=?, name=?, kind=?, address=?, city=?, region=?, postcode=?, lat=?, lng=?, capacity=?, hours=?, eta_days=?, active=? WHERE id=?", ...vals, ex.id);
    return present(D.get("SELECT * FROM pickup_points WHERE id=?", ex.id));
  }
  if (clash) throw fail("Another point already uses the code " + code, 409);
  const r = D.run("INSERT INTO pickup_points(code,name,kind,address,city,region,postcode,lat,lng,capacity,hours,eta_days,active,tenant_id) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", ...vals, Number(tid));
  return present(D.get("SELECT * FROM pickup_points WHERE id=?", r.lastInsertRowid));
}
/* a point still holding parcels is switched off, not deleted — its reservations stay whole */
function removePoint(tid, id) {
  const D = db();
  const p = D.get("SELECT * FROM pickup_points WHERE id=? AND tenant_id=?", Number(id), Number(tid));
  if (!p) throw fail("Pickup point not found", 404);
  if (held(tid, p.id) || D.get("SELECT id FROM pickup_reservations WHERE tenant_id=? AND point_id=? LIMIT 1", Number(tid), p.id)) {
    D.run("UPDATE pickup_points SET active=0 WHERE id=?", p.id);
    return { ok: true, deactivated: true };
  }
  D.run("DELETE FROM pickup_points WHERE id=?", p.id);
  return { ok: true, deleted: true };
}

/* ---------- checkout ---------- */
/* what choosing this point means for an order: the point, its fee and when it gets there */
function quote(tid, pointRef) {
  const P = params(tid);
  const D = db();
  const p = D.get("SELECT * FROM pickup_points WHERE tenant_id=? AND active=1 AND (id=? OR code=?)", Number(tid), Number(pointRef) || -1, String(pointRef || ""));
  if (!p) throw fail("That pickup point is not available", 422);
  const v = present(p, P);
  if (v.full) throw fail(p.name + " is full right now — choose another point", 409);
  return { point: v, fee: Math.max(0, Number(P.fee) || 0), free_shipping_applies: !!P.free_shipping_applies, eta: v.eta };
}
function newCode(len) {
  const n = Math.max(4, Math.min(12, Math.floor(Number(len) || 6)));
  let s = ""; for (let i = 0; i < n; i++) s += crypto.randomInt(0, 10);
  return s;
}
function reserve(tid, orderId, pointId, owner) {
  const P = params(tid);
  const D = db();
  const r = D.run("INSERT INTO pickup_reservations(tenant_id,point_id,order_id,owner,code,status) VALUES(?,?,?,?,?,?)",
    Number(tid), Number(pointId), Number(orderId), String(owner), newCode(P.code_length), states.initial("pickup"));
  return D.get("SELECT * FROM pickup_reservations WHERE id=?", r.lastInsertRowid);
}
/* the owner's view of their order's pickup — the only place the code is ever returned */
function forOrder(tid, orderId, owner) {
  const D = db();
  const r = D.get("SELECT * FROM pickup_reservations WHERE tenant_id=? AND order_id=? AND owner=?", Number(tid), Number(orderId), String(owner));
  if (!r) return null;
  const p = D.get("SELECT * FROM pickup_points WHERE id=?", r.point_id);
  const collectable = states.is("pickup", r.status, "collectable") || states.is("pickup", r.status, "awaiting_parcel");
  return { status: r.status, state: states.display("pickup", r.status), code: collectable ? r.code : null, hold_until: r.hold_until, ready_at: r.ready_at, collected_at: r.collected_at,
    point: p ? { name: p.name, address: p.address, city: p.city, postcode: p.postcode, hours: p.hours, kind: kindOf(p.kind) } : null };
}

/* ---------- the parcel's life ---------- */
function staffView(r) {
  const { code, ...rest } = r;
  return { ...rest, state: states.display("pickup", r.status), next: states.next("pickup", r.status) };
}
function reservations(tid, filter) {
  const f = filter || {};
  const where = ["r.tenant_id=?"], args = [Number(tid)];
  if (f.point_id) { where.push("r.point_id=?"); args.push(Number(f.point_id)); }
  if (f.tag) { const t = inTag(f.tag); where.push("r.status IN " + t.sql); args.push(...t.args); }
  return db().all("SELECT r.*, p.name point_name, o.num order_num, o.name customer FROM pickup_reservations r LEFT JOIN pickup_points p ON p.id=r.point_id LEFT JOIN orders o ON o.id=r.order_id WHERE " + where.join(" AND ") + " ORDER BY r.id DESC LIMIT 300", ...args).map(staffView);
}
function move(tid, r, to, extra) {
  const mv = states.apply("pickup", { tenantId: tid, from: r.status, to, row: r });
  const patch = Object.assign({}, mv.patch, extra || {});
  const cols = Object.keys(patch);
  db().run("UPDATE pickup_reservations SET " + cols.map(c => c + "=?").join(", ") + " WHERE id=?", ...cols.map(c => patch[c]), r.id);
  return db().get("SELECT * FROM pickup_reservations WHERE id=?", r.id);
}
const resOf = (tid, id) => {
  const r = db().get("SELECT * FROM pickup_reservations WHERE id=? AND tenant_id=?", Number(id), Number(tid));
  if (!r) throw fail("Pickup reservation not found", 404);
  return r;
};
/* a staff action is one of the machine's verbs (arrive, collect, expire, return, cancel) */
function act(tid, id, action, input) {
  const P = params(tid);
  const r = resOf(tid, id);
  const to = states.actionTarget("pickup", action);
  if (!to) throw fail("Unknown pickup action: " + action);
  if (!states.can("pickup", r.status, to)) throw fail("A parcel that is " + states.display("pickup", r.status).label + " cannot be moved that way", 409);
  /* collecting is the one move that needs proof: the code, with a lock-out on guessing */
  if (states.is("pickup", to, "success")) {
    const given = String((input || {}).code || "");
    if (r.attempts >= Number(P.max_attempts)) throw fail("Too many wrong codes — check the customer's identity and the order", 423);
    const okCode = given.length === r.code.length && crypto.timingSafeEqual(Buffer.from(given), Buffer.from(r.code));
    if (!okCode) { db().run("UPDATE pickup_reservations SET attempts=attempts+1 WHERE id=?", r.id); throw fail("That code does not match this parcel", 403); }
    const done = move(tid, r, to);
    fulfilOrder(tid, done.order_id);
    return staffView(done);
  }
  const extra = states.is("pickup", to, "collectable")
    ? { hold_until: new Date(Date.now() + Math.max(1, Number(P.hold_days) || 1) * 864e5).toISOString().slice(0, 19).replace("T", " ") }
    : null;
  const done = move(tid, r, to, extra);
  if (states.is("pickup", to, "collectable")) tellReady(tid, done, P);
  return staffView(done);
}
/* a collected parcel fulfils its order, where the order machine allows the move */
function fulfilOrder(tid, orderId) {
  try {
    const o = db().get("SELECT id, status FROM orders WHERE id=? AND tenant_id=?", Number(orderId), Number(tid));
    if (!o) return;
    const to = states.first("order", "fulfilled");
    if (states.can("order", o.status, to)) {
      const mv = states.apply("order", { tenantId: tid, from: o.status, to, row: o });
      const cols = Object.keys(mv.patch);
      db().run("UPDATE orders SET " + cols.map(c => c + "=?").join(", ") + " WHERE id=?", ...cols.map(c => mv.patch[c]), o.id);
    }
  } catch (e) { }
}
function tellReady(tid, r, P) {
  const D = db();
  const p = D.get("SELECT * FROM pickup_points WHERE id=?", r.point_id) || {};
  const o = D.get("SELECT num FROM orders WHERE id=?", r.order_id) || {};
  const title = "Ready to collect: order " + (o.num || r.order_id);
  const body = "Your parcel is waiting at " + (p.name || "your pickup point") + ", " + (p.address || "") + (p.hours ? " (" + p.hours + ")" : "") +
    ". Collect it by " + r.hold_until + " UTC with code " + r.code + ".";
  /* the notification kind is the capability's param, sent only if the notification registry knows it */
  const kind = rows("shopNotifKinds").map(x => x.key).find(k => k === String(P.notify_kind || ""));
  if (kind) D.run("INSERT INTO notifications(tenant_id,owner,kind,title,body,link,read,meta) VALUES(?,?,?,?,?,?,0,?)",
    Number(tid), r.owner, kind, title, body, "orders.html", JSON.stringify({ pickup: r.id }));
  if (!P.email_on_ready) return;
  const m = /:u:(\d+)$/.exec(String(r.owner));
  const u = m ? D.get("SELECT email FROM users WHERE id=? AND tenant_id=?", Number(m[1]), Number(tid)) : null;
  if (u && u.email) require("./mailer.js").deliver({ tenantId: Number(tid), channel: "email", to: u.email, kind: "pickup_ready", subject: title, text: body });
}
/* parcels past their holding time expire (the timer's pass, or staff asking now) */
function expireDue(tid) {
  if (!caps().on(Number(tid), "pickup_points", { buyer: false })) return { expired: 0 };
  const ex = inTag("expirable");
  const to = states.first("pickup", "failure");
  const due = db().all("SELECT * FROM pickup_reservations WHERE tenant_id=? AND status IN " + ex.sql + " AND hold_until IS NOT NULL AND hold_until < ?", Number(tid), ...ex.args, sqlNow());
  for (const r of due) if (states.can("pickup", r.status, to)) move(tid, r, to);
  return { expired: due.length };
}
function sweepAll() {
  const ex = inTag("expirable");
  let n = 0;
  for (const t of db().all("SELECT DISTINCT tenant_id FROM pickup_reservations WHERE status IN " + ex.sql, ...ex.args)) {
    try { n += expireDue(t.tenant_id).expired; } catch (e) { console.error("pickup sweep (tenant " + t.tenant_id + "):", e.message); }
  }
  return { expired: n };
}
/* the kinds of point, and the machine's verbs — which one needs the shopper's code */
function vocabulary() {
  return { kinds: rows("pickupKinds"),
    actions: Object.entries(states.actions("pickup")).map(([verb, to]) => ({ verb, to, label: states.display("pickup", to).label, needs_code: states.is("pickup", to, "success") })) };
}
/* what choosing a point costs and promises, for the checkout page */
function terms(tid) { const P = params(tid); return { fee: Math.max(0, Number(P.fee) || 0), free_shipping_applies: !!P.free_shipping_applies, hold_days: Number(P.hold_days) }; }

module.exports = { available, points, savePoint, removePoint, quote, reserve, forOrder, reservations, act, expireDue, sweepAll, vocabulary, terms };
