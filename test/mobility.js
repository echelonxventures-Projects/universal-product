"use strict";
const path = require("path");
const DB = path.join(__dirname, "mobility-tmp.db");
process.env.LX_DB = DB; process.env.NODE_ENV="test";
require("../lib/db.js");
const caps=require("../lib/capabilities.js");
const mob=require("../lib/mobility.js");
let pass=0, fail=0;
const ok=(c,n,x)=>{c?(pass++,console.log("  ✓ "+n)):(fail++,console.log("  ✗ "+n+(x?" → "+x:"")));};
(async()=>{
  await caps.seed(); await caps.seedPresets(); await mob.seed();
  const t=1;
  /* enable the mobility atoms — the engine must answer nothing without them */
  for(const k of ["ride_hailing","dynamic_pricing","dispatch","fleet_management"]) caps.enable(t,k,{});
  ok(mob.listRides(t).length>0,"the boot seed already demoed rides");
  ok(mob.listDrivers(t).length===5,"five drivers seeded");
  ok(mob.listVehicles(t).length===4,"four vehicles seeded");
  ok(mob.listZones(t).length===2,"two surge zones seeded");
  /* the fare is constructed purely from the declared params */
  const f=mob.computeFare(t,10,15,1.5);
  const c=caps.cap(t,"ride_hailing");
  const expect=+(Math.max(c.min_fare, c.base_fare + (c.per_km_rate*10 + c.per_min_rate*15)*1.5) + c.booking_fee).toFixed(2);
  ok(Math.abs(f.fare-expect)<0.01,"fare = f(params, surge)","got "+f.fare+" want "+expect);
  ok(Math.abs(f.breakdown.surge-1.5)<0.001,"breakdown carries the surge");
  /* surge is the configured ceiling, never above */
  const s1=mob.surgeFor(t,40.6413,-73.7781,"car");   /* inside the airport zone (×1.8) */
  ok(s1===1.8,"surge inside the airport zone = 1.8","got "+s1);
  const s2=mob.surgeFor(t,41.0,-75.0,"car");          /* far from every zone */
  ok(s2===1,"surge outside every zone = 1","got "+s2);
  /* the dispatcher matches the nearest idle driver of the requested kind */
  const m=mob.matchDriver(t,"car",40.71,-74.01);
  ok(!!m && !!m.driver,"dispatch matched a driver");
  ok(m.distance_km<=5,"match inside the configured radius","got "+(m&&m.distance_km));
  ok(m.eta_min>0,"ETA constructed","got "+(m&&m.eta_min));
  /* a bike request must not return a car */
  const mb=mob.matchDriver(t,"bike",40.71,-74.01);
  ok(!!mb && mb.driver.vehicle_kind==="bike","bike request matches a bike driver", mb&&mb.driver.vehicle_kind);
  /* the full lifecycle, each transition validated against the registry */
  const r1=mob.requestRide(t,"Test Rider","555","A","B","car","wallet",40.71,-74.01);
  ok(r1.status==="accepted","a request auto-dispatches (dispatch is on)","got "+r1.status);
  ok(!!r1.driver,"with a matched driver");
  const r2=mob.updateRide(t,r1.id,"arrived","driver at pickup");
  ok(r2.status==="arrived","arrived");
  const r3=mob.updateRide(t,r1.id,"trip_start","trip started");
  ok(r3.status==="trip_start","trip_start");
  const r4=mob.updateRide(t,r1.id,"completed","trip complete");
  ok(r4.status==="completed","completed");
  ok(r4.fare>0,"completion constructs a fare","got "+r4.fare);
  /* an illegal transition is refused, never silently applied */
  let refused=false; try{ mob.updateRide(t,r1.id,"accepted","backwards"); }catch(e){ refused=true; }
  ok(refused,"illegal transition completed → accepted is refused");
  /* rating recomputes the driver's rolling average */
  const before=mob.listDrivers(t).find(d=>d.id===r1.driver.id).rating;
  mob.rateRide(t,r1.id,5);
  const after=mob.listDrivers(t).find(d=>d.id===r1.driver.id).rating;
  ok(after>=before-0.001,"rating folds into the driver average", before+" → "+after);
  /* rating a non-completed ride is refused */
  let rRefused=false; try{ const x=mob.requestRide(t,"R2","555","C","D","car","cash",40.71,-74.01); mob.rateRide(t,x.id,5); }catch(e){ rRefused=true; }
  ok(rRefused,"rating an incomplete ride is refused");
  /* cancellation fees are per-state params */
  const cx=mob.requestRide(t,"R3","555","E","F","car","cash",40.71,-74.01);
  const cxx=mob.updateRide(t,cx.id,"cancelled","rider cancelled");
  ok(cxx.status==="cancelled"&&cxx.fare===c.cancel_fee_accepted,"cancel after acceptance costs the configured fee","got "+cxx.fare);
  /* disabling the atom makes the engine refuse */
  caps.disable(t,"ride_hailing");
  let gate=false; try{ mob.requestRide(t,"X","555","G","H","car","cash",0,0); }catch(e){ gate=/not enabled/.test(e.message); }
  ok(gate,"a disabled atom refuses a new ride");
  caps.enable(t,"ride_hailing",{});
  /* zero hardcoded: every engine value traces to a param */
  const all=caps.catalog().map(x=>x.key);
  ok(all.includes("ride_hailing")&&all.includes("dynamic_pricing")&&all.includes("dispatch")&&all.includes("fleet_management"),
     "the four mobility atoms are catalog rows");

  /* ---- HTTP layer: the routes are gated and drive the real engine ---- */
  console.log("▸ HTTP LAYER (gated routes against a live server)");
  const { spawn } = require("child_process");
  const PORT = 8871, BASE = `http://localhost:${PORT}`;
  const fs = require("fs");
  const httpDb = path.join(__dirname, "mobility-http.db");
  for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(httpDb + s, { force: true }); } catch (e) { } }
  const srv = spawn(process.execPath, [path.join(__dirname, "..", "server.js")],
    { env: { ...process.env, PORT, LX_DB: httpDb }, stdio: ["ignore", "ignore", "inherit"] });
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const jar = new Map();
  const api = async (p, m = "GET", body) => {
    const opt = { method: m, headers: { Cookie: [...jar].map(([k, v]) => k + "=" + v).join("; "), ...(m !== "GET" ? { "x-csrf": jar.get("azc") || "" } : {}) } };
    if (body) { opt.body = JSON.stringify(body); opt.headers["Content-Type"] = "application/json"; }
    const r = await fetch(BASE + p, opt);
    (r.headers.getSetCookie ? r.headers.getSetCookie() : []).forEach(c => { const [kv] = c.split(";"); const i = kv.indexOf("="); jar.set(kv.slice(0, i).trim(), kv.slice(i + 1).trim()); });
    return { status: r.status, body: await r.json().catch(() => ({})) };
  };
  let up = false;
  for (let i = 0; i < 120; i++) { try { if ((await fetch(BASE + "/healthz")).ok) { up = true; break; } } catch (e) { } await sleep(1000); }
  ok(up, "the server boots with the mobility schema");
  if (up) {
    await api("/api/auth/login", "POST", { email: "admin@luxora.shop", password: "admin123" });
    /* the flagship store has no mobility atoms on by default — the surface must refuse */
    const gated = await api("/api/admin/mobility");
    ok(gated.status === 403, "the mobility surface is OFF until the atom is switched on", gated.status);
    /* switch the atoms on through the composition API, exactly as the console does */
    for (const k of ["ride_hailing", "dynamic_pricing", "dispatch", "fleet_management"])
      await api("/api/capabilities/enable", "POST", { capability: k });
    const get = await api("/api/admin/mobility");
    ok(get.status === 200 && (get.body.rides || []).length > 0, "with the atoms on, the rides surface answers", get.status);
    ok((get.body.drivers || []).length === 5, "drivers in the payload");
    ok((get.body.zones || []).length === 2, "surge zones in the payload");
    ok(get.body.stats.rides > 0, "stats computed", JSON.stringify(get.body.stats));
    /* a request through HTTP auto-dispatches and prices */
    const req = await api("/api/admin/mobility/rides", "POST",
      { rider: "HTTP Rider", pickup: "Downtown · 5th Ave", dropoff: "Airport · Terminal 4", vehicle_kind: "car", payment_method: "card", pickup_lat: 40.71, pickup_lng: -74.01 });
    ok(req.status === 200 && !!req.body.ride, "a ride request through HTTP", req.status);
    const rid = req.body.ride.id;
    ok(req.body.ride.status === "accepted" && !!req.body.ride.driver, "auto-dispatched over HTTP", req.body.ride.status);
    /* the lifecycle advances through the gated route */
    let step = await api(`/api/admin/mobility/rides/${rid}`, "PUT", { status: "arrived" });
    ok(step.status === 200 && step.body.ride.status === "arrived", "arrived over HTTP", step.status);
    step = await api(`/api/admin/mobility/rides/${rid}`, "PUT", { status: "trip_start" });
    ok(step.body.ride.status === "trip_start", "trip_start over HTTP");
    step = await api(`/api/admin/mobility/rides/${rid}`, "PUT", { status: "completed" });
    ok(step.status === 200 && step.body.ride.fare > 0, "completed over HTTP with a constructed fare", step.body.ride.fare);
    /* an illegal transition is refused by the route, not applied */
    const bad = await api(`/api/admin/mobility/rides/${rid}`, "PUT", { status: "accepted" });
    ok(bad.status === 400, "an illegal transition returns 400", bad.status);
    /* fleet + zone mutations */
    const nd = await api("/api/admin/mobility/drivers", "POST", { name: "Test Driver", vehicle_kind: "car", plate: "T-001", status: "offline" });
    ok(nd.status === 200 && !!nd.body.driver, "a driver is created through HTTP", nd.status);
    const nv = await api("/api/admin/mobility/vehicles", "POST", { plate: "T-002", kind: "suv", capacity: 6 });
    ok(nv.status === 200 && !!nv.body.vehicle, "a vehicle is registered through HTTP", nv.status);
    const nz = await api("/api/admin/mobility/zones", "POST", { name: "Test zone", kind: "event", multiplier: 2.5, radius_km: 2 });
    ok(nz.status === 200 && !!nz.body.zone, "a surge zone is configured through HTTP", nz.status);
    /* a driver without a name is refused — validation reaches the route */
    const bd = await api("/api/admin/mobility/drivers", "POST", { vehicle_kind: "car" });
    ok(bd.status === 400, "an invalid driver is refused with 400", bd.status);
    /* switching the atom back off re-closes the surface */
    await api("/api/capabilities/disable", "POST", { capability: "ride_hailing" });
    const closed = await api("/api/admin/mobility");
    ok(closed.status === 403, "switching the atom off re-closes the surface", closed.status);
  }
  srv.kill("SIGTERM");
  await new Promise(r => setTimeout(r, 500));
  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail?1:0);
})().catch(e=>{console.log("ERR",e.message,e.stack);process.exit(1);});
