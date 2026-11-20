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

screen("rides", { group: "Mobility", label: "🚗 Rides & Dispatch", order: 0, render: async () => await vRides() });
screen("fleet", { group: "Mobility", label: "🚙 Fleet & Drivers", order: 1, render: async () => await vFleet() });
