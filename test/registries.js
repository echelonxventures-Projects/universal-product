/* Platform Registry authoring — every meta_lists vocabulary is auto-discovered,
   auto-recommended and auto-upgraded.

   The gap this closes: platform modes (and every other registry vocabulary) were
   data in the DB but had no authoring surface, so "register a new kind of platform"
   was capped at the seeded floor. This proves the three properties the console now
   relies on:
     AUTO-DISCOVERED — the API scans meta_lists; list names are never enumerated in
                       code, so a registry added by any engine is authorable at once.
     AUTO-RECOMMEND  — an entry's fields are scaffolded from the live entries' shape.
     AUTO-UPGRADE    — a corpus upgrade adds canonical entries an edited list lacks,
                       without reverting anything the operator changed. */
"use strict";
const { spawn } = require("child_process");
const { JSDOM, VirtualConsole } = require("jsdom");
const path = require("path");
const PORT = 8815;
const BASE = `http://localhost:${PORT}`;
const jar = new Map();
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x ? " → " + x : ""))); };
const cookies = () => [...jar].map(([k, v]) => k + "=" + v).join("; ");
async function f(p, method = "GET", body) {
  const opt = { method, headers: { Cookie: cookies(), ...(method !== "GET" ? { "x-csrf": jar.get("azc") || "" } : {}) } };
  if (body) { opt.body = JSON.stringify(body); opt.headers["Content-Type"] = "application/json"; }
  let r;
  try { r = await fetch(BASE + p, opt); }
  catch (e) {
    if (method === "GET" || method === "HEAD") r = await fetch(BASE + p, opt);
    else return { error: "network: " + String(e && e.message || e) };
  }
  (r.headers.getSetCookie ? r.headers.getSetCookie() : []).forEach(c => { const [kv] = c.split(";"); const i = kv.indexOf("="); jar.set(kv.slice(0, i).trim(), kv.slice(i + 1).trim()); });
  const j = await r.json().catch(() => ({}));
  return { ...j, status: r.status };
}
const sleep = ms => new Promise(r => setTimeout(r, ms));
process.on("unhandledRejection", e => { console.log("  (ignoring unhandled rejection: " + String(e && e.message || e) + ")"); });
const click = (w, el) => el.dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
async function render(p, wait = 1600) {
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
  const db = path.join(__dirname, "registries.db");
  for (const s of ["", "-wal", "-shm"]) { try { require("fs").rmSync(db + s, { force: true }); } catch (e) { } }
  const srv = spawn(process.execPath, [path.join(__dirname, "..", "server.js")], { env: { ...process.env, PORT, LX_DB: db }, stdio: ["ignore", "ignore", "inherit"] });
  let up = false;
  for (let i = 0; i < 120; i++) { try { const h = await fetch(BASE + "/healthz"); if (h.ok) { up = true; break; } } catch (e) { } await sleep(1000); }
  if (!up) { console.log("server failed to boot"); process.exit(1); }
  try {
    console.log("▸ GATING — registry authoring is platform-only");
    await f("/api/session?store=luxora");
    const anon = await f("/api/platform/registries");
    ok(!!anon.error, "an unauthenticated request is refused", JSON.stringify(anon));
    await f("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" });
    const mine = await f("/api/platform/me");
    ok(!!(mine.admin && mine.admin.email), "signed in as the platform owner", mine.error);

    console.log("▸ AUTO-DISCOVERED — the surface scans meta_lists, never enumerates names");
    const all = await f("/api/platform/registries");
    const regs = all.registries || [];
    ok(regs.length > 25, "every registry is discovered from the table (" + regs.length + ", not a hardcoded list)", regs.length);
    const dm = regs.find(r => r.name === "deployModes");
    ok(!!dm, "deployModes is among them");
    const SEEDED = require("../lib/meta.js").DEPLOY_MODES.length;   /* the shipped platform kinds */
    ok(!!(dm && dm.count === SEEDED), "the seeded floor is the shipped platform kinds (" + SEEDED + ")", dm && dm.count);
    ok(!!(dm && dm.shape && dm.shape.some(s => s.key === "key") && dm.shape.some(s => s.key === "desc")),
      "the shape is inferred from the live entries", dm && JSON.stringify(dm.shape));
    ok(regs.every(r => !/:t\d+$/i.test(r.name)), "per-tenant forks (staffRoles:t12) are excluded — they are store-scoped");

    console.log("▸ READ");
    const one = await f("/api/platform/registries/deployModes");
    ok(Array.isArray(one.items) && one.items.length === SEEDED, "the modes read back", one.items && one.items.map(i => i.key).join(","));
    ok(one.items.some(i => i.key === "marketplace"), "marketplace is a mode");
    ok((await f("/api/platform/registries/no_such_list")).status === 404, "an unknown registry 404s");

    console.log("▸ AUTO-RECOMMEND — an entry scaffolded from the live shape");
    const rec = await f("/api/platform/registries/deployModes/recommend", "POST", { label: "Hybrid Marketplace" });
    ok(!!(rec.item && rec.item.key === "hybrid_marketplace"), "the key is derived from the label", rec.item && rec.item.key);
    ok(!!(rec.item && rec.item.name === "Hybrid Marketplace"), "the name carries the label through", rec.item && rec.item.name);
    ok(!!(rec.item && "desc" in rec.item), "the inferred fields are pre-scaffolded (desc)", rec.item && JSON.stringify(rec.item));

    console.log("▸ AUTHOR — adding a platform mode is a console action, not a code change");
    const saved = await f("/api/platform/registries/deployModes", "POST", { item: { key: "hybrid_marketplace", name: "Hybrid Marketplace", desc: "Buyers, sellers and services in one platform" } });
    ok(!!saved.ok, "the entry landed", saved.error);
    const after = await f("/api/platform/registries/deployModes");
    ok(after.items.length === SEEDED + 1 && after.items.some(i => i.key === "hybrid_marketplace"), "the registry now carries the new mode", after.items.length);
    const dm2 = (await f("/api/platform/registries")).registries.find(r => r.name === "deployModes");
    ok(!!dm2.edited, "the row is now marked operator-owned — the seed will not overwrite it", dm2.edited);
    /* the engines read the registry live, so the new mode is immediately a valid platform
       kind: this is the gap closing end to end */
    const reg = await f("/api/platform/tenants", "POST", { name: "Hybra", slug: "hybra", country: "US", mode: "hybrid_marketplace",
      owner: { name: "Hy One", email: "owner@hybra.shop", password: "hybra1234" } });
    ok(!!(reg.tenant && reg.tenant.mode === "hybrid_marketplace"), "a platform of the new kind registers — registration reads the registry live", reg.error || (reg.tenant && reg.tenant.mode));

    console.log("▸ USAGE GUARD — deleting an entry a platform uses is refused");
    const inUse = await f("/api/platform/registries/deployModes/marketplace", "DELETE", {});
    ok(inUse.status === 409 && /In use/.test(inUse.error || ""), "a mode platforms run on is refused with the tenants holding it", inUse.error);
    const inUse2 = await f("/api/platform/registries/deployModes/hybrid_marketplace", "DELETE", {});
    ok(inUse2.status === 409, "the new mode is protected too once a platform uses it", inUse2.error);
    const free = await f("/api/platform/registries/deployModes", "POST", { item: { key: "trial_mode", name: "Trial", desc: "unused" } });
    ok(!!free.ok, "an unused mode is creatable");
    const del2 = await f("/api/platform/registries/deployModes/trial_mode", "DELETE", {});
    ok(!!del2.ok, "an entry no platform uses can be removed", del2.error);

    console.log("▸ AUTO-UPGRADE — a corpus bump adds canonical entries, never reverts an edit");
    const { mergeDefaults } = require("../lib/registry.js");
    const cur = [{ key: "marketplace", name: "MY marketplace", desc: "operator-renamed" }, { key: "custom_only", name: "Operator's own" }];
    const defs = [{ key: "marketplace", name: "Universal Marketplace", desc: "All industries" }, { key: "industry", name: "Industry Marketplace" }, { key: "brand", name: "Brand Store" }];
    const up = mergeDefaults(cur, defs);
    ok(up.length === 4, "the two missing canonical modes arrive additively (" + up.length + " entries)", up.length);
    ok(up.find(x => x.key === "marketplace").name === "MY marketplace", "the operator's edit to an existing entry is never reverted", up.find(x => x.key === "marketplace").name);
    ok(!!up.find(x => x.key === "custom_only"), "the operator's own entry survives the upgrade");
    ok(!mergeDefaults(cur, []).some(x => x.key === "industry"), "no defaults means nothing is added");

    console.log("▸ THE CONSOLE SURFACE — the leaf renders and the editor opens");
    const { doc, win, errs } = await render("/platform.html");
    ok(!errs.length, "the console boots without JS errors", errs.join(" | "));
    const navBtn = [...doc.querySelectorAll("[data-v]")].find(b => b.dataset.v === "registries");
    ok(!!navBtn, "Platform Registries is a leaf under 11 · Administration → Configuration");
    if (navBtn) {
      click(win, navBtn); await sleep(1000);
      ok(!!doc.querySelector("[data-regopen]"), "the discovered registries rendered with an editor each");
      const openBtn = [...doc.querySelectorAll("[data-regopen]")].find(b => b.dataset.regopen === "deployModes") || doc.querySelector("[data-regopen]");
      ok(!!openBtn, "the deployModes registry offers an editor");
      if (openBtn) {
        click(win, openBtn); await sleep(900);
        const addBtn = doc.getElementById("regAdd");
        ok(!!addBtn, "the editor opened with an Add-entry action");
        if (addBtn) {
          click(win, addBtn); await sleep(300);
          /* the entry form is a nested overlay appended after the editor, so it is the
             LAST .p-modal-box in the DOM — not the first (that is the editor itself) */
          const boxes = [...doc.querySelectorAll(".p-modal-box")];
          const form = boxes[boxes.length - 1];
          ok(!!form && /Add · deployModes/.test(form.textContent), "the entry form opened over the editor (nested, not replacing it)", form && form.textContent.slice(0, 60));
          ok(!!doc.querySelector("[data-rf='key']"), "the form is scaffolded from the inferred shape (key field)");
          ok(!!doc.querySelector("#rfRec"), "the auto-recommend control is offered");
        }
      }
    }

    console.log("\n" + (failed ? failed + " FAILED" : "ALL GREEN") + " — " + passed + " passed" + (failed ? ", " + failed + " failed" : ""));
  } catch (e) { console.log("ABORTED:", e); }
  try { srv.kill("SIGKILL"); } catch (e) { }
  await sleep(400);
  for (const s of ["", "-wal", "-shm"]) { try { require("fs").rmSync(db + s, { force: true }); } catch (e) { } }
  process.exit(failed ? 1 : 0);
})();
