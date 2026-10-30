/* LUXORA Platform — the platform is white-label: no other company's platform is named
   anywhere in the repository — code, comments, docs, tests, seed data, registries or file
   names. Platform types are described instead. The names are held only as hashes
   (scripts/white-label.js), so this guard never spells what it forbids. */
"use strict";
const path = require("path");
const w = require("../scripts/white-label.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + JSON.stringify(x) : ""))); };

console.log("▸ NO PLATFORM IS NAMED");
const found = w.scan(path.join(__dirname, ".."));
ok(!found.length, "no tracked or new file, and no file name, names another platform", found.slice(0, 20).map(h => h.file + ":" + h.line));
console.log("▸ THE GUARD WORKS WITHOUT SPELLING THE NAMES");
ok(w.clean("a general marketplace, quick commerce and a payments-led super app"), "platform types pass");
const probe = Buffer.from("cmlkZSBoYWlsaW5nIGFzIHRoZSB1YmVyIG9mIHRoaW5ncw==", "base64").toString();
ok(!w.clean(probe) && w.hits(probe)[0].line === 1, "a name in running text is caught, whatever its case");
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
