/* UCOS Ω∞ · the master document and its volumes stay current by themselves.
   The registry projects one master (UCOS-MASTER.md) and one or more volumes per register
   category. A category whose volume would pass manifest.json → projection.maxVolumeBytes
   splits into numbered parts; when it shrinks, the parts merge back. This proves:
     - the files on disk are exactly a fresh projection of the registry, so a registry edit
       that was not re-projected (or a hand edit to a document) fails the build;
     - no stray volume exists that the projection would not produce;
     - lowering the limit adds volumes, raising it merges them, and no volume holding more
       than one artifact passes the limit;
     - the master's volume register lists every volume;
     - the constitutional audit (laws, completeness, links) passes. */
"use strict";
const path = require("path");
const fs = require("fs");
const { execFileSync } = require("child_process");
const ROOT = path.join(__dirname, "..");
const proj = require(path.join(ROOT, "_registry", "project.js"));

let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };

try {
  console.log("▸ THE DOCUMENTS ARE A FRESH PROJECTION OF THE REGISTRY");
  const { files, volumes } = proj.build();
  const stale = Object.entries(files).filter(([rel, text]) => { try { return fs.readFileSync(path.join(ROOT, rel), "utf8") !== text; } catch (e) { return true; } }).map(([rel]) => rel);
  ok(!stale.length, "the master and every volume match the registry (run npm run registry after a registry change)", stale);
  const onDisk = fs.readdirSync(path.join(ROOT, proj.VOLUME_DIR)).map(f => proj.VOLUME_DIR + "/" + f);
  const stray = onDisk.filter(f => !files[f]);
  ok(!stray.length, "no volume exists that the projection does not produce", stray);
  const register = files[proj.MASTER_FILE];
  ok(volumes.every(v => register.includes(`](${proj.VOLUME_DIR}/${v.file})`)), "the master's volume register lists every volume (" + volumes.length + ")");

  console.log("▸ VOLUMES SPLIT AND MERGE BY THEMSELVES");
  const entries = t => (t.match(/\n#### /g) || []).length;
  const within = (fs_, max) => Object.entries(fs_).filter(([rel]) => rel.startsWith(proj.VOLUME_DIR + "/")).every(([, t]) => Buffer.byteLength(t) <= max || entries(t) <= 1);
  const small = proj.build({ maxVolumeBytes: 40 * 1024 });
  ok(small.volumes.length > volumes.length, "a lower limit generates more volumes: " + volumes.length + " → " + small.volumes.length);
  ok(within(small.files, 40 * 1024), "no volume holding more than one artifact passes the lower limit");
  ok(small.volumes.filter(v => v.of > 1).every(v => /^V\d+\.\d+$/.test(v.id)), "split volumes are numbered parts (V11.1, V11.2, …)");
  const big = proj.build({ maxVolumeBytes: 1e12 });
  const cats = require(path.join(ROOT, "_registry", "domains.json")).categories;
  ok(big.volumes.length === cats.length && big.volumes.every(v => v.of === 1), "a higher limit merges them back: one volume per category (" + cats.length + ")");
  const anchorsAt = r => new Map(r.volumes.map(v => [v.file, (r.files[proj.VOLUME_DIR + "/" + v.file].match(/<a id="/g) || []).length]));
  const total = r => [...anchorsAt(r).values()].reduce((a, b) => a + b, 0);
  ok(total(small) === total(big) && total(big) === total({ volumes, files }), "splitting moves entries between parts and never drops or repeats one");

  console.log("▸ THE CONSTITUTIONAL AUDIT");
  let out = "", code = 0;
  try { out = execFileSync(process.execPath, [path.join(ROOT, "_registry", "audit.js")], { encoding: "utf8" }); } catch (e) { code = e.status; out = String(e.stdout || ""); }
  ok(code === 0, "laws, completeness and every link pass the audit", out.split("\n").filter(l => /✗/.test(l)).slice(0, 5).join(" | "));
} catch (e) { failed++; console.log("  ✗ threw: " + (e && e.stack || e)); }
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
