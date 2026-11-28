/* LUXORA Platform — mobility domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the mobility domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "mobility", routes(kit) {
  const { T, actor, bad, get, json, logAction, mobOn, mobility, notify, publicLink, requireAdmin, signedIn } = kit;
  const TR = () => require("../trips.js");
  /* trips (lib/trips.js): the engine's refusals carry their status; anything else is a bad request */
  const call = async (res, fn) => { try { json(res, 200, await fn()); } catch (e) { bad(res, e.message, e.status || 400); } };
  const staff = (s, res, fn) => { if (requireAdmin(s, res)) return call(res, fn); };
  const rider = (s, res, fn) => { if (signedIn(s, res, "ride")) return call(res, fn); };
  const q = (url, k) => url.searchParams.get(k) || "";
  const B = b => b || {};
  /* who is acting, by their email: a payout is not approved by whoever made it */
  const who = s => { const a = actor(s); return Array.isArray(a) ? String(a[2] || a[1] || "") : String(a || ""); };
  /* a driver is a signed-in person whose email the store's fleet holds */
  const emailOf = s => ((s.user_id && get("SELECT email FROM users WHERE id=? AND tenant_id=?", s.user_id, T(s))) || {}).email || "";
  /* an emergency reaches the store's notifiers at once, with where it was raised */
  const alarm = (s, e) => { if (e.urgent) try { notify(T(s), "Emergency on ride " + e.ride, `${e.label} raised by the ${e.by_role} (${e.by_who || "unknown"}) on ride ${e.ride}` + (e.lat != null ? ` at ${e.lat}, ${e.lng}` : "") + `. Report ${e.ref}.`); } catch (x) { } return e; };

  function apiMobilityGet(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    if (!mobOn(s, "ride_hailing")) return bad(res, "Ride hailing is not enabled for this store", 403);
    json(res, 200, {
      rides: mobility.listRides(T(s), {
        status: url.searchParams.get("status") || "",
        driver_id: url.searchParams.get("driver_id") || "",
        q: url.searchParams.get("q") || ""
      }),
      drivers: mobility.listDrivers(T(s), {
        status: url.searchParams.get("dstatus") || "",
        vehicle_kind: url.searchParams.get("kind") || ""
      }),
      zones: mobility.listZones(T(s)),
      vehicles: mobility.listVehicles(T(s)),
      stats: mobility.summary(T(s)),
      statuses: require("../states.js").vocab("ride"), vehicleKinds: mobility.vehicleKinds()
    });
  }
  function apiMobilityRide(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    if (!mobOn(s, "ride_hailing")) return bad(res, "Ride hailing is not enabled for this store", 403);
    try {
      const r = mobility.requestRide(T(s), body.rider, body.rider_phone, body.pickup, body.dropoff,
        body.vehicle_kind, body.payment_method, body.pickup_lat != null ? Number(body.pickup_lat) : null,
        body.pickup_lng != null ? Number(body.pickup_lng) : null);
      logAction(s, "mobility.ride.request", "ride", r.id, { ref: r.ref });
      json(res, 200, { ride: r });
    } catch (e) { bad(res, e.message, 400); }
  }
  function apiMobilityRideStatus(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    if (!mobOn(s, "ride_hailing")) return bad(res, "Ride hailing is not enabled for this store", 403);
    try {
      const r = mobility.updateRide(T(s), id, String(body.status || ""), body.note || "");
      logAction(s, "mobility.ride.status", "ride", id, { status: body.status });
      json(res, 200, { ride: r });
    } catch (e) { bad(res, e.message, 400); }
  }
  function apiMobilityRate(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    if (!mobOn(s, "ride_hailing")) return bad(res, "Ride hailing is not enabled for this store", 403);
    try {
      json(res, 200, mobility.rateRide(T(s), id, body.rating));
    } catch (e) { bad(res, e.message, 400); }
  }
  function apiMobilityDriver(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    if (!mobOn(s, "fleet_management")) return bad(res, "Fleet management is not enabled for this store", 403);
    try {
      const d = mobility.upsertDriver(T(s), body);
      logAction(s, "mobility.driver.save", "driver", d.id, { name: d.name });
      json(res, 200, { driver: d });
    } catch (e) { bad(res, e.message, 400); }
  }
  function apiMobilityDriverToggle(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    if (!mobOn(s, "fleet_management")) return bad(res, "Fleet management is not enabled for this store", 403);
    try {
      json(res, 200, { driver: mobility.toggleDriver(T(s), id, body.online !== false && body.online !== 0) });
    } catch (e) { bad(res, e.message, 400); }
  }
  function apiMobilityDriverDeactivate(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    if (!mobOn(s, "fleet_management")) return bad(res, "Fleet management is not enabled for this store", 403);
    try {
      logAction(s, "mobility.driver.deactivate", "driver", id, {});
      json(res, 200, mobility.deactivateDriver(T(s), id));
    } catch (e) { bad(res, e.message, 400); }
  }
  function apiMobilityVehicle(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    if (!mobOn(s, "fleet_management")) return bad(res, "Fleet management is not enabled for this store", 403);
    try {
      const v = mobility.upsertVehicle(T(s), body);
      logAction(s, "mobility.vehicle.save", "vehicle", v.id, { plate: v.plate });
      json(res, 200, { vehicle: v });
    } catch (e) { bad(res, e.message, 400); }
  }
  function apiMobilityZone(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    if (!mobOn(s, "dynamic_pricing")) return bad(res, "Dynamic pricing is not enabled for this store", 403);
    try {
      const z = mobility.upsertZone(T(s), body);
      logAction(s, "mobility.zone.save", "surge_zone", z.id, { name: z.name });
      json(res, 200, { zone: z });
    } catch (e) { bad(res, e.message, 400); }
  }

  /* ---------- trips: the store console (section trips) ---------- */
  /* Safety reports (open emergencies first), rides booked for later and waiting, shared rides forming, drivers held for review and recent ratings, what each driver is owed, payouts, the places riders pick from, the local emergency number and the policy. */
  function apiTrips(req, res, url, s) { return staff(s, res, () => TR().overview(T(s))); }
  /* Takes an open emergency or report: whoever acknowledges it is handling it. */
  function apiTripSafetyAck(req, res, url, s, body, id) { return staff(s, res, () => { const e = TR().acknowledge(T(s), id, who(s)); logAction(s, "trips.safety.acknowledge", "ride_safety_event", e.ref, {}); return { report: e }; }); }
  /* Closes a report with its `outcome`. */
  function apiTripSafetyResolve(req, res, url, s, body, id) { return staff(s, res, () => { const e = TR().resolve(T(s), id, who(s), B(body).outcome); logAction(s, "trips.safety.resolve", "ride_safety_event", e.ref, {}); return { report: e }; }); }
  /* Lets a driver held for review drive again. */
  function apiTripDriverClear(req, res, url, s, body, id) { return staff(s, res, () => { const d = TR().clearReview(T(s), id); logAction(s, "trips.driver.clear_review", "driver", d.id, {}); return { driver: d }; }); }
  /* A driver's earnings statement: each trip's fare, the platform's share, the tip and what they keep, between `from` and `to` (days). */
  function apiTripDriverStatement(req, res, url, s, body, id) { return staff(s, res, () => ({ statement: TR().statement(T(s), id, q(url, "from"), q(url, "to")), payouts: TR().payouts(T(s), { driver_id: id }) })); }
  /* Cancels a ride a rider booked for later that is still waiting. */
  function apiTripBookingCancel(req, res, url, s, body, id) { return staff(s, res, () => { const b = TR().cancelSchedule(T(s), id); logAction(s, "trips.booking.cancel", "ride_schedule", b.ref, {}); return { booking: b }; }); }
  /* Dispatches bookings that are due and gives waiting rides a driver, now. */
  function apiTripSweep(req, res, url, s) { return staff(s, res, () => TR().sweep(T(s))); }
  /* Replaces the places riders pick from: `places` `[{ name, lat, lng }]`. */
  function apiTripPlaces(req, res, url, s, body) { return staff(s, res, () => { const p = TR().setPlaces(T(s), B(body).places); logAction(s, "trips.places", "settings", "trips", { places: p.length }); return { places: p }; }); }
  /* Payouts, newest first; `driver_id` and `status` narrow them. */
  function apiTripPayouts(req, res, url, s) { return staff(s, res, () => ({ payouts: TR().payouts(T(s), { driver_id: q(url, "driver_id"), status: q(url, "status") }), unpaid: TR().unpaid(T(s)) })); }
  /* Makes a payout of everything a driver (`driver_id`) earned up to `through` (a day; yesterday when not given) that no payout has taken. */
  function apiTripPayoutCreate(req, res, url, s, body) { return staff(s, res, () => { const p = TR().createPayout(T(s), B(body), who(s)); logAction(s, "trips.payout.create", "driver_payout", p.ref, { net: p.net }); return { payout: p }; }); }
  /* One payout and the trips it pays. */
  function apiTripPayout(req, res, url, s, body, id) { return staff(s, res, () => ({ payout: TR().payout(T(s), id) })); }
  /* Approves a pending payout — not by whoever made it: the books owe it to the driver. */
  function apiTripPayoutApprove(req, res, url, s, body, id) { return staff(s, res, () => { const p = TR().approvePayout(T(s), id, who(s)); logAction(s, "trips.payout.approve", "driver_payout", p.ref, { net: p.net }); return { payout: p }; }); }
  /* Records an approved payout as paid (`pay_ref`, the bank's reference): the books pay it from the bank. */
  function apiTripPayoutPay(req, res, url, s, body, id) { return staff(s, res, () => { const p = TR().payPayout(T(s), id, B(body).pay_ref); logAction(s, "trips.payout.pay", "driver_payout", p.ref, { net: p.net }); return { payout: p }; }); }
  /* Voids a payout not yet paid: its trips are free to be paid again. */
  function apiTripPayoutVoid(req, res, url, s, body, id) { return staff(s, res, () => { const p = TR().voidPayout(T(s), id); logAction(s, "trips.payout.void", "driver_payout", p.ref, {}); return { payout: p }; }); }

  /* ---------- the rider (signed in) ---------- */
  /* The rider's rides under way (with the driver's live position), rides booked for later, past rides, their rating, the vehicle kinds, shared-ride kinds and discount, the store's places, rating tags, tips offered and the emergency number. */
  function apiRides(req, res, url, s) { return rider(s, res, () => { TR().sweep(T(s)); return TR().mine(T(s), s.user_id); }); }
  /* What a ride would cost: `pickup_lat`, `pickup_lng`, `dropoff_lat`, `dropoff_lng`, `vehicle_kind`, `pool`. */
  function apiRideEstimate(req, res, url, s, body) { return call(res, () => ({ estimate: TR().estimate(T(s), B(body)) })); }
  /* Asks for a ride now: `pickup`, `dropoff` (words), their `_lat`/`_lng`, `vehicle_kind`, `seats`, `payment_method`, `rider_phone`; `pool: true` shares it with riders going the same way. */
  function apiRideRequest(req, res, url, s, body) { return rider(s, res, () => { const r = TR().request(T(s), s.user_id, B(body)); logAction(s, "trips.ride.request", "ride", r.id, { ref: r.ref, pool: !!r.pool }); return { ride: r }; }); }
  /* Books a ride for later: as asking for one now, with `pickup_at` (a time). */
  function apiRideBook(req, res, url, s, body) { return rider(s, res, () => ({ booking: TR().schedule(T(s), s.user_id, B(body)) })); }
  /* Cancels the rider's booking while it is still waiting. */
  function apiRideBookCancel(req, res, url, s, body, id) { return rider(s, res, () => ({ booking: TR().cancelSchedule(T(s), id, s.user_id) })); }
  /* One of the rider's rides: its state, driver and car, the live position and track, ratings, and what may be done now. */
  function apiRideGet(req, res, url, s, body, id) { return rider(s, res, () => ({ ride: TR().riderView(T(s), s.user_id, id) })); }
  /* Cancels the rider's ride before the trip starts; a cancellation fee applies once a driver has accepted. */
  function apiRideCancel(req, res, url, s, body, id) { return rider(s, res, () => ({ ride: TR().cancelByRider(T(s), s.user_id, id) })); }
  /* Rates the driver of a finished ride: `stars` 1–5, `tags`, `comment`. */
  function apiRideRate(req, res, url, s, body, id) { return rider(s, res, () => { TR().riderView(T(s), s.user_id, id); TR().rate(T(s), id, { ...B(body), by: "rider" }); return { ride: TR().riderView(T(s), s.user_id, id) }; }); }
  /* Tips the driver of a finished ride: `amount`. */
  function apiRideTip(req, res, url, s, body, id) { return rider(s, res, () => ({ ride: TR().tip(T(s), s.user_id, id, B(body).amount) })); }
  /* A private link to the ride's progress for the rider to send to someone. */
  function apiRideShare(req, res, url, s, body, id) { return rider(s, res, () => { const { token } = TR().share(T(s), s.user_id, id); return { token, link: publicLink(req, s, "trip.html", { t: token }) || "trip.html?t=" + token }; }); }
  /* Raises an emergency (`kind: "sos"`) or reports an incident or a lost item (`kind`, `note`) on the rider's ride, with where they are (`lat`, `lng`); an emergency alerts the store at once. */
  function apiRideSafety(req, res, url, s, body, id) { return rider(s, res, () => { const e = alarm(s, TR().raiseByRider(T(s), s.user_id, id, B(body))); logAction(s, "trips.safety.raise", "ride_safety_event", e.ref, { kind: e.kind }); return { report: e }; }); }

  /* ---------- the driver (signed in with the email the fleet holds) ---------- */
  /* The driver's state, rating, rides under way (riders' first names and ratings, the next step), recent rides, today's earnings, rating tags and the emergency number. */
  function apiDrive(req, res, url, s) { return rider(s, res, () => { TR().sweep(T(s)); return TR().driverHome(T(s), emailOf(s)); }); }
  /* Goes online (`online: true`) — and takes a ride that is waiting — or offline. */
  function apiDriveOnline(req, res, url, s, body) { return rider(s, res, () => TR().goOnline(T(s), emailOf(s), B(body).online !== false)); }
  /* Reports where the driver is: `lat`, `lng`. */
  function apiDrivePosition(req, res, url, s, body) { return rider(s, res, () => TR().pingAs(T(s), emailOf(s), B(body).lat, B(body).lng)); }
  /* Moves the driver's ride to its next step (`to`), or cancels it. */
  function apiDriveMove(req, res, url, s, body, id) { return rider(s, res, () => TR().advance(T(s), emailOf(s), id, B(body).to)); }
  /* Rates the rider of a finished ride: `stars`, `tags`, `comment`. */
  function apiDriveRate(req, res, url, s, body, id) { return rider(s, res, () => TR().rateByDriver(T(s), emailOf(s), id, B(body))); }
  /* Raises an emergency or reports an incident on the driver's ride; an emergency alerts the store at once. */
  function apiDriveSafety(req, res, url, s, body, id) { return rider(s, res, () => { const T_ = T(s), d = TR().driverOf(T_, emailOf(s)); if (!d) throw Object.assign(new Error("You are not a driver for this store"), { status: 403 }); const e = alarm(s, TR().raiseByDriver(T_, d, id, B(body))); logAction(s, "trips.safety.raise", "ride_safety_event", e.ref, { kind: e.kind }); return { report: e }; }); }
  /* The driver's earnings statement between `from` and `to` (days), and their payouts. */
  function apiDriveEarnings(req, res, url, s) { return rider(s, res, () => TR().statementAs(T(s), emailOf(s), q(url, "from"), q(url, "to"))); }

  /* ---------- a shared trip, from its private link (no sign-in) ---------- */
  /* The ride's progress, the driver's first name, the car and the live position, for whoever the rider sent the link to; closed a while after the ride. */
  function apiTripShared(req, res, url) { return call(res, () => ({ trip: TR().sharedView(q(url, "t")) })); }

  return [
    ["GET /api/admin/mobility", apiMobilityGet],
    ["POST /api/admin/mobility/rides", apiMobilityRide],
    ["PUT /api/admin/mobility/rides/:id", (r, re, u, s, b, p) => apiMobilityRideStatus(r, re, u, s, b, p)],
    ["POST /api/admin/mobility/rides/:id/rate", (r, re, u, s, b, p) => apiMobilityRate(r, re, u, s, b, p)],
    ["POST /api/admin/mobility/drivers", apiMobilityDriver],
    ["POST /api/admin/mobility/drivers/:id/toggle", (r, re, u, s, b, p) => apiMobilityDriverToggle(r, re, u, s, b, p)],
    ["POST /api/admin/mobility/drivers/:id/deactivate", (r, re, u, s, b, p) => apiMobilityDriverDeactivate(r, re, u, s, b, p)],
    ["POST /api/admin/mobility/vehicles", apiMobilityVehicle],
    ["POST /api/admin/mobility/zones", apiMobilityZone],
    ["GET /api/admin/trips", apiTrips],
    ["POST /api/admin/trips/safety/:id/acknowledge", (r, re, u, s, b, p) => apiTripSafetyAck(r, re, u, s, b, p)],
    ["POST /api/admin/trips/safety/:id/resolve", (r, re, u, s, b, p) => apiTripSafetyResolve(r, re, u, s, b, p)],
    ["POST /api/admin/trips/drivers/:id/clear-review", (r, re, u, s, b, p) => apiTripDriverClear(r, re, u, s, b, p)],
    ["GET /api/admin/trips/drivers/:id/statement", (r, re, u, s, b, p) => apiTripDriverStatement(r, re, u, s, b, p)],
    ["POST /api/admin/trips/bookings/:id/cancel", (r, re, u, s, b, p) => apiTripBookingCancel(r, re, u, s, b, p)],
    ["POST /api/admin/trips/sweep", apiTripSweep],
    ["PUT /api/admin/trips/places", apiTripPlaces],
    ["GET /api/admin/trips/payouts", apiTripPayouts],
    ["POST /api/admin/trips/payouts", apiTripPayoutCreate],
    ["GET /api/admin/trips/payouts/:id", (r, re, u, s, b, p) => apiTripPayout(r, re, u, s, b, p)],
    ["POST /api/admin/trips/payouts/:id/approve", (r, re, u, s, b, p) => apiTripPayoutApprove(r, re, u, s, b, p)],
    ["POST /api/admin/trips/payouts/:id/pay", (r, re, u, s, b, p) => apiTripPayoutPay(r, re, u, s, b, p)],
    ["POST /api/admin/trips/payouts/:id/void", (r, re, u, s, b, p) => apiTripPayoutVoid(r, re, u, s, b, p)],
    ["GET /api/rides", apiRides],
    ["POST /api/rides/estimate", apiRideEstimate],
    ["POST /api/rides", apiRideRequest],
    ["POST /api/rides/bookings", apiRideBook],
    ["POST /api/rides/bookings/:id/cancel", (r, re, u, s, b, p) => apiRideBookCancel(r, re, u, s, b, p)],
    ["GET /api/rides/:id", (r, re, u, s, b, p) => apiRideGet(r, re, u, s, b, p)],
    ["POST /api/rides/:id/cancel", (r, re, u, s, b, p) => apiRideCancel(r, re, u, s, b, p)],
    ["POST /api/rides/:id/rate", (r, re, u, s, b, p) => apiRideRate(r, re, u, s, b, p)],
    ["POST /api/rides/:id/tip", (r, re, u, s, b, p) => apiRideTip(r, re, u, s, b, p)],
    ["POST /api/rides/:id/share", (r, re, u, s, b, p) => apiRideShare(r, re, u, s, b, p)],
    ["POST /api/rides/:id/safety", (r, re, u, s, b, p) => apiRideSafety(r, re, u, s, b, p)],
    ["GET /api/drive", apiDrive],
    ["POST /api/drive/online", apiDriveOnline],
    ["POST /api/drive/position", apiDrivePosition],
    ["POST /api/drive/rides/:id/move", (r, re, u, s, b, p) => apiDriveMove(r, re, u, s, b, p)],
    ["POST /api/drive/rides/:id/rate", (r, re, u, s, b, p) => apiDriveRate(r, re, u, s, b, p)],
    ["POST /api/drive/rides/:id/safety", (r, re, u, s, b, p) => apiDriveSafety(r, re, u, s, b, p)],
    ["GET /api/drive/earnings", apiDriveEarnings],
    ["GET /api/trips/shared", apiTripShared]
  ];
} };
