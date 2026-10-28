/* LUXORA Platform — first-class Tax engine (all configuration, single source of truth for
   checkout + invoicing + reports). Rates are DATA: a jurisdiction rate registry (taxRules) with
   classes, plus per-product tax_rule overrides and compliance-based exemptions. Supports
   inclusive vs exclusive pricing, VAT/GST number validation, nexus, and digital-goods rules —
   so a store in any market/configures tax by data, not code.

   Backwards-compatible: `computeLegacy()` reproduces the historical checkout formula exactly
   (so existing behaviour/tests are unchanged); the richer `quote()` is what new surfaces use. */
"use strict";
/* seed data (lib/seed/tax.json): data, not code — the registries are seeded from it */
const SEED_TAX = require("./seed/tax.json");

let _db = null;
const db = () => _db || (_db = require("./db.js"));
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };
const list = (name, dflt) => J((db().get("SELECT items i FROM meta_lists WHERE name=?", name) || {}).i, dflt);
/* tax is money in a currency: computed exactly and rounded once, at that currency's own
   decimals and by its configured rule (lib/money.js) — never at a fixed two decimals, which
   mis-taxed every zero- and three-decimal currency */
const money = require("./money.js");

/* ---- registries (editable in Data Studio) ---- */
/* notes that lived in the seed literal (now lib/seed/tax.json): */
/* how a class is taxed is declared on its row: a fixed `rate`, a `rate_from` field of the
   jurisdiction's rule, the tax modes where a valid buyer VAT number makes it
   `reverse_charge`, and the `default` class for a line that names none */
/* default per-country: {country, mode, standard, reduced, digital, note} — GST/VAT/manual.
   THE ENGINE IS THE SINGLE SOURCE OF TRUTH for a jurisdiction's rates. A country master
   used to carry its own tax_mode/tax_rate, which meant one fact lived in two places and an
   operator editing either one alone silently split tax across surfaces (legacy checkout read
   the country row, quote() read this registry, and they disagreed). Tax is a first-class
   thing that OWNS tax; the country master owns geography. This registry is complete for every
   country the corpus seeds, so nothing is resolved by a fallback into another table — and
   an operator extends it in Data Studio (taxRules) for any country they add. */
/* number-format validators per country (regex + sample). B2B buyers supply VAT/GST/TRN. */
const REGISTRIES = SEED_TAX.REGISTRIES;

function seed() {
  const D = db();
  const ensure = (name, items) => D.run("INSERT OR IGNORE INTO meta_lists(name,label,items) VALUES(?,?,?)", name, name, JSON.stringify(items));
  ensure("taxClasses", REGISTRIES.taxClasses); require("./registry.js").addFields("taxClasses", REGISTRIES.taxClasses, ["default", "rate", "rate_from", "reverse_charge"]); ensure("exemptionReasons", REGISTRIES.exemptionReasons);
  /* taxRules is seeded into the engine's OWN table (tax_rules) and served as the `tax_rule`
     entity — first-class master data with typed fields, not a JSON blob. INSERT OR IGNORE keeps
     an operator's edit: re-seeding never clobbers a rate a merchant changed, and a country the
     corpus newly covers gets its rule on the next boot. */
  for (const r of REGISTRIES.taxRules)
    D.run("INSERT OR IGNORE INTO tax_rules(country,mode,standard,reduced,digital,zero,note) VALUES(?,?,?,?,?,?,?)",
      r.country, r.mode, r.standard, r.reduced != null ? r.reduced : null, r.digital != null ? r.digital : null, r.zero != null ? r.zero : null, r.note || null);
  /* taxNumberFormats must use string patterns; repair any legacy row stored with raw RegExp (which JSON-stored as null) */
  const cur = D.get("SELECT items FROM meta_lists WHERE name='taxNumberFormats'");
  let stale = true; try { const j = JSON.parse(cur && cur.items); stale = !j || Object.values(j).some(v => !v || !v.pattern); } catch (e) { }
  if (!cur || stale) D.run("INSERT INTO meta_lists(name,label,items) VALUES('taxNumberFormats','taxNumberFormats',?) ON CONFLICT(name) DO UPDATE SET items=excluded.items", JSON.stringify(REGISTRIES.taxNumberFormats));
}

function ruleFor(country) {
  const cc = (country || "").toUpperCase();
  /* the engine's own table first — it is the master. The REGISTRIES constant is only the seed
     declaration, so a warm DB that predates the table still resolves on the first boot */
  const row = db().get("SELECT country,mode,standard,reduced,digital,zero,note FROM tax_rules WHERE country=?", cc);
  if (row) return { country: row.country, mode: row.mode, standard: row.standard, reduced: row.reduced, digital: row.digital, zero: row.zero, note: row.note };
  return (REGISTRIES.taxRules.find(r => r.country === cc)) || null;
}
/* the ONE place a store's unconfigured tax resolves from. A store may set its own
   commerce.taxMode/taxRate; when it has not, its default is its jurisdiction's rule in the tax
   engine — never a column on the country master. Centralising this here is what keeps
   "blank = country default" true while tax stays owned by tax: every consumer (checkout,
   invoicing, the storefront label) asks the engine, so an operator's single edit in taxRules is
   reflected everywhere at once instead of drifting against a second copy. */
function defaultRateFor(country) {
  const r = ruleFor(country);
  return { mode: r && r.mode ? r.mode : "manual", rate: r && Number(r.standard) > 0 ? Number(r.standard) : 0 };
}
function validateNumber(country, num) {
  const fmts = list("taxNumberFormats", REGISTRIES.taxNumberFormats); const f = fmts[(country || "").toUpperCase()];
  num = String(num || "").replace(/\s+/g, "").toUpperCase();
  if (!num) return { ok: false, reason: "missing" };
  if (!f) return { ok: true, note: "no format rule for " + country };
  const src = f.pattern || (f.re && f.re.source);
  if (!src) return { ok: true, note: "rule unresolved" };
  let re; try { re = new RegExp(src); } catch (e) { return { ok: true, note: "bad rule" }; }
  return re.test(num) ? { ok: true } : { ok: false, reason: "invalid " + (f.label || country) };
}

/* a bag's tax, exactly: per line (each line's own rate) or on the document, summed unrounded
   and rounded ONCE for the document. lines: [{ amount: Money, rate? }]; goods and other are
   Money in `currency`; other below zero (store credit beyond the fees) taxes nothing */
function computeExact({ perLine, taxRate, lines, goods, other, currency }) {
  const rate = taxRate == null || taxRate === "" ? 0 : taxRate;
  const cur = money.currencyOf(currency);
  const otherPos = other && !money.isNegative(other) ? other : money.zero(cur.code);
  /* the unrounded tax as an exact decimal: Σ amount × rate */
  const parts = perLine
    ? (lines || []).map(l => money.times(money.toString(l.amount), l.rate == null || l.rate === "" ? rate : l.rate)).concat([money.times(money.toString(otherPos), rate)])
    : [money.times(money.toString(money.add(goods, otherPos)), rate)];
  return money.rounded(money.plus(...parts), cur.code);
}
/* the earlier number-in/number-out form, kept for callers that hold numbers: the same exact
   computation in the named currency */
function computeLegacy({ perLine, taxRate, lines, goodsBase, otherTaxable, currency }) {
  const c = money.currencyOf(currency).code;
  const lineAmt = it => money.rounded(money.times(it.unitBase, it.qty), c);
  const t = computeExact({ perLine, taxRate, currency: c, goods: money.rounded(goodsBase || 0, c), other: money.rounded(otherTaxable || 0, c),
    lines: (lines || []).map(it => ({ amount: lineAmt(it), rate: it.tax_rule && it.tax_rule.rate != null ? it.tax_rule.rate : null })) });
  return money.toNumber(t);
}

/* richer quote: per-class + jurisdiction rate + per-product override + exemption + inclusive mode.
   lines: [{ id, class, amount, tax_rule }] ; returns {tax, total, lines:[{...,tax,net}], exempt, notes} */
function quote(opts) {
  const tenantId = opts.tenantId;
  /* a store's tax jurisdiction is the country of its jurisdiction on the kernel (lib/stores.js) */
  const country = String(opts.country || require("./stores.js").country(tenantId)).toUpperCase();
  const rule = ruleFor(country) || {};
  const base = (rule.standard != null && rule.standard > 0) ? rule.standard : Number(opts.storeRate || 0);
  const rate = base;
  const inclusive = opts.inclusive !== false ? false : false; // default exclusive
  const buyerVat = opts.buyerVat; const hasValidVat = buyerVat ? validateNumber(country, buyerVat).ok : false;
  const classes = {}; let defaultClass = null;
  for (const c of list("taxClasses", REGISTRIES.taxClasses)) { classes[c.key] = c; if (c.default && !defaultClass) defaultClass = c.key; }
  // exempt products by compliance revocation: products with a 'revoked'/'expired' certificate of kind 'vat'/'gst' are still taxable; exemption is via buyer VAT (reverse charge) or product exempt class
  /* a quote is in one currency: the caller's, else the store's (lib/defaults.js) */
  const cur = money.currencyOf(opts.currency || require("./defaults.js").currency(tenantId)).code;
  const outLines = []; let tax = money.zero(cur), total = money.zero(cur); let exemptHits = [];
  for (const ln of (opts.lines || [])) {
    const tr = ln.tax_rule || {};
    let r = tr.rate != null ? Number(tr.rate) : rate;
    const cls = ln.class || tr.class || defaultClass;
    const c = classes[cls] || {};
    if (c.rate != null && c.rate !== "") r = Number(c.rate);
    else if (c.rate_from && rule[c.rate_from] != null && tr.rate == null) r = rule[c.rate_from];
    if (tr.exempt) r = 0;
    /* reverse charge: a class that declares it for this tax mode, with a valid buyer VAT
       number, is 0 here and flagged for the buyer's self-assessment */
    let note = "";
    if ((c.reverse_charge || []).includes(rule.mode) && hasValidVat) { r = 0; note = "reverse-charge (B2B)"; exemptHits.push({ line: ln.id, reason: "reverse-charge" }); }
    /* each line in the quote's currency, exactly; its tax rounded once, on the line */
    const amount = money.rounded(ln.amount == null || ln.amount === "" ? 0 : ln.amount, cur);
    let t, net = amount;
    if (opts.inclusive) {
      /* net = amount / (1 + r), exactly divided and rounded once; the tax is what is left */
      net = money.divRate(amount, money.plus(1, r || 0));
      t = money.sub(amount, net);
    } else t = money.mulRate(amount, r || 0);
    tax = money.add(tax, t); total = money.add(total, amount);
    outLines.push({ id: ln.id, class: cls, rate: r, amount: money.toNumber(amount), net: money.toNumber(net), tax: money.toNumber(t), note });
  }
  return { country, currency: cur, mode: rule.mode || "manual", inclusive: !!opts.inclusive, lines: outLines, total: money.toNumber(total), tax: money.toNumber(tax), hasValidVat, exempt: exemptHits };
}

function configFor(tenantId) {
  const country = require("./stores.js").country(tenantId);
  return { country, rule: ruleFor(country.toUpperCase()), classes: list("taxClasses", REGISTRIES.taxClasses) };
}

module.exports = { REGISTRIES, seed, ruleFor, defaultRateFor, validateNumber, computeLegacy, computeExact, quote, configFor, list, J };
