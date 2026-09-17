/* LUXORA Platform - multi-tenant SQLite layer (node:sqlite, zero deps) */
"use strict";

const { DatabaseSync } = require("node:sqlite");
const sec = require("./security.js");
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const { PRODUCTS, DEPARTMENTS, DEPT_ICONS, BANNERS, HOME_CARDS } = require("../public/js/data.js");

const DATA_DIR = path.join(__dirname, "..", "data");
if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
const DB_PATH = process.env.LX_DB || path.join(DATA_DIR, "luxora.db");

/* Driver selection at boot: `sqlite` (default) or `postgres` via the synchronous bridge
   (worker + SharedArrayBuffer + Atomics.wait — see lib/pgbridge.js). Choosing postgres means
   the schema+data were already migrated (Platform → Database → apply); SQLite-only DDL/triggers
   are skipped and every run/get/all/exec below speaks Postgres, unchanged for callers. */
const USE_PG = process.env.LX_DB_DRIVER === "postgres" && !!process.env.LX_PG_URL;

let db, exec, run, all, get;
if (USE_PG) {
  db = require("./pgbridge.js").open(process.env.LX_PG_URL, { timeoutMs: Number(process.env.LX_PG_TIMEOUT || 30000) });
  exec = sql => db.exec(sql);
  run = (sql, ...args) => db.run(sql, ...args);
  all = (sql, ...args) => db.all(sql, ...args);
  get = (sql, ...args) => db.get(sql, ...args);
} else {
  db = new DatabaseSync(DB_PATH);
  db.exec("PRAGMA busy_timeout = 3000;");
  exec = sql => db.exec(sql);
  run = (sql, ...args) => db.prepare(sql).run(...args);
  all = (sql, ...args) => db.prepare(sql).all(...args);
  get = (sql, ...args) => db.prepare(sql).get(...args);
}

/* ---------------- schema (SQLite source of truth; PG is created by the migration) ---------------- */
if (!USE_PG) exec(`
PRAGMA journal_mode = WAL;
CREATE TABLE IF NOT EXISTS tenants (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  slug TEXT NOT NULL UNIQUE, name TEXT NOT NULL, domain TEXT DEFAULT '',
  status TEXT NOT NULL DEFAULT 'active', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS plans (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL, price_month REAL NOT NULL DEFAULT 0, currency TEXT DEFAULT 'USD',
  max_products INTEGER NOT NULL DEFAULT 100, max_orders_month INTEGER NOT NULL DEFAULT 100,
  features TEXT DEFAULT '{}', position INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS subscriptions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL REFERENCES tenants(id), plan_id INTEGER NOT NULL REFERENCES plans(id),
  status TEXT NOT NULL DEFAULT 'active', started_at TEXT NOT NULL DEFAULT (datetime('now')),
  renews_at TEXT NOT NULL DEFAULT (datetime('now','+1 month'))
);
CREATE TABLE IF NOT EXISTS invoices (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL REFERENCES tenants(id), number TEXT NOT NULL UNIQUE,
  period_start TEXT, period_end TEXT, amount REAL NOT NULL, currency TEXT DEFAULT 'USD',
  status TEXT NOT NULL DEFAULT 'draft', issued_at TEXT NOT NULL DEFAULT (datetime('now')),
  paid_at TEXT, note TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER, actor_type TEXT NOT NULL DEFAULT 'system',
  actor_id INTEGER, actor_name TEXT, action TEXT NOT NULL,
  entity TEXT, entity_id TEXT, meta TEXT DEFAULT '', ip TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS platform_admins (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, salt TEXT NOT NULL, hash TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS platform_sessions (
  ptid TEXT PRIMARY KEY, admin_id INTEGER REFERENCES platform_admins(id),
  created_at TEXT NOT NULL DEFAULT (datetime('now')), expires_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS tokens (
  token TEXT PRIMARY KEY, tenant_id INTEGER NOT NULL, user_id INTEGER NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')), expires_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL DEFAULT 1,
  name TEXT NOT NULL, email TEXT NOT NULL, salt TEXT NOT NULL, hash TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'customer',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE(tenant_id, email)
);
CREATE TABLE IF NOT EXISTS sessions (
  sid TEXT PRIMARY KEY, user_id INTEGER REFERENCES users(id),
  created_at TEXT NOT NULL DEFAULT (datetime('now')), expires_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS tenant_state (
  sid TEXT NOT NULL, tenant_id INTEGER NOT NULL, zip TEXT NOT NULL DEFAULT '98109',
  gift_balance REAL NOT NULL DEFAULT 0, coupon TEXT DEFAULT '',
  PRIMARY KEY (sid, tenant_id)
);
CREATE TABLE IF NOT EXISTS products (
  tenant_id INTEGER NOT NULL DEFAULT 1, id TEXT NOT NULL,
  title TEXT NOT NULL, brand TEXT NOT NULL, dept TEXT NOT NULL,
  price REAL NOT NULL, list_price REAL, rating REAL, ratings_count INTEGER,
  emoji TEXT, hue INTEGER, priority INTEGER DEFAULT 0, stock INTEGER DEFAULT 0,
  flags TEXT, keywords TEXT, deal_pct INTEGER DEFAULT 0, position INTEGER DEFAULT 0,
  PRIMARY KEY (tenant_id, id)
);
CREATE TABLE IF NOT EXISTS product_bullets (
  tenant_id INTEGER NOT NULL DEFAULT 1, product_id TEXT NOT NULL, pos INTEGER NOT NULL, text TEXT NOT NULL,
  PRIMARY KEY (tenant_id, product_id, pos)
);
CREATE TABLE IF NOT EXISTS cart_items (
  owner TEXT NOT NULL, product_id TEXT NOT NULL, qty INTEGER NOT NULL DEFAULT 1, sku_id INTEGER,
  added_at TEXT NOT NULL DEFAULT (datetime('now')), PRIMARY KEY (owner, product_id)
);
CREATE TABLE IF NOT EXISTS saved_items (
  owner TEXT NOT NULL, product_id TEXT NOT NULL, added_at TEXT NOT NULL DEFAULT (datetime('now')),
  PRIMARY KEY (owner, product_id)
);
CREATE TABLE IF NOT EXISTS orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL DEFAULT 1,
  owner TEXT NOT NULL, num TEXT NOT NULL UNIQUE,
  name TEXT, address TEXT, city TEXT, state TEXT, zip TEXT,
  ship_option TEXT, pay_method TEXT,
  sub REAL, ship_fee REAL, gift_used REAL, tax REAL, total REAL,
  eta_days INTEGER DEFAULT 5, status TEXT DEFAULT 'processing',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS order_items (
  order_id INTEGER NOT NULL, product_id TEXT NOT NULL, qty INTEGER NOT NULL, price REAL NOT NULL, sku_id INTEGER
);
CREATE TABLE IF NOT EXISTS reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL DEFAULT 1,
  product_id TEXT NOT NULL, user_id INTEGER, name TEXT NOT NULL,
  rating INTEGER NOT NULL, title TEXT NOT NULL, body TEXT NOT NULL,
  verified INTEGER DEFAULT 0, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS view_history (
  owner TEXT NOT NULL, product_id TEXT NOT NULL, seen_at TEXT NOT NULL DEFAULT (datetime('now')),
  PRIMARY KEY (owner, product_id)
);
CREATE TABLE IF NOT EXISTS settings (
  tenant_id INTEGER NOT NULL DEFAULT 1, key TEXT NOT NULL, value TEXT NOT NULL,
  PRIMARY KEY (tenant_id, key)
);
CREATE TABLE IF NOT EXISTS departments (
  tenant_id INTEGER NOT NULL DEFAULT 1, key TEXT NOT NULL, label TEXT NOT NULL,
  icon TEXT DEFAULT '🏷️', active INTEGER NOT NULL DEFAULT 1, position INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (tenant_id, key)
);
CREATE TABLE IF NOT EXISTS home_banners (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL DEFAULT 1,
  title TEXT NOT NULL, subtitle TEXT, cta TEXT, hue INTEGER DEFAULT 210, dept TEXT DEFAULT '',
  active INTEGER NOT NULL DEFAULT 1, position INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS home_cards (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL DEFAULT 1,
  title TEXT NOT NULL, dept TEXT NOT NULL, tiles TEXT DEFAULT '[]',
  active INTEGER NOT NULL DEFAULT 1, position INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS tenant_gateways (
  tenant_id INTEGER NOT NULL, provider_id TEXT NOT NULL,
  enabled INTEGER NOT NULL DEFAULT 1, is_primary INTEGER NOT NULL DEFAULT 0,
  mode TEXT NOT NULL DEFAULT 'sandbox', config TEXT DEFAULT '{}', position INTEGER DEFAULT 0,
  PRIMARY KEY (tenant_id, provider_id)
);
CREATE TABLE IF NOT EXISTS payments (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  kind TEXT NOT NULL DEFAULT 'order', order_id INTEGER, invoice_id INTEGER,
  gateway TEXT NOT NULL, method TEXT, amount REAL NOT NULL, currency TEXT,
  fee REAL DEFAULT 0, status TEXT NOT NULL DEFAULT 'initiated',
  txn_ref TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS custom_providers (
  id INTEGER PRIMARY KEY AUTOINCREMENT, scope TEXT NOT NULL DEFAULT 'platform',
  tenant_id INTEGER, kind TEXT NOT NULL, manifest TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS taxonomy (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  parent_id INTEGER, level TEXT NOT NULL, key TEXT NOT NULL, name TEXT NOT NULL,
  icon TEXT DEFAULT '', attrs TEXT DEFAULT '{}', active INTEGER DEFAULT 1, position INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS attribute_defs (
  tenant_id INTEGER NOT NULL, key TEXT NOT NULL, label TEXT NOT NULL, grp TEXT DEFAULT 'General',
  type TEXT DEFAULT 'text', unit TEXT DEFAULT '', options TEXT DEFAULT '[]', validation TEXT DEFAULT '{}',
  industry TEXT DEFAULT '', position INTEGER DEFAULT 0, PRIMARY KEY (tenant_id, key)
);
CREATE TABLE IF NOT EXISTS skus (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, product_id TEXT NOT NULL,
  code TEXT NOT NULL, name TEXT DEFAULT '', identity TEXT DEFAULT '{}', variant TEXT DEFAULT '{}',
  price REAL, mrp REAL, stock INTEGER DEFAULT 0, active INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS warehouses (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, name TEXT NOT NULL,
  code TEXT, country TEXT DEFAULT 'US', region TEXT DEFAULT '', active INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS inventory (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, sku_id INTEGER NOT NULL,
  warehouse_id INTEGER, qty INTEGER DEFAULT 0, reserved INTEGER DEFAULT 0,
  lot TEXT DEFAULT '', batch TEXT DEFAULT '', expiry TEXT DEFAULT '', serial TEXT DEFAULT '[]'
);
CREATE TABLE IF NOT EXISTS relationships (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  from_id TEXT NOT NULL, to_id TEXT NOT NULL, type TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS promotions (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, name TEXT NOT NULL,
  type TEXT NOT NULL, value REAL DEFAULT 0, rules TEXT DEFAULT '{}', scope TEXT DEFAULT '{}',
  starts TEXT, ends TEXT, status TEXT DEFAULT 'active', code TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS sellers (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, name TEXT NOT NULL,
  role TEXT DEFAULT 'retailer', email TEXT, status TEXT DEFAULT 'active', commission_pct REAL DEFAULT 5
);
CREATE TABLE IF NOT EXISTS rfqs (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT NOT NULL UNIQUE,
  product_id TEXT, buyer_name TEXT, buyer_email TEXT, qty REAL, target_price REAL, currency TEXT,
  status TEXT DEFAULT 'open', quotes TEXT DEFAULT '[]', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS shipments (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, order_id INTEGER,
  tracking_ref TEXT UNIQUE, carrier TEXT, warehouse_id INTEGER,
  status TEXT NOT NULL DEFAULT 'pending', sla_due TEXT, dispatched_at TEXT, delivered_at TEXT,
  meta TEXT DEFAULT '{}', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS ix_shipments_order ON shipments(order_id);
CREATE INDEX IF NOT EXISTS ix_shipments_status ON shipments(status, tenant_id);
CREATE TABLE IF NOT EXISTS shipment_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT, shipment_id INTEGER NOT NULL, tenant_id INTEGER NOT NULL,
  status TEXT NOT NULL, location TEXT, note TEXT, ref TEXT, actor TEXT,
  at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS ix_ship_events_ship ON shipment_events(shipment_id);
CREATE TABLE IF NOT EXISTS returns (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT NOT NULL UNIQUE,
  order_id INTEGER, product_id TEXT, qty INTEGER DEFAULT 1, reason TEXT, status TEXT DEFAULT 'requested',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS settlements (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT NOT NULL UNIQUE,
  seller_id INTEGER, order_id INTEGER, gross REAL, commission REAL, net REAL,
  status TEXT DEFAULT 'pending', period TEXT
);
CREATE TABLE IF NOT EXISTS meta_lists (
  name TEXT PRIMARY KEY, label TEXT, items TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS countries (
  code TEXT PRIMARY KEY, name TEXT NOT NULL, currency TEXT NOT NULL, symbol TEXT NOT NULL,
  locale TEXT NOT NULL, decimals INTEGER NOT NULL DEFAULT 2, tax_mode TEXT DEFAULT 'manual',
  tax_rate REAL DEFAULT 0, position INTEGER DEFAULT 0, active INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS currencies (
  code TEXT PRIMARY KEY, name TEXT NOT NULL, symbol TEXT NOT NULL, decimals INTEGER NOT NULL DEFAULT 2,
  usd REAL NOT NULL DEFAULT 1, position INTEGER DEFAULT 0, active INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS tax_modes (
  key TEXT PRIMARY KEY, label TEXT NOT NULL, description TEXT, fields TEXT DEFAULT '[]', position INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS provider_defs (
  id TEXT NOT NULL, kind TEXT NOT NULL, name TEXT NOT NULL, emoji TEXT, description TEXT,
  methods TEXT DEFAULT '[]', fee_pct REAL DEFAULT 0, fee_fixed REAL DEFAULT 0, fields TEXT DEFAULT '[]',
  base_fee REAL DEFAULT 0, eta_min INTEGER, eta_max INTEGER, position INTEGER DEFAULT 0,
  enabled INTEGER DEFAULT 1, PRIMARY KEY (id, kind)
);
CREATE TABLE IF NOT EXISTS provider_availability (
  provider_id TEXT NOT NULL, country_code TEXT NOT NULL REFERENCES countries(code),
  PRIMARY KEY (provider_id, country_code)
);
CREATE TABLE IF NOT EXISTS fx_rates (
  id INTEGER PRIMARY KEY AUTOINCREMENT, currency TEXT NOT NULL, usd REAL NOT NULL,
  source TEXT DEFAULT 'manual', note TEXT DEFAULT '', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS platform_settings (
  key TEXT PRIMARY KEY, value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS modules (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, category TEXT, summary TEXT,
  price_type TEXT DEFAULT 'one_time', price REAL DEFAULT 0, currency TEXT DEFAULT 'USD',
  version TEXT DEFAULT '1.0', vendor TEXT DEFAULT 'LUXORA', manifest TEXT DEFAULT '{}',
  status TEXT DEFAULT 'active', position INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS tenant_modules (
  tenant_id INTEGER NOT NULL, module_id TEXT NOT NULL, status TEXT DEFAULT 'installed',
  config TEXT DEFAULT '{}', installed_at TEXT NOT NULL DEFAULT (datetime('now')), installed_by TEXT DEFAULT '',
  PRIMARY KEY (tenant_id, module_id)
);
CREATE TABLE IF NOT EXISTS wallets (
  tenant_id INTEGER NOT NULL, owner TEXT NOT NULL, balance REAL NOT NULL DEFAULT 0,
  updated_at TEXT NOT NULL DEFAULT (datetime('now')), PRIMARY KEY (tenant_id, owner)
);
CREATE TABLE IF NOT EXISTS links (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER,
  type TEXT NOT NULL, from_entity TEXT NOT NULL, from_uid TEXT NOT NULL,
  to_entity TEXT NOT NULL, to_uid TEXT NOT NULL, meta TEXT DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS context_types (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  grp TEXT NOT NULL, key TEXT NOT NULL, label TEXT NOT NULL, type TEXT DEFAULT 'context',
  fields TEXT DEFAULT '[]', position INTEGER DEFAULT 0, UNIQUE(grp, key)
);
CREATE TABLE IF NOT EXISTS entity_defs (
  key TEXT NOT NULL, scope TEXT NOT NULL DEFAULT 'tenant', tenant_id INTEGER NOT NULL DEFAULT 0,
  def TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT (datetime('now')),
  PRIMARY KEY (key, scope, tenant_id)
);
CREATE TABLE IF NOT EXISTS entity_data (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER, entity TEXT NOT NULL,
  data TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
/* ---------- advanced product-model entities (universal commerce blueprint) ---------- */
CREATE TABLE IF NOT EXISTS serialized_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  product_id TEXT NOT NULL, sku_id INTEGER, warehouse_id INTEGER,
  serial TEXT NOT NULL, imei TEXT, rfid TEXT, asset_tag TEXT,
  batch TEXT DEFAULT '', lot TEXT DEFAULT '', expiry TEXT,
  status TEXT NOT NULL DEFAULT 'in_stock', condition TEXT DEFAULT 'new',
  customer_id INTEGER, order_id INTEGER,
  purchase_date TEXT, warranty_end TEXT, meta TEXT DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS variant_groups (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  product_id TEXT NOT NULL, name TEXT NOT NULL, axis TEXT DEFAULT 'General',
  attr_key TEXT DEFAULT '', position INTEGER DEFAULT 0, active INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS compliance_records (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  scope TEXT NOT NULL DEFAULT 'product', ref_id TEXT NOT NULL DEFAULT '',
  kind TEXT NOT NULL DEFAULT 'certificate', code TEXT DEFAULT '', issuer TEXT DEFAULT '',
  jurisdiction TEXT DEFAULT '', status TEXT NOT NULL DEFAULT 'valid',
  valid_from TEXT, valid_to TEXT, doc_media TEXT DEFAULT '', notes TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS suppliers (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  name TEXT NOT NULL, party_role TEXT DEFAULT 'manufacturer', tax_id TEXT DEFAULT '',
  country TEXT DEFAULT 'US', region TEXT DEFAULT '', address TEXT DEFAULT '',
  email TEXT DEFAULT '', phone TEXT DEFAULT '', lead_time_days INTEGER DEFAULT 7,
  moq INTEGER DEFAULT 1, currency TEXT DEFAULT 'USD', payment_terms TEXT DEFAULT 'net30',
  on_time_pct REAL DEFAULT 0, status TEXT DEFAULT 'active',
  certifications TEXT DEFAULT '[]', price_list TEXT DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS localizations (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  entity TEXT NOT NULL DEFAULT 'product', ref_id TEXT NOT NULL, locale TEXT NOT NULL,
  name TEXT DEFAULT '', description TEXT DEFAULT '', bullets TEXT DEFAULT '[]',
  attrs TEXT DEFAULT '{}', active INTEGER DEFAULT 1,
  UNIQUE (tenant_id, entity, ref_id, locale)
);
CREATE TABLE IF NOT EXISTS product_suppliers (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  product_id TEXT NOT NULL, supplier_id INTEGER NOT NULL, supplier_sku TEXT DEFAULT '',
  price REAL, lead_days INTEGER DEFAULT 7, moq INTEGER DEFAULT 1,
  is_primary INTEGER DEFAULT 0, status TEXT DEFAULT 'active',
  UNIQUE (tenant_id, product_id, supplier_id)
);
CREATE TABLE IF NOT EXISTS contracts (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT NOT NULL,
  buyer_name TEXT NOT NULL, buyer_email TEXT NOT NULL, buyer_org TEXT DEFAULT '',
  supplier_id INTEGER, product_ids TEXT DEFAULT '[]', currency TEXT DEFAULT 'USD',
  pricing TEXT DEFAULT '{}', min_qty INTEGER DEFAULT 1, incoterms TEXT DEFAULT 'EXW',
  payment_terms TEXT DEFAULT 'net30', valid_from TEXT, valid_to TEXT,
  status TEXT NOT NULL DEFAULT 'draft', notes TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE (tenant_id, ref)
);
CREATE TABLE IF NOT EXISTS tenders (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT NOT NULL,
  title TEXT NOT NULL, buyer_org TEXT DEFAULT '', buyer_email TEXT DEFAULT '', description TEXT DEFAULT '',
  currency TEXT DEFAULT 'USD', budget REAL DEFAULT 0, open_at TEXT, close_at TEXT,
  status TEXT NOT NULL DEFAULT 'open', awarded_seller_id INTEGER, awarded_contract_id INTEGER,
  items TEXT DEFAULT '[]', bids TEXT DEFAULT '[]',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE (tenant_id, ref)
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_serial_tenant ON serialized_items(tenant_id, serial);
CREATE TABLE IF NOT EXISTS ai_usage (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  capability TEXT NOT NULL, provider TEXT NOT NULL, model TEXT DEFAULT '',
  units INTEGER NOT NULL DEFAULT 1, cost REAL NOT NULL DEFAULT 0, currency TEXT DEFAULT 'USD',
  tier TEXT DEFAULT 'free', status TEXT DEFAULT 'ok', actor TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS ai_tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  capability TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'queued',
  params TEXT DEFAULT '{}', result TEXT, cost REAL DEFAULT 0,
  actor TEXT DEFAULT '', created_at TEXT NOT NULL DEFAULT (datetime('now')), updated_at TEXT
);
/* ---------- subscription / usage billing (line items, metering, credits, dunning) ---------- */
CREATE TABLE IF NOT EXISTS invoice_lines (
  id INTEGER PRIMARY KEY AUTOINCREMENT, invoice_id INTEGER NOT NULL, tenant_id INTEGER NOT NULL,
  kind TEXT NOT NULL DEFAULT 'plan', description TEXT NOT NULL, qty REAL DEFAULT 1,
  unit_amount REAL DEFAULT 0, amount REAL DEFAULT 0, tax REAL DEFAULT 0, tax_class TEXT DEFAULT 'standard',
  ref TEXT DEFAULT '', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS usage_records (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, kind TEXT NOT NULL,
  ref TEXT DEFAULT '', description TEXT NOT NULL DEFAULT '', qty REAL DEFAULT 1, unit_amount REAL DEFAULT 0,
  amount REAL DEFAULT 0, currency TEXT DEFAULT 'USD', period TEXT NOT NULL DEFAULT '', billed INTEGER DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
/* ---------- Payments & Financial services (disputes · multi-gateway retries · payout runs · reconciliation) ---------- */
CREATE TABLE IF NOT EXISTS payment_attempts (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, payment_id INTEGER NOT NULL,
  gateway TEXT, attempt INTEGER DEFAULT 1, status TEXT NOT NULL DEFAULT 'pending',
  txn_ref TEXT, error TEXT, at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS ix_pay_attempts ON payment_attempts(payment_id);
CREATE TABLE IF NOT EXISTS disputes (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, payment_id INTEGER, order_id INTEGER,
  ref TEXT NOT NULL UNIQUE, reason TEXT, amount REAL, currency TEXT,
  state TEXT NOT NULL DEFAULT 'opened', resolution TEXT, closed_at TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS ix_disputes_state ON disputes(state, tenant_id);
CREATE TABLE IF NOT EXISTS payouts (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  seller_id INTEGER, kind TEXT NOT NULL DEFAULT 'seller', ref TEXT, period TEXT,
  gross REAL NOT NULL DEFAULT 0, fee REAL NOT NULL DEFAULT 0, net REAL NOT NULL DEFAULT 0,
  currency TEXT DEFAULT 'USD', status TEXT NOT NULL DEFAULT 'open',
  disbursed_at TEXT, note TEXT DEFAULT '', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS payout_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT, payout_id INTEGER NOT NULL, tenant_id INTEGER NOT NULL,
  ref TEXT NOT NULL, kind TEXT, description TEXT, amount REAL, currency TEXT, settled INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS recon_batches (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, period TEXT, gateway TEXT,
  source TEXT, lines INTEGER DEFAULT 0, matched INTEGER DEFAULT 0, unmatched INTEGER DEFAULT 0,
  total REAL DEFAULT 0, status TEXT NOT NULL DEFAULT 'open', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS recon_lines (
  id INTEGER PRIMARY KEY AUTOINCREMENT, batch_id INTEGER NOT NULL, tenant_id INTEGER NOT NULL,
  ref TEXT, source TEXT, amount REAL, status TEXT NOT NULL DEFAULT 'matched', note TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS credit_notes (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, number TEXT NOT NULL UNIQUE,
  invoice_id INTEGER, amount REAL NOT NULL, currency TEXT DEFAULT 'USD', reason TEXT DEFAULT '',
  status TEXT NOT NULL DEFAULT 'issued', to_wallet INTEGER DEFAULT 0, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS billing_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, invoice_id INTEGER,
  kind TEXT NOT NULL, detail TEXT DEFAULT '{}', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS ix_invoice_lines ON invoice_lines(invoice_id);
CREATE INDEX IF NOT EXISTS ix_usage_open ON usage_records(tenant_id, billed);
/* ---------- platform hardening: webhooks, entity metadata, idempotency ---------- */
CREATE TABLE IF NOT EXISTS webhooks (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, url TEXT NOT NULL,
  secret TEXT DEFAULT '', events TEXT DEFAULT '["*"]', active INTEGER DEFAULT 1,
  description TEXT DEFAULT '', created_at TEXT NOT NULL DEFAULT (datetime('now')), updated_at TEXT
);
CREATE TABLE IF NOT EXISTS webhook_deliveries (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, webhook_id INTEGER,
  event TEXT NOT NULL, subject_uid TEXT, payload TEXT DEFAULT '{}', status TEXT NOT NULL DEFAULT 'queued',
  attempts INTEGER DEFAULT 0, response TEXT DEFAULT '', next_retry_at TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS entity_meta (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  entity TEXT NOT NULL, ref_uid TEXT NOT NULL, tags TEXT DEFAULT '[]', meta TEXT DEFAULT '{}', notes TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now')), updated_at TEXT,
  UNIQUE (tenant_id, entity, ref_uid)
);
CREATE TABLE IF NOT EXISTS idempotency_keys (
  key TEXT PRIMARY KEY, tenant_id INTEGER, method TEXT, path TEXT, request_hash TEXT,
  status INTEGER, response TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')), expires_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_deliveries ON webhook_deliveries(tenant_id, status);
CREATE INDEX IF NOT EXISTS ix_entity_meta ON entity_meta(tenant_id, entity, ref_uid);
/* ---------- enterprise layer: cutover, identity, regions, observability, domain ---------- */
CREATE TABLE IF NOT EXISTS stock_transfers (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  from_warehouse INTEGER, to_warehouse INTEGER, sku_id INTEGER, qty INTEGER NOT NULL DEFAULT 1,
  status TEXT NOT NULL DEFAULT 'draft', reference TEXT DEFAULT '', note TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now')), deleted_at TEXT
);
CREATE TABLE IF NOT EXISTS remittance_records (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  period TEXT NOT NULL, jurisdiction TEXT NOT NULL, tax_type TEXT DEFAULT 'vat',
  taxable REAL DEFAULT 0, tax_collected REAL DEFAULT 0, currency TEXT DEFAULT 'USD',
  status TEXT NOT NULL DEFAULT 'pending', filed_at TEXT, reference TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now')), deleted_at TEXT
);
CREATE TABLE IF NOT EXISTS inbound_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER, provider TEXT, event TEXT,
  payload TEXT DEFAULT '{}', signature_ok INTEGER DEFAULT 0, processed INTEGER DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS sso_connections (
  tenant_id INTEGER PRIMARY KEY, provider TEXT DEFAULT 'okta', entity_id TEXT DEFAULT '',
  sso_url TEXT DEFAULT '', cert TEXT DEFAULT '', enabled INTEGER DEFAULT 0, domains TEXT DEFAULT '[]',
  mode TEXT DEFAULT 'saml', issuer TEXT DEFAULT '', client_id TEXT DEFAULT '', client_secret TEXT DEFAULT '',
  redirect_uri TEXT DEFAULT '', scope TEXT DEFAULT 'openid email profile', auto_provision INTEGER DEFAULT 0,
  default_role TEXT DEFAULT 'manager', updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS sso_states (
  state TEXT PRIMARY KEY, tenant_id INTEGER NOT NULL, nonce TEXT DEFAULT '', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS scim_tokens (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, token_hash TEXT NOT NULL,
  label TEXT DEFAULT '', prefix TEXT DEFAULT '', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
/* ---------- central Offers / Coupons / Wallet engine ---------- */
CREATE TABLE IF NOT EXISTS offers (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL DEFAULT 0,
  scope_level TEXT NOT NULL DEFAULT 'tenant', channel TEXT NOT NULL DEFAULT 'commerce',
  name TEXT NOT NULL, code TEXT DEFAULT '', type TEXT NOT NULL, direction TEXT NOT NULL DEFAULT 'discount',
  value REAL DEFAULT 0, currency TEXT DEFAULT 'USD',
  scope_type TEXT NOT NULL DEFAULT 'store', scope_value TEXT DEFAULT '{}',
  funder TEXT NOT NULL DEFAULT 'self', funder_ref TEXT DEFAULT '', brand_ref TEXT DEFAULT '',
  min_amount REAL DEFAULT 0, min_qty INTEGER DEFAULT 0, max_discount REAL DEFAULT 0,
  usage_limit INTEGER DEFAULT 0, per_owner_limit INTEGER DEFAULT 0, used INTEGER DEFAULT 0,
  stack_group TEXT DEFAULT '', stack_policy TEXT DEFAULT 'stack_with_others', priority INTEGER DEFAULT 0,
  starts TEXT, ends TEXT, status TEXT DEFAULT 'active', rules TEXT DEFAULT '{}', summary TEXT DEFAULT '',
  source TEXT DEFAULT 'offer', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS coupons (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL DEFAULT 0,
  code TEXT NOT NULL, offer_id INTEGER, funder TEXT DEFAULT 'self', funder_ref TEXT DEFAULT '', brand_ref TEXT DEFAULT '',
  kind TEXT NOT NULL DEFAULT 'single_use', value REAL DEFAULT 0, currency TEXT DEFAULT 'USD',
  max_uses INTEGER DEFAULT 1, per_owner_limit INTEGER DEFAULT 1, used INTEGER DEFAULT 0,
  issued_to TEXT DEFAULT '', batch TEXT DEFAULT '', starts TEXT, ends TEXT, status TEXT DEFAULT 'active', note TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now')), UNIQUE (tenant_id, code)
);
CREATE TABLE IF NOT EXISTS coupon_redemptions (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  coupon_id INTEGER, offer_id INTEGER, code TEXT, order_id INTEGER, invoice_id INTEGER,
  owner TEXT, channel TEXT DEFAULT 'commerce', amount REAL DEFAULT 0, qty INTEGER DEFAULT 1,
  funder TEXT DEFAULT 'self', funder_ref TEXT DEFAULT '', brand_ref TEXT DEFAULT '',
  meta TEXT DEFAULT '{}', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS wallet_entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL DEFAULT 0,
  owner TEXT NOT NULL, currency TEXT DEFAULT 'USD', kind TEXT NOT NULL,
  amount REAL NOT NULL, balance_after REAL DEFAULT 0, ref TEXT DEFAULT '', note TEXT DEFAULT '',
  channel TEXT DEFAULT 'commerce', actor TEXT DEFAULT 'system',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
/* ---------- GOIP Ω∞ — the four stores no existing table owns (attribution · funding · settlement ·
   entitlement). Everything else GOIP needs already lives in offers/coupons/coupon_redemptions/
   wallets/wallet_entries/links/usage_records/meta_lists/audit_log — see lib/goip.js. ---------- */
CREATE TABLE IF NOT EXISTS goip_touchpoints (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL DEFAULT 0,
  subject_uid TEXT DEFAULT '', offer_id INTEGER, code TEXT DEFAULT '', kind TEXT NOT NULL DEFAULT 'view',
  party TEXT DEFAULT '', party_type TEXT DEFAULT 'customer', channel TEXT DEFAULT 'commerce', distribution TEXT DEFAULT 'in_app',
  device TEXT DEFAULT '', owner TEXT DEFAULT '', session TEXT DEFAULT '', order_id INTEGER,
  value REAL DEFAULT 0, unit TEXT DEFAULT 'USD', context TEXT DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS goip_budgets (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL DEFAULT 0,
  domain TEXT NOT NULL DEFAULT 'incentive', funder TEXT NOT NULL DEFAULT 'self', funder_ref TEXT DEFAULT '',
  unit TEXT NOT NULL DEFAULT 'USD', allocated REAL DEFAULT 0, reserved REAL DEFAULT 0, consumed REAL DEFAULT 0,
  period TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'open', policy TEXT DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now')), updated_at TEXT
);
CREATE TABLE IF NOT EXISTS goip_settlements (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL DEFAULT 0,
  period TEXT NOT NULL DEFAULT '', party TEXT NOT NULL DEFAULT '', party_type TEXT NOT NULL DEFAULT 'merchant',
  unit TEXT NOT NULL DEFAULT 'USD', gross REAL DEFAULT 0, fees REAL DEFAULT 0, net REAL DEFAULT 0,
  redemptions REAL DEFAULT 0, status TEXT NOT NULL DEFAULT 'accrued', reference TEXT DEFAULT '',
  paid_at TEXT, meta TEXT DEFAULT '{}', created_at TEXT NOT NULL DEFAULT (datetime('now')), updated_at TEXT
);
CREATE TABLE IF NOT EXISTS goip_entitlements (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL DEFAULT 0,
  owner TEXT NOT NULL DEFAULT '', benefit TEXT NOT NULL DEFAULT '', unit TEXT DEFAULT '', qty REAL DEFAULT 0,
  tier TEXT DEFAULT '', scope TEXT DEFAULT '{}', starts TEXT, ends TEXT, status TEXT NOT NULL DEFAULT 'active',
  source_offer INTEGER, source_redemption INTEGER, meta TEXT DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS ix_goip_touch ON goip_touchpoints(tenant_id, owner, created_at);
CREATE INDEX IF NOT EXISTS ix_goip_touch_party ON goip_touchpoints(tenant_id, party_type, party);
CREATE INDEX IF NOT EXISTS ix_goip_budget ON goip_budgets(tenant_id, funder, unit, period, status);
CREATE INDEX IF NOT EXISTS ix_goip_settle ON goip_settlements(tenant_id, period, status);
CREATE INDEX IF NOT EXISTS ix_goip_ent ON goip_entitlements(tenant_id, owner, status);
CREATE UNIQUE INDEX IF NOT EXISTS ux_offers_code ON offers(tenant_id, code) WHERE code<>'';
CREATE INDEX IF NOT EXISTS ix_offers_chan ON offers(channel, status, tenant_id);
CREATE INDEX IF NOT EXISTS ix_wallet_tx ON wallet_entries(tenant_id, owner);
CREATE INDEX IF NOT EXISTS ix_products_tenant ON products(tenant_id, dept);
CREATE INDEX IF NOT EXISTS ix_reviews_pid ON reviews(tenant_id, product_id);
CREATE INDEX IF NOT EXISTS ix_orders_tenant ON orders(tenant_id, created_at);
 CREATE INDEX IF NOT EXISTS ix_audit_tenant ON audit_log(tenant_id, created_at);
`);

/* column migrations for existing DBs (SQLite source only; the PG schema is migrated) */
if (!USE_PG) {
try { db.exec("ALTER TABLE tenants ADD COLUMN mode TEXT NOT NULL DEFAULT 'marketplace'"); } catch (e) { }
try { db.exec("ALTER TABLE orders ADD COLUMN contexts TEXT DEFAULT '{}'"); } catch (e) { }
try { db.exec("ALTER TABLE tenant_state ADD COLUMN coupon TEXT DEFAULT ''"); } catch (e) { }
try { db.exec("ALTER TABLE tenants ADD COLUMN industries TEXT DEFAULT '[]'"); } catch (e) { }
try { db.exec("ALTER TABLE tenants ADD COLUMN profile TEXT DEFAULT '{}'"); } catch (e) { }
try { db.exec("ALTER TABLE tenants ADD COLUMN country TEXT DEFAULT 'US'"); } catch (e) { }
for (const c of ["users.kdf_version TEXT DEFAULT 'v1'", "users.pwd_history TEXT DEFAULT '[]'", "platform_admins.kdf_version TEXT DEFAULT 'v1'", "sessions.csrf TEXT", "audit_log.prev_hash TEXT", "audit_log.hash TEXT"]) {
  const [tb, col] = c.split("."); try { db.exec("ALTER TABLE " + tb + " ADD COLUMN " + col); } catch (e) { }
}
try { db.exec("ALTER TABLE orders ADD COLUMN currency TEXT DEFAULT ''"); } catch (e) { }
try { db.exec("ALTER TABLE orders ADD COLUMN fx REAL DEFAULT 1"); } catch (e) { }
for (const col of ["type TEXT DEFAULT 'physical'", "node_id INTEGER", "lifecycle TEXT DEFAULT 'published'", "identity TEXT DEFAULT '{}'", "attrs TEXT DEFAULT '{}'", "vertical TEXT DEFAULT '{}'", "media TEXT DEFAULT '[]'", "seo TEXT DEFAULT '{}'", "tax_rule TEXT DEFAULT '{}'", "geo_rules TEXT DEFAULT '[]'", "pricing_rules TEXT DEFAULT '[]'", "logistics TEXT DEFAULT '{}'", "packaging TEXT DEFAULT '[]'", "docs TEXT DEFAULT '[]'", "supplier_id INTEGER", "uom TEXT DEFAULT '{\"unit\":\"ea\"}'", "tax_profile TEXT DEFAULT ''", "invoice_profile TEXT DEFAULT ''", "payment_profiles TEXT DEFAULT '[]'"]) {
  try { db.exec("ALTER TABLE products ADD COLUMN " + col); } catch (e) { }
}
try { db.exec("ALTER TABLE skus ADD COLUMN group_id INTEGER"); } catch (e) { }
try { db.exec("ALTER TABLE cart_items ADD COLUMN sku_id INTEGER"); } catch (e) { }
try { db.exec("ALTER TABLE provider_defs ADD COLUMN spec TEXT DEFAULT '{}'"); } catch (e) { }
try { db.exec("ALTER TABLE audit_log ADD COLUMN trace_id TEXT"); } catch (e) { }
try { db.exec("ALTER TABLE orders ADD COLUMN trace_id TEXT"); } catch (e) { }
try { db.exec("ALTER TABLE invoices ADD COLUMN trace_id TEXT"); } catch (e) { }
try { db.exec("ALTER TABLE entity_meta ADD COLUMN ref_uid TEXT"); } catch (e) { }
try { db.exec("ALTER TABLE users ADD COLUMN staff_role TEXT DEFAULT 'owner'"); } catch (e) { }
try { db.exec("ALTER TABLE users ADD COLUMN perms TEXT DEFAULT '{}'"); } catch (e) { }
try { db.exec("ALTER TABLE users ADD COLUMN last_login TEXT"); } catch (e) { }
try { db.exec("ALTER TABLE users ADD COLUMN disabled INTEGER DEFAULT 0"); } catch (e) { }
try { db.exec("ALTER TABLE tenants ADD COLUMN region TEXT DEFAULT 'global'"); } catch (e) { }
try { db.exec("ALTER TABLE tenants ADD COLUMN sso_provider TEXT DEFAULT ''"); } catch (e) { }
try { db.exec("ALTER TABLE tenants ADD COLUMN cdn TEXT DEFAULT ''"); } catch (e) { }
for (const c of ["mode TEXT DEFAULT 'saml'", "issuer TEXT DEFAULT ''", "client_id TEXT DEFAULT ''", "client_secret TEXT DEFAULT ''", "redirect_uri TEXT DEFAULT ''", "scope TEXT DEFAULT 'openid email profile'", "auto_provision INTEGER DEFAULT 0", "default_role TEXT DEFAULT 'manager'"]) {
  try { db.exec("ALTER TABLE sso_connections ADD COLUMN " + c); } catch (e) { }
}
try { db.exec("ALTER TABLE webhook_deliveries ADD COLUMN subject_uid TEXT"); } catch (e) { }
/* governance: soft-delete column on content tables (idempotent; drives Trash + retention) */
for (const t of ["products", "offers", "coupons", "suppliers", "product_suppliers", "contracts", "tenders", "compliance_records", "serialized_items", "variant_groups", "localizations", "reviews", "orders", "warehouses", "departments", "attribute_defs", "taxonomy", "sellers", "home_banners", "home_cards", "promotions", "returns"]) {
  try { db.exec(`ALTER TABLE ${t} ADD COLUMN deleted_at TEXT`); } catch (e) { }
}
try { db.exec("ALTER TABLE order_items ADD COLUMN sku_id INTEGER"); } catch (e) { }
for (const col of ["credits REAL DEFAULT 0", "offer_type TEXT DEFAULT ''", "status TEXT DEFAULT 'redeemed'", "meta TEXT DEFAULT '{}'"]) { try { db.exec("ALTER TABLE coupon_redemptions ADD COLUMN " + col); } catch (e) { } }
/* GOIP Ω∞ constitutional columns on the value-exchange record (idempotent; self-heals on upgrade) */
for (const col of ["domain TEXT DEFAULT 'incentive'", "benefit TEXT DEFAULT ''", "reality TEXT DEFAULT 'any'", "economic_unit TEXT DEFAULT ''",
  "temporal_spec TEXT DEFAULT '{}'", "spatial_spec TEXT DEFAULT '{}'", "conditions TEXT DEFAULT '{}'", "distribution TEXT DEFAULT '[]'",
  "attribution_model TEXT DEFAULT 'last_touch'", "funding TEXT DEFAULT '{}'", "governance TEXT DEFAULT '{}'", "campaign TEXT DEFAULT ''",
  "version INTEGER DEFAULT 1", "parent_id INTEGER"]) { try { db.exec("ALTER TABLE offers ADD COLUMN " + col); } catch (e) { } }
try { db.exec("ALTER TABLE coupon_redemptions ADD COLUMN settlement_id INTEGER"); } catch (e) { }
try { db.exec("ALTER TABLE coupon_redemptions ADD COLUMN unit TEXT DEFAULT ''"); } catch (e) { }
}

/* ---------------- universal unique ids (SQLite triggers; PG uses gen_random_uuid defaults) ---------------- */
if (!USE_PG) require("./uid.js").ensureUids(db);

/* ---------------- relationships ---------------- */
function addLink(tenantId, type, fromEntity, fromUid, toEntity, toUid, meta) {
  if (!fromUid || !toUid) return null;
  const r = run("INSERT INTO links(tenant_id,type,from_entity,from_uid,to_entity,to_uid,meta) VALUES(?,?,?,?,?,?,?)",
    tenantId, type, fromEntity, fromUid, toEntity, toUid, JSON.stringify(meta || {}));
  return Number(r.lastInsertRowid);
}

/* ---------------- crypto (delegated to security L3 KDF) ---------------- */
sec.initDb({ get: (s, ...a) => get(s, ...a), run: (s, ...a) => run(s, ...a), all: (s, ...a) => all(s, ...a) });
sec.onRewrap(() => sec.rewrapSecrets(sec.encryptSecret, sec.decryptSecret));
/* L7: backfill the hash chain over pre-existing audit rows */
function seedAuditChain() {
  try { if (get("SELECT COUNT(*) c FROM audit_log WHERE hash IS NOT NULL").c > 0) return; } catch (e) { return; }
  const prev = {};
  for (const row of all("SELECT * FROM audit_log ORDER BY id")) {
    const scope = row.tenant_id == null ? "p" : String(row.tenant_id);
    const payload = { tenant: row.tenant_id, actor: row.actor_name || null, action: row.action, entity: row.entity || null, ref: row.entity_id || null, meta: row.meta, ip: row.ip || "" };
    const prevHash = prev[scope] || "GENESIS";
    const h = sec.chainRow(prevHash, payload);
    run("UPDATE audit_log SET prev_hash=?, hash=? WHERE id=?", prevHash, h, row.id);
    prev[scope] = h;
  }
}
function hashPasswordFor(pw, salt, ver, context) { return sec.kdfHash(pw, salt, ver, context); }
function passwordHistory(pw, saltOld, hashOld, ver, context) { return JSON.stringify([{ salt: saltOld, hash: hashOld, kdf: ver || "v1" }].slice(0, 5)); }
function passwordReused(tenantId, email, pw) {
  const u = get("SELECT salt, hash, kdf_version, pwd_history FROM users WHERE tenant_id=? AND email=?", tenantId, String(email).toLowerCase());
  if (!u) return false;
  const list = (() => { try { return JSON.parse(u.pwd_history || "[]"); } catch (e) { return []; } })();
  for (const h of list) if (sec.kdfVerify(pw, h.salt, h.hash, h.kdf, h.kdf === "v1" ? "" : email)) return true;
  return false;
}
function newUser(tenantId, name, email, pw, role) {
  const salt = sec.newSalt();
  const ver = sec.currentKdf();
  const r = run("INSERT INTO users(tenant_id,name,email,salt,hash,role,kdf_version,pwd_history) VALUES(?,?,?,?,?,?,?,?)",
    tenantId, name, email.toLowerCase(), salt, hashPasswordFor(pw, salt, ver, email), role || "customer", ver, JSON.stringify([]));
  return Number(r.lastInsertRowid);
}
function setKdfVersion(id, ver) { run("UPDATE users SET kdf_version=? WHERE id=?", ver, id); }
function setUserPassword(id, pw, context, oldSalt, oldHash, oldVer) {
  const salt = sec.newSalt(); const ver = sec.currentKdf();
  let hist = []; try { hist = JSON.parse((get("SELECT pwd_history h FROM users WHERE id=?", id).h) || "[]"); } catch (e) { }
  if (oldSalt && oldHash) hist.unshift({ salt: oldSalt, hash: oldHash, kdf: oldVer || ver });
  run("UPDATE users SET salt=?, hash=?, kdf_version=?, pwd_history=? WHERE id=?", salt, hashPasswordFor(pw, salt, ver, context), ver, JSON.stringify(hist.slice(0, 5)), id);
}
function verifyUser(tenantId, email, pw) {
  const u = get("SELECT * FROM users WHERE tenant_id=? AND email=?", tenantId, String(email).toLowerCase());
  if (!u) return null;
  const ver = u.kdf_version || "v1";
  if (!sec.kdfVerify(pw, u.salt, u.hash, ver, ver === "v1" ? "" : email)) return null;
  if (ver !== sec.currentKdf()) { /* L3: transparent upgrade on successful login */
    const salt = sec.newSalt();
    run("UPDATE users SET salt=?, hash=?, kdf_version=?, pwd_history=? WHERE id=?", salt, hashPasswordFor(pw, salt, sec.currentKdf(), email), sec.currentKdf(),
      JSON.stringify([{ salt: u.salt, hash: u.hash, kdf: ver }].concat(JSON.parse(u.pwd_history || "[]")).slice(0, 5)), u.id);
    u.upgraded = true;
  }
  return u;
}
function newPlatformAdmin(name, email, pw) {
  const salt = sec.newSalt(); const ver = sec.currentKdf();
  const r = run("INSERT INTO platform_admins(name,email,salt,hash,kdf_version) VALUES(?,?,?,?,?)", name, email.toLowerCase(), salt, hashPasswordFor(pw, salt, ver, "pa:" + email.toLowerCase()), ver);
  return Number(r.lastInsertRowid);
}
function verifyPlatformAdmin(email, pw) {
  const u = get("SELECT * FROM platform_admins WHERE email=?", String(email).toLowerCase());
  if (!u) return null;
  const ver = u.kdf_version || "v1";
  if (!sec.kdfVerify(pw, u.salt, u.hash, ver, ver === "v1" ? "" : "pa:" + u.email)) return null;
  if (ver !== sec.currentKdf()) { const salt = sec.newSalt(); run("UPDATE platform_admins SET salt=?, hash=?, kdf_version=? WHERE id=?", salt, hashPasswordFor(pw, salt, sec.currentKdf(), "pa:" + u.email), sec.currentKdf(), u.id); }
  return u;
}

/* ---------------- review generation (seed) ---------------- */
function hashStr(str) { let h = 2166136261; for (let i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }
function mulberry32(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const RV_AUTHORS = ["Jennifer M.", "David R.", "Priya S.", "Marcus T.", "Emily Chen", "Carlos D.", "Sarah W.", "Ahmed K.", "Linda O.", "Kevin B.", "Ana G.", "Robert P.", "Mei L.", "Jordan F.", "Rachel N."];
const RV_TITLES = { hi: ["Exactly what I wanted", "Great value for the price", "Buy it, you won't regret it", "Impressive quality", "My favorite purchase this year"], mid: ["Good but not perfect", "Decent for the money", "Nearly five stars", "Solid, with small caveats"], lo: ["Disappointed", "Not as described", "Needs improvement", "Returned it"] };
const RV_BODIES = {
  hi: ["absolutely nailed this one. Setup took under two minutes and it has worked flawlessly since. The build quality feels premium — highly recommend.", "I compared this against three competitors and this was the best by far. Shipping was fast, packaging excellent.", "Been using it daily for three months now. Quality, comfort and finish are all fantastic.", "Bought this as a gift and ended up ordering one for myself too. Worth every penny."],
  mid: ["It's a solid product overall. Docked one star because the manual could be clearer. Performance itself is good.", "Works well for the price. Not perfect, but it delivers on most promises.", "Good product, average packaging. Took a few days to get used to, but happy with it now."],
  lo: ["Expected more at this price. Support was slow. Looked elsewhere after that.", "Not compatible with my setup as advertised. Return was easy though.", "Mediocre experience. Quality control seems inconsistent."]
};
function seedReviews(tenantId, p) {
  const rnd = mulberry32(hashStr(p.id + "rv"));
  const n = 4 + Math.floor(rnd() * 2);
  for (let i = 0; i < n; i++) {
    const roll = rnd();
    const r = roll < 0.68 ? 5 : roll < 0.82 ? 4 : roll < 0.92 ? 3 : roll < 0.97 ? 2 : 1;
    const bucket = r >= 4 ? "hi" : r === 3 ? "mid" : "lo";
    const title = RV_TITLES[bucket][Math.floor(rnd() * RV_TITLES[bucket].length)];
    const author = RV_AUTHORS[Math.floor(rnd() * RV_AUTHORS.length)];
    const body = RV_BODIES[bucket][Math.floor(rnd() * RV_BODIES[bucket].length)].replace("{B}", p.b);
    const days = Math.floor(rnd() * 240 + 3);
    run(`INSERT INTO reviews(tenant_id,product_id,name,rating,title,body,verified,created_at) VALUES(?,?,?,?,?,?,1, datetime('now', ?))`,
      tenantId, p.id, author, r, title, body, `-${days} days`);
  }
}

/* ---------------- tenant catalog seeding ---------------- */
function seedTenantCatalog(tenantId, industries) {
  const list = (industries && industries.length) ? PRODUCTS.filter(p => industries.includes(DEPT_TO_INDUSTRY[p.d] || p.d)) : PRODUCTS;
  let pos = 0;
  for (const p of list) {
    const dpct = (p.l && p.l > p.p) ? Math.round((1 - p.p / p.l) * 100) : 0;
    const ex = get("SELECT id FROM products WHERE tenant_id=? AND id=?", tenantId, p.id);
    if (ex) continue;
    run(`INSERT INTO products(tenant_id,id,title,brand,dept,price,list_price,rating,ratings_count,emoji,hue,priority,stock,flags,keywords,deal_pct,position)
         VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`,
      tenantId, p.id, p.t, p.b, DEPT_TO_INDUSTRY[p.d] || p.d, p.p, p.l, p.r, p.c, p.e, p.h, p.pr, p.st, p.fl, p.kw, dpct, pos++);
    (p.about || []).forEach((a, i) => run("INSERT INTO product_bullets(tenant_id,product_id,pos,text) VALUES(?,?,?,?)", tenantId, p.id, i, a));
    seedReviews(tenantId, p);
  }
  return pos;
}
function seedTenantDepartments(tenantId, industries) {
  const meta = require("./meta.js");
  const list = meta.INDUSTRIES.filter(i => !industries || !industries.length || industries.includes(i.key));
  list.forEach((ind, i) => run("INSERT OR IGNORE INTO departments(tenant_id,key,label,icon,position) VALUES(?,?,?,?,?)", tenantId, ind.key, ind.name, ind.icon, i));
}
function seedTenantHome(tenantId, industries) {
  const inScope = dep => !industries || !industries.length || industries.includes(DEPT_TO_INDUSTRY[dep] || dep);
  if (get("SELECT COUNT(*) c FROM home_banners WHERE tenant_id=?", tenantId).c === 0)
    BANNERS.filter(b => inScope(b.dept)).forEach((b, i) => run("INSERT INTO home_banners(tenant_id,title,subtitle,cta,hue,dept,position) VALUES(?,?,?,?,?,?,?)", tenantId, b.title, b.sub, b.cta, b.hue, DEPT_TO_INDUSTRY[b.dept] || b.dept, i));
  if (get("SELECT COUNT(*) c FROM home_cards WHERE tenant_id=?", tenantId).c === 0)
    HOME_CARDS.filter(c => inScope(c.dept)).forEach((c, i) => run("INSERT INTO home_cards(tenant_id,title,dept,tiles,position) VALUES(?,?,?,?,?)", tenantId, c.title, DEPT_TO_INDUSTRY[c.dept] || c.dept, JSON.stringify(c.tiles), i));
}

/* ---------------- meta-model seeding ---------------- */
const CATEGORY_SEED = {
  electronics: ["Mobiles", "Laptops", "TVs & Display", "Audio"],
  grocery: ["Fresh Produce", "Dairy & Eggs", "Bakery", "Frozen Foods"],
  furniture: ["Living Room", "Bedroom", "Office", "Outdoor"],
  construction: ["Tools", "Fasteners", "Electrical", "Plumbing"],
  automotive: ["Spare Parts", "Tyres", "Lubricants", "Accessories"],
  jewellery: ["Rings", "Necklaces", "Bracelets", "Earrings"],
  fashion: ["Men", "Women", "Kids", "Footwear"],
  digital: ["Software", "E-Books", "Courses", "Licenses"],
  services: ["Home Services", "Consultation", "Repair", "Cleaning"],
  rental: ["Equipment", "Vehicles", "Property", "Events"],
  subscription: ["Boxes", "Media", "Software", "Membership"],
  industrial: ["MRO", "Safety Equipment", "Automation", "Machinery"],
  pharma: ["OTC", "Prescription", "Devices", "Wellness"],
  pets: ["Dog", "Cat", "Food", "Toys"],
  sports: ["Fitness", "Outdoor", "Cycling", "Water Sports"],
  media: ["Fiction", "Non-Fiction", "Kids", "Audio Books"],
  luxury: ["Watches", "Bags", "Fragrance", "Accessories"],
  healthcare: ["Diagnostics", "Monitors", "Care", "Nutrition"],
  chemicals: ["Industrial", "Lab", "Agro-Chem", "Consumer"],
  agriculture: ["Seeds", "Fertilizers", "Equipment", "Produce"]
};
const DEPT_TO_INDUSTRY = { electronics: "electronics", computers: "electronics", gaming: "electronics", home: "furniture", kitchen: "furniture", fashion: "fashion", beauty: "retail", toys: "retail", sports: "sports", books: "media", grocery: "grocery", pets: "pets", auto: "automotive", office: "retail", garden: "agriculture", health: "healthcare", tools: "construction", industrial: "industrial", digital: "digital", software: "software", services: "services", media: "media", luxury: "luxury", jewellery: "jewellery", construction: "construction", automotive: "automotive" };

function seedTaxonomy(tenantId, industries) {
  if (get("SELECT COUNT(*) c FROM taxonomy WHERE tenant_id=?", tenantId).c > 0) return;
  const meta = require("./meta.js");
  let pos = 0;
  for (const ind of meta.INDUSTRIES.filter(i => !industries || !industries.length || industries.includes(i.key))) {
    const r = run("INSERT INTO taxonomy(tenant_id,level,key,name,icon,position) VALUES(?,?,?,?,?,?)", tenantId, "industry", ind.key, ind.name, ind.icon, pos++);
    const iid = Number(r.lastInsertRowid);
    (CATEGORY_SEED[ind.key] || []).forEach((cat, ci) => {
      run("INSERT INTO taxonomy(tenant_id,parent_id,level,key,name,position) VALUES(?,?,?,?,?,?)", tenantId, iid, "category", ind.key + "." + cat.toLowerCase().replace(/[^a-z]+/g, "-"), cat, ci);
    });
  }
  const el = get("SELECT id FROM taxonomy WHERE tenant_id=? AND key='electronics'", tenantId);
  if (el) {
    const sub = run("INSERT INTO taxonomy(tenant_id,parent_id,level,key,name,position) VALUES(?,?, 'subcategory','electronics.laptops.ultrabook','Ultrabooks',0)", tenantId, get("SELECT id FROM taxonomy WHERE tenant_id=? AND key='electronics.laptops'", tenantId).id);
    const fam = run("INSERT INTO taxonomy(tenant_id,parent_id,level,key,name,position) VALUES(?,?, 'family','pulsebook','PulseBook',0)", tenantId, Number(sub.lastInsertRowid));
    run("INSERT INTO taxonomy(tenant_id,parent_id,level,key,name,position) VALUES(?,?, 'model','pulsebook.air14','Air 14',0)", tenantId, Number(fam.lastInsertRowid));
  }
}
function seedAttributes(tenantId) {
  if (get("SELECT COUNT(*) c FROM attribute_defs WHERE tenant_id=?", tenantId).c > 0) return;
  const defs = [
    ["color", "Colour", "Appearance", "select", "", ["black", "white", "silver", "gold", "rose", "navy", "beige"]],
    ["size", "Size", "Appearance", "text", "", []],
    ["material", "Material", "Composition", "text", "", []],
    ["weight_kg", "Weight", "Physical", "number", "kg", []],
    ["voltage", "Voltage", "Technical", "text", "V", []],
    ["warranty_months", "Warranty", "Commercial", "number", "month", []],
    ["fabric_gsm", "Fabric GSM", "Textile", "number", "g/m²", []],
    ["thread_count", "Thread Count", "Textile", "number", "", []],
    ["purity", "Purity", "Composition", "text", "K", []],
    ["expiry_date", "Expiry", "Compliance", "date", "", []],
    ["capacity_l", "Capacity", "Physical", "number", "l", []],
    ["energy_rating", "Energy Rating", "Technical", "select", "", ["A+++", "A++", "A+", "A", "B"]]
  ];
  defs.forEach((d, i) => run("INSERT INTO attribute_defs(tenant_id,key,label,grp,type,unit,options,position) VALUES(?,?,?,?,?,?,?,?)",
    tenantId, d[0], d[1], d[2], d[3], d[4], JSON.stringify(d[5]), i));
}
function seedWarehouses(tenantId, list) {
  if (get("SELECT COUNT(*) c FROM warehouses WHERE tenant_id=?", tenantId).c > 0) return;
  list.forEach(w => run("INSERT INTO warehouses(tenant_id,name,code,country,region) VALUES(?,?,?,?,?)", tenantId, w[0], w[1], w[2], w[3]));
}
function addVProduct(tenantId, p) {
  if (get("SELECT id FROM products WHERE tenant_id=? AND id=?", tenantId, p.id)) return;
  const node = get("SELECT id FROM taxonomy WHERE tenant_id=? AND key=?", tenantId, p.nodeKey || "");
  p.dept = DEPT_TO_INDUSTRY[p.dept] || p.dept;
  const dpct = p.list ? Math.round((1 - p.price / p.list) * 100) : 0;
  const pos = get("SELECT COALESCE(MAX(position),0) m FROM products WHERE tenant_id=?", tenantId).m + 1;
  run(`INSERT INTO products(tenant_id,id,title,brand,dept,price,list_price,rating,ratings_count,emoji,hue,priority,stock,flags,keywords,deal_pct,position,
       type,node_id,lifecycle,identity,attrs,vertical,media,seo,tax_rule,geo_rules,pricing_rules,logistics,packaging,docs,uom,supplier_id)
       VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`,
    tenantId, p.id, p.title, p.brand, p.dept || "retail", p.price, p.list || null, p.rating || 4.6, p.count || 120, p.emoji, p.hue || 200,
    p.priority === false ? 0 : 1, p.stock != null ? p.stock : 25, p.flags || "", p.kw || p.title.toLowerCase(), dpct, pos,
    p.type || "physical", node ? node.id : null, p.lifecycle || "published",
    JSON.stringify(p.identity || { sku: p.id }), JSON.stringify(p.attrs || {}), JSON.stringify(p.vertical || {}),
    JSON.stringify(p.media || [{ kind: "image", label: "Front", emoji: p.emoji }]), JSON.stringify(p.seo || { title: p.title, description: (p.about || [""])[0] }),
    JSON.stringify(p.tax_rule || { mode: "standard", exempt: false }), JSON.stringify(p.geo_rules || []),
    JSON.stringify(p.pricing_rules || {}), JSON.stringify(p.logistics || { shippingClass: "standard" }),
    JSON.stringify(p.packaging || []), JSON.stringify(p.docs || []), JSON.stringify(p.uom || { unit: "ea" }), p.supplier_id || null);
  (p.about || []).forEach((a, i) => run("INSERT INTO product_bullets(tenant_id,product_id,pos,text) VALUES(?,?,?,?)", tenantId, p.id, i, a));
  (p.skus || [{ code: p.id, name: "Default", price: p.price, stock: p.stock != null ? p.stock : 25 }]).forEach(sk => {
    const r = run("INSERT INTO skus(tenant_id,product_id,code,name,identity,variant,price,mrp,stock) VALUES(?,?,?,?,?,?,?,?,?)",
      tenantId, p.id, sk.code, sk.name || "", JSON.stringify(sk.identity || { sku: sk.code }), JSON.stringify(sk.variant || {}), sk.price, sk.mrp || null, sk.stock);
    const wh = get("SELECT id FROM warehouses WHERE tenant_id=? ORDER BY id LIMIT 1", tenantId);
    run("INSERT INTO inventory(tenant_id,sku_id,warehouse_id,qty,reserved,lot,batch,expiry,serial) VALUES(?,?,?,?,?,?,?,?,?)",
      tenantId, Number(r.lastInsertRowid), wh ? wh.id : null, sk.stock, 0, sk.lot || "", sk.batch || "", sk.expiry || "", JSON.stringify(sk.serial || []));
  });
  (p.rels || []).forEach(([to, type]) => run("INSERT INTO relationships(tenant_id,from_id,to_id,type) VALUES(?,?,?,?)", tenantId, p.id, to, type));
  seedReviews(tenantId, { id: p.id, b: p.brand });
}
function seedVerticalProducts(tenantId, allowed) {
  const V = [
    { id: "VR-GROC-01", title: "Alpine Organic Whole Milk 1L — Farm Fresh", brand: "Alpine Dairy", dept: "grocery", nodeKey: "grocery.dairy-eggs", type: "consumable", price: 4.99, list: 6.49, rating: 4.8, count: 2140, emoji: "🥛", hue: 205, stock: 120, flags: "bs", kw: "milk dairy organic fresh", about: ["Certified organic, single-origin Alpine valley milk", "Cold-chain delivered within 48h of milking", "Rich 3.8% butterfat, non-homogenised"], identity: { sku: "VR-GROC-01", gtin: "0762221021257", lot: "LOT-2291", batch: "B-2291", hsn: "0401" }, attrs: { capacity_l: 1, expiry_date: "2026-10-02" }, vertical: { expiry_date: "2026-10-02", mfg_date: "2026-09-08", best_before: "Use by 02 Oct", storage: "Refrigerate 2-4°C", temp_min: 2, temp_max: 4, lot_tracked: true, batch_tracked: true, nutrition: { energy_kcal: 65, protein_g: 3.4, fat_g: 3.8, carbs_g: 4.8 }, ingredients: "Organic whole cow's milk", allergens: ["milk"], origin: "CH", fssai: "FSSAI-10021", organic_cert: "USDA-ORG-8812" }, media: [{ kind: "image", label: "Bottle", emoji: "🥛" }, { kind: "certificate", label: "Organic cert", emoji: "📜" }], logistics: { shippingClass: "cold_chain" }, packaging: [{ level: "primary", unit: "bottle", qty: 1 }, { level: "secondary", unit: "case", qty: 12 }, { level: "tertiary", unit: "pallet", qty: 720 }], uom: { unit: "l" } },
    { id: "VR-FURN-01", title: "Nordica 3-Seater Bouclé Sofa — Sand", brand: "Nordica", dept: "home", nodeKey: "furniture.living-room", type: "physical", price: 1249, list: 1599, rating: 4.7, count: 860, emoji: "🛋️", hue: 35, stock: 8, flags: "bs", kw: "sofa living room boucle furniture", about: ["Kiln-dried beech frame, 10-year warranty", "Feather-wrapped high-resilience foam", "Modular — add chaise or 2-seater"], identity: { sku: "VR-FURN-01", gtin: "5901234123457", mpn: "NORD-3S-SND" }, attrs: { color: "beige", material: "Bouclé / beech", weight_kg: 62 }, vertical: { material: "Beech + bouclé", dimensions: "218×92×82 cm", weight_kg: 62, assembly_required: true, room: "living", swatches: ["sand", "fog", "clay"], wood_type: "European beech", fabric_type: "Bouclé 480gsm", spare_parts: true, assembly_service: true, install_service: true }, media: [{ kind: "image", label: "Front", emoji: "🛋️" }, { kind: "manual", label: "Assembly PDF", emoji: "📖" }, { kind: "model3d", label: "3D view", emoji: "🧊" }], seo: { title: "Nordica Bouclé Sofa", description: "Scandinavian 3-seater in sand bouclé" }, logistics: { shippingClass: "white_glove", install_required: true }, packaging: [{ level: "tertiary", unit: "carton", qty: 3 }], uom: { unit: "ea" }, rels: [["VR-BUND-01", "bundle"]] },
    { id: "VR-HARD-01", title: "M8×40 Stainless Hex Bolt — A2-70 (100 pack)", brand: "Fastenal Pro", dept: "auto", nodeKey: "construction.fasteners", type: "raw_material", price: 18.5, rating: 4.6, count: 430, emoji: "🔩", hue: 220, stock: 5000, flags: "", kw: "bolt fastener stainless hex m8 hardware", about: ["A2-70 austenitic stainless, marine grade", "DIN 931 partially threaded", "Bulk tiers auto-applied at checkout"], identity: { sku: "VR-HARD-01", gtin: "4041501123456", hsn: "7318", unspsc: "31161502", part_number: "M8-40-A270" }, attrs: { material: "A2-70 stainless", size: "M8×40" }, vertical: { thread_size: "M8×1.25", diameter_mm: 8, length_mm: 40, material_grade: "A2-70", tolerance: "6g", finish: "Plain", load_capacity: "33 kN proof", torque_rating: "25 Nm", pressure_rating: "n/a", compat_matrix: { wrench: "13mm", nut: "M8 DIN934" } }, pricing_rules: { tiers: [{ qty: 10, price: 16.5 }, { qty: 100, price: 14.2 }, { qty: 1000, price: 11.9 }], b2b: true }, logistics: { shippingClass: "heavy" }, packaging: [{ level: "primary", unit: "box", qty: 100 }, { level: "pallet", unit: "pallet", qty: 48000 }], uom: { unit: "set" } },
    { id: "VR-AUTO-01", title: "Ceramic Brake Pad Set — Front Axle", brand: "Brembo", dept: "auto", nodeKey: "automotive.spare-parts", type: "finished_good", price: 129.99, list: 164.99, rating: 4.7, count: 1210, emoji: "🛞", hue: 10, stock: 44, flags: "ac", kw: "brake pads ceramic automotive brembo", about: ["Low-dust ceramic compound", "Includes shims & hardware kit", "OE-matched friction"], identity: { sku: "VR-AUTO-01", gtin: "8032534012345", oem: "34116878204", mpn: "P83041" }, vertical: { makes: ["BMW", "Mini"], models: "3-series F30 / F31", years: "2012-2019", engine: "N20/N26/B48", fuel: "petrol", vin_mapping: "WBA…F30", oem_ref: "34116878204", fitment: { front: "yes", rotor: "320mm" }, labor_hours: 1.2 }, logistics: { shippingClass: "standard" }, rels: [["VR-HARD-01", "accessory"]], uom: { unit: "set" } },
    { id: "VR-ELEC-01", title: "PulseBook Air 14 — M-Class 16GB/512GB", brand: "Pulse", dept: "computers", nodeKey: "electronics.laptops", type: "physical", price: 1099, list: 1299, rating: 4.8, count: 3400, emoji: "💻", hue: 250, stock: 15, flags: "bs new", kw: "laptop ultrabook pulsebook computer", about: ["18-hour battery, fanless design", "14\" 2.8K 120Hz Liquid Retina", "Wi-Fi 7 + Thunderbolt 4"], identity: { sku: "VR-ELEC-01", gtin: "0123456789012", imei: null, serial: "PB-AIR14-0001", mpn: "PB14-M2-512" }, attrs: { color: "silver", weight_kg: 1.24, warranty_months: 24 }, vertical: { imei_required: false, serial_required: true, firmware: "2.4.1", warranty_months: 24, repair_coverage: "onsite", voltage: "100-240V", power_w: 67, energy_rating: "A+++", compat_matrix: { docks: "TB4/USB-C" } }, media: [{ kind: "image", label: "Open", emoji: "💻" }, { kind: "video", label: "Film", emoji: "🎬" }, { kind: "warranty_doc", label: "Warranty", emoji: "🛡️" }], logistics: { shippingClass: "fragile" }, rels: [["VR-BUND-01", "bundle"], ["VR-DIGI-01", "cross_sell"]], uom: { unit: "ea" } },
    { id: "VR-JEW-01", title: "Aurelia 22K Gold Bangle — Hallmarked", brand: "Velora", dept: "jewellery", nodeKey: "jewellery.bracelets", type: "physical", price: 2890, rating: 4.9, count: 310, emoji: "💍", hue: 45, stock: 6, flags: "bs", priority: false, kw: "gold bangle jewellery hallmark 22k", about: ["BIS hallmarked 22K (916) gold", "Live gold-rate locked at dispatch", "Complimentary lifetime polish"], identity: { sku: "VR-JEW-01", gtin: "8901234567890", serial: "VEL-BGL-2209" }, attrs: { purity: "22K", weight_kg: 0.042 }, vertical: { purity: "916 / 22K", hallmark: "BIS-916-HG", stone_cert: null, weight_g: 42, making_charges_pct: 11, live_pricing: true, metal: "gold" }, logistics: { shippingClass: "white_glove", cross_border_restricted: true }, geo_rules: [{ country: "IN", note: "Import duties included" }], uom: { unit: "g" } },
    { id: "VR-DIGI-01", title: "StudioForge Pro — Perpetual License (1 seat)", brand: "Forge Labs", dept: "computers", nodeKey: "digital.software", type: "license", price: 199, rating: 4.5, count: 980, emoji: "🧩", hue: 280, stock: 9999, flags: "", kw: "software license 3d design digital", about: ["Instant key delivery", "Perpetual + 1yr updates", "Offline activation"], identity: { sku: "VR-DIGI-01" }, vertical: { license_key: true, activation: "1 seat, 2 deactivations/yr", downloads: 3, streaming: "n/a", drm: "none", sub_rules: "optional upgrade plan" }, logistics: { shippingClass: "standard", digital: true }, uom: { unit: "ea" } },
    { id: "VR-SERV-01", title: "Home Deep Cleaning — 3 Rooms (2 crew)", brand: "SparkNest", dept: "home", nodeKey: "services.home-services", type: "appointment", price: 149, rating: 4.6, count: 540, emoji: "🧽", hue: 160, stock: 999, flags: "", kw: "cleaning service home appointment", about: ["Eco-certified products", "Vetted 2-person crew", "Re-clean guarantee"], identity: { sku: "VR-SERV-01" }, vertical: { appointment: true, duration_min: 180, location_mode: "onsite", workforce: 2, sla: "48h reschedule", contract: "none" }, logistics: { shippingClass: "standard", service: true }, uom: { unit: "hr" } },
    { id: "VR-RENT-01", title: "Pro Drill & Impact Driver Kit — Weekly Rental", brand: "Hilti", dept: "tools", nodeKey: "rental.equipment", type: "rental", price: 59, rating: 4.4, count: 210, emoji: "🛠️", hue: 20, stock: 12, flags: "", priority: false, kw: "rental drill tools equipment weekly", about: ["Deposit refundable on return", "Insurance option at checkout", "Pickup or delivery"], identity: { sku: "VR-RENT-01", serial: "HIL-KIT-77" }, vertical: { durations: [{ label: "Day", price: 25 }, { label: "Week", price: 59 }, { label: "Month", price: 149 }], deposit: 200, asset_tracking: true, damage: true, return_inspection: true }, logistics: { shippingClass: "heavy" }, uom: { unit: "day" } },
    { id: "VR-SUBS-01", title: "Bean Box — Specialty Coffee Subscription", brand: "Roast & Co", dept: "grocery", nodeKey: "subscription.boxes", type: "subscription", price: 24.99, rating: 4.8, count: 4200, emoji: "☕", hue: 25, stock: 999, flags: "bs", kw: "coffee subscription beans monthly", about: ["Rotating single-origin roasts", "Skip or pause anytime", "Free shipping every cycle"], identity: { sku: "VR-SUBS-01" }, vertical: { license_key: false, activation: "n/a", downloads: 0, streaming: "n/a", drm: "none", sub_rules: "monthly billing, cancel anytime" }, logistics: { shippingClass: "standard" }, uom: { unit: "month" } },
    { id: "VR-BUND-01", title: "Home Cinema Bundle — Sofa + PulseBook + Audio", brand: "LUXORA Studio", dept: "home", nodeKey: "furniture.living-room", type: "bundle", price: 1999, list: 2487, rating: 4.7, count: 90, emoji: "🎁", hue: 320, stock: 5, flags: "", kw: "bundle home cinema sofa laptop", about: ["Save $488 vs buying separately", "Curated by our design studio", "Single white-glove delivery"], identity: { sku: "VR-BUND-01" }, pricing_rules: { bundle_items: ["VR-FURN-01", "VR-ELEC-01"], bundle_price: 1999 }, rels: [["VR-FURN-01", "bundle"], ["VR-ELEC-01", "bundle"]], logistics: { shippingClass: "white_glove" }, uom: { unit: "set" } },
    { id: "VR-IND-01", title: "Industrial Air Compressor 5HP — Tank Mount", brand: "Atlas Copco", dept: "industrial", nodeKey: "industrial.machinery", type: "equipment", price: 2450, list: 2890, rating: 4.5, count: 140, emoji: "🏭", hue: 200, stock: 4, flags: "", priority: false, kw: "compressor industrial machinery air", about: ["AMC contracts available", "Calibration certificate included", "Installation crew on request"], identity: { sku: "VR-IND-01", gtin: "7312345678904", part_number: "AC-GX5-270" }, vertical: { tech_specs: { power_kw: 3.7, pressure_bar: 10, tank_l: 270, noise_db: 68 }, maintenance: "500h service interval", calibration: "ISO-17025", compliance_docs: "CE/UKCA", safety_sheet: "MSDS-AC", install_service: true, amc: true, warranty_contract: true }, pricing_rules: { tiers: [{ qty: 2, price: 2300 }, { qty: 5, price: 2150 }], b2b: true }, logistics: { shippingClass: "heavy", install_required: true }, uom: { unit: "ea" } },
    { id: "VR-VEHI-01", title: "Volt Crossover EV — 2026 Long Range", brand: "Volt Motors", dept: "auto", nodeKey: "automotive.spare-parts", type: "vehicle", price: 42900, rating: 4.6, count: 60, emoji: "🚙", hue: 190, stock: 3, flags: "new", priority: false, kw: "electric car vehicle ev crossover", about: ["520 km WLTP range", "Book a test drive online", "8-year battery warranty"], identity: { sku: "VR-VEHI-01", vin: "1VVK2345678901234" }, vertical: { vin: "1VVK2345678901234", make: "Volt", model: "Crossover", year: 2026, engine: "Dual motor AWD", transmission: "Single-speed", emission_class: "Zero", test_drive: true }, logistics: { shippingClass: "oversized" }, uom: { unit: "ea" } },
    { id: "VR-HEAL-01", title: "CardioGuard BP Monitor — Clinically Validated", brand: "Omron Health", dept: "health", nodeKey: "healthcare.monitors", type: "physical", price: 89.99, list: 99.99, rating: 4.6, count: 720, emoji: "🩺", hue: 170, stock: 30, flags: "", kw: "blood pressure monitor medical device", about: ["AFib detection algorithm", "Clinically validated accuracy", "2-user memory + app sync"], identity: { sku: "VR-HEAL-01", gtin: "4542234567890", serial: "CG-BP-0042" }, vertical: { lot_tracked: true, serial_tracked: true, udi: "04542234BP01", regulatory: "FDA 510(k) K213", expiry_tracked: false, storage_compliance: "10-40°C", prescription: false, audit_trail: true }, logistics: { shippingClass: "standard" }, uom: { unit: "ea" } }
  ];
  V.forEach(p => {
    if (allowed && allowed.length && !allowed.includes((p.nodeKey || "").split(".")[0])) return;
    addVProduct(tenantId, p);
  });
}
function seedMarketExtras(tenantId) {
  if (get("SELECT COUNT(*) c FROM promotions WHERE tenant_id=?", tenantId).c === 0) {
    run("INSERT INTO promotions(tenant_id,name,type,value,rules,scope,starts,ends,status,code) VALUES(?,?,?,?,?,?,?,?,?,?)",
      tenantId, "Fresh & Dairy 10%", "percent", 10, "{}", JSON.stringify({ node: "grocery" }), date0(), date365(), "active", "FRESH10");
    run("INSERT INTO promotions(tenant_id,name,type,value,rules,scope,starts,ends,status,code) VALUES(?,?,?,?,?,?,?,?,?,?)",
      tenantId, "Welcome 10% off", "percent", 10, "{}", "{}", date0(), date365(), "active", "WELCOME10");
  }
  if (get("SELECT COUNT(*) c FROM sellers WHERE tenant_id=?", tenantId).c === 0) {
    run("INSERT INTO sellers(tenant_id,name,role,email,commission_pct) VALUES(?,?,?,?,?)", tenantId, "Nordica AB", "manufacturer", "sales@nordica.example", 8);
    run("INSERT INTO sellers(tenant_id,name,role,email,commission_pct) VALUES(?,?,?,?,?)", tenantId, "Alpine Dairy Co", "manufacturer", "orders@alpine.example", 5);
    run("INSERT INTO sellers(tenant_id,name,role,email,commission_pct) VALUES(?,?,?,?,?)", tenantId, "TechVault Inc", "marketplace_seller", "partners@techvault.example", 12);
    run("INSERT INTO sellers(tenant_id,name,role,email,commission_pct) VALUES(?,?,?,?,?)", tenantId, "Fastenal Pro", "distributor", "b2b@fastenal.example", 6);
  }
  if (get("SELECT COUNT(*) c FROM rfqs WHERE tenant_id=?", tenantId).c === 0) {
    run("INSERT INTO rfqs(tenant_id,ref,product_id,buyer_name,buyer_email,qty,target_price,currency,status,quotes) VALUES(?,?,?,?,?,?,?,?,?,?)",
      tenantId, "RFQ-" + tenantId + "-1001", "VR-HARD-01", "BuildRight LLC", "procure@buildright.example", 5000, 10.5, "USD", "open", JSON.stringify([{ seller: "Fastenal Pro", price: 11.2, lead_days: 12, note: "ex-works" }]));
  }
  const ord = get("SELECT id FROM orders WHERE tenant_id=? ORDER BY id LIMIT 1", tenantId);
  if (ord && get("SELECT COUNT(*) c FROM returns WHERE tenant_id=?", tenantId).c === 0) {
    run("INSERT INTO returns(tenant_id,ref,order_id,product_id,qty,reason,status) VALUES(?,?,?,?,?,?,?)",
      tenantId, "RET-" + tenantId + "-2001", ord.id, "LX-CMP-005", 1, "Arrived damaged", "refunded");
    const seller = get("SELECT id, commission_pct FROM sellers WHERE tenant_id=? ORDER BY id LIMIT 1", tenantId);
    if (seller) {
      const o = get("SELECT total FROM orders WHERE id=?", ord.id);
      const gross = o.total, comm = +(gross * seller.commission_pct / 100).toFixed(2);
      run("INSERT INTO settlements(tenant_id,ref,seller_id,order_id,gross,commission,net,status,period) VALUES(?,?,?,?,?,?,?,?,?)",
        tenantId, "STL-" + tenantId + "-3001", seller.id, ord.id, gross, comm, +(gross - comm).toFixed(2), "paid", new Date().toISOString().slice(0, 7));
    }
  }
}
function date0() { return new Date().toISOString().slice(0, 10); }
function date365() { const d = new Date(); d.setDate(d.getDate() + 365); return d.toISOString().slice(0, 10); }
function seedMeta(tenantId, industries) {
  seedTaxonomy(tenantId, industries);
  seedAttributes(tenantId);
  seedWarehouses(tenantId, [["Main DC", "DC1", "US", "WA"], ["East DC", "DC2", "US", "NJ"]]);
  seedVerticalProducts(tenantId, industries);
  seedMarketExtras(tenantId);
  seedAdvanced(tenantId);
  /* backfill legacy catalog products with meta defaults */
  for (const p of all("SELECT id, dept FROM products WHERE tenant_id=? AND node_id IS NULL", tenantId)) {
    const ik = DEPT_TO_INDUSTRY[p.dept] || p.dept;
    const node = ik && get("SELECT id FROM taxonomy WHERE tenant_id=? AND key=?", tenantId, ik);
    run("UPDATE products SET node_id=?, type='physical', lifecycle='published', identity=json_object('sku', id), attrs='{}', vertical='{}', media=json_array(json_object('kind','image','label','Front','emoji',emoji)), seo='{}', tax_rule='{}', geo_rules='[]', pricing_rules='{}', logistics=json_object('shippingClass','standard'), packaging='[]', docs='[]', uom=json_object('unit','ea') WHERE tenant_id=? AND id=?", node ? node.id : null, tenantId, p.id);
  }
  for (const p of all("SELECT id, price, stock FROM products WHERE tenant_id=? AND id NOT IN (SELECT product_id FROM skus WHERE tenant_id=?)", tenantId, tenantId)) {
    const r = run("INSERT INTO skus(tenant_id,product_id,code,name,identity,variant,price,mrp,stock) VALUES(?,?,?,?,?,?,?,NULL,?)", tenantId, p.id, p.id, "Default", JSON.stringify({ sku: p.id }), "{}", p.price, p.stock);
    const wh = get("SELECT id FROM warehouses WHERE tenant_id=? ORDER BY id LIMIT 1", tenantId);
    run("INSERT INTO inventory(tenant_id,sku_id,warehouse_id,qty,reserved) VALUES(?,?,?,?,0)", tenantId, Number(r.lastInsertRowid), wh ? wh.id : null, p.stock);
  }
}

/* advanced universal-model seed: suppliers, serialization, variant groups,
   compliance/certifications, localizations, B2B contracts & tenders. Idempotent. */
function seedAdvanced(tenantId) {
  const wh1 = get("SELECT id FROM warehouses WHERE tenant_id=? ORDER BY id LIMIT 1", tenantId);
  const whId = wh1 ? wh1.id : null;
  const prod = id => get("SELECT * FROM products WHERE tenant_id=? AND id=?", tenantId, id);
  const jv = (s, d) => { try { return JSON.parse(s || JSON.stringify(d == null ? {} : d)); } catch (e) { return d; } };
  const firstSku = id => (get("SELECT id FROM skus WHERE tenant_id=? AND product_id=? ORDER BY id LIMIT 1", tenantId, id) || {}).id || null;

  if (get("SELECT COUNT(*) c FROM suppliers WHERE tenant_id=?", tenantId).c === 0) {
    const mk = (name, role, country, lead, moq, terms, certs, price_list) => run(
      "INSERT INTO suppliers(tenant_id,name,party_role,country,email,phone,lead_time_days,moq,currency,payment_terms,status,certifications,price_list) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
      tenantId, name, role, country, "sales@" + name.toLowerCase().replace(/[^a-z0-9]+/g, "") + ".example", "+1-555-0100", lead, moq, "USD", terms, "active", JSON.stringify(certs || []), JSON.stringify(price_list || {}));
    mk("Brembo Parts Co", "manufacturer", "IT", 14, 10, "net45", ["ISO-9001", "IATF-16949"], prod("VR-AUTO-01") ? { "VR-AUTO-01": 78 } : {});
    mk("Atlas Copco Supply", "manufacturer", "SE", 21, 1, "net60", ["CE"], {});
    mk("Global Fastener Supply", "distributor", "DE", 5, 500, "net30", ["DIN"], prod("VR-HARD-01") ? { "VR-HARD-01": 9.5 } : {});
    const supOf = n => (get("SELECT id FROM suppliers WHERE tenant_id=? AND name=?", tenantId, n) || {}).id || null;
    const link = (pid, supName, cost, lead, primary) => { const sid = supOf(supName); if (!sid || !prod(pid)) return; try { run("INSERT INTO product_suppliers(tenant_id,product_id,supplier_id,price,lead_days,is_primary) VALUES(?,?,?,?,?,?)", tenantId, pid, sid, cost, lead, primary ? 1 : 0); } catch (e) { } };
    link("VR-AUTO-01", "Brembo Parts Co", 78, 14, true);
    link("VR-IND-01", "Atlas Copco Supply", 1650, 21, true);
    link("VR-HARD-01", "Global Fastener Supply", 9.5, 5, true);
    link("VR-HARD-01", "Atlas Copco Supply", 10.2, 12, false);
  }

  if (get("SELECT COUNT(*) c FROM serialized_items WHERE tenant_id=?", tenantId).c === 0) {
    for (const p of all("SELECT * FROM products WHERE tenant_id=? AND (vertical LIKE '%serial%' OR identity LIKE '%serial%')", tenantId)) {
      const v = jv(p.vertical, {}), idn = jv(p.identity, {});
      if (!(v.serial_required || v.serial_tracked || idn.serial)) continue;
      const base = idn.serial || p.id + "-SN", now = new Date();
      for (let i = 1; i <= 3; i++) {
        const wy = new Date(now.getTime()); wy.setMonth(wy.getMonth() + (v.warranty_months || 24));
        try {
          run("INSERT INTO serialized_items(tenant_id,product_id,sku_id,warehouse_id,serial,imei,batch,lot,expiry,status,condition,warranty_end,purchase_date) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
            tenantId, p.id, firstSku(p.id), whId, base + "-" + String(i).padStart(3, "0"),
            v.imei_required ? "35" + (100000000000 + i) : null, "B-202" + i, "LOT-" + (5100 + i),
            p.type === "consumable" ? date365() : null, i === 3 ? "allocated" : "in_stock", "new", wy.toISOString().slice(0, 10), date0());
        } catch (e) { }
      }
    }
  }

  if (get("SELECT COUNT(*) c FROM variant_groups WHERE tenant_id=?", tenantId).c === 0) {
    const addGroup = (p, name, axis, attrKey, options) => {
      const gid = Number(run("INSERT INTO variant_groups(tenant_id,product_id,name,axis,attr_key,active) VALUES(?,?,?,?,?,1)", tenantId, p.id, name, axis, attrKey).lastInsertRowid);
      options.forEach(opt => {
        const code = p.id + "-" + opt.code; if (get("SELECT id FROM skus WHERE tenant_id=? AND code=?", tenantId, code)) return;
        const stock = opt.stock != null ? opt.stock : 20;
        const sr = run("INSERT INTO skus(tenant_id,product_id,code,name,identity,variant,price,mrp,stock,group_id,active) VALUES(?,?,?,?,?,?,?,?,?,?,1)",
          tenantId, p.id, code, opt.label, JSON.stringify({ sku: code }), JSON.stringify(Object.assign({ [attrKey]: opt.variant }, { })), (p.price + (opt.delta || 0)).toFixed(2), p.list_price || null, stock, gid);
        run("INSERT INTO inventory(tenant_id,sku_id,warehouse_id,qty,reserved) VALUES(?,?,?,?,0)", tenantId, Number(sr.lastInsertRowid), whId, stock);
      });
    };
    const sofa = prod("VR-FURN-01"); if (sofa) addGroup(sofa, "Colour", "Colour", "color", [{ code: "SND", label: "Sand", variant: "sand", delta: 0, stock: 8 }, { code: "FOG", label: "Fog", variant: "fog", delta: 40, stock: 5 }, { code: "CLY", label: "Clay", variant: "clay", delta: 60, stock: 4 }]);
    const lap = prod("VR-ELEC-01"); if (lap) addGroup(lap, "Storage", "Storage", "capacity_gb", [{ code: "512", label: "512GB", variant: 512, delta: 0, stock: 15 }, { code: "1TB", label: "1TB", variant: 1024, delta: 200, stock: 9 }]);
  }

  if (get("SELECT COUNT(*) c FROM compliance_records WHERE tenant_id=?", tenantId).c === 0) {
    const put = (p, kind, code, issuer, jur) => { if (!code) return; try { run("INSERT INTO compliance_records(tenant_id,scope,ref_id,kind,code,issuer,jurisdiction,status,valid_from,valid_to) VALUES(?,?,?,?,?,?,?,?,?,?)", tenantId, "product", p.id, kind, String(code), issuer || "", jur || "", "valid", date0(), date365()); } catch (e) { } };
    for (const p of all("SELECT id,identity,vertical FROM products WHERE tenant_id=?", tenantId)) {
      const v = jv(p.vertical, {}) || {}, idn = jv(p.identity, {}) || {};
      put(p, "authorization", v.fssai, "Food Safety Authority", "IN");
      put(p, "certificate", v.organic_cert, "USDA Organic", "US");
      put(p, "mark", v.hallmark, "BIS", "IN");
      put(p, "certificate", v.stone_cert, "GIA", "US");
      put(p, "registration", v.udi, "FDA UDI", "US");
      put(p, "approval", v.regulatory, "FDA", "US");
      put(p, "certificate", v.compliance_docs, "Conformity (Notified Body)", "");
      put(p, "certificate", v.calibration, "ISO-17025 Calibration", "");
      put(p, "license", v.seed_cert, "Seed Certification Board", "");
    }
  }

  if (get("SELECT COUNT(*) c FROM localizations WHERE tenant_id=?", tenantId).c === 0) {
    const loc = (ref, locale, name, desc, bullets) => { if (!prod(ref)) return; try { run("INSERT INTO localizations(tenant_id,entity,ref_id,locale,name,description,bullets) VALUES(?,?,?,?,?,?,?)", tenantId, "product", ref, locale, name, desc, JSON.stringify(bullets || [])); } catch (e) { } };
    loc("VR-GROC-01", "fr-FR", "Lait entier biologique des Alpes 1L", "Lait bio d’origine alpine, chaîne du froid garantie.", ["Certifié biologique", "Livré sous 48 h"]);
    loc("VR-GROC-01", "hi-IN", "अल्पाइन जैविक दूध 1L", "प्रमाणित जैविक अल्पाइन दूध।", ["प्रमाणित जैविक"]);
    loc("VR-FURN-01", "es-MX", "Sofá Bouclé Nordica 3 plazas — Arena", "Sofá escandinavo tapizado en bouclé color arena.", ["Estructura de haya", "Garantía de 10 años"]);
  }

  if (prod("VR-HARD-01") && get("SELECT COUNT(*) c FROM contracts WHERE tenant_id=?", tenantId).c === 0) {
    const supId = (get("SELECT id FROM suppliers WHERE tenant_id=? ORDER BY id LIMIT 1", tenantId) || {}).id || null;
    run("INSERT INTO contracts(tenant_id,ref,buyer_name,buyer_email,buyer_org,supplier_id,product_ids,currency,pricing,min_qty,incoterms,payment_terms,valid_from,valid_to,status,notes) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
      tenantId, "CT-ADV-" + tenantId + "-1001", "Demo Shopper", "demo@luxora.shop", "LUXORA Procurement", supId, JSON.stringify(["VR-HARD-01"]), "USD", JSON.stringify({ fixed: { "VR-HARD-01": 10.0 } }), 5, "FOB", "net30", date0(), date365(), "active", "Contracted bulk pricing for M8 fasteners.");
  }
  if (prod("VR-HARD-01") && get("SELECT COUNT(*) c FROM tenders WHERE tenant_id=?", tenantId).c === 0) {
    run("INSERT INTO tenders(tenant_id,ref,title,buyer_org,buyer_email,description,currency,budget,open_at,close_at,status,items) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
      tenantId, "TDR-ADV-" + tenantId + "-2001", "Annual fastener supply — M8 hex bolts", "BuildRight LLC", "procure@buildright.example", "Supply of 100,000 M8×40 A2-70 hex bolts over 12 months.", "USD", 1200000, date0(), date365(), "open", JSON.stringify([{ product_id: "VR-HARD-01", qty: 100000, unit_budget: 12 }]));
  }
}

/* ---------------- bootstrap ---------------- */
function bootstrap() {
  /* Seed bootstrap credentials — one documented default block; override via env, rotate via console. */
  const SEED = {
    platformEmail: (process.env.PLATFORM_EMAIL || "platform@luxora.shop").toLowerCase(),
    platformPw: process.env.PLATFORM_PASSWORD || "platform123",
    adminEmail: (process.env.ADMIN_EMAIL || "admin@luxora.shop").toLowerCase(),
    adminPw: process.env.ADMIN_PASSWORD || "admin123",
    aurumEmail: "admin@aurum.shop", aurumPw: process.env.AURUM_ADMIN_PASSWORD || "aurum123",
    veloraEmail: "admin@velora.shop", veloraPw: process.env.VELORA_ADMIN_PASSWORD || "velora123",
    demoEmail: "demo@luxora.shop", demoPw: process.env.DEMO_PASSWORD || "demo123"
  };
  seedAuditChain();
  if (get("SELECT COUNT(*) c FROM tenants").c === 0) {
    const t1 = Number(run("INSERT INTO tenants(slug,name,domain,mode,industries) VALUES('luxora','LUXORA','luxora.localhost','marketplace','[]')").lastInsertRowid);
    const t2 = Number(run("INSERT INTO tenants(slug,name,domain,status,mode,industries) VALUES('aurum','AURUM ATELIER','aurum.localhost','active','industry','[\"fashion\",\"beauty\",\"home\",\"kitchen\",\"health\"]')").lastInsertRowid);
    const t3 = Number(run("INSERT INTO tenants(slug,name,domain,status,mode,industries) VALUES('velora','VELORA','velora.localhost','active','brand','[\"jewellery\",\"luxury\"]')").lastInsertRowid);
    seedTenantDepartments(t1, null);
    seedTenantHome(t1, null);
    seedTenantCatalog(t1, null);
    seedMeta(t1, null);
    seedTenantDepartments(t2, ["fashion", "retail", "furniture", "healthcare", "grocery"]);
    seedTenantHome(t2, ["fashion", "retail", "furniture", "healthcare", "grocery"]);
    seedTenantCatalog(t2, ["fashion", "retail", "furniture", "healthcare", "grocery"]);
    seedMeta(t2, ["fashion", "retail", "grocery", "healthcare", "furniture"]);
    seedTenantDepartments(t3, ["jewellery", "luxury"]);
    seedTenantHome(t3, ["jewellery", "luxury"]);
    seedTenantCatalog(t3, ["fashion", "jewellery", "luxury"]);
    seedMeta(t3, ["jewellery", "luxury"]);
    addVProduct(t3, { id: "VL-BGL-01", title: "Aurelia 22K Gold Bangle — Hallmarked", brand: "Velora", dept: "jewellery", nodeKey: "jewellery.bracelets", type: "physical", price: 2890, rating: 4.9, count: 310, emoji: "💍", hue: 45, stock: 6, flags: "bs", priority: false, kw: "gold bangle jewellery hallmark", about: ["BIS hallmarked 22K gold", "Live gold-rate lock at dispatch", "Lifetime polish"], vertical: { purity: "916 / 22K", hallmark: "BIS-916", weight_g: 42, making_charges_pct: 11, live_pricing: true, metal: "gold" }, logistics: { shippingClass: "white_glove" } });
    addVProduct(t3, { id: "VL-RNG-01", title: "Solstice Solitaire Ring — 0.75ct GIA", brand: "Velora", dept: "jewellery", nodeKey: "jewellery.rings", type: "physical", price: 4650, rating: 4.8, count: 120, emoji: "💎", hue: 260, stock: 4, flags: "new", priority: false, kw: "diamond ring solitaire gia jewellery", about: ["GIA certified 0.75ct F/VS1", "Hand-set in 18K white gold", "Complimentary sizing"], vertical: { purity: "18K", hallmark: "BIS-750", stone_cert: "GIA-2141", weight_g: 4.2, making_charges_pct: 14, live_pricing: false, metal: "gold" }, logistics: { shippingClass: "white_glove" } });
    addVProduct(t3, { id: "VL-WCH-01", title: "Meridian Automatic — Sapphire Crystal", brand: "Velora", dept: "luxury", nodeKey: "luxury.watches", type: "physical", price: 1890, list: 2200, rating: 4.7, count: 240, emoji: "⌚", hue: 210, stock: 9, flags: "ac", priority: false, kw: "watch automatic sapphire luxury", about: ["In-house 42h calibre", "100m water resistance", "Alligator strap + steel bracelet"], vertical: { material: "316L steel", warranty_months: 36 }, logistics: { shippingClass: "white_glove" } });
    run("INSERT INTO settings(tenant_id,key,value) VALUES(?, 'brand', ?)", t3, JSON.stringify({ name: "VELORA", wordmark: "VELORA", tagline: "The house of gold — fine jewellery, hallmarked.", supportEmail: "atelier@velora.shop", footerNote: "© {year} Velora — brand store on LUXORA Platform." }));
    run("INSERT INTO settings(tenant_id,key,value) VALUES(?, 'theme', ?)", t3, JSON.stringify({ bg: "#FBF7F2", header: "#241A12", accent: "#B98A3E", accentDeep: "#8C6425", accentSoft: "#F3E7D2", ink: "#241A12", muted: "#7C6F60", line: "#EAE0D2", star: "#B98A3E", link: "#8C6425", linkHover: "#B98A3E", price: "#241A12", radius: "4px", radiusBtn: "4px", fontDisplay: '"Copperplate","Trajan Pro",Georgia,serif', fontBody: '"Futura","Century Gothic","Avenir Next",Arial,sans-serif' }));
    run("INSERT INTO settings(tenant_id,key,value) VALUES(?, 'copy', ?)", t3, JSON.stringify({ searchPlaceholder: "Discover the collection", addToCart: "Reserve", buyNow: "Enquire", priorityBadge: "ATELIER", bestSellers: "Signature Pieces", dealsTitle: "Private Viewing", reviewsTitle: "Client Words" }));
    run("INSERT INTO settings(tenant_id,key,value) VALUES(?, 'commerce', ?)", t3, JSON.stringify({ country: "AE", currency: "AED", symbol: "د.إ", locale: "ar-AE", taxMode: "vat", taxRate: 0.05, freeShipThreshold: 500, shipFee: 25, daysPriority: 1, daysStandard: 3, giftAmounts: [250, 500, 1000], giftMax: 5000 }));
    run("INSERT INTO tenant_gateways(tenant_id,provider_id,is_primary,mode,config,position) VALUES(?, 'tabby', 1, 'sandbox', '{}', 0)", t3);
    run("INSERT INTO tenant_gateways(tenant_id,provider_id,is_primary,mode,config,position) VALUES(?, 'stripe', 0, 'sandbox', '{}', 1)", t3);
    run("INSERT INTO tenant_gateways(tenant_id,provider_id,is_primary,mode,config,position) VALUES(?, 'cod', 0, 'live', '{}', 2)", t3);
    run("INSERT INTO tenant_gateways(tenant_id,provider_id,is_primary,mode,config,position) VALUES(?, 'ship:dhl', 1, 'live', '{}', 0)", t3);
    run("INSERT INTO tenant_gateways(tenant_id,provider_id,is_primary,mode,config,position) VALUES(?, 'notify:log', 1, 'live', '{}', 0)", t3);
    run("INSERT INTO warehouses(tenant_id,name,code,country,region) VALUES(?, 'Velora Atelier', 'DXB1', 'AE', 'Dubai')", t3);
    newUser(t3, "Velora Concierge", SEED.veloraEmail, SEED.veloraPw, "admin");
    console.log("  🏬 Brand store seeded: velora.localhost (AED/UAE, Tabby BNPL)");
    run("INSERT INTO settings(tenant_id,key,value) VALUES(?, 'brand', ?)", t2, JSON.stringify({
      name: "AURUM", wordmark: "AURUM", tagline: "Atelier of quiet luxury — fashion, beauty & home.",
      supportEmail: "concierge@aurum.shop", footerNote: "© {year} AURUM Atelier — white-label storefront on the LUXORA platform.",
      logo: "", accentOverride: null
    }));
    run("INSERT INTO settings(tenant_id,key,value) VALUES(?, 'theme', ?)", t2, JSON.stringify({
      bg: "#F7F3F4", header: "#1A1214", accent: "#B76E79", accentDeep: "#8E4A55", accentSoft: "#F6E3E7",
      ink: "#211A1C", muted: "#7A6E70", line: "#EBE0E2", star: "#B76E79", link: "#8E4A55", linkHover: "#B76E79",
      price: "#211A1C", deal: "#B3261E", success: "#1E7A45", radius: "22px", radiusBtn: "999px",
      fontDisplay: '"Baskerville","Palatino","Book Antiqua",Georgia,serif', fontBody: '"Optima","Avenir Next","Segoe UI",Arial,sans-serif'
    }));
    run("INSERT INTO settings(tenant_id,key,value) VALUES(?, 'copy', ?)", t2, JSON.stringify({
      searchPlaceholder: "Search the atelier", addToCart: "Add to bag", priorityBadge: "CONCIERGE",
      bestSellers: "Maison Favourites", dealsTitle: "Private Sale"
    }));
    run("INSERT INTO settings(tenant_id,key,value) VALUES(?, 'commerce', ?)", t2, JSON.stringify({
      country: "IN", currency: "INR", symbol: "₹", locale: "en-IN",
      taxRate: 0.12, taxMode: "gst", freeShipThreshold: 2500, shipFee: 99,
      daysPriority: 2, daysStandard: 5, perPage: 16, cartMaxQty: 10,
      giftAmounts: [500, 1000, 2500, 5000, 10000], giftMax: 10000
    }));
    /* payment gateways: LUXORA (US) → Stripe primary + PayPal + COD; AURUM (IN) → Razorpay + UPI + COD */
    run("INSERT INTO tenant_gateways(tenant_id,provider_id,is_primary,mode,config,position) VALUES(?, 'stripe', 1, 'sandbox', '{}', 0)", t1);
    run("INSERT INTO tenant_gateways(tenant_id,provider_id,is_primary,mode,config,position) VALUES(?, 'paypal', 0, 'sandbox', '{}', 1)", t1);
    run("INSERT INTO tenant_gateways(tenant_id,provider_id,is_primary,mode,config,position) VALUES(?, 'cod', 0, 'live', '{}', 2)", t1);
    run("INSERT INTO tenant_gateways(tenant_id,provider_id,is_primary,mode,config,position) VALUES(?, 'razorpay', 1, 'sandbox', '{}', 0)", t2);
    run("INSERT INTO tenant_gateways(tenant_id,provider_id,is_primary,mode,config,position) VALUES(?, 'upi', 0, 'live', '{}', 1)", t2);
    run("INSERT INTO tenant_gateways(tenant_id,provider_id,is_primary,mode,config,position) VALUES(?, 'cod', 0, 'live', '{}', 2)", t2);
    /* shipping carriers */
    run("INSERT INTO tenant_gateways(tenant_id,provider_id,is_primary,mode,config,position) VALUES(?, 'ship:house-std', 1, 'live', '{}', 0)", t1);
    run("INSERT INTO tenant_gateways(tenant_id,provider_id,is_primary,mode,config,position) VALUES(?, 'ship:house-exp', 0, 'live', '{}', 1)", t1);
    run("INSERT INTO tenant_gateways(tenant_id,provider_id,is_primary,mode,config,position) VALUES(?, 'ship:delhivery', 1, 'live', '{}', 0)", t2);
    run("INSERT INTO tenant_gateways(tenant_id,provider_id,is_primary,mode,config,position) VALUES(?, 'ship:bluedart', 0, 'live', '{}', 1)", t2);
    /* notifications */
    run("INSERT INTO tenant_gateways(tenant_id,provider_id,is_primary,mode,config,position) VALUES(?, 'notify:log', 1, 'live', '{}', 0)", t1);
    run("INSERT INTO tenant_gateways(tenant_id,provider_id,is_primary,mode,config,position) VALUES(?, 'notify:log', 1, 'live', '{}', 0)", t2);
    console.log(`  🏬 Tenants seeded: luxora (${get("SELECT COUNT(*) c FROM products WHERE tenant_id=?", t1).c} products), aurum (${get("SELECT COUNT(*) c FROM products WHERE tenant_id=?", t2).c} products)`);
  }
  if (get("SELECT COUNT(*) c FROM plans").c === 0) {
    run("INSERT INTO plans(name,price_month,max_products,max_orders_month,position) VALUES('Starter',0,60,100,0)");
    run("INSERT INTO plans(name,price_month,max_products,max_orders_month,position) VALUES('Growth',49,500,2000,1)");
    run("INSERT INTO plans(name,price_month,max_products,max_orders_month,position) VALUES('Enterprise',299,100000,100000,2)");
    const t1 = get("SELECT id FROM tenants WHERE slug='luxora'").id;
    const t2 = get("SELECT id FROM tenants WHERE slug='aurum'").id;
    run("INSERT INTO subscriptions(tenant_id,plan_id,status) VALUES(?,2,'active')", t1);
    run("INSERT INTO subscriptions(tenant_id,plan_id,status) VALUES(?,1,'trialing')", t2);
    const t3row = get("SELECT id FROM tenants WHERE slug='velora'");
    if (t3row) run("INSERT INTO subscriptions(tenant_id,plan_id,status) VALUES(?,3,'active')", t3row.id);
    run("INSERT INTO invoices(tenant_id,number,period_start,period_end,amount,status,paid_at,note) VALUES(?, 'INV-2026-0001', date('now','-1 month'), date('now'), 49, 'paid', datetime('now','-20 days'), 'Growth plan — monthly')", t1);
    run("INSERT INTO invoices(tenant_id,number,period_start,period_end,amount,status,note) VALUES(?, 'INV-2026-0002', date('now'), date('now','+1 month'), 49, 'draft', 'Growth plan — monthly')", t1);
    console.log("  💳 Plans, subscriptions & invoices seeded");
  }
  if (!get("SELECT id FROM platform_admins WHERE email=?", SEED.platformEmail)) newPlatformAdmin("Platform Owner", SEED.platformEmail, SEED.platformPw);
  console.log("  🛰  Platform admin: " + SEED.platformEmail + (process.env.PLATFORM_PASSWORD ? " · password from env" : " · password from seed defaults (override: PLATFORM_PASSWORD)"));
  if (!get("SELECT 1 ok FROM platform_settings WHERE key='demo_passwords'"))
    run("INSERT INTO platform_settings(key,value) VALUES('demo_passwords',?)", JSON.stringify({ list: [SEED.platformPw, SEED.adminPw, SEED.aurumPw, SEED.veloraPw, SEED.demoPw] }));
  const t1 = get("SELECT id FROM tenants WHERE slug='luxora'").id;
  if (!get("SELECT id FROM users WHERE tenant_id=? AND email=?", t1, SEED.demoEmail)) {
    const uid = newUser(t1, "Demo Shopper", SEED.demoEmail, SEED.demoPw, "customer");
    const owner = `t${t1}:u:${uid}`;
    run("INSERT INTO cart_items(owner,product_id,qty) VALUES(?,?,2)", owner, "LX-ELS-001");
    run("INSERT INTO cart_items(owner,product_id,qty) VALUES(?,?,1)", owner, "LX-KIT-001");
    const r = run(`INSERT INTO orders(tenant_id,owner,num,name,address,city,state,zip,ship_option,pay_method,sub,ship_fee,gift_used,tax,total,eta_days,status,created_at)
                   VALUES(?,?,'112-1234567-8901234','Demo Shopper','1219 Second Ave','Seattle','WA','98109','std','card',173.97,0,0,15.44,189.41,2,'delivered',datetime('now','-6 days'))`, t1, owner);
    run("INSERT INTO order_items(order_id,product_id,qty,price) VALUES(?,?,?,?)", Number(r.lastInsertRowid), "LX-CMP-005", 1, 104.90);
    run("INSERT INTO order_items(order_id,product_id,qty,price) VALUES(?,?,?,?)", Number(r.lastInsertRowid), "LX-FAS-001", 1, 69.07);
  }
  if (!get("SELECT id FROM users WHERE tenant_id=? AND email=?", t1, SEED.adminEmail))
    newUser(t1, "Store Admin", SEED.adminEmail, SEED.adminPw, "admin");
  const aurum = get("SELECT id FROM tenants WHERE slug='aurum'");
  if (aurum && !get("SELECT id FROM users WHERE tenant_id=? AND email=?", aurum.id, SEED.aurumEmail))
    newUser(aurum.id, "Aurum Concierge", SEED.aurumEmail, SEED.aurumPw, "admin");
  console.log("  🔑 Store admins: " + SEED.adminEmail + " · " + (aurum ? SEED.aurumEmail : "") + " · " + SEED.veloraEmail + " · passwords from env where set, else seed defaults (rotate in console)");
  if (!get("SELECT 1 ok FROM platform_settings WHERE key='demo_hint'"))
    run("INSERT INTO platform_settings(key,value) VALUES('demo_hint',?)", JSON.stringify({ enabled: process.env.LUXORA_DEMO_HINT !== "0", platformEmail: SEED.platformEmail, storeAdminHint: true }));
  /* upgrade self-heal: ensure universal-model data (serialization, variant groups, compliance, suppliers, i18n, B2B) exists for every tenant, incl. installs that predate these features. idempotent per tenant. */
  for (const tt of all("SELECT id FROM tenants")) { try { seedAdvanced(tt.id); } catch (e) { console.error("advanced backfill", tt.id, e.message); } }
  audit(null, "system", null, "platform", "boot", "system", null, `tenants=${get("SELECT COUNT(*) c FROM tenants").c}`);
}

/* ---------------- audit ---------------- */
function audit(tenantId, actorType, actorId, actorName, action, entity, entityId, meta, ip, traceId) {
  try {
    const scope = tenantId == null ? "p" : String(tenantId);
    const prev = tenantId == null
      ? get("SELECT hash h FROM audit_log WHERE tenant_id IS NULL ORDER BY id DESC LIMIT 1")
      : get("SELECT hash h FROM audit_log WHERE tenant_id=? ORDER BY id DESC LIMIT 1", Number(tenantId));
    const prevHash = (prev && prev.h) || "GENESIS";
    const ipStr = typeof ip === "string" ? ip : (ip && ip.socket && ip.socket.remoteAddress) || "";
    const trace = traceId || (ip && ip.__trace) || null;
    let metaStr;
    if (typeof meta === "string") metaStr = meta;
    else { try { metaStr = JSON.stringify(meta == null ? {} : meta); } catch (e) { metaStr = "{}"; } }
    const payload = { tenant: tenantId, actor: actorName || null, action, entity: entity || null, ref: (entityId == null || entityId === "") ? null : String(entityId), meta: metaStr, ip: ipStr };
    const hash = sec.chainRow(prevHash, payload);
    run("INSERT INTO audit_log(tenant_id,actor_type,actor_id,actor_name,action,entity,entity_id,meta,ip,prev_hash,hash,trace_id) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
      tenantId, actorType, actorId, actorName, action, entity, entityId == null ? null : String(entityId),
      payload.meta, ipStr, prevHash, hash, trace);
  } catch (e) { console.error("audit failed", e.message); }
}
function auditChainVerify(tenantId) {
  const rows = tenantId == null ? all("SELECT * FROM audit_log WHERE tenant_id IS NULL ORDER BY id") : all("SELECT * FROM audit_log WHERE tenant_id=? ORDER BY id", tenantId);
  let prev = "GENESIS";
  for (const row of rows) {
    const payload = { tenant: row.tenant_id, actor: row.actor_name || null, action: row.action, entity: row.entity || null, ref: row.entity_id || null, meta: row.meta, ip: row.ip || "" };
    const want = sec.chainRow(prev, payload);
    if (row.prev_hash !== prev || row.hash !== want) return { ok: false, broken_at: row.id, expected: want, found: row.hash };
    prev = row.hash;
  }
  return { ok: true, checked: rows.length, head: prev };
}

/* ---------------- helpers ---------------- */
function ownerFor(session) {
  const t = session.tenant ? session.tenant.id : 1;
  return session.user_id ? `t${t}:u:${session.user_id}` : `t${t}:s:${session.sid}`;
}
function tenantState(sid, tenantId) {
  let st = get("SELECT * FROM tenant_state WHERE sid=? AND tenant_id=?", sid, tenantId);
  if (!st) { run("INSERT INTO tenant_state(sid,tenant_id) VALUES(?,?)", sid, tenantId); st = { zip: "98109", gift_balance: 0 }; }
  return st;
}
function setTenantState(sid, tenantId, patch) {
  tenantState(sid, tenantId);
  if (patch.zip != null) run("UPDATE tenant_state SET zip=? WHERE sid=? AND tenant_id=?", patch.zip, sid, tenantId);
  if (patch.gift_balance != null) run("UPDATE tenant_state SET gift_balance=? WHERE sid=? AND tenant_id=?", patch.gift_balance, sid, tenantId);
}

bootstrap();

/* seed geo/provider registries AFTER exports are visible (breaks the circular require) */
module.exports = { db, DB_PATH, DEPT_TO_INDUSTRY, exec, run, all, get, newUser, verifyUser, newPlatformAdmin, verifyPlatformAdmin, hashPasswordFor, ownerFor, tenantState, setTenantState, addLink, audit, auditChainVerify, passwordReused, setUserPassword, setKdfVersion, seedTenantCatalog, seedTenantDepartments, seedTenantHome, seedMeta, seedTaxonomy };

try { require("./registry.js").seedRegistries(); } catch (e) { console.error("registry seed failed:", e.message); }
/* registries seeded after exports so the circular require sees the full db module */
