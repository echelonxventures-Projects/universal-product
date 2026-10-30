/* LUXORA Platform — the white-label guard.
   The platform is one master configured into any kind of commerce platform; it never names
   another company's platform — not in code, comments, docs, tests, seed data, registries or
   file names. Platform TYPES are described instead (general marketplace, quick commerce, B2B
   wholesale, payments-led super app, omnichannel retail, ride-hailing…).

   The guard cannot spell the names it forbids, so it holds only the first 16 hex digits of
   the SHA-256 of each lowercase name. Text is split into words (letters and digits); a word
   whose hash is on the list is a hit. To add a name, append its hash:
     node -e 'console.log(require("crypto").createHash("sha256").update("<name>").digest("hex").slice(0,16))'

   Usage: node scripts/white-label.js     scans every tracked file and file name; exits 1 on a hit */
"use strict";
const crypto = require("crypto");

const DENY = new Set(["000305c8f8d99edb", "047364b9be67f665", "09a2f4897466c7a5", "13ed070478ef62c3", "22ffba7a86ea9919", "24e6654bfd1ab85b", "2b1da9c840074a35", "2b78da3dc866654e", "2fc9fff8ab7f35aa", "34a533dfd7273a9b", "3ccbd9105a45d8fc", "40bd434c398a1eac", "4a3892e5bc960fe4", "4e44ddffb6dae607", "4e8c67d62118bf11", "504fda550dee86c6", "55a9f4f8994b1bbf", "56089dd0e1dfd48e", "5815755fc6efaccd", "583e17796e6a79e5", "5849f0dbde1a6968", "5ba14c9c0738b2e6", "6362a966d9f2a89d", "6bd81f7f06c17fb8", "74096f8f5513e45d", "743598aceb5d73b9", "74c860f63661b29c", "7a9c94a8c201bcc2", "8894283570d18338", "8a72266588ef612e", "8c0b0fb70efd5854", "943c3eeb252dbd17", "961281ce5eace239", "9782b0ba6c878626", "98932ea98ae9ca65", "999e524f02e0c1ac", "9b7e0298a58b592e", "a9aa319f40ddff4a", "ab7d0a36ecbe10c2", "b0126946c556dc47", "b095d3503eeae9c4", "b1bf8a88d292a1bb", "b48c9328a66ad7a5", "b5738c169b693bee", "ba94f3933307554e", "c138de7be42f7ed2", "c1e84f7c3e4f76b9", "cbc62794911ff31b", "d515d8e80615e3ba", "d7d794a32759e3e6", "dfbf85cc71c7dd60", "e5f2f4ada0333086", "eda2dfe8c9351786", "f0293172d6013983", "f9dc1bb6b2d8a86e", "fa1127852ed8507e"]);

const hashOf = w => crypto.createHash("sha256").update(w).digest("hex").slice(0, 16);
const memo = new Map();
const denied = w => { if (!memo.has(w)) memo.set(w, DENY.has(hashOf(w))); return memo.get(w); };
/* every denied word in a text, with its line number */
function hits(text) {
  const out = [];
  String(text == null ? "" : text).split("\n").forEach((line, i) => {
    for (const m of line.matchAll(/[A-Za-z0-9]+/g)) if (denied(m[0].toLowerCase())) out.push({ line: i + 1, word: m[0] });
  });
  return out;
}
const clean = text => hits(text).length === 0;

/* the repository: every tracked (or new, not ignored) file's name and text */
function scan(root) {
  const fs = require("fs"), path = require("path");
  const { execFileSync } = require("child_process");
  const files = execFileSync("git", ["ls-files", "--cached", "--others", "--exclude-standard", "-z"], { cwd: root, encoding: "utf8", maxBuffer: 64 << 20 }).split("\0").filter(Boolean);
  const out = [];
  for (const f of files) {
    for (const h of hits(f)) out.push({ file: f, line: 0, word: h.word, where: "file name" });
    let buf; try { buf = fs.readFileSync(path.join(root, f)); } catch (e) { continue; }
    if (buf.includes(0)) continue;   /* binary */
    for (const h of hits(buf.toString("utf8"))) out.push({ file: f, line: h.line, word: h.word });
  }
  return out;
}

module.exports = { hits, clean, scan };

if (require.main === module) {
  const found = scan(require("path").join(__dirname, ".."));
  for (const h of found.slice(0, 200)) console.log(`  ${h.file}:${h.line}  ${h.word}`);
  console.log(found.length ? `✗ ${found.length} platform name(s) found` : "✓ no platform names in the repository");
  process.exit(found.length ? 1 : 0);
}
