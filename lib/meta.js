/* LUXORA Platform - Universal Commerce Meta Model registries.
   Everything here is DATA. Tenants may override/extend via DB (custom registries). */
"use strict";

const INDUSTRIES = [
  { key: "retail", name: "Retail & Consumer", icon: "🛍️" },
  { key: "grocery", name: "Food & Grocery", icon: "🥦" },
  { key: "fashion", name: "Fashion & Apparel", icon: "👗" },
  { key: "furniture", name: "Furniture & Home", icon: "🛋️" },
  { key: "construction", name: "Construction & Hardware", icon: "🔩" },
  { key: "industrial", name: "Industrial & Manufacturing", icon: "🏭" },
  { key: "automotive", name: "Automotive", icon: "🚗" },
  { key: "agriculture", name: "Agriculture", icon: "🌾" },
  { key: "healthcare", name: "Healthcare", icon: "🏥" },
  { key: "pharma", name: "Pharmaceuticals", icon: "💊" },
  { key: "electronics", name: "Electronics", icon: "📺" },
  { key: "telecom", name: "Telecommunications", icon: "📡" },
  { key: "energy", name: "Energy", icon: "⚡" },
  { key: "chemicals", name: "Chemicals", icon: "🧪" },
  { key: "education", name: "Education", icon: "🎓" },
  { key: "media", name: "Books & Media", icon: "📚" },
  { key: "digital", name: "Digital Products", icon: "💾", purchase: "download" },
  { key: "software", name: "Software", icon: "🧩" },
  { key: "services", name: "Professional Services", icon: "🼻" },
  { key: "travel", name: "Travel", icon: "✈️" },
  { key: "realestate", name: "Real Estate", icon: "🏢" },
  { key: "finance", name: "Financial Products", icon: "📈" },
  { key: "rental", name: "Rental Assets", icon: "🔑", purchase: "rent" },
  { key: "subscription", name: "Subscription Products", icon: "🔁", purchase: "subscribe" },
  { key: "gov", name: "Government Procurement", icon: "🏛️" },
  { key: "defense", name: "Defense & Aerospace", icon: "🛰️" },
  { key: "marine", name: "Marine", icon: "🚢" },
  { key: "mining", name: "Mining", icon: "⛏️" },
  { key: "luxury", name: "Luxury Goods", icon: "💎" },
  { key: "art", name: "Art & Collectibles", icon: "🎨" },
  { key: "pets", name: "Pets & Veterinary", icon: "🐾" },
  { key: "sports", name: "Sports & Fitness", icon: "🏋️" },
  { key: "jewellery", name: "Jewellery & Precious Metals", icon: "💍" }
];

const PRODUCT_TYPES = [
  { key: "physical", name: "Physical Product", icon: "📦", plain: true },
  { key: "digital", name: "Digital Product", icon: "💿" },
  { key: "service", name: "Service", icon: "🛠️", service: true, purchase: "book" },
  { key: "rental", name: "Rental Asset", icon: "🔑" },
  { key: "subscription", name: "Subscription", icon: "🔁" },
  { key: "bundle", name: "Bundle", icon: "🎁" },
  { key: "kit", name: "Kit", icon: "🧰" },
  { key: "package", name: "Package", icon: "🗃️" },
  { key: "membership", name: "Membership", icon: "🎟️" },
  { key: "warranty", name: "Warranty", icon: "🛡️" },
  { key: "insurance", name: "Insurance", icon: "☂️" },
  { key: "license", name: "License", icon: "📜", purchase: "download" },
  { key: "course", name: "Course", icon: "🎓", purchase: "download" },
  { key: "appointment", name: "Appointment", icon: "📅", purchase: "book" },
  { key: "event_ticket", name: "Event Ticket", icon: "🎫" },
  { key: "vehicle", name: "Vehicle", icon: "🚙" },
  { key: "property", name: "Property", icon: "🏠" },
  { key: "equipment", name: "Equipment", icon: "⚙️" },
  { key: "resource", name: "Resource", icon: "🌐" },
  { key: "consumable", name: "Consumable", icon: "🧻" },
  { key: "raw_material", name: "Raw Material", icon: "🪨" },
  { key: "semi_finished", name: "Semi Finished Good", icon: "🔗" },
  { key: "finished_good", name: "Finished Good", icon: "✅" }
];

const LIFECYCLE = ["draft", "review", "approved", "published", "suspended", "discontinued", "archived"];
const LIFECYCLE_TRANSITIONS = {
  draft: ["review"], review: ["approved", "draft"], approved: ["published", "review"],
  published: ["suspended", "discontinued"], suspended: ["published", "archived"],
  discontinued: ["archived"], archived: []
};
const REL_TYPES = [
  { key: "parent", name: "Parent Product" }, { key: "variant", name: "Variant" },
  { key: "accessory", name: "Accessory" }, { key: "replacement", name: "Replacement" },
  { key: "cross_sell", name: "Cross Sell" }, { key: "upsell", name: "Upsell" },
  { key: "bundle", name: "Bundle" }, { key: "kit", name: "Kit" },
  { key: "compatible", name: "Compatible" }, { key: "alternative", name: "Alternative" },
  { key: "spare_part", name: "Spare Part" }
];
const MEDIA_KINDS = [
  { key: "image", name: "Image" }, { key: "video", name: "Video", player: "video" }, { key: "image360", name: "360° Image" },
  { key: "model3d", name: "3D Model" }, { key: "model_ar", name: "AR Model" }, { key: "cad", name: "CAD File" },
  { key: "pdf", name: "PDF" }, { key: "manual", name: "Instruction Manual" }, { key: "msds", name: "MSDS" },
  { key: "certificate", name: "Certificate" }, { key: "warranty_doc", name: "Warranty Document" }
];
const PACKAGING_LEVELS = [
  { key: "primary", name: "Primary Packaging", eg: "Bottle" }, { key: "secondary", name: "Secondary", eg: "Case" },
  { key: "tertiary", name: "Tertiary", eg: "Carton" }, { key: "pallet", name: "Pallet", eg: "Pallet" }
];
const UOM_UNITS = [
  { key: "ea", name: "Each / Count", dim: "count" }, { key: "g", name: "Gram", dim: "weight" }, { key: "kg", name: "Kilogram", dim: "weight" }, { key: "lb", name: "Pound", dim: "weight" }, { key: "t", name: "Tonne", dim: "weight" },
  { key: "ml", name: "Millilitre", dim: "volume" }, { key: "l", name: "Litre", dim: "volume" }, { key: "m3", name: "Cubic metre", dim: "volume" }, { key: "ft3", name: "Cubic foot", dim: "volume" },
  { key: "mm", name: "Millimetre", dim: "length" }, { key: "cm", name: "Centimetre", dim: "length" }, { key: "m", name: "Metre", dim: "length" }, { key: "in", name: "Inch", dim: "length" }, { key: "ft", name: "Foot", dim: "length" },
  { key: "m2", name: "Square metre", dim: "area" }, { key: "ft2", name: "Square foot", dim: "area" },
  { key: "sec", name: "Second", dim: "time" }, { key: "min", name: "Minute", dim: "time" }, { key: "hr", name: "Hour", dim: "time" }, { key: "day", name: "Day", dim: "time" }, { key: "month", name: "Month", dim: "time" },
  { key: "w", name: "Watt", dim: "power" }, { key: "kw", name: "Kilowatt", dim: "power" }, { key: "kwh", name: "Kilowatt-hour", dim: "energy" },
  { key: "pa", name: "Pascal", dim: "pressure" }, { key: "bar", name: "Bar", dim: "pressure" }, { key: "psi", name: "PSI", dim: "pressure" },
  { key: "c", name: "°Celsius", dim: "temperature" }, { key: "f", name: "°Fahrenheit", dim: "temperature" },
  { key: "mps", name: "m/s", dim: "speed" }, { key: "kmh", name: "km/h", dim: "speed" }, { key: "currency", name: "Money", dim: "currency" }, { key: "pair", name: "Pair", dim: "count" }, { key: "set", name: "Set", dim: "count" }, { key: "dozen", name: "Dozen", dim: "count" }
];
const UOM_CONVERSIONS = { "g→kg": 1000, "ml→l": 1000, "mm→cm": 10, "cm→m": 100, "mm→m": 1000, "in→cm": 2.54, "ft→m": 0.3048, "lb→kg": 0.4536, "ft2→m2": 0.0929, "ft3→m3": 0.0283, "min→hr": 60, "hr→day": 24, "day→month": 30, "w→kw": 1000, "bar→pa": 100000, "psi→bar": 0.0689, "dozen→ea": 12 };
const SELLER_ROLES = ["manufacturer", "distributor", "wholesaler", "retailer", "dropshipper", "franchise", "marketplace_seller", "importer", "exporter"];
const PROMO_TYPES = [
  { key: "percent", name: "% off" }, { key: "fixed", name: "Fixed amount off" }, { key: "bogo", name: "Buy X Get Y" },
  { key: "free_ship", name: "Free shipping" }, { key: "bundle_price", name: "Bundle price" }, { key: "tier_qty", name: "Quantity tier" }
];
const IDENTITY_FIELDS = ["sku", "gtin", "upc", "ean", "isbn", "issn", "mpn", "oem", "part_number", "vin", "imei", "serial", "batch", "lot", "hsn", "hs_code", "unspsc", "gs1_gpc", "eclas", "etim"];
/* a class that costs extra declares the logistics-guard setting that prices it (`surcharge`)
   and that setting's default */
const SHIPPING_CLASSES = ["standard", "dangerous_goods", "cold_chain", "heavy", "white_glove", "install_required", "cross_border_restricted", "fragile", "oversized"]
  .map(k => ({ key: k, name: k }));
SHIPPING_CLASSES.find(c => c.key === "standard").default = true;
Object.assign(SHIPPING_CLASSES.find(c => c.key === "cold_chain"), { surcharge: "coldFee", surcharge_default: 6.5 });
Object.assign(SHIPPING_CLASSES.find(c => c.key === "dangerous_goods"), { surcharge: "hazmatFee", surcharge_default: 12 });
/* the context groups a checkout line may carry (verticalContexts' keys), with their labels */
const CONTEXT_GROUPS = [{ key: "tax", name: "Tax treatment" }, { key: "invoice", name: "Invoice type" }, { key: "payment", name: "Payment mode" }];
/* ---- universal-model registries (all editable at runtime via meta_lists) ---- */
const SERIALIZED_STATUSES = ["in_stock", "allocated", "shipped", "delivered", "returned", "repaired", "quarantined", "lost", "retired"];
const SERIALIZED_CONDITIONS = ["new", "refurbished", "used", "damaged"];
const VARIANT_AXES = ["General", "Size", "Colour", "Material", "Storage", "Capacity", "Configuration", "Flavour", "Grade", "Bundle"];
const COMPLIANCE_SCOPES = ["product", "sku", "seller", "tenant"];
const COMPLIANCE_KINDS = ["certificate", "license", "approval", "authorization", "permit", "registration", "mark"];
const COMPLIANCE_STATUSES = ["valid", "expired", "pending", "revoked", "withdrawn"];
const SUPPLIER_ROLES = ["manufacturer", "distributor", "wholesaler", "importer", "exporter", "logistics", "service", "raw_material"];
const SUPPLIER_STATUSES = ["active", "suspended", "trial"];
const PAYMENT_TERMS = ["prepaid", "cod", "net15", "net30", "net45", "net60"];
const INCOTERMS = ["EXW", "FOB", "CIF", "DDP"];
const LOCALIZATION_ENTITIES = ["product", "sku", "taxonomy", "banner", "card"];
const CONTRACT_STATUSES = ["draft", "active", "expired", "terminated"];
const TENDER_STATUSES = ["open", "in_review", "awarded", "rejected", "cancelled"];
const LINK_STATUSES = ["active", "inactive"];

/* vertical commerce profiles: field schemas rendered dynamically per industry */
const F = (key, label, type, opts) => ({ key, label, type, ...(opts || {}) });
const VERTICALS = {
  grocery: { name: "Grocery Commerce", fields: [F("expiry_date", "Expiry Date", "date"), F("mfg_date", "Manufacturing Date", "date"), F("best_before", "Best Before", "text"), F("storage", "Storage Conditions", "text"), F("temp_min", "Min Temp (°C)", "number"), F("temp_max", "Max Temp (°C)", "number"), F("lot_tracked", "Lot Tracking", "bool"), F("batch_tracked", "Batch Tracking", "bool"), F("nutrition", "Nutritional Info (per 100g)", "json"), F("ingredients", "Ingredients", "text"), F("allergens", "Allergens", "multi", { options: ["milk", "nuts", "soy", "gluten", "eggs", "shellfish", "sesame"] }), F("origin", "Country of Origin", "text"), F("fssai", "FSSAI / Food License", "text"), F("organic_cert", "Organic Certification", "text")] },
  furniture: { name: "Furniture Commerce", fields: [F("material", "Primary Material", "text"), F("dimensions", "Dimensions (L×W×H cm)", "text"), F("weight_kg", "Weight (kg)", "number"), F("assembly_required", "Assembly Required", "bool"), F("assembly_doc", "Assembly Instructions", "media"), F("room", "Room", "select", { options: ["living", "bedroom", "office", "dining", "outdoor", "kids"] }), F("swatches", "Colour Swatches", "multi"), F("wood_type", "Wood Type", "text"), F("fabric_type", "Fabric Type", "text"), F("spare_parts", "Replacement Parts Available", "bool"), F("assembly_service", "Assembly Service", "bool"), F("install_service", "Installation Service", "bool")] },
  hardware: { name: "Hardware Commerce", fields: [F("thread_size", "Thread Size", "text"), F("diameter_mm", "Diameter (mm)", "number"), F("length_mm", "Length (mm)", "number"), F("material_grade", "Material Grade", "text"), F("tolerance", "Tolerance", "text"), F("finish", "Finish", "text"), F("load_capacity", "Load Capacity", "text"), F("torque", "Torque Rating", "text"), F("pressure_rating", "Pressure Rating", "text"), F("compat_matrix", "Compatibility Matrix", "json")] },
  construction: { name: "Construction Materials", fields: [F("coverage_area", "Area Coverage (m²/unit)", "number"), F("coverage_volume", "Volume Coverage (m³/unit)", "number"), F("weight", "Unit Weight", "text"), F("pallet_qty", "Pallet Quantity", "number"), F("hazard_class", "Hazard Class", "text"), F("fire_rating", "Fire Rating", "text"), F("structural_rating", "Structural Rating", "text"), F("install_guide", "Installation Guide", "media"), F("safety_doc", "Safety Documents", "media")] },
  automotive: { name: "Automotive Commerce", fields: [F("makes", "Vehicle Makes", "multi"), F("models", "Models", "text"), F("years", "Year Range", "text"), F("engine", "Engine Type", "text"), F("fuel", "Fuel Type", "select", { options: ["petrol", "diesel", "ev", "hybrid", "cng"] }), F("vin_mapping", "VIN Mapping", "text"), F("oem_ref", "OEM Reference", "text"), F("fitment", "Part Compatibility", "json"), F("labor_hours", "Installation Labor (hrs)", "number")] },
  industrial: { name: "Industrial Commerce", fields: [F("tech_specs", "Technical Specifications", "json"), F("maintenance", "Maintenance Schedule", "text"), F("calibration", "Calibration Records", "media"), F("compliance_docs", "Compliance Documents", "media"), F("safety_sheet", "Safety Sheet (MSDS)", "media"), F("install_service", "Installation Service", "bool"), F("amc", "AMC Contract Available", "bool"), F("warranty_contract", "Warranty Contract", "bool")] },
  electronics: { name: "Electronics Commerce", fields: [F("imei_required", "IMEI Tracked", "bool"), F("serial_required", "Serial Tracked", "bool"), F("firmware", "Firmware Version", "text"), F("warranty_months", "Warranty (months)", "number"), F("repair_coverage", "Repair Coverage", "text"), F("voltage", "Voltage (V)", "text"), F("power_w", "Power Rating (W)", "number"), F("energy_rating", "Energy Rating", "select", { options: ["A+++", "A++", "A+", "A", "B", "C"] }), F("compat_matrix", "Compatibility Matrix", "json")] },
  medical: { name: "Medical / Pharma", fields: [F("lot_tracked", "Lot Tracking", "bool"), F("serial_tracked", "Serial Tracking", "bool"), F("udi", "UDI Code", "text"), F("regulatory", "Regulatory Approval", "text"), F("expiry_tracked", "Expiry Tracking", "bool"), F("storage_compliance", "Storage Compliance", "text"), F("prescription", "Prescription Required", "bool"), F("audit_trail", "Audit Trail Required", "bool")] },
  chemicals: { name: "Chemical Commerce", fields: [F("cas_number", "CAS Number", "text"), F("hazard_class", "Hazard Classification", "text"), F("msds", "MSDS Attached", "media"), F("storage", "Storage Conditions", "text"), F("transport", "Transport Restrictions", "text"), F("env_compliance", "Environmental Compliance", "text")] },
  agriculture: { name: "Agriculture Commerce", fields: [F("crop", "Crop", "text"), F("season", "Seasonality", "multi", { options: ["kharif", "rabi", "zaid", "all-season"] }), F("soil", "Soil Compatibility", "text"), F("climate", "Climate Zone", "text"), F("seed_cert", "Seed Certification", "text"), F("pesticide_class", "Pesticide Classification", "text")] },
  jewellery: { name: "Jewellery Commerce", fields: [F("purity", "Purity (K / %)", "text"), F("hallmark", "Hallmark", "text"), F("stone_cert", "Stone Certification", "media"), F("weight_g", "Net Weight (g)", "number"), F("making_charges_pct", "Making Charges (%)", "number"), F("live_pricing", "Live Commodity Pricing", "bool"), F("metal", "Metal", "select", { options: ["gold", "silver", "platinum", "palladium"] })] },
  digital: { name: "Digital Product", fields: [F("license_key", "License Key Issued", "bool"), F("activation", "Activation Rules", "text"), F("downloads", "Download Entitlements", "number"), F("streaming", "Streaming Rights", "text"), F("drm", "DRM", "select", { options: ["none", "widevine", "fairplay", "custom"] }), F("sub_rules", "Subscription Rules", "text")] },
  service: { name: "Service Commerce", fields: [F("appointment", "Appointment Required", "bool"), F("duration_min", "Duration (min)", "number"), F("location_mode", "Location", "select", { options: ["onsite", "remote", "in_store", "hybrid"] }), F("workforce", "Staff Required", "number"), F("sla", "SLA", "text"), F("contract", "Contract Terms", "text")] },
  rental: { name: "Rental Commerce", fields: [F("durations", "Rental Durations", "json"), F("deposit", "Security Deposit", "number"), F("asset_tracking", "Asset Tracking", "bool"), F("damage", "Damage Assessment", "bool"), F("return_inspection", "Return Inspection", "bool")] },
  apparel: { name: "Apparel & Fashion", fields: [F("sizes", "Size System", "json"), F("fit", "Fit", "select", { options: ["slim", "regular", "relaxed", "oversized"] }), F("fabric_gsm", "Fabric GSM", "number"), F("thread_count", "Thread Count", "number"), F("care", "Care Instructions", "text"), F("gender", "Gender", "select", { options: ["men", "women", "unisex", "kids"] })] },
  vehicle: { name: "Vehicle Commerce", fields: [F("vin", "VIN", "text"), F("make", "Make", "text"), F("model", "Model", "text"), F("year", "Year", "number"), F("engine", "Engine", "text"), F("transmission", "Transmission", "text"), F("emission_class", "Emission Class", "text"), F("test_drive", "Test Drive Booking", "bool")] }
};
const INDUSTRY_VERTICAL = { grocery: "grocery", furniture: "furniture", construction: "hardware", retail: "apparel", fashion: "apparel", automotive: "automotive", industrial: "industrial", electronics: "electronics", healthcare: "medical", pharma: "medical", chemicals: "chemicals", agriculture: "agriculture", jewellery: "jewellery", luxury: "jewellery", digital: "digital", software: "digital", services: "service", rental: "rental", subscription: "digital", travel: "service", realestate: "service", finance: "service", media: "digital", education: "digital" };

/* KINDS OF PLATFORM. Each row is one kind an operator can launch any number of: what one
   is called, the capability blend it starts with when registration names none, what is
   provisioned for it, and which console sections apply. The rows are the `deployModes`
   registry — edited in 11 · Administration → Platforms, never here; a field a row leaves
   out takes this seed's value for its key, then lib/registry.js KIND_DEFAULTS.
     needsIndustries — a platform of this kind must name the industries its catalogue covers
     provision       — what registration sets up: payment gateways, shipping carriers, a
                       warehouse, and the shopfront (departments and a home page)
     sections        — the console sections a capability does not own (null: all of them);
                       an atom-owned section (rides, ops_hr…) follows the capabilities */
const KIND_CORE = ["dash", "analytics", "monitor", "team", "tenancy", "settings", "risk", "compliance", "privacy", "audit", "trash",
  "ai", "webhooks", "modules", "studio", "compose", "manual", "architecture", "helpdesk", "payments", "billing", "finance", "settlements"];
const DEPLOY_MODES = [
  { key: "marketplace", name: "Universal Marketplace", desc: "All industries, many sellers", needsIndustries: false, noun: "store", nounPlural: "stores", archetype: "", provision: { payments: true, shipping: true, warehouse: true, storefront: true }, sections: null },
  { key: "industry", name: "Industry Marketplace", desc: "Single industry vertical (furniture-only, grocery-only…)", needsIndustries: true, noun: "store", nounPlural: "stores", archetype: "", provision: { payments: true, shipping: true, warehouse: true, storefront: true }, sections: null },
  { key: "brand", name: "Brand Store", desc: "Single seller / single brand D2C", needsIndustries: true, noun: "store", nounPlural: "stores", archetype: "", provision: { payments: true, shipping: true, warehouse: true, storefront: true }, sections: null },
  { key: "mobility", name: "Mobility Platform", desc: "Ride hailing, dispatch and fleets", needsIndustries: false, noun: "operator", nounPlural: "operators", archetype: "blend_mobility",
    provision: { payments: true, shipping: false, warehouse: false, storefront: false }, sections: KIND_CORE.concat(["offers", "retention", "experiments", "localizations"]) },
  { key: "operations", name: "Business Operations (ERP)", desc: "People and payroll, procurement, manufacturing, projects", needsIndustries: false, noun: "company", nounPlural: "companies", archetype: "blend_operations",
    provision: { payments: true, shipping: false, warehouse: true, storefront: false }, sections: KIND_CORE.concat(["orders", "products", "skus", "attributes", "taxonomy", "brands", "suppliers", "planning", "logistics", "serialized", "localizations"]) },
  { key: "fintech", name: "Financial Services", desc: "Wallets, payment rails, lending and payouts", needsIndustries: false, noun: "provider", nounPlural: "providers", archetype: "blend_fintech",
    provision: { payments: true, shipping: false, warehouse: false, storefront: false }, sections: KIND_CORE.concat(["offers", "retention", "experiments", "affiliate", "localizations"]) }
];

function registry(tenantCustom) {
  const tc = tenantCustom || {};
  return {
    industries: [...(tc.industries || []), ...INDUSTRIES],
    productTypes: [...(tc.productTypes || []), ...PRODUCT_TYPES],
    verticals: { ...VERTICALS, ...(tc.verticals || {}) }
  };
}

/* ---- universal cross-vertical relationships ("tax", "invoice", "payment" must exist as
   entities/contexts/types, not columns). Contexts list available relationship types per
   vertical; the api enforces them on product.tax_profile / invoices / payments. ---- */
const VERTICAL_CONTEXTS = {
  tax: [
    { key: "gst_profile", label: "GST Profile (IN)", type: "tax", fields: [F("rate", "GST Rate", "select", { options: ["0", "5", "12", "18", "28"] }), F("hsn", "HSN Code", "text")] },
    { key: "vat_profile", label: "VAT Profile (EU)", type: "tax", fields: [F("rate", "VAT Rate", "select", { options: ["0", "7", "13", "19", "21"] }), F("reverse", "Reverse Charge", "bool")] },
    { key: "sales_tax", label: "State Sales Tax (US)", type: "tax", fields: [F("rate", "Rate", "number"), F("nexus", "Nexus State", "text")] },
    { key: "zero_rate", label: "Zero-Rated / Exempt", type: "tax", fields: [F("reason", "Exemption Reason", "text")] }
  ],
  invoice: [
    { key: "tax_invoice", label: "Tax Invoice (GST/VAT)", type: "invoice", fields: [F("requires_gstin", "Requires Buyer GSTIN/VAT ID", "bool"), F("e_invoice", "E-Invoice Mandated", "bool")] },
    { key: "commercial_invoice", label: "Commercial Invoice", type: "invoice", fields: [F("incoterms", "Incoterms", "select", { options: ["EXW", "FOB", "CIF", "DDP"] })] },
    { key: "proforma", label: "Proforma / Quotation", type: "invoice", fields: [F("validity_days", "Validity Days", "number")] },
    { key: "cash_receipt", label: "Cash Receipt (COD)", type: "invoice", fields: [] }
  ],
  payment: [
    { key: "online_capture", label: "Online Capture (Gateway)", type: "payment", fields: [F("mandates", "Supports Mandates/Recurring", "bool")] },
    { key: "bnpl", label: "Buy Now Pay Later", type: "payment", fields: [F("installments", "Installment Count", "number"), F("credit_check", "Soft Credit Check", "bool")] },
    { key: "cash_delivery", label: "Cash on Delivery", type: "payment", fields: [F("handling_fee", "Handling Fee", "money"), F("requires_otp", "OTP at Doorstep", "bool")] },
    { key: "invoice_net", label: "Invoice Terms (B2B Net)", type: "payment", fields: [F("net_days", "Net Days", "number"), F("credit_limit", "Credit Limit", "money")] }
  ]
};
/* Default context profiles for EVERY industry key (extendable at runtime via meta_lists).
   tax/invoice = default context key; payment = allowed set. */
const VERTICAL_TYPE_OF = (() => {
  const base = {
    grocery: { tax: "gst_profile", invoice: "tax_invoice", payment: ["online_capture", "cash_delivery"] },
    furniture: { tax: "sales_tax", invoice: "commercial_invoice", payment: ["online_capture", "bnpl", "cash_delivery"] },
    construction: { tax: "gst_profile", invoice: "proforma", payment: ["online_capture", "invoice_net", "cash_delivery"] },
    hardware: { tax: "gst_profile", invoice: "proforma", payment: ["online_capture", "invoice_net", "cash_delivery"] },
    jewellery: { tax: "gst_profile", invoice: "tax_invoice", payment: ["online_capture", "invoice_net"] },
    luxury: { tax: "vat_profile", invoice: "tax_invoice", payment: ["online_capture", "invoice_net"] },
    digital: { tax: "zero_rate", invoice: "commercial_invoice", payment: ["online_capture"] },
    software: { tax: "zero_rate", invoice: "commercial_invoice", payment: ["online_capture"] },
    services: { tax: "gst_profile", invoice: "tax_invoice", payment: ["online_capture", "invoice_net"] },
    rental: { tax: "sales_tax", invoice: "proforma", payment: ["online_capture", "invoice_net"] },
    subscription: { tax: "sales_tax", invoice: "commercial_invoice", payment: ["online_capture"] },
    automotive: { tax: "sales_tax", invoice: "tax_invoice", payment: ["online_capture", "cash_delivery"] },
    vehicle: { tax: "sales_tax", invoice: "commercial_invoice", payment: ["invoice_net", "bnpl"] },
    electronics: { tax: "sales_tax", invoice: "tax_invoice", payment: ["online_capture", "bnpl", "cash_delivery"] },
    fashion: { tax: "sales_tax", invoice: "tax_invoice", payment: ["online_capture", "bnpl", "cash_delivery"] },
    retail: { tax: "sales_tax", invoice: "tax_invoice", payment: ["online_capture", "cash_delivery"] }
  };
  const out = {};
  for (const ind of INDUSTRIES) out[ind.key] = base[ind.key] || { tax: "sales_tax", invoice: "commercial_invoice", payment: ["online_capture", "invoice_net", "cash_delivery"] };
  return out;
})();

/* the storefront's sort orders (productSortOrders) and the ad events a shopper may report
   (adEventKinds) — seed rows, editable as registry lists */
const SORT_ORDERS = [
  { key: "featured", name: "Featured", default: true, order: [{ flag: "bs", dir: "DESC" }, { field: "ratings_count", dir: "DESC" }] },
  { key: "price-asc", name: "Price: low to high", order: [{ field: "price", dir: "ASC" }] },
  { key: "price-desc", name: "Price: high to low", order: [{ field: "price", dir: "DESC" }] },
  { key: "rating", name: "Avg. customer review", order: [{ field: "rating", dir: "DESC" }, { field: "ratings_count", dir: "DESC" }] },
  { key: "new", name: "Newest arrivals", order: [{ flag: "new", dir: "DESC" }, { field: "position", dir: "DESC" }] },
  { key: "discount", name: "Biggest discount", order: [{ field: "deal_pct", dir: "DESC" }] }
];
const AD_EVENT_KINDS = [{ key: "impression", name: "Impression" }, { key: "click", name: "Click", self_reported: true }, { key: "conversion", name: "Conversion" }];
/* where FX rates come from: a source that `fetches` reads an HTTP JSON feed; the default is
   entered by hand */
const FX_SOURCES = [{ key: "manual", name: "Manual (offline)", default: true }, { key: "feed", name: "HTTP JSON feed", fetches: true }];
module.exports = { FX_SOURCES, CONTEXT_GROUPS, SORT_ORDERS, AD_EVENT_KINDS, INDUSTRIES, PRODUCT_TYPES, LIFECYCLE, LIFECYCLE_TRANSITIONS, REL_TYPES, MEDIA_KINDS, PACKAGING_LEVELS, UOM_UNITS, UOM_CONVERSIONS, SELLER_ROLES, PROMO_TYPES, IDENTITY_FIELDS, SHIPPING_CLASSES, SERIALIZED_STATUSES, SERIALIZED_CONDITIONS, VARIANT_AXES, COMPLIANCE_SCOPES, COMPLIANCE_KINDS, COMPLIANCE_STATUSES, SUPPLIER_ROLES, SUPPLIER_STATUSES, PAYMENT_TERMS, INCOTERMS, LOCALIZATION_ENTITIES, CONTRACT_STATUSES, TENDER_STATUSES, LINK_STATUSES, VERTICALS, INDUSTRY_VERTICAL, DEPLOY_MODES, VERTICAL_CONTEXTS, VERTICAL_TYPE_OF, registry };
