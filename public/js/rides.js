/* LUXORA Platform — the rider's and the driver's pages of the storefront (lib/trips.js, lib/mobility.js).
   ride.html: ask for a ride now, share one, or book one for later; follow the driver on the map; share
   the trip; the emergency button; cancel, rate and tip. drive.html: go online, report the position while
   online, move each ride on, rate riders, report, and see what was earned. Loaded before the storefront
   shell (public/js/app.js), which calls these pages by the page key the HTML declares. Every state,
   step and permission shown is what the server answered. */
"use strict";
(function () {
  const RX = {};
  const h = s => esc(s);
  const fmtWhen = s => { if (!s) return ""; const d = new Date(String(s).replace(" ", "T") + (/[zZ]$/.test(s) ? "" : "Z")); return isNaN(d) ? h(s) : h(d.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" })); };
  const stars = (name, label) => `<fieldset class="ride-stars"><legend>${h(label)}</legend>${[1, 2, 3, 4, 5].map(n => `<label><input type="radio" name="${name}" value="${n}"${n === 5 ? " checked" : ""}> ${"★".repeat(n)}</label>`).join("")}</fieldset>`;
  const tagBoxes = (name, tags) => `<fieldset class="ride-tags"><legend>What stood out</legend>${tags.map(t => `<label><input type="checkbox" name="${name}" value="${h(t)}"> ${h(t)}</label>`).join("")}</fieldset>`;
  const picked = name => [...document.querySelectorAll(`input[name="${name}"]:checked`)].map(x => x.value);
  const fail = e => toast("⚠️ " + h(e.message || e));
  let timer = null;
  /* the page refreshes itself, except while someone is typing or has a form open */
  const busy = () => { const a = document.activeElement; return (a && /^(INPUT|TEXTAREA|SELECT)$/.test(a.tagName)) || !!document.querySelector("#page details[open]"); };
  const every = (ms, fn) => { clearTimeout(timer); timer = setTimeout(async () => { if (document.visibilityState !== "hidden" && !busy()) await fn(); every(ms, fn); }, ms); };

  /* ---------- a small map: the pickup, the drop, the track and the driver, drawn to scale (no map tiles) ---------- */
  function mapSvg(tr) {
    if (!tr) return "";
    const pts = [tr.pickup, tr.dropoff, tr.driver, ...(tr.points || [])].filter(p => p && isFinite(p.lat) && isFinite(p.lng));
    if (!pts.length) return `<p class="pay-meta">The map appears once the pickup or the driver's position is known.</p>`;
    const lat0 = pts.reduce((s, p) => s + p.lat, 0) / pts.length, kx = Math.cos(lat0 * Math.PI / 180);
    const xy = p => [p.lng * kx, -p.lat];
    const xs = pts.map(p => xy(p)[0]), ys = pts.map(p => xy(p)[1]);
    let [x0, x1, y0, y1] = [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)];
    const span = Math.max(x1 - x0, y1 - y0, 0.004), pad = span * 0.15, W = 320, H = 220;
    const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2, s = Math.min(W, H) / (span + 2 * pad);
    const P = p => { const [x, y] = xy(p); return [(W / 2 + (x - cx) * s).toFixed(1), (H / 2 + (y - cy) * s).toFixed(1)]; };
    const line = (tr.points || []).map(p => P(p).join(",")).join(" ");
    const dot = (p, cls, label) => p ? (() => { const [x, y] = P(p); return `<circle class="${cls}" cx="${x}" cy="${y}" r="7"><title>${h(label)}</title></circle>`; })() : "";
    const km = (span * 111).toFixed(span * 111 < 2 ? 1 : 0);
    return `<figure class="ride-map"><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Map of the ride: pickup, drop${tr.driver ? " and the driver's position" : ""}">
      <rect x="0" y="0" width="${W}" height="${H}" class="ride-map-bg"/>${line ? `<polyline points="${line}" class="ride-map-track"/>` : ""}
      ${dot(tr.pickup, "ride-map-pick", "Pickup")}${dot(tr.dropoff, "ride-map-drop", "Drop")}${dot(tr.driver, "ride-map-car", "Driver")}</svg>
      <figcaption class="pay-meta">● green pickup · ● red drop · ● blue driver${tr.driver ? " (updated " + fmtWhen(tr.driver.at) + ")" : ""} · about ${km} km across</figcaption></figure>`;
  }
  const where = () => new Promise(ok => { if (!navigator.geolocation) return ok(null); navigator.geolocation.getCurrentPosition(p => ok({ lat: +p.coords.latitude.toFixed(6), lng: +p.coords.longitude.toFixed(6) }), () => ok(null), { enableHighAccuracy: true, timeout: 8000, maximumAge: 30000 }); });

  /* ============================== the rider ============================== */
  async function pageRide() {
    const main = $("#page");
    document.title = `Rides — ${CFG.brand.name}`;
    if (!S.user) { main.innerHTML = `<div class="reg"><div class="reg-hero"><h1>Rides</h1><p>Sign in to ask for a ride, book one for later or follow your driver.</p><button class="btn-yellow" data-act="signin-open">Sign in</button></div></div>`; return; }
    let d;
    try { d = await api("/rides"); } catch (e) { main.innerHTML = `<div class="r-empty"><h3>${h(e.message)}</h3></div>`; return; }
    RX.d = d;
    const placeList = `<datalist id="rdPlaces">${d.places.map(p => `<option value="${h(p.name)}"></option>`).join("")}</datalist>`;
    const kinds = d.kinds.map(k => `<option value="${h(k.key)}">${h(k.name || k.key)} · seats ${h(k.capacity || "")}</option>`).join("");
    const minAt = new Date(Date.now() + (d.schedule.minLeadMinutes + 5) * 60000), local = x => new Date(x - x.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
    main.innerHTML = `<div class="ride-wrap">
      <h1>Rides</h1>${d.me.rating ? `<p class="pay-meta">Your rating from drivers: ${d.me.rating.stars.toFixed(2)} ★ (${d.me.rating.count})</p>` : ""}
      <div id="rdActive">${d.active.map(rideCard).join("")}</div>
      ${d.active.length ? "" : `<section class="ride-card"><h2>Where to?</h2>${placeList}
        <form id="rdForm" class="ride-form">
          <label>From <input id="rdFrom" list="rdPlaces" maxlength="200" required autocomplete="off"></label>
          <p><button type="button" class="btn-white sm" id="rdHere">Use my location</button> <span class="pay-meta" id="rdHereMsg"></span></p>
          <label>To <input id="rdTo" list="rdPlaces" maxlength="200" required autocomplete="off"></label>
          <label>Vehicle <select id="rdKind">${kinds}</select></label>
          <label>Seats <input id="rdSeats" type="number" min="1" max="8" value="1"></label>
          <label>Pay by <select id="rdPay"><option value="cash">Cash</option><option value="card">Card</option><option value="wallet">Wallet</option><option value="upi">UPI</option></select></label>
          <label>Your phone, for the driver (optional) <input id="rdPhone" type="tel" maxlength="40" autocomplete="tel"></label>
          <label class="ride-check"><input id="rdPool" type="checkbox"> Share the ride with others going the same way (${h(d.poolDiscountPct)}% off)</label>
          <label class="ride-check"><input id="rdLater" type="checkbox"> Book for later</label>
          <label id="rdWhenRow" hidden>Pick me up at <input id="rdWhen" type="datetime-local" min="${local(minAt)}" value="${local(minAt)}"></label>
          <p id="rdQuote" class="pay-meta" aria-live="polite"></p>
          <p><button type="button" class="btn-white" id="rdEstimate">See the price</button> <button type="submit" class="btn-yellow" id="rdGo">Ask for a ride</button></p>
        </form></section>`}
      ${d.bookings.length ? `<section class="ride-card"><h2>Booked for later</h2>${d.bookings.map(b => `<div class="ride-row"><div><b>${fmtWhen(b.pickup_at)}</b> · ${h(b.pickup)} → ${h(b.dropoff)}<div class="pay-meta">${h(b.ref)} · ${h(b.vehicle_kind)} · ${h(b.status)}${b.estimate ? " · about " + money(b.estimate) : ""}</div></div>${b.waiting ? `<button class="btn-white sm" data-rd-bc="${b.id}">Cancel</button>` : ""}</div>`).join("")}</section>` : ""}
      ${d.past.length ? `<section class="ride-card"><h2>Past rides</h2>${d.past.map(pastCard).join("")}</section>` : ""}
      <p class="pay-meta">In an emergency call <b>${h(d.safety.emergency)}</b>.</p></div>`;
    wireRide();
    if (d.active.length) every(5000, refreshActive);
  }
  const coordsOf = name => { const p = (RX.d.places || []).find(x => x.name.toLowerCase() === String(name || "").trim().toLowerCase()); return p ? { lat: p.lat, lng: p.lng } : null; };
  function rideInput() {
    const from = $("#rdFrom").value, to = $("#rdTo").value;
    const a = (RX.here && from === RX.hereLabel) ? RX.here : coordsOf(from), b = coordsOf(to);
    return { pickup: from, dropoff: to, pickup_lat: a ? a.lat : undefined, pickup_lng: a ? a.lng : undefined, dropoff_lat: b ? b.lat : undefined, dropoff_lng: b ? b.lng : undefined,
      vehicle_kind: $("#rdKind").value, seats: Number($("#rdSeats").value) || 1, payment_method: $("#rdPay").value, rider_phone: $("#rdPhone").value, pool: $("#rdPool").checked };
  }
  function rideCard(r) {
    const c = r.can;
    return `<section class="ride-card ride-live" data-ride="${r.id}"><h2>${h(r.label)}</h2>
      <p>${h(r.pickup)} → ${h(r.dropoff)}${r.pool ? ` · <span class="a-chip">shared · ${h(r.pool.riders)} riders</span>` : ""}</p>
      ${r.driver ? `<p><b>${h(r.driver.name)}</b> · ${h(r.driver.vehicle_kind)} <b class="ride-plate">${h(r.driver.plate)}</b> · ${(+r.driver.rating).toFixed(1)} ★${r.driver.phone ? ` · <a href="tel:${h(r.driver.phone)}">Call</a>` : ""}</p>` : `<p class="pay-meta">Finding you a driver…</p>`}
      ${r.track && r.track.eta_min ? `<p>About <b>${h(r.track.eta_min)} min</b> ${r.on_board ? "to your drop" : "away"}</p>` : r.eta_min ? `<p>About <b>${h(r.eta_min)} min</b> away</p>` : ""}
      ${mapSvg(r.track)}
      <p class="ride-actions">${c.sos ? `<button class="ride-sos" data-rd-sos="${r.id}">🚨 Emergency</button>` : ""}
        ${c.share ? `<button class="btn-white sm" data-rd-share="${r.id}">Share my trip</button>` : ""}
        ${c.cancel ? `<button class="btn-white sm" data-rd-cancel="${r.id}">Cancel ride</button>` : ""}</p>
      <p class="pay-meta" id="rdShare${r.id}" aria-live="polite"></p></section>`;
  }
  function pastCard(r) {
    const c = r.can, d = RX.d;
    return `<div class="ride-past"><div><b>${fmtWhen(r.completed_at || r.cancelled_at || r.requested_at)}</b> · ${h(r.pickup)} → ${h(r.dropoff)}
      <div class="pay-meta">${h(r.ref)} · ${h(r.label)}${r.fare ? " · " + money(r.fare) : ""}${r.tip ? " + tip " + money(r.tip) : ""}${r.distance_km ? " · " + (+r.distance_km).toFixed(1) + " km" : ""}${r.driver ? " · " + h(r.driver.name) : ""}${r.ratings.rider ? " · you gave " + "★".repeat(r.ratings.rider.stars) : ""}</div></div>
      ${c.rate ? `<details><summary>Rate ${h(r.driver ? r.driver.name : "the driver")}</summary><form data-rd-rate="${r.id}">${stars("st" + r.id, "Stars")}${tagBoxes("tg" + r.id, [...d.ratings.riderTags, ...d.ratings.lowTags])}<label>Anything else (optional) <input name="cm" maxlength="500"></label><button class="btn-yellow sm">Send rating</button></form></details>` : ""}
      ${c.tip ? `<details><summary>Add a tip</summary><p>${d.tips.choices.map(a => `<button class="btn-white sm" data-rd-tip="${r.id}:${a}">${money(a)}</button>`).join(" ")} <label>Other <input type="number" min="0.01" max="${h(d.tips.max)}" step="0.01" id="rdTip${r.id}"></label> <button class="btn-white sm" data-rd-tipo="${r.id}">Tip</button></p></details>` : ""}
      ${c.report ? `<details><summary>Report a problem</summary><form data-rd-rep="${r.id}"><label>What happened <select name="kind">${d.safety.kinds.filter(k => !k.urgent).map(k => `<option value="${h(k.key)}">${h(k.label)}</option>`).join("")}</select></label><label>Tell us more <textarea name="note" maxlength="1000" required></textarea></label><button class="btn-white sm">Send</button></form></details>` : ""}</div>`;
  }
  async function refreshActive() {
    for (const el of document.querySelectorAll("[data-ride]")) {
      try {
        const r = (await api("/rides/" + el.dataset.ride)).ride;
        if (!r.track) { pageRide(); return; }
        const share = $("#rdShare" + r.id) ? $("#rdShare" + r.id).innerHTML : "";
        el.outerHTML = rideCard(r); if (share) $("#rdShare" + r.id).innerHTML = share;
        wireRide();
      } catch (e) { }
    }
  }
  function wireRide() {
    const on = (sel, fn) => document.querySelectorAll(sel).forEach(x => x.onclick = e => { e.preventDefault(); fn(x); });
    const sub = (sel, fn) => document.querySelectorAll(sel).forEach(x => x.onsubmit = e => { e.preventDefault(); fn(x); });
    const later = $("#rdLater"); if (later) later.onchange = () => { $("#rdWhenRow").hidden = !later.checked; $("#rdGo").textContent = later.checked ? "Book this ride" : "Ask for a ride"; };
    const here = $("#rdHere"); if (here) here.onclick = async () => {
      $("#rdHereMsg").textContent = "Finding you…"; const p = await where();
      if (!p) { $("#rdHereMsg").textContent = "Your position is not available — type the pickup instead."; return; }
      RX.here = p; RX.hereLabel = "My location (" + p.lat.toFixed(4) + ", " + p.lng.toFixed(4) + ")"; $("#rdFrom").value = RX.hereLabel; $("#rdHereMsg").textContent = "";
    };
    const est = $("#rdEstimate"); if (est) est.onclick = async () => {
      try { const e = (await api("/rides/estimate", "POST", rideInput())).estimate;
        $("#rdQuote").innerHTML = e.fare == null ? "The fare is worked out from the trip's distance and time — pick named places or your location for a price now."
          : `About <b>${money(e.fare)}</b> · ${h(e.distance_km)} km · ${h(e.duration_min)} min${e.surge > 1 ? ` · busy-time price ×${h(e.surge)}` : ""}${e.pool ? " · shared" : ""}`; } catch (e) { fail(e); }
    };
    const f = $("#rdForm"); if (f) f.onsubmit = async e => {
      e.preventDefault(); $("#rdGo").disabled = true;
      try {
        if ($("#rdLater").checked) { await api("/rides/bookings", "POST", { ...rideInput(), pool: false, pickup_at: new Date($("#rdWhen").value).toISOString() }); toast("Booked"); }
        else await api("/rides", "POST", rideInput());
        pageRide();
      } catch (x) { fail(x); $("#rdGo").disabled = false; }
    };
    on("[data-rd-cancel]", async x => { if (!confirm("Cancel this ride? A cancellation fee may apply once a driver is on the way.")) return; try { await api(`/rides/${x.dataset.rdCancel}/cancel`, "POST", {}); pageRide(); } catch (e) { fail(e); } });
    on("[data-rd-bc]", async x => { if (!confirm("Cancel this booking?")) return; try { await api(`/rides/bookings/${x.dataset.rdBc}/cancel`, "POST", {}); pageRide(); } catch (e) { fail(e); } });
    on("[data-rd-share]", async x => {
      try { const s = await api(`/rides/${x.dataset.rdShare}/share`, "POST", {}), out = $("#rdShare" + x.dataset.rdShare), link = new URL(s.link, location.href).href;
        if (navigator.share) { try { await navigator.share({ title: "Follow my ride", url: link }); } catch (e) { } }
        out.innerHTML = `Send this link to someone you trust: <a href="${h(link)}">${h(link)}</a>`;
        try { await navigator.clipboard.writeText(link); out.innerHTML += " (copied)"; } catch (e) { } } catch (e) { fail(e); }
    });
    on("[data-rd-sos]", async x => {
      if (!confirm(`Raise an emergency? The store is alerted at once with where you are. If you are in danger, also call ${RX.d.safety.emergency}.`)) return;
      const p = await where();
      try { const r = (await api(`/rides/${x.dataset.rdSos}/safety`, "POST", { kind: "sos", lat: p && p.lat, lng: p && p.lng })).report;
        dynModal("Help is on the way", `<p role="alert">The store has your emergency (<b>${h(r.ref)}</b>) and where you are.</p><p>If you are in danger, call <a class="btn-yellow" href="tel:${h(r.emergency)}">${h(r.emergency)}</a> now.</p>`); } catch (e) { fail(e); }
    });
    sub("[data-rd-rate]", async x => { const id = x.dataset.rdRate; try { await api(`/rides/${id}/rate`, "POST", { stars: Number(picked("st" + id)[0]), tags: picked("tg" + id), comment: x.cm.value }); toast("Thanks for rating"); pageRide(); } catch (e) { fail(e); } });
    on("[data-rd-tip]", async x => { const [id, a] = x.dataset.rdTip.split(":"); try { await api(`/rides/${id}/tip`, "POST", { amount: Number(a) }); toast("Thank you — your driver gets all of it"); pageRide(); } catch (e) { fail(e); } });
    on("[data-rd-tipo]", async x => { const id = x.dataset.rdTipo; try { await api(`/rides/${id}/tip`, "POST", { amount: Number($("#rdTip" + id).value) }); toast("Thank you"); pageRide(); } catch (e) { fail(e); } });
    sub("[data-rd-rep]", async x => { try { const r = (await api(`/rides/${x.dataset.rdRep}/safety`, "POST", { kind: x.kind.value, note: x.note.value })).report; toast("Reported — " + h(r.ref)); pageRide(); } catch (e) { fail(e); } });
  }

  /* ============================== the driver ============================== */
  let watch = null, lastSent = 0;
  function track(online) {
    if (!navigator.geolocation) return;
    if (!online) { if (watch != null) navigator.geolocation.clearWatch(watch); watch = null; return; }
    if (watch != null) return;
    watch = navigator.geolocation.watchPosition(p => {
      if (Date.now() - lastSent < 5000) return; lastSent = Date.now();
      api("/drive/position", "POST", { lat: +p.coords.latitude.toFixed(6), lng: +p.coords.longitude.toFixed(6) }).then(() => { const m = $("#dvPos"); if (m) m.textContent = "Position sent " + new Date().toLocaleTimeString(); }).catch(() => { });
    }, () => { const m = $("#dvPos"); if (m) m.textContent = "Your position is not available — riders cannot see you on the map and you are matched by your area."; }, { enableHighAccuracy: true, maximumAge: 5000, timeout: 20000 });
  }
  async function pageDrive() {
    const main = $("#page");
    document.title = `Drive — ${CFG.brand.name}`;
    if (!S.user) { main.innerHTML = `<div class="reg"><div class="reg-hero"><h1>Drive</h1><p>Sign in with the email the store has for you as a driver.</p><button class="btn-yellow" data-act="signin-open">Sign in</button></div></div>`; return; }
    let d;
    try { d = await api("/drive"); } catch (e) { main.innerHTML = `<div class="r-empty"><h3>${h(e.message)}</h3><p>Ask the store to add you to its fleet with the email you sign in with.</p></div>`; return; }
    RX.dv = d; track(d.me.online);
    const t = d.today;
    main.innerHTML = `<div class="ride-wrap"><h1>Drive</h1>
      <section class="ride-card"><h2>${h(d.me.name)} · ${h(d.me.vehicle_kind)} <span class="ride-plate">${h(d.me.plate || "")}</span></h2>
        <p>${(+d.me.rating).toFixed(2)} ★ from ${h(d.me.rating_count)} ratings${d.me.review ? ` · <b>held for review — the store will contact you before you get new rides</b>` : ""}</p>
        <p><button class="${d.me.online ? "btn-white" : "btn-yellow"}" id="dvOnline">${d.me.online ? "Go offline" : "Go online"}</button> <span class="pay-meta" id="dvPos" aria-live="polite">${d.me.online ? "You are online." : "You are offline."}</span></p>
        <p class="pay-meta">Today: ${h(t.trips)} trips · earned ${money(t.net)}${t.tips ? " (tips " + money(t.tips) + ")" : ""} · <a href="#" id="dvEarn">Earnings</a></p></section>
      ${d.active.map(driverCard).join("") || (d.me.online ? `<section class="ride-card"><p>Waiting for a ride…</p></section>` : "")}
      ${d.recent.length ? `<section class="ride-card"><h2>Recent rides</h2>${d.recent.map(recentCard).join("")}</section>` : ""}
      <div id="dvEarnings"></div>
      <p class="pay-meta">In an emergency call <b>${h(d.safety.emergency)}</b>.</p></div>`;
    wireDrive();
    if (d.me.online) every(5000, pageDrive);
  }
  function driverCard(r) {
    return `<section class="ride-card ride-live"><h2>${h(r.label)}</h2>
      <p><b>${h(r.rider)}</b>${r.rider_rating ? ` · ${r.rider_rating.stars.toFixed(1)} ★` : ""}${r.seats > 1 ? ` · ${h(r.seats)} seats` : ""}${r.pool_id ? ` · <span class="a-chip">shared ride</span>` : ""}${r.rider_phone ? ` · <a href="tel:${h(r.rider_phone)}">Call</a>` : ""}</p>
      <p>${h(r.pickup)} → ${h(r.dropoff)} · pays by ${h(r.payment_method)}</p>${mapSvg(r.track)}
      <p class="ride-actions">${r.next.map(m => `<button class="btn-yellow" data-dv-move="${r.id}:${h(m.to)}">${h(m.label)}</button>`).join(" ")}
        ${r.canCancel ? `<button class="btn-white sm" data-dv-cancel="${r.id}">Cancel ride</button>` : ""} <button class="ride-sos" data-dv-sos="${r.id}">🚨 Emergency</button></p></section>`;
  }
  function recentCard(r) {
    const d = RX.dv;
    return `<div class="ride-past"><div>${h(r.pickup)} → ${h(r.dropoff)}<div class="pay-meta">${h(r.ref)} · ${h(r.label)}${r.fare ? " · fare " + money(r.fare) + " · you keep " + money(r.fare - r.take + r.tip) : ""}${r.rated ? " · you gave " + "★".repeat(r.rated.stars) : ""}</div></div>
      ${r.canRate ? `<details><summary>Rate ${h(r.rider)}</summary><form data-dv-rate="${r.id}">${stars("ds" + r.id, "Stars")}${tagBoxes("dt" + r.id, [...d.ratings.driverTags, ...d.ratings.lowTags])}<label>Anything else (optional) <input name="cm" maxlength="500"></label><button class="btn-yellow sm">Send rating</button></form></details>` : ""}
      <details><summary>Report a problem</summary><form data-dv-rep="${r.id}"><label>What happened <select name="kind">${d.safety.kinds.filter(k => !k.urgent).map(k => `<option value="${h(k.key)}">${h(k.label)}</option>`).join("")}</select></label><label>Tell us more <textarea name="note" maxlength="1000" required></textarea></label><button class="btn-white sm">Send</button></form></details></div>`;
  }
  async function showEarnings() {
    const to = new Date().toISOString().slice(0, 10), from = new Date(Date.now() - 13 * 86400000).toISOString().slice(0, 10);
    try {
      const s = await api(`/drive/earnings?from=${from}&to=${to}`), t = s.totals;
      $("#dvEarnings").innerHTML = `<section class="ride-card"><h2>Earnings, ${h(from)} to ${h(to)}</h2>
        <p>${h(t.trips)} trips · fares ${money(t.fares)} · platform ${money(t.take)} · tips ${money(t.tips)} · <b>you earned ${money(t.net)}</b> · not yet paid ${money(s.unpaid.net)}</p>
        <div class="a-tablewrap"><table class="a-table"><thead><tr><th>when</th><th>ride</th><th>fare</th><th>platform</th><th>tip</th><th>you keep</th><th>paid</th></tr></thead><tbody>
        ${s.trips.map(x => `<tr><td>${fmtWhen(x.at)}</td><td>${h(x.ref)}${x.cancelled ? " (cancellation fee)" : ""}${x.pool ? " (shared)" : ""}</td><td>${money(x.fare)}</td><td>${money(x.take)}</td><td>${money(x.tip)}</td><td><b>${money(x.net)}</b></td><td>${x.payout ? h(x.payout) : "—"}</td></tr>`).join("") || `<tr><td colspan="7">No trips in these two weeks.</td></tr>`}</tbody></table></div>
        ${s.payouts.length ? `<h3>Payouts</h3>${s.payouts.map(p => `<p>${h(p.ref)} · up to ${h(p.through)} · ${money(p.net)} · ${h(p.status)}${p.paid_at ? " " + fmtWhen(p.paid_at) : ""}</p>`).join("")}` : ""}</section>`;
    } catch (e) { fail(e); }
  }
  function wireDrive() {
    const on = (sel, fn) => document.querySelectorAll(sel).forEach(x => x.onclick = e => { e.preventDefault(); fn(x); });
    const sub = (sel, fn) => document.querySelectorAll(sel).forEach(x => x.onsubmit = e => { e.preventDefault(); fn(x); });
    const o = $("#dvOnline"); if (o) o.onclick = async () => {
      const going = !RX.dv.me.online;
      try { if (going) { const p = await where(); if (p) await api("/drive/position", "POST", p).catch(() => { }); } await api("/drive/online", "POST", { online: going }); pageDrive(); } catch (e) { fail(e); }
    };
    const er = $("#dvEarn"); if (er) er.onclick = e => { e.preventDefault(); clearTimeout(timer); showEarnings(); };
    on("[data-dv-move]", async x => { const [id, to] = x.dataset.dvMove.split(":"); try { await api(`/drive/rides/${id}/move`, "POST", { to }); pageDrive(); } catch (e) { fail(e); } });
    on("[data-dv-cancel]", async x => { if (!confirm("Cancel this ride?")) return; const cancel = (RX.dv.active.find(r => String(r.id) === x.dataset.dvCancel) || {}).cancelTo; try { await api(`/drive/rides/${x.dataset.dvCancel}/move`, "POST", { to: cancel }); pageDrive(); } catch (e) { fail(e); } });
    on("[data-dv-sos]", async x => {
      if (!confirm(`Raise an emergency? The store is alerted at once with where you are. If you are in danger, also call ${RX.dv.safety.emergency}.`)) return;
      const p = await where();
      try { const r = (await api(`/drive/rides/${x.dataset.dvSos}/safety`, "POST", { kind: "sos", lat: p && p.lat, lng: p && p.lng })).report;
        dynModal("Help is on the way", `<p role="alert">The store has your emergency (<b>${h(r.ref)}</b>).</p><p>If you are in danger, call <a class="btn-yellow" href="tel:${h(r.emergency)}">${h(r.emergency)}</a> now.</p>`); } catch (e) { fail(e); }
    });
    sub("[data-dv-rate]", async x => { const id = x.dataset.dvRate; try { await api(`/drive/rides/${id}/rate`, "POST", { stars: Number(picked("ds" + id)[0]), tags: picked("dt" + id), comment: x.cm.value }); toast("Rating sent"); pageDrive(); } catch (e) { fail(e); } });
    sub("[data-dv-rep]", async x => { try { const r = (await api(`/drive/rides/${x.dataset.dvRep}/safety`, "POST", { kind: x.kind.value, note: x.note.value })).report; toast("Reported — " + h(r.ref)); } catch (e) { fail(e); } });
  }

  window.LX_PAGES = Object.assign(window.LX_PAGES || {}, { ride: pageRide, drive: pageDrive });
})();
