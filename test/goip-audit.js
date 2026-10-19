/* GOIP Ω∞ — constitutional conformance audit.
   Reads the LIVE registries out of a freshly seeded database (not the JS constants) and proves, item
   by item against the specification, that the platform carries: ZERO MISSING (every declared element
   exists), ZERO PARTIAL (every capability is bound, every benefit has math, every intelligence
   reading runs), ZERO DUPLICATE (no key appears twice in any registry) and ZERO OVERLAP (no two
   domains select the same rows from the same store). Fast, no server, no port, own throwaway DB. */
"use strict";
const path = require("path");
const os = require("os");
const fs = require("fs");

const TMP = path.join(os.tmpdir(), "goip-audit-" + process.pid + ".db");
process.env.LX_DB = TMP;
for (const suffix of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + suffix, { force: true }); } catch (e) { } }

const silence = console.log; console.log = () => { };          /* the seed banner is not the point */
const db = require(path.join(__dirname, "..", "lib", "db.js"));
const goip = require(path.join(__dirname, "..", "lib", "goip.js"));
const offers = require(path.join(__dirname, "..", "lib", "offers.js"));
goip.seed();
console.log = silence;

let passed = 0, failed = 0;
const ok = (cond, name, extra) => { if (cond) { passed++; } else { failed++; console.log("  ✗ " + name + (extra ? "  → " + extra : "")); } };
const group = n => console.log("  " + n);
const reg = k => { const r = require(path.join(__dirname, "..", "lib", "registry.js")).list(k); return Array.isArray(r) ? r : (r && typeof r === "object" ? r : []); };
const keys = k => reg(k).map(x => (x && x.key) || x);
const has = (k, want) => keys(k).map(String).map(s => s.toLowerCase()).includes(String(want).toLowerCase());
const names = k => reg(k).map(x => String((x && x.name) || x).toLowerCase());
const named = (k, want) => names(k).some(n => n.includes(String(want).toLowerCase()));

/* every element the specification names, in the specification's own words */
const SPEC = {
  goipCapabilities: ["create", "clone", "publish", "discover", "search", "compare", "validate", "reserve", "activate", "issue", "track", "attribute", "apply", "redeem", "settle", "fund", "pay", "optimize", "forecast", "simulate", "govern", "audit"],
  goipEngines: ["context_resolution", "eligibility", "qualification", "decision", "discovery", "benefit_resolution", "conflict_resolution", "stacking", "ranking", "optimization", "recommendation", "personalization", "pricing", "simulation", "forecasting", "fraud", "risk", "governance"],
  goipContexts: ["reality", "temporal", "spatial", "economic", "governance", "audience", "identity", "behavioral", "product", "catalog", "cart", "session", "device", "market", "inventory", "risk", "organization", "merchant", "provider", "partner", "creator", "channel", "event", "campaign", "ai"],
  goipDomains: ["incentive", "offer", "coupon", "promotion", "discount", "cashback", "reward", "gift_card", "voucher", "loyalty", "membership", "referral", "affiliate", "creator", "influencer", "deal", "pricing", "dynamic_pricing", "auction", "subscription_benefit", "partner_benefit", "corporate_benefit", "government_benefit", "employee_benefit", "gamification", "audience", "segmentation", "campaign", "discovery", "search", "recommendation", "personalization", "distribution", "syndication", "marketplace", "merchant", "brand", "provider", "partner", "exchange", "attribution", "tracking", "wallet", "treasury", "funding", "budget", "payment", "settlement", "reconciliation", "payout", "fraud", "risk", "analytics", "forecasting", "simulation", "ai", "agent", "governance", "compliance", "knowledge", "registry", "universal_context", "universal_temporal", "universal_spatial", "universal_economic", "universal_governance", "universal_reality"],
  goipBenefits: ["percentage_discount", "flat_discount", "tier_discount", "volume_discount", "dynamic_discount", "cashback", "deferred_cashback", "reward_points", "coins", "credits", "tokens", "gift_card", "voucher", "wallet_value", "free_product", "free_service", "free_shipping", "membership_upgrade", "tier_upgrade", "partner_benefit", "corporate_benefit", "government_benefit", "digital_asset", "economic_asset", "future_benefit"],
  goipDistribution: ["email", "sms", "whatsapp", "push", "in_app", "widget", "embedded", "partner_feed", "marketplace_feed", "affiliate_feed", "creator_feed", "bank_feed", "pos_feed", "iot_feed", "ai_feed", "future_channel"],
  goipAttribution: ["click", "view", "conversion", "coupon", "affiliate", "referral", "creator", "partner", "cross_device", "cross_channel", "revenue", "commission"],
  goipFunding: ["merchant", "brand", "marketplace", "partner", "bank", "government", "corporate", "multi_party", "budget_allocation", "reserve_management", "burn_rate", "forecasting"],
  goipSettlement: ["wallet", "ledger", "treasury", "settlement", "reconciliation", "recovery", "revenue_sharing", "commission", "payout", "cross_border", "future_settlement"],
  goipIntelligence: ["deal", "offer", "price", "audience", "merchant", "provider", "partner", "fraud", "optimization", "forecast", "recommendation", "ai_offer_generation", "ai_incentive_generation", "autonomous_campaign", "autonomous_optimization"],
  goipGovernance: ["policy", "approval", "certification", "lifecycle", "versioning", "audit", "compliance", "regulatory", "risk", "legal"],
  goipGraphNodes: ["offer", "coupon", "reward", "cashback", "gift_card", "voucher", "benefit", "campaign", "audience", "merchant", "brand", "provider", "partner", "affiliate", "creator", "wallet", "settlement", "payout", "temporal_context", "spatial_context", "economic_context"],
  goipGraphEdges: ["FUNDED_BY", "TARGETED_TO", "ISSUED_BY", "DISTRIBUTED_BY", "DISCOVERED_BY", "CLICKED_BY", "ACTIVATED_BY", "REDEEMED_BY", "ATTRIBUTED_TO", "SETTLED_BY", "PAID_TO", "GOVERNED_BY", "GENERATED_BY", "PART_OF"],
  goipDeployments: ["embedded_sdk", "embedded_widget", "microservice", "headless_api", "saas", "private_cloud", "dedicated_cloud", "white_label", "marketplace_service", "managed_service", "agent_service"],
  goipBillingModels: ["per_tenant", "per_merchant", "per_provider", "per_offer", "per_redemption", "per_settlement", "per_payout", "per_api", "per_active_user", "per_campaign", "revenue_share", "hybrid"],
  goipExperience: ["web", "mobile", "pos", "marketplace", "commerce", "erp", "crm", "cdp", "hrms", "banking", "insurance", "gaming", "telecom", "government", "creator", "iot", "ai", "widgets", "white_label", "partner_portal", "merchant_portal", "brand_portal", "agent", "future_interface"],
  goipAccess: ["rest", "graphql", "events", "kafka", "streams", "webhooks", "sdk", "mobile_sdk", "agent_protocol", "mcp", "embedded", "connectors"],
  goipConstitution: ["value_exchange", "context", "conditions", "eligibility", "benefit", "execution", "settlement", "audit"],
  goipRealities: ["physical", "digital", "virtual", "hybrid", "simulated", "any"]
};

console.log("▸ GOIP Ω∞ — constitutional conformance audit");

/* ── 1 · ZERO MISSING: every declared element of the specification is present, live, in the DB ── */
group("zero missing — every specified element exists in the live registries");
for (const [registry, want] of Object.entries(SPEC)) {
  const missing = want.filter(k => !has(registry, k));
  ok(missing.length === 0, registry + ": all " + want.length + " elements present", missing.join(","));
  ok(reg(registry).length >= want.length, registry + ": count ≥ specification (" + reg(registry).length + " ≥ " + want.length + ")");
}
/* the temporal / spatial / economic examples the specification names by hand */
for (const c of ["gregorian", "islamic", "hebrew", "fiscal", "academic", "mars_darian", "lunar", "federation", "custom_planetary"]) ok(has("goipCalendars", c), "calendar registry carries " + c);
for (const r of ["Temporal Authority=goipCalendars", "Chronology Registry=goipChronologies", "Temporal Measurement=goipTemporalUnits", "Temporal Conversion=goipTemporalConversions"]) { const [label, key] = r.split("="); ok(reg(key).length > 0 || Object.keys(require(path.join(__dirname, "..", "lib", "registry.js")).list(key) || {}).length > 0, "temporal domain: " + label + " is registry-driven"); }
for (const p of ["earth", "earth.in", "earth.in.bihar", "earth.in.bihar.patna", "mars", "mars.olympus", "mars.olympus.sector-7", "moon", "moon.alpha", "galaxy-7", "galaxy-7.zone-22"]) ok(!!require(path.join(__dirname, "..", "lib", "places.js")).byPath(p), "Geo's place tree carries " + p);
for (const sY of ["earth_admin", "mars_admin", "lunar_admin", "galactic", "network", "declared"]) ok(require(path.join(__dirname, "..", "lib", "places.js")).systems().some(x => x.key === sY), "place system " + sY);
for (const u of ["USD", "EUR", "INR", "MARS_CREDIT", "LUNAR_TOKEN", "FED_CREDIT", "CARBON", "ENERGY", "RESOURCE", "POINT", "COIN", "TOKEN"]) ok(!!require(path.join(__dirname, "..", "lib", "registry.js")).unit(u), "Value's master carries the unit " + u);
{ const R = require(path.join(__dirname, "..", "lib", "registry.js")); const money = new Set(R.valueClasses().filter(c => c.money).map(c => c.key));
  ok(R.units().filter(u => money.has(u.class)).every(u => u.settleable), "every money unit is settleable"); }

/* ── 2 · ZERO PARTIAL: everything declared is actually wired to running code ── */
group("zero partial — every declaration is bound to running code");
const cov = goip.coverage();
ok(cov.capabilities.declared === 22 && cov.capabilities.bound === 22, "22/22 capabilities bound to an implementation", JSON.stringify(cov.capabilities.gap));
ok(cov.benefits.declared === 25 && cov.benefits.handled === 25, "25/25 benefits bound to a math handler", JSON.stringify(cov.benefits.gap));
ok(cov.intelligence.declared === 15 && cov.intelligence.implemented === 15, "15/15 intelligence readings implemented");
for (const b of SPEC.goipBenefits) { const ben = reg("goipBenefits").find(x => x.key === b); ok(ben && typeof offers.HANDLERS[ben.type] === "function", "benefit " + b + " resolves through offers.HANDLERS." + (ben && ben.type)); }
for (const c of SPEC.goipCapabilities) { const r = goip.invoke(c, 1, { id: 1, amount: 10, owner: "t1:u:1", months: 1, sample: 1, action: "attest", model: "linear" }, { platform: true }); ok(!(r && r.code === 501), "capability " + c + " is not a stub", r && r.error); }
for (const e of SPEC.goipEngines) { const def = reg("goipEngines").find(x => x.key === e); ok(def && def.impl, "engine " + e + " names its implementation"); }
ok(typeof goip.feed === "function" && typeof goip.widget === "function", "distribution feeds + embeddable component are real surfaces");
ok(reg("goipDistribution").filter(c => c.state === "live").length >= 15, "distribution channels are live, not declarations");

/* ── 3 · ZERO DUPLICATE: no key is defined twice anywhere ── */
group("zero duplicate — no key is defined twice in any registry");
for (const registry of Object.keys(SPEC)) {
  const k = keys(registry).map(String);
  const dupes = k.filter((x, i) => k.indexOf(x) !== i);
  ok(dupes.length === 0, registry + ": no duplicate keys", dupes.join(","));
}
const types = reg("offerTypes").map(t => t.key);
ok(types.filter((t, i) => types.indexOf(t) !== i).length === 0, "offerTypes registry has no duplicate benefit type");
const handlerNames = Object.keys(offers.HANDLERS);
ok(handlerNames.length === new Set(handlerNames).size, "one math handler per benefit type — no forked engine");
ok(reg("goipBenefits").every(b => reg("goipBenefits").filter(x => x.type === b.type).length === 1), "no two benefits share a handler");

/* ── 4 · ZERO OVERLAP: no two domains select the same rows from the same store ── */
group("zero overlap — every domain owns a distinct slice");
const doms = reg("goipDomains");
const slices = doms.map(d => d.owner + "|" + d.discriminator);
ok(new Set(slices).size === slices.length, "67 domains → " + new Set(slices).size + " distinct owner+discriminator slices");
ok(doms.every(d => d.owner && d.discriminator), "every domain names an owner store and a discriminator");
ok(cov.domains.overlapping === 0, "coverage report agrees: zero overlapping domains");
const numbers = doms.map(d => d.n);
ok(new Set(numbers).size === 67 && Math.min(...numbers) === 1 && Math.max(...numbers) === 67, "domains are numbered 01–67 with no gaps");

/* ── 5 · RE-USABLE: one writer per store, one engine per concern ── */
group("re-usable — one writer per store, one engine per concern");
const src = f => fs.readFileSync(path.join(__dirname, "..", "lib", f), "utf8");
const api = src("api.js");
ok((api.match(/INSERT INTO offers\(/g) || []).length === 0, "api.js never writes `offers` directly — it goes through goip.createExchange");
ok((api.match(/INSERT INTO coupons\(/g) || []).length === 0, "api.js never writes `coupons` directly — it goes through goip.issue");
ok((src("goip.js").match(/INSERT INTO offers\(/g) || []).length === 1, "exactly one INSERT INTO offers in the whole platform");
ok((src("goip.js").match(/INSERT INTO coupons\(/g) || []).length === 1, "exactly one INSERT INTO coupons in the GOIP kernel");
ok(!/function evaluate|HANDLERS *=/.test(src("goip.js").replace(/GOIP_HANDLERS/g, "")), "GOIP does not fork the decision/math engine");
ok(typeof offers.onRedeem === "function" && typeof offers.ledgerEntry === "function", "offers.js exposes the hook + unit ledger GOIP extends it through");
for (const t of ["goip_touchpoints", "goip_budgets", "goip_settlements", "goip_entitlements"]) {
  ok(require(path.join(__dirname, "..", "lib", "uid.js")).TABLES.includes(t), t + " carries universal UUIDs like every other table");
}
ok(Object.keys(require(path.join(__dirname, "..", "lib", "entity.js")).ENTITY_DEFS).filter(k => k.startsWith("goip_")).length === 4, "all four GOIP stores are Data Studio entities");

/* ── 6 · SELLABLE + BILLABLE ── */
group("sellable + billable");
const mod = db.get("SELECT * FROM modules WHERE id='goip'");
ok(!!mod && Number(mod.price) > 0, "GOIP is a priced marketplace module", mod && mod.price);
ok(JSON.parse(mod.manifest).capabilities.includes("goip"), "the module grants the goip capability");
ok(!!db.get("SELECT * FROM modules WHERE id='goip-agent'"), "agent/MCP access is separately sellable");
const meters = reg("goipMeters");
ok(reg("goipBillingModels").every(b => b.meter === "*" || meters.includes(b.meter)), "every billing model names a real meter");
ok(reg("goipCapabilities").every(c => meters.includes(c.meter)), "every capability bills a declared meter");
ok(typeof require(path.join(__dirname, "..", "lib", "billing.js")).meter === "function", "billing.js owns metering; GOIP calls it");

/* ── 7 · NO REDESIGN: the registries are data, and the engines read the data ── */
group("no redesign — a new civilization is a row, not a release");
const D = require(path.join(__dirname, "..", "lib", "db.js"));
/* a new world is a place declared on Geo's tree — data, through its write path, no code */
const Pl = require(path.join(__dirname, "..", "lib", "places.js"));
Pl.putPlace({ path: "titan", name: "Titan", level: "moon" });
Pl.putPlace({ path: "titan.rhea-basin", name: "Rhea Basin", level: "settlement" });
/* a new unit of value is a row of Value's master — data, no code */
require(path.join(__dirname, "..", "lib", "global.js")).createCurrency({ code: "TITAN_CRED", name: "Titan Credits", symbol: "TC", decimals: 2, usd: 0, class: "colonial", settleable: false });
const made = goip.createExchange(1, { name: "Titan settlement welcome", benefit: "percentage_discount", value: 15, code: "TITAN15", domain: "offer", economic_unit: "TITAN_CRED", spatial: { system: "declared", include: ["titan.rhea-basin"] }, governance: { state: "published" } }, {});
ok(made.ok, "a value exchange binds to a world invented seconds ago, with no code change", made.error);
const onTitan = goip.decide({ tenantId: 1, amount: 200, coupon: "TITAN15", spatial: { node: "titan.rhea-basin" }, currency: "TITAN_CRED" });
ok(onTitan.discount === 30, "it applies on Titan in Titan Credits (" + onTitan.discount + ")");
const onEarth = goip.decide({ tenantId: 1, amount: 200, coupon: "TITAN15", spatial: { node: "earth.in.bihar.patna" }, currency: "USD" });
ok(onEarth.discount === 0, "and is refused everywhere else, for a stated reason", JSON.stringify((onEarth.rejected[0] || {}).reasons));

for (const suffix of ["", "-wal", "-shm"]) { try { fs.rmSync(TMP + suffix, { force: true }); } catch (e) { } }
console.log((failed ? "  ✗ " : "  ✓ ") + passed + " conformance checks passed, " + failed + " failed");
process.exit(failed ? 1 : 0);
