/* LUXORA Platform — applicability rules: where, for whom and for what anything applies.
   One engine (lib/rules.js) decides every subject — gateway, method, bank, carrier,
   capability, module, service, AI model, promotion, offer, coupon, sign-in method, and any
   type an operator registers — by any registered dimension: platform kind, platform,
   country or country group, currency, service, segment, channel, amount, dates, and any
   dimension added later. The platform owner bounds every platform; a platform narrows itself. */
"use strict";
const path = require("path");
const fs = require("fs");
const DB = path.join(__dirname, "rules.db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
const PORT = 8885;
Object.assign(process.env, { LX_DB: DB, PORT: String(PORT), LX_LOG: "" });
delete process.env.NODE_ENV;
const BASE = `http://localhost:${PORT}`;
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const mk = () => {
  const c = new Map();
  return async (p, m, b, h) => {
    const o = { method: m || "GET", headers: Object.assign({ Cookie: [...c].map(x => x[0] + "=" + x[1]).join("; ") }, m && m !== "GET" ? { "x-csrf": c.get("azc") || "", Origin: BASE, "Content-Type": "application/json" } : {}, h || {}) };
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
  const rules = require("../lib/rules.js");
  try {
    const P = mk(); await P("/api/session");
    ok((await P("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" })).status === 200, "platform owner signs in");

    console.log("▸ THE VOCABULARY IS DATA");
    const sch = (await P("/api/platform/rules")).body.schema;
    const types = sch.subjectTypes.map(t => t.key);
    ok(["gateway", "method", "bank", "carrier", "capability", "module", "service", "ai_model", "ai_capability", "promotion", "offer", "coupon", "login_method"].every(k => types.includes(k)), "every kind of thing is a rule subject", types);
    const dims = Object.fromEntries(sch.dimensions.map(d => [d.key, d]));
    ok(["kinds", "platforms", "countries", "currencies", "services", "segments", "channels"].every(k => dims[k]), "rules scope by kind, platform, country, currency, service, segment, channel");
    ok(dims.countries.options.some(o => o.key === "EU") && dims.countries.options.some(o => o.key === "IN"), "countries offer country groups as well as countries");
    ok(dims.segments.options.some(o => o.key === "premium") && dims.segments.options.some(o => o.key === "high_value"), "segments join the registry's and the offers engine's audiences");

    console.log("▸ A PLATFORM TO RULE");
    const t = await P("/api/platform/tenants", "POST", { name: "Bharat Bazaar", slug: "bharat", country: "IN", mode: "marketplace", seedCatalog: true, gateways: ["razorpay", "upi", "paytm", "cod"], owner: { name: "Owner", email: "owner@bharat.test", password: "Str0ng-bharat-pass" } });
    ok(t.status === 200, "an Indian marketplace is launched", t.body);
    const tid = db.get("SELECT id FROM tenants WHERE slug='bharat'").id;
    const gwOf = async (S, q) => ((await S("/api/providers?store=bharat" + (q || ""))).body.gateways || []).map(g => g.id);
    const G = mk(); await G("/api/session?store=bharat");
    const before = await gwOf(G);
    ok(before.includes("razorpay") && before.includes("cod"), "with no rules the platform's gateways are all offered", before);

    console.log("▸ PLATFORM OWNER RULES");
    const save = async (S, base, rule) => S(base, "POST", { rule });
    const cod = await save(P, "/api/platform/rules", { subject_type: "gateway", subject: "cod", effect: "deny", scope: { countries: ["IN"], min_amount: 1000 }, note: "no cash above ₹1000" });
    ok(cod.status === 200 && /deny cod/.test(cod.body.rule.summary), "a rule is saved and summarised", cod.body);
    ok(!(await gwOf(G, "&amount=5000")).includes("cod") && (await gwOf(G, "&amount=500")).includes("cod"), "cash on delivery is offered under ₹1000 only");
    ok(rules.decide("gateway", "cod", rules.context(tid, { buyer: false, country: "US", amount: 5000 })).ok === true, "the rule names IN — another country is untouched");

    const r2 = await save(P, "/api/platform/rules", { subject_type: "gateway", subject: "razorpay", effect: "allow", scope: { segments: ["signed_in"] } });
    ok(r2.status === 200, "an allow rule makes razorpay an allow-list (signed-in customers only)");
    ok(!(await gwOf(G)).includes("razorpay"), "a guest is not offered razorpay");
    const C = mk(); await C("/api/session?store=bharat");
    const reg = await C("/api/auth/register?store=bharat", "POST", { name: "Asha", email: "asha@bharat.test", password: "Asha-str0ng-pass" });
    ok(reg.status === 200, "a customer signs up", reg.body);
    ok((await gwOf(C)).includes("razorpay"), "a signed-in customer is offered razorpay");

    const bad1 = await save(P, "/api/platform/rules", { subject_type: "gateway", subject: "nope", effect: "deny" });
    const bad2 = await save(P, "/api/platform/rules", { subject_type: "gateway", subject: "cod", effect: "deny", scope: { countries: ["ZZ"] } });
    const bad3 = await save(P, "/api/platform/rules", { subject_type: "teleport", subject: "*" });
    ok(bad1.status === 400 && bad2.status === 400 && bad3.status === 400, "unknown subjects, dimension values and types are refused", [bad1.body, bad2.body, bad3.body]);

    console.log("▸ CAPABILITIES BY KIND AND COUNTRY");
    const featOf = async (S, slug) => (await S("/api/config?store=" + slug)).body.features || {};
    ok((await featOf(G, "bharat")).reviews === true, "reviews are on before any rule");
    const rv = await save(P, "/api/platform/rules", { subject_type: "capability", subject: "reviews", effect: "deny", scope: { kinds: ["marketplace"], countries: ["IN"] } });
    ok(rv.status === 200, "a capability is denied for Indian marketplaces");
    ok((await featOf(G, "bharat")).reviews === false, "the Indian marketplace loses reviews");
    const L = mk(); await L("/api/session?store=luxora");
    ok((await featOf(L, "luxora")).reviews === true, "a platform outside the scope keeps them");

    console.log("▸ A PLATFORM NARROWS ITSELF — NEVER WIDENS");
    const A = mk(); await A("/api/session?store=bharat");
    ok((await A("/api/auth/login?store=bharat", "POST", { email: "owner@bharat.test", password: "Str0ng-bharat-pass" })).status === 200, "the platform's admin signs in");
    const own = await save(A, "/api/admin/rules?store=bharat", { subject_type: "gateway", subject: "upi", effect: "deny", scope: { platforms: ["luxora"], kinds: ["brand"] } });
    ok(own.status === 200 && !own.body.rule.scope.platforms && !own.body.rule.scope.kinds, "its rule is its own — it cannot reach another platform or kind", own.body);
    ok(!(await gwOf(G)).includes("upi"), "its own deny applies to its buyers");
    const widen = await save(A, "/api/admin/rules?store=bharat", { subject_type: "gateway", subject: "cod", effect: "allow", priority: 999 });
    ok(widen.status === 200 && !(await gwOf(G, "&amount=5000")).includes("cod"), "its allow cannot lift a platform owner's deny");
    const view = (await A("/api/admin/rules?store=bharat")).body;
    ok(view.rules.length === 2 && view.inherited.some(r => r.subject === "cod") && view.inherited.some(r => r.subject === "reviews"), "it sees its own rules and the platform rules that reach it", view);
    ok(!view.schema.dimensions.some(d => d.key === "platforms"), "its editor has no platform/kind dimension");
    const x = (await A("/api/admin/rules/explain?store=bharat", "POST", { type: "gateway", context: { amount: 5000, segments: ["signed_in"] } })).body;
    const codX = (x.results || []).find(r => r.key === "cod"), rzX = (x.results || []).find(r => r.key === "razorpay");
    ok(codX && !codX.ok && /platform rule/.test(codX.reasons.join(" ")) && rzX && rzX.ok, "explain says what is blocked and why", x.results && x.results.slice(0, 4));
    const P2 = (await P("/api/platform/rules/explain", "POST", { type: "capability", context: { platform: "bharat" } })).body.results.find(r => r.key === "reviews");
    ok(P2 && !P2.ok, "the platform owner explains for any platform");
    ok((await P("/api/admin/rules?store=bharat")).status === 200, "the platform owner can open a platform's rules");

    console.log("▸ SERVICES, BANKS AND THE INSTRUMENTS THEY USE");
    db.run("INSERT INTO capability_values(tenant_id,capability,enabled,params) VALUES(?,?,1,'{}') ON CONFLICT(tenant_id,capability) DO UPDATE SET enabled=1", tid, "bank_payouts");
    await save(P, "/api/platform/rules", { subject_type: "bank", subject: "hdfc", effect: "deny", scope: { services: ["payout"] } });
    const po1 = await A("/api/fintech/payouts?store=bharat", "POST", { payee: "Vendor", amount: 100, currency: "INR", account_name: "V", account_number: "1234", ifsc: "HDFC0000123" });
    const po2 = await A("/api/fintech/payouts?store=bharat", "POST", { payee: "Vendor", amount: 100, currency: "INR", account_name: "V", account_number: "1234", ifsc: "SBIN0000123" });
    ok(po1.status >= 400 && /HDFC|hdfc/.test(po1.body.error || ""), "a payout to a bank denied for payouts is refused, naming the rule", po1.body);
    ok(po2.status === 200, "a payout to another bank goes through", po2.body);
    ok(rules.bankOf({ ifsc: "ICIC0001" }) === "icici" && rules.bankOf({ swift: "BARCGB22" }) === "barclays", "a bank is recognised from IFSC or SWIFT");
    await save(P, "/api/platform/rules", { subject_type: "service", subject: "order", effect: "deny", scope: { channels: ["pos"] } });
    const chk = await G("/api/rules/check?store=bharat", "POST", { type: "service", id: "order" }, { "x-channel": "pos" });
    ok(chk.status === 200 && chk.body.ok === false && chk.body.reasons === undefined, "any caller can ask; a shopper gets the verdict, not the rule text", chk.body);
    ok((await G("/api/rules/check?store=bharat", "POST", { type: "service", id: "order" })).body.ok === true, "on the web channel the service is open");

    console.log("▸ A DIMENSION ADDED LATER NEEDS NO CODE");
    const dimAdd = await P("/api/platform/registries/ruleDimensions", "POST", { item: { key: "devices", name: "Devices", fact: "device", match: "in", options: "" } });
    ok(dimAdd.status === 200, "a 'devices' dimension is registered", dimAdd.body);
    rules.bust();
    const dr = await save(P, "/api/platform/rules", { subject_type: "gateway", subject: "paytm", effect: "deny", scope: { devices: ["kiosk"] } });
    ok(dr.status === 200 && dr.body.rule.scope.devices, "a rule scopes by it", dr.body);
    const kiosk = await G("/api/rules/check?store=bharat", "POST", { type: "gateway", id: "paytm" }, { "x-ctx-device": "kiosk" });
    const phone = await G("/api/rules/check?store=bharat", "POST", { type: "gateway", id: "paytm", context: { device: "phone" } });
    ok(kiosk.body.ok === false && phone.body.ok === true, "the request supplies the fact (header or body context)", [kiosk.body, phone.body]);
    const typeAdd = await P("/api/platform/registries/ruleSubjectTypes", "POST", { item: { key: "warehouse", name: "Warehouse", source: "entity:warehouse" } });
    rules.bust();
    ok(typeAdd.status === 200 && rules.subjects("warehouse", tid).length >= 1, "a new subject type (any Data Studio entity) is one registry row", rules.subjects("warehouse", tid));

    console.log("▸ OFFERS, AI AND SIGN-IN");
    db.run("INSERT INTO coupons(tenant_id,code,kind,value,max_uses,per_owner_limit,status) VALUES(?,?,?,?,?,?,?)", tid, "DIWALI10", "multi_use", 10, 100, 5, "active");
    const cp0 = await C("/api/coupon?store=bharat", "POST", { code: "DIWALI10" });
    await save(P, "/api/platform/rules", { subject_type: "coupon", subject: "DIWALI10", effect: "allow", scope: { segments: ["premium"] } });
    const cp1 = await C("/api/coupon?store=bharat", "POST", { code: "DIWALI10" });
    ok(cp0.status === 200 && cp1.status >= 400, "a coupon limited to premium customers is refused to others", [cp0.status, cp1.body]);
    const asha = db.get("SELECT id FROM users WHERE email='asha@bharat.test'").id;
    const mem = await A("/api/admin/segments/members?store=bharat", "POST", { email: "asha@bharat.test", segment: "premium" });
    ok(mem.status === 200 && mem.body.members.some(m => m.owner === `t${tid}:u:${asha}`), "the platform puts a customer in a segment", mem.body);
    ok((await C("/api/coupon?store=bharat", "POST", { code: "DIWALI10" })).status === 200, "the premium customer can use it");
    await save(P, "/api/platform/rules", { subject_type: "ai_model", subject: "gpt-4o", effect: "deny", scope: { countries: ["IN"] } });
    ok(rules.decide("ai_model", "gpt-4o", rules.context(tid)).ok === false && rules.decide("ai_model", "gpt-4o-mini", rules.context(tid)).ok === true, "an AI model is ruled out for a country, its siblings stay");
    await save(P, "/api/platform/rules", { subject_type: "ai_capability", subject: "reporting", effect: "deny", scope: { platforms: ["bharat"] } });
    const ai = (await A("/api/ai?store=bharat")).body;
    const rep = (ai.capabilities || []).find(c => c.key === "reporting"), rec = (ai.capabilities || []).find(c => c.key === "product_recommendation");
    ok(rep && rep.status === "blocked_by_rule" && rec && rec.status !== "blocked_by_rule", "an AI capability is blocked for one platform, the others stay", [rep, rec && rec.status]);
    const run = await A("/api/ai/run/reporting?store=bharat", "POST", {});
    ok(run.status === 403, "running the blocked AI capability is refused", run.body);
    await save(P, "/api/platform/rules", { subject_type: "login_method", subject: "password", effect: "deny", scope: { platforms: ["bharat"], channels: ["app"] } });
    const C2 = mk(); await C2("/api/session?store=bharat");
    const lgApp = await C2("/api/auth/login?store=bharat", "POST", { email: "asha@bharat.test", password: "Asha-str0ng-pass" }, { "x-channel": "app" });
    const lgWeb = await C2("/api/auth/login?store=bharat", "POST", { email: "asha@bharat.test", password: "Asha-str0ng-pass" });
    ok(lgApp.status === 403 && lgWeb.status === 200, "a sign-in method is ruled per channel", [lgApp.body, lgWeb.status]);
    ok((await A("/api/auth/login?store=bharat", "POST", { email: "owner@bharat.test", password: "Str0ng-bharat-pass" }, { "x-channel": "app" })).status === 200, "the platform's own admin is never locked out by a customer rule");

    console.log("▸ CHECKOUT HOLDS THE RULE AT PAYMENT");
    const pid = db.get("SELECT id FROM products WHERE tenant_id=? AND stock>0 AND price>1000 ORDER BY price DESC LIMIT 1", tid);
    ok(!!pid, "the catalogue has an item over ₹1000 to check out");
    if (pid) {
      await C("/api/cart?store=bharat", "POST", { id: pid.id, qty: 1 });
      const co = await C("/api/checkout?store=bharat", "POST", { name: "Asha", address: "1 MG Road", city: "Bengaluru", zip: "560001", gateway: "cod" });
      const tot = db.get("SELECT price FROM products WHERE id=? AND tenant_id=?", pid.id, tid).price;
      ok(co.status === 422 && /amount/i.test(co.body.error || ""), "cash on delivery is refused at payment when the total is over the limit", { status: co.status, body: co.body, price: tot });
      const co2 = await C("/api/checkout?store=bharat", "POST", { name: "Asha", address: "1 MG Road", city: "Bengaluru", zip: "560001", gateway: "paytm" });
      ok(co2.status === 200, "another gateway the rules permit takes the payment", co2.body);
    }

    console.log("▸ REMOVING A RULE RESTORES THE DEFAULT");
    const list = (await P("/api/platform/rules")).body.rules;
    const codRule = list.find(r => r.subject === "cod");
    ok((await P("/api/platform/rules/" + codRule.id, "DELETE")).status === 200 && (await gwOf(G, "&amount=5000")).includes("cod"), "deleting the cash rule offers cash again");
    ok((await A("/api/platform/rules", "POST", { rule: { subject_type: "gateway", subject: "cod", effect: "deny" } })).status === 403, "a platform admin cannot write the platform owner's rules");
  } catch (e) { failed++; console.log("  ✗ threw: " + (e && e.stack || e)); }
  console.log(`\n${passed} passed, ${failed} failed`);
  process.exit(failed ? 1 : 0);
})();
