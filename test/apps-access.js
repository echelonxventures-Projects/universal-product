/* LUXORA Platform — one console, and access to anything configured is granted from it.
   The old store and platform pages redirect to /console.html in their scope. Anything
   configured after the build — a capability composed into an application, a custom
   entity — becomes its own grantable section ("app_<key>"): the owner reaches it the
   moment it exists, every other role (even an "everything" wildcard role) is refused
   until the app is granted in the console's Roles screen, and one store's own app never
   reaches another store. */
"use strict";
const path = require("path");
const fs = require("fs");
const DB = path.join(__dirname, "apps-access.db");
for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
const PORT = 8880;
Object.assign(process.env, { LX_DB: DB, PORT: String(PORT), LX_LOG: "" });
delete process.env.NODE_ENV;
const BASE = `http://localhost:${PORT}`;
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + (typeof x === "string" ? x : JSON.stringify(x)) : ""))); };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const mk = () => {
  const c = new Map();
  return async (p, m, b) => {
    const o = { method: m || "GET", headers: Object.assign({ Cookie: [...c].map(x => x[0] + "=" + x[1]).join("; ") }, m && m !== "GET" ? { "x-csrf": c.get("azc") || "", Origin: BASE, "Content-Type": "application/json" } : {}) };
    if (b !== undefined) o.body = JSON.stringify(b);
    const r = await fetch(BASE + p, o);
    (r.headers.getSetCookie ? r.headers.getSetCookie() : []).forEach(k => { const kv = k.split(";")[0], i = kv.indexOf("="); c.set(kv.slice(0, i).trim(), kv.slice(i + 1).trim()); });
    let body; try { body = await r.json(); } catch (e) { body = {}; }
    return { status: r.status, body };
  };
};
const sections = me => (me.body.apps || {});

(async () => {
  const silence = console.log; console.log = () => { };
  require("../server.js");
  const db = require("../lib/db.js");
  console.log = silence;
  for (let i = 0; i < 120; i++) { try { if ((await fetch(BASE + "/healthz")).ok) break; } catch (e) { } await sleep(250); }

  try {
    console.log("▸ ONE CONSOLE");
    const loc = async p => (await fetch(BASE + p, { redirect: "manual" })).headers.get("location");
    ok(await loc("/admin.html?store=luxora") === "/console.html?store=luxora&scope=store", "the store console address opens the console in store scope", await loc("/admin.html?store=luxora"));
    ok(await loc("/platform.html") === "/console.html?scope=platform", "the platform console address opens the console in platform scope");
    ok(await loc("/admin.html?store=luxora&token=abc&view=orders") === "/console.html?store=luxora&token=abc&view=orders&scope=store", "a hand-off token and a screen survive the redirect");
    ok((await fetch(BASE + "/console.html")).status === 200, "the console itself serves");

    const P = mk(); await P("/api/session");
    ok((await P("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" })).status === 200, "platform owner signs in");
    const imp = await P("/api/platform/tenants/1/impersonate", "POST", {});
    ok(/^\/console\.html\?store=luxora&scope=store&token=/.test(imp.body.url || ""), "Manage-store hands over into the console, not the old page", imp.body.url);

    const A = mk(); await A("/api/session?store=luxora");
    ok((await A("/api/auth/login?store=luxora", "POST", { email: "admin@luxora.shop", password: "admin123" })).status === 200, "store owner signs in");
    ok(((await A("/api/auth/me?store=luxora")).body.apps || {}).store.length === 0, "before anything is configured, there are no apps");

    console.log("▸ A NEW APP IS COMPOSED");
    const c = await P("/api/compose/insurance", "POST", {});
    ok(c.body.ok === true, "the platform composes an application", c.body.error);
    const pme = await P("/api/auth/me");
    const papp = (sections(pme).platform || []).find(a => a.section === "app_cp_insurance");
    ok(!!papp && /Insurance/.test(papp.label), "the platform owner sees it in the console at once, by name", sections(pme));
    ok((await P("/api/platform/roles")).body.sections.includes("app_cp_insurance"), "it is a grantable section in the platform Roles screen");
    const ame = await A("/api/auth/me?store=luxora");
    ok((sections(ame).store || []).some(a => a.section === "app_cp_insurance"), "the store owner sees it too");
    const roles = (await A("/api/admin/roles?store=luxora")).body;
    ok(roles.sections.includes("app_cp_insurance") && (roles.apps || []).some(a => a.section === "app_cp_insurance" && a.label), "it is a grantable, labelled section in the store Team & Roles screen");
    ok((await A("/api/meta/entity/cp_insurance?store=luxora")).status === 200, "the store owner can open its records");

    console.log("▸ OTHER ROLES WAIT FOR A GRANT");
    ok((await A("/api/admin/roles?store=luxora", "POST", { key: "desk", name: "Desk", sections: { orders: "read" } })).status === 200, "a store role without the app is created");
    ok((await A("/api/admin/staff?store=luxora", "POST", { name: "Dee Desk", email: "dee@luxora.shop", staff_role: "desk", password: "Desk-Pass-123" })).status === 200, "a staff member gets it");
    ok((await A("/api/admin/staff?store=luxora", "POST", { name: "Max Manager", email: "max@luxora.shop", staff_role: "manager", password: "Mgr-Pass-123" })).status === 200, "a manager (an 'everything' wildcard role) is added too");
    const D = mk(); await D("/api/session?store=luxora");
    ok((await D("/api/auth/login?store=luxora", "POST", { email: "dee@luxora.shop", password: "Desk-Pass-123" })).status === 200, "the staff member signs in");
    ok((sections(await D("/api/auth/me?store=luxora")).store || []).length === 0 && (await D("/api/meta/entity/cp_insurance?store=luxora")).status === 403, "without a grant the app is neither listed nor reachable");
    const M = mk(); await M("/api/session?store=luxora");
    await M("/api/auth/login?store=luxora", "POST", { email: "max@luxora.shop", password: "Mgr-Pass-123" });
    ok((await M("/api/meta/entity/cp_insurance?store=luxora")).status === 403, "a wildcard role does not pick up a new app on its own");

    ok((await A("/api/admin/roles?store=luxora", "POST", { key: "desk", name: "Desk", sections: { orders: "read", app_cp_insurance: "read" } })).status === 200, "the owner grants the app (read) in Team & Roles");
    const dme = await D("/api/auth/me?store=luxora");
    ok((sections(dme).store || []).some(a => a.section === "app_cp_insurance"), "the app now appears in the staff member's console");
    ok((await D("/api/meta/entity/cp_insurance?store=luxora")).status === 200, "and its records open");
    ok((await D("/api/meta/entity/cp_insurance?store=luxora", "POST", { name: "Policy X" })).status === 403, "read access does not allow writing");
    ok((await A("/api/admin/roles?store=luxora", "POST", { key: "desk", name: "Desk", sections: { orders: "read", app_gone: "read" } })).status === 200, "a grant naming an app that no longer exists is dropped, not an error");

    console.log("▸ THE SAME ON THE PLATFORM");
    ok((await P("/api/platform/admins", "POST", { name: "Sam Support", email: "sam@ops.example", password: "Support-Pass-123", role: "support" })).status === 200, "a support operator is added");
    const S = mk(); await S("/api/session");
    ok((await S("/api/platform/login", "POST", { email: "sam@ops.example", password: "Support-Pass-123" })).status === 200, "the operator signs in");
    ok((sections(await S("/api/auth/me")).platform || []).length === 0 && (await S("/api/platform/data/cp_insurance")).status === 403, "the operator cannot open the new app until granted");
    const sup = ((await P("/api/platform/roles")).body.roles || []).find(r => r.key === "support");
    ok((await P("/api/platform/roles", "POST", { ...sup, sections: { ...sup.sections, app_cp_insurance: "read" } })).status === 200, "the owner grants it in the platform Roles screen");
    ok((sections(await S("/api/auth/me")).platform || []).some(a => a.section === "app_cp_insurance") && (await S("/api/platform/data/cp_insurance")).status === 200, "the operator now sees and opens it");

    console.log("▸ ONE STORE'S APP STAYS IN THAT STORE");
    db.run("INSERT INTO entity_defs(key,scope,tenant_id,def) VALUES(?,?,?,?)", "zz_private", "tenant", 999, JSON.stringify({ label: "Other store's app", fields: [] }));
    const r2 = (await A("/api/admin/roles?store=luxora")).body;
    ok(!r2.sections.includes("app_zz_private") && !(sections(await A("/api/auth/me?store=luxora")).store || []).some(a => a.key === "zz_private"), "another store's app is not listed or grantable here");
    ok(!(await P("/api/platform/roles")).body.sections.includes("app_zz_private"), "nor is it a platform section");
  } catch (e) {
    failed++; console.error("  ✗ harness error:", e && e.stack || e);
  } finally {
    for (const s of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + s, { force: true }); } catch (e) { } }
  }
  console.log(`\n${passed} passed, ${failed} failed`);
  process.exit(failed ? 1 : 0);
})();
