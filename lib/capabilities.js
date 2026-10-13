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
    params: { default_moq: { type: "number", default: 1, label: "MOQ when no source declares one" } } },

  /* ---------- Storefront: the shopper-facing surfaces ----------
     Formerly settings.features.* booleans. Each was a silent flag on a settings
     row; each is now an atom in the same catalog as buy_box and escrow, so a
     feature is switched and tuned exactly the way a capability is, and the grant
     engine derives the console surface it lights through the same SECTIONS map. */
  { key: "reviews", label: "Product reviews", domain: "storefront", icon: "⭐", description: "Shopper-written product reviews with ratings, replies and moderation.",
    params: { moderation: { type: "bool", default: false, label: "A review is published only after a moderator approves it" } } },
  { key: "qna", label: "Questions & Answers", domain: "storefront", icon: "❓", description: "Shoppers ask and answer questions on a product page.",
    params: { buyer_answers: { type: "bool", default: true, label: "Other shoppers may answer a question, not only staff" } } },
  { key: "deals", label: "Deals page & strip", domain: "storefront", icon: "🏷️", description: "The /deals page, the header deal link and the storefront offers strip.",
    params: {} },
  { key: "coupons", label: "Promo codes", domain: "storefront", icon: "🎟️", description: "Shopper-redeemable coupon codes at cart and checkout. Platform policy may refuse this independently.",
    params: {} },
  { key: "gift_cards", label: "Gift cards & balance", domain: "storefront", icon: "🎁", description: "The gift-cards page, the gift-balance line in checkout and the wallet top-up path.",
    params: {} },
  { key: "registry", label: "Registries", domain: "storefront", icon: "📋", description: "Wish-list style product registries a shopper shares by link.",
    params: {} },
  { key: "customer_service", label: "Client care", domain: "storefront", icon: "🎧", description: "The customer-service page and the shopper-facing contact channel.",
    params: {} },
  { key: "save_for_later", label: "Save for later", domain: "storefront", icon: "📌", description: "Moving a cart line to a saved list and back.",
    params: {} },
  { key: "countdown", label: "Deal countdown", domain: "storefront", icon: "⏳", description: "A live countdown badge on time-limited offers.",
    params: {} },
  { key: "suggestions", label: "Search suggestions", domain: "storefront", icon: "💡", description: "Type-ahead suggestions on the storefront search box.",
    params: { max: { type: "number", default: 8, label: "Suggestions shown" } } },
  { key: "buy_now", label: "Buy now", domain: "storefront", icon: "⚡", description: "Skip the cart: a product's Buy Now goes straight to checkout.",
    params: {} },
  { key: "fiscal_selection", label: "Fiscal context picker", domain: "storefront", icon: "🧾", description: "Customer-facing selection of a tax/invoice context at checkout. Platform policy may refuse this independently.",
    params: {} },
  { key: "subscribe_save", label: "Subscribe & Save", domain: "storefront", icon: "🔁", description: "Recurring purchase schedules with a discount and a cadence.",
    params: { discount_pct: { type: "number", default: 5, label: "Default discount for a scheduled purchase", unit: "%" } } },
  { key: "membership", label: "Membership program", domain: "storefront", icon: "🎟️", description: "Paid or free tiers with perks applied at checkout (free shipping, bonus credit).",
    params: { bonus_pct: { type: "number", default: 0, label: "Checkout bonus credit a member earns", unit: "%" } } },
  { key: "fraud_screen", label: "Risk screening", domain: "storefront", icon: "🛡️", description: "Order-time risk screening that may flag or block a suspicious order.",
    params: { block_above: { type: "number", default: 90, label: "A risk score above this blocks the order" } } },
  { key: "experiments", label: "Experiments", domain: "storefront", icon: "🧪", description: "A/B experiment assignment for storefront surfaces.",
    params: {} },
  { key: "planning", label: "Supply-chain planning", domain: "storefront", icon: "🗺️", description: "Purchase suggestions, replenishment and demand planning for the store's buyers.",
    params: {} },
  { key: "admin_portal", label: "Admin portal link", domain: "storefront", icon: "⬡", description: "The 'Admin Console' link shown to a store's own staff on the storefront.",
    params: {} },

  /* ---------- Mobility: the ride-hailing / dispatch universe (E17) ----------
     Constitution E17: configuration alone yields Uber-, Ola-, DoorDash-, Swiggy- and
     Zomato-class platforms. The engine (lib/mobility.js) reads every value below
     through cap(); nothing about a fare, a match radius or a cancellation penalty is
     hard-coded, so an operator retunes the row and the marketplace follows. */
  { key: "ride_hailing", label: "Ride hailing", domain: "mobility", icon: "🚗", description: "The ride lifecycle: request → accept → arrive → trip start → complete/cancel, with fare construction and per-state cancellation fees.",
    params: {
      base_fare:          { type: "number", default: 2.50, label: "Base fare (pickup charge)" },
      per_km_rate:        { type: "number", default: 1.20, label: "Rate per kilometre" },
      per_min_rate:       { type: "number", default: 0.35, label: "Rate per minute" },
      min_fare:           { type: "number", default: 5.00, label: "Floor below which a completed fare is not charged" },
      booking_fee:        { type: "number", default: 0.50, label: "Fixed platform booking fee added to every fare" },
      platform_take_rate_pct: { type: "number", default: 15, label: "Platform commission on a driver's fare", unit: "%" },
      cancel_fee_accepted:{ type: "number", default: 1.00, label: "Cancellation fee once a driver accepted" },
      cancel_fee_midtrip: { type: "number", default: 5.00, label: "Cancellation fee once the trip started" }
    } },
  { key: "dynamic_pricing", label: "Surge / dynamic pricing", domain: "mobility", icon: "📈", description: "A multiplier raised by active surge zones and by the live demand/supply ratio, capped by configuration.",
    params: {
      surge_cap_multiplier: { type: "number", default: 3, label: "The multiplier is never raised above this ceiling" },
      demand_supply_enabled:{ type: "bool", default: true, label: "Raise the multiplier from the live open-rides / idle-drivers ratio" },
      demand_supply_step:   { type: "number", default: 1, label: "Each whole step of ratio above 1 adds one increment" },
      demand_supply_bps:    { type: "number", default: 15, label: "Points added per step (15 = +0.15%)", unit: "bps" },
      demand_supply_max_ratio: { type: "number", default: 3, label: "The ratio assumed when no driver is idle" }
    } },
  { key: "dispatch", label: "Dispatch & matching", domain: "mobility", icon: "🛰️", description: "Match a request to the nearest idle driver of the requested kind, with a search radius, ETA construction and auto-dispatch.",
    params: {
      auto_dispatch:          { type: "bool", default: true, label: "Assign a driver automatically on request (off = a manual dispatcher works the queue)" },
      match_radius_km:        { type: "number", default: 5, label: "Maximum distance a candidate driver may be", unit: "km" },
      eta_per_km_minutes:     { type: "number", default: 3, label: "ETA minutes per km of approach distance" },
      eta_pickup_buffer_minutes: { type: "number", default: 2, label: "Flat minutes added to every ETA" },
      unknown_position_penalty_km: { type: "number", default: 2, label: "Distance assumed for a driver with no last-known position", unit: "km" },
      city_centre_offset_km:  { type: "number", default: 0, label: "Subtracted from a driver's stored city distance", unit: "km" }
    } },
  { key: "fleet_management", label: "Fleet & driver management", domain: "mobility", icon: "🚙", description: "Drivers and vehicles: onboarding, online/offline state, vehicle kinds, maintenance state and the health that dispatch ranks on.",
    params: {
      driver_kinds: { type: "json", default: ["car", "suv", "bike", "auto", "van"], label: "Vehicle kinds the console offers" },
      min_rating_to_dispatch: { type: "number", default: 4.0, label: "A driver below this rating is held out of dispatch" }
    } },

  /* ---------- Operations: the ERP / HRMS / SCM universe (E18) ----------
     Constitution E18: configuration alone yields SAP-, Oracle-, ServiceNow- and
     Workday-class platforms. The engine (lib/operations.js) reads every value below
     through cap(); nothing about a tax rate, an overtime multiple, an approval
     threshold, a yield or an internal cost rate is hard-coded. */
  { key: "workforce", label: "HRMS & payroll", domain: "operations", icon: "🧑‍💼", description: "Employees, attendance and the payroll run: base + overtime + allowances, less configured deductions and tax, pro-rated by worked days.",
    params: {
      standard_hours_per_day: { type: "number", default: 8, label: "Standard hours before overtime begins" },
      overtime_multiplier:    { type: "number", default: 1.5, label: "Overtime pay multiple of the hourly rate" },
      allowance_amount:       { type: "number", default: 0, label: "Flat allowance added to every payslip" },
      deduction_flat:         { type: "number", default: 0, label: "Flat deduction before tax" },
      deduction_pct:          { type: "number", default: 0, label: "Deduction as a fraction of gross", unit: "%" },
      tax_rate_pct:           { type: "number", default: 0, label: "Tax applied to the taxable amount", unit: "%" }
    } },
  { key: "procurement", label: "Procurement & SCM", domain: "operations", icon: "🛒", description: "Purchase requests with lines and an approval gate: below the threshold a request self-approves, above it a sign-off is required before the status can advance.",
    params: {
      approval_threshold: { type: "number", default: 0, label: "A request costing more than this needs an approval row (0 = no gate)" },
      default_currency:   { type: "text", default: "USD", label: "Currency a purchase request is estimated in" }
    } },
  { key: "manufacturing", label: "Manufacturing", domain: "operations", icon: "🏭", description: "Work orders consuming a bill of materials, completing at a configured yield with a configured scrap loss, and posting the finished good to inventory.",
    params: {
      yield_pct:  { type: "number", default: 100, label: "Good units as a share of the run", unit: "%" },
      scrap_pct:  { type: "number", default: 0, label: "Units lost to scrap", unit: "%" },
      backflush:  { type: "bool", default: true, label: "Consume the BOM components on completion rather than on release" }
    } },
  { key: "projects", label: "Projects & approvals", domain: "operations", icon: "📐", description: "Projects, tasks and time-logging that accrues to a project's spend at a configured internal cost rate, plus the approval chain gating operational actions.",
    params: {
      internal_cost_per_hour: { type: "number", default: 0, label: "Cost rate applied to logged hours (0 = time is free)", unit: "/hr" },
      approval_levels:        { type: "number", default: 1, label: "Sign-off levels an approval passes through" }
    } }
];

/* ---------- seeding: the catalog becomes rows, once, without clobbering ---------- */
/* the stamped catalog version. A row whose seeded_from differs and that nobody
   has edited follows the catalog when it changes; bump this to revise the seed. */
const CATALOG_STAMP = "cap_v6";   /* v6: the operations universe (E18) joins the catalog —
                                     workforce, procurement, manufacturing, projects. Zero
                                     hard-coded rules: every tax rate, overtime multiple,
                                     approval threshold, yield and cost rate is a param
                                     lib/operations.js reads through cap() */

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
  p2p_transfer: ["finops"], insurance: ["finops"], gift_vouchers: ["finops"],
  /* mobility atoms (E17) — each lights its console leaf; the grant engine derives the
     store surface from the live composition, so a ride-hailing store's nav appears the
     moment the atom is on and never as a package */
  ride_hailing: ["rides"],
  dynamic_pricing: ["rides"],
  dispatch: ["rides"],
  fleet_management: ["fleet"],
  /* operations atoms (E18) — the ERP surface. Each lights its own console leaf; the
     grant engine derives the store nav from the live composition, so an operator
     composing an ERP store sees exactly the atoms they switched on, never a package */
  workforce: ["ops_hr"],
  procurement: ["ops_proc"],
  manufacturing: ["ops_mfg"],
  projects: ["ops_proj"]
};
/* the storefront atoms own no console section — a shopper-facing toggle is not a
   store-console leaf. Declared here so the grant engine never has to special-case
   the domain, and so the console's capability list can label the group. */
const STOREFRONT_KEYS = ["reviews", "qna", "deals", "coupons", "gift_cards", "registry",
  "customer_service", "save_for_later", "countdown", "suggestions", "buy_now", "fiscal_selection",
  "subscribe_save", "membership", "fraud_screen", "experiments", "planning", "admin_portal"];
/* SEED DEFAULTS. These atoms replace settings.features.* booleans that shipped ON
   (or off) for every store. The platform-level `enabled` column is seeded to match
   the old settings default exactly, so an existing store sees no behaviour change on
   the migration — the flag moves house, it does not flip. */
const SEED_ENABLED = { fiscal_selection: false };
function seedEnabled(key) { return SEED_ENABLED[key] !== false; }

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
    if (!ex) D.run("INSERT INTO platform_capabilities(key,label,domain,icon,description,params,sections,enabled,position,seeded_from) VALUES(?,?,?,?,?,?,?,?,?,?)",
      c.key, c.label, c.domain, c.icon, c.description, JSON.stringify(params), JSON.stringify(SECTIONS[c.key] || []), seedEnabled(c.key) ? 1 : 0, i, stamp);
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
   platform level, or never enabled for the tenant, is off.
   One exception, and it is deliberate: the STOREFRONT atoms replace settings
   flags that shipped ON for every store, so a tenant with no explicit row keeps
   the seed default rather than going dark. Marketplace/fintech/trade/qc atoms stay
   opt-in — absence means off — which preserves the parity layer's semantics. */
function tenantDefault(key) {
  return STOREFRONT_KEYS.indexOf(key) >= 0 && seedEnabled(key);
}
function on(tenantId, key) {
  const cap = catalogRow(key);
  if (!cap || !cap.enabled) return false;
  const v = db().get("SELECT enabled FROM capability_values WHERE tenant_id=? AND capability=?", Number(tenantId), key);
  return v ? !!v.enabled : tenantDefault(key);
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
/* the migration bridge: apply a legacy {featureKey: bool} map onto the composition.
   Each storefront atom is switched on or off for the tenant; a key that is not an
   atom is returned untouched so the caller keeps it on the settings row. This is the
   ONE write path the settings save, the onboarding wizard and tenant authoring share,
   so a feature is never written two ways. */
function applyFeatures(tenantId, feats) {
  if (!feats || typeof feats !== "object") return {};
  const leftover = {};
  for (const [k, v] of Object.entries(feats)) {
    const key = String(k).replace(/([A-Z])/g, (_, c) => "_" + c.toLowerCase());
    if (STOREFRONT_KEYS.indexOf(key) >= 0) {
      if (v) enable(tenantId, key, null, "settings.features"); else disable(tenantId, key);
    } else leftover[k] = !!v;
  }
  return leftover;
}
/* the settings row only persists keys that are NOT atoms — the atoms own their own
   rows. Reading back what a store still holds outside the catalog. */
function leftoverFeatures(tenantId) {
  const out = {};
  try {
    const row = db().get("SELECT value FROM settings WHERE tenant_id=? AND key='features'", Number(tenantId) || 1);
    const saved = row ? J(row.value, {}) : {};
    for (const k of Object.keys(saved)) {
      const key = String(k).replace(/([A-Z])/g, (_, c) => "_" + c.toLowerCase());
      if (STOREFRONT_KEYS.indexOf(key) < 0) out[k] = saved[k];
    }
  } catch (e) { }
  return out;
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
  /* a default-on atom with no explicit row is still part of the composition —
     the platform a tenant "is" includes what it has not switched off */
  for (const key of STOREFRONT_KEYS) {
    if (out.capabilities[key]) continue;
    if (on(tenantId, key)) {
      const cap = catalogRow(key);
      const p = {};
      for (const [k, v] of Object.entries(cap.params || {})) p[k] = v.default;
      out.capabilities[key] = { enabled: true, domain: cap.domain, label: cap.label, params: p, defaulted: true };
    }
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
  try { require("./settings.js").bust(tenantId); } catch (e) { }
  return compositionOf(tenantId);
}
function disable(tenantId, key) {
  /* a default-on atom has no row to UPDATE — switching it off must INSERT an
     explicit enabled=0, or the tenant default keeps it alive */
  db().run("INSERT INTO capability_values(tenant_id,capability,enabled,params,notes) VALUES(?,?,0,'','') ON CONFLICT(tenant_id,capability) DO UPDATE SET enabled=0",
    Number(tenantId), key);
  try { require("./settings.js").bust(tenantId); } catch (e) { }
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
    } },
  /* E17 · the mobility universe: the constitution names Uber-, Ola-, DoorDash-, Swiggy-
     and Zomato-class platforms as configuration, not code. The four atoms are the whole
     platform — the fare, the surge, the match and the fleet — each retuned per store */
  { key: "blend_mobility", label: "Mobility blend", description: "A worked example: ride hailing with surge pricing, nearest-driver dispatch and a fleet registry — the composition a ride-hailing or delivery operator would recognise.",
    capabilities: {
      ride_hailing:     { params: { base_fare: 2.50, per_km_rate: 1.20, per_min_rate: 0.35, min_fare: 5.00, booking_fee: 0.50, platform_take_rate_pct: 15 } },
      dynamic_pricing:  { params: { surge_cap_multiplier: 3, demand_supply_enabled: true } },
      dispatch:         { params: { auto_dispatch: true, match_radius_km: 5, eta_per_km_minutes: 3 } },
      fleet_management: { params: { driver_kinds: ["car", "suv", "bike", "auto", "van"], min_rating_to_dispatch: 4.0 } }
    } },
  /* E18 · the operations universe: the constitution names SAP-, Oracle-, ServiceNow- and
     Workday-class platforms as configuration, not code. Registering an ERP is now a
     platform type, not an atom-by-atom build */
  { key: "blend_operations", label: "Operations blend", description: "A worked example: HRMS and payroll, procurement with an approval gate, manufacturing with yield and scrap, and projects with an approval chain — the composition an ERP operator would recognise.",
    capabilities: {
      workforce:     { params: { standard_hours_per_day: 8, overtime_multiplier: 1.5, tax_rate_pct: 0 } },
      procurement:   { params: { approval_threshold: 0, default_currency: "USD" } },
      manufacturing: { params: { yield_pct: 100, scrap_pct: 0, backflush: true } },
      projects:      { params: { approval_levels: 1, internal_cost_per_hour: 0 } }
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
  /* a platform-level switch changes every tenant's derived features — drop the
     whole settings cache so no store serves a stale snapshot */
  try { require("./settings.js").bust(0); } catch (e) { }
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
  CATALOG, PRESETS, SECTIONS, STOREFRONT_KEYS, SEED_ENABLED, seed, seedPresets,
  catalogRow, catalogKeys, on, params, cap, sectionsOf, tenantDefault,
  compositionOf, enable, disable, applyPreset, applyFeatures, leftoverFeatures,
  catalog, presets, coerce, tune, setPlatform, savePreset, removePreset,
  define, undefine
};
