/* LUXORA Platform — the platform master as one surface (owner Perspective): for anything on the
   kernel, its five parts together.

     Registry      the kind that declares it, its owner and its identifiers
     Entity        its facts
     Context       the settings assigned at it, and whose they are
     Temporal      every version of it, as valid and as recorded, and its events
     Relationship  where it sits in every hierarchy, and what sits under it

   It reads any kind. It writes only RECORDS — kinds extending the record kind (lib/seed/screens.json)
   — because every other kind has an owner whose own write path it must go through. A new kind of
   record is a row declared here, so a register a platform needs takes no code; which of them a
   platform keeps is an answer to its setup (lib/platform-setup.js), and its records are its own,
   in its namespace. */
"use strict";

const K = require("./kernel.js");
const C = require("./kernel-context.js");
const LC = require("./kernel-lifecycle.js");
const M = require("./platform-master.js");
const SEED = require("./seed/screens.json");
const NS = SEED.namespace;
const fail = (msg, status) => { const e = new Error(msg); e.status = status || 400; throw e; };
const lang = () => require("./expression.js").SEED.sourceLanguage;
const shown = v => (v && typeof v === "object" && !Array.isArray(v) ? K.text(v, lang()) : v);

let ready = false;
function ensure() {
  M.ensure();
  if (ready) return;
  LC.ensureTables(); C.ensureTables();
  K.internal.tx(() => {
    for (const k of SEED.kinds) if (!K.kindOf(k.kind, NS)) K.defineKind({ ...k, namespace: NS }, SEED.actor);
    for (const h of SEED.hierarchies) if (!K.hierarchyOf(h.hierarchy, NS)) K.defineHierarchy({ ...h, namespace: NS }, SEED.actor);
  });
  ready = true;
}
const isRecord = kind => K.isA(kind, SEED.recordKind, NS);
/* a secret never leaves the kernel through a listing */
function open(uid, kind, o) {
  const a = K.attributes(uid, o) || {}, hidden = new Set(kind.attributes.filter(x => x.sensitive).map(x => x.key));
  return Object.fromEntries(Object.entries(a).map(([k, v]) => [k, hidden.has(k) ? "••••" : v]));
}
const title = (uid, kind, o) => { const a = open(uid, kind, o); return String(shown(a.title) || a.name || a.key || Object.values(K.identifiers(uid))[0] || uid); };
const label = uid => { const { k } = K.internal.kindForNode(uid); return { uid, kind: k.kind, title: title(uid, k) }; };

/* ---------- registry ---------- */
function kinds() {
  ensure();
  const n = new Map(K.countByKind().map(r => [r.kind, r.n]));
  return K.kinds(NS).map(k => ({ kind: k.kind, label: k.label, owner: k.owner, extends: k.extends, entities: n.get(k.kind) || 0, attributes: k.attributes, schemes: k.schemes, record: k.lineage.includes(SEED.recordKind) && k.kind !== SEED.recordKind }));
}
/* declares a kind of record: what it is called, who owns it and the facts it holds */
function declareKind(d, actor) {
  ensure();
  const kind = String((d && d.kind) || ""), base = (d && d.extends) || SEED.recordKind;
  if (!isRecord(base)) fail("A kind of record extends a kind of record");
  if (K.kindOf(kind, NS) && !isRecord(kind)) fail(`“${kind}” is declared by its owner`);
  return K.defineKind({ kind, owner: d.owner, label: d.label, extends: base, attributes: d.attributes || [], namespace: NS }, actor);
}
const REGISTRIES = {
  kinds: () => kinds().map(k => ({ key: k.kind, label: k.label, owner: k.owner, detail: k.entities + " entities" })),
  hierarchies: () => K.hierarchies(NS).map(h => ({ key: h.hierarchy, label: h.label, owner: h.owner, detail: h.placements + " placements" })),
  settings: () => C.settings(NS).map(s => ({ key: s.name, label: s.label, owner: s.owner, detail: s.type + " · " + s.assigned + " assigned" })),
  events: () => K.latestEvents(SEED.page).map(e => ({ key: e.seq, label: e.type, owner: e.actor, detail: e.at + (e.subject ? " · " + e.subject : "") })),
  changes: () => LC.changes().map(c => ({ key: c.id, label: c.title || c.label || "Change " + c.id, owner: c.actor || c.created_by, detail: c.state })),
  machines: () => Object.entries(require("./states.js").catalog()).map(([k, m]) => ({ key: k, label: k, owner: "Runtime", detail: Object.keys(m.states).join(" → ") }))
};
function registry(name) { ensure(); return (REGISTRIES[name] || fail("Unknown registry: " + name, 404))(); }
function overview() {
  ensure();
  return { kinds: K.kinds(NS).length, entities: K.countByKind().reduce((t, r) => t + r.n, 0), relationships: K.hierarchies(NS).reduce((t, h) => t + h.placements, 0), hierarchies: K.hierarchies(NS).length, settings: C.settings(NS).length, context: C.settings(NS).reduce((t, s) => t + s.assigned, 0), events: K.verifyEvents() };
}

/* ---------- entities ---------- */
function list(kind, o) {
  ensure();
  o = o || {};
  const k = K.kindOf(kind, NS) || fail("Unknown kind: " + kind, 404);
  const under = o.under ? M.uidOf(o.under) || fail("Unknown place in the master: " + o.under, 404) : null;
  const space = o.namespace || NS;
  let uids = under ? K.children(o.hierarchy, under, { namespace: NS, includeHidden: !!o.hidden }).filter(u => K.isA(K.internal.nodeRow(u).kind, kind, NS)).filter(u => K.internal.nodeRow(u).namespace === space)
    : K.nodes(kind, space, { withSubkinds: true, includeHidden: !!o.hidden });
  const rows = uids.map(u => ({ uid: u, title: title(u, k, { at: o.at }), kind: K.internal.nodeRow(u).kind, identifiers: K.identifiers(u), attributes: open(u, K.internal.kindForNode(u).k, { at: o.at }), listed: LC.nodeState(u) === K.SEED.lifecycle.nodeStates.initial }));
  const q = String(o.q || "").toLowerCase(), hit = q ? rows.filter(r => JSON.stringify([r.title, r.identifiers, r.attributes]).toLowerCase().includes(q)) : rows;
  return { kind: k.kind, label: k.label, owner: k.owner, attributes: k.attributes, editable: isRecord(k.kind), total: hit.length, rows: hit.slice(0, SEED.page) };
}
function entity(uid, o) {
  ensure();
  o = o || {};
  if (!K.internal.nodeRow(uid)) fail("Nothing in the master has that identity", 404);
  const { n, k } = K.internal.kindForNode(uid), hidden = new Set(k.attributes.filter(x => x.sensitive).map(x => x.key));
  const veil = a => Object.fromEntries(Object.entries(a || {}).map(([x, v]) => [x, hidden.has(x) ? "••••" : v]));
  return {
    registry: { kind: k.kind, label: k.label, owner: k.owner, lineage: k.lineage, namespace: n.namespace, identifiers: K.identifiers(uid), declared: k.attributes },
    entity: { uid, title: title(uid, k, o), state: LC.nodeState(uid), attributes: veil(K.attributes(uid, o)) },
    context: C.assignmentsAt(uid),
    temporal: { versions: K.history(uid).map(v => ({ ...v, attributes: veil(v.attributes) })), events: K.events({ subject: uid, limit: SEED.events }).map(e => ({ at: e.at, type: e.type, actor: e.actor })) },
    relationship: K.hierarchies(NS).map(h => {
      const at = { namespace: NS, at: o.at };
      return { hierarchy: h.hierarchy, label: h.label, above: K.parents(h.hierarchy, uid, at).map(label), below: K.children(h.hierarchy, uid, at).slice(0, SEED.page).map(label) };
    }).filter(r => r.above.length || r.below.length),
    editable: isRecord(k.kind)
  };
}

/* ---------- writing records ---------- */
const recordOf = (uid, space) => {
  const n = K.internal.nodeRow(uid);
  if (!n || (space && n.namespace !== space)) fail("Nothing here has that identity", 404);
  if (!isRecord(n.kind)) fail("This is changed on its owner's own screen");
  return n;
};
function create(kind, d, o, actor) {
  ensure();
  o = o || {};
  if (!K.kindOf(kind, NS) || !isRecord(kind) || kind === SEED.recordKind) fail(`“${kind}” is not a kind of record`);
  return K.internal.tx(() => {
    const uid = K.createNode(kind, { namespace: o.namespace || NS, attributes: (d && d.attributes) || {}, validFrom: d && d.from, validTo: d && d.to }, actor);
    if (o.hierarchy && o.under) K.place(o.hierarchy, uid, M.uidOf(o.under) || fail("Unknown place in the master: " + o.under), { namespace: NS }, actor);
    return uid;
  });
}
/* new facts, effective from an instant (now, or later); what held before stays */
function change(uid, d, o, actor) { ensure(); recordOf(uid, o && o.namespace); K.record(uid, (d && d.attributes) || {}, { validFrom: d && d.from, validTo: d && d.to }, actor); return entity(uid); }
function relate(uid, d, o, actor) {
  ensure(); recordOf(uid, o && o.namespace);
  if (!d || !K.hierarchyOf(d.hierarchy, NS)) fail("Unknown hierarchy");
  if (!SEED.hierarchies.some(h => h.hierarchy === d.hierarchy)) fail("That relationship is changed on its owner's own screen");
  const p = M.uidOf(d.parent) || fail("Nothing in the master has that identity");
  if (o && o.namespace && ![o.namespace, NS].includes(K.internal.nodeRow(p).namespace)) fail("Nothing here has that identity", 404);
  if (d.end) K.endPlacement(d.hierarchy, uid, p, null, { namespace: NS }, actor);
  else K.place(d.hierarchy, uid, p, { namespace: NS, validFrom: d.from, validTo: d.to }, actor);
  return entity(uid);
}
function setListed(uid, on, o, actor) { ensure(); recordOf(uid, o && o.namespace); on ? LC.unhide(uid, actor) : LC.hide(uid, actor); return entity(uid); }

/* ---------- which records a platform keeps ---------- */
const recordKinds = () => kinds().filter(k => k.record);
const kept = tid => { ensure(); return require("./platform-setup.js").answers(tid)[SEED.step] || []; };
function ownKind(tid, kind) { if (!kept(tid).includes(kind)) fail("This platform does not keep that", 403); return { namespace: require("./master-permissions.js").storeHolder(tid) }; }
module.exports = { ensure, kinds, declareKind, registry, overview, list, entity, create, change, relate, setListed, recordKinds, kept, ownKind, screens: () => SEED.screens };
