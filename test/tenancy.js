/* Tenancy hierarchy: Platform → Tenant → Org → BU → Brand → Store → Channel.
   Every node is data, the path is materialized, and the tree is the config cascade.
   Proves the engine through the API AND that the console renders it — the tree is the
   tenant's own org, so a store admin must be able to reorganise it with no code change. */
"use strict";
const { spawn } = require("child_process");
const { JSDOM, VirtualConsole } = require("jsdom");
const path = require("path");
const PORT = 8811;
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
  const db = path.join(__dirname, "tenancy.db");
  for (const s of ["", "-wal", "-shm"]) { try { require("fs").rmSync(db + s, { force: true }); } catch (e) { } }
  const srv = spawn(process.execPath, [path.join(__dirname, "..", "server.js")], { env: { ...process.env, PORT, LX_DB: db }, stdio: ["ignore", "ignore", "inherit"] });
  let up = false;
  for (let i = 0; i < 120; i++) { try { const h = await fetch(BASE + "/healthz"); if (h.ok) { up = true; break; } } catch (e) { } await sleep(1000); }
  if (!up) { console.log("server failed to boot"); process.exit(1); }
  try {
    console.log("▸ TENANCY HIERARCHY");
    await f("/api/session?store=luxora");
    const login = await f("/api/auth/login", "POST", { email: "admin@luxora.shop", password: "admin123" });
    ok(login.ok, "store admin login");
    /* an unauthenticated guest may not touch another tenant's org tree */
    const tr = await f("/api/tenancy/tree");
    ok(tr.tree && tr.tree.kind === "tenant", "the tenant root is auto-created on first access", tr.tree && tr.tree.kind);
    ok(Array.isArray(tr.kinds) && tr.kinds.length >= 10, "the node-kind vocabulary is shipped (" + (tr.kinds || []).length + " kinds)", tr.kinds && tr.kinds.join(","));

    /* build a chain: org → BU → brand → store → channel. The path is derived, never sent */
    const org = await f("/api/tenancy/node", "POST", { kind: "organization", name: "Acme Group" });
    ok(!org.error && /acme-group$/.test(org.path), "organisation created at path " + (org.path || org.error), org.error);
    const bu = await f("/api/tenancy/node", "POST", { kind: "business_unit", parent_id: org.id, name: "North America" });
    ok(!bu.error && bu.path === "luxora.acme-group.north-america", "BU nested under the org", bu.path || bu.error);
    const brand = await f("/api/tenancy/node", "POST", { kind: "brand", parent_id: bu.id, name: "Volt" });
    ok(!brand.error && /volt$/.test(brand.path), "brand nested under the BU", brand.path || brand.error);
    const store = await f("/api/tenancy/node", "POST", { kind: "store", parent_id: brand.id, name: "Volt Flagship" });
    ok(!store.error, "store nested under the brand", store.error);
    const chan = await f("/api/tenancy/node", "POST", { kind: "channel", parent_id: store.id, name: "Web" });
    ok(!chan.error, "channel nested under the store", chan.error);

    const t2 = await f("/api/tenancy/tree");
    const names = t2.tree ? JSON.stringify(flattenT(t2.tree).map(n => n.path)) : "[]";
    ok(t2.tree && flattenT(t2.tree).length === 6, "the tree holds all 6 nodes", names);
    ok(t2.tree && t2.tree.children.length === 1, "the root has exactly one top-level org");

    /* the vocabulary is the authority — an unknown kind is refused, never silently coerced */
    const bad = await f("/api/tenancy/node", "POST", { kind: "galaxy", name: "Nope" });
    ok(!!bad.error, "unknown node kind refused", JSON.stringify(bad));
    const dup = await f("/api/tenancy/node", "POST", { kind: "organization", name: "Acme Group" });
    ok(!!dup.error, "a duplicate path is refused (slug collision)", JSON.stringify(dup));

    /* a suspended node blocks creates beneath it — the org's own governance rule */
    const susp = await f("/api/tenancy/node/" + org.id, "PUT", { status: "suspended" });
    ok(!susp.error && susp.status === "suspended", "org suspended", susp.error);
    const underSuspended = await f("/api/tenancy/node", "POST", { kind: "store", parent_id: bu.id, name: "Blocked Store" });
    ok(!!underSuspended.error, "create beneath a suspended chain refused", JSON.stringify(underSuspended));
    await f("/api/tenancy/node/" + org.id, "PUT", { status: "active" });
    const afterResume = await f("/api/tenancy/node", "POST", { kind: "store", parent_id: bu.id, name: "Unblocked Store" });
    ok(!afterResume.error, "create works again once the chain is reactivated", afterResume.error);

    console.log("▸ CONFIG CASCADE — deepest wins, siblings are deep-merged not replaced");
    const K = "checkout.policies";
    const setCfg = (id, v) => f(`/api/tenancy/config/${id}/${K}`, "POST", v);
    const atBrand = await setCfg(brand.id, { returns: 30, currency: "USD" });
    ok(!atBrand.error, "config set on the brand node", atBrand.error);
    const inherited = await f(`/api/tenancy/resolve/${chan.id}?key=${encodeURIComponent(K)}`);
    ok(inherited.resolved && inherited.resolved.returns === 30, "the channel inherits the brand's value up the chain", JSON.stringify(inherited.resolved));
    const atStore = await setCfg(store.id, { currency: "CAD" });
    ok(!atStore.error, "override set on the store node", atStore.error);
    const overridden = await f(`/api/tenancy/resolve/${chan.id}?key=${encodeURIComponent(K)}`);
    ok(overridden.resolved && overridden.resolved.currency === "CAD", "the store's override wins over the brand", JSON.stringify(overridden.resolved));
    ok(overridden.resolved && overridden.resolved.returns === 30, "deep-merge: the untouched sibling key survives the override", JSON.stringify(overridden.resolved));
    const chainPaths = (overridden.chain || []).map(c => c.path);
    ok(chainPaths.length === 6 && chainPaths[0] === "luxora", "resolve reports the full chain root-first (root → channel)", JSON.stringify(chainPaths));

    console.log("▸ DELETION — a node takes its subtree with it, the root is immortal");
    const delSibling = await f("/api/tenancy/node/" + afterResume.id, "DELETE");
    ok(!delSibling.error && delSibling.removed === 1, "a leaf node deletes itself", delSibling.error || delSibling.removed);
    const delBU = await f("/api/tenancy/node/" + bu.id, "DELETE");
    ok(!delBU.error && delBU.removed >= 4, "deleting the BU removes its whole subtree (" + (delBU.removed || 0) + " nodes)", delBU.error);
    const after = await f("/api/tenancy/tree");
    ok(after.tree && flattenT(after.tree).length === 2, "only the root and the org survive", after.tree && JSON.stringify(flattenT(after.tree).map(n => n.path)));
    const delRoot = await f("/api/tenancy/node/" + after.tree.id, "DELETE");
    ok(!!delRoot.error, "the tenant root cannot be deleted", JSON.stringify(delRoot));

    console.log("▸ CONSOLE — the tree renders and the admin can drive it");
    const page = await render("/admin.html", 2200);
    const navBtn = Array.from(page.doc.querySelectorAll(".p-nav button")).find(b => b.dataset.v === "structure");
    ok(!!navBtn, "Org Structure is in the store console nav");
    if (navBtn) { click(page.win, navBtn); await sleep(1500); }
    ok(page.doc.querySelectorAll(".tn-row").length >= 2, "the tree renders one row per node", page.doc.querySelectorAll(".tn-row").length);
    ok(page.errs.length === 0, "no JS errors rendering the hierarchy", page.errs.slice(0, 2).join("|"));
    ok(!!page.doc.querySelector("[data-act='tn-new']"), "the + New node action is present");
    ok(!!page.doc.querySelector("[data-act='tn-toggle']"), "a non-root node carries a suspend/activate toggle");
    /* selecting a node opens the cascade inspector */
    const leaf = page.doc.querySelector(".tn-name");
    if (leaf) { click(page.win, leaf); await sleep(1200); }
    ok(!!page.doc.getElementById("tnKeyIn"), "selecting a node opens the configuration inspector");
    ok(page.doc.querySelectorAll(".p-table").length >= 1, "the inspector renders the per-node chain table");

    console.log(failed ? `\n${passed} passed, ${failed} failed` : `\n${passed} passed, 0 failed`);
  } finally {
    try { srv.kill("SIGKILL"); } catch (e) { }
    /* the main db alone — a SIGKILLed server leaves the WAL/SHM sidecars behind (a clean
       checkpoint removes them; a kill does not), and they would accumulate in test/ */
    for (const s of ["", "-wal", "-shm"]) { try { require("fs").rmSync(db + s, { force: true }); } catch (e) { } }
  }
  process.exit(failed ? 1 : 0);
})().catch(e => { console.log("ABORT", e.message); process.exit(1); });

function flattenT(n, out = []) { out.push(n); (n.children || []).forEach(c => flattenT(c, out)); return out; }
