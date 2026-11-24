/* LUXORA Platform — the second factor for people who run a platform or a store.

   A subject is a platform admin or a store user. They enrol an authenticator app (RFC 6238): the
   secret is sealed to them, and becomes active only once a code from it is confirmed, which also
   gives ten single-use recovery codes, kept only as digests. A code is accepted once: the time step
   it belongs to is remembered, and it and every earlier one are refused from then on.

   A session holds whether ITS sign-in was confirmed. `state` says what stands between a session and
   the authority it would carry: nothing (`ok`), a code (`verify`), or an enrolment (`setup`, where
   the policy requires a second factor of that subject in production). */
"use strict";

const crypto = require("crypto");
const db = () => require("./db.js");
const sec = () => require("./security.js");
const identity = () => require("./identity.js");
const fail = (msg, status) => Object.assign(new Error(msg), { status: status || 400 });
const STEP = 30, DIGITS = 6, RECOVERY = 10;
const ctx = (scope, id) => "mfa:" + scope + ":" + Number(id);
const digest = code => sec().blindIndex(String(code).toUpperCase().replace(/[^A-Z0-9]/g, ""), "mfa.recovery");

const rowOf = (scope, id) => db().get("SELECT * FROM mfa_factors WHERE scope=? AND subject_id=?", String(scope), Number(id));
const enrolled = (scope, id) => { const r = rowOf(scope, id); return !!(r && r.active); };
/* does the policy ask a second factor of this subject? As with every production guard, a
   development or test boot is left to sign in with its seed accounts */
function required(scope) {
  if (process.env.NODE_ENV !== "production") return false;
  const p = sec().policy();
  return scope === "platform" ? p.platformMfaRequired !== false : p.staffMfaRequired !== false;
}
function state(scope, id, confirmedAt) {
  if (enrolled(scope, id)) return confirmedAt ? "ok" : "verify";
  return required(scope) ? "setup" : "ok";
}
/* start: a fresh secret, not yet active. An active factor is replaced only by its owner, confirmed. */
function start(scope, id, label, issuer) {
  const secret = crypto.randomBytes(20);
  const b32 = identity().b32Encode(secret);
  db().run("INSERT INTO mfa_factors(scope,subject_id,pending) VALUES(?,?,?) ON CONFLICT(scope,subject_id) DO UPDATE SET pending=excluded.pending",
    String(scope), Number(id), sec().encryptSecret(b32, ctx(scope, id)));
  return { secret: b32, uri: "otpauth://totp/" + encodeURIComponent(issuer + ":" + label) + "?secret=" + b32 + "&issuer=" + encodeURIComponent(issuer) + "&digits=" + DIGITS + "&period=" + STEP };
}
/* the time step a code is valid for now (one step of clock drift either way), or null */
function stepOf(secret, code) {
  const c = String(code || "").replace(/\s/g, "");
  if (!new RegExp("^\\d{" + DIGITS + "}$").test(c)) return null;
  const now = Math.floor(Date.now() / 1000 / STEP);
  for (const s of [now, now - 1, now + 1]) {
    const want = identity().computeTotp(secret, STEP, DIGITS, s * STEP * 1000);
    if (crypto.timingSafeEqual(Buffer.from(want), Buffer.from(c))) return s;
  }
  return null;
}
function confirm(scope, id, code) {
  const r = rowOf(scope, id);
  if (!r || !r.pending) throw fail("Start the set-up again", 409);
  const secret = sec().safeDecrypt(r.pending, ctx(scope, id));
  const step = stepOf(secret, code);
  if (step == null) throw fail("That code is not right — check your phone's clock and try the next one", 401);
  const codes = Array.from({ length: RECOVERY }, () => crypto.randomBytes(5).toString("hex").toUpperCase().replace(/(.{5})/, "$1-"));
  db().run("UPDATE mfa_factors SET secret=pending, pending=NULL, active=1, last_step=?, recovery=?, confirmed_at=datetime('now') WHERE id=?", step, JSON.stringify(codes.map(digest)), r.id);
  return { recovery: codes };
}
/* a code from the app, or a recovery code (used up) */
function verify(scope, id, code) {
  const r = rowOf(scope, id);
  if (!r || !r.active) return false;
  const step = stepOf(sec().safeDecrypt(r.secret, ctx(scope, id)), code);
  if (step != null) return !!db().run("UPDATE mfa_factors SET last_step=? WHERE id=? AND last_step<?", step, r.id, step).changes;
  const clean = String(code || "").toUpperCase().replace(/[^A-Z0-9]/g, "");
  if (clean.length !== 10) return false;
  const left = JSON.parse(r.recovery || "[]"), d = digest(clean);
  if (!left.includes(d)) return false;
  return !!db().run("UPDATE mfa_factors SET recovery=? WHERE id=? AND recovery=?", JSON.stringify(left.filter(x => x !== d)), r.id, r.recovery).changes;
}
/* removed by its owner with a code, or for someone locked out by a person who may manage them */
function remove(scope, id) { return !!db().run("DELETE FROM mfa_factors WHERE scope=? AND subject_id=?", String(scope), Number(id)).changes; }
function status(scope, id) {
  const r = rowOf(scope, id);
  return { enrolled: !!(r && r.active), required: required(scope), recoveryLeft: r && r.active ? JSON.parse(r.recovery || "[]").length : 0 };
}

module.exports = { state, start, confirm, verify, remove, status, enrolled, required };
