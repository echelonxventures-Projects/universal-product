/* LUXORA Platform — the synchronous Postgres bridge pairs every reply with its request
   (lib/pgbridge.js). The worker runs in parallel, so its reply can land before the request thread
   reaches Atomics.wait; that reply is the answer, not an error (CI run 40476015559 failed four page
   loads with "reply arrived for a different request"). A reply carrying another request's id is
   refused — including an error reply, which must not surface as this request's error. Each case
   sets the shared memory exactly as the worker leaves it, so no timing is involved. */
"use strict";
const { awaitReply, DATA_BYTES } = require("../lib/pgbridge.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const throws = (fn, re, n) => { try { fn(); ok(false, n, "did not throw"); } catch (e) { ok(re.test(e.message), n, e.message); } };

/* the worker's reply(): payload at byte 4, its length in ctrl[1], ready flag ctrl[0] = 1 */
function memory() { return { ctrl: new Int32Array(new SharedArrayBuffer(16)), data: new SharedArrayBuffer(1024) }; }
function workerReplies(m, obj) {
  const json = Buffer.from(JSON.stringify(obj), "utf8");
  new DataView(m.data).setUint32(0, json.length, true);
  new Uint8Array(m.data).set(json, 4);
  Atomics.store(m.ctrl, 1, json.length);
  Atomics.store(m.ctrl, 0, 1);
}

console.log("pg bridge — a reply is paired by its id, not by the wait");
let m = memory();
workerReplies(m, { ok: true, rows: [[1]], columns: ["ok"], cmdTag: "SELECT 1", id: 7 });
let out = null; try { out = awaitReply(m.ctrl, m.data, 7, 50); } catch (e) { out = e.message; }
ok(out && out.rows && out.rows[0][0] === 1, "a reply stored before the wait began is returned (the wait answers not-equal)", out);

m = memory();
workerReplies(m, { ok: true, rows: [], columns: [], cmdTag: "", id: 6 });
throws(() => awaitReply(m.ctrl, m.data, 7, 50), /stale reply 6 for request 7/, "a reply to an earlier request is refused");

m = memory();
workerReplies(m, { error: "relation does not exist", id: 6 });
throws(() => awaitReply(m.ctrl, m.data, 7, 50), /stale reply/, "an earlier request's error is not raised as this request's error");

m = memory();
workerReplies(m, { error: "syntax error", id: 7 });
throws(() => awaitReply(m.ctrl, m.data, 7, 50), /^syntax error$/, "this request's own error is raised");

m = memory();
const t0 = Date.now();
throws(() => awaitReply(m.ctrl, m.data, 7, 40), /timeout after 40ms/, "no reply is a timeout");
ok(Date.now() - t0 >= 35, "and the wait lasted the timeout");

m = memory();
Atomics.store(m.ctrl, 0, -1);
throws(() => awaitReply(m.ctrl, m.data, 7, 50, () => new Error("worker crashed")), /worker crashed/, "a dead worker's error is raised");
ok(DATA_BYTES === 16 * 1024 * 1024, "the shared result buffer is 16 MB");

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
