/* LUXORA Platform — affiliate domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the affiliate domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "affiliate", routes(kit) {
  const { AFFILIATE_COLS, T, all, bad, json, requireAdmin, run, search } = kit;

  /* ========== Affiliate Network APIs ==========
     S1: this block was entirely unauthenticated and unscoped — an anonymous
     caller could register an affiliate, attribute another tenant's order to it,
     and pay itself the commission. Every management route now passes the store's
     admin gate, every query carries the session's tenant, and the tenant comes
     from the session, never the body. The one exception is the storefront
     tracking pixel (click), which is anonymous by design and was already scoped
     by the store the request resolved to. */
  function apiAffiliateNetworks(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { networks: all('SELECT * FROM affiliate_networks WHERE tenant_id=? OR tenant_id IS NULL ORDER BY id', T(s)) });
  }
  function apiAffiliateNetworkCreate(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    if (!body.name) return bad(res, 'name required', 400);
    const tenantId = T(s);
    const r = run('INSERT INTO affiliate_networks(name,slug,tenant_id,status,default_commission_pct,cookie_days,attribution_model,currency) VALUES(?,?,?,?,?,?,?,?)',
      body.name, body.slug || body.name.toLowerCase().replace(/\s+/g, '-'), tenantId, body.status || 'active', body.default_commission_pct || 5.0, body.cookie_days || 30, body.attribution_model || require("../defaults.js").of("goipAttributionModels"), require("../defaults.js").currency(tenantId));
    json(res, 200, { ok: true, id: Number(r.lastInsertRowid) });
  }
  function apiAffiliateList(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    const networkId = url.searchParams.get('network_id');
    const status = url.searchParams.get('status');
    const search = url.searchParams.get('search');
    let q = 'SELECT * FROM affiliates WHERE tenant_id=?';
    const p = [T(s)];
    if (networkId) { q += ' AND network_id=?'; p.push(Number(networkId)); }
    if (status) { q += ' AND status=?'; p.push(status); }
    if (search) { q += ' AND (name LIKE ? OR affiliate_code LIKE ?)'; p.push('%' + search + '%', '%' + search + '%'); }
    json(res, 200, { affiliates: all(q + ' ORDER BY created_at DESC', ...p) });
  }
  function apiAffiliateCreate(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    if (!body.name) return bad(res, 'name required', 400);
    const tenantId = T(s);
    const code = body.affiliate_code || 'AFF-' + Math.random().toString(36).slice(2,8).toUpperCase();
    const r = run('INSERT INTO affiliates(network_id,tenant_id,name,email,status,affiliate_code,commission_type,tier) VALUES(?,?,?,?,?,?,?,?)',
      body.network_id || 1, tenantId, body.name, body.email, 'pending', code, body.commission_type || 'revenue', body.tier || require("../defaults.js").of("affiliateTiers"));
    json(res, 200, { ok: true, id: Number(r.lastInsertRowid), code });
  }
  function apiAffiliateGet(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { affiliate: all('SELECT * FROM affiliates WHERE id=? AND tenant_id=?', id, T(s))[0] });
  }
  function apiAffiliateUpdate(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const updates = [];
    const p = [];
    for (const [k, v] of Object.entries(body)) {
      if (AFFILIATE_COLS.includes(k)) { updates.push(k + '=?'); p.push(v); }
    }
    if (!updates.length) return bad(res, 'no updatable fields provided', 400);
    p.push(body.id, T(s));
    run('UPDATE affiliates SET ' + updates.join(',') + ' WHERE id=? AND tenant_id=?', ...p);
    json(res, 200, { ok: true });
  }
  /* the storefront pixel: a shopper clicking an affiliate link. Anonymous by
     design — the click is recorded against the store the request resolved to,
     which is the only tenant it can ever be read back by */
  function apiAffiliateClick(req, res, url, s, body) {
    const tenantId = T(s);
    const clickId = 'clk-' + Date.now() + '-' + Math.random().toString(36).slice(2,6);
    run('INSERT INTO affiliate_clicks(affiliate_id,network_id,tenant_id,click_id,referrer,landing_url,campaign,source,medium) VALUES(?,?,?,?,?,?,?,?,?)',
      body.affiliate_id, body.network_id || 1, tenantId, clickId, body.referrer || '', body.landing_url || '', body.campaign || '', body.source || '', body.medium || '');
    json(res, 200, { click_id: clickId });
  }
  /* S1: the order must be THIS tenant's order and the affiliate THIS tenant's
     affiliate — otherwise the commission is a cross-tenant transfer, and the
     returned commission was a cross-tenant revenue oracle */
  function apiAffiliateConversion(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const tenantId = T(s);
    const order = all('SELECT * FROM orders WHERE id=? AND tenant_id=?', body.order_id, tenantId)[0];
    if (!order) return bad(res, 'order not found', 404);
    const aff = all('SELECT id FROM affiliates WHERE id=? AND tenant_id=?', body.affiliate_id, tenantId)[0];
    if (!aff) return bad(res, 'affiliate not found', 404);
    const commission = body.commission || (order.total * (body.commission_pct || 5) / 100);
    const r = run('INSERT INTO affiliate_conversions(affiliate_id,network_id,tenant_id,order_id,order_num,revenue,commission,commission_pct) VALUES(?,?,?,?,?,?,?,?)',
      body.affiliate_id, body.network_id || 1, tenantId, body.order_id, order.num, order.total, commission, body.commission_pct || 5);
    const convId = Number(r.lastInsertRowid);
    run('UPDATE affiliates SET balance = balance + ?, lifetime_sales = lifetime_sales + ?, lifetime_commissions = lifetime_commissions + ? WHERE id=? AND tenant_id=?',
      commission, order.total, commission, body.affiliate_id, tenantId);
    json(res, 200, { ok: true, conversion_id: convId, commission });
  }
  function apiAffiliateConversionGet(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { conversion: all('SELECT * FROM affiliate_conversions WHERE id=? AND tenant_id=?', id, T(s))[0] });
  }
  function apiAffiliateApprove(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    run('UPDATE affiliate_conversions SET status=?,approved_at=? WHERE id=? AND tenant_id=?', 'approved', new Date().toISOString(), body.id, T(s));
    json(res, 200, { ok: true });
  }
  function apiAffiliateReject(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    run('UPDATE affiliate_conversions SET status=?,approved_at=? WHERE id=? AND tenant_id=?', 'rejected', new Date().toISOString(), body.id, T(s));
    json(res, 200, { ok: true });
  }
  /* payouts carry no tenant column: scope through the affiliate they belong to,
     so one store can never see — or process — another store's payouts */
  function apiAffiliatePayouts(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    const affiliateId = url.searchParams.get('affiliate_id');
    const q = 'SELECT p.* FROM affiliate_payouts p JOIN affiliates a ON a.id=p.affiliate_id WHERE a.tenant_id=?';
    json(res, 200, { payouts: all(affiliateId ? q + ' AND p.affiliate_id=? ORDER BY p.created_at DESC' : q + ' ORDER BY p.created_at DESC',
      ...(affiliateId ? [T(s), Number(affiliateId)] : [T(s)])) });
  }
  function apiAffiliatePayoutCreate(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    if (!(body.amount >= 1)) return bad(res, 'amount must be at least 1', 400);
    const aff = all('SELECT id, network_id, balance FROM affiliates WHERE id=? AND tenant_id=?', body.affiliate_id, T(s))[0];
    if (!aff) return bad(res, 'affiliate not found', 404);
    run('INSERT INTO affiliate_payouts(affiliate_id,network_id,amount,status,method) VALUES(?,?,?,?,?)',
      aff.id, aff.network_id || 1, body.amount, 'pending', body.method || 'bank');
    json(res, 200, { ok: true });
  }
  function apiAffiliatePayoutProcess(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const p = all('SELECT p.id FROM affiliate_payouts p JOIN affiliates a ON a.id=p.affiliate_id WHERE p.id=? AND a.tenant_id=?', body.id, T(s))[0];
    if (!p) return bad(res, 'payout not found', 404);
    run('UPDATE affiliate_payouts SET status=?,paid_at=?,transaction_ref=? WHERE id=?', 'paid', new Date().toISOString(), 'TXN-' + Date.now(), body.id);
    json(res, 200, { ok: true });
  }
  function apiAffiliateReport(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    const networkId = url.searchParams.get('network_id') || 1;
    const summary = all('SELECT COUNT(*) as affiliates, SUM(lifetime_sales) as sales, SUM(lifetime_commissions) as commissions FROM affiliates WHERE network_id=? AND status=? AND tenant_id=?', networkId, 'active', T(s))[0];
    const topAffiliates = all('SELECT name,affiliate_code,lifetime_sales,lifetime_commissions FROM affiliates WHERE network_id=? AND status=? AND tenant_id=? ORDER BY lifetime_sales DESC LIMIT 10', networkId, 'active', T(s));
    json(res, 200, { 
      summary: { affiliates: summary.affiliates || 0, sales: summary.sales || 0, commissions: summary.commissions || 0 },
      top_affiliates: topAffiliates
    });
  }

  return [
    ["GET /api/affiliate/networks", apiAffiliateNetworks],
    ["POST /api/affiliate/networks", apiAffiliateNetworkCreate],
    ["GET /api/affiliate/affiliates", apiAffiliateList],
    ["POST /api/affiliate/affiliates", apiAffiliateCreate],
    ["GET /api/affiliate/affiliates/:id", apiAffiliateGet],
    ["PUT /api/affiliate/affiliates/:id", apiAffiliateUpdate],
    ["POST /api/affiliate/click", apiAffiliateClick],
    ["POST /api/affiliate/conversion", apiAffiliateConversion],
    ["GET /api/affiliate/conversions/:id", apiAffiliateConversionGet],
    ["POST /api/affiliate/conversions/:id/approve", apiAffiliateApprove],
    ["POST /api/affiliate/conversions/:id/reject", apiAffiliateReject],
    ["GET /api/affiliate/payouts", apiAffiliatePayouts],
    ["POST /api/affiliate/payouts", apiAffiliatePayoutCreate],
    ["POST /api/affiliate/payouts/:id/process", apiAffiliatePayoutProcess],
    ["GET /api/affiliate/reports", apiAffiliateReport]
  ];
} };
