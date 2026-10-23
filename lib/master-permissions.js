/* LUXORA Platform — permissions on the platform master (GLOBAL_MASTER.md §2, roadmap P28; owner
   Authority).

   The global platform decides what each platform may see and do with the master. A permission
   is a node of the master's permission kind, so it is versioned, time-bound and auditable like
   everything else, and it says:
     holder   — whose it is: a namespace ("tenant:42", "publisher:acme")
     scope    — the master nodes it covers; each covers itself and everything under it in any
                classification (an industry, a category, a universe, one item). Empty: the
                whole master
     objects  — what it covers there (items, attribute definitions, classifications, …)
     actions  — what the holder may do (view, select, sell, overlay, add, modify, retire); an
                action implies the actions its term names
     visible  — the attributes the holder sees (empty: every attribute that applies)
     review   — when the holder's changes are reviewed (before they take effect, or after)
   The objects, actions, review modes and the store access levels the console offers are
   vocabularies of the master, so a new action or level is data.

   A permission is revoked by recording that it is revoked from an instant on: what it allowed
   before stays answerable ("could this store sell it last month?"). */
"use strict";

const K = require("./kernel.js");
const M = require("./platform-master.js");
const fail = (msg, status) => { const e = new Error(msg); e.status = status || 400; throw e; };
const R = () => M.ROLES;
const NS = () => M.NAMESPACE;

/* ---------- the vocabularies ---------- */
const actions = () => M.vocabulary(R().actions);
const objects = () => M.vocabulary(R().objects);
const reviews = () => M.vocabulary(R().reviews);
const levels = () => M.vocabulary(R().accessLevels);
/* an action with every action it implies, transitively */
function closure(list) {
  const terms = new Map(actions().map(t => [t.name, t]));
  const out = new Set(), stack = [...(list || [])];
  while (stack.length) {
    const a = stack.pop();
    if (out.has(a)) continue;
    if (!terms.has(a)) fail("Unknown action: " + a);
    out.add(a);
    stack.push(...(terms.get(a).implies || []));
  }
  return out;
}
const holderOf = h => { const v = String(h || ""); K.internal.ns(v); return v; };
/* a store's holder: its namespace on the kernel */
const storeHolder = tenantId => R().storeNamespace + ":" + Number(tenantId);
const defaultOf = terms => (terms.find(t => t.default) || terms[0] || {}).name;

/* ---------- granting and revoking ---------- */
function grant(input, actor) {
  const i = input || {};
  const holder = holderOf(i.holder);
  const scope = (i.scope || []).map(r => M.uidOf(r) || fail("Not in the platform master: " + r, 404));
  const acts = [...closure(i.actions || [])];
  if (!acts.length) fail("A permission allows at least one action");
  const objs = i.objects && i.objects.length ? i.objects : [defaultOf(objects())];
  const known = new Set(objects().map(t => t.name));
  for (const o of objs) if (!known.has(o)) fail("Unknown object: " + o);
  const review = i.review || defaultOf(reviews());
  if (!reviews().some(t => t.name === review)) fail("Unknown review mode: " + review);
  return K.createNode(R().permission, { namespace: NS(), validFrom: i.validFrom,
    attributes: { holder, scope, objects: objs, actions: acts, visible: i.visible || [], review, revoked: false, ...(i.note ? { note: String(i.note) } : {}) } }, actor);
}
function revoke(uid, at, actor) {
  if (!K.internal.nodeRow(uid)) fail("Unknown permission", 404);
  return K.record(uid, { revoked: true }, { validFrom: at }, actor);
}
/* the holder's permissions in force at an instant (now by default) */
function of(holder, o) {
  const h = holderOf(holder);
  return K.nodes(R().permission, NS(), { includeHidden: false })
    .map(uid => ({ uid, ...(K.attributes(uid, o) || {}) }))
    .filter(p => p.holder === h && p.actions && !p.revoked);
}

/* ---------- answering ---------- */
/* the master nodes above a node in every classification it sits in: what a scope may name */
function coverOf(uid, o) {
  const R0 = R(), at = o && o.at;
  const up = new Set([uid]);
  for (const h of [M.TRADE, R0.universe]) for (const a of K.ancestors(h, uid, { namespace: NS(), at })) up.add(a);
  return up;
}
/* may the holder do an action with a node (an item, by default) at an instant? Answers the
   permission that allows it, or the reason it is refused */
function allows(holder, action, ref, o) {
  o = o || {};
  const uid = M.uidOf(ref);
  if (!uid) return { ok: false, reason: "Not in the platform master" };
  const object = o.object || defaultOf(objects());
  const cover = coverOf(uid, o);
  const held = of(holder, o).filter(p => (p.objects || []).includes(object) && (!p.scope.length || p.scope.some(s => cover.has(s))));
  const hit = held.find(p => closure(p.actions).has(action));
  if (hit) return { ok: true, permission: hit };
  return { ok: false, reason: held.length ? "Your permission does not allow " + action + " here" : "Not permitted by the platform — ask the platform admin to grant it" };
}
/* everything the holder may see: every master item under the scopes of its view permissions */
function visibleItems(holder, o) {
  const ps = of(holder, o).filter(p => closure(p.actions).has(R().viewAction));
  if (ps.some(p => !p.scope.length)) return M.items();
  const seen = new Set();
  for (const p of ps) for (const s of p.scope)
    for (const u of [s, ...K.descendants(M.TRADE, s, { namespace: NS() }), ...K.descendants(R().universe, s, { namespace: NS() })])
      if (K.isA(K.internal.nodeRow(u).kind, R().item, NS())) seen.add(u);
  return [...seen].map(u => M.node(u, o));
}

/* ---------- store access levels: one item, one store, as the console sets them ---------- */
/* the level a set of actions is: the level whose actions are exactly those */
function levelOf(acts) {
  const want = [...closure(acts)].sort().join();
  const l = levels().find(t => [...closure(t.actions || [])].sort().join() === want);
  return l ? l.name : null;
}
/* the item-scoped permissions a holder has on one item */
const onItem = (holder, uid) => of(holder).filter(p => p.scope.length === 1 && p.scope[0] === uid);
/* sets a store's access level on one item: its item-scoped permissions are revoked and, unless
   the level allows nothing, one permission with the level's actions is granted */
function setAccess(holder, ref, level, actor) {
  const uid = M.uidOf(ref) || fail("Unknown global product", 404);
  const l = levels().find(t => t.name === level) || fail("Unknown access level: " + level);
  return K.internal.tx(() => {
    for (const p of onItem(holder, uid)) revoke(p.uid, null, actor);
    return (l.actions || []).length ? grant({ holder, scope: [uid], actions: l.actions }, actor) : null;
  });
}
/* every store's access level on one item */
function accessOn(ref) {
  const uid = M.uidOf(ref);
  if (!uid) return [];
  return K.nodes(R().permission, NS()).map(p => ({ uid: p, ...(K.attributes(p) || {}) }))
    .filter(p => !p.revoked && p.scope.length === 1 && p.scope[0] === uid)
    .map(p => ({ holder: p.holder, level: levelOf(p.actions), permission: p.uid }));
}

/* ---------- an install that kept store access as rows: moved onto permissions once ---------- */
function legacyTable(name) {
  const D = require("./db.js");
  const rows = D.USE_PG
    ? D.all("SELECT table_name AS name FROM information_schema.tables WHERE table_name=?", name)
    : D.all("SELECT name FROM sqlite_master WHERE type='table' AND name=?", name);
  return rows.length > 0;
}
function adoptLegacy() {
  const TABLE = "store_product_config";
  if (!legacyTable(TABLE)) return 0;
  const D = require("./db.js");
  let n = 0;
  K.internal.tx(() => {
    for (const r of D.all("SELECT * FROM " + TABLE + " WHERE enabled=1")) {
      const uid = M.uidOf(r.global_product_id);
      const level = levels().find(t => t.name === r.permissions);
      if (!uid || !level) { console.error("store access not moved (unknown product or level):", r.tenant_id, r.global_product_id, r.permissions); continue; }
      setAccess(storeHolder(r.tenant_id), uid, level.name, "migration");
      n++;
    }
    D.run("DROP TABLE " + TABLE);
  });
  return n;
}

module.exports = { actions, objects, reviews, levels, closure, storeHolder, grant, revoke, of, allows, visibleItems, levelOf, setAccess, accessOn, adoptLegacy };
