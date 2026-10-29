/* LUXORA Platform — technology governance, from the command line (PR-053).

     node scripts/technology.js lock            regenerate technology.lock.json
     node scripts/technology.js inventory       regenerate TECHNOLOGY_INVENTORY.generated.md
     node scripts/technology.js check           the gate: the lock and the inventory are what the
                                                registry and the code give now; CI, the Dockerfile
                                                and package.json agree with the lock; every
                                                technology assumption in the code is declared and
                                                none is a violation. Exit 1 on any error
     node scripts/technology.js status          what is declared, discovered, a candidate,
                                                compatible, verified, approved and resolved —
                                                kept apart, never one list
     node scripts/technology.js proposals       what moved: evaluation lanes, upgrades, security,
                                                deprecation, end of life
     node scripts/technology.js discover <source> [--fetch] [--write] [--versions a,b]
                                                read a declared source (offline: its snapshot;
                                                --fetch: the source's declared https location),
                                                ingest it into a scratch registry and report what
                                                is new, refused and proposed. --write replaces that
                                                source's snapshot in lib/seed/technology-discovered.json;
                                                nothing else is ever written by discovery
     node scripts/technology.js verify-runtime <release>
                                                in a CI lane: the running runtime is the release the
                                                lock resolved (reads the lock only; no database)

   Everything but verify-runtime boots the kernel on a throwaway database: the registry is built
   from the declaration, the snapshots and package-lock.json every time, so the lock is a function
   of committed files and nothing else. */
"use strict";
const fs = require("fs");
const path = require("path");
const os = require("os");

const ROOT = path.join(__dirname, "..");
const SEED = require(path.join(ROOT, "lib", "seed", "technology.json"));
const LOCK = path.join(ROOT, SEED.lock);
const INVENTORY = path.join(ROOT, SEED.inventoryFile);
const [cmd, ...rest] = process.argv.slice(2);
const flag = k => rest.includes(k);
const opt = k => { const i = rest.indexOf(k); return i >= 0 ? rest[i + 1] : null; };

/* ---------- verify-runtime needs nothing but the lock ---------- */
if (cmd === "verify-runtime") {
  const key = rest[0];
  const lock = JSON.parse(fs.readFileSync(LOCK, "utf8"));
  const lane = (lock.ci.test || []).find(l => l.release === key);
  if (!lane) { console.error(`✗ ${key} is not a lane technology.lock.json resolves`); process.exit(1); }
  const running = process.versions.node;
  if (running !== lane.version) { console.error(`✗ the lane resolves ${lane.release}; this runtime is ${running}`); process.exit(1); }
  console.log(`✓ runtime ${running} is ${lane.release}${lane.evaluation ? " (evaluation lane)" : ""}${lane.primary ? " (primary: the production image's runtime)" : ""}`);
  process.exit(0);
}

/* ---------- the rest builds the registry on a throwaway database ---------- */
const TMP = path.join(os.tmpdir(), "technology-" + process.pid + ".db");
const clean = () => { for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } } };
clean();
process.env.LX_DB = TMP;
const quiet = console.log; console.log = () => { };
require(path.join(ROOT, "lib", "db.js"));
console.log = quiet;
const T = require(path.join(ROOT, "lib", "technology.js"));
const S = require(path.join(ROOT, "lib", "technology-scan.js"));
const done = code => { clean(); process.exit(code); };

function inventoryText() {
  const findings = S.scan(ROOT, SEED);
  return { findings, result: S.gate(findings, SEED), text: S.markdown(findings, SEED, S.gate(findings, SEED)) };
}

async function main() {
  if (cmd === "lock") { T.ensure(); fs.writeFileSync(LOCK, T.lockText()); console.log("written " + SEED.lock); return done(0); }
  if (cmd === "inventory") { fs.writeFileSync(INVENTORY, inventoryText().text); console.log("written " + SEED.inventoryFile); return done(0); }

  if (cmd === "check") {
    let errors = 0;
    const ok = (c, msg, detail) => { if (c) console.log("  ✓ " + msg); else { errors++; console.log("  ✗ " + msg); for (const d of [].concat(detail || [])) console.log("      " + d); } };
    console.log("▸ THE LOCK IS WHAT THE REGISTRY RESOLVES");
    T.ensure();
    const want = T.lockText(), have = fs.existsSync(LOCK) ? fs.readFileSync(LOCK, "utf8") : null;
    ok(have === want, SEED.lock + " is current", have == null ? "missing — node scripts/technology.js lock" : "drifted — the declaration, a snapshot or package-lock.json changed; node scripts/technology.js lock, then review the diff");
    const lock = JSON.parse(want);
    console.log("▸ WHAT CANNOT READ THE LOCK AGREES WITH IT");
    const cons = S.consumers(ROOT, lock, SEED);
    ok(!cons.length, "the CI workflow, the Dockerfile and package.json", cons);
    console.log("▸ EVERY RESOLVED RELEASE IS VERIFIED FOR ITS USE");
    for (const [use, r] of Object.entries(lock.resolutions)) ok(r.releases.length && r.releases.every(x => x.verified), `${use}: ${r.releases.map(x => x.key).join(", ") || "nothing resolved"}`, r.releases.filter(x => !x.verified).map(x => x.key + " is not verified"));
    ok(!lock.libraries.runtimeUnfit.length, `the ${lock.libraries.runtime} runtime libraries pass integrity, licence and contract`, lock.libraries.runtimeUnfit.map(x => x.key + ": " + x.failing.join(", ")));
    console.log("▸ EVERY TECHNOLOGY ASSUMPTION IN THE CODE IS DECLARED");
    const inv = inventoryText();
    ok(!inv.result.errors.length, `${inv.result.findings} findings, ${SEED.inventory.length} inventory entries`, inv.result.errors);
    const invHave = fs.existsSync(INVENTORY) ? fs.readFileSync(INVENTORY, "utf8") : null;
    ok(invHave === inv.text, SEED.inventoryFile + " is current", "node scripts/technology.js inventory");
    console.log("▸ REPORTED, NOT FAILED");
    const gaps = [...new Set(inv.result.gaps.map(g => g.id))];
    console.log(`  · unverified assumptions (gaps): ${gaps.join(", ") || "none"}`);
    if (lock.libraries.developmentUnfit.length) console.log(`  · ${lock.libraries.developmentUnfit.length} development libraries are not compatible as locked (no integrity hash in package-lock.json, or a contract check); they are not shipped`);
    for (const p of T.proposals()) console.log(`  · ${p.kind}: ${p.use} ${p.release} — ${p.detail}`);
    console.log(`\n${errors ? errors + " failed" : "technology gate passed"}`);
    return done(errors ? 1 : 0);
  }

  if (cmd === "status") {
    T.ensure();
    const rel = T.releases();
    const count = st => rel.filter(r => r.state === st).length;
    console.log("DECLARED (lib/seed/technology.json)");
    console.log(`  categories ${T.categories().map(c => c.key).join(", ")}`);
    console.log(`  items ${T.items().length}; sources ${SEED.sources.map(s => s.key + " [" + s.protocol + ", " + s.trust + "]").join(", ")}`);
    console.log("DISCOVERED AND EVALUATED (no state below approved is permission to use)");
    for (const s of SEED.states.list) console.log(`  ${s.key.padEnd(17)} ${String(count(s.key)).padStart(4)}  ${s.governed ? "governed" : "automatic"}`);
    console.log("COMPATIBILITY AND SECURITY, PER USE");
    const laneItems = new Set(SEED.uses.filter(u => u.evaluate).map(u => u.item));
    for (const r of rel.filter(x => x.evaluation && laneItems.has(x.item) && ["compatible", "verified", "approved", "active", "deprecated"].includes(x.state)))
      for (const u of r.evaluation.uses) console.log(`  ${r.key.padEnd(16)} ${u.use.padEnd(10)} compatible ${u.compatible ? "yes" : "no "}  verified ${u.verified ? "yes" : "no "}  ${[...u.warnings, ...u.advisory.map(a => a.check)].join("; ")}`);
    console.log("RESOLVED (governed resolutions; production marks what the deployed image runs)");
    for (const r of T.resolutions()) { const u = SEED.uses.find(x => x.key === r.use); console.log(`  ${r.use.padEnd(17)} ${u.production ? "production" : "ci        "} ${r.releases.map(x => x.key).join(", ")}`); }
    console.log("EVALUATION CANDIDATES (lanes that earn evidence; not approved)");
    for (const l of T.lanes("ci.test")) console.log(`  ${l.key} (${l.state})`);
    const rj = T.rejections(20);
    console.log(`REFUSED BY DISCOVERY (held with reasons in the kernel event log): ${rj.length}`);
    for (const r of rj.slice(0, 10)) console.log(`  ${r.source} ${r.entry}: ${r.reason}`);
    return done(0);
  }

  if (cmd === "proposals") { T.ensure(); for (const p of T.proposals()) console.log(`${p.kind.padEnd(12)} ${p.use.padEnd(17)} ${p.release.padEnd(20)} ${p.detail}`); return done(0); }

  if (cmd === "discover") {
    const key = rest[0];
    const src = SEED.sources.find(s => s.key === key);
    if (!src) { console.error("Unknown source " + key + "; declared: " + SEED.sources.map(s => s.key).join(", ")); return done(2); }
    T.ensure();
    const AD = require(path.join(ROOT, "lib", "technology-adapters.js"));
    let snap;
    if (flag("--fetch")) {
      const ad = AD.adapter(src.protocol);
      if (!ad.fetch) { console.error(`The ${src.protocol} adapter cannot fetch; its snapshot is maintained by hand from an observation`); return done(2); }
      const got = await ad.fetch(src, { versions: (opt("--versions") || "").split(",").filter(Boolean) });
      let entries = got.payload;
      let selection = "the whole payload";
      if (src.protocol === "release-index") {
        /* the lines the item declares support for, from the runtime floor on */
        const it = T.item(src.item), lines = Object.keys(it.lines || {}).map(Number), floor = T.floors()["platform.runtime"].floor;
        const n = v => String(v).replace(/^v/, "").split(".").map(Number);
        const ge = (a, b) => { for (let i = 0; i < 3; i++) if (a[i] !== b[i]) return a[i] > b[i]; return true; };
        entries = entries.filter(r => { const v = n(r.version); return v[0] >= Math.min(...lines) && v[0] <= Math.max(...lines) && ge(v, n(floor)); })
          .map(r => ({ version: r.version.replace(/^v/, ""), date: r.date, lts: r.lts, security: r.security, npm: r.npm, modules: r.modules, files: r.files }));
        selection = `the releases of lines ${Math.min(...lines)} to ${Math.max(...lines)} from ${floor} on; fields version, date, lts, security, npm, modules, files`;
      }
      snap = { source: src.key, fetchedAt: got.fetchedAt, location: got.location, payloadSha256: got.payloadSha256, selection, entries };
    } else {
      snap = JSON.parse(fs.readFileSync(path.join(ROOT, SEED.snapshots), "utf8")).snapshots.find(s => s.source === key);
      if (!snap) { console.error("No snapshot of " + key + "; use --fetch"); return done(2); }
    }
    const before = new Set(T.releases().map(r => r.key));
    const out = T.ingest(key, snap);
    T.evaluateAll();
    const fresh = out.accepted.filter(k => !before.has(k));
    console.log(`${key}: ${out.accepted.length} accepted (${fresh.length} new), ${out.unchanged.length} unchanged, ${out.rejected.length} refused`);
    for (const k of fresh) { const r = T.release(k); console.log(`  new ${k}: ${r.state}`); }
    for (const r of out.rejected) console.log(`  refused ${r.entry}: ${r.reason}`);
    for (const p of T.proposals()) console.log(`  proposal ${p.kind}: ${p.use} ${p.release} — ${p.detail}`);
    if (flag("--write") && flag("--fetch")) {
      const file = path.join(ROOT, SEED.snapshots), doc = JSON.parse(fs.readFileSync(file, "utf8"));
      doc.snapshots = doc.snapshots.filter(s => s.source !== key).concat([snap]).sort((a, b) => SEED.sources.findIndex(s => s.key === a.source) - SEED.sources.findIndex(s => s.key === b.source));
      fs.writeFileSync(file, JSON.stringify(doc, null, 2) + "\n");
      console.log(`written ${SEED.snapshots}; regenerate the lock (node scripts/technology.js lock) and review the diff`);
    }
    return done(0);
  }

  console.error("usage: node scripts/technology.js lock | inventory | check | status | proposals | discover <source> [--fetch] [--write] [--versions a,b] | verify-runtime <release>");
  return done(2);
}
main().catch(e => { console.error(e.stack || e.message); done(1); });
