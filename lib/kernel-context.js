/* LUXORA Platform — the kernel's context parts: scope (K11) and resolution (K12), owner
   Context; views (K10), owner Perspective.

   SCOPE. A setting is declared once (its key, owner and value type). A value is ASSIGNED in a
   namespace ("platform", "tenant:42", …) at a scope, and the scope is simply a node: a place, a
   store, a channel, a language, a segment, a device type or a person are all nodes of declared
   kinds, so the scope levels are data and a new level needs no code. A value assigned with no
   scope holds across its whole namespace. Every assignment has a time window.

   RESOLUTION. One resolver answers "what applies here and now". The caller gives its context —
   for each hierarchy, the node it stands at — and the namespaces to consult, most specific
   first. Walking up each hierarchy from that node, the nearest assignment wins; a declared
   resolution profile orders the hierarchies when more than one is in play. The answer carries
   where it came from (namespace, hierarchy, node, distance); when nothing is assigned the answer
   is "unresolved" — a default is an assignment like any other, never a value invented in code.

   VIEWS. A view selects subtrees of hierarchies — a root, a depth, the kinds to include — and
   labels, by reference. Its nodes are computed when asked, so a view never holds a copy and
   always shows the master as it is. */
"use strict";

const { run, get, all } = require("./db.js");
const K = require("./kernel.js");
const { tx, append, fail, instant, nowIso, before, window, recordedSeq, believed, validAt, ns, keyOk, nodeRow, J, TYPE_CHECKS, VALUE_TYPES, DOMAINS } = K.internal;
const EV = K.SEED.events;

let ready = false;
function ensureTables() {
  if (ready) return;
  K.ensureTables();
  /* one table of named declarations per family: settings, resolution profiles, views */
  run(`CREATE TABLE IF NOT EXISTS k_declarations (
    id INTEGER PRIMARY KEY AUTOINCREMENT, family TEXT NOT NULL, namespace TEXT NOT NULL, name TEXT NOT NULL,
    owner TEXT NOT NULL, spec TEXT NOT NULL, rec_from INTEGER NOT NULL, rec_to INTEGER)`);
  run(`CREATE INDEX IF NOT EXISTS ix_k_decl ON k_declarations(family, namespace, name, rec_to)`);
  run(`CREATE TABLE IF NOT EXISTS k_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT, namespace TEXT NOT NULL, setting TEXT NOT NULL, scope TEXT,
    value TEXT NOT NULL, valid_from TEXT NOT NULL, valid_to TEXT, rec_from INTEGER NOT NULL, rec_to INTEGER)`);
  run(`CREATE INDEX IF NOT EXISTS ix_k_assign ON k_assignments(setting, namespace, scope, rec_to)`);
  ready = true;
}

/* ---------- declarations ---------- */
const FAMILY = { setting: "setting", resolution: "resolution", view: "view" };
function declare(family, event, d, spec, actor) {
  ensureTables();
  const namespace = ns(d.namespace), name = keyOk(d.name, family);
  if (!DOMAINS.has(d.owner)) fail(`A ${family} needs an owning domain from the register: ${d.owner}`);
  return tx(() => {
    const seq = append(event, { namespace, subject: name, actor, payload: { owner: d.owner, spec } });
    run("UPDATE k_declarations SET rec_to=? WHERE family=? AND namespace=? AND name=? AND rec_to IS NULL", seq, family, namespace, name);
    run("INSERT INTO k_declarations(family,namespace,name,owner,spec,rec_from) VALUES(?,?,?,?,?,?)", family, namespace, name, d.owner, JSON.stringify(spec), seq);
    return declared(family, name, namespace);
  });
}
/* a declaration in a namespace, else the platform's */
function declared(family, name, namespace) {
  ensureTables();
  const q = "SELECT * FROM k_declarations WHERE family=? AND namespace=? AND name=? AND rec_to IS NULL";
  const r = get(q, family, ns(namespace), name) || get(q, family, K.SEED.defaultNamespace, name);
  return r ? { namespace: r.namespace, name: r.name, owner: r.owner, ...J(r.spec, {}) } : null;
}

/* ============================== K11 scope ============================== */
function declareSetting(d, actor) {
  d = d || {};
  if (!VALUE_TYPES.has(d.type)) fail("Unknown value type for setting " + d.name + ": " + d.type);
  return declare(FAMILY.setting, EV.settingDeclared, d, { label: d.label || d.name, type: d.type }, actor);
}
const settingOf = (name, namespace) => declared(FAMILY.setting, name, namespace);
/* assigns a value in a namespace at a scope node (null: the whole namespace), in a window;
   the overlapping part of any earlier assignment at the same place is superseded */
function assign(setting, value, o, actor) {
  ensureTables();
  o = o || {};
  const namespace = ns(o.namespace);
  const S = settingOf(setting, namespace);
  if (!S) fail("Unknown setting: " + setting);
  if (value === null || value === undefined || !TYPE_CHECKS[S.type](value)) fail(`${setting} must be ${S.type}`);
  const scope = o.scope == null ? null : String(o.scope);
  if (scope && !nodeRow(scope)) fail("A scope must be a node: " + scope);
  const w = window(o);
  const at = scope == null ? "scope IS NULL" : "scope=?", args = scope == null ? [] : [scope];
  return tx(() => {
    const seq = append(EV.valueAssigned, { namespace, subject: setting, actor, payload: { scope, value, validFrom: w.from, validTo: w.to } });
    const hits = all(`SELECT * FROM k_assignments WHERE setting=? AND namespace=? AND ${at} AND rec_to IS NULL`, setting, namespace, ...args)
      .filter(r => before(r.valid_from, w.to) && before(w.from, r.valid_to));
    for (const r of hits) {
      run("UPDATE k_assignments SET rec_to=? WHERE id=?", seq, r.id);
      if (r.valid_from < w.from) run("INSERT INTO k_assignments(namespace,setting,scope,value,valid_from,valid_to,rec_from) VALUES(?,?,?,?,?,?,?)", namespace, setting, scope, r.value, r.valid_from, w.from, seq);
      if (before(w.to, r.valid_to)) run("INSERT INTO k_assignments(namespace,setting,scope,value,valid_from,valid_to,rec_from) VALUES(?,?,?,?,?,?,?)", namespace, setting, scope, r.value, w.to, r.valid_to, seq);
    }
    run("INSERT INTO k_assignments(namespace,setting,scope,value,valid_from,valid_to,rec_from) VALUES(?,?,?,?,?,?,?)", namespace, setting, scope, JSON.stringify(value), w.from, w.to, seq);
    return seq;
  });
}

/* ============================== K12 resolution ============================== */
function defineResolution(d, actor) {
  d = d || {};
  const order = (d.order || []).map(h => keyOk(h, "Hierarchy"));
  if (!order.length) fail("A resolution profile orders at least one hierarchy");
  for (const h of order) if (!K.hierarchyOf(h, d.namespace)) fail("Unknown hierarchy: " + h);
  return declare(FAMILY.resolution, EV.resolutionDefined, d, { label: d.label || d.name, order }, actor);
}
/* resolve(setting, { context: { <hierarchy>: <node uid> }, namespaces: [most specific first],
   profile: <resolution profile>, at, recorded }) */
function resolve(setting, o) {
  ensureTables();
  o = o || {};
  const spaces = (o.namespaces && o.namespaces.length ? o.namespaces : [K.SEED.defaultNamespace]).map(ns);
  const context = o.context || {};
  const profile = o.profile ? declared(FAMILY.resolution, o.profile, spaces[0]) : null;
  if (o.profile && !profile) fail("Unknown resolution profile: " + o.profile);
  const hierarchies = profile ? profile.order.filter(h => context[h]) : Object.keys(context);
  const atT = instant(o.at, "at") || nowIso();
  const b = believed(recordedSeq(o.recorded)), v = validAt(atT);
  const valueAt = (space, scope) => {
    const r = get(`SELECT value FROM k_assignments WHERE setting=? AND namespace=? AND ${scope == null ? "scope IS NULL" : "scope=?"} AND ${b.sql} AND ${v.sql}`,
      setting, space, ...(scope == null ? [] : [scope]), ...b.args, ...v.args);
    return r ? { value: J(r.value, null) } : null;
  };
  const tried = [];
  for (const space of spaces) {
    if (!settingOf(setting, space)) continue;
    for (const h of hierarchies) {
      /* breadth-first up the hierarchy: distance 0 is the context node itself; at one distance a
         node in many places may reach several candidates — the first placed wins, and the answer
         says it was ambiguous */
      let level = [context[h]], distance = 0;
      const seen = new Set(level);
      while (level.length) {
        const found = level.map(n => ({ node: n, hit: valueAt(space, n) })).filter(x => x.hit);
        tried.push({ namespace: space, hierarchy: h, distance, nodes: level.length });
        if (found.length) return { resolved: true, value: found[0].hit.value, from: { namespace: space, hierarchy: h, node: found[0].node, distance }, ambiguous: found.length > 1 && new Set(found.map(f => JSON.stringify(f.hit.value))).size > 1, tried };
        const next = [];
        for (const n of level) for (const p of K.parents(h, n, { at: atT, recorded: o.recorded, namespace: space })) if (!seen.has(p)) { seen.add(p); next.push(p); }
        level = next; distance++;
      }
    }
    const whole = valueAt(space, null);
    tried.push({ namespace: space, hierarchy: null, distance: null, nodes: 0 });
    if (whole) return { resolved: true, value: whole.value, from: { namespace: space, hierarchy: null, node: null, distance: null }, ambiguous: false, tried };
  }
  return { resolved: false, value: undefined, from: null, ambiguous: false, tried };
}

/* ============================== K10 views ============================== */
function defineView(d, actor) {
  d = d || {};
  const selects = (d.selects || []).map(s => {
    keyOk(s.hierarchy, "Hierarchy");
    if (!K.hierarchyOf(s.hierarchy, d.namespace)) fail("Unknown hierarchy: " + s.hierarchy);
    if (s.root != null && !nodeRow(s.root)) fail("A view's root must be a node: " + s.root);
    const depth = s.depth == null ? null : Number(s.depth);
    if (depth != null && !(Number.isInteger(depth) && depth >= 0)) fail("A view's depth is a whole number ≥ 0");
    return { hierarchy: s.hierarchy, root: s.root == null ? null : String(s.root), depth, kinds: (s.kinds || []).map(k => keyOk(k, "Kind")), includeRoot: s.includeRoot !== false };
  });
  if (!selects.length) fail("A view selects at least one subtree");
  const labels = {};
  for (const [uid, label] of Object.entries(d.labels || {})) { if (!nodeRow(uid)) fail("A label must name a node: " + uid); labels[uid] = String(label); }
  return declare(FAMILY.view, EV.viewDefined, d, { label: d.label || d.name, selects, labels }, actor);
}
const viewOf = (name, namespace) => declared(FAMILY.view, name, namespace);
/* the view's nodes now (or at a time): computed from the master, never stored */
function viewNodes(name, o) {
  o = o || {};
  const V = viewOf(name, o.namespace);
  if (!V) fail("Unknown view: " + name);
  const out = new Map();
  for (const s of V.selects) {
    const opt = { at: o.at, recorded: o.recorded, depth: s.depth == null ? undefined : s.depth };
    const found = s.root == null
      ? K.children(s.hierarchy, null, opt).flatMap(top => [top, ...(s.depth === 0 ? [] : K.descendants(s.hierarchy, top, { ...opt, depth: s.depth == null ? undefined : s.depth - 1 }))])
      : [...(s.includeRoot ? [s.root] : []), ...K.descendants(s.hierarchy, s.root, opt)];
    for (const uid of found) {
      if (out.has(uid)) continue;
      const kind = nodeRow(uid).kind;
      if (s.kinds.length && !s.kinds.includes(kind)) continue;
      out.set(uid, { uid, kind, hierarchy: s.hierarchy, label: V.labels[uid] || null });
    }
  }
  return [...out.values()];
}

module.exports = { ensureTables, declareSetting, settingOf, assign, defineResolution, resolve, defineView, viewOf, viewNodes };
