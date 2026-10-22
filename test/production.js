/* LUXORA Platform — production posture (the 2026-10 readiness pass).
   Boots the real server with NODE_ENV=production on its own throwaway database and checks
   what a production deployment must never do and what it must always do:
     · refuse to boot on seed-default credentials or a malformed master key
     · never record a payment as captured that no live provider took
     · answer readiness, drain in-flight requests on SIGTERM and exit cleanly
     · back up while serving, and restore only what verifies */
"use strict";
const path = require("path"), fs = require("fs"), net = require("net"), os = require("os");
const { spawn } = require("child_process");
const ROOT = path.join(__dirname, "..");
const DB = path.join(__dirname, "production.db");
const PORT = 8881;
const BASE = `http://localhost:${PORT}`;
const PROD = { NODE_ENV: "production", PLATFORM_PASSWORD: "Prod-Test-Platform-9!", ADMIN_PASSWORD: "Prod-Test-Admin-9!", LX_DB: DB, PORT: String(PORT), LX_LOG: "" };
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const sleep = ms => new Promise(r => setTimeout(r, ms));

function env(extra) {
  const e = Object.assign({}, process.env, PROD, extra || {});
  for (const k of ["LX_ALLOW_SIMULATED_PAYMENTS", "LUXORA_MASTER_KEY", "LX_QUEUE", "LX_DB_DRIVER"]) if (!(extra && k in extra)) delete e[k];
  for (const [k, v] of Object.entries(e)) if (v === undefined) delete e[k];
  return e;
}
/* a server that must refuse: resolve with its exit code and stderr */
function refuses(extra) {
  return new Promise(resolve => {
    const p = spawn(process.execPath, [path.join(ROOT, "server.js")], { cwd: ROOT, env: env(extra), stdio: ["ignore", "ignore", "pipe"] });
    let err = ""; p.stderr.on("data", d => err += d);
    const t = setTimeout(() => p.kill("SIGKILL"), 120000);
    p.on("exit", code => { clearTimeout(t); resolve({ code, err }); });
  });
}
async function boot(extra) {
  const p = spawn(process.execPath, [path.join(ROOT, "server.js")], { cwd: ROOT, env: env(extra), stdio: ["ignore", "ignore", "pipe"] });
  let err = ""; p.stderr.on("data", d => err += d);
  for (let i = 0; i < 240; i++) {
    if (p.exitCode !== null) break;
    try { if ((await fetch(BASE + "/readyz")).ok) return p; } catch (e) { }
    await sleep(500);
  }
  console.error("server failed to boot\n" + err); process.exit(1);
}
const exited = p => p.exitCode !== null ? Promise.resolve(p.exitCode) : new Promise(r => p.on("exit", c => r(c)));
const mk = () => {
  const c = new Map();
  return async (p, m, b) => {
    const r = await fetch(BASE + p, { method: m || "GET", headers: Object.assign({ Cookie: [...c].map(x => x[0] + "=" + x[1]).join("; ") }, m && m !== "GET" ? { "x-csrf": c.get("azc") || "", Origin: BASE, "Content-Type": "application/json" } : {}), body: b === undefined ? undefined : JSON.stringify(b) });
    (r.headers.getSetCookie ? r.headers.getSetCookie() : []).forEach(k => { const kv = k.split(";")[0], i = kv.indexOf("="); c.set(kv.slice(0, i).trim(), kv.slice(i + 1).trim()); });
    const t = await r.text(); let j; try { j = JSON.parse(t); } catch (e) { j = { _raw: t }; }
    return { status: r.status, body: j };
  };
};
const ADDR = { name: "Prod Test", address: "1 Test St", city: "Seattle", state: "WA", zip: "98109", carrier: "house-std" };

(async () => {
  for (const s of ["", "-wal", "-shm"]) fs.rmSync(DB + s, { force: true });
  const bk = fs.mkdtempSync(path.join(os.tmpdir(), "lx-prod-bk-"));
  let srv;
  try {
    console.log("▸ POSTGRES MD5 AUTH SPEAKS THE REAL PROTOCOL");
    {
      /* libpq: "md5" + md5(hex(md5(password + user)) + salt). Vector computed with that
         formula; lib/pg.js hashed the inner digest's raw bytes and no server accepted it. */
      const pg = require("../lib/pg.js");
      const crypto = require("crypto");
      const inner = crypto.createHash("md5").update("s3cret" + "lx").digest("hex");
      const want = "md5" + crypto.createHash("md5").update(inner + "\x01\x02\x03\x04", "latin1").digest("hex");
      ok(typeof pg.md5 === "function" && pg.md5("lx", "s3cret", Buffer.from([1, 2, 3, 4])) === want, "the md5 password message matches libpq's", pg.md5 && pg.md5("lx", "s3cret", Buffer.from([1, 2, 3, 4])));
    }

    console.log("▸ KEY ROTATION NEVER OVERWRITES A LIVE KEY");
    {
      /* a keyring whose only version is k2 (what an env-key rotation used to leave behind):
         naming the next version "k" + count + 1 gave k2 again and replaced the live key.
         Run against an isolated copy — security.js keeps its keyring next to itself. */
      const iso = fs.mkdtempSync(path.join(os.tmpdir(), "lx-keyring-"));
      fs.mkdirSync(path.join(iso, "lib")); fs.mkdirSync(path.join(iso, "data"));
      fs.copyFileSync(path.join(ROOT, "lib", "security.js"), path.join(iso, "lib", "security.js"));
      fs.writeFileSync(path.join(iso, "data", "master.json"), JSON.stringify({ current: "k2", keys: { k2: require("crypto").randomBytes(32).toString("hex") } }));
      const script = `const s = require(${JSON.stringify(path.join(iso, "lib", "security.js"))});
        const sealed = s.encryptSecret("sk_test_value", "1|stripe|secretKey");
        const v = s.rotateKey();
        let opened; try { opened = s.decryptSecret(sealed, "1|stripe|secretKey"); } catch (e) { opened = "THROWS " + e.message; }
        console.log(JSON.stringify({ v, versions: s.keyInfo().count, opened }));`;
      const e2 = Object.assign({}, process.env); delete e2.LUXORA_MASTER_KEY;
      const out = require("child_process").execFileSync(process.execPath, ["-e", script], { env: e2 }).toString().trim().split("\n").pop();
      const r = JSON.parse(out);
      ok(r.v === "k3" && r.versions === 2 && r.opened === "sk_test_value", "rotating a keyring that holds only k2 adds k3 and keeps k2 readable", r);
      fs.rmSync(iso, { recursive: true, force: true });
    }

    console.log("▸ A PRODUCTION SERVER PAYS ONLY WITH REAL MONEY");
    srv = await boot();
    {
      const r = await fetch(BASE + "/readyz"); const j = await r.json();
      ok(r.status === 200 && j.ready === true && j.db === true, "/readyz answers 200 with the database reachable", j);
      const S = mk(); await S("/api/session");
      await S("/api/cart", "POST", { id: "LX-FAS-001", qty: 1 });
      const card = await S("/api/checkout", "POST", Object.assign({ gateway: "stripe", method: "card" }, ADDR));
      ok(card.status === 402 && /simulated capture is disabled/.test(card.body.error || ""), "a card checkout with no live gateway is declined, not simulated as captured", card);
      const orders = await S("/api/orders");
      const o = (orders.body.orders || [])[0];
      ok(o && o.status === "cancelled" && (!o.payment || o.payment.status === "failed"), "…and the order it opened is cancelled with no captured payment", o && { status: o.status, payment: o.payment });
      await S("/api/cart", "POST", { id: "LX-FAS-001", qty: 1 });
      const cod = await S("/api/checkout", "POST", Object.assign({ gateway: "cod", method: "cod" }, ADDR));
      ok(cod.status === 200 && cod.body.order && cod.body.order.payment_status === "pending", "cash on delivery still checks out — pending, nothing claimed", cod.status);
      /* ten different customers paying the same way within the hour are ten customers, not
         one card used ten times: the storefront sends no card, and the fraud screen used to
         fingerprint "cod:cod" for all of them and block the store from the 8th order on */
      const codes = [];
      for (let i = 0; i < 10; i++) {
        const C = mk(); await C("/api/session");
        await C("/api/cart", "POST", { id: "LX-FAS-001", qty: 1 });
        const r = await C("/api/checkout", "POST", Object.assign({ gateway: "cod", method: "cod" }, ADDR, { name: "Customer " + i, address: (i + 10) + " Elm St" }));
        codes.push(r.status);
      }
      ok(codes.every(c => c === 200), "ten customers paying cash on delivery in one hour all check out — none blocked as card velocity", codes);
    }

    console.log("▸ BACKUP WHILE SERVING, RESTORE ONLY WHAT VERIFIES");
    {
      const { backup } = require("../scripts/backup.js");
      const { restore } = require("../scripts/restore.js");
      const plain = await backup({ source: DB, outDir: bk, passphrase: "" });
      ok(plain.manifest.integrity === "ok" && plain.manifest.tables.orders >= 2, "a live backup is consistent and carries the orders just placed", plain.manifest.tables.orders);
      const enc = await backup({ source: DB, outDir: bk, passphrase: "prod-test-passphrase" });
      ok(enc.manifest.encrypted && fs.readFileSync(path.join(enc.dir, enc.manifest.file)).subarray(0, 5).toString() === "LXBK1", "with LX_BACKUP_PASSPHRASE the snapshot is written encrypted");
      const v = await restore(enc.dir, { verifyOnly: true, passphrase: "prod-test-passphrase" });
      ok(v.verified && v.rows === Object.values(enc.manifest.tables).reduce((a, b) => a + b, 0), "the encrypted backup decrypts and every table matches its manifest row count", v);
      let wrong = null; try { await restore(enc.dir, { verifyOnly: true, passphrase: "not-it" }); } catch (e) { wrong = e.message; }
      ok(/decryption failed/.test(wrong || ""), "a wrong passphrase is refused, never restored as garbage", wrong);
      const f = path.join(plain.dir, plain.manifest.file); const fd = fs.openSync(f, "r+"); fs.writeSync(fd, Buffer.from("X"), 0, 1, 4096); fs.closeSync(fd);
      let tamper = null; try { await restore(plain.dir, { verifyOnly: true }); } catch (e) { tamper = e.message; }
      ok(/checksum mismatch/.test(tamper || ""), "a backup altered in storage is refused", tamper);
      const target = path.join(bk, "restored.db");
      const r = await restore(enc.dir, { to: target, passphrase: "prod-test-passphrase" });
      ok(r.restored_to === target && fs.existsSync(target), "a verified backup is restored into place");
      let clobber = null; try { await restore(enc.dir, { to: target, passphrase: "prod-test-passphrase" }); } catch (e) { clobber = e.message; }
      ok(/exists/.test(clobber || ""), "…and an existing database is never overwritten without --force", clobber);
    }

    console.log("▸ SIGTERM DRAINS, NEVER CUTS OFF");
    {
      const body = JSON.stringify({ id: "LX-FAS-001", qty: 1 });
      const s = net.connect(PORT, "127.0.0.1"); let out = "";
      s.on("data", d => out += d);
      await new Promise(r => s.on("connect", r));
      s.write(`POST /api/cart HTTP/1.1\r\nHost: localhost\r\nContent-Type: application/json\r\nContent-Length: ${body.length}\r\nConnection: close\r\n\r\n`);
      await sleep(200);
      srv.kill("SIGTERM");
      await sleep(400);
      let refused = false; try { await fetch(BASE + "/healthz"); } catch (e) { refused = true; }
      ok(refused, "once draining, new connections are refused");
      s.write(body);
      await new Promise(r => s.on("close", r));
      ok(/^HTTP\/1\.1 200/.test(out), "a request in flight at SIGTERM still gets its response", out.split("\r\n")[0]);
      ok(await exited(srv) === 0, "…and the process exits 0");
      srv = null;
    }

    console.log("▸ OPERATOR SETTINGS ARE HONOURED, AND ONLY THOSE");
    {
      srv = await boot({ LX_ALLOW_SIMULATED_PAYMENTS: "1", LUXORA_MASTER_KEY: require("crypto").randomBytes(32).toString("hex") });
      const S = mk(); await S("/api/session");
      await S("/api/cart", "POST", { id: "LX-FAS-001", qty: 1 });
      const card = await S("/api/checkout", "POST", Object.assign({ gateway: "stripe", method: "card" }, ADDR));
      ok(card.status === 200 && card.body.order.payment_status === "captured", "LX_ALLOW_SIMULATED_PAYMENTS=1 (staging) restores the simulated capture", card.status);
      /* a key from the secret store cannot be rotated from the console: the rotation re-wrapped
         every secret under a random key and the next boot read them with the env key again */
      const P = mk(); await P("/api/session");
      const login = await P("/api/platform/login", "POST", { email: "platform@luxora.shop", password: PROD.PLATFORM_PASSWORD });
      const rot = await P("/api/platform/keys/rotate", "POST", {});
      ok(login.status === 200 && rot.status === 409 && /LUXORA_MASTER_KEY/.test(rot.body.error || ""), "with LUXORA_MASTER_KEY set, console key rotation is refused (409), not silently orphaned", { login: login.status, rot: rot.status });
      srv.kill("SIGTERM"); await exited(srv); srv = null;
    }

    console.log("▸ PRODUCTION REFUSES TO BOOT INSECURE");
    {
      const none = await refuses({ PLATFORM_PASSWORD: undefined, ADMIN_PASSWORD: undefined });
      ok(none.code !== 0 && /REFUSING TO START/.test(none.err), "no admin passwords set → refuses to start", none.code);
      const dflt = await refuses({ PLATFORM_PASSWORD: "platform123" });
      ok(dflt.code !== 0 && /platform@luxora\.shop still boots/.test(dflt.err), "a password set TO the documented default is refused too", dflt.code);
      const nonhex = await refuses({ LUXORA_MASTER_KEY: "correct-horse-battery-staple" });
      ok(nonhex.code !== 0 && /LUXORA_MASTER_KEY must be hex/.test(nonhex.err), "a non-hex master key refuses to boot (it decoded to a zero-length key)", nonhex.code);
      const short = await refuses({ LUXORA_MASTER_KEY: "abcd1234" });
      ok(short.code !== 0 && /production requires 64/.test(short.err), "a short master key is refused in production", short.code);
    }
  } catch (e) {
    failed++; console.log("  ✗ threw: " + (e && e.stack || e));
  } finally {
    if (srv) { srv.kill("SIGTERM"); await exited(srv); }
    for (const s of ["", "-wal", "-shm"]) fs.rmSync(DB + s, { force: true });
    fs.rmSync(bk, { recursive: true, force: true });
  }
  console.log(`\n${passed} passed, ${failed} failed`);
  process.exit(failed ? 1 : 0);
})();
