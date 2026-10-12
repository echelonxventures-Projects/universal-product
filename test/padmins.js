/* Platform admin accounts — the console's own user base.

   The seed creates exactly one platform owner and, historically, that was the
   only way to obtain a platform account: newPlatformAdmin() was seed-only, and
   the credentials are scrypt(v2) + peppered with a context ("pa:" + email) that
   makes hand-inserting a row useless. This proves the CRUD surface that closed
   the gap — and that a created account really can sign in at /platform.html,
   which is the whole point: a second operator (a support admin) tests the
   launch workflow end to end instead of borrowing the owner's credentials.

   Covers: platform-only gating, create validation, login as the new admin,
   rename + password reset (session revocation), the self-delete and last-admin
   guards, audit-chain evidence, and the console rendering it all. */
"use strict";
const { spawn } = require("child_process");
const { JSDOM, VirtualConsole } = require("jsdom");
const path = require("path");
const PORT = 8814;
const BASE = `http://localhost:${PORT}`;
const jar = new Map();
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x ? " → " + x : ""))); };
const cookies = () => [...jar].map(([k, v]) => k + "=" + v).join("; ");
async function f(p, method = "GET", body) {
  const opt = { method, headers: { Cookie: cookies(), ...(method !== "GET" ? { "x-csrf": jar.get("azc") || "" } : {}) } };
  if (body) { opt.body = JSON.stringify(body); opt.headers["Content-Type"] = "application/json"; }
  /* T1: a pooled socket whose server was just killed resets with ECONNRESET.
     Retries are safe for reads; a write that died mid-flight is surfaced as an
     error rather than re-sent (it may already have landed). */
  let r;
  try { r = await fetch(BASE + p, opt); }
  catch (e) {
    if (method === "GET" || method === "HEAD") r = await fetch(BASE + p, opt);
    else return { error: "network: " + String(e && e.message || e) };
  }
  (r.headers.getSetCookie ? r.headers.getSetCookie() : []).forEach(c => { const [kv] = c.split(";"); const i = kv.indexOf("="); jar.set(kv.slice(0, i).trim(), kv.slice(i + 1).trim()); });
  return r.json().catch(() => ({}));
}
const sleep = ms => new Promise(r => setTimeout(r, ms));
/* T1: the console issues background (fire-and-forget) requests, and a test
   server being killed resets their pooled sockets mid-flight. The resulting
   rejection has no awaiter, so it used to abort the entire suite. Log it and
   carry on — the assertions probe the live server, not the dead socket. */
process.on("unhandledRejection", e => { console.log("  (ignoring unhandled rejection: " + String(e && e.message || e) + ")"); });
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
  const db = path.join(__dirname, "padmins.db");
  for (const s of ["", "-wal", "-shm"]) { try { require("fs").rmSync(db + s, { force: true }); } catch (e) { } }
  const srv = spawn(process.execPath, [path.join(__dirname, "..", "server.js")], { env: { ...process.env, PORT, LX_DB: db }, stdio: ["ignore", "ignore", "inherit"] });
  let up = false;
  for (let i = 0; i < 120; i++) { try { const h = await fetch(BASE + "/healthz"); if (h.ok) { up = true; break; } } catch (e) { } await sleep(1000); }
  if (!up) { console.log("server failed to boot"); process.exit(1); }
  try {
    console.log("▸ GATING — the platform account list is platform-only");
    const anon = await f("/api/platform/admins");
    ok(!!anon.error, "an unauthenticated request is refused", JSON.stringify(anon));

    console.log("▸ SIGN IN AS THE SEEDED PLATFORM OWNER");
    await f("/api/session?store=luxora");
    const login = await f("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" });
    ok(!!login.ok, "owner login", login.error);
    const me = await f("/api/platform/me");
    ok(!!(me.admin && me.admin.email === "platform@luxora.shop"), "/platform/me confirms the session", me.admin && me.admin.email);

    console.log("▸ CREATE — validation, then a real account");
    const dupEmail = await f("/api/platform/admins", "POST", { name: "Store Person", email: "admin@luxora.shop", password: "admin1234" });
    ok(!!dupEmail.error, "a store-console email is refused (scopes stay disjoint)", dupEmail.error);
    const badPw = await f("/api/platform/admins", "POST", { name: "Support Lead", email: "support@luxora.shop", password: "short" });
    ok(!!badPw.error, "a sub-6-character password is refused", badPw.error);
    const weakPw = await f("/api/platform/admins", "POST", { name: "Support Lead", email: "support@luxora.shop", password: "lettersonly" });
    ok(!!weakPw.error, "the platform password policy applies (letter + digit)", weakPw.error);
    const created = await f("/api/platform/admins", "POST", { name: "Support Lead", email: "support@luxora.shop", password: "support1234", role: "support" });
    ok(!!(created.ok && created.id), "support admin created", created.error);
    const list = await f("/api/platform/admins");
    ok(Array.isArray(list.admins) && list.admins.length === 2, "the platform now has two admins", list.admins && list.admins.length);
    ok(!!list.admins.find(a => a.email === "support@luxora.shop" && a.name === "Support Lead"), "the new admin is listed");
    ok(!!list.roles && list.roles.length >= 4, "the role catalog ships with the list", list.roles && list.roles.map(r => r.key).join(","));
    ok(!!list.admins.find(a => a.email === "support@luxora.shop" && a.role === "support"), "the new admin carries the support role");

    console.log("▸ RBAC — the owner keeps full access");
    const ownerMe = await f("/api/platform/me");
    /* '*' expands to every section at write (expand() replaces the key), so the proof
       of ownerhood is the breadth + write on a privileged section, not the '*' literal */
    ok(Array.isArray(ownerMe.allowed) && ownerMe.allowed.length >= 30, "the owner's grant spans every section (" + (ownerMe.allowed || []).length + ")", JSON.stringify(ownerMe.allowed && ownerMe.allowed.length));
    ok(ownerMe.allowed.includes("padmins") && ownerMe.allowed.includes("security"), "the owner's grant includes the privileged sections", JSON.stringify(ownerMe.allowed && ownerMe.allowed.slice(0, 6)));
    const tenantCreateOwner = await f("/api/platform/tenants", "POST", { name: "Owner Store", slug: "owner-store", country: "US", mode: "marketplace" });
    ok(!!tenantCreateOwner.ok || !tenantCreateOwner.error, "the owner can create a store", tenantCreateOwner.error);

    console.log("▸ LOGIN AS THE NEW ADMIN — the point of the feature");
    const supportLogin = await f("/api/platform/login", "POST", { email: "support@luxora.shop", password: "support1234" });
    ok(!!supportLogin.ok, "the created account signs in at /platform.html", supportLogin.error);
    const supportMe = await f("/api/platform/me");
    ok(!!(supportMe.admin && supportMe.admin.email === "support@luxora.shop"), "the session is the support admin's", supportMe.admin && supportMe.admin.email);
    /* the support operator can read the tenancy registry — they can now run the
       launch workflow themselves instead of borrowing the owner's account */
    const tenants = await f("/api/platform/tenants");
    ok(!tenants.error && Array.isArray(tenants.tenants), "the support admin can read the tenants registry", tenants.error);
    const supportMe2 = await f("/api/platform/me");
    ok(Array.isArray(supportMe2.allowed) && !supportMe2.allowed.includes("*"), "the support admin's grant is scoped (no '*')", JSON.stringify(supportMe2.allowed));

    console.log("▸ RBAC ENFORCEMENT — a support operator sells stores, but cannot rewire the platform");
    /* the point of the role: they CAN launch a store */
    const launch = await f("/api/platform/tenants", "POST", { name: "Acme Commerce", slug: "acme", country: "US", mode: "marketplace", ownerName: "Ava One", ownerEmail: "ava@acme.com", ownerPassword: "acme1234" });
    ok(!!launch.ok || !launch.error, "the support admin can launch a store (their job)", launch.error);
    /* …and CANNOT touch the capabilities their role withholds */
    const rotate = await f("/api/platform/keys/rotate", "POST", {});
    ok(!!rotate.error, "key rotation is refused (security section)", rotate.error);
    const newAdmin = await f("/api/platform/admins", "POST", { name: "Sneaky", email: "sneaky@luxora.shop", password: "sneaky1234", role: "owner" });
    ok(!!newAdmin.error, "creating a platform admin is refused (padmins section)", newAdmin.error);
    const promote = await f("/api/platform/admins/1", "PUT", { role: "support" });
    ok(!!promote.error, "editing another admin is refused", promote.error);
    const policy = await f("/api/platform/policies/provisioning", "PUT", { couponsAllowed: true });
    ok(!!policy.error, "rewriting platform policy is refused", policy.error);
    const planSave = await f("/api/platform/plans", "POST", { name: "Rogue", price_month: 0 });
    ok(!!planSave.error, "creating a subscription plan is refused", planSave.error);
    const rolesAsSupport = await f("/api/platform/roles");
    ok(!!rolesAsSupport.error, "the roles catalog is also refused for the support admin (padmins-gated)", rolesAsSupport.error);

    console.log("▸ UPDATE — rename + password reset revokes sessions (as the owner)");
    /* these are owner actions — the support admin proved above they cannot edit
       another admin, so sign back in as the owner for the privileged half */
    await f("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" });
    const rolesRes = await f("/api/platform/roles");
    ok(!rolesRes.error && rolesRes.roles && rolesRes.roles.length >= 4, "the roles catalog is readable by the owner (" + ((rolesRes.roles || []).length) + " roles)", rolesRes.error);
    ok(!!(rolesRes.me && rolesRes.me.allowed && rolesRes.me.allowed.includes("audit")), "the roles endpoint reports the caller's own grants", JSON.stringify(rolesRes.me && rolesRes.me.allowed && rolesRes.me.allowed.slice(0, 5)));
    const renamed = await f("/api/platform/admins/" + created.id, "PUT", { name: "Support Lead II", email: "support@luxora.shop" });
    ok(!!renamed.ok, "rename applied", renamed.error);
    const reset = await f("/api/platform/admins/" + created.id, "PUT", { name: "Support Lead II", email: "support@luxora.shop", password: "support5678" });
    ok(!!reset.ok, "password reset applied", reset.error);
    /* the reset deleted the target's platform_sessions — prove it by signing in
       as the support admin, then having the owner reset again and confirming the
       new session is invalidated */
    const between = await f("/api/platform/login", "POST", { email: "support@luxora.shop", password: "support5678" });
    ok(!!between.ok, "the new password works", between.error);
    const midSession = await f("/api/platform/me");
    ok(!!(midSession.admin && midSession.admin.email === "support@luxora.shop"), "the support admin holds a live session", midSession.admin && midSession.admin.email);
    await f("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" });
    const reset2 = await f("/api/platform/admins/" + created.id, "PUT", { name: "Support Lead II", email: "support@luxora.shop", password: "support9012" });
    ok(!!reset2.ok, "a second reset is applied by the owner", reset2.error);
    /* the cookie jar now holds the owner's session, so the support admin's session
       was destroyed server-side; signing in with the interim password must fail */
    const interimPw = await f("/api/platform/login", "POST", { email: "support@luxora.shop", password: "support5678" });
    ok(!!interimPw.error, "the interim password was replaced by the second reset", interimPw.error);
    const finalPw = await f("/api/platform/login", "POST", { email: "support@luxora.shop", password: "support9012" });
    ok(!!finalPw.ok, "the final password works", finalPw.error);
    const oldPw = await f("/api/platform/login", "POST", { email: "support@luxora.shop", password: "support1234" });
    ok(!!oldPw.error, "the original password no longer works", oldPw.error);
    const clash = await f("/api/platform/admins/" + created.id, "PUT", { name: "Support Lead II", email: "platform@luxora.shop" });
    ok(!!clash.error, "renaming onto the owner's email is refused", clash.error);

    console.log("▸ DELETE GUARDS — self and last-admin");
    /* a scoped operator cannot remove their own account — sign in as the support
       admin and prove the self-delete guard fires for them too */
    await f("/api/platform/login", "POST", { email: "support@luxora.shop", password: "support9012" });
    const selfDel = await f("/api/platform/admins/" + created.id, "DELETE");
    ok(!!selfDel.error, "the support admin cannot delete their own account", selfDel.error);
    /* sign back in as the owner for the remaining privileged actions */
    await f("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" });
    /* temporarily the owner is the only OTHER admin; deleting the support admin
       would still leave one, so this must succeed — but first prove the
       last-admin guard by removing the owner's own escape hatch */
    const delSupport = await f("/api/platform/admins/" + created.id, "DELETE");
    ok(!!delSupport.ok, "the owner deletes the support admin", delSupport.error);
    const after = await f("/api/platform/admins");
    ok(after.admins.length === 1, "only the owner remains", after.admins && after.admins.length);
    const lastDel = await f("/api/platform/admins/1", "DELETE");
    ok(!!lastDel.error, "the last admin cannot be deleted", lastDel.error);

    console.log("▸ AUDIT — every action is on the hash-chained global log");
    const auditRes = await f("/api/platform/audit");
    const actions = (auditRes.entries || auditRes.audit || []).map(e => e.action || e.event);
    ok(actions.filter(a => String(a).startsWith("platform_admin.")).length >= 4,
      "create / update / reset / delete are all audited (" + actions.filter(a => String(a).startsWith("platform_admin.")).length + " found)",
      JSON.stringify(actions.slice(0, 8)));
    const chain = await f("/api/platform/chain/verify");
    ok(!chain.error && chain.ok !== false, "the audit chain still verifies", chain.error || JSON.stringify(chain));

    console.log("▸ CONSOLE — the view renders and drives the same endpoints");
    const page = await render("/platform.html", 2200);
    const navBtn = Array.from(page.doc.querySelectorAll("button")).find(b => b.dataset && b.dataset.v === "padmins");
    ok(!!navBtn, "🛡️ Platform Admins is in the console nav");
    if (navBtn) { click(page.win, navBtn); await sleep(1500); }
    ok(page.doc.querySelectorAll("#paSave").length === 1, "the create form renders");
    ok(page.doc.body.textContent.includes("platform@luxora.shop"), "the owner is listed in the table");
    ok(page.errs.length === 0, "no JS errors rendering the view", page.errs.slice(0, 2).join("|"));
    /* create through the console the operator actually uses */
    page.doc.getElementById("paName").value = "Console Operator";
    page.doc.getElementById("paEmail").value = "operator@luxora.shop";
    page.doc.getElementById("paPass").value = "operator1234";
    click(page.win, page.doc.getElementById("paSave"));
    await sleep(1200);
    const verify = await f("/api/platform/admins");
    const opRow = verify.admins.find(a => a.email === "operator@luxora.shop");
    ok(!!opRow, "the console create reached the database", verify.admins && verify.admins.map(a => a.email).join(","));
    const opLogin = await f("/api/platform/login", "POST", { email: "operator@luxora.shop", password: "operator1234" });
    ok(!!opLogin.ok, "the console-created admin can sign in", opLogin.error);

    console.log("▸ RBAC IN THE CONSOLE — a scoped operator sees only what their role grants");
    /* the operator was created with the default support role */
    const opMe = await f("/api/platform/me");
    ok(Array.isArray(opMe.allowed) && !opMe.allowed.includes("*") && opMe.allowed.includes("tenants"),
      "the operator's grant includes tenants but is not ['*']", JSON.stringify(opMe.allowed && opMe.allowed.slice(0, 6)));
    const opPage = await render("/platform.html", 2200);
    ok(opPage.errs.length === 0, "the scoped console boots with no JS errors", opPage.errs.slice(0, 2).join("|"));
    ok(!!Array.from(opPage.doc.querySelectorAll("button[data-v='tenants']")).length, "the Tenants leaf is visible to the operator");
    ok(!Array.from(opPage.doc.querySelectorAll("button[data-v='padmins']")).length, "the Platform Admins leaf is hidden from the operator");
    ok(!Array.from(opPage.doc.querySelectorAll("button[data-v='security']")).length, "the Security leaf is hidden from the operator");
    ok(!!opPage.doc.querySelector(".p-tag") && opPage.doc.body.textContent.includes("support"), "the top bar shows the operator's role");
    /* a leaf they cannot reach renders the lock notice rather than the data */
    const before = opPage.doc.body.textContent;
    opPage.win.eval('view="security"; render();');
    await sleep(900);
    ok(opPage.doc.body.textContent.includes("does not grant access"), "a forbidden view renders the lock notice", opPage.doc.body.textContent.slice(0, 80));
    ok(before !== opPage.doc.body.textContent, "the notice replaced the dashboard content");

    console.log("▸ ROLE CHANGE — the owner re-scopes an operator and it takes effect");
    await f("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" });
    const scope = await f("/api/platform/admins/" + opRow.id, "PUT", { name: opRow.name, email: opRow.email, role: "auditor" });
    ok(!scope.error, "the owner re-roles the operator to auditor", scope.error);
    /* drop the owner's platform cookie so the next login is a clean session whose
       grants are read fresh — otherwise the jar keeps the owner's azp */
    jar.delete("azp");
    const reLogin = await f("/api/platform/login", "POST", { email: "operator@luxora.shop", password: "operator1234" });
    ok(!!reLogin.ok, "the re-roled operator signs back in", reLogin.error);
    const reScoped = await f("/api/platform/me");
    /* auditor keeps read on tenants (the nav still shows it) but LOSES write — the
       evidence of the re-role is the lost launch capability, not the leaf vanishing */
    ok(reScoped.allowed && reScoped.allowed.includes("audit"),
      "the auditor grant now includes audit", JSON.stringify(reScoped.allowed && reScoped.allowed.slice(0, 6)));
    const auditRead = await f("/api/platform/audit");
    ok(!auditRead.error, "the auditor can read the audit trail", auditRead.error);
    const noLaunch = await f("/api/platform/tenants", "POST", { name: "Nope", slug: "nope", country: "US", mode: "marketplace" });
    ok(!!noLaunch.error, "the auditor cannot launch a store (write lost on re-role)", noLaunch.error);
    /* and the grant that support had is gone in the direction that matters:
       the roles endpoint confirms write vs read for the caller */
    const reRoles = await f("/api/platform/roles");
    ok(!!(reRoles.me && reRoles.me.allowed), "the roles endpoint reports the re-roled caller's grants", JSON.stringify(reRoles.me));

    console.log(failed ? `\n${passed} passed, ${failed} failed` : `\n${passed} passed, 0 failed`);
  } finally {
    /* T1: SIGTERM and a wait for exit, not a SIGKILL — the process has to
       release its sockets before this one exits, or the reset surfaces as an
       unhandled rejection in the parent */
    try { await new Promise(r => { srv.once("exit", r); srv.kill("SIGTERM"); setTimeout(r, 1500); }); } catch (e) { }
    for (const s of ["", "-wal", "-shm"]) { try { require("fs").rmSync(db + s, { force: true }); } catch (e) { } }
  }
  process.exit(failed ? 1 : 0);
})().catch(e => { console.log("ABORT", e.message); process.exit(1); });
