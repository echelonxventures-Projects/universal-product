/* LUXORA Platform — the services domain's store-console screens (_registry/business-domains.json).
   Loaded after the console shell (public/js/admin.js) in its scope; each screen registers its
   render, its wiring and its place in the nav. */
"use strict";

/* ---------- live sessions (lib/media-sessions.js) ---------- */
async function vSessions() {
  const gate = await coGate("sessions");
  if (!gate.any) return coOff("live sessions", "🎥 Live Sessions", gate.off);
  const d = await api("/sessions", {}).catch(e => ({ sessions: [], error: e.message }));
  return `<div class="a-head"><h2>🎥 Live Sessions</h2><p class="a-sub">Booked consultations, classes and calls held live. Carried by ${esc(((d.transports || []).find(t => t.builtin) || {}).name || "the platform")} unless the <code>media_sessions</code> capability names a media connector from the Provider Registry; charged by the minute where <code>per_minute_billing</code> is on (⏱️ Per-minute Charges).</p></div>
  <div class="a-card"><div class="a-tablewrap"><table class="a-table"><thead><tr><th>#</th><th>guest</th><th>mode</th><th>state</th><th>minutes</th><th>charged</th><th></th></tr></thead><tbody>
  ${(d.sessions || []).map(x => `<tr><td>${x.id}</td><td>${esc(x.guest)}</td><td>${esc(x.mode)}</td><td>${stateChip(x.state)}</td><td>${(x.seconds / 60).toFixed(1)}</td><td>${x.charged ? money(x.charged) : ""}</td>
    <td>${x.done ? "" : `<a class="btn-white sm" href="${esc(x.join_url)}" target="_blank" rel="noopener">Join</a>`}</td></tr>`).join("") || `<tr><td colspan="7">${esc(d.error || "No sessions yet.")}</td></tr>`}</tbody></table></div></div>`;
}
/* ---------- charged by the minute (capability per_minute_billing) ---------- */
async function vMetering() {
  const gate = await coGate("metering");
  if (!gate.any) return coOff("charging by the minute", "⏱️ Per-minute Charges", gate.off);
  const d = await api("/admin/per-minute", {}).catch(e => ({ error: e.message }));
  if (d.error) return `<div class="a-head"><h2>⏱️ Per-minute Charges</h2><p class="a-sub">${esc(d.error)}</p></div>`;
  const P = d.settings || {};
  return `<div class="a-head"><h2>⏱️ Per-minute Charges</h2><p class="a-sub">Live sessions charged to the guest's wallet at the item's price per minute, else ${money(P.default_rate)} a minute, in steps of ${esc(P.increment_seconds)} seconds with ${esc(P.minimum_minutes)} minute(s) always charged — the <code>per_minute_billing</code> capability's params. Charged so far: <b>${money(d.total)}</b>.</p></div>
  <div class="a-card"><div class="a-tablewrap"><table class="a-table"><thead><tr><th>#</th><th>guest</th><th>rate / min</th><th>state</th><th>minutes</th><th>charged</th></tr></thead><tbody>
  ${(d.sessions || []).map(x => `<tr><td>${x.id}</td><td>${esc(x.guest)}</td><td>${money(x.rate)}</td><td>${stateChip(x.state)}</td><td>${(x.seconds / 60).toFixed(1)}</td><td>${x.charged ? money(x.charged) : ""}</td></tr>`).join("") || '<tr><td colspan="6">No sessions charged by the minute yet.</td></tr>'}</tbody></table></div></div>`;
}
async function vBookings() {
  const gate = await coGate("bookings");
  if (!gate.any) return coOff("bookings", "📅 Bookings", gate.off);
  const from = new Date(Date.now() - 864e5).toISOString().slice(0, 19).replace("T", " "), to = new Date(Date.now() + 30 * 864e5).toISOString().slice(0, 19).replace("T", " ");
  const d = await api("/admin/bookings", { from, to });
  const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const hoursText = h => Object.entries(h || {}).map(([k, rs]) => days[k] + " " + rs.map(r => r.join("-")).join(", ")).join("; ");
  return `<div class="a-head"><h2>📅 Bookings</h2><p class="a-sub">Appointments, stays, rentals and experiences. Resource kinds and booking modes are the <code>bookingResourceKinds</code> and <code>bookingModes</code> registries; holding time and cancellation cut-off are the <code>bookings</code> capability's params.</p></div>
  <div class="a-card"><h3>Resource</h3><div class="p-form"><div class="row"><label><span>Code *</span><input id="brCode"></label><label><span>Name *</span><input id="brName"></label>
    <label><span>Kind</span><select id="brKind">${(d.resourceKinds || []).map(k => `<option value="${esc(k.key)}">${esc(k.name)}</option>`).join("")}</select></label><label><span>Capacity</span><input id="brCap" type="number" min="1" value="1"></label></div>
    <div class="row"><label><span>Time zone (blank: the store's)</span><input id="brTz" placeholder="e.g. Asia/Kolkata"></label></div>
    <label><span>Weekly hours — one line per day: weekday 0 (Sunday)–6, then HH:MM-HH:MM, …</span><textarea id="brHours" rows="3" placeholder="1 09:00-13:00, 14:00-18:00"></textarea></label>
    <button class="p-btn primary" id="brSave">Save resource</button></div>
    <div class="a-tablewrap"><table class="a-table"><thead><tr><th>code</th><th>name</th><th>kind</th><th>capacity</th><th>zone</th><th>hours</th></tr></thead><tbody>${(d.resources || []).map(r => `<tr><td><code>${esc(r.code)}</code></td><td>${esc(r.name)}</td><td>${esc(r.kind_row ? r.kind_row.name : r.kind)}</td><td>${r.capacity}</td><td>${esc(r.tz || "store")}</td><td>${esc(hoursText(r.hours))}</td></tr>`).join("") || '<tr><td colspan="6">No resources yet.</td></tr>'}</tbody></table></div></div>
  <div class="a-card"><h3>Make a product bookable</h3><div class="p-form"><div class="row"><label><span>Product id *</span><input id="bpProd"></label>
    <label><span>Mode</span><select id="bpMode">${(d.modes || []).map(m => `<option value="${esc(m.key)}">${esc(m.name)}</option>`).join("")}</select></label></div>
    <div>${(d.resources || []).map(r => `<label style="display:inline-block;margin-right:12px"><input type="checkbox" data-bp-res="${r.id}"> ${esc(r.name)}</label>`).join("")}</div>
    <div class="row"><label><span>Length (min)</span><input id="bpDur" type="number" value="60"></label><label><span>Every (min)</span><input id="bpStep" type="number" value="60"></label><label><span>Gap after (min)</span><input id="bpBuf" type="number" value="0"></label><label><span>Notice (hours)</span><input id="bpLead" type="number" value="0"></label></div>
    <div class="row"><label><span>Fewest days</span><input id="bpMin" type="number" value="1"></label><label><span>Most days</span><input id="bpMax" type="number" value="30"></label></div>
    <button class="p-btn primary" id="bpSave">Save</button></div></div>
  <div class="a-card"><h3>Next 30 days</h3><div class="a-tablewrap"><table class="a-table"><thead><tr><th>ref</th><th>when</th><th>product</th><th>state</th><th></th></tr></thead><tbody>
    ${(d.bookings || []).map(b => `<tr><td><code>${esc(b.ref)}</code></td><td>${esc(b.label)}</td><td><code>${esc(b.product_id)}</code></td><td>${stateChip(b.state)}</td><td style="white-space:nowrap">${verbRow(d.actions, b, "/admin/bookings/" + b.id)}</td></tr>`).join("") || '<tr><td colspan="5">Nothing booked.</td></tr>'}</tbody></table></div>
    <button class="btn-white sm" data-co-post="/admin/bookings/sweep">Expire lapsed holds now</button></div>`;
}
function wireBookings() {
  const s = $("#brSave"); if (!s) return;
  s.onclick = () => {
    const hours = {};
    fieldVal("#brHours").split(/\n/).map(l => l.trim()).filter(Boolean).forEach(l => { const m = /^([0-6])\s+(.+)$/.exec(l); if (m) hours[m[1]] = m[2].split(",").map(x => x.trim().split("-")); });
    postAndRender("/admin/bookings/resources", { code: fieldVal("#brCode"), name: fieldVal("#brName"), kind: fieldVal("#brKind"), capacity: fieldVal("#brCap"), tz: fieldVal("#brTz"), hours }, "POST", "Resource saved");
  };
  $("#bpSave").onclick = () => postAndRender("/admin/bookings/products/" + encodeURIComponent(fieldVal("#bpProd").trim()), { mode: fieldVal("#bpMode"), resource_ids: $$("[data-bp-res]").filter(c => c.checked).map(c => Number(c.dataset.bpRes)),
    duration_min: fieldVal("#bpDur"), step_min: fieldVal("#bpStep"), buffer_min: fieldVal("#bpBuf"), lead_hours: fieldVal("#bpLead"), min_units: fieldVal("#bpMin"), max_units: fieldVal("#bpMax") }, "PUT", "Product is bookable");
  wireCoPosts();
}

screen("bookings", { render: async () => await vBookings(), wire: async () => { wireBookings(); } });
screen("sessions", { render: async () => await vSessions() });
screen("metering", { render: async () => await vMetering() });
screen("installations", { render: view => vProdOptions(view), wire: () => wireProdOptions() });
screen("assemblies", { render: view => vProdOptions(view), wire: () => wireProdOptions() });
screen("warranties", { render: view => vProdOptions(view), wire: () => wireProdOptions() });
