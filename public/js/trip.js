/* LUXORA Platform — a ride someone shared, followed from their private link (lib/trips.js sharedView):
   the ride's progress, the driver's first name and car, and the live position, refreshed while the
   ride is under way. No sign-in; the link closes a while after the ride. */
"use strict";
(() => {
  const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const token = new URLSearchParams(location.search).get("t") || "", page = document.getElementById("page");
  const when = s => { const d = new Date(String(s || "").replace(" ", "T") + "Z"); return isNaN(d) ? "" : d.toLocaleTimeString(undefined, { timeStyle: "short" }); };
  /* the pickup, the drop, the track and the driver, drawn to scale (no map tiles) */
  const map = tr => {
    const pts = [tr.pickup, tr.dropoff, tr.driver, ...(tr.points || [])].filter(p => p && isFinite(p.lat) && isFinite(p.lng));
    if (!pts.length) return "";
    const lat0 = pts.reduce((s, p) => s + p.lat, 0) / pts.length, kx = Math.cos(lat0 * Math.PI / 180), xy = p => [p.lng * kx, -p.lat];
    const xs = pts.map(p => xy(p)[0]), ys = pts.map(p => xy(p)[1]), W = 320, H = 220;
    const span = Math.max(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys), 0.004), pad = span * 0.15;
    const cx = (Math.min(...xs) + Math.max(...xs)) / 2, cy = (Math.min(...ys) + Math.max(...ys)) / 2, k = Math.min(W, H) / (span + 2 * pad);
    const P = p => { const [x, y] = xy(p); return [(W / 2 + (x - cx) * k).toFixed(1), (H / 2 + (y - cy) * k).toFixed(1)]; };
    const dot = (p, c, t) => p ? `<circle class="${c}" cx="${P(p)[0]}" cy="${P(p)[1]}" r="7"><title>${t}</title></circle>` : "";
    const line = (tr.points || []).map(p => P(p).join(",")).join(" ");
    return `<figure class="ride-map"><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Map of the ride"><rect width="${W}" height="${H}" class="ride-map-bg"/>${line ? `<polyline points="${line}" class="ride-map-track"/>` : ""}${dot(tr.pickup, "ride-map-pick", "Pickup")}${dot(tr.dropoff, "ride-map-drop", "Drop")}${dot(tr.driver, "ride-map-car", "Driver")}</svg>
      <figcaption>● green pickup · ● red drop · ● blue driver${tr.driver ? " (updated " + when(tr.driver.at) + ")" : ""}</figcaption></figure>`;
  };
  const show = t => {
    document.title = (t.rider ? t.rider + "'s ride" : "A shared ride") + (t.store ? " — " + t.store : "");
    page.innerHTML = `<section class="ride-card"><p class="pay-meta">${esc(t.store)} · ${esc(t.ref)}</p><h1>${esc(t.rider || "A rider")}'s ride: ${esc(t.label)}</h1>
      <p>${esc(t.pickup)} → ${esc(t.dropoff)}</p>
      ${t.driver ? `<p>Driver <b>${esc(t.driver.name)}</b> · ${esc(t.driver.vehicle_kind)} <b class="ride-plate">${esc(t.driver.plate)}</b> · ${(+t.driver.rating).toFixed(1)} ★</p>` : "<p>Waiting for a driver.</p>"}
      ${t.track && t.track.eta_min ? `<p>About <b>${esc(t.track.eta_min)} min</b> to go.</p>` : ""}${t.ended ? `<p role="status"><b>${t.done ? "The ride has ended." : "The ride was cancelled."}</b></p>` : ""}
      ${map(t.track || {})}</section>`;
  };
  const load = async () => {
    const r = await fetch("/api/trips/shared?t=" + encodeURIComponent(token), { credentials: "same-origin" });
    const d = await r.json().catch(() => ({}));
    if (!r.ok) { page.innerHTML = `<h1>${r.status === 410 ? "This ride is over" : "This link is not valid"}</h1><p>${r.status === 410 ? "The link closed after the ride ended." : "It may have been copied incompletely. Ask whoever sent it for the link again."}</p>`; return; }
    show(d.trip);
    if (!d.trip.ended) setTimeout(load, 10000);
  };
  load();
})();
