/* LUXORA Platform - the surge-zone authoring surface (store console · Rides & Dispatch).
   A zone used to be creatable only through POST /api/admin/mobility/zones — the table
   rendered read-only. This drives the form end to end: open the modal, author a zone,
   pause it, edit it, and confirm the gating follows the dynamic_pricing atom. */
"use strict";

const { spawn } = require("child_process");
const { JSDOM, VirtualConsole } = require("jsdom");
const path = require("path");
const fs = require("fs");

const PORT = 8791;
const BASE = `http://localhost:${PORT}`;
const jar = new Map();
let passed = 0, failed = 0;
function ok(c, n, x) { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x ? "  → " + x : ""))); }
function cookieHeader() { return [...jar].map(([k, v]) => k + "=" + v).join("; "); }
async function f(p, method = "GET", body) {
  const opt = { method, headers: { Cookie: cookieHeader(), ...(method !== "GET" ? { "x-csrf": jar.get("azc") || "" } : {}) } };
  if (body) { opt.body = JSON.stringify(body); opt.headers["Content-Type"] = "application/json"; }
  const r = await fetch(BASE + p, opt);
  (r.headers.getSetCookie ? r.headers.getSetCookie() : []).forEach(c => {
    const [kv] = c.split(";"); const i = kv.indexOf("=");
    const k = kv.slice(0, i).trim(), v = kv.slice(i + 1).trim();
    if (k === "azs" && jar.has("azs") && v === jar.get("azs")) return;
    jar.set(k, v);
  });
  return r.json().catch(() => ({}));
}
async function render(p, wait = 1800) {
  const vc = new VirtualConsole(); const errs = [];
  vc.on("jsdomError", e => errs.push(String(e.message)));
  vc.on("error", (...a) => errs.push(a.join(" ")));
  const dom = await JSDOM.fromURL(BASE + p, {
    resources: "usable", runScripts: "dangerously", pretendToBeVisual: true, virtualConsole: vc,
    beforeParse(w) {
      w.fetch = (u, o) => {
        const url = String(u).startsWith("http") ? String(u) : BASE + String(u);
        const headers = Object.assign({ Cookie: cookieHeader() }, o && o.headers,
          (o && o.method && o.method !== "GET" && !(o.headers && (o.headers["x-csrf"] || o.headers["X-CSRF"]))) ? { "x-csrf": jar.get("azc") || "" } : {});
        return fetch(url, { ...o, headers }).then(res => {
          (res.headers.getSetCookie ? res.headers.getSetCookie() : []).forEach(c => {
            const [kv] = c.split(";"); const i = kv.indexOf("="); const k = kv.slice(0, i).trim(), v = kv.slice(i + 1).trim();
            if (k === "azs" && jar.has("azs")) return;
            jar.set(k, v);
          });
          return res;
        });
      };
      w.scrollTo = () => { };
    }
  });
  await new Promise(r => setTimeout(r, wait));
  return { doc: dom.window.document, win: dom.window, errs: errs.filter(e => !/css|Could not parse CSS/i.test(e)) };
}
const click = (w, el) => el.dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const dbBase = path.join(__dirname, "zone-form.db");
  for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(dbBase + s, { force: true }); } catch (e) { } }
  const srv = spawn(process.execPath, [path.join(__dirname, "..", "server.js")],
    { env: { ...process.env, PORT, LX_DB: dbBase }, stdio: ["ignore", "ignore", "inherit"] });
  let up = false;
  for (let i = 0; i < 120; i++) { try { if ((await fetch(BASE + "/healthz")).ok) { up = true; break; } } catch (e) { } await sleep(1000); }
  if (!up) { console.log("  ⚠ server never answered /healthz"); }

  try {
    await f("/api/session");
    await f("/api/auth/login", "POST", { email: "admin@luxora.shop", password: "admin123" });
    /* the whole surface is inert until the atoms are on — enable both before the console
       loads so the nav and the surge card render the live composition */
    await f("/api/capabilities/enable", "POST", { capability: "ride_hailing", tenant_id: 1 });
    await f("/api/capabilities/enable", "POST", { capability: "dynamic_pricing", tenant_id: 1 });

    const page = await render("/admin.html");
    ok(page.errs.length === 0, "console boots without JS errors", page.errs.slice(0, 2).join("|"));
    const ridesNav = [...page.doc.querySelectorAll(".p-nav button")].find(b => b.dataset.v === "rides");
    ok(!!ridesNav, "the Mobility nav appears once ride_hailing is on");
    click(page.win, ridesNav); await sleep(1200);

    ok(!!page.doc.querySelector("[data-act='mob-new-zone']"), "the surge card offers ＋ New zone");
    ok(page.doc.querySelectorAll(".a-table th").length > 0 && /state/.test(page.doc.body.textContent), "the zone table renders");

    /* author a zone through the modal — the engine upserts exactly these fields */
    click(page.win, page.doc.querySelector("[data-act='mob-new-zone']")); await sleep(400);
    const box = page.doc.querySelector("#modal .p-modal-box");
    ok(!!box && /New surge zone/.test(box.textContent), "the zone modal opens", box && box.textContent.slice(0, 30));
    page.doc.getElementById("znName").value = "Stadium event";
    page.doc.getElementById("znKind").value = "event";
    page.doc.getElementById("znMult").value = "2.25";
    page.doc.getElementById("znRad").value = "4";
    page.doc.getElementById("znLat").value = "40.75";
    page.doc.getElementById("znLng").value = "-73.99";
    click(page.win, page.doc.getElementById("znSave")); await sleep(1500);
    const made = await f("/api/admin/mobility");
    const z = (made.zones || []).find(x => x.name === "Stadium event");
    ok(!!z && z.multiplier === 2.25 && z.kind === "event" && z.radius_km === 4 && z.active === 1,
      "the authored zone persisted with its kind, multiplier, radius and active state", JSON.stringify(z));
    ok(!!z && z.center_lat === 40.75 && z.center_lng === -73.99, "the coordinates round-trip");

    /* pause it from the row — the toggle must carry the whole row back or the upsert
       flattens the multiplier and the coords to their defaults */
    const pauseBtn = [...page.doc.querySelectorAll("[data-act='mob-toggle-zone']")]
      .find(b => String(b.dataset.id) === String(z && z.id));
    ok(!!pauseBtn && /Pause/.test(pauseBtn.textContent), "an active zone shows Pause");
    click(page.win, pauseBtn); await sleep(1500);
    const afterPause = (await f("/api/admin/mobility")).zones.find(x => x.id === z.id);
    ok(!!afterPause && afterPause.active === 0 && afterPause.multiplier === 2.25,
      "pausing flips active and keeps the multiplier intact", JSON.stringify(afterPause));

    /* edit it — the modal must be pre-filled, and a changed multiplier must land */
    const editBtn = [...page.doc.querySelectorAll("[data-act='mob-edit-zone']")]
      .find(b => String(b.dataset.id) === String(z.id));
    click(page.win, editBtn); await sleep(400);
    const ebox = page.doc.querySelector("#modal .p-modal-box");
    ok(!!ebox && /Stadium event/.test(ebox.textContent), "the edit modal opens for the right zone");
    ok(page.doc.getElementById("znMult").value === "2.25" && page.doc.getElementById("znKind").value === "event",
      "the edit form is pre-filled", page.doc.getElementById("znMult") && page.doc.getElementById("znMult").value);
    page.doc.getElementById("znMult").value = "3.1";
    click(page.win, page.doc.getElementById("znSave")); await sleep(1500);
    const afterEdit = (await f("/api/admin/mobility")).zones.find(x => x.id === z.id);
    ok(!!afterEdit && afterEdit.multiplier === 3.1 && afterEdit.active === 0,
      "an edit updates the multiplier without touching the paused state", JSON.stringify(afterEdit));

    /* the atom gates the surface: switch dynamic_pricing off and both the button and the
       API must refuse */
    await f("/api/capabilities/disable", "POST", { capability: "dynamic_pricing", tenant_id: 1 });
    const page2 = await render("/admin.html");
    const ridesNav2 = [...page2.doc.querySelectorAll(".p-nav button")].find(b => b.dataset.v === "rides");
    click(page2.win, ridesNav2); await sleep(1200);
    ok(!page2.doc.querySelector("[data-act='mob-new-zone']"), "with the atom off the zone authoring is withdrawn");
    const refused = await f("/api/admin/mobility/zones", "POST", { name: "Should not save", multiplier: 9 });
    ok(!!refused.error, "the API refuses a zone while dynamic_pricing is off", refused.error);
  } catch (e) { console.log("  ⚠ " + e.message); }
  srv.kill();
  console.log(`\n${passed} passed, ${failed} failed`);
  process.exit(failed ? 1 : 0);
})();
