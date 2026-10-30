/* LUXORA Platform - pluggable provider registry: payments, shipping, notifications, tax, countries.
   Providers are pure data manifests - add new ones (built-in or custom JSON) with zero code changes. */
"use strict";
/* seed data (lib/seed/providers.json): data, not code — the registries are seeded from it */
const SEED_PROVIDERS = require("./seed/providers.json");

/* ---------------- countries (seed data; DB table is source of truth at runtime) ---- */
/* geography only: code, name, currency, symbol, locale. A country's decimals are its
   currency's; its tax is the tax engine's; where a provider operates is the provider's */
const COUNTRIES = SEED_PROVIDERS.COUNTRIES;

/* ---------------- currencies (seed data; DB table is source of truth at runtime) ---- */
/* usd = value of 1 unit in USD */
const CURRENCIES = SEED_PROVIDERS.CURRENCIES;

/* ---------------- connectors: payments, shipping, notifications, tax, marketing ----------------
   Every connector is a seed row (lib/seed/providers.json), written to provider_defs once and
   edited from the Provider Registry from then on — no connector is named in code. Rows that
   share a field set name it ("fields": "set:<name>", declared once under FIELD_SETS). */
const fieldsOf = f => (typeof f === "string" && f.startsWith("set:") ? (SEED_PROVIDERS.FIELD_SETS || {})[f.slice(4)] || [] : f);
const connectors = list => (list || []).map(p => (p.fields === undefined ? p : { ...p, fields: fieldsOf(p.fields) }));
const PAYMENT_PROVIDERS = connectors(SEED_PROVIDERS.PAYMENT_PROVIDERS);
const SHIPPING_PROVIDERS = connectors(SEED_PROVIDERS.SHIPPING_PROVIDERS);
const NOTIFICATION_PROVIDERS = connectors(SEED_PROVIDERS.NOTIFICATION_PROVIDERS);
const TAX_PROVIDERS = connectors(SEED_PROVIDERS.TAX_PROVIDERS);

/* ---------------- declarative integration SPECS (data, not code) ----------------
   Each entry is a "fill-in-the-blanks" request description the spec engine executes.
   Adding/changing a provider's protocol is editing this data (or a custom provider's
   manifest), never JavaScript. amountCents = amount*100 helper is provided by the engine. */
/* notes that lived in the seed literal (now lib/seed/providers.json): */
/* payments */
/* Stripe-hosted Checkout: the server never sees a card. The session is created here, the
   shopper is redirected to session.url, and the signed checkout.session.* webhook moves the
   payment to captured/failed. A refund is issued against the session's payment_intent. */
/* an order is created, the shopper pays it in Razorpay Checkout; `order.paid` (signed with
   the store's webhook secret, X-Razorpay-Signature = hex HMAC-SHA256 of the body) or a
   status lookup moves it to captured. A failed attempt does not fail the order — the
   shopper may retry it — so only "paid" is mapped. */
/* an order is created and the shopper approves it on PayPal (the approve link is the
   redirect); an approved order is then captured — by the CHECKOUT.ORDER.APPROVED webhook or
   by a status lookup — and PAYMENT.CAPTURE.COMPLETED confirms it. PayPal signs webhooks with
   a certificate, so the signature is checked by PayPal's own verify call. `env` is
   "sandbox." for testing and blank for live. */
/* Square signs webhooks with its signature key: x-square-hmacsha256-signature = base64
   HMAC-SHA256 of the notification URL followed by the body */
/* Braintree's signed webhooks are its own payload format; a status lookup confirms instead */
/* notifications */
/* marketing (fill-in-the-blanks; execute → /api/marketing) */
const PROVIDER_SPECS = SEED_PROVIDERS.PROVIDER_SPECS;

const MARKETING_PROVIDERS = connectors(SEED_PROVIDERS.MARKETING_PROVIDERS);

function supports(provider, country) {
  return provider.countries.includes("*") || provider.countries.includes(country);
}
function paymentProvider(id, customs) {
  return (customs || []).concat(PAYMENT_PROVIDERS).find(p => p.id === id);
}

module.exports = { COUNTRIES, CURRENCIES, PAYMENT_PROVIDERS, SHIPPING_PROVIDERS, NOTIFICATION_PROVIDERS, TAX_PROVIDERS, MARKETING_PROVIDERS, PROVIDER_SPECS, supports, paymentProvider };
