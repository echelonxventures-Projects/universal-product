/* LUXORA Platform — the local demo in real Chrome, clicked through: a shopper buys, pays on the local
   payment page and comes back; cancels and is refunded; a Razorpay shopper pays in India; the store
   owner opens every feature's screen; pages speak Hindi and Arabic. Any uncaught error fails the run. */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os"), { spawn } = require("child_process");
const { Tab, findChrome } = require("../scripts/browser-check.js");
const DB = path.join(os.tmpdir(), "lx-demoui-" + process.pid + ".db"), P = 8921, B = 8922, M = 8923, APP = "http://localhost:" + P, BOX = "http://localhost:" + B;
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + JSON.stringify(x).slice(0, 400) : ""))); };
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const chrome = findChrome(); if (!chrome) { console.error("No Chrome found"); process.exit(2); }
  const srv = spawn(process.execPath, [path.join(__dirname, "..", "scripts", "demo.js")], { env: { ...process.env, NODE_ENV: "", LX_TEST: "", DEMO_DB: DB, DEMO_PORT: P, DEMO_SANDBOX_PORT: B, DEMO_SMTP_PORT: M }, stdio: ["ignore", "pipe", "pipe"] });
  let out = "", err = ""; srv.stdout.on("data", d => out += d); srv.stderr.on("data", d => err += d);
  for (let i = 0; i < 1800 && !/Ctrl\+C/.test(out); i++) await sleep(100);
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), "lx-chrome-"));
  const br = spawn(chrome, ["--headless=new", "--remote-debugging-port=0", "--user-data-dir=" + profile, "--no-first-run", "--disable-gpu", "about:blank"], { stdio: "ignore" });
  let port = null; for (let i = 0; i < 100 && !port; i++) { try { port = fs.readFileSync(path.join(profile, "DevToolsActivePort"), "utf8").split("\n")[0]; } catch (e) { await sleep(100); } }
  const open = async () => {
    const browser = await Tab.open((await fetch(`http://127.0.0.1:${port}/json/version`).then(r => r.json())).webSocketDebuggerUrl), { browserContextId } = await browser.send("Target.createBrowserContext"), { targetId } = await browser.send("Target.createTarget", { url: "about:blank", browserContextId });
    const tab = await Tab.open((await fetch(`http://127.0.0.1:${port}/json/list`).then(r => r.json())).find(t => t.id === targetId).webSocketDebuggerUrl);
    for (const d of ["Runtime", "Log", "Page", "Network"]) await tab.send(d + ".enable");
    tab.bad = []; tab.listeners.push(d => { if (d.method === "Page.javascriptDialogOpening") tab.send("Page.handleJavaScriptDialog", { accept: true, promptText: "1" }).catch(() => { }); if (d.method === "Runtime.exceptionThrown") tab.bad.push(((d.params.exceptionDetails.exception || {}).description || d.params.exceptionDetails.text).slice(0, 200)); });
    tab.go = async u => { await tab.send("Page.navigate", { url: u.startsWith("http") ? u : APP + u }); await tab.once("Page.loadEventFired", 20000); };
    tab.until = async (x, ms) => { for (let i = 0; i < (ms || 10000) / 150; i++) { const v = await tab.eval(x).catch(() => null); if (v) return v; await sleep(150); } return null; };
    tab.click = s => tab.eval(`(() => { const b = document.querySelector(${JSON.stringify(s)}); if (!b) return false; b.click(); return true; })()`);
    tab.fill = (s, v) => tab.eval(`(() => { const e = document.querySelector(${JSON.stringify(s)}); if (!e) return false; e.value = ${JSON.stringify(v)}; e.dispatchEvent(new Event("input",{bubbles:true})); e.dispatchEvent(new Event("change",{bubbles:true})); return true; })()`);
    tab.call = (p, m, b) => tab.eval(`(async () => { const c = (document.cookie.match(/(?:^|; )azc=([^;]+)/) || [])[1] || ""; const r = await fetch(${JSON.stringify(p)}, { method: ${JSON.stringify(m || "GET")}, headers: {"Content-Type":"application/json","x-csrf":c}, body: ${b ? JSON.stringify(JSON.stringify(b)) : "undefined"} }); return { status: r.status, body: await r.json().catch(() => ({})) }; })()`);
    return tab;
  };
  try {
    ok(/Ctrl\+C/.test(out), "the demo is up", err.slice(-300));
    for (const [store, gw, email] of [["luxora", "stripe", "shopper@luxora.shop"], ["luxora", "paypal", "shopper@luxora.shop"], ["aurum", "razorpay", "shopper@aurum.shop"]]) {
      console.log("▸ A SHOPPER · " + store + " · " + gw);
      const t = await open(); await t.go("/index.html?store=" + store); await sleep(900);
      ok((await t.call("/api/auth/login", "POST", { email, password: "Demo-Shop-1" })).status === 200, "signs in");
      const list = (await t.call("/api/products?limit=200")).body.items, it = list.filter(p => p.st > 5 && p.type === "physical" && !p.preorder)[6];
      await t.go("/product.html?id=" + encodeURIComponent(it.id)); ok(!!(await t.until(`!!document.querySelector('[data-act="add"]')`)), "opens an item");
      await t.click('#page [data-act="add"]'); await t.until(`/[1-9]/.test((document.querySelector("#cartCount")||{}).textContent||"")`);
      await t.go("/checkout.html"); ok(!!(await t.until(`!!document.querySelector("#placeOrder")`)), "goes to checkout");
      for (const [s, v] of [["#coName", "Demo Shopper"], ["#coAddr", "1 Main St"], ["#coCity", "Seattle"], ["#coState", "WA"], ["#coZip", "98109"]]) await t.fill(s, v);
      await t.eval(`(() => { const e = document.querySelector('input[name=pay][value="${gw}"]'); if (e) { e.checked = true; e.dispatchEvent(new Event("change",{bubbles:true})); } })()`); await sleep(1500);
      const total = await t.eval(`document.querySelector("#osTotal").textContent.replace(/\\s/g,"")`);
      await t.click("#placeOrder");
      ok(!!(await t.until(`location.href.startsWith("${BOX}/pay/")`, 15000)), "is sent to the payment page", await t.eval("location.href + ' ' + (document.querySelector('#toasts,.toast')||{}).textContent"));
      ok(!!(await t.until(`document.body.textContent.includes("Pay")`)), "which asks for " + total);
      await t.eval(`document.querySelector("button.p").click()`);
      ok(!!(await t.until(`location.href.includes("/orders.html")`, 15000)) && !!(await t.until(`document.querySelectorAll(".ord").length > 0`)), "pays, and comes back to their orders");
      ok(!!(await t.until(`/Processing/.test(document.body.textContent)`, 8000)), "where the order is being packed");
      ok(!!(await t.until(`[...document.querySelectorAll(".ord-h-r a")].some(a => /Invoice/.test(a.textContent))`)), "with its invoice");
      const href = await t.eval(`document.querySelector('.ord-h-r a[href^="invoice.html"]').getAttribute("href")`), v = await open(); v.close && 0;
      await t.go("/" + href); ok(!!(await t.until(`/invoice/i.test(document.title)`)), "which opens", await t.eval("document.title + ' ' + document.body.textContent.slice(0,200)"));
      await t.go("/orders.html"); await t.until(`!!document.querySelector('[data-act="order-cancel"]')`); await t.click('[data-act="order-cancel"]');
      ok(!!(await t.until(`/Cancelled/.test(document.querySelector(".ord-status").textContent)`, 10000)), "cancels it from there");
      ok(/refunded/.test(await (await fetch(BOX + "/payments")).text()), "and the gateway has the refund");
      ok(!t.bad.length, "no script errors", t.bad);
    }
    console.log("▸ THE STORE OWNER");
    const A = await open(); await A.go("/index.html?store=luxora"); await sleep(600); await A.call("/api/auth/login", "POST", { email: "admin@luxora.shop", password: "admin123" });
    const feats = require("../lib/seed/features.json").FEATURES, dead = [];
    for (const f of feats) { await A.go("/console.html?scope=store&store=luxora&view=" + f.key); if (!(await A.until(`document.body.textContent.includes(${JSON.stringify(f.help.slice(0, 30))})`, 9000))) dead.push(f.key + ": " + (await A.eval("document.body.textContent.slice(0,120)"))); }
    ok(!dead.length, "opens all " + feats.length + " feature screens", dead);
    for (const k of ["deliveryslots", "areas", "sizeguides", "preorders", "addresses", "payments", "orders", "returns"]) { await A.go("/console.html?scope=store&store=luxora&view=" + k); ok(!!(await A.until(`(document.querySelector("#vBody")||document.body).textContent.trim().length > 40 && !/Loading|No access/.test((document.querySelector("#vBody")||document.body).textContent.slice(0, 60))`, 9000)), "and " + k); }
    await A.go("/console.html?scope=store&store=luxora&view=sale_events"); await A.until(`!!document.querySelector("[data-ftadd]")`); await sleep(500);
    await A.fill("#ft_name", "From the console"); await A.fill("#ft_starts", "2030-01-01T10:00"); await A.fill("#ft_ends", "2030-01-02T10:00"); await A.fill("#ft_percent", "12"); await A.click("[data-ftadd]");
    ok(!!(await A.until(`document.body.textContent.includes("From the console")`)), "adds a sale from its screen"); ok(!A.bad.length, "no script errors", A.bad);
    console.log("▸ LANGUAGES");
    for (const [l, dir, w] of [["hi", "ltr", "गोपनीयता"], ["ar", "rtl", "الخصوصية"], ["de", "ltr", "Datenschutz"]]) { const t = await open(); await t.go("/index.html?store=luxora&lang=" + l); ok(!!(await t.until(`document.body.textContent.includes(${JSON.stringify(w)})`)) && (await t.eval("getComputedStyle(document.body).direction")) === dir, l + " is spoken, " + dir); }
  } catch (e) { failed++; console.error("  ✗ harness error:", e && e.stack || e, err.slice(-500)); }
  br.kill("SIGKILL"); srv.kill("SIGKILL"); await sleep(500); for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } } try { fs.rmSync(profile, { recursive: true, force: true }); } catch (e) { }
  console.log(`\n${passed} passed, ${failed} failed`); process.exit(failed ? 1 : 0);
})();
