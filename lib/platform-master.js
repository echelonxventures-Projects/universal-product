/* LUXORA Platform — the platform master (GLOBAL_MASTER.md, roadmap P27; owners Identity,
   Semantic, Registry, Relationship and Measure).

   Every product and service of every industry is described ONCE, here, on the kernel:
     · its levels are kinds declared as rows (domain › industry › category › subcategory ›
       family › model, and any added), each kind extending another, so a new level, a new
       product type or a new service type is data;
     · what it is and where it sits are nodes placed in hierarchies — the trade taxonomy, the
       tariff nomenclature, the scientific nomenclature, tax classes, any added — one node in
       many hierarchies at once;
     · its codes are identifiers under identifier schemes, each declaring its format, its check
       rule, its issuing authority and the places it applies in (lib/kernel.js checks them);
     · what a source model calls columns are attribute definitions: nodes binding a typed,
       constrained fact to taxonomy nodes and kinds, inherited down the taxonomy and applicable
       by place, so an item's attribute set is computed, never copied;
     · its relationships (accessory of, generic of, fits, …) are hierarchies of their own;
     · units, packaging levels, media kinds, lifecycle states, fulfilment modes, roles and every
       other vocabulary are nodes too.
   Platforms see the master through permissions as projections (P28); nothing here is copied
   into a platform.

   The starter content (lib/seed/master.json) is written into the kernel the first time the
   master is asked for anything, in one transaction, and only what is missing: an edit made
   since is never overwritten. */
"use strict";

const K = require("./kernel.js");
const SEED = require("./seed/master.json");

/* the kinds and hierarchies this module plays a part with are named by role in the seed */
const NS = SEED.namespace, ACTOR = SEED.actor, KEY = SEED.keyScheme, R = SEED.roles;
const TRADE = R.trade;
const fail = (msg, status) => { const e = new Error(msg); e.status = status || 400; throw e; };
const uniq = xs => [...new Set(xs)];

/* ============================== the starter content ============================== */
let ensured = false;
const byKey = key => key == null ? null : K.resolveIdentifier(KEY, String(key));
/* a node with a key: found by the key, else created (and placed), never rewritten */
function keyed(kind, key, attributes, place, identifiers) {
  let uid = byKey(key);
  if (!uid) uid = K.createNode(kind, { namespace: NS, attributes, identifiers: { [KEY]: key, ...(identifiers || {}) } }, ACTOR);
  if (place && !K.placementsOf(place.hierarchy, uid).includes(place.parent || null)) K.place(place.hierarchy, uid, place.parent || null, { namespace: NS }, ACTOR);
  return uid;
}
const clean = o => Object.fromEntries(Object.entries(o).filter(([, v]) => v !== undefined && v !== null && !(Array.isArray(v) && !v.length)));

function writeTree(nodes, hierarchy, parent) {
  for (const n of nodes) {
    const ids = n.codes || {};
    const uid = keyed(n.kind, n.key, clean({ title: n.title, summary: n.summary, icon: n.icon, position: n.position, requires: n.requires, recommends: n.recommends }), { hierarchy, parent }, ids);
    writeTree(n.children || [], hierarchy, uid);
  }
}
/* a place is held as its code ({ scheme, value }) and resolved when asked, so a declaration
   written before the place tree is loaded still names the place */
const refOf = r => r && typeof r === "object" ? K.resolveIdentifier(r.scheme, r.value) : r;

function ensure() {
  if (ensured) return;
  K.ensureTables();
  K.internal.tx(() => {
    for (const k of SEED.kinds) if (!K.kindOf(k.kind, NS)) K.defineKind({ ...k, namespace: NS }, ACTOR);
    for (const h of SEED.hierarchies) if (!K.hierarchyOf(h.hierarchy, NS)) K.defineHierarchy({ hierarchy: h.hierarchy, owner: h.owner, label: h.label, namespace: NS }, ACTOR);
    /* identifier schemes first: every code written after this is checked against its scheme */
    const SCHEME = K.SEED.identity.declaredBy;
    for (const s of SEED.schemes) {
      if (K.resolveIdentifier(SCHEME, s.key)) continue;
      K.createNode(SCHEME, { namespace: NS, identifiers: { [SCHEME]: s.key },
        attributes: clean({ title: s.title, pattern: s.pattern, check: s.check, authority: s.authority, places: s.places }) }, ACTOR);
    }
    const DIM = R.dimension, UNIT = R.unit, UNITS = R.units;
    for (const d of SEED.dimensions) if (!K.resolveIdentifier(DIM, d.key)) K.createNode(DIM, { namespace: NS, identifiers: { [DIM]: d.key }, attributes: { title: d.title } }, ACTOR);
    for (const u of SEED.units) {
      if (K.resolveIdentifier(UNIT, u.key)) continue;
      const uid = K.createNode(UNIT, { namespace: NS, identifiers: { [UNIT]: u.key }, attributes: clean({ title: u.title, symbol: u.symbol, factor: u.factor, offset: u.offset }) }, ACTOR);
      K.place(UNITS, uid, K.resolveIdentifier(DIM, u.dimension), { namespace: NS }, ACTOR);
    }
    writeTree(SEED.taxonomy, TRADE, null);
    writeTree(SEED.tariff, R.tariff, null);
    syncUniverses();
    for (const a of SEED.attributes) keyed(R.attribute, a.key, clean({
      name: a.name, title: a.title, type: a.type, group: a.group, constraints: a.constraints, required: a.required || undefined,
      unit_dimension: a.unitDimension ? K.resolveIdentifier(DIM, a.unitDimension) : undefined,
      at: a.at.map(byKey), for_kinds: a.forKinds, places: a.places }));
    for (const v of SEED.vocabularies) {
      const vu = keyed(R.vocabulary, v.key, clean({ title: v.title }), { hierarchy: R.vocabularies, parent: null });
      v.terms.forEach((t, i) => keyed(R.term, t.key, clean({ name: t.name, title: t.title, data: t.data, position: i }), { hierarchy: R.vocabularies, parent: vu }));
    }
  });
  ensured = true;
}

/* ============================== reading ============================== */
const keyOf = uid => K.identifiers(uid)[KEY] || null;
const uidOf = ref => { ensure(); const r = String(ref || ""); return K.internal.nodeRow(r) ? r : byKey(r); };
function node(ref, o) {
  const uid = uidOf(ref);
  if (!uid) fail("Not in the platform master: " + ref, 404);
  const row = K.internal.nodeRow(uid);
  return { uid, key: keyOf(uid), kind: row.kind, attributes: K.attributes(uid, o) || {}, identifiers: K.identifiers(uid, o) };
}
/* the children of a node (null: the top) in a hierarchy, in position order */
function children(ref, o) {
  o = o || {};
  const h = o.hierarchy || TRADE;
  const parent = ref == null ? null : uidOf(ref);
  if (ref != null && !parent) fail("Not in the platform master: " + ref, 404);
  return K.children(h, parent, { namespace: NS, at: o.at }).map(u => node(u, o))
    .sort((a, b) => (a.attributes.position || 0) - (b.attributes.position || 0));
}
/* a subtree as nested nodes, to a depth */
function tree(ref, o) {
  o = o || {};
  const depth = o.depth == null ? 1 : Number(o.depth);
  const walk = (r, d) => children(r, o).map(n => d > 1 ? { ...n, children: walk(n.uid, d - 1) } : n);
  return walk(ref == null ? null : ref, depth);
}
/* where a node sits: every path from the top of a hierarchy down to it, as keys */
const paths = (ref, o) => K.paths((o && o.hierarchy) || TRADE, uidOf(ref), { namespace: NS }).map(p => p.map(keyOf));
/* a vocabulary's terms: { name, key, title, ...data } in order */
function vocabulary(key, o) {
  const v = uidOf(key);
  if (!v) fail("Unknown vocabulary: " + key, 404);
  return children(v, { ...(o || {}), hierarchy: R.vocabularies }).map(t => ({ name: t.attributes.name, key: t.key, title: t.attributes.title, ...(t.attributes.data || {}) }));
}
function vocabularies() {
  ensure();
  return K.nodes(R.vocabulary, NS).map(u => ({ key: keyOf(u), ...K.attributes(u) }));
}

/* the item kind a product universe is sold as: the kind whose term names the universe, else the
   kind the vocabulary marks for universes no kind names (a universe added later still sells) */
function kindForUniverse(universe) {
  const terms = vocabulary(R.itemKinds);
  return terms.find(t => (t.universes || []).includes(universe)) || terms.find(t => t.unmappedUniverses) || fail("No item kind is marked for universes no kind names");
}
/* the product universes are the registry's vocabulary (the constitution's, plus any an operator
   adds), never restated here: each becomes a classification node under its declared prefix */
const declaredUniverses = () => require("./registry.js").list("productUniverses") || [];
function syncUniverses() {
  writeTree(declaredUniverses().filter(u => u && u.key).map((u, i) => ({ key: R.universePrefix + u.key, kind: R.universeKind,
    title: { [require("./expression.js").SEED.sourceLanguage]: u.name || u.key }, icon: u.icon, position: i })), R.universe, null);
}
/* a universe's node — one the registry declares since the master was written is added on asking */
function universeNode(key) {
  ensure();
  const k = R.universePrefix + key;
  if (!byKey(k) && declaredUniverses().some(u => u && u.key === key)) K.internal.tx(syncUniverses);
  return byKey(k);
}
const universeOf = uid => { const u = K.parents(R.universe, uid, { namespace: NS })[0]; return u ? keyOf(u).slice(R.universePrefix.length) : null; };
/* the lifecycle term for a state, or for a status an older record used */
function lifecycleTerm(state) {
  const terms = vocabulary(R.lifecycle);
  return terms.find(t => t.name === state) || terms.find(t => (t.was || []).includes(state)) || null;
}

/* ============================== attribute sets ============================== */
/* the attribute definitions that apply to an item of `kind` placed under `at` (taxonomy nodes),
   in a context place: a definition bound nowhere applies everywhere; one bound to taxonomy nodes
   applies under any of them; one bound to kinds applies to those kinds and every kind extending
   them; one bound to places applies at those places and everywhere inside them */
function definitions() {
  ensure();
  return K.nodes(R.attribute, NS).map(u => ({ uid: u, key: keyOf(u), ...K.attributes(u) }));
}
function placeIsWithin(place, places) {
  if (!places || !places.length) return true;
  if (!place) return false;
  const G = require("./places.js");
  const up = new Set([place, ...K.ancestors(G.HIERARCHY, place, { namespace: G.NAMESPACE })]);
  return places.map(refOf).some(p => up.has(p));
}
function attributeSet(o) {
  o = o || {};
  const kind = o.kind ? K.kindOf(o.kind, NS) : null;
  if (o.kind && !kind) fail("Unknown kind: " + o.kind);
  const at = (o.at || []).map(uidOf).filter(Boolean);
  const under = new Set(at.flatMap(u => [u, ...K.ancestors(TRADE, u, { namespace: NS })]));
  return definitions().filter(d =>
    (!d.at || !d.at.length || d.at.some(u => under.has(u)))
    && (!d.for_kinds || !d.for_kinds.length || (kind && d.for_kinds.some(k => kind.lineage.includes(k))))
    && placeIsWithin(o.place || null, d.places))
    .sort((a, b) => String(a.group || "").localeCompare(String(b.group || "")) || (a.position || 0) - (b.position || 0));
}
/* checks facts against the definitions that apply; returns them cleaned, or fails naming the fact */
function checkFacts(facts, defs, o) {
  const by = new Map(defs.map(d => [d.name, d]));
  const out = {};
  for (const [name, v] of Object.entries(facts || {})) {
    const d = by.get(name);
    if (!d) fail(`No attribute ${name} applies here`);
    if (v === null) { out[name] = null; continue; }
    K.internal.checkValue(d.type, d.constraints || {}, v, { label: name });
    if (d.unit_dimension && v && v.unit && K.parents(R.units, v.unit, { namespace: NS })[0] !== d.unit_dimension)
      fail(`${name} must be measured in a unit of its dimension`);
    out[name] = v;
  }
  if (o && o.whole) for (const d of defs) if (d.required && (o.whole[d.name] == null)) fail(`${d.name} is required here`);
  return out;
}

/* ============================== items ============================== */
const ITEM = R.item;
/* creates an item: its kind, where it sits in the trade taxonomy (one or many places), its title
   and facts, its codes. Facts are checked against the attribute set that applies there */
function createItem(input, actor) {
  ensure();
  const i = input || {};
  const kind = K.kindOf(i.kind, NS);
  if (!kind || !kind.lineage.includes(ITEM)) fail("An item's kind must be a product or service kind: " + i.kind);
  const at = (i.at || []).map(r => uidOf(r) || fail("Not in the platform master: " + r));
  const universe = i.universe ? (universeNode(i.universe) || fail("Unknown product universe: " + i.universe)) : null;
  if (!at.length && !universe) fail("Say where the item sits in the taxonomy");
  if (i.lifecycle && !lifecycleTerm(i.lifecycle)) fail("Unknown lifecycle state: " + i.lifecycle);
  if (i.key && byKey(i.key)) fail("That key is taken: " + i.key, 409);
  const facts = checkFacts(i.facts, attributeSet({ kind: i.kind, at, place: i.place }), { whole: i.facts || {} });
  return K.internal.tx(() => {
    const uid = K.createNode(i.kind, { namespace: NS, attributes: clean({ title: i.title, summary: i.summary, description: i.description, facts, media: i.media, fulfilment: i.fulfilment, lifecycle: i.lifecycle && lifecycleTerm(i.lifecycle).name, icon: i.icon, profile: i.profile }),
      identifiers: clean({ ...(i.identifiers || {}), [KEY]: i.key }), validFrom: i.validFrom }, actor || ACTOR);
    for (const p of at) K.place(TRADE, uid, p, { namespace: NS, validFrom: i.validFrom }, actor || ACTOR);
    if (universe) K.place(R.universe, uid, universe, { namespace: NS, validFrom: i.validFrom }, actor || ACTOR);
    return uid;
  });
}
/* records facts on an item (merged over what it has), checked against where it sits now */
function setFacts(ref, facts, o, actor) {
  const n = node(ref);
  const at = K.placementsOf(TRADE, n.uid, { namespace: NS }).filter(Boolean);
  const merged = { ...(n.attributes.facts || {}), ...facts };
  for (const [k, v] of Object.entries(merged)) if (v === null) delete merged[k];
  checkFacts(facts, attributeSet({ kind: n.kind, at, place: o && o.place }), { whole: merged });
  return K.record(n.uid, { facts: merged }, o, actor || ACTOR);
}
/* moves an item: ends the placements it no longer has and adds the new ones (history keeps the old) */
function move(ref, to, actor) {
  const n = node(ref);
  const want = (to.at || []).map(r => uidOf(r) || fail("Not in the platform master: " + r));
  const sync = (h, wanted) => {
    const have = K.placementsOf(h, n.uid, { namespace: NS }).filter(Boolean);
    for (const p of have) if (!wanted.includes(p)) K.endPlacement(h, n.uid, p, null, { namespace: NS }, actor || ACTOR);
    for (const p of wanted) if (!have.includes(p)) K.place(h, n.uid, p, { namespace: NS }, actor || ACTOR);
  };
  return K.internal.tx(() => {
    if (to.at) sync(TRADE, want);
    if (to.universe !== undefined) sync(R.universe, to.universe ? [universeNode(to.universe) || fail("Unknown product universe: " + to.universe)] : []);
  });
}
/* records an item's own attributes (title, description, media, lifecycle, profile, …) */
function update(ref, patch, actor) {
  const n = node(ref);
  const p = { ...patch };
  if (p.lifecycle) p.lifecycle = (lifecycleTerm(p.lifecycle) || fail("Unknown lifecycle state: " + p.lifecycle)).name;
  if (p.facts) { setFacts(n.uid, p.facts, null, actor); delete p.facts; }
  return Object.keys(p).length ? K.record(n.uid, p, null, actor || ACTOR) : null;
}
function items(o) {
  ensure();
  o = o || {};
  const under = o.under ? uidOf(o.under) : null;
  const uids = under ? K.descendants(TRADE, under, { namespace: NS }) : K.nodes(ITEM, NS, { withSubkinds: true });
  return uids.filter(u => K.isA(K.internal.nodeRow(u).kind, o.kind || ITEM, NS)).map(u => node(u, o));
}

/* ============================== relationships ============================== */
/* the relationship types are the hierarchies declared under the relation prefix: a new one is a
   new hierarchy, declared like any other */
function relations() {
  ensure();
  return require("./db.js").all("SELECT hierarchy, spec FROM k_hierarchies WHERE namespace=? AND scope IS NULL AND rec_to IS NULL AND hierarchy LIKE ? ORDER BY id", NS, R.relationPrefix + "%")
    .map(h => ({ key: h.hierarchy.slice(R.relationPrefix.length), hierarchy: h.hierarchy, title: K.internal.J(h.spec, {}).label }));
}
const relationOf = key => relations().find(r => r.key === key) || fail("Unknown relationship: " + key);
function defineRelation(key, title, actor) {
  ensure();
  K.internal.keyOk(key, "Relationship");
  return K.defineHierarchy({ hierarchy: R.relationPrefix + key, owner: R.relationOwner, label: String(title || key), namespace: NS }, actor || ACTOR);
}
/* `from` is related to `to` (an accessory of, a generic of, fits, …) over a window */
function relate(rel, from, to, o, actor) {
  const r = relationOf(rel);
  return K.place(r.hierarchy, uidOf(from) || fail("Unknown item: " + from, 404), uidOf(to) || fail("Unknown item: " + to, 404), { namespace: NS, ...(o || {}) }, actor || ACTOR);
}
/* the items related to one: outward (what it is related to) or inward (what is related to it) */
function related(ref, rel, o) {
  const r = relationOf(rel), uid = uidOf(ref);
  return (o && o.inward ? K.children(r.hierarchy, uid, { namespace: NS }) : K.parents(r.hierarchy, uid, { namespace: NS })).map(u => node(u, o));
}

/* ============================== measure ============================== */
/* converts a quantity to another unit of the same dimension: amount × factor + offset is the
   base value of the dimension, so offset scales (temperature) convert as well as plain ones */
function convert(q, toUnit) {
  ensure();
  const to = K.internal.nodeRow(toUnit) ? toUnit : K.resolveIdentifier(R.unit, toUnit);
  if (!q || !to) fail("Unknown unit");
  const dim = u => K.parents(R.units, u, { namespace: NS })[0];
  if (dim(q.unit) !== dim(to)) fail("Those units measure different things");
  const a = K.attributes(q.unit), b = K.attributes(to);
  const base = q.amount * a.factor + (a.offset || 0);
  return { amount: (base - (b.offset || 0)) / b.factor, unit: to };
}
const unit = key => { ensure(); return K.resolveIdentifier(R.unit, key); };

/* ============================== registry lists the master answers ==============================
   Every list another part of the platform reads by name (product types, industries, units, …)
   is a projection of the master, declared in the seed: where its rows come from and their shape.
   Nothing is copied into the registry; an edit to a list is an edit to the master. */
const P = SEED.projections || {};
const L = () => require("./expression.js").SEED.sourceLanguage;
const text = v => K.text(v, L());
const projected = name => Object.prototype.hasOwnProperty.call(P, name);
/* the rows of a projection's source: { name, title, ...facts } */
const fromVocabulary = p => vocabulary(p.key);
const fromKind = p => {
  const out = [];
  const walk = (parent, up) => children(parent, { hierarchy: p.hierarchy }).forEach(n => {
    if (K.isA(n.kind, p.kind, NS)) out.push({ name: n.key, title: n.attributes.title, icon: n.attributes.icon, [p.parentField]: up });
    walk(n.uid, n.key);
  });
  walk(null, null);
  return out;
};
const fromUnits = () => K.nodes(R.dimension, NS).flatMap(d => K.children(R.units, d, { namespace: NS }).map(u => {
  const a = K.attributes(u);
  return { name: K.identifiers(u)[R.unit], title: a.title, symbol: a.symbol, dim: K.identifiers(d)[R.dimension], factor: a.factor, offset: a.offset || 0 };
}));
/* the codes an item may carry: the item kind's declared schemes, each with its declaration */
const fromSchemes = () => K.kindOf(R.item, NS).schemes.filter(k => k !== KEY).map(k => {
  const u = K.resolveIdentifier(K.SEED.identity.declaredBy, k);
  return { name: k, title: u ? K.attributes(u).title : { [L()]: k } };
});
const fromRelations = () => relations().map(r => ({ name: r.key, title: { [L()]: r.title } }));
const SOURCES = { vocabulary: fromVocabulary, kind: fromKind, units: fromUnits, schemes: fromSchemes, relations: fromRelations };
const facts = r => { const o = { ...r }; delete o.name; delete o.title; delete o.key; return o; };
const SHAPES = {
  objects: rows => rows.map(r => clean({ key: r.name, name: text(r.title), ...facts(r) })),
  names: rows => rows.map(r => r.name),
  codes: rows => rows.map(r => r.name),
  titles: rows => rows.map(r => text(r.title)),
  map: (rows, p) => Object.fromEntries(rows.map(r => [r.name, r[p.field] || []])),
  /* each unit against its dimension's base unit: one of it is this many base units */
  conversions: rows => Object.fromEntries(rows.filter(r => r.factor !== 1 && !r.offset).map(r => {
    const base = rows.find(b => b.dim === r.dim && b.factor === 1 && !b.offset);
    return base ? [r.name + "→" + base.name, r.factor] : null;
  }).filter(Boolean))
};
/* a list whose default is declared once, with every other list's (lib/seed/defaults.json),
   carries the flag on that row where no row flags itself */
function flagDefault(name, rows) {
  const want = (require("./seed/defaults.json").lists || {})[name];
  if (!want || !Array.isArray(rows) || rows.some(r => r && typeof r === "object" && r.default)) return rows;
  return rows.map(r => r && typeof r === "object" && r.key === want ? { ...r, default: true } : r);
}
let cacheSeq = -1; const cache = new Map();
/* a projection, recomputed only after the master has changed */
function projection(name) {
  if (!projected(name)) return undefined;
  ensure();
  const seq = (require("./db.js").get("SELECT MAX(seq) AS s FROM k_events") || {}).s || 0;
  if (seq !== cacheSeq) { cache.clear(); cacheSeq = seq; }
  if (!cache.has(name)) cache.set(name, flagDefault(name, SHAPES[P[name].shape](SOURCES[P[name].from](P[name]), P[name])));
  return cache.get(name);
}
const projections = () => Object.keys(P);
/* an entry of a projected list, as the registry's console saves it, written to the master */
const TERM = (p, item) => typeof item === "object" && item ? String(item.key || "") : String(item || "");
const saveVocabulary = (p, item, actor) => {
  const name = p.shape === "titles" ? String(item).trim().toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "") : TERM(p, item);
  if (!name) fail("An entry needs a key");
  const title = { [L()]: typeof item === "object" ? String(item.name || name) : String(item) };
  const data = typeof item === "object" ? facts(item) : {};
  const term = vocabulary(p.key).find(t => t.name === name);
  if (term) return K.record(term_uid(p.key, name), clean({ title, data: Object.keys(data).length ? data : undefined }), null, actor);
  return keyed(R.term, p.key + "." + name, clean({ name, title, data, position: vocabulary(p.key).length }), { hierarchy: R.vocabularies, parent: uidOf(p.key) });
};
const saveKind = (p, item, actor) => {
  const key = TERM(p, item);
  const uid = byKey(key), title = { [L()]: String(item.name || key) };
  if (uid) return K.record(uid, clean({ title, icon: item.icon }), null, actor);
  const parent = byKey(item[p.parentField]);
  if (!parent || !K.isA(K.internal.nodeRow(parent).kind, p.parentKind, NS)) fail(`Say which ${p.parentField} it sits under`);
  return keyed(p.kind, key, clean({ title, icon: item.icon }), { hierarchy: p.hierarchy, parent });
};
const saveUnits = (p, item, actor) => {
  const key = TERM(p, item), uid = K.resolveIdentifier(R.unit, key);
  const attrs = clean({ title: { [L()]: String(item.name || key) }, symbol: item.symbol || key, factor: item.factor == null ? undefined : Number(item.factor), offset: item.offset == null ? undefined : Number(item.offset) });
  if (uid) return K.record(uid, attrs, null, actor);
  const dim = K.resolveIdentifier(R.dimension, String(item.dim || "")) || fail("Say which dimension the unit measures");
  if (attrs.factor == null) fail("Say how many base units one of it is (factor)");
  const u = K.createNode(R.unit, { namespace: NS, identifiers: { [R.unit]: key }, attributes: attrs }, actor);
  K.place(R.units, u, dim, { namespace: NS }, actor);
  return u;
};
const saveSchemes = (p, item, actor) => {
  const key = TERM(p, item), by = K.SEED.identity.declaredBy, uid = K.resolveIdentifier(by, key);
  const attrs = clean({ title: { [L()]: String((item && item.name) || key) }, pattern: item && item.pattern, check: item && item.check, authority: item && item.authority });
  const out = uid ? K.record(uid, attrs, null, actor) : K.createNode(by, { namespace: NS, identifiers: { [by]: key }, attributes: attrs }, actor);
  /* an item may then carry a code under it */
  const own = require("./db.js").get("SELECT owner, spec FROM k_kinds WHERE namespace=? AND kind=? AND scope IS NULL AND rec_to IS NULL", NS, R.item);
  const spec = K.internal.J(own.spec, {});
  if (!spec.schemes.includes(key)) K.defineKind({ ...spec, kind: R.item, owner: own.owner, namespace: NS, schemes: [...spec.schemes, key] }, actor);
  return out;
};
const saveRelations = (p, item, actor) => defineRelation(TERM(p, item), (item && item.name) || TERM(p, item), actor);
const SAVES = { vocabulary: saveVocabulary, kind: saveKind, units: saveUnits, schemes: saveSchemes, relations: saveRelations };
const term_uid = (vocab, name) => byKey(vocab + "." + name);
function saveProjected(name, item, actor) {
  if (!projected(name)) fail("The platform master does not keep " + name);
  ensure();
  if (P[name].shape === "map" || P[name].shape === "conversions") fail(name + " follows from another list; edit that list");
  return K.internal.tx(() => SAVES[P[name].from](P[name], item, actor || ACTOR));
}
/* retiring an entry hides it from the list; its history and every reference to it stay */
function retireProjected(name, key, actor) {
  if (!projected(name)) fail("The platform master does not keep " + name);
  ensure();
  const p = P[name];
  const FIND = {
    vocabulary: () => term_uid(p.key, key), kind: () => byKey(key), units: () => K.resolveIdentifier(R.unit, key),
    schemes: () => K.resolveIdentifier(K.SEED.identity.declaredBy, key), relations: () => fail("A relationship type cannot be removed; it keeps the relationships recorded with it")
  };
  const uid = FIND[p.from]();
  if (!uid) fail("No such entry", 404);
  return require("./kernel-lifecycle.js").archive(uid, actor || ACTOR);
}
/* entries a registry list held before the master answered it, added to the master once */
function adoptList(name, items, actor) {
  if (!projected(name) || !Array.isArray(items)) return 0;
  const have = new Set((projection(name) || []).map(x => (x && typeof x === "object" ? String(x.key) : String(x))));
  let n = 0;
  for (const it of items) {
    const k = it && typeof it === "object" ? String(it.key) : String(it);
    if (have.has(k) || (P[name].shape === "titles" && have.has(String(it)))) continue;
    const item = P[name].from === "kind" && !it[P[name].parentField] ? { ...it, [P[name].parentField]: P[name].adoptUnder } : it;
    try { saveProjected(name, item, actor || "migration"); n++; } catch (e) { /* an entry the master cannot place is reported, never invented */ console.error("adopt " + name + "/" + k + ": " + e.message); }
  }
  return n;
}

/* ============================== summary ============================== */
function counts() {
  ensure();
  const n = kind => K.nodes(kind, NS, { withSubkinds: true }).length;
  return { classification: n(R.classification), items: n(ITEM), attributes: n(R.attribute), schemes: n(K.SEED.identity.declaredBy),
    units: n(R.unit), vocabularies: n(R.vocabulary), terms: n(R.term), relations: SEED.relations.length };
}

module.exports = { ensure, NAMESPACE: NS, KEY, TRADE, ROLES: R, placeWithin: placeIsWithin, uidOf, keyOf, node, children, tree, paths, vocabulary, vocabularies,
  projected, projection, projections, saveProjected, retireProjected, adoptList, defineRelation, /* the universes the registry has just declared, once the master is written */
  syncUniverses: () => ensured && K.internal.tx(syncUniverses),
  kindForUniverse, universeNode, universeOf, lifecycleTerm,
  definitions, attributeSet, checkFacts, createItem, setFacts, move, update, items, relations, relate, related, convert, unit, counts };
