/* LUXORA Platform — vouchers (the Voucher domain): an instrument of value that is not money
   and not a gift card.

   A voucher is a bank voucher, a store credit note, a government benefit note, an employee
   benefit token — a face value that may be spent, issued by someone other than the shop: a
   bank, an organisation, a benefits programme. It differs from a coupon in who stands
   behind it and how it is funded: a coupon is the shop's own discount, a voucher is value
   someone else has set aside for the shopper.

   The voucher domain owns the voucher kinds (lib/seed/vouchers.json) — what a voucher is,
   who issues it, whether it can be partially spent, how long it lives. It issues through the
   Coupon domain's writer (lib/coupons.js), because a voucher travels as a code with a
   face value, and the coupon domain owns codes. The voucher domain never writes the
   coupons table itself; it asks the coupon domain to issue one and records what kind of
   voucher it was.

   A gift card is a voucher in the everyday sense, but it is a different domain
   (lib/giftcards.js) with a different life: a code, a holder, a wallet balance it pays
   into. The two never borrow each other's writer. */
"use strict";

const SEED = require("./seed/vouchers.json");

let _db = null;
const db = () => _db || (_db = require("./db.js"));
const S = v => String(v == null ? "" : v);
const registry = () => require("./registry.js");

/* ---------- the kinds ---------- */
/* A kind is a row: what the voucher is called, who issues it, whether it may be partly
   spent, how long it lives, and the coupon kind its code travels as. The kinds are seeded
   from lib/seed/vouchers.json and are editable in Data Studio; the code never names one. */
const REGISTRIES = SEED.REGISTRIES;
const kinds = () => {
  const l = registry().list("voucherKinds");
  const seedRows = REGISTRIES.voucherKinds || [];
  const rows = (Array.isArray(l) && l.length ? l : seedRows).map(x => (typeof x === "string" ? Object.assign({ key: x }, seedRows.find(sd => sd && sd.key === x) || {}) : x));
  return rows.map(x => Object.assign({ name: x.key }, x));
};
const kindOf = key => kinds().find(k => String(k.key) === String(key)) || null;
const kindKeys = () => kinds().map(k => String(k.key));

function seed() {
  const D = db();
  const ensure = (name, items) => D.run("INSERT OR IGNORE INTO meta_lists(name,label,items) VALUES(?,?,?)", name, name, JSON.stringify(items));
  for (const [k, v] of Object.entries(REGISTRIES)) ensure(k, v);
  try {
    const reg = registry();
    reg.upgradeShape("voucherKinds", REGISTRIES.voucherKinds);
    reg.addFields("voucherKinds", REGISTRIES.voucherKinds, ["issued_by", "partial_spend", "validity_days", "code_kind"]);
  } catch (e) { }
}

/* ---------- issuing ---------- */
/* The voucher domain asks the Coupon domain for the code: a voucher travels as a code with a
   face value, and the coupon domain owns codes. The voucher's own record — what kind it is,
   who issued it, what it is worth — is written here, beside the code it travels on. */
function issue(tenantId, owner, grant, src) {
  const kind = kindOf(grant.voucher_kind) || kindOf(kindKeys()[0]);
  if (!kind) return null;
  const s = src || {};
  const currency = grant.unit || require("./defaults.js").currency(tenantId);
  const value = Number(grant.qty) || 0;
  const r = require("./coupons.js").issue(tenantId, {
    count: 1, kind: kind.code_kind, offer_id: s.offer_id || null,
    funder: s.funder || kind.issued_by || "self", funder_ref: s.funder_ref || kind.issued_by || "",
    value, currency,
    max_uses: Number(grant.max_uses) || 1, per_owner_limit: Number(grant.per_owner_limit) || 1,
    issued_to: owner || "", batch: "voucher", note: "issued as a " + kind.key,
    ends: grant.days ? new Date(Date.now() + Number(grant.days) * 86400000).toISOString().slice(0, 10) : null
  });
  if (!r || !r.code) return null;
  /* the voucher's own record: what it is, who stands behind it, what it is worth */
  const D = db();
  try {
    D.run(`INSERT INTO vouchers(tenant_id,code,kind,issued_by,offer_id,value,currency,issued_to,batch,starts,ends,status,note)
      VALUES(?,?,?,?,?,?,?,?,?,?,?, 'active',?)`, tenantId, r.code, kind.key, kind.issued_by || "", s.offer_id || null, value, String(currency).toUpperCase(),
      owner || "", "voucher", null, grant.days ? new Date(Date.now() + Number(grant.days) * 86400000).toISOString().slice(0, 10) : null, "issued as a " + kind.key);
  } catch (e) { }
  return { kind: "voucher", entity: "voucher", code: r.code, voucher_kind: kind.key };
}
/* the incentive kernel asks this domain to issue a voucher */
function issueAsGrant(tenantId, owner, grant, src) {
  return issue(tenantId, owner, grant, src);
}

/* ---------- listing ---------- */
function list(tenantId, filter) {
  const f = filter || {};
  return db().all("SELECT * FROM vouchers WHERE tenant_id=? ORDER BY id DESC LIMIT 500", tenantId)
    .filter(v => (!f.kind || v.kind === f.kind) && (!f.status || v.status === f.status));
}
function of(tenantId, code) {
  return db().get("SELECT * FROM vouchers WHERE tenant_id=? AND code=?", tenantId, String(code || "").trim().toUpperCase());
}

/* ---------- the offer that issues a voucher when it is bought ---------- */
/* An offer of type voucher_issue grants a voucher worth the offer's value, once the cart has
   reached the offer's minimum. The math is here, with the rest of the voucher domain. */
const rowOf = o => (o && o._row) || {};
const unitOf = o => S(rowOf(o).economic_unit || o.currency || require("./defaults.js").currency(o.tenant_id)).toUpperCase();
function grantOf(o) {
  const r = o.rules || {};
  return { benefit: "voucher", unit: unitOf(o), qty: Number(r.qty != null ? r.qty : o.value) || 0, tier: r.tier || "", days: Number(r.days || 0) || 0, scope: o.scope || {}, ref: r.ref || o.code || "" };
}
function offerHandler(o, its, amt) {
  if (amt < (Number(o.min_amount) || 0)) return {};
  const kinds = kindKeys();
  const k = kindOf(o.rules.voucher_kind) ? o.rules.voucher_kind : (kinds[0] || "");
  return { grant: Object.assign(grantOf(o), { kind: "voucher", voucher_kind: k }) };
}

/* ---------- registration ---------- */
function register() {
  const g = require("./grants.js");
  g.registerGrant("voucher", issueAsGrant);
  g.registerHandler("voucher_issue", offerHandler);
  return 1;
}

module.exports = { seed, register, REGISTRIES, kinds, kindOf, kindKeys, issue, issueAsGrant, offerHandler, list, of };

/* this domain registers itself the moment it is loaded */
register();
