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
  const out = [];
  const rows = C.all(`SELECT * FROM offers WHERE status='active' AND channel IN (?, 'any')
    AND (starts IS NULL OR starts<=?) AND (ends IS NULL OR ends>=?) AND (tenant_id=? ${allowGlobal ? "OR tenant_id=0" : ""})
    ORDER BY priority DESC, value DESC`, channel, now, now, tenantId);
  for (const o of rows) {
    if (o.code && o.code.toUpperCase() !== up) continue;
    out.push({ id: o.id, _src: "offer", code: o.code || null, type: o.type, direction: o.direction || "discount", channel: o.channel,
      value: Number(o.value) || 0, currency: o.currency, scope_type: o.scope_type || "store", scope: J(o.scope_value, {}),
      rules: J(o.rules, {}), funder: o.funder || "self", funder_ref: o.funder_ref, brand_ref: o.brand_ref,
      min_amount: Number(o.min_amount) || 0, min_qty: Number(o.min_qty) || 0, max_discount: Number(o.max_discount) || 0,
      usage_limit: Number(o.usage_limit) || 0, used: Number(o.used) || 0, per_owner_limit: Number(o.per_owner_limit) || 0,
      stack_group: o.stack_group || "", stack_policy: o.stack_policy || "stack_with_others", name: o.name, owner: null });
  }
  if (channel === "commerce") {
    for (const p of C.all("SELECT * FROM promotions WHERE tenant_id=? AND status='active' AND (starts IS NULL OR starts<=?) AND (ends IS NULL OR ends>=?)", tenantId, now, now)) {
      const sc = J(p.scope, {}), rules = J(p.rules, {});
      if (p.code && p.code.toUpperCase() !== up) continue;
      out.push({ id: p.id, _src: "promotion", code: p.code || null, type: p.type, direction: "discount", channel: "commerce",
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
function evaluate(ctx) {
  const D = db();
  const channel = ctx.channel || "commerce";
  const amount = Number(ctx.amount != null ? ctx.amount : subOf(ctx.items || []));
  const coupon = ctx.coupon;
  const items = (ctx.items || []).map(i => ({ id: i.id, dept: i.dept, brand: i.brand, node_id: i.node_id, price: Number(i.price != null ? i.price : i.p) || 0, qty: Number(i.qty) || 1 }));
  if (!items.length && amount > 0) items.push({ id: "__base", dept: "", brand: "", node_id: null, price: amount, qty: 1 });
  const maxStack = ctx.stackMax != null ? ctx.stackMax : 5;
  let offs = eligible(ctx.tenantId, channel, coupon, ctx.allowGlobal !== false);
  const requireOffersPro = channel === "commerce";
  const mods = require("./modules.js");
  const hasPro = mods.hasCap(ctx.tenantId, "offersPro");
  let discount = 0, credits = 0, freeShip = false; const applied = [], redemptions = []; const usedGroups = {};
  offs = offs.sort((a, b) => (b.type && a.type ? 0 : 0) || (b.min_amount - a.min_amount));
  for (const o of offs) {
    if (["bogo", "bundle_price", "multi_buy", "buy_x_get_y", "x_for_y"].includes(o.type) && requireOffersPro && !hasPro && o._src === "promotion") continue;
    if (o.usage_limit && o.used >= o.usage_limit) continue;
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
    if (d > 0 || res.credits || res.freeShip) {
      applied.push({ id: o.id, src: o._src, name: o.name, type: o.type, direction: o.direction, code: o.code || undefined, amount: d || 0, credits: r2(res.credits || 0), freeShip: !!res.freeShip, funder: o.funder });
      if (o.code) redemptions.push({ offer_id: o._src === "offer" ? o.id : null, code: o.code, amount: d || (res.credits || 0), funder: o.funder, funder_ref: o.funder_ref, brand_ref: o.brand_ref });
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
    if (cp) {
      if (cp.max_uses && cp.used >= cp.max_uses) return { ok: false, reason: "Coupon fully redeemed" };
      if (cp.per_owner_limit && owner) { const n = D.get("SELECT COUNT(*) c FROM coupon_redemptions WHERE coupon_id=? AND owner=?", cp.id, owner).c; if (n >= cp.per_owner_limit) return { ok: false, reason: "Coupon already used on this account" }; }
      if (cp.kind === "first_order" && owner) { const o = D.get("SELECT COUNT(*) c FROM orders WHERE owner=?", owner).c; if (o > 0) return { ok: false, reason: "New customers only" }; }
      return { ok: true, coupon: cp, code: c };
    }
    const offer = D.get("SELECT * FROM offers WHERE code=? AND status='active' AND (tenant_id=? OR tenant_id=0) AND (starts IS NULL OR starts<=?) AND (ends IS NULL OR ends>=?)", c, tenantId, today(), today());
    if (offer) return { ok: true, code: c, offer };
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
    D.run("INSERT INTO coupon_redemptions(tenant_id,coupon_id,offer_id,code,order_id,invoice_id,owner,channel,amount,funder,funder_ref,brand_ref) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
      tid, cp ? cp.id : null, rd.offer_id || (cp && cp.offer_id) || null, rd.code, oid || null, iid || null, owner, ctx.channel || "commerce", r2(rd.amount), rd.funder || "self", rd.funder_ref || "", rd.brand_ref || "");
    if (cp) { D.run("UPDATE coupons SET used=used+1 WHERE id=?", cp.id); if (cp.max_uses && (cp.used + 1) >= cp.max_uses) D.run("UPDATE coupons SET status='exhausted' WHERE id=?", cp.id); }
    if (rd.offer_id) D.run("UPDATE offers SET used=used+1 WHERE id=?", rd.offer_id);
  }
  if (result.credits > 0) credit(tid, owner, result.credits, "reward", ref && (ref.order_num || ref.note) || "offer-credit", ctx.currency || "USD", ctx.channel || "commerce", "offers");
  return { ok: true };
}

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
  D.run(`INSERT INTO wallets(tenant_id,owner,balance,updated_at) VALUES(?,?,?,datetime('now'))
         ON CONFLICT(tenant_id,owner) DO UPDATE SET balance=MAX(0, balance - ?), updated_at=datetime('now')`, tid, owner, amt, amt);
  const after = _bal(D, tid, owner);
  D.run("INSERT INTO wallet_entries(tenant_id,owner,currency,kind,amount,balance_after,ref,channel,actor) VALUES(?,?,?,?,?,?,?,?,?)",
    tid, owner, currency || "USD", kind || "redeem", -amt, after, ref || "", channel || "commerce", actor || "system");
  return { balance: after };
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

module.exports = { REGISTRIES, seed, evaluate, eligible, validateCoupon, findCoupon, redeem, credit, debit, ledger, stats, discountFor, J, HANDLERS };
