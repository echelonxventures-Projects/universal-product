/* LUXORA Platform - Shipping: live carrier rates, labels and tracking.
   A per-store parcel ledger (package_tracking) plus one live carrier integration through
   EasyPost, which fronts USPS, UPS, FedEx, DHL and ~100 others with one API: rate a
   parcel, buy the chosen rate's label, and receive signed tracker webhooks. Credentials
   live sealed on the platform's shipping_providers row (configured by a platform admin);
   with no active provider, quote/label still say so (501) rather than inventing data. */
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

  /* the live carrier: inactive until a platform admin saves an API key */
  run(`INSERT OR IGNORE INTO shipping_providers(provider_id, name, carrier_type, status, config, enabled_countries, services) VALUES('easypost','EasyPost (USPS · UPS · FedEx · DHL)','aggregator','inactive','{}','["*"]','["rates","labels","tracking"]')`);

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
  run(`ALTER TABLE shipping_quotes ADD COLUMN tenant_id INTEGER`);
  run(`ALTER TABLE shipping_quotes ADD COLUMN shipment_ref TEXT`);
  run(`ALTER TABLE shipping_quotes ADD COLUMN rate_ref TEXT`);
  run(`ALTER TABLE shipping_quotes ADD COLUMN carrier TEXT`);
  run(`ALTER TABLE package_tracking ADD COLUMN label_url TEXT`);
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
   active already (it did, so no provider could ever be configured). Secret values are
   sealed at rest; a masked or empty value on save keeps the stored one. */
const SECRET_KEYS = ['apiKey', 'webhookSecret', 'token', 'key', 'secret'];
const sec = () => require('./security.js');
function updateProviderConfig(providerId, config) {
  const provider = db().get('SELECT * FROM shipping_providers WHERE provider_id=?', String(providerId || ''));
  if (!provider) return { error: 'Provider not found', code: 404 };
  if (!config || typeof config !== 'object' || Array.isArray(config)) return { error: 'config object required', code: 400 };
  const merged = { ...J(provider.config, {}) };
  for (const [k, v] of Object.entries(config)) {
    if (v == null || v === '' || String(v).startsWith('••••')) continue;
    merged[k] = SECRET_KEYS.includes(k) ? sec().encryptSecret(String(v), '0|ship:' + provider.provider_id + '|' + k) : v;
  }
  db().run('UPDATE shipping_providers SET config=?, status=? WHERE provider_id=?',
    JSON.stringify(merged), merged.apiKey ? 'active' : 'inactive', provider.provider_id);
  return publicProvider(db().get('SELECT * FROM shipping_providers WHERE provider_id=?', provider.provider_id));
}
/* the platform console's view: every carrier, active or not, with which credentials are
   on file (never their values) */
function listProviders() {
  return db().all('SELECT * FROM shipping_providers ORDER BY name').map(p => {
    const cfg = J(p.config, {});
    return { ...publicProvider(p), keys: Object.fromEntries(Object.keys(cfg).map(k => [k, !!cfg[k]])) };
  });
}
/* disconnecting forgets the sealed credentials and takes the carrier out of service */
function disconnectProvider(providerId) {
  const provider = db().get('SELECT * FROM shipping_providers WHERE provider_id=?', String(providerId || ''));
  if (!provider) return { error: 'Provider not found', code: 404 };
  db().run("UPDATE shipping_providers SET config='{}', status='inactive' WHERE provider_id=?", provider.provider_id);
  return publicProvider(db().get('SELECT * FROM shipping_providers WHERE provider_id=?', provider.provider_id));
}
function providerSecrets(providerId) {
  const p = getProvider(providerId); if (!p) return null;
  const cfg = J(p.config, {}), out = {};
  for (const [k, v] of Object.entries(cfg)) out[k] = SECRET_KEYS.includes(k) ? (sec().safeDecrypt(String(v), '0|ship:' + p.provider_id + '|' + k) || '') : v;
  return out;
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

/* ═══════════════ 4 · RATE QUOTES + LABELS (EasyPost) ═══════════════ */
const NOT_INTEGRATED = { error: 'No live carrier is configured — a platform admin adds an EasyPost API key under Shipping providers', code: 501 };
const EP = 'https://api.easypost.com/v2';
const connect = () => require('./connect.js');
async function easypost(method, path, body) {
  const cfg = providerSecrets('easypost');
  if (!cfg || !cfg.apiKey) return { error: NOT_INTEGRATED.error, code: 501 };
  if (connect().offline()) return { error: 'Outbound calls are offline', code: 503 };
  const r = await connect().request(EP + path, { method, headers: { 'content-type': 'application/json', Authorization: 'Basic ' + Buffer.from(cfg.apiKey + ':').toString('base64') }, body: body ? JSON.stringify(body) : undefined });
  if (!r.ok) return { error: 'Carrier: ' + ((r.json && r.json.error && (r.json.error.message || r.json.error.code)) || ('HTTP ' + r.status)), code: 502 };
  return { json: r.json || {} };
}
const ADDR_KEYS = ['name', 'company', 'street1', 'street2', 'city', 'state', 'zip', 'country', 'phone', 'email'];
function address(a) {
  const o = {}; for (const k of ADDR_KEYS) if (a && a[k] != null && String(a[k]).trim()) o[k] = String(a[k]).trim().slice(0, 120);
  return o.street1 && o.city && o.zip && o.country ? o : null;
}
function parcel(p) {
  const w = Number(p && p.weight_oz);
  if (!(w > 0 && w <= 2400)) return null;
  const o = { weight: +w.toFixed(1) };
  for (const k of ['length', 'width', 'height']) { const v = Number(p[k]); if (v > 0 && v <= 200) o[k] = +v.toFixed(1); }
  return o;
}
/* rate a parcel from the store's origin to the order's (or a given) destination */
async function getQuote(tenantId, input) {
  const t = input || {};
  if (!getProvider('easypost')) return NOT_INTEGRATED;
  const from = address(t.from), to = address(t.to), pc = parcel(t.parcel);
  if (!from) return { error: "Set the store's ship-from address (street1, city, zip, country)", code: 400 };
  if (!to) return { error: 'Destination address needs street1, city, zip and country', code: 400 };
  if (!pc) return { error: 'parcel.weight_oz is required (0–2400 oz)', code: 400 };
  if (t.order_id != null && !db().get('SELECT id FROM orders WHERE id=? AND tenant_id=?', Number(t.order_id), tenantId)) return { error: 'Unknown order', code: 404 };
  const r = await easypost('POST', '/shipments', { shipment: { from_address: from, to_address: to, parcel: pc } });
  if (r.error) return r;
  const sh = r.json;
  const rates = (sh.rates || []).map(x => ({ id: x.id, carrier: x.carrier, service: x.service, price: Number(x.rate), currency: x.currency, days: x.delivery_days == null ? null : Number(x.delivery_days) }))
    .filter(x => x.id && x.price >= 0).sort((a, b) => a.price - b.price);
  for (const x of rates) db().run('INSERT INTO shipping_quotes(tenant_id, order_id, provider_id, service_type, price, currency, transit_days, status, shipment_ref, rate_ref, carrier) VALUES(?,?,?,?,?,?,?,?,?,?,?)',
    tenantId, t.order_id == null ? null : Number(t.order_id), 'easypost', x.service, x.price, x.currency || require("./defaults.js").currency(tenantId), x.days, 'quoted', String(sh.id), x.id, x.carrier);
  return { shipment_id: sh.id, rates, messages: (sh.messages || []).map(m => m.message).filter(Boolean).slice(0, 5) };
}
/* buy the label for a rate THIS store was quoted; registers the parcel for tracking */
async function saveLabel(tenantId, input) {
  const t = input || {};
  const q = db().get("SELECT * FROM shipping_quotes WHERE tenant_id=? AND shipment_ref=? AND rate_ref=? AND provider_id='easypost'", tenantId, String(t.shipment_id || ''), String(t.rate_id || ''));
  if (!q) return { error: 'Unknown quote — rate the parcel first and buy one of the returned rates', code: 404 };
  if (q.status === 'purchased') return { error: 'This shipment already has a label', code: 409 };
  const claim = db().run("UPDATE shipping_quotes SET status='purchasing' WHERE id=? AND status='quoted'", q.id);
  if (!claim.changes) return { error: 'This shipment already has a label', code: 409 };
  const r = await easypost('POST', '/shipments/' + encodeURIComponent(q.shipment_ref) + '/buy', { rate: { id: q.rate_ref } });
  if (r.error) { db().run("UPDATE shipping_quotes SET status='quoted' WHERE id=?", q.id); return r; }
  const sh = r.json;
  const tracking = String(sh.tracking_code || '');
  const label = sh.postage_label && sh.postage_label.label_url || null;
  if (!tracking || !label) { db().run("UPDATE shipping_quotes SET status='quoted' WHERE id=?", q.id); return { error: 'Carrier returned no label', code: 502 }; }
  db().run("UPDATE shipping_quotes SET status='purchased' WHERE shipment_ref=? AND tenant_id=?", q.shipment_ref, tenantId);
  const order = q.order_id ? db().get('SELECT id, num FROM orders WHERE id=? AND tenant_id=?', q.order_id, tenantId) : null;
  if (!db().get('SELECT id FROM package_tracking WHERE tracking_number=?', tracking))
    db().run("INSERT INTO package_tracking(tenant_id, order_id, order_num, tracking_number, provider_id, carrier_type, status, service_type, label_url) VALUES(?,?,?,?,?,?,?,?,?)",
      tenantId, order ? order.id : null, order ? order.num : null, tracking, 'easypost', q.carrier || 'api', 'pre_transit', q.service_type, label);
  return { ok: true, tracking_number: tracking, label_url: label, carrier: q.carrier, service: q.service_type, price: q.price, currency: q.currency, order_id: order ? order.id : null, order_num: order ? order.num : null };
}

/* ═══════════════ 5 · WEBHOOKS ═══════════════ */
/* EasyPost signs each webhook: X-Hmac-Signature = "hmac-sha256-hex=" + HMAC-SHA256(secret,
   raw body). Without a configured secret, or with a bad signature, nothing changes. */
function verifyWebhook(providerId, rawBody, headers) {
  const cfg = providerSecrets(String(providerId || ''));
  if (!cfg || !cfg.webhookSecret) return false;
  const got = String((headers || {})['x-hmac-signature'] || '');
  const want = 'hmac-sha256-hex=' + require('crypto').createHmac('sha256', cfg.webhookSecret.normalize('NFKD')).update(rawBody).digest('hex');
  return got.length === want.length && require('crypto').timingSafeEqual(Buffer.from(got), Buffer.from(want));
}
/* an EasyPost tracker event, or the generic {tracking_number, status} shape */
function normalizeEvent(payload) {
  const p = payload || {};
  if (p.object === 'Event' && p.result) {
    const t = p.result, last = (t.tracking_details || []).slice(-1)[0] || {};
    return { tracking_number: t.tracking_code, status: t.status, location: last.tracking_location || {}, description: last.message || p.description || '', timestamp: last.datetime || p.created_at };
  }
  return p;
}
function handleWebhook(providerId, payload) {
  const p = normalizeEvent(payload);
  const trackingNumber = p.tracking_number || p.trackingNumber;
  const status = String(p.status || p.currentStatus || '').toLowerCase();
  if (!trackingNumber || !status) return { error: 'tracking_number and status required', code: 400 };
  const tracking = db().get('SELECT * FROM package_tracking WHERE tracking_number=? AND provider_id=?', String(trackingNumber), String(providerId || ''));
  if (!tracking) return { error: 'Tracking not found', code: 404 };
  const events = J(tracking.events, []);
  events.push({ status, location: p.location || {}, description: String(p.description || '').slice(0, 300), timestamp: p.timestamp || nowIso() });
  db().run('UPDATE package_tracking SET status=?, events=?, current_location=?, updated_at=? WHERE id=?', status, JSON.stringify(events.slice(-100)), JSON.stringify(p.location || {}), nowIso(), tracking.id);
  return { ok: true, tracking_id: tracking.id, tenant_id: tracking.tenant_id, order_id: tracking.order_id, status };
}

module.exports = {
  seed,
  /* providers */ getProviders, getProvider, updateProviderConfig, listProviders, disconnectProvider,
  /* tracking */ createTracking, track, updateTracking, listTracking,
  /* quotes */ getQuote, saveLabel,
  /* webhooks */ handleWebhook, verifyWebhook
};
