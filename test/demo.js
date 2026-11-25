/* LUXORA Platform — the local demo, end to end: the real server and the platform's own provider specs
   against the local stand-ins, driven over HTTP the way a person would. */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os"), { spawn } = require("child_process");
const DB = path.join(os.tmpdir(), "lx-demo-" + process.pid + ".db"), P = 8911, B = 8912, M = 8913, APP = "http://localhost:" + P, BOX = "http://localhost:" + B;
const clean = () => { for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } } };
clean();
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + JSON.stringify(x).slice(0, 500) : ""))); };
const sleep = ms => new Promise(r => setTimeout(r, ms)), until = async (fn, ms = 8000) => { for (let i = 0; i < ms / 100; i++) { const v = await fn(); if (v) return v; await sleep(100); } return null; };
const mk = store => { const c = new Map(); const f = async (p, m, b) => {
  const o = { method: m || "GET", headers: { Cookie: [...c].map(x => x[0] + "=" + x[1]).join("; "), "Content-Type": "application/json", "x-csrf": c.get("azc") || "" } };
  if (b !== undefined) o.body = JSON.stringify(b);
  const r = await fetch(APP + p + (p.includes("?") ? "&" : "?") + "store=" + store, o); r.headers.getSetCookie().forEach(k => { const kv = k.split(";")[0], i = kv.indexOf("="); c.set(kv.slice(0, i).trim(), kv.slice(i + 1).trim()); });
  const t = await r.text(); let body; try { body = JSON.parse(t); } catch (e) { body = { _raw: t }; } return { status: r.status, body };
}; return f; };
const mails = async () => (await fetch(BOX + "/mail.json")).json();
const press = (url, what) => fetch(BOX + "/pay/" + url.split("/").pop() + "/" + what, { method: "POST", redirect: "manual" });
(async () => {
  const srv = spawn(process.execPath, [path.join(__dirname, "..", "scripts", "demo.js")], { env: { ...process.env, NODE_ENV: "", LX_TEST: "", DEMO_DB: DB, DEMO_PORT: P, DEMO_SANDBOX_PORT: B, DEMO_SMTP_PORT: M }, stdio: ["ignore", "pipe", "pipe"] });
  let out = "", err = ""; srv.stdout.on("data", d => out += d); srv.stderr.on("data", d => err += d);
  ok(!!(await until(() => /Ctrl\+C/.test(out), 180000)), "npm run demo starts", err.slice(-400));
  try {
    ok(!/^demo:/m.test(err), "everything it prepares is prepared", err.slice(-300));
    ok((await fetch(BOX + "/")).ok && /platform@luxora\.shop/.test(await (await fetch(BOX + "/")).text()), "its home page lists the demo accounts");
    for (const [s, e, w] of [["luxora", "admin@luxora.shop", "admin123"], ["aurum", "admin@aurum.shop", "aurum123"], ["velora", "admin@velora.shop", "velora123"], ["luxora", "orders@luxora.shop", "Demo-Staff-1"], ["luxora", "support@luxora.shop", "Demo-Staff-1"], ["luxora", "shopper@luxora.shop", "Demo-Shop-1"], ["aurum", "shopper@aurum.shop", "Demo-Shop-1"]]) { const c = mk(s); await c("/api/session"); ok((await c("/api/auth/login", "POST", { email: e, password: w })).status === 200, e + " signs in"); }
    const PA = mk("luxora"); await PA("/api/session"); ok((await PA("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" })).status === 200, "the platform admin signs in");
    const shops = { luxora: ["stripe", "paypal"], aurum: ["razorpay"], velora: ["stripe"] };
    for (const [store, gws] of Object.entries(shops)) for (const gw of gws) {
      console.log("▸ " + store.toUpperCase() + " · " + gw);
      const A = mk(store); await A("/api/session"); await A("/api/auth/login", "POST", { email: "admin@" + store + ".shop", password: { luxora: "admin123" }[store] || store + "123" });
      const items = (await A("/api/products?limit=200")).body.items.filter(p => p.st > 5 && p.type === "physical" && !p.preorder), id = items[3].id;
      const buy = async () => { const C = mk(store); await C("/api/session"); const a = await C("/api/cart", "POST", { id, qty: 1 }); const r = await C("/api/checkout", "POST", { name: "Dee Demo", email: "dee@example.com", address: "1 Main St", city: "Seattle", state: "WA", zip: "98109", gateway: gw }); return { C, r, o: r.body.order, a }; };
      const s0 = (await A("/api/products/" + id)).body.product.st, one = await buy();
      ok(one.r.status === 200 && one.o.payment_status === "pending" && String(one.o.payment_redirect).startsWith(BOX + "/pay/"), "checkout sends the shopper to pay", one.r.body.error || one.o);
      if (!one.o) continue;
      const pg = await (await fetch(one.o.payment_redirect)).text();
      ok(pg.includes(one.o.num) && pg.includes(Number(one.o.total).toFixed(2)), "the page asks for the order's own total", one.o.total);
      const st = async (x) => (await x.C("/api/orders")).body.orders[0];
      ok((await st(one)).status === "pending_payment", "unpaid, the order waits");
      await press(one.o.payment_redirect, "paid");
      ok(!!(await until(async () => (await st(one)).status === "processing")), "paid, it goes to be packed", (await st(one)).status);
      const oid = (await st(one)).id, cx = await one.C("/api/orders/" + oid + "/cancel", "POST", {});
      ok(cx.status === 200 && Math.abs(cx.body.refunded - one.o.total) < 0.02, "cancelled, all of it is refunded by the gateway", cx.body);
      ok((await A("/api/products/" + id)).body.product.st === s0, "and it is back on the shelf");
      const two = await buy(); await press(two.o.payment_redirect, "failed");
      if (gw === "paypal") await two.C("/api/orders/" + (await st(two)).id + "/cancel", "POST", {});
      ok(!!(await until(async () => (await st(two)).status === "cancelled")), "declined, the order is cancelled", (await st(two)).status);
      ok((await A("/api/products/" + id)).body.product.st === s0, "and nothing was taken");
    }
    console.log("▸ EMAIL AND SMS");
    ok((await mails()).some(m => m.via === "Email" && /dee@example\.com/.test(m.to) && /^Order .* confirmed/.test(m.subject)), "a guest's confirmation reaches the mailbox");
    const N = mk("luxora"); await N("/api/session"); await N("/api/auth/register", "POST", { name: "Nia New", email: "nia@example.com", password: "Nia-Strong-99" });
    const v = await until(async () => (await mails()).find(m => /nia@example\.com/.test(m.to))), tok = v && /verify=([0-9a-f]{64})/.exec(v.text);
    ok(tok && (await N("/api/auth/email/verify", "POST", { token: tok[1] })).status === 200, "the link in the welcome email confirms the address", v);
    await N("/api/auth/password/forgot", "POST", { email: "nia@example.com" });
    const rs = await until(async () => (await mails()).find(m => /nia@example\.com/.test(m.to) && /Reset/.test(m.subject))), rt = rs && /token=([0-9a-f]{64})/.exec(rs.text);
    ok(rt && (await N("/api/auth/password/reset", "POST", { token: rt[1], password: "Nia-Newer-77" })).status === 200, "a forgotten password is reset from the mailbox", rs);
    const LA = mk("luxora"); await LA("/api/session"); await LA("/api/auth/login", "POST", { email: "admin@luxora.shop", password: "admin123" });
    const sms = await LA("/api/admin/notifiers/test/sms", "POST", { to: "+15550123456" });
    ok(sms.body.ok && (await mails()).some(m => m.via === "SMS"), "an SMS reaches it too", sms.body);

    console.log("▸ A PARCEL, FROM LABEL TO DOOR TO RETURN");
    await LA("/api/admin/settings", "PUT", { commerce: { shipRates: "live", shipFrom: { name: "LUXORA", street1: "1 Demo St", city: "Seattle", state: "WA", zip: "98101", country: "US" } } });
    const it = (await LA("/api/products?limit=200")).body.items.filter(p => p.st > 5 && p.type === "physical" && !p.preorder)[4], C = mk("luxora"); await C("/api/session"); await C("/api/auth/login", "POST", { email: "shopper@luxora.shop", password: "Demo-Shop-1" }); await C("/api/cart", "POST", { id: it.id, qty: 2 });
    const dest = { name: "Demo Shopper", address: "1 Main St", city: "Seattle", state: "WA", zip: "98109", gateway: "stripe" }, q = await C("/api/checkout/quote", "POST", dest);
    ok(q.body.source === "live" && q.body.rates.length === 3, "the carrier's own rates are offered", q.body);
    const co = await C("/api/checkout", "POST", { ...dest, rate_id: q.body.rates[0].id }); await press(co.body.order.payment_redirect, "paid");
    const mine = async () => (await C("/api/orders")).body.orders.find(o => o.num === co.body.order.num);
    await until(async () => (await mine()).status === "processing");
    const sh = await LA("/api/shipping/quote", "POST", { order_id: (await mine()).id, parcel: { weight_oz: 24 } }), lb = await LA("/api/shipping/label", "POST", { shipment_id: sh.body.shipment_id, shipment_ref: sh.body.shipment_id, rate_id: (sh.body.rates || [{}])[0].id, rate_ref: (sh.body.rates || [{}])[0].id, order_id: (await mine()).id });
    ok(lb.status === 200 && (await mine()).status === "shipped" && (await mine()).tracking.length === 1, "a label is bought and the order ships with its tracking number", [sh.body, lb.body]);
    const pid = /\/parcels\/(shp_[0-9a-f]+)\/delivered/.exec(await (await fetch(BOX + "/parcels")).text());
    if (pid) await fetch(BOX + "/parcels/" + pid[1] + "/delivered", { method: "POST", redirect: "manual" });
    ok(!!(await until(async () => (await mine()).status === "delivered")), "the carrier's word that it arrived delivers the order", (await mine()).status);
    const ret = await C("/api/returns", "POST", { order_num: co.body.order.num, product_id: it.id, qty: 1, reason: "demo" });
    ok(ret.status === 200, "one of two is returned", ret.body);
    const rf = await LA("/api/admin/returns/" + ret.body.returns[0].id, "PUT", { status: "refunded" });
    ok(rf.status === 200 && Math.abs(rf.body.refunded - ret.body.returns[0].worth) < 0.02, "and refunded through the gateway", rf.body);
    const inv = await C("/api/orders/" + (await mine()).id + "/invoice");
    ok(inv.status === 200 && inv.body.invoice.number && inv.body.credits.length === 1, "with an invoice and a credit note", inv.body);
    const AU = mk("aurum"); await AU("/api/session"); await AU("/api/auth/login", "POST", { email: "admin@aurum.shop", password: "aurum123" });
    const ao = (await AU("/api/admin/orders")).body.orders.find(o => o.payment && o.payment.gateway === "razorpay" && o.payment.status === "refunded");
    const gi = ao && (await AU("/api/admin/orders/" + ao.id + "/invoice"));
    ok(gi && gi.status === 200 && gi.body.invoice.title === "Tax invoice" && gi.body.invoice.taxes.some(t => /GST/.test(t.name)), "an Indian order's is a GST tax invoice", gi && gi.body);
  } catch (e) { failed++; console.error("  ✗ harness error:", e && e.stack || e, err.slice(-600)); }
  srv.kill("SIGTERM"); await sleep(400); srv.kill("SIGKILL"); clean();
  console.log(`\n${passed} passed, ${failed} failed`); process.exit(failed ? 1 : 0);
})();
