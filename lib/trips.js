/* LUXORA Platform — trips (owner Operations, the mobility domain).

   What happens around a ride (lib/mobility.js), for the rider, the driver and the store:
   - the rating both ways: a rider rates the driver and a driver the rider, with tags; a driver's
     rating is the average of their recent ratings, and one who falls below the floor is held out
     of dispatch for the store to review (ride_ratings);
   - a ride booked for later: dispatched shortly before its time (ride_schedules);
   - a shared ride: riders going the same way share a car and each pays less (ride_pools);
   - the live position: the driver's phone reports where it is, the ride keeps its track, the
     nearest driver is matched by it, and a finished trip's distance and time come from it
     (ride_locations);
   - safety: a trip shared with someone by a private link, the emergency button, and incidents
     reported after a trip, handled by the store (ride_safety_events);
   - what each driver earns trip by trip — the fare less the platform's share, plus tips — and
     the payouts that pay it, on the books (driver_payouts).
   Bookings, safety reports and payouts are records on the master (lib/seed/row-records.json),
   each moving through its machine (lib/seed/states.json); policy is data (lib/seed/trips.json),
   and a store sets its own in settings trips.<key>. */
"use strict";

const db = () => require("./db.js");
const K = require("./kernel.js");
const RR = () => require("./row-records.js");
const states = require("./states.js");
const crypto = require("crypto");
const SEED = require("./seed/trips.json");
const M = SEED.machines, R = SEED.records;
const MOB = () => require("./mobility.js");
/* who rates or reports: the rider or the driver of a ride */
const SIDE = SEED.sides;
const caps = () => require("./capabilities.js");
const fail = (msg, status, code) => { const e = new Error(msg); e.status = status || 400; if (code) e.code = code; throw e; };
const N = Number;
const r2 = n => +Number(n || 0).toFixed(2);
const str = (v, n) => String(v == null ? "" : v).trim().slice(0, n || 200);
const tx = fn => K.internal.tx(fn);
const ph = xs => "(" + (xs.length ? xs.map(() => "?").join(",") : "NULL") + ")";
const own = tid => { try { return require("./settings.js").get(N(tid), "trips") || {}; } catch (e) { return {}; } };
const P = (tid, k) => ({ ...SEED[k], ...((own(tid) || {})[k] || {}) });
/* times are kept as the database keeps them: UTC, "YYYY-MM-DD HH:MM:SS" */
const at = ms => new Date(ms).toISOString().slice(0, 19).replace("T", " ");
const nowAt = () => at(Date.now());
const msOf = s => Date.parse(String(s || "").replace(" ", "T") + (/[zZ]|[+-]\d\d:?\d\d$/.test(String(s || "")) ? "" : "Z"));
const on = tid => { const c = caps().cap(N(tid), "ride_hailing"); return !!c && Object.keys(c).length > 0; };
const rideTag = (s, t) => !!s && states.has("ride", s) && states.is("ride", s, t);
const tagged = (m, s, t) => !!s && states.has(m, s) && states.is(m, s, t);
const inTag = (m, t) => { const xs = states.tagged(m, t); return { sql: ph(xs), args: xs }; };
const geo = (lat, lng) => lat != null && lng != null && lat !== "" && lng !== "" && isFinite(lat) && isFinite(lng) && Math.abs(lat) <= 90 && Math.abs(lng) <= 180;
const dist = (a, b, c, d) => MOB().dist(N(a), N(b), N(c), N(d));
const ended = r => r.completed_at || r.cancelled_at || null;

/* ============================== who is asking ============================== */
function rideRow(tid, id) { return db().get("SELECT * FROM rides WHERE id=? AND tenant_id=?", N(id), N(tid)) || fail("No such ride", 404); }
/* a rider's own ride */
function mineRide(tid, userId, id) { const r = rideRow(tid, id); if (!userId || N(r.user_id) !== N(userId)) fail("No such ride", 404); return r; }
/* the driver a signed-in person is, by their email */
function driverOf(tid, email) {
  const e = str(email, 200).toLowerCase();
  return e ? db().get("SELECT * FROM drivers WHERE tenant_id=? AND lower(email)=? AND deactivated_at IS NULL", N(tid), e) || null : null;
}
function asDriver(tid, email) { return driverOf(tid, email) || fail("You are not a driver for this store", 403, "not_driver"); }
function driverRide(tid, driver, id) { const r = rideRow(tid, id); if (N(r.driver_id) !== N(driver.id)) fail("No such ride", 404); return r; }
const userName = (tid, userId) => ((userId && db().get("SELECT name FROM users WHERE id=? AND tenant_id=?", N(userId), N(tid))) || {}).name || "";
const firstName = s => String(s || "").trim().split(/\s+/)[0] || "";

/* ============================== the route and its price ============================== */
/* the road distance between two points: the straight line times the road factor */
function routeKm(tid, i) {
  if (!geo(i.pickup_lat, i.pickup_lng) || !geo(i.dropoff_lat, i.dropoff_lng)) return null;
  return r2(dist(i.pickup_lat, i.pickup_lng, i.dropoff_lat, i.dropoff_lng) * N(P(tid, "route").roadFactor));
}
const minutesFor = (tid, km) => Math.max(1, Math.round(km / Math.max(1, N(P(tid, "route").kmPerHour)) * 60));
/* a shared ride's fare: the discount the store gives for sharing */
function poolFare(tid, fare) { return r2(N(fare) * (1 - N(P(tid, "pool").discountPct) / 100)); }
/* what a ride would cost, before it is asked for: { distance_km, duration_min, surge, fare, breakdown } — with no
   points on the map the fare is worked out from the trip's own distance and time when it ends */
function estimate(tid, input) {
  const i = input || {}, t = N(tid);
  if (!on(t)) fail("Rides are not open in this store", 403);
  const kind = MOB().vehicleKinds().find(k => k.key === String(i.vehicle_kind || "")) || MOB().vehicleKinds()[0];
  const km = routeKm(t, i);
  const dp = caps().cap(t, "dynamic_pricing"), surge = dp && Object.keys(dp).length ? MOB().surgeFor(t, geo(i.pickup_lat, i.pickup_lng) ? N(i.pickup_lat) : null, geo(i.pickup_lat, i.pickup_lng) ? N(i.pickup_lng) : null, kind.key) : 1;
  if (km == null) return { vehicle_kind: kind.key, surge, fare: null, distance_km: null, duration_min: null, byTrip: true };
  const min = minutesFor(t, km), f = MOB().computeFare(t, km, min, surge);
  const pool = !!i.pool && poolable(t, kind.key);
  return { vehicle_kind: kind.key, surge, distance_km: km, duration_min: min, fare: pool ? poolFare(t, f.fare) : f.fare, full: f.fare, pool, breakdown: f.breakdown };
}
/* a finished trip's distance and time, from its track when it has one, else the straight line between its points */
function measure(tid, rideId) {
  const r = db().get("SELECT * FROM rides WHERE id=? AND tenant_id=?", N(rideId), N(tid));
  if (!r) return {};
  const from = r.started_at || r.accepted_at || r.requested_at;
  const pts = db().all("SELECT lat, lng FROM ride_locations WHERE ride_id=? AND at>=? ORDER BY id", r.id, from || "");
  let km = 0; for (let k = 1; k < pts.length; k++) km += dist(pts[k - 1].lat, pts[k - 1].lng, pts[k].lat, pts[k].lng);
  if (pts.length < 2) km = routeKm(tid, r) || 0;
  const start = msOf(from), min = isFinite(start) ? Math.max(1, Math.round((Date.now() - start) / 60000)) : minutesFor(tid, km);
  return { distance_km: r2(km), duration_min: min };
}

/* ============================== asking for a ride ============================== */
function rideInput(tid, i) {
  const kinds = MOB().vehicleKinds();
  const kind = kinds.find(k => k.key === String(i.vehicle_kind || "")) || kinds[0];
  const pickup = str(i.pickup, 200), dropoff = str(i.dropoff, 200);
  if (!pickup || !dropoff) fail("Say where from and where to");
  for (const [a, b] of [["pickup_lat", "pickup_lng"], ["dropoff_lat", "dropoff_lng"]]) if ((i[a] != null && i[a] !== "") && !geo(i[a], i[b])) fail("A place on the map is a latitude and a longitude");
  const seats = Math.max(1, Math.floor(N(i.seats) || 1));
  if (seats > N(kind.capacity || 4)) fail("A " + kind.key + " seats " + (kind.capacity || 4));
  const g = (a, b) => geo(i[a], i[b]) ? [N(i[a]), N(i[b])] : [null, null];
  const [plat, plng] = g("pickup_lat", "pickup_lng"), [dlat, dlng] = g("dropoff_lat", "dropoff_lng");
  return { kind: kind.key, capacity: N(kind.capacity || 4), pickup, dropoff, plat, plng, dlat, dlng, seats, payment: str(i.payment_method, 20) || undefined, phone: str(i.rider_phone, 40) };
}
function activeOf(tid, userId) {
  const act = inTag("ride", "active");
  return db().get(`SELECT id, ref FROM rides WHERE tenant_id=? AND user_id=? AND status IN ${act.sql} LIMIT 1`, N(tid), N(userId), ...act.args);
}
/* a ride now, for a signed-in rider: { pickup, dropoff, *_lat/lng, vehicle_kind, seats, payment_method, pool } */
function request(tid, userId, input) {
  const t = N(tid), i = input || {};
  if (!on(t)) fail("Rides are not open in this store", 403);
  if (!userId) fail("Sign in to ask for a ride", 401);
  const x = rideInput(t, i);
  const busy = activeOf(t, userId); if (busy) fail("You already have a ride under way (" + busy.ref + ")", 409, "active_ride");
  if (i.pool) return pool(t, userId, x);
  const out = MOB().requestRide(t, userName(t, userId), x.phone, x.pickup, x.dropoff, x.kind, x.payment, x.plat, x.plng, { user_id: userId, seats: x.seats, dropoff_lat: x.dlat, dropoff_lng: x.dlng });
  return riderView(t, userId, out.id);
}

/* ============================== shared rides ============================== */
const poolable = (tid, kind) => (P(tid, "pool").kinds || []).includes(kind);
/* a forming pool this rider fits: same kind, room for their seats, nobody on board yet, and every
   rider in it picked up near this pickup and dropped near this drop */
function poolFor(tid, x) {
  const C = P(tid, "pool"), j = inTag(M.pool, "joinable"), act = inTag("ride", "active"), go = inTag("ride", "in_progress");
  for (const p of db().all(`SELECT * FROM ride_pools WHERE tenant_id=? AND vehicle_kind=? AND status IN ${j.sql} AND closes_at>? AND capacity - seats_taken >= ? ORDER BY id`, N(tid), x.kind, ...j.args, nowAt(), x.seats)) {
    const rides = db().all(`SELECT * FROM rides WHERE pool_id=? AND status IN ${act.sql}`, p.id, ...act.args);
    if (!rides.length || db().get(`SELECT 1 x FROM rides WHERE pool_id=? AND status IN ${go.sql}`, p.id, ...go.args)) continue;
    if (rides.every(r => geo(r.pickup_lat, r.pickup_lng) && geo(r.dropoff_lat, r.dropoff_lng)
      && dist(r.pickup_lat, r.pickup_lng, x.plat, x.plng) <= N(C.pickupWithinKm) && dist(r.dropoff_lat, r.dropoff_lng, x.dlat, x.dlng) <= N(C.dropoffWithinKm))) return p;
  }
  return null;
}
function pool(tid, userId, x) {
  const C = P(tid, "pool");
  if (!poolable(tid, x.kind)) fail("Shared rides are not offered in a " + x.kind, 409);
  if (x.seats > N(C.maxSeatsPerRider)) fail("A shared ride takes up to " + C.maxSeatsPerRider + " seats per rider");
  if (x.plat == null || x.dlat == null) fail("A shared ride needs the pickup and the drop on the map");
  const id = tx(() => {
    let p = poolFor(tid, x);
    if (p) {
      const w = db().run("UPDATE ride_pools SET seats_taken = seats_taken + ? WHERE id=? AND seats_taken + ? <= capacity", x.seats, p.id, x.seats);
      if (!w.changes) p = null;
    }
    if (!p) {
      const w = db().run("INSERT INTO ride_pools(tenant_id, vehicle_kind, capacity, seats_taken, status, closes_at) VALUES(?,?,?,?,?,?)",
        N(tid), x.kind, x.capacity, x.seats, states.initial(M.pool), at(Date.now() + N(C.openMinutes) * 60000));
      p = db().get("SELECT * FROM ride_pools WHERE id=?", N(w.lastInsertRowid));
    }
    const out = MOB().requestRide(tid, userName(tid, userId), x.phone, x.pickup, x.dropoff, x.kind, x.payment, x.plat, x.plng,
      { user_id: userId, seats: x.seats, pool_id: p.id, driver_id: p.driver_id || undefined, dropoff_lat: x.dlat, dropoff_lng: x.dlng });
    if (out.driver && !p.driver_id) db().run("UPDATE ride_pools SET driver_id=? WHERE id=?", out.driver.id, p.id);
    const now = db().get("SELECT * FROM ride_pools WHERE id=?", p.id);
    if (now.seats_taken >= now.capacity) closePool(now);
    return out.id;
  });
  return riderView(tid, userId, id);
}
function closePool(p) {
  if (!tagged(M.pool, p.status, "joinable")) return;
  const { patch } = states.apply(M.pool, { tenantId: p.tenant_id, from: p.status, to: states.first(M.pool, "terminal"), row: p });
  const cols = Object.keys(patch);
  db().run(`UPDATE ride_pools SET ${cols.map(c => c + "=?").join(", ")} WHERE id=? AND status=?`, ...cols.map(c => patch[c]), p.id, p.status);
}

/* ============================== dispatch: a driver for what waits ============================== */
/* puts a driver on a waiting ride, through the ride machine; false when someone else got there first */
function assign(tid, ride, driver, eta) {
  const to = states.first("ride", "assigned");
  const { patch } = states.apply("ride", { tenantId: tid, from: ride.status, to, row: ride });
  const cols = Object.keys(patch);
  const w = db().run(`UPDATE rides SET driver_id=?, eta_min=?, ${cols.map(c => c + "=?").join(", ")} WHERE id=? AND status=? AND driver_id IS NULL`, driver.id, N(eta) || 0, ...cols.map(c => patch[c]), ride.id, ride.status);
  if (!w.changes) return false;
  db().run("UPDATE drivers SET status=? WHERE id=?", states.first("driver", "engaged"), driver.id);
  db().run("INSERT INTO ride_events(tenant_id, ride_id, status, note) VALUES(?,?,?,?)", tid, ride.id, to, "dispatched to " + driver.name);
  return true;
}
/* rides still waiting for a driver get the nearest free one; the riders of a shared ride all get its driver */
function dispatchWaiting(tid) {
  const t = N(tid), dis = caps().cap(t, "dispatch");
  if (!on(t) || !dis || !Object.keys(dis).length || dis.auto_dispatch === false) return 0;
  const first = states.initial("ride"); let n = 0;
  for (const r of db().all("SELECT * FROM rides WHERE tenant_id=? AND status=? AND driver_id IS NULL ORDER BY id LIMIT 50", t, first)) {
    try {
      tx(() => {
        const mate = r.pool_id ? db().get("SELECT driver_id FROM ride_pools WHERE id=? AND driver_id IS NOT NULL", r.pool_id) : null;
        const d = mate ? db().get("SELECT * FROM drivers WHERE id=?", mate.driver_id) : null;
        const m = d ? { driver: d, eta_min: 0 } : MOB().matchDriver(t, r.vehicle_kind, r.pickup_lat, r.pickup_lng);
        if (!m || !assign(t, r, m.driver, m.eta_min)) return;
        n++;
        if (r.pool_id && !mate) db().run("UPDATE ride_pools SET driver_id=? WHERE id=? AND driver_id IS NULL", m.driver.id, r.pool_id);
      });
    } catch (e) { /* the ride moved meanwhile */ }
  }
  return n;
}

/* ============================== rides booked for later ============================== */
const nextRef = (tid, table, ref) => `${ref}-${N(tid)}-${String(db().get(`SELECT COUNT(*) c FROM ${table} WHERE tenant_id=?`, N(tid)).c + 1).padStart(5, "0")}`;
function scheduleRow(tid, id) { return db().get("SELECT * FROM ride_schedules WHERE id=? AND tenant_id=?", N(id), N(tid)) || fail("No such booking", 404); }
/* a ride booked for `pickup_at` (any time the browser gives, kept in UTC) */
function schedule(tid, userId, input) {
  const t = N(tid), i = input || {}, C = P(t, "schedule");
  if (!on(t)) fail("Rides are not open in this store", 403);
  if (!userId) fail("Sign in to book a ride", 401);
  const x = rideInput(t, i), when = Date.parse(String(i.pickup_at || ""));
  if (!isFinite(when)) fail("Say when to be picked up");
  if (when < Date.now() + N(C.minLeadMinutes) * 60000) fail("A ride is booked at least " + C.minLeadMinutes + " minutes ahead — ask for one now instead");
  if (when > Date.now() + N(C.maxDaysAhead) * 86400000) fail("A ride is booked up to " + C.maxDaysAhead + " days ahead");
  const e = estimate(t, { ...i, vehicle_kind: x.kind, pool: false });
  const w = RR().created(R.schedule, () => db().run(`INSERT INTO ride_schedules(tenant_id, ref, user_id, rider, rider_phone, pickup, dropoff, pickup_lat, pickup_lng, dropoff_lat, dropoff_lng, vehicle_kind, payment_method, seats, pickup_at, estimate, status, note)
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`, t, nextRef(t, "ride_schedules", "RS"), N(userId), userName(t, userId), x.phone, x.pickup, x.dropoff, x.plat, x.plng, x.dlat, x.dlng,
    x.kind, x.payment, x.seats, at(when), e.fare || 0, states.initial(M.schedule), str(i.note, 300)));
  return scheduleRow(t, w.lastInsertRowid);
}
function moveSchedule(s, to, extra) {
  const { patch } = states.apply(M.schedule, { tenantId: s.tenant_id, from: s.status, to, row: s });
  const all = { ...patch, ...(extra || {}) }, cols = Object.keys(all);
  RR().change(R.schedule, s.id, () => { const w = db().run(`UPDATE ride_schedules SET ${cols.map(c => c + "=?").join(", ")} WHERE id=? AND status=?`, ...cols.map(c => all[c]), s.id, s.status); if (!w.changes) fail("This booking has just changed — reload it", 409); return w; });
}
/* a booking is cancelled free until it is dispatched; after that it is a ride, cancelled as one */
function cancelSchedule(tid, id, userId) {
  const s = scheduleRow(tid, id);
  if (userId != null && N(s.user_id) !== N(userId)) fail("No such booking", 404);
  if (!tagged(M.schedule, s.status, "waiting")) fail("Only a booking that is still waiting is cancelled here", 409);
  moveSchedule(s, states.first(M.schedule, "cancelled"));
  return scheduleRow(tid, id);
}
/* bookings whose time has come are dispatched as rides; one the platform could not reach in time is missed */
function dispatchDue(tid) {
  const t = N(tid), C = P(t, "schedule"), wait = inTag(M.schedule, "waiting");
  let n = 0;
  for (const s of db().all(`SELECT * FROM ride_schedules WHERE tenant_id=? AND status IN ${wait.sql} AND pickup_at<=? ORDER BY pickup_at LIMIT 100`, t, ...wait.args, at(Date.now() + N(C.dispatchLeadMinutes) * 60000))) {
    try {
      tx(() => {
        if (msOf(s.pickup_at) + N(C.missedAfterMinutes) * 60000 < Date.now()) { moveSchedule(s, states.first(M.schedule, "missed")); return; }
        const out = MOB().requestRide(t, s.rider, s.rider_phone, s.pickup, s.dropoff, s.vehicle_kind, s.payment_method, s.pickup_lat, s.pickup_lng,
          { user_id: s.user_id, seats: s.seats, schedule_id: s.id, dropoff_lat: s.dropoff_lat, dropoff_lng: s.dropoff_lng });
        moveSchedule(s, states.first(M.schedule, "dispatched"), { ride_id: out.id });
        n++;
      });
    } catch (e) { /* changed meanwhile, or rides closed */ }
  }
  return n;
}
function schedules(tid, f) {
  const o = f || {};
  return db().all("SELECT * FROM ride_schedules WHERE tenant_id=? AND (?=0 OR user_id=?) AND (?='' OR status=?) ORDER BY pickup_at DESC LIMIT 300",
    N(tid), N(o.user_id) || 0, N(o.user_id) || 0, str(o.status), str(o.status)).map(s => ({ ...s, waiting: tagged(M.schedule, s.status, "waiting") }));
}

/* ============================== the live position ============================== */
const freshSince = tid => at(Date.now() - N(P(tid, "tracking").staleMinutes) * 60000);
/* the driver's phone reports where it is: kept on the driver, and on the track of each ride under way */
function ping(tid, driver, lat, lng) {
  if (!geo(lat, lng)) fail("A position is a latitude and a longitude");
  const C = P(tid, "tracking");
  if (driver.last_at && msOf(driver.last_at) > Date.now() - N(C.minSecondsBetween) * 1000) return { kept: false };
  const act = inTag("ride", "active"), now = nowAt();
  tx(() => {
    db().run("UPDATE drivers SET last_lat=?, last_lng=?, last_at=? WHERE id=?", N(lat), N(lng), now, driver.id);
    for (const r of db().all(`SELECT id FROM rides WHERE driver_id=? AND status IN ${act.sql}`, driver.id, ...act.args))
      db().run("INSERT INTO ride_locations(tenant_id, driver_id, ride_id, lat, lng, at) VALUES(?,?,?,?,?,?)", N(tid), driver.id, r.id, N(lat), N(lng), now);
  });
  return { kept: true, at: now };
}
/* a ride's track and where its driver is now, with the time to the pickup (before it) or the drop (on it) */
function track(tid, r) {
  const C = P(tid, "tracking"), d = r.driver_id ? db().get("SELECT * FROM drivers WHERE id=?", r.driver_id) : null;
  const pts = db().all("SELECT lat, lng, at FROM ride_locations WHERE ride_id=? ORDER BY id DESC LIMIT ?", r.id, N(C.trackPoints)).reverse();
  const live = !rideTag(r.status, "terminal") && d && d.last_lat != null && d.last_at >= freshSince(tid);
  const per = N((caps().cap(N(tid), "dispatch") || {}).eta_per_km_minutes) || 3;
  let eta = null;
  if (live) {
    const [la, ln] = rideTag(r.status, "in_progress") ? [r.dropoff_lat, r.dropoff_lng] : [r.pickup_lat, r.pickup_lng];
    if (geo(la, ln)) eta = Math.max(1, Math.round(dist(d.last_lat, d.last_lng, la, ln) * N(P(tid, "route").roadFactor) * per));
  }
  return { points: pts, driver: live ? { lat: d.last_lat, lng: d.last_lng, at: d.last_at } : null, eta_min: eta,
    pickup: geo(r.pickup_lat, r.pickup_lng) ? { lat: r.pickup_lat, lng: r.pickup_lng } : null, dropoff: geo(r.dropoff_lat, r.dropoff_lng) ? { lat: r.dropoff_lat, lng: r.dropoff_lng } : null };
}

/* ============================== ratings, both ways ============================== */
const ageDays = s => (Date.now() - msOf(s)) / 86400000;
/* { by: "rider" | "driver", stars 1–5, tags, comment } — once per side, within the window after the trip */
function rate(tid, rideId, input) {
  const t = N(tid), i = input || {}, C = P(t, "rating"), r = rideRow(t, rideId);
  if (!rideTag(r.status, "rateable")) fail("Only a completed ride is rated", 409);
  if (ended(r) && ageDays(ended(r)) > N(C.windowDays)) fail("A ride is rated within " + C.windowDays + " days of it", 409);
  const by = i.by === SIDE.driver ? SIDE.driver : SIDE.rider, stars = N(i.stars);
  if (!(Number.isInteger(stars) && stars >= 1 && stars <= 5)) fail("Rate 1 to 5 stars");
  const allowed = new Set([...(by === SIDE.rider ? C.riderTags : C.driverTags), ...C.lowTags]);
  const tags = [...new Set((Array.isArray(i.tags) ? i.tags : []).map(x => str(x, 60)))].filter(x => allowed.has(x)).slice(0, 8);
  tx(() => {
    const w = db().run("INSERT INTO ride_ratings(tenant_id, ride_id, by_role, driver_id, user_id, stars, tags, comment) VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(ride_id, by_role) DO NOTHING",
      t, r.id, by, r.driver_id, r.user_id, stars, JSON.stringify(tags), str(i.comment, 500));
    if (!w.changes) fail("This ride is already rated", 409, "rated");
    if (by === SIDE.rider) { db().run("UPDATE rides SET rating=? WHERE id=?", stars, r.id); if (r.driver_id) refreshDriver(t, r.driver_id); }
  });
  return ratingsOf(t, r.id);
}
/* the floor: the fleet's minimum rating to dispatch when fleet management is on, else the policy's */
const floorOf = tid => { const f = N((caps().cap(N(tid), "fleet_management") || {}).min_rating_to_dispatch); return f > 0 ? f : N(P(tid, "rating").reviewBelow); };
/* a driver's rating is the average of their recent ratings; one below the floor is held for review */
function refreshDriver(tid, driverId) {
  const C = P(tid, "rating");
  const xs = db().all("SELECT stars FROM ride_ratings WHERE tenant_id=? AND driver_id=? AND by_role='rider' ORDER BY id DESC LIMIT ?", N(tid), N(driverId), N(C.averageOver));
  if (!xs.length) return;
  const avg = r2(xs.reduce((s, x) => s + N(x.stars), 0) / xs.length), low = xs.length >= N(C.minToJudge) && avg < floorOf(tid);
  const n = db().get("SELECT COUNT(*) n FROM ride_ratings WHERE tenant_id=? AND driver_id=? AND by_role='rider'", N(tid), N(driverId)).n;
  db().run("UPDATE drivers SET rating=?, rating_count=?, review=CASE WHEN ?=1 THEN 1 ELSE review END WHERE id=?", avg, n, low ? 1 : 0, N(driverId));
}
/* the store looked at a held driver and lets them drive again */
function clearReview(tid, driverId) {
  const w = db().run("UPDATE drivers SET review=0 WHERE id=? AND tenant_id=?", N(driverId), N(tid));
  if (!w.changes) fail("No such driver", 404);
  return db().get("SELECT * FROM drivers WHERE id=?", N(driverId));
}
/* a rider's rating, from what their drivers gave them */
function riderRating(tid, userId) {
  if (!userId) return null;
  const xs = db().all("SELECT stars FROM ride_ratings WHERE tenant_id=? AND user_id=? AND by_role='driver' ORDER BY id DESC LIMIT ?", N(tid), N(userId), N(P(tid, "rating").averageOver));
  return xs.length ? { stars: r2(xs.reduce((s, x) => s + N(x.stars), 0) / xs.length), count: xs.length } : null;
}
function ratingsOf(tid, rideId) {
  const out = {};
  for (const x of db().all("SELECT by_role, stars, tags, comment, at FROM ride_ratings WHERE ride_id=? AND tenant_id=?", N(rideId), N(tid))) out[x.by_role] = { ...x, tags: JSON.parse(x.tags || "[]") };
  return out;
}
function ratingVocab(tid) { const C = P(tid, "rating"); return { riderTags: C.riderTags, driverTags: C.driverTags, lowTags: C.lowTags, windowDays: C.windowDays }; }

/* ============================== tips ============================== */
/* a rider's tip on a finished ride, once, among the amounts the tips capability offers or up to its largest */
function tip(tid, userId, rideId, amount) {
  const t = N(tid), r = mineRide(t, userId, rideId), T = require("./tips.js");
  if (!T.on(t)) fail("This store does not take tips", 403);
  if (!rideTag(r.status, "success")) fail("A tip is added to a finished ride", 409);
  if (ended(r) && ageDays(ended(r)) > N(P(t, "rating").windowDays)) fail("A tip is added within " + P(t, "rating").windowDays + " days of the ride", 409);
  const v = T.vocabulary(t), a = r2(amount);
  if (!(a > 0 && a <= N(v.max))) fail("A tip is more than 0 and at most " + v.max);
  tx(() => {
    const w = db().run("UPDATE rides SET tip=? WHERE id=? AND tip=0 AND payout_id IS NULL", a, r.id);
    if (!w.changes) fail(r.payout_id ? "This trip is already paid out to the driver" : "This ride already has a tip", 409);
    if (r.driver_id) db().run("UPDATE drivers SET earnings = earnings + ? WHERE id=?", a, r.driver_id);
  });
  return riderView(t, userId, r.id);
}

/* ============================== sharing a trip ============================== */
/* a private link to the ride's progress, for whoever the rider sends it to; readable until a while after the ride */
function share(tid, userId, rideId) {
  const r = mineRide(tid, userId, rideId);
  if (rideTag(r.status, "terminal")) fail("This ride is over", 409);
  if (r.share_token) return { token: r.share_token };
  const token = crypto.randomBytes(24).toString("base64url");
  db().run("UPDATE rides SET share_token=? WHERE id=? AND share_token IS NULL", token, r.id);
  return { token: rideRow(tid, r.id).share_token };
}
/* what the link shows: the ride's progress, the driver's first name, the car, and the live position */
function sharedView(token) {
  const tk = str(token, 64);
  const r = tk.length >= 20 ? db().get("SELECT * FROM rides WHERE share_token=?", tk) : null;
  if (!r) fail("This link is not valid", 404);
  const end = ended(r);
  if (end && msOf(end) + N(P(r.tenant_id, "share").hoursAfter) * 3600000 < Date.now()) fail("This trip is over and its link has closed", 410, "closed");
  const d = r.driver_id ? db().get("SELECT name, vehicle_kind, plate, rating FROM drivers WHERE id=?", r.driver_id) : null;
  return { store: (db().get("SELECT name FROM tenants WHERE id=?", r.tenant_id) || {}).name || "", ref: r.ref, status: r.status, label: labelOf(r.status),
    rider: firstName(r.rider), pickup: r.pickup, dropoff: r.dropoff, ended: !!end, done: rideTag(r.status, "success"), started_at: r.started_at,
    driver: d ? { name: firstName(d.name), vehicle_kind: d.vehicle_kind, plate: d.plate, rating: d.rating } : null, track: track(r.tenant_id, r) };
}
const labelOf = s => { try { return states.display("ride", s).label; } catch (e) { return s; } };

/* ============================== safety ============================== */
const kindsOf = tid => P(tid, "safety").kinds || SEED.safety.kinds;
function emergencyNumber(tid) {
  const S = P(tid, "safety"); let c = "";
  try { c = String(require("./stores.js").country(N(tid)) || "").toUpperCase(); } catch (e) { }
  return (S.emergencyNumbers || {})[c] || S.emergencyDefault;
}
function safetyRow(tid, id) { return db().get("SELECT * FROM ride_safety_events WHERE id=? AND tenant_id=?", N(id), N(tid)) || fail("No such report", 404); }
/* an emergency raised, or an incident reported, on a ride by its rider or its driver: { kind, note, lat, lng } */
function raise(tid, ride, who, input) {
  const t = N(tid), i = input || {}, k = kindsOf(t).find(x => x.key === String(i.kind || ""));
  if (!k) fail("Say what happened: " + kindsOf(t).map(x => x.key).join(", "));
  if (!k.urgent && !str(i.note)) fail("Tell us what happened");
  if (ended(ride) && ageDays(ended(ride)) > N(P(t, "rating").windowDays) * 4) fail("This ride is too long ago to report here — contact the store", 409);
  const pos = geo(i.lat, i.lng) ? [N(i.lat), N(i.lng)] : (() => { const d = ride.driver_id && db().get("SELECT last_lat, last_lng FROM drivers WHERE id=?", ride.driver_id); return d && geo(d.last_lat, d.last_lng) ? [d.last_lat, d.last_lng] : [null, null]; })();
  const w = RR().created(R.safety, () => db().run("INSERT INTO ride_safety_events(tenant_id, ref, ride_id, kind, by_role, by_who, lat, lng, note, status) VALUES(?,?,?,?,?,?,?,?,?,?)",
    t, nextRef(t, "ride_safety_events", "SAF"), ride.id, k.key, who.role, str(who.name, 120), pos[0], pos[1], str(i.note, 1000), states.initial(M.safety)));
  return { ...safetyRow(t, w.lastInsertRowid), urgent: !!k.urgent, label: k.label, emergency: emergencyNumber(t), ride: ride.ref };
}
function raiseByRider(tid, userId, rideId, input) { const r = mineRide(tid, userId, rideId); return raise(tid, r, { role: SIDE.rider, name: userName(tid, userId) }, input); }
function raiseByDriver(tid, driver, rideId, input) { const r = driverRide(tid, driver, rideId); return raise(tid, r, { role: SIDE.driver, name: driver.name }, input); }
function moveSafety(e, to, extra) {
  const { patch } = states.apply(M.safety, { tenantId: e.tenant_id, from: e.status, to, row: e });
  const all = { ...patch, ...(extra || {}) }, cols = Object.keys(all);
  RR().change(R.safety, e.id, () => { const w = db().run(`UPDATE ride_safety_events SET ${cols.map(c => c + "=?").join(", ")} WHERE id=? AND status=?`, ...cols.map(c => all[c]), e.id, e.status); if (!w.changes) fail("This report has just changed — reload it", 409); return w; });
}
function acknowledge(tid, id, actor) {
  const e = safetyRow(tid, id);
  if (!tagged(M.safety, e.status, "unhandled")) fail("Someone is already on this", 409);
  moveSafety(e, states.first(M.safety, "handling"), { handled_by: str(actor, 120) });
  return safety(tid, { id });
}
function resolve(tid, id, actor, outcome) {
  const e = safetyRow(tid, id);
  if (!tagged(M.safety, e.status, "open")) fail("This report is already closed", 409);
  if (!str(outcome)) fail("Say how it was resolved");
  moveSafety(e, states.first(M.safety, "resolved"), { handled_by: e.handled_by || str(actor, 120), outcome: str(outcome, 1000) });
  return safety(tid, { id });
}
/* reports, the open emergencies first; `id`, `status` narrow them */
function safety(tid, f) {
  const o = f || {}, open = states.tagged(M.safety, "open"), kinds = new Map(kindsOf(tid).map(k => [k.key, k]));
  const rows = db().all(`SELECT e.*, r.ref ride_ref, r.rider, r.pickup, r.dropoff, d.name driver_name, d.phone driver_phone, r.rider_phone FROM ride_safety_events e LEFT JOIN rides r ON r.id=e.ride_id LEFT JOIN drivers d ON d.id=r.driver_id
    WHERE e.tenant_id=? AND (?=0 OR e.id=?) AND (?='' OR e.status=?) ORDER BY CASE WHEN e.status IN ${ph(open)} THEN 0 ELSE 1 END, e.id DESC LIMIT 300`,
    N(tid), N(o.id) || 0, N(o.id) || 0, str(o.status), str(o.status), ...open);
  const out = rows.map(e => ({ ...e, label: (kinds.get(e.kind) || {}).label || e.kind, urgent: !!(kinds.get(e.kind) || {}).urgent, open: open.includes(e.status), unhandled: tagged(M.safety, e.status, "unhandled") }));
  return o.id ? out[0] || fail("No such report", 404) : out;
}

/* ============================== the rider ============================== */
function canFor(tid, r, userId) {
  const T = require("./tips.js"), C = P(tid, "rating"), end = ended(r), fresh = !end || ageDays(end) <= N(C.windowDays);
  const cancelTo = states.first("ride", "failure"), mine = ratingsOf(tid, r.id);
  return { cancel: states.can("ride", r.status, cancelTo) && !rideTag(r.status, "in_progress"), share: !rideTag(r.status, "terminal"), sos: !end || ageDays(end) < 1,
    rate: rideTag(r.status, "rateable") && fresh && !mine.rider, tip: T.on(tid) && rideTag(r.status, "success") && fresh && !N(r.tip) && !r.payout_id, report: !!end };
}
function riderView(tid, userId, id) {
  const r = mineRide(tid, userId, id), d = r.driver_id ? db().get("SELECT name, vehicle_kind, plate, rating, phone FROM drivers WHERE id=?", r.driver_id) : null;
  const pool = r.pool_id ? db().get("SELECT capacity, seats_taken, status FROM ride_pools WHERE id=?", r.pool_id) : null;
  return { id: r.id, ref: r.ref, status: r.status, label: labelOf(r.status), on_board: rideTag(r.status, "in_progress"), pickup: r.pickup, dropoff: r.dropoff, vehicle_kind: r.vehicle_kind, seats: r.seats, payment_method: r.payment_method,
    fare: r.fare, surge: r.surge, tip: r.tip, distance_km: r.distance_km, duration_min: r.duration_min, eta_min: r.eta_min, requested_at: r.requested_at, completed_at: r.completed_at, cancelled_at: r.cancelled_at,
    pool: pool ? { riders: db().get("SELECT COUNT(*) n FROM rides WHERE pool_id=?", r.pool_id).n, seats_taken: pool.seats_taken, capacity: pool.capacity } : null,
    driver: d ? { name: firstName(d.name), vehicle_kind: d.vehicle_kind, plate: d.plate, rating: d.rating, phone: rideTag(r.status, "terminal") ? "" : d.phone } : null,
    share_token: r.share_token || null, ratings: ratingsOf(tid, r.id), can: canFor(tid, r, userId), track: rideTag(r.status, "terminal") ? null : track(tid, r) };
}
function cancelByRider(tid, userId, id) {
  const r = mineRide(tid, userId, id), to = states.first("ride", "failure");
  if (!canFor(tid, r, userId).cancel) fail("This ride can no longer be cancelled here", 409);
  tx(() => { MOB().updateRide(N(tid), r.id, to, "cancelled by the rider"); if (r.pool_id) db().run("UPDATE ride_pools SET seats_taken = seats_taken - ? WHERE id=? AND seats_taken >= ?", r.seats, r.pool_id, r.seats); });
  return riderView(tid, userId, r.id);
}
/* the rider's page: what is under way, what is booked, and past rides */
function mine(tid, userId) {
  const t = N(tid);
  if (!on(t)) fail("Rides are not open in this store", 403);
  const act = inTag("ride", "active");
  const active = db().all(`SELECT id FROM rides WHERE tenant_id=? AND user_id=? AND status IN ${act.sql} ORDER BY id DESC`, t, N(userId), ...act.args).map(r => riderView(t, userId, r.id));
  const past = db().all(`SELECT id FROM rides WHERE tenant_id=? AND user_id=? AND status NOT IN ${act.sql} ORDER BY id DESC LIMIT 30`, t, N(userId), ...act.args).map(r => riderView(t, userId, r.id));
  const T = require("./tips.js"), S = P(t, "schedule");
  return { active, past, bookings: schedules(t, { user_id: userId }).slice(0, 30), me: { rating: riderRating(t, userId) },
    kinds: MOB().vehicleKinds(), poolKinds: P(t, "pool").kinds, poolDiscountPct: P(t, "pool").discountPct, places: places(t), ratings: ratingVocab(t),
    tips: T.vocabulary(t), safety: { kinds: kindsOf(t), emergency: emergencyNumber(t) }, schedule: { minLeadMinutes: S.minLeadMinutes, maxDaysAhead: S.maxDaysAhead } };
}

/* ============================== the driver ============================== */
function driverRideView(tid, r) {
  const mineRated = ratingsOf(tid, r.id).driver;
  return { id: r.id, ref: r.ref, status: r.status, label: labelOf(r.status), rider: firstName(r.rider), rider_phone: rideTag(r.status, "terminal") ? "" : r.rider_phone, rider_rating: riderRating(tid, r.user_id),
    pickup: r.pickup, dropoff: r.dropoff, seats: r.seats, pool_id: r.pool_id, payment_method: r.payment_method, fare: r.fare, tip: r.tip, take: r.take,
    next: rideTag(r.status, "terminal") ? [] : (states.labelledMoves("ride") || []).filter(m => m.from === r.status && !rideTag(m.to, "failure")).map(m => ({ to: m.to, label: m.label })),
    canCancel: !rideTag(r.status, "terminal") && states.can("ride", r.status, states.first("ride", "failure")), cancelTo: states.first("ride", "failure"),
    canRate: rideTag(r.status, "rateable") && !mineRated && (!ended(r) || ageDays(ended(r)) <= N(P(tid, "rating").windowDays)), rated: mineRated || null, track: rideTag(r.status, "terminal") ? null : track(tid, r) };
}
function driverHome(tid, email) {
  const t = N(tid);
  if (!on(t)) fail("Rides are not open in this store", 403);
  const d = asDriver(t, email), act = inTag("ride", "active");
  const active = db().all(`SELECT * FROM rides WHERE driver_id=? AND status IN ${act.sql} ORDER BY id`, d.id, ...act.args).map(r => driverRideView(t, r));
  const recent = db().all(`SELECT * FROM rides WHERE driver_id=? AND status NOT IN ${act.sql} ORDER BY id DESC LIMIT 20`, d.id, ...act.args).map(r => driverRideView(t, r));
  const today = at(Date.now()).slice(0, 10);
  return { me: { id: d.id, name: d.name, status: d.status, online: states.is("driver", d.status, "online"), rating: d.rating, rating_count: d.rating_count, review: !!d.review, vehicle_kind: d.vehicle_kind, plate: d.plate, last_at: d.last_at },
    active, recent, today: statement(t, d.id, today, today).totals, ratings: ratingVocab(t), safety: { kinds: kindsOf(t), emergency: emergencyNumber(t) } };
}
function goOnline(tid, email, online) {
  const d = asDriver(tid, email);
  if (states.is("driver", d.status, "blocked")) fail("Your account is suspended — contact the store", 403);
  MOB().toggleDriver(N(tid), d.id, !!online);
  if (online) dispatchWaiting(tid);
  return driverHome(tid, email);
}
function pingAs(tid, email, lat, lng) { return ping(N(tid), asDriver(tid, email), lat, lng); }
/* the driver moves their ride on: arrived, on the way, dropped off — or cancels it */
function advance(tid, email, rideId, to) {
  const d = asDriver(tid, email), r = driverRide(tid, d, rideId), cancel = rideTag(String(to || ""), "failure");
  if (!states.can("ride", r.status, String(to || ""))) fail("That is not the next step for this ride", 409);
  tx(() => {
    MOB().updateRide(N(tid), r.id, String(to), cancel ? "cancelled by the driver" : "by the driver");
    /* once someone is on board, nobody else joins the shared ride */
    if (r.pool_id && rideTag(String(to), "in_progress")) { const p = db().get("SELECT * FROM ride_pools WHERE id=?", r.pool_id); if (p) closePool(p); }
  });
  if (cancel) dispatchWaiting(tid);
  return driverHome(tid, email);
}
function rateByDriver(tid, email, rideId, input) { const d = asDriver(tid, email); driverRide(tid, d, rideId); rate(tid, rideId, { ...(input || {}), by: SIDE.driver }); return driverHome(tid, email); }

/* ============================== earnings and payouts ============================== */
/* each trip that earned: the fare (or the cancellation fee), the platform's share, the tip, and what the driver keeps */
function statement(tid, driverId, from, to) {
  const t = N(tid), bill = inTag("ride", "billable");
  const a = /^\d{4}-\d{2}-\d{2}$/.test(String(from || "")) ? from : "0000-01-01", b = /^\d{4}-\d{2}-\d{2}$/.test(String(to || "")) ? to : "9999-12-31";
  const rows = db().all(`SELECT r.*, p.ref payout_ref, p.status payout_status FROM rides r LEFT JOIN driver_payouts p ON p.id=r.payout_id
    WHERE r.tenant_id=? AND r.driver_id=? AND r.status IN ${bill.sql} AND (r.fare>0 OR r.tip>0) AND COALESCE(r.completed_at, r.cancelled_at)>=? AND COALESCE(r.completed_at, r.cancelled_at)<? ORDER BY COALESCE(r.completed_at, r.cancelled_at) DESC LIMIT 2000`,
    t, N(driverId), ...bill.args, a, b + " 99");
  const trips = rows.map(r => ({ id: r.id, ref: r.ref, at: ended(r), pickup: r.pickup, dropoff: r.dropoff, status: r.status, cancelled: rideTag(r.status, "failure"), pool: !!r.pool_id,
    distance_km: r.distance_km, fare: r2(r.fare), take: r2(r.take), tip: r2(r.tip), net: r2(N(r.fare) - N(r.take) + N(r.tip)), payout: r.payout_ref || null }));
  const sum = (xs, k) => r2(xs.reduce((s, x) => s + x[k], 0)), unpaid = trips.filter(x => !x.payout);
  return { from: a, to: b, trips, totals: { trips: trips.length, fares: sum(trips, "fare"), take: sum(trips, "take"), tips: sum(trips, "tip"), net: sum(trips, "net") },
    unpaid: { trips: unpaid.length, net: sum(unpaid, "net") } };
}
function statementAs(tid, email, from, to) { const d = asDriver(tid, email); return { driver: { id: d.id, name: d.name }, ...statement(tid, d.id, from, to), payouts: payouts(tid, { driver_id: d.id }) }; }
function payoutRow(tid, id) { return db().get("SELECT * FROM driver_payouts WHERE id=? AND tenant_id=?", N(id), N(tid)) || fail("No such payout", 404); }
/* a payout of everything a driver earned up to `through` (a day) that no payout has taken */
function createPayout(tid, input, actor) {
  const t = N(tid), i = input || {}, d = db().get("SELECT * FROM drivers WHERE id=? AND tenant_id=?", N(i.driver_id), t) || fail("No such driver", 404);
  const through = /^\d{4}-\d{2}-\d{2}$/.test(String(i.through || "")) ? i.through : at(Date.now() - 86400000).slice(0, 10);
  return tx(() => {
    const s = statement(t, d.id, "0000-01-01", through), due = s.trips.filter(x => !x.payout);
    if (!due.length) fail(d.name + " has nothing unpaid up to " + through, 409, "nothing_due");
    const sum = k => r2(due.reduce((a, x) => a + x[k], 0)), currency = require("./defaults.js").currency(t);
    const w = RR().created(R.payout, () => db().run("INSERT INTO driver_payouts(tenant_id, ref, driver_id, currency, through, trips, fares, take, tips, net, status, created_by) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
      t, nextRef(t, "driver_payouts", P(t, "payout").ref), d.id, currency, through, due.length, sum("fare"), sum("take"), sum("tip"), sum("net"), states.initial(M.payout), str(actor, 120)));
    const id = N(w.lastInsertRowid), ids = due.map(x => x.id);
    const c = db().run(`UPDATE rides SET payout_id=? WHERE id IN ${ph(ids)} AND payout_id IS NULL`, id, ...ids);
    if (c.changes !== ids.length) fail("Some of these trips were just paid out — try again", 409);
    return payout(t, id);
  });
}
function movePayout(p, to, extra) {
  const { patch } = states.apply(M.payout, { tenantId: p.tenant_id, from: p.status, to, row: p });
  const all = { ...patch, ...(extra || {}) }, cols = Object.keys(all);
  RR().change(R.payout, p.id, () => { const w = db().run(`UPDATE driver_payouts SET ${cols.map(c => c + "=?").join(", ")} WHERE id=? AND status=?`, ...cols.map(c => all[c]), p.id, p.status); if (!w.changes) fail("This payout has just changed — reload it", 409); return w; });
}
/* approved by someone other than whoever made it: the books owe it to the driver */
function approvePayout(tid, id, actor) {
  const p = payoutRow(tid, id);
  if (!tagged(M.payout, p.status, "editable")) fail("Only a pending payout is approved", 409);
  if (str(actor, 120) && str(actor, 120) === p.created_by) fail("Whoever made a payout does not approve it", 403, "own_payout");
  movePayout(p, states.first(M.payout, "owed"), { approved_by: str(actor, 120) });
  return payout(tid, id);
}
function payPayout(tid, id, payRef) {
  const p = payoutRow(tid, id);
  if (!tagged(M.payout, p.status, "owed")) fail("Only an approved payout is paid", 409);
  movePayout(p, states.first(M.payout, "success"), { pay_ref: str(payRef, 120) });
  return payout(tid, id);
}
/* a payout not yet paid is voided: its trips are free to be paid again */
function voidPayout(tid, id) {
  const p = payoutRow(tid, id);
  if (tagged(M.payout, p.status, "terminal")) fail("A payout that is paid or void stays as it is", 409);
  tx(() => { movePayout(p, states.first(M.payout, "void")); db().run("UPDATE rides SET payout_id=NULL WHERE payout_id=?", p.id); });
  return payout(tid, id);
}
function payout(tid, id) {
  const p = payoutRow(tid, id), d = db().get("SELECT name FROM drivers WHERE id=?", p.driver_id) || {};
  return { ...p, driver: d.name || "", editable: tagged(M.payout, p.status, "editable"), owed: tagged(M.payout, p.status, "owed"), open: !tagged(M.payout, p.status, "terminal"),
    rides: db().all("SELECT ref, fare, take, tip, COALESCE(completed_at, cancelled_at) at FROM rides WHERE payout_id=? ORDER BY id", p.id) };
}
function payouts(tid, f) {
  const o = f || {};
  return db().all("SELECT p.*, d.name driver FROM driver_payouts p LEFT JOIN drivers d ON d.id=p.driver_id WHERE p.tenant_id=? AND (?=0 OR p.driver_id=?) AND (?='' OR p.status=?) ORDER BY p.id DESC LIMIT 300",
    N(tid), N(o.driver_id) || 0, N(o.driver_id) || 0, str(o.status), str(o.status))
    .map(p => ({ ...p, editable: tagged(M.payout, p.status, "editable"), owed: tagged(M.payout, p.status, "owed"), open: !tagged(M.payout, p.status, "terminal") }));
}
/* what each driver has earned and not yet been paid */
function unpaid(tid) {
  const t = N(tid), bill = inTag("ride", "billable");
  return db().all(`SELECT d.id, d.name, COUNT(r.id) trips, COALESCE(SUM(r.fare - r.take + r.tip),0) net FROM drivers d JOIN rides r ON r.driver_id=d.id
    WHERE d.tenant_id=? AND r.status IN ${bill.sql} AND (r.fare>0 OR r.tip>0) AND r.payout_id IS NULL GROUP BY d.id, d.name ORDER BY d.name`, t, ...bill.args).map(x => ({ ...x, net: r2(x.net) }));
}

/* ============================== places riders pick from ============================== */
function places(tid) { const l = own(tid).places; return Array.isArray(l) ? l : []; }
/* [{ name, lat, lng }] — the store's named places (a station, the airport), offered when a rider asks for a ride */
function setPlaces(tid, list) {
  if (!Array.isArray(list)) fail("Send the places as a list");
  const out = list.slice(0, 200).map(p => ({ name: str(p && p.name, 120), lat: N(p && p.lat), lng: N(p && p.lng) }));
  for (const p of out) { if (!p.name) fail("Name each place"); if (!geo(p.lat, p.lng)) fail(p.name + ": a place is a latitude and a longitude"); }
  require("./settings.js").save(N(tid), { trips: { ...own(tid), places: out } });
  return places(tid);
}

/* ============================== the store's view ============================== */
function overview(tid) {
  const t = N(tid), wait = inTag(M.schedule, "waiting"), j = inTag(M.pool, "joinable"), C = P(t, "rating");
  return {
    safety: safety(t, {}).slice(0, 100),
    bookings: db().all(`SELECT * FROM ride_schedules WHERE tenant_id=? AND status IN ${wait.sql} ORDER BY pickup_at LIMIT 200`, t, ...wait.args),
    pools: db().all(`SELECT p.*, d.name driver_name, (SELECT COUNT(*) FROM rides r WHERE r.pool_id=p.id) riders FROM ride_pools p LEFT JOIN drivers d ON d.id=p.driver_id WHERE p.tenant_id=? AND p.status IN ${j.sql} ORDER BY p.id DESC LIMIT 100`, t, ...j.args),
    review: db().all("SELECT id, name, rating, rating_count, review, status FROM drivers WHERE tenant_id=? AND deactivated_at IS NULL AND (review=1 OR (rating_count>=? AND rating<?)) ORDER BY rating", t, N(C.minToJudge), floorOf(t)),
    ratings: db().all("SELECT g.*, r.ref, d.name driver_name FROM ride_ratings g JOIN rides r ON r.id=g.ride_id LEFT JOIN drivers d ON d.id=g.driver_id WHERE g.tenant_id=? ORDER BY g.id DESC LIMIT 100", t).map(x => ({ ...x, tags: JSON.parse(x.tags || "[]") })),
    unpaid: unpaid(t), payouts: payouts(t, {}), drivers: db().all("SELECT id, name FROM drivers WHERE tenant_id=? AND deactivated_at IS NULL ORDER BY name", t),
    places: places(t), emergency: emergencyNumber(t),
    policy: { rating: { ...C, floor: floorOf(t) }, pool: P(t, "pool"), schedule: P(t, "schedule") }
  };
}

/* ============================== the clock ============================== */
/* bookings dispatched when due, waiting rides given a driver, shared rides closed when their time is up */
function sweep(tid) {
  const t = N(tid), j = inTag(M.pool, "joinable");
  const due = dispatchDue(t);
  for (const p of db().all(`SELECT * FROM ride_pools WHERE tenant_id=? AND status IN ${j.sql} AND closes_at<=?`, t, ...j.args, nowAt())) { try { closePool(p); } catch (e) { } }
  return { due, dispatched: dispatchWaiting(t) };
}
function sweepAll() {
  let n = 0;
  for (const r of db().all("SELECT DISTINCT tenant_id FROM rides UNION SELECT DISTINCT tenant_id FROM ride_schedules")) {
    try { if (on(r.tenant_id)) { const x = sweep(r.tenant_id); n += x.due + x.dispatched; } } catch (e) { console.error("trips sweep:", e.message); }
  }
  return n;
}

module.exports = {
  estimate, measure, poolFare, request, schedule, cancelSchedule, schedules, dispatchDue, dispatchWaiting,
  freshSince, ping, pingAs, track, rate, refreshDriver, clearReview, riderRating, ratingsOf, tip,
  share, sharedView, emergencyNumber, raiseByRider, raiseByDriver, acknowledge, resolve, safety,
  riderView, cancelByRider, mine, driverOf, driverHome, goOnline, advance, rateByDriver,
  statement, statementAs, createPayout, approvePayout, payPayout, voidPayout, payout, payouts, unpaid,
  places, setPlaces, overview, sweep, sweepAll, SEED
};
