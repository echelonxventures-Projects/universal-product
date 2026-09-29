/* LUXORA Platform — Marketplace engine.
   Seller onboarding & verification, a seller-scoped portal surface, buy-box
   multi-seller offers, FBA inbound, seller performance / account health,
   buyer-protection (A-to-z) claims, sponsored brands/display creatives and
   smart-fulfilment grading.

   Everything that looks like an enum is a registry row (meta_lists — see
   lib/parity-registries.js). Settlements and payouts reuse the single finance
   ledger (lib/fin.js, lib/offers.js) rather than opening a new money path. */
"use strict";

const db = () => require("./db.js");
const fin = () => require("./fin.js");
const offers = () => require("./offers.js");
const reg = () => require("./parity-registries.js");
const caps = () => require("./capabilities.js");
const crypto = require("crypto");

const J = (v, d) => { try { return v == null || v === "" ? (d == null ? [] : d) : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d == null ? [] : d; } };
const refOf = (pfx) => pfx + "-" + Date.now().toString(36).toUpperCase().slice(-6) + crypto.randomBytes(2).toString("hex").toUpperCase();

/* ---------- seller onboarding & verification ---------- */
/* an application carries the business identity + payout instrument; the store
   stays 'pending' until review — the marketplace's own onboarding gate. */
function apply(tenantId, input) {
  const D = db();
  const status = reg().has("mktOnboardingStatuses", input.status) ? input.status : "submitted";
  let sellerId = Number(input.seller_id) || null;
  if (!sellerId && input.business_name) {
    const ex = D.get("SELECT id FROM sellers WHERE tenant_id=? AND name=?", Number(tenantId), String(input.business_name));
    if (ex) sellerId = ex.id;
  }
  const r = D.run("INSERT INTO seller_onboarding(tenant_id,seller_id,ref,business_name,business_type,gstin,pan,tan,bank_name,bank_account,bank_ifsc,docs,status,submitted_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'))",
    Number(tenantId), sellerId, refOf("SELLER"), String(input.business_name || ""),
    reg().has("mktBusinessTypes", input.business_type) ? input.business_type : "proprietorship",
    String(input.gstin || ""), String(input.pan || ""), String(input.tan || ""),
    String(input.bank_name || ""), String(input.bank_account || ""), String(input.bank_ifsc || ""),
    JSON.stringify(input.docs || []), status);
  return D.get("SELECT * FROM seller_onboarding WHERE id=?", r.lastInsertRowid);
}
/* review flips the application (and the seller it belongs to); approval also
   stamps the seller's verified flag so the storefront can show the badge */
function review(tenantId, onboardingId, decision, by, notes) {
  const D = db();
  const ob = D.get("SELECT * FROM seller_onboarding WHERE id=? AND tenant_id=?", Number(onboardingId), Number(tenantId));
  if (!ob) throw new Error("Unknown seller application");
  if (!["approved", "rejected", "documents_pending", "verification"].includes(decision)) throw new Error("Unknown review decision");
  D.run("UPDATE seller_onboarding SET status=?, reviewed_at=datetime('now'), reviewed_by=?, notes=? WHERE id=?",
    decision, String(by || ""), String(notes || ""), ob.id);
  if (decision === "approved" && ob.seller_id) {
    D.run("UPDATE sellers SET onboarding_status='approved', verified=1 WHERE id=? AND tenant_id=?", ob.seller_id, Number(tenantId));
  } else if (ob.seller_id) {
    D.run("UPDATE sellers SET onboarding_status=? WHERE id=? AND tenant_id=?", decision, ob.seller_id, Number(tenantId));
  }
  return D.get("SELECT * FROM seller_onboarding WHERE id=?", ob.id);
}

/* ---------- buy-box: competing seller offers on one product ---------- */
/* the buy-box winner is the offer with the best composite of price, fulfilment
   speed and seller health — the three axes a featured-offer box optimises.
   Recomputing is idempotent: exactly one active offer per product wins. */
function score(o, health, P) {
  /* the three axes are capability parameters, not constants — an operator can
     decide that trust outranks price for a luxury marketplace instead */
  const priceW = Number(P.price_weight), speedW = Number(P.speed_weight), trustW = Number(P.trust_weight);
  const speed = (Number(o.shipping_days) || Number(P.speed_baseline_days) || 3) + (Number(o.handling_hours) || Number(P.handling_baseline_hours) || 12) / 24;
  const trust = (health && health.health_score) || 50;
  return priceW * (1 / Math.max(0.01, Number(o.price) || 1)) * 100 + speedW * (10 - Math.min(10, speed)) + trustW * (trust / 100);
}
function recomputeBuybox(tenantId, productId) {
  const D = db();
  const P = caps().cap(tenantId, "buy_box");
  if (!Object.keys(P).length) return { winner: null, offers: [], error: "buy_box not enabled for this tenant" };
  const offers0 = D.all("SELECT * FROM seller_offers WHERE tenant_id=? AND product_id=? AND offer_status='active'", Number(tenantId), String(productId));
  if (!offers0.length) return { winner: null, offers: [] };
  for (const o of offers0) {
    const h = D.get("SELECT health_score FROM seller_performance WHERE tenant_id=? AND seller_id=? ORDER BY id DESC LIMIT 1", Number(tenantId), o.seller_id);
    o.buybox_score = +score(o, h, P).toFixed(4);
  }
  offers0.sort((a, b) => b.buybox_score - a.buybox_score);
  D.run("UPDATE seller_offers SET buybox=0 WHERE tenant_id=? AND product_id=?", Number(tenantId), String(productId));
  D.run("UPDATE seller_offers SET buybox=1 WHERE id=?", offers0[0].id);
  return { winner: offers0[0], offers: offers0 };
}
function listOffers(tenantId, productId) {
  return db().all("SELECT * FROM seller_offers WHERE tenant_id=? AND product_id=? ORDER BY price ASC", Number(tenantId), String(productId));
}
/* the storefront reads the winning offer to render "other sellers" + the box price */
function buyboxFor(tenantId, productId) {
  const D = db();
  const win = D.get("SELECT * FROM seller_offers WHERE tenant_id=? AND product_id=? AND offer_status='active' AND buybox=1", Number(tenantId), String(productId));
  if (!win) return null;
  const seller = D.get("SELECT * FROM sellers WHERE id=? AND tenant_id=?", win.seller_id, Number(tenantId));
  return { ...win, seller };
}

/* ---------- FBA inbound ---------- */
function fbaInbound(tenantId, input) {
  const D = db();
  const P = caps().cap(tenantId, "fba_inbound");
  const status = reg().has("mktFbaStatuses", input.status) ? input.status : (P.default_status || "created");
  const r = D.run("INSERT INTO fba_inbound(tenant_id,ref,seller_id,warehouse_id,sku_id,units,fee,status) VALUES(?,?,?,?,?,?,?,?)",
    Number(tenantId), refOf("FBA"), Number(input.seller_id) || null, Number(input.warehouse_id) || null,
    Number(input.sku_id) || null, Number(input.units) || 0, +Number(input.fee || 0).toFixed(2), status);
  return D.get("SELECT * FROM fba_inbound WHERE id=?", r.lastInsertRowid);
}
/* receiving closes the inbound and moves units into the FC's inventory */
function receiveFba(tenantId, inboundId) {
  const D = db();
  const f = D.get("SELECT * FROM fba_inbound WHERE id=? AND tenant_id=? AND status IN ('created','in_transit','receiving')", Number(inboundId), Number(tenantId));
  if (!f) throw new Error("FBA inbound not receivable");
  D.run("UPDATE fba_inbound SET status='received', received_at=datetime('now') WHERE id=?", f.id);
  if (f.sku_id && f.warehouse_id) {
    /* the legacy inventory table has no uniqueness on (tenant,sku,warehouse), so
       the accumulation is read-then-written rather than an ON CONFLICT upsert */
    const cur = D.get("SELECT id, qty FROM inventory WHERE tenant_id=? AND sku_id=? AND warehouse_id=?", Number(tenantId), f.sku_id, f.warehouse_id);
    if (cur) D.run("UPDATE inventory SET qty=qty+? WHERE id=?", Number(f.units) || 0, cur.id);
    else D.run("INSERT INTO inventory(tenant_id,sku_id,warehouse_id,qty) VALUES(?,?,?,?)",
      Number(tenantId), f.sku_id, f.warehouse_id, Number(f.units) || 0);
  }
  return D.get("SELECT * FROM fba_inbound WHERE id=?", f.id);
}

/* ---------- seller performance / account health ---------- */
/* account-health axes: ODR (order defect rate), late-shipment rate,
   pre-fulfilment cancellation rate and valid-tracking rate. Each is computed from
   real orders/returns/claims for the period, then rolled into a health score that
   drives tier and suspension. Thresholds are registry-driven (mktTiers). */
function computePerformance(tenantId, sellerId, period) {
  const D = db();
  const P = caps().cap(tenantId, "seller_health");
  if (!Object.keys(P).length) throw new Error("seller_health is not enabled for this tenant");
  const p = String(period || new Date().toISOString().slice(0, 7));
  const seller = D.get("SELECT * FROM sellers WHERE id=? AND tenant_id=?", Number(sellerId), Number(tenantId));
  if (!seller) throw new Error("Unknown seller");
  /* orders attributed to this seller (via the products' supplier_id or the order's
     seller_id) in the given month */
  const rows = D.all(`SELECT o.id, o.status FROM orders o WHERE o.tenant_id=? AND strftime('%Y-%m', o.created_at)=?
    AND (o.seller_id=? OR o.id IN (SELECT oi.order_id FROM order_items oi JOIN products p ON p.id=oi.product_id WHERE p.tenant_id=? AND p.supplier_id=?))`,
    Number(tenantId), p, Number(sellerId), Number(tenantId), Number(sellerId));
  const orders = rows.length;
  const cancelled = rows.filter(o => o.status === "cancelled").length;
  /* ODR = buyer claims opened + returns requested, over orders */
  const claims = D.all("SELECT id FROM buyer_claims WHERE tenant_id=? AND seller_id=? AND strftime('%Y-%m', created_at)=?", Number(tenantId), Number(sellerId), p).length;
  const returns = D.all("SELECT r.id FROM returns r JOIN orders o ON o.id=r.order_id WHERE r.tenant_id=? AND o.seller_id=? AND strftime('%Y-%m', r.created_at)=?", Number(tenantId), Number(sellerId), p).length;
  const lateDays = Number(P.late_shipment_days);
  const late = D.all(`SELECT s.id FROM shipments s WHERE s.tenant_id=? AND s.status NOT IN ('delivered') AND s.created_at < datetime('now','-' || ? || ' days')
    AND s.order_id IN (SELECT o.id FROM orders o WHERE o.tenant_id=? AND strftime('%Y-%m', o.created_at)=? AND (o.seller_id=? OR o.id IN (SELECT oi.order_id FROM order_items oi JOIN products p ON p.id=oi.product_id WHERE p.supplier_id=?)))`,
    Number(tenantId), lateDays, Number(tenantId), p, Number(sellerId)).length;
  const shipped = rows.filter(o => ["shipped", "delivered"].includes(o.status)).length;
  const odrW = Number(P.odr_weight), cancelW = Number(P.cancellation_weight), lateW = Number(P.late_weight);
  const odr = orders ? +(100 * (claims + returns) / orders * odrW).toFixed(2) : 0;
  const cancelRate = orders ? +(100 * cancelled / orders * cancelW).toFixed(2) : 0;
  const lateRate = shipped ? +(100 * late / Math.max(1, shipped) * lateW).toFixed(2) : 0;
  const vtr = shipped ? +(100 - Math.min(100, lateRate)).toFixed(2) : 100;
  /* health: 100 minus weighted defects. The tier cut-offs are capability
     parameters — an operator can raise platinum to 98 or add a sixth tier. */
  const health = Math.max(0, Math.min(100, +(100 - (odr + cancelRate + lateRate)).toFixed(2)));
  const thresholds = P.tier_thresholds || {};
  let tier = "standard";
  for (const [t, cut] of Object.entries(thresholds)) if (health >= Number(cut)) { tier = t; break; }
  const suspendBelow = Number(P.suspend_below);
  D.run("INSERT INTO seller_performance(tenant_id,seller_id,period,orders,odr,odr_targets,late_ship_rate,late_shipments,cancel_rate,cancellations,valid_tracked_rate,health_score,tier,status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?, 'computed')",
    Number(tenantId), Number(sellerId), p, orders, odr, claims + returns, lateRate, late, cancelRate, cancelled, vtr, health, tier);
  D.run("UPDATE sellers SET health_score=?, tier=? WHERE id=? AND tenant_id=?", health, tier, Number(sellerId), Number(tenantId));
  /* an unhealthy seller is suspended from the buy-box automatically */
  if (health < suspendBelow) D.run("UPDATE seller_offers SET offer_status='suspended' WHERE seller_id=? AND tenant_id=?", Number(sellerId), Number(tenantId));
  return D.get("SELECT * FROM seller_performance ORDER BY id DESC LIMIT 1");
}
function healthFor(tenantId, sellerId) {
  return db().get("SELECT * FROM seller_performance WHERE tenant_id=? AND seller_id=? ORDER BY id DESC LIMIT 1", Number(tenantId), Number(sellerId));
}

/* ---------- buyer protection claims (A-to-z) ---------- */
function openClaim(tenantId, input) {
  const D = db();
  const kind = reg().has("mktClaimKinds", input.kind) ? input.kind : "atoz";
  const r = D.run("INSERT INTO buyer_claims(tenant_id,ref,order_id,buyer,seller_id,kind,reason,amount,currency,evidence,status) VALUES(?,?,?,?,?,?,?,?,?,?, 'opened')",
    Number(tenantId), refOf("CLAIM"), Number(input.order_id) || null, String(input.buyer || ""),
    Number(input.seller_id) || null, kind, String(input.reason || ""), +Number(input.amount || 0).toFixed(2),
    String(input.currency || "USD"), JSON.stringify(input.evidence || []));
  const c = D.get("SELECT * FROM buyer_claims WHERE id=?", r.lastInsertRowid);
  /* mark any escrow hold on that order as disputed so funds don't release mid-claim */
  const P = caps().cap(tenantId, "buyer_protection");
  if (P.auto_dispute_escrow) {
    const esc = D.get("SELECT id FROM escrow_holds WHERE tenant_id=? AND order_id=? AND held=1", Number(tenantId), Number(input.order_id) || 0);
    if (esc) D.run("UPDATE escrow_holds SET dispute_opened=1, status='disputed' WHERE id=?", esc.id);
  }
  return c;
}
function resolveClaim(tenantId, claimId, resolution, by) {
  const D = db();
  const c = D.get("SELECT * FROM buyer_claims WHERE id=? AND tenant_id=?", Number(claimId), Number(tenantId));
  if (!c) throw new Error("Unknown claim");
  const res = String(resolution || "").startsWith("resolved_") ? resolution : "resolved_" + resolution;
  D.run("UPDATE buyer_claims SET status=?, resolution=?, resolved_at=datetime('now'), resolved_by=? WHERE id=?",
    res, String(resolution || ""), String(by || ""), c.id);
  const P = caps().cap(tenantId, "buyer_protection");
  if (res === "resolved_buyer" && c.buyer) offers().credit(tenantId, c.buyer, c.amount, P.refund_kind || "refund", "claim:" + c.ref, c.currency, "claims");
  return D.get("SELECT * FROM buyer_claims WHERE id=?", c.id);
}

/* ---------- smart fulfilment (graded SLAs) ---------- */
function enrolSmart(tenantId, input) {
  const D = db();
  const P = caps().cap(tenantId, "smart_fulfilment");
  if (!Object.keys(P).length) throw new Error("smart_fulfilment is not enabled for this tenant");
  const grade = reg().has("mktSmartGrades", input.grade) ? input.grade : "b";
  /* the grade → SLA table is a capability parameter, so a operator can retune
     every grade's promise without a code change */
  const slaTable = P.sla_hours || {};
  const sla = slaTable[grade] != null ? Number(slaTable[grade]) : Number(P.default_sla_hours) || 24;
  const r = D.run("INSERT INTO smart_fulfilment(tenant_id,seller_id,ref,grade,sla_hours,packed_same_day,score,status) VALUES(?,?,?,?,?,?,?, 'enrolled')",
    Number(tenantId), Number(input.seller_id) || null, refOf("SF"), grade, Number(input.sla_hours || sla) || sla,
    input.packed_same_day ? 1 : 0, +Number(input.score || 0).toFixed(2));
  return D.get("SELECT * FROM smart_fulfilment WHERE id=?", r.lastInsertRowid);
}

/* ---------- seller-scoped portal surface ---------- */
/* the seller portal is a read + act window scoped to one seller: the caller
   proves the seller identity (a staff user with the seller link, or an API token
   issued per seller). No /api/seller/* route owns data — this helper composes the
   same generic entity rows the console already serves, filtered to one seller. */
function sellerPortal(tenantId, sellerId) {
  const D = db();
  const seller = D.get("SELECT * FROM sellers WHERE id=? AND tenant_id=?", Number(sellerId), Number(tenantId));
  if (!seller) throw new Error("Unknown seller");
  const perf = healthFor(tenantId, sellerId);
  const myOffers = D.all("SELECT * FROM seller_offers WHERE tenant_id=? AND seller_id=? ORDER BY id DESC", Number(tenantId), Number(sellerId));
  const myOrders = D.all(`SELECT o.* FROM orders o WHERE o.tenant_id=? AND (o.seller_id=? OR o.id IN
    (SELECT oi.order_id FROM order_items oi JOIN products p ON p.id=oi.product_id WHERE p.tenant_id=? AND p.supplier_id=?))
    ORDER BY o.id DESC LIMIT 50`, Number(tenantId), Number(sellerId), Number(tenantId), Number(sellerId));
  const myClaims = D.all("SELECT * FROM buyer_claims WHERE tenant_id=? AND seller_id=? ORDER BY id DESC LIMIT 50", Number(tenantId), Number(sellerId));
  const myFba = D.all("SELECT * FROM fba_inbound WHERE tenant_id=? AND seller_id=? ORDER BY id DESC", Number(tenantId), Number(sellerId));
  const myAds = D.all("SELECT * FROM sponsored_creatives WHERE tenant_id=? AND seller_id=? ORDER BY id DESC", Number(tenantId), Number(sellerId));
  const payout = D.get("SELECT COALESCE(SUM(net),0) net, COALESCE(SUM(commission),0) com FROM settlements WHERE tenant_id=? AND seller_id=?", Number(tenantId), Number(sellerId));
  return { seller, performance: perf, offers: myOffers, orders: myOrders, claims: myClaims, fba: myFba, ads: myAds, payout };
}

module.exports = {
  apply, review,
  recomputeBuybox, listOffers, buyboxFor,
  fbaInbound, receiveFba,
  computePerformance, healthFor,
  openClaim, resolveClaim,
  enrolSmart,
  sellerPortal
};
