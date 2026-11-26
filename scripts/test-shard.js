/* LUXORA Platform — the test suite in shards, for CI (owner Quality).

   The suite is the `npm test` chain in package.json, and nothing else: this splits that one list,
   so a test added to the chain is in a shard without anyone listing it twice. The syntax checks run
   in the first shard; the test files are spread across the shards by how long each took
   (scripts/test-times.json), longest first onto the lightest shard. Every command in a shard runs
   even after one fails, so one CI run reports every failure, not only the first.

     node scripts/test-shard.js 2/4        run shard 2 of 4
     node scripts/test-shard.js --list 4   show how 4 shards are made up
     node scripts/test-shard.js --times <file>   refresh the timings from "<exit> <secs>s <command>" lines */
"use strict";
const fs = require("fs"), path = require("path"), { spawnSync } = require("child_process");
const ROOT = path.join(__dirname, ".."), TIMES = path.join(__dirname, "test-times.json");

function chain() {
  const t = require(path.join(ROOT, "package.json")).scripts.test.replace(/^export LX_TEST=1 && /, "");
  return t.split(" && ").map(c => c.trim()).filter(Boolean);
}
const isCheck = c => /--check|size-guard/.test(c);
function shards(n) {
  const T = JSON.parse(fs.readFileSync(TIMES, "utf8")), secs = c => T.seconds[c] != null ? T.seconds[c] : T.default;
  const all = chain(), out = Array.from({ length: n }, () => ({ commands: [], seconds: 0 }));
  out[0].commands.push(...all.filter(isCheck));
  for (const c of all.filter(c => !isCheck(c)).sort((a, b) => secs(b) - secs(a) || a.localeCompare(b))) {
    const s = out.reduce((m, x) => (x.seconds < m.seconds ? x : m), out[0]);
    s.commands.push(c); s.seconds += secs(c);
  }
  /* every command of the chain is in exactly one shard */
  const placed = out.flatMap(s => s.commands);
  if (placed.length !== all.length || new Set(placed).size !== all.length) throw new Error("shards do not cover the suite once");
  return out;
}
function run(i, n) {
  const s = shards(n)[i - 1], failed = [];
  if (!s) throw new Error("No shard " + i + " of " + n);
  console.log(`shard ${i}/${n}: ${s.commands.length} commands, about ${Math.round(s.seconds / 60)} min`);
  for (const c of s.commands) {
    const t = Date.now();
    const r = spawnSync(c, { cwd: ROOT, shell: true, stdio: "inherit", env: { ...process.env, LX_TEST: "1" } });
    const took = Math.round((Date.now() - t) / 1000);
    if (r.status !== 0) failed.push(c);
    console.log(`${r.status === 0 ? "✓" : "✗"} ${c} (${took}s)`);
  }
  console.log(failed.length ? `\n✗ ${failed.length} failed in shard ${i}/${n}:\n  ` + failed.join("\n  ") : `\n✓ shard ${i}/${n} passed`);
  return failed.length ? 1 : 0;
}
if (require.main === module) {
  const a = process.argv.slice(2);
  if (a[0] === "--list") { shards(Number(a[1]) || 4).forEach((s, i) => console.log(`shard ${i + 1}: ${s.commands.length} commands, ~${s.seconds}s`)); }
  else if (a[0] === "--times") {
    const T = JSON.parse(fs.readFileSync(TIMES, "utf8"));
    for (const l of fs.readFileSync(a[1], "utf8").trim().split("\n")) { const m = /^\d+ (\d+)s (.+)$/.exec(l); if (m) T.seconds[m[2]] = Number(m[1]); }
    fs.writeFileSync(TIMES, JSON.stringify(T, null, 1) + "\n");
  } else {
    const m = /^(\d+)\/(\d+)$/.exec(a[0] || "");
    if (!m) { console.error("Usage: node scripts/test-shard.js <i>/<n>"); process.exit(2); }
    process.exit(run(Number(m[1]), Number(m[2])));
  }
}
module.exports = { chain, shards };
