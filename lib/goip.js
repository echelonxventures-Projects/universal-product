/* GOIP Ω∞ — GLOBAL OFFER INFRASTRUCTURE PLATFORM
   Universal Incentive · Offer · Reward · Value-Exchange operating system for LUXORA.

   GOIP is not a coupon/offer/promotion/reward/cashback/gift-card/affiliate platform. It is the
   constitutional layer those things are *instances* of: one VALUE EXCHANGE record, resolved through
   one CONTEXT, gated by declared CONDITIONS and ELIGIBILITY, paying a registry-declared BENEFIT,
   EXECUTED once, SETTLED to its funding parties and AUDITed on a hash chain.

   ZERO DUPLICATE / ZERO OVERLAP is a design rule, not a slogan — every concept has exactly ONE home:
     value-exchange math ............ lib/offers.js  (HANDLERS; GOIP registers new benefit handlers there)
     candidate selection + stacking . lib/offers.js  evaluate() (GOIP passes constitutional filter/rank hooks)
     money ledger / wallet .......... lib/offers.js  credit()/debit() → wallets + wallet_entries
     issued codes ................... coupons        redemption ledger → coupon_redemptions
     metering / invoices ............ lib/billing.js recordUsage()
     registries (all of them) ....... meta_lists     via lib/registry.js list() → editable in Data Studio
     graph .......................... links          via db.addLink()
     audit .......................... audit_log      hash-chained, via db.audit()
     events ......................... lib/events.js  emit()
     policy gates ................... lib/security.js policy()
   GOIP owns ONLY what has no home: the constitution, the capability router, context resolution, the
   temporal/spatial/economic/reality domains, the 67-domain map, the condition engine, attribution,
   funding budgets, settlement/payout runs, entitlements, intelligence, governance state and
   commercialization. Four tables exist for exactly those: goip_touchpoints, goip_budgets,
   goip_settlements, goip_entitlements.

   Every list below is SEEDED into meta_lists (INSERT OR IGNORE) — after first boot the DATABASE is the
   source of truth and new calendars, planets, economic units, benefits, domains, channels, attribution
   models, billing models or whole civilizations are added in Data Studio with no code change. */
"use strict";

let _db = null;
const db = () => _db || (_db = require("./db.js"));
const offersMod = () => require("./offers.js");
const billingMod = () => require("./billing.js");
const registryMod = () => require("./registry.js");
const modulesMod = () => require("./modules.js");
const securityMod = () => require("./security.js");
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };
const r2 = n => +Number(n || 0).toFixed(2);
const r4 = n => +Number(n || 0).toFixed(4);
const nowIso = () => new Date().toISOString();
const today = () => new Date().toISOString().slice(0, 10);
const period = d => (d || new Date()).toISOString().slice(0, 7);
const arr = v => Array.isArray(v) ? v : (v == null || v === "" ? [] : [v]);
const S = v => String(v == null ? "" : v);

/* ═══════════════ 1 · CORE CONSTITUTIONAL ABSTRACTION (the 8-stage chain) ═══════════════ */
const CONSTITUTION = [
  { step: 1, key: "value_exchange", name: "Value Exchange", question: "What is being exchanged?", owner: "offers", engine: "governance" },
  { step: 2, key: "context", name: "Context", question: "In which reality/time/place/economy/audience?", owner: "goip", engine: "context_resolution" },
  { step: 3, key: "conditions", name: "Conditions", question: "Which declared conditions must hold?", owner: "goip", engine: "qualification" },
  { step: 4, key: "eligibility", name: "Eligibility", question: "Is this exchange permitted at all?", owner: "goip", engine: "eligibility" },
  { step: 5, key: "benefit", name: "Benefit", question: "What value is produced, in which unit?", owner: "offers", engine: "benefit_resolution" },
  { step: 6, key: "execution", name: "Execution", question: "Apply / redeem / issue / grant — once.", owner: "offers", engine: "decision" },
  { step: 7, key: "settlement", name: "Settlement", question: "Who funded it and who gets paid?", owner: "goip", engine: "governance" },
  { step: 8, key: "audit", name: "Audit", question: "Prove every step, tamper-evident.", owner: "audit_log", engine: "governance" }
];

/* ═══════════════ 2 · UNIVERSAL CAPABILITY LAYER (22) ═══════════════
   Consumers speak ONLY these verbs. They never learn the words coupon, cashback, reward, gift card,
   discount, promotion, commission, referral, subsidy or any future construct. */
const CAPABILITIES = [
  { key: "create", name: "Create Value Exchange", stage: "value_exchange", engine: "governance", writes: "offers", meter: "goip.create", scope: "tenant" },
  { key: "clone", name: "Clone Value Exchange", stage: "value_exchange", engine: "governance", writes: "offers", meter: "goip.create", scope: "tenant" },
  { key: "publish", name: "Publish Value Exchange", stage: "value_exchange", engine: "governance", writes: "offers", meter: "goip.publish", scope: "tenant" },
  { key: "discover", name: "Discover Value Exchange", stage: "context", engine: "discovery", writes: null, meter: "goip.decision", scope: "any" },
  { key: "search", name: "Search Value Exchange", stage: "context", engine: "discovery", writes: null, meter: "goip.decision", scope: "any" },
  { key: "compare", name: "Compare Value Exchange", stage: "benefit", engine: "ranking", writes: null, meter: "goip.decision", scope: "any" },
  { key: "validate", name: "Validate Value Exchange", stage: "conditions", engine: "qualification", writes: null, meter: "goip.decision", scope: "any" },
  { key: "reserve", name: "Reserve Value Exchange", stage: "execution", engine: "decision", writes: "coupon_redemptions", meter: "goip.reserve", scope: "tenant" },
  { key: "activate", name: "Activate Value Exchange", stage: "execution", engine: "governance", writes: "coupon_redemptions", meter: "goip.reserve", scope: "any" },
  { key: "issue", name: "Issue Value Exchange", stage: "execution", engine: "governance", writes: "coupons", meter: "goip.issue", scope: "tenant" },
  { key: "track", name: "Track Value Exchange", stage: "context", engine: "personalization", writes: "goip_touchpoints", meter: "goip.track", scope: "any" },
  { key: "attribute", name: "Attribute Value Exchange", stage: "settlement", engine: "decision", writes: null, meter: "goip.attribute", scope: "tenant" },
  { key: "apply", name: "Apply Value Exchange", stage: "benefit", engine: "benefit_resolution", writes: null, meter: "goip.decision", scope: "any" },
  { key: "redeem", name: "Redeem Value Exchange", stage: "execution", engine: "decision", writes: "coupon_redemptions", meter: "goip.redemption", scope: "tenant" },
  { key: "settle", name: "Settle Value Exchange", stage: "settlement", engine: "governance", writes: "goip_settlements", meter: "goip.settlement", scope: "platform" },
  { key: "fund", name: "Fund Value Exchange", stage: "settlement", engine: "governance", writes: "goip_budgets", meter: "goip.fund", scope: "tenant" },
  { key: "pay", name: "Pay Value Exchange", stage: "settlement", engine: "governance", writes: "goip_settlements", meter: "goip.payout", scope: "platform" },
  { key: "optimize", name: "Optimize Value Exchange", stage: "benefit", engine: "optimization", writes: null, meter: "goip.intelligence", scope: "tenant" },
  { key: "forecast", name: "Forecast Value Exchange", stage: "settlement", engine: "forecasting", writes: null, meter: "goip.intelligence", scope: "tenant" },
  { key: "simulate", name: "Simulate Value Exchange", stage: "benefit", engine: "simulation", writes: null, meter: "goip.intelligence", scope: "tenant" },
  { key: "govern", name: "Govern Value Exchange", stage: "audit", engine: "governance", writes: "offers", meter: "goip.govern", scope: "tenant" },
  { key: "audit", name: "Audit Value Exchange", stage: "audit", engine: "governance", writes: null, meter: "goip.govern", scope: "tenant" }
];

/* ═══════════════ 3 · UNIVERSAL DECISION FABRIC (18 engines, one job each) ═══════════════ */
const ENGINES = [
  { key: "context_resolution", name: "Context Resolution Engine", owns: "fills all 25 context dimensions", impl: "goip.resolveContext" },
  { key: "eligibility", name: "Eligibility Engine", owns: "is this exchange permitted in this context", impl: "goip.eligibility" },
  { key: "qualification", name: "Qualification Engine", owns: "declared conditions over the resolved context", impl: "goip.qualify" },
  { key: "decision", name: "Decision Engine", owns: "which qualified exchanges actually execute", impl: "offers.evaluate + goip hooks" },
  { key: "discovery", name: "Offer Discovery Engine", owns: "what is available to this subject now", impl: "goip.discover" },
  { key: "benefit_resolution", name: "Benefit Resolution Engine", owns: "benefit → concrete units", impl: "offers.HANDLERS (+GOIP handlers)" },
  { key: "conflict_resolution", name: "Conflict Resolution Engine", owns: "same-domain collisions", impl: "goip.resolveConflicts" },
  { key: "stacking", name: "Stacking Engine", owns: "stack groups / exclusivity / max count", impl: "offers.evaluate" },
  { key: "ranking", name: "Ranking Engine", owns: "order candidates by objective", impl: "goip.rank" },
  { key: "optimization", name: "Optimization Engine", owns: "parameter proposals against an objective", impl: "goip.optimize" },
  { key: "recommendation", name: "Recommendation Engine", owns: "best next exchange for a subject", impl: "goip.recommend" },
  { key: "personalization", name: "Personalization Engine", owns: "subject segments + behaviour", impl: "goip.personalize" },
  { key: "pricing", name: "Pricing Engine", owns: "net price after value exchange", impl: "goip.price" },
  { key: "simulation", name: "Simulation Engine", owns: "what-if over real or synthetic carts", impl: "goip.simulate" },
  { key: "forecasting", name: "Forecasting Engine", owns: "burn / liability projection", impl: "goip.forecast" },
  { key: "fraud", name: "Fraud Engine", owns: "abuse signals per subject/instrument", impl: "goip.fraudScore" },
  { key: "risk", name: "Risk Engine", owns: "exposure of an instrument", impl: "goip.riskScore" },
  { key: "governance", name: "Governance Engine", owns: "policy, approval, lifecycle, version, audit", impl: "goip.govern" }
];

/* ═══════════════ 4 · UNIVERSAL CONTEXT FABRIC (25 dimensions) ═══════════════ */
const CONTEXTS = [
  { key: "reality", name: "Reality Context", source: "registry:goipRealities" },
  { key: "temporal", name: "Temporal Context", source: "registry:goipCalendars" },
  { key: "spatial", name: "Spatial Context", source: "registry:goipSpatialSystems" },
  { key: "economic", name: "Economic Context", source: "registry:goipEconomicUnits + currencies" },
  { key: "governance", name: "Governance Context", source: "security.policy()" },
  { key: "audience", name: "Audience Context", source: "orders + goip_entitlements" },
  { key: "identity", name: "Identity Context", source: "users / session owner" },
  { key: "behavioral", name: "Behavioral Context", source: "view_history + orders" },
  { key: "product", name: "Product Context", source: "products" },
  { key: "catalog", name: "Catalog Context", source: "taxonomy + departments" },
  { key: "cart", name: "Cart Context", source: "cart items passed by the caller" },
  { key: "session", name: "Session Context", source: "sessions" },
  { key: "device", name: "Device Context", source: "caller-supplied" },
  { key: "market", name: "Market Context", source: "tenants + countries" },
  { key: "inventory", name: "Inventory Context", source: "inventory + skus" },
  { key: "risk", name: "Risk Context", source: "goip.fraudScore" },
  { key: "organization", name: "Organization Context", source: "tenants" },
  { key: "merchant", name: "Merchant Context", source: "tenants + sellers" },
  { key: "provider", name: "Provider Context", source: "provider_defs" },
  { key: "partner", name: "Partner Context", source: "suppliers + links" },
  { key: "creator", name: "Creator Context", source: "goip_touchpoints (party_type=creator)" },
  { key: "channel", name: "Channel Context", source: "registry:goipDistribution" },
  { key: "event", name: "Event Context", source: "caller-supplied + events bus" },
  { key: "campaign", name: "Campaign Context", source: "offers.campaign" },
  { key: "ai", name: "AI Context", source: "ai.tierOf" }
];

/* ═══════════════ 5 · UNIVERSAL TEMPORAL DOMAIN (no assumption of year/month/week/day/timezone) ═══════════════ */
const CALENDARS = [
  { key: "gregorian", name: "Gregorian", chronology: "solar_terrestrial", epoch: "0001-01-01", day_seconds: 86400, year_days: 365.2425, authority: "ISO 8601" },
  { key: "iso_week", name: "ISO week calendar", chronology: "solar_terrestrial", epoch: "0001-01-01", day_seconds: 86400, year_days: 364, authority: "ISO 8601" },
  { key: "islamic", name: "Islamic (Hijri)", chronology: "lunar_terrestrial", epoch: "0622-07-16", day_seconds: 86400, year_days: 354.367, authority: "Umm al-Qura" },
  { key: "hebrew", name: "Hebrew", chronology: "lunisolar_terrestrial", epoch: "-3760-09-07", day_seconds: 86400, year_days: 365.2468, authority: "Hillel II" },
  { key: "fiscal", name: "Fiscal calendar", chronology: "solar_terrestrial", epoch: "anchor:fiscal_year_start", day_seconds: 86400, year_days: 365.2425, authority: "tenant" },
  { key: "academic", name: "Academic calendar", chronology: "solar_terrestrial", epoch: "anchor:term_start", day_seconds: 86400, year_days: 365.2425, authority: "institution" },
  { key: "lunar", name: "Lunar (synodic)", chronology: "lunar_terrestrial", epoch: "2000-01-06", day_seconds: 86400, year_days: 354.367, authority: "synodic month 29.530589 d" },
  { key: "mars_darian", name: "Mars Colony (Darian)", chronology: "solar_martian", epoch: "1609-03-11", day_seconds: 88775.244, year_days: 668.5991, authority: "Darian" },
  { key: "federation", name: "Federation Standard", chronology: "federation_standard", epoch: "2161-01-01", day_seconds: 86400, year_days: 365, authority: "federation" },
  { key: "custom_planetary", name: "Custom Planetary", chronology: "declared", epoch: "declared", day_seconds: 0, year_days: 0, authority: "registry" }
];
const CHRONOLOGIES = [
  { key: "solar_terrestrial", name: "Solar (Earth)", base_unit: "second", rotation_seconds: 86400 },
  { key: "lunar_terrestrial", name: "Lunar (Earth)", base_unit: "second", rotation_seconds: 86400 },
  { key: "lunisolar_terrestrial", name: "Lunisolar (Earth)", base_unit: "second", rotation_seconds: 86400 },
  { key: "solar_martian", name: "Solar (Mars sol)", base_unit: "second", rotation_seconds: 88775.244 },
  { key: "solar_lunar_colony", name: "Solar (Moon colony)", base_unit: "second", rotation_seconds: 2551442.8 },
  { key: "federation_standard", name: "Federation standard", base_unit: "second", rotation_seconds: 86400 },
  { key: "declared", name: "Declared by registry", base_unit: "second", rotation_seconds: 0 }
];
/* temporal measurement: every unit declares its length in the base unit (seconds). Nothing is assumed. */
const TEMPORAL_UNITS = [
  { key: "second", name: "Second", seconds: 1 }, { key: "minute", name: "Minute", seconds: 60 },
  { key: "hour", name: "Hour", seconds: 3600 }, { key: "day", name: "Day (Earth)", seconds: 86400 },
  { key: "sol", name: "Sol (Mars day)", seconds: 88775.244 }, { key: "week", name: "Week", seconds: 604800 },
  { key: "month", name: "Month (mean Gregorian)", seconds: 2629746 }, { key: "quarter", name: "Quarter", seconds: 7889238 },
  { key: "year", name: "Year (mean Gregorian)", seconds: 31556952 }, { key: "mars_year", name: "Mars year", seconds: 59355072 },
  { key: "lunation", name: "Lunation", seconds: 2551442.8 }, { key: "cycle", name: "Declared cycle", seconds: 0 }
];
const TEMPORAL_CONVERSIONS = { sol_per_day: 1.0274912517, day_per_sol: 0.9732696, mars_year_days: 686.98, lunation_days: 29.530589 };

/* ═══════════════ 6 · UNIVERSAL SPATIAL DOMAIN (no assumption of country/state/city/lat/long) ═══════════════ */
const SPATIAL_SYSTEMS = [
  { key: "earth_admin", name: "Earth · administrative", body: "earth", levels: ["planet", "country", "region", "city", "district"], coordinate: "wgs84", calendar: "gregorian" },
  { key: "mars_admin", name: "Mars · territorial", body: "mars", levels: ["planet", "territory", "sector", "habitat"], coordinate: "mars_areographic", calendar: "mars_darian" },
  { key: "lunar_admin", name: "Moon · colonial", body: "moon", levels: ["body", "colony", "dome", "bay"], coordinate: "lunar_selenographic", calendar: "lunar" },
  { key: "galactic", name: "Galactic · zonal", body: "galaxy-7", levels: ["galaxy", "zone", "system", "station"], coordinate: "galactic_polar", calendar: "federation" },
  { key: "network", name: "Network · non-physical", body: "virtual", levels: ["realm", "shard", "room"], coordinate: "none" },
  { key: "declared", name: "Declared hierarchy", body: "any", levels: [], coordinate: "declared" }
];
const COORDINATE_SYSTEMS = [
  { key: "wgs84", name: "WGS-84 geodetic", axes: ["lat", "lon", "alt"], unit: "degree/metre" },
  { key: "mars_areographic", name: "Areographic", axes: ["lat", "lon", "elev"], unit: "degree/metre" },
  { key: "lunar_selenographic", name: "Selenographic", axes: ["lat", "lon", "elev"], unit: "degree/metre" },
  { key: "galactic_polar", name: "Galactic polar", axes: ["l", "b", "r"], unit: "degree/parsec" },
  { key: "none", name: "Non-spatial", axes: [], unit: "" },
  { key: "declared", name: "Declared", axes: [], unit: "declared" }
];
/* hierarchy nodes: path is the ONLY truth; prefix-matching scopes any exchange to any place, anywhere. */
const SPATIAL_NODES = [
  { key: "earth", system: "earth_admin", parent: null, name: "Earth", level: "planet" },
  { key: "earth.in", system: "earth_admin", parent: "earth", name: "India", level: "country" },
  { key: "earth.in.bihar", system: "earth_admin", parent: "earth.in", name: "Bihar", level: "region" },
  { key: "earth.in.bihar.patna", system: "earth_admin", parent: "earth.in.bihar", name: "Patna", level: "city" },
  { key: "earth.us", system: "earth_admin", parent: "earth", name: "United States", level: "country" },
  { key: "earth.ae", system: "earth_admin", parent: "earth", name: "United Arab Emirates", level: "country" },
  { key: "mars", system: "mars_admin", parent: null, name: "Mars", level: "planet" },
  { key: "mars.olympus", system: "mars_admin", parent: "mars", name: "Olympus Territory", level: "territory" },
  { key: "mars.olympus.sector-7", system: "mars_admin", parent: "mars.olympus", name: "Sector-7", level: "sector" },
  { key: "moon", system: "lunar_admin", parent: null, name: "Moon", level: "body" },
  { key: "moon.alpha", system: "lunar_admin", parent: "moon", name: "Colony Alpha", level: "colony" },
  { key: "galaxy-7", system: "galactic", parent: null, name: "Galaxy-7", level: "galaxy" },
  { key: "galaxy-7.zone-22", system: "galactic", parent: "galaxy-7", name: "Zone-22", level: "zone" },
  { key: "virtual", system: "network", parent: null, name: "Virtual realm", level: "realm" }
];

/* ═══════════════ 7 · UNIVERSAL ECONOMIC DOMAIN (no hardcoded currency) ═══════════════ */
const ECONOMIC_UNITS = [
  { key: "USD", name: "US Dollar", class: "fiat", decimals: 2, base_rate: 1, settleable: true, source: "currencies" },
  { key: "EUR", name: "Euro", class: "fiat", decimals: 2, base_rate: 1.09, settleable: true, source: "currencies" },
  { key: "INR", name: "Indian Rupee", class: "fiat", decimals: 2, base_rate: 0.012, settleable: true, source: "currencies" },
  { key: "MARS_CREDIT", name: "Mars Credits", class: "colonial", decimals: 2, base_rate: 0, settleable: false, source: "registry" },
  { key: "LUNAR_TOKEN", name: "Lunar Tokens", class: "colonial", decimals: 0, base_rate: 0, settleable: false, source: "registry" },
  { key: "FED_CREDIT", name: "Federation Credits", class: "federation", decimals: 2, base_rate: 0, settleable: false, source: "registry" },
  { key: "CARBON", name: "Carbon Credits", class: "environmental", decimals: 3, base_rate: 0, settleable: true, source: "registry" },
  { key: "ENERGY", name: "Energy Credits", class: "utility", decimals: 3, base_rate: 0, settleable: true, source: "registry" },
  { key: "RESOURCE", name: "Resource Units", class: "commodity", decimals: 3, base_rate: 0, settleable: true, source: "registry" },
  { key: "POINT", name: "Reward Points", class: "loyalty", decimals: 0, base_rate: 0.01, settleable: false, source: "registry" },
  { key: "COIN", name: "Coins", class: "loyalty", decimals: 0, base_rate: 0.01, settleable: false, source: "registry" },
  { key: "TOKEN", name: "Tokens", class: "digital", decimals: 0, base_rate: 0, settleable: false, source: "registry" }
];
const ASSET_CLASSES = ["fiat", "colonial", "federation", "environmental", "utility", "commodity", "loyalty", "digital", "entitlement", "declared"];
const REALITIES = [
  { key: "physical", name: "Physical reality" }, { key: "digital", name: "Digital reality" },
  { key: "virtual", name: "Virtual / immersive reality" }, { key: "hybrid", name: "Hybrid phygital" },
  { key: "simulated", name: "Simulated / sandbox" }, { key: "any", name: "Reality-agnostic" }
];

/* ═══════════════ 8 · CONSTITUTIONAL DOMAIN ECOSYSTEM (67) ═══════════════
   Every domain names the ONE store that owns it and the exact discriminator that isolates its rows.
   Two domains never share a discriminator — that is what "zero overlap" means here, mechanically. */
const D = (n, key, name, owner, discriminator, fabric) => ({ n, key, name, owner, discriminator, fabric });
const DOMAINS = [
  D(1, "incentive", "Incentive Domain", "offers", "every value-exchange row (the root record)", "capability"),
  D(2, "offer", "Offer Domain", "offers", "source='offer'", "capability"),
  D(3, "coupon", "Coupon Domain", "coupons", "coupons.kind in code/single_use/multi_use/first_order", "benefit"),
  D(4, "promotion", "Promotion Domain", "promotions", "legacy per-store promotions (read-through)", "benefit"),
  D(5, "discount", "Discount Domain", "offers", "direction='discount'", "benefit"),
  D(6, "cashback", "Cashback Domain", "offers", "benefit in cashback/deferred_cashback", "benefit"),
  D(7, "reward", "Reward Domain", "offers", "benefit in reward_points/coins", "benefit"),
  D(8, "gift_card", "Gift Card Domain", "coupons", "kind='gift_card'", "benefit"),
  D(9, "voucher", "Voucher Domain", "coupons", "kind in bank_voucher/bulk_issued", "benefit"),
  D(10, "loyalty", "Loyalty Domain", "goip_entitlements", "benefit='tier_upgrade'", "benefit"),
  D(11, "membership", "Membership Domain", "goip_entitlements", "benefit='membership_upgrade'", "benefit"),
  D(12, "referral", "Referral Domain", "goip_touchpoints", "party_type='referrer'", "attribution"),
  D(13, "affiliate", "Affiliate Domain", "goip_touchpoints", "party_type='affiliate'", "attribution"),
  D(14, "creator", "Creator Domain", "goip_touchpoints", "party_type='creator'", "attribution"),
  D(15, "influencer", "Influencer Domain", "goip_touchpoints", "party_type='influencer'", "attribution"),
  D(16, "deal", "Deal Domain", "offers", "campaign<>'' and distribution includes a public channel", "distribution"),
  D(17, "pricing", "Pricing Domain", "products.pricing_rules", "tier/B2B price rules on the product", "benefit"),
  D(18, "dynamic_pricing", "Dynamic Pricing Domain", "offers", "benefit='dynamic_discount'", "benefit"),
  D(19, "auction", "Auction Domain", "tenders", "tender lifecycle → award → contract", "benefit"),
  D(20, "subscription_benefit", "Subscription Benefit Domain", "offers", "channel='subscription'", "benefit"),
  D(21, "partner_benefit", "Partner Benefit Domain", "offers", "funder='partner'", "funding"),
  D(22, "corporate_benefit", "Corporate Benefit Domain", "offers", "funder='corporate'", "funding"),
  D(23, "government_benefit", "Government Benefit Domain", "offers", "funder='government'", "funding"),
  D(24, "employee_benefit", "Employee Benefit Domain", "offers", "rules.audience='employee'", "funding"),
  D(25, "gamification", "Gamification Domain", "goip_entitlements", "rules.game<>'' grants", "benefit"),
  D(26, "audience", "Audience Domain", "meta_lists:goipAudiences", "declared audience definitions", "context"),
  D(27, "segmentation", "Segmentation Domain", "goip.personalize", "computed segments per subject", "context"),
  D(28, "campaign", "Campaign Domain", "offers", "offers.campaign grouping", "distribution"),
  D(29, "discovery", "Discovery Domain", "capability:discover", "context-eligible set for a subject", "capability"),
  D(30, "search", "Search Domain", "capability:search", "text/domain/benefit query over exchanges", "capability"),
  D(31, "recommendation", "Recommendation Domain", "engine:recommendation", "ranked next-best exchange", "intelligence"),
  D(32, "personalization", "Personalization Domain", "engine:personalization", "subject-level tailoring", "intelligence"),
  D(33, "distribution", "Distribution Domain", "offers.distribution", "channels an exchange is published to", "distribution"),
  D(34, "syndication", "Syndication Domain", "webhooks + feeds", "outbound feeds of exchanges", "distribution"),
  D(35, "marketplace", "Marketplace Domain", "tenants", "mode='marketplace'", "context"),
  D(36, "merchant", "Merchant Domain", "tenants", "the operating store", "context"),
  D(37, "brand", "Brand Domain", "offers.brand_ref", "brand attached to an exchange", "context"),
  D(38, "provider", "Provider Domain", "provider_defs", "payment/shipping/notification/ai/marketing providers", "context"),
  D(39, "partner", "Partner Domain", "suppliers", "supply + benefit partners", "context"),
  D(40, "exchange", "Exchange Domain", "meta_lists:goipEconomicUnits + fx_rates", "unit → unit conversion", "economic"),
  D(41, "attribution", "Attribution Domain", "goip_touchpoints", "attribution model run over touchpoints", "attribution"),
  D(42, "tracking", "Tracking Domain", "goip_touchpoints", "raw touchpoint capture", "attribution"),
  D(43, "wallet", "Wallet Domain", "wallets + wallet_entries", "owner balances and entries", "settlement"),
  D(44, "treasury", "Treasury Domain", "goip_budgets", "aggregate position across all budgets", "funding"),
  D(45, "funding", "Funding Domain", "goip_budgets", "who funds an exchange (rows)", "funding"),
  D(46, "budget", "Budget Domain", "goip_budgets", "allocated / reserved ceilings", "funding"),
  D(47, "payment", "Payment Domain", "payments", "gateway money movement", "settlement"),
  D(48, "settlement", "Settlement Domain", "goip_settlements", "status='accrued'|'approved'", "settlement"),
  D(49, "reconciliation", "Reconciliation Domain", "goip_settlements", "status='reconciled'", "settlement"),
  D(50, "payout", "Payout Domain", "goip_settlements", "status='paid'", "settlement"),
  D(51, "fraud", "Fraud Domain", "engine:fraud", "abuse scoring", "governance"),
  D(52, "risk", "Risk Domain", "engine:risk", "exposure scoring", "governance"),
  D(53, "analytics", "Analytics Domain", "coupon_redemptions", "offers.analytics aggregates", "intelligence"),
  D(54, "forecasting", "Forecasting Domain", "engine:forecasting", "burn / liability projection", "intelligence"),
  D(55, "simulation", "Simulation Domain", "engine:simulation", "what-if runs (never writes)", "intelligence"),
  D(56, "ai", "AI Domain", "ai.js", "capabilities, providers, metering", "intelligence"),
  D(57, "agent", "Agent Domain", "capability router", "agent/MCP callers speak capabilities only", "capability"),
  D(58, "governance", "Governance Domain", "offers.governance", "lifecycle + approval state machine", "governance"),
  D(59, "compliance", "Compliance Domain", "compliance_records", "certifications, validity, jurisdiction", "governance"),
  D(60, "knowledge", "Knowledge Domain", "goip.manifest()", "the platform's machine-readable self-description", "governance"),
  D(61, "registry", "Registry Domain", "meta_lists", "every list the platform obeys", "context"),
  D(62, "universal_context", "Universal Context Domain", "goip.resolveContext", "the 25 resolved dimensions", "context"),
  D(63, "universal_temporal", "Universal Temporal Domain", "meta_lists:goipCalendars", "calendars, chronologies, units, conversions", "context"),
  D(64, "universal_spatial", "Universal Spatial Domain", "meta_lists:goipSpatialNodes", "systems, coordinates, hierarchy paths", "context"),
  D(65, "universal_economic", "Universal Economic Domain", "meta_lists:goipEconomicUnits", "units, classes, rates", "economic"),
  D(66, "universal_governance", "Universal Governance Domain", "security.policy()", "platform policy over every store", "governance"),
  D(67, "universal_reality", "Universal Reality Domain", "meta_lists:goipRealities", "reality models an exchange may bind to", "context")
];

/* ═══════════════ 9 · BENEFIT FABRIC (25) ═══════════════
   Each benefit binds to exactly ONE math handler in offers.HANDLERS. Handlers that did not exist are
   registered there by GOIP at seed time — the platform keeps a single benefit-math engine, forever. */
const B = (key, name, type, direction, unit, grants) => ({ key, name, type, direction, unit, grants: grants || "" });
const BENEFITS = [
  B("percentage_discount", "Percentage Discount", "percent", "discount", "%"),
  B("flat_discount", "Flat Discount", "fixed", "discount", "amount"),
  B("tier_discount", "Tier Discount", "tier_qty", "discount", "amount"),
  B("volume_discount", "Volume Discount", "multi_buy", "discount", "amount"),
  B("dynamic_discount", "Dynamic Discount", "dynamic_discount", "discount", "%"),
  B("cashback", "Cashback", "cashback", "credit", "%"),
  B("deferred_cashback", "Deferred Cashback", "deferred_cashback", "credit", "%"),
  B("reward_points", "Reward Points", "reward_points", "reward", "POINT"),
  B("coins", "Coins", "coins", "reward", "COIN"),
  B("credits", "Credits", "spend_get_credit", "credit", "amount"),
  B("tokens", "Tokens", "tokens", "reward", "TOKEN"),
  B("gift_card", "Gift Cards", "gift_card_credit", "gift", "amount", "coupon:gift_card"),
  B("voucher", "Vouchers", "voucher_issue", "gift", "amount", "coupon:bank_voucher"),
  B("wallet_value", "Wallet Value", "wallet_value", "credit", "amount"),
  B("free_product", "Free Products", "free_product", "discount", "items"),
  B("free_service", "Free Services", "free_service", "discount", "items"),
  B("free_shipping", "Free Shipping", "free_ship", "free_ship", ""),
  B("membership_upgrade", "Membership Upgrade", "membership_upgrade", "exchange", "tier", "entitlement:membership"),
  B("tier_upgrade", "Tier Upgrade", "tier_upgrade", "exchange", "tier", "entitlement:tier"),
  B("partner_benefit", "Partner Benefits", "partner_benefit", "exchange", "declared", "entitlement:partner"),
  B("corporate_benefit", "Corporate Benefits", "corporate_benefit", "exchange", "declared", "entitlement:corporate"),
  B("government_benefit", "Government Benefits", "government_benefit", "discount", "amount"),
  B("digital_asset", "Digital Assets", "digital_asset", "gift", "TOKEN", "entitlement:asset"),
  B("economic_asset", "Economic Assets", "economic_asset", "gift", "declared", "entitlement:asset"),
  B("future_benefit", "Future Benefits", "future_benefit", "exchange", "declared", "entitlement:declared")
];
/* legacy offer types stay first-class: they are benefits too, already handled by offers.HANDLERS */
/* the benefit/offer type vocabulary is declared once, in offers.js, and seeded
   from there — a second literal copy here duplicated the declaration and could
   drift (Law 002). Removed. */

/* ═══════════════ 10 · DISTRIBUTION FABRIC (16) ═══════════════ */
const DISTRIBUTION = [
  { key: "email", name: "Email", binding: "provider_defs:notification", state: "live" },
  { key: "sms", name: "SMS", binding: "provider_defs:notification", state: "live" },
  { key: "whatsapp", name: "WhatsApp", binding: "provider_defs:notification", state: "live" },
  { key: "push", name: "Push", binding: "provider_defs:notification", state: "live" },
  { key: "in_app", name: "In-App", binding: "storefront + console surfaces", state: "live" },
  { key: "widget", name: "Widget", binding: "GET /api/goip/widget", state: "live" },
  { key: "embedded", name: "Embedded Component", binding: "GET /api/goip/widget?embed=1", state: "live" },
  { key: "partner_feed", name: "Partner Feed", binding: "GET /api/goip/feed/:channel", state: "live" },
  { key: "marketplace_feed", name: "Marketplace Feed", binding: "GET /api/goip/feed/:channel", state: "live" },
  { key: "affiliate_feed", name: "Affiliate Feed", binding: "GET /api/goip/feed/:channel", state: "live" },
  { key: "creator_feed", name: "Creator Feed", binding: "GET /api/goip/feed/:channel", state: "live" },
  { key: "bank_feed", name: "Bank Feed", binding: "GET /api/goip/feed/:channel", state: "live" },
  { key: "pos_feed", name: "POS Feed", binding: "GET /api/goip/feed/:channel", state: "live" },
  { key: "iot_feed", name: "IoT Feed", binding: "GET /api/goip/feed/:channel", state: "live" },
  { key: "ai_feed", name: "AI Feed", binding: "GET /api/goip/feed/:channel", state: "live" },
  { key: "future_channel", name: "Future Distribution Channels", binding: "add a row here — feeds resolve by key", state: "registry" }
];

/* ═══════════════ 11 · ATTRIBUTION FABRIC (12) ═══════════════ */
const ATTRIBUTION = [
  { key: "click", name: "Click Attribution", basis: "touchpoint.kind='click'", model: "last_touch" },
  { key: "view", name: "View Attribution", basis: "touchpoint.kind='view'", model: "linear" },
  { key: "conversion", name: "Conversion Attribution", basis: "touchpoint.kind='conversion'", model: "last_touch" },
  { key: "coupon", name: "Coupon Attribution", basis: "coupon_redemptions.code", model: "deterministic" },
  { key: "affiliate", name: "Affiliate Attribution", basis: "party_type='affiliate'", model: "last_touch" },
  { key: "referral", name: "Referral Attribution", basis: "party_type='referrer'", model: "first_touch" },
  { key: "creator", name: "Creator Attribution", basis: "party_type='creator'", model: "position_based" },
  { key: "partner", name: "Partner Attribution", basis: "party_type='partner'", model: "linear" },
  { key: "cross_device", name: "Cross Device Attribution", basis: "owner identity across device ids", model: "identity_stitch" },
  { key: "cross_channel", name: "Cross Channel Attribution", basis: "distinct channels on the path", model: "linear" },
  { key: "revenue", name: "Revenue Attribution", basis: "order value on the converting touchpoint", model: "deterministic" },
  { key: "commission", name: "Commission Attribution", basis: "attributed revenue × party rate", model: "deterministic" }
];
const ATTRIBUTION_MODELS = ["last_touch", "first_touch", "linear", "position_based", "time_decay", "deterministic", "identity_stitch"];

/* ═══════════════ 12 · FUNDING FABRIC (12) ═══════════════ */
const FUNDING = [
  { key: "merchant", name: "Merchant Funding", party_type: "merchant", kind: "source" },
  { key: "brand", name: "Brand Funding", party_type: "brand", kind: "source" },
  { key: "marketplace", name: "Marketplace Funding", party_type: "marketplace", kind: "source" },
  { key: "partner", name: "Partner Funding", party_type: "partner", kind: "source" },
  { key: "bank", name: "Bank Funding", party_type: "bank", kind: "source" },
  { key: "government", name: "Government Funding", party_type: "government", kind: "source" },
  { key: "corporate", name: "Corporate Funding", party_type: "corporate", kind: "source" },
  { key: "multi_party", name: "Multi-Party Funding", party_type: "split", kind: "source" },
  { key: "budget_allocation", name: "Budget Allocation", party_type: "", kind: "control" },
  { key: "reserve_management", name: "Reserve Management", party_type: "", kind: "control" },
  { key: "burn_rate", name: "Burn Rate", party_type: "", kind: "measure" },
  { key: "forecasting", name: "Funding Forecasting", party_type: "", kind: "measure" }
];
const FUNDERS = ["self", "merchant", "brand", "marketplace", "partner", "bank", "government", "corporate", "platform", "split"];

/* ═══════════════ 13 · SETTLEMENT & PAYOUT FABRIC (11) ═══════════════ */
const SETTLEMENT = [
  { key: "wallet", name: "Wallet", store: "wallets", stage: "hold" },
  { key: "ledger", name: "Ledger", store: "wallet_entries", stage: "record" },
  { key: "treasury", name: "Treasury", store: "goip_budgets", stage: "position" },
  { key: "settlement", name: "Settlement", store: "goip_settlements", stage: "accrue" },
  { key: "reconciliation", name: "Reconciliation", store: "goip_settlements", stage: "reconcile" },
  { key: "recovery", name: "Recovery", store: "coupon_redemptions", stage: "clawback" },
  { key: "revenue_sharing", name: "Revenue Sharing", store: "goip_settlements", stage: "split" },
  { key: "commission", name: "Commission", store: "goip_settlements", stage: "split" },
  { key: "payout", name: "Payout", store: "goip_settlements", stage: "pay" },
  { key: "cross_border", name: "Cross Border Settlement", store: "goip_settlements", stage: "pay" },
  { key: "future_settlement", name: "Future Settlement Models", store: "registry", stage: "declared" }
];
const SETTLEMENT_STATUSES = ["accrued", "approved", "paid", "reconciled", "reversed", "held"];

/* ═══════════════ 14 · INTELLIGENCE FABRIC (15) ═══════════════ */
const INTELLIGENCE = [
  { key: "deal", name: "Deal Intelligence", impl: "goip.intel.deal" },
  { key: "offer", name: "Offer Intelligence", impl: "goip.intel.offer" },
  { key: "price", name: "Price Intelligence", impl: "goip.intel.price" },
  { key: "audience", name: "Audience Intelligence", impl: "goip.intel.audience" },
  { key: "merchant", name: "Merchant Intelligence", impl: "goip.intel.merchant" },
  { key: "provider", name: "Provider Intelligence", impl: "goip.intel.provider" },
  { key: "partner", name: "Partner Intelligence", impl: "goip.intel.partner" },
  { key: "fraud", name: "Fraud Intelligence", impl: "goip.intel.fraud" },
  { key: "optimization", name: "Optimization Intelligence", impl: "goip.intel.optimization" },
  { key: "forecast", name: "Forecast Intelligence", impl: "goip.intel.forecast" },
  { key: "recommendation", name: "Recommendation Intelligence", impl: "goip.intel.recommendation" },
  { key: "ai_offer_generation", name: "AI Offer Generation", impl: "goip.intel.ai_offer_generation" },
  { key: "ai_incentive_generation", name: "AI Incentive Generation", impl: "goip.intel.ai_incentive_generation" },
  { key: "autonomous_campaign", name: "Autonomous Campaign Generation", impl: "goip.intel.autonomous_campaign" },
  { key: "autonomous_optimization", name: "Autonomous Optimization", impl: "goip.intel.autonomous_optimization" }
];

/* ═══════════════ 15 · GOVERNANCE & COMPLIANCE FABRIC (10) ═══════════════ */
const GOVERNANCE = [
  { key: "policy", name: "Policy Engine", action: "policy", store: "platform_settings.security" },
  { key: "approval", name: "Approval Engine", action: "approve|reject", store: "offers.governance" },
  { key: "certification", name: "Certification Engine", action: "certify", store: "compliance_records" },
  { key: "lifecycle", name: "Lifecycle Engine", action: "publish|suspend|retire", store: "offers.status" },
  { key: "versioning", name: "Versioning Engine", action: "version", store: "offers.version + parent_id" },
  { key: "audit", name: "Audit Engine", action: "audit", store: "audit_log (hash chain)" },
  { key: "compliance", name: "Compliance Engine", action: "attest", store: "compliance_records" },
  { key: "regulatory", name: "Regulatory Engine", action: "restrict", store: "offers.governance.jurisdictions" },
  { key: "risk", name: "Risk Engine", action: "score", store: "engine:risk" },
  { key: "legal", name: "Legal Engine", action: "terms", store: "offers.governance.terms" }
];
const GOVERNANCE_STATES = ["draft", "submitted", "approved", "rejected", "certified", "published", "suspended", "retired"];
const GOVERNANCE_TRANSITIONS = { draft: ["submitted", "retired"], submitted: ["approved", "rejected", "draft"], approved: ["certified", "published", "suspended", "draft"], rejected: ["draft", "retired"], certified: ["published", "suspended"], published: ["suspended", "retired"], suspended: ["published", "retired"], retired: [] };

/* ═══════════════ 16 · UNIVERSAL INCENTIVE GRAPH (21 node kinds · 14 relationships) ═══════════════ */
const GRAPH_NODES = [
  { key: "offer", store: "offers" }, { key: "coupon", store: "coupons" }, { key: "reward", store: "goip_entitlements" },
  { key: "cashback", store: "wallet_entries" }, { key: "gift_card", store: "coupons" }, { key: "voucher", store: "coupons" },
  { key: "benefit", store: "meta_lists:goipBenefits" }, { key: "campaign", store: "offers.campaign" }, { key: "audience", store: "meta_lists:goipAudiences" },
  { key: "merchant", store: "tenants" }, { key: "brand", store: "offers.brand_ref" }, { key: "provider", store: "provider_defs" },
  { key: "partner", store: "suppliers" }, { key: "affiliate", store: "goip_touchpoints" }, { key: "creator", store: "goip_touchpoints" },
  { key: "wallet", store: "wallets" }, { key: "settlement", store: "goip_settlements" }, { key: "payout", store: "goip_settlements" },
  { key: "temporal_context", store: "meta_lists:goipCalendars" }, { key: "spatial_context", store: "meta_lists:goipSpatialNodes" }, { key: "economic_context", store: "meta_lists:goipEconomicUnits" }
];
const GRAPH_EDGES = ["FUNDED_BY", "TARGETED_TO", "ISSUED_BY", "DISTRIBUTED_BY", "DISCOVERED_BY", "CLICKED_BY", "ACTIVATED_BY", "REDEEMED_BY", "ATTRIBUTED_TO", "SETTLED_BY", "PAID_TO", "GOVERNED_BY", "GENERATED_BY", "PART_OF"];

/* ═══════════════ 17 · EXPERIENCE + ACCESS FABRIC ═══════════════ */
const EXPERIENCE = [
  { key: "web", name: "Web", binding: "public/index.html", state: "live" }, { key: "mobile", name: "Mobile", binding: "responsive storefront + REST", state: "live" },
  { key: "pos", name: "POS", binding: "REST /api/goip", state: "adapter" }, { key: "marketplace", name: "Marketplace", binding: "tenant mode=marketplace", state: "live" },
  { key: "commerce", name: "Commerce", binding: "cart/checkout channel", state: "live" }, { key: "erp", name: "ERP", binding: "connectors + webhooks", state: "adapter" },
  { key: "crm", name: "CRM", binding: "connectors + webhooks", state: "adapter" }, { key: "cdp", name: "CDP", binding: "touchpoint feed", state: "adapter" },
  { key: "hrms", name: "HRMS", binding: "employee_benefit domain", state: "adapter" }, { key: "banking", name: "Banking", binding: "funder=bank + bank feed", state: "live" },
  { key: "insurance", name: "Insurance", binding: "funder=corporate + entitlements", state: "adapter" }, { key: "gaming", name: "Gaming", binding: "gamification domain", state: "live" },
  { key: "telecom", name: "Telecom", binding: "channel registry", state: "adapter" }, { key: "government", name: "Government", binding: "funder=government", state: "live" },
  { key: "creator", name: "Creator", binding: "creator domain + feed", state: "live" }, { key: "iot", name: "IoT", binding: "iot_feed channel", state: "adapter" },
  { key: "ai", name: "AI", binding: "ai channel + ai feed", state: "live" }, { key: "widgets", name: "Widgets", binding: "/api/goip/widget", state: "live" },
  { key: "white_label", name: "White Label Portals", binding: "per-tenant branding", state: "live" }, { key: "partner_portal", name: "Partner Portals", binding: "partner feed + scoped API", state: "live" },
  { key: "merchant_portal", name: "Merchant Portals", binding: "/console.html", state: "live" }, { key: "brand_portal", name: "Brand Portals", binding: "brand-scoped API", state: "live" },
  { key: "agent", name: "Agent Interfaces", binding: "capability router", state: "live" }, { key: "future_interface", name: "Future Interfaces", binding: "add a row — capabilities are surface-agnostic", state: "registry" }
];
const ACCESS = [
  { key: "rest", name: "REST", binding: "/api/goip/*", state: "live" }, { key: "graphql", name: "GraphQL", binding: "single capability resolver", state: "adapter" },
  { key: "events", name: "Events", binding: "lib/events.js", state: "live" }, { key: "kafka", name: "Kafka", binding: "queue driver (LX_QUEUE)", state: "adapter" },
  { key: "streams", name: "Streams", binding: "queue driver", state: "adapter" }, { key: "webhooks", name: "Webhooks", binding: "webhooks table (HMAC)", state: "live" },
  { key: "sdk", name: "SDK", binding: "capability contract", state: "adapter" }, { key: "mobile_sdk", name: "Mobile SDK", binding: "capability contract", state: "adapter" },
  { key: "agent_protocol", name: "Agent Protocol", binding: "POST /api/goip/:capability", state: "live" }, { key: "mcp", name: "MCP", binding: "capability manifest", state: "adapter" },
  { key: "embedded", name: "Embedded Components", binding: "/api/goip/widget", state: "live" }, { key: "connectors", name: "Connectors", binding: "provider_defs.spec", state: "live" }
];

/* ═══════════════ 18 · PRODUCTIZATION & COMMERCIALIZATION ═══════════════ */
const DEPLOYMENTS = [
  { key: "embedded_sdk", name: "Embedded SDK" }, { key: "embedded_widget", name: "Embedded Widget" }, { key: "microservice", name: "Microservice" },
  { key: "headless_api", name: "Headless API" }, { key: "saas", name: "SaaS" }, { key: "private_cloud", name: "Private Cloud" },
  { key: "dedicated_cloud", name: "Dedicated Cloud" }, { key: "white_label", name: "White Label" }, { key: "marketplace_service", name: "Marketplace Service" },
  { key: "managed_service", name: "Managed Service" }, { key: "agent_service", name: "Agent Service" }
];
/* every billing model names the meter it bills on; meters are written to usage_records (billing.js) */
const BILLING_MODELS = [
  { key: "per_tenant", name: "Per Tenant", meter: "goip.tenant", unit: "tenant/month", rate: 99 },
  { key: "per_merchant", name: "Per Merchant", meter: "goip.merchant", unit: "merchant/month", rate: 49 },
  { key: "per_provider", name: "Per Provider", meter: "goip.provider", unit: "provider/month", rate: 19 },
  { key: "per_offer", name: "Per Offer", meter: "goip.create", unit: "value exchange", rate: 0.5 },
  { key: "per_redemption", name: "Per Redemption", meter: "goip.redemption", unit: "redemption", rate: 0.02 },
  { key: "per_settlement", name: "Per Settlement", meter: "goip.settlement", unit: "settlement run", rate: 0.25 },
  { key: "per_payout", name: "Per Payout", meter: "goip.payout", unit: "payout", rate: 0.35 },
  { key: "per_api", name: "Per API", meter: "goip.decision", unit: "1k decisions", rate: 0.004 },
  { key: "per_active_user", name: "Per Active User", meter: "goip.active_user", unit: "MAU", rate: 0.01 },
  { key: "per_campaign", name: "Per Campaign", meter: "goip.publish", unit: "campaign", rate: 5 },
  { key: "revenue_share", name: "Revenue Share", meter: "goip.settlement", unit: "% of settled value", rate: 0.5 },
  { key: "hybrid", name: "Hybrid", meter: "*", unit: "platform + usage", rate: 0 }
];
const METERS = ["goip.create", "goip.publish", "goip.issue", "goip.reserve", "goip.track", "goip.attribute", "goip.decision", "goip.redemption", "goip.settlement", "goip.payout", "goip.fund", "goip.govern", "goip.intelligence", "goip.tenant", "goip.merchant", "goip.provider", "goip.active_user"];
const AUDIENCES = [
  { key: "everyone", name: "Everyone", rule: {} },
  { key: "new_customer", name: "New customers", rule: { "audience.orders": { lte: 0 } } },
  { key: "returning", name: "Returning customers", rule: { "audience.orders": { gte: 1 } } },
  { key: "high_value", name: "High value", rule: { "audience.lifetime": { gte: 1000 } } },
  { key: "employee", name: "Employees", rule: { "identity.staff": { eq: true } } },
  { key: "member", name: "Members", rule: { "audience.entitlements": { has: "membership_upgrade" } } },
  { key: "partner", name: "Partner accounts", rule: { "partner.id": { exists: true } } },
  { key: "declared", name: "Declared audience", rule: {} }
];

/* ═══════════════ 19 · REGISTRY SEED (every list above becomes DATA, editable in Data Studio) ═══════════════ */
const REGISTRIES = {
  goipConstitution: CONSTITUTION, goipCapabilities: CAPABILITIES, goipEngines: ENGINES, goipContexts: CONTEXTS,
  goipCalendars: CALENDARS, goipChronologies: CHRONOLOGIES, goipTemporalUnits: TEMPORAL_UNITS, goipTemporalConversions: TEMPORAL_CONVERSIONS,
  goipSpatialSystems: SPATIAL_SYSTEMS, goipCoordinateSystems: COORDINATE_SYSTEMS, goipSpatialNodes: SPATIAL_NODES,
  goipEconomicUnits: ECONOMIC_UNITS, goipAssetClasses: ASSET_CLASSES, goipRealities: REALITIES,
  goipDomains: DOMAINS, goipBenefits: BENEFITS, goipDistribution: DISTRIBUTION,
  goipAttribution: ATTRIBUTION, goipAttributionModels: ATTRIBUTION_MODELS, goipFunding: FUNDING, goipFunders: FUNDERS,
  goipSettlement: SETTLEMENT, goipSettlementStatuses: SETTLEMENT_STATUSES, goipIntelligence: INTELLIGENCE,
  goipGovernance: GOVERNANCE, goipGovernanceStates: GOVERNANCE_STATES, goipGovernanceTransitions: GOVERNANCE_TRANSITIONS,
  goipGraphNodes: GRAPH_NODES, goipGraphEdges: GRAPH_EDGES, goipExperience: EXPERIENCE, goipAccess: ACCESS,
  goipDeployments: DEPLOYMENTS, goipBillingModels: BILLING_MODELS, goipMeters: METERS, goipAudiences: AUDIENCES,
  goipPartyTypes: ["merchant", "brand", "marketplace", "partner", "bank", "government", "corporate", "platform", "affiliate", "creator", "influencer", "referrer", "customer"],
  goipTouchpointKinds: ["impression", "view", "click", "scan", "share", "install", "signup", "conversion", "return"],
  goipEntitlementStatuses: ["active", "consumed", "expired", "revoked"],
  goipObjectives: ["max_benefit", "min_cost", "max_margin", "max_conversion", "balanced"]
};
const REG = k => { const r = registryMod().list(k); return (Array.isArray(r) && r.length) || (r && typeof r === "object" && Object.keys(r).length) ? r : REGISTRIES[k]; };
const regBy = (k, key) => arr(REG(k)).find(x => x && x.key === key) || null;

function seed() {
  const Db = db();
  for (const [name, items] of Object.entries(REGISTRIES))
    Db.run("INSERT OR IGNORE INTO meta_lists(name,label,items) VALUES(?,?,?)", name, name, JSON.stringify(items));
  /* the benefit fabric must be visible to the SAME offer-type registry the rest of the platform reads,
     so a GOIP benefit is selectable everywhere an offer type is — one registry, not two. */
  try {
    const cur = arr(registryMod().list("offerTypes"));
    const have = new Set(cur.map(t => t.key));
    let changed = false;
    for (const b of BENEFITS) if (!have.has(b.type)) { cur.push({ key: b.type, name: b.name, direction: b.direction, unit: b.unit, goip: b.key }); changed = true; }
    if (changed) Db.run("UPDATE meta_lists SET items=? WHERE name='offerTypes'", JSON.stringify(cur));
    const funders = arr(registryMod().list("offerFunders")); let fch = false;
    for (const f of FUNDERS) if (!funders.includes(f)) { funders.push(f); fch = true; }
    if (fch) Db.run("UPDATE meta_lists SET items=? WHERE name='offerFunders'", JSON.stringify(funders));
    const scopes = arr(registryMod().list("offerScopes")); let sch = false;
    for (const s of ["audience", "spatial", "temporal", "economic", "domain", "party"]) if (!scopes.includes(s)) { scopes.push(s); sch = true; }
    if (sch) Db.run("UPDATE meta_lists SET items=? WHERE name='offerScopes'", JSON.stringify(scopes));
  } catch (e) { console.error("goip registry merge:", e.message); }
  registerHandlers();
  registerHooks();
  let demo = { skipped: true };
  try { demo = seedDemo(); } catch (e) { console.error("goip demo seed:", e.message); }
  return { registries: Object.keys(REGISTRIES).length, benefits: BENEFITS.length, domains: DOMAINS.length, demo };
}

/* ═══════════════ 19b · DEMO SEED — a working constitution on first boot ═══════════════
   Seven global value exchanges that together exercise every axis (context, benefit, funding,
   distribution, governance), three funding budgets and a touchpoint path, plus GOIP installed on the
   flagship store so the meters bill. Every exchange is CODE-GATED or off-world, so nothing
   auto-applies to an unsuspecting cart. Runs once; the marker lives in platform_settings. */
const DEMO_EXCHANGES = [
  { name: "GOIP · New-customer welcome", benefit: "percentage_discount", value: 10, code: "GOIPWELCOME", domain: "offer",
    funder: "marketplace", funder_ref: "LUXORA", max_discount: 50, per_owner_limit: 1, summary: "10% for a subject with no prior orders — the condition engine decides, not a flag.",
    conditions: { "audience.orders": { lte: 0 } }, distribution: ["email", "in_app", "widget", "push"], governance: { state: "published" } },
  { name: "GOIP · Bank cashback (multi-party funded)", benefit: "cashback", value: 5, code: "GOIPBANK", domain: "cashback",
    funder: "split", funder_ref: "HDFC", min_amount: 100, summary: "5% back to the wallet, funded 70/30 by a bank and a brand and settled to both.",
    funding: { parties: [{ party: "HDFC", party_type: "bank", share: 0.7 }, { party: "NIKE", party_type: "brand", share: 0.3 }] },
    spatial: { system: "earth_admin", include: ["earth"] }, distribution: ["email", "bank_feed", "in_app"], governance: { state: "published" } },
  { name: "GOIP · Olympus Sector-7 sol offer", benefit: "percentage_discount", value: 15, code: "GOIPSOL", domain: "offer",
    funder: "partner", funder_ref: "olympus-coop", economic_unit: "MARS_CREDIT", summary: "Priced in Mars Credits, scoped to Olympus Territory, timed by the Darian calendar.",
    spatial: { system: "mars_admin", include: ["mars.olympus"] }, temporal: { calendar: "mars_darian" }, distribution: ["in_app", "iot_feed"], governance: { state: "published" } },
  { name: "GOIP · Bihar public subsidy", benefit: "government_benefit", value: 25, code: "GOIPGOV", domain: "government_benefit",
    funder: "government", funder_ref: "BIHAR-DEPT", summary: "A flat state subsidy, restricted by jurisdiction and spatial path.",
    spatial: { system: "earth_admin", include: ["earth.in.bihar"] }, governance: { state: "published", jurisdictions: ["earth.in"] },
    distribution: ["sms", "whatsapp", "in_app"], rules: { scheme: "BIHAR-RETAIL-2026" } },
  { name: "GOIP · Points per spend", benefit: "reward_points", value: 0, code: "GOIPPOINTS", domain: "reward",
    funder: "self", summary: "2 points per unit spent — a non-money benefit with its own ledger, never the cash wallet.",
    rules: { rate: 2 }, distribution: ["in_app", "creator_feed"], governance: { state: "published" } },
  { name: "GOIP · Gold membership grant", benefit: "membership_upgrade", value: 1, code: "GOIPGOLD", domain: "membership",
    funder: "self", summary: "Grants a 365-day entitlement rather than money.", rules: { tier: "gold", days: 365 },
    distribution: ["email", "in_app"], governance: { state: "published" } },
  { name: "GOIP · Deferred cashback (30 days)", benefit: "deferred_cashback", value: 10, code: "GOIPDEFER", domain: "cashback",
    funder: "brand", funder_ref: "NIKE", summary: "Value promised now, released to the wallet on its due date by the settlement run.",
    rules: { defer_days: 30 }, distribution: ["email", "in_app"], governance: { state: "published" } }
];
function seedDemo() {
  const Db = db();
  try { if ((Db.get("SELECT value FROM platform_settings WHERE key='goip_demo'") || {}).value) return { skipped: true }; } catch (e) { return { skipped: true }; }
  const made = [];
  for (const x of DEMO_EXCHANGES) {
    try { if (Db.get("SELECT id FROM offers WHERE code=? AND tenant_id=0", x.code)) continue; } catch (e) { }
    const r = createExchange(0, Object.assign({ scope_level: "global", channel: "commerce", scope_type: "store", status: "active" }, x), { platform: true, generated_by: "seed" });
    if (r.ok) made.push(r.id);
  }
  /* funding budgets so burn, settlement and payout have something to move */
  fund(0, { funder: "split", funder_ref: "HDFC", unit: "USD", amount: 5000, domain: "cashback", policy: { alert_at_pct: 80 } });
  fund(0, { funder: "marketplace", funder_ref: "LUXORA", unit: "USD", amount: 2500, domain: "incentive" });
  fund(0, { funder: "partner", funder_ref: "olympus-coop", unit: "MARS_CREDIT", amount: 100000, domain: "offer" });
  /* the flagship store buys GOIP: capabilities on, meters billing (the others stay unentitled on purpose) */
  const flagship = Db.get("SELECT id FROM tenants WHERE slug='luxora'");
  if (flagship) {
    try {
      Db.run(`INSERT INTO tenant_modules(tenant_id,module_id,status,config) VALUES(?, 'goip','installed',?)
              ON CONFLICT(tenant_id,module_id) DO UPDATE SET status='installed'`, flagship.id,
        JSON.stringify({ deployment: "saas", billing_model: "hybrid", objective: "balanced", calendar: "gregorian" }));
    } catch (e) { }
    /* a touchpoint path so attribution has a real journey to replay */
    const owner = "t" + flagship.id + ":u:2";
    try {
      track(flagship.id, { kind: "impression", owner, party: "creator-42", party_type: "creator", channel: "commerce", distribution: "creator_feed", value: 0 });
      track(flagship.id, { kind: "click", owner, party: "creator-42", party_type: "creator", channel: "commerce", distribution: "creator_feed", value: 0 });
      track(flagship.id, { kind: "view", owner, party: "aff-7", party_type: "affiliate", channel: "commerce", distribution: "affiliate_feed", value: 0 });
    } catch (e) { }
  }
  try { Db.run("INSERT INTO platform_settings(key,value) VALUES('goip_demo','1') ON CONFLICT(key) DO UPDATE SET value='1'"); } catch (e) { }
  return { ok: true, exchanges: made.length };
}

/* ═══════════════ 20 · BENEFIT HANDLERS (registered INTO offers.HANDLERS — one math engine) ═══════════════ */
const lineTotal = i => Number(i.price) * Number(i.qty);
const subOf = its => its.reduce((n, i) => n + lineTotal(i), 0);
const qtyOf = its => its.reduce((n, i) => n + Number(i.qty), 0);
const rowOf = o => (o && o._row) || {};
const unitOf = o => S(rowOf(o).economic_unit || o.currency || "USD").toUpperCase();
const moneyUnit = u => { const e = regBy("goipEconomicUnits", S(u).toUpperCase()); return !e || e.class === "fiat"; };
function grantOf(o, benefit, unit, qty) {
  const r = o.rules || {};
  return { benefit, unit: unit || unitOf(o), qty: Number(qty != null ? qty : (r.qty != null ? r.qty : o.value)) || 0, tier: r.tier || "", days: Number(r.days || 0) || 0, scope: o.scope || {}, ref: r.ref || o.code || "" };
}
const GOIP_HANDLERS = {
  dynamic_discount: (o, its, amt) => {
    const curve = arr(o.rules.curve).slice().sort((a, b) => Number(a.min || 0) - Number(b.min || 0));
    let pct = Number(o.value) || 0;
    for (const t of curve) if (amt >= Number(t.min || 0)) pct = Number(t.pct != null ? t.pct : t.value) || pct;
    if (o.rules.max_pct) pct = Math.min(pct, Number(o.rules.max_pct));
    return { discount: subOf(its) * pct / 100, meta: { pct } };
  },
  deferred_cashback: (o, its) => ({ credits: subOf(its) * (Number(o.value) || 0) / 100, unit: unitOf(o), defer: o.rules.defer_days != null ? Number(o.rules.defer_days) : 30 }),
  reward_points: (o, its) => ({ credits: o.rules.rate ? Math.floor(subOf(its) * Number(o.rules.rate)) : (Number(o.value) || 0), unit: S(o.rules.unit || rowOf(o).economic_unit || "POINT").toUpperCase() }),
  coins: (o, its) => ({ credits: o.rules.rate ? Math.floor(subOf(its) * Number(o.rules.rate)) : (Number(o.value) || 0), unit: S(o.rules.unit || "COIN").toUpperCase() }),
  tokens: (o, its) => ({ credits: o.rules.rate ? Math.floor(subOf(its) * Number(o.rules.rate)) : (Number(o.value) || 0), unit: S(o.rules.unit || rowOf(o).economic_unit || "TOKEN").toUpperCase() }),
  wallet_value: (o, its, amt) => (amt >= (Number(o.rules.min || o.min_amount) || 0) ? { credits: Number(o.value) || 0, unit: unitOf(o) } : {}),
  free_product: (o, its) => {
    const n = Number(o.rules.qty || 1); if (!its.length) return {};
    const sorted = its.slice().sort((a, b) => a.price - b.price);
    let left = n, d = 0;
    for (const i of sorted) { const take = Math.min(left, Number(i.qty) || 0); d += take * Number(i.price); left -= take; if (left <= 0) break; }
    return { discount: d };
  },
  free_service: (o, its) => GOIP_HANDLERS.free_product(o, its.filter(i => !o.rules.service_dept || i.dept === o.rules.service_dept)),
  government_benefit: (o, its, amt) => ({ discount: Math.min(Number(o.value) || 0, subOf(its)), meta: { subsidy: true, scheme: o.rules.scheme || o.funder_ref || "" } }),
  voucher_issue: (o, its, amt) => (amt >= (Number(o.min_amount) || 0) ? { grant: Object.assign(grantOf(o, "voucher", unitOf(o)), { kind: "coupon", coupon_kind: o.rules.coupon_kind || "bank_voucher" }) } : {}),
  membership_upgrade: o => ({ grant: grantOf(o, "membership_upgrade", "tier", 1) }),
  tier_upgrade: o => ({ grant: grantOf(o, "tier_upgrade", "tier", 1) }),
  partner_benefit: o => ({ grant: grantOf(o, "partner_benefit") }),
  corporate_benefit: o => ({ grant: grantOf(o, "corporate_benefit") }),
  digital_asset: o => ({ grant: grantOf(o, "digital_asset", S(o.rules.unit || "TOKEN").toUpperCase()) }),
  economic_asset: o => ({ grant: grantOf(o, "economic_asset", unitOf(o)) }),
  /* the extension point: a future benefit is DECLARED in goipBenefits with {derive:{from,factor}} and
     resolves through the handler it derives from — new value constructs need data, never code. */
  future_benefit: (o, its, amt) => {
    const decl = regBy("goipBenefits", S(o.rules.benefit || "future_benefit"));
    const from = decl && decl.derive && decl.derive.from;
    const H = offersMod().HANDLERS[from];
    if (!H) return { grant: grantOf(o, "future_benefit") };
    const res = H(Object.assign({}, o, { value: Number(o.value) * Number((decl.derive && decl.derive.factor) || 1) }), its, amt) || {};
    return res;
  }
};
function registerHandlers() { const H = offersMod().HANDLERS; for (const [k, fn] of Object.entries(GOIP_HANDLERS)) if (!H[k]) H[k] = fn; return Object.keys(GOIP_HANDLERS).length; }

/* post-redemption hook: grants, deferred credits, budget burn, settlement accrual, graph edges.
   Registered on offers.redeem so the plain storefront checkout path gets all of it too. */
let _hooked = false;
function registerHooks() {
  if (_hooked) return false; const O = offersMod();
  if (typeof O.onRedeem !== "function") return false;
  O.onRedeem((ctx, result, ref) => { try { postRedeem(ctx, result, ref); } catch (e) { console.error("goip postRedeem:", e.message); } });
  _hooked = true; return true;
}

/* ═══════════════ 21 · CONTEXT RESOLUTION ENGINE (fills all 25 dimensions) ═══════════════ */
function tenantRow(tid) { return db().get("SELECT * FROM tenants WHERE id=?", tid) || { id: tid, slug: "", name: "", mode: "marketplace", country: "US" }; }
function spatialPathFor(country) {
  const nodes = arr(REG("goipSpatialNodes"));
  const n = nodes.find(x => S(x.key).toLowerCase() === "earth." + S(country).toLowerCase());
  return n ? n.key : "earth";
}
function calendarFor(tid) {
  try { const st = require("./settings.js").load(tid); return (st.goip && st.goip.calendar) || "gregorian"; } catch (e) { return "gregorian"; }
}
/* the temporal authority of a place: declared on the spatial system, else derived from its body.
   A cart on Mars is on the Darian calendar without anyone having to say so. */
function calendarForSystem(sysKey) {
  const sys = arr(REG("goipSpatialSystems")).find(x => x.key === S(sysKey));
  if (!sys) return "";
  if (sys.calendar) return sys.calendar;
  return { mars: "mars_darian", moon: "lunar", "galaxy-7": "federation" }[S(sys.body)] || "";
}
function resolveContext(input) {
  const c = input || {}; const Db = db(); const tid = Number(c.tenantId || 0);
  const t = tenantRow(tid);
  const owner = c.owner || null;
  const items = arr(c.items).map(i => ({ id: i.id, dept: i.dept, brand: i.brand, node_id: i.node_id, price: Number(i.price != null ? i.price : i.p) || 0, qty: Number(i.qty) || 1, type: i.type || "" }));
  const amount = Number(c.amount != null ? c.amount : subOf(items)) || 0;
  const now = new Date();
  const spatialKey = S(c.spatial && c.spatial.node || c.spatialNode || spatialPathFor(t.country || "US"));
  const spatialNode = arr(REG("goipSpatialNodes")).find(n => n.key === spatialKey) || { key: spatialKey, system: "earth_admin", level: "declared", name: spatialKey };
  const cal = regBy("goipCalendars", S(c.calendar || calendarForSystem(spatialNode.system) || calendarFor(tid))) || regBy("goipCalendars", "gregorian");
  const unit = S(c.currency || c.unit || t.currency || "USD").toUpperCase();
  const eu = regBy("goipEconomicUnits", unit) || { key: unit, class: "fiat", decimals: 2, base_rate: 1, settleable: true };
  let orders = 0, lifetime = 0, lastOrder = null, staff = false;
  if (owner) {
    try { const o = Db.get("SELECT COUNT(*) n, COALESCE(SUM(total),0) v, MAX(created_at) last FROM orders WHERE tenant_id=? AND owner=?", tid, owner); orders = o.n || 0; lifetime = r2(o.v || 0); lastOrder = o.last || null; } catch (e) { }
    const uid = /:u:(\d+)$/.exec(S(owner)); if (uid) { try { const u = Db.get("SELECT role, staff_role FROM users WHERE id=?", Number(uid[1])); staff = !!(u && u.role === "admin"); } catch (e) { } }
  }
  const ents = owner ? entitlementsOf(tid, owner).map(e => e.benefit) : [];
  const segs = personalize(tid, owner, { orders, lifetime, entitlements: ents, amount });
  let stock = null;
  if (items.length) { try { stock = items.map(i => ({ id: i.id, stock: (Db.get("SELECT stock FROM products WHERE tenant_id=? AND id=?", tid, i.id) || {}).stock })); } catch (e) { } }
  let aiTier = "free"; try { aiTier = require("./ai.js").tierOf(tid).tier || "free"; } catch (e) { }
  const pol = (() => { try { return securityMod().policy().provisioning || {}; } catch (e) { return {}; } })();
  return {
    reality: S(c.reality || "physical"),
    temporal: { calendar: cal.key, chronology: cal.chronology, instant: now.toISOString(), date: today(), period: period(now), weekday: now.getUTCDay(), hour: now.getUTCHours(), day_seconds: cal.day_seconds, year_days: cal.year_days, tz: c.tz || "UTC" },
    spatial: { system: spatialNode.system, node: spatialNode.key, path: S(spatialNode.key).split("."), level: spatialNode.level, name: spatialNode.name, coordinates: c.coordinates || null },
    economic: { unit, class: eu.class, decimals: eu.decimals, base_rate: eu.base_rate, settleable: !!eu.settleable, amount, base_amount: eu.base_rate ? r2(amount * eu.base_rate) : null },
    governance: { policy: pol, coupons_allowed: pol.couponsAllowed !== false, global_allowed: pol.globalOffersAllowed !== false, approval_required: !!pol.goipApprovalRequired },
    audience: { segments: segs, orders, lifetime, entitlements: ents, last_order: lastOrder },
    identity: { owner, authenticated: !!(owner && /:u:/.test(S(owner))), staff, sid: c.sid || null },
    behavioral: { items: items.length, qty: qtyOf(items), basket: amount, repeat: orders > 0 },
    product: { ids: items.map(i => i.id), brands: [...new Set(items.map(i => i.brand).filter(Boolean))], types: [...new Set(items.map(i => i.type).filter(Boolean))] },
    catalog: { depts: [...new Set(items.map(i => i.dept).filter(Boolean))], nodes: [...new Set(items.map(i => i.node_id).filter(Boolean))] },
    cart: { items, amount, qty: qtyOf(items), currency: unit },
    session: { sid: c.sid || null, channel: S(c.channel || "commerce") },
    device: { kind: S(c.device || "unknown"), ua: S(c.ua || "") },
    market: { country: t.country || "US", region: t.region || "global", currency: unit, mode: t.mode },
    inventory: { lines: stock },
    risk: { score: owner ? fraudScore(tid, owner).score : 0 },
    organization: { tenant_id: tid, slug: t.slug, name: t.name, mode: t.mode },
    merchant: { tenant_id: tid, slug: t.slug, seller: c.seller || null },
    provider: { payment: c.provider || null, kinds: ["payment", "shipping", "notification", "ai", "marketing"] },
    partner: { id: c.partner || null, type: c.partner_type || null },
    creator: { id: c.creator || null },
    channel: { key: S(c.channel || "commerce"), distribution: S(c.distribution || "in_app") },
    event: { key: S(c.event || ""), at: now.toISOString() },
    campaign: { key: S(c.campaign || "") },
    ai: { tier: aiTier }
  };
}

/* ═══════════════ 22 · CONDITION ENGINE (declared conditions over the resolved context) ═══════════════ */
function dig(obj, path) { return S(path).split(".").reduce((o, k) => (o == null ? o : o[k]), obj); }
const OPS = {
  eq: (a, b) => a === b || S(a) === S(b), ne: (a, b) => !(a === b || S(a) === S(b)),
  gt: (a, b) => Number(a) > Number(b), gte: (a, b) => Number(a) >= Number(b),
  lt: (a, b) => Number(a) < Number(b), lte: (a, b) => Number(a) <= Number(b),
  in: (a, b) => arr(b).some(x => S(x) === S(a)), nin: (a, b) => !arr(b).some(x => S(x) === S(a)),
  has: (a, b) => arr(a).some(x => S(x) === S(b)), nhas: (a, b) => !arr(a).some(x => S(x) === S(b)),
  between: (a, b) => Number(a) >= Number(arr(b)[0]) && Number(a) <= Number(arr(b)[1]),
  exists: (a, b) => (b === false ? (a == null || a === "") : (a != null && a !== "")),
  prefix: (a, b) => S(a).indexOf(S(b)) === 0, matches: (a, b) => arr(b).some(x => S(a).indexOf(S(x)) === 0)
};
/* conditions: { "audience.orders": {gte:1}, "spatial.node": {prefix:"earth.in"}, "temporal.weekday": {in:[6,0]} } */
function qualify(conditions, ctx) {
  const reasons = []; const cond = conditions && typeof conditions === "object" ? conditions : {};
  for (const [path, test] of Object.entries(cond)) {
    const actual = dig(ctx, path);
    const checks = (test && typeof test === "object" && !Array.isArray(test)) ? test : { eq: test };
    for (const [op, expect] of Object.entries(checks)) {
      const fn = OPS[op]; if (!fn) { reasons.push(path + ": unknown operator " + op); continue; }
      if (!fn(actual, expect)) reasons.push(path + " " + op + " " + JSON.stringify(expect) + " (actual " + JSON.stringify(actual === undefined ? null : actual) + ")");
    }
  }
  return { ok: reasons.length === 0, reasons };
}

/* ═══════════════ 23 · PERSONALIZATION · FRAUD · RISK ═══════════════ */
function personalize(tenantId, owner, facts) {
  const f = facts || {}; const segs = [];
  for (const a of arr(REG("goipAudiences"))) {
    if (!a || !a.key) continue;
    if (a.key === "everyone") { segs.push(a.key); continue; }
    const probe = { audience: { orders: f.orders || 0, lifetime: f.lifetime || 0, entitlements: f.entitlements || [] }, identity: { staff: !!f.staff }, partner: { id: f.partner || null } };
    if (a.rule && Object.keys(a.rule).length && qualify(a.rule, probe).ok) segs.push(a.key);
  }
  if ((f.amount || 0) >= 500) segs.push("high_basket");
  return segs;
}
function fraudScore(tenantId, owner) {
  const Db = db(); let score = 0; const signals = [];
  if (!owner) return { score: 0, signals };
  try {
    const d = Db.get("SELECT COUNT(*) n, COALESCE(SUM(amount),0) v FROM coupon_redemptions WHERE tenant_id=? AND owner=? AND created_at > datetime('now','-1 day')", tenantId, owner);
    if (d.n >= 5) { score += 30; signals.push("velocity:" + d.n + " redemptions/24h"); }
    if (d.v >= 500) { score += 25; signals.push("value:" + r2(d.v) + " discounted/24h"); }
    const v = Db.get("SELECT COUNT(*) n FROM coupon_redemptions WHERE tenant_id=? AND owner=? AND status='voided'", tenantId, owner);
    if (v.n >= 2) { score += 20; signals.push("clawbacks:" + v.n); }
    const codes = Db.get("SELECT COUNT(DISTINCT code) n FROM coupon_redemptions WHERE tenant_id=? AND owner=? AND created_at > datetime('now','-7 day')", tenantId, owner);
    if (codes.n >= 6) { score += 25; signals.push("code-spraying:" + codes.n + " codes/7d"); }
  } catch (e) { }
  return { score: Math.min(100, score), signals };
}
function riskScore(tenantId, row) {
  const Db = db(); let score = 0; const signals = [];
  const o = row || {}; const rules = J(o.rules, {});
  const openEnded = !o.usage_limit && !o.ends;
  if (openEnded) { score += 25; signals.push("no usage limit and no end date"); }
  if (!o.max_discount && (o.type === "percent" || o.type === "flash_percent" || o.type === "dynamic_discount")) { score += 20; signals.push("percentage benefit with no cap"); }
  if (Number(o.value) >= 50 && /percent/.test(S(o.type))) { score += 25; signals.push("≥50% benefit"); }
  if (!o.per_owner_limit) { score += 10; signals.push("unlimited per owner"); }
  if (S(o.funder) === "self" && Number(o.value) >= 30) { score += 10; signals.push("self-funded at high value"); }
  let exposure = 0;
  try { const u = Db.get("SELECT COALESCE(SUM(amount),0) a, COUNT(*) n FROM coupon_redemptions WHERE offer_id=? AND status='redeemed'", o.id) || {}; exposure = r2(u.a || 0); if ((u.n || 0) > 0 && o.usage_limit) { const burn = u.n / o.usage_limit; if (burn > 0.8) { score += 10; signals.push("usage " + Math.round(burn * 100) + "% of limit"); } } } catch (e) { }
  if (rules.unbounded) { score += 10; signals.push("declared unbounded"); }
  return { score: Math.min(100, score), signals, exposure };
}

/* ═══════════════ 24 · ELIGIBILITY ENGINE (constitutional gates: reality/time/place/economy/governance/audience) ═══════════════ */
function temporalOk(spec, tctx) {
  if (!spec || !Object.keys(spec).length) return { ok: true };
  if (spec.calendar && spec.calendar !== "any" && spec.calendar !== tctx.calendar) return { ok: false, why: "calendar " + spec.calendar + " ≠ " + tctx.calendar };
  if (spec.weekdays && spec.weekdays.length && !spec.weekdays.map(Number).includes(tctx.weekday)) return { ok: false, why: "weekday " + tctx.weekday + " not in window" };
  if (spec.hours && spec.hours.length === 2 && !(tctx.hour >= Number(spec.hours[0]) && tctx.hour <= Number(spec.hours[1]))) return { ok: false, why: "hour " + tctx.hour + " outside " + spec.hours.join("-") };
  if (spec.periods && spec.periods.length && !spec.periods.includes(tctx.period)) return { ok: false, why: "period " + tctx.period + " not listed" };
  if (spec.from && tctx.date < spec.from) return { ok: false, why: "before " + spec.from };
  if (spec.to && tctx.date > spec.to) return { ok: false, why: "after " + spec.to };
  return { ok: true };
}
function spatialOk(spec, sctx) {
  if (!spec || !Object.keys(spec).length) return { ok: true };
  if (spec.system && spec.system !== "any" && spec.system !== sctx.system) return { ok: false, why: "spatial system " + spec.system + " ≠ " + sctx.system };
  const node = S(sctx.node);
  const inc = arr(spec.include), exc = arr(spec.exclude);
  if (exc.length && exc.some(p => node === S(p) || node.indexOf(S(p) + ".") === 0)) return { ok: false, why: node + " excluded" };
  if (inc.length && !inc.some(p => node === S(p) || node.indexOf(S(p) + ".") === 0)) return { ok: false, why: node + " outside " + inc.join("/") };
  return { ok: true };
}
function economicOk(row, ectx) {
  const unit = S(row.economic_unit || "").toUpperCase();
  if (!unit || unit === "ANY") return { ok: true };
  if (unit === S(ectx.unit).toUpperCase()) return { ok: true };
  const decl = regBy("goipEconomicUnits", unit);
  if (decl && decl.base_rate && ectx.base_rate) return { ok: true, converted: true };
  return { ok: false, why: "economic unit " + unit + " ≠ " + ectx.unit + " and no conversion declared" };
}
function eligibility(cand, rctx) {
  const row = (cand && cand._row) || cand || {}; const reasons = [];
  const reality = S(row.reality || "any");
  if (reality !== "any" && reality !== rctx.reality) reasons.push("reality " + reality + " ≠ " + rctx.reality);
  const t = temporalOk(J(row.temporal_spec, {}), rctx.temporal); if (!t.ok) reasons.push(t.why);
  const s = spatialOk(J(row.spatial_spec, {}), rctx.spatial); if (!s.ok) reasons.push(s.why);
  const e = economicOk(row, rctx.economic); if (!e.ok) reasons.push(e.why);
  const gov = J(row.governance, {});
  const state = S(gov.state || (row.id ? "published" : "published"));
  if (GOVERNANCE_STATES.includes(state) && !["approved", "certified", "published"].includes(state)) reasons.push("governance state " + state);
  if (rctx.governance.approval_required && !["approved", "certified", "published"].includes(state)) reasons.push("approval required by platform policy");
  const juris = arr(gov.jurisdictions);
  if (juris.length && !juris.some(j => S(rctx.spatial.node).indexOf(S(j)) === 0 || S(j) === S(rctx.market.country))) reasons.push("jurisdiction not permitted");
  const aud = arr(J(row.scope_value, {}).audience || (cand.rules || {}).audience);
  if (aud.length && !aud.some(a => arr(rctx.audience.segments).includes(S(a)))) reasons.push("audience " + aud.join("/") + " not matched");
  const cond = J(row.conditions, (cand.rules || {}).conditions || {});
  const q = qualify(cond, rctx); if (!q.ok) reasons.push(...q.reasons);
  /* opt-in exchanges (card-linked / app-activated) demand an activation entitlement for this subject */
  if ((cand.rules || {}).requires_activation || J(row.rules, {}).requires_activation) {
    const own = rctx.identity.owner;
    const act = own ? db().get("SELECT id FROM goip_entitlements WHERE tenant_id=? AND owner=? AND benefit='activation' AND source_offer=? AND status='active'", Number(row.tenant_id) || rctx.organization.tenant_id, own, row.id) : null;
    if (!act) reasons.push("requires activation by the subject");
  }
  if (rctx.risk.score >= 80 && cand.code) reasons.push("risk score " + rctx.risk.score + " blocks code redemption");
  return { ok: reasons.length === 0, reasons };
}

/* ═══════════════ 25 · RANKING + CONFLICT RESOLUTION ═══════════════ */
function benefitWeight(c, amount) {
  const t = S(c.type);
  if (/percent/.test(t)) return (Number(c.value) || 0) / 100 * (amount || 0);
  if (t === "free_ship" || t === "threshold_free_ship") return 5;
  return Number(c.value) || 0;
}
function rank(objective, amount) {
  const obj = S(objective || "max_benefit");
  return (a, b) => {
    const pa = Number((a._row || {}).priority || 0), pb = Number((b._row || {}).priority || 0);
    if (pa !== pb) return pb - pa;
    const wa = benefitWeight(a, amount), wb = benefitWeight(b, amount);
    if (obj === "min_cost") return wa - wb;
    if (obj === "max_margin") return (a.funder === "self" ? 1 : 0) - (b.funder === "self" ? 1 : 0) || wa - wb;
    if (obj === "max_conversion") return (b.code ? 0 : 1) - (a.code ? 0 : 1) || wb - wa;
    if (obj === "balanced") return (wb - wa) * 0.5 + (pb - pa);
    return wb - wa;
  };
}
/* same domain + same stack group ⇒ only the strongest survives (offers.js owns generic stacking) */
function resolveConflicts(cands, amount) {
  const seen = new Map(); const kept = []; const dropped = [];
  for (const c of cands.slice().sort(rank("max_benefit", amount))) {
    const row = c._row || {}; const key = S(row.domain || "incentive") + "|" + S(c.stack_group || "");
    if (c.stack_group && seen.has(key)) { dropped.push({ id: c.id, name: c.name, reason: "domain/stack conflict with #" + seen.get(key) }); continue; }
    if (c.stack_group) seen.set(key, c.id);
    kept.push(c);
  }
  return { kept, dropped };
}

/* ═══════════════ 26 · THE DECISION PIPELINE (context → conditions → eligibility → benefit → execution) ═══════════════ */
function decide(input) {
  const ctx = input || {};
  const rctx = ctx.__resolved || resolveContext(ctx);
  const rejected = []; const allowed = new Map();
  const O = offersMod();
  const pool = O.eligible(Number(ctx.tenantId || 0), S(ctx.channel || "commerce"), ctx.coupon, ctx.allowGlobal !== false);
  const okPool = [];
  for (const c of pool) {
    const el = eligibility(c, rctx);
    if (!el.ok) { rejected.push({ id: c.id, src: c._src, name: c.name, reasons: el.reasons }); continue; }
    okPool.push(c);
  }
  const { kept, dropped } = resolveConflicts(okPool, rctx.economic.amount);
  for (const d of dropped) rejected.push({ id: d.id, name: d.name, reasons: [d.reason] });
  for (const c of kept) allowed.set(c._src + ":" + c.id, true);
  const res = O.evaluate(Object.assign({}, ctx, {
    pool: kept.slice().sort(rank(ctx.objective || "max_benefit", rctx.economic.amount)),
    rank: rank(ctx.objective || "max_benefit", rctx.economic.amount)
  }));
  return Object.assign({ context: rctx, considered: pool.length, eligible: kept.length, rejected }, res);
}

/* ═══════════════ 27 · ENTITLEMENTS (non-monetary benefits get a real, queryable home) ═══════════════ */
function entitlementsOf(tenantId, owner) {
  try { return db().all("SELECT * FROM goip_entitlements WHERE tenant_id=? AND owner=? AND status='active' AND (ends IS NULL OR ends>=?) ORDER BY id DESC", tenantId, owner, today()); } catch (e) { return []; }
}
function grantEntitlement(tenantId, owner, grant, src) {
  const g = grant || {}; const Db = db();
  /* a granted voucher/gift card IS an issued coupon — it goes through the one issuance writer */
  if (S(g.kind) === "coupon") {
    const r = issue(tenantId, {
      count: 1, kind: g.coupon_kind || "bank_voucher", offer_id: (src && src.offer_id) || null,
      funder: (src && src.funder) || "self", funder_ref: (src && src.funder_ref) || "",
      value: Number(g.qty) || 0, currency: g.unit || "USD", max_uses: 1, per_owner_limit: 1,
      issued_to: owner || "", batch: "goip", note: "granted by GOIP",
      ends: g.days ? new Date(Date.now() + Number(g.days) * 86400000).toISOString().slice(0, 10) : null
    });
    return r && r.code ? { kind: "coupon", code: r.code } : null;
  }
  const ends = (g.due || g.days) ? new Date(Date.now() + (Number(g.days) || 0) * 86400000).toISOString().slice(0, 10) : null;
  const id = Number(Db.run(`INSERT INTO goip_entitlements(tenant_id,owner,benefit,unit,qty,tier,scope,starts,ends,status,source_offer,source_redemption,meta)
    VALUES(?,?,?,?,?,?,?,?,?,'active',?,?,?)`, tenantId, S(owner), S(g.benefit || "future_benefit"), S(g.unit || ""), Number(g.qty) || 0, S(g.tier || ""),
    JSON.stringify(g.scope || {}), today(), ends, (src && src.offer_id) || null, (src && src.redemption_id) || null, JSON.stringify({ ref: g.ref || "" })).lastInsertRowid);
  return { kind: "entitlement", id, benefit: g.benefit };
}
function consumeEntitlement(tenantId, id, note) {
  const r = db().run("UPDATE goip_entitlements SET status='consumed', meta=? WHERE id=? AND tenant_id=? AND status='active'", JSON.stringify({ consumed_at: nowIso(), note: S(note) }), Number(id), tenantId);
  return { ok: !!r.changes };
}

/* ═══════════════ 28 · METERING (every capability is billable; billing.js owns usage_records) ═══════════════ */
function hasGoip(tenantId) { try { return modulesMod().hasCap(tenantId, "goip"); } catch (e) { return false; } }
function billingModel(meterKey) { return arr(REG("goipBillingModels")).find(m => m.meter === meterKey) || null; }
function meter(tenantId, meterKey, qty, opts) {
  if (!tenantId || !meterKey) return null;
  const model = billingModel(meterKey);
  const rate = hasGoip(tenantId) && model ? Number(model.rate) || 0 : 0;
  try { return billingMod().meter(tenantId, meterKey, "GOIP · " + (model ? model.name : meterKey), Number(qty) || 1, rate, { period: period(), currency: (opts && opts.currency) || "USD" }); } catch (e) { return null; }
}

/* ═══════════════ 29 · GRAPH PROJECTION (nodes/edges live in the existing `links` table) ═══════════════ */
function edge(tenantId, type, fromEntity, fromUid, toEntity, toUid, meta) {
  if (!GRAPH_EDGES.includes(type) || !fromUid || !toUid) return null;
  try { return db().addLink(tenantId, type, fromEntity, fromUid, toEntity, toUid, meta || {}); } catch (e) { return null; }
}
function uidOf(table, id) { try { return (db().get(`SELECT uid FROM ${table} WHERE id=?`, Number(id)) || {}).uid || null; } catch (e) { return null; } }
function graph(tenantId, uid, depth) {
  const Db = db(); const seen = new Set([uid]); const nodes = [{ uid, root: true }]; const edges = [];
  let frontier = [uid]; const max = Math.min(3, Number(depth) || 1);
  for (let d = 0; d < max; d++) {
    const next = [];
    for (const u of frontier) {
      const rows = Db.all("SELECT * FROM links WHERE (tenant_id=? OR tenant_id=0) AND (from_uid=? OR to_uid=?) ORDER BY id DESC LIMIT 200", tenantId, u, u);
      for (const l of rows) {
        edges.push({ type: l.type, from: l.from_uid, from_entity: l.from_entity, to: l.to_uid, to_entity: l.to_entity, meta: J(l.meta, {}) });
        for (const [uu, ee] of [[l.from_uid, l.from_entity], [l.to_uid, l.to_entity]]) if (uu && !seen.has(uu)) { seen.add(uu); nodes.push({ uid: uu, entity: ee }); next.push(uu); }
      }
    }
    frontier = next; if (!frontier.length) break;
  }
  return { root: uid, depth: max, nodes, edges: edges.filter((e, i, a) => a.findIndex(x => x.type === e.type && x.from === e.from && x.to === e.to) === i) };
}

/* ═══════════════ 30 · ATTRIBUTION FABRIC ═══════════════ */
function track(tenantId, t) {
  const Db = db(); const d = t || {};
  const kinds = arr(REG("goipTouchpointKinds"));
  const kind = kinds.includes(S(d.kind)) ? S(d.kind) : "view";
  const id = Number(Db.run(`INSERT INTO goip_touchpoints(tenant_id,subject_uid,offer_id,code,kind,party,party_type,channel,distribution,device,owner,session,order_id,value,unit,context)
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`, tenantId, S(d.subject_uid || ""), d.offer_id ? Number(d.offer_id) : null, S(d.code || "").toUpperCase(), kind,
    S(d.party || ""), S(d.party_type || "customer"), S(d.channel || "commerce"), S(d.distribution || "in_app"), S(d.device || ""), S(d.owner || ""), S(d.session || ""),
    d.order_id ? Number(d.order_id) : null, Number(d.value) || 0, S(d.unit || "USD").toUpperCase(), JSON.stringify(d.context || {})).lastInsertRowid);
  if (d.subject_uid && d.party) {
    const EDGE = { click: "CLICKED_BY", view: "DISCOVERED_BY", impression: "DISTRIBUTED_BY", conversion: "REDEEMED_BY", share: "DISTRIBUTED_BY", scan: "DISCOVERED_BY", signup: "ATTRIBUTED_TO", install: "ATTRIBUTED_TO", return: "ATTRIBUTED_TO" }[kind] || "DISCOVERED_BY";
    edge(tenantId, EDGE, "offer", S(d.subject_uid), S(d.party_type || "customer"), S(d.party), { kind, at: nowIso() });
  }
  meter(tenantId, "goip.track", 1);
  return { ok: true, id, kind };
}
function touchpoints(tenantId, filter) {
  const f = filter || {}; const w = ["tenant_id=?"]; const a = [tenantId];
  if (f.owner) { w.push("owner=?"); a.push(S(f.owner)); }
  if (f.order_id) { w.push("order_id=?"); a.push(Number(f.order_id)); }
  if (f.party) { w.push("party=?"); a.push(S(f.party)); }
  if (f.since) { w.push("created_at>=?"); a.push(S(f.since)); }
  return db().all(`SELECT * FROM goip_touchpoints WHERE ${w.join(" AND ")} ORDER BY id ASC LIMIT 500`, ...a).map(r => ({ ...r, context: J(r.context, {}) }));
}
/* run any declared attribution model over a subject's touchpoint path */
function attribute(tenantId, input) {
  const i = input || {}; const model = S(i.model || "last_touch");
  const path = touchpoints(tenantId, { owner: i.owner, order_id: i.order_id, since: i.since });
  const revenue = Number(i.value != null ? i.value : (path.find(p => p.kind === "conversion") || {}).value) || 0;
  const parties = path.filter(p => p.party && p.party_type !== "customer");
  if (!parties.length) return { model, revenue: r2(revenue), path: path.length, credits: [] };
  let weights = [];
  if (model === "first_touch") weights = parties.map((p, n) => n === 0 ? 1 : 0);
  else if (model === "last_touch") weights = parties.map((p, n) => n === parties.length - 1 ? 1 : 0);
  else if (model === "linear") weights = parties.map(() => 1 / parties.length);
  else if (model === "position_based") weights = parties.map((p, n) => parties.length === 1 ? 1 : (n === 0 || n === parties.length - 1) ? 0.4 : 0.2 / Math.max(1, parties.length - 2));
  else if (model === "time_decay") { const t0 = new Date(parties[0].created_at).getTime(); const tn = new Date(parties[parties.length - 1].created_at).getTime() || t0 + 1; weights = parties.map(p => { const t = new Date(p.created_at).getTime(); return tn === t0 ? 1 / parties.length : 0.2 + 0.8 * ((t - t0) / (tn - t0)); }); }
  else if (model === "identity_stitch") { const byOwner = {}; parties.forEach(p => { byOwner[p.party] = (byOwner[p.party] || 0) + 1; }); weights = parties.map(p => 1 / (parties.length * 1)); }
  else weights = parties.map((p, n) => n === parties.length - 1 ? 1 : 0);
  const sum = weights.reduce((n, w) => n + w, 0) || 1;
  const byParty = {};
  parties.forEach((p, n) => {
    const share = weights[n] / sum;
    const k = p.party_type + ":" + p.party;
    byParty[k] = byParty[k] || { party: p.party, party_type: p.party_type, share: 0, revenue: 0, touches: 0 };
    byParty[k].share += share; byParty[k].revenue += revenue * share; byParty[k].touches++;
  });
  const rate = Number(i.commission_rate || 0);
  const credits = Object.values(byParty).map(c => ({ ...c, share: r4(c.share), revenue: r2(c.revenue), commission: r2(c.revenue * rate / 100) }));
  meter(tenantId, "goip.attribute", 1);
  return { model, revenue: r2(revenue), path: path.length, credits };
}

/* ═══════════════ 31 · FUNDING FABRIC (budgets · reserves · burn · treasury) ═══════════════ */
function budgets(tenantId, filter) {
  const f = filter || {}; const w = ["(tenant_id=? OR tenant_id=0)"]; const a = [tenantId];
  if (f.funder) { w.push("funder=?"); a.push(S(f.funder)); }
  if (f.domain) { w.push("domain=?"); a.push(S(f.domain)); }
  if (f.status) { w.push("status=?"); a.push(S(f.status)); }
  return db().all(`SELECT * FROM goip_budgets WHERE ${w.join(" AND ")} ORDER BY id DESC`, ...a).map(b => ({
    ...b, policy: J(b.policy, {}), available: r2(Number(b.allocated) - Number(b.reserved) - Number(b.consumed)),
    burn_pct: Number(b.allocated) ? Math.round(Number(b.consumed) / Number(b.allocated) * 100) : 0
  }));
}
function fund(tenantId, input) {
  const i = input || {}; const Db = db();
  const funder = FUNDERS.includes(S(i.funder)) ? S(i.funder) : "self";
  const unit = S(i.unit || "USD").toUpperCase();
  const domain = S(i.domain || "incentive");
  const existing = i.id ? Db.get("SELECT * FROM goip_budgets WHERE id=? AND (tenant_id=? OR tenant_id=0)", Number(i.id), tenantId)
    : Db.get("SELECT * FROM goip_budgets WHERE tenant_id=? AND funder=? AND funder_ref=? AND unit=? AND domain=? AND period=? AND status='open'", tenantId, funder, S(i.funder_ref || ""), unit, domain, S(i.period || period()));
  let id;
  if (existing) { Db.run("UPDATE goip_budgets SET allocated=allocated+?, policy=?, updated_at=datetime('now') WHERE id=?", Number(i.amount) || 0, JSON.stringify(i.policy || J(existing.policy, {})), existing.id); id = existing.id; }
  else id = Number(Db.run(`INSERT INTO goip_budgets(tenant_id,domain,funder,funder_ref,unit,allocated,reserved,consumed,period,status,policy)
      VALUES(?,?,?,?,?,?,0,0,?, 'open',?)`, tenantId, domain, funder, S(i.funder_ref || ""), unit, Number(i.amount) || 0, S(i.period || period()), JSON.stringify(i.policy || {})).lastInsertRowid);
  meter(tenantId, "goip.fund", 1, { currency: unit });
  return { ok: true, id, funder, unit, domain, period: S(i.period || period()) };
}
/* a store spends its own budget first, then the platform-wide (tenant 0) budget it inherits, and
   always the most specific match: exact funder ref before any ref, exact domain before `incentive`. */
function budgetFor(tenantId, funder, funderRef, unit, domain) {
  const Db = db();
  return Db.get(`SELECT * FROM goip_budgets WHERE (tenant_id=? OR tenant_id=0) AND funder=? AND unit=?
      AND (funder_ref=? OR funder_ref='') AND (domain=? OR domain='incentive') AND status='open' AND period=?
    ORDER BY (tenant_id<>0) DESC, (funder_ref<>'') DESC, (domain<>'incentive') DESC LIMIT 1`,
    tenantId, S(funder || "self"), S(unit || "USD").toUpperCase(), S(funderRef || ""), S(domain || "incentive"), period());
}
function reserveBudget(tenantId, b, amount) { if (!b) return false; db().run("UPDATE goip_budgets SET reserved=reserved+?, updated_at=datetime('now') WHERE id=?", r2(amount), b.id); return true; }
function consumeBudget(tenantId, funder, funderRef, unit, domain, amount, fromReserved) {
  const b = budgetFor(tenantId, funder, funderRef, unit, domain); if (!b) return null;
  db().run("UPDATE goip_budgets SET consumed=consumed+?, reserved=MAX(0,reserved-?), updated_at=datetime('now') WHERE id=?", r2(amount), fromReserved ? r2(amount) : 0, b.id);
  const after = db().get("SELECT * FROM goip_budgets WHERE id=?", b.id);
  if (Number(after.allocated) && Number(after.consumed) >= Number(after.allocated)) db().run("UPDATE goip_budgets SET status='exhausted' WHERE id=?", b.id);
  return { id: b.id, consumed: r2(after.consumed), allocated: r2(after.allocated) };
}
function treasury(tenantId) {
  const rows = budgets(tenantId, {});
  const byUnit = {};
  for (const b of rows) {
    const u = byUnit[b.unit] = byUnit[b.unit] || { unit: b.unit, allocated: 0, reserved: 0, consumed: 0, available: 0, budgets: 0 };
    u.allocated += Number(b.allocated); u.reserved += Number(b.reserved); u.consumed += Number(b.consumed); u.available += b.available; u.budgets++;
  }
  const burn = burnRate(tenantId);
  return { positions: Object.values(byUnit).map(u => ({ ...u, allocated: r2(u.allocated), reserved: r2(u.reserved), consumed: r2(u.consumed), available: r2(u.available) })), burn };
}
function burnRate(tenantId) {
  const Db = db();
  const rows = Db.all(`SELECT substr(created_at,1,7) period, COALESCE(SUM(amount),0) discount, COALESCE(SUM(credits),0) credits, COUNT(*) n
    FROM coupon_redemptions WHERE tenant_id=? AND status='redeemed' GROUP BY 1 ORDER BY 1 DESC LIMIT 6`, tenantId);
  const per = rows.map(r => ({ period: r.period, cost: r2(Number(r.discount) + Number(r.credits)), redemptions: r.n }));
  const avg = per.length ? r2(per.reduce((n, p) => n + p.cost, 0) / per.length) : 0;
  return { monthly: per, average: avg, latest: per[0] || null };
}

/* ═══════════════ 32 · SETTLEMENT · PAYOUT · RECONCILIATION · RECOVERY ═══════════════ */
function partiesFor(row, redemption) {
  const funding = J(row && row.funding, {});
  const split = arr(funding.parties);
  if (split.length) {
    const total = split.reduce((n, p) => n + (Number(p.share) || 0), 0) || 1;
    return split.map(p => ({ party: S(p.party || p.ref || row.funder_ref || "unnamed"), party_type: S(p.party_type || p.type || "partner"), share: (Number(p.share) || 0) / total }));
  }
  const f = S((redemption && redemption.funder) || (row && row.funder) || "self");
  let party = S((redemption && redemption.funder_ref) || (row && row.funder_ref) || "");
  if (!party && f === "self") { const t = db().get("SELECT slug FROM tenants WHERE id=?", Number((redemption && redemption.tenant_id) || 0)); party = (t && t.slug) || "merchant"; }
  return [{ party: party || f, party_type: f === "self" ? "merchant" : f, share: 1 }];
}
function accrue(tenantId, key, amount, n, unit) {
  const Db = db();
  const row = Db.get("SELECT * FROM goip_settlements WHERE tenant_id=? AND period=? AND party=? AND party_type=? AND unit=? AND status='accrued'", tenantId, key.period, key.party, key.party_type, unit);
  if (row) { Db.run("UPDATE goip_settlements SET gross=gross+?, net=net+?, redemptions=redemptions+?, updated_at=datetime('now') WHERE id=?", r2(amount), r2(amount), Number(n) || 1, row.id); return row.id; }
  return Number(Db.run(`INSERT INTO goip_settlements(tenant_id,period,party,party_type,unit,gross,fees,net,redemptions,status,meta) VALUES(?,?,?,?,?,?,0,?,?, 'accrued',?)`,
    tenantId, key.period, key.party, key.party_type, unit, r2(amount), r2(amount), Number(n) || 1, JSON.stringify({ opened: nowIso() })).lastInsertRowid);
}
/* the settlement run: every redeemed-but-unsettled redemption is attributed to its funding parties exactly once */
function settle(tenantId, opts) {
  const o = opts || {}; const Db = db(); const per = S(o.period || period());
  const rows = Db.all(`SELECT r.*, o.funding, o.funder AS o_funder, o.funder_ref AS o_funder_ref, o.economic_unit, o.domain AS o_domain FROM coupon_redemptions r
    LEFT JOIN offers o ON o.id=r.offer_id
    WHERE r.tenant_id=? AND r.status='redeemed' AND (r.settlement_id IS NULL OR r.settlement_id=0) AND substr(r.created_at,1,7)<=?`, tenantId, per);
  let settled = 0; const touched = new Set();
  for (const r of rows) {
    const unit = S(r.unit || r.economic_unit || "USD").toUpperCase();
    const amount = r2(Number(r.amount) + Number(r.credits || 0));
    if (amount <= 0) { Db.run("UPDATE coupon_redemptions SET settlement_id=-1 WHERE id=?", r.id); continue; }
    const parties = partiesFor({ funding: r.funding, funder: r.o_funder || r.funder, funder_ref: r.o_funder_ref || r.funder_ref }, r);
    let last = null;
    for (const p of parties) {
      const id = accrue(tenantId, { period: S(r.created_at).slice(0, 7), party: p.party || p.party_type, party_type: p.party_type }, amount * p.share, 1 / parties.length, unit);
      touched.add(id); last = id;
    }
    Db.run("UPDATE coupon_redemptions SET settlement_id=? WHERE id=?", last, r.id);
    settled++;
  }
  meter(tenantId, "goip.settlement", Math.max(1, touched.size));
  return { ok: true, period: per, redemptions_settled: settled, settlements: [...touched].length, rows: settlements(tenantId, { period: per }) };
}
function settlements(tenantId, filter) {
  const f = filter || {}; const w = ["tenant_id=?"]; const a = [tenantId];
  if (f.period) { w.push("period=?"); a.push(S(f.period)); }
  if (f.status) { w.push("status=?"); a.push(S(f.status)); }
  if (f.party) { w.push("party=?"); a.push(S(f.party)); }
  return db().all(`SELECT * FROM goip_settlements WHERE ${w.join(" AND ")} ORDER BY id DESC LIMIT 500`, ...a).map(r => ({ ...r, meta: J(r.meta, {}) }));
}
function approveSettlement(tenantId, id) { const r = db().run("UPDATE goip_settlements SET status='approved', updated_at=datetime('now') WHERE id=? AND tenant_id=? AND status='accrued'", Number(id), tenantId); return { ok: !!r.changes }; }
function pay(tenantId, input) {
  const i = input || {}; const Db = db();
  const s = Db.get("SELECT * FROM goip_settlements WHERE id=? AND tenant_id=?", Number(i.id), tenantId);
  if (!s) return { error: "Unknown settlement", code: 404 };
  if (s.status === "paid" || s.status === "reconciled") return { error: "Already paid", code: 409 };
  const fees = r2(Number(i.fees) || 0);
  const net = r2(Number(s.gross) - fees);
  const ref = S(i.reference || ("PAYOUT-" + new Date().getFullYear() + "-" + String(s.id).padStart(5, "0")));
  Db.run("UPDATE goip_settlements SET status='paid', fees=?, net=?, reference=?, paid_at=datetime('now'), updated_at=datetime('now') WHERE id=?", fees, net, ref, s.id);
  /* an internal party (a wallet owner) is paid into the ledger the platform already owns */
  if (i.to_wallet && i.owner) { try { offersMod().credit(tenantId, S(i.owner), net, "transfer", "goip:payout:" + ref, s.unit, "settlement", "goip"); } catch (e) { } }
  const suid = uidOf("goip_settlements", s.id);
  if (suid) edge(tenantId, "PAID_TO", "settlement", suid, S(s.party_type || "partner"), S(s.party), { net, unit: s.unit, reference: ref });
  meter(tenantId, "goip.payout", 1, { currency: s.unit });
  try { require("./events.js").emit(tenantId, "goip.payout", { settlement: s.id, party: s.party, net, unit: s.unit, reference: ref }, { uid: suid }); } catch (e) { }
  return { ok: true, id: s.id, reference: ref, net, unit: s.unit };
}
function reconcile(tenantId, input) {
  const i = input || {}; const Db = db();
  const r = Db.run("UPDATE goip_settlements SET status='reconciled', meta=?, updated_at=datetime('now') WHERE id=? AND tenant_id=? AND status='paid'",
    JSON.stringify({ reconciled_at: nowIso(), external_ref: S(i.external_ref || ""), note: S(i.note || "") }), Number(i.id), tenantId);
  return { ok: !!r.changes };
}
/* recovery: a refunded order claws its settlement back (offers.reverseRedemption raises the hook) */
function recover(tenantId, ref) {
  const Db = db(); const oid = ref && ref.order_id; if (!oid) return { ok: false };
  const rows = Db.all("SELECT * FROM coupon_redemptions WHERE tenant_id=? AND order_id=? AND settlement_id IS NOT NULL AND settlement_id>0", tenantId, oid);
  let recovered = 0;
  for (const r of rows) {
    const amount = r2(Number(r.amount) + Number(r.credits || 0));
    const s = Db.get("SELECT * FROM goip_settlements WHERE id=?", r.settlement_id);
    if (s && (s.status === "accrued" || s.status === "approved")) {
      Db.run("UPDATE goip_settlements SET gross=MAX(0,gross-?), net=MAX(0,net-?), redemptions=MAX(0,redemptions-1), updated_at=datetime('now') WHERE id=?", amount, amount, s.id);
    } else if (s) {
      Db.run(`INSERT INTO goip_settlements(tenant_id,period,party,party_type,unit,gross,fees,net,redemptions,status,meta) VALUES(?,?,?,?,?,?,0,?,1,'reversed',?)`,
        tenantId, s.period, s.party, s.party_type, s.unit, -amount, -amount, JSON.stringify({ recovers: s.id, order_id: oid }));
    }
    Db.run("UPDATE coupon_redemptions SET settlement_id=NULL WHERE id=?", r.id);
    recovered++;
  }
  /* entitlements granted by that order are revoked with it */
  try { Db.run("UPDATE goip_entitlements SET status='revoked' WHERE tenant_id=? AND source_redemption IN (SELECT id FROM coupon_redemptions WHERE order_id=?) AND status='active'", tenantId, oid); } catch (e) { }
  return { ok: true, recovered };
}

/* ═══════════════ 33 · POST-REDEMPTION (grants · deferred value · budget burn · accrual · graph) ═══════════════ */
function postRedeem(ctx, result, ref) {
  const tid = Number(ctx.tenantId || 0); if (!tid) return;
  const Db = db(); const owner = S(ctx.owner || "");
  const oid = ref && ref.order_id;
  for (const rd of arr(result && result.redemptions)) {
    const row = rd.offer_id ? Db.get("SELECT * FROM offers WHERE id=?", rd.offer_id) : null;
    const unit = S(rd.unit || (row && row.economic_unit) || ctx.currency || "USD").toUpperCase();
    const amount = r2(Number(rd.amount || 0) + Number(rd.credits || 0));
    const redemption = Db.get("SELECT id FROM coupon_redemptions WHERE tenant_id=? AND COALESCE(offer_id,0)=? AND COALESCE(code,'')=? ORDER BY id DESC LIMIT 1", tid, Number(rd.offer_id || 0), S(rd.code || ""));
    if (rd.grant && owner) {
      const g = grantEntitlement(tid, owner, rd.grant, { offer_id: rd.offer_id || null, redemption_id: redemption && redemption.id, funder: rd.funder, funder_ref: rd.funder_ref });
      if (g && row) { const ou = uidOf("offers", row.id); if (ou) edge(tid, "ISSUED_BY", g.kind === "coupon" ? "coupon" : "benefit", S(g.code || g.id), "offer", ou, { benefit: rd.grant.benefit }); }
    }
    if (rd.defer && owner) {
      grantEntitlement(tid, owner, { benefit: "deferred_cashback", unit, qty: Number(rd.credits) || 0, days: Number(rd.defer) || 0, due: true, ref: (ref && ref.order_num) || "" },
        { offer_id: rd.offer_id || null, redemption_id: redemption && redemption.id });
    }
    if (amount > 0) {
      const burn = consumeBudget(tid, S(rd.funder || (row && row.funder) || "self"), S(rd.funder_ref || (row && row.funder_ref) || ""), unit, S((row && row.domain) || "incentive"), amount, true);
      if (burn && row) { const ou = uidOf("offers", row.id); if (ou) edge(tid, "FUNDED_BY", "offer", ou, "budget", String(burn.id), { amount, unit }); }
    }
    if (row) {
      const ou = uidOf("offers", row.id);
      if (ou && owner) edge(tid, "REDEEMED_BY", "offer", ou, "customer", owner, { amount, unit, order: (ref && ref.order_num) || null });
      if (ou) edge(tid, "FUNDED_BY", "offer", ou, S(rd.funder || row.funder || "self"), S(rd.funder_ref || row.funder_ref || row.funder || "self"), { amount, unit });
    }
    meter(tid, "goip.redemption", 1, { currency: unit });
  }
  if (oid && owner) { try { track(tid, { kind: "conversion", owner, order_id: oid, value: Number((ref && ref.value) || result.discount || 0), party: owner, party_type: "customer", channel: ctx.channel || "commerce" }); } catch (e) { } }
}
/* deferred value becomes real money on its due date — swept by the settle capability or a scheduled call */
function releaseDeferred(tenantId) {
  const Db = db(); let released = 0;
  const rows = Db.all("SELECT * FROM goip_entitlements WHERE tenant_id=? AND benefit='deferred_cashback' AND status='active' AND ends IS NOT NULL AND ends<=?", tenantId, today());
  for (const e of rows) {
    try {
      if (moneyUnit(e.unit)) offersMod().credit(tenantId, e.owner, Number(e.qty) || 0, "cashback", "goip:deferred:" + e.id, e.unit, "commerce", "goip");
      else offersMod().ledgerEntry(tenantId, e.owner, e.unit, "reward", Number(e.qty) || 0, "goip:deferred:" + e.id, "commerce", "goip");
      Db.run("UPDATE goip_entitlements SET status='consumed', meta=? WHERE id=?", JSON.stringify({ released_at: nowIso() }), e.id);
      released++;
    } catch (err) { }
  }
  return { ok: true, released };
}

/* ═══════════════ 34 · VALUE-EXCHANGE WRITER (the single writer for the `offers` table) ═══════════════ */
function benefitOf(key) { return arr(REG("goipBenefits")).find(b => b.key === key || b.type === key) || null; }
function normalize(body, opts) {
  const b = body || {}; const o = opts || {};
  const types = arr(registryMod().list("offerTypes"));
  const ben = benefitOf(S(b.benefit || b.type));
  const type = ben ? ben.type : S(b.type);
  if (!S(b.name)) return { error: "A name is required" };
  if (!types.some(t => t.key === type)) return { error: "Unknown benefit/offer type: " + (b.benefit || b.type) };
  const dirs = arr(registryMod().list("offerDirections")), chans = arr(registryMod().list("offerChannels")),
    scopes = arr(registryMod().list("offerScopes")), funders = arr(registryMod().list("offerFunders")), stacks = arr(registryMod().list("stackingPolicies"));
  const globalReq = (S(b.scope_level) === "global" || Number(b.tenant_id) === 0) && o.platform;
  const dom = arr(REG("goipDomains")).find(d => d.key === S(b.domain)) || null;
  const gov = Object.assign({ state: "draft", version: 1, jurisdictions: [], terms: "", approvals: [] }, J(b.governance, {}));
  if (!GOVERNANCE_STATES.includes(S(gov.state))) gov.state = "draft";
  const f = {
    tenant_id: globalReq ? 0 : Number(o.tenantId || 0), scope_level: globalReq ? "global" : "tenant",
    name: S(b.name), code: S(b.code || "").toUpperCase(), type,
    direction: dirs.includes(S(b.direction)) ? S(b.direction) : ((ben && ben.direction) || (types.find(t => t.key === type) || {}).direction || "discount"),
    channel: chans.includes(S(b.channel)) ? S(b.channel) : "commerce",
    scope_type: scopes.includes(S(b.scope_type)) ? S(b.scope_type) : "store",
    funder: funders.includes(S(b.funder)) ? S(b.funder) : "self", funder_ref: S(b.funder_ref || ""), brand_ref: S(b.brand_ref || ""),
    value: Number(b.value) || 0, currency: S(b.currency || "USD").toUpperCase(),
    min_amount: Number(b.min_amount) || 0, min_qty: Number(b.min_qty) || 0, max_discount: Number(b.max_discount) || 0,
    usage_limit: Number(b.usage_limit) || 0, per_owner_limit: Number(b.per_owner_limit) || 0,
    stack_group: S(b.stack_group || ""), stack_policy: stacks.includes(S(b.stack_policy)) ? S(b.stack_policy) : "stack_with_others",
    priority: Number(b.priority) || 0, scope_value: JSON.stringify(b.scope || b.scope_value || {}), rules: JSON.stringify(b.rules || {}),
    starts: b.starts || null, ends: b.ends || null,
    status: arr(registryMod().list("offerStatuses")).includes(S(b.status)) ? S(b.status) : "active", summary: S(b.summary || ""),
    /* ── constitutional columns ── */
    domain: dom ? dom.key : "incentive", benefit: ben ? ben.key : type, reality: (arr(REG("goipRealities")).some(r => r.key === S(b.reality)) ? S(b.reality) : "any"),
    economic_unit: S(b.economic_unit || b.unit || "").toUpperCase(),
    temporal_spec: JSON.stringify(b.temporal || b.temporal_spec || {}), spatial_spec: JSON.stringify(b.spatial || b.spatial_spec || {}),
    conditions: JSON.stringify(b.conditions || {}), distribution: JSON.stringify(arr(b.distribution)), attribution_model: arr(REG("goipAttributionModels")).includes(S(b.attribution_model)) ? S(b.attribution_model) : "last_touch",
    funding: JSON.stringify(b.funding || {}), governance: JSON.stringify(gov), campaign: S(b.campaign || ""),
    version: Number(b.version) || gov.version || 1, parent_id: b.parent_id ? Number(b.parent_id) : null
  };
  return { ok: true, fields: f, global: globalReq };
}
function createExchange(tenantId, body, opts) {
  const o = Object.assign({ tenantId }, opts || {});
  const n = normalize(body, o); if (n.error) return n;
  const f = n.fields; const Db = db();
  const K = Object.keys(f), V = K.map(k => f[k]);
  let id = (body && body.id) || (opts && opts.id) || null;
  if (id) {
    const owns = Db.get("SELECT id,tenant_id FROM offers WHERE id=?", Number(id)); if (!owns) return { error: "Not found", code: 404 };
    if (owns.tenant_id !== f.tenant_id && !(o.platform && owns.tenant_id === 0)) return { error: "Not permitted", code: 403 };
    Db.run(`UPDATE offers SET ${K.map(k => k + "=?").join(",")} WHERE id=?`, ...V, Number(id));
  } else {
    Db.run(`INSERT INTO offers(${K.join(",")}) VALUES(${K.map(() => "?").join(",")})`, ...V);
    id = Number(Db.get("SELECT id FROM offers ORDER BY id DESC LIMIT 1").id);
  }
  const uid = uidOf("offers", id);
  if (uid) {
    if (f.campaign) edge(f.tenant_id, "PART_OF", "offer", uid, "campaign", f.campaign, {});
    if (f.brand_ref) edge(f.tenant_id, "TARGETED_TO", "offer", uid, "brand", f.brand_ref, {});
    edge(f.tenant_id, "GOVERNED_BY", "offer", uid, "policy", "platform", { state: J(f.governance, {}).state });
    for (const ch of J(f.distribution, [])) edge(f.tenant_id, "DISTRIBUTED_BY", "offer", uid, "channel", S(ch), {});
    if (o.generated_by) edge(f.tenant_id, "GENERATED_BY", "offer", uid, "engine", S(o.generated_by), {});
  }
  meter(tenantId, "goip.create", 1, { currency: f.currency });
  try { require("./events.js").emit(f.tenant_id, "offer.created", { id, name: f.name, domain: f.domain, benefit: f.benefit, global: n.global }, { uid }); } catch (e) { }
  return { ok: true, id, uid, global: n.global, domain: f.domain, benefit: f.benefit };
}
function exchange(tenantId, id) {
  const r = db().get("SELECT * FROM offers WHERE id=? AND (tenant_id=? OR tenant_id=0)", Number(id), tenantId);
  if (!r) return null;
  return Object.assign({}, r, { scope: J(r.scope_value, {}), rules: J(r.rules, {}), temporal: J(r.temporal_spec, {}), spatial: J(r.spatial_spec, {}), conditions: J(r.conditions, {}), distribution: J(r.distribution, []), funding: J(r.funding, {}), governance: J(r.governance, { state: "published" }), risk: riskScore(tenantId, r) });
}
function listExchanges(tenantId, filter) {
  const f = filter || {}; const w = ["(tenant_id=? OR tenant_id=0)"]; const a = [tenantId];
  if (f.domain) { w.push("domain=?"); a.push(S(f.domain)); }
  if (f.benefit) { w.push("benefit=?"); a.push(S(f.benefit)); }
  if (f.channel) { w.push("channel=?"); a.push(S(f.channel)); }
  if (f.status) { w.push("status=?"); a.push(S(f.status)); }
  if (f.campaign) { w.push("campaign=?"); a.push(S(f.campaign)); }
  if (f.global) { w[0] = "tenant_id=?"; a[0] = 0; }
  if (f.q) { w.push("(LOWER(name) LIKE ? OR LOWER(code) LIKE ? OR LOWER(summary) LIKE ?)"); const q = "%" + S(f.q).toLowerCase() + "%"; a.push(q, q, q); }
  return db().all(`SELECT * FROM offers WHERE ${w.join(" AND ")} AND deleted_at IS NULL ORDER BY priority DESC, id DESC LIMIT ?`, ...a, Math.min(500, Number(f.limit) || 200))
    .map(r => Object.assign({}, r, { scope: J(r.scope_value, {}), rules: J(r.rules, {}), governance: J(r.governance, { state: "published" }), distribution: J(r.distribution, []) }));
}

/* ═══════════════ 35 · ISSUANCE (the single writer for `coupons`) ═══════════════ */
function issue(tenantId, body) {
  const b = body || {}; const Db = db(); const crypto = require("crypto");
  const kinds = arr(registryMod().list("couponKinds")); const funders = arr(registryMod().list("offerFunders"));
  const kind = kinds.includes(S(b.kind)) ? S(b.kind) : "single_use";
  const funder = funders.includes(S(b.funder)) ? S(b.funder) : "self";
  const n = Math.min(1000, Math.max(1, Number(b.count) || 1));
  const batch = S(b.batch || (n > 1 ? "B" + Date.now().toString(36) : ""));
  let prefix = S(b.prefix || "");
  if (!prefix) { try { const st = require("./settings.js").load(tenantId); prefix = (st.offers && st.offers.couponCodePrefix) || ""; } catch (e) { } }
  const made = []; const errors = [];
  for (let i = 0; i < n; i++) {
    const code = S(n === 1 && b.code ? b.code : ((prefix || "GOIP") + "-" + crypto.randomBytes(3).toString("hex"))).toUpperCase();
    try {
      Db.run(`INSERT INTO coupons(tenant_id,code,offer_id,funder,funder_ref,brand_ref,kind,value,currency,max_uses,per_owner_limit,issued_to,batch,starts,ends,status,note)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, 'active',?)`, tenantId, code, b.offer_id ? Number(b.offer_id) : null, funder, S(b.funder_ref || ""), S(b.brand_ref || ""),
        kind, Number(b.value) || 0, S(b.currency || "USD").toUpperCase(), Number(b.max_uses) || 1, Number(b.per_owner_limit) || 1, S(b.issued_to || ""), batch,
        b.starts || null, b.ends || null, S(b.note || (n > 1 ? "bulk" : "")));
      made.push(code);
      const cu = (Db.get("SELECT uid FROM coupons WHERE tenant_id=? AND code=?", tenantId, code) || {}).uid;
      if (cu && b.offer_id) { const ou = uidOf("offers", b.offer_id); if (ou) edge(tenantId, "PART_OF", "coupon", cu, "offer", ou, { kind }); }
      if (cu) edge(tenantId, "ISSUED_BY", "coupon", cu, funder === "self" ? "merchant" : funder, S(b.funder_ref || funder), { kind, batch });
    } catch (e) { if (n === 1) return { error: "Duplicate code", code: 409 }; errors.push(code); i--; if (errors.length > n * 3) break; }
  }
  meter(tenantId, "goip.issue", made.length);
  return { ok: true, batch, count: made.length, codes: made, code: made[0] };
}

/* ═══════════════ 36 · RESERVATION · ACTIVATION ═══════════════ */
function reserve(tenantId, input) {
  const i = input || {}; const Db = db();
  const res = decide(Object.assign({}, i, { tenantId }));
  if (!res.applied.length) return { ok: false, reason: "Nothing eligible to reserve", context: res.context };
  const ids = [];
  for (const rd of res.redemptions) {
    const row = rd.offer_id ? Db.get("SELECT * FROM offers WHERE id=?", rd.offer_id) : null;
    const unit = S(rd.unit || (row && row.economic_unit) || i.currency || "USD").toUpperCase();
    const amount = r2(Number(rd.amount || 0) + Number(rd.credits || 0));
    const rid = Number(Db.run(`INSERT INTO coupon_redemptions(tenant_id,coupon_id,offer_id,code,order_id,owner,channel,amount,credits,offer_type,funder,funder_ref,brand_ref,status,meta)
      VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?, 'reserved',?)`, tenantId, null, rd.offer_id || null, rd.code || null, i.order_id ? Number(i.order_id) : null, S(i.owner || ""),
      S(i.channel || "commerce"), r2(rd.amount || 0), r2(rd.credits || 0), S(rd.type || ""), S(rd.funder || "self"), S(rd.funder_ref || ""), S(rd.brand_ref || ""),
      JSON.stringify({ reserved_at: nowIso(), expires: new Date(Date.now() + (Number(i.ttl_minutes) || 30) * 60000).toISOString(), unit })).lastInsertRowid);
    const b = budgetFor(tenantId, S(rd.funder || "self"), S(rd.funder_ref || ""), unit, S((row && row.domain) || "incentive"));
    if (b) reserveBudget(tenantId, b, amount);
    ids.push(rid);
  }
  meter(tenantId, "goip.reserve", ids.length);
  return { ok: true, reservations: ids, discount: res.discount, credits: res.credits, applied: res.applied, expires_in_minutes: Number(i.ttl_minutes) || 30 };
}
function releaseReservation(tenantId, id) {
  const Db = db(); const r = Db.get("SELECT * FROM coupon_redemptions WHERE id=? AND tenant_id=? AND status='reserved'", Number(id), tenantId);
  if (!r) return { error: "Unknown reservation", code: 404 };
  const meta = J(r.meta, {}); const unit = S(meta.unit || "USD");
  const b = budgetFor(tenantId, r.funder, r.funder_ref, unit, "incentive");
  if (b) db().run("UPDATE goip_budgets SET reserved=MAX(0,reserved-?) WHERE id=?", r2(Number(r.amount) + Number(r.credits || 0)), b.id);
  Db.run("UPDATE coupon_redemptions SET status='voided', meta=? WHERE id=?", JSON.stringify(Object.assign(meta, { released_at: nowIso() })), r.id);
  return { ok: true };
}
/* activation: an owner opts in to an exchange (card-linked / app-activated offers). Eligibility can
   then demand it via rules.requires_activation — no new table, it is an entitlement. */
function activate(tenantId, input) {
  const i = input || {}; const Db = db();
  const row = i.offer_id ? Db.get("SELECT * FROM offers WHERE id=? AND (tenant_id=? OR tenant_id=0)", Number(i.offer_id), tenantId)
    : Db.get("SELECT * FROM offers WHERE code=? AND (tenant_id=? OR tenant_id=0)", S(i.code).toUpperCase(), tenantId);
  if (!row) return { error: "Unknown value exchange", code: 404 };
  const owner = S(i.owner || ""); if (!owner) return { error: "owner required" };
  const have = Db.get("SELECT id FROM goip_entitlements WHERE tenant_id=? AND owner=? AND benefit='activation' AND source_offer=? AND status='active'", tenantId, owner, row.id);
  if (have) return { ok: true, already: true, id: have.id };
  const g = grantEntitlement(tenantId, owner, { benefit: "activation", unit: "", qty: 1, days: Number(i.days || 0) || 0, ref: row.code || String(row.id) }, { offer_id: row.id });
  const ou = uidOf("offers", row.id); if (ou) edge(tenantId, "ACTIVATED_BY", "offer", ou, "customer", owner, { at: nowIso() });
  meter(tenantId, "goip.reserve", 1);
  return { ok: true, id: g && g.id, offer_id: row.id };
}

/* ═══════════════ 37 · PRICING · RECOMMENDATION · SIMULATION · FORECAST · OPTIMIZATION ═══════════════ */
function price(input) {
  const res = decide(input || {});
  const gross = r2(res.context.economic.amount);
  return { gross, discount: res.discount, credits: res.credits, free_shipping: res.freeShip, net: r2(Math.max(0, gross - res.discount)), unit: res.context.economic.unit, applied: res.applied };
}
function recommend(tenantId, input) {
  const i = input || {}; const rctx = resolveContext(Object.assign({ tenantId }, i));
  const pool = offersMod().eligible(tenantId, S(i.channel || "commerce"), i.coupon || "*", true);
  const out = [];
  for (const c of pool) {
    const el = eligibility(c, rctx);
    const w = benefitWeight(c, rctx.economic.amount);
    out.push({ id: c.id, name: c.name, code: c.code, type: c.type, benefit: S((c._row || {}).benefit || c.type), eligible: el.ok, reasons: el.reasons, est_value: r2(w), gap: el.ok ? null : el.reasons[0] });
  }
  out.sort((a, b) => (b.eligible - a.eligible) || (b.est_value - a.est_value));
  return { subject: i.owner || null, segments: rctx.audience.segments, recommendations: out.slice(0, Number(i.limit) || 10) };
}
/* simulation never writes: it replays real orders (or supplied carts) through the live decision pipeline */
function simulate(tenantId, input) {
  const i = input || {}; const Db = db();
  let carts = arr(i.carts);
  if (!carts.length) {
    const orders = Db.all("SELECT id, total, owner FROM orders WHERE tenant_id=? ORDER BY id DESC LIMIT ?", tenantId, Math.min(200, Number(i.sample) || 50));
    carts = orders.map(o => {
      const items = Db.all("SELECT product_id id, price, qty FROM order_items WHERE order_id=?", o.id);
      return { amount: Number(o.total) || 0, owner: o.owner, items: items.map(it => ({ id: it.id, price: Number(it.price), qty: Number(it.qty) })) };
    });
  }
  if (!carts.length) return { ok: true, carts: 0, note: "no orders to replay — pass carts[] to simulate" };
  let discount = 0, credits = 0, hits = 0, ship = 0; const byOffer = {};
  for (const c of carts) {
    const res = decide(Object.assign({ tenantId, channel: i.channel || "commerce", coupon: i.coupon, objective: i.objective }, c, { __resolved: null }));
    if (res.applied.length) hits++;
    discount += res.discount; credits += res.credits; if (res.freeShip) ship++;
    for (const a of res.applied) { const k = a.name; byOffer[k] = byOffer[k] || { name: k, applications: 0, cost: 0 }; byOffer[k].applications++; byOffer[k].cost += (a.amount || 0) + (a.credits || 0); }
  }
  const gross = carts.reduce((n, c) => n + (Number(c.amount) || 0), 0);
  return {
    ok: true, carts: carts.length, gross: r2(gross), discount: r2(discount), credits: r2(credits), free_shipping: ship,
    take_rate_pct: gross ? +((discount + credits) / gross * 100).toFixed(2) : 0, hit_rate_pct: +(hits / carts.length * 100).toFixed(1),
    avg_cost_per_cart: r2((discount + credits) / carts.length), by_exchange: Object.values(byOffer).map(o => ({ ...o, cost: r2(o.cost) })).sort((a, b) => b.cost - a.cost)
  };
}
function forecast(tenantId, input) {
  const i = input || {}; const months = Math.min(12, Math.max(1, Number(i.months) || 3));
  const burn = burnRate(tenantId); const series = burn.monthly.slice().reverse();
  const n = series.length;
  let slope = 0, base = burn.average;
  if (n >= 2) { const first = series[0].cost, last = series[n - 1].cost; slope = (last - first) / Math.max(1, n - 1); base = last; }
  const projection = []; const start = new Date();
  for (let m = 1; m <= months; m++) {
    const d = new Date(start.getFullYear(), start.getMonth() + m, 1);
    projection.push({ period: d.toISOString().slice(0, 7), projected_cost: r2(Math.max(0, base + slope * m)), basis: n >= 2 ? "trend" : "average" });
  }
  const t = treasury(tenantId);
  const available = t.positions.reduce((s, p) => s + (moneyUnit(p.unit) ? p.available : 0), 0);
  const monthly = projection[0] ? projection[0].projected_cost : 0;
  const runway = monthly > 0 ? Math.floor(available / monthly) : null;
  const liability = db().get("SELECT COALESCE(SUM(qty),0) q FROM goip_entitlements WHERE tenant_id=? AND status='active'", tenantId) || { q: 0 };
  return { history: burn.monthly, projection, available: r2(available), runway_months: runway, outstanding_entitlements: r2(liability.q), exhaustion: runway != null ? new Date(Date.now() + runway * 2629746000).toISOString().slice(0, 10) : null };
}
function optimize(tenantId, input) {
  const i = input || {}; const objective = S(i.objective || "balanced"); const Db = db();
  const rows = listExchanges(tenantId, { status: "active", limit: 200 });
  const budgetCap = Number(i.budget) || (treasury(tenantId).positions.find(p => moneyUnit(p.unit)) || {}).available || 0;
  const proposals = [];
  for (const o of rows) {
    const use = Db.get("SELECT COUNT(*) n, COALESCE(SUM(amount),0) a, COALESCE(SUM(credits),0) c FROM coupon_redemptions WHERE offer_id=? AND status='redeemed'", o.id) || { n: 0, a: 0, c: 0 };
    const cost = r2(Number(use.a) + Number(use.c));
    const risk = riskScore(tenantId, o);
    const per = use.n ? r2(cost / use.n) : 0;
    if (risk.score >= 60) proposals.push({ id: o.id, name: o.name, action: "add_guardrail", change: { max_discount: o.max_discount || r2(per * 2 || 25), usage_limit: o.usage_limit || Math.max(50, use.n * 2), per_owner_limit: o.per_owner_limit || 1 }, why: "risk " + risk.score + ": " + risk.signals.slice(0, 2).join("; "), impact: "caps worst-case exposure" });
    if (!use.n && o.status === "active") proposals.push({ id: o.id, name: o.name, action: "retire_or_reprice", change: { value: r2(Number(o.value) * 1.25) }, why: "zero redemptions since launch", impact: "either lift the benefit or free the budget" });
    if (use.n > 0 && budgetCap && cost > budgetCap * 0.4) proposals.push({ id: o.id, name: o.name, action: "reduce_value", change: { value: r2(Number(o.value) * (budgetCap * 0.4 / cost)) }, why: "consumes " + Math.round(cost / budgetCap * 100) + "% of available budget", impact: "fits the exchange inside its funding envelope" });
    if (objective === "max_conversion" && o.code && use.n === 0) proposals.push({ id: o.id, name: o.name, action: "drop_code_requirement", change: { code: "" }, why: "coded exchange with no redemptions", impact: "auto-apply raises take-up" });
  }
  meter(tenantId, "goip.intelligence", 1);
  return { objective, budget: r2(budgetCap), proposals: proposals.slice(0, 25), evaluated: rows.length };
}

/* ═══════════════ 38 · INTELLIGENCE FABRIC (15 real readings, no placeholders) ═══════════════ */
const INTEL = {
  deal: tid => { const D = db(); return { top: D.all("SELECT o.id,o.name,o.type,o.value,COUNT(r.id) n, COALESCE(SUM(r.amount),0) discount FROM offers o LEFT JOIN coupon_redemptions r ON r.offer_id=o.id AND r.status='redeemed' WHERE (o.tenant_id=? OR o.tenant_id=0) GROUP BY o.id ORDER BY n DESC LIMIT 10", tid) }; },
  offer: tid => offersMod().analytics(tid),
  price: tid => { const D = db(); const p = D.get("SELECT COALESCE(AVG(total),0) avg_order, COUNT(*) n FROM orders WHERE tenant_id=?", tid) || {}; const d = D.get("SELECT COALESCE(AVG(amount),0) avg_discount FROM coupon_redemptions WHERE tenant_id=? AND status='redeemed'", tid) || {}; return { avg_order: r2(p.avg_order), orders: p.n, avg_discount: r2(d.avg_discount), effective_margin_impact_pct: p.avg_order ? +(d.avg_discount / p.avg_order * 100).toFixed(2) : 0 }; },
  audience: tid => { const D = db(); const seg = {}; for (const r of D.all("SELECT owner, COUNT(*) n, COALESCE(SUM(amount),0) a FROM coupon_redemptions WHERE tenant_id=? AND status='redeemed' GROUP BY owner ORDER BY a DESC LIMIT 100", tid)) { const s = personalize(tid, r.owner, { orders: r.n, lifetime: r.a }); for (const k of s) { seg[k] = seg[k] || { segment: k, subjects: 0, value: 0 }; seg[k].subjects++; seg[k].value += Number(r.a); } } return { segments: Object.values(seg).map(s => ({ ...s, value: r2(s.value) })) }; },
  merchant: () => { const D = db(); return { stores: D.all("SELECT t.slug, t.name, COUNT(r.id) redemptions, COALESCE(SUM(r.amount),0) discount FROM tenants t LEFT JOIN coupon_redemptions r ON r.tenant_id=t.id GROUP BY t.id ORDER BY redemptions DESC").map(x => ({ ...x, discount: r2(x.discount) })) }; },
  provider: tid => { const D = db(); return { providers: D.all("SELECT gateway provider, method, COUNT(*) n, COALESCE(SUM(amount),0) v, COALESCE(SUM(fee),0) fees FROM payments WHERE tenant_id=? GROUP BY gateway, method ORDER BY n DESC", tid).map(x => ({ ...x, v: r2(x.v), fees: r2(x.fees) })) }; },
  partner: tid => { const D = db(); return { parties: D.all("SELECT party, party_type, COUNT(*) touches, COALESCE(SUM(value),0) value FROM goip_touchpoints WHERE tenant_id=? AND party_type<>'customer' GROUP BY party, party_type ORDER BY touches DESC LIMIT 25", tid).map(x => ({ ...x, value: r2(x.value) })) }; },
  fraud: tid => { const D = db(); const owners = D.all("SELECT DISTINCT owner FROM coupon_redemptions WHERE tenant_id=? AND created_at > datetime('now','-30 day') LIMIT 200", tid); const scored = owners.map(o => ({ owner: o.owner, ...fraudScore(tid, o.owner) })).filter(x => x.score > 0).sort((a, b) => b.score - a.score); return { flagged: scored.slice(0, 20), scanned: owners.length }; },
  optimization: tid => optimize(tid, {}),
  forecast: tid => forecast(tid, {}),
  recommendation: tid => recommend(tid, { limit: 10 }),
  /* generation: proposals are DRAFTS. Nothing is published without the governance engine. */
  ai_offer_generation: (tid, i) => {
    const D = db(); const dept = D.all("SELECT dept, COUNT(*) n, COALESCE(AVG(price),0) p FROM products WHERE tenant_id=? GROUP BY dept ORDER BY n DESC LIMIT 5", tid);
    const slow = D.all("SELECT id, title, dept, price FROM products WHERE tenant_id=? AND stock > 20 ORDER BY ratings_count ASC LIMIT 5", tid);
    return { drafts: dept.map((d, n) => ({ name: (d.dept || "store").toUpperCase() + " · " + (10 + n * 5) + "% category push", benefit: "percentage_discount", value: 10 + n * 5, domain: "offer", scope_type: "category", scope: { categories: [d.dept] }, min_amount: r2(Number(d.p) * 1.5), rationale: d.n + " products, avg " + r2(d.p) })).concat(slow.slice(0, 2).map(p => ({ name: "Move slow stock · " + p.title, benefit: "flat_discount", value: r2(Number(p.price) * 0.15), domain: "deal", scope_type: "product", scope: { products: [p.id] }, rationale: "high stock, low review velocity" }))) };
  },
  ai_incentive_generation: (tid, i) => {
    const t = treasury(tid); const avail = (t.positions.find(p => moneyUnit(p.unit)) || { available: 0 }).available;
    const segs = INTEL.audience(tid).segments;
    return { drafts: segs.slice(0, 4).map(s => ({ name: "Win-back · " + s.segment, benefit: s.segment === "high_value" ? "reward_points" : "cashback", value: s.segment === "high_value" ? 500 : 5, domain: s.segment === "high_value" ? "reward" : "cashback", scope_type: "audience", scope: { audience: [s.segment] }, funding: { parties: [{ party: "merchant", party_type: "merchant", share: 1 }] }, budget_hint: r2(avail / Math.max(1, segs.length)), rationale: s.subjects + " subjects worth " + r2(s.value) })) };
  },
  autonomous_campaign: (tid, i) => {
    const gen = INTEL.ai_offer_generation(tid, i).drafts.slice(0, 3);
    const name = "AUTO-" + new Date().toISOString().slice(0, 10).replace(/-/g, "");
    return { campaign: name, steps: gen.map((g, n) => ({ order: n + 1, exchange: g, distribution: ["email", "in_app", n === 0 ? "push" : "widget"], starts: new Date(Date.now() + n * 7 * 86400000).toISOString().slice(0, 10), governance: "draft → submit → approve → publish" })) };
  },
  autonomous_optimization: (tid, i) => { const o = optimize(tid, i || {}); return { applied: [], proposed: o.proposals, note: "autonomous mode proposes; the governance engine decides. Call govern(apply_optimization) to commit a proposal." }; }
};
function intel(tenantId, key, input) {
  const k = S(key); const fn = INTEL[k];
  if (!fn) return { error: "Unknown intelligence: " + k, available: Object.keys(INTEL) };
  meter(tenantId, "goip.intelligence", 1);
  return fn(tenantId, input || {});
}

/* ═══════════════ 39 · GOVERNANCE ENGINE (policy · approval · certification · lifecycle · version · legal) ═══════════════ */
const GOV_ACTIONS = {
  submit: "submitted", approve: "approved", reject: "rejected", certify: "certified",
  publish: "published", suspend: "suspended", retire: "retired", reopen: "draft"
};
function govern(tenantId, input) {
  const i = input || {}; const Db = db(); const action = S(i.action);
  const row = Db.get("SELECT * FROM offers WHERE id=? AND (tenant_id=? OR tenant_id=0)", Number(i.id), tenantId);
  if (!row) return { error: "Unknown value exchange", code: 404 };
  const gov = Object.assign({ state: "draft", version: Number(row.version) || 1, jurisdictions: [], terms: "", approvals: [] }, J(row.governance, {}));
  const from = S(gov.state);
  if (action === "version") {
    const clone = Object.assign({}, exchange(tenantId, row.id));
    const body = Object.assign({}, clone, { name: clone.name, code: "", version: Number(row.version || 1) + 1, parent_id: row.id, status: "draft",
      governance: { state: "draft", version: Number(row.version || 1) + 1, jurisdictions: gov.jurisdictions, terms: gov.terms, approvals: [], code_pending: S(row.code || ""), supersedes: row.id } });
    delete body.id; delete body.uid; delete body.created_at;
    const made = createExchange(tenantId, body, { platform: !!i.platform });
    meter(tenantId, "goip.govern", 1);
    return Object.assign({ ok: true, action, from_id: row.id }, made);
  }
  if (action === "restrict") { gov.jurisdictions = arr(i.jurisdictions).map(S); }
  else if (action === "terms") { gov.terms = S(i.terms); }
  else if (action === "attest") { gov.attestations = arr(gov.attestations).concat([{ by: S(i.actor || "platform"), at: nowIso(), note: S(i.note || "") }]); }
  else if (action === "apply_optimization") {
    const patch = i.change || {}; const allowed = ["value", "max_discount", "usage_limit", "per_owner_limit", "min_amount", "code", "priority", "ends"];
    const K = Object.keys(patch).filter(k => allowed.includes(k)); if (!K.length) return { error: "No applicable change" };
    Db.run(`UPDATE offers SET ${K.map(k => k + "=?").join(",")} WHERE id=?`, ...K.map(k => patch[k]), row.id);
    gov.optimizations = arr(gov.optimizations).concat([{ at: nowIso(), change: patch, why: S(i.why || "") }]);
  }
  else if (GOV_ACTIONS[action]) {
    const to = GOV_ACTIONS[action];
    const allowed = arr((REG("goipGovernanceTransitions") || GOVERNANCE_TRANSITIONS)[from] || GOVERNANCE_TRANSITIONS[from] || []);
    if (!allowed.includes(to)) return { error: "Illegal transition " + from + " → " + to, allowed, code: 409 };
    gov.state = to;
    gov.approvals = arr(gov.approvals).concat([{ from, to, by: S(i.actor || "platform"), at: nowIso(), note: S(i.note || "") }]);
    if (to === "published") {
      Db.run("UPDATE offers SET status='active' WHERE id=?", row.id);
      /* supersession: a published version takes the public code from the version it replaces, and retires it */
      const prevId = Number(gov.supersedes || row.parent_id || 0);
      if (prevId) {
        const prev = Db.get("SELECT * FROM offers WHERE id=?", prevId);
        if (prev) {
          const pg = Object.assign(J(prev.governance, {}), { state: "retired", superseded_by: row.id, retired_at: nowIso() });
          Db.run("UPDATE offers SET code='', status='inactive', governance=? WHERE id=?", JSON.stringify(pg), prev.id);
          if (gov.code_pending) { Db.run("UPDATE offers SET code=? WHERE id=?", S(gov.code_pending), row.id); delete gov.code_pending; }
        }
      }
    }
    if (to === "suspended" || to === "retired") Db.run("UPDATE offers SET status='inactive' WHERE id=?", row.id);
  } else return { error: "Unknown governance action: " + action, actions: Object.keys(GOV_ACTIONS).concat(["version", "restrict", "terms", "attest", "apply_optimization"]) };
  Db.run("UPDATE offers SET governance=? WHERE id=?", JSON.stringify(gov), row.id);
  const uid = uidOf("offers", row.id);
  if (uid) edge(tenantId, "GOVERNED_BY", "offer", uid, "policy", S(i.actor || "platform"), { action, state: gov.state });
  meter(tenantId, "goip.govern", 1);
  if (action === "publish") { meter(tenantId, "goip.publish", 1); try { require("./events.js").emit(row.tenant_id, "offer.created", { id: row.id, name: row.name, published: true }, { uid }); } catch (e) { } }
  return { ok: true, action, state: gov.state, governance: gov };
}
function auditTrail(tenantId, id) {
  const Db = db(); const row = id ? Db.get("SELECT * FROM offers WHERE id=?", Number(id)) : null;
  const uid = row ? row.uid : null;
  const entries = id
    ? Db.all("SELECT * FROM audit_log WHERE (entity='offer' AND entity_id=?) OR entity_id=? ORDER BY id DESC LIMIT 200", String(id), String(uid || ""))
    : Db.all("SELECT * FROM audit_log WHERE tenant_id=? AND (entity IN ('offer','coupon','goip')) ORDER BY id DESC LIMIT 200", tenantId);
  let chain = null; try { chain = db().auditChainVerify(tenantId); } catch (e) { chain = { ok: null, note: "chain verification unavailable" }; }
  const redemptions = id ? Db.all("SELECT id,code,owner,amount,credits,status,created_at,settlement_id FROM coupon_redemptions WHERE offer_id=? ORDER BY id DESC LIMIT 100", Number(id)) : [];
  return { exchange: row ? { id: row.id, uid: row.uid, name: row.name, governance: J(row.governance, {}) } : null, entries, redemptions, chain, graph: uid ? graph(tenantId, uid, 1) : null };
}

/* ═══════════════ 40 · DISCOVERY · SEARCH · COMPARE · VALIDATE ═══════════════ */
function discover(tenantId, input) {
  const i = input || {}; const rctx = resolveContext(Object.assign({ tenantId }, i));
  const pool = offersMod().eligible(tenantId, S(i.channel || "commerce"), i.coupon || "*", rctx.governance.global_allowed);
  const items = [];
  for (const c of pool) {
    const el = eligibility(c, rctx); if (!el.ok) continue;
    const row = c._row || {};
    if (i.distribution && arr(J(row.distribution, [])).length && !arr(J(row.distribution, [])).includes(S(i.distribution))) continue;
    items.push({ id: c.id, uid: row.uid, name: c.name, code: c.code, benefit: S(row.benefit || c.type), type: c.type, direction: c.direction, value: c.value, domain: S(row.domain || "incentive"), unit: unitOf(c), summary: S(row.summary || ""), est_value: r2(benefitWeight(c, rctx.economic.amount)), funder: c.funder, campaign: S(row.campaign || "") });
  }
  items.sort((a, b) => b.est_value - a.est_value);
  meter(tenantId, "goip.decision", 1);
  return { context: { reality: rctx.reality, calendar: rctx.temporal.calendar, place: rctx.spatial.node, unit: rctx.economic.unit, segments: rctx.audience.segments }, count: items.length, items };
}
function search(tenantId, input) {
  const i = input || {};
  const rows = listExchanges(tenantId, { q: i.q, domain: i.domain, benefit: i.benefit, channel: i.channel, status: i.status, campaign: i.campaign, limit: i.limit });
  meter(tenantId, "goip.decision", 1);
  return { count: rows.length, items: rows.map(r => ({ id: r.id, uid: r.uid, name: r.name, code: r.code, domain: r.domain, benefit: r.benefit, type: r.type, value: r.value, unit: S(r.economic_unit || r.currency), status: r.status, state: (r.governance || {}).state, campaign: r.campaign })) };
}
function compare(tenantId, input) {
  const i = input || {}; const rctx = resolveContext(Object.assign({ tenantId }, i));
  const ids = arr(i.ids).map(Number).filter(Boolean);
  const pool = offersMod().eligible(tenantId, S(i.channel || "commerce"), i.coupon || "*", true).filter(c => !ids.length || ids.includes(c.id));
  const items = pool.map(c => {
    const el = eligibility(c, rctx);
    const H = offersMod().HANDLERS[c.type];
    let benefit = {}; try { benefit = H ? (H(c, rctx.cart.items.length ? rctx.cart.items : [{ id: "__base", price: rctx.economic.amount, qty: 1, dept: "", brand: "" }], rctx.economic.amount) || {}) : {}; } catch (e) { }
    return {
      id: c.id, name: c.name, benefit_key: S((c._row || {}).benefit || c.type), eligible: el.ok, reasons: el.reasons,
      discount: r2(benefit.discount || 0), credits: r2(benefit.credits || 0), free_shipping: !!benefit.freeShip, grant: benefit.grant || null,
      unit: S(benefit.unit || unitOf(c)), funder: c.funder, net: r2(Math.max(0, rctx.economic.amount - (benefit.discount || 0)))
    };
  }).sort((a, b) => (b.eligible - a.eligible) || (b.discount + b.credits) - (a.discount + a.credits));
  meter(tenantId, "goip.decision", 1);
  return { amount: rctx.economic.amount, unit: rctx.economic.unit, best: items.find(x => x.eligible) || null, items };
}
function validate(tenantId, input) {
  const i = input || {}; const rctx = resolveContext(Object.assign({ tenantId }, i));
  const out = { context: rctx, code: S(i.coupon || "").toUpperCase() || null, ok: true, checks: [] };
  if (out.code) {
    const v = offersMod().validateCoupon(tenantId, out.code, i.owner || "");
    out.checks.push({ check: "code", ok: !!v.ok, detail: v.reason || "accepted" });
    if (!v.ok) out.ok = false;
  }
  const pool = offersMod().eligible(tenantId, S(i.channel || "commerce"), i.coupon || "*", true);
  const target = i.id ? pool.filter(c => c.id === Number(i.id)) : pool.filter(c => !out.code || S(c.code).toUpperCase() === out.code);
  for (const c of target) {
    const el = eligibility(c, rctx);
    out.checks.push({ check: "eligibility:" + c.name, ok: el.ok, detail: el.ok ? "all constitutional gates passed" : el.reasons.join("; ") });
    if (!el.ok) out.ok = false;
  }
  if (!target.length && out.code) { out.ok = false; out.checks.push({ check: "exists", ok: false, detail: "no value exchange carries this code in this context" }); }
  meter(tenantId, "goip.decision", 1);
  return out;
}

/* ═══════════════ 40b · DISTRIBUTION FEEDS + EMBEDDABLE COMPONENT (public, published-only) ═══════════════ */
function feed(tenantId, channelKey, input) {
  const i = input || {}; const ch = arr(REG("goipDistribution")).find(c => c.key === S(channelKey));
  if (!ch) return { error: "Unknown distribution channel: " + channelKey, channels: arr(REG("goipDistribution")).map(c => c.key), code: 404 };
  const rctx = resolveContext(Object.assign({ tenantId }, i));
  const items = discover(tenantId, Object.assign({}, i, { distribution: ch.key })).items
    .filter(x => { const row = db().get("SELECT distribution, governance FROM offers WHERE id=?", x.id); if (!row) return true;
      const dist = J(row.distribution, []); const st = S(J(row.governance, {}).state || "published");
      return (!dist.length || dist.includes(ch.key)) && ["published", "certified", "approved"].includes(st); })
    .map(x => ({ id: x.id, uid: x.uid, title: x.name, code: x.code || null, benefit: x.benefit, value: x.value, unit: x.unit, summary: x.summary, campaign: x.campaign || null }));
  return { channel: ch.key, name: ch.name, store: rctx.organization.slug, place: rctx.spatial.node, unit: rctx.economic.unit, count: items.length, items };
}
function widget(tenantId, input) {
  /* `channel` is the value-exchange channel (commerce/subscription/ai); the distribution channel a
     widget renders is its own axis — never conflate the two. */
  const i = Object.assign({}, input || {});
  const dist = S(i.distribution || i.channel_key || "widget"); delete i.channel_key;
  i.distribution = dist; i.channel = S(i.channel || "commerce");
  const d = feed(tenantId, dist, i);
  if (d.error) return d;
  const esc = t => S(t).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const html = `<div class="goip-widget" style="font:14px/1.5 system-ui,sans-serif;display:grid;gap:8px">
${d.items.slice(0, 10).map(i => `  <div style="border:1px solid #e5e7eb;border-radius:10px;padding:10px 12px">
    <b>${esc(i.title)}</b>${i.code ? ` · <code>${esc(i.code)}</code>` : ""}
    <div style="opacity:.7;font-size:12px">${esc(i.benefit)} · ${esc(i.value)} ${esc(i.unit)}${i.summary ? " — " + esc(i.summary) : ""}</div>
  </div>`).join("\n") || '  <div style="opacity:.6">No value exchanges available right now.</div>'}
</div>`;
  return { channel: d.channel, count: d.count, items: d.items, html };
}

/* ═══════════════ 41 · THE CAPABILITY ROUTER — the ONLY entry point consumers need ═══════════════ */
const IMPL = {
  create: (tid, i, o) => createExchange(tid, i, o),
  clone: (tid, i, o) => {
    const src = exchange(tid, i.id); if (!src) return { error: "Unknown value exchange", code: 404 };
    const body = Object.assign({}, src, i.patch || {}, { name: S((i.patch && i.patch.name) || (src.name + " (copy)")), code: S((i.patch && i.patch.code) || ""), parent_id: src.id, governance: { state: "draft", version: 1, jurisdictions: (src.governance || {}).jurisdictions || [], terms: (src.governance || {}).terms || "", approvals: [] } });
    delete body.id; delete body.uid; delete body.created_at; delete body.used;
    return createExchange(tid, body, o);
  },
  publish: (tid, i, o) => govern(tid, { id: i.id, action: "publish", actor: o && o.actor, platform: o && o.platform }),
  discover: (tid, i) => discover(tid, i),
  search: (tid, i) => search(tid, i),
  compare: (tid, i) => compare(tid, i),
  validate: (tid, i) => validate(tid, i),
  reserve: (tid, i) => reserve(tid, i),
  activate: (tid, i) => activate(tid, i),
  issue: (tid, i) => issue(tid, i),
  track: (tid, i) => track(tid, i),
  attribute: (tid, i) => attribute(tid, i),
  apply: (tid, i) => { const r = decide(Object.assign({ tenantId: tid }, i)); meter(tid, "goip.decision", 1); return r; },
  redeem: (tid, i) => {
    const ctx = Object.assign({ tenantId: tid }, i);
    const res = decide(ctx);
    if (!res.applied.length) return { ok: false, reason: "Nothing applicable in this context", rejected: res.rejected };
    if (i.reservation_ids) for (const rid of arr(i.reservation_ids)) { try { db().run("UPDATE coupon_redemptions SET status='voided' WHERE id=? AND tenant_id=? AND status='reserved'", Number(rid), tid); } catch (e) { } }
    offersMod().redeem(ctx, res, i.ref || { order_id: i.order_id, order_num: i.order_num, invoice_id: i.invoice_id });
    return { ok: true, discount: res.discount, credits: res.credits, freeShip: res.freeShip, applied: res.applied };
  },
  /* the settlement capability carries the whole settlement fabric: accrual (default), approval and
     reconciliation are stages of the same run, not separate capabilities. */
  settle: (tid, i, o) => {
    if (i.approve) return approveSettlement(Number(i.tenant_id) || tid, i.approve);
    if (i.reconcile) return reconcile(Number(i.tenant_id) || tid, { id: i.reconcile, external_ref: i.external_ref, note: i.note });
    if (i.all && o && o.platform) {
      const tenants = db().all("SELECT id, slug FROM tenants ORDER BY id");
      const runs = tenants.map(t => { const rel = releaseDeferred(t.id); const r = settle(t.id, i); return { tenant: t.slug, tenant_id: t.id, redemptions_settled: r.redemptions_settled, settlements: r.settlements, deferred_released: rel.released }; });
      return { ok: true, period: S(i.period || period()), scope: "all stores", runs, redemptions_settled: runs.reduce((n, r) => n + r.redemptions_settled, 0) };
    }
    const rel = releaseDeferred(tid); const r = settle(tid, i); return Object.assign(r, { deferred_released: rel.released });
  },
  fund: (tid, i) => fund(tid, i),
  pay: (tid, i) => pay(tid, i),
  optimize: (tid, i) => optimize(tid, i),
  forecast: (tid, i) => forecast(tid, i),
  simulate: (tid, i) => simulate(tid, i),
  govern: (tid, i, o) => govern(tid, Object.assign({}, i, { actor: (o && o.actor) || i.actor, platform: o && o.platform })),
  audit: (tid, i) => auditTrail(tid, i.id)
};
function capability(key) { return arr(REG("goipCapabilities")).find(c => c.key === S(key)) || null; }
function invoke(key, tenantId, input, opts) {
  const cap = capability(key);
  if (!cap) return { error: "Unknown capability: " + key, capabilities: arr(REG("goipCapabilities")).map(c => c.key), code: 404 };
  const fn = IMPL[cap.key];
  if (!fn) return { error: "Capability declared but not bound: " + cap.key, code: 501 };
  if (cap.scope === "platform" && !(opts && opts.platform)) return { error: "Capability '" + cap.key + "' is platform-scoped", code: 403 };
  const started = Date.now();
  const result = fn(Number(tenantId || 0), input || {}, opts || {});
  if (result && result.error) return Object.assign({ ok: false, capability: cap.key }, result);
  return { ok: true, capability: cap.key, stage: cap.stage, engine: cap.engine, ms: Date.now() - started, result };
}

/* ═══════════════ 42 · MANIFEST — the platform describing itself (Knowledge Domain) ═══════════════ */
function coverage() {
  const caps = arr(REG("goipCapabilities"));
  const bound = caps.filter(c => !!IMPL[c.key]).length;
  const engines = arr(REG("goipEngines"));
  const benefits = arr(REG("goipBenefits"));
  const H = offersMod().HANDLERS;
  const handled = benefits.filter(b => !!H[b.type]).length;
  const domains = arr(REG("goipDomains"));
  const discs = new Set(domains.map(d => d.owner + "|" + d.discriminator));
  return {
    capabilities: { declared: caps.length, bound, gap: caps.filter(c => !IMPL[c.key]).map(c => c.key) },
    engines: { declared: engines.length },
    benefits: { declared: benefits.length, handled, gap: benefits.filter(b => !H[b.type]).map(b => b.key) },
    domains: { declared: domains.length, distinct_owners: discs.size, overlapping: domains.length - discs.size },
    contexts: { declared: arr(REG("goipContexts")).length },
    fabrics: { distribution: arr(REG("goipDistribution")).length, attribution: arr(REG("goipAttribution")).length, funding: arr(REG("goipFunding")).length, settlement: arr(REG("goipSettlement")).length, intelligence: arr(REG("goipIntelligence")).length, governance: arr(REG("goipGovernance")).length },
    intelligence: { declared: arr(REG("goipIntelligence")).length, implemented: arr(REG("goipIntelligence")).filter(x => !!INTEL[x.key]).length },
    graph: { nodes: arr(REG("goipGraphNodes")).length, edges: arr(REG("goipGraphEdges")).length },
    temporal: { calendars: arr(REG("goipCalendars")).length, chronologies: arr(REG("goipChronologies")).length, units: arr(REG("goipTemporalUnits")).length },
    spatial: { systems: arr(REG("goipSpatialSystems")).length, coordinate_systems: arr(REG("goipCoordinateSystems")).length, nodes: arr(REG("goipSpatialNodes")).length },
    economic: { units: arr(REG("goipEconomicUnits")).length, classes: arr(REG("goipAssetClasses")).length },
    reality: { models: arr(REG("goipRealities")).length },
    experience: { surfaces: arr(REG("goipExperience")).length }, access: { protocols: arr(REG("goipAccess")).length },
    commercial: { deployments: arr(REG("goipDeployments")).length, billing_models: arr(REG("goipBillingModels")).length, meters: arr(REG("goipMeters")).length }
  };
}
function manifest(tenantId) {
  return {
    product: "GOIP Ω∞", title: "GLOBAL OFFER INFRASTRUCTURE PLATFORM",
    subtitle: "Universal Incentive · Offer · Reward · Value Exchange Operating System",
    version: "1.0", constitution: arr(REG("goipConstitution")),
    capabilities: arr(REG("goipCapabilities")), engines: arr(REG("goipEngines")), contexts: arr(REG("goipContexts")),
    domains: arr(REG("goipDomains")), benefits: arr(REG("goipBenefits")),
    temporal: { calendars: arr(REG("goipCalendars")), chronologies: arr(REG("goipChronologies")), units: arr(REG("goipTemporalUnits")), conversions: REG("goipTemporalConversions") },
    spatial: { systems: arr(REG("goipSpatialSystems")), coordinates: arr(REG("goipCoordinateSystems")), nodes: arr(REG("goipSpatialNodes")) },
    economic: { units: arr(REG("goipEconomicUnits")), classes: arr(REG("goipAssetClasses")) }, realities: arr(REG("goipRealities")),
    fabrics: { distribution: arr(REG("goipDistribution")), attribution: arr(REG("goipAttribution")), attribution_models: arr(REG("goipAttributionModels")), funding: arr(REG("goipFunding")), settlement: arr(REG("goipSettlement")), intelligence: arr(REG("goipIntelligence")), governance: arr(REG("goipGovernance")) },
    graph: { nodes: arr(REG("goipGraphNodes")), edges: arr(REG("goipGraphEdges")) },
    experience: arr(REG("goipExperience")), access: arr(REG("goipAccess")),
    commercialization: { deployments: arr(REG("goipDeployments")), billing_models: arr(REG("goipBillingModels")), meters: arr(REG("goipMeters")) },
    governance_states: GOVERNANCE_STATES, coverage: coverage(),
    entitled: tenantId ? hasGoip(tenantId) : null
  };
}

module.exports = {
  /* constitution + registries */
  CONSTITUTION, CAPABILITIES, ENGINES, CONTEXTS, DOMAINS, BENEFITS, DISTRIBUTION, ATTRIBUTION, FUNDING, SETTLEMENT,
  INTELLIGENCE, GOVERNANCE, GRAPH_NODES, GRAPH_EDGES, EXPERIENCE, ACCESS, DEPLOYMENTS, BILLING_MODELS, REGISTRIES,
  CALENDARS, SPATIAL_NODES, ECONOMIC_UNITS, REALITIES, GOVERNANCE_STATES, GOIP_HANDLERS,
  /* lifecycle */ seed, seedDemo, DEMO_EXCHANGES, registerHandlers, registerHooks, manifest, coverage,
  /* engines */ resolveContext, qualify, eligibility, decide, rank, resolveConflicts, personalize, fraudScore, riskScore, price, recommend,
  /* capabilities */ invoke, capability, createExchange, exchange, listExchanges, issue, reserve, releaseReservation, activate,
  discover, search, compare, validate, feed, widget, track, touchpoints, attribute, fund, budgets, budgetFor, treasury, burnRate,
  settle, settlements, approveSettlement, pay, reconcile, recover, optimize, forecast, simulate, govern, auditTrail, intel, INTEL,
  /* value */ grantEntitlement, entitlementsOf, consumeEntitlement, releaseDeferred, postRedeem, meter, graph, edge, uidOf,
  J, r2
};
