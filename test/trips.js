/* Trips (lib/trips.js): ratings both ways, rides booked for later, shared rides, the live position,
   safety, and what drivers earn and are paid — on a fresh database. */
"use strict";
const path = require("path");
const DB = path.join(__dirname, "trips-tmp.db");
process.env.LX_DB = DB; process.env.NODE_ENV = "test";
for (const s of ["", "-wal", "-shm"]) { try { require("fs").rmSync(DB + s, { force: true }); } catch (e) { } }
const db = require("../lib/db.js");
const caps = require("../lib/capabilities.js");
const mob = require("../lib/mobility.js");
const T = require("../lib/trips.js");
const states = require("../lib/states.js");
let pass = 0, fail = 0;
const ok = (c, n, x) => { c ? (pass++, console.log("  ✓ " + n)) : (fail++, console.log("  ✗ " + n + (x !== undefined ? " → " + JSON.stringify(x).slice(0, 300) : ""))); };
const throws = (fn, re, n) => { try { fn(); ok(false, n, "did not throw"); } catch (e) { ok(re.test(e.message), n, e.message); } };
const code = (fn, c, n) => { try { fn(); ok(false, n, "did not throw"); } catch (e) { ok(e.status === c || e.code === c, n, [e.status, e.code, e.message]); } };
const at = ms => new Date(ms).toISOString().slice(0, 19).replace("T", " ");

(async () => {
  console.log("▸ TRIPS");
  await caps.seed(); await caps.seedPresets(); await mob.seed();
  const t = 1;
  throws(() => T.estimate(t, {}), /not open/, "nothing works until rides are open in the store");
  for (const k of ["ride_hailing", "dynamic_pricing", "dispatch", "fleet_management", "tips"]) caps.enable(t, k, {});
  /* our own riders and drivers, with the demo fleet off the road and surge zones paused */
  db.run("UPDATE drivers SET status='offline' WHERE tenant_id=?", t);
  db.run("UPDATE surge_zones SET active=0 WHERE tenant_id=?", t);
  const user = (name, email) => Number(db.run("INSERT INTO users(tenant_id,name,email,salt,hash) VALUES(?,?,?,?,?)", t, name, email, "s", "h").lastInsertRowid);
  const ann = user("Ann Rider", "ann@example.test"), bob = user("Bob Rider", "bob@example.test"), cy = user("Cy Rider", "cy@example.test");
  const drv = (name, email, kind) => mob.upsertDriver(t, { name, email, vehicle_kind: kind, plate: "TR-" + name.slice(0, 3).toUpperCase() });
  const d1 = drv("Dana Driver", "dana@example.test", "car"), d2 = drv("Eli Driver", "eli@example.test", "car");
  /* 40.70,-74.00 is the pickup area; Dana is 0.5 km away, Eli 4 km away */
  T.goOnline(t, "dana@example.test", true); T.goOnline(t, "eli@example.test", true);
  db.run("UPDATE drivers SET last_at=NULL WHERE id IN (?,?)", d1.id, d2.id);
  T.pingAs(t, "dana@example.test", 40.7045, -74.0);
  T.pingAs(t, "eli@example.test", 40.736, -74.0);
  const pick = { pickup: "Main St", pickup_lat: 40.70, pickup_lng: -74.00, dropoff: "Harbour", dropoff_lat: 40.75, dropoff_lng: -74.00 };

  /* ---------- estimates and the nearest driver ---------- */
  const e = T.estimate(t, { ...pick, vehicle_kind: "car" });
  ok(e.distance_km > 5 && e.distance_km < 8 && e.fare > 0 && e.duration_min > 0, "an estimate prices the road distance between the two points", e);
  const ep = T.estimate(t, { ...pick, vehicle_kind: "car", pool: true });
  ok(ep.pool && Math.abs(ep.fare - +(ep.full * 0.75).toFixed(2)) < 0.011, "a shared ride is quoted at the sharing discount", ep);
  ok(T.estimate(t, { pickup: "A", dropoff: "B" }).byTrip === true, "with no points on the map the fare is worked out from the trip");
  throws(() => T.request(t, null, pick), /Sign in/, "a ride is asked for by a signed-in rider");
  throws(() => T.request(t, ann, { ...pick, pickup_lat: 123 }), /latitude/, "a point off the globe is refused");
  const r1 = T.request(t, ann, { ...pick, vehicle_kind: "car" });
  ok(r1.driver && r1.driver.name === "Dana", "the nearest driver by their reported position is matched (not the higher-ranked further one)", r1.driver);
  ok(r1.status === states.first("ride", "assigned") && r1.label === "Driver on the way", "the rider sees the ride's state in words", [r1.status, r1.label]);
  code(() => T.request(t, ann, pick), "active_ride", "one ride under way per rider");

  /* ---------- the live track ---------- */
  T.pingAs(t, "dana@example.test", 40.7045, -74.0);
  ok(T.pingAs(t, "dana@example.test", 40.7046, -74.0).kept === false, "a position sooner than the minimum gap is not kept");
  db.run("UPDATE drivers SET last_at=? WHERE id=?", at(Date.now() - 60000), d1.id);
  T.pingAs(t, "dana@example.test", 40.701, -74.0);
  let v = T.riderView(t, ann, r1.id);
  ok(v.track && v.track.driver && v.track.eta_min >= 1 && v.track.points.length >= 1, "the rider sees the driver's live position, the track and the time to the pickup", v.track);
  code(() => T.advance(t, "eli@example.test", r1.id, "arrived"), 404, "another driver cannot move this ride");
  const steps = T.driverHome(t, "dana@example.test").active[0].next.map(m => m.to);
  ok(steps.length === 1 && !steps.some(s => states.is("ride", s, "failure")), "the driver is offered the ride's next step (cancelling is its own button)", steps);
  T.advance(t, "dana@example.test", r1.id, steps[0]);
  T.advance(t, "dana@example.test", r1.id, T.driverHome(t, "dana@example.test").active[0].next[0].to);
  /* the trip: four points north */
  db.run("UPDATE rides SET started_at=? WHERE id=?", at(Date.now() - 12 * 60000), r1.id);
  for (const [k, lat] of [40.71, 40.72, 40.735, 40.75].entries()) { db.run("UPDATE drivers SET last_at=? WHERE id=?", at(Date.now() - 60000), d1.id); T.pingAs(t, "dana@example.test", lat, -74.0); }
  T.advance(t, "dana@example.test", r1.id, T.driverHome(t, "dana@example.test").active[0].next[0].to);
  const done = db.get("SELECT * FROM rides WHERE id=?", r1.id);
  ok(states.is("ride", done.status, "success") && done.distance_km > 4.5 && done.distance_km < 6 && done.duration_min >= 11, "a finished trip's distance and time come from its track", [done.distance_km, done.duration_min]);
  const takePct = caps.cap(t, "ride_hailing").platform_take_rate_pct;
  ok(done.fare > 0 && Math.abs(done.take - +(done.fare * takePct / 100).toFixed(2)) < 0.011, "the platform's share of the fare is kept on the ride", [done.fare, done.take]);
  ok(states.is("driver", db.get("SELECT status FROM drivers WHERE id=?", d1.id).status, "available"), "the driver is free again");

  /* ---------- ratings both ways ---------- */
  throws(() => T.rate(t, r1.id, { by: "rider", stars: 6 }), /1 to 5/, "stars are 1 to 5");
  const g = T.rate(t, r1.id, { by: "rider", stars: 5, tags: ["Safe driving", "made up"], comment: "Great" });
  ok(g.rider.stars === 5 && g.rider.tags.length === 1 && g.rider.tags[0] === "Safe driving", "a rider rates the driver; only the offered tags are kept", g.rider);
  code(() => T.rate(t, r1.id, { by: "rider", stars: 1 }), "rated", "a ride is rated once by each side");
  T.rateByDriver(t, "dana@example.test", r1.id, { stars: 4, tags: ["Polite"] });
  ok(T.riderRating(t, ann).stars === 4, "a driver rates the rider; the rider's rating comes from their drivers");
  ok(db.get("SELECT rating, rating_count FROM drivers WHERE id=?", d1.id).rating_count === 1, "the driver's rating counts their ratings");
  /* the review floor: five poor ratings hold a driver out of dispatch */
  const fake = () => { const id = Number(db.run("INSERT INTO rides(tenant_id,ref,rider,pickup,dropoff,driver_id,status,completed_at,user_id) VALUES(?,?,?,?,?,?,?,?,?)", t, "RIDE-F-" + Math.random().toString(36).slice(2), "X", "A", "B", d2.id, states.first("ride", "success"), at(Date.now()), bob).lastInsertRowid); return id; };
  for (let k = 0; k < 5; k++) T.rate(t, fake(), { by: "rider", stars: 3 });
  const eli = db.get("SELECT rating, review FROM drivers WHERE id=?", d2.id);
  ok(eli.rating === 3 && eli.review === 1, "a driver whose recent average falls below the floor is held for review", eli);
  ok(T.overview(t).review.some(x => x.id === d2.id), "the store sees who is held for review");
  db.run("UPDATE rides SET completed_at=? WHERE id=?", at(Date.now() - 10 * 86400000), fake());
  code(() => T.rate(t, db.get("SELECT MAX(id) m FROM rides").m, { by: "rider", stars: 5 }), 409, "a ride is rated only within the window after it");

  /* ---------- tips ---------- */
  throws(() => T.tip(t, bob, r1.id, 2), /No such ride/, "a tip is the rider's own");
  throws(() => T.tip(t, ann, r1.id, 9999), /at most/, "a tip is at most the largest the store allows");
  const tipped = T.tip(t, ann, r1.id, 5);
  ok(tipped.tip === 5 && tipped.can.tip === false, "a rider tips once on a finished ride");

  /* ---------- the held driver is not matched; the free one is ---------- */
  /* Dana is back near the pickup (a driver beyond the match radius is not matched) */
  db.run("UPDATE drivers SET last_at=? WHERE id=?", at(Date.now() - 60000), d1.id); T.pingAs(t, "dana@example.test", 40.703, -74.0);
  db.run("UPDATE drivers SET last_at=? WHERE id=?", at(Date.now() - 60000), d2.id); T.pingAs(t, "eli@example.test", 40.7005, -74.0);
  const r2 = T.request(t, bob, { ...pick, vehicle_kind: "car" });
  ok(r2.driver && r2.driver.name === "Dana", "a driver held for review is not dispatched", r2.driver);
  T.cancelByRider(t, bob, r2.id);
  ok(states.is("ride", db.get("SELECT status FROM rides WHERE id=?", r2.id).status, "failure"), "a rider cancels before the trip starts");
  T.clearReview(t, d2.id);
  ok(db.get("SELECT review FROM drivers WHERE id=?", d2.id).review === 0, "the store lets a reviewed driver drive again");

  /* ---------- safety ---------- */
  const r3 = T.request(t, cy, { ...pick, vehicle_kind: "car" });
  const share = T.share(t, cy, r3.id);
  ok(share.token.length >= 30 && T.share(t, cy, r3.id).token === share.token, "a rider shares their trip with a private link (one link per ride)");
  const sv = T.sharedView(share.token);
  ok(sv.rider === "Cy" && sv.driver && sv.driver.plate && !JSON.stringify(sv).includes("example.test") && !("rider_phone" in sv), "the shared link shows the trip, the driver's first name and the car — no contact details", sv);
  code(() => T.sharedView("x".repeat(30)), 404, "a made-up link shows nothing");
  throws(() => T.raiseByRider(t, cy, r3.id, { kind: "fire" }), /Say what happened/, "a report is of a known kind");
  const sos = T.raiseByRider(t, cy, r3.id, { kind: "sos", lat: 40.7, lng: -74 });
  ok(sos.urgent && sos.emergency && sos.ref.startsWith("SAF-"), "the emergency button raises an urgent report and gives the local emergency number", sos);
  ok(T.overview(t).safety[0].id === sos.id && T.overview(t).safety[0].unhandled, "the store sees the open emergency first");
  T.acknowledge(t, sos.id, "ops@example.test");
  code(() => T.acknowledge(t, sos.id, "ops2@example.test"), 409, "an emergency is taken by one person");
  throws(() => T.resolve(t, sos.id, "ops@example.test", ""), /how it was resolved/, "resolving says how");
  ok(T.resolve(t, sos.id, "ops@example.test", "Called the rider; all fine").status === states.first("ride_safety", "resolved"), "the store resolves it");
  throws(() => T.raiseByDriver(t, db.get("SELECT * FROM drivers WHERE tenant_id=? AND email LIKE '%example.test' AND id<>?", t, db.get("SELECT driver_id FROM rides WHERE id=?", r3.id).driver_id), r3.id, { kind: "incident", note: "x" }), /No such ride/, "a driver reports only on their own rides");
  throws(() => T.raiseByRider(t, cy, r3.id, { kind: "incident" }), /what happened/, "an incident says what happened");
  T.cancelByRider(t, cy, r3.id);

  /* ---------- shared rides ---------- */
  T.goOnline(t, "eli@example.test", false);
  const p1 = T.request(t, ann, { ...pick, vehicle_kind: "car", pool: true });
  const p2 = T.request(t, bob, { pickup: "Near Main", pickup_lat: 40.705, pickup_lng: -74.003, dropoff: "Near Harbour", dropoff_lat: 40.752, dropoff_lng: -74.002, vehicle_kind: "car", pool: true });
  const far = T.request(t, cy, { pickup: "Uptown", pickup_lat: 40.80, pickup_lng: -73.95, dropoff: "Airport", dropoff_lat: 40.64, dropoff_lng: -73.78, vehicle_kind: "car", pool: true });
  const pr = id => db.get("SELECT * FROM rides WHERE id=?", id);
  ok(pr(p1.id).pool_id && pr(p1.id).pool_id === pr(p2.id).pool_id, "a rider going the same way joins the shared ride");
  ok(pr(far.id).pool_id !== pr(p1.id).pool_id, "a rider going elsewhere gets a shared ride of their own");
  ok(pr(p2.id).driver_id === pr(p1.id).driver_id && p2.pool.riders === 2, "the riders of a shared ride have the same driver", [pr(p1.id).driver_id, pr(p2.id).driver_id]);
  throws(() => T.request(t, ann, { pickup: "A", dropoff: "B", pool: true, vehicle_kind: "car" }), /already have a ride/, "still one ride under way per rider");
  /* the driver picks up both and drops each */
  const dana = () => T.driverHome(t, "dana@example.test");
  ok(dana().active.length === 2, "the driver sees both riders of the shared ride");
  for (const id of [p1.id, p2.id]) { T.advance(t, "dana@example.test", id, dana().active.find(x => x.id === id).next[0].to); T.advance(t, "dana@example.test", id, dana().active.find(x => x.id === id).next[0].to); }
  ok(states.is("ride_pool", db.get("SELECT status FROM ride_pools WHERE id=?", pr(p1.id).pool_id).status, "terminal"), "once someone is on board, nobody else joins");
  T.advance(t, "dana@example.test", p1.id, dana().active.find(x => x.id === p1.id).next[0].to);
  ok(states.is("driver", db.get("SELECT status FROM drivers WHERE id=?", d1.id).status, "engaged"), "the driver stays busy while a rider of the shared ride is still on board");
  T.advance(t, "dana@example.test", p2.id, dana().active.find(x => x.id === p2.id).next[0].to);
  ok(states.is("driver", db.get("SELECT status FROM drivers WHERE id=?", d1.id).status, "available"), "and is free once the last one is dropped");
  const f1 = pr(p1.id), full = mob.computeFare(t, f1.distance_km, f1.duration_min, f1.surge).fare;
  ok(Math.abs(f1.fare - +(full * 0.75).toFixed(2)) < 0.011, "a shared rider pays the discounted fare", [f1.fare, full]);
  T.cancelByRider(t, cy, far.id);

  /* ---------- rides booked for later ---------- */
  throws(() => T.schedule(t, ann, { ...pick, pickup_at: new Date(Date.now() + 5 * 60000).toISOString() }), /at least/, "a booking is far enough ahead");
  throws(() => T.schedule(t, ann, { ...pick, pickup_at: new Date(Date.now() + 90 * 86400000).toISOString() }), /days ahead/, "and not too far");
  const b1 = T.schedule(t, ann, { ...pick, vehicle_kind: "car", pickup_at: new Date(Date.now() + 2 * 3600000).toISOString() });
  ok(b1.ref.startsWith("RS-") && b1.estimate > 0 && states.is("ride_schedule", b1.status, "waiting"), "a rider books a ride for later, with an estimate", b1);
  ok(T.sweep(t).due === 0, "a booking is not dispatched before its time");
  db.run("UPDATE ride_schedules SET pickup_at=? WHERE id=?", at(Date.now() + 10 * 60000), b1.id);
  ok(T.sweep(t).due === 1, "within the lead time the booking is dispatched as a ride");
  const b1r = db.get("SELECT * FROM ride_schedules WHERE id=?", b1.id);
  ok(states.is("ride_schedule", b1r.status, "dispatched") && pr(b1r.ride_id).user_id === ann && pr(b1r.ride_id).driver_id, "it becomes the rider's ride, with a driver", b1r);
  code(() => T.cancelSchedule(t, b1.id, ann), 409, "a dispatched booking is cancelled as a ride");
  T.cancelByRider(t, ann, b1r.ride_id);
  const b2 = T.schedule(t, bob, { ...pick, pickup_at: new Date(Date.now() + 3 * 3600000).toISOString() });
  code(() => T.cancelSchedule(t, b2.id, ann), 404, "only the rider's own booking");
  ok(states.is("ride_schedule", T.cancelSchedule(t, b2.id, bob).status, "cancelled"), "a waiting booking is cancelled free");
  const b3 = T.schedule(t, bob, { ...pick, pickup_at: new Date(Date.now() + 3 * 3600000).toISOString() });
  db.run("UPDATE ride_schedules SET pickup_at=? WHERE id=?", at(Date.now() - 2 * 3600000), b3.id);
  T.sweep(t);
  ok(states.is("ride_schedule", db.get("SELECT status FROM ride_schedules WHERE id=?", b3.id).status, "missed"), "a booking the platform could not reach in time is marked missed, not sent late");

  /* ---------- waiting rides get a driver when one is free ---------- */
  T.goOnline(t, "dana@example.test", false);
  const w1 = T.request(t, cy, { ...pick, vehicle_kind: "car" });
  ok(!w1.driver, "with nobody online the ride waits");
  T.goOnline(t, "eli@example.test", true);
  ok(pr(w1.id).driver_id === d2.id, "a driver coming online takes the waiting ride");
  ok(T.driverHome(t, "eli@example.test").active[0].canCancel, "the driver may cancel a ride they have accepted");
  T.advance(t, "eli@example.test", w1.id, states.first("ride", "failure"));
  ok(states.is("ride", pr(w1.id).status, "failure"), "a driver cancels a ride");

  /* ---------- earnings and payouts ---------- */
  const st = T.statementAs(t, "dana@example.test");
  const net = st.trips.find(x => x.ref === done.ref);
  ok(net && net.tip === 5 && Math.abs(net.net - (done.fare - done.take + 5)) < 0.011, "the driver's statement shows each trip's fare, the platform's share, the tip and what they keep", net);
  ok(st.unpaid.trips === st.trips.length && st.unpaid.net === st.totals.net, "nothing is paid yet");
  const today = at(Date.now()).slice(0, 10);
  const po = T.createPayout(t, { driver_id: d1.id, through: today }, "fin@example.test");
  ok(po.ref.startsWith("DPO-") && po.trips === st.trips.length && Math.abs(po.net - st.totals.net) < 0.011 && po.editable, "a payout takes every unpaid trip up to the day", po);
  code(() => T.createPayout(t, { driver_id: d1.id, through: today }, "fin@example.test"), "nothing_due", "a trip is paid once");
  code(() => T.approvePayout(t, po.id, "fin@example.test"), "own_payout", "whoever made a payout does not approve it");
  const tb = () => require("../lib/books.js").trialBalance(t, {}).flatMap(c => c.rows);
  const bal = c => (tb().find(r => r.account === c) || { balance: 0 }).balance;
  T.approvePayout(t, po.id, "boss@example.test");
  ok(Math.abs(bal("2150") - po.net) < 0.011 && Math.abs(bal("5200") - po.net) < 0.011, "approval puts the driver's earnings on the books as owed to them", [bal("2150"), bal("5200")]);
  T.payPayout(t, po.id, "BANK-1");
  ok(Math.abs(bal("2150")) < 0.011, "paying clears what is owed to the driver from the bank");
  ok(T.statementAs(t, "dana@example.test").unpaid.trips === 0, "the statement shows the trips as paid");
  code(() => T.tip(t, ann, p1.id, 2), 409, "a trip already paid out takes no tip");
  /* a void releases trips */
  const eliSt = T.statement(t, d2.id);
  if (eliSt.unpaid.trips) {
    const po2 = T.createPayout(t, { driver_id: d2.id, through: today }, "fin@example.test");
    T.voidPayout(t, po2.id);
    ok(T.statement(t, d2.id).unpaid.trips === eliSt.unpaid.trips, "a voided payout frees its trips to be paid again");
  } else ok(true, "a voided payout frees its trips to be paid again (no unpaid trips)");
  code(() => T.voidPayout(t, po.id), 409, "a paid payout stays paid");
  ok(T.overview(t).payouts.length >= 1 && Array.isArray(T.overview(t).unpaid), "the store sees payouts and what each driver is owed");

  /* ---------- places ---------- */
  throws(() => T.setPlaces(t, [{ name: "Airport", lat: 999, lng: 0 }]), /latitude/, "a place is on the map");
  ok(T.setPlaces(t, [{ name: "Airport", lat: 40.64, lng: -73.78 }]).length === 1 && T.mine(t, ann).places[0].name === "Airport", "the store names places riders pick from");

  /* ---------- the rider's page ---------- */
  const m = T.mine(t, ann);
  ok(m.past.length >= 2 && m.bookings.length >= 1 && m.ratings.riderTags.length && m.safety.emergency, "the rider's page has past rides, bookings, rating tags and the emergency number");
  ok(!JSON.stringify(m).includes("dana@example.test"), "a rider never sees a driver's email");
  throws(() => T.driverHome(t, "ann@example.test"), /not a driver/, "only a driver opens the driver's page");

  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.log("ERR", e.message, e.stack); process.exit(1); });
