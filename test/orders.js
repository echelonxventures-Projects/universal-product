/* LUXORA Platform — an order's stock and money, end to end: what checkout takes, and what a
   cancellation, a failed or late payment and a return give back. Runs the real server in this
   process on its own throwaway database; the payment gateway is a stand-in, nothing is sent out. */
"use strict";
const path = require("path"), fs = require("fs"), crypto = require("crypto");
const DB = path.join(__dirname, "orders.db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
process.env.LX_DB = DB; process.env.PORT = "8897"; process.env.LX_LOG = "";
delete process.env.NODE_ENV; delete process.env.LX_OFFLINE;
const BASE = "http://localhost:" + process.env.PORT, Q = "?store=luxora", WHSEC = "whsec_orders_test";
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + JSON.stringify(x) : ""))); };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms = 4000) => { for (let i = 0; i < ms / 50; i++) { const v = await fn(); if (v) return v; await sleep(50); } return null; };
const mk = () => {
  const c = new Map();
  return async (p, m, b) => {
    const o = { method: m || "GET", headers: { Cookie: [...c].map(x => x[0] + "=" + x[1]).join("; "), "Content-Type": "application/json", "x-csrf": c.get("azc") || "" } };
    if (b !== undefined) o.body = JSON.stringify(b);
    const r = await fetch(BASE + p, o);
    r.headers.getSetCookie().forEach(k => { const kv = k.split(";")[0], i = kv.indexOf("="); c.set(kv.slice(0, i).trim(), kv.slice(i + 1).trim()); });
    const t = await r.text(); let body; try { body = JSON.parse(t); } catch (e) { body = { _raw: t }; }
    return { status: r.status, body };
  };
};
const refundCalls = []; let refundOk = true, n = 0;
const gateway = (url, o) => {
  let json = {}, status = 200;
  const form = o && o.body ? Object.fromEntries(new URLSearchParams(o.body)) : {};
  if (url.endsWith("/checkout/sessions")) { n++; json = { id: "cs_" + n, url: "https://pay.test/" + n, status: "open", payment_status: "unpaid", form }; gateway.last = form; }
  else if (url.endsWith("/refunds")) { refundCalls.push(form); status = refundOk ? 200 : 402; json = refundOk ? { id: "re_" + refundCalls.length, status: "succeeded" } : { error: { message: "card closed" } }; }
  else status = 404;
  return Promise.resolve({ ok: status < 300, status, text: async () => JSON.stringify(json) });
};
const hook = async (type, cs, extra) => {
  const raw = JSON.stringify({ id: "evt_" + crypto.randomBytes(4).toString("hex"), type, data: { object: Object.assign({ id: cs, payment_status: "paid", payment_intent: "pi_" + cs }, extra) } });
  const t = Math.floor(Date.now() / 1000);
  const r = await fetch(BASE + "/api/webhooks/inbound/stripe" + Q, { method: "POST", headers: { "Content-Type": "application/json", "Stripe-Signature": `t=${t},v1=` + crypto.createHmac("sha256", WHSEC).update(t + "." + raw).digest("hex") }, body: raw });
  return r.status;
};

(async () => {
  const quiet = console.log; console.log = () => { };
  require("../server.js");
  const db = require("../lib/db.js"), connect = require("../lib/connect.js");
  console.log = quiet;
  connect.__setTransport(gateway);
  for (let i = 0; i < 720; i++) { try { if ((await fetch(BASE + "/healthz")).ok) break; } catch (e) { } await sleep(250); }
  try {
    const A = mk(); await A("/api/session" + Q);
    ok((await A("/api/auth/login" + Q, "POST", { email: "admin@luxora.shop", password: "admin123" })).status === 200, "the store admin signs in");
    await A("/api/admin/gateways" + Q, "PUT", { gateways: [{ id: "stripe", enabled: true, primary: true, mode: "live", config: { publishableKey: "pk", secretKey: "sk_live_x", webhookSecret: WHSEC } }, { id: "cod", enabled: true, mode: "live", config: {} }] });
    const P = db.all("SELECT p.id FROM products p WHERE p.tenant_id=1 AND p.type='physical' AND p.lifecycle='published' AND p.deleted_at IS NULL AND p.price BETWEEN 20 AND 300 AND (SELECT COUNT(*) FROM skus k WHERE k.tenant_id=1 AND k.product_id=p.id AND k.active=1)=1 ORDER BY p.id LIMIT 2").map(x => x.id);
    const set = (id, q) => { db.run("UPDATE products SET stock=? WHERE tenant_id=1 AND id=?", q, id); db.run("UPDATE skus SET stock=? WHERE tenant_id=1 AND product_id=?", q, id); db.run("UPDATE inventory SET qty=? WHERE tenant_id=1 AND sku_id IN (SELECT id FROM skus WHERE tenant_id=1 AND product_id=?)", q, id); };
    const counts = id => [db.get("SELECT stock s FROM products WHERE tenant_id=1 AND id=?", id).s, db.get("SELECT stock s FROM skus WHERE tenant_id=1 AND product_id=?", id).s, db.get("SELECT SUM(qty) s FROM inventory WHERE tenant_id=1 AND sku_id IN (SELECT id FROM skus WHERE tenant_id=1 AND product_id=?)", id).s];
    const shopper = async () => { const C = mk(); await C("/api/session" + Q); await C("/api/auth/register" + Q, "POST", { name: "Olive Order", email: "o" + crypto.randomBytes(4).toString("hex") + "@example.com", password: "Long-Enough-Pass-9" }); return C; };
    const dest = { name: "Olive Order", address: "1 Main St", city: "Seattle", state: "WA", zip: "98109", carrier: "house-std" };
    const place = async (C, items, gw) => { for (const [id, q] of items) await C("/api/cart" + Q, "POST", { id, qty: q }); const r = await C("/api/checkout" + Q, "POST", { ...dest, gateway: gw || "cod" }); return r; };
    const row = num => db.get("SELECT * FROM orders WHERE num=?", num);
    const pay = num => db.get("SELECT p.* FROM payments p JOIN orders o ON o.id=p.order_id WHERE o.num=?", num);
    const paid = async (C, items) => { const r = await place(C, items, "stripe"); const p = pay(r.body.order.num); await hook("checkout.session.completed", p.txn_ref, { amount_total: Math.round(p.amount * 100) }); return r.body.order.num; };
    const [X, Y] = P;
    await A("/api/admin/settings" + Q, "PUT", { features: { fraudScreen: false } });

    console.log("▸ STOCK");
    set(X, 3);
    const C1 = await shopper(), C2 = await shopper();
    await C1("/api/cart" + Q, "POST", { id: X, qty: 3 }); await C2("/api/cart" + Q, "POST", { id: X, qty: 3 });
    const both = await Promise.all([C1, C2].map(C => C("/api/checkout" + Q, "POST", { ...dest, gateway: "cod" })));
    ok(both.map(b => b.status).sort().join() === "200,409", "two shoppers with the last units in their bags: one gets them", both.map(b => [b.status, b.body.error]));
    ok(counts(X).join() === "0,0,0", "the item, its variant and its warehouse all show none left", counts(X));
    ok((await (await shopper())("/api/cart" + Q, "POST", { id: X, qty: 1 })).status === 400, "a sold-out item cannot be added to a bag");
    set(X, 2);
    const C3 = await shopper();
    const add = await C3("/api/cart" + Q, "POST", { id: X, qty: 9 });
    ok(add.body.items[0].qty === 2, "a bag never holds more than is left", add.body.items[0].qty);
    ok((await C3("/api/cart" + Q, "PUT", { id: X, qty: 1.5 })).status === 400, "a fraction of an item is refused");
    set(X, 10); set(Y, 1);
    await C3("/api/cart" + Q, "POST", { id: Y, qty: 1 }); set(Y, 0);
    const mixed = await C3("/api/checkout" + Q, "POST", { ...dest, gateway: "cod" });
    ok(mixed.status === 409 && counts(X).join() === "10,10,10", "one item short: the order is refused and nothing is taken", [mixed.status, mixed.body.error, counts(X)]);

    console.log("▸ CANCELLING");
    set(X, 10); set(Y, 10);
    const C4 = await shopper();
    const cash = (await place(C4, [[X, 2]])).body.order.num;
    const mine = (await C4("/api/orders" + Q)).body.orders.find(o => o.num === cash);
    ok(mine.can.cancel === true && mine.can.return === false, "the shopper is told what they can do with the order", mine.can);
    ok((await C4("/api/orders/" + mine.id + "/cancel" + Q, "POST", {})).status === 200 && counts(X).join() === "10,10,10", "cancelling puts the stock back", counts(X));
    ok(pay(cash).status === "failed", "cash that was never taken is closed", pay(cash).status);
    ok((await C4("/api/orders/" + mine.id + "/cancel" + Q, "POST", {})).status === 409 && counts(X).join() === "10,10,10", "a second cancel is refused and gives nothing back twice", counts(X));
    const num = await paid(C4, [[X, 1]]);
    ok(pay(num).status === "captured" && row(num).status === "processing", "a paid order is captured", [pay(num).status, row(num).status]);
    const total = pay(num).amount;
    const cx = await C4("/api/orders/" + row(num).id + "/cancel" + Q, "POST", {});
    ok(cx.status === 200 && Math.abs(cx.body.refunded - total) < 0.01 && refundCalls.length === 1 && refundCalls[0].amount === String(Math.round(total * 100)) && refundCalls[0].payment_intent === pay(num).provider_payment_id, "cancelling a paid order refunds it through the gateway, in full", [cx.body, refundCalls]);
    ok(pay(num).status === "refunded" && counts(X)[0] === 10, "the payment is refunded and the stock is back", [pay(num).status, counts(X)]);
    ok((await A("/api/admin/orders/" + row(num).id + "/status" + Q, "PUT", { status: "shipped" })).status === 409, "a cancelled order cannot be reopened");
    const n2 = await paid(C4, [[X, 1]]); refundOk = false;
    const cy = await C4("/api/orders/" + row(n2).id + "/cancel" + Q, "POST", {});
    ok(cy.status === 200 && cy.body.refunded === 0 && cy.body.owed > 0 && pay(n2).status === "captured", "a refund the gateway refuses is reported as owed, never as made", [cy.body, pay(n2).status]);
    ok((await A("/api/admin/payments" + Q)).body.owed.some(r => r.order_num === n2 && /card closed/.test(r.error)), "staff see what is owed and why");
    refundOk = true;
    const again = await A("/api/admin/payments/" + pay(n2).id + "/refund" + Q, "POST", {});
    ok(again.status === 200 && pay(n2).status === "refunded", "staff send it again", again.body);
    const n3 = (await place(C4, [[X, 1]], "stripe")).body.order.num;
    await C4("/api/orders/" + row(n3).id + "/cancel" + Q, "POST", {});
    const before = refundCalls.length;
    await hook("checkout.session.completed", pay(n3).txn_ref, { amount_total: Math.round(pay(n3).amount * 100) });
    ok(await until(() => refundCalls.length === before + 1 && pay(n3).status === "refunded") && row(n3).status === "cancelled", "money that arrives after the order was cancelled goes straight back", [refundCalls.length - before, pay(n3).status, row(n3).status]);
    const n4 = (await place(C4, [[X, 1]], "stripe")).body.order.num;
    const c0 = counts(X)[0];
    await hook("checkout.session.expired", pay(n4).txn_ref, { payment_status: "unpaid" });
    ok(row(n4).status === "cancelled" && counts(X)[0] === c0 + 1, "an abandoned payment page puts the stock back", [row(n4).status, c0, counts(X)[0]]);

    console.log("▸ PART REFUNDS");
    const n5 = await paid(C4, [[X, 2]]);
    const p5 = pay(n5);
    ok((await A("/api/admin/payments/" + p5.id + "/refund" + Q, "POST", { amount: 5 })).body.full === false && pay(n5).status === "captured", "part of a payment can be refunded");
    ok((await A("/api/admin/payments/" + p5.id + "/refund" + Q, "POST", { amount: p5.amount })).status === 409, "never more than what is left of it");
    const race = await Promise.all([0, 1].map(() => A("/api/admin/payments/" + p5.id + "/refund" + Q, "POST", { amount: +(p5.amount - 5).toFixed(2) })));
    ok(race.filter(r => r.status === 200).length === 1 && pay(n5).refunded <= p5.amount + 0.001, "two refunds at once cannot exceed the payment", race.map(r => r.status));

    console.log("▸ RETURNS");
    const n6 = await paid(C4, [[X, 2], [Y, 1]]);
    const o6 = row(n6);
    ok((await C4("/api/returns" + Q, "POST", { order_num: n6, product_id: X, qty: 1 })).status === 409, "nothing is returned before it has been handed over");
    await A("/api/admin/orders/" + o6.id + "/status" + Q, "PUT", { status: "shipped" });
    ok((await C4("/api/orders/" + o6.id + "/cancel" + Q, "POST", {})).status === 409, "an order on its way is not cancelled by the shopper");
    await A("/api/admin/orders/" + o6.id + "/status" + Q, "PUT", { status: "delivered" });
    ok((await C4("/api/returns" + Q, "POST", { order_num: n6, product_id: "NOT-BOUGHT", qty: 1 })).status === 409, "an item that was not bought cannot be returned");
    ok((await C4("/api/returns" + Q, "POST", { order_num: n6, product_id: X, qty: 999 })).status === 409, "nor more than was bought");
    const rt = await C4("/api/returns" + Q, "POST", { order_num: n6, product_id: X, qty: 1, reason: "too big" });
    ok(rt.status === 200 && rt.body.returns.length === 1, "one of two is returned", rt.body);
    const bx = counts(X)[0], rc = refundCalls.length, rid = rt.body.returns[0].id;
    refundOk = false;
    ok((await A("/api/admin/returns/" + rid + Q, "PUT", { status: "refunded" })).status === 502 && db.get("SELECT status FROM returns WHERE id=?", rid).status === "requested", "a refund that cannot be sent leaves the return where it was");
    refundOk = true;
    const done = await A("/api/meta/entity/ret/" + rid + Q, "PUT", { status: "refunded" });
    ok(done.status === 200 && Math.abs(Number(refundCalls[refundCalls.length - 1].amount) / 100 - rt.body.returns[0].worth) < 0.011 && counts(X)[0] === bx + 1, "approved from the record editor: that item's share is refunded and it is back on the shelf", [done.body, refundCalls.slice(rc), rt.body.returns[0].worth, counts(X)[0] - bx]);
    ok((await A("/api/admin/returns/" + rid + Q, "PUT", { status: "requested" })).status === 409, "a closed return stays closed");
    const rest = await C4("/api/returns" + Q, "POST", { order_num: n6, reason: "all of it" });
    ok(rest.status === 200 && rest.body.returns.length === 2 && rest.body.returns.every(r => r.qty === 1), "the rest of the order is returned in one request", rest.body);
    for (const r of rest.body.returns) await A("/api/admin/returns/" + r.id + Q, "PUT", { status: "refunded" });
    const p6 = pay(n6), ship = row(n6).ship_fee;
    ok(Math.abs(p6.refunded - (p6.amount - ship)) < 0.03, "returning everything gives back all but the delivery fee", [p6.refunded, p6.amount, ship]);
    ok((await C4("/api/returns" + Q, "POST", { order_num: n6 })).status === 409, "nothing is left to return");
    const stranger = await shopper();
    ok((await stranger("/api/returns" + Q, "POST", { order_num: n5 })).status === 404, "another shopper's order cannot be returned");

    console.log("▸ INVOICES");
    const IV = require("../lib/invoices.js");
    ok(IV.yearLabel(new Date("2026-03-31T12:00:00Z"), 4) === "2526" && IV.yearLabel(new Date("2026-04-01T12:00:00Z"), 4) === "2627" && IV.yearLabel(new Date("2026-04-01"), 1) === "26", "a fiscal year starts when its rule says");
    const unpaid = (await place(C4, [[X, 1]], "stripe")).body.order;
    ok((await C4("/api/orders/" + row(unpaid.num).id + "/invoice" + Q)).status === 409, "an unpaid order has no invoice");
    db.run("UPDATE orders SET state='Karnataka' WHERE num=?", n6);
    require("../lib/settings.js").save(1, { commerce: { taxMode: "gst" }, legal: { businessName: "Acme", address: "1 MG Road", state: "karnataka", taxId: "29ABCDE1234F1Z5" } });
    const iv = (await C4("/api/orders/" + o6.id + "/invoice" + Q)).body;
    ok(iv.invoice && /^INV\d{4}\/00001$/.test(iv.invoice.number) && iv.invoice.taxes.map(t => t.name).join() === "CGST,SGST", "an in-state order's tax is split, under the first number of the series", iv.invoice && [iv.invoice.number, iv.invoice.taxes]);
    const cents = n => Math.round(n * 100), sum = (xs, k) => xs.reduce((n, x) => n + cents(x[k]), 0);
    ok(sum(iv.invoice.lines, "taxable") === cents(iv.invoice.taxable) && sum(iv.invoice.lines, "tax") === cents(iv.invoice.tax) && sum(iv.invoice.taxes, "amount") === cents(iv.invoice.tax) && cents(iv.invoice.taxable) + cents(iv.invoice.tax) === cents(iv.invoice.total) && cents(iv.invoice.total) === cents(o6.total + o6.gift_used), "to the cent: lines, tax parts and the order agree", iv.invoice);
    ok(iv.invoice.lines[0].description !== X, "items are named, not numbered", iv.invoice.lines[0].description);
    ok(iv.credits.length === 3 && iv.credits.every(c => c.against === iv.invoice.number && /^CRN/.test(c.number)) && Math.abs(iv.credits.reduce((n, c) => n + c.total, 0) - p6.refunded) < 0.01, "each refund has its credit note", iv.credits.map(c => [c.number, c.total]));
    const twice = (await C4("/api/orders/" + o6.id + "/invoice" + Q)).body;
    ok(twice.invoice.number === iv.invoice.number && twice.credits.length === 3 && db.get("SELECT COUNT(*) c FROM invoice_documents WHERE order_id=?", o6.id).c === 4, "asking again issues nothing new");
    ok((await stranger("/api/orders/" + o6.id + "/invoice" + Q)).status === 404 && (await A("/api/admin/orders/" + o6.id + "/invoice" + Q)).status === 200, "only its buyer and the store's staff see it");
    const iv2 = (await A("/api/admin/orders/" + row(n5).id + "/invoice" + Q)).body.invoice;
    ok(/00002$/.test(iv2.number) && iv2.taxes.map(t => t.name).join() === "IGST", "the next order takes the next number, its tax as another state's", [iv2.number, iv2.taxes]);

    console.log("▸ LETTERS");
    const L = require("../lib/letters.js"), langs = Object.keys(L.SEED.letters.order_moved), holes = t => [...new Set((t.join("\n").match(/\{\w+\}/g) || []))].sort().join();
    const odd = []; for (const [k, by] of Object.entries(L.SEED.letters)) for (const l of langs) if (!by[l] || holes(by[l]) !== holes(by.en) || by[l].length !== by.en.length) odd.push(k + ":" + l);
    ok(!odd.length, "every letter says the same things in every language", odd);
    ok(!/\{|sent/.test(L.write("order_cancelled", "en", { num: "1" }).text) && L.write("order_cancelled", "en", { num: "1" }).text === "Your order has been cancelled.", "a line with nothing to say is left out");
    const H = await shopper(); await fetch(BASE + "/api/session"); const hi = await fetch(BASE + "/api/session"); void hi;
    const uid = db.get("SELECT MAX(id) m FROM users").m; db.run("UPDATE users SET lang='hi' WHERE id=?", uid);
    set(X, 10); const lo = (await place(H, [[X, 1]])).body.order.num; db.run("UPDATE users SET lang='hi' WHERE id=?", uid);
    await H("/api/orders/" + row(lo).id + "/cancel" + Q, "POST", {});
    ok(db.get("SELECT title t FROM notifications WHERE owner=? ORDER BY id DESC LIMIT 1", "t1:u:" + uid).t === "ऑर्डर " + lo + " रद्द", "a shopper is written to in their language", db.get("SELECT title t FROM notifications WHERE owner=? ORDER BY id DESC LIMIT 1", "t1:u:" + uid));
    ok(/Versandt/.test(L.write("order_moved", "de", { num: "1", state: "Shipped" }).subject) && L.write("order_moved", "ja", { num: "1", state: "Shipped" }).subject === "Order 1: Shipped", "states are named in it too; a language with no letters falls back");

    console.log("▸ ON THE MASTER");
    const OR = require("../lib/order-records.js"), K = require("../lib/kernel.js");
    const lr = row(lo), rec = OR.at(lr.id), hist = OR.statusHistory(lr.id).map(h => h.status);
    ok(rec && K.internal.nodeRow(lr.uid).kind === "commerce.order" && rec.num === lo && rec.total === Number(lr.total), "an order is on the master with its deal", rec);
    ok(hist[0] === hist.find(Boolean) && hist[hist.length - 1] === lr.status && hist.length >= 2, "its status history: as placed, and as it is now", hist);
    const person = db.get("SELECT uid FROM users WHERE id=?", uid).uid;
    ok(rec.buyer === person && OR.ordersOf(person).includes(lr.uid), "the person who placed it is a relationship");
    const pu = db.get("SELECT uid FROM products WHERE tenant_id=1 AND id=?", X).uid;
    ok(rec.lines.length === 1 && rec.lines[0].offering === pu && rec.lines[0].qty === 1, "its lines are the offerings bought", rec.lines);
    ok(!db.all("SELECT attrs FROM k_versions WHERE node=?", lr.uid).some(v => /Olive Order|1 Main St|@example\.com/.test(v.attrs)), "the buyer's name, address and email are not copied onto it");
    const seqO = K.lastSeq(); ok(OR.importRows() === 0 && K.lastSeq() === seqO, "every order is on the master, and a warm pass writes nothing");

    console.log("▸ CURRENCY");
    require("../lib/settings.js").save(1, { commerce: { taxMode: null } });
    const cfg = (await A("/api/config" + Q)).body.commerce;
    const other = db.get("SELECT code FROM currencies WHERE code<>? AND usd>0 AND decimals=2 AND ABS(usd-1)>0.3 ORDER BY code LIMIT 1", cfg.currency).code;
    require("../lib/security.js").setPolicy({ provisioning: { currencyOverridesAllowed: true } });
    await A("/api/admin/settings" + Q, "PUT", { commerce: { currency: other }, features: { fraudScreen: false } });
    set(X, 10);
    const fx = await place(await shopper(), [[X, 1]], "stripe");
    ok(fx.status === 200 && fx.body.order.currency === other && gateway.last["line_items[0][price_data][unit_amount]"] === String(Math.round(fx.body.order.total * 100)) && gateway.last["line_items[0][price_data][currency]"] === other.toLowerCase(), "the gateway is asked for exactly what the shopper was shown, in that currency", [other, fx.status, fx.body.error || fx.body.order.total, gateway.last["line_items[0][price_data][unit_amount]"]]);

    console.log("▸ PRODUCTION TAKES NO SIMULATED MONEY");
    const api = require("../lib/api.js");
    process.env.NODE_ENV = "production";
    db.run("UPDATE tenant_gateways SET mode='sandbox' WHERE tenant_id=1 AND provider_id='stripe'");
    const Z = mk(); await Z("/api/session" + Q); await Z("/api/cart" + Q, "POST", { id: X, qty: 1 });
    const free = await Z("/api/checkout" + Q, "POST", { ...dest, gateway: "stripe" });
    ok(free.status === 422 && !db.get("SELECT 1 x FROM orders WHERE owner LIKE ? AND pay_method='stripe' AND status='processing'", "%" + "none"), "a sandbox gateway takes no order", [free.status, free.body.error]);
    const cod = await Z("/api/checkout" + Q, "POST", { ...dest, gateway: "cod" });
    ok(cod.status === 200 && cod.body.order.payment_status === "pending", "cash on delivery still does, and waits to be recorded", [cod.status, cod.body.error || cod.body.order.payment_status]);
    delete process.env.NODE_ENV;
  } catch (e) { failed++; console.error("  ✗ harness error:", e && e.stack || e); }
  console.log(`\n${passed} passed, ${failed} failed`);
  for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
  process.exit(failed ? 1 : 0);
})();
