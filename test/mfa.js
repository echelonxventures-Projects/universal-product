/* LUXORA Platform — sign-in protection: the second factor for admins, a lockout that a stranger
   cannot turn on an account's owner, confirmed email addresses and guests' order news. A real
   production-mode server on its own throwaway database. */
"use strict";
const path = require("path"), fs = require("fs"), net = require("net"), { spawn } = require("child_process");
const DB = path.join(__dirname, "mfa.db"), PORT = 8898, BASE = "http://localhost:" + PORT;
const clean = () => { for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } } };
clean();
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + JSON.stringify(x) : ""))); };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const mk = () => {
  const c = new Map();
  const fn = async (p, m, b) => {
    const o = { method: m || "GET", headers: { Cookie: [...c].map(x => x[0] + "=" + x[1]).join("; "), "Content-Type": "application/json", "x-csrf": c.get("azc") || "" } };
    if (b !== undefined) o.body = JSON.stringify(b);
    const r = await fetch(BASE + p, o);
    r.headers.getSetCookie().forEach(k => { const kv = k.split(";")[0], i = kv.indexOf("="); c.set(kv.slice(0, i).trim(), kv.slice(i + 1).trim()); });
    const t = await r.text(); let body; try { body = JSON.parse(t); } catch (e) { body = { _raw: t }; }
    return { status: r.status, body };
  };
  fn.jar = c; return fn;
};
(async () => {
  const srv = spawn(process.execPath, [path.join(__dirname, "..", "server.js")], { env: { ...process.env, NODE_ENV: "production", PORT, LX_DB: DB, LX_LOG: "", LX_OFFLINE: "1", PLATFORM_PASSWORD: "Plat-Strong-77", ADMIN_PASSWORD: "Admin-Strong-77" }, stdio: ["ignore", "ignore", "pipe"] });
  let err = ""; srv.stderr.on("data", d => { err += d; });
  for (let i = 0; i < 240; i++) { try { if ((await fetch(BASE + "/readyz")).ok) break; } catch (e) { } await sleep(500); }
  process.env.LX_DB = DB;
  const { DatabaseSync } = require("node:sqlite"); const db = new DatabaseSync(DB); db.exec("PRAGMA busy_timeout=5000");
  const crypto = require("crypto");
  const b32 = s => { let bits = 0, v = 0; const out = []; for (const ch of s) { v = (v << 5) | "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567".indexOf(ch); bits += 5; if (bits >= 8) { out.push((v >>> (bits - 8)) & 255); bits -= 8; } } return Buffer.from(out); };
  const totp = (secret, off) => { const n = Buffer.alloc(8); n.writeBigUInt64BE(BigInt(Math.floor(Date.now() / 30000) + (off || 0))); const h = crypto.createHmac("sha1", b32(secret)).update(n).digest(); const o = h[19] & 15; return String((h.readUInt32BE(o) & 0x7fffffff) % 1e6).padStart(6, "0"); };
  try {
    console.log("▸ PLATFORM ADMIN");
    const P = mk(); await P("/api/session");
    const l = await P("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "Plat-Strong-77" });
    ok(l.status === 200 && l.body.mfa === "setup", "in production an admin with no second factor must set one up", l.body);
    ok((await P("/api/platform/tenants")).status !== 200 && (await P("/api/auth/me")).body.hasPlatform === false, "until then the sign-in carries no authority");
    ok((await P("/metrics")).status === 401, "nor the metrics");
    const st = (await P("/api/platform/mfa/start", "POST", {})).body;
    ok((await P("/api/platform/mfa/confirm", "POST", { code: "000000" })).status === 401, "a wrong code turns nothing on");
    const code0 = totp(st.secret);
    const cf = await P("/api/platform/mfa/confirm", "POST", { code: code0 });
    ok(cf.status === 200 && cf.body.recovery.length === 10, "a right code turns it on and gives recovery codes", cf.body.error);
    ok((await P("/api/platform/tenants")).status === 200, "and the sign-in has its authority");
    const row = db.prepare("SELECT secret, recovery FROM mfa_factors WHERE scope='platform'").get();
    ok(/^lux\.v1\./.test(row.secret) && !row.recovery.includes(cf.body.recovery[0].replace("-", "")), "the secret is sealed and recovery codes are kept only as digests");
    const P2 = mk(); await P2("/api/session");
    const l2 = await P2("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "Plat-Strong-77" });
    ok(l2.body.mfa === "verify" && (await P2("/api/platform/tenants")).status !== 200, "a new sign-in needs a code", l2.body);
    ok((await P2("/api/platform/mfa/start", "POST", {})).status === 403, "the password alone cannot replace the factor");
    ok((await P2("/api/platform/mfa/verify", "POST", { code: code0 })).status === 401, "a code already used is refused");
    ok((await P2("/api/platform/mfa/verify", "POST", { code: totp(st.secret, 1) })).status === 200 && (await P2("/api/platform/tenants")).status === 200, "the next code opens it");
    const P3 = mk(); await P3("/api/session"); await P3("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "Plat-Strong-77" });
    ok((await P3("/api/platform/mfa/verify", "POST", { code: cf.body.recovery[0].toLowerCase() })).status === 200, "a recovery code works");
    const P4 = mk(); await P4("/api/session"); await P4("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "Plat-Strong-77" });
    ok((await P4("/api/platform/mfa/verify", "POST", { code: cf.body.recovery[0] })).status === 401, "once");
    let locked = 0; for (let i = 0; i < 8; i++) locked = (await P4("/api/platform/mfa/verify", "POST", { code: "111111" })).status;
    ok(locked === 423 || locked === 429, "guessing codes is locked out", locked);

    console.log("▸ STORE STAFF");
    const A = mk(); await A("/api/session");
    const al = await A("/api/auth/login", "POST", { email: "admin@luxora.shop", password: "Admin-Strong-77" });
    ok(al.body.mfa === "setup" && (await A("/api/admin/orders")).status === 403 && !(await A("/api/session")).body.allowedSections.length, "a store admin must set one up too", al.body);
    const as = (await A("/api/auth/mfa/start", "POST", {})).body;
    ok((await A("/api/auth/mfa/confirm", "POST", { code: totp(as.secret) })).status === 200 && (await A("/api/admin/orders")).status === 200, "and then has their authority");

    console.log("▸ LOCKOUT");
    await sleep(1000);
    const C = mk(); await C("/api/session");
    ok((await C("/api/auth/register", "POST", { name: "Lou Lock", email: "lou@example.com", password: "Lou-Strong-99" })).status === 200 && C.jar.has("azd"), "signing up marks the browser");
    await C("/api/auth/logout", "POST", {});
    const X = mk(); await X("/api/session"); let s = 0;
    for (let i = 0; i < 7; i++) { s = (await X("/api/auth/login", "POST", { email: "lou@example.com", password: "wrong" + i })).status; if (s === 429) { await sleep(2500); i--; } }
    ok(s === 423, "a stranger's guesses lock strangers out", s);
    let back = await C("/api/auth/login", "POST", { email: "lou@example.com", password: "Lou-Strong-99" });
    if (back.status === 429) { await sleep(3000); back = await C("/api/auth/login", "POST", { email: "lou@example.com", password: "Lou-Strong-99" }); }
    ok(back.status === 200, "but not the owner, on a browser they have used", [back.status, back.body.error]);

    console.log("▸ EMAIL");
    const u = db.prepare("SELECT id, email_verified_at FROM users WHERE email='lou@example.com'").get();
    ok(!u.email_verified_at, "an address starts unconfirmed");
    const tok = crypto.randomBytes(32).toString("hex");
    db.prepare("INSERT INTO email_verifications(tenant_id,user_id,email,token_hash,expires_at) VALUES(1,?,?,?,?)").run(u.id, "lou@example.com", crypto.createHash("sha256").update(tok).digest("hex"), Date.now() + 1e6);
    ok((await X("/api/auth/email/verify", "POST", { token: "0".repeat(64) })).status === 400, "a made-up link confirms nothing");
    ok((await X("/api/auth/email/verify", "POST", { token: tok })).status === 200 && !!db.prepare("SELECT email_verified_at v FROM users WHERE id=?").get(u.id).v, "the link sent to it does");
    let again = await X("/api/auth/email/verify", "POST", { token: tok });
    if (again.status === 429) { await sleep(3000); again = await X("/api/auth/email/verify", "POST", { token: tok }); }
    ok(again.status === 400, "once", again);
    db.prepare("INSERT INTO products(tenant_id,id,title,brand,dept,price,stock,lifecycle,type) VALUES(1,'G1','Guest item','B','books',10,5,'published','physical')").run();
    const G = mk(); await G("/api/session"); await G("/api/cart", "POST", { id: "G1", qty: 1 });
    const dest = { name: "Gus Guest", address: "1 St", city: "X", state: "WA", zip: "98109", gateway: "cod" };
    ok((await G("/api/checkout", "POST", { ...dest, email: "not-an-email" })).status === 422, "a guest's address is checked");
    const go = await G("/api/checkout", "POST", { ...dest, email: "Gus@Example.com" });
    ok(go.status === 200 && db.prepare("SELECT email FROM orders WHERE num=?").get(go.body.order.num).email === "gus@example.com", "and kept on the order", [go.status, go.body.error]);
  } catch (e) { failed++; console.error("  ✗ harness error:", e && e.stack || e, err.slice(-800)); }
  srv.kill("SIGTERM"); await sleep(300); try { db.close(); } catch (e) { }
  clean();
  console.log(`\n${passed} passed, ${failed} failed`);
  process.exit(failed ? 1 : 0);
})();
