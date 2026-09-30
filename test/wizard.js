/* Wizard smoke: log into the platform console, walk the guided setup wizard, launch a store. */
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
    console.log("▸ GUIDED SETUP WIZARD");
    const login = await f("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" });
    ok(login.ok, "platform login");
    const { doc, win, errs } = await render("/platform.html", 2500);
    ok(errs.length === 0, "console boots with no JS errors", errs.join(" | ").slice(0, 200));

    /* open the wizard (the console lands on Command; the nav carries Setup) */
    const navBtn = Array.from(doc.querySelectorAll(".p-nav button")).find(b => b.dataset.v === "setup");
    ok(!!navBtn, "Setup Wizard is in the nav");
    if (navBtn) { click(win, navBtn); await sleep(900); }
    const wName = doc.getElementById("wName");
    ok(!!wName, "wizard step 1 (identity) rendered");
    if (!wName) { console.log(failed ? `\n${passed} passed, ${failed} failed` : "abort"); process.exit(1); }
    doc.getElementById("wName").value = "Acme One"; doc.getElementById("wSlug").value = "acme1";
    doc.getElementById("wTag").value = "Wizard-launched store";
    click(win, doc.querySelector('[data-wz="next"]')); await sleep(700);
    ok(doc.getElementById("wOwnName"), "advanced to owner step", doc.body.textContent.slice(0, 60));

    // step 2: owner
    doc.getElementById("wOwnName").value = "Ava One"; doc.getElementById("wOwnEmail").value = "owner@acme1.shop"; doc.getElementById("wOwnPass").value = "acme1234";
    click(win, doc.querySelector('[data-wz="next"]')); await sleep(700);
    ok(doc.getElementById("wCountry"), "advanced to jurisdiction step");

    // step 3: jurisdiction — pick India to change the gateway/shipping availability
    doc.getElementById("wCountry").value = "IN";
    doc.getElementById("wCountry").dispatchEvent(new win.Event("change", { bubbles: true }));
    await sleep(300);
    ok(doc.getElementById("wTaxHint").textContent.includes("gst"), "country tax hint shows gst", doc.getElementById("wTaxHint").textContent);
    click(win, doc.querySelector('[data-wz="next"]')); await sleep(700);

    // step 4: payments — IN availability should have disabled unsupported gateways
    const gwBoxes = Array.from(doc.querySelectorAll("[data-gw]"));
    ok(gwBoxes.length > 0, "gateway list rendered");
    await sleep(400); /* let the change handler's availability pass settle */
    const disabled = Array.from(doc.querySelectorAll("[data-gw]")).filter(b => b.disabled).map(b => b.dataset.gw);
    ok(disabled.includes("square"), "US-only gateway disabled for IN", disabled.join(","));
    const rz = doc.querySelector('[data-gw="razorpay"]');
    ok(rz && !rz.disabled, "razorpay available for IN");
    click(win, doc.querySelector('[data-wz="next"]')); await sleep(700);

    // step 5: shipping — set rates + carriers
    ok(doc.getElementById("wFreeShip"), "shipping step rendered");
    doc.getElementById("wFreeShip").value = "60";
    const delhivery = doc.querySelector('[data-ship="delhivery"]');
    ok(delhivery && !delhivery.disabled, "delhivery carrier available for IN");
    if (delhivery) delhivery.checked = true;
    click(win, doc.querySelector('[data-wz="next"]')); await sleep(700);

    // step 6: catalogue
    ok(doc.getElementById("wIndGrid"), "catalogue step rendered");
    click(win, doc.querySelector('[data-wz="next"]')); await sleep(700);

    // step 7: features — toggle two on
    ok(doc.querySelector("[data-feat]"), "features step rendered");
    doc.querySelector('[data-feat="membership"]').checked = true;
    doc.querySelector('[data-feat="subscribeSave"]').checked = true;
    click(win, doc.querySelector('[data-wz="next"]')); await sleep(700);

    // step 8: launch
    ok(doc.getElementById("wzGo"), "launch button rendered");
    const sent = [];
    const origFetch = win.fetch;
    win.fetch = (u, o) => { if (String(u).includes("/platform/tenants")) sent.push({ u: String(u), o }); return origFetch(u, o); };
    click(win, doc.getElementById("wzGo")); await sleep(2500);
    win.fetch = origFetch;
    ok(doc.querySelector(".p-modal"), "checklist modal appeared after launch");
    if (sent.length) console.log("    jur:", (sent[0].o.body || "").match(/"jurisdiction":\{[^}]*\}/) + " | country-field: " + (sent[0].o.body || "").match(/"country":"[A-Z]{2}"/));
    else console.log("    no /platform/tenants call captured — launch button may not have fired");

    // verify through the API (independent witness)
    const cfg = await f("/api/config?store=acme1");
    ok(cfg.brand && cfg.brand.name === "Acme One", "storefront brand is Acme One", cfg.brand && cfg.brand.name);
    ok(cfg.commerce && cfg.commerce.freeShipThreshold === 60, "free-ship threshold 60", cfg.commerce && cfg.commerce.freeShipThreshold);
    ok(cfg.commerce && cfg.commerce.currency === "INR", "INR derived from jurisdiction", cfg.commerce && cfg.commerce.currency);
    ok(cfg.features && cfg.features.membership === true && cfg.features.subscribeSave === true, "wizard feature flags applied");
    const setup = await f("/api/platform/tenants/" + cfg.tenant.id + "/setup");
    ok(setup.steps && setup.total >= 8, "setup endpoint reports steps", setup.error);
    ok(setup.done >= 7, "checklist marks the wizard's own steps done (" + setup.done + "/" + setup.total + ")", setup.error);
    const ships = await f("/api/shipping/providers");
    ok(ships, "shipping registry reachable");

    /* ── edit mode: re-open the wizard on the store we just launched ── */
    console.log("▸ WIZARD · EDIT MODE");
    const editNav = Array.from(doc.querySelectorAll(".p-nav button")).find(b => b.dataset.v === "tenants");
    if (editNav) { click(win, editNav); await sleep(900); }
    const setupBtn = doc.querySelector('[data-tedit="' + cfg.tenant.id + '"]');
    ok(!!setupBtn, "store row has a Setup button");
    if (setupBtn) {
      click(win, setupBtn); await sleep(1200);
      ok(doc.getElementById("wName") && doc.getElementById("wName").value === "Acme One", "wizard re-opened pre-filled", doc.getElementById("wName") && doc.getElementById("wName").value);
      ok(doc.getElementById("wSlug") && doc.getElementById("wSlug").disabled, "slug locked in edit mode");
      /* jump to the shipping step and change the free-ship threshold, then go to the
         launch step (Save lives there, not on the shipping step) */
      const shipStep = doc.querySelector('[data-goto="4"]');
      if (shipStep) { click(win, shipStep); await sleep(900); }
      const fs = doc.getElementById("wFreeShip");
      ok(fs && Number(fs.value) === 60, "shipping step shows current threshold 60", fs && fs.value);
      if (fs) fs.value = "99";
      const launchStep = doc.querySelector('[data-goto="7"]');
      if (launchStep) { click(win, launchStep); await sleep(900); }
      const saveBtn = doc.getElementById("wzGo");
      ok(!!saveBtn, "save button present on the launch step");
      if (saveBtn) { click(win, saveBtn); await sleep(2200); }
      const cfg2 = await f("/api/config?store=acme1");
      ok(cfg2.commerce && cfg2.commerce.freeShipThreshold === 99, "edit-mode save changed threshold to 99", cfg2.commerce && cfg2.commerce.freeShipThreshold);
      ok(cfg2.commerce && cfg2.commerce.currency === "INR", "INR survived the edit", cfg2.commerce && cfg2.commerce.currency);
      ok(cfg2.commerce && cfg.commerce && cfg2.commerce.taxRate === cfg.commerce.taxRate && cfg2.commerce.taxMode === cfg.commerce.taxMode,
        "tax preserved across the edit (" + (cfg.commerce && cfg.commerce.taxMode) + " @ " + (cfg.commerce && cfg.commerce.taxRate) + ")",
        cfg2.commerce && JSON.stringify({ mode: cfg2.commerce.taxMode, rate: cfg2.commerce.taxRate }));
    }

    console.log(failed ? `\n${passed} passed, ${failed} failed` : `\n${passed} passed, 0 failed`);
  } finally {
    try { srv.kill("SIGKILL"); } catch (e) { }
    try { require("fs").rmSync(db, { force: true }); } catch (e) { }
  }
  process.exit(failed ? 1 : 0);
})().catch(e => { console.log("ABORT", e.message); process.exit(1); });
