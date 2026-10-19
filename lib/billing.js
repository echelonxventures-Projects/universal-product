/* LUXORA Platform — first-class Billing engine (line items + tax + usage metering + credit notes
   + dunning + aging). Used for subscription invoices, plan-change proration, metered usage
   (AI units, orders over plan cap, storage), refunds-to-wallet, and platform revenue. All amounts
   in a single currency (platform billing currency, default USD); taxes flow through the Tax engine.
   Complements offers.js (discounts on invoices) + connect.js (gateway payment). */
"use strict";

let _db = null;
const db = () => _db || (_db = require("./db.js"));
/* invoices and credit notes are state machines (lib/states.js): asked by meaning, never named */
const states = require("./states.js");
const stIn = (machine, tag) => { const xs = states.tagged(machine, tag); return { sql: "(" + (xs.length ? xs.map(() => "?").join(",") : "NULL") + ")", args: xs }; };
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };
const r2 = n => +Number(n || 0).toFixed(2);
const DAY = 86400000;

function sub(tenantId) { return db().get(`SELECT s.*, p.name plan, p.price_month, p.currency, p.max_products, p.max_orders_month FROM subscriptions s JOIN plans p ON p.id=s.plan_id WHERE s.tenant_id=? AND s.status IN ${stIn("plan_subscription", "current").sql} ORDER BY s.id DESC`, tenantId, ...stIn("plan_subscription", "current").args); }
function tenantCurrency(tenantId) { return require("./defaults.js").currency(tenantId); }
function nextNumber() { const D = db(); return "INV-" + new Date().getFullYear() + "-" + String(D.get("SELECT COUNT(*) c FROM invoices").c + 1).padStart(4, "0"); }
function nextNoteNumber() { const D = db(); return "CN-" + new Date().getFullYear() + "-" + String(D.get("SELECT COUNT(*) c FROM credit_notes").c + 1).padStart(4, "0"); }

/* ---- metering: record usage of something billable; billed=0 until invoiced ---- */
function recordUsage(tenantId, kind, description, qty, unitAmount, opts) {
  opts = opts || {}; const D = db();
  return Number(D.run("INSERT INTO usage_records(tenant_id,kind,ref,description,qty,unit_amount,amount,currency,period) VALUES(?,?,?,?,?,?,?,?,?)",
    tenantId, kind, opts.ref || "", description, Number(qty) || 0, Number(unitAmount) || 0, r2((Number(qty) || 0) * (Number(unitAmount) || 0)), opts.currency || require("./defaults.js").currency(tenantId), opts.period || monthOf()).lastInsertRowid);
}
function monthOf(d) { return (d || new Date()).toISOString().slice(0, 7); }
/* meter(): the aggregating form of recordUsage — one open row per (kind, period, ref) that grows,
   so a per-redemption meter never explodes an invoice into thousands of lines. */
function meter(tenantId, kind, description, qty, unitAmount, opts) {
  opts = opts || {}; const D = db(); const per = opts.period || monthOf(); const ref = opts.ref || "";
  const q = Number(qty) || 0, u = Number(unitAmount) || 0;
  const row = D.get("SELECT * FROM usage_records WHERE tenant_id=? AND kind=? AND period=? AND ref=? AND billed=0 AND unit_amount=?", tenantId, kind, per, ref, u);
  if (row) { const nq = Number(row.qty) + q; D.run("UPDATE usage_records SET qty=?, amount=? WHERE id=?", nq, r2(nq * u), row.id); return row.id; }
  return recordUsage(tenantId, kind, description || kind, q, u, { ref, period: per, currency: opts.currency || require("./defaults.js").currency(tenantId) });
}
function openUsage(tenantId, period) { return db().all("SELECT * FROM usage_records WHERE tenant_id=? AND billed=0 AND (?='' OR period<=?)", tenantId, period || "", period || "").map(r => ({ ...r, meta: J(r.meta, {}) })); }

/* ---- invoice assembly: plan line + proration + usage lines + tax + discount ---- */
function planFor(tenantId) { return sub(tenantId) || db().get("SELECT id plan_id, name plan, price_month, currency FROM plans ORDER BY position LIMIT 1"); }
function daysBetween(a, b) { return Math.max(0, Math.round((new Date(b).getTime() - new Date(a).getTime()) / DAY)); }

function issueInvoice(tenantId, opts) {
  opts = opts || {}; const D = db();
  const s = sub(tenantId); const cur = opts.currency || (s && s.currency) || require("./defaults.js").currency(tenantId);
  const lines = [];
  if (s) {
    const period_start = opts.period_start || (s.started_at || D.get("SELECT date('now') d").d).slice ? (opts.period_start || D.get("SELECT date('now','start of month') d").d) : new Date().toISOString().slice(0, 10);
    const period_end = opts.period_end || D.get("SELECT date('now','+1 month','start of month','-1 day') d").d;
    const base = Number(s.price_month) || 0;
    lines.push({ kind: "plan", description: `${s.plan} plan — monthly`, qty: 1, unit_amount: base, amount: base, tax_class: "standard", ref: "sub:" + s.plan_id });
    if (opts.prorate && opts.prorationDays) { const pr = r2(base * (opts.prorationDays / 30)); lines.push({ kind: "proration", description: "Prorated adjustment", qty: 1, unit_amount: pr, amount: pr, tax_class: "standard", ref: "prorate" }); }
  }
  for (const u of openUsage(tenantId)) lines.push({ kind: "usage", description: u.description, qty: u.qty, unit_amount: u.unit_amount, amount: u.amount, tax_class: u.kind === "ai" ? "digital" : "standard", ref: "usage:" + u.id });
  // discount from central offers (subscription channel)
  let discount = 0; try { const off = require("./offers.js").discountFor("subscription", tenantId, lines.reduce((n, l) => n + l.amount, 0), {}); discount = off.discount || 0; } catch (e) { }
  const taxOn = (lines.reduce((n, l) => n + l.amount, 0) - discount);
  let tax = 0;
  if (opts.tax !== false) { try { const D2 = db(); const country = require("./stores.js").country(tenantId); /* the invoice's tax comes from the tax engine's own jurisdiction rule — quote() resolves it
      from taxRules. Reading the country master's tax_rate here would re-introduce the second
      source of truth that drifts against taxRules (and it used to OVERRIDE the engine for any
      country whose rule is positive, so an operator's taxRules edit never reached an invoice) */
    const tx = require("./tax.js").quote({ tenantId, country, lines: lines.map(l => ({ id: l.ref, class: l.tax_class, amount: l.amount, tax_rule: {} })), inclusive: false }); tax = r2(tx.tax); } catch (e) { } }
  const amount = r2(Math.max(0, taxOn) + tax);
  const num = opts.number || nextNumber();
  const invId = Number(D.run("INSERT INTO invoices(tenant_id,number,period_start,period_end,amount,currency,status,note) VALUES(?,?,?,?,?,?,?,?)",
    tenantId, num, (lines.find(l => l.kind === "plan") ? D.get("SELECT date('now','start of month') d").d : null), D.get("SELECT date('now','+1 month','start of month','-1 day') d").d, amount, cur, states.initial("invoice"), opts.note || "Subscription").lastInsertRowid);
  for (const l of lines) D.run("INSERT INTO invoice_lines(invoice_id,tenant_id,kind,description,qty,unit_amount,amount,tax_class,ref) VALUES(?,?,?,?,?,?,?,?,?)", invId, tenantId, l.kind, l.description, l.qty, r2(l.unit_amount), r2(l.amount), l.tax_class, l.ref);
  if (discount) D.run("INSERT INTO invoice_lines(invoice_id,tenant_id,kind,description,qty,unit_amount,amount,tax_class,ref) VALUES(?,?,?,?,?,?,?,'standard','offer')", invId, tenantId, "discount", "Offer discount", 1, -discount, -discount);
  if (tax) D.run("INSERT INTO invoice_lines(invoice_id,tenant_id,kind,description,qty,unit_amount,amount,tax_class,ref) VALUES(?,?,?,?,?,?,?,'standard','tax')", invId, tenantId, "tax", "Tax", 1, tax, tax);
  D.run("INSERT INTO billing_events(tenant_id,invoice_id,kind,detail) VALUES(?,?, 'invoice.created', ?)", tenantId, invId, JSON.stringify({ number: num, amount }));
  for (const u of openUsage(tenantId)) D.run("UPDATE usage_records SET billed=1 WHERE id=?", u.id);
  return { id: invId, number: num, amount, tax, discount, lines };
}

/* ---- proration on plan change: emit a line + return days for invoice ---- */
function prorationDays(tenantId, from, to) {
  const D = db(); const s = sub(tenantId); if (!s) return 0;
  const cycleEnd = D.get("SELECT date(renews_at) d FROM subscriptions WHERE id=?", s.id).d;
  return Math.max(0, daysBetween(new Date().toISOString().slice(0, 10), cycleEnd));
}

/* ---- credit note / refund (optionally to wallet) ---- */
function creditNote(tenantId, invoiceId, amount, reason, opts) {
  opts = opts || {}; const D = db(); const inv = D.get("SELECT * FROM invoices WHERE id=? AND tenant_id=?", Number(invoiceId), tenantId); if (!inv) return { error: "Unknown invoice" };
  const num = nextNoteNumber(); const cnId = Number(D.run("INSERT INTO credit_notes(tenant_id,number,invoice_id,amount,currency,reason,status,to_wallet) VALUES(?,?,?,?,?,?,?,?)", tenantId, num, inv.id, r2(Math.abs(Number(amount) || inv.amount)), inv.currency, String(reason || ""), states.initial("credit_note"), opts.to_wallet ? 1 : 0).lastInsertRowid);
  D.run("INSERT INTO billing_events(tenant_id,invoice_id,kind,detail) VALUES(?,?, 'credit.note', ?)", tenantId, inv.id, JSON.stringify({ number: num, amount: r2(Math.abs(Number(amount) || inv.amount)), to_wallet: !!opts.to_wallet }));
  if (opts.to_wallet) { try { require("./offers.js").credit(tenantId, opts.owner || ("t" + tenantId + ":u:billing"), r2(Number(amount) || inv.amount), "refund", "credit:" + num, require("./defaults.js").currency(tenantId), "subscription", "billing"); } catch (e) { } }
  return { ok: true, number: num, id: cnId, amount: r2(Number(amount) || inv.amount) };
}
function voidNote(id) { db().run("UPDATE credit_notes SET status=? WHERE id=?", states.first("credit_note", "void"), Number(id)); return { ok: true }; }

/* ---- dunning: overdue invoices → escalating events (email handled by caller) ---- */
function dunning(tenantId) {
  const D = db(); const col = stIn("invoice", "collectable"); const overdue = D.all("SELECT * FROM invoices WHERE tenant_id=? AND status IN " + col.sql + " AND period_end IS NOT NULL AND period_end < date('now')", tenantId, ...col.args);
  const out = [];
  for (const inv of overdue) { const days = daysBetween(inv.period_end, new Date().toISOString().slice(0, 10)); D.run("UPDATE invoices SET status=? WHERE id=?", states.first("invoice", "late"), inv.id);
    const stage = days >= 30 ? "final_notice" : days >= 14 ? "suspend_warning" : days >= 7 ? "second" : "first";
    D.run("INSERT INTO billing_events(tenant_id,invoice_id,kind,detail) VALUES(?,?, 'dunning', ?)", tenantId, inv.id, JSON.stringify({ stage, days }));
    out.push({ invoice: inv.number, days, stage }); }
  return { ok: true, actions: out };
}

/* ---- aging buckets + revenue snapshot (platform + per tenant) ---- */
function aging(tenantId) {
  const D = db(); const col = stIn("invoice", "collectable"); const rows = D.all("SELECT amount, period_end, status FROM invoices WHERE (?=0 OR tenant_id=?) AND status IN " + col.sql, tenantId || 0, tenantId || 0, ...col.args);
  const b = { current: 0, d30: 0, d60: 0, d90: 0 }; const now = Date.now();
  for (const r of rows) { const days = r.period_end ? Math.round((now - new Date(r.period_end).getTime()) / DAY) : 0; const amt = Number(r.amount) || 0;
    if (days <= 0) b.current += amt; else if (days <= 30) b.d30 += amt; else if (days <= 60) b.d60 += amt; else b.d90 += amt; }
  return { buckets: b, total: r2(b.current + b.d30 + b.d60 + b.d90) };
}

/* ---- tenant-facing summary + lines ---- */
function invoice(tenantId, id) { const inv = db().get("SELECT * FROM invoices WHERE id=? AND (?=0 OR tenant_id=?)", Number(id), tenantId || 0, tenantId || 0); if (!inv) return null; inv.lines = db().all("SELECT * FROM invoice_lines WHERE invoice_id=? ORDER BY id", inv.id); return inv; }
function list(tenantId) { const D = db(); const invs = D.all("SELECT * FROM invoices WHERE (?=0 OR tenant_id=?) ORDER BY id DESC LIMIT 200", tenantId || 0, tenantId || 0).map(i => { i.lines = D.all("SELECT kind, description, qty, unit_amount, amount, tax, tax_class FROM invoice_lines WHERE invoice_id=? ORDER BY id", i.id); return i; }); const notes = D.all("SELECT * FROM credit_notes WHERE (?=0 OR tenant_id=?) ORDER BY id DESC LIMIT 200", tenantId || 0, tenantId || 0); const events = D.all("SELECT * FROM billing_events WHERE (?=0 OR tenant_id=?) ORDER BY id DESC LIMIT 200", tenantId || 0, tenantId || 0); return { invoices: invs, notes, events }; }

module.exports = { sub, recordUsage, meter, openUsage, issueInvoice, prorationDays, creditNote, voidNote, dunning, aging, invoice, list, planFor, r2, monthOf };
