/* LUXORA Platform - pluggable provider registry: payments, shipping, notifications, tax, countries.
   Providers are pure data manifests - add new ones (built-in or custom JSON) with zero code changes. */
"use strict";

/* ---------------- countries ---------------- */
const COUNTRIES = {
  US: { name: "United States", currency: "USD", symbol: "$", locale: "en-US", tax: { mode: "manual", rate: 0.08875 }, payments: ["stripe", "paypal", "square", "braintree", "adyen", "cod", "bank"], shipping: ["house-std", "fedex", "ups", "usps"] },
  IN: { name: "India", currency: "INR", symbol: "₹", locale: "en-IN", tax: { mode: "gst", rate: 0.12 }, payments: ["razorpay", "upi", "paytm", "cod", "bank"], shipping: ["house-std", "delhivery", "bluedart"] },
  GB: { name: "United Kingdom", currency: "GBP", symbol: "£", locale: "en-GB", tax: { mode: "vat", rate: 0.20 }, payments: ["stripe", "paypal", "klarna", "cod"], shipping: ["house-std", "royalmail", "dhl"] },
  DE: { name: "Germany", currency: "EUR", symbol: "€", locale: "de-DE", tax: { mode: "vat", rate: 0.19 }, payments: ["stripe", "paypal", "klarna", "ideal", "cod"], shipping: ["house-std", "dhl", "deutschepost"] },
  FR: { name: "France", currency: "EUR", symbol: "€", locale: "fr-FR", tax: { mode: "vat", rate: 0.20 }, payments: ["stripe", "paypal", "klarna"], shipping: ["house-std", "dhl"] },
  NL: { name: "Netherlands", currency: "EUR", symbol: "€", locale: "nl-NL", tax: { mode: "vat", rate: 0.21 }, payments: ["ideal", "paypal", "klarna"], shipping: ["house-std", "dhl", "deutschepost"] },
  BR: { name: "Brazil", currency: "BRL", symbol: "R$", locale: "pt-BR", tax: { mode: "manual", rate: 0.17 }, payments: ["pix", "paypal", "cod"], shipping: ["house-std", "correios"] },
  KE: { name: "Kenya", currency: "KES", symbol: "KSh", locale: "en-KE", tax: { mode: "vat", rate: 0.16 }, payments: ["mpesa", "paypal", "cod"], shipping: ["house-std"] },
  AE: { name: "UAE", currency: "AED", symbol: "د.إ", locale: "ar-AE", tax: { mode: "vat", rate: 0.05 }, payments: ["tabby", "stripe", "cod"], shipping: ["house-std", "dhl"] },
  JP: { name: "Japan", currency: "JPY", symbol: "¥", locale: "ja-JP", tax: { mode: "manual", rate: 0.10 }, payments: ["stripe", "paypal", "alipay"], shipping: ["house-std"] },
  SG: { name: "Singapore", currency: "SGD", symbol: "S$", locale: "en-SG", tax: { mode: "gst", rate: 0.09 }, payments: ["stripe", "paypal", "alipay"], shipping: ["house-std", "dhl"] },
  AU: { name: "Australia", currency: "AUD", symbol: "A$", locale: "en-AU", tax: { mode: "gst", rate: 0.10 }, payments: ["stripe", "paypal", "square"], shipping: ["house-std", "fedex"] },
  CA: { name: "Canada", currency: "CAD", symbol: "C$", locale: "en-CA", tax: { mode: "manual", rate: 0.13 }, payments: ["stripe", "paypal", "square"], shipping: ["house-std", "ups", "fedex"] }
};

/* ---------------- currencies (seed data; DB table is source of truth at runtime) ---- */
/* usd = value of 1 unit in USD */
const CURRENCIES = [
  { code: "USD", name: "US Dollar", symbol: "$", decimals: 2, usd: 1 },
  { code: "EUR", name: "Euro", symbol: "€", decimals: 2, usd: 1.08 },
  { code: "GBP", name: "British Pound", symbol: "£", decimals: 2, usd: 1.27 },
  { code: "INR", name: "Indian Rupee", symbol: "₹", decimals: 2, usd: 0.012 },
  { code: "JPY", name: "Japanese Yen", symbol: "¥", decimals: 0, usd: 0.0067 },
  { code: "AED", name: "UAE Dirham", symbol: "د.إ", decimals: 2, usd: 0.2723 },
  { code: "BRL", name: "Brazilian Real", symbol: "R$", decimals: 2, usd: 0.19 },
  { code: "KES", name: "Kenyan Shilling", symbol: "KSh", decimals: 2, usd: 0.0078 },
  { code: "SGD", name: "Singapore Dollar", symbol: "S$", decimals: 2, usd: 0.74 },
  { code: "AUD", name: "Australian Dollar", symbol: "A$", decimals: 2, usd: 0.66 },
  { code: "CAD", name: "Canadian Dollar", symbol: "C$", decimals: 2, usd: 0.73 },
  { code: "CHF", name: "Swiss Franc", symbol: "CHF", decimals: 2, usd: 1.12 },
  { code: "CNY", name: "Chinese Yuan", symbol: "¥", decimals: 2, usd: 0.14 },
  { code: "SAR", name: "Saudi Riyal", symbol: "﷼", decimals: 2, usd: 0.267 },
  { code: "SEK", name: "Swedish Krona", symbol: "kr", decimals: 2, usd: 0.095 },
  { code: "ZAR", name: "South African Rand", symbol: "R", decimals: 2, usd: 0.055 },
  { code: "MXN", name: "Mexican Peso", symbol: "Mex$", decimals: 2, usd: 0.058 },
  { code: "TRY", name: "Turkish Lira", symbol: "₺", decimals: 2, usd: 0.03 },
  { code: "NGN", name: "Nigerian Naira", symbol: "₦", decimals: 2, usd: 0.00065 },
  { code: "NZD", name: "New Zealand Dollar", symbol: "NZ$", decimals: 2, usd: 0.61 }
];

/* ---------------- payment providers ---------------- */
const CARD_FIELDS = [
  { key: "publishableKey", label: "Publishable key" },
  { key: "secretKey", label: "Secret key", secret: true },
  { key: "webhookSecret", label: "Webhook signing secret", secret: true }
];
const PAYMENT_PROVIDERS = [
  { id: "stripe", name: "Stripe", emoji: "💳", countries: ["US", "GB", "DE", "FR", "JP", "SG", "AU", "CA"], methods: ["card", "apple_pay", "google_pay"], feePct: 2.9, feeFixed: 0.30, fields: CARD_FIELDS, desc: "Cards, wallets & global payments" },
  { id: "paypal", name: "PayPal", emoji: "🅿️", countries: ["*"], methods: ["paypal", "card"], feePct: 3.49, feeFixed: 0.49, fields: [{ key: "clientId", label: "Client ID" }, { key: "secret", label: "Secret", secret: true }], desc: "Wallet & checkout worldwide" },
  { id: "square", name: "Square", emoji: "⬛", countries: ["US", "GB", "AU", "CA", "JP"], methods: ["card", "afterpay"], feePct: 2.6, feeFixed: 0.10, fields: [{ key: "appId", label: "Square App ID" }, { key: "token", label: "Access token", secret: true }], desc: "Cards & buy-now-pay-later" },
  { id: "braintree", name: "Braintree (PayPal)", emoji: "🧩", countries: ["US", "GB", "AU", "CA"], methods: ["card", "paypal", "venmo"], feePct: 2.59, feeFixed: 0.49, fields: [{ key: "merchantId", label: "Merchant ID" }, { key: "publicKey", label: "Public key" }, { key: "privateKey", label: "Private key", secret: true }], desc: "Enterprise card processing" },
  { id: "adyen", name: "Adyen", emoji: "🟢", countries: ["*"], methods: ["card", "ideal", "klarna", "wechatpay"], feePct: 2.6, feeFixed: 0.12, fields: [{ key: "apiKey", label: "API key", secret: true }, { key: "merchantAccount", label: "Merchant account" }], desc: "Global omnichannel acquiring" },
  { id: "razorpay", name: "Razorpay", emoji: "⚡", countries: ["IN"], methods: ["card", "upi", "netbanking", "wallet"], feePct: 2.0, feeFixed: 0, fields: [{ key: "keyId", label: "Key ID" }, { key: "keySecret", label: "Key secret", secret: true }], desc: "India's payments stack — UPI, cards, netbanking" },
  { id: "upi", name: "UPI", emoji: "📱", countries: ["IN"], methods: ["upi"], feePct: 0, feeFixed: 0, fields: [], desc: "Unified Payments Interface — zero MDR" },
  { id: "paytm", name: "Paytm", emoji: "🔵", countries: ["IN"], methods: ["wallet", "upi", "card"], feePct: 1.8, feeFixed: 0, fields: [{ key: "merchantId", label: "Merchant ID" }, { key: "apiKey", label: "API key", secret: true }], desc: "Wallets & UPI" },
  { id: "pix", name: "PIX", emoji: "🔎", countries: ["BR"], methods: ["pix"], feePct: 0.99, feeFixed: 0, fields: [{ key: "clientId", label: "Client ID" }, { key: "clientSecret", label: "Client secret", secret: true }], desc: "Brazil's instant payment rail" },
  { id: "ideal", name: "iDEAL", emoji: "🟠", countries: ["NL"], methods: ["bank_transfer"], feePct: 0.8, feeFixed: 0.35, fields: [{ key: "merchantId", label: "Merchant ID" }], desc: "Dutch online bank transfer" },
  { id: "klarna", name: "Klarna", emoji: "🩷", countries: ["GB", "DE", "NL", "FR", "SE"], methods: ["bnpl", "pay_now"], feePct: 3.29, feeFixed: 0.50, fields: [{ key: "country", label: "Klarna country" }, { key: "apiKey", label: "API key", secret: true }], desc: "Buy now, pay later" },
  { id: "mpesa", name: "M-Pesa", emoji: "📲", countries: ["KE"], methods: ["mobile_money"], feePct: 1.5, feeFixed: 0, fields: [{ key: "shortcode", label: "Paybill shortcode" }, { key: "apikey", label: "API key", secret: true }], desc: "Mobile money in East Africa" },
  { id: "tabby", name: "Tabby", emoji: "🟪", countries: ["AE", "SA"], methods: ["bnpl"], feePct: 4.5, feeFixed: 0, fields: [{ key: "publicKey", label: "Public key" }, { key: "secretKey", label: "Secret key", secret: true }], desc: "Split-in-4 payments, MENA" },
  { id: "alipay", name: "Alipay+", emoji: "🔷", countries: ["CN", "SG", "JP"], methods: ["wallet", "qr"], feePct: 2.2, feeFixed: 0, fields: [{ key: "appId", label: "App ID" }, { key: "privateKey", label: "Private key", secret: true }], desc: "APAC wallets & QR" },
  { id: "cod", name: "Cash on Delivery", emoji: "💵", countries: ["*"], methods: ["cod"], feePct: 0, feeFixed: 0, fields: [], desc: "Pay at the doorstep" },
  { id: "bank", name: "Bank Transfer / NEFT", emoji: "🏦", countries: ["*"], methods: ["bank_transfer"], feePct: 0, feeFixed: 0, fields: [{ key: "account", label: "Settlement account" }], desc: "Direct bank transfer" }
];

/* ---------------- shipping providers ---------------- */
const SHIPPING_PROVIDERS = [
  { id: "house-std", name: "House Standard", emoji: "📦", countries: ["*"], eta: [3, 5], baseFee: 0, freeOver: 35, desc: "Complimentary over threshold" },
  { id: "house-exp", name: "House Express", emoji: "⚡", countries: ["*"], eta: [1, 2], baseFee: 9.99, freeOver: 0, desc: "Priority next-day" },
  { id: "fedex", name: "FedEx", emoji: "🟣", countries: ["US", "CA", "AU", "SG"], eta: [1, 3], baseFee: 12.5, freeOver: 0 },
  { id: "ups", name: "UPS", emoji: "🟤", countries: ["US", "CA", "GB", "DE"], eta: [2, 4], baseFee: 10.9, freeOver: 0 },
  { id: "usps", name: "USPS", emoji: "🦅", countries: ["US"], eta: [2, 5], baseFee: 5.5, freeOver: 0 },
  { id: "dhl", name: "DHL Express", emoji: "🟡", countries: ["*"], eta: [1, 3], baseFee: 14.9, freeOver: 0 },
  { id: "royalmail", name: "Royal Mail", emoji: "👑", countries: ["GB"], eta: [2, 4], baseFee: 6.2, freeOver: 0 },
  { id: "deutschepost", name: "Deutsche Post", emoji: "🏤", countries: ["DE", "NL", "FR"], eta: [2, 4], baseFee: 5.9, freeOver: 0 },
  { id: "delhivery", name: "Delhivery", emoji: "🇮🇳", countries: ["IN"], eta: [2, 5], baseFee: 49, freeOver: 0 },
  { id: "bluedart", name: "BlueDart", emoji: "🔷", countries: ["IN"], eta: [1, 3], baseFee: 89, freeOver: 0 },
  { id: "correios", name: "Correios", emoji: "🇧🇷", countries: ["BR"], eta: [3, 8], baseFee: 18, freeOver: 0 }
];

/* ---------------- notification providers ---------------- */
const NOTIFICATION_PROVIDERS = [
  { id: "log", name: "Console (dev)", emoji: "🖥️", countries: ["*"], fields: [], desc: "Writes to server log — always available" },
  { id: "smtp", name: "SMTP Email", emoji: "✉️", countries: ["*"], fields: [{ key: "host", label: "Host" }, { key: "port", label: "Port" }, { key: "user", label: "User" }, { key: "pass", label: "Password", secret: true }, { key: "from", label: "From address" }] },
  { id: "sendgrid", name: "SendGrid", emoji: "📤", countries: ["*"], fields: [{ key: "apiKey", label: "API key", secret: true }, { key: "from", label: "From address" }] },
  { id: "mailrelay", name: "Cloud Email Relay", emoji: "🅂", countries: ["*"], fields: [{ key: "region", label: "Region" }, { key: "key", label: "Access key" }, { key: "secret", label: "Secret", secret: true }, { key: "from", label: "From address" }] },
  { id: "twilio", name: "Twilio SMS", emoji: "💬", countries: ["*"], fields: [{ key: "sid", label: "Account SID" }, { key: "token", label: "Auth token", secret: true }, { key: "from", label: "From number" }] },
  { id: "whatsapp", name: "WhatsApp Business", emoji: "🟩", countries: ["*"], fields: [{ key: "phoneId", label: "Phone number ID" }, { key: "token", label: "Access token", secret: true }] }
];

/* ---------------- tax providers ---------------- */
const TAX_PROVIDERS = [
  { id: "manual", name: "Manual rate", desc: "Flat percentage configured by the store" },
  { id: "gst", name: "GST (India)", desc: "Goods & Services Tax" },
  { id: "vat", name: "VAT", desc: "Value Added Tax" },
  { id: "avalara", name: "Avalara", desc: "Automated global tax engine", fields: [{ key: "licenseKey", label: "License key", secret: true }] }
];

/* ---------------- declarative integration SPECS (data, not code) ----------------
   Each entry is a "fill-in-the-blanks" request description the spec engine executes.
   Adding/changing a provider's protocol is editing this data (or a custom provider's
   manifest), never JavaScript. amountCents = amount*100 helper is provided by the engine. */
const PROVIDER_SPECS = {
  /* payments */
  "payment:stripe": { method: "POST", url: "https://api.stripe.com/v1/payment_intents", form: true, auth: { type: "basic", user: "{{cfg.apiKey}}", pass: "" }, idempotencyHeader: "Idempotency-Key", body: { amount: "{{amountCents}}", currency: "{{currency}}", "automatic_payment_methods[enabled]": "true" }, idPath: "id", statusPath: "status", statusMap: { succeeded: "captured", requires_capture: "pending", processing: "pending" }, errorPath: "error.message" },
  "payment:razorpay": { method: "POST", url: "https://api.razorpay.com/v1/orders", auth: { type: "basic", user: "{{cfg.keyId}}", pass: "{{cfg.keySecret}}" }, body: { amount: "{{amountCents}}", currency: "{{currency}}", receipt: "{{idempotency}}" }, idPath: "id", statusPath: "status", okStatus: "pending", errorPath: "error.description" },
  "payment:paypal": { token: { url: "https://api-m.{{cfg.env}}paypal.com/v1/oauth2/token", form: true, auth: { type: "basic", user: "{{cfg.clientId}}", pass: "{{cfg.secret}}" }, body: { grant_type: "client_credentials" }, path: "access_token" }, method: "POST", url: "https://api-m.{{cfg.env}}paypal.com/v2/checkout/orders", auth: { type: "bearer", token: "{{token}}" }, body: { intent: "CAPTURE", purchase_units: [{ amount: { currency_code: "{{currency}}", value: "{{money}}" } }] }, idPath: "id", statusPath: "status", statusMap: { COMPLETED: "captured", CREATED: "pending" }, errorPath: "message" },
  "payment:square": { method: "POST", url: "https://connect.squareup.com/v2/payments", auth: { type: "bearer", token: "{{cfg.token}}" }, idempotencyHeader: "Idempotency-Key", body: { amount_money: { amount: "{{amountCents}}", currency: "{{currency}}" }, source_id: "{{cfg.sourceId}}" }, idPath: "payment.id", statusPath: "payment.status", statusMap: { COMPLETED: "captured", PENDING: "pending" } },
  "payment:braintree": { method: "POST", url: "https://api.braintreegateway.com:443/merchants/{{cfg.merchantId}}/transactions", auth: { type: "basic", user: "{{cfg.publicKey}}", pass: "{{cfg.privateKey}}" }, body: { transaction: { amount: "{{money}}", order_id: "{{idempotency}}", channel: "luxe" } }, idPath: "transaction.id", statusPath: "transaction.status", statusMap: { submitted_for_settlement: "captured", authorized: "pending" } },
  /* notifications */
  "notification:resend": { method: "POST", url: "https://api.resend.com/emails", auth: { type: "bearer", token: "{{cfg.apiKey}}" }, body: { from: "{{cfg.from}}", to: ["{{to}}"], subject: "{{subject}}", text: "{{text}}" }, idPath: "id" },
  "notification:sendgrid": { method: "POST", url: "https://api.sendgrid.com/v3/mail/send", auth: { type: "bearer", token: "{{cfg.apiKey}}" }, body: { personalizations: [{ to: [{ email: "{{to}}" }] }], from: { email: "{{cfg.from}}" }, subject: "{{subject}}", content: [{ type: "text/plain", value: "{{text}}" }] } },
  "notification:twilio": { method: "POST", url: "https://api.twilio.com/2010-04-01/Accounts/{{cfg.accountSid}}/Messages.json", form: true, auth: { type: "basic", user: "{{cfg.accountSid}}", pass: "{{cfg.authToken}}" }, body: { To: "{{to}}", From: "{{cfg.from}}", Body: "{{subject}} {{text}}" }, idPath: "sid" },
  /* marketing (fill-in-the-blanks; execute → /api/marketing) */
  "marketing:meta": { method: "POST", url: "https://graph.facebook.com/v21.0/{{cfg.adAccountId}}/activities", auth: { type: "apikey", header: "Authorization", value: "Bearer {{cfg.accessToken}}" }, body: { event: "custom_update", user_data: { em: ["{{payload.hash}}"] }, custom_data: { currency: "{{payload.currency}}", value: "{{payload.value}}" }, action_source: "website" }, okStatus: "captured" },
  "marketing:google-ads": { method: "POST", url: "https://googleads.googleapis.com/v18/customers/{{cfg.customerId}}:uploadConversionActions:upload", form: false, auth: { type: "bearer", token: "{{cfg.accessToken}}" }, body: { conversionActions: [{ conversionAction: "customers/{{cfg.customerId}}/conversionActions/{{cfg.conversionActionId}}", gclid: "{{payload.gclid}}", conversionDateTime: "{{iso}}", value: "{{payload.value}}", currencyCode: "{{payload.currency}}" }] }, okStatus: "captured" },
  "marketing:ga4": { method: "POST", url: "https://www.google-analytics.com/mp/collect?measurement_id={{cfg.measurementId}}&api_secret={{cfg.apiSecret}}", body: { client_id: "{{payload.clientId}}", events: [{ name: "{{payload.event}}", params: { value: "{{payload.value}}" } }] }, okStatus: "captured" },
  "marketing:tiktok": { method: "POST", url: "https://business-api.tiktok.com/open_api/v1.3/event/track/", auth: { type: "apikey", header: "Access-Token", value: "{{cfg.accessToken}}" }, body: { event_source: "web", event_source_id: "{{cfg.pixelId}}", user: { email: "{{payload.hash}}" }, events: [{ event: "{{payload.event}}", event_time: "{{ts}}", channel: "web", properties: { value: "{{payload.value}}" } }] }, okStatus: "captured" }
};

const MARKETING_PROVIDERS = [
  { id: "meta", name: "Meta (Facebook/Instagram)", emoji: "📘", countries: ["*"], fields: [{ key: "adAccountId", label: "Ad Account ID" }, { key: "accessToken", label: "Access token", secret: true }], desc: "Server-side conversions API (CAPI)" },
  { id: "google-ads", name: "Google Ads", emoji: "🔍", countries: ["*"], fields: [{ key: "customerId", label: "Customer ID" }, { key: "conversionActionId", label: "Conversion action ID" }, { key: "accessToken", label: "OAuth token", secret: true }], desc: "Enhanced conversions / offline upload" },
  { id: "ga4", name: "Google Analytics 4", emoji: "📊", countries: ["*"], fields: [{ key: "measurementId", label: "Measurement ID" }, { key: "apiSecret", label: "API secret", secret: true }], desc: "Measurement Protocol events" },
  { id: "tiktok", name: "TikTok", emoji: "🎵", countries: ["*"], fields: [{ key: "pixelId", label: "Pixel ID" }, { key: "accessToken", label: "Access token", secret: true }], desc: "Events API conversions" }
];

function supports(provider, country) {
  return provider.countries.includes("*") || provider.countries.includes(country);
}
function countryProfile(code) {
  const c = COUNTRIES[code] || COUNTRIES.US;
  return {
    code, ...c,
    payments: PAYMENT_PROVIDERS.filter(p => c.payments.includes(p.id)),
    shipping: SHIPPING_PROVIDERS.filter(s => c.shipping.includes(s.id))
  };
}
function paymentProvider(id, customs) {
  return (customs || []).concat(PAYMENT_PROVIDERS).find(p => p.id === id);
}

module.exports = { COUNTRIES, CURRENCIES, PAYMENT_PROVIDERS, SHIPPING_PROVIDERS, NOTIFICATION_PROVIDERS, TAX_PROVIDERS, MARKETING_PROVIDERS, PROVIDER_SPECS, supports, countryProfile, paymentProvider };
