/* LUXORA Platform — live integrations end to end, against stand-ins for Stripe and EasyPost.
   The server runs in this process so its outbound HTTP can be pointed at a fake gateway
   (connect.__setTransport): checkout creates a hosted Checkout session and hands the shopper
   its URL, the order waits for payment, only a correctly signed webhook for the right
   amount captures it (once), an expired session releases the order, and a refund is
   issued through the gateway — or refused, and the payment left as it was. Shipping rates a
   parcel through the carrier, buys only a rate this store was quoted (once), tells the
   customer, and advances tracking only on a correctly signed carrier webhook. */
"use strict";
const path = require("path");
const fs = require("fs");
const crypto = require("crypto");
const DB = path.join(__dirname, "integrations.db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
const PORT = 8876;
Object.assign(process.env, { LX_DB: DB, PORT: String(PORT), LX_LOG: "" });
delete process.env.NODE_ENV;
const BASE = `http://localhost:${PORT}`;
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const sleep = ms => new Promise(r => setTimeout(r, ms));

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
    return { status: r.status, body };
  };
  fn.jar = c;
  return fn;
};

/* ---- the stand-in gateway: Stripe's Checkout Sessions + Refunds endpoints ---- */
const calls = [];
let refundReply = { status: 200, json: { id: "re_1", status: "succeeded" } };
let n = 0;
function fakeStripe(url, o) {
  const form = Object.fromEntries(new URLSearchParams(o.body || ""));
  calls.push({ url, headers: o.headers, form });
  let status = 200, json;
  if (url === "https://api.stripe.com/v1/checkout/sessions") { n++; json = { id: "cs_test_" + n, object: "checkout.session", url: "https://checkout.stripe.com/c/pay/cs_test_" + n, status: "open", payment_status: "unpaid" }; }
  else if (url === "https://api.stripe.com/v1/refunds") { status = refundReply.status; json = refundReply.json; }
  else if (url.startsWith("https://api.stripe.com/v1/checkout/sessions/")) { const id = url.split("/").pop(); json = Object.assign({ id, object: "checkout.session" }, lookupReply(id)); }
  /* PayPal: OAuth, the webhook verify call, the order lookup and the capture */
  else if (url === "https://api-m.paypal.com/v1/oauth2/token") json = { access_token: "pp_token" };
  else if (url === "https://api-m.paypal.com/v1/notifications/verify-webhook-signature") { const b = JSON.parse(o.body); calls[calls.length - 1].json = b; json = { verification_status: b.transmission_sig === "good-sig" && b.webhook_id === "WH-1" ? "SUCCESS" : "FAILURE" }; }
  else if (url === "https://api-m.paypal.com/v2/checkout/orders/PP-ORDER-1") json = { id: "PP-ORDER-1", status: "APPROVED", purchase_units: [{ amount: { value: String(ppAmount) } }] };
  else if (url === "https://api-m.paypal.com/v2/checkout/orders/PP-ORDER-1/capture") json = { id: "PP-ORDER-1", status: "COMPLETED", purchase_units: [{ payments: { captures: [{ id: "CAP-1", amount: { value: String(ppAmount) } }] } }] };
  else if (url === "https://api.easypost.com/v2/shipments") {
    const b = JSON.parse(o.body); calls[calls.length - 1].json = b;
    json = { id: "shp_1", object: "Shipment", rates: [
      { id: "rate_ups", carrier: "UPS", service: "Ground", rate: "11.20", currency: "USD", delivery_days: 3 },
      { id: "rate_usps", carrier: "USPS", service: "GroundAdvantage", rate: "7.85", currency: "USD", delivery_days: 4 }], messages: [] };
  }
  else if (url === "https://api.easypost.com/v2/shipments/shp_1/buy") { calls[calls.length - 1].json = JSON.parse(o.body); json = { id: "shp_1", tracking_code: "9400111899223197428490", postage_label: { label_url: "https://easypost-files.s3.amazonaws.com/label.png" }, selected_rate: { id: "rate_usps" } }; }
  else { status = 404; json = { error: { message: "unexpected " + url } }; }
  return Promise.resolve({ ok: status < 300, status, text: async () => JSON.stringify(json) });
}
let lookupReply = () => ({ status: "open", payment_status: "unpaid" });
let ppAmount = 0;
const WHSEC = "whsec_test_secret";
const signed = (payload, secret, t) => { t = t || Math.floor(Date.now() / 1000); const raw = JSON.stringify(payload); return { raw, sig: `t=${t},v1=` + crypto.createHmac("sha256", secret).update(t + "." + raw).digest("hex") }; };
const hook = async (payload, secret, store) => {
  const { raw, sig } = signed(payload, secret || WHSEC);
  const r = await fetch(BASE + "/api/webhooks/inbound/stripe?store=" + (store || "luxora"), { method: "POST", headers: { "Content-Type": "application/json", "Stripe-Signature": sig }, body: raw });
  return { status: r.status, body: await r.json().catch(() => ({})) };
};
const sessionEvent = (type, cs, extra) => ({ id: "evt_" + crypto.randomBytes(4).toString("hex"), type, data: { object: Object.assign({ id: cs, object: "checkout.session", payment_status: "paid", payment_intent: "pi_" + cs.slice(3) }, extra || {}) } });

(async () => {
  const silence = console.log; console.log = () => { };
  require("../server.js");
  const connect = require("../lib/connect.js");
  const db = require("../lib/db.js");
  console.log = silence;
  connect.__setTransport(fakeStripe);
  for (let i = 0; i < 120; i++) { try { if ((await fetch(BASE + "/healthz")).ok) break; } catch (e) { } await sleep(250); }

  try {
    const A = mk(); await A("/api/session?store=luxora");
    ok((await A("/api/auth/login?store=luxora", "POST", { email: "admin@luxora.shop", password: "admin123" })).status === 200, "store admin signs in");
    const gwList = [{ id: "stripe", enabled: true, primary: true, mode: "live", config: { publishableKey: "pk_test_1", secretKey: "sk_test_live_key", webhookSecret: WHSEC } }, { id: "cod", enabled: true, mode: "sandbox", config: {} }];
    ok((await A("/api/admin/gateways?store=luxora", "PUT", { gateways: gwList })).status === 200, "Stripe is enabled live with a secret key and webhook signing secret");
    /* saving the list again as the console would — secrets come back masked — keeps them */
    const shown = (await A("/api/admin/gateways?store=luxora")).body;
    const stripeShown = (shown.enabled || shown.gateways || []).find(g => (g.id || g.provider_id) === "stripe") || {};
    const masked = Object.fromEntries(Object.keys(stripeShown.config || { secretKey: 1, webhookSecret: 1 }).map(k => [k, "••••" + k]));
    await A("/api/admin/gateways?store=luxora", "PUT", { gateways: [Object.assign({}, gwList[0], { config: Object.assign({ publishableKey: "pk_test_1" }, masked) }), gwList[1]] });

    const product = db.get("SELECT id FROM products WHERE tenant_id=1 AND lifecycle='published' AND deleted_at IS NULL AND stock > 5 ORDER BY id LIMIT 1");
    const buy = async () => {
      const C = mk(); await C("/api/session?store=luxora");
      await C("/api/auth/register?store=luxora", "POST", { name: "Pat Payer", email: "pat" + crypto.randomBytes(3).toString("hex") + "@example.com", password: "Pay-Me-Now-123" });
      await C("/api/cart?store=luxora", "POST", { id: product.id, qty: 1 });
      const co = await C("/api/checkout?store=luxora", "POST", { name: "Pat Payer", address: "1 Main St", city: "Seattle", state: "WA", zip: "98109", gateway: "stripe", carrier: "house-std" });
      return { C, co };
    };

    console.log("▸ CHECKOUT HANDS THE SHOPPER TO STRIPE AND WAITS");
    const { co } = await buy();
    const order = co.body.order || {};
    const call = calls.find(c => c.url.endsWith("/checkout/sessions"));
    ok(co.status === 200 && order.payment_status === "pending", "a live card checkout is pending, never captured on creation", co.body);
    ok(order.payment_redirect === "https://checkout.stripe.com/c/pay/cs_test_1", "the shopper is sent to the Stripe-hosted page", order.payment_redirect);
    ok(call && call.headers.Authorization === "Basic " + Buffer.from("sk_test_live_key:").toString("base64"), "the session is created with the store's secret key (kept across a masked re-save)", call && call.headers.Authorization);
    ok(call && call.form["line_items[0][price_data][unit_amount]"] === String(Math.round(order.total * 100)) && call.form["line_items[0][price_data][currency]"] === String(order.currency).toLowerCase(), "the session charges exactly the order total", call && call.form);
    ok(call && call.headers["Idempotency-Key"] === order.num && call.form.client_reference_id === order.num, "the order number is the idempotency key and the session's reference");
    ok(call && /\/orders\.html\?store=luxora&paid=/.test(call.form.success_url) && /\/checkout\.html\?/.test(call.form.cancel_url), "the shopper comes back to the store after paying or cancelling", call && [call.form.success_url, call.form.cancel_url]);
    const row = () => db.get("SELECT p.*, o.status ostatus FROM payments p JOIN orders o ON o.id=p.order_id WHERE o.num=?", order.num);
    ok(row().status === "pending" && row().ostatus === "pending_payment" && row().txn_ref === "cs_test_1", "the order waits as pending_payment against the session id", row());

    console.log("▸ ONLY A SIGNED WEBHOOK FOR THE RIGHT AMOUNT CAPTURES");
    const cents = Math.round(order.total * 100);
    const forged = await hook(sessionEvent("checkout.session.completed", "cs_test_1", { amount_total: cents }), "whsec_wrong");
    ok(forged.status === 401 && row().status === "pending", "a webhook signed with the wrong secret is refused and changes nothing", forged);
    const short = await hook(sessionEvent("checkout.session.completed", "cs_test_1", { amount_total: cents - 100 }));
    ok(row().status === "pending", "a paid event for a different amount does not capture", short.body);
    const paid = await hook(sessionEvent("checkout.session.completed", "cs_test_1", { amount_total: cents }));
    ok(paid.status === 200 && row().status === "captured" && row().ostatus === "processing", "the signed completion captures the payment and releases the order", paid.body);
    ok(row().provider_payment_id === "pi_test_1", "the payment intent is kept for refunds", row().provider_payment_id);
    const replay = await hook(sessionEvent("checkout.session.expired", "cs_test_1", {}));
    ok(replay.status === 200 && row().status === "captured", "a later or replayed event cannot undo a capture", replay.body);
    const other = await hook(sessionEvent("checkout.session.completed", "cs_test_1", { amount_total: cents }), WHSEC, "aurum");
    ok(other.status === 401 || (other.body.applied && other.body.applied.ignored !== false), "another store's secret cannot reach this store's payment", other);

    console.log("▸ AN ABANDONED PAYMENT RELEASES THE ORDER");
    const second = (await buy()).co.body.order || {};
    const row2 = () => db.get("SELECT p.*, o.status ostatus FROM payments p JOIN orders o ON o.id=p.order_id WHERE o.num=?", second.num);
    await hook(sessionEvent("checkout.session.expired", row2().txn_ref, { payment_status: "unpaid" }));
    ok(row2().status === "failed" && row2().ostatus === "cancelled", "an expired session fails the payment and cancels the order", row2());

    console.log("▸ REFUNDS GO BACK THROUGH THE GATEWAY");
    const pid = row().id;
    refundReply = { status: 400, json: { error: { message: "charge already refunded" } } };
    const refused = await A("/api/admin/payments/" + pid + "/refund?store=luxora", "POST", {});
    ok(refused.status === 502 && row().status === "captured", "a refund the gateway refuses leaves the payment captured", refused.body);
    refundReply = { status: 200, json: { id: "re_1", status: "succeeded" } };
    const before = calls.length;
    const rf = await A("/api/admin/payments/" + pid + "/refund?store=luxora", "POST", {});
    const rc = calls.slice(before).find(c => c.url.endsWith("/refunds"));
    ok(rf.status === 200 && row().status === "refunded", "an accepted refund marks the payment refunded", rf.body);
    /* each refund of a payment has its own provider key (a payment can be refunded in parts): it
       names the payment and the refund record, so a retry of that refund is deduplicated */
    const rrow = db.get("SELECT * FROM refunds WHERE payment_id=? AND status='succeeded'", pid) || {};
    ok(rc && rc.form.payment_intent === "pi_test_1" && rc.headers["Idempotency-Key"] === "refund-" + pid + "-" + rrow.id, "the refund names the payment intent, idempotently", rc && { form: rc.form, key: rc.headers["Idempotency-Key"] });
    const twice = await A("/api/admin/payments/" + pid + "/refund?store=luxora", "POST", {});
    ok(twice.status >= 400 && calls.slice(before).filter(c => c.url.endsWith("/refunds")).length === 1, "a payment is refunded once", twice.status);

    console.log("▸ PROVIDER EVENTS ARE APPLIED ONCE; REFUNDS AND CHARGEBACKS MADE AT THE PROVIDER ARE APPLIED");
    {
      const pending = async () => {
        const o = (await buy()).co.body.order || {};
        const rowOf = () => db.get("SELECT p.*, o.status ostatus FROM payments p JOIN orders o ON o.id=p.order_id WHERE o.num=?", o.num);
        return { rowOf, c: Math.round(o.total * 100) };
      };
      const captured = async () => {
        const x = await pending();
        await hook(sessionEvent("checkout.session.completed", x.rowOf().txn_ref, { amount_total: x.c }));
        return Object.assign(x, { pi: x.rowOf().provider_payment_id });
      };
      const evt = (id, type, obj) => ({ id, type, data: { object: obj } });
      const audits = (pid, action) => db.get("SELECT COUNT(*) n FROM audit_log WHERE entity='payment' AND entity_id=? AND action=?", String(pid), action).n;

      const a = await captured();
      ok(a.rowOf().status === "captured" && /^pi_/.test(a.pi || ""), "a fresh payment is captured with its payment intent", a.rowOf());
      const partial = evt("evt_part_1", "charge.refunded", { id: "ch_a", object: "charge", payment_intent: a.pi, amount: a.c, amount_refunded: a.c - 100 });
      const p1 = await hook(partial);
      /* the provider's cumulative refunded amount is applied exactly: that much is refunded, the
         rest stays refundable and the payment stays captured (PR-029) */
      ok(p1.status === 200 && p1.body.applied && p1.body.applied.partial === true && a.rowOf().status === "captured" && Number(a.rowOf().refunded_minor) === a.c - 100, "a partial refund at the provider is applied as a partial refund; the payment stays captured", [p1.body, a.rowOf().refunded_minor]);
      const p1again = await hook(partial);
      ok(p1again.body.applied && p1again.body.applied.duplicate === true && audits(a.rowOf().id, "payment.partial_refund") === 1, "the same event delivered again is acknowledged and applied once", [p1again.body, audits(a.rowOf().id, "payment.partial_refund")]);
      const full = evt("evt_full_1", "charge.refunded", { id: "ch_a", object: "charge", payment_intent: a.pi, amount: a.c, amount_refunded: a.c });
      const f1 = await hook(full);
      ok(f1.status === 200 && a.rowOf().status === "refunded", "a full refund made at the provider marks the payment refunded", [f1.body, a.rowOf().status]);
      const f2 = await hook(full);
      ok(f2.body.applied && f2.body.applied.duplicate === true && audits(a.rowOf().id, "payment.refunded") === 1, "re-delivering the refund does not refund twice", f2.body);

      const b = await captured();
      const stray = await hook(evt("evt_stray_1", "charge.refunded", { id: "ch_x", object: "charge", payment_intent: "pi_unknown", amount: b.c, amount_refunded: b.c }));
      ok(stray.body.applied && stray.body.applied.ignored === true && b.rowOf().status === "captured", "a refund for a payment this store does not have changes nothing", stray.body);
      const m = await pending();
      const mm = await hook(evt("evt_cap_mm", "checkout.session.completed", { id: m.rowOf().txn_ref, object: "checkout.session", payment_status: "paid", amount_total: m.c - 1 }));
      ok(mm.body.applied && mm.body.applied.ok === false && m.rowOf().status === "pending" && !db.get("SELECT 1 x FROM gateway_events WHERE event_id='evt_cap_mm'"), "an event that was not applied is not claimed, so the provider's retry can be", mm.body);

      const dsp = (id, type, extra) => evt(id, type, Object.assign({ id: "dp_b", object: "dispute", payment_intent: b.pi, amount: b.c, reason: "fraudulent" }, extra || {}));
      const dRow = () => db.get("SELECT * FROM disputes WHERE ref='stripe:dp_b'");
      const d1 = await hook(dsp("evt_dsp_1", "charge.dispute.created", { status: "needs_response" }));
      ok(d1.status === 200 && dRow() && dRow().state === "opened" && dRow().payment_id === b.rowOf().id && b.rowOf().status === "captured", "a chargeback at the provider opens a dispute on the payment", [d1.body, dRow()]);
      ok(dRow() && Math.abs(dRow().amount - b.rowOf().amount) < 1e-9 && dRow().reason === "fraudulent", "the dispute carries the provider's amount and reason", dRow());
      await hook(dsp("evt_dsp_1b", "charge.dispute.created", { status: "needs_response" }));
      ok(db.get("SELECT COUNT(*) n FROM disputes WHERE ref='stripe:dp_b'").n === 1, "a second event for the same chargeback opens no second dispute");
      const lost = await hook(dsp("evt_dsp_2", "charge.dispute.closed", { status: "lost" }));
      ok(lost.status === 200 && dRow().state === "lost" && b.rowOf().status === "disputed_lost", "a lost chargeback closes the dispute and marks the payment lost", [lost.body, dRow() && dRow().state, b.rowOf().status]);
      const won = await hook(dsp("evt_dsp_3", "charge.dispute.closed", { status: "won" }));
      ok(won.body.applied && won.body.applied.unchanged === true && dRow().state === "lost", "a closed dispute is not reopened by a later event", won.body);
      const forged = await hook(dsp("evt_dsp_4", "charge.dispute.created", { id: "dp_c" }), "whsec_wrong");
      ok(forged.status === 401 && !db.get("SELECT 1 x FROM disputes WHERE ref='stripe:dp_c'") && !db.get("SELECT 1 x FROM gateway_events WHERE event_id='evt_dsp_4'"), "a wrongly signed chargeback opens nothing and claims no event id", forged.status);
    }


    console.log("▸ EVERY GATEWAY CONFIRMS FROM ITS SPEC, NOT FROM CODE");
    {
      /* many orders from one address in a minute is exactly what risk screening blocks */
      await A("/api/admin/settings?store=luxora", "PUT", { features: { fraudScreen: false } });
      const sec = require("../lib/security.js");
      /* an order whose payment went to another gateway: the row is re-pointed so the event
         under test is the only thing that can settle it */
      const pendingOn = async (gw, ref) => {
        const o = (await buy()).co.body.order;
        db.run("UPDATE payments SET gateway=?, txn_ref=? WHERE order_id=(SELECT id FROM orders WHERE num=?)", gw, ref, o.num);
        return { o, row: () => db.get("SELECT p.*, o.status ostatus FROM payments p JOIN orders o ON o.id=p.order_id WHERE o.num=?", o.num) };
      };
      const gwCfg = (id, cfg, secrets) => db.run("INSERT OR REPLACE INTO tenant_gateways(tenant_id,provider_id,enabled,mode,config) VALUES(1,?,0,'live',?)", id, sec.sealConfig(1, id, cfg, secrets));
      const post = (prov, raw, headers) => fetch(BASE + "/api/webhooks/inbound/" + prov + "?store=luxora", { method: "POST", headers: Object.assign({ "Content-Type": "application/json" }, headers), body: raw }).then(async r => ({ status: r.status, body: await r.json().catch(() => ({})) }));

      gwCfg("razorpay", { keyId: "rzp_k", keySecret: "rzp_s", webhookSecret: "rzp_whsec" }, ["keySecret", "webhookSecret"]);
      const rz = await pendingOn("razorpay", "order_rzp_1");
      const rzAmt = Math.round(rz.o.total * 100);
      const rzRaw = JSON.stringify({ event: "order.paid", payload: { order: { entity: { id: "order_rzp_1", amount_paid: rzAmt } }, payment: { entity: { id: "pay_rzp_1", order_id: "order_rzp_1", amount: rzAmt } } } });
      const rzSig = k => crypto.createHmac("sha256", k).update(rzRaw).digest("hex");
      ok((await post("razorpay", rzRaw, { "X-Razorpay-Signature": rzSig("wrong") })).status === 401 && rz.row().status === "pending", "Razorpay: a webhook signed with the wrong secret changes nothing");
      const rzOk = await post("razorpay", rzRaw, { "X-Razorpay-Signature": rzSig("rzp_whsec") });
      ok(rzOk.status === 200 && rz.row().status === "captured" && rz.row().ostatus === "processing" && rz.row().provider_payment_id === "pay_rzp_1", "Razorpay: a signed order.paid captures the payment and releases the order", rzOk.body);

      gwCfg("square", { appId: "sq_app", token: "sq_tok", webhookSecret: "sq_key", webhookUrl: "https://shop.example/api/webhooks/inbound/square" }, ["token", "webhookSecret"]);
      const sq = await pendingOn("square", "sq_pay_1");
      const sqRaw = JSON.stringify({ type: "payment.updated", data: { object: { payment: { id: "sq_pay_1", status: "COMPLETED", amount_money: { amount: Math.round(sq.o.total * 100) } } } } });
      const sqSig = (k, u) => crypto.createHmac("sha256", k).update(u + sqRaw).digest("base64");
      ok((await post("square", sqRaw, { "X-Square-HmacSha256-Signature": sqSig("sq_key", "https://elsewhere.example/hook") })).status === 401 && sq.row().status === "pending", "Square: a signature over a different notification URL is refused");
      const sqOk = await post("square", sqRaw, { "X-Square-HmacSha256-Signature": sqSig("sq_key", "https://shop.example/api/webhooks/inbound/square") });
      ok(sqOk.status === 200 && sq.row().status === "captured", "Square: the URL + body signature verifies and the completed payment captures", sqOk.body);

      gwCfg("paypal", { clientId: "pp_id", secret: "pp_secret", env: "", webhookId: "WH-1" }, ["secret"]);
      const pp = await pendingOn("paypal", "PP-ORDER-1");
      ppAmount = pp.o.total.toFixed(2);
      const ppRaw = JSON.stringify({ event_type: "CHECKOUT.ORDER.APPROVED", resource: { id: "PP-ORDER-1" } });
      const ppHdr = sig => ({ "PayPal-Transmission-Id": "t1", "PayPal-Transmission-Sig": sig, "PayPal-Transmission-Time": "2026-10-16T00:00:00Z", "PayPal-Cert-Url": "https://api.paypal.com/cert", "PayPal-Auth-Algo": "SHA256withRSA" });
      ok((await post("paypal", ppRaw, ppHdr("forged"))).status === 401 && pp.row().status === "pending", "PayPal: a webhook PayPal's own verify call rejects changes nothing");
      const vBefore = calls.length;
      const ppOk = await post("paypal", ppRaw, ppHdr("good-sig"));
      const vCall = calls.slice(vBefore).find(c => c.url.endsWith("/verify-webhook-signature"));
      ok(vCall && vCall.json.webhook_event && vCall.json.webhook_event.resource.id === "PP-ORDER-1" && vCall.json.transmission_id === "t1", "PayPal: the event and its transmission headers are sent to PayPal to verify", vCall && vCall.json);
      ok(ppOk.status === 200 && calls.slice(vBefore).some(c => c.url.endsWith("/PP-ORDER-1/capture")), "PayPal: an approved order is captured", ppOk.body);
      ok(pp.row().status === "captured" && pp.row().provider_payment_id === "CAP-1", "PayPal: the capture settles the payment, keeping the capture id for refunds", pp.row());

      /* Razorpay: a partial refund and a chargeback made at Razorpay, against the payment captured above */
      const rzPost = (raw, id) => post("razorpay", raw, { "X-Razorpay-Signature": crypto.createHmac("sha256", "rzp_whsec").update(raw).digest("hex"), "X-Razorpay-Event-Id": id });
      const rzRefund = JSON.stringify({ event: "refund.processed", payload: { refund: { entity: { id: "rfnd_rzp_1", amount: 100, payment_id: "pay_rzp_1", status: "processed" } } } });
      const rzr = await rzPost(rzRefund, "evt_rzp_rf_1");
      ok(rzr.status === 200 && rzr.body.applied && rzr.body.applied.partial === true && Number(rz.row().refunded_minor) === 100 && rz.row().status === "captured", "Razorpay: a partial refund made at Razorpay is applied for its exact amount", [rzr.body, rz.row().refunded_minor]);
      ok(((await rzPost(rzRefund, "evt_rzp_rf_1")).body.applied || {}).duplicate === true && Number(rz.row().refunded_minor) === 100, "Razorpay: the same refund delivered again is applied once");
      const rzDsp = JSON.stringify({ event: "payment.dispute.created", payload: { payment: { entity: { id: "pay_rzp_1" } }, dispute: { entity: { id: "disp_rzp_1", amount: rzAmt, reason_code: "chargeback", status: "open" } } } });
      const rzd = await rzPost(rzDsp, "evt_rzp_d_1");
      const rzDrow = db.get("SELECT * FROM disputes WHERE ref='razorpay:disp_rzp_1'");
      ok(rzd.status === 200 && rzDrow && rzDrow.state === "opened" && rzDrow.payment_id === rz.row().id, "Razorpay: a chargeback opens a dispute against the payment", [rzd.body, rzDrow]);

      /* PhonePe, current API: sha256 of the merchant's webhook credentials; the merchant's own order id is the reference */
      gwCfg("phonepe", { clientId: "pp_c", clientSecret: "pp_s", clientVersion: "1", authBase: "https://pp.example/id", apiBase: "https://pp.example/pg", webhookSecret: "pp_user:pp_pass" }, ["clientSecret", "webhookSecret"]);
      const ph = await pendingOn("phonepe", "LX-PP-1");
      const phAmt = Math.round(ph.o.total * 100);
      const phPost = (raw, creds) => post("phonepe", raw, { Authorization: crypto.createHash("sha256").update(creds).digest("hex") });
      const phDone = JSON.stringify({ event: "checkout.order.completed", payload: { orderId: "OMO1", merchantOrderId: "LX-PP-1", state: "COMPLETED", amount: phAmt } });
      ok((await phPost(phDone, "pp_user:wrong")).status === 401 && ph.row().status === "pending", "PhonePe: a webhook with other credentials changes nothing");
      ok((await phPost(JSON.stringify({ event: "checkout.order.completed", payload: { merchantOrderId: "LX-PP-1", state: "COMPLETED", amount: phAmt - 1 } }), "pp_user:pp_pass")).status === 200 && ph.row().status === "pending", "PhonePe: a completed order for a different amount does not capture");
      const phOk = await phPost(phDone, "pp_user:pp_pass");
      ok(phOk.status === 200 && ph.row().status === "captured" && ph.row().provider_payment_id === "LX-PP-1", "PhonePe: a verified completed order captures the payment, keeping the order id for refunds", [phOk.body, ph.row().status]);
      const phRefund = JSON.stringify({ event: "pg.refund.completed", payload: { originalMerchantOrderId: "LX-PP-1", merchantRefundId: "R-1", refundId: "OMR1", state: "COMPLETED", amount: 100 } });
      const phr = await phPost(phRefund, "pp_user:pp_pass");
      ok(phr.body.applied && phr.body.applied.partial === true && Number(ph.row().refunded_minor) === 100, "PhonePe: a partial refund completed at PhonePe is applied", phr.body);
      ok(((await phPost(phRefund, "pp_user:pp_pass")).body.applied || {}).duplicate === true && Number(ph.row().refunded_minor) === 100, "PhonePe: with no event id, the same delivery is still applied once");

      /* PhonePe, salt-key API: the callback is base64 in `response`, verified by X-VERIFY */
      gwCfg("phonepe-legacy", { merchantId: "M_T", saltKey: "salt-1", saltIndex: "1", apiBase: "https://pp.example/hermes", callbackUrl: BASE + "/api/webhooks/inbound/phonepe-legacy", webhookSecret: "salt-1" }, ["saltKey", "webhookSecret"]);
      const pl = await pendingOn("phonepe-legacy", "LX-PL-1");
      const plResp = Buffer.from(JSON.stringify({ success: true, code: "PAYMENT_SUCCESS", data: { merchantId: "M_T", merchantTransactionId: "LX-PL-1", transactionId: "T-1", amount: Math.round(pl.o.total * 100), state: "COMPLETED" } })).toString("base64");
      const plRaw = JSON.stringify({ response: plResp });
      const plSig = salt => crypto.createHash("sha256").update(plResp + salt).digest("hex") + "###1";
      ok((await post("phonepe-legacy", plRaw, { "X-VERIFY": plSig("other") })).status === 401 && pl.row().status === "pending", "PhonePe (salt key): a callback signed with another salt changes nothing");
      const plOk = await post("phonepe-legacy", plRaw, { "X-VERIFY": plSig("salt-1") });
      ok(plOk.status === 200 && pl.row().status === "captured" && pl.row().provider_payment_id === "LX-PL-1", "PhonePe (salt key): the decoded, verified callback captures the payment", [plOk.body, pl.row().status]);

      console.log("▸ A WEBHOOK THAT NEVER ARRIVES IS COVERED BY A LOOKUP");
      const lk = await buy();
      const lrow = () => db.get("SELECT p.*, o.status ostatus FROM payments p JOIN orders o ON o.id=p.order_id WHERE o.num=?", lk.co.body.order.num);
      const lid = lrow().id;
      lookupReply = () => ({ status: "open", payment_status: "unpaid" });
      const still = await A("/api/admin/payments/" + lid + "/reconcile?store=luxora", "POST", {});
      ok(still.status === 200 && lrow().status === "pending", "checking an unpaid session leaves it pending", still.body);
      lookupReply = id => ({ status: "complete", payment_status: "paid", payment_intent: "pi_" + id, amount_total: Math.round(lk.co.body.order.total * 100) });
      const rec = await A("/api/admin/payments/" + lid + "/reconcile?store=luxora", "POST", {});
      ok(rec.status === 200 && lrow().status === "captured" && lrow().ostatus === "processing" && /^pi_/.test(lrow().provider_payment_id), "the console's check captures a payment the gateway reports paid", rec.body);
      const sw = await buy();
      const srow = () => db.get("SELECT p.*, o.status ostatus FROM payments p JOIN orders o ON o.id=p.order_id WHERE o.num=?", sw.co.body.order.num);
      lookupReply = () => ({ status: "expired", payment_status: "unpaid" });
      const swept = await require("../lib/api.js").reconcilePending(50);
      ok(swept.ran >= 1 && srow().status === "failed" && srow().ostatus === "cancelled", "the background sweep fails an expired session and releases its order", swept);
      lookupReply = () => ({ status: "open", payment_status: "unpaid" });

      console.log("▸ MONEY TAKEN OFFLINE IS RECORDED BY THE STORE");
      const C2 = mk(); await C2("/api/session?store=luxora");
      await C2("/api/auth/register?store=luxora", "POST", { name: "Cash Buyer", email: "cash" + crypto.randomBytes(3).toString("hex") + "@example.com", password: "Pay-Me-Later-123" });
      await C2("/api/cart?store=luxora", "POST", { id: product.id, qty: 1 });
      const cod = await C2("/api/checkout?store=luxora", "POST", { name: "Cash Buyer", address: "2 Main St", city: "Seattle", state: "WA", zip: "98109", gateway: "cod" });
      const crow = () => db.get("SELECT p.* FROM payments p JOIN orders o ON o.id=p.order_id WHERE o.num=?", cod.body.order.num);
      const ledger = (await A("/api/admin/payments?store=luxora")).body.payments || [];
      const lrowCod = ledger.find(x => x.id === crow().id);
      ok(crow().status === "pending" && lrowCod && lrowCod.offline === true && lrowCod.order_num === cod.body.order.num, "a cash order waits, and the ledger marks it as settled offline", lrowCod);
      ok((await A("/api/admin/payments/" + crow().id + "/reconcile?store=luxora", "POST", {})).status === 409, "there is no gateway to ask about cash");
      const got = await A("/api/admin/payments/" + crow().id + "/received?store=luxora", "POST", { note: "paid at the door" });
      ok(got.status === 200 && crow().status === "captured", "the store records the cash as received", got.body);
      ok((await A("/api/admin/payments/" + crow().id + "/received?store=luxora", "POST", {})).status === 409, "and only once");
      const live2 = await buy();
      const l2 = db.get("SELECT p.id FROM payments p JOIN orders o ON o.id=p.order_id WHERE o.num=?", live2.co.body.order.num);
      ok((await A("/api/admin/payments/" + l2.id + "/received?store=luxora", "POST", {})).status === 409, "a gateway payment cannot be marked received by hand");
    }

    console.log("▸ THE GATEWAY IS ASKED FOR WHAT THE SHOPPER WAS SHOWN, IN THEIR CURRENCY");
    {
      /* a store showing a currency other than its base one: the session the gateway creates must
         carry the shown total in the shown currency — the payment row alone cannot prove it,
         because it is written separately from the request */
      const Pf = mk(); await Pf("/api/session");
      await Pf("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" });
      const pol = (await Pf("/api/platform/config")).body.policy || {};
      await Pf("/api/platform/config", "PUT", { provisioning: Object.assign({}, pol.provisioning, { currencyOverridesAllowed: true }) });
      const base = String(((await A("/api/cart?store=luxora")).body.currency || {}).base || "");
      const other = ["EUR", "GBP", "JPY", "USD"].find(c => c !== base);
      /* a shipping fee and a tax beside the goods, and an exchange rate at which converting each
         shown part and converting the total once round differently: the charge must be the sum
         of the parts the shopper saw */
      const was = ((await A("/api/admin/settings?store=luxora")).body.settings || (await A("/api/admin/settings?store=luxora")).body || {}).commerce || {};
      const set = await A("/api/admin/settings?store=luxora", "PUT", { commerce: { currency: other, shipFee: 7.77, freeShipThreshold: 999999, taxRate: 0.0825 } });
      const Mx = require("../lib/money.js"), C0 = mk(); await C0("/api/session?store=luxora"); await C0("/api/cart?store=luxora", "POST", { id: product.id, qty: 1 });
      const origUsd = db.get("SELECT usd FROM currencies WHERE code=?", other).usd;
      let differs = null;
      for (const k of [1, 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]) {
        await Pf("/api/platform/fx/rates", "POST", { rates: { [other]: +(origUsd * (1 + k / 997)).toFixed(6) } });
        const cm = (await C0("/api/cart?store=luxora")).body.money;
        const once = Mx.convertTo(Mx.fromJSON(cm.base.total), cm.fx, other);
        if (!Mx.eq(once, Mx.fromJSON(cm.total))) { differs = { fx: cm.fx, once: Mx.toString(once), parts: cm.total.amount }; break; }
      }
      ok(!!differs, "an exchange rate is found at which part-by-part and once-for-the-total conversion differ by a minor unit", differs);
      const before = calls.length;
      const fx = await buy();
      const o2 = fx.co.body.order || {};
      const sess = calls.slice(before).find(c => c.url.endsWith("/checkout/sessions"));
      const minor = require("../lib/spec.js").minorUnits(o2.total, o2.currency);
      ok(set.status === 200 && o2.currency === other && o2.currency !== base && sess
        && sess.form["line_items[0][price_data][unit_amount]"] === String(minor) && sess.form["line_items[0][price_data][currency]"] === other.toLowerCase(),
        "with a display currency other than the base, the gateway is asked for exactly the shown total in the shown currency", { base, shown: [o2.total, o2.currency], sent: sess && [sess.form["line_items[0][price_data][unit_amount]"], sess.form["line_items[0][price_data][currency]"]] });
      const prow = db.get("SELECT p.amount, p.amount_minor, p.currency, p.money_scale FROM payments p JOIN orders o ON o.id=p.order_id WHERE o.num=?", o2.num);
      ok(prow && prow.currency === other && Math.abs(prow.amount - o2.total) < 1e-9, "…and the payment row records the same amount and currency", prow);
      /* one amount everywhere (PR-016): what the response serializes, the order row's and the
         payment row's exact minor units, and what the gateway was sent */
      const orow = db.get("SELECT total, total_minor, sub_minor, ship_fee_minor, gift_used_minor, tax_minor, currency, money_scale FROM orders WHERE num=?", o2.num);
      const mm = o2.money || {};
      ok(mm.v === 1 && mm.total && mm.total.currency === other && String(orow.total_minor) === mm.total.minor && String(prow.amount_minor) === mm.total.minor && sess && sess.form["line_items[0][price_data][unit_amount]"] === mm.total.minor,
        "the shown total, the order's and the payment's minor units and the gateway's amount are one exact figure", { response: mm.total, order: orow.total_minor, payment: prow.amount_minor, gateway: sess && sess.form["line_items[0][price_data][unit_amount]"] });
      const bm = k => BigInt(mm[k].minor);
      ok(bm("net") + bm("ship") + bm("surcharge") + BigInt(JSON.parse(db.get("SELECT charges FROM orders WHERE num=?", o2.num).charges || "[]").reduce((n, c) => n + Number(c.money ? c.money.minor : 0), 0)) + bm("tax") - bm("gift") === bm("total") && BigInt(orow.sub_minor) === bm("net") && BigInt(orow.tax_minor) === bm("tax"),
        "the shown components add up exactly to the shown total, and the order row holds those components", mm);
      ok(mm.base && mm.base.total.currency === base && mm.fx === String(o2.fx), "the base-currency figures and the rate they were converted at are recorded beside them", mm.base && mm.base.total);
      await A("/api/admin/settings?store=luxora", "PUT", { commerce: { currency: base, shipFee: was.shipFee, freeShipThreshold: was.freeShipThreshold, taxRate: was.taxRate == null ? null : was.taxRate } });
      await Pf("/api/platform/fx/rates", "POST", { rates: { [other]: origUsd } });
      await Pf("/api/platform/config", "PUT", { provisioning: Object.assign({}, pol.provisioning) });
    }

    console.log("▸ PART OF A PAYMENT GOES BACK, EXACTLY AND ONCE");
    {
      const third = (await buy()).co.body.order || {};
      const row3 = () => db.get("SELECT p.* FROM payments p JOIN orders o ON o.id=p.order_id WHERE o.num=?", third.num);
      const c3 = Number(row3().amount_minor);
      await hook(sessionEvent("checkout.session.completed", row3().txn_ref, { amount_total: c3, payment_intent: "pi_part_3" }));
      ok(row3().status === "captured" && row3().provider_payment_id === "pi_part_3", "a third order is captured", row3());
      refundReply = { status: 200, json: { id: "re_part_1", status: "succeeded" } };
      const R = (body, key) => A("/api/admin/payments/" + row3().id + "/refund?store=luxora", "POST", body, key ? { "Idempotency-Key": key } : {});
      const before = calls.length;
      const noKey = await R({ amount: "1.00" });
      ok(noKey.status === 400 && /idempotency key/i.test(noKey.body.error || ""), "part of a payment needs an Idempotency-Key", noKey.body);
      const part = await R({ amount: "1.00" }, "part-1");
      const sent = calls.slice(before).filter(c => c.url.endsWith("/refunds"));
      ok(part.status === 200 && Number(row3().refunded_minor) === 100 && row3().status === "captured" && part.body.refundable && part.body.refundable.minor === String(c3 - 100), "a refund of 1.00 is applied: the payment stays captured with the rest refundable", part.body);
      ok(sent.length === 1 && sent[0].form.amount === "100" && sent[0].form.payment_intent === "pi_part_3", "the provider is asked for exactly 100 minor units of that payment intent", sent[0] && sent[0].form);
      const again = await R({ amount: "1.00" }, "part-1");
      ok(again.status === 200 && calls.slice(before).filter(c => c.url.endsWith("/refunds")).length === 1 && Number(row3().refunded_minor) === 100, "the same request again is not sent or applied twice", again.body);
      const over = await R({ amount: (c3 / 100).toFixed(2) }, "part-2");
      ok(over.status === 409 && Number(row3().refunded_minor) === 100, "more than what is left is refused", over.body);
      /* a provider answering a second refund with the first one's id made no new refund: it is
         kept as unknown (reserved, for review), never counted as money returned */
      const dup = await R({ amount: "1.00" }, "part-dup");
      ok(dup.status === 202 && dup.body.unknown && dup.body.refund.status === "unknown" && row3().status === "captured", "a provider answer naming an already-recorded refund is not taken as a new refund", dup.body);
      const listed = await A("/api/admin/payments/" + row3().id + "/refunds?store=luxora");
      ok(listed.status === 200 && listed.body.refunds.length === 2 && listed.body.refunds.some(r => r.status === "unknown"), "the payment's refunds are listed with their states", listed.body);
      const settled = await A("/api/admin/refunds/" + dup.body.refund.id + "/resolve?store=luxora", "POST", { outcome: "failed", note: "the provider's dashboard shows one refund" });
      ok(settled.status === 200 && settled.body.refund.status === "failed" && Number(row3().refunded_minor) === 100, "staff resolve it as failed from the provider's record, and its reservation is given back", settled.body);
      const twiceResolved = await A("/api/admin/refunds/" + dup.body.refund.id + "/resolve?store=luxora", "POST", { outcome: "succeeded" });
      ok(twiceResolved.status === 409, "a resolved refund cannot be resolved again", twiceResolved.body);
      refundReply = { status: 200, json: { id: "re_part_2", status: "succeeded" } };
      const rest = await R({}, "part-3");
      ok(rest.status === 200 && rest.body.full && row3().status === "refunded" && Number(row3().refunded_minor) === c3, "refunding the rest reverses the payment", rest.body);
      ok(require("../lib/money-store.js").verify().ok, "verify(): every money row and every payment's refunded total is consistent");
    }

    console.log("▸ CARRIER RATES, LABELS AND TRACKING");
    {
      const none = await A("/api/shipping/quote?store=luxora", "POST", { order_id: 1, parcel: { weight_oz: 10 } });
      ok(none.status === 501, "with no carrier key the quote says it is not integrated", none);
      const P = mk(); await P("/api/session");
      ok((await P("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" })).status === 200, "platform admin signs in");
      const cfg = await P("/api/shipping/providers/config", "POST", { provider_id: "easypost", config: { apiKey: "EZTK_live_key", webhookSecret: "ep_whsec" } });
      ok(cfg.status === 200 && cfg.body.provider.status === "active" && cfg.body.provider.configured && !JSON.stringify(cfg.body).includes("EZTK_live_key"), "EasyPost is activated with an API key that is never echoed back", cfg.body);
      const listing = await P("/api/platform/shipping/providers");
      const epRow = (listing.body.providers || []).find(x => x.provider_id === "easypost") || {};
      ok(listing.status === 200 && epRow.keys && epRow.keys.apiKey === true && epRow.keys.webhookSecret === true && !JSON.stringify(listing.body).includes("EZTK_live_key") && !JSON.stringify(listing.body).includes("ep_whsec"), "the platform console sees which carrier keys are on file, never the keys", listing.body);
      ok((await A("/api/platform/shipping/providers?store=luxora")).status >= 401 && (await A("/api/platform/shipping/providers/easypost/disconnect?store=luxora", "POST", {})).status >= 401, "a store admin can neither list nor disconnect the platform carrier account");
      /* a save with only the webhook secret keeps the key on file */
      await P("/api/shipping/providers/config", "POST", { provider_id: "easypost", config: { apiKey: "", webhookSecret: "ep_whsec" } });
      ok((await P("/api/platform/shipping/providers")).body.providers.find(x => x.provider_id === "easypost").status === "active", "saving with a blank key keeps the stored key");
      const stored = db.get("SELECT config FROM shipping_providers WHERE provider_id='easypost'");
      ok(stored && !stored.config.includes("EZTK_live_key") && !stored.config.includes("ep_whsec"), "the carrier key and webhook secret are sealed at rest");
      const shopper = mk(); await shopper("/api/session?store=luxora");
      ok((await shopper("/api/shipping/quote?store=luxora", "POST", { order_id: 1, parcel: { weight_oz: 10 } })).status === 403, "a shopper cannot rate or buy labels");
      const noFrom = await A("/api/shipping/quote?store=luxora", "POST", { order_id: row().order_id, parcel: { weight_oz: 10 } });
      ok(noFrom.status === 400 && /ship-from/.test(noFrom.body.error), "without a ship-from address the store is told to set one", noFrom.body);
      ok((await A("/api/admin/settings?store=luxora", "PUT", { commerce: { shipFrom: { name: "LUXORA Warehouse", street1: "400 Pine St", city: "Seattle", state: "WA", zip: "98101", country: "US" } } })).status === 200, "the store saves its ship-from address");
      const badFrom = await A("/api/admin/settings?store=luxora", "PUT", { commerce: { shipFrom: { street1: "1 Nowhere", city: "Seattle", country: "US" } } });
      ok(badFrom.status === 400 && /postal code/.test(badFrom.body.error), "a ship-from address without a postal code is refused", badFrom.body);
      ok((await A("/api/admin/settings?store=luxora", "PUT", { commerce: { shipFrom: { street1: "1 Nowhere", city: "Seattle", zip: "98101", country: "USA" } } })).status === 400, "a ship-from country must be a 2-letter code");
      await A("/api/admin/settings?store=luxora", "PUT", { commerce: { shipFrom: { street1: "9 Dock Rd", street2: "Bay 4", city: "Tacoma", zip: "98402", country: "us", evil: "x" } } });
      await A("/api/admin/settings?store=luxora", "PUT", { commerce: { shipFrom: { name: "LUXORA Warehouse", street1: "400 Pine St", city: "Seattle", state: "WA", zip: "98101", country: "US" } } });
      const savedFrom = (await A("/api/admin/settings?store=luxora")).body.settings.commerce.shipFrom;
      ok(savedFrom.street1 === "400 Pine St" && !("street2" in savedFrom) && !("evil" in savedFrom), "a new ship-from address replaces the old one whole, keeping only address fields", savedFrom);
      const before = calls.length;
      const q = await A("/api/shipping/quote?store=luxora", "POST", { order_id: row().order_id, parcel: { weight_oz: 18, length: 10, width: 8, height: 4 } });
      const qc = calls.slice(before).find(c => c.url.endsWith("/v2/shipments"));
      ok(q.status === 200 && q.body.rates.length === 2 && q.body.rates[0].carrier === "USPS" && q.body.rates[0].price === 7.85, "live rates come back, cheapest first", q.body);
      ok(qc && qc.headers.Authorization === "Basic " + Buffer.from("EZTK_live_key:").toString("base64"), "the carrier is called with the platform's key");
      ok(qc && qc.json.shipment.to_address.street1 === "1 Main St" && qc.json.shipment.from_address.zip === "98101" && qc.json.shipment.parcel.weight === 18, "the order's own address and the store's origin are rated", qc && qc.json);
      const foreign = await A("/api/shipping/label?store=luxora", "POST", { shipment_id: "shp_other", rate_id: "rate_usps" });
      ok(foreign.status === 404, "a label can only be bought for a rate this store was quoted", foreign.status);
      const lab = await A("/api/shipping/label?store=luxora", "POST", { shipment_id: "shp_1", rate_id: "rate_usps" });
      const bc = calls.find(c => c.url.endsWith("/shipments/shp_1/buy"));
      ok(lab.status === 200 && lab.body.tracking_number === "9400111899223197428490" && /^https:/.test(lab.body.label_url), "buying the rate returns the label and tracking number", lab.body);
      ok(bc && bc.json.rate.id === "rate_usps", "the chosen rate is the one bought", bc && bc.json);
      const twice = await A("/api/shipping/label?store=luxora", "POST", { shipment_id: "shp_1", rate_id: "rate_ups" });
      ok(twice.status === 409 && calls.filter(c => c.url.endsWith("/buy")).length === 1, "a shipment gets one label", twice.status);
      ok(db.get("SELECT status FROM orders WHERE id=?", row().order_id).status === "shipped", "buying the label marks the order shipped");
      const labels = await A("/api/shipping/orders/" + row().order_id + "/labels?store=luxora");
      ok(labels.status === 200 && labels.body.labels.length === 1 && labels.body.labels[0].tracking_number === "9400111899223197428490" && /^https:/.test(labels.body.labels[0].label_url), "the order's label is listed for reprinting", labels.body);
      ok((await shopper("/api/shipping/orders/" + row().order_id + "/labels?store=luxora")).status === 403, "a shopper cannot list an order's labels");
      const fresh = await buy();
      const unpaid = db.get("SELECT id, status FROM orders WHERE num=?", fresh.co.body.order.num);
      ok(unpaid && unpaid.status === "pending_payment" && ((await A("/api/shipping/quote?store=luxora", "POST", { order_id: unpaid.id, parcel: { weight_oz: 10 } })).status === 409), "an unpaid order cannot be rated for shipping", unpaid);
      const tr = db.get("SELECT * FROM package_tracking WHERE tracking_number='9400111899223197428490'");
      ok(tr && tr.tenant_id === 1 && tr.order_id === row().order_id && tr.status === "pre_transit", "the parcel is registered for tracking against the order", tr);

      const evt = { object: "Event", description: "tracker.updated", result: { object: "Tracker", tracking_code: "9400111899223197428490", status: "in_transit", tracking_details: [{ message: "Departed facility", datetime: "2026-10-15T10:00:00Z", tracking_location: { city: "Seattle", state: "WA" } }] } };
      const raw = JSON.stringify(evt);
      const sig = s => "hmac-sha256-hex=" + crypto.createHmac("sha256", s).update(raw).digest("hex");
      const send = h => fetch(BASE + "/api/shipping/webhook/easypost", { method: "POST", headers: { "Content-Type": "application/json", "X-Hmac-Signature": h }, body: raw });
      ok((await send(sig("wrong"))).status === 401 && db.get("SELECT status FROM package_tracking WHERE id=?", tr.id).status === "pre_transit", "an unsigned or mis-signed tracking webhook changes nothing");
      ok((await send(sig("ep_whsec"))).status === 200 && db.get("SELECT status FROM package_tracking WHERE id=?", tr.id).status === "in_transit", "a signed tracker update advances the parcel");

      console.log("▸ CHECKOUT CHARGES THE LIVE CARRIER RATE");
      {
        const S = mk(); await S("/api/session?store=luxora");
        await S("/api/auth/register?store=luxora", "POST", { name: "Rae Rates", email: "rae" + crypto.randomBytes(3).toString("hex") + "@example.com", password: "Rate-Me-Now-123" });
        await S("/api/cart?store=luxora", "POST", { id: product.id, qty: 1 });
        const dest = { name: "Rae Rates", address: "77 Lake Ave", city: "Portland", state: "OR", zip: "97201" };
        ok((await A("/api/admin/settings?store=luxora", "PUT", { commerce: { shipRates: "sometimes" } })).status === 400, "the shipping price mode is validated");
        await A("/api/admin/settings?store=luxora", "PUT", { commerce: { freeShipThreshold: 1000000 } });
        const fixedQ = await S("/api/checkout/quote?store=luxora", "POST", dest);
        ok(fixedQ.status === 200 && fixedQ.body.source === "fixed" && fixedQ.body.rates.length === 0, "in fixed mode no carrier is asked", fixedQ.body);
        ok((await A("/api/admin/settings?store=luxora", "PUT", { commerce: { shipRates: "live", parcelWeightKg: 1 } })).status === 200, "the store switches to live carrier rates");
        const qBefore = calls.length;
        const lq = await S("/api/checkout/quote?store=luxora", "POST", dest);
        const shipCall = calls.slice(qBefore).find(c => c.url.endsWith("/v2/shipments"));
        ok(lq.status === 200 && lq.body.source === "live" && lq.body.rates.length === 2 && lq.body.shipFee === 7.85 && lq.body.rate_id === "rate_usps", "the quote offers the carrier's rates and starts on the cheapest", lq.body);
        ok(shipCall && shipCall.json.shipment.to_address.street1 === "77 Lake Ave" && shipCall.json.shipment.from_address.zip === "98101" && shipCall.json.shipment.parcel.weight > 0, "the parcel is rated from the ship-from address to the shopper's", shipCall && shipCall.json);
        const ups = await S("/api/checkout/quote?store=luxora", "POST", { ...dest, rate_id: "rate_ups" });
        ok(ups.body.shipFee === 11.2 && ups.body.total > lq.body.total, "choosing another rate re-prices the order", ups.body);
        const noAddr = await S("/api/checkout/quote?store=luxora", "POST", {});
        ok(noAddr.body.source === "fixed", "without an address the flat fee is shown until one is entered", noAddr.body);
        const co = await S("/api/checkout?store=luxora", "POST", { ...dest, gateway: "cod", rate_id: "rate_ups" });
        const ord = db.get("SELECT * FROM orders WHERE num=?", co.body.order && co.body.order.num);
        ok(co.status === 200 && ord && Math.abs(ord.ship_fee - 11.2) < 0.001 && ord.ship_option === "ups" && co.body.order.shipping.source === "live" && Math.abs(co.body.order.total - ups.body.total) < 0.01, "checkout charges the chosen rate — the same total the quote showed", co.body.order);
        ok(db.get("SELECT COUNT(*) c FROM shipping_quotes WHERE order_id=? AND rate_ref='rate_ups'", ord.id).c === 1, "the rate the shopper paid for is attached to the order for the label");
        await A("/api/admin/settings?store=luxora", "PUT", { commerce: { shipRates: "fixed", freeShipThreshold: 35 } });
      }
      const disc = await P("/api/platform/shipping/providers/easypost/disconnect", "POST", {});
      const after = db.get("SELECT config, status FROM shipping_providers WHERE provider_id='easypost'");
      ok(disc.status === 200 && after.status === "inactive" && after.config === "{}", "disconnecting deletes the sealed keys and takes the carrier out of service", after);
      ok((await A("/api/shipping/quote?store=luxora", "POST", { order_id: row().order_id, parcel: { weight_oz: 10 } })).status === 501, "a disconnected carrier gives no rates");
    }

    console.log("▸ AMOUNTS IN CURRENCIES WITHOUT MINOR UNITS");
    const spec = require("../lib/spec.js");
    ok(spec.verifyHmac({ header: "x-sig", encoding: "hex" }, "k", "body", { "x-sig": crypto.createHmac("sha256", "k").update("body").digest("hex") }) === true && spec.verifyHmac({ header: "x-sig" }, "k", "tampered", { "x-sig": crypto.createHmac("sha256", "k").update("body").digest("hex") }) === false && spec.verifyHmac(null, "k", "b", {}) === null, "a declared HMAC scheme verifies exactly the bytes signed");
    ok(spec.minorUnits(1500, "JPY") === 1500 && spec.minorUnits(12.34, "USD") === 1234 && spec.minorUnits(10, "KRW") === 10, "¥1,500 is sent as 1500, $12.34 as 1234");
  } catch (e) {
    failed++; console.error("  ✗ harness error:", e && e.stack || e);
  }
  console.log(`\n${passed} passed, ${failed} failed`);
  for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
  process.exit(failed ? 1 : 0);
})();
