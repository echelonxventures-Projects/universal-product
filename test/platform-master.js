/* The platform master (GLOBAL_MASTER.md, P27): every product and service described once on the
   kernel — kinds that extend kinds, a trade taxonomy and a tariff nomenclature over the same
   nodes, identifier schemes that check their codes, attribute definitions inherited down the
   taxonomy and applicable by place, relationships as hierarchies, units that convert, and every
   vocabulary as nodes. Nothing here names an industry in code: the test reads them from the seed. */
"use strict";
const path = require("path");
const fs = require("fs");
const os = require("os");
const TMP = path.join(os.tmpdir(), "pmaster-" + process.pid + ".db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
process.env.LX_DB = TMP;
const silence = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = silence;
const K = require("../lib/kernel.js");
const M = require("../lib/platform-master.js");
const SEED = require("../lib/seed/master.json");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const throws = (fn, re, n) => { try { fn(); ok(false, n, "did not throw"); } catch (e) { ok(re.test(e.message), n, e.message); } };
const count = xs => xs.reduce((n, x) => n + 1 + count(x.children || []), 0);

console.log("platform master — the starter content");
const t0 = Date.now();
M.ensure();
const c = M.counts();
const universes = require("../lib/canonical.js").vocab("productUniverses");
ok(c.classification === count(SEED.taxonomy) + count(SEED.tariff) + universes.length, "every taxonomy and tariff node of the seed, and every product universe the constitution declares, is on the kernel", c);
ok(c.attributes === SEED.attributes.length && c.schemes === SEED.schemes.length && c.units === SEED.units.length, "every attribute definition, identifier scheme and unit too", c);
ok(c.vocabularies === SEED.vocabularies.length && c.terms === SEED.vocabularies.reduce((n, v) => n + v.terms.length, 0), "and every vocabulary with its terms", c);
console.log("    (" + (Date.now() - t0) + " ms for " + K.events({ limit: 1 }).length + "+ events)");
const before = db.get("SELECT COUNT(*) AS n FROM k_events").n;
require("../lib/platform-master.js").ensure();
ok(db.get("SELECT COUNT(*) AS n FROM k_events").n === before, "a second pass writes nothing");

console.log("platform master — the trade taxonomy");
const top = M.children(null);
ok(top.length === SEED.taxonomy.length && top[0].key === SEED.taxonomy[0].key, "the top of the taxonomy is the seed's domains, in order");
const ind = SEED.taxonomy[1].children[0];          /* an industry of the second domain */
const industry = M.node(ind.key, { lang: "en" });
ok(industry.kind === ind.kind && industry.attributes.title === ind.title.en, "an industry is a node of its kind, its title answered in a language");
ok(JSON.stringify(industry.attributes.requires || []) === JSON.stringify(ind.requires || []), "it carries the capabilities its kind of business requires");
const cat = ind.children[0], sub = cat.children[0];
ok(M.paths(sub.key)[0].join(">") === [SEED.taxonomy[1].key, ind.key, cat.key, sub.key].join(">"), "a subcategory's path runs from its domain");
ok(M.tree(ind.key, { depth: 2 }).length === ind.children.length && M.tree(ind.key, { depth: 2 })[0].children.length === cat.children.length, "a subtree reads to a depth");
throws(() => K.place(M.TRADE, M.uidOf(ind.key), M.uidOf(sub.key), { namespace: M.NAMESPACE }), /may not sit under|cycle/, "levels sit only where their kind allows");

console.log("platform master — the tariff nomenclature over the same kernel");
const ch = SEED.tariff[0].children[0];
const chapter = M.node(ch.key);
ok(chapter.identifiers.hs_code === ch.codes.hs_code, "a tariff chapter carries its code under its scheme");
ok(K.resolveIdentifier("hs_code", ch.codes.hs_code) === chapter.uid, "and is found by it");

console.log("platform master — identifier schemes check their codes");
const kinds = M.vocabulary("vocab.item_kinds");
const physical = kinds.find(k => k.fulfilment && k.fulfilment.includes(SEED.vocabularies.find(v => v.key === SEED.projections.fulfilmentModes.key).terms[0].name));
const at = [sub.key];
const item = M.createItem({ kind: physical.kind, at, title: { en: "Sample item" }, identifiers: { gtin: "4006381333931" } }, "test");
ok(M.node(item).identifiers.gtin === "4006381333931", "a valid code is accepted");
throws(() => M.createItem({ kind: physical.kind, at, title: { en: "Bad code" }, identifiers: { gtin: "4006381333932" } }), /check digit/, "a code that fails its scheme's check digit is refused");
throws(() => M.createItem({ kind: physical.kind, at, title: { en: "Bad code" }, identifiers: { imei: "12345" } }), /not a valid imei/, "a code that breaks its scheme's format is refused");
throws(() => K.assignIdentifier(item, "isbn", "0306406153"), /check digit/, "an ISBN-10 with a wrong check digit is refused");
throws(() => K.assignIdentifier(item, "cas", "7732-18-4"), /check digit/, "so is a CAS number with a wrong check digit");

console.log("platform master — attribute definitions are inherited down the taxonomy");
const bound = SEED.attributes.find(a => a.at.length && a.at.some(k => k.split(".").length === 1));
const boundTo = bound.at.find(k => k.split(".").length === 1);
const node0 = (function find(xs) { for (const x of xs) { if (x.key === boundTo) return x; const f = find(x.children || []); if (f) return f; } return null; })(SEED.taxonomy);
const deep = node0.children[0].children[0].key;
const setDeep = M.attributeSet({ kind: physical.kind, at: [deep] }).map(d => d.name);
ok(setDeep.includes(bound.name), "a definition bound to an industry applies to items deep under it", bound.name);
const elsewhere = (function find(xs) { for (const x of xs) { if (x.kind === sub.kind && !x.key.startsWith(boundTo + ".")) return x; const f = find(x.children || []); if (f) return f; } return null; })(SEED.taxonomy.slice().reverse());
ok(!M.attributeSet({ kind: physical.kind, at: [elsewhere.key] }).map(d => d.name).includes(bound.name), "and not to items elsewhere");
const everywhere = SEED.attributes.find(a => !a.at.length && !a.forKinds.length);
ok(setDeep.includes(everywhere.name), "a definition bound nowhere applies everywhere");
const forKind = SEED.attributes.find(a => !a.at.length && a.forKinds.length);
const serviceKind = kinds.find(k => !forKind.forKinds.some(f => K.isA(k.kind, f)));
ok(setDeep.includes(forKind.name) !== M.attributeSet({ kind: serviceKind.kind, at: [deep] }).map(d => d.name).includes(forKind.name), "a definition bound to a kind applies to that kind and its sub-kinds only");

console.log("platform master — facts are checked against the attribute set");
const oneOf = SEED.attributes.find(a => a.constraints && a.constraints.oneOf && a.at.length);
const oneOfAt = (function find(xs) { for (const x of xs) { if (oneOf.at.includes(x.key)) return x.children && x.children[0] ? (x.children[0].children && x.children[0].children[0] ? x.children[0].children[0] : x.children[0]) : x; const f = find(x.children || []); if (f) return f; } return null; })(SEED.taxonomy);
const good = M.createItem({ kind: physical.kind, at: [oneOfAt.key], title: { en: "Checked item" }, facts: { [oneOf.name]: oneOf.constraints.oneOf[0] } }, "test");
ok(M.node(good).attributes.facts[oneOf.name] === oneOf.constraints.oneOf[0], "a fact inside its rules is recorded");
throws(() => M.setFacts(good, { [oneOf.name]: "not-a-choice" }), /breaks the rule/, "a fact outside its rules is refused");
throws(() => M.setFacts(good, { not_declared_anywhere: 1 }), /No attribute/, "a fact no definition declares is refused");
const qty = SEED.attributes.find(a => a.type === "quantity" && a.unitDimension && !a.at.length && (!a.forKinds.length || a.forKinds.some(f => K.isA(physical.kind, f))));
const wrongDim = SEED.units.find(u => u.dimension !== qty.unitDimension), rightDim = SEED.units.find(u => u.dimension === qty.unitDimension);
throws(() => M.setFacts(good, { [qty.name]: { amount: 1, unit: M.unit(wrongDim.key) } }), /unit of its dimension/, "a quantity in a unit of another dimension is refused");
M.setFacts(good, { [qty.name]: { amount: 2, unit: M.unit(rightDim.key) } });
ok(M.node(good).attributes.facts[qty.name].amount === 2 && M.node(good).attributes.facts[oneOf.name], "facts merge over what the item has");

console.log("platform master — units convert");
const g = M.unit("g"), kg = M.unit("kg"), c_ = M.unit("c"), f_ = M.unit("f");
ok(Math.abs(M.convert({ amount: 1500, unit: g }, "kg").amount - 1.5) < 1e-9, "1500 g is 1.5 kg");
ok(Math.abs(M.convert({ amount: 100, unit: c_ }, "f").amount - 212) < 1e-6, "100 °C is 212 °F");
throws(() => M.convert({ amount: 1, unit: kg }, "m"), /different things/, "units of different dimensions do not convert");

console.log("platform master — relationships are hierarchies of their own");
const rel = SEED.relations[0].key;
const acc = M.createItem({ kind: physical.kind, at, title: { en: "An accessory" } }, "test");
M.relate(rel, acc, item, {}, "test");
ok(M.related(acc, rel).some(n => n.uid === item) && M.related(item, rel, { inward: true }).some(n => n.uid === acc), "a relationship reads both ways");
throws(() => M.relate("not_a_relation", acc, item), /Unknown relationship/, "relationships come from the declared list");

console.log("platform master — product universes");
ok(universes.every(u => M.universeNode(u.key)), "each declared universe is a classification node");
ok(universes.every(u => M.kindForUniverse(u.key).kind), "each sells as an item kind, read from the kinds vocabulary");
ok(M.kindForUniverse("a_universe_declared_later").unmappedUniverses === true, "a universe no kind names sells as the kind marked for it");
const inU = M.createItem({ kind: M.kindForUniverse(universes[1].key).kind, universe: universes[1].key, title: { en: "In a universe" }, lifecycle: "active" }, "test");
ok(M.universeOf(inU) === universes[1].key && M.node(inU).attributes.lifecycle === M.lifecycleTerm("active").name, "an item sits in a universe; an older status maps to its lifecycle term");
M.move(inU, { at: [sub.key], universe: universes[2].key }, "test");
ok(M.universeOf(inU) === universes[2].key && M.paths(inU)[0].slice(-2)[0] === sub.key, "moving an item ends old placements and adds new ones");
throws(() => M.update(inU, { lifecycle: "nonsense" }), /Unknown lifecycle/, "lifecycle states come from the vocabulary");

console.log("platform master — vocabularies are nodes");
const fm = SEED.vocabularies.find(v => v.key === SEED.projections.fulfilmentModes.key);
ok(M.vocabulary(fm.key).map(t => t.name).join() === fm.terms.map(t => t.name).join(), "a vocabulary's terms read in order, with their data");
ok(M.vocabulary(fm.key).every(t => Array.isArray(t.requires)), "each fulfilment mode states the capabilities it needs");
ok(M.items({ under: sub.key }).length >= 2, "items are listed under any taxonomy node");

for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
