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
  flags TEXT, keywords TEXT, deal_pct INTEGER DEFAULT 0, position INTEGER DEFAULT 0, type TEXT DEFAULT 'physical', node_id INTEGER, lifecycle TEXT DEFAULT 'published', identity TEXT DEFAULT '{}', attrs TEXT DEFAULT '{}', vertical TEXT DEFAULT '{}', media TEXT DEFAULT '[]', seo TEXT DEFAULT '{}', tax_rule TEXT DEFAULT '{}', geo_rules TEXT DEFAULT '[]', pricing_rules TEXT DEFAULT '[]', logistics TEXT DEFAULT '{}', packaging TEXT DEFAULT '[]', docs TEXT DEFAULT '[]', supplier_id INTEGER, uom TEXT DEFAULT '{"unit":"ea"}', tax_profile TEXT DEFAULT '', invoice_profile TEXT DEFAULT '', payment_profiles TEXT DEFAULT '[]', source_universe TEXT, source_kind TEXT DEFAULT 'seed', uid TEXT,
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
  price REAL, mrp REAL, stock INTEGER DEFAULT 0, active INTEGER DEFAULT 1, group_id INTEGER, uid TEXT
);
CREATE UNIQUE INDEX ux_skus_uid ON skus(uid);
CREATE TRIGGER trg_skus_uid AFTER INSERT ON skus
               BEGIN UPDATE skus SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
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
  name TEXT PRIMARY KEY, label TEXT, items TEXT NOT NULL, seeded_from TEXT
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
/* ---------- UCOS Ω∞ constitutional registry (UPIP + UMQSOCR documents) ---------- */
CREATE TABLE ucos_documents (
  doc_id TEXT PRIMARY KEY, file TEXT NOT NULL, code TEXT NOT NULL, name TEXT NOT NULL,
  kind TEXT NOT NULL DEFAULT 'architecture',
  parts INTEGER DEFAULT 0, sections INTEGER DEFAULT 0, articles INTEGER DEFAULT 0,
  concepts INTEGER DEFAULT 0, registries INTEGER DEFAULT 0, lines INTEGER DEFAULT 0, chars INTEGER DEFAULT 0
, uid TEXT);
CREATE TABLE ucos_parts (
  id INTEGER PRIMARY KEY AUTOINCREMENT, doc_id TEXT NOT NULL, no INTEGER, label TEXT, title TEXT, line INTEGER
, uid TEXT);
CREATE INDEX ix_ucos_parts ON ucos_parts(doc_id, no);
CREATE TABLE ucos_sections (
  id INTEGER PRIMARY KEY AUTOINCREMENT, doc_id TEXT NOT NULL, qkey TEXT NOT NULL,
  no INTEGER, key TEXT, name TEXT, part_no INTEGER, line INTEGER,
  concepts INTEGER DEFAULT 0, registries INTEGER DEFAULT 0, meta TEXT DEFAULT '{}',
  kind TEXT DEFAULT 'section', doc_block TEXT
, uid TEXT);
CREATE UNIQUE INDEX ux_ucos_sections ON ucos_sections(doc_id, qkey);
CREATE TABLE ucos_concepts (
  id INTEGER PRIMARY KEY AUTOINCREMENT, doc_id TEXT NOT NULL, key TEXT NOT NULL,
  name TEXT NOT NULL, container_kind TEXT, container_key TEXT, container_name TEXT,
  part_no INTEGER, line INTEGER
, uid TEXT);
CREATE INDEX ix_ucos_concepts ON ucos_concepts(doc_id, key);
CREATE INDEX ix_ucos_concepts_name ON ucos_concepts(doc_id, name);
CREATE TABLE ucos_registries (
  id INTEGER PRIMARY KEY AUTOINCREMENT, doc_id TEXT NOT NULL, key TEXT NOT NULL, label TEXT,
  container_kind TEXT, container_key TEXT, items TEXT DEFAULT '[]', item_count INTEGER DEFAULT 0, line INTEGER
, uid TEXT);
CREATE INDEX ix_ucos_reg ON ucos_registries(doc_id, key);
CREATE TABLE ucos_edges (
  id INTEGER PRIMARY KEY AUTOINCREMENT, doc_id TEXT NOT NULL,
  source_type TEXT NOT NULL, source_id TEXT NOT NULL, rel TEXT NOT NULL,
  target_type TEXT NOT NULL, target_id TEXT NOT NULL
, uid TEXT);
CREATE UNIQUE INDEX ux_ucos_edges ON ucos_edges(doc_id, source_type, source_id, rel, target_type, target_id);
CREATE INDEX ix_ucos_edges_src ON ucos_edges(doc_id, source_type, source_id);
/* annotation layer — the write path; the documents stay immutable (see lib/db.js) */
CREATE TABLE ucos_annotations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  doc_id TEXT NOT NULL,
  target_kind TEXT NOT NULL,
  target_key TEXT NOT NULL,
  note TEXT NOT NULL,
  pin INTEGER DEFAULT 0,
  created_by TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
, uid TEXT);
CREATE INDEX ix_ucos_ann ON ucos_annotations(doc_id, target_kind, target_key);
CREATE INDEX ix_ucos_ann_pin ON ucos_annotations(doc_id, target_kind, target_key, pin);
/* ---------- UCOS Ω∞ Foundation Registry (Architecture3 Articles 2-8) ----------
   The operational half of the constitution: every universe, domain and capability
   the corpus declares is registered here as data. No foundation may be asserted
   in code (Article 4.2), so this table — not a JS constant — is the source of truth. */
CREATE TABLE ucos_foundations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  key TEXT NOT NULL UNIQUE,              /* canonical identity (Article 8.2: globally unique) */
  name TEXT NOT NULL,
  parent TEXT,                           /* parent foundation (derivation, Article 4.1) */
  universe TEXT,                         /* the declared universe this foundation belongs to */
  lifecycle TEXT NOT NULL DEFAULT 'canonical',   /* Article 5.1 states */
  governance TEXT NOT NULL DEFAULT 'Foundation Authority',  /* Article 6 */
  classification TEXT,                   /* universe | domain | foundation | primitive | capability */
  source_doc TEXT,                       /* traceability: which corpus document declares it */
  source_line INTEGER,
  discovery TEXT,                        /* Article 2.2 discovery handle */
  created_at TEXT
);
CREATE INDEX ix_ucos_foundations_universe ON ucos_foundations(universe, lifecycle);
CREATE INDEX ix_ucos_foundations_parent ON ucos_foundations(parent);
/* dependency edges (Article 3.1 dependency graph; Article 3.2: acyclic) */
CREATE TABLE ucos_foundation_deps (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  foundation TEXT NOT NULL,
  dependency TEXT NOT NULL,
  UNIQUE(foundation, dependency)
);
CREATE INDEX ix_ucos_foundation_deps_dep ON ucos_foundation_deps(dependency);
/* evolution edges (Article 3.1 evolution graph; Article 8.3: succession, never in-place mutation) */
CREATE TABLE ucos_foundation_evolution (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  foundation TEXT NOT NULL,              /* successor */
  predecessor TEXT NOT NULL,
  UNIQUE(foundation, predecessor)
);
/* composition edges (Article 3.1 composition graph: what composes what) */
CREATE TABLE ucos_foundation_composition (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  parent TEXT NOT NULL,
  child TEXT NOT NULL,
  UNIQUE(parent, child)
);
CREATE INDEX ix_ucos_foundation_comp_child ON ucos_foundation_composition(child);
/* Article 6: append-audited ledger of every admission, transition and retirement */
CREATE TABLE ucos_foundation_audit (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  foundation TEXT NOT NULL,
  event TEXT NOT NULL,                   /* Article 7.2 events */
  detail TEXT DEFAULT '{}',
  at TEXT NOT NULL
);
CREATE INDEX ix_ucos_foundation_audit_f ON ucos_foundation_audit(foundation, at);
/* ---------- instantiated universes: each declared universe becomes a live,
   data-defined entity (zero per-universe code; Article 4.2 compliance) ---------- */
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

/* ---------- advanced universal-model entities: suppliers, serialization, variant groups, compliance, localization, contracts, tenders ---------- */
CREATE TABLE serialized_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  product_id TEXT NOT NULL,
  sku_id INTEGER,
  warehouse_id INTEGER,
  serial TEXT NOT NULL,
  imei TEXT,
  rfid TEXT,
  asset_tag TEXT,
  batch TEXT DEFAULT '',
  lot TEXT DEFAULT '',
  expiry TEXT,
  status TEXT NOT NULL DEFAULT 'in_stock',
  condition TEXT DEFAULT 'new',
  customer_id INTEGER,
  order_id INTEGER,
  purchase_date TEXT,
  warranty_end TEXT,
  meta TEXT DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  uid TEXT
);
CREATE UNIQUE INDEX ux_serialized_items_uid ON serialized_items(uid);
CREATE TRIGGER trg_serialized_items_uid AFTER INSERT ON serialized_items
               BEGIN UPDATE serialized_items SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE TABLE variant_groups (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  product_id TEXT NOT NULL,
  name TEXT NOT NULL,
  axis TEXT DEFAULT 'General',
  attr_key TEXT DEFAULT '',
  position INTEGER DEFAULT 0,
  active INTEGER DEFAULT 1,
  uid TEXT
);
CREATE UNIQUE INDEX ux_variant_groups_uid ON variant_groups(uid);
CREATE TRIGGER trg_variant_groups_uid AFTER INSERT ON variant_groups
               BEGIN UPDATE variant_groups SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE TABLE compliance_records (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  scope TEXT NOT NULL DEFAULT 'product',
  ref_id TEXT NOT NULL DEFAULT '',
  kind TEXT NOT NULL DEFAULT 'certificate',
  code TEXT DEFAULT '',
  issuer TEXT DEFAULT '',
  jurisdiction TEXT DEFAULT '',
  status TEXT NOT NULL DEFAULT 'valid',
  valid_from TEXT,
  valid_to TEXT,
  doc_media TEXT DEFAULT '',
  notes TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  uid TEXT
);
CREATE UNIQUE INDEX ux_compliance_records_uid ON compliance_records(uid);
CREATE TRIGGER trg_compliance_records_uid AFTER INSERT ON compliance_records
               BEGIN UPDATE compliance_records SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE TABLE suppliers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  party_role TEXT DEFAULT 'manufacturer',
  tax_id TEXT DEFAULT '',
  country TEXT DEFAULT 'US',
  region TEXT DEFAULT '',
  address TEXT DEFAULT '',
  email TEXT DEFAULT '',
  phone TEXT DEFAULT '',
  lead_time_days INTEGER DEFAULT 7,
  moq INTEGER DEFAULT 1,
  currency TEXT DEFAULT 'USD',
  payment_terms TEXT DEFAULT 'net30',
  on_time_pct REAL DEFAULT 0,
  status TEXT DEFAULT 'active',
  certifications TEXT DEFAULT '[]',
  price_list TEXT DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  uid TEXT
);
CREATE UNIQUE INDEX ux_suppliers_uid ON suppliers(uid);
CREATE TRIGGER trg_suppliers_uid AFTER INSERT ON suppliers
               BEGIN UPDATE suppliers SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE TABLE product_suppliers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  product_id TEXT NOT NULL,
  supplier_id INTEGER NOT NULL,
  supplier_sku TEXT DEFAULT '',
  price REAL,
  lead_days INTEGER DEFAULT 7,
  moq INTEGER DEFAULT 1,
  is_primary INTEGER DEFAULT 0,
  status TEXT DEFAULT 'active',
  uid TEXT,
  UNIQUE (tenant_id, product_id, supplier_id)
);
CREATE UNIQUE INDEX ux_product_suppliers_uid ON product_suppliers(uid);
CREATE TRIGGER trg_product_suppliers_uid AFTER INSERT ON product_suppliers
               BEGIN UPDATE product_suppliers SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE TABLE localizations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  entity TEXT NOT NULL DEFAULT 'product',
  ref_id TEXT NOT NULL,
  locale TEXT NOT NULL,
  name TEXT DEFAULT '',
  description TEXT DEFAULT '',
  bullets TEXT DEFAULT '[]',
  attrs TEXT DEFAULT '{}',
  active INTEGER DEFAULT 1,
  uid TEXT,
  UNIQUE (tenant_id, entity, ref_id, locale)
);
CREATE UNIQUE INDEX ux_localizations_uid ON localizations(uid);
CREATE TRIGGER trg_localizations_uid AFTER INSERT ON localizations
               BEGIN UPDATE localizations SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE TABLE contracts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  ref TEXT NOT NULL,
  buyer_name TEXT NOT NULL,
  buyer_email TEXT NOT NULL,
  buyer_org TEXT DEFAULT '',
  supplier_id INTEGER,
  product_ids TEXT DEFAULT '[]',
  currency TEXT DEFAULT 'USD',
  pricing TEXT DEFAULT '{}',
  min_qty INTEGER DEFAULT 1,
  incoterms TEXT DEFAULT 'EXW',
  payment_terms TEXT DEFAULT 'net30',
  valid_from TEXT,
  valid_to TEXT,
  status TEXT NOT NULL DEFAULT 'draft',
  notes TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  uid TEXT,
  UNIQUE (tenant_id, ref)
);
CREATE UNIQUE INDEX ux_contracts_uid ON contracts(uid);
CREATE TRIGGER trg_contracts_uid AFTER INSERT ON contracts
               BEGIN UPDATE contracts SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE TABLE tenders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  ref TEXT NOT NULL,
  title TEXT NOT NULL,
  buyer_org TEXT DEFAULT '',
  buyer_email TEXT DEFAULT '',
  description TEXT DEFAULT '',
  currency TEXT DEFAULT 'USD',
  budget REAL DEFAULT 0,
  open_at TEXT,
  close_at TEXT,
  status TEXT NOT NULL DEFAULT 'open',
  awarded_seller_id INTEGER,
  awarded_contract_id INTEGER,
  items TEXT DEFAULT '[]',
  bids TEXT DEFAULT '[]',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  uid TEXT,
  UNIQUE (tenant_id, ref)
);
CREATE UNIQUE INDEX ux_tenders_uid ON tenders(uid);
CREATE TRIGGER trg_tenders_uid AFTER INSERT ON tenders
               BEGIN UPDATE tenders SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ix_serial_tenant ON serialized_items(tenant_id, serial);

/* ---------- AI product layer: usage ledger + task queue ---------- */
CREATE TABLE ai_usage (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  capability TEXT NOT NULL,
  provider TEXT NOT NULL,
  model TEXT DEFAULT '',
  units INTEGER NOT NULL DEFAULT 1,
  cost REAL NOT NULL DEFAULT 0,
  currency TEXT DEFAULT 'USD',
  tier TEXT DEFAULT 'free',
  status TEXT DEFAULT 'ok',
  actor TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  uid TEXT
);
CREATE UNIQUE INDEX ux_ai_usage_uid ON ai_usage(uid);
CREATE TRIGGER trg_ai_usage_uid AFTER INSERT ON ai_usage
               BEGIN UPDATE ai_usage SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE TABLE ai_tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  capability TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'queued',
  params TEXT DEFAULT '{}',
  result TEXT,
  cost REAL DEFAULT 0,
  actor TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT,
  uid TEXT
);
CREATE UNIQUE INDEX ux_ai_tasks_uid ON ai_tasks(uid);
CREATE TRIGGER trg_ai_tasks_uid AFTER INSERT ON ai_tasks
               BEGIN UPDATE ai_tasks SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;

/* ---------- central offers / coupons / wallet ledger ---------- */
CREATE TABLE offers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL DEFAULT 0,
  scope_level TEXT NOT NULL DEFAULT 'tenant',
  channel TEXT NOT NULL DEFAULT 'commerce',
  name TEXT NOT NULL,
  code TEXT DEFAULT '',
  type TEXT NOT NULL,
  direction TEXT NOT NULL DEFAULT 'discount',
  value REAL DEFAULT 0,
  currency TEXT DEFAULT 'USD',
  scope_type TEXT NOT NULL DEFAULT 'store',
  scope_value TEXT DEFAULT '{}',
  funder TEXT NOT NULL DEFAULT 'self',
  funder_ref TEXT DEFAULT '',
  brand_ref TEXT DEFAULT '',
  min_amount REAL DEFAULT 0,
  min_qty INTEGER DEFAULT 0,
  max_discount REAL DEFAULT 0,
  usage_limit INTEGER DEFAULT 0,
  per_owner_limit INTEGER DEFAULT 0,
  used INTEGER DEFAULT 0,
  stack_group TEXT DEFAULT '',
  stack_policy TEXT DEFAULT 'stack_with_others',
  priority INTEGER DEFAULT 0,
  starts TEXT,
  ends TEXT,
  status TEXT DEFAULT 'active',
  rules TEXT DEFAULT '{}',
  summary TEXT DEFAULT '',
  source TEXT DEFAULT 'offer',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  uid TEXT
);
CREATE UNIQUE INDEX ux_offers_uid ON offers(uid);
CREATE TRIGGER trg_offers_uid AFTER INSERT ON offers
               BEGIN UPDATE offers SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE TABLE coupons (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL DEFAULT 0,
  code TEXT NOT NULL,
  offer_id INTEGER,
  funder TEXT DEFAULT 'self',
  funder_ref TEXT DEFAULT '',
  brand_ref TEXT DEFAULT '',
  kind TEXT NOT NULL DEFAULT 'single_use',
  value REAL DEFAULT 0,
  currency TEXT DEFAULT 'USD',
  max_uses INTEGER DEFAULT 1,
  per_owner_limit INTEGER DEFAULT 1,
  used INTEGER DEFAULT 0,
  issued_to TEXT DEFAULT '',
  batch TEXT DEFAULT '',
  starts TEXT,
  ends TEXT,
  status TEXT DEFAULT 'active',
  note TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  uid TEXT,
  UNIQUE (tenant_id, code)
);
CREATE UNIQUE INDEX ux_coupons_uid ON coupons(uid);
CREATE TRIGGER trg_coupons_uid AFTER INSERT ON coupons
               BEGIN UPDATE coupons SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE TABLE coupon_redemptions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  coupon_id INTEGER,
  offer_id INTEGER,
  code TEXT,
  order_id INTEGER,
  invoice_id INTEGER,
  owner TEXT,
  channel TEXT DEFAULT 'commerce',
  amount REAL DEFAULT 0,
  qty INTEGER DEFAULT 1,
  funder TEXT DEFAULT 'self',
  funder_ref TEXT DEFAULT '',
  brand_ref TEXT DEFAULT '',
  meta TEXT DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  uid TEXT
);
CREATE UNIQUE INDEX ux_coupon_redemptions_uid ON coupon_redemptions(uid);
CREATE TRIGGER trg_coupon_redemptions_uid AFTER INSERT ON coupon_redemptions
               BEGIN UPDATE coupon_redemptions SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE TABLE wallet_entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL DEFAULT 0,
  owner TEXT NOT NULL,
  currency TEXT DEFAULT 'USD',
  kind TEXT NOT NULL,
  amount REAL NOT NULL,
  balance_after REAL DEFAULT 0,
  ref TEXT DEFAULT '',
  note TEXT DEFAULT '',
  channel TEXT DEFAULT 'commerce',
  actor TEXT DEFAULT 'system',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  uid TEXT
);
CREATE UNIQUE INDEX ux_wallet_entries_uid ON wallet_entries(uid);
CREATE TRIGGER trg_wallet_entries_uid AFTER INSERT ON wallet_entries
               BEGIN UPDATE wallet_entries SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE UNIQUE INDEX ux_offers_code ON offers(tenant_id, code) WHERE code<>'';
CREATE INDEX ix_offers_chan ON offers(channel, status, tenant_id);
CREATE INDEX ix_wallet_tx ON wallet_entries(tenant_id, owner);

/* ---------- billing engine: line items, usage metering, credit notes, dunning events ---------- */
CREATE TABLE invoice_lines (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  invoice_id INTEGER NOT NULL,
  tenant_id INTEGER NOT NULL,
  kind TEXT NOT NULL DEFAULT 'plan',
  description TEXT NOT NULL,
  qty REAL DEFAULT 1,
  unit_amount REAL DEFAULT 0,
  amount REAL DEFAULT 0,
  tax REAL DEFAULT 0,
  tax_class TEXT DEFAULT 'standard',
  ref TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  uid TEXT
);
CREATE UNIQUE INDEX ux_invoice_lines_uid ON invoice_lines(uid);
CREATE TRIGGER trg_invoice_lines_uid AFTER INSERT ON invoice_lines
               BEGIN UPDATE invoice_lines SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE TABLE usage_records (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  kind TEXT NOT NULL,
  ref TEXT DEFAULT '',
  description TEXT NOT NULL DEFAULT '',
  qty REAL DEFAULT 1,
  unit_amount REAL DEFAULT 0,
  amount REAL DEFAULT 0,
  currency TEXT DEFAULT 'USD',
  period TEXT NOT NULL DEFAULT '',
  billed INTEGER DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  uid TEXT
);
CREATE UNIQUE INDEX ux_usage_records_uid ON usage_records(uid);
CREATE TRIGGER trg_usage_records_uid AFTER INSERT ON usage_records
               BEGIN UPDATE usage_records SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE TABLE credit_notes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  number TEXT NOT NULL UNIQUE,
  invoice_id INTEGER,
  amount REAL NOT NULL,
  currency TEXT DEFAULT 'USD',
  reason TEXT DEFAULT '',
  status TEXT NOT NULL DEFAULT 'issued',
  to_wallet INTEGER DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  uid TEXT
);
CREATE UNIQUE INDEX ux_credit_notes_uid ON credit_notes(uid);
CREATE TRIGGER trg_credit_notes_uid AFTER INSERT ON credit_notes
               BEGIN UPDATE credit_notes SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE TABLE billing_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  invoice_id INTEGER,
  kind TEXT NOT NULL,
  detail TEXT DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  uid TEXT
);
CREATE UNIQUE INDEX ux_billing_events_uid ON billing_events(uid);
CREATE TRIGGER trg_billing_events_uid AFTER INSERT ON billing_events
               BEGIN UPDATE billing_events SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE INDEX IF NOT EXISTS ix_invoice_lines ON invoice_lines(invoice_id);
CREATE INDEX IF NOT EXISTS ix_usage_open ON usage_records(tenant_id, billed);

/* ---------- platform hardening: webhooks, event deliveries, universal entity metadata, idempotency ---------- */
CREATE TABLE webhooks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  url TEXT NOT NULL,
  secret TEXT DEFAULT '',
  events TEXT DEFAULT '["*"]',
  active INTEGER DEFAULT 1,
  description TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT,
  uid TEXT
);
CREATE UNIQUE INDEX ux_webhooks_uid ON webhooks(uid);
CREATE TRIGGER trg_webhooks_uid AFTER INSERT ON webhooks
               BEGIN UPDATE webhooks SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE TABLE webhook_deliveries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  webhook_id INTEGER,
  event TEXT NOT NULL,
  subject_uid TEXT,
  payload TEXT DEFAULT '{}',
  status TEXT NOT NULL DEFAULT 'queued',
  attempts INTEGER DEFAULT 0,
  response TEXT DEFAULT '',
  next_retry_at TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  uid TEXT
);
CREATE UNIQUE INDEX ux_webhook_deliveries_uid ON webhook_deliveries(uid);
CREATE TRIGGER trg_webhook_deliveries_uid AFTER INSERT ON webhook_deliveries
               BEGIN UPDATE webhook_deliveries SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE TABLE entity_usage (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  entity TEXT NOT NULL,
  action TEXT NOT NULL,
  at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE(tenant_id, entity, action)
);
CREATE TABLE entity_meta (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  entity TEXT NOT NULL,
  ref_uid TEXT NOT NULL,
  tags TEXT DEFAULT '[]',
  meta TEXT DEFAULT '{}',
  notes TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT,
  uid TEXT,
  UNIQUE (tenant_id, entity, ref_uid)
);
CREATE UNIQUE INDEX ux_entity_meta_uid ON entity_meta(uid);
CREATE TRIGGER trg_entity_meta_uid AFTER INSERT ON entity_meta
               BEGIN UPDATE entity_meta SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE TABLE idempotency_keys (
  key TEXT PRIMARY KEY,
  tenant_id INTEGER,
  method TEXT,
  path TEXT,
  request_hash TEXT,
  status INTEGER,
  response TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  expires_at TEXT NOT NULL,
  uid TEXT
);
CREATE UNIQUE INDEX ux_idempotency_keys_uid ON idempotency_keys(uid);
CREATE TRIGGER trg_idempotency_keys_uid AFTER INSERT ON idempotency_keys
               BEGIN UPDATE idempotency_keys SET uid = lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6))) WHERE rowid = NEW.rowid; END;
CREATE INDEX IF NOT EXISTS ix_deliveries ON webhook_deliveries(tenant_id, status);
CREATE INDEX IF NOT EXISTS ix_entity_meta ON entity_meta(tenant_id, entity, ref_uid);

/* ---------- governance: soft-delete (deleted_at) on content tables ----------
   Additive columns applied via idempotent ALTER at boot (lib/db.js). Reads filter `deleted_at IS NULL`;
   the entity delete endpoint soft-deletes by default (hard with ?hard=1). Retention (platform_settings
   .retention / tenant settings 'retention') drives purge() that hard-deletes tombstoned rows past N days. */
ALTER TABLE products ADD COLUMN deleted_at TEXT;
ALTER TABLE orders   ADD COLUMN deleted_at TEXT;
ALTER TABLE reviews  ADD COLUMN deleted_at TEXT;
ALTER TABLE suppliers ADD COLUMN deleted_at TEXT;
ALTER TABLE offers   ADD COLUMN deleted_at TEXT;
ALTER TABLE contracts ADD COLUMN deleted_at TEXT;
ALTER TABLE tenders  ADD COLUMN deleted_at TEXT;
ALTER TABLE returns  ADD COLUMN deleted_at TEXT;

/* ---------- RBAC: staff roles + per-user permission overrides ---------- */
ALTER TABLE users ADD COLUMN staff_role TEXT DEFAULT 'owner';   /* key into meta_lists.staffRoles */
ALTER TABLE users ADD COLUMN perms      TEXT DEFAULT '{}';      /* per-user {section: read|write|false} override */
ALTER TABLE users ADD COLUMN disabled   INTEGER DEFAULT 0;      /* soft-disable login for staff */
ALTER TABLE users ADD COLUMN last_login TEXT;

/* ---------- enterprise ops tables ---------- */
ALTER TABLE tenants ADD COLUMN region TEXT DEFAULT 'global';
ALTER TABLE tenants ADD COLUMN sso_provider TEXT DEFAULT '';
ALTER TABLE tenants ADD COLUMN cdn TEXT DEFAULT '';
CREATE TABLE IF NOT EXISTS sso_connections (tenant_id INTEGER PRIMARY KEY, provider TEXT DEFAULT 'okta', entity_id TEXT DEFAULT '', sso_url TEXT DEFAULT '', cert TEXT DEFAULT '', enabled INTEGER DEFAULT 0, domains TEXT DEFAULT '[]', updated_at TEXT);
CREATE TABLE IF NOT EXISTS scim_tokens (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, token_hash TEXT NOT NULL, label TEXT DEFAULT '', prefix TEXT DEFAULT '', created_at TEXT);
CREATE TABLE IF NOT EXISTS stock_transfers (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, from_warehouse INTEGER, to_warehouse INTEGER, sku_id INTEGER, qty INTEGER NOT NULL DEFAULT 1, status TEXT DEFAULT 'draft', reference TEXT DEFAULT '', note TEXT DEFAULT '', created_at TEXT, deleted_at TEXT);
CREATE TABLE IF NOT EXISTS remittance_records (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, period TEXT NOT NULL, jurisdiction TEXT NOT NULL, tax_type TEXT DEFAULT 'vat', taxable REAL DEFAULT 0, tax_collected REAL DEFAULT 0, currency TEXT DEFAULT 'USD', status TEXT DEFAULT 'pending', filed_at TEXT, reference TEXT DEFAULT '', created_at TEXT, deleted_at TEXT);
CREATE TABLE IF NOT EXISTS inbound_events (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER, provider TEXT, event TEXT, payload TEXT DEFAULT '{}', signature_ok INTEGER DEFAULT 0, processed INTEGER DEFAULT 0, created_at TEXT);
CREATE TABLE IF NOT EXISTS tickets (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT NOT NULL UNIQUE,
  subject TEXT NOT NULL, reason TEXT NOT NULL DEFAULT 'other', priority TEXT NOT NULL DEFAULT 'normal',
  status TEXT NOT NULL DEFAULT 'new', assignee TEXT, owner TEXT, owner_name TEXT NOT NULL, owner_email TEXT,
  order_ref TEXT DEFAULT '', product_id TEXT DEFAULT '', body TEXT NOT NULL, channel TEXT DEFAULT 'email',
  sla_response TEXT, sla_resolution TEXT, first_response_at TEXT, resolved_at TEXT,
  csat INTEGER, csat_comment TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS ix_tickets ON tickets(tenant_id, status, priority);
CREATE TABLE IF NOT EXISTS agent_availability (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, agent_id TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'offline', updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE (tenant_id, agent_id)
);
CREATE TABLE IF NOT EXISTS ticket_notes (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ticket_id INTEGER NOT NULL,
  role TEXT NOT NULL DEFAULT 'agent', author TEXT NOT NULL, body TEXT NOT NULL, visibility TEXT NOT NULL DEFAULT 'public',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS capabilities (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  key TEXT NOT NULL,
  category TEXT NOT NULL DEFAULT 'feature',
  name TEXT NOT NULL,
  description TEXT DEFAULT '',
  version TEXT DEFAULT '1.0.0',
  schema TEXT DEFAULT '{}',
  config TEXT DEFAULT '{}',
  dependencies TEXT DEFAULT '[]',
  status TEXT DEFAULT 'active',
  enabled INTEGER DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_capabilities_tenant_key ON capabilities(tenant_id, key);

CREATE TABLE IF NOT EXISTS provider_availability (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  provider_id TEXT NOT NULL,
  country_code TEXT NOT NULL,
  region TEXT DEFAULT '',
  enabled INTEGER DEFAULT 1,
  config TEXT DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_provider_availability ON provider_availability(provider_id, country_code);

CREATE TABLE IF NOT EXISTS modules (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  category TEXT DEFAULT 'feature',
  summary TEXT DEFAULT '',
  price REAL DEFAULT 0,
  manifest TEXT DEFAULT '{}',
  status TEXT DEFAULT 'active',
  position INTEGER DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS provider_defs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  key TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  category TEXT DEFAULT 'feature',
  description TEXT DEFAULT '',
  config_schema TEXT DEFAULT '{}',
  enabled INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS localizations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  locale TEXT NOT NULL,
  name TEXT NOT NULL,
  currency TEXT DEFAULT 'USD',
  currency_symbol TEXT DEFAULT '',
  enabled INTEGER DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_localizations_tenant_locale ON localizations(tenant_id, locale);

CREATE TABLE IF NOT EXISTS payments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  order_id INTEGER NOT NULL,
  gateway TEXT NOT NULL,
  method TEXT DEFAULT '',
  txn_ref TEXT,
  amount REAL NOT NULL DEFAULT 0,
  currency TEXT DEFAULT 'USD',
  fee REAL DEFAULT 0,
  status TEXT DEFAULT 'pending',
  kind TEXT DEFAULT 'order',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS provider_availability (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  provider_id TEXT NOT NULL,
  country_code TEXT NOT NULL,
  region TEXT DEFAULT '',
  enabled INTEGER DEFAULT 1,
  config TEXT DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_prov_avail ON provider_availability(provider_id, country_code);

CREATE TABLE IF NOT EXISTS ai_usage (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  capability TEXT NOT NULL,
  provider TEXT NOT NULL,
  tier TEXT DEFAULT '',
  units REAL DEFAULT 0,
  cost REAL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS config_store (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  key TEXT NOT NULL,
  scope TEXT NOT NULL DEFAULT 'platform',
  tenant_id INTEGER,
  version INTEGER DEFAULT 1,
  value TEXT DEFAULT '{}',
  active INTEGER DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_config_store ON config_store(key, scope, tenant_id);

CREATE TABLE IF NOT EXISTS store_product_config (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  global_product_id TEXT NOT NULL,
  category TEXT DEFAULT '',
  permissions TEXT DEFAULT 'read',
  enabled INTEGER DEFAULT 1,
  config TEXT DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_spc ON store_product_config(tenant_id, global_product_id);

CREATE TABLE IF NOT EXISTS affiliate_networks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER,
  name TEXT NOT NULL,
  description TEXT DEFAULT '',
  commission_pct REAL DEFAULT 0,
  status TEXT DEFAULT 'active',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS affiliates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  network_id INTEGER,
  tenant_id INTEGER,
  name TEXT NOT NULL,
  affiliate_code TEXT UNIQUE,
  email TEXT,
  status TEXT DEFAULT 'active',
  lifetime_sales REAL DEFAULT 0,
  lifetime_commissions REAL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS affiliate_conversions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  affiliate_id INTEGER NOT NULL,
  order_id INTEGER,
  amount REAL DEFAULT 0,
  commission REAL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sitemap_config (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER DEFAULT 1,
  hostname TEXT DEFAULT 'https://example.com',
  enabled INTEGER DEFAULT 1,
  last_generated TEXT,
  next_run TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS usage_records (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  kind TEXT NOT NULL,
  qty REAL DEFAULT 1,
  amount REAL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS identity_providers (
  id TEXT PRIMARY KEY,
  tenant_id INTEGER NOT NULL,
  provider_type TEXT NOT NULL,
  name TEXT NOT NULL,
  enabled INTEGER DEFAULT 1,
  config TEXT DEFAULT '{}',
  display_order INTEGER DEFAULT 0,
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT
);

CREATE TABLE IF NOT EXISTS platform_identity_templates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  description TEXT DEFAULT '',
  config TEXT DEFAULT '{}',
  is_default INTEGER DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS global_products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sku TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  description TEXT DEFAULT '',
  category TEXT DEFAULT '',
  price REAL DEFAULT 0,
  tax_class TEXT DEFAULT 'standard',
  is_service INTEGER DEFAULT 0,
  attributes TEXT DEFAULT '{}',
  media TEXT DEFAULT '[]',
  profile TEXT DEFAULT '{}',
  status TEXT DEFAULT 'draft',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT
);

CREATE TABLE IF NOT EXISTS departments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  key TEXT NOT NULL UNIQUE,
  label TEXT NOT NULL,
  icon TEXT DEFAULT '',
  position INTEGER DEFAULT 0,
  active INTEGER DEFAULT 1
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_dept_tenant ON departments(tenant_id, key);

CREATE TABLE IF NOT EXISTS brands (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  key TEXT NOT NULL UNIQUE,
  label TEXT NOT NULL,
  icon TEXT,
  logo TEXT,
  story TEXT,
  country TEXT,
  active INTEGER NOT NULL DEFAULT 1,
  position INTEGER NOT NULL DEFAULT 0
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_brand_tenant ON brands(tenant_id, key);

CREATE TABLE IF NOT EXISTS attribute_defs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  key TEXT NOT NULL UNIQUE,
  label TEXT NOT NULL,
  type TEXT NOT NULL,
  options TEXT DEFAULT '[]',
  validation TEXT DEFAULT '{}',
  position INTEGER DEFAULT 0
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_attr_tenant ON attribute_defs(tenant_id, key);

/* ============================================================
   UNIVERSAL COMMERCE PARITY LAYER — Amazon · Flipkart · Zepto ·
   Blinkit · Paytm · Alibaba. Entity + registry driven; mirrored from
   lib/db.js (SQLite source of truth). Keep both in sync.
   ============================================================ */
CREATE TABLE IF NOT EXISTS dark_stores (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, uid TEXT, code TEXT, name TEXT NOT NULL, kind TEXT NOT NULL DEFAULT 'dark_store', address TEXT, city TEXT, region TEXT, pincode TEXT, country TEXT, lat REAL, lng REAL, service_radius_km REAL DEFAULT 3.0, promise_minutes INTEGER DEFAULT 10, prep_minutes INTEGER DEFAULT 4, min_order REAL DEFAULT 0, delivery_fee REAL DEFAULT 0, service_pincodes TEXT DEFAULT '[]', service_days TEXT DEFAULT '[]', status TEXT NOT NULL DEFAULT 'active', deleted_at TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_darkstore_tenant ON dark_stores(tenant_id, status);
CREATE TABLE IF NOT EXISTS delivery_slots (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, store_id INTEGER, day_offset INTEGER DEFAULT 0, window_start TEXT NOT NULL, window_end TEXT NOT NULL, capacity INTEGER DEFAULT 20, booked INTEGER DEFAULT 0, cutoff_minutes INTEGER DEFAULT 0, fee REAL DEFAULT 0, promise_minutes INTEGER, status TEXT NOT NULL DEFAULT 'open', deleted_at TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_slots_tenant ON delivery_slots(tenant_id, store_id, day_offset);
CREATE TABLE IF NOT EXISTS service_areas (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, store_id INTEGER, pincode TEXT NOT NULL, area_name TEXT, serviceable INTEGER DEFAULT 1, eta_minutes INTEGER DEFAULT 10, fee REAL DEFAULT 0, min_order REAL DEFAULT 0, cod_available INTEGER DEFAULT 1, status TEXT NOT NULL DEFAULT 'active', deleted_at TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_service_tenant ON service_areas(tenant_id, pincode, serviceable);
CREATE TABLE IF NOT EXISTS store_inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, store_id INTEGER NOT NULL, sku_id INTEGER, product_id TEXT, qty INTEGER DEFAULT 0, reserved INTEGER DEFAULT 0, safety_stock INTEGER DEFAULT 0, status TEXT NOT NULL DEFAULT 'active', deleted_at TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_storeinv ON store_inventory(tenant_id, store_id, product_id);
CREATE TABLE IF NOT EXISTS riders (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, uid TEXT, name TEXT NOT NULL, phone TEXT, vehicle TEXT, store_id INTEGER, city TEXT, status TEXT NOT NULL DEFAULT 'offline', shift_start TEXT, shift_end TEXT, rating REAL, deliveries INTEGER DEFAULT 0, deleted_at TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_riders_tenant ON riders(tenant_id, status);
CREATE TABLE IF NOT EXISTS dispatch_runs (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT, store_id INTEGER, slot_id INTEGER, rider_id INTEGER, order_ids TEXT DEFAULT '[]', status TEXT NOT NULL DEFAULT 'assigned', batch_count INTEGER DEFAULT 0, pod_otp TEXT, pod_at TEXT, notes TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_dispatch_tenant ON dispatch_runs(tenant_id, status);
CREATE TABLE IF NOT EXISTS upi_handles (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, owner TEXT NOT NULL, vpa TEXT NOT NULL, name TEXT, verified INTEGER DEFAULT 0, is_default INTEGER DEFAULT 0, status TEXT NOT NULL DEFAULT 'active', created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_upi_owner ON upi_handles(tenant_id, owner);
CREATE TABLE IF NOT EXISTS upi_collects (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT, owner TEXT, payer_vpa TEXT, amount REAL NOT NULL, currency TEXT, note TEXT, status TEXT NOT NULL DEFAULT 'initiated', txn_ref TEXT, expires_at TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_collect_tenant ON upi_collects(tenant_id, status);
CREATE TABLE IF NOT EXISTS qr_codes (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT, kind TEXT NOT NULL DEFAULT 'upi', payload TEXT NOT NULL, label TEXT, amount REAL, owner TEXT, svg TEXT, scans INTEGER DEFAULT 0, status TEXT NOT NULL DEFAULT 'active', created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_qr_tenant ON qr_codes(tenant_id, kind, status);
CREATE TABLE IF NOT EXISTS payment_links (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT, token TEXT NOT NULL, title TEXT, amount REAL NOT NULL, currency TEXT, owner TEXT, gateway TEXT, purpose TEXT, expires_at TEXT, paid_at TEXT, status TEXT NOT NULL DEFAULT 'issued', txn_ref TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_paylinks_tenant ON payment_links(tenant_id, status);
CREATE TABLE IF NOT EXISTS mandates (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT, owner TEXT NOT NULL, mandate_id TEXT, gateway TEXT, max_amount REAL, frequency TEXT, purpose TEXT, status TEXT NOT NULL DEFAULT 'registered', next_charge_at TEXT, charged_amount REAL DEFAULT 0, charges_done INTEGER DEFAULT 0, created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_mandates_owner ON mandates(tenant_id, owner, status);
CREATE TABLE IF NOT EXISTS escrow_holds (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT, order_id INTEGER, buyer TEXT, seller TEXT, amount REAL NOT NULL, currency TEXT, held INTEGER DEFAULT 1, released_at TEXT, dispute_opened INTEGER DEFAULT 0, status TEXT NOT NULL DEFAULT 'held', meta TEXT DEFAULT '{}', created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_escrow_tenant ON escrow_holds(tenant_id, status);
CREATE TABLE IF NOT EXISTS split_payments (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT, payment_id INTEGER, order_id INTEGER, splits TEXT NOT NULL DEFAULT '[]', status TEXT NOT NULL DEFAULT 'pending', settled_at TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_splits_tenant ON split_payments(tenant_id, status);
CREATE TABLE IF NOT EXISTS kyc_profiles (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, owner TEXT NOT NULL, kind TEXT NOT NULL DEFAULT 'individual', full_name TEXT, dob TEXT, pan TEXT, aadhaar_masked TEXT, gstin TEXT, company TEXT, website TEXT, doc_type TEXT, doc_ref TEXT, doc_status TEXT NOT NULL DEFAULT 'unverified', status TEXT NOT NULL DEFAULT 'pending', verified_at TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_kyc_owner ON kyc_profiles(tenant_id, owner, status);
CREATE TABLE IF NOT EXISTS bank_payouts (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT, payee TEXT, amount REAL NOT NULL, currency TEXT, account_name TEXT, account_number TEXT, ifsc TEXT, upi_vpa TEXT, gateway TEXT, status TEXT NOT NULL DEFAULT 'queued', txn_ref TEXT, failure_reason TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_payouts_tenant ON bank_payouts(tenant_id, status);
CREATE TABLE IF NOT EXISTS billers (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, name TEXT NOT NULL, category TEXT NOT NULL, code TEXT, fetch_required INTEGER DEFAULT 1, fields TEXT DEFAULT '[]', status TEXT NOT NULL DEFAULT 'active', position INTEGER DEFAULT 0);
CREATE INDEX IF NOT EXISTS ix_billers_tenant ON billers(tenant_id, category, status);
CREATE TABLE IF NOT EXISTS bill_payments (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT, owner TEXT, biller_id INTEGER, category TEXT, account_no TEXT, amount REAL NOT NULL, currency TEXT, convenience_fee REAL DEFAULT 0, status TEXT NOT NULL DEFAULT 'initiated', txn_ref TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_billpay_tenant ON bill_payments(tenant_id, owner, status);
CREATE TABLE IF NOT EXISTS recharges (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT, owner TEXT, number TEXT NOT NULL, operator TEXT, circle TEXT, plan_id INTEGER, amount REAL NOT NULL, currency TEXT, kind TEXT NOT NULL DEFAULT 'mobile', status TEXT NOT NULL DEFAULT 'initiated', txn_ref TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_recharge_tenant ON recharges(tenant_id, owner, status);
CREATE TABLE IF NOT EXISTS recharge_plans (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, operator TEXT NOT NULL, circle TEXT, kind TEXT NOT NULL DEFAULT 'mobile', amount REAL NOT NULL, currency TEXT, validity TEXT, data TEXT, sms TEXT, calls TEXT, description TEXT, popular INTEGER DEFAULT 0, status TEXT NOT NULL DEFAULT 'active', position INTEGER DEFAULT 0);
CREATE INDEX IF NOT EXISTS ix_plans_tenant ON recharge_plans(tenant_id, operator, kind);
CREATE TABLE IF NOT EXISTS bnpl_accounts (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, owner TEXT NOT NULL, provider TEXT, credit_limit REAL DEFAULT 0, used REAL DEFAULT 0, available REAL DEFAULT 0, tenure_months INTEGER DEFAULT 3, status TEXT NOT NULL DEFAULT 'inactive', kyc_id INTEGER, created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_bnpl_owner ON bnpl_accounts(tenant_id, owner, status);
CREATE TABLE IF NOT EXISTS bnpl_emis (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, account_id INTEGER NOT NULL, order_id INTEGER, installment_no INTEGER, amount REAL, due_at TEXT, status TEXT NOT NULL DEFAULT 'upcoming', paid_at TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_emi_account ON bnpl_emis(tenant_id, account_id, status);
CREATE TABLE IF NOT EXISTS loans (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT, owner TEXT NOT NULL, principal REAL NOT NULL, currency TEXT, tenure_months INTEGER, rate REAL, emi REAL, processing_fee REAL, disbursed_at TEXT, status TEXT NOT NULL DEFAULT 'applied', kyc_id INTEGER, created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_loans_tenant ON loans(tenant_id, owner, status);
CREATE TABLE IF NOT EXISTS insurance_policies (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT, owner TEXT NOT NULL, product_id INTEGER, plan_name TEXT, premium REAL NOT NULL, currency TEXT, cover REAL, starts_at TEXT, ends_at TEXT, nominees TEXT, status TEXT NOT NULL DEFAULT 'quoted', created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_insurance_tenant ON insurance_policies(tenant_id, owner, status);
CREATE TABLE IF NOT EXISTS gift_vouchers (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, code TEXT NOT NULL, amount REAL NOT NULL, currency TEXT, buyer TEXT, recipient TEXT, recipient_email TEXT, message TEXT, expires_at TEXT, redeemed_at TEXT, redeemed_by TEXT, status TEXT NOT NULL DEFAULT 'issued', created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_voucher_tenant ON gift_vouchers(tenant_id, code, status);
CREATE TABLE IF NOT EXISTS seller_onboarding (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, seller_id INTEGER, ref TEXT, business_name TEXT NOT NULL, business_type TEXT, gstin TEXT, pan TEXT, tan TEXT, bank_name TEXT, bank_account TEXT, bank_ifsc TEXT, docs TEXT DEFAULT '[]', status TEXT NOT NULL DEFAULT 'submitted', submitted_at TEXT, reviewed_at TEXT, reviewed_by TEXT, notes TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_onb_tenant ON seller_onboarding(tenant_id, status);
CREATE TABLE IF NOT EXISTS seller_offers (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, product_id TEXT NOT NULL, sku_id INTEGER, seller_id INTEGER NOT NULL, price REAL NOT NULL, currency TEXT, condition TEXT DEFAULT 'new', fulfillment TEXT DEFAULT 'fbm', handling_hours INTEGER, shipping_days INTEGER, offer_status TEXT NOT NULL DEFAULT 'active', buybox INTEGER DEFAULT 0, buybox_score REAL DEFAULT 0, deleted_at TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_offers_product ON seller_offers(tenant_id, product_id, offer_status, price);
CREATE TABLE IF NOT EXISTS fba_inbound (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT, seller_id INTEGER, warehouse_id INTEGER, sku_id INTEGER, units INTEGER, status TEXT NOT NULL DEFAULT 'created', fee REAL, tracking_ref TEXT, received_at TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_fba_tenant ON fba_inbound(tenant_id, seller_id, status);
CREATE TABLE IF NOT EXISTS seller_performance (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, seller_id INTEGER NOT NULL, period TEXT NOT NULL, orders INTEGER DEFAULT 0, odr REAL DEFAULT 0, odr_targets INTEGER DEFAULT 0, late_ship_rate REAL DEFAULT 0, late_shipments INTEGER DEFAULT 0, cancel_rate REAL DEFAULT 0, cancellations INTEGER DEFAULT 0, valid_tracked_rate REAL DEFAULT 0, health_score REAL DEFAULT 0, tier TEXT DEFAULT 'standard', status TEXT NOT NULL DEFAULT 'computed', created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_perf_seller ON seller_performance(tenant_id, seller_id, period);
CREATE TABLE IF NOT EXISTS buyer_claims (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT, order_id INTEGER, buyer TEXT, seller_id INTEGER, kind TEXT NOT NULL DEFAULT 'atoz', reason TEXT, amount REAL, currency TEXT, evidence TEXT DEFAULT '[]', status TEXT NOT NULL DEFAULT 'opened', resolution TEXT, resolved_at TEXT, resolved_by TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_claims_tenant ON buyer_claims(tenant_id, status);
CREATE TABLE IF NOT EXISTS smart_fulfilment (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, seller_id INTEGER, ref TEXT, grade TEXT DEFAULT 'b', sla_hours INTEGER, packed_same_day INTEGER DEFAULT 0, score REAL DEFAULT 0, status TEXT NOT NULL DEFAULT 'enrolled', created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_smartful_tenant ON smart_fulfilment(tenant_id, seller_id);
CREATE TABLE IF NOT EXISTS sponsored_creatives (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ad_id INTEGER, seller_id INTEGER, kind TEXT NOT NULL DEFAULT 'sponsored_product', headline TEXT, creative TEXT, landing TEXT, bid_model TEXT, bid_amount REAL, budget REAL, spent REAL DEFAULT 0, status TEXT NOT NULL DEFAULT 'draft', start_at TEXT, end_at TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_creative_tenant ON sponsored_creatives(tenant_id, kind, status);
CREATE TABLE IF NOT EXISTS trade_assurance (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT, order_id INTEGER, buyer TEXT, seller TEXT, amount REAL NOT NULL, currency TEXT, fee REAL, milestones TEXT DEFAULT '[]', current_milestone TEXT, held INTEGER DEFAULT 1, released_at TEXT, status TEXT NOT NULL DEFAULT 'holding', created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_ta_tenant ON trade_assurance(tenant_id, status);
CREATE TABLE IF NOT EXISTS gold_suppliers (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, supplier_id INTEGER NOT NULL, tier TEXT NOT NULL DEFAULT 'gold', starts_at TEXT, ends_at TEXT, fee REAL, currency TEXT, verified INTEGER DEFAULT 0, verification_level TEXT, status TEXT NOT NULL DEFAULT 'active', created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_gold_tenant ON gold_suppliers(tenant_id, supplier_id, status);
CREATE TABLE IF NOT EXISTS company_verifications (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, supplier_id INTEGER, ref TEXT, company_name TEXT NOT NULL, country TEXT, registration_no TEXT, year_established TEXT, employees TEXT, revenue TEXT, export_share TEXT, audit_docs TEXT DEFAULT '[]', audit_by TEXT, audit_at TEXT, verification_status TEXT NOT NULL DEFAULT 'pending', badges TEXT DEFAULT '[]', notes TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_verif_tenant ON company_verifications(tenant_id, verification_status);
CREATE TABLE IF NOT EXISTS export_documents (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT, order_id INTEGER, doc_kind TEXT NOT NULL, buyer TEXT, consignee TEXT, shipper TEXT, origin_country TEXT, dest_country TEXT, port_loading TEXT, port_discharge TEXT, incoterms TEXT, currency TEXT, total_value REAL, hs_codes TEXT, packages INTEGER, gross_weight REAL, net_weight REAL, marks TEXT, body TEXT, rendered TEXT, status TEXT NOT NULL DEFAULT 'draft', created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_exportdocs_tenant ON export_documents(tenant_id, doc_kind, status);
CREATE TABLE IF NOT EXISTS letters_of_credit (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT, order_id INTEGER, buyer TEXT, seller TEXT, issuing_bank TEXT, advising_bank TEXT, lc_number TEXT, amount REAL NOT NULL, currency TEXT, issue_date TEXT, expiry_date TEXT, port_loading TEXT, port_discharge TEXT, latest_shipment TEXT, docs_required TEXT DEFAULT '[]', status TEXT NOT NULL DEFAULT 'issued', created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_lc_tenant ON letters_of_credit(tenant_id, status);
CREATE TABLE IF NOT EXISTS rfq_quotes (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, rfq_id INTEGER NOT NULL, supplier_id INTEGER, seller_id INTEGER, unit_price REAL NOT NULL, currency TEXT, moq INTEGER, lead_days INTEGER, payment_terms TEXT, validity_days INTEGER, quote_ref TEXT, attachments TEXT DEFAULT '[]', status TEXT NOT NULL DEFAULT 'submitted', rank INTEGER, created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_rfqquotes_tenant ON rfq_quotes(tenant_id, rfq_id, status);
CREATE TABLE IF NOT EXISTS tender_bids (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, tender_id INTEGER NOT NULL, bidder TEXT NOT NULL, amount REAL NOT NULL, currency TEXT, terms TEXT, bid_ref TEXT, attachments TEXT DEFAULT '[]', status TEXT NOT NULL DEFAULT 'submitted', rank INTEGER, submitted_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_tenderbids_tender ON tender_bids(tender_id, status);
CREATE TABLE IF NOT EXISTS price_lists (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, name TEXT NOT NULL, currency TEXT, segment TEXT, starts_at TEXT, ends_at TEXT, status TEXT NOT NULL DEFAULT 'active', created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_pricelists_tenant ON price_lists(tenant_id, status);
CREATE TABLE IF NOT EXISTS price_list_items (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, price_list_id INTEGER NOT NULL, product_id TEXT, sku_id INTEGER, price REAL NOT NULL, min_qty INTEGER DEFAULT 1, max_qty INTEGER, status TEXT NOT NULL DEFAULT 'active', created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_plitems_pl ON price_list_items(price_list_id, product_id);
CREATE TABLE IF NOT EXISTS gift_registries (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT, owner TEXT NOT NULL, name TEXT NOT NULL, event TEXT, event_date TEXT, shipping_address TEXT, notes TEXT, items TEXT DEFAULT '[]', contributors TEXT DEFAULT '[]', status TEXT NOT NULL DEFAULT 'open', created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_registry_owner ON gift_registries(tenant_id, owner, status);
CREATE TABLE IF NOT EXISTS notifications (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, owner TEXT, kind TEXT NOT NULL, title TEXT NOT NULL, body TEXT, link TEXT, read INTEGER DEFAULT 0, meta TEXT DEFAULT '{}', created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_notif_owner ON notifications(tenant_id, owner, read, created_at);
CREATE TABLE IF NOT EXISTS compare_lists (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, owner TEXT NOT NULL, product_ids TEXT DEFAULT '[]', created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_compare_owner ON compare_lists(tenant_id, owner);
CREATE TABLE IF NOT EXISTS invoice_documents (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, ref TEXT, order_id INTEGER, owner TEXT, doc_kind TEXT NOT NULL, invoice_number TEXT, place_of_supply TEXT, gstin TEXT, pan TEXT, taxable REAL, tax REAL, total REAL, currency TEXT, body TEXT, rendered TEXT, status TEXT NOT NULL DEFAULT 'generated', created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_invoicedocs_tenant ON invoice_documents(tenant_id, order_id, doc_kind);

/* THE CAPABILITY LAYER — every business rule of the parity engines is a row
   here, individually switchable + tunable per tenant. Mirrored from lib/db.js. */
CREATE TABLE IF NOT EXISTS platform_capabilities (id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT NOT NULL UNIQUE, label TEXT NOT NULL, domain TEXT NOT NULL, icon TEXT, description TEXT, params TEXT NOT NULL DEFAULT '{}', enabled INTEGER DEFAULT 1, position INTEGER DEFAULT 0, seeded_from TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_pcap_domain ON platform_capabilities(domain, enabled);
CREATE TABLE IF NOT EXISTS capability_values (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, capability TEXT NOT NULL, enabled INTEGER DEFAULT 1, params TEXT NOT NULL DEFAULT '{}', notes TEXT, UNIQUE(tenant_id, capability));
CREATE INDEX IF NOT EXISTS ix_capvals_tenant ON capability_values(tenant_id, capability);
CREATE TABLE IF NOT EXISTS capability_presets (id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT NOT NULL UNIQUE, label TEXT NOT NULL, description TEXT, capabilities TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL DEFAULT (datetime('now')));
CREATE INDEX IF NOT EXISTS ix_cappreset_key ON capability_presets(key);
CREATE TABLE IF NOT EXISTS capability_preset_assignments (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, preset_key TEXT NOT NULL, UNIQUE(tenant_id, preset_key));

/* THE TENANCY HIERARCHY — Platform → Tenant → Organization → Business Unit → Brand →
   Store → Channel. One row per node; the materialized `path` makes a subtree a LIKE away,
   and the tree doubles as the CONFIG CASCADE (a key resolved at a Store inherits up the
   chain, deepest wins). Mirrored from lib/db.js. */
CREATE TABLE IF NOT EXISTS tenancy_nodes (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, kind TEXT NOT NULL, parent_id INTEGER, slug TEXT NOT NULL, name TEXT NOT NULL, path TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'active', profile TEXT DEFAULT '{}', config TEXT DEFAULT '{}', uid TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')), UNIQUE(tenant_id, path));
CREATE INDEX IF NOT EXISTS ix_tenancy_parent ON tenancy_nodes(tenant_id, parent_id);
CREATE INDEX IF NOT EXISTS ix_tenancy_kind ON tenancy_nodes(tenant_id, kind);
CREATE TABLE IF NOT EXISTS tenancy_config (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, node_id INTEGER NOT NULL, key TEXT NOT NULL, value TEXT DEFAULT '{}', updated_at TEXT NOT NULL DEFAULT (datetime('now')), UNIQUE(tenant_id, node_id, key));
