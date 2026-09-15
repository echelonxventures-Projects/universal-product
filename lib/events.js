/* LUXORA Platform — event bus + declarative outbound webhooks.
   One place emits domain events; matching tenant webhooks get an HMAC-signed POST. Delivery is
   offline-safe (queued + skipped when no endpoint / LX_OFFLINE / test transport) so nothing blocks a
   request or hits the network unintentionally. The event catalog is DATA (meta_lists.webhookEvents)
   so new event types need no code. Retries ride the configured queue/backoff via drain(). */
"use strict";

let _db = null; const db = () => _db || (_db = require("./db.js"));
const crypto = require("crypto");
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };

const EVENTS = ["order.created", "order.paid", "order.refunded", "coupon.redeemed", "ai.usage",
  "invoice.created", "invoice.paid", "offer.created", "product.reviewed", "customer.created", "store.launched"];

let fetchFn = (...a) => fetch(...a);
function __setTransport(f) { const prev = fetchFn; fetchFn = f || ((...a) => fetch(...a)); return prev; }
function offline() { return process.env.LX_OFFLINE === "1"; }
function seed() { db().run("INSERT OR IGNORE INTO meta_lists(name,label,items) VALUES('webhookEvents','webhookEvents',?)", JSON.stringify(EVENTS)); }

function sign(secret, body) { return "sha256=" + crypto.createHmac("sha256", secret || "").update(body).digest("hex"); }
function matchWebhooks(tenantId, event) {
  return db().all("SELECT * FROM webhooks WHERE tenant_id=? AND active=1", tenantId).map(w => ({ ...w, events: J(w.events, ["*"]) }))
    .filter(w => w.events.includes("*") || w.events.includes(event));
}

/* emit: record a delivery per matching webhook, attempt immediately unless offline */
function emit(tenantId, event, data, opts) {
  opts = opts || {}; const D = db();
  const payload = JSON.stringify({ id: crypto.randomBytes(8).toString("hex"), event, at: new Date().toISOString(), uid: opts.uid || null, data: data || {} });
  const whs = matchWebhooks(tenantId, event); const ids = [];
  for (const w of whs) {
    const r = D.run("INSERT INTO webhook_deliveries(tenant_id,webhook_id,event,subject_uid,payload,status,attempts,created_at) VALUES(?,?,?,?,?, 'queued', 0, datetime('now'))", tenantId, w.id, event, opts.uid || null, payload);
    const did = Number(r.lastInsertRowid); ids.push(did);
    if (!offline()) deliver(did).catch(() => { });
  }
  return ids;
}
async function deliver(deliveryId) {
  const D = db(); const row = D.get("SELECT * FROM webhook_deliveries WHERE id=?", Number(deliveryId)); if (!row) return { error: "no delivery" };
  const w = D.get("SELECT * FROM webhooks WHERE id=?", row.webhook_id); if (!w) { D.run("UPDATE webhook_deliveries SET status='skipped' WHERE id=?", row.id); return { skipped: true }; }
  const body = row.payload; const headers = { "content-type": "application/json", "user-agent": "LUXORA-Webhooks/1", "x-lux-event": row.event, "x-lux-delivery": String(row.id), "x-lux-signature": sign(w.secret, body) };
  D.run("UPDATE webhook_deliveries SET attempts=attempts+1, status='in_flight' WHERE id=?", row.id);
  try {
    const ac = new AbortController(); const to = setTimeout(() => ac.abort(), 10000);
    let r = { status: 0 }; try { r = await fetchFn(w.url, { method: "POST", headers, body, signal: ac.signal }); } finally { clearTimeout(to); }
    const text = r && r.text ? await Promise.resolve(r.text()).catch(() => "") : "";
    const ok = r && r.status >= 200 && r.status < 300;
    D.run("UPDATE webhook_deliveries SET status=?, response=?, next_retry_at=? WHERE id=?", ok ? "delivered" : "failed", String(r && r.status) + " " + String(text).slice(0, 200), ok ? null : new Date(Date.now() + 60000 * Math.pow(2, Math.min(6, (r && row.attempts) || 1))).toISOString(), row.id);
    return { ok, status: r && r.status };
  } catch (e) { D.run("UPDATE webhook_deliveries SET status='failed', response=? WHERE id=?", String(e.message).slice(0, 200), row.id); return { ok: false, error: e.message }; }
}
async function drain(tenantId, max) { const D = db(); const rows = D.all("SELECT id FROM webhook_deliveries WHERE status IN ('queued','failed') AND (next_retry_at IS NULL OR next_retry_at<=datetime('now')) AND (?=0 OR tenant_id=?) ORDER BY id LIMIT ?", tenantId || 0, tenantId || 0, Math.min(100, max || 25)); let n = 0; for (const r of rows) { if (offline()) break; await deliver(r.id); n++; } return { drained: n, remaining: D.get("SELECT COUNT(*) c FROM webhook_deliveries WHERE status IN ('queued','failed')").c }; }

function webhookEvents() { return J((db().get("SELECT items i FROM meta_lists WHERE name='webhookEvents'") || {}).i, EVENTS); }
function list(tenantId) { const rows = db().all("SELECT * FROM webhooks WHERE (?=0 OR tenant_id=?) ORDER BY id DESC", tenantId || 0, tenantId || 0).map(w => ({ ...w, events: J(w.events, []) })); const recent = db().all("SELECT id,webhook_id,event,status,attempts,response,created_at FROM webhook_deliveries WHERE (?=0 OR tenant_id=?) ORDER BY id DESC LIMIT 100", tenantId || 0, tenantId || 0); return { webhooks: rows, deliveries: recent }; }
function create(tenantId, body) { const ev = Array.isArray(body.events) && body.events.length ? body.events : ["*"]; const id = Number(db().run("INSERT INTO webhooks(tenant_id,url,secret,events,active,description) VALUES(?,?,?,?,?,?)", tenantId, String(body.url), String(body.secret || ""), JSON.stringify(ev), body.active === false ? 0 : 1, String(body.description || "")).lastInsertRowid); return id; }
function update(id, tenantId, body) { const D = db(); const w = D.get("SELECT * FROM webhooks WHERE id=? AND tenant_id=?", Number(id), tenantId); if (!w) return false; const ev = Array.isArray(body.events) && body.events.length ? body.events : J(w.events, ["*"]); D.run("UPDATE webhooks SET url=?, secret=?, events=?, active=?, description=?, updated_at=datetime('now') WHERE id=?", String(body.url || w.url), body.secret != null ? String(body.secret) : w.secret, JSON.stringify(ev), body.active != null ? (body.active ? 1 : 0) : w.active, body.description != null ? String(body.description) : w.description, Number(id)); return true; }
function remove(id, tenantId) { return db().run("DELETE FROM webhooks WHERE id=? AND tenant_id=?", Number(id), tenantId).changes > 0; }
/* verify an inbound payload (for consumers/testing inbound signature validation) */
function verify(secret, body, headerSig) { const expect = sign(secret, typeof body === "string" ? body : JSON.stringify(body)); const a = Buffer.from(expect); const b = Buffer.from(String(headerSig || "")); return a.length === b.length && crypto.timingSafeEqual(a, b); }

module.exports = { EVENTS, seed, emit, deliver, drain, list, create, update, remove, webhookEvents, verify, sign, __setTransport };
