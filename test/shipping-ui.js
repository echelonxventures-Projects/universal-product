/* LUXORA Platform — the shipping screens, clicked through in real Chrome.
   The server runs in this process with a stand-in EasyPost (connect.__setTransport), so the
   screens are exercised exactly as a person would use them without buying real postage: the
   platform admin connects the carrier account, the store admin saves a ship-from address,
   then ships a paid order — weighs the parcel, compares rates, buys one — and the platform
   admin disconnects the account again. Every step is checked in the database too, and the
   pages must raise no CSP violation, uncaught error or console error along the way. */
"use strict";
const path = require("path");
const fs = require("fs");
const os = require("os");
const { spawn } = require("child_process");
const { Tab, findChrome, problems } = require("../scripts/browser-check.js");
const DB = path.join(__dirname, "shipping-ui.db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
const PORT = 8879;
Object.assign(process.env, { LX_DB: DB, PORT: String(PORT), LX_LOG: "" });
delete process.env.NODE_ENV;
const BASE = `http://localhost:${PORT}`;
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const sleep = ms => new Promise(r => setTimeout(r, ms));

/* the stand-in carrier: one shipment with two rates, and its purchase */
const bought = [];
function fakeEasyPost(url, o) {
  let status = 200, json;
  if (url === "https://api.easypost.com/v2/shipments") json = { id: "shp_ui", rates: [
    { id: "rate_ups", carrier: "UPS", service: "Ground", rate: "11.20", currency: "USD", delivery_days: 3 },
    { id: "rate_usps", carrier: "USPS", service: "GroundAdvantage", rate: "7.85", currency: "USD", delivery_days: 4 }], messages: [] };
  else if (url === "https://api.easypost.com/v2/shipments/shp_ui/buy") { bought.push(JSON.parse(o.body).rate.id); json = { id: "shp_ui", tracking_code: "9400100000000000000001", postage_label: { label_url: "https://easypost-files.s3.amazonaws.com/ui-label.png" } }; }
  else { status = 404; json = { error: { message: "unexpected " + url } }; }
  return Promise.resolve({ ok: status < 300, status, text: async () => JSON.stringify(json) });
}

(async () => {
  const chrome = findChrome();
  if (!chrome) { console.error("No Chrome/Chromium found — set CHROME_PATH"); process.exit(2); }
  const silence = console.log; console.log = () => { };
  require("../server.js");
  const connect = require("../lib/connect.js");
  const db = require("../lib/db.js");
  console.log = silence;
  connect.__setTransport(fakeEasyPost);
  for (let i = 0; i < 120; i++) { try { if ((await fetch(BASE + "/healthz")).ok) break; } catch (e) { } await sleep(250); }

  const profile = fs.mkdtempSync(path.join(os.tmpdir(), "luxora-chrome-"));
  const br = spawn(chrome, ["--headless=new", "--remote-debugging-port=0", "--user-data-dir=" + profile, "--no-first-run", "--no-default-browser-check", "--disable-gpu", "--disable-extensions", ...(process.getuid && process.getuid() === 0 ? ["--no-sandbox"] : []), "about:blank"], { stdio: "ignore" });
  let port = null;
  for (let i = 0; i < 100 && !port; i++) { try { port = fs.readFileSync(path.join(profile, "DevToolsActivePort"), "utf8").split("\n")[0]; } catch (e) { await sleep(100); } }

  /* a signed-in tab in its own browser context; confirm() dialogs are accepted */
  async function signedIn(login, cred) {
    const ctx = await fetch(`http://127.0.0.1:${port}/json/version`).then(r => r.json());
    const browser = await Tab.open(ctx.webSocketDebuggerUrl);
    const { browserContextId } = await browser.send("Target.createBrowserContext");
    const { targetId } = await browser.send("Target.createTarget", { url: "about:blank", browserContextId });
    const list = await fetch(`http://127.0.0.1:${port}/json/list`).then(r => r.json());
    const tab = await Tab.open(list.find(t => t.id === targetId).webSocketDebuggerUrl);
    for (const d of ["Runtime", "Log", "Page", "Network"]) await tab.send(d + ".enable");
    tab.listeners.push(d => { if (d.method === "Page.javascriptDialogOpening") tab.send("Page.handleJavaScriptDialog", { accept: true }).catch(() => { }); });
    await tab.send("Page.navigate", { url: BASE + "/index.html?store=luxora" }); await tab.once("Page.loadEventFired", 15000); await sleep(600);
    const st = await tab.eval(`(async () => { const c = (document.cookie.match(/(?:^|; )azc=([^;]+)/) || [])[1] || ""; return (await fetch(${JSON.stringify(login)}, { method: "POST", headers: { "Content-Type": "application/json", "x-csrf": c }, body: JSON.stringify(${JSON.stringify(cred)}) })).status; })()`);
    tab.done = async () => { tab.close(); await browser.send("Target.disposeBrowserContext", { browserContextId }).catch(() => { }); browser.close(); };
    return { tab, st };
  }
  const until = async (tab, expr, ms) => { for (let i = 0; i < (ms || 8000) / 150; i++) { const v = await tab.eval(expr).catch(() => null); if (v) return v; await sleep(150); } return null; };
  const open = async (tab, page, view) => {
    await tab.send("Page.navigate", { url: BASE + page }); await tab.once("Page.loadEventFired", 15000);
    await until(tab, `!!document.querySelector('.p-nav button[data-v="${view}"]')`);
    await tab.eval(`document.querySelector('.p-nav button[data-v="${view}"]').click()`);
  };
  const type = (tab, sel, v) => tab.eval(`(() => { const i = document.querySelector(${JSON.stringify(sel)}); i.value = ${JSON.stringify(v)}; i.dispatchEvent(new Event("input", { bubbles: true })); return true; })()`);
  const click = (tab, sel) => tab.eval(`(() => { const b = document.querySelector(${JSON.stringify(sel)}); if (b) b.click(); return !!b; })()`);
  const ep = () => db.get("SELECT status, config FROM shipping_providers WHERE provider_id='easypost'");

  try {
    console.log("▸ THE PLATFORM ADMIN CONNECTS EASYPOST");
    const P = await signedIn("/api/platform/login", { email: "platform@luxora.shop", password: "platform123" });
    ok(P.st === 200, "platform admin signs in");
    P.tab.events = [];
    await open(P.tab, "/platform.html", "providers");
    ok(await until(P.tab, `!!document.querySelector("#carrierAccounts #epKey")`), "Provider Registry shows the EasyPost carrier account");
    ok(/not connected/.test(await P.tab.eval(`document.querySelector("#carrierAccounts h2").innerText`)), "it starts out not connected");
    ok(/\/api\/shipping\/webhook\/easypost$/.test(await P.tab.eval(`document.querySelector("#epHook").value`)), "the webhook URL to paste into EasyPost is shown");
    await type(P.tab, "#epKey", "EZTK_ui_test_key"); await type(P.tab, "#epSecret", "ui_whsec");
    await click(P.tab, "#epSave");
    ok(await until(P.tab, `/\\bconnected\\b/.test(document.querySelector("#carrierAccounts h2")?.innerText || "") && !/not connected/.test(document.querySelector("#carrierAccounts h2").innerText)`), "Save connects it and the screen says so");
    const row = ep();
    ok(row.status === "active" && !row.config.includes("EZTK_ui_test_key") && !row.config.includes("ui_whsec"), "the key and secret are stored sealed", row);
    ok(!(await P.tab.eval("document.documentElement.outerHTML")).includes("EZTK_ui_test_key"), "the key never comes back into the page");
    ok((await P.tab.eval(`document.querySelectorAll("#carrierAccounts .badge.active").length`)) >= 3, "both credentials show as on file");
    const pIssues = problems(P.tab.events);
    ok(!pIssues.length, "no browser errors on the platform screen", pIssues);

    console.log("▸ THE STORE ADMIN SETS THE SHIP-FROM ADDRESS");
    const S = await signedIn("/api/auth/login?store=luxora", { email: "admin@luxora.shop", password: "admin123" });
    ok(S.st === 200, "store admin signs in");
    S.tab.events = [];
    await open(S.tab, "/admin.html", "shipping");
    ok(await until(S.tab, `/connected/.test(document.querySelector("#shippingProviders")?.innerText || "")`), "Shipping & Tracking shows the carrier as connected");
    ok(await until(S.tab, `!!document.querySelector("#sfSave")`), "the ship-from form is shown");
    await type(S.tab, '[data-sf="street1"]', "400 Pine St");
    await click(S.tab, "#sfSave");
    await sleep(800);
    ok(!(db.get("SELECT value FROM settings WHERE tenant_id=1 AND key='commerce'") || { value: "" }).value.includes("400 Pine St"), "an incomplete address is not saved");
    for (const [k, v] of [["name", "LUXORA Warehouse"], ["city", "Seattle"], ["state", "WA"], ["zip", "98101"], ["country", "US"]]) await type(S.tab, `[data-sf="${k}"]`, v);
    await click(S.tab, "#sfSave");
    const saved = await (async () => { for (let i = 0; i < 40; i++) { const r = db.get("SELECT value FROM settings WHERE tenant_id=1 AND key='commerce'"); const sf = r && JSON.parse(r.value).shipFrom; if (sf && sf.zip === "98101") return sf; await sleep(150); } return null; })();
    ok(saved && saved.street1 === "400 Pine St" && saved.city === "Seattle" && saved.country === "US", "a complete address is saved", saved);
    ok(await until(S.tab, `!!document.querySelector("#sfClear")`), "the form reloads with the saved address");

    console.log("▸ THE STORE ADMIN SHIPS AN ORDER");
    /* a cash-on-delivery order, placed the way a shopper would */
    const order = await S.tab.eval(`(async () => {
      const c = () => (document.cookie.match(/(?:^|; )azc=([^;]+)/) || [])[1] || "";
      const call = (p, m, b) => fetch(p, { method: m, headers: { "Content-Type": "application/json", "x-csrf": c() }, body: b ? JSON.stringify(b) : undefined }).then(r => r.json());
      await call("/api/admin/gateways?store=luxora", "PUT", { gateways: [{ id: "cod", enabled: true, primary: true, mode: "sandbox", config: {} }] });
      const p = (await fetch("/api/products?limit=5&store=luxora").then(r => r.json())).items.find(x => x.st > 2);
      await call("/api/cart?store=luxora", "POST", { id: p.id, qty: 1 });
      const co = await call("/api/checkout?store=luxora", "POST", { name: "Sam Shopper", address: "1 Main St", city: "Portland", state: "OR", zip: "97201", gateway: "cod", carrier: "house-std" });
      return co.order || co;
    })()`);
    const o = order && order.num && db.get("SELECT id, num, status FROM orders WHERE num=?", order.num);
    ok(o && o.status === "processing", "a paid order is waiting to ship", o || order);
    S.tab.events = [];
    await open(S.tab, "/admin.html", "orders");
    const shipBtn = `[data-act="ship-order"][data-id="${o && o.id}"]`;
    ok(await until(S.tab, `!!document.querySelector('${shipBtn}')`), "the order has a Ship button");
    await click(S.tab, shipBtn);
    ok(await until(S.tab, `!!document.querySelector("#shW")`), "Ship opens the parcel form");
    await click(S.tab, "#shRate");
    await sleep(300);
    ok(!(await S.tab.eval(`!!document.querySelector("[data-buy]")`)), "rates are not requested without a weight");
    await type(S.tab, "#shW", "18");
    await click(S.tab, "#shRate");
    ok(await until(S.tab, `document.querySelectorAll("[data-buy]").length === 2`), "both carrier rates are listed");
    ok(/USPS/.test(await S.tab.eval(`document.querySelector("#shRates tbody tr").innerText`)), "the cheapest rate is first");
    await click(S.tab, '[data-buy="rate_usps"]');
    ok(await until(S.tab, `/Label bought/.test(document.querySelector("#shipBody")?.innerText || "")`), "Buy label shows the label was bought");
    ok(bought.length === 1 && bought[0] === "rate_usps", "exactly the chosen rate was bought", bought);
    ok(await S.tab.eval(`document.querySelector('#shipBody a[href="https://easypost-files.s3.amazonaws.com/ui-label.png"]') !== null`), "the label can be printed from the confirmation");
    ok(db.get("SELECT status FROM orders WHERE id=?", o.id).status === "shipped", "the order is now shipped");
    await S.tab.eval(`document.querySelector("#modal").innerHTML = ""`);
    ok(await until(S.tab, `/Label/.test(document.querySelector('${shipBtn}')?.innerText || "")`), "the order's button becomes Label once shipped");
    await click(S.tab, shipBtn);
    ok(await until(S.tab, `/already has a label/.test(document.querySelector("#shipBody")?.innerText || "") && /9400100000000000000001/.test(document.querySelector("#shipBody").innerText)`), "reopening it shows the existing label first");
    const sIssues = problems(S.tab.events);
    ok(!sIssues.length, "no browser errors on the store screens", sIssues);
    await S.tab.done();

    console.log("▸ THE PLATFORM ADMIN DISCONNECTS EASYPOST");
    P.tab.events = [];
    await open(P.tab, "/platform.html", "providers");
    await until(P.tab, `!!document.querySelector("#epDisconnect")`);
    await click(P.tab, "#epDisconnect");
    ok(await until(P.tab, `/not connected/.test(document.querySelector("#carrierAccounts h2")?.innerText || "")`), "Disconnect returns the screen to not connected");
    ok(ep().status === "inactive" && ep().config === "{}", "the stored keys are deleted", ep());
    const dIssues = problems(P.tab.events);
    ok(!dIssues.length, "no browser errors while disconnecting", dIssues);
    await P.tab.done();
  } catch (e) {
    failed++; console.error("  ✗ harness error:", e && e.stack || e);
  } finally {
    try { br.kill(); } catch (e) { }
    await sleep(300);
    try { fs.rmSync(profile, { recursive: true, force: true }); } catch (e) { }
    for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
  }
  console.log(`\n${passed} passed, ${failed} failed`);
  process.exit(failed ? 1 : 0);
})();
