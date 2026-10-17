/* UCOS Ω∞ · the single source of truth — integrity gate + seal, proven.
   --------------------------------------------------------------------------
   The mandate: everything the platform operates is declared by ONE compiled
   registry, with Zero Duplicate · Zero Partial · Zero Overlap · Zero Missing ·
   No Leakage — sealed and authenticated, auto-arranged, traceable, searchable.

   This proves it executably, in three parts:

     §A  the gate    — the five criteria over the compiled registry
     §B  the seal    — tamper is detected, drift is detected, recovery is a
                       re-compile from the sources (and strict mode refuses both)
     §C  the runtime — what the platform actually seeded EQUALS what the seal
                       declares; no second source is live

   Fast, no server, no port, own throwaway DB. */
"use strict";
const path = require("path");
const fs = require("fs");
const crypto = require("crypto");

const TMP = path.join(require("os").tmpdir(), "ssot-" + process.pid + ".db");
process.env.LX_DB = TMP;
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }

const silence = console.log; console.log = () => { };
const db = require(path.join(__dirname, "..", "lib", "db.js"));          /* boots through canonical */
const ucos = require(path.join(__dirname, "..", "lib", "ucos.js"));
const can = require(path.join(__dirname, "..", "lib", "canonical.js"));
const gate = require(path.join(__dirname, "..", "_registry", "gate.js"));
console.log = silence;

let passed = 0, failed = 0;
function ok(c, n, x) { if (c) { passed++; console.log("  ✓ " + n); } else { failed++; console.log("  ✗ " + n + (x ? " → " + x : "")); } }
const key = s => String(s || "").toLowerCase().replace(/[^a-z0-9]+/g, "_").slice(0, 120);

console.log("\n▸ §A THE GATE — the five criteria over the compiled registry");
{
  const payload = can.load();
  const report = gate.run(payload);
  console.log("  the gate checked " + report.checked + " properties (" + report.passed + " passed):");
  ok(report.ok, "the compiled registry passes all five criteria", report.fails.map(f => f.name).join("; "));
  for (const f of report.fails) ok(false, "  ✗ " + f.name, f.detail);
  ok(report.counts.universes === 2937, "the compiled registry declares the constitutional universes (2919 + the 18 contract artifacts)", report.counts.universes);
  ok(report.counts.concepts > 30000, "and the full concept layer", report.counts.concepts);
}

console.log("\n▸ §A1 THE REGISTER — one categorised owner for every declaration");
{
  const payload = can.load();
  const report = gate.run(payload);
  const rf = payload.registryFiles, reg = report.register;
  ok(reg && reg.categories >= 13 && reg.domains === rf.domains.domains.length, "the register reports its categories and domains", JSON.stringify(reg && { c: reg.categories, d: reg.domains }));
  ok(rf.primitives.primitives.every(p => !("owner" in p)) && rf.terminology.terms.every(t => !("ownerDomain" in t)),
    "ownership is declared once — primitives and terms carry no owner of their own");
  const hits = can.search("time", { limit: 3 });
  ok(hits[0] && hits[0].kind === "domain" && hits[0].name === "Time" && /^C04 /.test(hits[0].category), "search ranks the owning domain first, with its category", JSON.stringify(hits[0]));
  const c04 = can.search("e", { kind: "domain", category: "C04", limit: 50 });
  ok(c04.length > 0 && c04.every(h => h.kind === "domain" && /^C04 /.test(h.category)), "a category facet returns only that category's domains", c04.map(h => h.name).join(", "));
  const byOwner = can.search("a", { owner: "Security", limit: 50 });
  ok(byOwner.length > 0 && byOwner.every(h => h.owner === "Security"), "an owner facet returns only what that domain owns", byOwner.length + " hits");

  const twice = JSON.parse(JSON.stringify(payload));
  twice.registryFiles.domains.domains[1].owns.push(twice.registryFiles.domains.domains[0].owns[0]);
  const r1 = gate.run(twice);
  ok(r1.fails.some(f => /owned by at most one domain/.test(f.name)), "a name owned by two domains fails the gate");
  const loose = JSON.parse(JSON.stringify(payload));
  loose.registryFiles.domains.domains[0].category = "C99";
  loose.registryFiles.manifest.artifacts[0].owner = "Nobody";
  const r2 = gate.run(loose);
  ok(r2.fails.some(f => /declared category/.test(f.name)) && r2.fails.some(f => /owning domain/.test(f.name)), "an uncategorised domain and an unowned artifact fail the gate");
  const reserved = JSON.parse(JSON.stringify(payload));
  reserved.registryFiles.terminology.terms.push({ termId: "T-X", canonicalName: rf.primitives.prohibited[0], definition: "x" });
  reserved.registryFiles.domains.domains[0].owns.push(rf.primitives.prohibited[0]);
  ok(gate.run(reserved).fails.some(f => /reserves for projections/.test(f.name)), "a term named like a projection fails the gate");

  /* the law register, the kernel, the code map and the build path are gated too */
  ok(reg.laws >= 26 && reg.kernel >= 12 && reg.modules > 100, "the register reports laws, kernel parts and code modules", JSON.stringify({ l: reg.laws, k: reg.kernel, m: reg.modules }));
  const law = JSON.parse(JSON.stringify(payload));
  law.registryFiles.domains.laws[0].sources = [];
  law.registryFiles.domains.laws[1].sources = ["no-such-doc:1"];
  const r3 = gate.run(law);
  ok(r3.fails.some(f => /every law has a statement/.test(f.name)) && r3.fails.some(f => /law source/.test(f.name)), "a law without a source, or with a source that does not exist, fails the gate");
  const code = JSON.parse(JSON.stringify(payload));
  code.registryFiles.codebase.modules = code.registryFiles.codebase.modules.slice(1);
  code.registryFiles.codebase.modules.push({ path: "lib/no-such-file.js", owner: "Registry" });
  const r4 = gate.run(code);
  ok(r4.fails.some(f => /every code file has a home/.test(f.name)), "an unmapped code file, or a mapping to a file that does not exist, fails the gate");
  const step = JSON.parse(JSON.stringify(payload));
  step.registryFiles.roadmap.steps[0].deliveredBy = ["AMD-9999"];
  ok(gate.run(step).fails.some(f => /build step/.test(f.name)), "a done step naming an amendment that does not exist fails the gate");
  ok(can.search("fundamental axiom", { kind: "law" })[0]?.key === "LAW-001", "a law is found by any of its names (Fundamental Axiom → LAW-001)");
}

console.log("\n▸ §A2 THE GATE REFUSES A BROKEN COMPILE");
{
  /* a registry with a duplicate universe key and a dangling domain ownership must
     be refused — the gate is a gate, not a report */
  const payload = can.load();
  const broken = JSON.parse(JSON.stringify(payload));
  broken.universes.push({ ...broken.universes[0] });                     /* duplicate key */
  broken.registryFiles.domains.domains[0].owns.push("No_Such_Primitive_xyz");
  const r = gate.run(broken);
  ok(!r.ok, "a duplicate key and a dangling ownership fail the gate", r.fails.map(f => f.name).join("; "));
  ok(r.fails.some(f => /duplicate/i.test(f.name)), "the duplicate is reported as a duplicate");
  ok(r.fails.some(f => /ownership/i.test(f.name)), "the dangling reference is reported as missing");
}

console.log("\n▸ §B THE SEAL — tamper, drift and recovery");
{
  const good = fs.readFileSync(can.ENVELOPE, "utf8");
  const env = JSON.parse(good);

  /* B1: a byte-flipped payload must fail verification — on-disk tampering can
     never change what the platform operates undetected */
  const tampered = JSON.parse(good);
  tampered.payload = tampered.payload.slice(0, -8) + "AAAAAAAA";
  let e1 = null; try { can.open(tampered); } catch (e) { e1 = e; }
  ok(!!e1 && /signature invalid|auth tag|FAILED/i.test(e1.message), "a tampered payload is refused", e1 && e1.message);

  /* B2: a swapped-in manifest (stale-but-valid) must fail the signature too — the
     HMAC binds the manifest to the payload so drift cannot be hidden */
  const swapped = JSON.parse(good);
  const fake = JSON.parse(JSON.stringify(swapped.manifest));
  const anyKey = Object.keys(fake)[0];
  fake[anyKey].sha256 = "0".repeat(64);
  swapped.manifest = fake;
  let e2 = null; try { can.open(swapped); } catch (e) { e2 = e; }
  ok(!!e2 && /signature invalid/i.test(e2.message), "a swapped manifest fails the signature (drift cannot be hidden)", e2 && e2.message);

  /* B3: the verified path reports the real state */
  const v = can.verify();
  ok(v.ok === true, "the shipped seal verifies clean", v.error || JSON.stringify(v.drift));
  ok(!!v.digest && v.digest.length === 64, "the seal carries a 256-bit content digest");

  /* B4: drift is DETECTED — an edited input no longer matches the sealed manifest,
     which is the whole point of content-addressing the sources */
  const live = can.liveManifest();
  const sealed = env.manifest;
  const delta = can.manifestDelta(live, sealed);
  ok(delta.clean === true, "the sources match the sealed manifest on a clean tree", JSON.stringify(delta));
  const probe = path.join(__dirname, "..", "Architecture6.txt");
  const orig = fs.readFileSync(probe, "utf8");
  try {
    fs.writeFileSync(probe, orig + "\n<!-- gate probe: drift -->\n");
    const d2 = can.manifestDelta(can.liveManifest(), sealed);
    ok(d2.clean === false && d2.changed.length === 1, "an edited corpus is detected as drift", d2.changed.join(","));
  } finally { fs.writeFileSync(probe, orig); }
  ok(can.manifestDelta(can.liveManifest(), sealed).clean === true, "drift clears once the source is restored");

  /* B5: strict mode makes a drifted seal a hard stop instead of an auto-recovery */
  const savedStrict = process.env.LX_REGISTRY_STRICT;
  try {
    process.env.LX_REGISTRY_STRICT = "1";
    fs.writeFileSync(probe, orig + "\n<!-- gate probe: strict -->\n");
    let threw = false;
    try { can.load(true); } catch (e) { threw = /STRICT|drift/i.test(e.message); }
    ok(threw, "LX_REGISTRY_STRICT refuses a stale seal instead of re-compiling", threw ? "" : "no throw");
  } finally {
    process.env.LX_REGISTRY_STRICT = savedStrict;
    fs.writeFileSync(probe, orig);
    can.refresh();
  }
  /* the runtime recovers on its own once the source is restored */
  ok(!!can.load(), "the registry re-loads cleanly after recovery");
}

console.log("\n▸ §C THE RUNTIME — what booted IS the seal (no second source live)");
{
  const payload = can.load();
  const u = db.get("SELECT COUNT(*) n FROM ucos_universes").n;
  ok(u === payload.universes.length, "the live universe table equals the compiled registry", u + " vs " + payload.universes.length);
  const c = db.get("SELECT COUNT(*) n FROM ucos_concepts").n;
  ok(c === payload.counts.concepts, "the live concept table equals the compiled registry", c + " vs " + payload.counts.concepts);
  const d = db.get("SELECT COUNT(*) n FROM ucos_documents").n;
  ok(d === payload.counts.documents, "the live document table equals the compiled registry", d + " vs " + payload.counts.documents);

  /* provenance survives the compile: a universe still points at its document+line */
  const ins = payload.universes.find(x => x.key === "insurance");
  ok(!!ins && !!ins.sourceDoc && ins.sourceLine > 0, "a universe carries its document and line through the compile", ins && ins.sourceDoc + ":" + ins.sourceLine);
  ok(ins.sourceDoc === "upip" && ins.sourceLine > 0, "Insurance resolves first-wins to the earliest document that declares it", ins && ins.sourceDoc + ":" + ins.sourceLine);

  /* the vocabulary declarations the corpus owns are served from the compile */
  ok(ucos.productUniverses().length === payload.vocabularies.productUniverses.length, "the product-universe vocabulary comes from the compiled registry", ucos.productUniverses().length);
  ok(ucos.lifecycleStates().length === 7 && ucos.lifecycleStates().join(",") === payload.vocabularies.lifecycleStates.join(","), "the lifecycle comes from the compiled registry", ucos.lifecycleStates().join(","));
  ok(ucos.transitionGrammar().length === payload.vocabularies.transitionGrammar.length, "the transition grammar comes from the compiled registry");

  /* the console grant surface is derived from the navs, so it cannot drift.
     The store console redirects several nav leaves to one shared grant section
     (promotions + goip → offers, structure → tenancy, sso → settings) and its canSee()
     asks about the REDIRECTED key, so the surface must be the resolved sections. The
     surface is also closed under the entity router — privacy (consent / privacy_request)
     and compose (cp_* records) authorise against sections no nav leaf names. */
  const rb = require(path.join(__dirname, "..", "lib", "rbac.js"));
  const pb = require(path.join(__dirname, "..", "lib", "prbac.js"));
  const nav = can.consoleSec();
  const navSec = nav.adminNavSec || {};
  const resolved = [...new Set(nav.admin.map(k => navSec[k] || k))];
  ok(resolved.every(s => rb.SECTIONS.includes(s)), "the store grant surface covers every section the store nav requests", resolved.filter(s => !rb.SECTIONS.includes(s)).join(","));
  ok(rb.SECTIONS.every(s => resolved.includes(s) || s === "compose" || Object.values(rb.KEY_SECTION).includes(s)), "the store grant surface adds only router-reachable sections", rb.SECTIONS.filter(s => !resolved.includes(s) && s !== "compose" && !Object.values(rb.KEY_SECTION).includes(s)).join(","));
  ok(!!navSec.structure && navSec.structure === "tenancy", "the store nav's NAVSEC redirection is captured by the compile", JSON.stringify(navSec));
  ok(JSON.stringify(pb.SECTIONS) === JSON.stringify(nav.platform), "the platform grant surface is exactly the platform nav", pb.SECTIONS.length + " leaves");
  /* the owner's '*' expansion must light up every nav button: a surface of raw leaves
     hid Org Structure from the owner while a scoped manager (granted 'settings' by
     name) could still see it — the inverted-access symptom */
  const ownerAllowed = Object.keys(rb.expand({ "*": "write" }));
  ok(resolved.every(s => ownerAllowed.includes(s)), "the owner role's '*' grant reaches every section the nav requests", resolved.filter(s => !ownerAllowed.includes(s)).join(","));
  /* a section reached only through the entity router, never the nav, is still grantable
     and still resolves for a scoped role — the closure that keeps datasets authorisable */
  const support = rb.grant({ role: "admin", staff_role: "support" }, 1);
  ok(support["store:privacy"] === "write", "a router-only section (privacy) is grantable and resolves", JSON.stringify(Object.keys(support).sort()));
  /* every shipped role grants only real sections, so the console's role editor never
     shows a phantom checkbox that validateRole would reject the moment it is saved */
  for (const r of rb.ROLES) {
    const unknown = Object.keys(r.sections || {}).filter(k => k !== "*" && !rb.SECTIONS.includes(k));
    ok(!unknown.length, "the '" + r.key + "' role grants only real sections", unknown.join(","));
  }

  /* traceable + searchable: any declaration resolves with provenance */
  const hit = can.search("insurance", { limit: 5 });
  ok(hit.length > 0 && hit.every(h => h.provenance && h.kind), "the registry is searchable with provenance on every hit", hit.length + " hits");
}

console.log("\n" + (failed ? "✗ " + failed + " check(s) failed" : "✓ all single-source-of-truth checks passed") + "  (" + passed + " passed)");
process.exit(failed ? 1 : 0);
