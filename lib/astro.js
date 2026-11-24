/* LUXORA Platform — the astrology engine: a birth chart (planetary positions, ascendant, houses,
   signs, nakshatras), the Vimshottari dasha periods and the panchang, from a date, time and place.

   Everything a store chooses is data (lib/seed/astro.json), set in Store console → Capabilities →
   Astrology engine (capability astro_engine): which PROVIDER computes the positions, the zodiac,
   the ayanamsa, the house system and the chart style. A provider declares its transport:
     builtin — computed here from published formulas: the Sun (Meeus ch. 25), the Moon (Meeus
               ch. 47, its largest terms), the planets from JPL's approximate Keplerian elements
               (1800-2050), the mean lunar node, sidereal time and the ascendant. No licence, no
               dependency; accurate to a few arcminutes, which is well inside a nakshatra pada
               (3°20') except for a body within minutes of a boundary.
     module  — a library the operator installs under their own licence (Swiss Ephemeris needs a
               commercial one for a closed platform); the platform never ships it.
   Every result names the provider and settings that produced it. */
"use strict";
const SEED = require("./seed/astro.json");

const D2R = Math.PI / 180, R2D = 180 / Math.PI;
const norm = x => ((x % 360) + 360) % 360;
const sin = d => Math.sin(d * D2R), cos = d => Math.cos(d * D2R);
const byKey = (list, k) => (list || []).find(x => x.key === k) || null;

/* ---------- time ---------- */
const julianDay = date => date.getTime() / 86400000 + 2440587.5;
/* TT − UT in seconds (Espenak & Meeus polynomial approximations) */
function deltaT(year) {
  const y = year;
  if (y >= 2005 && y < 2050) { const t = y - 2000; return 62.92 + 0.32217 * t + 0.005589 * t * t; }
  if (y >= 1986 && y < 2005) { const t = y - 2000; return 63.86 + 0.3345 * t - 0.060374 * t * t + 0.0017275 * t ** 3 + 0.000651814 * t ** 4 + 0.00002373599 * t ** 5; }
  if (y >= 1961 && y < 1986) { const t = y - 1975; return 45.45 + 1.067 * t - t * t / 260 - t ** 3 / 718; }
  if (y >= 1941 && y < 1961) { const t = y - 1950; return 29.07 + 0.407 * t - t * t / 233 + t ** 3 / 2547; }
  if (y >= 1920 && y < 1941) { const t = y - 1920; return 21.20 + 0.84493 * t - 0.076100 * t * t + 0.0020936 * t ** 3; }
  if (y >= 1900 && y < 1920) { const t = y - 1900; return -2.79 + 1.494119 * t - 0.0598939 * t * t + 0.0061966 * t ** 3 - 0.000197 * t ** 4; }
  if (y >= 2050 && y < 2150) return -20 + 32 * ((y - 1820) / 100) ** 2 - 0.5628 * (2150 - y);
  const u = (y - 1820) / 100; return -20 + 32 * u * u;
}
/* the local wall time of a birth, in a named zone (IANA) or at an explicit UTC offset, as an instant */
function instantOf(birth) {
  const b = birth || {};
  /* astronomical year numbering: 1 BC is year 0, 2 BC is -1 (a date's year may be 1 to 4 digits, or negative) */
  const m = /^(-?\d{1,4})-(\d{2})-(\d{2})$/.exec(String(b.date || ""));
  const t = /^(\d{1,2}):(\d{2})(?::(\d{2}))?$/.exec(String(b.time || "12:00"));
  if (!m || !t) throw new Error("birth date (YYYY-MM-DD) and time (HH:MM) are required");
  const year = +m[1];
  if (year < SEED.ELEMENTS_LONG.validFromYear || year > SEED.ELEMENTS_LONG.validToYear) throw new Error("dates from " + (1 - SEED.ELEMENTS_LONG.validFromYear) + " BC to AD " + SEED.ELEMENTS_LONG.validToYear + " are supported");
  /* Date.UTC reads years 0-99 as 1900-1999; setting the full year keeps them as given */
  const d0 = new Date(Date.UTC(2000, +m[2] - 1, +m[3], +t[1], +t[2], +(t[3] || 0))); d0.setUTCFullYear(year);
  let wall = d0.getTime();
  /* a date written in the Julian calendar (most records before 1582): the same day number in the
     Julian calendar, read as an instant (the calendars' days differ by a year-dependent count) */
  const cal = b.calendar || SEED.CALENDARS[0].key;
  if (!byKey(SEED.CALENDARS, cal)) throw new Error("unknown calendar: " + cal);
  if (byKey(SEED.CALENDARS, cal).julian) {
    const a = Math.floor((14 - +m[2]) / 12), y = year + 4800 - a, mo = +m[2] + 12 * a - 3;
    const jdn = +m[3] + Math.floor((153 * mo + 2) / 5) + 365 * y + Math.floor(y / 4) - 32083;
    wall = (jdn - 2440588) * 86400000 + ((+t[1]) * 3600 + (+t[2]) * 60 + (+(t[3] || 0))) * 1000;
  }
  if (b.utcOffsetMinutes != null && b.utcOffsetMinutes !== "") return new Date(wall - Number(b.utcOffsetMinutes) * 60000);
  if (!b.timeZone) throw new Error("timeZone (e.g. Asia/Kolkata) or utcOffsetMinutes is required");
  /* the zone's offset at that wall time (Time owns the wall clock): guess, then correct once (DST edges) */
  const time = require("./time.js");
  if (!time.knowsZone(b.timeZone)) throw new Error("unknown timeZone " + b.timeZone);
  const offsetAt = ms => { const w = time.wallClock(new Date(ms), b.timeZone); return (Date.UTC(w.year, w.month - 1, w.day, w.hour, w.minute, w.second) - ms) / 60000; };
  const off = offsetAt(wall);
  return new Date(wall - offsetAt(wall - off * 60000) * 60000);
}

/* ---------- the built-in provider ---------- */
function nutationLongitude(T) {
  const om = 125.04452 - 1934.136261 * T, L = 280.4665 + 36000.7698 * T, Lm = 218.3165 + 481267.8813 * T;
  return (-17.20 * sin(om) - 1.32 * sin(2 * L) - 0.23 * sin(2 * Lm) + 0.21 * sin(2 * om)) / 3600;
}
const obliquity = T => 23.4392911 - 0.0130042 * T - 1.64e-7 * T * T + 5.04e-7 * T ** 3;
function sunApparent(T) {
  const L0 = 280.46646 + 36000.76983 * T + 0.0003032 * T * T;
  const M = 357.52911 + 35999.05029 * T - 0.0001537 * T * T;
  const C = (1.914602 - 0.004817 * T - 0.000014 * T * T) * sin(M) + (0.019993 - 0.000101 * T) * sin(2 * M) + 0.000289 * sin(3 * M);
  const om = 125.04 - 1934.136 * T;
  return norm(L0 + C - 0.00569 - 0.00478 * sin(om));
}
function moonApparent(T) {
  const Lp = 218.3164477 + 481267.88123421 * T - 0.0015786 * T * T + T ** 3 / 538841 - T ** 4 / 65194000;
  const D = 297.8501921 + 445267.1114034 * T - 0.0018819 * T * T + T ** 3 / 545868 - T ** 4 / 113065000;
  const M = 357.5291092 + 35999.0502909 * T - 0.0001536 * T * T + T ** 3 / 24490000;
  const Mp = 134.9633964 + 477198.8675055 * T + 0.0087414 * T * T + T ** 3 / 69699 - T ** 4 / 14712000;
  const F = 93.2720950 + 483202.0175233 * T - 0.0036539 * T * T - T ** 3 / 3526000 + T ** 4 / 863310000;
  const E = 1 - 0.002516 * T - 0.0000074 * T * T;
  const A1 = 119.75 + 131.849 * T, A2 = 53.09 + 479264.290 * T;
  let sl = 0;
  for (const [d, m, mp, f, c] of SEED.MOON_TERMS.longitude) sl += c * (Math.abs(m) === 1 ? E : Math.abs(m) === 2 ? E * E : 1) * sin(d * D + m * M + mp * Mp + f * F);
  sl += 3958 * sin(A1) + 1962 * sin(Lp - F) + 318 * sin(A2);
  return norm(Lp + sl / 1e6 + nutationLongitude(T));
}
/* heliocentric ecliptic coordinates (J2000 ecliptic) of a planet from its approximate elements */
/* JPL's 1800-2050 elements inside their interval (more accurate there), the 3000 BC - AD 3000
   elements outside it, with the extra mean-anomaly terms they need for Jupiter to Neptune */
const INSIDE_TABLE1 = T => T >= -2 && T <= 0.5;
function helio(name, T) {
  const short = INSIDE_TABLE1(T) && SEED.ELEMENTS[name];
  const [el, rate, extra] = short ? SEED.ELEMENTS[name] : SEED.ELEMENTS_LONG[name];
  const [a, e, I, L, wbar, node] = el.map((v, i) => v + rate[i] * T);
  const w = wbar - node;
  let M = L - wbar;
  if (!short && extra) { const [b, c, sTerm, f] = extra; M += b * T * T + c * cos(f * T) + sTerm * sin(f * T); }
  M = norm(M); if (M > 180) M -= 360;
  let E = M + R2D * e * sin(M);
  for (let i = 0; i < 12; i++) { const dE = (M - (E - R2D * e * sin(E))) / (1 - e * cos(E)); E += dE; if (Math.abs(dE) < 1e-9) break; }
  const xp = a * (cos(E) - e), yp = a * Math.sqrt(1 - e * e) * sin(E);
  const x = (cos(w) * cos(node) - sin(w) * sin(node) * cos(I)) * xp + (-sin(w) * cos(node) - cos(w) * sin(node) * cos(I)) * yp;
  const y = (cos(w) * sin(node) + sin(w) * cos(node) * cos(I)) * xp + (-sin(w) * sin(node) + cos(w) * cos(node) * cos(I)) * yp;
  const z = (sin(w) * sin(I)) * xp + (cos(w) * sin(I)) * yp;
  return [x, y, z];
}
function planetApparent(name, T) {
  /* light time: the planet is seen where it was when its light left it */
  const earth = helio("earth", T);
  let p = helio(name, T);
  for (let i = 0; i < 2; i++) {
    const dist = Math.hypot(p[0] - earth[0], p[1] - earth[1], p[2] - earth[2]);
    p = helio(name, T - dist * 0.0057755183 / 36525);
  }
  const lon = Math.atan2(p[1] - earth[1], p[0] - earth[0]) * R2D;
  /* the elements are referred to the J2000 ecliptic: add precession since J2000 to reach the
     ecliptic of date, then nutation and annual aberration (approximate) */
  const prec = (5029.0966 * T + 1.11113 * T * T) / 3600;
  const sunL = sunApparent(T);
  const aberr = -20.4898 / 3600 * cos(sunL - lon);
  return norm(lon + prec + nutationLongitude(T) + aberr);
}
const meanNode = T => norm(125.0445479 - 1934.1362891 * T + 0.0020754 * T * T + T ** 3 / 467441);
function siderealTime(jdUT, lon) {
  const T = (jdUT - 2451545) / 36525;
  return norm(280.46061837 + 360.98564736629 * (jdUT - 2451545) + 0.000387933 * T * T - T ** 3 / 38710000 + Number(lon || 0));
}
function angles(jdUT, T, lat, lon) {
  const ramc = siderealTime(jdUT, lon), eps = obliquity(T) + 0.00256 * cos(125.04 - 1934.136 * T);
  const asc = norm(Math.atan2(cos(ramc), -(sin(ramc) * cos(eps) + Math.tan(lat * D2R) * sin(eps))) * R2D);
  const mc = norm(Math.atan2(sin(ramc), cos(ramc) * cos(eps)) * R2D);
  return { asc, mc, ramc, obliquity: eps };
}
const BUILTIN = {
  positions(jdUT, lat, lon, opts) {
    const year = 2000 + (jdUT - 2451545) / 365.25;
    const jdTT = jdUT + deltaT(year) / 86400, T = (jdTT - 2451545) / 36525;
    const out = { sun: sunApparent(T), moon: moonApparent(T) };
    for (const b of SEED.BODIES) if (b.elements && (!b.outer || (opts || {}).outer)) out[b.key] = planetApparent(b.elements, T);
    out.rahu = meanNode(T); out.ketu = norm(out.rahu + 180);
    return { longitudes: out, angles: angles(jdUT, T, lat, lon), T };
  }
};
/* an operator-installed module (Swiss Ephemeris); written to its documented API, not run here */
function moduleProvider(p) {
  let swe; try { swe = require(p.module); } catch (e) { throw new Error(p.label + " is not installed on this server — the operator installs it under their own licence"); }
  const ids = { sun: swe.SE_SUN, moon: swe.SE_MOON, mars: swe.SE_MARS, mercury: swe.SE_MERCURY, jupiter: swe.SE_JUPITER, venus: swe.SE_VENUS, saturn: swe.SE_SATURN, rahu: swe.SE_MEAN_NODE };
  return { positions(jdUT, lat, lon, opts) {
    const out = {};
    if ((opts || {}).outer) Object.assign(ids, { uranus: swe.SE_URANUS, neptune: swe.SE_NEPTUNE });
    for (const [k, id] of Object.entries(ids)) out[k] = norm(swe.swe_calc_ut(jdUT, id, swe.SEFLG_SPEED).longitude);
    out.ketu = norm(out.rahu + 180);
    const h = swe.swe_houses(jdUT, lat, lon, "W");
    return { longitudes: out, angles: { asc: norm(h.ascendant), mc: norm(h.mc) }, T: (jdUT - 2451545) / 36525 };
  } };
}
/* the transports a provider row may declare — the engine dispatches on the declaration, never a name */
const TRANSPORTS = { builtin: () => BUILTIN, module: moduleProvider };
function providerOf(key) {
  const p = byKey(SEED.PROVIDERS, key);
  if (!p) throw new Error("unknown astrology provider: " + key);
  const t = TRANSPORTS[p.transport];
  if (!t) throw new Error("provider " + key + " declares an unknown transport " + p.transport);
  return t(p);
}

/* ---------- reading a longitude ---------- */
const NAK = 360 / 27;
function ayanamsa(key, T) { const a = byKey(SEED.AYANAMSAS, key); if (!a) throw new Error("unknown ayanamsa: " + key); return a.j2000 + a.perCentury * T; }
function place(lon) {
  const s = SEED.SIGNS[Math.floor(lon / 30)], n = Math.floor(lon / NAK);
  const k = SEED.NAKSHATRAS[n];
  return { longitude: +lon.toFixed(4), sign: s.key, signLabel: s.label, signVedic: s.vedic, degreeInSign: +(lon % 30).toFixed(4),
    nakshatra: k.key, nakshatraLabel: k.label, nakshatraLord: k.lord, pada: Math.floor((lon % NAK) / (NAK / 4)) + 1 };
}
/* ---------- houses ----------
   Each system declares its method (lib/seed/astro.json HOUSE_SYSTEMS). Quadrant systems work on the
   tropical sky — RAMC, obliquity, latitude — and the zodiac is applied afterwards. A cusp on a
   house circle with pole height `pole` at right ascension R is the ecliptic point
   atan2(sin R, cos R cos ε − tan pole sin ε) (the ascendant is R = RAMC + 90°, pole = latitude). */
const cuspAt = (R, pole, eps) => norm(Math.atan2(sin(R), cos(R) * cos(eps) - Math.tan(pole * D2R) * sin(eps)) * R2D);
const eclipticOfRA = (ra, eps) => norm(Math.atan2(sin(ra), cos(ra) * cos(eps)) * R2D);
/* the four angles' quadrants filled in: 10 = MC, 1 = ASC; 4..9 opposite 10..3 */
function fromQuadrant(asc, mc, c11, c12, c2, c3) {
  const c = { 1: asc, 2: c2, 3: c3, 10: mc, 11: c11, 12: c12 };
  for (const [a, b] of [[4, 10], [5, 11], [6, 12], [7, 1], [8, 2], [9, 3]]) c[a] = norm(c[b] + 180);
  return Array.from({ length: 12 }, (_, i) => c[i + 1]);
}
function porphyryCusps(a) {
  const q = norm(a.asc - a.mc), q2 = norm(a.mc + 180 - a.asc);
  return fromQuadrant(a.asc, a.mc, a.mc + q / 3, a.mc + 2 * q / 3, a.asc + q2 / 3, a.asc + 2 * q2 / 3).map(norm);
}
/* Placidus: a cusp is the ecliptic point a set fraction of its own diurnal (houses 11, 12) or
   nocturnal (houses 2, 3) semi-arc from the meridian; found by iterating on its declination */
function placidusCusp(a, lat, frac, below, start) {
  let lam = start;
  for (let i = 0; i < 60; i++) {
    const dec = Math.asin(sin(a.obliquity) * sin(lam)) * R2D, x = Math.tan(lat * D2R) * Math.tan(dec * D2R);
    if (Math.abs(x) >= 1) throw new Error("Placidus houses are undefined at this latitude for this time");
    const ad = Math.asin(x) * R2D, dsa = 90 + ad, nsa = 90 - ad;
    const ra = a.ramc + (below ? dsa + frac * nsa : frac * dsa);
    const next = eclipticOfRA(ra, a.obliquity);
    if (Math.abs(((next - lam + 540) % 360) - 180) < 1e-9) { lam = next; break; }
    lam = next;
  }
  return lam;
}
const house_whole_sign = a => { const first = Math.floor(a.ascZ / 30); return { cusps: Array.from({ length: 12 }, (_, i) => ((first + i) % 12) * 30), zodiacal: true }; };
const house_equal = a => ({ cusps: Array.from({ length: 12 }, (_, i) => norm(a.ascZ + 30 * i)), zodiacal: true });
const house_porphyry = a => ({ cusps: porphyryCusps(a) });
/* Sripati: the Porphyry cusps are each house's middle (bhava madhya); a house runs from the
   sandhi midway to the previous madhya to the sandhi midway to the next */
const house_sripati = a => { const m = porphyryCusps(a); return { cusps: m, starts: m.map((c, i) => norm(c - norm(c - m[(i + 11) % 12]) / 2)) }; };
const house_placidus = (a, lat) => { const p = porphyryCusps(a); return { cusps: fromQuadrant(a.asc, a.mc, placidusCusp(a, lat, 1 / 3, false, p[10]), placidusCusp(a, lat, 2 / 3, false, p[11]), placidusCusp(a, lat, 1 / 3, true, p[1]), placidusCusp(a, lat, 2 / 3, true, p[2])) }; };
/* Koch: the MC's diurnal semi-arc trisected, measured as oblique ascension from the MC's */
const house_koch = (a, lat) => {
  const dec = Math.asin(sin(a.obliquity) * sin(a.mc)) * R2D, x = Math.tan(lat * D2R) * Math.tan(dec * D2R);
  if (Math.abs(x) >= 1) throw new Error("Koch houses are undefined at this latitude");
  const ad = Math.asin(x) * R2D, step = (90 + ad) / 3, oa = a.ramc - ad;
  const k = n => cuspAt(oa + n * step, lat, a.obliquity);
  return { cusps: fromQuadrant(a.asc, a.mc, k(1), k(2), k(4), k(5)) };
};
/* Regiomontanus: the celestial equator in 30° steps from the meridian */
const house_regiomontanus = (a, lat) => { const k = off => cuspAt(a.ramc + off, Math.atan(Math.tan(lat * D2R) * sin(off)) * R2D, a.obliquity); return { cusps: fromQuadrant(a.asc, a.mc, k(30), k(60), k(120), k(150)) }; };
/* Campanus: the prime vertical in 30° steps from the meridian */
const house_campanus = (a, lat) => { const k = A => cuspAt(a.ramc + Math.atan2(sin(A) * cos(lat), cos(A)) * R2D, Math.asin(sin(lat) * sin(A)) * R2D, a.obliquity); return { cusps: fromQuadrant(a.asc, a.mc, k(30), k(60), k(120), k(150)) }; };
const HOUSE_METHODS = { whole_sign: house_whole_sign, equal: house_equal, porphyry: house_porphyry, sripati: house_sripati, placidus: house_placidus, koch: house_koch, regiomontanus: house_regiomontanus, campanus: house_campanus };
/* KP: a point's sign lord, star (nakshatra) lord, sub lord and sub-sub lord — each nakshatra shared
   out in Vimshottari proportions, starting from its own lord */
function kpLords(lon) {
  const V = SEED.VIMSHOTTARI, n = Math.floor(lon / NAK), star = SEED.NAKSHATRAS[n].lord;
  const split = (from, span, offset) => { let i = V.order.indexOf(from), at = 0; for (let k = 0; k < 9; k++) { const lord = V.order[(i + k) % 9], len = span * V.years[lord] / 120; if (offset < at + len || k === 8) return { lord, start: at, len }; at += len; } };
  const sub = split(star, NAK, lon - n * NAK), subsub = split(sub.lord, sub.len, (lon - n * NAK) - sub.start);
  return { signLord: SEED.SIGNS[Math.floor(lon / 30)].lord, starLord: star, subLord: sub.lord, subSubLord: subsub.lord };
}
function houses(system, a, lat, ayan) {
  const sys = byKey(SEED.HOUSE_SYSTEMS, system); if (!sys) throw new Error("unknown house system: " + system);
  const r = HOUSE_METHODS[sys.method](a, lat);
  const z = l => r.zodiacal ? norm(l) : norm(l - ayan);
  return r.cusps.map((c, i) => Object.assign({ house: i + 1, cusp: +z(c).toFixed(4), start: +z(r.starts ? r.starts[i] : c).toFixed(4), sign: SEED.SIGNS[Math.floor(z(c) / 30)].key },
    sys.kpLords ? kpLords(z(c)) : {}));
}
/* the house a longitude falls in: from its house's start up to the next house's start */
const houseOf = (hs, lon) => { for (let i = 0; i < 12; i++) { const a = hs[i].start, b = hs[(i + 1) % 12].start; if (norm(lon - a) < norm(b - a)) return hs[i].house; } return 12; };

/* ---------- the store's settings ---------- */
function settingsOf(params) {
  const p = Object.assign({ provider: "builtin", zodiac: "sidereal", ayanamsa: "lahiri", house_system: "whole_sign", chart_style: "north", bodies: SEED.BODY_SETS[0].key }, params || {});
  if (!byKey(SEED.ZODIACS, p.zodiac)) throw new Error("unknown zodiac: " + p.zodiac);
  if (!byKey(SEED.BODY_SETS, p.bodies)) throw new Error("unknown set of bodies: " + p.bodies);
  if (!byKey(SEED.HOUSE_SYSTEMS, p.house_system)) throw new Error("unknown house system: " + p.house_system);
  if (!byKey(SEED.CHART_STYLES, p.chart_style)) throw new Error("unknown chart style: " + p.chart_style);
  if (p.zodiac === "sidereal") ayanamsa(p.ayanamsa, 0);
  return p;
}

/* ---------- what a store asks for ---------- */
function chart(birth, params) {
  const p = settingsOf(params);
  const lat = Number(birth && birth.latitude), lon = Number(birth && birth.longitude);
  if (!isFinite(lat) || Math.abs(lat) > 66.5 || !isFinite(lon) || Math.abs(lon) > 180) throw new Error("latitude (within ±66.5°) and longitude are required");
  const at = instantOf(birth), jd = julianDay(at);
  const raw = providerOf(p.provider).positions(jd, lat, lon, { outer: byKey(SEED.BODY_SETS, p.bodies).outer });
  const ayan = p.zodiac === "sidereal" ? ayanamsa(p.ayanamsa, raw.T) : 0;
  const z = l => norm(l - ayan);
  const asc = z(raw.angles.asc);
  /* the houses are computed on the tropical sky (RAMC and obliquity from the instant, whichever provider gave the positions) */
  const ramc = siderealTime(jd, lon), eps = obliquity(raw.T) + 0.00256 * cos(125.04 - 1934.136 * raw.T);
  const hs = houses(p.house_system, { asc: raw.angles.asc, mc: raw.angles.mc, ramc, obliquity: eps, ascZ: asc }, lat, ayan);
  const kp = (byKey(SEED.HOUSE_SYSTEMS, p.house_system) || {}).kpLords;
  const bodies = SEED.BODIES.filter(b => raw.longitudes[b.key] != null).map(b => Object.assign({ body: b.key, label: b.label, short: b.short }, place(z(raw.longitudes[b.key])), { house: houseOf(hs, z(raw.longitudes[b.key])) }, kp ? kpLords(z(raw.longitudes[b.key])) : {}));
  return {
    instant: at.toISOString(), julianDay: +jd.toFixed(6),
    settings: { provider: p.provider, zodiac: p.zodiac, ayanamsa: p.zodiac === "sidereal" ? p.ayanamsa : null, ayanamsaDegrees: +ayan.toFixed(4), house_system: p.house_system, chart_style: p.chart_style },
    ascendant: place(asc), midheaven: place(z(raw.angles.mc)), houses: hs, bodies,
    dasha: vimshottari(z(raw.longitudes.moon), at)
  };
}
/* the mahadashas from birth: the Moon's nakshatra lord's period, already partly run, then the rest in order */
function vimshottari(moonLon, birthAt) {
  const V = SEED.VIMSHOTTARI, n = Math.floor(moonLon / NAK), frac = (moonLon % NAK) / NAK;
  const first = V.order.indexOf(SEED.NAKSHATRAS[n].lord), day = 86400000 * V.yearDays;
  const out = []; let start = birthAt.getTime() - frac * V.years[V.order[first]] * day;
  const iso = ms => new Date(ms).toISOString().slice(0, 10);
  for (let i = 0; i < 9; i++) {
    const lord = V.order[(first + i) % 9], end = start + V.years[lord] * day;
    /* the antardashas: the mahadasha's years shared out in the same order, starting from its own lord */
    const subs = []; let s2 = start; const li = V.order.indexOf(lord);
    for (let k = 0; k < 9; k++) { const sub = V.order[(li + k) % 9], len = V.years[lord] * V.years[sub] / 120 * day; subs.push({ lord: sub, start: iso(s2), end: iso(s2 + len) }); s2 += len; }
    out.push({ lord, years: V.years[lord], start: iso(start), end: iso(end), antardashas: subs });
    start = end;
  }
  return { system: "vimshottari", balanceAtBirthYears: +((1 - frac) * V.years[V.order[first]]).toFixed(3), periods: out };
}
/* the panchang at an instant and place: tithi, paksha, vara, nakshatra, yoga, karana. The vara is
   the weekday of the local civil date (the traditional day runs sunrise to sunrise). */
function panchang(when, params) {
  const p = settingsOf(params);
  const at = instantOf(when), jd = julianDay(at);
  const raw = providerOf(p.provider).positions(jd, Number(when.latitude) || 0, Number(when.longitude) || 0);
  const ayan = ayanamsa(p.zodiac === "sidereal" ? p.ayanamsa : SEED.AYANAMSAS[0].key, raw.T);
  const sun = norm(raw.longitudes.sun - ayan), moon = norm(raw.longitudes.moon - ayan);
  const elong = norm(moon - sun), ti = Math.floor(elong / 12), half = Math.floor(elong / 6);
  const K = SEED.KARANAS;
  const karana = half === 0 ? K.first : half >= 57 ? K.last[half - 57] : K.movable[(half - 1) % 7];
  const vi = when.timeZone ? require("./time.js").wallClock(at, when.timeZone).weekday
    : new Date(at.getTime() + Number(when.utcOffsetMinutes || 0) * 60000).getUTCDay();
  return {
    instant: at.toISOString(), settings: { provider: p.provider, ayanamsa: p.zodiac === "sidereal" ? p.ayanamsa : SEED.AYANAMSAS[0].key },
    tithi: { number: ti + 1, name: SEED.TITHIS[ti], paksha: SEED.PAKSHAS[ti < 15 ? 0 : 1] },
    vara: SEED.VARAS[vi], nakshatra: place(moon).nakshatraLabel,
    yoga: SEED.YOGAS[Math.floor(norm(sun + moon) / NAK)], karana
  };
}
/* kundli matching (ashtakoota) from each person's Moon: every koota's points out of its maximum, the
   total out of 36, and which kootas use a table an astrologer has yet to confirm */
function match(first, second, params) {
  const p = settingsOf(Object.assign({}, params, { zodiac: "sidereal" }));
  const M = SEED.MATCHING;
  const moonOf = b => { const c = chart(b, p); const m = c.bodies.find(x => x.body === "moon"); return { lon: m.longitude, sign: Math.floor(m.longitude / 30), nak: Math.floor(m.longitude / NAK), place: m }; };
  const a = moonOf(first), b = moonOf(second);
  const lordOf = i => SEED.SIGNS[i].lord;
  const vashyaOf = x => { const v = M.vashya.bySign[x.sign]; return Array.isArray(v) ? v[(x.lon % 30) < 15 ? 0 : 1] : v; };
  const rel = (from, to) => { const f = M.friendship[from]; return f.friends.includes(to) ? "friend" : f.enemies.includes(to) ? "enemy" : "neutral"; };
  const pair = (x, y, table) => table[x + "+" + y] != null ? table[x + "+" + y] : table[y + "+" + x];
  const taraFrom = (from, to) => { let r = ((to - from + 27) % 27 + 1) % 9; if (r === 0) r = 9; return M.tara.badRemainders.includes(r) ? 0 : M.tara.perDirection; };
  const dist = ((b.sign - a.sign + 12) % 12) + 1, back = ((a.sign - b.sign + 12) % 12) + 1;
  const ya = M.yoni.byNakshatra[a.nak], yb = M.yoni.byNakshatra[b.nak];
  const points = {
    varna: M.varna.rank[M.varna.bySign[a.sign]] >= M.varna.rank[M.varna.bySign[b.sign]] ? 1 : 0,
    vashya: vashyaOf(a) === vashyaOf(b) ? M.vashya.same : M.vashya.other,
    tara: taraFrom(b.nak, a.nak) + taraFrom(a.nak, b.nak),
    yoni: ya === yb ? M.yoni.same : M.yoni.swornEnemies.some(([x, y]) => (x === ya && y === yb) || (x === yb && y === ya)) ? M.yoni.enemy : M.yoni.other,
    graha_maitri: lordOf(a.sign) === lordOf(b.sign) ? M.grahaMaitriPoints["friend+friend"] : pair(rel(lordOf(a.sign), lordOf(b.sign)), rel(lordOf(b.sign), lordOf(a.sign)), M.grahaMaitriPoints),
    gana: pair(M.gana.byNakshatra[a.nak], M.gana.byNakshatra[b.nak], M.gana.points),
    bhakoot: M.bhakoot.badDistances.some(([x, y]) => (dist === x && back === y) || (dist === y && back === x)) ? 0 : M.bhakoot.good,
    nadi: M.nadi.byNakshatra[a.nak] === M.nadi.byNakshatra[b.nak] ? M.nadi.same : M.nadi.different
  };
  const kootas = M.kootas.map(k => ({ koota: k.key, label: k.label, points: points[k.key], max: k.max, verified: k.verified, note: k.note || null }));
  const unverified = kootas.filter(k => !k.verified).map(k => k.label);
  return { first: { moonSign: a.place.signLabel, nakshatra: a.place.nakshatraLabel }, second: { moonSign: b.place.signLabel, nakshatra: b.place.nakshatraLabel },
    kootas, total: kootas.reduce((t, k) => t + k.points, 0), max: kootas.reduce((t, k) => t + k.max, 0),
    needsExpertReview: unverified.length > 0, unverifiedKootas: unverified, settings: { provider: p.provider, ayanamsa: p.ayanamsa } };
}
/* the choices the console offers: everything a store may pick, from the declaration */
function vocabulary() {
  const pick = l => (l || []).map(x => ({ key: x.key, label: x.label, note: x.note }));
  return { providers: pick(SEED.PROVIDERS), zodiacs: pick(SEED.ZODIACS), ayanamsas: pick(SEED.AYANAMSAS), houseSystems: pick(SEED.HOUSE_SYSTEMS), chartStyles: pick(SEED.CHART_STYLES) };
}

module.exports = { chart, panchang, match, vocabulary, kpLords, settingsOf, instantOf, julianDay, deltaT, BUILTIN, _internal: { sunApparent, moonApparent, planetApparent, siderealTime, angles, obliquity, HOUSE_METHODS, cuspAt } };
