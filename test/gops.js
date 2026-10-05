/* Verifies every Global Operations view renders across stores without JS errors. */
"use strict";
const { spawn } = require("child_process");
const { JSDOM, VirtualConsole } = require("jsdom");
const path = require("path");
const PORT = 8807;
const BASE = `http://localhost:${PORT}`;
const jar = new Map();
let passed = 0, failed = 0;
function ok(c, n, x) { if (c) { passed++; console.log("  ✓ " + n); } else { failed++; console.log("  ✗ " + n + (x ? " → " + x : "")); } }
function cookieHeader() { return [...jar].map(([k, v]) => k + "=" + v).join("; "); }
async function f(p, method = "GET", body) {
  const opt = { method, headers: { Cookie: cookieHeader(), ...(method !== "GET" ? { "x-csrf": jar.get("azc") || "" } : {}) } };
  if (body) { opt.body = JSON.stringify(body); opt.headers["Content-Type"] = "application/json"; }
  const r = await fetch(BASE + p, opt);
  (r.headers.getSetCookie ? r.headers.getSetCookie() : []).forEach(c => { const [kv] = c.split(";"); const i = kv.indexOf("="); jar.set(kv.slice(0, i).trim(), kv.slice(i + 1).trim()); });
  return r.json().catch(() => ({}));
}
async function render(p, wait = 2200) {
  const vc = new VirtualConsole(); const errs = [];
  vc.on("jsdomError", e => errs.push(String(e.message)));
  vc.on("error", (...a) => errs.push(a.join(" ")));
  const dom = await JSDOM.fromURL(BASE + p, { resources: "usable", runScripts: "dangerously", pretendToBeVisual: true, virtualConsole: vc,
    beforeParse(w) {
      w.fetch = (u, o = {}) => {
        const url = String(u).startsWith("http") ? String(u) : BASE + String(u);
        const headers = Object.assign({ Cookie: cookieHeader() }, o.headers);
        if (o.method && o.method !== "GET" && !headers["x-csrf"]) headers["x-csrf"] = jar.get("azc") || "";
        return fetch(url, { ...o, headers }).then(res => { (res.headers.getSetCookie ? res.headers.getSetCookie() : []).forEach(c => { const [kv] = c.split(";"); const i = kv.indexOf("="); jar.set(kv.slice(0, i).trim(), kv.slice(i + 1).trim()); }); return res; });
      };
      w.scrollTo = () => { };
    } });
  await new Promise(r => setTimeout(r, wait));
  return { doc: dom.window.document, win: dom.window, errs: errs.filter(e => !/css|Could not parse CSS/i.test(e)) };
}
const click = (w, el) => el.dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const db = path.join(__dirname, "gops.db");
  for (const s of ["", "-wal", "-shm"]) { try { require("fs").rmSync(db + s, { force: true }); } catch (e) { } }
  const srv = spawn(process.execPath, [path.join(__dirname, "..", "server.js")], { env: { ...process.env, PORT, LX_DB: db }, stdio: ["ignore", "ignore", "inherit"] });
  let up = false;
  for (let i = 0; i < 120; i++) { try { const h = await fetch(BASE + "/healthz"); if (h.ok) { up = true; break; } } catch (e) { } await sleep(1000); }
  if (!up) { console.log("server failed to boot"); process.exit(1); }
  try {
    await f("/api/session");
    const pl = await f("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" });
    ok(!!pl.admin, "platform login");

    console.log("▸ TENANCY — the platform registry");
    {
      const hp = await render("/platform.html");
      ok(/MRR|Collected/i.test(hp.doc.body.textContent), "the console lands on the platform command dashboard", hp.doc.body.textContent.slice(0, 60));
      ok(hp.doc.querySelectorAll(".p-nav-sec").length === 12, "the canonical 12-section tree renders", hp.doc.querySelectorAll(".p-nav-sec").length);
      // the tenants registry is the platform's tenancy surface: every tenant listed with
      // an edit action (the wizard is gone; authoring is a single modal now)
      const tBtn = [...hp.doc.querySelectorAll("[data-v]")].find(x => x.dataset.v === "tenants-admin");
      click(hp.win, tBtn); await sleep(1600);
      ok(hp.doc.querySelectorAll("[data-tedit]").length >= 3, "tenants view lists every tenant with an Edit action", hp.doc.querySelectorAll("[data-tedit]").length);
      ok(/Tenants \(/.test(hp.doc.body.textContent), "the surface is the tenant registry, not a store hub");
      ok(hp.errs.length === 0, "tenants view: no JS errors", hp.errs.slice(0, 2).join("|"));
      click(hp.win, hp.doc.querySelector("[data-tedit]")); await sleep(1200);
      ok(!!hp.doc.getElementById("tnName"), "edit opens a single tenant modal (no guided wizard)");
      const mc = hp.doc.querySelector("[data-mclose]"); if (mc) click(hp.win, mc);
    }

    console.log("▸ GLOBAL OPERATIONS views render (cross-store, no JS errors)");
    const page = await render("/platform.html");
    const nav = [...page.doc.querySelectorAll("[data-v]")];
    ok(nav.length >= 100, "canonical nav: a leaf per capability (zero-gap tree)", nav.length);
    const gopsKeys = ["gops", "gorders", "gcatalog", "gb2b", "gmarket", "gfinance", "goffers", "gsupport", "gcontent", "grisk", "gteam", "ganalytics", "gdata", "persons", "knowledge-graph", "marketplace", "workflows"];
    for (const k of gopsKeys) ok(nav.some(b => b.dataset.v === k), "nav has " + k);

    // Ops Hub
    let b = nav.find(x => x.dataset.v === "gops"); click(page.win, b); await sleep(2500);
    const hub = page.doc.body.textContent;
    ok(/Platform GMV|Tenant comparison/.test(hub), "ops hub renders KPIs + tenant comparison");
    ok(page.doc.querySelectorAll("table tbody tr").length >= 3, "ops hub: tenant comparison lists every tenant", page.doc.querySelectorAll("table tbody tr").length);
    ok(page.errs.length === 0, "ops hub: no JS errors", page.errs.slice(0, 2).join("|"));

    // each remaining view: render, require tables + zero errors. The regexes pin the
    // capability coverage: every store capability must surface somewhere in the platform.
    const expect = { gorders: [/Orders/, /RFQs/, /Shipments|fulfilment/i, /serialized|Serialized/, /dispatch|Quick-commerce/i],
      gcatalog: [/product|Products/i, /sku|SKU/i, /Replenishment|Planning/i],
      gb2b: [/seller|Seller/i, /tender|Tender/i, /assurance|letter of credit|Trade/i],
      gmarket: [/Ad inventory|Seller KPIs/],
      gfinance: [/Payout|Dispute/i, /settlement|Settlement/i, /Configured providers|UPI|escrow/i],
      goffers: [/Promotion|Recurring|Membership/i, /Affiliate/i],
      gsupport: [/Support queue|SLA/],
      gcontent: [/brand|Brand/i, /Taxonomy|taxonomy/i, /review|Review|Moderation/i],
      grisk: [/Risk|Trash/i],
      gteam: [/Staff|Webhook/i, /settings|Settings/i],
      ganalytics: [/Top products|Inventory value/i, /Experiment/i] };
    for (const [k, res] of Object.entries(expect)) {
      const bb = [...page.doc.querySelectorAll("[data-v]")].find(x => x.dataset.v === k);
      click(page.win, bb); await sleep(2500);
      const txt = page.doc.body.textContent;
      ok(res.every(r => r.test(txt)), k + " renders expected panels", txt.slice(0, 80).replace(/\s+/g, " "));
      ok(page.errs.length === 0, k + ": no JS errors", page.errs.slice(0, 2).join("|"));
    }

    // Data Explorer: dataset picker is generated from live metadata and switching works
    let dd = [...page.doc.querySelectorAll("[data-v]")].find(x => x.dataset.v === "gdata");
    click(page.win, dd); await sleep(2000);
    const sel = page.doc.getElementById("gEntity");
    ok(!!sel && sel.options.length >= 30, "data explorer: dataset list is generated (not fixed)", sel && sel.options.length);
    if (sel) { sel.value = "brand"; sel.dispatchEvent(new page.win.Event("change", { bubbles: true })); await sleep(2000);
      ok(page.doc.querySelectorAll("table tbody tr").length >= 1, "data explorer: switching dataset re-renders", page.doc.querySelectorAll("table tbody tr").length); }

    // store filter narrows to one store on the hub
    let hh = [...page.doc.querySelectorAll("[data-v]")].find(x => x.dataset.v === "gops");
    click(page.win, hh); await sleep(2200);
    const tt = page.doc.getElementById("gTenant");
    ok(!!tt && tt.options.length >= 4, "store filter lists every store", tt && tt.options.length);
    if (tt) { tt.value = String(tt.options[1].value); tt.dispatchEvent(new page.win.Event("change", { bubbles: true })); await sleep(2200);
      ok(page.doc.querySelectorAll("table tbody tr").length >= 1, "store filter narrows (still renders)"); }
    ok(page.errs.length === 0, "final: no JS errors", page.errs.slice(0, 2).join("|"));

    console.log("▸ FAN-OUT security boundary");
    const bad1 = await f("/api/platform/fanout?path=/api/admin/planning/run");
    ok(!!bad1.error, "non-GET route refused", JSON.stringify(bad1));
    const bad2 = await f("/api/platform/fanout?path=/api/platform/tenants");
    ok(!!bad2.error, "non-allowlisted platform route refused");
    const bad3 = await f("/api/platform/fanout?path=/api/meta/entity/order");
    ok(!!bad3.error, "generic entity route refused (served by /platform/data instead)");
    const good = await f("/api/platform/fanout?path=/api/admin/stats");
    ok(!!good.results && good.results.length >= 3, "allowlisted stats fans out to every store", good.results && good.results.length);

    console.log("▸ GENERIC READER");
    const idx = await f("/api/platform/data");
    ok(idx.entities.length >= 30, "entity index enumerates", idx.entities.length);
    ok(idx.entities.some(e => e.key === "order" && Array.isArray(e.fields)), "index carries field metadata for rendering");
    const orders = await f("/api/platform/data/order");
    ok(Array.isArray(orders.rows), "cross-store order read");
    ok(orders.rows.every(r => r.tenant_id != null), "every row carries tenant_id");
    const oneStore = await f("/api/platform/data/order?tenant_id=2");
    ok(oneStore.rows.every(r => r.tenant_id === 2), "tenant filter narrows to one store", JSON.stringify(oneStore.rows.map(r => r.tenant_id)));
  } catch (e) { console.log("FATAL", e); failed++; }
  console.log(`\n${passed} passed, ${failed} failed`);
  srv.kill(); for (const s of ["", "-wal", "-shm"]) { try { require("fs").rmSync(db + s, { force: true }); } catch (e) { } }
  process.exit(failed ? 1 : 0);
})();
