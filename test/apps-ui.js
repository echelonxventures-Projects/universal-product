/* LUXORA Platform — configured apps in the one console, clicked through in real Chrome.
   The platform composes an application; the owner finds it in the console's own menu at
   once, opens it, and the address bar keeps the screen across a reload. The store owner
   sees it too, and the Team & Roles editor names it so it can be granted; a staff member
   without the grant never sees it. The old addresses land in the console. */
"use strict";
const path = require("path");
const fs = require("fs");
const os = require("os");
const { spawn } = require("child_process");
const { Tab, findChrome, problems } = require("../scripts/browser-check.js");
const DB = path.join(__dirname, "apps-ui.db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
const PORT = 8881;
Object.assign(process.env, { LX_DB: DB, PORT: String(PORT), LX_LOG: "" });
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
    tab.listeners.push(d => { if (d.method === "Page.javascriptDialogOpening") tab.send("Page.handleJavaScriptDialog", { accept: true }).catch(() => { }); });
    await tab.send("Page.navigate", { url: BASE + "/index.html?store=luxora" }); await tab.once("Page.loadEventFired", 15000); await sleep(600);
    const call = (p, m, b) => tab.eval(`(async () => { const c = (document.cookie.match(/(?:^|; )azc=([^;]+)/) || [])[1] || ""; const r = await fetch(${JSON.stringify(p)}, { method: ${JSON.stringify(m || "GET")}, headers: { "Content-Type": "application/json", "x-csrf": c }, body: ${b ? JSON.stringify(JSON.stringify(b)) : "undefined"} }); return r.status; })()`);
    const st = await call(login, "POST", cred);
    tab.call = call;
    tab.done = async () => { tab.close(); await browser.send("Target.disposeBrowserContext", { browserContextId }).catch(() => { }); browser.close(); };
    return { tab, st };
  }
  const until = async (tab, expr, ms) => { for (let i = 0; i < (ms || 8000) / 150; i++) { const v = await tab.eval(expr).catch(() => null); if (v) return v; await sleep(150); } return null; };
  const go = async (tab, url) => { await tab.send("Page.navigate", { url: BASE + url }); await tab.once("Page.loadEventFired", 15000); };
  const navText = tab => tab.eval(`document.querySelector("#pSide .p-nav")?.innerText || ""`);
  const navBtn = (scope, v) => `#pSide .p-nav button[data-s="${scope}"][data-v="${v}"]`;

  try {
    console.log("▸ THE OLD ADDRESSES LAND IN THE CONSOLE");
    const P = await signedIn("/api/platform/login", { email: "platform@luxora.shop", password: "platform123" });
    ok(P.st === 200, "platform owner signs in");
    P.tab.events = [];
    await go(P.tab, "/platform.html");
    ok(await until(P.tab, `location.pathname === "/console.html" && !!document.querySelector("#pSide .p-nav button")`), "the platform address opens the console", await P.tab.eval("location.href"));

    console.log("▸ A NEW APP APPEARS IN THE MENU");
    ok(!/Configured apps/.test(await navText(P.tab)), "before anything is composed there is no Configured apps menu");
    const cst = await P.tab.call("/api/compose/insurance", "POST", {});
    ok(cst >= 200 && cst < 300, "an application is composed", cst);
    await go(P.tab, "/console.html?scope=platform");
    ok(await until(P.tab, `!!document.querySelector('${navBtn("platform", "app_cp_insurance")}')`), "it appears under Configured apps for the owner");
    const appBtn = await P.tab.eval(`(() => { const b = document.querySelector('${navBtn("platform", "app_cp_insurance")}'); const sec = b && b.closest(".p-nav-sec"); return { label: b ? b.textContent : "", section: sec ? sec.querySelector("summary").textContent : "" }; })()`);
    ok(/Insurance/.test(appBtn.label) && /Configured apps/.test(appBtn.section), "named in the menu, in its own section", appBtn);
    await P.tab.eval(`document.querySelector('${navBtn("platform", "app_cp_insurance")}').click()`);
    ok(await until(P.tab, `!!document.querySelector("#vBody table") && /Insurance/.test(document.querySelector("#vTitle")?.innerText || "")`), "opening it shows its records screen");
    ok(/view=app_cp_insurance/.test(await P.tab.eval("location.search")) && /scope=platform/.test(await P.tab.eval("location.search")), "the address bar names the screen");
    await P.tab.send("Page.reload"); await P.tab.once("Page.loadEventFired", 15000);
    ok(await until(P.tab, `/Insurance/.test(document.querySelector("#vTitle")?.innerText || "") && !!document.querySelector("#vBody table")`), "a reload reopens the same screen");
    const pIssues = problems(P.tab.events);
    ok(!pIssues.length, "no browser errors on the platform side", pIssues);

    console.log("▸ THE STORE OWNER SEES IT AND CAN GRANT IT");
    const S = await signedIn("/api/auth/login?store=luxora", { email: "admin@luxora.shop", password: "admin123" });
    ok(S.st === 200, "store owner signs in");
    S.tab.events = [];
    await go(S.tab, "/admin.html?store=luxora");
    ok(await until(S.tab, `location.pathname === "/console.html" && !!document.querySelector('${navBtn("store", "app_cp_insurance")}')`), "the store address opens the console, with the app in the menu");
    await S.tab.eval(`document.querySelector('${navBtn("store", "app_cp_insurance")}').click()`);
    ok(await until(S.tab, `!!document.querySelector('#vBody [data-new="cp_insurance"]')`), "the store owner opens it, with + New");
    await S.tab.eval(`document.querySelector('#vBody [data-new="cp_insurance"]').click()`);
    ok(await until(S.tab, `!!document.querySelector("#modal .p-modal")`), "+ New opens the record form (the console provides the form container)");
    await S.tab.eval(`document.getElementById("modal").innerHTML = ""`);
    await S.tab.eval(`document.querySelector('${navBtn("store", "team")}').click()`);
    ok(await until(S.tab, `!!document.getElementById("roleNew")`), "Team & Roles opens");
    await S.tab.eval(`document.getElementById("roleNew").click()`);
    ok(await until(S.tab, `[...document.querySelectorAll("#modal [data-rmsec]")].some(x => x.dataset.rmsec === "app_cp_insurance")`), "the role editor offers the app as a grant");
    ok(await S.tab.eval(`[...document.querySelectorAll("#modal label")].some(l => /Insurance/.test(l.innerText) && /app/.test(l.innerText) && l.querySelector('[data-rmsec="app_cp_insurance"]'))`), "and names it, not just its key");
    await S.tab.eval(`document.getElementById("modal").innerHTML = ""`);
    const sIssues = problems(S.tab.events);
    ok(!sIssues.length, "no browser errors on the store side", sIssues);

    console.log("▸ STAFF WITHOUT THE GRANT DON'T SEE IT");
    await S.tab.call("/api/admin/roles?store=luxora", "POST", { key: "desk", name: "Desk", sections: { orders: "write" } });
    await S.tab.call("/api/admin/staff?store=luxora", "POST", { name: "Dee Desk", email: "dee@luxora.shop", staff_role: "desk", password: "Desk-Pass-123" });
    const D = await signedIn("/api/auth/login?store=luxora", { email: "dee@luxora.shop", password: "Desk-Pass-123" });
    await go(D.tab, "/console.html?scope=store");
    ok(await until(D.tab, `!!document.querySelector('${navBtn("store", "orders")}')`), "the staff member's console opens");
    ok(!(await D.tab.eval(`!!document.querySelector('${navBtn("store", "app_cp_insurance")}')`)), "the ungranted app is not in their menu");
    await S.tab.call("/api/admin/roles?store=luxora", "POST", { key: "desk", name: "Desk", sections: { orders: "write", app_cp_insurance: "read" } });
    await go(D.tab, "/console.html?scope=store");
    ok(await until(D.tab, `!!document.querySelector('${navBtn("store", "app_cp_insurance")}')`), "once granted, it appears in their menu");
    await D.tab.done(); await S.tab.done(); await P.tab.done();
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
