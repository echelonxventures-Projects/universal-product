/* LUXORA Platform — local stand-ins for the outside services, for running the whole platform on one
   machine with demo credentials. The platform's own provider specs and adapters run unchanged: only
   where their requests GO is replaced (connect.__setTransport), so what works here is the same code
   that talks to the real service. Payment pages, a mailbox for email and SMS, and carriers.
   Never used by the server itself; scripts/demo.js and test/demo.js start it. */
"use strict";
const http = require("http"), net = require("net"), crypto = require("crypto");
const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const rid = p => p + crypto.randomBytes(7).toString("hex");
const hmac = (secret, data, enc) => crypto.createHmac("sha256", secret).update(data).digest(enc || "hex");
/* the demo's credentials: accepted here and nowhere else */
const CREDS = {
  stripe: { publishableKey: "pk_demo", secretKey: "sk_demo_stripe", webhookSecret: "whsec_demo_stripe" },
  razorpay: { keyId: "rzp_demo_key", keySecret: "rzp_demo_secret", webhookSecret: "whsec_demo_razorpay" },
  paypal: { clientId: "paypal_demo_client", secret: "paypal_demo_secret", webhookId: "WH-DEMO" },
  easypost: { apiKey: "easypost_demo_key", webhookSecret: "whsec_demo_easypost" },
  twilio: { sid: "ACdemo", token: "twilio_demo_token", from: "+15550100000" }
};

function start(opts) {
  const o = Object.assign({ port: 8790, smtpPort: 8791, app: "http://localhost:8787" }, opts);
  const base = "http://localhost:" + o.port, pays = new Map(), inbox = [], shipments = new Map(), sse = [];
  const post = (path, raw, headers) => fetch(o.app + path, { method: "POST", headers: { "Content-Type": "application/json", ...headers }, body: raw }).then(r => r.status).catch(() => 0);
  const note = m => { inbox.unshift({ at: new Date(), ...m }); if (inbox.length > 500) inbox.pop(); };
  /* ---------- payments ---------- */
  const storeOf = url => { try { return new URL(url).searchParams.get("store") || ""; } catch (e) { return ""; } };
  const pay = (kind, amount, currency, ref, back, cancel) => { const p = { id: rid({ stripe: "cs_demo_", razorpay: "plink_demo_", paypal: "PPDEMO" }[kind]), kind, amount: Number(amount), currency: String(currency).toUpperCase(), ref, back, cancel, store: storeOf(back), status: "open", payment: rid({ stripe: "pi_demo_", razorpay: "pay_demo_", paypal: "CAPDEMO" }[kind]), refunded: 0 }; pays.set(p.id, p); return p; };
  const decimals = c => { try { return new Intl.NumberFormat("en", { style: "currency", currency: c }).resolvedOptions().maximumFractionDigits; } catch (e) { return 2; } };
  const money = p => (p.amount / 10 ** decimals(p.currency)).toFixed(decimals(p.currency));
  async function tell(p) {
    const q = "?store=" + encodeURIComponent(p.store), ok = p.status === "paid";
    if (p.kind === "stripe") {
      const raw = JSON.stringify({ id: rid("evt_"), type: ok ? "checkout.session.completed" : "checkout.session.expired", data: { object: { id: p.id, payment_status: ok ? "paid" : "unpaid", payment_intent: p.payment, amount_total: p.amount } } }), t = Math.floor(Date.now() / 1000);
      return post("/api/webhooks/inbound/stripe" + q, raw, { "Stripe-Signature": `t=${t},v1=` + hmac(CREDS.stripe.webhookSecret, t + "." + raw) });
    }
    if (p.kind === "razorpay") {
      const raw = JSON.stringify({ event: ok ? "payment_link.paid" : "payment_link.cancelled", payload: { payment_link: { entity: { id: p.id, amount_paid: ok ? p.amount : 0 } }, payment: { entity: { id: p.payment } } } });
      return post("/api/webhooks/inbound/razorpay" + q, raw, { "x-razorpay-signature": hmac(CREDS.razorpay.webhookSecret, raw) });
    }
    if (ok) return post("/api/webhooks/inbound/paypal" + q, JSON.stringify({ event_type: "CHECKOUT.ORDER.APPROVED", resource: { id: p.id } }), { "paypal-transmission-id": "demo", "paypal-auth-algo": "demo", "paypal-cert-url": "demo", "paypal-transmission-sig": "demo", "paypal-transmission-time": "demo" });
    return 0;
  }
  /* ---------- the requests the platform sends out ---------- */
  function answer(url, req) {
    const u = new URL(url), h = Object.fromEntries(Object.entries(req.headers || {}).map(([k, v]) => [k.toLowerCase(), v])), m = String(req.method || "GET").toUpperCase();
    let b = {}; try { b = /urlencoded/.test(h["content-type"] || "") ? Object.fromEntries(new URLSearchParams(req.body || "")) : JSON.parse(req.body || "{}"); } catch (e) { }
    const basic = (a, c) => h.authorization === "Basic " + Buffer.from(a + ":" + (c || "")).toString("base64");
    const no = (s, j) => ({ status: s, json: j });
    if (u.host === "api.stripe.com") {
      if (!basic(CREDS.stripe.secretKey)) return no(401, { error: { message: "Invalid API key (demo)" } });
      if (u.pathname === "/v1/checkout/sessions" && m === "POST") { const p = pay("stripe", b["line_items[0][price_data][unit_amount]"], b["line_items[0][price_data][currency]"], b.client_reference_id, b.success_url, b.cancel_url); return no(200, { id: p.id, url: base + "/pay/" + p.id, payment_status: "unpaid", status: "open" }); }
      if (u.pathname.startsWith("/v1/checkout/sessions/")) { const p = pays.get(u.pathname.split("/").pop()); return p ? no(200, { id: p.id, payment_status: p.status === "paid" ? "paid" : "unpaid", status: p.status === "failed" ? "expired" : p.status === "paid" ? "complete" : "open", payment_intent: p.payment, amount_total: p.amount }) : no(404, { error: { message: "No such session" } }); }
      if (u.pathname === "/v1/refunds") return refund([...pays.values()].find(p => p.payment === b.payment_intent), Number(b.amount), r => ({ id: r, status: "succeeded" }), e => ({ error: { message: e } }));
    }
    if (u.host === "api.razorpay.com") {
      if (!basic(CREDS.razorpay.keyId, CREDS.razorpay.keySecret)) return no(401, { error: { description: "Authentication failed (demo)" } });
      const rf = /^\/v1\/payments\/([^/]+)\/refund$/.exec(u.pathname);
      if (rf) return refund([...pays.values()].find(p => p.payment === rf[1]), Number(b.amount), r => ({ id: r, status: "processed" }), e => ({ error: { description: e } }));
      if (u.pathname === "/v1/payment_links" && m === "POST") { const p = pay("razorpay", b.amount, b.currency, b.reference_id, b.callback_url, b.callback_url); return no(200, { id: p.id, short_url: base + "/pay/" + p.id, status: "created" }); }
      const p = pays.get(u.pathname.split("/").pop());
      return p ? no(200, { id: p.id, status: { open: "created", paid: "paid", failed: "cancelled" }[p.status], amount_paid: p.status === "paid" ? p.amount : 0, payments: p.status === "paid" ? [{ payment_id: p.payment }] : [] }) : no(404, { error: { description: "Not found" } });
    }
    if (/^api-m\..*paypal\.com$|^api-m\.paypal\.com$/.test(u.host)) {
      if (u.pathname === "/v1/oauth2/token") return basic(CREDS.paypal.clientId, CREDS.paypal.secret) ? no(200, { access_token: "paypal_demo_token" }) : no(401, { error: { message: "Invalid client (demo)" } });
      if (h.authorization !== "Bearer paypal_demo_token") return no(401, { message: "Unauthorized" });
      if (u.pathname.endsWith("/verify-webhook-signature")) return no(200, { verification_status: "SUCCESS" });
      const rf = /^\/v2\/payments\/captures\/([^/]+)\/refund$/.exec(u.pathname);
      if (rf) { const p = [...pays.values()].find(x => x.payment === rf[1]); return refund(p, p ? Math.round(Number((b.amount || {}).value) * 10 ** decimals(p.currency)) : 0, r => ({ id: r, status: "COMPLETED" }), e => ({ message: e })); }
      if (u.pathname === "/v2/checkout/orders" && m === "POST") { const un = b.purchase_units[0], c = un.amount.currency_code, p = pay("paypal", Math.round(Number(un.amount.value) * 10 ** decimals(c)), c, un.custom_id, b.application_context.return_url, b.application_context.cancel_url); return no(200, { id: p.id, status: "CREATED", links: [{ rel: "approve", href: base + "/pay/" + p.id }] }); }
      const parts = u.pathname.split("/"), cap = parts.pop() === "capture", p = pays.get(cap ? parts.pop() : u.pathname.split("/").pop());
      if (!p) return no(404, { message: "Not found" });
      if (cap && p.status === "paid") p.captured = true;
      const amt = { value: money(p), currency_code: p.currency };
      return no(200, { id: p.id, status: p.captured ? "COMPLETED" : p.status === "paid" ? "APPROVED" : "CREATED", purchase_units: [{ amount: amt, payments: { captures: p.captured ? [{ id: p.payment, amount: amt }] : [] } }] });
    }
    if (u.host === "api.twilio.com") { if (!basic(CREDS.twilio.sid, CREDS.twilio.token)) return no(401, { message: "Authenticate (demo)" }); note({ via: "SMS", to: b.To, subject: "", text: b.Body }); return no(201, { sid: rid("SM") }); }
    if (u.host === "api.resend.com" || u.host === "api.sendgrid.com") { note({ via: "Email", to: String(b.to || JSON.stringify(b.personalizations || "")), subject: b.subject, text: b.text || JSON.stringify(b.content || "") }); return no(200, { id: rid("em_") }); }
    if (u.host === "api.easypost.com") {
      if (!basic(CREDS.easypost.apiKey)) return no(401, { error: { message: "Invalid API key (demo)" } });
      const by = /^\/v2\/shipments\/([^/]+)\/buy$/.exec(u.pathname);
      if (by) { const s = shipments.get(by[1]); if (!s) return no(404, { error: { message: "No such shipment" } }); s.tracking = "DEMO" + crypto.randomInt(1e9, 9e9); s.state = "in_transit"; return no(200, { id: s.id, tracking_code: s.tracking, postage_label: { label_url: base + "/label/" + s.id } }); }
      const oz = Number(((b.shipment || {}).parcel || {}).weight || 16), s = { id: rid("shp_"), to: (b.shipment || {}).to_address || {}, state: "quoted" }; shipments.set(s.id, s);
      return no(200, { id: s.id, rates: [["DemoPost", "Ground", 4 + oz / 40, 5], ["DemoPost", "Priority", 8 + oz / 25, 2], ["DemoExpress", "Overnight", 19 + oz / 12, 1]].map(([carrier, service, rate, d]) => ({ id: rid("rate_"), carrier, service, rate: rate.toFixed(2), currency: "USD", delivery_days: d })), messages: [] });
    }
    return no(503, { error: { message: "No stand-in for " + u.host + " — the demo reaches no outside service" } });
    function refund(p, amt, good, bad) { if (!p || p.status !== "paid") return no(400, bad("No such payment")); if (!(amt > 0) || p.refunded + amt > p.amount) return no(400, bad("Refund is more than what is left")); p.refunded += amt; return no(200, good(rid("rf_"))); }
  }
  const transport = async (url, req) => { const r = answer(String(url), req || {}); return { ok: r.status < 300, status: r.status, text: async () => JSON.stringify(r.json) }; };
  /* ---------- the pages a person uses ---------- */
  const page = (title, body) => `<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)}</title><style>body{font:16px/1.5 system-ui;max-width:860px;margin:0 auto;padding:24px 16px;color:#111;background:#fafafa}.c{background:#fff;border:1px solid #ddd;border-radius:10px;padding:20px;margin:12px 0}button,.b{font:inherit;padding:10px 18px;border-radius:8px;border:1px solid #bbb;background:#fff;cursor:pointer;margin:4px 6px 4px 0}.p{background:#166534;color:#fff;border-color:#166534}.r{background:#fff;color:#991b1b}nav a{margin-right:14px}pre{white-space:pre-wrap;font:inherit;margin:8px 0}small{color:#555}</style><nav><a href="/">Demo home</a><a href="/mail">Mailbox</a><a href="/payments">Payments</a><a href="/parcels">Parcels</a></nav><h1>${esc(title)}</h1><p><small>A local stand-in. No real money, message or parcel.</small></p>${body}</html>`;
  const server = http.createServer(async (req, res) => {
    const u = new URL(req.url, base), html = (t, b, s) => { res.writeHead(s || 200, { "Content-Type": "text/html; charset=utf-8" }); res.end(page(t, b)); };
    const act = /^\/pay\/([^/]+)\/(paid|failed)$/.exec(u.pathname), see = /^\/pay\/([^/]+)$/.exec(u.pathname), par = /^\/parcels\/([^/]+)\/(out_for_delivery|delivered)$/.exec(u.pathname);
    if (act && req.method === "POST") { const p = pays.get(act[1]); if (!p) return html("Unknown payment", "", 404); if (p.status === "open") { p.status = act[2]; await tell(p); } res.writeHead(303, { Location: p.status === "paid" ? p.back : p.cancel || p.back }); return res.end(); }
    if (see) { const p = pays.get(see[1]); if (!p) return html("Unknown payment", "", 404); return html("Demo " + p.kind + " payment", `<div class="c"><p>Order <b>${esc(p.ref)}</b></p><p style="font-size:28px">${esc(money(p))} ${esc(p.currency)}</p>${p.status === "open" ? `<form method="post" action="/pay/${p.id}/paid" style="display:inline"><button class="p">Pay</button></form><form method="post" action="/pay/${p.id}/failed" style="display:inline"><button class="r">Decline</button></form><a class="b" href="${esc(p.back)}">Leave without paying</a>` : `<p>This payment is ${esc(p.status)}.</p>`}</div>`); }
    if (par && req.method === "POST") {
      const s = [...shipments.values()].find(x => x.id === par[1]);
      if (s && s.tracking) { s.state = par[2]; const raw = JSON.stringify({ object: "Event", description: "tracker.updated", result: { tracking_code: s.tracking, status: par[2], tracking_details: [{ message: par[2], datetime: new Date().toISOString(), tracking_location: { city: "Demo City" } }] } }); await post("/api/shipping/webhook/easypost", raw, { "X-Hmac-Signature": "hmac-sha256-hex=" + hmac(CREDS.easypost.webhookSecret, raw) }); }
      res.writeHead(303, { Location: "/parcels" }); return res.end();
    }
    if (u.pathname === "/mail.json") { res.writeHead(200, { "Content-Type": "application/json" }); return res.end(JSON.stringify(inbox)); }
    if (u.pathname === "/mail") return html("Mailbox", inbox.map(m => `<div class="c"><b>${esc(m.subject || m.via)}</b><br><small>${esc(m.via)} to ${esc(m.to)} · ${m.at.toLocaleTimeString()}</small><pre>${esc(m.text).replace(/https?:\/\/[^\s<]+/g, x => `<a href="${x}">${x}</a>`)}</pre></div>`).join("") || "<p>Nothing yet.</p>");
    if (u.pathname === "/payments") return html("Payments", [...pays.values()].reverse().map(p => `<div class="c"><a href="/pay/${p.id}">${esc(p.kind)} · ${esc(p.ref)}</a> — ${esc(money(p))} ${esc(p.currency)} — ${esc(p.status)}${p.refunded ? " — refunded " + p.refunded / 10 ** decimals(p.currency) : ""}</div>`).join("") || "<p>Nothing yet.</p>");
    if (u.pathname === "/parcels") return html("Parcels", [...shipments.values()].filter(s => s.tracking).reverse().map(s => `<div class="c">${esc(s.tracking)} to ${esc(s.to.name || "")}, ${esc(s.to.city || "")} — ${esc(s.state)} ${["out_for_delivery", "delivered"].map(x => `<form method="post" action="/parcels/${s.id}/${x}" style="display:inline"><button>${x.replace(/_/g, " ")}</button></form>`).join("")}</div>`).join("") || "<p>No labels bought yet.</p>");
    if (u.pathname.startsWith("/label/")) return html("Demo shipping label", `<div class="c">${esc(u.pathname.slice(7))}</div>`);
    if (u.pathname === "/") return html("LUXORA demo", o.home || "");
    html("Not found", "", 404);
  });
  /* ---------- an SMTP server that keeps what it is sent ---------- */
  const smtp = net.createServer(s => {
    let buf = "", data = null, to = [];
    s.on("error", () => { }); s.write("220 demo ESMTP\r\n");
    s.on("data", d => {
      buf += d; let i;
      while ((i = buf.indexOf("\r\n")) >= 0) {
        const l = buf.slice(0, i); buf = buf.slice(i + 2); const U = l.toUpperCase();
        if (data) {
          if (l !== ".") { data.push(l.startsWith("..") ? l.slice(1) : l); continue; }
          const k = data.indexOf(""), head = data.slice(0, k).join("\n"), raw = data.slice(k + 1).join("\r\n");
          const body = /base64/i.test(head) ? Buffer.from(raw, "base64").toString("utf8") : /quoted-printable/i.test(head) ? Buffer.from(raw.replace(/=\r\n/g, "").replace(/=([0-9A-F]{2})/gi, (_, x) => String.fromCharCode(parseInt(x, 16))), "latin1").toString("utf8") : raw;
          const sj = (/^Subject: (.*)$/mi.exec(head) || [])[1] || "";
          note({ via: "Email", to: to.join(", "), subject: sj.replace(/=\?utf-8\?B\?([^?]+)\?=\s*/gi, (_, x) => Buffer.from(x, "base64").toString("utf8")), text: body }); data = null; to = []; s.write("250 queued\r\n"); continue;
        }
        if (U.startsWith("EHLO")) s.write("250-demo\r\n250 AUTH PLAIN\r\n"); else if (U.startsWith("AUTH")) s.write("235 ok\r\n");
        else if (U.startsWith("RCPT TO:")) { to.push(l.slice(8).replace(/[<>]/g, "").trim()); s.write("250 ok\r\n"); }
        else if (U === "DATA") { data = []; s.write("354 go\r\n"); } else if (U === "QUIT") { s.write("221 bye\r\n"); s.end(); } else s.write("250 ok\r\n");
      }
    });
  });
  const ready = Promise.all([[server, o.port], [smtp, o.smtpPort]].map(([x, p]) => new Promise((ok, no) => { x.once("error", no); x.listen(p, "127.0.0.1", ok); })));
  return { ready, transport, inbox, pays, shipments, base, CREDS, stop: () => { server.close(); smtp.close(); } };
}
module.exports = { start, CREDS };
