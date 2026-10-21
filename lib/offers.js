/* LUXORA Platform — Central Offers / Coupons / Discounts / Wallet engine.
   ONE reusable service (like registry.js / ai.js / modules.js) that any surface — storefront cart,
   checkout, platform subscription billing, AI metering, or a client API — calls to compute discounts,
   credits, free-shipping and coupon redemptions. Everything (types, scopes, channels, directions,
   funders, coupon kinds, limits) is DATA in meta_lists; new offer types/scope rules are added without
   code. Legacy per-store `promotions` are read too, so nothing that already works regresses. */
"use strict";
/* seed data (lib/seed/offers.json): data, not code — the registries are seeded from it */
const SEED_OFFERS = require("./seed/offers.json");

let _db = null;
const db = () => _db || (_db = require("./db.js"));
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };
const list = (name, dflt) => J((db().get("SELECT items i FROM meta_lists WHERE name=?", name) || {}).i, dflt);
const today = () => new Date().toISOString().slice(0, 10);
const r2 = n => +Number(n || 0).toFixed(2);

/* ---- registry SEED (INSERT OR IGNORE ⇒ editable in Data Studio, self-heals on upgrade) ---- */
/* notes that lived in the seed literal (now lib/seed/offers.json): */
/* behaviour is declared on the rows: a type's `pro` gate, `cart_wide` (applies without
   scoped items) and `absolute` (currency-bound); a channel that `includes_promotions` and
   `gates_pro`; how a scope `match`es items; a stacking policy's `blocks`; a coupon kind
   that is `new_customers_only` */
const REGISTRIES = SEED_OFFERS.REGISTRIES;

function seed() {
  const D = db();
  const ensure = (name, items) => D.run("INSERT OR IGNORE INTO meta_lists(name,label,items) VALUES(?,?,?)", name, name, JSON.stringify(items));
  for (const [k, v] of Object.entries(REGISTRIES)) ensure(k, v);
  /* existing installs: plain-name lists become rows that carry their behaviour; new fields
     reach rows that lack them (an operator's own values are never overwritten) */
  try {
    const reg = require("./registry.js");
    for (const n of ["offerChannels", "offerScopes", "couponKinds", "stackingPolicies"]) { reg.upgradeShape(n, REGISTRIES[n]); reg.addFields(n, REGISTRIES[n], ["includes_promotions", "gates_pro", "match", "item", "scope", "blocks", "new_customers_only"]); }
    /* the stacking value "any" was renamed "others" (it collided with a channel key) */
    const RENAMED = { any: "others" };
    try { const sp = reg.list("stackingPolicies"); if (Array.isArray(sp) && sp.some(r => r && RENAMED[r.blocks])) db().run("UPDATE meta_lists SET items=? WHERE name='stackingPolicies'", JSON.stringify(sp.map(r => (r && RENAMED[r.blocks] ? { ...r, blocks: RENAMED[r.blocks] } : r)))); } catch (e) { }
    reg.addFields("offerTypes", REGISTRIES.offerTypes, ["pro", "cart_wide", "absolute", "percentage", "uncapped_risk", "rank_weight"]);
  } catch (e) { }
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
      rules: J(o.rules, {}), funder: o.funder || require("./defaults.js").of("offerFunders"), funder_ref: o.funder_ref, brand_ref: o.brand_ref,
      min_amount: Number(o.min_amount) || 0, min_qty: Number(o.min_qty) || 0, max_discount: Number(o.max_discount) || 0,
      usage_limit: Number(o.usage_limit) || 0, used: Number(o.used) || 0, per_owner_limit: Number(o.per_owner_limit) || 0,
      stack_group: o.stack_group || "", stack_policy: o.stack_policy || "stack_with_others", name: o.name, owner: null });
  }
  if ((rowOf("offerChannels", channel) || {}).includes_promotions) {
    for (const p of C.all("SELECT * FROM promotions WHERE tenant_id=? AND status='active' AND (starts IS NULL OR starts<=?) AND (ends IS NULL OR ends>=?)", tenantId, now, now)) {
      const sc = J(p.scope, {}), rules = J(p.rules, {});
      if (p.code && !anyCode && p.code.toUpperCase() !== up) continue;
      out.push({ id: p.id, _src: "promotion", _row: p, code: p.code || null, type: p.type, direction: "discount", channel: require("./defaults.js").of("offerChannels"),
        value: Number(p.value) || 0, currency: null, scope_type: promoScope(sc),
        scope: sc, rules, funder: require("./defaults.js").of("offerFunders"), brand_ref: null, min_amount: rules.min || 0, min_qty: 0, max_discount: 0,
        usage_limit: 0, used: 0, per_owner_limit: 0, stack_group: "", stack_policy: "stack_with_others", name: p.name });
    }
  }
  return out;
}

/* a legacy promotion's scope is the first scope row whose declared scope field it carries */
function promoScope(sc) {
  const rows = listRows("offerScopes");
  const hit = rows.find(r => r.match !== "all" && (r.scope || []).some(f => sc && sc[f] != null && sc[f] !== ""));
  return hit ? hit.key : ((rows.find(r => r.match === "all") || { key: "store" }).key);
}
/* how a scope matches items is its row's: `all`, `in` (the item field is in the scope's
   listed values) or `taxonomy` (the item sits under the scope's node) */
function scopeItems(offer, items, C, tenantId) {
  const row = rowOf("offerScopes", offer.scope_type) || { match: "all" }, sc = offer.scope || {};
  const vals = [].concat(...(row.scope || []).map(f => (sc[f] == null ? [] : [].concat(sc[f]))));
  if (row.match === "in") return items.filter(i => vals.includes(i[row.item]));
  if (row.match === "taxonomy") {
    const nodeKey = vals[0]; if (!nodeKey) return [];
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
/* the vocabularies' behaviour rows, read per call (an operator's edit is live at once) */
const rowOf = (name, key) => (listRows(name).find(r => r.key === String(key)) || null);
function listRows(name) { const reg = require("./registry.js"); const l = reg.list(name); const seedRows = REGISTRIES[name] || []; return (Array.isArray(l) && l.length ? l : seedRows).map(x => (typeof x === "string" ? Object.assign({ key: x }, seedRows.find(sd => sd && sd.key === x) || {}) : x)); }
const typeIs = (type, flag) => !!(rowOf("offerTypes", type) || {})[flag];
function evaluate(ctx) {
  const D = db();
  const channel = ctx.channel || require("./defaults.js").of("offerChannels");
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
  const requireOffersPro = !!(rowOf("offerChannels", channel) || {}).gates_pro;
  const mods = require("./modules.js");
  const hasPro = require("./gates.js").on(ctx.tenantId, "offers.pro");
  let discount = 0, credits = 0, freeShip = false; const applied = [], redemptions = []; const usedGroups = {};
  offs = typeof ctx.rank === "function" ? offs.slice().sort(ctx.rank) : offs.sort((a, b) => (b.type && a.type ? 0 : 0) || (b.min_amount - a.min_amount));
  for (const o of offs) {
    if (typeIs(o.type, "pro") && requireOffersPro && !hasPro && o._src === "promotion") continue;
    /* currency guard: absolute-value types are only valid in their own currency; % / ratio / ship are currency-agnostic */
    if (typeIs(o.type, "absolute") && o.currency && currency && String(o.currency).toUpperCase() !== currency) continue;
    if (o.usage_limit && o.used >= o.usage_limit) continue;
    if (o.per_owner_limit && owner && o._src === "offer") { const n = D.get("SELECT COUNT(*) c FROM coupon_redemptions WHERE offer_id=? AND owner=? AND status='redeemed'", o.id, owner).c; if (n >= o.per_owner_limit) continue; }
    if (o.min_amount && amount < o.min_amount) continue;
    if (o.min_qty && qtyOf(items) < o.min_qty) continue;
    const blocks = (rowOf("stackingPolicies", o.stack_policy) || {}).blocks;
    if (blocks === "others" && applied.length) continue;
    if (blocks === "group" && o.stack_group && usedGroups[o.stack_group]) continue;
    if (applied.length >= maxStack) break;
    const its = scopeItems(o, items, D, ctx.tenantId);
    if (!its.length && !typeIs(o.type, "cart_wide")) continue;
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
      if ((rowOf("couponKinds", cp.kind) || {}).new_customers_only && owner) { const o = D.get("SELECT COUNT(*) c FROM orders WHERE owner=?", owner).c; if (o > 0) return { ok: false, reason: "New customers only" }; }
      return { ok: true, coupon: cp, code: c };
    }
    const offer = D.get("SELECT * FROM offers WHERE code=? AND status='active' AND (tenant_id=? OR tenant_id=0) AND (starts IS NULL OR starts<=?) AND (ends IS NULL OR ends>=?)", c, tenantId, today(), today());
    if (offer) { const blocked = ruled("coupons.offer", offer.id); if (blocked) return blocked; return { ok: true, code: c, offer }; }
  }
  // also accept legacy promotions or central auto codes via evaluate
  const anyEligible = eligible(tenantId, require("./defaults.js").of("offerChannels"), c, true).some(o => o.code === c);
  return anyEligible ? { ok: true, code: c } : { ok: false, reason: "Invalid or expired promo code" };
}
function redeem(ctx, result, ref) {
  const D = db();
  const owner = ctx.owner || "", tid = ctx.tenantId, oid = ref && ref.order_id, iid = ref && ref.invoice_id;
  for (const rd of (result.redemptions || [])) {
    const cp = rd.code ? findCoupon(tid, rd.code) : null;
    const offerId = rd.offer_id || (cp && cp.offer_id) || null;
    D.run("INSERT INTO coupon_redemptions(tenant_id,coupon_id,offer_id,code,order_id,invoice_id,owner,channel,amount,credits,offer_type,funder,funder_ref,brand_ref,unit,status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, 'redeemed')",
      tid, cp ? cp.id : null, offerId, rd.code, oid || null, iid || null, owner, ctx.channel || require("./defaults.js").of("offerChannels"), r2(rd.amount || 0), r2(rd.credits || 0), rd.type || "", rd.funder || require("./defaults.js").of("offerFunders"), rd.funder_ref || "", rd.brand_ref || "",
      String(rd.unit || ctx.currency || require("./defaults.js").currency(ctx.tenantId)).toUpperCase());
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
  const cur = (ctx.currency || require("./defaults.js").currency(ctx.tenantId)).toUpperCase();
  if (legacy > 0) credit(tid, owner, legacy, "reward", (ref && (ref.order_num || ref.note)) || "offer-credit", cur, ctx.channel || require("./defaults.js").of("offerChannels"), "offers");
  for (const [u, amt] of Object.entries(byUnit)) {
    if (u === cur || moneyUnit(u)) credit(tid, owner, amt, "cashback", (ref && (ref.order_num || ref.note)) || "offer-credit", u, ctx.channel || require("./defaults.js").of("offerChannels"), "offers");
    else ledgerEntry(tid, owner, u, "reward", amt, (ref && (ref.order_num || ref.note)) || "offer-credit", ctx.channel || require("./defaults.js").of("offerChannels"), "offers");
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
  /* the rewards and cashback this order credited are reversed — each a reversal linked to its journal */
  if (ref && ref.order_num) {
    const owner = (D.get("SELECT owner FROM orders WHERE id=?", oid) || {}).owner;
    const ins = require("./seed/wallet.json").operations.filter(o => o.direction === "in" && o.counter === "issuance").map(o => o.key);
    const js = owner ? D.all(`SELECT j.id FROM ledger_journals j JOIN ledger_postings p ON p.journal_id=j.id JOIN ledger_accounts a ON a.id=p.account_id JOIN wallet_instances w ON w.id=a.wallet_id
      WHERE j.tenant_id=? AND w.owner=? AND j.ref=? AND j.reverses IS NULL AND j.op IN (${ins.map(() => "?").join(",")}) AND NOT EXISTS (SELECT 1 FROM ledger_journals r WHERE r.reverses=j.id)`, tenantId, owner, String(ref.order_num), ...ins) : [];
    for (const j of js) { try { W().reverse(tenantId, j.id, "offers", "clawback: refund of " + ref.order_num); } catch (e) { console.error("offer clawback:", e.message); } }
  }
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
/* a unit is money when its Value class says so (lib/registry.js isMoney) */
const moneyUnit = u => require("./registry.js").isMoney(u);

/* ---- money: every credit and debit is a journal on the owner's wallet (lib/wallet.js owns the
   ledger; these are its callers' older names). `kind` is the wallet operation it posts under; a
   debit beyond what is available is refused, never clamped. ---- */
const W = () => require("./wallet.js");
/* a kind the wallet declares for this direction posts as itself; any other (a label from an older
   caller, or a kind of the other direction) as the wallet's default for the direction */
const opFor = (kind, dir) => (require("./seed/wallet.json").operations.some(o => o.key === kind && (o.direction === dir || o.direction === "either")) ? kind : W().defaultOp(dir));
function _bal(D, tid, owner) { const r = D.get("SELECT balance b FROM wallets WHERE tenant_id=? AND owner=?", tid, owner); return r ? +Number(r.b) : 0; }
function credit(tid, owner, amount, kind, ref, currency, channel, actor) {
  const amt = Number(amount) || 0; if (amt === 0) return { balance: _bal(db(), tid, owner) };
  if (!(amt > 0)) throw new Error("Credit amount must be positive");
  const w = W().walletFor(tid, owner, currency, opFor(kind, "in"));
  const out = W().post(tid, { op: opFor(kind, "in"), wallet: w.id, amount: amt.toFixed(W().unitOf(w.unit).decimals), ref, channel: channel || require("./defaults.js").of("offerChannels"), actor });
  return { balance: out.wallet.posted };
}
function debit(tid, owner, amount, kind, ref, currency, channel, actor) {
  const amt = Number(amount) || 0; if (amt === 0) return { balance: _bal(db(), tid, owner) };
  /* a debit only ever takes money out */
  if (!(amt > 0)) throw new Error("Debit amount must be positive");
  const w = W().walletFor(tid, owner, currency, opFor(kind, "out"));
  const out = W().post(tid, { op: opFor(kind, "out"), wallet: w.id, amount: amt.toFixed(W().unitOf(w.unit).decimals), ref, channel: channel || require("./defaults.js").of("offerChannels"), actor });
  return { balance: out.wallet.posted };
}
/* a non-money unit (points, coins, credits) moves in the owner's wallet for that unit */
function ledgerEntry(tid, owner, unit, kind, amount, ref, channel, actor) {
  const amt = Number(amount) || 0; if (!amt) return { balance: unitBalance(tid, owner, unit) };
  const code = String(unit || require("./defaults.js").currency(tid)).toUpperCase();
  const op = amt > 0 ? opFor(kind, "in") : opFor(kind, "out");
  const w = W().walletFor(tid, owner, code, op);
  const out = W().post(tid, { op, wallet: w.id, amount: Math.abs(amt).toFixed(W().unitOf(code).decimals), ref, channel: channel || require("./defaults.js").of("offerChannels"), actor });
  return { balance: out.wallet.posted, unit: code };
}
function unitBalance(tid, owner, unit) {
  const code = String(unit || require("./defaults.js").currency(tid)).toUpperCase();
  const w = db().get("SELECT id FROM wallet_instances WHERE tenant_id=? AND owner=? AND unit=? ORDER BY created_at, id LIMIT 1", tid, owner, code);
  return w ? W().balances(tid, owner, w.id).posted : 0;
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
