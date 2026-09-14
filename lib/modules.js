/* LUXORA Platform - Capability Marketplace.
   EVERYTHING is a product: identity, gid, geo, billing, seo, recommendations, cart, listing,
   checkout, tax, offers, wallet, logistics, payment rails, catalog packs, themes.
   Modules are catalog rows with price + manifest; manifests declare capabilities/features/
   gateways/catalog actions; the platform auto-applies free baselines at provisioning ("purchase"). */
"use strict";

const { run, get, all } = require("./db.js");
const settings = require("./settings.js");

function J(v, d) { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } }

/* ---------- marketplace SEED (written to the `modules` table once; from then on the DB is the
   source of truth — add/edit/delete modules live in the platform console, no code changes) ---------- */
const MARKET = [
  /* free baselines — auto-installed ("purchased") when a store is provisioned */
  { id: "identity-basic", name: "Identity — Email & Password", category: "Identity", price: 0, capabilities: ["identity"], summary: "Account login, sessions, CSRF-bound identity." },
  { id: "gid-basic", name: "Global IDs", category: "Identity", price: 0, capabilities: ["gid"], summary: "Universal UUIDv4 on every entity, trigger-enforced." },
  { id: "geo-basic", name: "Geo & Currency", category: "Geo", price: 0, capabilities: ["geo"], summary: "Country, currency, locale, decimals, FX registry." },
  { id: "cart-basic", name: "Cart", category: "Commerce", price: 0, capabilities: ["cart"], summary: "Cart, coupons slot, save-for-later." },
  { id: "listing-basic", name: "Listing & Search", category: "Commerce", price: 0, capabilities: ["listing"], summary: "Faceted listing, sorting, pagination." },
  { id: "checkout-basic", name: "Checkout", category: "Commerce", price: 0, capabilities: ["checkout"], summary: "Address, carrier selection, tax, order snapshot." },
  { id: "seo-basic", name: "SEO Basics", category: "Growth", price: 0, capabilities: ["seo"], summary: "Titles, meta descriptions, per-product SEO data." },
  { id: "reco-basic", name: "Related Items", category: "Growth", price: 0, capabilities: ["reco"], summary: "Same-department related products." },
  { id: "billing-basic", name: "Store Billing", category: "Billing", price: 0, capabilities: ["billing"], summary: "Invoices ledger, plan & usage visibility." },
  /* paid premium modules — purchased on demand */
  { id: "wallet", name: "Customer Wallets", category: "Wallets", price: 19, capabilities: ["wallet"], summary: "Account-bound gift balance, auto-applied at checkout, merges on login." },
  { id: "offers-pro", name: "Offers Engine Pro", category: "Offers", price: 29, capabilities: ["offersPro"], summary: "BOGO and bundle-price promotions in the checkout engine." },
  { id: "tax-perline", name: "Per-Line Tax Engine", category: "Tax", price: 39, capabilities: ["taxPerLine"], summary: "Each product's tax_rule overrides the store rate, line by line." },
  { id: "logistics-guard", name: "Logistics Guard", category: "Logistics", price: 24, capabilities: ["logisticsGuard"], summary: "Cold-chain & hazmat surcharges enforced at checkout.", fields: [{ key: "coldFee", label: "Cold-chain fee (base)" }, { key: "hazmatFee", label: "Hazmat fee (base)" }] },
  { id: "seo-pro", name: "SEO Pro", category: "Growth", price: 15, capabilities: ["seoPro"], summary: "XML sitemap + robots endpoints per store." },
  { id: "reco-pro", name: "Recommendation Engine", category: "Growth", price: 34, capabilities: ["recoPro"], summary: "Co-purchase recommendations from real order data (customers-also-bought)." },
  { id: "listing-pro", name: "Listing Pro", category: "Commerce", price: 19, capabilities: ["listingPro"], summary: "Live facet aggregation API (counts by brand/category/price)." },
  { id: "geo-pro", name: "Multi-Currency Shopper", category: "Geo", price: 22, capabilities: ["geoPro"], summary: " shoppers browse prices in their own currency at live FX (settlement stays in store currency)." },
  { id: "identity-pro", name: "Identity Pro", category: "Identity", price: 12, capabilities: ["identityPro"], summary: "Login-required checkout policy for regulated goods.", fields: [{ key: "requireLoginCheckout", label: "Require login at checkout (true/false)" }] },
  { id: "billing-pro", name: "Billing Pro", category: "Billing", price: 9, capabilities: ["billingPro"], summary: "Self-service invoice payment through the store's own gateways." },
  { id: "ai-pro", name: "AI Premium", category: "Intelligence", price: 29, capabilities: ["aiPro"], summary: "Unlocks premium AI models (OpenAI/Anthropic/Stability/Google Vision) with higher limits — bring your own keys. Free built-in engine stays on for every store.", fields: [{ key: "defaultProvider", label: "Default premium provider id" }] },
  /* payment rail packs */
  { id: "pack-payments-us", name: "US Payments Pack", category: "Payments", price: 15, capabilities: ["gatewayPack"], gateways: ["stripe", "paypal", "bank"] },
  { id: "pack-payments-in", name: "India Payments Pack", category: "Payments", price: 15, capabilities: ["gatewayPack"], gateways: ["razorpay", "upi", "paytm"] },
  { id: "pack-payments-ae", name: "MENA Payments Pack", category: "Payments", price: 15, capabilities: ["gatewayPack"], gateways: ["tabby", "stripe"] },
  /* catalog packs — the product range itself is a purchasable module */
  { id: "catalog-grocery", name: "Grocery Catalog Pack", category: "Catalogs", price: 49, capabilities: ["catalogPack"], catalog: ["grocery"] },
  { id: "catalog-furniture", name: "Furniture Catalog Pack", category: "Catalogs", price: 49, capabilities: ["catalogPack"], catalog: ["furniture"] },
  { id: "catalog-jewellery", name: "Jewellery Catalog Pack", category: "Catalogs", price: 59, capabilities: ["catalogPack"], catalog: ["jewellery", "luxury"] },
  { id: "catalog-pharma", name: "Pharma Catalog Pack", category: "Catalogs", price: 69, capabilities: ["catalogPack"], catalog: ["pharma", "healthcare"] },
  { id: "catalog-fashion", name: "Fashion Catalog Pack", category: "Catalogs", price: 49, capabilities: ["catalogPack"], catalog: ["fashion", "retail"] },
  /* themes */
  { id: "theme-glass", name: "Glass Theme Kit", category: "Experience", price: 9, capabilities: ["theme"], features: { glassTheme: true } }
];

function seedMarket() {
  if (get("SELECT COUNT(*) c FROM modules").c > 0) return;
  MARKET.forEach((m, i) => run(`INSERT INTO modules(id,name,category,summary,price_type,price,currency,version,vendor,manifest,position)
    VALUES(?,?,?,?,?,?,?,?,?,?,?)`, m.id, m.name, m.category, m.summary || "", m.price > 0 ? "one_time" : "free",
    m.price || 0, "USD", "1.0", "LUXORA",
    JSON.stringify({ capabilities: m.capabilities || [], features: m.features || {}, gateways: m.gateways || [], catalog: m.catalog || [], fields: m.fields || [] }), i));
}
seedMarket();

/* ---------- state ---------- */
function moduleRow(id) { return get("SELECT * FROM modules WHERE id=?", id); }
function installedRow(tid, id) { return get("SELECT * FROM tenant_modules WHERE tenant_id=? AND module_id=?", tid, id); }
function installed(tid) {
  return all(`SELECT tm.module_id, tm.status, tm.config, tm.installed_at, m.name, m.category, m.price, m.manifest
    FROM tenant_modules tm JOIN modules m ON m.id=tm.module_id WHERE tm.tenant_id=? AND tm.status='installed' ORDER BY m.category, m.position`, tid)
    .map(r => ({ ...r, manifest: J(r.manifest, {}), config: J(r.config, {}) }));
}
function caps(tid) { const s = new Set(); installed(tid).forEach(m => (m.manifest.capabilities || []).forEach(c => s.add(c))); return s; }
function hasCap(tid, c) { return caps(tid).has(c); }
function moduleConfig(tid, id) { const r = installedRow(tid, id); return r ? J(r.config, {}) : {}; }

/* ---------- apply / unapply: the plug-and-play core ---------- */
function applyModule(tenantId, module, config) {
  const man = J(module.manifest, {});
  if (man.features && Object.keys(man.features).length) {
    const st = settings.load(tenantId);
    settings.save(tenantId, { features: { ...st.features, ...man.features } });
  }
  if (man.catalog && man.catalog.length) {
    const db = require("./db.js");
    const meta = require("./meta.js");
    man.catalog.forEach(k => {
      const ind = meta.INDUSTRIES.find(x => x.key === k);
      if (ind) run("INSERT OR IGNORE INTO departments(tenant_id,key,label,icon,position) VALUES(?,?,?,?,?)", tenantId, k, ind.name, ind.icon,
        get("SELECT COALESCE(MAX(position),0)+1 p FROM departments WHERE tenant_id=?", tenantId).p);
    });
    db.seedTaxonomy(tenantId, man.catalog);
    db.seedTenantDepartments(tenantId, man.catalog);
    db.seedTenantCatalog(tenantId, man.catalog);
  }
  if (man.gateways && man.gateways.length) {
    const t = get("SELECT country FROM tenants WHERE id=?", tenantId);
    const registry = require("./registry.js");
    const country = registry.country((t && t.country) || "US");
    man.gateways.filter(p => registry.supports(p, country.code)).forEach((p, i) =>
      run(`INSERT INTO tenant_gateways(tenant_id,provider_id,enabled,is_primary,mode,config,position) VALUES(?,?,1,?,'sandbox','{}',?)
           ON CONFLICT(tenant_id,provider_id) DO UPDATE SET enabled=1`, tenantId, p, i === 0 ? 1 : 0, i));
  }
  run(`INSERT INTO tenant_modules(tenant_id,module_id,status,config,installed_by) VALUES(?,?,'installed',?,?)
       ON CONFLICT(tenant_id,module_id) DO UPDATE SET status='installed', config=excluded.config`,
    tenantId, module.id, JSON.stringify(config || {}), (config && config.__by) || "");
  return { ok: true, id: module.id };
}
function unapplyModule(tenantId, module) {
  const man = J(module.manifest, {});
  if (man.features) { const st = settings.load(tenantId); const off = {}; for (const k of Object.keys(man.features)) off[k] = false; settings.save(tenantId, { features: { ...st.features, ...off } }); }
  if (man.gateways) for (const p of man.gateways) run("UPDATE tenant_gateways SET enabled=0 WHERE tenant_id=? AND provider_id=?", tenantId, p);
  run("UPDATE tenant_modules SET status='disabled' WHERE tenant_id=? AND module_id=?", tenantId, module.id);
  return { ok: true };
}

/* ---------- provisioning auto-purchase: every store gets all free baselines ---------- */
function ensureBaselines() {
  const tenants = all("SELECT id, slug FROM tenants");
  for (const t of tenants) {
    for (const m of all("SELECT * FROM modules WHERE price=0 AND status='active'")) {
      const row = get("SELECT status FROM tenant_modules WHERE tenant_id=? AND module_id=?", t.id, m.id);
      if (!row) run("INSERT INTO tenant_modules(tenant_id,module_id,status,config) VALUES(?,?,'installed','{}')", t.id, m.id);
      else if (row.status !== "installed") run("UPDATE tenant_modules SET status='installed' WHERE tenant_id=? AND module_id=?", t.id, m.id);
    }
  }
}

/* ---------- wallets (account-bound; the wallet capability owns this table) ---------- */
function ownerFor(s) { const t = s.tenant ? s.tenant.id : 1; return s.user_id ? `t${t}:u:${s.user_id}` : `t${t}:s:${s.sid}`; }
function walletBalance(tid, owner) { const r0 = get("SELECT balance b FROM wallets WHERE tenant_id=? AND owner=?", tid, owner); return r0 ? +r0.b : 0; }
function _journal(tid, owner, kind, delta) { const after = get("SELECT balance b FROM wallets WHERE tenant_id=? AND owner=?", tid, owner); try { run("INSERT INTO wallet_entries(tenant_id,owner,currency,kind,amount,balance_after,actor) VALUES(?,?,?,?,?,?,?)", tid, owner, "USD", kind, delta, after ? +after.b : 0, "wallet"); } catch (e) { } }
function walletAdd(tid, owner, amt) {
  run(`INSERT INTO wallets(tenant_id,owner,balance,updated_at) VALUES(?,?,?,datetime('now'))
       ON CONFLICT(tenant_id,owner) DO UPDATE SET balance=balance+excluded.balance, updated_at=datetime('now')`, tid, owner, amt);
  _journal(tid, owner, amt >= 0 ? "deposit" : "adjust", amt);
}
function walletSet(tid, owner, amt) { const before = walletBalance(tid, owner); run("INSERT INTO wallets(tenant_id,owner,balance) VALUES(?,?,?) ON CONFLICT(tenant_id,owner) DO UPDATE SET balance=excluded.balance", tid, owner, Math.max(0, +(amt || 0).toFixed(2))); _journal(tid, owner, amt < before ? "redeem" : "adjust", +(amt - before).toFixed(2)); }
function walletMerge(fromOwner, toOwner) {
  const a = get("SELECT tenant_id tid, balance b FROM wallets WHERE owner=?", fromOwner);
  if (!a || !a.b) return;
  walletAdd(a.tid, toOwner, a.b);
  run("DELETE FROM wallets WHERE owner=?", fromOwner);
}

module.exports = { MARKET, seedMarket, ensureBaselines, moduleRow, installed, installedRow, caps, hasCap, moduleConfig, applyModule, unapplyModule, walletBalance, walletAdd, walletSet, walletMerge, ownerFor, J };
