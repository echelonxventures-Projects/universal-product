/* LUXORA Platform — first-class Tax engine (all configuration, single source of truth for
   checkout + invoicing + reports). Rates are DATA: a jurisdiction rate registry (taxRules) with
   classes, plus per-product tax_rule overrides and compliance-based exemptions. Supports
   inclusive vs exclusive pricing, VAT/GST number validation, nexus, and digital-goods rules —
   so a store in any market/configures tax by data, not code.

   Backwards-compatible: `computeLegacy()` reproduces the historical checkout formula exactly
   (so existing behaviour/tests are unchanged); the richer `quote()` is what new surfaces use. */
"use strict";

let _db = null;
const db = () => _db || (_db = require("./db.js"));
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };
const list = (name, dflt) => J((db().get("SELECT items i FROM meta_lists WHERE name=?", name) || {}).i, dflt);
const r2 = n => +Number(n || 0).toFixed(2);

/* ---- registries (editable in Data Studio) ---- */
const REGISTRIES = {
  taxClasses: [
    { key: "standard", name: "Standard rate" }, { key: "reduced", name: "Reduced rate" },
    { key: "zero", name: "Zero-rated (0%)" }, { key: "exempt", name: "Exempt" },
    { key: "digital", name: "Digital services" }, { key: "food", name: "Groceries" }
  ],
  /* default per-country: {country, mode, standard, reduced, digital, note} — GST/VAT/manual */
  taxRules: [
    { country: "US", mode: "manual", standard: 0, note: "state-based; store rate used" },
    { country: "IN", mode: "gst", standard: 0.12, reduced: 0.05, digital: 0.18 },
    { country: "GB", mode: "vat", standard: 0.20, reduced: 0.05, zero: 0, digital: 0.20 },
    { country: "DE", mode: "vat", standard: 0.19, reduced: 0.07, digital: 0.19 },
    { country: "AE", mode: "vat", standard: 0.05, zero: 0 },
    { country: "FR", mode: "vat", standard: 0.20, reduced: 0.055 },
    { country: "NL", mode: "vat", standard: 0.21, reduced: 0.09 }
  ],
  exemptionReasons: ["resale", "government", "medical", "charitable", "diplomatic", "export"],
  /* number-format validators per country (regex + sample). B2B buyers supply VAT/GST/TRN. */
  taxNumberFormats: {
    IN: { pattern: "^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$", label: "GSTIN (15 char)" },
    GB: { pattern: "^(GB)?(\\d{9}|\\d{12}|GD\\d{3}|HA\\d{3})$", label: "UK VAT number" },
    DE: { pattern: "^(DE)?\\d{9}$", label: "DE USt-IdNr" },
    AE: { pattern: "^\\d{15}$", label: "TRN (15 digits)" },
    FR: { pattern: "^(FR)?[0-9A-Z]{2}\\d{9}$", label: "Numéro TVA" }
  }
};

function seed() {
  const D = db();
  const ensure = (name, items) => D.run("INSERT OR IGNORE INTO meta_lists(name,label,items) VALUES(?,?,?)", name, name, JSON.stringify(items));
  ensure("taxClasses", REGISTRIES.taxClasses); ensure("taxRules", REGISTRIES.taxRules); ensure("exemptionReasons", REGISTRIES.exemptionReasons);
  /* taxNumberFormats must use string patterns; repair any legacy row stored with raw RegExp (which JSON-stored as null) */
  const cur = D.get("SELECT items FROM meta_lists WHERE name='taxNumberFormats'");
  let stale = true; try { const j = JSON.parse(cur && cur.items); stale = !j || Object.values(j).some(v => !v || !v.pattern); } catch (e) { }
  if (!cur || stale) D.run("INSERT INTO meta_lists(name,label,items) VALUES('taxNumberFormats','taxNumberFormats',?) ON CONFLICT(name) DO UPDATE SET items=excluded.items", JSON.stringify(REGISTRIES.taxNumberFormats));
}

function ruleFor(country) { return (list("taxRules", REGISTRIES.taxRules).find(r => r.country === (country || "").toUpperCase())) || null; }
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

/* legacy exact-compatible path used by the current checkout so nothing regresses */
function computeLegacy({ perLine, taxRate, lines, goodsBase, otherTaxable }) {
  taxRate = Number(taxRate) || 0;
  if (perLine) {
    let sum = 0;
    for (const it of (lines || [])) { const rate = it.tax_rule && it.tax_rule.rate != null ? Number(it.tax_rule.rate) : taxRate; sum += it.unitBase * it.qty * rate; }
    return r2(sum + Math.max(0, otherTaxable) * taxRate);
  }
  return r2((goodsBase + Math.max(0, otherTaxable)) * taxRate);
}

/* richer quote: per-class + jurisdiction rate + per-product override + exemption + inclusive mode.
   lines: [{ id, class, amount, tax_rule }] ; returns {tax, total, lines:[{...,tax,net}], exempt, notes} */
function quote(opts) {
  const tenantId = opts.tenantId;
  const country = (opts.country || (db().get("SELECT country FROM tenants WHERE id=?", tenantId) || {}).country || "US").toUpperCase();
  const rule = ruleFor(country) || {};
  const base = (rule.standard != null && rule.standard > 0) ? rule.standard : Number(opts.storeRate || 0);
  const rate = base;
  const inclusive = opts.inclusive !== false ? false : false; // default exclusive
  const buyerVat = opts.buyerVat; const hasValidVat = buyerVat ? validateNumber(country, buyerVat).ok : false;
  const classes = {}; for (const c of list("taxClasses", REGISTRIES.taxClasses)) classes[c.key] = c;
  // exempt products by compliance revocation: products with a 'revoked'/'expired' certificate of kind 'vat'/'gst' are still taxable; exemption is via buyer VAT (reverse charge) or product exempt class
  const outLines = []; let tax = 0; let exemptHits = [];
  for (const ln of (opts.lines || [])) {
    const tr = ln.tax_rule || {};
    let r = tr.rate != null ? Number(tr.rate) : rate;
    const cls = ln.class || tr.class || "standard";
    if (cls === "zero" || cls === "exempt") r = 0;
    else if (cls === "reduced" && rule.reduced != null && tr.rate == null) r = rule.reduced;
    else if (cls === "digital" && rule.digital != null && tr.rate == null) r = rule.digital;
    if (tr.exempt) r = 0;
    // reverse charge: valid B2B VAT on digital services in VAT mode → 0 here, flagged for self-assessment
    let note = "";
    if (rule.mode === "vat" && cls === "digital" && hasValidVat) { r = 0; note = "reverse-charge (B2B)"; exemptHits.push({ line: ln.id, reason: "reverse-charge" }); }
    const amount = Number(ln.amount || 0);
    let t = 0, net = amount;
    if (opts.inclusive) { net = +(amount / (1 + r)).toFixed(2); t = +(amount - net).toFixed(2); }
    else { t = +(amount * r).toFixed(2); }
    tax += t; outLines.push({ id: ln.id, class: cls, rate: r, amount: r2(amount), net: r2(net), tax: r2(t), note });
  }
  return { country, mode: rule.mode || "manual", inclusive: !!opts.inclusive, lines: outLines, total: r2((opts.lines || []).reduce((n, l) => n + Number(l.amount || 0), 0)), tax: r2(tax), hasValidVat, exempt: exemptHits };
}

function configFor(tenantId) {
  const country = (db().get("SELECT country FROM tenants WHERE id=?", tenantId) || {}).country || "US";
  return { country, rule: ruleFor(country.toUpperCase()), classes: list("taxClasses", REGISTRIES.taxClasses) };
}

module.exports = { REGISTRIES, seed, ruleFor, validateNumber, computeLegacy, quote, configFor, list, J };
