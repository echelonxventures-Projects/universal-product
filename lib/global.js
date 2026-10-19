/* LUXORA Platform - Global Configuration Module
   Central repository for platform-wide definitions (Countries, Currencies, Providers, Plans)
   that can be configured per-tenant. All global data flows from this module to tenants. */
"use strict";

let _db = null;
const db = () => _db || (_db = require("./db.js"));
/* a master row is checked against its entity's own field declarations (pattern, format,
   bounds) — the same check the Data Studio path runs */
function invalid(entity, data, partial) {
  const { ENTITY_DEFS, validate, coerce } = require("./entity.js");
  const def = ENTITY_DEFS[entity], row = {};
  for (const f of def.fields) if (f.key in data) row[f.key] = coerce(f, data[f.key]);
  const errs = validate(def, row, partial);
  return errs.length ? { ok: false, error: errs.join("; ") } : null;
}
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };

/* S8: the update* builders turned request body keys into SET clause text
   (`${k}=?`), which makes the column list a request-controlled string even
   though the values stay bound. Whitelist each table's columns against its
   declared schema and JSON-encode the structured ones, the way the entity
   engine whitelists its own dynamic builders. Returns the [clause, params]
   pair the callers append the key to. */
function setClause(data, allowed, jsonCols) {
  const fields = [], values = [];
  for (const k of Object.keys(data)) {
    if (!allowed.includes(k)) continue;
    fields.push(k + "=?");
    values.push(jsonCols.includes(k) ? JSON.stringify(data[k]) : data[k]);
  }
  if (!fields.length) return null;
  return [fields, values];
}
/* a country's own columns; its currency and locale are settings at its place (lib/places.js) */
const COLS_COUNTRY = ["name", "position", "active"];
const COLS_CURRENCY = ["name", "symbol", "decimals", "usd", "position", "active"];
const COLS_PROVIDER = ["name", "emoji", "description", "methods", "fee_pct", "fee_fixed", "fields", "base_fee", "eta_min", "eta_max", "position", "enabled"];
const COLS_PLAN = ["name", "price_month", "currency", "max_products", "max_orders_month", "features", "position"];

/* =========================== COUNTRIES ===========================
    The country/currency catalog is declared once, in lib/providers.js, and seeded
    into the DB; this module reads the live rows. A second seed literal here was a
    duplicate declaration of the same catalog (Law 002) — removed. */

function listCountries() {
  return db().all("SELECT * FROM countries ORDER BY position, code").map(r => places().read("country", r));
}

function getCountry(code) {
  const r = db().get("SELECT * FROM countries WHERE code=?", code.toUpperCase());
  return r ? places().read("country", r) : r;
}

function createCountry(data) {
  const bad = invalid("country", data); if (bad) return bad;
  data = { ...data, code: String(data.code).toUpperCase(), currency: String(data.currency).toUpperCase() };
  /* geography only — a country carries no tax facts; the tax engine owns jurisdiction rates.
     The place is recorded on the kernel first and the row in the same transaction (lib/places.js) */
  if (db().get("SELECT 1 AS x FROM countries WHERE code=?", data.code)) return { ok: false, error: "Country already exists: " + data.code };
  return places().through(false, "country", { ...data, active: data.active !== false ? 1 : 0 }, data.code, () => {
    places().insertCountry({ ...data, active: data.active !== false ? 1 : 0 });
    return { ok: true, code: data.code };
  });
}

function updateCountry(code, data) {
  const { code: _c, ...rest } = data; const bad = invalid("country", rest, true); if (bad) return bad;
  if (data.currency) data = { ...data, currency: String(data.currency).toUpperCase() };
  if (!db().get("SELECT 1 AS x FROM countries WHERE code=?", code.toUpperCase())) return { ok: false, error: "Not found" };
  const sc = setClause(data, COLS_COUNTRY, []);
  return places().through(false, "country", data, code.toUpperCase(), () => {
    if (sc) db().run(`UPDATE countries SET ${sc[0].join(", ")} WHERE code=?`, ...sc[1], code.toUpperCase());
    return { ok: true, code };
  });
}

const setActive = (code, on) => places().through(false, "country", { active: on ? 1 : 0 }, code.toUpperCase(), () => {
  db().run("UPDATE countries SET active=? WHERE code=?", on ? 1 : 0, code.toUpperCase()); return { ok: true };
});
function enableCountry(code) { return setActive(code, true); }
function disableCountry(code) { return setActive(code, false); }
/* every write to the country master goes through Geo's write path: the kernel first */
const places = () => require("./places.js");

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
  const bad = invalid("currency", data); if (bad) return bad;
  data = { ...data, code: String(data.code).toUpperCase() };
  const D = db();
  D.run("INSERT INTO currencies(code,name,symbol,decimals,usd,active,uid) VALUES(?,?,?,?,?,?,?)",
    data.code, data.name, data.symbol, data.decimals != null && data.decimals !== "" ? Number(data.decimals) : 2, data.usd || 1, data.active !== false ? 1 : 0, data.uid || null);
  return { ok: true, code: data.code };
}

function updateCurrency(code, data) {
  const { code: _c, ...rest } = data; const bad = invalid("currency", rest, true); if (bad) return bad;
  const sc = setClause(data, COLS_CURRENCY, []);
  if (!sc) return { ok: true };
  const [fields, values] = sc;
  values.push(code.toUpperCase());
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
    data.eta_min, data.eta_max, data.position || 0, data.enabled !== false ? 1 : 0, data.uid || null);
  return { ok: true, id: data.id, kind: data.kind };
}

function updateProvider(id, kind, data) {
  const sc = setClause(data, COLS_PROVIDER, ["methods", "fields"]);
  if (!sc) return { ok: true };
  const [fields, values] = sc;
  values.push(id, kind);
  db().run(`UPDATE provider_defs SET ${fields.join(", ")} WHERE id=? AND kind=?`, ...values);
  return { ok: true, id, kind };
}

/* Provider-country availability */
function listProviderAvailability(providerId) {
  return db().all("SELECT * FROM provider_availability WHERE provider_id=? ORDER BY country_code", providerId);
}

function enableProviderInCountry(providerId, countryCode) {
  /* re-enabling clears the exemption an operator's earlier disable recorded, or the next
     reconciliation would honour the stale exemption and unlink it again */
  try { require("./registry.js").unexemptProvider(providerId, countryCode); } catch (e) { }
  db().run("INSERT INTO provider_availability(provider_id,country_code,uid) VALUES(?,?,?)", 
    providerId, countryCode, null);
  return { ok: true, providerId, countryCode };
}

function disableProviderInCountry(providerId, countryCode) {
  /* a raw DELETE is not durable: reconcileDerived would re-materialise the row on the next
     boot or country addition. Record the exemption so the console's disable is authoritative
     (exemptProvider also deletes the row) */
  try { require("./registry.js").exemptProvider(providerId, countryCode); }
  catch (e) { db().run("DELETE FROM provider_availability WHERE provider_id=? AND country_code=?", providerId, countryCode); }
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
    data.name, data.price_month || 0, data.currency || require("./defaults.js").platformCurrency(), data.max_products || 100, 
    data.max_orders_month || 100, JSON.stringify(data.features || {}), data.position || 0, data.uid || null);
  return { ok: true, id: Number(D.lastInsertRowid) };
}

function updatePlan(id, data) {
  const sc = setClause(data, COLS_PLAN, ["features"]);
  if (!sc) return { ok: true };
  const [fields, values] = sc;
  values.push(id);
  db().run(`UPDATE plans SET ${fields.join(", ")} WHERE id=?`, ...values);
  return { ok: true, id };
}

/* =========================== TENANT CONFIGURATION =========================== */
/* Assign global configurations to tenants */
/* a store's country is its jurisdiction on the kernel (lib/stores.js) */
function getTenantCountry(tenantId) {
  return require("./stores.js").country(tenantId);
}

function setTenantCountry(tenantId, countryCode) {
  try { require("./stores.js").setJurisdiction(tenantId, String(countryCode).toUpperCase()); }
  catch (e) { if (e.status === 400) return { ok: false, error: e.message }; throw e; }
  require("./settings.js").bust(tenantId);
  return { ok: true, tenantId, country: String(countryCode).toUpperCase() };
}

function getTenantCurrency(tenantId) {
  return require("./defaults.js").currency(tenantId);
}

function setTenantCurrency(tenantId, currencyCode) {
  /* a store's currency is its commerce setting (tenants has no currency column) */
  const row = db().get("SELECT value FROM settings WHERE tenant_id=? AND key='commerce'", tenantId);
  let commerce = {}; try { commerce = JSON.parse((row && row.value) || "{}"); } catch (e) { }
  require("./settings.js").save(tenantId, { commerce: Object.assign(commerce, { currency: currencyCode.toUpperCase() }) });
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
  D.run("INSERT INTO subscriptions(tenant_id,plan_id,status,started_at,renews_at) VALUES(?,?,?, datetime('now'), datetime('now','+1 month'))", tenantId, planId, require("./states.js").first("plan_subscription", "paying"));
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
