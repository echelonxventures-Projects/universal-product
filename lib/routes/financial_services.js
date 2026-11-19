/* LUXORA Platform — financial_services domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the financial_services domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "financial_services", routes(kit) {
  const { T, actor, bad, finOwns, fintech, get, isAdmin, json, ownerFor, requireAdmin, stIs } = kit;

  function apiFinBillers(req, res, url, s) {
    json(res, 200, { billers: fintech.billers(T(s)) });
  }
  function apiFinBillPay(req, res, url, s, body) {
    try { json(res, 200, { bill: fintech.payBill(T(s), ownerFor(s), body) }); } catch (e) { bad(res, e.message); }
  }
  function apiFinPlans(req, res, url, s) {
    json(res, 200, { plans: fintech.plans(T(s)) });
  }
  function apiFinRecharge(req, res, url, s, body) {
    try { json(res, 200, { recharge: fintech.doRecharge(T(s), ownerFor(s), body) }); } catch (e) { bad(res, e.message); }
  }
  function apiFinBnplOpen(req, res, url, s, body) {
    try { json(res, 200, { account: fintech.openBnpl(T(s), ownerFor(s), body) }); } catch (e) { bad(res, e.message); }
  }
  function apiFinBnplSpend(req, res, url, s, body, id) {
    if (!finOwns(s, "bnpl_accounts", id)) return bad(res, "BNPL account not found", 404);
    try { json(res, 200, { emis: fintech.spendBnpl(T(s), Number(id), body.order_id, body.amount) }); }
    catch (e) { bad(res, e.message); }
  }
  /* a customer pays an installment from their wallet; staff may record an offline payment.
     It used to mark any EMI paid for free, restoring the credit line without a payment. */
  function apiFinEmiPay(req, res, url, s, body, id) {
    const e = get("SELECT e.id, e.amount, e.status, a.owner FROM bnpl_emis e JOIN bnpl_accounts a ON a.id=e.account_id WHERE e.id=? AND e.tenant_id=?", Number(id), T(s));
    const staff = !!(s.platform_admin || isAdmin(s));
    if (!e || (!staff && e.owner !== ownerFor(s))) return bad(res, "EMI not found", 404);
    if (stIs("emi", e.status, "settled") || !(+e.amount > 0)) return bad(res, "EMI not payable");
    /* the installment is spent from the wallet (refused beyond what is available); if recording it
       fails, that spend is reversed — linked to it, never re-credited by hand */
    let paid = null;
    if (!staff) {
      try { const Wl = require("../wallet.js"), w0 = Wl.walletFor(T(s), e.owner); paid = Wl.post(T(s), { op: "redeem", wallet: w0.id, amount: Number(e.amount).toFixed(Wl.unitOf(w0.unit).decimals), ref: "emi:" + e.id, idem: "emi:" + e.id, actor: e.owner }).journal; }
      catch (err) { return bad(res, err.status === 402 ? "Insufficient wallet balance to pay this installment" : err.message, err.status || 400); }
    }
    try { json(res, 200, { emi: fintech.payEmi(T(s), Number(id)) }); }
    catch (err) { if (paid) { try { require("../wallet.js").reverse(T(s), paid.id, e.owner, "installment not recorded: " + err.message); } catch (x) { console.error("emi reversal:", x.message); } } bad(res, err.message); }
  }
  function apiFinLoanApply(req, res, url, s, body) {
    try { json(res, 200, { loan: fintech.applyLoan(T(s), ownerFor(s), body) }); } catch (e) { bad(res, e.message); }
  }
  function apiFinLoanDisburse(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    try { json(res, 200, { loan: fintech.disburseLoan(T(s), Number(id)) }); } catch (e) { bad(res, e.message); }
  }
  function apiFinInsuranceQuote(req, res, url, s, body) {
    try { json(res, 200, { policy: fintech.quoteInsurance(T(s), ownerFor(s), body) }); } catch (e) { bad(res, e.message); }
  }
  function apiFinInsuranceActivate(req, res, url, s, body, id) {
    if (!finOwns(s, "insurance_policies", id)) return bad(res, "Policy not found", 404);
    try { json(res, 200, { policy: fintech.activateInsurance(T(s), Number(id)) }); } catch (e) { bad(res, e.message); }
  }

  return [
    ["GET /api/fintech/billers", apiFinBillers],
    ["POST /api/fintech/bills", apiFinBillPay],
    ["GET /api/fintech/plans", apiFinPlans],
    ["POST /api/fintech/recharge", apiFinRecharge],
    ["POST /api/fintech/bnpl", apiFinBnplOpen],
    ["POST /api/fintech/bnpl/:id/spend", (r, re, u, s, b, p) => apiFinBnplSpend(r, re, u, s, b, p)],
    ["POST /api/fintech/emi/:id/pay", (r, re, u, s, b, p) => apiFinEmiPay(r, re, u, s, b, p)],
    ["POST /api/fintech/loans", apiFinLoanApply],
    ["POST /api/fintech/loans/:id/disburse", (r, re, u, s, b, p) => apiFinLoanDisburse(r, re, u, s, b, p)],
    ["POST /api/fintech/insurance", apiFinInsuranceQuote],
    ["POST /api/fintech/insurance/:id/activate", (r, re, u, s, b, p) => apiFinInsuranceActivate(r, re, u, s, b, p)]
  ];
} };
