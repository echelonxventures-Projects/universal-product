CREATE TABLE tenants (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  slug TEXT NOT NULL UNIQUE, name TEXT NOT NULL, domain TEXT DEFAULT '',
  status TEXT NOT NULL DEFAULT 'active', created_at TEXT NOT NULL DEFAULT (datetime('now'))
, mode TEXT NOT NULL DEFAULT 'marketplace', industries TEXT DEFAULT '[]', profile TEXT DEFAULT '{}', country TEXT DEFAULT 'US', uid TEXT);
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
, uid TEXT);
CREATE TABLE audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER, actor_type TEXT NOT NULL DEFAULT 'system',
  actor_id INTEGER, actor_name TEXT, action TEXT NOT NULL,
  entity TEXT, entity_id TEXT, meta TEXT DEFAULT '', ip TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
, prev_hash TEXT, hash TEXT, uid TEXT);
CREATE TABLE platform_admins (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, salt TEXT NOT NULL, hash TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
, kdf_version TEXT DEFAULT 'v1', uid TEXT);
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
  created_at TEXT NOT NULL DEFAULT (datetime('now')), kdf_version TEXT DEFAULT 'v1', pwd_history TEXT DEFAULT '[]', uid TEXT,
  UNIQUE(tenant_id, email)
);
CREATE TABLE sessions (
  sid TEXT PRIMARY KEY, user_id INTEGER REFERENCES users(id),
  created_at TEXT NOT NULL DEFAULT (datetime('now')), expires_at TEXT NOT NULL
, csrf TEXT, uid TEXT);
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
  flags TEXT, keywords TEXT, deal_pct INTEGER DEFAULT 0, position INTEGER DEFAULT 0, type TEXT DEFAULT 'physical', node_id INTEGER, lifecycle TEXT DEFAULT 'published', identity TEXT DEFAULT '{}', attrs TEXT DEFAULT '{}', vertical TEXT DEFAULT '{}', media TEXT DEFAULT '[]', seo TEXT DEFAULT '{}', tax_rule TEXT DEFAULT '{}', geo_rules TEXT DEFAULT '[]', pricing_rules TEXT DEFAULT '[]', logistics TEXT DEFAULT '{}', packaging TEXT DEFAULT '[]', docs TEXT DEFAULT '[]', supplier_id INTEGER, uom TEXT DEFAULT '{"unit":"ea"}', tax_profile TEXT DEFAULT '', invoice_profile TEXT DEFAULT '', payment_profiles TEXT DEFAULT '[]', uid TEXT,
  PRIMARY KEY (tenant_id, id)
);
CREATE TABLE product_bullets (
  tenant_id INTEGER NOT NULL DEFAULT 1, product_id TEXT NOT NULL, pos INTEGER NOT NULL, text TEXT NOT NULL, uid TEXT,
  PRIMARY KEY (tenant_id, product_id, pos)
);
CREATE TABLE cart_items (
  owner TEXT NOT NULL, product_id TEXT NOT NULL, qty INTEGER NOT NULL DEFAULT 1,
  added_at TEXT NOT NULL DEFAULT (datetime('now')), uid TEXT, PRIMARY KEY (owner, product_id)
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
, contexts TEXT DEFAULT '{}', currency TEXT DEFAULT '', fx REAL DEFAULT 1, uid TEXT);
CREATE TABLE order_items (
  order_id INTEGER NOT NULL, product_id TEXT NOT NULL, qty INTEGER NOT NULL, price REAL NOT NULL
, uid TEXT);
CREATE TABLE reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL DEFAULT 1,
  product_id TEXT NOT NULL, user_id INTEGER, name TEXT NOT NULL,
  rating INTEGER NOT NULL, title TEXT NOT NULL, body TEXT NOT NULL,
  verified INTEGER DEFAULT 0, created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
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
  icon TEXT DEFAULT '🏷️', active INTEGER NOT NULL DEFAULT 1, position INTEGER NOT NULL DEFAULT 0, uid TEXT,
  PRIMARY KEY (tenant_id, key)
);
CREATE TABLE home_banners (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL DEFAULT 1,
  title TEXT NOT NULL, subtitle TEXT, cta TEXT, hue INTEGER DEFAULT 210, dept TEXT DEFAULT '',
  active INTEGER NOT NULL DEFAULT 1, position INTEGER NOT NULL DEFAULT 0
, uid TEXT);
CREATE TABLE home_cards (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL DEFAULT 1,
  title TEXT NOT NULL, dept TEXT NOT NULL, tiles TEXT DEFAULT '[]',
  active INTEGER NOT NULL DEFAULT 1, position INTEGER NOT NULL DEFAULT 0
, uid TEXT);
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
, uid TEXT);
CREATE TABLE custom_providers (
  id INTEGER PRIMARY KEY AUTOINCREMENT, scope TEXT NOT NULL DEFAULT 'platform',
  tenant_id INTEGER, kind TEXT NOT NULL, manifest TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE TABLE taxonomy (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  parent_id INTEGER, level TEXT NOT NULL, key TEXT NOT NULL, name TEXT NOT NULL,
  icon TEXT DEFAULT '', attrs TEXT DEFAULT '{}', active INTEGER DEFAULT 1, position INTEGER DEFAULT 0
);
CREATE TABLE attribute_defs (
  tenant_id INTEGER NOT NULL, key TEXT NOT NULL, label TEXT NOT NULL, grp TEXT DEFAULT 'General',
  type TEXT DEFAULT 'text', unit TEXT DEFAULT '', options TEXT DEFAULT '[]', validation TEXT DEFAULT '{}',
  industry TEXT DEFAULT '', position INTEGER DEFAULT 0, PRIMARY KEY (tenant_id, key)
);
CREATE TABLE skus (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, product_id TEXT NOT NULL,
  code TEXT NOT NULL, name TEXT DEFAULT '', identity TEXT DEFAULT '{}', variant TEXT DEFAULT '{}',
  price REAL, mrp REAL, stock INTEGER DEFAULT 0, active INTEGER DEFAULT 1
);
CREATE TABLE warehouses (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, name TEXT NOT NULL,
  code TEXT, country TEXT DEFAULT 'US', region TEXT DEFAULT '', active INTEGER DEFAULT 1
);
CREATE TABLE inventory (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, sku_id INTEGER NOT NULL,
  warehouse_id INTEGER, qty INTEGER DEFAULT 0, reserved INTEGER DEFAULT 0,
  lot TEXT DEFAULT '', batch TEXT DEFAULT '', expiry TEXT DEFAULT '', serial TEXT DEFAULT '[]'
);
CREATE TABLE relationships (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL,
  from_id TEXT NOT NULL, to_id TEXT NOT NULL, type TEXT NOT NULL
);
CREATE TABLE promotions (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, name TEXT NOT NULL,
  type TEXT NOT NULL, value REAL DEFAULT 0, rules TEXT DEFAULT '{}', scope TEXT DEFAULT '{}',
  starts TEXT, ends TEXT, status TEXT DEFAULT 'active', code TEXT DEFAULT ''
);
CREATE TABLE sellers (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, name TEXT NOT NULL,
  role TEXT DEFAULT 'retailer', email TEXT, status TEXT DEFAULT 'active', commission_pct REAL DEFAULT 5
);
CREATE TABLE rfqs (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT NOT NULL UNIQUE,
  product_id TEXT, buyer_name TEXT, buyer_email TEXT, qty REAL, target_price REAL, currency TEXT,
  status TEXT DEFAULT 'open', quotes TEXT DEFAULT '[]', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE returns (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT NOT NULL UNIQUE,
  order_id INTEGER, product_id TEXT, qty INTEGER DEFAULT 1, reason TEXT, status TEXT DEFAULT 'requested',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE settlements (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT NOT NULL UNIQUE,
  seller_id INTEGER, order_id INTEGER, gross REAL, commission REAL, net REAL,
  status TEXT DEFAULT 'pending', period TEXT
);
CREATE TABLE meta_lists (
  name TEXT PRIMARY KEY, label TEXT, items TEXT NOT NULL
, uid TEXT);
CREATE TABLE countries (
  code TEXT PRIMARY KEY, name TEXT NOT NULL, currency TEXT NOT NULL, symbol TEXT NOT NULL,
  locale TEXT NOT NULL, decimals INTEGER NOT NULL DEFAULT 2, tax_mode TEXT DEFAULT 'manual',
  tax_rate REAL DEFAULT 0, position INTEGER DEFAULT 0, active INTEGER DEFAULT 1
, uid TEXT);
CREATE TABLE currencies (
  code TEXT PRIMARY KEY, name TEXT NOT NULL, symbol TEXT NOT NULL, decimals INTEGER NOT NULL DEFAULT 2,
  usd REAL NOT NULL DEFAULT 1, position INTEGER DEFAULT 0, active INTEGER DEFAULT 1
, uid TEXT);
CREATE TABLE tax_modes (
  key TEXT PRIMARY KEY, label TEXT NOT NULL, description TEXT, fields TEXT DEFAULT '[]', position INTEGER DEFAULT 0
, uid TEXT);
CREATE TABLE provider_defs (
  id TEXT NOT NULL, kind TEXT NOT NULL, name TEXT NOT NULL, emoji TEXT, description TEXT,
  methods TEXT DEFAULT '[]', fee_pct REAL DEFAULT 0, fee_fixed REAL DEFAULT 0, fields TEXT DEFAULT '[]',
  base_fee REAL DEFAULT 0, eta_min INTEGER, eta_max INTEGER, position INTEGER DEFAULT 0,
  enabled INTEGER DEFAULT 1, uid TEXT, PRIMARY KEY (id, kind)
);
CREATE TABLE provider_availability (
  provider_id TEXT NOT NULL, country_code TEXT NOT NULL REFERENCES countries(code), uid TEXT,
  PRIMARY KEY (provider_id, country_code)
);
CREATE TABLE fx_rates (
  id INTEGER PRIMARY KEY AUTOINCREMENT, currency TEXT NOT NULL, usd REAL NOT NULL,
  source TEXT DEFAULT 'manual', note TEXT DEFAULT '', created_at TEXT NOT NULL DEFAULT (datetime('now'))
, uid TEXT);
CREATE TABLE platform_settings (
  key TEXT PRIMARY KEY, value TEXT NOT NULL
, uid TEXT);
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
CREATE INDEX ix_products_tenant ON products(tenant_id, dept);
CREATE INDEX ix_reviews_pid ON reviews(tenant_id, product_id);
CREATE INDEX ix_orders_tenant ON orders(tenant_id, created_at);
CREATE INDEX ix_audit_tenant ON audit_log(tenant_id, created_at);
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
