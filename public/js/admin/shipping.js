/* LUXORA Platform — the shipping domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

async function vLogistics() {
  const [ships, sla, carriers] = await Promise.all([api("/shipments", {}), api("/admin/sla", { days: 3 }), api("/carriers", {})]);
  const statuses = ships.statuses || [];
  const by = {}; ships.shipments.forEach(s => by[s.status] = (by[s.status] || 0) + 1);
  return `<div class="a-head"><h2>🚚 Logistics &amp; Fulfilment</h2><p class="a-sub">Fulfilment state machine · shipment tracking · 3PL carrier abstraction · warehouse routing · SLA · return disposition. States &amp; dispositions live in Data Studio: <code>logisticsStates</code>, <code>logisticsDispositions</code>.</p></div>
  <div class="a-card"><h3>Active shipments</h3>
    <p class="a-sub">${Object.entries(by).map(([k, v]) => `<span class="a-chip">${esc(k)}·${v}</span>`).join(" ") || "none"}</p>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>ref</th><th>order</th><th>carrier</th><th>status</th><th>warehouse</th></tr></thead>
      <tbody>${ships.shipments.slice(0, 25).map(s => `<tr><td><code>${esc(s.tracking_ref)}</code></td><td>${s.order_id}</td><td>${esc(s.carrier || "—")}</td><td><span class="a-chip">${esc(s.status)}</span></td><td>${s.warehouse_id || "—"}</td></tr>`).join("") || '<tr><td colspan="5">No shipments yet.</td></tr>'}</tbody></table></div>
  </div>
  <div class="a-card"><h3>SLA breaches (&gt;3 days undelivered)</h3>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>ref</th><th>status</th><th>created</th></tr></thead>
      <tbody>${sla.breaches.map(b => `<tr><td><code>${esc(b.tracking_ref)}</code></td><td>${esc(b.status)}</td><td>${esc(b.created_at)}</td></tr>`).join("") || '<tr><td colspan="3">On schedule.</td></tr>'}</tbody></table></div>
  </div>
  <div class="a-card"><h3>3PL carriers (registry)</h3>
    <div>${(carriers.carriers || []).map(c => `<span class="a-chip">${esc(c.emoji || "")} ${esc(c.name)}</span>`).join(" ") || "none configured"}</div>
  </div>`;
}
/* ---------- Quick-commerce: dark stores, slots, serviceability, dispatch ---------- */
async function vQcOps() {
  const gate = await coGate("qcops");
  if (!gate.any) return coOff("quick-commerce", "⚡ Quick-commerce", gate.off);
  const d = await api("/qc/stores", {});
  const stores = d.stores || [], riders = d.riders || [];
  const runs = (await api("/qc/runs", {})).runs || [];
  const slots = await Promise.all((stores.slice(0, 4)).map(s => api("/qc/slots", { store: s.id, day: 0 }).then(x => x.slots || []).catch(() => [])));
  const flat = slots.flatMap((sl, i) => sl.map(x => ({ ...x, store: stores[i] && stores[i].name })));
  return `<div class="a-head"><h2>⚡ Quick-commerce Ops</h2>
    <p class="a-sub">Dark stores, delivery slots, per-store inventory pinning, riders and dispatch runs closed with a proof-of-delivery OTP. The promise a store advertises is its own minutes plus prep time, resolved per pincode. Kinds, statuses and vehicles are Data Studio registries: <code>qcStoreKinds</code>, <code>qcSlotStatuses</code>, <code>qcVehicles</code>.</p>
    <p class="a-sub"><b>On for this store:</b> ${gate.on.map(k => `<span class="a-chip">${esc(k)}</span>`).join(" ")}${gate.off.length ? ` <span class="p-tag">off: ${esc(gate.off.join(", "))}</span>` : ""}</p></div>
  <div class="a-card"><h3>Dark stores · ${stores.length}</h3>
    <p class="a-sub">${coChips(stores, s => s.kind || "dark_store")}</p>
    ${coTbl(["store", "code", "kind", "city", "pincode", "radius", "promise", "min order", "fee", "status"],
      stores, s => [esc(s.name), `<code>${esc(s.code)}</code>`, esc(s.kind), esc(s.city), esc(s.pincode), (s.service_radius_km || 0) + " km", (s.promise_minutes || 0) + " min", money(s.min_order), money(s.delivery_fee), coBadge(s.status)])}
    <button class="p-btn sm primary" data-act="co-new" data-key="dark_store">+ New dark store</button>
    <button class="p-btn sm" data-act="co-new" data-key="rider">+ New rider</button></div>
  <div class="a-card"><h3>Today's delivery slots</h3>
    ${coTbl(["window", "store", "capacity", "booked", "fee", "status"], flat,
      s => [`${esc(s.window_start)}–${esc(s.window_end)}`, esc(s.store || "—"), s.capacity, s.booked, s.fee ? money(s.fee) : "—", coBadge(s.status)],
      "No open slots today — create one from the dark store.")}</div>
  <div class="a-card"><h3>Riders · ${riders.length}</h3>
    ${coTbl(["rider", "phone", "vehicle", "city", "status", "rating", "deliveries"], riders,
      r => [esc(r.name), esc(r.phone || "—"), esc(r.vehicle || "—"), esc(r.city || "—"), coBadge(r.status), r.rating || "—", r.deliveries || 0])}</div>
  <div class="a-card"><h3>Dispatch runs · ${runs.length}</h3>
    <p class="a-sub">${coChips(runs, r => r.status)}</p>
    ${coTbl(["run", "store", "rider", "batch", "orders", "PoD OTP", "status"], runs,
      r => [`<code>${esc(r.ref)}</code>`, esc(String(r.store_id || "—")), esc(String(r.rider_id || "—")), r.batch_count || 0, (r.order_ids || []).length, `<code>${esc(r.pod_otp || "—")}</code>`, coBadge(r.status)])}
    <div style="display:flex;gap:8px;margin-top:8px;flex-wrap:wrap"><label><span>Store</span><select id="qcRunStore">${stores.map(s => `<option value="${s.id}">${esc(s.name)}</option>`).join("")}</select></label>
      <label><span>Rider</span><select id="qcRunRider">${riders.map(r => `<option value="${r.id}">${esc(r.name)}</option>`).join("")}</select></label>
      <label><span>Order ids (CSV)</span><input id="qcRunOrders" placeholder="101,102"></label>
      <button class="p-btn sm primary" id="qcRunGo">Create run</button></div></div>`;
}
function wireQcOps() {
  const g = $("#qcRunGo"); if (g) g.onclick = async () => {
    try {
      const orders = String($("#qcRunOrders").value || "").split(",").map(x => Number(x.trim())).filter(Boolean);
      const r = await api("/qc/runs", "POST", { store_id: Number($("#qcRunStore").value), rider_id: Number($("#qcRunRider").value), order_ids: orders, batch_count: orders.length });
      toast("Dispatch run " + (r.run && r.run.ref)); render();
    } catch (e) { toast(e.message); }
  };
}
async function vPickup() {
  const gate = await coGate("pickup");
  if (!gate.any) return coOff("pickup point", "📍 Pickup Points", gate.off);
  const d = await api("/admin/pickup", {});
  window.__pk = d;
  const kindName = k => ((d.kinds || []).find(x => x.key === k) || { name: k }).name;
  return `<div class="a-head"><h2>📍 Pickup Points &amp; Lockers</h2><p class="a-sub">Points shoppers can choose at checkout instead of a home address. The kinds of point are the <code>pickupKinds</code> registry; the fee, holding days, code length and lock-out are the <code>pickup_points</code> capability's params; a parcel's life is the <code>pickup</code> state machine.</p></div>
  <div class="a-card"><h3>Points</h3>
    <div style="margin-bottom:8px"><button class="btn-yellow sm" data-pk-new>＋ New point</button></div>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>code</th><th>name</th><th>kind</th><th>address</th><th>in use</th><th>hours</th><th>arrives in</th><th>state</th><th></th></tr></thead>
    <tbody>${(d.points || []).map(p => `<tr><td><code>${esc(p.code)}</code></td><td>${esc(p.name)}</td><td>${esc(kindName(p.kind))}</td>
      <td>${esc([p.address, p.city, p.postcode].filter(Boolean).join(", "))}</td><td>${p.held}${Number(p.capacity) > 0 ? " / " + p.capacity : ""}${p.full ? ' <span class="a-chip">full</span>' : ""}</td>
      <td>${esc(p.hours || "—")}</td><td>${p.eta != null ? esc(p.eta) + " d" : "—"}</td><td>${p.active ? "on" : "off"}</td>
      <td style="white-space:nowrap"><button class="btn-white sm" data-pk-edit="${p.id}">Edit</button> <button class="btn-white sm" data-pk-del="${p.id}">Remove</button></td></tr>`).join("") || '<tr><td colspan="9">No pickup points yet — add a locker, a counter or a shop.</td></tr>'}</tbody></table></div></div>
  <div class="a-card"><h3>Parcels</h3>
    <div style="margin-bottom:8px"><button class="btn-white sm" data-pk-sweep>Expire overdue parcels now</button></div>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>order</th><th>customer</th><th>point</th><th>state</th><th>hold until</th><th>wrong codes</th><th></th></tr></thead>
    <tbody>${(d.reservations || []).map(r => `<tr><td><code>${esc(r.order_num || r.order_id)}</code></td><td>${esc(r.customer || "—")}</td><td>${esc(r.point_name || "—")}</td>
      <td>${stateChip(r.state)}</td><td>${esc(r.hold_until || "—")}</td><td>${r.attempts || 0}</td><td style="white-space:nowrap">${verbButtons(d.actions || [], r, "pk-act")}</td></tr>`).join("") || '<tr><td colspan="7">No parcels for pickup yet.</td></tr>'}</tbody></table></div></div>`;
}
function wirePickup() {
  const d = window.__pk || {};
  $$("[data-pk-new]").forEach(b => b.onclick = () => pickupModal(null));
  $$("[data-pk-edit]").forEach(b => b.onclick = () => pickupModal((d.points || []).find(p => String(p.id) === b.dataset.pkEdit)));
  $$("[data-pk-del]").forEach(b => b.onclick = async () => {
    if (!confirm("Remove this point? A point with parcels is switched off instead.")) return;
    try { const r = await api("/admin/pickup/points/" + b.dataset.pkDel, "DELETE"); toast(r.deactivated ? "Switched off (it has parcels)" : "Removed"); render(); } catch (e) { toast(e.message); }
  });
  $$("[data-pk-sweep]").forEach(b => b.onclick = async () => { try { const r = await api("/admin/pickup/sweep", "POST", {}); toast(r.expired + " parcel(s) expired"); render(); } catch (e) { toast(e.message); } });
  $$("[data-pk-act]").forEach(b => b.onclick = async () => {
    const a = (d.actions || []).find(x => x.verb === b.dataset.pkAct) || {};
    let code;
    if (a.needs_code) { code = prompt("The customer's pickup code"); if (code == null) return; }
    try { const r = await api("/admin/pickup/reservations/" + b.dataset.id, "POST", { action: a.verb, code }); toast("Parcel " + r.reservation.state.label); render(); } catch (e) { toast(e.message); }
  });
}
/* ========== Shipping & Tracking UI ========== */
/* the carrier account is platform-wide (Platform → Provider Registry); what a store sets is
   its own ship-from address, the origin of every rate and label it buys */
function shippingHtml() {
  const html = `
    <div class="a-head">
      <h2>📦 Shipping & Tracking</h2>
      <p class="a-sub">Carrier rates and labels, your ship-from address, and parcel tracking</p>
    </div>
    <div class="a-card">
      <h3>Carrier account</h3>
      <div id="shippingProviders"></div>
    </div>
    <div class="a-card">
      <h3>Ship-from address</h3>
      <p class="a-sub">Where your parcels leave from. Carriers price every rate from this address.</p>
      <div id="shipFrom"></div>
    </div>
    <div class="a-card">
      <h3>What shoppers pay for shipping</h3>
      <p class="a-sub">A flat fee, or the connected carrier's live rate from your ship-from address to the shopper's. Free-shipping rules apply to both.</p>
      <div id="shipRates"></div>
    </div>
    <div class="a-card">
      <h3>Track Shipment</h3>
      <p class="a-sub">Enter tracking number to see real-time status</p>
      <div class="p-form">
        <input type="text" id="trackNumber" placeholder="Tracking number" style="flex:1">
        <button class="p-btn" id="shTrack">Track</button>
      </div>
      <div id="trackResult"></div>
    </div>
  `;
  return html;
}
function wireShipping() {
  const tr = $("#shTrack"); if (tr) tr.onclick = () => trackShipment();
  loadShippingProviders();
  loadShipFrom();
  loadShipRates();
}

screen("shipping", { render: async () => shippingHtml(), wire: async () => { wireShipping(); } });
screen("pickup", { render: async () => await vPickup(), wire: async () => { wirePickup(); } });
screen("logistics", { render: async () => await vLogistics() });
screen("qcops", { render: async () => await vQcOps(), wire: async () => { wireQcOps(); } });

/* ---------- delivery slots and where the store delivers ---------- */
const WEEKDAYS = () => Array.from({ length: 7 }, (_, i) => new Date(Date.UTC(2023, 0, 1 + i)).toLocaleDateString(undefined, { weekday: "long", timeZone: "UTC" }));
async function vDeliverySlots() {
  const gate = await coGate("deliveryslots");
  if (!gate.any) return coOff("delivery slots", "🗓️ Delivery Slots", gate.off);
  const d = await api("/admin/delivery-windows", {}), days = WEEKDAYS();
  return `<div class="a-head"><h2>🗓️ Delivery Slots</h2><p class="a-sub">Windows repeat each week; a capacity of 0 is no limit. How far ahead shoppers may choose, the cutoff and whether a choice is required are the capability's settings.</p></div>
  <div class="a-card"><div class="p-form"><div class="row"><label><span>Day</span><select id="dwDay">${days.map((n, i) => `<option value="${i}">${esc(n)}</option>`).join("")}</select></label><label><span>From</span><input id="dwFrom" type="time" value="09:00"></label><label><span>To</span><input id="dwTo" type="time" value="12:00"></label><label><span>Deliveries</span><input id="dwCap" type="number" min="0" value="20"></label><label><span>Fee</span><input id="dwFee" type="number" min="0" step="0.01" value="0"></label><button class="p-btn primary" id="dwAdd">Add</button></div></div>
  <div class="a-tablewrap"><table class="a-table"><thead><tr><th>day</th><th>hours</th><th>deliveries</th><th>fee</th><th></th></tr></thead><tbody>${d.windows.map(w => `<tr><td>${esc(days[w.weekday])}</td><td>${esc(w.starts)}–${esc(w.ends)}</td><td>${w.capacity || "no limit"}</td><td>${money(w.fee)}</td><td><button class="btn-white sm" data-dwdel="${w.id}">Remove</button></td></tr>`).join("") || '<tr><td colspan="5">No windows yet.</td></tr>'}</tbody></table></div></div>
  <div class="a-card"><h3>Booked</h3><div class="a-tablewrap"><table class="a-table"><thead><tr><th>day</th><th>hours</th><th>order</th><th>to</th><th>state</th></tr></thead><tbody>${d.schedule.map(b => `<tr><td>${esc(b.day)}</td><td>${esc(b.starts)}–${esc(b.ends)}</td><td>${esc(b.num)}</td><td>${esc([b.name, b.address, b.city, b.zip].filter(Boolean).join(", "))}</td><td>${esc(b.status)}</td></tr>`).join("") || '<tr><td colspan="5">Nothing booked.</td></tr>'}</tbody></table></div></div>`;
}
function wireDeliverySlots() {
  const b = $("#dwAdd"); if (b) b.onclick = () => postAndRender("/admin/delivery-windows", { weekday: Number(fieldVal("#dwDay")), starts: fieldVal("#dwFrom"), ends: fieldVal("#dwTo"), capacity: Number(fieldVal("#dwCap")), fee: Number(fieldVal("#dwFee")) }, "POST", "Window added");
  $$("[data-dwdel]").forEach(x => x.onclick = async () => { try { await api("/admin/delivery-windows/" + x.dataset.dwdel, "DELETE"); render(); } catch (e) { toast(e.message); } });
}
async function vAreas() {
  const gate = await coGate("areas");
  if (!gate.any) return coOff("serviceable areas", "📮 Serviceable Areas", gate.off);
  const d = await api("/admin/serviceable-areas", {});
  return `<div class="a-head"><h2>📮 Serviceable Areas</h2><p class="a-sub">With no area set the store delivers everywhere. List postcodes, beginnings (560*) and ranges (110001-110099), separated by spaces or commas.</p></div>
  <div class="a-card"><div class="p-form"><div class="row"><label><span>Name</span><input id="saName"></label><label><span>Extra fee</span><input id="saFee" type="number" min="0" step="0.01" value="0"></label><label><span>Extra days</span><input id="saDays" type="number" min="0" value="0"></label></div><label><span>Postcodes</span><textarea id="saCodes" rows="3"></textarea></label><button class="p-btn primary" id="saAdd">Add area</button></div>
  <div class="a-tablewrap"><table class="a-table"><thead><tr><th>area</th><th>postcodes</th><th>fee</th><th>days</th><th></th></tr></thead><tbody>${d.areas.map(a => `<tr><td>${esc(a.name)}</td><td>${esc(a.postcodes.length > 120 ? a.postcodes.slice(0, 120) + "…" : a.postcodes)}</td><td>${money(a.fee)}</td><td>+${a.extra_days}</td><td><button class="btn-white sm" data-sadel="${a.id}">Remove</button></td></tr>`).join("") || '<tr><td colspan="5">No areas: the store delivers everywhere.</td></tr>'}</tbody></table></div></div>`;
}
function wireAreas() {
  const b = $("#saAdd"); if (b) b.onclick = () => postAndRender("/admin/serviceable-areas", { name: fieldVal("#saName"), postcodes: fieldVal("#saCodes"), fee: Number(fieldVal("#saFee")), extra_days: Number(fieldVal("#saDays")) }, "POST", "Area added");
  $$("[data-sadel]").forEach(x => x.onclick = async () => { try { await api("/admin/serviceable-areas/" + x.dataset.sadel, "DELETE"); render(); } catch (e) { toast(e.message); } });
}
screen("deliveryslots", { render: async () => await vDeliverySlots(), wire: async () => { wireDeliverySlots(); } });
screen("areas", { render: async () => await vAreas(), wire: async () => { wireAreas(); } });
