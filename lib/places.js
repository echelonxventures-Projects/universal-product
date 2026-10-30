/* LUXORA Platform — places on the kernel (P09, owner Geo).

   Every place is a node of the declared place kind in one place tree (lib/seed/places.json):
   countries at the top — nothing above them is invented — and subdivisions under their country
   or their parent subdivision, to any depth. A country's code and a subdivision's code are
   identifiers in their declared schemes, and a row's universal ID becomes its node's, so a place
   keeps one identity across the move.

   Every write to a place — a console edit, global.js, the registry's seeding and repair — goes
   through this module's write path (through): the kernel first, the row in the same transaction.
   The boot pass (importRows) only IMPORTS rows the kernel has never seen, from an
   install that predates the place tree; it never changes a place that exists, so the kernel, not
   the table, is the record. A switched-off place is hidden (reversible); a deleted one is
   archived, so its history stays. */
"use strict";

const { all, get, run } = require("./db.js");
const K = require("./kernel.js");
const LC = require("./kernel-lifecycle.js");
const C = require("./kernel-context.js");
const SEED = require("./seed/places.json");
const M = SEED.master;
const NS = SEED.namespace;
const H = SEED.hierarchy.hierarchy;

const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
/* the setting whose value must name a currency in Value's master, its symbol and decimals */
const MONEY = () => SEED.settings.find(st => st.name === M.currencySetting);

/* declares the place kind, the place tree, the settings at a place and the coordinate systems
   when they are missing or differ from the seed */
function declare() {
  const k = K.kindOf(SEED.kind.kind, NS);
  const want = { ...SEED.kind, namespace: NS };
  if (!k || k.owner !== want.owner || !same(k.attributes.map(a => a.key), want.attributes.map(a => a.key)) || !same(k.schemes, want.schemes) || !same(k.parents, want.parents) || k.shape !== !!want.shape)
    K.defineKind(want, M.actor);
  if (!K.hierarchyOf(H, NS)) K.defineHierarchy({ ...SEED.hierarchy, namespace: NS }, M.actor);
  for (const st of SEED.settings.concat(SEED.placeSettings)) {
    const cur = C.settingOf(st.name, NS);
    if (!cur || cur.owner !== st.owner || cur.type !== st.type) C.declareSetting({ name: st.name, owner: st.owner, type: st.type, label: st.label, namespace: NS }, M.actor);
  }
  const SH = require("./kernel-shape.js");
  for (const cs of SEED.coordinateSystems) {
    const cur = SH.systemOf(cs.system, NS);
    if (!cur || !same(cur.axes.map(a => a.key), cs.axes.map(a => a.key))) SH.defineSystem({ ...cs, owner: SEED.kind.owner, namespace: NS }, M.actor);
  }
}

/* ============================== paths: every place, at any scale ==============================
   A place's path is its parent's path and its own segment ("earth.in.bihar.patna"): the offer
   engine scopes an exchange to a place and everything in it by path. A country's segment is its
   code, a subdivision's the part of its code after its country's; a declared entry with a `code`
   gives that place its declared path instead. */
const PS = M.pathScheme;
const byPath = path => nodeFor(PS, String(path || ""));
const pathOf = uid => (uid && K.identifiers(uid)[PS]) || null;
const ALIAS = new Map(SEED.declared.filter(d => d.code).map(d => [String(d.code).toUpperCase(), d.path]));
const parentPath = path => path.includes(".") ? path.slice(0, path.lastIndexOf(".")) : null;
function segmentOf(uid) {
  const ids = K.identifiers(uid);
  if (ids[M.countryScheme]) return ids[M.countryScheme].toLowerCase();
  if (ids[M.subdivisionScheme]) { const c = ids[M.subdivisionScheme]; return (c.includes("-") ? c.slice(c.indexOf("-") + 1) : c).toLowerCase(); }
  const own = ids[PS];
  return own ? own.slice(own.lastIndexOf(".") + 1) : null;
}
function wantedPath(uid) {
  const ids = K.identifiers(uid);
  const code = ids[M.countryScheme] || ids[M.subdivisionScheme];
  if (code && ALIAS.has(code)) return ALIAS.get(code);
  const seg = segmentOf(uid);
  if (!seg) return null;
  const parent = K.placementsOf(H, uid, { namespace: NS }).find(Boolean);
  if (!parent) return seg;
  const pp = pathOf(parent) || wantedPath(parent);
  return pp ? pp + "." + seg : null;
}
/* gives a place the path its position calls for, and its descendants theirs (after a move) */
function repath(uid, actor) {
  const want = wantedPath(uid), cur = pathOf(uid);
  if (!want || want === cur) return 0;
  if (cur) K.endIdentifier(uid, PS, cur, null, actor);
  K.assignIdentifier(uid, PS, want, {}, actor);
  let n = 1;
  for (const c of K.children(H, uid, { namespace: NS, includeHidden: true })) n += repath(c, actor);
  return n;
}
/* the place the countries sit under, once it is declared */
const countryParent = () => (M.countryParent ? byPath(M.countryParent) : null);

/* the declared places (bodies, colonies, cities…) are created once their parent exists; a
   country at the top moves under the declared country parent; every place gets its path. Runs at
   boot, before a seeding batch and after a country's subdivisions materialise. Idempotent: a warm
   pass writes nothing. Returns how many writes it made. */
function declarePlaces() {
  let n = 0;
  for (const d of SEED.declared.slice().sort((a, b) => a.path.split(".").length - b.path.split(".").length)) {
    if (d.code) continue;
    let uid = byPath(d.path);
    if (!uid) {
      const pp = parentPath(d.path), parent = pp ? byPath(pp) : null;
      if (pp && !parent) continue;
      const attrs = { name: d.name };
      for (const key of ["level", "system", "levels", "coordinate"]) if (d[key] != null) attrs[key] = d[key];
      uid = K.createNode(SEED.kind.kind, { namespace: NS, attributes: attrs, identifiers: { [PS]: d.path } }, M.actor);
      K.place(H, uid, parent, { namespace: NS }, M.actor);
      n++;
    }
    for (const [name, v] of Object.entries(d.settings || {})) if (C.assignedAt(name, { namespace: NS, scope: uid }) === undefined) { C.assign(name, v, { namespace: NS, scope: uid }, M.actor); n++; }
  }
  const top = countryParent();
  if (top) for (const uid of K.children(H, null, { namespace: NS, includeHidden: true })) {
    if (!K.identifiers(uid)[M.countryScheme]) continue;
    K.endPlacement(H, uid, null, null, { namespace: NS }, M.actor);
    K.place(H, uid, top, { namespace: NS }, M.actor);
    n++;
  }
  for (const uid of K.nodes(SEED.kind.kind, NS, { includeHidden: true })) if (!pathOf(uid)) n += repath(uid, M.actor);
  for (const [code, path] of ALIAS) { const uid = byCode(code); if (uid && pathOf(uid) !== path) n += repath(uid, M.actor); }
  return n;
}
/* a country's settings (currency, locale…) are assigned at its node from the master's columns */
function assignSettings(uid, row, stats, actor) {
  for (const st of SEED.settings) {
    const v = row[st.column];
    if (v == null || v === "") continue;
    if (C.assignedAt(st.name, { namespace: NS, scope: uid }) !== v) { C.assign(st.name, v, { namespace: NS, scope: uid }, actor); stats.assigned++; }
  }
}

function nodeFor(scheme, code) { return K.resolveIdentifier(scheme, code, {}); }
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

/* one row onto one node: create it, or record what changed — name, level, parent, shown/hidden */
function upsert(scheme, row, parent, level, stats, actor) {
  let uid = nodeFor(scheme, row.code);
  const attrs = { name: row.name };
  if (level) attrs.level = level;
  if (!uid) {
    const adopt = row.uid && UUID.test(row.uid) && !get("SELECT 1 AS x FROM k_nodes WHERE uid=?", String(row.uid).toLowerCase()) ? row.uid : undefined;
    uid = K.createNode(SEED.kind.kind, { namespace: NS, uid: adopt, attributes: attrs, identifiers: { [scheme]: row.code } }, actor);
    stats.created++;
  } else {
    const cur = K.attributes(uid) || {};
    const patch = {};
    for (const [k, v] of Object.entries(attrs)) if (cur[k] !== v) patch[k] = v;
    if (!level && cur.level != null) patch.level = null;
    if (Object.keys(patch).length) { K.record(uid, patch, {}, actor); stats.updated++; }
  }
  const now = K.placementsOf(H, uid, { namespace: NS });
  const want = parent || null;
  if (!(now.length === 1 && now[0] === want)) {
    for (const p of now) K.endPlacement(H, uid, p, null, { namespace: NS }, actor);
    K.place(H, uid, want, { namespace: NS }, actor);
    stats.placed++;
  }
  repath(uid, actor);
  const state = LC.nodeState(uid);
  const hidden = K.SEED.lifecycle.nodeStates.hidden, active = K.SEED.lifecycle.nodeStates.initial, archived = K.SEED.lifecycle.nodeStates.archived;
  const wantState = row.active === 0 ? hidden : active;
  if (state === archived && wantState === active) { LC.unhide(uid, actor); stats.restored++; }
  else if (state === archived && wantState === hidden) { LC.unhide(uid, actor); LC.hide(uid, actor); stats.restored++; }
  else if (state !== wantState) { wantState === hidden ? LC.hide(uid, actor) : LC.unhide(uid, actor); stats.states++; }
  return uid;
}

/* a column an install that predates the place tree may still carry, read from the catalogue —
   never by a failing select, which would abort the surrounding transaction on Postgres */
function hasColumn(col, table) {
  const t = String(table);
  if (!/^[a-z_]+$/.test(t)) return false;
  const D = require("./db.js");
  const cols = D.USE_PG
    ? all("SELECT column_name AS name FROM information_schema.columns WHERE table_name=?", t)
    : all(`PRAGMA table_info(${t})`);
  return cols.some(c => c.name === col);
}
/* imports, in one transaction, every country and subdivision row the kernel has never seen —
   an install that predates the place tree. A place that exists is never touched: its changes
   arrive through the write path. A legacy country column holding a setting (its currency, its
   locale) is carried onto the kernel where the place has no assignment yet; the column itself is
   left alone (scripts/retire-country-columns.js drops the retired ones, when an operator says so).
   A warm pass writes nothing. */
function importRows() {
  K.ensureTables(); LC.ensureTables();
  const stats = { created: 0, updated: 0, placed: 0, states: 0, archived: 0, restored: 0, assigned: 0 };
  K.internal.tx(() => {
    declare();
    const cols = SEED.settings.map(st => st.column).filter(c => hasColumn(c, M.table));
    for (const c of all(`SELECT code, name, active, uid${cols.map(x => ", " + x).join("")} FROM countries ORDER BY position, code`)) {
      const uid = nodeFor(M.countryScheme, c.code) || upsert(M.countryScheme, c, countryParent(), M.countryLevel, stats, M.importActor);
      if (cols.length) carrySettings(uid, c, stats);
    }
    const subs = all("SELECT rowid AS id, code, country_code, name, level, parent_id, active FROM subdivisions ORDER BY country_code, position, code");
    const byId = new Map(subs.map(s => [s.id, s]));
    /* parents before children, to any depth */
    const depth = s => { let d = 0, p = s; const guard = new Set(); while (p && p.parent_id && byId.has(p.parent_id) && !guard.has(p.id)) { guard.add(p.id); p = byId.get(p.parent_id); d++; } return d; };
    for (const s of subs.slice().sort((a, b) => depth(a) - depth(b))) {
      if (nodeFor(M.subdivisionScheme, s.code)) continue;
      const pr = s.parent_id && byId.get(s.parent_id);
      const parent = (pr && nodeFor(M.subdivisionScheme, pr.code)) || nodeFor(M.countryScheme, s.country_code);
      if (!parent) continue;
      upsert(M.subdivisionScheme, s, parent, s.level || null, stats, M.importActor);
    }
    stats.declared = declarePlaces();
    stats.legacyPaths = importLegacyPaths();
  });
  return stats;
}
/* drops the retired country columns, on an operator's explicit instruction only (never at boot):
   the rows are imported first, and nothing is dropped unless every country's settings are on the
   kernel. Returns the columns dropped. */
function retireColumns() {
  return K.internal.tx(() => {
    importRows();
    const present = M.retiredColumns.filter(c => hasColumn(c, M.table));
    if (!present.length) return [];
    const missing = [];
    for (const c of all("SELECT code FROM countries")) {
      const uid = nodeFor(M.countryScheme, c.code);
      for (const st of SEED.settings) if (!uid || C.assignedAt(st.name, { namespace: NS, scope: uid }) === undefined) missing.push(c.code + ":" + st.name);
    }
    if (missing.length) throw new Error("Not every country's settings are on the kernel: " + missing.slice(0, 20).join(", "));
    for (const col of present) run(`ALTER TABLE countries DROP COLUMN ${col}`);
    return present;
  });
}
/* a legacy column's value reaches the kernel only where the place has no assignment of its own */
function carrySettings(uid, row, stats) {
  for (const st of SEED.settings) {
    const v = row[st.column];
    if (v == null || v === "" || C.assignedAt(st.name, { namespace: NS, scope: uid }) !== undefined) continue;
    C.assign(st.name, v, { namespace: NS, scope: uid }, M.importActor); stats.assigned++;
  }
}
/* the values a new country row must still carry on an install whose table keeps the retired
   columns (NOT NULL there): its settings as given, its currency's symbol and decimals. Nothing
   reads them; they only let the row be written until the columns are retired. */
function legacyColumns(row) {
  const out = {};
  const present = M.retiredColumns.filter(c => hasColumn(c, M.table));
  if (!present.length) return out;
  const money = MONEY();
  const cur = money && row[money.column] ? require("./registry.js").currency(row[money.column]) : null;
  const from = { ...(cur ? { symbol: cur.symbol, decimals: cur.decimals } : {}) };
  for (const st of SEED.settings) from[st.column] = row[st.column];
  for (const col of present) if (from[col] != null && from[col] !== "") out[col] = from[col];
  return out;
}
/* a country row, as the write path writes it: its own columns, and the legacy ones while present */
function insertCountry(row) {
  const cols = { code: String(row.code).toUpperCase(), name: row.name, ...legacyColumns(row) };
  if (row.position != null) cols.position = Number(row.position);
  if (row.active != null) cols.active = row.active === false || row.active === 0 || row.active === "0" ? 0 : 1;
  const keys = Object.keys(cols);
  return run(`INSERT INTO countries(${keys.join(",")}) VALUES(${keys.map(() => "?").join(",")})`, ...keys.map(k => cols[k]));
}
/* several writes through the write path as one transaction (a seeding or repair pass) */
function batch(fn) {
  K.ensureTables(); LC.ensureTables();
  return K.internal.tx(() => { declare(); declarePlaces(); const out = fn(); declarePlaces(); return out; });
}

/* ============================== writes: the kernel first ==============================
   A write to a country or a subdivision is recorded on the kernel and the master row is
   written in the same transaction, so the two cannot disagree and a write the kernel refuses
   never reaches the row. `writeRow` is the caller's own row write (the entity engine's or
   global.js's); it returns { error } to refuse, which rolls the kernel change back too. */
const REFUSED = Symbol("refused");
function ensurePlace(scheme, code, row, parent, level) {
  const stats = { created: 0, updated: 0, placed: 0, states: 0, archived: 0, restored: 0, assigned: 0 };
  const uid = upsert(scheme, { ...row, code }, parent, level, stats, M.actor);
  return uid;
}
function putCountry(code, patch) {
  code = String(code || "").toUpperCase();
  const cur = get("SELECT code, name, active, uid FROM countries WHERE code=?", code) || {};
  const row = { ...cur, ...patch, code };
  if (!row.name) throw Object.assign(new Error("A country needs a name"), { status: 400 });
  /* a new country names every setting; an edit changes only the settings it sends */
  for (const st of SEED.settings) if (!cur.code && (row[st.column] == null || row[st.column] === "")) throw Object.assign(new Error("A country needs its " + st.label), { status: 400 });
  const money = MONEY();
  if (money && row[money.column] != null && row[money.column] !== "") {
    row[money.column] = String(row[money.column]).toUpperCase();
    /* a currency nobody holds yet is made in Value's master from the symbol the writer gave */
    if (!require("./registry.js").ensureCurrency(row[money.column], { symbol: row.symbol, decimals: row.decimals })) throw Object.assign(new Error("Unknown currency: " + row[money.column] + " — add it to the currencies, or give its symbol"), { status: 400 });
  }
  const uid = ensurePlace(M.countryScheme, code, { ...row, active: row.active === false || row.active === 0 || row.active === "0" ? 0 : 1 }, countryParent(), M.countryLevel);
  assignSettings(uid, row, { assigned: 0 }, M.actor);
  return uid;
}
function putSubdivision(code, patch) {
  code = String(code || "").toUpperCase();
  const cur = get("SELECT rowid AS id, code, country_code, name, level, parent_id, active FROM subdivisions WHERE code=?", code) || {};
  const row = { ...cur, ...patch, code };
  const pr = row.parent_id ? get("SELECT code FROM subdivisions WHERE rowid=?", Number(row.parent_id)) : null;
  const parent = pr ? nodeFor(M.subdivisionScheme, pr.code) : nodeFor(M.countryScheme, String(row.country_code || "").toUpperCase());
  if (!parent) throw Object.assign(new Error("A subdivision sits under a known country or subdivision"), { status: 400 });
  return ensurePlace(M.subdivisionScheme, code, { ...row, active: row.active === false || row.active === 0 || row.active === "0" ? 0 : 1 }, parent, row.level || null);
}
function archiveCode(scheme, code) {
  const uid = nodeFor(scheme, String(code || "").toUpperCase());
  if (uid && LC.nodeState(uid) !== K.SEED.lifecycle.nodeStates.archived) LC.archive(uid, M.actor);
  return uid;
}
/* the entity engine's writer for the built-in country and subdivision entities: `code` is the
   place's code, `removing` whether the write takes the place away */
function through(removing, key, row, code, writeRow) {
  try {
    return K.internal.tx(() => {
      K.ensureTables(); LC.ensureTables(); declare();
      if (key === "country") {
        if (removing) { for (const s of all("SELECT code FROM subdivisions WHERE country_code=?", String(code).toUpperCase())) archiveCode(M.subdivisionScheme, s.code); archiveCode(M.countryScheme, code); }
        else putCountry(code, row || {});
      } else if (key === "subdivision") {
        if (removing) archiveCode(M.subdivisionScheme, code);
        else putSubdivision(code, row || {});
      }
      const out = writeRow();
      if (out && out.error) throw Object.assign(new Error(out.error), { [REFUSED]: out });
      /* the row carries its node's universal ID: one identity for the place */
      if (key === "country" && !removing) { const n = nodeFor(M.countryScheme, String(code).toUpperCase()); if (n) run("UPDATE countries SET uid=? WHERE code=?", n, String(code).toUpperCase()); }
      return out;
    });
  } catch (e) {
    if (e[REFUSED]) return e[REFUSED];
    if (e.status === 400) return { error: e.message };
    throw e;
  }
}

/* a country's subdivisions leave with it: their places are archived, deepest first, and the rows go */
function withdrawSubdivisions(countryCode, deleteRows) {
  return K.internal.tx(() => {
    K.ensureTables(); LC.ensureTables();
    for (const r of all("SELECT code FROM subdivisions WHERE country_code=? ORDER BY parent_id IS NULL, code", String(countryCode).toUpperCase())) archiveCode(M.subdivisionScheme, r.code);
    return deleteRows();
  });
}

/* what applies at a place, answered by the resolver: each declared setting (currency, locale…)
   by its name, nearest assignment up the place tree first. A code with no place answers {}. */
function facts(code, o) {
  const uid = nodeFor(M.countryScheme, String(code || "").toUpperCase()) || nodeFor(M.subdivisionScheme, String(code || "").toUpperCase());
  if (!uid) return {};
  const out = {};
  for (const st of SEED.settings) {
    const r = C.resolve(st.name, { context: { [H]: uid }, namespaces: [NS], at: o && o.at });
    if (r.resolved) out[st.column] = r.value;
  }
  return out;
}

/* the entity engine's hooks for the fields this writer holds (stored: false): a country row is
   read with its settings resolved at its place and its currency's symbol and decimals, and a new
   one is written with the legacy columns its table may still require */
function read(key, row) {
  return key === "country" ? require("./registry.js").withFacts(row) : row;
}
function columns(key, row) {
  return key === "country" ? legacyColumns(row) : {};
}
/* the countries at which a setting holds a value now — "which countries use this currency" */
function using(settingColumn, value) {
  const st = SEED.settings.find(x => x.column === settingColumn);
  if (!st) return [];
  K.ensureTables();
  return C.scopesWith(st.name, value, { namespace: NS }).map(uid => K.identifiers(uid)[M.countryScheme]).filter(Boolean);
}

/* a place's own code (its country or subdivision code), and the country a place lies in: itself,
   or the nearest place above it that is a country */
function codeOf(uid) {
  const ids = uid ? K.identifiers(uid) : {};
  return ids[M.countryScheme] || ids[M.subdivisionScheme] || null;
}
function countryOf(uid, o) {
  if (!uid) return null;
  const own = K.identifiers(uid)[M.countryScheme];
  if (own) return own;
  for (const a of K.ancestors(H, uid, { namespace: NS, includeHidden: true, at: o && o.at })) { const c = K.identifiers(a)[M.countryScheme]; if (c) return c; }
  return null;
}
/* the place a code names: a country's or a subdivision's */
const byCode = code => nodeFor(M.countryScheme, String(code || "").toUpperCase()) || nodeFor(M.subdivisionScheme, String(code || "").toUpperCase());

/* ============================== places at any scale, by path ==============================
   What the offer engine (and any caller) reads of a place it names by path. A place's system is
   the one its nearest declaring ancestor heads (a planet heads its administrative system); a
   place under none is in the declared system. Its calendar is Time's setting, nearest up. */
function systemOf(uid) {
  for (const u of [uid, ...K.ancestors(H, uid, { namespace: NS })]) { const a = K.attributes(u) || {}; if (a.system) return a.system; }
  return M.declaredSystem;
}
function spatial(path) {
  const uid = byPath(path);
  if (!uid) return null;
  const a = K.attributes(uid) || {};
  return { key: path, name: a.name, level: a.level || null, system: systemOf(uid), parent: parentPath(path), coordinate: a.coordinate || null };
}
function calendarAt(path) {
  const uid = byPath(path);
  if (!uid) return null;
  const st = SEED.placeSettings.find(x => x.name === M.calendarSetting);
  const r = st ? C.resolve(st.name, { context: { [H]: uid }, namespaces: [NS] }) : null;
  return r && r.resolved ? r.value : null;
}
/* the place systems: each place that heads one, with its levels, coordinates and calendar */
function systems() {
  const out = [];
  for (const uid of K.nodes(SEED.kind.kind, NS)) {
    const a = K.attributes(uid) || {};
    if (!a.system) continue;
    const path = pathOf(uid);
    out.push({ key: a.system, name: a.name, body: path, levels: a.levels || [], coordinate: a.coordinate || null, calendar: calendarAt(path) });
  }
  out.push({ key: M.declaredSystem, name: M.declaredSystem, body: null, levels: [], coordinate: null, calendar: null });
  return out;
}
function coordinateSystems() {
  const SH = require("./kernel-shape.js");
  return SEED.coordinateSystems.map(cs => SH.systemOf(cs.system, NS)).filter(Boolean).map(x => ({ key: x.system, name: x.label, axes: x.axes.map(a => a.key), units: x.axes.map(a => a.unit) }));
}
/* every place with a path, as { key, name, system, level, parent } */
function placesByPath() {
  return K.nodes(SEED.kind.kind, NS).map(uid => pathOf(uid) && spatial(pathOf(uid))).filter(Boolean).sort((a, b) => a.key < b.key ? -1 : 1);
}
/* declares a place at runtime — a new world, a colony, a district — under the place its path
   names (which must exist), or at the top; the kernel first, nothing else to write */
function putPlace(d, actor) {
  const path = String((d && d.path) || "").trim().toLowerCase();
  if (!/^[a-z0-9][a-z0-9_-]*(\.[a-z0-9][a-z0-9_-]*)*$/.test(path)) throw Object.assign(new Error("A place path is dot-separated segments of letters, digits, - and _"), { status: 400 });
  if (!d.name) throw Object.assign(new Error("A place needs a name"), { status: 400 });
  return K.internal.tx(() => {
    declare();
    const pp = parentPath(path), parent = pp ? byPath(pp) : null;
    if (pp && !parent) throw Object.assign(new Error("No place at " + pp), { status: 400 });
    const attrs = { name: String(d.name) };
    for (const key of ["level", "system", "levels", "coordinate"]) if (d[key] != null && d[key] !== "") attrs[key] = d[key];
    let uid = byPath(path);
    if (uid) { K.record(uid, attrs, {}, actor || M.actor); return uid; }
    uid = K.createNode(SEED.kind.kind, { namespace: NS, attributes: attrs, identifiers: { [PS]: path } }, actor || M.actor);
    K.place(H, uid, parent, { namespace: NS }, actor || M.actor);
    return uid;
  });
}

/* places an operator added to the offer engine's old spatial list (an install from before the
   place tree) are declared here once, parents first; a path a place already has is skipped */
function importLegacyPaths() {
  const row = get("SELECT items FROM meta_lists WHERE name=?", M.legacyPathList);
  let list = []; try { list = row ? JSON.parse(row.items) : []; } catch (e) { list = []; }
  let n = 0;
  for (const x of (Array.isArray(list) ? list : []).filter(x => x && x.key).sort((a, b) => String(a.key).split(".").length - String(b.key).split(".").length)) {
    const path = String(x.key).toLowerCase();
    if (byPath(path)) continue;
    const pp = parentPath(path);
    if (pp && !byPath(pp)) continue;
    putPlace({ path, name: x.name || path, level: x.level }, M.importActor); n++;
  }
  return n;
}

/* reads, for callers moving onto the kernel */
const country = code => nodeFor(M.countryScheme, String(code || "").toUpperCase());
const subdivision = code => nodeFor(M.subdivisionScheme, String(code || "").toUpperCase());

module.exports = { DECLARED_SYSTEM: M.declaredSystem, importLegacyPaths, byPath, pathOf, spatial, calendarAt, systems, coordinateSystems, placesByPath, putPlace, declarePlaces, TABLE: M.table, codeOf, countryOf, byCode, RETIRED: M.retiredColumns, declare, importRows, retireColumns, batch, facts, read, columns, using, insertCountry, hasColumn, putCountry, putSubdivision, through, withdrawSubdivisions, country, subdivision, HIERARCHY: H, NAMESPACE: NS };
