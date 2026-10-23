/* LUXORA Platform — production-readiness regressions. Each block is a gap that would have
   stopped a real launch: a signed-out person could never receive a code or reset link,
   payments, carriers, the console under the CSP, and recoverable backups. Runs a real
   server on its own throwaway database, with local stand-ins for every outside service
   (an SMTP server, a payment gateway, a carrier API) — nothing here touches the network. */
"use strict";
const DB = require("path").join(__dirname, "production.db");
process.env.LX_DB = DB;
const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");
const net = require("net");
const http = require("http");
const PORT = 8875;
const BASE = `http://localhost:${PORT}`;
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms = 5000) => { for (let i = 0; i < ms / 50; i++) { const v = await fn(); if (v) return v; await sleep(50); } return null; };

const mk = () => {
  const c = new Map();
  const H = () => [...c].map(x => x[0] + "=" + x[1]).join("; ");
  const fn = async (p, m, b, extra) => {
    const o = { method: m || "GET", headers: Object.assign({ Cookie: H() }, m && m !== "GET" ? { "x-csrf": c.get("azc") || "", Origin: BASE, "Content-Type": "application/json" } : {}, extra || {}) };
    if (b !== undefined) o.body = typeof b === "string" ? b : JSON.stringify(b);
    const r = await fetch(BASE + p, o);
    (r.headers.getSetCookie ? r.headers.getSetCookie() : []).forEach(k => { const kv = k.split(";")[0], i = kv.indexOf("="); c.set(kv.slice(0, i).trim(), kv.slice(i + 1).trim()); });
    const text = await r.text();
    let body; try { body = JSON.parse(text); } catch (e) { body = { _raw: text }; }
    return { status: r.status, body, headers: r.headers };
  };
  fn.jar = c;
  return fn;
};
const alive = async () => { try { return (await fetch(BASE + "/healthz")).ok; } catch (e) { return false; } };

/* ---- a local SMTP server: records every message; offers STARTTLS only when asked to ---- */
function smtpServer(opts = {}) {
  const inbox = [];
  const srv = net.createServer(sock => {
    let buf = "", data = null, msg = { auth: null, from: null, to: [] };
    const say = l => sock.write(l + "\r\n");
    say("220 test.local ESMTP");
    sock.on("data", d => {
      buf += d;
      let i;
      while ((i = buf.indexOf("\r\n")) >= 0) {
        const line = buf.slice(0, i); buf = buf.slice(i + 2);
        if (data !== null) {
          if (line === ".") { msg.data = data.join("\r\n"); inbox.push(msg); msg = { auth: msg.auth, from: null, to: [] }; data = null; say("250 queued"); }
          else data.push(line.startsWith("..") ? line.slice(1) : line);
          continue;
        }
        const u = line.toUpperCase();
        if (u.startsWith("EHLO")) { sock.write("250-test.local\r\n" + (opts.starttls ? "250-STARTTLS\r\n" : "") + "250 AUTH PLAIN\r\n"); }
        else if (u.startsWith("AUTH PLAIN ")) { msg.auth = Buffer.from(line.slice(11), "base64").toString().split("\0").slice(1); say("235 ok"); }
        else if (u.startsWith("MAIL FROM:")) { msg.from = line.slice(10); say("250 ok"); }
        else if (u.startsWith("RCPT TO:")) { msg.to.push(line.slice(8)); say("250 ok"); }
        else if (u === "DATA") { data = []; say("354 go"); }
        else if (u === "QUIT") { say("221 bye"); sock.end(); }
        else say("502 no");
      }
    });
    sock.on("error", () => { });
  });
  return new Promise(r => srv.listen(0, "127.0.0.1", () => r({ srv, inbox, port: srv.address().port })));
}
const header = (m, name) => { const h = (m.data || "").split("\r\n\r\n")[0].split("\r\n").find(l => l.toLowerCase().startsWith(name.toLowerCase() + ":")); return h ? h.slice(name.length + 1).trim() : null; };
const bodyOf = m => (m.data || "").split("\r\n\r\n").slice(1).join("\r\n\r\n");

(async () => {
  for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
  const mail = await smtpServer();
  const env = { ...process.env, PORT, LX_DB: DB, LX_LOG: "", LX_MAIL_PROVIDER: "smtp", LX_MAIL_FROM: "LUXORA <no-reply@luxora.test>",
    LX_SMTP_URL: `smtp://mailer:s3cret@127.0.0.1:${mail.port}`, LX_SMTP_ALLOW_PLAINTEXT: "1" };
  const srv = spawn(process.execPath, [path.join(__dirname, "..", "server.js")], { env, stdio: ["ignore", "ignore", "pipe"] });
  let stderr = ""; srv.stderr.on("data", d => { stderr += d; });
  for (let i = 0; i < 120 && !(await alive()); i++) await sleep(500);
  if (!(await alive())) { console.error("server failed to boot\n" + stderr); process.exit(1); }

  try {
    console.log("▸ A SIGNED-OUT PERSON RECEIVES CODES AND LINKS BY EMAIL");
    {
      const A = mk(); await A("/api/session?store=luxora");
      const li = await A("/api/auth/login?store=luxora", "POST", { email: "admin@luxora.shop", password: "admin123" });
      ok(li.status === 200, "store admin signs in", li.body);
      const pv = await A("/api/admin/identity-providers?store=luxora", "PUT", { provider_type: "otp", name: "Email OTP", enabled: true, config: { channel: "email", length: 6, ttl: 5 } });
      ok(pv.status === 200 && pv.body.ok, "an email OTP provider is configured", pv.body);
      await A("/api/admin/identity-providers?store=luxora", "PUT", { provider_type: "magic_link", name: "Magic link", enabled: true, config: { ttl: 15, baseUrl: "https://shop.example" } });

      const G = mk(); await G("/api/session?store=luxora");
      const reg = await G("/api/auth/register?store=luxora", "POST", { name: "Mia Mail", email: "mia@example.com", password: "Correct-Horse-9" });
      ok(reg.status === 200, "a customer registers", reg.body);
      await G("/api/auth/logout?store=luxora", "POST", {});
      const before = mail.inbox.length;
      const init = await G("/api/auth/login-init?store=luxora", "POST", { email: "mia@example.com", method: "otp" });
      ok(init.body.action === "otp_sent" && !JSON.stringify(init.body).match(/\b\d{6}\b/), "requesting a code answers without the code", init.body);
      const m = await until(() => mail.inbox.slice(before).find(x => x.to.some(t => t.includes("mia@example.com"))));
      ok(!!m, "the code arrives at the account's email address over SMTP");
      ok(m && m.auth && m.auth[0] === "mailer" && m.auth[1] === "s3cret", "the relay is authenticated with the configured credentials", m && m.auth);
      ok(m && /no-reply@luxora\.test/.test(m.from) && header(m, "Subject") === "Your sign-in code", "it is from the platform sender, with a plain subject", m && [m.from, header(m, "Subject")]);
      const code = m && (/\b(\d{6})\b/.exec(bodyOf(m)) || [])[1];
      const v = await G("/api/auth/login/otp?store=luxora", "POST", { email: "mia@example.com", otp: code });
      ok(v.status === 200 && v.body.ok, "the emailed code signs the customer in", v.body);

      await G("/api/auth/logout?store=luxora", "POST", {});
      const b2 = mail.inbox.length;
      const ml = await G("/api/auth/login-init?store=luxora", "POST", { email: "mia@example.com", method: "magic_link" });
      ok(ml.body.action === "magic_link_sent" && !ml.body.token && !ml.body.link, "a magic link is requested without the token in the response", ml.body);
      const lm = await until(() => mail.inbox.slice(b2).find(x => x.to.some(t => t.includes("mia@example.com"))));
      const tok = lm && (/token=([0-9a-f]{48})/.exec(bodyOf(lm)) || [])[1];
      ok(!!tok && bodyOf(lm).includes("https://shop.example/"), "the email carries a link on the store's own address", lm && bodyOf(lm));
      const mv = await G("/api/auth/login/magic?store=luxora", "POST", { email: "mia@example.com", token: tok });
      ok(mv.status === 200 && mv.body.ok, "the emailed link signs the customer in", mv.body);

      const b3 = mail.inbox.length;
      await G("/api/auth/login-init?store=luxora", "POST", { email: "nobody-here@example.com", method: "otp" });
      await sleep(300);
      ok(!mail.inbox.slice(b3).some(x => x.to.some(t => t.includes("nobody-here"))), "no email goes to an address with no account");
    }

    console.log("▸ A FORGOTTEN PASSWORD CAN BE RESET FROM THE MAILBOX");
    {
      const G = mk(); await G("/api/session?store=luxora");
      await G("/api/auth/register?store=luxora", "POST", { name: "Ray Reset", email: "ray@example.com", password: "Old-Password-77" });
      const other = mk(); await other("/api/session?store=luxora");
      await other("/api/auth/login?store=luxora", "POST", { email: "ray@example.com", password: "Old-Password-77" });
      ok((await other("/api/session?store=luxora")).body.user, "the account is signed in on a second device");

      const A = mk(); await A("/api/session?store=luxora");
      const b0 = mail.inbox.length;
      const known = await A("/api/auth/password/forgot?store=luxora", "POST", { email: "ray@example.com" });
      const unknown = await A("/api/auth/password/forgot?store=luxora", "POST", { email: "ghost@example.com" });
      ok(known.status === 200 && unknown.status === 200 && known.body.message === unknown.body.message, "the answer is identical for a known and an unknown email", [known.body, unknown.body]);
      ok(!/[0-9a-f]{64}/.test(JSON.stringify(known.body)), "the response never carries the token");
      const m = await until(() => mail.inbox.slice(b0).find(x => x.to.some(t => t.includes("ray@example.com"))));
      const link = m && (/(http\S+reset\.html\S+)/.exec(bodyOf(m)) || [])[1];
      const token = link && new URL(link).searchParams.get("token");
      ok(!!token && /^[0-9a-f]{64}$/.test(token), "the reset link arrives by email", m && bodyOf(m));
      await sleep(200);
      ok(!mail.inbox.slice(b0).some(x => x.to.some(t => t.includes("ghost"))), "nothing is sent for an email with no account");
      const { DatabaseSync } = require("node:sqlite");
      const peek = new DatabaseSync(DB, { readOnly: true });
      const stored = peek.prepare("SELECT token_hash FROM password_resets ORDER BY id DESC LIMIT 1").get();
      peek.close();
      ok(stored && stored.token_hash !== token && stored.token_hash.length === 64, "only a hash of the token is stored");

      const hostile = await new Promise(resolve => {
        const body = JSON.stringify({ email: "ray@example.com" });
        const rq = http.request({ host: "127.0.0.1", port: PORT, path: "/api/auth/password/forgot?store=luxora", method: "POST",
          headers: { Host: "evil.example", "Content-Type": "application/json", "Content-Length": Buffer.byteLength(body), Origin: "http://evil.example",
            Cookie: [...A.jar].map(x => x[0] + "=" + x[1]).join("; "), "x-csrf": A.jar.get("azc") || "" } }, r => { r.resume(); r.on("end", () => resolve({ status: r.statusCode })); });
        rq.on("error", () => resolve({ status: 0 })); rq.end(body);
      });
      const hm = await until(() => mail.inbox.slice(b0 + 1).find(x => x.to.some(t => t.includes("ray@example.com"))));
      ok(!hm || !bodyOf(hm).includes("evil.example"), "a forged Host header never becomes the link in the email", hm && bodyOf(hm));
      ok(hostile.status === 200 && hm && !/https?:/.test(bodyOf(hm)), "…with an untrusted Host the email carries a code, not a link", hm && bodyOf(hm));
      const b5 = mail.inbox.length;
      await A("/api/auth/password/forgot?store=luxora", "POST", { email: "ray@example.com" });
      const nm = await until(() => mail.inbox.slice(b5).find(x => x.to.some(t => t.includes("ray@example.com"))));
      const newer = nm && (/token=([0-9a-f]{64})/.exec(bodyOf(nm)) || [])[1];

      const weak = await A("/api/auth/password/reset?store=luxora", "POST", { token: newer, password: "short" });
      ok(weak.status === 422, "the password policy still applies", weak.status);
      const stale = await A("/api/auth/password/reset?store=luxora", "POST", { token, password: "Brand-New-Pass-88" });
      ok(stale.status === 400, "requesting a new link retires the older one", stale.status);
      const reuse = await A("/api/auth/password/reset?store=luxora", "POST", { token: newer, password: "Old-Password-77" });
      ok(reuse.status === 422, "the current password cannot be chosen again", reuse.status);
      const b1 = mail.inbox.length;
      const good = await A("/api/auth/password/reset?store=luxora", "POST", { token: newer, password: "Brand-New-Pass-88" });
      ok(good.status === 200 && good.body.ok, "a valid link sets the new password", good.body);
      ok(!(await other("/api/session?store=luxora")).body.user, "every session the account held is signed out");
      const again = await A("/api/auth/password/reset?store=luxora", "POST", { token: newer, password: "Another-Pass-99" });
      ok(again.status === 400, "a link works once", again.status);
      const oldPw = await A("/api/auth/login?store=luxora", "POST", { email: "ray@example.com", password: "Old-Password-77" });
      const newPw = await A("/api/auth/login?store=luxora", "POST", { email: "ray@example.com", password: "Brand-New-Pass-88" });
      ok(oldPw.status === 401 && newPw.status === 200, "the old password stops working and the new one signs in", [oldPw.status, newPw.status]);
      ok(!!(await until(() => mail.inbox.slice(b1).find(x => header(x, "Subject") && /password was changed/.test(header(x, "Subject"))))), "the account holder is told the password changed");
      const elsewhere = await A("/api/auth/password/reset?store=aurum", "POST", { token: "f".repeat(64), password: "Brand-New-Pass-88" });
      ok(elsewhere.status === 400, "a bogus token is refused", elsewhere.status);
      let throttled = 0;
      const b2 = mail.inbox.length;
      for (let i = 0; i < 5; i++) await A("/api/auth/password/forgot?store=luxora", "POST", { email: "ray@example.com" });
      await sleep(400);
      throttled = mail.inbox.slice(b2).filter(x => x.to.some(t => t.includes("ray@example.com"))).length;
      ok(throttled === 0, "after three reset emails in 15 minutes, further requests send nothing", throttled);
    }

    console.log("▸ DELIVERY TRANSPORTS");
    {
      const mailer = require("../lib/mailer.js");
      const connect = require("../lib/connect.js");
      const saved = { ...process.env };
      Object.assign(process.env, { LX_MAIL_PROVIDER: "smtp", LX_MAIL_FROM: "Shop <s@luxora.test>", LX_SMTP_URL: `smtp://u:p@127.0.0.1:${mail.port}` });
      delete process.env.LX_SMTP_ALLOW_PLAINTEXT;
      const plain = await mailer.send({ tenantId: 0, channel: "email", to: "x@example.com", subject: "s", text: "t" });
      ok(!plain.sent && /STARTTLS/.test(plain.error), "a relay without STARTTLS is refused unless plaintext is explicitly allowed", plain);
      process.env.LX_SMTP_ALLOW_PLAINTEXT = "1";
      const b = mail.inbox.length;
      const inj = await mailer.send({ tenantId: 0, channel: "email", to: "x@example.com", subject: "Hi\r\nBcc: victim@example.com", text: "line\n.\nafter" });
      const im = mail.inbox[b];
      ok(inj.sent && im && !/^Bcc:/mi.test(im.data) && im.to.length === 1, "a newline in the subject cannot add a header or a recipient", im && im.data);
      ok(im && bodyOf(im).includes("\r\n.\r\nafter"), "a body line holding a lone dot survives (dot-stuffing)", im && bodyOf(im));
      const badTo = await mailer.send({ tenantId: 0, channel: "email", to: "x@example.com>\r\nRCPT TO:<y@example.com", subject: "s", text: "t" });
      ok(!badTo.sent, "a recipient carrying SMTP syntax is refused", badTo);

      const calls = [];
      connect.__setTransport(async (url, o) => { calls.push({ url, o }); return { ok: true, status: 201, text: async () => JSON.stringify({ sid: "SM1", id: "re_1" }) }; });
      Object.assign(process.env, { LX_SMS_PROVIDER: "twilio", LX_SMS_ACCOUNT_SID: "AC123", LX_SMS_AUTH_TOKEN: "tok", LX_SMS_FROM: "+15550001111" });
      const sms = await mailer.send({ tenantId: 0, channel: "sms", to: "+15551234567", subject: "Your sign-in code", text: "Your code is 123456" });
      const c0 = calls[0];
      ok(sms.sent && c0 && c0.url === "https://api.twilio.com/2010-04-01/Accounts/AC123/Messages.json", "SMS goes to Twilio's Messages API for the configured account", c0 && c0.url);
      ok(c0 && c0.o.headers.Authorization === "Basic " + Buffer.from("AC123:tok").toString("base64") && /To=%2B15551234567/.test(c0.o.body) && /Body=Your\+code\+is\+123456/.test(c0.o.body), "…authenticated, to the right number, with the message", c0 && c0.o.body);
      Object.assign(process.env, { LX_MAIL_PROVIDER: "resend", LX_MAIL_API_KEY: "re_key" });
      const rs = await mailer.send({ tenantId: 0, channel: "email", to: "x@example.com", subject: "Hello", text: "Body" });
      const c1 = calls[1];
      ok(rs.sent && c1 && c1.url === "https://api.resend.com/emails" && c1.o.headers.Authorization === "Bearer re_key" && JSON.parse(c1.o.body).to[0] === "x@example.com", "email can go through an HTTP provider (Resend) instead of SMTP", c1 && c1.o.body);
      connect.__setTransport(async () => ({ ok: false, status: 401, text: async () => JSON.stringify({ message: "bad key" }) }));
      const fail = await mailer.send({ tenantId: 0, channel: "email", to: "x@example.com", subject: "Hello", text: "Body" });
      ok(!fail.sent && /bad key/.test(fail.error), "a provider rejection is reported, not treated as sent", fail);
      connect.__setTransport(null);
      for (const k of Object.keys(process.env)) if (!(k in saved)) delete process.env[k];
      Object.assign(process.env, saved);
      const none = await mailer.send({ tenantId: 0, channel: "sms", to: "+15551234567", subject: "s", text: "t" });
      ok(!none.sent && /no sms transport/.test(none.error), "with no transport the send reports that, rather than claiming success", none);
    }
  } catch (e) {
    failed++; console.error("  ✗ harness error:", e && e.stack || e);
  } finally {
    srv.kill("SIGTERM"); mail.srv.close();
    await sleep(300);
    for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
  }
  console.log(`\n${passed} passed, ${failed} failed`);
  process.exit(failed ? 1 : 0);
})();
