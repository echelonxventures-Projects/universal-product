/* LUXORA Platform — a new store is provisioned from configuration, never from literals.
   What a store starts with when its registration leaves a choice open — the deploy mode,
   how many of its country's gateways and carriers, the cash and house-shipping providers,
   the delivery promise — is platform policy. The catalogue content an archetype opens a
   store with is data on the archetype's row, so an operator's own archetype (say, one
   saved from a store tuned to look like a big marketplace) carries content too. Owner
   passwords meet the platform's credential policy, like every other password. */
"use strict";
const path = require("path");
const fs = require("fs");
const DB = path.join(__dirname, "provisioning.db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
const PORT = 8883;
Object.assign(process.env, { LX_DB: DB, PORT: String(PORT), LX_LOG: "" });
delete process.env.NODE_ENV;
const BASE = `http://localhost:${PORT}`;
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const mk = () => {
  const c = new Map();
  return async (p, m, b) => {
    const o = { method: m || "GET", headers: Object.assign({ Cookie: [...c].map(x => x[0] + "=" + x[1]).join("; ") }, m && m !== "GET" ? { "x-csrf": c.get("azc") || "", Origin: BASE, "Content-Type": "application/json" } : {}) };
    if (b !== undefined) o.body = JSON.stringify(b);
    const r = await fetch(BASE + p, o);
    (r.headers.getSetCookie ? r.headers.getSetCookie() : []).forEach(k => { const kv = k.split(";")[0], i = kv.indexOf("="); c.set(kv.slice(0, i).trim(), kv.slice(i + 1).trim()); });
    let body; try { body = await r.json(); } catch (e) { body = {}; }
    return { status: r.status, body };
  };
};

(async () => {
  const silence = console.log; console.log = () => { };
  require("../server.js");
  const db = require("../lib/db.js");
  console.log = silence;
  for (let i = 0; i < 120; i++) { try { if ((await fetch(BASE + "/healthz")).ok) break; } catch (e) { } await sleep(250); }
  const gw = tid => db.all("SELECT provider_id FROM tenant_gateways WHERE tenant_id=? ORDER BY provider_id", tid).map(r => r.provider_id);
  const owner = n => ({ ownerName: "Owner " + n, ownerEmail: "owner@" + n + ".test", ownerPassword: "Str0ng-" + n + "-pass" });

  try {
    const P = mk(); await P("/api/session");
    ok((await P("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" })).status === 200, "platform owner signs in");

    console.log("▸ NEW-STORE DEFAULTS ARE POLICY");
    const cfg = (await P("/api/platform/config")).body;
    const pv = cfg.policy.provisioning;
    ok(pv.defaultMode === "marketplace" && pv.paymentGatewaysPerStore === 2 && pv.cashGateway === "cod" && pv.houseShipping === "house-std" && pv.carriersPerStore === 2,
      "the shipped defaults are visible as policy values", pv);
    const meta = (await P("/api/meta")).body;
    const ind = (meta.deployModes || []).find(m => m.key === "industry");
    ok(ind && ind.needsIndustries === true && meta.deployModes.find(m => m.key === "marketplace").needsIndustries === false,
      "whether a mode needs industries is served from the mode registry", meta.deployModes);

    const a = await P("/api/platform/tenants", "POST", { name: "Default Store", slug: "dflt", country: "US", ...owner("dflt") });
    ok(a.status === 200, "a store registers with nothing chosen", a.body.error);
    const ga = gw(a.body.tenant.id);
    ok(a.body.tenant.mode === "marketplace", "it takes the policy's default mode", a.body.tenant.mode);
    ok(ga.includes("cod") && ga.includes("ship:house-std"), "it gets the policy's cash gateway and house shipping", ga);

    const put = await P("/api/platform/config", "PUT", { provisioning: { defaultMode: "brand", paymentGatewaysPerStore: 1, cashGateway: "", houseShipping: "", carriersPerStore: 0, shipDaysPriority: 1, shipDaysStandard: 3 } });
    ok(put.status === 200, "the platform changes the new-store defaults", put.body.error);
    const b = await P("/api/platform/tenants", "POST", { name: "Policy Store", slug: "polst", country: "US", industries: ["electronics"], shipping: { freeShipThreshold: 50 }, ...owner("polst") });
    ok(b.status === 200, "the next store registers", b.body.error);
    const gb = gw(b.body.tenant.id);
    const pays = gb.filter(x => !/^(ship|notify):/.test(x)), ships = gb.filter(x => x.startsWith("ship:"));
    ok(b.body.tenant.mode === "brand", "it takes the new default mode", b.body.tenant.mode);
    ok(pays.length === 1 && !pays.includes("cod"), "one country gateway and no cash gateway", pays);
    ok(ships.length === 0, "no house shipping and no carriers", ships);
    const comm = require("../lib/settings.js").load(b.body.tenant.id).commerce;
    ok(comm.daysPriority === 1 && comm.daysStandard === 3, "the delivery promise comes from policy", { p: comm.daysPriority, s: comm.daysStandard });
    const c = await P("/api/platform/tenants", "POST", { name: "Unscoped", slug: "unscoped", country: "US", mode: "brand", ...owner("unscoped") });
    ok(c.status === 400 && /industr/i.test(c.body.error || ""), "a mode that needs industries still refuses a store without them", c.body);
    await P("/api/platform/config", "PUT", { provisioning: { defaultMode: "marketplace", paymentGatewaysPerStore: 2, cashGateway: "cod", houseShipping: "house-std", carriersPerStore: 2, shipDaysPriority: 2, shipDaysStandard: 5 } });

    console.log("▸ THE DEFAULT COUNTRY IS POLICY, AND A STORE KEEPS ITS OWN");
    ok(pv.defaultCountry === "US", "the shipped default country is a policy value", pv.defaultCountry);
    ok((await P("/api/platform/config", "PUT", { provisioning: { defaultCountry: "ZZ" } })).status === 400, "an unknown default country is refused");
    ok((await P("/api/platform/config", "PUT", { provisioning: { defaultCountry: "gb" } })).status === 200, "the platform changes the default country");
    const gbs = await P("/api/platform/tenants", "POST", { name: "No Country", slug: "nocountry", ...owner("nocountry") });
    ok(gbs.status === 200 && db.get("SELECT country FROM tenants WHERE id=?", gbs.body.tenant.id).country === "GB", "a store registered without a country gets the policy's", gbs.body.error);
    const settingsMod = require("../lib/settings.js");
    settingsMod.reset(gbs.body.tenant.id);
    ok(settingsMod.load(gbs.body.tenant.id).commerce.country === "GB", "resetting a store's settings keeps the store in its own country");
    await P("/api/platform/config", "PUT", { provisioning: { defaultCountry: "US" } });
    ok((await P("/api/platform/config", "PUT", { paymentReconcileMinutes: -1 })).status === 400 && (await P("/api/platform/config", "PUT", { paymentReconcileMinutes: 5 })).body.policy.paymentReconcileMinutes === 5, "how often pending gateway payments are checked is a validated policy value");

    console.log("▸ OWNER PASSWORDS MEET THE PLATFORM POLICY");
    const weak = await P("/api/platform/tenants", "POST", { name: "Weak", slug: "weak", country: "US", ownerName: "Owner Weak", ownerEmail: "o@weak.test", ownerPassword: "abcdef" });
    ok(weak.status === 400 && /Owner password/.test(weak.body.error || ""), "a password the policy refuses is refused for an owner too", weak.body);
    ok(!db.get("SELECT id FROM tenants WHERE slug='weak'"), "and no half-made store is left behind");

    console.log("▸ AN ARCHETYPE CARRIES ITS CATALOGUE CONTENT AS DATA");
    const presets = (await P("/api/capabilities")).body.presets || [];
    const mkt = presets.find(p => p.key === "blend_marketplace");
    ok(mkt && Array.isArray(mkt.universes) && mkt.universes.includes("uv_marketplace"), "the marketplace archetype's content is on its row", mkt && mkt.universes);
    const save = await P("/api/capabilities/preset", "POST", { key: "blend_bigstore", label: "Big store", description: "marketplace + storefront extras",
      capabilities: { buy_box: { params: { price_weight: 0.7 } }, reviews: {}, qna: {}, deals: {}, membership: {}, subscribe_save: {} }, universes: ["uv_marketplace", "bad key!"] });
    ok(save.status === 200 && JSON.stringify(save.body.preset.universes) === '["uv_marketplace"]', "an operator's archetype saves with content, keeping only valid keys", save.body);
    const d = await P("/api/platform/tenants", "POST", { name: "Big Store", slug: "bigstore", country: "US", archetype: "blend_bigstore", ...owner("bigstore") });
    ok(d.status === 200, "a store registers from the operator's archetype", d.body.error);
    const vals = db.all("SELECT capability, params FROM capability_values WHERE tenant_id=? AND enabled=1", d.body.tenant.id);
    const bb = vals.find(v => v.capability === "buy_box");
    ok(["reviews", "qna", "deals", "membership", "subscribe_save", "buy_box"].every(k => vals.some(v => v.capability === k)), "every capability of the archetype is on", vals.map(v => v.capability));
    ok(bb && JSON.parse(bb.params).price_weight === 0.7, "with the archetype's tuning", bb && bb.params);
    ok((d.body.activated || []).some(x => x.key === "uv_marketplace"), "and the archetype's content is activated into it", d.body.activated);
    const every = presets.find(p => p.key === "blend_everything_store");
    ok(every && ["reviews", "qna", "deals", "coupons", "gift_cards", "registry", "subscribe_save", "membership", "buy_now", "buy_box", "fba_inbound"].every(k => k in every.capabilities) && every.universes.length > 0, "a full everything-store archetype ships as data", every && Object.keys(every.capabilities));
    const capView = (await P("/api/capabilities")).body;
    ok((capView.domains || []).some(x => x.key === "storefront" && x.name) && (capView.domains || []).length >= 7, "capability domains are titled from the registry", capView.domains);
    const resave = await P("/api/capabilities/preset", "POST", { key: "blend_bigstore", label: "Big store v2", capabilities: { reviews: {} } });
    ok(resave.status === 200 && JSON.stringify(resave.body.preset.universes) === '["uv_marketplace"]', "re-saving without naming content keeps the content", resave.body.preset);

    console.log("▸ CHECKOUT READS PROVIDERS FROM DATA, NOT BY NAME");
    const off = db.get("SELECT items FROM meta_lists WHERE name='offlinePaymentMethods'");
    ok(off && /bank_transfer/.test(off.items) && /cod/.test(off.items), "offline payment methods are a registry", off && off.items);
    const C = mk(); await C("/api/session?store=luxora");
    ok((await C("/api/auth/login?store=luxora", "POST", { email: "demo@luxora.shop", password: "demo123" })).status === 200, "a shopper signs in");
    const prod = db.get("SELECT id FROM products WHERE tenant_id=1 AND stock>5 ORDER BY id LIMIT 1");
    const buy = async extra => {
      await C("/api/cart?store=luxora", "POST", { id: prod.id, qty: 1 });
      return C("/api/checkout?store=luxora", "POST", { name: "Pat Buyer", address: "1 Main St", city: "Portland", state: "OR", zip: "97201", ...extra });
    };
    const o1 = await buy({ gateway: "cod" });
    ok(o1.status === 200, "cash on delivery checks out", o1.body.error);
    const ord1 = db.get("SELECT id, ship_option carrier FROM orders WHERE tenant_id=1 ORDER BY id DESC LIMIT 1");
    const pay1 = db.get("SELECT status FROM payments WHERE tenant_id=1 AND order_id=?", ord1.id);
    ok(pay1 && pay1.status === "pending", "an offline method leaves the payment pending", pay1);
    const primary = db.get("SELECT provider_id FROM tenant_gateways WHERE tenant_id=1 AND provider_id LIKE 'ship:%' AND enabled=1 ORDER BY is_primary DESC, position LIMIT 1").provider_id.slice(5);
    ok(ord1.carrier === primary, "with no carrier chosen, the store's primary carrier ships it", { carrier: ord1.carrier, primary });
    db.run("DELETE FROM provider_availability WHERE provider_id='cod' AND country_code='US'");
    const o2 = await buy({ gateway: "cod" });
    ok(o2.status === 422, "once cash on delivery is unlinked from the country, checkout refuses it", o2.body);
    const prov2 = (await C("/api/providers?store=luxora")).body;
    ok(!(prov2.gateways || []).some(g => g.id === "cod"), "and the shopper is no longer offered it", (prov2.gateways || []).map(g => g.id));
    db.run("INSERT OR IGNORE INTO provider_availability(provider_id,country_code) VALUES('cod','US')");
    const inv = db.get("SELECT id FROM invoices WHERE status!='paid' ORDER BY id LIMIT 1") || null;
    if (inv) {
      const ip = await P("/api/platform/invoices/" + inv.id + "/pay", "POST", {});
      ok(ip.status === 422 && /gateway/i.test(ip.body.error || ""), "collecting an invoice names its gateway — none is assumed", ip.body);
    } else ok(true, "no unpaid invoice to collect (skipped)");
  } catch (e) {
    failed++; console.error("  ✗ harness error:", e && e.stack || e);
  } finally {
    for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
  }
  console.log(`\n${passed} passed, ${failed} failed`);
  process.exit(failed ? 1 : 0);
})();
