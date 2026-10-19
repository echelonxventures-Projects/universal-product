/* The kernel, first slice (FOUNDATIONS K01–K04, K06–K08): kinds declared as data, nodes with
   universal IDs and any number of code schemes, hierarchies at any depth where one node sits in
   many places, typed and encrypted attributes, bi-temporal versions (valid time and recorded
   time; nothing overwritten) and one hash-chained event log. The test builds a place tree from
   a galaxy down to a single coordinate-sized site and a second, overlapping hierarchy, with no
   word of geography in the kernel itself. */
"use strict";
const path = require("path");
const fs = require("fs");
const os = require("os");
const TMP = path.join(os.tmpdir(), "kernel-" + process.pid + ".db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
process.env.LX_DB = TMP;
const silence = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = silence;
const K = require("../lib/kernel.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const throws = (fn, re, n) => { try { fn(); ok(false, n, "did not throw"); } catch (e) { ok(re.test(e.message), n, e.message); } };
const T = (y, m) => new Date(Date.UTC(y, (m || 1) - 1, 1)).toISOString();

console.log("kernel — kinds (K01) and attributes (K06)");
const place = K.defineKind({ kind: "place", owner: "Geo", label: "Place", parents: ["place", "market"], schemes: ["iso2", "iau"],
  attributes: [{ key: "name", type: "text", required: true }, { key: "population", type: "integer" }, { key: "secret_note", type: "text", sensitive: true }] }, "test");
ok(place && place.owner === "Geo" && place.attributes.length === 3, "a kind is declared as data with typed attributes");
throws(() => K.defineKind({ kind: "x", owner: "Nobody" }), /owning domain/, "a kind's owner must be a domain in the register");
throws(() => K.defineKind({ kind: "y", owner: "Geo", attributes: [{ key: "a", type: "colour" }] }), /Unknown value type/, "attribute types come from the declared value types");
throws(() => K.defineKind({ kind: "Bad Key", owner: "Geo" }), /must match/, "keys follow the declared pattern");
throws(() => K.defineKind({ kind: "z", owner: "Geo", attributes: [{ key: "a", type: "text" }, { key: "a", type: "text" }] }), /declared twice/, "an attribute is declared once");
K.defineKind({ kind: "market", owner: "Commerce", parents: ["market"], root: true, attributes: [{ key: "name", type: "text", required: true }] }, "test");
ok(K.kinds().map(k => k.kind).join(",") === "market,place", "kinds are listed per namespace");

console.log("kernel — nodes (K02) and identifiers (K04)");
const universe = K.createNode("place", { validFrom: T(1900), attributes: { name: "Observable universe" } }, "test");
const galaxy = K.createNode("place", { validFrom: T(1900), attributes: { name: "Milky Way" } }, "test");
const sol = K.createNode("place", { validFrom: T(1900), attributes: { name: "Solar System" } }, "test");
const earth = K.createNode("place", { validFrom: T(1900), attributes: { name: "Earth" }, identifiers: { iau: "399" } }, "test");
const asia = K.createNode("place", { validFrom: T(1900), attributes: { name: "Asia" } }, "test");
const ocean = K.createNode("place", { validFrom: T(1900), attributes: { name: "Indian Ocean" } }, "test");
const india = K.createNode("place", { validFrom: T(1947, 8), attributes: { name: "India", population: 361000000, secret_note: "sealed" }, identifiers: { iso2: "IN" } }, "test");
const site = K.createNode("place", { validFrom: T(2020), attributes: { name: "A single site" } }, "test");
ok(/^[0-9a-f-]{36}$/.test(india), "every node gets a universal ID");
ok(K.nodes("place").length === 8, "nodes of a kind are listed with no limit on count");
ok(K.resolveIdentifier("iso2", "IN") === india && K.resolveIdentifier("iau", "399") === earth, "a code in any declared scheme resolves to its node");
ok(K.identifiers(india).uid === india && K.identifiers(india).iso2 === "IN", "a node's identifiers include its universal ID");
throws(() => K.assignIdentifier(earth, "iso2", "IN"), /already names/, "one code names one node at a time");
throws(() => K.assignIdentifier(india, "zip", "1"), /declares no identifier scheme/, "schemes are declared by the kind");
throws(() => K.createNode("place", { attributes: {} }), /required/, "required attributes are enforced");
throws(() => K.createNode("place", { attributes: { name: 7 } }), /must be text/, "values are type-checked");
throws(() => K.createNode("place", { attributes: { name: "x", colour: "red" } }), /declares no attribute/, "only declared attributes are accepted");
K.endIdentifier(india, "iso2", "IN", T(2030));
ok(K.resolveIdentifier("iso2", "IN", { at: T(2031) }) === null && K.resolveIdentifier("iso2", "IN", { at: T(2029) }) === india, "an identifier has a time window");
K.assignIdentifier(earth, "iso2", "IN", { validFrom: T(2031) });
ok(K.resolveIdentifier("iso2", "IN", { at: T(2032) }) === earth, "a code freed in time may name another node afterwards");

console.log("kernel — attributes are encrypted at rest when sensitive (K06)");
const raw = db.get("SELECT attrs FROM k_versions WHERE node=? AND rec_to IS NULL", india).attrs;
ok(!raw.includes("sealed") && /lux\.v1\./.test(raw), "a sensitive value is stored sealed");
ok(K.attributes(india).secret_note === "sealed", "and read back in the clear by the kernel");

console.log("kernel — versions are bi-temporal (K07)");
const beforeChange = K.events({ limit: 500 }).slice(-1)[0].seq;
K.record(india, { population: 1400000000 }, { validFrom: T(2023) }, "test");
ok(K.attributes(india, { at: T(1990) }).population === 361000000, "the past is unchanged by a later fact");
ok(K.attributes(india, { at: T(2024) }).population === 1400000000, "the new fact holds from its valid time");
ok(K.attributes(india, { at: T(2024) }).name === "India", "a patch keeps the facts it does not touch");
ok(K.attributes(india, { at: T(2024), recorded: beforeChange }).population === 361000000, "what was believed before the change can still be asked");
K.record(india, { population: 900000000 }, { validFrom: T(2000), validTo: T(2010) }, "test");
ok(K.attributes(india, { at: T(2005) }).population === 900000000 && K.attributes(india, { at: T(2015) }).population === 361000000 && K.attributes(india, { at: T(2024) }).population === 1400000000,
  "a bounded correction changes only its own window");
ok(K.attributes(india, { at: T(1940) }) === null, "a node has no facts before it existed");
const hist = K.history(india);
ok(hist.length > 3 && hist.some(h => h.recordedTo != null), "superseded versions are kept, never overwritten");
K.record(india, { population: null }, { validFrom: T(2025) }, "test");
ok(!("population" in K.attributes(india, { at: T(2026) })) && K.attributes(india, { at: T(2024) }).population === 1400000000, "an attribute can be withdrawn from a point in time");
throws(() => K.record(india, { name: null }, { validFrom: T(2026) }), /required/, "a required attribute cannot be withdrawn");
throws(() => K.record(india, { population: 1 }, { validFrom: T(2026), validTo: T(2025) }), /after validFrom/, "a window must run forwards");

console.log("kernel — hierarchies at any depth, one node in many places (K03)");
K.defineHierarchy({ hierarchy: "physical", owner: "Geo", label: "Physical containment" }, "test");
K.defineHierarchy({ hierarchy: "markets", owner: "Commerce", label: "Markets" }, "test");
const P = (n, p, f) => K.place("physical", n, p, { validFrom: f || T(1900) }, "test");
P(universe, null); P(galaxy, universe); P(sol, galaxy); P(earth, sol); P(asia, earth); P(ocean, earth);
P(india, asia, T(1947, 8)); P(site, india, T(2020)); P(site, ocean, T(2020));
ok(K.children("physical", null).join() === universe, "the top of a hierarchy is whatever was placed there");
ok(K.ancestors("physical", site).length === 7, "a node's ancestors run all the way up through every place it sits");
ok(K.paths("physical", site).length === 2, "a node in two places has two paths");
ok(K.descendants("physical", universe).length === 7, "a subtree is found from any node, at any depth");
ok(K.descendants("physical", universe, { depth: 2 }).length === 2, "and can be limited by depth");
ok(K.parents("physical", india, { at: T(1940) }).length === 0, "placements have valid time");
throws(() => P(universe, site), /cycle/, "a placement may not make a cycle");
throws(() => P(asia, earth), /already sits there/, "the same placement is not recorded twice");
const mk = K.createNode("market", { validFrom: T(2020), attributes: { name: "South Asia market" } }, "test");
K.place("markets", mk, null, { validFrom: T(2020) }, "test");
K.place("markets", india, mk, { validFrom: T(2020) }, "test");
ok(K.children("markets", mk).join() === india && K.parents("physical", india).join() === asia, "hierarchies share nodes and do not see each other");
throws(() => K.place("physical", mk, earth), /may not sit under/, "a kind declares where it may sit");
K.endPlacement("physical", site, ocean, T(2025));
ok(K.paths("physical", site).length === 1 && K.paths("physical", site, { at: T(2024) }).length === 2, "ending a placement keeps its past");

console.log("kernel — one event log, hash-chained (K08)");
const log = K.events({ subject: india });
ok(log.length >= 5 && log.every(e => e.subject === india), "every change to a node is in the log");
ok(K.verifyEvents().ok, "the chain verifies");
const victim = K.events({ limit: 3 })[1];
db.run("UPDATE k_events SET payload=? WHERE seq=?", "{}", victim.seq);
const v = K.verifyEvents();
ok(!v.ok && v.brokenAt === victim.seq, "an edited event breaks the chain at that event");

console.log("kernel — shape: any coordinate system, any coordinate resolves to every node containing it (K05)");
const S = require("../lib/kernel-shape.js");
K.defineKind({ kind: "place", owner: "Geo", label: "Place", parents: ["place", "market"], schemes: ["iso2", "iau"], shape: true,
  attributes: [{ key: "name", type: "text", required: true }, { key: "population", type: "integer" }, { key: "secret_note", type: "text", sensitive: true }] }, "test");
S.defineSystem({ system: "geodetic", owner: "Geo", axes: [{ key: "lat", min: -90, max: 90 }, { key: "lon", min: -180, max: 180, wrap: true }] }, "test");
S.defineSystem({ system: "galactic", owner: "Geo", axes: [{ key: "x", unit: "ly" }, { key: "y", unit: "ly" }, { key: "z", unit: "ly" }] }, "test");
throws(() => S.defineSystem({ system: "bad", owner: "Geo", axes: [{ key: "a", wrap: true }] }), /needs both bounds/, "a wrapping axis is bounded");
S.setShape(india, "geodetic", { type: "box", min: [6, 68], max: [36, 98] }, { validFrom: T(1947, 8) }, "test");
S.setShape(asia, "geodetic", { type: "box", min: [-11, 25], max: [81, -170] }, { validFrom: T(1900) }, "test");
S.setShape(site, "geodetic", { type: "polygon", ring: [[28.60, 77.20], [28.60, 77.21], [28.61, 77.21], [28.61, 77.20]] }, { validFrom: T(2020) }, "test");
S.setShape(galaxy, "galactic", { type: "ball", center: [0, 0, 0], radius: 52850 }, { validFrom: T(1900) }, "test");
const here = S.containing("geodetic", [28.605, 77.205]).sort();
ok(here.length === 3 && [india, asia, site].every(u => here.includes(u)), "a coordinate resolves to the site, the country and the continent at once");
ok(S.containing("geodetic", [60, 179]).join() === asia && S.containing("geodetic", [60, -175]).join() === asia, "a box may cross a wrapping axis's seam");
ok(S.containing("geodetic", [0, 0]).length === 0, "a coordinate inside nothing resolves to nothing");
ok(S.containing("galactic", [26000, 0, 20]).join() === galaxy && S.containing("galactic", [90000, 0, 0]).length === 0, "the same works for a galaxy in light-years");
throws(() => S.containing("geodetic", [95, 0]), /outside/, "a coordinate is checked against its system's bounds");
throws(() => S.setShape(mk, "geodetic", { type: "point", at: [0, 0] }), /carries no shape/, "only a kind that carries a shape has one");
throws(() => S.setShape(india, "geodetic", { type: "box", min: [40, 0], max: [30, 1] }), /min is above max/, "a box runs forwards on an axis that does not wrap");
S.setShape(india, "geodetic", { type: "box", min: [8, 68], max: [37, 97] }, { validFrom: T(2040) }, "test");
ok(S.shapeOf(india, "geodetic", { at: T(2041) }).min[0] === 8 && S.shapeOf(india, "geodetic", { at: T(2030) }).min[0] === 6, "a shape has valid time; a new one does not erase the old");

console.log("kernel — scope and resolution: nearest wins, every answer says where it came from (K11, K12)");
const C = require("../lib/kernel-context.js");
C.declareSetting({ name: "display.system", owner: "Measure", type: "text" }, "test");
C.declareSetting({ name: "never.assigned", owner: "Measure", type: "text" }, "test");
C.assign("display.system", "everywhere", {}, "test");
C.assign("display.system", "india", { scope: india, validFrom: T(2000) }, "test");
C.assign("display.system", "ocean", { scope: ocean, validFrom: T(2000) }, "test");
C.assign("display.system", "acme-site", { scope: site, namespace: "tenant:acme" }, "test");
const r1 = C.resolve("display.system", { context: { physical: site }, namespaces: ["tenant:acme", "platform"] });
ok(r1.value === "acme-site" && r1.from.namespace === "tenant:acme" && r1.from.distance === 0, "a tenant's own assignment wins where it applies");
const r2 = C.resolve("display.system", { context: { physical: site } });
ok(r2.value === "india" && r2.from.node === india && r2.from.distance === 1 && !r2.ambiguous, "otherwise the nearest assignment up the hierarchy wins");
const r3 = C.resolve("display.system", { context: { physical: site }, at: T(2024) });
ok(r3.ambiguous && ["india", "ocean"].includes(r3.value), "a node in two places with different answers is reported as ambiguous");
const r4 = C.resolve("display.system", { context: { physical: galaxy } });
ok(r4.value === "everywhere" && r4.from.node === null, "with nothing nearer, the namespace-wide assignment answers");
const r5 = C.resolve("never.assigned", { context: { physical: site } });
ok(r5.resolved === false && r5.value === undefined && r5.tried.length > 0, "nothing assigned is unresolved — no value is invented");
C.assign("display.system", "india-later", { scope: india, validFrom: T(2030) }, "test");
ok(C.resolve("display.system", { context: { physical: india }, at: T(2031) }).value === "india-later" && C.resolve("display.system", { context: { physical: india }, at: T(2026) }).value === "india",
  "assignments have valid time");
throws(() => C.assign("display.system", 5, {}), /must be text/, "an assigned value has its declared type");
throws(() => C.assign("display.system", "x", { scope: "not-a-node" }), /must be a node/, "a scope is a node");
throws(() => C.assign("display.system", "x", { namespace: "galaxy:1" }), /Unknown namespace/, "a namespace has a declared type");
C.assign("display.system", "market", { scope: mk }, "test");
C.assign("display.system", "universe", { scope: universe }, "test");
C.defineResolution({ name: "markets-first", owner: "Context", order: ["markets", "physical"] }, "test");
C.defineResolution({ name: "physical-first", owner: "Context", order: ["physical", "markets"] }, "test");
ok(C.resolve("display.system", { context: { markets: mk, physical: galaxy }, profile: "markets-first" }).value === "market"
  && C.resolve("display.system", { context: { markets: mk, physical: galaxy }, profile: "physical-first" }).value === "universe",
  "a resolution profile orders the hierarchies");

console.log("kernel — views select by reference and are computed live (K10)");
C.defineView({ name: "asia", owner: "Perspective", selects: [{ hierarchy: "physical", root: asia }], labels: { [india]: "Bharat" } }, "test");
const va = C.viewNodes("asia");
ok(va.map(n => n.uid).sort().join() === [asia, india, site].sort().join() && va.find(n => n.uid === india).label === "Bharat", "a view selects a subtree and labels it");
C.defineView({ name: "earth-top", owner: "Perspective", selects: [{ hierarchy: "physical", root: earth, depth: 1, includeRoot: false }] }, "test");
ok(C.viewNodes("earth-top").map(n => n.uid).sort().join() === [asia, ocean].sort().join(), "a view limits depth");
C.defineView({ name: "markets", owner: "Perspective", selects: [{ hierarchy: "markets", root: null, kinds: ["market"] }] }, "test");
ok(C.viewNodes("markets").map(n => n.uid).join() === mk, "a view filters by kind");
const city = K.createNode("place", { attributes: { name: "A new city" } }, "test");
K.place("physical", city, india, {}, "test");
ok(C.viewNodes("asia").some(n => n.uid === city), "a node added to the master appears in the view with no change to the view");
ok(!JSON.stringify(db.all("SELECT spec FROM k_declarations WHERE family='view'")).includes(site), "a view stores references, not copies");

console.log("kernel — the change lifecycle: draft, validate, preview, approve, publish, schedule, roll back (K09)");
const LC = require("../lib/kernel-lifecycle.js");
const nodesBefore = db.get("SELECT COUNT(*) AS n FROM k_nodes").n;
const ch = LC.draft({ title: "Add a district", ops: [
  { op: "createNode", args: ["place", { attributes: { name: "A district" } }] },
  { op: "place", args: ["physical", "$0", city] },
  { op: "record", args: [india, { population: 1450000000 }, { validFrom: T(2026) }] },
  { op: "assign", args: ["display.system", "district", { scope: "$0" }] }
] }, "author");
ok(LC.change(ch).state === "draft", "a change starts as a draft of operations written as data");
throws(() => LC.draft({ ops: [{ op: "dropTable" }] }, "author"), /unknown operation/, "only declared operations can be drafted");
const rep = LC.validate(ch, "author");
ok(rep.ok && LC.change(ch).state === "validated", "a valid change validates");
ok(db.get("SELECT COUNT(*) AS n FROM k_nodes").n === nodesBefore, "validation is a dry run that leaves nothing behind");
const pv = LC.preview(ch, res => C.resolve("display.system", { context: { physical: res[0] } }).value);
ok(pv.ok && pv.result === "district" && db.get("SELECT COUNT(*) AS n FROM k_nodes").n === nodesBefore, "a preview answers questions about the result, then undoes it");
throws(() => LC.approve(ch, "reviewer"), /permission/, "approving needs the approve permission");
throws(() => LC.approve(ch, "author", ["kernel.approve"]), /someone other than its author/, "the author cannot approve their own change");
LC.approve(ch, "reviewer", ["kernel.approve"]);
const popBefore = K.attributes(india).population;
const pub = LC.publish(ch, {}, "reviewer");
const district = pub.result[0];
ok(pub.state === "published" && K.parents("physical", district).join() === city && K.attributes(india).population === 1450000000, "publishing applies every operation");
ok(pub.seqFrom > 0 && pub.seqTo >= pub.seqFrom, "a published change occupies a range of the event log");
LC.rollback(ch, "reviewer");
ok(LC.change(ch).state === "rolled-back", "a published change can be rolled back");
ok(K.attributes(india).population === popBefore && K.parents("physical", district).length === 0 && C.resolve("display.system", { context: { physical: district } }).value === "everywhere",
  "rolling back closes what it recorded and reopens what it superseded");
ok(K.attributes(india, { recorded: pub.seqTo }).population === 1450000000, "and what was believed while it was published can still be asked");
const bad = LC.draft({ ops: [{ op: "record", args: [india, { name: 42 }] }] }, "author");
const badRep = LC.validate(bad, "author");
ok(!badRep.ok && /must be text/.test(badRep.error) && LC.change(bad).state === "draft", "an invalid change reports why and stays a draft");
const sch = LC.draft({ ops: [{ op: "record", args: [asia, { population: 4800000000 }] }] }, "author");
LC.validate(sch, "author"); LC.approve(sch, "reviewer", ["kernel.approve"]);
ok(LC.publish(sch, { at: T(2099) }, "reviewer").state === "scheduled" && LC.publishDue(T(2098)).length === 0, "a change can be scheduled and waits for its time");
const due = LC.publishDue(T(2100), "scheduler");
ok(due.length === 1 && due[0].ok && K.attributes(asia).population === 4800000000, "and is published when it falls due");
const c1 = LC.draft({ ops: [{ op: "record", args: [asia, { population: 1 }] }] }, "author"); LC.validate(c1, "author"); LC.approve(c1, "reviewer", ["kernel.approve"]); LC.publish(c1, {}, "reviewer");
const c2 = LC.draft({ ops: [{ op: "record", args: [asia, { population: 2 }] }] }, "author"); LC.validate(c2, "author"); LC.approve(c2, "reviewer", ["kernel.approve"]); LC.publish(c2, {}, "reviewer");
throws(() => LC.rollback(c1, "reviewer"), /later change built on this one/, "a change a later one built on cannot be rolled back first");
LC.rollback(c2, "reviewer"); LC.rollback(c1, "reviewer");
ok(K.attributes(asia).population === 4800000000, "rolled back in reverse order, the earlier state returns");
throws(() => LC.edit(ch, [{ op: "createNode", args: ["place", {}] }]), /Only a draft/, "only a draft can be edited");

console.log("kernel — hide is reversible, delete is archive, purge needs its own permission (K09)");
const temp = K.createNode("place", { attributes: { name: "Temporary", secret_note: "x" }, identifiers: {} }, "test");
LC.hide(temp, "test"); ok(LC.nodeState(temp) === "hidden", "a node can be hidden");
LC.unhide(temp, "test"); ok(LC.nodeState(temp) === "active", "and shown again");
const hid = K.createNode("place", { attributes: { name: "Hidden town" } }, "test");
K.place("physical", hid, india, {}, "test");
S.setShape(hid, "geodetic", { type: "point", at: [20, 80] }, {}, "test");
const under = K.createNode("place", { attributes: { name: "Under the hidden town" } }, "test");
K.place("physical", under, hid, {}, "test");
LC.hide(hid, "test");
ok(!K.children("physical", india).includes(hid) && K.children("physical", india, { includeHidden: true }).includes(hid), "a hidden node drops out of listings, unless asked for");
ok(!C.viewNodes("asia").some(n => n.uid === hid) && C.viewNodes("asia").some(n => n.uid === under), "views leave it out; what sits under it stays");
ok(!S.containing("geodetic", [20, 80]).includes(hid) && !K.nodes("place").includes(hid), "coordinate lookups and node lists leave it out");
ok(K.ancestors("physical", under).includes(hid), "the structure itself is unchanged");
LC.unhide(hid, "test");
ok(K.children("physical", india).includes(hid), "unhiding brings it back");
throws(() => LC.purge(temp, ["kernel.purge"], "test"), /Only an archived node/, "only an archived node can be purged");
LC.archive(temp, "test");
throws(() => LC.purge(temp, [], "test"), /permission/, "purging needs the separate permission");
LC.purge(temp, ["kernel.purge"], "test");
ok(!db.get("SELECT 1 AS x FROM k_nodes WHERE uid=?", temp) && !db.get("SELECT 1 AS x FROM k_versions WHERE node=?", temp), "a purged node and its facts are gone");
ok(K.events({ subject: temp, type: "kernel.node.purged" }).length === 1, "leaving one tombstone event");
throws(() => { LC.archive(asia, "test"); LC.purge(asia, ["kernel.purge"], "test"); }, /still sit under/, "a node others sit under cannot be purged");

console.log("kernel — a failed write leaves nothing behind");
const count = db.get("SELECT COUNT(*) AS n FROM k_nodes").n, evs = db.get("SELECT COUNT(*) AS n FROM k_events").n;
throws(() => K.createNode("place", { attributes: { name: "Atlantis" }, identifiers: { iso2: "IN" }, validFrom: T(2032) }), /already names/, "a clashing identifier rejects the whole create");
ok(db.get("SELECT COUNT(*) AS n FROM k_nodes").n === count && db.get("SELECT COUNT(*) AS n FROM k_events").n === evs, "no node and no event survive the failed write");

for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
