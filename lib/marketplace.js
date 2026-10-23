/* LUXORA Platform — Marketplace & Seller ecosystem.
   Ad inventory (CPC / CPM / CPA), a simple Generalized-Second-Price ranker, impression/click ledger
   with last-click and decayed attribution, a seller KPI dashboard (orders, take-rate, ad ROI),
   and take-rate settlement hooks into the fin/billing ledgers. All configuration lives in
   meta_lists so new bid models, attribution models, or ad surfaces are added from Data Studio. */
"use strict";

const db = () => require("./db.js");
const bidModel = key => { const l = require("./registry.js").list("mktBidModels"); const rows = Array.isArray(l) && l.length ? l : BID_MODELS; return rows.find(r => r && r.key === String(key)) || {}; };
const defaultBidModel = () => { const l = require("./registry.js").list("mktBidModels"); const rows = Array.isArray(l) && l.length ? l : BID_MODELS; return ((rows.find(r => r && r.default) || rows[0]) || {}).key; };
/* orders are a state machine (lib/states.js): the statuses that count are a tag */
const states = require("./states.js");
const stIn = (machine, tag) => { const xs = states.tagged(machine, tag); return { sql: "(" + (xs.length ? xs.map(() => "?").join(",") : "NULL") + ")", args: xs }; };
const fin = () => require("./fin.js");
const caps = () => require("./capabilities.js");
const offers = () => require("./offers.js");
const billing = () => require("./billing.js");
const J = (v, d) => { try { return v == null || v === "" ? (d == null ? [] : d) : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d == null ? [] : d; } };

/* how a bid model charges is declared on its row: the ad event it `charges_on`, the unit it
   is priced `per` (a CPM bid is per thousand impressions) and its ranking `basis` — so a new
   model (cost per view, per add-to-cart…) is one registry row */
const BID_MODELS = [
  { key: "cpc", name: "cpc", charges_on: "click", per: 1, basis: "action", default: true },
  { key: "cpm", name: "cpm", charges_on: "impression", per: 1000, basis: "impression" },
  { key: "cpa", name: "cpa", charges_on: "conversion", per: 1, basis: "action" }
];
const ATTR_MODELS = ["last_click", "first_click", "linear", "time_decay"];
const AD_SURFACES = ["search", "product_detail", "home", "category", "post_purchase", "email"];

function seed() {
  const D = db();
  const put = (name, label, items) => {
    const existing = D.get("SELECT items FROM meta_lists WHERE name=?", name);
    const cur = J(existing ? existing.items : "[]", []);
    for (const it of items) if (!cur.some(x => (x.key || x) === (it.key || it))) cur.push(it);
    if (existing) D.run("UPDATE meta_lists SET items=? WHERE name=?", JSON.stringify(cur), name);
    else D.run("INSERT INTO meta_lists(name,label,items) VALUES(?,?,?)", name, label, JSON.stringify(cur));
  };
  put("mktBidModels", "Marketplace · Bid models", BID_MODELS);
  require("./registry.js").addFields("mktBidModels", BID_MODELS, ["charges_on", "per", "basis", "default"]);
  put("mktAttribution", "Marketplace · Attribution models", ATTR_MODELS.map(k => ({ key: k, name: k })));
  put("mktSurfaces", "Marketplace · Ad surfaces", AD_SURFACES.map(k => ({ key: k, name: k })));
}

/* ---------- ad CRUD ---------- */
function createAd(tenantId, input) {
  const D = db();
  const r = D.run("INSERT INTO ads(tenant_id,seller_id,name,status,bid_model,bid_amount,budget,target,start_at,end_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
    tenantId, Number(input.seller_id) || null, String(input.name || "Ad"), String(input.status || states.initial("ad")),
    String(input.bid_model || defaultBidModel()), Number(input.bid_amount) || 0, Number(input.budget) || 0,
    JSON.stringify(input.target || {}), input.start_at || null, input.end_at || null);
  return D.get("SELECT * FROM ads WHERE id=?", r.lastInsertRowid);
}

function listAds(tenantId, f) {
  const D = db(); f = f || {};
  let sql = "SELECT * FROM ads WHERE tenant_id=?", a = [tenantId];
  if (f.status) { sql += " AND status=?"; a.push(f.status); }
  if (f.seller_id) { sql += " AND seller_id=?"; a.push(Number(f.seller_id)); }
  sql += " ORDER BY id DESC LIMIT 200";
  return D.all(sql, ...a);
}

/* ---------- impression / click ledger ---------- */
function recordEvent(tenantId, adId, kind, ref) {
  const D = db();
  const ad = D.get("SELECT * FROM ads WHERE id=? AND tenant_id=?", adId, tenantId);
  if (!ad) throw new Error("Unknown ad " + adId);
  /* the event costs the bid when it is the one the ad's bid model charges on */
  const bm = bidModel(ad.bid_model);
  const cost = bm.charges_on === kind ? (Number(ad.bid_amount) || 0) / (Number(bm.per) || 1) : 0;
  D.run("INSERT INTO ad_events(tenant_id,ad_id,kind,ref,cost) VALUES(?,?,?,?,?)", tenantId, adId, kind, String(ref || ""), cost);
  if (cost) D.run("UPDATE ads SET spent=spent+? WHERE id=? AND tenant_id=?", cost, adId, tenantId);
  return D.get("SELECT * FROM ad_events WHERE id=?", D.get("SELECT MAX(id) m FROM ad_events WHERE ad_id=? AND tenant_id=?", adId, tenantId).m).id;
}

/* ---------- GSP ranker (position-bidding) ---------- */
/* the auction's tuning is the sponsored_ads capability's params; a store that has not switched
   the capability on still ranks (the console's preview) with the catalog's own defaults */
function adParams(tenantId) {
  const P = caps().cap(tenantId, "sponsored_ads");
  if (Object.keys(P).length) return P;
  const row = caps().catalogRow("sponsored_ads");
  return Object.fromEntries(Object.entries((row && row.params) || {}).map(([k, p]) => [k, p && p.default]));
}
const sqlNow = () => new Date().toISOString().slice(0, 19).replace("T", " ");
const sqlTime = v => String(v || "").replace("T", " ").slice(0, 19);
/* may this ad serve here, now? surface, schedule, budget, reserve price and keywords */
function eligible(a, surface, P, q) {
  const t = J(a.target, {});
  if (t.surface && surface && t.surface !== surface) return false;
  if (P.enforce_schedule) {
    const now = sqlNow();
    if (a.start_at && sqlTime(a.start_at) > now) return false;
    if (a.end_at && sqlTime(a.end_at) < now) return false;
  }
  if (P.enforce_budget && Number(a.budget) > 0 && Number(a.spent) >= Number(a.budget)) return false;
  if (Number(a.bid_amount || 0) < Number(P.reserve_price || 0)) return false;
  /* a keyword-targeted ad answers only searches that name one of its keywords */
  const kws = Array.isArray(t.keywords) ? t.keywords.map(k => String(k).toLowerCase().trim()).filter(Boolean) : [];
  if (q != null && kws.length) {
    const ql = " " + String(q).toLowerCase().replace(/\s+/g, " ").trim() + " ";
    if (!kws.some(k => ql.includes(" " + k + " ") || ql.includes(" " + k))) return false;
  }
  return true;
}
function rankAds(tenantId, surface, slots, opts) {
  const D = db();
  const o = opts || {};
  const P = adParams(tenantId);
  const sv = states.tagged("ad", "serving");
  const active = D.all("SELECT * FROM ads WHERE tenant_id=? AND status IN (" + (sv.map(() => "?").join(",") || "NULL") + ")", tenantId, ...sv)
    .filter(a => eligible(a, surface, P, o.q));
  /* predicted click rate: a baseline, lifted by the ad's past spend up to a cap */
  const pctr = a => Number(P.pctr_baseline) + Math.min(Number(P.pctr_spend_lift), (a.spent || 0) / (Number(P.spend_divisor) || 1));
  const scored = active.map(a => {
    const value = Number(a.bid_amount || 0) / (Number(bidModel(a.bid_model).per) || 1);
    return { ad: a, score: value * pctr(a), pctr: pctr(a) };
  }).sort((x, y) => y.score - x.score);
  const n = Math.max(1, Number(slots) || Number(P.slots) || 1);
  const out = [];
  scored.slice(0, n).forEach((s, i) => {
    // GSP: pay the next bidder's price
    const next = scored[i + 1] ? scored[i + 1].score : s.score * Number(P.runner_up_factor);
    const bm = bidModel(s.ad.bid_model);
    const charge = bm.basis === "impression" ? next * (Number(bm.per) || 1) : next / Math.max(0.001, s.pctr);
    out.push({ position: i + 1, ad: s.ad.id, name: s.ad.name, seller: s.ad.seller_id, model: s.ad.bid_model, charge: +Math.min(charge, Number(s.ad.bid_amount || 0)).toFixed(4) });
  });
  return out;
}
/* what a shopper sees: the auction's winners that advertise a product still on sale, each
   served once — recording the impression the capability names (charged under per-thousand
   bidding), at most once per viewer, ad and day */
function sponsored(tenantId, surface, opts) {
  const o = opts || {};
  const P = caps().cap(tenantId, "sponsored_ads");
  if (!Object.keys(P).length) return { label: null, items: [] };
  const D = db();
  const ranked = rankAds(tenantId, surface, Number(o.slots) || Number(P.slots), { q: o.q == null ? "" : o.q });
  const items = [];
  for (const r of ranked) {
    const ad = D.get("SELECT * FROM ads WHERE id=? AND tenant_id=?", r.ad, tenantId);
    const t = J(ad && ad.target, {});
    const p = t.product_id ? D.get("SELECT * FROM products WHERE tenant_id=? AND id=? AND lifecycle='published' AND deleted_at IS NULL AND stock>0", tenantId, String(t.product_id)) : null;
    if (!p || (o.exclude && o.exclude.includes(p.id))) continue;
    if (P.record_impressions && P.impression_event && o.viewer) {
      const ref = String(o.viewer) + ":" + sqlNow().slice(0, 10);
      if (!D.get("SELECT id FROM ad_events WHERE tenant_id=? AND ad_id=? AND kind=? AND ref=?", tenantId, ad.id, String(P.impression_event), ref)) recordEvent(tenantId, ad.id, String(P.impression_event), ref);
    }
    items.push({ ad: ad.id, position: r.position, product: p });
  }
  return { label: P.label || null, items };
}

/* ---------- attribution ---------- */
function attribute(tenantId, orderId, revenue, model) {
  const D = db();
  const m = String(model || require("./defaults.js").of("mktAttribution"));
  const click = D.get("SELECT ae.ad_id, a.seller_id FROM ad_events ae JOIN ads a ON a.id=ae.ad_id WHERE ae.tenant_id=? AND ae.kind='click' AND ae.ref LIKE ? ORDER BY ae.id DESC LIMIT 1", tenantId, "%" + orderId + "%");
  if (!click) return null;
  const ad = D.get("SELECT * FROM ads WHERE id=?", click.ad_id);
  const takeRate = Number((ad && ad.bid_amount) || 0.05) || 0.05;
  const commission = +(Number(revenue || 0) * takeRate).toFixed(2);
  D.run("INSERT INTO attribution(tenant_id,order_id,ad_id,seller_id,model,revenue,commission) VALUES(?,?,?,?,?,?,?)",
    tenantId, orderId, click.ad_id, click.seller_id, m, revenue, commission);
  return D.get("SELECT * FROM attribution WHERE order_id=? AND tenant_id=? AND ad_id=?", orderId, tenantId, click.ad_id);
}

/* ---------- seller KPIs ---------- */
function sellerMetrics(tenantId, sellerId, period) {
  const D = db();
  const p = String(period || "");
  const seller = D.get("SELECT * FROM sellers WHERE id=? AND tenant_id=?", sellerId, tenantId) || {};
  // orders that include at least one product; KPIs are per-seller via seller_id on ads/attribution
  const base = "SELECT COUNT(DISTINCT o.id) c, COALESCE(SUM(o.total),0) r FROM orders o WHERE o.tenant_id=? AND o.status IN " + stIn("order", "fulfilment").sql + " AND (" + (p ? "strftime('%Y-%m', o.created_at)=?" : "1=1") + ")";
  const fa = stIn("order", "fulfilment").args;
  /* only bind the period when the SQL actually carries its placeholder — an empty period
     builds a `1=1` branch with one fewer `?`, and binding it anyway raises
     "column index out of range" and takes the whole metrics call down with it */
  /* COUNT(DISTINCT o.id) already collapses to one row — a `GROUP BY o.id` here would
     return *no* row for a store with zero orders, leaving `.c` undefined and throwing,
     so it is omitted (a no-order store must read 0, not crash) */
  const ord = p ? D.get(base, tenantId, ...fa, p).c : D.get(base, tenantId, ...fa).c;
  const rev = p ? D.get(base, tenantId, ...fa, p).r : D.get(base, tenantId, ...fa).r;
  const takeRate = Number(seller.commission_pct || 5) / 100;
  const commission = +(Number(rev) * takeRate).toFixed(2);
  const adSpend = D.get("SELECT COALESCE(SUM(spent),0) s FROM ads WHERE tenant_id=? AND seller_id=?", tenantId, sellerId).s;
  const adRevenue = D.get("SELECT COALESCE(SUM(revenue),0) r FROM attribution WHERE tenant_id=? AND seller_id=?", tenantId, sellerId).r;
  const adRoi = adSpend ? +(adRevenue / adSpend).toFixed(2) : 0;
  D.run("INSERT INTO seller_metrics(tenant_id,seller_id,period,orders,revenue,take_rate,commission,ads_spend,ad_roi) VALUES(?,?,?,?,?,?,?,?,?)",
    tenantId, sellerId, p, ord, rev, takeRate, commission, adSpend, adRoi);
  return { seller_id: sellerId, period: p, orders: ord, revenue: rev, take_rate: takeRate, commission, ads_spend: adSpend, ad_revenue: adRevenue, ad_roi: adRoi };
}

function allSellerMetrics(tenantId, period) {
  const D = db();
  const sellers = D.all("SELECT id FROM sellers WHERE tenant_id=?", tenantId);
  return sellers.map(s => sellerMetrics(tenantId, s.id, period));
}

/* ---------- take-rate settlement ---------- */
function settleTakeRate(tenantId, sellerId, period) {
  const D = db();
  const m = sellerMetrics(tenantId, sellerId, period);
  // credit the seller's commission into their wallet via the offers ledger (single source of truth)
  offers().credit(tenantId, "seller:" + sellerId, m.commission, "take_rate", "settle:" + (period || "spot"), require("./defaults.js").currency(tenantId), "marketplace");
  const p = fin().openPayout(tenantId, sellerId, "commission", period || "", [{ ref: "order:" + m.orders, kind: "commission", amount: m.commission, currency: require("./defaults.js").currency(tenantId) }]);
  return { metrics: m, payout: p };
}

module.exports = {
  seed, BID_MODELS, ATTR_MODELS, AD_SURFACES,
  createAd, listAds, recordEvent, rankAds, sponsored,
  attribute, sellerMetrics, allSellerMetrics,
  settleTakeRate
};
