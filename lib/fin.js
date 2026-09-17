/* LUXORA Platform — Payments & Financial services.
   Multi-gateway payment retry, chargeback / dispute lifecycle, batch payout runs to sellers,
   bank-feed reconciliation, and FX-aware ledger reads. Built on the existing payments /
   settlements / wallet_entries ledger so every financial movement is a single source of truth.
   All configuration (dispute states, payout kinds, recon sources, billing meters) lives in
   meta_lists — add new states or meter kinds from Data Studio with zero code. */
"use strict";

const db = () => require("./db.js");
const billing = () => require("./billing.js");
const offers = () => require("./offers.js");
const registry = () => require("./registry.js");
const J = (v, d) => { try { return v == null || v === "" ? (d == null ? [] : d) : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d == null ? [] : d; } };

const DISPUTE_STATES = ["opened", "evidence_requested", "evidence_submitted", "won", "lost", "closed"];
const PAYOUT_KINDS = ["seller", "creator", "partner", "commission", "refund", "cross_border"];
const RECON_SOURCES = ["gateway", "bank", "card_network", "wallet", "crypto"];

/* ---------- schema / registry seed (idempotent) ---------- */
function seed() {
  const D = db();
  const put = (name, label, items) => {
    const existing = D.get("SELECT items FROM meta_lists WHERE name=?", name);
    const cur = J(existing ? existing.items : "[]", []);
    for (const it of items) if (!cur.some(x => (x.key || x) === (it.key || it))) cur.push(it);
    if (existing) D.run("UPDATE meta_lists SET items=? WHERE name=?", JSON.stringify(cur), name);
    else D.run("INSERT INTO meta_lists(name,label,items) VALUES(?,?,?)", name, label, JSON.stringify(cur));
  };
  put("finDisputeStates", "Finance · Dispute states", DISPUTE_STATES.map(k => ({ key: k, name: k })));
  put("finPayoutKinds", "Finance · Payout kinds", PAYOUT_KINDS.map(k => ({ key: k, name: k })));
  put("finReconSources", "Finance · Reconciliation sources", RECON_SOURCES.map(k => ({ key: k, name: k })));
}

/* ---------- multi-gateway retry ---------- */
function attempt(tenantId, paymentId, gateway, status, txnRef, error) {
  const D = db();
  const last = D.get("SELECT MAX(attempt) m FROM payment_attempts WHERE payment_id=? AND tenant_id=?", paymentId, tenantId);
  const n = (last && last.m) ? Number(last.m) + 1 : 1;
  D.run("INSERT INTO payment_attempts(tenant_id,payment_id,gateway,attempt,status,txn_ref,error) VALUES(?,?,?,?,?,?,?)",
    tenantId, paymentId, String(gateway || ""), n, String(status || "pending"), String(txnRef || ""), String(error || ""));
  D.run("UPDATE payments SET status=?, txn_ref=COALESCE(?,txn_ref) WHERE id=? AND tenant_id=?", status, txnRef || null, paymentId, tenantId);
  return n;
}

function retry(tenantId, paymentId, attempts) {
  // mark the payment as retrying; the gateway spec (provider_defs) decides failover order
  const D = db();
  const p = D.get("SELECT * FROM payments WHERE id=? AND tenant_id=?", paymentId, tenantId);
  if (!p) return null;
  if (attempts) attempt(tenantId, p.id, p.gateway, "retry", "", "auto-retry");
  D.run("UPDATE payments SET status='retrying' WHERE id=? AND tenant_id=?", paymentId, tenantId);
  return D.get("SELECT * FROM payments WHERE id=?", paymentId);
}

function attempts(tenantId, paymentId) {
  return db().all("SELECT * FROM payment_attempts WHERE payment_id=? AND tenant_id=? ORDER BY attempt", paymentId, tenantId);
}

/* ---------- disputes / chargebacks ---------- */
function openDispute(tenantId, input) {
  const D = db();
  const ref = "DSP-" + Date.now().toString(36).toUpperCase().slice(-8);
  const r = D.run("INSERT INTO disputes(tenant_id,payment_id,order_id,ref,reason,amount,currency,state) VALUES(?,?,?,?,?,?,?,?)",
    tenantId, Number(input.payment_id) || null, Number(input.order_id) || null, ref,
    String(input.reason || "chargeback"), Number(input.amount) || 0, String(input.currency || "USD"), "opened");
  const id = Number(r.lastInsertRowid);
  return D.get("SELECT * FROM disputes WHERE id=?", id);
}

function transitionDispute(tenantId, disputeId, toState, extra) {
  const D = db();
  if (!DISPUTE_STATES.includes(toState)) throw new Error("Unknown dispute state: " + toState);
  const d = D.get("SELECT * FROM disputes WHERE id=? AND tenant_id=?", disputeId, tenantId);
  if (!d) throw new Error("Unknown dispute " + disputeId);
  const now = new Date().toISOString().slice(0, 19).replace("T", " ");
  if (toState === "won" || toState === "lost") D.run("UPDATE disputes SET state=?, resolution=?, closed_at=? WHERE id=?", toState, (extra && extra.resolution) || "", now, disputeId);
  else D.run("UPDATE disputes SET state=?, resolution=? WHERE id=?", toState, (extra && extra.resolution) || "", disputeId);
  if (toState === "lost" && d.payment_id) {
    // claw back the money: credit a note against the payment's order/owner
    D.run("UPDATE payments SET status='disputed_lost' WHERE id=? AND tenant_id=?", d.payment_id, tenantId);
    billing().recordUsage(tenantId, "dispute.loss", "Chargeback lost — " + (d.ref || ""), 1, Number(d.amount || 0), { currency: d.currency || "USD" });
  }
  return D.get("SELECT * FROM disputes WHERE id=?", disputeId);
}

function disputes(tenantId, f) {
  const D = db(); f = f || {};
  let sql = "SELECT * FROM disputes WHERE tenant_id=?", a = [tenantId];
  if (f.state) { sql += " AND state=?"; a.push(f.state); }
  sql += " ORDER BY id DESC LIMIT 200";
  return D.all(sql, ...a);
}

/* ---------- payout runs ---------- */
function openPayout(tenantId, sellerId, kind, period, items) {
  const D = db();
  const gross = items.reduce((s, i) => s + Number(i.amount || 0), 0);
  const fee = 0; // take-rate / network fee applied per-item by the marketplace module if present
  const net = +(gross - fee).toFixed(2);
  const r = D.run("INSERT INTO payouts(tenant_id,seller_id,kind,ref,period,gross,fee,net,status) VALUES(?,?,?,?,?,?,?,?,?)",
    tenantId, Number(sellerId) || null, String(kind || "seller"), "PMT-" + Date.now().toString(36).toUpperCase().slice(-6),
    String(period || ""), gross, fee, net, "open");
  const pid = Number(r.lastInsertRowid);
  for (const it of items || []) D.run("INSERT INTO payout_items(payout_id,tenant_id,ref,kind,description,amount,currency) VALUES(?,?,?,?,?,?,?)",
    pid, tenantId, String(it.ref || ""), String(it.kind || kind), String(it.description || ""), Number(it.amount || 0), String(it.currency || "USD"));
  return D.get("SELECT * FROM payouts WHERE id=?", pid);
}

function disbursePayout(tenantId, payoutId) {
  const D = db();
  const p = D.get("SELECT * FROM payouts WHERE id=? AND tenant_id=?", payoutId, tenantId);
  if (!p) throw new Error("Unknown payout " + payoutId);
  const now = new Date().toISOString().slice(0, 19).replace("T", " ");
  D.run("UPDATE payouts SET status='disbursed', disbursed_at=? WHERE id=?", now, payoutId);
  D.run("UPDATE payout_items SET settled=1 WHERE payout_id=?", payoutId);
  // single ledger entry: the net amount leaves the platform wallet into the payee's wallet
  if (p.seller_id != null) {
    offers().credit(tenantId, "seller:" + p.seller_id, p.net, "payout", "payout:" + payoutId, p.currency, "finance");
  }
  return D.get("SELECT * FROM payouts WHERE id=?", payoutId);
}

function payoutItems(tenantId, payoutId) {
  return db().all("SELECT * FROM payout_items WHERE payout_id=? AND tenant_id=?", payoutId, tenantId);
}

/* ---------- bank-feed reconciliation ---------- */
function reconcile(tenantId, input) {
  const D = db();
  const lines = Array.isArray(input.lines) ? input.lines : [];
  const period = String(input.period || "");
  const source = String(input.source || "bank");
  const gateway = String(input.gateway || "");
  const r = D.run("INSERT INTO recon_batches(tenant_id,period,gateway,source,lines) VALUES(?,?,?,?,?)", tenantId, period, gateway, source, lines.length);
  const batchId = Number(r.lastInsertRowid);
  let matched = 0, unmatched = 0, total = 0;
  for (const ln of lines) {
    total += Number(ln.amount || 0);
    const hit = D.get("SELECT id FROM payments WHERE tenant_id=? AND txn_ref=? AND status IN ('succeeded','captured','disputed_lost','disputed_won')", tenantId, String(ln.ref || ""));
    const ok = !!hit;
    if (ok) matched++; else unmatched++;
    D.run("INSERT INTO recon_lines(batch_id,tenant_id,ref,source,amount,status,note) VALUES(?,?,?,?,?,?,?)",
      batchId, tenantId, String(ln.ref || ""), source, Number(ln.amount || 0), ok ? "matched" : "unmatched", ok ? "" : (ln.note || "no matching payment"));
  }
  D.run("UPDATE recon_batches SET lines=?, matched=?, unmatched=?, total=?, status=? WHERE id=?",
    lines.length, matched, unmatched, +total.toFixed(2), unmatched === 0 ? "closed" : "open", batchId);
  return D.get("SELECT * FROM recon_batches WHERE id=?", batchId);
}

function reconLines(tenantId, batchId) {
  return db().all("SELECT * FROM recon_lines WHERE batch_id=? AND tenant_id=?", batchId, tenantId);
}

/* ---------- ledger + FX-aware reads ---------- */
function ledger(tenantId, owner) {
  const D = db();
  const rows = D.all("SELECT * FROM wallet_entries WHERE tenant_id=? AND owner=? ORDER BY id DESC LIMIT 500", tenantId, owner);
  return rows.map(e => ({ ...e, note: e.note, fx: e.currency ? registry().fxTo("USD", e.currency) : 1 }));
}

function ledgerFx(tenantId, owner, toCurrency) {
  return ledger(tenantId, owner).map(e => {
    const rate = e.currency && toCurrency ? registry().fxTo(e.currency, toCurrency) : 1;
    return { ...e, amount_local: e.amount, amount_target: +(e.amount * rate).toFixed(4), rate };
  });
}

module.exports = {
  seed, DISPUTE_STATES, PAYOUT_KINDS, RECON_SOURCES,
  attempt, retry, attempts,
  openDispute, transitionDispute, disputes,
  openPayout, disbursePayout, payoutItems,
  reconcile, reconLines,
  ledger, ledgerFx
};
