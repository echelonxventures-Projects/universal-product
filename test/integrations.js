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
    ok(rc && rc.form.payment_intent === "pi_test_1" && rc.headers["Idempotency-Key"] === "refund-" + pid, "the refund names the payment intent, idempotently", rc && rc.form);
    const twice = await A("/api/admin/payments/" + pid + "/refund?store=luxora", "POST", {});
    ok(twice.status >= 400 && calls.slice(before).filter(c => c.url.endsWith("/refunds")).length === 1, "a payment is refunded once", twice.status);

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
      const disc = await P("/api/platform/shipping/providers/easypost/disconnect", "POST", {});
      const after = db.get("SELECT config, status FROM shipping_providers WHERE provider_id='easypost'");
      ok(disc.status === 200 && after.status === "inactive" && after.config === "{}", "disconnecting deletes the sealed keys and takes the carrier out of service", after);
      ok((await A("/api/shipping/quote?store=luxora", "POST", { order_id: row().order_id, parcel: { weight_oz: 10 } })).status === 501, "a disconnected carrier gives no rates");
    }

    console.log("▸ AMOUNTS IN CURRENCIES WITHOUT MINOR UNITS");
    const spec = require("../lib/spec.js");
    ok(spec.minorUnits(1500, "JPY") === 1500 && spec.minorUnits(12.34, "USD") === 1234 && spec.minorUnits(10, "KRW") === 10, "¥1,500 is sent as 1500, $12.34 as 1234");
  } catch (e) {
    failed++; console.error("  ✗ harness error:", e && e.stack || e);
  }
  console.log(`\n${passed} passed, ${failed} failed`);
  for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
  process.exit(failed ? 1 : 0);
})();
