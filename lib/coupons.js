/* LUXORA Platform — coupons (the Coupon domain): a code that carries a value.

   A coupon is a code a shopper types at the cart. It is issued (staff issue one, a bulk
   batch is generated, an incentive grants one), it is validated at the cart (is it live,
   has it been used too often, has this shopper used it too often, does a rule block it),
   it is redeemed at checkout into the redemption ledger, and it is voided when an order
   is refunded — the code's use is taken back with the discount.

   Everything a coupon is lives here: the `coupons` table, the `coupon_redemptions` ledger,
   the coupon kinds, the code prefix, the redemption writer and the clawback. The offers
   engine asks this domain whether a code is good (findCoupon, validateCoupon) and this
   domain writes the redemption; the incentive kernel asks this domain to issue a code when
   an offer grants one.

   A voucher is a coupon of a declared kind — a bank voucher is a coupon whose kind says
   so — and the Voucher domain (lib/vouchers.js) names its own kinds and issues through
   this domain's writer. Nothing here knows what a voucher is.

   The kinds are data (lib/seed/coupons.json), the code prefix is a store setting, and the
   redemption ledger's life is the `redemption` state machine. */
"use strict";

const crypto = require("crypto");
const SEED = require("./seed/coupons.json");

let _db = null;
const db = () => _db || (_db = require("./db.js"));
const S = v => String(v == null ? "" : v);
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };
const today = () => new Date().toISOString().slice(0, 10);
const r2 = n => +Number(n || 0).toFixed(2);
const registry = () => require("./registry.js");
const states = () => require("./states.js");
const defaults = () => require("./defaults.js");

/* ---------- the kinds ---------- */
/* a kind is a row: what it is called, and the rules it carries (a new-customers-only kind,
   a bulk kind, a single-use kind). The kinds are seeded from lib/seed/coupons.json and are
   editable in Data Studio; the code never names one. */
const REGISTRIES = SEED.REGISTRIES;
const kinds = () => {
  const l = registry().list("couponKinds");
  const seedRows = REGISTRIES.couponKinds || [];
  const rows = (Array.isArray(l) && l.length ? l : seedRows).map(x => (typeof x === "string" ? Object.assign({ key: x }, seedRows.find(sd => sd && sd.key === x) || {}) : x));
  return rows.map(x => Object.assign({ name: x.key }, x));
};
const kindOf = key => kinds().find(k => String(k.key) === String(key)) || null;
const kindKeys = () => kinds().map(k => String(k.key));

function seed() {
  const D = db();
  const ensure = (name, items) => require("./registry.js").ensureList(name, name, items);
  for (const [k, v] of Object.entries(REGISTRIES)) ensure(k, v);
  try {
    const reg = registry();
    reg.upgradeShape("couponKinds", REGISTRIES.couponKinds);
    reg.addFields("couponKinds", REGISTRIES.couponKinds, ["new_customers_only"]);
  } catch (e) { }
}

/* ---------- the code ---------- */
/* the prefix is the store's setting (its offers.couponCodePrefix); a bulk batch gets one
   batch label and one prefix for the whole lot */
function prefixFor(tenantId) {
  try { const st = require("./settings.js").load(tenantId); return S((st.offers && st.offers.couponCodePrefix) || ""); } catch (e) { return ""; }
}
const randomCode = prefix => (S(prefix) || "CPN") + "-" + crypto.randomBytes(3).toString("hex");

/* ---------- issuing: the one writer for `coupons` ---------- */
function issue(tenantId, body) {
  const b = body || {}; const Db = db();
  const ks = kindKeys(), funders = registry().keys("offerFunders");
  const kind = ks.includes(S(b.kind)) ? S(b.kind) : defaults().of("couponKinds");
  if (!kind || !ks.includes(kind)) return { error: "No coupon kind is configured", code: 422 };
  const funder = funders.includes(S(b.funder)) ? S(b.funder) : defaults().of("offerFunders");
  const n = Math.min(1000, Math.max(1, Number(b.count) || 1));
  const batch = S(b.batch || (n > 1 ? "B" + Date.now().toString(36) : ""));
  const prefix = S(b.prefix || "") || prefixFor(tenantId);
  const made = [], errors = [];
  for (let i = 0; i < n; i++) {
    const code = S(n === 1 && b.code ? b.code : randomCode(prefix)).toUpperCase();
    try {
      Db.run(`INSERT INTO coupons(tenant_id,code,offer_id,funder,funder_ref,brand_ref,kind,value,currency,max_uses,per_owner_limit,issued_to,batch,starts,ends,status,note)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, 'active',?)`, tenantId, code, b.offer_id ? Number(b.offer_id) : null, funder, S(b.funder_ref || ""), S(b.brand_ref || ""),
        kind, Number(b.value) || 0, S(b.currency || defaults().currency(tenantId)).toUpperCase(), Number(b.max_uses) || 1, Number(b.per_owner_limit) || 1, S(b.issued_to || ""), batch,
        b.starts || null, b.ends || null, S(b.note || (n > 1 ? "bulk" : "")));
      made.push(code);
    } catch (e) { if (n === 1) return { error: "Duplicate code", code: 409 }; errors.push(code); i--; if (errors.length > n * 3) break; }
  }
  return { ok: true, batch, count: made.length, codes: made, code: made[0] };
}

/* ---------- finding and validating ---------- */
function find(tenantId, code) {
  const D = db(); const c = String(code || "").trim().toUpperCase(); if (!c) return null;
  return D.get("SELECT * FROM coupons WHERE status='active' AND code=? AND (tenant_id=? OR tenant_id=0) AND (starts IS NULL OR starts<=?) AND (ends IS NULL OR ends>=?)", c, tenantId, today(), today());
}
/* is this code good, and why not */
function validate(tenantId, code, owner) {
  const D = db(); const c = String(code || "").trim().toUpperCase();
  if (c) {
    const cp = find(tenantId, c);
    /* a coupon code, and the offer behind it, are subject to the applicability rules */
    const rules = require("./rules.js"); const rctx = rules.at("coupons.code", tenantId);
    const ruled = (point, id) => { const d = rules.decideAt(point, String(id), rctx); return d.ok ? null : { ok: false, reason: "This code is not available here" + (d.reasons.length ? " — " + d.reasons.join("; ") : "") }; };
    if (cp) {
      const blocked = ruled("coupons.code", cp.code) || (cp.offer_id ? ruled("coupons.offer", cp.offer_id) : null);
      if (blocked) return blocked;
      if (cp.max_uses && cp.used >= cp.max_uses) return { ok: false, reason: "Coupon fully redeemed" };
      if (cp.per_owner_limit && owner) { const n = D.get("SELECT COUNT(*) c FROM coupon_redemptions WHERE coupon_id=? AND owner=?", cp.id, owner).c; if (n >= cp.per_owner_limit) return { ok: false, reason: "Coupon already used on this account" }; }
      const kind = kindOf(cp.kind);
      if (kind && kind.new_customers_only && owner) { const o = D.get("SELECT COUNT(*) c FROM orders WHERE owner=?", owner).c; if (o > 0) return { ok: false, reason: "New customers only" }; }
      return { ok: true, coupon: cp, code: c };
    }
    const offer = D.get("SELECT * FROM offers WHERE code=? AND status='active' AND (tenant_id=? OR tenant_id=0) AND (starts IS NULL OR starts<=?) AND (ends IS NULL OR ends>=?)", c, tenantId, today(), today());
    if (offer) { const blocked = ruled("coupons.offer", offer.id); if (blocked) return blocked; return { ok: true, code: c, offer }; }
  }
  /* an offer's own code may be applied without a coupon row (a coded exchange) */
  const anyEligible = require("./offers.js").eligible(tenantId, defaults().of("offerChannels"), c, true).some(o => o.code === c);
  return anyEligible ? { ok: true, code: c } : { ok: false, reason: "Invalid or expired promo code" };
}

/* ---------- the redemption ledger ---------- */
/* a redemption is what a code was worth on one order: its amount, its credits, the offer it
   came from and the funder who bears it. Its life is the `redemption` state machine. */
function recordRedemption(tenantId, row) {
  const D = db();
  const id = Number(D.run(`INSERT INTO coupon_redemptions(tenant_id,coupon_id,offer_id,code,order_id,invoice_id,owner,channel,amount,credits,offer_type,funder,funder_ref,brand_ref,unit,status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, 'redeemed')`,
    tenantId, row.coupon_id || null, row.offer_id || null, row.code || null, row.order_id || null, row.invoice_id || null, S(row.owner || ""),
    S(row.channel || defaults().of("offerChannels")), r2(row.amount || 0), r2(row.credits || 0), S(row.offer_type || ""),
    S(row.funder || defaults().of("offerFunders")), S(row.funder_ref || ""), S(row.brand_ref || ""), S(row.unit || "").toUpperCase()).lastInsertRowid);
  if (row.coupon_id) { D.run("UPDATE coupons SET used=used+1 WHERE id=?", row.coupon_id); const cp = D.get("SELECT used,max_uses FROM coupons WHERE id=?", row.coupon_id); if (cp && cp.max_uses && (cp.used + 1) >= cp.max_uses) D.run("UPDATE coupons SET status='exhausted' WHERE id=?", row.coupon_id); }
  if (row.offer_id) D.run("UPDATE offers SET used=used+1 WHERE id=?", row.offer_id);
  return id;
}
/* a reservation: a code held before the order is placed, released when it is not */
function recordReservation(tenantId, row) {
  const D = db();
  const id = Number(D.run(`INSERT INTO coupon_redemptions(tenant_id,coupon_id,offer_id,code,order_id,owner,channel,amount,credits,offer_type,funder,funder_ref,brand_ref,status,meta)
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?, 'reserved',?)`, tenantId, null, row.offer_id || null, row.code || null, row.order_id ? Number(row.order_id) : null, S(row.owner || ""),
    S(row.channel || defaults().of("offerChannels")), r2(row.amount || 0), r2(row.credits || 0), S(row.offer_type || ""), S(row.funder || defaults().of("offerFunders")), S(row.funder_ref || ""), S(row.brand_ref || ""),
    JSON.stringify({ reserved_at: new Date().toISOString(), expires: new Date(Date.now() + (Number(row.ttl_minutes) || 30) * 60000).toISOString(), unit: S(row.unit || "") })).lastInsertRowid);
  return id;
}
/* take a redemption back: the code's use and the offer's use return, the row is voided */
function voidRedemption(tenantId, id, reason) {
  const D = db(); const r = D.get("SELECT * FROM coupon_redemptions WHERE id=? AND tenant_id=?", Number(id), tenantId);
  if (!r) return { ok: false, reason: "Unknown redemption" };
  if (r.coupon_id) { D.run("UPDATE coupons SET used=MAX(0,used-1) WHERE id=?", r.coupon_id); D.run("UPDATE coupons SET status='active' WHERE id=? AND status='exhausted'", r.coupon_id); }
  if (r.offer_id) D.run("UPDATE offers SET used=MAX(0,used-1) WHERE id=?", r.offer_id);
  D.run("UPDATE coupon_redemptions SET status=?, meta=? WHERE id=?", states().first("redemption", "void"), JSON.stringify(Object.assign(J(r.meta, {}), { void_reason: S(reason || "") })), r.id);
  return { ok: true };
}
/* every redemption of one order, voided together when the order is refunded */
function voidOrder(tenantId, orderId, reason) {
  const D = db(); const rows = D.all("SELECT * FROM coupon_redemptions WHERE tenant_id=? AND order_id=? AND status='redeemed'", tenantId, orderId);
  for (const r of rows) voidRedemption(tenantId, r.id, reason);
  return { ok: true, voided: rows.length };
}

/* ---------- the lifecycle sweep ---------- */
/* a code past its end is no longer good; the sweep runs whenever the codes are listed */
function sweep(tenantId) {
  try { db().run("UPDATE coupons SET status='expired' WHERE tenant_id=? AND status='active' AND ends IS NOT NULL AND ends<?", tenantId, today()); } catch (e) { }
  return true;
}

/* ---------- listing ---------- */
function list(tenantId, filter) {
  const f = filter || {};
  const D = db();
  sweep(tenantId);
  const rows = D.all("SELECT * FROM coupons WHERE tenant_id=? OR tenant_id=0 ORDER BY id DESC LIMIT 500", tenantId);
  return rows.filter(c => (!f.kind || c.kind === f.kind) && (!f.status || c.status === f.status));
}
function redemptions(tenantId, limit) {
  const n = Math.min(500, Number(limit) || 200);
  /* the platform view asks for every store's redemptions (tenantId 0); a store asks for its own */
  return Number(tenantId) ? db().all("SELECT * FROM coupon_redemptions WHERE tenant_id=? ORDER BY id DESC LIMIT ?", tenantId, n)
    : db().all("SELECT * FROM coupon_redemptions ORDER BY id DESC LIMIT ?", n);
}
function analytics(tenantId) {
  const D = db();
  const by = t => D.all(`SELECT ${t} k, COUNT(*) n, COALESCE(SUM(amount),0) discount, COALESCE(SUM(credits),0) credits FROM coupon_redemptions WHERE ${tenantId ? "tenant_id=?" : "1=1"} AND status='redeemed' GROUP BY ${t} ORDER BY n DESC`, ...(tenantId ? [tenantId] : []));
  const tot = D.get(`SELECT COUNT(*) n, COALESCE(SUM(amount),0) discount, COALESCE(SUM(credits),0) credits FROM coupon_redemptions WHERE ${tenantId ? "tenant_id=?" : "1=1"} AND status='redeemed'`, ...(tenantId ? [tenantId] : []));
  return { totals: { redemptions: tot.n, discount: r2(tot.discount), credits: r2(tot.credits) }, byCode: by("code"), byType: by("offer_type"), byFunder: by("funder") };
}
function stats(tenantId) {
  const D = db();
  const byFunder = D.all(`SELECT funder, SUM(amount) amount, COUNT(*) n FROM coupon_redemptions ${tenantId ? "WHERE tenant_id=?" : "WHERE 1=1"} GROUP BY funder`, ...(tenantId ? [tenantId] : []));
  return { byFunder: byFunder.map(r => ({ funder: r.funder, amount: r2(r.amount), redemptions: r.n })) };
}

/* ---------- the incentive kernel asks this domain to issue a code ---------- */
/* An offer that grants a coupon (a voucher, a promo code) names the kind and the value; the
   code is written here, by the one writer, and the kernel never learns what a code is. */
function issueAsGrant(tenantId, owner, grant, src) {
  const s = src || {};
  const r = issue(tenantId, {
    count: 1, kind: grant.coupon_kind, offer_id: s.offer_id || null,
    funder: s.funder || defaults().of("offerFunders"), funder_ref: s.funder_ref || "",
    value: Number(grant.qty) || 0, currency: grant.unit || defaults().currency(tenantId), max_uses: 1, per_owner_limit: 1,
    issued_to: owner || "", batch: "goip", note: "granted by an offer",
    ends: grant.days ? new Date(Date.now() + Number(grant.days) * 86400000).toISOString().slice(0, 10) : null
  });
  return r && r.code ? { kind: "coupon", entity: "coupon", code: r.code } : null;
}

/* ---------- the offer that issues a code when it is bought ---------- */
/* An offer of type voucher_issue grants a code worth the offer's value, once the cart has
   reached the offer's minimum. The math is here, with the rest of the coupon domain. */
const rowOf = o => (o && o._row) || {};
const unitOf = o => S(rowOf(o).economic_unit || o.currency || defaults().currency(o.tenant_id)).toUpperCase();
function grantOf(o) {
  const r = o.rules || {};
  return { benefit: "voucher", unit: unitOf(o), qty: Number(r.qty != null ? r.qty : o.value) || 0, tier: r.tier || "", days: Number(r.days || 0) || 0, scope: o.scope || {}, ref: r.ref || o.code || "" };
}
function offerHandler(o, its, amt) {
  if (amt < (Number(o.min_amount) || 0)) return {};
  const k = kindOf(o.rules.coupon_kind) ? o.rules.coupon_kind : kindKeys()[0];
  return { grant: Object.assign(grantOf(o), { kind: "coupon", coupon_kind: k }) };
}

/* ---------- registration ---------- */
function register() {
  const g = require("./grants.js");
  g.registerGrant("coupon", issueAsGrant);
  g.registerHandler("coupon_issue", offerHandler);
  return 1;
}

module.exports = { seed, register, REGISTRIES, kinds, kindOf, kindKeys, issue, issueAsGrant, offerHandler, find, validate,
  recordRedemption, recordReservation, voidRedemption, voidOrder, list, redemptions, analytics, stats, sweep };

/* this domain registers itself the moment it is loaded: the incentive kernel learns that a
   coupon is issued here, and the offers engine learns the math of a coupon offer */
register();
