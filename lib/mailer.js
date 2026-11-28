/* LUXORA Platform — person-to-person delivery: a message addressed to ONE recipient (a sign-in
   code, a password-reset link, an order confirmation), as opposed to lib/api.js notify(), which
   broadcasts a store event to the store's own configured address.

   Transport, first match wins:
     1. the store's own live notification gateway for the channel (Console → Payments &
        notifications): smtp / sendgrid / resend for email, twilio for SMS;
     2. the platform default: the master deployment's own live gateway for the channel, set in
        the same console screen on the master store (the environment no longer carries one);
     3. none — outside production the message is written to the server log so a developer can
        follow the flow; in production nothing is logged (the text carries a credential).
   A provider's spec (provider_defs.spec) either describes an HTTP request, executed by the
   spec engine (lib/connect.js), or declares a kernel `transport` the platform speaks itself —
   `smtp` (spoken here directly, zero dependencies) or `log` (the server log). The engines
   dispatch on the declared transport, never on a provider's name. */
"use strict";

const net = require("net");
const tls = require("tls");
const crypto = require("crypto");
let _db = null; const db = () => _db || (_db = require("./db.js"));
const connect = () => require("./connect.js");
const sec = () => require("./security.js");

/* the delivery channels are a registry list (deliveryChannels, seeded from lib/seed/providers.json): each row
   declares its providers, the address it delivers to and that address's pattern, the environment adapter
   that supplies a platform default, and which channel is the default */
const CHANNELS = require("./seed/providers.json").DELIVERY_CHANNELS;
function channels() { try { const l = require("./registry.js").list("deliveryChannels"); if (Array.isArray(l) && l.length) return l; } catch (e) { } return CHANNELS; }
function channelOf(key) { const cs = channels(); return cs.find(c => c.key === String(key || "")) || cs.find(c => c.default) || cs[0] || {}; }
const providerKeys = ch => (ch.providers || []).map(p => (typeof p === "string" ? p : p.key));
const providerRow = (ch, id) => (ch.providers || []).map(p => (typeof p === "string" ? { key: p } : p)).find(p => p.key === id) || {};

/* the kernel transports — what a spec's `transport` may name. `local` writes to this
   server (no credential, nothing leaves the machine). Anything else goes through the spec engine. */
const KERNEL = {
  log: { local: true, send: async (cfg, m) => { console.log(`  ✉️  [${m.via}] ${oneLine(m.subject)} — ${oneLine(m.text)}`); return { sent: true }; } },
  smtp: {
    send: async (cfg, m) => { await smtpSend(cfg, m); return { sent: true }; },
  }
};
/* the transport a notification provider's spec declares: the row on file decides (an
   operator's edit included); the seed's declaration only stands in when there is no row */
/* the kind the mailer and notifier speak for: the providerKinds row these providers seed under */
const KIND = "notification";
function transportOf(providerId) {
  const id = String(providerId || "");
  try {
    const r = db().get("SELECT spec FROM provider_defs WHERE id=? AND kind=?", id, KIND);
    if (r) { let j = {}; try { j = JSON.parse(r.spec || "{}") || {}; } catch (e) { } return j.transport ? String(j.transport) : null; }
  } catch (e) { }
  try { const sp = require("./providers.js").PROVIDER_SPECS[KIND + ":" + id]; return (sp && sp.transport) || null; } catch (e) { return null; }
}
function kernelOf(providerId) { const t = transportOf(providerId); return (t && KERNEL[t]) || null; }
/* a provider that only writes to this server (the dev console notifier) */
function isLocal(providerId) { return !!(kernelOf(providerId) || {}).local; }
/* the notifier a new store starts with: the first notification provider whose transport is local */
function localNotifier() {
  let ids = [];
  try { ids = db().all("SELECT id FROM provider_defs WHERE kind=? AND enabled=1 ORDER BY position", KIND).map(r => r.id); } catch (e) { }
  if (!ids.length) try { ids = require("./providers.js").NOTIFICATION_PROVIDERS.map(p => p.id); } catch (e) { }
  return ids.find(id => isLocal(id)) || null;
}

function offline() {
  if (process.env.LX_OFFLINE === "1") return true;
  try { return require("./config.js").driverOf("outbound") === "offline"; } catch (e) { return false; }
}
const oneLine = v => String(v == null ? "" : v).replace(/[\r\n]+/g, " ").trim();

/* ---------- transport resolution ---------- */
function storeTransport(tenantId, channel) {
  const ids = providerKeys(channelOf(channel));
  let rows = [];
  try { rows = db().all("SELECT provider_id, config FROM tenant_gateways WHERE tenant_id=? AND provider_id LIKE 'notify:%' AND enabled=1 AND mode='live' ORDER BY position", Number(tenantId) || 0); } catch (e) { return null; }
  for (const r of rows) {
    const id = r.provider_id.slice(7);
    if (!ids.includes(id)) continue;
    try { const rules = require("./rules.js"); if (!rules.permitsAt("mailer.transport", id, rules.at("mailer.transport", tenantId))) continue; } catch (e) { }
    let cfg = {};
    try { cfg = sec().unsealConfig(tenantId, r.provider_id, r.config || "{}"); } catch (e) { continue; }
    if (cfg && Object.keys(cfg).length) return { provider: id, config: cfg, scope: "store" };
  }
  return null;
}
/* the platform default: the master deployment's own live gateway for the channel (a store with
   none of its own sends through it). Configured in the console like any store's, never in code
   or the environment. */
function platformTransport(tenantId, channel) {
  let m = null; try { m = db().masterTenant(); } catch (e) { }
  if (!m || Number(m.id) === Number(tenantId)) return null;
  const t = storeTransport(m.id, channel);
  return t ? Object.assign(t, { scope: "platform" }) : null;
}
function transportFor(tenantId, channel) { return storeTransport(tenantId, channel) || platformTransport(tenantId, channel); }
function configured(tenantId, channel) { return !!transportFor(tenantId, channelOf(channel).key); }

/* ---------- send ---------- */
async function send(o) {
  const ch = channelOf(o.channel), channel = ch.key;
  const to = oneLine(o.to);
  if (!to) return { sent: false, error: "no recipient" };
  if (ch.pattern && !new RegExp(ch.pattern).test(to)) return { sent: false, error: "invalid " + (ch.address || channel) + (ch.address === "phone" ? " number" : " address") };
  const t = transportFor(o.tenantId, channel);
  if (!t || offline()) {
    if (process.env.NODE_ENV !== "production") console.log(`  ✉️  [${channel}${t ? "·offline" : "·unconfigured"}] to ${to}: ${oneLine(o.subject)} — ${oneLine(o.text)}`);
    return { sent: false, error: t ? "outbound is offline" : "no " + channel + " transport configured" };
  }
  try {
    const k = kernelOf(t.provider);
    if (k) { const r = await k.send(t.config, { to, subject: o.subject, text: o.text, html: o.html, via: t.provider }); return { ...r, via: t.provider, scope: t.scope }; }
    const r = await connect().notify({ provider: t.provider, config: t.config, to, subject: oneLine(o.subject), text: String(o.text || "") });
    if (r.live && r.ok) return { sent: true, via: t.provider, scope: t.scope, id: r.id };
    return { sent: false, via: t.provider, error: r.error || r.reason || "not sent" };
  } catch (e) { return { sent: false, via: t.provider, error: e.message }; }
}
/* fire-and-forget for request paths: the outcome lands in the audit log, never in the response */
function deliver(o) {
  send(o).then(r => {
    if (!r.sent && process.env.NODE_ENV === "production") console.error(`  ✉️  ${channelOf(o.channel).key} delivery failed (${o.kind || "message"}, tenant ${o.tenantId}): ${r.error}`);
    try { db().audit(Number(o.tenantId) || 0, "system", null, "mailer", r.sent ? "message.sent" : "message.failed", "message", o.kind || "message",
      { channel: channelOf(o.channel).key, via: r.via || null, error: r.sent ? undefined : r.error }); } catch (e) { }
  }).catch(() => { });
}

/* a relay on this machine may speak without TLS (a local postfix / dev relay — the credential
   never crosses a network); any other host must offer STARTTLS. There is no switch for it
   (LX_SMTP_ALLOW_PLAINTEXT used to allow plaintext to any host). */
function plaintextAllowed(host) {
  const h = String(host || "").replace(/^\[|\]$/g, "").toLowerCase();
  return h === "localhost" || h === "::1" || /^127\./.test(h);
}
/* ---------- SMTP (RFC 5321) — implicit TLS on smtps/465, STARTTLS required otherwise ---------- */
function smtpSend(cfg, msg) {
  const host = String(cfg.host || ""), port = Number(cfg.port) || 587;
  const implicit = cfg.secure === true || cfg.secure === "true" || port === 465;
  const allowPlain = plaintextAllowed(host);
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
        } else if (!allowPlain) throw new Error("SMTP server does not offer STARTTLS (plaintext is allowed only to a relay on this machine)");
      }
      if (cfg.user) await cmd("AUTH PLAIN " + Buffer.from("\0" + cfg.user + "\0" + (cfg.pass || "")).toString("base64"), [235]);
      await cmd("MAIL FROM:<" + fromAddr + ">", [250]);
      await cmd("RCPT TO:<" + msg.to + ">", [250, 251]);
      await cmd("DATA", [354]);
      /* plain text, and with an HTML part (msg.html) a multipart/alternative of both — a reader shows the richer one */
      const crlf = v => String(v || "").replace(/\r?\n/g, "\r\n");
      const boundary = "lx-" + crypto.randomBytes(12).toString("hex");
      const raw = msg.html
        ? ["--" + boundary, "Content-Type: text/plain; charset=utf-8", "Content-Transfer-Encoding: 8bit", "", crlf(msg.text),
           "--" + boundary, "Content-Type: text/html; charset=utf-8", "Content-Transfer-Encoding: 8bit", "", crlf(msg.html), "--" + boundary + "--"].join("\r\n")
        : crlf(msg.text);
      const body = raw.split("\r\n").map(l => l.startsWith(".") ? "." + l : l).join("\r\n");
      const head = [
        "From: " + from, "To: <" + msg.to + ">", "Subject: " + encodeHeader(oneLine(msg.subject)),
        "Date: " + new Date().toUTCString(), "Message-ID: <" + crypto.randomBytes(12).toString("hex") + "@" + (fromAddr.split("@")[1] || name) + ">",
        "MIME-Version: 1.0", msg.html ? 'Content-Type: multipart/alternative; boundary="' + boundary + '"' : "Content-Type: text/plain; charset=utf-8", "Content-Transfer-Encoding: 8bit"
      ].join("\r\n");
      await cmd(head + "\r\n\r\n" + body + "\r\n.", [250]);
      try { sock.write("QUIT\r\n"); } catch (e) { }
      done = true; clearTimeout(timer); sock.end(); resolve({ ok: true });
    })().catch(fail);
  });
}
function encodeHeader(s) { return /^[\x20-\x7e]*$/.test(s) ? s : "=?UTF-8?B?" + Buffer.from(s, "utf8").toString("base64") + "?="; }

module.exports = { plaintextAllowed, CHANNELS, KERNEL, channelOf, send, deliver, configured, transportFor, transportOf, kernelOf, isLocal, localNotifier, smtpSend };
