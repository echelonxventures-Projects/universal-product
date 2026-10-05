/* User & role management — define roles and their rights (platform-wide and for every
   store's domain) and create users carrying them, all from the platform console.

   Both grant surfaces are DATA in meta_lists, so this proves the management contract:
   a role is created, validated against its surface's real sections, scoped per section,
   edited, and deleted only when nobody holds it — and an operator's version survives a
   reboot (the seed's self-heal never reverts an edit). Users are created INTO a store
   with a role, through the same password policy the storefront enforces, and the
   resulting account really can sign in to that store's console.

   NOTE on DB reads: the server and this process hold separate SQLite connections, and a
   connection opened before the server's first write keeps reading that older WAL
   snapshot. So every assertion is made either through the API (the server's own
   connection) or through a freshly opened connection — never the module's cached one. */
"use strict";
const DB = require("path").join(__dirname, "roles.db");
process.env.LX_DB = DB;   /* before any lib require, so a fresh connection opens this file */
const { spawn } = require("child_process");
const { JSDOM, VirtualConsole } = require("jsdom");
const { DatabaseSync } = require("node:sqlite");
const path = require("path");
const prbac = require("../lib/prbac.js");
const rbac = require("../lib/rbac.js");
const PORT = 8831;
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
/* a brand-new connection per read: the cached one pins a stale snapshot (see header) */
const fresh = (sql, ...p) => { try { return new DatabaseSync(DB, { readOnly: true }).prepare(sql).get(...p) || null; } catch (e) { return null; } };
const freshAll = (sql, ...p) => { try { return new DatabaseSync(DB, { readOnly: true }).prepare(sql).all(...p) || []; } catch (e) { return []; } };
const sleep = ms => new Promise(r => setTimeout(r, ms));
async function render(page, wait = 2000) {
  const errs = [];
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
    } });
  await new Promise(r => setTimeout(r, wait));
  return { doc: dom.window.document, win: dom.window, errs: errs.filter(e => !/css|Could not parse CSS/i.test(e)), dom };
}
const navTo = async (doc, key, ms = 1800) => { const b = [...doc.querySelectorAll(".p-nav button")].find(x => x.dataset.v === key); if (b) b.click(); await sleep(ms); return !!b; };

(async () => {
  for (const s of ["", "-wal", "-shm"]) { try { require("fs").rmSync(DB + s, { force: true }); } catch (e) { } }
  const boot = async () => {
    const srv = spawn(process.execPath, [path.join(__dirname, "..", "server.js")], { env: { ...process.env, PORT, LX_DB: DB }, stdio: ["ignore", "ignore", "inherit"] });
    for (let i = 0; i < 120; i++) { try { if ((await fetch(BASE + "/healthz")).ok) return srv; } catch (e) { } await sleep(500); }
    throw new Error("server failed to boot");
  };
  let srv = await boot();
  try {
    await f("/api/session?store=luxora");
    await f("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" });

    console.log("▸ GATING — role management is a distinct trust");
    const anonSave = await fetch(BASE + "/api/platform/roles", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ key: "rogue", name: "Rogue", sections: { "*": "write" } }) }).then(r => r.json().catch(() => ({})));
    ok(!!anonSave.error, "an unauthenticated role write is refused", anonSave.error);

    console.log("▸ PLATFORM ROLES — define a role and its rights");
    const made = await f("/api/platform/roles", "POST", { key: "photographer", name: "Photographer", desc: "Catalog imagery", sections: { dash: "read", gproducts: "write", gcatalog: "write" } });
    ok(!!made.ok, "the role is created", made.error);
    ok(!!(made.role && made.role.sections.gproducts === "write"), "the grant map is stored as written", JSON.stringify(made.role && made.role.sections));
    const catalog = await f("/api/platform/roles");
    ok(!!catalog.roles.find(r => r.key === "photographer"), "the role appears in the catalog");
    ok(Array.isArray(catalog.sections) && catalog.sections.length > 50, "the surface ships its real section list (" + (catalog.sections || []).length + ")", String(catalog.sections && catalog.sections.length));
    ok(catalog.roles.find(r => r.key === "photographer").sections.dash === "read", "a read grant round-trips");

    console.log("▸ VALIDATION — the section list is the authority on what a grant may name");
    ok(!!(await f("/api/platform/roles", "POST", { key: "Bad Key", name: "Bad", sections: {} })).error, "a key with spaces/uppercase is refused");
    ok(!!(await f("/api/platform/roles", "POST", { key: "noname", sections: {} })).error, "a role without a name is refused");
    ok(!!(await f("/api/platform/roles", "POST", { key: "bogus", name: "Bogus", sections: { no_such_section: "write" } })).error, "a grant for an unknown section is refused");
    ok(!!(await f("/api/platform/roles", "POST", { key: "bogus", name: "Bogus", sections: { dash: "execute" } })).error, "a grant value outside read/write/off is refused");
    ok(!prbac.role("bogus"), "a rejected save leaves no role behind", JSON.stringify(prbac.role("bogus")));

    console.log("▸ EDIT — a save replaces the grant map in full");
    const edited = await f("/api/platform/roles", "POST", { key: "photographer", name: "Photographer", desc: "Catalog imagery", sections: { dash: "write" } });
    ok(!!edited.ok && edited.role.sections.dash === "write" && !("gproducts" in edited.role.sections), "cleared grants are dropped, not merged", JSON.stringify(edited.role && edited.role.sections));
    /* expand() is the grant algebra can()/grant() resolve through — a pure function of
       the stored map, so it is asserted directly rather than via a stale DB lookup */
    const g = prbac.expand(edited.role.sections);
    ok(g.dash === "write" && !("gproducts" in g), "the expanded map carries only the surviving grants", JSON.stringify(g));

    console.log("▸ WILDCARD — '*' sets the default every section inherits, and off beats it");
    const wide = await f("/api/platform/roles", "POST", { key: "wide", name: "Wide", sections: { "*": "read", security: false } });
    const w = prbac.expand(wide.role.sections);
    ok(w.gproducts === "read", "'*' read expands to a section the map never names", JSON.stringify(w.gproducts));
    ok(w.security === false, "an explicit off beats the wildcard", JSON.stringify(w.security));

    console.log("▸ DELETE — guards protect the escape hatch and live assignments");
    ok(!!(await f("/api/platform/roles/owner", "DELETE", {})).error, "the owner role cannot be deleted");
    ok(!!(await f("/api/platform/roles/no_such_role", "DELETE", {})).error, "deleting an unknown role is refused");
    /* a role an operator holds is not removable — reassign first */
    const held = await f("/api/platform/admins", "POST", { name: "Shutter Bug", email: "shutter@luxora.shop", password: "shutter1234", role: "photographer" });
    ok(!!held.ok, "an operator is created carrying the role", held.error);
    const inUse = await f("/api/platform/roles/photographer", "DELETE", {});
    ok(!!inUse.error && /reassign/i.test(inUse.error), "a held role is refused with the reason", inUse.error);
    ok(freshAll("SELECT id FROM platform_admins WHERE role='photographer'").length === 1, "the assignment is what blocks the delete");
    /* the update handler requires name + email alongside the new role */
    const reassigned = await f("/api/platform/admins/" + held.id, "PUT", { name: "Shutter Bug", email: "shutter@luxora.shop", role: "support" });
    ok(!!reassigned.ok, "the operator is reassigned off the role", reassigned.error);
    ok((fresh("SELECT role FROM platform_admins WHERE id=?", held.id) || {}).role === "support", "the reassignment is committed");
    ok(!!(await f("/api/platform/roles/photographer", "DELETE", {})).ok, "once released, the role deletes");
    ok(!prbac.role("photographer"), "and is gone from the catalog");

    console.log("▸ ENFORCEMENT — an operator's role gates their own management");
    await f("/api/platform/roles", "POST", { key: "restricted", name: "Restricted", sections: { dash: "read" } });
    await f("/api/platform/admins", "POST", { name: "No Edit", email: "noedit@luxora.shop", password: "noedit1234", role: "restricted" });
    await f("/api/platform/login", "POST", { email: "noedit@luxora.shop", password: "noedit1234" });
    ok(!!(await f("/api/platform/roles", "POST", { key: "rogue", name: "Rogue", sections: {} })).error, "a role without the roles grant cannot define roles");
    ok(!!(await f("/api/platform/users", "POST", { tenant_id: 1, name: "Rogue", email: "rogue@luxora.shop", password: "rogue1234", role: "customer" })).error, "a role without the users grant cannot create users");
    await f("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" });

    console.log("▸ STAFF ROLES — the store surface, one set applied on every store's domain");
    const sMade = await f("/api/platform/roles/staff", "POST", { key: "visual", name: "Visual Merch", desc: "Storefront imagery", sections: { products: "write", content: "write", orders: "read" } });
    ok(!!sMade.ok, "the staff role is created on the store surface", sMade.error);
    /* the store surface is read through the same cross-store reader the console uses */
    const fan = await f("/api/platform/fanout?path=/api/admin/roles&flat=1");
    ok(!!(fan.merged || {}).roles && fan.merged.roles.some(r => r.key === "visual"), "every store serves the new role", JSON.stringify((fan.merged || {}).roles && fan.merged.roles.length));
    const s = prbac.expand(sMade.role.sections);
    ok(s.content === "write" && !("billing" in s), "the store grant map is stored as written", JSON.stringify(s));
    ok(!!(await f("/api/platform/roles/staff/nosuch", "DELETE", {})).error, "deleting an unknown staff role is refused");
    ok(!!(await f("/api/platform/roles/staff/owner", "DELETE", {})).error, "the store owner role is equally protected");

    console.log("▸ USERS — created into a store, carrying a role");
    const noStore = await f("/api/platform/users", "POST", { name: "Nobody", email: "nobody@luxora.shop", password: "nobody1234", role: "customer" });
    ok(!!noStore.error, "a user without a store is refused", noStore.error);
    ok(!!(await f("/api/platform/users", "POST", { tenant_id: 1, name: "Bad", email: "not-an-email", password: "good1234", role: "customer" })).error, "a malformed email is refused");
    ok(!!(await f("/api/platform/users", "POST", { tenant_id: 1, name: "Bad", email: "weak@luxora.shop", password: "letters", role: "customer" })).error, "the storefront password policy applies");
    ok(!!(await f("/api/platform/users", "POST", { tenant_id: 1, name: "Bad", email: "bad@luxora.shop", password: "good1234", role: "admin", staff_role: "nosuch" })).error, "an unknown staff role is refused");
    const cust = await f("/api/platform/users", "POST", { tenant_id: 1, name: "Alex Rao", email: "alex@luxora.shop", password: "alex1234", role: "customer" });
    ok(!!cust.ok && !!cust.id, "a customer is created in the chosen store", cust.error);
    ok((fresh("SELECT tenant_id, role FROM users WHERE id=?", cust.id) || {}).tenant_id === 1, "the row is scoped to that store");
    const admin = await f("/api/platform/users", "POST", { tenant_id: 1, name: "Sam Lee", email: "sam@luxora.shop", password: "sam12345", role: "admin", staff_role: "visual" });
    ok(!!admin.ok, "a store admin is created with the staff role", admin.error);
    ok((fresh("SELECT staff_role FROM users WHERE id=?", admin.id) || {}).staff_role === "visual", "the staff role is assigned to the account");
    const dup = await f("/api/platform/users", "POST", { tenant_id: 1, name: "Dup", email: "sam@luxora.shop", password: "sam12345", role: "admin" });
    ok(!!dup.error && /already has an account/i.test(dup.error), "the same email on the same store is a conflict", dup.error);
    ok(cust.generated === undefined, "a provided password is not echoed back", JSON.stringify(cust.generated));
    const gen = await f("/api/platform/users", "POST", { tenant_id: 1, name: "Gen Pw", email: "genpw@luxora.shop", role: "customer" });
    ok(!!gen.ok && typeof gen.generated === "string" && gen.generated.length >= 8, "an omitted password is generated and shown once", JSON.stringify(gen.generated));
    /* the same email on a DIFFERENT store is a distinct account — UNIQUE(tenant_id,email) */
    const aurum = fresh("SELECT id FROM tenants WHERE slug='aurum'");
    ok(!!(await f("/api/platform/users", "POST", { tenant_id: aurum.id, name: "Sam Lee", email: "sam@luxora.shop", password: "sam12345", role: "admin", staff_role: "manager" })).ok, "the same email on another store is its own account");

    console.log("▸ STAFF DELETE GUARD — a role a store team holds is not removable");
    const sInUse = await f("/api/platform/roles/staff/visual", "DELETE", {});
    ok(!!sInUse.error && /reassign/i.test(sInUse.error), "the held staff role is refused with the reason", sInUse.error);
    ok(freshAll("SELECT id FROM users WHERE staff_role='visual'").length === 1, "the store assignment is what blocks the delete");

    console.log("▸ SELF-HEAL — an operator's roles survive a reboot (the seed never reverts an edit)");
    srv.kill(); srv = await boot();
    /* the session lives in the DB, so the same cookie still authenticates after restart */
    const after = await f("/api/platform/roles");
    ok(!!after.roles.find(r => r.key === "restricted"), "the operator's platform role survived the reboot");
    ok(after.roles.find(r => r.key === "restricted").sections.dash === "read", "and so did its exact grants");
    const afterStaff = await f("/api/platform/fanout?path=/api/admin/roles&flat=1");
    ok((afterStaff.merged || {}).roles.some(r => r.key === "visual"), "the operator's staff role survived the reboot");
    ok((fresh("SELECT edited FROM meta_lists WHERE name='platformRoles'") || {}).edited === 1, "the row is stamped edited, so the seed leaves it alone");

    console.log("▸ STORE SIGN-IN — a platform-created account really works");
    const storeLogin = await f("/api/auth/login?store=luxora", "POST", { email: "sam@luxora.shop", password: "sam12345" });
    ok(!!(storeLogin.ok && storeLogin.user && storeLogin.user.staff_role === "visual"), "the created admin signs in to the store console with the assigned role", JSON.stringify(storeLogin));
    ok(!!(await f("/api/auth/login?store=luxora", "POST", { email: "alex@luxora.shop", password: "alex1234" })).ok, "the created customer signs in too");
    /* the assigned staff role is what the store console enforces: 'visual' grants no
       team access, so the staff listing is refused while the session is otherwise valid */
    const teamRead = await f("/api/admin/staff");
    ok(!!teamRead.error, "the store role withholds the team section from its own holder", teamRead.error);
    /* re-establish the platform session for the console tests (the two scopes are disjoint) */
    await f("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" });

    console.log("▸ CONSOLE — the roles page manages both surfaces");
    const R = await render("/platform.html", 2600);
    ok(!R.errs.length, "the console boots with no JS errors", R.errs.join(" | "));
    ok(await navTo(R.doc, "roles-admin"), "the Roles leaf is in the nav");
    ok(/Platform roles/.test(R.doc.body.textContent) && /Store staff roles/.test(R.doc.body.textContent), "both role surfaces render");
    ok(!!R.doc.querySelector("[data-rnew]"), "the New role control is present for an operator who may write");
    const before = (await f("/api/platform/roles")).roles.length;
    R.win.document.querySelector("[data-rnew='platform']").click(); await sleep(300);
    const m = R.win.document.getElementById("modal");
    ok(!!m && !!m.querySelector("#rfName"), "the new-role modal opens with the grants editor");
    ok(m.querySelectorAll("[data-sec]").length > 50, "the editor renders one control per section (" + m.querySelectorAll("[data-sec]").length + ")");
    ok(!!m.querySelector("#grWild"), "the wildcard control is present");
    /* type the name and confirm the key derives from it */
    const nameEl = m.querySelector("#rfName");
    nameEl.value = "Console Role";
    nameEl.dispatchEvent(new R.win.Event("input", { bubbles: true }));
    ok(m.querySelector("#rfKey").value === "console_role", "the key is derived from the name", m.querySelector("#rfKey").value);
    m.querySelector("#rfSave").click(); await sleep(1500);
    const afterCreate = (await f("/api/platform/roles")).roles;
    ok(afterCreate.length === before + 1 && !!afterCreate.find(r => r.key === "console_role"), "saving the form creates the role", JSON.stringify(afterCreate.map(r => r.key).slice(-3)));
    ok(afterCreate.find(r => r.key === "console_role").name === "Console Role", "the role's name round-trips");

    console.log("▸ CONSOLE — the users page creates accounts into a store");
    const U = await render("/platform.html", 2600);
    ok(await navTo(U.doc, "users-admin"), "the Users leaf is in the nav");
    ok(/across tenants/.test(U.doc.body.textContent), "the cross-store account table renders");
    ok(!!U.doc.querySelector("[data-unew]"), "the New user control is present");
    ok(U.doc.body.textContent.includes("sam@luxora.shop"), "the API-created admin is visible in the table");
    const ubefore = fresh("SELECT COUNT(*) c FROM users WHERE tenant_id=1").c;
    U.win.document.querySelector("[data-unew]").click(); await sleep(300);
    const um = U.win.document.getElementById("modal");
    ok(!!um && !!um.querySelector("#unTenant"), "the new-user modal opens with a store picker");
    ok(um.querySelector("#unStaffWrap").style.display === "none", "the staff-role picker is hidden for a customer");
    um.querySelector("#unRole").value = "admin";
    um.querySelector("#unRole").dispatchEvent(new U.win.Event("change", { bubbles: true }));
    ok(um.querySelector("#unStaffWrap").style.display !== "none", "the staff-role picker appears for a store admin");
    um.querySelector("#unName").value = "Console User";
    um.querySelector("#unEmail").value = "consoleuser@luxora.shop";
    um.querySelector("#unPw").value = "console1234";
    um.querySelector("#unSave").click(); await sleep(1500);
    const urow = fresh("SELECT role, staff_role FROM users WHERE tenant_id=1 AND email='consoleuser@luxora.shop'");
    ok(!!urow && urow.role === "admin" && urow.staff_role === "manager", "the console-created admin carries the default staff role", JSON.stringify(urow));
    ok(fresh("SELECT COUNT(*) c FROM users WHERE tenant_id=1").c === ubefore + 1, "the account appears in the store's user count");

    R.dom.window.close(); U.dom.window.close();
  } finally {
    srv.kill();
    for (const s of ["", "-wal", "-shm"]) { try { require("fs").rmSync(DB + s, { force: true }); } catch (e) { } }
  }
  console.log(failed ? `\n${passed} passed, ${failed} FAILED` : `\n${passed} passed, 0 failed`);
  process.exit(failed ? 1 : 0);
})();
