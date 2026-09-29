/* LUXORA Platform — Universal Commerce registries.
   Every status, kind, type, tier and category the commerce entities reference is
   a row in meta_lists, editable at runtime from Data Studio. Nothing is an enum
   in code: add a quick-commerce store kind, a fintech payout status, a B2B
   document type or a buyer-claim state here (or in the console) and every
   dropdown, every validation option and every state machine that reads the
   registry follows on the next request. This is the platform's Knowledge-Once
   rule applied to the commerce capability set. No vendor name appears in any
   list — these are the platform's own vocabularies. */
"use strict";

const db = () => require("./db.js");
const J = (v, d) => { try { return v == null || v === "" ? (d == null ? [] : d) : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d == null ? [] : d; } };

/* registries are { name, label, items[] }; items are plain strings or {key,name} */
const REG = {
  /* ---------- Quick-commerce ---------- */
  qcStoreKinds: { label: "QC · Store kinds", items: ["dark_store", "micro_warehouse", "partner_store", "pickup_point", "cloud_store"] },
  qcStoreStatuses: { label: "QC · Store statuses", items: ["active", "paused", "offline", "onboarding"] },
  qcSlotStatuses: { label: "QC · Slot statuses", items: ["open", "filling", "full", "closed", "cancelled"] },
  qcAreaStatuses: { label: "QC · Service-area statuses", items: ["active", "inactive", "restricted"] },
  qcInvStatuses: { label: "QC · Store-inventory statuses", items: ["active", "low", "out", "blocked"] },
  qcVehicles: { label: "QC · Rider vehicles", items: ["bicycle", "scooter", "motorbike", "van", "car", "on_foot"] },
  qcRiderStatuses: { label: "QC · Rider statuses", items: ["offline", "online", "assigned", "on_delivery", "break"] },
  qcDispatchStatuses: { label: "QC · Dispatch statuses", items: ["assigned", "out_for_delivery", "delivered", "failed", "cancelled"] },
  qcDeliveryKinds: { label: "QC · Delivery kinds", items: ["standard", "express", "instant", "scheduled", "click_and_collect"] },

  /* ---------- Fintech ---------- */
  finUpiStatuses: { label: "Fin · UPI statuses", items: ["active", "pending_verification", "suspended", "failed"] },
  finCollectStatuses: { label: "Fin · UPI collect statuses", items: ["initiated", "pending", "success", "failed", "expired", "cancelled"] },
  finQrKinds: { label: "Fin · QR kinds", items: ["upi", "bharatqr", "static", "dynamic", "order", "merchant"] },
  finQrStatuses: { label: "Fin · QR statuses", items: ["active", "paused", "expired", "revoked"] },
  finLinkStatuses: { label: "Fin · Payment-link statuses", items: ["issued", "viewed", "paid", "expired", "cancelled", "failed"] },
  finMandateFrequencies: { label: "Fin · Mandate frequencies", items: ["onetime", "weekly", "monthly", "quarterly", "yearly", "asperbill"] },
  finMandateStatuses: { label: "Fin · Mandate statuses", items: ["registered", "active", "paused", "revoked", "failed", "completed"] },
  finEscrowStatuses: { label: "Fin · Escrow statuses", items: ["held", "released", "refunded", "disputed", "cancelled"] },
  finSplitStatuses: { label: "Fin · Split statuses", items: ["pending", "settled", "failed", "reversed"] },
  finKycKinds: { label: "Fin · KYC kinds", items: ["individual", "proprietor", "partnership", "private_ltd", "public_ltd", "llp", "trust", "society"] },
  finKycDocs: { label: "Fin · KYC documents", items: ["pan", "aadhaar", "passport", "voter_id", "driving_licence", "gstin_cert", "company_reg", "bank_statement", "utility_bill"] },
  finKycDocStatuses: { label: "Fin · KYC doc statuses", items: ["unverified", "pending", "approved", "rejected"] },
  finKycStatuses: { label: "Fin · KYC statuses", items: ["pending", "min_kyc", "full_kyc", "verified", "rejected", "expired"] },
  finPayoutStatuses: { label: "Fin · Payout statuses", items: ["queued", "processing", "success", "failed", "reversed", "cancelled"] },
  finBillerCategories: { label: "Fin · Biller categories (BBPS)", items: ["electricity", "water", "gas", "broadband", "landline", "mobile_postpaid", "dth", "cable_tv", "insurance", "loan_emi", "credit_card", "rent", "education", "donation", "fastag", "lpg"] },
  finBillStatuses: { label: "Fin · Bill-payment statuses", items: ["initiated", "pending", "success", "failed", "refunded"] },
  finOperators: { label: "Fin · Mobile/DTH operators", items: ["jio", "airtel", "vi", "bsnl", "mtnl", "dish_tv", "tata_sky", "d2h", "sun_direct", "videocon"] },
  finCircles: { label: "Fin · Telecom circles", items: ["national", "delhi", "mumbai", "kolkata", "chennai", "karnataka", "maharashtra", "gujarat", "rajasthan", "up_east", "up_west", "west_bengal", "tamil_nadu", "kerala", "andhra_pradesh", "telangana", "punjab", "haryana", "bihar", "jharkhand", "odisha", "assam", "mp", "cg", "hp", "jk", "north_east"] },
  finRechargeKinds: { label: "Fin · Recharge kinds", items: ["mobile", "dth", "broadband", "fastag", "metro"] },
  finRechargeStatuses: { label: "Fin · Recharge statuses", items: ["initiated", "pending", "success", "failed", "refunded"] },
  finBnplStatuses: { label: "Fin · BNPL statuses", items: ["inactive", "active", "suspended", "closed", "defaulted"] },
  finEmiStatuses: { label: "Fin · EMI statuses", items: ["upcoming", "due", "paid", "overdue", "failed", "settled"] },
  finLoanStatuses: { label: "Fin · Loan statuses", items: ["applied", "under_review", "approved", "rejected", "disbursed", "closed", "defaulted"] },
  finInsuranceStatuses: { label: "Fin · Insurance statuses", items: ["quoted", "active", "lapsed", "cancelled", "claimed", "matured"] },
  finVoucherStatuses: { label: "Fin · Voucher statuses", items: ["issued", "active", "redeemed", "expired", "cancelled"] },

  /* ---------- Marketplace ---------- */
  mktBusinessTypes: { label: "Mkt · Business types", items: ["proprietorship", "partnership", "private_limited", "public_limited", "llp", "huf", "society", "trust", "foreign_company"] },
  mktOnboardingStatuses: { label: "Mkt · Onboarding statuses", items: ["submitted", "documents_pending", "verification", "approved", "rejected", "suspended"] },
  mktConditions: { label: "Mkt · Offer conditions", items: ["new", "renewed", "refurbished", "used", "open_box", "damaged"] },
  mktFulfillment: { label: "Mkt · Fulfilment channels", items: ["fbm", "fba", "seller_fulfilled_prime", "qcommerce", "dropship"] },
  mktOfferStatuses: { label: "Mkt · Offer statuses", items: ["active", "inactive", "suspended", "buybox_revoked"] },
  mktFbaStatuses: { label: "Mkt · FBA inbound statuses", items: ["created", "in_transit", "receiving", "received", "closed", "cancelled"] },
  mktTiers: { label: "Mkt · Seller tiers", items: ["standard", "growth", "premium", "gold", "platinum"] },
  mktClaimKinds: { label: "Mkt · Buyer-claim kinds", items: ["atoz", "product_not_as_described", "damaged", "wrong_item", "never_arrived", "return_refund", "warranty"] },
  mktClaimStatuses: { label: "Mkt · Buyer-claim statuses", items: ["opened", "under_review", "evidence_requested", "evidence_submitted", "deciding", "resolved_buyer", "resolved_seller", "closed"] },
  mktSmartGrades: { label: "Mkt · Smart-fulfilment grades", items: ["a_plus", "a", "b", "c", "d"] },
  mktSmartStatuses: { label: "Mkt · Smart-fulfilment statuses", items: ["enrolled", "probation", "suspended", "opted_out"] },
  mktAdKinds: { label: "Mkt · Sponsored ad kinds", items: ["sponsored_product", "sponsored_brand", "sponsored_display", "sponsored_brand_video", "dsp", "store_spotlight"] },
  mktCreativeStatuses: { label: "Mkt · Creative statuses", items: ["draft", "in_review", "approved", "rejected", "live", "paused", "completed"] },

  /* ---------- B2B trust & trade ---------- */
  b2bAssuranceStatuses: { label: "B2B · Trade-assurance statuses", items: ["holding", "production", "shipped", "delivered", "released", "refunded", "disputed", "cancelled"] },
  b2bGoldTiers: { label: "B2B · Gold-supplier tiers", items: ["gold", "gold_plus", "premium", "verified_pro", "standard"] },
  b2bVerificationLevels: { label: "B2B · Verification levels", items: ["unverified", "basic", "verified", "gold_verified", "audited_pro"] },
  b2bVerificationStatuses: { label: "B2B · Verification statuses", items: ["pending", "document_review", "audit_scheduled", "audited", "approved", "rejected", "expired"] },
  b2bDocKinds: { label: "B2B · Export document kinds", items: ["commercial_invoice", "packing_list", "bill_of_lading", "air_waybill", "certificate_of_origin", "insurance_certificate", "inspection_cert", "packing_declaration", "msds", "dangerous_goods_declaration"] },
  b2bDocStatuses: { label: "B2B · Export document statuses", items: ["draft", "pending_review", "approved", "issued", "amended", "cancelled"] },
  b2bLcStatuses: { label: "B2B · LC statuses", items: ["issued", "advised", "confirmed", "documents_presented", "discrepant", "accepted", "paid", "amended", "cancelled"] },
  b2bQuoteStatuses: { label: "B2B · RFQ quote statuses", items: ["submitted", "shortlisted", "accepted", "rejected", "expired", "withdrawn"] },
  b2bBidStatuses: { label: "B2B · Tender-bid statuses", items: ["submitted", "technically_qualified", "shortlisted", "awarded", "rejected", "withdrawn"] },
  b2bSegments: { label: "B2B · Price-list segments", items: ["retail_customer", "wholesale", "distributor", "dealer", "enterprise", "gov", "export", "vip"] },

  /* ---------- Shopper experience ---------- */
  shopEvents: { label: "Shop · Registry events", items: ["wedding", "baby_shower", "birthday", "house_warming", "anniversary", "festival", "graduation", "corporate_gifting", "new_home"] },
  shopRegistryStatuses: { label: "Shop · Registry statuses", items: ["open", "closed", "fulfilled", "cancelled"] },
  shopNotifKinds: { label: "Shop · Notification kinds", items: ["order_placed", "order_paid", "order_shipped", "order_out_for_delivery", "order_delivered", "order_cancelled", "return_update", "refund_credit", "deal_alert", "back_in_stock", "price_drop", "registry_update", "wishlist_offer", "support_reply", "kyc_update", "payout_update", "bill_due", "emi_due"] },
  shopDocKinds: { label: "Shop · Document kinds", items: ["tax_invoice", "retail_invoice", "gst_invoice", "credit_note", "debit_note", "delivery_challan", "export_invoice", "proforma"] },
  shopDocStatuses: { label: "Shop · Document statuses", items: ["generated", "issued", "emailed", "amended", "cancelled"] }
};

/* seed: idempotent, preserves operator edits (a console edit is never clobbered;
   only lists that were seeded by this module and left untouched self-heal) */
function seed() {
  const D = db();
  const stamp = "parity_v1";
  for (const [name, def] of Object.entries(REG)) {
    const items = def.items.map(it => (typeof it === "string" ? { key: it, name: it } : it));
    const ex = D.get("SELECT items, seeded_from FROM meta_lists WHERE name=?", name);
    if (!ex) D.run("INSERT INTO meta_lists(name,label,items,seeded_from) VALUES(?,?,?,?)", name, def.label, JSON.stringify(items), stamp);
    else if (!ex.seeded_from) D.run("UPDATE meta_lists SET items=?, seeded_from=?, label=? WHERE name=?", JSON.stringify(items), stamp, def.label, name);
  }
}

/* read a registry as an array of {key,name} (or plain strings when flat) */
function list(name) {
  const row = db().get("SELECT items FROM meta_lists WHERE name=?", name);
  return J(row ? row.items : "[]", []);
}
/* read a registry as a plain array of keys (for select options + validation) */
function keys(name) { return list(name).map(x => x.key || x); }
/* registry membership test (used by the parity engines for state validation) */
function has(name, value) { return keys(name).includes(value); }

module.exports = { REG, seed, list, keys, has };
