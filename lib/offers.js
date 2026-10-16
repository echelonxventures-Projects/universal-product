/* LUXORA Platform — Central Offers / Coupons / Discounts / Wallet engine.
   ONE reusable service (like registry.js / ai.js / modules.js) that any surface — storefront cart,
   checkout, platform subscription billing, AI metering, or a client API — calls to compute discounts,
   credits, free-shipping and coupon redemptions. Everything (types, scopes, channels, directions,
   funders, coupon kinds, limits) is DATA in meta_lists; new offer types/scope rules are added without
   code. Legacy per-store `promotions` are read too, so nothing that already works regresses. */
"use strict";

let _db = null;
const db = () => _db || (_db = require("./db.js"));
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };
const list = (name, dflt) => J((db().get("SELECT items i FROM meta_lists WHERE name=?", name) || {}).i, dflt);
const today = () => new Date().toISOString().slice(0, 10);
const r2 = n => +Number(n || 0).toFixed(2);

/* ---- registry SEED (INSERT OR IGNORE ⇒ editable in Data Studio, self-heals on upgrade) ---- */
const REGISTRIES = {
  offerTypes: [
    { key: "percent", name: "% off", direction: "discount", unit: "%" },
    { key: "fixed", name: "Fixed amount off", direction: "discount", unit: "amount" },
    { key: "fixed_per_item", name: "Fixed off per item", direction: "discount", unit: "amount" },
    { key: "free_ship", name: "Free shipping", direction: "free_ship", unit: "" },
    { key: "threshold_free_ship", name: "Free ship over threshold", direction: "free_ship", unit: "amount" },
    { key: "bogo", name: "Buy 1 Get 1", direction: "discount", unit: "items" },
    { key: "buy_x_get_y", name: "Buy X Get Y free", direction: "discount", unit: "items" },
    { key: "x_for_y", name: "X for the price of Y", direction: "discount", unit: "items" },
    { key: "multi_buy", name: "Multi-buy tier", direction: "discount", unit: "amount" },
    { key: "bundle_price", name: "Bundle price", direction: "discount", unit: "amount" },
    { key: "tier_qty", name: "Quantity tier (whole cart)", direction: "discount", unit: "amount" },
    { key: "flash_percent", name: "Flash % off (time-bound)", direction: "discount", unit: "%" },
    { key: "cashback", name: "Cashback to wallet", direction: "credit", unit: "%" },
    { key: "spend_get_credit", name: "Spend ≥ min, get credit", direction: "reward", unit: "amount" },
    { key: "gift_card_credit", name: "Gift-card credit", direction: "credit", unit: "amount" }
  ],
  offerDirections: ["discount", "credit", "reward", "free_ship", "exchange", "gift"],
  offerChannels: ["commerce", "subscription", "ai", "any"],
  offerScopes: ["store", "category", "node", "product", "brand", "customer", "cart", "line", "subscription", "ai"],
  offerFunders: ["self", "bank", "brand", "partner", "platform"],
  couponKinds: ["code", "single_use", "multi_use", "first_order", "bulk_issued", "gift_card", "bank_voucher", "referral"],
  stackingPolicies: ["stack_with_others", "group_exclusive", "exclusive", "max_count"],
  offerStatuses: ["draft", "scheduled", "active", "expired", "inactive"],
  couponStatuses: ["active", "exhausted", "revoked", "expired"],
  redemptionStatuses: ["redeemed", "voided", "reserved"],
  walletEntryKinds: ["deposit", "redeem", "refund", "reward", "adjust", "transfer", "expire", "cashback"],
  walletAccountKinds: ["gift", "reward", "prepaid", "refund"]
};

function seed() {
  const D = db();
  const ensure = (name, items) => D.run("INSERT OR IGNORE INTO meta_lists(name,label,items) VALUES(?,?,?)", name, name, JSON.stringify(items));
  for (const [k, v] of Object.entries(REGISTRIES)) ensure(k, v);
}

/* ---- eligible offers: central (tenant + global) + legacy promotions (commerce only) ---- */
function eligible(tenantId, channel, coupon, allowGlobal) {
  const C = db(); const now = today(); const up = String(coupon || "").trim().toUpperCase();
  const anyCode = up === "*"; /* discovery reads the whole eligible catalogue, coded exchanges included */
  /* lifecycle sweep: activate scheduled offers whose start has passed; expire those past end */
  try { C.run("UPDATE offers SET status='active' WHERE status IN ('scheduled','draft') AND starts IS NOT NULL AND starts<=? AND (ends IS NULL OR ends>=?)", now, now); C.run("UPDATE offers SET status='expired' WHERE status='active' AND ends IS NOT NULL AND ends<?", now); C.run("UPDATE coupons SET status='expired' WHERE status='active' AND ends IS NOT NULL AND ends<?", now); } catch (e) { }
  const out = [];
  const rows = C.all(`SELECT * FROM offers WHERE status='active' AND channel IN (?, 'any')
    AND (starts IS NULL OR starts<=?) AND (ends IS NULL OR ends>=?) AND (tenant_id=? ${allowGlobal ? "OR tenant_id=0" : ""})
    ORDER BY priority DESC, value DESC`, channel, now, now, tenantId);
  for (const o of rows) {
    if (o.code && !anyCode && o.code.toUpperCase() !== up) continue;
    out.push({ id: o.id, _src: "offer", _row: o, code: o.code || null, type: o.type, direction: o.direction || "discount", channel: o.channel,
      value: Number(o.value) || 0, currency: o.currency, scope_type: o.scope_type || "store", scope: J(o.scope_value, {}),
      rules: J(o.rules, {}), funder: o.funder || "self", funder_ref: o.funder_ref, brand_ref: o.brand_ref,
      min_amount: Number(o.min_amount) || 0, min_qty: Number(o.min_qty) || 0, max_discount: Number(o.max_discount) || 0,
      usage_limit: Number(o.usage_limit) || 0, used: Number(o.used) || 0, per_owner_limit: Number(o.per_owner_limit) || 0,
      stack_group: o.stack_group || "", stack_policy: o.stack_policy || "stack_with_others", name: o.name, owner: null });
  }
  if (channel === "commerce") {
    for (const p of C.all("SELECT * FROM promotions WHERE tenant_id=? AND status='active' AND (starts IS NULL OR starts<=?) AND (ends IS NULL OR ends>=?)", tenantId, now, now)) {
      const sc = J(p.scope, {}), rules = J(p.rules, {});
      if (p.code && !anyCode && p.code.toUpperCase() !== up) continue;
      out.push({ id: p.id, _src: "promotion", _row: p, code: p.code || null, type: p.type, direction: "discount", channel: "commerce",
        value: Number(p.value) || 0, currency: null, scope_type: sc.node ? "node" : sc.products ? "product" : "store",
        scope: sc, rules, funder: "self", brand_ref: null, min_amount: rules.min || 0, min_qty: 0, max_discount: 0,
        usage_limit: 0, used: 0, per_owner_limit: 0, stack_group: "", stack_policy: "stack_with_others", name: p.name });
    }
  }
  return out;
}

function scopeItems(offer, items, C, tenantId) {
  const st = offer.scope_type, sc = offer.scope || {};
  if (st === "store" || st === "cart" || st === "line") return items;
  if (st === "category") return items.filter(i => (sc.categories || sc.category ? [].concat(sc.categories || sc.category) : []).includes(i.dept));
  if (st === "brand") return items.filter(i => (sc.brands || []).includes(i.brand));
  if (st === "product") return items.filter(i => (sc.products || []).includes(i.id));
  if (st === "node") {
    const nodeKey = sc.node; if (!nodeKey) return [];
    const node = C.get("SELECT id FROM taxonomy WHERE tenant_id=? AND key=?", tenantId, nodeKey); if (!node) return [];
    const ids = [node.id]; let grew = true;
    const allNodes = C.all("SELECT id,parent_id FROM taxonomy WHERE tenant_id=?", tenantId);
    while (grew) { grew = false; for (const n of allNodes) if (ids.includes(n.parent_id) && !ids.includes(n.id)) { ids.push(n.id); grew = true; } }
    return items.filter(i => i.node_id && ids.includes(i.node_id));
  }
  return items;
}
const lineTotal = i => Number(i.price) * Number(i.qty);
const subOf = its => its.reduce((n, i) => n + lineTotal(i), 0);
const qtyOf = its => its.reduce((n, i) => n + Number(i.qty), 0);

/* ---- type handlers (data-driven math; unknown type ⇒ skipped ⇒ extensible at registry level) ---- */
const HANDLERS = {
  percent: (o, its) => ({ discount: subOf(its) * o.value / 100 }),
  flash_percent: (o, its) => ({ discount: subOf(its) * o.value / 100 }),
  fixed: (o, its) => ({ discount: Math.min(o.value, subOf(its)) }),
  fixed_per_item: (o, its) => ({ discount: Math.min(o.value * qtyOf(its), subOf(its)) }),
  free_ship: () => ({ freeShip: true }),
  threshold_free_ship: (o, its, amt) => (amt >= o.value ? { freeShip: true } : {}),
  bogo: (o, its) => { let d = 0; for (const i of its) { const free = Math.floor(i.qty / 2) * (o.value || 1); d += Math.min(free, Math.max(0, i.qty - 1)) * lineTotal(i) / i.qty; } return { discount: d }; },
  buy_x_get_y: (o, its) => { const x = Number(o.rules.x || 1), y = Number(o.rules.y || 1); let d = 0; for (const i of its) { const sets = Math.floor(i.qty / (x + y)); d += sets * y * lineTotal(i) / i.qty; } return { discount: d }; },
  x_for_y: (o, its) => { const x = Number(o.rules.x || 2), y = Number(o.rules.y || 1); let d = 0; for (const i of its) { const sets = Math.floor(i.qty / x); d += sets * (x - y) * lineTotal(i) / i.qty; } return { discount: d }; },
  multi_buy: (o, its) => { let d = 0; for (const i of its) { let price = i.price; (o.rules.tiers || []).forEach(t => { if (i.qty >= t.qty) price = t.price; }); d += Math.max(0, (i.price - price)) * i.qty; } return { discount: d }; },
  bundle_price: (o, its) => { const req = o.scope.products || []; if (!req.length || !req.every(id => its.some(i => i.id === id))) return {}; const bundle = its.filter(i => req.includes(i.id)); return { discount: Math.max(0, subOf(bundle) - o.value) }; },
  tier_qty: (o, its) => { let priceRate = 1; (o.rules.tiers || []).forEach(t => { if (qtyOf(its) >= t.qty) priceRate = t.rate != null ? t.rate : (1 - (t.pct || 0) / 100); }); return { discount: subOf(its) * (1 - priceRate) }; },
  cashback: (o, its) => ({ credits: subOf(its) * o.value / 100 }),
  spend_get_credit: (o, its, amt) => (amt >= (o.rules.min || o.min_amount) ? { credits: o.rules.credit != null ? Number(o.rules.credit) : o.value } : {}),
  gift_card_credit: () => ({})
};

/* ---- evaluate: the one entry every surface uses ---- */
const ABS_TYPES = new Set(["fixed", "fixed_per_item", "bundle_price", "multi_buy", "spend_get_credit"]);
function evaluate(ctx) {
  const D = db();
  const channel = ctx.channel || "commerce";
  const amount = Number(ctx.amount != null ? ctx.amount : subOf(ctx.items || []));
  const coupon = ctx.coupon;
  const currency = ctx.currency ? String(ctx.currency).toUpperCase() : null;
  const owner = ctx.owner || null;
  const items = (ctx.items || []).map(i => ({ id: i.id, dept: i.dept, brand: i.brand, node_id: i.node_id, price: Number(i.price != null ? i.price : i.p) || 0, qty: Number(i.qty) || 1 }));
  if (!items.length && amount > 0) items.push({ id: "__base", dept: "", brand: "", node_id: null, price: amount, qty: 1 });
  const maxStack = ctx.stackMax != null ? ctx.stackMax : 5;
  /* GOIP hooks: an outer engine may supply the candidate pool (already gated by the constitutional
     eligibility engine), filter it, and impose an order (ranking objective). All three are optional —
     without them this is exactly the classic offers engine. */
  let offs = Array.isArray(ctx.pool) ? ctx.pool : eligible(ctx.tenantId, channel, coupon, ctx.allowGlobal !== false);
  if (typeof ctx.filter === "function") offs = offs.filter(o => { try { return !!ctx.filter(o); } catch (e) { return false; } });
  const requireOffersPro = channel === "commerce";
  const mods = require("./modules.js");
  const hasPro = mods.hasCap(ctx.tenantId, "offersPro");
  let discount = 0, credits = 0, freeShip = false; const applied = [], redemptions = []; const usedGroups = {};
  offs = typeof ctx.rank === "function" ? offs.slice().sort(ctx.rank) : offs.sort((a, b) => (b.type && a.type ? 0 : 0) || (b.min_amount - a.min_amount));
  for (const o of offs) {
    if (["bogo", "bundle_price", "multi_buy", "buy_x_get_y", "x_for_y"].includes(o.type) && requireOffersPro && !hasPro && o._src === "promotion") continue;
    /* currency guard: absolute-value types are only valid in their own currency; % / ratio / ship are currency-agnostic */
    if (ABS_TYPES.has(o.type) && o.currency && currency && String(o.currency).toUpperCase() !== currency) continue;
    if (o.usage_limit && o.used >= o.usage_limit) continue;
    if (o.per_owner_limit && owner && o._src === "offer") { const n = D.get("SELECT COUNT(*) c FROM coupon_redemptions WHERE offer_id=? AND owner=? AND status='redeemed'", o.id, owner).c; if (n >= o.per_owner_limit) continue; }
    if (o.min_amount && amount < o.min_amount) continue;
    if (o.min_qty && qtyOf(items) < o.min_qty) continue;
    if (o.stack_policy === "exclusive" && applied.length) continue;
    if (o.stack_group && usedGroups[o.stack_group] && o.stack_policy === "group_exclusive") continue;
    if (applied.length >= maxStack) break;
    const its = scopeItems(o, items, D, ctx.tenantId);
    if (!its.length && !["free_ship", "threshold_free_ship", "tier_qty", "spend_get_credit"].includes(o.type)) continue;
    const h = HANDLERS[o.type]; if (!h) continue;
    let res = {}; try { res = h(o, its, amount) || {}; } catch (e) { continue; }
    let d = r2(res.discount || 0); if (o.max_discount) d = Math.min(d, o.max_discount); d = Math.min(d, r2(amount - discount));
    if (d > 0) { discount += d; }
    if (res.credits) credits += Number(res.credits);
    if (res.freeShip) freeShip = true;
    if (d > 0 || res.credits || res.freeShip || res.grant) {
      const offerId = o._src === "offer" ? o.id : null;
      applied.push({ id: o.id, src: o._src, name: o.name, type: o.type, direction: o.direction, code: o.code || undefined, amount: d || 0, credits: r2(res.credits || 0), freeShip: !!res.freeShip, funder: o.funder, unit: res.unit || undefined, grant: res.grant || undefined });
      /* track every code- or central-offer-based application (usage/limits/analytics/clawback); legacy promos only when a code */
      if (offerId || o.code) redemptions.push({ offer_id: offerId, coupon_id: null, code: o.code || null, amount: d || 0, credits: r2(res.credits || 0), type: o.type, funder: o.funder, funder_ref: o.funder_ref, brand_ref: o.brand_ref, unit: res.unit || null, grant: res.grant || null, defer: res.defer || 0 });
      if (o.stack_group) usedGroups[o.stack_group] = 1;
    }
  }
  return { discount: r2(discount), credits: r2(credits), freeShip, applied, redemptions, netBase: r2(amount - discount) };
}

/* ---- coupons (issuable codes, funder-aware) + validation incl. ownership limits ---- */
function findCoupon(tenantId, code) {
  const D = db(); const c = String(code || "").trim().toUpperCase(); if (!c) return null;
  return D.get("SELECT * FROM coupons WHERE status='active' AND code=? AND (tenant_id=? OR tenant_id=0) AND (starts IS NULL OR starts<=?) AND (ends IS NULL OR ends>=?)", c, tenantId, today(), today());
}
function validateCoupon(tenantId, code, owner) {
  const D = db(); const c = String(code || "").trim().toUpperCase();
  if (c) {
    const cp = findCoupon(tenantId, c);
    /* a coupon code, and the offer behind it, are subject to the applicability rules */
    const rules = require("./rules.js"); const rctx = rules.at("coupons.code", tenantId);
    const ruled = (point, id) => { const d = rules.decideAt(point, String(id), rctx); return d.ok ? null : { ok: false, reason: "This code is not available here" + (d.reasons.length ? " — " + d.reasons.join("; ") : "") }; };
    if (cp) {
      const blocked = ruled("coupons.code", cp.code) || (cp.offer_id ? ruled("coupons.offer", cp.offer_id) : null);
      if (blocked) return blocked;
      if (cp.max_uses && cp.used >= cp.max_uses) return { ok: false, reason: "Coupon fully redeemed" };
      if (cp.per_owner_limit && owner) { const n = D.get("SELECT COUNT(*) c FROM coupon_redemptions WHERE coupon_id=? AND owner=?", cp.id, owner).c; if (n >= cp.per_owner_limit) return { ok: false, reason: "Coupon already used on this account" }; }
      if (cp.kind === "first_order" && owner) { const o = D.get("SELECT COUNT(*) c FROM orders WHERE owner=?", owner).c; if (o > 0) return { ok: false, reason: "New customers only" }; }
      return { ok: true, coupon: cp, code: c };
    }
    const offer = D.get("SELECT * FROM offers WHERE code=? AND status='active' AND (tenant_id=? OR tenant_id=0) AND (starts IS NULL OR starts<=?) AND (ends IS NULL OR ends>=?)", c, tenantId, today(), today());
    if (offer) { const blocked = ruled("coupons.offer", offer.id); if (blocked) return blocked; return { ok: true, code: c, offer }; }
  }
  // also accept legacy promotions or central auto codes via evaluate
  const anyEligible = eligible(tenantId, "commerce", c, true).some(o => o.code === c);
  return anyEligible ? { ok: true, code: c } : { ok: false, reason: "Invalid or expired promo code" };
}
function redeem(ctx, result, ref) {
  const D = db();
  const owner = ctx.owner || "", tid = ctx.tenantId, oid = ref && ref.order_id, iid = ref && ref.invoice_id;
  for (const rd of (result.redemptions || [])) {
    const cp = rd.code ? findCoupon(tid, rd.code) : null;
    const offerId = rd.offer_id || (cp && cp.offer_id) || null;
    D.run("INSERT INTO coupon_redemptions(tenant_id,coupon_id,offer_id,code,order_id,invoice_id,owner,channel,amount,credits,offer_type,funder,funder_ref,brand_ref,unit,status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, 'redeemed')",
      tid, cp ? cp.id : null, offerId, rd.code, oid || null, iid || null, owner, ctx.channel || "commerce", r2(rd.amount || 0), r2(rd.credits || 0), rd.type || "", rd.funder || "self", rd.funder_ref || "", rd.brand_ref || "",
      String(rd.unit || ctx.currency || "USD").toUpperCase());
    if (cp) { D.run("UPDATE coupons SET used=used+1 WHERE id=?", cp.id); if (cp.max_uses && (cp.used + 1) >= cp.max_uses) D.run("UPDATE coupons SET status='exhausted' WHERE id=?", cp.id); }
    if (offerId) D.run("UPDATE offers SET used=used+1 WHERE id=?", offerId);
  }
  /* credits are paid in their declared economic unit: money moves the wallet balance, everything else
     (points, coins, tokens, colonial credits…) is a ledger-only entry in that unit. Deferred value is
     not paid here at all — the GOIP hook schedules it and releases it on its due date. */
  const byUnit = {}; let legacy = 0;
  for (const rd of (result.redemptions || [])) {
    const c = Number(rd.credits) || 0; if (c <= 0 || rd.defer) continue;
    const u = String(rd.unit || "").toUpperCase();
    if (!u) legacy += c; else byUnit[u] = (byUnit[u] || 0) + c;
  }
  const deferred = (result.redemptions || []).reduce((n, rd) => n + (rd.defer ? Number(rd.credits) || 0 : 0), 0);
  if (!result.redemptions || !result.redemptions.length) legacy = Number(result.credits) || 0;
  const cur = (ctx.currency || "USD").toUpperCase();
  if (legacy > 0) credit(tid, owner, legacy, "reward", (ref && (ref.order_num || ref.note)) || "offer-credit", cur, ctx.channel || "commerce", "offers");
  for (const [u, amt] of Object.entries(byUnit)) {
    if (u === cur || MONEYISH.has(u)) credit(tid, owner, amt, "cashback", (ref && (ref.order_num || ref.note)) || "offer-credit", u, ctx.channel || "commerce", "offers");
    else ledgerEntry(tid, owner, u, "reward", amt, (ref && (ref.order_num || ref.note)) || "offer-credit", ctx.channel || "commerce", "offers");
  }
  for (const fn of REDEEM_HOOKS) { try { fn(ctx, result, ref); } catch (e) { console.error("offers redeem hook:", e.message); } }
  return { ok: true, credited: { money: r2(legacy), units: byUnit, deferred: r2(deferred) } };
}
/* claw back coupons + offer usage + wallet reward credits when an order is refunded */
function reverseRedemption(tenantId, ref) {
  const D = db(); const oid = ref && ref.order_id; if (!oid) return { ok: false, reason: "no order" };
  const rows = D.all("SELECT * FROM coupon_redemptions WHERE tenant_id=? AND order_id=? AND status='redeemed'", tenantId, oid);
  for (const r of rows) {
    if (r.coupon_id) { D.run("UPDATE coupons SET used=MAX(0,used-1) WHERE id=?", r.coupon_id); D.run("UPDATE coupons SET status='active' WHERE id=? AND status='exhausted'", r.coupon_id); }
    if (r.offer_id) D.run("UPDATE offers SET used=MAX(0,used-1) WHERE id=?", r.offer_id);
    D.run("UPDATE coupon_redemptions SET status='voided', meta=? WHERE id=?", JSON.stringify({ void_reason: "refund" }), r.id);
  }
  /* reverse the wallet reward credits booked for this order */
  if (ref && ref.order_num) { const owner = (D.get("SELECT owner FROM orders WHERE id=?", oid) || {}).owner; const we = D.all("SELECT amount FROM wallet_entries WHERE tenant_id=? AND owner=? AND kind IN ('reward','cashback') AND ref=? AND amount>0", tenantId, owner, ref.order_num); for (const e of we) debit(tenantId, owner, Number(e.amount), "refund", ref.order_num + ":clawback", "USD", "commerce", "offers"); }
  for (const fn of REVERSE_HOOKS) { try { fn(tenantId, ref); } catch (e) { console.error("offers reverse hook:", e.message); } }
  return { ok: true, voided: rows.length };
}
function analytics(tenantId) {
  const D = db();
  const by = t => D.all(`SELECT ${t} k, COUNT(*) n, COALESCE(SUM(amount),0) discount, COALESCE(SUM(credits),0) credits FROM coupon_redemptions WHERE ${tenantId ? "tenant_id=?" : "1=1"} AND status='redeemed' GROUP BY ${t} ORDER BY n DESC`, ...(tenantId ? [tenantId] : []));
  const tot = D.get(`SELECT COUNT(*) n, COALESCE(SUM(amount),0) discount, COALESCE(SUM(credits),0) credits FROM coupon_redemptions WHERE ${tenantId ? "tenant_id=?" : "1=1"} AND status='redeemed'`, ...(tenantId ? [tenantId] : []));
  return { totals: { redemptions: tot.n, discount: r2(tot.discount), credits: r2(tot.credits) }, byCode: by("code"), byType: by("offer_type"), byFunder: by("funder"), bySource: D.all(`SELECT CASE WHEN offer_id IS NULL THEN 'coupon' ELSE 'offer' END src, COUNT(*) n FROM coupon_redemptions ${tenantId ? "WHERE tenant_id=?" : ""} GROUP BY src`, ...(tenantId ? [tenantId] : [])) };
}

/* ---- hooks: one post-redemption / post-reversal notification point (GOIP registers here, so the
   plain storefront checkout path grants entitlements, burns budget and accrues settlement too) ---- */
const REDEEM_HOOKS = [], REVERSE_HOOKS = [];
function onRedeem(fn) { if (typeof fn === "function") REDEEM_HOOKS.push(fn); return REDEEM_HOOKS.length; }
function onReverse(fn) { if (typeof fn === "function") REVERSE_HOOKS.push(fn); return REVERSE_HOOKS.length; }
/* units that move the money balance; everything else is ledger-only (points/coins/tokens/credits) */
const MONEYISH = new Set(["USD", "EUR", "INR", "GBP", "AED", "AUD", "CAD", "JPY", "BRL", "SGD", "ZAR", "KES", "SAR", "CHF", "CNY", "MXN", "NGN", "IDR"]);

/* ---- wallet double-entry ledger (balances stay authoritative for existing flows) ---- */
function _bal(D, tid, owner) { const r = D.get("SELECT balance b FROM wallets WHERE tenant_id=? AND owner=?", tid, owner); return r ? +Number(r.b) : 0; }
function credit(tid, owner, amount, kind, ref, currency, channel, actor) {
  const D = db(); const amt = Number(amount) || 0; if (amt === 0) return { balance: _bal(D, tid, owner) };
  D.run(`INSERT INTO wallets(tenant_id,owner,balance,updated_at) VALUES(?,?,?,datetime('now'))
         ON CONFLICT(tenant_id,owner) DO UPDATE SET balance=balance+excluded.balance, updated_at=datetime('now')`, tid, owner, amt);
  const after = _bal(D, tid, owner);
  D.run("INSERT INTO wallet_entries(tenant_id,owner,currency,kind,amount,balance_after,ref,channel,actor) VALUES(?,?,?,?,?,?,?,?,?)",
    tid, owner, currency || "USD", kind || "deposit", amt, after, ref || "", channel || "commerce", actor || "system");
  return { balance: after };
}
function debit(tid, owner, amount, kind, ref, currency, channel, actor) {
  const D = db(); const amt = Number(amount) || 0; if (amt === 0) return { balance: _bal(D, tid, owner) };
  /* a debit only ever takes money out. A negative amount used to run `balance - (-x)` and
     CREDIT the wallet — a client-chosen negative premium / fee / spend minted money. */
  if (!(amt > 0)) throw new Error("Debit amount must be positive");
  D.run(`INSERT INTO wallets(tenant_id,owner,balance,updated_at) VALUES(?,?,?,datetime('now'))
         ON CONFLICT(tenant_id,owner) DO UPDATE SET balance=MAX(0, balance - ?), updated_at=datetime('now')`, tid, owner, amt, amt);
  const after = _bal(D, tid, owner);
  D.run("INSERT INTO wallet_entries(tenant_id,owner,currency,kind,amount,balance_after,ref,channel,actor) VALUES(?,?,?,?,?,?,?,?,?)",
    tid, owner, currency || "USD", kind || "redeem", -amt, after, ref || "", channel || "commerce", actor || "system");
  return { balance: after };
}
/* a ledger entry in a non-money unit: recorded, queryable, never touching the money balance */
function ledgerEntry(tid, owner, unit, kind, amount, ref, channel, actor) {
  const D = db(); const amt = Number(amount) || 0; if (!amt) return { balance: unitBalance(tid, owner, unit) };
  const after = unitBalance(tid, owner, unit) + amt;
  D.run("INSERT INTO wallet_entries(tenant_id,owner,currency,kind,amount,balance_after,ref,channel,actor) VALUES(?,?,?,?,?,?,?,?,?)",
    tid, owner, String(unit || "USD").toUpperCase(), kind || "reward", amt, after, ref || "", channel || "commerce", actor || "goip");
  return { balance: after, unit: String(unit || "USD").toUpperCase() };
}
function unitBalance(tid, owner, unit) {
  const r = db().get("SELECT COALESCE(SUM(amount),0) b FROM wallet_entries WHERE tenant_id=? AND owner=? AND currency=?", tid, owner, String(unit || "USD").toUpperCase());
  return r ? +Number(r.b).toFixed(4) : 0;
}
function ledger(tenantId, owner) { const D = db(); return D.all("SELECT * FROM wallet_entries WHERE tenant_id=? AND owner=? ORDER BY id DESC LIMIT 200", tenantId, owner); }

function stats(tenantId) {
  const D = db();
  const byFunder = D.all(`SELECT funder, SUM(amount) amount, COUNT(*) n FROM coupon_redemptions ${tenantId ? "WHERE tenant_id=?" : "WHERE 1=1"} GROUP BY funder`, ...(tenantId ? [tenantId] : []));
  return { byFunder: byFunder.map(r => ({ funder: r.funder, amount: r2(r.amount), redemptions: r.n })) };
}

function discountFor(channel, tenantId, amount, opts) {
  const res = evaluate(Object.assign({ channel, tenantId, amount: Number(amount) || 0, items: [] }, opts || {}));
  return res;
}

module.exports = { REGISTRIES, seed, evaluate, eligible, validateCoupon, findCoupon, redeem, reverseRedemption, analytics, credit, debit, ledger, ledgerEntry, unitBalance, onRedeem, onReverse, stats, discountFor, J, HANDLERS };
