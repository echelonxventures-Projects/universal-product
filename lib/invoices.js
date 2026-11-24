/* LUXORA Platform — tax invoices and credit notes for a store's orders.

   One invoice per order, issued once the order is paid or handed over, never altered: what it says
   is what was true then. Numbers run in one unbroken series per store and fiscal year, taken in the
   same transaction that writes the document. How a tax mode invoices — its title, what its tax
   number and item code are called, when its fiscal year starts and which parts the tax splits into
   inside or across a state — is declared (lib/seed/tax.json INVOICING), never written here. A refund
   has its own credit note, against the invoice it corrects. */
"use strict";

const db = () => require("./db.js");
const states = require("./states.js");
const reg = () => require("./registry.js");
const RULES = require("./seed/tax.json").INVOICING;
const tx = fn => require("./kernel.js").internal.tx(fn);
const fail = (msg, status) => Object.assign(new Error(msg), { status: status || 400 });
const J = (v, d) => { try { return v ? JSON.parse(v) : d; } catch (e) { return d; } };
const same = (a, b) => String(a || "").trim().toLowerCase() === String(b || "").trim().toLowerCase();

const settingsOf = tid => require("./settings.js").load(tid);
function ruleOf(tid) {
  const c = settingsOf(tid).commerce;
  const mode = c.taxMode || require("./tax.js").defaultRateFor(c.country).mode;
  return { mode, ...(RULES.default || {}), ...(RULES[mode] || {}) };
}
/* the fiscal year a date falls in, as its series shows it: 2627 for April 2026 to March 2027 */
function yearLabel(date, startMonth) {
  const y = date.getUTCFullYear(), m = date.getUTCMonth() + 1, start = Number(startMonth) || 1;
  if (start === 1) return String(y).slice(2);
  const from = m >= start ? y : y - 1;
  return String(from).slice(2) + String(from + 1).slice(2);
}
function nextNumber(tid, kind, rule) {
  const D = db(), series = (rule.prefix || {})[kind] + yearLabel(new Date(), rule.fiscalStart);
  D.run("INSERT OR IGNORE INTO invoice_series(tenant_id,series,next) VALUES(?,?,1)", tid, series);
  const n = D.get("SELECT next FROM invoice_series WHERE tenant_id=? AND series=?", tid, series).next;
  D.run("UPDATE invoice_series SET next=next+1 WHERE tenant_id=? AND series=?", tid, series);
  return series + "/" + String(n).padStart(5, "0");
}
const due = order => states.has("order", order.status) && (states.is("order", order.status, "dispatched")
  || !!db().get("SELECT 1 x FROM payments WHERE order_id=? AND status IN (" + states.tagged("payment", "settled").concat(states.tagged("payment", "reversed")).map(() => "?").join(",") + ")", order.id, ...states.tagged("payment", "settled"), ...states.tagged("payment", "reversed")));

/* an amount shared out by weight, to the cent, with nothing lost to rounding */
function share(total, weights, decimals) {
  const k = 10 ** decimals, sum = weights.reduce((a, b) => a + b, 0);
  let left = Math.round(total * k);
  return weights.map((w, i) => { const v = i === weights.length - 1 ? left : Math.round(sum > 0 ? total * k * w / sum : 0); left -= v; return v / k; });
}
/* the document's body, from the order as it was placed */
function compose(tid, order, rule) {
  const D = db(), s = settingsOf(tid), legal = s.legal || {}, cur = reg().currency(order.currency) || { decimals: 2 }, dec = cur.decimals != null ? cur.decimals : 2;
  const items = D.all("SELECT product_id, sku_id, qty, price FROM order_items WHERE order_id=?", order.id).map(i => {
    const p = D.get("SELECT title, identity, tax_rule FROM products WHERE tenant_id=? AND id=?", tid, i.product_id) || {};
    const k = i.sku_id ? D.get("SELECT name, identity FROM skus WHERE id=?", i.sku_id) : null;
    const id = { ...J(p.identity, {}), ...J(k && k.identity, {}) };
    return { description: (p.title || i.product_id) + (k && k.name && !same(k.name, "Default") ? " — " + k.name : ""), code: String(id[rule.codeField] || ""), qty: Number(i.qty), value: Number(i.price) * Number(i.qty), rate: Number((J(p.tax_rule, {}) || {}).rate) };
  });
  const gross = Number(order.total) + Number(order.gift_used || 0), taxTotal = Number(order.tax) || 0, ship = Number(order.ship_fee) || 0;
  const goods = Math.max(0, gross - taxTotal - ship);
  const lines = items.concat(ship > 0 ? [{ description: "Delivery", code: "", qty: 1, value: ship, rate: NaN, ship: true }] : []);
  const taxable = share(goods, items.map(i => i.value), dec).concat(ship > 0 ? [ship] : []);
  const tax = share(taxTotal, lines.map((l, i) => taxable[i] * (isFinite(l.rate) ? l.rate : 1 * (Number(s.commerce.taxRate) || Number(require("./tax.js").defaultRateFor(s.commerce.country).rate) || 1))), dec);
  const inState = legal.state && order.state && same(legal.state, order.state);
  const parts = (rule.parts || []).filter(p => p.where === "any" || (p.where === "same_state") === !!inState);
  const split = parts.length && taxTotal > 0 ? parts.map((p, i) => ({ name: p.name, amount: share(taxTotal, parts.map(x => x.share), dec)[i] })) : taxTotal > 0 ? [{ name: rule.taxName, amount: taxTotal }] : [];
  return {
    title: rule.title, numberLabel: rule.numberLabel, codeLabel: rule.codeLabel, currency: order.currency, decimals: dec, order: order.num, placed: order.created_at,
    seller: { name: legal.businessName || (s.brand && s.brand.name) || "", address: legal.address || "", state: legal.state || "", taxId: legal.taxId || "", companyId: legal.companyId || "", email: legal.supportEmail || "" },
    buyer: { name: order.name || "", address: [order.address, order.city, order.state, order.zip].filter(Boolean).join(", "), taxId: order.buyer_tax_id || "" },
    placeOfSupply: order.state || "",
    lines: lines.map((l, i) => ({ description: l.description, code: l.code, qty: l.qty, taxable: taxable[i], tax: tax[i], rate: taxable[i] > 0 ? +(tax[i] / taxable[i] * 100).toFixed(2) : 0, total: +(taxable[i] + tax[i]).toFixed(dec) })),
    taxes: split, taxable: +(goods + ship).toFixed(dec), tax: +taxTotal.toFixed(dec), total: +gross.toFixed(dec), fromBalance: +Number(order.gift_used || 0).toFixed(dec)
  };
}
const present = d => d && ({ id: d.id, ref: d.ref, number: d.invoice_number, kind: d.doc_kind, issued: d.created_at, order_id: d.order_id, ...J(d.body, {}) });
const find = (tid, orderId, kind, ref) => db().get("SELECT * FROM invoice_documents WHERE tenant_id=? AND order_id=? AND doc_kind=?" + (ref ? " AND ref=?" : "") + " ORDER BY id LIMIT 1", Number(tid), Number(orderId), kind, ...(ref ? [ref] : []));
const missing = tid => { const l = settingsOf(tid).legal || {}, rule = ruleOf(tid); return (rule.needs || []).filter(k => !String(l[k] || "").trim()); };
function write(tid, order, kind, ref, rule, body) {
  const number = nextNumber(Number(tid), kind, rule);
  const r = db().run("INSERT INTO invoice_documents(tenant_id,ref,order_id,owner,doc_kind,invoice_number,place_of_supply,gstin,pan,taxable,tax,total,currency,body,status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?, 'generated')",
    Number(tid), ref, order.id, order.owner, kind, number, body.placeOfSupply, body.seller.taxId, "", body.taxable, body.tax, body.total, order.currency || "", JSON.stringify(body));
  return db().get("SELECT * FROM invoice_documents WHERE id=?", r.lastInsertRowid);
}
/* the order's invoice: the one already issued, else issued now */
function invoice(tid, order) {
  const kind = RULES.kinds.invoice, have = find(tid, order.id, kind);
  if (have) return present(have);
  if (!due(order)) throw fail("The invoice is issued once the order is paid or on its way", 409);
  const gaps = missing(tid);
  if (gaps.length) throw fail("The store has not filled in its tax details yet", 409);
  return present(tx(() => find(tid, order.id, kind) || write(tid, order, kind, "INV:" + order.id, ruleOf(tid), compose(tid, order, ruleOf(tid)))));
}
/* a credit note for each refund made on an invoiced order */
function credits(tid, order) {
  const inv = find(tid, order.id, RULES.kinds.invoice);
  if (!inv) return [];
  const body = J(inv.body, {}), kind = RULES.kinds.credit, rule = ruleOf(tid);
  return require("./refunds.js").listFor(tid, order.id).filter(r => r.done).map(r => {
    const ref = "CN:" + r.id, have = find(tid, order.id, kind, ref);
    if (have) return present(have);
    const k = 10 ** (body.decimals == null ? 2 : body.decimals), tax = Math.round(Number(r.amount) * k * (body.total > 0 ? body.tax / body.total : 0)) / k;
    const b = { ...body, title: rule.creditTitle, against: inv.invoice_number, reason: r.reason || "", lines: [{ description: "Refund" + (r.reason ? " — " + r.reason : ""), code: "", qty: 1, taxable: +(r.amount - tax).toFixed(body.decimals), tax, rate: "", total: Number(r.amount) }],
      taxes: (body.taxes || []).map(t => ({ name: t.name, amount: Math.round(tax * k * (body.tax > 0 ? t.amount / body.tax : 0)) / k })), taxable: +(r.amount - tax).toFixed(body.decimals), tax, total: Number(r.amount), fromBalance: 0 };
    return present(tx(() => find(tid, order.id, kind, ref) || write(tid, order, kind, ref, rule, b)));
  });
}
const documents = (tid, order) => ({ invoice: invoice(tid, order), credits: credits(tid, order) });

module.exports = { documents, invoice, credits, yearLabel, missing };
