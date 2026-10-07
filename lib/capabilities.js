/* LUXORA Platform — The Capability Layer.
   --------------------------------------------------------------------------
   "Configure types, standards, quality, features and functionalities of any
   platform or service" — this module is that statement made literal.

   A CAPABILITY is one individually switchable, individually tunable function of
   the platform: "buy_box", "trade_assurance", "qr_pay", "instant_delivery"…
   Each ships its own set of PARAMS (a standard, a threshold, a weight, a fee),
   declared with a type and a default. The parity engines contain no business-rule
   literal whatsoever: they ask `cap()` for the value and act on the answer.

    COMPOSITION, NOT TEMPLATE. A tenant does not pick a template — it composes a
    platform capability-by-capability: a buy-box, a dispatch OTP and a UPI collect
    may all be enabled in one store while trade assurance stays off. Every preset
    below is a seeded worked example; they are rows, so an operator renames, edits
    or deletes them, or defines a brand-new archetype from the console. No engine
    knows which capabilities a tenant uses until it asks — the "platform type" IS
    the set of rows, not a code branch, and no vendor, product or brand name is
    baked into any definition: a capability declares what it does and which knobs
    tune it, never whose it is. Parity with any platform is a consequence of the
    composition, not a label.

   RESOLUTION ORDER for a parameter: tenant's own override → the preset the
   tenant is assigned (if any) → the platform default declared in this catalog.
   An unknown capability or param falls back to its declared default, and a
   capability that is not enabled answers `false` for every param — so a
   disabled capability is inert, never an error. (Architecture3 §2.1: No
   Hard-Coded Business Logic, Registry Driven Everything, Infinite
   Composability, Infinite Extensibility.) */
"use strict";

const db = () => require("./db.js");
const J = (v, d) => { try { return v == null || v === "" ? (d == null ? {} : d) : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d == null ? {} : d; } };

/* ============================================================
   THE CATALOG — the platform's declaration of what is configurable.
   Every `params` entry is { type, default, label, unit? }. This is the ONLY
   place a business-rule default lives, and it is data: an operator edits the
   row in platform_capabilities and every engine follows on the next call.
   ============================================================ */
const CATALOG = [
  /* ---------- Marketplace: standards of listing trust & competition ---------- */
  { key: "buy_box", label: "Buy-box competition", domain: "marketplace", icon: "🏆", description: "Multiple sellers compete for one product's featured offer. The winner is the best composite of price, fulfilment speed and seller trust — each weight is tunable here.",
    params: {
      price_weight:   { type: "number", default: 0.6,  label: "Price weight", unit: "0-1" },
      speed_weight:   { type: "number", default: 0.25, label: "Fulfilment-speed weight", unit: "0-1" },
      trust_weight:   { type: "number", default: 0.15, label: "Seller-trust weight", unit: "0-1" },
      speed_baseline_days: { type: "number", default: 3, label: "Speed baseline (days assumed when unknown)" },
      handling_baseline_hours: { type: "number", default: 12, label: "Handling baseline (hours assumed when unknown)" },
      recompute_on_change: { type: "bool", default: true, label: "Recompute the winner when an offer or health row changes" }
    } },
  { key: "seller_health", label: "Seller account health", domain: "marketplace", icon: "❤️", description: "Account health: defect, cancellation and late-shipment rates roll into a score that decides the tier and suspension.",
    params: {
      odr_weight:         { type: "number", default: 2.0, label: "Order-defect-rate weight" },
      cancellation_weight:{ type: "number", default: 1.5, label: "Cancellation-rate weight" },
      late_weight:        { type: "number", default: 1.0, label: "Late-shipment weight" },
      tier_thresholds:    { type: "json", default: { platinum: 95, gold: 85, premium: 70, growth: 50 }, label: "Tier thresholds (score → tier), highest first" },
      suspend_below:      { type: "number", default: 40, label: "Health score below which a seller's offers are suspended" },
      late_shipment_days: { type: "number", default: 3,  label: "A shipment is 'late' after this many days undelivered" }
    } },
  { key: "buyer_protection", label: "Buyer protection (A-to-z)", domain: "marketplace", icon: "🛡️", description: "A buyer may raise a claim against a seller; a claim resolved in the buyer's favour credits the buyer from the ledger.",
    params: {
      auto_dispute_escrow: { type: "bool", default: true, label: "Mark an order's escrow hold disputed while a claim is open" },
      refund_kind:         { type: "text", default: "refund", label: "Wallet ledger kind used for a buyer-favour refund" }
    } },
  { key: "smart_fulfilment", label: "Smart-fulfilment grading", domain: "marketplace", icon: "⚡", description: "Fulfilment grading: each grade carries a dispatch SLA in hours.",
    params: {
      sla_hours: { type: "json", default: { a_plus: 4, a: 8, b: 24, c: 48, d: 72 }, label: "Grade → dispatch SLA hours" },
      default_sla_hours: { type: "number", default: 24, label: "SLA for an unmapped grade" }
    } },
  { key: "fba_inbound", label: "Fulfilment-centre inbound", domain: "marketplace", icon: "📦", description: "Sellers ship units to a fulfilment centre; receiving closes the inbound and adds the units to FC inventory.",
    params: { default_status: { type: "text", default: "created", label: "Initial status of an inbound shipment" } } },

  /* ---------- Fintech: the rails of money movement ---------- */
  { key: "upi_collect", label: "UPI collect", domain: "fintech", icon: "💸", description: "Raise a collect request against a payer VPA; settlement credits the single wallet ledger.",
    params: {
      new_handle_status: { type: "text", default: "pending_verification", label: "Status of a freshly added VPA" },
      collect_expiry_hours: { type: "number", default: 1, label: "A collect request expires after this many hours" },
      min_amount: { type: "number", default: 0.01, label: "Lowest collectable amount (0 disables the floor)" }
    } },
  { key: "qr_pay", label: "QR scan-pay", domain: "fintech", icon: "▦", description: "Issue QR records from the registry's kinds; a scan is counted and (optionally) a payment completed.",
    params: { default_kind: { type: "text", default: "upi", label: "QR kind when none is supplied" } } },
  { key: "payment_links", label: "Payment links", domain: "fintech", icon: "🔗", description: "Issue a tokenised link that credits the owner's wallet when paid. Single-use by default.",
    params: {
      expiry_days: { type: "number", default: 7, label: "A link is payable for this many days" },
      single_use:  { type: "bool", default: true, label: "A paid link cannot be paid again" }
    } },
  { key: "mandates", label: "Mandates / auto-debit", domain: "fintech", icon: "🔁", description: "Register an auto-debit mandate and charge it up to its cap. Subscriptions ride on this.",
    params: {
      default_frequency: { type: "text", default: "monthly", label: "Frequency when none is supplied" },
      recharge_window_days: { type: "number", default: 30, label: "Days added to the next-charge-at on each charge" }
    } },
  { key: "escrow", label: "Escrow hold & release", domain: "fintech", icon: "🔒", description: "Hold funds at order time and release to the seller only on confirmation. Trade assurance composes this capability.",
    params: {
      dispute_freezes: { type: "bool", default: true, label: "A dispute prevents release until resolved" },
      release_kind:    { type: "text", default: "deposit", label: "Wallet ledger kind used for a seller release" }
    } },
  { key: "split_payments", label: "Split payments", domain: "fintech", icon: "✂️", description: "Divide a payment across parties at order time. The parts must sum to the total, or the ledger would drift.",
    params: {
      tolerance: { type: "number", default: 0.01, label: "Rounding tolerance when comparing the split sum with the total" },
      settle_immediately: { type: "bool", default: true, label: "Settle the parts when the payment lands" }
    } },
  { key: "kyc", label: "KYC verification", domain: "fintech", icon: "🪪", description: "Identity verification that gates credit: BNPL and loans require the full tier.",
    params: {
      full_tier_status: { type: "text", default: "full_kyc", label: "KYC profile status that satisfies the full tier" },
      min_tier_status:  { type: "text", default: "min_kyc", label: "Status for the limited tier" }
    } },
  { key: "bnpl", label: "Buy-now-pay-later", domain: "fintech", icon: "💳", description: "A KYC-gated credit account that generates an EMI schedule on each spend.",
    params: {
      default_tenure_months: { type: "number", default: 3, label: "Tenure when none is supplied" },
      min_amount: { type: "number", default: 0.01, label: "Lowest financeable amount" }
    } },
  { key: "lending", label: "Loans & credit lines", domain: "fintech", icon: "🏦", description: "Apply, approve and disburse credit. The EMI is computed from the principal, tenure and rate.",
    params: {
      default_tenure_months: { type: "number", default: 12, label: "Tenure when none is supplied" },
      default_rate_pct:      { type: "number", default: 0, label: "Annual rate when none is supplied (0 = flat)" }
    } },
  { key: "bank_payouts", label: "Bank payouts", domain: "fintech", icon: "🏦", description: "Queue a payout to a bank account or VPA and process it through the configured gateway.",
    params: { default_status: { type: "text", default: "queued", label: "Initial status of a queued payout" } } },
  { key: "bbps", label: "Bill payments (BBPS)", domain: "fintech", icon: "🧾", description: "Pay electricity, water, gas and similar bills through registered billers.",
    params: { default_category: { type: "text", default: "electricity", label: "Category when the biller is unknown" } } },
  { key: "recharge", label: "Mobile / DTH recharge", domain: "fintech", icon: "📱", description: "Prepaid recharge against a plan catalogue; a recharge debits the wallet on success.",
    params: { default_kind: { type: "text", default: "mobile", label: "Recharge kind when none is supplied" } } },
  { key: "p2p_transfer", label: "P2P wallet transfer", domain: "fintech", icon: "⇄", description: "Wallet-to-wallet transfer between two owners. Self-transfer and overdraft are refused.",
    params: { ledger_unit: { type: "text", default: "USD", label: "Unit the transfer row is written in" } } },
  { key: "insurance", label: "Insurance distribution", domain: "fintech", icon: "🛡️", description: "Quote a policy and activate it; activation debits the premium from the wallet.",
    params: { activation_debits_premium: { type: "bool", default: true, label: "Activating a policy charges the premium" } } },
  { key: "gift_vouchers", label: "Gift vouchers", domain: "fintech", icon: "🎁", description: "Issue a code with a balance; redemption credits the holder's wallet. Expired codes are retired on use.",
    params: { code_length: { type: "number", default: 12, label: "Length of the generated voucher code" } } },

  /* ---------- Quick-commerce: the promise engine ---------- */
  { key: "instant_delivery", label: "Instant / quick-commerce delivery", domain: "qc", icon: "⚡", description: "Dark stores, serviceability, delivery slots and proof-of-delivery OTP. The promise is the store's own advertised minutes plus prep time.",
    params: {
      default_promise_minutes: { type: "number", default: 10, label: "Promise minutes a store advertises when unset" },
      default_prep_minutes:    { type: "number", default: 4,  label: "Prep minutes added to every promise" },
      default_radius_km:       { type: "number", default: 3,  label: "Service radius for geo resolution when unset" },
      promise_includes_prep:   { type: "bool", default: true, label: "The shown promise is store minutes + prep" },
      otp_length:              { type: "number", default: 6,  label: "Digits in a proof-of-delivery OTP" }
    } },
  { key: "store_inventory", label: "Store-inventory pinning", domain: "qc", icon: "📍", description: "Per-store stock pinning so a dark store cannot oversell. Safety stock is held back from the sellable count.",
    params: {
      reserve_at_pin:  { type: "bool", default: true, label: "Reserve the units when a cart is pinned to a store" },
      consume_on_delivery: { type: "bool", default: true, label: "Decrement the store's qty when a run is delivered" }
    } },
  { key: "dispatch_batching", label: "Dispatch batching & PoD", domain: "qc", icon: "🧺", description: "Batch orders onto one rider for one slot and close delivery with an OTP handshake.",
    params: {
      release_slot_on_delivery: { type: "bool", default: true, label: "Return the slot seat when the run closes" },
      rider_goes_online_after:  { type: "bool", default: true, label: "A rider returns to online after delivering" }
    } },

  /* ---------- B2B trust & trade ---------- */
  { key: "trade_assurance", label: "Trade assurance", domain: "trade", icon: "🤝", description: "Order-level escrow with milestones: funds release to the seller only when the buyer confirms receipt.",
    params: {
      assurance_fee_pct: { type: "number", default: 0.02, label: "Assurance fee as a fraction of the order (0.02 = 2%)", unit: "fraction" },
      default_milestones: { type: "json", default: ["paid", "production", "shipped", "delivered"], label: "Milestone sequence when none is supplied" }
    } },
  { key: "gold_supplier", label: "Gold-supplier membership", domain: "trade", icon: "🥇", description: "Paid supplier memberships with a verification level that drives storefront badges.",
    params: { default_tier: { type: "text", default: "gold", label: "Tier when none is supplied" } } },
  { key: "company_verification", label: "Company verification audit", domain: "trade", icon: "🔍", description: "An audit of a supplier's identity and export record; approval stamps badges and activates the membership.",
    params: { approval_activates_membership: { type: "bool", default: true, label: "An approved audit marks the supplier's gold membership verified" } } },
  { key: "export_documents", label: "Export / customs documents", domain: "trade", icon: "📄", description: "Generate commercial invoices, packing lists, bills of lading and certificates deterministically from the order's own fields.",
    params: {
      default_doc_kind: { type: "text", default: "commercial_invoice", label: "Document kind when none is supplied" },
      default_incoterms:{ type: "text", default: "EXW", label: "Incoterms when none is supplied" },
      default_origin:   { type: "text", default: "US", label: "Origin country when none is supplied" }
    } },
  { key: "letters_of_credit", label: "Letters of credit", domain: "trade", icon: "🏦", description: "Issue, present and settle an LC. A clean presentation pays; a discrepant one is recorded, not thrown.",
    params: { presentable_statuses: { type: "json", default: ["issued", "advised", "confirmed"], label: "LC statuses from which a presentation is allowed" } } },
  { key: "rfq_bidding", label: "RFQ multi-seller bidding", domain: "trade", icon: "💬", description: "Suppliers quote against a buyer's RFQ; quotes rank by unit price then lead time. Accepting one closes the rest.",
    params: {
      rank_by: { type: "json", default: ["unit_price", "lead_days"], label: "Columns the ranking orders by, ascending" },
      default_validity_days: { type: "number", default: 30, label: "Quote validity when none is supplied" }
    } },
  { key: "reverse_auction", label: "Tender reverse auction", domain: "trade", icon: "🔨", description: "Open tenders take sealed bids and rank them lowest-first; awarding rejects every other bid.",
    params: { mirror_to_tender_column: { type: "bool", default: true, label: "Keep the legacy tenders.bids column in sync for the existing console" } } },
  { key: "segment_pricing", label: "Segment price lists", domain: "trade", icon: "🏷️", description: "Per-segment prices with quantity tiers; the storefront resolves the buyer's segment and reads the override.",
    params: { best_price_wins: { type: "bool", default: true, label: "When several tiers fit, the lowest price wins" } } },
  { key: "moq_enforcement", label: "MOQ enforcement", domain: "trade", icon: "≥", description: "The cart must respect each line's minimum order quantity — from the product, the supplier link or the price list.",
    params: { default_moq: { type: "number", default: 1, label: "MOQ when no source declares one" } } }
];

/* ---------- seeding: the catalog becomes rows, once, without clobbering ---------- */
/* the stamped catalog version. A row whose seeded_from differs and that nobody
   has edited follows the catalog when it changes; bump this to revise the seed. */
const CATALOG_STAMP = "cap_v3";   /* v3: each atom declares the console sections it governs */

/* ---------- the console surface an atom governs ----------
   A store console section is not a bundle someone buys: it is the shadow of the
   individual capabilities this tenant switched on. Each ATOM declares the nav leaves
   it lights — buy_box lights Marketplace & Marketplace Ops; rfq_bidding lights RFQs;
   instant_delivery lights Quick-commerce Ops. The grant engine (lib/authz.js) derives
   the store surface from the tenant's LIVE composition through this map, so a leaf
   appears the moment its atom is on and nothing is ever granted as a package. A section
   no atom names is governed by the tenant's own profile (NAVFIT) instead — vertical
   facts like serial tracking and replenishment, which no engine owns.
   Seeded into the catalog column; an operator's edit is the truth at runtime, with the
   declared list a floor (same rule as params — an operator may add a leaf an atom
   lights, never delete one the console would then hide while its engine still runs). */
const SECTIONS = {
  buy_box: ["marketplace", "mktops"],
  seller_health: ["sellers", "mktops"],
  buyer_protection: ["mktops"],
  smart_fulfilment: ["mktops"],
  fba_inbound: ["mktops"],
  trade_assurance: ["contracts", "tradeops"],
  gold_supplier: ["sellers", "tradeops"],
  company_verification: ["tradeops"],
  export_documents: ["tradeops"],
  letters_of_credit: ["contracts", "tradeops"],
  rfq_bidding: ["rfqs", "tradeops"],
  reverse_auction: ["tenders", "tradeops"],
  segment_pricing: ["tradeops"],
  moq_enforcement: ["contracts", "tradeops"],
  instant_delivery: ["qcops"],
  store_inventory: ["qcops"],
  dispatch_batching: ["qcops"],
  upi_collect: ["finops"], qr_pay: ["finops"], payment_links: ["finops"], mandates: ["finops"],
  escrow: ["finops"], split_payments: ["finops"], kyc: ["finops"], bnpl: ["finops"],
  lending: ["finops"], bank_payouts: ["finops"], bbps: ["finops"], recharge: ["finops"],
  p2p_transfer: ["finops"], insurance: ["finops"], gift_vouchers: ["finops"]
};
/* the section list a catalog row resolves: the atom's declared leaves ∪ the operator's
   own (authored atoms have no declaration — theirs is the whole story) */
function sectionsOf(key, row) {
  const base = row && Array.isArray(row.sections) ? row.sections : [];
  const floor = SECTIONS[key] || [];
  return [...new Set(floor.concat(base))];
}

function seed() {
  const D = db();
  const stamp = CATALOG_STAMP;
  CATALOG.forEach((c, i) => {
    const params = {};
    for (const [k, p] of Object.entries(c.params)) params[k] = { type: p.type, default: p.default, label: p.label, unit: p.unit };
    const ex = D.get("SELECT params, seeded_from, edited FROM platform_capabilities WHERE key=?", c.key);
    if (!ex) D.run("INSERT INTO platform_capabilities(key,label,domain,icon,description,params,sections,enabled,position,seeded_from) VALUES(?,?,?,?,?,?,?,1,?,?)",
      c.key, c.label, c.domain, c.icon, c.description, JSON.stringify(params), JSON.stringify(SECTIONS[c.key] || []), i, stamp);
    /* SELF-HEAL, BUT NEVER AN OVERWRITE. A row nobody has touched follows the
       catalog when the catalog changes (a new param, a revised description, a new
       section it lights) — detected by the stamped version moving on. The moment an
       operator edits a row from the console, `edited` is set and the row is theirs
       forever: the catalog may grow around it, it never clobbers the operator's tuning. */
    else if (!ex.edited && ex.seeded_from !== stamp) D.run("UPDATE platform_capabilities SET params=?, seeded_from=?, label=?, description=?, sections=? WHERE key=?",
      JSON.stringify(params), stamp, c.label, c.description, JSON.stringify(SECTIONS[c.key] || []), c.key);
  });
}

/* ---------- resolution ---------- */
function catalogRow(key) {
  const r = db().get("SELECT * FROM platform_capabilities WHERE key=?", key);
  if (!r) { const c = CATALOG.find(x => x.key === key); return c ? { key, params: c.params, sections: SECTIONS[key] || [], enabled: 1 } : null; }
  return { ...r, params: J(r.params, {}), sections: sectionsOf(key, r) };
}
function catalogKeys(domain) {
  return (domain ? CATALOG.filter(c => c.domain === domain) : CATALOG).map(c => c.key);
}
/* is the capability switched on for this tenant? A capability disabled at
   platform level, or never enabled for the tenant, is off. */
function on(tenantId, key) {
  const cap = catalogRow(key);
  if (!cap || !cap.enabled) return false;
  const v = db().get("SELECT enabled FROM capability_values WHERE tenant_id=? AND capability=?", Number(tenantId), key);
  return v ? !!v.enabled : false;
}
/* the effective parameter set for one capability + tenant:
   platform default → assigned preset → the tenant's own row */
function params(tenantId, key) {
  const cap = catalogRow(key);
  if (!cap) return {};
  const out = {};
  /* a seeded capability's catalog params are a FLOOR: an operator may add or
     retune a param, but can never accidentally delete one an engine reads
     (cap() would then answer undefined and the engine would misbehave silently).
     An operator-authored capability owns its params outright — there is no
     in-code catalog to fall back to, by design. */
  const seedCat = CATALOG.find(x => x.key === key);
  const declared = Object.assign({}, seedCat ? seedCat.params : {}, cap.params || {});
  for (const [k, p] of Object.entries(declared)) out[k] = p.default;
  const tid = Number(tenantId);
  const presetRow = db().get("SELECT preset_key FROM capability_preset_assignments WHERE tenant_id=?", tid);
  if (presetRow) {
    const preset = db().get("SELECT capabilities FROM capability_presets WHERE key=?", presetRow.preset_key);
    const entry = preset ? J(preset.capabilities, {})[key] : null;
    if (entry && entry.params) Object.assign(out, entry.params);
  }
  const mine = db().get("SELECT params FROM capability_values WHERE tenant_id=? AND capability=?", tid, key);
  if (mine) Object.assign(out, J(mine.params, {}));
  return out;
}
/* the single read the engines make: `cap(t, "trade_assurance").assurance_fee_pct`.
   A disabled capability answers falsy for everything, so the caller can guard
   on the same call it reads from. */
function cap(tenantId, key) {
  if (!on(tenantId, key)) return {};
  return params(tenantId, key);
}

/* ---------- composition: the platform a tenant actually is ---------- */
/* the capabilities a tenant has switched on, each with its effective params —
   this object IS the tenant's platform type; there is no other definition */
function compositionOf(tenantId) {
  const tid = Number(tenantId);
  const rows = db().all("SELECT capability, enabled, params FROM capability_values WHERE tenant_id=? ORDER BY capability", tid);
  const presetRow = db().get("SELECT preset_key FROM capability_preset_assignments WHERE tenant_id=?", tid);
  const out = { tenant_id: tid, preset: presetRow ? presetRow.preset_key : null, capabilities: {} };
  for (const r of rows) {
    const cap = catalogRow(r.capability);
    if (!cap || !cap.enabled || !r.enabled) continue;
    const p = {};
    for (const [k, v] of Object.entries(cap.params || {})) p[k] = v.default;
    Object.assign(p, J(r.params, {}));
    out.capabilities[r.capability] = { enabled: true, domain: cap.domain, label: cap.label, params: p };
  }
  return out;
}
/* enable a capability for a tenant, with optional param overrides */
function enable(tenantId, key, overrides, notes) {
  const cap = catalogRow(key);
  if (!cap) throw new Error("Unknown capability: " + key);
  if (!cap.enabled) throw new Error("Capability is disabled at platform level: " + key);
  const p = overrides && typeof overrides === "object" ? overrides : {};
  db().run("INSERT INTO capability_values(tenant_id,capability,enabled,params,notes) VALUES(?,?,1,?,?) ON CONFLICT(tenant_id,capability) DO UPDATE SET enabled=1, params=excluded.params, notes=excluded.notes",
    Number(tenantId), key, JSON.stringify(p), String(notes || ""));
  return compositionOf(tenantId);
}
function disable(tenantId, key) {
  db().run("UPDATE capability_values SET enabled=0 WHERE tenant_id=? AND capability=?", Number(tenantId), key);
  return compositionOf(tenantId);
}
/* apply a named preset to a tenant: each entry becomes a capability_values row */
function applyPreset(tenantId, presetKey) {
  const D = db();
  const preset = D.get("SELECT * FROM capability_presets WHERE key=?", presetKey);
  if (!preset) throw new Error("Unknown capability preset: " + presetKey);
  const caps = J(preset.capabilities, {});
  for (const [key, entry] of Object.entries(caps)) {
    const cap = catalogRow(key);
    if (!cap) continue;
    D.run("INSERT INTO capability_values(tenant_id,capability,enabled,params) VALUES(?,?,?,?) ON CONFLICT(tenant_id,capability) DO UPDATE SET enabled=excluded.enabled, params=excluded.params",
      Number(tenantId), key, entry.enabled === false ? 0 : 1, JSON.stringify(entry.params || {}));
  }
  D.run("INSERT INTO capability_preset_assignments(tenant_id,preset_key) VALUES(?,?) ON CONFLICT(tenant_id,preset_key) DO NOTHING", Number(tenantId), presetKey);
  return compositionOf(tenantId);
}

/* ---------- presets: named, reusable blends (rows, not code) ---------- */
const PRESETS = [
  { key: "blend_marketplace", label: "Marketplace blend", description: "A worked example: multi-seller competition with buyer protection and trade assurance — the composition a marketplace operator would recognise.",
    capabilities: {
      buy_box:        { params: { price_weight: 0.6, speed_weight: 0.25, trust_weight: 0.15 } },
      seller_health:  { params: { suspend_below: 40 } },
      buyer_protection: {},
      smart_fulfilment: {},
      fba_inbound:    {},
      escrow:         {},
      split_payments: {},
      kyc:            {},
      payment_links:  {},
      bank_payouts:   {}
    } },
  { key: "blend_quick_commerce", label: "Quick-commerce blend", description: "A worked example: dark stores, a minutes-level promise, OTP proof-of-delivery and wallet rails — the composition a quick-commerce operator would recognise.",
    capabilities: {
      instant_delivery: { params: { default_promise_minutes: 10, default_prep_minutes: 4, default_radius_km: 3 } },
      store_inventory:  {},
      dispatch_batching: {},
      qr_pay:           {},
      upi_collect:      {},
      p2p_transfer:     {},
      gift_vouchers:    {}
    } },
  { key: "blend_b2b_trade", label: "B2B trade blend", description: "A worked example: assurance escrow, memberships, verification audits, export documents, LCs and RFQ bidding — the composition a B2B-trade operator would recognise.",
    capabilities: {
      trade_assurance: { params: { assurance_fee_pct: 0.02 } },
      gold_supplier:   {},
      company_verification: {},
      export_documents: {},
      letters_of_credit: {},
      rfq_bidding:     {},
      reverse_auction: {},
      segment_pricing: {},
      moq_enforcement: {}
    } },
  { key: "blend_fintech", label: "Fintech rails blend", description: "A worked example: the full money rail set — UPI, QR, links, mandates, escrow, splits, KYC, payouts, BBPS, recharge, BNPL, lending, insurance and vouchers.",
    capabilities: {
      upi_collect: {}, qr_pay: {}, payment_links: {}, mandates: {}, escrow: {}, split_payments: {},
      kyc: {}, bank_payouts: {}, bbps: {}, recharge: {}, p2p_transfer: {}, bnpl: {}, lending: {},
      insurance: {}, gift_vouchers: {}
    } },
  /* deliberately mixed: proves the platform is a composition, not a template —
     marketplace competition, quick-commerce dispatch and fintech rails in one
     store, none of it inherited from a single template */
  { key: "blend_mixed", label: "Mixed commerce blend", description: "Proof of composition: marketplace buy-box and buyer protection, quick-commerce dispatch and store pinning, and UPI rails from fintech — none of which comes from one vendor.",
    capabilities: {
      buy_box:           { params: { price_weight: 0.7, speed_weight: 0.2, trust_weight: 0.1 } },
      buyer_protection:  {},
      instant_delivery:  { params: { default_promise_minutes: 15 } },
      store_inventory:   {},
      dispatch_batching: {},
      upi_collect:       {},
      escrow:            {},
      kyc:               {}
    } }
];
function seedPresets() {
  const D = db();
  for (const p of PRESETS) {
    D.run("INSERT INTO capability_presets(key,label,description,capabilities) VALUES(?,?,?,?) ON CONFLICT(key) DO UPDATE SET label=excluded.label, description=excluded.description",
      p.key, p.label, p.description, JSON.stringify(p.capabilities));
  }
}

/* ---------- the configuration surface (the console lives here) ---------- */
/* the whole catalog as the console renders it: every capability with its
   declared params, its domain and its platform switch */
function catalog() {
  return db().all("SELECT * FROM platform_capabilities ORDER BY position, key")
    .map(r => ({ ...r, params: J(r.params, {}), sections: sectionsOf(r.key, r) }));
}
/* every archetype (preset) — seeded worked examples plus the operator's own */
function presets() {
  return db().all("SELECT * FROM capability_presets ORDER BY key")
    .map(r => ({ ...r, capabilities: J(r.capabilities, {}) }));
}
/* coerce a value to the param's DECLARED type. The console's inputs arrive as
   strings; the engines expect typed values. An unknown capability or param, or a
   value that cannot be coerced, is refused — a configured standard is validated,
   never silently dropped */
function coerce(capKey, param, value) {
  const cap = catalogRow(capKey);
  if (!cap) throw new Error("Unknown capability: " + capKey);
  const def = (cap.params || {})[param];
  if (!def) throw new Error("Unknown parameter: " + param + " on " + capKey);
  const t = def.type;
  if (t === "number") { const n = Number(value); if (!isFinite(n)) throw new Error(param + " must be a number"); return n; }
  if (t === "bool") return /^(1|true|yes|on)$/i.test(String(value));
  if (t === "json") { try { return typeof value === "string" ? JSON.parse(value) : value; } catch (e) { throw new Error(param + " must be valid JSON"); } }
  return String(value);
}
/* tune ONE parameter for a tenant. The capability is enabled and the param merged
   onto the defaults — configuring a standard is the act of switching it on */
function tune(tenantId, key, param, value) {
  const v = coerce(key, param, value);
  const cur = db().get("SELECT params FROM capability_values WHERE tenant_id=? AND capability=?", Number(tenantId), key);
  const merged = { ...(cur ? J(cur.params, {}) : {}), [param]: v };
  return enable(tenantId, key, merged);
}
/* platform-level: switch a capability off for every tenant, or retitle it. Marks
   the row edited so the catalog's future revisions never clobber the decision */
function setPlatform(key, patch) {
  const cap = catalogRow(key);
  if (!cap) throw new Error("Unknown capability: " + key);
  const sets = [], vals = [];
  if (patch && patch.enabled != null) { sets.push("enabled=?"); vals.push(patch.enabled ? 1 : 0); }
  if (patch && patch.label != null) { sets.push("label=?"); vals.push(String(patch.label).trim()); }
  if (patch && patch.description != null) { sets.push("description=?"); vals.push(String(patch.description)); }
  if (!sets.length) throw new Error("nothing to update");
  sets.push("edited=1"); vals.push(key);
  db().run("UPDATE platform_capabilities SET " + sets.join(",") + " WHERE key=?", ...vals);
  return catalogRow(key);
}
/* author an archetype: a named, reusable capability set. Unknown capabilities are
   dropped rather than persisted — a preset may only reference the real catalog */
function savePreset(key, label, description, capabilities) {
  const k = String(key || "").trim();
  if (!k) throw new Error("preset key required");
  const clean = {};
  for (const [ck, v] of Object.entries(capabilities || {})) {
    if (!catalogRow(ck)) continue;
    clean[ck] = { enabled: !(v && v.enabled === false), params: (v && v.params) || {} };
  }
  db().run("INSERT INTO capability_presets(key,label,description,capabilities) VALUES(?,?,?,?) ON CONFLICT(key) DO UPDATE SET label=excluded.label, description=excluded.description, capabilities=excluded.capabilities",
    k, String(label || k).trim(), String(description || ""), JSON.stringify(clean));
  return presets().find(p => p.key === k);
}
function removePreset(key) {
  if (!key) throw new Error("preset key required");
  db().run("DELETE FROM capability_presets WHERE key=?", String(key));
  db().run("DELETE FROM capability_preset_assignments WHERE preset_key=?", String(key));
  return { ok: true };
}

/* ---------- AUTHORING: the catalog is open-ended ----------
   This is the difference between a configurable commerce platform and a
   configurable ANY platform. The seeded catalog covers commerce domains; an
   operator extends it from the console to define a capability no release knew
   about — surge pricing for a mobility platform, creator payouts for a video
   one, lead scoring for a CRM — each with its own typed parameters. Every
   engine, form and dropdown that reads the catalog follows on the next call,
   because the catalog IS the vocabulary. */
function define(key, label, domain, icon, description, params) {
  const D = db();
  const k = String(key || "").trim();
  if (!k) throw new Error("capability key required");
  if (!String(label || "").trim()) throw new Error("capability label required");
  const decl = {};
  for (const [pk, p] of Object.entries(params || {})) {
    const t = String((p && p.type) || "text").toLowerCase();
    if (!["number", "bool", "text", "json"].includes(t))
      throw new Error("param '" + pk + "' has an unknown type '" + t + "' (number | bool | text | json)");
    decl[pk] = { type: t, default: p == null ? undefined : p.default, label: String((p && p.label) || pk), unit: p && p.unit ? String(p.unit) : undefined };
  }
  const pos = D.get("SELECT COALESCE(MAX(position), -1) + 1 p FROM platform_capabilities");
  /* seeded_from 'operator' marks a row the catalog never seeded — it is the
     operator's own, and it is the signal the console uses to offer deletion
     (a seeded row can only be disabled, never removed) */
  D.run("INSERT INTO platform_capabilities(key,label,domain,icon,description,params,enabled,position,seeded_from,edited) VALUES(?,?,?,?,?,?,1,?,?,1) ON CONFLICT(key) DO UPDATE SET label=excluded.label, domain=excluded.domain, icon=excluded.icon, description=excluded.description, params=excluded.params, edited=1",
    k, String(label).trim(), String(domain || "custom").trim(), String(icon || "▪").slice(0, 4),
    String(description || ""), JSON.stringify(decl), pos ? pos.p : 0, "operator");
  return catalogRow(k);
}
/* removing a capability: a seeded one cannot be deleted (the code that reads it
   still exists — disable it platform-wide instead); an authored one can, but
   only once no store is using it, or its composition would reference a phantom */
function undefine(key) {
  const D = db();
  const k = String(key || "").trim();
  if (!k) throw new Error("capability key required");
  if (CATALOG.some(c => c.key === k))
    throw new Error("a seeded capability cannot be deleted — switch it off platform-wide instead");
  if (D.get("SELECT 1 FROM capability_values WHERE capability=? AND enabled=1 LIMIT 1", k))
    throw new Error("a capability a store has switched on cannot be deleted — switch it off first");
  D.run("DELETE FROM capability_values WHERE capability=?", k); /* clear orphaned disabled rows */
  D.run("DELETE FROM platform_capabilities WHERE key=?", k);
  return { ok: true };
}

module.exports = {
  CATALOG, PRESETS, SECTIONS, seed, seedPresets,
  catalogRow, catalogKeys, on, params, cap, sectionsOf,
  compositionOf, enable, disable, applyPreset,
  catalog, presets, coerce, tune, setPlatform, savePreset, removePreset,
  define, undefine
};
