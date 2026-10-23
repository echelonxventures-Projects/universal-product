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
const { tx, append, fail, instant, nowIso, before, window, recordedSeq, believed, validAt, ns, keyOk, scopeOk, nodeRow, J, TYPE_CHECKS, VALUE_TYPES, DOMAINS, ensureColumn } = K.internal;
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
  /* a declaration may belong to a scope node inside its namespace; null is the whole namespace */
  ensureColumn("k_declarations", "scope", "TEXT");
  ready = true;
}

/* ---------- declarations ---------- */
const FAMILY = { setting: "setting", resolution: "resolution", view: "view" };
function declare(family, event, d, spec, actor) {
  ensureTables();
  const namespace = ns(d.namespace), name = keyOk(d.name, family), scope = scopeOk(d.scope);
  if (!DOMAINS.has(d.owner)) fail(`A ${family} needs an owning domain from the register: ${d.owner}`);
  return tx(() => {
    const seq = append(event, { namespace, subject: name, actor, payload: { owner: d.owner, scope, spec } });
    run(`UPDATE k_declarations SET rec_to=? WHERE family=? AND namespace=? AND name=? AND ${scope == null ? "scope IS NULL" : "scope=?"} AND rec_to IS NULL`, seq, family, namespace, name, ...(scope == null ? [] : [scope]));
    run("INSERT INTO k_declarations(family,namespace,name,owner,spec,scope,rec_from) VALUES(?,?,?,?,?,?,?)", family, namespace, name, d.owner, JSON.stringify(spec), scope, seq);
    return declared(family, name, namespace, scope);
  });
}
/* a declaration at a scope, else across the namespace, else the platform's */
function declared(family, name, namespace, scope) {
  ensureTables();
  const q = "SELECT * FROM k_declarations WHERE family=? AND namespace=? AND name=? AND rec_to IS NULL";
  const r = (scope ? get(q + " AND scope=?", family, ns(namespace), name, String(scope)) : null)
    || get(q + " AND scope IS NULL", family, ns(namespace), name) || get(q + " AND scope IS NULL", family, K.SEED.defaultNamespace, name);
  return r ? { namespace: r.namespace, name: r.name, owner: r.owner, scope: r.scope || null, ...J(r.spec, {}) } : null;
}

/* ============================== K11 scope ============================== */
function declareSetting(d, actor) {
  d = d || {};
  if (!VALUE_TYPES.has(d.type)) fail("Unknown value type for setting " + d.name + ": " + d.type);
  return declare(FAMILY.setting, EV.settingDeclared, d, { label: d.label || d.name, type: d.type }, actor);
}
const settingOf = (name, namespace, scope) => declared(FAMILY.setting, name, namespace, scope);
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

/* the value assigned at exactly one scope (no walking), or undefined */
function assignedAt(setting, o) {
  ensureTables();
  o = o || {};
  const space = ns(o.namespace), scope = o.scope == null ? null : String(o.scope);
  const b = believed(recordedSeq(o.recorded)), v = validAt(instant(o.at, "at") || nowIso());
  const r = get(`SELECT value FROM k_assignments WHERE setting=? AND namespace=? AND ${scope == null ? "scope IS NULL" : "scope=?"} AND ${b.sql} AND ${v.sql}`,
    setting, space, ...(scope == null ? [] : [scope]), ...b.args, ...v.args);
  return r ? J(r.value, null) : undefined;
}
/* the scopes at which a value is assigned now (or at `at`, as recorded at `recorded`): who uses it */
function scopesWith(setting, value, o) {
  ensureTables();
  o = o || {};
  const space = ns(o.namespace);
  const b = believed(recordedSeq(o.recorded)), v = validAt(instant(o.at, "at") || nowIso());
  return all(`SELECT scope FROM k_assignments WHERE setting=? AND namespace=? AND value=? AND scope IS NOT NULL AND ${b.sql} AND ${v.sql}`,
    setting, space, JSON.stringify(value), ...b.args, ...v.args).map(r => r.scope);
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
  const profile = o.profile ? declared(FAMILY.resolution, o.profile, spaces[0], o.declaredAt) : null;
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
  /* each grouping declares its parameters and what each must be (lib/seed/kernel.json groupings) */
  const PARAM = {
    key: (v, name) => keyOk(v, name),
    hierarchy: (v, name) => { keyOk(v, name); if (!K.hierarchyOf(v, d.namespace, d.scope)) fail("Unknown hierarchy: " + v); return v; }
  };
  const groupBy = (d.groupBy || []).map(g => {
    const decl = g && GROUPING_DECL.get(g.by);
    if (!decl || !GROUPINGS[g.by]) fail("Unknown grouping: " + (g && g.by));
    return Object.entries(decl.params || {}).reduce((out, [name, type]) => (out[name] = PARAM[type](g[name], name), out), { by: g.by });
  });
  return declare(FAMILY.view, EV.viewDefined, d, { label: d.label || d.name, selects, labels, groupBy }, actor);
}
const viewOf = (name, namespace, scope) => declared(FAMILY.view, name, namespace, scope);
/* view groupings (lib/seed/kernel.json groupings): each declared grouping's key for one node */
const GROUPING_DECL = new Map((K.SEED.groupings || []).map(g => [g.key, g]));
const GROUPINGS = {
  kind: n => n.kind,
  attribute: (n, g, o) => { const a = K.attributes(n.uid, o) || {}; return a[g.key] == null ? null : a[g.key]; },
  ancestor: (n, g, o) => {
    const nearest = (uids, seen) => {
      for (const u of uids) { const r = nodeRow(u); if (r && K.isA(r.kind, g.kind, r.namespace, r.scope)) return u; }
      const up = [...new Set(uids.flatMap(u => K.parents(g.hierarchy, u, o)))].filter(u => !seen.has(u));
      up.forEach(u => seen.add(u));
      return up.length ? nearest(up, seen) : null;
    };
    return nearest(K.parents(g.hierarchy, n.uid, o), new Set());
  }
};
/* the view's nodes grouped by its declared groupings, in order: [{ keys: [...], nodes: [...] }] */
function viewGroups(name, o) {
  o = o || {};
  const V = viewOf(name, o.namespace, o.scope);
  if (!V) fail("Unknown view: " + name);
  const groups = new Map();
  for (const n of viewNodes(name, o)) {
    const keys = (V.groupBy || []).map(g => GROUPINGS[g.by](n, g, { at: o.at, recorded: o.recorded, lang: o.lang, namespace: o.namespace }));
    const id = JSON.stringify(keys);
    if (!groups.has(id)) groups.set(id, { keys, nodes: [] });
    groups.get(id).nodes.push(n);
  }
  return [...groups.values()];
}
/* the view's nodes now (or at a time): computed from the master, never stored */
function viewNodes(name, o) {
  o = o || {};
  const V = viewOf(name, o.namespace, o.scope);
  if (!V) fail("Unknown view: " + name);
  const out = new Map();
  for (const s of V.selects) {
    const opt = { at: o.at, recorded: o.recorded, depth: s.depth == null ? undefined : s.depth, namespace: o.namespace, scope: o.scope };
    const found = s.root == null
      ? K.children(s.hierarchy, null, opt).flatMap(top => [top, ...(s.depth === 0 ? [] : K.descendants(s.hierarchy, top, { ...opt, depth: s.depth == null ? undefined : s.depth - 1 }))])
      : [...(s.includeRoot ? K.internal.listed([s.root], opt) : []), ...K.descendants(s.hierarchy, s.root, opt)];
    for (const uid of found) {
      if (out.has(uid)) continue;
      const row = nodeRow(uid), kind = row.kind;
      /* a selected kind takes every kind that extends it */
      if (s.kinds.length && !s.kinds.some(k => K.isA(kind, k, row.namespace, row.scope))) continue;
      out.set(uid, { uid, kind, hierarchy: s.hierarchy, label: V.labels[uid] || null });
    }
  }
  return [...out.values()];
}

module.exports = { ensureTables, declareSetting, settingOf, assign, assignedAt, scopesWith, defineResolution, resolve, defineView, viewOf, viewNodes, viewGroups };
