/* LUXORA Platform — the storefront's astrology page (public/astro.html): a birth chart drawn in the
   store's chart style, the planets, the Vimshottari dasha with today's period marked, the panchang,
   kundli matching and the astrology guide. Every number comes from the platform (POST
   /api/astro/chart, /panchang, the MCP tool astro_match via /api/mcp, /api/assistant/astro/ask). */
"use strict";
(function () {
  const $ = s => document.querySelector(s);
  const esc = v => String(v == null ? "" : v).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
  const csrf = () => (document.cookie.match(/(?:^|;\s*)azc=([^;]+)/) || [])[1] || "";
  async function call(path, body) {
    const r = await fetch("/api" + path, body ? { method: "POST", headers: { "Content-Type": "application/json", "x-csrf": csrf() }, body: JSON.stringify(body), credentials: "same-origin" } : { credentials: "same-origin" });
    const j = await r.json().catch(() => ({}));
    if (!r.ok) throw Object.assign(new Error(j.error || ("HTTP " + r.status)), { status: r.status });
    return j;
  }
  const state = { birth: null, chart: null, style: "north", conversation: null, history: [] };
  const birthOf = (d, t, z, la, lo) => ({ date: d, time: t, timeZone: z, latitude: Number(la), longitude: Number(lo) });

  /* ---------- the chart, in the store's style ---------- */
  const SHORT = b => b.short || b.body.slice(0, 2);
  function northSvg(c) {
    /* houses are fixed places; signs move: house 1 is the top diamond */
    const P = [[200, 110], [110, 50], [50, 110], [110, 200], [50, 290], [110, 350], [200, 290], [290, 350], [350, 290], [290, 200], [350, 110], [290, 50]];
    const bodiesIn = h => c.bodies.filter(b => b.house === h).map(SHORT).join(" ");
    const signNo = h => ((c.houses[h - 1] || {}).sign ? ["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"].indexOf(c.houses[h - 1].sign) + 1 : "");
    return `<svg viewBox="0 0 400 400" width="100%" role="img" aria-label="North Indian birth chart">
      <rect x="2" y="2" width="396" height="396" fill="#fff" stroke="#333" stroke-width="2"/>
      <line x1="2" y1="2" x2="398" y2="398" stroke="#333"/><line x1="398" y1="2" x2="2" y2="398" stroke="#333"/>
      <polygon points="200,2 398,200 200,398 2,200" fill="none" stroke="#333"/>
      ${P.map(([x, y], i) => `<text x="${x}" y="${y - 14}" font-size="11" fill="#999" text-anchor="middle">${signNo(i + 1)}</text><text x="${x}" y="${y + 6}" font-size="15" font-weight="700" fill="#1f2937" text-anchor="middle">${esc(bodiesIn(i + 1))}</text>`).join("")}
      <text x="200" y="135" font-size="10" fill="#b45309" text-anchor="middle">Asc</text></svg>`;
  }
  function southSvg(c) {
    /* signs are fixed places (Pisces top-left, clockwise); the ascendant's sign is marked */
    const order = ["pisces", "aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius", "capricorn", "aquarius"];
    const cells = [[0, 0], [1, 0], [2, 0], [3, 0], [3, 1], [3, 2], [3, 3], [2, 3], [1, 3], [0, 3], [0, 2], [0, 1]];
    return `<svg viewBox="0 0 400 400" width="100%" role="img" aria-label="South Indian birth chart">
      ${cells.map(([cx, cy], i) => { const s = order[i], asc = c.ascendant.sign === s; const bs = c.bodies.filter(b => b.sign === s).map(SHORT).join(" ");
        return `<rect x="${cx * 100 + 1}" y="${cy * 100 + 1}" width="98" height="98" fill="${asc ? "#fff7e0" : "#fff"}" stroke="#333"/><text x="${cx * 100 + 6}" y="${cy * 100 + 16}" font-size="10" fill="#999">${esc(s.slice(0, 3))}${asc ? " · Asc" : ""}</text><text x="${cx * 100 + 50}" y="${cy * 100 + 58}" font-size="14" font-weight="700" fill="#1f2937" text-anchor="middle">${esc(bs)}</text>`; }).join("")}
      <text x="200" y="205" font-size="13" fill="#666" text-anchor="middle">Rashi chart</text></svg>`;
  }
  function westernSvg(c) {
    const cx = 200, cy = 200, R = 180, r = 120, asc = c.ascendant.longitude;
    const at = (lon, rad) => { const a = Math.PI - (lon - asc) * Math.PI / 180; return [cx + rad * Math.cos(a), cy - rad * Math.sin(a)]; };
    const spokes = Array.from({ length: 12 }, (_, i) => { const [x1, y1] = at(Math.floor(asc / 30) * 30 + i * 30, r); const [x2, y2] = at(Math.floor(asc / 30) * 30 + i * 30, R); return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#bbb"/>`; }).join("");
    return `<svg viewBox="0 0 400 400" width="100%" role="img" aria-label="Western chart wheel"><circle cx="${cx}" cy="${cy}" r="${R}" fill="#fff" stroke="#333"/><circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#333"/>${spokes}
      ${c.bodies.map((b, i) => { const [x, y] = at(b.longitude, r + 30 - (i % 2) * 14); return `<text x="${x}" y="${y}" font-size="13" font-weight="700" text-anchor="middle" fill="#1f2937">${esc(SHORT(b))}</text>`; }).join("")}
      <text x="${at(asc, R + 12)[0]}" y="${at(asc, R + 12)[1]}" font-size="11" fill="#b45309" text-anchor="middle">Asc</text></svg>`;
  }
  const STYLES = { north: northSvg, south: southSvg, western: westernSvg };

  function show(c) {
    state.chart = c;
    $("#chartSvg").innerHTML = (STYLES[c.settings.chart_style] || northSvg)(c);
    $("#chartSettings").textContent = [c.settings.zodiac, c.settings.ayanamsa && ("ayanamsa " + c.settings.ayanamsa + " " + c.settings.ayanamsaDegrees + "°"), c.settings.house_system.replace("_", " ") + " houses", "provider: " + c.settings.provider].filter(Boolean).join(" · ");
    $("#bodies").innerHTML = `<thead><tr><th>Body</th><th>Sign</th><th>Degree</th><th>Nakshatra · pada</th><th>House</th></tr></thead><tbody>
      <tr><td>Ascendant</td><td>${esc(c.ascendant.signLabel)}</td><td>${c.ascendant.degreeInSign.toFixed(2)}°</td><td>${esc(c.ascendant.nakshatraLabel)} · ${c.ascendant.pada}</td><td>1</td></tr>
      ${c.bodies.map(b => `<tr><td>${esc(b.label)}</td><td>${esc(b.signLabel)} <span class="muted">${esc(b.signVedic)}</span></td><td>${b.degreeInSign.toFixed(2)}°</td><td>${esc(b.nakshatraLabel)} · ${b.pada}</td><td>${b.house}</td></tr>`).join("")}</tbody>`;
    const today = new Date().toISOString().slice(0, 10);
    $("#dasha").innerHTML = `<p class="muted">Balance of the first period at birth: ${c.dasha.balanceAtBirthYears} years.</p><table><thead><tr><th>Mahadasha</th><th>From</th><th>To</th></tr></thead><tbody>
      ${c.dasha.periods.map(p => { const now = p.start <= today && p.end > today; const sub = now ? (p.antardashas || []).find(a => a.start <= today && a.end > today) : null;
        return `<tr class="${now ? "now" : ""}"><td>${esc(p.lord)}${now ? " — now" : ""}${sub ? `<br><span class="muted">antardasha: ${esc(sub.lord)} until ${esc(sub.end)}</span>` : ""}</td><td>${esc(p.start)}</td><td>${esc(p.end)}</td></tr>`; }).join("")}</tbody></table>`;
    $("#astroOut").hidden = false;
  }
  async function panchangNow() {
    const d = new Date(), pad = n => String(n).padStart(2, "0");
    const when = { date: d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()), time: pad(d.getHours()) + ":" + pad(d.getMinutes()), timeZone: state.birth.timeZone, latitude: state.birth.latitude, longitude: state.birth.longitude };
    try { const { panchang: p } = await call("/astro/panchang", { when });
      $("#panchang").innerHTML = `<table><tbody><tr><th>Tithi</th><td>${esc(p.tithi.name)} (${esc(p.tithi.paksha)} paksha)</td></tr><tr><th>Vara</th><td>${esc(p.vara)}</td></tr><tr><th>Nakshatra</th><td>${esc(p.nakshatra)}</td></tr><tr><th>Yoga</th><td>${esc(p.yoga)}</td></tr><tr><th>Karana</th><td>${esc(p.karana)}</td></tr></tbody></table><p class="muted">At ${esc(when.date)} ${esc(when.time)} in ${esc(when.timeZone)}.</p>`;
    } catch (e) { $("#panchang").textContent = e.message; }
  }

  /* ---------- matching, through the platform's MCP tool ---------- */
  async function match() {
    const second = birthOf($("#mDate").value, $("#mTime").value, state.birth.timeZone, $("#mLat").value, $("#mLon").value);
    try {
      const r = await call("/mcp", { jsonrpc: "2.0", id: Date.now(), method: "tools/call", params: { name: "astro_match", arguments: { first: state.birth, second } } });
      const out = r.result || {}; if (out.isError) throw new Error(out.content[0].text);
      const m = out.structuredContent.match;
      $("#match").innerHTML = `<p><b>${m.total} / ${m.max}</b> gunas — Moon in ${esc(m.first.nakshatra)} and ${esc(m.second.nakshatra)}.</p><table><tbody>${m.kootas.map(k => `<tr><td>${esc(k.label)}${k.verified ? "" : " *"}</td><td>${k.points} / ${k.max}</td></tr>`).join("")}</tbody></table>
        ${m.needsExpertReview ? `<p class="note">* ${esc(m.unverifiedKootas.join(", "))} use simplified tables; ask an astrologer to confirm these.</p>` : ""}`;
    } catch (e) { $("#match").textContent = e.message; }
  }

  /* ---------- the astrology guide ---------- */
  function say(who, text, turn) {
    const div = document.createElement("div"); div.className = "msg" + (who === "me" ? " me" : "");
    div.innerHTML = esc(text) + (turn ? ` <span class="noprint"><button class="btn-white sm" data-rate="${turn}|5" title="Helpful">👍</button> <button class="btn-white sm" data-rate="${turn}|1" title="Not helpful">👎</button></span>` : "");
    $("#chat").appendChild(div); $("#chat").scrollTop = 1e9;
    div.querySelectorAll("[data-rate]").forEach(b => b.onclick = async () => {
      const [t, rating] = b.dataset.rate.split("|"); const correction = Number(rating) < 3 ? prompt("What should it have said? (optional — your correction goes to the store's astrologers)") : "";
      try { await call("/assistant/turns/" + t + "/rate", { rating: Number(rating), correction: correction || undefined }); b.parentNode.textContent = "Thank you"; } catch (e) { b.parentNode.textContent = e.message; }
    });
  }
  async function ask() {
    const message = $("#chatIn").value.trim(); if (!message) return;
    $("#chatIn").value = ""; say("me", message);
    try {
      const r = await call("/assistant/astro/ask", { message, birth: state.birth, conversation: state.conversation, history: state.history });
      state.conversation = r.conversation; state.history.push({ role: "user", content: message }, { role: "assistant", content: r.answer });
      say("guide", r.answer, r.turn);
      if (r.handoff) { const a = $("#handoff"); a.textContent = r.handoff.label; a.href = r.handoff.path; a.hidden = false; }
      $("#chatNote").textContent = r.disclaimer || "";
    } catch (e) { say("guide", e.status === 404 ? "The astrology guide is not available in this store." : e.message); }
  }

  async function boot() {
    const zones = (Intl.supportedValuesOf ? Intl.supportedValuesOf("timeZone") : [Intl.DateTimeFormat().resolvedOptions().timeZone]);
    const mine = Intl.DateTimeFormat().resolvedOptions().timeZone;
    $("#zones").innerHTML = zones.map(z => `<option value="${esc(z)}">`).join("");
    if (!$("#bZone").value) $("#bZone").value = mine || "";
    try { await call("/astro"); } catch (e) { $("#astroOff").hidden = false; $("#astroForm").hidden = true; return; }
    $("#astroForm").onsubmit = async ev => {
      ev.preventDefault(); $("#astroErr").textContent = "";
      state.birth = birthOf($("#bDate").value, $("#bTime").value, $("#bZone").value, $("#bLat").value, $("#bLon").value);
      try { const { chart } = await call("/astro/chart", { birth: state.birth }); show(chart); panchangNow(); } catch (e) { $("#astroErr").textContent = e.message; }
    };
    $("#mGo").onclick = match; $("#chatGo").onclick = ask; $("#printBtn").onclick = () => window.print();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
