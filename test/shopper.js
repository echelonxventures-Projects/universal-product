/* LUXORA Platform — the shopper and brand atoms, end to end: wish lists, price & stock alerts,
   pickup points & lockers, rich product content, the brand registry and sponsored results.
   Each is a capability atom a store switches on and tunes; each kind, visibility, module and
   status is a registry row. Runs a real server on its own throwaway database; nothing here
   touches the network. */
"use strict";
const path = require("path");
const fs = require("fs");
const DB = path.join(__dirname, "shopper.db");
process.env.LX_DB = DB;
const { spawn } = require("child_process");
const PORT = 8887;
const BASE = `http://localhost:${PORT}`;
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (fn, ms = 5000) => { for (let i = 0; i < ms / 50; i++) { const v = await fn(); if (v) return v; await sleep(50); } return null; };

const mk = () => {
  const c = new Map();
  const H = () => [...c].map(x => x[0] + "=" + x[1]).join("; ");
  return async (p, m, b) => {
    const o = { method: m || "GET", headers: Object.assign({ Cookie: H() }, m && m !== "GET" ? { "x-csrf": c.get("azc") || "", Origin: BASE, "Content-Type": "application/json" } : {}) };
    if (b !== undefined) o.body = JSON.stringify(b);
    const r = await fetch(BASE + p, o);
    (r.headers.getSetCookie ? r.headers.getSetCookie() : []).forEach(k => { const kv = k.split(";")[0], i = kv.indexOf("="); c.set(kv.slice(0, i).trim(), kv.slice(i + 1).trim()); });
    const text = await r.text();
    let body; try { body = JSON.parse(text); } catch (e) { body = { _raw: text }; }
    return { status: r.status, body };
  };
};
const alive = async () => { try { return (await fetch(BASE + "/healthz")).ok; } catch (e) { return false; } };
const Q = "?store=luxora";
const shopper = async (tag) => {
  const C = mk(); await C("/api/session" + Q);
  const r = await C("/api/auth/register" + Q, "POST", { name: "Shopper " + tag, email: "shopper-" + tag + "@example.com", password: "Correct-Horse-" + tag + "-9" });
  if (r.status !== 200) throw new Error("register " + tag + ": " + JSON.stringify(r.body));
  return C;
};

(async () => {
  for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
  const srv = spawn(process.execPath, [path.join(__dirname, "..", "server.js")], { env: { ...process.env, PORT, LX_DB: DB, LX_LOG: "", LX_OFFLINE: "1" }, stdio: ["ignore", "ignore", "pipe"] });
  let stderr = ""; srv.stderr.on("data", d => { stderr += d; });
  for (let i = 0; i < 120 && !(await alive()); i++) await sleep(500);
  if (!(await alive())) { console.error("server failed to boot\n" + stderr); process.exit(1); }
  const db = require(path.join(__dirname, "..", "lib", "db.js"));

  try {
    const A = mk(); await A("/api/session" + Q);
    ok((await A("/api/auth/login" + Q, "POST", { email: "admin@luxora.shop", password: "admin123" })).status === 200, "store admin signs in");
    const P = mk(); await P("/api/session");
    ok((await P("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" })).status === 200, "platform owner signs in");
    const enable = k => A("/api/capabilities/enable" + Q, "POST", { capability: k });
    const disable = k => A("/api/capabilities/disable" + Q, "POST", { capability: k });
    const tune = (k, param, value) => A("/api/capabilities/param" + Q, "POST", { capability: k, param, value });
    for (const k of ["wish_lists", "product_alerts", "pickup_points", "rich_content", "brand_registry", "sponsored_ads"]) await disable(k);

    /* a product with a registered brands row, in stock, and a second product */
    const prod = db.get("SELECT p.id, p.price, p.stock, b.key brand FROM products p JOIN brands b ON b.tenant_id=p.tenant_id AND (b.key=p.brand OR lower(b.label)=lower(p.brand)) WHERE p.tenant_id=1 AND p.lifecycle='published' AND p.deleted_at IS NULL AND p.stock > 5 AND p.price > 20 ORDER BY p.id LIMIT 1");
    const prod2 = db.get("SELECT id, price FROM products WHERE tenant_id=1 AND lifecycle='published' AND deleted_at IS NULL AND stock > 5 AND id<>? ORDER BY id LIMIT 1", prod.id);
    ok(!!prod && !!prod2, "fixture products found", { prod, prod2 });

    console.log("▸ EVERY FEATURE IS A CAPABILITY ATOM, OFF UNTIL SWITCHED ON");
    {
      const S0 = await shopper("off");
      ok((await S0("/api/lists" + Q)).status === 403, "lists answer 403 while wish_lists is off");
      ok((await S0("/api/alerts" + Q, "POST", { product_id: prod.id, kind: "price_drop" })).status === 403, "alerts answer 403 while product_alerts is off");
      ok((await S0("/api/pickup/points" + Q)).status === 403, "pickup points answer 403 while pickup_points is off");
      const sp = await S0("/api/marketplace/sponsored" + Q + "&surface=search&q=x");
      ok(sp.status === 200 && sp.body.items.length === 0, "no sponsored results while sponsored_ads is off", sp.body);
      const cfg = await S0("/api/config" + Q);
      ok(cfg.body.atoms && cfg.body.atoms.wish_lists === false && "pickup_points" in cfg.body.atoms, "the storefront config says which shopper atoms are on", cfg.body.atoms);
      for (const k of ["wish_lists", "product_alerts", "pickup_points", "rich_content", "brand_registry", "sponsored_ads"]) {
        const r = await enable(k); ok(r.status === 200, "store admin switches on " + k, r.body);
      }
      ok((await S0("/api/config" + Q)).body.atoms.wish_lists === true, "and the config follows");
      const caps = (await A("/api/capabilities" + Q)).body;
      const ev = (caps.presets || []).find(p => p.key === "blend_everything_store");
      ok(ev && ["wish_lists", "product_alerts", "pickup_points", "rich_content", "brand_registry", "sponsored_ads"].every(k => k in (ev.capabilities || {})), "the Everything-store blend carries all six", ev && Object.keys(ev.capabilities || {}));
    }

    console.log("▸ WISH LISTS");
    {
      ok((await mk()("/api/lists" + Q)).status === 401, "a signed-out visitor is asked to sign in");
      const S = await shopper("lists");
      const v = (await S("/api/lists" + Q)).body;
      ok(v.kinds.some(k => k.key === "wish_list" && k.gifting) && v.visibilities.some(x => x.key === "shared" && x.shared), "kinds, visibilities and priorities come from the registry", v);
      const l1 = await S("/api/lists" + Q, "POST", { name: "Birthday ideas" });
      ok(l1.status === 200 && l1.body.list.kind.key === "wish_list" && l1.body.list.visibility.key === "private", "a new list starts as the default kind and its kind's visibility", l1.body);
      const id1 = l1.body.list.id, token = l1.body.list.token;
      const add = await S(`/api/lists/${id1}/items${Q}`, "POST", { product_id: prod.id, qty: 2, priority: "high", note: "size M" });
      ok(add.status === 200 && add.body.list.items.length === 1 && add.body.list.items[0].product.id === prod.id && add.body.list.items[0].priority.key === "high", "an item is added with a quantity, a priority and a note", add.body);
      ok((await S(`/api/lists/${id1}/items${Q}`, "POST", { product_id: "NOPE" })).status === 404, "an unknown product is refused");
      const pp = await S(`/api/products/${encodeURIComponent(prod.id)}${Q}`);
      ok(pp.body.mine && pp.body.mine.lists.some(x => x.id === id1), "the product page knows which of my lists hold it", pp.body.mine);
      ok((await mk()(`/api/shared-lists/${token}${Q}`)).status === 404, "a private list cannot be opened by its link");
      ok((await S(`/api/lists/${id1}${Q}`, "PUT", { visibility: "shared" })).status === 200, "the owner shares it by link");
      const O = mk(); await O("/api/session" + Q);
      const sh = await O(`/api/shared-lists/${token}${Q}`);
      ok(sh.status === 200 && sh.body.list.items.length === 1 && !sh.body.list.token && sh.body.list.by === "Shopper lists", "anyone with the link sees it (without the link's secret)", sh.body);
      const itemId = sh.body.list.items[0].id;
      const bought = await O(`/api/shared-lists/${token}/purchased${Q}`, "POST", { item_id: itemId, qty: 1 });
      ok(bought.status === 200 && bought.body.list.items[0].purchased === 1, "a gift-giver marks one bought on a wish list", bought.body);
      const idea = await S("/api/lists" + Q, "POST", { name: "Living room", kind: "idea_list" });
      ok(idea.body.list.visibility.key === "public", "an idea list starts public, as its kind row says");
      await S(`/api/lists/${idea.body.list.id}/items${Q}`, "POST", { product_id: prod2.id });
      const ib = await O(`/api/shared-lists/${idea.body.list.token}/purchased${Q}`, "POST", { item_id: (await O(`/api/shared-lists/${idea.body.list.token}${Q}`)).body.list.items[0].id });
      ok(ib.status === 403, "purchases are not tracked on a kind of list that does not gift");
      const found = await O("/api/lists/find" + Q + "&q=living");
      ok(found.body.lists.some(l => l.id === idea.body.list.id) && !found.body.lists.some(l => l.id === id1), "public lists can be found; shared-by-link ones cannot", found.body);
      const mv = await S(`/api/list-items/${itemId}${Q}`, "PUT", { list_id: idea.body.list.id });
      ok(mv.status === 200 && mv.body.list.items.length === 2, "an item moves to another of my lists", mv.body);
      const Other = await shopper("other");
      ok((await Other(`/api/lists/${id1}${Q}`)).status === 404 && (await Other(`/api/list-items/${itemId}${Q}`, "DELETE")).status === 404, "another shopper cannot read or edit my lists");
      await tune("wish_lists", "allow_public", false);
      ok((await S("/api/lists" + Q, "POST", { name: "Public", visibility: "public" })).status === 403, "a store that turns public lists off refuses one");
      await tune("wish_lists", "max_lists", 2);
      ok((await S("/api/lists" + Q, "POST", { name: "Third" })).status === 400, "the list limit is the capability's param");
      await tune("wish_lists", "max_lists", 20); await tune("wish_lists", "allow_public", true);
      /* a new kind of list is one registry row */
      const nk = await P("/api/platform/registries/listKinds", "POST", { item: { key: "baby_list", name: "Baby list", default_visibility: "shared", gifting: true } });
      ok(nk.status === 200, "a platform admin adds a kind of list in the registry", nk.body);
      const bl = await S("/api/lists" + Q, "POST", { name: "For the baby", kind: "baby_list" });
      ok(bl.status === 200 && bl.body.list.kind.key === "baby_list" && bl.body.list.visibility.key === "shared", "and shoppers can keep one at once — no code", bl.body);
      ok((await S(`/api/lists/${id1}${Q}`, "DELETE")).status === 200 && (await S(`/api/lists/${id1}${Q}`)).status === 404, "the owner deletes a list");
    }

    console.log("▸ PRICE & STOCK ALERTS");
    {
      const S = await shopper("alerts");
      const kinds = (await S("/api/alerts" + Q + "&product=" + encodeURIComponent(prod.id))).body.kinds;
      ok(kinds.some(k => k.key === "back_in_stock" && !k.available) && kinds.some(k => k.key === "price_drop" && k.available), "an in-stock product offers price alerts but not back-in-stock", kinds);
      ok((await S("/api/alerts" + Q, "POST", { product_id: prod.id, kind: "back_in_stock" })).status === 400, "back-in-stock cannot be set on a product in stock");
      ok((await S("/api/alerts" + Q, "POST", { product_id: prod.id, kind: "price_target" })).status === 400, "a target alert needs a target");
      const w = await S("/api/alerts" + Q, "POST", { product_id: prod.id, kind: "price_drop" });
      ok(w.status === 200 && w.body.alert.watching, "a shopper watches a price", w.body);
      const notes = async () => (await S("/api/notifications" + Q)).body.notifications || [];
      await A(`/api/admin/products/${encodeURIComponent(prod.id)}${Q}`, "PUT", { price: +(prod.price * 0.98).toFixed(2) });
      await sleep(400);
      ok(!(await notes()).some(n => n.kind === "price_drop"), "a 2% drop is below the store's 5% threshold — no alert");
      await A(`/api/admin/products/${encodeURIComponent(prod.id)}${Q}`, "PUT", { price: +(prod.price * 0.8).toFixed(2) });
      const n1 = await until(async () => (await notes()).find(n => n.kind === "price_drop"));
      ok(!!n1 && /Price drop/.test(n1.title) && n1.link.includes(prod.id), "a 20% drop alerts the shopper in-app, with a link to the product", n1);
      const after = (await S("/api/alerts" + Q)).body.alerts.find(a => a.id === w.body.alert.id);
      ok(after.watching && after.fires === 1 && Math.abs(after.baseline_price - prod.price * 0.8) < 0.02, "it keeps watching from the new price (rearm)", after);
      const t = await S("/api/alerts" + Q, "POST", { product_id: prod.id, kind: "price_target", target_price: +(prod.price * 0.6).toFixed(2) });
      ok(t.status === 200, "a target-price alert is set");
      await A(`/api/admin/products/${encodeURIComponent(prod.id)}${Q}`, "PUT", { price: +(prod.price * 0.55).toFixed(2) });
      ok(!!(await until(async () => (await notes()).find(n => /target price/.test(n.title)))), "reaching the target alerts");
      /* back in stock */
      await A(`/api/admin/products/${encodeURIComponent(prod2.id)}${Q}`, "PUT", { stock: 0 });
      const b = await S("/api/alerts" + Q, "POST", { product_id: prod2.id, kind: "back_in_stock" });
      ok(b.status === 200, "back-in-stock is set on a sold-out product", b.body);
      await A(`/api/admin/products/${encodeURIComponent(prod2.id)}${Q}`, "PUT", { stock: 12 });
      ok(!!(await until(async () => (await notes()).find(n => n.kind === "back_in_stock"))), "restocking alerts");
      const c = await S(`/api/alerts/${b.body.alert.id}${Q}`, "DELETE");
      ok(c.status === 200 && !c.body.alert.watching, "a shopper cancels an alert", c.body);
      const Other = await shopper("alerts2");
      ok((await Other(`/api/alerts/${w.body.alert.id}${Q}`, "DELETE")).status === 404, "nobody else can cancel it");
      /* a new kind is a row naming an existing trigger */
      await P("/api/platform/registries/alertKinds", "POST", { item: { key: "deep_cut", name: "Deep cut", trigger: "price_at_or_below_target", watchable: "any", needs_target: true, notification_kind: "deal_alert", title: "Deep cut on {title}", body: "{price}" } });
      const dk = await S("/api/alerts" + Q, "POST", { product_id: prod.id, kind: "deep_cut", target_price: 1 });
      ok(dk.status === 200, "a new kind of alert is a registry row naming a trigger", dk.body);
      await P("/api/platform/registries/alertKinds", "POST", { item: { key: "mystery", name: "Mystery", trigger: "no_such_trigger" } });
      ok((await S("/api/alerts" + Q, "POST", { product_id: prod.id, kind: "mystery" })).status === 400, "a row naming a trigger the engine does not have is refused, never guessed");
      await A(`/api/admin/products/${encodeURIComponent(prod.id)}${Q}`, "PUT", { price: prod.price });
    }

    console.log("▸ PICKUP POINTS & LOCKERS");
    {
      await tune("pickup_points", "fee", 1.5);
      const bad = await A("/api/admin/pickup/points" + Q, "POST", { code: "Bad Code", name: "x", address: "y" });
      ok(bad.status === 400, "a point needs a clean code");
      const pt = await A("/api/admin/pickup/points" + Q, "POST", { code: "locker-1", name: "Station Locker", kind: "locker", address: "1 Station Rd", city: "Springfield", postcode: "12345", capacity: 1, hours: "24/7", eta_days: 2 });
      ok(pt.status === 200 && pt.body.point.kind_row.key === "locker", "staff add a locker", pt.body);
      const pointId = pt.body.point.id;
      const S = await shopper("pickup");
      const list = await S("/api/pickup/points" + Q + "&q=12345");
      ok(list.status === 200 && list.body.points[0].id === pointId && list.body.fee > 0, "shoppers see the point and its fee", list.body);
      await S("/api/cart" + Q, "POST", { id: prod2.id, qty: 1 });
      const q = await S("/api/checkout/quote" + Q, "POST", { pickup_point: pointId });
      ok(q.status === 200 && q.body.source === "pickup" && q.body.pickup.id === pointId && q.body.eta === 2, "the quote prices the point's fee and its arrival, not a carrier", q.body);
      const co = await S("/api/checkout" + Q, "POST", { name: "Pia Pickup", gateway: "cod", pickup_point: pointId });
      ok(co.status === 200 && co.body.order.pickup && /^\d{6}$/.test(co.body.order.pickup.code), "checkout needs no address and returns a 6-digit pickup code", co.body);
      const code = co.body.order.pickup.code;
      const S2 = await shopper("pickup2");
      await S2("/api/cart" + Q, "POST", { id: prod2.id, qty: 1 });
      ok((await S2("/api/checkout/quote" + Q, "POST", { pickup_point: pointId })).status === 409, "a full point is refused");
      const adm = (await A("/api/admin/pickup" + Q)).body;
      const res1 = adm.reservations.find(r => r.point_id === pointId);
      ok(res1 && !("code" in res1) && res1.order_num === co.body.order.num, "staff see the reservation, never the code", res1);
      ok((await A(`/api/admin/pickup/reservations/${res1.id}${Q}`, "POST", { action: "collect", code })).status === 409, "a parcel not yet arrived cannot be collected");
      const ar = await A(`/api/admin/pickup/reservations/${res1.id}${Q}`, "POST", { action: "arrive" });
      ok(ar.status === 200 && ar.body.reservation.hold_until, "staff mark it arrived; it is held until a date", ar.body);
      const ready = await until(async () => ((await S("/api/notifications" + Q)).body.notifications || []).find(n => n.kind === "pickup_ready"));
      ok(!!ready && ready.body.includes(code), "the shopper is told it is ready, with the code", ready);
      const mine = (await S("/api/orders" + Q)).body.orders.find(o => o.num === co.body.order.num);
      ok(mine.pickup && mine.pickup.code === code && mine.pickup.point.name === "Station Locker", "the order page shows the point and the code");
      ok((await A(`/api/admin/pickup/reservations/${res1.id}${Q}`, "POST", { action: "collect", code: "000000" === code ? "111111" : "000000" })).status === 403, "a wrong code is refused");
      const col = await A(`/api/admin/pickup/reservations/${res1.id}${Q}`, "POST", { action: "collect", code });
      ok(col.status === 200 && col.body.reservation.collected_at, "the right code collects it", col.body);
      const after = (await S("/api/orders" + Q)).body.orders.find(o => o.num === co.body.order.num);
      ok(after.pickup.code === null, "the code is no longer shown once collected");
      /* expiry: a parcel left past its holding time */
      await A("/api/admin/pickup/points" + Q, "POST", { id: pointId, code: "locker-1", name: "Station Locker", kind: "locker", address: "1 Station Rd", capacity: 5 });
      const co2 = await S2("/api/checkout" + Q, "POST", { name: "Late Lou", gateway: "cod", pickup_point: "locker-1" });
      ok(co2.status === 200, "a point can be chosen by its code too", co2.body);
      const r2 = db.get("SELECT id FROM pickup_reservations WHERE order_id=(SELECT id FROM orders WHERE num=?)", co2.body.order.num);
      await A(`/api/admin/pickup/reservations/${r2.id}${Q}`, "POST", { action: "arrive" });
      db.run("UPDATE pickup_reservations SET hold_until='2000-01-01 00:00:00' WHERE id=?", r2.id);
      const sw = await A("/api/admin/pickup/sweep" + Q, "POST", {});
      ok(sw.body.expired === 1, "the sweep expires a parcel past its holding time", sw.body);
      const ret = await A(`/api/admin/pickup/reservations/${r2.id}${Q}`, "POST", { action: "return" });
      ok(ret.status === 200, "an expired parcel is returned");
      /* a cancelled order frees its place */
      await A("/api/admin/pickup/points" + Q, "POST", { code: "kiosk", name: "Kiosk", address: "2 Market St", capacity: 1 });
      const S3 = await shopper("pickup3");
      await S3("/api/cart" + Q, "POST", { id: prod2.id, qty: 1 });
      const k1 = await S3("/api/checkout" + Q, "POST", { name: "Kim Kiosk", gateway: "cod", pickup_point: "kiosk" });
      await S2("/api/cart" + Q, "POST", { id: prod2.id, qty: 1 });
      ok(k1.status === 200 && (await S2("/api/checkout/quote" + Q, "POST", { pickup_point: "kiosk" })).status === 409, "the one-place kiosk is full");
      const kid = db.get("SELECT id FROM orders WHERE num=?", k1.body.order.num).id;
      const cx = await S3(`/api/orders/${kid}/cancel${Q}`, "POST", {});
      ok(cx.status === 200 && (await S2("/api/checkout/quote" + Q, "POST", { pickup_point: "kiosk" })).status === 200, "cancelling the order frees its place", cx.body);
      const rm = await A(`/api/admin/pickup/points/${pointId}${Q}`, "DELETE");
      ok(rm.status === 200 && rm.body.deactivated, "a point with history is switched off, not deleted", rm.body);
    }

    console.log("▸ BRAND REGISTRY");
    let ownerSeller, claimId;
    {
      const sid = n => Number(db.run("INSERT INTO sellers(tenant_id,name) VALUES(1,?)", n).lastInsertRowid);
      ownerSeller = sid("Brand Owner Ltd"); const rogue = sid("Rogue Reseller");
      ok((await A("/api/admin/brand-registry/claims" + Q, "POST", { brand: prod.brand, seller_id: ownerSeller })).status === 400, "a claim needs a trademark number");
      ok((await A("/api/admin/brand-registry/claims" + Q, "POST", { brand: "no-such-brand", seller_id: ownerSeller, trademark_number: "1" })).status === 404, "an unknown brand is refused");
      const c = await A("/api/admin/brand-registry/claims" + Q, "POST", { brand: prod.brand, seller_id: ownerSeller, trademark_number: "TM-778899", trademark_office: "National IP Office", evidence: "registration certificate.pdf" });
      ok(c.status === 200 && c.body.claim.state.key === "submitted", "an owner's claim waits for review", c.body);
      claimId = c.body.claim.id;
      ok((await A("/api/admin/brand-registry/claims" + Q, "POST", { brand: prod.brand, seller_id: ownerSeller, trademark_number: "TM-778899" })).status === 409, "the same claim cannot wait twice");
      const offer = Number(db.run("INSERT INTO seller_offers(tenant_id,product_id,seller_id,price,offer_status) VALUES(1,?,?,?,'active')", prod.id, rogue, prod.price * 0.5).lastInsertRowid);
      ok((await A("/api/admin/brand-registry/reports" + Q, "POST", { claim_id: claimId, kind: "counterfeit", offer_id: offer })).status === 403, "an unapproved claimant cannot report");
      const ap = await A(`/api/admin/brand-registry/claims/${claimId}${Q}`, "POST", { action: "approve", notes: "certificate checked" });
      ok(ap.status === 200 && ap.body.claim.status === "approved", "staff approve the claim", ap.body);
      const c2 = await A("/api/admin/brand-registry/claims" + Q, "POST", { brand: prod.brand, seller_id: rogue, trademark_number: "FAKE" });
      ok(c2.status === 409, "a brand has one approved owner", c2.body);
      const pp = await mk()(`/api/products/${encodeURIComponent(prod.id)}${Q}`);
      ok(pp.body.brand_registry && pp.body.brand_registry.brand === prod.brand, "the product page shows a registered-brand badge", pp.body.brand_registry);
      const rp = await A("/api/admin/brand-registry/reports" + Q, "POST", { claim_id: claimId, kind: "counterfeit", offer_id: offer, details: "half price, wrong logo" });
      ok(rp.status === 200 && rp.body.report.seller_id === rogue, "the owner reports a counterfeit offer", rp.body);
      await tune("brand_registry", "offer_state_on_infringement", "no_such_state");
      ok((await A(`/api/admin/brand-registry/reports/${rp.body.report.id}${Q}`, "POST", { action: "uphold" })).status === 409, "an offer state the seller-offer machine lacks is refused, not written");
      await tune("brand_registry", "offer_state_on_infringement", "suspended");
      const up = await A(`/api/admin/brand-registry/reports/${rp.body.report.id}${Q}`, "POST", { action: "uphold", outcome: "test buy confirmed" });
      ok(up.status === 200 && up.body.report.offers_affected === 1 && db.get("SELECT offer_status FROM seller_offers WHERE id=?", offer).offer_status === "suspended", "upholding suspends the offending offer", up.body);
      ok((await A(`/api/admin/brand-registry/reports/${rp.body.report.id}${Q}`, "POST", { action: "dismiss" })).status === 409, "a decided report cannot be decided again");
    }

    console.log("▸ RICH PRODUCT CONTENT");
    {
      const mods = [{ kind: "banner", image: "https://cdn.example.com/hero.jpg", headline: "Made to last" }, { kind: "feature_list", headline: "Why it's different", items: "Hand finished\nTen-year warranty" }];
      ok((await A("/api/admin/rich-content" + Q, "POST", { product_id: prod.id, modules: mods })).status === 400, "an image on a host the platform does not allow is refused (the browser would block it)");
      ok((await P("/api/platform/config", "PUT", { cspImgHosts: ["not a host"] })).status === 400, "the platform's image hosts must be hostnames");
      ok((await P("/api/platform/config", "PUT", { cspImgHosts: ["cdn.example.com"] })).status === 200, "the platform allows a brand CDN");
      const csp = (await fetch(BASE + "/index.html" + Q)).headers.get("content-security-policy") || "";
      ok(/img-src 'self' data: https:\/\/cdn\.example\.com/.test(csp), "and the storefront's CSP lets images load from it", csp);
      const own = await A("/api/admin/rich-content" + Q, "POST", { product_id: prod.id, modules: [{ kind: "banner", image: "/media/hero.jpg" }] });
      ok(own.status === 200 && own.body.content.modules[0].image === "/media/hero.jpg", "the store's own image paths are accepted", own.body);
      ok((await A("/api/admin/rich-content" + Q, "POST", { product_id: prod.id, modules: [{ kind: "banner", image: "//evil.example/x.jpg" }] })).status === 400, "a protocol-relative address is not mistaken for the store's own");
      ok((await A("/api/admin/rich-content" + Q, "POST", { product_id: prod.id, modules: [{ kind: "banner", image: "http://insecure.example.com/x.jpg" }] })).status === 400, "an image must be served over https");
      ok((await A("/api/admin/rich-content" + Q, "POST", { product_id: prod.id, modules: [{ kind: "carousel_3d" }] })).status === 400, "an unknown module kind is refused");
      ok((await A("/api/admin/rich-content" + Q, "POST", { product_id: prod.id, modules: [{ kind: "image_text", image: "https://cdn.example.com/a.jpg" }] })).status === 400, "a required field is required");
      const d = await A("/api/admin/rich-content" + Q, "POST", { product_id: prod.id, modules: mods, seller_id: ownerSeller });
      ok(d.status === 200 && d.body.content.editable && d.body.content.modules[1].items.length === 2, "a draft is saved; lines become list entries", d.body);
      ok(!(await mk()(`/api/products/${encodeURIComponent(prod.id)}${Q}`)).body.rich_content, "a draft is not shown to shoppers");
      const sub = await A(`/api/admin/rich-content/${d.body.content.id}${Q}`, "POST", { action: "submit" });
      ok(sub.status === 200 && sub.body.content.status === "submitted", "submitting sends it for review", sub.body);
      const ap = await A(`/api/admin/rich-content/${d.body.content.id}${Q}`, "POST", { action: "approve" });
      ok(ap.status === 200 && ap.body.content.status === "approved", "staff approve it");
      const live = (await mk()(`/api/products/${encodeURIComponent(prod.id)}${Q}`)).body.rich_content;
      ok(live && live.modules.length === 2 && live.modules[0].image === "https://cdn.example.com/hero.jpg" && live.kinds.some(k => k.key === "banner"), "the product page shows it, with the module rows to render it", live);
      const d2 = await A("/api/admin/rich-content" + Q, "POST", { product_id: prod.id, modules: [{ kind: "faq", rows: "Is it waterproof? | Yes, to 50 m" }], seller_id: ownerSeller });
      ok(d2.body.content.version === 2 && d2.body.content.id !== d.body.content.id, "editing live content starts version 2");
      await tune("rich_content", "require_approval", false);
      const v2 = await A(`/api/admin/rich-content/${d2.body.content.id}${Q}`, "POST", { action: "submit" });
      ok(v2.body.content.status === "approved", "with review turned off, submitting publishes at once", v2.body);
      ok(db.get("SELECT status FROM rich_content WHERE id=?", d.body.content.id).status === "retired", "the version it replaces is retired");
      await tune("rich_content", "brand_owner_only", true);
      ok((await A("/api/admin/rich-content" + Q, "POST", { product_id: prod.id, modules: mods })).status === 403, "with owner-only on, content without the brand's owner is refused");
      ok((await A("/api/admin/rich-content" + Q, "POST", { product_id: prod.id, modules: mods, seller_id: ownerSeller })).status === 200, "the registered owner may publish");
      await tune("rich_content", "max_modules", 1);
      ok((await A("/api/admin/rich-content" + Q, "POST", { product_id: prod.id, modules: mods, seller_id: ownerSeller })).status === 400, "the module limit is the capability's param");
      await tune("rich_content", "max_modules", 7);
      /* a new module is a registry row of typed fields */
      await P("/api/platform/registries/contentModules", "POST", { item: { key: "size_guide", name: "Size guide", fields: [{ key: "rows", label: "Sizes", type: "table", max_cols: 4, required: true }] } });
      const sg = await A("/api/admin/rich-content" + Q, "POST", { product_id: prod.id, modules: [{ kind: "size_guide", rows: [["S", "36"], ["M", "38"]] }], seller_id: ownerSeller });
      ok(sg.status === 200 && sg.body.content.modules[0].rows.length === 2, "a new module kind is a registry row", sg.body);
      await P("/api/platform/registries/contentModules", "POST", { item: { key: "hologram", name: "Hologram", fields: [{ key: "x", label: "X", type: "hologram" }] } });
      ok((await A("/api/admin/rich-content" + Q, "POST", { product_id: prod.id, modules: [{ kind: "hologram", x: "1" }], seller_id: ownerSeller })).status === 400, "a field type the engine cannot show is refused");
    }

    console.log("▸ SPONSORED PRODUCTS");
    {
      const ad = await A("/api/admin/marketplace/ads" + Q, "POST", { name: "Spring push", bid_model: "cpc", bid_amount: 1.5, budget: 10, target: { surface: "search", keywords: ["blanket"], product_id: prod.id } });
      ok(ad.status === 200, "staff create a keyword-targeted ad for a product", ad.body);
      const adId = ad.body.ad.id;
      const S = await shopper("ads");
      const hit = await S("/api/marketplace/sponsored" + Q + "&surface=search&q=wool%20blanket");
      ok(hit.body.items.length === 1 && hit.body.items[0].product.id === prod.id && hit.body.label === "Sponsored", "a search naming its keyword shows it, labelled", hit.body);
      ok((await S("/api/marketplace/sponsored" + Q + "&surface=search&q=sofa")).body.items.length === 0, "a search that does not, does not");
      await S("/api/marketplace/sponsored" + Q + "&surface=search&q=blanket");
      ok(db.get("SELECT COUNT(*) c FROM ad_events WHERE ad_id=? AND kind='impression'", adId).c === 1, "serving records one impression per viewer per day");
      const click = await S(`/api/marketplace/ads/${adId}/event${Q}`, "POST", { kind: "click" });
      ok(click.status === 200 && db.get("SELECT spent FROM ads WHERE id=?", adId).spent === 1.5, "a click charges the bid", click.body);
      db.run("UPDATE ads SET spent=10 WHERE id=?", adId);
      ok((await S("/api/marketplace/sponsored" + Q + "&surface=search&q=blanket")).body.items.length === 0, "an ad that spent its budget stops serving");
      db.run("UPDATE ads SET spent=0, end_at='2000-01-01 00:00:00' WHERE id=?", adId);
      ok((await S("/api/marketplace/sponsored" + Q + "&surface=search&q=blanket")).body.items.length === 0, "an ad past its end stops serving");
      db.run("UPDATE ads SET end_at=NULL WHERE id=?", adId);
      await tune("sponsored_ads", "reserve_price", 2);
      ok((await S("/api/marketplace/sponsored" + Q + "&surface=search&q=blanket")).body.items.length === 0, "a bid under the reserve price does not serve");
      await tune("sponsored_ads", "reserve_price", 0);
      ok((await S("/api/marketplace/sponsored" + Q + "&surface=search&q=blanket")).body.items.length === 1, "and serves again once it clears it");
      await tune("sponsored_ads", "label", "Ad");
      ok((await S("/api/marketplace/sponsored" + Q + "&surface=search&q=blanket")).body.label === "Ad", "the label is the store's to word");
    }
  } catch (e) { failed++; console.log("  ✗ threw: " + (e && e.stack || e)); }
  srv.kill();
  console.log(`\n${passed} passed, ${failed} failed`);
  for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
  process.exit(failed ? 1 : 0);
})();
