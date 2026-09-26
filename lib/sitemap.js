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
function getConfig(tenantId) {
  const config = db().get('SELECT * FROM sitemap_config WHERE tenant_id=?', tenantId || 1) || {};
  return { ...DEFAULTS, ...config };
}

function updateConfig(tenantId, patch) {
  const updates = [];
  const params = [];
  for (const [key, value] of Object.entries(patch)) {
    if (['id', 'tenant_id', 'created_at', 'updated_at', 'last_generated', 'next_run'].includes(key)) continue;
    updates.push(key + '=?');
    params.push(value);
  }
  if (updates.length) {
    params.push(tenantId || 1);
    db().run('UPDATE sitemap_config SET ' + updates.join(', ') + ', updated_at=? WHERE tenant_id=?', [...params, nowIso(), tenantId || 1]);
  }
  return getConfig(tenantId);
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
  const params = [tenantId || 1];
  const where = ['tenant_id=?', 'lifecycle=?'];
  params.push(f.status || 'published');
  if (f.limit) { where.push('LIMIT ?'); params.push(f.limit); }
  return db().all('SELECT id, title, brand, dept, price, keywords, created_at FROM products WHERE ' + where.join(' AND '), params);
}

function getCategories(tenantId) {
  return db().all('SELECT DISTINCT dept FROM products WHERE tenant_id=? AND lifecycle=?', tenantId || 1, 'published');
}

function getPages(tenantId) {
  const pages = [
    { loc: '', title: 'Home', type: 'homepage', priority: 1.0 },
    { loc: '/products', title: 'Products', type: 'category', priority: 0.8 },
    { loc: '/deals', title: 'Deals & Offers', type: 'category', priority: 0.8 },
    { loc: '/cart', title: 'Cart', type: 'page', priority: 0.5 },
    { loc: '/checkout', title: 'Checkout', type: 'page', priority: 0.6 },
    { loc: '/customer-service', title: 'Customer Service', type: 'page', priority: 0.5 }
  ];
  return pages;
}

function getEntryLoc(product, hostname, type) {
  if (type === 'product') {
    const slug = (product.title || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
    return `${hostname}/product/${product.id || slug}`;
  }
  if (type === 'category') {
    const deptSlug = (product.dept || 'products').toLowerCase().replace(/[^a-z0-9]+/g, '-');
    return `${hostname}/category/${deptSlug}`;
  }
  return `${hostname}${(product.loc || '').replace(/^\/+/, '')}`;
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
  categories.forEach(cat => {
    entries.push({
      loc: `${config.hostname}/category/${(cat.dept || '').toLowerCase()}`,
      type: 'category',
      priority: config.priority.category,
      changefreq: config.changefreq.category,
      lastmod: today()
    });
  });
  
  /* Products */
  const products = getProducts(tenantId, { status: 'published', limit: config.maxPerFile });
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
  
  /* Store entry */
  db().run('DELETE FROM sitemap_entries WHERE tenant_id=?', tenantId || 1);
  const chunkSize = config.maxPerFile;
  const chunks = [];
  for (let i = 0; i < entries.length; i += chunkSize) {
    chunks.push(entries.slice(i, i + chunkSize));
  }
  
  chunks.forEach((chunk, idx) => {
    const content = generateXML(chunk);
    const filename = `sitemap${idx > 0 ? '_' + idx : ''}.xml`;
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
    xml += `    <loc>${config.hostname}/sitemap/${f.filename}</loc>\n`;
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
  get,
  DEFAULTS
};
