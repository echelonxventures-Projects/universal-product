/* LUXORA Platform — mobility domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the mobility domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "mobility", routes(kit) {
  const { T, bad, json, logAction, mobOn, mobility, requireAdmin } = kit;

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

  return [
    ["GET /api/admin/mobility", apiMobilityGet],
    ["POST /api/admin/mobility/rides", apiMobilityRide],
    ["PUT /api/admin/mobility/rides/:id", (r, re, u, s, b, p) => apiMobilityRideStatus(r, re, u, s, b, p)],
    ["POST /api/admin/mobility/rides/:id/rate", (r, re, u, s, b, p) => apiMobilityRate(r, re, u, s, b, p)],
    ["POST /api/admin/mobility/drivers", apiMobilityDriver],
    ["POST /api/admin/mobility/drivers/:id/toggle", (r, re, u, s, b, p) => apiMobilityDriverToggle(r, re, u, s, b, p)],
    ["POST /api/admin/mobility/drivers/:id/deactivate", (r, re, u, s, b, p) => apiMobilityDriverDeactivate(r, re, u, s, b, p)],
    ["POST /api/admin/mobility/vehicles", apiMobilityVehicle],
    ["POST /api/admin/mobility/zones", apiMobilityZone]
  ];
} };
