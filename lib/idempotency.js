/* LUXORA Platform — idempotency for mutations (safe client retries).
   A client may send `Idempotency-Key` on POST/PUT/DELETE /api. The first request runs and its
   response is stored (key → status+body, TTL). Replays short-circuit with the stored response so a
   retried "place order" / "capture payment" never double-executes. Scoping is per-tenant + method
   + path + request-hash so a key reused with a different payload is rejected (422), not silently
   applied. Disabled entirely with LX_IDEMPOTENCY=0. */
"use strict";

let _db = null; const db = () => _db || (_db = require("./db.js"));
const crypto = require("crypto");
const HOUR = 24 * 3600 * 1000;

function enabled() { return process.env.LX_IDEMPOTENCY !== "0"; }
function hash(method, path, body) { return crypto.createHash("sha256").update(method + "|" + path + "|" + JSON.stringify(body || {})).digest("hex").slice(0, 32); }
function lookup(key, tenantId) {
  if (!key) return null; const D = db();
  const row = D.get("SELECT * FROM idempotency_keys WHERE key=? AND (tenant_id IS NULL OR tenant_id=?)", key, tenantId || 0);
  if (!row) return null;
  if (row.expires_at && new Date(row.expires_at).getTime() < Date.now()) { D.run("DELETE FROM idempotency_keys WHERE key=?", key); return null; }
  return row;
}
function claim(key, tenantId, method, path, body) {
  if (!key) return { fresh: true };
  const D = db(); const rh = hash(method, path, body);
  const ex = lookup(key, tenantId);
  if (ex) return ex.request_hash === rh ? { replay: ex } : { conflict: true };
  D.run("INSERT INTO idempotency_keys(key,tenant_id,method,path,request_hash,status,created_at,expires_at) VALUES(?,?,?,?,?,?,datetime('now'),datetime('now','+1 day'))", key, tenantId || 0, method, path, rh, 0);
  return { fresh: true };
}
function store(key, tenantId, status, response) { if (!key) return; db().run("UPDATE idempotency_keys SET status=?, response=? WHERE key=?", status, JSON.stringify(response || null), key); }
function purge() { db().run("DELETE FROM idempotency_keys WHERE expires_at < datetime('now')"); return { ok: true }; }

module.exports = { enabled, lookup, claim, store, purge, hash };
