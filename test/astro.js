/* LUXORA Platform — the astrology engine (lib/astro.js) against published reference values:
   Meeus's worked examples for the Sun, the Moon and Venus; real sky events (the great
   conjunction, an opposition of Mars, transits of Mercury and Venus); the ascendant on the eastern
   horizon; and the chart, dasha and panchang built from them. No server, no network. */
"use strict";
const astro = require("../lib/astro.js");
const SEED = require("../lib/seed/astro.json");
const I = astro._internal;
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + JSON.stringify(x) : ""))); };
const T = jd => (jd - 2451545) / 36525;
const near = (a, b, tol) => Math.abs((((a - b) % 360) + 540) % 360 - 180) <= tol;
const tAt = iso => T(astro.julianDay(new Date(iso)) + 69.2 / 86400);

console.log("▸ THE BUILT-IN PROVIDER MATCHES PUBLISHED REFERENCE VALUES");
ok(near(I.sunApparent(T(2448908.5)), 199.90895, 0.001), "the Sun, 1992 Oct 13 (Meeus example 25.a): 199.90895°", I.sunApparent(T(2448908.5)));
ok(near(I.moonApparent(T(2448724.5)), 133.16727, 0.01), "the Moon, 1992 Apr 12 (Meeus example 47.a, with nutation): 133.16727°", I.moonApparent(T(2448724.5)));
ok(near(I.planetApparent("venus", T(2448976.5)), 313.08102, 0.01), "Venus, 1992 Dec 20 (Meeus example 33.a): 313.08102°", I.planetApparent("venus", T(2448976.5)));
{
  const t = tAt("2020-12-21T18:00:00Z");
  ok(near(I.planetApparent("jupiter", t), I.planetApparent("saturn", t), 0.15), "Jupiter and Saturn meet at the great conjunction of 2020 Dec 21");
}
{ const t = tAt("2020-10-13T23:20:00Z"); ok(near(I.planetApparent("mars", t), I.sunApparent(t) + 180, 0.1), "Mars stands opposite the Sun at its 2020 Oct 13 opposition"); }
{ const t = tAt("2019-11-11T15:20:00Z"); ok(near(I.planetApparent("mercury", t), I.sunApparent(t), 0.05), "Mercury lines up with the Sun at its 2019 Nov 11 transit"); }
{ const t = tAt("2012-06-06T01:30:00Z"); ok(near(I.planetApparent("venus", t), I.sunApparent(t), 0.05), "Venus lines up with the Sun at its 2012 Jun 6 transit"); }

console.log("▸ THE ASCENDANT IS THE POINT OF THE ECLIPTIC RISING IN THE EAST");
{
  let worst = 0, east = true;
  for (const [iso, lat, lon] of [["1990-03-15T05:30:00Z", 28.61, 77.21], ["2001-08-01T20:10:00Z", 19.08, 72.88], ["1975-12-25T11:00:00Z", 13.08, 80.27], ["2024-06-21T00:00:00Z", 51.5, -0.13], ["1985-01-01T12:00:00Z", -33.87, 151.21]]) {
    const jd = astro.julianDay(new Date(iso)), t = T(jd), a = I.angles(jd, t, lat, lon);
    const eps = a.obliquity * Math.PI / 180, L = a.asc * Math.PI / 180;
    const ra = Math.atan2(Math.sin(L) * Math.cos(eps), Math.cos(L)), dec = Math.asin(Math.sin(L) * Math.sin(eps));
    const H = (I.siderealTime(jd, lon) * Math.PI / 180) - ra, phi = lat * Math.PI / 180;
    const alt = Math.asin(Math.sin(phi) * Math.sin(dec) + Math.cos(phi) * Math.cos(dec) * Math.cos(H)) * 180 / Math.PI;
    worst = Math.max(worst, Math.abs(alt)); if (Math.sin(H) > 0) east = false;
  }
  ok(worst < 0.01, "at five dates and places the ascendant sits on the horizon (altitude 0°)", worst);
  ok(east, "…on the eastern side, rising");
}

console.log("▸ A CHART, FROM A BIRTH DATE, TIME AND PLACE");
const birth = { date: "1990-03-15", time: "11:00", timeZone: "Asia/Kolkata", latitude: 28.6139, longitude: 77.2090 };
const c = astro.chart(birth, { ayanamsa: "lahiri" });
ok(c.instant === "1990-03-15T05:30:00.000Z", "the local time in Asia/Kolkata is read as the right instant", c.instant);
ok(c.bodies.length === SEED.BODIES.length && c.bodies.every(b => b.longitude >= 0 && b.longitude < 360 && b.pada >= 1 && b.pada <= 4 && SEED.NAKSHATRAS.some(n => n.key === b.nakshatra)), "every body has a longitude, a sign, a nakshatra and a pada");
const ra = c.bodies.find(b => b.body === "rahu"), ke = c.bodies.find(b => b.body === "ketu");
ok(near(ra.longitude, ke.longitude + 180, 0.0002), "Rahu and Ketu are exactly opposite");
const trop = astro.chart(birth, { zodiac: "tropical" });
const sunS = c.bodies.find(b => b.body === "sun").longitude, sunT = trop.bodies.find(b => b.body === "sun").longitude;
ok(near(sunT - sunS, c.settings.ayanamsaDegrees, 0.001) && c.settings.ayanamsaDegrees > 23.6 && c.settings.ayanamsaDegrees < 23.9, "the sidereal zodiac is the tropical less the Lahiri ayanamsa (≈23.7° in 1990)", c.settings.ayanamsaDegrees);
ok(c.houses.length === 12 && c.houses[0].sign === c.ascendant.sign, "whole-sign houses start at the ascendant's sign");
const eq = astro.chart(birth, { house_system: "equal" });
ok(near(eq.houses[0].cusp, eq.ascendant.longitude, 0.0001) && near(eq.houses[3].cusp, eq.ascendant.longitude + 90, 0.0001), "equal houses run in 30° steps from the ascendant");
ok(c.bodies.every(b => b.house >= 1 && b.house <= 12), "every body is placed in a house");

console.log("▸ THE VIMSHOTTARI DASHA");
const moon = c.bodies.find(b => b.body === "moon");
const d = c.dasha;
ok(d.periods.length === 9 && d.periods[0].lord === moon.nakshatraLord, "the first mahadasha is the Moon's nakshatra lord's", [d.periods[0].lord, moon.nakshatraLord]);
ok(d.periods.reduce((s, p) => s + p.years, 0) === 120, "the nine periods make 120 years");
ok(d.balanceAtBirthYears > 0 && d.balanceAtBirthYears <= SEED.VIMSHOTTARI.years[d.periods[0].lord], "the balance at birth is part of the first period", d.balanceAtBirthYears);
ok(d.periods[0].start <= "1990-03-15" && d.periods[0].end > "1990-03-15" && d.periods[1].start === d.periods[0].end, "the periods run on from birth without gaps");

console.log("▸ ANTARDASHAS AND KUNDLI MATCHING");
{
  const md = c.dasha.periods[1];
  ok(md.antardashas.length === 9 && md.antardashas[0].lord === md.lord && md.antardashas[0].start === md.start && md.antardashas[8].end === md.end, "each mahadasha's nine antardashas start with its own lord and fill it exactly", md.antardashas.map(x => x.lord));
  const self = astro.match(birth, birth);
  const k = Object.fromEntries(self.kootas.map(x => [x.koota, x.points]));
  ok(self.max === 36 && k.nadi === 0 && k.bhakoot === 7 && k.graha_maitri === 5 && k.tara === 3 && k.varna === 1, "matching a chart with itself: same nadi scores 0, same sign and lord score in full", k);
  const other = astro.match(birth, { date: "1992-07-08", time: "06:45", timeZone: "Asia/Kolkata", latitude: 19.08, longitude: 72.88 });
  ok(other.total >= 0 && other.total <= 36 && other.kootas.every(x => x.points >= 0 && x.points <= x.max), "every koota scores within its maximum", other.kootas);
  ok(other.needsExpertReview && other.unverifiedKootas.join() === "Vashya,Yoni,Gana", "kootas on simplified tables are named for an astrologer to confirm", other.unverifiedKootas);
}

console.log("▸ THE PANCHANG");
{
  /* a full moon (2024 Apr 23 23:49 UTC) is Purnima; a new moon (2024 Apr 8 18:21 UTC) Amavasya */
  const full = astro.panchang({ date: "2024-04-24", time: "05:30", timeZone: "Asia/Kolkata", latitude: 28.61, longitude: 77.21 });
  ok(full.tithi.name === "Purnima" || full.tithi.number === 16, "at the full moon of 2024 Apr 23 the tithi is Purnima (or has just turned)", full.tithi);
  const nw = astro.panchang({ date: "2024-04-08", time: "23:30", timeZone: "Asia/Kolkata", latitude: 28.61, longitude: 77.21 });
  ok(nw.tithi.name === "Amavasya" || nw.tithi.number === 1, "at the new moon of 2024 Apr 8 the tithi is Amavasya (or has just turned)", nw.tithi);
  ok(full.vara === "Budhavara", "2024 Apr 24 is a Wednesday (Budhavara) in India", full.vara);
  ok(SEED.YOGAS.includes(full.yoga) && typeof full.karana === "string", "a yoga and a karana are named", [full.yoga, full.karana]);
}

console.log("▸ THE STORE'S CHOICES ARE CHECKED; A PROVIDER NOT INSTALLED SAYS SO");
const throws = (fn, re) => { try { fn(); return false; } catch (e) { return re.test(e.message); } };
ok(throws(() => astro.chart(birth, { ayanamsa: "invented" }), /unknown ayanamsa/), "an unknown ayanamsa is refused");
ok(throws(() => astro.chart(birth, { house_system: "invented" }), /unknown house system/), "an unknown house system is refused");
ok(throws(() => astro.chart(birth, { provider: "invented" }), /unknown astrology provider/), "an unknown provider is refused");
ok(throws(() => astro.chart(birth, { provider: "swisseph" }), /not installed/), "Swiss Ephemeris, not installed, says so instead of computing something else");
ok(throws(() => astro.chart({ date: "1990-03-15", time: "11:00", latitude: 28.6, longitude: 77.2 }), /timeZone/), "a birth with no time zone is refused (a wrong zone would move every house)");
ok(throws(() => astro.chart({ ...birth, latitude: 80 }), /latitude/), "a latitude beyond the polar circles is refused (the ascendant is undefined there)");
const v = astro.vocabulary();
ok(v.providers.some(p => p.key === "builtin") && v.ayanamsas.some(a => a.key === "lahiri") && v.houseSystems.length >= 2, "the choices offered come from the declaration");

/* ---- over HTTP: a store switches the engine on in its capabilities and computes with its own settings ---- */
(async () => {
  const path = require("path"), fs = require("fs"), { spawn } = require("child_process");
  const DB = path.join(__dirname, "astro.db"), PORT = 8843, BASE = "http://localhost:" + PORT;
  const clean = () => { for (const x of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + x, { force: true }); } catch (e) { } } };
  clean();
  const srv = spawn(process.execPath, [path.join(__dirname, "..", "server.js")], { env: { ...process.env, PORT, LX_DB: DB, LX_LOG: "" }, stdio: ["ignore", "ignore", "pipe"] });
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const alive = async () => { try { return (await fetch(BASE + "/healthz")).ok; } catch (e) { return false; } };
  try {
    for (let i = 0; i < 240 && !(await alive()); i++) await sleep(500);
    console.log("▸ OVER HTTP, WITH THE STORE'S OWN SETTINGS");
    const jar = new Map();
    const f = async (p, m, b) => { const h = { Cookie: [...jar].map(x => x.join("=")).join("; ") }; if (m && m !== "GET") Object.assign(h, { "x-csrf": jar.get("azc") || "", "Content-Type": "application/json", Origin: BASE });
      const r = await fetch(BASE + p, { method: m || "GET", headers: h, body: b ? JSON.stringify(b) : undefined }); (r.headers.getSetCookie() || []).forEach(k => { const kv = k.split(";")[0], i = kv.indexOf("="); jar.set(kv.slice(0, i), kv.slice(i + 1)); }); return { st: r.status, b: await r.json().catch(() => ({})) }; };
    await f("/api/session");
    ok((await f("/api/astro")).st === 404, "a store without the capability has no astrology engine");
    await f("/api/auth/login", "POST", { email: "admin@luxora.shop", password: "admin123" });
    const en = await f("/api/capabilities/enable", "POST", { capability: "astro_engine" });
    ok(en.st === 200, "the owner switches the Astrology engine on in Capabilities", en.b);
    const v = await f("/api/astro");
    ok(v.st === 200 && v.b.settings.provider === "builtin" && v.b.choices.ayanamsas.length >= 3, "the store's settings and the choices come back", v.b.settings);
    const ch = await f("/api/astro/chart", "POST", { birth });
    ok(ch.st === 200 && ch.b.chart.bodies.length === 9 && ch.b.chart.dasha.periods.length === 9, "a birth chart is computed through the API", ch.b.error);
    await f("/api/capabilities/param", "POST", { capability: "astro_engine", param: "ayanamsa", value: "raman" });
    const ch2 = await f("/api/astro/chart", "POST", { birth });
    ok(ch2.b.chart && ch2.b.chart.settings.ayanamsa === "raman" && Math.abs(ch2.b.chart.settings.ayanamsaDegrees - ch.b.chart.settings.ayanamsaDegrees) > 1, "changing the store's ayanamsa changes the chart", ch2.b.chart && ch2.b.chart.settings);
    const bad = await f("/api/astro/chart", "POST", { birth: { date: "1990-03-15" } });
    ok(bad.st === 400 && /time zone|timeZone|latitude/.test(bad.b.error), "a birth missing its place or zone is refused with the reason", bad.b);
    const pc = await f("/api/astro/panchang", "POST", { when: { date: "2024-04-24", time: "05:30", timeZone: "Asia/Kolkata", latitude: 28.61, longitude: 77.21 } });
    ok(pc.st === 200 && pc.b.panchang.vara === "Budhavara", "the panchang is computed through the API", pc.b);
  } catch (e) { failed++; console.log("  ✗ harness error: " + (e && e.stack || e)); }
  finally { srv.kill("SIGTERM"); await sleep(300); clean(); }
  console.log(`\n${passed} passed, ${failed} failed`);
  process.exit(failed ? 1 : 0);
})();
