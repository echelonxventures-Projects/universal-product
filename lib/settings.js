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
    country: "US", currency: null, symbol: null, locale: null, decimals: null,
    taxMode: null, taxRate: null, freeShipThreshold: 35, shipFee: 5.99,
    daysPriority: 2, daysStandard: 5,
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
function reset(tenantId) { run("DELETE FROM settings WHERE tenant_id=?", tenantId); cacheAd().delete(tenantId); cacheAd().delete(tenantId || 1); }
function get(tenantId, path) {
  return path.split(".").reduce((o, k) => (o == null ? undefined : o[k]), load(tenantId));
}

module.exports = { DEFAULTS, load, save, reset, get, deepMerge };
