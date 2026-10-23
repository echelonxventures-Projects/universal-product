/* LUXORA Platform — contributions to the platform master and the addenda they leave
   (GLOBAL_MASTER.md §3, roadmap P28; owner Evolution).

   A platform never changes the master directly. What it proposes — an addition, a modification,
   a local value, a retirement — is a CONTRIBUTION: a node recording who proposed what, on which
   entity, under which permission. The global platform reviews every one (DEC-015, DEC-017). Once
   approved it lands where the reviewer places it:
     apply     — the master entity changes (a new version), or the new entity joins the master
     new       — a new master entity, beside the one it was proposed on
     addendum  — an extension attached to the entity without changing it, applicable to the
                 platforms and places the reviewer names (a retirement as an addendum hides the
                 entity there)
   or it is rejected, with a reason the platform reads.

   When a contribution takes effect is the permission's review mode: reviewed before (nothing
   changes until approval) or after (it takes effect at once for the proposing platform only, as a
   provisional addendum — or a provisional entity for an addition — that the review then places or
   withdraws). The actions, placements and review modes are master vocabularies; the life of a
   contribution is the `contribution` state machine, asked by what a state means.

   What a platform sees of an entity is the master plus the addenda that apply to it, filtered to
   the attributes its permission makes visible (view()). */
"use strict";

const K = require("./kernel.js");
const M = require("./platform-master.js");
const MP = require("./master-permissions.js");
const states = require("./states.js");
const fail = (msg, status) => { const e = new Error(msg); e.status = status || 400; throw e; };
const R = () => M.ROLES;
const NS = () => M.NAMESPACE;
const machine = () => R().contributionMachine;
const term = (vocab, name) => M.vocabulary(vocab).find(t => t.name === name) || null;
const clean = o => Object.fromEntries(Object.entries(o).filter(([, v]) => v !== undefined && v !== null));

function read(uid) {
  const a = K.attributes(uid);
  if (!a || K.internal.nodeRow(uid).kind !== R().contribution) fail("Unknown contribution", 404);
  return { uid, ...a, state: states.display(machine(), a.status), awaiting: states.is(machine(), a.status, "awaiting_review") };
}
function addenda(of, o) {
  return K.nodes(R().addendum, NS()).map(u => ({ uid: u, ...(K.attributes(u, o) || {}) })).filter(a => a.of === of);
}

/* ---------- proposing ---------- */
/* the node a permission must cover: the target, or for an addition the place it is proposed under */
const coverFor = (act, i) => act.target ? i.target : ((i.proposal && i.proposal.at && i.proposal.at[0]) || (i.proposal && i.proposal.universe && (R().universePrefix + i.proposal.universe)));
function propose(holder, input, by) {
  const i = input || {};
  const act = term(R().contributionActions, i.action) || fail("Unknown contribution: " + i.action);
  const target = act.target ? (M.uidOf(i.target) || fail("Not in the platform master: " + i.target, 404)) : null;
  const cover = coverFor(act, { ...i, target });
  if (!cover) fail("Say where in the master the addition belongs");
  const allowed = MP.allows(holder, act.needs, cover, { object: i.object });
  if (!allowed.ok) fail(allowed.reason, 403);
  const review = allowed.permission.review;
  const now = !term(R().reviews, review).effectiveOnApproval;
  return K.internal.tx(() => {
    const uid = K.createNode(R().contribution, { namespace: NS(), attributes: clean({
      holder, action: act.name, object: i.object || null, target, patch: i.patch || null, proposal: i.proposal || null,
      review, status: states.initial(machine()), by: by || holder }) }, by);
    /* reviewed after: the change holds at once, for the proposing platform only */
    if (now) {
      const provisional = act.target
        ? K.createNode(R().addendum, { namespace: NS(), attributes: clean({ of: target, patch: i.patch || {}, holders: [holder], places: [], hidden: !!act.hides, provisional: true, from: uid }) }, by)
        : M.createItem({ ...i.proposal, lifecycle: undefined }, by);
      K.record(uid, { provisional }, null, by);
    }
    return read(uid);
  });
}
function withdraw(holder, uid, by) {
  const c = read(uid);
  if (c.holder !== holder) fail("Unknown contribution", 404);
  return settle(c, states.actionTarget(machine(), "withdraw"), { by });
}

/* ---------- reviewing ---------- */
/* the global platform decides: approve with a placement, or reject with a reason */
function review(uid, decision, by) {
  const c = read(uid);
  if (!c.awaiting) fail("This contribution has already been decided", 409);
  const d = decision || {};
  const to = states.actionTarget(machine(), d.action);
  if (!to || !states.can(machine(), c.status, to)) fail("Approve or reject the contribution");
  if (by && by === c.by) fail("A contribution is reviewed by someone other than its author", 403);
  if (!states.is(machine(), to, "success")) {
    if (!String(d.reason || "").trim()) fail("Say why it is rejected");
    return settle(c, to, { by, reason: d.reason });
  }
  const place = term(R().placements, d.placement) || fail("Say where it lands: " + M.vocabulary(R().placements).map(t => t.name).join(", "));
  if (!(place.for || []).includes(c.action)) fail(`A ${c.action} cannot land as ${place.name}`);
  return K.internal.tx(() => {
    const result = land(c, place, d, by);
    return settle(c, to, { by, placement: place.name, result, reason: d.reason });
  });
}
/* where an approved contribution lands; returns the node it changed or made */
function land(c, place, d, by) {
  const act = term(R().contributionActions, c.action);
  const provisionalItem = !act.target && c.provisional;
  if (place.attaches) {
    if (c.provisional) retireNode(c.provisional, by);
    return K.createNode(R().addendum, { namespace: NS(), attributes: clean({ of: c.target, patch: c.patch || {},
      holders: d.holders || [c.holder], places: d.places || [], hidden: !!act.hides, provisional: false, from: c.uid }) }, by);
  }
  if (!act.target) return provisionalItem || M.createItem(c.proposal, by);
  if (c.provisional) retireNode(c.provisional, by);
  if (place.creates) return copyWith(c.target, c.patch || {}, by);
  if (act.hides) {
    M.update(c.target, { lifecycle: M.vocabulary(R().lifecycle).find(t => t.retired).name }, by);
    return c.target;
  }
  M.update(c.target, c.patch || {}, by);
  return c.target;
}
/* a new entity: the target's kind, places and attributes with the patch over them */
function copyWith(target, patch, by) {
  const n = M.node(target);
  const at = K.placementsOf(M.TRADE, n.uid, { namespace: NS() }).filter(Boolean);
  const universe = M.universeOf(n.uid);
  const { facts, ...rest } = patch;
  return M.createItem({ kind: n.kind, at, universe: universe || undefined, ...n.attributes, ...rest, facts: { ...(n.attributes.facts || {}), ...(facts || {}) } }, by);
}
function settle(c, to, extra) {
  const e = extra || {};
  const mv = states.apply(machine(), { from: c.status, to, row: c });
  if (!states.is(machine(), to, "success") && c.provisional) retireNode(c.provisional, e.by);
  K.record(c.uid, clean({ status: mv.to, placement: e.placement, result: e.result, reason: e.reason, reviewed_by: e.by }), null, e.by);
  return read(c.uid);
}
/* a node that no longer holds: hidden from every listing and, for an item, retired; history kept */
function retireNode(uid, by) {
  const row = K.internal.nodeRow(uid);
  if (K.isA(row.kind, R().item, NS())) M.update(uid, { lifecycle: M.vocabulary(R().lifecycle).find(t => t.retired).name }, by);
  require("./kernel-lifecycle.js").archive(uid, by);
}

/* ---------- reading ---------- */
function list(o) {
  o = o || {};
  return K.nodes(R().contribution, NS()).map(read)
    .filter(c => (!o.holder || c.holder === o.holder) && (!o.status || c.status === o.status) && (!o.awaiting || c.awaiting))
    .reverse();
}
/* what a holder sees of an entity: the master, with the addenda for it (and its place) over it,
   cut to the attributes its permission makes visible; null when an addendum hides it there */
function view(holder, ref, o) {
  o = o || {};
  const n = M.node(ref, { ...o, lang: undefined });
  const attrs = { ...n.attributes, facts: { ...(n.attributes.facts || {}) } };
  for (const a of addenda(n.uid, o)) {
    if (a.holders && a.holders.length && !a.holders.includes(holder)) continue;
    if (a.places && a.places.length && !M.placeWithin(o.place || null, a.places)) continue;
    if (a.hidden) return null;
    const { facts, ...rest } = a.patch || {};
    Object.assign(attrs, rest);
    Object.assign(attrs.facts, facts || {});
  }
  const p = MP.allows(holder, R().viewAction, n.uid, o);
  if (!p.ok) return null;
  const visible = p.permission.visible || [];
  if (visible.length) attrs.facts = Object.fromEntries(Object.entries(attrs.facts).filter(([k]) => visible.includes(k)));
  /* text in many languages is answered in the language asked, after the addenda are over it */
  if (o.lang) {
    const localised = new Set(K.SEED.valueTypes.filter(t => t.localised).map(t => t.key));
    for (const a of K.kindOf(n.kind, NS()).attributes) if (localised.has(a.type) && attrs[a.key] != null) attrs[a.key] = K.text(attrs[a.key], o.lang);
  }
  return { ...n, attributes: attrs };
}

module.exports = { propose, withdraw, review, list, read, view, addenda };
