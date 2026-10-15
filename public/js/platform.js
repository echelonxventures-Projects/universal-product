/* LUXORA Platform - super-admin console: tenants, plans, billing, providers, monitoring, audit */
"use strict";

const $ = s => document.querySelector(s);
const $$ = s => Array.from(document.querySelectorAll(s));
function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }
function __csrf() { const m = /(?:^|; )azc=([^;]+)/.exec(document.cookie || ""); return m ? m[1] : ""; }
async function api(path, method = "GET", body) {
  let url = "/api" + path;
  const opt = { method, headers: { "Content-Type": "application/json", "x-csrf": __csrf() }, credentials: "same-origin" };
  if (method === "GET" && body) {
    const params = new URLSearchParams(body);
    url += "?" + params.toString();
  } else if (body) {
    opt.body = JSON.stringify(body);
  }
  const r = await fetch(url, opt);
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.error || ("HTTP " + r.status));
  return data;
}

function linkify(m) {
  return esc(m).replace(/\/(platform|admin)\.html(\?store=[A-Za-z0-9-]+)?/g, function (s) {
    return '<a href="' + s + '" style="text-decoration:underline">' + (s.indexOf("platform") >= 0 ? "Platform console" : "Store console") + " →</a>";
  });
}
function money(n) { return "$" + (+n).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
let toastT;
function toast(msg, type = "info") {
  /* re-query after the fallback create: render() may have replaced the shell, leaving
     the earlier lookup stale — appending to a detached node silently swallows the toast
     (and, in newer engines, throws). */
  let container = document.getElementById("toastContainer");
  if (!container) { container = document.createElement("div"); container.id = "toastContainer"; document.body.appendChild(container); }
  const toastEl = document.createElement("div");
  toastEl.className = "toast " + (type === "error" ? "error" : "success");
  toastEl.textContent = msg;
  container.appendChild(toastEl);
  setTimeout(() => toastEl.remove(), 3000);
  let t = $("#ptoast");
  if (!t) { t = document.createElement("div"); t.id = "ptoast"; t.className = "p-toast"; document.body.appendChild(t); }
  t.innerHTML = `<div class="toast $type"><span>✅</span> </div>`; t.classList.add("show");
  clearTimeout(toastT); toastT = setTimeout(() => t.classList.remove("show"), 3200);
}
/* Grouped by function (Stores, Constitution, Identity…) so a platform operator
   navigates by domain, not by a 30-item flat list. Keys are unchanged; NAVFLAT
   drives the title lookup. */
/* ╔════════════════════════════════════════════════════════════════════╗
   ║  UCOS Ω∞ — THE SINGLE CANONICAL NAVIGATION MODEL                     ║
   ╚════════════════════════════════════════════════════════════════════╝
   The constitution declares one canonical home for every capability. This tree IS
   that declaration, rendered as navigation: 12 sections → capability groups → leaves.
   Order is the constitutional flow — existence first (Foundation), then knowledge,
   then the business of commerce, then the architecture that governs it all.

   ZERO-GAP RESOLUTION. Every leaf carries a resolver, so navigation can never dead-end:
     v:<key>    → a dedicated console view
     e:<entity> → the generic cross-entity dataset reader (any of ~3000 entities)
     u:<uv>     → a universe registry record (any of 2831 instantiated universes)
   The menu is not a hand-maintained list that can drift from the platform — a leaf with
   no dedicated view resolves through the same metadata-driven readers the Data Studio
   uses, so nothing is orphaned and nothing is duplicated. */
const NAV = [
  { n: "01 · Foundation", g: [
    { g: "Identity", l: [
      ["identity", "🔐 Identity · Auth", { v: "identity" }],
      ["identity-templates", "📋 Identity Templates", { v: "identity-templates" }],
      ["persons", "👥 Persons", { u: "person" }],
      ["organizations", "🏢 Organizations", { u: "organization" }],
      ["tenants", "🏬 Tenants", { e: "tenant" }],
      ["users", "👤 Users", { v: "users" }],
      ["roles", "🎭 Roles", { v: "roles" }],
      ["permissions", "🔑 Permissions", { u: "permission" }],
      ["credentials", "🧷 Credentials", { u: "credential_chain" }],
      ["authentication", "🔓 Authentication", { u: "authentication" }],
      ["authorization", "🛂 Authorization", { u: "authorization" }],
      ["trust", "🤝 Trust", { u: "trust" }],
      ["verification", "✔️ Verification", { u: "verification_management" }],
      ["kyc", "📄 KYC", { e: "kyc_profile" }],
      ["kyb", "🏛️ KYB", { u: "kyb" }],
      ["identity-graph", "🕸️ Identity Graph", { u: "identity_universe" }],
    ] },
    { g: "Geography", l: [
      ["countries", "🗺️ Countries", { e: "country" }],
      ["states", "🏞️ States · Regions", { u: "region" }],
      ["cities", "🏙️ Cities", { u: "city" }],
      ["jurisdictions", "⚖️ Jurisdictions", { u: "jurisdiction" }],
      ["addresses", "📍 Addresses", { e: "address" }],
      ["geo", "🌍 Geo Registry · Taxes", { v: "geo" }],
      ["geography", "🌐 Geography Universe", { u: "geography" }],
    ] },
    { g: "Temporal", l: [
      ["calendars", "📅 Calendars", { u: "calendars" }],
      ["schedules", "⏱️ Schedules", { u: "schedules" }],
      ["recurrence", "🔁 Recurrence", { e: "recurring_cycle" }],
      ["appointments", "🗓️ Appointments", { u: "appointment" }],
      ["reservations", "🪑 Reservations", { u: "booking" }],
      ["time-windows", "🪟 Time Windows", { u: "time_window" }],
      ["delivery-slots", "🚚 Delivery Slots", { e: "delivery_slot" }],
      ["availability", "🟢 Availability", { u: "availability" }],
      ["sla", "🛡️ SLA", { u: "sla" }],
      ["temporal", "⏳ Temporal Universe", { u: "temporal" }],
    ] },
    { g: "Currency", l: [
      ["currencies", "💰 Currencies", { e: "currency" }],
      ["fx", "📈 Exchange Rates", { v: "geo" }],
      ["currency-universe", "🪙 Currency Universe", { u: "currency_universe" }],
    ] },
    { g: "Localization", l: [
      ["languages", "🗣️ Languages", { u: "language" }],
      ["localization", "🌐 Localization", { e: "localization" }],
      ["translation", "🔤 Translation Registry", { u: "translation" }],
      ["cultural", "🌍 Cultural Context", { u: "cultural" }],
    ] },
  ] },
  { n: "02 · Knowledge", g: [
    { g: "Products", l: [
      ["gproducts", "🌐 Global Products", { v: "gproducts" }],
      ["product-families", "👨‍👩‍👧 Product Families", { u: "product_family" }],
      ["product-types", "📦 Product Types", { u: "product_type" }],
      ["variants", "🧬 Variants", { u: "product_variants" }],
      ["attributes", "🧩 Attributes", { e: "attribute" }],
      ["specifications", "📐 Specifications", { u: "specification" }],
      ["bundles", "🧺 Bundles · Kits", { u: "bundle_offer" }],
      ["collections", "📚 Collections", { u: "collection" }],
      ["product-graph", "🕸️ Product Graph", { u: "product_ontology" }],
      ["product-registry", "🗄️ Product Registry", { u: "global_product_registry_universe" }],
    ] },
    { g: "Services", l: [
      ["global-services", "🌐 Global Services", { u: "service" }],
      ["service-types", "🛠️ Service Types", { u: "service_type" }],
      ["service-plans", "📜 Service Plans", { u: "subscription" }],
      ["entitlements", "✅ Entitlements", { u: "entitlement" }],
      ["service-registry", "🗄️ Service Registry", { u: "global_service_registry_universe" }],
    ] },
    { g: "Catalog & Taxonomy", l: [
      ["gcatalog", "📦 Catalog · SKUs", { v: "gcatalog" }],
      ["taxonomy", "🗂️ Industry · Categories", { v: "taxonomy" }],
      ["categories", "🏷️ Category Tree", { u: "navigational_category_hierarchy" }],
      ["taxonomy-universe", "🌳 Taxonomy Universe", { u: "universal_taxonomy_universe" }],
    ] },
    { g: "Provenance", l: [
      ["brands", "🏷️ Brands · Manufacturers", { v: "brands" }],
      ["suppliers", "🚚 Suppliers", { e: "supplier" }],
      ["vendors", "🤝 Vendors", { u: "vendor" }],
      ["manufacturers", "🏭 Manufacturers", { e: "brand" }],
      ["assets", "🧱 Assets", { u: "asset" }],
      ["documents", "📄 Documents", { u: "document" }],
      ["media", "🎬 Media", { u: "media" }],
      ["content", "📝 Content", { e: "banner" }],
    ] },
    { g: "Knowledge Graph", l: [
      ["knowledge-graph", "🕸️ Knowledge Graph", { u: "knowledge_graph" }],
      ["ontology", "🧠 Ontology Registry", { u: "ontology" }],
      ["semantic", "🔗 Semantic Registry", { u: "semantic" }],
      ["canonical-registry", "🗄️ Canonical Knowledge Registry", { u: "universal_knowledge_graph" }],
    ] },
  ] },
  { n: "03 · Business", g: [
    { g: "Parties", l: [
      ["customers", "🧑‍🤝‍🧑 Customers", { e: "customer" }],
      ["sellers", "🏪 Sellers", { e: "seller" }],
      ["buyers", "🛍️ Buyers", { u: "buyer" }],
      ["partners", "🤝 Partners", { u: "partner" }],
      ["distributors", "🚚 Distributors", { u: "distributor" }],
      ["dealers", "🏪 Dealers", { u: "dealer" }],
      ["franchises", " franchises", { u: "franchise" }],
      ["workforce", "👷 Workforce", { u: "workforce" }],
    ] },
    { g: "CRM", l: [
      ["leads", "🎯 Leads", { u: "lead" }],
      ["opportunities", "💼 Opportunities", { u: "opportunity" }],
      ["accounts", "🗂️ Accounts", { u: "crm_account" }],
      ["contacts", "📇 Contacts", { u: "contact" }],
      ["activities", "📅 Activities", { u: "activity" }],
      ["pipelines", "🧩 Pipelines", { u: "pipeline" }],
    ] },
    { g: "Agreements", l: [
      ["contracts", "📜 Contracts", { e: "contract" }],
      ["agreements", "✍️ Agreements", { u: "agreement" }],
      ["relationships", " 🔗 Relationships", { u: "relationship" }],
      ["universal-links", "🔗 Universal Links (Primitive)", { e: "link" }],
      ["context-types", "🧭 Context Types (Primitive)", { e: "context_type" }],
      ["business-networks", "🌐 Business Networks", { u: "business_network" }],
      ["business-organizations", "🏢 Organizations", { u: "organization" }],
    ] },
  ] },
  { n: "04 · Commerce", g: [
    { g: "Merchandising", l: [
      ["catalogs", "📚 Catalogs", { u: "catalog" }],
      ["pricing", "💲 Pricing", { u: "pricing" }],
      ["dynamic-pricing", "📊 Dynamic Pricing", { u: "dynamic_pricing" }],
      ["price-lists", "📋 Price Lists", { e: "price_list" }],
      ["promotions", "🎉 Promotions · Coupons", { e: "promotion" }],
      ["merchandising", "🛍️ Merchandising", { u: "catalog_merchandising" }],
    ] },
    { g: "Offers & Incentives", l: [
      ["goffers", "🏷️ Offers · Affiliates", { v: "goffers" }],
      ["loyalty", "⭐ Loyalty", { u: "loyalty" }],
      ["rewards", "🎁 Rewards", { u: "reward" }],
      ["referrals", "🔗 Referrals", { u: "referral" }],
      ["goffers-affiliates", "🏷️ Offers · Affiliates", { v: "goffers" }],
      ["goip", "Ω∞ GOIP · Value Exchange", { v: "offers" }],
    ] },
    { g: "Marketplace", l: [
      ["gmarket", "📣 Ads · Marketplace", { v: "gmarket" }],
      ["marketplace", "🛒 Marketplace", { u: "marketplace" }],
      ["advertising", "📢 Advertising", { u: "advertising" }],
      ["sponsored", "📣 Sponsored Creatives", { e: "sponsored_creative" }],
    ] },
    { g: "Trade", l: [
      ["gb2b", "🤝 Sellers · B2B · Trade", { v: "gb2b" }],
      ["rfq", "📨 RFQs", { e: "rfq" }],
      ["tenders", "🏅 Tenders", { e: "tender" }],
      ["trade-assurance", "🛡️ Trade Assurance", { e: "trade_assurance" }],
      ["letters-of-credit", "📜 Letters of Credit", { e: "letter_of_credit" }],
    ] },
    { g: "Transactions", l: [
      ["cart", "🛒 Cart", { u: "cart" }],
      ["checkout", "💳 Checkout", { u: "checkout" }],
      ["gorders", "🧾 Orders · Fulfilment", { v: "gorders" }],
      ["returns", "↩️ Returns · Exchanges", { e: "ret" }],
      ["reviews", "⭐ Reviews · UGC", { e: "review" }],
    ] },
    { g: "Recurring", l: [
      ["subs", "🔁 Subscriptions", { v: "subs" }],
      ["memberships", "🎟️ Memberships", { e: "membership" }],
      ["recurring-billing", "♻️ Recurring Billing", { u: "recurring_billing" }],
    ] },
    { g: "Billing & Payment", l: [
      ["plans", "💼 Plans", { v: "plans" }],
      ["subs-plans", "🔁 Subscriptions", { v: "subs" }],
      ["invoices", "🧾 Invoices", { v: "invoices" }],
      ["billing", "💳 Billing Ops", { v: "billing" }],
      ["gfinance", "💸 Finance · Payments", { v: "gfinance" }],
      ["payments", "💳 Payments", { e: "payment" }],
      ["settlements", "🧮 Settlements", { e: "settlement" }],
      ["escrow", "🔒 Escrow", { e: "escrow_hold" }],
    ] },
  ] },
  { n: "05 · Operations", g: [
    { g: "Overview", l: [
      ["gops", "🧭 Ops Hub", { v: "gops" }],
    ] },
    { g: "Supply", l: [
      ["inventory", "📦 Inventory", { e: "inventory" }],
      ["warehousing", "🏬 Warehousing", { e: "warehouse" }],
      ["procurement", "🛒 Procurement", { u: "procurement" }],
      ["stock-transfers", "🔀 Stock Transfers", { e: "stock_transfer" }],
      ["replenishment", "🔄 Replenishment", { e: "replenishment" }],
    ] },
    { g: "Fulfilment", l: [
      ["fulfilment", "📦 Fulfilment", { e: "smart_fulfilment" }],
      ["fba", "📦 FBA Inbound", { e: "fba_inbound" }],
      ["logistics", "🚚 Logistics", { u: "logistics" }],
      ["transportation", "🚛 Transportation", { u: "transportation" }],
      ["shipping", "📮 Shipping", { e: "shipment" }],
      ["tracking", "📍 Tracking", { u: "tracking" }],
      ["reverse-logistics", "↩️ Reverse Logistics", { u: "returns" }],
    ] },
    { g: "Service Delivery", l: [
      ["field-ops", "🧰 Field Operations", { u: "field_service_visit" }],
      ["work-orders", "🔧 Work Orders", { u: "work_order" }],
      ["maintenance", "🛠️ Maintenance", { u: "maintenance" }],
      ["dark-stores", "🏬 Dark Stores", { e: "dark_store" }],
      ["dispatch", "⚡ Dispatch Runs", { e: "dispatch_run" }],
      ["riders", "🛵 Riders", { e: "rider" }],
    ] },
    { g: "Support", l: [
      ["gsupport", "🎧 Support · SLA", { v: "gsupport" }],
      ["tickets", "🎫 Tickets", { e: "ticket" }],
      ["cases", "📋 Cases", { u: "support_case" }],
      ["incidents", "🚨 Incidents", { u: "operational_incident" }],
      ["qna", "❓ Q&A", { e: "qna_question" }],
    ] },
  ] },
  { n: "06 · Experience", g: [
    { g: "Surfaces", l: [
      ["websites", "🌐 Websites", { u: "website" }],
      ["mobile", "📱 Mobile Apps", { u: "mobile_app" }],
      ["kiosks", "🛎️ Kiosks · POS", { u: "kiosk" }],
      ["portals", "🚪 Portals", { u: "portal" }],
    ] },
    { g: "Presentation", l: [
      ["gcontent", "🖼️ Content · UGC", { v: "gcontent" }],
      ["themes", "🎨 Themes", { v: "themes" }],
      ["branding", "🖌️ Branding", { u: "brand_skin" }],
      ["personalization", "🎯 Personalization", { u: "personalization" }],
      ["accessibility", "♿ Accessibility", { u: "accessibility" }],
      ["ui-components", "🧩 UI Components", { u: "ui_component" }],
    ] },
    { g: "Channels", l: [
      ["channels", "📡 Channels", { u: "channel_universe" }],
      ["notifications", "🔔 Notifications", { e: "notification" }],
      ["email", "✉️ Email", { u: "email" }],
      ["social", "📱 Social", { u: "social" }],
    ] },
    { g: "Journeys", l: [
      ["ux-journeys", "🧭 UX Journeys", { u: "ux_journey" }],
      ["customer-journeys", "🛤️ Customer Journeys", { u: "customer_journey" }],
      ["experience-registry", "🗄️ Experience Registry", { u: "experience_universe" }],
    ] },
  ] },
  { n: "07 · Intelligence", g: [
    { g: "Models & Agents", l: [
      ["ai", "🧠 AI · Providers & Plans", { v: "ai" }],
      ["ai-models", "🤖 AI Models", { u: "ai_model" }],
      ["agents", "🤖 Agents", { u: "agent" }],
      ["agent-teams", "👥 Agent Teams", { u: "agent_team" }],
      ["prompts", "💬 Prompt Registry", { u: "prompt" }],
    ] },
    { g: "Engines", l: [
      ["reasoning", "🧩 Reasoning Engine", { u: "reasoning" }],
      ["recommendation", "🎯 Recommendation", { u: "recommendation" }],
      ["search-intel", "🔍 Search", { u: "search" }],
      ["personalization-intel", "🎯 Personalization Engine", { u: "personalization_engine" }],
      ["optimization", "⚙️ Optimization", { u: "optimization" }],
      ["simulation", "🧪 Simulation", { u: "simulation" }],
      ["forecasting", "📈 Forecasting", { u: "forecasting" }],
      ["digital-twins", "👯 Digital Twins", { u: "digital_twin" }],
    ] },
    { g: "Trust Intelligence", l: [
      ["fraud", "🕵️ Fraud Detection", { u: "fraud_detection" }],
      ["risk-intel", "⚠️ Risk Engine", { u: "risk" }],
      ["knowledge-intel", "🧠 Knowledge Intelligence", { u: "knowledge_intelligence" }],
    ] },
    { g: "Autonomy", l: [
      ["autonomous-planning", "🗓️ Autonomous Planning", { u: "autonomous_planning" }],
      ["autonomous-execution", " ▶️ Autonomous Execution", { u: "autonomous_execution" }],
      ["autonomous-verification", "✔️ Autonomous Verification", { u: "autonomous_verification" }],
      ["learning", "📚 Learning Engine", { u: "learning" }],
      ["evolution", "🧬 Evolution Engine", { u: "evolution" }],
    ] },
    { g: "Analytics", l: [
      ["ganalytics", "📊 Analytics · A/B", { v: "ganalytics" }],
      ["experiments", "🧪 Experiments", { e: "experiment" }],
      ["intelligence-registry", "🗄️ Intelligence Registry", { u: "intelligence_registry" }],
    ] },
  ] },
  { n: "08 · Governance", g: [
    { g: "Policy", l: [
      ["policies", "🔒 Policies", { v: "policies" }],
      ["standards", "📏 Standards", { u: "standard" }],
      ["regulations", "📜 Regulations", { u: "regulation" }],
      ["rules", "📏 Rules", { u: "rule" }],
      ["decisions", "⚖️ Decisions", { u: "decision" }],
    ] },
    { g: "Compliance", l: [
      ["compliance", "🛡️ Compliance", { e: "compliance" }],
      ["compliance-controls", "🛡️ Compliance Controls", { e: "compliance_control" }],
      ["certifications", "🏅 Certifications", { u: "certification" }],
      ["privacy", "🔒 Privacy", { e: "consent" }],
      ["privacy-requests", "📨 Privacy Requests", { e: "privacy_request" }],
      ["erasure", "🧹 Erasure Log", { e: "erasure_log" }],
    ] },
    { g: "Risk & Security", l: [
      ["risk", "⚠️ Risk", { e: "risk_event" }],
      ["risk-blocks", "⛔ Risk Blocks", { e: "risk_block" }],
      ["security", "🔐 Security", { u: "security" }],
      ["controls", "🎛️ Controls", { u: "control" }],
      ["evidence", "🧾 Evidence", { u: "evidence" }],
    ] },
    { g: "Oversight", l: [
      ["grisk", "🛡️ Risk · Compliance · Trash", { v: "grisk" }],
      ["audit", "📜 Global Audit", { v: "audit" }],
      ["review-governance", "🔍 Reviews", { u: "review_governance" }],
      ["approvals", "✅ Approvals", { u: "approval" }],
      ["change-control", "🔄 Change Control", { u: "change_control" }],
      ["trace", "🧭 Traceability", { v: "trace" }],
      ["ai-governance", "🧠 AI Governance", { u: "ai_governance" }],
      ["agent-governance", "🤖 Agent Governance", { u: "agent_governance" }],
      ["governance-graph", "🕸️ Governance Graph", { u: "governance_graph" }],
    ] },
  ] },
  { n: "09 · Platform", g: [
    { g: "Capabilities", l: [
      ["capabilities", "⚙️ Capabilities", { v: "capabilities" }],
      ["capability-tree", "🌳 Capability Tree", { v: "capability-tree" }],
      ["capability-registry", "🗄️ Capability Registry", { u: "capability_registry" }],
      ["capability-composition", "🧩 Capability Composition", { u: "capability_composition" }],
      ["capability-discovery", "🧭 Capability Discovery", { u: "capability_discovery" }],
    ] },
    { g: "Composition", l: [
      ["compose", "🧬 Composition Engine", { v: "compose" }],
    ] },
    { g: "Extension", l: [
      ["providers", "🔌 Provider Registry", { v: "providers" }],
      ["modules", "🧩 Module Marketplace", { v: "modules" }],
      ["connectors", "🔌 Connectors", { u: "connectors" }],
      ["integrations", "🔗 Integrations", { u: "integration" }],
      ["extensions", "🧩 Extensions", { u: "extension" }],
    ] },
    { g: "Runtime", l: [
      ["runtime", "🧩 Runtime · Infra", { v: "runtime" }],
      ["runtime-registry", "🗄️ Runtime Registry", { u: "runtime" }],
      ["deployment", "🚀 Deployment", { u: "deployment" }],
      ["infrastructure", "🏗️ Infrastructure", { u: "infrastructure" }],
      ["apis", "🔌 APIs", { u: "api_product" }],
      ["events", "⚡ Events", { u: "event" }],
      ["workflows", "🔀 Workflows", { u: "workflow" }],
    ] },
    { g: "Evolution", l: [
      ["versioning", "🔢 Versioning", { u: "versioning" }],
      ["migration", "🔀 Migration", { u: "migration" }],
      ["deprecation", "🗑️ Deprecation", { u: "deprecation" }],
      ["impact-analysis", "📊 Impact Analysis", { u: "impact_analysis" }],
      ["self-healing", "🩹 Self Healing", { u: "self_healing" }],
      ["self-optimization", "⚙️ Self Optimization", { u: "self_optimization" }],
    ] },
  ] },
  { n: "10 · Observability", g: [
    { g: "Telemetry", l: [
      ["dash", "◈ Command", { v: "dash" }],
      ["monitor", "📈 Monitoring", { v: "monitor" }],
      ["metrics", "📊 Metrics", { u: "metrics" }],
      ["logs", "🪵 Logs", { u: "logs" }],
      ["traces", " 🔗 Traces", { u: "traces" }],
      ["alerting", "🚨 Alerting", { u: "alerting" }],
    ] },
    { g: "Health", l: [
      ["reliability", "🛡️ Reliability", { u: "reliability" }],
      ["health-availability", "🟢 Availability", { u: "availability" }],
      ["capacity", "📦 Capacity", { u: "capacity" }],
      ["performance", "⚡ Performance", { u: "performance" }],
      ["health", "💚 Health", { u: "health" }],
    ] },
    { g: "Insight", l: [
      ["dashboards", "📊 Dashboards", { v: "dashboards" }],
      ["gdata", "🧬 Data Explorer", { v: "gdata" }],
      ["studio", "🛠️ Data Studio", { v: "studio" }],
      ["definitions", "📐 Entity Definitions", { v: "definitions" }],
      ["slo", "🎯 SLO · SLA", { u: "slo" }],
      ["rca", "🔍 Root Cause Analysis", { u: "root_cause_analysis" }],
      ["diagnostics", "🩺 Diagnostics", { u: "diagnostics" }],
      ["cost", "💸 Cost · Usage", { u: "cost" }],
    ] },
  ] },
  { n: "11 · Administration", g: [
    { g: "Tenancy", l: [
      ["tenants-admin", "🏬 Tenants", { v: "tenants" }],
      ["companies", "🏢 Companies", { u: "company" }],
      ["workspaces", "🗂️ Workspaces", { u: "workspace" }],
      ["environments", "🌍 Environments", { v: "runtime" }],
    ] },
    { g: "Access", l: [
      ["users-admin", "👤 Users", { v: "users" }],
      ["roles-admin", "🎭 Roles", { v: "roles" }],
      ["permissions-admin", "🔑 Permissions", { u: "permission" }],
      ["padmins", "🛡️ Platform Admins", { v: "padmins" }],
      ["licenses", "🪪 Licenses", { u: "license" }],
      ["gteam", "👥 Team · Access · Settings", { v: "gteam" }],
    ] },
    { g: "Configuration", l: [
      ["registries", "📚 Platform Registries", { v: "registries" }],
      ["configurations", "⚙️ Configurations", { u: "configuration" }],
      ["secrets", "保密 Secrets", { u: "secrets_management" }],
      ["settings", "⚙️ Settings", { v: "gteam" }],
      ["feature-flags", "🚩 Feature Flags", { v: "runtime" }],
      ["provisioning", "🛡️ Provisioning", { v: "provisioning" }],
    ] },
  ] },
  { n: "12 · Architecture", g: [
    { g: "Constitution Ω∞", l: [
      ["ucii", "🌀 UCII Ω∞ Registry", { v: "ucii" }],
      ["ucos", "♾️ UCOS Ω∞ Constitution", { v: "ucos" }],
      ["foundations", "🏛️ Foundations", { v: "foundations" }],
      ["universes", "🧬 Universes", { v: "universes" }],
      ["domains", "🔀 Domains", { v: "domains" }],
    ] },
    { g: "Canonical Model", l: [
      ["canonical-objects", "📦 Canonical Objects", { u: "canonical_object" }],
      ["canonical-schemas", "📐 Canonical Schemas", { u: "canonical_schema" }],
      ["canonical-relationships", "🔗 Canonical Relationships", { u: "canonical_relationship" }],
      ["canonical-events", "⚡ Canonical Events", { u: "canonical_event" }],
      ["canonical-apis", "🔌 Canonical APIs", { u: "canonical_api" }],
      ["canonical-workflows", "🔀 Canonical Workflows", { u: "canonical_workflow" }],
    ] },
    { g: "Graphs", l: [
      ["capability-graph", "🕸️ Capability Graph", { u: "capability_graph" }],
      ["knowledge-graph-arch", "🕸️ Knowledge Graph", { u: "knowledge_graph" }],
      ["dependency-graph", "🕸️ Dependency Graph", { u: "dependency_graph" }],
      ["traceability-graph", "🕸️ Traceability Graph", { u: "traceability_graph" }],
    ] },
    { g: "Reference", l: [
      ["reference-architecture", "🏛️ Reference Architecture", { u: "reference_architecture" }],
      ["security-architecture", "🔐 Security Architecture", { u: "security_architecture" }],
      ["data-architecture", "🗄️ Data Architecture", { u: "data_architecture" }],
      ["ai-architecture", "🧠 AI Architecture", { u: "ai_architecture" }],
      ["evolution-architecture", "🧬 Evolution Architecture", { u: "evolution_architecture" }],
    ] },
    { g: "Documentation", l: [
      ["manual", "📘 User Manual", { v: "manual" }],
      ["architecture", "🏛️ Architecture", { v: "architecture" }],
    ] },
  ] },
];
/* NAVFLAT keeps the O(1) leaf lookup the shell's title bar needs — one pass, no per-render
   tree walks, and the canonical home of any key is discoverable in both directions. */
const NAVFLAT = [];
const NAVKEY = {};
for (const sec of NAV) for (const grp of sec.g) for (const [k, l, res] of grp.l) {
  NAVFLAT.push([k, l, res, sec.n + " · " + grp.g]);
  NAVKEY[k] = { label: l, res, home: sec.n + " · " + grp.g };
}
/* the console opens on the constitutional dashboard — the platform's front door is the
   command view, not any single store's setup */
let view = "dash";
const P = { user: null, tenants: [], plans: [] };

/* RBAC: a leaf is visible when its key is in the admin's grants ('*' = owner). The nav
   is generated from the same NAV the back-end section map names, so a hidden leaf is
   also a refused API call — the two cannot disagree. */
const canSee = k => { if (!P.allowed || P.allowed.includes("*")) return true; if (k === "dash") return true; return P.allowed.includes(k); };

/* the open-section memory: a section stays expanded while the operator works inside it,
   so navigating between a group's leaves never collapses the tree on them. */
const NAVOPEN = new Set();
function navTree() {
  return NAV.map(sec => {
    const groups = sec.g.map(grp => {
      const items = grp.l.filter(([k]) => canSee(k));
      return items.length ? `<div class="p-nav-grp"><small>${esc(grp.g)}</small>${items.map(([k, l]) => `<button data-v="${k}" class="${view === k ? "on" : ""}">${l}</button>`).join("")}</div>` : "";
    }).join("");
    if (!groups) return "";
    const inSec = sec.g.some(grp => grp.l.some(([k]) => k === view));
    if (inSec) NAVOPEN.add(sec.n);
    const open = NAVOPEN.has(sec.n);
    return `<details class="p-nav-sec" ${open ? "open" : ""}>
      <summary>${esc(sec.n)}</summary>${groups}
    </details>`;
  }).join("");
}
function shell(content) {
  const meta = NAVKEY[view];
  $("#app").innerHTML = `
  <div class="p-shell">
    <aside class="p-side" id="pSide">
      <div class="p-logo"><b>LUXORA</b><small>Platform Console</small>
        <button class="p-side-close" id="pSideClose" aria-label="Close navigation">✕</button></div>
      <nav class="p-nav">${navTree()}</nav>
    </aside>
    <div class="p-scrim" id="pScrim"></div>
    <main class="p-main"><div class="p-top"><button class="p-hamburger" id="pBurger" aria-label="Open navigation">☰</button><h1 id="vTitle">${meta ? meta.label.replace(/^\S+\s/, "") : view}</h1><span class="spacer"></span>
      ${meta ? `<span class="p-tag">${esc(meta.home)}</span>` : ""}
      <span class="p-chip">platform</span><span class="p-user">${esc(P.user.email)}</span>
      <span class="p-tag">${esc((P.user && P.user.role) || "owner")}</span>
      <button class="p-btn sm" id="logoutBtn">Sign out</button></div>
      <div id="vBody">${content}</div></main>
  </div>`;
  $$(".p-nav button").forEach(b => b.onclick = () => { view = b.dataset.v; render(); });
  $("#logoutBtn").onclick = async () => { await api("/platform/logout", "POST"); location.reload(); };
  wireDrawer();
}
/* the touch drawer: on tablet/phone the sidebar is off-canvas and opened by the hamburger.
   Wired once per render (the shell is re-written each time) and closes on navigation or a
   tap on the scrim, so a phone user never has to hunt for a close button. */
function wireDrawer() {
  const side = $("#pSide"), scrim = $("#pScrim"), burger = $("#pBurger"), close = $("#pSideClose");
  if (burger) burger.onclick = () => { if (side) side.classList.add("p-side-open"); if (scrim) scrim.style.display = "block"; };
  const shut = () => { if (side) side.classList.remove("p-side-open"); if (scrim) scrim.style.display = "none"; };
  if (close) close.onclick = shut;
  if (scrim) scrim.onclick = shut;
  $$(".p-nav button").forEach(b => b.addEventListener("click", shut));
}

async function vDash() {
  const [rev, mon, tenants] = await Promise.all([api("/platform/revenue"), api("/platform/monitor"), api("/platform/tenants")]);
  const max = Math.max(1, ...rev.byMonth.map(m => m.paid));
  return `
  <div class="p-cards">
    <div class="p-stat"><em>MRR</em><b>${money(rev.mrr)}</b><small>recurring</small></div>
    <div class="p-stat"><em>Collected</em><b>${money(rev.collected)}</b></div>
    <div class="p-stat"><em>Outstanding</em><b>${money(rev.outstanding)}</b><small style="color:var(--p-red)">unpaid</small></div>
    <div class="p-stat"><em>Platform GMV</em><b>${money(rev.gmv)}</b><small>gateway fees ${money(rev.gatewayFees)}</small></div>
    <div class="p-stat"><em>Stores</em><b>${tenants.tenants.length}</b></div>
    <div class="p-stat"><em>Requests</em><b>${mon.totals.req}</b><small>${mon.totals.err} errors · ${mon.totals.avgMs}ms avg</small></div>
  </div>
  <div class="p-grid2">
    <div class="p-panel"><h2>Billing by month</h2><div class="p-chart">${rev.byMonth.map(m => `<div class="bar" style="height:${Math.max(4, m.paid / max * 100)}%" data-tip="${esc(m.m)}: ${money(m.paid)}"></div>`).join("") || '<div class="p-empty">No invoices</div>'}</div></div>
    <div class="p-panel"><h2>Stores</h2><table class="p-table"><thead><tr><th>Store</th><th>Mode</th><th class="num">Products</th><th class="num">GMV</th><th>Plan</th></tr></thead>
      <tbody>${tenants.tenants.map(t => `<tr><td><a href="/index.html?store=${esc(t.slug)}" target="_blank">${esc(t.name)}</a></td><td>${esc(t.mode)}</td><td class="num">${t.products}</td><td class="num">${money(t.gmv)}</td><td>${esc(t.plan || "—")}</td></tr>`).join("")}</tbody></table></div>
  </div>
  <div class="p-panel"><h2>System</h2><div class="p-kv"><em>Uptime</em><span>${Math.floor(mon.system.uptimeSec / 60)} min</span><em>Memory</em><span>${mon.system.rssMB} MB</span><em>Database</em><span>${mon.system.dbKB} KB</span><em>Node</em><span>${esc(mon.system.node)}</span></div></div>`;
}
async function vTenants() {
  const { tenants } = await api("/platform/tenants");
  P.tenants = tenants;
  return `
  <div class="p-panel"><div style="display:flex;align-items:center;gap:12px;margin-bottom:6px">
    <h2 style="margin:0">Tenants (${tenants.length})</h2><span style="flex:1"></span>
    <button class="p-btn primary sm" id="newTenant">＋ Register platform</button></div>
    <p style="margin:0 0 14px;color:var(--p-muted);font-size:13px">The platform's tenancy registry. A tenant's <b>Products</b>, SKUs &amp; inventory, orders, suppliers, compliance and settings live in its <b>Store Console</b> — click <b>Manage · Catalog</b> to open it.</p>
    <div class="p-scroll-x"><table class="p-table"><thead><tr><th>Tenant</th><th>Slug</th><th>Jurisdiction</th><th>Owner</th><th>Mode</th><th>Industries</th><th class="num">Products</th><th class="num">Orders</th><th class="num">GMV</th><th>Plan</th><th>Status</th><th></th></tr></thead>
    <tbody>${tenants.map(t => `<tr><td><b>${esc(t.name)}</b></td><td>${esc(t.slug)}</td><td>${esc(t.country || "—")}</td><td class="p-tag">${esc((t.profile && t.profile.ownerEmail) || "—")}</td><td>${esc(t.mode)}</td>
      <td class="p-tag">${esc((t.industries || "[]").replace(/["[\]]/g, "").slice(0, 40))}</td>
      <td class="num">${t.products}</td><td class="num">${t.orders}</td><td class="num">${money(t.gmv)}</td>
      <td>${esc(t.plan || "—")}</td><td><span class="badge ${esc(t.status)}">${esc(t.status)}</span></td>
      <td style="white-space:nowrap"><button class="p-btn sm" data-open="${t.id}">Open</button>
        <button class="p-btn sm" data-tedit="${t.id}" title="Edit this tenant's identity">Edit</button>
        <button class="p-btn sm primary" data-imp="${t.id}" title="Enter this store's Store Console — Products, SKUs, Orders and more">Manage · Catalog</button>
        <button class="p-btn sm" data-susp="${t.id}">${t.status === "active" ? "Suspend" : "Resume"}</button>
        <button class="p-btn sm" data-inv="${t.id}">Invoice</button>
        <button class="p-btn sm danger" data-del="${t.id}">✕</button></td></tr>`).join("")}</tbody></table></div></div>`;
}
/* platform registration: ONE guided pass that composes a whole platform — a marketplace,
   a ride-hailing service, an ERP — from the registries themselves. Every option below is
   enumerated from a live registry (/api/meta, the capability presets, the identity
   templates, the plan catalogue), so a new industry, archetype, auth policy or country
   appears here the moment it is added anywhere; nothing in this walk is a hard-coded list
   that can drift from the platform. Identity is part of the same pass — never deferred to
   a separate screen — so a platform is registered complete: type, capabilities, catalogue
   AND authentication policy.
   The console remains the place to TUNE a platform; this is the place to REGISTER one. */
async function registerModal() {
  const [meta, capd, pland, idtd] = await Promise.all([api("/meta"), api("/capabilities"), api("/platform/plans"), api("/platform/identity-templates")]);
  const industries = meta.industries || [], countries = (meta.countries || []).filter(c => c.active), modes = meta.deployModes || [];
  const presets = (capd.presets || []).filter(p => p.key !== "blend_mixed" || true);
  const plans = pland.plans || [];
  /* identity policies are enumerated from the identity registry exactly like archetypes
     from the capability registry — the default template is pre-chosen so a platform is
     never registered without a deliberate authentication policy */
  const idTemplates = (idtd.templates || []).slice().sort((a, b) => (b.is_default || 0) - (a.is_default || 0));
  const defTmpl = idTemplates.find(t => t.is_default) || idTemplates[0];
  const R = { name: "", slug: "", country: "US", mode: "marketplace", ownerName: "", ownerEmail: "", ownerPassword: "",
    legalName: "", taxId: "", language: "", archetype: "", industries: [], seedUniverses: true, seedCatalog: false,
    identityTemplate: defTmpl ? defTmpl.id : null, planId: plans[0] ? plans[0].id : 1 };
  let step = 0;
  const m = modal(`<div class="p-modal-head"><h3>Register a platform</h3><button data-mclose>✕</button></div>
    <div id="regBody"></div>`);
  const body = () => m.querySelector("#regBody");
  const STEPS = ["Registration", "Identity & language", "Platform type", "Services & products", "Review"];
  const sync = () => {
    const g = id => { const el = m.querySelector("#" + id); return el ? el.value.trim() : undefined; };
    const had = { name: R.name, slug: R.slug, country: R.country, mode: R.mode, language: R.language };
    if (step > 0 || had.name !== undefined) {
      R.name = g("rName") !== undefined ? g("rName") : R.name;
      R.slug = g("rSlug") !== undefined ? g("rSlug") : R.slug;
      R.country = g("rCountry") || R.country;
      R.mode = g("rMode") || R.mode;
      R.ownerName = g("rOwnerName") !== undefined ? g("rOwnerName") : R.ownerName;
      R.ownerEmail = g("rOwnerEmail") !== undefined ? g("rOwnerEmail") : R.ownerEmail;
      R.ownerPassword = g("rOwnerPass") !== undefined ? g("rOwnerPass") : R.ownerPassword;
      R.legalName = g("rLegal") !== undefined ? g("rLegal") : R.legalName;
      R.taxId = g("rTax") !== undefined ? g("rTax") : R.taxId;
      R.language = g("rLang") !== undefined ? g("rLang") : R.language;
      R.planId = m.querySelector("#rPlan") ? Number(m.querySelector("#rPlan").value) : R.planId;
      const arch = m.querySelector("input[name='rArch']:checked"); if (arch) R.archetype = arch.value;
      const idt = m.querySelector("input[name='rIdTmpl']:checked"); if (idt) R.identityTemplate = idt.value ? Number(idt.value) : null;
      m.querySelectorAll("[data-ind]").forEach(c => { const k = c.dataset.ind; const on = c.classList.contains("on"); R.industries = R.industries.includes(k) ? (on ? R.industries : R.industries.filter(x => x !== k)) : (on ? R.industries.concat(k) : R.industries); });
      const su = m.querySelector("#rSeedUv"); if (su) R.seedUniverses = su.checked;
      const sc = m.querySelector("#rSeedCat"); if (sc) R.seedCatalog = sc.checked;
    }
  };
  const stepHtml = () => {
    const dots = STEPS.map((s, i) => `<span class="a-chip" style="${i === step ? "background:var(--p-accent);color:#111" : "opacity:.5"}">${i + 1}. ${s}</span>`).join(" ");
    if (step === 0) return `<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px">${dots}</div><div class="p-form">
      <label><span>Platform name *</span><input id="rName" value="${esc(R.name)}" placeholder="Acme Commerce"></label>
      <label><span>Slug (store URL) *</span><input id="rSlug" value="${esc(R.slug)}" placeholder="acme"></label>
      <label><span>Country / jurisdiction *</span><select id="rCountry">${countries.map(c => `<option value="${c.code}" ${R.country === c.code ? "selected" : ""}>${esc(c.name)} · ${c.currency}</option>`).join("")}</select></label>
      <label><span>Platform mode *</span><select id="rMode">${modes.map(x => `<option value="${x.key}" ${R.mode === x.key ? "selected" : ""}>${esc(x.name)} — ${esc(x.desc)}</option>`).join("")}</select></label>
      <label><span>Admin name *</span><input id="rOwnerName" value="${esc(R.ownerName)}" placeholder="Ava One"></label>
      <label><span>Admin email *</span><input id="rOwnerEmail" value="${esc(R.ownerEmail)}" placeholder="admin@acme.com"></label>
      <label><span>Admin password *</span><input id="rOwnerPass" type="password" value="${esc(R.ownerPassword)}" placeholder="6+ characters"></label>
      <label><span>Legal name (optional)</span><input id="rLegal" value="${esc(R.legalName)}" placeholder="Acme Commerce Pvt Ltd"></label>
      <label><span>Tax ID (optional)</span><input id="rTax" value="${esc(R.taxId)}" placeholder="GSTIN / EIN"></label></div>`;
    if (step === 1) { const ctry = countries.find(c => c.code === R.country);
      /* a template's config arrives as a JSON string from the list endpoint */
      const cfgOf = t => { try { return typeof t.config === "string" ? JSON.parse(t.config || "{}") : (t.config || {}); } catch (e) { return {}; } };
      const pwOf = t => { const p = cfgOf(t).password || {}; return (p.minLength || 10) + "+ chars"
        + (p.requireUppercase ? " · mixed case" : "") + (p.requireSpecialChars ? " · symbols" : "")
        + (p.expiryDays ? " · expires " + p.expiryDays + "d" : " · never expires"); };
      const mfOf = t => { const c = cfgOf(t), m = c.mfa || {}; return m.enabled ? "MFA on" + (m.requireForStaff ? " · required for all staff" : m.requireForAdmin ? " · required for admins" : "") : "no MFA"; };
      return `<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px">${dots}</div><div class="p-form">
      <label><span>Language / locale</span><input id="rLang" value="${esc(R.language || (ctry && ctry.locale) || "en-US")}" placeholder="en-US"></label>
      <p class="p-tag" style="margin:4px 0 2px">The locale defaults from the chosen jurisdiction (${esc(R.country)} → ${ctry ? ctry.locale : "—"}). The authentication policy is picked here from the identity registry (${idTemplates.length} templates) — a platform is never registered without one. Tune it later from <b>01 · Foundation → Identity</b>.</p>
      <div style="display:grid;gap:8px">${idTemplates.map(t => `<label style="display:flex;gap:10px;align-items:flex-start;border:1px solid var(--p-border);border-radius:10px;padding:10px;cursor:pointer;${R.identityTemplate === t.id ? "border-color:var(--p-accent)" : ""}">
        <input type="radio" name="rIdTmpl" value="${t.id}" ${R.identityTemplate === t.id ? "checked" : ""} style="margin-top:3px">
        <span><b>${esc(t.name)}</b>${t.is_default ? ' <span class="a-chip">default</span>' : ""}<br>
        <span class="p-tag">${esc(t.description || "")}</span><br>
        <code style="font-size:10px">${pwOf(t)} · ${mfOf(t)}</code></span></label>`).join("") || '<p class="p-empty">No identity templates registered — the engine defaults will apply. Create one from 01 · Foundation → Identity Templates.</p>'}</div></div>`; }
    if (step === 2) return `<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px">${dots}</div>
      <p class="p-tag">An archetype writes the store's capability rows in one call — this is what the platform <b>is</b>. Tuning afterwards is kept.</p>
      <div style="display:grid;gap:8px">${presets.map(p => `<label style="display:flex;gap:10px;align-items:flex-start;border:1px solid var(--p-border);border-radius:10px;padding:10px;cursor:pointer;${R.archetype === p.key ? "border-color:var(--p-accent)" : ""}">
        <input type="radio" name="rArch" value="${esc(p.key)}" ${R.archetype === p.key ? "checked" : ""} style="margin-top:3px">
        <span><b>${esc(p.label)}</b> <code style="font-size:10px">${esc(p.key)}</code><br><span class="p-tag">${esc(p.description || "")}</span></span></label>`).join("")}
      <label style="display:flex;gap:10px;align-items:center;border:1px solid var(--p-border);border-radius:10px;padding:10px;cursor:pointer;${R.archetype === "" ? "border-color:var(--p-accent)" : ""}">
        <input type="radio" name="rArch" value="" ${R.archetype === "" ? "checked" : ""}>
        <span><b>No archetype</b><br><span class="p-tag">Register an empty platform and compose it capability-by-capability in ⚙️ Capabilities.</span></span></label></div>`;
    if (step === 3) return `<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px">${dots}</div>
      <p class="p-tag">Industries scope the catalogue${R.mode === "marketplace" ? "" : " — required for this mode"}. Picked from the registry (${industries.length} registered).</p>
      <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px">${industries.map(i => `<button class="p-btn sm ${R.industries.includes(i.key) ? "primary on" : ""}" data-ind="${esc(i.key)}" type="button">${esc(i.icon || "▪")} ${esc(i.name)}</button>`).join("")}</div>
      <div class="p-form">
      <label class="checkbox-group"><input type="checkbox" id="rSeedUv" ${R.seedUniverses ? "checked" : ""}> Activate the archetype's catalog content (universes publish products, SKUs and inventory)</label>
      <label class="checkbox-group"><input type="checkbox" id="rSeedCat" ${R.seedCatalog ? "checked" : ""}> Also seed the demo product catalogue</label></div>`;
    const arch = presets.find(p => p.key === R.archetype);
    return `<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px">${dots}</div>
      <div class="p-form">
      <label><span>Subscription plan</span><select id="rPlan">${plans.map(p => `<option value="${p.id}" ${R.planId === p.id ? "selected" : ""}>${esc(p.name)} — ${money(p.price_month)}/mo · ${p.max_products.toLocaleString()} products</option>`).join("")}</select></label></div>
      <div class="a-tablewrap" style="margin-top:10px"><table class="p-table"><tbody>
      <tr><td>Platform</td><td><b>${esc(R.name)}</b> <code>${esc(R.slug)}</code></td></tr>
      <tr><td>Jurisdiction</td><td>${esc(R.country)}${R.legalName ? " · " + esc(R.legalName) : ""}${R.taxId ? " · " + esc(R.taxId) : ""}</td></tr>
      <tr><td>Admin</td><td>${esc(R.ownerEmail)}</td></tr>
      <tr><td>Mode</td><td>${esc(R.mode)}</td></tr>
      <tr><td>Language</td><td>${esc(R.language)}</td></tr>
      <tr><td>Identity policy</td><td>${(() => { const t = idTemplates.find(x => x.id === R.identityTemplate); return t ? "<b>" + esc(t.name) + "</b> · password &amp; MFA policy" : "engine defaults"; })()}</td></tr>
      <tr><td>Platform type</td><td>${arch ? "<b>" + esc(arch.label) + "</b> · " + Object.keys(arch.capabilities || {}).length + " capabilities" : "no archetype — composed by hand"}</td></tr>
      <tr><td>Industries</td><td>${R.industries.length ? R.industries.map(k => { const i = industries.find(x => x.key === k); return esc(i ? i.name : k); }).join(", ") : "—"}</td></tr>
      <tr><td>Catalogue</td><td>${R.seedUniverses ? "universe content activated" : "no universe content"}${R.seedCatalog ? " + demo products" : ""}</td></tr>
      </tbody></table></div>`;
  };
  const paint = () => {
    body().innerHTML = stepHtml()
      + `<div style="display:flex;gap:8px;margin-top:14px;align-items:center">
         ${step > 0 ? '<button class="p-btn sm" id="regBack">← Back</button>' : ""}
         ${step < STEPS.length - 1 ? '<button class="p-btn primary" id="regNext">Next →</button>' : '<button class="p-btn primary" id="regGo">⚡ Register platform</button>'}
         <span class="p-tag">Step ${step + 1} of ${STEPS.length}</span></div>`;
    const back = m.querySelector("#regBack"); if (back) back.onclick = () => { sync(); step--; paint(); };
    const next = m.querySelector("#regNext"); if (next) next.onclick = () => { sync(); step++; paint(); };
    m.querySelectorAll("[data-ind]").forEach(c => c.onclick = () => { c.classList.toggle("on"); c.classList.toggle("primary"); });
    const go = m.querySelector("#regGo");
    if (go) go.onclick = async () => {
      sync();
      if (!R.name || !R.slug) return toast("Name and slug are required");
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(R.ownerEmail) || String(R.ownerPassword).length < 6) return toast("Admin needs a valid email and a 6+ character password");
      if ((R.mode === "industry" || R.mode === "brand") && !R.industries.length) return toast("Pick at least one industry for this mode");
      go.disabled = true; go.textContent = "Registering…";
      try {
        const r = await api("/platform/tenants", "POST", {
          name: R.name, slug: R.slug, country: R.country, mode: R.mode,
          owner: { name: R.ownerName, email: R.ownerEmail, password: R.ownerPassword },
          jurisdiction: { legalName: R.legalName, taxId: R.taxId, country: R.country },
          language: R.language, archetype: R.archetype || undefined, identity_template: R.identityTemplate || undefined,
          industries: R.industries, seedUniverses: R.seedUniverses, seedCatalog: R.seedCatalog,
          plan_id: R.planId
        });
        if (r.error) { go.disabled = false; go.textContent = "⚡ Register platform"; return toast(r.error); }
        m.innerHTML = "";
        toast(`Registered ${r.tenant.name}${r.archetype ? " · " + r.archetype : ""}${r.identity ? " · " + r.identity.name + " identity" : ""}${(r.activated || []).length ? " · " + r.activated.length + " catalogue offerings published" : ""}`);
        render();
      } catch (e) { go.disabled = false; go.textContent = "⚡ Register platform"; toast(e.message); }
    };
  };
  paint();
}
/* tenant authoring: a single form for EDIT only — registration is the guided flow above;
   the constitutional model treats a tenant as an identity record the platform provisions */
async function tenantModal(id) {
  const t = id ? P.tenants.find(x => x.id === id) : null;
  const isEdit = !!t;
  const m = modal(`<div class="p-modal-head"><h3>${isEdit ? "Edit · " + esc(t.name) : "New tenant"}</h3><button data-mclose>✕</button></div>
    <div class="p-form">
      <label><span>Name</span><input id="tnName" value="${t ? esc(t.name) : ""}" placeholder="Acme Commerce"></label>
      <label><span>Slug</span><input id="tnSlug" value="${t ? esc(t.slug) : ""}" placeholder="acme" ${isEdit ? "disabled" : ""}></label>
      <label><span>Country</span><input id="tnCountry" value="${t ? esc(t.country || "") : ""}" placeholder="US"></label>
      <label><span>Owner name</span><input id="tnOwnerName" value="${t && t.profile ? esc(t.profile.ownerName || "") : ""}" placeholder="Ava One"></label>
      <label><span>Owner email</span><input id="tnOwner" value="${t && t.profile ? esc(t.profile.ownerEmail || "") : ""}" placeholder="owner@acme.com"></label>
      ${isEdit ? "" : '<label><span>Owner password</span><input id="tnPass" type="password" placeholder="6+ characters" minlength="6"></label>'}
      <label><span>Mode</span><select id="tnMode">${["marketplace", "industry", "brand"].map(x => `<option ${t && t.mode === x ? "selected" : ""}>${x}</option>`).join("")}</select></label>
      <button class="p-btn primary" id="tnSave">${isEdit ? "Save changes" : "Create tenant"}</button>
    </div>`);
  m.querySelector("#tnSave").onclick = async () => {
    const body = {
      name: m.querySelector("#tnName").value.trim(),
      slug: m.querySelector("#tnSlug").value.trim().toLowerCase(),
      country: m.querySelector("#tnCountry").value.trim().toUpperCase(),
      ownerName: m.querySelector("#tnOwnerName").value.trim(),
      ownerEmail: m.querySelector("#tnOwner").value.trim(),
      mode: m.querySelector("#tnMode").value
    };
    const pass = m.querySelector("#tnPass");
    if (pass) body.ownerPassword = pass.value;
    if (!body.name || !body.slug) return toast("Name and slug are required");
    try {
      if (isEdit) await api("/platform/tenants/" + t.id, "PUT", body);
      else await api("/platform/tenants", "POST", body);
      m.innerHTML = ""; toast(isEdit ? "Tenant updated" : "Tenant created"); render();
    } catch (e) { toast(e.message); }
  };
}

async function vPlans() {
  const { plans } = await api("/platform/plans");
  P.plans = plans;
  return `<div class="p-panel"><div style="display:flex;align-items:center;gap:12px;margin-bottom:14px">
    <h2 style="margin:0">Plans</h2><span style="flex:1"></span><button class="p-btn primary sm" id="newPlan">+ New plan</button></div>
    <table class="p-table"><thead><tr><th>Name</th><th class="num">Price/mo</th><th>Currency</th><th class="num">Max products</th><th class="num">Max orders/mo</th><th></th></tr></thead>
    <tbody>${plans.map(p => `<tr><td><b>${esc(p.name)}</b></td><td class="num">${money(p.price_month)}</td><td>${esc(p.currency)}</td><td class="num">${p.max_products.toLocaleString()}</td><td class="num">${p.max_orders_month.toLocaleString()}</td>
      <td><button class="p-btn sm" data-editplan="${p.id}">Edit</button></td></tr>`).join("")}</tbody></table></div>`;
}
async function vSubs() {
  const [subs, tenants, plans] = await Promise.all([api("/meta/entity/subscription"), api("/platform/tenants"), api("/platform/plans")]);
  const tn = Object.fromEntries(tenants.tenants.map(t => [t.id, t.name]));
  const pn = Object.fromEntries(plans.plans.map(p => [p.id, p.name]));
  return `<div class="p-panel"><div style="display:flex;align-items:center;gap:12px;margin-bottom:14px">
    <h2 style="margin:0">Subscriptions</h2><span style="flex:1"></span><button class="p-btn primary sm" id="newSub">+ Assign plan</button></div>
    <table class="p-table"><thead><tr><th>Store</th><th>Plan</th><th>Status</th><th>Started</th><th>Renews</th></tr></thead>
    <tbody>${subs.rows.map(s => `<tr><td>${esc(tn[s.tenant_id] || s.tenant_id)}</td><td>${esc(pn[s.plan_id] || s.plan_id)}</td>
      <td><span class="badge ${esc(s.status)}">${esc(s.status)}</span></td><td>${esc(s.started_at)}</td><td>${esc(s.renews_at)}</td></tr>`).join("")}</tbody></table></div>`;
}
async function vInvoices() {
  const { invoices } = await api("/platform/invoices");
  return `<div class="p-panel"><h2>Invoices</h2>
    <table class="p-table"><thead><tr><th>Number</th><th>Store</th><th>Period</th><th class="num">Amount</th><th>Status</th><th>Issued</th><th></th></tr></thead>
    <tbody>${invoices.map(i => `<tr><td>${esc(i.number)}</td><td>${esc(i.tenant_name)}</td><td>${esc(i.period_start)} → ${esc(i.period_end || "")}</td>
      <td class="num">${money(i.amount)}</td><td><span class="badge ${esc(i.status)}">${esc(i.status)}</span></td><td class="p-tag">${esc(i.issued_at)}</td>
      <td>${i.status !== "paid" ? `<button class="p-btn sm primary" data-payinv="${i.id}">Collect</button>` : "✓"}</td></tr>`).join("")}</tbody></table></div>`;
}
/* live carrier accounts: the credentials every store's rates and labels use. Keys are
   sealed on save and never come back — the form shows only whether one is on file, and a
   blank field keeps the stored value. */
async function vCarrierAccounts() {
  const { providers, public_url } = await api("/platform/shipping/providers").catch(() => ({ providers: [] }));
  const ep = providers.find(p => p.provider_id === "easypost");
  if (!ep) return "";
  const k = ep.keys || {};
  const hook = (public_url || location.origin) + "/api/shipping/webhook/easypost";
  const onFile = has => has ? '<span class="badge active">on file</span>' : '<span class="badge inactive">not set</span>';
  return `<div class="p-panel" id="carrierAccounts"><h2>🚚 Carrier account · EasyPost <span class="badge ${esc(ep.status)}">${ep.status === "active" ? "connected" : "not connected"}</span></h2>
    <p class="p-tag">One EasyPost account gives every store live rates, labels and tracking for USPS, UPS, FedEx, DHL and ~100 more carriers. Get the keys at <b>easypost.com → Account → API Keys</b> (a <code>EZTK…</code> test key buys free sample labels). Each store then sets its own ship-from address in <b>Store console → Shipping &amp; Tracking</b>.</p>
    <div class="p-form">
      <div class="row"><label><span>API key ${onFile(k.apiKey)}</span><input id="epKey" type="password" autocomplete="off" placeholder="${k.apiKey ? "•••• leave blank to keep" : "EZAK… or EZTK…"}"></label>
      <label><span>Webhook secret ${onFile(k.webhookSecret)}</span><input id="epSecret" type="password" autocomplete="off" placeholder="${k.webhookSecret ? "•••• leave blank to keep" : "the secret you type into EasyPost's webhook form"}"></label></div>
      <label><span>Webhook URL — add it in EasyPost → Account → Webhooks, with the secret above</span><input id="epHook" readonly value="${esc(hook)}"></label>
      ${!public_url && /localhost|127\.0\.0\.1/.test(location.hostname) ? '<p class="p-tag">EasyPost can\'t reach localhost. Locally, tracking updates won\'t arrive unless you expose the server with a tunnel; rates and labels still work. In production set <code>LX_PUBLIC_URL</code>.</p>' : ""}
      <div style="display:flex;gap:8px"><button class="p-btn primary" id="epSave">Save</button>
      <button class="p-btn" id="epCopy">Copy webhook URL</button>
      ${ep.status === "active" || k.apiKey ? '<button class="p-btn danger" id="epDisconnect">Disconnect</button>' : ""}</div>
    </div></div>`;
}
async function vProviders() {
  const { custom, availability } = await api("/platform/custom-providers");
  const { providerKinds } = await api("/meta");
  const [pay, ship, not] = await Promise.all([api("/meta/entity/provider_def"), api("/meta/entity/country")]);
  const byCountry = {};
  availability.forEach(a => { (byCountry[a.provider_id] = byCountry[a.provider_id] || []).push(a.country_code); });
  const kindTable = (kind, title) => {
    const rows = pay.rows.filter(x => x.kind === kind);
    return `<div class="p-panel"><h2>${title} (${rows.length})</h2>
      <table class="p-table"><thead><tr><th></th><th>Provider</th><th>Countries (availability relation)</th><th>Methods</th><th class="num">Fee</th><th></th></tr></thead>
      <tbody>${rows.map(p => `<tr><td class="t-emoji">${esc(p.emoji)}</td><td><b>${esc(p.name)}</b><br><span class="p-tag">${esc(p.description || "")}</span></td>
        <td class="p-tag">${(byCountry[p.id] || []).length >= 13 ? "🌍 global · " + (byCountry[p.id] || []).length : esc((byCountry[p.id] || []).join(" "))}</td>
        <td class="p-tag">${esc((JSON.parse(p.methods || "[]")).join(", "))}</td><td class="num">${p.fee_pct}%</td>
        <td style="white-space:nowrap"><button class="p-btn sm" data-pedit="${p.id}">Edit</button>
        <button class="p-btn sm" data-pavail="${p.id}">Countries</button></td></tr>`).join("")}</tbody></table></div>`;
  };
  return `
  <p class="p-tag" style="margin:0 0 14px">Provider catalogue is entity data — provider_def + provider_availability (countries) + country + tax_mode. Edit here or via the entity APIs; every storefront and checkout reads these live.</p>
  ${await vCarrierAccounts()}
  ${kindTable("payment", "Payment providers")}
  <div class="p-grid2">${kindTable("shipping", "Shipping carriers")}${kindTable("notification", "Notification channels")}</div>
  <div class="p-panel"><h2>Custom providers (${custom.length})</h2>
    <table class="p-table"><thead><tr><th>Kind</th><th>ID</th><th>Name</th><th></th></tr></thead>
    <tbody>${custom.map(c => { const m = JSON.parse(c.manifest); return `<tr><td>${esc(c.kind)}</td><td>${esc(m.id)}</td><td>${esc(m.name)}</td><td><button class="p-btn sm danger" data-delprov="${c.id}">✕</button></td></tr>`; }).join("") || '<tr><td colspan="4" class="p-empty">None</td></tr>'}</tbody></table>
    <h2 style="margin-top:18px">Register a new provider</h2>
    <p class="p-tag">Fill in the form below to register a provider. ID is auto-generated.</p>
    <div class="p-form">
      <div class="row"><label><span>Kind</span><select id="cpKind">${(providerKinds || []).map(k => `<option>${esc(k)}</option>`).join("")}</select></label>
      <label><span>ID (auto)</span><input id="cpId" placeholder="Auto-generated UUID" readonly style="background:var(--p-bg)"></label>
      <label><span>Name (required)</span><input id="cpName" placeholder="e.g. My Payment Gateway"></label>
      <label><span>Emoji</span><input id="cpEmoji" placeholder="🔌" value="🔌"></label></div>
      <div class="row"><label><span>Description</span><input id="cpDesc" placeholder="Short description of what this provider does"></label></div>
      <div class="row"><label><span>Countries</span><input id="cpCountries" placeholder="* for all, or comma-separated codes (e.g. US,IN,CN)"></label>
      <label><span>Fee %</span><input id="cpFeePct" type="number" step="0.1" value="0"></label>
      <label><span>Fee (fixed)</span><input id="cpFeeFixed" type="number" step="0.01" value="0"></label></div>
      <div class="row"><label><span>Methods</span><input id="cpMethods" placeholder="Comma-separated (e.g. card,upi,netbanking)"></label>
      <button class="p-btn sm" id="cpAddField">+ Add credential field</button></div>
      <div id="cpFieldsContainer"></div>
      <button class="p-btn primary" id="cpSave">Register provider</button>
      <div id="cpError" class="p-tag" style="display:none;background:var(--p-red);color:#fff"></div>
    </div></div>`;
}
 async function vUCII() {
  const [caps, domains, policies, workflows, configs, entityTypes] = await Promise.all([
    api("/ucii/capabilities"),
    api("/ucii/domains"),
    api("/ucii/policies"),
    api("/ucii/workflows"),
    api("/ucii/config", "GET", { scope: "platform" }),
    api("/meta/entity-def")
  ]);
  
  const configCategories = {
    'identity': ['sso', 'mfa', 'auth'],
    'commerce': ['product', 'cart', 'order', 'payment'],
    'integrations': ['payments', 'shipping', 'tax']
  };
  
  const configByCategory = Object.fromEntries(
    Object.entries(configCategories).map(([cat, keys]) => [
      cat, 
      configs.config ? Object.keys(configs.config).filter(k => keys.some(key => k.includes(key))) : []
    ])
  );
  
  return `
  <div class="p-panel"><h2>UCII Ω∞ Registry</h2>
    <p class="p-tag">Zero duplicates, zero overlapping, zero gaps through registry-first design.</p>
    
    <div style="margin-top:14px">
      <h3>🧩 Capabilities</h3>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;margin:8px 0">
        ${caps.capabilities.map(c => `
          <div class="p-card" style="padding:12px">
            <div style="display:flex;justify-content:space-between;align-items:center">
              <div>
                <b>${esc(c.name)}</b>
                <div class="p-tag" style="font-size:12px">${esc(c.category || 'uncategorized')}</div>
              </div>
              <span class="badge ${esc(c.status)}">${esc(c.status)}</span>
            </div>
          </div>
        `).join('') || '<p class="p-tag">No capabilities defined.</p>'}
      </div>
      <button class="p-btn sm" data-action="newCap">+ New Capability</button>
    </div>
    
    <div style="margin-top:14px">
      <h3>🌐 Domains</h3>
      <div style="display:flex;gap:10px;flex-wrap:wrap;margin:8px 0">
        ${domains.domains.map(d => `
          <div class="p-tag" style="padding:8px 12px"><b>${esc(d.name)}</b></div>
        `).join('') || '<p class="p-tag">No domains defined.</p>'}
      </div>
      <button class="p-btn sm" data-action="newDomain">+ New Domain</button>
    </div>
    
    <div style="margin-top:14px">
      <h3>📜 Configuration</h3>
      ${Object.entries(configByCategory).map(([cat, items]) => `
        <div style="margin:10px 0">
          <h4 style="margin:0 0 5px">${esc(cat)}</h4>
          <div style="display:flex;gap:8px;flex-wrap:wrap">
            ${items.map(k => `<div class="p-tag" style="font-size:12px">${esc(k)}</div>`).join('') || '<span class="p-tag">No config</span>'}
          </div>
        </div>
      `).join('')}
    </div>
    
    <div style="margin-top:14px">
      <h3>📋 Entity Schemas</h3>
      <div style="display:flex;gap:10px;flex-wrap:wrap;margin:8px 0">
        ${(entityTypes.rows || []).map(e => `
          <div class="p-tag" style="padding:8px 12px">
            <b>${esc(e.key)}</b>
            <div class="p-tag" style="font-size:12px">${e.isBuiltIn ? 'Built-in' : 'Custom'}</div>
          </div>
        `).join('') || '<p class="p-tag">No entity schemas.</p>'}
      </div>
    </div>
    
    <div style="margin-top:14px">
      <h3>⚙️ Workflows & Policies</h3>
      <div style="display:flex;gap:20px;margin:8px 0">
        <div>
          <div class="p-tag"><b>${workflows.workflows.length}</b> workflows</div>
          <button class="p-btn sm" data-action="newWorkflow">+ New</button>
        </div>
        <div>
          <div class="p-tag"><b>${policies.policies.length}</b> policies</div>
          <button class="p-btn sm" data-action="newPolicy">+ New</button>
        </div>
      </div>
    </div>
  </div>`;
}
 async function vStudio(preset) {
  const tenants = await api("/platform/tenants");
  const { rows: entityDefs } = await api("/meta/entity-def");
  const entities = entityDefs.map(e => ({ ...e, ...JSON.parse(e.def || "{}") }));
  /* a universe's Records button passes the entity to open — mark it selected in the
     markup itself so nothing has to mutate the freshly-parsed DOM to preselect it */
  const sel = (preset && entities.some(e => e.key === preset)) ? preset : (entities[0] && entities[0].key);
  return `
  <div class="p-panel"><h2>Platform Data Studio</h2>
    <p class="p-tag">Browse all entity data across all stores.</p>
    <div style="margin:14px 0">
      <label><span>Store</span><select id="studioTenant">${tenants.tenants.map(t => `<option value="${t.id}">${esc(t.name)} (${esc(t.slug)})</option>`).join("")}</select></label>
      <label><span>Entity</span><select id="studioEntity">${entities.map(e => `<option value="${esc(e.key)}" ${e.key === sel ? "selected" : ""}>${esc(e.label)}</option>`).join("")}</select></label>
      <button class="p-btn primary" id="studioLoad">Load</button>
    </div>
    <div id="studioBody"></div>
  </div>`;
 }
 async function vDefinitions() {
  const data = await api("/meta/entity-def");
  const rows = data.rows || [];
  const defs = rows.map(e => ({ 
    ...e, 
    ...JSON.parse(e.def || "{}"),
    isBuiltIn: e.isBuiltIn
  }));
  const tenants = await api("/platform/tenants");
  return `
  <div class="p-panel"><h2>Global Entity Definitions</h2>
    <p class="p-tag">Built-in entities (read-only) + custom entities you define. Stores only use what Platform enables.</p>
    <div style="display:flex;gap:10px;margin-bottom:14px">
      <button class="p-btn primary" id="newDef">+ Define Custom Entity</button>
    </div>
    <div class="p-scroll-x">
      <table class="p-table">
         <thead><tr><th>Key</th><th>Label</th><th>Icon</th><th>Enabled For</th><th></th></tr></thead>
         <tbody>${defs.map(e => {
           const enabledTenants = (tenants.tenants || []).filter(t => t.custom_entities && t.custom_entities.includes(e.key));
           if (e.isBuiltIn) {
             return `<tr><td><b>${esc(e.key)}</b><span class="p-tag" style="margin-left:8px">Built-in</span></td><td>${esc(e.label)}</td><td>${esc(e.icon)}</td><td><span class="p-tag">N/A</span></td><td><span class="p-tag">Read-only</span></td></tr>`;
           }
           const allTenants = (tenants.tenants || []).map(t => ({
             ...t,
             enabled: enabledTenants.some(et => et.id === t.id)
           }));
           const toggleBtns = allTenants.map(t => 
             `<button class="p-btn sm ${t.enabled ? 'primary' : ''}" data-toggle-entity="${e.key}" data-tenant="${t.id}">${t.enabled ? '✕' : '+'}</button>`
           ).join(" ");
           return `<tr><td><b>${esc(e.key)}</b></td><td>${esc(e.label)}</td><td>${esc(e.icon)}</td><td>${enabledTenants.length > 0 ? enabledTenants.map(t => `<span class="badge">${esc(t.slug)}</span>`).join(" ") : '<span class="p-tag">None</span>'}</td><td>${toggleBtns} <button class="p-btn sm" data-edit="${e.key}">Edit</button></td></tr>`;
         }).join("")}</tbody>
      </table>
    </div>
    <div class="p-modal" id="defModal" style="display:none">
      <div class="p-modal-box">
        <h3 id="defTitle">Define Entity</h3>
        <div class="p-form">
          <div class="row">
            <label><span>Key</span><input id="defKey" placeholder="service_contract"></label>
            <label><span>Label</span><input id="defLabel" placeholder="Service Contracts"></label>
          </div>
          <label><span>Icon</span><input id="defIcon" placeholder="🧾"></label>
          <label><span>Fields (JSON array)</span><textarea id="defFields" rows="5">[
  {"key":"name","label":"Name","type":"text","required":true},
  {"key":"value","label":"Value","type":"money"}
]</textarea></label>
          <div style="display:flex;gap:10px;margin-top:8px">
            <button class="p-btn primary" id="saveDef">Save</button>
            <button class="p-btn" id="cancelDef">Cancel</button>
          </div>
        </div>
      </div>
    </div>
  </div>`;
}
async function vGeo() {
  const [cs, tm, pv, cy, fx, rules] = await Promise.all([api("/meta/entity/country"), api("/meta/entity/tax_mode"), api("/meta/entity/provider_availability"), api("/meta/entity/currency"), api("/platform/fx"), api("/meta/entity/taxRules")]);
  P.fx = fx;
  const cnt = {}; pv.rows.forEach(r => cnt[r.provider_id] = (cnt[r.provider_id] || 0) + 1);
  /* tax is owned by the tax engine, so a country's rate is looked up from the engine's own
     registry (taxRules) — never read off the country row, which would show a stale second copy
     that drifts the moment an operator edits the rule */
  const ruleOf = {};
  for (const r of ((rules && rules.rows) || [])) ruleOf[r.country] = r;
  const taxCell = code => { const r = ruleOf[code]; if (!r) return '<span class="p-tag">no rule</span>'; return `<span class="badge published">${esc(r.mode)}</span>`; };
  const rateCell = code => { const r = ruleOf[code]; const v = r && Number(r.standard); return (v != null && v > 0) ? (v * 100).toFixed(2) + "%" : '<span class="p-tag">store rate</span>'; };
  return `
  <div class="p-panel"><h2>Countries &amp; currencies (entity: country)</h2>
    <p class="p-tag">Storefronts derive currency, symbol, locale and decimals from these rows. Tax is owned by the tax engine (taxRules), not the country — add a country and it instantly appears in every store's settings and provider availability.</p>
    <div class="p-scroll-x"><table class="p-table"><thead><tr><th>Code</th><th>Name</th><th>Currency</th><th>Symbol</th><th>Locale</th><th class="num">Decimals</th><th>Tax mode <em class="p-tag">(from taxRules)</em></th><th class="num">Rate</th><th class="num">Providers</th></tr></thead>
    <tbody>${cs.rows.map(c => `<tr><td><b>${esc(c.code)}</b></td><td>${esc(c.name)}</td><td>${esc(c.currency)}</td><td class="t-emoji" style="font-size:16px">${esc(c.symbol)}</td><td class="p-tag">${esc(c.locale)}</td><td class="num">${c.decimals}</td><td>${taxCell(c.code)}</td><td class="num">${rateCell(c.code)}</td><td class="num">${new Set(pv.rows.filter(x => x.country_code === c.code).map(x => x.provider_id)).size}</td></tr>`).join("")}</tbody></table></div>
    <button class="p-btn primary sm" id="addCountry">+ Add country</button></div>
  <div class="p-panel"><h2>Currencies &amp; FX (entity: currency)</h2>
    <p class="p-tag">Jurisdiction sets the default; stores may override to any currency here — storefront prices, cart and checkout totals convert at these rates and snapshot them per order.</p>
    <div class="p-scroll-x"><table class="p-table"><thead><tr><th>Code</th><th>Name</th><th>Symbol</th><th class="num">Decimals</th><th class="num">1 unit = USD</th><th>Countries</th><th></th></tr></thead>
    <tbody>${cy.rows.map(x => `<tr><td><b>${esc(x.code)}</b></td><td>${esc(x.name)}</td><td class="t-emoji" style="font-size:15px">${esc(x.symbol)}</td><td class="num">${x.decimals}</td><td class="num">${x.usd}</td>
      <td class="p-tag">${cs.rows.filter(c => c.currency === x.code).map(c => c.code).join(" ") || "—"}</td>
      <td style="white-space:nowrap"><button class="p-btn sm" data-cedit="${esc(x.code)}">Edit</button> <button class="p-btn sm danger" data-cdel="${esc(x.code)}">✕</button></td></tr>`).join("")}</tbody></table></div>
    <button class="p-btn primary sm" id="addCur">+ Add currency</button></div>
  <div class="p-panel"><h2>Conversions &amp; FX feed</h2>
    <div class="row3" style="display:grid;grid-template-columns:1fr 2fr auto;gap:12px;align-items:end">
      <label><span>Rate source</span><select id="fxProv"><option value="manual" ${(fx.provider.provider||"manual")==="manual"?"selected":""}>Manual (offline)</option><option value="feed" ${fx.provider.provider==="feed"?"selected":""}>HTTP JSON feed</option></select></label>
      <label><span>Feed URL — JSON of {"CODE": usdValue}</span><input id="fxUrl" value="${esc(fx.provider.url||"")}" placeholder="https://your-fx-provider.example/rates.json"></label>
      <span><button class="p-btn sm" id="fxProvSave">Save</button> <button class="p-btn sm primary" id="fxSync">⟳ Sync now</button></span></div>
    <p class="p-tag">Last sync: ${fx.lastSync ? esc(fx.lastSync.at)+" — applied "+fx.lastSync.applied.length+(fx.lastSync.skipped.length?" skipped "+fx.lastSync.skipped.join(","):"") : "never"} · USD is always the 1.0 anchor.</p>
    <details style="margin:10px 0"><summary class="p-tag" style="cursor:pointer">Bulk update rates (manual)</summary>
      <textarea id="fxBulk" rows="4" style="width:100%;background:var(--p-bg);border:1px solid var(--p-line);border-radius:10px;color:var(--p-text);padding:10px;font-family:monospace">{ "EUR": 1.08, "GBP": 1.27, "INR": 0.012 }</textarea>
      <button class="p-btn sm primary" id="fxBulkGo">Apply rates</button></details>
    <div class="row3" style="display:grid;grid-template-columns:1fr 1fr 1fr auto;gap:10px;align-items:end;margin-bottom:10px">
      <label><span>Convert amount</span><input id="cxAmount" type="number" step="any" value="100"></label>
      <label><span>From</span><select id="cxFrom">${cy.rows.map(x => `<option>${x.code}</option>`).join("")}</select></label>
      <label><span>To</span><select id="cxTo">${cy.rows.map(x => `<option value="${x.code}" ${x.code==="INR"?"selected":""}>${x.code}</option>`).join("")}</select></label>
      <button class="p-btn sm" id="cxGo">Convert →</button><div class="p-tag" id="cxOut"></div></div>
    <table class="p-table"><thead><tr><th>When</th><th>Currency</th><th class="num">USD value</th><th>Source</th><th>Detail</th></tr></thead>
    <tbody>${fx.history.slice(0, 25).map(h => `<tr><td class="p-tag">${esc(h.created_at)}</td><td><b>${esc(h.currency)}</b></td><td class="num">${h.usd}</td><td><span class="badge ${h.source==="feed"?"published":"draft"}">${esc(h.source)}</span></td><td class="p-tag">${esc((h.note||"").slice(0,48))}</td></tr>`).join("") || '<tr><td colspan="5" class="p-empty">No rate changes recorded yet — edit a rate or sync a feed</td></tr>'}</tbody></table></div>
  <div class="p-panel"><h2>Tax modes (entity: tax_mode)</h2>
    <table class="p-table"><thead><tr><th>Key</th><th>Label</th><th>Description</th><th></th></tr></thead>
    <tbody>${tm.rows.map(t => `<tr><td><b>${esc(t.key)}</b></td><td>${esc(t.label)}</td><td class="p-tag">${esc(t.description || "")}</td><td><span class="p-tag">${tm.rows.filter(x => x.tax_mode === t.key).length ? "" : ""}</span></td></tr>`).join("")}</tbody></table>
    <button class="p-btn primary sm" id="addTax">+ Add tax mode</button></div>`;
}
async function wireGeoFx() {
  const d = document;
  const g = id => d.getElementById(id);
  if (!g("fxSync")) return;
  g("fxProvSave").onclick = async () => { try { await api("/platform/fx/provider", "PUT", { provider: g("fxProv").value, url: g("fxUrl").value }); toast("FX provider saved"); render(); } catch (e) { toast(e.message); } };
  g("fxSync").onclick = async () => { try { const r = await api("/platform/fx/sync", "POST", {}); toast("Synced " + r.applied.length + " rates" + (r.skipped.length ? " (skipped " + r.skipped.join(",") + ")" : "")); render(); } catch (e) { toast(e.message); } };
  const bg = g("fxBulkGo"); if (bg) bg.onclick = async () => { try { const rates = JSON.parse(g("fxBulk").value); const r = await api("/platform/fx/rates", "POST", { rates, note: "platform bulk" }); toast("Applied " + r.applied.length + (r.skipped.length ? ", skipped " + r.skipped.join(",") : "")); render(); } catch (e) { toast(e.message); } };
  g("cxGo").onclick = async () => { try { const r = await api("/fx?amount=" + encodeURIComponent(g("cxAmount").value || 1) + "&from=" + g("cxFrom").value + "&to=" + g("cxTo").value); g("cxOut").textContent = `= ${r.result.toLocaleString()} ${r.to} (rate ${r.rate})`; } catch (e) { g("cxOut").textContent = e.message; } };
}
/* ============ GLOBAL PRODUCTS: platform-level master catalog tenants subscribe to ============ */
let gpFilter = "", gpUniverse = "", gpUniverses = [], gpKinds = [], gpTaxClasses = [], gpCategories = [], gpProfileFields = [];
/* universe → product type, from the registry's own map (universeProductTypes) — the form
   shows the type as a consequence of the universe instead of a checkbox that can
   contradict it. Filled once from the list response. */
let gpTypeMap = null;
function universeTypeMap() {
  if (gpTypeMap) return gpTypeMap;
  const rows = (window.__universeProductTypes || []);
  gpTypeMap = Object.fromEntries(rows.map(r => [r.key, r.type]));
  return gpTypeMap;
}
async function vGproducts() {
  const q = new URLSearchParams();
  if (gpFilter) q.set("category", gpFilter);
  if (gpUniverse) q.set("universe", gpUniverse);
  const { products, universes, kinds, taxClasses, categories, universeProductTypes, profileFields } = await api("/platform/global-products" + (q.toString() ? "?" + q.toString() : ""));
  gpUniverses = universes || [];
  gpKinds = kinds || [];
  gpTaxClasses = taxClasses || [];
  gpCategories = categories || [];
  gpProfileFields = profileFields || [];
  gpTypeMap = null; window.__universeProductTypes = universeProductTypes || [];
  const cats = [...new Set(products.map(p => p.category).filter(Boolean))];
  const uOf = p => (gpUniverses.find(u => u.key === p.universe) || {});
  return `
  <div class="p-panel"><div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;flex-wrap:wrap">
    <h2 style="margin:0">Global Products (${products.length})</h2>
    <select id="gpCat" style="padding:6px 10px;border:1px solid var(--p-border);border-radius:8px;background:var(--p-bg)">
      <option value="">All categories</option>${cats.map(c => `<option value="${esc(c)}" ${c === gpFilter ? "selected" : ""}>${esc(c)}</option>`).join("")}
    </select>
    <select id="gpUniv" style="padding:6px 10px;border:1px solid var(--p-border);border-radius:8px;background:var(--p-bg)" title="The product universes the constitution declares (UPIP §1 VISION)">
      <option value="">All universes</option>${gpUniverses.map(u => `<option value="${esc(u.key)}" ${u.key === gpUniverse ? "selected" : ""}>${esc(u.icon || "🧩")} ${esc(u.name)}</option>`).join("")}
    </select>
    <span style="flex:1"></span>
    <button class="p-btn primary sm" id="gpNew">+ New global product</button></div>
    <p style="margin:0 0 14px;color:var(--p-muted);font-size:13px">Platform-level master products, populated <b>automatically</b> from the corpus (one canonical archetype per universe UPIP §1 declares) and <b>manually</b> by you. Stores may import one into their own catalogue only when you permit it — <b>Store access</b> below is that gate (the "if the Global Platform permits" clause, as data).</p>
    <div class="p-scroll-x"><table class="p-table"><thead><tr><th>SKU</th><th>Name</th><th>Category</th><th>Universe</th><th class="num">Price</th><th>Tax class</th><th>Type</th><th>Status</th><th>Store access</th><th></th></tr></thead>
    <tbody>${products.map(p => `<tr><td><b>${esc(p.sku)}</b></td><td>${esc(p.name)}</td><td class="p-tag">${esc(p.category || "—")}</td>
      <td><span title="${esc(p.universe || "physical_products")}">${esc(uOf(p).icon || "🧩")} ${esc(uOf(p).name || p.universe)}</span></td>
      <td class="num">${money(p.price)}</td><td>${esc(p.tax_class)}</td><td>${esc(universeTypeMap()[p.universe] || (p.is_service ? "service" : "physical"))}</td>
      <td><span class="badge ${esc(p.status)}">${esc(p.status)}</span></td>
      <td><button class="p-btn sm" data-gpacc="${p.id}" title="Grant or revoke which stores may list this product">${(p.permissions || []).length} store${(p.permissions || []).length === 1 ? "" : "s"}</button></td>
      <td style="white-space:nowrap"><button class="p-btn sm" data-gpedit="${p.id}">Edit</button>
        <button class="p-btn sm danger" data-gpdel="${p.id}">✕</button></td></tr>`).join("") || '<tr><td colspan="10" class="p-empty">No global products yet</td></tr>'}</tbody></table></div></div>`;
}
function wireGproducts() {
  const cat = document.getElementById("gpCat");
  if (cat) cat.onchange = () => { gpFilter = cat.value; render(); };
  const univ = document.getElementById("gpUniv");
  if (univ) univ.onchange = () => { gpUniverse = univ.value; render(); };
  document.getElementById("gpNew").onclick = () => gpModal(null);
  $$("[data-gpedit]").forEach(b => b.onclick = () => {
    api("/platform/global-products").then(({ products, universes, kinds, taxClasses, categories, universeProductTypes, profileFields }) => {
      gpUniverses = universes || [];
      gpKinds = kinds || [];
      gpTaxClasses = taxClasses || [];
      gpCategories = categories || [];
      gpProfileFields = profileFields || [];
      gpTypeMap = null; window.__universeProductTypes = universeProductTypes || [];
      const p = products.find(x => String(x.id) === b.dataset.gpedit);
      if (p) gpModal(p);
    }).catch(e => toast(e.message));
  });
  $$("[data-gpdel]").forEach(b => b.onclick = async () => {
    if (!confirm("Delete this global product?")) return;
    try { await api("/platform/global-products/" + b.dataset.gpdel, "DELETE", {}); toast("Deleted"); render(); }
    catch (e) { toast(e.message); }
  });
  $$("[data-gpacc]").forEach(b => b.onclick = async () => {
    try { gpAccessModal(b.dataset.gpacc); } catch (e) { toast(e.message); }
  });
}
/* the platform side of "if the Global Platform permits": grant or revoke a store's
   access to list a global product. Pure data — one store_product_config row — and the
   store console reads the consequence on its next render, never a code deployment. */
async function gpAccessModal(productId) {
  const [{ products }, { tenants }] = await Promise.all([
    api("/platform/global-products"), api("/platform/tenants")]);
  const p = products.find(x => String(x.id) === String(productId));
  if (!p) return toast("Product not found");
  const perms = (p.permissions || []);
  const m = modal(`
    <h3 style="margin:0 0 6px">Store access — ${esc(p.name)}</h3>
    <p style="margin:0 0 14px;color:var(--p-muted);font-size:13px">A store admin can import this product into their catalogue only when granted <b>list</b> or <b>sell</b> below. Read-only lets them see it; revoking removes the grant (already-listed copies stay, as the merchant's own data).</p>
    <div class="p-scroll-x" style="max-height:46vh;overflow:auto"><table class="p-table"><thead><tr><th>Store</th><th>Permission</th><th></th></tr></thead>
    <tbody>${(tenants || []).map(t => {
      const row = perms.find(x => Number(x.tenant_id) === Number(t.id));
      return `<tr><td><b>${esc(t.name)}</b> <span style="color:var(--p-muted);font-size:12px">${esc(t.slug)}</span></td>
        <td><select data-accsel="${t.id}" style="padding:4px 8px;border:1px solid var(--p-border);border-radius:6px;background:var(--p-bg)">
          ${["none", "read", "list", "sell"].map(l => `<option value="${l}" ${row ? (row.permissions === l ? "selected" : "") : (l === "none" ? "selected" : "")}>${l}</option>`).join("")}
        </select></td>
        <td>${row ? '<span class="badge active">granted</span>' : '<span class="badge">—</span>'}</td></tr>`;
    }).join("") || '<tr><td colspan="3" class="p-empty">No stores provisioned</td></tr>'}</tbody></table></div>
    <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:14px">
      <button class="p-btn" id="gpaCancel">Close</button></div>`);
  m.querySelector("#gpaCancel").onclick = () => { m.innerHTML = ""; };
  m.querySelectorAll("[data-accsel]").forEach(sel => sel.onchange = async () => {
    const tenantId = sel.dataset.accsel, level = sel.value;
    try {
      if (level === "none") await api("/platform/store-product-config/" + tenantId + "/" + productId, "DELETE", {});
      else await api("/platform/store-product-config", "POST", { tenant_id: Number(tenantId), global_product_id: Number(productId), permissions: level, enabled: 1 });
      toast(level === "none" ? "Access revoked" : "Granted " + level);
      m.innerHTML = ""; render();
    } catch (e) { toast(e.message); }
  });
}
/* the product form adapts to the universe the operator picks: the corpus declares the
   configuration fields for each universe (lib/api.js::apiUniverseFields reads them
   structurally), so "Insurance" shows insurance's fields and "Streaming" shows
   streaming's — no per-industry form code anywhere. `draft` carries values across a
   universe switch so nothing an operator typed is lost. */
/* harvest the visible profile fields; a JSON block that won't parse rides along raw —
   the save handler re-parses and reports the error to the operator */
function collectProfile(m) {
  const out = {};
  m.querySelectorAll("[data-pf]").forEach(el => {
    const k = el.dataset.pf;
    if (el.dataset.pfjson) { try { out[k] = JSON.parse(el.value); } catch (e) { out[k] = el.value; } }
    else out[k] = el.value;
  });
  return out;
}
async function gpModal(p, draft = {}) {
  const isEdit = !!p;
  const universe = draft.universe || (p ? p.universe : "physical_products");
  const attrs = Object.assign({}, p ? (p.attributes || {}) : {}, draft.attrs || {});
  const media = (p ? (p.media || []) : []).concat(draft.media || []);
  /* the platform authors the WHOLE product: `profile` carries every authorable field of
     the store product (declared once, in the products entity, and shipped by the API as
     profileFields — so this form can never offer a field the validator would refuse) */
  const prof = Object.assign({}, p ? (p.profile || {}) : {}, draft.profile || {});
  const pfScalar = (gpProfileFields || []).filter(f => f.type !== "json");
  const pfJson = (gpProfileFields || []).filter(f => f.type === "json");
  const pfVal = f => { const v = prof[f.key]; return v == null ? "" : (typeof v === "string" ? v : JSON.stringify(v, null, 1)); };
  const pfScalarHtml = pfScalar.map(f => {
    const isNum = f.type === "number" || f.type === "money";
    return `<label><span>${esc(f.label)}</span><input data-pf="${esc(f.key)}" ${isNum ? 'type="number" step="any"' : 'type="text"'} value="${esc(f.type === "number" || f.type === "money" ? (pfVal(f) === "" ? "" : pfVal(f)) : pfVal(f))}"></label>`;
  }).join("");
  const pfJsonHtml = pfJson.map(f => `<label><span>${esc(f.label)}</span><textarea data-pf="${esc(f.key)}" data-pfjson="1" rows="3" placeholder="{} or []">${esc(pfVal(f))}</textarea>${f.hint ? `<small class="medit-hint">${esc(f.hint)}</small>` : ""}</label>`).join("");
  let fields = [];
  try { fields = (await api("/platform/universe-fields/" + encodeURIComponent(universe))).fields || []; }
  catch (e) { /* unknown universe → no declared configuration, the editor still works */ }
  const uName = (gpUniverses.find(u => u.key === universe) || {}).name || universe;
  const declaredKeys = new Set(fields.map(f => f.key));
  const customAttrs = Object.fromEntries(Object.entries(attrs).filter(([k]) => !declaredKeys.has(k)));
  const typeMap = universeTypeMap();
  const catVal = draft.category != null ? draft.category : (p ? p.category : "");
  const taxVal = draft.tax_class != null ? draft.tax_class : (p ? p.tax_class : "standard");
  const typeName = typeMap[universe] || "service";
  const m = modal(`
    <h3 style="margin:0 0 14px">${isEdit ? "Edit" : "New"} global product</h3>
    <div class="p-form" style="display:grid;gap:10px">
      <label><span>SKU *</span><input id="gpSku" value="${esc(draft.sku != null ? draft.sku : (p ? p.sku : ""))}" placeholder="e.g. GPU-001"></label>
      <label><span>Name *</span><input id="gpName" value="${esc(draft.name != null ? draft.name : (p ? p.name : ""))}"></label>
      <label><span>Description</span><textarea id="gpDesc" rows="2">${esc(draft.description != null ? draft.description : (p ? p.description : ""))}</textarea></label>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px">
        <label><span>Category</span><select id="gpCatSel">${gpCategories.map(c => `<option value="${esc(c.key)}" ${catVal === c.key ? "selected" : ""}>${c.icon ? esc(c.icon) + " " : ""}${esc(c.name)}</option>`).join("")}</select></label>
        <label><span>Price</span><input id="gpPrice" type="number" step="0.01" min="0" value="${draft.price != null ? draft.price : (p ? p.price : 0)}"></label>
        <label><span>Tax class</span><select id="gpTax">${gpTaxClasses.map(t => `<option value="${esc(t.key)}" ${taxVal === t.key ? "selected" : ""}>${esc(t.name)}</option>`).join("")}</select></label>
      </div>
      <label><span>Product universe</span><select id="gpUnivSel">${gpUniverses.map(u => `<option value="${esc(u.key)}" ${universe === u.key ? "selected" : ""}>${esc(u.icon || "🧩")} ${esc(u.name)}</option>`).join("")}</select>
        <small class="medit-hint">Sets the product's type and the configuration section below — the universe is the authority on both.</small></label>
      <div class="gp-derived"><span>Product type</span><b id="gpTypeBadge">${esc(typeName)}</b><small>· derived from the universe, never hand-set</small></div>
      <label><span>Status</span><select id="gpStatus">${["draft", "active", "retired"].map(s => `<option value="${s}" ${(draft.status != null ? draft.status : (p ? p.status : "draft")) === s ? "selected" : ""}>${s}</option>`).join("")}</select></label>
      <div class="gp-sec"><h4>Configuration <small>· declared by the ${esc(uName)} universe</small></h4>
        ${fields.length ? fields.map(f => `<label><span>${esc(f.label)}${f.required ? " *" : ""}</span>
          ${f.type === "select" ? `<select data-uf="${esc(f.key)}">${(f.options || []).map(o => `<option ${String(attrs[f.key] || "") === String(o) ? "selected" : ""}>${esc(o)}</option>`).join("")}</select>`
            : `<input data-uf="${esc(f.key)}" value="${esc(attrs[f.key] != null ? attrs[f.key] : "")}" ${f.required ? "required" : ""}>`}</label>`).join("")
          : '<p class="medit-hint">This universe declares no extra fields — the corpus keeps it open. Use custom attributes below.</p>'}</div>
      <div class="gp-sec"><h4>Store catalogue details <small>· what every importing store receives</small></h4>
        <p class="medit-hint">The platform defines the product completely — these are the store product's own fields, written onto the store row at import. The store keeps only its operations: stock, ratings, lifecycle and its sales copy.</p>
        <div class="row3" style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px">${pfScalarHtml}</div>
        ${pfJson.length ? `<details class="gp-deep"><summary>Deep configuration · ${pfJson.length} profile${pfJson.length === 1 ? "" : "s"}</summary><div class="gp-deep-grid">${pfJsonHtml}</div></details>` : ""}</div>
      <div class="gp-sec"><h4>Media <small>· images, videos, documents</small></h4><div id="gpMedia"></div></div>
      <div class="gp-sec"><h4>Custom attributes <small>· anything else shoppers should know</small></h4><div id="gpAttrs"></div></div>
      <div class="p-err hidden" id="gpErr" style="color:var(--p-red);font-size:13px"></div>
      <div style="display:flex;gap:10px;justify-content:flex-end">
        <button class="p-btn" id="gpCancel">Cancel</button>
        <button class="p-btn primary" id="gpSave">${isEdit ? "Save changes" : "Create product"}</button></div>
    </div>`);
  const getMedia = mediaEditor(m.querySelector("#gpMedia"), media, gpKinds);
  const getAttrs = kvEditor(m.querySelector("#gpAttrs"), customAttrs);
  m.querySelector("#gpUnivSel").onchange = e => {
    /* swap the configuration section to the new universe, preserving everything typed */
    const d = { sku: m.querySelector("#gpSku").value, name: m.querySelector("#gpName").value, description: m.querySelector("#gpDesc").value,
      category: m.querySelector("#gpCatSel").value, price: m.querySelector("#gpPrice").value, tax_class: m.querySelector("#gpTax").value,
      status: m.querySelector("#gpStatus").value, universe: e.target.value,
      attrs: Object.assign(getAttrs(), Object.fromEntries(Array.from(m.querySelectorAll("[data-uf]")).map(el => [el.dataset.uf, el.value]))),
      media: getMedia(), profile: collectProfile(m) };
    m.innerHTML = ""; gpModal(p, d);
  };
  m.querySelector("#gpCancel").onclick = () => { m.innerHTML = ""; };
  m.querySelector("#gpSave").onclick = async () => {
    const err = m.querySelector("#gpErr");
    const val = id => m.querySelector(id).value;
    if (!val("#gpSku").trim() || !val("#gpName").trim()) { err.textContent = "SKU and name are required"; err.classList.remove("hidden"); return; }
    const declared = {};
    m.querySelectorAll("[data-uf]").forEach(el => { declared[el.dataset.uf] = el.value; });
    /* the profile is the store product's full definition — invalid JSON is caught here so
      the operator fixes the field instead of the server rejecting the whole save */
    const profOut = {};
    let profErr = "";
    m.querySelectorAll("[data-pf]").forEach(el => {
      const k = el.dataset.pf, raw = String(el.value || "");
      if (el.dataset.pfjson) { if (!raw.trim()) return; try { profOut[k] = JSON.parse(raw); } catch (e) { profErr = k + " is not valid JSON"; } }
      else if (raw !== "") profOut[k] = raw;
    });
    if (profErr) { err.textContent = profErr; err.classList.remove("hidden"); return; }
    /* is_service is deliberately NOT in the body — the API derives it from the universe,
       so the record can never contradict its own archetype */
    const body = { sku: val("#gpSku").trim(), name: val("#gpName").trim(), description: val("#gpDesc"), category: val("#gpCatSel"),
      universe: val("#gpUnivSel"), price: Number(val("#gpPrice")) || 0, tax_class: val("#gpTax"),
      attributes: Object.assign(getAttrs(), declared), media: getMedia(), profile: profOut, status: val("#gpStatus") };
    try {
      if (isEdit) await api("/platform/global-products/" + p.id, "PUT", body);
      else await api("/platform/global-products", "POST", body);
      toast(isEdit ? "Product updated" : "Product created"); m.innerHTML = ""; render();
    } catch (e) { err.textContent = e.message; err.classList.remove("hidden"); }
  };
}
/* ============ MODULE MARKETPLACE: every capability is a purchasable product ============ */
async function vModules() {
  const { modules, installs, tenants } = await api("/platform/modules");
  P.mods = { modules, installs, tenants };
  const installedSet = new Set(installs.filter(i => i.status === "installed").map(i => i.tenant_id + "|" + i.module_id));
  const cats = {};
  modules.forEach(m => { (cats[m.category] = cats[m.category] || []).push(m); });
  return `
  <p class="p-tag" style="margin:0 0 14px">Modules are products: buying one creates a paid invoice (MOD-*) and applies its manifest — features, payment rails, catalog ranges, engine capabilities — instantly. Every store auto-purchases the free baselines (identity, gid, geo, cart, listing, checkout, seo, reco, billing).</p>
  ${Object.entries(cats).map(([cat, ms]) => `
  <div class="p-panel"><h2>${esc(cat)}</h2><div class="mod-grid">${ms.map(m => {
    const caps = (m.manifest.capabilities || []).join(", ");
    return `<div class="mod-card"><div class="mod-head"><b>${esc(m.name)}</b><span class="price">${m.price > 0 ? "$" + m.price : "free"}</span></div>
      <p class="p-tag">${esc(m.summary || "")}</p><p class="p-tag"><code>${esc(caps || m.id)}</code></p>
      <div class="mod-installs">${tenants.map(t => {
        const on = installedSet.has(t.id + "|" + m.id);
        return `<span class="mi ${on ? "on" : ""}" data-mod="${esc(m.id)}" data-tid="${t.id}" title="${esc(m.name)} → ${esc(t.name)}">${esc(t.slug)}</span>`;
      }).join("")}</div></div>`;
  }).join("")}</div></div>`).join("")}`;
}
async function wireModules() {
  document.querySelectorAll("[data-mod]").forEach(el => {
    el.onclick = async () => {
      const { modules, tenants } = P.mods;
      const m = modules.find(x => x.id === el.dataset.mod); const t = tenants.find(x => String(x.id) === el.dataset.tid);
      const installed = el.classList.contains("on");
      const fields = (m.manifest.fields || []);
      const mm = modal(`<div class="p-modal-head"><h3>${esc(m.name)} → ${esc(t.name)}</h3><button data-mclose>✕</button></div>
        <div class="p-form">
        ${installed ? `<p class="p-tag">${m.price > 0 ? "Purchased (invoice on record)." : "Baseline — auto-purchased at provisioning."}</p><button class="p-btn danger" id="mUn">Uninstall / disable</button>` :
          `<p class="p-tag">${m.price > 0 ? "Price: $" + m.price + " — a paid invoice will be created and marked collected." : "Free — installs instantly."}</p>
           ${fields.map(f => `<label><span>${esc(f.label || f.key)}</span><input data-cfg="${esc(f.key)}" placeholder="e.g. ${f.key === "requireLoginCheckout" ? "true" : "…"}"></label>`).join("")}
           <button class="p-btn primary" id="mBuy">Purchase & install</button>`}
        </div>`);
      if (installed) mm.querySelector("#mUn").onclick = async () => {
        try { await api("/platform/modules/" + encodeURIComponent(m.id) + "/uninstall", "POST", { tenant_id: t.id }); mm.innerHTML = ""; toast("Module disabled"); render(); } catch (e) { toast(e.message); }
      };
      else mm.querySelector("#mBuy").onclick = async () => {
        const cfg = {};
        mm.querySelectorAll("[data-cfg]").forEach(i => { if (i.value) cfg[i.dataset.cfg] = (i.value === "true" || i.value === "false") ? i.value === "true" : (isNaN(+i.value) ? i.value : +i.value); });
        try {
          const r = await api("/platform/modules/" + encodeURIComponent(m.id) + "/install", "POST", { tenant_id: t.id, config: cfg });
          mm.innerHTML = ""; toast(r.invoice ? "Installed · invoice " + r.invoice : "Installed"); render();
        } catch (e) { toast(e.message); }
      };
    };
  });
}

async function vMonitor() {
  const m = await api("/platform/monitor");
  const max = Math.max(1, ...m.series.map(x => x.req));
  return `
  <div class="p-cards">
    <div class="p-stat"><em>Total requests</em><b>${m.totals.req}</b><small>${m.totals.err} errors</small></div>
    <div class="p-stat"><em>Avg latency</em><b>${m.totals.avgMs}ms</b></div>
    <div class="p-stat"><em>Uptime</em><b>${Math.floor(m.system.uptimeSec / 60)}m</b></div>
    <div class="p-stat"><em>Memory</em><b>${m.system.rssMB}MB</b></div>
    <div class="p-stat"><em>DB size</em><b>${m.system.dbKB}KB</b></div>
  </div>
  <div class="p-panel"><h2>Live traffic · all tenants · last 30 min</h2>
    <div class="p-chart">${m.series.map(x => `<div class="bar" style="height:${Math.max(3, x.req / max * 100)}%" data-tip="${new Date(x.t).toLocaleTimeString()}: ${x.req}"></div>`).join("")}</div></div>
  <div class="p-grid2">
    <div class="p-panel"><h2>Top endpoints</h2><table class="p-table"><thead><tr><th>Endpoint</th><th class="num">Calls</th><th class="num">Err</th><th class="num">ms</th></tr></thead>
      <tbody>${m.endpoints.map(x => `<tr><td>${esc(x.endpoint)}</td><td class="num">${x.count}</td><td class="num">${x.err}</td><td class="num">${x.avgMs}</td></tr>`).join("")}</tbody></table></div>
    <div class="p-panel"><h2>Stores</h2><table class="p-table"><thead><tr><th>Slug</th><th>Name</th><th>Status</th></tr></thead>
      <tbody>${m.tenants.map(t => `<tr><td>${esc(t.slug)}</td><td>${esc(t.name)}</td><td><span class="badge ${esc(t.status)}">${esc(t.status)}</span></td></tr>`).join("")}</tbody></table></div>
  </div>`;
}
async function vAudit() {
  const { entries } = await api("/platform/audit");
  return `<div class="p-panel"><h2>Global audit trail</h2>
    <input class="p-search" placeholder="Filter…" id="auditQ" style="margin-bottom:12px">
    <div class="p-scroll-x"><table class="p-table" id="auditTbl"><thead><tr><th>When</th><th>Store</th><th>Actor</th><th>Action</th><th>Entity</th><th>Ref</th><th>Detail</th></tr></thead>
    <tbody>${entries.map(e => `<tr><td>${esc(e.created_at)}</td><td>${esc(e.tenant_id || "—")}</td><td>${esc(e.actor_type)} · ${esc(e.actor_name || "")}</td>
      <td><b>${esc(e.action)}</b></td><td>${esc(e.entity || "")}</td><td>${esc(e.entity_id || "")}</td><td class="p-tag">${esc((e.meta || "").slice(0, 80))}</td></tr>`).join("")}</tbody></table></div></div>`;
}

function modal(html) {
  let m = $("#modal");
  if (!m) { m = document.createElement("div"); m.id = "modal"; document.body.appendChild(m); }
  m.innerHTML = `<div class="p-modal"><div class="p-modal-box">${html}</div></div>`;
  m.querySelector(".p-modal").addEventListener("click", e => { if (e.target.classList.contains("p-modal")) m.innerHTML = ""; });
  return m;
}
document.addEventListener("click", async e => {
  try {
    const open = e.target.closest("[data-open]"), imp = e.target.closest("[data-imp]"), susp = e.target.closest("[data-susp]"),
      del = e.target.closest("[data-del]"), inv = e.target.closest("[data-inv]"), pay = e.target.closest("[data-payinv]"),
      editp = e.target.closest("[data-editplan]"), delprov = e.target.closest("[data-delprov]");
    if (open) window.open("/index.html?store=" + P.tenants.find(t => t.id == open.dataset.open).slug, "_blank");
    if (imp) { const r = await api(`/platform/tenants/${imp.dataset.imp}/impersonate`, "POST", {}); window.open(r.url, "_blank"); }
    if (susp) { const t = P.tenants.find(x => x.id == susp.dataset.susp); await api("/platform/tenants/" + t.id, "PUT", { status: t.status === "active" ? "suspended" : "active" }); render(); }
    if (del) { if (confirm("Delete store and ALL its data?")) { await api("/platform/tenants/" + del.dataset.del, "DELETE", {}); render(); } }
    if (inv) { await api(`/platform/tenants/${inv.dataset.inv}/invoice`, "POST", {}); toast("Invoice generated"); render(); }
    if (pay) {
      const m = modal(`<div class="p-modal-head"><h3>Collect invoice</h3><button data-mclose>✕</button></div>
        <div class="p-form"><label><span>Gateway</span><select id="payGw"><option>stripe</option><option>paypal</option><option>razorpay</option><option>adyen</option><option>bank</option></select></label>
        <button class="p-btn primary" id="payGo">Charge</button></div>`);
      m.querySelector("#payGo").onclick = async () => {
        const r = await api(`/platform/invoices/${pay.dataset.payinv}/pay`, "POST", { gateway: m.querySelector("#payGw").value });
        m.innerHTML = ""; toast("Paid · txn " + r.txn_ref); render();
      };
    }
    if (editp) {
      const p = P.plans.find(x => x.id == editp.dataset.editplan);
      const m = modal(`<div class="p-modal-head"><h3>${esc(p.name)}</h3><button data-mclose>✕</button></div>
        <div class="p-form"><div class="row"><label><span>Name</span><input id="plnName" value="${esc(p.name)}"></label><label><span>Price/mo</span><input id="plnPrice" type="number" step="any" value="${p.price_month}"></label></div>
        <div class="row"><label><span>Max products</span><input id="plnP" type="number" value="${p.max_products}"></label><label><span>Max orders/mo</span><input id="plnO" type="number" value="${p.max_orders_month}"></label></div>
        <button class="p-btn primary" id="plnSave">Save</button></div>`);
      m.querySelector("#plnSave").onclick = async () => {
        await api("/platform/plans/" + p.id, "PUT", { name: m.querySelector("#plnName").value, price_month: Number(m.querySelector("#plnPrice").value), max_products: Number(m.querySelector("#plnP").value), max_orders_month: Number(m.querySelector("#plnO").value) });
        m.innerHTML = ""; toast("Plan updated"); render();
      };
    }
    if (delprov) { await api("/platform/custom-providers/" + delprov.dataset.delprov, "DELETE", {}); render(); }
    if (e.target.id === "newTenant") return registerModal();
    const regopen = e.target.closest("[data-regopen]");
    if (regopen) return registryEditor(regopen.dataset.regopen);
    const edit = e.target.closest("[data-tedit]");
    if (edit) return tenantModal(Number(edit.dataset.tedit));
    if (e.target.id === "newPlan") {
      const mm = modal(`<div class="p-modal-head"><h3>New plan</h3><button data-mclose>✕</button></div>
        <div class="p-form"><div class="row"><label><span>Name</span><input id="npName"></label><label><span>Price/mo</span><input id="npPrice" type="number" step="any"></label></div>
        <div class="row"><label><span>Max products</span><input id="npP" type="number" value="500"></label><label><span>Max orders/mo</span><input id="npO" type="number" value="2000"></label></div>
        <button class="p-btn primary" id="npGo">Create</button></div>`);
      mm.querySelector("#npGo").onclick = async () => {
        await api("/platform/plans", "POST", { name: mm.querySelector("#npName").value, price_month: Number(mm.querySelector("#npPrice").value), max_products: Number(mm.querySelector("#npP").value), max_orders_month: Number(mm.querySelector("#npO").value) });
        mm.innerHTML = ""; toast("Plan created"); render();
      };
    }
    if (e.target.id === "newSub") {
      const [tenants, plans] = await Promise.all([api("/platform/tenants"), api("/platform/plans")]);
      const mm = modal(`<div class="p-modal-head"><h3>Assign plan</h3><button data-mclose>✕</button></div>
        <div class="p-form"><label><span>Store</span><select id="sbT">${tenants.tenants.map(t => `<option value="${t.id}">${esc(t.name)}</option>`).join("")}</select></label>
        <label><span>Plan</span><select id="sbP">${plans.plans.map(p => `<option value="${p.id}">${esc(p.name)}</option>`).join("")}</select></label>
        <button class="p-btn primary" id="sbGo">Assign</button></div>`);
      mm.querySelector("#sbGo").onclick = async () => {
        await api(`/platform/tenants/${mm.querySelector("#sbT").value}/subscribe`, "POST", { plan_id: Number(mm.querySelector("#sbP").value) });
        mm.innerHTML = ""; toast("Subscription updated"); render();
      };
    }
    const cpFields = [];
    function renderCpFields() {
      const container = $("#cpFieldsContainer");
      if (!container) return;
      container.innerHTML = cpFields.map((f, i) => `
        <div style="display:flex;gap:8px;align-items:flex-end;margin-top:8px">
          <input placeholder="Key" value="${esc(f.key)}" style="flex:1" data-cpfkey="${i}">
          <input placeholder="Label" value="${esc(f.label)}" style="flex:1" data-cpflabel="${i}">
          <label style="font-size:12px"><input type="checkbox" ${f.secret ? "checked" : ""} data-cpfsecret="${i}"> Secret</label>
          <button class="p-btn sm danger" data-cpfdel="${i}">✕</button>
        </div>`).join("");
      $$("[data-cpfdel]").forEach(b => b.onclick = () => { cpFields.splice(Number(b.dataset.cpfdel), 1); renderCpFields(); });
      $$("[data-cpfkey]").forEach(inp => inp.oninput = () => { cpFields[inp.dataset.cpfkey].key = inp.value; });
      $$("[data-cpflabel]").forEach(inp => inp.oninput = () => { cpFields[inp.dataset.cpflabel].label = inp.value; });
      $$("[data-cpfsecret]").forEach(inp => inp.onchange = () => { cpFields[inp.dataset.cpfsecret].secret = inp.checked; });
    }
    // UUID generator
    const uuid = () => crypto.randomUUID ? crypto.randomUUID() : ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g,c=>(c^crypto.getRandomValues(new Uint8Array(1))[0]&15>>c/4).toString(16));
    // Generate UUID for ID field
    if ($("#cpId")) $("#cpId").value = uuid();
    // Initialize with default field
    cpFields.push({key:"apiKey",label:"API Key",secret:true});
    renderCpFields();
    if ($("#cpAddField")) $("#cpAddField").onclick = () => { cpFields.push({key:"",label:"",secret:false}); renderCpFields(); };
    // Validate UUID
    const validateUUID = (id) => {
      if (!id) return { valid: false, error: "ID is required" };
      if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(id))
        return { valid: false, error: "ID must be a valid UUID format" };
      return { valid: true };
    };
    // Validate provider name
    const validateName = (name) => {
      if (!name) return { valid: false, error: "Name is required" };
      if (name.length < 3 || name.length > 100)
        return { valid: false, error: "Name must be 3-100 characters" };
      return { valid: true };
    };
    // Validate methods
    const validateMethods = (methods) => {
      if (!methods || methods.length === 0)
        return { valid: false, error: "At least one method is required" };
      for (let i = 0; i < methods.length; i++) {
        if (!/^[a-z0-9_]+$/.test(methods[i]))
          return { valid: false, error: `Method ${i+1} must be lowercase alphanumeric with underscores` };
        if (methods[i].length < 2 || methods[i].length > 50)
          return { valid: false, error: `Method ${i+1} must be 2-50 characters` };
      }
      return { valid: true };
    };
    // Validate credential fields
    const validateFields = (fields) => {
      if (fields.length === 0) return { valid: false, error: "At least one credential field is required" };
      const seenKeys = new Set();
      for (let i = 0; i < fields.length; i++) {
        const f = fields[i];
        if (!f.key) return { valid: false, error: `Field ${i+1} is missing key` };
        if (!f.label) return { valid: false, error: `Field ${i+1} is missing label` };
        if (!/^[a-zA-Z][a-zA-Z0-9]*$/.test(f.key))
          return { valid: false, error: `Field ${i+1} key must start with letter, alphanumeric only` };
        if (seenKeys.has(f.key))
          return { valid: false, error: `Duplicate field key: ${f.key}` };
        seenKeys.add(f.key);
      }
      return { valid: true };
    };
    if (e.target.id === "epSave") {
      const apiKey = $("#epKey").value.trim(), webhookSecret = $("#epSecret").value.trim();
      if (!apiKey && !webhookSecret) return toast("Enter the API key or the webhook secret to save", "error");
      if (apiKey && !/^EZ[AT]K/.test(apiKey) && !confirm("EasyPost keys start with EZAK (live) or EZTK (test). Save this key anyway?")) return;
      const r = await api("/shipping/providers/config", "POST", { provider_id: "easypost", config: { apiKey, webhookSecret } });
      toast(r.provider && r.provider.status === "active" ? "EasyPost connected — every store can rate and buy labels" : "Saved — add the API key to connect"); render();
    }
    if (e.target.id === "epCopy") { const h = $("#epHook"); h.select(); try { await navigator.clipboard.writeText(h.value); toast("Webhook URL copied"); } catch (x) { toast("Select the URL and copy it"); } }
    if (e.target.id === "epDisconnect") {
      if (!confirm("Disconnect EasyPost? The stored keys are deleted and no store can rate or buy labels until it is connected again.")) return;
      await api("/platform/shipping/providers/easypost/disconnect", "POST", {});
      toast("EasyPost disconnected"); render();
    }
    if (e.target.id === "cpSave") {
      const kind = $("#cpKind").value;
      const id = $("#cpId").value.trim();
      const name = $("#cpName").value.trim();
      const emoji = $("#cpEmoji").value.trim() || "🔌";
      const desc = $("#cpDesc").value.trim();
      const countries = $("#cpCountries").value.trim() || "*";
      const feePct = parseFloat($("#cpFeePct").value) || 0;
      const feeFixed = parseFloat($("#cpFeeFixed").value) || 0;
      const methods = $("#cpMethods").value.split(",").map(s => s.trim()).filter(Boolean);
      const error = $("#cpError");
      // Validate
      const idVal = validateUUID(id);
      if (!idVal.valid) { error.textContent = idVal.error; error.style.display = "block"; return; }
      const nameVal = validateName(name);
      if (!nameVal.valid) { error.textContent = nameVal.error; error.style.display = "block"; return; }
      const methodsVal = validateMethods(methods);
      if (!methodsVal.valid) { error.textContent = methodsVal.error; error.style.display = "block"; return; }
      const fieldsVal = validateFields(cpFields.filter(f => f.key));
      if (!fieldsVal.valid) { error.textContent = fieldsVal.error; error.style.display = "block"; return; }
      error.style.display = "none";
      const manifest = {
        id, name, emoji, desc,
        countries: countries.split(",").map(s => s.trim()).filter(Boolean),
        methods,
        fields: cpFields.filter(f => f.key).map(f => ({key:f.key,label:f.label,secret:f.secret})),
        feePct, feeFixed
      };
      await api("/platform/custom-providers", "POST", { kind, manifest });
      toast("Provider registered platform-wide"); render();
    }
    const pe = e.target.closest("[data-pedit]"), pa = e.target.closest("[data-pavail]");
    if (pe) {
      const { rows } = await api("/meta/entity/provider_def");
      const r = rows.find(x => x.id === pe.dataset.pedit);
      const m = modal(`<div class="p-modal-head"><h3>${esc(r.name)}</h3><button data-mclose>✕</button></div>
        <div class="p-form"><div class="row3"><label><span>Name</span><input id="pvName" value="${esc(r.name)}"></label><label><span>Emoji</span><input id="pvEmoji" value="${esc(r.emoji || "")}"></label><label><span>Fee %</span><input id="pvFee" type="number" step="any" value="${r.fee_pct}"></label></div>
        <label><span>Methods (JSON)</span><input id="pvM" value="${esc(r.methods)}"></label>
        <label><span>Credential fields (JSON)</span><textarea id="pvF" rows="3">${esc(r.fields)}</textarea></label>
        <button class="p-btn primary" id="pvSave">Save</button></div>`);
      m.querySelector("#pvSave").onclick = async () => {
        await api("/meta/entity/provider_def/" + encodeURIComponent(r.id + "|" + r.kind), "PUT", { name: m.querySelector("#pvName").value, emoji: m.querySelector("#pvEmoji").value, fee_pct: Number(m.querySelector("#pvFee").value), methods: JSON.parse(m.querySelector("#pvM").value || "[]"), fields: JSON.parse(m.querySelector("#pvF").value || "[]") });
        m.innerHTML = ""; toast("Provider updated — live everywhere"); render();
      };
    }
    if (pa) {
      const [all0, av] = await Promise.all([api("/meta/entity/country"), api("/meta/entity/provider_availability")]);
      const have = new Set(av.rows.filter(x => x.provider_id === pa.dataset.pavail).map(x => x.country_code));
      const m = modal(`<div class="p-modal-head"><h3>Availability · ${esc(pa.dataset.pavail)}</h3><button data-mclose>✕</button></div>
        <div class="p-form">${all0.rows.map(c => `<label style="display:flex;gap:8px;align-items:center"><input type="checkbox" data-cc="${c.code}" ${have.has(c.code) ? "checked" : ""}> ${esc(c.name)} (${c.code} · ${esc(c.currency)})</label>`).join("")}
        <button class="p-btn primary" id="avSave">Save availability</button></div>`);
      m.querySelector("#avSave").onclick = async () => {
        const cur = new Set([...m.querySelectorAll("[data-cc]:checked")].map(x => x.dataset.cc));
        for (const c of m.querySelectorAll("[data-cc]")) {
          const key = c.dataset.cc;
          if (c.checked && !have.has(key)) await api("/meta/entity/provider_availability", "POST", { provider_id: pa.dataset.pavail, country_code: key });
          if (!c.checked && have.has(key)) await api("/meta/entity/provider_availability/" + encodeURIComponent(pa.dataset.pavail + "|" + key), "DELETE", {});
        }
        m.innerHTML = ""; toast("Availability saved"); render();
      };
    }
    if (e.target.id === "addCountry") {
      const m = modal(`<div class="p-modal-head"><h3>New country</h3><button data-mclose>✕</button></div>
        <div class="p-form"><div class="row3"><label><span>Code</span><input id="ncCode" maxlength="4" placeholder="CH"></label><label><span>Name</span><input id="ncName"></label><label><span>Currency</span><input id="ncCur" placeholder="CHF"></label></div>
        <div class="row3"><label><span>Symbol</span><input id="ncSym"></label><label><span>Locale</span><input id="ncLoc" placeholder="de-CH"></label><label><span>Decimals</span><input id="ncDec" type="number" value="2"></label></div>
        <p class="p-tag">A country is geography only — currency, symbol, locale, decimals. It carries no tax: set the jurisdiction's rates in the Tax engine (taxRules), and configure each store's tax in its Commerce settings.</p>
        <button class="p-btn primary" id="ncGo">Add</button></div>`);
      m.querySelector("#ncGo").onclick = async () => {
        const q = x => m.querySelector(x).value;
        await api("/meta/entity/country", "POST", { code: q("#ncCode").value.toUpperCase(), name: q("#ncName").value, currency: q("#ncCur").value, symbol: q("#ncSym").value, locale: q("#ncLoc").value, decimals: Number(q("#ncDec").value) });
        m.innerHTML = ""; toast("Country entity created — now assignable to providers"); render();
      };
    }
    if (e.target.id === "addCur" || e.target.closest("[data-cedit]")) {
      const code = e.target.dataset ? e.target.dataset.cedit : null;
      const { rows } = await api("/meta/entity/currency");
      const x = code ? rows.find(r => r.code === code) : null;
      const mm = modal(`<div class="p-modal-head"><h3>${x ? "Edit " + esc(x.code) : "New currency"}</h3><button data-mclose>✕</button></div>
        <div class="p-form"><div class="row3"><label><span>Code *</span><input id="cyCode" value="${x ? esc(x.code) : ""}" ${x ? "disabled" : ""}></label><label><span>Name *</span><input id="cyName" value="${x ? esc(x.name) : ""}"></label><label><span>Symbol *</span><input id="cySym" value="${x ? esc(x.symbol) : ""}"></label></div>
        <div class="row3"><label><span>Decimals</span><input id="cyDec" type="number" value="${x ? x.decimals : 2}"></label><label><span>1 unit = USD</span><input id="cyUsd" type="number" step="0.000001" value="${x ? x.usd : 1}"></label><label><span>Active</span><select id="cyAct"><option value="1">yes</option><option value="0" ${x && !x.active ? "selected" : ""}>no</option></select></label></div>
        <button class="p-btn primary" id="cyGo">Save</button></div>`);
      mm.querySelector("#cyGo").onclick = async () => {
        const q = i => mm.querySelector(i).value;
        const body = { code: q("#cyCode").value.toUpperCase(), name: q("#cyName").value, symbol: q("#cySym").value, decimals: Number(q("#cyDec").value), usd: Number(q("#cyUsd").value), active: Number(q("#cyAct").value) };
        try { await api(x ? "/meta/entity/currency/" + encodeURIComponent(x.code) : "/meta/entity/currency", x ? "PUT" : "POST", body); mm.innerHTML = ""; toast("Currency saved"); render(); } catch (e2) { toast(e2.message); }
      };
    }
    const cdel = e.target.closest("[data-cdel]");
    if (cdel) { try { await api("/meta/entity/currency/" + encodeURIComponent(cdel.dataset.cdel), "DELETE", {}); toast("Currency removed"); render(); } catch (e2) { toast(e2.message); } }
    if (e.target.id === "addTax") {
      const key = prompt("Tax mode key (e.g. sales_tax)"); if (!key) return;
      const label = prompt("Label") || key;
      await api("/meta/entity/tax_mode", "POST", { key: key.toLowerCase().replace(/\W/g, "_"), label, description: "", fields: [] });
      toast("Tax mode created"); render();
    }
    if (e.target.id === "auditQ") {
      const q = e.target.value.toLowerCase();
      $$("#auditTbl tbody tr").forEach(tr => tr.style.display = tr.textContent.toLowerCase().includes(q) ? "" : "none");
    }
  } catch (err) { toast(err.message); }
});

async function vAI() {
  const d = await api("/platform/ai");
  const cap = d.capabilities || [], prov = d.providers || [], plans = d.plans || [], tiers = d.tierByTenant || [];
  const usedBy = {}; (d.usage || []).forEach(u => usedBy[u.slug] = u);
  return `<div class="p-panel"><h2>🧠 AI · Providers, Capabilities & Plans</h2>
    <p style="color:var(--p-muted);font-size:13px">AI is a product on this platform: providers, capabilities, plans and pricing are all <b>editable data</b> (Provider Registry kind “ai”, Data Studio registries). Every store gets the <b>free built-in engine</b> automatically; premium models unlock only for <b>paid</b> stores (active paid plan or the AI Premium module).</p>
    <div class="p-grid"><div class="p-card"><h3>AI Providers (${prov.length})</h3><table class="p-table"><thead><tr><th></th><th>Provider</th><th>Cost / unit</th><th>Capabilities</th></tr></thead><tbody>
      ${prov.map(p => `<tr><td>${esc(p.emoji)}</td><td><b>${esc(p.name)}</b><br><code>${esc(p.id)}</code></td><td>${Number(p.feePct) === 0 && (!p.feeFixed) ? "<span class='badge published'>free</span>" : money(p.feeFixed || 0)}</td><td class="p-tag">${esc((p.methods || []).join(", "))}</td></tr>`).join("")}
    </tbody></table></div>
    <div class="p-card"><h3>Plans</h3>${plans.map(pl => `<div class="p-stat"><b>${esc(pl.name)}</b> · ${pl.price ? money(pl.price) + "/" + esc(pl.billing) : "free"}<div class="p-tag">${esc(pl.note)}</div></div>`).join("")}
    </div></div>
    <h3>Capabilities</h3><div class="p-grid">${cap.map(c => `<div class="p-card"><b>${esc(c.icon)} ${esc(c.name)}</b><div class="p-tag">${esc(c.unit)} · premium: ${(c.premiumProviders || []).join(", ") || "—"}</div><div style="font-size:12px">${esc(c.desc)}</div><div class="p-tag">free/day ${c.freeLimit.perDay} · premium/day ${c.premiumLimit.perDay}</div></div>`).join("")}</div>
    <h3>Store tiers & usage</h3><table class="p-table"><thead><tr><th>Store</th><th>AI tier</th><th>Why</th><th class="num">Calls</th><th class="num">Accrued</th></tr></thead><tbody>
      ${tiers.map(t => { const u = usedBy[t.slug] || {}; return `<tr><td>${esc(t.name)}</td><td><span class="badge ${t.premium ? "published" : "processing"}">${t.premium ? "premium" : "free"}</span></td><td class="p-tag">${t.hasPaidPlan ? "paid plan" : ""}${t.hasAiPro ? (t.hasPaidPlan ? " + " : "") + "AI Pro" : ""}${!t.premium ? "trial/free plan" : ""}</td><td class="num">${u.calls || 0}</td><td class="num">${money(u.cost || 0)}</td></tr>`; }).join("")}
    </tbody></table>
    <p class="p-tag">Manage providers in <b>🔌 Provider Registry</b> (add/enable “ai” kind). Editing capabilities/plans/limits = change the <code>aiCapabilities</code>/<code>aiPlans</code> registries in Data Studio — no code.</p></div>`;
}
/* ═══ GOIP Ω∞ — GLOBAL OFFER INFRASTRUCTURE PLATFORM · platform control plane ═══
   Nine surfaces over one constitution: the 8-stage chain, the 22 capabilities (live-invokable),
   the 67 domains, the value-exchange register, every registry, funding→settlement→payout,
   attribution, intelligence and commercialization. Nothing here is hardcoded: every list is a
   meta_lists registry served by /api/goip, editable in Data Studio. */
let goipTab = "constitution";
const GOIP_TABS = [["constitution", "Ω Constitution"], ["capabilities", "⚡ Capabilities"], ["domains", "🌐 67 Domains"],
["exchanges", "💠 Value Exchanges"], ["registries", "📚 Registries"], ["funding", "🏦 Funding · Settlement"],
["attribution", "🔗 Attribution · Graph"], ["intelligence", "🧠 Intelligence"], ["commercial", "💳 Commercialization"]];
const GOIP = { manifest: null, platform: null };
function gTabs() { return `<div class="p-nav" style="display:flex;flex-wrap:wrap;gap:6px;margin:0 0 12px">${GOIP_TABS.map(([k, l]) => `<button class="p-btn sm ${goipTab === k ? "primary" : ""}" data-gt="${k}">${l}</button>`).join("")}</div>`; }
function pj(v, d) { try { return v ? JSON.parse(v) : (d || {}); } catch (e) { return d || {}; } }
function gRow(k, v) { return `<tr><td class="p-tag">${esc(k)}</td><td>${v}</td></tr>`; }
function gCount(n, label, ok) { return `<div class="p-stat"><em>${esc(label)}</em><b>${n}</b><small style="color:${ok === false ? "var(--p-red)" : "var(--p-muted)"}">${ok === false ? "gap" : "complete"}</small></div>`; }

async function vGlobalOffers() {
  const [m, d] = await Promise.all([api("/goip"), api("/platform/offers")]);
  GOIP.manifest = m; GOIP.platform = d;
  const c = m.coverage;
  const head = `<div class="p-panel"><h2>Ω∞ GOIP — GLOBAL OFFER INFRASTRUCTURE PLATFORM</h2>
    <p style="color:var(--p-muted);font-size:13px;margin:0 0 10px">${esc(m.subtitle)} — a constitutional platform for <b>any</b> incentive, offer, promotion, benefit, entitlement, subsidy, commission, loyalty construct or future value-exchange model, across any industry, organization, country, planet, economy, calendar, governance model or reality. Consumers call <b>capabilities</b>; they never learn the words coupon, cashback or gift card.</p>
    <div class="p-cards">
      ${gCount(c.capabilities.bound + "/" + c.capabilities.declared, "Capabilities bound", c.capabilities.gap.length === 0)}
      ${gCount(c.domains.declared, "Constitutional domains", c.domains.overlapping === 0)}
      ${gCount(c.benefits.handled + "/" + c.benefits.declared, "Benefits with math", c.benefits.gap.length === 0)}
      ${gCount(c.contexts.declared, "Context dimensions", true)}
      ${gCount(c.engines.declared, "Decision engines", true)}
      ${gCount(c.economic.units, "Economic units", true)}
    </div></div>`;
  return head + gTabs() + `<div id="goipBody">` + (await gView()) + `</div>`;
}
async function gView() {
  const m = GOIP.manifest, d = GOIP.platform;
  if (goipTab === "constitution") return gConstitution(m, d);
  if (goipTab === "capabilities") return gCapabilities(m);
  if (goipTab === "domains") return gDomains(m, d);
  if (goipTab === "exchanges") return gExchanges(m, d);
  if (goipTab === "registries") return gRegistries(m);
  if (goipTab === "funding") return gFunding(m, d);
  if (goipTab === "attribution") return await gAttribution(m, d);
  if (goipTab === "intelligence") return await gIntelligence(m);
  if (goipTab === "commercial") return gCommercial(m, d);
  return "";
}
function gConstitution(m, d) {
  const c = m.coverage;
  return `<div class="p-grid">
    <div class="p-card"><h3>The chain every value exchange walks</h3>
      <table class="p-table"><tbody>${m.constitution.map(x => `<tr><td><b>${x.step}. ${esc(x.name)}</b><div class="p-tag">${esc(x.question)}</div></td><td class="p-tag">owner <code>${esc(x.owner)}</code><br>engine <code>${esc(x.engine)}</code></td></tr>`).join("")}</tbody></table></div>
    <div class="p-card"><h3>Zero-gap scorecard</h3><table class="p-table"><tbody>
      ${gRow("Capabilities declared → bound", c.capabilities.bound + " / " + c.capabilities.declared + (c.capabilities.gap.length ? ' <span class="badge draft">' + esc(c.capabilities.gap.join(",")) + "</span>" : ' <span class="badge published">no gap</span>'))}
      ${gRow("Benefits declared → with math", c.benefits.handled + " / " + c.benefits.declared + (c.benefits.gap.length ? ' <span class="badge draft">' + esc(c.benefits.gap.join(",")) + "</span>" : ' <span class="badge published">no gap</span>'))}
      ${gRow("Domains → distinct owners", c.domains.declared + " / " + c.domains.distinct_owners + (c.domains.overlapping ? ' <span class="badge draft">' + c.domains.overlapping + " overlapping</span>" : ' <span class="badge published">zero overlap</span>'))}
      ${gRow("Intelligence implemented", c.intelligence.implemented + " / " + c.intelligence.declared)}
      ${gRow("Fabrics", Object.entries(c.fabrics).map(([k, v]) => `${esc(k)} <b>${v}</b>`).join(" · "))}
      ${gRow("Temporal", c.temporal.calendars + " calendars · " + c.temporal.chronologies + " chronologies · " + c.temporal.units + " units")}
      ${gRow("Spatial", c.spatial.systems + " systems · " + c.spatial.coordinate_systems + " coordinate systems · " + c.spatial.nodes + " nodes")}
      ${gRow("Economic · reality", c.economic.units + " units · " + c.economic.classes + " classes · " + c.reality.models + " reality models")}
      ${gRow("Graph", c.graph.nodes + " node kinds · " + c.graph.edges + " relationships")}
      ${gRow("Surfaces · protocols", c.experience.surfaces + " experience surfaces · " + c.access.protocols + " access protocols")}
      ${gRow("Commercial", c.commercial.deployments + " deployment models · " + c.commercial.billing_models + " billing models · " + c.commercial.meters + " meters")}
    </tbody></table></div></div>
    <div class="p-panel"><h3>Experience fabric</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>Surface</th><th>Bound to</th><th>State</th></tr></thead><tbody>
      ${m.experience.map(x => `<tr><td>${esc(x.name)}</td><td class="p-tag"><code>${esc(x.binding)}</code></td><td><span class="badge ${x.state === "live" ? "published" : "draft"}">${esc(x.state)}</span></td></tr>`).join("")}
    </tbody></table></div></div>
    <div class="p-panel"><h3>Universal access fabric</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>Protocol</th><th>Bound to</th><th>State</th></tr></thead><tbody>
      ${m.access.map(x => `<tr><td>${esc(x.name)}</td><td class="p-tag"><code>${esc(x.binding)}</code></td><td><span class="badge ${x.state === "live" ? "published" : "draft"}">${esc(x.state)}</span></td></tr>`).join("")}
    </tbody></table></div></div>`;
}
function gCapabilities(m) {
  return `<div class="p-panel"><h3>Universal capability layer — the only vocabulary a consumer needs</h3>
    <p class="p-tag">Every call is <code>POST /api/goip/&lt;capability&gt;</code>. Scope decides who may call it: <b>any</b> = a shopper session, <b>tenant</b> = store admin, <b>platform</b> = this console. Each capability writes exactly one store and bills exactly one meter.</p>
    <div class="p-scroll-x"><table class="p-table"><thead><tr><th>Capability</th><th>Stage</th><th>Engine</th><th>Writes</th><th>Meter</th><th>Scope</th><th></th></tr></thead><tbody>
      ${m.capabilities.map(c => `<tr><td><b>${esc(c.name)}</b><br><code>${esc(c.key)}</code></td><td class="p-tag">${esc(c.stage)}</td><td class="p-tag">${esc(c.engine)}</td><td class="p-tag">${esc(c.writes || "—")}</td><td class="p-tag">${esc(c.meter)}</td><td><span class="badge ${c.scope === "platform" ? "draft" : "published"}">${esc(c.scope)}</span></td>
        <td style="text-align:right"><button class="p-btn sm" data-gcap="${esc(c.key)}">invoke</button></td></tr>`).join("")}
    </tbody></table></div>
    <div class="p-panel" style="margin-top:10px"><h3>Capability console</h3>
      <div style="display:flex;gap:8px;align-items:end;flex-wrap:wrap">
        <label><span>Capability</span><select id="gcSel">${m.capabilities.map(c => `<option value="${esc(c.key)}">${esc(c.key)} — ${esc(c.name)}</option>`).join("")}</select></label>
        <button class="p-btn primary sm" id="gcRun">Invoke</button>
      </div>
      <label style="display:block;margin-top:8px"><span>Input (JSON)</span><textarea id="gcBody" rows="5" style="width:100%;font-family:ui-monospace,monospace;font-size:12px">{ "amount": 250 }</textarea></label>
      <pre id="gcOut" class="p-scroll-x" style="background:var(--p-bg2,#0b1020);color:#9ae6b4;padding:10px;border-radius:8px;max-height:320px;overflow:auto;font-size:12px">—</pre>
    </div>
    <div class="p-panel"><h3>Decision fabric — 18 engines, one job each</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>Engine</th><th>Owns</th><th>Implementation</th></tr></thead><tbody>
      ${m.engines.map(e => `<tr><td><b>${esc(e.name)}</b></td><td>${esc(e.owns)}</td><td class="p-tag"><code>${esc(e.impl)}</code></td></tr>`).join("")}
    </tbody></table></div></div>
    <div class="p-panel"><h3>Context fabric — 25 dimensions resolved on every decision</h3><div class="p-grid">
      ${m.contexts.map(x => `<div class="p-card" style="padding:8px 10px"><b>${esc(x.name)}</b><div class="p-tag">${esc(x.source)}</div></div>`).join("")}
    </div></div>`;
}
function gDomains(m, d) {
  const counts = {}; (d.domains || []).forEach(x => counts[x.domain] = x.n);
  return `<div class="p-panel"><h3>67 constitutional domains — each with exactly one owner and one discriminator</h3>
    <p class="p-tag">The discriminator is what makes overlap impossible: no two domains select the same rows from the same store. Live counts are value-exchange records currently in each domain.</p>
    <div class="p-scroll-x"><table class="p-table"><thead><tr><th>#</th><th>Domain</th><th>Owner (store)</th><th>Discriminator</th><th>Fabric</th><th class="num">Records</th></tr></thead><tbody>
      ${m.domains.map(x => `<tr><td class="p-tag">${String(x.n).padStart(2, "0")}</td><td><b>${esc(x.name)}</b><br><code>${esc(x.key)}</code></td><td class="p-tag"><code>${esc(x.owner)}</code></td><td style="font-size:12px">${esc(x.discriminator)}</td><td><span class="badge ${x.fabric === "capability" ? "published" : "draft"}">${esc(x.fabric)}</span></td><td class="num">${counts[x.key] || 0}</td></tr>`).join("")}
    </tbody></table></div></div>`;
}
function gExchanges(m, d) {
  const opt = (arrx, val) => (arrx || []).map(x => `<option value="${esc(x.key || x)}" ${val === (x.key || x) ? "selected" : ""}>${esc(x.name || x)}</option>`).join("");
  const benefits = m.benefits, domains = m.domains, units = m.economic.units, places = m.spatial.nodes, cals = m.temporal.calendars, dist = m.fabrics.distribution;
  return `<div class="p-panel"><h3>Publish a global value exchange</h3>
    <p class="p-tag">Scope = <b>global</b> — every store inherits it (bank cashbacks, brand vouchers, government subsidies, marketplace-wide sales, partner benefits). Stores honour global exchanges only while <b>Provisioning → global offers</b> allows it.</p>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:8px;align-items:end">
      <label><span>Name</span><input id="gName" placeholder="Platform-wide 2% credit"></label>
      <label><span>Benefit</span><select id="gBenefit">${opt(benefits, "percentage_discount")}</select></label>
      <label><span>Value</span><input id="gValue" type="number" step="0.01" value="10"></label>
      <label><span>Code (optional)</span><input id="gCode" placeholder="GLOBAL10"></label>
      <label><span>Domain</span><select id="gDomain">${opt(domains, "incentive")}</select></label>
      <label><span>Channel</span><select id="gChan"><option>commerce</option><option>subscription</option><option>ai</option><option>any</option></select></label>
      <label><span>Funder</span><select id="gFunder">${opt(m.fabrics.funding.filter(f => f.kind === "source").map(f => ({ key: f.party_type === "split" ? "split" : f.key, name: f.name })))}</select></label>
      <label><span>Funder ref</span><input id="gFunderRef" placeholder="HDFC / Nike / Ministry"></label>
      <label><span>Economic unit</span><select id="gUnit"><option value="">store currency</option>${opt(units)}</select></label>
      <label><span>Reality</span><select id="gReality">${opt(m.realities, "any")}</select></label>
      <label><span>Calendar</span><select id="gCal"><option value="">any</option>${opt(cals)}</select></label>
      <label><span>Place (prefix)</span><select id="gPlace"><option value="">anywhere</option>${opt(places)}</select></label>
      <label><span>Usage limit</span><input id="gUse" type="number" value="0"></label>
      <label><span>Governance</span><select id="gGov">${opt(m.governance_states.map(x => ({ key: x, name: x })), "published")}</select></label>
    </div>
    <label style="display:block;margin-top:8px"><span>Distribution channels</span>
      <div style="display:flex;flex-wrap:wrap;gap:8px">${dist.map(c => `<label style="display:flex;gap:4px;align-items:center;font-size:12px"><input type="checkbox" data-gdist="${esc(c.key)}"> ${esc(c.name)}</label>`).join("")}</div></label>
    <label style="display:block;margin-top:8px"><span>Declared conditions (JSON over the resolved context)</span><input id="gCond" placeholder='{ "audience.orders": { "gte": 1 }, "cart.amount": { "gte": 100 } }'></label>
    <label style="display:block;margin-top:8px"><span>Funding split (JSON, multi-party)</span><input id="gFund" placeholder='{ "parties": [{ "party": "HDFC", "party_type": "bank", "share": 0.6 }, { "party": "NIKE", "party_type": "brand", "share": 0.4 }] }'></label>
    <div style="margin-top:8px"><button class="p-btn primary sm" id="gSave">Publish value exchange</button> <span class="p-tag" id="gSaveMsg"></span></div>
  </div>
  <div class="p-panel"><h3>Global value exchanges</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>Name</th><th>Domain · Benefit</th><th>Context</th><th>Funder</th><th class="num">Value</th><th class="num">Used/Limit</th><th>State</th><th></th></tr></thead>
    <tbody>${(d.global || []).map(o => `<tr><td><b>${esc(o.name)}</b>${o.code ? ` <code>${esc(o.code)}</code>` : ""}${o.version > 1 ? ` <span class="p-tag">v${o.version}</span>` : ""}</td>
      <td class="p-tag">${esc(o.domain || "incentive")}<br>${esc(o.benefit || o.type)}</td>
      <td class="p-tag">${esc(o.reality || "any")} · ${esc((pj(o.spatial_spec).include || []).join(",") || "anywhere")} · ${esc(pj(o.temporal_spec).calendar || "any calendar")} · ${esc(o.economic_unit || o.currency)}</td>
      <td>${esc(o.funder)}${o.funder_ref ? " " + esc(o.funder_ref) : ""}</td><td class="num">${esc(o.value)}</td><td class="num">${o.used}/${o.usage_limit || "∞"}</td>
      <td><span class="badge ${(pj(o.governance).state || o.status) === "published" || o.status === "active" ? "published" : "draft"}">${esc(pj(o.governance).state || o.status)}</span></td>
      <td style="text-align:right;white-space:nowrap"><button class="p-btn sm" data-ggov="publish" data-gid="${o.id}">publish</button> <button class="p-btn sm" data-ggov="suspend" data-gid="${o.id}">suspend</button> <button class="p-btn sm" data-ggov="version" data-gid="${o.id}">version</button></td></tr>`).join("") || '<tr><td colspan="8">No global value exchanges yet.</td></tr>'}</tbody></table></div></div>
  <div class="p-panel"><h3>Benefit fabric — 25 constructs, one math engine</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>Benefit</th><th>Handler (offers.HANDLERS)</th><th>Direction</th><th>Unit</th><th>Grants</th></tr></thead><tbody>
    ${m.benefits.map(b => `<tr><td><b>${esc(b.name)}</b><br><code>${esc(b.key)}</code></td><td class="p-tag"><code>${esc(b.type)}</code></td><td>${esc(b.direction)}</td><td class="p-tag">${esc(b.unit || "—")}</td><td class="p-tag">${esc(b.grants || "—")}</td></tr>`).join("")}
  </tbody></table></div></div>`;
}
function gRegistries(m) {
  const tbl = (title, rows, cols) => `<div class="p-panel"><h3>${esc(title)}</h3><div class="p-scroll-x"><table class="p-table"><thead><tr>${cols.map(c => `<th>${esc(c[0])}</th>`).join("")}</tr></thead><tbody>${(rows || []).map(r => `<tr>${cols.map(c => `<td>${esc(typeof c[1] === "function" ? c[1](r) : r[c[1]])}</td>`).join("")}</tr>`).join("")}</tbody></table></div></div>`;
  return `<p class="p-tag">Every row below is a <code>meta_lists</code> registry — add a calendar, a planet, an economic unit, a benefit, a channel, an attribution model or an entire civilization in <b>Data Studio → Registries</b> and the engines obey it on the next request. No code, no redeploy, no redesign.</p>
  ${tbl("Temporal authority · calendars", m.temporal.calendars, [["Calendar", "name"], ["Key", "key"], ["Chronology", "chronology"], ["Epoch", "epoch"], ["Day (s)", "day_seconds"], ["Year (days)", "year_days"], ["Authority", "authority"]])}
  ${tbl("Chronologies", m.temporal.chronologies, [["Chronology", "name"], ["Base unit", "base_unit"], ["Rotation (s)", "rotation_seconds"]])}
  ${tbl("Temporal measurement", m.temporal.units, [["Unit", "name"], ["Key", "key"], ["Seconds", "seconds"]])}
  ${tbl("Spatial systems", m.spatial.systems, [["System", "name"], ["Body", "body"], ["Levels", r => (r.levels || []).join(" → ")], ["Coordinates", "coordinate"]])}
  ${tbl("Coordinate systems", m.spatial.coordinates, [["System", "name"], ["Axes", r => (r.axes || []).join(", ") || "—"], ["Unit", "unit"]])}
  ${tbl("Spatial hierarchy", m.spatial.nodes, [["Path", "key"], ["Name", "name"], ["System", "system"], ["Level", "level"], ["Parent", r => r.parent || "—"]])}
  ${tbl("Economic units", m.economic.units, [["Unit", "name"], ["Key", "key"], ["Class", "class"], ["Decimals", "decimals"], ["Rate → USD", r => r.base_rate || "declared"], ["Settleable", r => r.settleable ? "yes" : "no"]])}
  ${tbl("Reality models", m.realities, [["Reality", "name"], ["Key", "key"]])}
  ${tbl("Distribution fabric", m.fabrics.distribution, [["Channel", "name"], ["Bound to", "binding"], ["State", "state"]])}
  ${tbl("Attribution fabric", m.fabrics.attribution, [["Attribution", "name"], ["Basis", "basis"], ["Default model", "model"]])}
  ${tbl("Funding fabric", m.fabrics.funding, [["Funding", "name"], ["Party type", r => r.party_type || "—"], ["Kind", "kind"]])}
  ${tbl("Settlement fabric", m.fabrics.settlement, [["Element", "name"], ["Store", "store"], ["Stage", "stage"]])}
  ${tbl("Governance fabric", m.fabrics.governance, [["Engine", "name"], ["Action", "action"], ["Store", "store"]])}`;
}
function gFunding(m, d) {
  const t = d.treasury || { positions: [], burn: { monthly: [] } };
  const byFunder = (d.stats && d.stats.byFunder) || [];
  return `<div class="p-cards">
      ${(t.positions || []).map(p => `<div class="p-stat"><em>${esc(p.unit)} treasury</em><b>${p.available}</b><small>allocated ${p.allocated} · consumed ${p.consumed}</small></div>`).join("") || '<div class="p-stat"><em>Treasury</em><b>—</b><small>no budgets funded yet</small></div>'}
      <div class="p-stat"><em>Avg monthly burn</em><b>${money((t.burn && t.burn.average) || 0)}</b><small>last ${(t.burn && t.burn.monthly || []).length} periods</small></div>
    </div>
    <div class="p-panel"><h3>Fund a budget</h3>
      <div style="display:flex;gap:8px;align-items:end;flex-wrap:wrap">
        <label><span>Funder</span><select id="fFunder">${(m.fabrics.funding.filter(f => f.kind === "source")).map(f => `<option value="${esc(f.party_type === "split" ? "split" : f.key)}">${esc(f.name)}</option>`).join("")}</select></label>
        <label><span>Funder ref</span><input id="fRef" placeholder="HDFC"></label>
        <label><span>Unit</span><select id="fUnit">${m.economic.units.map(u => `<option value="${esc(u.key)}">${esc(u.key)}</option>`).join("")}</select></label>
        <label><span>Domain</span><select id="fDomain">${m.domains.map(x => `<option value="${esc(x.key)}" ${x.key === "incentive" ? "selected" : ""}>${esc(x.name)}</option>`).join("")}</select></label>
        <label><span>Amount</span><input id="fAmount" type="number" value="1000"></label>
        <button class="p-btn primary sm" id="fGo">Allocate</button>
      </div></div>
    <div class="p-panel"><h3>Budgets</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>Funder</th><th>Domain</th><th>Unit</th><th>Period</th><th class="num">Allocated</th><th class="num">Reserved</th><th class="num">Consumed</th><th class="num">Available</th><th class="num">Burn</th><th>Status</th></tr></thead><tbody>
      ${(d.budgets || []).map(b => `<tr><td>${esc(b.funder)}${b.funder_ref ? " " + esc(b.funder_ref) : ""}</td><td class="p-tag">${esc(b.domain)}</td><td>${esc(b.unit)}</td><td class="p-tag">${esc(b.period)}</td><td class="num">${b.allocated}</td><td class="num">${b.reserved}</td><td class="num">${b.consumed}</td><td class="num">${b.available}</td><td class="num">${b.burn_pct}%</td><td><span class="badge ${b.status === "open" ? "published" : "draft"}">${esc(b.status)}</span></td></tr>`).join("") || '<tr><td colspan="10">No budgets — allocate one above.</td></tr>'}
    </tbody></table></div></div>
    <div class="p-panel"><h3>Settlement &amp; payout</h3>
      <div style="display:flex;gap:8px;align-items:end;flex-wrap:wrap;margin-bottom:8px">
        <label><span>Period</span><input id="sPeriod" value="${esc(d.period || "")}" placeholder="YYYY-MM"></label>
        <button class="p-btn primary sm" id="sRun">Run settlement</button>
        <span class="p-tag">Each redeemed-but-unsettled redemption is attributed to its funding parties exactly once — re-running settles nothing twice.</span>
      </div>
      <div class="p-scroll-x"><table class="p-table"><thead><tr><th>Period</th><th>Party</th><th>Type</th><th>Unit</th><th class="num">Gross</th><th class="num">Fees</th><th class="num">Net</th><th class="num">Redemptions</th><th>Status</th><th></th></tr></thead><tbody>
        ${(d.settlements || []).map(x => `<tr><td class="p-tag">${esc(x.period)}</td><td><b>${esc(x.party)}</b></td><td class="p-tag">${esc(x.party_type)}</td><td>${esc(x.unit)}</td><td class="num">${x.gross}</td><td class="num">${x.fees}</td><td class="num">${x.net}</td><td class="num">${x.redemptions}</td><td><span class="badge ${x.status === "paid" || x.status === "reconciled" ? "published" : "draft"}">${esc(x.status)}</span>${x.reference ? `<br><code>${esc(x.reference)}</code>` : ""}</td>
          <td style="text-align:right;white-space:nowrap">${x.status === "accrued" ? `<button class="p-btn sm" data-sapprove="${x.id}" data-stenant="${x.tenant_id}">approve</button> ` : ""}${x.status === "accrued" || x.status === "approved" ? `<button class="p-btn sm primary" data-spay="${x.id}" data-stenant="${x.tenant_id}">pay</button>` : ""}${x.status === "paid" ? `<button class="p-btn sm" data-srec="${x.id}" data-stenant="${x.tenant_id}">reconcile</button>` : ""}</td></tr>`).join("") || '<tr><td colspan="10">Nothing accrued yet — run a settlement.</td></tr>'}
      </tbody></table></div></div>
    <div class="p-panel"><h3>Redemption split by funder (all stores)</h3>${byFunder.length ? `<table class="p-table"><thead><tr><th>Funder</th><th class="num">Value granted</th><th class="num">Redemptions</th></tr></thead><tbody>${byFunder.map(f => `<tr><td>${esc(f.funder)}</td><td class="num">${money(f.amount)}</td><td class="num">${f.redemptions}</td></tr>`).join("")}</tbody></table>` : '<p class="p-tag">No redemptions yet.</p>'}</div>`;
}
async function gAttribution(m, d) {
  let tp = { touchpoints: [] };
  try { tp = await api("/goip/touchpoints"); } catch (e) { }
  return `<div class="p-panel"><h3>Attribution fabric</h3>
    <p class="p-tag">Touchpoints are captured by <code>POST /api/goip/track</code> from any surface; <code>POST /api/goip/attribute</code> replays a subject's path through any declared model (${m.fabrics.attribution_models.join(", ")}) and splits revenue and commission across the parties that earned it.</p>
    <div style="display:flex;gap:8px;align-items:end;flex-wrap:wrap">
      <label><span>Subject (owner)</span><input id="aOwner" placeholder="t1:u:2"></label>
      <label><span>Model</span><select id="aModel">${m.fabrics.attribution_models.map(x => `<option>${esc(x)}</option>`).join("")}</select></label>
      <label><span>Revenue</span><input id="aValue" type="number" value="0"></label>
      <label><span>Commission %</span><input id="aRate" type="number" value="10"></label>
      <button class="p-btn primary sm" id="aRun">Attribute</button>
    </div>
    <pre id="aOut" class="p-scroll-x" style="background:var(--p-bg2,#0b1020);color:#9ae6b4;padding:10px;border-radius:8px;margin-top:8px;max-height:260px;overflow:auto;font-size:12px">—</pre>
  </div>
  <div class="p-panel"><h3>Recent touchpoints</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>When</th><th>Kind</th><th>Party</th><th>Channel</th><th>Subject</th><th class="num">Value</th></tr></thead><tbody>
    ${(tp.touchpoints || []).slice(-25).reverse().map(t => `<tr><td class="p-tag">${esc(String(t.created_at || "").slice(0, 19))}</td><td><span class="badge ${t.kind === "conversion" ? "published" : "draft"}">${esc(t.kind)}</span></td><td>${esc(t.party)}<div class="p-tag">${esc(t.party_type)}</div></td><td class="p-tag">${esc(t.channel)} · ${esc(t.distribution)}</td><td class="p-tag">${esc((t.owner || "").slice(0, 22))}</td><td class="num">${t.value}</td></tr>`).join("") || '<tr><td colspan="6">No touchpoints recorded yet.</td></tr>'}
  </tbody></table></div></div>
  <div class="p-panel"><h3>Universal incentive graph</h3>
    <p class="p-tag">${m.graph.nodes.length} node kinds · ${m.graph.edges.length} relationships, projected onto the platform's existing <code>links</code> table — every edge is queryable with <code>GET /api/goip/exchanges/:id</code>.</p>
    <div class="p-grid">${m.graph.nodes.map(n => `<div class="p-card" style="padding:6px 10px"><b>${esc(n.key)}</b><div class="p-tag">${esc(n.store)}</div></div>`).join("")}</div>
    <p style="margin-top:8px">${m.graph.edges.map(e => `<code style="margin-right:6px">${esc(e)}</code>`).join("")}</p></div>`;
}
async function gIntelligence(m) {
  return `<div class="p-panel"><h3>Intelligence fabric — 15 readings over live data</h3>
    <div style="display:flex;gap:8px;align-items:end;flex-wrap:wrap">
      <label><span>Reading</span><select id="iSel">${m.fabrics.intelligence.map(x => `<option value="${esc(x.key)}">${esc(x.name)}</option>`).join("")}</select></label>
      <button class="p-btn primary sm" id="iRun">Read</button>
      <span class="p-tag">Generation readings propose drafts; nothing publishes without the governance engine.</span>
    </div>
    <pre id="iOut" class="p-scroll-x" style="background:var(--p-bg2,#0b1020);color:#9ae6b4;padding:10px;border-radius:8px;margin-top:8px;max-height:420px;overflow:auto;font-size:12px">Pick a reading.</pre>
  </div>`;
}
function gCommercial(m, d) {
  const meters = d.meters || [], installs = d.installs || [];
  return `<div class="p-panel"><h3>Deployment models</h3><div class="p-grid">
      ${m.commercialization.deployments.map(x => `<div class="p-card" style="padding:8px 10px"><b>${esc(x.name)}</b><div class="p-tag"><code>${esc(x.key)}</code></div></div>`).join("")}
    </div></div>
    <div class="p-panel"><h3>Billing models — every capability bills a meter</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>Model</th><th>Meter</th><th>Unit</th><th class="num">Rate</th><th class="num">Metered qty</th><th class="num">Accrued</th></tr></thead><tbody>
      ${m.commercialization.billing_models.map(b => { const live = meters.find(x => x.kind === b.meter) || { qty: 0, amount: 0 }; return `<tr><td><b>${esc(b.name)}</b></td><td class="p-tag"><code>${esc(b.meter)}</code></td><td class="p-tag">${esc(b.unit)}</td><td class="num">${b.rate}</td><td class="num">${live.qty || 0}</td><td class="num">${money(live.amount || 0)}</td></tr>`; }).join("")}
    </tbody></table></div>
    <p class="p-tag">Meters are written through <code>billing.meter()</code> into <code>usage_records</code> — they ride the existing invoice run, so GOIP usage appears as billed lines on the store's next invoice. Rates apply only to stores that purchased the GOIP module; everyone else is metered at zero.</p></div>
    <div class="p-panel"><h3>Stores entitled to GOIP</h3><table class="p-table"><thead><tr><th>Store</th><th>Status</th></tr></thead><tbody>
      ${installs.map(i => `<tr><td>${esc(i.slug)}</td><td><span class="badge ${i.status === "installed" ? "published" : "draft"}">${esc(i.status)}</span></td></tr>`).join("") || '<tr><td colspan="2">No store has purchased GOIP yet — sell it in <b>🧩 Module Marketplace</b>.</td></tr>'}
    </tbody></table></div>`;
}
function wireGlobalOffers() {
  const $id = i => document.getElementById(i);
  const gval = i => { const el = $id(i); return el ? el.value : ""; };
  const jparse = (v, d) => { try { return v ? JSON.parse(v) : d; } catch (e) { return d; } };
  document.querySelectorAll("[data-gt]").forEach(b => b.onclick = async () => {
    goipTab = b.dataset.gt;
    document.querySelectorAll("[data-gt]").forEach(x => x.classList.toggle("primary", x.dataset.gt === goipTab));
    const body = $id("goipBody"); if (body) { body.innerHTML = '<div class="p-empty">Loading…</div>'; body.innerHTML = await gView(); wireGlobalOffers(); }
  });
  if ($id("gSave")) $id("gSave").onclick = async () => {
    const dist = [...document.querySelectorAll("[data-gdist]")].filter(c => c.checked).map(c => c.dataset.gdist);
    const place = gval("gPlace"), cal = gval("gCal");
    try {
      const r = await api("/goip/create", "POST", {
        name: gval("gName"), benefit: gval("gBenefit"), value: Number(gval("gValue")), code: gval("gCode"),
        domain: gval("gDomain"), channel: gval("gChan"), funder: gval("gFunder"), funder_ref: gval("gFunderRef"),
        economic_unit: gval("gUnit"), reality: gval("gReality"), usage_limit: Number(gval("gUse")) || 0,
        temporal: cal ? { calendar: cal } : {}, spatial: place ? { include: [place] } : {},
        conditions: jparse(gval("gCond"), {}), funding: jparse(gval("gFund"), {}), distribution: dist,
        governance: { state: gval("gGov") }, scope_level: "global", scope_type: "store", status: "active"
      });
      toast("Value exchange published (#" + (r.result && r.result.id) + ")"); render();
    } catch (e) { toast(e.message); }
  };
  document.querySelectorAll("[data-ggov]").forEach(b => b.onclick = async () => {
    try { const r = await api("/goip/govern", "POST", { id: Number(b.dataset.gid), action: b.dataset.ggov }); toast(b.dataset.ggov + " → " + ((r.result && r.result.state) || (r.result && r.result.id) || "ok")); render(); }
    catch (e) { toast(e.message); }
  });
  if ($id("gcRun")) $id("gcRun").onclick = async () => {
    const out = $id("gcOut"); out.textContent = "…";
    try { const r = await api("/goip/" + gval("gcSel"), "POST", jparse(gval("gcBody"), {})); out.textContent = JSON.stringify(r, null, 2); }
    catch (e) { out.textContent = "⚠️ " + e.message; }
  };
  document.querySelectorAll("[data-gcap]").forEach(b => b.onclick = () => { const sel = $id("gcSel"); if (sel) { sel.value = b.dataset.gcap; sel.scrollIntoView({ block: "center" }); } });
  if ($id("fGo")) $id("fGo").onclick = async () => {
    try { await api("/goip/fund", "POST", { funder: gval("fFunder"), funder_ref: gval("fRef"), unit: gval("fUnit"), domain: gval("fDomain"), amount: Number(gval("fAmount")) || 0 }); toast("Budget allocated"); render(); }
    catch (e) { toast(e.message); }
  };
  if ($id("sRun")) $id("sRun").onclick = async () => {
    try { const r = await api("/goip/settle", "POST", { period: gval("sPeriod"), all: true }); toast((r.result.redemptions_settled || 0) + " redemptions settled across all stores"); render(); }
    catch (e) { toast(e.message); }
  };
  document.querySelectorAll("[data-spay]").forEach(b => b.onclick = async () => {
    const fees = prompt("Payout fees (blank = 0)"); if (fees === null) return;
    try { const r = await api("/goip/pay", "POST", { id: Number(b.dataset.spay), fees: Number(fees) || 0, tenant_id: Number(b.dataset.stenant || 0) || undefined }); toast("Paid " + r.result.net + " " + r.result.unit + " · " + r.result.reference); render(); }
    catch (e) { toast(e.message); }
  });
  document.querySelectorAll("[data-sapprove]").forEach(b => b.onclick = async () => {
    try { await api("/goip/settle", "POST", { approve: Number(b.dataset.sapprove), tenant_id: Number(b.dataset.stenant || 0) || undefined }); toast("Settlement approved"); render(); }
    catch (e) { toast(e.message); }
  });
  document.querySelectorAll("[data-srec]").forEach(b => b.onclick = async () => {
    const ref = prompt("External reference (bank statement id)"); if (ref === null) return;
    try { await api("/goip/settle", "POST", { reconcile: Number(b.dataset.srec), external_ref: ref, tenant_id: Number(b.dataset.stenant || 0) || undefined }); toast("Reconciled"); render(); }
    catch (e) { toast(e.message); }
  });
  if ($id("aRun")) $id("aRun").onclick = async () => {
    const out = $id("aOut"); out.textContent = "…";
    try { const r = await api("/goip/attribute", "POST", { owner: gval("aOwner"), model: gval("aModel"), value: Number(gval("aValue")) || 0, commission_rate: Number(gval("aRate")) || 0 }); out.textContent = JSON.stringify(r.result, null, 2); }
    catch (e) { out.textContent = "⚠️ " + e.message; }
  };
  if ($id("iRun")) $id("iRun").onclick = async () => {
    const out = $id("iOut"); out.textContent = "…";
    try { const r = await api("/goip/intelligence/" + gval("iSel")); out.textContent = JSON.stringify(r.result, null, 2); }
    catch (e) { out.textContent = "⚠️ " + e.message; }
  };
}
function wireDefinitions() {
  const $id = i => document.getElementById(i);
  const modal = $id("defModal");
  $id("newDef").onclick = () => { $id("defTitle").textContent = "Define Entity"; $id("defKey").value = ""; $id("defLabel").value = ""; $id("defIcon").value = ""; $id("defFields").value = ""; modal.style.display = "block"; };
  $id("cancelDef").onclick = () => { modal.style.display = "none"; };
  $id("saveDef").onclick = async () => {
    const key = $id("defKey").value.trim();
    const label = $id("defLabel").value.trim();
    const icon = $id("defIcon").value.trim() || "🧬";
    const fields = JSON.parse($id("defFields").value || "[]");
    if (!key || !label || !Array.isArray(fields)) { alert("Key, label and fields required"); return; }
    try {
      await api("/meta/entity-def", "POST", { key, label, icon, fields });
      toast("Entity definition saved"); modal.style.display = "none"; render();
    } catch (e) { toast(e.message); }
  };
 $$("[data-edit]").forEach(b => b.onclick = async () => {
    const key = b.dataset.edit;
    const row = await api("/meta/entity-def");
    const def = row.rows.find(r => r.key === key);
    if (!def) return;
    $id("defTitle").textContent = "Edit Entity";
    $id("defKey").value = def.key;
    $id("defLabel").value = JSON.parse(def.def || "{}").label;
    $id("defIcon").value = JSON.parse(def.def || "{}").icon || "";
    $id("defFields").value = JSON.stringify(JSON.parse(def.def || "{}").fields || [], null, 2);
    modal.style.display = "block";
  });
  $$("[data-toggle-entity]").forEach(b => b.onclick = async () => {
    const key = b.dataset.toggleEntity;
    const tenantId = b.dataset.tenant;
    const enabled = b.textContent === '✕';
    try {
      if (enabled) {
        await api(`/meta/entity-def/${key}/disable?tenant_id=${tenantId}`, "POST");
      } else {
        await api(`/meta/entity-def/${key}/enable?tenant_id=${tenantId}`, "POST");
      }
      toast(enabled ? "Entity disabled for store" : "Entity enabled for store");
      render();
    } catch (e) { toast(e.message); }
  });
 }
function wireStudio() {
  /* getElementById is unreliable in the moment right after this view's 1,900-option
     select is parsed (jsdom's id map lags one tick); querySelector sees the live tree
     immediately, so every binding here resolves through it */
  const $ = s => document.querySelector(s);
  if ($("#studioLoad")) $("#studioLoad").onclick = async () => {
    const tenantId = $("#studioTenant").value;
    const entity = $("#studioEntity").value;
    try {
      const { rows } = await api(`/meta/entity/${entity}?tenant_id=${tenantId}`);
      const def = (await api("/meta/entity-def")).rows.find(r => r.key === entity);
      const schema = JSON.parse(def.def || "{}");
      const fields = schema.fields || [];
      const tbody = rows.map(r => {
        const cells = fields.filter(f => f.list).map(f => `<td>${esc(r[f.key] || "")}</td>`).join("");
        return `<tr>${cells}<td><button class="p-btn sm" data-view="${r.id}">View</button></td></tr>`;
      }).join("") || '<tr><td colspan="5" class="p-empty">No data</td></tr>';
      $("#studioBody").innerHTML = `<div class="p-panel"><h3>${esc(schema.label || entity)} Data</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>${fields.filter(f => f.list).map(f => `<th>${esc(f.label)}</th>`).join("")}<th>Actions</th></tr></thead><tbody>${tbody}</tbody></table></div></div>`;
    } catch (e) { toast(e.message); }
  };
}
function wireUCII() {
  const $ = s => document.querySelector(s);
  $$("[data-action]").forEach(b => b.onclick = async () => {
    const action = b.dataset.action;
    try {
      if (action === "newCap") {
        const key = prompt("Capability key (e.g., offer_engine):");
        if (!key) return;
        const name = prompt("Name:", key);
        await api("/ucii/capabilities", "POST", { key, name, category: "custom", status: "active" });
        toast("Capability created"); render();
      } else if (action === "newDomain") {
        const key = prompt("Domain key (e.g., commerce):");
        if (!key) return;
        await api("/ucii/domains", "POST", { key, status: "active" });
        toast("Domain created"); render();
      } else if (action === "newPolicy") {
        const key = prompt("Policy key (e.g., max_discount_limit):");
        if (!key) return;
        const domain = prompt("Domain:", "commerce");
        await api("/ucii/policies", "POST", { key, domain, rule: "{}", status: "active" });
        toast("Policy created"); render();
      } else if (action === "newWorkflow") {
        const key = prompt("Workflow key (e.g., order_fulfillment):");
        if (!key) return;
        const domain = prompt("Domain:", "commerce");
        await api("/ucii/workflows", "POST", { key, domain, trigger: "event", steps: "[]", status: "active" });
        toast("Workflow created"); render();
      } else if (action === "newSchema") {
        const key = prompt("Entity schema key (e.g., customer_extension):");
        if (!key) return;
        const label = prompt("Label:", key);
        await api("/meta/entity-def", "POST", { key, label, icon: "📋", fields: [] });
        toast("Schema created"); render();
      }
    } catch (e) { toast(e.message); }
  });
  
  // Click on capability to configure
  $$("[data-cap]").forEach(b => b.onclick = async () => {
    const capKey = b.dataset.cap;
    try {
      const [cap, config] = await Promise.all([
        api("/ucii/capabilities"),
        api("/ucii/config", "GET", { key: capKey, scope: "platform" })
      ]);
      const capability = cap.capabilities.find(c => c.key === capKey);
      if (!capability) { toast("Capability not found"); return; }
      
      const configData = config.config || {};
      const configStr = JSON.stringify(configData, null, 2);
      
      const configBody = `
        <div class="p-panel"><h3>Configure ${esc(capability.name)}</h3>
          <textarea id="capConfig" rows="12" style="width:100%;font-family:monospace">${esc(configStr)}</textarea>
          <div style="margin-top:10px">
            <button class="p-btn primary" id="saveCapConfig">Save Configuration</button>
            <button class="p-btn" id="cancelCapConfig">Cancel</button>
          </div>
        </div>`;
      
      const modal = document.createElement("div");
      modal.className = "p-modal";
      modal.id = "capConfigModal";
      modal.innerHTML = configBody;
      document.body.appendChild(modal);
      modal.style.display = "block";
      
      document.getElementById("saveCapConfig").onclick = async () => {
        try {
          const newConfig = JSON.parse(document.getElementById("capConfig").value);
          await api("/ucii/config", "POST", { key: capKey, value: newConfig, scope: "platform" });
          toast("Configuration saved");
          modal.remove();
          render();
        } catch (e) {
          alert("Invalid JSON: " + e.message);
        }
      };
      
      document.getElementById("cancelCapConfig").onclick = () => { modal.remove(); };
    } catch (e) { toast(e.message); }
  });
}
/* UCOS Ω∞ Constitution — the two Architecture documents parsed into a canonical registry.
   The console only ever READS the seeded tables; the documents remain the single truth. */
async function vUCOS() {
  const [man, docs, h] = await Promise.all([api("/ucos/manifest"), api("/ucos/docs"), api("/ucos/health").catch(() => null)]);
  const stat = k => k.toLocaleString();
  const hc = h || {};
  const badge = hc.ok
    ? '<span class="badge published">healthy</span>'
    : '<span class="badge failed">' + esc(hc.status || "unknown") + '</span>';
  const probs = (hc.problems || []).map(p2 => '<div class="p-tag" style="margin:3px 0">' + esc(p2.severity || "warn") + " · " + esc(p2.code) + " — " + esc(p2.detail || "") + '</div>').join("");
  return `
  <div class="p-panel"><h2>♾️ UCOS Ω∞ · Constitutional Registry</h2>
    <p class="p-tag">Knowledge-Once · Configuration-Over-Code · Registry-First — the Architecture documents are parsed, never transcribed. Every row points back to its source line.</p>
    <div style="display:flex;align-items:center;gap:8px;margin:10px 0;flex-wrap:wrap">
      ${badge}
      <span class="p-tag">sections ${stat((hc.counts || {}).sections || 0)} · articles ${stat((hc.counts || {}).articles || 0)} · concepts ${stat((hc.counts || {}).concepts || 0)} · edges ${stat((hc.counts || {}).edges || 0)}</span>
      <button class="p-btn sm" id="ucosHealthBtn">↻ Health</button>
      <button class="p-btn sm" id="ucosDriftBtn">Drift check</button>
    </div>
    ${probs ? '<div class="p-card" style="padding:10px;margin-bottom:10px">' + probs + '</div>' : ""}
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:12px;margin-top:14px">
      ${(docs.documents || []).map(d => `
        <div class="p-card" style="padding:14px">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <div><b>${esc(d.code)} Ω∞</b><div class="p-tag" style="font-size:12px">${esc(d.kind)}</div></div>
            <span class="badge active">${stat(d.sections + d.articles)} containers</span>
          </div>
          <div style="font-size:13px;margin:8px 0;color:var(--p-fg)">${esc(d.name)}</div>
          <div class="p-tag">📄 ${esc(d.file)} · ${stat(d.lines)} lines</div>
          <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:8px">
            <span class="p-tag">Parts ${stat(d.parts)}</span>
            <span class="p-tag">Sections ${stat(d.sections)}</span>
            <span class="p-tag">Articles ${stat(d.articles)}</span>
            <span class="p-tag">Concepts ${stat(d.concepts)}</span>
            <span class="p-tag">Registries ${stat(d.registries)}</span>
          </div>
          <div style="margin-top:10px;display:flex;gap:6px;flex-wrap:wrap">
            <button class="p-btn sm" data-browse="${esc(d.doc_id)}" data-kind="sections">Sections</button>
            <button class="p-btn sm" data-browse="${esc(d.doc_id)}" data-kind="articles">Articles</button>
            <button class="p-btn sm" data-browse="${esc(d.doc_id)}" data-kind="concepts">Concepts</button>
            <button class="p-btn sm" data-browse="${esc(d.doc_id)}" data-kind="registries">Registries</button>
          </div>
        </div>`).join("")}
    </div>
    <div style="margin-top:16px">
      <h3>🔎 Search the constitution</h3>
        <div style="display:flex;gap:8px">
          <input id="ucosQ" placeholder="e.g. quantum, entitlement, quantity…" class="p-form" style="flex:1;padding:10px 12px;border-radius:10px;border:1px solid var(--p-line);background:var(--p-bg);color:var(--p-text);font-size:13.5px">
          <button class="p-btn primary" id="ucosGo">Search</button>
        </div>
      <div id="ucosResults" style="margin-top:10px"></div>
      <div id="ucosPager" style="margin-top:6px;display:flex;gap:8px;align-items:center"></div>
    </div>
    <div style="margin-top:16px">
      <button class="p-btn" data-action="ucosReparse">↻ Re-parse documents (idempotent)</button>
      <span class="p-tag" style="margin-left:8px">Re-reads the source files; duplicates are prevented by unique keys</span>
    </div>
  </div>`;
}
function wireUCOS() {
  const stat2 = n => Number(n || 0).toLocaleString();
  /* registry list items render as chips, not a raw JSON blob */
  const renderItems = items => (Array.isArray(items) ? items : [])
    .map(i => '<span class="p-tag" style="margin:2px">' + esc(typeof i === "string" ? i : (i && i.name) || JSON.stringify(i)) + '</span>').join(" ");
  /* a page of rows: sections/articles/concepts/registries share this renderer */
  const renderResults = (rows, kind) => {
    const el = document.getElementById("ucosResults");
    if (!el) return;
    if (!rows.length) { el.innerHTML = '<p class="p-tag">No matches.</p>'; return; }
    el.innerHTML = rows.map(r => {
      if (kind === "registries") return '<div class="p-card" style="padding:10px;margin:6px 0;font-size:13px">' +
        '<b>' + esc(r.name) + '</b> <span class="p-tag">' + esc(r.container_name || "") + ' · line ' + stat2(r.line) + '</span>' +
        '<div style="margin-top:5px">' + renderItems(r.items) + '</div></div>';
      return '<div class="p-card" style="padding:10px;margin:6px 0;font-size:13px">' +
        '<b>' + esc(r.name) + '</b> <span class="p-tag">' + esc(kind) + ' · line ' + stat2(r.line) + '</span>' +
        (r.container ? '<div class="p-tag">in ' + esc(r.container) + '</div>' : "") +
        '<button class="p-btn sm" style="margin-left:6px" data-graph="' + esc(r.doc || "") + '" data-gtype="' + esc(kind === "concepts" ? "concept" : "section") + '" data-gid="' + esc(r.qkey || r.key || "") + '" data-gname="' + esc((r.name || "").slice(0, 40)) + '" data-gcontainer="' + esc(r.container || "") + '">⌘ graph</button>' +
        '<button class="p-btn sm" data-ann="' + esc(r.doc || "") + '" data-akind="' + esc(kind === "concepts" ? "concept" : "section") + '" data-akey="' + esc(r.qkey || r.key || "") + '">✎ annotate</button>' +
        '<div class="ucos-ann-list" data-annlist="' + esc(r.doc || "") + '|' + esc(kind === "concepts" ? "concept" : "section") + '|' + esc(r.qkey || r.key || "") + '"></div>' +
        '</div>';
    }).join("");
    wireGraph();
    wireAnnotate();
  };
  /* annotation layer: inline notes per row, plus a composer; the documents stay read-only */
  const wireAnnotate = () => {
    $('[data-annlist]').forEach(el => loadAnnotations(el));
    $('[data-ann]').forEach(b => b.onclick = () => {
      const doc = b.dataset.ann, kind = b.dataset.akind, key = b.dataset.akey;
      const list = document.querySelector('[data-annlist="' + doc + '|' + kind + '|' + key + '"]');
      if (!list) return;
      if (list.dataset.open === '1') { list.dataset.open = '0'; list.innerHTML = ''; return; }
      list.dataset.open = '1';
      const boxId = 'annTxt_' + key.replace(/[^A-Za-z0-9_-]/g, '_');
      list.innerHTML = '<div style="margin-top:6px;padding:8px;border:1px dashed var(--p-line);border-radius:8px">' +
        '<textarea id="' + boxId + '" rows="2" placeholder="Add an operator note (the document itself is never edited)…" style="width:100%;padding:6px;border-radius:6px;border:1px solid var(--p-line);background:var(--p-bg);color:var(--p-text);font-size:12.5px"></textarea>' +
        '<label style="font-size:12px;margin:4px 0;display:inline-block"><input type="checkbox" id="annPin_' + key.replace(/[^A-Za-z0-9_-]/g, '_') + '"> pin to top</label>' +
        '<button class="p-btn sm primary" data-annsave="' + doc + '|' + kind + '|' + key + '">Save</button></div>';
      const save = list.querySelector('[data-annsave]');
      if (save) save.onclick = async () => {
        const txt = (list.querySelector('textarea') || {}).value;
        const pin = !!(list.querySelector('input[type=checkbox]') || {}).checked;
        if (!txt || !txt.trim()) { toast('note is required'); return; }
        try {
          const r = await api('/ucos/' + doc + '/annotations', 'POST', { kind, key, note: txt, pin });
          if (!r.ok) { toast(r.error); return; }
          toast('Annotation saved');
          loadAnnotations(list);
        } catch (e) { toast(e.message); }
      };
    });
  };
  const loadAnnotations = async el => {
    const parts = (el.dataset.annlist || '').split('|');
    if (parts.length < 3) return;
    const doc = parts[0], kind = parts[1], key = parts.slice(2).join('|');
    const wasOpen = el.dataset.open === '1';
    if (!wasOpen) return;
    try {
      const r = await api('/ucos/' + doc + '/annotations', 'GET', { kind, key, limit: 20 });
      el.innerHTML = (r.rows || []).map(a => '<div class="p-card" style="padding:6px 8px;margin:4px 0;font-size:12px">' +
        (a.pin ? '<span class="badge published">pinned</span> ' : '') +
        esc(a.note) + '<span class="p-tag">' + esc(a.created_by || '') + ' · ' + esc((a.updated_at || '').slice(0, 10)) + '</span>' +
        '<button class="p-btn sm danger" data-anndel="' + a.id + '" data-anndoc="' + doc + '" style="margin-left:4px">✕</button></div>').join('') +
        ((r.total || 0) > (r.rows || []).length ? '<div class="p-tag">' + ((r.total) - (r.rows || []).length) + ' more…</div>' : '');
      el.querySelectorAll('[data-anndel]').forEach(d => d.onclick = async () => {
        try { const rr = await api('/ucos/' + d.dataset.anndoc + '/annotations/' + d.dataset.anndel, 'DELETE'); if (!rr.ok) { toast(rr.error); return; } toast('Annotation removed'); loadAnnotations(el); }
        catch (e) { toast(e.message); }
      });
    } catch (e) { /* reads are best-effort; the row still renders */ }
  };
  /* paginated browser: keeps a cursor so Next/Prev walk the real total */
  let cursor = { doc: "", kind: "", offset: 0, limit: 25, part: null, q: null };
  const renderPager = (total, offset, limit) => {
    const el = document.getElementById("ucosPager");
    if (!el) return;
    const pages = Math.ceil(total / limit) || 1;
    const cur = Math.floor(offset / limit) + 1;
    el.innerHTML = '<span class="p-tag">' + stat2(total) + ' rows · page ' + cur + ' / ' + pages + '</span> ' +
      (offset > 0 ? '<button class="p-btn sm" data-pg="prev">← Prev</button>' : "") +
      (offset + limit < total ? '<button class="p-btn sm" data-pg="next">Next →</button>' : "");
    el.querySelectorAll("[data-pg]").forEach(b => b.onclick = () => loadPage(b.dataset.pg === "next" ? cursor.offset + cursor.limit : Math.max(0, cursor.offset - cursor.limit)));
  };
  const loadPage = async offset => {
    const c = cursor;
    try {
      const params = { limit: c.limit, offset: offset == null ? c.offset : offset };
      if (c.part != null) params.part = c.part;
      if (c.q) params.q = c.q;
      const r = await api(`/ucos/${c.doc}/${c.kind}`, "GET", params);
      c.offset = offset == null ? c.offset : offset;
      const rows = r[c.kind] || [];
      renderResults(rows.map(x => Object.assign({ doc: c.doc }, x, { name: x.name || x.label || x.qkey, container: x.container_name || x.container || x.title || "" })), c.kind);
      renderPager(Number(r.total || rows.length), Number(r.offset || 0), Number(r.limit || c.limit));
    } catch (e) { toast(e.message); }
  };
  $$("[data-browse]").forEach(b => b.onclick = () => {
    cursor = { doc: b.dataset.browse, kind: b.dataset.kind, offset: 0, limit: 25, part: null, q: null };
    loadPage(0);
  });
  const go = async () => {
    const q = (document.getElementById("ucosQ") || {}).value;
    if (!q) return;
    try { const r = await api("/ucos/search", "GET", { q, limit: 30 }); renderResults(r.results || [], "search"); }
    catch (e) { toast(e.message); }
  };
  const btn = document.getElementById("ucosGo");
  if (btn) btn.onclick = go;
  const inp = document.getElementById("ucosQ");
  if (inp) inp.onkeydown = e => { if (e.key === "Enter") go(); };
  $$("[data-action='ucosReparse']").forEach(b => b.onclick = async () => {
    try { const r = await api("/ucos/reparse", "POST", {}); toast(`Re-parsed: ${r.stats.sections} sections, ${r.stats.concepts} concepts, ${r.stats.edges} edges`); render(); }
    catch (e) { toast(e.message); }
  });
  const hb = document.getElementById("ucosHealthBtn");
  if (hb) hb.onclick = () => render();
  const dbtn = document.getElementById("ucosDriftBtn");
  if (dbtn) dbtn.onclick = async () => {
    try { const r = await api("/ucos/drift", "GET", {}); toast(r.drifted ? "⚠ " + r.message : "✓ " + r.message); }
    catch (e) { toast(e.message); }
  };
  /* graph explorer: a node and its immediate neighbourhood as radial SVG */
  const wireGraph = () => {
    $$("[data-graph]").forEach(b => b.onclick = async () => {
      const doc = b.dataset.graph, type = b.dataset.gtype, id = b.dataset.gid;
      if (!doc || !id) return;
      try {
        const r = await api(`/ucos/${doc}/neighbours`, "GET", { type, id, limit: 60 });
        drawGraph(doc, type, id, b.dataset.gname || id, b.dataset.gcontainer || "", r);
      } catch (e) { toast(e.message); }
    });
  };
  const drawGraph = (doc, type, id, name, container, r) => {
    const el = document.getElementById("ucosResults");
    if (!el) return;
    const edges = r.edges || [], names = r.names || {};
    const cx = 220, cy = 180, R = 120;
    const label = (t, i2) => names[t + "|" + i2] || i2;
    const pts = edges.map((e, i2) => {
      const isSrc = e.source_type === type && String(e.source_id) === String(id);
      const other = isSrc ? { t: e.target_type, id: e.target_id, rel: e.rel } : { t: e.source_type, id: e.source_id, rel: e.rel };
      const ang = (i2 / Math.max(1, edges.length)) * Math.PI * 2 - Math.PI / 2;
      return { x: cx + R * Math.cos(ang), y: cy + R * Math.sin(ang), t: other.t, id: other.id, rel: other.rel, name: label(other.t, other.id) };
    });
    el.innerHTML = '<div class="p-card" style="padding:12px">' +
      '<div style="display:flex;justify-content:space-between;align-items:center"><b>⌘ Knowledge graph · ' + esc(name) + '</b>' +
      '<button class="p-btn sm" id="ucosGraphClose">close</button></div>' +
      '<div class="p-tag">' + esc(type) + ' · ' + esc(container || doc) + ' · ' + edges.length + ' edge(s)</div>' +
      '<svg viewBox="0 0 440 360" style="width:100%;max-width:560px;margin-top:8px">' +
      pts.map(p2 => '<line x1="' + cx + '" y1="' + cy + '" x2="' + (+p2.x.toFixed(1)) + '" y2="' + (+p2.y.toFixed(1)) + '" stroke="var(--p-line)" stroke-width="1"/>').join("") +
      pts.map(p2 => '<g data-node="' + esc(p2.t + "|" + p2.id) + '" style="cursor:pointer"><circle cx="' + (+p2.x.toFixed(1)) + '" cy="' + (+p2.y.toFixed(1)) + '" r="5" fill="' + (p2.t === "concept" ? "#6b8cff" : p2.t === "section" ? "#37b24d" : "#868e96") + '"/><text x="' + (+p2.x.toFixed(1)) + '" y="' + (+p2.y.toFixed(1) - 9) + '" font-size="9" text-anchor="middle" fill="var(--p-text)">' + esc((p2.name || p2.id || "").slice(0, 26)) + '</text></g>').join("") +
      '<circle cx="' + cx + '" cy="' + cy + '" r="9" fill="var(--p-accent)"/><text x="' + cx + '" y="' + (cy - 14) + '" font-size="10" font-weight="bold" text-anchor="middle" fill="var(--p-text)">' + esc((name || id).slice(0, 30)) + '</text>' +
      '</svg></div>';
    const cl = document.getElementById("ucosGraphClose");
    if (cl) cl.onclick = () => { el.innerHTML = ""; };
    el.querySelectorAll("[data-node]").forEach(g => g.onclick = () => {
      const parts = g.dataset.node.split("|");
      const t = parts[0], nid = parts.slice(1).join("|");
      if (!t || !nid) return;
      api(`/ucos/${doc}/neighbours`, "GET", { type: t, id: nid, limit: 60 })
        .then(rr => drawGraph(doc, t, nid, names[t + "|" + nid] || nid, "", rr))
        .catch(e2 => toast(e2.message));
    });
  };
}
/* Universes — every universe the corpus declares, instantiated as a live, data-defined
   entity. Coverage is the measurable answer to "is everything implemented?" */
const stat2 = n => Number(n || 0).toLocaleString();
async function vUniverses() {
  const d = await api("/ucos/universes");
  const st = d.stats || {};
  const cov = st.coverage || 0;
  const badge = cov === 100 ? '<span class="badge published">100% instantiated</span>'
    : '<span class="badge failed">' + cov + '% instantiated</span>';
  const rows = (d.universes || []).map(u => `
    <tr>
      <td><b>${esc(u.name)}</b><div class="p-tag" style="font-size:11px">${esc(u.entity_key)}</div></td>
      <td>${esc(u.source_doc)}:${u.source_line || "?"}</td>
      <td>${stat2(u.concepts || 0)}</td>
      <td>${stat2(u.records || 0)}</td>
      <td><span class="badge ${u.lifecycle === "canonical" ? "active" : "failed"}">${esc(u.lifecycle || "—")}</span></td>
      <td style="text-align:right;white-space:nowrap">
        <button class="p-btn sm" data-uv="${esc(u.entity_key)}">Records</button>
        <button class="p-btn sm primary" data-uvpub="${esc(u.entity_key)}">→ Storefront</button>
        ${u.records ? '<button class="p-btn sm danger" data-uvwd="' + esc(u.entity_key) + '">Withdraw</button>' : ""}
      </td>
    </tr>`).join("");
  /* activation publishes into ONE store's catalog — the platform console must say which.
     No silent default: the selector remembers the operator's choice and the actions read it. */
  if (!window.__tenantId && P.tenants.length) window.__tenantId = P.tenants[0].id;
  const tidOpts = P.tenants.map(t => `<option value="${t.id}" ${Number(window.__tenantId) === t.id ? "selected" : ""}>${esc(t.name)} (${esc(t.slug)})</option>`).join("");
  return `
  <div class="p-panel"><h2>🧬 Universes · instantiated from the constitution</h2>
    <p class="p-tag">Each universe the Architecture documents declare is registered as a foundation and instantiated as a live, data-defined entity — zero per-universe code (Article 4.2). Fields are derived from the corpus itself.</p>
    <div style="display:flex;gap:8px;align-items:center;margin:10px 0;flex-wrap:wrap">
      ${badge}
      <span class="p-tag">${stat2(st.declared || 0)} declared · ${stat2(st.instantiated || 0)} instantiated · ${stat2(st.live || 0)} canonical · ${stat2(st.records || 0)} records created</span>
      <label class="p-tag" style="display:flex;align-items:center;gap:6px">Target store
        <select id="uvTenant" style="min-width:170px">${tidOpts}</select>
      </label>
      <button class="p-btn sm" id="uvRefresh">↻ Re-instantiate</button>
      <button class="p-btn sm primary" id="uvActivateAll">⚡ Activate all → storefront</button>
    </div>
    <div style="max-height:60vh;overflow:auto;border:1px solid var(--p-line);border-radius:10px">
      <table style="width:100%;border-collapse:collapse;font-size:13px">
        <thead><tr style="text-align:left;color:var(--p-fg)"><th style="padding:8px">Universe</th><th>Source</th><th>Concepts</th><th>Records</th><th>Lifecycle</th><th></th></tr></thead>
        <tbody>${rows || '<tr><td colspan="6" class="p-tag">No universes instantiated yet — run Re-instantiate.</td></tr>'}</tbody>
      </table>
    </div>
  </div>`;
}
function wireUniverses() {
  /* the target store is the operator's explicit choice — never a hardcoded tenant. The
     selector is the single source; every activation/publish/withdraw reads it here. */
  const sel = document.getElementById("uvTenant");
  if (sel) { sel.onchange = () => { window.__tenantId = Number(sel.value); }; window.__tenantId = Number(sel.value); }
  const target = () => { const t = Number(window.__tenantId); if (!t) { toast("Select a target store first"); return null; } return t; };
  const refresh = document.getElementById("uvRefresh");
  if (refresh) refresh.onclick = async () => {
    try {
      const r = await api("/ucos/universes/instantiate", "POST", {});
      toast((r.stats && r.stats.coverage === 100) ? "All " + stat2(r.stats.instantiated) + " universes instantiated" : "Instantiated " + r.instantiated + " of " + r.discovered);
      render();
    } catch (e) { toast(e.message); }
  };
  /* ACTIVATE ALL: materialize every universe's canonical offering and publish it into the
     selected tenant's catalog, so the whole constitution becomes shopper-
     transactable in one action. Bounded and idempotent — a warm pass skips what is
     already on the shelf. */
  const actAll = document.getElementById("uvActivateAll");
  if (actAll) actAll.onclick = async () => {
    const tid = target(); if (tid === null) return;
    if (!confirm("Publish a canonical offering for every universe into this store's catalog? Existing records are kept; already-published universes are skipped.")) return;
    try {
      const r = await api("/ucos/catalog/activate?tenant_id=" + tid, "POST", { limit: 250 });
      if (r.ok) toast("Activated " + stat2(r.activated) + " universes · " + stat2(r.published) + " offerings published" + (r.remaining ? " · " + stat2(r.remaining) + " remain (activate again)" : " · complete"));
      else toast("Activated " + stat2(r.activated) + " · " + stat2(r.failed) + " failed");
      render();
    } catch (e) { toast(e.message); }
  };
  /* publish a universe's records into the selected tenant's storefront — the record
     becomes shopper-transactable through the standard catalog/cart/checkout path */
  /* open this universe's records in the Data Studio, pre-selected and auto-loaded —
     the Studio is the console's record browser; the definitions view only lists shapes */
  document.querySelectorAll("[data-uv]").forEach(b => b.onclick = () => {
    window.__entityJump = b.dataset.uv;
    view = "studio";
    render();
  });
  document.querySelectorAll("[data-uvpub]").forEach(b => b.onclick = async () => {
    const tid = target(); if (tid === null) return;
    const key = b.dataset.uvpub;
    try {
      /* activate, not just publish: if the universe has no offering yet, its canonical
         one is materialized first, so the button is never a silent no-op */
      const r = await api("/ucos/catalog/" + key + "/activate?tenant_id=" + tid, "POST", {});
      toast(r.ok ? "Published " + r.published + " record(s) to the storefront" + (r.materialized ? " (canonical offering created)" : "") : (r.error || "publish failed"));
      render();
    } catch (e) { toast(e.message); }
  });
  document.querySelectorAll("[data-uvwd]").forEach(b => b.onclick = async () => {
    const tid = target(); if (tid === null) return;
    const key = b.dataset.uvwd;
    try {
      const r = await api("/ucos/catalog/" + key + "/withdraw?tenant_id=" + tid, "POST", {});
      toast(r.ok ? "Withdrew " + r.removed + " record(s) from the storefront" : (r.error || "withdraw failed"));
      render();
    } catch (e) { toast(e.message); }
  });
}
/* Foundations — the UCOS Article 2-8 registry: canonical form, five graphs,
   lifecycle, admission rules and the append-only audit ledger. */
async function vFoundations() {
  const [man, v] = await Promise.all([api("/ucos/foundations/manifest"), api("/ucos/foundations/verify").catch(() => null)]);
  const byU = man.byUniverse || [];
  const byL = man.byLifecycle || {};
  const checkRow = (label, ok2) => `<div class="p-tag" style="margin:3px 0">${ok2 ? "✓" : "✗"} ${esc(label)}</div>`;
  return `
  <div class="p-panel"><h2>🏛️ Foundations · the operational registry</h2>
    <p class="p-tag">Architecture3 Articles 2-8, executed: canonical form, the five graphs, admission, lifecycle and the audit ledger — all enforced in code.</p>
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin:10px 0;align-items:center">
      <span class="badge ${(v && v.ok) ? "published" : "failed"}">${(v && v.ok) ? "all invariants hold" : "invariant violations"}</span>
      <span class="p-tag">${stat2((man.populations || {}).foundations || 0)} foundations · ${stat2((man.populations || {}).dependencies || 0)} dependency edges</span>
      <button class="p-btn sm" id="fdVerify">↻ Verify invariants</button>
      <button class="p-btn sm" id="fdLedger">Audit ledger</button>
    </div>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px">
      <div class="p-card" style="padding:12px">
        <b>Article 3.2 / 8.2 invariants</b>
        <div style="margin-top:6px">
          ${v ? ["identitiesUnique", "dependenciesResolve", "acyclic", "noOrphans"].map(k => checkRow(k + " — " + (v.checks[k] ? "ok" : "VIOLATED"), v.checks[k])).join("") : '<div class="p-tag">unavailable</div>'}
        </div>
      </div>
      <div class="p-card" style="padding:12px">
        <b>Article 5.1 lifecycle</b>
        <div style="margin-top:6px;display:flex;gap:6px;flex-wrap:wrap">
          ${man.lifecycle.map(s => '<span class="p-tag">' + esc(s) + " " + stat2(byL[s] || 0) + '</span>').join("")}
        </div>
      </div>
      <div class="p-card" style="padding:12px">
        <b>Article 3.1 graphs</b>
        <div style="margin-top:6px">${Object.entries(man.graphs || {}).map(([k, d]) => '<div class="p-tag" style="margin:3px 0">' + esc(k) + " — " + esc(d) + '</div>').join("")}</div>
      </div>
    </div>
    <h3 style="margin-top:16px">Largest universes</h3>
    <div style="max-height:34vh;overflow:auto;border:1px solid var(--p-line);border-radius:10px">
      <table style="width:100%;border-collapse:collapse;font-size:13px">
        <thead><tr style="text-align:left"><th style="padding:8px">Universe</th><th>Foundations</th></tr></thead>
        <tbody>${byU.slice(0, 40).map(u => `<tr><td style="padding:6px 8px">${esc(u.universe || "(universe)")}</td><td>${stat2(u.n)}</td></tr>`).join("") || '<tr><td class="p-tag">none</td></tr>'}</tbody>
      </table>
    </div>
  </div>`;
}
function wireFoundations() {
  const verify = document.getElementById("fdVerify");
  if (verify) verify.onclick = async () => { try { const r = await api("/ucos/foundations/verify"); toast(r.ok ? "Invariants hold · " + stat2(r.populations.foundations) + " foundations" : "VIOLATIONS: " + JSON.stringify(r.violations)); render(); } catch (e) { toast(e.message); } };
  const ledger = document.getElementById("fdLedger");
  if (ledger) ledger.onclick = async () => {
    try {
      const r = await api("/ucos/foundations/ledger?limit=60");
      const evs = (r.events || []).map(e => `<tr><td style="padding:6px 8px">${esc(e.at || "")}</td><td><b>${esc(e.event)}</b></td><td>${esc(e.foundation)}</td></tr>`).join("");
      alert("Append-only audit ledger (Article 6)\n\n" + (r.events || []).slice(0, 20).map(e => e.at + "  " + e.event + "  " + e.foundation).join("\n"));
    } catch (e) { toast(e.message); }
  };
}
/* Traceability — where is each corpus declaration implemented? The matrix at a
   glance, and a per-key trace through every runtime layer. */
let trKey = "";
async function vTrace() {
  const m = await api("/ucos/matrix");
  const t = trKey ? await api("/ucos/trace?key=" + encodeURIComponent(trKey)).catch(() => null) : null;
  const docRows = (m.perDocument || []).map(d => `<tr><td><b>${esc(d.doc)}</b></td><td class="p-tag">${esc(d.file)}</td><td class="num">${stat2(d.concepts)}</td><td class="num">${stat2(d.foundations)}</td><td class="num">${stat2(d.universes)}</td><td class="num">${d.conceptCoverage}%</td></tr>`).join("");
  const layerRow = l => `<tr><td style="padding:6px 8px">${l.present ? "✓" : "✗"}</td><td><b>${esc(l.layer)}</b></td><td class="num">${stat2(l.n)}</td>
    <td class="p-tag" style="max-width:420px;word-break:break-word">${esc(JSON.stringify(l.artifacts).slice(0, 300))}</td></tr>`;
  return `
  <div class="p-panel"><h2>🧭 Traceability · corpus → runtime</h2>
    <p class="p-tag">Every declaration maps to runtime artifacts: registry concept → foundation → universe → live entity → records → catalog projection → API → console. Absent layers are reported, not hidden.</p>
    <div style="display:flex;gap:8px;align-items:center;margin:10px 0;flex-wrap:wrap">
      <span class="badge published">${stat2((m.corpus || {}).concepts || 0)} concepts · ${stat2((m.corpus || {}).documents || 0)} documents</span>
      <span class="badge published">${stat2((m.implementation || {}).universes || 0)} universes · ${stat2((m.implementation || {}).liveEntities || 0)} live entities</span>
      <span class="badge ${((m.implementation || {}).catalogProjections || 0) ? "published" : "draft"}">${stat2((m.implementation || {}).catalogProjections || 0)} catalog projections</span>
    </div>
    <div class="p-scroll-x" style="margin-bottom:14px"><table class="p-table"><thead><tr><th>Doc</th><th>File</th><th>Concepts</th><th>Foundations</th><th>Universes</th><th>Concept→foundation</th></tr></thead>
      <tbody>${docRows || '<tr><td colspan="6" class="p-empty">no documents</td></tr>'}</tbody></table></div>
    ${(m.notes || []).map(x2 => `<p class="p-tag" style="margin:2px 0">· ${esc(x2)}</p>`).join("")}
    <h3 style="margin-top:16px">Trace a key</h3>
    <div style="display:flex;gap:8px;margin:8px 0">
      <input id="trKey" value="${esc(trKey)}" placeholder="e.g. Insurance, uv_streaming_product, Streaming Product" style="flex:1;padding:7px 10px;border:1px solid var(--p-border);border-radius:8px;background:var(--p-bg)">
      <button class="p-btn primary sm" id="trGo">Trace</button>
    </div>
    ${t ? `<p style="margin:6px 0"><b>${esc(t.key)}</b> — ${esc(t.verdict)}</p>
      <div class="p-scroll-x"><table class="p-table"><thead><tr><th></th><th>Layer</th><th>n</th><th>Artifacts</th></tr></thead>
      <tbody>${(t.layers || []).map(layerRow).join("")}</tbody></table></div>`
      : '<p class="p-tag">Enter a key to see every runtime layer it resolves to.</p>'}
  </div>`;
}
function wireTrace() {
  const go = document.getElementById("trGo");
  if (go) go.onclick = () => { trKey = document.getElementById("trKey").value.trim(); render(); };
  const inp = document.getElementById("trKey");
  if (inp) inp.onkeydown = e => { if (e.key === "Enter") { trKey = inp.value.trim(); render(); } };
}
/* Domains — every universe's records move through the corpus's own state machine
   (UCOS 5.1 states + 5.2 rules, UMQSOCR Art. 10 components). Rendered as a board:
   one column per state, records advance by rule-gated transitions. Zero per-domain
   code — the machine is derived from the constitution for all 1,877 universes. */
let dmKey = "";
async function vDomains() {
  const all = await api("/ucos/domains");
  const list = all.domains || [];
  if (!dmKey && list.length) dmKey = list[0].entityKey;
  const d = dmKey ? await api("/ucos/domain/" + encodeURIComponent(dmKey)).catch(() => null) : null;
  const cols = (d ? d.states : []).map(st => {
    const n = (d && d.byState && d.byState[st]) || 0;
    return `<div style="flex:1;min-width:110px;background:var(--p-bg);border:1px solid var(--p-line);border-radius:10px;padding:8px">
      <div style="font-size:12px;font-weight:600;color:var(--p-fg)">${esc(st)}</div>
      <div style="font-size:20px;font-weight:700;margin:4px 0;color:var(--p-fg)">${n}</div>
      <div style="height:4px;border-radius:2px;background:var(--p-line);overflow:hidden"><div style="height:100%;width:${d && d.records ? Math.min(100, Math.round(n / d.records * 100)) : 0}%;background:var(--p-accent)"></div></div>
    </div>`;
  }).join("");
  const recRows = d ? (d.records_ || []) : [];
  return `
  <div class="p-panel"><h2>🔀 Domains · corpus-declared state machines</h2>
    <p class="p-tag">Each universe is a domain: its records advance through the lifecycle the constitution declares — states (UCOS 5.1), rules (5.2), and the Art. 10 transition grammar. Transitions are refused unless the rule holds, and every move is append-audited (Art. 6). No per-domain code.</p>
    <div style="display:flex;gap:8px;align-items:center;margin:10px 0;flex-wrap:wrap">
      <select id="dmSel" style="padding:7px 10px;border:1px solid var(--p-border);border-radius:8px;background:var(--p-bg);max-width:340px">
        ${list.map(x => `<option value="${esc(x.entityKey)}" ${x.entityKey === dmKey ? "selected" : ""}>${esc(x.universe)} · ${x.records} records</option>`).join("")}
      </select>
      <span class="p-tag">${d ? stat2(d.records) + " records · " + stat2(d.transitions) + " transitions logged" : ""}</span>
      <span class="p-tag">source ${d ? esc(d.source) : "—"}</span>
    </div>
    <div style="display:flex;gap:8px;overflow-x:auto;padding-bottom:8px">${cols || '<div class="p-empty">No universe selected</div>'}</div>
    <h3 style="margin-top:12px">Records</h3>
    <div class="p-scroll-x"><table class="p-table"><thead><tr><th>Record</th><th>State</th><th>Next transition</th><th>Rule</th><th></th></tr></thead>
    <tbody>${recRows.length ? recRows.map(r => {
      const av = r.available ? r.available[0] : null;
      return `<tr><td><b>${esc(r.name)}</b><div class="p-tag" style="font-size:11px">#${r.id}</div></td>
        <td><span class="badge ${esc(String(r.status || d.states[0]).toLowerCase())}">${esc(r.status || d.states[0])}</span></td>
        <td class="p-tag">${av ? esc(av.from) + " → " + esc(av.to) : "terminal"}</td>
        <td class="p-tag">${av && av.blocked ? '<span style="color:var(--p-red)">⛔ ' + esc(av.blocked) + '</span>' : (av && av.condition ? '<span style="color:var(--p-green)">✓ ' + esc(av.condition) + '</span>' : "—")}</td>
        <td>${av ? `<button class="p-btn sm ${av.blocked ? "" : "primary"}" data-dmfire="${r.id}">${av.blocked ? "Blocked" : "Advance"}</button>` : ""}</td></tr>`;
    }).join("") : '<tr><td colspan="5" class="p-empty">No records yet — create some in the Data Studio, or activate the universe.</td></tr>'}</tbody></table></div>
    <p class="p-tag" style="margin-top:10px">Transition grammar (UMQSOCR Art. 10): ${d ? d.grammar.map(g => "<code>" + esc(g) + "</code>").join(" · ") : ""}</p>
  </div>`;
}
function wireDomains() {
  const sel = document.getElementById("dmSel");
  if (sel) sel.onchange = () => { dmKey = sel.value; render(); };
  document.querySelectorAll("[data-dmfire]").forEach(b => b.onclick = async () => {
    const rid = b.dataset.dmfire;
    try {
      const r = await api("/ucos/domain/" + encodeURIComponent(dmKey) + "/fire", "POST", { record_id: Number(rid) });
      if (r.ok) toast((r.from || "") + " → " + (r.to || "") + (r.rule ? "  [" + r.rule + "]" : ""));
      else toast(r.error || "transition refused");
      render();
    } catch (e) { toast(e.message); }
  });
}
async function vRuntime() {
  const d = await api("/platform/runtime"); const [eNv, fL] = await Promise.all([api("/platform/environments"), api("/platform/flags")]);
  const rt = d.runtime, cat = d.catalog, active = d.active;
  const concerns = Object.keys(cat.catalog);
  const envRows = (eNv.environments || []).map(e => `<tr><td><b>${esc(e.label)}</b>${e.active ? ' <span class="badge published">ACTIVE</span>' : ""}<br><code>${esc(e.name)}</code></td><td>${esc(e.region || "—")}</td><td class="p-tag">${e.tenants && e.tenants.length ? e.tenants.join(",") : "base"}</td><td>${(e.flags || []).length ? e.flags.map(f => `<code>${esc(f)}</code>`).join(" ") : "—"}</td><td class="p-tag">${Object.entries(e.runtime || {}).map(([k, v]) => `${k}:${v.driver}`).join(" ") || "defaults"}</td>
    <td style="text-align:right;white-space:nowrap"><button class="p-btn sm primary" data-envact="${esc(e.name)}">Activate</button> <button class="p-btn sm" data-envedit="${esc(e.name)}">Edit</button> <button class="p-btn sm danger" data-envdel="${esc(e.name)}">✕</button></td></tr>`).join("");
  const flagRows = Object.entries(fL.flags || {}).map(([k, f]) => `<tr><td><code>${esc(k)}</code></td><td>${esc(f.description || "")}</td><td><span class="badge ${f.default ? "published" : "draft"}">${f.default ? "on" : "off"}</span></td><td class="num">${f.rollout}%</td><td><button class="p-btn sm" data-flagedit="${esc(k)}" data-r="${f.rollout}" data-d="${f.default ? 1 : 0}">edit</button> <button class="p-btn sm danger" data-flagdel="${esc(k)}">✕</button></td></tr>`).join("");
  return `<div class="p-panel"><h2>🧩 Runtime · Infra</h2>
    <p style="color:var(--p-muted);font-size:13px;margin:0 0 12px">Every backend is a <b>config choice</b>. Define unlimited <b>named environments</b> (bundles of driver choices + secrets + feature flags), activate one to swap the whole topology, or set <code>LX_ENV=prod</code> at boot.</p>
    ${d.offline ? '<p class="badge processing" style="display:inline-block;padding:6px 10px;border-radius:8px;margin-bottom:8px">LX_OFFLINE=1 — outbound forced to simulated</p>' : ""}
    <h3>Environments</h3>
    ${envRows ? `<div class="p-scroll-x"><table class="p-table"><thead><tr><th>Environment</th><th>Region</th><th>Tenants</th><th>Flags</th><th>Runtime overlay</th><th></th></tr></thead><tbody>${envRows}</tbody></table></div>` : '<p class="p-tag">No environments yet — the base runtime below is active.</p>'}
    <div class="p-panel" style="margin-top:10px"><b>New environment</b>
      <div style="display:flex;gap:8px;align-items:end;flex-wrap:wrap;margin-top:6px">
        <label><span>Name</span><input id="envName" placeholder="prod-eu"></label>
        <label><span>Region</span><input id="envRegion" placeholder="eu-west-1"></label>
        <label><span>Tenant ids (CSV)</span><input id="envTenants" placeholder="1,4"></label>
        <button class="p-btn sm primary" id="envCreate">Create</button>
        <button class="p-btn sm" id="envExport">Export JSON</button>
        <label style="font-size:12px"><span>Import (JSON)</span><input type="file" id="envImportFile" accept="application/json" style="display:inline-block"></label>
      </div></div>
    <h3 style="margin-top:16px">Feature flags</h3>
    ${flagRows ? `<table class="p-table"><thead><tr><th>Flag</th><th>What</th><th>Default</th><th class="num">Rollout</th><th></th></tr></thead><tbody>${flagRows}</tbody></table>` : '<p class="p-tag">No flags.</p>'}
    <div style="display:flex;gap:8px;align-items:end;flex-wrap:wrap;margin-top:6px"><label><span>New flag</span><input id="flagName" placeholder="checkout.upsells"></label><label><span>Rollout %</span><input id="flagRollout" type="number" value="0" min="0" max="100"></label><label><span>Default on</span><input id="flagDefault" type="checkbox"></label><button class="p-btn sm primary" id="flagSave">Add</button></div>
    <h3 style="margin-top:16px">Base runtime (active now)</h3>
    <table class="p-table"><thead><tr><th>Concern</th><th>Default</th><th>Active</th><th>Driver</th><th>Connection</th></tr></thead><tbody>
      ${concerns.map(k => { const c = cat.catalog[k], cur = rt[k], kinds = c.drivers.map(dr => `<option ${dr === cur.driver ? "selected" : ""}>${dr}</option>`).join(""); const fields = cat.driverFields[cur.driver] || []; const params = cur.params || {}; const inp = fields.map(f => `<label style="display:block;font-size:11px"><span>${esc(f.label)}</span><input data-rtp="${k}.${f.key}" type="${f.secret ? "password" : "text"}" value="${esc(f.secret ? "••••" : (params[f.key] || ""))}" placeholder="${esc(f.key)}"></label>`).join("") || '<span class="p-tag">none</span>'; return `<tr><td><b>${esc(c.label)}</b><br><code>${k}</code></td><td><code>${c.default}</code></td><td><span class="p-tag">${esc(active[k] || cur.driver)}</span></td><td><select data-rt="${k}">${kinds}</select></td><td>${inp}</td></tr>`; }).join("")}
    </tbody></table>
    <div style="margin-top:12px"><button class="p-btn primary sm" id="rtSave">Apply base runtime</button> <button class="p-btn sm" id="rtTest">Test connections</button> <span id="rtTestOut" class="p-tag"></span></div></div>
    <div class="p-panel"><h2>🐘 Database (Postgres cutover)</h2>
      <p style="color:var(--p-muted);font-size:13px;margin:0 0 10px">Set driver <b>postgres</b> + connection string above and save, then dry-run / verify / apply. SQLite is the default; nothing changes until you switch.</p>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px"><button class="p-btn sm" id="dbPing">Test connection</button><button class="p-btn sm" id="dbDry">Dry-run migration</button><button class="p-btn sm primary" id="dbApply">Apply migration</button><button class="p-btn sm danger" id="dbBack">Revert to SQLite</button></div>
      <pre id="dbOut" style="background:#0b0d12;color:#cfe;padding:10px;border-radius:10px;font-size:12px;max-height:220px;overflow:auto">Status loading…</pre>
      <h3 style="margin-top:12px">Regions &amp; Edge / CDN</h3><div id="regWrap" class="p-tag">loading…</div>
    </div>`;
}
function wireRuntime() {
  const $ = s => document.querySelector(s), $$ = s => Array.from(document.querySelectorAll(s));
  const baseBody = () => { const body = {}; $$("[data-rt]").forEach(sel => { body[sel.dataset.rt] = { driver: sel.value }; }); $$("[data-rtp]").forEach(inp => { const [k, field] = inp.dataset.rtp.split("."); body[k] = body[k] || {}; body[k].params = body[k].params || {}; if (inp.value && !inp.value.startsWith("••••")) body[k].params[field] = inp.value; }); return body; };
  const save = async () => { try { await api("/platform/runtime", "PUT", baseBody()); toast("Base runtime applied"); render(); } catch (e) { toast(e.message); } };
  if ($("#rtSave")) $("#rtSave").onclick = save;
  if ($("#rtTest")) $("#rtTest").onclick = async () => { const out = []; for (const c of ["cache", "ratelimit", "queue", "storage", "db"]) { try { const r = await api("/platform/runtime/test", "POST", { concern: c }); out.push(c + "=" + (r.ok ? "ok" : "FAIL") + (r.error ? ":" + r.error : "")); } catch (e) { out.push(c + "=err"); } } $("#rtTestOut").textContent = out.join(" · "); };
  const dbLog = obj => { const el = document.getElementById("dbOut"); if (el) el.textContent = JSON.stringify(obj, null, 1).slice(0, 4000); };
  (async () => { try { dbLog(await api("/platform/db")); } catch (e) { dbLog({ error: e.message }); } })();
  if ($("#dbPing")) $("#dbPing").onclick = async () => { try { dbLog(await api("/platform/db/ping", "POST", {})); } catch (e) { dbLog({ error: e.message }); } };
  if ($("#dbDry")) $("#dbDry").onclick = async () => { try { dbLog(await api("/platform/db/apply", "POST", { dryRun: true })); } catch (e) { dbLog({ error: e.message }); } };
  if ($("#dbApply")) $("#dbApply").onclick = async () => { if (!confirm("Apply migration to the configured Postgres? Runs DDL + data copy.")) return; try { dbLog(await api("/platform/db/apply", "POST", {})); } catch (e) { dbLog({ error: e.message }); } };
  if ($("#dbBack")) $("#dbBack").onclick = async () => { try { await api("/platform/db/switch", "POST", { driver: "sqlite" }); toast("Reverted to SQLite"); render(); } catch (e) { toast(e.message); } };
  let REG = { list: [], cdn: "" };
  const renderReg = () => { const el = document.getElementById("regWrap"); if (!el) return; el.innerHTML = `${REG.list.map((r, i) => `<span class="p-tag"><input data-regk="${i}" value="${esc(r.key)}" size="8"> <input data-regl="${i}" value="${esc(r.label)}" size="10"> <button class="p-btn sm danger" data-regdel="${i}">✕</button></span>`).join(" ")}<div style="margin-top:6px"><label>CDN base URL <input id="cdn" value="${esc(REG.cdn || "")}" placeholder="https://cdn.example (blank = off)" style="min-width:280px"></label> <button class="p-btn sm" id="regAdd">+ region</button> <button class="p-btn sm primary" id="regSave">Save regions</button></div>`; };
  (async () => { try { REG = await api("/platform/regions"); renderReg(); } catch (e) { const el = document.getElementById("regWrap"); if (el) el.textContent = "regions error: " + e.message; } })();
  const regWrap = document.getElementById("regWrap"); if (regWrap) regWrap.onclick = e => {
    if (e.target.id === "regAdd") { REG.list.push({ key: "", label: "" }); renderReg(); }
    else if (e.target.dataset && e.target.dataset.regdel) { REG.list.splice(Number(e.target.dataset.regdel), 1); renderReg(); }
    else if (e.target.id === "regSave") { document.querySelectorAll("[data-regk]").forEach(x => { REG.list[Number(x.dataset.regk)] = REG.list[Number(x.dataset.regk)] || {}; REG.list[Number(x.dataset.regk)].key = x.value; }); document.querySelectorAll("[data-regl]").forEach(x => { REG.list[Number(x.dataset.regl)].label = x.value; }); REG.cdn = (document.getElementById("cdn") || {}).value || ""; api("/platform/regions", "PUT", REG).then(() => toast("Regions saved")).catch(er => toast(er.message)); }
  };
  if ($("#envCreate")) $("#envCreate").onclick = async () => { try { await api("/platform/environments?name=" + encodeURIComponent($("#envName").value), "POST", { name: $("#envName").value, label: $("#envName").value, region: $("#envRegion").value, tenants: $("#envTenants").value.split(",").map(x => Number(x)).filter(Boolean), runtime: baseBody() }); toast("Environment created"); render(); } catch (e) { toast(e.message); } };
  $$("[data-envact]").forEach(b => b.onclick = async () => { try { await api("/platform/environments/" + encodeURIComponent(b.dataset.envact) + "/activate", "POST", {}); toast("Environment activated"); render(); } catch (e) { toast(e.message); } });
  $$("[data-envdel]").forEach(b => b.onclick = async () => { if (!confirm("Delete environment?")) return; try { await api("/platform/environments/" + encodeURIComponent(b.dataset.envdel), "DELETE", {}); render(); } catch (e) { toast(e.message); } });
  $$("[data-envedit]").forEach(b => b.onclick = async () => { const e = (await api("/platform/environments/" + encodeURIComponent(b.dataset.envedit))).environment; $("#envName").value = e.name; $("#envRegion").value = e.region || ""; $("#envTenants").value = (e.tenants || []).join(","); /* load its overlay into selects */ for (const [k, cfg] of Object.entries(e.runtime || {})) { const sel = $(`[data-rt="${k}"]`); if (sel) sel.value = cfg.driver; } toast("Loaded " + e.name + " into the base form — Create to update"); });
  if ($("#envExport")) $("#envExport").onclick = async () => { const r = await api("/platform/environments-export"); const blob = new Blob([JSON.stringify(r.bundle, null, 1)], { type: "application/json" }); const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "luxora-environments.json"; a.click(); };
  if ($("#envImportFile")) $("#envImportFile").onchange = e => { const file = e.target.files[0]; if (!file) return; const fr = new FileReader(); fr.onload = async () => { try { const bundle = JSON.parse(fr.result); await api("/platform/environments-import", "POST", { bundle }); toast("Environments imported"); render(); } catch (err) { toast(err.message); } }; fr.readAsText(file); };
  if ($("#flagSave")) $("#flagSave").onclick = async () => { try { await api("/platform/flags/" + encodeURIComponent($("#flagName").value), "PUT", { name: $("#flagName").value, rollout: Number($("#flagRollout").value) || 0, default: $("#flagDefault").checked }); toast("Flag set"); render(); } catch (e) { toast(e.message); } };
  $$("[data-flagedit]").forEach(b => b.onclick = async () => { const r = Number(prompt("Rollout % (0-100)", b.dataset.r)); if (r == null) return; const d = confirm("Default ON?"); await api("/platform/flags/" + encodeURIComponent(b.dataset.flagedit), "PUT", { rollout: r, default: d }); render(); });
  $$("[data-flagdel]").forEach(b => b.onclick = async () => { await api("/platform/flags/" + encodeURIComponent(b.dataset.flagdel), "DELETE", {}); render(); });
}
async function vBillingOps() {
  const d = await api("/platform/billing/aging"); const tenants = (await api("/platform/tenants")).tenants;
  const ag = d.aging, inv = (d.all && d.all.invoices) || [], notes = (d.all && d.all.notes) || [], events = (d.all && d.all.events) || [];
  const bStatus = s => `<span class="badge ${s === "paid" ? "published" : s === "overdue" ? "failed" : "processing"}">${esc(s)}</span>`;
  return `<div class="p-panel"><h2>💳 Billing Ops</h2>
    <p style="color:var(--p-muted);font-size:13px;margin:0 0 12px">Line-item subscription + usage invoicing, tax (via the Tax engine), credit notes / refunds-to-wallet (via the Offers wallet), dunning, and receivables aging.</p>
    <div class="p-cards" style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px">
      <div class="p-stat"><b>${money(ag.current)}</b> current</div><div class="p-stat"><b>${money(ag.d30)}</b> 1–30d</div><div class="p-stat"><b>${money(ag.d60)}</b> 31–60d</div><div class="p-stat"><b>${money(ag.d90)}</b> 60d+</div>
      <div class="p-stat"><b>${money(ag.total)}</b> receivable</div>
    </div>
    <div style="display:flex;gap:8px;margin-bottom:12px"><button class="p-btn sm primary" id="runDunning">Run dunning sweep</button>
      <span id="dunOut" class="p-tag"></span></div>
    <h3>Generate invoice</h3>
    <div style="display:flex;gap:8px;align-items:end;flex-wrap:wrap"><label><span>Store</span><select id="biTenant">${tenants.map(t => `<option value="${t.id}">${esc(t.name)}</option>`).join("")}</select></label><button class="p-btn sm" id="biGo">Issue monthly + usage invoice</button></div>
    <h3>Record metered usage</h3>
    <div style="display:flex;gap:8px;align-items:end;flex-wrap:wrap">
      <label><span>Store</span><select id="usTenant">${tenants.map(t => `<option value="${t.id}">${esc(t.name)}</option>`).join("")}</select></label>
      <label><span>Kind</span><select id="usKind"><option>ai</option><option>orders</option><option>storage</option><option>api</option><option>manual</option></select></label>
      <label><span>Description</span><input id="usDesc" placeholder="AI premium units"></label>
      <label><span>Qty</span><input id="usQty" type="number" value="1"></label>
      <label><span>Unit</span><input id="usUnit" type="number" step="0.01" value="0"></label>
      <button class="p-btn sm" id="usGo">Add usage</button></div>
    <h3>Invoices (all stores)</h3><div class="p-scroll-x"><table class="p-table"><thead><tr><th>#</th><th class="num">Amount</th><th>Status</th><th>Period</th><th>Lines</th><th></th></tr></thead><tbody>
      ${inv.map(i => `<tr><td><code>${esc(i.number)}</code></td><td class="num">${money(i.amount)}</td><td>${bStatus(i.status)}</td><td>${esc(i.period_start || "")}→${esc(i.period_end || "")}</td><td class="p-tag">${(i.lines || []).map(l => `${l.kind} ${money(l.amount)}`).join(", ")}</td>
        <td style="text-align:right"><button class="p-btn sm danger" data-ref="${i.id}">Credit/Refund</button></td></tr>`).join("") || '<tr><td colspan="6">None.</td></tr>'}
    </tbody></table></div>
    <h3>Credit notes</h3>${notes.length ? `<table class="p-table"><thead><tr><th>#</th><th class="num">Amount</th><th>Wallet</th><th>Reason</th></tr></thead><tbody>${notes.map(n => `<tr><td><code>${esc(n.number)}</code></td><td class="num">${money(n.amount)}</td><td>${n.to_wallet ? "yes" : "no"}</td><td>${esc(n.reason || "")}</td></tr>`).join("")}</tbody></table>` : '<p class="p-tag">None.</p>'}
    <h3>Billing events</h3><div class="p-tag" style="max-height:220px;overflow:auto">${events.slice(0, 20).map(e => { let d = {}; try { d = JSON.parse(e.detail || "{}"); } catch (x) { } return `${esc((e.created_at || "").slice(0, 16))} · ${esc(e.kind)} · ${esc(JSON.stringify(d))}`; }).join("<br>") || "—"}</div>
    </div>`;
}
function wireBillingOps() {
  const $ = s => document.querySelector(s);
  if ($("#runDunning")) $("#runDunning").onclick = async () => { try { const r = await api("/platform/billing/dunning", "POST", {}); $("#dunOut").textContent = (r.actions.length) + " overdue actions"; render(); } catch (e) { toast(e.message); } };
  if ($("#biGo")) $("#biGo").onclick = async () => { try { await api("/platform/tenants/" + $("#biTenant").value + "/invoice", "POST", {}); toast("Invoice issued"); render(); } catch (e) { toast(e.message); } };
  if ($("#usGo")) $("#usGo").onclick = async () => { try { await api("/platform/usage", "POST", { tenant_id: Number($("#usTenant").value), kind: $("#usKind").value, description: $("#usDesc").value || $("#usKind").value, qty: Number($("#usQty").value) || 1, unit_amount: Number($("#usUnit").value) || 0 }); toast("Usage recorded"); render(); } catch (e) { toast(e.message); } };
  document.querySelectorAll("[data-ref]").forEach(b => b.onclick = async () => { const amt = prompt("Refund amount (blank = full)"); try { await api("/platform/invoices/" + b.dataset.ref + "/refund", "POST", { amount: amt ? Number(amt) : undefined, to_wallet: confirm("Credit to the store's customer wallet? (OK) or log a credit note only (Cancel)") }); toast("Credit note issued"); render(); } catch (e) { toast(e.message); } });
}
/* ============================================================
   GLOBAL OPERATIONS — every store capability, read across ALL stores
   ------------------------------------------------------------
   The Store Console edits ONE store; this surface watches every store at once. Two
   generic primitives back every view, so no capability is re-implemented and none is
   missing:
     • gTable(key)    — the generic cross-tenant entity reader (/api/platform/data/:key),
                        built on the same definitions the Store Console uses
     • gFan(path)     — the fan-out that runs the store's OWN read-only handler once per
                        store and merges, so the business logic lives exactly once
   The store keeps read+write; the platform gets oversight — zero overlap, zero duplicate. */
const G = { entities: null, tmap: {}, q: "", tenantId: "", entity: "order" };
async function gMeta() {
  if (!G.entities) {
    const m = await api("/platform/data");
    G.entities = m.entities || [];
    G.tmap = {};
    for (const t of (m.tenants || [])) G.tmap[String(t.id)] = t;
  }
  return G;
}
const gStore = id => { const t = G.tmap[String(id)]; return t ? esc(t.name) : ("store " + esc(id)); };
function gCell(v, f) {
  if (v == null) return "";
  if (f.type === "bool") return v ? "✓" : "—";
  if (f.type === "money") return money(v);
  const badge = ["status", "lifecycle", "state", "priority", "kind"];
  if (badge.includes(f.key)) return `<span class="badge ${esc(v)}">${esc(v)}</span>`;
  return esc(String(v).slice(0, 64));
}
/* the shared store-filter + search bar. Both apply to every dataset on the view, and the
   search re-renders debounced with focus restored, so typing never fights the console. */
function gBar(title, icon, sub, datasets) {
  const opts = Object.values(G.tmap).map(t => `<option value="${t.id}" ${String(G.tenantId) === String(t.id) ? "selected" : ""}>${esc(t.name)}</option>`).join("");
  return `<div class="p-head"><h2>${icon} ${esc(title)}</h2><p class="p-sub">${sub}</p></div>
  <div class="p-panel" style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;padding:10px 14px">
    <label style="font-size:13px;color:var(--p-muted)">Tenant</label>
    <select id="gTenant" style="min-width:170px"><option value="">All tenants</option>${opts}</select>
    <input class="p-search" id="gQ" placeholder="Search across tenants…" value="${esc(G.q)}" style="flex:1;min-width:220px">
    <span class="p-tag">${datasets} dataset${datasets === 1 ? "" : "s"} · platform-level oversight</span>
  </div>`;
}
function wireG() {
  const t = $("#gTenant");
  if (t) t.onchange = () => { G.tenantId = t.value; render(); };
  const q = $("#gQ");
  if (q) {
    let tm;
    q.oninput = () => { clearTimeout(tm); const pos = q.selectionStart; tm = setTimeout(() => { render().then(() => { const n = $("#gQ"); if (n) { n.focus(); try { n.setSelectionRange(pos, pos); } catch (e) { } } }); }, 400); };
    q.onkeydown = e => { if (e.key === "Enter") { clearTimeout(tm); render(); } };
  }
}
/* one cross-tenant table per entity — columns come straight from the entity's own
   list-visible fields (the same defs the Store Console renders), never hardcoded here.
   The toolbar is the platform's dataset surface, present wherever a dataset renders (a
   universe's records, a capability leaf, the Global Operations views): a per-table filter,
   New / Edit / Delete through the platform write endpoints, and CSV / JSON import-export.
   A dataset the identity may not write hides its write buttons — the endpoints refuse the
   same writes, so the toolbar and the API can never disagree. */
const gq = {}, gCache = {}, gDefs = {};
function gFilterRows(key, rows, fields) {
  const q = String(gq[key] || "").trim().toLowerCase();
  if (!q) return rows;
  return rows.filter(r => fields.some(f => String(r[f.key] ?? "").toLowerCase().includes(q)) || String(r.id ?? "").toLowerCase().includes(q));
}
function gRowHtml(r, def, fields) {
  const id = r[def.pk] != null ? r[def.pk] : r.id;
  return `<tr>${def.tenantScoped ? `<td>${gStore(r.tenant_id)}</td>` : ""}${fields.map(f => `<td>${gCell(r[f.key], f)}</td>`).join("")}
    <td style="text-align:right;white-space:nowrap"><button class="p-btn sm" data-gedit="${esc(def.key)}" data-id="${esc(id)}">Edit</button>
    <button class="p-btn sm danger" data-gdel="${esc(def.key)}" data-id="${esc(id)}">✕</button></td></tr>`;
}
async function gTable(key, opts = {}) {
  await gMeta();
  const def = (G.entities || []).find(e => e.key === key);
  if (!def) return `<div class="p-empty">Dataset <code>${esc(key)}</code> is not served by the platform registry.</div>`;
  const p = new URLSearchParams();
  if (G.q) p.set("q", G.q);
  if (G.tenantId) p.set("tenant_id", G.tenantId);
  if (opts.trash) p.set("trash", "1");
  const qs = p.toString();
  let rows = [];
  try { rows = (await api("/platform/data/" + encodeURIComponent(key) + (qs ? "?" + qs : ""))).rows || []; }
  catch (e) { return `<div class="p-empty">⚠️ ${esc(e.message)}</div>`; }
  const listFields = (def.fields || []).slice(0, 7);
  const canWrite = def.writable !== false;
  gDefs[key] = def; gCache[key] = rows;
  const shown = gFilterRows(key, rows, listFields);
  const span = listFields.length + (def.tenantScoped ? 1 : 0) + (canWrite ? 1 : 0) || 1;
  return `<div class="p-panel" data-gtable="${esc(key)}"><div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;flex-wrap:wrap">
    <h2 style="margin:0">${esc(def.name || key)}</h2><span class="p-tag" data-gcount>${shown.length}${def.tenantScoped ? " across tenants" : ""}</span>
    <input class="p-search" data-gq="${esc(key)}" placeholder="Filter ${esc(String(def.name || key).toLowerCase())}…" value="${esc(gq[key] || "")}" style="min-width:150px;max-width:260px">
    <span style="flex:1"></span>
    ${canWrite ? `<button class="p-btn sm primary" data-gnew="${esc(key)}">+ New</button>
    <button class="p-btn sm" data-gimport="${esc(key)}" title="Paste CSV or JSON records">⇪ Import</button>` : ""}
    <button class="p-btn sm" data-gexport="${esc(key)}" title="Export — every format the platform can render, and the scope of the export">⇩ Export</button></div>
    <div class="p-scroll-x"><table class="p-table"><thead><tr>${def.tenantScoped ? "<th>Store</th>" : ""}${listFields.map(f => `<th>${esc(f.label)}</th>`).join("")}${canWrite ? "<th></th>" : ""}</tr></thead>
    <tbody>${shown.slice(0, 200).map(r => gRowHtml(r, def, listFields)).join("") || `<tr><td colspan="${span}" class="p-empty">No records${canWrite ? " — add one with + New or ⇪ Import" : ""}</td></tr>`}</tbody></table></div></div>`;
}
/* ---------- the record form: built from the entity's own declaration, the same defs the
   Store Console's editor renders — the platform never carries a second copy of a schema.
   A platform-level registry (countries, currencies, the uv_* universes…) writes at scope
   0 so every store inherits the row; a store-scoped dataset makes the operator name the
   store rather than silently filing the record under whichever one was open */
async function gFieldInput(f, val) {
  const fid = "gf_" + f.key;
  const req = f.required ? ' <em style="color:var(--p-red)" title="required">*</em>' : "";
  if (f.type === "bool") return `<label class="p-check"><input type="checkbox" id="${fid}" ${val ? "checked" : ""}> <span>${esc(f.label)}${req}</span></label>`;
  if (f.type === "textarea") return `<label><span>${esc(f.label)}${req}</span><textarea id="${fid}" rows="3">${esc(val == null ? "" : val)}</textarea></label>`;
  if (f.type === "json" || f.type === "multi") return `<label><span>${esc(f.label)}${req} <small>(JSON)</small></span><textarea id="${fid}" rows="3" placeholder="{}">${esc(typeof val === "string" ? val : (val == null ? "" : JSON.stringify(val, null, 1)))}</textarea></label>`;
  if (f.type === "select") {
    const opts = Array.isArray(f.options) ? f.options : [];
    return `<label><span>${esc(f.label)}${req}</span><select id="${fid}"><option value="">—</option>${opts.map(o => `<option ${String(o) === String(val) ? "selected" : ""}>${esc(o)}</option>`).join("")}</select></label>`;
  }
  if (String(f.type || "").startsWith("ref:")) {
    const refKey = f.type.slice(4);
    const refDef = (G.entities || []).find(e => e.key === refKey) || {};
    const pk = refDef.pk || "id";
    let opts = [];
    try { opts = (await api("/platform/data/" + encodeURIComponent(refKey))).rows || []; } catch (e) { opts = []; }
    const items = opts.map(r => ({ v: r[pk] != null ? r[pk] : (r.code || r.id), l: r.title || r.name || r.label || r.code || String(r[pk] != null ? r[pk] : r.id) }));
    /* a value the registry no longer lists must still be representable, or a required ref
       renders empty and blocks every save of that record (the value survives, unseen) */
    const unmatched = val != null && val !== "" && !items.some(o => String(o.v) === String(val));
    return `<label><span>${esc(f.label)}${req}</span><select id="${fid}"><option value="">—</option>${unmatched ? `<option value="${esc(val)}" selected>${esc(val)}</option>` : ""}${items.map(o => `<option value="${esc(o.v)}" ${String(o.v) === String(val) ? "selected" : ""}>${esc(o.l)}</option>`).join("")}</select></label>`;
  }
  if (f.readonly) return `<label><span>${esc(f.label)}${req}</span><input id="${fid}" type="text" value="${esc(val == null ? "" : val)}" disabled title="managed by the platform"></label>`;
  const t = f.type === "money" || f.type === "number" ? "number" : f.type === "date" ? "date" : "text";
  return `<label><span>${esc(f.label)}${req}</span><input id="${fid}" type="${t}" step="any" value="${esc(val == null ? "" : val)}"></label>`;
}
function gCollect(def, m) {
  const row = {};
  for (const f of def.fields) {
    if (f.readonly) continue;
    const el = m.querySelector("#gf_" + f.key);
    if (!el) continue;
    if (f.type === "bool") { row[f.key] = el.checked ? 1 : 0; continue; }
    let v = el.value;
    if (f.type === "json" || f.type === "multi") {
      if (String(v).trim() === "") { row[f.key] = null; continue; }
      try { v = JSON.parse(v); } catch (e) { toast("Invalid JSON in " + f.label); throw e; }
      row[f.key] = v; continue;
    }
    if (f.type === "money" || f.type === "number") { row[f.key] = v === "" ? null : Number(v); continue; }
    row[f.key] = v;
  }
  return row;
}
function gScopeSelect(def, id) {
  /* platformLevel is the /def answer; the index carries the same fact as tenantScoped
     (inverted) — either shape decides whether a store needs naming */
  const level = def.platformLevel != null ? def.platformLevel : !def.tenantScoped;
  if (level) return "";
  const tenants = Object.values(G.tmap || {});
  const json = def.storage === "json";
  return `<label style="max-width:280px"><span>Store ${json ? "<small>(blank = platform level)</small>" : "*"}</span>
    <select id="${id}"><option value="">${json ? "Platform level (all stores)" : "— pick a store —"}</option>
    ${tenants.map(t => `<option value="${t.id}" ${String(G.tenantId) === String(t.id) ? "selected" : ""}>${esc(t.name)}</option>`).join("")}</select></label>`;
}
async function gRecordForm(key, id) {
  const def = await api("/platform/data/" + encodeURIComponent(key) + "/def");
  if (!def || def.error) { toast((def && def.error) || "Dataset unavailable"); return; }
  let row = {};
  if (id != null) {
    const { rows } = await api("/platform/data/" + encodeURIComponent(key));
    row = (rows || []).find(r => String(r[def.pk] ?? r.id) === String(id)) || {};
  }
  const m = modal(`<div class="p-modal-head"><h3>${id != null ? "Edit" : "New"} · ${esc(def.label || def.name || key)}</h3><button data-mclose>✕</button></div>
    <div class="p-form">${gScopeSelect(def, "gf_tenant")}
      ${(await Promise.all(def.fields.map(f => gFieldInput(f, row[f.key])))).join("")}
      <div style="display:flex;gap:10px;margin-top:8px"><button class="p-btn primary" id="gfSave">${id != null ? "Save" : "Create"}</button><button class="p-btn" data-mclose>Cancel</button></div></div>`);
  m.querySelector("#gfSave").onclick = async () => {
    try {
      const body = gCollect(def, m);
      const tidEl = m.querySelector("#gf_tenant");
      if (tidEl) body.tenant_id = tidEl.value ? Number(tidEl.value) : "";
      if (!def.platformLevel && def.storage !== "json" && !body.tenant_id) { toast("Pick a store — this dataset is store-scoped"); return; }
      if (id != null) await api("/platform/data/" + encodeURIComponent(key) + "/" + encodeURIComponent(id), "PUT", body);
      else await api("/platform/data/" + encodeURIComponent(key), "POST", body);
      m.innerHTML = ""; toast(id != null ? "Saved" : "Created"); render();
    } catch (e) { toast(e.message); }
  };
}
/* import: one box, CSV or JSON (auto-detected); every row is validated exactly like a
   hand-entered one, and each rejection comes back with its row number so the operator
   fixes the data instead of guessing which line the engine refused */
async function gImportForm(key) {
  /* the store-required guard needs the entity's scope and storage kind, and the index the
     toolbar renders from carries neither — so the declaration is read from /def (the same
     answer the record form uses), falling back to the index if the def call fails */
  let def = await api("/platform/data/" + encodeURIComponent(key) + "/def");
  if (!def || def.error) def = (G.entities || []).find(e => e.key === key) || {};
  const cols = (def.fields || []).filter(f => !f.readonly).map(f => f.key).join(", ");
  const m = modal(`<div class="p-modal-head"><h3>⇪ Import · ${esc(def.name || key)}</h3><button data-mclose>✕</button></div>
    <div class="p-form">
      <p class="p-tag" style="margin:0 0 8px">Paste a JSON array, or CSV whose first row is the column headers. Only declared columns are kept; each row is validated like a hand-entered record.</p>
      <label><span>Records</span><textarea id="giBody" rows="9" style="font-family:monospace" placeholder="${esc(cols)}&#10;…"></textarea></label>
      <label><span>Columns</span><input value="${esc(cols)}" readonly title="the fields this entity declares"></label>
      <div class="p-sample"><span class="p-tag" style="flex:1">Don't know the shape? Download a sample file — these exact columns plus one example row.</span>
        <select id="giSampleFmt" style="min-height:30px"><option value="csv">CSV</option><option value="json">JSON</option></select>
        <button class="p-btn sm" id="giSample" title="Download a sample file with this dataset's current columns">⇩ Sample file</button></div>
      ${gScopeSelect(def, "giTenant")}
      <div style="display:flex;gap:10px;margin-top:8px"><button class="p-btn primary" id="giGo">Import</button><button class="p-btn" data-mclose>Cancel</button></div>
      <div id="giOut" style="margin-top:8px"></div></div>`);
  /* the sample file: the endpoint answers this dataset's own current columns with one
     example row, in the same CSV/JSON shape the importer accepts — so an operator fills
     in a file they downloaded rather than guessing which headers the engine will take */
  m.querySelector("#giSample").onclick = async () => {
    const fmt = m.querySelector("#giSampleFmt").value;
    try { await gDownload("/api/platform/data/" + encodeURIComponent(key) + "/sample?format=" + fmt, key + "-sample." + fmt); toast("Sample downloaded"); }
    catch (e) { toast(e.message); }
  };
  m.querySelector("#giGo").onclick = async () => {
    const body = { text: m.querySelector("#giBody").value };
    const tid = m.querySelector("#giTenant");
    if (tid) body.tenant_id = tid.value ? Number(tid.value) : "";
    if (!def.platformLevel && def.storage !== "json" && !body.tenant_id) { toast("Pick a store — this dataset is store-scoped"); return; }
    const out = m.querySelector("#giOut");
    out.innerHTML = '<p class="p-tag">Importing…</p>';
    try {
      const r = await api("/platform/data/" + encodeURIComponent(key) + "/import", "POST", body);
      out.innerHTML = `<p class="p-tag">✅ ${r.imported} imported${r.failed.length ? " · ⚠️ " + r.failed.length + " rejected" : ""}</p>`
        + (r.failed.length ? `<div class="p-scroll-x" style="max-height:180px"><table class="p-table"><thead><tr><th>Row</th><th>Why rejected</th></tr></thead>
          <tbody>${r.failed.slice(0, 50).map(f => `<tr><td class="num">${f.index}</td><td>${esc(f.error)}</td></tr>`).join("")}</tbody></table></div>` : "");
      if (!r.failed.length) { m.innerHTML = ""; toast("Imported " + r.imported); render(); }
    } catch (e) { out.innerHTML = `<p class="p-tag" style="color:var(--p-red)">⚠️ ${esc(e.message)}</p>`; }
  };
}
/* the export menu: one button, every format + every scope. The format list is fetched
   from the export endpoint itself (?format=formats), so a format registered server-side
   appears here with no client change — the menu never carries a second list that could
   drift from what the server can actually emit */
const gFmtCache = {};
/* the format list plus the reason it came back empty, so an operator is told what to fix
   rather than just "unavailable" — the usual cause is a platform service running code older
   than this page (it answers the export with a file instead of the registry) */
async function gFormats(key) {
  if (!gFmtCache[key]) {
    let formats = [], reason = "";
    try {
      const r = await api("/platform/data/" + encodeURIComponent(key) + "/export?format=formats");
      formats = r.formats || [];
      if (!formats.length) reason = r.error || "the platform service did not answer a format list — it may be running older code than this page; restart it and retry";
    } catch (e) { reason = e.message; }
    gFmtCache[key] = { formats, reason };
  }
  return gFmtCache[key];
}
/* a blob download — the same path the sample file and the export use, so every format
   lands in the downloads folder through one code path */
function gDownload(url, filename) {
  return fetch(url, { headers: { "x-csrf": __csrf() }, credentials: "same-origin" })
    .then(r => { if (!r.ok) return r.json().catch(() => ({})).then(j => { throw new Error(j.error || ("HTTP " + r.status)); }); return r.blob(); })
    .then(blob => {
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = filename;
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(a.href), 4000);
    });
}
function gMenuClose() { const m = document.querySelector("[data-gmenu]"); if (m) m.remove(); }
async function gExportMenu(btn, key) {
  gMenuClose();
  const def = gDefs[key] || {};
  const fmts = await gFormats(key);
  if (!fmts.formats.length) { toast(fmts.reason || "Export unavailable for this dataset"); return; }
  const formats = fmts.formats;
  const listFields = (def.fields || []).slice(0, 7);
  const allRows = gCache[key] || [];
  /* the visible page is exactly what the table is showing, so its rows are identified by
     their primary keys and the export cannot drift from what the operator is looking at */
  const visIds = gFilterRows(key, allRows, listFields).slice(0, 200)
    .map(r => r[def.pk] != null ? r[def.pk] : r.id);
  const dateCols = (def.fields || []).filter(f => f.type === "date");
  const base = new URLSearchParams();
  if (G.q) base.set("q", G.q);
  if (G.tenantId) base.set("tenant_id", G.tenantId);
  const m = document.createElement("div");
  m.className = "p-menu";
  m.setAttribute("data-gmenu", "1");
  m.innerHTML = `<div class="p-menu-sec">Format</div>
    <div class="p-fmts">${formats.map((f, i) => `<button type="button" class="p-btn sm${i === 0 ? " primary" : ""}" data-gfmt="${esc(f.key)}" title="${esc(f.label)}">${esc(f.label)}</button>`).join("")}</div>
    <div class="p-menu-sec">Scope</div>
    <label class="p-check"><input type="radio" name="gscope" value="all" checked><span>All matching (${allRows.length})</span></label>
    <label class="p-check"><input type="radio" name="gscope" value="page" ${visIds.length ? "" : "disabled"}><span>Current page (${visIds.length})</span></label>
    <label class="p-check"><input type="radio" name="gscope" value="range"><span>Rows</span>
      <input type="number" class="p-mini" id="gxFrom" min="1" value="1" aria-label="from row"> – <input type="number" class="p-mini" id="gxTo" min="1" value="${allRows.length}" aria-label="to row"></label>
    <label class="p-check"><input type="radio" name="gscope" value="date" ${dateCols.length ? "" : "disabled"}>
      <span>Date</span><select class="p-mini" id="gxCol" ${dateCols.length ? "" : "disabled"} aria-label="date column">${dateCols.map(c => `<option value="${esc(c.key)}">${esc(c.label || c.key)}</option>`).join("")}</select>
      <input type="date" class="p-mini" id="gxFromD" aria-label="from date"><input type="date" class="p-mini" id="gxToD" aria-label="to date"></label>
    ${dateCols.length ? "" : `<span class="p-tag">no date columns on this dataset</span>`}
    <div class="p-menu-foot"><button class="p-btn primary" id="gxGo">⇩ Download</button></div>`;
  document.body.appendChild(m);
  const r = btn.getBoundingClientRect();
  m.style.left = Math.max(8, Math.min(r.left, window.innerWidth - m.offsetWidth - 12)) + "px";
  m.style.top = Math.min(r.bottom + 6, window.innerHeight - m.offsetHeight - 12) + "px";
  /* a format pill selects, but does not start, the export — the scope stays the operator's */
  m.querySelectorAll("[data-gfmt]").forEach(b => b.onclick = () => {
    m.querySelectorAll("[data-gfmt]").forEach(x => x.classList.remove("primary"));
    b.classList.add("primary");
  });
  /* touching a scope's inputs selects that scope, so the operator never exports a range
     they set up but then forgot to pick */
  const pickScope = s => { const x = m.querySelector(`input[name=gscope][value="${s}"]`); if (x && !x.disabled) x.checked = true; };
  ["#gxFrom", "#gxTo"].forEach(s => { const el = m.querySelector(s); if (el) el.oninput = () => pickScope("range"); });
  ["#gxCol", "#gxFromD", "#gxToD"].forEach(s => { const el = m.querySelector(s); if (el) el.oninput = () => pickScope("date"); });
  m.querySelector("#gxGo").onclick = async () => {
    const fmtEl = m.querySelector("[data-gfmt].primary");
    const fmt = fmtEl ? fmtEl.dataset.gfmt : "csv";
    const scope = (m.querySelector("input[name=gscope]:checked") || {}).value || "all";
    const extra = { format: fmt };
    if (scope === "page") extra.ids = visIds.join(",");
    else if (scope === "range") { extra.from = m.querySelector("#gxFrom").value; extra.to = m.querySelector("#gxTo").value; }
    else if (scope === "date") { extra.date_col = m.querySelector("#gxCol").value; extra.date_from = m.querySelector("#gxFromD").value; extra.date_to = m.querySelector("#gxToD").value; }
    const p = new URLSearchParams(base);
    for (const [k, v] of Object.entries(extra)) if (v != null && v !== "") p.set(k, v);
    const ext = (formats.find(x => x.key === fmt) || {}).ext || fmt;
    try {
      await gDownload("/api/platform/data/" + encodeURIComponent(key) + "/export?" + p.toString(), key + "." + ext);
      toast("Exported " + key + "." + ext);
      gMenuClose();
    } catch (e) { toast(e.message); }
  };
}
/* the menu closes on any click outside itself (the export button itself is exempt — it
   re-opens) and on Escape, so a menu can never be left dangling over a re-rendered view */
document.addEventListener("click", e => {
  if (!e.target.closest) return;
  if (e.target.closest("[data-gmenu]") || e.target.closest("[data-gexport]")) return;
  gMenuClose();
});
document.addEventListener("keydown", e => { if (e.key === "Escape") gMenuClose(); });
async function gDelete(key, id) {
  const def = (G.entities || []).find(e => e.key === key) || {};
  const label = String(def.name || key).toLowerCase().replace(/s$/, "");
  if (!confirm("Delete this " + label + " record?")) return;
  const p = new URLSearchParams();
  if (G.tenantId) p.set("tenant_id", G.tenantId);
  try {
    const r = await api("/platform/data/" + encodeURIComponent(key) + "/" + encodeURIComponent(id) + (p.toString() ? "?" + p.toString() : ""), "DELETE", {});
    toast(r.trashed ? "Moved to trash" : "Deleted"); render();
  } catch (e) { toast(e.message); }
}
/* the toolbar's wiring is delegated at document level (like the store console's entity
   buttons) so it survives every re-render without each view re-attaching it; the data-g*
   prefixes keep these buttons clear of the store bundle's data-new/edit/del handlers when
   the unified console has both bundles loaded */
document.addEventListener("click", async e => {
  const nb = e.target.closest("[data-gnew]"), eb = e.target.closest("[data-gedit]"),
    db = e.target.closest("[data-gdel]"), ib = e.target.closest("[data-gimport]"),
    xb = e.target.closest("[data-gexport]");
  try {
    if (nb) return await gRecordForm(nb.dataset.gnew, null);
    if (eb) return await gRecordForm(eb.dataset.gedit, eb.dataset.gedit && eb.dataset.id);
    if (db) return await gDelete(db.dataset.gdel, db.dataset.id);
    if (ib) return gImportForm(ib.dataset.gimport);
    if (xb) return await gExportMenu(xb, xb.dataset.gexport);
  } catch (err) { toast(err.message); }
});
/* a per-table filter re-filters the rows already in hand and rewrites only its own tbody —
   no re-render, no refetch, so typing in one table never disturbs the rest of the page */
document.addEventListener("input", e => {
  const q = e.target.closest && e.target.closest("[data-gq]");
  if (!q) return;
  const key = q.dataset.gq, def = gDefs[key], box = q.closest("[data-gtable]");
  gq[key] = q.value;
  if (!def || !box) return;
  const listFields = (def.fields || []).slice(0, 7);
  const rows = gFilterRows(key, gCache[key] || [], listFields);
  const cnt = box.querySelector("[data-gcount]");
  if (cnt) cnt.textContent = rows.length + (def.tenantScoped ? " across tenants" : "");
  const tbody = box.querySelector("tbody");
  if (tbody) tbody.innerHTML = rows.slice(0, 200).map(r => gRowHtml(r, def, listFields)).join("")
    || `<tr><td colspan="${listFields.length + (def.tenantScoped ? 1 : 0) + 1}" class="p-empty">No records match “${esc(q.value)}”</td></tr>`;
});
/* a fan-out panel: when columns are omitted they are derived from the payload itself, so a
   view stays correct even if the store handler's shape grows (zero hard-coding, zero partial) */
async function gFan(path) {
  const p = new URLSearchParams({ path, flat: "1" });
  if (G.tenantId) p.set("tenant_id", G.tenantId);
  try { return await api("/platform/fanout?" + p.toString()); } catch (e) { return { results: [], merged: {} }; }
}
function gRows(title, icon, rows, cols, opts = {}) {
  const r = rows || [];
  const c = cols || (r.length ? Object.keys(r[0]).filter(k => k !== "tenant_id" && k !== "store").slice(0, 7).map(k => ({ l: k, k })) : []);
  const f = x => c.map(col => `<td>${col.f ? col.f(x) : esc(String(x[col.k] ?? "").slice(0, 60))}</td>`).join("");
  return `<div class="p-panel"><div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
    <h2 style="margin:0">${icon} ${esc(title)}</h2><span class="p-tag">${r.length} across tenants</span></div>
    <div class="p-scroll-x"><table class="p-table"><thead><tr><th>Store</th>${c.map(col => `<th>${esc(col.l)}</th>`).join("")}</tr></thead>
    <tbody>${r.slice(0, opts.cap || 150).map(x => `<tr><td>${gStore(x.tenant_id)}</td>${f(x)}</tr>`).join("") || `<tr><td colspan="${c.length + 1}" class="p-empty">No records</td></tr>`}</tbody></table></div></div>`;
}
/* ---------- the views ---------- */
async function vGops() {
  await gMeta();
  const st = await gFan("/api/admin/stats");
  const m = st.merged || {};
  const per = (st.results || []).filter(r => r.ok && r.data).map(r => ({
    tenant_id: r.tenant_id, store: r.name, revenue: r.data.revenue, orders: r.data.orders,
    pending: r.data.pending, customers: r.data.customers, products: r.data.products,
    plan: (r.data.plan || {}).name
  }));
  return gBar("Operations Hub", "🧭", "Platform health from each tenant's own stats handler — one fan-out, zero duplicated logic.", 4)
    + `<div class="p-cards">
      <div class="p-stat"><em>Platform GMV</em><b>${money(m.revenue || 0)}</b><small>summed across tenants</small></div>
      <div class="p-stat"><em>Orders</em><b>${m.orders || 0}</b><small>${m.pending || 0} open</small></div>
      <div class="p-stat"><em>Customers</em><b>${m.customers || 0}</b></div>
      <div class="p-stat"><em>Products</em><b>${(m.products || 0).toLocaleString()}</b><small>platform-wide</small></div>
    </div>`
    + gRows("Tenant comparison", "🏬", per, [
      { l: "Store", k: "store" }, { l: "Revenue", k: "revenue", f: x => money(x.revenue || 0) },
      { l: "Orders", k: "orders" }, { l: "Open", k: "pending" }, { l: "Customers", k: "customers" },
      { l: "Products", k: "products" }, { l: "Plan", k: "plan" }
    ])
    + gRows("Low stock — platform-wide", "⚠️", m.lowStock, [
      { l: "Product", f: x => esc(String(x.title || x.id).slice(0, 56)) }, { l: "Stock", k: "stock" }
    ])
    + gRows("Recent orders — platform-wide", "🧾", m.recent, [
      { l: "Order #", k: "num" }, { l: "Customer", k: "name" }, { l: "Total", k: "total", f: x => money(x.total) },
      { l: "Status", k: "status", f: x => `<span class="badge ${esc(x.status)}">${esc(x.status)}</span>` }
    ]);
}
async function vGorders() {
  await gMeta();
  const ships = await gFan("/api/shipments");
  return gBar("Orders · Returns · RFQs", "🧾", "Orders, returns, B2B requests, fulfilment, serialized goods and quick-commerce dispatch — the same records each tenant's console edits, read platform-wide.", 3)
    + await gTable("order") + await gTable("ret") + await gTable("rfq")
    + gRows("Shipments & fulfilment", "🚚", (ships.merged || {}).shipments, [
      { l: "Ref", k: "tracking_ref" }, { l: "Order", k: "order_id" }, { l: "Carrier", k: "carrier" },
      { l: "Status", k: "status" }, { l: "Warehouse", k: "warehouse_id" }
    ])
    + await gTable("serialized")
    + gRows("Quick-commerce dispatch runs", "⚡", await gFanRows("/api/qc/runs"))
    + gRows("Riders", "🛵", await gFanRows("/api/qc/riders"));
}
/* helper for the quick-commerce fan-out lists (the store endpoint returns its rows under a
   domain key, so the auto-column renderer just needs the merged payload's array) */
async function gFanRows(path, key) {
  const j = await gFan(path);
  const m = j.merged || {};
  return m[key] || m.runs || m.riders || m.rows || [];
}
async function vGcatalog() {
  await gMeta();
  const plan = await gFan("/api/admin/planning");
  return gBar("Catalog · Products · SKUs", "📦", "Products, variants/SKUs, inventory, warehousing and replenishment planning platform-wide — inventory counts are the platform's goods view.", 5)
    + await gTable("product") + await gTable("sku") + await gTable("inventory") + await gTable("variant_group") + await gTable("warehouse")
    + gRows("Replenishment plan", "📦", (plan.merged || {}).replenishments)
    + gRows("Planning stats — per tenant", "📈", (plan.results || []).filter(r => r.ok && r.data).map(r => ({ tenant_id: r.tenant_id, store: r.name, ...(r.data.stats || {}) })));
}
async function vGb2b() {
  await gMeta();
  return gBar("Sellers · Suppliers · B2B", "🤝", "Marketplace sellers & onboarding, suppliers and procurement, B2B contracts/tenders, FBA and smart fulfilment, buyer claims, and trade trust (assurance, verification, letters of credit) — platform-wide.", 11)
    + await gTable("seller") + await gTable("supplier") + await gTable("product_supplier")
    + await gTable("contract") + await gTable("tender")
    + await gTable("seller_onboarding") + await gTable("seller_offer") + await gTable("seller_performance")
    + await gTable("fba_inbound") + await gTable("smart_fulfilment") + await gTable("buyer_claim")
    + await gTable("trade_assurance") + await gTable("company_verification") + await gTable("letter_of_credit");
}
async function vGmarket() {
  await gMeta();
  const [ads, kpi] = await Promise.all([gFan("/api/marketplace/ads"), gFan("/api/admin/marketplace/metrics")]);
  return gBar("Ads · Marketplace", "📣", "Sponsored inventory, auctions and seller KPIs — GSP bidding, take rate and settlement, platform-wide.", 2)
    + gRows("Ad inventory", "📣", (ads.merged || {}).ads, [
      { l: "Name", k: "name" }, { l: "Seller", k: "seller_id" }, { l: "Model", k: "bid_model" },
      { l: "Bid", k: "bid_amount", f: x => money(x.bid_amount) }, { l: "Spent", k: "spent", f: x => money(x.spent) },
      { l: "Status", k: "status" }
    ])
    + gRows("Seller KPIs", "📊", (kpi.merged || {}).sellers, [
      { l: "Seller", k: "seller_id" }, { l: "Orders", k: "orders" }, { l: "Revenue", k: "revenue", f: x => money(x.revenue) },
      { l: "Take", k: "take_rate", f: x => ((x.take_rate || 0) * 100).toFixed(0) + "%" },
      { l: "Commission", k: "commission", f: x => money(x.commission) }, { l: "Ad spend", k: "ads_spend", f: x => money(x.ads_spend) },
      { l: "Ad ROI", k: "ad_roi" }
    ]);
}
async function vGfinance() {
  await gMeta();
  const [disp, pays, bill, xfer, paym, gw] = await Promise.all([
    gFan("/api/admin/fin/disputes"), gFan("/api/admin/fin/payouts"), gFan("/api/admin/billing"),
    gFan("/api/admin/transfers"), gFan("/api/admin/payments"), gFan("/api/admin/gateways")
  ]);
  return gBar("Finance · Payments", "💸", "Disputes, payout runs, billing, wallets, gateway turnover and each store's configured payment/shipping/notify providers — plus the fintech rails (UPI, escrow, splits, mandates, BNPL, KYC).", 5)
    + gRows("Disputes / chargebacks", "⚖️", (disp.merged || {}).disputes, [
      { l: "Ref", k: "ref" }, { l: "Amount", k: "amount", f: x => money(x.amount) + " " + esc(x.currency || "") }, { l: "State", k: "state" }
    ])
    + gRows("Payout runs", "🏦", (pays.merged || {}).payouts, [
      { l: "Ref", k: "ref" }, { l: "Kind", k: "kind" }, { l: "Gross", k: "gross", f: x => money(x.gross) },
      { l: "Net", k: "net", f: x => money(x.net) }, { l: "Status", k: "status" }
    ])
    + gRows("Billing — per tenant", "🧮", (bill.results || []).filter(r => r.ok && r.data).map(r => ({ tenant_id: r.tenant_id, store: r.name, ...r.data })))
    + gRows("Wallet transfers", "🔁", (xfer.merged || {}).transfers || (xfer.merged || {}).rows || (xfer.merged || {}).entries)
    + gRows("Gateway turnover", "💳", (paym.merged || {}).payments, [
      { l: "Gateway", k: "gateway" }, { l: "Count", k: "c" }, { l: "Amount", k: "amt", f: x => money(x.amt) }, { l: "Fee", k: "fee", f: x => money(x.fee) }
    ])
    + gRows("Configured providers — per tenant", "🔌", (gw.results || []).filter(r => r.ok && r.data).map(r => {
      const d = r.data;
      return { tenant_id: r.tenant_id, store: r.name, gateways: (d.gateways || []).map(x => x.id).join(", "), carriers: (d.carriers || []).map(x => x.id).join(", "), notifiers: (d.notifiers || []).map(x => x.id).join(", "), country: (d.country || {}).code };
    }))
    + await gTable("settlement")
    + await gTable("upi_handle") + await gTable("escrow_hold") + await gTable("split_payment")
    + await gTable("mandate") + await gTable("bnpl_account") + await gTable("kyc_profile");
}
async function vGoffers() {
  await gMeta();
  const [promos, ret, rec, mem, aff, affPayout] = await Promise.all([
    gFan("/api/admin/promotions"), gFan("/api/admin/retention"), gFan("/api/admin/recurring"), gFan("/api/admin/memberships"),
    gFan("/api/affiliate/affiliates"), gFan("/api/affiliate/payouts")
  ]);
  return gBar("Offers · Subscriptions · Affiliates", "🏷️", "Promotions, retention policy, recurring/membership programmes and the affiliate network, platform-wide.", 4)
    + gRows("Promotions & coupons", "🏷️", (promos.merged || {}).promotions, [
      { l: "Name", k: "name" }, { l: "Type", k: "type" }, { l: "Value", k: "value" }, { l: "Code", k: "code" },
      { l: "Status", k: "status", f: x => `<span class="badge ${esc(x.status)}">${esc(x.status)}</span>` }
    ])
    + gRows("Recurring schedules", "🔁", (rec.merged || {}).recurring || (rec.merged || {}).schedules)
    + gRows("Memberships", "🏅", (mem.merged || {}).memberships)
    + gRows("Retention policy — per tenant", "🗑️", (ret.results || []).filter(r => r.ok && r.data).map(r => ({ tenant_id: r.tenant_id, store: r.name, ...(r.data.retention || r.data.defaults || {}) })))
    + gRows("Affiliates & influencers", "🤝", (aff.merged || {}).affiliates)
    + gRows("Affiliate payouts", "💸", (affPayout.merged || {}).payouts);
}
async function vGsupport() {
  await gMeta();
  const [tk, sla] = await Promise.all([gFan("/api/admin/helpdesk/tickets"), gFan("/api/admin/helpdesk/sla")]);
  return gBar("Support · SLA", "🎧", "The platform's support queue and SLA health — cases, agents and breaches, cross-store.", 2)
    + gRows("Support queue", "🎧", (tk.merged || {}).tickets, [
      { l: "Ref", k: "ref" }, { l: "Subject", k: "subject" }, { l: "Customer", k: "owner_name" },
      { l: "Priority", k: "priority" }, { l: "Status", k: "status" }, { l: "Agent", k: "assignee" }, { l: "CSAT", k: "csat" }
    ])
    + gRows("SLA health", "⏱️", (sla.merged || {}).health || (sla.merged || {}).breaches, [
      { l: "Ref", k: "ref" }, { l: "Priority", k: "priority" }, { l: "Status", k: "status" },
      { l: "Breach", k: "breach", f: x => x.breach ? `<span class="badge suspended">⚠ ${esc(x.breach)}</span>` : "on schedule" }
    ]);
}
async function vGcontent() {
  await gMeta();
  const [rev, queue] = await Promise.all([gFan("/api/admin/reviews"), gFan("/api/admin/ugc/queue")]);
  return gBar("Content · Brands · UGC", "🖼️", "Home content (banners/cards/departments), brands, taxonomy, the EAV attribute catalogue, and reviews/Q&A moderation, platform-wide.", 6)
    + await gTable("brand") + await gTable("banner") + await gTable("card") + await gTable("department")
    + await gTable("taxonomy") + await gTable("attribute")
    + gRows("Latest reviews", "⭐", (rev.merged || {}).reviews, [
      { l: "Product", k: "product_id" }, { l: "Author", k: "name" }, { l: "Rating", k: "rating" },
      { l: "State", k: "state" }, { l: "Helpful", k: "votes_helpful" }
    ])
    + gRows("Moderation queue", "🧹", (queue.merged || {}).reviews
      ? [...(queue.merged || {}).reviews, ...(queue.merged || {}).questions, ...(queue.merged || {}).answers]
      : (queue.merged || {}).queue);
}
async function vGrisk() {
  await gMeta();
  const [risk, trash, tax] = await Promise.all([gFan("/api/admin/risk/queue"), gFan("/api/admin/trash"), gFan("/api/admin/tax/report")]);
  return gBar("Risk · Compliance · Trash", "🛡️", "Fraud queue, soft-delete/retention and tax exposure, plus compliance & localization records — platform-wide.", 3)
    + gRows("Risk / fraud queue", "🛡️", (risk.merged || {}).queue)
    + gRows("Trash — per tenant", "🗑️", (trash.results || []).filter(r => r.ok && r.data).map(r => ({ tenant_id: r.tenant_id, store: r.name, ...(r.data.counts || {}) })))
    + gRows("Tax report", "🧾", (tax.merged || {}).rows || (tax.merged || {}).report || (tax.merged || {}).lines)
    + await gTable("compliance") + await gTable("localization");
}
async function vGteam() {
  await gMeta();
  const [staff, roles, sso, hooks, set] = await Promise.all([
    gFan("/api/admin/staff"), gFan("/api/admin/roles"), gFan("/api/admin/sso"), gFan("/api/admin/webhooks"), gFan("/api/admin/settings")
  ]);
  return gBar("Team · SSO · Webhooks · Settings", "👥", "Staff & RBAC roles, SSO configuration, webhook deliveries and tenant settings — platform-wide.", 4)
    + gRows("Staff", "👥", (staff.merged || {}).staff, [
      { l: "Name", k: "name" }, { l: "Email", k: "email" }, { l: "Role", k: "staff_role" },
      { l: "Disabled", k: "disabled", f: x => x.disabled ? "✓" : "—" }
    ])
    + gRows("RBAC roles", "🔐", (roles.merged || {}).roles)
    + gRows("SSO — per tenant", "🔑", (sso.results || []).filter(r => r.ok && r.data).map(r => ({ tenant_id: r.tenant_id, store: r.name, ...r.data })))
    + gRows("Webhooks", "🔗", (hooks.merged || {}).webhooks)
    + gRows("Webhook deliveries", "📨", (hooks.merged || {}).deliveries)
    + gRows("Tenant settings — per tenant", "⚙️", (set.results || []).filter(r => r.ok && r.data).map(r => ({ tenant_id: r.tenant_id, store: r.name, ...r.data })));
}
async function vGanalytics() {
  await gMeta();
  const [an, mon] = await Promise.all([gFan("/api/admin/analytics"), gFan("/api/admin/monitor")]);
  const a = an.merged || {};
  return gBar("Analytics", "📊", "Revenue mix, top products, funnel and inventory value aggregated platform-wide.", 2)
    + `<div class="p-cards">
      <div class="p-stat"><em>Inventory value</em><b>${money(a.invValue || 0)}</b><small>platform-wide</small></div>
      <div class="p-stat"><em>Funnel views</em><b>${((a.funnel || {}).views) || 0}</b></div>
      <div class="p-stat"><em>Funnel carts</em><b>${((a.funnel || {}).carts) || 0}</b></div>
      <div class="p-stat"><em>Funnel orders</em><b>${((a.funnel || {}).orders) || 0}</b></div>
    </div>`
    + gRows("Top products", "🛒", a.topProducts, [
      { l: "Product", f: x => esc(String(x.title || x.product_id).slice(0, 56)) }, { l: "Units", k: "units" }, { l: "Revenue", k: "rev", f: x => money(x.rev) }
    ])
    + gRows("Revenue by industry", "🏭", a.byIndustry, [{ l: "Industry", k: "industry" }, { l: "Revenue", k: "rev", f: x => money(x.rev) }])
    + gRows("Product types", "🗂️", a.byType, [{ l: "Type", k: "type" }, { l: "Count", k: "c" }])
    + gRows("Experiments (A/B)", "🧪", ((await gFan("/api/admin/experiments")).merged || {}).experiments)
    + gRows("Monitoring — per tenant", "📈", (mon.results || []).filter(r => r.ok && r.data).map(r => ({ tenant_id: r.tenant_id, store: r.name, ...r.data })));
}
async function vGdata() {
  await gMeta();
  const entities = G.entities || [];
  const opts = entities.map(e => `<option value="${esc(e.key)}" ${G.entity === e.key ? "selected" : ""}>${esc(e.key)}</option>`).join("");
  return gBar("Data Explorer", "🧬", "Every entity the platform serves — pick a dataset and filter. The menu is generated from live entity metadata, not a fixed list.", 1)
    + `<div class="p-panel" style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;padding:10px 14px">
      <label style="font-size:13px;color:var(--p-muted)">Dataset</label>
      <select id="gEntity" style="min-width:220px">${opts}</select>
      <span class="p-tag">${entities.length} entities available</span></div>`
    + await gTable(G.entity);
}
function wireGdata() {
  const sel = $("#gEntity");
  if (sel) sel.onchange = () => { G.entity = sel.value; render(); };
}
/* ---------- end Global Operations ---------- */

/* ════════════════════════ THE ZERO-GAP RESOLVERS ════════════════════════
   Any NAV leaf without a dedicated view resolves here. Both reuse the same
   metadata-driven readers the rest of the console uses, so a leaf is NEVER a dead
   link: an entity-backed capability renders as a cross-entity dataset table, a
   universe-backed one renders as its registry record plus its live records. This is
   what "nothing is orphaned" means in practice — the tree is complete by construction,
   and the data is served by the platform, never re-declared in the front-end. */

/* { e: <entityKey> } → the generic platform dataset reader. Falls back to the universe
   entity of the same name when the core registry does not serve the key, so a leaf
   always finds its data wherever it lives. */
async function vEntityLeaf(key, meta) {
  await gMeta();
  const served = (G.entities || []).some(e => e.key === key);
  if (served) {
    return gBar(meta.label.replace(/^\S+\s/, ""), meta.label.match(/^\S+/)?.[0] || "◈",
      "The " + esc(meta.home) + " registry — every record the platform holds for this capability, read through the generic dataset reader.", 1)
      + await gTable(key);
  }
  return vUniverseLeaf(key, meta);
}
/* { u: <universeKey> } → the constitutional registry record for the universe: its
   declaration, its lifecycle state, and its instantiated records. When a universe has
   not been instantiated, the console says so plainly and offers the instantiation path
   rather than rendering an empty table with no explanation. */
async function vUniverseLeaf(key, meta) {
  await gMeta();
  const d = await api("/ucos/universes").catch(() => null);
  const uni = d && (d.universes || []).find(x => x.key === key || x.entity_key === key);
  const title = meta.label.replace(/^\S+\s/, "");
  const icon = meta.label.match(/^\S+/)?.[0] || "◈";
  if (!uni) {
    return gBar(title, icon, "This capability is declared in the constitutional corpus but is not yet bound to a registry record. Nothing is broken — the leaf is reached, and the platform reports the gap honestly instead of faking empty data.", 0)
      + `<div class="p-panel"><div class="p-empty">Not instantiated in this registry.
        <div style="margin-top:10px"><button class="p-btn sm primary" data-uvinst="1">⚡ Instantiate universes from the constitution</button></div></div></div>`;
  }
  const head = gBar(title, icon, "The " + esc(uni.name) + " universe — declared in " + esc(uni.source_doc) + " line " + (uni.source_line || "?") + ", registered as a foundation and instantiated as a live entity (Article 4.2). Fields are derived from the corpus itself; no per-universe code exists.", 1)
    + `<div class="p-cards">
      <div class="p-stat"><em>Concepts</em><b>${stat2(uni.concepts || 0)}</b></div>
      <div class="p-stat"><em>Records</em><b>${stat2(uni.records || 0)}</b></div>
      <div class="p-stat"><em>Lifecycle</em><b>${esc(uni.lifecycle || "—")}</b></div>
      <div class="p-stat"><em>Entity</em><b style="font-size:13px">${esc(uni.entity_key)}</b></div>
    </div>`;
  const served = (G.entities || []).some(e => e.key === uni.entity_key);
  return head
    + (served ? await gTable(uni.entity_key)
      : `<div class="p-panel"><div class="p-empty">Universe entity <code>${esc(uni.entity_key)}</code> holds ${stat2(uni.records || 0)} record(s). Browse them in Data Studio.</div>
         <div style="margin-top:8px"><button class="p-btn sm primary" data-uv="${esc(uni.entity_key)}">Open in Data Studio →</button></div></div>`);
}
function wireLeaf() {
  document.querySelectorAll("[data-uv]").forEach(b => b.onclick = () => { window.__entityJump = b.dataset.uv; view = "studio"; render(); });
  const inst = document.querySelector("[data-uvinst]");
  if (inst) inst.onclick = async () => {
    try { const r = await api("/ucos/universes/instantiate", "POST", {}); toast((r.stats && r.stats.coverage === 100) ? "All universes instantiated" : "Instantiated " + r.instantiated + " of " + r.discovered); render(); }
    catch (e) { toast(e.message); }
  };
}

/* 02 · Knowledge — the industry/category tree. The taxonomy endpoint returns a nested
   tree (industry → category → subcategory), so the view walks it recursively rather than
   flattening the hierarchy: an operator sees the taxonomy the way it is declared. */
async function vTaxonomy() {
  await gMeta();
  const t = await api("/taxonomy");
  const renderNode = (n, d) => `<details class="p-node" ${d < 1 ? "open" : ""} style="margin-left:${d * 14}px">
    <summary><span class="p-ico">${esc(n.icon || "📂")}</span> <b>${esc(n.name)}</b>
      <span class="p-tag">${esc(n.level || "category")}${n.key ? " · " + esc(n.key) : ""}</span>
      ${n.active ? "" : '<span class="p-tag" style="background:var(--p-red);color:#fff">inactive</span>'}</summary>
    ${(n.children || []).map(c => renderNode(c, d + 1)).join("")}</details>`;
  const roots = (t.tree || []).filter(n => n.level === "industry");
  return gBar("Industry · Categories", "🗂️", "The platform's canonical industry → category tree. Every store inherits this taxonomy; nothing here is per-store.", roots.length)
    + `<div class="p-panel">${roots.map(n => renderNode(n, 0)).join("") || '<div class="p-empty">No taxonomy seeded</div>'}</div>`
    + await gTable("taxonomy");
}
/* 02 · Knowledge — brands & manufacturers across stores, through the generic
   platform-data reader (both are standard entities, so no bespoke handler is needed). */
async function vBrands() {
  await gMeta();
  return gBar("Brands · Manufacturers", "🏷️", "The brand and manufacturer registry — the knowledge layer a catalog's provenance resolves against, platform-wide.", 2)
    + await gTable("brand") + await gTable("supplier");
}
/* 09 · Platform — the capability tree: every capability and its sub-capabilities grouped
   by domain, showing which are enabled for the chosen tenant. The constitutional "one
   canonical home" view of what the platform composes from. */
async function vCapabilityTree() {
  capData = await api("/capabilities" + (capTenant ? "?tenant_id=" + encodeURIComponent(capTenant) : ""));
  capTenant = capData.tenant_id;
  const d = capData;
  const byDomain = {};
  for (const c of d.catalog) (byDomain[c.domain] = byDomain[c.domain] || []).push(c);
  const DOMAINS = { marketplace: "🛒 Marketplace", qc: "⚡ Quick-commerce", fintech: "💸 Fintech", trade: "🤝 B2B trust & trade" };
  const tenantOpts = (d.tenants || []).map(t => `<option value="${t.id}" ${t.id === capTenant ? "selected" : ""}>${t.master ? "★ Master platform" : "deployment · " + esc(t.name)} · ${esc(t.slug)}</option>`).join("");
  const domHtml = Object.keys(byDomain).map(dom => {
    const caps = byDomain[dom];
    const on = caps.filter(c => c.on).length;
    /* a capability's params ARE its sub-capabilities — each a tunable facet the platform
       composes, so the tree nests them under their parent capability. */
    const capHtml = caps.map(c => `<details class="p-node" ${c.on ? "open" : ""}>
      <summary><span class="p-ico">${c.on ? "✅" : "⚪"}</span> <b>${esc(c.label || c.key)}</b>
        <code style="font-size:11px">${esc(c.key)}</code>
        <span class="p-tag">${Object.keys(c.params || {}).length} sub-capabilities</span></summary>
      <div style="padding:6px 0 6px 18px;display:flex;flex-direction:column;gap:4px">
        ${Object.entries(c.params || {}).map(([k, p]) => `<div class="p-tag">${esc(p.label || k)} <code style="font-size:10px">${esc(p.type)}${p.unit ? " · " + esc(p.unit) : ""}</code>${p.description ? " — " + esc(p.description) : ""}</div>`).join("") || '<div class="p-empty">No sub-capabilities declared</div>'}
        ${c.description ? `<div style="font-size:12px;color:var(--p-muted)">${esc(c.description)}</div>` : ""}
      </div></details>`).join("");
    return `<div class="p-panel"><div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
      <h2 style="margin:0">${DOMAINS[dom] || "◈ " + esc(dom)}</h2>
      <span class="p-tag">${on}/${caps.length} enabled</span></div>${capHtml}</div>`;
  }).join("");
  return gBar("Capability Tree", "🌳", "Every capability in the constitutional registry and its sub-capabilities, grouped by domain. Toggle and tune in Capabilities; this is the map of what composes.", d.catalog.length)
    + `<div class="p-panel"><label style="font-size:12px">Tenant scope
        <select id="capTenant">${tenantOpts}</select></label></div>`
    + (domHtml || '<div class="p-empty">No capabilities registered</div>');
}
function wireCapabilityTree() {
  const sel = $("#capTenant");
  if (sel) sel.onchange = () => { capTenant = sel.value; render(); };
}
/* 09 · Platform — the composition engine. Application = Capability Composition: any
   declared capability (a universe, a catalog capability, a dataset) is materialized as a
   data model + API + workflow + UI + dashboard + security policy, derived from its own
   declaration. This view is the platform's build surface — an operator picks a declared
   capability and the platform composes it, never the reverse. Every row resolves to real
   machinery; nothing here is a mock. */
let composeFilter = "";
async function vCompose() {
  const c = await api("/compose/candidates");
  const led = await api("/compose/ledger").catch(() => ({ ledger: [] }));
  const ledger = led.ledger || [];
  const k = composeFilter || "";
  const match = x => !k || (x.label + " " + x.key + " " + (x.home || "") + " " + (x.source || "")).toLowerCase().includes(k.toLowerCase());
  const CAP = 120;
  const group = (title, icon, list, note) => {
    const rows = list.filter(match);
    return `<div class="p-panel"><div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;flex-wrap:wrap">
      <h2 style="margin:0">${icon} ${esc(title)}</h2><span class="p-tag">${rows.length}${rows.length > CAP ? " shown of " + list.length : " · all"}</span>
      ${note ? `<span style="font-size:12px;color:var(--p-muted)">${note}</span>` : ""}</div>
      <div class="p-scroll-x"><table class="p-table"><thead><tr><th>Capability</th><th>Key</th><th>Declared in</th><th>Home</th><th>Status</th><th></th></tr></thead>
      <tbody>${rows.slice(0, CAP).map(x => `<tr>
        <td><b>${esc(x.label)}</b>${x.concepts ? ` <span class="p-tag">${x.concepts} concepts</span>` : ""}</td>
        <td><code style="font-size:11px">${esc(x.key)}</code></td>
        <td><span class="p-tag">${esc(x.source || "—")}</span></td>
        <td style="font-size:12px">${esc(x.home || "—")}</td>
        <td>${x.composed ? '<span class="badge canonical">composed</span>' : '<span class="p-tag">declared</span>'}</td>
        <td style="white-space:nowrap">${x.composed
          ? `<button class="p-btn sm" data-recomp="${esc(x.key)}" title="Re-derive from the current declaration">Recompose</button>
             <button class="p-btn sm" data-manifest="${esc(x.key)}" title="Every artifact the composition produced">Manifest</button>`
          : `<button class="p-btn sm primary" data-comp="${esc(x.key)}" title="Materialize this capability's full application surface">Compose</button>`}</td></tr>`).join("")
        || `<tr><td colspan="6" class="p-empty">${k ? "No match for “" + esc(k) + "”" : "Nothing declared"}</td></tr>`}</tbody></table></div></div>`;
  };
  return `<div class="p-head"><h2>🧬 Composition Engine</h2>
    <p class="p-sub">The constitution's central claim, made mechanical — <b>Application = Capability Composition</b>. Compose any declared capability and the platform materializes its data model, REST API, lifecycle workflow, console UI, dashboard and security policy from the declaration itself. This path contains no per-capability code, so a capability the corpus adds tomorrow composes with no new code anywhere.</p></div>
  <div class="p-cards">
    <div class="p-stat"><em>Universes</em><b>${stat2(c.counts.universe)}</b><small>declared in the corpus</small></div>
    <div class="p-stat"><em>Capabilities</em><b>${stat2(c.counts.capability)}</b><small>in the catalog</small></div>
    <div class="p-stat"><em>Datasets</em><b>${stat2(c.counts.entity)}</b><small>declared entities</small></div>
    <div class="p-stat"><em>Composed</em><b>${stat2(c.counts.composed)}</b><small>materialized so far</small></div>
  </div>
  <div class="p-panel" style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;padding:10px 14px">
    <input class="p-search" id="compQ" placeholder="Filter capabilities by name, key or source…" value="${esc(k)}" style="flex:1;min-width:240px">
    <span class="p-tag">${stat2(ledger.length)} composition${ledger.length === 1 ? "" : "s"} in the ledger</span>
  </div>
  ${group("Universes", "🧬", c.universes, "the constitutional corpus's own declarations")}
  ${group("Capabilities", "⚙️", c.capabilities, "the configurable platform's catalog")}
  ${group("Datasets", "🧱", c.entities, "the platform's declared entities")}
  <div class="p-panel"><h2>🧾 Composition ledger</h2>
    <p style="margin:0 0 10px;color:var(--p-muted);font-size:13px">Append-only — every composition and recomposition is recorded with its provenance, so the platform's evolution is itself traceable (Article 7 — Evolution Governance).</p>
    <div class="p-scroll-x"><table class="p-table"><thead><tr><th>Capability</th><th>Model</th><th>Declared in</th><th class="num">Records</th><th>Composed</th></tr></thead>
    <tbody>${ledger.map(e => `<tr>
      <td><b>${esc(e.capability)}</b></td>
      <td><code style="font-size:11px">${esc(e.key)}</code></td>
      <td><span class="p-tag">${esc(e.source || "—")}</span></td>
      <td class="num">${stat2(e.records || 0)}</td>
      <td>${esc(String(e.composed_at || "").replace("T", " ").slice(0, 19))}</td></tr>`).join("")
      || `<tr><td colspan="5" class="p-empty">Nothing composed yet — compose a capability above.</td></tr>`}</tbody></table></div></div>`;
}
function wireCompose() {
  const q = $("#compQ");
  if (q) {
    let tm;
    q.oninput = () => { clearTimeout(tm); const pos = q.selectionStart; tm = setTimeout(() => { render().then(() => { const n = $("#compQ"); if (n) { n.focus(); try { n.setSelectionRange(pos, pos); } catch (e) { } } }); }, 400); };
    q.onkeydown = e => { if (e.key === "Enter") { clearTimeout(tm); render(); } };
  }
  const act = async (key, path, ok) => {
    try { const r = await api(path, "POST", {}); toast(ok + ": " + ((r.model && r.model.label) || key)); render(); }
    catch (e) { toast(e.message); }
  };
  $$("#vBody [data-comp]").forEach(b => b.onclick = () => act(b.dataset.comp, "/compose/" + encodeURIComponent(b.dataset.comp), "Composed"));
  $$("#vBody [data-recomp]").forEach(b => b.onclick = () => act(b.dataset.recomp, "/compose/" + encodeURIComponent(b.dataset.recomp) + "/recompose", "Recomposed"));
  $$("#vBody [data-manifest]").forEach(b => b.onclick = async () => {
    try {
      const m = await api("/compose/" + encodeURIComponent(b.dataset.manifest));
      const a = m.artifacts || {};
      const row = (label, v) => `<div style="display:flex;gap:10px;padding:5px 0;border-bottom:1px solid var(--p-border);font-size:13px"><span style="min-width:130px;color:var(--p-muted)">${label}</span><span>${v}</span></div>`;
      modal(`<div style="display:flex;align-items:center;gap:10px;margin-bottom:10px"><h3 style="margin:0">🧬 ${esc(m.capability)}</h3>
        <span class="p-tag">${esc(m.key)}</span><span style="flex:1"></span>
        <button class="p-btn sm" data-mclose>✕</button></div>
        ${row("Declared in", `<span class="p-tag">${esc(m.source || "—")}</span>`)}
        ${row("Records", `<b>${stat2(m.records || 0)}</b> in the composed dataset`)}
        ${row("Data model", `<code>${esc((a.dataModel || {}).key || "—")}</code> · ${((a.dataModel || {}).fields || 0)} fields · <code>${esc((a.dataModel || {}).endpoint || "")}</code>`)}
        ${row("API", (((a.api || {}).rest || []).map(x => `<code style="font-size:11px">${esc(x)}</code>`).join(" ") || "—"))}
        ${row("Workflow", `<code>${esc((a.workflow || {}).key || "—")}</code> · ${(((a.workflow || {}).steps || []).length)} states · ${(((a.workflow || {}).config || {}).grammar || []).length} grammar tokens`)}
        ${row("UI", `${(((a.ui || {}).listFields || []).length)} list fields · ${(((a.ui || {}).formFields || []).length)} form fields · ${(((a.ui || {}).surfaces || []).join(", ") || "")}`)}
        ${row("Dashboard", `<code>${esc((a.dashboard || {}).key || "—")}</code> · ${(((a.dashboard || {}).widgets || []).length)} widgets`)}
        ${row("Security", `read: ${esc((((a.security || {}).roles || {}).read || []).join(", "))} · write: ${esc((((a.security || {}).roles || {}).write || []).join(", "))}`)}
        ${row("Composed", esc(String(m.composed_at || "").replace("T", " ").slice(0, 19)))}`);
    } catch (e) { toast(e.message); }
  });
}
/* the dedicated views — the console's purpose-built surfaces. Every leaf whose resolver
   is { v: ... } lands here; the generic paths below never re-implement them. */
/* the dedicated views — the console's purpose-built surfaces. Every leaf whose resolver
   is { v: ... } lands here. VIEWFNS produces the HTML; WIREFNS attaches the behaviour and
   runs strictly AFTER innerHTML is assigned, so a wiring pass never looks up a detached
   DOM node (the order bug that made gproducts throw on a null #gpNew). */
const VIEWFNS = {
  dash: () => vDash(),
  tenants: () => vTenants(),
  plans: () => vPlans(),
  subs: () => vSubs(),
  invoices: () => vInvoices(),
  billing: () => vBillingOps(),
  gproducts: () => vGproducts(),
  modules: () => vModules(),
  providers: () => vProviders(),
  ucii: () => vUCII(),
  ucos: () => vUCOS(),
  universes: () => vUniverses(),
  domains: () => vDomains(),
  foundations: () => vFoundations(),
  trace: () => vTrace(),
  ai: () => vAI(),
  offers: () => vGlobalOffers(),
  runtime: () => vRuntime(),
  capabilities: () => vCapabilities(),
  compose: () => vCompose(),
  policies: () => vPolicies(),
  identity: () => viewIdentity(),
  "identity-templates": () => viewIdentityTemplates(),
  themes: () => vThemes(),
  dashboards: () => vDashboards(),
  definitions: () => vDefinitions(),
  geo: () => vGeo(),
  monitor: () => vMonitor(),
  audit: () => vAudit(),
  gops: () => vGops(),
  gorders: () => vGorders(),
  gcatalog: () => vGcatalog(),
  gb2b: () => vGb2b(),
  gmarket: () => vGmarket(),
  gfinance: () => vGfinance(),
  goffers: () => vGoffers(),
  gsupport: () => vGsupport(),
  gcontent: () => vGcontent(),
  grisk: () => vGrisk(),
  gteam: () => vGteam(),
  ganalytics: () => vGanalytics(),
  gdata: () => vGdata(),
  taxonomy: () => vTaxonomy(),
  brands: () => vBrands(),
  "capability-tree": () => vCapabilityTree(),
  /* the Data Studio: a universe's Records button hands the entity over through
     __entityJump; consume it here and replay the preset click in WIREFNS, once the
     Load button actually exists in the DOM. */
  studio: () => { window.__studioPreset = window.__entityJump; window.__entityJump = null; return vStudio(window.__studioPreset); },
  provisioning: () => vProvisioning(),
  registries: () => vRegistries(),
  padmins: () => vPAdmins(),
  roles: () => vRoles(),
  users: () => vUsers(),
  manual: () => { window.open("/docs/user-manual.html", "_blank"); return Promise.resolve('<div class="p-empty">Opened the User Manual in a new tab.</div>'); },
  architecture: () => { window.open("/docs/architecture.html", "_blank"); return Promise.resolve('<div class="p-empty">Opened the Architecture reference in a new tab.</div>'); },
};
const WIREFNS = {
  billing: () => wireBillingOps(),
  gproducts: () => wireGproducts(),
  modules: () => wireModules(),
  ucii: () => wireUCII(),
  ucos: () => wireUCOS(),
  universes: () => wireUniverses(),
  domains: () => wireDomains(),
  foundations: () => wireFoundations(),
  trace: () => wireTrace(),
  offers: () => wireGlobalOffers(),
  runtime: () => wireRuntime(),
  capabilities: () => wireCapabilities(),
  compose: () => wireCompose(),
  policies: () => wirePolicies(),
  identity: () => wireIdentity(),
  "identity-templates": () => wireIdentityTemplates(),
  themes: () => wireThemes(),
  dashboards: () => wireDashboards(),
  definitions: () => wireDefinitions(),
  geo: () => wireGeoFx(),
  "capability-tree": () => wireCapabilityTree(),
  studio: () => { wireStudio(); if (window.__studioPreset) { const b = document.querySelector("#studioLoad"); if (b) b.click(); } },
  gops: () => wireG(),
  gorders: () => wireG(),
  gcatalog: () => wireG(),
  gb2b: () => wireG(),
  gmarket: () => wireG(),
  gfinance: () => wireG(),
  goffers: () => wireG(),
  gsupport: () => wireG(),
  gcontent: () => wireG(),
  grisk: () => wireG(),
  gteam: () => wireG(),
  ganalytics: () => wireG(),
  gdata: () => { wireG(); wireGdata(); },
  padmins: () => wirePAdmins(),
  roles: () => wireRoles(),
  users: () => { wireG(); wireUsers(); },
};
async function render() {
  shell('<div class="p-empty">Loading…</div>');
  const body = $("#vBody");
  try {
    const meta = NAVKEY[view];
    if (!meta) { body.innerHTML = await vDash(); return; }
    /* a leaf the admin's role does not grant never renders, even by direct URL — the
       back-end refuses the same call, so this is defence in depth, not the gate itself */
    if (view !== "dash" && !canSee(view)) {
      const r = meta.res || {};
      body.innerHTML = `<div class="p-empty">🔒 Your platform role does not grant access to “${esc(meta.label.replace(/^\S+\s/, ""))}”.${P.user && P.user.role ? ` <span class="p-tag">role: ${esc(P.user.role)}</span>` : ""}</div>`;
      return;
    }
    const r = meta.res || {};
    if (r.v && VIEWFNS[r.v]) { body.innerHTML = await VIEWFNS[r.v](); if (WIREFNS[r.v]) WIREFNS[r.v](); }
    else if (r.e) { body.innerHTML = await vEntityLeaf(r.e, meta); wireLeaf(); }
    else if (r.u) { body.innerHTML = await vUniverseLeaf(r.u, meta); wireLeaf(); }
    else body.innerHTML = await vDash();
  } catch (e) { body.innerHTML = `<div class="p-empty">⚠️ ${esc(e.message)}</div>`; }
}
document.addEventListener("click", e => { if (e.target.closest("[data-mclose]")) { const mm = document.getElementById("modal"); if (mm) mm.innerHTML = ""; } }); /* __mclose */
(async function boot() {
  /* the unified console (/console.html) loads this bundle inside its own scope and
     drives the views itself; a guest-loaded bundle must not paint #app or it would
     clobber the one shell. LX_GUEST is set by that console's bundle wrapper */
  if (typeof LX_GUEST !== "undefined" && LX_GUEST) return;
  try {
    const me = await api("/platform/me");
    if (!me.admin) {
      $("#app").innerHTML = `<div class="p-login"><div class="p-login-box"><h1>LUXORA</h1><p>Platform Console</p>
        <form id="pf" class="p-form"><label><span>Email</span><input id="pe" type="email" required></label>
        <label><span>Password</span><input id="pp" type="password" required></label>
        <button class="p-btn primary" style="width:100%">Sign in</button></form>
        <p class="p-err hidden" id="pfErr" style="color:var(--p-red);font-size:13px;margin:10px 0 0"></p>
        <p class="hint" id="pfHint"></p>
        <p class="hint" id="pfStores">Store consoles: loading…</p></div></div>`;
      api("/stores").then(st => { const el = document.getElementById("pfStores"); if (el) el.innerHTML = "Store consoles: " + (st.stores || []).map(x => `<a href="/admin.html?store=${esc(x.slug)}">${esc(x.name)}</a>`).join(" · ") + " · <a href='/index.html'>Storefronts</a>"; }).catch(() => { });
      api("/platform/hint").then(h => { const el = document.getElementById("pfHint"); if (el && h.demo && h.email) el.innerHTML = "Owner sign-in: <code>" + esc(h.email) + "</code>" + (h.password ? " / <code>" + esc(h.password) + "</code>" : "") + " — set via env PLATFORM_EMAIL / PLATFORM_PASSWORD."; }).catch(() => { });
      $("#pf").onsubmit = async e => {
        e.preventDefault();
        try { await api("/platform/login", "POST", { email: $("#pe").value, password: $("#pp").value }); boot(); }
        catch (err) { const b = document.getElementById("pfErr"); if (b) { b.innerHTML = "⚠️ " + linkify(err.message); b.classList.remove("hidden"); } toast(err.message); }
      };
      return;
    }
    P.user = me.admin;
    /* the platform console's own RBAC: the admin's grants filter the nav, and a view
       outside them is refused with the same voice the store console uses. An owner's
       grant arrives as ['*'] and everything stays visible. */
    P.allowed = Array.isArray(me.allowed) ? me.allowed : ["*"];
    render();
  } catch (e) { console.error(e); }
})();

async function vDocs() {
  return `<div class="p-head">
    <h2>📄 Architecture & User Manual</h2>
    <p class="p-sub">Documentation for LUXORA Platform</p>
  </div>
  <div class="p-card">
    <h3>📘 User Manual</h3>
    <p>Comprehensive guide for all platform roles (Platform Admin, Store Admin, Customers).</p>
    <p><a href="/docs/user-manual.html" target="_blank">View User Manual</a></p>
    
    <h3>🏛️ Architecture Documentation</h3>
    <p>Technical architecture, data models, and API specifications.</p>
    <p><a href="/docs/architecture.html" target="_blank">View Architecture</a></p>
    
    <h3>📚 Quick Links</h3>
    <ul>
      <li><a href="/GOIP-ROADMAP-2.md" target="_blank">GOIP Roadmap</a></li>
      <li><a href="/README.md" target="_blank">README</a></li>
      <li><a href="/USER_MANUAL.md" target="_blank">Full Manual (Source)</a></li>
    </ul>
  </div>
  <div class="p-card">
    <h3>🔗 API Reference</h3>
    <p>See the platform API endpoints for integration.</p>
    <ul>
      <li><code>POST /api/goip/:capability</code> - GOIP value exchange capabilities</li>
      <li><code>GET /api/platform/security</code> - Security scorecard</li>
      <li><code>GET /healthz</code> - Health check</li>
    </ul>
  </div>`;
}

function wireDocs() {
  // Add click handlers if needed for docs page
}

/* Platform Policies — dynamic, data-driven platform behaviour. Each policy is a
   config_store row keyed policy.<category>; the console edits them live (no restart).
   The table keys on the BARE category (the store strips the policy. prefix), so edit and
   delete address the row the operator actually clicked. */
async function vPolicies() {
  const res = await api("/platform/policies");
  const list = res.policies || [];
  const rows = list.map(p => {
    let cfg = null;
    try { cfg = JSON.parse(p.value || "{}"); } catch (e) { cfg = null; }
    const cat = String(p.key).replace(/^policy\./, "");
    return `<tr>
      <td><code>${esc(cat)}</code></td>
      <td>${cfg == null ? '<span class="badge failed">invalid JSON</span>'
        : `<pre style="max-width:560px;max-height:180px;overflow:auto;margin:0;font-size:12px">${esc(JSON.stringify(cfg, null, 1))}</pre>`}</td>
      <td style="white-space:nowrap">
        <button class="p-btn sm" data-poledit="${esc(cat)}">Edit</button>
        <button class="p-btn sm danger" data-poldel="${esc(cat)}">✕</button>
      </td>
    </tr>`;
  }).join("") || '<tr><td colspan="3" class="p-empty">No policies configured — add one above, or PUT /api/platform/policies/&lt;category&gt; from an integration.</td></tr>';
  return `<div class="p-panel"><h2>🔒 Platform Policies</h2>
    <p class="p-tag">Runtime-configurable platform behaviour — identity, SEO, reviews, search, checkout, features, provisioning. Edits take effect immediately; no restart.</p>
    <div style="margin:10px 0"><button class="p-btn primary" id="polAdd">+ Add Policy</button></div>
    <div class="p-tablewrap"><table class="p-table"><thead>
      <tr><th>Category</th><th>Configuration</th><th>Actions</th></tr>
    </thead><tbody>${rows}</tbody></table></div>
  </div>`;
}

/* one modal serves add and edit: category + a JSON editor seeded with the live value */
function policyModal(category, current) {
  const editing = !!category;
  const m = modal(`<div class="p-modal-head"><h3>${editing ? "Edit policy · " + esc(category) : "Add policy"}</h3><button data-mclose>✕</button></div>
    <div class="p-form">
      <label><span>Category</span><input type="text" id="polCat" ${editing ? "disabled" : ""} value="${esc(category || "")}" placeholder="seo · reviews · features · checkout…"></label>
      <label><span>Configuration (JSON)</span><textarea id="polJson" rows="10" style="font-family:ui-monospace,monospace;font-size:12px">${esc(current != null ? JSON.stringify(current, null, 2) : "{\n  \n}")}</textarea></label>
      <div class="p-err hidden" id="polErr" style="color:var(--p-red);font-size:13px;margin:6px 0"></div>
      <button class="p-btn primary" id="polSave">${editing ? "Save changes" : "Create policy"}</button>
    </div>`);
  m.querySelector("#polSave").onclick = async () => {
    const cat = m.querySelector("#polCat").value.trim().replace(/^policy\./, "");
    const err = m.querySelector("#polErr");
    if (!cat) { err.textContent = "Category required"; err.classList.remove("hidden"); return; }
    let cfg;
    try { cfg = JSON.parse(m.querySelector("#polJson").value || "{}"); }
    catch (e) { err.textContent = "Invalid JSON: " + e.message; err.classList.remove("hidden"); return; }
    try {
      await api(`/platform/policies/${encodeURIComponent(cat)}`, "PUT", cfg);
      m.innerHTML = ""; toast("Policy saved"); render();
    } catch (e) { err.textContent = e.message; err.classList.remove("hidden"); }
  };
}

function deletePolicy(key) {
  if (!confirm("Delete the " + key + " policy?")) return;
  api(`/platform/policies/${encodeURIComponent(key)}`, "DELETE")
    .then(() => { toast("Policy deleted"); render(); })
    .catch(e => toast(e.message));
}

async function wirePolicies() {
  const add = $("#polAdd");
  if (add) add.onclick = () => policyModal("", null);
  document.querySelectorAll("[data-poledit]").forEach(b => b.onclick = async () => {
    const cat = b.dataset.poledit;
    try { const r = await api(`/platform/policies/${encodeURIComponent(cat)}`); policyModal(cat, r.policy || {}); }
    catch (e) { toast(e.message); }
  });
  document.querySelectorAll("[data-poldel]").forEach(b => b.onclick = () => deletePolicy(b.dataset.poldel));
}

/* Themes — every skin the storefront can wear. Presets are data (infinitely
   extendable: an operator dials a hue and names it, and it becomes a reusable
   theme), and any scope can override: platform → tenant → department → product. */
let thHue = 210, thDark = true;
async function vThemes() {
  const d = await api("/themes");
  const presets = d.presets || [];
  const assigns = (d.assignments || []).filter(a => a.scope !== "platform" || a.scope_key === "*");
  const swatch = p => `<div style="width:34px;height:34px;border-radius:9px;background:${p.preview || "linear-gradient(135deg,#999,#333)"};border:1px solid var(--p-line);flex:none"></div>`;
  const presetRows = presets.map(p => `<tr>
    <td>${swatch(p)}</td>
    <td><b>${esc(p.name)}</b><div class="p-tag" style="font-size:11px">${esc(p.key)} · ${p.built_in ? "built-in" : "operator"}</div></td>
    <td><span class="badge ${p.mood === "futurist" ? "failed" : "published"}">${esc(p.mood || "—")}</span></td>
    <td class="p-tag">${Object.keys(p.vars || {}).length} vars</td>
    <td style="white-space:nowrap">
      <button class="p-btn sm" data-thprev="${esc(p.key)}">Preview vars</button>
      <button class="p-btn sm primary" data-thassign="${esc(p.key)}">Assign…</button>
    </td></tr>`).join("");
  const assignRows = assigns.map(a => `<tr>
    <td><span class="badge published">${esc(a.scope)}</span></td>
    <td class="p-tag">${esc(a.scope_key)}</td>
    <td>${esc(a.theme_name || a.theme_key || "—")}</td>
    <td><button class="p-btn sm danger" data-thun="${a.scope}|${esc(a.scope_key)}">Clear</button></td></tr>`).join("");
  const live = await api("/themes/resolve").catch(() => ({}));
  return `
  <div class="p-panel"><h2>🎨 Themes · universal, data-driven skins</h2>
    <p class="p-tag">Every theme is a row in a registry — create one from any hue and it is live, no deploy. Assignments cascade: <b>product → department → tenant → platform</b>; the most specific wins. A live store's own settings remain the default unless a preset is assigned.</p>
    <div style="display:flex;gap:8px;align-items:center;margin:10px 0;flex-wrap:wrap">
      <span class="badge published">live skin: ${esc((live.theme && live.theme.name) || "store settings")}</span>
      <span class="p-tag">${live.via ? "via " + esc(live.via) : "tenant settings.theme"}</span>
    </div>
    <div class="p-scroll-x" style="margin-bottom:14px"><table class="p-table"><thead><tr><th></th><th>Theme</th><th>Mood</th><th>Vars</th><th></th></tr></thead>
      <tbody>${presetRows || '<tr><td colspan="5" class="p-empty">No themes seeded yet</td></tr>'}</tbody></table></div>
    <h3>Generative studio — dial a hue, name it, keep it</h3>
    <p class="p-tag">The palette is a function of a hue, so the theme space is unbounded: the gallery above is finite, this dial is not. Preview live, then save the result as a permanent preset.</p>
    <div style="display:flex;gap:12px;align-items:flex-end;flex-wrap:wrap;margin:10px 0">
      <label style="display:flex;flex-direction:column;gap:4px"><span class="p-tag">Hue <b id="thHueVal">${thHue}°</b></span>
        <input type="range" id="thHue" min="0" max="359" value="${thHue}" style="width:220px;accent-color:var(--p-accent)"></label>
      <label style="display:flex;gap:6px;align-items:center"><input type="checkbox" id="thDark" ${thDark ? "checked" : ""}> Dark mode</label>
      <button class="p-btn sm" id="thPreview">⚡ Preview</button>
      <span style="flex:1"></span>
      <input id="thName" placeholder="Theme name…" style="padding:7px 10px;border:1px solid var(--p-border);border-radius:8px;background:var(--p-bg);width:200px">
      <button class="p-btn sm primary" id="thSave">★ Save as preset</button>
    </div>
    <div id="thVars" class="p-tag" style="margin-top:6px">— press Preview —</div>
    <h3 style="margin-top:16px">Active assignments</h3>
    <div class="p-scroll-x"><table class="p-table"><thead><tr><th>Scope</th><th>Key</th><th>Theme</th><th></th></tr></thead>
      <tbody>${assignRows || '<tr><td colspan="4" class="p-empty">No overrides — the store wears its own settings.theme</td></tr>'}</tbody></table></div>
  </div>`;
}
function wireThemes() {
  const hue = document.getElementById("thHue");
  if (hue) hue.oninput = () => { document.getElementById("thHueVal").textContent = hue.value + "°"; thHue = Number(hue.value); };
  const dk = document.getElementById("thDark");
  if (dk) dk.onchange = () => { thDark = dk.checked; };
  const prev = document.getElementById("thPreview");
  if (prev) prev.onclick = async () => {
    try {
      const r = await api("/themes/preview?hue=" + thHue + (thDark ? "" : "&light=1"));
      const v = r.vars || {};
      document.getElementById("thVars").innerHTML = Object.keys(v).slice(0, 10)
        .map(k => "<code>" + k + "</code>=" + String(v[k]).slice(0, 28)).join(" · ") + " …";
      /* live-dress this console so the operator sees the skin in situ */
      const root = document.documentElement.style;
      for (const [k, val] of Object.entries(v)) if (k.startsWith("--")) root.setProperty(k, val);
    } catch (e) { toast(e.message); }
  };
  const save = document.getElementById("thSave");
  if (save) save.onclick = async () => {
    const name = document.getElementById("thName").value.trim();
    if (!name) return toast("name the theme first");
    try {
      const r = await api("/themes", "POST", { key: name.toLowerCase().replace(/[^a-z0-9-]+/g, "-"), name, hue: thHue, dark: thDark });
      if (r.ok) { toast("Theme '" + name + "' saved — assignable everywhere"); render(); }
      else toast(r.error || "save failed");
    } catch (e) { toast(e.message); }
  };
  document.querySelectorAll("[data-thassign]").forEach(b => b.onclick = async () => {
    const key = b.dataset.thassign;
    const scope = prompt("Scope for '" + key + "': platform | tenant | dept | product", "tenant");
    if (!scope) return;
    const scopeKey = prompt("Scope key (tenant id / dept key / product id; '*' for platform)", scope === "platform" ? "*" : String(window.__tenantId || 1));
    if (scopeKey == null) return;
    try {
      const r = await api("/themes/assign", "POST", { scope, scope_key: scopeKey, theme_key: key });
      toast(r.ok ? "Assigned " + key + " to " + scope + ":" + scopeKey : (r.error || "assign failed"));
      render();
    } catch (e) { toast(e.message); }
  });
  document.querySelectorAll("[data-thprev]").forEach(b => b.onclick = () => {
    const p = (document.__presets || []).find(x => x.key === b.dataset.thprev);
    if (!p) return;
    const root = document.documentElement.style;
    for (const [k, v] of Object.entries(p.vars || {})) if (k.startsWith("--")) root.setProperty(k, v);
    toast("Previewing " + p.name + " on this console");
  });
  document.querySelectorAll("[data-thun]").forEach(b => b.onclick = async () => {
    const [scope, scopeKey] = b.dataset.thun.split("|");
    try { await api("/themes/unassign", "POST", { scope, scope_key: scopeKey }); toast("Override cleared"); render(); }
    catch (e) { toast(e.message); }
  });
}

/* Capabilities — the configuration layer. A store IS the set of capabilities it
   has switched on; every standard, quality, feature and functionality below is a
   row, tuned live from this console, and an archetype is a named reusable blend.
   No vendor or brand name is baked into any definition — parity with any platform
   is a consequence of the composition, never a label. */
let capData = null, capTenant = null;
async function vCapabilities() {
  capData = await api("/capabilities" + (capTenant ? "?tenant_id=" + encodeURIComponent(capTenant) : ""));
  capTenant = capData.tenant_id;
  const d = capData;
  const byDomain = {};
  for (const c of d.catalog) (byDomain[c.domain] = byDomain[c.domain] || []).push(c);
  const onCount = d.catalog.filter(c => c.on).length;
  const tenantOpts = (d.tenants || []).map(t => `<option value="${t.id}" ${t.id === capTenant ? "selected" : ""}>${t.master ? "★ Master platform" : "deployment · " + esc(t.name)} · ${esc(t.slug)}</option>`).join("");
  const presetRows = (d.presets || []).map(p => `<tr>
    <td><b>${esc(p.label)}</b><br><code>${esc(p.key)}</code></td>
    <td class="p-tag">${esc(p.description || "—")}</td>
    <td class="num">${Object.keys(p.capabilities || {}).length}</td>
    <td style="white-space:nowrap">
      <button class="p-btn sm primary" data-cappreset="${esc(p.key)}">Apply</button>
      <button class="p-btn sm danger" data-cappdel="${esc(p.key)}">✕</button></td></tr>`).join("");
  const DOMAINS = { marketplace: "🛒 Marketplace", qc: "⚡ Quick-commerce", fintech: "💸 Fintech", trade: "🤝 B2B trust & trade" };
  const domLabel = dom => DOMAINS[dom] || "◈ " + esc(dom).replace(/^\w/, c => c.toUpperCase());
  const catHtml = Object.keys(byDomain).map(dom => {
    const rows = byDomain[dom].map(c => {
      const ps = c.params || {}, pkeys = Object.keys(ps);
      const pIn = pkeys.map(k => {
        const def = ps[k], v = (c.effective && c.effective[k] !== undefined) ? c.effective[k] : def.default;
        const lab = `<label style="display:flex;flex-direction:column;gap:2px;font-size:12px"><span class="p-tag">${esc(def.label || k)} <code style="font-size:10px">${esc(def.type)}${def.unit ? " · " + esc(def.unit) : ""}</code></span>`;
        if (def.type === "bool") return lab + `<input type="checkbox" data-capinp="${esc(c.key)}|${esc(k)}" ${v ? "checked" : ""}></label>`;
        if (def.type === "json") return lab + `<textarea data-capinp="${esc(c.key)}|${esc(k)}" rows="2" style="min-width:180px;font-family:monospace;font-size:12px">${esc(typeof v === "string" ? v : JSON.stringify(v))}</textarea></label>`;
        if (def.type === "number") return lab + `<input type="number" step="any" data-capinp="${esc(c.key)}|${esc(k)}" value="${esc(v)}"></label>`;
        return lab + `<input type="text" data-capinp="${esc(c.key)}|${esc(k)}" value="${esc(v)}"></label>`;
      }).join("");
      return `<tr>
        <td style="font-size:17px">${esc(c.icon || "▪")}</td>
        <td><b>${esc(c.label)}</b> ${c.edited ? '<span class="badge draft">edited</span>' : ""}<br><code>${esc(c.key)}</code></td>
        <td class="p-tag">${esc(c.description || "")}</td>
        <td style="white-space:nowrap">
          <span class="badge ${c.enabled ? "published" : "draft"}">${c.enabled ? "platform on" : "platform off"}</span><br>
          <button class="p-btn sm ${c.on ? "primary" : ""}" data-captoggle="${esc(c.key)}">${c.on ? "● ON for store" : "○ off"}</button></td>
        <td>${pkeys.length ? `<button class="p-btn sm" data-capcfg="${esc(c.key)}">⚙ ${pkeys.length}</button>` : '<span class="p-tag">no params</span>'}
          ${c.seeded_from === "operator" ? `<button class="p-btn sm danger" data-capdel="${esc(c.key)}" title="delete authored capability">✕</button>` : ""}</td></tr>
        ${pkeys.length ? `<tr class="capcfg" id="capcfg-${esc(c.key)}" style="display:none"><td colspan="5" style="background:var(--p-bg);padding:10px">
          <div style="display:flex;gap:14px;flex-wrap:wrap">${pIn}</div>
          <button class="p-btn sm primary" style="margin-top:8px" data-capsave="${esc(c.key)}">Save tuning</button>
          <span class="p-tag">defaults come from the catalog; your values override them for this store</span></td></tr>` : ""}`;
    }).join("");
    return `<h4 style="margin:16px 0 6px">${domLabel(dom)}</h4>
      <div class="p-scroll-x"><table class="p-table"><thead><tr><th></th><th>Capability</th><th>What it governs</th><th>State</th><th>Tuning</th></tr></thead>
      <tbody>${rows}</tbody></table></div>`;
  }).join("");
  const checkList = d.catalog.map(c => `<label style="display:flex;gap:5px;align-items:center;font-size:12px;min-width:160px"><input type="checkbox" data-capnew="${esc(c.key)}"> ${esc(c.icon || "▪")} ${esc(c.label)}</label>`).join("");
  return `
  <div class="p-panel"><h2>⚙️ Capabilities · the configurable platform</h2>
    <p class="p-tag">A platform is not a template and no vendor name defines one — it is <b>the set of capabilities the master has switched on</b>. Everything below is a row: switch a capability on, tune its standards (weights, thresholds, fees, SLAs), and the master becomes that platform — an e-commerce platform, an ERP, a ride-hailing platform, a consultancy platform, or a type no one has named yet. The engines read this table at runtime and are inert while a capability is off, so changing a row is the whole deploy.</p>
    <div style="display:flex;gap:10px;align-items:center;margin:12px 0;flex-wrap:wrap">
      <label style="display:flex;gap:6px;align-items:center"><span class="p-tag">Composing</span>
        <select id="capTenant" style="padding:7px 10px;border:1px solid var(--p-border);border-radius:8px;background:var(--p-bg)">${tenantOpts}</select></label>
      <span class="badge published">${onCount} of ${d.catalog.length} on</span>
      ${d.composition && d.composition.preset ? `<span class="p-tag">archetype: <b>${esc(d.composition.preset)}</b></span>` : '<span class="p-tag">composed capability-by-capability</span>'}
    </div>
    <h3>Archetypes — named, reusable compositions</h3>
    <p class="p-tag">An archetype is a starter set. Applying one writes capability rows for the store; from that moment the store owns them and any tuning is kept.</p>
    <div class="p-scroll-x" style="margin-bottom:14px"><table class="p-table"><thead><tr><th>Archetype</th><th>Intent</th><th>Caps</th><th></th></tr></thead>
      <tbody>${presetRows || '<tr><td colspan="4" class="p-empty">No archetypes defined</td></tr>'}</tbody></table></div>
    <details><summary class="p-tag" style="cursor:pointer">＋ Define a new archetype (custom platform or service)</summary>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin:8px 0">
        <input id="capNewKey" placeholder="key (e.g. blend_luxury)" style="padding:7px 10px;border:1px solid var(--p-border);border-radius:8px;background:var(--p-bg);width:210px">
        <input id="capNewLabel" placeholder="Label" style="padding:7px 10px;border:1px solid var(--p-border);border-radius:8px;background:var(--p-bg);width:180px">
        <button class="p-btn sm primary" id="capNewSave">Create archetype</button>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px">${checkList}</div></details>
    <details><summary class="p-tag" style="cursor:pointer">＋ Define a new capability (the catalog is open-ended — any platform, any domain)</summary>
      <p class="p-tag" style="margin:8px 0">The seeded catalog covers commerce. A platform beyond that — mobility, streaming, ERP, CRM, anything not yet named — is built by <b>defining its capabilities here</b> with typed parameters. Engines read them through the same <code>cap()</code> call, so a new domain is live the moment it is saved.</p>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin:8px 0">
        <input id="capDefKey" placeholder="key (e.g. surge_pricing)" style="padding:7px 10px;border:1px solid var(--p-border);border-radius:8px;background:var(--p-bg);width:190px">
        <input id="capDefLabel" placeholder="Label (e.g. Surge pricing)" style="padding:7px 10px;border:1px solid var(--p-border);border-radius:8px;background:var(--p-bg);width:180px">
        <input id="capDefDomain" placeholder="domain (e.g. mobility)" style="padding:7px 10px;border:1px solid var(--p-border);border-radius:8px;background:var(--p-bg);width:160px">
        <input id="capDefIcon" placeholder="🚗" maxlength="3" style="padding:7px 10px;border:1px solid var(--p-border);border-radius:8px;background:var(--p-bg);width:60px">
        <input id="capDefDesc" placeholder="what it governs" style="padding:7px 10px;border:1px solid var(--p-border);border-radius:8px;background:var(--p-bg);flex:2;min-width:220px">
        <button class="p-btn sm primary" id="capDefSave">Create capability</button>
      </div>
      <div id="capDefParams" style="display:flex;flex-direction:column;gap:6px;margin:6px 0 4px"></div>
      <button class="p-btn sm" id="capDefAddParam">＋ add parameter</button>
      <span class="p-tag"> each parameter is typed: number · bool · text · json — the type governs the form and the coercion </span>
    </details>
    ${catHtml}
  </div>`;
}
function wireCapabilities() {
  const sel = document.getElementById("capTenant");
  if (sel) sel.onchange = () => { capTenant = Number(sel.value); render(); };
  document.querySelectorAll("[data-captoggle]").forEach(b => b.onclick = async () => {
    const key = b.dataset.captoggle, on = /ON/.test(b.textContent);
    try {
      if (on) { await api("/capabilities/disable", "POST", { capability: key, tenant_id: capTenant }); toast(key + " switched off"); }
      else { await api("/capabilities/enable", "POST", { capability: key, tenant_id: capTenant }); toast(key + " switched on"); }
      render();
    } catch (e) { toast(e.message); }
  });
  document.querySelectorAll("[data-capcfg]").forEach(b => b.onclick = () => {
    const row = document.getElementById("capcfg-" + b.dataset.capcfg);
    if (row) row.style.display = row.style.display === "none" ? "" : "none";
  });
  document.querySelectorAll("[data-capsave]").forEach(b => b.onclick = async () => {
    const key = b.dataset.capsave;
    const all = Array.from(document.querySelectorAll("[data-capinp]")).filter(el => el.dataset.capinp.startsWith(key + "|"));
    if (!all.length) return toast("no parameters to save");
    let saved = 0;
    for (const el of all) {
      const [, param] = el.dataset.capinp.split("|");
      const val = el.type === "checkbox" ? el.checked : el.value;
      try { await api("/capabilities/param", "POST", { capability: key, param, value: val, tenant_id: capTenant }); saved++; }
      catch (e) { toast(key + "." + param + ": " + e.message); return; }
    }
    toast(saved + " parameter" + (saved > 1 ? "s" : "") + " saved for " + key);
    render();
  });
  document.querySelectorAll("[data-cappreset]").forEach(b => b.onclick = async () => {
    try {
      const r = await api("/capabilities/preset/apply", "POST", { preset: b.dataset.cappreset, tenant_id: capTenant });
      toast("Archetype applied: " + Object.keys(r.capabilities || {}).length + " capabilities");
      render();
    } catch (e) { toast(e.message); }
  });
  document.querySelectorAll("[data-cappdel]").forEach(b => b.onclick = async () => {
    if (!confirm("Delete archetype '" + b.dataset.cappdel + "'?")) return;
    try { await api("/capabilities/preset/delete", "POST", { preset: b.dataset.cappdel }); toast("Archetype deleted"); render(); }
    catch (e) { toast(e.message); }
  });
  document.querySelectorAll("[data-capdel]").forEach(b => b.onclick = async () => {
    if (!confirm("Delete capability '" + b.dataset.capdel + "'? A store using it must switch it off first.")) return;
    try { await api("/capabilities/catalog/" + encodeURIComponent(b.dataset.capdel), "DELETE"); toast("Capability deleted"); render(); }
    catch (e) { toast(e.message); }
  });
  const ns = document.getElementById("capNewSave");
  if (ns) ns.onclick = async () => {
    const key = document.getElementById("capNewKey").value.trim();
    if (!key) return toast("give the archetype a key");
    const capsOn = Array.from(document.querySelectorAll("[data-capnew]")).filter(c => c.checked).map(c => c.dataset.capnew);
    if (!capsOn.length) return toast("select at least one capability");
    try {
      const capObj = {}; capsOn.forEach(c => capObj[c] = { enabled: true, params: {} });
      await api("/capabilities/preset", "POST", { key, label: document.getElementById("capNewLabel").value.trim() || key, capabilities: capObj });
      toast("Archetype '" + key + "' created — apply it to any store");
      render();
    } catch (e) { toast(e.message); }
  };
  /* ── capability authoring: the open-ended catalog ── */
  const paramRow = (i) => `<div style="display:flex;gap:6px;flex-wrap:wrap" data-capdefrow="${i}">
    <input placeholder="param key" data-capdef-pk style="padding:6px 9px;border:1px solid var(--p-border);border-radius:8px;background:var(--p-bg);width:150px">
    <input placeholder="label" data-capdef-pl style="padding:6px 9px;border:1px solid var(--p-border);border-radius:8px;background:var(--p-bg);width:150px">
    <select data-capdef-pt style="padding:6px 9px;border:1px solid var(--p-border);border-radius:8px;background:var(--p-bg)">
      <option value="number">number</option><option value="bool">bool</option><option value="text">text</option><option value="json">json</option></select>
    <input placeholder="default value" data-capdef-pd style="padding:6px 9px;border:1px solid var(--p-border);border-radius:8px;background:var(--p-bg);width:150px"></div>`;
  let paramRows = 0;
  const addP = document.getElementById("capDefAddParam");
  if (addP) addP.onclick = () => {
    paramRows++;
    const host = document.getElementById("capDefParams");
    const wrap = document.createElement("div");
    wrap.innerHTML = paramRow(paramRows);
    host.appendChild(wrap.firstElementChild);
  };
  const ds = document.getElementById("capDefSave");
  if (ds) ds.onclick = async () => {
    const key = document.getElementById("capDefKey").value.trim();
    const label = document.getElementById("capDefLabel").value.trim();
    if (!key || !label) return toast("give the capability a key and a label");
    const params = {};
    document.querySelectorAll("[data-capdefrow]").forEach(row => {
      const pk = row.querySelector("[data-capdef-pk]").value.trim();
      if (!pk) return;
      const t = row.querySelector("[data-capdef-pt]").value;
      const raw = row.querySelector("[data-capdef-pd]").value;
      let d = raw;
      if (t === "number") d = raw === "" ? 0 : Number(raw);
      else if (t === "bool") d = /^(1|true|yes|on)$/i.test(raw);
      else if (t === "json") { try { d = raw === "" ? {} : JSON.parse(raw); } catch (e) { return toast("param '" + pk + "': invalid JSON default"); } }
      params[pk] = { type: t, default: d, label: row.querySelector("[data-capdef-pl]").value.trim() || pk };
    });
    try {
      await api("/capabilities/catalog", "POST", {
        key, label, domain: document.getElementById("capDefDomain").value.trim() || "custom",
        icon: document.getElementById("capDefIcon").value.trim() || "▪",
        description: document.getElementById("capDefDesc").value.trim(), params
      });
      toast("Capability '" + key + "' defined — switch it on for any store");
      render();
    } catch (e) { toast(e.message); }
  };
}

/* Dashboards & Reports — Architecture1 §394/§395 made visible. A dashboard is a runtime
    object: pick one and the engine renders every widget it declares, computed live from the
   entity each widget points at. The picker below is derived from the engine itself
   (entities, metrics, visualization kinds), and the "＋ widget" action is one row — the
   operator never writes code to get a new KPI. Reports (§395) run the same data through
   Data → Analytics → Visualization → Report on demand. */
let dbSel = null, dbEntities = [], dbWidgetDash = null;
async function vDashboards() {
  const [listRes, entRes, repRes] = await Promise.all([
    api("/dashboards").catch(() => ({ dashboards: [] })),
    api("/dashboards/entities").catch(() => ({ entities: [], metrics: [], kinds: [] })),
    api("/reports").catch(() => ({ reports: [] }))
  ]);
  const ds = listRes.dashboards || [];
  dbEntities = entRes.entities || [];
  const metrics = entRes.metrics || [], kinds = entRes.kinds || [];
  if (!dbSel || !ds.some(d => d.key === dbSel)) dbSel = ds.length ? ds[0].key : null;
  const active = dbSel ? await api("/dashboards/" + encodeURIComponent(dbSel)).catch(() => ({ widgets: [] })) : { widgets: [] };
  const renderWidget = w => {
    if (w.error) return `<div class="db-card" style="grid-column:span ${w.span || 3}"><div class="db-kpi-label">${esc(w.label)}</div><div class="p-tag" style="color:var(--p-danger)">⚠ ${esc(w.error)}</div></div>`;
    if (w.kind === "kpi") return `<div class="db-card" style="grid-column:span ${w.span || 3}">
      <div class="db-kpi-label">${esc(w.label)}</div>
      <div class="db-kpi-value">${fmtNum(w.value)}</div>
      <div class="p-tag">${esc(w.metric)}${w.column ? " · " + esc(w.column) : ""} · ${esc(w.entity)}</div></div>`;
    const buckets = w.buckets || [];
    const max = Math.max(1, ...buckets.map(b => Math.abs(Number(b.value) || 0)));
    if (w.kind === "bar") return `<div class="db-card" style="grid-column:span ${w.span || 3}">
      <div class="db-kpi-label">${esc(w.label)}</div>
      <div class="db-bars">${buckets.map(b => `<div class="db-bar-row"><span class="db-bar-k">${esc(String(b.key).slice(0, 22))}</span>
        <div class="db-bar-track"><div class="db-bar-fill" style="width:${Math.max(2, Math.abs(Number(b.value) || 0) / max * 100)}%"></div></div>
        <span class="db-bar-v">${fmtNum(b.value)}</span></div>`).join("") || '<div class="p-empty">no data</div>'}</div></div>`;
    if (w.kind === "donut") { const tot = buckets.reduce((a, b) => a + (Number(b.value) || 0), 0) || 1;
      let acc = 0;
      const segs = buckets.map((b, i) => { const frac = (Number(b.value) || 0) / tot; const seg = `<circle cx="32" cy="32" r="26" fill="none" stroke="hsl(${(i * 67 + 190) % 360} 70% 55%)" stroke-width="12" stroke-dasharray="${(frac * 163).toFixed(1)} 163" stroke-dashoffset="${(-acc * 163).toFixed(1)}" transform="rotate(-90 32 32)"></circle>`; acc += frac; return seg; }).join("");
      return `<div class="db-card" style="grid-column:span ${w.span || 3}"><div class="db-kpi-label">${esc(w.label)}</div>
        <div style="display:flex;gap:14px;align-items:center"><svg width="64" height="64" viewBox="0 0 64 64">${segs || '<circle cx="32" cy="32" r="26" fill="none" stroke="var(--p-line)" stroke-width="12"/>'}</svg>
        <div style="flex:1;min-width:0">${buckets.slice(0, 6).map((b, i) => `<div style="display:flex;justify-content:space-between;font-size:12px;padding:1px 0"><span style="color:var(--p-muted)"><i style="display:inline-block;width:9px;height:9px;border-radius:2px;background:hsl(${(i * 67 + 190) % 360} 70% 55%);margin-right:5px"></i>${esc(String(b.key).slice(0, 18))}</span><b>${fmtNum(b.value)}</b></div>`).join("") || '<div class="p-empty">no data</div>'}</div></div></div>`; }
    if (w.kind === "line") { const vals = buckets.map(b => Number(b.value) || 0); const mx = Math.max(1, ...vals), mn = Math.min(0, ...vals);
      const pts = vals.map((v, i) => `${(i / Math.max(1, vals.length - 1) * 100).toFixed(1)},${(100 - (v - mn) / Math.max(1, mx - mn) * 92).toFixed(1)}`).join(" ");
      return `<div class="db-card" style="grid-column:span ${w.span || 3}"><div class="db-kpi-label">${esc(w.label)}</div>
        <svg viewBox="0 0 100 100" preserveAspectRatio="none" style="width:100%;height:120px">${vals.length > 1 ? `<polyline points="${pts}" fill="none" stroke="var(--p-accent)" stroke-width="2.5" vector-effect="non-scaling-stroke"/>` : '<text x="50" y="50" text-anchor="middle" fill="var(--p-muted)" font-size="9">need 2+ points</text>'}</svg>
        <div class="p-tag">${buckets.length} groups · ${esc(w.dimension || "")}</div></div>`; }
    /* table */
    return `<div class="db-card" style="grid-column:span ${w.span || 3}"><div class="db-kpi-label">${esc(w.label)}</div>
      <table class="p-table" style="font-size:12px"><thead><tr><th>${esc(w.dimension || "group")}</th><th style="text-align:right">${esc(w.metric)}${w.column ? "(" + esc(w.column) + ")" : ""}</th></tr></thead>
      <tbody>${buckets.map(b => `<tr><td>${esc(String(b.key).slice(0, 30))}</td><td style="text-align:right"><b>${fmtNum(b.value)}</b></td></tr>`).join("") || '<tr><td colspan="2" class="p-empty">no data</td></tr>'}</tbody></table></div>`;
  };
  const entOpts = dbEntities.map(e => `<option value="${esc(e.key)}">${esc(e.icon || "🧩")} ${esc(e.label)}</option>`).join("");
  const widgetForm = `<details style="margin-top:14px"><summary style="cursor:pointer;padding:8px 0"><b>＋ Add a widget</b> <span class="p-tag">— a KPI is one row, computed by the engine</span></summary>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;padding:12px 0">
      <label><span class="p-tag">Label</span><input id="dwLabel" class="p-input" placeholder="e.g. Revenue this month"></label>
      <label><span class="p-tag">Visualization</span><select id="dwKind" class="p-input">${kinds.map(k => `<option value="${k}">${k}</option>`).join("")}</select></label>
      <label><span class="p-tag">Entity</span><select id="dwEntity" class="p-input">${entOpts}</select></label>
      <label><span class="p-tag">Metric</span><select id="dwMetric" class="p-input">${metrics.map(m => `<option value="${m}">${m}</option>`).join("")}</select></label>
      <label><span class="p-tag">Column (sum/avg/…)</span><input id="dwColumn" class="p-input" placeholder="total"></label>
      <label><span class="p-tag">Group by</span><input id="dwDim" class="p-input" placeholder="status"></label>
      <label><span class="p-tag">Span (1-6)</span><input id="dwSpan" class="p-input" type="number" min="1" max="6" value="3"></label>
      <button class="p-btn primary" id="dwAdd" style="align-self:end">＋ Add widget</button>
    </div>
    <div id="dwFields" class="p-tag"></div></details>`;
  const tabs = ds.map(d => `<button class="p-btn sm ${d.key === dbSel ? "primary" : ""}" data-dbtab="${esc(d.key)}">${esc(d.icon || "📊")} ${esc(d.name)}</button>`).join("")
    || '<span class="p-empty">No dashboards yet</span>';
  const reps = repRes.reports || [];
  const repRows = reps.map(r => `<tr>
    <td><b>${esc(r.name)}</b><div class="p-tag">${esc(r.key)} · ${esc(r.entity)}</div></td>
    <td><span class="badge ${r.kind === "Regulatory" ? "failed" : "published"}">${esc(r.kind)}</span></td>
    <td class="p-tag">${esc(r.schedule)}</td>
    <td class="p-tag">${esc(r.last_run ? String(r.last_run).slice(0, 16) : "never")}</td>
    <td style="white-space:nowrap"><button class="p-btn sm" data-reprun="${esc(r.key)}">▶ Run</button>
      <button class="p-btn sm danger" data-repdel="${esc(r.key)}">Delete</button></td></tr>`).join("");
  return `
  <div class="p-panel"><h2>📊 Dashboards · the universal dashboard engine (Architecture1 §394)</h2>
    <p class="p-tag">A dashboard is a <b>runtime object</b>: each widget below is a row pointing at an entity and a metric, computed live by one generic engine — no per-dashboard code, no deploy. Add a KPI with the form under any board; a new dashboard is a POST to <code>/api/dashboards</code>. Every visualization here (KPI · bars · donut · line · table) is drawn from the same two engine outputs: a scalar <code>value</code> or a list of <code>buckets</code>.</p>
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin:10px 0">${tabs}</div>
    ${active.widgets && active.widgets.length ? `<div class="db-grid" style="display:grid;grid-template-columns:repeat(6,1fr);gap:12px">${(active.widgets || []).map(renderWidget).join("")}</div>`
      : '<div class="p-empty" style="padding:20px">This dashboard has no widgets yet — add the first one below.</div>'}
    ${widgetForm}
    <div style="display:flex;gap:8px;margin-top:14px;flex-wrap:wrap">
      <button class="p-btn sm" id="dbNew">＋ New dashboard</button>
      ${dbSel ? `<button class="p-btn sm danger" id="dbDel">Delete this dashboard</button>` : ""}
    </div>
  </div>
  <div class="p-panel" style="margin-top:14px"><h2>📄 Reports · the reporting engine (Architecture1 §395)</h2>
    <p class="p-tag">A report is the pipeline the constitution names — <b>Data → Analytics → Visualization → Report</b> — declared as a row: entity, metrics, dimensions, cadence. Scheduled reports run when read; run any report on demand. Output is columns + rows, so a downstream tool or the <b>Data Studio</b> can dress it.</p>
    <div class="p-scroll-x"><table class="p-table"><thead><tr><th>Report</th><th>Kind</th><th>Schedule</th><th>Last run</th><th></th></tr></thead>
      <tbody>${repRows || '<tr><td colspan="5" class="p-empty">No reports declared</td></tr>'}</tbody></table></div>
    <div id="repOut" style="margin-top:10px"></div>
  </div>`;
}
function fmtNum(v) { const n = Number(v); if (!isFinite(n)) return "—"; return Math.abs(n) >= 1000 ? n.toLocaleString(undefined, { maximumFractionDigits: 1 }) : String(Math.round(n * 100) / 100); }
function wireDashboards() {
  document.querySelectorAll("[data-dbtab]").forEach(b => b.onclick = () => { dbSel = b.dataset.dbtab; render(); });
  document.querySelectorAll("[data-reprun]").forEach(b => b.onclick = async () => {
    try {
      const r = await api("/reports/" + encodeURIComponent(b.dataset.reprun) + "/run");
      const el = document.getElementById("repOut");
      if (r.error) { el.innerHTML = '<div class="p-tag" style="color:var(--p-danger)">⚠ ' + esc(r.error) + '</div>'; return; }
      const cols = r.columns || [];
      el.innerHTML = `<h3 style="margin:10px 0 4px">${esc(r.report.name)} <span class="p-tag">${r.rows.length} rows · ${esc(new Date(r.generatedAt).toLocaleString())}</span></h3>
        <div class="p-scroll-x"><table class="p-table" style="font-size:12px"><thead><tr>${cols.map(c => `<th>${esc(c)}</th>`).join("")}</tr></thead>
        <tbody>${r.rows.slice(0, 25).map(row => `<tr>${cols.map(c => `<td>${esc(fmtNum(row[c]))}</td>`).join("")}</tr>`).join("") || '<tr><td colspan="' + cols.length + '" class="p-empty">no rows</td></tr>'}</tbody></table></div>`;
    } catch (e) { toast(e.message); }
  });
  document.querySelectorAll("[data-repdel]").forEach(b => b.onclick = async () => {
    try { await api("/reports/" + encodeURIComponent(b.dataset.repdel), "DELETE"); toast("Report deleted"); render(); }
    catch (e) { toast(e.message); }
  });
  const add = document.getElementById("dwAdd");
  if (add) add.onclick = async () => {
    const g = id => (document.getElementById(id) || {}).value || "";
    try {
      const r = await api("/dashboards/" + encodeURIComponent(dbSel) + "/widgets", "POST",
        { label: g("dwLabel") || "New KPI", kind: g("dwKind"), entity: g("dwEntity"), metric: g("dwMetric"), column: g("dwColumn"), dimension: g("dwDim"), span: Number(g("dwSpan")) || 3 });
      if (r.ok) { toast("Widget added — engine is computing it now"); render(); } else toast(r.error || "add failed");
    } catch (e) { toast(e.message); }
  };
  const ent = document.getElementById("dwEntity");
  if (ent) ent.onchange = () => {
    const e = dbEntities.find(x => x.key === ent.value);
    const el = document.getElementById("dwFields");
    if (el && e) el.textContent = "fields: " + e.fields.map(f => f.col || f.key).join(", ");
  };
  const nw = document.getElementById("dbNew");
  if (nw) nw.onclick = async () => {
    const name = prompt("Dashboard name", "My Dashboard");
    if (!name) return;
    try {
      const r = await api("/dashboards/new", "POST", { name, type: "Operational", audience: "admin" });
      if (r.ok) { dbSel = r.key; toast("Dashboard created — add widgets"); render(); } else toast(r.error || "create failed");
    } catch (e) { toast(e.message); }
  };
  const del = document.getElementById("dbDel");
  if (del) del.onclick = async () => {
    if (!confirm("Delete this dashboard and its widgets?")) return;
    try { await api("/dashboards/" + encodeURIComponent(dbSel), "DELETE"); dbSel = null; toast("Deleted"); render(); }
    catch (e) { toast(e.message); }
  };
}

async function viewIdentity() {
  try {
    const [settingsRes, providersRes, templatesRes, typesRes] = await Promise.all([
      api("/admin/identity-settings").catch(() => ({ settings: {} })),
      api("/admin/identity-providers").catch(() => ({ providers: [] })),
      api("/platform/identity-templates").catch(() => ({ templates: [] })),
      api("/admin/identity-provider-types").catch(() => ({ types: [] }))
    ]);
    const settings = settingsRes.settings || {};
    const providers = providersRes.providers || [];
    const templates = templatesRes.templates || [];
    const pTypes = typesRes.types || [];
    
    const password = settings.password || {};
    const mfa = settings.mfa || {};
    const session = settings.session || {};
    const login = settings.login || {};
    
    return `<div class="card">
      <h3>🔐 Identity & Authentication Configuration</h3>
      <div class="form-group">
        <label>Password Policy</label>
        <div class="grid grid-2">
          <input type="number" id="minLen" value="${password.minLength || 8}" min="6" max="64" placeholder="Min Length">
          <input type="number" id="expiryDays" value="${password.expiryDays || 0}" min="0" max="365" placeholder="Expiry Days">
        </div>
        <div style="margin-top:8px;display:flex;gap:8px;flex-wrap:wrap">
          <label class="checkbox-group"><input type="checkbox" id="reqUpper" ${password.requireUppercase ? 'checked' : ''}> Require Uppercase</label>
          <label class="checkbox-group"><input type="checkbox" id="reqNumbers" ${password.requireNumbers ? 'checked' : ''}> Require Numbers</label>
          <label class="checkbox-group"><input type="checkbox" id="reqSpecial" ${password.requireSpecialChars ? 'checked' : ''}> Require Special Chars</label>
        </div>
      </div>
      
      <div class="form-group">
        <label>Multi-Factor Authentication</label>
        <label class="checkbox-group"><input type="checkbox" id="mfaEnabled" ${mfa.enabled ? 'checked' : ''}> Enable MFA</label>
        <label class="checkbox-group"><input type="checkbox" id="mfaAdmin" ${mfa.requireForAdmin ? 'checked' : ''}> Require for Admins</label>
      </div>
      
      <div class="form-group">
        <label>Session Settings</label>
        <div class="grid grid-3">
          <input type="number" id="sessTimeout" value="${session.timeoutMinutes || 120}" min="5" max="1440" placeholder="Timeout (min)">
          <input type="number" id="sessMax" value="${session.maxConcurrent || 3}" min="1" max="10" placeholder="Max Concurrent">
          <input type="number" id="sessRemember" value="${session.rememberMeDays || 30}" min="1" max="365" placeholder="Remember Me">
        </div>
      </div>
      
      <div class="form-group">
        <label>Login Settings</label>
        <div class="grid grid-2">
          <input type="number" id="maxAttempts" value="${login.maxAttempts || 5}" min="1" max="20" placeholder="Max Attempts">
          <input type="number" id="lockout" value="${login.lockoutMinutes || 30}" min="1" max="240" placeholder="Lockout (min)">
        </div>
        <label class="checkbox-group" style="margin-top:8px"><input type="checkbox" id="guestCheckout" ${login.allowGuestCheckout ? 'checked' : ''}> Allow Guest Checkout</label>
      </div>
      
      <button class="btn" data-act="save-identity">Save Settings</button>
    </div>
    
    <div class="card" style="margin-top:16px">
      <h3>🔌 Identity Providers</h3>
      <div id="providersList" class="grid" style="grid-template-columns:1fr">
        ${providers.map(p => `
          <div class="card" style="border:1px solid var(--border-color);margin-bottom:8px">
            <div style="display:flex;justify-content:space-between;align-items:center">
              <div>
                <b>${esc(p.name)}</b>
                <span class="badge" style="margin-left:8px">${esc(p.provider_type)}</span>
                <span class="badge ${p.enabled ? 'badge-success' : ''}" style="margin-left:8px">${p.enabled ? 'Enabled' : 'Disabled'}</span>
              </div>
              <div>
                <button class="btn-icon" data-act="edit-provider" data-id="${esc(p.id)}">✎</button>
                <button class="btn-icon" style="color:var(--danger)" data-act="delete-provider" data-id="${esc(p.id)}">✕</button>
              </div>
            </div>
          </div>
        `).join('') || '<p class="alert alert-info">No providers configured. Click + Add Provider below.</p>'}
      </div>
      <button class="btn" style="margin-top:12px" data-act="add-provider">+ Add Provider</button>
    </div>
    
    <div class="card" style="margin-top:16px">
      <h3>📋 Apply Global Template</h3>
      <div class="grid grid-2">
        <select id="tmplSelect" class="form-group">
          <option value="">-- Select a template --</option>
          ${templates.map(t => `<option value="${t.id}">${esc(t.name)}${t.is_default ? ' (Default)' : ''}</option>`).join('')}
        </select>
        <select id="tmplTenant" class="form-group">
          ${P.tenants.map(t => `<option value="${t.id}">${esc(t.name)} (${esc(t.slug)})</option>`).join('')}
        </select>
      </div>
      <button class="btn btn-outline" id="applyTmplBtn">Apply template to store</button>
    </div>
    
    <div class="card" style="margin-top:16px">
      <h3>🔧 Provider Types</h3>
      <p class="p-tag">The vocabulary of authentication kinds is registry data — the flow each row names is how the login engine routes it. Add one and the Add-Provider form can use it.</p>
      ${pTypes.map(t => `
        <div class="card" style="border:1px solid var(--border-color);margin-bottom:8px">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <div><b>${esc(t.label || t.key)}</b> <span class="badge" style="margin-left:8px">${esc(t.key)}</span>${t.flow ? ` <span class="badge" style="margin-left:4px">${esc(t.flow)} flow</span>` : ""}${t.delivery ? ` <span class="badge" style="margin-left:4px">${esc(t.delivery)}</span>` : ""}</div>
            <span class="p-tag">${(t.fields || []).length} config field(s): ${(t.fields || []).map(esc).join(", ") || "—"}</span>
          </div>
        </div>
      `).join("") || '<p class="alert alert-info">No provider types registered.</p>'}
      <button class="btn" style="margin-top:12px" id="ptAddBtn">+ New provider type</button>
    </div>`;
  } catch (e) {
    return `<div class="card" style="color:var(--danger)">Error: ${esc(e.message)}</div>`;
  }
}

async function saveIdentity() {
  const body = {
    password: {
      minLength: parseInt(document.getElementById("minLen").value) || 8,
      requireUppercase: !!document.getElementById("reqUpper").checked,
      requireNumbers: !!document.getElementById("reqNumbers").checked,
      requireSpecialChars: !!document.getElementById("reqSpecial").checked,
      expiryDays: parseInt(document.getElementById("expiryDays").value) || 0
    },
    mfa: {
      enabled: !!document.getElementById("mfaEnabled").checked,
      requireForAdmin: !!document.getElementById("mfaAdmin").checked
    },
    session: {
      timeoutMinutes: parseInt(document.getElementById("sessTimeout").value) || 120,
      maxConcurrent: parseInt(document.getElementById("sessMax").value) || 3,
      rememberMeDays: parseInt(document.getElementById("sessRemember").value) || 30
    },
    login: {
      maxAttempts: parseInt(document.getElementById("maxAttempts").value) || 5,
      lockoutMinutes: parseInt(document.getElementById("lockout").value) || 30,
      allowGuestCheckout: !!document.getElementById("guestCheckout").checked
    }
  };
  try {
    await api("/admin/identity-settings", "PUT", body);
    toast("Settings saved");
    viewIdentity();
  } catch (e) {
    toast("Error: " + e.message);
  }
}

/* Apply a global identity template to a store — the target is ALWAYS an explicit tenant id
   chosen in the console (a platform store selector), never a hardcoded store. Shared by the
   Identity view's apply control and the Identity Templates view's per-row Apply action. */
async function applyIdentityTemplate(templateId, tenantId) {
  if (!templateId) return toast("Select a template");
  if (!tenantId) return toast("Select a target store");
  try {
    const r = await api(`/platform/identity-templates/${templateId}/apply`, "POST", { tenant_id: Number(tenantId) });
    toast(`Template applied to ${esc(r.slug)}${r.providers ? ` · ${r.providers} provider(s)` : ""}`);
    render();
  } catch (e) { toast("Error: " + e.message); }
}

/* the provider type list and the per-type config form are both DERIVED from the registry
   (identity-provider-types), so a type created in the Provider Types card — including its
   own config fields and the flow it routes through — is immediately selectable here with no
   second place to maintain. The types the last render fetched are cached; a caller that
   arrives cold (the button is on the same page) falls back to a fetch. */
let _idpTypes = null;
async function _providerTypes() {
  if (_idpTypes && _idpTypes.length) return _idpTypes;
  try { const r = await api("/admin/identity-provider-types"); _idpTypes = r.types || []; } catch (e) { _idpTypes = []; }
  return _idpTypes;
}
const SECRET_FIELD_RE = /secret|password|cert/i;
function _providerFieldInput(key) {
  const secret = SECRET_FIELD_RE.test(key);
  return `<div class="form-group"><label>${esc(key)}${secret ? " (sealed at rest)" : ""}</label>
    <input type="${secret ? "password" : "text"}" id="pf_${esc(key)}" placeholder="${esc(key)}"></div>`;
}
/* add — or, given an existing provider, edit — an identity provider. On edit the type is
   fixed, non-secret fields are prefilled, and a secret left blank keeps its sealed value. */
async function addProvider(existing) {
  const types = await _providerTypes();
  if (!types.length) return toast("Create a provider type first");
  let cur = {};
  if (existing) { try { cur = typeof existing.config === "string" ? JSON.parse(existing.config || "{}") : (existing.config || {}); } catch (e) { cur = {}; } }
  const modal = document.createElement("div");
  modal.className = "modal-overlay";
  modal.innerHTML = `
    <div class="modal">
      <div class="modal-header">
        <h3 class="modal-title">${existing ? "Edit" : "Add"} Identity Provider</h3>
        <button class="btn-icon" data-act="close-overlay">✕</button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label>Provider Type</label>
          <select id="provTypeAdd">
            ${types.map(t => `<option value="${esc(t.key)}">${esc(t.label || t.key)} · ${esc(t.flow || "external")} flow</option>`).join("")}
          </select>
        </div>
        <div class="form-group">
          <label>Name</label>
          <input type="text" id="provNameAdd" placeholder="e.g., Company SSO">
        </div>
        <div id="provFieldsAdd"></div>
        <div class="form-group checkbox-group">
          <input type="checkbox" id="provEnabledAdd" checked>
          <label>Enabled</label>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-outline" data-act="close-overlay">Cancel</button>
        <button class="btn" data-act="save-provider">Save</button>
      </div>
    </div>
  `;
  document.body.appendChild(modal);

  const typeSelect = modal.querySelector("#provTypeAdd");
  const fieldsDiv = modal.querySelector("#provFieldsAdd");

  const renderFields = () => {
    const type = types.find(t => t.key === typeSelect.value) || {};
    const fields = type.fields || [];
    fieldsDiv.innerHTML = fields.length
      ? fields.map(_providerFieldInput).join("")
      : `<p class="p-tag">This type takes no configuration fields.</p>`;
  };
  typeSelect.onchange = renderFields;
  if (existing) {
    typeSelect.value = existing.provider_type; typeSelect.disabled = true;
    modal.querySelector("#provNameAdd").value = existing.name || "";
    modal.querySelector("#provEnabledAdd").checked = !!existing.enabled;
  }
  renderFields();
  if (existing) for (const [k, v] of Object.entries(cur)) {
    const el = modal.querySelector("#pf_" + CSS.escape(k));
    if (el && !SECRET_FIELD_RE.test(k) && typeof v !== "object") el.value = v;
  }

  window.saveProviderAdd = async () => {
    const type = typeSelect.value;
    const name = document.getElementById("provNameAdd")?.value.trim();
    const enabled = document.getElementById("provEnabledAdd")?.checked;
    if (!name) return toast("Enter provider name");

    const config = {};
    const t = types.find(x => x.key === type) || {};
    for (const f of (t.fields || [])) {
      const el = document.getElementById("pf_" + f);
      if (el && el.value !== "") config[f] = el.value;
    }

    try {
      await api("/admin/identity-providers", "PUT", existing ? { id: existing.id, provider_type: type, name, enabled, config } : { provider_type: type, name, enabled, config });
      toast(existing ? "Provider updated" : "Provider added");
      modal.remove();
      viewIdentity();
    } catch (e) {
      toast("Error: " + e.message);
    }
  };
}
async function editProvider(id) {
  const r = await api("/admin/identity-providers").catch(() => ({ providers: [] }));
  const p = (r.providers || []).find(x => String(x.id) === String(id));
  if (!p) return toast("Provider not found");
  return addProvider(p);
}
async function deleteProvider(id) {
  if (!confirm("Delete this identity provider? Users who sign in with it will need another method.")) return;
  const r = await api("/admin/identity-providers/" + encodeURIComponent(id), "DELETE");
  if (r && r.error) return toast("Error: " + r.error);
  toast("Provider deleted");
  viewIdentity();
}
/* the identity view's buttons are wired by delegation (data-act) — inline onclick
   attributes need CSP 'unsafe-inline', which the platform no longer allows */
document.addEventListener("click", e => {
  const b = e.target.closest("[data-act]");
  if (!b) return;
  const act = b.dataset.act;
  if (act === "save-identity") saveIdentity();
  else if (act === "add-provider") addProvider();
  else if (act === "edit-provider") editProvider(b.dataset.id);
  else if (act === "delete-provider") deleteProvider(b.dataset.id);
  else if (act === "close-overlay") { const o = b.closest(".modal-overlay"); if (o) o.remove(); }
  else if (act === "save-provider") { if (window.saveProviderAdd) window.saveProviderAdd(); }
});
async function addProviderType() {
  /* the modal() helper owns the markup (the hand-rolled version's ✕ targeted a class the
     overlay never had, so it could never close). The registry shape is {key, label, fields[]};
     fields are config keys an instance of this type carries. */
  const m = modal(`<div class="p-modal-head"><h3>Create provider type</h3><button data-mclose>✕</button></div>
    <div class="p-form">
      <label><span>Key (e.g. ldap, saml)</span><input type="text" id="ptKey" placeholder="custom"></label>
      <label><span>Label (e.g. LDAP, SAML)</span><input type="text" id="ptLabel" placeholder="Custom Provider"></label>
      <label><span>Flow — how this kind proves the claim</span><select id="ptFlow">
        <option value="external">external — an authority (SSO/OIDC/directory) returns an assertion</option>
        <option value="challenge">challenge — a short-lived code (OTP, authenticator)</option>
        <option value="link">link — a passwordless link by email</option>
        <option value="biometric">biometric — a WebAuthn challenge</option>
        <option value="password">password — the native email+password</option>
      </select></label>
      <label><span>Config fields — one key per line (e.g. url, cert, ttl)</span><textarea id="ptFields" rows="4" placeholder="url&#10;cert&#10;domains"></textarea></label>
      <div class="p-err hidden" id="ptErr" style="color:var(--p-red);font-size:13px;margin:6px 0"></div>
      <button class="p-btn primary" id="ptGo">Create</button>
    </div>`);
  m.querySelector("#ptGo").onclick = async () => {
    const key = m.querySelector("#ptKey").value.trim().toLowerCase().replace(/[^a-z0-9_-]/g, "");
    const label = m.querySelector("#ptLabel").value.trim();
    const flow = m.querySelector("#ptFlow").value;
    const err = m.querySelector("#ptErr");
    if (!key || !label) { err.textContent = "Key and label are required"; err.classList.remove("hidden"); return; }
    const fields = m.querySelector("#ptFields").value.split(/[\s,]+/).map(s => s.trim()).filter(Boolean);
    try {
      await api("/admin/identity-provider-types", "POST", { key, label, flow, fields });
      _idpTypes = null;   /* the new type is pickable in the Add-Provider form immediately */
      m.innerHTML = ""; toast("Provider type created"); render();
    } catch (e) { err.textContent = e.message; err.classList.remove("hidden"); }
  };
}
/* the identity-template form's configuration fields, rendered for create AND edit so the
   two cannot drift; p is the prefix that separates the two sets of inputs */
function tmplConfigFields(p, c) {
  c = c || {};
  const pw = c.password || {}, mfa = c.mfa || {}, se = c.session || {}, lg = c.login || {};
  return `
  <h4>Password Policy</h4>
  <label><span>Min Length</span><input type="number" id="${p}PwdMin" value="${pw.minLength || 12}" min="6" max="64"></label>
  <label><span>Require Uppercase</span><input type="checkbox" id="${p}PwdUpper" ${pw.requireUppercase ? "checked" : ""}></label>
  <label><span>Require Numbers</span><input type="checkbox" id="${p}PwdNum" ${pw.requireNumbers ? "checked" : ""}></label>
  <label><span>Require Special</span><input type="checkbox" id="${p}PwdSpec" ${pw.requireSpecialChars ? "checked" : ""}></label>
  <label><span>Expiry (days)</span><input type="number" id="${p}PwdExpiry" value="${pw.expiryDays != null ? pw.expiryDays : 90}" min="0" max="365"></label>
  <h4>MFA</h4>
  <label><span>Enable MFA</span><input type="checkbox" id="${p}MfaEnabled" ${mfa.enabled ? "checked" : ""}></label>
  <label><span>Require for Admins</span><input type="checkbox" id="${p}MfaAdmin" ${mfa.requireForAdmin ? "checked" : ""}></label>
  <h4>Session</h4>
  <label><span>Timeout (minutes)</span><input type="number" id="${p}SessTimeout" value="${se.timeoutMinutes || 120}" min="5" max="1440"></label>
  <label><span>Max Concurrent</span><input type="number" id="${p}SessMax" value="${se.maxConcurrent || 3}" min="1" max="10"></label>
  <h4>Login</h4>
  <label><span>Max Attempts</span><input type="number" id="${p}LoginMax" value="${lg.maxAttempts || 5}" min="1" max="20"></label>
  <label><span>Lockout (minutes)</span><input type="number" id="${p}LoginLockout" value="${lg.lockoutMinutes || 30}" min="1" max="240"></label>`;
}
function collectTmplConfig(p) {
  return {
    password: {
      minLength: parseInt($(`#${p}PwdMin`).value) || 12,
      requireUppercase: !!$(`#${p}PwdUpper`).checked,
      requireNumbers: !!$(`#${p}PwdNum`).checked,
      requireSpecialChars: !!$(`#${p}PwdSpec`).checked,
      expiryDays: parseInt($(`#${p}PwdExpiry`).value) || 0
    },
    mfa: { enabled: !!$(`#${p}MfaEnabled`).checked, requireForAdmin: !!$(`#${p}MfaAdmin`).checked },
    session: { timeoutMinutes: parseInt($(`#${p}SessTimeout`).value) || 120, maxConcurrent: parseInt($(`#${p}SessMax`).value) || 3 },
    login: { maxAttempts: parseInt($(`#${p}LoginMax`).value) || 5, lockoutMinutes: parseInt($(`#${p}LoginLockout`).value) || 30 }
  };
}

async function viewIdentityTemplates() {
  const res = await api("/platform/identity-templates");
  /* the apply modal lists every tenant the platform operates — ensure the list is loaded
     even when the operator arrives here without visiting the tenants view first */
  if (!P.tenants.length) P.tenants = (await api("/platform/tenants")).tenants || [];
  const templates = res.templates || [];
  const rows = templates.map(t => `<tr>
      <td><b>${esc(t.name)}</b> ${t.is_default ? '<span class="badge published">★ default</span>' : ""}<div class="p-tag" style="font-size:11px">${esc(t.description || "")}</div></td>
      <td style="white-space:nowrap">
        <button class="p-btn sm primary" data-tmplapply="${t.id}">Apply →</button>
        <button class="p-btn sm" data-tmpledit="${t.id}">Edit</button>
        <button class="p-btn sm danger" data-tmpldel="${t.id}">✕</button>
      </td>
    </tr>`).join("") || '<tr><td colspan="2" class="p-empty">No templates yet — create one above.</td></tr>';
  return `<div class="p-panel"><h2>📋 Global Identity Templates</h2>
    <p class="p-tag">Centralized identity configurations. Apply one to ANY store from the table — the target store is chosen per action, never assumed.</p>
    <div class="p-form" style="max-width:520px">
      <h3>Create Template</h3>
      <label><span>Name</span><input type="text" id="tmplName" placeholder="e.g., Enterprise SSO"></label>
      <label><span>Description</span><input type="text" id="tmplDesc" placeholder="SSO + MFA + strong passwords"></label>
      <label><span>Set as default</span><input type="checkbox" id="tmplDefault"></label>
      ${tmplConfigFields("tmpl", {})}
      <button class="p-btn primary" id="tmplSave">Create Template</button>
    </div>
    <h3 style="margin-top:18px">Saved Templates</h3>
    <div class="p-tablewrap"><table class="p-table"><thead>
      <tr><th>Template</th><th>Actions</th></tr>
    </thead><tbody>${rows}</tbody></table></div>
  </div>`;
}

async function saveTemplate() {
  const name = $("#tmplName").value.trim();
  if (!name) return toast("Enter template name");
  try {
    await api("/platform/identity-templates", "POST", {
      name, description: $("#tmplDesc").value, config: collectTmplConfig("tmpl"), is_default: !!$("#tmplDefault").checked
    });
    toast("Template created");
    render();
  } catch (e) { toast("Error: " + e.message); }
}

/* real edit: the PUT route exists, so edit in place — never the old delete-and-recreate
   hack that silently discarded the template and its apply history */
async function editTemplate(id) {
  try {
    const res = await api(`/platform/identity-templates/${id}`);
    const t = res.template;
    const cfg = t.config || {};
    const m = modal(`<div class="p-modal-head"><h3>Edit · ${esc(t.name)}</h3><button data-mclose>✕</button></div>
      <div class="p-form" style="max-width:520px">
        <label><span>Name</span><input type="text" id="edName" value="${esc(t.name)}"></label>
        <label><span>Description</span><input type="text" id="edDesc" value="${esc(t.description || "")}"></label>
        <label><span>Set as default</span><input type="checkbox" id="edDefault" ${t.is_default ? "checked" : ""}></label>
        ${tmplConfigFields("ed", cfg)}
        <button class="p-btn primary" id="edSave">Save changes</button>
      </div>`);
    m.querySelector("#edSave").onclick = async () => {
      const name = m.querySelector("#edName").value.trim();
      if (!name) return toast("Name required");
      try {
        await api(`/platform/identity-templates/${id}`, "PUT", {
          name, description: m.querySelector("#edDesc").value, config: collectTmplConfig("ed"), is_default: !!m.querySelector("#edDefault").checked
        });
        m.innerHTML = ""; toast("Template updated"); render();
      } catch (e) { toast("Error: " + e.message); }
    };
  } catch (e) { toast("Error: " + e.message); }
}

async function deleteTemplate(id) {
  if (!confirm("Delete this template?")) return;
  try {
    await api(`/platform/identity-templates/${id}`, "DELETE");
    toast("Template deleted");
    render();
  } catch (e) { toast("Error: " + e.message); }
}

/* apply a template to a store: the target is an explicit per-action choice (any store the
   platform operates), so no template is ever welded to one store */
function applyTemplateModal(id) {
  const m = modal(`<div class="p-modal-head"><h3>Apply identity template</h3><button data-mclose>✕</button></div>
    <div class="p-form">
      <label><span>Target store</span>
        <select id="atTenant">${P.tenants.map(t => `<option value="${t.id}">${esc(t.name)} (${esc(t.slug)})</option>`).join("")}</select>
      </label>
      <p class="p-tag">The store's identity settings and providers are replaced by the template.</p>
      <button class="p-btn primary" id="atGo">Apply template</button>
    </div>`);
  m.querySelector("#atGo").onclick = () => { const tid = m.querySelector("#atTenant").value; m.innerHTML = ""; applyIdentityTemplate(id, tid); };
}

async function wireIdentityTemplates() {
  const save = $("#tmplSave");
  if (save) save.onclick = () => saveTemplate();
  document.querySelectorAll("[data-tmplapply]").forEach(b => b.onclick = () => applyTemplateModal(b.dataset.tmplapply));
  document.querySelectorAll("[data-tmpledit]").forEach(b => b.onclick = () => editTemplate(b.dataset.tmpledit));
  document.querySelectorAll("[data-tmpldel]").forEach(b => b.onclick = () => deleteTemplate(b.dataset.tmpldel));
}

/* ═══════════════════ PLATFORM ADMIN ACCOUNTS + ROLES ═══════════════════
   The console's own user base, each carrying a ROLE that decides what this
   console shows them and what the API accepts from them (lib/prbac.js).
   The seed creates one platform owner with full access; this view is the
   only way to add more operators and to scope what they may do.
   Mirrors the store console's Team & Roles page: a role table (data), a
   member table with an inline role picker, a create form, an edit modal
   and confirm-on-delete. Self-deletion and deleting the last admin are
   refused server-side; the UI greys them out too. */
async function vPAdmins() {
  const res = await api("/platform/admins");
  const admins = res.admins || [];
  const roles = res.roles || [];
  const me = (P.user && P.user.id) || null;
  const canWrite = !P.allowed || P.allowed.includes("*") || P.allowed.includes("padmins");
  const roleTag = a => a.role ? `<span class="badge">${esc(a.role)}</span>` : '<span class="badge published">owner</span>';
  const rows = admins.map(a => `<tr>
      <td><b>${esc(a.name)}</b> ${a.id === me ? '<span class="badge published">you</span>' : ""}</td>
      <td>${esc(a.email)}</td>
      <td>${canWrite && a.id !== me
        ? `<select data-parole="${a.id}">${roles.map(r => `<option value="${esc(r.key)}" ${a.role === r.key ? "selected" : ""}>${esc(r.name)}</option>`).join("")}</select>`
        : roleTag(a)}</td>
      <td class="p-tag">${esc(String(a.created_at || "").slice(0, 19))}</td>
      <td style="white-space:nowrap">
        <button class="p-btn sm" data-paedit="${a.id}">Edit</button>
        <button class="p-btn sm danger" data-padel="${a.id}" ${a.id === me ? "disabled title='You cannot delete your own account'" : ""}>✕</button>
      </td>
    </tr>`).join("") || '<tr><td colspan="5" class="p-empty">No platform admins.</td></tr>';
  const roleRows = roles.map(r => `<tr><td><b>${esc(r.name)}</b> <code>${esc(r.key)}</code><br><span class="p-tag">${esc(r.desc || "")}</span></td>
      <td class="p-tag">${Object.entries(r.sections || {}).map(([k, v]) => `${esc(k)}=${esc(v)}`).join(" · ")}</td></tr>`).join("");
  return `<div class="p-panel"><h2>🛡️ Platform Admins <span class="p-tag">${admins.length}</span></h2>
    <p class="p-tag">Accounts that can sign in to this console, scoped by role. The platform must always keep at least one.</p>
    <h3>Roles</h3>
    <div class="p-scroll-x"><table class="p-table"><thead><tr><th>Role</th><th>Grants (section: access)</th></tr></thead>
      <tbody>${roleRows || '<tr><td colspan="2" class="p-empty">No roles.</td></tr>'}</tbody></table></div>
    <h3 style="margin-top:18px">Administrators</h3>
    <div class="p-scroll-x"><table class="p-table"><thead>
      <tr><th>Name</th><th>Email</th><th>Role</th><th>Created</th><th>Actions</th></tr>
    </thead><tbody>${rows}</tbody></table></div>
    ${canWrite ? `<div class="p-form" style="max-width:520px;margin-top:14px">
      <h3>Add platform admin</h3>
      <label><span>Name</span><input type="text" id="paName" placeholder="Support Lead"></label>
      <label><span>Email</span><input type="email" id="paEmail" placeholder="support@luxora.shop"></label>
      <label><span>Password</span><input type="password" id="paPass" placeholder="6+ characters, letter + digit" minlength="6"></label>
      <label><span>Role</span><select id="paRole">${roles.filter(r => r.key !== "owner").map(r => `<option value="${esc(r.key)}">${esc(r.name)}</option>`).join("")}</select></label>
      <button class="p-btn primary" id="paSave">Create admin</button>
    </div>` : '<p class="p-tag">Your role is read-only here.</p>'}
  </div>`;
}
function wirePAdmins() {
  const save = $("#paSave");
  if (save) save.onclick = async () => {
    const name = $("#paName").value.trim();
    const email = $("#paEmail").value.trim();
    const password = $("#paPass").value;
    const role = $("#paRole") ? $("#paRole").value : "support";
    if (!name || !email || !password) return toast("Name, email and password are required");
    try {
      await api("/platform/admins", "POST", { name, email, password, role });
      toast("Platform admin created — they can sign in at /platform.html");
      render();
    } catch (e) { toast("Error: " + e.message); }
  };
  /* inline role change — the back-end re-checks the role exists, so a stale
     option can never write an unknown key */
  document.querySelectorAll("[data-parole]").forEach(sel => sel.onchange = async () => {
    try { await api("/platform/admins/" + sel.dataset.parole, "PUT", { role: sel.value }); toast("Role updated — effective on their next sign-in"); }
    catch (e) { toast(e.message); render(); }
  });
  document.querySelectorAll("[data-paedit]").forEach(b => b.onclick = () => editPAdmin(b.dataset.paedit));
  document.querySelectorAll("[data-padel]").forEach(b => b.onclick = () => deletePAdmin(b.dataset.padel));
}
async function editPAdmin(id) {
  try {
    const res = await api("/platform/admins");
    const admins = res.admins || [];
    const roles = res.roles || [];
    const a = admins.find(x => x.id === Number(id));
    if (!a) return toast("Admin not found");
    const m = modal(`<div class="p-modal-head"><h3>Edit · ${esc(a.name)}</h3><button data-mclose>✕</button></div>
      <div class="p-form" style="max-width:520px">
        <label><span>Name</span><input type="text" id="edName" value="${esc(a.name)}"></label>
        <label><span>Email</span><input type="email" id="edEmail" value="${esc(a.email)}"></label>
        <label><span>Role</span><select id="edRole">${roles.map(r => `<option value="${esc(r.key)}" ${(a.role || "owner") === r.key ? "selected" : ""}>${esc(r.name)}</option>`).join("")}</select></label>
        <label><span>New password <span class="p-tag">leave blank to keep</span></span><input type="password" id="edPass" placeholder="6+ characters" minlength="6"></label>
        <button class="p-btn primary" id="edSave">Save changes</button>
      </div>`);
    m.querySelector("#edSave").onclick = async () => {
      const name = m.querySelector("#edName").value.trim();
      const email = m.querySelector("#edEmail").value.trim();
      const password = m.querySelector("#edPass").value;
      const role = m.querySelector("#edRole").value;
      if (!name || !email) return toast("Name and email are required");
      try {
        await api(`/platform/admins/${id}`, "PUT", { name, email, role, password: password || undefined });
        m.innerHTML = ""; toast("Platform admin updated" + (password ? " — sessions signed out" : "")); render();
      } catch (e) { toast("Error: " + e.message); }
    };
  } catch (e) { toast("Error: " + e.message); }
}
async function deletePAdmin(id) {
  if (!confirm("Delete this platform admin? Their console sessions are revoked immediately.")) return;
  try {
    await api(`/platform/admins/${id}`, "DELETE", {});
    toast("Platform admin deleted");
    render();
  } catch (e) { toast("Error: " + e.message); }
}
/* ═══════════════════ USERS ═════════════════
   Every account across every store, read through the generic dataset reader — and
   creation. An account belongs to exactly one store, so the operator picks the store
   (the domain) and a role: a store admin's authority is a staff role from the store
   surface (rbac), a customer carries none. Writes go to the platform endpoint, which
   runs the same password policy the storefront signup enforces. */
async function vUsers() {
  await gMeta();
  const canWrite = !P.allowed || P.allowed.includes("*") || P.allowed.includes("users");
  const staff = await gFan("/api/admin/roles").catch(() => ({}));
  const srow = (staff.results || []).find(r => r.ok && r.data);
  window.__userStaffRoles = srow ? (srow.data.roles || []) : [];
  return gBar("Users", "👤", "Every account the platform holds across every store — read through the generic dataset reader.", 1)
    + (canWrite ? `<div class="p-panel" style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;padding:10px 14px">
        <button class="p-btn sm primary" data-unew="1">＋ New user</button>
        <span class="p-tag">a user belongs to one store — a store admin's authority is the staff role you assign</span>
      </div>` : "")
    + await gTable("customer");
}
function userFormModal() {
  const tenants = Object.values(G.tmap || {});
  const staffRoles = window.__userStaffRoles || [];
  const m = modal(`<div class="p-modal-head"><h3>New user</h3><button data-mclose>✕</button></div>
    <p class="p-tag">An account belongs to one store. A store admin's authority is the staff role you pick; a customer has none.</p>
    <div class="p-form" style="max-width:560px">
      <label><span>Store</span><select id="unTenant">${tenants.map(t => `<option value="${t.id}">${esc(t.name)}</option>`).join("")}</select></label>
      <div class="row">
        <label><span>Name</span><input type="text" id="unName" placeholder="Alex Rao"></label>
        <label><span>Email</span><input type="email" id="unEmail" placeholder="alex@store.shop"></label>
      </div>
      <label><span>Password <span class="p-tag">blank to generate</span></span><input type="password" id="unPw" placeholder="6+ characters, letter + digit"></label>
      <label><span>Role</span><select id="unRole"><option value="customer">Customer</option><option value="admin">Store admin</option></select></label>
      <label id="unStaffWrap"><span>Staff role</span><select id="unStaff">${/* the store surface lists owner first, but full store control is the wrong default
          for a new admin — the platform API defaults an omitted staff role to manager */ staffRoles.map(r => `<option value="${esc(r.key)}" ${r.key === "manager" ? "selected" : ""}>${esc(r.name)}</option>`).join("")}</select></label>
      <div style="display:flex;gap:8px;margin-top:4px">
        <button class="p-btn primary" id="unSave">Create user</button>
        <button class="p-btn" data-mclose>Cancel</button>
      </div>
      <div id="unGen" class="p-tag" style="margin-top:8px"></div>
    </div>`);
  const roleSel = m.querySelector("#unRole");
  const sync = () => { m.querySelector("#unStaffWrap").style.display = roleSel.value === "admin" ? "" : "none"; };
  roleSel.onchange = sync; sync();
  m.querySelector("#unSave").onclick = async () => {
    const name = m.querySelector("#unName").value.trim();
    const email = m.querySelector("#unEmail").value.trim();
    if (!name || !email) return toast("Name and email are required");
    const payload = { tenant_id: m.querySelector("#unTenant").value, name, email,
      password: m.querySelector("#unPw").value || undefined, role: roleSel.value };
    if (roleSel.value === "admin") payload.staff_role = m.querySelector("#unStaff").value;
    try {
      const r = await api("/platform/users", "POST", payload);
      /* a generated password is shown once and the modal stays open so the operator can
         copy it — the table behind has already refreshed */
      if (r.generated) { m.querySelector("#unGen").textContent = "generated password: " + r.generated; toast("User created — copy the password, it is shown once"); }
      else { m.innerHTML = ""; toast("User created"); }
      render();
    } catch (e) { toast(e.message); }
  };
}
function wireUsers() {
  const b = document.querySelector("[data-unew]");
  if (b) b.onclick = () => userFormModal();
}
/* ═══════════════════ ROLES ═════════════════
   The platform's two live role sets — both DATA in meta_lists, never code. The
   platform console's own operators are scoped by platformRoles (lib/prbac.js);
   every store's staff are scoped by staffRoles (lib/rbac.js). The corpus's "Role"
   universe is a declaration artefact (uv_role); THIS leaf is where the roles
   actually in force are read AND defined — creating a role, describing it and
   scoping its rights per section, platform-wide or for every store's domain,
   without a deploy. */
const GRANT_OPTS = [["", "inherit"], ["off", "off"], ["read", "read"], ["write", "write"]];

/* ╔════════════════════════════════════════════════════════════════════╗
   ║  PLATFORM REGISTRIES — every vocabulary, auto-discovered             ║
   ╚════════════════════════════════════════════════════════════════════╝
   The list of lists is fetched from the API, never hardcoded, so a registry
   created by any engine (or a future seed) is authorable here the moment it
   exists. Adding a platform mode here is what makes "register an Uber-like
   platform" a data change: the registration walk, every form select and every
   engine read the same rows on the next request.

   AUTO-RECOMMEND: an entry's fields are scaffolded from the live entries'
   own shape — the API infers the keys and their types from the data, so the
   authoring form never depends on a schema written in code.
   AUTO-UPGRADE: a row an operator has edited is marked operator-owned; a
   corpus upgrade only ADDS canonical entries the list lacks, never reverts an
   edit (lib/registry.js mergeDefaults).                                        */
async function vRegistries() {
  const { registries } = await api("/platform/registries");
  const rows = (registries || []).map(r => `<tr>
      <td><b>${esc(r.label)}</b> <code style="font-size:10px">${esc(r.name)}</code></td>
      <td class="num">${r.count}</td>
      <td>${r.edited ? '<span class="a-chip">operator-owned</span>' : '<span class="a-chip" style="opacity:.55">seeded floor</span>'}</td>
      <td><code style="font-size:10px">${esc(r.seeded_from || "—")}</code></td>
      <td style="white-space:nowrap"><button class="p-btn sm primary" data-regopen="${esc(r.name)}">Edit entries</button></td>
    </tr>`).join("") || '<tr><td colspan="5" class="p-empty">No registries discovered yet.</td></tr>';
  return `<div class="p-panel"><h2>📚 Platform Registries</h2>
    <p class="p-tag">Every vocabulary the platform reads — platform modes, industries, statuses, roles, provider kinds — is a <code>meta_lists</code> row discovered from the table itself. Add an entry and the registration walk, every form select and every engine obey it on the next request. Deleting an entry a platform still uses is refused with the platform(s) holding it.</p>
    <div class="p-scroll-x"><table class="p-table"><thead><tr><th>Registry</th><th class="num">Entries</th><th>Ownership</th><th>Seeded from</th><th></th></tr></thead>
    <tbody>${rows}</tbody></table></div></div>`;
}
/* the entry editor for one registry: items as rows, add/edit/delete. The add/edit form is
   scaffolded from the registry's recommended entry (its inferred shape), so a list whose
   shape changes in the data is reflected here without a code change. */
async function registryEditor(name) {
  const enc = encodeURIComponent(name);
  const [{ items }, rec] = await Promise.all([
    api("/platform/registries/" + enc),
    api("/platform/registries/" + enc + "/recommend", "POST", { label: "" }).catch(() => ({ item: {} }))
  ]);
  const shape = (rec && rec.item) || {};
  const keys = Object.keys(shape);
  const cell = v => Array.isArray(v) ? "[" + v.length + "]"
    : (v && typeof v === "object") ? "{…}"
    : String(v == null ? "" : v).slice(0, 60);
  const itemRows = (items || []).map((it, i) => {
    const obj = it && typeof it === "object" ? it : { key: String(it) };
    return `<tr><td><b>${esc(String(obj.key != null ? obj.key : ""))}</b></td>
      <td>${keys.filter(k => k !== "key").map(k => `<span class="p-tag" style="margin-right:4px">${esc(k)}: ${esc(cell(obj[k]))}</span>`).join("") || '<span class="p-tag">—</span>'}</td>
      <td style="white-space:nowrap">
        <button class="p-btn sm" data-regedit="${i}">Edit</button>
        <button class="p-btn sm danger" data-regdel="${esc(String(obj.key != null ? obj.key : ""))}">✕</button></td></tr>`;
  }).join("") || '<tr><td colspan="3" class="p-empty">No entries yet — add the first below.</td></tr>';
  const m = modal(`<div class="p-modal-head"><h3>📚 ${esc(name)}</h3><button data-mclose>✕</button></div>
    <div class="p-scroll-x" style="max-height:46vh;overflow:auto;margin-bottom:12px"><table class="p-table"><thead><tr><th>Key</th><th>Fields</th><th></th></tr></thead>
      <tbody id="regRows">${itemRows}</tbody></table></div>
    <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
      <button class="p-btn primary sm" id="regAdd">＋ Add entry</button>
      <span class="p-tag">${(items || []).length} entries · form scaffolded from the live shape (${keys.length} fields)</span></div>`);
  const refreshRows = () => { /* re-render rows after a save/delete without reopening */
    api("/platform/registries/" + enc).then(({ items: its }) => {
      m.querySelector("#regRows").innerHTML = (its || []).map((it, i) => {
        const obj = it && typeof it === "object" ? it : { key: String(it) };
        return `<tr><td><b>${esc(String(obj.key != null ? obj.key : ""))}</b></td>
          <td>${keys.filter(k => k !== "key").map(k => `<span class="p-tag" style="margin-right:4px">${esc(k)}: ${esc(cell(obj[k]))}</span>`).join("") || '<span class="p-tag">—</span>'}</td>
          <td style="white-space:nowrap">
            <button class="p-btn sm" data-regedit="${i}">Edit</button>
            <button class="p-btn sm danger" data-regdel="${esc(String(obj.key != null ? obj.key : ""))}">✕</button></td></tr>`;
      }).join("") || '<tr><td colspan="3" class="p-empty">No entries yet — add the first below.</td></tr>';
      wireRows();
    }).catch(() => { });
  };
  const entryForm = prefill => {
    /* a nested overlay with its own container: modal() reuses the single #modal element,
       so this form must not touch it — the editor underneath stays open and restores on close */
    const f = document.createElement("div");
    f.className = "p-modal";
    f.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:1100;display:flex;align-items:center;justify-content:center;padding:16px";
    f.innerHTML = `<div class="p-modal-box" style="max-width:560px;max-height:86vh;overflow:auto">
      <div class="p-modal-head"><h3>${prefill ? "Edit" : "Add"} · ${esc(name)}</h3><button data-rfclose>✕</button></div>
      <div class="p-form">
      ${keys.map(k => `<label><span>${esc(k)} ${k === "key" ? "*" : ""}</span>
        <input data-rf="${esc(k)}" value="${esc(String(prefill && prefill[k] != null ? (typeof prefill[k] === "object" ? JSON.stringify(prefill[k]) : prefill[k]) : (shape[k] != null ? shape[k] : "")))}"
        ${k === "key" && prefill ? "disabled" : ""} placeholder="${k === "key" ? "snake_case_key" : ""}"></label>`).join("")}
      ${keys.length ? "" : '<p class="p-tag">This registry has no items yet — a key and name are a good start.</p>'}
      <label><span>Reset all fields from a label (auto-recommend)</span>
        <span style="display:flex;gap:6px"><input id="rfLabel" placeholder="Hybrid Marketplace" style="flex:1">
        <button class="p-btn sm" id="rfRec" type="button">✨ Recommend</button></span></label>
      </div>
      <div style="display:flex;gap:8px;margin-top:12px"><button class="p-btn primary" id="rfSave">${prefill ? "Save changes" : "Add entry"}</button></div></div>`;
    document.body.appendChild(f);
    const close = () => { try { document.body.removeChild(f); } catch (e) { } };
    f.addEventListener("click", e => { if (e.target === f) close(); });
    f.querySelector("[data-rfclose]").onclick = close;
    f.querySelector("#rfRec").onclick = async () => {
      const label = f.querySelector("#rfLabel").value.trim();
      const { item } = await api("/platform/registries/" + enc + "/recommend", "POST", { label });
      if (item) for (const k of keys) {
        const el = f.querySelector(`[data-rf="${esc(k)}"]`);
        if (el && !el.disabled && item[k] != null) el.value = typeof item[k] === "object" ? JSON.stringify(item[k]) : item[k];
      }
    };
    f.querySelector("#rfSave").onclick = async () => {
      const item = {};
      for (const k of keys) {
        const el = f.querySelector(`[data-rf="${esc(k)}"]`);
        let v = el ? el.value : "";
        if (shape[k] === "number") v = v === "" ? 0 : Number(v);
        else if (shape[k] === "boolean") v = /^(1|true|yes|on)$/i.test(v);
        else if (shape[k] === "array" || shape[k] === "object") { try { v = JSON.parse(v); } catch (e) { v = shape[k] === "array" ? [] : {}; } }
        item[k] = v;
      }
      if (!item.key) return toast("An entry needs a key");
      const r = await api("/platform/registries/" + enc, "POST", { item });
      if (r.error) return toast(r.error);
      close();
      toast("Entry saved · " + item.key);
      refreshRows();
    };
  };
  const wireRows = () => {
    m.querySelectorAll("[data-regdel]").forEach(b => b.onclick = async () => {
      const r = await api("/platform/registries/" + enc + "/" + encodeURIComponent(b.dataset.regdel), "DELETE", {});
      if (r.error) return toast(r.error);
      toast("Entry removed");
      refreshRows();
    });
    m.querySelectorAll("[data-regedit]").forEach(b => b.onclick = () => {
      const it = (items || [])[Number(b.dataset.regedit)];
      entryForm(it && typeof it === "object" ? it : { key: String(it) });
    });
  };
  wireRows();
  m.querySelector("#regAdd").onclick = () => entryForm(null);
}

async function vRoles() {
  await gMeta();
  const [plat, staff] = await Promise.all([
    api("/platform/roles").catch(() => ({})),
    gFan("/api/admin/roles")
  ]);
  const proles = plat.roles || [];
  const psections = plat.sections || [];
  /* staff roles are one platform-wide list, so the fan-out returns a copy per store —
     dedupe by key, and take the section list from any store's copy (they are identical);
     the store count is carried as the honest note that a role applies everywhere, not
     that it exists many times */
  const srows = (staff.results || []).filter(r => r.ok && r.data);
  const ssections = srows.length ? (srows[0].data.sections || []) : [];
  const seen = new Map();
  for (const r of srows) for (const ro of (r.data.roles || []))
    if (!seen.has(ro.key)) seen.set(ro.key, { ...ro, stores: srows.length });
  const sroles = [...seen.values()];
  /* stash the loaded sets for wireRoles — the editor needs the section list and the
     role being edited, and the console re-fetches on every render, never holds a
     second source of truth beyond the DOM's own lifetime */
  window.__roleSections = { platform: psections, staff: ssections };
  window.__roleRoles = { platform: proles, staff: sroles };
  const canWrite = !P.allowed || P.allowed.includes("*") || P.allowed.includes("roles");
  const grants = r => Object.entries(r.sections || {}).map(([k, v]) => `${esc(k)}=${esc(v)}`).join(" · ") || "—";
  const table = (roles, scope) => roles.length
    ? `<div class="p-scroll-x"><table class="p-table"><thead><tr><th>Role</th><th>Key</th><th>Grants (section: access)</th>${canWrite ? "<th></th>" : ""}</tr></thead>
      <tbody>${roles.map(r => `<tr><td><b>${esc(r.name)}</b><br><span class="p-tag">${esc(r.desc || "")}</span></td>
        <td><code>${esc(r.key)}</code></td><td class="p-tag">${grants(r)}</td>
        ${canWrite ? `<td style="white-space:nowrap"><button class="p-btn sm" data-redt="${scope}" data-rekey="${esc(r.key)}">Edit</button>
          <button class="p-btn sm danger" data-rdel="${scope}" data-rekey="${esc(r.key)}">✕</button></td>` : ""}</tr>`).join("")}</tbody></table></div>`
    : `<div class="p-empty">No roles in scope.</div>`;
  const newBtn = scope => canWrite
    ? `<button class="p-btn sm primary" data-rnew="${scope}" style="margin-left:8px">＋ New role</button>` : "";
  return gBar("Roles", "🎭", "Both role sets the platform enforces — data in meta_lists, re-scopable without code. Platform roles govern this console's operators; staff roles govern every store's team.", 2)
    + `<div class="p-cards">
      <div class="p-stat"><em>Platform roles</em><b>${stat2(proles.length)}</b><small>this console's operators</small></div>
      <div class="p-stat"><em>Staff roles</em><b>${stat2(sroles.length)}</b><small>in force on ${sroles.length ? sroles[0].stores : 0} stores</small></div>
    </div>
    <div class="p-panel"><h2>🛡️ Platform roles <span class="p-tag">${proles.length}</span>${newBtn("platform")}
      <p class="p-tag">Roles a platform admin may carry — platform-wide (lib/prbac.js · meta_lists 'platformRoles').</p></h2>
      ${table(proles, "platform")}</div>
    <div class="p-panel"><h2>🏪 Store staff roles <span class="p-tag">${sroles.length}</span>${newBtn("staff")}
      <p class="p-tag">Roles a store admin may carry — one set, applied by every store's domain (lib/rbac.js · meta_lists 'staffRoles').</p></h2>
      ${table(sroles, "staff")}</div>`;
}
/* the grant editor: one control per section the scope knows. A grant is one of
   inherit (absent from the map — falls back to the wildcard), off (false, an explicit
   deny that beats the wildcard), read or write. The wildcard row sets the default every
   inherited section resolves to. A scope may carry ~200 sections, so the grid scrolls
   and a filter plus bulk-set narrow it to the ones an operator is actually scoping. */
function grantsEditor(sections, role) {
  const secs = (role && role.sections) || {};
  const wild = "*" in secs ? String(secs["*"]) : "";
  const row = (k, label) => {
    const v = k in secs ? String(secs[k]) : "";
    const cur = GRANT_OPTS.some(o => o[0] === v) ? v : "off";
    return `<label class="p-grant"><span>${esc(label || k)}</span>
      <select data-sec="${esc(k)}">${GRANT_OPTS.map(o => `<option value="${o[0]}" ${cur === o[0] ? "selected" : ""}>${o[1]}</option>`).join("")}</select></label>`;
  };
  return `<div style="display:flex;gap:8px;flex-wrap:wrap;align-items:end;margin-bottom:10px">
      <label><span>Everything (wildcard)</span><select id="grWild">${GRANT_OPTS.map(o => `<option value="${o[0]}" ${wild === o[0] ? "selected" : ""}>${o[1]}</option>`).join("")}</select></label>
      <input class="p-search" id="grFilter" placeholder="Filter sections…" style="flex:1;min-width:180px">
      <button class="p-btn sm" data-grbulk="read">filtered → read</button>
      <button class="p-btn sm" data-grbulk="write">filtered → write</button>
      <button class="p-btn sm" data-grbulk="">filtered → inherit</button>
    </div>
    <div id="grGrid" class="p-scroll-y" style="max-height:340px;display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:6px 14px;padding:4px">
      ${sections.map(k => row(k)).join("")}
    </div>`;
}
/* read the editor's DOM back into a grant map; 'inherit' is absent by design, so a
   cleared grant leaves the map and the wildcard (or nothing) decides it */
function grantsRead(m) {
  const secs = {};
  const w = m.querySelector("#grWild");
  if (w && w.value) secs["*"] = w.value;
  m.querySelectorAll("[data-sec]").forEach(sel => {
    const k = sel.dataset.sec;
    if (!k) return;
    if (sel.value === "off") secs[k] = false;
    else if (sel.value) secs[k] = sel.value;
  });
  return secs;
}
function roleFormModal(scope, sections, role) {
  const isNew = !role;
  const legend = scope === "platform"
    ? "Platform roles govern this console's own operators (platform-wide)."
    : "Staff roles govern every store's team — one set applied on every store's domain.";
  const m = modal(`<div class="p-modal-head"><h3>${isNew ? "New" : "Edit"} · ${scope === "platform" ? "platform" : "store staff"} role</h3><button data-mclose>✕</button></div>
    <p class="p-tag">${esc(legend)}</p>
    <div class="p-form" style="max-width:560px">
      <label><span>Name</span><input type="text" id="rfName" value="${esc(role ? role.name : "")}" placeholder="Order Desk"></label>
      ${isNew ? `<label><span>Key <span class="p-tag">a-z 0-9 _ -</span></span><input type="text" id="rfKey" placeholder="order_desk"></label>` : ""}
      <label><span>Description</span><input type="text" id="rfDesc" value="${esc(role ? role.desc || "" : "")}" placeholder="What this role may do"></label>
      <h4 style="margin:10px 0 4px">Rights by section</h4>
      ${grantsEditor(sections, role)}
      <div style="display:flex;gap:8px;margin-top:14px">
        <button class="p-btn primary" id="rfSave">${isNew ? "Create role" : "Save changes"}</button>
        <button class="p-btn" data-mclose>Cancel</button>
      </div>
    </div>`);
  const grid = m.querySelector("#grGrid");
  const filter = m.querySelector("#grFilter");
  filter.oninput = () => {
    const q = filter.value.toLowerCase();
    [...grid.querySelectorAll(".p-grant")].forEach(l => {
      const k = l.querySelector("span").textContent.toLowerCase();
      l.style.display = k.includes(q) ? "" : "none";
    });
  };
  m.querySelectorAll("[data-grbulk]").forEach(b => b.onclick = () => {
    const v = b.dataset.grbulk;
    [...grid.querySelectorAll(".p-grant")].forEach(l => { if (l.style.display !== "none") { const s = l.querySelector("select"); s.value = v; } });
  });
  if (isNew) m.querySelector("#rfKey").value = (m.querySelector("#rfName").value || "").toLowerCase().replace(/[^a-z0-9_-]+/g, "_").replace(/^_|_$/g, "");
  /* derive the key from the name as the operator types it, only while untouched — an
     edited key is an operator's explicit choice and is never overwritten */
  if (isNew) {
    let keyTouched = false;
    const nameEl = m.querySelector("#rfName"), keyEl = m.querySelector("#rfKey");
    keyEl.oninput = () => { keyTouched = true; };
    nameEl.oninput = () => { if (keyTouched) return; keyEl.value = nameEl.value.toLowerCase().replace(/[^a-z0-9_-]+/g, "_").replace(/^_|_$/g, ""); };
  }
  m.querySelector("#rfSave").onclick = async () => {
    const name = m.querySelector("#rfName").value.trim();
    const key = isNew ? m.querySelector("#rfKey").value.trim() : role.key;
    if (!name) return toast("A role name is required");
    if (!/^[a-z][a-z0-9_-]{1,30}$/.test(key)) return toast("Key must be 2-31 chars, start with a letter, a-z 0-9 _ -");
    const body = { key, name, desc: m.querySelector("#rfDesc").value.trim(), sections: grantsRead(m) };
    try {
      const path = scope === "platform" ? "/platform/roles" : "/platform/roles/staff";
      await api(path, "POST", body);
      toast((isNew ? "Role created" : "Role updated") + " — effective on the next sign-in");
      m.innerHTML = ""; render();
    } catch (e) { toast(e.message); }
  };
}
function wireRoles() {
  document.querySelectorAll("[data-rnew]").forEach(b => b.onclick = () => {
    const scope = b.dataset.rnew;
    const sections = scope === "platform" ? (window.__roleSections || {}).platform || [] : (window.__roleSections || {}).staff || [];
    roleFormModal(scope, sections, null);
  });
  document.querySelectorAll("[data-redt]").forEach(b => b.onclick = () => {
    const scope = b.dataset.redt, key = b.dataset.rekey;
    const list = scope === "platform" ? (window.__roleRoles || {}).platform || [] : (window.__roleRoles || {}).staff || [];
    const role = list.find(r => r.key === key);
    if (!role) return toast("Role no longer exists — refresh");
    const sections = scope === "platform" ? (window.__roleSections || {}).platform || [] : (window.__roleSections || {}).staff || [];
    roleFormModal(scope, sections, role);
  });
  document.querySelectorAll("[data-rdel]").forEach(b => b.onclick = async () => {
    const scope = b.dataset.rdel, key = b.dataset.rekey;
    if (!confirm(`Delete the role '${key}'? ` + (scope === "platform"
      ? "Operators holding it fall back to owner (full access)."
      : "Staff holding it fall back to owner (full access)."))) return;
    const path = scope === "platform" ? `/platform/roles/${encodeURIComponent(key)}` : `/platform/roles/staff/${encodeURIComponent(key)}`;
    try { await api(path, "DELETE", {}); toast("Role deleted"); render(); }
    catch (e) { toast(e.message); }
  });
}
async function wireIdentity() {
  /* the Identity view's apply control: template + explicit target store, wired (not inline) */
  const btn = $("#applyTmplBtn");
  if (btn) btn.onclick = () => applyIdentityTemplate($("#tmplSelect").value, $("#tmplTenant").value);
}
