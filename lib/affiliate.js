/* LUXORA Platform - Affiliate Network Module
   Full-stack affiliate tracking, attribution, commissions, and payouts.
   Built on top of GOIP touchpoints and settlement infrastructure.
   Registry-driven: all rules, tiers, and networks are configurable.
*/
"use strict";

const db = () => require("./db.js");
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d || {}; } };
const r2 = n => +Number(n || 0).toFixed(2);
const nowIso = () => new Date().toISOString();
const today = () => new Date().toISOString().slice(0, 10);

/* ═══════════════ 1 · DATABASE TABLES ═══════════════ */
function seed() {
  const run = (sql, ...params) => { try { db().run(sql, ...params); } catch (e) { } };
  run(`CREATE TABLE IF NOT EXISTS affiliate_networks (
    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, slug TEXT UNIQUE, tenant_id INTEGER DEFAULT 1,
    status TEXT DEFAULT 'active', default_commission_pct REAL DEFAULT 5.0, cookie_days INTEGER DEFAULT 30,
    attribution_model TEXT DEFAULT 'last_touch', min_payout REAL DEFAULT 50.0, currency TEXT DEFAULT 'USD',
    created_at TEXT DEFAULT (datetime('now')), uid TEXT )`);
  run(`CREATE TABLE IF NOT EXISTS affiliates (
    id INTEGER PRIMARY KEY AUTOINCREMENT, network_id INTEGER REFERENCES affiliate_networks(id), tenant_id INTEGER DEFAULT 1,
    name TEXT NOT NULL, email TEXT UNIQUE, status TEXT DEFAULT 'pending', affiliate_code TEXT UNIQUE,
    tracking_url TEXT, deep_link_template TEXT, commission_pct REAL, commission_type TEXT DEFAULT 'revenue',
    tier TEXT DEFAULT 'standard', balance REAL DEFAULT 0, lifetime_sales REAL DEFAULT 0,
    lifetime_commissions REAL DEFAULT 0, created_at TEXT DEFAULT (datetime('now')), last_activity TEXT,
    metadata TEXT DEFAULT '{}', uid TEXT )`);
  run(`CREATE TABLE IF NOT EXISTS affiliate_clicks (
    id INTEGER PRIMARY KEY AUTOINCREMENT, affiliate_id INTEGER REFERENCES affiliates(id),
    network_id INTEGER REFERENCES affiliate_networks(id), tenant_id INTEGER DEFAULT 1,
    click_id TEXT UNIQUE, ip TEXT, user_agent TEXT, referrer TEXT, landing_url TEXT,
    campaign TEXT, source TEXT, medium TEXT, created_at TEXT DEFAULT (datetime('now')), uid TEXT )`);
  run(`CREATE TABLE IF NOT EXISTS affiliate_conversions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, affiliate_id INTEGER REFERENCES affiliates(id),
    network_id INTEGER REFERENCES affiliate_networks(id), tenant_id INTEGER DEFAULT 1,
    click_id TEXT REFERENCES affiliate_clicks(click_id), order_id INTEGER REFERENCES orders(id),
    order_num TEXT, conversion_type TEXT DEFAULT 'sale', revenue REAL, commission REAL,
    commission_pct REAL, status TEXT DEFAULT 'pending', approved_at TEXT, paid_at TEXT,
    payment_id INTEGER, created_at TEXT DEFAULT (datetime('now')), uid TEXT )`);
  run(`CREATE TABLE IF NOT EXISTS commission_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT, network_id INTEGER REFERENCES affiliate_networks(id),
    tenant_id INTEGER DEFAULT 1, name TEXT NOT NULL, status TEXT DEFAULT 'active',
    applies_to TEXT DEFAULT 'all', condition TEXT DEFAULT '{}', commission_type TEXT DEFAULT 'revenue',
    commission_value REAL, min_order REAL DEFAULT 0, max_order REAL, tier TEXT,
    product_ids TEXT, category_ids TEXT, brand_ids TEXT, start_date TEXT, end_date TEXT,
    position INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now')), uid TEXT )`);
  run(`CREATE TABLE IF NOT EXISTS affiliate_tiers (
    id INTEGER PRIMARY KEY AUTOINCREMENT, network_id INTEGER REFERENCES affiliate_networks(id),
    name TEXT NOT NULL, min_sales REAL DEFAULT 0, commission_bonus_pct REAL DEFAULT 0,
    benefits TEXT DEFAULT '[]', position INTEGER DEFAULT 0, uid TEXT )`);
  run(`CREATE TABLE IF NOT EXISTS affiliate_payouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT, affiliate_id INTEGER REFERENCES affiliates(id),
    network_id INTEGER REFERENCES affiliate_networks(id), amount REAL NOT NULL,
    status TEXT DEFAULT 'pending', method TEXT DEFAULT 'bank', transaction_ref TEXT,
    paid_at TEXT, created_at TEXT DEFAULT (datetime('now')), uid TEXT )`);
}

/* ═══════════════ 2 · NETWORK & AFFILIATE MANAGEMENT ═══════════════ */
function createNetwork(input) {
  const n = input || {};
  const name = n.name || 'Default Network';
  const slug = n.slug || name.toLowerCase().replace(/\s+/g, '-');
  db().run('INSERT INTO affiliate_networks(name, slug, tenant_id, status, default_commission_pct, cookie_days, attribution_model, min_payout, currency) VALUES(?,?,?,?,?,?,?,?,?)',
    name, slug, n.tenant_id || 1, n.status || 'active', n.default_commission_pct || 5.0, n.cookie_days || 30, n.attribution_model || require("./defaults.js").of("goipAttributionModels"), n.min_payout || 50.0, n.currency || require("./defaults.js").currency(n.tenant_id));
  return getNetwork(db().get('SELECT last_insert_rowid() as id').id);
}
function getNetwork(id) { return db().get('SELECT * FROM affiliate_networks WHERE id=?', id) || null; }
function listNetworks(tenantId) { return db().all('SELECT * FROM affiliate_networks WHERE tenant_id=? OR tenant_id IS NULL ORDER BY id', tenantId || 1); }

function createAffiliate(input) {
  const a = input || {};
  const network = getNetwork(a.network_id) || getNetwork(1);
  if (!network) return { error: 'Network not found', code: 404 };
  const code = a.affiliate_code || 'AFF-' + Math.random().toString(36).slice(2, 8).toUpperCase();
  const trackingUrl = a.tracking_url || '';
  db().run('INSERT INTO affiliates(network_id, tenant_id, name, email, status, affiliate_code, tracking_url, commission_pct, commission_type, tier, metadata) VALUES(?,?,?,?,?,?,?,?,?,?,?)',
    network.id, a.tenant_id || 1, a.name, a.email, 'pending', code, trackingUrl, a.commission_pct || null, a.commission_type || 'revenue', a.tier || 'standard', JSON.stringify(a.metadata || {}));
  return getAffiliate(db().get('SELECT last_insert_rowid() as id').id);
}
function getAffiliate(id) {
  const row = db().get('SELECT * FROM affiliates WHERE id=?', id);
  if (!row) return null;
  return { ...row, metadata: J(row.metadata, {}) };
}
function listAffiliates(networkId, filters) {
  const f = filters || {}, where = ['network_id=?'], params = [networkId];
  if (f.status) { where.push('status=?'); params.push(f.status); }
  if (f.search) { where.push('(name LIKE ? OR affiliate_code LIKE ?)'); params.push('%' + f.search + '%', '%' + f.search + '%'); }
  return db().all('SELECT * FROM affiliates WHERE ' + where.join(' AND ') + ' ORDER BY created_at DESC', params);
}

/* ═══════════════ 3 · TRACKING ═══════════════ */
function trackClick(input) {
  const c = input || {};
  const clickId = 'clk-' + Date.now() + '-' + Math.random().toString(36).slice(2,6);
  db().run('INSERT INTO affiliate_clicks(affiliate_id, network_id, tenant_id, click_id, referrer, landing_url, campaign) VALUES(?,?,?,?,?,?,?)',
    c.affiliate_id, c.network_id || 1, c.tenant_id || 1, clickId, c.referrer || '', c.landing_url || '', c.campaign || '');
  return { click_id: clickId };
}

/* ═══════════════ 4 · CONVERSIONS & COMMISSIONS ═══════════════ */
function getRules(networkId) { return db().all('SELECT * FROM commission_rules WHERE network_id=? AND status=? ORDER BY position', networkId, 'active'); }

function calculateCommission(order, affiliate, ruleSet) {
  const rules = ruleSet || getRules(affiliate.network_id);
  const applicable = rules.filter(r => r.status === 'active');
  const rule = applicable[0] || { commission_type: affiliate.commission_type || 'revenue', commission_value: affiliate.commission_pct || 5.0 };
  const revenue = order.total || 0;
  const commission = rule.commission_type === 'fixed' ? rule.commission_value : revenue * (rule.commission_value / 100);
  return { revenue: r2(revenue), commission: r2(commission), commission_pct: rule.commission_value };
}

function recordConversion(input) {
  const c = input || {};
  const order = c.order_id ? db().get('SELECT * FROM orders WHERE id=?', c.order_id) : null;
  if (!order) return { error: 'Order not found', code: 404 };
  const commission = calculateCommission(order, { network_id: c.network_id || 1, commission_type: c.commission_type || 'revenue', commission_pct: c.commission_pct || 5 });
  db().run('INSERT INTO affiliate_conversions(affiliate_id, network_id, tenant_id, order_id, order_num, revenue, commission, commission_pct) VALUES(?,?,?,?,?,?,?,?)',
    c.affiliate_id, c.network_id || 1, c.tenant_id || 1, c.order_id, order.num, commission.revenue, commission.commission, commission.commission_pct);
  db().run('UPDATE affiliates SET balance = balance + ?, lifetime_sales = lifetime_sales + ?, lifetime_commissions = lifetime_commissions + ? WHERE id=?',
    commission.commission, commission.revenue, commission.commission, c.affiliate_id);
  return { commission: commission.commission };
}

/* ═══════════════ 5 · PAYOUTS ═══════════════ */
function createPayout(input) {
  const p = input || {};
  const affiliate = db().get('SELECT * FROM affiliates WHERE id=?', p.affiliate_id);
  if (!affiliate) return { error: 'Affiliate not found', code: 404 };
  if (affiliate.balance < p.amount) return { error: 'Insufficient balance', code: 400 };
  db().run('INSERT INTO affiliate_payouts(affiliate_id, network_id, amount, status, method) VALUES(?,?,?,?,?)',
    affiliate.id, affiliate.network_id, p.amount, 'pending', p.method || 'bank');
  db().run('UPDATE affiliates SET balance = balance - ? WHERE id=?', p.amount, affiliate.id);
  return { ok: true };
}

/* ═══════════════ 6 · REPORTS ═══════════════ */
function getReport(networkId) {
  const summary = db().get('SELECT COUNT(*) as affiliates, SUM(lifetime_sales) as sales, SUM(lifetime_commissions) as commissions FROM affiliates WHERE network_id=? AND status=?', networkId, 'active');
  const topAffiliates = db().all('SELECT name, affiliate_code, lifetime_sales, lifetime_commissions FROM affiliates WHERE network_id=? AND status=? ORDER BY lifetime_sales DESC LIMIT 10', networkId, 'active');
  return {
    summary: { affiliates: (summary && summary.affiliates) || 0, sales: r2((summary && summary.sales) || 0), commissions: r2((summary && summary.commissions) || 0) },
    top_affiliates: topAffiliates
  };
}

module.exports = {
  seed,
  createNetwork, getNetwork, listNetworks,
  createAffiliate, getAffiliate, listAffiliates,
  trackClick,
  getRules, calculateCommission, recordConversion,
  createPayout,
  getReport
};
