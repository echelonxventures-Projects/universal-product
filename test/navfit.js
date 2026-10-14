/* THE TENANT IS WHAT IT IS — the store console's surface is data about the tenant,
   not a hardcoded menu.
   ---------------------------------------------------------------------------
   A store console section is granted by one of two things, and never by a bundle:

     · an individual CAPABILITY the tenant switched on — each atom in the catalog
       declares the nav leaves it lights (buy_box → Marketplace & Marketplace Ops,
       rfq_bidding → RFQs, instant_delivery → Quick-commerce Ops). The surface is a
       shadow of the composition: one atom on, and its leaf AND its engine arrive
       together; off, and both go. Nothing is ever sold as a package of sections.

     · the tenant's OWN PROFILE — the vertical facts no engine owns (serial tracking
       belongs to tracked-goods industries; replenishment belongs to physical stock),
       declared as NAVFIT next to the store nav and harvested into the compiled
       canonical registry.

   Both are applied at the ONE choke point that decides a grant — lib/authz.js
   storeGrants — so dropping a section there hides it in BOTH consoles' navs and refuses
   it at the API, for an owner exactly as for restricted staff.

   The three seeded tenants are the three shapes:
     luxora  — composed marketplace + B2B trade + quick-commerce, every industry
     aurum   — composed marketplace + B2B trade (no quick commerce), fashion/beauty/…
     velora  — an uncomposed brand house, jewellery + luxury → no marketplace surface */
"use strict";
const DB = require("path").join(__dirname, "navfit.db");
process.env.LX_DB = DB;
process.env.LUXORA_DEMO_BRANDS = "1";   /* these suites exercise the demo-brand fixtures */
const { spawn } = require("child_process");
const { JSDOM, VirtualConsole } = require("jsdom");
const path = require("path");
const authz = require("../lib/authz.js");
const canonical = require("../lib/canonical.js");
const PORT = 8871;
const BASE = `http://localhost:${PORT}`;
const jar = new Map();
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x ? " → " + x : ""))); };
const cookies = () => [...jar].map(([k, v]) => k + "=" + v).join("; ");
async function f(p, method = "GET", body) {
  const opt = { method, headers: { Cookie: cookies(), ...(method !== "GET" ? { "x-csrf": jar.get("azc") || "" } : {}) } };
  if (body) { opt.body = JSON.stringify(body); opt.headers["Content-Type"] = "application/json"; }
  const r = await fetch(BASE + p, opt);
  (r.headers.getSetCookie ? r.headers.getSetCookie() : []).forEach(c => { const [kv] = c.split(";"); const i = kv.indexOf("="); jar.set(kv.slice(0, i).trim(), kv.slice(i + 1).trim()); });
  return { status: r.status, body: await r.json().catch(() => ({})) };
}
const sleep = ms => new Promise(r => setTimeout(r, ms));
async function waitFor(cond, ms = 7000) {
  for (let i = 0; i < ms / 100; i++) { try { if (cond()) return true; } catch (e) { } await sleep(100); }
  return false;
}
async function render(page) {
  const errs = [];
  const vc = new VirtualConsole();
  vc.on("jsdomError", e => errs.push(String(e.message)));
  vc.on("error", (...a) => errs.push(a.join(" ")));
  const dom = await JSDOM.fromURL(BASE + page, { resources: "usable", runScripts: "dangerously", pretendToBeVisual: true, virtualConsole: vc,
    beforeParse(w) {
      w.fetch = (u, o) => { const url = String(u).startsWith("http") ? String(u) : BASE + String(u);
        const headers = Object.assign({ Cookie: cookies() }, o && o.headers);
        if (o && o.method && o.method !== "GET" && !headers["x-csrf"]) headers["x-csrf"] = jar.get("azc") || "";
        return fetch(url, { ...o, headers }).then(res => { (res.headers.getSetCookie ? res.headers.getSetCookie() : []).forEach(c => { const [kv] = c.split(";"); const i = kv.indexOf("="); jar.set(kv.slice(0, i).trim(), kv.slice(i + 1).trim()); }); return res; }); };
      w.scrollTo = () => { };
    } });
  await waitFor(() => { const d = dom.window.document;
    const body = d.querySelector("#vBody"), nav = d.querySelector(".p-nav");
    return !!body && !!nav && !/Loading/i.test(body.textContent || "") && !!nav.querySelector("button[data-s]"); });
  return { doc: dom.window.document, errs: errs.filter(e => !/css|Could not parse CSS|Not implemented/i.test(e)) };
}
const hasLeaf = (doc, v) => [...doc.querySelectorAll(".p-nav button")].some(b => b.dataset.v === v);

(async () => {
  for (const s of ["", "-wal", "-shm"]) { try { require("fs").rmSync(DB + s, { force: true }); } catch (e) { } }
  const boot = async () => {
    const srv = spawn(process.execPath, [path.join(__dirname, "..", "server.js")], { env: { ...process.env, PORT, LX_DB: DB }, stdio: ["ignore", "ignore", "inherit"] });
    for (let i = 0; i < 120; i++) {
      /* healthz answering is not proof OUR server booted: if a stale process from a killed
         run still holds PORT, the child dies on EADDRINUSE and healthz is answered by that
         stranger — and the suite would then test a server it never started. A dead child is
         the one condition that silently corrupts every assertion after it, so it is checked
         before every probe and again after one settles past the bind */
      if (srv.exitCode !== null) break;
      try { if ((await fetch(BASE + "/healthz")).ok) { await sleep(300); if (srv.exitCode === null) return srv; break; } } catch (e) { }
      await sleep(500);
    }
    throw new Error("the server we spawned did not boot — port " + PORT + " is held by a stale process from a killed run (lsof -iTCP:" + PORT + " to find it, kill the pid, re-run)");
  };
  const srv = await boot();
  try {

    console.log("▸ §A THE FITNESS MAP IS COMPILED, NOT HARDCODED");
    const fit = canonical.consoleSec().adminNavFit;
    ok(!!fit.serialized && Array.isArray(fit.serialized.industries) && fit.serialized.industries.includes("jewellery"),
      "the canonical registry harvested NAVFIT — the vertical facts no atom owns", Object.keys(fit).join(","));
    ok(!!fit.planning && fit.planning.notIndustries.includes("digital"), "planning is a vertical fact too — physical stock gets replenished");
    /* ZERO DUPLICATION — a section an atom lights is never also in NAVFIT. The
       atom-owned surface is derived from the capability catalog (each atom declares the
       leaves it governs), so re-declaring it in the store bundle would be a second
       source of one truth. */
    const secCaps = authz.capabilitySections();
    ok(secCaps.size >= 9, "the capability catalog declares the atom-owned surface", [...secCaps.keys()].sort().join(","));
    ok(secCaps.get("rfqs").includes("rfq_bidding"), "rfq_bidding lights the RFQs leaf");
    ok(secCaps.get("qcops").includes("instant_delivery"), "instant_delivery lights Quick-commerce Ops");
    ok(secCaps.get("marketplace").includes("buy_box"), "buy_box lights Marketplace");
    for (const s of secCaps.keys())
      ok(!(s in fit), "atom-owned “" + s + "” is not duplicated in NAVFIT (one source of truth)");

    console.log("▸ §B A MARKETPLACE HOLDS THE FULL STORE SURFACE (luxora)");
    jar.clear();
    await f("/api/session?store=luxora");
    const lux = await f("/api/auth/login?store=luxora", "POST", { email: "admin@luxora.shop", password: "admin123" });
    ok(!!lux.body.ok, "the luxora store admin signs in", JSON.stringify(lux.body));
    const luxSess = (await f("/api/session")).body;
    const luxAllowed = luxSess.allowedSections || [];
    for (const s of ["sellers", "marketplace", "rfqs", "tenders", "contracts", "mktops", "tradeops", "finops", "serialized", "qcops", "planning", "orders", "products", "settings", "team"])
      ok(luxAllowed.includes(s), "luxora (composed marketplace + B2B + quick-commerce) keeps “" + s + "”", luxAllowed.join(","));
    ok((await f("/api/meta/entity/rfq")).status === 200, "and the entity router reads rfqs for it");

    console.log("▸ §C A BRAND STORE IS TRIMMED TO WHAT IT IS (velora — jewellery D2C)");
    jar.clear();
    await f("/api/session?store=velora");
    const vel = await f("/api/auth/login?store=velora", "POST", { email: "admin@velora.shop", password: "velora123" });
    ok(!!vel.body.ok, "the velora store admin signs in", JSON.stringify(vel.body));
    const velAllowed = (await f("/api/session")).body.allowedSections || [];
    for (const s of ["sellers", "marketplace", "rfqs", "tenders", "contracts", "mktops", "tradeops", "qcops", "finops"])
      ok(!velAllowed.includes(s), "velora (no marketplace composition) loses “" + s + "”", velAllowed.join(","));
    ok(velAllowed.includes("planning"), "it KEEPS planning — jewellery is physical stock that gets replenished", velAllowed.join(","));
    for (const s of ["orders", "products", "settings", "team", "payments", "compliance"])
      ok(velAllowed.includes(s), "and keeps the universal “" + s + "”", velAllowed.join(","));
    ok(velAllowed.includes("serialized"), "it KEEPS serial tracking — jewellery is hallmark/serial-tracked", velAllowed.join(","));
    ok((await f("/api/meta/entity/rfq")).status === 403, "the router refuses rfqs (defence in depth, not just a hidden button)");
    ok((await f("/api/meta/entity/dark_store")).status === 403, "and refuses the quick-commerce surface");
    ok((await f("/api/meta/entity/product")).status === 200, "while the universal product surface still reads");

    console.log("▸ §D COMPOSITION BEATS OWNERSHIP — even the brand's owner lacks the unlit surface");
    ok(vel.body.user && (vel.body.user.staff_role === "owner" || vel.body.user.staff_role == null), "the signed-in velora admin is an owner", JSON.stringify(vel.body.user && vel.body.user.staff_role));
    ok(!velAllowed.includes("rfqs"), "an OWNER of an uncomposed store holds no rfqs grant — '*' is bounded by what the tenant is");
    ok(!authz.can({ store: { role: "admin", tenant_id: 3 }, tenantId: 3 }, "store:rfqs", null, "read"), "authz.can agrees: the owner cannot read store:rfqs");

    console.log("▸ §E AN INDUSTRY MARKETPLACE KEEPS B2B, DROPS THE REST (aurum — fashion/beauty/home/kitchen/health)");
    jar.clear();
    await f("/api/session?store=aurum");
    const aur = await f("/api/auth/login?store=aurum", "POST", { email: "admin@aurum.shop", password: "aurum123" });
    ok(!!aur.body.ok, "the aurum store admin signs in", JSON.stringify(aur.body));
    const aurAllowed = (await f("/api/session")).body.allowedSections || [];
    ok(["rfqs", "sellers", "tenders", "contracts", "mktops", "tradeops"].every(s => aurAllowed.includes(s)), "an industry marketplace keeps the B2B surface its composition holds", aurAllowed.join(","));
    ok(!aurAllowed.includes("serialized"), "but drops serial tracking — none of its industries track serials", aurAllowed.join(","));
    ok(!aurAllowed.includes("qcops"), "and drops quick-commerce — nothing in its composition lights it", aurAllowed.join(","));

    console.log("▸ §F THE ONE CONSOLE'S NAV IS WHAT THE TENANT IS");
    jar.clear();
    await f("/api/session?store=velora");
    await f("/api/auth/login?store=velora", "POST", { email: "admin@velora.shop", password: "velora123" });
    const V = await render("/console.html");
    ok(!V.errs.length, "velora's console boots with no JS errors", V.errs.join(" | "));
    ok(!hasLeaf(V.doc, "rfqs") && !hasLeaf(V.doc, "sellers") && !hasLeaf(V.doc, "tenders"), "the nav offers no B2B leaves", "");
    ok(hasLeaf(V.doc, "orders") && hasLeaf(V.doc, "products"), "and still offers the commerce it does run");
    jar.clear();
    await f("/api/session?store=luxora");
    await f("/api/auth/login?store=luxora", "POST", { email: "admin@luxora.shop", password: "admin123" });
    const L = await render("/console.html");
    ok(!L.errs.length, "luxora's console boots with no JS errors", L.errs.join(" | "));
    ok(hasLeaf(L.doc, "rfqs") && hasLeaf(L.doc, "sellers"), "the marketplace's nav carries the B2B leaves the brand's lacks");

    console.log("▸ §G THE FITNESS FUNCTIONS");
    /* NAVFIT governs only the vertical facts no atom owns */
    ok(authz.sectionFits("serialized", { mode: "brand", industries: ["jewellery"] }), "serial tracking fits jewellery");
    ok(!authz.sectionFits("serialized", { mode: "brand", industries: ["services"] }), "serial tracking does not fit services");
    ok(authz.sectionFits("serialized", { mode: "brand", industries: [] }), "a tenant declaring no industries is universal — fitness does not narrow it");
    ok(authz.sectionFits("planning", { mode: "brand", industries: ["jewellery"] }), "planning fits a physical vertical");
    ok(!authz.sectionFits("planning", { mode: "brand", industries: ["digital"] }), "planning does not fit a digital vertical (notIndustries)");
    ok(authz.sectionFits("orders", { mode: "brand", industries: ["jewellery"] }), "orders fit everyone — untagged sections are universal");
    ok(authz.sectionFits("unknown-section", { mode: "brand", industries: ["services"] }), "an untagged section is universal");
    ok(authz.sectionFits("anything", null) === true, "an unknown tenant is served the whole surface (fail-open: fitness never widens or narrows by accident)");
    ok(!!authz.tenantFit(3) && authz.tenantFit(3).mode === "brand", "tenantFit reads velora's mode from its row", JSON.stringify(authz.tenantFit(3)));
    /* the one choke point: an atom-owned section answers to the live composition,
       everything else answers to the tenant's own profile */
    ok(authz.sectionGranted("rfqs", authz.tenantFit(1), 1), "luxora is granted rfqs (rfq_bidding is in its composition)");
    ok(!authz.sectionGranted("rfqs", authz.tenantFit(3), 3), "velora is not granted rfqs (no rfq_bidding in its composition)");
    ok(authz.sectionGranted("serialized", authz.tenantFit(3), 3), "velora IS granted serial — a vertical fact, not an engine");
    ok(!authz.sectionGranted("qcops", authz.tenantFit(3), 3), "velora is not granted quick-commerce");
    ok(authz.sectionGranted("planning", authz.tenantFit(3), 3), "planning answers to NAVFIT alone");

    console.log("▸ §H ONE ATOM LIGHTS ITS LEAF AND ITS ENGINE — nothing is a bundle");
    /* velora is an uncomposed brand store: no RFQ surface and no RFQ engine. Switch ONE
       atom on through the console's own channel and both arrive together — the surface is
       a shadow of the composition, never a package someone buys */
    jar.clear();
    await f("/api/session?store=velora");
    await f("/api/auth/login?store=velora", "POST", { email: "admin@velora.shop", password: "velora123" });
    ok(!authz.grant({ store: { role: "admin", staff_role: "owner", tenant_id: 3 }, tenantId: 3 })["store:rfqs"], "velora starts with no rfqs grant");
    /* the capability write endpoints answer the composition itself ({tenant_id, preset,
       capabilities}), never an {ok} envelope — that is the contract test/parity.js:569
       pins and the console reads; f() returns {status, body}, so the assertion is on the
       status and the atom's presence in the returned composition */
    const en = await f("/api/capabilities/enable", "POST", { capability: "rfq_bidding" });
    ok(en.status === 200 && !!(en.body.capabilities || {}).rfq_bidding, "the store admin switches rfq_bidding on", JSON.stringify(en.body));
    ok(!!authz.grant({ store: { role: "admin", staff_role: "owner", tenant_id: 3 }, tenantId: 3 })["store:rfqs"], "and the RFQs leaf is granted with it");
    ok(authz.can({ store: { role: "admin", tenant_id: 3 }, tenantId: 3 }, "store:rfqs", null, "read"), "authz.can agrees: the owner can now read store:rfqs");
    ok((await f("/api/meta/entity/rfq")).status === 200, "and the entity router serves rfqs — the engine came with the leaf");
    const V2 = await render("/console.html");
    ok(!V2.errs.length, "velora's console boots after the switch", V2.errs.join(" | "));
    ok(hasLeaf(V2.doc, "rfqs"), "and its nav offers the RFQs leaf its atom lights");
    ok((await f("/api/capabilities")).body.catalog.some(c => c.key === "rfq_bidding" && (c.sections || []).includes("rfqs")),
      "the served catalog carries the declaration the gate derived from");
    /* switching the atom off removes both — no residual grant, no residual engine */
    const di = await f("/api/capabilities/disable", "POST", { capability: "rfq_bidding" });
    ok(di.status === 200 && !(di.body.capabilities || {}).rfq_bidding, "the atom is switched off", JSON.stringify(di.body));
    ok(!authz.grant({ store: { role: "admin", staff_role: "owner", tenant_id: 3 }, tenantId: 3 })["store:rfqs"], "the leaf is gone with the atom");
    ok((await f("/api/meta/entity/rfq")).status === 403, "and the router refuses rfqs again");

    console.log("▸ §I AN ARCHETYPE COMPOSES ATOMS — the surface still follows the composition");
    /* a purchasable archetype is a convenience that composes individual atoms; the leaves
       it lights are a consequence, never a grant it makes itself */
    jar.clear();
    await f("/api/session");
    const pl2 = await f("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" });
    ok(!!pl2.body.ok, "the platform owner signs in");
    ok(!!(await f("/api/platform/modules/pack-qcommerce/install", "POST", { tenant_id: 3 })).body.ok, "the quick-commerce archetype is installed for velora");
    ok(!!(await f("/api/capabilities?tenant_id=3")).body.composition.capabilities.instant_delivery, "it composed its atoms — instant_delivery is on");
    ok(!!authz.grant({ store: { role: "admin", staff_role: "owner", tenant_id: 3 }, tenantId: 3 })["store:qcops"], "and the Quick-commerce leaf those atoms light is granted");
    jar.clear();
    await f("/api/session?store=velora");
    await f("/api/auth/login?store=velora", "POST", { email: "admin@velora.shop", password: "velora123" });
    ok((await f("/api/meta/entity/dark_store")).status === 200, "the quick-commerce engine serves the store now");
    jar.clear();
    await f("/api/session");
    await f("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" });
    ok(!!(await f("/api/platform/modules/pack-qcommerce/uninstall", "POST", { tenant_id: 3 })).body.ok, "the archetype is released");
    ok(!(await f("/api/capabilities?tenant_id=3")).body.composition.capabilities.instant_delivery, "its atoms went with it");
    ok(!authz.grant({ store: { role: "admin", staff_role: "owner", tenant_id: 3 }, tenantId: 3 })["store:qcops"], "and the leaf it lit is gone");

    console.log(failed ? `\n${passed} passed, ${failed} FAILED` : `\n${passed} passed, 0 failed`);
  } finally {
    srv.kill();
    for (const s of ["", "-wal", "-shm"]) { try { require("fs").rmSync(DB + s, { force: true }); } catch (e) { } }
  }
  process.exit(failed ? 1 : 0);
})().catch(e => { console.log("ABORT", e && e.stack || e); process.exit(1); });
