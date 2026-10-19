/* LUXORA Platform — the kernel's shape part (FOUNDATIONS K05; owner Geo).

   A node whose kind carries a shape has, in any number of declared COORDINATE SYSTEMS, a point,
   box, ball or polygon, each in a time window. A coordinate system is data: its axes, their
   bounds and whether an axis wraps (a longitude does; a galactic distance does not). Nothing
   here assumes a planet: a shelf's millimetres, a city's latitude and longitude and a galaxy's
   light-years are all just declared systems. Any coordinate resolves to every node whose shape
   contains it — the shop, the city, the country, the continent and the planet at once. */
"use strict";

const { run, get, all } = require("./db.js");
const K = require("./kernel.js");
const { tx, append, fail, instant, nowIso, before, window, recordedSeq, believed, validAt, ns, keyOk, kindForNode, J, DOMAINS } = K.internal;
const EV = K.SEED.events;
const SHAPES = new Set(K.SEED.shapeTypes.map(t => t.key));

let ready = false;
function ensureTables() {
  if (ready) return;
  K.ensureTables();
  run(`CREATE TABLE IF NOT EXISTS k_coord_systems (
    id INTEGER PRIMARY KEY AUTOINCREMENT, namespace TEXT NOT NULL, system TEXT NOT NULL,
    owner TEXT NOT NULL, spec TEXT NOT NULL, rec_from INTEGER NOT NULL, rec_to INTEGER)`);
  run(`CREATE INDEX IF NOT EXISTS ix_k_coord ON k_coord_systems(namespace, system, rec_to)`);
  run(`CREATE TABLE IF NOT EXISTS k_shapes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, node TEXT NOT NULL, system TEXT NOT NULL, geom TEXT NOT NULL,
    valid_from TEXT NOT NULL, valid_to TEXT, rec_from INTEGER NOT NULL, rec_to INTEGER)`);
  run(`CREATE INDEX IF NOT EXISTS ix_k_shapes ON k_shapes(system, rec_to)`);
  run(`CREATE INDEX IF NOT EXISTS ix_k_shapes_node ON k_shapes(node, system, rec_to)`);
  ready = true;
}

/* ---------- coordinate systems ---------- */
function defineSystem(d, actor) {
  ensureTables();
  d = d || {};
  const namespace = ns(d.namespace), system = keyOk(d.system, "Coordinate system");
  if (!DOMAINS.has(d.owner)) fail("A coordinate system needs an owning domain from the register: " + d.owner);
  const axes = (d.axes || []).map(a => {
    keyOk(a.key, "Axis");
    const min = a.min == null ? null : Number(a.min), max = a.max == null ? null : Number(a.max);
    if ((min != null && !isFinite(min)) || (max != null && !isFinite(max)) || (min != null && max != null && !(min < max))) fail("Axis " + a.key + " needs min < max");
    if (a.wrap && (min == null || max == null)) fail("A wrapping axis needs both bounds: " + a.key);
    return { key: a.key, min, max, wrap: !!a.wrap, unit: a.unit || null };
  });
  if (!axes.length) fail("A coordinate system needs at least one axis");
  if (new Set(axes.map(a => a.key)).size !== axes.length) fail("An axis is declared twice");
  const spec = { label: d.label || system, axes };
  return tx(() => {
    const seq = append(EV.coordinateSystemDefined, { namespace, subject: system, actor, payload: { owner: d.owner, spec } });
    run("UPDATE k_coord_systems SET rec_to=? WHERE namespace=? AND system=? AND rec_to IS NULL", seq, namespace, system);
    run("INSERT INTO k_coord_systems(namespace,system,owner,spec,rec_from) VALUES(?,?,?,?,?)", namespace, system, d.owner, JSON.stringify(spec), seq);
    return systemOf(system, namespace);
  });
}
function systemOf(system, namespace) {
  ensureTables();
  const space = ns(namespace);
  const r = get("SELECT * FROM k_coord_systems WHERE namespace=? AND system=? AND rec_to IS NULL", space, system)
    || get("SELECT * FROM k_coord_systems WHERE namespace=? AND system=? AND rec_to IS NULL", K.SEED.defaultNamespace, system);
  return r ? { namespace: r.namespace, system: r.system, owner: r.owner, ...J(r.spec, {}) } : null;
}

/* ---------- geometry ---------- */
function checkPoint(S, p, label) {
  if (!Array.isArray(p) || p.length !== S.axes.length || p.some(x => typeof x !== "number" || !isFinite(x))) fail(`${label} needs ${S.axes.length} numbers (${S.axes.map(a => a.key).join(", ")})`);
  S.axes.forEach((a, i) => { if ((a.min != null && p[i] < a.min) || (a.max != null && p[i] > a.max)) fail(`${label}: ${a.key} is outside ${a.min}..${a.max}`); });
  return p;
}
function checkGeom(S, g) {
  if (!g || !SHAPES.has(g.type)) fail("Unknown shape type: " + (g && g.type));
  if (g.type === "point") return { type: "point", at: checkPoint(S, g.at, "point") };
  if (g.type === "box") {
    checkPoint(S, g.min, "box min"); checkPoint(S, g.max, "box max");
    /* min > max is allowed only on a wrapping axis, where the box crosses the seam */
    S.axes.forEach((a, i) => { if (g.min[i] > g.max[i] && !a.wrap) fail(`box: ${a.key} min is above max`); });
    return { type: "box", min: g.min, max: g.max };
  }
  if (g.type === "ball") {
    checkPoint(S, g.center, "ball centre");
    if (typeof g.radius !== "number" || !(g.radius >= 0)) fail("ball: radius must be a number ≥ 0");
    return { type: "ball", center: g.center, radius: g.radius };
  }
  if (S.axes.length < 2) fail("A polygon needs a system with at least two axes");
  if (!Array.isArray(g.ring) || g.ring.length < 3) fail("polygon: a ring needs at least three corners");
  const ring = g.ring.map((c, i) => { if (!Array.isArray(c) || c.length < 2 || c.slice(0, 2).some(x => typeof x !== "number" || !isFinite(x))) fail("polygon: corner " + i + " needs two numbers"); return [c[0], c[1]]; });
  return { type: "polygon", ring };
}
/* how each declared shape type contains a point — the declarations are lib/seed/kernel.json shapeTypes */
const inAxis = (a, lo, hi, v) => lo <= hi ? v >= lo && v <= hi : a.wrap && (v >= lo || v <= hi);
const CONTAINS = {
  point: (S, g, p) => g.at.every((x, i) => x === p[i]),
  box: (S, g, p) => S.axes.every((a, i) => inAxis(a, g.min[i], g.max[i], p[i])),
  ball: (S, g, p) => {
    let d2 = 0;
    S.axes.forEach((a, i) => { let d = Math.abs(p[i] - g.center[i]); if (a.wrap) d = Math.min(d, (a.max - a.min) - d); d2 += d * d; });
    return d2 <= g.radius * g.radius;
  },
  polygon: (S, g, p) => {
    const [x, y] = p; let inside = false;
    for (let i = 0, j = g.ring.length - 1; i < g.ring.length; j = i++) {
      const [xi, yi] = g.ring[i], [xj, yj] = g.ring[j];
      if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) inside = !inside;
    }
    return inside;
  }
};

/* ---------- shapes ---------- */
/* a node has one shape per system at a time: a new shape supersedes the overlapping part of the old */
function setShape(uid, system, geom, o, actor) {
  ensureTables();
  o = o || {};
  const { n, k } = kindForNode(uid);
  if (!k.shape) fail(`Kind ${k.kind} carries no shape`);
  const S = systemOf(system, n.namespace);
  if (!S) fail("Unknown coordinate system: " + system);
  const g = checkGeom(S, geom);
  const w = window(o);
  return tx(() => {
    const seq = append(EV.shapeRecorded, { namespace: n.namespace, subject: uid, actor, payload: { system, type: g.type, validFrom: w.from, validTo: w.to } });
    const hits = all("SELECT * FROM k_shapes WHERE node=? AND system=? AND rec_to IS NULL", uid, system)
      .filter(r => before(r.valid_from, w.to) && before(w.from, r.valid_to));
    for (const r of hits) {
      run("UPDATE k_shapes SET rec_to=? WHERE id=?", seq, r.id);
      if (r.valid_from < w.from) run("INSERT INTO k_shapes(node,system,geom,valid_from,valid_to,rec_from) VALUES(?,?,?,?,?,?)", uid, system, r.geom, r.valid_from, w.from, seq);
      if (before(w.to, r.valid_to)) run("INSERT INTO k_shapes(node,system,geom,valid_from,valid_to,rec_from) VALUES(?,?,?,?,?,?)", uid, system, r.geom, w.to, r.valid_to, seq);
    }
    run("INSERT INTO k_shapes(node,system,geom,valid_from,valid_to,rec_from) VALUES(?,?,?,?,?,?)", uid, system, JSON.stringify(g), w.from, w.to, seq);
    return seq;
  });
}
function shapeOf(uid, system, o) {
  ensureTables();
  o = o || {};
  const b = believed(recordedSeq(o.recorded)), v = validAt(instant(o.at, "at") || nowIso());
  const r = get(`SELECT geom FROM k_shapes WHERE node=? AND system=? AND ${b.sql} AND ${v.sql}`, uid, system, ...b.args, ...v.args);
  return r ? J(r.geom, null) : null;
}
/* every node whose shape in this system contains the coordinate, at a time */
function containing(system, point, o) {
  ensureTables();
  o = o || {};
  const S = systemOf(system, o.namespace);
  if (!S) fail("Unknown coordinate system: " + system);
  checkPoint(S, point, "coordinate");
  const b = believed(recordedSeq(o.recorded)), v = validAt(instant(o.at, "at") || nowIso());
  return all(`SELECT node, geom FROM k_shapes WHERE system=? AND ${b.sql} AND ${v.sql} ORDER BY id`, system, ...b.args, ...v.args)
    .filter(r => { const g = J(r.geom, null); return g && CONTAINS[g.type](S, g, point); })
    .map(r => r.node)
    .filter((u, i, arr) => arr.indexOf(u) === i)
    .filter(u => K.internal.listed([u], o).length);
}

module.exports = { ensureTables, defineSystem, systemOf, setShape, shapeOf, containing };
