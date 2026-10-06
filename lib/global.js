/* LUXORA Platform - Global Configuration Module
   Central repository for platform-wide definitions (Countries, Currencies, Providers, Plans)
   that can be configured per-tenant. All global data flows from this module to tenants. */
"use strict";

let _db = null;
const db = () => _db || (_db = require("./db.js"));
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };

/* =========================== COUNTRIES ===========================
    The country/currency catalog is declared once, in lib/providers.js, and seeded
    into the DB; this module reads the live rows. A second seed literal here was a
    duplicate declaration of the same catalog (Law 002) — removed. */

function listCountries() {
  return db().all("SELECT * FROM countries ORDER BY position, code");
}

function getCountry(code) {
  return db().get("SELECT * FROM countries WHERE code=?", code.toUpperCase());
}

function createCountry(data) {
  const D = db();
  D.run("INSERT INTO countries(code,name,currency,symbol,locale,decimals,tax_mode,tax_rate,active,uid) VALUES(?,?,?,?,?,?,?,?,?,?)",
    data.code, data.name, data.currency, data.symbol, data.locale, data.decimals || 2, data.tax_mode || "manual", data.tax_rate || 0, data.active !== false ? 1 : 0, data.uid || D.newUid());
  return { ok: true, code: data.code };
}

function updateCountry(code, data) {
  const fields = []; const values = [];
  Object.keys(data).forEach(k => { fields.push(`${k}=?`); values.push(data[k]); });
  if (!fields.length) return { ok: true };
  fields.push("updated_at=datetime('now')"); values.push(code.toUpperCase());
  db().run(`UPDATE countries SET ${fields.join(", ")} WHERE code=?`, ...values);
  return { ok: true, code };
}

function enableCountry(code) { db().run("UPDATE countries SET active=1 WHERE code=?", code.toUpperCase()); return { ok: true }; }
function disableCountry(code) { db().run("UPDATE countries SET active=0 WHERE code=?", code.toUpperCase()); return { ok: true }; }

/* =========================== CURRENCIES ===========================
    Declared once in lib/providers.js and seeded; this module reads the live rows
    (see the note under COUNTRIES above). */

function listCurrencies() {
  return db().all("SELECT * FROM currencies ORDER BY position, code");
}

function getCurrency(code) {
  return db().get("SELECT * FROM currencies WHERE code=?", code.toUpperCase());
}

function createCurrency(data) {
  const D = db();
  D.run("INSERT INTO currencies(code,name,symbol,decimals,usd,active,uid) VALUES(?,?,?,?,?,?,?)",
    data.code, data.name, data.symbol, data.decimals || 2, data.usd || 1, data.active !== false ? 1 : 0, data.uid || D.newUid());
  return { ok: true, code: data.code };
}

function updateCurrency(code, data) {
  const fields = []; const values = [];
  Object.keys(data).forEach(k => { fields.push(`${k}=?`); values.push(data[k]); });
  if (!fields.length) return { ok: true };
  fields.push("updated_at=datetime('now')"); values.push(code.toUpperCase());
  db().run(`UPDATE currencies SET ${fields.join(", ")} WHERE code=?`, ...values);
  return { ok: true, code };
}

/* =========================== PROVIDERS =========================== */
/* Global provider definitions for payments, shipping, notifications, tax, marketing */
function listProviders(kind) {
  const q = kind ? "WHERE kind=?" : "";
  const params = kind ? [kind] : [];
  return db().all(`SELECT * FROM provider_defs ${q} ORDER BY position, id`, ...params);
}

function getProvider(id, kind) {
  return db().get("SELECT * FROM provider_defs WHERE id=? AND kind=?", id, kind);
}

function createProvider(data) {
  const D = db();
  D.run(`INSERT INTO provider_defs(id,kind,name,emoji,description,methods,fee_pct,fee_fixed,fields,base_fee,eta_min,eta_max,position,enabled,uid) 
         VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`,
    data.id, data.kind, data.name, data.emoji || "", data.description || "", JSON.stringify(data.methods || []), 
    data.fee_pct || 0, data.fee_fixed || 0, JSON.stringify(data.fields || []), data.base_fee || 0, 
    data.eta_min, data.eta_max, data.position || 0, data.enabled !== false ? 1 : 0, data.uid || D.newUid());
  return { ok: true, id: data.id, kind: data.kind };
}

function updateProvider(id, kind, data) {
  const fields = []; const values = [];
  Object.keys(data).forEach(k => { 
    if (["methods", "fields"].includes(k)) { fields.push(`${k}=?`); values.push(JSON.stringify(data[k])); }
    else { fields.push(`${k}=?`); values.push(data[k]); }
  });
  if (!fields.length) return { ok: true };
  fields.push("updated_at=datetime('now')"); values.push(id, kind);
  db().run(`UPDATE provider_defs SET ${fields.join(", ")} WHERE id=? AND kind=?`, ...values);
  return { ok: true, id, kind };
}

/* Provider-country availability */
function listProviderAvailability(providerId) {
  return db().all("SELECT * FROM provider_availability WHERE provider_id=? ORDER BY country_code", providerId);
}

function enableProviderInCountry(providerId, countryCode) {
  db().run("INSERT INTO provider_availability(provider_id,country_code,uid) VALUES(?,?,?)", 
    providerId, countryCode, db().newUid());
  return { ok: true, providerId, countryCode };
}

function disableProviderInCountry(providerId, countryCode) {
  db().run("DELETE FROM provider_availability WHERE provider_id=? AND country_code=?", providerId, countryCode);
  return { ok: true, providerId, countryCode };
}

function providerSupportsCountry(providerId, countryCode) {
  const row = db().get("SELECT 1 FROM provider_availability WHERE provider_id=? AND country_code=?", providerId, countryCode);
  return !!row;
}

/* =========================== PLANS =========================== */
/* Global subscription plans that can be assigned to tenants */
function listPlans() {
  return db().all("SELECT * FROM plans ORDER BY position, id");
}

function getPlan(id) {
  return db().get("SELECT * FROM plans WHERE id=?", id);
}

function createPlan(data) {
  const D = db();
  D.run("INSERT INTO plans(name,price_month,currency,max_products,max_orders_month,features,position,uid) VALUES(?,?,?,?,?,?,?,?)",
    data.name, data.price_month || 0, data.currency || "USD", data.max_products || 100, 
    data.max_orders_month || 100, JSON.stringify(data.features || {}), data.position || 0, data.uid || D.newUid());
  return { ok: true, id: Number(D.lastInsertRowid) };
}

function updatePlan(id, data) {
  const fields = []; const values = [];
  Object.keys(data).forEach(k => { 
    if (["features"].includes(k)) { fields.push(`${k}=?`); values.push(JSON.stringify(data[k])); }
    else { fields.push(`${k}=?`); values.push(data[k]); }
  });
  if (!fields.length) return { ok: true };
  fields.push("updated_at=datetime('now')"); values.push(id);
  db().run(`UPDATE plans SET ${fields.join(", ")} WHERE id=?`, ...values);
  return { ok: true, id };
}

/* =========================== TENANT CONFIGURATION =========================== */
/* Assign global configurations to tenants */
function getTenantCountry(tenantId) {
  const row = db().get("SELECT country FROM tenants WHERE id=?", tenantId);
  return row ? row.country : "US";
}

function setTenantCountry(tenantId, countryCode) {
  db().run("UPDATE tenants SET country=? WHERE id=?", countryCode.toUpperCase(), tenantId);
  return { ok: true, tenantId, country: countryCode };
}

function getTenantCurrency(tenantId) {
  const row = db().get("SELECT currency FROM tenants WHERE id=?", tenantId);
  return row ? row.currency : "USD";
}

function setTenantCurrency(tenantId, currencyCode) {
  db().run("UPDATE tenants SET currency=? WHERE id=?", currencyCode.toUpperCase(), tenantId);
  return { ok: true, tenantId, currency: currencyCode };
}

function getTenantProviders(tenantId, kind) {
  return db().all("SELECT provider_id, config, active FROM tenant_gateways WHERE tenant_id=? AND kind=?", tenantId, kind || "payment");
}

function addTenantProvider(tenantId, providerId, kind, config) {
  db().run("INSERT INTO tenant_gateways(tenant_id,provider_id,kind,config,active) VALUES(?,?,?,?,1)",
    tenantId, providerId, kind || "payment", JSON.stringify(config || {}));
  return { ok: true, tenantId, providerId, kind };
}

function removeTenantProvider(tenantId, providerId, kind) {
  db().run("DELETE FROM tenant_gateways WHERE tenant_id=? AND provider_id=? AND kind=?", tenantId, providerId, kind || "payment");
  return { ok: true };
}

function getTenantPlan(tenantId) {
  const sub = db().get("SELECT plan_id FROM subscriptions WHERE tenant_id=? AND status='active' ORDER BY id DESC", tenantId);
  return sub ? sub.plan_id : null;
}

function assignTenantPlan(tenantId, planId) {
  const D = db();
  D.run("DELETE FROM subscriptions WHERE tenant_id=?", tenantId);
  D.run("INSERT INTO subscriptions(tenant_id,plan_id,status,started_at,renews_at) VALUES(?,?, 'active', datetime('now'), datetime('now','+1 month'))", tenantId, planId);
  return { ok: true, tenantId, planId };
}

/* =========================== GLOBAL SETTINGS =========================== */
function getGlobalSetting(key) {
  const row = db().get("SELECT value FROM platform_settings WHERE key=?", key);
  return row ? J(row.value) : null;
}

function setGlobalSetting(key, value) {
  db().run("INSERT INTO platform_settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", key, JSON.stringify(value));
  return { ok: true, key };
}

function deleteGlobalSetting(key) {
  db().run("DELETE FROM platform_settings WHERE key=?", key);
  return { ok: true };
}

/* =========================== EXPORTS =========================== */
module.exports = {
  /* Countries */
  listCountries, getCountry, createCountry, updateCountry, enableCountry, disableCountry,
  /* Currencies */
  listCurrencies, getCurrency, createCurrency, updateCurrency,
  /* Providers */
  listProviders, getProvider, createProvider, updateProvider,
  listProviderAvailability, enableProviderInCountry, disableProviderInCountry, providerSupportsCountry,
  /* Plans */
  listPlans, getPlan, createPlan, updatePlan,
  /* Tenant Configuration */
  getTenantCountry, setTenantCountry,
  getTenantCurrency, setTenantCurrency,
  getTenantProviders, addTenantProvider, removeTenantProvider,
  getTenantPlan, assignTenantPlan,
  /* Global Settings */
  getGlobalSetting, setGlobalSetting, deleteGlobalSetting
};
