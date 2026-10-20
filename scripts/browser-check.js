/* LUXORA Platform — real-browser check of every page under the production security headers.
   Boots a server on a throwaway database, drives headless Chrome over the DevTools protocol
   (no Puppeteer — Node's built-in WebSocket), and fails on anything a person would hit: a
   Content-Security-Policy violation, an uncaught exception, a console error, a script or
   stylesheet that failed to load, or a page that rendered nothing. The consoles are checked
   signed out (their sign-in screens) and signed in.

     npm run check:browser            (CHROME_PATH=/path/to/chrome to choose the binary)

   Exits 0 when clean, 1 with a report otherwise, 2 when no Chrome is installed. */
"use strict";
const { spawn } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const ROOT = path.join(__dirname, "..");
const PORT = Number(process.env.CHECK_PORT || 8877);
const BASE = `http://localhost:${PORT}`;
const DB = path.join(os.tmpdir(), "luxora-browser-" + process.pid + ".db");
const sleep = ms => new Promise(r => setTimeout(r, ms));

function findChrome() {
  const c = [process.env.CHROME_PATH, "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome", "/usr/bin/google-chrome-stable", "/usr/bin/chromium", "/usr/bin/chromium-browser",
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"].filter(Boolean);
  return c.find(p => { try { return fs.statSync(p).isFile(); } catch (e) { return false; } }) || null;
}

/* the pages, and what "rendered" means on each */
const STORE = "() => { const m = document.querySelector('#page'); return !!m && m.innerText.trim().length > 20 && !/Something went wrong/.test(m.innerText) }";
const PAGES = [
  ["/index.html?store=luxora", STORE], ["/results.html?q=a", STORE], ["/product.html?id=__PRODUCT__", STORE],
  ["/cart.html", STORE], ["/deals.html", STORE], ["/orders.html", "() => !!document.querySelector('#page')"],
  ["/gift-cards.html", STORE], ["/customer-service.html", STORE], ["/registry.html", "() => !!document.querySelector('#page')"], ["/sell.html", "() => !!document.querySelector('#page h1, #page h3')"], ["/messages.html", "() => !!document.querySelector('#page h1, #page h3')"],
  ["/reset.html", "() => !!document.querySelector('#resetForm')"], ["/reset.html?token=" + "0".repeat(64), "() => !!document.querySelector('#rpPass')"], ["/does-not-exist.html", "() => document.body.innerText.length > 10"],
  ["/admin.html", "() => document.body.innerText.trim().length > 20"], ["/platform.html", "() => document.body.innerText.trim().length > 20"],
  ["/console.html", "() => document.body.innerText.trim().length > 20"], ["/docs/user-manual.html", "() => document.body.innerText.trim().length > 20"], ["/docs/architecture.html", "() => document.body.innerText.trim().length > 20"]
];
const SIGNED_IN = [
  { name: "store admin", login: "/api/auth/login?store=luxora", cred: { email: "admin@luxora.shop", password: "admin123" }, pages: ["/console.html", "/admin.html", "/checkout.html", "/orders.html"], walk: "/console.html?scope=store" },
  { name: "platform admin", login: "/api/platform/login", cred: { email: "platform@luxora.shop", password: "platform123" }, pages: ["/console.html", "/platform.html"], walk: "/console.html?scope=platform" }
];

class Tab {
  constructor(ws) { this.ws = ws; this.id = 0; this.wait = new Map(); this.events = []; this.listeners = [];
    ws.onmessage = m => { const d = JSON.parse(m.data); if (d.id && this.wait.has(d.id)) { const w = this.wait.get(d.id); this.wait.delete(d.id); d.error ? w.rej(new Error(d.error.message)) : w.res(d.result); } else if (d.method) { this.events.push(d); this.listeners.forEach(f => f(d)); } }; }
  static open(url) { return new Promise((res, rej) => { const ws = new WebSocket(url); ws.onopen = () => res(new Tab(ws)); ws.onerror = e => rej(new Error("devtools socket: " + (e.message || "error"))); }); }
  send(method, params) { const id = ++this.id; this.ws.send(JSON.stringify({ id, method, params: params || {} })); return new Promise((res, rej) => { this.wait.set(id, { res, rej }); setTimeout(() => { if (this.wait.has(id)) { this.wait.delete(id); rej(new Error(method + " timed out")); } }, 20000); }); }
  once(method, ms) { return new Promise(res => { const t = setTimeout(() => res(null), ms); const f = d => { if (d.method === method) { clearTimeout(t); this.listeners = this.listeners.filter(x => x !== f); res(d); } }; this.listeners.push(f); }); }
  async eval(expr) { const r = await this.send("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true }); return r.result && r.result.value; }
  close() { try { this.ws.close(); } catch (e) { } }
}

/* everything on a page that a person would notice is wrong */
function problems(events) {
  const out = [];
  for (const e of events) {
    const p = e.params || {};
    if (e.method === "Runtime.exceptionThrown") out.push("uncaught: " + ((p.exceptionDetails && (p.exceptionDetails.exception && p.exceptionDetails.exception.description || p.exceptionDetails.text)) || "?").split("\n")[0]);
    else if (e.method === "Runtime.consoleAPICalled" && p.type === "error") out.push("console.error: " + (p.args || []).map(a => a.value || a.description || "").join(" ").slice(0, 200));
    else if (e.method === "Log.entryAdded" && p.entry && p.entry.level === "error") {
      const t = p.entry.text || "";
      /* a 401/403/404 from an API call the page makes signed out is expected — not a defect */
      if (/status of (401|403|404)/.test(t) && /\/api\//.test(p.entry.url || "")) continue;
      if (/favicon\.ico/.test(p.entry.url || t)) continue;
      if (/status of 404/.test(t) && /does-not-exist/.test(p.entry.url || "")) continue; /* the 404 page's own status */
      out.push((/Content Security Policy|Refused to/.test(t) ? "CSP: " : "log: ") + t.slice(0, 240) + (p.entry.url ? " (" + p.entry.url.replace(BASE, "") + ")" : ""));
    }
    else if (e.method === "Network.loadingFailed" && !p.canceled && /^(Script|Stylesheet|Document)$/.test(p.type || "")) out.push("failed to load " + p.type + ": " + (p.errorText || ""));
    else if (e.method === "Network.responseReceived" && /^(Script|Stylesheet)$/.test(p.type || "") && p.response && p.response.status >= 400) out.push(p.type + " " + p.response.status + ": " + p.response.url.replace(BASE, ""));
  }
  return [...new Set(out)];
}

/* test/shipping-ui.js drives Chrome with the same helpers */
module.exports = { Tab, findChrome, problems };
if (require.main === module) (async () => {
  const chrome = findChrome();
  if (!chrome) { console.error("No Chrome/Chromium found — set CHROME_PATH"); process.exit(2); }
  for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
  const env = { ...process.env, PORT: String(PORT), LX_DB: DB, LX_LOG: "" };
  delete env.NODE_ENV;
  const srv = spawn(process.execPath, [path.join(ROOT, "server.js")], { env, stdio: ["ignore", "ignore", "pipe"] });
  let srvErr = ""; srv.stderr.on("data", d => { srvErr += d; });
  for (let i = 0; i < 120; i++) { try { if ((await fetch(BASE + "/healthz")).ok) break; } catch (e) { } await sleep(500); }

  const profile = fs.mkdtempSync(path.join(os.tmpdir(), "luxora-chrome-"));
  const br = spawn(chrome, ["--headless=new", "--remote-debugging-port=0", "--user-data-dir=" + profile, "--no-first-run", "--no-default-browser-check", "--disable-gpu", "--disable-extensions", ...(process.getuid && process.getuid() === 0 ? ["--no-sandbox"] : []), "about:blank"], { stdio: "ignore" });
  let port = null;
  for (let i = 0; i < 100 && !port; i++) { try { port = fs.readFileSync(path.join(profile, "DevToolsActivePort"), "utf8").split("\n")[0]; } catch (e) { await sleep(100); } }
  const done = code => { try { br.kill(); } catch (e) { } try { srv.kill("SIGTERM"); } catch (e) { }
    setTimeout(() => { for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } } try { fs.rmSync(profile, { recursive: true, force: true }); } catch (e) { } process.exit(code); }, 500); };
  if (!port) { console.error("Chrome did not start its DevTools endpoint"); return done(1); }

  const product = await fetch(BASE + "/api/products?limit=1&store=luxora").then(r => r.json()).then(j => (j.items && j.items[0] && j.items[0].id) || "").catch(() => "");
  const report = [];
  let checked = 0;

  /* one browser context per identity, so cookies never leak between runs */
  async function visit(pages, who, signIn) {
    const ctx = await fetch(`http://127.0.0.1:${port}/json/version`).then(r => r.json());
    const browser = await Tab.open(ctx.webSocketDebuggerUrl);
    const { browserContextId } = await browser.send("Target.createBrowserContext");
    const { targetId } = await browser.send("Target.createTarget", { url: "about:blank", browserContextId });
    const list = await fetch(`http://127.0.0.1:${port}/json/list`).then(r => r.json());
    const tab = await Tab.open(list.find(t => t.id === targetId).webSocketDebuggerUrl);
    for (const d of ["Runtime", "Log", "Page", "Network"]) await tab.send(d + ".enable");
    if (signIn) {
      await tab.send("Page.navigate", { url: BASE + "/index.html?store=luxora" }); await tab.once("Page.loadEventFired", 15000); await sleep(800);
      const r = await tab.eval(`(async () => { const c = (document.cookie.match(/(?:^|; )azc=([^;]+)/) || [])[1] || ""; const x = await fetch(${JSON.stringify(signIn.login)}, { method: "POST", headers: { "Content-Type": "application/json", "x-csrf": c }, body: JSON.stringify(${JSON.stringify(signIn.cred)}) }); return x.status; })()`);
      if (r !== 200) report.push({ page: "(sign-in)", who, issues: ["sign-in returned " + r] });
    }
    for (const [p, ready] of pages) {
      tab.events = [];
      const url = BASE + p.replace("__PRODUCT__", encodeURIComponent(product));
      await tab.send("Page.navigate", { url });
      await tab.once("Page.loadEventFired", 15000);
      let ok = false;
      for (let i = 0; i < 40 && !ok; i++) { ok = !!(await tab.eval("(" + ready + ")()").catch(() => false)); if (!ok) await sleep(150); }
      await sleep(700); /* let late async boot work surface its errors */
      const issues = problems(tab.events);
      if (!ok) issues.unshift("page did not render");
      checked++;
      report.push({ page: p, who, issues });
    }
    /* every section of a console, opened the way a person would: its nav button */
    if (signIn && signIn.walk) {
      tab.events = [];
      await tab.send("Page.navigate", { url: BASE + signIn.walk }); await tab.once("Page.loadEventFired", 15000);
      let views = [];
      for (let i = 0; i < 40 && !views.length; i++) { views = (await tab.eval("[...document.querySelectorAll('#pSide .p-nav button[data-v]')].map(b => b.dataset.v)").catch(() => [])) || []; if (!views.length) await sleep(150); }
      if (!views.length) report.push({ page: signIn.walk + " (sections)", who, issues: ["no section navigation found"] });
      for (const v of views) {
        tab.events = [];
        await tab.eval(`(() => { const b = document.querySelector('#pSide .p-nav button[data-v="${v}"]'); if (b) b.click(); return !!b; })()`);
        await sleep(900);
        const empty = await tab.eval("(() => { const m = document.querySelector('#view, .p-main, main'); return !m || m.innerText.trim().length < 5 })()").catch(() => false);
        const issues = problems(tab.events);
        if (empty) issues.unshift("section rendered nothing");
        /* a view's own failure is caught and printed into the page, not thrown — so a
           missing function or a bad property read shows up only as text on screen */
        const broke = await tab.eval("(() => { const m = document.querySelector('#vBody'); const t = m ? m.innerText : ''; return /is not defined|is not a function|Cannot read propert|Unexpected token|undefined \\(reading/.test(t) ? t.trim().slice(0, 160) : '' })()").catch(() => "");
        if (broke) issues.unshift("view failed: " + broke);
        checked++;
        report.push({ page: signIn.walk + " › " + v, who, issues });
      }
    }
    tab.close();
    await browser.send("Target.disposeBrowserContext", { browserContextId }).catch(() => { });
    browser.close();
  }

  try {
    await visit(PAGES, "signed out");
    for (const si of SIGNED_IN) await visit(si.pages.map(p => [p, "() => document.body.innerText.trim().length > 20"]), si.name, si);
  } catch (e) { report.push({ page: "(harness)", who: "-", issues: [e.message] }); }

  const bad = report.filter(r => r.issues.length);
  for (const r of report) console.log((r.issues.length ? "  ✗ " : "  ✓ ") + r.page + "  [" + r.who + "]" + (r.issues.length ? "\n      " + r.issues.join("\n      ") : ""));
  console.log(`\n${checked} page loads in ${path.basename(chrome)} — ${bad.length ? bad.length + " with problems" : "no CSP violations, uncaught errors or failed loads"}`);
  if (srvErr.trim() && bad.length) console.log("\nserver stderr:\n" + srvErr.slice(-2000));
  done(bad.length ? 1 : 0);
})();
