/* LUXORA Platform — payments domain routes (_registry/business-domains.json `payments`).
   A payment's refunds — each an exact amount of the payment's currency (lib/refunds.js) — and
   the operator's settlement of a refund whose outcome the provider never gave. The refund itself
   (POST /api/admin/payments/:id/refund) predates this file and stays in lib/api.js. What it
   needs from the shared HTTP kit (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "payments", routes(kit) {
  const { T, actor, bad, get, json, logAction, refundEffects, requireAdmin, requireSection } = kit;
  const refunds = () => require("../refunds.js");

  /* a payment's refunds and what is left to refund */
  function apiAdminPaymentRefunds(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    const p = get("SELECT * FROM payments WHERE id=? AND tenant_id=?", Number(id), T(s));
    if (!p) return bad(res, "Unknown payment", 404);
    let summary = null; try { summary = refunds().summary(p); } catch (e) { summary = { review: e.message }; }
    json(res, 200, { payment: p.id, ...summary, refunds: refunds().ofPayment(p.id) });
  }
  /* staff settle a refund whose outcome the provider never gave (unknown) or that is still
     processing, after checking the provider's own record: success keeps it, failure gives it back */
  function apiAdminRefundResolve(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    if (!requireSection(s, res, "payments", "write")) return;
    const r = get("SELECT * FROM refunds WHERE id=? AND tenant_id=?", Number(id), T(s));
    if (!r) return bad(res, "Unknown refund", 404);
    let out;
    try { out = refunds().resolve(r, String(body.outcome || ""), { by: actor(s)[2], note: body.note, providerRefundId: body.provider_refund_id }); }
    catch (e) { if (!e.status) throw e; return bad(res, e.message, e.status); }
    const claw = out.full ? refundEffects(get("SELECT * FROM payments WHERE id=?", r.payment_id)) : null;
    logAction(s, "refund.resolve", "refund", r.id, { outcome: body.outcome, payment: r.payment_id, full: !!out.full, clawback: claw && claw.voided, note: String(body.note || "") }, req);
    json(res, 200, { ok: true, ...out });
  }

  return [
    ["GET /api/admin/payments/:id/refunds", (r, re, u, s, b, p) => apiAdminPaymentRefunds(r, re, u, s, b, p)],
    ["POST /api/admin/refunds/:id/resolve", (r, re, u, s, b, p) => apiAdminRefundResolve(r, re, u, s, b, p)]
  ];
} };
