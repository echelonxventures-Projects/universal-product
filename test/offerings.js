/* What a store offers, on the kernel (lib/offerings.js): every product is an offering of the master,
   whose price history is answerable at any instant, hidden while it is in the bin and archived when
   deleted — whichever screen or engine wrote it. */
"use strict";
const path = require("path"), fs = require("fs"), os = require("os"), { spawn } = require("child_process");
const TMP = path.join(os.tmpdir(), "offerings-" + process.pid + ".db"), PORT = 8961, BASE = "http://localhost:" + PORT;
const wipe = () => { for (const s of ["", "-wal", "-shm"]) try { fs.rmSync(TMP + s, { force: true }); } catch (e) { } };
wipe(); process.env.LX_DB = TMP; process.env.LUXORA_DEMO_BRANDS = "1";
const log = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = log;
const K = require("../lib/kernel.js"), O = require("../lib/offerings.js"), E = require("../lib/entity.js"), G = require("../lib/governance.js"), LC = require("../lib/kernel-lifecycle.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + JSON.stringify(x).slice(0, 300) : ""))); };
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  console.log("▸ EVERY PRODUCT IS AN OFFERING");
  const rows = db.all("SELECT tenant_id, id, uid, title, price FROM products");
  ok(rows.length > 50 && rows.every(r => K.internal.nodeRow(r.uid) && K.internal.nodeRow(r.uid).kind === "offering.listing" && K.internal.nodeRow(r.uid).namespace === "tenant:" + r.tenant_id), "every product is an offering in its store's namespace", rows.length);
  const one = rows[0]; ok(O.at(one.tenant_id, one.id).title === one.title && O.at(one.tenant_id, one.id).price === Number(one.price), "with the offer's facts");
  const seq = K.lastSeq(); ok(O.importRows() === 0 && K.lastSeq() === seq, "a warm pass writes nothing");

  console.log("▸ FROM EVERY SCREEN, WITH HISTORY");
  const srv = spawn(process.execPath, [path.join(__dirname, "..", "server.js")], { env: { ...process.env, PORT, LX_DB: TMP, LX_LOG: "", LX_OFFLINE: "1" }, stdio: ["ignore", "ignore", "inherit"] });
  try {
    for (let i = 0; i < 360; i++) { try { if ((await fetch(BASE + "/healthz")).ok) break; } catch (e) { } await sleep(500); }
    const jar = {}; const call = async (p, m, b) => { const r = await fetch(BASE + p, { method: m || "GET", headers: { "content-type": "application/json", cookie: Object.entries(jar).map(x => x.join("=")).join("; "), ...(jar.azc ? { "x-csrf": jar.azc } : {}) }, body: b ? JSON.stringify(b) : undefined }); r.headers.getSetCookie().forEach(k => { const [a] = k.split(";"); const i = a.indexOf("="); jar[a.slice(0, i)] = a.slice(i + 1); }); return { status: r.status, body: await r.json().catch(() => null) }; };
    await call("/api/session?store=luxora"); await call("/api/auth/login?store=luxora", "POST", { email: "admin@luxora.shop", password: "admin123" });
    const made = await call("/api/admin/products?store=luxora", "POST", { title: "Kernel Kettle", brand: "Ox", dept: "home", price: 40, stock: 5 });
    const pid = made.body && (made.body.id || (made.body.product && made.body.product.id));
    ok(made.status === 200 && O.at(1, pid) && O.at(1, pid).price === 40, "a product made in the console is an offering at once", made);
    const t0 = new Date().toISOString(); await sleep(20);
    await call("/api/admin/products/" + pid + "?store=luxora", "PUT", { price: 35, title: "Kernel Kettle II" });
    await sleep(20); const t1 = new Date().toISOString(); await sleep(20);
    await call("/api/admin/products/" + pid + "?store=luxora", "PUT", { price: 38 });
    ok(O.at(1, pid).price === 38 && O.at(1, pid, { at: t0 }).price === 40 && O.at(1, pid, { at: t1 }).price === 35 && O.at(1, pid, { at: t1 }).title === "Kernel Kettle II", "its price and title at any instant", O.priceHistory(1, pid));
    ok(O.priceHistory(1, pid).map(p => p.price).join() === "40,35,38", "its price history", O.priceHistory(1, pid));
    const before = O.at(1, pid).price; db.run("UPDATE products SET stock=stock+1 WHERE tenant_id=1 AND id=?", pid);
    ok(O.priceHistory(1, pid).length === 3 && before === 38, "stock is not the offer: it makes no version");
    E.updateEntity(1, "product", pid, { title: "Studio Kettle" }); ok(O.at(1, pid).title === "Studio Kettle", "an edit in Data Studio reaches the offering");
    ok(G.trash(1, "product", pid).ok && O.at(1, pid).listed === false, "in the bin it is hidden");
    ok(G.restore(1, "product", pid).ok && O.at(1, pid).listed === true, "restored, it is on sale again");
    const uid = db.get("SELECT uid FROM products WHERE tenant_id=1 AND id=?", pid).uid;
    const del = await call("/api/admin/products/" + pid + "?store=luxora", "DELETE");
    ok(del.status === 200 && !db.get("SELECT id FROM products WHERE tenant_id=1 AND id=?", pid) && LC.nodeState(uid) === "archived" && K.history(uid).length >= 3, "deleted, it is archived with its history", del);
  } catch (e) { failed++; console.log("  ✗ threw: " + (e.stack || e)); }
  finally { srv.kill(); }
  ok(K.verifyEvents().ok, "the record of events is whole");
  console.log(`\n${passed} passed, ${failed} failed`); wipe(); process.exit(failed ? 1 : 0);
})();
