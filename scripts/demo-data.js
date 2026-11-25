/* LUXORA Platform — what the demo's stores start with: their stand-in connections, every capability
   switched on in the LUXORA store, staff and shoppers, and an example of each shopper feature. Adds
   what is missing and changes nothing that is there, so a demo keeps what is done in it. */
"use strict";
async function prepare({ db, sec, creds, smtpPort }) {
  const { get, all, run } = db, id = slug => get("SELECT id FROM tenants WHERE slug=?", slug).id;
  const L = id("luxora"), A = id("aurum"), V = id("velora"), problems = [];
  const attempt = (what, fn) => { try { return fn(); } catch (e) { problems.push(what + ": " + e.message); return null; } };
  const done = key => { const k = "demo." + key; if (get("SELECT 1 x FROM platform_settings WHERE key=?", k)) return true; require("../lib/settings.js").initPlatform(k, 1); return false; };
  /* connections: live, with the stand-ins' credentials */
  const secrets = (pid, kind) => { const d = require("../lib/registry.js").providerDefs(kind).find(p => p.id === pid) || { fields: [] }; return d.fields.filter(f => f.secret).map(f => f.key); };
  const link = (t, pid, kind, cfg, pos) => { const g = kind === "notification" ? "notify:" + pid : pid; run("INSERT INTO tenant_gateways(tenant_id,provider_id,enabled,is_primary,mode,config,position) VALUES(?,?,1,?,'live',?,?) ON CONFLICT(tenant_id,provider_id) DO UPDATE SET enabled=1, mode='live', config=excluded.config", t, g, pos === 0 ? 1 : 0, sec.sealConfig(t, g, cfg, secrets(pid, kind)), pos); };
  if (!done("connections")) {
    link(L, "stripe", "payment", creds.stripe, 0); link(L, "paypal", "payment", { ...creds.paypal, env: "" }, 1); link(A, "razorpay", "payment", creds.razorpay, 0); link(V, "stripe", "payment", creds.stripe, 0);
    link(L, "smtp", "notification", { host: "127.0.0.1", port: String(smtpPort), user: "demo", pass: "demo", from: "LUXORA Demo <demo@luxora.shop>" }, 5); link(L, "twilio", "notification", creds.twilio, 6);
    run("UPDATE tenant_gateways SET enabled=0 WHERE mode='sandbox' AND provider_id NOT LIKE 'ship:%' AND provider_id NOT LIKE 'notify:%'");
    attempt("carrier", () => { require("../lib/shipping.js").updateProviderConfig("easypost", creds.easypost); });
  }
  /* people */
  const person = async (t, name, email, pw, role, staff) => { if (get("SELECT 1 x FROM users WHERE tenant_id=? AND email=?", t, email)) return; const u = await db.newUserAsync(t, name, email, pw, role); run("UPDATE users SET email_verified_at=datetime('now')" + (staff ? ", staff_role='" + staff + "'" : "") + " WHERE id=?", u); };
  await person(L, "Olive Orders", "orders@luxora.shop", "Demo-Staff-1", "admin", "orders");
  await person(L, "Sam Support", "support@luxora.shop", "Demo-Staff-1", "admin", "support");
  await person(L, "Demo Shopper", "shopper@luxora.shop", "Demo-Shop-1", "customer");
  await person(A, "Demo Shopper", "shopper@aurum.shop", "Demo-Shop-1", "customer");
  if (!done("settings")) {
    const save = require("../lib/settings.js").save, legal = (n, a, st, tax, c) => ({ businessName: n, address: a, state: st, taxId: tax, supportEmail: "care@luxora.shop", phone: "+1 555 0100", privacyEmail: "privacy@luxora.shop", officer: "Demo Officer", paymentProvider: "a demo payment provider", carriers: "demo carriers", messaging: "a demo email service", hosting: "this computer", deliveryAreas: "Anywhere, in the demo", refundDays: "7", retention: "Until the demo is reset.", legalBasis: "Demo only.", answerDays: "30", governingLaw: c, updatedOn: "25 November 2026" });
    save(L, { legal: legal("LUXORA Demo Inc.", "1 Demo Street, Seattle, WA 98109", "WA", "", "Washington, USA"), features: { fraudScreen: false } });
    save(A, { legal: legal("Aurum Demo Pvt Ltd", "1 MG Road, Bengaluru 560001", "Karnataka", "29ABCDE1234F1Z5", "Karnataka, India"), features: { fraudScreen: false } });
    save(V, { legal: legal("Velora Demo LLC", "1 Demo Marina, Dubai", "Dubai", "", "Dubai, UAE"), features: { fraudScreen: false } });
    run("UPDATE subscriptions SET plan_id=(SELECT id FROM plans ORDER BY max_orders_month DESC LIMIT 1)");
  }
  /* every capability on in LUXORA, with its own defaults; the two that can stop a checkout stay easy */
  if (!done("capabilities")) {
    const caps = require("../lib/capabilities.js"), SEED = require("../lib/seed/capabilities.json").CATALOG;
    for (const c of SEED) run("INSERT INTO capability_values(tenant_id,capability,enabled,params) VALUES(?,?,1,'{}') ON CONFLICT(tenant_id,capability) DO UPDATE SET enabled=1", L, c.key);
    for (const k of ["delivery_slots", "serviceable_areas", "size_guides", "preorders", "wish_lists", "product_alerts", "pickup_points"]) run("INSERT INTO capability_values(tenant_id,capability,enabled,params) VALUES(?,?,1,'{}') ON CONFLICT(tenant_id,capability) DO UPDATE SET enabled=1", A, k);
    if (caps.bust) { caps.bust(L); caps.bust(A); }
  }
  if (!done("examples")) {
    const phys = all("SELECT id, title, price FROM products WHERE tenant_id=? AND type='physical' AND lifecycle='published' AND deleted_at IS NULL AND stock>20 AND price BETWEEN 15 AND 400 ORDER BY id LIMIT 12", L), day = n => new Date(Date.now() + n * 864e5).toISOString();
    const inDays = n => day(n).slice(0, 10);
    attempt("delivery windows", () => { const W = require("../lib/delivery-windows.js"); for (let d = 0; d < 7; d++) { W.save(L, { weekday: d, starts: "09:00", ends: "12:00", capacity: 10, fee: 0 }); W.save(L, { weekday: d, starts: "17:00", ends: "20:00", capacity: 5, fee: 3 }); } });
    attempt("size guide", () => require("../lib/size-guides.js").save(L, { name: "Clothing sizes", scope: "dept", target: "fashion", rows: "Size, Chest (cm), Waist (cm)\nS, 88-92, 72-76\nM, 94-98, 78-82\nL, 100-104, 84-88", note: "Between sizes? Choose the larger." }));
    attempt("pre-order", () => require("../lib/preorders.js").save(L, { product_id: phys[0].id, ships_on: inDays(30), max_qty: 25 }));
    attempt("pickup point", () => require("../lib/pickup.js").savePoint(L, { code: "demo-locker", name: "Pike Place locker", address: "85 Pike St", city: "Seattle", postcode: "98101", capacity: 20, hours: "Open all day" }));
    attempt("auction", () => require("../lib/auctions.js").create(L, { owner: "", staff: true }, { product_id: phys[1].id, title: phys[1].title, start_price: Math.round(phys[1].price / 2), ends_at: day(3) }));
    attempt("group buy", () => require("../lib/groupbuy.js").create(L, { product_id: phys[2].id, group_price: +(phys[2].price * 0.7).toFixed(2), min_members: 2, ends_at: day(5) }));
    attempt("fee", () => require("../lib/fees.js").saveRule(L, { code: "small-order", name: "Small order fee", amount: 2, below_amount: 20, active: true }));
  }
  if (problems.length) console.error("demo: " + problems.join(" · "));
  return problems;
}
module.exports = { prepare };
