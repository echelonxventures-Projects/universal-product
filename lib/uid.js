/* LUXORA Platform - Universal Unique IDs: every row in every table gets a UUIDv4
   at insert time via SQLite triggers (covers seeds, API, entity engine, manual SQL). */
"use strict";

const TABLES = [
  "tenants", "plans", "subscriptions", "invoices", "audit_log", "platform_admins", "platform_sessions",
  "tokens", "users", "sessions", "tenant_state", "products", "product_bullets", "cart_items", "saved_items",
  "orders", "order_items", "reviews", "view_history", "settings", "departments", "home_banners", "home_cards",
  "entity_defs", "entity_data", "countries", "tax_modes", "currencies", "provider_defs", "provider_availability",
  "meta_lists", "tenant_gateways", "custom_providers", "payments", "fx_rates", "platform_settings",
  "links", "context_types", "modules", "tenant_modules", "wallets",
  "serialized_items", "variant_groups", "compliance_records", "suppliers", "product_suppliers", "localizations", "contracts", "tenders",
  "ai_usage", "ai_tasks", "offers", "coupons", "coupon_redemptions", "wallet_entries",
  "invoice_lines", "usage_records", "credit_notes", "billing_events",
  "webhooks", "webhook_deliveries", "entity_meta", "idempotency_keys",
  "stock_transfers", "remittance_records", "inbound_events", "sso_connections", "scim_tokens"
];

const UUID_SQL = `lower(hex(randomblob(4))||'-'||hex(randomblob(2))||'-4'||substr(hex(randomblob(2)),2)||'-'||substr('89ab',abs(random())%4+1,1)||substr(hex(randomblob(2)),2)||'-'||hex(randomblob(6)))`;

function ensureUids(db) {
  for (const t of TABLES) {
    try {
      db.exec(`ALTER TABLE ${t} ADD COLUMN uid TEXT`);
    } catch (e) { /* column already present */ }
    try { db.exec(`CREATE UNIQUE INDEX IF NOT EXISTS ux_${t}_uid ON ${t}(uid)`); } catch (e) { console.error("uid index", t, e.message); }
    try {
      db.exec(`CREATE TRIGGER IF NOT EXISTS trg_${t}_uid AFTER INSERT ON ${t}
               BEGIN UPDATE ${t} SET uid = ${UUID_SQL} WHERE rowid = NEW.rowid; END;`);
    } catch (e) { console.error("uid trigger", t, e.message); }
    /* backfill rows that predate the trigger */
    const rows = db.prepare(`SELECT rowid FROM ${t} WHERE uid IS NULL`).all();
    if (rows.length) {
      const upd = db.prepare(`UPDATE ${t} SET uid = ${UUID_SQL} WHERE rowid = ?`);
      for (const r of rows) upd.run(r.rowid);
    }
  }
  return TABLES.length;
}

module.exports = { ensureUids, TABLES, UUID_SQL };
