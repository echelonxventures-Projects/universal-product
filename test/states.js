/* LUXORA Platform — the state-machine kernel (lib/states.js).
   A state machine is a registry row: its vocabulary, its legal moves, what each state MEANS
   (tags) and what entering it DOES (stamps, sets, guards, named handlers). Engines ask by
   meaning and run moves through the kernel; they never name a state. */
"use strict";
const path = require("path");
const fs = require("fs");
const DB = path.join(__dirname, "states.db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
const PORT = 8886;
Object.assign(process.env, { LX_DB: DB, PORT: String(PORT), LX_LOG: "" });
delete process.env.NODE_ENV;
const BASE = `http://localhost:${PORT}`;
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const throws = fn => { try { fn(); return null; } catch (e) { return e.message; } };
const mk = () => {
  const c = new Map();
  return async (p, m, b) => {
    const o = { method: m || "GET", headers: Object.assign({ Cookie: [...c].map(x => x[0] + "=" + x[1]).join("; ") }, m && m !== "GET" ? { "x-csrf": c.get("azc") || "", Origin: BASE, "Content-Type": "application/json" } : {}) };
    if (b !== undefined) o.body = JSON.stringify(b);
    const r = await fetch(BASE + p, o);
    (r.headers.getSetCookie ? r.headers.getSetCookie() : []).forEach(k => { const kv = k.split(";")[0], i = kv.indexOf("="); c.set(kv.slice(0, i).trim(), kv.slice(i + 1).trim()); });
    let body; try { body = await r.json(); } catch (e) { body = {}; }
    return { status: r.status, body };
  };
};

(async () => {
  const silence = console.log; console.log = () => { };
  require("../server.js");
  const db = require("../lib/db.js");
  console.log = silence;
  for (let i = 0; i < 120; i++) { try { if ((await fetch(BASE + "/healthz")).ok) break; } catch (e) { } await sleep(250); }
  const st = require("../lib/states.js");
  const reg = require("../lib/registry.js");
  try {
    console.log("▸ MACHINES ARE REGISTRY ROWS");
    const machines = reg.list("stateMachines");
    ok(Array.isArray(machines) && machines.length >= 10, "the state machines are a registry list", (machines || []).length);
    ok(st.vocab("ride").includes("completed") && st.vocab("ride").length === reg.list("mobilityRideStatuses").length, "a machine's vocabulary is its registry list");
    ok(st.initial("ride") === "requested", "a machine declares its initial state");

    console.log("▸ ENGINES ASK WHAT A STATE MEANS");
    ok(st.is("ride", "completed", "rateable") && !st.is("ride", "cancelled", "rateable"), "a tag says what a state means");
    ok(st.tagged("ride", "terminal").sort().join(",") === "cancelled,completed", "every state that means something is found by its tag");
    ok(st.first("dispatch_run", "success") === "delivered", "the state to move a record to is found by meaning");
    ok(/declares no state tagged/.test(throws(() => st.first("ride", "no_such_tag")) || ""), "asking for a meaning no state has is an error, not a guess");

    console.log("▸ THE LEGAL MOVES ARE DATA, IN ANY SHAPE");
    ok(st.can("ride", "requested", "accepted") && !st.can("ride", "requested", "completed"), "a 'from>to' registry list");
    ok(st.can("purchase_request", "draft", "submitted") && !st.can("purchase_request", "draft", "approved"), "a { from: [to] } map");
    ok(st.can("ticket", "new", "closed") && !st.can("ticket", "new", "teleported"), "a free machine allows any move between known states only");
    ok(st.next("purchase_request", "submitted").join() === "approved", "the next legal states are listed");

    console.log("▸ ENTERING A STATE DOES WHAT THE ROW DECLARES");
    const p1 = st.apply("ride", { from: "requested", to: "accepted", row: {}, force: false });
    ok(p1.patch.status === "accepted" && /^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d$/.test(p1.patch.accepted_at), "a stamp writes the time column, in the machine's clock", p1.patch);
    const p2 = st.apply("experiment", { from: "draft", to: "running", row: {} });
    ok(/T.*Z$/.test(p2.patch.started_at), "a machine may keep ISO time", p2.patch);
    const p3 = st.apply("experiment", { from: "paused", to: "running", row: { started_at: "2026-01-01T00:00:00Z" } });
    ok(p3.patch.started_at === undefined, "a once-stamp never overwrites the first time");
    const p4 = st.apply("replenishment", { from: "suggested", to: "skipped", row: {} });
    ok(p4.patch.po_status === "skipped" && p4.patch.closed_at, "a set writes declared fields", p4.patch);
    ok(/Illegal transition: requested → completed/.test(throws(() => st.apply("ride", { from: "requested", to: "completed", row: {} })) || ""), "an illegal move is refused, naming the legal ones");
    ok(/Unknown ride state/.test(throws(() => st.apply("ride", { from: "requested", to: "teleported", row: {} })) || ""), "an unknown state is refused");
    let seen = null;
    st.handle("ride", "settle_fare", ctx => { seen = ctx.from + ">" + ctx.to; ctx.patch.fare = 42; });
    st.handle("ride", "release_driver", () => { });
    st.handle("ride", "cancel_fee", (ctx, e) => { ctx.patch.fare = e.param; });
    const p5 = st.apply("ride", { from: "trip_start", to: "completed", row: {} });
    ok(seen === "trip_start>completed" && p5.patch.fare === 42 && p5.ran.includes("settle_fare"), "a transition runs the handlers its row names, which may extend the patch", p5);
    const p6 = st.apply("ride", { from: "trip_start", to: "cancelled", row: {} });
    ok(p6.patch.fare === "cancel_fee_midtrip" && p6.ran.join() === "release_driver,cancel_fee", "general effects run before specific ones, with the row's arguments", p6.ran);
    st.handle("purchase_request", "approval_threshold", ctx => { if (ctx.extra.cost > 10) throw new Error("needs approval"); });
    st.handle("purchase_request", "record_approver", ctx => { ctx.patch.approved_by = ctx.extra.by; });
    ok(throws(() => st.apply("purchase_request", { from: "submitted", to: "approved", row: {}, extra: { cost: 99 } })) === "needs approval", "a guard handler can refuse the move");
    const p7 = st.apply("purchase_request", { from: "submitted", to: "approved", row: {}, extra: { cost: 1, by: "ana" } });
    ok(p7.patch.approved_by === "ana" && p7.patch.approved_at, "a passed guard lets the move and its effects run", p7.patch);

    console.log("▸ CHANGING A MACHINE IS A DATA EDIT");
    const P = mk(); await P("/api/session");
    ok((await P("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" })).status === 200, "platform owner signs in");
    const ticket = machines.find(m => m.key === "ticket");
    const edited = { ...ticket, meta: { ...ticket.meta, pending: { tags: ["waiting_on_customer"] } } };
    const save = await P("/api/platform/registries/stateMachines", "POST", { item: edited });
    st.bust();
    ok(save.status === 200 && st.is("ticket", "pending", "waiting_on_customer"), "a new meaning for a state is one registry edit", save.body);
    await P("/api/platform/registries/stateMachines", "POST", { item: ticket }); st.bust();
    console.log("▸ ENGINES FOLLOW THE MACHINE, NOT THEIR OWN CODE");
    const mob = require("../lib/mobility.js");
    const tid = db.get("SELECT id FROM tenants ORDER BY id LIMIT 1").id;
    db.run("INSERT INTO capability_values(tenant_id,capability,enabled,params) VALUES(?,?,1,'{}') ON CONFLICT(tenant_id,capability) DO UPDATE SET enabled=1", tid, "ride_hailing");
    db.run("INSERT INTO rides(tenant_id,ref,rider,pickup,dropoff,vehicle_kind,status,surge,payment_method) VALUES(?,?,?,?,?,?,?,1,'cash')", tid, "RIDE-T-1", "Test", "A", "B", "car", "cancelled");
    const rideId = db.get("SELECT id FROM rides WHERE ref='RIDE-T-1'").id;
    ok(/Only a completed ride/.test(throws(() => mob.rateRide(tid, rideId, 5)) || ""), "a cancelled ride cannot be rated while only completed means rateable");
    const ride = machines.find(m => m.key === "ride");
    const rideEdit = { ...ride, meta: { ...ride.meta, cancelled: { ...ride.meta.cancelled, tags: ride.meta.cancelled.tags.concat(["rateable"]) } } };
    await P("/api/platform/registries/stateMachines", "POST", { item: rideEdit }); st.bust();
    ok(throws(() => mob.rateRide(tid, rideId, 4)) === null, "tagging cancelled as rateable lets the engine rate it — no code change");
    await P("/api/platform/registries/stateMachines", "POST", { item: ride }); st.bust();
    const before = mob.summary(tid).active;
    db.run("INSERT INTO rides(tenant_id,ref,rider,pickup,dropoff,vehicle_kind,status,surge,payment_method) VALUES(?,?,?,?,?,?,?,1,'cash')", tid, "RIDE-T-2", "Test", "A", "B", "car", "arrived");
    ok(mob.summary(tid).active === before + 1, "the engine's stats count a state where its tags put it");

    console.log("▸ THE GATE: CONVERTED ENGINES NAME NO STATE");
    const BY_FILE = { mobility: ["ride", "driver", "vehicle"], operations: ["purchase_request", "approval", "payroll_run", "payroll_line", "work_order", "employee", "project", "task"],
      planning: ["replenishment"], fin: ["dispute", "seller_payout"], qcommerce: ["dispatch_run", "rider", "dark_store", "service_area", "delivery_slot"],
      trade: ["rfq", "rfq_quote", "tender", "tender_bid", "verification", "supplier"], logistics: ["shipment"], experiments: ["experiment"], helpdesk: ["ticket", "agent"],
      /* the orders batch: orders, payments, invoices, credit notes and returns */
      api: ["order", "payment", "invoice", "credit_note", "return"], billing: ["invoice", "credit_note"], marketplace: ["order"], recurring: ["payment"] };
    BY_FILE.fin = BY_FILE.fin.concat(["payment"]); BY_FILE.planning = BY_FILE.planning.concat(["order"]); BY_FILE.qcommerce = BY_FILE.qcommerce.concat(["order"]);
    const named = [];
    for (const [f, ms] of Object.entries(BY_FILE)) {
      const vocab = new Set(ms.flatMap(m => st.vocab(m)));
      const src = fs.readFileSync(path.join(__dirname, "..", "lib", f + ".js"), "utf8").replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/[^\n]*/g, "");
      const pats = [/(?:===|!==|==|!=)\s*["']([a-z_]+)["']/g, /["']([a-z_]+)["']\s*(?:===|!==)/g, /status\s*!?=\s*'([a-z_]+)'/g, /status\s+(?:NOT\s+)?IN\s*\(([^)]*)\)/gi, /\[\s*((?:["'][a-z_]+["']\s*,?\s*)+)\]\.includes\(/g];
      for (const re of pats) { let m; while ((m = re.exec(src))) for (const lit of (m[1].match(/[a-z_]+/g) || [])) if (vocab.has(lit)) named.push(f + ": " + lit); }
    }
    ok(named.length === 0, "no converted engine compares, filters or lists one of its machine's states by name", [...new Set(named)]);
    const kernel = fs.readFileSync(path.join(__dirname, "..", "lib", "states.js"), "utf8").replace(/\/\*[\s\S]*?\*\//g, "");
    ok(!/"(completed|cancelled|paid|delivered|approved|ride|ticket|terminal|success)"/.test(kernel), "the kernel names no machine, state or tag");
  } catch (e) { failed++; console.log("  ✗ threw: " + (e && e.stack || e)); }
  console.log(`\n${passed} passed, ${failed} failed`);
  process.exit(failed ? 1 : 0);
})();
