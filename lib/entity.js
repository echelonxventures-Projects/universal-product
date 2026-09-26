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
    F("tax_mode", "Default Tax Mode", "ref:tax_mode", { list: true }), F("tax_rate", "Default Tax Rate", "number"), F("position", "Position", "number")]
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
  meta_list: {
    table: "meta_lists", noTenant: true, pk: "name", pkType: "text", label: "Registries (lists)", icon: "📚", perm: { read: ["platform"], write: ["platform"] }, platformOnly: true,
    fields: [F("name", "Name", "text", { required: true, list: true }), F("label", "Label", "text"), F("items", "Items (JSON)", "json", { required: true })]
  },
  tax_mode: {
    table: "tax_modes", noTenant: true, pk: "key", pkType: "text", label: "Tax Modes", icon: "🧾", perm: { read: ["platform"], write: ["platform"] }, platformOnly: true,
    fields: [F("key", "Key", "text", { required: true, list: true }), F("label", "Label", "text", { required: true, list: true }),
    F("description", "Description", "text"), F("fields", "Extra Fields", "json"), F("position", "Position", "number")]
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
      F("brand", "Brand", "text", { required: true, list: true }), F("dept", "Department", "ref:department", { list: true }),
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
      F("supplier_id", "Marketplace Seller", "ref:seller")
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
    F("state", "State", "text"), F("zip", "ZIP", "text"), F("country", "Country", "text"),
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

/* ---- custom entities (fully data-defined, JSON storage) ---- */
function customEntityDefs(tenantId) {
  const rows = all("SELECT key, def FROM entity_defs WHERE scope='platform' OR (scope='tenant' AND tenant_id=?)", tenantId);
  const out = {};
  for (const r of rows) { try { out[r.key] = JSON.parse(r.def); } catch (e) { } }
  return out;
}
function allEntities(tenantId) { return { ...ENTITY_DEFS, ...customEntityDefs(tenantId) }; }

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
    if (f.required && (v == null || v === "")) { if (!partial || !(f.key in row)) continue; errs.push(f.label + " is required"); continue; }
    if ((f.type === "number" || f.type === "money") && v != null && v !== "" && isNaN(Number(v))) errs.push(f.label + " must be a number");
    if (f.type === "select") {
      const opts = Array.isArray(f.options) ? f.options : (typeof f.options === "string" && f.options.indexOf(".") < 0 ? optionValues(f.options) : null);
      if (opts && v != null && v !== "" && !opts.includes(v)) errs.push(f.label + " invalid option");
    }
    if (f.type === "json" && typeof v === "string" && v) { try { JSON.parse(v); } catch (e) { errs.push(f.label + " invalid JSON"); } }
  }
  return errs;
}
function listEntities(tenantId, key, opts) {
  opts = opts || {};
  const defs = allEntities(tenantId);
  const def = defs[key];
  if (!def) return null;
  if (def.storage === "json") {
    let rows = all("SELECT * FROM entity_data WHERE entity=? AND (tenant_id=? OR tenant_id IS NULL)", key, tenantId);
    return rows.map(r => ({ id: r.id, ...JSON.parse(r.data || "{}"), created_at: r.created_at }));
  }
  const fieldCols = def.fields.map(f => (f.col || f.key) + (f.col && f.col !== f.key ? " AS " + f.key : ""));
  if (!def.composite && def.pk && !def.fields.some(f => (f.col || f.key) === def.pk)) fieldCols.unshift(def.pk);
  const cols = fieldCols.join(",");
  let sql = `SELECT ${cols}${def.composite ? `,${def.pk2} as _pk2` : ""} FROM ${def.table}`;
  const args = [];
  const clauses = [];
  if (!def.platformOnly && !def.noTenant) { clauses.push("tenant_id=?"); args.push(tenantId); }
  if (opts.hideDeleted) clauses.push("deleted_at IS NULL");
  if (clauses.length) sql += " WHERE " + clauses.join(" AND ");
  sql += ` ORDER BY ${def.composite ? def.pk : def.pkType === "text" ? def.pk : "id"} DESC LIMIT 500`;
  const rows = all(sql, ...args);
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
  const ph = cols.map(() => "?").join(",");
  try { run(`INSERT INTO ${def.table}(${cols.join(",")}) VALUES(${ph})`, ...vals); }
  catch (e) { if (/UNIQUE/.test(e.message)) return { error: "Record already exists (duplicate key)" }; throw e; }
  return { id: def.composite ? row[def.pk] + "|" + row[def.pk2] : (def.pkType === "text" ? row[def.pk] : "created") };
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
  if (!sets.length) return { ok: true };
  const where = (def.platformOnly || def.noTenant) ? "" : "tenant_id=? AND ";
  const wargs = (def.platformOnly || def.noTenant) ? [] : [tenantId];
  const pkCond = def.composite ? `${def.pk}=? AND ${def.pk2}=?` : `${def.pk}=?`;
  const pkVals = def.composite ? String(id).split("|") : [def.pkType === "text" ? String(id) : Number(id)];
  const r = run(`UPDATE ${def.table} SET ${sets.join(",")} WHERE ${where}${pkCond}`, ...vals, ...wargs, ...pkVals);
  if (!r.changes) return { error: "Not found", code: 404 };
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
  return { ok: true };
}

module.exports = { ENTITY_DEFS, allEntities, customEntityDefs, listEntities, createEntity, updateEntity, deleteEntity, validate, coerce };
