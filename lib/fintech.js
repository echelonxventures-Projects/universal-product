/* LUXORA Platform — Fintech engine (configurable money rails).
   UPI collect/push, QR scan-pay, payment links, mandates/auto-debit, escrow
   hold-and-release, split payments, KYC, bank-account payouts, BBPS bill payments,
   mobile/DTH recharge, P2P wallet transfer, BNPL/EMI, loans & credit lines,
   insurance distribution and gift vouchers.

   All statuses/kinds/categories are registry rows (meta_lists — see
   lib/parity-registries.js); outbound money movement goes through the platform's
   existing provider-spec engine (lib/connect.js) when a live gateway spec exists,
   and otherwise records a deterministic simulated reference so the ledger is
   complete and reconcilable either way. Money itself stays in the single wallet
   ledger (lib/offers.js / lib/modules.js) — this engine never opens a second
   source of truth for balances. */
"use strict";

const db = () => require("./db.js");
/* every service entry point asks the applicability rules first (lib/rules.js). It names only
   its own binding point; the ruleBindings registry row says which service it is, which
   instruments (gateway, method, bank) it checks and which input fields feed which facts */
const guard = (point, tid, input) => require("./rules.js").guardAt(point, tid, input || {});
const offers = () => require("./offers.js");
const mods = () => require("./modules.js");
const reg = () => require("./parity-registries.js");
const crypto = require("crypto");

const J = (v, d) => { try { return v == null || v === "" ? (d == null ? [] : d) : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d == null ? [] : d; } };
const refOf = (pfx) => pfx + "-" + Date.now().toString(36).toUpperCase().slice(-6) + crypto.randomBytes(2).toString("hex").toUpperCase();
const token = (n) => crypto.randomBytes(n || 24).toString("hex");
const code = (n) => Array.from({ length: n }, () => "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"[Math.floor(Math.random() * 32)]).join("");

/* ---------- simulated vs live outbound ---------- */
/* a rail is "live" only when the platform has a provider spec for it and outbound
   mode is not offline; otherwise a deterministic sim ref keeps the ledger honest */
/* these rails are SIMULATED: no money reaches a biller, a payee's bank or a payer's UPI app.
   That is the development/sandbox experience; in production a simulated settlement would
   record (and charge wallets for) payments that never happened, so it is refused unless the
   operator opts in with LX_ALLOW_SIMULATED_PAYMENTS=1. Checked up front by every rail, and
   again here so no path can settle without it. */
function simulatedAllowed() {
  return process.env.NODE_ENV !== "production" || process.env.LX_ALLOW_SIMULATED_PAYMENTS === "1";
}
function requireSimulated(kind) {
  if (!simulatedAllowed()) throw new Error("The " + kind + " rail is simulated and is disabled in production — connect a live provider");
}
function sim(tenantId, kind, amount, currency) {
  requireSimulated(kind);
  return { live: false, ref: kind + "_sim_" + crypto.randomBytes(7).toString("hex"), fee: 0, status: "captured" };
}

/* ---------- UPI: VPA management + collect requests ---------- */
/* the owner sees their own pending handles too (verification is the bank's job);
   the API layer can filter by status when it needs only usable handles */
function upi(tenantId, owner) {
  const D = db();
  const rows = D.all("SELECT * FROM upi_handles WHERE tenant_id=? AND owner=? AND status IN ('active','pending_verification') ORDER BY is_default DESC, id", Number(tenantId), String(owner));
  return { handles: rows, default: rows.find(h => h.is_default && h.status === "active") || rows.find(h => h.status === "active") || null };
}
function addUpi(tenantId, owner, vpa, name) {
  const D = db();
  const status = reg().has("finUpiStatuses", "pending_verification") ? "pending_verification" : "active";
  const r = D.run("INSERT INTO upi_handles(tenant_id,owner,vpa,name,verified,is_default,status) VALUES(?,?,?, ?,0,0,?)",
    Number(tenantId), String(owner), String(vpa).toLowerCase(), String(name || ""), status);
  return D.get("SELECT * FROM upi_handles WHERE id=?", r.lastInsertRowid);
}
/* a collect request is raised by the payee; the payer approves on their UPI app.
   The settlement is a wallet ledger entry when it completes. */
function collectUpi(tenantId, owner, payerVpa, amount, currency, note) {
  guard("fintech.upi_collect", tenantId, { amount, currency });
  const D = db();
  const amt = +Number(amount || 0).toFixed(2);
  if (!(amt > 0)) throw new Error("Collect amount must be positive");
  const r = D.run("INSERT INTO upi_collects(tenant_id,ref,owner,payer_vpa,amount,currency,note,status,expires_at) VALUES(?,?,?,?,?,?,?, 'initiated', datetime('now','+1 hour'))",
    Number(tenantId), refOf("UPI"), String(owner), String(payerVpa), amt, String(currency || "USD"), String(note || ""));
  return D.get("SELECT * FROM upi_collects WHERE id=?", r.lastInsertRowid);
}
/* settle a collect (the PSP callback or the operator's manual confirmation) */
function settleCollect(tenantId, collectId, ok) {
  const D = db();
  const c = D.get("SELECT * FROM upi_collects WHERE id=? AND tenant_id=?", Number(collectId), Number(tenantId));
  if (!c) throw new Error("Unknown collect request");
  const status = ok ? "success" : "failed";
  D.run("UPDATE upi_collects SET status=?, txn_ref=? WHERE id=?", status, sim(tenantId, "upi", c.amount, c.currency).ref, c.id);
  if (ok) offers().credit(tenantId, c.owner, c.amount, "deposit", "upi_collect:" + c.ref, c.currency, "upi");
  return D.get("SELECT * FROM upi_collects WHERE id=?", c.id);
}

/* ---------- QR codes ---------- */
/* payload-only: the record stores what the QR encodes; the console renders the
   matrix client-side from the payload (no image pipeline needed server-side) */
function createQr(tenantId, input) {
  const D = db();
  const kind = reg().has("finQrKinds", input.kind) ? input.kind : "upi";
  const payload = String(input.payload || "");
  const r = D.run("INSERT INTO qr_codes(tenant_id,ref,kind,payload,label,amount,owner,status) VALUES(?,?,?,?,?,?,?, 'active')",
    Number(tenantId), refOf("QR"), kind, payload, String(input.label || ""), +Number(input.amount || 0).toFixed(2) || null, String(input.owner || ""));
  return D.get("SELECT * FROM qr_codes WHERE id=?", r.lastInsertRowid);
}
function scanQr(tenantId, qrId) {
  const D = db();
  D.run("UPDATE qr_codes SET scans=scans+1 WHERE id=? AND tenant_id=?", Number(qrId), Number(tenantId));
  const row = D.get("SELECT * FROM qr_codes WHERE id=? AND tenant_id=?", Number(qrId), Number(tenantId));
  if (!row) throw new Error("Unknown QR code");
  return row;
}

/* ---------- payment links ---------- */
function createLink(tenantId, input) {
  guard("fintech.payment_link", tenantId, input);
  const D = db();
  const r = D.run("INSERT INTO payment_links(tenant_id,ref,token,title,amount,currency,owner,gateway,purpose,expires_at,status) VALUES(?,?,?,?,?,?,?,?,?,datetime('now','+7 days'),'issued')",
    Number(tenantId), refOf("PL"), token(), String(input.title || "Payment"), +Number(input.amount || 0).toFixed(2),
    String(input.currency || "USD"), String(input.owner || ""), String(input.gateway || ""), String(input.purpose || ""));
  return D.get("SELECT * FROM payment_links WHERE id=?", r.lastInsertRowid);
}
function payLink(tenantId, linkToken) {
  const D = db();
  const link = D.get("SELECT * FROM payment_links WHERE tenant_id=? AND token=? AND status='issued'", Number(tenantId), String(linkToken));
  if (!link) throw new Error("Payment link not found or already used");
  requireSimulated("payment link");
  const s = sim(tenantId, "link", link.amount, link.currency);
  D.run("UPDATE payment_links SET status='paid', paid_at=datetime('now'), txn_ref=? WHERE id=?", s.ref, link.id);
  if (link.owner) offers().credit(tenantId, link.owner, link.amount, "deposit", "payment_link:" + link.ref, link.currency, "link");
  return D.get("SELECT * FROM payment_links WHERE id=?", link.id);
}

/* ---------- mandates (auto-debit / subscriptions) ---------- */
function registerMandate(tenantId, input) {
  guard("fintech.mandate", tenantId, input);
  const D = db();
  const freq = reg().has("finMandateFrequencies", input.frequency) ? input.frequency : "monthly";
  const r = D.run("INSERT INTO mandates(tenant_id,ref,owner,mandate_id,gateway,max_amount,frequency,purpose,next_charge_at,status) VALUES(?,?,?,?,?,?,?,?,datetime('now','+30 days'),'registered')",
    Number(tenantId), refOf("MAND"), String(input.owner), String(input.mandate_id || token(12)), String(input.gateway || ""),
    +Number(input.max_amount || 0).toFixed(2), freq, String(input.purpose || "subscription"));
  return D.get("SELECT * FROM mandates WHERE id=?", r.lastInsertRowid);
}
/* charge a mandate up to its cap; a real PSP would debit the instrument here */
function chargeMandate(tenantId, mandateId, amount) {
  const D = db();
  const m = D.get("SELECT * FROM mandates WHERE id=? AND tenant_id=? AND status IN ('registered','active')", Number(mandateId), Number(tenantId));
  if (!m) throw new Error("Mandate not active");
  const amt = +Number(amount || 0).toFixed(2);
  if (!(amt > 0)) throw new Error("Charge amount must be positive");
  const charged = +(Number(m.charged_amount || 0) + amt).toFixed(2);
  if (m.max_amount && charged > +m.max_amount) throw new Error("Charge exceeds mandate cap");
  D.run("UPDATE mandates SET charged_amount=?, charges_done=charges_done+1, next_charge_at=datetime('now','+30 days') WHERE id=?",
    charged, m.id);
  if (m.owner) offers().debit(tenantId, m.owner, amt, "redeem", "mandate_charge:" + m.ref, "USD", "mandate");
  return D.get("SELECT * FROM mandates WHERE id=?", m.id);
}

/* ---------- escrow: hold funds until delivery (also serves Trade Assurance) ---------- */
function hold(tenantId, orderId, buyer, seller, amount, currency, meta) {
  guard("fintech.escrow", tenantId, { amount, currency });
  const D = db();
  const r = D.run("INSERT INTO escrow_holds(tenant_id,ref,order_id,buyer,seller,amount,currency,held,dispute_opened,status,meta) VALUES(?,?,?,?,?,?,?,1,0,'held',?)",
    Number(tenantId), refOf("ESC"), Number(orderId) || null, String(buyer), String(seller),
    +Number(amount || 0).toFixed(2), String(currency || "USD"), JSON.stringify(meta || {}));
  return D.get("SELECT * FROM escrow_holds WHERE id=?", r.lastInsertRowid);
}
function releaseEscrow(tenantId, escrowId) {
  const D = db();
  const e = D.get("SELECT * FROM escrow_holds WHERE id=? AND tenant_id=? AND held=1", Number(escrowId), Number(tenantId));
  if (!e) throw new Error("Escrow hold not found or already released");
  D.run("UPDATE escrow_holds SET held=0, released_at=datetime('now'), status='released' WHERE id=?", e.id);
  if (e.seller) offers().credit(tenantId, e.seller, e.amount, "deposit", "escrow_release:" + e.ref, e.currency, "escrow");
  return D.get("SELECT * FROM escrow_holds WHERE id=?", e.id);
}
function disputeEscrow(tenantId, escrowId, opened) {
  const D = db();
  D.run("UPDATE escrow_holds SET dispute_opened=?, status=? WHERE id=? AND tenant_id=?",
    opened ? 1 : 0, opened ? "disputed" : "held", Number(escrowId), Number(tenantId));
  const row = D.get("SELECT * FROM escrow_holds WHERE id=? AND tenant_id=?", Number(escrowId), Number(tenantId));
  if (!row) throw new Error("Unknown escrow");
  return row;
}

/* ---------- split payments (marketplace pay-out-at-order) ---------- */
/* splits is [{party, amount, kind}]; the sum must equal the payment amount so the
   ledger never drifts from what the customer was charged */
function splitPayment(tenantId, paymentId, orderId, amount, splits) {
  const D = db();
  const list = (Array.isArray(splits) ? splits : J(splits, [])).map(s => ({ party: String(s.party), amount: +Number(s.amount || 0).toFixed(2), kind: String(s.kind || "payout") }));
  const sum = +list.reduce((n, s) => n + s.amount, 0).toFixed(2);
  if (Math.abs(sum - +Number(amount || 0).toFixed(2)) > 0.01) throw new Error("Split amounts must sum to the payment total");
  const r = D.run("INSERT INTO split_payments(tenant_id,ref,payment_id,order_id,splits,status) VALUES(?,?,?,?,?,'pending')",
    Number(tenantId), refOf("SPL"), Number(paymentId) || null, Number(orderId) || null, JSON.stringify(list));
  return settleSplit(tenantId, r.lastInsertRowid);
}
function settleSplit(tenantId, splitId) {
  const D = db();
  const sp = D.get("SELECT * FROM split_payments WHERE id=? AND tenant_id=?", Number(splitId), Number(tenantId));
  if (!sp) throw new Error("Unknown split");
  for (const s of J(sp.splits, [])) offers().credit(tenantId, s.party, s.amount, s.kind === "commission" ? "redeem" : "deposit", "split:" + sp.ref, "USD", "split");
  D.run("UPDATE split_payments SET status='settled', settled_at=datetime('now') WHERE id=?", sp.id);
  return D.get("SELECT * FROM split_payments WHERE id=?", sp.id);
}

/* ---------- KYC ---------- */
function submitKyc(tenantId, owner, input) {
  const D = db();
  const kind = reg().has("finKycKinds", input.kind) ? input.kind : "individual";
  const docType = reg().has("finKycDocs", input.doc_type) ? input.doc_type : "pan";
  const r = D.run("INSERT INTO kyc_profiles(tenant_id,owner,kind,full_name,dob,pan,aadhaar_masked,gstin,company,website,doc_type,doc_ref,doc_status,status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,'pending','pending')",
    Number(tenantId), String(owner), kind, String(input.full_name || ""), String(input.dob || ""), String(input.pan || ""),
    input.aadhaar_masked || null, String(input.gstin || ""), String(input.company || ""), String(input.website || ""),
    docType, String(input.doc_ref || ""));
  return D.get("SELECT * FROM kyc_profiles WHERE id=?", r.lastInsertRowid);
}
/* approve escalates min→full KYC; the wallet limit tier follows the KYC level */
function verifyKyc(tenantId, kycId, level, ok) {
  const D = db();
  const k = D.get("SELECT * FROM kyc_profiles WHERE id=? AND tenant_id=?", Number(kycId), Number(tenantId));
  if (!k) throw new Error("Unknown KYC profile");
  const status = ok ? (level === "full" ? "full_kyc" : "min_kyc") : "rejected";
  D.run("UPDATE kyc_profiles SET status=?, doc_status=?, verified_at=datetime('now') WHERE id=?", status, ok ? "approved" : "rejected", k.id);
  D.run("UPDATE users SET kyc_status=? WHERE id=(SELECT SUBSTR(owner, INSTR(owner,':u:')+3) FROM kyc_profiles WHERE id=?)", status, k.id);
  return D.get("SELECT * FROM kyc_profiles WHERE id=?", k.id);
}

/* ---------- bank payouts ---------- */
function queuePayout(tenantId, input) {
  guard("fintech.payout", tenantId, input);
  const D = db();
  const r = D.run("INSERT INTO bank_payouts(tenant_id,ref,payee,amount,currency,account_name,account_number,ifsc,upi_vpa,gateway,status) VALUES(?,?,?,?,?,?,?,?,?,?,'queued')",
    Number(tenantId), refOf("PYT"), String(input.payee), +Number(input.amount || 0).toFixed(2), String(input.currency || "USD"),
    String(input.account_name || ""), String(input.account_number || ""), String(input.ifsc || ""), String(input.upi_vpa || ""), String(input.gateway || ""));
  return D.get("SELECT * FROM bank_payouts WHERE id=?", r.lastInsertRowid);
}
function processPayout(tenantId, payoutId) {
  const D = db();
  const p = D.get("SELECT * FROM bank_payouts WHERE id=? AND tenant_id=? AND status='queued'", Number(payoutId), Number(tenantId));
  if (!p) throw new Error("Payout not queued");
  const s = sim(tenantId, "payout", p.amount, p.currency);
  D.run("UPDATE bank_payouts SET status='success', txn_ref=? WHERE id=?", s.ref, p.id);
  return D.get("SELECT * FROM bank_payouts WHERE id=?", p.id);
}

/* ---------- BBPS bill payments ---------- */
function billers(tenantId, category) {
  const D = db();
  return category
    ? D.all("SELECT * FROM billers WHERE tenant_id=? AND category=? AND status='active' ORDER BY position,name", Number(tenantId), String(category))
    : D.all("SELECT * FROM billers WHERE tenant_id=? AND status='active' ORDER BY position,name", Number(tenantId));
}
/* a customer-paid service is paid FROM the wallet: the balance must cover it before anything
   is recorded (offers.debit clamps at zero, so an unfunded payment used to succeed for free) */
function requireFunds(tenantId, owner, amount) {
  const bal = mods().walletBalance(Number(tenantId), String(owner));
  if (bal + 1e-9 < amount) throw new Error("Insufficient wallet balance");
}
function payBill(tenantId, owner, input) {
  guard("fintech.bill_pay", tenantId, input);
  const D = db();
  const amt = +Number(input.amount || 0).toFixed(2);
  if (!(amt > 0)) throw new Error("Bill amount must be positive");
  const fee = +Number(input.convenience_fee || 0).toFixed(2);
  /* the fee is a non-negative charge — a negative one turned the bill payment into a credit */
  if (!(fee >= 0) || fee > amt) throw new Error("Convenience fee must be between 0 and the bill amount");
  requireSimulated("bill payment");
  requireFunds(tenantId, owner, +(amt + fee).toFixed(2));
  const biller = D.get("SELECT * FROM billers WHERE id=? AND tenant_id=?", Number(input.biller_id), Number(tenantId));
  const cat = (biller && biller.category) || String(input.category || "electricity");
  const r = D.run("INSERT INTO bill_payments(tenant_id,ref,owner,biller_id,category,account_no,amount,currency,convenience_fee,status) VALUES(?,?,?,?,?,?,?,?,?, 'initiated')",
    Number(tenantId), refOf("BILL"), String(owner), Number(input.biller_id) || null, cat, String(input.account_no || ""), amt,
    String(input.currency || "USD"), fee);
  const row = D.get("SELECT * FROM bill_payments WHERE id=?", r.lastInsertRowid);
  return settleBill(tenantId, row.id, true);
}
function settleBill(tenantId, billId, ok) {
  const D = db();
  const b = D.get("SELECT * FROM bill_payments WHERE id=? AND tenant_id=?", Number(billId), Number(tenantId));
  if (!b) throw new Error("Unknown bill payment");
  D.run("UPDATE bill_payments SET status=?, txn_ref=? WHERE id=?", ok ? "success" : "failed", sim(tenantId, "bill", b.amount, b.currency).ref, b.id);
  if (ok && b.owner) offers().debit(tenantId, b.owner, +(b.amount + (b.convenience_fee || 0)).toFixed(2), "redeem", "bill_payment:" + b.ref, b.currency, "bbps");
  return D.get("SELECT * FROM bill_payments WHERE id=?", b.id);
}

/* ---------- mobile / DTH recharge ---------- */
function plans(tenantId, operator, kind) {
  const D = db();
  return D.all("SELECT * FROM recharge_plans WHERE tenant_id=? AND status='active' AND (? OR operator=?) AND (? OR kind=?) ORDER BY popular DESC, amount",
    Number(tenantId), operator ? 0 : 1, String(operator || ""), kind ? 0 : 1, String(kind || ""));
}
function doRecharge(tenantId, owner, input) {
  guard("fintech.recharge", tenantId, input);
  const D = db();
  const amt = +Number(input.amount || 0).toFixed(2);
  if (!(amt > 0)) throw new Error("Recharge amount must be positive");
  requireSimulated("recharge");
  requireFunds(tenantId, owner, amt);
  const kind = reg().has("finRechargeKinds", input.kind) ? input.kind : "mobile";
  const r = D.run("INSERT INTO recharges(tenant_id,ref,owner,number,operator,circle,plan_id,amount,currency,kind,status) VALUES(?,?,?,?,?,?,?,?,?,?, 'initiated')",
    Number(tenantId), refOf("RC"), String(owner), String(input.number || ""), String(input.operator || ""),
    String(input.circle || "national"), Number(input.plan_id) || null, amt, String(input.currency || "USD"), kind);
  const row = D.get("SELECT * FROM recharges WHERE id=?", r.lastInsertRowid);
  return settleRecharge(tenantId, row.id, true);
}
function settleRecharge(tenantId, rechargeId, ok) {
  const D = db();
  const rc = D.get("SELECT * FROM recharges WHERE id=? AND tenant_id=?", Number(rechargeId), Number(tenantId));
  if (!rc) throw new Error("Unknown recharge");
  D.run("UPDATE recharges SET status=?, txn_ref=? WHERE id=?", ok ? "success" : "failed", sim(tenantId, "recharge", rc.amount, rc.currency).ref, rc.id);
  if (ok && rc.owner) offers().debit(tenantId, rc.owner, rc.amount, "redeem", "recharge:" + rc.ref, rc.currency, "recharge");
  return D.get("SELECT * FROM recharges WHERE id=?", rc.id);
}

/* ---------- P2P: wallet-to-wallet transfer ---------- */
function transfer(tenantId, fromOwner, toOwner, amount, note) {
  guard("fintech.transfer", tenantId, { amount });
  const amt = +Number(amount || 0).toFixed(2);
  if (!(amt > 0)) throw new Error("Transfer amount must be positive");
  if (String(fromOwner) === String(toOwner)) throw new Error("Cannot transfer to the same wallet");
  const bal = mods().walletBalance(tenantId, fromOwner);
  if (bal < amt) throw new Error("Insufficient wallet balance");
  mods().walletAdd(tenantId, fromOwner, -amt);
  mods().walletAdd(tenantId, toOwner, amt);
  offers().ledgerEntry(tenantId, fromOwner, "transfer", -amt, "p2p:" + refOf("P2P"), "USD", "p2p", { to: toOwner, note: String(note || "") });
  return { from: fromOwner, to: toOwner, amount: amt, balance: mods().walletBalance(tenantId, fromOwner) };
}

/* ---------- BNPL / EMI ---------- */
/* eligibility is KYC-gated and limit-bearing; an EMI schedule is generated from
   the tenure so collections can be tracked per installment */
/* credit terms are the LENDER's policy, never the applicant's input: a customer used to
   choose their own BNPL credit limit and their own loan interest rate/fee. The policy is
   platform data (platform_settings key "fin_credit_policy", per-tenant overrides under
   "t<id>"), with conservative defaults. */
const CREDIT_DEFAULTS = { bnplMaxLimit: 500, loanMaxPrincipal: 5000, loanRatePct: 18, loanProcessingFeePct: 1, maxTenureMonths: 24 };
function creditPolicy(tenantId) {
  let stored = {};
  try { const r = db().get("SELECT value FROM platform_settings WHERE key='fin_credit_policy'"); stored = r ? JSON.parse(r.value) : {}; } catch (e) { stored = {}; }
  const own = (stored && stored["t" + Number(tenantId)]) || {};
  const { ...base } = stored || {};
  return { ...CREDIT_DEFAULTS, ...base, ...own };
}
function openBnpl(tenantId, owner, input) {
  guard("fintech.bnpl", tenantId, input);
  const D = db();
  const kyc = D.get("SELECT id,status FROM kyc_profiles WHERE tenant_id=? AND owner=? AND status IN ('full_kyc','verified') ORDER BY id DESC LIMIT 1", Number(tenantId), String(owner));
  if (!kyc) throw new Error("Full KYC required to open a BNPL account");
  const pol = creditPolicy(tenantId);
  const requested = +Number(input.credit_limit || 0).toFixed(2);
  if (!(requested > 0)) throw new Error("Requested credit limit must be positive");
  const limit = Math.min(requested, Number(pol.bnplMaxLimit) || 0);
  const tenure = Math.min(Math.max(1, Number(input.tenure_months || 3) || 3), Number(pol.maxTenureMonths) || 24);
  const r = D.run("INSERT INTO bnpl_accounts(tenant_id,owner,provider,credit_limit,used,available,tenure_months,status,kyc_id) VALUES(?,?,?,?,?,?,?, 'active',?)",
    Number(tenantId), String(owner), String(input.provider || "platform"), limit, 0, limit, tenure, kyc.id);
  return D.get("SELECT * FROM bnpl_accounts WHERE id=?", r.lastInsertRowid);
}
/* spend returns the full EMI schedule so the console and the API render the
   repayment plan, not just the first installment */
function spendBnpl(tenantId, accountId, orderId, amount) {
  const D = db();
  const a = D.get("SELECT * FROM bnpl_accounts WHERE id=? AND tenant_id=? AND status='active'", Number(accountId), Number(tenantId));
  if (!a) throw new Error("BNPL account not active");
  const amt = +Number(amount || 0).toFixed(2);
  /* a spend draws on the credit line; a negative one created negative EMIs whose "payment"
     credited the customer's wallet */
  if (!(amt > 0)) throw new Error("Spend amount must be positive");
  if (amt > +a.available) throw new Error("Exceeds available BNPL limit");
  const n = Math.max(1, Number(a.tenure_months) || 3);
  const per = +(amt / n).toFixed(2);
  D.run("UPDATE bnpl_accounts SET used=?, available=? WHERE id=?", +(a.used + amt).toFixed(2), +(a.available - amt).toFixed(2), a.id);

  for (let i = 1; i <= n; i++) {
    D.run("INSERT INTO bnpl_emis(tenant_id,account_id,order_id,installment_no,amount,due_at,status) VALUES(?,?,?,?,?,date('now','+' || ? || ' months'),'upcoming')",
      Number(tenantId), a.id, Number(orderId) || null, i, per, i);
  }
  return D.all("SELECT * FROM bnpl_emis WHERE account_id=? ORDER BY installment_no", a.id);
}
function payEmi(tenantId, emiId) {
  const D = db();
  const e = D.get("SELECT * FROM bnpl_emis WHERE id=? AND tenant_id=?", Number(emiId), Number(tenantId));
  if (!e || e.status === "paid" || !(+e.amount > 0)) throw new Error("EMI not payable");
  D.run("UPDATE bnpl_emis SET status='paid', paid_at=datetime('now') WHERE id=?", e.id);
  const a = D.get("SELECT * FROM bnpl_accounts WHERE id=?", e.account_id);
  if (a) D.run("UPDATE bnpl_accounts SET used=MAX(0,used-?), available=MIN(credit_limit,available+?) WHERE id=?", e.amount, e.amount, a.id);
  return D.get("SELECT * FROM bnpl_emis WHERE id=?", e.id);
}

/* ---------- loans & credit lines ---------- */
function emiFor(principal, months, ratePct) {
  const r = (Number(ratePct || 0) / 100) / 12;
  const n = Math.max(1, Number(months) || 12);
  if (!r) return +(Number(principal) / n).toFixed(2);
  const p = Number(principal);
  return +(p * r * (1 + r) ** n / ((1 + r) ** n - 1)).toFixed(2);
}
function applyLoan(tenantId, owner, input) {
  guard("fintech.loan", tenantId, input);
  const D = db();
  const kyc = D.get("SELECT id FROM kyc_profiles WHERE tenant_id=? AND owner=? AND status IN ('full_kyc','verified') ORDER BY id DESC LIMIT 1", Number(tenantId), String(owner));
  if (!kyc) throw new Error("Full KYC required to apply for credit");
  const pol = creditPolicy(tenantId);
  const principal = +Number(input.principal || 0).toFixed(2);
  if (principal <= 0) throw new Error("Principal must be positive");
  if (principal > Number(pol.loanMaxPrincipal)) throw new Error("Principal exceeds the maximum of " + pol.loanMaxPrincipal);
  const tenure = Math.min(Math.max(1, Number(input.tenure_months || 12) || 12), Number(pol.maxTenureMonths) || 24);
  const rate = Number(pol.loanRatePct) || 0;
  const fee = +(principal * (Number(pol.loanProcessingFeePct) || 0) / 100).toFixed(2);
  const emi = emiFor(principal, tenure, rate);
  const r = D.run("INSERT INTO loans(tenant_id,ref,owner,principal,currency,tenure_months,rate,emi,processing_fee,status,kyc_id) VALUES(?,?,?,?,?,?,?,?,?, 'applied',?)",
    Number(tenantId), refOf("LN"), String(owner), principal, String(input.currency || "USD"),
    tenure, rate, emi, fee, kyc.id);
  return D.get("SELECT * FROM loans WHERE id=?", r.lastInsertRowid);
}
function disburseLoan(tenantId, loanId) {
  const D = db();
  const l = D.get("SELECT * FROM loans WHERE id=? AND tenant_id=? AND status='approved'", Number(loanId), Number(tenantId));
  if (!l) throw new Error("Loan not approved");
  D.run("UPDATE loans SET status='disbursed', disbursed_at=datetime('now') WHERE id=?", l.id);
  offers().credit(tenantId, l.owner, l.principal, "deposit", "loan_disbursement:" + l.ref, l.currency, "loan");
  return D.get("SELECT * FROM loans WHERE id=?", l.id);
}

/* ---------- insurance distribution ---------- */
function quoteInsurance(tenantId, owner, input) {
  guard("fintech.insurance", tenantId, input);
  const D = db();
  const premium = +Number(input.premium || 0).toFixed(2);
  /* activation debits the premium from the owner's wallet — a negative premium credited it */
  if (!(premium > 0)) throw new Error("Premium must be positive");
  if (!(Number(input.cover || 0) >= 0)) throw new Error("Cover cannot be negative");
  const r = D.run("INSERT INTO insurance_policies(tenant_id,ref,owner,product_id,plan_name,premium,currency,cover,starts_at,ends_at,nominees,status) VALUES(?,?,?,?,?,?,?,?,?,?,?, 'quoted')",
    Number(tenantId), refOf("INS"), String(owner), Number(input.product_id) || null, String(input.plan_name || ""),
    premium, String(input.currency || "USD"), +Number(input.cover || 0).toFixed(2),
    String(input.starts_at || null), String(input.ends_at || null), JSON.stringify(input.nominees || []));
  return D.get("SELECT * FROM insurance_policies WHERE id=?", r.lastInsertRowid);
}
function activateInsurance(tenantId, policyId) {
  const D = db();
  const p = D.get("SELECT * FROM insurance_policies WHERE id=? AND tenant_id=? AND status='quoted'", Number(policyId), Number(tenantId));
  if (!p) throw new Error("Policy not in a quotable state");
  /* checks first: the policy only becomes active once its (positive) premium is paid */
  if (!(+p.premium > 0)) throw new Error("Policy premium is not payable");
  if (p.owner) requireFunds(tenantId, p.owner, +p.premium);
  D.run("UPDATE insurance_policies SET status='active' WHERE id=?", p.id);
  if (p.owner) offers().debit(tenantId, p.owner, p.premium, "redeem", "insurance_premium:" + p.ref, p.currency, "insurance");
  return D.get("SELECT * FROM insurance_policies WHERE id=?", p.id);
}

/* ---------- gift vouchers (storefront purchasable + redeemable) ---------- */
function issueVoucher(tenantId, input) {
  const D = db();
  const amt = +Number(input.amount || 0).toFixed(2);
  if (!(amt > 0)) throw new Error("Voucher amount must be positive");
  const c = code(12);
  const r = D.run("INSERT INTO gift_vouchers(tenant_id,code,amount,currency,buyer,recipient,recipient_email,message,expires_at,status) VALUES(?,?,?,?,?,?,?,?,?, 'issued')",
    Number(tenantId), c, amt, String(input.currency || "USD"), String(input.buyer || ""), String(input.recipient || ""),
    String(input.recipient_email || ""), String(input.message || ""), String(input.expires_at || null));
  return D.get("SELECT * FROM gift_vouchers WHERE id=?", r.lastInsertRowid);
}
function redeemVoucher(tenantId, voucherCode, owner) {
  const D = db();
  const v = D.get("SELECT * FROM gift_vouchers WHERE tenant_id=? AND code=? AND status='issued'", Number(tenantId), String(voucherCode));
  if (!v) throw new Error("Voucher not found or already redeemed");
  if (v.expires_at && new Date(String(v.expires_at).replace(" ", "T")) < new Date()) {
    D.run("UPDATE gift_vouchers SET status='expired' WHERE id=?", v.id);
    throw new Error("Voucher has expired");
  }
  D.run("UPDATE gift_vouchers SET status='redeemed', redeemed_at=datetime('now'), redeemed_by=? WHERE id=?", String(owner || ""), v.id);
  offers().credit(tenantId, owner, v.amount, "deposit", "voucher:" + v.code, v.currency, "voucher");
  return D.get("SELECT * FROM gift_vouchers WHERE id=?", v.id);
}

module.exports = { simulatedAllowed, creditPolicy, CREDIT_DEFAULTS,
  upi, addUpi, collectUpi, settleCollect,
  createQr, scanQr,
  createLink, payLink,
  registerMandate, chargeMandate,
  hold, releaseEscrow, disputeEscrow,
  splitPayment, settleSplit,
  submitKyc, verifyKyc,
  queuePayout, processPayout,
  billers, payBill, settleBill,
  plans, doRecharge, settleRecharge,
  transfer,
  openBnpl, spendBnpl, payEmi,
  emiFor, applyLoan, disburseLoan,
  quoteInsurance, activateInsurance,
  issueVoucher, redeemVoucher
};
