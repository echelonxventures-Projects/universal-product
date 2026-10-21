/* LUXORA Platform — configuring a platform by its setup steps (GLOBAL_MASTER.md §4, roadmap P29;
   owner Package).

   A platform is configured by answering the blueprint's steps — official jurisdiction, working
   jurisdictions, languages, currencies, taxes, identity types, selling model, what it sells, how it
   delivers, features, sites. The steps are the master's `blueprint_steps` vocabulary: each names
   its answer, where its options come from, whether many may be chosen and whether it must be
   answered. Nothing here lists the steps.

   Each answer is its own setting on the kernel, in the platform's namespace, effective from the
   minute it is given for (DEC-018): a jurisdiction can move next Monday at 09:00 while the
   languages change now, and what held at any minute stays answerable. applyDue() applies whatever
   has come due: the jurisdiction and the places served move, the currency and language follow,
   the platform's permission on the master covers what it sells, and discovery decides the
   capabilities (lib/platform-discovery.js) — mandatory ones on, recommended ones on unless
   switched off, and what no capability provides yet recorded as requested, for the platform owner
   to edit (DEC-019). */
"use strict";

const K = require("./kernel.js");
const C = require("./kernel-context.js");
const M = require("./platform-master.js");
const fail = (msg, status) => { const e = new Error(msg); e.status = status || 400; throw e; };
const R = () => M.ROLES;
const S = () => require("./seed/master.json").setup;
const ns = tid => require("./master-permissions.js").storeHolder(tid);
const steps = () => M.vocabulary(R().blueprintSteps);
const setting = answer => S().settingPrefix + answer;

/* ---------- where each step's options come from ---------- */
const lang = () => require("./expression.js").SEED.sourceLanguage;
const reg = () => require("./registry.js");
const SOURCES = {
  places: () => reg().countries().map(c => ({ key: c.code, name: c.name })),
  languages: () => require("./expression.js").languages().map(l => ({ key: l.key, name: l.native || l.name || l.key })),
  valueUnits: () => reg().currencies().map(c => ({ key: c.code, name: c.name || c.code })),
  taxRegimes: () => (reg().list("taxModes").length ? reg().list("taxModes") : require("./db.js").all("SELECT key, name FROM tax_modes")).map(t => ({ key: t.key || t, name: t.name || t.key || t })),
  identityFields: () => reg().list("identityFields").map(k => ({ key: k, name: k })),
  sellingModels: () => reg().list("sellingModels").map(t => ({ key: t.key, name: t.name })),
  fulfilmentModes: () => reg().list("fulfilmentModes").map(t => ({ key: t.key, name: t.name })),
  master: () => [...reg().list("industries").map(i => ({ key: i.key, name: i.name, group: i.domain })),
    ...reg().list("productTypes").map(t => ({ key: t.key, name: t.name, group: "kind" }))],
  discovery: () => require("./capabilities.js").catalog().map(c => ({ key: c.key, name: c.name || c.key })),
  sites: () => require("./themes.js").presets().map(t => ({ key: t.key || t.id, name: t.name || t.key }))
};
function options(stepName) {
  const st = steps().find(s => s.name === stepName) || fail("Unknown setup step: " + stepName);
  return (SOURCES[st.from] || fail("No option source " + st.from))();
}
function describe() {
  return steps().map(s => ({ step: s.name, title: K.text(s.title, lang()), answer: s.answer, from: s.from, many: !!s.many, required: !!s.required }));
}

/* ---------- checking answers ---------- */
/* an answer to a step whose options are a master taxonomy may name any node of it */
const masterKnows = v => !!(M.uidOf(v) || M.vocabulary(R().itemKinds).some(t => t.name === v));
function check(answers, o) {
  const a = answers || {};
  for (const st of steps()) {
    const v = a[st.answer];
    const empty = v == null || (Array.isArray(v) && !v.length) || v === "";
    if (empty) { if (st.required && !(o && o.partial)) fail(`Answer “${K.text(st.title, lang())}”`); continue; }
    if (st.many && !Array.isArray(v)) fail(`“${K.text(st.title, lang())}” takes a list`);
    if (!st.many && Array.isArray(v)) fail(`“${K.text(st.title, lang())}” takes one answer`);
    /* an open step may name what is not built yet (it is requested); the master accepts any node */
    if (st.open) continue;
    const known = st.from === "master" ? null : new Set(options(st.name).map(x => String(x.key)));
    for (const x of [].concat(v)) if (known ? !known.has(String(x)) : !masterKnows(x)) fail(`“${x}” is not an option of “${K.text(st.title, lang())}”`);
  }
  return a;
}

/* ---------- answers on the kernel, each effective to the minute ---------- */
const minute = at => { const t = at ? new Date(at).getTime() : Date.now(); if (isNaN(t)) fail("Not a valid time: " + at); return new Date(Math.floor(t / S().resolutionMs) * S().resolutionMs).toISOString(); };
function declareSettings() {
  for (const st of steps()) if (!C.settingOf(setting(st.name), M.NAMESPACE)) C.declareSetting({ name: setting(st.name), owner: S().owner, type: S().valueType, namespace: M.NAMESPACE }, "setup");
  if (!C.settingOf(setting(S().appliedAnswer), M.NAMESPACE)) C.declareSetting({ name: setting(S().appliedAnswer), owner: S().owner, type: S().valueType, namespace: M.NAMESPACE }, "setup");
}
/* the answers in force at an instant (now by default) */
function answers(tid, o) {
  M.ensure();
  const out = {};
  for (const st of steps()) {
    const r = C.resolve(setting(st.name), { namespaces: [ns(tid)], at: o && o.at });
    if (r.resolved && r.from && r.from.namespace === ns(tid)) out[st.answer] = r.value.value;
  }
  return out;
}
/* gives answers (all or some) for a platform, effective from a minute (now by default) */
function answer(tid, given, o, actor) {
  o = o || {};
  M.ensure();
  const merged = check({ ...answers(tid, { at: o.at }), ...(given || {}) }, { partial: !!o.partial });
  const from = minute(o.at);
  K.internal.tx(() => {
    declareSettings();
    for (const st of steps()) if (given && Object.prototype.hasOwnProperty.call(given, st.answer))
      C.assign(setting(st.name), { value: given[st.answer] }, { namespace: ns(tid), validFrom: from }, actor);
  });
  return { answers: merged, from, applied: new Date(from) <= new Date() ? applyDue(tid, actor) : null };
}

/* ---------- applying what has come due ---------- */
const placeCode = v => String(v || "").toUpperCase();
const EFFECTS = {
  official: (tid, v, a, actor) => require("./stores.js").setJurisdiction(tid, placeCode(v), actor),
  working: (tid, v, a, actor) => { for (const c of v || []) require("./stores.js").serve(tid, placeCode(c), null, actor); },
  languages: (tid, v) => saveCommerce(tid, { locale: (v || [])[0] || null }),
  currencies: (tid, v) => saveCommerce(tid, { currency: (v || [])[0] || null }),
  taxes: (tid, v) => saveCommerce(tid, { taxMode: (v || [])[0] || null }),
  offerings: (tid, v, a, actor, applied) => {
    /* the platform's permission on the master covers what it sells, at the setup's access level */
    const MP = require("./master-permissions.js");
    if (applied.permission) { try { MP.revoke(applied.permission, null, actor); } catch (e) { /* revoked already */ } }
    const nodes = (v || []).map(x => M.uidOf(x)).filter(Boolean);
    const level = MP.levels().find(l => l.name === S().accessLevel) || fail("The setup's access level is not declared: " + S().accessLevel);
    applied.permission = nodes.length ? MP.grant({ holder: ns(tid), scope: nodes, actions: level.actions, objects: S().objects }, actor) : null;
    require("./store-taxonomy.js").sync(tid);
  }
};
function saveCommerce(tid, patch) {
  const st = require("./settings.js");
  st.save(tid, { commerce: { ...st.load(tid).commerce, ...patch } });
}
function applyDue(tid, actor) {
  M.ensure();
  const now = answers(tid);
  const r = C.resolve(setting(S().appliedAnswer), { namespaces: [ns(tid)] });
  const applied = { ...((r.resolved && r.from && r.from.namespace === ns(tid) && r.value.value) || { answers: {}, enabled: [], requested: [] }) };
  const changed = steps().filter(st => JSON.stringify(now[st.answer]) !== JSON.stringify(applied.answers[st.answer]));
  if (!changed.length) return { changed: [], ...applied };
  const caps = require("./capabilities.js");
  const D = require("./platform-discovery.js");
  return K.internal.tx(() => {
    for (const st of changed) if (EFFECTS[st.answer] && now[st.answer] != null) EFFECTS[st.answer](tid, now[st.answer], now, actor, applied);
    /* the capabilities follow from every answer together */
    const found = D.discover(now);
    const on = new Set(D.onAfter(found, now.declined || []));
    for (const key of on) if (!caps.on(Number(tid), key)) caps.enable(Number(tid), key);
    for (const key of applied.enabled || []) if (!on.has(key) && caps.on(Number(tid), key)) caps.disable(Number(tid), key);
    const next = { answers: now, enabled: [...on], requested: found.filter(f => !f.available).map(f => ({ key: f.key, reasons: f.reasons })),
      permission: applied.permission || null };
    declareSettings();
    C.assign(setting(S().appliedAnswer), { value: next }, { namespace: ns(tid) }, actor);
    return { changed: changed.map(s => s.answer), ...next, discovery: found };
  });
}
/* what discovery makes of a platform's answers now — the console's preview, and the owner's list
   of requests */
function state(tid) {
  const now = answers(tid);
  const r = C.resolve(setting(S().appliedAnswer), { namespaces: [ns(tid)] });
  return { answers: now, applied: (r.resolved && r.value.value) || null, discovery: require("./platform-discovery.js").discover(now), steps: describe() };
}
/* the platform owner edits a platform's requests afterwards (DEC-019): the requests are an answer */
function setRequests(tid, requests, actor) {
  return answer(tid, { requests: Array.isArray(requests) ? requests.map(String) : [] }, { partial: true }, actor);
}

/* every platform with answers on the kernel has what has come due applied (the server runs this
   once per resolution: a minute) */
function sweepAll(actor) {
  const prefix = R().storeNamespace + ":";
  const rows = require("./db.js").all("SELECT DISTINCT namespace FROM k_assignments WHERE setting LIKE ? AND namespace LIKE ? AND rec_to IS NULL", S().settingPrefix + "%", prefix + "%");
  let n = 0;
  for (const r of rows) { try { if (applyDue(Number(r.namespace.slice(prefix.length)), actor || "setup-sweep").changed.length) n++; } catch (e) { console.error("setup sweep " + r.namespace + ": " + e.message); } }
  return n;
}
const resolutionMs = () => S().resolutionMs;

/* the answers a starter package pre-fills: the kind's own starter answers, the jurisdiction and
   industries registration named, and the capabilities of the kind's starting blend as features the
   platform switched on — every one editable, none a gate */
function starterAnswers(kind, o) {
  const k = kind || {}, st = k.starter || {};
  const blend = k.archetype ? (require("./capabilities.js").presets().find(p => p.key === k.archetype) || {}).capabilities || {} : {};
  /* the jurisdiction's own currency and language (Value's and Expression's facts of the place) */
  const place = o && o.official ? require("./registry.js").country(o.official) : null;
  const E = require("./expression.js");
  return Object.fromEntries(Object.entries({
    official: o && o.official, sellingModel: st.sellingModel,
    languages: place && place.locale && E.language(place.locale) ? [E.base(place.locale)] : undefined,
    currencies: place && place.currency ? [place.currency] : undefined,
    offerings: [...new Set([...((o && o.industries) || []), ...(st.offerings || [])])],
    fulfilment: st.fulfilment, features: Object.keys(blend)
  }).filter(([, v]) => v != null && !(Array.isArray(v) && !v.length)));
}
/* what a platform is provisioned with, from its answers: a shopfront when it sells anything, and
   shipping and a warehouse when it delivers something physical (the fulfilment modes say which) */
function provisionFor(a) {
  const modes = M.vocabulary(R().fulfilmentModes);
  const off = require("./platform-discovery.js").resolveOfferings(a.offerings || []);
  /* the modes it chose, else every mode the kinds it sells can use */
  const possible = a.fulfilment && a.fulfilment.length ? a.fulfilment : off.kinds.flatMap(t => t.fulfilment || []);
  const physical = possible.some(m => (modes.find(x => x.name === m) || {}).physical) || (!possible.length && off.nodes.length > 0);
  const model = M.vocabulary(R().sellingModels).find(t => t.name === a.sellingModel) || {};
  return { payments: true, shipping: physical, warehouse: physical, storefront: (a.offerings || []).length > 0 && model.storefront !== false };
}

module.exports = { describe, options, check, answers, answer, applyDue, state, setRequests, sweepAll, resolutionMs, starterAnswers, provisionFor };
