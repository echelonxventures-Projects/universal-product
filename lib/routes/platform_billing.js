/* LUXORA Platform — platform_billing domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the platform_billing domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "platform_billing", routes(kit) {
  const { T, all, audit, bad, billing, enabledGateways, gatewaySecrets, get, invoicePaid, json, logAction, registry, requireAdmin, requirePlatform, requirePlatformSection, run, settlePayment, simulatedSettlementAllowed, stIn, stIs } = kit;

  function apiBillingPay(req, res, url, s, body, id) {
    return (async () => {
    if (!requireAdmin(s, res)) return;
    if (!require("../gates.js").on(T(s), "billing.self_pay")) return bad(res, require("../gates.js").message("billing.self_pay"), 403);
    const inv = get("SELECT * FROM invoices WHERE id=? AND tenant_id=?", Number(id), T(s));
    if (!inv) return bad(res, "Unknown invoice", 404);
    if (stIs("invoice", inv.status, "success")) return bad(res, "Invoice already paid");
    const gws = enabledGateways(T(s));
    const g = gws.find(x => x.id === String(body.gateway || "")) || gws[0];
    if (!g) return bad(res, "No payment gateway configured", 422);
    const sim = await settlePayment(T(s), g, inv.amount, inv.currency || require("../defaults.js").currency(T(s)), inv.number);
    if (stIs("payment", sim.status, "failure")) return bad(res, "Payment declined: " + (sim.error || "gateway error"), 402);
    /* a platform invoice is settled by a REAL capture — a simulated/sandbox gateway can't mark
       money owed to the platform as paid (allowed outside production for development) */
    if (!sim.live && !simulatedSettlementAllowed()) return bad(res, "A live payment gateway is required to pay this invoice", 402);
    if (!stIs("payment", sim.status, "settled")) return bad(res, "Payment is pending — the invoice is marked paid once the capture completes", 202);
    invoicePaid(inv);
    require("../row-records.js").created("payment", () => run("INSERT INTO payments(tenant_id,kind,invoice_id,gateway,method,amount,currency,fee,status,txn_ref) VALUES(?,?,?,?,?,?,?,?,?,?)",
      T(s), "invoice", inv.id, g.id, (g.methods || ["card"])[0], inv.amount, inv.currency || require("../defaults.js").currency(T(s)), sim.fee, sim.status, sim.ref));
    logAction(s, "invoice.pay", "invoice", inv.number, { gateway: g.id, live: !!sim.live }, req);
    json(res, 200, { ok: true, number: inv.number });
    })();
  }
  function apiAdminBilling(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    const t = T(s);
    json(res, 200, {
      subscription: get(`SELECT s.status, s.started_at, s.renews_at, p.name plan, p.price_month, p.currency, p.max_products, p.max_orders_month FROM subscriptions s JOIN plans p ON p.id=s.plan_id WHERE s.tenant_id=? ORDER BY s.id DESC`, t) || null,
      invoices: all("SELECT * FROM invoices WHERE tenant_id=? ORDER BY issued_at DESC", t),
      usage: { products: get("SELECT COUNT(*) c FROM products WHERE tenant_id=? AND (source_kind!='universe' OR source_kind IS NULL)", t).c,
        activatedUniverses: get("SELECT COUNT(DISTINCT source_universe) c FROM products WHERE tenant_id=? AND source_kind='universe'", t).c,
        ordersMonth: get("SELECT COUNT(*) c FROM orders WHERE tenant_id=? AND created_at >= date('now','start of month')", t).c }
    });
  }
  function apiPlatformPlans(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    json(res, 200, { plans: all("SELECT * FROM plans ORDER BY position") });
  }
  function apiPlatformPlanSave(req, res, url, s, body, id) {
    if (!requirePlatformSection(s, res, "plans", "write")) return;
    if (!body.name) return bad(res, "Name required");
    const vals = [String(body.name), Number(body.price_month) || 0, String(body.currency || require("../defaults.js").platformCurrency()), Math.max(1, Number(body.max_products) || 100), Math.max(1, Number(body.max_orders_month) || 100), Number(body.position) || 0];
    if (id) run("UPDATE plans SET name=?,price_month=?,currency=?,max_products=?,max_orders_month=?,position=? WHERE id=?", ...vals, Number(id));
    else run("INSERT INTO plans(name,price_month,currency,max_products,max_orders_month,position) VALUES(?,?,?,?,?,?)", ...vals);
    audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "plan.save", "plan", id || "new");
    json(res, 200, { plans: all("SELECT * FROM plans ORDER BY position") });
  }
  function apiPlatformInvoices(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    json(res, 200, { invoices: all("SELECT i.*, t.slug tenant_slug, t.name tenant_name FROM invoices i JOIN tenants t ON t.id=i.tenant_id ORDER BY i.issued_at DESC") });
  }
  function apiPlatformInvoiceRefund(req, res, url, s, body, id) {
    if (!requirePlatform(s, res)) return;
    const inv = get("SELECT * FROM invoices WHERE id=?", Number(id)); if (!inv) return bad(res, "Unknown invoice", 404);
    /* a credit note is bounded by what is left to credit on the invoice; money only goes to a
       wallet when the invoice was actually paid, and only to a wallet of the invoiced store */
    const credited = get("SELECT COALESCE(SUM(amount),0) c FROM credit_notes WHERE invoice_id=? AND status IN " + stIn("credit_note", "live").sql, inv.id, ...stIn("credit_note", "live").args).c;
    const amount = body.amount != null ? +Number(body.amount).toFixed(2) : +(inv.amount - credited).toFixed(2);
    if (!(amount > 0) || amount > +(inv.amount - credited).toFixed(2) + 1e-9) return bad(res, "Credit must be positive and at most the uncredited balance (" + (+(inv.amount - credited).toFixed(2)) + ")", 400);
    if (body.to_wallet && !stIs("invoice", inv.status, "success")) return bad(res, "Only a paid invoice can be refunded to a wallet", 400);
    const owner = body.owner ? String(body.owner) : undefined;
    if (owner && !owner.startsWith("t" + inv.tenant_id + ":")) return bad(res, "The refund wallet must belong to the invoiced store", 400);
    const r = billing.creditNote(inv.tenant_id, inv.id, amount, String(body.reason || "refund"), { to_wallet: !!body.to_wallet, owner });
    if (r.error) return bad(res, r.error);
    logAction(s, "invoice.credit_note", "invoice", inv.number, { amount: r.amount, to_wallet: !!body.to_wallet }, req);
    json(res, 200, { ok: true, credit_note: r });
  }
  function apiPlatformDunning(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return; const t = Number(body && body.tenant_id || 0);
    const r = billing.dunning(t); logAction(s, "billing.dunning", "billing", t || null, { actions: r.actions.length });
    json(res, 200, r);
  }
  function apiPlatformAging(req, res, url, s) { if (!requirePlatform(s, res)) return; json(res, 200, { aging: billing.aging(0), all: billing.list(0) }); }
  function apiPlatformUsage(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    if (!body.tenant_id || !body.description) return bad(res, "tenant_id and description required");
    const id = billing.recordUsage(Number(body.tenant_id), String(body.kind || "manual"), String(body.description), Number(body.qty) || 1, Number(body.unit_amount) || 0, { currency: body.currency, ref: body.ref, period: body.period });
    logAction(s, "billing.usage", "usage_record", id, { tenant: body.tenant_id, amount: body.unit_amount });
    json(res, 200, { ok: true, id });
  }
  function apiAdminBillingDetail(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    const data = billing.list(T(s)); data.aging = billing.aging(T(s)).buckets; data.usage = all("SELECT * FROM usage_records WHERE tenant_id=? ORDER BY id DESC LIMIT 100", T(s));
    json(res, 200, data);
  }
  function apiPlatformInvoicePay(req, res, url, s, body, id) {
    return (async () => {
    if (!requirePlatform(s, res)) return;
    const inv = get("SELECT * FROM invoices WHERE id=?", Number(id));
    if (!inv) return bad(res, "Unknown invoice", 404);
    if (stIs("invoice", inv.status, "success")) return bad(res, "Already paid");
    const gwId = String(body.gateway || "");
    if (!gwId) return bad(res, "Pick the gateway the invoice is collected through", 422);
    const gw = registry.providerDefs("payment").find(p => p.id === gwId);
    if (!gw) return bad(res, "Unknown gateway", 422);
    const gs = gatewaySecrets(inv.tenant_id, gwId);
    const sim = await settlePayment(inv.tenant_id, Object.assign({}, gw, { mode: gs ? gs.mode : "sandbox" }), inv.amount, inv.currency, inv.number);
    if (stIs("payment", sim.status, "failure")) return bad(res, "Payment declined: " + (sim.error || "gateway error"), 402);
    invoicePaid(inv);
    require("../row-records.js").created("payment", () => run("INSERT INTO payments(tenant_id,kind,invoice_id,gateway,method,amount,currency,fee,status,txn_ref) VALUES(?,?,?,?,?,?,?,?,?,?)",
      inv.tenant_id, "subscription", inv.id, gw.id, "card", inv.amount, inv.currency, sim.fee, sim.status, sim.ref));
    audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "invoice.pay", "invoice", inv.number, { gateway: gw.id, txn: sim.ref, live: !!sim.live });
    json(res, 200, { ok: true, txn_ref: sim.ref });
    })();
  }
  function apiPlatformRevenue(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    json(res, 200, {
      mrr: get("SELECT COALESCE(SUM(p.price_month),0) t FROM subscriptions s JOIN plans p ON p.id=s.plan_id WHERE s.status IN " + stIn("plan_subscription", "current").sql, ...stIn("plan_subscription", "current").args).t, /* plans priced in platform billing currency (USD) */
      collected: get("SELECT COALESCE(SUM(i.amount * COALESCE(c.usd,1)),0) t FROM invoices i LEFT JOIN currencies c ON c.code=i.currency WHERE i.status IN " + stIn("invoice", "success").sql, ...stIn("invoice", "success").args).t,
      outstanding: get("SELECT COALESCE(SUM(amount),0) t FROM invoices WHERE status NOT IN " + stIn("invoice", "success").sql, ...stIn("invoice", "success").args).t,
      gatewayFees: get("SELECT COALESCE(SUM(p.fee * COALESCE(c.usd,1)),0) t FROM payments p LEFT JOIN currencies c ON c.code=p.currency WHERE p.kind='order'").t,
      gmv: get("SELECT COALESCE(SUM(o.total * COALESCE(c.usd,1)),0) t FROM orders o LEFT JOIN currencies c ON c.code=o.currency").t,
      byMonth: all("SELECT strftime('%Y-%m', issued_at) m, SUM(CASE WHEN status IN " + stIn("invoice", "success").sql + " THEN amount ELSE 0 END) paid FROM invoices GROUP BY m ORDER BY m", ...stIn("invoice", "success").args)
    });
  }

  return [
    ["GET /api/admin/billing", apiAdminBilling],
    ["POST /api/billing/invoices/:id/pay", (r, re, u, s, b, p) => apiBillingPay(r, re, u, s, b, p)],
    ["GET /api/platform/plans", apiPlatformPlans],
    ["POST /api/platform/plans", (r, re, u, s, b, p) => apiPlatformPlanSave(r, re, u, s, b, p)],
    ["PUT /api/platform/plans/:id", (r, re, u, s, b, p) => apiPlatformPlanSave(r, re, u, s, b, p)],
    ["GET /api/platform/invoices", apiPlatformInvoices],
    ["POST /api/platform/invoices/:id/refund", (r, re, u, s, b, p) => apiPlatformInvoiceRefund(r, re, u, s, b, p)],
    ["POST /api/platform/billing/dunning", apiPlatformDunning],
    ["GET /api/platform/billing/aging", apiPlatformAging],
    ["POST /api/platform/usage", apiPlatformUsage],
    ["GET /api/admin/billing/detail", apiAdminBillingDetail],
    ["POST /api/platform/invoices/:id/pay", (r, re, u, s, b, p) => apiPlatformInvoicePay(r, re, u, s, b, p)],
    ["GET /api/platform/revenue", apiPlatformRevenue]
  ];
} };
