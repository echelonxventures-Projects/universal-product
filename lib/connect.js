/* LUXORA Platform — outbound integration layer (payments, notifications, AI).
   Zero dependencies: uses Node's global fetch. Real HTTP only when a gateway/notifier is in
   `live` mode with credentials; otherwise callers fall back to the offline/simulated path, so the
   platform works with no secrets and nothing hangs. Adapters are keyed by provider id and can be
   extended by data (custom_provider manifests). `__setFetch` lets tests inject a fake transport. */
"use strict";

let fetchFn = (...a) => fetch(...a);
function __setFetch(f) { const prev = fetchFn; fetchFn = f || ((...a) => fetch(...a)); return prev; }

function http(url, { method = "POST", headers = {}, body, timeoutMs = 12000 } = {}) {
  const ac = new AbortController();
  const t = setTimeout(() => ac.abort(), timeoutMs);
  const opts = { method, headers: Object.assign({ "content-type": "application/json" }, headers), signal: ac.signal };
  if (body != null) opts.body = typeof body === "string" ? body : JSON.stringify(body);
  return fetchFn(url, opts).then(async r => {
    const text = await r.text(); let json = null; try { json = JSON.parse(text); } catch (e) { }
    return { status: r.status, ok: r.ok, json, text };
  }).finally(() => clearTimeout(t));
}
const basic = (u, p) => "Basic " + Buffer.from(u + ":" + p).toString("base64");

/* ---- payment adapters: return {ref,status} on success or throw ---- */
const PAY = {
  async stripe(cfg, o) {
    const form = new URLSearchParams({ amount: String(Math.round(o.amount * 100)), currency: (o.currency || "usd").toLowerCase(), "automatic_payment_methods[enabled]": "true", "capture_method": "automatic" });
    const r = await http("https://api.stripe.com/v1/payment_intents", { headers: { Authorization: basic(cfg.apiKey || cfg.secretKey, ""), "content-type": "application/x-www-form-urlencoded", "Idempotency-Key": o.idempotency || "" }, body: form.toString() });
    if (!r.ok) throw new Error((r.json && r.json.error && r.json.error.message) || ("stripe " + r.status));
    return { ref: r.json.id, status: r.json.status === "succeeded" || r.json.status === "requires_capture" ? "captured" : "pending", client: r.json.client_secret };
  },
  async razorpay(cfg, o) {
    const r = await http("https://api.razorpay.com/v1/orders", { headers: { Authorization: basic(cfg.keyId, cfg.keySecret) }, body: { amount: Math.round(o.amount * 100), currency: (o.currency || "INR").toUpperCase(), receipt: o.idempotency || ("rcpt_" + Date.now()) } });
    if (!r.ok) throw new Error((r.json && r.json.error && r.json.error.description) || ("razorpay " + r.status));
    return { ref: r.json.id, status: "pending", client: r.json.id };
  },
  async paypal(cfg, o) {
    const tok = await http("https://api-m." + (cfg.env === "live" ? "" : "sandbox.") + "paypal.com/v1/oauth2/token", { headers: { Authorization: basic(cfg.clientId, cfg.secret), "content-type": "application/x-www-form-urlencoded" }, body: "grant_type=client_credentials" });
    if (!tok.ok) throw new Error("paypal auth " + tok.status);
    const acc = tok.json.access_token;
    const r = await http("https://api-m." + (cfg.env === "live" ? "" : "sandbox.") + "paypal.com/v2/checkout/orders", { headers: { Authorization: "Bearer " + acc }, body: { intent: "CAPTURE", purchase_units: [{ amount: { currency_code: o.currency || "USD", value: o.amount.toFixed(2) } }] } });
    if (!r.ok) throw new Error("paypal " + r.status);
    return { ref: r.json.id, status: r.json.status === "COMPLETED" ? "captured" : "pending" };
  },
  async square(cfg, o) {
    const r = await http("https://connect.squareup.com/v2/payments", { headers: { Authorization: "Bearer " + (cfg.token || cfg.accessToken), "Idempotency-Key": o.idempotency || String(Date.now()) }, body: { source_id: "sq0idp-sandbox", amount_money: { amount: Math.round(o.amount * 100), currency: o.currency || "USD" } } });
    if (!r.ok) throw new Error("square " + r.status);
    return { ref: r.json.payment && r.json.payment.id, status: (r.json.payment && r.json.payment.status) || "pending" };
  },
  async braintree(cfg, o) {
    const r = await http("https://api.braintreegateway.com:443/merchants/" + cfg.merchantId + "/transactions", { headers: { Authorization: basic(cfg.publicKey, cfg.privateKey) }, body: { transaction: { amount: o.amount.toFixed(2), order_id: o.idempotency, channel: "luxe", credit_card: { number: "4111111111111111", expiration_date: "12/30" } } } });
    if (!r.ok) throw new Error("braintree " + r.status);
    return { ref: r.json.transaction && r.json.transaction.id, status: (r.json.transaction && r.json.transaction.status) || "pending" };
  }
  /* cod / bank / upi / paytm / wallet rails settle offline → no adapter → caller simulates */
};

/* ---- notification adapters ---- */
const NOTIFY = {
  async resend(cfg, o) { const r = await http("https://api.resend.com/emails", { headers: { Authorization: "Bearer " + cfg.apiKey }, body: { from: cfg.from || "onboarding@resend.dev", to: [].concat(o.to), subject: o.subject, text: o.text } }); if (!r.ok) throw new Error("resend " + r.status); return { id: r.json.id }; },
  async sendgrid(cfg, o) { const r = await http("https://api.sendgrid.com/v3/mail/send", { headers: { Authorization: "Bearer " + cfg.apiKey }, body: { personalizations: [{ to: [].concat(o.to).map(e => ({ email: e })) }], from: { email: cfg.from }, subject: o.subject, content: [{ type: "text/plain", value: o.text }] } }); if (!r.ok) throw new Error("sendgrid " + r.status); return { id: r.headers || "queued" }; },
  async twilio(cfg, o) { const to = o.to || cfg.to; const r = await http("https://api.twilio.com/2010-04-01/Accounts/" + cfg.accountSid + "/Messages.json", { headers: { Authorization: basic(cfg.accountSid, cfg.authToken), "content-type": "application/x-www-form-urlencoded" }, body: new URLSearchParams({ To: to, From: cfg.from, Body: (o.subject || "") + " " + (o.text || "") }).toString() }); if (!r.ok) throw new Error("twilio " + r.status); return { id: r.json.sid }; },
  async webhook(cfg, o) { const r = await http(cfg.url, { method: "POST", headers: cfg.secret ? { Authorization: "Bearer " + cfg.secret } : {}, body: { event: o.subject, text: o.text, to: o.to, at: new Date().toISOString() } }); if (!r.ok) throw new Error("webhook " + r.status); return { id: String(r.status) }; }
};

function credsOk(cfg, fields) { if (!cfg) return false; return (fields || []).every(f => !f.required || (cfg[f.key] && !String(cfg[f.key]).startsWith("••••") && !String(cfg[f.key]).startsWith("lux.v1."))); }

/* ---- pay: {provider, config, amount, currency, idempotency, offline} ---- */
async function pay(o) {
  const ad = PAY[o.provider];
  if (o.offline || process.env.LX_OFFLINE === "1") return { live: false };
  if (!ad || !o.config || !Object.keys(o.config).length) return { live: false };
  try { const r = await ad(o.config, o); return { live: true, ok: true, ...r }; }
  catch (e) { return { live: true, ok: false, error: e.message }; }
}
async function notify(o) {
  const ad = NOTIFY[o.provider];
  if (o.offline || process.env.LX_OFFLINE === "1") return { live: false };
  if (!ad || !o.config || !Object.keys(o.config).length) return { live: false };
  try { const r = await ad(o.config, o); return { live: true, ok: true, id: r && r.id }; }
  catch (e) { return { live: true, ok: false, error: e.message }; }
}
async function ping(o) {
  if (process.env.LX_OFFLINE === "1") return { live: false };
  if (!o.config || !Object.keys(o.config || {}).length) return { live: false, ok: false, error: "No credentials" };
  // cheap auth check via the provider adapter using a minimal no-op call where possible
  try { const r = await pay(Object.assign({ amount: 0, idempotency: "ping_" + Date.now() }, o)); return { live: true, ok: r.ok, error: r.error }; }
  catch (e) { return { live: true, ok: false, error: e.message }; }
}

module.exports = { pay, notify, ping, PAY, NOTIFY, __setFetch };
