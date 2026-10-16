/* LUXORA Platform — any kind of platform, any number of each, configured from the console.
   A kind is a registry row (deployModes): what one is called, the capability blend it
   starts with, what registration provisions for it and which console sections apply.
   Registering a platform of a kind applies all of it; editing or adding a kind is data. */
"use strict";
const path = require("path");
const fs = require("fs");
const DB = path.join(__dirname, "kinds.db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
const PORT = 8884;
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
  const whs = tid => db.all("SELECT country FROM warehouses WHERE tenant_id=?", tid).map(r => r.country);
  const owner = n => ({ owner: { name: "Owner " + n, email: "owner@" + n + ".test", password: "Str0ng-" + n + "-pass" } });
  /* what the platform's own admin is shown, as the console's nav reads it */
  const sectionsOf = async slug => {
    const S = mk(); await S("/api/session?store=" + slug);
    await S("/api/auth/login?store=" + slug, "POST", { email: "owner@" + slug + ".test", password: "Str0ng-" + slug + "-pass" });
    return (await S("/api/auth/me?store=" + slug)).body;
  };

  try {
    const P = mk(); await P("/api/session");
    ok((await P("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" })).status === 200, "platform owner signs in");

    console.log("▸ KINDS ARE REGISTRY ROWS");
    const kd = (await P("/api/platform/kinds")).body;
    const keys = (kd.kinds || []).map(k => k.key);
    ok(["marketplace", "industry", "brand", "mobility", "operations", "fintech"].every(k => keys.includes(k)), "the shipped kinds are served", keys);
    ok(kd.presets.some(p => p.key === "blend_mobility") && kd.sections.some(x => x.key === "rides" && x.capabilities.includes("ride_hailing")),
      "the editor gets the blends and the console sections, with the capabilities that own some");
    ok(kd.sections.some(x => x.key === "ops_hr"), "underscore-named sections (ops_hr…) exist as console sections");
    const meta = (await P("/api/meta")).body;
    ok(meta.deployModes.find(m => m.key === "mobility").provision.shipping === false, "/api/meta serves each kind's provisioning");

    console.log("▸ A KIND PROVISIONS ONLY WHAT IT DECLARES");
    const mob = await P("/api/platform/tenants", "POST", { name: "Ride Co", slug: "rideco", country: "IN", mode: "mobility", ...owner("rideco") });
    ok(mob.status === 200, "a mobility platform registers by kind alone", mob.body.error);
    const mt = mob.body.tenant.id;
    ok(mob.body.archetype === "blend_mobility", "it starts with its kind's blend", mob.body.archetype);
    ok(!gw(mt).some(g => g.startsWith("ship:")) && gw(mt).some(g => !g.includes(":")), "it has payment gateways and no shipping carriers", gw(mt));
    ok(whs(mt).length === 0, "and no warehouse — not even demo ones", whs(mt));
    ok(mob.body.storeUrl === null && mob.body.kind.noun === "operator", "it has no shopfront, and one is called an operator", mob.body.kind);
    const mme = await sectionsOf("rideco");
    ok(mme.allowedSections.includes("rides") && mme.allowedSections.includes("fleet"), "its admin sees rides and fleet", mme.allowedSections);
    ok(!["shipping", "returns", "content", "sitemap", "ugc", "products"].some(k => mme.allowedSections.includes(k)), "and no shop screens", mme.allowedSections);
    ok(mme.tenant.kind && mme.tenant.kind.noun === "operator", "the console is told its kind");
    const ms = (await P("/api/platform/tenants/" + mt + "/setup")).body;
    ok(!ms.steps.some(x => ["shipping", "catalogue", "features"].includes(x.key)) && ms.steps.some(x => x.key === "capabilities"), "its setup checklist has no shop steps", ms.steps.map(x => x.key));

    const erp = await P("/api/platform/tenants", "POST", { name: "Make Co", slug: "makeco", country: "IN", mode: "operations", ...owner("makeco") });
    ok(erp.status === 200 && erp.body.archetype === "blend_operations", "an ERP platform registers with its blend", erp.body.error || erp.body.archetype);
    ok(JSON.stringify(whs(erp.body.tenant.id)) === '["IN"]', "it gets one warehouse, in its own country", whs(erp.body.tenant.id));
    const eme = await sectionsOf("makeco");
    ok(["ops_hr", "ops_mfg", "ops_proj", "ops_proc"].every(k => eme.allowedSections.includes(k)), "its admin sees People & Payroll, Manufacturing, Projects and Purchase Requests", eme.allowedSections);

    const none = await P("/api/platform/tenants", "POST", { name: "Bare Co", slug: "bareco", country: "IN", mode: "mobility", archetype: "", ...owner("bareco") });
    ok(none.status === 200 && none.body.archetype === null, "an explicit empty blend registers with none", none.body.archetype);

    const shop = await P("/api/platform/tenants", "POST", { name: "Shop Co", slug: "shopco", country: "IN", mode: "marketplace", ...owner("shopco") });
    const st = shop.body.tenant.id;
    ok(gw(st).some(g => g.startsWith("ship:")) && JSON.stringify(whs(st)) === '["IN"]', "a marketplace still gets carriers, and one warehouse in its country (no US demo ones)", { gw: gw(st), wh: whs(st) });
    ok((await sectionsOf("shopco")).allowedSections.includes("shipping"), "and every shop screen");

    console.log("▸ A PLATFORM STARTS WITH ITS COUNTRY'S OWN PROVIDERS");
    /* the country's own providers rank ahead of worldwide ones — no provider is named in code */
    ok(["razorpay", "upi", "cod"].every(g => gw(st).includes(g)) && !gw(st).includes("paypal") && !gw(st).includes("adyen"), "an Indian platform starts with Razorpay, UPI and cash on delivery", gw(st));
    ok(db.get("SELECT provider_id FROM tenant_gateways WHERE tenant_id=? AND is_primary=1 AND provider_id NOT LIKE '%:%'", st).provider_id === "razorpay", "Razorpay is its primary gateway");
    ok(gw(st).includes("ship:delhivery") && gw(st).includes("ship:bluedart"), "and Indian carriers", gw(st));
    const us = await P("/api/platform/tenants", "POST", { name: "US Co", slug: "usco", country: "US", mode: "marketplace", ...owner("usco") });
    ok(us.status === 200 && gw(us.body.tenant.id)[0] !== undefined && db.get("SELECT provider_id FROM tenant_gateways WHERE tenant_id=? AND is_primary=1 AND provider_id NOT LIKE '%:%'", us.body.tenant.id).provider_id === "stripe", "a US platform still starts with Stripe", gw(us.body.tenant.id));
    const deny = await P("/api/platform/rules", "POST", { rule: { subject_type: "gateway", subject: "razorpay", effect: "deny", scope: { kinds: ["mobility"] } } });
    const brand = await P("/api/platform/tenants", "POST", { name: "Cab Co", slug: "cabco", country: "IN", mode: "mobility", ...owner("cabco") });
    ok(deny.status === 200 && brand.status === 200 && brand.body.tenant && !gw(brand.body.tenant.id).includes("razorpay") && gw(brand.body.tenant.id).includes("upi"), "a gateway an availability rule denies for the kind is never provisioned", gw(brand.body.tenant.id));
    await P("/api/platform/rules/" + deny.body.rule.id, "DELETE");

    console.log("▸ ANY KIND, CONFIGURED FROM THE CONSOLE");
    const bad = await P("/api/platform/kinds", "POST", { kind: { key: "Bad Key", name: "x" } });
    ok(bad.status === 400, "a malformed key is refused", bad.body);
    ok((await P("/api/platform/kinds", "POST", { kind: { key: "clinic", name: "Clinic", archetype: "nope" } })).status === 400, "an unknown blend is refused");
    ok((await P("/api/platform/kinds", "POST", { kind: { key: "clinic", name: "Clinic", sections: ["dash", "nope"] } })).status === 400, "an unknown section is refused");
    const add = await P("/api/platform/kinds", "POST", { kind: { key: "clinic", name: "Clinic Network", desc: "Appointments and billing", noun: "clinic", nounPlural: "clinics",
      archetype: "", provision: { payments: true, shipping: false, warehouse: false, storefront: false }, sections: ["dash", "settings", "team", "payments", "helpdesk", "rides"] } });
    ok(add.status === 200 && add.body.kind.noun === "clinic", "a new kind is added", add.body.error);
    ok(!add.body.kind.sections.includes("rides"), "a capability-owned section is never kept on a kind", add.body.kind.sections);
    const c1 = await P("/api/platform/tenants", "POST", { name: "Clinic One", slug: "clinic1", country: "IN", mode: "clinic", ...owner("clinic1") });
    const c2 = await P("/api/platform/tenants", "POST", { name: "Clinic Two", slug: "clinic2", country: "IN", mode: "clinic", ...owner("clinic2") });
    ok(c1.status === 200 && c2.status === 200, "any number of platforms launch from it", c1.body.error || c2.body.error);
    const cme = await sectionsOf("clinic2");
    ok(cme.allowedSections.includes("helpdesk") && !cme.allowedSections.includes("orders") && !cme.allowedSections.includes("analytics"), "each gets exactly the kind's sections", cme.allowedSections);
    const listed = (await P("/api/platform/kinds")).body.kinds.find(k => k.key === "clinic");
    ok(listed.platforms === 2, "the kinds list counts its platforms", listed.platforms);
    const ts = (await P("/api/platform/tenants")).body.tenants.find(t => t.slug === "clinic1");
    ok(ts.kind && ts.kind.name === "Clinic Network", "the tenant list names each platform's kind");

    const edit = await P("/api/platform/kinds", "POST", { kind: { ...listed, sections: listed.sections.concat(["analytics"]) } });
    ok(edit.status === 200, "a kind is edited", edit.body.error);
    ok((await sectionsOf("clinic1")).allowedSections.includes("analytics"), "an edit reaches the platforms already launched");
    ok((await P("/api/platform/kinds/clinic", "DELETE", {})).status === 409, "a kind in use cannot be removed");
    await P("/api/platform/kinds", "POST", { kind: { key: "spare", name: "Spare" } });
    ok((await P("/api/platform/kinds/spare", "DELETE", {})).status === 200, "an unused kind is removed");

    const shell = fs.readFileSync(path.join(__dirname, "../public/js/platform.js"), "utf8");
    ok(/function kindsPanel/.test(shell) && /data-klaunch/.test(shell) && /function kindModal/.test(shell), "the console has the kinds panel, launch and editor");
  } catch (e) { failed++; console.log("  ✗ threw: " + (e && e.stack || e)); }
  console.log(`\n${passed} passed, ${failed} failed`);
  for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
  process.exit(failed ? 1 : 0);
})();
