/* LUXORA Platform - per-tenant settings engine (DB-backed, env-overridable, deep-merged) */
"use strict";

const { all, run } = require("./db.js");
let _adapters = null, _config = null;
const cacheAd = () => { if (!_adapters) { _adapters = require("./adapters.js"); _config = require("./config.js"); } if (!cacheAd._i) cacheAd._i = _adapters.build("cache", _config.get("cache")); return cacheAd._i; };

const DEFAULTS = {
  brand: {
    name: "LUXORA",
    wordmark: "LUXORA",
    logo: "",
    tagline: "Curated commerce, delivered beautifully.",
    supportEmail: "care@luxora.shop",
    poweredBy: "Powered by LUXORA Platform",
    footerNote: "© {year} {brand} — a premium demo storefront. Independent project, not affiliated with any retailer."
  },
  theme: {
    bg: "#F4F1EA", surface: "#FFFFFF", ink: "#16181D", muted: "#6E6A61", line: "#E8E2D6",
    header: "#0C0E13", headerText: "#F4F1EA", headerMuted: "#9A958A",
    accent: "#C6A15B", accentDeep: "#9E7A33", accentSoft: "#F5EBD6",
    price: "#16181D", deal: "#B3261E", success: "#1E7A45", star: "#C9A227",
    link: "#8A6D3B", linkHover: "#B08A4A",
    radius: "18px", radiusBtn: "999px",
    fontDisplay: '"Didot","Bodoni MT","Playfair Display",Georgia,"Times New Roman",serif',
    fontBody: '"Inter","Helvetica Neue","Segoe UI",Arial,sans-serif',
    customCSS: ""
  },
  commerce: {
    country: null, currency: null, symbol: null, locale: null, decimals: null,
    taxMode: null, taxRate: null, freeShipThreshold: 35, shipFee: 5.99,
    daysPriority: 2, daysStandard: 5,
    /* "fixed" charges the flat fee / the carrier's base fee; "live" asks the connected carrier
       account for a rate from shipFrom to the shopper. A product with no weight of its own
       ships as parcelWeightKg per item. */
    shipRates: "fixed", parcelWeightKg: 0.5,
    perPage: 16, cartMaxQty: 10,
    giftAmounts: [10, 15, 20, 25, 50, 100, 200, 250, 500, 1000, 2000], giftMax: 2000
  },
  features: {
    reviews: true, deals: true, giftCards: true, registry: true, customerService: true,
    saveForLater: true, countdown: true, suggestions: true, buyNow: true, adminPortal: true, coupons: true, fiscalSelection: false,
    qna: true, subscribeSave: true, membership: true, fraudScreen: true, experiments: true, planning: true
  },
  ugc: { moderation: false, reviewMedia: true, reviewReplies: true },
  ai: {
    enabled: true, tier: "auto",
    product_recommendation: { enabled: true, premium: false },
    image_processing: { enabled: true, premium: false },
    data_analysis: { enabled: true, premium: false },
    data_cleaning: { enabled: true, premium: false },
    reporting: { enabled: true, premium: false }
  },
  offers: {
    enabled: true, stackMax: 5, allowGlobal: true,
    couponCodePrefix: "", walletEnabled: true
  },
  copy: {
    searchPlaceholder: "Search the collection",
    deliverTo: "Ship to",
    addToCart: "Add to cart",
    buyNow: "Buy Now",
    priorityBadge: "PRIORITY",
    priorityPerk: "Complimentary 2-day delivery on thousands of pieces",
    emptyCart: "Your {brand} bag is empty",
    emptyCartHint: "Curated picks are waiting — explore today's edit.",
    signIn: "Sign in",
    accountLists: "Account & Lists",
    yourOrders: "Your Orders",
    backToTop: "Back to top",
    proceedCheckout: "Proceed to checkout",
    placeOrder: "Place your order",
    orderPlaced: "Order placed, thank you",
    freeShipQualify: "Your order qualifies for complimentary delivery",
    freeShipGap: "Add {gap} more to unlock complimentary delivery",
    seeMore: "Explore",
    bestSellers: "House Favourites",
    topRated: "Highest Rated",
    newArrivals: "New This Season",
    dealsTitle: "The Edit — Limited Offers",
    relatedTitle: "You May Also Admire",
    fbtTitle: "Completes the Look",
    reviewsTitle: "Owner Reviews",
    qnaTitle: "Customer Questions & Answers",
    writeReview: "Write a review",
    aboutItem: "Details & Craft",
    inStock: "In stock",
    lowStock: "Only {n} left — reserve soon",
    outOfStock: "Sold out",
    deliverEstimate: "Estimated arrival",
    giftBalanceLabel: "Your gift balance",
    couponPlaceholder: "Promo code",
    couponApply: "Apply",
    couponApplied: "✓ Promo applied to your bag",
    couponInvalid: "That code did not work"
  }
};

function isObj(v) { return v && typeof v === "object" && !Array.isArray(v); }
function deepMerge(base, over) {
  if (!isObj(base) || !isObj(over)) return over === undefined ? base : over;
  const out = { ...base };
  for (const k of Object.keys(over)) out[k] = isObj(over[k]) ? deepMerge(base[k], over[k]) : over[k];
  return out;
}
/* FEATURES ARE CAPABILITIES. The `features` block below is the historical default
   and the shape the console renders, but the LIVE value is the tenant's capability
   composition: each settings.features.<key> is answered by the storefront atom of
   the same idea. `featuresOf` merges the atom answer over the settings answer, so a
   feature is switched in exactly one place — Capabilities — and every reader
   (storefront, cart, checkout, console) sees the same bit. The settings row is
   preserved for the migration and for any key not yet an atom. */
function featuresOf(tenantId, base) {
  const out = { ...(base || {}) };
  try {
    const caps = require("./capabilities.js");
    for (const key of caps.STOREFRONT_KEYS) {
      /* the settings contract is camelCase (giftCards, fiscalSelection…), the atom
         keys are snake_case — translate so every existing reader keeps working */
      const camel = key.replace(/_([a-z])/g, (_, c) => c.toUpperCase());
      /* the platform alone: this result is cached for every buyer (buyer-scoped rules are
         applied per request by forBuyer below) */
      if (caps.on(tenantId, key, { buyer: false })) out[camel] = true;
      else out[camel] = false;
    }
  } catch (e) { /* a cold boot before the catalog seeds answers the settings default */ }
  return out;
}
function envOverrides() {
  const o = {};
  if (process.env.BRAND_NAME) o.brand = { name: process.env.BRAND_NAME };
  if (process.env.CURRENCY_SYMBOL) o.commerce = { symbol: process.env.CURRENCY_SYMBOL };
  if (process.env.TAX_RATE) o.commerce = { ...(o.commerce || {}), taxRate: Number(process.env.TAX_RATE) };
  return o;
}
function load(tenantId) {
  const key = tenantId || 1; const C = cacheAd();
  if (C.has(key)) return C.get(key);
  let saved = {};
  try {
    for (const row of all("SELECT key, value FROM settings WHERE tenant_id=?", key)) {
      try { saved[row.key] = JSON.parse(row.value); } catch (e) { }
    }
  } catch (e) { }
  const merged = deepMerge(deepMerge(DEFAULTS, saved), envOverrides());
  /* a store's country is its tenant row's (set at registration), then platform policy —
     never a literal here, so resetting settings cannot move a store to another country */
  if (!merged.commerce.country) {
    let tc = null; try { tc = (require("./db.js").get("SELECT country FROM tenants WHERE id=?", key) || {}).country; } catch (e) { }
    /* a copy: with nothing saved, merged.commerce IS the shared DEFAULTS object */
    merged.commerce = { ...merged.commerce, country: String(tc || require("./security.js").defaultCountry()).toUpperCase() };
  }
  merged.features = featuresOf(key, merged.features);
  C.set(key, merged);
  return merged;
}
function save(tenantId, partial) {
  for (const [k, v] of Object.entries(partial)) {
    if (!(k in DEFAULTS)) continue;
    run("INSERT INTO settings(tenant_id,key,value) VALUES(?,?,?) ON CONFLICT(tenant_id,key) DO UPDATE SET value=excluded.value",
      tenantId, k, JSON.stringify(v));
  }
  cacheAd().delete(tenantId); cacheAd().delete(tenantId || 1);
}
/* reset restores the commerce defaults only — it used to wipe every key, including the store's
   identity/login policy */
function reset(tenantId) { const keys = Object.keys(DEFAULTS); run("DELETE FROM settings WHERE tenant_id=? AND key IN (" + keys.map(() => "?").join(",") + ")", tenantId, ...keys); cacheAd().delete(tenantId); cacheAd().delete(tenantId || 1); }
/* a capability switch changes the derived `features` block, so the settings cache
   must not serve a pre-switch snapshot. Called by capabilities.enable/disable —
   it cannot require us (we require it), so this is the one direction that compiles.
   A falsy tenantId means "every tenant" (a platform-level switch). */
function bust(tenantId) {
  const C = cacheAd();
  if (!tenantId) { for (const t of all("SELECT id FROM tenants")) C.delete(t.id); C.delete(1); return; }
  C.delete(Number(tenantId)); C.delete(tenantId || 1);
}
/* the cached settings, with the storefront features a buyer-scoped applicability rule turns
   off for THIS request's buyer — the cache itself is never written with a buyer's answer */
function forBuyer(tenantId) {
  const base = load(tenantId);
  let rules; try { rules = require("./rules.js"); } catch (e) { return base; }
  const st = rules.current();
  if (!st || st.staff || !rules.contextualAt("capability.on")) return base;
  st.cfg = st.cfg || {};
  if (st.cfg[tenantId]) return st.cfg[tenantId];
  const caps = require("./capabilities.js");
  const features = { ...base.features };
  for (const key of caps.STOREFRONT_KEYS) {
    const camel = key.replace(/_([a-z])/g, (_, c) => c.toUpperCase());
    if (features[camel] && !caps.on(tenantId, key)) features[camel] = false;
  }
  return (st.cfg[tenantId] = { ...base, features });
}
function get(tenantId, path) {
  return path.split(".").reduce((o, k) => (o == null ? undefined : o[k]), load(tenantId));
}

module.exports = { DEFAULTS, load, forBuyer, save, reset, get, deepMerge, featuresOf, bust };
