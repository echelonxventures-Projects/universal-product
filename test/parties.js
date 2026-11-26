/* People on the kernel (lib/parties.js): every account is a person of the master, whose identity
   changes keep their history, whose role is a relationship, whose email is sealed — and who is
   purged without trace when they ask to be forgotten. */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os");
const TMP = path.join(os.tmpdir(), "parties-" + process.pid + ".db");
const wipe = () => { for (const s of ["", "-wal", "-shm"]) try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } };
wipe(); process.env.LX_DB = TMP; process.env.LUXORA_DEMO_BRANDS = "1";
const log = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = log;
const K = require("../lib/kernel.js"), P = require("../lib/parties.js"), E = require("../lib/entity.js"), C = require("../lib/compliance.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + JSON.stringify(x).slice(0, 300) : ""))); };
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  console.log("▸ EVERY ACCOUNT IS A PERSON");
  const users = db.all("SELECT id, uid, tenant_id, role FROM users");
  ok(users.length > 1 && users.every(u => K.internal.nodeRow(u.uid) && K.internal.nodeRow(u.uid).kind === "party.person"), "every account is a person with its own identity", users.length);
  ok(users.every(u => K.internal.nodeRow(u.uid).namespace === "tenant:" + u.tenant_id), "in its store's namespace");
  const seq = K.lastSeq(); ok(P.importRows() === 0 && K.lastSeq() === seq, "a warm pass writes nothing");
  const admin = users.find(u => u.role === "admin"), shopper = users.find(u => u.role === "customer");
  ok(P.at(admin.id).roles.includes("vocab.party_roles.staff") && P.at(shopper.id).roles.includes("vocab.party_roles.customer"), "the role a person plays is a relationship");
  const id = db.newUser(1, "Asha Rao", "asha@example.com", "Strong-Pass-1", "customer"), uid = db.get("SELECT uid FROM users WHERE id=?", id).uid;
  ok(P.at(id) && P.at(id).name === "Asha Rao" && P.at(id).email === "asha@example.com", "a new account is a person at once");
  ok(!db.all("SELECT attrs FROM k_versions WHERE node=?", uid).some(r => r.attrs.includes("asha@example.com")), "the email is sealed on the kernel, never stored plain");

  console.log("▸ WHO THEY ARE, OVER TIME");
  const then = new Date().toISOString(); await sleep(15);
  P.set(id, { name: "Asha R. Kapoor", email: "asha.k@example.com" }, "test");
  ok(db.get("SELECT name, email FROM users WHERE id=?", id).name === "Asha R. Kapoor" && P.at(id).email === "asha.k@example.com", "a change is the kernel's and the row's");
  ok(P.at(id, { at: then }).name === "Asha Rao", "who they were before stays answerable");
  P.set(id, { role: "admin", staff_role: "support" }, "test");
  ok(P.at(id).roles.join() === "vocab.party_roles.staff" && P.at(id).staff_role === "support" && db.get("SELECT role FROM users WHERE id=?", id).role === "admin", "a new role moves the relationship");
  P.set(id, { disabled: 1 }, "test"); ok(P.at(id).disabled === true && db.get("SELECT disabled d FROM users WHERE id=?", id).d === 1, "disabling is recorded");
  P.set(id, { hash: "nope" }, "test"); ok(db.get("SELECT hash FROM users WHERE id=?", id).hash !== "nope", "credentials are not the person's: set() does not touch them");
  const c = db.newUser(1, "Data Studio", "ds@example.com", "Strong-Pass-1", "customer");
  E.updateEntity(1, "customer", c, { name: "Edited In Studio" });
  ok(P.at(c).name === "Edited In Studio", "an edit in Data Studio reaches the person");

  console.log("▸ REMOVED, AND FORGOTTEN");
  const r = db.newUser(1, "Gone Soon", "gone@example.com", "Strong-Pass-1", "customer"), ruid = db.get("SELECT uid FROM users WHERE id=?", r).uid;
  P.remove(r, "test");
  ok(!db.get("SELECT id FROM users WHERE id=?", r) && require("../lib/kernel-lifecycle.js").nodeState(ruid) === "archived" && K.history(ruid).length > 0, "a deleted account's person is archived, its history kept");
  const f = db.newUser(1, "Forget Me", "forget@example.com", "Strong-Pass-1", "customer"), fuid = db.get("SELECT uid FROM users WHERE id=?", f).uid;
  P.set(f, { name: "Forget Me Please" }, "test");
  const out = C.eraseSubject(1, "forget@example.com", "test");
  ok(out.removed.some(x => x.startsWith("person:")) && !db.get("SELECT id FROM users WHERE id=?", f), "erasure removes the person and the account", out);
  ok(!K.internal.nodeRow(fuid) && db.get("SELECT COUNT(*) n FROM k_versions WHERE node=?", fuid).n === 0 && db.get("SELECT COUNT(*) n FROM k_placements WHERE node=?", fuid).n === 0, "no version of who they were remains");
  ok(!db.all("SELECT payload FROM k_events").some(e => /Forget Me|forget@example/.test(e.payload)), "and the event log never held their name or email");
  ok(K.verifyEvents().ok, "the record of events is whole");
  console.log(`\n${passed} passed, ${failed} failed`); wipe(); process.exit(failed ? 1 : 0);
})().catch(e => { console.error(e); wipe(); process.exit(1); });
