/* LUXORA Platform - Auto-Sitemap Generator for SEO
   Generates dynamic XML/JSON sitemaps with automatic updates
   Supports multi-tenant, multi-currency, and localized content
   Registry-driven: schedule and rules are configurable
*/
"use strict";

const db = () => require("./db.js");
const path = require("path");
const fs = require("fs");

const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d || {}; } };
const nowIso = () => new Date().toISOString();
const toSitemapDate = (d) => d ? new Date(d).toISOString().split('T')[0] : today();
const today = () => new Date().toISOString().slice(0, 10);

const DEFAULTS = {
  hostname: 'https://example.com',
  maxPerFile: 50000,
  priority: {
    homepage: 1.0,
    category: 0.8,
    product: 0.7,
    page: 0.6,
    default: 0.5
  },
  changefreq: {
    homepage: 'daily',
    category: 'weekly',
    product: 'monthly',
    page: 'monthly',
    default: 'monthly'
  },
  schedule: '0 2 * * *' /* cron: 2 AM daily */
};

/* ═══════════════ 1 · TABLES ═══════════════ */
function seed() {
  const run = (sql, ...params) => { try { db().run(sql, ...params); } catch (e) { } };
  
  run(`CREATE TABLE IF NOT EXISTS sitemap_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER DEFAULT 1,
    hostname TEXT,
    max_per_file INTEGER DEFAULT 50000,
    enabled INTEGER DEFAULT 1,
    last_generated TEXT,
    next_run TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
  )`);
  
  run(`CREATE TABLE IF NOT EXISTS sitemap_entries (
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
  )`);
  
  run(`CREATE TABLE IF NOT EXISTS sitemap_files (
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
  )`);
  
  /* Init default config */
  const existing = db().get('SELECT id FROM sitemap_config WHERE tenant_id=?', 1);
  if (!existing) {
    db().run('INSERT INTO sitemap_config(tenant_id, hostname, enabled) VALUES(?,?,?)', 1, DEFAULTS.hostname, 1);
  }
}

/* ═══════════════ 2 · CONFIG MANAGEMENT ═══════════════ */
/* the store's own origin when it has not set one — never a placeholder domain */
function storeOrigin(tenantId) {
  const t = db().get('SELECT domain FROM tenants WHERE id=?', tenantId || 1);
  return t && t.domain ? 'https://' + String(t.domain).replace(/^https?:\/\//, '').replace(/\/+$/, '') : '';
}
function getConfig(tenantId) {
  const row = db().get('SELECT * FROM sitemap_config WHERE tenant_id=?', tenantId || 1) || {};
  const config = { ...DEFAULTS, ...row };
  if (!row.hostname || row.hostname === DEFAULTS.hostname) config.hostname = storeOrigin(tenantId) || DEFAULTS.hostname;
  config.hostname = String(config.hostname).replace(/\/+$/, '');
  config.maxPerFile = Number(row.max_per_file) || DEFAULTS.maxPerFile;
  return config;
}

/* only the declared, operator-editable columns are writable. Keys used to be spliced
   into the SQL as column names straight from the request body (SQL injection), and the
   parameters were passed as one array argument, so every update failed anyway. */
const EDITABLE = {
  hostname: v => { const h = String(v || '').trim(); if (!/^https?:\/\/[^\s/$.?#][^\s]*$/i.test(h)) throw new Error('hostname must be an http(s) URL'); return h.replace(/\/+$/, ''); },
  max_per_file: v => { const n = Math.floor(Number(v)); if (!(n >= 1 && n <= 50000)) throw new Error('max_per_file must be between 1 and 50000'); return n; },
  enabled: v => (v === true || v === 1 || v === '1' || v === 'true') ? 1 : 0
};
function updateConfig(tenantId, patch) {
  const tid = tenantId || 1;
  const cols = [], vals = [];
  for (const [key, value] of Object.entries(patch || {})) {
    if (!EDITABLE[key]) continue;
    cols.push(key); vals.push(EDITABLE[key](value));
  }
  if (!db().get('SELECT id FROM sitemap_config WHERE tenant_id=?', tid))
    db().run('INSERT INTO sitemap_config(tenant_id, enabled) VALUES(?,1)', tid);
  if (cols.length)
    db().run('UPDATE sitemap_config SET ' + cols.map(c => c + '=?').join(', ') + ', updated_at=? WHERE tenant_id=?', ...vals, nowIso(), tid);
  return getConfig(tid);
}

/* ═══════════════ 3 · SITEMAP GENERATION ═══════════════ */
function escapeXml(str) {
  return String(str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

function getProducts(tenantId, filters) {
  const f = filters || {};
  return db().all('SELECT id, title, brand, dept, price, keywords FROM products WHERE tenant_id=? AND lifecycle=? ORDER BY id LIMIT ?',
    tenantId || 1, f.status || 'published', Number(f.limit) || 50000);
}

function getCategories(tenantId) {
  return db().all('SELECT DISTINCT dept FROM products WHERE tenant_id=? AND lifecycle=?', tenantId || 1, 'published');
}

/* the storefront's real, indexable pages (cart/checkout are private and never listed);
   locations match the URLs the server actually serves */
function getPages(tenantId) {
  return [
    { loc: '/deals.html', title: 'Deals & Offers', type: 'category', priority: 0.8 },
    { loc: '/gift-cards.html', title: 'Gift Cards', type: 'page', priority: 0.5 },
    { loc: '/customer-service.html', title: 'Customer Service', type: 'page', priority: 0.5 }
  ];
}

function getEntryLoc(product, hostname, type) {
  if (type === 'product') return `${hostname}/product.html?id=${encodeURIComponent(product.id)}`;
  if (type === 'category') return `${hostname}/results.html?dept=${encodeURIComponent(product.dept || '')}`;
  return `${hostname}/${(product.loc || '').replace(/^\/+/, '')}`;
}

function buildSitemapEntries(tenantId) {
  const config = getConfig(tenantId);
  const entries = [];
  
  /* Homepage */
  entries.push({
    loc: config.hostname,
    type: 'homepage',
    priority: config.priority.homepage,
    changefreq: config.changefreq.homepage,
    lastmod: today()
  });
  
  /* Pages */
  const pages = getPages(tenantId);
  pages.forEach(page => {
    entries.push({
      loc: `${config.hostname}${page.loc}`,
      type: page.type,
      priority: page.priority,
      changefreq: config.changefreq.default,
      lastmod: today()
    });
  });
  
  /* Categories */
  const categories = getCategories(tenantId);
  categories.filter(cat => cat.dept).forEach(cat => {
    entries.push({
      loc: getEntryLoc(cat, config.hostname, 'category'),
      type: 'category',
      priority: config.priority.category,
      changefreq: config.changefreq.category,
      lastmod: today()
    });
  });
  
  /* Products */
  const products = getProducts(tenantId, { status: 'published', limit: 50000 });
  products.forEach(p => {
    entries.push({
      loc: getEntryLoc(p, config.hostname, 'product'),
      type: 'product',
      priority: config.priority.product,
      changefreq: config.changefreq.product,
      lastmod: toSitemapDate(p.created_at)
    });
  });
  
  return entries;
}

function generateXML(entries) {
  let xml = '<?xml version="1.0" encoding="UTF-8"?>\n';
  xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n';
  
  entries.forEach(entry => {
    xml += '  <url>\n';
    xml += `    <loc>${escapeXml(entry.loc)}</loc>\n`;
    xml += `    <lastmod>${entry.lastmod || today()}</lastmod>\n`;
    xml += `    <changefreq>${entry.changefreq || 'monthly'}</changefreq>\n`;
    xml += `    <priority>${entry.priority || 0.5}</priority>\n`;
    xml += '  </url>\n';
  });
  
  xml += '</urlset>';
  return xml;
}

function generateJSON(entries) {
  return JSON.stringify({
    urlset: entries.map(e => ({
      loc: e.loc,
      lastmod: e.lastmod || today(),
      changefreq: e.changefreq || 'monthly',
      priority: e.priority || 0.5
    }))
  }, null, 2);
}

function generate(tenantId, format) {
  const config = getConfig(tenantId);
  if (!config.enabled) return { error: 'Sitemap generation disabled', code: 403 };
  
  const entries = buildSitemapEntries(tenantId);
  const xml = generateXML(entries);
  
  /* the file ledger is per tenant; filenames are tenant-qualified because the column is
     globally UNIQUE (a second store's generate used to collide with the first's) */
  db().run('DELETE FROM sitemap_entries WHERE tenant_id=?', tenantId || 1);
  db().run('DELETE FROM sitemap_files WHERE tenant_id=?', tenantId || 1);
  const chunkSize = config.maxPerFile;
  const chunks = [];
  for (let i = 0; i < entries.length; i += chunkSize) {
    chunks.push(entries.slice(i, i + chunkSize));
  }
  
  chunks.forEach((chunk, idx) => {
    const content = generateXML(chunk);
    const filename = `t${tenantId || 1}-sitemap${idx > 0 ? '_' + idx : ''}.xml`;
    db().run(
      'INSERT INTO sitemap_files(tenant_id, filename, sitemap_type, entry_count, file_size, generated_at, status) VALUES(?,?,?,?,?,?,?)',
      tenantId || 1, filename, 'pages', chunk.length, content.length, nowIso(), 'pending'
    );
  });
  
  db().run('UPDATE sitemap_config SET last_generated=? WHERE tenant_id=?', nowIso(), tenantId || 1);
  
  return {
    hostname: config.hostname,
    entries: entries.length,
    chunks: chunks.length,
    format: format || 'xml',
    content: format === 'json' ? generateJSON(entries) : xml,
    last_generated: nowIso()
  };
}

function generateSitemapIndex(tenantId) {
  const config = getConfig(tenantId);
  const files = db().all('SELECT * FROM sitemap_files WHERE tenant_id=? AND status=? ORDER BY id', tenantId || 1, 'pending');
  
  let xml = '<?xml version="1.0" encoding="UTF-8"?>\n';
  xml += '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n';
  
  files.forEach(f => {
    xml += '  <sitemap>\n';
    xml += `    <loc>${escapeXml(config.hostname + '/sitemap/' + f.filename)}</loc>\n`;
    xml += `    <lastmod>${f.generated_at || today()}</lastmod>\n`;
    xml += '  </sitemap>\n';
  });
  
  xml += '</sitemapindex>';
  return xml;
}

/* ═══════════════ 4 · SCHEDULED UPDATES ═══════════════ */
function schedule(tenantId) {
  const config = getConfig(tenantId);
  const nextRun = new Date();
  nextRun.setHours(2, 0, 0, 0); /* 2 AM */
  if (nextRun <= new Date()) nextRun.setDate(nextRun.getDate() + 1);
  
  db().run('UPDATE sitemap_config SET next_run=? WHERE tenant_id=?', nextRun.toISOString(), tenantId || 1);
  
  return {
    scheduled: true,
    next_run: nextRun.toISOString()
  };
}

function trigger(tenantId) {
  generate(tenantId);
  return { triggered: true, at: nowIso() };
}

/* ═══════════════ 5 · API ROUTE HANDLERS ═══════════════ */
function get(tenantId) {
  const config = getConfig(tenantId);
  const files = db().all('SELECT * FROM sitemap_files WHERE tenant_id=? ORDER BY id', tenantId || 1);
  const entries = db().all('SELECT * FROM sitemap_entries WHERE tenant_id=? ORDER BY id', tenantId || 1);
  
  return {
    config: { ...config, last_generated: config.last_generated ? toSitemapDate(config.last_generated) : null },
    files,
    total_entries: entries.length,
    last_generated: config.last_generated ? toSitemapDate(config.last_generated) : null
  };
}

module.exports = {
  seed,
  getConfig, updateConfig,
  generate, generateXML, generateJSON, generateSitemapIndex,
  schedule, trigger,
  get, buildSitemapEntries,
  DEFAULTS
};
