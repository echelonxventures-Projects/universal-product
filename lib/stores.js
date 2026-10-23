/* LUXORA Platform — stores on the kernel (P09, owners Party and Relationship).

   A store is a node of the store kind (lib/seed/stores.json), known by its store id; a store
   row's universal ID becomes its node's. The places a store serves are a relationship of their
   own: in the `serves` hierarchy the store sits under each place it serves — a country, a
   subdivision, any place at any scale, any mix — each with its own time window. Its jurisdiction
   is a Party setting at the store's node naming one of those places: it answers where the store
   is registered, and so its tax and its default currency and locale (resolved at that place).

   Every write of a store's places or jurisdiction goes through this module, the kernel first.
   A store from before the place tree is imported at boot: its jurisdiction is what its storefront
   showed (its saved commerce country), else its row's country column, else the platform's
   provisioning policy. Nothing is read from those legacy places once the store is on the kernel. */
"use strict";

/* db functions resolved at call time: a store can be written while the db module still boots */
const all = (...a) => require("./db.js").all(...a);
const get = (...a) => require("./db.js").get(...a);
const K = require("./kernel.js");
const C = require("./kernel-context.js");
const P = require("./places.js");
const SEED = require("./seed/stores.json");
const M = SEED.master;
const NS = SEED.namespace;
const H = SEED.hierarchy.hierarchy;
const JUR = SEED.jurisdiction;

const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const bad = msg => Object.assign(new Error(msg), { status: 400 });

/* declares the store kind, the serves hierarchy and the jurisdiction setting when missing or changed */
function declare() {
  K.ensureTables(); C.ensureTables();
  P.declare();
  const k = K.kindOf(SEED.kind.kind, NS);
  const want = { ...SEED.kind, namespace: NS };
  if (!k || k.owner !== want.owner || !same(k.attributes.map(a => a.key), want.attributes.map(a => a.key)) || !same(k.schemes, want.schemes) || !same(k.parents, want.parents) || k.root !== !!want.root)
    K.defineKind(want, M.actor);
  if (!K.hierarchyOf(H, NS)) K.defineHierarchy({ ...SEED.hierarchy, namespace: NS }, M.actor);
  const cur = C.settingOf(JUR.name, NS);
  if (!cur || cur.owner !== JUR.owner || cur.type !== JUR.type) C.declareSetting({ ...JUR, namespace: NS }, M.actor);
}

const nodeOf = tid => K.resolveIdentifier(M.scheme, String(tid), {});
function placeFor(code) {
  const uid = P.byCode(code);
  if (!uid) throw bad("Unknown place: " + code);
  return uid;
}

/* the store's node, created from its row when it has none */
function ensure(tid, actor) {
  const have = nodeOf(tid);
  if (have) return have;
  const row = get("SELECT id, name, uid FROM tenants WHERE id=?", Number(tid));
  if (!row) throw bad("Unknown store: " + tid);
  const adopt = row.uid && UUID.test(row.uid) && !get("SELECT 1 AS x FROM k_nodes WHERE uid=?", String(row.uid).toLowerCase()) ? row.uid : undefined;
  return K.createNode(SEED.kind.kind, { namespace: NS, uid: adopt, attributes: { name: row.name }, identifiers: { [M.scheme]: String(row.id) } }, actor || M.actor);
}

/* the store serves a place from now (or o.validFrom) on; serving it again is a no-op */
function serve(tid, code, o, actor) {
  return K.internal.tx(() => {
    declare();
    const uid = ensure(tid, actor);
    const p = placeFor(code);
    if (K.parents(H, uid, { namespace: NS }).includes(p)) return false;
    K.place(H, uid, p, { namespace: NS, validFrom: o && o.validFrom }, actor || M.actor);
    return true;
  });
}
/* the store stops serving a place; it may not stop serving its jurisdiction */
function unserve(tid, code, actor) {
  return K.internal.tx(() => {
    const uid = nodeOf(tid);
    const p = placeFor(code);
    if (!uid || !K.parents(H, uid, { namespace: NS }).includes(p)) return false;
    if (C.assignedAt(JUR.name, { namespace: NS, scope: uid }) === p) throw bad("A store cannot stop serving its jurisdiction — move its jurisdiction first");
    K.endPlacement(H, uid, p, null, { namespace: NS }, actor || M.actor);
    return true;
  });
}
/* the codes of the places the store serves now (or at o.at) */
function served(tid, o) {
  const uid = nodeOf(tid);
  if (!uid) return [];
  return K.parents(H, uid, { namespace: NS, at: o && o.at }).map(P.codeOf).filter(Boolean);
}
/* the store's jurisdiction moves to a place, which it then serves */
function setJurisdiction(tid, code, actor) {
  return K.internal.tx(() => {
    declare();
    const uid = ensure(tid, actor);
    const p = placeFor(code);
    serve(tid, code, null, actor);
    if (C.assignedAt(JUR.name, { namespace: NS, scope: uid }) !== p) C.assign(JUR.name, p, { namespace: NS, scope: uid }, actor || M.actor);
    /* the store's cached settings carry its country (settings may itself still be loading, when
       it is what booted the db) */
    const settings = require("./settings.js");
    if (typeof settings.bust === "function") settings.bust(tid);
    return p;
  });
}

/* where a store from before the place tree said it was: what its storefront showed, its row's
   column, then the platform's provisioning policy */
function legacyJurisdiction(tid) {
  let saved = null;
  try { const r = get("SELECT value FROM settings WHERE tenant_id=? AND key=?", Number(tid), M.legacySetting.key); saved = r ? (JSON.parse(r.value) || {})[M.legacySetting.field] : null; } catch (e) { saved = null; }
  if (saved && P.byCode(saved)) return String(saved).toUpperCase();
  for (const col of M.legacyColumns) if (P.hasColumn(col, M.table)) {
    const r = get(`SELECT ${col} AS v FROM tenants WHERE id=?`, Number(tid));
    if (r && r.v && P.byCode(r.v)) return String(r.v).toUpperCase();
  }
  return require("./security.js").defaultCountry();
}
/* the code of the store's jurisdiction: its assignment on the kernel; a store not yet on the
   kernel answers what it said before (until the boot import brings it over) */
function jurisdiction(tid, o) {
  const uid = nodeOf(tid);
  const p = uid ? C.assignedAt(JUR.name, { namespace: NS, scope: uid, at: o && o.at }) : undefined;
  return p ? P.codeOf(p) : legacyJurisdiction(tid);
}
/* the country the store's jurisdiction lies in */
function country(tid, o) {
  const code = jurisdiction(tid, o);
  const p = P.byCode(code);
  return (p && P.countryOf(p)) || code;
}
/* the stores that serve a place (or any place under it) now: their store ids */
function serving(code) {
  const p = P.byCode(code);
  if (!p) return [];
  const under = new Set([p, ...K.descendants(P.HIERARCHY, p, { includeHidden: true })]);
  const out = new Set();
  for (const u of under) for (const s of K.children(H, u, { namespace: NS })) { const id = K.identifiers(s)[M.scheme]; if (id) out.add(Number(id)); }
  return [...out];
}

/* brings every store the kernel has never seen onto it, in one transaction; a warm pass writes nothing */
function importStores() {
  const stats = { created: 0, jurisdictions: 0 };
  K.internal.tx(() => {
    declare();
    for (const t of all("SELECT id FROM tenants ORDER BY id")) {
      let uid = nodeOf(t.id);
      if (!uid) { uid = ensure(t.id, M.importActor); stats.created++; }
      if (C.assignedAt(JUR.name, { namespace: NS, scope: uid }) !== undefined) continue;
      const code = legacyJurisdiction(t.id);
      if (!P.byCode(code)) continue;
      setJurisdiction(t.id, code, M.importActor); stats.jurisdictions++;
    }
  });
  return stats;
}

/* a store leaves: its node is archived (its places and history kept) in the same transaction as
   the caller's removal of its rows */
function withdraw(tid, deleteRows) {
  return K.internal.tx(() => {
    const uid = nodeOf(tid);
    const LC = require("./kernel-lifecycle.js");
    if (uid && LC.nodeState(uid) !== K.SEED.lifecycle.nodeStates.archived) LC.archive(uid, M.actor);
    return deleteRows();
  });
}

module.exports = { withdraw, declare, ensure, serve, unserve, served, setJurisdiction, jurisdiction, country, serving, importStores, HIERARCHY: H, NAMESPACE: NS };
