/* LUXORA Platform — identity domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the identity domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "identity", routes(kit) {
  const { letters, J, RESET_TTL_MIN, T, all, appInfo, audit, authz, bad, crypto, engineFail, enterprise, establishSession, get, hashPasswordFor, ipOf, isTls, json, kindBrief, logAction, mergeOwner, mods, newPlatformAdmin, newUser, newUserAsync, ownerFor, passwordReusedAsync, platformSections, prbac, publicLink, rbac, requireAdmin, requirePlatform, requirePlatformSection, requireSection, requireStore, rotateSession, rules, run, sec, setUserPasswordAsync, settings, sha256hex, verifyPlatformAdminAsync, verifyUserAsync } = kit;

  const mfa = require("../mfa.js");
  /* the account a sign-in is for, as its lockout counts it: accounts belong to one store */
  const account = (s, email) => "t" + T(s) + ":" + String(email || "").toLowerCase();
  function rememberDevice(req, res, s, acct) {
    s.device = sec.deviceCookie(acct, s.device);
    res.appendHeader("Set-Cookie", sec.DEVICE_COOKIE + "=" + s.device + "; Path=/; HttpOnly; SameSite=Lax; Max-Age=31536000" + (isTls(req) ? "; Secure" : ""));
  }
  /* ---------------- the second factor ----------------
     Guesses share the sign-in's lockout: six digits are guessable without one. */
  function tryCode(scope, id, code) {
    const key = "mfa:" + scope + ":" + id, lock = sec.lockState(key);
    if (lock.locked) return { locked: lock.retryAfterSec };
    const ok = mfa.verify(scope, id, code);
    if (ok) sec.noteLoginOk(key); else sec.noteLoginFail(key);
    return { ok };
  }
  function confirmStaff(s, userId, code) {
    const r = tryCode("user", userId, code);
    if (r.ok) { run("UPDATE sessions SET mfa_at=datetime('now') WHERE sid=?", s.sid); s.mfa_at = new Date().toISOString(); }
    return r;
  }
  function confirmPlatform(adminId, ptid, code) {
    const r = tryCode("platform", adminId, code);
    if (r.ok) run("UPDATE platform_sessions SET mfa_at=datetime('now') WHERE ptid=?", ptid);
    return r;
  }
  /* who a second-factor request is about: the platform sign-in or the store sign-in on this browser */
  function mfaSubject(s, scope) {
    if (scope === "platform") { const a = s.platform_admin || s.platform_pending; return a ? { scope, id: a.id, label: a.email, ok: !!s.platform_admin, confirm: code => confirmPlatform(a.id, s.ptid, code), mark: () => run("UPDATE platform_sessions SET mfa_at=datetime('now') WHERE ptid=?", s.ptid) } : null; }
    const u = s.user_id ? get("SELECT id,email,role,disabled FROM users WHERE id=? AND tenant_id=?", s.user_id, T(s)) : null;
    return u && !u.disabled ? { scope: "user", id: u.id, label: u.email, ok: mfa.state("user", u.id, s.mfa_at) === "ok", confirm: code => confirmStaff(s, u.id, code), mark: () => run("UPDATE sessions SET mfa_at=datetime('now') WHERE sid=?", s.sid) } : null;
  }
  const answerCode = (res, r) => r.locked ? bad(res, "Too many wrong codes — retry in " + r.locked + "s", 423) : r.ok ? json(res, 200, { ok: true }) : bad(res, "That code is not right", 401);
  function mfaCall(req, res, url, s, fn) {
    const m = mfaSubject(s, /^\/api\/platform\//.test(url.pathname) ? "platform" : "user");
    if (!m) return bad(res, "Please sign in", 401);
    try { fn(m); } catch (e) { engineFail(res, e); }
  }
  /* whether the signed-in person has a second factor, must have one, and has confirmed it on this sign-in */
  function apiMfaStatus(req, res, url, s) { mfaCall(req, res, url, s, m => json(res, 200, { ...mfa.status(m.scope, m.id), confirmed: m.ok })); }
  /* confirms this sign-in with a code from the authenticator app, or a recovery code */
  function apiMfaVerify(req, res, url, s, body) { mfaCall(req, res, url, s, m => answerCode(res, m.confirm((body || {}).code))); }
  /* starts setting up an authenticator app: a new key, not active until a code from it is confirmed */
  function apiMfaStart(req, res, url, s) {
    mfaCall(req, res, url, s, m => {
      if (mfa.enrolled(m.scope, m.id) && !m.ok) return bad(res, "Confirm your current code first", 403);
      json(res, 200, mfa.start(m.scope, m.id, m.label, m.scope === "platform" ? ((require("../db.js").masterTenant() || {}).name || "LUXORA") : s.tenant.name));
    });
  }
  const mfaLog = (req, s, m, action) => m.scope === "platform" ? audit(null, "platform", m.id, m.label, action, "platform", null, {}) : logAction(s, action, "user", m.id, {}, req);
  /* turns the new key on with a code from it, and gives the recovery codes once */
  function apiMfaConfirm(req, res, url, s, body) {
    mfaCall(req, res, url, s, m => {
      if (mfa.enrolled(m.scope, m.id) && !m.ok) return bad(res, "Confirm your current code first", 403);
      const out = mfa.confirm(m.scope, m.id, (body || {}).code);
      m.mark(); mfaLog(req, s, m, "mfa.enrol");
      json(res, 200, { ok: true, ...out });
    });
  }
  /* turns the second factor off, only with a working code */
  function apiMfaRemove(req, res, url, s, body) {
    mfaCall(req, res, url, s, m => {
      const r = tryCode(m.scope, m.id, (body || {}).code);
      if (!r.ok) return answerCode(res, r);
      mfa.remove(m.scope, m.id); mfaLog(req, s, m, "mfa.remove");
      json(res, 200, { ok: true });
    });
  }
  /* someone who lost their phone and codes: a platform admin who may manage admins resets another's */
  function apiPlatformAdminMfaReset(req, res, url, s, body, id) {
    if (!requirePlatformSection(s, res, "padmins", "write")) return;
    if (Number(id) === s.platform_admin.id) return bad(res, "You cannot reset your own second factor", 409);
    const a = get("SELECT id,email FROM platform_admins WHERE id=?", Number(id));
    if (!a) return bad(res, "Unknown admin", 404);
    mfa.remove("platform", a.id);
    run("DELETE FROM platform_sessions WHERE admin_id=?", a.id);
    audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "mfa.reset", "platform_admin", a.id, { email: a.email }, ipOf(req), s.trace);
    json(res, 200, { ok: true });
  }
  /* resets a staff member's second factor when they have lost it; an owner's only by an owner */
  function apiStaffMfaReset(req, res, url, s, body, id) {
    if (!requireSection(s, res, "team", "write")) return;
    if (Number(id) === Number(s.user_id)) return bad(res, "You cannot reset your own second factor", 409);
    const u = get("SELECT id,email,staff_role FROM users WHERE id=? AND tenant_id=? AND role='admin'", Number(id), T(s));
    if (!u) return bad(res, "Unknown staff member", 404);
    const me = s.user_id ? get("SELECT staff_role FROM users WHERE id=?", s.user_id) : null;
    if (!s.platform_admin && (u.staff_role || "owner") === "owner" && (!me || (me.staff_role || "owner") !== "owner")) return bad(res, "Only an owner can reset an owner's second factor", 403);
    mfa.remove("user", u.id);
    run("UPDATE sessions SET user_id=NULL, mfa_at=NULL WHERE user_id=?", u.id);
    logAction(s, "mfa.reset", "user", u.id, { email: u.email }, req);
    json(res, 200, { ok: true });
  }
  /* ---------------- confirming an email address ---------------- */
  const VERIFY_HOURS = 48;
  function sendVerification(req, s, userId, email) {
    const mailer = require("../mailer.js");
    if (!mailer.transportFor(T(s), "email") && process.env.NODE_ENV === "production") return false;
    if (get("SELECT COUNT(*) c FROM email_verifications WHERE user_id=? AND created_at > datetime('now','-1 hour')", userId).c >= 3) return false;
    const token = crypto.randomBytes(32).toString("hex");
    run("INSERT INTO email_verifications(tenant_id,user_id,email,token_hash,expires_at) VALUES(?,?,?,?,?)", T(s), userId, email, sha256hex(token), Date.now() + VERIFY_HOURS * 3600e3);
    const link = publicLink(req, s, "orders.html", { verify: token });
    mailer.deliver({ tenantId: T(s), channel: "email", to: email, kind: "email_verify", ...letters.write("email_verify", letters.langOf(T(s), { userId }), { store: s.tenant.name, link, code: link ? "" : token, hours: VERIFY_HOURS }) });
    return true;
  }
  /* confirms an email address with the link sent to it */
  function apiEmailVerify(req, res, url, s, body) {
    const token = String(body.token || "");
    const v = /^[0-9a-f]{64}$/.test(token) ? get("SELECT * FROM email_verifications WHERE token_hash=? AND tenant_id=?", sha256hex(token), T(s)) : null;
    const u = v && !v.used_at && v.expires_at > Date.now() ? get("SELECT id,email FROM users WHERE id=? AND tenant_id=?", v.user_id, T(s)) : null;
    if (!u || u.email !== v.email) return bad(res, "This confirmation link is invalid or has expired — send yourself a new one", 400);
    run("UPDATE email_verifications SET used_at=datetime('now') WHERE user_id=? AND used_at IS NULL", u.id);
    run("UPDATE users SET email_verified_at=datetime('now') WHERE id=?", u.id);
    logAction(s, "auth.email_verified", "user", u.id, { email: u.email }, req);
    json(res, 200, { ok: true });
  }
  /* sends the signed-in shopper another confirmation link */
  function apiEmailVerifySend(req, res, url, s) {
    const u = s.user_id ? get("SELECT id,email,email_verified_at FROM users WHERE id=? AND tenant_id=?", s.user_id, T(s)) : null;
    if (!u) return bad(res, "Please sign in", 401);
    if (u.email_verified_at) return json(res, 200, { ok: true, already: true });
    if (!sendVerification(req, s, u.id, u.email)) return bad(res, "We can't send another confirmation right now — try again later", 429);
    json(res, 200, { ok: true });
  }

  /* ---------------- session ---------------- */
  function apiSession(req, res, url, s) {
    const owner = ownerFor(s);
    const cart = all("SELECT product_id, qty FROM cart_items WHERE owner=?", owner);
    const sub = cart.reduce((n, c) => { const p = get("SELECT price FROM products WHERE tenant_id=? AND id=?", T(s), c.product_id); return p ? n + p.price * c.qty : n; }, 0);
    const urow = s.user_id ? get("SELECT id,name,email,role,staff_role,perms,email_verified_at FROM users WHERE id=? AND tenant_id=?", s.user_id, T(s)) : null;
    const staffOk = !!urow && mfa.state("user", urow.id, s.mfa_at) === "ok";
    json(res, 200, {
      user: urow,
      allowedSections: s.platform_admin ? ["*"] : (staffOk ? rbac.allowedSections(urow, T(s)) : []),
      zip: s.zip, gift: require("../gates.js").on(T(s), "checkout.wallet") ? require("../wallet.js").checkoutAvailable(T(s), mods.ownerFor(s)) : 0, coupon: s.coupon || "", capabilities: [...mods.caps(T(s))].filter(c => mods.hasCap(T(s), c)), gates: require("../gates.js").all(T(s)),
      cartCount: cart.reduce((n, c) => n + c.qty, 0), cartSubtotal: sub,
      saved: all("SELECT product_id FROM saved_items WHERE owner=?", owner).map(r => r.product_id),
      viewed: all("SELECT product_id FROM view_history WHERE owner=? ORDER BY seen_at DESC LIMIT 12", owner).map(r => r.product_id)
    });
  }
  /* request-path credential work runs on the thread pool (await …Async): a synchronous scrypt
     here stalled the whole server for every anonymous registration / login / hint request */
  async function apiRegister(req, res, url, s, body) {
    const name = String(body.name || "").trim().slice(0, 60);
    const email = String(body.email || "").trim().toLowerCase();
    const password = String(body.password || "");
    if (!name || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return bad(res, "Please enter a valid name and email");
    const perr = sec.checkPassword(password, email);
    if (perr) return bad(res, perr);
    if (get("SELECT id FROM users WHERE tenant_id=? AND email=?", T(s), email)) return bad(res, "That email already has an account", 409);
    const uid = await newUserAsync(T(s), name, email, password, "customer");
    mergeOwner("t" + T(s) + ":s:" + s.sid, "t" + T(s) + ":u:" + uid);
    mods.walletMerge("t" + T(s) + ":s:" + s.sid, "t" + T(s) + ":u:" + uid);
    run("UPDATE sessions SET user_id=?, mfa_at=NULL WHERE sid=?", uid, s.sid);
    s.user_id = uid; s.mfa_at = null;
    rotateSession(req, res, s);
    rememberDevice(req, res, s, account(s, email));
    run("UPDATE users SET lang=? WHERE id=?", letters.heard(req, url, T(s)), uid);
    sendVerification(req, s, uid, email);
    logAction(s, "auth.register", "user", uid, { email });
    json(res, 200, { ok: true, user: { id: uid, name, email, role: "customer" } });
  }
  async function apiLogin(req, res, url, s, body) {
    const email = String(body.email || "").trim();
    const key = sec.loginKey(account(s, email), s.device);
    const lock = sec.lockState(key);
    if (lock.locked) return bad(res, "Account temporarily locked after failed attempts — retry in " + lock.retryAfterSec + "s", 423);
    const u = await verifyUserAsync(T(s), email, String(body.password || ""));
    /* one answer for every failure. The old messages told an anonymous caller whether the
       email existed, which store it belonged to, whether it was a platform account — and
       printed the store admin's own email address. */
    if (!u) { sec.noteLoginFail(key); logAction(s, "auth.login_failed", "user", null, { email }, req);
      return bad(res, "Invalid email or password for " + s.tenant.name + " (accounts belong to one store — add ?store=slug to switch)", 401);
    }
    sec.noteLoginOk(key);
    if (u.disabled) return bad(res, "This account has been disabled by a store owner", 403);
    /* a sign-in method is subject to the applicability rules for customers (a platform's own
       staff are never locked out of their console by a customer-facing rule) */
    if (!rules.exempt("login.password", u.role)) { const d = rules.decideAt("login.password", undefined, rules.at("login.password", T(s))); if (!d.ok) return bad(res, "This sign-in method is not available here — " + d.reasons.join("; "), 403); }
    /* the unified console holds both authorities at once: a store sign-in binds the
       store user without dropping a platform session this client may also hold. The
       scopes cannot blend — authz namespaces each authority's grants */
    run("UPDATE users SET last_login=datetime('now') WHERE id=?", u.id);
    mergeOwner("t" + T(s) + ":s:" + s.sid, "t" + T(s) + ":u:" + u.id);
    mods.walletMerge("t" + T(s) + ":s:" + s.sid, "t" + T(s) + ":u:" + u.id);
    run("UPDATE sessions SET user_id=?, mfa_at=NULL WHERE sid=?", u.id, s.sid);
    s.user_id = u.id; s.mfa_at = null;
    rotateSession(req, res, s);
    if (body.code) confirmStaff(s, u.id, body.code);
    rememberDevice(req, res, s, account(s, u.email));
    run("UPDATE users SET lang=? WHERE id=?", letters.heard(req, url, T(s)), u.id);
    logAction(s, "auth.login", "user", u.id, { email: u.email });
    const step = u.role === "admin" ? mfa.state("user", u.id, s.mfa_at) : "ok";
    json(res, 200, { ok: true, ...(step === "ok" ? {} : { mfa: step }), user: { id: u.id, name: u.name, email: u.email, role: u.role, staff_role: u.staff_role || "owner" } });
  }
  /* "forgot password" answers the same whether or not the account exists, so it cannot be
     used to discover who shops here. At most three links per account per 15 minutes; a new
     link retires the older ones. */
  function apiPasswordForgot(req, res, url, s, body) {
    if (!requireStore(s, res)) return;
    const email = String(body.email || "").trim().toLowerCase();
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return bad(res, "Please enter a valid email", 400);
    const answer = { ok: true, message: "If an account exists for that email, a reset link is on its way. It expires in " + RESET_TTL_MIN + " minutes." };
    const u = get("SELECT id, email, name, disabled FROM users WHERE tenant_id=? AND email=?", T(s), email);
    if (!u || u.disabled) { logAction(s, "auth.password_forgot", "user", null, { known: false }, req); return json(res, 200, answer); }
    const recent = get("SELECT COUNT(*) c FROM password_resets WHERE user_id=? AND created_at > datetime('now','-15 minutes')", u.id).c;
    if (recent >= 3) { logAction(s, "auth.password_forgot", "user", u.id, { throttled: true }, req); return json(res, 200, answer); }
    const token = crypto.randomBytes(32).toString("hex");
    run("UPDATE password_resets SET used_at=datetime('now') WHERE user_id=? AND used_at IS NULL", u.id);
    run("INSERT INTO password_resets(tenant_id,user_id,token_hash,expires_at,ip) VALUES(?,?,?,?,?)", T(s), u.id, sha256hex(token), Date.now() + RESET_TTL_MIN * 60000, ipOf(req));
    const link = publicLink(req, s, "reset.html", { token });
    require("../mailer.js").deliver({ tenantId: T(s), channel: "email", to: u.email, kind: "password_reset", ...letters.write("password_reset", letters.langOf(T(s), { userId: u.id }), { store: s.tenant.name, email: u.email, link, code: link ? "" : token, minutes: RESET_TTL_MIN }) });
    logAction(s, "auth.password_forgot", "user", u.id, { sent: true }, req);
    json(res, 200, answer);
  }
  /* a reset proves control of the mailbox, so it ends every session the account holds (the
     reason for a reset is often that someone else is signed in) and clears the lockout */
  async function apiPasswordReset(req, res, url, s, body) {
    if (!requireStore(s, res)) return;
    const token = String(body.token || "").trim();
    const password = String(body.password || "");
    const row = /^[0-9a-f]{64}$/.test(token) ? get("SELECT * FROM password_resets WHERE token_hash=? AND tenant_id=?", sha256hex(token), T(s)) : null;
    if (!row || row.used_at || row.expires_at < Date.now()) return bad(res, "This reset link is invalid or has expired — request a new one", 400);
    const u = get("SELECT id, email, disabled FROM users WHERE id=? AND tenant_id=?", row.user_id, T(s));
    if (!u || u.disabled) return bad(res, "This reset link is invalid or has expired — request a new one", 400);
    const perr = sec.checkPassword(password, u.email);
    if (perr) return bad(res, perr, 422);
    if ((await verifyUserAsync(T(s), u.email, password)) || (await passwordReusedAsync(T(s), u.email, password))) return bad(res, "You cannot reuse a previous password", 422);
    /* claim the token before the slow hash, so two concurrent submissions cannot both win */
    const claimed = run("UPDATE password_resets SET used_at=datetime('now') WHERE id=? AND used_at IS NULL", row.id);
    if (!claimed.changes) return bad(res, "This reset link is invalid or has expired — request a new one", 400);
    await setUserPasswordAsync(u.id, password, u.email);
    run("UPDATE sessions SET user_id=NULL WHERE user_id=?", u.id);
    if (s.user_id === u.id) s.user_id = null;
    run("UPDATE users SET email_verified_at=COALESCE(email_verified_at, datetime('now')) WHERE id=?", u.id);
    sec.noteLoginOk(account(s, u.email));
    sec.noteLoginOk("otp:" + T(s) + ":" + u.email);
    logAction(s, "auth.password_reset", "user", u.id, {}, req);
    require("../mailer.js").deliver({ tenantId: T(s), channel: "email", to: u.email, kind: "password_changed", ...letters.write("password_changed", letters.langOf(T(s), { userId: u.id }), { store: s.tenant.name, email: u.email }) });
    json(res, 200, { ok: true });
  }
  function apiLogout(req, res, url, s) {
    run("UPDATE sessions SET user_id=NULL, mfa_at=NULL WHERE sid=?", s.sid);
    s.user_id = null;
    rotateSession(req, res, s);
    json(res, 200, { ok: true });
  }
  function apiTokenExchange(req, res, url, s, body) {
    const t = get("SELECT * FROM tokens WHERE token=? AND expires_at > datetime('now')", String(body.token || ""));
    if (!t) return bad(res, "Invalid or expired token", 401);
    if (t.tenant_id !== T(s)) return bad(res, "Token issued for a different store", 403);
    run("DELETE FROM tokens WHERE token=?", t.token);
    /* handed over by a platform admin whose own second factor is confirmed */
    run("UPDATE sessions SET user_id=?, mfa_at=datetime('now') WHERE sid=?", t.user_id, s.sid);
    s.user_id = t.user_id; s.mfa_at = new Date().toISOString();
    rotateSession(req, res, s);
    const u = get("SELECT id,name,email,role FROM users WHERE id=?", t.user_id);
    json(res, 200, { ok: true, user: u });
  }
  /* ---------------- identity ---------------- */
  function apiIdentityProvidersGet(req, res, url, s) {
    /* provider configs carry client ids/secrets — staff only (the sign-in menu a shopper
       needs is GET /api/auth/methods) */
    if (!requireSection(s, res, "settings", "read", "identity")) return;
    const identity = require("../identity.js");
    json(res, 200, { providers: identity.getIdentityProviders(T(s)) });
  }
  function apiIdentityProvidersPut(req, res, url, s, body) {
    if (!requireSection(s, res, "settings", "write", "identity")) return;
    const identity = require("../identity.js");
    json(res, 200, identity.upsertIdentityProvider(T(s), body));
  }
  function apiIdentityProviderDelete(req, res, url, s) {
    if (!requireSection(s, res, "settings", "write", "identity")) return;
    const identity = require("../identity.js");
    const id = url.pathname.match(/\/identity-providers\/([^/]+)$/)?.[1];
    if (!id) return bad(res, "Provider ID required", 400);
    json(res, 200, identity.deleteIdentityProvider(T(s), id));
  }
  function apiIdentitySettingsGet(req, res, url, s) {
    if (!requireSection(s, res, "settings", "read", "identity")) return;
    const identity = require("../identity.js");
    json(res, 200, { settings: identity.getIdentitySettings(T(s)) });
  }
  function apiIdentitySettingsPut(req, res, url, s, body) {
    if (!requireSection(s, res, "settings", "write", "identity")) return;
    const identity = require("../identity.js");
    json(res, 200, identity.setIdentitySettings(T(s), body));
  }
  function apiLoginInit(req, res, url, s, body) {
    if (!requireStore(s, res)) return;
    /* email/method must arrive as strings — node:sqlite raises a TypeError when asked to
       bind undefined, which turned a malformed client request into a 500. */
    if (!body.email || !body.method) return bad(res, 'email and method required', 400);
    const identity = require("../identity.js");
    /* opts are the caller's INTENT (register vs sign-in) and display hints, never security
       parameters — ttl/length/channel come from the store's provider row */
    const opts = { register: !!body.register, base_url: String(body.base_url || ""), state: String(body.state || "") };
    json(res, 200, identity.initiateLogin(T(s), String(body.email), String(body.method), opts));
  }
  /* the callback every external authority (SSO/OIDC/OAuth/directory) returns the user to.
     The state resolves the provider this login belongs to; the id_token is verified by the
     platform's single verifier, and the account is created when the provider allows it. */
  function apiLoginCallback(req, res, url, s, body) {
    if (!requireStore(s, res)) return;
    const identity = require("../identity.js");
    const idToken = String(body.id_token || body.access_token || body.token || "");
    if (!idToken) return bad(res, "id_token is required", 400);
    const r = identity.completeExternal(T(s), idToken, body.state ? String(body.state) : null);
    if (!r.ok) return bad(res, r.error, 401);
    establishSession(req, res, s, r.userId, "auth.external_login", { email: r.email, method: "external" });
    json(res, 200, { ok: true, user: r.user, provisioned: !!r.provisioned });
  }
  function apiAuthMethods(req, res, url, s) {
    if (!requireStore(s, res)) return;
    const identity = require("../identity.js");
    json(res, 200, { methods: identity.enabledMethods(T(s)), settings: { passwordEnabled: identity.getIdentitySettings(T(s)).login.passwordEnabled !== false } });
  }
  function apiLoginOtpVerify(req, res, url, s, body) {
    if (!requireStore(s, res)) return;
    const identity = require("../identity.js");
    /* code and authenticator logins share the password path's lockout: a 6-digit code (and a
       TOTP's ±1 window) is guessable without one */
    const lockKey = sec.loginKey("otp:" + T(s) + ":" + String(body.email || "").toLowerCase(), s.device);
    const lock = sec.lockState(lockKey);
    if (lock.locked) return bad(res, "Too many attempts — retry in " + lock.retryAfterSec + "s", 423);
    const user = get("SELECT id FROM users WHERE email=? AND tenant_id=?", String(body.email || "").toLowerCase(), T(s));
    if (!user) { sec.noteLoginFail(lockKey); return json(res, 200, { ok: false, error: "Invalid or expired code" }); }
    const result = identity.verifyOTP(T(s), user.id, body.email, body.otp);
    if (!result.ok) sec.noteLoginFail(lockKey); else sec.noteLoginOk(lockKey);
    if (result.ok) establishSession(req, res, s, user.id, "auth.otp_login", { email: body.email, method: result.method || "code" });
    json(res, 200, result);
  }
  function apiLoginMagicLinkVerify(req, res, url, s, body) {
    if (!requireStore(s, res)) return;
    const identity = require("../identity.js");
    const user = get("SELECT id FROM users WHERE email=? AND tenant_id=?", String(body.email || "").toLowerCase(), T(s));
    if (!user) return json(res, 200, { ok: false, error: "Invalid or expired sign-in" });
    const result = identity.verifyMagicLink(user.id, body.token);
    if (result.ok) establishSession(req, res, s, user.id, "auth.magic_link_login", { email: body.email });
    json(res, 200, result);
  }
  function apiLoginBiometricVerify(req, res, url, s, body) {
    if (!requireStore(s, res)) return;
    const identity = require("../identity.js");
    const user = get("SELECT id FROM users WHERE email=? AND tenant_id=?", String(body.email || "").toLowerCase(), T(s));
    if (!user) return json(res, 200, { ok: false, error: "Invalid or expired sign-in" });
    const result = identity.verifyBiometric(user.id, body.challenge, body.assertion);
    if (result.ok) establishSession(req, res, s, user.id, "auth.biometric_login", { email: body.email });
    json(res, 200, result);
  }
  /* enrol a WebAuthn credential on the signed-in account. Called twice by a console:
     once with no body to mint the challenge the authenticator signs, then with the
     attestation + clientDataJSON. The attestation is VERIFIED server-side (challenge,
     origin and, for packed/u2f, the certificate signature) before any key is bound —
     an account can never gain a credential by asserting it has one. */
  function apiBiometricRegister(req, res, url, s, body) {
    if (!requireStore(s, res)) return;
    const identity = require("../identity.js");
    const user = s.user_id ? get("SELECT id, tenant_id FROM users WHERE id=?", s.user_id) : null;
    if (!user) return bad(res, "Not authenticated", 401);
    if (body && body.attestation) {
      json(res, 200, identity.registerBiometric(user.id, body.attestation, body.challenge,
        { tenantId: user.tenant_id, clientDataJSON: body.clientDataJSON, origin: body.origin || null }));
      return;
    }
    json(res, 200, identity.biometricChallenge(user.id, user.tenant_id));
  }
  function apiIdentityMethodsGet(req, res, url, s) {
    if (!requireStore(s, res)) return;
    const identity = require("../identity.js");
    const user = s.user_id ? get("SELECT id FROM users WHERE id=?", s.user_id) : null;
    if (!user) return bad(res, "Not authenticated", 401);
    json(res, 200, { methods: identity.getUserIdentityMethods(user.id) });
  }
  async function apiIdentityMethodsLink(req, res, url, s, body) {
    if (!requireStore(s, res)) return;
    const identity = require("../identity.js");
    const user = s.user_id ? get("SELECT id FROM users WHERE id=?", s.user_id) : null;
    if (!user) return bad(res, "Not authenticated", 401);
    /* a passkey is enrolled only through the attested biometric flow, never linked as a bare row */
    if (/webauthn|passkey|biometric/i.test(String(body.method_type || ""))) return bad(res, "Passkeys are enrolled through the biometric registration flow", 400);
    /* adding a sign-in credential (an authenticator, a phone, another email) is a takeover path
       for a stolen session: it needs a sign-in within the last 10 minutes, or the current password */
    const fresh = get("SELECT 1 ok FROM sessions WHERE sid=? AND auth_at IS NOT NULL AND auth_at > datetime('now','-10 minutes')", s.sid);
    const full = get("SELECT email FROM users WHERE id=?", user.id);
    if (!fresh && !(body.current_password && full && (await verifyUserAsync(T(s), full.email, String(body.current_password)))))
      return bad(res, "Please sign in again (or confirm your current password) to add a sign-in method", 401);
    json(res, 200, identity.linkIdentityMethod(user.id, body.method_type, body.identifier, body.metadata, body.is_primary));
  }
  function apiIdentityMethodsUnlink(req, res, url, s) {
    if (!requireStore(s, res)) return;
    const identity = require("../identity.js");
    const user = s.user_id ? get("SELECT id FROM users WHERE id=?", s.user_id) : null;
    if (!user) return bad(res, "Not authenticated", 401);
    const methodId = url.pathname.match(/\/identity-methods\/([^/]+)$/)?.[1];
    if (!methodId) return bad(res, "Method ID required", 400);
    json(res, 200, identity.unlinkIdentityMethod(user.id, methodId));
  }
  function apiIdentityMethodsSetPrimary(req, res, url, s) {
    if (!requireStore(s, res)) return;
    const identity = require("../identity.js");
    const user = s.user_id ? get("SELECT id FROM users WHERE id=?", s.user_id) : null;
    if (!user) return bad(res, "Not authenticated", 401);
    const methodId = url.pathname.match(/\/identity-methods\/([^/]+)$/)?.[1];
    if (!methodId) return bad(res, "Method ID required", 400);
    json(res, 200, identity.setPrimaryMethod(user.id, methodId));
  }
  function apiAdminUsers(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    const t = T(s);
    json(res, 200, { users: all(`SELECT id,name,email,role,created_at,(SELECT COUNT(*) FROM orders o WHERE o.owner='t${t}:u:'||users.id) orders,(SELECT COALESCE(SUM(total),0) FROM orders o WHERE o.owner='t${t}:u:'||users.id) spend FROM users WHERE tenant_id=? ORDER BY created_at DESC`, t) });
  }
  function apiAdminUserDelete(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    const u = get("SELECT * FROM users WHERE id=? AND tenant_id=?", Number(id), T(s));
    if (!u) return bad(res, "Unknown user", 404);
    if (u.role === "admin") return bad(res, "Store admins cannot be deleted here");
    run("DELETE FROM users WHERE id=?", u.id);
    run("DELETE FROM cart_items WHERE owner=?", `t${T(s)}:u:${u.id}`);
    run("UPDATE sessions SET user_id=NULL WHERE user_id=?", u.id);
    logAction(s, "user.delete", "user", id, { email: u.email });
    json(res, 200, { ok: true });
  }
  async function apiAdminAccount(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const u = get("SELECT * FROM users WHERE id=?", s.user_id);
    /* changing the sign-in password or email proves the current password first — a hijacked
       session must not be able to lock the owner out */
    if ((body.password || body.email) && !(await verifyUserAsync(T(s), u.email, String(body.current_password || ""))))
      return bad(res, "Your current password is required to change your password or email", 403);
    if (body.password) {
      const perr = sec.checkPassword(String(body.password), u.email);
      if (perr) return bad(res, perr);
      if (await passwordReusedAsync(T(s), u.email, String(body.password))) return bad(res, "You cannot reuse a previous password", 422);
      await setUserPasswordAsync(u.id, String(body.password), u.email);
      logAction(s, "account.password", "user", u.id, { upgraded: true });
    }
    if (body.email) {
      const email = String(body.email).trim().toLowerCase();
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return bad(res, "Invalid email");
      if (get("SELECT id FROM users WHERE tenant_id=? AND email=? AND id!=?", T(s), email, u.id)) return bad(res, "Email already in use", 409);
      run("UPDATE users SET email=? WHERE id=?", email, u.id);
      logAction(s, "account.email", "user", u.id, { email });
    }
    json(res, 200, { ok: true });
  }
  /* ================= PLATFORM ================= */
  async function apiPlatformLogin(req, res, url, s, body) {
    const email = String(body.email || "").trim();
    const key = sec.loginKey("platform:" + email, s.device);
    const lock = sec.lockState(key);
    if (lock.locked) return bad(res, "Account temporarily locked — retry in " + lock.retryAfterSec + "s", 423);
    const a = await verifyPlatformAdminAsync(email, String(body.password || ""));
    if (!a) { sec.noteLoginFail(key);
      return bad(res, "Invalid platform credentials", 401);
    }
    const ptid = crypto.randomBytes(20).toString("hex");
    run("INSERT INTO platform_sessions(ptid, admin_id, expires_at) VALUES(?,?,datetime('now','+12 hours'))", ptid, a.id);
    /* the mirror image of the store path: a platform sign-in no longer drops the
       client's store-user binding. One identity may hold both authorities; each
       stays scoped to its own surface */
    res.appendHeader("Set-Cookie", `azp=${ptid}; Path=/; HttpOnly; SameSite=Lax; Max-Age=43200${isTls(req) ? "; Secure" : ""}`);
    sec.noteLoginOk(key);
    rememberDevice(req, res, s, "platform:" + email);
    if (body.code) confirmPlatform(a.id, ptid, body.code);
    const ps = get("SELECT mfa_at FROM platform_sessions WHERE ptid=?", ptid);
    const step = mfa.state("platform", a.id, ps.mfa_at);
    audit(null, "platform", a.id, a.email, "platform.login", "platform", null, { mfa: step });
    json(res, 200, { ok: true, ...(step === "ok" ? {} : { mfa: step }), admin: { id: a.id, name: a.name, email: a.email } });
  }
  function apiPlatformLogout(req, res, url, s) {
    if (s.ptid) run("DELETE FROM platform_sessions WHERE ptid=?", s.ptid);
    res.setHeader("Set-Cookie", "azp=; Path=/; Max-Age=0");
    json(res, 200, { ok: true });
  }
  function apiPlatformMe(req, res, url, s) {
    json(res, 200, { admin: s.platform_admin, allowed: prbac.allowedSections(s.platform_admin), money: require("../defaults.js").platformMoney() });
  }
  function apiAuthMe(req, res, url, s) {
    const urow = s.user_id ? get("SELECT id,name,email,role,staff_role,perms,tenant_id FROM users WHERE id=?", s.user_id) : null;
    const staff = urow && urow.role === "admin" ? urow : null;
    const staffStep = staff ? mfa.state("user", staff.id, s.mfa_at) : "ok";
    const storeUser = staff && staffStep === "ok" ? staff : null;
    const identity = { store: storeUser, platform: s.platform_admin || null, tenantId: T(s) };
    json(res, 200, {
      ok: true,
      /* how platform amounts are shown (the platform's currency and locale) */
      money: require("../defaults.js").platformMoney(),
      user: s.user_id ? get("SELECT id,name,email,role FROM users WHERE id=?", s.user_id) : null,
      admin: s.platform_admin || null,
      tenant: s.tenant ? { id: s.tenant.id, slug: s.tenant.slug, name: s.tenant.name, kind: kindBrief(s.tenant) } : null,
      identity,
      /* the combined grant map, scope-namespaced: { "store:orders": "write", ... } */
      grants: authz.grant(identity),
      /* and per-scope allowance lists for the consoles' existing canSee() shapes */
      allowedSections: storeUser ? rbac.allowedSections(storeUser, T(s)) : [],
      platformAllowed: s.platform_admin ? prbac.allowedSections(s.platform_admin) : [],
      hasStore: !!storeUser, hasPlatform: !!s.platform_admin,
      /* what still stands between this sign-in and its authority: a code, or an enrolment */
      mfa: { platform: s.platform_pending ? s.platform_pending.mfa : null, store: staffStep === "ok" ? null : staffStep },
      /* the configured apps each scope may open — the console lists them in its nav */
      apps: {
        store: storeUser ? (() => { const al = rbac.allowedSections(storeUser, T(s)); return authz.appsFor(T(s)).filter(a => al.includes(a.section)).map(appInfo); })() : [],
        platform: s.platform_admin ? (() => { const al = prbac.allowedSections(s.platform_admin); return authz.configuredApps().filter(a => !a.tenant_id && al.includes(a.section)).map(appInfo); })() : []
      }
    });
  }
  /* ────────────────────────────────────────────────────────────────
     PLATFORM ADMIN ACCOUNTS — the console's own user base.

     The seed creates exactly one platform owner, and for the whole
     history of this build that was the *only* way to get a platform
     account: newPlatformAdmin() was called solely by the seed. So a
     second operator — a support admin, a second owner — had to be
     created by hand in SQLite, which is impossible in practice
     because the credentials are scrypt(v2) + peppered and the pepper
     context ("pa:" + email) is baked into the hash.

     This is the CRUD surface that fixes it. Platform-only, audited on
     the global hash-chained log, and it reuses the *same* primitives
     the seed and the login path use — newPlatformAdmin / hashPasswordFor
     / checkPassword — so a created account signs in at /platform.html
     with no second code path and no divergent hashing.
     ──────────────────────────────────────────────────────────────── */
  function apiPlatformAdmins(req, res, url, s, body) {
    if (!requirePlatformSection(s, res, "padmins", "read")) return;
    if (req.method === "GET") {
      const admins = all("SELECT id,name,email,role,kdf_version,created_at FROM platform_admins ORDER BY id").map(a => ({
        ...a,
        you: a.id === (s.platform_admin && s.platform_admin.id)
      }));
      return json(res, 200, { admins, roles: prbac.roles(), sections: platformSections(), apps: authz.configuredApps().filter(a => !a.tenant_id).map(appInfo) });
    }
    if (req.method === "POST") {
      if (!requirePlatformSection(s, res, "padmins", "write")) return;
      const name = String(body.name || "").trim();
      const email = String(body.email || "").trim().toLowerCase();
      const pw = String(body.password || "");
      const role = String(body.role || "support");
      if (name.length < 2) return bad(res, "Name must be at least 2 characters");
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return bad(res, "A valid email is required");
      if (get("SELECT id FROM platform_admins WHERE email=?", email)) return bad(res, "That email is already a platform admin", 409);
      /* the store login and the platform login refuse each other's accounts
         (see apiPlatformLogin + the store login), so an email that already
         belongs to a store console can never become a platform account */
      if (get("SELECT id FROM users WHERE email=? LIMIT 1", email)) return bad(res, "That email is already a store-console account — use a different address", 409);
      const pol = sec.checkPassword(pw, email);
      if (pol) return bad(res, pol);
      if (!prbac.role(role)) return bad(res, "Unknown platform role");
      const id = newPlatformAdmin(name, email, pw);
      run("UPDATE platform_admins SET role=? WHERE id=?", role, id);
      audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "platform_admin.create", "platform_admin", id, { name, email, role }, ipOf(req), s.trace);
      return json(res, 200, { ok: true, id });
    }
    return bad(res, "Method not allowed", 405);
  }
  function apiPlatformAdminUpdate(req, res, url, s, body, id) {
    if (!requirePlatformSection(s, res, "padmins", "write")) return;
    const aid = Number(id);
    const a = get("SELECT id,name,email,role FROM platform_admins WHERE id=?", aid);
    if (!a) return bad(res, "Platform admin not found", 404);
    const name = String(body.name || "").trim();
    const email = String(body.email || "").trim().toLowerCase();
    if (name.length < 2) return bad(res, "Name must be at least 2 characters");
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return bad(res, "A valid email is required");
    if (email !== a.email) {
      if (get("SELECT id FROM platform_admins WHERE email=?", email)) return bad(res, "That email is already a platform admin", 409);
      if (get("SELECT id FROM users WHERE email=? LIMIT 1", email)) return bad(res, "That email is already a store-console account", 409);
    }
    const pw = body.password != null ? String(body.password) : "";
    if (pw) {
      const pol = sec.checkPassword(pw, email);
      if (pol) return bad(res, pol);
    }
    /* role + per-user override layer, on the same contract as store staff roles */
    const role = body.role != null ? String(body.role) : a.role;
    if (role && !prbac.role(role)) return bad(res, "Unknown platform role");
    const perms = body.perms != null ? JSON.stringify(body.perms) : null;
    if (name !== a.name || email !== a.email) run("UPDATE platform_admins SET name=?, email=? WHERE id=?", name, email, aid);
    if (role !== a.role) run("UPDATE platform_admins SET role=? WHERE id=?", role || null, aid);
    if (perms) run("UPDATE platform_admins SET perms=? WHERE id=?", perms, aid);
    if (pw) {
      /* re-hash exactly as the seed does; the pepper context is the NEW email,
         so a rename and a reset in one call still leaves a verifiable credential */
      const salt = sec.newSalt(); const ver = sec.currentKdf();
      run("UPDATE platform_admins SET salt=?, hash=?, kdf_version=? WHERE id=?", salt, hashPasswordFor(pw, salt, ver, "pa:" + email), ver, aid);
      /* a password change invalidates every platform session this operator holds */
      run("DELETE FROM platform_sessions WHERE admin_id=?", aid);
    }
    audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "platform_admin.update", "platform_admin", aid,
      { name, email, renamed: email !== a.email, password_reset: !!pw, role: role || null, perms_changed: !!perms }, ipOf(req), s.trace);
    return json(res, 200, { ok: true });
  }
  function apiPlatformAdminDelete(req, res, url, s, body, id) {
    if (!requirePlatformSection(s, res, "padmins", "write")) return;
    const aid = Number(id);
    if (aid === Number(s.platform_admin.id)) return bad(res, "You cannot delete your own account");
    const a = get("SELECT id,email FROM platform_admins WHERE id=?", aid);
    if (!a) return bad(res, "Platform admin not found", 404);
    /* the platform must always keep one operator — the same guard the store
       console applies to its own staff (apiStaffDelete) */
    if (get("SELECT COUNT(*) c FROM platform_admins").c <= 1) return bad(res, "The platform must keep at least one admin");
    run("DELETE FROM platform_sessions WHERE admin_id=?", aid);
    run("DELETE FROM platform_admins WHERE id=?", aid);
    audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "platform_admin.delete", "platform_admin", aid, { email: a.email }, ipOf(req), s.trace);
    return json(res, 200, { ok: true });
  }
  /* ---------- user creation ----------
     An account belongs to exactly one store (UNIQUE(tenant_id,email)), so the platform
     console creates one INTO a chosen store — the store picker is the domain the role is
     scoped against. A store admin's authority is a staff role from the store surface
     (rbac); a customer carries none. The password runs through the same policy the
     storefront signup enforces, so a platform-created account is never a weak back door,
     and an omitted password is generated server-side and shown once. */
  function apiPlatformUserCreate(req, res, url, s, body) {
    if (!requirePlatformSection(s, res, "users", "write")) return;
    const tid = Number(body.tenant_id);
    if (!get("SELECT id FROM tenants WHERE id=?", tid)) return bad(res, "Choose the store this user belongs to", 400);
    const name = String(body.name || "").trim();
    const email = String(body.email || "").toLowerCase().trim();
    if (!name || !email) return bad(res, "Name and email are required", 400);
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return bad(res, "That email address is not valid", 400);
    const role = body.role === "admin" ? "admin" : "customer";
    const staffRole = role === "admin" ? String(body.staff_role || require("../defaults.js").of("staffRoles")) : null;
    if (staffRole && rbac.role(tid, staffRole) === null) return bad(res, "Unknown staff role: " + staffRole, 400);
    if (get("SELECT id FROM users WHERE tenant_id=? AND email=?", tid, email))
      return bad(res, "That email already has an account on this store", 409);
    const pw = String(body.password || crypto.randomBytes(9).toString("hex"));
    const policyErr = sec.checkPassword(pw, email);
    if (policyErr) return bad(res, policyErr, 400);
    const id = newUser(tid, name, email, pw, role);
    if (staffRole) run("UPDATE users SET staff_role=? WHERE id=?", staffRole, id);
    logAction(s, "platform.user.create", "user", id, { email, tenant_id: tid, role, staff_role: staffRole }, req);
    json(res, 200, { ok: true, id, generated: body.password ? undefined : pw });
  }
  function apiSsoGet(req, res, url, s) { if (!requireAdmin(s, res)) return; json(res, 200, { connection: enterprise.ssoConnection(T(s)) || { enabled: false } }); }
  function apiSsoSet(req, res, url, s, body) { if (!requireAdmin(s, res)) return; if (!requireSection(s, res, "settings", "write")) return; json(res, 200, enterprise.setSso(T(s), body || {})); }
  /* SSO always runs against the store this request is addressed to (subdomain / ?store= /
     cookie) — a body-supplied tenant_id let one store's callback sign a user into another */
  function apiSsoStart(req, res, url, s, body) { const r = enterprise.ssoStart(T(s), String(body.email || "")); if (r.error) return bad(res, r.error, 400); json(res, 200, r); }
  function apiSsoCallback(req, res, url, s, body) {
    return (async () => {
      const idToken = String(body.id_token || "");
      const r = enterprise.oidcComplete(T(s), idToken, body.state ? String(body.state) : null);
      if (!r.ok) return bad(res, r.error, 401);
      establishSession(req, res, s, r.userId, "auth.sso_login", { email: r.email });
      json(res, 200, { ok: true, user: { id: r.userId, email: r.email, role: r.role } });
    })();
  }
  function apiScimUsersList(req, res, url, s) { return (async () => { const t = Number(url.searchParams.get("tenant_id") || 1); const bearer = (req.headers.authorization || "").replace(/^Bearer\s+/i, ""); if (!enterprise.scimAuth(t, bearer)) return bad(res, "Invalid SCIM token", 401); json(res, 200, Object.assign({ schemas: "urn:ietf:params:scim:api:messages:2.0:ListResponse" }, await enterprise.scimList(t))); })(); }
  function apiScimUserCreate(req, res, url, s, body) { return (async () => { const t = Number(url.searchParams.get("tenant_id") || (body && body._tenant) || 1); const bearer = (req.headers.authorization || "").replace(/^Bearer\s+/i, ""); if (!enterprise.scimAuth(t, bearer)) return bad(res, "Invalid SCIM token", 401); const r = await enterprise.scimCreate(t, body || {}); if (r.error) return bad(res, r.error, 400); json(res, 201, r); })(); }
  function apiScimToken(req, res, url, s, body) { if (!requireAdmin(s, res)) return; const t = T(s); const r = enterprise.createScim(t, body && body.label); logAction(s, "scim.token", "scim_token", r.id, {}, req); json(res, 200, { id: r.id, token: r.token, note: "store this token now; only a hash is kept" }); }
  /* ========== Identity Templates APIs ========== */
  function apiIdentityTemplates(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    if (req.method === 'GET') {
      const templates = all("SELECT * FROM platform_identity_templates ORDER BY is_default DESC, created_at");
      return json(res, 200, { templates });
    }
    if (req.method === 'POST') {
      const { name, description, config, is_default } = body || {};
      if (!name) return bad(res, 'name required', 400);
      const isDef = is_default ? 1 : 0;
      const id = Number(run("INSERT INTO platform_identity_templates(name,description,config,is_default) VALUES(?,?,?,?)",
        name, description || '', JSON.stringify(config || {}), isDef).lastInsertRowid);
      return json(res, 200, { ok: true, id });
    }
    if (req.method === 'DELETE') {
      const id = url.pathname.match(/\/identity-templates\/(\d+)/)?.[1];
      if (!id) return bad(res, 'id required', 400);
      run("DELETE FROM platform_identity_templates WHERE id=?", id);
      return json(res, 200, { ok: true });
    }
    return bad(res, 'Method not allowed', 405);
  }
  function apiIdentityTemplate(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    const id = url.pathname.match(/\/identity-templates\/(\d+)/)?.[1];
    if (!id) return bad(res, 'id required', 400);
    if (req.method === 'GET') {
      const template = get("SELECT * FROM platform_identity_templates WHERE id=?", id);
      if (!template) return bad(res, 'template not found', 404);
      return json(res, 200, { template: { ...template, config: JSON.parse(template.config || '{}') } });
    }
    if (req.method === 'PUT') {
      const { name, description, config, is_default } = body || {};
      if (!name) return bad(res, 'name required', 400);
      const isDef = is_default ? 1 : 0;
      run("UPDATE platform_identity_templates SET name=?,description=?,config=?,is_default=? WHERE id=?",
        name, description || '', JSON.stringify(config || {}), isDef, id);
      return json(res, 200, { ok: true });
    }
    return bad(res, 'Method not allowed', 405);
  }
  /* Apply a global identity template to ANY store — the platform console configures every
     tenant, so the target is a body parameter (validated against the tenants table), never a
     hardcoded store. Mirrors the provisioning path's apply logic exactly so the two cannot
     drift. Platform-only: writing another store's identity settings is a platform action. */
  function apiIdentityTemplateApply(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    const id = url.pathname.match(/\/identity-templates\/(\d+)\/apply$/)?.[1];
    if (!id) return bad(res, 'template id required', 400);
    const tmpl = get("SELECT config FROM platform_identity_templates WHERE id=?", id);
    if (!tmpl) return bad(res, 'template not found', 404);
    const tid = Number(body && body.tenant_id);
    const t = get("SELECT id, slug FROM tenants WHERE id=?", tid);
    if (!t) return bad(res, 'unknown tenant_id', 400);
    const config = J(tmpl.config, {});
    const identity = require("../identity.js");
    const settings = identity.setIdentitySettings(tid, config);
    let providers = 0;
    if (Array.isArray(config.providers)) for (const p of config.providers) { try { identity.upsertIdentityProvider(tid, p); providers++; } catch (e) { } }
    audit(T(s) || null, 'platform', s.platform_admin.id, s.platform_admin.email, 'identity.template.apply', 'tenant', tid, { template: Number(id), providers });
    return json(res, 200, { ok: true, tenant_id: tid, slug: t.slug, settings, providers });
  }
  /* ========== Identity Provider Types (registry vocabulary) ========== */
  function apiIdentityProviderTypes(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    const identity = require("../identity.js");
    if (req.method === 'GET') return json(res, 200, { types: identity.getProviderTypes() });
    return bad(res, 'Method not allowed', 405);
  }
  /* a new authentication KIND is platform vocabulary — authoring it is a platform action, and
     the console's provider-type form is the only writer. Idempotent by key. */
  function apiIdentityProviderTypeCreate(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    const identity = require("../identity.js");
    const r = identity.createProviderType(body || {});
    if (!r.ok) return bad(res, r.error, 400);
    return json(res, 200, r);
  }

  return [
    ["GET /api/session", apiSession],
    ["POST /api/auth/register", apiRegister],
    ["POST /api/auth/login", apiLogin],
    ["POST /api/auth/logout", apiLogout],
    ["POST /api/auth/token-exchange", apiTokenExchange],
    ["GET /api/admin/users", apiAdminUsers],
    ["DELETE /api/admin/users/:id", (r, re, u, s, b, p) => apiAdminUserDelete(r, re, u, s, b, p)],
    ["PUT /api/admin/account", apiAdminAccount],
    ["GET /api/platform/identity-templates", apiIdentityTemplates],
    ["POST /api/platform/identity-templates", apiIdentityTemplates],
    ["DELETE /api/platform/identity-templates/:id", apiIdentityTemplates],
    ["GET /api/platform/identity-templates/:id", apiIdentityTemplate],
    ["PUT /api/platform/identity-templates/:id", apiIdentityTemplate],
    ["POST /api/platform/identity-templates/:id/apply", apiIdentityTemplateApply],
    ["GET /api/admin/sso", apiSsoGet],
    ["PUT /api/admin/sso", apiSsoSet],
    ["POST /api/auth/sso/start", apiSsoStart],
    ["POST /api/auth/sso/callback", apiSsoCallback],
    ["GET /api/admin/identity-providers", apiIdentityProvidersGet],
    ["PUT /api/admin/identity-providers", apiIdentityProvidersPut],
    ["DELETE /api/admin/identity-providers/:id", apiIdentityProviderDelete],
    ["GET /api/admin/identity-provider-types", apiIdentityProviderTypes],
    ["POST /api/admin/identity-provider-types", apiIdentityProviderTypeCreate],
    ["GET /api/admin/identity-settings", apiIdentitySettingsGet],
    ["PUT /api/admin/identity-settings", apiIdentitySettingsPut],
    ["GET /api/auth/mfa", apiMfaStatus],
    ["POST /api/auth/mfa/verify", apiMfaVerify],
    ["POST /api/auth/mfa/start", apiMfaStart],
    ["POST /api/auth/mfa/confirm", apiMfaConfirm],
    ["POST /api/auth/mfa/remove", apiMfaRemove],
    ["GET /api/platform/mfa", apiMfaStatus],
    ["POST /api/platform/mfa/verify", apiMfaVerify],
    ["POST /api/platform/mfa/start", apiMfaStart],
    ["POST /api/platform/mfa/confirm", apiMfaConfirm],
    ["POST /api/platform/mfa/remove", apiMfaRemove],
    ["POST /api/platform/admins/:id/mfa-reset", (r, re, u, s, b, p) => apiPlatformAdminMfaReset(r, re, u, s, b, p)],
    ["POST /api/admin/staff/:id/mfa-reset", (r, re, u, s, b, p) => apiStaffMfaReset(r, re, u, s, b, p)],
    ["POST /api/auth/email/verify", apiEmailVerify],
    ["POST /api/auth/email/send", apiEmailVerifySend],
    ["POST /api/auth/password/forgot", apiPasswordForgot],
    ["POST /api/auth/password/reset", apiPasswordReset],
    ["POST /api/auth/login-init", apiLoginInit],
    ["POST /api/auth/login/otp", apiLoginOtpVerify],
    ["POST /api/auth/login/magic", apiLoginMagicLinkVerify],
    ["POST /api/auth/login/biometric", apiLoginBiometricVerify],
    ["POST /api/auth/biometric/register", apiBiometricRegister],
    ["POST /api/auth/login/callback", apiLoginCallback],
    ["GET /api/auth/methods", apiAuthMethods],
    ["GET /api/user/identity-methods", apiIdentityMethodsGet],
    ["POST /api/user/identity-methods", apiIdentityMethodsLink],
    ["DELETE /api/user/identity-methods/:id", apiIdentityMethodsUnlink],
    ["PUT /api/user/identity-methods/:id/primary", apiIdentityMethodsSetPrimary],
    ["GET /api/scim/Users", apiScimUsersList],
    ["POST /api/scim/Users", apiScimUserCreate],
    ["POST /api/admin/scim/token", apiScimToken],
    ["POST /api/platform/login", apiPlatformLogin],
    ["POST /api/platform/logout", apiPlatformLogout],
    ["GET /api/platform/me", apiPlatformMe],
    ["GET /api/auth/me", apiAuthMe],
    ["GET /api/platform/admins", apiPlatformAdmins],
    ["POST /api/platform/admins", apiPlatformAdmins],
    ["PUT /api/platform/admins/:id", (r, re, u, s, b, p) => apiPlatformAdminUpdate(r, re, u, s, b, p)],
    ["DELETE /api/platform/admins/:id", (r, re, u, s, b, p) => apiPlatformAdminDelete(r, re, u, s, b, p)],
    ["POST /api/platform/users", apiPlatformUserCreate]
  ];
} };
