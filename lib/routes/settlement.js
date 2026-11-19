/* LUXORA Platform — settlement domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the settlement domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "settlement", routes(kit) {
  const { T, all, bad, fin, fintech, get, isAdmin, json, logAction, ownerFor, requireAdmin, requireStaff, run, states } = kit;

  /* ---- Payments & Financial services (disputes · retries · payouts · reconciliation · FX ledger) ---- */
  function apiFinDisputes(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    const f = {}; if (url.searchParams.get("state")) f.state = url.searchParams.get("state");
    json(res, 200, { disputes: fin.disputes(T(s), f), states: require("../states.js").vocab("dispute") });
  }
  function apiFinDisputeOpen(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const d = fin.openDispute(T(s), body || {});
    logAction(s, "fin.dispute.open", "dispute", d.id, { payment: body.payment_id, amount: body.amount });
    json(res, 200, { dispute: fin.disputes(T(s), { state: d.state }).find(x => x.id === d.id) });
  }
  function apiFinDisputeStatus(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try {
      const d = fin.transitionDispute(T(s), Number(id), String(body.state), body);
      logAction(s, "fin.dispute.transition", "dispute", d.id, { to: body.state });
      json(res, 200, { dispute: d });
    } catch (e) { bad(res, e.message); }
  }
  function apiFinRetry(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    const p = fin.retry(T(s), Number(id), true);
    if (!p) return bad(res, "Unknown payment", 404);
    json(res, 200, { payment: p, attempts: fin.attempts(T(s), p.id) });
  }
  function apiFinPayouts(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    const t = T(s);
    const rows = all("SELECT * FROM payouts WHERE tenant_id=? ORDER BY id DESC LIMIT 200", t);
    json(res, 200, { payouts: rows.map(p => ({ ...p, items: fin.payoutItems(t, p.id).length })), kinds: fin.PAYOUT_KINDS });
  }
  function apiFinPayoutOpen(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const p = fin.openPayout(T(s), body.seller_id, body.kind, body.period, body.items || []);
    logAction(s, "fin.payout.open", "payout", p.id, { seller: body.seller_id, gross: p.gross });
    json(res, 200, { payout: p });
  }
  function apiFinPayoutDisburse(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try {
      const p = fin.disbursePayout(T(s), Number(id));
      logAction(s, "fin.payout.disburse", "payout", p.id, { net: p.net });
      json(res, 200, { payout: p });
    } catch (e) { bad(res, e.message); }
  }
  function apiFinReconcile(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const b = fin.reconcile(T(s), body || {});
    logAction(s, "fin.recon.run", "recon", b.id, { lines: b.lines, unmatched: b.unmatched });
    json(res, 200, { batch: b, lines: fin.reconLines(T(s), b.id) });
  }
  /* a caller reads their OWN ledger; naming another owner (?owner=) is a staff action — a guest
     could read any customer's or seller's wallet history */
  function apiFinLedger(req, res, url, s) {
    const staff = !!(s.platform_admin || isAdmin(s));
    const owner = staff && url.searchParams.get("owner") ? url.searchParams.get("owner") : ownerFor(s);
    const to = url.searchParams.get("to") || null;
    json(res, 200, { owner, entries: to ? fin.ledgerFx(T(s), owner, to) : fin.ledger(T(s), owner) });
  }
  function apiAdminSettlements(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { settlements: all("SELECT st.*, se.name seller FROM settlements st LEFT JOIN sellers se ON se.id=st.seller_id WHERE st.tenant_id=? ORDER BY st.id DESC", T(s)) });
  }
  function apiAdminSettlementGenerate(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const t = T(s);
    const period = String(body.period || new Date().toISOString().slice(0, 7));
    if (!/^\d{4}-\d{2}$/.test(period)) return bad(res, "period must be YYYY-MM", 400);
    /* gross is the LINE value (order_items carries price and qty — orders does not, so the old
       sum was NaN), over orders that actually stood; and a period settles once per seller */
    const lines = all("SELECT oi.product_id, oi.price, oi.qty FROM orders o JOIN order_items oi ON oi.order_id=o.id WHERE o.tenant_id=? AND strftime('%Y-%m', o.created_at)=? AND COALESCE(o.status,'') NOT IN ('cancelled','refunded','returned')", t, period);
    let made = 0, skipped = 0;
    const bySeller = {};
    for (const o of lines) {
      const p = get("SELECT supplier_id FROM products WHERE tenant_id=? AND id=?", t, o.product_id);
      if (!p || !p.supplier_id) continue;
      bySeller[p.supplier_id] = (bySeller[p.supplier_id] || 0) + (Number(o.price) || 0) * (Number(o.qty) || 0);
    }
    for (const [sid, gross] of Object.entries(bySeller)) {
      const seller = get("SELECT * FROM sellers WHERE id=? AND tenant_id=?", Number(sid), t);
      if (!seller) continue;
      if (get("SELECT id FROM settlements WHERE tenant_id=? AND seller_id=? AND period=?", t, seller.id, period)) { skipped++; continue; }
      const comm = +(gross * seller.commission_pct / 100).toFixed(2);
      run("INSERT INTO settlements(tenant_id,ref,seller_id,gross,commission,net,status,period) VALUES(?,?,?,?,?,?, 'pending', ?)",
        t, "STL-" + (3000 + get("SELECT COUNT(*) c FROM settlements WHERE tenant_id=?", t).c + 1), seller.id, +gross.toFixed(2), comm, +(gross - comm).toFixed(2), period);
      made++;
    }
    logAction(s, "settlement.generate", "settlement", period, { count: made });
    json(res, 200, { ok: true, generated: made, already_settled: skipped });
  }
  function apiFinPayoutQueue(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { payout: fintech.queuePayout(T(s), body) }); } catch (e) { bad(res, e.message); }
  }
  function apiFinPayoutProcess(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { payout: fintech.processPayout(T(s), Number(id)) }); } catch (e) { bad(res, e.message); }
  }

  return [
    ["POST /api/fintech/payouts", apiFinPayoutQueue],
    ["POST /api/fintech/payouts/:id/process", (r, re, u, s, b, p) => apiFinPayoutProcess(r, re, u, s, b, p)],
    ["GET /api/admin/fin/disputes", apiFinDisputes],
    ["POST /api/admin/fin/disputes", apiFinDisputeOpen],
    ["PUT /api/admin/fin/disputes/:id", (r, re, u, s, b, p) => apiFinDisputeStatus(r, re, u, s, b, p)],
    ["POST /api/admin/fin/payments/:id/retry", (r, re, u, s, b, p) => apiFinRetry(r, re, u, s, b, p)],
    ["GET /api/admin/fin/payouts", apiFinPayouts],
    ["POST /api/admin/fin/payouts", apiFinPayoutOpen],
    ["POST /api/admin/fin/payouts/:id/disburse", (r, re, u, s, b, p) => apiFinPayoutDisburse(r, re, u, s, b, p)],
    ["POST /api/admin/fin/reconcile", apiFinReconcile],
    ["GET /api/admin/fin/ledger", apiFinLedger],
    ["GET /api/admin/settlements", apiAdminSettlements],
    ["POST /api/admin/settlements/generate", apiAdminSettlementGenerate]
  ];
} };
