/* LUXORA Platform — delivery slots, serviceable areas, size guides and pre-orders: each switched on,
   set up from the console and met at checkout. The real server in this process. */
"use strict";
const path = require("path"), fs = require("fs"), crypto = require("crypto");
const DB = path.join(__dirname, "fulfil.db");
const clean = () => { for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } } };
clean();
process.env.LX_DB = DB; process.env.PORT = "8901"; process.env.LX_LOG = ""; process.env.LX_OFFLINE = "1"; delete process.env.NODE_ENV;
const BASE = "http://localhost:8901", Q = "?store=luxora";
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + JSON.stringify(x) : ""))); };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const mk = () => { const c = new Map(); return async (p, m, b) => {
  const o = { method: m || "GET", headers: { Cookie: [...c].map(x => x[0] + "=" + x[1]).join("; "), "Content-Type": "application/json", "x-csrf": c.get("azc") || "" } };
  if (b !== undefined) o.body = JSON.stringify(b);
  const r = await fetch(BASE + p, o); r.headers.getSetCookie().forEach(k => { const kv = k.split(";")[0], i = kv.indexOf("="); c.set(kv.slice(0, i).trim(), kv.slice(i + 1).trim()); });
  const t = await r.text(); let body; try { body = JSON.parse(t); } catch (e) { body = { _raw: t }; } return { status: r.status, body };
}; };
(async () => {
  const quiet = console.log; console.log = () => { }; require("../server.js"); const db = require("../lib/db.js"); console.log = quiet;
  for (let i = 0; i < 160; i++) { try { if ((await fetch(BASE + "/readyz")).ok) break; } catch (e) { } await sleep(250); }
  const caps = require("../lib/capabilities.js");
  const set = (key, on, params) => { db.run("INSERT INTO capability_values(tenant_id,capability,enabled,params) VALUES(1,?,?,?) ON CONFLICT(tenant_id,capability) DO UPDATE SET enabled=excluded.enabled, params=excluded.params", key, on ? 1 : 0, JSON.stringify(params || {})); if (caps.bust) caps.bust(1); };
  try {
    const A = mk(); await A("/api/session" + Q); await A("/api/auth/login" + Q, "POST", { email: "admin@luxora.shop", password: "admin123" });
    await A("/api/admin/settings" + Q, "PUT", { features: { fraudScreen: false } });
    const P = db.all("SELECT id, brand, dept FROM products WHERE tenant_id=1 AND type='physical' AND lifecycle='published' AND deleted_at IS NULL AND stock>10 AND price BETWEEN 10 AND 30 ORDER BY id LIMIT 2");
    const X = P[0].id, dest = { name: "Fay Fulfil", address: "1 Main St", city: "Seattle", state: "WA", zip: "560001", gateway: "cod", carrier: "house-std" };
    const buy = async (extra, id) => { const C = mk(); await C("/api/session" + Q); const a = await C("/api/cart" + Q, "POST", { id: id || X, qty: 1 }); const r = await C("/api/checkout" + Q, "POST", { ...dest, ...extra }); return { C, a, r, q: () => C("/api/checkout/quote" + Q, "POST", { ...dest, ...extra }) }; };

    console.log("▸ OFF UNTIL SWITCHED ON");
    ok((await A("/api/admin/delivery-windows" + Q, "POST", { weekday: 1, starts: "09:00", ends: "12:00" })).status === 403, "delivery slots");
    ok((await A("/api/admin/serviceable-areas" + Q, "POST", { name: "x", postcodes: "1" })).status === 403, "serviceable areas");
    ok((await A("/api/admin/size-guides" + Q, "POST", { name: "x", scope: "item", target: X, rows: "a,b\n1,2" })).status === 403, "size guides");
    ok((await A("/api/admin/preorders" + Q, "POST", { product_id: X, ships_on: "2099-01-01", max_qty: 1 })).status === 403, "pre-orders");

    console.log("▸ DELIVERY SLOTS");
    set("delivery_slots", true, { days_ahead: 9, cutoff_minutes: 60, required: true });
    for (const bad of [{ weekday: 9, starts: "09:00", ends: "12:00" }, { weekday: 1, starts: "12:00", ends: "09:00" }, { weekday: 1, starts: "9am", ends: "12:00" }]) ok((await A("/api/admin/delivery-windows" + Q, "POST", bad)).status === 400, "refused: " + JSON.stringify(bad));
    ok((await buy({})).r.status === 200, "with no window set, nothing is asked");
    const DW = require("../lib/delivery-windows.js");
    const dow = (new Date().getUTCDay() + 3) % 7;
    await A("/api/admin/delivery-windows" + Q, "POST", { weekday: dow, starts: "09:00", ends: "12:00", capacity: 1, fee: 4 });
    const C0 = mk(); await C0("/api/session" + Q);
    const slots = (await C0("/api/shipping/slots" + Q)).body.slots;
    ok(slots.length >= 1 && slots.every(s => new Date(s.day + "T00:00:00Z").getUTCDay() === dow && s.left === 1), "its dates ahead are offered", slots);
    ok((await buy({})).r.status === 422, "a choice is asked for");
    ok((await buy({ delivery_slot: "1@1999-01-01" })).r.status === 409, "a made-up time is refused");
    const n0 = db.get("SELECT COUNT(*) c FROM orders").c;
    const [s1, s2] = await Promise.all([buy({ delivery_slot: slots[0].key }), buy({ delivery_slot: slots[0].key })]);
    ok([s1, s2].map(x => x.r.status).sort().join() === "200,409", "the last place goes to one of two", [s1.r.body.error, s2.r.body.error]);
    const won = s1.r.status === 200 ? s1 : s2, plain = db.get("SELECT ship_fee f FROM orders WHERE id=(SELECT MIN(id) FROM orders WHERE owner LIKE 't1:s:%')").f;
    const o = db.get("SELECT * FROM orders WHERE num=?", won.r.body.order.num);
    ok(Math.abs(o.ship_fee - plain - 4) < 0.01, "its fee is on the order", [o.ship_fee, plain]);
    ok((await won.C("/api/orders" + Q)).body.orders[0].slot.day === slots[0].day, "the shopper sees it on their order");
    ok((await A("/api/admin/delivery-windows" + Q)).body.schedule.some(b => b.num === o.num), "staff see the day's deliveries");
    ok(!(await C0("/api/shipping/slots" + Q)).body.slots.some(s => s.key === slots[0].key), "a full time is no longer offered");
    await won.C("/api/orders/" + o.id + "/cancel" + Q, "POST", {});
    ok((await C0("/api/shipping/slots" + Q)).body.slots.some(s => s.key === slots[0].key), "cancelling frees it");
    set("delivery_slots", false);

    console.log("▸ SERVICEABLE AREAS");
    set("serviceable_areas", true, { message: "Not there yet" });
    ok((await buy({ zip: "99999" })).r.status === 200, "with no area set the store delivers everywhere");
    ok((await A("/api/admin/serviceable-areas" + Q, "POST", { name: "bad", postcodes: "110099-110001" })).status === 400, "a range runs upwards");
    await A("/api/admin/serviceable-areas" + Q, "POST", { name: "South", postcodes: "560*, 110001-110099 SW1A1AA", fee: 3, extra_days: 2 });
    const SA = require("../lib/serviceable-areas.js");
    ok(["560001", "110050", "sw1a 1aa"].every(z => SA.check(1, z).served) && ["56", "110100", "11005", "SW1A1AB", ""].every(z => !SA.check(1, z).served), "postcodes, beginnings and ranges", ["56", "110100", "11005", "SW1A1AB", ""].map(z => SA.check(1, z).served));
    const out = await buy({ zip: "99999" });
    ok(out.r.status === 422 && /Not there yet/.test(out.r.body.error), "outside, the order is refused before anything is charged", out.r.body);
    const inn = await buy({ zip: "560034" });
    ok(inn.r.status === 200 && Math.abs(db.get("SELECT ship_fee f FROM orders WHERE num=?", inn.r.body.order.num).f - plain - 3) < 0.01, "inside, its fee is added", inn.r.body.error);
    set("serviceable_areas", false);

    console.log("▸ SIZE GUIDES");
    set("size_guides", true, { label: "Find your size" });
    ok((await A("/api/admin/size-guides" + Q, "POST", { name: "x", scope: "item", target: X, rows: "Size,Chest\nS" })).status === 400, "every row is as wide as the heading");
    await A("/api/admin/size-guides" + Q, "POST", { name: "Dept", scope: "dept", target: P[0].dept, rows: "Size,Chest\nS,90" });
    const g = async () => (await C0("/api/products/" + X + "/size-guide" + Q)).body;
    ok((await g()).guide.name === "Dept", "an item shows its department's");
    await A("/api/admin/size-guides" + Q, "POST", { name: "Own", scope: "item", target: X, rows: "Size,Chest\nS,<b>" });
    ok((await g()).guide.name === "Own" && (await g()).label === "Find your size", "or its own, where it has one");

    console.log("▸ PRE-ORDERS");
    set("preorders", true, {}); await sleep(1100);
    ok((await A("/api/admin/preorders" + Q, "POST", { product_id: X, ships_on: "2001-01-01", max_qty: 5 })).status === 400, "the day is in the future");
    db.run("UPDATE products SET stock=0 WHERE tenant_id=1 AND id=?", X);
    ok((await buy({})).a.status === 400, "sold out, it cannot be bought");
    const day = new Date(Date.now() + 20 * 864e5).toISOString().slice(0, 10);
    await A("/api/admin/preorders" + Q, "POST", { product_id: X, ships_on: day, max_qty: 2 });
    ok((await C0("/api/products/" + X + Q)).body.product.preorder.ships_on === day, "on pre-order, the shopper is told the day");
    const p1 = await buy({}), p2 = await buy({}), p3 = await buy({});
    ok(p1.r.status === 200 && p2.r.status === 200 && p3.a.status === 400, "as many as may be promised, and no more", [p1.r.body.error, p2.r.body.error, p3.a.body.error]);
    ok(db.get("SELECT stock s FROM products WHERE tenant_id=1 AND id=?", X).s === 0, "the shelf is not touched");
    const po = db.get("SELECT id FROM orders WHERE num=?", p1.r.body.order.num).id;
    await p1.C("/api/orders/" + po + "/cancel" + Q, "POST", {});
    ok((await buy({})).r.status === 200, "a cancelled promise can be promised again");
    db.run("UPDATE preorders SET ships_on=date('now','-1 day')"); db.run("UPDATE products SET stock=5 WHERE tenant_id=1 AND id=?", X); db.run("UPDATE skus SET stock=5 WHERE tenant_id=1 AND product_id=?", X);
    ok((await buy({})).r.status === 200 && db.get("SELECT stock s FROM products WHERE tenant_id=1 AND id=?", X).s === 4, "once the day comes it sells from the shelf");
  } catch (e) { failed++; console.error("  ✗ harness error:", e && e.stack || e); }
  console.log(`\n${passed} passed, ${failed} failed`); clean(); process.exit(failed ? 1 : 0);
})();
