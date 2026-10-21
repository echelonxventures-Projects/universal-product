/* LUXORA Platform — discovery: the capabilities a platform needs, derived from what it answered at
   setup (GLOBAL_MASTER.md §4, roadmap P29; owner Package).

   Nothing here knows a kind of business. Every requirement is declared where it belongs, as data
   of the platform master:
     · a taxonomy node (an industry, a category, …) names what selling under it requires and
       recommends — and what it says holds for everything under it;
     · an item kind names what selling it requires and recommends, and its fulfilment modes name
       theirs (an appointment needs bookings; a video call needs bookings and media sessions);
     · a selling model names its own (a marketplace needs seller health);
     · a jurisdiction's rule names what selling certain kinds or nodes there requires.
   Discovery reads them for the answers given and classes every capability:
     mandatory   — something chosen requires it; it cannot be switched off while the cause remains
     recommended — something chosen recommends it; on unless switched off
     added       — switched on by the platform's own choice, with no cause
     requested   — named (as a requirement, a recommendation or a request) but no capability atom
                   provides it yet: it goes to the platform owner as a request
   Each comes with the reasons it was derived — what was chosen and what it declared. */
"use strict";

const K = require("./kernel.js");
const M = require("./platform-master.js");
const fail = (msg, status) => { const e = new Error(msg); e.status = status || 400; throw e; };
const R = () => M.ROLES;
const lang = () => require("./expression.js").SEED.sourceLanguage;
const title = t => K.text(t, lang());

/* what the platform sells, resolved: taxonomy nodes (with everything above them, whose
   declarations hold below) and item kinds (with the kinds they extend) */
function resolveOfferings(offerings) {
  const kindTerms = M.vocabulary(R().itemKinds);
  const nodes = [], kinds = [];
  for (const o of offerings || []) {
    const term = kindTerms.find(t => t.name === o || t.kind === o);
    if (term) { kinds.push(term); continue; }
    const uid = M.uidOf(o) || fail("Not in the platform master: " + o);
    nodes.push(uid);
  }
  const lineage = new Set(nodes.flatMap(u => [u, ...K.ancestors(M.TRADE, u, { namespace: M.NAMESPACE })]));
  return { nodes, lineage: [...lineage], kinds };
}
/* is a place one of these, or inside one */
const within = (places, rulePlaces) => !rulePlaces || !rulePlaces.length || places.some(p => M.placeWithin(p, rulePlaces));
const placeOf = r => (r && typeof r === "object" ? K.resolveIdentifier(r.scheme, r.value) : M.uidOf(r) || r);

/* what each class's declared test asks of a capability's findings */
const TESTS = { requires: e => e.requires.length > 0, recommends: e => e.recommends.length > 0, added: e => e.added, requested: () => true };
function discover(answers) {
  const a = answers || {};
  const off = resolveOfferings(a.offerings);
  const out = new Map();
  const note = (key, cls, reason) => {
    if (!key) return;
    if (!out.has(key)) out.set(key, { key, requires: [], recommends: [], added: false, requested: false });
    const e = out.get(key);
    if (cls === "requires") e.requires.push(reason); else if (cls === "recommends") e.recommends.push(reason); else if (cls === "added") e.added = true; else e.requested = true;
  };
  const declare = (src, why) => { for (const k of src.requires || []) note(k, "requires", why); for (const k of src.recommends || []) note(k, "recommends", why); };
  /* the taxonomy: every chosen node and everything above it */
  for (const u of off.lineage) {
    const at = K.attributes(u) || {};
    declare(at, "you sell " + title(at.title));
  }
  /* item kinds and their fulfilment modes: a mode the platform chose requires what it requires; a
     mode its kinds can use but it did not choose only recommends it */
  const modes = M.vocabulary(R().fulfilmentModes);
  const chosenModes = new Set(a.fulfilment || []);
  for (const m of chosenModes) if (!modes.some(x => x.name === m)) fail("Unknown fulfilment mode: " + m);
  for (const t of off.kinds) {
    declare(t, "you sell " + title(t.title).toLowerCase());
    for (const m of t.fulfilment || []) {
      const mt = modes.find(x => x.name === m);
      if (!mt) continue;
      const why = title(t.title).toLowerCase() + " can be delivered by " + title(mt.title).toLowerCase();
      if (chosenModes.has(m)) declare(mt, title(t.title).toLowerCase() + " is delivered by " + title(mt.title).toLowerCase());
      else declare({ recommends: [...(mt.requires || []), ...(mt.recommends || [])] }, why);
    }
  }
  /* the selling model */
  if (a.sellingModel) {
    const sm = M.vocabulary(R().sellingModels).find(t => t.name === a.sellingModel) || fail("Unknown selling model: " + a.sellingModel);
    declare(sm, "you sell as a " + title(sm.title).toLowerCase());
  }
  /* the jurisdictions' rules, where they apply to what is sold */
  const places = [a.official, ...(a.working || [])].filter(Boolean).map(placeOf).filter(Boolean);
  const chosenKinds = new Set(off.kinds.flatMap(t => K.kindOf(t.kind, M.NAMESPACE).lineage));
  const chosenNodes = new Set(off.lineage.map(M.keyOf));
  for (const rule of M.vocabulary(R().authorityRules)) {
    const applies = (rule.forKinds || []).some(k => chosenKinds.has(k)) || (rule.forNodes || []).some(k => chosenNodes.has(k));
    if (applies && within(places, rule.places)) for (const k of rule.requires || []) note(k, "requires", "the law where you trade: " + title(rule.title).toLowerCase());
  }
  for (const k of a.features || []) note(k, "added", "you chose it");
  for (const k of a.requests || []) note(k, "requested", "you asked for it");
  /* class each; a capability no atom provides is requested whatever named it */
  const known = new Set(require("./capabilities.js").catalog().map(c => c.key));
  const CLASS = M.vocabulary(R().discoveryClasses);
  /* the classes in their declared order: the first whose test holds is the capability's class */
  const classOf = e => (CLASS.find(c => TESTS[c.test] && TESTS[c.test](e)) || {}).name;
  const requestedClass = (CLASS.find(c => c.unavailable) || {}).name;
  return [...out.values()].map(e => ({ key: e.key, class: known.has(e.key) ? classOf(e) : requestedClass, available: known.has(e.key),
    reasons: [...new Set([...e.requires, ...e.recommends, ...(e.added ? ["you chose it"] : []), ...(e.requested ? ["you asked for it"] : [])])] }))
    .sort((x, y) => CLASS.findIndex(c => c.name === x.class) - CLASS.findIndex(c => c.name === y.class) || x.key.localeCompare(y.key));
}
/* the capabilities that are on after discovery: mandatory, recommended unless switched off, added */
function onAfter(found, switchedOff) {
  const off = new Set(switchedOff || []);
  const CLASS = M.vocabulary(R().discoveryClasses);
  return found.filter(f => f.available && (CLASS.find(c => c.name === f.class) || {}).on && !(off.has(f.key) && (CLASS.find(c => c.name === f.class) || {}).optional)).map(f => f.key);
}

module.exports = { discover, onAfter, resolveOfferings };
