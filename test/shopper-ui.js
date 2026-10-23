/* LUXORA Platform — the shopper and brand atoms clicked through in real Chrome, under the
   production CSP: a shopper adds a product to a list and sets a price alert from the product
   page (which shows the brand's rich content and its registered-brand badge), sees a
   sponsored result in search, manages the list, and checks out to a pickup locker and gets a
   code; staff open the Pickup Points, Rich Content, Brand Registry and Ads screens. Any
   uncaught exception, console error, CSP violation or failed load fails the run. */
"use strict";
const path = require("path");
const fs = require("fs");
const os = require("os");
const { spawn } = require("child_process");
const { Tab, findChrome, problems } = require("../scripts/browser-check.js");
const DB = path.join(__dirname, "shopper-ui.db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
const PORT = 8888;
Object.assign(process.env, { LX_DB: DB, PORT: String(PORT), LX_LOG: "", LX_OFFLINE: "1" });
delete process.env.NODE_ENV;
const BASE = `http://localhost:${PORT}`;
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const chrome = findChrome();
  if (!chrome) { console.error("No Chrome/Chromium found — set CHROME_PATH"); process.exit(2); }
  const silence = console.log; console.log = () => { };
  require("../server.js");
  console.log = silence;
  for (let i = 0; i < 120; i++) { try { if ((await fetch(BASE + "/healthz")).ok) break; } catch (e) { } await sleep(250); }
  const db = require("../lib/db.js");

  const profile = fs.mkdtempSync(path.join(os.tmpdir(), "luxora-chrome-"));
  const br = spawn(chrome, ["--headless=new", "--remote-debugging-port=0", "--user-data-dir=" + profile, "--no-first-run", "--no-default-browser-check", "--disable-gpu", "--disable-extensions", ...(process.getuid && process.getuid() === 0 ? ["--no-sandbox"] : []), "about:blank"], { stdio: "ignore" });
  let port = null;
  for (let i = 0; i < 100 && !port; i++) { try { port = fs.readFileSync(path.join(profile, "DevToolsActivePort"), "utf8").split("\n")[0]; } catch (e) { await sleep(100); } }

  async function signedIn(login, cred) {
    const ctx = await fetch(`http://127.0.0.1:${port}/json/version`).then(r => r.json());
    const browser = await Tab.open(ctx.webSocketDebuggerUrl);
    const { browserContextId } = await browser.send("Target.createBrowserContext");
    const { targetId } = await browser.send("Target.createTarget", { url: "about:blank", browserContextId });
    const list = await fetch(`http://127.0.0.1:${port}/json/list`).then(r => r.json());
    const tab = await Tab.open(list.find(t => t.id === targetId).webSocketDebuggerUrl);
    for (const d of ["Runtime", "Log", "Page", "Network"]) await tab.send(d + ".enable");
    tab.listeners.push(d => { if (d.method === "Page.javascriptDialogOpening") tab.send("Page.handleJavaScriptDialog", { accept: true, promptText: "" }).catch(() => { }); });
    await tab.send("Page.navigate", { url: BASE + "/index.html?store=luxora" }); await tab.once("Page.loadEventFired", 15000); await sleep(600);
    const call = (p, m, b) => tab.eval(`(async () => { const c = (document.cookie.match(/(?:^|; )azc=([^;]+)/) || [])[1] || ""; const r = await fetch(${JSON.stringify(p)}, { method: ${JSON.stringify(m || "GET")}, headers: { "Content-Type": "application/json", "x-csrf": c }, body: ${b ? JSON.stringify(JSON.stringify(b)) : "undefined"} }); return { status: r.status, body: await r.json().catch(() => null) }; })()`);
    const st = (await call(login, "POST", cred)).status;
    tab.call = call;
    tab.done = async () => { tab.close(); await browser.send("Target.disposeBrowserContext", { browserContextId }).catch(() => { }); browser.close(); };
    return { tab, st };
  }
  const until = async (tab, expr, ms) => { for (let i = 0; i < (ms || 8000) / 150; i++) { const v = await tab.eval(expr).catch(() => null); if (v) return v; await sleep(150); } return null; };
  const go = async (tab, url) => { await tab.send("Page.navigate", { url: BASE + url }); await tab.once("Page.loadEventFired", 15000); };
  const click = (tab, sel) => tab.eval(`(() => { const b = document.querySelector(${JSON.stringify(sel)}); if (!b) return false; b.click(); return true; })()`);
  const set = (tab, sel, v) => tab.eval(`(() => { const e = document.querySelector(${JSON.stringify(sel)}); if (!e) return false; e.value = ${JSON.stringify(v)}; e.dispatchEvent(new Event("input", { bubbles: true })); e.dispatchEvent(new Event("change", { bubbles: true })); return true; })()`);

  try {
    console.log("▸ STAFF SWITCH THE ATOMS ON AND SET UP");
    const A = await signedIn("/api/auth/login?store=luxora", { email: "admin@luxora.shop", password: "admin123" });
    ok(A.st === 200, "store admin signs in");
    A.tab.events = [];
    for (const k of ["wish_lists", "product_alerts", "pickup_points", "rich_content", "brand_registry", "sponsored_ads"])
      ok((await A.tab.call("/api/capabilities/enable", "POST", { capability: k })).status === 200, "switches on " + k);
    const prod = db.get("SELECT p.id, p.title, b.key brand FROM products p JOIN brands b ON b.tenant_id=p.tenant_id AND (b.key=p.brand OR lower(b.label)=lower(p.brand)) WHERE p.tenant_id=1 AND p.lifecycle='published' AND p.deleted_at IS NULL AND p.stock > 5 ORDER BY p.id LIMIT 1");
    const pt = await A.tab.call("/api/admin/pickup/points", "POST", { code: "station", name: "Station Locker", kind: "locker", address: "1 Station Rd", city: "Springfield", postcode: "12345", hours: "24/7" });
    ok(pt.status === 200, "a locker is added", pt.body);
    const rc = await A.tab.call("/api/admin/rich-content", "POST", { product_id: prod.id, modules: [{ kind: "feature_list", headline: "Why it's different", items: "Hand finished\nTen-year warranty" }, { kind: "comparison", rows: "Model | Weight\nThis one | 1.2 kg\nOld one | 1.9 kg" }] });
    await A.tab.call(`/api/admin/rich-content/${rc.body.content.id}`, "POST", { action: "submit" });
    ok((await A.tab.call(`/api/admin/rich-content/${rc.body.content.id}`, "POST", { action: "approve" })).status === 200, "brand content is approved");
    const cl = await A.tab.call("/api/admin/brand-registry/claims", "POST", { brand: prod.brand, trademark_number: "TM-1" });
    ok((await A.tab.call(`/api/admin/brand-registry/claims/${cl.body.claim.id}`, "POST", { action: "approve" })).status === 200, "the brand is registered");
    ok((await A.tab.call("/api/admin/marketplace/ads", "POST", { name: "UI ad", bid_model: "cpc", bid_amount: 1, target: { keywords: ["zephyr"], product_id: prod.id } })).status === 200, "a keyword ad is created");

    console.log("▸ THE CONSOLE SCREENS");
    for (const [v, re] of [["pickup", /Station Locker/], ["richcontent", /Why it|Feature list/], ["brandreg", /TM-1/], ["marketplace", /New sponsored product/]]) {
      await go(A.tab, "/console.html?scope=store&view=" + v);
      ok(!!(await until(A.tab, `${re}.test(document.querySelector("#vBody")?.innerText || "")`)), "the " + v + " screen renders its records");
    }
    await go(A.tab, "/console.html?scope=store&view=richcontent");
    await until(A.tab, `!!document.querySelector("#rcKind")`);
    await click(A.tab, "#rcAdd");
    ok(!!(await until(A.tab, `document.querySelectorAll("[data-rc-mod] [data-f]").length > 0`)), "adding a module draws an input for each field its registry row declares");
    const aIssues = problems(A.tab.events);
    ok(!aIssues.length, "no browser errors in the console", aIssues);

    console.log("▸ A SHOPPER: PRODUCT PAGE, LISTS AND ALERTS");
    const S = await signedIn("/api/auth/register?store=luxora", { name: "Ula Shopper", email: "ula@example.com", password: "Correct-Horse-Ula-9" });
    ok(S.st === 200, "a shopper registers");
    S.tab.events = [];
    await go(S.tab, "/product.html?id=" + encodeURIComponent(prod.id));
    ok(!!(await until(S.tab, `!!document.querySelector(".rc .rc-table th") && /Ten-year warranty/.test(document.querySelector(".rc").innerText)`)), "the product page shows the brand's content, the comparison with its header row");
    ok(!!(await S.tab.eval(`!!document.querySelector(".pp-regbrand")`)), "and the registered-brand badge");
    await click(S.tab, "[data-act='lst-add']");
    ok(!!(await until(S.tab, `!document.querySelector("#dynModal").classList.contains("hidden") && !!document.querySelector("#lpSave")`)), "Add to List opens the list picker");
    await set(S.tab, "#lpName", "Birthday");
    await click(S.tab, "#lpSave");
    ok(!!(await until(S.tab, `/In Birthday/.test(document.querySelector(".buybox")?.innerText || "")`)), "a new list is made and the page says the product is in it");
    await click(S.tab, "[data-act='alert-open']");
    ok(!!(await until(S.tab, `!!document.querySelector("#alSave")`)), "Price alert opens the alert picker with the kinds available");
    await click(S.tab, "#alSave");
    ok(!!(await until(S.tab, `/1 alert on this item/.test(document.querySelector(".buybox")?.innerText || "")`)), "the alert is set");
    await go(S.tab, "/registry.html");
    ok(!!(await until(S.tab, `/Birthday/.test(document.querySelector(".lst-head")?.innerText || "") && !!document.querySelector(".lst-item") && !!document.querySelector("#alerts tbody tr")`)), "the lists page shows the list, its item and the alert");
    await S.tab.eval(`(() => { const s = document.querySelector("[data-lx=prio]"); s.value = s.options[s.options.length - 1].value; s.dispatchEvent(new Event("change", { bubbles: true })); })()`);
    ok(!!(await until(S.tab, `(() => { const s = document.querySelector("[data-lx=prio]"); return s && s.selectedIndex === s.options.length - 1; })()`)), "changing an item's priority saves it");

    console.log("▸ SPONSORED RESULTS");
    await go(S.tab, "/results.html?q=zephyr");
    ok(!!(await until(S.tab, `!!document.querySelector(".r-sponsored .sp-card .sp-tag") && /Sponsored/.test(document.querySelector(".r-sponsored").innerText)`)), "a search naming the ad's keyword shows a labelled sponsored product");

    console.log("▸ CHECKOUT TO A PICKUP LOCKER");
    await S.tab.call("/api/cart", "POST", { id: prod.id, qty: 1 });
    await go(S.tab, "/checkout.html");
    await until(S.tab, `!!document.querySelector("input[name=coMode][value='1']")`);
    await click(S.tab, "input[name=coMode][value='1']");
    ok(!!(await until(S.tab, `!!document.querySelector("input[name=coPk]:checked") && /Station Locker/.test(document.querySelector("#coRates")?.innerText || "")`)), "choosing a pickup point lists the locker and the summary collects from it");
    ok(await S.tab.eval(`document.querySelector("#coAddr").hidden && !document.querySelector("#coAddr").required`), "the address is no longer asked for");
    await S.tab.eval(`(() => { const r = [...document.querySelectorAll("input[name=pay]")].find(x => /cod/i.test(x.value)) || document.querySelector("input[name=pay]"); r.checked = true; })()`);
    await click(S.tab, "#placeOrder");
    ok(!!(await until(S.tab, `/Your pickup code/.test(document.querySelector(".oco")?.innerText || "") && /^\\d{6}$/.test(document.querySelector(".oco .pk-code")?.innerText || "")`, 15000)), "the confirmation gives a 6-digit pickup code");
    await go(S.tab, "/orders.html");
    ok(!!(await until(S.tab, `/Station Locker/.test(document.querySelector(".ord-pk")?.innerText || "") && !!document.querySelector(".ord-pk .pk-code")`)), "Your Orders shows the locker and the code");

    console.log("▸ PLATFORM-TYPE PANELS: OPTIONS, BOOKINGS, SELLING, MESSAGES");
    for (const k of ["product_options", "bookings", "peer_listings", "conversations", "price_negotiation"])
      ok((await A.tab.call("/api/capabilities/enable", "POST", { capability: k })).status === 200, "switches on " + k);
    const [po, pb] = db.all("SELECT id FROM products WHERE tenant_id=1 AND lifecycle='published' AND deleted_at IS NULL AND stock > 5 AND id<>? ORDER BY id LIMIT 2", prod.id);
    const og = await A.tab.call("/api/admin/options", "POST", { code: "size", name: "Size", kind: "choice", min_select: 1, max_select: 1, values: [{ code: "s", name: "Small" }, { code: "l", name: "Large", price_delta: 5 }] });
    await A.tab.call(`/api/admin/options/products/${encodeURIComponent(po.id)}`, "PUT", { groups: [og.body.group.id] });
    const allWeek = Object.fromEntries([0, 1, 2, 3, 4, 5, 6].map(d => [String(d), [["08:00", "20:00"]]]));
    const res = await A.tab.call("/api/admin/bookings/resources", "POST", { code: "chair-1", name: "Chair One", kind: "staff", tz: "UTC", hours: allWeek });
    ok((await A.tab.call(`/api/admin/bookings/products/${encodeURIComponent(pb.id)}`, "PUT", { mode: "timed", resource_ids: [res.body.resource.id], duration_min: 60, step_min: 60 })).status === 200, "a product is made bookable");
    await go(S.tab, "/product.html?id=" + encodeURIComponent(po.id));
    ok(!!(await until(S.tab, `!!document.querySelector("#ppOptions input[value='l']")`)), "the product page offers its options");
    await S.tab.eval(`document.querySelector("#ppOptions input[value='l']").click()`);
    await click(S.tab, "#bbAdd");
    await go(S.tab, "/cart.html");
    ok(!!(await until(S.tab, `/Size: Large/.test(document.querySelector(".cart-main")?.innerText || "")`)), "the bag line shows the chosen option");
    await go(S.tab, "/product.html?id=" + encodeURIComponent(pb.id));
    ok(!!(await until(S.tab, `!!document.querySelector("#bkFind") && document.querySelector("#bbAdd")?.hidden !== false`)), "a bookable product asks for a time instead of Add to bag");
    await set(S.tab, "#bkDate", new Date(Date.now() + 2 * 864e5).toISOString().slice(0, 10));
    await click(S.tab, "#bkFind");
    ok(!!(await until(S.tab, `document.querySelectorAll(".ppx-slot").length >= 10`)), "it shows the free times that day");
    await click(S.tab, ".ppx-slot");
    ok(!!(await until(S.tab, `/held for you/.test(document.querySelector("#toast")?.innerText || "")`)), "choosing one holds it and puts it in the bag");
    await go(S.tab, "/sell.html");
    ok(!!(await until(S.tab, `!!document.querySelector("#slCreate")`)), "the selling page opens");
    await set(S.tab, "#slTitle", "Old bicycle"); await set(S.tab, "#slPrice", "40");
    await click(S.tab, "#slCreate");
    ok(!!(await until(S.tab, `/Old bicycle/.test(document.querySelector(".lst-main")?.innerText || "")`)), "a listing is drafted from the page");
    await go(S.tab, "/product.html?id=" + encodeURIComponent(po.id));
    await until(S.tab, `!!document.querySelector("[data-act='msg-open']")`);
    await click(S.tab, "[data-act='msg-open']");
    await until(S.tab, `!!document.querySelector("#msgSend")`);
    await set(S.tab, "#msgBody", "Is it in stock in Large?");
    await click(S.tab, "#msgSend");
    await go(S.tab, "/messages.html");
    ok(!!(await until(S.tab, `/in stock in Large/.test(document.querySelector(".msg-thread")?.innerText || "")`)), "the messages page shows the conversation");
    for (const [v, re] of [["prodoptions", /Size/], ["bookings", /Chair One/], ["listings", /Old bicycle|No listings/], ["conversations", /in stock|No conversations|Messages/]]) {
      await go(A.tab, "/console.html?scope=store&view=" + v);
      ok(!!(await until(A.tab, `${re}.test(document.querySelector("#vBody")?.innerText || "")`)), "the " + v + " console screen renders");
    }
    const aIssues2 = problems(A.tab.events);
    ok(!aIssues2.length, "no browser errors on the new console screens", aIssues2);
    const sIssues = problems(S.tab.events);
    ok(!sIssues.length, "no browser errors on the storefront", sIssues);

    await A.tab.done(); await S.tab.done();
  } catch (e) { failed++; console.log("  ✗ threw: " + (e && e.stack || e)); }
  finally {
    try { br.kill(); } catch (e) { }
    try { fs.rmSync(profile, { recursive: true, force: true }); } catch (e) { }
  }
  console.log(`\n${passed} passed, ${failed} failed`);
  for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
  process.exit(failed ? 1 : 0);
})();
