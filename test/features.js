/* LUXORA Platform — every shopper feature (lib/features/): off until switched on, set up through the
   console's own route, and met where a shopper meets it. The real server in this process. */
"use strict";
const path = require("path"), fs = require("fs"), crypto = require("crypto");
const DB = path.join(__dirname, "features.db");
const clean = () => { for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } } };
clean();
process.env.LX_DB = DB; process.env.PORT = "8903"; process.env.LX_LOG = ""; process.env.LX_OFFLINE = "1"; delete process.env.NODE_ENV;
const BASE = "http://localhost:8903", Q = "?store=luxora";
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + JSON.stringify(x).slice(0, 400) : ""))); };
const sleep = ms => new Promise(r => setTimeout(r, ms)), near = (a, b, d) => Math.abs(a - b) < (d || 0.02);
const mk = () => { const c = new Map(); return async (p, m, b) => {
  const o = { method: m || "GET", headers: { Cookie: [...c].map(x => x[0] + "=" + x[1]).join("; "), "Content-Type": "application/json", "x-csrf": c.get("azc") || "" } };
  if (b !== undefined) o.body = JSON.stringify(b);
  const r = await fetch(BASE + p + (p.includes("?") ? "&store=luxora" : Q), o); r.headers.getSetCookie().forEach(k => { const kv = k.split(";")[0], i = kv.indexOf("="); c.set(kv.slice(0, i).trim(), kv.slice(i + 1).trim()); });
  const t = await r.text(); let body; try { body = JSON.parse(t); } catch (e) { body = { _raw: t }; } return { status: r.status, body };
}; };
(async () => {
  const quiet = console.log; console.log = () => { }; require("../server.js"); const db = require("../lib/db.js"), F = require("../lib/features.js"), O = require("../lib/orders.js"); console.log = quiet;
  for (let i = 0; i < 160; i++) { try { if ((await fetch(BASE + "/readyz")).ok) break; } catch (e) { } await sleep(250); }
  try {
    const A = mk(); await A("/api/session"); await A("/api/auth/login", "POST", { email: "admin@luxora.shop", password: "admin123" });
    await A("/api/admin/settings", "PUT", { features: { fraudScreen: false } });
    /* plain items of this test's own */
    let n = 0; const item = (o) => { const id = "FT-" + (++n); db.run("INSERT INTO products(tenant_id,id,title,brand,dept,price,stock,lifecycle,type,attrs,logistics,identity) VALUES(1,?,?,?,?,?,?,'published','physical',?,?,?)", id, "Item " + n, (o || {}).brand || "FtBrand", (o || {}).dept || "ftdept", (o || {}).price || 100, (o || {}).stock == null ? 50 : o.stock, JSON.stringify((o || {}).attrs || {}), JSON.stringify((o || {}).logistics || {}), JSON.stringify((o || {}).identity || {})); const s = db.run("INSERT INTO skus(tenant_id,product_id,code,name,stock,active) VALUES(1,?,?,'Default',?,1)", id, id, (o || {}).stock == null ? 50 : o.stock); return { id, sku: Number(s.lastInsertRowid) }; };
    const set = async (key, params) => { db.run("INSERT INTO capability_values(tenant_id,capability,enabled,params) VALUES(1,?,1,?) ON CONFLICT(tenant_id,capability) DO UPDATE SET enabled=1, params=excluded.params", key, JSON.stringify(params || {})); await sleep(1100); };
    const off = async key => { db.run("UPDATE capability_values SET enabled=0 WHERE tenant_id=1 AND capability=?", key); await sleep(1100); };
    const row = async (key, b) => { const r = await A("/api/admin/features/" + key, "POST", b); if (r.status !== 200) throw new Error(key + ": " + JSON.stringify(r.body)); return r.body.rows[r.body.rows.length - 1]; };
    const guest = async () => { const C = mk(); await C("/api/session"); return C; };
    const shopper = async () => { const C = mk(), e = "f" + crypto.randomBytes(4).toString("hex") + "@example.com"; await C("/api/session"); const r = await C("/api/auth/register", "POST", { name: "Fee Ture", email: e, password: "Strong-Pass-99" }); C.id = r.body.user.id; C.email = e; return C; };
    const dest = { name: "Fee Ture", address: "1 Main St", city: "Seattle", state: "WA", zip: "98109", gateway: "cod", carrier: "house-std", email: "g@example.com" };
    const add = (C, id, terms, qty) => C("/api/cart", "POST", { id, qty: qty || 1, terms });
    const buy = async (C, id, o) => { const a = await add(C, id, (o || {}).terms, (o || {}).qty); if (a.status !== 200) return a; return C("/api/checkout", "POST", { ...dest, ...((o || {}).body || {}) }); };
    const ord = r => db.get("SELECT * FROM orders WHERE num=?", r.body.order.num);
    const deliver = async o => { await O.setStatus(1, O.orderOf(1, o.id), "shipped", {}); await O.setStatus(1, O.orderOf(1, o.id), "delivered", {}); };
    const block = async (C, id, key) => ((await C("/api/products/" + id)).body.features || []).find(b => b.key === key);
    const keys = [...F.defs.keys()];

    console.log("▸ THE FRAME");
    ok(keys.length === 26 && keys.every(k => F.engines.has(k)) && [...F.engines.keys()].every(k => F.defs.has(k)), "every declared feature has its engine, and every engine its declaration");
    for (const k of keys) db.run("INSERT INTO capability_values(tenant_id,capability,enabled,params) VALUES(1,?,0,'{}') ON CONFLICT(tenant_id,capability) DO UPDATE SET enabled=0", k);
    await sleep(1100);
    const refused = []; for (const k of keys) if ((await A("/api/admin/features/" + k, "POST", {})).status !== 403) refused.push(k);
    ok(!refused.length, "each is refused until switched on", refused);
    const G = await guest();
    ok((await G("/api/admin/features/sale_events")).status === 403, "a shopper cannot set one up");
    ok((await A("/api/admin/features/constructor")).status === 404 && (await G("/api/features/sale_events/constructor", "POST", {})).status !== 200, "nothing undeclared is reached");

    console.log("▸ PRICES");
    const a = item(), now = Date.now(), iso = d => new Date(now + d * 864e5).toISOString();
    await set("sale_events");
    ok((await A("/api/admin/features/sale_events", "POST", { name: "x", starts: iso(1), ends: iso(0), percent: 10 })).status === 400 && (await A("/api/admin/features/sale_events", "POST", { name: "x", starts: iso(0), ends: iso(1), percent: 500 })).status === 400, "a sale ends after it starts, and takes a sensible share");
    await row("sale_events", { name: "Spring", starts: iso(-1), ends: iso(1), percent: 20, target: a.id, per_order: 2 }); await row("sale_events", { name: "Later", starts: iso(1), ends: iso(2), percent: 90, target: a.id });
    ok(near((await G("/api/products/" + a.id)).body.product.p, 80) && (await G("/api/products/" + a.id)).body.product.l === 100, "on sale: the lower price, with the one before it", (await G("/api/products/" + a.id)).body.product);
    const s1 = await add(G, a.id, undefined, 9); ok(near(s1.body.items[0].unit, 80) && s1.body.items[0].qty === 2, "and in the bag, no more than it allows", s1.body.items[0]); await off("sale_events");
    const b = item(); await set("club_pricing"); await row("club_pricing", { tier: "*", percent: 10, target: b.id });
    const M = await shopper(); db.run("INSERT INTO memberships(tenant_id,owner,tier,status) VALUES(1,?,'plus','active')", "t1:u:" + M.id);
    ok(near((await add(M, b.id)).body.items[0].unit, 90) && near((await add(await guest(), b.id)).body.items[0].unit, 100), "members pay less, others do not"); await off("club_pricing");
    const c = item(); await set("live_selling"); await row("live_selling", { name: "Show", starts: iso(-0.01), ends: iso(1), stream: "https://video.example.com/x", products: c.id, percent: 50 });
    ok((await A("/api/admin/features/live_selling", "POST", { name: "x", starts: iso(0), ends: iso(1), stream: "javascript:alert(1)", products: c.id })).status === 400, "a stream is an https link");
    ok(near((await add(await guest(), c.id)).body.items[0].unit, 50) && (await G("/api/features/live_selling")).body.shows[0].live === true, "while a show is on its items are at its price"); await off("live_selling");

    console.log("▸ PAYING");
    const d = item(); await set("payment_instrument_offers"); await row("payment_instrument_offers", { name: "Cash 10%", gateway: "cod", percent: 10, max_off: 8, min_amount: 50 });
    const P1 = await guest(), base = await buy(P1, d.id), o1 = ord(base);
    ok(JSON.parse(o1.charges).some(x => x.amount === -8), "money off for the way it is paid, up to its most", o1.charges);
    const P2 = await guest(); await add(P2, d.id); const q2 = await P2("/api/checkout/quote", "POST", { ...dest, gateway: "stripe" });
    ok(!(q2.body.charges || []).some(x => x.amount < 0), "and not for another way"); await off("payment_instrument_offers");
    await set("instalments_without_cost"); await row("instalments_without_cost", { gateway: "cod", months: "3, 6", min_amount: 50 });
    ok((await G("/api/features/instalments_without_cost?amount=300")).body.plans.map(x => x.months).join() === "3,6", "plans are offered for the amount");
    const I1 = await guest(); ok((await buy(I1, d.id, { body: { instalments: 12 } })).status === 422, "one that is not offered is refused");
    const i2 = await I1("/api/checkout", "POST", { ...dest, instalments: 3 }); ok(i2.status === 200 && F.records(1, "instalments_without_cost", { about: i2.body.order.num })[0].months === 3, "the one chosen is kept on the order", i2.body); 
    const spec = require("../lib/spec.js"), RZ = require("../lib/seed/providers.json").PROVIDER_SPECS["payment:razorpay"], sent = async extra => { let b; await spec.execute(RZ, { config: { keyId: "k", keySecret: "s" }, amount: 300, currency: "INR", idempotency: "n", extra }, async (u, o) => { b = JSON.parse(o.body); return { ok: true, status: 200, json: { id: "x", status: "created" } }; }); return b; };
    ok((await sent({ gatewayOffer: "offer_1" })).options.order.offers[0] === "offer_1" && !("options" in await sent({})), "the plan's offer reaches the gateway, and only when there is one"); await off("instalments_without_cost");

    console.log("▸ ABROAD");
    const e = item({ identity: { hs: "6109.10", origin: "IN" } }), e2 = item(); await set("duties_at_checkout"); await row("duties_at_checkout", { country: "GB", percent: 5 }); await row("duties_at_checkout", { country: "GB", code: "6109", percent: 12 });
    const D1 = await guest(), dr = await buy(D1, e.id, { body: { country: "GB" } });
    ok(dr.status === 200 && JSON.parse(ord(dr).charges).some(x => /duty/i.test(x.name) && near(x.amount, 12)), "the most particular rate is charged", dr.body.error || ord(dr).charges);
    const dh = await buy(await guest(), e.id); ok(!JSON.parse(ord(dh).charges).some(x => /duty/i.test(x.name)), "nothing at home"); await off("duties_at_checkout");
    await set("customs_declarations"); const cu = await buy(await guest(), e.id, { body: { country: "GB" } }), cr = F.records(1, "customs_declarations", { about: cu.body.order.num })[0];
    const doc = await A("/api/admin/features/customs_declarations/document/" + cr.id, "POST", {}); ok(doc.body.document && doc.body.document.items[0].code === "6109.10" && doc.body.document.items[0].origin === "IN" && near(doc.body.document.value, 100), "a declaration is made from the order", doc.body);
    ok((await A("/api/admin/features/customs_declarations/declare/" + cr.id, "POST", {})).status === 200 && (await A("/api/admin/features/customs_declarations/declare/" + cr.id, "POST", {})).status === 409, "declared once");
    const cu2 = await buy(await guest(), e2.id, { body: { country: "GB" } }), cr2 = F.records(1, "customs_declarations", { about: cu2.body.order.num })[0]; ok((await A("/api/admin/features/customs_declarations/declare/" + cr2.id, "POST", {})).status === 409, "never without its customs codes"); await off("customs_declarations");

    console.log("▸ SENDING");
    const cheap = item({ price: 10 }); await set("consolidated_shipping", { hours: 24 });
    const S1 = await shopper(), f1 = ord(await buy(S1, cheap.id)), f2 = ord(await buy(S1, cheap.id)), f3 = ord(await buy(S1, cheap.id, { body: { address: "9 Other St" } }));
    ok(f1.ship_fee > 0 && f2.ship_fee === 0 && f3.ship_fee > 0, "a second order to the same address leaves with the first, free", [f1.ship_fee, f2.ship_fee, f3.ship_fee]); await off("consolidated_shipping");
    const g1 = item(), g2 = item(); await set("supplier_direct"); await row("supplier_direct", { name: "Sup", email: "sup@example.com", target: g1.id, days: 4 });
    const so = ord(await buy(await guest(), g1.id)), sr = F.records(1, "supplier_direct", { about: so.num })[0]; ok(sr.state === "sent" && sr.lines[0].id === g1.id && so.eta_days >= 4, "a supplier's part goes to them at once");
    ok((await A("/api/admin/features/supplier_direct/shipped/" + sr.id, "POST", { value: "TRK1" })).status === 200 && O.orderOf(1, so.id).status === "shipped", "when they have sent it the order ships"); await off("supplier_direct");
    const h = item(); await set("cold_chain", { carriers: "house-exp", fee: 3 }); await row("cold_chain", { target: h.id, min_c: 2, max_c: 8 });
    const C1 = await guest(); ok((await buy(C1, h.id)).status === 422, "what must stay cold goes only by those who keep it so");
    const co = await C1("/api/checkout", "POST", { ...dest, carrier: "house-exp" }), cold = co.status === 200 && F.records(1, "cold_chain", { about: co.body.order.num })[0]; ok(!!cold, "and then its temperature is kept", co.body);
    ok((await A("/api/admin/features/cold_chain/reading/" + cold.id, "POST", { value: "5" })).body.outOfRange === false && (await A("/api/admin/features/cold_chain/reading/" + cold.id, "POST", { value: "11" })).body.outOfRange === true && (await A("/api/admin/features/cold_chain/reading/" + cold.id, "POST", { value: "" })).status === 400, "a reading outside its range is raised"); await off("cold_chain");
    const lg = item({ logistics: { shippingClass: "oversized" } }); await set("large_item_delivery"); const lo = await row("large_item_delivery", { name: "Room of choice", fee: 25, days: 2 });
    const L1 = await guest(); ok((await buy(L1, lg.id)).status === 422, "a large item asks how it is brought in"); const l2 = await L1("/api/checkout", "POST", { ...dest, large_option: lo.id }); ok(l2.status === 200 && ord(l2).ship_fee >= 25, "and charges for it", l2.body); await off("large_item_delivery");
    await set("dated_delivery", { min_days: 1, days_ahead: 30 }); const day = x => new Date(now + x * 864e5).toISOString().slice(0, 10);
    const DD = await guest(); ok((await buy(DD, d.id, { body: { deliver_on: day(90) } })).status === 422, "a day too far is refused"); const d2 = await DD("/api/checkout", "POST", { ...dest, deliver_on: day(5), gift_note: "Happy day" }); ok(d2.status === 200 && F.records(1, "dated_delivery", { about: d2.body.order.num })[0].on === day(5), "a gift keeps its day and message", d2.body); await off("dated_delivery");

    console.log("▸ SELLING ON");
    const rm = item(); await set("reseller_margins", { max_percent: 30 }); const R = await shopper();
    ok((await add(R, rm.id, { resale: { margin: 31 } })).status === 400 && (await add(await guest(), rm.id, { resale: { margin: 5 } })).status === 401, "a margin has its most, and a reseller signs in");
    const ro = ord(await buy(R, rm.id, { terms: { resale: { margin: 20 } } })); ok(near(ro.sub, 120), "it is added to the price", ro.sub);
    const bal = async C => Number(require("../lib/wallet.js").walletsOf(1, "t1:u:" + C.id).reduce((n, w) => n + Number(w.posted != null ? w.posted : w.balance || 0), 0)); const b0 = await bal(R); await deliver(ro); ok(near(await bal(R) - b0, 20) && F.records(1, "reseller_margins", { about: ro.num })[0].state === "paid", "and paid to their wallet on delivery", [b0, await bal(R)]); await off("reseller_margins");
    await set("affiliate_commissions", { days: 30 }); await row("affiliate_commissions", { code: "amy1", email: "amy@example.com", percent: 10 });
    const V = await guest(); ok((await V("/api/features/affiliate_commissions/visit", "POST", { code: "nobody" })).body.ok === false, "an unknown code earns nothing"); await V("/api/features/affiliate_commissions/visit", "POST", { code: "AMY1" });
    const ao = ord(await buy(V, d.id)), ar = F.records(1, "affiliate_commissions", { about: ao.num })[0]; ok(ar && near(ar.amount, 10) && ar.state === "waiting", "the one who sent the shopper is owed a share", ar);
    await deliver(ao); ok(F.records(1, "affiliate_commissions", { about: ao.num })[0].state === "earned" && (await A("/api/admin/features/affiliate_commissions/paid/" + ar.id, "POST", { value: "ref" })).status === 200, "earned on delivery, and paid by staff");
    const V2 = await guest(); await V2("/api/features/affiliate_commissions/visit", "POST", { code: "amy1" }); const own = ord(await buy(V2, d.id, { body: { email: "AMY@example.com" } })); ok(!F.records(1, "affiliate_commissions", { about: own.num }).length, "never on their own order"); await off("affiliate_commissions");
    await set("gamified_rewards", { first: 0.5, more: 0.25, most: 1 }); const W = await shopper(); const two = await Promise.all([0, 1].map(() => W("/api/features/gamified_rewards/checkin", "POST", {})));
    ok(two.map(x => x.status).sort().join() === "200,409" && near(await bal(W), 0.5), "a check-in is once a day", [two.map(x => x.body), await bal(W)]); ok((await (await guest())("/api/features/gamified_rewards/checkin", "POST", {})).status === 401, "and signed in"); await off("gamified_rewards");
    const fu = item(), fm = item(); await set("funding_goals"); await row("funding_goals", { product_id: fu.id, goal: 1000, ends: iso(1) }); await row("funding_goals", { product_id: fm.id, goal: 100, ends: iso(1) });
    const p1 = ord(await buy(await guest(), fu.id)), p2 = ord(await buy(await guest(), fm.id)); ok(/10%/.test((await block(G, fu.id, "funding_goals")).text), "its item shows what is pledged", await block(G, fu.id, "funding_goals"));
    db.run("UPDATE feature_rows SET data=REPLACE(data, ?, ?) WHERE feature='funding_goals'", iso(1), iso(-0.01)); await sleep(1100); ok((await add(await guest(), fu.id)).status === 409, "once closed, nothing more is pledged"); await F.sweepAll();
    ok(O.orderOf(1, p1.id).status === "cancelled" && O.orderOf(1, p2.id).status === "processing", "a goal missed cancels its pledges, a goal met goes ahead", [O.orderOf(1, p1.id).status, O.orderOf(1, p2.id).status]); await off("funding_goals");

    console.log("▸ CHOOSING");
    const ev = item({ stock: 100 }); await set("seat_maps", { hold_minutes: 10 }); ok((await A("/api/admin/features/seat_maps", "POST", { product_id: ev.id, layout: "nonsense" })).status === 400, "a layout is rows of seats"); await row("seat_maps", { product_id: ev.id, venue: "Hall", layout: "A:1-3=150\nB:1-3" });
    ok((await add(await guest(), ev.id)).status === 409, "a seat is chosen"); const E1 = await guest(), E2 = await guest(); const both = await Promise.all([E1, E2].map(C => add(C, ev.id, { seat: { seat: "A1" } }))); ok(both.map(x => x.status).sort().join() === "200,409", "one seat, one shopper", both.map(x => x.status));
    const win = both[0].status === 200 ? E1 : E2, lose = win === E1 ? E2 : E1; const sm = (await lose("/api/features/seat_maps?product=" + ev.id)).body; ok(sm.seats.find(x => x.seat === "A1").free === false && sm.seats.find(x => x.seat === "A1").price === 150 && sm.seats.length === 6, "a seat held is shown taken");
    const eo = await win("/api/checkout", "POST", dest); ok(eo.status === 200 && near(ord(eo).sub, 150), "it is sold at its own price", eo.body); await O.cancel(1, O.orderOf(1, ord(eo).id), {}); ok((await add(lose, ev.id, { seat: { seat: "A1" } })).status === 200, "a cancelled seat is free again"); await off("seat_maps");
    const tr = item(); await set("travel_itineraries"); await row("travel_itineraries", { product_id: tr.id, days: "Arrive\nHike\nHome", notice_days: 3 }); ok((await add(await guest(), tr.id)).status === 409 && (await add(await guest(), tr.id, { trip: { starts: day(1) } })).status === 400, "a trip starts on a day, with notice");
    const TR = await shopper(); await buy(TR, tr.id, { terms: { trip: { starts: day(10), travellers: "Two" } } }); const tm = (await TR("/api/features")).body.features.find(x => x.key === "travel_itineraries"); ok(tm && tm.rows[0].rows.length === 3 && tm.rows[0].rows[1][0] === day(11), "the order carries its plan, day by day", tm); await off("travel_itineraries");
    const pt = item(); await set("fitment"); await row("fitment", { product_id: pt.id, make: "Honda", model: "City", from_year: 2015, to_year: 2020 }); const FT = await shopper(); ok((await FT("/api/features/fitment/add", "POST", { make: "Honda", model: "City", year: 1800 })).status === 400, "a vehicle has a real year"); await FT("/api/features/fitment/add", "POST", { make: "honda", model: "city", year: 2018 });
    ok(/^✓/.test((await block(FT, pt.id, "fitment")).title), "a part says it fits the shopper's vehicle"); const FN = await shopper(); await FN("/api/features/fitment/add", "POST", { make: "Honda", model: "City", year: 2022 }); ok(/^✗/.test((await block(FN, pt.id, "fitment")).title) && (await G("/api/features/fitment?make=Honda&model=City&year=2016")).body.products[0] === pt.id, "or that it does not"); await off("fitment");
    const wt = item({ price: 10, stock: 100 }); await set("sell_by_weight"); await row("sell_by_weight", { product_id: wt.id, unit: "kg", min: 0.25, max: 5, step: 0.25 }); ok((await add(await guest(), wt.id)).status === 409 && (await add(await guest(), wt.id, { weight: { amount: 0.3 } })).status === 400 && (await add(await guest(), wt.id, { weight: { amount: 9 } })).status === 400, "an amount is chosen, in its steps");
    const wo = ord(await buy(await guest(), wt.id, { terms: { weight: { amount: 1.5 } } })); ok(near(wo.sub, 15) && db.get("SELECT stock s FROM products WHERE id=?", wt.id).s === 94, "priced by its amount, its stock by steps", [wo.sub, db.get("SELECT stock s FROM products WHERE id=?", wt.id).s]); await O.cancel(1, O.orderOf(1, wo.id), {}); ok(db.get("SELECT stock s FROM products WHERE id=?", wt.id).s === 100, "and back again"); await off("sell_by_weight");

    console.log("▸ MEDICINE AND FOOD");
    const rx = item({ attrs: { schedule: "H" } }), ban = item({ attrs: { schedule: "X" } }), otc = item({ attrs: { schedule: "G" } }); await set("schedule_rules", { attr: "schedule", case_kind: "prescription" }); await row("schedule_rules", { schedule: "H", sold: true, prescription: true }); await row("schedule_rules", { schedule: "X", sold: false }); await row("schedule_rules", { schedule: "G", sold: true, max_qty: 2 });
    ok((await add(await guest(), rx.id)).status === 409 && (await add(await guest(), ban.id)).status === 409, "a prescription is needed, or it is not sold"); ok((await add(await guest(), otc.id, undefined, 9)).body.items[0].qty === 2, "no more than its schedule allows"); await off("schedule_rules");
    const br = item({ dept: "rx", price: 100, attrs: { composition: "Paracetamol 500mg + Caffeine", strength: "500", form: "tab" } }), gen = item({ dept: "rx", price: 30, attrs: { composition: "caffeine + PARACETAMOL 500MG", strength: "500", form: "tab" } }); item({ dept: "rx", price: 20, attrs: { composition: "Ibuprofen", strength: "500", form: "tab" } });
    await set("generic_alternatives", { attrs: "composition strength form" }); const ga = await block(G, br.id, "generic_alternatives"); ok(ga && ga.products.length === 1 && ga.products[0].id === gen.id && ga.products[0].saves === 70, "the same medicine, for less", ga); await off("generic_alternatives");
    const rf = item(); await set("refill_reminders", { days_before: 3 }); await row("refill_reminders", { target: rf.id, days: 30 }); const RF = await shopper(), rfo = ord(await buy(RF, rf.id, { qty: 2 })); await deliver(rfo); const rr = F.records(1, "refill_reminders", { about: rfo.num })[0]; ok(rr && rr.on === day(57), "a reminder is set for before it runs out", rr);
    db.run("UPDATE feature_records SET data=REPLACE(data, ?, ?) WHERE id=?", rr.on, day(-1), rr.id); await F.sweepAll(); await F.sweepAll(); ok(F.records(1, "refill_reminders", { id: rr.id })[0].state === "told" && db.get("SELECT COUNT(*) c FROM notifications WHERE owner=? AND title LIKE 'Time to refill%'", "t1:u:" + RF.id).c === 1, "and told once"); await off("refill_reminders");
    const KH = require("../lib/features/kitchen_hours.js"); ok(KH.isOpen([{ weekday: 1, opens: "18:00", closes: "02:00" }], { dow: 2, min: 60 }) && !KH.isOpen([{ weekday: 1, opens: "18:00", closes: "02:00" }], { dow: 1, min: 60 }), "hours past midnight belong to the day they open");
    const kf = item(), wd = new Date().getUTCDay(); await set("kitchen_hours"); await row("kitchen_hours", { weekday: (wd + 3) % 7, opens: "10:00", closes: "11:00", target: kf.id }); const kc = await add(await guest(), kf.id); ok(kc.status === 409 && /opens/.test(kc.body.error), "closed, it cannot be ordered, and says when it opens", kc.body); ok((await add(await guest(), d.id)).status === 200, "other items can"); await off("kitchen_hours");
    const fx = item({ stock: 9 }); for (const [q, exp] of [[3, day(-1)], [2, day(4)], [4, day(40)]]) db.run("INSERT INTO inventory(tenant_id,sku_id,qty,expiry,batch) VALUES(1,?,?,?,?)", fx.sku, q, exp, exp); await set("batch_expiry", { min_days: 2 });
    ok((await add(await guest(), fx.id, undefined, 9)).body.items[0].qty === 6, "what has expired is not sold"); await buy(await guest(), fx.id, { qty: 3 }); const bq = db.all("SELECT qty FROM inventory WHERE sku_id=? ORDER BY expiry", fx.sku).map(x => x.qty); ok(bq.join() === "3,0,3", "the first to expire leaves first", bq);
    await set("freshness_windows"); await row("freshness_windows", { target: fx.id, days: 30 }); ok((await add(await guest(), fx.id, undefined, 9)).body.items[0].qty === 3 && /30 days/.test((await block(G, fx.id, "freshness_windows")).title), "a freshness promise is kept"); await row("freshness_windows", { target: fx.id, days: 60 }); ok((await add(await guest(), fx.id)).status === 409, "or it is not sold");
    const wl = (await A("/api/admin/features/batch_expiry")).body.list.find(x => /expired/.test(x.chip) && x.text.includes("Item")); ok(wl && (await A("/api/admin/features/batch_expiry/writeoff/" + wl.id, "POST", {})).body.qty === 3 && db.get("SELECT stock s FROM products WHERE id=?", fx.id).s === 3, "an expired batch is written off the counts", db.get("SELECT stock s FROM products WHERE id=?", fx.id).s); await off("batch_expiry"); await off("freshness_windows");
  } catch (e) { failed++; console.error("  ✗ harness error:", e && e.stack || e); }
  console.log(`\n${passed} passed, ${failed} failed`); clean(); process.exit(failed ? 1 : 0);
})();
