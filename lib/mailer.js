/* LUXORA Platform — person-to-person delivery: a message addressed to ONE recipient (a sign-in
   code, a password-reset link, an order confirmation), as opposed to lib/api.js notify(), which
   broadcasts a store event to the store's own configured address.

   Transport, first match wins:
     1. the store's own live notification gateway for the channel (Console → Payments &
        notifications): smtp / sendgrid / resend for email, twilio for SMS;
     2. the platform default from the environment:
          email  LX_MAIL_PROVIDER=smtp|sendgrid|resend, LX_MAIL_FROM,
                 LX_SMTP_URL=smtp[s]://user:pass@host:port (smtp) or LX_MAIL_API_KEY (http)
          sms    LX_SMS_PROVIDER=twilio, LX_SMS_ACCOUNT_SID, LX_SMS_AUTH_TOKEN, LX_SMS_FROM
     3. none — outside production the message is written to the server log so a developer can
        follow the flow; in production nothing is logged (the text carries a credential).
   HTTP providers go through the spec engine (lib/connect.js); SMTP is spoken here directly,
   zero dependencies. */
"use strict";

const net = require("net");
const tls = require("tls");
const crypto = require("crypto");
let _db = null; const db = () => _db || (_db = require("./db.js"));
const connect = () => require("./connect.js");
const sec = () => require("./security.js");

const EMAIL_PROVIDERS = ["smtp", "sendgrid", "resend"];
const SMS_PROVIDERS = ["twilio"];

function offline() {
  if (process.env.LX_OFFLINE === "1") return true;
  try { return require("./config.js").driverOf("outbound") === "offline"; } catch (e) { return false; }
}
const oneLine = v => String(v == null ? "" : v).replace(/[\r\n]+/g, " ").trim();

/* ---------- transport resolution ---------- */
function storeTransport(tenantId, channel) {
  const ids = channel === "sms" ? SMS_PROVIDERS : EMAIL_PROVIDERS;
  let rows = [];
  try { rows = db().all("SELECT provider_id, config FROM tenant_gateways WHERE tenant_id=? AND provider_id LIKE 'notify:%' AND enabled=1 AND mode='live' ORDER BY position", Number(tenantId) || 0); } catch (e) { return null; }
  for (const r of rows) {
    const id = r.provider_id.slice(7);
    if (!ids.includes(id)) continue;
    let cfg = {};
    try { cfg = sec().unsealConfig(tenantId, r.provider_id, r.config || "{}"); } catch (e) { continue; }
    if (cfg && Object.keys(cfg).length) return { provider: id, config: cfg, scope: "store" };
  }
  return null;
}
function envTransport(channel) {
  const e = process.env;
  if (channel === "sms") {
    if ((e.LX_SMS_PROVIDER || "") !== "twilio" || !e.LX_SMS_ACCOUNT_SID || !e.LX_SMS_AUTH_TOKEN || !e.LX_SMS_FROM) return null;
    return { provider: "twilio", config: { sid: e.LX_SMS_ACCOUNT_SID, token: e.LX_SMS_AUTH_TOKEN, from: e.LX_SMS_FROM }, scope: "platform" };
  }
  const p = e.LX_MAIL_PROVIDER || (e.LX_SMTP_URL ? "smtp" : "");
  if (!p || !e.LX_MAIL_FROM) return null;
  if (p === "smtp") {
    if (!e.LX_SMTP_URL) return null;
    let u; try { u = new URL(e.LX_SMTP_URL); } catch (err) { return null; }
    return { provider: "smtp", config: { host: u.hostname, port: u.port || (u.protocol === "smtps:" ? "465" : "587"), user: decodeURIComponent(u.username), pass: decodeURIComponent(u.password), from: e.LX_MAIL_FROM, secure: u.protocol === "smtps:" }, scope: "platform" };
  }
  if (EMAIL_PROVIDERS.includes(p) && e.LX_MAIL_API_KEY) return { provider: p, config: { apiKey: e.LX_MAIL_API_KEY, from: e.LX_MAIL_FROM }, scope: "platform" };
  return null;
}
function transportFor(tenantId, channel) { return storeTransport(tenantId, channel) || envTransport(channel); }
function configured(tenantId, channel) { return !!transportFor(tenantId, channel || "email"); }

/* ---------- send ---------- */
async function send(o) {
  const channel = o.channel === "sms" ? "sms" : "email";
  const to = oneLine(o.to);
  if (!to) return { sent: false, error: "no recipient" };
  if (channel === "email" && !/^[^@\s<>]+@[^@\s<>]+\.[^@\s<>]+$/.test(to)) return { sent: false, error: "invalid email address" };
  if (channel === "sms" && !/^\+?[0-9][0-9 ()-]{5,19}$/.test(to)) return { sent: false, error: "invalid phone number" };
  const t = transportFor(o.tenantId, channel);
  if (!t || offline()) {
    if (process.env.NODE_ENV !== "production") console.log(`  ✉️  [${channel}${t ? "·offline" : "·unconfigured"}] to ${to}: ${oneLine(o.subject)} — ${oneLine(o.text)}`);
    return { sent: false, error: t ? "outbound is offline" : "no " + channel + " transport configured" };
  }
  try {
    if (t.provider === "smtp") { await smtpSend(t.config, { to, subject: o.subject, text: o.text }); return { sent: true, via: "smtp", scope: t.scope }; }
    const r = await connect().notify({ provider: t.provider, config: t.config, to, subject: oneLine(o.subject), text: String(o.text || "") });
    if (r.live && r.ok) return { sent: true, via: t.provider, scope: t.scope, id: r.id };
    return { sent: false, via: t.provider, error: r.error || r.reason || "not sent" };
  } catch (e) { return { sent: false, via: t.provider, error: e.message }; }
}
/* fire-and-forget for request paths: the outcome lands in the audit log, never in the response */
function deliver(o) {
  send(o).then(r => {
    if (!r.sent && process.env.NODE_ENV === "production") console.error(`  ✉️  ${o.channel || "email"} delivery failed (${o.kind || "message"}, tenant ${o.tenantId}): ${r.error}`);
    try { db().audit(Number(o.tenantId) || 0, "system", null, "mailer", r.sent ? "message.sent" : "message.failed", "message", o.kind || "message",
      { channel: o.channel || "email", via: r.via || null, error: r.sent ? undefined : r.error }); } catch (e) { }
  }).catch(() => { });
}

/* ---------- SMTP (RFC 5321) — implicit TLS on smtps/465, STARTTLS required otherwise ---------- */
function smtpSend(cfg, msg) {
  const host = String(cfg.host || ""), port = Number(cfg.port) || 587;
  const implicit = cfg.secure === true || cfg.secure === "true" || port === 465;
  const allowPlain = process.env.LX_SMTP_ALLOW_PLAINTEXT === "1";
  const from = oneLine(cfg.from), fromAddr = (/<([^>]+)>/.exec(from) || [null, from])[1];
  const timeoutMs = Number(cfg.timeoutMs) || 15000;
  return new Promise((resolve, reject) => {
    let sock = implicit ? tls.connect({ host, port, servername: host }) : net.connect({ host, port });
    let buf = "", waiter = null, done = false;
    const timer = setTimeout(() => fail(new Error("SMTP timeout")), timeoutMs);
    function fail(e) { if (done) return; done = true; clearTimeout(timer); try { sock.destroy(); } catch (x) { } reject(e); }
    function attach(s) {
      s.setEncoding("utf8");
      s.on("data", d => { buf += d; pump(); });
      s.on("error", fail);
    }
    /* a reply is complete at a line "NNN <text>" (a space, not a dash, after the code) */
    function pump() {
      if (!waiter) return;
      const lines = buf.split("\r\n");
      for (let i = 0; i < lines.length - 1; i++) {
        if (/^\d{3} /.test(lines[i]) || /^\d{3}$/.test(lines[i])) {
          const reply = lines.slice(0, i + 1); buf = lines.slice(i + 1).join("\r\n");
          const w = waiter; waiter = null; w({ code: Number(reply[i].slice(0, 3)), lines: reply }); return;
        }
      }
    }
    const read = () => new Promise(r => { waiter = r; pump(); });
    async function cmd(line, okCodes) {
      if (line != null) sock.write(line + "\r\n");
      const r = await read();
      if (!okCodes.includes(r.code)) throw new Error("SMTP " + r.code + " " + r.lines.join(" ").slice(4, 200));
      return r;
    }
    attach(sock);
    (async () => {
      await cmd(null, [220]);
      const name = "luxora.local";
      let ehlo = await cmd("EHLO " + name, [250]);
      if (!implicit) {
        if (ehlo.lines.some(l => /STARTTLS/i.test(l))) {
          await cmd("STARTTLS", [220]);
          sock.removeAllListeners("data"); sock.removeAllListeners("error");
          sock = tls.connect({ socket: sock, servername: host });
          attach(sock);
          await new Promise((res, rej) => { sock.once("secureConnect", res); sock.once("error", rej); });
          ehlo = await cmd("EHLO " + name, [250]);
        } else if (!allowPlain) throw new Error("SMTP server does not offer STARTTLS (set LX_SMTP_ALLOW_PLAINTEXT=1 only for a local relay)");
      }
      if (cfg.user) await cmd("AUTH PLAIN " + Buffer.from("\0" + cfg.user + "\0" + (cfg.pass || "")).toString("base64"), [235]);
      await cmd("MAIL FROM:<" + fromAddr + ">", [250]);
      await cmd("RCPT TO:<" + msg.to + ">", [250, 251]);
      await cmd("DATA", [354]);
      const body = String(msg.text || "").replace(/\r?\n/g, "\r\n").split("\r\n").map(l => l.startsWith(".") ? "." + l : l).join("\r\n");
      const head = [
        "From: " + from, "To: <" + msg.to + ">", "Subject: " + encodeHeader(oneLine(msg.subject)),
        "Date: " + new Date().toUTCString(), "Message-ID: <" + crypto.randomBytes(12).toString("hex") + "@" + (fromAddr.split("@")[1] || name) + ">",
        "MIME-Version: 1.0", "Content-Type: text/plain; charset=utf-8", "Content-Transfer-Encoding: 8bit"
      ].join("\r\n");
      await cmd(head + "\r\n\r\n" + body + "\r\n.", [250]);
      try { sock.write("QUIT\r\n"); } catch (e) { }
      done = true; clearTimeout(timer); sock.end(); resolve({ ok: true });
    })().catch(fail);
  });
}
function encodeHeader(s) { return /^[\x20-\x7e]*$/.test(s) ? s : "=?UTF-8?B?" + Buffer.from(s, "utf8").toString("base64") + "?="; }

module.exports = { send, deliver, configured, transportFor, smtpSend };
