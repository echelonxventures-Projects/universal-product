/* Verifies the platform console's dataset surface end to end against a live server + DOM:
   the Countries leaf renders the real country registry (not the uv_country universe), the
   gTable toolbar is present, and New / search / import / export actually move records. */
"use strict";
const DB = require("path").join(__dirname, "gtable-test.db");
process.env.LX_DB = DB;
const { spawn } = require("child_process");
const { JSDOM, VirtualConsole } = require("jsdom");
const path = require("path");
const fs = require("fs");
const zlib = require("zlib");
const PORT = 8875;
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
/* read one entry out of the zip the export writes: the workbook's sheet XML is stored
   DEFLATEd, so its contents can only be verified by inflating the raw stream */
function zipEntry(buf, name) {
  const want = Buffer.from(name);
  let i = buf.length - 22;
  while (i > 0 && buf.readUInt32LE(i) !== 0x06054b50) i--;      /* end-of-central-directory */
  if (i <= 0) return null;
  const count = buf.readUInt16LE(i + 10), cdOff = buf.readUInt32LE(i + 16);
  let p = cdOff;
  for (let e = 0; e < count; e++) {
    const nlen = buf.readUInt16LE(p + 28), csize = buf.readUInt32LE(p + 20), off = buf.readUInt32LE(p + 42);
    if (buf.slice(p + 46, p + 46 + nlen).equals(want)) {
      const lhNlen = buf.readUInt16LE(off + 26), start = off + 30 + lhNlen;
      return zlib.inflateRawSync(buf.slice(start, start + csize)).toString("utf8");
    }
    p += 46 + nlen;
  }
  return null;
}
const sleep = ms => new Promise(r => setTimeout(r, ms));
async function waitFor(cond, ms = 9000) {
  for (let i = 0; i < ms / 100; i++) { try { if (cond()) return true; } catch (e) { } await sleep(100); }
  return false;
}
const errs = [];
async function render(page, wait = 6000) {
  const vc = new VirtualConsole();
  vc.on("jsdomError", e => errs.push(String(e.message)));
  vc.on("error", (...a) => errs.push(a.join(" ")));
  const dom = await JSDOM.fromURL(BASE + page, { resources: "usable", runScripts: "dangerously", pretendToBeVisual: true, virtualConsole: vc,
    beforeParse(w) {
      w.fetch = (u, o) => { const url = String(u).startsWith("http") ? String(u) : BASE + String(u);
        const headers = Object.assign({ Cookie: cookies() }, o && o.headers);
        if (o && o.method && o.method !== "GET" && !headers["x-csrf"]) headers["x-csrf"] = jar.get("azc") || "";
        return fetch(url, { ...o, headers }).then(res => { (res.headers.getSetCookie ? res.headers.getSetCookie() : []).forEach(c => { const [kv] = c.split(";"); const i = kv.indexOf("="); jar.set(kv.slice(0, i).trim(), kv.slice(i + 1).trim()); }); return res; }); };
      w.scrollTo = () => { };
      /* jsdom does not implement object URLs — stub them so the export's download path is
         exercised end to end (the fetch itself is real) */
      w.URL.createObjectURL = () => "blob:stub"; w.URL.revokeObjectURL = () => { };
    } });
  await waitFor(() => { const d = dom.window.document;
    const body = d.querySelector("#vBody"), nav = d.querySelector(".p-nav");
    return !!body && !!nav && !/Loading/i.test(body.textContent || "") && !!nav.querySelector("button[data-s]"); }, wait);
  return dom.window.document;
}
const settled = doc => !!doc.querySelector(".p-nav button[data-s]");
const waitForSettled = async (doc, ms = 9000) => waitFor(() => settled(doc), ms);
const click = async (doc, sel, attr) => { const b = doc.querySelector(sel); if (b) b.click(); return !!b; };

(async () => {
  for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
  const boot = async () => {
    const srv = spawn(process.execPath, [path.join(__dirname, "..", "server.js")], { env: { ...process.env, PORT, LX_DB: DB }, stdio: ["ignore", "ignore", "inherit"] });
    for (let i = 0; i < 120; i++) {
      /* healthz answering is not proof OUR server booted: a stale process from a killed run
         holding PORT makes the child die on EADDRINUSE while healthz is answered by that
         stranger — the suite would then test a server it never started */
      if (srv.exitCode !== null) break;
      try { if ((await fetch(BASE + "/healthz")).ok) { await sleep(300); if (srv.exitCode === null) return srv; break; } } catch (e) { }
      await sleep(500);
    }
    throw new Error("the server we spawned did not boot — port " + PORT + " is held by a stale process from a killed run (lsof -iTCP:" + PORT + " to find it, kill the pid, re-run)");
  };
  const srv = await boot();
  try {
    await f("/api/session?store=luxora");
    const plat = await f("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" });
    ok(!!plat.ok, "platform sign-in");
    await f("/api/auth/login?store=luxora", "POST", { email: "admin@luxora.shop", password: "admin123" });

    console.log("▸ §A THE COUNTRIES LEAF RENDERS THE REAL REGISTRY");
    const doc = await render("/console.html");
    ok(await waitForSettled(doc), "the one console boots");
    const btn = [...doc.querySelectorAll(".p-nav button")].find(b => b.dataset.s === "platform" && b.dataset.v === "countries");
    ok(!!btn, "the Countries leaf is in the nav");
    if (btn) btn.click();
    ok(await waitForSettled(doc) && await waitFor(() => /Countries/i.test((doc.querySelector("#vTitle") || {}).textContent || "")), "the Countries view opens", (doc.querySelector("#vTitle") || {}).textContent);
    const bodyTxt = (doc.querySelector("#vBody") || {}).textContent || "";
    ok(/United States/.test(bodyTxt), "the real country rows render (United States), not the uv_country universe", bodyTxt.slice(0, 120));
    ok(!/no per-universe code exists|declared in/.test(bodyTxt), "the universe fall-through is gone");
    ok(!!doc.querySelector("[data-gtable=country]"), "the dataset panel carries the gTable toolbar");
    ok(!!doc.querySelector("[data-gnew=country]"), "+ New is offered (writable dataset)");
    ok(!!doc.querySelector("[data-gexport=country]"), "the single ⇩ Export button is offered");
    ok(!doc.querySelector("[data-gexport=country][data-fmt]"), "the per-format CSV/JSON buttons are gone — one button, a menu of formats");
    ok(!!doc.querySelector("[data-gq=country]"), "a per-table filter is offered");
    const rowsBefore = doc.querySelectorAll("[data-gtable=country] tbody tr").length;
    ok(rowsBefore > 10, "many countries listed (" + rowsBefore + " rows)", "");

    console.log("▸ §B NEW RECORD THROUGH THE FORM");
    ok(await click(doc, "[data-gnew=country]"), "+ New opens the form modal");
    ok(await waitFor(() => !!doc.querySelector("#gfSave")), "the form rendered from the entity's own declaration");
    const codeIn = doc.querySelector("#gf_code"), nameIn = doc.querySelector("#gf_name");
    ok(!!codeIn && !!nameIn, "the required code/name fields are in the form");
    if (codeIn && nameIn) {
      codeIn.value = "ZP"; nameIn.value = "Zephyria";
      doc.querySelector("#gf_currency").value = "ZEP";
      doc.querySelector("#gf_symbol").value = "ⓩ";
      doc.querySelector("#gf_locale").value = "en-ZP";
      doc.querySelector("#gf_decimals").value = "2";
      doc.querySelector("#gfSave").click();
      ok(await waitFor(() => !doc.querySelector("#gfSave")), "the form saved and closed");
      const made = await f("/api/platform/data/country?q=Zephyria");
      ok(!!(made.rows || []).some(r => r.code === "ZP" && r.name === "Zephyria"), "the record was written at platform scope", JSON.stringify(made));
    }

    console.log("▸ §C PER-TABLE FILTER");
    const q = doc.querySelector("[data-gq=country]");
    ok(!!q, "filter input present");
    if (q) {
      q.value = "Zephyria";
      q.dispatchEvent(new doc.defaultView.Event("input", { bubbles: true }));
      ok(await waitFor(() => { const t = doc.querySelector("[data-gtable=country] tbody"); return t && /Zephyria/.test(t.textContent) && t.querySelectorAll("tr").length === 1; }), "the filter narrows the table in place", (doc.querySelector("[data-gtable=country] tbody") || {}).textContent);
      const cnt = doc.querySelector("[data-gtable=country] [data-gcount]");
      ok(!!cnt && /\b1\b/.test(cnt.textContent), "the count follows the filter (" + (cnt && cnt.textContent) + ")");
      q.value = ""; q.dispatchEvent(new doc.defaultView.Event("input", { bubbles: true }));
    }

    console.log("▸ §D IMPORT THROUGH THE MODAL");
    ok(await click(doc, "[data-gimport=country]"), "⇪ Import opens the import modal");
    ok(await waitFor(() => !!doc.querySelector("#giGo")), "the import modal rendered");
    ok(!!doc.querySelector("#giSample"), "the import modal offers a sample file with the dataset's current columns");
    const gi = doc.querySelector("#giBody");
    if (gi) {
      gi.value = "code,name,currency,symbol,locale,decimals\nIM,Importia,IMP,₹,en-IM,2\nBX,,BAD,¥,bx,2";
      doc.querySelector("#giGo").click();
      ok(await waitFor(() => /imported/i.test((doc.querySelector("#giOut") || {}).textContent || "")), "import reported a result", (doc.querySelector("#giOut") || {}).textContent);
      const outTxt = (doc.querySelector("#giOut") || {}).textContent || "";
      ok(/1 imported/.test(outTxt) && /1 rejected/i.test(outTxt), "the good row imported and the bad row was rejected with its row number", outTxt);
      ok(/<td class="num">2<\/td>/.test(doc.querySelector("#giOut").innerHTML) && /Name is required/i.test(doc.querySelector("#giOut").innerHTML), "the rejection names row 2 and why");
    }

    console.log("▸ §E EXPORT — FORMATS, SCOPE AND THE SAMPLE FILE");
    const csv = await fetch(BASE + "/api/platform/data/country/export?format=csv", { headers: { Cookie: cookies(), "x-csrf": jar.get("azc") || "" } });
    ok(csv.status === 200 && /text\/csv/.test(csv.headers.get("content-type") || ""), "CSV export answers 200 as text/csv");
    const csvTxt = await csv.text();
    ok(/^code,name,/.test(csvTxt) && /Importia/.test(csvTxt), "the CSV carries the declared columns and the imported row", csvTxt.split("\n")[0]);
    const j = await f("/api/platform/data/country/export?format=json");
    ok(!!(j.rows || []).length, "JSON export returns rows (" + ((j.rows || []).length) + ")");
    /* the console's format menu is discovered from the registry, so it can never list a
       format the server cannot render (and a new one needs no client change) */
    const fmts = await f("/api/platform/data/country/export?format=formats");
    const fmtKeys = (fmts.formats || []).map(x => x.key);
    ok(["csv", "json", "xlsx", "pdf"].every(k => fmtKeys.includes(k)), "format discovery lists csv/json/xlsx/pdf", JSON.stringify(fmtKeys));
    /* the sample file: this dataset's current columns + one example row, in the exact
       shapes the importer accepts */
    const scsv = await fetch(BASE + "/api/platform/data/country/sample?format=csv", { headers: { Cookie: cookies(), "x-csrf": jar.get("azc") || "" } });
    const scsvTxt = await scsv.text();
    ok(/^code,name,currency,symbol,/.test(scsvTxt), "the CSV sample leads with the entity's own columns", scsvTxt.split("\n")[0]);
    ok(scsvTxt.trim().split("\n").length === 2, "the sample is a header row plus one example row", String(scsvTxt.trim().split("\n").length));
    const sj = await f("/api/platform/data/country/sample?format=json");
    ok(Array.isArray(sj) && sj.length === 1 && "code" in sj[0], "the JSON sample is a one-element array keyed by the entity's columns", JSON.stringify(sj));
    /* xlsx: a real workbook is a ZIP of XML parts, built with zero dependencies */
    const xlsx = await fetch(BASE + "/api/platform/data/country/export?format=xlsx", { headers: { Cookie: cookies(), "x-csrf": jar.get("azc") || "" } });
    const xb = Buffer.from(await xlsx.arrayBuffer());
    ok(xlsx.status === 200 && /spreadsheetml\.sheet/.test(xlsx.headers.get("content-type") || ""), "XLSX export answers 200 as a spreadsheet");
    ok(xb.slice(0, 4).toString("hex") === "504b0304", "the .xlsx body is a ZIP container (PK)", xb.slice(0, 4).toString("hex"));
    ok(xb.includes(Buffer.from("[Content_Types].xml")) && xb.includes(Buffer.from("xl/worksheets/sheet1.xml")), "the workbook's parts are zipped under their OOXML names");
    const sheet = zipEntry(xb, "xl/worksheets/sheet1.xml");
    ok(!!sheet && /<sheetData>/.test(sheet) && /United States/.test(sheet) && /inlineStr/.test(sheet), "the sheet inflates to real worksheet XML with the data as cells", sheet && sheet.slice(0, 80));
    /* pdf: the standard header + trailer, and page objects an reader can resolve */
    const pdf = await fetch(BASE + "/api/platform/data/country/export?format=pdf", { headers: { Cookie: cookies(), "x-csrf": jar.get("azc") || "" } });
    const pb = Buffer.from(await pdf.arrayBuffer());
    ok(pdf.status === 200 && /application\/pdf/.test(pdf.headers.get("content-type") || ""), "PDF export answers 200 as application/pdf");
    ok(pb.slice(0, 5).toString() === "%PDF-" && pb.slice(-5).toString() === "%%EOF", "the PDF is a real PDF (%PDF- header, %%EOF trailer)", pb.slice(-5).toString());
    ok(pb.includes(Buffer.from("/Type /Page")) && pb.includes(Buffer.from("startxref")), "the PDF carries page objects and a cross-reference table");
    /* scope: a row range over the filtered set */
    const rng = await f("/api/platform/data/country/export?format=json&from=1&to=2");
    ok((rng.rows || []).length === 2, "a row range exports exactly rows 1–2", String((rng.rows || []).length));
    /* scope: the visible page, by primary key */
    const ids = await f("/api/platform/data/country/export?format=json&ids=US");
    ok((ids.rows || []).length === 1 && ids.rows[0].code === "US", "the ids scope exports exactly the rows named (the current page)", JSON.stringify(ids.rows || []));
    /* scope: a date window — exercised on an order's created_at, and proven to exclude as
       well as include */
    const tlist = await f("/api/platform/data");
    const lx = (tlist.tenants || []).find(t => t.slug === "luxora");
    if (lx) {
      const tall = await f("/api/platform/data/order/export?format=json&tenant_id=" + lx.id + "&date_col=created_at&date_from=2000-01-01&date_to=2100-01-01");
      const tnone = await f("/api/platform/data/order/export?format=json&tenant_id=" + lx.id + "&date_col=created_at&date_from=2100-01-02&date_to=2101-01-01");
      ok((tall.rows || []).length > 0, "a date window that covers the data includes rows (" + ((tall.rows || []).length) + ")");
      ok((tnone.rows || []).length === 0, "a date window after the data excludes every row");
    }

    console.log("▸ §F DELETE (and its guards)");
    const delBad = await f("/api/platform/data/country/IM", "DELETE", {});
    ok(!!delBad.ok, "an import-created country can be deleted", JSON.stringify(delBad));
    const delGuard = await f("/api/platform/data/country/US", "DELETE", {});
    ok(!!delGuard.error && /(provider|store serves this country)/i.test(delGuard.error), "a country in use is refused with an actionable reason", JSON.stringify(delGuard));
    const left = await f("/api/platform/data/country?q=Zephyria");
    ok((left.rows || []).length === 1, "Zephyria remains for the cleanup");

    console.log("▸ §G A UNIVERSE LEAF IS OPERABLE TOO (uv_* JSON storage)");
    const uni = [...doc.querySelectorAll(".p-nav button")].find(b => b.dataset.s === "platform" && b.dataset.v === "universes");
    if (uni) uni.click();
    ok(await waitForSettled(doc), "the Universes view opens");
    /* create directly through the endpoint (the form path is already proven) and confirm it
       appears in the universe's dataset table, then remove it again */
    const made = await f("/api/platform/data/uv_country", "POST", { name: "Console Probe Nation", code: "CPN", status: "proposed" });
    ok(!!made.id, "a uv_country record was created at platform scope", JSON.stringify(made));
    const list = await f("/api/platform/data/uv_country");
    ok((list.rows || []).some(r => r.name === "Console Probe Nation"), "the universe reader lists it");
    const gone = await f("/api/platform/data/uv_country/" + made.id, "DELETE", {});
    ok(!!gone.ok, "the universe record is deleted", JSON.stringify(gone));

    console.log("▸ §H THE EXPORT MENU — ONE BUTTON, EVERY OPTION");
    /* back to a dataset leaf so the gTable toolbar is on the page */
    const cbtn = [...doc.querySelectorAll(".p-nav button")].find(b => b.dataset.s === "platform" && b.dataset.v === "countries");
    if (cbtn) cbtn.click();
    ok(await waitForSettled(doc) && await waitFor(() => !!doc.querySelector("[data-gexport=country]")), "a dataset leaf carries the single ⇩ Export button");
    ok(await click(doc, "[data-gexport=country]"), "⇩ Export opens the menu");
    ok(await waitFor(() => !!doc.querySelector("[data-gmenu] #gxGo")), "the menu rendered (formats fetched from the registry)");
    const mfmts = [...doc.querySelectorAll("[data-gmenu] [data-gfmt]")].map(b => b.dataset.gfmt);
    ok(["csv", "json", "xlsx", "pdf"].every(k => mfmts.includes(k)), "the menu lists every registered format, discovered not hardcoded", JSON.stringify(mfmts));
    const scopes = [...doc.querySelectorAll("[data-gmenu] input[name=gscope]")].map(i => i.value);
    ok(["all", "page", "range", "date"].every(s => scopes.includes(s)), "the menu offers all four scopes (all / current page / range / date)", JSON.stringify(scopes));
    ok(!!doc.querySelector("#gxFrom") && !!doc.querySelector("#gxTo") && !!doc.querySelector("#gxCol"), "the range and date scope controls rendered");
    /* pick xlsx + the current page, then download: the menu closes once the export starts */
    const xbtn = doc.querySelector('[data-gmenu] [data-gfmt=xlsx]');
    if (xbtn) xbtn.click();
    const pg = doc.querySelector('[data-gmenu] input[name=gscope][value=page]');
    if (pg) pg.checked = true;
    const go = doc.querySelector("#gxGo");
    if (go) go.click();
    ok(await waitFor(() => !doc.querySelector("[data-gmenu]"), 8000), "the xlsx export of the current page downloaded and the menu closed");

    ok(!errs.some(e => !/css|Could not parse CSS|Not implemented/i.test(e)), "no JS errors", errs.join(" | "));
    console.log(failed ? `\n${passed} passed, ${failed} FAILED` : `\n${passed} passed, 0 failed`);
  } finally {
    srv.kill();
    for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
    process.exit(failed ? 1 : 0);
  }
})().catch(e => { console.log("ABORT", e && e.stack || e); process.exit(1); });
