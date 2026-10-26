/* Health records (lib/health-records.js): the shopper's own vault — private records, shared with a
   party for some days and taken back, every share recorded. Capability: health_records. */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os");
const TMP = path.join(os.tmpdir(), "health-records-" + process.pid + ".db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
process.env.LX_DB = TMP;
const silence = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = silence;
const HR = require("../lib/health-records.js");
const caps = require("../lib/capabilities.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const throws = (fn, re, n) => { try { fn(); ok(false, n, "did not throw"); } catch (e) { ok(re.test(e.message), n, e.message); } };
const T = 1, who = "shopper:test", other = "shopper:other", party = "practitioner:7";

console.log("health records — off, the vault is closed");
throws(() => HR.vault(T, who), /not available/, "a store with the capability off keeps no records");

console.log("health records — keeping");
caps.enable(T, "health_records", { vault_limit: 2, max_share_days: 10 });
throws(() => HR.keep(T, who, { title: "Scan", url: "not a link" }), /link/, "a record is a link to a file");
throws(() => HR.keep(T, who, { url: "https://example.com/a.pdf" }), /Name/, "and is named");
const r1 = HR.keep(T, who, { title: "Blood test", url: "https://example.com/a.pdf" });
HR.keep(T, who, { title: "Scan", url: "https://example.com/b.pdf" });
throws(() => HR.keep(T, who, { title: "Third", url: "https://example.com/c.pdf" }), /full/, "no more than the vault_limit");
ok(HR.vault(T, who).records.length === 2 && HR.vault(T, other).records.length === 0, "a vault is its owner's alone");

console.log("health records — sharing");
throws(() => HR.share(T, other, { what: "record", ref: r1.id, party }), /Not in your vault/, "only the owner shares a record");
throws(() => HR.share(T, who, { what: "record", ref: r1.id }), /who/, "a share names who may see it");
const sh = HR.share(T, who, { what: "record", ref: r1.id, party, days: 99 });
const days = (new Date(sh.until.replace(" ", "T") + "Z") - Date.now()) / 86400000;
ok(days > 9 && days <= 10, "a share lasts no longer than max_share_days", sh.until);
const seen = HR.sharedWith(T, party);
ok(seen.length === 1 && seen[0].item.url.endsWith("a.pdf"), "the party sees what is shared with it");
ok(HR.sharedWith(T, "practitioner:8").length === 0, "and no other party does");
HR.unshare(T, who, sh.id);
ok(HR.sharedWith(T, party).length === 0, "taken back, it is no longer seen");
ok(HR.vault(T, who).shares.length === 1, "and the share stays recorded");
throws(() => HR.unshare(T, other, sh.id), /Not your share/, "only the owner takes a share back");

for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
