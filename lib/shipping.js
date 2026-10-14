/* LUXORA Platform - Shipping tracking module
   A per-store parcel ledger: tracking numbers registered by staff, advanced by carrier
   webhooks (handleWebhook). Carrier provider rows hold credentials for a future live
   integration; no carrier rate/label/tracking API is called today, and quote/label say so
   (501) rather than inventing data. */
"use strict";

const db = () => require("./db.js");
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d || {}; } };
const nowIso = () => new Date().toISOString();

/* ═══════════════ 1 · TABLES ═══════════════ */
function seed() {
  const run = (sql, ...params) => { try { db().run(sql, ...params); } catch (e) { } };
  
  run(`CREATE TABLE IF NOT EXISTS shipping_providers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_id TEXT UNIQUE,
    name TEXT,
    carrier_type TEXT DEFAULT 'api',
    status TEXT DEFAULT 'inactive',
    config TEXT DEFAULT '{}',
    enabled_countries TEXT DEFAULT '[]',
    services TEXT DEFAULT '[]',
    created_at TEXT DEFAULT (datetime('now')),
    uid TEXT
  )`);
  
  run(`CREATE TABLE IF NOT EXISTS package_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER REFERENCES orders(id),
    order_num TEXT,
    tracking_number TEXT UNIQUE,
    provider_id TEXT,
    carrier_type TEXT DEFAULT 'api',
    status TEXT DEFAULT 'pending',
    origin_address TEXT DEFAULT '{}',
    destination_address TEXT DEFAULT '{}',
    package_weight REAL,
    package_dimensions TEXT DEFAULT '{}',
    service_type TEXT,
    estimated_delivery TEXT,
    events TEXT DEFAULT '[]',
    current_location TEXT DEFAULT '{}',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    uid TEXT
  )`);
  
  /* tracking rows were unscoped — every store read every other store's parcels */
  run(`ALTER TABLE package_tracking ADD COLUMN tenant_id INTEGER`);
  run(`CREATE INDEX IF NOT EXISTS ix_package_tracking_tenant ON package_tracking(tenant_id, tracking_number)`);

  run(`CREATE TABLE IF NOT EXISTS shipping_quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER REFERENCES orders(id),
    tracking_id INTEGER REFERENCES package_tracking(id),
    provider_id TEXT,
    service_type TEXT,
    price REAL,
    currency TEXT DEFAULT 'USD',
    transit_days INTEGER,
    guaranteed_delivery TEXT,
    status TEXT DEFAULT 'pending',
    created_at TEXT DEFAULT (datetime('now')),
    uid TEXT
  )`);
}

/* ═══════════════ 2 · PROVIDER CONFIG ═══════════════ */
/* provider rows hold carrier API credentials — a listing never returns the config itself,
   only whether one is present */
function publicProvider(p) {
  if (!p) return null;
  const cfg = J(p.config, {});
  const { config, ...rest } = p;
  return { ...rest, configured: !!(cfg.apiKey || cfg.token || cfg.key), enabled_countries: J(p.enabled_countries, []), services: J(p.services, []) };
}
function getProviders(tenantId) {
  return db().all('SELECT * FROM shipping_providers WHERE status=? ORDER BY name', 'active').map(publicProvider);
}

function getProvider(providerId) {
  return db().get('SELECT * FROM shipping_providers WHERE provider_id=? AND status=?', providerId, 'active') || null;
}

/* configuring a provider is how it becomes active — so the lookup cannot require it to be
   active already (it did, so no provider could ever be configured) */
function updateProviderConfig(providerId, config) {
  const provider = db().get('SELECT * FROM shipping_providers WHERE provider_id=?', String(providerId || ''));
  if (!provider) return { error: 'Provider not found', code: 404 };
  if (!config || typeof config !== 'object' || Array.isArray(config)) return { error: 'config object required', code: 400 };
  const merged = { ...J(provider.config, {}), ...config };
  db().run('UPDATE shipping_providers SET config=?, status=? WHERE provider_id=?',
    JSON.stringify(merged), merged.apiKey ? 'active' : 'inactive', provider.provider_id);
  return publicProvider(db().get('SELECT * FROM shipping_providers WHERE provider_id=?', provider.provider_id));
}

/* ═══════════════ 3 · TRACKING ═══════════════ */
/* every tracking row belongs to one store; reads and writes are scoped by tenant */
function createTracking(tenantId, input) {
  const t = input || {};
  const trackingNumber = String(t.tracking_number || '').trim();
  if (!trackingNumber) return { error: 'tracking_number required', code: 400 };
  if (db().get('SELECT id FROM package_tracking WHERE tracking_number=?', trackingNumber)) return { error: 'tracking number already registered', code: 409 };
  if (t.order_id != null && !db().get('SELECT id FROM orders WHERE id=? AND tenant_id=?', Number(t.order_id), tenantId)) return { error: 'Unknown order', code: 404 };
  db().run(
    'INSERT INTO package_tracking(tenant_id, order_id, order_num, tracking_number, provider_id, origin_address, destination_address, package_weight, package_dimensions) VALUES(?,?,?,?,?,?,?,?,?)',
    tenantId, t.order_id == null ? null : Number(t.order_id), t.order_num == null ? null : String(t.order_num), trackingNumber,
    t.provider_id == null ? null : String(t.provider_id), JSON.stringify(t.origin || {}), JSON.stringify(t.destination || {}),
    t.weight == null ? null : Number(t.weight), JSON.stringify(t.dimensions || {})
  );
  return track(tenantId, trackingNumber);
}

function track(tenantId, trackingNumber) {
  const existing = db().get('SELECT * FROM package_tracking WHERE tracking_number=? AND tenant_id=?', String(trackingNumber || ''), tenantId);
  if (!existing) return { error: 'Tracking number not found', code: 404 };
  const provider = getProvider(existing.provider_id);
  /* status/events advance through carrier webhooks (handleWebhook) or staff updates;
     there is no polling integration with carrier APIs */
  return {
    tracking_number: existing.tracking_number,
    provider: provider ? { id: provider.provider_id, name: provider.name } : null,
    order_id: existing.order_id,
    status: existing.status || 'pending',
    origin: J(existing.origin_address, {}),
    destination: J(existing.destination_address, {}),
    estimated_delivery: existing.estimated_delivery,
    events: J(existing.events, []),
    current_location: J(existing.current_location, {}),
    created_at: existing.created_at
  };
}

const TRACKING_EDITABLE = ['status', 'estimated_delivery', 'service_type', 'package_weight'];
function updateTracking(tenantId, trackingId, updates) {
  const existing = db().get('SELECT * FROM package_tracking WHERE id=? AND tenant_id=?', Number(trackingId), tenantId);
  if (!existing) return { error: 'Tracking not found', code: 404 };
  const cols = [], vals = [];
  for (const [key, value] of Object.entries(updates || {})) {
    if (!TRACKING_EDITABLE.includes(key)) continue;
    cols.push(key + '=?'); vals.push(value == null ? null : String(value));
  }
  db().run('UPDATE package_tracking SET ' + cols.concat('updated_at=?').join(', ') + ' WHERE id=?', ...vals, nowIso(), existing.id);
  return track(tenantId, existing.tracking_number);
}

function listTracking(tenantId, orderId) {
  return db().all('SELECT * FROM package_tracking WHERE tenant_id=? AND order_id=? ORDER BY created_at DESC', tenantId, Number(orderId));
}

/* ═══════════════ 4 · RATE QUOTES + LABELS ═══════════════ */
/* No carrier rate or label API is integrated. These used to return invented prices and an
   example.com label URL, which a caller could not tell apart from a real quote. They now
   say so; store shipping rates come from the store's own shipping settings and the 3PL
   carriers registry (GET /api/carriers). */
const NOT_INTEGRATED = { error: 'No live carrier rate/label integration is configured for this platform', code: 501 };
function getQuote(input) { return NOT_INTEGRATED; }
function saveLabel(input) { return NOT_INTEGRATED; }

/* ═══════════════ 5 · WEBHOOKS ═══════════════ */
function handleWebhook(providerId, payload) {
  const p = payload || {};
  const trackingNumber = p.tracking_number || p.trackingNumber;
  const status = String(p.status || p.currentStatus || '').toLowerCase();
  if (!trackingNumber || !status) return { error: 'tracking_number and status required', code: 400 };
  const tracking = db().get('SELECT * FROM package_tracking WHERE tracking_number=? AND provider_id=?', String(trackingNumber), String(providerId || ''));
  if (!tracking) return { error: 'Tracking not found', code: 404 };
  const events = J(tracking.events, []);
  events.push({ status, location: p.location || {}, description: String(p.description || ''), timestamp: p.timestamp || nowIso() });
  db().run('UPDATE package_tracking SET status=?, events=?, updated_at=? WHERE id=?', status, JSON.stringify(events), nowIso(), tracking.id);
  return { ok: true, tracking_id: tracking.id };
}

module.exports = {
  seed,
  /* providers */ getProviders, getProvider, updateProviderConfig,
  /* tracking */ createTracking, track, updateTracking, listTracking,
  /* quotes */ getQuote, saveLabel,
  /* webhooks */ handleWebhook
};
