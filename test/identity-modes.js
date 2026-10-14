/* Roles are per-store and login is per-method — both driven by registry data.

   A. ROLES: two stores start on the shared default role set; one store forks, re-scopes a
      role and defines one the other has never heard of, and the store console ENFORCES the
      fork (a grant removed on one store is refused there and still allowed on the other; a
      role only one store defines can only be assigned there). The fork survives a reboot.
   B. LOGIN: the vocabulary of sign-in kinds is a registry and the engine dispatches on the
      flow the registry names — so signup+sign-in by OTP, magic link, authenticator (TOTP),
      SSO/OIDC (token verified against the platform's single verifier) and a brand-new type
      ("passkey") all work with no code change, and the challenge ledger actually expires.

   The platform console and a store console are disjoint trust scopes (the two logins refuse
   each other's accounts), so the harness switches between them deliberately. */
"use strict";
const DB = require("path").join(__dirname, "identity.db");
process.env.LX_DB = DB;   /* before any lib require, so a fresh connection opens this file */
process.env.LUXORA_DEMO_BRANDS = "1";   /* these suites exercise the demo-brand fixtures */
const crypto = require("crypto");
const { spawn } = require("child_process");
const { DatabaseSync } = require("node:sqlite");
const path = require("path");
const rbac = require("../lib/rbac.js");
const identity = require("../lib/identity.js");
const PORT = 8841;
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
const fresh = (sql, ...p) => { try { return new DatabaseSync(DB, { readOnly: true }).prepare(sql).get(...p) || null; } catch (e) { return null; } };
const sleep = ms => new Promise(r => setTimeout(r, ms));
/* the two console scopes are disjoint; each switch starts a clean cookie jar */
const storeLogin = async (slug, email, pw) => { jar.clear(); await f("/api/session?store=" + slug); return f("/api/auth/login?store=" + slug, "POST", { email, password: pw }); };
const platLogin = async () => { jar.clear(); await f("/api/session?store=luxora"); return f("/api/platform/login", "POST", { email: "platform@luxora.shop", password: "platform123" }); };
const b64u = o => Buffer.from(JSON.stringify(o)).toString("base64url");
const makeIdToken = (payload, secret) => {
  const h = b64u({ alg: "HS256", typ: "JWT" }), p = b64u(payload);
  const sig = crypto.createHmac("sha256", secret).update(h + "." + p).digest("base64url");
  return h + "." + p + "." + sig;
};

(async () => {
  for (const s of ["", "-wal", "-shm"]) { try { require("fs").rmSync(DB + s, { force: true }); } catch (e) { } }
  const boot = async () => {
    const srv = spawn(process.execPath, [path.join(__dirname, "..", "server.js")], { env: { ...process.env, PORT, LX_DB: DB }, stdio: ["ignore", "ignore", "inherit"] });
    for (let i = 0; i < 120; i++) { try { if ((await fetch(BASE + "/healthz")).ok) return srv; } catch (e) { } await sleep(500); }
    throw new Error("server failed to boot");
  };
  let srv = await boot();
  try {
    const luxora = fresh("SELECT id FROM tenants WHERE slug='luxora'");
    const aurum = fresh("SELECT id FROM tenants WHERE slug='aurum'");
    ok(!!luxora && !!aurum, "two stores are seeded for the tenancy test");
    /* this suite drives dozens of auth handshakes in under a minute; the auth rate limit is
       platform POLICY data, so an operator raises it for a load test rather than the test
       working around the limiter */
    await platLogin();
    ok(!!(await f("/api/platform/config", "PUT", { authPerMin: 600, apiPerMin: 3000 })).policy, "the auth rate limit is raised for this run (policy is data)");

    /* ======================= A · ROLES ARE PER-STORE ======================= */
    console.log("▸ A1 — both stores start on the shared default role set");
    await storeLogin("luxora", "admin@luxora.shop", "admin123");
    const beforeLux = await f("/api/admin/roles");
    ok(beforeLux.ownSet === false, "luxora reports it has not forked (ownSet false)");
    ok((beforeLux.roles || []).some(r => r.key === "manager"), "the inherited default is visible on luxora");

    console.log("▸ A2 — forking one store re-scopes a role for THAT store only");
    await platLogin();
    const forked = await f("/api/platform/roles/staff", "POST", { tenant_id: luxora.id, key: "manager", name: "Store Manager", desc: "No payments", sections: { "*": "write", team: false, settings: "read", studio: false, payments: false } });
    ok(!!forked.ok, "the platform writes luxora's own role set", forked.error);
    ok(forked.tenant_id === luxora.id, "the save names which store's set it wrote");
    const mgrL = (fresh("SELECT items FROM meta_lists WHERE name='staffRoles:t" + luxora.id + "'") || {}).items;
    const mgrA = (fresh("SELECT items FROM meta_lists WHERE name='staffRoles'") || {}).items;
    ok(!!mgrL && !!mgrA, "both the forked row and the shared default live in the registry");
    const gL = rbac.expand((JSON.parse(mgrL).find(r => r.key === "manager") || {}).sections);
    const gA = rbac.expand((JSON.parse(mgrA).find(r => r.key === "manager") || {}).sections);
    ok(gL.payments === false, "luxora's manager lost payments", JSON.stringify(gL.payments));
    ok(gA.payments === "write", "aurum's manager still has payments (unforked)", JSON.stringify(gA.payments));
    await storeLogin("luxora", "admin@luxora.shop", "admin123");
    ok((await f("/api/admin/roles")).ownSet === true, "luxora now reports its own set");
    await storeLogin("aurum", "admin@aurum.shop", "aurum123");
    ok((await f("/api/admin/roles")).ownSet === false, "aurum is still on the shared default");

    console.log("▸ A3 — the store console enforces the fork on a real staff member");
    await platLogin();
    const sL = await f("/api/platform/users", "POST", { tenant_id: luxora.id, name: "Lux Manager", email: "mgr-lux@luxora.shop", password: "staff12345", role: "admin", staff_role: "manager" });
    const sA = await f("/api/platform/users", "POST", { tenant_id: aurum.id, name: "Aurum Manager", email: "mgr-aur@aurum.shop", password: "staff12345", role: "admin", staff_role: "manager" });
    ok(!!sL.ok && !!sA.ok, "a manager is created on each store", sL.error || sA.error);
    await storeLogin("luxora", "mgr-lux@luxora.shop", "staff12345");
    const gateL = await f("/api/admin/gateways", "PUT", { gateways: [] });
    ok(!!gateL.error && /payments/i.test(gateL.error), "luxora's manager is refused the payments gate", gateL.error);
    await storeLogin("aurum", "mgr-aur@aurum.shop", "staff12345");
    const gateA = await f("/api/admin/gateways", "PUT", { gateways: [] });
    ok(!!gateA.ok, "aurum's manager passes the same gate (default still grants payments)", gateA.error);

    console.log("▸ A4 — a role only one store defines is assignable only there");
    await platLogin();
    const onlyLux = await f("/api/platform/roles/staff", "POST", { tenant_id: luxora.id, key: "people_ops", name: "People Ops", desc: "Owns the team", sections: { dash: "read", team: "write" } });
    ok(!!onlyLux.ok, "luxora defines a role the platform default does not have", onlyLux.error);
    ok(!!(await f("/api/platform/users", "POST", { tenant_id: luxora.id, name: "HR", email: "hr@luxora.shop", password: "hr12345678", role: "admin", staff_role: "people_ops" })).ok, "and assigns it on luxora");
    const noRole = await f("/api/platform/users", "POST", { tenant_id: aurum.id, name: "HR", email: "hr@aurum.shop", password: "hr12345678", role: "admin", staff_role: "people_ops" });
    ok(!!noRole.error && /unknown staff role/i.test(noRole.error), "aurum rejects the role it never defined", noRole.error);
    await storeLogin("luxora", "hr@luxora.shop", "hr12345678");
    ok(Array.isArray((await f("/api/admin/staff")).staff), "the store-only role's team grant is enforced (the team lists)");
    const ownRole = await f("/api/admin/roles", "POST", { key: "scheduler", name: "Scheduler", sections: { orders: "read" } });
    ok(!!ownRole.ok && ownRole.ownSet === true, "a store defines its own roles from its own console", ownRole.error);
    ok((await f("/api/admin/roles")).roles.some(r => r.key === "scheduler"), "the store-defined role is in the store's set");
    await storeLogin("aurum", "admin@aurum.shop", "aurum123");
    ok((await f("/api/admin/roles")).roles.some(r => r.key === "scheduler") === false, "and in no other store's");

    console.log("▸ A5 — an operator's fork survives a reboot (the seed never reverts an edit)");
    srv.kill(); srv = await boot();
    await storeLogin("luxora", "hr@luxora.shop", "hr12345678");
    ok((await f("/api/admin/roles")).roles.some(r => r.key === "scheduler"), "the store-defined role survived the reboot");
    ok((fresh("SELECT edited FROM meta_lists WHERE name='staffRoles:t" + luxora.id + "'") || {}).edited === 1, "the fork is stamped edited, so the seed leaves it alone");

    /* ======================= B · LOGIN IS PER-METHOD, REGISTRY-DRIVEN ======================= */
    console.log("▸ B1 — a store's sign-in menu is derived from its enabled providers");
    ok((await f("/api/auth/methods?store=luxora")).methods.some(m => m.key === "password"), "password is offered by default");
    await storeLogin("luxora", "admin@luxora.shop", "admin123");
    ok(!!(await f("/api/admin/identity-providers", "PUT", { provider_type: "otp", name: "Email OTP", enabled: true, config: { channel: "email", length: 6, ttl: 5 } })).ok, "an OTP provider is configured for this store");
    ok((await f("/api/auth/methods?store=luxora")).methods.some(m => m.flow === "challenge"), "enabling it adds the challenge flow to the store's menu");

    console.log("▸ B2 — OTP: signup AND signin in one flow, session really established");
    const initReg = await f("/api/auth/login-init?store=luxora", "POST", { email: "otp@luxora.shop", method: "otp", register: true });
    ok(!!initReg.ok && initReg.action === "otp_sent", "register:true creates the account and issues a code", initReg.error);
    ok(initReg.ttl_minutes === 5, "the TTL comes from the store's provider config, not the client", JSON.stringify(initReg.ttl_minutes));
    ok(!!fresh("SELECT id FROM users WHERE email='otp@luxora.shop'"), "the account exists from the register flow");
    const code = (fresh("SELECT otp, expires_at FROM identity_otps ORDER BY id DESC LIMIT 1") || {});
    ok(!!code.otp && code.expires_at > Date.now(), "the code is stored with a real future expiry (epoch ms)");
    ok(!!(await f("/api/auth/login/otp?store=luxora", "POST", { email: "otp@luxora.shop", otp: code.otp })).ok, "the code verifies and signs the account in");
    ok(!!(await f("/api/session?store=luxora")).user, "and the session is bound to the new account");
    ok(!!(await f("/api/auth/login/otp?store=luxora", "POST", { email: "otp@luxora.shop", otp: code.otp })).error, "a used code cannot be replayed");
    ok(!!(await f("/api/auth/login/otp?store=luxora", "POST", { email: "otp@luxora.shop", otp: "000000" })).error, "a wrong code is refused");

    console.log("▸ B3 — MAGIC LINK: the ledger actually expires (the binding bug, fixed)");
    await storeLogin("luxora", "admin@luxora.shop", "admin123");
    ok(!!(await f("/api/admin/identity-providers", "PUT", { provider_type: "magic_link", name: "Email Link", enabled: true, config: { ttl: 15 } })).ok, "a magic-link provider is configured");
    const ml = await f("/api/auth/login-init?store=luxora", "POST", { email: "otp@luxora.shop", method: "magic_link" });
    ok(!!ml.ok && ml.action === "magic_link_sent", "a magic link is issued", ml.error);
    const mlRow = fresh("SELECT expires_at FROM identity_magic_links ORDER BY id DESC LIMIT 1");
    ok(!!mlRow && mlRow.expires_at > Date.now(), "the token's expiry is a real future timestamp", JSON.stringify(mlRow && mlRow.expires_at));
    ok(!!(await f("/api/auth/login/magic?store=luxora", "POST", { email: "otp@luxora.shop", token: ml.token })).ok, "the link signs the user in");
    ok(!!(await f("/api/auth/login/magic?store=luxora", "POST", { email: "otp@luxora.shop", token: "totally-bogus" })).error, "a bogus token is refused");

    console.log("▸ B4 — AUTHENTICATOR (TOTP): enrolled once, sealed at rest, verified by the app's code");
    /* the magic-link sign-in left the session bound to the account, so it enrols its own
       authenticator through the user's own endpoint */
    ok(!!(await f("/api/session?store=luxora")).user, "the account session carried over");
    await storeLogin("luxora", "admin@luxora.shop", "admin123");
    ok(!!(await f("/api/admin/identity-providers", "PUT", { provider_type: "totp", name: "Authenticator", enabled: true, config: { issuer: "LUXORA-TEST", digits: 6, step: 30 } })).ok, "a totp provider is configured");
    jar.clear(); await f("/api/session?store=luxora");
    await f("/api/auth/login-init?store=luxora", "POST", { email: "otp@luxora.shop", method: "magic_link" });
    const ml2 = (await f("/api/auth/login-init?store=luxora", "POST", { email: "otp@luxora.shop", method: "magic_link" }));
    await f("/api/auth/login/magic?store=luxora", "POST", { email: "otp@luxora.shop", token: ml2.token });
    ok(!!(await f("/api/session?store=luxora")).user, "signed back in passwordlessly to enrol");
    const enrol = await f("/api/user/identity-methods", "POST", { method_type: "totp", identifier: "otp@luxora.shop", metadata: { issuer: "LUXORA-TEST" }, is_primary: true });
    ok(!!enrol.ok && typeof enrol.secret === "string" && enrol.secret.length >= 16, "enrolment returns the provisioning secret once", enrol.error);
    ok(/^otpauth:\/\/totp\//.test(enrol.uri || ""), "and the otpauth URI for the QR");
    const stored = JSON.parse(((fresh("SELECT metadata FROM user_identity_methods WHERE method_type='totp' ORDER BY created_at DESC LIMIT 1") || {}).metadata) || "{}");
    ok(stored.secret && stored.secret.startsWith("lux.v1."), "the stored copy is sealed at rest, not plaintext");
    /* the seal is bound to this account, so the server's own unseal is what the next two
       assertions exercise (a wrong code is refused, the app-derived one verifies) rather
       than a second process's keyring, which boots its own master key */
    const tc = await f("/api/auth/login-init?store=luxora", "POST", { email: "otp@luxora.shop", method: "totp" });
    ok(!!tc.ok && tc.action === "totp_challenge", "the authenticator flow asks for the app's code (nothing is sent)", tc.error);
    ok(!!(await f("/api/auth/login/otp?store=luxora", "POST", { email: "otp@luxora.shop", otp: "000000" })).error, "a wrong authenticator code is refused");
    ok(!!(await f("/api/auth/login/otp?store=luxora", "POST", { email: "otp@luxora.shop", otp: identity.computeTotp(enrol.secret, 30, 6) })).ok, "the app-derived code verifies");

    console.log("▸ B5 — a brand-new provider type works with zero code (registry → flow)");
    await platLogin();
    const pt = await f("/api/admin/identity-provider-types", "POST", { key: "passkey", label: "Passkey", flow: "biometric", fields: ["rpId", "rpName"] });
    ok(!!pt.ok, "a new type is registered naming a flow the engine already has", pt.error);
    await storeLogin("luxora", "admin@luxora.shop", "admin123");
    ok(!!(await f("/api/admin/identity-providers", "PUT", { provider_type: "passkey", name: "Device Passkey", enabled: true, config: { rpId: "luxora.localhost" } })).ok, "a provider of the new type is configured");
    const pk = await f("/api/auth/login-init?store=luxora", "POST", { email: "otp@luxora.shop", method: "passkey" });
    ok(!!pk.ok && pk.action === "biometric_challenge", "the new type routes to the flow it named — no code change", pk.error);
    ok(!!(await f("/api/auth/login/biometric?store=luxora", "POST", { email: "otp@luxora.shop", challenge: pk.challenge, assertion: { clientDataJSON: "x", authenticatorData: "y", signature: "z" } })).error, "the flow is reachable and a fabricated assertion is refused — the stub that accepted it is gone");
    await platLogin();
    ok(!!(await f("/api/admin/identity-provider-types", "POST", { key: "bogusflow", label: "Bogus", flow: "telepathy", fields: [] })).error, "a type naming an unknown flow is refused at registration");

    console.log("▸ B6 — SSO/OIDC: one redirect, one verifier, auto-provisioned account");
    const ISS = "https://idp.example.com", CID = "test-client", SECRET = "shared-secret";
    await storeLogin("luxora", "admin@luxora.shop", "admin123");
    ok(!!(await f("/api/admin/identity-providers", "PUT", { provider_type: "openid", name: "Corp IdP", enabled: true, config: { issuer: ISS, clientId: CID, clientSecret: SECRET, redirectUri: "https://luxora.localhost/auth/callback", scope: "openid email profile" } })).ok, "an OIDC provider is configured (secret sealed by the store)");
    const sso = await f("/api/auth/login-init?store=luxora", "POST", { email: "corp@luxora.shop", method: "openid" });
    ok(!!sso.ok && sso.action === "external_redirect", "the external flow builds the authorize URL", sso.error);
    ok(sso.url.startsWith(ISS + "/authorize") && sso.url.includes("state="), "the URL is built from the provider config and carries a state", sso.url);
    ok(!!fresh("SELECT provider_id FROM identity_login_states WHERE state=?", sso.state), "the state remembers which provider this login belongs to");
    const badState = await f("/api/auth/login/callback?store=luxora", "POST", { id_token: makeIdToken({ email: "corp@luxora.shop", iss: ISS, aud: CID, exp: Math.floor(Date.now() / 1000) + 60 }, SECRET), state: "no-such-state" });
    ok(!!badState.error, "a callback with an unknown state is refused", badState.error);
    const badSig = await f("/api/auth/login/callback?store=luxora", "POST", { id_token: makeIdToken({ email: "corp@luxora.shop", iss: ISS, aud: CID, exp: Math.floor(Date.now() / 1000) + 60 }, "wrong-secret"), state: sso.state });
    ok(!!badSig.error, "a token signed with the wrong secret is refused", badSig.error);
    const cb = await f("/api/auth/login/callback?store=luxora", "POST", { id_token: makeIdToken({ email: "corp@luxora.shop", iss: ISS, aud: CID, exp: Math.floor(Date.now() / 1000) + 60 }, SECRET), state: sso.state });
    ok(!!cb.ok && !!cb.provisioned, "a valid token provisions the account and signs it in", cb.error);
    ok(!!fresh("SELECT id FROM users WHERE email='corp@luxora.shop'"), "the SSO account exists on this store");

    console.log("▸ B7 — registration is a deliberate choice, never a login side effect");
    const unknown = await f("/api/auth/login-init?store=luxora", "POST", { email: "ghost@luxora.shop", method: "otp" });
    ok(!!unknown.error && unknown.action === "register", "an unknown account is sign-UP, not a silent create", unknown.error);
    ok(Array.isArray(unknown.available), "the store's enabled methods are offered back so the UI never dead-ends");
    const noEnrol = await f("/api/auth/login-init?store=luxora", "POST", { email: "ghost@luxora.shop", method: "totp", register: true });
    ok(!!noEnrol.error && noEnrol.action === "enrol_totp", "a totp signup without an enrolled authenticator says so", noEnrol.error);
    const disabledMethod = await f("/api/auth/login-init?store=luxora", "POST", { email: "admin@luxora.shop", method: "carrier_pigeon" });
    ok(!!disabledMethod.error && Array.isArray(disabledMethod.available), "an unregistered method is refused with the alternatives", disabledMethod.error);
    const tamper = await f("/api/auth/login-init?store=luxora", "POST", { email: "admin@luxora.shop", method: "otp", config: { ttl: 99999, length: 4 } });
    ok(!!tamper.ok && tamper.ttl_minutes === 5, "client-supplied ttl/length are ignored — the store's provider row decides", JSON.stringify(tamper.ttl_minutes));
  } finally {
    srv.kill();
    for (const s of ["", "-wal", "-shm"]) { try { require("fs").rmSync(DB + s, { force: true }); } catch (e) { } }
  }
  console.log(failed ? `\n${passed} passed, ${failed} FAILED` : `\n${passed} passed, 0 failed`);
  process.exit(failed ? 1 : 0);
})();
