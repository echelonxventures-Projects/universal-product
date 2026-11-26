/* The platform master as one surface: units of value on the kernel (lib/value-units.js), and the five
   parts of anything in the master, the records a platform keeps and what each console screen shows
   (lib/master-view.js). */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os");
const TMP = path.join(os.tmpdir(), "master-view-" + process.pid + ".db");
const wipe = () => { for (const s of ["", "-wal", "-shm"]) try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } };
wipe(); process.env.LX_DB = TMP; process.env.LUXORA_DEMO_BRANDS = "1";
const log = console.log; console.log = () => { };
const db = require("../lib/db.js"), reg = require("../lib/registry.js");
console.log = log;
const K = require("../lib/kernel.js"), V = require("../lib/value-units.js"), E = require("../lib/entity.js"), MV = require("../lib/master-view.js"), P = require("../lib/platform-setup.js"), M = require("../lib/platform-master.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + JSON.stringify(x) : ""))); };
const refused = fn => { try { fn(); return false; } catch (e) { return !!e.status; } };
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  console.log("▸ UNITS OF VALUE");
  const rows = db.all("SELECT code, uid FROM currencies");
  ok(rows.length > 0 && rows.every(r => V.uidOf(r.code) === r.uid), "every unit is an entity with its row's identity");
  const seq = K.verifyEvents().count; ok(V.importRows() === 0 && K.verifyEvents().count === seq, "a warm pass writes nothing");
  const own = db.all("SELECT id, name FROM tenants"), code = reg.country(require("../lib/settings.js").load(own[0].id).commerce.country).currency;
  const no = E.updateEntity(0, "currency", code, { active: false });
  ok(no.error && no.error.includes(own[0].name) && reg.currency(code).active === 1 && V.at(code).listed, "a unit a store trades in cannot be switched off, and says who", no);
  ok(!!E.deleteEntity(0, "currency", code).error && !!reg.currency(code), "nor deleted");
  ok(!require("../lib/global.js").updateCurrency(code, { active: false }).ok, "nor by the other writer");
  const free = rows.map(r => r.code).find(c => !V.usedBy(c).length && V.at(c).listed);
  ok(E.updateEntity(0, "currency", free, { active: false }).ok && !V.at(free).listed && !reg.currencies().some(c => c.code === free), "an unused one can: it is hidden everywhere");
  ok(!P.options("currencies").some(o => o.key === free), "and is no longer offered in setup");
  ok(E.updateEntity(0, "currency", free, { active: true }).ok && V.at(free).listed, "and switched on again");
  const before = V.at(free).rate, then = new Date().toISOString(); await sleep(20); V.setRate(free, 7.5);
  ok(V.at(free).rate === 7.5 && reg.currency(free).usd === 7.5 && V.at(free, { at: then }).rate === before, "a rate changes from now; the one before it stays answerable");
  const made = E.createEntity(0, "currency", { code: "SOLAR", name: "Solar", symbol: "S", decimals: 2, usd: 0, class: "utility", settleable: 1, active: 1 });
  ok(made.id === "SOLAR" && V.uidOf("SOLAR") && db.get("SELECT uid FROM currencies WHERE code='SOLAR'").uid === V.uidOf("SOLAR"), "a new unit is an entity first", made);
  E.updateEntity(0, "currency", "SOLAR", { class: "commodity" });
  ok(K.parents(V.HIERARCHY, V.uidOf("SOLAR"), { namespace: "platform" }).map(u => K.attributes(u).key).join() === "commodity", "its class is a relationship");
  ok(E.deleteEntity(0, "currency", "SOLAR").ok && !V.uidOf("SOLAR") && !reg.currency("SOLAR"), "a deleted one is archived");

  console.log("▸ ONE SURFACE");
  const u = MV.entity(V.uidOf(free));
  ok(u.registry.owner === "Value" && u.entity.attributes.symbol && u.temporal.versions.length > 1 && u.relationship.some(r => r.hierarchy === V.HIERARCHY) && Array.isArray(u.context), "an entity shows its five parts", Object.keys(u));
  ok(MV.entity(require("../lib/places.js").byCode(reg.countries()[0].code)).context.some(c => c.setting === "value.currency"), "a place shows the currency that applies there");
  ok(MV.list(V.KIND, { at: then }).rows.find(r => r.identifiers["value-unit"] === free).attributes.rate === before, "a list can be read as it stood at an instant");
  const bad = [];
  for (const [k, b] of Object.entries(MV.screens())) try {
    if (b.kind) MV.list(b.kind, b); else if (b.registry) MV.registry(b.registry); else if (b.vocabulary) M.vocabulary(b.vocabulary);
    else if (b.entity) { if (!E.ENTITY_DEFS && !require("../lib/seed/entity.json").ENTITY_DEFS[b.entity]) throw new Error("no entity"); } else if (!b.view && !b.planned) throw new Error("answers nothing");
  } catch (e) { bad.push(k + ": " + e.message); }
  ok(!bad.length, "every screen's binding answers", bad);
  const nav = fs.readFileSync(path.join(__dirname, "..", "public", "js", "platform.js"), "utf8"), leaves = require("../lib/consoles.js").declared("platform");
  const views = new Set([...nav.slice(nav.indexOf("const VIEWFNS")).matchAll(/^ {2}"?([\w-]+)"?: \(\) =>/gm)].map(m => m[1]));
  const lost = Object.entries(MV.screens()).filter(([k, b]) => !leaves.some(l => l.shows && l.shows.u === k) || (b.view && !views.has(b.view))).map(x => x[0]);
  ok(!lost.length, "every binding is of a screen the console has, to a view it has", lost);

  console.log("▸ RECORDS");
  const d = MV.create("party.organisation", { attributes: { name: "Acme" } }, { hierarchy: "party.roles", under: "vocab.party_roles.dealer" }, "t");
  ok(MV.list("party.organisation", { hierarchy: "party.roles", under: "vocab.party_roles.dealer" }).total === 1 && MV.list("party.organisation", { hierarchy: "party.roles", under: "vocab.party_roles.partner" }).total === 0, "an organisation is one entity, listed under the role it plays");
  MV.relate(d, { hierarchy: "party.roles", parent: "vocab.party_roles.partner" }, {}, "t");
  ok(MV.entity(d).relationship.find(r => r.hierarchy === "party.roles").above.length === 2, "and may play another, as the same entity");
  const soon = new Date(Date.now() + 86400000).toISOString(); MV.change(d, { attributes: { name: "Acme Two" }, from: soon }, {}, "t");
  ok(MV.entity(d).entity.title === "Acme" && MV.entity(d, { at: soon }).entity.title === "Acme Two", "a change can be made for later");
  ok(refused(() => MV.create("place", { attributes: { name: "x" } }, {}, "t")) && refused(() => MV.change(V.uidOf(free), { attributes: { name: "x" } }, {}, "t")) && refused(() => MV.declareKind({ kind: "place", owner: "Geo" }, "t")) && refused(() => MV.relate(d, { hierarchy: "place.tree", parent: d }, {}, "t")), "what has an owner is changed only by its owner");
  MV.declareKind({ kind: "clinic.ward", owner: "Party", label: "Ward", attributes: [{ key: "beds", type: "integer", constraints: { min: 1 } }] }, "t");
  ok(P.options("records").some(o => o.key === "clinic.ward"), "a kind declared as data is offered in setup");
  const [a, b] = own.map(t => t.id); ok(refused(() => MV.ownKind(a, "clinic.ward")), "a platform keeps only what its setup chose");
  P.answer(a, { records: ["clinic.ward"] }, { partial: true }, "t");
  const at = MV.ownKind(a, "clinic.ward"), w = MV.create("clinic.ward", { attributes: { name: "North", beds: 4 } }, at, "t");
  ok(MV.list("clinic.ward", at).total === 1 && MV.list("clinic.ward").total === 0, "its records are its own");
  ok(refused(() => MV.create("clinic.ward", { attributes: { name: "X", beds: 0 } }, at, "t")) && refused(() => MV.create("clinic.ward", { attributes: { beds: 2 } }, at, "t")), "held to the kind's rules");
  { P.answer(b, { records: ["clinic.ward"] }, { partial: true }, "t"); const other = MV.ownKind(b, "clinic.ward"); ok(MV.list("clinic.ward", other).total === 0 && refused(() => MV.change(w, { attributes: { beds: 9 } }, other, "t")) && refused(() => MV.setListed(w, false, other, "t")), "no other platform sees or changes them"); }
  ok(refused(() => MV.change(d, { attributes: { name: "x" } }, at, "t")), "nor can it change the master's");
  MV.setListed(w, false, at, "t"); ok(MV.list("clinic.ward", at).total === 0 && MV.entity(w).temporal.versions.length === 1, "a removed record keeps its history");
  ok(K.verifyEvents().ok, "the record of events is whole");
  console.log(`\n${passed} passed, ${failed} failed`); wipe(); process.exit(failed ? 1 : 0);
})().catch(e => { console.error(e); wipe(); process.exit(1); });
