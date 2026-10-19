/* Time (P11): calendars, chronologies, temporal units and conversions are Time's registries, not
   code in the offer engine; a place's time zone is Time's setting at the place, resolved up the
   place tree, so a country has its zone, a subdivision or a colony can have its own, and the
   offer engine reads the local date, weekday and hour where an exchange happens. */
"use strict";
const path = require("path");
const fs = require("fs");
const os = require("os");
const TMP = path.join(os.tmpdir(), "time-" + process.pid + ".db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
process.env.LX_DB = TMP;
const silence = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = silence;
const T = require("../lib/time.js");
const P = require("../lib/places.js");
const S = require("../lib/stores.js");
const goip = require("../lib/goip.js");
const SEED = require("../lib/seed/time.json");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };

console.log("time — the registries are Time's");
for (const [kind, name] of Object.entries(SEED.lists)) ok(!!db.get("SELECT 1 AS x FROM meta_lists WHERE name=?", name), "Time's " + kind + " are a registry list (" + name + ")");
ok(T.calendars().some(c => c.key === "mars_darian") && T.units().some(u => u.key === "sol"), "a Martian calendar and the sol are rows");
ok(T.calendar(T.defaultCalendar()) && T.defaultCalendar() === SEED.defaultCalendar, "the default calendar is declared, not written in code", T.defaultCalendar());
const src = fs.readFileSync(path.join(__dirname, "..", "lib", "goip.js"), "utf8");
ok(!/const (CALENDARS|CHRONOLOGIES|TEMPORAL_UNITS|TEMPORAL_CONVERSIONS) =/.test(src), "the offer engine holds no time list of its own");

console.log("time — a place's zone is Time's setting, resolved up the place tree");
const [code, zone] = Object.entries(SEED.countryZones).find(([c]) => P.country(c));
const country = P.country(code);
ok(T.zoneAt(country) === zone, "a country has its primary zone from the seed: " + code + " " + zone);
const sub = db.get("SELECT code FROM subdivisions WHERE country_code=? LIMIT 1", code);
if (sub) {
  ok(T.zoneAt(P.subdivision(sub.code)) === zone, "a subdivision is in its country's zone unless it has its own");
  T.setZone(P.subdivision(sub.code), "Pacific/Honolulu");
  ok(T.zoneAt(P.subdivision(sub.code)) === "Pacific/Honolulu" && T.zoneAt(country) === zone, "a zone set at a subdivision applies there, not to its country");
}
const mars = P.byPath("mars");
if (mars) {
  ok(T.zoneAt(mars) === SEED.defaultZone, "a place under no zone is in the default zone");
  T.setZone(mars, "MTC");
  ok(T.zoneAtPath("mars.olympus.sector-7") === "MTC", "a colony's own clock is a zone like any other, inherited below it");
  ok(T.local(new Date(), "MTC") === null, "a zone the host's clock does not know carries no local time");
}
ok(Object.values(SEED.countryZones).every(z => T.local(new Date(), z)), "every seeded zone is one the host's clock knows");
const noon = new Date("2026-01-03T23:30:00Z");
const ist = T.local(noon, "Asia/Kolkata");
ok(ist && ist.date === "2026-01-04" && ist.weekday === 0 && ist.hour === 5, "the local date, weekday and hour follow the zone (23:30 UTC Saturday is 05:00 Sunday in Kolkata)", ist);
ok(T.assignZones() === 0, "assigning the seed's zones again writes nothing");

console.log("time — the offer engine reads the zone where the exchange happens");
const tid = db.get("SELECT id FROM tenants ORDER BY id LIMIT 1").id;
const home = S.jurisdiction(tid);
const ctx = goip.resolveContext({ tenantId: tid });
ok(ctx.temporal.tz === T.zoneAt(P.byCode(home)) && ctx.temporal.local && ctx.temporal.local.zone === ctx.temporal.tz, "a store's exchange is in its jurisdiction's zone, with its local time", ctx.temporal);
if (mars) ok(goip.resolveContext({ tenantId: tid, spatial: { node: "mars.olympus.sector-7" } }).temporal.tz === "MTC", "an exchange on Mars is on Mars time");
ok(goip.resolveContext({ tenantId: tid, tz: "Asia/Tokyo" }).temporal.tz === "Asia/Tokyo", "a request may state its own zone");

for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
