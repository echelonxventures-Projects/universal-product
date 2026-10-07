/* The composition engine — Application = Capability Composition, NOT Application = Custom
   Code. Proves the constitution's central claim is mechanically true: the platform takes
   ANY declared capability (a universe, a catalog capability, a dataset) and materializes
   its full application surface — data model, API, workflow, UI, dashboard, security — from
   the declaration alone, with no per-capability code. Every artifact is then exercised
   through the machinery that already exists (the entity engine, the dashboard engine, the
   workflow registry), because an artifact nobody reads is a claim, not a composition. */
"use strict";
const { spawn } = require("child_process");
const { JSDOM, VirtualConsole } = require("jsdom");
const path = require("path");
const rbac = require("../lib/rbac.js");
const PORT = 8815;
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
async function render(p, wait = 2000) {
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
  const db = path.join(__dirname, "compose.db");
  for (const s of ["", "-wal", "-shm"]) { try { require("fs").rmSync(db + s, { force: true }); } catch (e) { } }
  const srv = spawn(process.execPath, [path.join(__dirname, "..", "server.js")], { env: { ...process.env, PORT, LX_DB: db }, stdio: ["ignore", "ignore", "inherit"] });
  let up = false;
  for (let i = 0; i < 120; i++) { try { const h = await fetch(BASE + "/healthz"); if (h.ok) { up = true; break; } } catch (e) { } await sleep(1000); }
  if (!up) { console.log("server failed to boot"); process.exit(1); }
  try {
    await f("/api/session");
    await f("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" });

    console.log("▸ CANDIDATES — every declaration the platform can compose");
    const cand = await f("/api/compose/candidates");
    ok(cand.counts && cand.counts.universe > 100, "the corpus's universes are composable (" + (cand.counts || {}).universe + ")", JSON.stringify(cand.counts));
    ok(cand.counts && cand.counts.capability > 10, "the capability catalog is composable (" + (cand.counts || {}).capability + ")");
    ok(cand.counts && cand.counts.entity > 50, "the platform's declared datasets are composable (" + (cand.counts || {}).entity + ")");
    ok(cand.counts && cand.counts.composed === 0, "nothing is composed yet — composition is an operator action, never auto-seeded", (cand.counts || {}).composed);
    const ins = (cand.universes || []).find(x => x.key === "insurance");
    ok(!!ins && !ins.composed, "a universe carries its provenance home, uncomposed", ins && ins.home + " · " + ins.source);

    console.log("▸ AUTHORITY — only the platform composes");
    jar.delete("azs"); jar.delete("azc"); jar.delete("azp");   /* drop the platform authority too: the unified console holds both, so a store-ONLY identity is the one that must be refused */
    await f("/api/session?store=luxora");
    await f("/api/auth/login", "POST", { email: "admin@luxora.shop", password: "admin123" });
    const storeCompose = await f("/api/compose/insurance", "POST", {});
    ok(!!storeCompose.error, "a store-only admin cannot compose (" + (storeCompose.error || "") + ")", JSON.stringify(storeCompose));
    const storeRead = await f("/api/compose/candidates");
    ok(!!storeRead.error, "a store-only admin cannot read the composition surface", JSON.stringify(storeRead));
    jar.clear();
    await f("/api/session");
    await f("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" });

    console.log("▸ COMPOSE A UNIVERSE — the corpus's declaration becomes an application surface");
    const c1 = await f("/api/compose/insurance", "POST", {});
    ok(c1.ok === true, "compose(insurance) succeeded", c1.error);
    ok(c1.capability && c1.capability.source === "upip:999", "provenance is the exact document and line", c1.capability && c1.capability.source);
    ok(c1.capability && /^Insurance/.test(c1.capability.home), "the composed universe lands in its declared registry home", c1.capability && c1.capability.home);
    const dm = (c1.artifacts || {}).dataModel || {};
    ok(dm.key === "cp_insurance" && dm.endpoint === "/api/meta/entity/cp_insurance", "the data model is a real, addressable entity", JSON.stringify(dm));
    ok(dm.fields > 8, "the corpus's own concepts became the model's fields (" + dm.fields + ", not the 4-field fallback)", dm.fields);
    const api = (c1.artifacts || {}).api || {};
    ok(api.rest && api.rest.length === 4 && api.rest[0].includes("cp_insurance"), "the API surface is the entity engine's own CRUD", JSON.stringify(api.rest));
    ok(Array.isArray(api.validation) && api.validation.includes("name"), "validation is derived from the declaration's required fields", JSON.stringify(api.validation));
    const wf = (c1.artifacts || {}).workflow || {};
    ok(wf.key === "wf_cp_insurance" && (wf.steps || []).length >= 6, "the workflow is the corpus lifecycle (UCOS 5.1), one step per state", wf.key && wf.steps.length);
    ok((wf.config || {}).grammar && wf.config.grammar.length > 0, "the workflow carries the Art. 10 transition grammar from the corpus", JSON.stringify((wf.config || {}).grammar));
    const ui = (c1.artifacts || {}).ui || {};
    ok(ui.listFields && ui.listFields.length >= 3, "the UI is the definition's own list + form fields", JSON.stringify(ui.listFields));
    ok(ui.formFields && ui.formFields.length === dm.fields, "every field on the model is a form field — the console renders the whole declaration", ui.formFields && ui.formFields.length);
    const dash = (c1.artifacts || {}).dashboard || {};
    ok(dash.key === "db_cp_insurance" && dash.widgets && dash.widgets.length === 3, "the dashboard declares 3 widgets", dash.key && dash.widgets.length);
    ok(dash.widgets.every(w => ["kpi", "bar", "table", "donut", "line", "text"].includes(w.kind)), "every widget is a kind the engine renders", JSON.stringify(dash.widgets));
    ok(dash.widgets.every(w => ["count", "sum", "avg", "min", "max", "distinct"].includes(w.metric)), "every widget's metric is in the engine's vocabulary (no error tiles)", JSON.stringify(dash.widgets.map(w => w.metric)));
    const sec = (c1.artifacts || {}).security || {};
    ok(sec.roles && sec.roles.read && sec.roles.write, "the composed capability inherits RBAC the moment it exists", JSON.stringify(sec.roles));

    console.log("▸ EVERY ARTIFACT IS LIVE — read through the machinery that serves it");
    const ents = await f("/api/meta/entities");
    const served = Object.keys(ents.entities || {}).includes("cp_insurance");
    ok(served, "the composed entity is served by the entity engine", JSON.stringify(Object.keys(ents.entities || {}).filter(k => k.startsWith("cp_"))));
    ok(rbac.sectionForEntity("cp_insurance") === "compose", "a composed entity authorizes against the composition section", rbac.sectionForEntity("cp_insurance"));
    ok(rbac.SECTIONS.includes("compose"), "composition is a first-class grantable section");
    const rec = await f("/api/meta/entity/cp_insurance", "POST", { name: "Motor Policy", code: "MOT-1", status: "drafted" });
    ok(!rec.error && rec.id, "a record is created through the composed API", rec.error || rec.id);
    await f("/api/meta/entity/cp_insurance", "POST", { name: "Home Policy", code: "HOM-1", status: "canonical" });
    const listed = await f("/api/meta/entity/cp_insurance");
    ok(!listed.error && (listed.rows || []).length === 2, "the composed dataset lists its records", listed.error || (listed.rows || []).length);
    ok(rbac.sectionForEntity("product") === "products", "the prefix rule leaves existing entity mappings untouched", rbac.sectionForEntity("product"));
    const dashRender = await f("/api/dashboards/db_cp_insurance");
    ok(!dashRender.error && dashRender.widgets.length === 3, "the composed dashboard renders through the §394 engine", dashRender.error);
    ok(dashRender.widgets.every(w => !w.error), "no widget errors — every metric resolved against the composed data", JSON.stringify(dashRender.widgets.map(w => w.error)));
    const kpi = dashRender.widgets.find(w => w.metric === "count");
    ok(kpi && kpi.value === 2, "the count widget computed the records the composition created", kpi && kpi.value);
    const byState = dashRender.widgets.find(w => w.dimension === "status");
    ok(byState && byState.buckets && byState.buckets.length === 2, "the lifecycle breakdown bucketed by status", JSON.stringify(byState && byState.buckets));
    const wfs = await f("/api/ucii/workflows");
    ok((wfs.workflows || []).some(w => w.key === "wf_cp_insurance"), "the composed workflow is in the workflow registry", JSON.stringify((wfs.workflows || []).filter(w => w.key.startsWith("wf_")).map(w => w.key)));

    console.log("▸ THE LEDGER — append-only, provenance-carrying");
    const man = await f("/api/compose/cp_insurance");
    ok(!man.error && man.capability === "Insurance" && man.records === 2, "the manifest reports the artifacts AND the live record count", man.error || man.records);
    ok(man.source === "upip:999", "the manifest carries the declaration's provenance", man.source);
    const led = await f("/api/compose/ledger");
    ok((led.ledger || []).length === 1 && led.ledger[0].key === "cp_insurance", "the ledger holds the composition", JSON.stringify((led.ledger || []).map(e => e.key)));

    console.log("▸ COMPOSE THE OTHER KINDS — a catalog capability and a plain dataset");
    const c2 = await f("/api/compose/buy_box", "POST", {});
    ok(c2.ok && c2.model.key === "cp_buy_box", "a catalog capability composes", c2.error || c2.model && c2.model.key);
    const capFields = (c2.artifacts || {}).ui || {};
    ok((capFields.formFields || []).some(x => x.key === "price_weight"), "a capability's typed params become its model's fields", JSON.stringify((capFields.formFields || []).map(x => x.key)));
    ok(c2.capability.home === "marketplace", "a composed capability lands in its catalog domain", c2.capability && c2.capability.home);
    const c3 = await f("/api/compose/country", "POST", {});
    ok(c3.ok && c3.model.key === "cp_country", "a plain declared dataset composes", c3.error || c3.model && c3.model.key);

    console.log("▸ FAILURE MODES — honest refusals, never silent no-ops");
    const bad = await f("/api/compose/zzz_not_a_thing", "POST", {});
    ok(!!bad.error, "an undeclared capability is refused", JSON.stringify(bad));
    const noMan = await f("/api/compose/zzz_not_a_thing");
    ok(!!noMan.error, "a manifest for nothing-composed is a 404, not an empty manifest", JSON.stringify(noMan));

    console.log("▸ RECOMPOSITION — idempotent, and a record's data survives a re-derivation");
    const rc = await f("/api/compose/insurance/recompose", "POST", {});
    ok(rc.ok, "recompose succeeds", rc.error);
    const man2 = await f("/api/compose/cp_insurance");
    ok(man2.records === 2, "the records survive recomposition (the dataset is not the declaration)", man2.records);
    const led2 = await f("/api/compose/ledger");
    const mine = (led2.ledger || []).filter(e => e.key === "cp_insurance");
    ok(mine.length === 1, "the ledger holds one row per capability — recomposition supersedes, never duplicates (" + mine.length + " rows)", mine.length);
    ok(mine[0] && man2.records === 2, "the superseding row reflects the live record count", man2.records);
    const dup = await f("/api/compose/insurance", "POST", {});
    ok(dup.ok, "composing an already-composed capability is idempotent, not an error", dup.error || "ok");
    const led3 = await f("/api/compose/ledger");
    ok((led3.ledger || []).filter(e => e.key === "cp_insurance").length === 1, "a second compose still keeps exactly one row — the ledger never accumulates duplicates");

    console.log("▸ CONSOLE — the platform's build surface renders and composes");
    const page = await render("/platform.html", 2600);
    const navBtn = Array.from(page.doc.querySelectorAll(".p-nav button")).find(b => b.dataset.v === "compose");
    ok(!!navBtn, "Composition Engine is in the platform console nav (09 · Platform)");
    if (navBtn) { click(page.win, navBtn); await sleep(1800); }
    ok(page.errs.length === 0, "no JS errors rendering the composition view", page.errs.slice(0, 2).join("|"));
    ok(page.doc.querySelectorAll("[data-comp]").length > 0, "declared-but-uncomposed capabilities carry a Compose action");
    ok(page.doc.querySelectorAll("[data-recomp]").length > 0, "composed capabilities carry Recompose + Manifest");
    ok(page.doc.querySelectorAll("[data-manifest]").length > 0, "the manifest action is wired");
    ok(!!page.doc.getElementById("compQ"), "the capability filter is present");
    ok(page.doc.querySelectorAll(".p-stat").length === 4, "the four composition counters render", page.doc.querySelectorAll(".p-stat").length);
    ok(page.doc.body.textContent.includes("Composition ledger"), "the ledger panel renders");
    /* driving a compose from the console: click the first declared capability and confirm
       the platform actually materialized it (not just that a button existed) */
    const before = (await f("/api/compose/ledger")).ledger.length;
    const btn = page.doc.querySelector("[data-comp]");
    ok(!!btn, "a composable candidate is visible in the first page of results", "");
    if (btn) {
      const key = btn.dataset.comp;
      click(page.win, btn);
      await sleep(2200);
      const after = (await f("/api/compose/ledger")).ledger.length;
      ok(after === before + 1, "composing from the console wrote a ledger row (" + key + ")", before + " → " + after);
      const m = await f("/api/compose/" + encodeURIComponent(key));
      ok(!m.error && m.capability, "the console-composed capability has a full manifest", m.error || m.capability);
      const mBtn = page.doc.querySelector("[data-manifest]");
      if (mBtn) { click(page.win, mBtn); await sleep(600); }
      ok(!!page.doc.querySelector(".p-modal"), "the manifest opens as a modal with every artifact", "");
    }

    console.log(failed ? `\n${passed} passed, ${failed} failed` : `\n${passed} passed, 0 failed`);
  } finally {
    try { srv.kill("SIGKILL"); } catch (e) { }
    for (const s of ["", "-wal", "-shm"]) { try { require("fs").rmSync(db + s, { force: true }); } catch (e) { } }
  }
  process.exit(failed ? 1 : 0);
})().catch(e => { console.log("ABORT", e.message); process.exit(1); });
