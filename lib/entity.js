/* LUXORA Platform - Universal Entity Meta Model.
   Every entity (built-in or custom) is described as data: fields, types, validation,
   permissions, list/form rendering hints. The generic engine below performs CRUD,
   validation, tenant scoping and auditing for ALL of them - zero per-entity code. */
"use strict";

const crypto = require("crypto");
const { run, get, all } = require("./db.js");

/* field types: text | textarea | number | money | bool | date | select | multi | json | secret | ref:<entity> | readonly */
const F = (key, label, type, o) => ({ key, label, type, ...(o || {}) });

const ENTITY_DEFS = {
  country: {
    table: "countries", noTenant: true, pk: "code", pkType: "text", label: "Countries", icon: "🌍", perm: { read: ["platform"], write: ["platform"] }, platformOnly: true,
    fields: [F("code", "Code", "text", { required: true, list: true, upper: true }), F("name", "Name", "text", { required: true, list: true }),
    F("currency", "Currency", "text", { required: true, list: true, upper: true }), F("symbol", "Symbol", "text", { required: true, list: true }),
    F("locale", "Locale", "text", { required: true, list: true }), F("decimals", "Decimals", "number", { list: true }),
    F("position", "Position", "number")]
  },
  subdivision: {
    table: "subdivisions", noTenant: true, pk: "code", pkType: "text", label: "States / Provinces", icon: "🗺️", perm: { read: ["platform"], write: ["platform"] }, platformOnly: true,
    /* a subdivision is a child of the COUNTRY master, never a child of a store. It is
       platform-level master data (the same noTenant/platformOnly pair countries, currencies
       and the uv_* universes carry) so it is created once and reused by every store, service
       and ERP that needs a jurisdiction — the master itself never gains a tenant_id. A store
       ATTACHES to it by resolving its jurisdiction (settings/checkout/tax), never by owning a
       row. See lib/registry.js reconcileSubdivisions: adding a country materialises its
       states/provinces automatically, at write time and on every boot. */
    fields: [F("code", "Code", "text", { required: true, list: true, upper: true }),
    F("country_code", "Country", "ref:country", { required: true, list: true }),
    F("name", "Name", "text", { required: true, list: true }),
    F("level", "Level", "text", { list: true, hint: "state / province / region / county / prefecture / emirate / territory / district" }),
    F("parent_id", "Parent Division", "ref:subdivision", { hint: "blank = directly under the country; the tree is unbounded (state → province → district)" }),
    F("position", "Position", "number"), F("active", "Active", "bool", { list: true })]
  },
  currency: {
    table: "currencies", noTenant: true, pk: "code", pkType: "text", label: "Currencies", icon: "💱", perm: { read: ["platform"], write: ["platform"] }, platformOnly: true,
    fields: [F("code", "Code", "text", { required: true, list: true, upper: true }), F("name", "Name", "text", { required: true, list: true }),
    F("symbol", "Symbol", "text", { required: true, list: true }), F("decimals", "Decimals", "number", { required: true, list: true }),
    F("usd", "Value in USD (1 unit = x USD)", "number", { required: true, list: true }), F("position", "Position", "number"), F("active", "Active", "bool")]
  },
  module: {
    table: "modules", noTenant: true, pk: "id", pkType: "text", label: "Marketplace Modules", icon: "🧩", perm: { read: ["platform"], write: ["platform"] }, platformOnly: true,
    fields: [F("id", "ID", "text", { required: true, list: true, upper: true }), F("name", "Name", "text", { required: true, list: true }),
    F("category", "Category", "text", { list: true }), F("summary", "Summary", "textarea"), F("price_type", "Price type", "select", { options: ["free", "one_time", "monthly"] }),
    F("price", "Price (USD)", "number", { list: true }), F("version", "Version", "text"), F("vendor", "Vendor", "text"),
    F("manifest", "Manifest", "json"), F("status", "Status", "select", { options: ["active", "retired"] }), F("position", "Position", "number")]
  },
  tenant_module: {
    table: "tenant_modules", noTenant: true, pk: "module_id", pk2: "tenant_id", pkType: "text", composite: true, label: "Module Installs", icon: "🔌", perm: { read: ["platform"], write: ["platform"] }, platformOnly: true,
    fields: [F("module_id", "Module", "text", { required: true, list: true }), F("tenant_id", "Store", "ref:tenant", { required: true, list: true }),
    F("status", "Status", "select", { options: ["installed", "disabled"] }), F("config", "Config", "json")]
  },
/* Universal Dashboard & Reporting Engine (Architecture1 §394/§395): a dashboard is a
   runtime object — Identity/Audience/Widgets/Metrics/Filters — stored as entity data, so
   CRUD, validation and forms arrive from this declaration and the engine in
   lib/dashboards.js computes metrics generically. No per-dashboard code anywhere. */
  dashboard: {
    table: "dashboards", pk: "id", label: "Dashboards", icon: "📊", perm: { read: ["admin", "platform"], write: ["admin", "platform"] },
    fields: [
      F("key", "Key", "text", { required: true, list: true }),
      F("name", "Name", "text", { required: true, list: true }),
      F("type", "Type", "select", { options: "dashboardTypes", list: true }),
      F("audience", "Audience", "select", { options: ["admin", "platform", "all"], list: true }),
      F("description", "Description", "textarea"),
      F("active", "Active", "bool", { list: true }),
      F("position", "Position", "number")
    ]
  },
  dashboard_widget: {
    table: "dashboard_widgets", pk: "id", label: "Dashboard Widgets", icon: "🧩", perm: { read: ["admin", "platform"], write: ["admin", "platform"] },
    fields: [
      F("dashboard_id", "Dashboard", "number", { required: true, list: true }),
      F("kind", "Visualization", "select", { options: ["kpi", "table", "bar", "line", "donut", "text"], required: true, list: true }),
      F("label", "Label", "text", { required: true, list: true }),
      F("entity", "Entity", "text", { required: true, list: true, hint: "any entity key, e.g. orders" }),
      F("metric", "Metric", "select", { options: ["count", "sum", "avg", "min", "max", "distinct"], list: true }),
      F("column", "Column", "text", { hint: "column for sum/avg/min/max/distinct" }),
      F("dimension", "Group by", "text", { hint: "column to break the metric down by" }),
      F("ord", "Order", "select", { options: ["desc", "asc"] }),
      F("lim", "Limit", "number"),
      F("filter", "Filters", "json", { hint: "{\"field\": \"value\"}" }),
      F("position", "Position", "number"),
      F("span", "Span (1-6)", "number")
    ]
  },
  report: {
    table: "reports", pk: "id", label: "Reports", icon: "📄", perm: { read: ["admin", "platform"], write: ["admin", "platform"] },
    fields: [
      F("key", "Key", "text", { required: true, list: true }),
      F("name", "Name", "text", { required: true, list: true }),
      F("kind", "Kind", "select", { options: ["scheduled", "event", "regulatory", "operational", "executive", "ai"], required: true, list: true }),
      F("entity", "Entity", "text", { required: true, list: true }),
      F("metrics", "Metrics", "json", { hint: "[{\"metric\":\"sum\",\"column\":\"total\",\"alias\":\"revenue\"}]" }),
      F("dimensions", "Dimensions", "json", { hint: "[\"status\"]" }),
      F("filter", "Filters", "json"),
      F("schedule", "Schedule", "select", { options: ["manual", "daily", "weekly", "monthly"], list: true }),
      F("format", "Format", "select", { options: ["table", "csv", "json"], list: true }),
      F("active", "Active", "bool", { list: true }),
      F("last_run", "Last Run", "date", { readonly: true, list: true }),
      F("position", "Position", "number")
    ]
  },
  meta_list: {
    table: "meta_lists", noTenant: true, pk: "name", pkType: "text", label: "Registries (lists)", icon: "📚", perm: { read: ["platform"], write: ["platform"] }, platformOnly: true,
    /* an operator edit to a registry list is stamped `edited=1`, which every revisioned
       seed (rb_v2 / reg_v1 / cap_v2…) reads as "the operator owns this row — never
       clobber it". Without the stamp the self-heal would silently revert console edits. */
    editedStamp: true,
    fields: [F("name", "Name", "text", { required: true, list: true }), F("label", "Label", "text"), F("items", "Items (JSON)", "json", { required: true })]
  },
  compliance_control: {
    table: "compliance_controls", pk: "id", label: "Compliance Controls", icon: "🛡️", perm: { read: ["platform"], write: ["platform"] },
    fields: [F("regulation", "Regulation", "select", { options: "regulations", required: true, list: true }),
    F("control_id", "Control", "text", { required: true, list: true }), F("name", "Control name", "text", { list: true }),
    F("evidence", "Evidence", "text", { list: true }), F("status", "Status", "select", { options: "controlStatuses", required: true, list: true })]
  },
  consent: {
    table: "consents", pk: "id", label: "Consent Ledger", icon: "🔐", perm: { read: ["admin", "platform"], write: ["admin", "platform"] },
    fields: [F("subject", "Subject", "text", { required: true, list: true }), F("purpose", "Purpose", "select", { options: "privacyPurposes", required: true, list: true }),
    F("status", "Status", "select", { options: ["granted", "withdrawn", "denied"], required: true, list: true }),
    F("lawful_basis", "Lawful basis", "text", { list: true }), F("source", "Source", "text"), F("granted_at", "Granted", "date", { readonly: true, list: true }), F("withdrawn_at", "Withdrawn", "date", { readonly: true })]
  },
  privacy_request: {
    table: "privacy_requests", pk: "id", pkType: "text", label: "Privacy Requests (DSR)", icon: "📨", perm: { read: ["admin", "platform"], write: ["admin", "platform"] },
    fields: [F("id", "Request ID", "text", { required: true, list: true }), F("subject", "Subject", "text", { required: true, list: true }),
    F("kind", "Kind", "select", { options: "privacyRequestKinds", required: true, list: true }),
    F("status", "Status", "select", { options: "privacyRequestStates", required: true, list: true }), F("due_at", "Due", "date", { list: true }), F("fulfilled_at", "Fulfilled", "date", { readonly: true })]
  },
  erasure_log: {
    table: "erasure_log", pk: "id", label: "Erasure Log", icon: "🧽", perm: { read: ["platform"], write: ["platform"] },
    fields: [F("subject", "Subject", "text", { required: true, list: true }), F("removed", "Removed (JSON)", "json", { list: true }), F("executed_by", "Executed by", "text", { list: true })]
  },
  tax_mode: {
    table: "tax_modes", noTenant: true, pk: "key", pkType: "text", label: "Tax Modes", icon: "🧾", perm: { read: ["platform"], write: ["platform"] }, platformOnly: true,
    fields: [F("key", "Key", "text", { required: true, list: true }), F("label", "Label", "text", { required: true, list: true }),
    F("description", "Description", "text"), F("fields", "Extra Fields", "json"), F("position", "Position", "number")]
  },
  tax_rule: {
    table: "tax_rules", noTenant: true, pk: "country", pkType: "text", label: "Tax Rules (by Country)", icon: "💸", perm: { read: ["platform"], write: ["platform"] }, platformOnly: true,
    /* TAX OWNS TAX. A jurisdiction's rates are the tax engine's own master data — one row per
       country — not columns on the country master. This entity is the single source of truth the
       checkout, invoicing and the storefront label all resolve (lib/tax.js ruleFor); a country
       master carries no tax facts, so there is no second copy to drift against. Seeded from the
       engine's registry and re-asserted only where nobody has edited it. */
    fields: [F("country", "Country", "ref:country", { required: true, list: true }),
    F("mode", "Mode", "ref:tax_mode", { required: true, list: true }),
    F("standard", "Standard rate", "number", { required: true, list: true }),
    F("reduced", "Reduced rate", "number"), F("digital", "Digital rate", "number"),
    F("zero", "Zero rate", "number"), F("note", "Note", "textarea")]
  },
  provider_def: {
    table: "provider_defs", noTenant: true, pk: "id", pk2: "kind", composite: true, label: "Provider Catalog", icon: "🔌", perm: { read: ["platform"], write: ["platform"] }, platformOnly: true,
    fields: [F("id", "ID", "text", { required: true, list: true }), F("kind", "Kind", "select", { options: "providerKinds", required: true, list: true }),
    F("name", "Name", "text", { required: true, list: true }), F("emoji", "Icon", "text"), F("description", "Description", "text", { list: true }),
    F("methods", "Methods", "json"), F("fee_pct", "Fee %", "number", { list: true }), F("fee_fixed", "Fixed Fee", "number"),
    F("fields", "Credential Fields", "json"), F("base_fee", "Base Fee (ship)", "number"), F("eta_min", "ETA min", "number"), F("eta_max", "ETA max", "number"),
    F("position", "Position", "number"), F("enabled", "Enabled", "bool")]
  },
  provider_availability: {
    table: "provider_availability", noTenant: true, pk: "provider_id", pk2: "country_code", pkType: "text", composite: true, label: "Provider × Country", icon: "🗺️", perm: { read: ["platform"], write: ["platform"] }, platformOnly: true,
    fields: [F("provider_id", "Provider", "text", { required: true, list: true }), F("country_code", "Country", "ref:country", { required: true, list: true })]
  },
  product: {
    table: "products", pk: "id", pkType: "text", label: "Products", icon: "📦", perm: { read: ["admin", "platform"], write: ["admin"] }, sec: 'P2',
    fields: [
      F("uid", "Universal ID", "text", { readonly: true, list: true }),
      F("id", "Reference", "text", { readonly: true, list: true }), F("title", "Title", "text", { required: true, list: true }),
      F("brand", "Brand", "ref:brand", { required: true, list: true }), F("dept", "Department", "ref:department", { list: true }),
      F("type", "Product Type", "select", { options: "productTypes", list: true }), F("node_id", "Taxonomy Node", "ref:taxonomy"),
      F("price", "Price", "money", { required: true, list: true }), F("list", "List Price", "money", { col: "list_price" }),
      F("stock", "Stock", "number", { list: true }), F("rating", "Rating", "number"), F("count", "Ratings Count", "number", { col: "ratings_count" }),
      F("emoji", "Icon", "text"), F("hue", "Tint", "number"), F("priority", "Priority Eligible", "bool"),
      F("flags", "Flags", "text", { hint: "bs,new,ac" }), F("keywords", "Keywords", "textarea"),
      F("lifecycle", "Lifecycle", "select", { options: "lifecycle", list: true }),
      F("identity", "Identity (GTIN/HSN/…)", "json"), F("attrs", "Attributes", "json"), F("vertical", "Vertical Profile", "json"),
      F("media", "Media", "json"), F("seo", "SEO", "json"), F("pricing_rules", "Pricing Rules", "json"),
      F("logistics", "Logistics", "json"), F("packaging", "Packaging", "json"), F("uom", "Unit of Measure", "json"),
      F("tax_rule", "Tax Rule", "json"), F("geo_rules", "Geo Rules", "json"), F("docs", "Documents", "json"),
      F("supplier_id", "Marketplace Seller", "ref:seller"),
      F("source_kind", "Source", "select", { options: ["seed", "universe", "import"], readonly: true, list: true, hint: "seeded, activated from a corpus universe, or imported" }),
      F("source_universe", "Source Universe", "text", { readonly: true, list: true, hint: "the corpus universe this offering was activated from" })
    ]
  },
  sku: {
    table: "skus", pk: "id", label: "SKUs", icon: "🔖", perm: { read: ["admin", "platform"], write: ["admin"] }, sec: 'P2',
    fields: [F("uid", "Universal ID", "text", { readonly: true, list: true }), F("product_id", "Product", "ref:product", { required: true, list: true }), F("code", "SKU Code", "text", { required: true, list: true }),
    F("name", "Variant Name", "text", { list: true }), F("group_id", "Variant Group", "ref:variant_group", { list: true }),
    F("price", "Price", "money", { list: true }), F("mrp", "MRP", "money"),
    F("stock", "Stock", "number", { list: true }), F("active", "Active", "bool"), F("identity", "Identity", "json"), F("variant", "Variant Attributes", "json")]
  },
  inventory: {
    table: "inventory", pk: "id", label: "Inventory", icon: "🏬", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("sku_id", "SKU", "ref:sku", { required: true, list: true }), F("warehouse_id", "Warehouse", "ref:warehouse", { list: true }),
    F("qty", "Quantity", "number", { required: true, list: true }), F("reserved", "Reserved", "number"), F("lot", "Lot", "text"),
    F("batch", "Batch", "text"), F("expiry", "Expiry", "date")]
  },
  warehouse: {
    table: "warehouses", pk: "id", label: "Warehouses", icon: "🏭", perm: { read: ["admin", "platform"], write: ["admin"] }, sec: 'P2',
    fields: [F("uid", "Universal ID", "text", { readonly: true, list: true }), F("name", "Name", "text", { required: true, list: true }), F("code", "Code", "text", { list: true }),
    F("country", "Country", "text"), F("region", "Region", "text"), F("active", "Active", "bool")]
  },
  serialized: {
    table: "serialized_items", pk: "id", label: "Serialized Items", icon: "🔢", perm: { read: ["admin", "platform"], write: ["admin"] }, sec: 'P3',
    fields: [F("uid", "Universal ID", "text", { readonly: true, list: true }), F("id", "ID", "number", { readonly: true, list: true }),
    F("product_id", "Product", "ref:product", { required: true, list: true }), F("sku_id", "SKU", "ref:sku", { list: true }),
    F("warehouse_id", "Warehouse", "ref:warehouse", { list: true }),
    F("serial", "Serial Number", "text", { required: true, list: true }), F("imei", "IMEI", "text", { list: true }),
    F("rfid", "RFID / Tag", "text"), F("asset_tag", "Asset Tag", "text"), F("batch", "Batch", "text"), F("lot", "Lot", "text"),
    F("expiry", "Expiry", "date", { list: true }),
    F("status", "Status", "select", { options: "serializedStatuses", list: true }),
    F("condition", "Condition", "select", { options: "serializedConditions", list: true }),
    F("order_id", "Order", "number", { list: true }), F("purchase_date", "Purchase Date", "date"), F("warranty_end", "Warranty End", "date"),
    F("meta", "Meta", "json")]
  },
  variant_group: {
    table: "variant_groups", pk: "id", label: "Variant Groups", icon: "🎛️", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("id", "ID", "number", { readonly: true, list: true }),
    F("product_id", "Product", "ref:product", { required: true, list: true }), F("name", "Name", "text", { required: true, list: true }),
    F("axis", "Axis", "select", { options: "variantAxes", list: true }),
    F("attr_key", "Attribute Key", "text"), F("position", "Position", "number"), F("active", "Active", "bool")]
  },
  compliance: {
    table: "compliance_records", pk: "id", label: "Compliance & Certifications", icon: "✅", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("id", "ID", "number", { readonly: true, list: true }),
    F("scope", "Applies To", "select", { options: "complianceScopes", list: true }),
    F("ref_id", "Reference", "text", { list: true }), F("kind", "Kind", "select", { options: "complianceKinds", list: true }),
    F("code", "Code / Number", "text", { required: true, list: true }), F("issuer", "Issuing Body", "text", { list: true }),
    F("jurisdiction", "Jurisdiction", "text", { list: true, hint: "country code" }),
    F("status", "Status", "select", { options: "complianceStatuses", list: true }),
    F("valid_from", "Valid From", "date"), F("valid_to", "Valid To", "date"), F("doc_media", "Document Ref", "text"), F("notes", "Notes", "textarea")]
  },
  supplier: {
    table: "suppliers", pk: "id", label: "Suppliers", icon: "🚚", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("id", "ID", "number", { readonly: true, list: true }),
    F("name", "Name", "text", { required: true, list: true }),
    F("party_role", "Party Role", "select", { options: "supplierRoles", list: true }),
    F("tax_id", "Tax / GSTIN", "text"), F("country", "Country", "text", { list: true }), F("region", "Region", "text"), F("address", "Address", "textarea"),
    F("email", "Email", "text", { list: true }), F("phone", "Phone", "text"),
    F("lead_time_days", "Lead Time (days)", "number", { list: true }), F("moq", "Min Order Qty", "number"), F("currency", "Currency", "text"),
    F("payment_terms", "Payment Terms", "select", { options: "paymentTerms", list: true }),
    F("on_time_pct", "On-time %", "number"), F("status", "Status", "select", { options: "supplierStatuses", list: true }),
    F("certifications", "Certifications", "json"), F("price_list", "Price List", "json")]
  },
  product_supplier: {
    table: "product_suppliers", pk: "id", label: "Supplier Links", icon: "🔗", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("id", "ID", "number", { readonly: true, list: true }),
    F("product_id", "Product", "ref:product", { required: true, list: true }), F("supplier_id", "Supplier", "ref:supplier", { required: true, list: true }),
    F("supplier_sku", "Supplier SKU", "text"), F("price", "Unit Cost", "money", { list: true }),
    F("lead_days", "Lead Days", "number", { list: true }), F("moq", "Min Order", "number"),
    F("is_primary", "Primary", "bool", { list: true }), F("status", "Status", "select", { options: "linkStatuses", list: true })]
  },
  localization: {
    table: "localizations", pk: "id", label: "Localizations (i18n)", icon: "🌐", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("id", "ID", "number", { readonly: true, list: true }),
    F("entity", "Object Type", "select", { options: "localizationEntities", list: true }),
    F("ref_id", "Object Reference", "text", { required: true, list: true }), F("locale", "Locale", "text", { required: true, list: true, hint: "e.g. fr-FR" }),
    F("name", "Localized Name", "text", { list: true }), F("description", "Description", "textarea"),
    F("bullets", "Bullets", "json"), F("attrs", "Attributes", "json"), F("active", "Active", "bool")]
  },
  contract: {
    table: "contracts", pk: "id", label: "B2B Contracts", icon: "📝", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("id", "ID", "number", { readonly: true, list: true }), F("ref", "Contract #", "text", { readonly: true, list: true }),
    F("buyer_name", "Buyer", "text", { required: true, list: true }), F("buyer_email", "Buyer Email", "text", { required: true, list: true }),
    F("buyer_org", "Buyer Org", "text"), F("supplier_id", "Supplier", "ref:supplier", { list: true }),
    F("product_ids", "Products", "json", { hint: '["prodId", …]' }), F("currency", "Currency", "text"),
    F("pricing", "Pricing", "json", { hint: '{"fixed":{"id":price},"tiers":[…]}' }),     F("min_qty", "Min Qty", "number"),
    F("incoterms", "Incoterms", "select", { options: "incoterms" }),
    F("payment_terms", "Payment Terms", "select", { options: "paymentTerms" }),
    F("valid_from", "Valid From", "date"), F("valid_to", "Valid To", "date"),
    F("status", "Status", "select", { options: "contractStatuses", list: true }), F("notes", "Notes", "textarea")]
  },
  tender: {
    table: "tenders", pk: "id", label: "Tenders (Procurement)", icon: "🏛️", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("id", "ID", "number", { readonly: true, list: true }), F("ref", "Tender #", "text", { readonly: true, list: true }),
    F("title", "Title", "text", { required: true, list: true }), F("buyer_org", "Issuing Org", "text", { list: true }),
    F("buyer_email", "Contact Email", "text"), F("description", "Description", "textarea"), F("currency", "Currency", "text"),
    F("budget", "Budget", "money", { list: true }), F("open_at", "Opens", "date"), F("close_at", "Closes", "date"),
    F("status", "Status", "select", { options: "tenderStatuses", list: true }),
    F("awarded_seller_id", "Awarded Seller", "number", { readonly: true, list: true }), F("awarded_contract_id", "Awarded Contract", "number", { readonly: true, list: true }),
    F("items", "Line Items", "json"), F("bids", "Bids", "json")]
  },
  ai_usage: {
    table: "ai_usage", pk: "id", label: "AI Usage Ledger", icon: "🧮", perm: { read: ["admin", "platform"], write: [] },
    fields: [F("id", "ID", "number", { readonly: true, list: true }),
    F("capability", "Capability", "select", { options: "aiCapabilityKeys", list: true }), F("provider", "Provider", "text", { list: true }),
    F("model", "Model", "text", { list: true }), F("units", "Units", "number", { list: true }), F("cost", "Cost", "money", { list: true }),
    F("currency", "Currency", "text"), F("tier", "Tier", "select", { options: ["free", "premium"], list: true }), F("status", "Status", "text", { list: true }),
    F("actor", "Actor", "text"), F("created_at", "At", "readonly", { list: true })]
  },
  ai_task: {
    table: "ai_tasks", pk: "id", label: "AI Tasks", icon: "🤖", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("id", "ID", "number", { readonly: true, list: true }),
    F("capability", "Capability", "select", { options: "aiCapabilityKeys", required: true, list: true }),
    F("status", "Status", "select", { options: ["queued", "running", "done", "failed"], list: true }),
    F("params", "Params", "json"), F("result", "Result", "json", { readonly: true }), F("cost", "Cost", "money", { readonly: true, list: true }),
    F("actor", "Actor", "text", { readonly: true }), F("created_at", "Created", "readonly", { list: true })]
  },
  stock_transfer: {
    table: "stock_transfers", pk: "id", label: "Stock Transfers", icon: "🔄", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("id", "ID", "number", { readonly: true, list: true }),
    F("from_warehouse", "From", "ref:warehouse", { required: true, list: true }), F("to_warehouse", "To", "ref:warehouse", { required: true, list: true }),
    F("sku_id", "SKU", "ref:sku", { required: true, list: true }), F("qty", "Qty", "number", { required: true, list: true }),
    F("status", "Status", "select", { options: ["draft", "in_transit", "completed", "cancelled"], list: true }), F("reference", "Reference", "text"), F("note", "Note", "textarea"),
    F("created_at", "When", "readonly", { list: true })]
  },
  remittance: {
    table: "remittance_records", pk: "id", label: "Tax Remittance", icon: "🧾", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("id", "ID", "number", { readonly: true, list: true }),
    F("period", "Period", "text", { required: true, list: true }), F("jurisdiction", "Jurisdiction", "text", { required: true, list: true }),
    F("tax_type", "Type", "select", { options: ["vat", "gst", "sales", "withholding"], list: true }),
    F("taxable", "Taxable", "money", { list: true }), F("tax_collected", "Tax Collected", "money", { list: true }),
    F("status", "Status", "select", { options: ["pending", "filed", "paid", "amended"], list: true }), F("reference", "Reference", "text"), F("filed_at", "Filed", "date")]
  },
  order: {
    table: "orders", pk: "id", label: "Orders", icon: "🧾", perm: { read: ["admin", "platform"], write: ["admin"] }, sec: 'P2',
    fields: [F("uid", "Universal ID", "text", { readonly: true, list: true }), F("num", "Order #", "text", { readonly: true, list: true }), F("name", "Customer", "text", { list: true }),
    F("address", "Address", "textarea"), F("city", "City", "text"), F("state", "State", "text"), F("zip", "ZIP", "text"),
    F("sub", "Subtotal", "money", { list: true }), F("ship_fee", "Shipping", "money"), F("tax", "Tax", "money"),
    F("gift_used", "Gift Applied", "money"), F("total", "Total", "money", { list: true }),
    F("status", "Status", "select", { options: ["processing", "shipped", "delivered", "cancelled"], list: true }),
    F("pay_method", "Gateway", "text", { list: true }), F("ship_option", "Carrier", "text"), F("created_at", "Placed", "readonly", { list: true })]
  },
  ret: {
    table: "returns", pk: "id", label: "Returns", icon: "↩️", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("ref", "Return #", "text", { readonly: true, list: true }), F("order_id", "Order", "ref:order", { list: true }),
    F("product_id", "Product", "ref:product"), F("qty", "Qty", "number"), F("reason", "Reason", "textarea", { list: true }),
    F("status", "Status", "select", { options: ["requested", "approved", "received", "refunded", "rejected"], list: true }), F("created_at", "Date", "readonly", { list: true })]
  },
  rfq: {
    table: "rfqs", pk: "id", label: "RFQs (B2B)", icon: "📋", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("ref", "RFQ #", "text", { readonly: true, list: true }), F("product_id", "Product", "ref:product", { list: true }),
    F("buyer_name", "Buyer", "text", { required: true, list: true }), F("buyer_email", "Email", "text"),
    F("qty", "Quantity", "number", { list: true }), F("target_price", "Target Price", "money"),
    F("status", "Status", "select", { options: ["open", "quoted", "accepted", "rejected", "closed"], list: true }), F("quotes", "Quotes", "json")]
  },
  settlement: {
    table: "settlements", pk: "id", label: "Settlements", icon: "🤝", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("ref", "Settlement #", "text", { readonly: true, list: true }), F("seller_id", "Seller", "ref:seller", { list: true }),
    F("order_id", "Order", "ref:order"), F("gross", "Gross", "money", { list: true }), F("commission", "Commission", "money"),
    F("net", "Net Payable", "money", { list: true }), F("status", "Status", "select", { options: ["pending", "paid"], list: true }), F("period", "Period", "text")]
  },
  seller: {
    table: "sellers", pk: "id", label: "Sellers", icon: "🏪", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("name", "Name", "text", { required: true, list: true }), F("role", "Role", "select", { options: "sellerRoles", list: true }),
    F("email", "Email", "text"), F("status", "Status", "select", { options: ["active", "suspended"], list: true }), F("commission_pct", "Commission %", "number")]
  },
  promotion: {
    table: "promotions", pk: "id", label: "Promotions", icon: "🎯", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("name", "Name", "text", { required: true, list: true }), F("type", "Type", "select", { options: "promoTypes", list: true }),
    F("value", "Value", "number", { list: true }), F("code", "Coupon Code", "text"), F("starts", "Starts", "date"), F("ends", "Ends", "date"),
    F("status", "Status", "select", { options: ["active", "inactive"], list: true }), F("rules", "Rules", "json"), F("scope", "Scope", "json")]
  },
  department: {
    table: "departments", pk: "key", pkType: "text", label: "Departments", icon: "🗂️", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("key", "Key", "text", { required: true, list: true }), F("label", "Label", "text", { required: true, list: true }),
    F("icon", "Icon", "text"), F("active", "Active", "bool"), F("position", "Position", "number")]
  },
  brand: {
    table: "brands", pk: "key", pkType: "text", label: "Brands", icon: "🏷️", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("key", "Key", "text", { required: true, list: true }), F("label", "Brand Name", "text", { required: true, list: true }),
    F("icon", "Icon (emoji)", "text", { list: true }), F("logo", "Logo (URL or inline SVG)", "text"),
    F("story", "Brand Story", "textarea"), F("country", "Country of Origin", "text", { list: true }),
    F("active", "Active", "bool", { list: true }), F("position", "Position", "number")]
  },
  taxonomy: {
    table: "taxonomy", pk: "id", label: "Taxonomy", icon: "🌳", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("parent_id", "Parent", "ref:taxonomy", { list: true }), F("level", "Level", "select", { options: ["domain", "industry", "category", "subcategory", "family", "model"], list: true }),
    F("key", "Key", "text", { required: true, list: true }), F("name", "Name", "text", { required: true, list: true }),
    F("icon", "Icon", "text"), F("attrs", "Attributes", "json"), F("active", "Active", "bool"), F("position", "Position", "number")]
  },
  attribute: {
    table: "attribute_defs", pk: "key", pkType: "text", label: "Attribute Definitions", icon: "🧬", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("key", "Key", "text", { required: true, list: true }), F("label", "Label", "text", { required: true, list: true }),
    F("grp", "Group", "text", { list: true }), F("type", "Type", "select", { options: ["text", "number", "bool", "date", "select", "multi", "json"], list: true }),
    F("unit", "Unit", "text"), F("options", "Options", "json"), F("validation", "Validation", "json"), F("industry", "Industry", "text"), F("position", "Position", "number")]
  },
  /* the context primitive: a dimension (grp) holds named profiles (key) with their own
     declarative fields. Seeded from the registry's verticalContexts, but the table is the
     source of truth, so an operator adds a context dimension here and it appears in the
     product view and at checkout with no code change (see api.js context resolution). */
  context_type: {
    table: "context_types", noTenant: true, pk: "id", pkType: "number", label: "Context Types", icon: "🧭", perm: { read: ["platform"], write: ["platform"] }, platformOnly: true,
    fields: [F("grp", "Dimension", "text", { required: true, list: true }), F("key", "Profile Key", "text", { required: true, list: true }),
    F("label", "Label", "text", { required: true, list: true }), F("type", "Kind", "text", { list: true }),
    F("fields", "Fields", "json"), F("position", "Position", "number")]
  },
  /* the relationship primitive: a typed edge between any two entities by their universal id.
     RELATIONSHIP OWNS RELATIONSHIP — an edge is created once here and reused by every surface
     that relates two things, exactly as a country master is created once and reused by every
     jurisdiction. The product-scoped `relationships` table the storefront reads is a DERIVED
     projection of this (lib/registry.js reconcileLinks), never a second source of truth: the
     old path wrote the projection first and mirrored here best-effort, which left the primitive
     optional and silently absent, so an edge existed in one store's catalogue and in nothing
     else. `links` is noTenant because an edge is platform-level — a store attaches to it by
     owning its endpoints, never by scoping the row. */
  link: {
    table: "links", noTenant: true, pk: "id", pkType: "number", label: "Universal Links", icon: "🔗", perm: { read: ["platform"], write: ["platform"] }, platformOnly: true,
    fields: [F("type", "Relationship Type", "select", { options: "relTypes", required: true, list: true }),
    F("from_entity", "From Entity", "text", { required: true, list: true }), F("from_uid", "From UID", "text", { required: true, list: true }),
    F("to_entity", "To Entity", "text", { required: true, list: true }), F("to_uid", "To UID", "text", { required: true, list: true }),
    F("meta", "Metadata", "json"), F("created_at", "When", "readonly", { list: true })]
  },
  banner: {
    table: "home_banners", pk: "id", label: "Home Banners", icon: "🖼️", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("title", "Title", "text", { required: true, list: true }), F("subtitle", "Subtitle", "text"), F("cta", "CTA", "text"),
    F("hue", "Tint", "number"), F("dept", "Department", "ref:department"), F("active", "Active", "bool"), F("position", "Position", "number")]
  },
  card: {
    table: "home_cards", pk: "id", label: "Home Cards", icon: "🃏", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("title", "Title", "text", { required: true, list: true }), F("dept", "Department", "ref:department", { list: true }),
    F("tiles", "Tiles", "json"), F("active", "Active", "bool"), F("position", "Position", "number")]
  },
  review: {
    table: "reviews", pk: "id", label: "Reviews", icon: "⭐", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("product_id", "Product", "ref:product", { list: true }), F("name", "Author", "text", { list: true }),
    F("rating", "Rating", "number", { list: true }), F("title", "Title", "text", { list: true }), F("body", "Body", "textarea"),
    F("verified", "Verified", "bool"), F("state", "Moderation", "select", { options: "ugcStates", list: true }),
    F("votes_helpful", "Helpful votes", "number", { list: true }), F("votes_total", "Total votes", "number"),
    F("media", "Media", "json"), F("created_at", "Date", "readonly", { list: true })]
  },
  review_reply: {
    table: "review_replies", pk: "id", label: "Review Replies", icon: "💬", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("review_id", "Review", "number", { required: true, list: true }), F("author", "Author", "text", { list: true }),
    F("role", "Role", "select", { options: "ugcRoles", list: true }), F("body", "Reply", "textarea"), F("created_at", "Date", "readonly", { list: true })]
  },
  qna_question: {
    table: "qna_questions", pk: "id", label: "Product Questions", icon: "❓", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("product_id", "Product", "ref:product", { list: true }), F("name", "Asked by", "text", { list: true }),
    F("body", "Question", "textarea", { list: true }), F("state", "Moderation", "select", { options: "ugcStates", list: true }),
    F("votes_helpful", "Helpful votes", "number", { list: true }), F("votes_total", "Total votes", "number"),
    F("answered_at", "Answered", "readonly"), F("created_at", "Asked", "readonly", { list: true })]
  },
  qna_answer: {
    table: "qna_answers", pk: "id", label: "Question Answers", icon: "💡", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("question_id", "Question", "number", { required: true, list: true }), F("name", "Answered by", "text", { list: true }),
    F("role", "Role", "select", { options: "ugcRoles", list: true }), F("body", "Answer", "textarea"),
    F("state", "Moderation", "select", { options: "ugcStates", list: true }), F("votes_helpful", "Helpful votes", "number", { list: true }),
    F("votes_total", "Total votes", "number"), F("created_at", "Date", "readonly", { list: true })]
  },
  ticket: {
    table: "tickets", pk: "id", label: "Support Tickets", icon: "🎧", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("ref", "Reference", "text", { list: true }), F("subject", "Subject", "text", { list: true }),
    F("reason", "Reason", "select", { options: "hdReasons", list: true }), F("priority", "Priority", "select", { options: "hdPriorities", list: true }),
    F("status", "Status", "select", { options: "hdStatuses", list: true }), F("assignee", "Assignee", "text", { list: true }),
    F("owner_name", "Customer", "text", { list: true }), F("owner_email", "Email", "text"),
    F("order_ref", "Order ref", "text"), F("product_id", "Product", "ref:product"),
    F("body", "Message", "textarea"), F("csat", "CSAT", "number", { list: true }),
    F("sla_response", "SLA · response", "date"), F("sla_resolution", "SLA · resolution", "date"),
    F("created_at", "Opened", "readonly", { list: true })]
  },
  ticket_note: {
    table: "ticket_notes", pk: "id", label: "Ticket Notes", icon: "📝", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("ticket_id", "Ticket", "number", { required: true, list: true }), F("author", "Author", "text", { list: true }),
    F("role", "Role", "text", { list: true }), F("body", "Note", "textarea"),
    F("visibility", "Visibility", "select", { options: ["public", "internal"], list: true }), F("created_at", "Date", "readonly", { list: true })]
  },
  address: {
    table: "addresses", pk: "id", label: "Address Book", icon: "📍", perm: { read: ["admin", "platform"], write: [] },
    fields: [F("label", "Label", "text", { list: true }), F("name", "Recipient", "text", { required: true, list: true }),
    F("address", "Address", "text", { required: true, list: true }), F("city", "City", "text", { required: true, list: true }),
    F("state", "State / Province", "ref:subdivision"), F("zip", "ZIP", "text"), F("country", "Country", "ref:country"),
    F("phone", "Phone", "text"), F("is_default", "Default", "bool", { list: true })]
  },
  recurring_schedule: {
    table: "recurring_schedules", pk: "id", label: "Subscribe & Save", icon: "🔁", perm: { read: ["admin", "platform"], write: [] },
    fields: [F("owner", "Customer", "text", { list: true }), F("product_id", "Product", "ref:product", { list: true }),
    F("qty", "Qty", "number", { list: true }), F("frequency_days", "Frequency (days)", "number", { list: true }),
    F("discount_pct", "Discount %", "number", { list: true }), F("next_ship_at", "Next shipment", "date", { list: true }),
    F("status", "Status", "select", { options: "recSchedStatuses", list: true }), F("cycles_completed", "Cycles done", "number", { list: true }),
    F("created_at", "Started", "readonly", { list: true })]
  },
  recurring_cycle: {
    table: "recurring_cycles", pk: "id", label: "Delivery Cycles", icon: "📦", perm: { read: ["admin", "platform"], write: [] },
    fields: [F("schedule_id", "Schedule", "number", { required: true, list: true }), F("order_ref", "Order", "text", { list: true }),
    F("status", "Status", "select", { options: "recCycleStatuses", list: true }), F("at", "Ships at", "date", { list: true })]
  },
  membership: {
    table: "memberships", pk: "id", label: "Memberships", icon: "🎟️", perm: { read: ["admin", "platform"], write: [] },
    fields: [F("owner", "Customer", "text", { list: true }), F("tier", "Tier", "select", { options: "membershipTiers", list: true }),
    F("status", "Status", "select", { options: "membershipStatuses", list: true }),
    F("started_at", "Started", "readonly", { list: true }), F("renews_at", "Renews", "date", { list: true }), F("cancelled_at", "Cancelled", "date")]
  },
  risk_event: {
    table: "risk_events", pk: "id", label: "Risk Events", icon: "🛡️", perm: { read: ["admin", "platform"], write: [] },
    fields: [F("owner", "Customer", "text", { list: true }), F("ip", "IP", "text", { list: true }),
    F("amount", "Amount", "money", { list: true }), F("score", "Risk score", "number", { list: true }),
    F("action", "Decision", "select", { options: "riskActions", list: true }), F("signals", "Signals", "json"),
    F("ref", "Reference", "text", { list: true }), F("resolved", "Resolved", "bool", { list: true }),
    F("resolution", "Resolution", "text"), F("created_at", "At", "readonly", { list: true })]
  },
  risk_block: {
    table: "risk_blocklist", pk: "id", label: "Risk Blocklists", icon: "⛔", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("kind", "Kind", "select", { options: ["email", "card", "address", "ip"], list: true }),
    F("value", "Fingerprint", "text", { required: true, list: true }), F("note", "Note", "text"), F("created_at", "Added", "readonly", { list: true })]
  },
  experiment: {
    table: "experiments", pk: "id", label: "Experiments", icon: "🧪", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("key", "Key", "text", { required: true, list: true }), F("name", "Name", "text", { list: true }),
    F("variants", "Variants", "json"), F("status", "Status", "select", { options: "expStatuses", list: true }),
    F("metric", "Metric", "text", { list: true }), F("started_at", "Started", "date", { list: true }), F("ended_at", "Ended", "date")]
  },
  replenishment: {
    table: "replenishments", pk: "id", label: "Replenishments", icon: "📦", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("sku_id", "SKU", "number", { list: true }), F("product_id", "Product", "text", { list: true }),
    F("on_hand", "On hand", "number", { list: true }), F("reserved", "Reserved", "number"), F("available", "Available", "number", { list: true }),
    F("avg_daily", "Avg / day", "number"), F("forecast_30d", "Forecast 30d", "number", { list: true }), F("trend", "Trend", "number"),
    F("lead_days", "Lead days", "number"), F("safety_stock", "Safety stock", "number"), F("reorder_point", "Reorder point", "number", { list: true }),
    F("reorder_qty", "Reorder qty", "number", { list: true }), F("min_qty", "Min qty", "number"), F("max_qty", "Max qty", "number"),
    F("supplier_name", "Supplier", "text", { list: true }), F("unit_cost", "Unit cost", "money"),
    F("status", "Status", "select", { options: "planStatuses", list: true }), F("priority", "Priority", "select", { options: "planPriorities", list: true }),
    F("po_ref", "PO ref", "text", { list: true }), F("generated_at", "Generated", "readonly", { list: true })]
  },
  customer: {
    table: "users", pk: "id", label: "Customers", icon: "👥", perm: { read: ["admin", "platform"], write: ["admin"] }, sec: 'P3',
    fields: [F("uid", "Universal ID", "text", { readonly: true, list: true }), F("name", "Name", "text", { required: true, list: true }), F("email", "Email", "text", { required: true, list: true }),
    F("role", "Role", "select", { options: ["customer", "admin"], list: true }), F("created_at", "Joined", "readonly", { list: true })]
  },
  gateway: {
    table: "tenant_gateways", pk: "provider_id", pkType: "text", label: "Payment Gateways", icon: "💳", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("provider_id", "Provider", "text", { required: true, list: true }), F("enabled", "Enabled", "bool", { list: true }),
    F("is_primary", "Primary", "bool", { list: true }), F("mode", "Mode", "select", { options: ["sandbox", "live"], list: true }),
    F("config", "Config", "json"), F("position", "Position", "number")]
  },
  payment: {
    table: "payments", pk: "id", label: "Payments", icon: "🧮", perm: { read: ["admin", "platform"], write: [] }, sec: 'P4',
    fields: [F("uid", "Universal ID", "text", { readonly: true, list: true }), F("kind", "Kind", "select", { options: ["order", "subscription"], list: true }), F("gateway", "Gateway", "text", { list: true }),
    F("method", "Method", "text"), F("amount", "Amount", "money", { list: true }), F("currency", "Currency", "text"),
    F("fee", "Fee", "money", { list: true }), F("status", "Status", "select", { options: ["initiated", "pending", "captured", "failed", "refunded"], list: true }),
    F("txn_ref", "Txn Ref", "text", { list: true }), F("created_at", "Date", "readonly", { list: true })]
  },
  tenant: {
    table: "tenants", pk: "id", label: "Stores (Tenants)", icon: "🏬", perm: { read: ["platform"], write: ["platform"] }, platformOnly: true, sec: 'P3',
    fields: [F("uid", "Universal ID", "text", { readonly: true, list: true }), F("slug", "Slug", "text", { required: true, list: true }), F("name", "Name", "text", { required: true, list: true }),
    F("domain", "Domain", "text", { list: true }), F("mode", "Mode", "select", { options: "deployModes", list: true }),
    F("industries", "Industries", "json"), F("status", "Status", "select", { options: ["active", "suspended"], list: true })]
  },
  plan: {
    table: "plans", pk: "id", label: "Plans", icon: "💼", perm: { read: ["platform"], write: ["platform"] }, platformOnly: true,
    fields: [F("name", "Name", "text", { required: true, list: true }), F("price_month", "Price / Month", "money", { list: true }),
    F("currency", "Currency", "text"), F("max_products", "Max Products", "number", { list: true }), F("max_orders_month", "Max Orders / Month", "number", { list: true }), F("position", "Position", "number")]
  },
  subscription: {
    table: "subscriptions", pk: "id", label: "Subscriptions", icon: "🔁", perm: { read: ["platform"], write: ["platform"] }, platformOnly: true,
    fields: [F("tenant_id", "Store", "ref:tenant", { required: true, list: true }), F("plan_id", "Plan", "ref:plan", { required: true, list: true }),
    F("status", "Status", "select", { options: ["trialing", "active", "past_due", "cancelled"], list: true }), F("renews_at", "Renews", "date")]
  },
  invoice: {
    table: "invoices", pk: "id", label: "Invoices", icon: "🧾", perm: { read: ["platform"], write: ["platform"] }, platformOnly: true, sec: 'P4',
    fields: [F("uid", "Universal ID", "text", { readonly: true, list: true }), F("tenant_id", "Store", "ref:tenant", { required: true, list: true }), F("number", "Number", "text", { required: true, list: true }),
    F("amount", "Amount", "money", { required: true, list: true }), F("currency", "Currency", "text"),
    F("status", "Status", "select", { options: ["draft", "paid", "overdue", "void"], list: true }), F("period_start", "Period Start", "date"),
    F("period_end", "Period End", "date"), F("note", "Note", "text"), F("issued_at", "Issued", "readonly", { list: true })]
  },
  custom_provider: {
    table: "custom_providers", pk: "id", label: "Custom Providers", icon: "🔌", perm: { read: ["platform", "admin"], write: ["platform", "admin"] },
    fields: [F("scope", "Scope", "select", { options: ["platform", "tenant"], list: true }), F("kind", "Kind", "select", { options: "providerKinds", list: true }),
    F("manifest", "Manifest", "json", { required: true })]
  },
  /* ---- GOIP Ω∞ stores: the four records no other entity owns ---- */
  goip_touchpoint: {
    table: "goip_touchpoints", pk: "id", label: "GOIP · Touchpoints", icon: "🔗", perm: { read: ["admin", "platform"], write: ["platform"] },
    fields: [F("kind", "Kind", "select", { options: "goipTouchpointKinds", list: true }), F("party", "Party", "text", { list: true }),
    F("party_type", "Party type", "select", { options: "goipPartyTypes", list: true }), F("channel", "Channel", "text", { list: true }),
    F("distribution", "Distribution", "text", { list: true }), F("owner", "Subject", "text", { list: true }),
    F("subject_uid", "Value exchange (uid)", "text"), F("offer_id", "Value exchange", "number"), F("code", "Code", "text"),
    F("order_id", "Order", "number"), F("value", "Value", "money", { list: true }), F("unit", "Unit", "text"),
    F("device", "Device", "text"), F("session", "Session", "text"), F("context", "Context", "json"), F("created_at", "When", "readonly", { list: true })]
  },
  goip_budget: {
    table: "goip_budgets", pk: "id", label: "GOIP · Funding budgets", icon: "🏦", perm: { read: ["admin", "platform"], write: ["platform"] },
    fields: [F("funder", "Funder", "select", { options: "goipFunders", required: true, list: true }), F("funder_ref", "Funder ref", "text", { list: true }),
    F("domain", "Domain", "text", { list: true }), F("unit", "Economic unit", "text", { required: true, list: true }),
    F("allocated", "Allocated", "money", { list: true }), F("reserved", "Reserved", "money", { list: true }), F("consumed", "Consumed", "money", { list: true }),
    F("period", "Period", "text", { list: true }), F("status", "Status", "select", { options: ["open", "exhausted", "closed"], list: true }), F("policy", "Policy", "json")]
  },
  goip_settlement: {
    table: "goip_settlements", pk: "id", label: "GOIP · Settlements", icon: "💱", perm: { read: ["admin", "platform"], write: ["platform"] },
    fields: [F("period", "Period", "text", { list: true }), F("party", "Party", "text", { required: true, list: true }),
    F("party_type", "Party type", "select", { options: "goipPartyTypes", list: true }), F("unit", "Unit", "text", { list: true }),
    F("gross", "Gross", "money", { list: true }), F("fees", "Fees", "money"), F("net", "Net", "money", { list: true }),
    F("redemptions", "Redemptions", "number", { list: true }), F("status", "Status", "select", { options: "goipSettlementStatuses", list: true }),
    F("reference", "Payout reference", "text", { list: true }), F("paid_at", "Paid", "readonly"), F("meta", "Meta", "json")]
  },
  goip_entitlement: {
    table: "goip_entitlements", pk: "id", label: "GOIP · Entitlements", icon: "🎟️", perm: { read: ["admin", "platform"], write: ["platform"] },
    fields: [F("owner", "Subject", "text", { required: true, list: true }), F("benefit", "Benefit", "text", { required: true, list: true }),
    F("unit", "Unit", "text", { list: true }), F("qty", "Quantity", "number", { list: true }), F("tier", "Tier", "text", { list: true }),
    F("scope", "Scope", "json"), F("starts", "Starts", "date"), F("ends", "Ends / due", "date", { list: true }),
    F("status", "Status", "select", { options: "goipEntitlementStatuses", list: true }),
    F("source_offer", "From value exchange", "number"), F("source_redemption", "From redemption", "number"), F("meta", "Meta", "json")]
  }
};

/* ============================================================
   UNIVERSAL COMMERCE ENTITIES — each block is one capability,
   expressed purely as entity data: fields, types, options
   from registries (meta_lists). CRUD, validation, forms, lists and
   RBAC gates arrive generically from this declaration — zero
   per-domain code (Architecture3 Article 4.2). Merged into the entity
   set by allEntities() so tenant-defined custom entities can override.
   ============================================================ */
const PARITY_DEFS = {
/* ---------- Quick-commerce ---------- */
  dark_store: {
    table: "dark_stores", pk: "id", label: "Dark Stores", icon: "🏬", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("uid", "Universal ID", "text", { readonly: true, list: true }), F("name", "Store Name", "text", { required: true, list: true }),
    F("code", "Store Code", "text", { list: true }), F("kind", "Store Type", "select", { options: "qcStoreKinds", list: true }),
    F("address", "Address", "textarea"), F("city", "City", "text", { list: true }), F("region", "Region", "text"), F("pincode", "Pincode", "text", { list: true }),
    F("country", "Country", "text"), F("lat", "Latitude", "number"), F("lng", "Longitude", "number"),
    F("service_radius_km", "Service Radius (km)", "number", { list: true }),
    F("promise_minutes", "Promise (minutes)", "number", { list: true }), F("prep_minutes", "Prep (minutes)", "number"),
    F("min_order", "Min Order", "money"), F("delivery_fee", "Delivery Fee", "money"),
    F("service_pincodes", "Service Pincodes", "json"), F("service_days", "Service Days", "json"),
    F("status", "Status", "select", { options: "qcStoreStatuses", list: true })]
  },
  delivery_slot: {
    table: "delivery_slots", pk: "id", label: "Delivery Slots", icon: "🕐", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("store_id", "Store", "ref:dark_store", { list: true }), F("day_offset", "Day Offset", "number", { list: true }),
    F("window_start", "Window Start", "text", { required: true, list: true }), F("window_end", "Window End", "text", { required: true, list: true }),
    F("capacity", "Capacity", "number", { list: true }), F("booked", "Booked", "number", { list: true }),
    F("cutoff_minutes", "Cutoff (min)", "number"), F("fee", "Slot Fee", "money"),
    F("promise_minutes", "Promise (min)", "number"), F("status", "Status", "select", { options: "qcSlotStatuses", list: true })]
  },
  service_area: {
    table: "service_areas", pk: "id", label: "Service Areas", icon: "🗺️", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("store_id", "Store", "ref:dark_store", { list: true }), F("pincode", "Pincode / ZIP", "text", { required: true, list: true }),
    F("area_name", "Area Name", "text", { list: true }), F("serviceable", "Serviceable", "bool", { list: true }),
    F("eta_minutes", "ETA (min)", "number", { list: true }), F("fee", "Delivery Fee", "money"), F("min_order", "Min Order", "money"),
    F("cod_available", "COD Available", "bool"), F("status", "Status", "select", { options: "qcAreaStatuses", list: true })]
  },
  store_inventory: {
    table: "store_inventory", pk: "id", label: "Store Inventory", icon: "📦", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("store_id", "Store", "ref:dark_store", { required: true, list: true }),
    F("product_id", "Product", "ref:product", { list: true }), F("sku_id", "SKU", "ref:sku", { list: true }),
    F("qty", "Quantity", "number", { list: true }), F("reserved", "Reserved", "number", { list: true }),
    F("safety_stock", "Safety Stock", "number"), F("status", "Status", "select", { options: "qcInvStatuses", list: true })]
  },
  rider: {
    table: "riders", pk: "id", label: "Riders", icon: "🛵", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("uid", "Universal ID", "text", { readonly: true, list: true }), F("name", "Rider Name", "text", { required: true, list: true }),
    F("phone", "Phone", "text", { list: true }), F("vehicle", "Vehicle", "select", { options: "qcVehicles", list: true }),
    F("store_id", "Home Store", "ref:dark_store", { list: true }), F("city", "City", "text", { list: true }),
    F("status", "Status", "select", { options: "qcRiderStatuses", list: true }),
    F("shift_start", "Shift Start", "text"), F("shift_end", "Shift End", "text"),
    F("rating", "Rating", "number", { list: true }), F("deliveries", "Deliveries", "number", { list: true })]
  },
  dispatch_run: {
    table: "dispatch_runs", pk: "id", label: "Dispatch Runs", icon: "🧺", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("ref", "Run #", "text", { readonly: true, list: true }), F("store_id", "Store", "ref:dark_store", { list: true }),
    F("slot_id", "Slot", "ref:delivery_slot", { list: true }), F("rider_id", "Rider", "ref:rider", { list: true }),
    F("order_ids", "Orders", "json"), F("batch_count", "Batch Size", "number", { list: true }),
    F("pod_otp", "PoD OTP", "text"), F("pod_at", "Delivered At", "readonly", { list: true }),
    F("status", "Status", "select", { options: "qcDispatchStatuses", list: true }), F("notes", "Notes", "textarea")]
  },

  /* ---------- Fintech ---------- */
  upi_handle: {
    table: "upi_handles", pk: "id", label: "UPI Handles (VPA)", icon: "📱", perm: { read: ["admin", "platform"], write: [] },
    fields: [F("owner", "Customer", "text", { list: true }), F("vpa", "VPA", "text", { required: true, list: true }),
    F("name", "Name at Bank", "text"), F("verified", "Verified", "bool", { list: true }),
    F("is_default", "Default", "bool", { list: true }), F("status", "Status", "select", { options: "finUpiStatuses", list: true })]
  },
  upi_collect: {
    table: "upi_collects", pk: "id", label: "UPI Collect Requests", icon: "💸", perm: { read: ["admin", "platform"], write: [] },
    fields: [F("ref", "Request #", "text", { readonly: true, list: true }), F("owner", "Payee", "text", { list: true }),
    F("payer_vpa", "Payer VPA", "text", { list: true }), F("amount", "Amount", "money", { required: true, list: true }),
    F("currency", "Currency", "text"), F("note", "Note", "text"),
    F("status", "Status", "select", { options: "finCollectStatuses", list: true }), F("txn_ref", "Txn Ref", "text", { list: true }),
    F("expires_at", "Expires", "date", { list: true })]
  },
  qr_code: {
    table: "qr_codes", pk: "id", label: "QR Codes", icon: "▦", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("ref", "QR #", "text", { readonly: true, list: true }), F("kind", "Kind", "select", { options: "finQrKinds", list: true }),
    F("payload", "Payload", "textarea", { required: true }), F("label", "Label", "text", { list: true }),
    F("amount", "Amount", "money"), F("owner", "Owner", "text"), F("svg", "SVG", "json", { readonly: true }),
    F("scans", "Scans", "number", { list: true }), F("status", "Status", "select", { options: "finQrStatuses", list: true })]
  },
  payment_link: {
    table: "payment_links", pk: "id", label: "Payment Links", icon: "🔗", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("ref", "Link #", "text", { readonly: true, list: true }), F("token", "Token", "text", { readonly: true }),
    F("title", "Title", "text", { required: true, list: true }), F("amount", "Amount", "money", { required: true, list: true }),
    F("currency", "Currency", "text"), F("owner", "Payer", "text"), F("gateway", "Gateway", "text", { list: true }),
    F("purpose", "Purpose", "text"), F("expires_at", "Expires", "date"),
    F("status", "Status", "select", { options: "finLinkStatuses", list: true }), F("txn_ref", "Txn Ref", "text")]
  },
  mandate: {
    table: "mandates", pk: "id", label: "Mandates (Auto-Debit)", icon: "🔁", perm: { read: ["admin", "platform"], write: [] },
    fields: [F("ref", "Mandate #", "text", { readonly: true, list: true }), F("owner", "Customer", "text", { required: true, list: true }),
    F("mandate_id", "Mandate ID", "text"), F("gateway", "Gateway", "text", { list: true }),
    F("max_amount", "Max Amount", "money"), F("frequency", "Frequency", "select", { options: "finMandateFrequencies", list: true }),
    F("purpose", "Purpose", "text"), F("next_charge_at", "Next Charge", "date", { list: true }),
    F("charged_amount", "Charged So Far", "money", { list: true }), F("charges_done", "Charges Done", "number"),
    F("status", "Status", "select", { options: "finMandateStatuses", list: true })]
  },
  escrow_hold: {
    table: "escrow_holds", pk: "id", label: "Escrow Holds", icon: "🛡️", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("ref", "Escrow #", "text", { readonly: true, list: true }), F("order_id", "Order", "ref:order", { list: true }),
    F("buyer", "Buyer", "text", { list: true }), F("seller", "Seller", "text", { list: true }),
    F("amount", "Amount Held", "money", { required: true, list: true }), F("currency", "Currency", "text"),
    F("held", "Held", "bool", { list: true }), F("released_at", "Released", "readonly", { list: true }),
    F("dispute_opened", "Dispute Opened", "bool"), F("status", "Status", "select", { options: "finEscrowStatuses", list: true }),
    F("meta", "Meta", "json")]
  },
  split_payment: {
    table: "split_payments", pk: "id", label: "Split Payments", icon: "➗", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("ref", "Split #", "text", { readonly: true, list: true }), F("payment_id", "Payment", "ref:payment", { list: true }),
    F("order_id", "Order", "ref:order", { list: true }), F("splits", "Splits", "json", { hint: '[{"party":"seller:1","amount":10}]' }),
    F("status", "Status", "select", { options: "finSplitStatuses", list: true }), F("settled_at", "Settled", "readonly", { list: true })]
  },
  kyc_profile: {
    table: "kyc_profiles", pk: "id", label: "KYC Profiles", icon: "🪪", perm: { read: ["admin", "platform"], write: [] },
    fields: [F("owner", "Customer", "text", { required: true, list: true }), F("kind", "Type", "select", { options: "finKycKinds", list: true }),
    F("full_name", "Full Name", "text", { required: true, list: true }), F("dob", "Date of Birth", "date"),
    F("pan", "PAN", "text"), F("aadhaar_masked", "Aadhaar (masked)", "text"), F("gstin", "GSTIN", "text"),
    F("company", "Company", "text"), F("website", "Website", "text"),
    F("doc_type", "Document Type", "select", { options: "finKycDocs", list: true }), F("doc_ref", "Document Ref", "text"),
    F("doc_status", "Doc Status", "select", { options: "finKycDocStatuses", list: true }),
    F("status", "Status", "select", { options: "finKycStatuses", list: true }), F("verified_at", "Verified", "readonly", { list: true })]
  },
  bank_payout: {
    table: "bank_payouts", pk: "id", label: "Bank Payouts", icon: "🏦", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("ref", "Payout #", "text", { readonly: true, list: true }), F("payee", "Payee", "text", { required: true, list: true }),
    F("amount", "Amount", "money", { required: true, list: true }), F("currency", "Currency", "text"),
    F("account_name", "Account Name", "text"), F("account_number", "Account Number", "text"),
    F("ifsc", "IFSC", "text"), F("upi_vpa", "UPI VPA", "text"),
    F("gateway", "Gateway", "text", { list: true }), F("status", "Status", "select", { options: "finPayoutStatuses", list: true }),
    F("txn_ref", "Txn Ref", "text"), F("failure_reason", "Failure Reason", "text")]
  },
  biller: {
    table: "billers", pk: "id", label: "Billers (BBPS)", icon: "🧾", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("name", "Biller Name", "text", { required: true, list: true }), F("category", "Category", "select", { options: "finBillerCategories", list: true }),
    F("code", "Biller Code", "text"), F("fetch_required", "Bill Fetch Required", "bool"),
    F("fields", "Input Fields", "json"), F("status", "Status", "select", { options: ["active", "inactive"], list: true }),
    F("position", "Position", "number")]
  },
  bill_payment: {
    table: "bill_payments", pk: "id", label: "Bill Payments", icon: "💡", perm: { read: ["admin", "platform"], write: [] },
    fields: [F("ref", "Payment #", "text", { readonly: true, list: true }), F("owner", "Customer", "text", { list: true }),
    F("biller_id", "Biller", "ref:biller", { list: true }), F("category", "Category", "text", { list: true }),
    F("account_no", "Account / Consumer No", "text", { list: true }),
    F("amount", "Amount", "money", { required: true, list: true }), F("currency", "Currency", "text"),
    F("convenience_fee", "Convenience Fee", "money"), F("status", "Status", "select", { options: "finBillStatuses", list: true }),
    F("txn_ref", "Txn Ref", "text")]
  },
  recharge: {
    table: "recharges", pk: "id", label: "Mobile / DTH Recharges", icon: "📡", perm: { read: ["admin", "platform"], write: [] },
    fields: [F("ref", "Recharge #", "text", { readonly: true, list: true }), F("owner", "Customer", "text", { list: true }),
    F("number", "Number", "text", { required: true, list: true }), F("operator", "Operator", "select", { options: "finOperators", list: true }),
    F("circle", "Circle", "select", { options: "finCircles", list: true }), F("plan_id", "Plan", "ref:recharge_plan"),
    F("amount", "Amount", "money", { required: true, list: true }), F("currency", "Currency", "text"),
    F("kind", "Kind", "select", { options: "finRechargeKinds", list: true }),
    F("status", "Status", "select", { options: "finRechargeStatuses", list: true }), F("txn_ref", "Txn Ref", "text")]
  },
  recharge_plan: {
    table: "recharge_plans", pk: "id", label: "Recharge Plans", icon: "📋", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("operator", "Operator", "select", { options: "finOperators", required: true, list: true }),
    F("circle", "Circle", "select", { options: "finCircles", list: true }), F("kind", "Kind", "select", { options: "finRechargeKinds", list: true }),
    F("amount", "Price", "money", { required: true, list: true }), F("currency", "Currency", "text"),
    F("validity", "Validity", "text", { list: true }), F("data", "Data", "text"), F("sms", "SMS", "text"), F("calls", "Calls", "text"),
    F("description", "Description", "textarea"), F("popular", "Popular", "bool", { list: true }),
    F("status", "Status", "select", { options: ["active", "inactive"], list: true }), F("position", "Position", "number")]
  },
  bnpl_account: {
    table: "bnpl_accounts", pk: "id", label: "BNPL Accounts", icon: "💳", perm: { read: ["admin", "platform"], write: [] },
    fields: [F("owner", "Customer", "text", { required: true, list: true }), F("provider", "Provider", "text"),
    F("credit_limit", "Credit Limit", "money", { list: true }), F("used", "Used", "money", { list: true }),
    F("available", "Available", "money", { list: true }), F("tenure_months", "Tenure (months)", "number"),
    F("status", "Status", "select", { options: "finBnplStatuses", list: true }), F("kyc_id", "KYC Profile", "ref:kyc_profile")]
  },
  bnpl_emi: {
    table: "bnpl_emis", pk: "id", label: "BNPL EMIs", icon: "📅", perm: { read: ["admin", "platform"], write: [] },
    fields: [F("account_id", "Account", "ref:bnpl_account", { required: true, list: true }), F("order_id", "Order", "ref:order", { list: true }),
    F("installment_no", "Installment #", "number", { list: true }), F("amount", "Amount", "money", { list: true }),
    F("due_at", "Due", "date", { list: true }), F("status", "Status", "select", { options: "finEmiStatuses", list: true }),
    F("paid_at", "Paid At", "readonly")]
  },
  loan: {
    table: "loans", pk: "id", label: "Loans & Credit Lines", icon: "🏦", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("ref", "Loan #", "text", { readonly: true, list: true }), F("owner", "Customer", "text", { required: true, list: true }),
    F("principal", "Principal", "money", { required: true, list: true }), F("currency", "Currency", "text"),
    F("tenure_months", "Tenure (months)", "number", { list: true }), F("rate", "Interest Rate %", "number"),
    F("emi", "EMI", "money", { list: true }), F("processing_fee", "Processing Fee", "money"),
    F("disbursed_at", "Disbursed", "date"), F("status", "Status", "select", { options: "finLoanStatuses", list: true }),
    F("kyc_id", "KYC Profile", "ref:kyc_profile")]
  },
  insurance_policy: {
    table: "insurance_policies", pk: "id", label: "Insurance Policies", icon: "☂️", perm: { read: ["admin", "platform"], write: [] },
    fields: [F("ref", "Policy #", "text", { readonly: true, list: true }), F("owner", "Customer", "text", { required: true, list: true }),
    F("product_id", "Insurance Product", "ref:product", { list: true }), F("plan_name", "Plan", "text", { list: true }),
    F("premium", "Premium", "money", { required: true, list: true }), F("currency", "Currency", "text"),
    F("cover", "Cover Amount", "money", { list: true }), F("starts_at", "Starts", "date"), F("ends_at", "Ends", "date"),
    F("nominees", "Nominees", "json"), F("status", "Status", "select", { options: "finInsuranceStatuses", list: true })]
  },
  gift_voucher: {
    table: "gift_vouchers", pk: "id", label: "Gift Vouchers", icon: "🎁", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("code", "Voucher Code", "text", { required: true, list: true }), F("amount", "Face Value", "money", { required: true, list: true }),
    F("currency", "Currency", "text"), F("buyer", "Buyer", "text", { list: true }),
    F("recipient", "Recipient", "text"), F("recipient_email", "Recipient Email", "text"),
    F("message", "Message", "textarea"), F("expires_at", "Expires", "date", { list: true }),
    F("redeemed_at", "Redeemed", "readonly", { list: true }), F("redeemed_by", "Redeemed By", "text"),
    F("status", "Status", "select", { options: "finVoucherStatuses", list: true })]
  },

  /* ---------- Marketplace ---------- */
  seller_onboarding: {
    table: "seller_onboarding", pk: "id", label: "Seller Onboarding", icon: "🧾", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("ref", "Application #", "text", { readonly: true, list: true }), F("seller_id", "Seller", "ref:seller", { list: true }),
    F("business_name", "Business Name", "text", { required: true, list: true }), F("business_type", "Business Type", "select", { options: "mktBusinessTypes", list: true }),
    F("gstin", "GSTIN", "text", { list: true }), F("pan", "PAN", "text"), F("tan", "TAN", "text"),
    F("bank_name", "Bank Name", "text"), F("bank_account", "Bank Account", "text"), F("bank_ifsc", "IFSC", "text"),
    F("docs", "Documents", "json"), F("status", "Status", "select", { options: "mktOnboardingStatuses", list: true }),
    F("submitted_at", "Submitted", "readonly", { list: true }), F("reviewed_at", "Reviewed", "readonly"),
    F("reviewed_by", "Reviewed By", "text"), F("notes", "Notes", "textarea")]
  },
  seller_offer: {
    table: "seller_offers", pk: "id", label: "Seller Offers (Buy-Box)", icon: "🏆", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("product_id", "Product", "ref:product", { required: true, list: true }), F("sku_id", "SKU", "ref:sku"),
    F("seller_id", "Seller", "ref:seller", { required: true, list: true }),
    F("price", "Offer Price", "money", { required: true, list: true }), F("currency", "Currency", "text"),
    F("condition", "Condition", "select", { options: "mktConditions", list: true }),
    F("fulfillment", "Fulfilment", "select", { options: "mktFulfillment", list: true }),
    F("handling_hours", "Handling (hrs)", "number"), F("shipping_days", "Shipping Days", "number", { list: true }),
    F("offer_status", "Status", "select", { options: "mktOfferStatuses", list: true }),
    F("buybox", "Buy-Box Winner", "bool", { list: true }), F("buybox_score", "Buy-Box Score", "number", { list: true })]
  },
  fba_inbound: {
    table: "fba_inbound", pk: "id", label: "FBA Inbound", icon: "📥", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("ref", "Inbound #", "text", { readonly: true, list: true }), F("seller_id", "Seller", "ref:seller", { list: true }),
    F("warehouse_id", "Fulfilment Centre", "ref:warehouse", { list: true }), F("sku_id", "SKU", "ref:sku", { list: true }),
    F("units", "Units", "number", { required: true, list: true }), F("fee", "FBA Fee", "money"),
    F("tracking_ref", "Tracking Ref", "text"), F("received_at", "Received", "readonly", { list: true }),
    F("status", "Status", "select", { options: "mktFbaStatuses", list: true })]
  },
  seller_performance: {
    table: "seller_performance", pk: "id", label: "Seller Performance", icon: "📈", perm: { read: ["admin", "platform"], write: [] },
    fields: [F("seller_id", "Seller", "ref:seller", { required: true, list: true }), F("period", "Period", "text", { required: true, list: true }),
    F("orders", "Orders", "number", { list: true }), F("odr", "ODR %", "number", { list: true }), F("odr_targets", "ODR Count", "number"),
    F("late_ship_rate", "Late Ship %", "number", { list: true }), F("late_shipments", "Late Shipments", "number"),
    F("cancel_rate", "Cancel %", "number", { list: true }), F("cancellations", "Cancellations", "number"),
    F("valid_tracked_rate", "Valid Tracking %", "number"), F("health_score", "Health Score", "number", { list: true }),
    F("tier", "Tier", "select", { options: "mktTiers", list: true }), F("status", "Status", "select", { options: ["computed", "archived"], list: true })]
  },
  buyer_claim: {
    table: "buyer_claims", pk: "id", label: "Buyer Protection Claims", icon: "⚖️", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("ref", "Claim #", "text", { readonly: true, list: true }), F("order_id", "Order", "ref:order", { list: true }),
    F("buyer", "Buyer", "text", { list: true }), F("seller_id", "Seller", "ref:seller", { list: true }),
    F("kind", "Claim Type", "select", { options: "mktClaimKinds", list: true }), F("reason", "Reason", "textarea", { list: true }),
    F("amount", "Claim Amount", "money", { list: true }), F("currency", "Currency", "text"),
    F("evidence", "Evidence", "json"), F("status", "Status", "select", { options: "mktClaimStatuses", list: true }),
    F("resolution", "Resolution", "text"), F("resolved_at", "Resolved", "readonly", { list: true }), F("resolved_by", "Resolved By", "text")]
  },
  smart_fulfilment: {
    table: "smart_fulfilment", pk: "id", label: "Smart Fulfilment", icon: "🎯", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("ref", "Enrolment #", "text", { readonly: true, list: true }), F("seller_id", "Seller", "ref:seller", { list: true }),
    F("grade", "Grade", "select", { options: "mktSmartGrades", list: true }), F("sla_hours", "SLA (hours)", "number", { list: true }),
    F("packed_same_day", "Same-Day Packing", "bool"), F("score", "Quality Score", "number", { list: true }),
    F("status", "Status", "select", { options: "mktSmartStatuses", list: true })]
  },
  sponsored_creative: {
    table: "sponsored_creatives", pk: "id", label: "Sponsored Brands / Display", icon: "📣", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("ad_id", "Sponsored Ad", "ref:ad", { list: true }), F("seller_id", "Seller", "ref:seller", { list: true }),
    F("kind", "Ad Type", "select", { options: "mktAdKinds", list: true }), F("headline", "Headline", "text", { list: true }),
    F("creative", "Creative / Asset", "json"), F("landing", "Landing Page", "text"),
    F("bid_model", "Bid Model", "select", { options: "mktBidModels", list: true }), F("bid_amount", "Bid", "money"),
    F("budget", "Budget", "money", { list: true }), F("spent", "Spent", "money", { list: true }),
    F("status", "Status", "select", { options: "mktCreativeStatuses", list: true }),
    F("start_at", "Starts", "date"), F("end_at", "Ends", "date")]
  },

  /* ---------- B2B trust & trade ---------- */
  trade_assurance: {
    table: "trade_assurance", pk: "id", label: "Trade Assurance", icon: "🛡️", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("ref", "Order #", "text", { readonly: true, list: true }), F("order_id", "Order", "ref:order", { list: true }),
    F("buyer", "Buyer", "text", { list: true }), F("seller", "Seller", "text", { list: true }),
    F("amount", "Order Amount", "money", { required: true, list: true }), F("currency", "Currency", "text"),
    F("fee", "Assurance Fee", "money"), F("milestones", "Milestones", "json"), F("current_milestone", "Current Milestone", "text", { list: true }),
    F("held", "Funds Held", "bool", { list: true }), F("released_at", "Released", "readonly", { list: true }),
    F("status", "Status", "select", { options: "b2bAssuranceStatuses", list: true })]
  },
  gold_supplier: {
    table: "gold_suppliers", pk: "id", label: "Gold Suppliers", icon: "🥇", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("supplier_id", "Supplier", "ref:supplier", { required: true, list: true }),
    F("tier", "Tier", "select", { options: "b2bGoldTiers", list: true }),
    F("starts_at", "Starts", "date", { list: true }), F("ends_at", "Renews", "date", { list: true }),
    F("fee", "Membership Fee", "money"), F("currency", "Currency", "text"),
    F("verified", "Verified", "bool", { list: true }), F("verification_level", "Verification Level", "select", { options: "b2bVerificationLevels", list: true }),
    F("status", "Status", "select", { options: ["active", "expired", "cancelled"], list: true })]
  },
  company_verification: {
    table: "company_verifications", pk: "id", label: "Company Verifications", icon: "✅", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("ref", "Audit #", "text", { readonly: true, list: true }), F("supplier_id", "Supplier", "ref:supplier", { list: true }),
    F("company_name", "Company Name", "text", { required: true, list: true }), F("country", "Country", "text", { list: true }),
    F("registration_no", "Registration No", "text"), F("year_established", "Year Established", "text"),
    F("employees", "Employees", "text"), F("revenue", "Revenue Range", "text"), F("export_share", "Export Share", "text"),
    F("audit_docs", "Audit Documents", "json"), F("audit_by", "Audited By", "text", { list: true }), F("audit_at", "Audit Date", "date"),
    F("verification_status", "Status", "select", { options: "b2bVerificationStatuses", list: true }),
    F("badges", "Badges", "json"), F("notes", "Notes", "textarea")]
  },
  export_document: {
    table: "export_documents", pk: "id", label: "Export / Customs Documents", icon: "📄", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("ref", "Doc #", "text", { readonly: true, list: true }), F("order_id", "Order", "ref:order", { list: true }),
    F("doc_kind", "Document Type", "select", { options: "b2bDocKinds", list: true }),
    F("buyer", "Buyer", "text"), F("consignee", "Consignee", "text"), F("shipper", "Shipper", "text"),
    F("origin_country", "Origin", "text"), F("dest_country", "Destination", "text"),
    F("port_loading", "Port of Loading", "text"), F("port_discharge", "Port of Discharge", "text"),
    F("incoterms", "Incoterms", "select", { options: "incoterms", list: true }),
    F("currency", "Currency", "text"), F("total_value", "Total Value", "money", { list: true }),
    F("hs_codes", "HS Codes", "json"), F("packages", "Packages", "number"),
    F("gross_weight", "Gross Weight", "number"), F("net_weight", "Net Weight", "number"),
    F("marks", "Marks & Numbers", "textarea"), F("body", "Line Items", "json"),
    F("rendered", "Rendered Document", "textarea", { readonly: true }),
    F("status", "Status", "select", { options: "b2bDocStatuses", list: true })]
  },
  letter_of_credit: {
    table: "letters_of_credit", pk: "id", label: "Letters of Credit", icon: "📜", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("ref", "LC #", "text", { readonly: true, list: true }), F("order_id", "Order", "ref:order", { list: true }),
    F("buyer", "Applicant", "text", { list: true }), F("seller", "Beneficiary", "text", { list: true }),
    F("issuing_bank", "Issuing Bank", "text", { list: true }), F("advising_bank", "Advising Bank", "text"),
    F("lc_number", "LC Number", "text", { list: true }), F("amount", "Amount", "money", { required: true, list: true }),
    F("currency", "Currency", "text"), F("issue_date", "Issue Date", "date"), F("expiry_date", "Expiry Date", "date", { list: true }),
    F("port_loading", "Port of Loading", "text"), F("port_discharge", "Port of Discharge", "text"),
    F("latest_shipment", "Latest Shipment", "date"), F("docs_required", "Documents Required", "json"),
    F("status", "Status", "select", { options: "b2bLcStatuses", list: true })]
  },
  rfq_quote: {
    table: "rfq_quotes", pk: "id", label: "RFQ Quotes (Seller Bids)", icon: "💹", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("rfq_id", "RFQ", "ref:rfq", { required: true, list: true }), F("supplier_id", "Supplier", "ref:supplier", { list: true }),
    F("seller_id", "Seller", "ref:seller", { list: true }),
    F("unit_price", "Unit Price", "money", { required: true, list: true }), F("currency", "Currency", "text"),
    F("moq", "MOQ", "number", { list: true }), F("lead_days", "Lead Days", "number", { list: true }),
    F("payment_terms", "Payment Terms", "select", { options: "paymentTerms", list: true }), F("validity_days", "Valid (days)", "number"),
    F("quote_ref", "Quote #", "text"), F("attachments", "Attachments", "json"),
    F("status", "Status", "select", { options: "b2bQuoteStatuses", list: true }), F("rank", "Rank", "number", { list: true })]
  },
  tender_bid: {
    table: "tender_bids", pk: "id", label: "Tender Bids", icon: "🗳️", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("tender_id", "Tender", "ref:tender", { required: true, list: true }), F("bidder", "Bidder", "text", { required: true, list: true }),
    F("amount", "Bid Amount", "money", { required: true, list: true }), F("currency", "Currency", "text"),
    F("terms", "Terms", "textarea"), F("bid_ref", "Bid #", "text"),
    F("attachments", "Attachments", "json"), F("status", "Status", "select", { options: "b2bBidStatuses", list: true }),
    F("rank", "Rank", "number", { list: true })]
  },
  price_list: {
    table: "price_lists", pk: "id", label: "Price Lists", icon: "🏷️", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("name", "Price List Name", "text", { required: true, list: true }), F("currency", "Currency", "text"),
    F("segment", "Segment", "select", { options: "b2bSegments", list: true }),
    F("starts_at", "Starts", "date"), F("ends_at", "Ends", "date"),
    F("status", "Status", "select", { options: ["active", "inactive"], list: true })]
  },
  price_list_item: {
    table: "price_list_items", pk: "id", label: "Price List Items", icon: "📐", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("price_list_id", "Price List", "ref:price_list", { required: true, list: true }),
    F("product_id", "Product", "ref:product", { list: true }), F("sku_id", "SKU", "ref:sku"),
    F("price", "Price", "money", { required: true, list: true }), F("min_qty", "Min Qty", "number", { list: true }), F("max_qty", "Max Qty", "number"),
    F("status", "Status", "select", { options: ["active", "inactive"], list: true })]
  },

  /* ---------- Shopper experience completions ---------- */
  gift_registry: {
    table: "gift_registries", pk: "id", label: "Gift Registries", icon: "🎁", perm: { read: ["admin", "platform"], write: [] },
    fields: [F("ref", "Registry #", "text", { readonly: true, list: true }), F("owner", "Creator", "text", { required: true, list: true }),
    F("name", "Registry Name", "text", { required: true, list: true }), F("event", "Event", "select", { options: "shopEvents", list: true }),
    F("event_date", "Event Date", "date", { list: true }), F("shipping_address", "Shipping Address", "textarea"),
    F("notes", "Notes", "textarea"), F("items", "Wishlist Items", "json"), F("contributors", "Contributors", "json"),
    F("status", "Status", "select", { options: "shopRegistryStatuses", list: true })]
  },
  notification: {
    table: "notifications", pk: "id", label: "Notifications", icon: "🔔", perm: { read: ["admin", "platform"], write: [] },
    fields: [F("owner", "Recipient", "text", { list: true }), F("kind", "Kind", "select", { options: "shopNotifKinds", list: true }),
    F("title", "Title", "text", { required: true, list: true }), F("body", "Body", "textarea"),
    F("link", "Link", "text"), F("read", "Read", "bool", { list: true }), F("meta", "Meta", "json"),
    F("created_at", "When", "readonly", { list: true })]
  },
  compare_list: {
    table: "compare_lists", pk: "id", label: "Compare Lists", icon: "⚖️", perm: { read: ["admin", "platform"], write: [] },
    fields: [F("owner", "Customer", "text", { required: true, list: true }), F("product_ids", "Products", "json"),
    F("created_at", "Created", "readonly", { list: true })]
  },
  invoice_document: {
    table: "invoice_documents", pk: "id", label: "Invoice / Tax Docs", icon: "🧾", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("ref", "Doc #", "text", { readonly: true, list: true }), F("order_id", "Order", "ref:order", { list: true }),
    F("owner", "Customer", "text"), F("doc_kind", "Document Type", "select", { options: "shopDocKinds", list: true }),
    F("invoice_number", "Invoice Number", "text", { list: true }), F("place_of_supply", "Place of Supply", "text"),
    F("gstin", "GSTIN", "text"), F("pan", "PAN", "text"),
    F("taxable", "Taxable", "money", { list: true }), F("tax", "Tax", "money", { list: true }), F("total", "Total", "money", { list: true }),
    F("currency", "Currency", "text"), F("body", "Line Items", "json"),
    F("rendered", "Rendered", "textarea", { readonly: true }), F("status", "Status", "select", { options: "shopDocStatuses", list: true })]
  },
  /* ---- E17 · the mobility universe ---- */
  ride: {
    table: "rides", pk: "id", label: "Rides", icon: "🚗", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("ref", "Reference", "text", { readonly: true, list: true }), F("rider", "Rider", "text", { list: true }),
    F("rider_phone", "Rider phone", "text"), F("pickup", "Pickup", "text", { list: true }), F("dropoff", "Drop-off", "text", { list: true }),
    F("vehicle_kind", "Vehicle", "select", { options: "mobilityVehicleKinds", list: true }), F("driver_id", "Driver", "ref:driver"),
    F("status", "Status", "select", { options: "mobilityRideStatuses", list: true }),
    F("distance_km", "Distance (km)", "number"), F("duration_min", "Duration (min)", "number"),
    F("fare", "Fare", "money", { list: true }), F("surge", "Surge ×", "number", { list: true }),
    F("eta_min", "ETA (min)", "number"), F("payment_method", "Payment", "select", { options: ["cash", "wallet", "card", "upi"], list: true }),
    F("rating", "Rating", "number"), F("note", "Note", "text"),
    F("requested_at", "Requested", "readonly", { list: true })]
  },
  driver: {
    table: "drivers", pk: "id", label: "Drivers", icon: "🧑‍✈️", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("name", "Name", "text", { required: true, list: true }), F("email", "Email", "text", { list: true }),
    F("phone", "Phone", "text"), F("city", "City", "text", { list: true }),
    F("vehicle_kind", "Vehicle", "select", { options: "mobilityVehicleKinds", list: true }), F("plate", "Plate", "text", { list: true }),
    F("license", "Licence", "text"), F("status", "State", "select", { options: ["offline", "online", "busy", "suspended"], list: true }),
    F("rating", "Rating", "number", { list: true }), F("rides_completed", "Rides", "number", { list: true }),
    F("earnings", "Earnings", "money", { list: true }), F("city_latency", "Distance from centre (km)", "number"),
    F("joined_at", "Joined", "readonly", { list: true })]
  },
  vehicle: {
    table: "vehicles", pk: "id", label: "Vehicles", icon: "🚙", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("plate", "Plate", "text", { required: true, list: true }),
    F("kind", "Kind", "select", { options: "mobilityVehicleKinds", list: true }), F("capacity", "Capacity", "number", { list: true }),
    F("status", "Status", "select", { options: ["active", "maintenance", "retired"], list: true }),
    F("odometer", "Odometer (km)", "number"), F("insurance_until", "Insurance until", "date"),
    F("driver_id", "Driver", "ref:driver"), F("created_at", "Added", "readonly", { list: true })]
  },
  surge_zone: {
    table: "surge_zones", pk: "id", label: "Surge Zones", icon: "📈", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("name", "Zone", "text", { required: true, list: true }), F("kind", "Kind", "select", { options: ["geofence", "event", "weather"], list: true }),
    F("multiplier", "Multiplier ×", "number", { list: true }), F("center_lat", "Centre latitude", "number"),
    F("center_lng", "Centre longitude", "number"), F("radius_km", "Radius (km)", "number", { list: true }),
    F("active", "Active", "bool", { list: true }), F("starts_at", "Starts", "date"), F("ends_at", "Ends", "date")]
  },
  /* ---- E18 · the operations universe ---- */
  employee: {
    table: "employees", pk: "id", label: "Employees", icon: "🧑‍💼", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("code", "Code", "text", { readonly: true, list: true }), F("name", "Name", "text", { required: true, list: true }),
    F("email", "Email", "text", { list: true }), F("department", "Department", "text", { list: true }),
    F("designation", "Designation", "text"), F("status", "Status", "select", { options: ["active", "on_leave", "terminated"], list: true }),
    F("base_salary", "Base salary", "money", { list: true }), F("pay_frequency", "Pay frequency", "select", { options: ["monthly", "biweekly", "weekly"], list: true }),
    F("bank_account", "Bank account", "text"), F("tax_id", "Tax ID", "text"),
    F("joined_at", "Joined", "readonly", { list: true })]
  },
  attendance: {
    table: "attendance", pk: "id", label: "Attendance", icon: "🕐", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("employee_id", "Employee", "ref:employee", { required: true, list: true }), F("date", "Date", "date", { required: true, list: true }),
    F("check_in", "Check-in", "text"), F("check_out", "Check-out", "text"),
    F("status", "Status", "select", { options: ["present", "late", "half_day", "absent", "leave"], list: true }),
    F("hours", "Hours", "number", { list: true })]
  },
  payroll_run: {
    table: "payroll_runs", pk: "id", label: "Payroll Runs", icon: "💰", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("period", "Period", "text", { readonly: true, list: true }), F("headcount", "Headcount", "number", { list: true }),
    F("gross", "Gross", "money", { list: true }), F("deductions", "Deductions", "money", { list: true }),
    F("net", "Net", "money", { list: true }), F("status", "Status", "select", { options: ["draft", "approved", "paid"], list: true }),
    F("run_at", "Run at", "readonly", { list: true })]
  },
  purchase_request: {
    table: "purchase_requests", pk: "id", label: "Purchase Requests", icon: "🛒", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("ref", "Reference", "text", { readonly: true, list: true }), F("requested_by", "Requested by", "text", { list: true }),
    F("department", "Department", "text", { list: true }), F("status", "Status", "select", { options: "opsPrStatuses", list: true }),
    F("note", "Note", "text"), F("required_by", "Required by", "date"),
    F("approved_by", "Approved by", "text"), F("approved_at", "Approved at", "readonly")]
  },
  purchase_request_line: {
    table: "purchase_request_lines", pk: "id", label: "Request Lines", icon: "📝", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("request_id", "Request", "ref:purchase_request", { required: true, list: true }),
    F("item", "Item", "text", { required: true, list: true }), F("qty", "Qty", "number", { list: true }),
    F("unit", "Unit", "text"), F("est_unit_cost", "Est. unit cost", "money", { list: true })]
  },
  work_order: {
    table: "work_orders", pk: "id", label: "Work Orders", icon: "🏭", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("ref", "Reference", "text", { readonly: true, list: true }), F("product_id", "Product", "text", { list: true }),
    F("qty", "Qty", "number", { list: true }), F("completed_qty", "Completed", "number", { list: true }),
    F("status", "Status", "select", { options: "opsWoStatuses", list: true }), F("bom", "Bill of materials", "json"),
    F("unit_cost", "Unit cost", "money"), F("planned_start", "Planned start", "date"), F("planned_end", "Planned end", "date"),
    F("completed_at", "Completed", "readonly", { list: true })]
  },
  project: {
    table: "projects", pk: "id", label: "Projects", icon: "📐", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("code", "Code", "text", { readonly: true, list: true }), F("name", "Name", "text", { required: true, list: true }),
    F("owner", "Owner", "text", { list: true }), F("client", "Client", "text"),
    F("budget", "Budget", "money", { list: true }), F("spent", "Spent", "money", { list: true }),
    F("status", "Status", "select", { options: "opsProjectStatuses", list: true }),
    F("start_date", "Start", "date"), F("due_date", "Due", "date", { list: true })]
  },
  task: {
    table: "tasks", pk: "id", label: "Tasks", icon: "✅", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("project_id", "Project", "ref:project", { list: true }), F("title", "Title", "text", { required: true, list: true }),
    F("assignee", "Assignee", "text", { list: true }), F("status", "Status", "select", { options: "opsTaskStatuses", list: true }),
    F("priority", "Priority", "select", { options: ["low", "normal", "high", "urgent"], list: true }),
    F("estimate_hours", "Estimate (h)", "number"), F("logged_hours", "Logged (h)", "number", { list: true }),
    F("due_date", "Due", "date", { list: true })]
  },
  approval: {
    table: "approvals", pk: "id", label: "Approvals", icon: "🖋️", perm: { read: ["admin", "platform"], write: ["admin"] },
    fields: [F("kind", "Kind", "select", { options: "opsApprovalKinds", list: true }), F("ref", "Reference", "text", { list: true }),
    F("requester", "Requester", "text", { list: true }), F("approver", "Approver", "text"),
    F("status", "Status", "select", { options: ["pending", "approved", "rejected"], list: true }),
    F("note", "Note", "text"), F("decided_at", "Decided", "readonly", { list: true })]
  }
};

/* ---- custom entities (fully data-defined, JSON storage) ---- */
function customEntityDefs(tenantId) {
  const rows = all("SELECT key, def FROM entity_defs WHERE scope='platform' OR (scope='tenant' AND tenant_id=?)", tenantId);
  const out = {};
  for (const r of rows) { try { out[r.key] = JSON.parse(r.def); } catch (e) { } }
  return out;
}
/* the commerce layer ships as
   entity data exactly like every other entity; a tenant-defined custom entity of the
   same key wins, so an operator can reshape any domain from Data Studio. */
function allEntities(tenantId) { return { ...ENTITY_DEFS, ...PARITY_DEFS, ...customEntityDefs(tenantId) }; }

function coerce(field, raw) {
  if (field.upper && typeof raw === "string") raw = raw.toUpperCase();
  switch (field.type) {
    case "number": case "money": return raw === "" || raw == null ? null : Number(raw);
    case "bool": return raw === true || raw === 1 || raw === "1" || raw === "true" || raw === "on" ? 1 : 0;
    case "json": case "multi": return typeof raw === "string" ? raw : JSON.stringify(raw == null ? null : raw);
    default: return raw == null ? null : String(raw);
  }
}
function optionValues(name) {
  if (!name) return null;
  const r = get("SELECT items FROM meta_lists WHERE name=?", name);
  if (!r) return null;
  let j; try { j = JSON.parse(r.items); } catch (e) { return null; }
  if (!Array.isArray(j)) return null;
  return j.map(x => x && typeof x === "object" ? (x.key != null ? x.key : x.id != null ? x.id : x.code != null ? x.code : x.value) : x).filter(x => x != null);
}
function validate(def, row, partial) {
  const errs = [];
  for (const f of def.fields) {
    if (f.readonly) continue;
    const v = row[f.key];
    /* a required field must be present and non-empty. On a PARTIAL update (a console edit
       touching a few fields) only the fields the payload actually names are checked — an
       update must not fail on required columns the caller didn't send. On a full create or
       an import, every required field is checked: an empty name, a missing code, a blank
       currency are rejected here as "required" rather than slipping through as an empty
       string that SQLite accepts against NOT NULL (an import's blank cell is "", not NULL). */
    if (f.required && (v == null || v === "")) {
      if (partial && !(f.key in row)) continue;
      errs.push(f.label + " is required"); continue;
    }
    if ((f.type === "number" || f.type === "money") && v != null && v !== "" && isNaN(Number(v))) errs.push(f.label + " must be a number");
    if (f.type === "select") {
      const opts = Array.isArray(f.options) ? f.options : (typeof f.options === "string" && f.options.indexOf(".") < 0 ? optionValues(f.options) : null);
      if (opts && v != null && v !== "" && !opts.includes(v)) errs.push(f.label + " invalid option");
    }
    if (f.type === "json" && typeof v === "string" && v) { try { JSON.parse(v); } catch (e) { errs.push(f.label + " invalid JSON"); } }
  }
  return errs;
}
/* a server-side filter is what makes a large catalogue usable: an entity such as `sku`
   grows past any fixed cap once the corpus is activated (~2,000 SKUs on the flagship),
   so the console and API must be able to ask for "the SKUs of THIS product" and get a
   deterministic answer. `q` is a free-text search over the listed columns; `where` is a
   set of equality predicates on declared fields. Both are parameterized and both are
   whitelisted against the entity's own field list, so nothing arbitrary reaches SQL. */
function listEntities(tenantId, key, opts) {
  opts = opts || {};
  const defs = allEntities(tenantId);
  const def = defs[key];
  if (!def) return null;
  const q = opts.q != null ? String(opts.q).trim() : "";
  const whereRaw = opts.where && typeof opts.where === "object" ? opts.where : {};
  if (def.storage === "json") {
    /* a PLATFORM-LEVEL master (a universe, or any platformOnly/noTenant json entity) is
       inherited by every store: its rows live at tenant 0 and are read with no store
       filter, so the master is reusable everywhere and is never duplicated per store.
       A store-scoped entity keeps its own rows plus any NULL-scoped ones — never
       another store's. This is the read half of "master data has no tenant_id" */
    const scoped = !def.platformOnly && !def.noTenant;
    let rows = all("SELECT * FROM entity_data WHERE entity=?" + (scoped ? " AND (tenant_id=? OR tenant_id IS NULL)" : ""), key, ...(scoped ? [tenantId] : []));
    let out = rows.map(r => ({ id: r.id, ...JSON.parse(r.data || "{}"), created_at: r.created_at }));
    const wkeys = Object.keys(whereRaw);
    if (wkeys.length) out = out.filter(r => wkeys.every(k => String(r[k]) === String(whereRaw[k])));
    if (q) { const cols = def.fields.filter(f => f.list && (f.type === "text" || f.type === "textarea")).map(f => f.key);
      if (cols.length) out = out.filter(r => cols.some(c => String(r[c] || "").toLowerCase().includes(q.toLowerCase()))); }
    return out;
  }
  const fieldCols = def.fields.map(f => (f.col || f.key) + (f.col && f.col !== f.key ? " AS " + f.key : ""));
  if (!def.composite && def.pk && !def.fields.some(f => (f.col || f.key) === def.pk)) fieldCols.unshift(def.pk);
  const cols = fieldCols.join(",");
  let sql = `SELECT ${cols}${def.composite ? `,${def.pk2} as _pk2` : ""} FROM ${def.table}`;
  const args = [];
  const clauses = [];
  if (!def.platformOnly && !def.noTenant) { clauses.push("tenant_id=?"); args.push(tenantId); }
  if (opts.hideDeleted) clauses.push("deleted_at IS NULL");
  /* `where` predicates: only declared fields, always parameterized */
  for (const [k, v] of Object.entries(whereRaw)) {
    const col = def.fields.find(f => f.key === k);
    if (col) { clauses.push((col.col || col.key) + "=?"); args.push(v); }
  }
  /* `q`: LIKE over the text columns the entity marks as list-visible */
  if (q) {
    const textCols = def.fields.filter(f => f.list && (f.type === "text" || f.type === "textarea")).map(f => f.col || f.key);
    if (textCols.length) {
      clauses.push("(" + textCols.map(c => "CAST(" + c + " AS TEXT) LIKE ?").join(" OR ") + ")");
      args.push(...textCols.map(() => "%" + q + "%"));
    }
  }
  if (clauses.length) sql += " WHERE " + clauses.join(" AND ");
  sql += ` ORDER BY ${def.composite ? def.pk : def.pkType === "text" ? def.pk : "id"} DESC`;
  /* a filtered query is answering a specific question, so it may need rows that a capped
     scan would miss; an explicit filter lifts the cap, an unfiltered browse keeps it. */
  const filtered = q || Object.keys(whereRaw).length;
  sql += " LIMIT " + (filtered ? Math.min(5000, Math.max(500, opts.limit || 500)) : 500);
  const rows = all(sql, ...args);
  if (def.composite) rows.forEach(r => { r.id = String(r[def.pk]) + "|" + String(r[def.pk2]); });
  return rows;
}
/* The Global Platform mirror of listEntities. Same definitions, same whitelist, same
   parameterization — never a second copy of the field list. Two differences, both
   structural: (1) tenant_id is SELECTed and stamped onto every row so the global console
   can render a Store column, and (2) the tenant predicate is optional, so the platform
   reads *across* stores by default and narrows to one store only when asked. This single
   reader is what makes every entity-backed store capability visible in the Platform
   Console with zero per-capability code (Knowledge-Once). */
function listEntitiesGlobal(key, opts) {
  opts = opts || {};
  const tenantId = opts.tenantId != null ? Number(opts.tenantId) : null;
  const defs = allEntities(tenantId);
  const def = defs[key];
  if (!def) return null;
  const q = opts.q != null ? String(opts.q).trim() : "";
  const whereRaw = opts.where && typeof opts.where === "object" ? { ...opts.where } : {};
  delete whereRaw.tenant_id;
  const multi = !def.platformOnly && !def.noTenant;
  if (def.storage === "json") {
    let rows = all("SELECT * FROM entity_data WHERE entity=? " + (multi ? "AND (tenant_id IS NOT NULL" + (tenantId != null ? " AND tenant_id=?" : "") + ")" : ""), key, ...(multi && tenantId != null ? [tenantId] : []));
    let out = rows.map(r => ({ id: r.id, ...(multi ? { tenant_id: r.tenant_id } : {}), ...JSON.parse(r.data || "{}"), created_at: r.created_at }));
    const wkeys = Object.keys(whereRaw);
    if (wkeys.length) out = out.filter(r => wkeys.every(k => String(r[k]) === String(whereRaw[k])));
    if (q) { const cols = def.fields.filter(f => f.list && (f.type === "text" || f.type === "textarea")).map(f => f.key);
      if (cols.length) out = out.filter(r => cols.some(c => String(r[c] || "").toLowerCase().includes(q.toLowerCase()))); }
    return out;
  }
  const fieldCols = multi ? ["tenant_id"] : [];
  fieldCols.push(...def.fields.map(f => (f.col || f.key) + (f.col && f.col !== f.key ? " AS " + f.key : "")));
  if (!def.composite && def.pk && !def.fields.some(f => (f.col || f.key) === def.pk)) fieldCols.unshift(def.pk);
  const cols = fieldCols.join(",");
  const orderKey = def.composite ? def.pk : def.pkType === "text" ? def.pk : "id";
  /* one shared, parameterized query builder — the filtered and the per-store browse paths
     below resolve to the same SQL, so the whitelist is never duplicated */
  const fetch = (tid, limit) => {
    let sql = `SELECT ${cols}${def.composite ? `,${def.pk2} as _pk2` : ""} FROM ${def.table}`;
    const args = [];
    const clauses = [];
    if (multi && tid != null) { clauses.push("tenant_id=?"); args.push(tid); }
    if (opts.hideDeleted) clauses.push("deleted_at IS NULL");
    for (const [k, v] of Object.entries(whereRaw)) {
      const col = def.fields.find(f => f.key === k);
      if (col) { clauses.push((col.col || col.key) + "=?"); args.push(v); }
    }
    if (q) {
      const textCols = def.fields.filter(f => f.list && (f.type === "text" || f.type === "textarea")).map(f => f.col || f.key);
      if (textCols.length) {
        clauses.push("(" + textCols.map(c => "CAST(" + c + " AS TEXT) LIKE ?").join(" OR ") + ")");
        args.push(...textCols.map(() => "%" + q + "%"));
      }
    }
    if (clauses.length) sql += " WHERE " + clauses.join(" AND ");
    sql += ` ORDER BY ${orderKey} DESC LIMIT ${limit}`;
    return all(sql, ...args);
  };
  const filtered = q || Object.keys(whereRaw).length;
  /* a *global* browse must represent every store: bounding per store (not globally) keeps
     a large catalogue from crowding the other stores out of the platform view. A filtered
     query is answering one specific question, so it scans across stores under one cap. */
  if (multi && tenantId == null && !filtered) {
    const tids = all("SELECT id FROM tenants ORDER BY id").map(r => r.id);
    const per = Math.max(25, Math.min(500, Math.ceil((opts.limit || 500) / Math.max(1, tids.length))));
    let rows = [];
    for (const tid of tids) rows = rows.concat(fetch(tid, per));
    if (def.composite) rows.forEach(r => { r.id = String(r[def.pk]) + "|" + String(r[def.pk2]); });
    return rows;
  }
  const limit = (filtered || tenantId != null) ? Math.min(5000, Math.max(500, opts.limit || 500)) : 500;
  const rows = fetch(tenantId, limit);
  if (def.composite) rows.forEach(r => { r.id = String(r[def.pk]) + "|" + String(r[def.pk2]); });
  return rows;
}
/* Generate structured Universal ID (UID)
 format: PREFIX-TENANT-SEC-UNIQUE
 Example: TXN-LX01-P2-a1b2c3d4e5f6g7h8 */
function generateUID(tenant, prefix, security = 'P2') {
  const unique = crypto.randomBytes(8).toString('hex');
  return `${prefix}-${tenant}-${security}-${unique}`;
}
function createEntity(tenantId, key, row) {
  const def = allEntities(tenantId)[key];
  if (!def) return { error: "Unknown entity" };
  const errs = validate(def, row);
  if (errs.length) return { error: errs.join("; ") };
  if (def.storage === "json") {
    const r = run("INSERT INTO entity_data(tenant_id,entity,data) VALUES(?,?,?)", tenantId, key, JSON.stringify(row));
    return { id: Number(r.lastInsertRowid) };
  }
  const cols = def.noTenant ? [] : ["tenant_id"], vals = def.noTenant ? [] : [tenantId];
  if (def.pkType === "text" || def.composite) {
    if (!row[def.pk]) { 
      if (def.composite) return { error: "Composite key required" }; 
      // Generate UID if uid field exists in entity
      if (def.fields.some(f => f.key === 'uid')) {
        const prefix = def.table === "products" ? "PROD" : def.table === "orders" ? "ORD" : 
                       def.table === "users" ? "USR" : def.table === "invoices" ? "INV" : "ENT";
        const sec = def.sec || 'P2';
        row[def.pk] = generateUID(String(tenantId), prefix, sec);
      } else {
        row[def.pk] = (def.table === "products" ? "LX" : "K") + crypto.randomBytes(4).toString("hex").toUpperCase();
      }
    }
    cols.push(def.pk); vals.push(String(row[def.pk]));
  }
  for (const f of def.fields) {
    if (f.readonly || f.key === def.pk) continue;
    if (row[f.key] !== undefined) { cols.push(f.col || f.key); vals.push(coerce(f, row[f.key])); }
  }
  /* an operator-authored row is owned outright: the seed never rewrites it */
  if (def.editedStamp) { cols.push("edited"); vals.push(1); }
  const ph = cols.map(() => "?").join(",");
  try { run(`INSERT INTO ${def.table}(${cols.join(",")}) VALUES(${ph})`, ...vals); }
  /* an import's bad row must be REPORTED, not fatal. Any integrity error — a NOT NULL the
     console's field list doesn't mirror, a FK the DB enforces but the form can't express —
     becomes a per-row rejection so the good rows still land and the caller sees which row
     failed and why. Throwing here would abort the whole request over one row (import rolled
     back every good record with it) */
  catch (e) {
    if (/UNIQUE/.test(e.message)) return { error: "Record already exists (duplicate key)" };
    if (/(NOT NULL|FOREIGN KEY|CHECK|CONSTRAINT)/i.test(e.message)) return { error: e.message.replace(/^Error: /, "") };
    throw e;
  }
  propagate(key);
  return { id: def.composite ? row[def.pk] + "|" + row[def.pk2] : (def.pkType === "text" ? row[def.pk] : "created") };
}
/* the write path is where a registry entry becomes live everywhere it is needed. Adding a
   country in Country Master used to stop at the `countries` row: its currency, FX quote and
   availability links to every global provider appeared only on the next boot. Reconciling
   here is what makes "add it and it is everywhere" true at the moment of the write.
   Guarded per-key and fault-tolerant — a reconciliation failure must never block the write
   itself, which already succeeded; the next boot reconciles again. */
function propagate(key) {
  try {
    if (key === "country" || key === "currency" || key === "provider_def" || key === "provider_availability")
      require("./registry.js").reconcileDerived();
    /* a link IS the relationship primitive: writing or removing one must re-derive the product
       projection the storefront reads, or an edge created in the platform console appears only
       after a restart. reconcileLinks is idempotent and handles both directions, so this is safe
       on a warm DB and costs a few writes on a cold one. */
    if (key === "link") require("./registry.js").reconcileLinks();
  } catch (e) { console.error("entity reconcile failed:", e.message); }
}
function updateEntity(tenantId, key, id, row) {
  const def = allEntities(tenantId)[key];
  if (!def) return { error: "Unknown entity" };
  const errs = validate(def, row, true);
  if (errs.length) return { error: errs.join("; ") };
  if (def.storage === "json") {
    const ex = get("SELECT * FROM entity_data WHERE id=? AND entity=?", Number(id), key);
    if (!ex) return { error: "Not found", code: 404 };
    run("UPDATE entity_data SET data=? WHERE id=?", JSON.stringify({ ...JSON.parse(ex.data || "{}"), ...row }), Number(id));
    return { ok: true };
  }
  const sets = [], vals = [];
  for (const f of def.fields) {
    if (f.readonly || row[f.key] === undefined) continue;
    sets.push((f.col || f.key) + "=?"); vals.push(coerce(f, row[f.key]));
  }
  /* a console write claims the row: revisioned seeds read `edited` and stand down */
  if (def.editedStamp) sets.push("edited=1");
  if (!sets.length) return { ok: true };
  const where = (def.platformOnly || def.noTenant) ? "" : "tenant_id=? AND ";
  const wargs = (def.platformOnly || def.noTenant) ? [] : [tenantId];
  const pkCond = def.composite ? `${def.pk}=? AND ${def.pk2}=?` : `${def.pk}=?`;
  const pkVals = def.composite ? String(id).split("|") : [def.pkType === "text" ? String(id) : Number(id)];
  const r = run(`UPDATE ${def.table} SET ${sets.join(",")} WHERE ${where}${pkCond}`, ...vals, ...wargs, ...pkVals);
  if (!r.changes) return { error: "Not found", code: 404 };
  propagate(key);
  return { ok: true };
}
function deleteEntity(tenantId, key, id) {
  const def = allEntities(tenantId)[key];
  if (!def) return { error: "Unknown entity" };
  if (def.storage === "json") { run("DELETE FROM entity_data WHERE id=? AND entity=?", Number(id), key); return { ok: true }; }
  const where = (def.platformOnly || def.noTenant) ? "" : "tenant_id=? AND ";
  const wargs = (def.platformOnly || def.noTenant) ? [] : [tenantId];
  const pkCond = def.composite ? `${def.pk}=? AND ${def.pk2}=?` : `${def.pk}=?`;
  const pkVals = def.composite ? String(id).split("|") : [def.pkType === "text" ? String(id) : Number(id)];
  run(`DELETE FROM ${def.table} WHERE ${where}${pkCond}`, ...wargs, ...pkVals);
  propagate(key);
  return { ok: true };
}

module.exports = { ENTITY_DEFS, allEntities, customEntityDefs, listEntities, listEntitiesGlobal, createEntity, updateEntity, deleteEntity, validate, coerce };
