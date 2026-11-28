/* More than one server (lib/cluster.js): leases (a job on a clock runs on one server per period, a
   lock holds across servers), epochs (a cache dropped on one server is dropped on all), the servers
   alive, rate limits shared out, sign-in failures counted for every server, the keyring shared by
   every server and refused to one given another key, and two hash chains kept whole by servers
   writing at once. Then two real servers on one database: one store's settings changed through one
   are served by the other, and a guesser locked out on one is locked out on the other. */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os"), crypto = require("crypto"), { spawn, spawnSync } = require("child_process");
const TMP = path.join(os.tmpdir(), "cluster-" + process.pid + ".db");
const wipe = () => { for (const s of ["", "-wal", "-shm"]) try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } };
wipe(); process.env.LX_DB = TMP;
const KEY = crypto.randomBytes(32).toString("hex");
process.env.LUXORA_MASTER_KEY = KEY;
const log = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = log;
const CL = require("../lib/cluster.js"), sec = require("../lib/security.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + JSON.stringify(x).slice(0, 400) : ""))); };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const ROOT = path.join(__dirname, "..");
/* a second process on the same database: runs `code` with db, cluster and security loaded, prints its JSON answer */
const other = (code, env) => {
  const r = spawnSync(process.execPath, ["-e", `const l=console.log;console.log=()=>{};const db=require(${JSON.stringify(path.join(ROOT, "lib/db.js"))});console.log=l;
    const CL=require(${JSON.stringify(path.join(ROOT, "lib/cluster.js"))}), sec=require(${JSON.stringify(path.join(ROOT, "lib/security.js"))});
    Promise.resolve((async()=>{${code}})()).then(v=>{process.stdout.write("\\n@@"+JSON.stringify(v===undefined?null:v));process.exit(0)},e=>{process.stdout.write("\\n@@"+JSON.stringify({error:e.message}));process.exit(0)})`],
    { env: { ...process.env, LX_DB: TMP, LUXORA_MASTER_KEY: KEY, ...(env || {}) }, encoding: "utf8", timeout: 120000 });
  const m = /@@(.*)$/s.exec(r.stdout || ""); return m ? JSON.parse(m[1]) : { error: String(r.stderr || "").split("\n").filter(l => !/^\s+at /.test(l)).join(" ").slice(0, 600) };
};
(async () => {
  try {
    console.log("leases");
    ok(CL.lease("t1", 60000, "a"), "a lease is taken by the first holder");
    ok(!CL.lease("t1", 60000, "b"), "another holder is refused while it lasts");
    ok(CL.lease("t1", 60000, "a"), "its holder renews it");
    ok(CL.lease("t1", 60000, "b", Date.now() + 61000), "once it has run out another holder takes it");
    ok(CL.release("t1", "b") && CL.lease("t1", 1000, "a"), "a released lease is free at once");
    let ran = 0;
    CL.once("job", 60000, () => ran++); CL.once("job", 60000, () => ran++);
    ok(ran === 2, "a job on a clock: the server holding the period runs it when its own timer comes round", ran);
    ok(other(`let n=0; CL.once("job", 60000, () => n++); return n;`) === 0, "another server does not run it in the same period");
    db.run("UPDATE cluster_leases SET until=? WHERE name='job:job'", Date.now() - 1);
    ok(other(`let n=0; CL.once("job", 60000, () => n++); return n;`) === 1, "the next period it runs on whichever server comes first");
    ran = 0; CL.once("job", 60000, () => ran++);
    ok(ran === 0, "and not again on this one");
    console.log("locks across servers");
    let inside = null;
    const first = CL.withLock("bag", async () => { await sleep(300); return "done"; });
    await sleep(20);
    const second = await CL.withLock("bag", async () => "never");
    ok(second.locked, "a second call for the same lock is refused while the first holds it");
    ok(other(`return (await CL.withLock("bag", async () => 1)).locked;`) === true, "also from another server");
    ok((await first).value === "done", "the first finishes");
    ok((await CL.withLock("bag", async () => "again")).value === "again", "and the lock is free after it");
    ok(throws(() => CL.bump("nonsense")), "only the caches it knows are kept in step");
    console.log("caches kept in step");
    const S = require("../lib/settings.js");
    CL.listen(); CL.poll();
    const before = S.load(1).brand.tagline;
    const changed = other(`require(${JSON.stringify(path.join(ROOT, "lib/settings.js"))}).save(1, { brand: { ...require(${JSON.stringify(path.join(ROOT, "lib/settings.js"))}).load(1).brand, tagline: "Changed elsewhere" } }); return true;`);
    ok(changed === true && S.load(1).brand.tagline === before, "a store's settings saved on another server: this one still has its copy", S.load(1).brand.tagline);
    ok(CL.poll() >= 1 && S.load(1).brand.tagline === "Changed elsewhere", "until it reads the counters, then it serves the new value");
    ok(CL.poll() === 0, "nothing more is dropped when nothing more changed");
    let dropped = null; CL.on("search", r => { dropped = r; });
    other(`require(${JSON.stringify(path.join(ROOT, "lib/search.js"))}).invalidate(7); return 1;`);
    CL.poll(); ok(dropped === "7", "a store's search index dropped on another server is dropped here", dropped);
    CL.listen();
    console.log("servers");
    CL.beat();
    other(`CL.beat(); return 1;`);
    ok(CL.beat() === 2 && CL.liveCount() === 2, "each server counts the servers alive (the other one beat a moment ago)", CL.nodes().map(n => n.id));
    const Lim = sec.RateLimiter(10, 0);
    let let_ = 0; for (let i = 0; i < 10; i++) if (Lim("k1")) let_++;
    ok(let_ === 5, "with two servers, each lets through its half of a limit", let_);
    db.run("UPDATE cluster_nodes SET seen_at=? WHERE id<>?", Date.now() - 60000, CL.NODE);
    ok(CL.beat() === 1, "a server not heard from is no longer counted");
    const st = CL.status();
    ok(st.nodes.length === 1 && st.nodes[0].self && st.versions.length === 1, "the status lists the servers alive and their versions", st.nodes);
    console.log("sign-in failures, for every server");
    for (let i = 0; i < 5; i++) other(`sec.noteLoginFail("guess@example.com"); return 1;`);
    ok(sec.lockState("guess@example.com").locked, "failures on other servers lock the account here");
    sec.noteLoginOk("guess@example.com");
    ok(!sec.lockState("guess@example.com").locked && !db.get("SELECT 1 x FROM login_attempts WHERE key='guess@example.com'"), "a good sign-in clears it everywhere");
    console.log("the keyring every server shares");
    ok(!!db.get("SELECT 1 x FROM cluster_keyring WHERE id=1"), "the keyring is kept in the database, sealed with the key every server is given");
    const was = sec.keyInfo().version;
    const sealed = other(`const v = sec.rotateKey(); return { v, s: sec.encryptSecret("for every server", "ctx") };`);
    ok(sealed.v && sealed.v !== was && sealed.s.split(".")[2] === sealed.v, "another server rotates the key and seals with the new version", sealed);
    ok(sec.decryptSecret(sealed.s, "ctx") === "for every server", "this server opens it: it reads the shared keyring for the version it lacks");
    ok(sec.keyInfo().version === sealed.v, "and takes the new version as current");
    const mine = sec.encryptSecret("back the other way", "ctx");
    ok(other(`return sec.decryptSecret(${JSON.stringify(mine)}, "ctx");`) === "back the other way", "what this server seals the other opens");
    ok(other(`return sec.blindIndex("x@example.com", "owner");`) === sec.blindIndex("x@example.com", "owner"), "a blind index is the same on every server");
    const stranger = other(`return 1;`, { LUXORA_MASTER_KEY: crypto.randomBytes(32).toString("hex") });
    ok(stranger && /differs from the one the other servers use/.test(stranger.error || ""), "a server given another key refuses to start", stranger);
    console.log("hash chains with servers writing at once");
    const writers = [0, 1].map(k => new Promise(res => {
      const p = spawn(process.execPath, ["-e", `const l=console.log;console.log=()=>{};const db=require(${JSON.stringify(path.join(ROOT, "lib/db.js"))});const K=require(${JSON.stringify(path.join(ROOT, "lib/kernel.js"))});console.log=l;
        for (let i=0;i<60;i++){ db.audit(1,"system",null,"w${k}","test.write","x",String(i),"{}"); K.internal.tx(()=>K.internal.append("test.written",{payload:{w:${k},i}})); }`], { env: { ...process.env, LX_DB: TMP, LUXORA_MASTER_KEY: KEY }, stdio: "ignore" });
      p.on("exit", res);
    }));
    await Promise.all(writers);
    ok(db.get("SELECT COUNT(*) n FROM audit_log WHERE action='test.write'").n === 120, "every audit row of both servers is written", db.get("SELECT COUNT(*) n FROM audit_log WHERE action='test.write'").n);
    ok(db.auditChainVerify(1).ok, "and the store's audit chain is whole", db.auditChainVerify(1));
    const K = require("../lib/kernel.js");
    ok(db.get("SELECT COUNT(*) n FROM k_events WHERE type='test.written'").n === 120 && K.verifyEvents().ok, "the event log too", K.verifyEvents());
    CL.stop();
    ok(!db.get("SELECT 1 x FROM cluster_nodes WHERE id=?", CL.NODE), "a server shutting down leaves at once");

    console.log("two servers on one database");
    const PA = 18951, PB = 18952;
    const boot = port => spawn(process.execPath, [path.join(ROOT, "server.js")], { env: { ...process.env, PORT: port, LX_DB: TMP, LUXORA_MASTER_KEY: KEY, LX_LOG: "" }, stdio: ["ignore", "ignore", "pipe"] });
    const up = async port => { for (let i = 0; i < 300; i++) { try { if ((await fetch("http://localhost:" + port + "/healthz")).ok) return true; } catch (e) { } await sleep(200); } return false; };
    const A = boot(PA); const aUp = await up(PA);
    const B = boot(PB); const bUp = await up(PB);
    try {
      ok(aUp && bUp, "both servers start on the same database");
      await sleep(500);
      ok(db.all("SELECT id FROM cluster_nodes WHERE seen_at>?", Date.now() - 45000).length >= 2, "both are in the list of servers");
      const client = port => { const jar = new Map(); return async (p, m, b) => {
        const h = { "Content-Type": "application/json", Cookie: [...jar].map(x => x.join("=")).join("; ") }; if (jar.get("azc")) h["x-csrf"] = jar.get("azc");
        const r = await fetch("http://localhost:" + port + p, { method: m || "GET", headers: h, body: b ? JSON.stringify(b) : undefined });
        (r.headers.getSetCookie() || []).forEach(k => { const kv = k.split(";")[0], i = kv.indexOf("="); jar.set(kv.slice(0, i), kv.slice(i + 1)); });
        return { st: r.status, b: await r.json().catch(() => ({})) }; }; };
      const a = client(PA), b = client(PB);
      await a("/api/session"); await b("/api/session");
      ok((await b("/api/config")).b.brand, "the second server serves the store");
      const login = await a("/api/auth/login", "POST", { email: "admin@luxora.shop", password: "admin123" });
      const cur = (await a("/api/admin/settings")).b;
      const put = await a("/api/admin/settings", "PUT", { brand: { ...((cur.settings || cur).brand || {}), tagline: "Saved through the first server" } });
      ok(login.st === 200 && put.st === 200, "the store's admin saves a setting through the first server", [login.st, put.st, put.b.error]);
      let seen = ""; for (let i = 0; i < 30 && seen !== "Saved through the first server"; i++) { await sleep(200); seen = (await b("/api/config")).b.brand.tagline; }
      ok(seen === "Saved through the first server", "the second server serves it within seconds", seen);
      const g1 = client(PA), g2 = client(PB); await g1("/api/session"); await g2("/api/session");
      for (let i = 0; i < 5; i++) await g1("/api/auth/login", "POST", { email: "victim@example.com", password: "wrong-" + i });
      const locked = await g2("/api/auth/login", "POST", { email: "victim@example.com", password: "wrong-again" });
      ok(locked.st === 423, "a guesser locked out on one server is locked out on the other", [locked.st, locked.b.error]);
    } finally { for (const p of [A, B]) p.kill("SIGTERM"); await sleep(800); }
    ok(!db.all("SELECT id FROM cluster_nodes WHERE seen_at>?", Date.now() - 45000).length, "both leave the list when they stop");
  } catch (e) { failed++; console.log("  ✗ threw: " + (e.stack || e.message)); }
  console.log(`\n${passed} passed, ${failed} failed`);
  wipe();
  process.exit(failed ? 1 : 0);
})();
function throws(fn) { try { fn(); return false; } catch (e) { return true; } }
