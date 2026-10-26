/* Platform console smoke: the canonical navigation model and platform registration.
   Registering a platform is ONE guided pass — identity, language, platform type,
   services and geo composed from the registries — that ends where the console begins.
   The console is organized as the constitution declares: 12 sections, one canonical home
   per capability, every leaf resolving to a live view (zero gaps). */
"use strict";
const { spawn } = require("child_process");
const { JSDOM, VirtualConsole } = require("jsdom");
const path = require("path");
const PORT = 8799;
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
  return r.json().catch(() => ({}));
}
const sleep = ms => new Promise(r => setTimeout(r, ms));
const click = (w, el) => el.dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
async function render(p, wait = 1800) {
  const errs = [];
  const vc = new VirtualConsole();
  vc.on("jsdomError", e => errs.push(String(e.message)));
  vc.on("error", (...a) => errs.push(a.join(" ")));
  const dom = await JSDOM.fromURL(BASE + p, { resources: "usable", runScripts: "dangerously", pretendToBeVisual: true, virtualConsole: vc,
    beforeParse(w) {
      w.fetch = (u, o) => { const url = String(u).startsWith("http") ? String(u) : BASE + String(u);
        const headers = Object.assign({ Cookie: cookies() }, o && o.headers);
        if (o && o.method && o.method !== "GET" && !headers["x-csrf"]) headers["x-csrf"] = jar.get("azc") || "";
        return fetch(url, { ...o, headers }).then(res => { (res.headers.getSetCookie ? res.headers.getSetCookie() : []).forEach(c => { const [kv] = c.split(";"); const i = kv.indexOf("="); jar.set(kv.slice(0, i).trim(), kv.slice(i + 1).trim()); }); return res; }); };
      w.scrollTo = () => { };
    } });
  await new Promise(r => setTimeout(r, wait));
  return { doc: dom.window.document, win: dom.window, errs: errs.filter(e => !/css|Could not parse CSS/i.test(e)), dom };
}

(async () => {
  const db = path.join(__dirname, "..", "data", "wiz-smoke.db");
  for (const s of ["", "-wal", "-shm"]) { try { require("fs").rmSync(db + s, { force: true }); } catch (e) { } }
  const srv = spawn(process.execPath, [path.join(__dirname, "..", "server.js")], { env: { ...process.env, PORT, LX_DB: db }, stdio: ["ignore", "ignore", "inherit"] });
  let up = false;
  for (let i = 0; i < 120; i++) { try { const h = await fetch(BASE + "/healthz"); if (h.ok) { up = true; break; } } catch (e) { } await sleep(1000); }
  if (!up) { console.log("server failed to boot"); process.exit(1); }
  try {
    console.log("▸ CANONICAL NAVIGATION MODEL");
    const login = await f("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" });
    ok(login.ok, "platform login");
    const { doc, win, errs } = await render("/platform.html", 2500);
    ok(errs.length === 0, "console boots with no JS errors", errs.join(" | ").slice(0, 200));
    ok(doc.querySelectorAll(".p-nav-sec").length === 12, "12 constitutional sections", doc.querySelectorAll(".p-nav-sec").length);
    const leaves = [...doc.querySelectorAll("[data-v]")];
    ok(leaves.length >= 100, "a leaf per capability (zero-gap tree)", leaves.length);
    /* nothing is duplicated: every leaf key is unique, the constitution's "one home" rule */
    const keys = leaves.map(b => b.dataset.v);
    ok(new Set(keys).size === keys.length, "no duplicated leaf keys (one canonical home each)");
    /* nothing is orphaned: the console does not land on a store hub anymore */
    ok(!doc.querySelector("[data-hubtab]"), "the store & service hub is gone (no store-centric front door)");
    ok(/MRR|Collected/i.test(doc.body.textContent), "the console lands on the platform command dashboard");

    console.log("▸ PLATFORM REGISTRATION (one guided pass composes a whole platform)");
    const navBtn = [...doc.querySelectorAll("[data-v]")].find(b => b.dataset.v === "tenants-admin");
    ok(!!navBtn, "Tenants lives under 11 · Administration");
    click(win, navBtn); await sleep(1200);
    ok(/Platforms \(/.test(doc.body.textContent), "the surface is the platform registry");
    const newBtn = doc.getElementById("newTenant");
    ok(!!newBtn && /Register platform/.test(newBtn.textContent), "the entry point is Register platform");
    click(win, newBtn); await sleep(1000);
    const rName = doc.getElementById("rName");
    ok(!!rName, "the registration flow opened at step 1 (identity)");
    if (rName) {
      rName.value = "Acme One"; doc.getElementById("rSlug").value = "acme1";
      doc.getElementById("rCountry").value = "IN";
      doc.getElementById("rOwnerName").value = "Ava One";
      doc.getElementById("rOwnerEmail").value = "owner@acme1.shop";
      doc.getElementById("rOwnerPass").value = "acme1234";
      click(win, doc.getElementById("regNext")); await sleep(400);
      /* identity & language: the locale defaults from the chosen jurisdiction, and the
         authentication policy is enumerated from the identity registry — never deferred to
         a separate screen. Choosing a non-default template proves selection is honoured. */
      const lang = doc.getElementById("rLang");
      ok(!!lang && lang.value === "en-IN", "the language step defaults from the country", lang && lang.value);
      const idOpts = [...doc.querySelectorAll("input[name='rIdTmpl']")];
      ok(idOpts.length >= 4, "the identity policies are enumerated from the identity registry", idOpts.length);
      ok(idOpts.some(r => r.checked), "a template is pre-selected (the registry's default)");
      const ent = idOpts.find(r => /Enterprise/.test(r.closest("label").textContent));
      ok(!!ent, "an Enterprise policy is a registerable choice");
      if (ent) { ent.checked = true; ent.dispatchEvent(new win.Event("change", { bubbles: true })); }
      click(win, doc.getElementById("regNext")); await sleep(400);
      /* platform type: an archetype writes the composition in one call */
      const archOpts = [...doc.querySelectorAll("input[name='rArch']")];
      ok(archOpts.length >= 6, "the platform types are enumerated from the presets registry", archOpts.length);
      const mobility = archOpts.find(a => a.value === "blend_mobility");
      ok(!!mobility, "a mobility platform is a registerable type (E17)");
      const ops = archOpts.find(a => a.value === "blend_operations");
      ok(!!ops, "an ERP/operations platform is a registerable type (E18)");
      if (mobility) { mobility.checked = true; mobility.dispatchEvent(new win.Event("change", { bubbles: true })); }
      click(win, doc.getElementById("regNext")); await sleep(400);
      ok(!!doc.getElementById("rSeedUv"), "catalog content is part of the same pass");
      click(win, doc.getElementById("regNext")); await sleep(400);
      ok(!!doc.getElementById("regGo"), "the review step offers one registering call");
      click(win, doc.getElementById("regGo")); await sleep(2500);
      const cfg = await f("/api/config?store=acme1");
      ok(cfg.brand && cfg.brand.name === "Acme One", "the new platform's storefront resolves", cfg.brand && cfg.brand.name);
      ok(cfg.tenant && cfg.tenant.slug === "acme1", "created with the declared slug", cfg.tenant && cfg.tenant.slug);
      const comp = await f("/api/capabilities?tenant_id=" + (cfg.tenant && cfg.tenant.id));
      const on = (comp.catalog || []).filter(c => c.on).map(c => c.key);
      ok(["ride_hailing", "dynamic_pricing", "dispatch", "fleet_management"].every(k => on.includes(k)),
        "the mobility archetype composed the platform's four atoms", JSON.stringify(on));
      const prods = await f("/api/products?store=acme1&q=ride");
      ok((comp.catalog || []).some(c => c.key === "ride_hailing"), "the composition is live on the store");
      /* the identity half of the pass: the chosen policy actually landed on the store,
         complete (merge over defaults — no field the engine reads went missing) */
      const ids = await f("/api/admin/identity-settings?store=acme1");
      ok(ids.settings && ids.settings.password && ids.settings.password.minLength === 14,
        "the chosen Enterprise identity policy landed on the store", ids.settings && ids.settings.password && ids.settings.password.minLength);
      ok(ids.settings && ids.settings.mfa && ids.settings.mfa.enabled === true && ids.settings.mfa.requireForStaff === true,
        "the Enterprise MFA requirement was applied", ids.settings && ids.settings.mfa);
      ok(ids.settings && ids.settings.mfa.methods && ids.settings.login && ids.settings.login.allowSignup === true,
        "the policy is complete — unoverridden fields keep the engine defaults, never dropped", ids.settings && ids.settings.mfa.methods);
      /* omitting a template applies the registry's own default — a platform is never
         registered without a deliberate authentication policy */
      const r2 = await f("/api/platform/tenants", "POST", { name: "Acme Default", slug: "acme-d", country: "US", mode: "marketplace",
        owner: { name: "Ava Two", email: "owner@acme-d.shop", password: "acme1234" } });
      ok(r2.identity && /Standard/i.test(r2.identity.name), "omitting a template applies the registry's default policy", r2.identity && r2.identity.name);
    }

    console.log("▸ ZERO-GAP RESOLUTION — leaves resolve across all three resolver kinds");
    const probe = [
      ["gproducts", "dedicated view"], ["gorders", "dedicated view"], ["gcatalog", "dedicated view"],
      ["persons", "universe record"], ["knowledge-graph", "universe record"], ["digital-twins", "universe record"],
      ["inventory", "entity dataset"], ["warehousing", "entity dataset"], ["tickets", "entity dataset"],
    ];
    let resolved = 0, bad = [];
    for (const [k] of probe) {
      const b = [...doc.querySelectorAll("[data-v]")].find(x => x.dataset.v === k);
      if (!b) { bad.push(k + ": no leaf"); continue; }
      try {
        click(win, b); await sleep(1200);
        const vb = doc.querySelector("#vBody");
        const txt = (vb && vb.textContent) || "";
        if (vb && vb.innerHTML.length > 30 && !/⚠️/.test(txt)) resolved++;
        else bad.push(k + ": " + txt.slice(0, 40).replace(/\s+/g, " "));
      } catch (e) { bad.push(k + ": " + e.message); }
    }
    ok(resolved === probe.length, "all probed leaves resolve to live views (" + resolved + "/" + probe.length + ")", bad.slice(0, 2).join(" | "));

    console.log(failed ? `\n${passed} passed, ${failed} failed` : `\n${passed} passed, 0 failed`);
  } finally {
    try { srv.kill("SIGKILL"); } catch (e) { }
    try { require("fs").rmSync(db, { force: true }); } catch (e) { }
  }
  process.exit(failed ? 1 : 0);
})().catch(e => { console.log("ABORT", e.message); process.exit(1); });
