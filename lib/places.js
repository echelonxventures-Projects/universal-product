/* LUXORA Platform — places on the kernel (P09, owner Geo).

   Every place is a node of the declared place kind in one place tree (lib/seed/places.json):
   countries at the top — nothing above them is invented — and subdivisions under their country
   or their parent subdivision, to any depth. A country's code and a subdivision's code are
   identifiers in their declared schemes, and a row's universal ID becomes its node's, so a place
   keeps one identity across the move.

   This step MIRRORS the existing master (the countries and subdivisions tables) onto the kernel:
   the tables stay the source until the writes move onto the kernel, and the mirror runs after
   every write to them and on every boot. It is idempotent: a warm pass writes nothing. A
   switched-off row is a hidden node (reversible); a row that disappears is an archived node, so
   its history stays. */
"use strict";

const { all, get } = require("./db.js");
const K = require("./kernel.js");
const LC = require("./kernel-lifecycle.js");
const SEED = require("./seed/places.json");
const M = SEED.mirror;
const NS = SEED.namespace;
const H = SEED.hierarchy.hierarchy;

const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

/* declares the place kind and the place tree when they are missing or differ from the seed */
function declare() {
  const k = K.kindOf(SEED.kind.kind, NS);
  const want = { ...SEED.kind, namespace: NS };
  if (!k || k.owner !== want.owner || !same(k.attributes.map(a => a.key), want.attributes.map(a => a.key)) || !same(k.schemes, want.schemes) || !same(k.parents, want.parents) || k.shape !== !!want.shape)
    K.defineKind(want, M.actor);
  if (!K.hierarchyOf(H, NS)) K.defineHierarchy({ ...SEED.hierarchy, namespace: NS }, M.actor);
}

function nodeFor(scheme, code) { return K.resolveIdentifier(scheme, code, {}); }
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

/* one row onto one node: create it, or record what changed — name, level, parent, shown/hidden */
function upsert(scheme, row, parent, level, stats) {
  let uid = nodeFor(scheme, row.code);
  const attrs = { name: row.name };
  if (level) attrs.level = level;
  if (!uid) {
    const adopt = row.uid && UUID.test(row.uid) && !get("SELECT 1 AS x FROM k_nodes WHERE uid=?", String(row.uid).toLowerCase()) ? row.uid : undefined;
    uid = K.createNode(SEED.kind.kind, { namespace: NS, uid: adopt, attributes: attrs, identifiers: { [scheme]: row.code } }, M.actor);
    stats.created++;
  } else {
    const cur = K.attributes(uid) || {};
    const patch = {};
    for (const [k, v] of Object.entries(attrs)) if (cur[k] !== v) patch[k] = v;
    if (!level && cur.level != null) patch.level = null;
    if (Object.keys(patch).length) { K.record(uid, patch, {}, M.actor); stats.updated++; }
  }
  const now = K.placementsOf(H, uid, { namespace: NS });
  const want = parent || null;
  if (!(now.length === 1 && now[0] === want)) {
    for (const p of now) K.endPlacement(H, uid, p, null, { namespace: NS }, M.actor);
    K.place(H, uid, want, { namespace: NS }, M.actor);
    stats.placed++;
  }
  const state = LC.nodeState(uid);
  const hidden = K.SEED.lifecycle.nodeStates.hidden, active = K.SEED.lifecycle.nodeStates.initial, archived = K.SEED.lifecycle.nodeStates.archived;
  const wantState = row.active === 0 ? hidden : active;
  if (state === archived && wantState === active) { LC.unhide(uid, M.actor); stats.restored++; }
  else if (state === archived && wantState === hidden) { LC.unhide(uid, M.actor); LC.hide(uid, M.actor); stats.restored++; }
  else if (state !== wantState) { wantState === hidden ? LC.hide(uid, M.actor) : LC.unhide(uid, M.actor); stats.states++; }
  return uid;
}

/* mirrors the countries and subdivisions tables onto the place tree, in one transaction */
function mirror() {
  K.ensureTables(); LC.ensureTables();
  const stats = { created: 0, updated: 0, placed: 0, states: 0, archived: 0, restored: 0 };
  K.internal.tx(() => {
    declare();
    const seen = new Set();
    const countryNode = new Map();
    for (const c of all("SELECT code, name, active, uid FROM countries ORDER BY position, code")) {
      const uid = upsert(M.countryScheme, c, null, M.countryLevel, stats);
      countryNode.set(c.code, uid); seen.add(uid);
    }
    const subs = all("SELECT rowid AS id, code, country_code, name, level, parent_id, active FROM subdivisions ORDER BY country_code, position, code");
    const byId = new Map(subs.map(s => [s.id, s]));
    /* parents before children, to any depth */
    const depth = s => { let d = 0, p = s; const guard = new Set(); while (p && p.parent_id && byId.has(p.parent_id) && !guard.has(p.id)) { guard.add(p.id); p = byId.get(p.parent_id); d++; } return d; };
    const subNode = new Map();
    for (const s of subs.slice().sort((a, b) => depth(a) - depth(b))) {
      const parent = s.parent_id && subNode.has(s.parent_id) ? subNode.get(s.parent_id) : countryNode.get(s.country_code);
      if (!parent) continue;
      const uid = upsert(M.subdivisionScheme, s, parent, s.level || null, stats);
      subNode.set(s.id, uid); seen.add(uid);
    }
    /* a place whose row is gone is archived, never erased */
    const archived = K.SEED.lifecycle.nodeStates.archived;
    for (const uid of K.nodes(SEED.kind.kind, NS, { includeHidden: true })) {
      if (seen.has(uid)) continue;
      const ids = K.identifiers(uid);
      if (!ids[M.countryScheme] && !ids[M.subdivisionScheme]) continue;     /* not a mirrored place */
      if (LC.nodeState(uid) !== archived) { LC.archive(uid, M.actor); stats.archived++; }
    }
  });
  return stats;
}

/* reads, for callers moving onto the kernel */
const country = code => nodeFor(M.countryScheme, String(code || "").toUpperCase());
const subdivision = code => nodeFor(M.subdivisionScheme, String(code || "").toUpperCase());

module.exports = { declare, mirror, country, subdivision, HIERARCHY: H, NAMESPACE: NS };
