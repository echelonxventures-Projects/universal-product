/* LUXORA Platform — where a store delivers: the places it serves, named by postcode.

   An area is a list of postcodes, beginnings of postcodes (560*) and ranges (110001-110099). With
   the capability on and any area set, an order to an address outside every active area is refused
   before anything is charged; an area may add its own fee and days. Capability: serviceable_areas. */
"use strict";

const db = () => require("./db.js");
const caps = () => require("./capabilities.js");
const fail = (msg, status) => Object.assign(new Error(msg), { status: status || 400 });
const on = tid => caps().on(Number(tid), "serviceable_areas");
const norm = z => String(z || "").toUpperCase().replace(/[^A-Z0-9]/g, "");
function rules(text) {
  return String(text || "").split(/[\s,;]+/).filter(Boolean).map(r => {
    const m = /^(\d{3,10})-(\d{3,10})$/.exec(r);
    if (m) { if (m[1].length !== m[2].length || Number(m[2]) < Number(m[1])) throw fail("A range runs from a lower to a higher postcode of the same length: " + r); return { from: m[1], to: m[2] }; }
    const star = r.endsWith("*"), z = norm(star ? r.slice(0, -1) : r);
    if (!z || z.length > 10) throw fail("Not a postcode: " + r);
    return star ? { start: z } : { is: z };
  });
}
const holds = (rs, z) => rs.some(r => r.is ? r.is === z : r.start ? z.startsWith(r.start) : z.length === r.from.length && /^\d+$/.test(z) && z >= r.from && z <= r.to);
const list = tid => db().all("SELECT * FROM serviceable_areas WHERE tenant_id=? ORDER BY name", Number(tid));
function save(tid, input) {
  if (!on(tid)) throw fail("Serviceable areas are not available in this store", 403);
  const i = input || {}, name = String(i.name || "").trim().slice(0, 80), codes = String(i.postcodes || "").trim().slice(0, 20000);
  if (!name) throw fail("An area needs a name");
  if (!rules(codes).length) throw fail("List the postcodes it covers");
  const v = [name, codes, Math.max(0, +Number(i.fee || 0).toFixed(2)), i.extra_days === "" || i.extra_days == null ? 0 : Math.max(0, Math.min(60, Math.floor(Number(i.extra_days) || 0))), i.active === false || i.active === 0 ? 0 : 1];
  if (i.id) { if (!db().run("UPDATE serviceable_areas SET name=?,postcodes=?,fee=?,extra_days=?,active=? WHERE id=? AND tenant_id=?", ...v, Number(i.id), Number(tid)).changes) throw fail("Area not found", 404); }
  else db().run("INSERT INTO serviceable_areas(name,postcodes,fee,extra_days,active,tenant_id) VALUES(?,?,?,?,?,?)", ...v, Number(tid));
  return list(tid);
}
function remove(tid, id) { if (!db().run("DELETE FROM serviceable_areas WHERE id=? AND tenant_id=?", Number(id), Number(tid)).changes) throw fail("Area not found", 404); return list(tid); }
/* { served, area?, fee, extra_days }: a store with no area set serves everywhere */
function check(tid, postcode) {
  const areas = on(tid) ? list(tid).filter(a => a.active) : [];
  if (!areas.length) return { served: true, limited: false, fee: 0, extra_days: 0 };
  const z = norm(postcode), a = z && areas.find(x => { try { return holds(rules(x.postcodes), z); } catch (e) { return false; } });
  return a ? { served: true, limited: true, area: a.name, fee: a.fee, extra_days: a.extra_days } : { served: false, limited: true, fee: 0, extra_days: 0 };
}
module.exports = { on, list, save, remove, check, rules, holds };
