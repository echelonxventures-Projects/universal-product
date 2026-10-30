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
/* money is exact, in the invoice's own currency (lib/money.js): each line is unit × quantity
   rounded once, the discount and tax once each, the total their exact sum — never a fixed two
   decimals. r2 stays for the callers that round a plain figure in a currency they name */
const money = require("./money.js");
const MS = () => require("./money-store.js");
const r2 = (n, currency) => money.toNumber(money.rounded(n || 0, currency || require("./defaults.js").platformCurrency()));
const DAY = 86400000;

function sub(tenantId) { return db().get(`SELECT s.*, p.name plan, p.price_month, p.currency, p.max_products, p.max_orders_month FROM subscriptions s JOIN plans p ON p.id=s.plan_id WHERE s.tenant_id=? AND s.status IN ${stIn("plan_subscription", "current").sql} ORDER BY s.id DESC`, tenantId, ...stIn("plan_subscription", "current").args); }
function tenantCurrency(tenantId) { return require("./defaults.js").currency(tenantId); }
function nextNumber() { const D = db(); return "INV-" + new Date().getFullYear() + "-" + String(D.get("SELECT COUNT(*) c FROM invoices").c + 1).padStart(4, "0"); }
function nextNoteNumber() { const D = db(); return "CN-" + new Date().getFullYear() + "-" + String(D.get("SELECT COUNT(*) c FROM credit_notes").c + 1).padStart(4, "0"); }

/* ---- metering: record usage of something billable; billed=0 until invoiced ---- */
function recordUsage(tenantId, kind, description, qty, unitAmount, opts) {
  opts = opts || {}; const D = db();
  return Number(D.run("INSERT INTO usage_records(tenant_id,kind,ref,description,qty,unit_amount,amount,currency,period) VALUES(?,?,?,?,?,?,?,?,?)",
    tenantId, kind, opts.ref || "", description, Number(qty) || 0, Number(unitAmount) || 0, usageAmount(qty, unitAmount, opts.currency || require("./defaults.js").currency(tenantId)), opts.currency || require("./defaults.js").currency(tenantId), opts.period || monthOf()).lastInsertRowid);
}
/* metered usage is a rate × a quantity; its amount is their exact product, rounded once */
function usageAmount(qty, unit, currency) { return money.toNumber(money.rounded(money.times(Number(unit) || 0, Number(qty) || 0), currency)); }
function monthOf(d) { return (d || new Date()).toISOString().slice(0, 7); }
/* meter(): the aggregating form of recordUsage — one open row per (kind, period, ref) that grows,
   so a per-redemption meter never explodes an invoice into thousands of lines. */
function meter(tenantId, kind, description, qty, unitAmount, opts) {
  opts = opts || {}; const D = db(); const per = opts.period || monthOf(); const ref = opts.ref || "";
  const q = Number(qty) || 0, u = Number(unitAmount) || 0;
  const row = D.get("SELECT * FROM usage_records WHERE tenant_id=? AND kind=? AND period=? AND ref=? AND billed=0 AND unit_amount=?", tenantId, kind, per, ref, u);
  if (row) { const nq = Number(money.plus(row.qty, q)); D.run("UPDATE usage_records SET qty=?, amount=? WHERE id=?", nq, usageAmount(nq, u, row.currency), row.id); return row.id; }
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
    const base = money.rounded(s.price_month || 0, cur);
    lines.push({ kind: "plan", description: `${s.plan} plan — monthly`, qty: 1, unit: base, amount: base, tax_class: "standard", ref: "sub:" + s.plan_id });
    if (opts.prorate && opts.prorationDays) { const pr = money.divRate(money.mulQty(base, opts.prorationDays), 30); lines.push({ kind: "proration", description: "Prorated adjustment", qty: 1, unit: pr, amount: pr, tax_class: "standard", ref: "prorate" }); }
  }
  /* an invoice is in one currency: usage metered in another stays open and is reported, never
     added to it as if it were the same money */
  const billed = [], otherCurrency = [];
  for (const u of openUsage(tenantId)) {
    if (String(u.currency || "").toUpperCase() !== String(cur).toUpperCase()) { otherCurrency.push({ id: u.id, currency: u.currency }); continue; }
    const unit = money.rounded(u.unit_amount || 0, cur);
    lines.push({ kind: "usage", description: u.description, qty: u.qty, unit, amount: money.rounded(money.times(money.toString(unit), u.qty || 0), cur), tax_class: u.kind === "ai" ? "digital" : "standard", ref: "usage:" + u.id });
    billed.push(u.id);
  }
  const gross = money.sum(lines.map(l => l.amount), cur);
  // discount from central offers (subscription channel)
  let discount = money.zero(cur); try { const off = require("./offers.js").discountFor("subscription", tenantId, money.toNumber(gross), {}); discount = money.min(money.rounded(off.discount || 0, cur), gross); } catch (e) { }
  const taxOn = money.sub(gross, discount);
  let tax = money.zero(cur);
  if (opts.tax !== false) { const country = require("./stores.js").country(tenantId); /* the invoice's tax comes from the tax engine's own jurisdiction rule — quote() resolves it
      from taxRules. Reading the country master's tax_rate here would re-introduce the second
      source of truth that drifts against taxRules (and it used to OVERRIDE the engine for any
      country whose rule is positive, so an operator's taxRules edit never reached an invoice) */
    const tx = require("./tax.js").quote({ tenantId, country, currency: cur, lines: lines.map(l => ({ id: l.ref, class: l.tax_class, amount: money.toString(l.amount), tax_rule: {} })), inclusive: false }); tax = money.rounded(tx.tax, cur); }
  const amount = money.add(money.max(money.zero(cur), taxOn), tax);
  const num = opts.number || nextNumber();
  const invId = Number(MS().insert("invoices", { tenant_id: tenantId, number: num, period_start: lines.find(l => l.kind === "plan") ? D.get("SELECT date('now','start of month') d").d : null, period_end: D.get("SELECT date('now','+1 month','start of month','-1 day') d").d, status: states.initial("invoice"), note: opts.note || "Subscription" }, cur, { amount }).lastInsertRowid);
  const line = (kind, description, qty, unit, amt, taxClass, ref) => MS().insert("invoice_lines", { invoice_id: invId, tenant_id: tenantId, kind, description, qty, tax_class: taxClass, ref }, cur, { unit_amount: unit, amount: amt });
  for (const l of lines) line(l.kind, l.description, l.qty, l.unit, l.amount, l.tax_class, l.ref);
  if (!money.isZero(discount)) line("discount", "Offer discount", 1, money.neg(discount), money.neg(discount), "standard", "offer");
  if (!money.isZero(tax)) line("tax", "Tax", 1, tax, tax, "standard", "tax");
  D.run("INSERT INTO billing_events(tenant_id,invoice_id,kind,detail) VALUES(?,?, 'invoice.created', ?)", tenantId, invId, JSON.stringify({ number: num, amount: money.toString(amount), currency: cur, usage_in_other_currency: otherCurrency }));
  for (const id of billed) D.run("UPDATE usage_records SET billed=1 WHERE id=?", id);
  const N = money.toNumber;
  return { id: invId, number: num, amount: N(amount), tax: N(tax), discount: N(discount), currency: cur, money: { v: money.SERIAL_VERSION, amount: money.toJSON(amount), tax: money.toJSON(tax), discount: money.toJSON(discount) },
    lines: lines.map(l => ({ kind: l.kind, description: l.description, qty: l.qty, unit_amount: N(l.unit), amount: N(l.amount), tax_class: l.tax_class, ref: l.ref })), usage_in_other_currency: otherCurrency };
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
  /* a credit note is exact money in the invoice's currency (its amount, or the given part of it) */
  const full = MS().amountOf("invoices", inv, "amount");
  const amt = amount == null || amount === "" ? full : money.of(money.isMoney(amount) ? amount : String(amount).replace(/^-/, ""), full.currency);
  const num = nextNoteNumber();
  const cnId = Number(MS().insert("credit_notes", { tenant_id: tenantId, number: num, invoice_id: inv.id, reason: String(reason || ""), status: states.initial("credit_note"), to_wallet: opts.to_wallet ? 1 : 0 }, full.currency, { amount: amt }).lastInsertRowid);
  D.run("INSERT INTO billing_events(tenant_id,invoice_id,kind,detail) VALUES(?,?, 'credit.note', ?)", tenantId, inv.id, JSON.stringify({ number: num, amount: money.toString(amt), currency: amt.currency, to_wallet: !!opts.to_wallet }));
  /* to the store's wallet in the invoice's own currency — the money the credit note is in */
  if (opts.to_wallet) { try { require("./offers.js").credit(tenantId, opts.owner || ("t" + tenantId + ":u:billing"), money.toString(amt), "refund", "credit:" + num, amt.currency, "subscription", "billing"); } catch (e) { } }
  return { ok: true, number: num, id: cnId, amount: money.toNumber(amt), money: money.toJSON(amt) };
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
  const D = db(); const col = stIn("invoice", "collectable"); const rows = D.all("SELECT amount, amount_minor, currency, money_scale, money_state, period_end, status FROM invoices WHERE (?=0 OR tenant_id=?) AND status IN " + col.sql, tenantId || 0, tenantId || 0, ...col.args);
  /* summed exactly, per currency: amounts in two currencies are never one figure. `buckets` and
     `total` are the platform currency's (what the console has always shown); `byCurrency` has
     every currency, and invoices under money review are counted apart, not guessed */
  const now = Date.now(), per = {}; let underReview = 0;
  for (const r of rows) {
    let amt; try { amt = MS().amountOf("invoices", r, "amount"); } catch (e) { underReview++; continue; }
    if (!amt) continue;
    const days = r.period_end ? Math.round((now - new Date(r.period_end).getTime()) / DAY) : 0;
    const k = days <= 0 ? "current" : days <= 30 ? "d30" : days <= 60 ? "d60" : "d90";
    const b = per[amt.currency] || (per[amt.currency] = { current: money.zero(amt.currency), d30: money.zero(amt.currency), d60: money.zero(amt.currency), d90: money.zero(amt.currency) });
    b[k] = money.add(b[k], amt);
  }
  const N = money.toNumber, byCurrency = {};
  for (const [c, b] of Object.entries(per)) byCurrency[c] = { current: N(b.current), d30: N(b.d30), d60: N(b.d60), d90: N(b.d90), total: N(money.add(b.current, b.d30, b.d60, b.d90)) };
  const pc = require("./defaults.js").platformCurrency(), main = byCurrency[pc] || { current: 0, d30: 0, d60: 0, d90: 0, total: 0 };
  return { buckets: { current: main.current, d30: main.d30, d60: main.d60, d90: main.d90 }, total: main.total, currency: pc, byCurrency, underReview };
}

/* ---- tenant-facing summary + lines ---- */
function invoice(tenantId, id) { const inv = db().get("SELECT * FROM invoices WHERE id=? AND (?=0 OR tenant_id=?)", Number(id), tenantId || 0, tenantId || 0); if (!inv) return null; inv.lines = db().all("SELECT * FROM invoice_lines WHERE invoice_id=? ORDER BY id", inv.id); return inv; }
function list(tenantId) { const D = db(); const invs = D.all("SELECT * FROM invoices WHERE (?=0 OR tenant_id=?) ORDER BY id DESC LIMIT 200", tenantId || 0, tenantId || 0).map(i => { i.lines = D.all("SELECT kind, description, qty, unit_amount, amount, tax, tax_class FROM invoice_lines WHERE invoice_id=? ORDER BY id", i.id); return i; }); const notes = D.all("SELECT * FROM credit_notes WHERE (?=0 OR tenant_id=?) ORDER BY id DESC LIMIT 200", tenantId || 0, tenantId || 0); const events = D.all("SELECT * FROM billing_events WHERE (?=0 OR tenant_id=?) ORDER BY id DESC LIMIT 200", tenantId || 0, tenantId || 0); return { invoices: invs, notes, events }; }

module.exports = { sub, recordUsage, meter, openUsage, issueInvoice, prorationDays, creditNote, voidNote, dunning, aging, invoice, list, planFor, r2, monthOf };
