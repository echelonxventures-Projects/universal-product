/* LUXORA Platform — the kernel (FOUNDATIONS K01–K12), first slice: kinds, nodes, identifiers,
   hierarchies, typed attributes, bi-temporal versions and the event log.

   Every domain builds on these parts instead of its own tables: a place, a currency, a language,
   a store or a person is a NODE of a declared KIND; where it sits is a PLACEMENT in a named
   HIERARCHY; its codes are IDENTIFIERS in declared schemes; its facts are ATTRIBUTE versions
   with valid time and recorded time; and every change is one EVENT in one hash-chained log.
   No domain vocabulary appears here — a kind, a scheme or a hierarchy is data a person or an
   agent declares, with no limit on count or depth.

   Recorded time is the event sequence: each write appends its event first and stamps its rows
   with that sequence number, so "what did we believe at T" is "rows recorded at or before the
   last event at T and not yet superseded then". Nothing is overwritten; superseding closes a
   row's recorded interval and writes the replacement.

   The parts have different owners (lib/../_registry/codebase.json): kinds and attributes are
   Registry's, nodes and identifiers Identity's, hierarchies Relationship's, versions
   Evolution's and the event log Runtime's. */
"use strict";

const crypto = require("crypto");
const { exec, run, get, all } = require("./db.js");
const sec = require("./security.js");
const SEED = require("./seed/kernel.json");
const DOMAINS = new Set(require("../_registry/domains.json").domains.map(d => d.name));

const EV = SEED.events;
const KEY_RE = new RegExp(SEED.limits.keyPattern);
const J = (v, d) => { try { return v == null || v === "" ? d : JSON.parse(v); } catch (e) { return d; } };
const fail = msg => { const e = new Error(msg); e.status = 400; throw e; };

/* ============================== storage ============================== */
let ready = false;
function ensureTables() {
  if (ready) return;
  /* Runtime: the event log. seq is recorded time for every other table. */
  run(`CREATE TABLE IF NOT EXISTS k_events (
    seq INTEGER PRIMARY KEY AUTOINCREMENT, at TEXT NOT NULL, type TEXT NOT NULL,
    namespace TEXT NOT NULL, subject TEXT, actor TEXT, payload TEXT NOT NULL DEFAULT '{}',
    prev_hash TEXT NOT NULL, hash TEXT NOT NULL)`);
  run(`CREATE INDEX IF NOT EXISTS ix_k_events_subject ON k_events(subject, seq)`);
  run(`CREATE INDEX IF NOT EXISTS ix_k_events_at ON k_events(at)`);
  /* Registry: kinds (one row per recorded declaration; the open row is current) */
  run(`CREATE TABLE IF NOT EXISTS k_kinds (
    id INTEGER PRIMARY KEY AUTOINCREMENT, namespace TEXT NOT NULL, kind TEXT NOT NULL,
    owner TEXT NOT NULL, spec TEXT NOT NULL, rec_from INTEGER NOT NULL, rec_to INTEGER)`);
  run(`CREATE INDEX IF NOT EXISTS ix_k_kinds ON k_kinds(namespace, kind, rec_to)`);
  /* Identity: nodes and identifiers */
  run(`CREATE TABLE IF NOT EXISTS k_nodes (
    uid TEXT PRIMARY KEY, namespace TEXT NOT NULL, kind TEXT NOT NULL, rec_from INTEGER NOT NULL)`);
  run(`CREATE INDEX IF NOT EXISTS ix_k_nodes_kind ON k_nodes(namespace, kind)`);
  run(`CREATE TABLE IF NOT EXISTS k_identifiers (
    id INTEGER PRIMARY KEY AUTOINCREMENT, node TEXT NOT NULL, scheme TEXT NOT NULL, value TEXT NOT NULL,
    valid_from TEXT NOT NULL, valid_to TEXT, rec_from INTEGER NOT NULL, rec_to INTEGER)`);
  run(`CREATE INDEX IF NOT EXISTS ix_k_ident_value ON k_identifiers(scheme, value, rec_to)`);
  run(`CREATE INDEX IF NOT EXISTS ix_k_ident_node ON k_identifiers(node, rec_to)`);
  /* Relationship: hierarchies and placements */
  run(`CREATE TABLE IF NOT EXISTS k_hierarchies (
    id INTEGER PRIMARY KEY AUTOINCREMENT, namespace TEXT NOT NULL, hierarchy TEXT NOT NULL,
    owner TEXT NOT NULL, spec TEXT NOT NULL, rec_from INTEGER NOT NULL, rec_to INTEGER)`);
  run(`CREATE INDEX IF NOT EXISTS ix_k_hier ON k_hierarchies(namespace, hierarchy, rec_to)`);
  run(`CREATE TABLE IF NOT EXISTS k_placements (
    id INTEGER PRIMARY KEY AUTOINCREMENT, hierarchy TEXT NOT NULL, node TEXT NOT NULL, parent TEXT,
    valid_from TEXT NOT NULL, valid_to TEXT, rec_from INTEGER NOT NULL, rec_to INTEGER)`);
  run(`CREATE INDEX IF NOT EXISTS ix_k_place_parent ON k_placements(hierarchy, parent, rec_to)`);
  run(`CREATE INDEX IF NOT EXISTS ix_k_place_node ON k_placements(hierarchy, node, rec_to)`);
  /* Evolution: attribute versions, bi-temporal */
  run(`CREATE TABLE IF NOT EXISTS k_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, node TEXT NOT NULL, attrs TEXT NOT NULL,
    valid_from TEXT NOT NULL, valid_to TEXT, rec_from INTEGER NOT NULL, rec_to INTEGER)`);
  run(`CREATE INDEX IF NOT EXISTS ix_k_versions ON k_versions(node, rec_to, valid_from)`);
  ready = true;
}

/* one write = one transaction; nested calls join the outer one */
let depth = 0;
function tx(fn) {
  ensureTables();
  if (depth) { depth++; try { return fn(); } finally { depth--; } }
  exec("BEGIN"); depth = 1;
  try { const out = fn(); exec("COMMIT"); return out; }
  catch (e) { try { exec("ROLLBACK"); } catch (_) { } throw e; }
  finally { depth = 0; }
}

/* ============================== time ============================== */
/* valid time is an ISO-8601 instant; null valid_to is "until further notice" */
function instant(t, label) {
  if (t == null || t === "") return null;
  const d = t instanceof Date ? t : new Date(t);
  if (isNaN(d.getTime())) fail(label + " is not a valid instant: " + t);
  return d.toISOString();
}
const nowIso = () => new Date().toISOString();
const before = (a, b) => b == null ? a != null : a != null && a < b;     /* a < b, null = +∞ */
const minEnd = (a, b) => a == null ? b : b == null ? a : (a < b ? a : b);
const maxStart = (a, b) => a > b ? a : b;
function window(o) {
  const from = instant(o && o.validFrom, "validFrom") || nowIso();
  const to = instant(o && o.validTo, "validTo");
  if (to != null && !before(from, to)) fail("validTo must be after validFrom");
  return { from, to };
}
/* recorded time: a sequence number, or the last event at or before an instant */
function recordedSeq(r) {
  if (r == null) return null;
  if (typeof r === "number") return r;
  const row = get("SELECT MAX(seq) AS s FROM k_events WHERE at<=?", instant(r, "recorded"));
  return row && row.s != null ? row.s : 0;
}
/* the SQL that selects rows believed at recorded seq s (current belief when s is null) */
const believed = s => s == null ? { sql: "rec_to IS NULL", args: [] } : { sql: "rec_from<=? AND (rec_to IS NULL OR rec_to>?)", args: [s, s] };
const validAt = at => ({ sql: "valid_from<=? AND (valid_to IS NULL OR valid_to>?)", args: [at, at] });

/* ============================== K08 events (Runtime) ============================== */
const canon = v => JSON.stringify(v, (k, x) => x && typeof x === "object" && !Array.isArray(x) ? Object.keys(x).sort().reduce((o, key) => (o[key] = x[key], o), {}) : x);
function append(type, o) {
  ensureTables();
  const at = nowIso();
  const ns = (o && o.namespace) || SEED.defaultNamespace;
  const payload = canon((o && o.payload) || {});
  const prev = get("SELECT hash FROM k_events ORDER BY seq DESC LIMIT 1");
  const prevHash = prev ? prev.hash : "";
  const hash = crypto.createHash("sha256").update([prevHash, at, type, ns, (o && o.subject) || "", (o && o.actor) || "", payload].join("\n")).digest("hex");
  const r = run("INSERT INTO k_events(at,type,namespace,subject,actor,payload,prev_hash,hash) VALUES(?,?,?,?,?,?,?,?)",
    at, String(type), ns, (o && o.subject) || null, (o && o.actor) || null, payload, prevHash, hash);
  return Number(r.lastInsertRowid);
}
function events(q) {
  ensureTables();
  q = q || {};
  const where = [], args = [];
  if (q.since != null) { where.push("seq>?"); args.push(Number(q.since)); }
  if (q.subject) { where.push("subject=?"); args.push(String(q.subject)); }
  if (q.type) { where.push("type=?"); args.push(String(q.type)); }
  if (q.namespace) { where.push("namespace=?"); args.push(String(q.namespace)); }
  const limit = Math.min(Number(q.limit) || SEED.limits.eventPage, SEED.limits.eventPage);
  return all(`SELECT * FROM k_events ${where.length ? "WHERE " + where.join(" AND ") : ""} ORDER BY seq LIMIT ${limit}`, ...args)
    .map(e => ({ ...e, payload: J(e.payload, {}) }));
}
/* the chain proves no event was edited, removed or reordered */
function verifyEvents() {
  ensureTables();
  let prevHash = "", count = 0;
  for (const e of all("SELECT * FROM k_events ORDER BY seq")) {
    const hash = crypto.createHash("sha256").update([prevHash, e.at, e.type, e.namespace, e.subject || "", e.actor || "", e.payload].join("\n")).digest("hex");
    if (e.prev_hash !== prevHash || e.hash !== hash) return { ok: false, count, brokenAt: e.seq };
    prevHash = e.hash; count++;
  }
  return { ok: true, count };
}

/* ============================== K01 kinds + K06 attributes (Registry) ============================== */
const VALUE_TYPES = new Set(SEED.valueTypes.map(t => t.key));
const NAMESPACES = new Set(SEED.namespaces);
/* each declared value type's check — the declarations live in lib/seed/kernel.json */
const TYPE_CHECKS = {
  text: v => typeof v === "string",
  number: v => typeof v === "number" && isFinite(v),
  integer: v => Number.isInteger(v),
  boolean: v => typeof v === "boolean",
  instant: v => typeof v === "string" && !isNaN(new Date(v).getTime()),
  node: v => typeof v === "string" && !!get("SELECT 1 AS x FROM k_nodes WHERE uid=?", v),
  list: v => Array.isArray(v),
  record: v => !!v && typeof v === "object" && !Array.isArray(v)
};
const ns = n => { const v = n || SEED.defaultNamespace; if (!NAMESPACES.has(v)) fail("Unknown namespace: " + v); return v; };
const keyOk = (k, label) => { if (typeof k !== "string" || !KEY_RE.test(k)) fail(label + " must match " + SEED.limits.keyPattern + ": " + k); return k; };

function normaliseKind(d) {
  const attributes = (d.attributes || []).map(a => {
    keyOk(a.key, "Attribute key");
    if (!VALUE_TYPES.has(a.type)) fail("Unknown value type for " + a.key + ": " + a.type);
    return { key: a.key, type: a.type, required: !!a.required, sensitive: !!a.sensitive, label: a.label || a.key };
  });
  const seen = new Set();
  for (const a of attributes) { if (seen.has(a.key)) fail("Attribute declared twice: " + a.key); seen.add(a.key); }
  const parents = (d.parents || []).map(p => p === "*" ? p : keyOk(p, "Parent kind"));
  const schemes = (d.schemes || []).map(s => keyOk(s, "Identifier scheme"));
  return { label: d.label || d.kind, attributes, parents, root: d.root !== false, schemes, shape: !!d.shape };
}
function defineKind(d, actor) {
  d = d || {};
  const namespace = ns(d.namespace), kind = keyOk(d.kind, "Kind");
  if (!DOMAINS.has(d.owner)) fail("A kind needs an owning domain from the register: " + d.owner);
  const spec = normaliseKind(d);
  return tx(() => {
    const seq = append(EV.kindDefined, { namespace, subject: kind, actor, payload: { owner: d.owner, spec } });
    run("UPDATE k_kinds SET rec_to=? WHERE namespace=? AND kind=? AND rec_to IS NULL", seq, namespace, kind);
    run("INSERT INTO k_kinds(namespace,kind,owner,spec,rec_from) VALUES(?,?,?,?,?)", namespace, kind, d.owner, JSON.stringify(spec), seq);
    return kindOf(kind, namespace);
  });
}
function kindOf(kind, namespace, recorded) {
  ensureTables();
  const b = believed(recordedSeq(recorded));
  const r = get(`SELECT * FROM k_kinds WHERE namespace=? AND kind=? AND ${b.sql}`, ns(namespace), kind, ...b.args);
  return r ? { namespace: r.namespace, kind: r.kind, owner: r.owner, ...J(r.spec, {}) } : null;
}
function kinds(namespace) {
  ensureTables();
  return all("SELECT * FROM k_kinds WHERE namespace=? AND rec_to IS NULL ORDER BY kind", ns(namespace))
    .map(r => ({ namespace: r.namespace, kind: r.kind, owner: r.owner, ...J(r.spec, {}) }));
}
const ctx = (uid, key) => "kernel:" + uid + ":" + key;
/* validates a patch against the kind; sensitive values are sealed with the node and key as AAD */
function checkAttrs(k, uid, patch, whole) {
  const decl = new Map(k.attributes.map(a => [a.key, a]));
  const out = {};
  for (const [key, v] of Object.entries(patch || {})) {
    const a = decl.get(key);
    if (!a) fail(`Kind ${k.kind} declares no attribute ${key}`);
    if (v === null) { out[key] = null; continue; }
    if (!TYPE_CHECKS[a.type](v)) fail(`${key} must be ${a.type}`);
    out[key] = a.sensitive ? sec.encryptSecret(JSON.stringify(v), ctx(uid, key)) : v;
  }
  if (whole) for (const a of k.attributes) if (a.required && (whole[a.key] == null)) fail(`${a.key} is required for kind ${k.kind}`);
  return out;
}
function openAttrs(k, uid, attrs) {
  const sensitive = new Set(k.attributes.filter(a => a.sensitive).map(a => a.key));
  const out = {};
  for (const [key, v] of Object.entries(attrs)) {
    if (v === null) continue;
    out[key] = sensitive.has(key) ? J(sec.safeDecrypt(v, ctx(uid, key)), null) : v;
  }
  return out;
}

/* ============================== K02 nodes + K04 identifiers (Identity) ============================== */
function nodeRow(uid) { ensureTables(); return get("SELECT * FROM k_nodes WHERE uid=?", String(uid)); }
function kindForNode(uid) {
  const n = nodeRow(uid); if (!n) fail("Unknown node: " + uid);
  const k = kindOf(n.kind, n.namespace); if (!k) fail("Node " + uid + " has no declared kind " + n.kind);
  return { n, k };
}
function createNode(kind, o, actor) {
  o = o || {};
  const namespace = ns(o.namespace);
  const k = kindOf(kind, namespace);
  if (!k) fail("Unknown kind: " + kind);
  const uid = crypto.randomUUID();
  const w = window(o);
  return tx(() => {
    const seq = append(EV.nodeCreated, { namespace, subject: uid, actor, payload: { kind } });
    run("INSERT INTO k_nodes(uid,namespace,kind,rec_from) VALUES(?,?,?,?)", uid, namespace, kind, seq);
    record(uid, o.attributes || {}, { validFrom: w.from, validTo: w.to }, actor, true);
    for (const [scheme, value] of Object.entries(o.identifiers || {})) assignIdentifier(uid, scheme, value, { validFrom: w.from, validTo: w.to }, actor);
    return uid;
  });
}
function nodes(kind, namespace) {
  ensureTables();
  return all("SELECT uid FROM k_nodes WHERE namespace=? AND kind=? ORDER BY rec_from", ns(namespace), kind).map(r => r.uid);
}
function assignIdentifier(uid, scheme, value, o, actor) {
  const { n, k } = kindForNode(uid);
  keyOk(scheme, "Identifier scheme");
  if (!k.schemes.includes(scheme)) fail(`Kind ${k.kind} declares no identifier scheme ${scheme}`);
  value = String(value == null ? "" : value).trim();
  if (!value) fail("An identifier needs a value");
  const w = window(o);
  return tx(() => {
    /* a code names one node at a time: no other node may hold it in an overlapping window */
    const clash = all("SELECT * FROM k_identifiers WHERE scheme=? AND value=? AND rec_to IS NULL AND node<>?", scheme, value, uid)
      .find(r => before(r.valid_from, w.to) && before(w.from, r.valid_to));
    if (clash) fail(`${scheme} ${value} already names node ${clash.node} in that window`);
    const seq = append(EV.identifierAssigned, { namespace: n.namespace, subject: uid, actor, payload: { scheme, value, validFrom: w.from, validTo: w.to } });
    run("INSERT INTO k_identifiers(node,scheme,value,valid_from,valid_to,rec_from) VALUES(?,?,?,?,?,?)", uid, scheme, value, w.from, w.to, seq);
    return seq;
  });
}
/* ends an identifier at an instant: the open row is superseded by one that stops there */
function endIdentifier(uid, scheme, value, at, actor) {
  const end = instant(at, "at") || nowIso();
  return tx(() => {
    const rows = all("SELECT * FROM k_identifiers WHERE node=? AND scheme=? AND value=? AND rec_to IS NULL", uid, scheme, String(value))
      .filter(r => before(r.valid_from, end) && before(end, r.valid_to));
    if (!rows.length) fail("No identifier to end at " + end);
    const seq = append(EV.identifierEnded, { namespace: nodeRow(uid).namespace, subject: uid, actor, payload: { scheme, value, at: end } });
    for (const r of rows) {
      run("UPDATE k_identifiers SET rec_to=? WHERE id=?", seq, r.id);
      run("INSERT INTO k_identifiers(node,scheme,value,valid_from,valid_to,rec_from) VALUES(?,?,?,?,?,?)", uid, scheme, r.value, r.valid_from, end, seq);
    }
    return seq;
  });
}
function identifiers(uid, o) {
  ensureTables();
  o = o || {};
  const b = believed(recordedSeq(o.recorded)), v = validAt(instant(o.at, "at") || nowIso());
  const out = { [SEED.identity.scheme]: uid };
  for (const r of all(`SELECT scheme, value FROM k_identifiers WHERE node=? AND ${b.sql} AND ${v.sql} ORDER BY id`, uid, ...b.args, ...v.args)) out[r.scheme] = r.value;
  return out;
}
function resolveIdentifier(scheme, value, o) {
  ensureTables();
  o = o || {};
  if (scheme === SEED.identity.scheme) return nodeRow(value) ? value : null;
  const b = believed(recordedSeq(o.recorded)), v = validAt(instant(o.at, "at") || nowIso());
  const r = get(`SELECT node FROM k_identifiers WHERE scheme=? AND value=? AND ${b.sql} AND ${v.sql}`, scheme, String(value), ...b.args, ...v.args);
  return r ? r.node : null;
}

/* ============================== K07 versions (Evolution) ============================== */
/* records a patch over [validFrom, validTo): every believed version that overlaps is
   superseded, and replaced by its untouched edges plus the merged middle; any part of the
   window no version covered gets the patch alone */
function record(uid, patch, o, actor, creating) {
  const { n, k } = kindForNode(uid);
  const w = window(o);
  const clean = checkAttrs(k, uid, patch, null);
  return tx(() => {
    const seq = append(EV.attributesRecorded, { namespace: n.namespace, subject: uid, actor, payload: { keys: Object.keys(clean).sort(), validFrom: w.from, validTo: w.to } });
    const hits = all("SELECT * FROM k_versions WHERE node=? AND rec_to IS NULL ORDER BY valid_from", uid)
      .filter(r => before(r.valid_from, w.to) && before(w.from, r.valid_to));
    const writes = [];
    let cursor = w.from;
    for (const r of hits) {
      const a = J(r.attrs, {});
      run("UPDATE k_versions SET rec_to=? WHERE id=?", seq, r.id);
      if (r.valid_from < w.from) writes.push([a, r.valid_from, w.from]);
      const s = maxStart(r.valid_from, w.from), e = minEnd(r.valid_to, w.to);
      if (cursor < s) writes.push([clean, cursor, s]);
      writes.push([{ ...a, ...clean }, s, e]);
      if (before(w.to, r.valid_to)) writes.push([a, w.to, r.valid_to]);
      cursor = e;
    }
    if (cursor != null && before(cursor, w.to)) writes.push([clean, cursor, w.to]);
    for (const [a, from, to] of writes) {
      /* required attributes hold in every stretch of valid time the node has */
      checkAttrs(k, uid, {}, Object.fromEntries(Object.entries(a).filter(([, v]) => v !== null)));
      run("INSERT INTO k_versions(node,attrs,valid_from,valid_to,rec_from) VALUES(?,?,?,?,?)", uid, JSON.stringify(a), from, to, seq);
    }
    return seq;
  });
}
function attributes(uid, o) {
  o = o || {};
  const { k } = kindForNode(uid);
  const b = believed(recordedSeq(o.recorded)), v = validAt(instant(o.at, "at") || nowIso());
  const r = get(`SELECT attrs FROM k_versions WHERE node=? AND ${b.sql} AND ${v.sql}`, uid, ...b.args, ...v.args);
  return r ? openAttrs(k, uid, J(r.attrs, {})) : null;
}
/* the full record of belief: every version ever written, superseded or not */
function history(uid) {
  const { k } = kindForNode(uid);
  return all("SELECT * FROM k_versions WHERE node=? ORDER BY rec_from, valid_from", uid)
    .map(r => ({ validFrom: r.valid_from, validTo: r.valid_to, recordedFrom: r.rec_from, recordedTo: r.rec_to, attributes: openAttrs(k, uid, J(r.attrs, {})) }));
}

/* ============================== K03 hierarchies (Relationship) ============================== */
function defineHierarchy(d, actor) {
  d = d || {};
  const namespace = ns(d.namespace), hierarchy = keyOk(d.hierarchy, "Hierarchy");
  if (!DOMAINS.has(d.owner)) fail("A hierarchy needs an owning domain from the register: " + d.owner);
  const spec = { label: d.label || hierarchy };
  return tx(() => {
    const seq = append(EV.hierarchyDefined, { namespace, subject: hierarchy, actor, payload: { owner: d.owner, spec } });
    run("UPDATE k_hierarchies SET rec_to=? WHERE namespace=? AND hierarchy=? AND rec_to IS NULL", seq, namespace, hierarchy);
    run("INSERT INTO k_hierarchies(namespace,hierarchy,owner,spec,rec_from) VALUES(?,?,?,?,?)", namespace, hierarchy, d.owner, JSON.stringify(spec), seq);
    return hierarchyOf(hierarchy, namespace);
  });
}
function hierarchyOf(hierarchy, namespace) {
  ensureTables();
  const r = get("SELECT * FROM k_hierarchies WHERE namespace=? AND hierarchy=? AND rec_to IS NULL", ns(namespace), hierarchy);
  return r ? { namespace: r.namespace, hierarchy: r.hierarchy, owner: r.owner, ...J(r.spec, {}) } : null;
}
/* hierarchies are addressed as "<namespace>/<key>" in placements, so one key may exist per namespace */
const hid = (h, namespace) => ns(namespace) + "/" + h;
/* edges valid at one instant (o.at), or — with o.during — at any time in a window */
function edges(h, col, val, o) {
  const b = believed(recordedSeq(o && o.recorded));
  const rows = (v) => all(`SELECT * FROM k_placements WHERE hierarchy=? AND ${col} ${val == null ? "IS NULL" : "=?"} AND ${b.sql}${v ? " AND " + v.sql : ""} ORDER BY id`,
    h, ...(val == null ? [] : [val]), ...b.args, ...(v ? v.args : []));
  if (o && o.during) return rows(null).filter(r => before(r.valid_from, o.during.to) && before(o.during.from, r.valid_to));
  return rows(validAt(instant(o && o.at, "at") || nowIso()));
}
function ancestorSet(h, uid, o) {
  const seen = new Set(), stack = [uid];
  while (stack.length) {
    const u = stack.pop();
    for (const e of edges(h, "node", u, o)) if (e.parent && !seen.has(e.parent)) {
      seen.add(e.parent); stack.push(e.parent);
      if (seen.size > SEED.limits.maxDepth) fail("Hierarchy deeper than " + SEED.limits.maxDepth);
    }
  }
  return seen;
}
function place(hierarchy, uid, parent, o, actor) {
  o = o || {};
  const H = hierarchyOf(hierarchy, o.namespace);
  if (!H) fail("Unknown hierarchy: " + hierarchy);
  const h = hid(hierarchy, o.namespace);
  const { k } = kindForNode(uid);
  const w = window(o);
  if (parent == null) { if (!k.root) fail(`Kind ${k.kind} may not sit at the top of a hierarchy`); }
  else {
    const pk = kindForNode(parent).k;
    if (!k.parents.includes("*") && !k.parents.includes(pk.kind)) fail(`Kind ${k.kind} may not sit under kind ${pk.kind}`);
    /* a cycle at any moment of the window is a cycle */
    if (parent === uid || ancestorSet(h, parent, { during: w }).has(uid)) fail("That placement would make a cycle");
  }
  return tx(() => {
    const dup = all(`SELECT * FROM k_placements WHERE hierarchy=? AND node=? AND parent ${parent == null ? "IS NULL" : "=?"} AND rec_to IS NULL`, h, uid, ...(parent == null ? [] : [parent]))
      .find(r => before(r.valid_from, w.to) && before(w.from, r.valid_to));
    if (dup) fail("The node already sits there in that window");
    const seq = append(EV.nodePlaced, { namespace: H.namespace, subject: uid, actor, payload: { hierarchy: h, parent: parent || null, validFrom: w.from, validTo: w.to } });
    const r = run("INSERT INTO k_placements(hierarchy,node,parent,valid_from,valid_to,rec_from) VALUES(?,?,?,?,?,?)", h, uid, parent || null, w.from, w.to, seq);
    return Number(r.lastInsertRowid);
  });
}
function endPlacement(hierarchy, uid, parent, at, o, actor) {
  o = o || {};
  const h = hid(hierarchy, o.namespace);
  const end = instant(at, "at") || nowIso();
  return tx(() => {
    const rows = all(`SELECT * FROM k_placements WHERE hierarchy=? AND node=? AND parent ${parent == null ? "IS NULL" : "=?"} AND rec_to IS NULL`, h, uid, ...(parent == null ? [] : [parent]))
      .filter(r => before(r.valid_from, end) && before(end, r.valid_to));
    if (!rows.length) fail("No placement to end at " + end);
    const seq = append(EV.placementEnded, { namespace: ns(o.namespace), subject: uid, actor, payload: { hierarchy: h, parent: parent || null, at: end } });
    for (const r of rows) {
      run("UPDATE k_placements SET rec_to=? WHERE id=?", seq, r.id);
      run("INSERT INTO k_placements(hierarchy,node,parent,valid_from,valid_to,rec_from) VALUES(?,?,?,?,?,?)", h, uid, r.parent, r.valid_from, end, seq);
    }
    return seq;
  });
}
const children = (hierarchy, uid, o) => { ensureTables(); return [...new Set(edges(hid(hierarchy, o && o.namespace), "parent", uid == null ? null : uid, o).map(e => e.node))]; };
const parents = (hierarchy, uid, o) => { ensureTables(); return [...new Set(edges(hid(hierarchy, o && o.namespace), "node", uid, o).map(e => e.parent).filter(Boolean))]; };
const ancestors = (hierarchy, uid, o) => { ensureTables(); return [...ancestorSet(hid(hierarchy, o && o.namespace), uid, o)]; };
/* every path from a top node down to this one: a node in many places has many paths */
function paths(hierarchy, uid, o) {
  ensureTables();
  const h = hid(hierarchy, o && o.namespace);
  const up = (u, seen) => {
    if (seen.size > SEED.limits.maxDepth) fail("Hierarchy deeper than " + SEED.limits.maxDepth);
    const es = edges(h, "node", u, o);
    if (!es.length) return [];
    return es.flatMap(e => e.parent == null ? [[u]] : seen.has(e.parent) ? [] : up(e.parent, new Set([...seen, u])).map(p => [...p, u]));
  };
  return up(uid, new Set());
}
function descendants(hierarchy, uid, o) {
  ensureTables();
  const h = hid(hierarchy, o && o.namespace);
  const max = o && o.depth != null ? Number(o.depth) : SEED.limits.maxDepth;
  const seen = new Set(); let level = [uid], d = 0;
  while (level.length && d < max) {
    const next = [];
    for (const u of level) for (const e of edges(h, "parent", u, o)) if (!seen.has(e.node)) { seen.add(e.node); next.push(e.node); }
    level = next; d++;
  }
  return [...seen];
}

module.exports = {
  ensureTables, SEED,
  /* K08 */ append, events, verifyEvents,
  /* K01 + K06 */ defineKind, kindOf, kinds,
  /* K02 + K04 */ createNode, nodes, assignIdentifier, endIdentifier, identifiers, resolveIdentifier,
  /* K07 */ record, attributes, history,
  /* K03 */ defineHierarchy, hierarchyOf, place, endPlacement, children, parents, ancestors, paths, descendants
};
