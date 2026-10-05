/* Platform console smoke: the canonical navigation model and tenant authoring.
   The guided store wizard was removed — a tenant is authored in one modal, and the
   console is now organized as the constitution declares: 12 sections, one canonical home
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

    console.log("▸ TENANT AUTHORING (the modal replaces the guided wizard)");
    const navBtn = [...doc.querySelectorAll("[data-v]")].find(b => b.dataset.v === "tenants-admin");
    ok(!!navBtn, "Tenants lives under 11 · Administration");
    click(win, navBtn); await sleep(1200);
    ok(/Tenants \(/.test(doc.body.textContent), "the surface is the tenant registry");
    const newBtn = doc.getElementById("newTenant");
    ok(!!newBtn, "+ New tenant action present");
    click(win, newBtn); await sleep(700);
    const tnName = doc.getElementById("tnName");
    ok(!!tnName, "the tenant modal rendered (one form, no wizard)");
    if (tnName) {
      tnName.value = "Acme One"; doc.getElementById("tnSlug").value = "acme1";
      doc.getElementById("tnCountry").value = "IN";
      doc.getElementById("tnOwnerName").value = "Ava One";
      doc.getElementById("tnOwner").value = "owner@acme1.shop";
      const tp = doc.getElementById("tnPass"); if (tp) tp.value = "acme1234";
      click(win, doc.getElementById("tnSave")); await sleep(1800);
      const cfg = await f("/api/config?store=acme1");
      ok(cfg.brand && cfg.brand.name === "Acme One", "the new tenant's storefront resolves", cfg.brand && cfg.brand.name);
      ok(cfg.tenant && cfg.tenant.slug === "acme1", "tenant created with the declared slug", cfg.tenant && cfg.tenant.slug);
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
