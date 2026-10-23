CREATE TABLE tenants (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  slug TEXT NOT NULL UNIQUE, name TEXT NOT NULL, domain TEXT DEFAULT '',
  status TEXT NOT NULL DEFAULT 'active', created_at TEXT NOT NULL DEFAULT (datetime('now'))
, mode TEXT NOT NULL DEFAULT 'marketplace', industries TEXT DEFAULT '[]', profile TEXT DEFAULT '{}', region TEXT DEFAULT 'global', sso_provider TEXT DEFAULT '', cdn TEXT DEFAULT '', uid TEXT);
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE plans (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL, price_month REAL NOT NULL DEFAULT 0, currency TEXT DEFAULT 'USD',
  max_products INTEGER NOT NULL DEFAULT 100, max_orders_month INTEGER NOT NULL DEFAULT 100,
  features TEXT DEFAULT '{}', position INTEGER DEFAULT 0
, uid TEXT);
CREATE TABLE subscriptions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL REFERENCES tenants(id), plan_id INTEGER NOT NULL REFERENCES plans(id),
  status TEXT NOT NULL DEFAULT 'active', started_at TEXT NOT NULL DEFAULT (datetime('now')),
  renews_at TEXT NOT NULL DEFAULT (datetime('now','+1 month'))
, uid TEXT);
CREATE TABLE invoices (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL REFERENCES tenants(id), number TEXT NOT NULL UNIQUE,
  period_start TEXT, period_end TEXT, amount REAL NOT NULL, currency TEXT DEFAULT 'USD',
  status TEXT NOT NULL DEFAULT 'draft', issued_at TEXT NOT NULL DEFAULT (datetime('now')),
  paid_at TEXT, note TEXT DEFAULT ''
, trace_id TEXT, uid TEXT);
CREATE TABLE audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER, actor_type TEXT NOT NULL DEFAULT 'system',
  actor_id INTEGER, actor_name TEXT, action TEXT NOT NULL,
  entity TEXT, entity_id TEXT, meta TEXT DEFAULT '', ip TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
, prev_hash TEXT, hash TEXT, trace_id TEXT, uid TEXT);
CREATE TABLE platform_admins (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, salt TEXT NOT NULL, hash TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
, kdf_version TEXT DEFAULT 'v1', role TEXT, perms TEXT DEFAULT '{}', uid TEXT);
CREATE TABLE platform_sessions (
  ptid TEXT PRIMARY KEY, admin_id INTEGER REFERENCES platform_admins(id),
  created_at TEXT NOT NULL DEFAULT (datetime('now')), expires_at TEXT NOT NULL
, uid TEXT);
CREATE TABLE tokens (
  token TEXT PRIMARY KEY, tenant_id INTEGER NOT NULL, user_id INTEGER NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')), expires_at TEXT NOT NULL
, uid TEXT);
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL DEFAULT 1,
  name TEXT NOT NULL, email TEXT NOT NULL, salt TEXT NOT NULL, hash TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'customer',
  created_at TEXT NOT NULL DEFAULT (datetime('now')), kyc_status TEXT DEFAULT 'unverified', bnpl_eligible INTEGER DEFAULT 0, loyalty_points INTEGER DEFAULT 0, kdf_version TEXT DEFAULT 'v1', pwd_history TEXT DEFAULT '[]', staff_role TEXT DEFAULT 'owner', perms TEXT DEFAULT '{}', last_login TEXT, disabled INTEGER DEFAULT 0, uid TEXT,
  UNIQUE(tenant_id, email)
);
CREATE TABLE sessions (
  sid TEXT PRIMARY KEY, user_id INTEGER REFERENCES users(id),
  created_at TEXT NOT NULL DEFAULT (datetime('now')), expires_at TEXT NOT NULL
, csrf TEXT, auth_at TEXT, uid TEXT);
CREATE TABLE tenant_state (
  sid TEXT NOT NULL, tenant_id INTEGER NOT NULL, zip TEXT NOT NULL DEFAULT '98109',
  gift_balance REAL NOT NULL DEFAULT 0, coupon TEXT DEFAULT '', uid TEXT,
  PRIMARY KEY (sid, tenant_id)
);
CREATE TABLE products (
  tenant_id INTEGER NOT NULL DEFAULT 1, id TEXT NOT NULL,
  title TEXT NOT NULL, brand TEXT NOT NULL, dept TEXT NOT NULL,
  price REAL NOT NULL, list_price REAL, rating REAL, ratings_count INTEGER,
  emoji TEXT, hue INTEGER, priority INTEGER DEFAULT 0, stock INTEGER DEFAULT 0,
  flags TEXT, keywords TEXT, deal_pct INTEGER DEFAULT 0, position INTEGER DEFAULT 0, moq INTEGER DEFAULT 1, compare_enabled INTEGER DEFAULT 1, gift_wrap INTEGER DEFAULT 1, type TEXT DEFAULT 'physical', node_id INTEGER, lifecycle TEXT DEFAULT 'published', identity TEXT DEFAULT '{}', attrs TEXT DEFAULT '{}', vertical TEXT DEFAULT '{}', media TEXT DEFAULT '[]', seo TEXT DEFAULT '{}', tax_rule TEXT DEFAULT '{}', geo_rules TEXT DEFAULT '[]', pricing_rules TEXT DEFAULT '[]', logistics TEXT DEFAULT '{}', packaging TEXT DEFAULT '[]', docs TEXT DEFAULT '[]', supplier_id INTEGER, uom TEXT DEFAULT '{"unit":"ea"}', tax_profile TEXT DEFAULT '', invoice_profile TEXT DEFAULT '', payment_profiles TEXT DEFAULT '[]', source_universe TEXT, source_kind TEXT DEFAULT 'seed', source_global_id TEXT, deleted_at TEXT, uid TEXT,
  PRIMARY KEY (tenant_id, id)
);
CREATE TABLE product_bullets (
  tenant_id INTEGER NOT NULL DEFAULT 1, product_id TEXT NOT NULL, pos INTEGER NOT NULL, text TEXT NOT NULL, uid TEXT,
  PRIMARY KEY (tenant_id, product_id, pos)
);
CREATE TABLE cart_items (
  owner TEXT NOT NULL, product_id TEXT NOT NULL, qty INTEGER NOT NULL DEFAULT 1, sku_id INTEGER,
  line TEXT NOT NULL DEFAULT '', terms TEXT NOT NULL DEFAULT '{}',
  added_at TEXT NOT NULL DEFAULT (datetime('now')), slot_id INTEGER, store_id INTEGER, gift_wrap INTEGER DEFAULT 0, uid TEXT, PRIMARY KEY (owner, product_id, line)
);
CREATE TABLE saved_items (
  owner TEXT NOT NULL, product_id TEXT NOT NULL, added_at TEXT NOT NULL DEFAULT (datetime('now')), uid TEXT,
  PRIMARY KEY (owner, product_id)
);
CREATE TABLE orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL DEFAULT 1,
  owner TEXT NOT NULL, num TEXT NOT NULL UNIQUE,
  name TEXT, address TEXT, city TEXT, state TEXT, zip TEXT,
  ship_option TEXT, pay_method TEXT,
  sub REAL, ship_fee REAL, gift_used REAL, tax REAL, total REAL,
  eta_days INTEGER DEFAULT 5, status TEXT DEFAULT 'processing',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
, store_id INTEGER, slot_id INTEGER, promise_minutes INTEGER, delivery_kind TEXT DEFAULT 'standard', cancel_reason TEXT, seller_id INTEGER, escrow_ref TEXT, invoice_ref TEXT, gift_wrap INTEGER DEFAULT 0, gift_message TEXT, contexts TEXT DEFAULT '{}', currency TEXT DEFAULT '', fx REAL DEFAULT 1, trace_id TEXT, charges TEXT NOT NULL DEFAULT '[]', deleted_at TEXT, uid TEXT);
CREATE TABLE order_items (
  order_id INTEGER NOT NULL, product_id TEXT NOT NULL, qty INTEGER NOT NULL, price REAL NOT NULL, sku_id INTEGER,
  terms TEXT DEFAULT '{}'
, uid TEXT);
CREATE TABLE reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL DEFAULT 1,
  product_id TEXT NOT NULL, user_id INTEGER, name TEXT NOT NULL,
  rating INTEGER NOT NULL, title TEXT NOT NULL, body TEXT NOT NULL,
  verified INTEGER DEFAULT 0, created_at TEXT NOT NULL DEFAULT (datetime('now'))
, votes_helpful INTEGER DEFAULT 0, votes_total INTEGER DEFAULT 0, state TEXT DEFAULT 'approved', media TEXT DEFAULT '[]', deleted_at TEXT, uid TEXT);
CREATE TABLE view_history (
  owner TEXT NOT NULL, product_id TEXT NOT NULL, seen_at TEXT NOT NULL DEFAULT (datetime('now')), uid TEXT,
  PRIMARY KEY (owner, product_id)
);
CREATE TABLE settings (
  tenant_id INTEGER NOT NULL DEFAULT 1, key TEXT NOT NULL, value TEXT NOT NULL, uid TEXT,
  PRIMARY KEY (tenant_id, key)
);
CREATE TABLE departments (
  tenant_id INTEGER NOT NULL DEFAULT 1, key TEXT NOT NULL, label TEXT NOT NULL,
  icon TEXT DEFAULT '🏷️', active INTEGER NOT NULL DEFAULT 1, position INTEGER NOT NULL DEFAULT 0, deleted_at TEXT, uid TEXT,
  PRIMARY KEY (tenant_id, key)
);
CREATE TABLE brands (
  tenant_id INTEGER NOT NULL DEFAULT 1, key TEXT NOT NULL, label TEXT NOT NULL,
  icon TEXT, logo TEXT, story TEXT, country TEXT, active INTEGER NOT NULL DEFAULT 1, position INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (tenant_id, key)
);
CREATE TABLE home_banners (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL DEFAULT 1,
  title TEXT NOT NULL, subtitle TEXT, cta TEXT, hue INTEGER DEFAULT 210, dept TEXT DEFAULT '',
  active INTEGER NOT NULL DEFAULT 1, position INTEGER NOT NULL DEFAULT 0
, deleted_at TEXT, uid TEXT);
CREATE TABLE home_cards (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL DEFAULT 1,
  title TEXT NOT NULL, dept TEXT NOT NULL, tiles TEXT DEFAULT '[]',
  active INTEGER NOT NULL DEFAULT 1, position INTEGER NOT NULL DEFAULT 0
, deleted_at TEXT, uid TEXT);
CREATE TABLE tenant_gateways (
  tenant_id INTEGER NOT NULL, provider_id TEXT NOT NULL,
  enabled INTEGER NOT NULL DEFAULT 1, is_primary INTEGER NOT NULL DEFAULT 0,
  mode TEXT NOT NULL DEFAULT 'sandbox', config TEXT DEFAULT '{}', position INTEGER DEFAULT 0, uid TEXT,
  PRIMARY KEY (tenant_id, provider_id)
);
CREATE TABLE payments (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  kind TEXT NOT NULL DEFAULT 'order', order_id INTEGER, invoice_id INTEGER,
  gateway TEXT NOT NULL, method TEXT, amount REAL NOT NULL, currency TEXT,
  fee REAL DEFAULT 0, status TEXT NOT NULL DEFAULT 'initiated',
  txn_ref TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now'))
, provider_payment_id TEXT, live INTEGER DEFAULT 0, uid TEXT);
CREATE TABLE custom_providers (
  id INTEGER PRIMARY KEY AUTOINCREMENT, scope TEXT NOT NULL DEFAULT 'platform',
  tenant_id INTEGER, kind TEXT NOT NULL, manifest TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE TABLE taxonomy (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  parent_id INTEGER, level TEXT NOT NULL, key TEXT NOT NULL, name TEXT NOT NULL,
  icon TEXT DEFAULT '', attrs TEXT DEFAULT '{}', active INTEGER DEFAULT 1, position INTEGER DEFAULT 0
, deleted_at TEXT, node_uid TEXT);
CREATE TABLE attribute_defs (
  tenant_id INTEGER NOT NULL, key TEXT NOT NULL, label TEXT NOT NULL, grp TEXT DEFAULT 'General',
  type TEXT DEFAULT 'text', unit TEXT DEFAULT '', options TEXT DEFAULT '[]', validation TEXT DEFAULT '{}',
  industry TEXT DEFAULT '', position INTEGER DEFAULT 0, category TEXT DEFAULT '', deleted_at TEXT, node_uid TEXT, PRIMARY KEY (tenant_id, key)
);
CREATE TABLE skus (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, product_id TEXT NOT NULL,
  code TEXT NOT NULL, name TEXT DEFAULT '', identity TEXT DEFAULT '{}', variant TEXT DEFAULT '{}',
  price REAL, mrp REAL, stock INTEGER DEFAULT 0, active INTEGER DEFAULT 1
, group_id INTEGER, uid TEXT);
CREATE TABLE warehouses (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, name TEXT NOT NULL,
  code TEXT, country TEXT DEFAULT 'US', region TEXT DEFAULT '', active INTEGER DEFAULT 1
, kind TEXT DEFAULT 'warehouse', lat REAL, lng REAL, service_radius_km REAL, promise_minutes INTEGER, pincode TEXT, city TEXT, deleted_at TEXT, uid TEXT);
CREATE TABLE inventory (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, sku_id INTEGER NOT NULL,
  warehouse_id INTEGER, qty INTEGER DEFAULT 0, reserved INTEGER DEFAULT 0,
  lot TEXT DEFAULT '', batch TEXT DEFAULT '', expiry TEXT DEFAULT '', serial TEXT DEFAULT '[]'
, uid TEXT);
CREATE TABLE relationships (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  from_id TEXT NOT NULL, to_id TEXT NOT NULL, type TEXT NOT NULL
);
CREATE UNIQUE INDEX ux_relationships_edge ON relationships(tenant_id, from_id, to_id, type);
CREATE TABLE promotions (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, name TEXT NOT NULL,
  type TEXT NOT NULL, value REAL DEFAULT 0, rules TEXT DEFAULT '{}', scope TEXT DEFAULT '{}',
  starts TEXT, ends TEXT, status TEXT DEFAULT 'active', code TEXT DEFAULT ''
, deleted_at TEXT);
CREATE TABLE sellers (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, name TEXT NOT NULL,
  role TEXT DEFAULT 'retailer', email TEXT, status TEXT DEFAULT 'active', commission_pct REAL DEFAULT 5
, onboarding_status TEXT DEFAULT 'pending', verified INTEGER DEFAULT 0, rating REAL DEFAULT 0, tier TEXT DEFAULT 'standard', health_score REAL DEFAULT 0, deleted_at TEXT, owner TEXT);
CREATE TABLE rfqs (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT NOT NULL UNIQUE,
  product_id TEXT, buyer_name TEXT, buyer_email TEXT, qty REAL, target_price REAL, currency TEXT,
  status TEXT DEFAULT 'open', quotes TEXT DEFAULT '[]', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE shipments (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, order_id INTEGER,
  tracking_ref TEXT UNIQUE, carrier TEXT, warehouse_id INTEGER,
  status TEXT NOT NULL DEFAULT 'pending', sla_due TEXT, dispatched_at TEXT, delivered_at TEXT,
  meta TEXT DEFAULT '{}', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_shipments_order ON shipments(order_id);
CREATE INDEX ix_shipments_status ON shipments(status, tenant_id);
CREATE TABLE shipment_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT, shipment_id INTEGER NOT NULL, tenant_id INTEGER NOT NULL,
  status TEXT NOT NULL, location TEXT, note TEXT, ref TEXT, actor TEXT,
  at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_ship_events_ship ON shipment_events(shipment_id);
CREATE TABLE returns (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT NOT NULL UNIQUE,
  order_id INTEGER, product_id TEXT, qty INTEGER DEFAULT 1, reason TEXT, status TEXT DEFAULT 'requested',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
, deleted_at TEXT);
CREATE TABLE settlements (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT NOT NULL UNIQUE,
  seller_id INTEGER, order_id INTEGER, gross REAL, commission REAL, net REAL,
  status TEXT DEFAULT 'pending', period TEXT
);
CREATE TABLE meta_lists (
  name TEXT PRIMARY KEY, label TEXT, items TEXT NOT NULL, seeded_from TEXT
, edited INTEGER DEFAULT 0, uid TEXT);
CREATE TABLE countries (
  code TEXT PRIMARY KEY, name TEXT NOT NULL, position INTEGER DEFAULT 0, active INTEGER DEFAULT 1
, uid TEXT);
CREATE TABLE currencies (
  code TEXT PRIMARY KEY, name TEXT NOT NULL, symbol TEXT NOT NULL, decimals INTEGER NOT NULL DEFAULT 2,
  usd REAL NOT NULL DEFAULT 1, position INTEGER DEFAULT 0, active INTEGER DEFAULT 1, class TEXT, settleable INTEGER DEFAULT 1
, uid TEXT);
CREATE TABLE messages (
  lang TEXT NOT NULL, key TEXT NOT NULL, text TEXT NOT NULL, PRIMARY KEY (lang, key)
);
CREATE TABLE tax_modes (
  key TEXT PRIMARY KEY, label TEXT NOT NULL, description TEXT, fields TEXT DEFAULT '[]', position INTEGER DEFAULT 0
, uid TEXT);
CREATE TABLE tax_rules (
  country TEXT PRIMARY KEY REFERENCES countries(code),
  mode TEXT NOT NULL DEFAULT 'manual',
  standard REAL NOT NULL DEFAULT 0,
  reduced REAL, digital REAL, zero REAL, note TEXT
);
CREATE TABLE provider_defs (
  id TEXT NOT NULL, kind TEXT NOT NULL, name TEXT NOT NULL, emoji TEXT, description TEXT,
  methods TEXT DEFAULT '[]', fee_pct REAL DEFAULT 0, fee_fixed REAL DEFAULT 0, fields TEXT DEFAULT '[]',
  base_fee REAL DEFAULT 0, eta_min INTEGER, eta_max INTEGER, position INTEGER DEFAULT 0,
  enabled INTEGER DEFAULT 1, spec TEXT DEFAULT '{}', global INTEGER DEFAULT 0, uid TEXT, PRIMARY KEY (id, kind)
);
CREATE TABLE provider_availability (
  provider_id TEXT NOT NULL, country_code TEXT NOT NULL REFERENCES countries(code), uid TEXT,
  PRIMARY KEY (provider_id, country_code)
);
CREATE TABLE subdivisions (
  code TEXT PRIMARY KEY,              /* ISO 3166-2, globally unique: the master key (US-CA, IN-MH) */
  country_code TEXT NOT NULL REFERENCES countries(code),
  name TEXT NOT NULL,                 /* the operator-facing label (California, Maharashtra) */
  level TEXT,                         /* what this level is called: state / province / county / prefecture / emirate / region / territory / district */
  parent_id INTEGER,                  /* a finer division under another division; NULL = directly under the country */
  position INTEGER DEFAULT 0,
  active INTEGER DEFAULT 1
);
CREATE INDEX ix_subdivisions_country ON subdivisions(country_code, active);
CREATE TABLE fx_rates (
  id INTEGER PRIMARY KEY AUTOINCREMENT, currency TEXT NOT NULL, usd REAL NOT NULL,
  source TEXT DEFAULT 'manual', note TEXT DEFAULT '', created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE TABLE platform_settings (
  key TEXT PRIMARY KEY, value TEXT NOT NULL
, uid TEXT);
CREATE TABLE modules (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, category TEXT, summary TEXT,
  price_type TEXT DEFAULT 'one_time', price REAL DEFAULT 0, currency TEXT DEFAULT 'USD',
  version TEXT DEFAULT '1.0', vendor TEXT DEFAULT 'LUXORA', manifest TEXT DEFAULT '{}',
  status TEXT DEFAULT 'active', position INTEGER DEFAULT 0
, uid TEXT);
CREATE TABLE tenant_modules (
  tenant_id INTEGER NOT NULL, module_id TEXT NOT NULL, status TEXT DEFAULT 'installed',
  config TEXT DEFAULT '{}', installed_at TEXT NOT NULL DEFAULT (datetime('now')), installed_by TEXT DEFAULT '', uid TEXT,
  PRIMARY KEY (tenant_id, module_id)
);
CREATE TABLE wallets (
  tenant_id INTEGER NOT NULL, owner TEXT NOT NULL, balance REAL NOT NULL DEFAULT 0,
  updated_at TEXT NOT NULL DEFAULT (datetime('now')), uid TEXT, PRIMARY KEY (tenant_id, owner)
);
CREATE TABLE links (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER,
  type TEXT NOT NULL, from_entity TEXT NOT NULL, from_uid TEXT NOT NULL,
  to_entity TEXT NOT NULL, to_uid TEXT NOT NULL, meta TEXT DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE TABLE context_types (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  grp TEXT NOT NULL, key TEXT NOT NULL, label TEXT NOT NULL, type TEXT DEFAULT 'context',
  fields TEXT DEFAULT '[]', position INTEGER DEFAULT 0, uid TEXT, UNIQUE(grp, key)
);
CREATE TABLE entity_defs (
  key TEXT NOT NULL, scope TEXT NOT NULL DEFAULT 'tenant', tenant_id INTEGER NOT NULL DEFAULT 0,
  def TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT (datetime('now')), uid TEXT,
  PRIMARY KEY (key, scope, tenant_id)
);
CREATE TABLE entity_data (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER, entity TEXT NOT NULL,
  data TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE TABLE entity_types (
  id INTEGER PRIMARY KEY AUTOINCREMENT, entity TEXT NOT NULL, type_key TEXT NOT NULL,
  label TEXT NOT NULL, icon TEXT DEFAULT '📝', fields TEXT NOT NULL DEFAULT '[]',
  config TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE (entity, type_key)
);
CREATE INDEX ix_etype_entity ON entity_types(entity);
CREATE TABLE entity_attributes (
  id INTEGER PRIMARY KEY AUTOINCREMENT, attribute_key TEXT NOT NULL,
  entity TEXT NOT NULL, position INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE (entity, attribute_key)
);
CREATE INDEX ix_eattr_entity ON entity_attributes(entity, position);
CREATE TABLE tenant_entities (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, entity TEXT NOT NULL,
  enabled INTEGER NOT NULL DEFAULT 1, requirement TEXT NOT NULL DEFAULT 'optional',
  custom_name TEXT, config TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE (tenant_id, entity)
);
CREATE INDEX ix_tent_tenant ON tenant_entities(tenant_id, enabled);
CREATE TABLE entity_field_config (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, entity TEXT NOT NULL,
  field_key TEXT NOT NULL, required INTEGER NOT NULL DEFAULT 0, hidden INTEGER NOT NULL DEFAULT 0,
  config TEXT NOT NULL DEFAULT '{}', updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE (tenant_id, entity, field_key)
);
CREATE TABLE serialized_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  product_id TEXT NOT NULL, sku_id INTEGER, warehouse_id INTEGER,
  serial TEXT NOT NULL, imei TEXT, rfid TEXT, asset_tag TEXT,
  batch TEXT DEFAULT '', lot TEXT DEFAULT '', expiry TEXT,
  status TEXT NOT NULL DEFAULT 'in_stock', condition TEXT DEFAULT 'new',
  customer_id INTEGER, order_id INTEGER,
  purchase_date TEXT, warranty_end TEXT, meta TEXT DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
, deleted_at TEXT, uid TEXT);
CREATE TABLE variant_groups (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  product_id TEXT NOT NULL, name TEXT NOT NULL, axis TEXT DEFAULT 'General',
  attr_key TEXT DEFAULT '', position INTEGER DEFAULT 0, active INTEGER DEFAULT 1
, deleted_at TEXT, uid TEXT);
CREATE TABLE compliance_records (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  scope TEXT NOT NULL DEFAULT 'product', ref_id TEXT NOT NULL DEFAULT '',
  kind TEXT NOT NULL DEFAULT 'certificate', code TEXT DEFAULT '', issuer TEXT DEFAULT '',
  jurisdiction TEXT DEFAULT '', status TEXT NOT NULL DEFAULT 'valid',
  valid_from TEXT, valid_to TEXT, doc_media TEXT DEFAULT '', notes TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
, deleted_at TEXT, uid TEXT);
CREATE TABLE compliance_controls (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER,                        /* NULL = platform control template */
  regulation TEXT NOT NULL,                 /* gdpr · pci-dss · … (registry key) */
  control_id TEXT NOT NULL,                 /* the regulation's own control number */
  name TEXT NOT NULL,
  evidence TEXT DEFAULT '',                 /* what proves it (engine + artifact) */
  status TEXT NOT NULL DEFAULT 'pending_evidence',
  updated_at TEXT,
  UNIQUE(tenant_id, regulation, control_id)
);
CREATE INDEX ix_compliance_controls_reg ON compliance_controls(regulation, control_id);
CREATE TABLE compliance_evidence (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  control_id INTEGER NOT NULL,
  tenant_id INTEGER,
  note TEXT NOT NULL,
  provided_by TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE consents (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  subject TEXT NOT NULL,                    /* the data subject's identifier (email) */
  purpose TEXT NOT NULL,                    /* registry key: privacyPurposes */
  status TEXT NOT NULL DEFAULT 'granted',   /* granted · withdrawn · denied */
  lawful_basis TEXT DEFAULT 'consent',
  source TEXT DEFAULT 'console',            /* console · checkout · signup · api */
  ip TEXT DEFAULT '',
  granted_at TEXT NOT NULL DEFAULT (datetime('now')),
  withdrawn_at TEXT,
  updated_at TEXT,
  UNIQUE(tenant_id, subject, purpose)
);
CREATE INDEX ix_consents_subject ON consents(tenant_id, subject, status);
CREATE TABLE privacy_requests (
  id TEXT PRIMARY KEY,                      /* DSR-XXXX */
  tenant_id INTEGER NOT NULL,
  subject TEXT NOT NULL,
  kind TEXT NOT NULL,                       /* access · erasure · portability · rectification · objection */
  status TEXT NOT NULL DEFAULT 'received',
  due_at TEXT,
  fulfilled_at TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT
);
CREATE TABLE privacy_request_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  request_id TEXT NOT NULL,
  from_state TEXT,
  to_state TEXT NOT NULL,
  actor TEXT DEFAULT '',
  detail TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE erasure_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  subject TEXT NOT NULL,
  removed TEXT NOT NULL DEFAULT '[]',       /* JSON: {table: rows} */
  executed_by TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE tenancy_nodes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  kind TEXT NOT NULL,                       /* organization · business_unit · brand · store · channel · … */
  parent_id INTEGER,                        /* NULL = the tenant root, which is created once and immortal */
  slug TEXT NOT NULL,
  name TEXT NOT NULL,
  path TEXT NOT NULL,                       /* root.child.grandchild — UNIQUE within a tenant */
  status TEXT NOT NULL DEFAULT 'active',    /* active · suspended (a suspended node blocks creates beneath it) */
  profile TEXT DEFAULT '{}',                /* free-form JSON: addresses, contacts, legal entity facts */
  config TEXT DEFAULT '{}',                 /* inline config; tenancy_config rows are the typed overrides */
  uid TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE(tenant_id, path)
);
CREATE INDEX ix_tenancy_parent ON tenancy_nodes(tenant_id, parent_id);
CREATE INDEX ix_tenancy_kind ON tenancy_nodes(tenant_id, kind);
CREATE TABLE tenancy_config (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  node_id INTEGER NOT NULL,
  key TEXT NOT NULL,
  value TEXT DEFAULT '{}',
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE(tenant_id, node_id, key)
);
CREATE TABLE suppliers (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  name TEXT NOT NULL, party_role TEXT DEFAULT 'manufacturer', tax_id TEXT DEFAULT '',
  country TEXT DEFAULT 'US', region TEXT DEFAULT '', address TEXT DEFAULT '',
  email TEXT DEFAULT '', phone TEXT DEFAULT '', lead_time_days INTEGER DEFAULT 7,
  moq INTEGER DEFAULT 1, currency TEXT DEFAULT 'USD', payment_terms TEXT DEFAULT 'net30',
  on_time_pct REAL DEFAULT 0, status TEXT DEFAULT 'active',
  certifications TEXT DEFAULT '[]', price_list TEXT DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
, deleted_at TEXT, uid TEXT);
CREATE TABLE localizations (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  entity TEXT NOT NULL DEFAULT 'product', ref_id TEXT NOT NULL, locale TEXT NOT NULL,
  name TEXT DEFAULT '', description TEXT DEFAULT '', bullets TEXT DEFAULT '[]',
  attrs TEXT DEFAULT '{}', active INTEGER DEFAULT 1, deleted_at TEXT, uid TEXT,
  UNIQUE (tenant_id, entity, ref_id, locale)
);
CREATE TABLE product_suppliers (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  product_id TEXT NOT NULL, supplier_id INTEGER NOT NULL, supplier_sku TEXT DEFAULT '',
  price REAL, lead_days INTEGER DEFAULT 7, moq INTEGER DEFAULT 1,
  is_primary INTEGER DEFAULT 0, status TEXT DEFAULT 'active', deleted_at TEXT, uid TEXT,
  UNIQUE (tenant_id, product_id, supplier_id)
);
CREATE TABLE contracts (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT NOT NULL,
  buyer_name TEXT NOT NULL, buyer_email TEXT NOT NULL, buyer_org TEXT DEFAULT '',
  supplier_id INTEGER, product_ids TEXT DEFAULT '[]', currency TEXT DEFAULT 'USD',
  pricing TEXT DEFAULT '{}', min_qty INTEGER DEFAULT 1, incoterms TEXT DEFAULT 'EXW',
  payment_terms TEXT DEFAULT 'net30', valid_from TEXT, valid_to TEXT,
  status TEXT NOT NULL DEFAULT 'draft', notes TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now')), deleted_at TEXT, uid TEXT,
  UNIQUE (tenant_id, ref)
);
CREATE TABLE tenders (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT NOT NULL,
  title TEXT NOT NULL, buyer_org TEXT DEFAULT '', buyer_email TEXT DEFAULT '', description TEXT DEFAULT '',
  currency TEXT DEFAULT 'USD', budget REAL DEFAULT 0, open_at TEXT, close_at TEXT,
  status TEXT NOT NULL DEFAULT 'open', awarded_seller_id INTEGER, awarded_contract_id INTEGER,
  items TEXT DEFAULT '[]', bids TEXT DEFAULT '[]',
  created_at TEXT NOT NULL DEFAULT (datetime('now')), deleted_at TEXT, uid TEXT,
  UNIQUE (tenant_id, ref)
);
CREATE UNIQUE INDEX ix_serial_tenant ON serialized_items(tenant_id, serial);
CREATE TABLE ai_usage (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  capability TEXT NOT NULL, provider TEXT NOT NULL, model TEXT DEFAULT '',
  units INTEGER NOT NULL DEFAULT 1, cost REAL NOT NULL DEFAULT 0, currency TEXT DEFAULT 'USD',
  tier TEXT DEFAULT 'free', status TEXT DEFAULT 'ok', actor TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE TABLE ai_tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  capability TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'queued',
  params TEXT DEFAULT '{}', result TEXT, cost REAL DEFAULT 0,
  actor TEXT DEFAULT '', created_at TEXT NOT NULL DEFAULT (datetime('now')), updated_at TEXT
, uid TEXT);
CREATE TABLE invoice_lines (
  id INTEGER PRIMARY KEY AUTOINCREMENT, invoice_id INTEGER NOT NULL, tenant_id INTEGER NOT NULL,
  kind TEXT NOT NULL DEFAULT 'plan', description TEXT NOT NULL, qty REAL DEFAULT 1,
  unit_amount REAL DEFAULT 0, amount REAL DEFAULT 0, tax REAL DEFAULT 0, tax_class TEXT DEFAULT 'standard',
  ref TEXT DEFAULT '', created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE TABLE usage_records (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, kind TEXT NOT NULL,
  ref TEXT DEFAULT '', description TEXT NOT NULL DEFAULT '', qty REAL DEFAULT 1, unit_amount REAL DEFAULT 0,
  amount REAL DEFAULT 0, currency TEXT DEFAULT 'USD', period TEXT NOT NULL DEFAULT '', billed INTEGER DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE TABLE payment_attempts (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, payment_id INTEGER NOT NULL,
  gateway TEXT, attempt INTEGER DEFAULT 1, status TEXT NOT NULL DEFAULT 'pending',
  txn_ref TEXT, error TEXT, at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_pay_attempts ON payment_attempts(payment_id);
CREATE TABLE disputes (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, payment_id INTEGER, order_id INTEGER,
  ref TEXT NOT NULL UNIQUE, reason TEXT, amount REAL, currency TEXT,
  state TEXT NOT NULL DEFAULT 'opened', resolution TEXT, closed_at TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_disputes_state ON disputes(state, tenant_id);
CREATE TABLE payouts (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  seller_id INTEGER, kind TEXT NOT NULL DEFAULT 'seller', ref TEXT, period TEXT,
  gross REAL NOT NULL DEFAULT 0, fee REAL NOT NULL DEFAULT 0, net REAL NOT NULL DEFAULT 0,
  currency TEXT DEFAULT 'USD', status TEXT NOT NULL DEFAULT 'open',
  disbursed_at TEXT, note TEXT DEFAULT '', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE payout_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT, payout_id INTEGER NOT NULL, tenant_id INTEGER NOT NULL,
  ref TEXT NOT NULL, kind TEXT, description TEXT, amount REAL, currency TEXT, settled INTEGER DEFAULT 0
);
CREATE TABLE recon_batches (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, period TEXT, gateway TEXT,
  source TEXT, lines INTEGER DEFAULT 0, matched INTEGER DEFAULT 0, unmatched INTEGER DEFAULT 0,
  total REAL DEFAULT 0, status TEXT NOT NULL DEFAULT 'open', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE recon_lines (
  id INTEGER PRIMARY KEY AUTOINCREMENT, batch_id INTEGER NOT NULL, tenant_id INTEGER NOT NULL,
  ref TEXT, source TEXT, amount REAL, status TEXT NOT NULL DEFAULT 'matched', note TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE ads (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, seller_id INTEGER,
  name TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'active', bid_model TEXT NOT NULL DEFAULT 'cpc',
  bid_amount REAL NOT NULL DEFAULT 0, budget REAL DEFAULT 0, spent REAL DEFAULT 0,
  target TEXT DEFAULT '{}', start_at TEXT, end_at TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_ads ON ads(tenant_id, status, bid_model);
CREATE TABLE ad_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ad_id INTEGER NOT NULL,
  kind TEXT NOT NULL DEFAULT 'impression', ref TEXT, cost REAL DEFAULT 0,
  at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_ad_events ON ad_events(ad_id, kind);
CREATE TABLE attribution (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  order_id INTEGER, ad_id INTEGER, seller_id INTEGER, model TEXT DEFAULT 'last_click',
  revenue REAL DEFAULT 0, commission REAL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE seller_metrics (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, seller_id INTEGER,
  period TEXT, orders INTEGER DEFAULT 0, revenue REAL DEFAULT 0, take_rate REAL DEFAULT 0,
  commission REAL DEFAULT 0, ads_spend REAL DEFAULT 0, ad_roi REAL DEFAULT 0,
  note TEXT DEFAULT '{}', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE review_replies (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, review_id INTEGER NOT NULL,
  author TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'seller', body TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE INDEX ix_review_replies ON review_replies(review_id);
CREATE TABLE ugc_votes (
  entity TEXT NOT NULL, entity_id INTEGER NOT NULL, tenant_id INTEGER NOT NULL,
  owner TEXT NOT NULL, dir TEXT NOT NULL DEFAULT 'up', at TEXT NOT NULL DEFAULT (datetime('now')), uid TEXT,
  PRIMARY KEY (entity, entity_id, owner)
);
CREATE TABLE qna_questions (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, product_id TEXT NOT NULL,
  owner TEXT, name TEXT NOT NULL, body TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'approved',
  votes_helpful INTEGER DEFAULT 0, votes_total INTEGER DEFAULT 0, answered_at TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE INDEX ix_qna_q ON qna_questions(tenant_id, product_id, state);
CREATE TABLE qna_answers (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, question_id INTEGER NOT NULL,
  owner TEXT, name TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'customer', body TEXT NOT NULL,
  state TEXT NOT NULL DEFAULT 'approved', votes_helpful INTEGER DEFAULT 0, votes_total INTEGER DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE INDEX ix_qna_a ON qna_answers(question_id, state);
CREATE TABLE tickets (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT NOT NULL UNIQUE,
  subject TEXT NOT NULL, reason TEXT NOT NULL DEFAULT 'other', priority TEXT NOT NULL DEFAULT 'normal',
  status TEXT NOT NULL DEFAULT 'new', assignee TEXT, owner TEXT, owner_name TEXT NOT NULL, owner_email TEXT,
  order_ref TEXT DEFAULT '', product_id TEXT DEFAULT '', body TEXT NOT NULL, channel TEXT DEFAULT 'email',
  sla_response TEXT, sla_resolution TEXT, first_response_at TEXT, resolved_at TEXT,
  csat INTEGER, csat_comment TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE INDEX ix_tickets ON tickets(tenant_id, status, priority);
CREATE TABLE agent_availability (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, agent_id TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'offline', updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE (tenant_id, agent_id)
);
CREATE TABLE ticket_notes (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ticket_id INTEGER NOT NULL,
  role TEXT NOT NULL DEFAULT 'agent', author TEXT NOT NULL, body TEXT NOT NULL, visibility TEXT NOT NULL DEFAULT 'public',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE INDEX ix_ticket_notes ON ticket_notes(ticket_id);
CREATE TABLE addresses (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, owner TEXT NOT NULL,
  label TEXT NOT NULL DEFAULT 'Home', name TEXT NOT NULL, address TEXT NOT NULL, city TEXT NOT NULL,
  state TEXT DEFAULT '', zip TEXT DEFAULT '', country TEXT DEFAULT '', phone TEXT DEFAULT '',
  is_default INTEGER DEFAULT 0, created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE INDEX ix_addresses ON addresses(tenant_id, owner);
CREATE TABLE recurring_schedules (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, owner TEXT NOT NULL,
  product_id TEXT NOT NULL, sku_id INTEGER, qty INTEGER DEFAULT 1, frequency_days INTEGER NOT NULL DEFAULT 30,
  discount_pct REAL DEFAULT 0, next_ship_at TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'active',
  cycles_completed INTEGER DEFAULT 0, created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE INDEX ix_rec_sched ON recurring_schedules(tenant_id, owner, status);
CREATE TABLE recurring_cycles (
  id INTEGER PRIMARY KEY AUTOINCREMENT, schedule_id INTEGER NOT NULL, tenant_id INTEGER NOT NULL,
  order_ref TEXT DEFAULT '', status TEXT NOT NULL DEFAULT 'scheduled', at TEXT NOT NULL
, uid TEXT);
CREATE INDEX ix_rec_cycles ON recurring_cycles(schedule_id, at, status);
CREATE TABLE memberships (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, owner TEXT NOT NULL,
  tier TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'active',
  started_at TEXT NOT NULL DEFAULT (datetime('now')), renews_at TEXT, cancelled_at TEXT
, uid TEXT);
CREATE INDEX ix_memberships ON memberships(tenant_id, owner, status);
CREATE TABLE risk_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  owner TEXT DEFAULT '', ip TEXT DEFAULT '', card_fp TEXT DEFAULT '', addr_fp TEXT DEFAULT '',
  amount REAL DEFAULT 0, score INTEGER DEFAULT 0, action TEXT NOT NULL DEFAULT 'approve',
  signals TEXT DEFAULT '{}', ref TEXT DEFAULT '',
  resolved INTEGER DEFAULT 0, resolution TEXT DEFAULT '', note TEXT DEFAULT '', resolved_at TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE INDEX ix_risk_events ON risk_events(tenant_id, action, resolved, created_at);
CREATE INDEX ix_risk_velocity ON risk_events(tenant_id, owner, created_at);
CREATE TABLE risk_blocklist (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  kind TEXT NOT NULL, value TEXT NOT NULL, note TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now')), uid TEXT,
  UNIQUE (tenant_id, kind, value)
);
CREATE TABLE experiments (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  key TEXT NOT NULL, name TEXT NOT NULL, variants TEXT NOT NULL DEFAULT '[]',
  status TEXT NOT NULL DEFAULT 'draft', metric TEXT DEFAULT 'conversion',
  started_at TEXT, ended_at TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')), uid TEXT,
  UNIQUE (tenant_id, key)
);
CREATE TABLE exp_assignments (
  id INTEGER PRIMARY KEY AUTOINCREMENT, experiment_id INTEGER NOT NULL, tenant_id INTEGER NOT NULL,
  subject TEXT NOT NULL, variant TEXT NOT NULL, at TEXT NOT NULL DEFAULT (datetime('now')), uid TEXT,
  UNIQUE (experiment_id, subject)
);
CREATE INDEX ix_exp_assign ON exp_assignments(experiment_id, variant);
CREATE TABLE exp_conversions (
  id INTEGER PRIMARY KEY AUTOINCREMENT, experiment_id INTEGER NOT NULL, tenant_id INTEGER NOT NULL,
  variant TEXT NOT NULL, subject TEXT NOT NULL, value REAL DEFAULT 1,
  at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE INDEX ix_exp_conv ON exp_conversions(experiment_id, variant);
CREATE TABLE replenishments (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  sku_id INTEGER NOT NULL, product_id TEXT NOT NULL,
  on_hand INTEGER DEFAULT 0, reserved INTEGER DEFAULT 0, available INTEGER DEFAULT 0,
  avg_daily REAL DEFAULT 0, forecast_30d INTEGER DEFAULT 0, trend REAL DEFAULT 0,
  lead_days INTEGER DEFAULT 7, safety_stock INTEGER DEFAULT 0, reorder_point INTEGER DEFAULT 0,
  reorder_qty INTEGER DEFAULT 0, min_qty INTEGER DEFAULT 1, max_qty INTEGER DEFAULT 0,
  supplier_id INTEGER, supplier_name TEXT DEFAULT '', unit_cost REAL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'suggested', priority TEXT DEFAULT 'normal',
  po_ref TEXT DEFAULT '', po_status TEXT DEFAULT '',
  generated_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT, closed_at TEXT,
  UNIQUE (tenant_id, sku_id)
);
CREATE INDEX ix_replen ON replenishments(tenant_id, status, priority);
CREATE INDEX ix_replen_sku ON replenishments(tenant_id, sku_id);
CREATE TABLE credit_notes (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, number TEXT NOT NULL UNIQUE,
  invoice_id INTEGER, amount REAL NOT NULL, currency TEXT DEFAULT 'USD', reason TEXT DEFAULT '',
  status TEXT NOT NULL DEFAULT 'issued', to_wallet INTEGER DEFAULT 0, created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE TABLE billing_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, invoice_id INTEGER,
  kind TEXT NOT NULL, detail TEXT DEFAULT '{}', created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE INDEX ix_invoice_lines ON invoice_lines(invoice_id);
CREATE INDEX ix_usage_open ON usage_records(tenant_id, billed);
CREATE TABLE webhooks (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, url TEXT NOT NULL,
  secret TEXT DEFAULT '', events TEXT DEFAULT '["*"]', active INTEGER DEFAULT 1,
  description TEXT DEFAULT '', created_at TEXT NOT NULL DEFAULT (datetime('now')), updated_at TEXT
, uid TEXT);
CREATE TABLE webhook_deliveries (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, webhook_id INTEGER,
  event TEXT NOT NULL, subject_uid TEXT, payload TEXT DEFAULT '{}', status TEXT NOT NULL DEFAULT 'queued',
  attempts INTEGER DEFAULT 0, response TEXT DEFAULT '', next_retry_at TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE TABLE entity_meta (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  entity TEXT NOT NULL, ref_uid TEXT NOT NULL, tags TEXT DEFAULT '[]', meta TEXT DEFAULT '{}', notes TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now')), updated_at TEXT, uid TEXT,
  UNIQUE (tenant_id, entity, ref_uid)
);
CREATE TABLE idempotency_keys (
  key TEXT PRIMARY KEY, tenant_id INTEGER, method TEXT, path TEXT, request_hash TEXT,
  status INTEGER, response TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')), expires_at TEXT NOT NULL
, uid TEXT);
CREATE INDEX ix_deliveries ON webhook_deliveries(tenant_id, status);
CREATE INDEX ix_entity_meta ON entity_meta(tenant_id, entity, ref_uid);
CREATE TABLE stock_transfers (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  from_warehouse INTEGER, to_warehouse INTEGER, sku_id INTEGER, qty INTEGER NOT NULL DEFAULT 1,
  status TEXT NOT NULL DEFAULT 'draft', reference TEXT DEFAULT '', note TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now')), deleted_at TEXT
, uid TEXT);
CREATE TABLE remittance_records (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  period TEXT NOT NULL, jurisdiction TEXT NOT NULL, tax_type TEXT DEFAULT 'vat',
  taxable REAL DEFAULT 0, tax_collected REAL DEFAULT 0, currency TEXT DEFAULT 'USD',
  status TEXT NOT NULL DEFAULT 'pending', filed_at TEXT, reference TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now')), deleted_at TEXT
, uid TEXT);
CREATE TABLE inbound_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER, provider TEXT, event TEXT,
  payload TEXT DEFAULT '{}', signature_ok INTEGER DEFAULT 0, processed INTEGER DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE TABLE sso_connections (
  tenant_id INTEGER PRIMARY KEY, provider TEXT DEFAULT 'okta', entity_id TEXT DEFAULT '',
  sso_url TEXT DEFAULT '', cert TEXT DEFAULT '', enabled INTEGER DEFAULT 0, domains TEXT DEFAULT '[]',
  mode TEXT DEFAULT 'saml', issuer TEXT DEFAULT '', client_id TEXT DEFAULT '', client_secret TEXT DEFAULT '',
  redirect_uri TEXT DEFAULT '', scope TEXT DEFAULT 'openid email profile', auto_provision INTEGER DEFAULT 0,
  default_role TEXT DEFAULT 'manager', updated_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE TABLE sso_states (
  state TEXT PRIMARY KEY, tenant_id INTEGER NOT NULL, nonce TEXT DEFAULT '', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE scim_tokens (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, token_hash TEXT NOT NULL,
  label TEXT DEFAULT '', prefix TEXT DEFAULT '', created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE TABLE offers (
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
, deleted_at TEXT, domain TEXT DEFAULT 'incentive', benefit TEXT DEFAULT '', reality TEXT DEFAULT 'any', economic_unit TEXT DEFAULT '', temporal_spec TEXT DEFAULT '{}', spatial_spec TEXT DEFAULT '{}', conditions TEXT DEFAULT '{}', distribution TEXT DEFAULT '[]', attribution_model TEXT DEFAULT 'last_touch', funding TEXT DEFAULT '{}', governance TEXT DEFAULT '{}', campaign TEXT DEFAULT '', version INTEGER DEFAULT 1, parent_id INTEGER, uid TEXT);
CREATE TABLE coupons (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL DEFAULT 0,
  code TEXT NOT NULL, offer_id INTEGER, funder TEXT DEFAULT 'self', funder_ref TEXT DEFAULT '', brand_ref TEXT DEFAULT '',
  kind TEXT NOT NULL DEFAULT 'single_use', value REAL DEFAULT 0, currency TEXT DEFAULT 'USD',
  max_uses INTEGER DEFAULT 1, per_owner_limit INTEGER DEFAULT 1, used INTEGER DEFAULT 0,
  issued_to TEXT DEFAULT '', batch TEXT DEFAULT '', starts TEXT, ends TEXT, status TEXT DEFAULT 'active', note TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now')), deleted_at TEXT, uid TEXT, UNIQUE (tenant_id, code)
);
CREATE TABLE coupon_redemptions (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  coupon_id INTEGER, offer_id INTEGER, code TEXT, order_id INTEGER, invoice_id INTEGER,
  owner TEXT, channel TEXT DEFAULT 'commerce', amount REAL DEFAULT 0, qty INTEGER DEFAULT 1,
  funder TEXT DEFAULT 'self', funder_ref TEXT DEFAULT '', brand_ref TEXT DEFAULT '',
  meta TEXT DEFAULT '{}', created_at TEXT NOT NULL DEFAULT (datetime('now'))
, credits REAL DEFAULT 0, offer_type TEXT DEFAULT '', status TEXT DEFAULT 'redeemed', settlement_id INTEGER, unit TEXT DEFAULT '', uid TEXT);
CREATE TABLE wallet_entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL DEFAULT 0,
  owner TEXT NOT NULL, currency TEXT DEFAULT 'USD', kind TEXT NOT NULL,
  amount REAL NOT NULL, balance_after REAL DEFAULT 0, ref TEXT DEFAULT '', note TEXT DEFAULT '',
  channel TEXT DEFAULT 'commerce', actor TEXT DEFAULT 'system',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE TABLE ledger_accounts (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, wallet_id TEXT, system_key TEXT, unit TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')), UNIQUE(wallet_id), UNIQUE(tenant_id, system_key, unit)
);
CREATE TABLE ledger_journals (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, op TEXT NOT NULL, ref TEXT NOT NULL DEFAULT '', idem_key TEXT,
  request_hash TEXT NOT NULL DEFAULT '', actor TEXT NOT NULL DEFAULT '', reason TEXT NOT NULL DEFAULT '', reverses INTEGER, event_seq INTEGER,
  created_at TEXT NOT NULL DEFAULT (datetime('now')), UNIQUE(tenant_id, idem_key), UNIQUE(reverses)
);
CREATE TABLE ledger_postings (
  id INTEGER PRIMARY KEY AUTOINCREMENT, journal_id INTEGER NOT NULL, account_id INTEGER NOT NULL, unit TEXT NOT NULL, amount INTEGER NOT NULL
);
CREATE INDEX ix_ledger_postings_account ON ledger_postings(account_id);
CREATE INDEX ix_ledger_postings_journal ON ledger_postings(journal_id);
CREATE TABLE wallet_holds (
  id INTEGER PRIMARY KEY AUTOINCREMENT, wallet_id TEXT NOT NULL, amount INTEGER NOT NULL, captured INTEGER NOT NULL DEFAULT 0,
  purpose TEXT NOT NULL DEFAULT '', ref TEXT NOT NULL DEFAULT '', idem_key TEXT, expires_at TEXT, status TEXT NOT NULL, decided_at TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')), UNIQUE(wallet_id, idem_key)
);
CREATE INDEX ix_wallet_holds ON wallet_holds(wallet_id, status);
CREATE TABLE goip_touchpoints (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL DEFAULT 0,
  subject_uid TEXT DEFAULT '', offer_id INTEGER, code TEXT DEFAULT '', kind TEXT NOT NULL DEFAULT 'view',
  party TEXT DEFAULT '', party_type TEXT DEFAULT 'customer', channel TEXT DEFAULT 'commerce', distribution TEXT DEFAULT 'in_app',
  device TEXT DEFAULT '', owner TEXT DEFAULT '', session TEXT DEFAULT '', order_id INTEGER,
  value REAL DEFAULT 0, unit TEXT DEFAULT 'USD', context TEXT DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE TABLE goip_budgets (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL DEFAULT 0,
  domain TEXT NOT NULL DEFAULT 'incentive', funder TEXT NOT NULL DEFAULT 'self', funder_ref TEXT DEFAULT '',
  unit TEXT NOT NULL DEFAULT 'USD', allocated REAL DEFAULT 0, reserved REAL DEFAULT 0, consumed REAL DEFAULT 0,
  period TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'open', policy TEXT DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now')), updated_at TEXT
, uid TEXT);
CREATE TABLE goip_settlements (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL DEFAULT 0,
  period TEXT NOT NULL DEFAULT '', party TEXT NOT NULL DEFAULT '', party_type TEXT NOT NULL DEFAULT 'merchant',
  unit TEXT NOT NULL DEFAULT 'USD', gross REAL DEFAULT 0, fees REAL DEFAULT 0, net REAL DEFAULT 0,
  redemptions REAL DEFAULT 0, status TEXT NOT NULL DEFAULT 'accrued', reference TEXT DEFAULT '',
  paid_at TEXT, meta TEXT DEFAULT '{}', created_at TEXT NOT NULL DEFAULT (datetime('now')), updated_at TEXT
, uid TEXT);
CREATE TABLE goip_entitlements (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL DEFAULT 0,
  owner TEXT NOT NULL DEFAULT '', benefit TEXT NOT NULL DEFAULT '', unit TEXT DEFAULT '', qty REAL DEFAULT 0,
  tier TEXT DEFAULT '', scope TEXT DEFAULT '{}', starts TEXT, ends TEXT, status TEXT NOT NULL DEFAULT 'active',
  source_offer INTEGER, source_redemption INTEGER, meta TEXT DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE TABLE entity_usage (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  entity TEXT NOT NULL, action TEXT NOT NULL, at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE (tenant_id, entity, action)
);
CREATE TABLE capabilities (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  key TEXT NOT NULL, category TEXT NOT NULL DEFAULT 'feature', name TEXT NOT NULL,
  description TEXT DEFAULT '', version TEXT DEFAULT '1.0.0', schema TEXT DEFAULT '{}',
  config TEXT DEFAULT '{}', dependencies TEXT DEFAULT '[]', status TEXT DEFAULT 'active',
  enabled INTEGER DEFAULT 1, created_at TEXT NOT NULL DEFAULT (datetime('now')), updated_at TEXT
);
CREATE TABLE config_store (
  id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT NOT NULL,
  scope TEXT NOT NULL DEFAULT 'platform', tenant_id INTEGER, version INTEGER DEFAULT 1,
  value TEXT DEFAULT '{}', active INTEGER DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT (datetime('now')), updated_at TEXT,
  UNIQUE (key, scope, tenant_id)
);
CREATE TABLE workflows (
  id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT NOT NULL UNIQUE, domain TEXT NOT NULL,
  name TEXT, description TEXT DEFAULT '', trigger TEXT NOT NULL,
  steps TEXT NOT NULL DEFAULT '[]', config TEXT NOT NULL DEFAULT '{}', status TEXT NOT NULL DEFAULT 'active',
  created_at TEXT NOT NULL DEFAULT (datetime('now')), updated_at TEXT
);
CREATE INDEX ix_workflow_domain ON workflows(domain, status);
CREATE TABLE knowledge_graph (
  id INTEGER PRIMARY KEY AUTOINCREMENT, source_type TEXT NOT NULL, source_id INTEGER NOT NULL,
  relationship TEXT NOT NULL, target_type TEXT NOT NULL, target_id INTEGER NOT NULL,
  weight REAL NOT NULL DEFAULT 1.0, metadata TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_kg_source ON knowledge_graph(source_type, source_id);
CREATE INDEX ix_kg_target ON knowledge_graph(target_type, target_id);
CREATE TABLE usage_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER, entity TEXT NOT NULL,
  entity_id INTEGER, event_type TEXT NOT NULL, quantity REAL NOT NULL DEFAULT 1,
  unit TEXT NOT NULL DEFAULT 'count', metadata TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_usage_tenant ON usage_events(tenant_id, entity, created_at);
CREATE TABLE composition_ledger (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  key TEXT NOT NULL UNIQUE,           /* the composed model key (cp_<capability>) — one row per capability */
  capability TEXT NOT NULL,          /* the human label of what was composed */
  source TEXT,                       /* provenance: doc:line / catalog / registry */
  artifacts TEXT NOT NULL DEFAULT '{}',  /* the full manifest (data model, API, workflow, UI, dashboard, security) */
  composed_at TEXT NOT NULL
);
CREATE INDEX ix_composition_key ON composition_ledger(key, composed_at);
CREATE TABLE domains (
  id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT NOT NULL UNIQUE, name TEXT NOT NULL,
  description TEXT DEFAULT '', parent TEXT DEFAULT '',
  schema TEXT NOT NULL DEFAULT '{}', policies TEXT NOT NULL DEFAULT '[]',
  status TEXT NOT NULL DEFAULT 'active', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_domain_parent ON domains(parent, status);
CREATE TABLE policies (
  id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT NOT NULL UNIQUE, domain TEXT,
  name TEXT NOT NULL, description TEXT DEFAULT '', type TEXT NOT NULL DEFAULT 'validation',
  priority INTEGER NOT NULL DEFAULT 0, rule TEXT NOT NULL, context TEXT NOT NULL DEFAULT '{}',
  status TEXT NOT NULL DEFAULT 'active', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_policy_domain ON policies(domain, priority, status);
CREATE TABLE identity_providers (
  id TEXT PRIMARY KEY, tenant_id INTEGER NOT NULL, provider_type TEXT NOT NULL, name TEXT NOT NULL,
  enabled INTEGER DEFAULT 1, config TEXT DEFAULT '{}', display_order INTEGER DEFAULT 0,
  created_at TEXT DEFAULT (datetime('now')), updated_at TEXT
);
CREATE TABLE platform_identity_templates (
  id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, description TEXT DEFAULT '',
  config TEXT DEFAULT '{}', is_default INTEGER DEFAULT 0, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE user_identity_methods (
  user_id INTEGER NOT NULL, method_id TEXT PRIMARY KEY, method_type TEXT NOT NULL,
  identifier TEXT NOT NULL, metadata TEXT DEFAULT '{}', is_primary INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now')), updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_uim_user ON user_identity_methods(user_id, is_primary);
CREATE TABLE identity_otps (
  id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, identifier TEXT NOT NULL,
  otp TEXT NOT NULL, expires_at INTEGER NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,
  verified INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_otp_user ON identity_otps(user_id, identifier, verified);
CREATE TABLE identity_magic_links (
  id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, identifier TEXT NOT NULL,
  token TEXT NOT NULL, expires_at INTEGER NOT NULL, used_at TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_magic_token ON identity_magic_links(token, used_at);
CREATE TABLE identity_biometric_challenges (
  id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, challenge TEXT NOT NULL,
  expires_at INTEGER NOT NULL, verified INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_bio_challenge ON identity_biometric_challenges(user_id, challenge, verified);
CREATE TABLE identity_login_states (
  state TEXT PRIMARY KEY, tenant_id INTEGER NOT NULL, provider_id TEXT NOT NULL,
  expires_at INTEGER NOT NULL, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_login_state ON identity_login_states(tenant_id, expires_at);
CREATE INDEX ix_goip_touch ON goip_touchpoints(tenant_id, owner, created_at);
CREATE INDEX ix_goip_touch_party ON goip_touchpoints(tenant_id, party_type, party);
CREATE INDEX ix_goip_budget ON goip_budgets(tenant_id, funder, unit, period, status);
CREATE INDEX ix_goip_settle ON goip_settlements(tenant_id, period, status);
CREATE INDEX ix_goip_ent ON goip_entitlements(tenant_id, owner, status);
CREATE UNIQUE INDEX ux_offers_code ON offers(tenant_id, code) WHERE code<>'';
CREATE INDEX ix_offers_chan ON offers(channel, status, tenant_id);
CREATE INDEX ix_wallet_tx ON wallet_entries(tenant_id, owner);
CREATE INDEX ix_products_tenant ON products(tenant_id, dept);
CREATE INDEX ix_reviews_pid ON reviews(tenant_id, product_id);
CREATE INDEX ix_orders_tenant ON orders(tenant_id, created_at);
CREATE INDEX ix_audit_tenant ON audit_log(tenant_id, created_at);
CREATE TABLE ucos_documents (
  doc_id TEXT PRIMARY KEY, file TEXT NOT NULL, code TEXT NOT NULL, name TEXT NOT NULL,
  kind TEXT NOT NULL DEFAULT 'architecture',
  parts INTEGER DEFAULT 0, sections INTEGER DEFAULT 0, articles INTEGER DEFAULT 0,
  concepts INTEGER DEFAULT 0, registries INTEGER DEFAULT 0, lines INTEGER DEFAULT 0, chars INTEGER DEFAULT 0
);
CREATE TABLE ucos_parts (
  id INTEGER PRIMARY KEY AUTOINCREMENT, doc_id TEXT NOT NULL, no INTEGER, label TEXT, title TEXT, line INTEGER
);
CREATE INDEX ix_ucos_parts ON ucos_parts(doc_id, no);
CREATE TABLE ucos_sections (
  id INTEGER PRIMARY KEY AUTOINCREMENT, doc_id TEXT NOT NULL, qkey TEXT NOT NULL,
  no INTEGER, key TEXT, name TEXT, part_no INTEGER, line INTEGER,
  concepts INTEGER DEFAULT 0, registries INTEGER DEFAULT 0, meta TEXT DEFAULT '{}',
  kind TEXT DEFAULT 'section', doc_block TEXT
);
CREATE UNIQUE INDEX ux_ucos_sections ON ucos_sections(doc_id, qkey);
CREATE TABLE ucos_concepts (
  id INTEGER PRIMARY KEY AUTOINCREMENT, doc_id TEXT NOT NULL, key TEXT NOT NULL,
  name TEXT NOT NULL, container_kind TEXT, container_key TEXT, container_name TEXT,
  part_no INTEGER, line INTEGER
);
CREATE INDEX ix_ucos_concepts ON ucos_concepts(doc_id, key);
CREATE INDEX ix_ucos_concepts_name ON ucos_concepts(doc_id, name);
CREATE TABLE ucos_registries (
  id INTEGER PRIMARY KEY AUTOINCREMENT, doc_id TEXT NOT NULL, key TEXT NOT NULL, label TEXT,
  container_kind TEXT, container_key TEXT, items TEXT DEFAULT '[]', item_count INTEGER DEFAULT 0, line INTEGER
);
CREATE INDEX ix_ucos_reg ON ucos_registries(doc_id, key);
CREATE TABLE ucos_edges (
  id INTEGER PRIMARY KEY AUTOINCREMENT, doc_id TEXT NOT NULL,
  source_type TEXT NOT NULL, source_id TEXT NOT NULL, rel TEXT NOT NULL,
  target_type TEXT NOT NULL, target_id TEXT NOT NULL
);
CREATE UNIQUE INDEX ux_ucos_edges ON ucos_edges(doc_id, source_type, source_id, rel, target_type, target_id);
CREATE INDEX ix_ucos_edges_src ON ucos_edges(doc_id, source_type, source_id);
CREATE TABLE ucos_annotations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  doc_id TEXT NOT NULL,          /* which constitution the target belongs to */
  target_kind TEXT NOT NULL,     /* concept | section | part */
  target_key TEXT NOT NULL,      /* canonical key from the parse (never a display name) */
  note TEXT NOT NULL,            /* the annotation body */
  pin INTEGER DEFAULT 0,         /* pinned annotations float to the top of the registry view */
  created_by TEXT,               /* platform admin email */
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX ix_ucos_ann ON ucos_annotations(doc_id, target_kind, target_key);
CREATE INDEX ix_ucos_ann_pin ON ucos_annotations(doc_id, target_kind, target_key, pin);
CREATE TABLE ucos_foundations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  key TEXT NOT NULL UNIQUE,              /* canonical identity (Article 8.2: globally unique) */
  name TEXT NOT NULL,
  parent TEXT,                           /* parent foundation (derivation, Article 4.1) */
  universe TEXT,                         /* the declared universe this foundation belongs to */
  lifecycle TEXT NOT NULL DEFAULT 'canonical',      /* Article 5.1 states */
  governance TEXT NOT NULL DEFAULT 'Foundation Authority',  /* Article 6 */
  classification TEXT,                   /* universe | domain | foundation | primitive | capability */
  source_doc TEXT,                       /* traceability: which corpus document declares it */
  source_line INTEGER,
  discovery TEXT,                        /* Article 2.2 discovery handle */
  created_at TEXT
);
CREATE INDEX ix_ucos_foundations_universe ON ucos_foundations(universe, lifecycle);
CREATE INDEX ix_ucos_foundations_parent ON ucos_foundations(parent);
CREATE TABLE ucos_foundation_deps (
  id INTEGER PRIMARY KEY AUTOINCREMENT, foundation TEXT NOT NULL, dependency TEXT NOT NULL,
  UNIQUE(foundation, dependency)
);
CREATE INDEX ix_ucos_foundation_deps_dep ON ucos_foundation_deps(dependency);
CREATE TABLE ucos_foundation_evolution (
  id INTEGER PRIMARY KEY AUTOINCREMENT, foundation TEXT NOT NULL, predecessor TEXT NOT NULL,
  UNIQUE(foundation, predecessor)
);
CREATE TABLE ucos_foundation_composition (
  id INTEGER PRIMARY KEY AUTOINCREMENT, parent TEXT NOT NULL, child TEXT NOT NULL,
  UNIQUE(parent, child)
);
CREATE INDEX ix_ucos_foundation_comp_child ON ucos_foundation_composition(child);
CREATE TABLE ucos_foundation_audit (
  id INTEGER PRIMARY KEY AUTOINCREMENT, foundation TEXT NOT NULL, event TEXT NOT NULL,
  detail TEXT DEFAULT '{}', at TEXT NOT NULL
);
CREATE INDEX ix_ucos_foundation_audit_f ON ucos_foundation_audit(foundation, at);
CREATE TABLE ucos_universes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  key TEXT NOT NULL UNIQUE,              /* universe identity = its foundation key */
  name TEXT NOT NULL,
  source_doc TEXT NOT NULL,              /* which corpus document declares it */
  source_line INTEGER,
  entity_key TEXT NOT NULL,              /* the generic entity_def key it instantiates as */
  concepts INTEGER DEFAULT 0,            /* corpus concepts this universe governs */
  instantiated_at TEXT,
  UNIQUE(entity_key)
);
CREATE TABLE ucos_record_transitions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  entity_key TEXT NOT NULL,              /* which universe's record transitioned */
  record_id INTEGER NOT NULL,
  from_state TEXT NOT NULL,
  to_state TEXT NOT NULL,
  rule TEXT,                             /* the corpus rule that authorized it (5.2) */
  actor TEXT,                            /* who fired the transition */
  detail TEXT DEFAULT '{}',
  at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_ucos_record_tr_entity ON ucos_record_transitions(entity_key, record_id, at);
CREATE TABLE theme_presets (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  key TEXT NOT NULL UNIQUE,               /* "quantum-glass", "solar-flare"… */
  name TEXT NOT NULL,
  mood TEXT,                              /* light | dark | futurist | organic… the registry's own vocabulary */
  vars TEXT NOT NULL,                     /* the CSS custom properties, as JSON */
  preview TEXT,                           /* a small gradient/emoji signature for the picker */
  built_in INTEGER DEFAULT 0,             /* shipped presets vs operator-created */
  position INTEGER DEFAULT 0
);
CREATE TABLE theme_assignments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  scope TEXT NOT NULL,                    /* platform | tenant | dept | product */
  scope_key TEXT NOT NULL,                /* tenant id / dept key / product id ("*" = any) */
  theme_key TEXT NOT NULL,
  UNIQUE(scope, scope_key)
);
CREATE INDEX ix_theme_assign_lookup ON theme_assignments(scope, scope_key);
CREATE TABLE dashboards (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER,                       /* NULL = platform canonical template */
  key TEXT NOT NULL,
  name TEXT NOT NULL,
  type TEXT,                               /* §394 dashboard categories */
  audience TEXT DEFAULT 'admin',           /* admin | platform | all */
  description TEXT,
  active INTEGER DEFAULT 1,
  position INTEGER DEFAULT 0,
  UNIQUE(tenant_id, key)
);
CREATE INDEX ix_dash_lookup ON dashboards(tenant_id, active, position);
CREATE TABLE dashboard_widgets (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  dashboard_id INTEGER NOT NULL,
  kind TEXT,                               /* kpi | table | bar | line | donut | text */
  label TEXT,
  entity TEXT,                             /* any entity key the engine knows */
  metric TEXT,                             /* count | sum | avg | min | max | distinct */
  column TEXT,                             /* column for sum/avg/min/max/distinct */
  dimension TEXT,                          /* group-by column (table/bar/line/donut) */
  ord TEXT DEFAULT 'desc',                 /* asc | desc — ordering of the aggregate */
  lim INTEGER DEFAULT 10,
  filter TEXT DEFAULT '{}',                /* JSON {field: value} equality predicates */
  position INTEGER DEFAULT 0,
  span INTEGER DEFAULT 3                   /* grid width 1..6 (of 6) */
);
CREATE INDEX ix_widgets_dash ON dashboard_widgets(dashboard_id, position);
CREATE TABLE dashboard_prefs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER,
  user_id INTEGER NOT NULL,
  dashboard_id INTEGER NOT NULL,
  widget_id INTEGER,
  hidden INTEGER DEFAULT 0,
  position INTEGER,
  UNIQUE(user_id, dashboard_id, widget_id)
);
CREATE TABLE reports (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER,                       /* NULL = platform canonical template */
  key TEXT NOT NULL,
  name TEXT NOT NULL,
  kind TEXT,                               /* §395: scheduled | event | regulatory | operational | executive | ai */
  entity TEXT NOT NULL,
  metrics TEXT DEFAULT '[]',               /* JSON [{metric,column,alias}] */
  dimensions TEXT DEFAULT '[]',            /* JSON [column] */
  filter TEXT DEFAULT '{}',
  schedule TEXT DEFAULT 'manual',          /* manual | daily | weekly | monthly */
  format TEXT DEFAULT 'table',             /* table | csv | json */
  active INTEGER DEFAULT 1,
  last_run TEXT,
  position INTEGER DEFAULT 0,
  UNIQUE(tenant_id, key)
);
CREATE INDEX ix_reports_lookup ON reports(tenant_id, active, position);
CREATE UNIQUE INDEX ux_reports_platform_key ON reports(key, ifnull(tenant_id, 0));
CREATE TABLE dark_stores (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  uid TEXT, code TEXT, name TEXT NOT NULL, kind TEXT NOT NULL DEFAULT 'dark_store',
  address TEXT, city TEXT, region TEXT, pincode TEXT, country TEXT,
  lat REAL, lng REAL, service_radius_km REAL DEFAULT 3.0,
  promise_minutes INTEGER DEFAULT 10, prep_minutes INTEGER DEFAULT 4,
  min_order REAL DEFAULT 0, delivery_fee REAL DEFAULT 0,
  service_pincodes TEXT DEFAULT '[]', service_days TEXT DEFAULT '[]',
  status TEXT NOT NULL DEFAULT 'active',
  deleted_at TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_darkstore_tenant ON dark_stores(tenant_id, status);
CREATE TABLE delivery_slots (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  store_id INTEGER, day_offset INTEGER DEFAULT 0,
  window_start TEXT NOT NULL, window_end TEXT NOT NULL,
  capacity INTEGER DEFAULT 20, booked INTEGER DEFAULT 0,
  cutoff_minutes INTEGER DEFAULT 0, fee REAL DEFAULT 0,
  promise_minutes INTEGER, status TEXT NOT NULL DEFAULT 'open',
  deleted_at TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_slots_tenant ON delivery_slots(tenant_id, store_id, day_offset);
CREATE TABLE service_areas (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  store_id INTEGER, pincode TEXT NOT NULL, area_name TEXT,
  serviceable INTEGER DEFAULT 1, eta_minutes INTEGER DEFAULT 10,
  fee REAL DEFAULT 0, min_order REAL DEFAULT 0, cod_available INTEGER DEFAULT 1,
  status TEXT NOT NULL DEFAULT 'active',
  deleted_at TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_service_tenant ON service_areas(tenant_id, pincode, serviceable);
CREATE TABLE store_inventory (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  store_id INTEGER NOT NULL, sku_id INTEGER, product_id TEXT,
  qty INTEGER DEFAULT 0, reserved INTEGER DEFAULT 0, safety_stock INTEGER DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'active',
  deleted_at TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_storeinv ON store_inventory(tenant_id, store_id, product_id);
CREATE TABLE riders (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  uid TEXT, name TEXT NOT NULL, phone TEXT, vehicle TEXT,
  store_id INTEGER, city TEXT, status TEXT NOT NULL DEFAULT 'offline',
  shift_start TEXT, shift_end TEXT, rating REAL, deliveries INTEGER DEFAULT 0,
  deleted_at TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_riders_tenant ON riders(tenant_id, status);
CREATE TABLE dispatch_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  ref TEXT, store_id INTEGER, slot_id INTEGER, rider_id INTEGER,
  order_ids TEXT DEFAULT '[]', status TEXT NOT NULL DEFAULT 'assigned',
  batch_count INTEGER DEFAULT 0, pod_otp TEXT, pod_at TEXT,
  notes TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_dispatch_tenant ON dispatch_runs(tenant_id, status);
CREATE TABLE upi_handles (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  owner TEXT NOT NULL, vpa TEXT NOT NULL, name TEXT,
  verified INTEGER DEFAULT 0, is_default INTEGER DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'active', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_upi_owner ON upi_handles(tenant_id, owner);
CREATE TABLE upi_collects (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  ref TEXT, owner TEXT, payer_vpa TEXT, amount REAL NOT NULL,
  currency TEXT, note TEXT, status TEXT NOT NULL DEFAULT 'initiated',
  txn_ref TEXT, expires_at TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_collect_tenant ON upi_collects(tenant_id, status);
CREATE TABLE qr_codes (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  ref TEXT, kind TEXT NOT NULL DEFAULT 'upi', payload TEXT NOT NULL,
  label TEXT, amount REAL, owner TEXT, svg TEXT,
  scans INTEGER DEFAULT 0, status TEXT NOT NULL DEFAULT 'active',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_qr_tenant ON qr_codes(tenant_id, kind, status);
CREATE TABLE payment_links (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  ref TEXT, token TEXT NOT NULL, title TEXT, amount REAL NOT NULL,
  currency TEXT, owner TEXT, gateway TEXT, purpose TEXT,
  expires_at TEXT, paid_at TEXT, status TEXT NOT NULL DEFAULT 'issued',
  txn_ref TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_paylinks_tenant ON payment_links(tenant_id, status);
CREATE TABLE mandates (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  ref TEXT, owner TEXT NOT NULL, mandate_id TEXT, gateway TEXT,
  max_amount REAL, frequency TEXT, purpose TEXT,
  status TEXT NOT NULL DEFAULT 'registered', next_charge_at TEXT,
  charged_amount REAL DEFAULT 0, charges_done INTEGER DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_mandates_owner ON mandates(tenant_id, owner, status);
CREATE TABLE escrow_holds (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  ref TEXT, order_id INTEGER, buyer TEXT, seller TEXT,
  amount REAL NOT NULL, currency TEXT, held INTEGER DEFAULT 1,
  released_at TEXT, dispute_opened INTEGER DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'held', meta TEXT DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_escrow_tenant ON escrow_holds(tenant_id, status);
CREATE TABLE split_payments (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  ref TEXT, payment_id INTEGER, order_id INTEGER,
  splits TEXT NOT NULL DEFAULT '[]', status TEXT NOT NULL DEFAULT 'pending',
  settled_at TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_splits_tenant ON split_payments(tenant_id, status);
CREATE TABLE kyc_profiles (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  owner TEXT NOT NULL, kind TEXT NOT NULL DEFAULT 'individual',
  full_name TEXT, dob TEXT, pan TEXT, aadhaar_masked TEXT,
  gstin TEXT, company TEXT, website TEXT,
  doc_type TEXT, doc_ref TEXT, doc_status TEXT NOT NULL DEFAULT 'unverified',
  status TEXT NOT NULL DEFAULT 'pending', verified_at TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_kyc_owner ON kyc_profiles(tenant_id, owner, status);
CREATE TABLE bank_payouts (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  ref TEXT, payee TEXT, amount REAL NOT NULL, currency TEXT,
  account_name TEXT, account_number TEXT, ifsc TEXT, upi_vpa TEXT,
  gateway TEXT, status TEXT NOT NULL DEFAULT 'queued',
  txn_ref TEXT, failure_reason TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_payouts_tenant ON bank_payouts(tenant_id, status);
CREATE TABLE applicability_rules (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER,
  subject_type TEXT NOT NULL, subject TEXT NOT NULL DEFAULT '*',
  effect TEXT NOT NULL DEFAULT 'allow', priority INTEGER NOT NULL DEFAULT 0,
  scope TEXT NOT NULL DEFAULT '{}', params TEXT NOT NULL DEFAULT '{}',
  note TEXT DEFAULT '', active INTEGER NOT NULL DEFAULT 1, created_by TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')), updated_at TEXT
);
CREATE INDEX ix_rules_subject ON applicability_rules(subject_type, tenant_id, active);
CREATE TABLE segment_members (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  owner TEXT NOT NULL, segment TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE(tenant_id, owner, segment)
);
CREATE TABLE billers (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  name TEXT NOT NULL, category TEXT NOT NULL, code TEXT,
  fetch_required INTEGER DEFAULT 1, fields TEXT DEFAULT '[]',
  status TEXT NOT NULL DEFAULT 'active', position INTEGER DEFAULT 0
);
CREATE INDEX ix_billers_tenant ON billers(tenant_id, category, status);
CREATE TABLE bill_payments (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  ref TEXT, owner TEXT, biller_id INTEGER, category TEXT,
  account_no TEXT, amount REAL NOT NULL, currency TEXT,
  convenience_fee REAL DEFAULT 0, status TEXT NOT NULL DEFAULT 'initiated',
  txn_ref TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_billpay_tenant ON bill_payments(tenant_id, owner, status);
CREATE TABLE recharges (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  ref TEXT, owner TEXT, number TEXT NOT NULL, operator TEXT,
  circle TEXT, plan_id INTEGER, amount REAL NOT NULL, currency TEXT,
  kind TEXT NOT NULL DEFAULT 'mobile', status TEXT NOT NULL DEFAULT 'initiated',
  txn_ref TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_recharge_tenant ON recharges(tenant_id, owner, status);
CREATE TABLE recharge_plans (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  operator TEXT NOT NULL, circle TEXT, kind TEXT NOT NULL DEFAULT 'mobile',
  amount REAL NOT NULL, currency TEXT, validity TEXT, data TEXT,
  sms TEXT, calls TEXT, description TEXT, popular INTEGER DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'active', position INTEGER DEFAULT 0
);
CREATE INDEX ix_plans_tenant ON recharge_plans(tenant_id, operator, kind);
CREATE TABLE bnpl_accounts (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  owner TEXT NOT NULL, provider TEXT, credit_limit REAL DEFAULT 0,
  used REAL DEFAULT 0, available REAL DEFAULT 0, tenure_months INTEGER DEFAULT 3,
  status TEXT NOT NULL DEFAULT 'inactive', kyc_id INTEGER,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_bnpl_owner ON bnpl_accounts(tenant_id, owner, status);
CREATE TABLE bnpl_emis (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  account_id INTEGER NOT NULL, order_id INTEGER,
  installment_no INTEGER, amount REAL, due_at TEXT,
  status TEXT NOT NULL DEFAULT 'upcoming', paid_at TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_emi_account ON bnpl_emis(tenant_id, account_id, status);
CREATE TABLE loans (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  ref TEXT, owner TEXT NOT NULL, principal REAL NOT NULL,
  currency TEXT, tenure_months INTEGER, rate REAL,
  emi REAL, processing_fee REAL, disbursed_at TEXT,
  status TEXT NOT NULL DEFAULT 'applied', kyc_id INTEGER,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_loans_tenant ON loans(tenant_id, owner, status);
CREATE TABLE insurance_policies (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  ref TEXT, owner TEXT NOT NULL, product_id INTEGER, plan_name TEXT,
  premium REAL NOT NULL, currency TEXT, cover REAL,
  starts_at TEXT, ends_at TEXT, nominees TEXT,
  status TEXT NOT NULL DEFAULT 'quoted', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_insurance_tenant ON insurance_policies(tenant_id, owner, status);
CREATE TABLE gift_vouchers (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  code TEXT NOT NULL, amount REAL NOT NULL, currency TEXT,
  buyer TEXT, recipient TEXT, recipient_email TEXT, message TEXT,
  expires_at TEXT, redeemed_at TEXT, redeemed_by TEXT,
  status TEXT NOT NULL DEFAULT 'issued', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_voucher_tenant ON gift_vouchers(tenant_id, code, status);
CREATE TABLE seller_onboarding (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  seller_id INTEGER, ref TEXT, business_name TEXT NOT NULL,
  business_type TEXT, gstin TEXT, pan TEXT, tan TEXT,
  bank_name TEXT, bank_account TEXT, bank_ifsc TEXT,
  docs TEXT DEFAULT '[]', status TEXT NOT NULL DEFAULT 'submitted',
  submitted_at TEXT, reviewed_at TEXT, reviewed_by TEXT, notes TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_onb_tenant ON seller_onboarding(tenant_id, status);
CREATE TABLE seller_offers (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  product_id TEXT NOT NULL, sku_id INTEGER, seller_id INTEGER NOT NULL,
  price REAL NOT NULL, currency TEXT, condition TEXT DEFAULT 'new',
  fulfillment TEXT DEFAULT 'fbm', handling_hours INTEGER,
  shipping_days INTEGER, offer_status TEXT NOT NULL DEFAULT 'active',
  buybox INTEGER DEFAULT 0, buybox_score REAL DEFAULT 0,
  deleted_at TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_offers_product ON seller_offers(tenant_id, product_id, offer_status, price);
CREATE TABLE fba_inbound (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  ref TEXT, seller_id INTEGER, warehouse_id INTEGER,
  sku_id INTEGER, units INTEGER, status TEXT NOT NULL DEFAULT 'created',
  fee REAL, tracking_ref TEXT, received_at TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_fba_tenant ON fba_inbound(tenant_id, seller_id, status);
CREATE TABLE seller_performance (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  seller_id INTEGER NOT NULL, period TEXT NOT NULL,
  orders INTEGER DEFAULT 0, odr REAL DEFAULT 0, odr_targets INTEGER DEFAULT 0,
  late_ship_rate REAL DEFAULT 0, late_shipments INTEGER DEFAULT 0,
  cancel_rate REAL DEFAULT 0, cancellations INTEGER DEFAULT 0,
  valid_tracked_rate REAL DEFAULT 0, health_score REAL DEFAULT 0,
  tier TEXT DEFAULT 'standard', status TEXT NOT NULL DEFAULT 'computed',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_perf_seller ON seller_performance(tenant_id, seller_id, period);
CREATE TABLE buyer_claims (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  ref TEXT, order_id INTEGER, buyer TEXT, seller_id INTEGER,
  kind TEXT NOT NULL DEFAULT 'atoz', reason TEXT,
  amount REAL, currency TEXT, evidence TEXT DEFAULT '[]',
  status TEXT NOT NULL DEFAULT 'opened', resolution TEXT,
  resolved_at TEXT, resolved_by TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_claims_tenant ON buyer_claims(tenant_id, status);
CREATE TABLE smart_fulfilment (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  seller_id INTEGER, ref TEXT, grade TEXT DEFAULT 'b',
  sla_hours INTEGER, packed_same_day INTEGER DEFAULT 0,
  score REAL DEFAULT 0, status TEXT NOT NULL DEFAULT 'enrolled',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_smartful_tenant ON smart_fulfilment(tenant_id, seller_id);
CREATE TABLE sponsored_creatives (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  ad_id INTEGER, seller_id INTEGER, kind TEXT NOT NULL DEFAULT 'sponsored_product',
  headline TEXT, creative TEXT, landing TEXT,
  bid_model TEXT, bid_amount REAL, budget REAL, spent REAL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'draft', start_at TEXT, end_at TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_creative_tenant ON sponsored_creatives(tenant_id, kind, status);
CREATE TABLE trade_assurance (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  ref TEXT, order_id INTEGER, buyer TEXT, seller TEXT,
  amount REAL NOT NULL, currency TEXT, fee REAL,
  milestones TEXT DEFAULT '[]', current_milestone TEXT,
  held INTEGER DEFAULT 1, released_at TEXT,
  status TEXT NOT NULL DEFAULT 'holding', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_ta_tenant ON trade_assurance(tenant_id, status);
CREATE TABLE gold_suppliers (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  supplier_id INTEGER NOT NULL, tier TEXT NOT NULL DEFAULT 'gold',
  starts_at TEXT, ends_at TEXT, fee REAL, currency TEXT,
  verified INTEGER DEFAULT 0, verification_level TEXT,
  status TEXT NOT NULL DEFAULT 'active', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_gold_tenant ON gold_suppliers(tenant_id, supplier_id, status);
CREATE TABLE company_verifications (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  supplier_id INTEGER, ref TEXT, company_name TEXT NOT NULL,
  country TEXT, registration_no TEXT, year_established TEXT,
  employees TEXT, revenue TEXT, export_share TEXT,
  audit_docs TEXT DEFAULT '[]', audit_by TEXT, audit_at TEXT,
  verification_status TEXT NOT NULL DEFAULT 'pending',
  badges TEXT DEFAULT '[]', notes TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_verif_tenant ON company_verifications(tenant_id, verification_status);
CREATE TABLE export_documents (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  ref TEXT, order_id INTEGER, doc_kind TEXT NOT NULL,
  buyer TEXT, consignee TEXT, shipper TEXT,
  origin_country TEXT, dest_country TEXT, port_loading TEXT, port_discharge TEXT,
  incoterms TEXT, currency TEXT, total_value REAL,
  hs_codes TEXT, packages INTEGER, gross_weight REAL, net_weight REAL,
  marks TEXT, body TEXT, rendered TEXT,
  status TEXT NOT NULL DEFAULT 'draft', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_exportdocs_tenant ON export_documents(tenant_id, doc_kind, status);
CREATE TABLE letters_of_credit (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  ref TEXT, order_id INTEGER, buyer TEXT, seller TEXT,
  issuing_bank TEXT, advising_bank TEXT, lc_number TEXT,
  amount REAL NOT NULL, currency TEXT, issue_date TEXT, expiry_date TEXT,
  port_loading TEXT, port_discharge TEXT, latest_shipment TEXT,
  docs_required TEXT DEFAULT '[]', status TEXT NOT NULL DEFAULT 'issued',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_lc_tenant ON letters_of_credit(tenant_id, status);
CREATE TABLE rfq_quotes (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  rfq_id INTEGER NOT NULL, supplier_id INTEGER, seller_id INTEGER,
  unit_price REAL NOT NULL, currency TEXT, moq INTEGER,
  lead_days INTEGER, payment_terms TEXT, validity_days INTEGER,
  quote_ref TEXT, attachments TEXT DEFAULT '[]',
  status TEXT NOT NULL DEFAULT 'submitted', rank INTEGER,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_rfqquotes_tenant ON rfq_quotes(tenant_id, rfq_id, status);
CREATE TABLE tender_bids (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  tender_id INTEGER NOT NULL, bidder TEXT NOT NULL,
  amount REAL NOT NULL, currency TEXT, terms TEXT,
  bid_ref TEXT, attachments TEXT DEFAULT '[]',
  status TEXT NOT NULL DEFAULT 'submitted', rank INTEGER,
  submitted_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_tenderbids_tender ON tender_bids(tender_id, status);
CREATE TABLE price_lists (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  name TEXT NOT NULL, currency TEXT, segment TEXT,
  starts_at TEXT, ends_at TEXT, status TEXT NOT NULL DEFAULT 'active',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_pricelists_tenant ON price_lists(tenant_id, status);
CREATE TABLE price_list_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  price_list_id INTEGER NOT NULL, product_id TEXT, sku_id INTEGER,
  price REAL NOT NULL, min_qty INTEGER DEFAULT 1, max_qty INTEGER,
  status TEXT NOT NULL DEFAULT 'active', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_plitems_pl ON price_list_items(price_list_id, product_id);
CREATE TABLE gift_registries (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  ref TEXT, owner TEXT NOT NULL, name TEXT NOT NULL, event TEXT,
  event_date TEXT, shipping_address TEXT, notes TEXT,
  items TEXT DEFAULT '[]', contributors TEXT DEFAULT '[]',
  status TEXT NOT NULL DEFAULT 'open', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_registry_owner ON gift_registries(tenant_id, owner, status);
CREATE TABLE notifications (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  owner TEXT, kind TEXT NOT NULL, title TEXT NOT NULL, body TEXT,
  link TEXT, read INTEGER DEFAULT 0, meta TEXT DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_notif_owner ON notifications(tenant_id, owner, read, created_at);
CREATE TABLE compare_lists (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  owner TEXT NOT NULL, product_ids TEXT DEFAULT '[]',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_compare_owner ON compare_lists(tenant_id, owner);
CREATE TABLE shopper_lists (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, owner TEXT NOT NULL, owner_name TEXT DEFAULT '',
  kind TEXT NOT NULL, name TEXT NOT NULL, visibility TEXT NOT NULL, token TEXT NOT NULL, notes TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now')), updated_at TEXT
);
CREATE INDEX ix_slist_owner ON shopper_lists(tenant_id, owner);
CREATE UNIQUE INDEX ux_slist_token ON shopper_lists(token);
CREATE TABLE shopper_list_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, list_id INTEGER NOT NULL,
  product_id TEXT NOT NULL, qty INTEGER NOT NULL DEFAULT 1, purchased INTEGER NOT NULL DEFAULT 0,
  priority TEXT, note TEXT DEFAULT '', price_added REAL,
  added_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE UNIQUE INDEX ux_slist_item ON shopper_list_items(list_id, product_id);
CREATE TABLE product_watches (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, owner TEXT NOT NULL,
  product_id TEXT NOT NULL, kind TEXT NOT NULL, target_price REAL, baseline_price REAL, baseline_stock INTEGER,
  status TEXT NOT NULL DEFAULT 'active', fired_at TEXT, fired_price REAL, fires INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_watch_product ON product_watches(tenant_id, product_id, status);
CREATE INDEX ix_watch_owner ON product_watches(tenant_id, owner);
CREATE TABLE pickup_points (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, code TEXT NOT NULL,
  name TEXT NOT NULL, kind TEXT NOT NULL, address TEXT NOT NULL, city TEXT DEFAULT '', region TEXT DEFAULT '', postcode TEXT DEFAULT '',
  lat REAL, lng REAL, capacity INTEGER NOT NULL DEFAULT 0, hours TEXT DEFAULT '', eta_days INTEGER,
  active INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE UNIQUE INDEX ux_pickup_code ON pickup_points(tenant_id, code);
CREATE TABLE pickup_reservations (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, point_id INTEGER NOT NULL,
  order_id INTEGER NOT NULL, owner TEXT NOT NULL, code TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'reserved',
  hold_until TEXT, ready_at TEXT, collected_at TEXT, closed_at TEXT, attempts INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_pickup_res ON pickup_reservations(tenant_id, point_id, status);
CREATE UNIQUE INDEX ux_pickup_order ON pickup_reservations(tenant_id, order_id);
CREATE TABLE rich_content (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, product_id TEXT NOT NULL,
  seller_id INTEGER, author TEXT DEFAULT '', modules TEXT NOT NULL DEFAULT '[]',
  status TEXT NOT NULL DEFAULT 'draft', version INTEGER NOT NULL DEFAULT 1, review_notes TEXT DEFAULT '',
  submitted_at TEXT, reviewed_at TEXT, reviewed_by TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')), updated_at TEXT
);
CREATE INDEX ix_rich_product ON rich_content(tenant_id, product_id, status);
CREATE TABLE brand_claims (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, brand TEXT NOT NULL,
  seller_id INTEGER, claimant TEXT DEFAULT '', trademark_number TEXT DEFAULT '', trademark_office TEXT DEFAULT '',
  evidence TEXT DEFAULT '[]', status TEXT NOT NULL DEFAULT 'submitted', notes TEXT DEFAULT '',
  reviewed_by TEXT, reviewed_at TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_brand_claims ON brand_claims(tenant_id, brand, status);
CREATE TABLE brand_reports (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, brand TEXT NOT NULL, claim_id INTEGER NOT NULL,
  kind TEXT NOT NULL, product_id TEXT, offer_id INTEGER, seller_id INTEGER, details TEXT DEFAULT '',
  status TEXT NOT NULL DEFAULT 'open', outcome TEXT DEFAULT '', reviewed_by TEXT, reviewed_at TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_brand_reports ON brand_reports(tenant_id, brand, status);
CREATE TABLE option_groups (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, code TEXT NOT NULL, name TEXT NOT NULL, kind TEXT NOT NULL,
  min_select INTEGER NOT NULL DEFAULT 0, max_select INTEGER NOT NULL DEFAULT 1, max_length INTEGER, position INTEGER NOT NULL DEFAULT 0,
  active INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE UNIQUE INDEX ux_option_group ON option_groups(tenant_id, code);
CREATE TABLE option_values (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, group_id INTEGER NOT NULL, code TEXT NOT NULL, name TEXT NOT NULL,
  price_delta REAL NOT NULL DEFAULT 0, position INTEGER NOT NULL DEFAULT 0, active INTEGER NOT NULL DEFAULT 1, extra TEXT NOT NULL DEFAULT '{}'
);
CREATE UNIQUE INDEX ux_option_value ON option_values(group_id, code);
CREATE TABLE option_follow_ups (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, order_id INTEGER NOT NULL, product_id TEXT NOT NULL,
  owner TEXT NOT NULL, group_code TEXT NOT NULL, value_code TEXT NOT NULL DEFAULT '', kind TEXT NOT NULL, detail TEXT NOT NULL DEFAULT '',
  scheduled_for TEXT, ends_at TEXT, proof_url TEXT NOT NULL DEFAULT '', note TEXT NOT NULL DEFAULT '', rounds INTEGER NOT NULL DEFAULT 0, status TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')), decided_at TEXT
);
CREATE INDEX ix_option_follow_ups ON option_follow_ups(tenant_id, order_id);
CREATE TABLE cases (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, kind TEXT NOT NULL, subject_type TEXT NOT NULL DEFAULT '', subject_id TEXT,
  owner TEXT NOT NULL, fields TEXT NOT NULL DEFAULT '{}', docs TEXT NOT NULL DEFAULT '[]', status TEXT NOT NULL, amount REAL, valid_until TEXT,
  used_order INTEGER, decided_by TEXT NOT NULL DEFAULT '', reason TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL DEFAULT (datetime('now')), decided_at TEXT
);
CREATE INDEX ix_cases ON cases(tenant_id, kind, owner);
CREATE TABLE order_charge_rules (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, code TEXT NOT NULL, name TEXT NOT NULL, amount REAL NOT NULL DEFAULT 0, percent REAL NOT NULL DEFAULT 0,
  below_amount REAL, from_hour INTEGER, to_hour INTEGER, waive_for_members INTEGER NOT NULL DEFAULT 0, waive_with_free_shipping INTEGER NOT NULL DEFAULT 0,
  taxable INTEGER NOT NULL DEFAULT 0, active INTEGER NOT NULL DEFAULT 1, position INTEGER NOT NULL DEFAULT 0, UNIQUE(tenant_id, code)
);
CREATE TABLE bag_tips (tenant_id INTEGER NOT NULL, owner TEXT NOT NULL, amount REAL NOT NULL, PRIMARY KEY (tenant_id, owner));
CREATE TABLE media_sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, subject_type TEXT NOT NULL, subject_id TEXT NOT NULL, guest TEXT NOT NULL, host TEXT NOT NULL DEFAULT '',
  mode TEXT NOT NULL DEFAULT '', transport TEXT NOT NULL DEFAULT '', room TEXT NOT NULL, rate REAL NOT NULL DEFAULT 0, status TEXT NOT NULL,
  started_at TEXT, ended_at TEXT, seconds INTEGER NOT NULL DEFAULT 0, charged REAL NOT NULL DEFAULT 0, shortfall REAL NOT NULL DEFAULT 0, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_media_sessions ON media_sessions(tenant_id, subject_type, subject_id);
CREATE TABLE media_signals (
  id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER NOT NULL, side TEXT NOT NULL, type TEXT NOT NULL, data TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_media_signals ON media_signals(session_id, id);
CREATE TABLE trials (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, order_id INTEGER NOT NULL, product_id TEXT NOT NULL, owner TEXT NOT NULL, qty INTEGER NOT NULL DEFAULT 1,
  unit REAL NOT NULL, deposit REAL NOT NULL DEFAULT 0, charged REAL NOT NULL DEFAULT 0, refunded REAL NOT NULL DEFAULT 0, notified_short INTEGER NOT NULL DEFAULT 0, ends_at TEXT NOT NULL, status TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')), decided_at TEXT
);
CREATE INDEX ix_trials ON trials(tenant_id, owner);
CREATE TABLE deliverables (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, order_id INTEGER NOT NULL, product_id TEXT NOT NULL, owner TEXT NOT NULL, kind TEXT NOT NULL,
  value TEXT, status TEXT NOT NULL, steps_total INTEGER NOT NULL DEFAULT 0, steps_done INTEGER NOT NULL DEFAULT 0, delivered_at TEXT, delivered_by TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_deliverables ON deliverables(tenant_id, owner);
CREATE TABLE deliverable_pool (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, product_id TEXT NOT NULL, code TEXT NOT NULL, taken_by INTEGER, UNIQUE(tenant_id, product_id, code)
);
CREATE TABLE vault_records (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, owner TEXT NOT NULL, title TEXT NOT NULL, url TEXT NOT NULL, kind TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE vault_shares (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, owner TEXT NOT NULL, what TEXT NOT NULL, ref INTEGER NOT NULL, party TEXT NOT NULL, until TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE product_option_groups (
  tenant_id INTEGER NOT NULL, product_id TEXT NOT NULL, group_id INTEGER NOT NULL, position INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (tenant_id, product_id, group_id)
);
CREATE TABLE booking_resources (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, code TEXT NOT NULL, name TEXT NOT NULL, kind TEXT NOT NULL,
  capacity INTEGER NOT NULL DEFAULT 1, tz TEXT, hours TEXT NOT NULL DEFAULT '{}', active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE UNIQUE INDEX ux_booking_resource ON booking_resources(tenant_id, code);
CREATE TABLE product_bookings (
  tenant_id INTEGER NOT NULL, product_id TEXT NOT NULL, mode TEXT NOT NULL, resource_ids TEXT NOT NULL DEFAULT '[]',
  duration_min INTEGER NOT NULL DEFAULT 60, step_min INTEGER NOT NULL DEFAULT 60, buffer_min INTEGER NOT NULL DEFAULT 0,
  lead_hours INTEGER NOT NULL DEFAULT 0, horizon_days INTEGER NOT NULL DEFAULT 365, min_units INTEGER NOT NULL DEFAULT 1, max_units INTEGER NOT NULL DEFAULT 30,
  PRIMARY KEY (tenant_id, product_id)
);
CREATE TABLE bookings (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT NOT NULL, product_id TEXT NOT NULL, resource_id INTEGER NOT NULL,
  owner TEXT NOT NULL, starts_at TEXT NOT NULL, ends_at TEXT NOT NULL, units INTEGER NOT NULL DEFAULT 1, qty INTEGER NOT NULL DEFAULT 1,
  status TEXT NOT NULL DEFAULT 'held', hold_until TEXT, order_id INTEGER, confirmed_at TEXT, closed_at TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_bookings_resource ON bookings(tenant_id, resource_id, starts_at);
CREATE INDEX ix_bookings_owner ON bookings(tenant_id, owner);
CREATE TABLE price_offers (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, product_id TEXT NOT NULL, owner TEXT NOT NULL, seller TEXT NOT NULL DEFAULT '',
  qty INTEGER NOT NULL DEFAULT 1, amount REAL NOT NULL, counter_amount REAL, note TEXT DEFAULT '', status TEXT NOT NULL DEFAULT 'open',
  history TEXT NOT NULL DEFAULT '[]', expires_at TEXT, decided_at TEXT, order_id INTEGER, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_price_offers ON price_offers(tenant_id, product_id, status);
CREATE INDEX ix_price_offers_owner ON price_offers(tenant_id, owner);
CREATE TABLE auctions (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, product_id TEXT NOT NULL, seller TEXT NOT NULL DEFAULT '',
  start_price REAL NOT NULL, reserve_price REAL, buy_now_price REAL, current_price REAL, leader TEXT, leader_max REAL,
  bids INTEGER NOT NULL DEFAULT 0, starts_at TEXT NOT NULL, ends_at TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'scheduled',
  winner TEXT, final_price REAL, pay_by TEXT, order_id INTEGER, closed_at TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_auctions ON auctions(tenant_id, status, ends_at);
CREATE TABLE auction_bids (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, auction_id INTEGER NOT NULL, owner TEXT NOT NULL,
  max_amount REAL NOT NULL, at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_auction_bids ON auction_bids(auction_id, max_amount);
CREATE TABLE peer_listings (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, owner TEXT NOT NULL, owner_name TEXT DEFAULT '', seller_id INTEGER, product_id TEXT,
  title TEXT NOT NULL, description TEXT DEFAULT '', price REAL NOT NULL, qty INTEGER NOT NULL DEFAULT 1, sold INTEGER NOT NULL DEFAULT 0,
  condition TEXT, dept TEXT, images TEXT NOT NULL DEFAULT '[]', status TEXT NOT NULL DEFAULT 'draft', review_notes TEXT DEFAULT '',
  published_at TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')), updated_at TEXT
);
CREATE INDEX ix_peer_listings ON peer_listings(tenant_id, status);
CREATE INDEX ix_peer_listings_owner ON peer_listings(tenant_id, owner);
CREATE TABLE peer_earnings (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, listing_id INTEGER NOT NULL, owner TEXT NOT NULL, order_id INTEGER NOT NULL,
  gross REAL NOT NULL, commission REAL NOT NULL, net REAL NOT NULL, currency TEXT, status TEXT NOT NULL DEFAULT 'pending',
  release_at TEXT, credited_at TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_peer_earnings ON peer_earnings(tenant_id, status, release_at);
CREATE TABLE conversations (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, subject_kind TEXT NOT NULL, subject_ref TEXT NOT NULL,
  buyer TEXT NOT NULL, counterpart TEXT NOT NULL DEFAULT '', title TEXT DEFAULT '', status TEXT NOT NULL DEFAULT 'open',
  last_at TEXT NOT NULL DEFAULT (datetime('now')), created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_conversations ON conversations(tenant_id, buyer);
CREATE INDEX ix_conversations_cp ON conversations(tenant_id, counterpart);
CREATE TABLE conversation_messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, conversation_id INTEGER NOT NULL, sender TEXT NOT NULL, side TEXT NOT NULL,
  body TEXT NOT NULL, hidden INTEGER NOT NULL DEFAULT 0, read_by_other INTEGER NOT NULL DEFAULT 0, at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_conversation_messages ON conversation_messages(conversation_id, id);
CREATE TABLE group_campaigns (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, product_id TEXT NOT NULL, title TEXT DEFAULT '', group_price REAL NOT NULL,
  min_members INTEGER NOT NULL, max_members INTEGER, ends_at TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'open', closed_at TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_group_campaigns ON group_campaigns(tenant_id, status, ends_at);
CREATE TABLE group_members (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, campaign_id INTEGER NOT NULL, owner TEXT NOT NULL, order_id INTEGER NOT NULL,
  qty INTEGER NOT NULL DEFAULT 1, paid REAL NOT NULL DEFAULT 0, refunded INTEGER NOT NULL DEFAULT 0, joined_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_group_members ON group_members(campaign_id);
CREATE TABLE order_substitutions (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, order_id INTEGER NOT NULL, product_id TEXT NOT NULL, substitute_id TEXT,
  qty INTEGER NOT NULL DEFAULT 1, original_unit REAL NOT NULL DEFAULT 0, substitute_unit REAL, refund REAL NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'proposed', decided_at TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_order_substitutions ON order_substitutions(tenant_id, order_id);
CREATE TABLE invoice_documents (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  ref TEXT, order_id INTEGER, owner TEXT,
  doc_kind TEXT NOT NULL, invoice_number TEXT,
  place_of_supply TEXT, gstin TEXT, pan TEXT,
  taxable REAL, tax REAL, total REAL, currency TEXT,
  body TEXT, rendered TEXT, status TEXT NOT NULL DEFAULT 'generated',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_invoicedocs_tenant ON invoice_documents(tenant_id, order_id, doc_kind);
CREATE TABLE platform_capabilities (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  key TEXT NOT NULL UNIQUE,            /* buy_box, trade_assurance, qr_pay … */
  label TEXT NOT NULL,                 /* "Buy-box competition" */
  domain TEXT NOT NULL,                /* marketplace | fintech | qc | trade */
  icon TEXT,                           /* for the console */
  description TEXT,
  params TEXT NOT NULL DEFAULT '{}',   /* the tunables, each {type,default,...} */
  sections TEXT NOT NULL DEFAULT '[]',  /* the store console leaves this atom lights */
  enabled INTEGER DEFAULT 1,           /* platform-level switch */
  position INTEGER DEFAULT 0,
  seeded_from TEXT,                     /* self-heal marker, never clobbers an edit */
  edited INTEGER DEFAULT 0,             /* 1 once an operator owns this row */
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_pcap_domain ON platform_capabilities(domain, enabled);
CREATE TABLE capability_values (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  capability TEXT NOT NULL,
  enabled INTEGER DEFAULT 1,
  params TEXT NOT NULL DEFAULT '{}',   /* overrides merged onto the defaults */
  notes TEXT,
  UNIQUE(tenant_id, capability)
);
CREATE INDEX ix_capvals_tenant ON capability_values(tenant_id, capability);
CREATE TABLE capability_presets (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  key TEXT NOT NULL UNIQUE,
  label TEXT NOT NULL,
  description TEXT,
  capabilities TEXT NOT NULL DEFAULT '{}',  /* {key: {enabled, params}} */
  universes TEXT,                           /* JSON [universe key] a new store opens with; NULL = none declared */
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX ix_cappreset_key ON capability_presets(key);
CREATE TABLE capability_preset_assignments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  preset_key TEXT NOT NULL,
  UNIQUE(tenant_id, preset_key)
);
CREATE TABLE platform_branding (
  id INTEGER PRIMARY KEY,
  name TEXT, logo TEXT, tagline TEXT,
  colors TEXT NOT NULL DEFAULT '{}', fonts TEXT NOT NULL DEFAULT '{}',
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE store_branding (
  tenant_id INTEGER PRIMARY KEY,
  name TEXT, logo TEXT, tagline TEXT,
  colors TEXT NOT NULL DEFAULT '{}', fonts TEXT NOT NULL DEFAULT '{}',
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE store_branding_perms (
  tenant_id INTEGER PRIMARY KEY,
  can_change_name INTEGER NOT NULL DEFAULT 0,
  can_change_logo INTEGER NOT NULL DEFAULT 0,
  can_change_colors INTEGER NOT NULL DEFAULT 0,
  can_change_fonts INTEGER NOT NULL DEFAULT 0,
  can_change_footer INTEGER NOT NULL DEFAULT 0,
  can_change_nav INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE drivers (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  name TEXT NOT NULL, email TEXT, phone TEXT, city TEXT DEFAULT '',
  vehicle_kind TEXT NOT NULL DEFAULT 'car',   /* car | suv | bike | auto | van */
  plate TEXT DEFAULT '', license TEXT DEFAULT '',
  status TEXT NOT NULL DEFAULT 'offline',      /* offline | online | busy | suspended */
  rating REAL NOT NULL DEFAULT 5.0, rides_completed INTEGER NOT NULL DEFAULT 0,
  rides_cancelled INTEGER NOT NULL DEFAULT 0, earnings REAL NOT NULL DEFAULT 0,
  city_latency REAL DEFAULT 0,                  /* last reported distance from the city centre, km */
  joined_at TEXT NOT NULL DEFAULT (datetime('now')),
  deactivated_at TEXT, uid TEXT,
  UNIQUE (tenant_id, email)
);
CREATE INDEX ix_drivers ON drivers(tenant_id, status, vehicle_kind);
CREATE TABLE rides (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  ref TEXT NOT NULL UNIQUE,
  rider TEXT, rider_phone TEXT,
  pickup TEXT NOT NULL, dropoff TEXT NOT NULL,
  pickup_lat REAL, pickup_lng REAL, dropoff_lat REAL, dropoff_lng REAL,
  vehicle_kind TEXT NOT NULL DEFAULT 'car', driver_id INTEGER,
  status TEXT NOT NULL DEFAULT 'requested',     /* requested → accepted → arrived → trip_start → completed | cancelled */
  fare REAL DEFAULT 0, surge REAL NOT NULL DEFAULT 1.0,
  distance_km REAL DEFAULT 0, duration_min REAL DEFAULT 0, eta_min REAL DEFAULT 0,
  payment_method TEXT DEFAULT 'cash',           /* cash | wallet | card | upi */
  rating INTEGER, note TEXT DEFAULT '',
  requested_at TEXT NOT NULL DEFAULT (datetime('now')),
  accepted_at TEXT, arrived_at TEXT, started_at TEXT, completed_at TEXT, cancelled_at TEXT
, uid TEXT);
CREATE INDEX ix_rides ON rides(tenant_id, status, requested_at);
CREATE INDEX ix_rides_driver ON rides(driver_id, status);
CREATE TABLE ride_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ride_id INTEGER NOT NULL,
  status TEXT NOT NULL, note TEXT DEFAULT '', at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE INDEX ix_ride_events ON ride_events(ride_id, at);
CREATE TABLE surge_zones (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  name TEXT NOT NULL, kind TEXT NOT NULL DEFAULT 'geofence',  /* geofence | event | weather */
  multiplier REAL NOT NULL DEFAULT 1.0,
  center_lat REAL, center_lng REAL, radius_km REAL DEFAULT 3,
  active INTEGER NOT NULL DEFAULT 1,
  starts_at TEXT, ends_at TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE INDEX ix_surge ON surge_zones(tenant_id, active);
CREATE TABLE vehicles (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  plate TEXT NOT NULL, kind TEXT NOT NULL DEFAULT 'car',
  capacity INTEGER NOT NULL DEFAULT 4,
  status TEXT NOT NULL DEFAULT 'active',         /* active | maintenance | retired */
  odometer REAL DEFAULT 0, insurance_until TEXT,
  driver_id INTEGER,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE INDEX ix_vehicles ON vehicles(tenant_id, status, kind);
CREATE TABLE employees (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  code TEXT NOT NULL, name TEXT NOT NULL, email TEXT,
  department TEXT DEFAULT '', designation TEXT DEFAULT '',
  status TEXT NOT NULL DEFAULT 'active',     /* active | on_leave | terminated */
  joined_at TEXT NOT NULL DEFAULT (datetime('now')), exited_at TEXT,
  base_salary REAL NOT NULL DEFAULT 0, pay_frequency TEXT NOT NULL DEFAULT 'monthly',
  bank_account TEXT DEFAULT '', tax_id TEXT DEFAULT '',
  manager_id INTEGER, uid TEXT,
  UNIQUE (tenant_id, code)
);
CREATE INDEX ix_employees ON employees(tenant_id, status, department);
CREATE TABLE attendance (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, employee_id INTEGER NOT NULL,
  date TEXT NOT NULL, check_in TEXT, check_out TEXT,
  status TEXT NOT NULL DEFAULT 'present',     /* present | late | half_day | absent | leave */
  hours REAL DEFAULT 0, note TEXT DEFAULT '', uid TEXT,
  UNIQUE (tenant_id, employee_id, date)
);
CREATE INDEX ix_attendance ON attendance(tenant_id, date, status);
CREATE TABLE payroll_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  period TEXT NOT NULL,                       /* e.g. 2026-10 */
  status TEXT NOT NULL DEFAULT 'draft',       /* draft | approved | paid */
  gross REAL NOT NULL DEFAULT 0, deductions REAL NOT NULL DEFAULT 0, net REAL NOT NULL DEFAULT 0,
  headcount INTEGER NOT NULL DEFAULT 0,
  run_at TEXT NOT NULL DEFAULT (datetime('now')), approved_at TEXT, paid_at TEXT, uid TEXT,
  UNIQUE (tenant_id, period)
);
CREATE TABLE payroll_lines (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, run_id INTEGER NOT NULL,
  employee_id INTEGER NOT NULL, employee_code TEXT, employee_name TEXT,
  base REAL NOT NULL DEFAULT 0, overtime REAL NOT NULL DEFAULT 0,
  deductions REAL NOT NULL DEFAULT 0, tax REAL NOT NULL DEFAULT 0, net REAL NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'pending', uid TEXT,     /* pending | paid */
  UNIQUE (run_id, employee_id)
);
CREATE INDEX ix_payroll_lines ON payroll_lines(run_id);
CREATE TABLE purchase_requests (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  ref TEXT NOT NULL UNIQUE,
  requested_by TEXT, department TEXT DEFAULT '',
  status TEXT NOT NULL DEFAULT 'draft',       /* draft → submitted → approved → ordered → received | rejected */
  note TEXT DEFAULT '',
  required_by TEXT, approved_by TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')), approved_at TEXT
, uid TEXT);
CREATE INDEX ix_pr ON purchase_requests(tenant_id, status);
CREATE TABLE purchase_request_lines (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, request_id INTEGER NOT NULL,
  item TEXT NOT NULL, qty INTEGER NOT NULL DEFAULT 1, unit TEXT DEFAULT 'ea',
  est_unit_cost REAL NOT NULL DEFAULT 0, note TEXT DEFAULT ''
, uid TEXT);
CREATE INDEX ix_prl ON purchase_request_lines(request_id);
CREATE TABLE work_orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  ref TEXT NOT NULL UNIQUE,
  product_id TEXT, sku_id INTEGER,
  qty INTEGER NOT NULL DEFAULT 1, completed_qty INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'planned',     /* planned → released → in_progress → done | scrapped */
  bom TEXT DEFAULT '{}',                        /* the bill of materials, data not code */
  unit_cost REAL NOT NULL DEFAULT 0,
  planned_start TEXT, planned_end TEXT,
  started_at TEXT, completed_at TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE INDEX ix_wo ON work_orders(tenant_id, status);
CREATE TABLE projects (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  code TEXT NOT NULL, name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'planning',    /* planning | active | on_hold | done | cancelled */
  owner TEXT, client TEXT DEFAULT '',
  budget REAL NOT NULL DEFAULT 0, spent REAL NOT NULL DEFAULT 0,
  start_date TEXT, due_date TEXT, completed_at TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')), uid TEXT,
  UNIQUE (tenant_id, code)
);
CREATE INDEX ix_projects ON projects(tenant_id, status);
CREATE TABLE tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, project_id INTEGER,
  title TEXT NOT NULL, description TEXT DEFAULT '',
  assignee TEXT, status TEXT NOT NULL DEFAULT 'todo',    /* todo | in_progress | review | done */
  priority TEXT NOT NULL DEFAULT 'normal',              /* low | normal | high | urgent */
  estimate_hours REAL DEFAULT 0, logged_hours REAL DEFAULT 0,
  due_date TEXT, completed_at TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE INDEX ix_tasks ON tasks(tenant_id, project_id, status);
CREATE TABLE approvals (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  kind TEXT NOT NULL,                          /* purchase_request | work_order | payroll | custom */
  ref_id INTEGER NOT NULL, ref TEXT DEFAULT '',
  requester TEXT, approver TEXT,
  status TEXT NOT NULL DEFAULT 'pending',      /* pending | approved | rejected */
  level INTEGER NOT NULL DEFAULT 1,
  note TEXT DEFAULT '',
  decided_at TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE INDEX ix_approvals ON approvals(tenant_id, status, kind);
CREATE UNIQUE INDEX ux_composition_key ON composition_ledger(key);
CREATE INDEX ix_products_source_global ON products(tenant_id, source_global_id);
CREATE TRIGGER ledger_journals_no_update BEFORE UPDATE ON ledger_journals BEGIN SELECT RAISE(ABORT, 'posted ledger records are immutable'); END;
CREATE TRIGGER ledger_journals_no_delete BEFORE DELETE ON ledger_journals BEGIN SELECT RAISE(ABORT, 'posted ledger records are immutable'); END;
CREATE TRIGGER ledger_postings_no_update BEFORE UPDATE ON ledger_postings BEGIN SELECT RAISE(ABORT, 'posted ledger records are immutable'); END;
CREATE TRIGGER ledger_postings_no_delete BEFORE DELETE ON ledger_postings BEGIN SELECT RAISE(ABORT, 'posted ledger records are immutable'); END;
CREATE TABLE password_resets (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, user_id INTEGER NOT NULL,
  token_hash TEXT NOT NULL UNIQUE, expires_at INTEGER NOT NULL, used_at TEXT, ip TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX ix_pwreset_user ON password_resets(user_id, created_at);
CREATE INDEX ix_payments_ref ON payments(gateway, txn_ref);
CREATE UNIQUE INDEX ux_tenants_uid ON tenants(uid);
CREATE TRIGGER trg_tenants_uid AFTER INSERT ON tenants
               BEGIN UPDATE tenants SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_plans_uid ON plans(uid);
CREATE TRIGGER trg_plans_uid AFTER INSERT ON plans
               BEGIN UPDATE plans SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_subscriptions_uid ON subscriptions(uid);
CREATE TRIGGER trg_subscriptions_uid AFTER INSERT ON subscriptions
               BEGIN UPDATE subscriptions SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_invoices_uid ON invoices(uid);
CREATE TRIGGER trg_invoices_uid AFTER INSERT ON invoices
               BEGIN UPDATE invoices SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_audit_log_uid ON audit_log(uid);
CREATE TRIGGER trg_audit_log_uid AFTER INSERT ON audit_log
               BEGIN UPDATE audit_log SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_platform_admins_uid ON platform_admins(uid);
CREATE TRIGGER trg_platform_admins_uid AFTER INSERT ON platform_admins
               BEGIN UPDATE platform_admins SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_platform_sessions_uid ON platform_sessions(uid);
CREATE TRIGGER trg_platform_sessions_uid AFTER INSERT ON platform_sessions
               BEGIN UPDATE platform_sessions SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_tokens_uid ON tokens(uid);
CREATE TRIGGER trg_tokens_uid AFTER INSERT ON tokens
               BEGIN UPDATE tokens SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_users_uid ON users(uid);
CREATE TRIGGER trg_users_uid AFTER INSERT ON users
               BEGIN UPDATE users SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_sessions_uid ON sessions(uid);
CREATE TRIGGER trg_sessions_uid AFTER INSERT ON sessions
               BEGIN UPDATE sessions SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_tenant_state_uid ON tenant_state(uid);
CREATE TRIGGER trg_tenant_state_uid AFTER INSERT ON tenant_state
               BEGIN UPDATE tenant_state SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_products_uid ON products(uid);
CREATE TRIGGER trg_products_uid AFTER INSERT ON products
               BEGIN UPDATE products SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_product_bullets_uid ON product_bullets(uid);
CREATE TRIGGER trg_product_bullets_uid AFTER INSERT ON product_bullets
               BEGIN UPDATE product_bullets SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_cart_items_uid ON cart_items(uid);
CREATE TRIGGER trg_cart_items_uid AFTER INSERT ON cart_items
               BEGIN UPDATE cart_items SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_saved_items_uid ON saved_items(uid);
CREATE TRIGGER trg_saved_items_uid AFTER INSERT ON saved_items
               BEGIN UPDATE saved_items SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_orders_uid ON orders(uid);
CREATE TRIGGER trg_orders_uid AFTER INSERT ON orders
               BEGIN UPDATE orders SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_order_items_uid ON order_items(uid);
CREATE TRIGGER trg_order_items_uid AFTER INSERT ON order_items
               BEGIN UPDATE order_items SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_reviews_uid ON reviews(uid);
CREATE TRIGGER trg_reviews_uid AFTER INSERT ON reviews
               BEGIN UPDATE reviews SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_view_history_uid ON view_history(uid);
CREATE TRIGGER trg_view_history_uid AFTER INSERT ON view_history
               BEGIN UPDATE view_history SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_settings_uid ON settings(uid);
CREATE TRIGGER trg_settings_uid AFTER INSERT ON settings
               BEGIN UPDATE settings SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_departments_uid ON departments(uid);
CREATE TRIGGER trg_departments_uid AFTER INSERT ON departments
               BEGIN UPDATE departments SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_home_banners_uid ON home_banners(uid);
CREATE TRIGGER trg_home_banners_uid AFTER INSERT ON home_banners
               BEGIN UPDATE home_banners SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_home_cards_uid ON home_cards(uid);
CREATE TRIGGER trg_home_cards_uid AFTER INSERT ON home_cards
               BEGIN UPDATE home_cards SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_skus_uid ON skus(uid);
CREATE TRIGGER trg_skus_uid AFTER INSERT ON skus
               BEGIN UPDATE skus SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_inventory_uid ON inventory(uid);
CREATE TRIGGER trg_inventory_uid AFTER INSERT ON inventory
               BEGIN UPDATE inventory SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_warehouses_uid ON warehouses(uid);
CREATE TRIGGER trg_warehouses_uid AFTER INSERT ON warehouses
               BEGIN UPDATE warehouses SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_entity_defs_uid ON entity_defs(uid);
CREATE TRIGGER trg_entity_defs_uid AFTER INSERT ON entity_defs
               BEGIN UPDATE entity_defs SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_entity_data_uid ON entity_data(uid);
CREATE TRIGGER trg_entity_data_uid AFTER INSERT ON entity_data
               BEGIN UPDATE entity_data SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_countries_uid ON countries(uid);
CREATE TRIGGER trg_countries_uid AFTER INSERT ON countries
               BEGIN UPDATE countries SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_tax_modes_uid ON tax_modes(uid);
CREATE TRIGGER trg_tax_modes_uid AFTER INSERT ON tax_modes
               BEGIN UPDATE tax_modes SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_currencies_uid ON currencies(uid);
CREATE TRIGGER trg_currencies_uid AFTER INSERT ON currencies
               BEGIN UPDATE currencies SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_provider_defs_uid ON provider_defs(uid);
CREATE TRIGGER trg_provider_defs_uid AFTER INSERT ON provider_defs
               BEGIN UPDATE provider_defs SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_provider_availability_uid ON provider_availability(uid);
CREATE TRIGGER trg_provider_availability_uid AFTER INSERT ON provider_availability
               BEGIN UPDATE provider_availability SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_meta_lists_uid ON meta_lists(uid);
CREATE TRIGGER trg_meta_lists_uid AFTER INSERT ON meta_lists
               BEGIN UPDATE meta_lists SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_tenant_gateways_uid ON tenant_gateways(uid);
CREATE TRIGGER trg_tenant_gateways_uid AFTER INSERT ON tenant_gateways
               BEGIN UPDATE tenant_gateways SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_custom_providers_uid ON custom_providers(uid);
CREATE TRIGGER trg_custom_providers_uid AFTER INSERT ON custom_providers
               BEGIN UPDATE custom_providers SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_payments_uid ON payments(uid);
CREATE TRIGGER trg_payments_uid AFTER INSERT ON payments
               BEGIN UPDATE payments SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_fx_rates_uid ON fx_rates(uid);
CREATE TRIGGER trg_fx_rates_uid AFTER INSERT ON fx_rates
               BEGIN UPDATE fx_rates SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_platform_settings_uid ON platform_settings(uid);
CREATE TRIGGER trg_platform_settings_uid AFTER INSERT ON platform_settings
               BEGIN UPDATE platform_settings SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_links_uid ON links(uid);
CREATE TRIGGER trg_links_uid AFTER INSERT ON links
               BEGIN UPDATE links SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_context_types_uid ON context_types(uid);
CREATE TRIGGER trg_context_types_uid AFTER INSERT ON context_types
               BEGIN UPDATE context_types SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_modules_uid ON modules(uid);
CREATE TRIGGER trg_modules_uid AFTER INSERT ON modules
               BEGIN UPDATE modules SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_tenant_modules_uid ON tenant_modules(uid);
CREATE TRIGGER trg_tenant_modules_uid AFTER INSERT ON tenant_modules
               BEGIN UPDATE tenant_modules SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_wallets_uid ON wallets(uid);
CREATE TRIGGER trg_wallets_uid AFTER INSERT ON wallets
               BEGIN UPDATE wallets SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_serialized_items_uid ON serialized_items(uid);
CREATE TRIGGER trg_serialized_items_uid AFTER INSERT ON serialized_items
               BEGIN UPDATE serialized_items SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_variant_groups_uid ON variant_groups(uid);
CREATE TRIGGER trg_variant_groups_uid AFTER INSERT ON variant_groups
               BEGIN UPDATE variant_groups SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_compliance_records_uid ON compliance_records(uid);
CREATE TRIGGER trg_compliance_records_uid AFTER INSERT ON compliance_records
               BEGIN UPDATE compliance_records SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_suppliers_uid ON suppliers(uid);
CREATE TRIGGER trg_suppliers_uid AFTER INSERT ON suppliers
               BEGIN UPDATE suppliers SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_product_suppliers_uid ON product_suppliers(uid);
CREATE TRIGGER trg_product_suppliers_uid AFTER INSERT ON product_suppliers
               BEGIN UPDATE product_suppliers SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_localizations_uid ON localizations(uid);
CREATE TRIGGER trg_localizations_uid AFTER INSERT ON localizations
               BEGIN UPDATE localizations SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_contracts_uid ON contracts(uid);
CREATE TRIGGER trg_contracts_uid AFTER INSERT ON contracts
               BEGIN UPDATE contracts SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_tenders_uid ON tenders(uid);
CREATE TRIGGER trg_tenders_uid AFTER INSERT ON tenders
               BEGIN UPDATE tenders SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_ai_usage_uid ON ai_usage(uid);
CREATE TRIGGER trg_ai_usage_uid AFTER INSERT ON ai_usage
               BEGIN UPDATE ai_usage SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_ai_tasks_uid ON ai_tasks(uid);
CREATE TRIGGER trg_ai_tasks_uid AFTER INSERT ON ai_tasks
               BEGIN UPDATE ai_tasks SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_offers_uid ON offers(uid);
CREATE TRIGGER trg_offers_uid AFTER INSERT ON offers
               BEGIN UPDATE offers SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_coupons_uid ON coupons(uid);
CREATE TRIGGER trg_coupons_uid AFTER INSERT ON coupons
               BEGIN UPDATE coupons SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_coupon_redemptions_uid ON coupon_redemptions(uid);
CREATE TRIGGER trg_coupon_redemptions_uid AFTER INSERT ON coupon_redemptions
               BEGIN UPDATE coupon_redemptions SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_wallet_entries_uid ON wallet_entries(uid);
CREATE TRIGGER trg_wallet_entries_uid AFTER INSERT ON wallet_entries
               BEGIN UPDATE wallet_entries SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_invoice_lines_uid ON invoice_lines(uid);
CREATE TRIGGER trg_invoice_lines_uid AFTER INSERT ON invoice_lines
               BEGIN UPDATE invoice_lines SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_usage_records_uid ON usage_records(uid);
CREATE TRIGGER trg_usage_records_uid AFTER INSERT ON usage_records
               BEGIN UPDATE usage_records SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_credit_notes_uid ON credit_notes(uid);
CREATE TRIGGER trg_credit_notes_uid AFTER INSERT ON credit_notes
               BEGIN UPDATE credit_notes SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_billing_events_uid ON billing_events(uid);
CREATE TRIGGER trg_billing_events_uid AFTER INSERT ON billing_events
               BEGIN UPDATE billing_events SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_webhooks_uid ON webhooks(uid);
CREATE TRIGGER trg_webhooks_uid AFTER INSERT ON webhooks
               BEGIN UPDATE webhooks SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_webhook_deliveries_uid ON webhook_deliveries(uid);
CREATE TRIGGER trg_webhook_deliveries_uid AFTER INSERT ON webhook_deliveries
               BEGIN UPDATE webhook_deliveries SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_entity_meta_uid ON entity_meta(uid);
CREATE TRIGGER trg_entity_meta_uid AFTER INSERT ON entity_meta
               BEGIN UPDATE entity_meta SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_idempotency_keys_uid ON idempotency_keys(uid);
CREATE TRIGGER trg_idempotency_keys_uid AFTER INSERT ON idempotency_keys
               BEGIN UPDATE idempotency_keys SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_stock_transfers_uid ON stock_transfers(uid);
CREATE TRIGGER trg_stock_transfers_uid AFTER INSERT ON stock_transfers
               BEGIN UPDATE stock_transfers SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_remittance_records_uid ON remittance_records(uid);
CREATE TRIGGER trg_remittance_records_uid AFTER INSERT ON remittance_records
               BEGIN UPDATE remittance_records SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_inbound_events_uid ON inbound_events(uid);
CREATE TRIGGER trg_inbound_events_uid AFTER INSERT ON inbound_events
               BEGIN UPDATE inbound_events SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_sso_connections_uid ON sso_connections(uid);
CREATE TRIGGER trg_sso_connections_uid AFTER INSERT ON sso_connections
               BEGIN UPDATE sso_connections SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_scim_tokens_uid ON scim_tokens(uid);
CREATE TRIGGER trg_scim_tokens_uid AFTER INSERT ON scim_tokens
               BEGIN UPDATE scim_tokens SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_goip_touchpoints_uid ON goip_touchpoints(uid);
CREATE TRIGGER trg_goip_touchpoints_uid AFTER INSERT ON goip_touchpoints
               BEGIN UPDATE goip_touchpoints SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_goip_budgets_uid ON goip_budgets(uid);
CREATE TRIGGER trg_goip_budgets_uid AFTER INSERT ON goip_budgets
               BEGIN UPDATE goip_budgets SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_goip_settlements_uid ON goip_settlements(uid);
CREATE TRIGGER trg_goip_settlements_uid AFTER INSERT ON goip_settlements
               BEGIN UPDATE goip_settlements SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_goip_entitlements_uid ON goip_entitlements(uid);
CREATE TRIGGER trg_goip_entitlements_uid AFTER INSERT ON goip_entitlements
               BEGIN UPDATE goip_entitlements SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_review_replies_uid ON review_replies(uid);
CREATE TRIGGER trg_review_replies_uid AFTER INSERT ON review_replies
               BEGIN UPDATE review_replies SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_ugc_votes_uid ON ugc_votes(uid);
CREATE TRIGGER trg_ugc_votes_uid AFTER INSERT ON ugc_votes
               BEGIN UPDATE ugc_votes SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_qna_questions_uid ON qna_questions(uid);
CREATE TRIGGER trg_qna_questions_uid AFTER INSERT ON qna_questions
               BEGIN UPDATE qna_questions SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_qna_answers_uid ON qna_answers(uid);
CREATE TRIGGER trg_qna_answers_uid AFTER INSERT ON qna_answers
               BEGIN UPDATE qna_answers SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_tickets_uid ON tickets(uid);
CREATE TRIGGER trg_tickets_uid AFTER INSERT ON tickets
               BEGIN UPDATE tickets SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_ticket_notes_uid ON ticket_notes(uid);
CREATE TRIGGER trg_ticket_notes_uid AFTER INSERT ON ticket_notes
               BEGIN UPDATE ticket_notes SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_addresses_uid ON addresses(uid);
CREATE TRIGGER trg_addresses_uid AFTER INSERT ON addresses
               BEGIN UPDATE addresses SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_recurring_schedules_uid ON recurring_schedules(uid);
CREATE TRIGGER trg_recurring_schedules_uid AFTER INSERT ON recurring_schedules
               BEGIN UPDATE recurring_schedules SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_recurring_cycles_uid ON recurring_cycles(uid);
CREATE TRIGGER trg_recurring_cycles_uid AFTER INSERT ON recurring_cycles
               BEGIN UPDATE recurring_cycles SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_memberships_uid ON memberships(uid);
CREATE TRIGGER trg_memberships_uid AFTER INSERT ON memberships
               BEGIN UPDATE memberships SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_risk_events_uid ON risk_events(uid);
CREATE TRIGGER trg_risk_events_uid AFTER INSERT ON risk_events
               BEGIN UPDATE risk_events SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_risk_blocklist_uid ON risk_blocklist(uid);
CREATE TRIGGER trg_risk_blocklist_uid AFTER INSERT ON risk_blocklist
               BEGIN UPDATE risk_blocklist SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_experiments_uid ON experiments(uid);
CREATE TRIGGER trg_experiments_uid AFTER INSERT ON experiments
               BEGIN UPDATE experiments SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_exp_assignments_uid ON exp_assignments(uid);
CREATE TRIGGER trg_exp_assignments_uid AFTER INSERT ON exp_assignments
               BEGIN UPDATE exp_assignments SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_exp_conversions_uid ON exp_conversions(uid);
CREATE TRIGGER trg_exp_conversions_uid AFTER INSERT ON exp_conversions
               BEGIN UPDATE exp_conversions SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_rides_uid ON rides(uid);
CREATE TRIGGER trg_rides_uid AFTER INSERT ON rides
               BEGIN UPDATE rides SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_ride_events_uid ON ride_events(uid);
CREATE TRIGGER trg_ride_events_uid AFTER INSERT ON ride_events
               BEGIN UPDATE ride_events SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_drivers_uid ON drivers(uid);
CREATE TRIGGER trg_drivers_uid AFTER INSERT ON drivers
               BEGIN UPDATE drivers SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_vehicles_uid ON vehicles(uid);
CREATE TRIGGER trg_vehicles_uid AFTER INSERT ON vehicles
               BEGIN UPDATE vehicles SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_surge_zones_uid ON surge_zones(uid);
CREATE TRIGGER trg_surge_zones_uid AFTER INSERT ON surge_zones
               BEGIN UPDATE surge_zones SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_employees_uid ON employees(uid);
CREATE TRIGGER trg_employees_uid AFTER INSERT ON employees
               BEGIN UPDATE employees SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_attendance_uid ON attendance(uid);
CREATE TRIGGER trg_attendance_uid AFTER INSERT ON attendance
               BEGIN UPDATE attendance SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_payroll_runs_uid ON payroll_runs(uid);
CREATE TRIGGER trg_payroll_runs_uid AFTER INSERT ON payroll_runs
               BEGIN UPDATE payroll_runs SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_payroll_lines_uid ON payroll_lines(uid);
CREATE TRIGGER trg_payroll_lines_uid AFTER INSERT ON payroll_lines
               BEGIN UPDATE payroll_lines SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_purchase_requests_uid ON purchase_requests(uid);
CREATE TRIGGER trg_purchase_requests_uid AFTER INSERT ON purchase_requests
               BEGIN UPDATE purchase_requests SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_purchase_request_lines_uid ON purchase_request_lines(uid);
CREATE TRIGGER trg_purchase_request_lines_uid AFTER INSERT ON purchase_request_lines
               BEGIN UPDATE purchase_request_lines SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_work_orders_uid ON work_orders(uid);
CREATE TRIGGER trg_work_orders_uid AFTER INSERT ON work_orders
               BEGIN UPDATE work_orders SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_projects_uid ON projects(uid);
CREATE TRIGGER trg_projects_uid AFTER INSERT ON projects
               BEGIN UPDATE projects SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_tasks_uid ON tasks(uid);
CREATE TRIGGER trg_tasks_uid AFTER INSERT ON tasks
               BEGIN UPDATE tasks SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_approvals_uid ON approvals(uid);
CREATE TRIGGER trg_approvals_uid AFTER INSERT ON approvals
               BEGIN UPDATE approvals SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE TABLE k_events (
    seq INTEGER PRIMARY KEY AUTOINCREMENT, at TEXT NOT NULL, type TEXT NOT NULL,
    namespace TEXT NOT NULL, subject TEXT, actor TEXT, payload TEXT NOT NULL DEFAULT '{}',
    prev_hash TEXT NOT NULL, hash TEXT NOT NULL);
CREATE INDEX ix_k_events_subject ON k_events(subject, seq);
CREATE INDEX ix_k_events_at ON k_events(at);
CREATE TABLE k_kinds (
    id INTEGER PRIMARY KEY AUTOINCREMENT, namespace TEXT NOT NULL, kind TEXT NOT NULL,
    owner TEXT NOT NULL, spec TEXT NOT NULL, rec_from INTEGER NOT NULL, rec_to INTEGER, scope TEXT);
CREATE INDEX ix_k_kinds ON k_kinds(namespace, kind, rec_to);
CREATE TABLE k_nodes (
    uid TEXT PRIMARY KEY, namespace TEXT NOT NULL, kind TEXT NOT NULL, rec_from INTEGER NOT NULL, scope TEXT);
CREATE INDEX ix_k_nodes_kind ON k_nodes(namespace, kind);
CREATE TABLE k_identifiers (
    id INTEGER PRIMARY KEY AUTOINCREMENT, node TEXT NOT NULL, scheme TEXT NOT NULL, value TEXT NOT NULL,
    valid_from TEXT NOT NULL, valid_to TEXT, rec_from INTEGER NOT NULL, rec_to INTEGER);
CREATE INDEX ix_k_ident_value ON k_identifiers(scheme, value, rec_to);
CREATE INDEX ix_k_ident_node ON k_identifiers(node, rec_to);
CREATE TABLE k_hierarchies (
    id INTEGER PRIMARY KEY AUTOINCREMENT, namespace TEXT NOT NULL, hierarchy TEXT NOT NULL,
    owner TEXT NOT NULL, spec TEXT NOT NULL, rec_from INTEGER NOT NULL, rec_to INTEGER, scope TEXT);
CREATE INDEX ix_k_hier ON k_hierarchies(namespace, hierarchy, rec_to);
CREATE TABLE k_placements (
    id INTEGER PRIMARY KEY AUTOINCREMENT, hierarchy TEXT NOT NULL, node TEXT NOT NULL, parent TEXT,
    valid_from TEXT NOT NULL, valid_to TEXT, rec_from INTEGER NOT NULL, rec_to INTEGER);
CREATE INDEX ix_k_place_parent ON k_placements(hierarchy, parent, rec_to);
CREATE INDEX ix_k_place_node ON k_placements(hierarchy, node, rec_to);
CREATE TABLE k_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, node TEXT NOT NULL, attrs TEXT NOT NULL,
    valid_from TEXT NOT NULL, valid_to TEXT, rec_from INTEGER NOT NULL, rec_to INTEGER);
CREATE INDEX ix_k_versions ON k_versions(node, rec_to, valid_from);
CREATE TABLE k_node_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT, node TEXT NOT NULL, state TEXT NOT NULL, rec_from INTEGER NOT NULL, rec_to INTEGER);
CREATE INDEX ix_k_node_states ON k_node_states(node, rec_to);
CREATE TABLE k_coord_systems (
    id INTEGER PRIMARY KEY AUTOINCREMENT, namespace TEXT NOT NULL, system TEXT NOT NULL,
    owner TEXT NOT NULL, spec TEXT NOT NULL, rec_from INTEGER NOT NULL, rec_to INTEGER);
CREATE INDEX ix_k_coord ON k_coord_systems(namespace, system, rec_to);
CREATE TABLE k_shapes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, node TEXT NOT NULL, system TEXT NOT NULL, geom TEXT NOT NULL,
    valid_from TEXT NOT NULL, valid_to TEXT, rec_from INTEGER NOT NULL, rec_to INTEGER);
CREATE INDEX ix_k_shapes ON k_shapes(system, rec_to);
CREATE INDEX ix_k_shapes_node ON k_shapes(node, system, rec_to);
CREATE TABLE k_declarations (
    id INTEGER PRIMARY KEY AUTOINCREMENT, family TEXT NOT NULL, namespace TEXT NOT NULL, name TEXT NOT NULL,
    owner TEXT NOT NULL, spec TEXT NOT NULL, rec_from INTEGER NOT NULL, rec_to INTEGER, scope TEXT);
CREATE INDEX ix_k_decl ON k_declarations(family, namespace, name, rec_to);
CREATE TABLE k_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT, namespace TEXT NOT NULL, setting TEXT NOT NULL, scope TEXT,
    value TEXT NOT NULL, valid_from TEXT NOT NULL, valid_to TEXT, rec_from INTEGER NOT NULL, rec_to INTEGER);
CREATE INDEX ix_k_assign ON k_assignments(setting, namespace, scope, rec_to);
CREATE TABLE k_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, namespace TEXT NOT NULL, title TEXT NOT NULL, ops TEXT NOT NULL,
    state TEXT NOT NULL, author TEXT, approver TEXT, publish_at TEXT, seq_from INTEGER, seq_to INTEGER,
    rolled_back_seq INTEGER, result TEXT, report TEXT, created_at TEXT NOT NULL);
CREATE INDEX ix_k_changes_state ON k_changes(state, publish_at);
CREATE TABLE affiliate_networks (
    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, slug TEXT UNIQUE, tenant_id INTEGER DEFAULT 1,
    status TEXT DEFAULT 'active', default_commission_pct REAL DEFAULT 5.0, cookie_days INTEGER DEFAULT 30,
    attribution_model TEXT DEFAULT 'last_touch', min_payout REAL DEFAULT 50.0, currency TEXT DEFAULT 'USD',
    created_at TEXT DEFAULT (datetime('now')), uid TEXT );
CREATE TABLE affiliates (
    id INTEGER PRIMARY KEY AUTOINCREMENT, network_id INTEGER REFERENCES affiliate_networks(id), tenant_id INTEGER DEFAULT 1,
    name TEXT NOT NULL, email TEXT UNIQUE, status TEXT DEFAULT 'pending', affiliate_code TEXT UNIQUE,
    tracking_url TEXT, deep_link_template TEXT, commission_pct REAL, commission_type TEXT DEFAULT 'revenue',
    tier TEXT DEFAULT 'standard', balance REAL DEFAULT 0, lifetime_sales REAL DEFAULT 0,
    lifetime_commissions REAL DEFAULT 0, created_at TEXT DEFAULT (datetime('now')), last_activity TEXT,
    metadata TEXT DEFAULT '{}', uid TEXT );
CREATE TABLE affiliate_clicks (
    id INTEGER PRIMARY KEY AUTOINCREMENT, affiliate_id INTEGER REFERENCES affiliates(id),
    network_id INTEGER REFERENCES affiliate_networks(id), tenant_id INTEGER DEFAULT 1,
    click_id TEXT UNIQUE, ip TEXT, user_agent TEXT, referrer TEXT, landing_url TEXT,
    campaign TEXT, source TEXT, medium TEXT, created_at TEXT DEFAULT (datetime('now')), uid TEXT );
CREATE TABLE affiliate_conversions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, affiliate_id INTEGER REFERENCES affiliates(id),
    network_id INTEGER REFERENCES affiliate_networks(id), tenant_id INTEGER DEFAULT 1,
    click_id TEXT REFERENCES affiliate_clicks(click_id), order_id INTEGER REFERENCES orders(id),
    order_num TEXT, conversion_type TEXT DEFAULT 'sale', revenue REAL, commission REAL,
    commission_pct REAL, status TEXT DEFAULT 'pending', approved_at TEXT, paid_at TEXT,
    payment_id INTEGER, created_at TEXT DEFAULT (datetime('now')), uid TEXT );
CREATE TABLE commission_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT, network_id INTEGER REFERENCES affiliate_networks(id),
    tenant_id INTEGER DEFAULT 1, name TEXT NOT NULL, status TEXT DEFAULT 'active',
    applies_to TEXT DEFAULT 'all', condition TEXT DEFAULT '{}', commission_type TEXT DEFAULT 'revenue',
    commission_value REAL, min_order REAL DEFAULT 0, max_order REAL, tier TEXT,
    product_ids TEXT, category_ids TEXT, brand_ids TEXT, start_date TEXT, end_date TEXT,
    position INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now')), uid TEXT );
CREATE TABLE affiliate_tiers (
    id INTEGER PRIMARY KEY AUTOINCREMENT, network_id INTEGER REFERENCES affiliate_networks(id),
    name TEXT NOT NULL, min_sales REAL DEFAULT 0, commission_bonus_pct REAL DEFAULT 0,
    benefits TEXT DEFAULT '[]', position INTEGER DEFAULT 0, uid TEXT );
CREATE TABLE affiliate_payouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT, affiliate_id INTEGER REFERENCES affiliates(id),
    network_id INTEGER REFERENCES affiliate_networks(id), amount REAL NOT NULL,
    status TEXT DEFAULT 'pending', method TEXT DEFAULT 'bank', transaction_ref TEXT,
    paid_at TEXT, created_at TEXT DEFAULT (datetime('now')), uid TEXT );
CREATE TABLE sitemap_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER DEFAULT 1,
    hostname TEXT,
    max_per_file INTEGER DEFAULT 50000,
    enabled INTEGER DEFAULT 1,
    last_generated TEXT,
    next_run TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
  );
CREATE TABLE sitemap_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER DEFAULT 1,
    loc TEXT UNIQUE,
    sitemap_type TEXT DEFAULT 'pages',
    priority REAL DEFAULT 0.5,
    changefreq TEXT DEFAULT 'monthly',
    lastmod TEXT,
    images TEXT DEFAULT '[]',
    languages TEXT DEFAULT '[]',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
  );
CREATE TABLE sitemap_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER DEFAULT 1,
    filename TEXT UNIQUE,
    sitemap_type TEXT DEFAULT 'pages',
    entry_count INTEGER DEFAULT 0,
    file_size INTEGER DEFAULT 0,
    generated_at TEXT,
    status TEXT DEFAULT 'pending',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
  );
CREATE TABLE shipping_providers (
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
  );
CREATE TABLE package_tracking (
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
  , tenant_id INTEGER, label_url TEXT);
CREATE INDEX ix_package_tracking_tenant ON package_tracking(tenant_id, tracking_number);
CREATE TABLE shipping_quotes (
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
  , tenant_id INTEGER, shipment_ref TEXT, rate_ref TEXT, carrier TEXT);
