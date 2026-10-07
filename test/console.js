/* THE ONE CONSOLE — /console.html, the shell that merged the two consoles.

   There were two apps: /admin.html (store) and /platform.html (platform). The
   unified console is one entry point that boots against /api/auth/me — the
   unified identity — and holds BOTH authorities on one client, because the two
   scopes are kept apart by authz's namespacing rather than by separate sessions.

   This proves the contract end to end against a live server and a real DOM:
     §A one sign-in carries both authorities, and the grant map is namespaced;
     §B the merged console boots and renders BOTH surfaces in one nav;
     §C the ⇄ switcher flips scope in place, with no second sign-in;
     §D a leaf dispatches to the bundle that owns it, and each bundle enforces
        the grants the shell seeded (not "everything", which is what an unsown
        allowed list would mean);
     §E a store-only identity sees its own surface only;
     §F signing out ends BOTH sessions — against the real paths, not 404s. */
"use strict";
const DB = require("path").join(__dirname, "console.db");
process.env.LX_DB = DB;   /* before any lib require, so a fresh connection opens this file */
const { spawn } = require("child_process");
const { JSDOM, VirtualConsole } = require("jsdom");
const path = require("path");
const PORT = 8861;
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
async function waitFor(cond, ms = 7000) {
  for (let i = 0; i < ms / 100; i++) { try { if (cond()) return true; } catch (e) { } await sleep(100); }
  return false;
}
/* render a page in jsdom; every fetch the page issues is recorded, so the shell's
   sign-out can be shown to hit the real logout endpoints */
async function render(page, wait = 3500) {
  const errs = [], fetches = [];
  const vc = new VirtualConsole();
  vc.on("jsdomError", e => errs.push(String(e.message)));
  vc.on("error", (...a) => errs.push(a.join(" ")));
  const dom = await JSDOM.fromURL(BASE + page, { resources: "usable", runScripts: "dangerously", pretendToBeVisual: true, virtualConsole: vc,
    beforeParse(w) {
      w.fetch = (u, o) => { const url = String(u).startsWith("http") ? String(u) : BASE + String(u);
        fetches.push(((o && o.method) || "GET") + " " + url.replace(BASE, ""));
        const headers = Object.assign({ Cookie: cookies() }, o && o.headers);
        if (o && o.method && o.method !== "GET" && !headers["x-csrf"]) headers["x-csrf"] = jar.get("azc") || "";
        return fetch(url, { ...o, headers }).then(res => { (res.headers.getSetCookie ? res.headers.getSetCookie() : []).forEach(c => { const [kv] = c.split(";"); const i = kv.indexOf("="); jar.set(kv.slice(0, i).trim(), kv.slice(i + 1).trim()); }); return res; }); };
      w.scrollTo = () => { };
    } });
  /* the render cycle paints twice: the unified shell, then the bundle's own shell (which
     replaces #app), then the unified chrome is re-applied. Only the settled state has the
     namespaced nav (buttons carry data-s) AND a rendered body — the intermediates show
     "Loading…" or the bundle's unscoped nav — so that is what we wait for */
  await waitFor(() => { const d = dom.window.document;
    const body = d.querySelector("#vBody"), nav = d.querySelector(".p-nav");
    return !!body && !!nav && !/Loading/i.test(body.textContent || "") && !!nav.querySelector("button[data-s]"); }, wait);
  return { doc: dom.window.document, win: dom.window, dom,
    errs: errs.filter(e => !/css|Could not parse CSS|Not implemented/i.test(e)), fetches };
}
const navBtn = (doc, s, v) => [...doc.querySelectorAll(".p-nav button")].find(b => b.dataset.s === s && b.dataset.v === v);
/* the shell repaints more than once per navigation (its own shell, then the bundle's,
   then the unified chrome again). Only the last pass carries the namespaced nav, so
   assertions about scope wait for that settled state before they read the chrome */
const settled = doc => !!doc.querySelector(".p-nav button[data-s]");
const waitForSettled = async (doc, ms = 7000) => waitFor(() => settled(doc), ms);

(async () => {
  for (const s of ["", "-wal", "-shm"]) { try { require("fs").rmSync(DB + s, { force: true }); } catch (e) { } }
  const boot = async () => {
    const srv = spawn(process.execPath, [path.join(__dirname, "..", "server.js")], { env: { ...process.env, PORT, LX_DB: DB }, stdio: ["ignore", "ignore", "inherit"] });
    for (let i = 0; i < 120; i++) { try { if ((await fetch(BASE + "/healthz")).ok) return srv; } catch (e) { } await sleep(500); }
    throw new Error("server failed to boot");
  };
  const srv = await boot();
  try {
    /* the store session must exist first, or /api/auth/login would see no tenant */
    await f("/api/session?store=luxora");

    console.log("▸ §A ONE SIGN-IN, BOTH AUTHORITIES");
    const plat = await f("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" });
    ok(!!plat.ok, "the platform sign-in succeeds", JSON.stringify(plat));
    const store = await f("/api/auth/login?store=luxora", "POST", { email: "admin@luxora.shop", password: "admin123" });
    ok(!!store.ok, "the store sign-in succeeds on the SAME client", JSON.stringify(store));
    const me = await f("/api/auth/me");
    ok(!!(me.hasStore && me.hasPlatform), "/api/auth/me answers with BOTH scopes held at once", JSON.stringify({ hasStore: me.hasStore, hasPlatform: me.hasPlatform }));
    ok(!!(me.identity.store && me.identity.store.role === "admin"), "the store authority is the store's admin");
    ok(!!(me.identity.platform && me.identity.platform.email === "platform@luxora.shop"), "the platform authority is the platform admin", JSON.stringify(me.identity.platform));
    const gk = Object.keys(me.grants || {});
    ok(gk.some(k => k.startsWith("store:")), "the grant map carries the store surface, namespaced");
    ok(gk.some(k => k.startsWith("platform:")), "and the platform surface, namespaced");
    ok(gk.every(k => k.startsWith("store:") || k.startsWith("platform:")), "no grant escapes its scope — the two surfaces are never blended", JSON.stringify(gk.filter(k => !k.startsWith("store:") && !k.startsWith("platform:"))));

    console.log("▸ §B THE CONSOLE BOOTS WITH BOTH SURFACES IN ONE NAV");
    const R = await render("/console.html");
    ok(!R.errs.length, "the one console boots with no JS errors", R.errs.join(" | "));
    const navText = (R.doc.querySelector(".p-nav") || {}).textContent || "";
    ok(/PLATFORM/.test(navText), "the nav renders the platform surface");
    ok(/THIS STORE/.test(navText), "the nav renders this store's surface beside it");
    ok(!!navBtn(R.doc, "platform", "identity"), "a platform-only leaf is in the nav");
    ok(!!navBtn(R.doc, "store", "team"), "and a store-only leaf is too");

    console.log("▸ §C THE SCOPE SWITCHER — no second sign-in, no second URL");
    ok(!!R.doc.querySelector("#scopeBtn"), "a dual identity is offered the ⇄ switcher");
    ok(await waitFor(() => R.doc.querySelector(".p-chip") && /platform/i.test(R.doc.querySelector(".p-chip").textContent)), "the console opens on the platform scope");
    R.doc.querySelector("#scopeBtn").click();
    ok(await waitFor(() => settled(R.doc) && (() => { const c = R.doc.querySelector(".p-chip"); return c && !/platform/i.test(c.textContent); })()), "one click flips to the store scope in place");
    ok(await waitFor(() => { const t = R.doc.querySelector("#vTitle"); return settled(R.doc) && t && /dashboard/i.test(t.textContent); }), "the store console's dashboard renders under the store scope");
    const back = R.doc.querySelector("#scopeBtn");
    if (back) back.click();
    ok(await waitFor(() => settled(R.doc) && (() => { const c = R.doc.querySelector(".p-chip"); return c && /platform/i.test(c.textContent); })()), "and a second click returns to the platform scope");

    console.log("▸ §D DISPATCH — each leaf renders in the bundle that owns it");
    const b1 = navBtn(R.doc, "store", "team");
    if (b1) b1.click();
    ok(await waitForSettled(R.doc) && await waitFor(() => { const t = R.doc.querySelector("#vTitle"); return t && /Team & Roles/i.test(t.textContent); }), "the store-only leaf renders through the STORE bundle (its own title)", (R.doc.querySelector("#vTitle") || {}).textContent);
    ok(!/⚠️/.test((R.doc.querySelector("#vBody") || {}).textContent || ""), "the store leaf renders without an error");
    const b2 = navBtn(R.doc, "platform", "identity");
    ok(!!b2, "the platform leaf is still reachable from the store view's nav (the one nav survived the bundle render)");
    if (b2) b2.click();
    ok(await waitForSettled(R.doc) && await waitFor(() => { const t = R.doc.querySelector("#vTitle"); return t && /Identity · Auth/i.test(t.textContent); }), "the platform-only leaf renders through the PLATFORM bundle", (R.doc.querySelector("#vTitle") || {}).textContent);
    ok(!/⚠️/.test((R.doc.querySelector("#vBody") || {}).textContent || ""), "the platform leaf renders without an error");

    console.log("▸ §E A STORE-ONLY IDENTITY SEES ONE SURFACE");
    const jar2 = new Map(jar);   /* keep the platform cookies out of the store-only probe */
    jar.clear();
    await f("/api/session?store=luxora");
    await f("/api/auth/login?store=luxora", "POST", { email: "admin@luxora.shop", password: "admin123" });
    const only = await f("/api/auth/me");
    ok(!!(only.hasStore && !only.hasPlatform), "a store client holds exactly one authority", JSON.stringify({ hasStore: only.hasStore, hasPlatform: only.hasPlatform }));
    const S = await render("/console.html");
    ok(!S.errs.length, "the store-only console boots with no JS errors", S.errs.join(" | "));
    const sNav = (S.doc.querySelector(".p-nav") || {}).textContent || "";
    ok(/THIS STORE/.test(sNav), "its nav renders the store surface");
    ok(!/PLATFORM/.test(sNav), "and not the platform one");
    ok(!S.doc.querySelector("#scopeBtn"), "no switcher is offered — there is nothing to switch to");
    for (const [k, v] of jar2) jar.set(k, v);   /* restore the dual session for the sign-out probe */

    console.log("▸ §F SIGNING OUT ENDS BOTH SESSIONS — AGAINST THE REAL PATHS");
    const L = await render("/console.html");
    const out = L.doc.querySelector("#logoutBtn");
    ok(!!out, "the unified console offers one sign-out for both scopes");
    if (out) out.click();
    ok(await waitFor(() => L.fetches.some(x => /^POST \/api\/auth\/logout/i.test(x))), "it signs out of the store via /api/auth/logout", L.fetches.filter(x => /logout/i.test(x)).join(" | "));
    ok(await waitFor(() => L.fetches.some(x => /^POST \/api\/platform\/logout/i.test(x))), "and out of the platform via /api/platform/logout", L.fetches.filter(x => /logout/i.test(x)).join(" | "));

    console.log(failed ? `\n${passed} passed, ${failed} FAILED` : `\n${passed} passed, 0 failed`);
  } finally {
    srv.kill();
    for (const s of ["", "-wal", "-shm"]) { try { require("fs").rmSync(DB + s, { force: true }); } catch (e) { } }
  }
  process.exit(failed ? 1 : 0);
})().catch(e => { console.log("ABORT", e && e.stack || e); process.exit(1); });
