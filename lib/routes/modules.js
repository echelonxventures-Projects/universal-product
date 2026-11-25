/* LUXORA Platform — modules domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the modules domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "modules", routes(kit) {
  const { features, ownerFor, engineFail, requireSection, J, T, all, audit, bad, capTenantScope, caps, crypto, env, get, ipOf, json, logAction, masterTenant, mods, requireAdmin, requirePlatform, requirePlatformSection, requireStaff, rl, run, stIn, stIs } = kit;

  /* ================= MODULE MARKETPLACE (everything is a product) ================= */
  /* store-facing marketplace: the store itself purchases modules */
  function apiMarket(req, res, url, s) {
    const modules = all("SELECT id,name,category,summary,price,manifest,status FROM modules WHERE status IN " + stIn("module", "listed").sql + " ORDER BY position", ...stIn("module", "listed").args).map(m => ({ id: m.id, name: m.name, category: m.category, summary: m.summary, price: m.price, capabilities: (J(m.manifest, {}).capabilities || []), fields: (J(m.manifest, {}).fields || []) }));
    json(res, 200, { modules, installed: mods.installed(T(s)).map(m => ({ id: m.module_id, capabilities: (m.manifest.capabilities || []), config: m.config })) });
  }
  function apiModulePurchase(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const m = mods.moduleRow(String(body.module_id || ""));
    if (!m || !stIs("module", m.status, "listed")) return bad(res, "Unknown module", 404);
    let invoice = null;
    const was = (mods.installedRow(T(s), m.id) || {}).status === "installed";
    if (!was && m.price > 0) {
      const number = "MOD-" + (1000 + get("SELECT COUNT(*) c FROM invoices").c + 1);
      /* the module is billed on account: an OPEN invoice the store owes (dunning applies). It
         used to be written as already paid, with a fabricated captured payment. */
      run("INSERT INTO invoices(tenant_id,number,period_start,period_end,amount,currency,status,note) VALUES(?,?,date('now'),date('now'),?,?,'draft',?)", T(s), number, m.price, m.currency || require("../defaults.js").platformCurrency(), "Module: " + m.name);
      invoice = number;
    }
    mods.applyModule(T(s), m, body.config || {});
    logAction(s, "module.purchase", "tenant_module", T(s) + ":" + m.id, { invoice }, req);
    json(res, 200, { ok: true, invoice });
  }
  function apiModuleRelease(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const m = mods.moduleRow(String(body.module_id || "")); if (!m) return bad(res, "Unknown module", 404);
    /* the module that provides the wallet point cannot be released while the point is live */
    if (require("../gates.js").on(T(s), "checkout.wallet") && require("../gates.js").provides(m, "checkout.wallet")) return bad(res, require("../gates.js").row("checkout.wallet").live_state || require("../gates.js").message("checkout.wallet"), 409);
    mods.unapplyModule(T(s), m);
    logAction(s, "module.release", "tenant_module", T(s) + ":" + m.id, {}, req);
    json(res, 200, { ok: true });
  }
  function apiPlatformModules(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    const modules = all("SELECT * FROM modules ORDER BY position").map(m => ({ ...m, manifest: J(m.manifest, {}) }));
    const installs = all("SELECT tenant_id, module_id, status, config, installed_at FROM tenant_modules");
    json(res, 200, { modules, installs, tenants: all("SELECT id, slug, name FROM tenants ORDER BY id") });
  }
  function apiModuleInstall(req, res, url, s, body, id) {
    if (!requirePlatformSection(s, res, "modules", "write")) return;
    const m = mods.moduleRow(id);
    if (!m || !stIs("module", m.status, "listed")) return bad(res, "Unknown module", 404);
    const tid = Number(body.tenant_id);
    if (!get("SELECT id FROM tenants WHERE id=?", tid)) return bad(res, "Unknown store", 404);
    let invoice = null;
    const wasInstalled = (mods.installedRow(tid, id) || {}).status === "installed";
    if (!wasInstalled && m.price > 0) {
      const number = "MOD-" + (1000 + get("SELECT COUNT(*) c FROM invoices").c + 1);
      const r = run("INSERT INTO invoices(tenant_id,number,period_start,period_end,amount,currency,status,paid_at,note) VALUES(?,?,date('now'),date('now'),?,?,'paid',datetime('now'),?)",
        tid, number, m.price, m.currency || require("../defaults.js").platformCurrency(), `Module: ${m.name}`);
      run("INSERT INTO payments(tenant_id,kind,invoice_id,gateway,method,amount,currency,fee,status,txn_ref) VALUES(?,?,?,?,?,?,?,?,?,?)",
        tid, "module", Number(r.lastInsertRowid), "platform-billing", "invoice", m.price, m.currency || require("../defaults.js").platformCurrency(), 0, "captured", `mod_sim_${crypto.randomBytes(6).toString("hex")}`);
      invoice = number;
    }
    const cfg = Object.assign({}, body.config || {});
    mods.applyModule(tid, m, cfg);
    audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "module.install", "tenant_module", `${tid}:${id}`, { invoice }, ipOf(req));
    json(res, 200, { ok: true, module: id, invoice });
  }
  function apiModuleUninstall(req, res, url, s, body, id) {
    if (!requirePlatformSection(s, res, "modules", "write")) return;
    const m = mods.moduleRow(id); if (!m) return bad(res, "Unknown module", 404);
    mods.unapplyModule(Number(body.tenant_id), m);
    audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "module.uninstall", "tenant_module", `${body.tenant_id}:${id}`, {}, ipOf(req));
    json(res, 200, { ok: true });
  }
  function apiModuleConfigure(req, res, url, s, body, id) {
    if (!requirePlatformSection(s, res, "modules", "write")) return;
    const m = mods.moduleRow(id); if (!m) return bad(res, "Unknown module", 404);
    const tid = Number(body.tenant_id);
    run("UPDATE tenant_modules SET config=? WHERE tenant_id=? AND module_id=?", JSON.stringify(body.config || {}), tid, id);
    mods.applyModule(tid, m, body.config || {});
    audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "module.configure", "tenant_module", `${tid}:${id}`, { config: Object.keys(body.config || {}) }, ipOf(req));
    json(res, 200, { ok: true });
  }
  function apiStoreModules(req, res, url, s) {
    json(res, 200, { installed: mods.installed(T(s)).map(m => ({ id: m.module_id, name: m.name, category: m.category, capabilities: (m.manifest.capabilities || []), config: m.config, installed_at: m.installed_at })), capabilities: [...mods.caps(T(s))].filter(c => mods.hasCap(T(s), c)), gates: require("../gates.js").all(T(s)) });
  }
  function apiFlags(req, res, url, s) { if (!requirePlatform(s, res)) return; json(res, 200, { flags: env.flags() }); }
  function apiFlagSet(req, res, url, s, body, name) { if (!requirePlatform(s, res)) return; try { json(res, 200, { ok: true, flag: env.setFlag(name || body.name, body) }); } catch (e) { return bad(res, e.message); } }
  function apiFlagDelete(req, res, url, s, body, name) { if (!requirePlatform(s, res)) return; env.delFlag(String(name || "")); json(res, 200, { ok: true }); }
  /* one read renders the entire console: the catalog (what is configurable),
     the archetypes, and the selected tenant's live composition */
  function apiCapabilities(req, res, url, s) {
    if (!requireStaff(s, res)) return;
    /* a platform admin composes the master's own deployment by default — the
       deployment the platform itself is — and may read any additional deployment
       it provisioned through ?tenant_id= */
    const master = masterTenant();
    const tid = s.platform_admin && url.searchParams.get("tenant_id") ? Number(url.searchParams.get("tenant_id")) : T(s);
    /* `params` = the declared definitions (type/default/label — the form scaffolding);
       `effective` = this tenant's resolved values (defaults → preset → own overrides),
       empty while the capability is off, so the console tunes what it reads */
    /* settings_atom: the capability is also a storefront feature toggle (the console marks it) */
    const catalog = caps.catalog().map(c => ({ ...c, on: caps.on(tid, c.key), effective: caps.cap(tid, c.key), settings_atom: caps.STOREFRONT_KEYS.includes(c.key) }));
    json(res, 200, {
      catalog, presets: caps.presets(), composition: caps.compositionOf(tid), tenant_id: tid, domains: rl("capabilityDomains"), paramTypes: caps.PARAM_TYPES,
      master_id: master && master.id,
      tenants: s.platform_admin ? (all("SELECT id, slug, name FROM tenants ORDER BY id") || [])
        .map(t => ({ ...t, master: !!(master && t.id === master.id) }))
        .sort((a, b) => (b.master ? 1 : 0) - (a.master ? 1 : 0)) : undefined
    });
  }
  /* platform-level: switch a capability off for every store, or retitle it */
  function apiCapPlatform(req, res, url, s, body, key) {
    if (!requirePlatform(s, res)) return;
    try {
      const out = caps.setPlatform(String(key || "").trim(), { enabled: body.enabled, label: body.label, description: body.description });
      logAction(s, "capability.platform", "capability", String(key), { enabled: body.enabled }, req);
      json(res, 200, { capability: out });
    } catch (e) { bad(res, e.message, 409); }
  }
  /* switch a capability ON for a tenant, with optional param overrides */
  function apiCapEnable(req, res, url, s, body) {
    /* S3: capTenantScope only checked WHICH tenant, never that the caller is
       staff — so an anonymous shopper could recompose any store. The read
       (apiCapabilities) already gated on admin; the writes must too. */
    if (!requireStaff(s, res)) return;
    const tid = capTenantScope(s, body);
    if (tid === null) return bad(res, "You can only configure your own store", 403);
    try {
      const out = caps.enable(tid, String(body.capability || "").trim(), body.params || {}, body.notes);
      logAction(s, "capability.enable", "capability", String(body.capability), { tenant_id: tid }, req);
      json(res, 200, out);
    } catch (e) { bad(res, e.message, 409); }
  }
  function apiCapDisable(req, res, url, s, body) {
    if (!requireStaff(s, res)) return;
    const tid = capTenantScope(s, body);
    if (tid === null) return bad(res, "You can only configure your own store", 403);
    const out = caps.disable(tid, String(body.capability || "").trim());
    logAction(s, "capability.disable", "capability", String(body.capability), { tenant_id: tid }, req);
    json(res, 200, out);
  }
  /* tune ONE declared parameter — coerced to its declared type, and refused if
     the capability or parameter is unknown to the catalog */
  function apiCapParam(req, res, url, s, body) {
    if (!requireStaff(s, res)) return;
    const tid = capTenantScope(s, body);
    if (tid === null) return bad(res, "You can only configure your own store", 403);
    try {
      const out = caps.tune(tid, String(body.capability || "").trim(), String(body.param || "").trim(), body.value);
      logAction(s, "capability.param", "capability", String(body.capability) + "." + body.param, { tenant_id: tid, value: body.value }, req);
      json(res, 200, out);
    } catch (e) { bad(res, e.message, 409); }
  }
  /* apply a named archetype to a tenant */
  function apiCapPresetApply(req, res, url, s, body) {
    if (!requireStaff(s, res)) return;
    const tid = capTenantScope(s, body);
    if (tid === null) return bad(res, "You can only configure your own store", 403);
    try {
      const out = caps.applyPreset(tid, String(body.preset || "").trim());
      logAction(s, "capability.preset.apply", "capability_preset", String(body.preset), { tenant_id: tid }, req);
      json(res, 200, out);
    } catch (e) { bad(res, e.message, 409); }
  }
  /* author or rewrite an archetype — a platform-owned vocabulary */
  function apiCapPresetSave(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    try {
      const out = caps.savePreset(body.key, body.label, body.description, body.capabilities || {}, body.universes);
      logAction(s, "capability.preset.save", "capability_preset", String(body.key), req);
      json(res, 200, { preset: out });
    } catch (e) { bad(res, e.message, 409); }
  }
  function apiCapPresetDelete(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    const out = caps.removePreset(String(body.preset || "").trim());
    logAction(s, "capability.preset.delete", "capability_preset", String(body.preset), req);
    json(res, 200, out);
  }
  /* author a capability the seed never knew about — the open-ended catalog. This is
     what makes the platform any platform: surge pricing for mobility, creator
     payouts for video, lead scoring for a CRM, all as typed data */
  function apiCapDefine(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    try {
      const out = caps.define(body.key, body.label, body.domain, body.icon, body.description, body.params || {});
      logAction(s, "capability.define", "capability", String(body.key), { domain: body.domain }, req);
      json(res, 200, { capability: out });
    } catch (e) { bad(res, e.message, 409); }
  }
  function apiCapUndefine(req, res, url, s, body, key) {
    if (!requirePlatform(s, res)) return;
    try {
      const out = caps.undefine(String(key || "").trim());
      logAction(s, "capability.undefine", "capability", String(key), req);
      json(res, 200, out);
    } catch (e) { bad(res, e.message, 409); }
  }

  /* ---------------- shopper features (lib/features.js) ---------------- */
  const who = s => ({ tid: T(s), owner: ownerFor(s) });
  const fcall = async (res, fn) => { try { json(res, 200, await fn()); } catch (e) { engineFail(res, e); } };
  const fsec = key => (features.defs.get(String(key)) || {}).section || "studio";
  /* what the shopper has of each feature: shown on their account */
  function apiFeaturesMine(req, res, url, s) { fcall(res, () => ({ features: features.mine(who(s)) })); }
  /* what a feature shows anyone */
  function apiFeatureOpen(req, res, url, s, body, key) { fcall(res, () => features.open(String(key), { ...who(s), query: Object.fromEntries(url.searchParams) })); }
  /* something a shopper does with a feature */
  function apiFeatureAct(req, res, url, s, body, key, action) { fcall(res, () => features.act(String(key), String(action), { ...who(s), body: body || {} })); }
  /* a feature's rows and records, with the fields the console asks for */
  function apiAdminFeature(req, res, url, s, body, key) { if (requireSection(s, res, fsec(key), "read")) fcall(res, () => { const d = features.defs.get(String(key)); if (!d) throw features.fail("Unknown feature", 404); return { feature: d, on: features.on(T(s), d.key), rows: features.rows(T(s), d.key), list: features.on(T(s), d.key) ? features.staffList(T(s), d.key) : [] }; }); }
  /* adds or changes one of a feature's rows */
  function apiAdminFeatureSave(req, res, url, s, body, key) { if (requireSection(s, res, fsec(key), "write")) fcall(res, () => { const rows = features.save(T(s), String(key), body); logAction(s, "feature.save", "feature", key, body, req); return { rows }; }); }
  /* removes one of a feature's rows */
  function apiAdminFeatureDelete(req, res, url, s, body, key, id) { if (requireSection(s, res, fsec(key), "write")) fcall(res, () => { const rows = features.remove(T(s), String(key), id); logAction(s, "feature.remove", "feature", key + ":" + id, {}, req); return { rows }; }); }
  /* something staff do with one of a feature's records */
  function apiAdminFeatureAct(req, res, url, s, body, key, action, id) { if (requireSection(s, res, fsec(key), "write")) fcall(res, async () => { const out = await features.staffAct(String(key), String(action), { tid: T(s), id: Number(id), body: body || {}, actor: s.platform_admin ? s.platform_admin.email : "user:" + s.user_id }); logAction(s, "feature." + action, "feature", key + ":" + id, body, req); return out; }); }

  return [
    ["GET /api/features", apiFeaturesMine],
    ["GET /api/features/:key", (r, re, u, s, b, p) => apiFeatureOpen(r, re, u, s, b, p)],
    ["POST /api/features/:key/:action", (r, re, u, s, b, p, a) => apiFeatureAct(r, re, u, s, b, p, a)],
    ["GET /api/admin/features/:key", (r, re, u, s, b, p) => apiAdminFeature(r, re, u, s, b, p)],
    ["POST /api/admin/features/:key", (r, re, u, s, b, p) => apiAdminFeatureSave(r, re, u, s, b, p)],
    ["DELETE /api/admin/features/:key/:id", (r, re, u, s, b, p, i) => apiAdminFeatureDelete(r, re, u, s, b, p, i)],
    ["POST /api/admin/features/:key/:action/:id", (r, re, u, s, b, p, a, m, i) => apiAdminFeatureAct(r, re, u, s, b, p, a, i)],
    ["GET /api/capabilities", apiCapabilities],
    ["POST /api/capabilities/platform/:key", (r, re, u, s, b, p) => apiCapPlatform(r, re, u, s, b, p)],
    ["POST /api/capabilities/enable", apiCapEnable],
    ["POST /api/capabilities/disable", apiCapDisable],
    ["POST /api/capabilities/param", apiCapParam],
    ["POST /api/capabilities/preset/apply", apiCapPresetApply],
    ["POST /api/capabilities/preset", apiCapPresetSave],
    ["POST /api/capabilities/preset/delete", apiCapPresetDelete],
    ["POST /api/capabilities/catalog", apiCapDefine],
    ["DELETE /api/capabilities/catalog/:key", apiCapUndefine],
    ["GET /api/platform/flags", apiFlags],
    ["PUT /api/platform/flags/:name", (r, re, u, s, b, p) => apiFlagSet(r, re, u, s, b, p)],
    ["DELETE /api/platform/flags/:name", (r, re, u, s, b, p) => apiFlagDelete(r, re, u, s, b, p)],
    ["GET /api/platform/modules", apiPlatformModules],
    ["POST /api/platform/modules/:id/install", (r, re, u, s, b, p) => apiModuleInstall(r, re, u, s, b, p)],
    ["POST /api/platform/modules/:id/uninstall", (r, re, u, s, b, p) => apiModuleUninstall(r, re, u, s, b, p)],
    ["POST /api/platform/modules/:id/configure", (r, re, u, s, b, p) => apiModuleConfigure(r, re, u, s, b, p)],
    ["GET /api/modules", apiStoreModules],
    ["GET /api/market", apiMarket],
    ["POST /api/modules/purchase", apiModulePurchase],
    ["POST /api/modules/release", apiModuleRelease]
  ];
} };
