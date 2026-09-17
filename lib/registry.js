/* LUXORA Platform - runtime registry: geo (countries/currencies), tax modes, provider catalog,
   availability relationships and list registries. All stored in DB tables (seeded once from
   providers.js/meta.js constants) and editable at runtime via the entity engine. */
"use strict";

/* db functions resolved lazily via require() to avoid circular-import partial exports */
const { all, get, run } = (() => {
  let target = null;
  const lazy = {};
  for (const fn of ["all", "get", "run", "exec"]) lazy[fn] = (...a) => (target || (target = require("./db.js")))[fn](...a);
  return lazy;
})();
const providers = require("./providers.js");
const meta = require("./meta.js");

function J(v, d) { try { return JSON.parse(v == null || v === "" ? (d || "{}") : v); } catch (e) { return d || {}; } }

/* ---------- bootstrap seeding (idempotent) ---------- */
function seedRegistries() {
  if (get("SELECT COUNT(*) c FROM countries").c === 0) {
    let i = 0;
    for (const [code, c] of Object.entries(providers.COUNTRIES)) {
      run("INSERT INTO countries(code,name,currency,symbol,locale,decimals,tax_mode,tax_rate,position) VALUES(?,?,?,?,?,?,?,?,?)",
        code, c.name, c.currency, c.symbol, c.locale, c.currency === "JPY" ? 0 : 2, c.tax.mode, c.tax.rate, i++);
    }
  }
  if (get("SELECT COUNT(*) c FROM currencies").c === 0) {
    const known = new Set();
    providers.CURRENCIES.forEach((cur, i) => { run("INSERT INTO currencies(code,name,symbol,decimals,usd,position) VALUES(?,?,?,?,?,?)", cur.code, cur.name, cur.symbol, cur.decimals, cur.usd, i); known.add(cur.code); });
    all("SELECT DISTINCT currency, symbol, decimals FROM countries").forEach((c, i) => {
      if (known.has(c.currency)) return;
      run("INSERT OR IGNORE INTO currencies(code,name,symbol,decimals,usd,position) VALUES(?,?,?,?,?,?)", c.currency, c.currency, c.symbol, c.decimals, 1, 100 + i);
    });
    if (get("SELECT COUNT(*) c FROM fx_rates").c === 0)
      all("SELECT code, usd FROM currencies").forEach(c => run("INSERT INTO fx_rates(currency,usd,source,note) VALUES(?,?,?,?)", c.code, c.usd, "seed", "initial registry"));
  }
  if (get("SELECT COUNT(*) c FROM tax_modes").c === 0) {
    providers.TAX_PROVIDERS.forEach((t, i) => run("INSERT INTO tax_modes(key,label,description,fields,position) VALUES(?,?,?,?,?)",
      t.id, t.name, t.desc || "", JSON.stringify(t.fields || []), i));
  }
  if (get("SELECT COUNT(*) c FROM provider_defs").c === 0) {
    const put = (kind, list) => list.forEach((p, i) => run(
      "INSERT INTO provider_defs(id,kind,name,emoji,description,methods,fee_pct,fee_fixed,fields,base_fee,eta_min,eta_max,position) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
      p.id, kind, p.name, p.emoji || "🔌", p.desc || "", JSON.stringify(p.methods || []), Number(p.feePct) || 0, Number(p.feeFixed) || 0,
      JSON.stringify(p.fields || []), Number(p.baseFee) || 0, p.eta ? p.eta[0] : null, p.eta ? p.eta[1] : null, i));
    put("payment", providers.PAYMENT_PROVIDERS);
    put("shipping", providers.SHIPPING_PROVIDERS);
    put("notification", providers.NOTIFICATION_PROVIDERS);
  }
  /* specs are DATA (fill-in-the-blanks): attach declarative request specs to every provider, and
     register marketing providers (Meta/Google/GA4/TikTok). Idempotent + self-heals on upgrade. */
  for (const key of Object.keys(providers.PROVIDER_SPECS)) {
    const [kind, id] = key.split(":"); if (!id) continue;
    run("INSERT INTO provider_defs(id,kind,name,emoji,description,methods,fields,spec,enabled,position) VALUES(?,?,?,?,?,'[]','[]',?,1,999) ON CONFLICT(id,kind) DO UPDATE SET spec=excluded.spec", id, kind, id, "🔌", kind, JSON.stringify(providers.PROVIDER_SPECS[key]));
  }
  for (const m of providers.MARKETING_PROVIDERS) {
    run("INSERT INTO provider_defs(id,kind,name,emoji,description,methods,fields,spec,enabled,position) VALUES(?,?,?,?,?,'[]',?,?,1,?) ON CONFLICT(id,kind) DO UPDATE SET name=excluded.name, description=excluded.description, fields=excluded.fields, spec=excluded.spec",
      m.id, "marketing", m.name, m.emoji, m.desc || "", JSON.stringify(m.fields || []), JSON.stringify(providers.PROVIDER_SPECS["marketing:" + m.id] || {}), m.id.length);
  }
  if (get("SELECT COUNT(*) c FROM provider_availability").c === 0) {
    /* backfill: any country code referenced by a provider must exist as an entity row */
    const missing = new Set();
    for (const p of providers.PAYMENT_PROVIDERS.concat(providers.SHIPPING_PROVIDERS, providers.NOTIFICATION_PROVIDERS, providers.MARKETING_PROVIDERS))
      p.countries.forEach(c => { if (c !== "*" && !get("SELECT 1 ok FROM countries WHERE code=?", c)) missing.add(c); });
    [...missing].forEach((c, i) => run("INSERT INTO countries(code,name,currency,symbol,locale,decimals,tax_mode,tax_rate,position) VALUES(?,?,?,?,?,?,?,?,?)",
      c, c + " (auto-registered)", c, c + " ", "en-" + c, 2, "manual", 0, 100 + i));
    const link = (pid, countries) => countries.forEach(cc => run("INSERT OR IGNORE INTO provider_availability(provider_id,country_code) VALUES(?,?)", pid, cc));
    providers.PAYMENT_PROVIDERS.concat(providers.SHIPPING_PROVIDERS, providers.NOTIFICATION_PROVIDERS, providers.MARKETING_PROVIDERS).forEach(p => {
      if (p.countries.includes("*")) all("SELECT code FROM countries").forEach(c => link(p.id, [c.code]));
      else link(p.id, p.countries);
    });
  }
  {
    const verticalFields = {}; const verticalTypes = { tax: [], invoice: [], payment: [] };
    for (const [vk, v] of Object.entries(meta.VERTICALS)) verticalFields[vk] = v.fields;
    for (const [gk, items] of Object.entries(meta.VERTICAL_CONTEXTS)) for (const it of items) (verticalTypes[gk] = verticalTypes[gk] || []).push({ ...it, group: gk });
    const lists = {
      industries: meta.INDUSTRIES, productTypes: meta.PRODUCT_TYPES, lifecycle: meta.LIFECYCLE, lifecycleTransitions: meta.LIFECYCLE_TRANSITIONS,
      relTypes: meta.REL_TYPES, mediaKinds: meta.MEDIA_KINDS, packagingLevels: meta.PACKAGING_LEVELS,
      uomUnits: meta.UOM_UNITS, uomConversions: meta.UOM_CONVERSIONS, sellerRoles: meta.SELLER_ROLES,
      promoTypes: meta.PROMO_TYPES, identityFields: meta.IDENTITY_FIELDS, shippingClasses: meta.SHIPPING_CLASSES,
      serializedStatuses: meta.SERIALIZED_STATUSES, serializedConditions: meta.SERIALIZED_CONDITIONS, variantAxes: meta.VARIANT_AXES,
      complianceScopes: meta.COMPLIANCE_SCOPES, complianceKinds: meta.COMPLIANCE_KINDS, complianceStatuses: meta.COMPLIANCE_STATUSES,
      supplierRoles: meta.SUPPLIER_ROLES, supplierStatuses: meta.SUPPLIER_STATUSES, paymentTerms: meta.PAYMENT_TERMS, incoterms: meta.INCOTERMS,
      localizationEntities: meta.LOCALIZATION_ENTITIES, contractStatuses: meta.CONTRACT_STATUSES, tenderStatuses: meta.TENDER_STATUSES, linkStatuses: meta.LINK_STATUSES,
      verticals: meta.VERTICALS, industryVertical: meta.INDUSTRY_VERTICAL, deployModes: meta.DEPLOY_MODES,
      verticalFields, verticalTypes, verticalContexts: meta.VERTICAL_CONTEXTS, verticalTypeOf: meta.VERTICAL_TYPE_OF,
      /* Search & Discovery: registry-driven synonyms + boost rules (editable in Data Studio) */
      searchSynonyms: { tv: ["television", "smart tv", "display"], laptop: ["laptop computer", "notebook"], sofa: ["couch", "settee"], airpods: ["earbuds", "headphones"], gold: ["22k gold", "916", "hallmarked"], drill: ["power drill", "impact driver"], wine: ["vintage wine", "red wine"] },
      searchBoosts: [{ id: "LX-ELS-007", reason: "flagship", weight: 0.5 }, { id: "VR-JEW-01", reason: "high-margin", weight: 0.3 }]
    };
    for (const [k, v] of Object.entries(lists)) if (v !== undefined) run("INSERT OR IGNORE INTO meta_lists(name,label,items) VALUES(?,?,?)", k, k, JSON.stringify(v));
  }
  /* AI product layer: idempotent provider/capability/plan seeding (runs on every boot, safe on upgrade) */
  try { require("./ai.js").seed(); } catch (e) { console.error("ai seed failed:", e.message); }
  /* Central offers/coupons/wallet registries (data-driven, self-heal on upgrade) */
  try { require("./offers.js").seed(); } catch (e) { console.error("offers seed failed:", e.message); }
  try { require("./goip.js").seed(); } catch (e) { console.error("goip seed failed:", e.message); }
  /* Tax engine registries */
  try { require("./tax.js").seed(); } catch (e) { console.error("tax seed failed:", e.message); }
  try { require("./logistics.js").seed(); } catch (e) { console.error("logistics seed failed:", e.message); }
  try { require("./fin.js").seed(); } catch (e) { console.error("fin seed failed:", e.message); }
  try { require("./marketplace.js").seed(); } catch (e) { console.error("marketplace seed failed:", e.message); }
  /* Event catalog (webhook event types) */
  try { require("./events.js").seed(); } catch (e) { console.error("events seed failed:", e.message); }
  /* RBAC staff roles */
  try { require("./rbac.js").seed(); } catch (e) { console.error("rbac seed failed:", e.message); }
}

/* ---------- read API (DB is source of truth) ---------- */
function list(name) {
  const r = get("SELECT items FROM meta_lists WHERE name=?", name);
  return r ? J(r.items, name.includes("ical") || name === "lifecycleTransitions" || name === "uomConversions" || name === "industryVertical" || name === "verticals" || name === "verticalFields" ? {} : []) : [];
}
function countries() { return all("SELECT * FROM countries ORDER BY position"); }
function country(code) { return get("SELECT * FROM countries WHERE code=?", code) || get("SELECT * FROM countries ORDER BY position LIMIT 1"); }
function currencies() { return all("SELECT * FROM currencies WHERE active=1 ORDER BY position"); }
function currency(code) { return get("SELECT * FROM currencies WHERE code=?", String(code || "").toUpperCase()); }
function fxTo(base, target) { const b = currency(base), t = currency(target); if (!b || !t || !t.usd) return 1; return +(b.usd / t.usd).toFixed(6); }
function taxModes() { return all("SELECT * FROM tax_modes ORDER BY position").map(t => ({ ...t, fields: J(t.fields, []) })); }
function providerDefs(kind) {
  const rows = kind ? all("SELECT * FROM provider_defs WHERE kind=? AND enabled=1 ORDER BY position", kind)
    : all("SELECT * FROM provider_defs WHERE enabled=1 ORDER BY kind, position");
  return rows.map(p => ({ id: p.id, name: p.name, emoji: p.emoji, desc: p.description, methods: J(p.methods, []), feePct: p.fee_pct, feeFixed: p.fee_fixed, fields: J(p.fields, []), baseFee: p.base_fee || undefined, eta: p.eta_min != null ? [p.eta_min, p.eta_max] : undefined }));
}
function providersFor(kind, countryCode) {
  return all(`SELECT pd.* FROM provider_availability pa JOIN provider_defs pd ON pd.id=pa.provider_id
              WHERE pa.country_code=? AND pd.kind=? AND pd.enabled=1 ORDER BY pd.position`, countryCode, kind)
    .map(p => ({ id: p.id, name: p.name, emoji: p.emoji, desc: p.description, methods: J(p.methods, []), feePct: p.fee_pct, feeFixed: p.fee_fixed, fields: J(p.fields, []), baseFee: p.base_fee || undefined, eta: p.eta_min != null ? [p.eta_min, p.eta_max] : undefined }));
}
function countryProfile(code) {
  const c = country(code);
  if (!c) return null;
  return {
    code: c.code, name: c.name, currency: c.currency, symbol: c.symbol, locale: c.locale, decimals: c.decimals,
    tax: { mode: c.tax_mode, rate: c.tax_rate },
    payments: providersFor("payment", c.code), shipping: providersFor("shipping", c.code),
    notifications: providersFor("notification", c.code)
  };
}
function supports(providerId, countryCode) {
  return !!get("SELECT 1 ok FROM provider_availability WHERE provider_id=? AND country_code=?", providerId, countryCode);
}

module.exports = { seedRegistries, list, countries, country, currencies, currency, fxTo, taxModes, providerDefs, providersFor, countryProfile, supports, J };
