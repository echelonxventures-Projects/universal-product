/* LUXORA Platform — the EasyPost carrier adapter. EasyPost fronts USPS, UPS, FedEx, DHL and ~100
   others with one API: rate a parcel, buy the chosen rate's label, and send signed tracker webhooks.
   LAW-015: a vendor lives in its adapter and is chosen by configuration. The shipping engine
   (lib/shipping.js) finds every lib/carrier-<id>.js, seeds its provider row, and rates, buys and
   tracks through whichever carrier a platform admin activated — it names none of them.
   An adapter exports: row (its shipping_providers row), quote, buy, verify and normalize. */
"use strict";

const BASE = "https://api.easypost.com/v2";
/* the provider row the engine seeds, inactive until a platform admin saves an API key */
const row = { provider_id: "easypost", name: "EasyPost (USPS · UPS · FedEx · DHL)", carrier_type: "aggregator", enabled_countries: ["*"], services: ["rates", "labels", "tracking"] };

async function call(connect, cfg, method, path, body) {
  const r = await connect.request(BASE + path, { method, headers: { "content-type": "application/json", Authorization: "Basic " + Buffer.from(cfg.apiKey + ":").toString("base64") }, body: body ? JSON.stringify(body) : undefined });
  if (!r.ok) return { error: "Carrier: " + ((r.json && r.json.error && (r.json.error.message || r.json.error.code)) || ("HTTP " + r.status)), code: 502 };
  return { json: r.json || {} };
}
/* rate a parcel: the carrier's shipment and every rate on it, cheapest first */
async function quote(connect, cfg, { from, to, parcel }) {
  const r = await call(connect, cfg, "POST", "/shipments", { shipment: { from_address: from, to_address: to, parcel } });
  if (r.error) return r;
  const sh = r.json;
  const rates = (sh.rates || []).map(x => ({ id: x.id, carrier: x.carrier, service: x.service, price: Number(x.rate), currency: x.currency, days: x.delivery_days == null ? null : Number(x.delivery_days) }))
    .filter(x => x.id && x.price >= 0).sort((a, b) => a.price - b.price);
  return { shipment_id: sh.id, rates, messages: (sh.messages || []).map(m => m.message).filter(Boolean).slice(0, 5) };
}
/* buy the label for one of a shipment's rates */
async function buy(connect, cfg, { shipment_ref, rate_ref }) {
  const r = await call(connect, cfg, "POST", "/shipments/" + encodeURIComponent(shipment_ref) + "/buy", { rate: { id: rate_ref } });
  if (r.error) return r;
  return { tracking: String(r.json.tracking_code || ""), label: (r.json.postage_label && r.json.postage_label.label_url) || null };
}
/* EasyPost signs each webhook: X-Hmac-Signature = "hmac-sha256-hex=" + HMAC-SHA256(secret, raw body) */
function verify(cfg, rawBody, headers) {
  const crypto = require("crypto");
  const got = String((headers || {})["x-hmac-signature"] || "");
  const want = "hmac-sha256-hex=" + crypto.createHmac("sha256", cfg.webhookSecret.normalize("NFKD")).update(rawBody).digest("hex");
  return got.length === want.length && crypto.timingSafeEqual(Buffer.from(got), Buffer.from(want));
}
/* an EasyPost tracker event as the engine's {tracking_number, status, location, description, timestamp};
   any other shape passes through unchanged (the generic form) */
function normalize(payload) {
  const p = payload || {};
  if (p.object === "Event" && p.result) {
    const t = p.result, last = (t.tracking_details || []).slice(-1)[0] || {};
    return { tracking_number: t.tracking_code, status: t.status, location: last.tracking_location || {}, description: last.message || p.description || "", timestamp: last.datetime || p.created_at };
  }
  return p;
}

/* what a platform admin is asked for to connect it, and where they find it (the console draws this) */
const setup = {
  name: "EasyPost",
  intro: "One EasyPost account gives every store live rates, labels and tracking for USPS, UPS, FedEx, DHL and ~100 more carriers. Get the keys at easypost.com → Account → API Keys (an EZTK… test key buys free sample labels). Each store then sets its own ship-from address in Store console → Shipping & Tracking.",
  fields: [
    { key: "apiKey", label: "API key", secret: true, required: true, hint: "EZAK… or EZTK…", pattern: "^EZ[AT]K", patternNote: "EasyPost keys start with EZAK (live) or EZTK (test)." },
    { key: "webhookSecret", label: "Webhook secret", secret: true, hint: "the secret you type into EasyPost's webhook form" }
  ],
  webhook: { path: "/api/shipping/webhook/easypost", where: "add it in EasyPost → Account → Webhooks, with the secret above" }
};
module.exports = { setup, row, quote, buy, verify, normalize };
