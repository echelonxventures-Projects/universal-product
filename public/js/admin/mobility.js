/* LUXORA Platform — the mobility domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

/* ========== E17 · the mobility universe (rides & dispatch · fleet) ==========
   The console renders only what lib/mobility.js answered: every fare, surge
   multiplier, ETA and cancellation fee was computed from the store's own capability
   params. No rate is hard-coded in this file. */
async function vRides() {
  const [d, caps] = await Promise.all([api("/admin/mobility", {}), coCaps()]);
  const surgeOn = hasCap({ on: caps.filter(c => c.on).map(c => c.key) }, "dynamic_pricing");
  const st = d.stats || {};
  const rides = d.rides || [];
  await loadSM();
  const active = rides.filter(r => !smIs("ride", r.status, "terminal"));
  const done = rides.filter(r => smIs("ride", r.status, "terminal"));
  /* each ride's next step is the ride machine's next legal move (cancelling is its own button) */
  const nextOf = st => { const mv = smNext("ride", st)[0]; return mv ? [mv.to, mv.label] : undefined; };
  const chip = s => `<span class="a-chip">${esc(s)}</span>`;
  return `<div class="a-head"><h2>🚗 Rides &amp; Dispatch</h2><p class="a-sub">The ride lifecycle, surge pricing and live dispatch. Fares, cancellation fees and the platform commission are the store's own capability params — <code>ride_hailing</code> · <code>dynamic_pricing</code> · <code>dispatch</code> — and the legal transitions live in Data Studio (<code>mobilityTransitions</code>), so no rate or rule is hard-coded here.</p></div>
  <div class="a-cards">
    <div class="a-card"><h3>Live</h3>
      <div class="a-stats">${[["Rides", st.rides || 0], ["Active now", st.active || 0], ["Drivers online", st.drivers_online || 0], ["Gross revenue", (st.gross_revenue || 0).toFixed(2)], ["Avg rating", (st.avg_rating || 0).toFixed(1)]].map(([k, v]) => `<div><b>${v}</b><span>${k}</span></div>`).join("")}</div>
      <div style="margin-top:10px"><button class="btn-yellow" data-act="mob-new-ride">＋ Request a ride</button></div></div>
    <div class="a-card"><h3>Surge zones</h3>
      ${surgeOn ? `<div style="margin-bottom:8px"><button class="btn-yellow sm" data-act="mob-new-zone">＋ New zone</button></div>`
        : `<p class="p-tag">Switch on <code>dynamic_pricing</code> in ⚙️ Capabilities to raise a multiplier by zone.</p>`}
      <div class="a-tablewrap"><table class="a-table"><thead><tr><th>zone</th><th>kind</th><th>multiplier</th><th>radius</th><th>state</th>${surgeOn ? "<th></th>" : ""}</tr></thead>
      <tbody>${(d.zones || []).map(z => `<tr>
        <td>${esc(z.name)}</td><td>${esc(z.kind)}</td><td><b>×${(+z.multiplier).toFixed(2)}</b></td><td>${z.radius_km} km</td>
        <td>${chip(z.active ? "active" : "idle")}</td>
        ${surgeOn ? `<td style="white-space:nowrap">
          <button class="btn-white sm" data-act="mob-toggle-zone" data-id="${z.id}" data-on="${z.active ? 0 : 1}">${z.active ? "Pause" : "Resume"}</button>
          <button class="btn-white sm" data-act="mob-edit-zone" data-id="${z.id}">Edit</button></td>` : ""}
      </tr>`).join("") || `<tr><td colspan="${surgeOn ? 6 : 5}">No surge zones — every ride prices at ×1.</td></tr>`}</tbody></table></div></div>
  </div>
  <div class="a-card"><h3>Active rides (${active.length})</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>ref</th><th>rider</th><th>route</th><th>vehicle</th><th>driver</th><th>surge</th><th>eta</th><th>status</th><th></th></tr></thead>
    <tbody>${active.map(r => { const nx = nextOf(r.status); return `<tr>
      <td><code>${esc(r.ref)}</code></td><td>${esc(r.rider || "—")}</td>
      <td>${esc(r.pickup)} → ${esc(r.dropoff)}</td><td>${chip(r.vehicle_kind)}</td>
      <td>${esc(r.driver_name || "unassigned")}</td>
      <td>${(+r.surge) > 1 ? `<b>×${(+r.surge).toFixed(2)}</b>` : "—"}</td>
      <td>${r.eta_min ? r.eta_min + " min" : "—"}</td><td>${chip(r.status)}</td>
      <td>${nx ? `<button class="btn-white sm" data-act="mob-next" data-id="${r.id}" data-to="${nx[0]}">${nx[1]}</button>` : ""}</td>
    </tr>`; }).join("") || `<tr><td colspan="9">No rides in flight — request one above.</td></tr>`}</tbody></table></div></div>
  <div class="a-card"><h3>Ride history</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>ref</th><th>rider</th><th>route</th><th>driver</th><th>distance</th><th>duration</th><th>fare</th><th>rating</th><th>status</th></tr></thead>
    <tbody>${done.map(r => `<tr>
      <td><code>${esc(r.ref)}</code></td><td>${esc(r.rider || "—")}</td>
      <td>${esc(r.pickup)} → ${esc(r.dropoff)}</td><td>${esc(r.driver_name || "—")}</td>
      <td>${(+r.distance_km).toFixed(1)} km</td><td>${(+r.duration_min).toFixed(0)} min</td>
      <td>${r.fare ? (+r.fare).toFixed(2) : "—"}</td><td>${r.rating || "—"}</td><td>${chip(r.status)}</td>
    </tr>`).join("") || `<tr><td colspan="9">No completed rides yet.</td></tr>`}</tbody></table></div></div>`;
}
async function vFleet() {
  const d = await api("/admin/mobility", {});
  const st = d.stats || {};
  const chip = s => `<span class="a-chip">${esc(s)}</span>`;
  return `<div class="a-head"><h2>🚙 Fleet &amp; Drivers</h2><p class="a-sub">Driver onboarding, online state and the vehicle registry. Dispatch ranks candidates by rating then proximity, and a driver below the configured floor (<code>fleet_management · min_rating_to_dispatch</code>) is held out of matching. Vehicle kinds are the Data Studio list <code>mobilityVehicleKinds</code>.</p></div>
  <div class="a-cards">
    <div class="a-card"><h3>Fleet health</h3>
      <div class="a-stats">${[["Drivers", st.drivers || 0], ["Online", st.drivers_online || 0], ["Avg rating", (st.driver_avg_rating || 0).toFixed(2)], ["Completed", st.completed || 0], ["Cancelled", st.cancelled || 0]].map(([k, v]) => `<div><b>${v}</b><span>${k}</span></div>`).join("")}</div>
      <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap"><button class="btn-yellow" data-act="mob-new-driver">＋ Add driver</button><button class="btn-white" data-act="mob-new-vehicle">＋ Add vehicle</button></div></div>
    <div class="a-card"><h3>Vehicles</h3>
      <div class="a-tablewrap"><table class="a-table"><thead><tr><th>plate</th><th>kind</th><th>capacity</th><th>driver</th><th>odometer</th><th>insurance</th><th>status</th></tr></thead>
      <tbody>${(d.vehicles || []).map(v => `<tr><td><code>${esc(v.plate)}</code></td><td>${esc(v.kind)}</td><td>${v.capacity}</td>
      <td>${esc(v.driver_name || "—")}</td><td>${(+v.odometer).toFixed(0)} km</td><td>${esc(v.insurance_until || "—")}</td><td>${chip(v.status)}</td></tr>`).join("") || `<tr><td colspan="7">No vehicles registered.</td></tr>`}</tbody></table></div></div>
  </div>
  <div class="a-card"><h3>Drivers</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>name</th><th>city</th><th>vehicle</th><th>plate</th><th>rating</th><th>rides</th><th>earnings</th><th>state</th><th></th></tr></thead>
    <tbody>${(d.drivers || []).map(x => `<tr>
      <td>${esc(x.name)}${x.email ? `<div class="a-sub">${esc(x.email)}</div>` : ""}</td>
      <td>${esc(x.city || "—")}</td><td>${chip(x.vehicle_kind)}</td><td><code>${esc(x.plate || "—")}</code></td>
      <td>${(+x.rating).toFixed(2)}</td><td>${x.rides_completed}</td><td>${(+x.earnings).toFixed(2)}</td>
      <td>${chip(x.status)}</td>
      <td>${smIs("driver", x.status, "blocked") ? "" : `<button class="btn-white sm" data-act="mob-toggle-driver" data-id="${x.id}" data-to="${smIs("driver", x.status, "online") ? "0" : "1"}">${smIs("driver", x.status, "online") ? "Go offline" : "Go online"}</button> <button class="btn-white sm" data-act="mob-deact-driver" data-id="${x.id}">Deactivate</button>`}
      ${x.deactivated_at ? `<span class="a-sub">since ${esc(x.deactivated_at)}</span>` : ""}</td>
    </tr>`).join("") || `<tr><td colspan="9">No drivers yet — add one above.</td></tr>`}</tbody></table></div></div>`;
}

screen("rides", { render: async () => await vRides() });
screen("fleet", { render: async () => await vFleet() });

/* ========== trips: safety, rides booked for later, shared rides, ratings and driver pay (lib/trips.js) ==========
   Everything here is what the engine answered: whether a report is still unhandled, whether a payout
   may be approved or paid, who is held for review. */
let trDriver = null;
async function vTrips() {
  const o = await api("/admin/trips");
  const st = trDriver ? await api("/admin/trips/drivers/" + trDriver + "/statement").catch(() => null) : null;
  const drivers = o.drivers.map(d => `<option value="${d.id}"${String(d.id) === String(trDriver) ? " selected" : ""}>${esc(d.name)}</option>`).join("");
  const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
  const where = e => e.lat != null ? `<div class="a-sub">📍 ${(+e.lat).toFixed(5)}, ${(+e.lng).toFixed(5)}</div>` : "";
  const urgent = o.safety.filter(e => e.urgent && e.open);
  return `<div class="a-head"><h2>🛡️ Trips, Safety &amp; Pay</h2><p class="a-sub">Emergencies and incidents riders and drivers report, rides booked for later, shared rides forming, drivers whose ratings fell below the floor (${o.policy.rating.floor}), and what each driver earned and is paid. Local emergency number: <b>${esc(o.emergency)}</b>.</p></div>
  ${urgent.length ? `<div class="a-card" role="alert" style="border:2px solid #b91c1c"><h3>🚨 Open emergencies: ${urgent.length}</h3><p>Call the rider or driver now. If anyone is in danger, call the emergency number: <b>${esc(o.emergency)}</b></p></div>` : ""}
  <div class="a-card"><h3>Safety reports</h3>${coTbl(["report", "ride", "what", "by", "contact", "status", ""], o.safety, e => [`<code>${esc(e.ref)}</code><div class="a-sub">${esc(e.created_at)}</div>`, `<code>${esc(e.ride_ref || "—")}</code><div class="a-sub">${esc(e.pickup || "")} → ${esc(e.dropoff || "")}</div>`,
    `${e.urgent ? `<b>🚨 ${esc(e.label)}</b>` : esc(e.label)}${e.note ? `<div class="a-sub">${esc(e.note)}</div>` : ""}${where(e)}`, `${esc(e.by_role)}<div class="a-sub">${esc(e.by_who)}</div>`,
    `${e.rider_phone ? "rider " + esc(e.rider_phone) : ""}${e.driver_phone ? `<div>driver ${esc(e.driver_name || "")} ${esc(e.driver_phone)}</div>` : ""}`,
    coBadge(e.status) + (e.handled_by ? `<div class="a-sub">${esc(e.handled_by)}</div>` : "") + (e.outcome ? `<div class="a-sub">${esc(e.outcome)}</div>` : ""),
    (e.unhandled ? `<button class="p-btn sm primary" data-tr-ack="${e.id}">I'm on it</button> ` : "") + (e.open ? `<button class="p-btn sm" data-tr-res="${e.id}">Resolve</button>` : "")], "No reports.")}</div>
  <div class="a-cards">
    <div class="a-card"><h3>Booked for later</h3>${coTbl(["booking", "pickup at (UTC)", "rider", "route", "kind", "estimate", ""], o.bookings, b => [`<code>${esc(b.ref)}</code>`, esc(b.pickup_at), esc(b.rider), `${esc(b.pickup)} → ${esc(b.dropoff)}`, esc(b.vehicle_kind), b.estimate ? money(b.estimate) : "—", `<button class="p-btn sm" data-tr-bc="${b.id}">Cancel</button>`], "Nothing booked.")}
      <p><button class="p-btn sm" id="trSweep">Dispatch what is due now</button></p></div>
    <div class="a-card"><h3>Shared rides forming</h3>${coTbl(["kind", "riders", "seats", "driver", "open until (UTC)"], o.pools, p => [esc(p.vehicle_kind), p.riders, p.seats_taken + " of " + p.capacity, esc(p.driver_name || "finding one"), esc(p.closes_at)], "None forming.")}
      <p class="a-sub">Sharing discount: ${o.policy.pool.discountPct}% · pickups within: ${o.policy.pool.pickupWithinKm} km · drops within: ${o.policy.pool.dropoffWithinKm} km</p></div>
  </div>
  <div class="a-cards">
    <div class="a-card"><h3>Drivers to review</h3>${coTbl(["driver", "rating", "ratings", "held", ""], o.review, d => [esc(d.name), (+d.rating).toFixed(2), d.rating_count, d.review ? "held out of dispatch" : "below the floor", d.review ? `<button class="p-btn sm" data-tr-clear="${d.id}">Let them drive</button>` : ""], "Nobody below the floor.")}</div>
    <div class="a-card"><h3>Recent ratings</h3>${coTbl(["ride", "by", "stars", "tags", "comment"], o.ratings.slice(0, 30), g => [`<code>${esc(g.ref)}</code>`, esc(g.by_role) + (g.driver_name ? `<div class="a-sub">${esc(g.driver_name)}</div>` : ""), "★".repeat(g.stars), g.tags.map(x => `<span class="a-chip">${esc(x)}</span>`).join(" "), esc(g.comment || "")], "No ratings yet.")}</div>
  </div>
  <div class="a-card"><h3>Driver pay</h3>
    ${coTbl(["driver", "unpaid trips", "unpaid", ""], o.unpaid, u => [esc(u.name), u.trips, money(u.net), `<button class="p-btn sm" data-tr-pay="${u.id}">Make payout</button> <button class="p-btn sm" data-tr-st="${u.id}">Statement</button>`], "Nothing unpaid.")}
    <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:flex-end;margin-top:8px"><label><span>Driver</span><select id="trD">${drivers}</select></label><label><span>Pay trips up to</span><input id="trThrough" type="date" value="${yesterday}"></label>
      <button class="p-btn sm primary" id="trMake">Make payout</button><button class="p-btn sm" id="trShow">Show statement</button></div>
    <h4 style="margin-top:12px">Payouts</h4>
    ${coTbl(["payout", "driver", "up to", "trips", "fares", "platform", "tips", "to pay", "status", ""], o.payouts, p => [`<code>${esc(p.ref)}</code>`, esc(p.driver), esc(p.through), p.trips, money(p.fares), money(p.take), money(p.tips), `<b>${money(p.net)}</b>`,
      coBadge(p.status) + (p.pay_ref ? `<div class="a-sub">${esc(p.pay_ref)}</div>` : ""),
      (p.editable ? `<button class="p-btn sm primary" data-tr-po="${p.id}:approve">Approve</button> ` : "") + (p.owed ? `<button class="p-btn sm primary" data-tr-po="${p.id}:pay">Mark paid</button> ` : "") + (p.open ? `<button class="p-btn sm" data-tr-po="${p.id}:void">Void</button>` : "")], "No payouts yet.")}</div>
  ${st ? `<div class="a-card"><h3>Statement</h3><div class="a-stats">${[["Trips", st.statement.totals.trips], ["Fares", money(st.statement.totals.fares)], ["Platform", money(st.statement.totals.take)], ["Tips", money(st.statement.totals.tips)], ["Earned", money(st.statement.totals.net)], ["Unpaid", money(st.statement.unpaid.net)]].map(([k, v]) => `<div><b>${v}</b><span>${k}</span></div>`).join("")}</div>
    ${coTbl(["ride", "when", "route", "fare", "platform", "tip", "earned", "paid by"], st.statement.trips, x => [`<code>${esc(x.ref)}</code>${x.pool ? ` <span class="a-chip">shared</span>` : ""}${x.cancelled ? ` <span class="a-chip">cancellation fee</span>` : ""}`, esc(x.at), `${esc(x.pickup)} → ${esc(x.dropoff)}`, money(x.fare), money(x.take), money(x.tip), `<b>${money(x.net)}</b>`, x.payout ? `<code>${esc(x.payout)}</code>` : "unpaid"], "No trips.")}</div>` : ""}
  <div class="a-card"><h3>Places riders pick from</h3><p class="a-sub">Named places offered when a rider asks for a ride — one per line: <code>name, latitude, longitude</code>.</p>
    <textarea id="trPlaces" rows="5" style="width:100%">${esc(o.places.map(p => `${p.name}, ${p.lat}, ${p.lng}`).join("\n"))}</textarea><p><button class="p-btn sm primary" id="trSavePlaces">Save places</button></p></div>`;
}
function wireTrips() {
  const go = async (fn, msg) => { try { await fn(); if (msg) toast(msg); render(); } catch (e) { toast(e.message); } };
  const on = (sel, fn) => document.querySelectorAll(sel).forEach(x => x.onclick = () => fn(x));
  on("[data-tr-ack]", x => go(() => api(`/admin/trips/safety/${x.dataset.trAck}/acknowledge`, "POST", {}), "You are handling it"));
  on("[data-tr-res]", x => { const outcome = prompt("How was it resolved?"); if (outcome) go(() => api(`/admin/trips/safety/${x.dataset.trRes}/resolve`, "POST", { outcome }), "Resolved"); });
  on("[data-tr-bc]", x => { if (confirm("Cancel this booking?")) go(() => api(`/admin/trips/bookings/${x.dataset.trBc}/cancel`, "POST", {}), "Cancelled"); });
  on("[data-tr-clear]", x => go(() => api(`/admin/trips/drivers/${x.dataset.trClear}/clear-review`, "POST", {}), "They can drive again"));
  on("[data-tr-st]", x => { trDriver = x.dataset.trSt; render(); });
  on("[data-tr-pay]", x => go(() => api("/admin/trips/payouts", "POST", { driver_id: Number(x.dataset.trPay), through: $("#trThrough").value }), "Payout made"));
  on("[data-tr-po]", x => { const [id, act] = x.dataset.trPo.split(":"), body = {};
    if (x.dataset.trPo.endsWith(":pay")) { const r = prompt("The bank's reference for this payment (optional)"); if (r === null) return; body.pay_ref = r; }
    go(() => api(`/admin/trips/payouts/${id}/${act}`, "POST", body), "Done"); });
  const b = (id, fn) => { const e = $(id); if (e) e.onclick = fn; };
  b("#trSweep", () => go(() => api("/admin/trips/sweep", "POST", {}), "Dispatched what was due"));
  b("#trMake", () => go(() => api("/admin/trips/payouts", "POST", { driver_id: Number($("#trD").value), through: $("#trThrough").value }), "Payout made"));
  b("#trShow", () => { trDriver = $("#trD").value; render(); });
  b("#trSavePlaces", () => {
    const places = $("#trPlaces").value.split("\n").map(l => l.trim()).filter(Boolean).map(l => { const p = l.split(","); const lng = p.pop(), lat = p.pop(); return { name: p.join(",").trim(), lat: Number(lat), lng: Number(lng) }; });
    go(() => api("/admin/trips/places", "PUT", { places }), "Places saved");
  });
}
screen("trips", { render: async () => await vTrips(), wire: wireTrips });
