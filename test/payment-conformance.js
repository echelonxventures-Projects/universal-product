/* LUXORA Platform — payment provider conformance, one provider spec at a time, against a stand-in
   transport (no server, no database, no network). Each spec is read from lib/seed/providers.json —
   the data the platform runs — and checked for what its provider expects of a payment, a status
   lookup, a full and a partial refund, and its webhooks: the request's shape and signature, the
   amount in the currency's minor unit, states mapped by meaning (an unknown state is never money
   received), a forged webhook refused, and one delivery identified as one event.
   Built from each provider's published integration documents: passing here is NOT sandbox
   evidence (PRODUCTION_READINESS.md PR-050) — the field names are data and can be corrected from a
   sandbox run without a code change. */
"use strict";
const crypto = require("crypto");
const path = require("path"), fs = require("fs");
/* a status lookup reads the payment machine's tags: from a throwaway database, never the dev one */
const DB = path.join(__dirname, "payment-conformance.db");
for (const x of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + x, { force: true }); } catch (e) { } }
process.env.LX_DB = DB;
{ const say = console.log; console.log = () => { }; require("../lib/db.js"); console.log = say; }
const spec = require("../lib/spec.js");
const connect = require("../lib/connect.js");
const SPECS = require("../lib/seed/providers.json").PROVIDER_SPECS;
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const sha = v => crypto.createHash("sha256").update(v).digest("hex");
const b64 = o => Buffer.from(JSON.stringify(o)).toString("base64");
const unb64 = s => JSON.parse(Buffer.from(s, "base64").toString("utf8"));

/* the stand-in: each test sets the replies by URL and reads back what was sent */
let calls = [], replies = {};
connect.__setTransport((url, o) => {
  let body = o.body; try { body = JSON.parse(o.body); } catch (e) { body = Object.fromEntries(new URLSearchParams(o.body || "")); }
  calls.push({ url, method: o.method, headers: o.headers, body, raw: o.body });
  const r = Object.entries(replies).find(([k]) => url === k || url.startsWith(k));
  const [status, json] = r ? r[1] : [404, { message: "unexpected " + url }];
  return Promise.resolve({ ok: status < 300, status, text: async () => JSON.stringify(json) });
});
/* INR has two decimals: 1,234.50 is 123450 paise — passed explicitly so no database is read */
const pay = (provider, config, extra) => connect.pay({ provider, spec: SPECS["payment:" + provider], config, amount: "1234.50", currency: "INR", decimals: 2, idempotency: "LX-1001", extra: Object.assign({ returnUrl: "https://shop.example/orders.html?paid=LX-1001" }, extra || {}) });
const refund = (provider, config, amount, paymentId) => connect.refund({ provider, spec: SPECS["payment:" + provider], config, amount, currency: "INR", decimals: 2, paymentId, idempotency: "refund-7-3" });
const lookup = (provider, config, ref) => connect.lookup({ provider, spec: SPECS["payment:" + provider], config, ref, currency: "INR", decimals: 2, idempotency: "capture-7" });
const hookOk = (provider, secret, raw, headers) => spec.verifyHmac(SPECS["payment:" + provider].webhook.signature, secret, raw, headers, "");
const event = (provider, raw, headers) => spec.webhookEvent(SPECS["payment:" + provider], JSON.parse(raw), headers || {});

(async () => {
  try {
    console.log("▸ RAZORPAY — refunds and disputes added to its order, lookup and capture rules");
    {
      const cfg = { keyId: "rzp_k", keySecret: "rzp_s" };
      const auth = "Basic " + Buffer.from("rzp_k:rzp_s").toString("base64");
      replies = { "https://api.razorpay.com/v1/payments/pay_1/refund": [200, { id: "rfnd_1", entity: "refund", amount: 25050, payment_id: "pay_1", status: "processed" }] };
      calls = [];
      const r = await refund("razorpay", cfg, "250.50", "pay_1");
      const c = calls[0] || {};
      ok(c.url === "https://api.razorpay.com/v1/payments/pay_1/refund" && c.method === "POST" && c.headers.Authorization === auth, "a refund is posted against the provider's payment id with the store's key", c.url);
      ok(c.body && c.body.amount === 25050 && c.body.receipt === "refund-7-3", "a partial refund sends its exact amount in paise and its own receipt", c.body);
      ok(r.live && r.ok && r.id === "rfnd_1" && r.status === "refunded", "a processed refund is reported refunded with the provider's refund id", r);
      replies = { "https://api.razorpay.com/v1/payments/pay_1/refund": [200, { id: "rfnd_2", status: "pending" }] };
      ok((await refund("razorpay", cfg, "1", "pay_1")).status === "refund_pending", "a pending refund is pending, not refunded");
      replies = { "https://api.razorpay.com/v1/payments/pay_1/refund": [400, { error: { code: "BAD_REQUEST_ERROR", description: "The refund amount provided is greater than amount captured" } }] };
      const no = await refund("razorpay", cfg, "99999", "pay_1");
      ok(no.live && !no.ok && no.status === "failed" && /greater than amount captured/.test(no.error), "a refusal is a failure with the provider's reason", no);
      ok((await refund("razorpay", { keyId: "rzp_k" }, "1", "pay_1")).live === false, "without the secret key nothing is sent");

      const secret = "rzp_whsec";
      const refundEvt = JSON.stringify({ event: "refund.processed", payload: { refund: { entity: { id: "rfnd_1", amount: 25050, payment_id: "pay_1", status: "processed" } }, payment: { entity: { id: "pay_1" } } } });
      const sig = k => ({ "x-razorpay-signature": crypto.createHmac("sha256", k).update(refundEvt).digest("hex"), "x-razorpay-event-id": "evt_rf_1" });
      ok(hookOk("razorpay", secret, refundEvt, sig(secret)) === true && hookOk("razorpay", secret, refundEvt, sig("wrong")) === false, "a refund webhook verifies only with the signing secret");
      const e = event("razorpay", refundEvt, sig(secret));
      ok(e && e.status === "refunded" && e.paymentId === "pay_1" && e.ref === null && e.refundId === "rfnd_1" && e.amountMeaning === "refund" && spec.eventMinor(e, "INR") === 25050 && e.id === "evt_rf_1", "refund.processed is one refund, by id, of the named payment", e);
      const dsp = (type, status) => JSON.stringify({ event: type, payload: { payment: { entity: { id: "pay_1" } }, dispute: { entity: { id: "disp_1", amount: 123450, reason_code: "chargeback", status } } } });
      const d1 = event("razorpay", dsp("payment.dispute.created", "open"), { "x-razorpay-event-id": "evt_d1" });
      ok(d1 && d1.dispute === "opened" && d1.disputeId === "disp_1" && d1.paymentId === "pay_1" && d1.reason === "chargeback" && spec.eventMinor(d1, "INR") === 123450, "a dispute opens against the payment with the provider's amount and reason", d1);
      ok(["won", "lost", "closed"].every(x => (event("razorpay", dsp("payment.dispute." + x, x)) || {}).dispute === x), "won, lost and closed disputes are mapped");
      ok(event("razorpay", JSON.stringify({ event: "refund.failed", payload: { refund: { entity: { id: "rfnd_9", payment_id: "pay_1" } } } })) === null, "a failed refund event changes no payment (the refund's own outcome stands)");
      ok(event("razorpay", JSON.stringify({ event: "payment.failed", payload: { payment: { entity: { id: "pay_x", order_id: "order_1" } } } })) === null, "one failed attempt does not fail an order the shopper can still pay");
    }

    console.log("▸ PHONEPE — the current checkout API (OAuth client credentials)");
    {
      const cfg = { clientId: "PP_CLIENT", clientSecret: "pp_secret", clientVersion: "1", authBase: "https://pp.example/apis/identity-manager", apiBase: "https://pp.example/apis/pg" };
      const tokenUrl = "https://pp.example/apis/identity-manager/v1/oauth/token";
      replies = { [tokenUrl]: [200, { access_token: "pp_tok", expires_at: 1 }], "https://pp.example/apis/pg/checkout/v2/pay": [200, { orderId: "OMO123", state: "PENDING", expireAt: 1, redirectUrl: "https://pp.example/checkout/OMO123" }] };
      calls = [];
      const r = await pay("phonepe", cfg);
      const [tk, c] = calls;
      ok(tk && tk.url === tokenUrl && tk.body.client_id === "PP_CLIENT" && tk.body.client_secret === "pp_secret" && tk.body.client_version === "1" && tk.body.grant_type === "client_credentials", "a token is obtained with the client credentials first", tk && tk.body);
      ok(c && c.url === "https://pp.example/apis/pg/checkout/v2/pay" && c.headers.Authorization === "O-Bearer pp_tok", "the payment is created with the O-Bearer token", c && c.headers);
      ok(c && c.body.merchantOrderId === "LX-1001" && c.body.amount === 123450 && c.body.paymentFlow.type === "PG_CHECKOUT" && c.body.paymentFlow.merchantUrls.redirectUrl === "https://shop.example/orders.html?paid=LX-1001", "it asks for the exact amount in paise under the order number and returns the shopper to the store", c && c.body);
      ok(r.ok && r.id === "LX-1001" && r.status === "pending" && r.redirect === "https://pp.example/checkout/OMO123", "the payment waits under the merchant's own reference and sends the shopper to PhonePe", r);
      ok((await pay("phonepe", Object.assign({}, cfg, { clientSecret: "" }))).live === false, "without the client secret nothing is sent");

      replies = { [tokenUrl]: [200, { access_token: "pp_tok" }], "https://pp.example/apis/pg/checkout/v2/order/LX-1001/status": [200, { orderId: "OMO123", state: "COMPLETED", amount: 123450 }] };
      calls = [];
      const lk = await lookup("phonepe", cfg, "LX-1001");
      ok(lk.ok && lk.status === "captured" && Number(lk.amount) === 123450 && lk.paymentId === "LX-1001" && calls[1].method === "GET", "a status lookup of a completed order is captured, with its amount", lk);
      replies[ "https://pp.example/apis/pg/checkout/v2/order/LX-1001/status"] = [200, { state: "SOMETHING_NEW" }];
      ok((await lookup("phonepe", cfg, "LX-1001")).status === "pending", "a state the spec does not name is pending, never captured");

      replies = { [tokenUrl]: [200, { access_token: "pp_tok" }], "https://pp.example/apis/pg/payments/v2/refund": [200, { refundId: "OMR1", amount: 25050, state: "PENDING" }] };
      calls = [];
      const rf = await refund("phonepe", cfg, "250.50", "LX-1001");
      ok(calls[1] && calls[1].body.merchantRefundId === "refund-7-3" && calls[1].body.originalMerchantOrderId === "LX-1001" && calls[1].body.amount === 25050, "a partial refund names the original order, its own id and the exact amount", calls[1] && calls[1].body);
      ok(rf.ok && rf.id === "OMR1" && rf.status === "refund_pending", "an accepted refund is pending until PhonePe completes it", rf);

      const creds = "merchant_user:merchant_pass";
      const done = JSON.stringify({ event: "checkout.order.completed", payload: { orderId: "OMO123", merchantOrderId: "LX-1001", state: "COMPLETED", amount: 123450 } });
      ok(hookOk("phonepe", creds, done, { authorization: sha(creds) }) === true, "a webhook carrying sha256 of the merchant's webhook credentials verifies");
      ok(hookOk("phonepe", creds, done, { authorization: sha("merchant_user:other") }) === false && hookOk("phonepe", creds, done, {}) === false, "other credentials, or none, are refused");
      const e = event("phonepe", done);
      ok(e && e.status === "captured" && e.ref === "LX-1001" && e.paymentId === "LX-1001" && spec.eventMinor(e, "INR") === 123450, "a completed order captures its payment for its exact amount", e);
      ok(e && e.id === event("phonepe", done).id && e.id !== (event("phonepe", JSON.stringify({ event: "checkout.order.failed", payload: { merchantOrderId: "LX-1001", state: "FAILED" } })) || {}).id, "PhonePe sends no event id: one delivery is identified by its event, order and state", e && e.id);
      const rdone = event("phonepe", JSON.stringify({ event: "pg.refund.completed", payload: { originalMerchantOrderId: "LX-1001", merchantRefundId: "refund-7-3", refundId: "OMR1", state: "COMPLETED", amount: 25050 } }));
      ok(rdone && rdone.status === "refunded" && rdone.ref === null && rdone.paymentId === "LX-1001" && rdone.refundId === "OMR1" && rdone.amountMeaning === "refund", "a completed refund is one refund, by id, of the original order", rdone);
    }

    console.log("▸ PHONEPE — the older salt-key API (base64 request, X-VERIFY)");
    {
      const cfg = { merchantId: "M_TEST", saltKey: "salt-abc", saltIndex: "1", apiBase: "https://pp.example/apis/hermes", callbackUrl: "https://shop.example/api/webhooks/inbound/phonepe-legacy" };
      replies = { "https://pp.example/apis/hermes/pg/v1/pay": [200, { success: true, code: "PAYMENT_INITIATED", data: { merchantId: "M_TEST", merchantTransactionId: "LX-1001", instrumentResponse: { type: "PAY_PAGE", redirectInfo: { url: "https://pp.example/pay/LX-1001", method: "GET" } } } }] };
      calls = [];
      const r = await pay("phonepe-legacy", cfg);
      const c = calls[0] || {};
      const inner = c.body && c.body.request ? unb64(c.body.request) : {};
      ok(c.url === "https://pp.example/apis/hermes/pg/v1/pay" && Object.keys(c.body || {}).join() === "request", "the request travels base64-encoded in one field", c.body);
      ok(inner.merchantId === "M_TEST" && inner.merchantTransactionId === "LX-1001" && inner.amount === 123450 && inner.callbackUrl === cfg.callbackUrl && inner.paymentInstrument.type === "PAY_PAGE", "the encoded request carries the exact amount in paise under the order number", inner);
      ok(c.headers["X-VERIFY"] === sha(c.body.request + "/pg/v1/pay" + "salt-abc") + "###1", "X-VERIFY is sha256(request + path + salt key) and the salt index", c.headers["X-VERIFY"]);
      ok(r.ok && r.id === "LX-1001" && r.status === "pending" && r.redirect === "https://pp.example/pay/LX-1001", "an initiated payment waits and sends the shopper to PhonePe", r);

      replies = { "https://pp.example/apis/hermes/pg/v1/status/M_TEST/LX-1001": [200, { success: true, code: "PAYMENT_SUCCESS", data: { merchantTransactionId: "LX-1001", transactionId: "T1", amount: 123450, state: "COMPLETED" } }] };
      calls = [];
      const lk = await lookup("phonepe-legacy", cfg, "LX-1001");
      ok(calls[0].headers["X-VERIFY"] === sha("/pg/v1/status/M_TEST/LX-1001" + "salt-abc") + "###1" && calls[0].headers["X-MERCHANT-ID"] === "M_TEST" && calls[0].method === "GET", "the status call is signed over its path, with the merchant id header", calls[0].headers);
      ok(lk.ok && lk.status === "captured" && Number(lk.amount) === 123450 && lk.paymentId === "LX-1001", "a successful transaction is captured, with its amount", lk);

      replies = { "https://pp.example/apis/hermes/pg/v1/refund": [200, { success: true, code: "PAYMENT_PENDING", data: { transactionId: "TR1", amount: 25050 } }] };
      calls = [];
      const rf = await refund("phonepe-legacy", cfg, "250.50", "LX-1001");
      const rin = calls[0] && calls[0].body.request ? unb64(calls[0].body.request) : {};
      ok(rin.originalTransactionId === "LX-1001" && rin.merchantTransactionId === "refund-7-3" && rin.amount === 25050 && calls[0].headers["X-VERIFY"] === sha(calls[0].body.request + "/pg/v1/refund" + "salt-abc") + "###1", "a partial refund is encoded, signed, names the original transaction and sends the exact amount", rin);
      ok(rf.ok && rf.id === "TR1" && rf.status === "refund_pending", "a pending refund stays pending", rf);

      const decoded = { success: true, code: "PAYMENT_SUCCESS", data: { merchantId: "M_TEST", merchantTransactionId: "LX-1001", transactionId: "T1", amount: 123450, state: "COMPLETED" } };
      const response = b64(decoded), raw = JSON.stringify({ response });
      ok(hookOk("phonepe-legacy", "salt-abc", raw, { "x-verify": sha(response + "salt-abc") + "###1" }) === true, "a callback verifies with sha256(response + salt key)");
      ok(hookOk("phonepe-legacy", "salt-abc", raw, { "x-verify": sha(response + "other") + "###1" }) === false && hookOk("phonepe-legacy", "salt-abc", JSON.stringify({ response: b64(Object.assign({}, decoded, { data: Object.assign({}, decoded.data, { amount: 1 }) })) }), { "x-verify": sha(response + "salt-abc") + "###1" }) === false, "another salt, or a changed body, is refused");
      const e = event("phonepe-legacy", raw);
      ok(e && e.status === "captured" && e.ref === "LX-1001" && e.paymentId === "LX-1001" && spec.eventMinor(e, "INR") === 123450 && e.id === "PAYMENT_SUCCESS:LX-1001:T1", "the decoded callback captures its transaction for its exact amount, identified once", e);
      ok(event("phonepe-legacy", JSON.stringify({ response: "not base64 json" })) === null, "an undecodable callback is ignored");
      ok((event("phonepe-legacy", JSON.stringify({ response: b64({ code: "PAYMENT_ERROR", data: { merchantTransactionId: "LX-1001" } }) })) || {}).status === "failed", "a failed transaction is failed");
    }

    console.log("▸ EVERY PAYMENT SPEC VALIDATES");
    {
      for (const [k, s] of Object.entries(SPECS).filter(([k]) => k.startsWith("payment:"))) {
        const blocks = [["pay", s], ["lookup", s.lookup], ["refund", s.refund]].filter(b => b[1]);
        ok(blocks.every(([, b]) => spec.validate(b) === null), k + ": every block it declares validates (" + blocks.map(b => b[0]).join(", ") + ")");
      }
    }
  } catch (e) { failed++; console.log("  ✗ FATAL " + (e && e.stack || e)); }
  for (const x of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + x, { force: true }); } catch (e) { } }
  console.log("\n" + (failed ? "✗" : "✓") + " payment conformance: " + passed + " passed, " + failed + " failed");
  process.exit(failed ? 1 : 0);
})();
