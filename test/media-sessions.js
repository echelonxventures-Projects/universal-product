/* Live sessions (lib/media-sessions.js): a booked consultation held by audio or video — carried by
   the platform itself (only the handshake relayed) or by a media connector — and charged by the
   minute where metered. */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os");
const TMP = path.join(os.tmpdir(), "msess-" + process.pid + ".db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
process.env.LX_DB = TMP;
const silence = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = silence;
const MS = require("../lib/media-sessions.js");
const caps = require("../lib/capabilities.js");
const offers = require("../lib/offers.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const throws = (fn, re, n) => { try { fn(); ok(false, n, "did not throw"); } catch (e) { ok(re.test(e.message), n, e.message); } };
const T = 1, guest = { owner: "shopper:guest" }, staff = { owner: "staff:1", staff: true }, stranger = { owner: "shopper:other" };
const p = db.get("SELECT * FROM products WHERE tenant_id=? AND lifecycle='published' LIMIT 1", T);
const book = () => db.run("INSERT INTO bookings(tenant_id,ref,product_id,resource_id,owner,starts_at,ends_at,status) VALUES(?,?,?,?,?,?,?,?)", T, "BK-" + Math.random().toString(36).slice(2, 8), p.id, 1, guest.owner, "2030-01-01 10:00", "2030-01-01 11:00", "confirmed").lastInsertRowid;

console.log("live sessions — a store with the capability holds them");
throws(() => MS.forBooking(T, book(), guest), /not available/, "with the capability off, no session");
caps.enable(T, "media_sessions");
const b1 = book();
const s1 = MS.forBooking(T, b1, guest);
ok(s1.id && s1.state.key && /\?id=/.test(s1.join_url), "a booking has a session, held on the platform's own page", s1.join_url);
ok(MS.forBooking(T, b1, staff).id === s1.id, "one session per booking");
throws(() => MS.forBooking(T, b1, stranger), /Unknown booking/, "only its guest (or the store) opens it");

console.log("live sessions — the platform relays only the handshake");
const g = MS.join(T, s1.id, guest);
ok(g.side === "guest" && g.session.live, "the guest joins, and the session goes live");
ok(MS.join(T, s1.id, staff).side === "host", "the store's staff join as its host");
throws(() => MS.join(T, s1.id, stranger), /not found/, "no one else may join");
MS.signal(T, s1.id, guest, { type: "offer", data: { sdp: "v=0" } });
MS.signal(T, s1.id, guest, { type: "candidate", data: { candidate: "a" } });
const forHost = MS.signals(T, s1.id, staff, 0);
ok(forHost.length === 2 && forHost[0].type === "offer" && forHost[0].data.sdp === "v=0", "the host reads what the guest handed it, in order");
ok(MS.signals(T, s1.id, guest, 0).length === 0, "and a side never reads its own");
throws(() => MS.signal(T, s1.id, guest, { type: "virus" }), /Unknown signal/, "only the declared kinds of signal pass");

console.log("live sessions — ending counts the minutes; metered, they are charged");
const e1 = MS.end(T, s1.id, guest);
ok(e1.done && e1.charged === 0, "an unmetered session ends free");
caps.enable(T, "per_minute_billing", { default_rate: 2, minimum_minutes: 3 });
const b2 = book();
const s2 = MS.forBooking(T, b2, guest);
ok(s2.rate === 2, "a metered session carries its rate");
throws(() => MS.join(T, s2.id, guest), /needs 6/, "it goes live only when the guest holds enough for its minimum");
offers.credit(T, guest.owner, 50, "deposit", "test", null, "test");
MS.join(T, s2.id, guest);
const e2 = MS.end(T, s2.id, guest);
ok(Math.abs(e2.charged - 6) < 0.01, "ending charges at least the minimum", e2.charged);
ok(Math.abs(db.get("SELECT balance FROM wallets WHERE tenant_id=? AND owner=?", T, guest.owner).balance - 44) < 0.01, "from the guest's wallet");
const b3 = book(), s3 = MS.forBooking(T, b3, guest);
ok(MS.end(T, s3.id, guest).state.key !== e2.state.key, "a session that never started is cancelled, not charged");

console.log("live sessions — a connector carries them instead");
db.run("INSERT OR IGNORE INTO provider_defs(id,kind,name) VALUES('roomhost','media','Room host')");
caps.enable(T, "media_sessions", { transport: "roomhost", room_url: "https://rooms.example/{room}" });
const s4 = MS.forBooking(T, book(), guest);
ok(s4.transport === "roomhost" && s4.join_url === "https://rooms.example/" + s4.room, "a registered connector's room link is the store's template");
ok(MS.vocabulary(T).transports.some(t => t.id === "roomhost"), "connectors are read from the Provider Registry");

for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } }
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
