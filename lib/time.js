/* LUXORA Platform — Time (P11, owner Time).

   Calendars, chronologies, temporal units and their conversions are Time's registries
   (lib/seed/time.json): a Martian sol, a lunar month and the Gregorian year are rows, not code.

   A place's time zone is Time's setting at the place, resolved up the place tree like its
   calendar: assigned at a country from the seed, assignable at any subdivision, city or colony
   under it, and a place under none is in the seed's default zone. A zone the host's clock
   knows (an IANA name) also answers the local date, weekday and hour at an instant; any other
   zone (a colony's own) is carried as declared. */
"use strict";

const TIME = require("./seed/time.json");
const reg = () => require("./registry.js");
const J = (v, d) => { try { return v == null || v === "" ? d : JSON.parse(v); } catch (e) { return d; } };

/* ---------- Time's registries ---------- */
function listOf(kind) {
  let l = null;
  try { l = reg().list(TIME.lists[kind]); } catch (e) { l = null; }
  const has = Array.isArray(l) ? l.length : (l && typeof l === "object" && Object.keys(l).length);
  return has ? l : TIME[kind];
}
const calendars = () => listOf("calendars");
const chronologies = () => listOf("chronologies");
const units = () => listOf("units");
const conversions = () => listOf("conversions");
const calendar = key => (calendars() || []).find(c => c && c.key === key) || null;
function defaultCalendar() {
  let d; try { d = require("./defaults.js").of(TIME.lists.calendars); } catch (e) { d = undefined; }
  return d || TIME.defaultCalendar;
}
/* rows an operator added to the offer engine's old lists join Time's, once (additive) */
function mergeLegacy() {
  const { all, run } = require("./db.js");
  let n = 0;
  for (const [kind, oldName] of Object.entries(TIME.legacyLists)) {
    const oldRow = all("SELECT items FROM meta_lists WHERE name=?", oldName)[0];
    const newRow = all("SELECT items FROM meta_lists WHERE name=?", TIME.lists[kind])[0];
    if (!oldRow || !newRow) continue;
    const prev = J(oldRow.items, null), cur = J(newRow.items, null);
    if (Array.isArray(prev) && Array.isArray(cur)) {
      const add = prev.filter(x => x && x.key && !cur.some(c => c && c.key === x.key));
      if (add.length) { run("UPDATE meta_lists SET items=? WHERE name=?", JSON.stringify(cur.concat(add)), TIME.lists[kind]); n += add.length; }
    } else if (prev && cur && typeof prev === "object" && typeof cur === "object" && !Array.isArray(prev)) {
      const add = Object.keys(prev).filter(k => !(k in cur));
      if (add.length) { const next = { ...cur }; for (const k of add) next[k] = prev[k]; run("UPDATE meta_lists SET items=? WHERE name=?", JSON.stringify(next), TIME.lists[kind]); n += add.length; }
    }
  }
  return n;
}

/* ---------- time zones: Time's setting at a place ---------- */
const P = () => require("./places.js");
const C = () => require("./kernel-context.js");
const K = () => require("./kernel.js");
function declare() {
  const st = TIME.zoneSetting, ns = P().NAMESPACE;
  const cur = C().settingOf(st.name, ns);
  if (!cur || cur.owner !== st.owner || cur.type !== st.type) C().declareSetting({ ...st, namespace: ns }, TIME.actor);
}
/* each seeded country's primary zone, where its place has none; a warm pass writes nothing */
function assignZones() {
  K().ensureTables(); C().ensureTables();
  return K().internal.tx(() => {
    declare();
    let n = 0;
    for (const [code, zone] of Object.entries(TIME.countryZones)) {
      const uid = P().country(code);
      if (!uid || C().assignedAt(TIME.zoneSetting.name, { namespace: P().NAMESPACE, scope: uid }) !== undefined) continue;
      C().assign(TIME.zoneSetting.name, zone, { namespace: P().NAMESPACE, scope: uid }, TIME.actor); n++;
    }
    return n;
  });
}
/* sets a place's zone (a country, a subdivision, a colony) — a zone the host's clock knows is
   checked; any other is a colony's own and is taken as declared */
function setZone(placeUid, zone, actor) {
  if (!placeUid) throw Object.assign(new Error("Unknown place"), { status: 400 });
  const z = String(zone || "").trim();
  if (!z) throw Object.assign(new Error("A time zone needs a name"), { status: 400 });
  return K().internal.tx(() => { declare(); return C().assign(TIME.zoneSetting.name, z, { namespace: P().NAMESPACE, scope: placeUid }, actor || TIME.actor); });
}
/* the zone at a place: the nearest assignment up the place tree, else the default zone */
function zoneAt(placeUid, o) {
  if (!placeUid) return TIME.defaultZone;
  const r = C().resolve(TIME.zoneSetting.name, { context: { [P().HIERARCHY]: placeUid }, namespaces: [P().NAMESPACE], at: o && o.at });
  return r && r.resolved ? r.value : TIME.defaultZone;
}
const zoneAtPath = path => zoneAt(P().byPath(path));
/* the zone of a store: its jurisdiction's */
const zoneOfStore = tid => zoneAt(P().byCode(require("./stores.js").jurisdiction(tid)));
/* the local date, weekday (0 = Sunday) and hour at an instant in a zone the host's clock knows;
   null for a zone it does not (a colony's own clock) */
const WEEKDAYS = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 };
function local(instant, zone) {
  try {
    const parts = Object.fromEntries(new Intl.DateTimeFormat("en-US", { timeZone: zone, year: "numeric", month: "2-digit", day: "2-digit", weekday: "short", hour: "2-digit", hourCycle: "h23" })
      .formatToParts(instant instanceof Date ? instant : new Date(instant)).map(p => [p.type, p.value]));
    return { zone, date: parts.year + "-" + parts.month + "-" + parts.day, weekday: WEEKDAYS[parts.weekday], hour: Number(parts.hour) };
  } catch (e) { return null; }
}

module.exports = { TIME, calendars, calendar, chronologies, units, conversions, defaultCalendar, mergeLegacy, declare, assignZones, setZone, zoneAt, zoneAtPath, zoneOfStore, local };
