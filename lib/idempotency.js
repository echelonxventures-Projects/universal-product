/* LUXORA Platform — idempotency for mutations (safe client retries).
   A client may send `Idempotency-Key` on POST/PUT/DELETE /api. The first request runs and its
   response is stored (key → status+body, TTL). Replays short-circuit with the stored response so a
   retried "place order" / "capture payment" never double-executes.

   Scoping: a key belongs to ONE caller — tenant + principal (the signed-in user, the platform
   admin, or the anonymous session). It is stored as a hash of that scope, so two callers that
   happen to pick the same key never see each other's responses (a replay used to hand one
   shopper another shopper's stored response) and never collide on the table's primary key.
   Within a scope the method + path + request-hash must match, so a key reused with a different
   payload is rejected (422), not silently applied.

   Lifecycle: a claimed-but-unfinished key answers 409 (a concurrent retry must not be told the
   operation succeeded while it is still running); a 5xx response is NOT kept, so a retry after a
   server failure runs again instead of replaying the failure for a day; expired rows are purged
   on a timer started by the server. Disabled entirely with LX_IDEMPOTENCY=0. */
"use strict";

let _db = null; const db = () => _db || (_db = require("./db.js"));
const crypto = require("crypto");

function enabled() { return process.env.LX_IDEMPOTENCY !== "0"; }
function hash(method, path, body) { return crypto.createHash("sha256").update(method + "|" + path + "|" + JSON.stringify(body || {})).digest("hex").slice(0, 32); }
/* the stored key: the caller's key bound to tenant + principal */
function scoped(key, tenantId, principal) {
  return "ik_" + crypto.createHash("sha256").update(String(tenantId || 0) + "|" + String(principal || "") + "|" + String(key)).digest("hex");
}
function lookup(skey) {
  if (!skey) return null; const D = db();
  const row = D.get("SELECT * FROM idempotency_keys WHERE key=?", skey);
  if (!row) return null;
  if (row.expires_at && new Date(row.expires_at.replace(" ", "T") + "Z").getTime() < Date.now()) { D.run("DELETE FROM idempotency_keys WHERE key=?", skey); return null; }
  return row;
}
function claim(key, tenantId, principal, method, path, body) {
  if (!key) return { fresh: true };
  const D = db(); const rh = hash(method, path, body); const skey = scoped(key, tenantId, principal);
  const ex = lookup(skey);
  if (ex) {
    if (ex.request_hash !== rh || ex.method !== method || ex.path !== path) return { conflict: true, skey };
    if (!ex.status) return { inflight: true, skey };
    return { replay: ex, skey };
  }
  D.run("INSERT INTO idempotency_keys(key,tenant_id,method,path,request_hash,status,created_at,expires_at) VALUES(?,?,?,?,?,?,datetime('now'),datetime('now','+1 day'))", skey, tenantId || 0, method, path, rh, 0);
  return { fresh: true, skey };
}
function store(skey, status, response) {
  if (!skey) return;
  /* a server failure is not an outcome worth replaying — release the key so a retry runs */
  if (!status || status >= 500) { db().run("DELETE FROM idempotency_keys WHERE key=?", skey); return; }
  db().run("UPDATE idempotency_keys SET status=?, response=? WHERE key=?", status, typeof response === "string" ? response : JSON.stringify(response == null ? null : response), skey);
}
function purge() { db().run("DELETE FROM idempotency_keys WHERE expires_at < datetime('now')"); return { ok: true }; }

module.exports = { enabled, lookup, claim, store, purge, hash, scoped };
