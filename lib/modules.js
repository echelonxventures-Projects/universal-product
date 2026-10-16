/* LUXORA Platform - Capability Marketplace.
   EVERYTHING is a product: identity, gid, geo, billing, seo, recommendations, cart, listing,
   checkout, tax, offers, wallet, logistics, payment rails, catalog packs, themes.
   Modules are catalog rows with price + manifest; manifests declare capabilities/features/
   gateways/catalog actions; the platform auto-applies free baselines at provisioning ("purchase"). */
"use strict";
/* seed data (lib/seed/modules.json): data, not code — the registries are seeded from it */
const SEED_MODULES = require("./seed/modules.json");

const { run, get, all } = require("./db.js");
const settings = require("./settings.js");

function J(v, d) { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } }

/* ---------- marketplace SEED (written to the `modules` table once; from then on the DB is the
   source of truth — add/edit/delete modules live in the platform console, no code changes) ---------- */
/* notes that lived in the seed literal (now lib/seed/modules.json): */
/* free baselines — auto-installed ("purchased") when a store is provisioned */
/* paid premium modules — purchased on demand */
/* payment rail packs */
/* catalog packs — the product range itself is a purchasable module */
/* GOIP Ω∞ — the value-exchange infrastructure itself is a product: one purchase turns every
   capability, fabric and registry on for a store and starts the meters that bill it. */
/* commerce archetypes — a purchasable COMPOSITION, never a bundle of console surface.
   Installing one composes the individual atoms it names (the blends below expand into
   their capabilities in applyModule), and the store console's nav lights up as a
   consequence: each atom declares the section(s) it governs and the grant engine
   derives the surface from the live composition (lib/authz.js). An operator can just as
   well switch a single atom on in ⚙️ Capabilities — the archetype is the convenience,
   never the gate. */
/* themes */
const MARKET = SEED_MODULES.MARKET;

function seedMarket() {
  /* INSERT OR IGNORE keeps the DB authoritative (edits/deletes in the console survive) while new
     catalogue entries still appear on an existing install — same self-healing rule as the registries. */
  MARKET.forEach((m, i) => run(`INSERT OR IGNORE INTO modules(id,name,category,summary,price_type,price,currency,version,vendor,manifest,position)
    VALUES(?,?,?,?,?,?,?,?,?,?,?)`, m.id, m.name, m.category, m.summary || "", m.price > 0 ? "one_time" : "free",
    m.price || 0, require("./defaults.js").platformCurrency(), "1.0", "LUXORA",
    JSON.stringify({ capabilities: m.capabilities || [], features: m.features || {}, gateways: m.gateways || [], catalog: m.catalog || [], fields: m.fields || [] }), i));
}
seedMarket();

/* ---------- state ---------- */
function moduleRow(id) { return get("SELECT * FROM modules WHERE id=?", id); }
function installedRow(tid, id) { return get("SELECT * FROM tenant_modules WHERE tenant_id=? AND module_id=?", tid, id); }
function installed(tid) {
  return all(`SELECT tm.module_id, tm.status, tm.config, tm.installed_at, m.name, m.category, m.price, m.manifest
    FROM tenant_modules tm JOIN modules m ON m.id=tm.module_id WHERE tm.tenant_id=? AND tm.status='installed' ORDER BY m.category, m.position`, tid)
    .map(r => ({ ...r, manifest: J(r.manifest, {}), config: J(r.config, {}) }));
}
function caps(tid) { const s = new Set(); installed(tid).forEach(m => (m.manifest.capabilities || []).forEach(c => s.add(c))); return s; }
/* a module capability is also subject to the applicability rules (type "module") */
function hasCap(tid, c) { if (!caps(tid).has(c)) return false; const rules = require("./rules.js"); return rules.permitsAt("module.cap", c, rules.at("module.cap", tid)); }
function moduleConfig(tid, id) { const r = installedRow(tid, id); return r ? J(r.config, {}) : {}; }

/* ---------- apply / unapply: the plug-and-play core ---------- */
function applyModule(tenantId, module, config) {
  const man = J(module.manifest, {});
  if (man.features && Object.keys(man.features).length) {
    const st = settings.load(tenantId);
    settings.save(tenantId, { features: { ...st.features, ...man.features } });
  }
  if (man.catalog && man.catalog.length) {
    const db = require("./db.js");
    const meta = require("./meta.js");
    man.catalog.forEach(k => {
      const ind = meta.INDUSTRIES.find(x => x.key === k);
      if (ind) run("INSERT OR IGNORE INTO departments(tenant_id,key,label,icon,position) VALUES(?,?,?,?,?)", tenantId, k, ind.name, ind.icon,
        get("SELECT COALESCE(MAX(position),0)+1 p FROM departments WHERE tenant_id=?", tenantId).p);
    });
    db.seedTaxonomy(tenantId, man.catalog);
    db.seedTenantDepartments(tenantId, man.catalog);
    db.seedTenantCatalog(tenantId, man.catalog);
  }
  if (man.gateways && man.gateways.length) {
    const t = get("SELECT country FROM tenants WHERE id=?", tenantId);
    const registry = require("./registry.js");
    const country = registry.country((t && t.country) || require("./security.js").defaultCountry());
    man.gateways.filter(p => registry.supports(p, country.code)).forEach((p, i) =>
      run(`INSERT INTO tenant_gateways(tenant_id,provider_id,enabled,is_primary,mode,config,position) VALUES(?,?,1,?,'sandbox','{}',?)
           ON CONFLICT(tenant_id,provider_id) DO UPDATE SET enabled=1`, tenantId, p, i === 0 ? 1 : 0, i));
  }
  if (man.capabilities && man.capabilities.includes("identityPro")) {
    const identity = require("./identity.js");
    const settings = identity.getIdentitySettings(tenantId);
    const password = settings.password || {};
    const mfa = settings.mfa || {};
    const session = settings.session || {};
    const login = settings.login || {};
    
    identity.setIdentitySettings(tenantId, {
      password: {
        minLength: config.passwordMinLength || password.minLength || 10,
        requireUppercase: password.requireUppercase || true,
        requireNumbers: password.requireNumbers || true,
        requireSpecialChars: password.requireSpecialChars || true,
        expiryDays: password.expiryDays || 0
      },
      mfa: {
        enabled: mfa.enabled || false,
        requireForAdmin: config.mfaRequired || true,
        requireForStaff: false,
        methods: mfa.methods || ["totp", "sms"]
      },
      session: {
        timeoutMinutes: config.sessionTimeoutMinutes || session.timeoutMinutes || 120,
        maxConcurrent: session.maxConcurrent || 3,
        rememberMeDays: session.rememberMeDays || 30
      },
      login: {
        maxAttempts: login.maxAttempts || 5,
        lockoutMinutes: login.lockoutMinutes || 30,
        allowGuestCheckout: config.requireLoginCheckout ? false : true
      }
    });
    
    if (config.ssoProviders) {
      const providers = config.ssoProviders.split(",").map(s => s.trim());
      providers.forEach(p => {
        identity.upsertIdentityProvider(tenantId, {
          provider_type: "sso",
          name: p.charAt(0).toUpperCase() + p.slice(1),
          enabled: true,
          config: { provider: p }
        });
      });
    }
    if (config.socialProviders) {
      const providers = config.socialProviders.split(",").map(s => s.trim());
      providers.forEach(p => {
        identity.upsertIdentityProvider(tenantId, {
          provider_type: "oauth",
          name: p.charAt(0).toUpperCase() + p.slice(1) + " OAuth",
          enabled: true,
          config: { provider: p }
        });
      });
    }
    if (config.magicLinkEnabled) {
      identity.upsertIdentityProvider(tenantId, {
        provider_type: "magic_link",
        name: "Magic Link",
        enabled: true,
        config: { provider: "email" }
      });
    }
    if (config.biometricEnabled) {
      identity.upsertIdentityProvider(tenantId, {
        provider_type: "biometric",
        name: "WebAuthn",
        enabled: true,
        config: { provider: "webauthn" }
      });
    }
    identity.upsertIdentityProvider(tenantId, {
      provider_type: "otp",
      name: "OTP",
      enabled: true,
      config: { provider: config.otpMethod || "email" }
    });
  }
  if (man.capabilities && man.capabilities.length) composeCapabilities(tenantId, man, true);
  run(`INSERT INTO tenant_modules(tenant_id,module_id,status,config,installed_by) VALUES(?,?,'installed',?,?)
       ON CONFLICT(tenant_id,module_id) DO UPDATE SET status='installed', config=excluded.config`,
    tenantId, module.id, JSON.stringify(config || {}), (config && config.__by) || "");
  return { ok: true, id: module.id };
}
/* ---------- capability composition: a pack's engines come on with it ----------
   A module's `capabilities` name catalog capabilities or blend PRESETS. Installing
   composes them for the tenant — a preset is expanded into the capabilities it declares
   (the registry's own membership, never a hardcoded list) — and releasing disables them.
   A capability the platform switched off is never turned on, so a pack can never widen a
   gate the platform closed. Keys that are neither a preset nor a catalog capability
   (the feature flags other modules use, e.g. "wallet" / "identityPro") are left to the
   session's capability list, exactly as before. */
function composeCapabilities(tenantId, man, on) {
  const keys = new Set();
  for (const k of (man.capabilities || [])) {
    const preset = get("SELECT capabilities FROM capability_presets WHERE key=?", k);
    if (preset) { for (const ck of Object.keys(J(preset.capabilities, {}))) keys.add(ck); }
    else keys.add(k);
  }
  if (!keys.size) return;
  const capabilities = require("./capabilities.js");
  for (const k of keys) {
    const cap = capabilities.catalogRow(k);
    if (!cap || !cap.enabled) continue;
    if (on) capabilities.enable(tenantId, k, {}, "module");
    else capabilities.disable(tenantId, k);
  }
}
function unapplyModule(tenantId, module) {
  const man = J(module.manifest, {});
  if (man.features) { const st = settings.load(tenantId); const off = {}; for (const k of Object.keys(man.features)) off[k] = false; settings.save(tenantId, { features: { ...st.features, ...off } }); }
  if (man.gateways) for (const p of man.gateways) run("UPDATE tenant_gateways SET enabled=0 WHERE tenant_id=? AND provider_id=?", tenantId, p);
  if (man.capabilities && man.capabilities.length) composeCapabilities(tenantId, man, false);
  run("UPDATE tenant_modules SET status='disabled' WHERE tenant_id=? AND module_id=?", tenantId, module.id);
  return { ok: true };
}

/* ---------- provisioning auto-purchase: every store gets all free baselines ---------- */
function ensureBaselines() {
  const tenants = all("SELECT id, slug FROM tenants");
  for (const t of tenants) {
    for (const m of all("SELECT * FROM modules WHERE price=0 AND status='active'")) {
      const row = get("SELECT status FROM tenant_modules WHERE tenant_id=? AND module_id=?", t.id, m.id);
      if (!row) run("INSERT INTO tenant_modules(tenant_id,module_id,status,config) VALUES(?,?,'installed','{}')", t.id, m.id);
      else if (row.status !== "installed") run("UPDATE tenant_modules SET status='installed' WHERE tenant_id=? AND module_id=?", t.id, m.id);
    }
  }
}

/* ---------- wallets (account-bound; the wallet capability owns this table) ---------- */
function ownerFor(s) { const t = s.tenant ? s.tenant.id : 1; return s.user_id ? `t${t}:u:${s.user_id}` : `t${t}:s:${s.sid}`; }
function walletBalance(tid, owner) { const r0 = get("SELECT balance b FROM wallets WHERE tenant_id=? AND owner=?", tid, owner); return r0 ? +r0.b : 0; }
function _journal(tid, owner, kind, delta) { const after = get("SELECT balance b FROM wallets WHERE tenant_id=? AND owner=?", tid, owner); try { run("INSERT INTO wallet_entries(tenant_id,owner,currency,kind,amount,balance_after,actor) VALUES(?,?,?,?,?,?,?)", tid, owner, require("./defaults.js").currency(tid), kind, delta, after ? +after.b : 0, "wallet"); } catch (e) { } }
function walletAdd(tid, owner, amt) {
  run(`INSERT INTO wallets(tenant_id,owner,balance,updated_at) VALUES(?,?,?,datetime('now'))
       ON CONFLICT(tenant_id,owner) DO UPDATE SET balance=balance+excluded.balance, updated_at=datetime('now')`, tid, owner, amt);
  _journal(tid, owner, amt >= 0 ? "deposit" : "adjust", amt);
}
function walletSet(tid, owner, amt) { const before = walletBalance(tid, owner); run("INSERT INTO wallets(tenant_id,owner,balance) VALUES(?,?,?) ON CONFLICT(tenant_id,owner) DO UPDATE SET balance=excluded.balance", tid, owner, Math.max(0, +(amt || 0).toFixed(2))); _journal(tid, owner, amt < before ? "redeem" : "adjust", +(amt - before).toFixed(2)); }
function walletMerge(fromOwner, toOwner) {
  const a = get("SELECT tenant_id tid, balance b FROM wallets WHERE owner=?", fromOwner);
  if (!a || !a.b) return;
  walletAdd(a.tid, toOwner, a.b);
  run("DELETE FROM wallets WHERE owner=?", fromOwner);
}

module.exports = { MARKET, seedMarket, ensureBaselines, moduleRow, installed, installedRow, caps, hasCap, moduleConfig, applyModule, unapplyModule, walletBalance, walletAdd, walletSet, walletMerge, ownerFor, J };
