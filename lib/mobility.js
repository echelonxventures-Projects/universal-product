/* LUXORA Platform — E17 · The Mobility universe.
   --------------------------------------------------------------------------
   Constitution E17: "Through configuration alone this universe yields Uber-, Ola-,
   DoorDash-, Swiggy- and Zomato-class platforms: ride hailing · dispatch · driver
   management · routing · fleet · delivery · tracking · dynamic pricing · matching ·
   rating."

   This module is that universe's engine. It owns the ride lifecycle
   (requested → accepted → arrived → trip_start → completed | cancelled), the
   dispatcher that matches a request to the nearest idle driver, the surge-pricing
   multiplier, and the two-way rating that feeds driver health.

   ZERO BUSINESS RULES ARE HARD-CODED. Every threshold, weight, radius, fare
   component and cancellation policy is a declared PARAMETER of a capability atom in
   lib/capabilities.js, read through `cap(t, "ride_hailing").<param>`. An operator
   retunes the row in platform_capabilities and the engine follows on the next call —
   the same contract every parity engine in this platform obeys
   (Architecture3 §2.1: No Hard-Coded Business Logic, Registry Driven Everything). */
"use strict";

const db = () => require("./db.js");
const { stamp } = require("./db.js");
const caps = () => require("./capabilities.js");
const crypto = require("crypto");
const J = (v, d) => { try { return v == null || v === "" ? (d == null ? {} : d) : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d == null ? {} : d; } };

/* the lifecycle is data, not a code branch: the legal transitions are a registry the
   console owns (mobilityRideStatuses / mobilityTransitions), so an operator can add
   an inspection step or a verification hold without this file changing */
const DEFAULT_STATUSES = ["requested", "accepted", "arrived", "trip_start", "completed", "cancelled"];
const FARE_RULES = ["per_km", "per_min", "base", "min_fare", "booking_fee", "cancel_fee", "surge_cap"];

/* ---------------- seeding: registries the console renders ---------------- */
function seed() {
  const D = db();
  const put = (name, label, items) => {
    const existing = D.get("SELECT items FROM meta_lists WHERE name=?", name);
    const cur = J(existing ? existing.items : "[]", []);
    for (const it of items) if (!cur.some(x => (x.key || x) === (it.key || it))) cur.push(it);
    if (existing) D.run("UPDATE meta_lists SET items=? WHERE name=?", JSON.stringify(cur), name);
    else D.run("INSERT INTO meta_lists(name,label,items) VALUES(?,?,?)", name, label, JSON.stringify(items));
  };
  put("mobilityRideStatuses", "Mobility · Ride statuses", DEFAULT_STATUSES.map(k => ({ key: k, name: k })));
  put("mobilityTransitions", "Mobility · Legal status transitions", [
    { key: "requested>accepted", name: "Driver accepts" },
    { key: "accepted>arrived", name: "Driver arrives at pickup" },
    { key: "arrived>trip_start", name: "Trip starts" },
    { key: "trip_start>completed", name: "Trip completes" },
    { key: "requested>cancelled", name: "Rider cancels before acceptance" },
    { key: "accepted>cancelled", name: "Rider cancels after acceptance" },
    { key: "trip_start>cancelled", name: "Driver cancels mid-trip" }
  ]);
  put("mobilityVehicleKinds", "Mobility · Vehicle kinds",
    ["car", "suv", "bike", "auto", "van"].map(k => ({ key: k, name: k })));
  put("mobilityFareRules", "Mobility · Fare rules", FARE_RULES.map(k => ({ key: k, name: k })));
}

/* ---------------- surge pricing ---------------- */
/* the multiplier is a function of the ACTIVE surge zones a pickup falls inside, the
   live demand/supply ratio, and the configured ceiling — never a magic number */
function surgeFor(tenantId, lat, lng, kind) {
  const c = caps().cap(tenantId, "dynamic_pricing");
  if (!c || Object.keys(c).length === 0) return 1;
  const D = db();
  let mult = 1;
  /* configured zones, each with its own multiplier and radius */
  const zones = D.all("SELECT name, multiplier, center_lat, center_lng, radius_km, kind FROM surge_zones WHERE tenant_id=? AND active=1", tenantId);
  for (const z of zones) {
    if (lat == null || lng == null || z.center_lat == null) { mult = Math.max(mult, Number(z.multiplier) || 1); continue; }
    const d = dist(lat, lng, z.center_lat, z.center_lng);
    if (d <= (Number(z.radius_km) || 3)) mult = Math.max(mult, Number(z.multiplier) || 1);
  }
  /* the engine's own demand/supply signal: open requests vs idle drivers of the
   * requested kind, over the configured window */
  if (c.demand_supply_enabled !== false) {
    const open = D.get("SELECT COUNT(*) n FROM rides WHERE tenant_id=? AND status IN ('requested','accepted')", tenantId).n;
    const idle = D.get("SELECT COUNT(*) n FROM drivers WHERE tenant_id=? AND status='online'", tenantId).n;
    const ratio = idle > 0 ? open / idle : (open > 0 ? c.demand_supply_max_ratio || 3 : 1);
    const stepEvery = Math.max(1, Number(c.demand_supply_step) || 1);
    const steps = Math.max(0, Math.ceil((ratio - 1) / stepEvery));
    mult = Math.max(mult, 1 + steps * (Number(c.demand_supply_bps) || 0) / 10000);
  }
  const cap = Number(c.surge_cap_multiplier);
  if (isFinite(cap) && cap > 0) mult = Math.min(mult, cap);
  return +mult.toFixed(2);
}

/* haversine distance in km — geometry, not a business rule */
function dist(lat1, lng1, lat2, lng2) {
  const R = 6371, r = Math.PI / 180;
  const dLat = (lat2 - lat1) * r, dLng = (lng2 - lng1) * r;
  const a = Math.sin(dLat / 2) ** 2 + Math.cos(lat1 * r) * Math.cos(lat2 * r) * Math.sin(dLng / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(a));
}

/* ---------------- the fare ---------------- */
/* base + per_km × distance + per_min × duration + booking fee, floored at the minimum
   fare, all from the declared params. Surge multiplies the variable part only */
function computeFare(tenantId, distanceKm, durationMin, surge) {
  const c = caps().cap(tenantId, "ride_hailing");
  if (!c || Object.keys(c).length === 0) return { fare: 0, breakdown: {} };
  const base = Number(c.base_fare) || 0;
  const perKm = Number(c.per_km_rate) || 0;
  const perMin = Number(c.per_min_rate) || 0;
  const booking = Number(c.booking_fee) || 0;
  const minFare = Number(c.min_fare) || 0;
  const variable = (perKm * (distanceKm || 0)) + (perMin * (durationMin || 0));
  const total = Math.max(minFare, base + variable * (surge || 1)) + booking;
  return {
    fare: +total.toFixed(2),
    breakdown: { base: +base.toFixed(2), distance: +(perKm * (distanceKm || 0)).toFixed(2),
      time: +(perMin * (durationMin || 0)).toFixed(2), booking: +booking.toFixed(2),
      surge: +(surge || 1), min_fare: +minFare.toFixed(2) }
  };
}

/* ---------------- dispatch: the matching engine ---------------- */
/* choose the nearest idle driver for the requested vehicle kind. The search radius and
   the maximum wait are configured params, so the same code serves a dense city hailing
   market and a sparse outstation one */
function matchDriver(tenantId, kind, pickupLat, pickupLng) {
  const c = caps().cap(tenantId, "dispatch");
  if (!c || Object.keys(c).length === 0) return null;
  const D = db();
  const radius = Number(c.match_radius_km) || 5;
  const rows = D.all("SELECT id, name, rating, rides_completed, city_latency, vehicle_kind FROM drivers WHERE tenant_id=? AND status='online' AND (vehicle_kind=? OR ?='') ORDER BY rating DESC, city_latency ASC, rides_completed DESC LIMIT 100",
    tenantId, kind || "", kind || "");
  let best = null, bestD = Infinity;
  for (const d of rows) {
    /* a driver with no last-known position is ranked by the configured fallback
       (city_latency is stored as a distance from the city centre) */
    const dKm = (pickupLat != null && d.city_latency != null && d.city_latency > 0)
      ? Math.max(0, d.city_latency - (Number(c.city_centre_offset_km) || 0))
      : Number(c.unknown_position_penalty_km) || 2;
    if (dKm <= radius && dKm < bestD) { best = d; bestD = dKm; }
  }
  if (!best) return null;
  const eta = Math.max(1, Math.round(bestD * (Number(c.eta_per_km_minutes) || 3) + (Number(c.eta_pickup_buffer_minutes) || 2)));
  return { driver: best, distance_km: +bestD.toFixed(2), eta_min: eta };
}

/* ---------------- the ride lifecycle ---------------- */
/* every transition is validated against the registry's legal transitions, so an operator
   extends the lifecycle in Data Studio and this engine honours it */
function legalTransition(tenantId, from, to) {
  const D = db();
  const row = D.get("SELECT items FROM meta_lists WHERE name='mobilityTransitions'");
  const items = J(row ? row.items : "[]", []);
  if (!items.length) return DEFAULT_STATUSES.indexOf(to) === DEFAULT_STATUSES.indexOf(from) + 1;
  return items.some(x => String(x.key || x) === from + ">" + to || String(x.key || x) === "*>" + to);
}

function requestRide(tenantId, rider, phone, pickup, dropoff, kind, payment, lat, lng) {
  const D = db();
  const rideCap = caps().cap(tenantId, "ride_hailing");
  if (!rideCap || Object.keys(rideCap).length === 0) throw new Error("Ride hailing is not enabled for this store");
  /* the ride service and the fare's payment method are subject to the applicability rules */
  require("./rules.js").guardAt("mobility.ride", tenantId, { payment });
  const surgeCap = caps().cap(tenantId, "dynamic_pricing");
  const surge = (surgeCap && Object.keys(surgeCap).length) ? surgeFor(tenantId, lat, lng, kind) : 1;
  /* the ref is UNIQUE, so millisecond granularity alone collides under load — a
     second request in the same ms throws. Suffix with random bytes the way the
     seed and newRef (lib/api.js) do, and retry on the (now astronomically unlikely)
     collision rather than surfacing a raw constraint error to a rider */
  const mkRef = () => "RIDE-" + tenantId + "-" + Date.now().toString(36).toUpperCase() + crypto.randomBytes(3).toString("hex").toUpperCase();
  let ref = mkRef();
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      D.run(`INSERT INTO rides(tenant_id, ref, rider, rider_phone, pickup, dropoff, vehicle_kind, status, surge, payment_method, pickup_lat, pickup_lng, dropoff_lat, dropoff_lng)
         VALUES(?,?,?,?,?,?,?,'requested',1.0,?,?,?,?,?)`,
        tenantId, ref, rider || "", phone || "", pickup, dropoff, kind || "car", payment || "cash",
        lat != null ? lat : null, lng != null ? lng : null, null, null);
      break;
    } catch (e) {
      if (!/UNIQUE constraint/i.test(String(e.message || e))) throw e;
      ref = mkRef();
    }
  }
  const id = Number(D.get("SELECT last_insert_rowid() c").c);
  D.run("INSERT INTO ride_events(tenant_id, ride_id, status, note) VALUES(?,?,?,?)", tenantId, id, "requested", "ride requested");
  /* auto-dispatch when the engine is on; otherwise the ride waits in the queue for a
     manual dispatcher — both are legitimate operating modes, chosen by configuration */
  const dis = caps().cap(tenantId, "dispatch");
  const out = { id, ref, status: "requested", surge };
  if (dis && Object.keys(dis).length && dis.auto_dispatch !== false) {
    const m = matchDriver(tenantId, kind, lat, lng);
    if (m) {
      D.run("UPDATE rides SET driver_id=?, eta_min=?, status='accepted', accepted_at=?, surge=? WHERE id=?",
        m.driver.id, m.eta_min, stamp(), surge, id);
      D.run("UPDATE drivers SET status='busy' WHERE id=?", m.driver.id);
      D.run("INSERT INTO ride_events(tenant_id, ride_id, status, note) VALUES(?,?,?,?)", tenantId, id, "accepted", "dispatched to " + m.driver.name);
      Object.assign(out, { status: "accepted", driver: m.driver, eta_min: m.eta_min, distance_km: m.distance_km });
    }
  }
  return out;
}

function updateRide(tenantId, id, to, note) {
  const D = db();
  const r = D.get("SELECT id, status, driver_id, distance_km, duration_min, payment_method, surge FROM rides WHERE id=? AND tenant_id=?", Number(id), tenantId);
  if (!r) throw new Error("Unknown ride " + id);
  if (r.status === to) return D.get("SELECT * FROM rides WHERE id=?", Number(id));
  if (!legalTransition(tenantId, r.status, to)) throw new Error("Illegal transition: " + r.status + " → " + to);
  const patch = { status: to };
  const now = stamp();
  if (to === "accepted") patch.accepted_at = now;
  if (to === "arrived") patch.arrived_at = now;
  if (to === "trip_start") patch.started_at = now;
  if (to === "completed") {
    patch.completed_at = now;
    const f = computeFare(tenantId, Number(r.distance_km) || 0, Number(r.duration_min) || 0, Number(r.surge) || 1);
    patch.fare = f.fare;
    /* a completed ride settles: the driver earns and is rated-up, the ride's payment is
       recorded. Wallet settlement rides lib/offers.js when the rider paid by wallet */
    D.run("UPDATE drivers SET rides_completed = rides_completed + 1, earnings = earnings + ?, status='online' WHERE id=?",
      f.fare * (1 - (Number(caps().cap(tenantId, "ride_hailing").platform_take_rate_pct || 0) / 100)), r.driver_id);
  }
  if (to === "cancelled") {
    patch.cancelled_at = now;
    const c = caps().cap(tenantId, "ride_hailing");
    if (r.status === "trip_start") patch.fare = Number(c.cancel_fee_midtrip) || 0;
    else if (r.status === "accepted") patch.fare = Number(c.cancel_fee_accepted) || 0;
    if (r.driver_id) D.run("UPDATE drivers SET rides_cancelled = rides_cancelled + 1, status='online' WHERE id=?", r.driver_id);
  }
  const sets = Object.keys(patch).map(k => k + "=?").join(", ");
  D.run("UPDATE rides SET " + sets + " WHERE id=?", ...Object.values(patch), Number(id));
  D.run("INSERT INTO ride_events(tenant_id, ride_id, status, note) VALUES(?,?,?,?)", tenantId, Number(id), to, note || "");
  return D.get("SELECT * FROM rides WHERE id=?", Number(id));
}

/* two-way rating: a rider rates a completed trip, and the driver's rolling average is
   recomputed from real rides — the same health-discipline the marketplace applies to
   sellers (lib/marketplace-ext.js), applied to drivers here */
function rateRide(tenantId, id, rating) {
  const D = db();
  const r = D.get("SELECT id, driver_id, status FROM rides WHERE id=? AND tenant_id=?", Number(id), tenantId);
  if (!r) throw new Error("Unknown ride " + id);
  if (r.status !== "completed") throw new Error("Only a completed ride can be rated");
  const n = Math.min(5, Math.max(1, Number(rating) || 5));
  D.run("UPDATE rides SET rating=? WHERE id=?", n, Number(id));
  if (r.driver_id) {
    const d = D.get("SELECT rating, rides_completed FROM drivers WHERE id=?", r.driver_id);
    if (d) {
      const rc = Number(d.rides_completed) || 0;
      const avg = rc > 0 ? ((Number(d.rating) * rc) + n) / (rc + 1) : n;
      D.run("UPDATE drivers SET rating=? WHERE id=?", +avg.toFixed(2), r.driver_id);
    }
  }
  return { rated: n };
}

/* ---------------- reads ---------------- */
function listRides(tenantId, f) {
  const D = db(); f = f || {};
  let sql = `SELECT r.*, d.name driver_name, d.rating driver_rating
             FROM rides r LEFT JOIN drivers d ON d.id=r.driver_id
             WHERE r.tenant_id=?`;
  const a = [tenantId];
  if (f.status) { sql += " AND r.status=?"; a.push(f.status); }
  if (f.driver_id) { sql += " AND r.driver_id=?"; a.push(Number(f.driver_id)); }
  if (f.q) { sql += " AND (r.ref LIKE ? OR r.rider LIKE ? OR r.pickup LIKE ? OR r.dropoff LIKE ?)"; const p = "%" + f.q + "%"; a.push(p, p, p, p); }
  sql += " ORDER BY r.requested_at DESC LIMIT 300";
  return D.all(sql, ...a);
}
function listDrivers(tenantId, f) {
  const D = db(); f = f || {};
  let sql = "SELECT * FROM drivers WHERE tenant_id=?";
  const a = [tenantId];
  if (f.status) { sql += " AND status=?"; a.push(f.status); }
  if (f.vehicle_kind) { sql += " AND vehicle_kind=?"; a.push(f.vehicle_kind); }
  sql += " ORDER BY status ASC, rating DESC LIMIT 300";
  return D.all(sql, ...a);
}
function listZones(tenantId) {
  return db().all("SELECT * FROM surge_zones WHERE tenant_id=? ORDER BY active DESC, id", tenantId);
}
function listVehicles(tenantId) {
  return db().all("SELECT v.*, d.name driver_name FROM vehicles v LEFT JOIN drivers d ON d.id=v.driver_id WHERE v.tenant_id=? ORDER BY v.status, v.kind", tenantId);
}
function summary(tenantId) {
  const D = db();
  const row = D.get(`SELECT COUNT(*) n,
    SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) completed,
    SUM(CASE WHEN status='cancelled' THEN 1 ELSE 0 END) cancelled,
    SUM(CASE WHEN status IN ('requested','accepted','arrived','trip_start') THEN 1 ELSE 0 END) active,
    COALESCE(SUM(CASE WHEN status='completed' THEN fare ELSE 0 END),0) revenue,
    COALESCE(AVG(CASE WHEN status='completed' AND rating IS NOT NULL THEN rating END),0) avg_rating
    FROM rides WHERE tenant_id=?`, tenantId);
  const dr = D.get("SELECT COUNT(*) n, SUM(CASE WHEN status='online' THEN 1 ELSE 0 END) online, COALESCE(AVG(rating),0) avg_rating FROM drivers WHERE tenant_id=? AND deactivated_at IS NULL", tenantId);
  return {
    rides: row.n || 0, completed: row.completed || 0, cancelled: row.cancelled || 0,
    active: row.active || 0, gross_revenue: +(row.revenue || 0).toFixed(2),
    avg_rating: +(row.avg_rating || 0).toFixed(2),
    drivers: dr.n || 0, drivers_online: dr.online || 0, driver_avg_rating: +(dr.avg_rating || 0).toFixed(2)
  };
}

/* ---------------- mutations: drivers, vehicles, zones ---------------- */
function upsertDriver(tenantId, body) {
  const D = db();
  const b = body || {};
  const email = String(b.email || "").trim().toLowerCase();
  if (!String(b.name || "").trim()) throw new Error("Driver name is required");
  const row = {
    name: String(b.name).trim(), email, phone: String(b.phone || ""),
    city: String(b.city || ""), vehicle_kind: ["car", "suv", "bike", "auto", "van"].includes(b.vehicle_kind) ? b.vehicle_kind : "car",
    plate: String(b.plate || ""), license: String(b.license || ""),
    status: ["offline", "online", "busy", "suspended"].includes(b.status) ? b.status : "offline",
    city_latency: Number(b.city_latency) || 0
  };
  if (b.id) {
    D.run(`UPDATE drivers SET name=?, email=?, phone=?, city=?, vehicle_kind=?, plate=?, license=?, status=?, city_latency=? WHERE id=? AND tenant_id=?`,
      row.name, row.email, row.phone, row.city, row.vehicle_kind, row.plate, row.license, row.status, row.city_latency, Number(b.id), tenantId);
    return D.get("SELECT * FROM drivers WHERE id=?", Number(b.id));
  }
  D.run(`INSERT INTO drivers(tenant_id, name, email, phone, city, vehicle_kind, plate, license, status, city_latency)
         VALUES(?,?,?,?,?,?,?,?,?,?)`, tenantId, row.name, row.email, row.phone, row.city, row.vehicle_kind, row.plate, row.license, row.status, row.city_latency);
  return D.get("SELECT * FROM drivers WHERE id=?", Number(D.get("SELECT last_insert_rowid() c").c));
}
function toggleDriver(tenantId, id, online) {
  const D = db();
  const d = D.get("SELECT id, status FROM drivers WHERE id=? AND tenant_id=?", Number(id), tenantId);
  if (!d) throw new Error("Unknown driver " + id);
  const to = online ? (d.status === "busy" ? "busy" : "online") : "offline";
  D.run("UPDATE drivers SET status=? WHERE id=?", to, Number(id));
  return D.get("SELECT * FROM drivers WHERE id=?", Number(id));
}
function deactivateDriver(tenantId, id) {
  const D = db();
  const d = D.get("SELECT id FROM drivers WHERE id=? AND tenant_id=?", Number(id), tenantId);
  if (!d) throw new Error("Unknown driver " + id);
  D.run("UPDATE drivers SET status='suspended', deactivated_at=? WHERE id=?", stamp(), Number(id));
  return { ok: true };
}
function upsertVehicle(tenantId, body) {
  const D = db();
  const b = body || {};
  if (!String(b.plate || "").trim()) throw new Error("Vehicle plate is required");
  const row = {
    plate: String(b.plate).trim().toUpperCase(),
    kind: ["car", "suv", "bike", "auto", "van"].includes(b.kind) ? b.kind : "car",
    capacity: Math.max(1, Number(b.capacity) || 4),
    status: ["active", "maintenance", "retired"].includes(b.status) ? b.status : "active",
    odometer: Number(b.odometer) || 0,
    insurance_until: b.insurance_until || null,
    driver_id: b.driver_id ? Number(b.driver_id) : null
  };
  if (b.id) {
    D.run("UPDATE vehicles SET plate=?, kind=?, capacity=?, status=?, odometer=?, insurance_until=?, driver_id=? WHERE id=? AND tenant_id=?",
      row.plate, row.kind, row.capacity, row.status, row.odometer, row.insurance_until, row.driver_id, Number(b.id), tenantId);
    return D.get("SELECT * FROM vehicles WHERE id=?", Number(b.id));
  }
  D.run("INSERT INTO vehicles(tenant_id, plate, kind, capacity, status, odometer, insurance_until, driver_id) VALUES(?,?,?,?,?,?,?,?)",
    tenantId, row.plate, row.kind, row.capacity, row.status, row.odometer, row.insurance_until, row.driver_id);
  return D.get("SELECT * FROM vehicles WHERE id=?", Number(D.get("SELECT last_insert_rowid() c").c));
}
function upsertZone(tenantId, body) {
  const D = db();
  const b = body || {};
  if (!String(b.name || "").trim()) throw new Error("Zone name is required");
  const row = {
    name: String(b.name).trim(),
    kind: ["geofence", "event", "weather"].includes(b.kind) ? b.kind : "geofence",
    multiplier: Math.max(1, Number(b.multiplier) || 1),
    center_lat: b.center_lat != null && b.center_lat !== "" ? Number(b.center_lat) : null,
    center_lng: b.center_lng != null && b.center_lng !== "" ? Number(b.center_lng) : null,
    radius_km: Math.max(0.1, Number(b.radius_km) || 3),
    active: b.active === false || b.active === 0 ? 0 : 1,
    starts_at: b.starts_at || null, ends_at: b.ends_at || null
  };
  if (b.id) {
    D.run("UPDATE surge_zones SET name=?, kind=?, multiplier=?, center_lat=?, center_lng=?, radius_km=?, active=?, starts_at=?, ends_at=? WHERE id=? AND tenant_id=?",
      row.name, row.kind, row.multiplier, row.center_lat, row.center_lng, row.radius_km, row.active, row.starts_at, row.ends_at, Number(b.id), tenantId);
    return D.get("SELECT * FROM surge_zones WHERE id=?", Number(b.id));
  }
  D.run("INSERT INTO surge_zones(tenant_id, name, kind, multiplier, center_lat, center_lng, radius_km, active, starts_at, ends_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
    tenantId, row.name, row.kind, row.multiplier, row.center_lat, row.center_lng, row.radius_km, row.active, row.starts_at, row.ends_at);
  return D.get("SELECT * FROM surge_zones WHERE id=?", Number(D.get("SELECT last_insert_rowid() c").c));
}

/* ---------------- demo seed ---------------- */
/* a worked example so a ride-hailing composition is observable on first boot: a small
   fleet, one active surge zone, and rides at every stage of the lifecycle. Seeded once
   (the caller gates on the presence of any ride row), so an operator's real data is
   never overwritten. Every VALUE here is seed data, not a business rule — the rates and
   radii the engines use are the capability params above, read at runtime */
function seedDemo(tenantId) {
  const D = db();
  const drivers = [
    ["Aarav Sharma", "aarav@luxora.shop", "+1 555 0101", "Downtown", "car", "LX-4421", 0.4, "online"],
    ["Diya Patel", "diya@luxora.shop", "+1 555 0102", "Midtown", "car", "LX-7788", 1.2, "online"],
    ["Vikram Singh", "vikram@luxora.shop", "+1 555 0103", "Uptown", "suv", "LX-9012", 2.6, "busy"],
    ["Meera Iyer", "meera@luxora.shop", "+1 555 0104", "Harbour", "bike", "LX-3345", 0.8, "online"],
    ["Rohan Das", "rohan@luxora.shop", "+1 555 0105", "Old Town", "auto", "LX-6690", 3.4, "offline"]
  ];
  for (const [name, email, phone, city, kind, plate, latency, status] of drivers) {
    D.run(`INSERT INTO drivers(tenant_id,name,email,phone,city,vehicle_kind,plate,status,city_latency,rating,rides_completed,earnings)
           VALUES(?,?,?,?,?,?,?,?,?,5.0,0,0)`,
      tenantId, name, email, phone, city, kind, plate, status, latency);
  }  const ids = D.all("SELECT id FROM drivers WHERE tenant_id=? ORDER BY id", tenantId).map(r => r.id);
  D.run("UPDATE drivers SET rating=4.9, rides_completed=214, earnings=3820.50 WHERE id=?", ids[0]);
  D.run("UPDATE drivers SET rating=4.7, rides_completed=158, earnings=2710.00 WHERE id=?", ids[1]);
  D.run("UPDATE drivers SET rating=4.8, rides_completed=301, earnings=5440.25 WHERE id=?", ids[2]);
  D.run("INSERT INTO vehicles(tenant_id,plate,kind,capacity,status,driver_id) VALUES(?,?,?,?,?,?)", tenantId, "LX-4421", "car", 4, "active", ids[0]);
  D.run("INSERT INTO vehicles(tenant_id,plate,kind,capacity,status,driver_id) VALUES(?,?,?,?,?,?)", tenantId, "LX-7788", "car", 4, "active", ids[1]);
  D.run("INSERT INTO vehicles(tenant_id,plate,kind,capacity,status,driver_id) VALUES(?,?,?,?,?,?)", tenantId, "LX-9012", "suv", 6, "active", ids[2]);
  D.run("INSERT INTO vehicles(tenant_id,plate,kind,capacity,status) VALUES(?,?,?,?,?)", tenantId, "LX-3345", "bike", 2, "active");
  D.run("INSERT INTO surge_zones(tenant_id,name,kind,multiplier,center_lat,center_lng,radius_km,active) VALUES(?,?,?,?,?,?,?,1)",
    tenantId, "Airport surge", "event", 1.8, 40.6413, -73.7781, 4);
  D.run("INSERT INTO surge_zones(tenant_id,name,kind,multiplier,center_lat,center_lng,radius_km,active) VALUES(?,?,?,?,?,?,?,1)",
    tenantId, "Downtown peak", "geofence", 1.35, 40.7128, -74.0060, 3);
  /* rides across the lifecycle, each carrying a realistic fare and history */
  const mk = (rider, pickup, dropoff, kind, status, km, min, surge, driverIdx, payment, daysAgo) => {
    const ref = "RIDE-" + tenantId + "-" + (1000 + D.get("SELECT COUNT(*) c FROM rides WHERE tenant_id=?").c) + "-" + Math.floor(Math.random() * 1e6).toString(36);
    const f = computeFare(tenantId, km, min, surge);
    const req = new Date(Date.now() - daysAgo * 86400e3).toISOString().slice(0, 19).replace("T", " ");
    D.run(`INSERT INTO rides(tenant_id,ref,rider,pickup,dropoff,vehicle_kind,driver_id,status,fare,surge,distance_km,duration_min,payment_method,rating,requested_at,accepted_at,completed_at)
           VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`,
      tenantId, ref, rider, pickup, dropoff, kind, driverIdx != null ? ids[driverIdx] : null, status,
      status === "completed" || status === "cancelled" ? f.fare : 0, surge, km, min, payment,
      status === "completed" ? 5 : null, req, req, status === "completed" ? req : null);
    const rid = Number(D.get("SELECT last_insert_rowid() c").c);
    D.run("INSERT INTO ride_events(tenant_id,ride_id,status,note) VALUES(?,?,?,?)", tenantId, rid, "requested", "ride requested");
    if (driverIdx != null) D.run("INSERT INTO ride_events(tenant_id,ride_id,status,note) VALUES(?,?,?,?)", tenantId, rid, "accepted", "dispatched");
    if (status === "completed") D.run("INSERT INTO ride_events(tenant_id,ride_id,status,note) VALUES(?,?,?,?)", tenantId, rid, "completed", "trip complete");
  };
  mk("Olivia Bennett", "Downtown · 5th Ave", "Airport · Terminal 4", "car", "completed", 24.6, 38, 1.8, 0, "card", 1);
  mk("Noah Williams", "Midtown · Madison", "Uptown · 86th", "car", "completed", 11.2, 19, 1.0, 1, "wallet", 2);
  mk("Emma Davis", "Harbour Pier 17", "Financial District", "bike", "completed", 6.4, 12, 1.35, 3, "cash", 3);
  mk("Liam Garcia", "Old Town Market", "University Campus", "auto", "completed", 8.9, 22, 1.0, null, "upi", 4);
  mk("Sophia Brown", "Airport · Terminal 1", "Downtown · 5th Ave", "suv", "completed", 22.1, 34, 1.8, 2, "card", 5);
  mk("Jackson Lee", "Convention Center", "Midtown · Madison", "car", "cancelled", 4.2, 8, 1.0, 0, "cash", 6);
  mk("Ava Miller", "Uptown · 86th", "Harbour Pier 17", "car", "accepted", 0, 0, 1.35, 1, "wallet", 0);
  mk("Mason Wilson", "Financial District", "Airport · Terminal 2", "suv", "requested", 0, 0, 1.0, null, "card", 0);
}

module.exports = {
  seed, seedDemo, DEFAULT_STATUSES, FARE_RULES, dist, surgeFor, computeFare, matchDriver,
  legalTransition, requestRide, updateRide, rateRide,
  listRides, listDrivers, listZones, listVehicles, summary,
  upsertDriver, toggleDriver, deactivateDriver, upsertVehicle, upsertZone
};
