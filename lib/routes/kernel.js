/* LUXORA Platform — kernel domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the kernel domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "kernel", routes(kit) {
  const { CFG, EXPORT_FORMATS, J, T, all, applyExportScope, audit, authz, bad, csvOf, customProviders, entity, entityPerm, events, exportCols, get, globalmod, governance, json, logAction, meta, options, ownerFor, parseImportPayload, platformDataSection, platformEntityDef, platformWriteTenant, rbac, registry, requireAdmin, requirePlatform, requirePlatformRoute, requirePlatformSection, requireSection, rl, run, sampleValueFor, states, universeFieldsOf } = kit;

  function apiAdminEntityUsage(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { usage: all("SELECT * FROM entity_usage WHERE tenant_id=? ORDER BY at DESC", T(s)) });
  }
  function apiPlatformKinds(req, res, url, s) {
    if (!requirePlatformSection(s, res, "tenants", "read")) return;
    const counts = Object.fromEntries(all("SELECT mode, COUNT(*) n FROM tenants GROUP BY mode").map(r => [r.mode, r.n]));
    const presets = all("SELECT key,label,description FROM capability_presets ORDER BY label");
    const labels = (() => { try { return require("../canonical.js").consoleSec().adminLabels || {}; } catch (e) { return {}; } })();
    const navSec = (() => { try { return require("../canonical.js").consoleSec().adminNavSec || {}; } catch (e) { return {}; } })();
    const owners = authz.capabilitySections();
    const byKey = {};
    for (const [leaf, label] of Object.entries(labels)) { const k = navSec[leaf] || leaf; (byKey[k] = byKey[k] || []).push(label); }
    const sections = authz.SURFACES.store.filter(k => !/^app_/.test(k)).map(k => ({ key: k, label: (byKey[k] || [k]).join(" · "), capabilities: owners.get(k) || [] }));
    json(res, 200, { kinds: registry.kinds().map(k => ({ ...k, platforms: counts[k.key] || 0 })), presets, sections, defaults: registry.KIND_DEFAULTS });
  }
  function apiPlatformKindSave(req, res, url, s, body) {
    if (!requirePlatformSection(s, res, "tenants", "write")) return;
    const it = body && body.kind;
    if (!it || typeof it !== "object") return bad(res, "kind required", 400);
    const sections = it.sections == null ? null : (Array.isArray(it.sections) ? [...new Set(it.sections.map(String))] : it.sections);
    /* a section a capability owns is never on a kind's list — the capability decides it */
    const owned = authz.capabilitySections();
    const item = { key: String(it.key || "").trim(), name: String(it.name || "").trim().slice(0, 60), desc: String(it.desc || "").trim().slice(0, 200),
      needsIndustries: !!it.needsIndustries, noun: String(it.noun || "").trim().slice(0, 30) || registry.KIND_DEFAULTS.noun,
      nounPlural: String(it.nounPlural || "").trim().slice(0, 30) || registry.KIND_DEFAULTS.nounPlural, archetype: String(it.archetype || "").trim(),
      provision: it.provision && typeof it.provision === "object" ? Object.fromEntries(Object.keys(registry.KIND_DEFAULTS.provision).map(k => [k, it.provision[k] !== false])) : registry.KIND_DEFAULTS.provision,
      sections: Array.isArray(sections) ? sections.filter(k => !owned.has(k)) : sections };
    const r = registry.saveItem("deployModes", item);
    if (!r.ok) return bad(res, r.error, 400);
    audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "kind.save", "kind", item.key, { name: item.name, archetype: item.archetype });
    json(res, 200, { kind: registry.kind(item.key) });
  }
  function apiPlatformKindDelete(req, res, url, s, body, key) {
    if (!requirePlatformSection(s, res, "tenants", "write")) return;
    const r = registry.deleteItem("deployModes", decodeURIComponent(String(key || "")));
    if (!r.ok) return bad(res, r.error, 409);
    audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "kind.delete", "kind", r.key, {});
    json(res, 200, { ok: true });
  }
  function apiMeta(req, res, url, s) {
    const c = CFG(s);
    const tInds = J(s.tenant.industries, []);
    const allowed = tInds.length ? tInds : null;
    const reg = meta.registry(customProviders(T(s), "registry").reduce((o, m) => ({ ...o, ...m }), {}));
    json(res, 200, {
      /* every state machine's states (what each means, how it shows) and labelled moves, so a
         console asks by meaning instead of naming statuses */
      stateMachines: states.catalog(),
      /* the default row of each declared list and the platform currency (lib/defaults.js) */
      defaults: require("../defaults.js").all(),
      industries: allowed ? reg.industries.filter(i => allowed.includes(i.key)) : reg.industries,
      productTypes: reg.productTypes, lifecycle: rl("lifecycle"), lifecycleTransitions: rl("lifecycleTransitions"),
      relTypes: rl("relTypes"), mediaKinds: rl("mediaKinds"), packagingLevels: rl("packagingLevels"),
      uomUnits: rl("uomUnits"), uomConversions: rl("uomConversions"), sellerRoles: rl("sellerRoles"),
      identityFields: rl("identityFields"), shippingClasses: rl("shippingClasses"), contextGroups: rl("contextGroups"),
      serializedStatuses: rl("serializedStatuses"), serializedConditions: rl("serializedConditions"), variantAxes: rl("variantAxes"),
      complianceScopes: rl("complianceScopes"), complianceKinds: rl("complianceKinds"), complianceStatuses: rl("complianceStatuses"),
      supplierRoles: rl("supplierRoles"), supplierStatuses: rl("supplierStatuses"), paymentTerms: rl("paymentTerms"), incoterms: rl("incoterms"),
      localizationEntities: rl("localizationEntities"), contractStatuses: rl("contractStatuses"), tenderStatuses: rl("tenderStatuses"), linkStatuses: rl("linkStatuses"),
      providerKinds: rl("providerKinds"), aiCapabilityKeys: rl("aiCapabilityKeys"), aiCapabilities: rl("aiCapabilities"), aiPlans: rl("aiPlans"),
      offerTypes: rl("offerTypes"), offerScopes: rl("offerScopes"), offerChannels: rl("offerChannels"), offerDirections: rl("offerDirections"), offerFunders: rl("offerFunders"), couponKinds: rl("couponKinds"), stackingPolicies: rl("stackingPolicies"), offerStatuses: rl("offerStatuses"), couponStatuses: rl("couponStatuses"), walletOperations: require("../wallet.js").vocabulary().operations,
      verticals: reg.verticals, verticalFields: rl("verticalFields"), verticalTypes: rl("verticalTypes"), verticalContexts: rl("verticalContexts"), verticalTypeOf: rl("verticalTypeOf"),
      countries: registry.countries(), taxModes: registry.taxModes(),
      providers: { payment: registry.providerDefs("payment"), shipping: registry.providerDefs("shipping"), notification: registry.providerDefs("notification") },
      providersAi: registry.providerDefs("ai"),
      deployModes: registry.kinds(),
      tenant: { id: s.tenant.id, slug: s.tenant.slug, name: s.tenant.name, mode: s.tenant.mode, industries: J(s.tenant.industries, []) }
    });
  }
  function apiEntities(req, res, url, s) {
    const defs = entity.allEntities(T(s));
    const out = {};
    for (const [k, d] of Object.entries(defs)) {
      if (!entityPerm(s, d, false)) continue;
      /* options may be an inline array OR a string naming a registry vocabulary the console
         resolves client-side ("lifecycle", "productTypes"…). The string is what the console's
         fieldInput needs to populate the select — dropping it rendered those selects EMPTY,
         and collect() then submitted "" for the field, so editing a product silently wiped
         its lifecycle (unpublishing it) and its type. Both shapes are data, both are kept */
      out[k] = { ...d, fields: d.fields.map(f => ({ ...f, options: (Array.isArray(f.options) || typeof f.options === "string") ? f.options : undefined })) };
    }
    json(res, 200, { entities: out });
  }
  function apiEntityList(req, res, url, s, body, key) {
    const defs = entity.allEntities(T(s));
    const def = defs[key];
    if (!def) return bad(res, "Unknown entity", 404);
    if (!entityPerm(s, def, false)) return bad(res, "Not permitted", 403);
    if (!requireSection(s, res, rbac.sectionForEntity(key), "read")) return;
    const hide = governance.isSoft(key) && url.searchParams.get("trash") !== "1";
    run("INSERT INTO entity_usage(tenant_id,entity,action,at) VALUES(?,?,?,datetime('now')) ON CONFLICT(tenant_id,entity,action) DO UPDATE SET at=datetime('now')", T(s), key, "list");
    /* pass server-side filters into the entity engine: `q` (free text) and any other
       search param (field equality). Both are whitelisted and parameterized in the engine,
       which is what makes an entity such as `sku` queryable past the browse cap once the
       corpus is activated (~2,000 SKUs on the flagship). */
    const where = {};
    for (const [k, v] of url.searchParams.entries()) if (k !== "q" && k !== "trash") where[k] = v;
    const opts = { hideDeleted: hide, q: url.searchParams.get("q") || "" };
    if (Object.keys(where).length) opts.where = where;
    json(res, 200, { entity: key, rows: entity.listEntities(T(s), key, opts) });
  }
  function apiEntityCreate(req, res, url, s, body, key) {
    const defs = entity.allEntities(T(s));
    const def = defs[key];
    if (!def) return bad(res, "Unknown entity", 404);
    if (!entityPerm(s, def, true)) return bad(res, "Not permitted", 403);
    if (!requireSection(s, res, rbac.sectionForEntity(key), "write")) return;
    const r = entity.createEntity(T(s), key, body || {});
    if (r.error) return bad(res, r.error);
    run("INSERT INTO entity_usage(tenant_id,entity,action,at) VALUES(?,?,?,datetime('now')) ON CONFLICT(tenant_id,entity,action) DO UPDATE SET at=datetime('now')", T(s), key, "create");
    logAction(s, key + ".create", key, r.id, body);
    json(res, 200, { ok: true, id: r.id });
  }
  function apiEntityUpdate(req, res, url, s, body, key, id) {
    const defs = entity.allEntities(T(s));
    const def = defs[key];
    if (!def) return bad(res, "Unknown entity", 404);
    if (!entityPerm(s, def, true)) return bad(res, "Not permitted", 403);
    if (!requireSection(s, res, rbac.sectionForEntity(key), "write")) return;
    const r = entity.updateEntity(T(s), key, id, body || {});
    if (r.error) return bad(res, r.error, r.code || 400);
    run("INSERT INTO entity_usage(tenant_id,entity,action,at) VALUES(?,?,?,datetime('now')) ON CONFLICT(tenant_id,entity,action) DO UPDATE SET at=datetime('now')", T(s), key, "update");
    logAction(s, key + ".update", key, id, body);
    json(res, 200, { ok: true });
  }
  function apiEntityDelete(req, res, url, s, body, key, id) {
    const defs = entity.allEntities(T(s));
    const def = defs[key];
    if (!def) return bad(res, "Unknown entity", 404);
    if (!entityPerm(s, def, true)) return bad(res, "Not permitted", 403);
    if (!requireSection(s, res, rbac.sectionForEntity(key), "write")) return;
    if (key === "currency") {
      if (require("../places.js").using("currency", String(id).toUpperCase()).length) return bad(res, "Currency is the official currency of a country entity — reassign that country first");
      if (all("SELECT value FROM settings WHERE key='commerce'").some(r => JSON.stringify(r).includes('"' + id + '"'))) return bad(res, "Currency in use by a store — switch that store's currency first");
    }
    if (governance.isSoft(key) && url.searchParams.get("hard") !== "1") {
      const t = governance.trash(T(s), key, id);
      if (t.error) return bad(res, t.error, t.code || 400);
      logAction(s, key + ".trash", key, id);
      return json(res, 200, { ok: true, trashed: true });
    }
    const r = entity.deleteEntity(T(s), key, id);
    if (r.error) return bad(res, r.error);
    logAction(s, key + ".delete", key, id);
    json(res, 200, { ok: true });
  }
  function apiEntityDefSave(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    const key = String(body.key || "").trim().toLowerCase().replace(/[^a-z0-9_]/g, "");
    if (!key || !body.label || !Array.isArray(body.fields)) return bad(res, "key, label and fields[] required");
    const def = { table: null, storage: "json", pk: "id", label: String(body.label), icon: String(body.icon || "🧬"), perm: { read: ["admin", "platform"], write: ["admin", "platform"] }, fields: body.fields };
    run("INSERT INTO entity_defs(key,scope,tenant_id,def) VALUES(?,?,?,?) ON CONFLICT(key,scope,tenant_id) DO UPDATE SET def=excluded.def",
      key, "platform", 0, JSON.stringify(def));
    logAction(s, "entity_def.save", "entity_def", key);
    json(res, 200, { ok: true });
  }
   function apiEntityDefsList(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    const { ENTITY_DEFS } = require("../entity.js");
    const custom = all("SELECT key, scope, tenant_id, def FROM entity_defs WHERE scope='platform'");
    const customKeys = new Set(custom.map(r => r.key));
    const builtIn = Object.entries(ENTITY_DEFS).map(([key, def]) => ({
      key, def: JSON.stringify(def), isBuiltIn: true
    }));
    const customRows = custom.map(r => ({ ...r, isBuiltIn: false }));
    json(res, 200, { rows: [...builtIn, ...customRows] });
  }
   function apiEntityDefDelete(req, res, url, s, body, key) {
    if (!requirePlatform(s, res)) return;
    run("DELETE FROM entity_defs WHERE key=? AND scope='platform'", key);
    run("DELETE FROM entity_data WHERE entity=?", key);
    logAction(s, "entity_def.delete", "entity_def", key);
    json(res, 200, { ok: true });
  }
   function apiEntityDefEnable(req, res, url, s, body, key) {
    if (!requirePlatform(s, res)) return;
    const tenantId = url.searchParams.get("tenant_id");
    if (!tenantId) return bad(res, "tenant_id required", 400);
    const { ENTITY_DEFS } = require("../entity.js");
    const platformDef = ENTITY_DEFS[key];
    const defStr = platformDef ? JSON.stringify(platformDef) : "{}";
    run("INSERT INTO entity_defs(key,scope,tenant_id,def) VALUES(?,?,?,?) ON CONFLICT(key,scope,tenant_id) DO UPDATE SET def=excluded.def",
      key, "tenant", Number(tenantId), defStr);
    logAction(s, "entity_def.enable", "entity_def", key);
    json(res, 200, { ok: true });
  }
   function apiEntityDefDisable(req, res, url, s, body, key) {
    if (!requirePlatform(s, res)) return;
    const tenantId = url.searchParams.get("tenant_id");
    if (!tenantId) return bad(res, "tenant_id required", 400);
    run("DELETE FROM entity_defs WHERE key=? AND scope='tenant' AND tenant_id=?", key, Number(tenantId));
    logAction(s, "entity_def.disable", "entity_def", key);
    json(res, 200, { ok: true });
  }
   function apiTenantEntityDefs(req, res, url, s) {
    const tenantId = T(s);
    const rows = all("SELECT key, def FROM entity_defs WHERE scope='tenant' AND tenant_id=?", tenantId);
    const out = {};
    for (const r of rows) { try { out[r.key] = JSON.parse(r.def || "{}"); } catch (e) { } }
    json(res, 200, { entities: out });
  }
  /* ========== Global Entity Configuration API ========== */
  function apiEntityTypeList(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    const entity = url.searchParams.get('entity');
    const q = entity ? 'WHERE entity=?' : '';
    const p = entity ? [entity] : [];
    json(res, 200, { types: all(`SELECT * FROM entity_types ${q} ORDER BY entity, type_key`, ...p) });
  }
  function apiEntityTypeCreate(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    if (!body.entity || !body.type_key || !body.label) return bad(res, 'entity, type_key, label required', 400);
    run('INSERT INTO entity_types(entity,type_key,label,icon,fields,config) VALUES(?,?,?,?,?,?)',
      body.entity, body.type_key, body.label, body.icon || '📝', JSON.stringify(body.fields || []), JSON.stringify(body.config || {}));
    logAction(s, 'entity_type.create', 'entity_type', `${body.entity}:${body.type_key}`);
    json(res, 200, { ok: true });
  }
  function apiEntityTypeUpdate(req, res, url, s, body, entity, type_key) {
    if (!requirePlatform(s, res)) return;
    run('UPDATE entity_types SET label=?, icon=?, fields=?, config=? WHERE entity=? AND type_key=?',
      body.label, body.icon, JSON.stringify(body.fields || []), JSON.stringify(body.config || {}), entity, type_key);
    logAction(s, 'entity_type.update', 'entity_type', `${entity}:${type_key}`);
    json(res, 200, { ok: true });
  }
  function apiEntityTypeDelete(req, res, url, s, body, entity, type_key) {
    if (!requirePlatform(s, res)) return;
    run('DELETE FROM entity_types WHERE entity=? AND type_key=?', entity, type_key);
    logAction(s, 'entity_type.delete', 'entity_type', `${entity}:${type_key}`);
    json(res, 200, { ok: true });
  }
  /* ---------- Global Platform: cross-tenant commerce data ----------
     One generic reader serves every entity-backed store capability. The Store Console
     reads ONE tenant through /api/meta/entity/:key; the Platform Console reads ACROSS
     stores through /api/platform/data/:key. Both resolve through the same definitions,
     the same field whitelist and the same parameterized predicates in lib/entity.js, so
     a capability's data model is defined exactly once — the platform never forks a store's
     schema, and the store never diverges from the platform.
     GET /api/platform/data enumerates the served entities so the console builds its Global
     Operations surface from live metadata rather than a hardcoded menu (zero hard-coding). */
  function apiPlatformDataIndex(req, res, url, s) {
    if (!requirePlatformSection(s, res, "gdata", "read")) return;
    const defs = entity.allEntities(null);
    /* the index carries each entity's list-visible fields and pk so the console renders a
       cross-store table without a second field-definition copy anywhere (the Store Console
       reads the very same defs through /api/meta/entities). */
    /* platform-level registries (countries, currencies, tax modes, the uv_* universes…)
       are datasets too — they are what a Geography or Tenants leaf is about — so only the
       storage kind gates the index, never the scope. Excluding them made such a leaf fall
       through to the universe view and render the wrong records with no editor */
    const entities = Object.entries(defs)
      .filter(([key, def]) => def.storage === "json" || def.table)
      .map(([key, def]) => ({
        key, name: def.name || key, soft: governance.isSoft(key),
        /* a platform-level registry carries no store column; the console renders one only
           for genuinely store-scoped datasets (the same test the reader's `multi` makes) */
        tenantScoped: !(def.platformOnly || def.noTenant), pk: def.pk || "id",
        pkType: def.pkType === "text" ? "text" : "number",
        writable: (def.perm.write || []).includes("platform"),
        fields: (def.fields || []).filter(f => f.list).map(f => ({ key: f.key, label: f.label, type: f.type, ...(f.display ? { display: f.display } : {}) }))
      }))
      .sort((a, b) => a.key.localeCompare(b.key));
    const tenants = all("SELECT id, name, slug FROM tenants ORDER BY name").map(t => ({ id: t.id, name: t.name, slug: t.slug }));
    json(res, 200, { entities, tenants });
  }
  function apiPlatformDataList(req, res, url, s, body, key) {
    if (!requirePlatformSection(s, res, platformDataSection(key), "read")) return;
    const opts = { q: url.searchParams.get("q") || "", limit: url.searchParams.get("limit") || 500 };
    const hide = governance.isSoft(key) && url.searchParams.get("trash") !== "1";
    if (hide) opts.hideDeleted = true;
    const tenantId = url.searchParams.get("tenant_id");
    if (tenantId) opts.tenantId = tenantId;
    /* the same whitelisted, parameterized field predicates the store endpoint accepts —
       nothing arbitrary reaches SQL, and a platform query is as bounded as a store one */
    const where = {};
    for (const [k, v] of url.searchParams.entries())
      if (!["q", "trash", "tenant_id", "limit"].includes(k)) where[k] = v;
    if (Object.keys(where).length) opts.where = where;
    const rows = entity.listEntitiesGlobal(key, opts);
    if (rows === null) return bad(res, "Unknown entity", 404);
    json(res, 200, { entity: key, rows });
  }
  function apiPlatformDataDef(req, res, url, s, body, key) {
    if (!requirePlatformSection(s, res, platformDataSection(key), "read")) return;
    const def = platformEntityDef(key, null);
    if (!def || !(def.storage === "json" || def.table)) return bad(res, "Unknown entity", 404);
    json(res, 200, {
      key, name: def.name || key, label: def.label, icon: def.icon,
      pk: def.pk || "id", pkType: def.pkType === "text" ? "text" : "number",
      composite: !!def.composite, storage: def.storage,
      platformLevel: !!(def.platformOnly || def.noTenant),
      writable: (def.perm.write || []).includes("platform"),
      fields: def.fields.map(f => ({ ...f, options: (Array.isArray(f.options) || typeof f.options === "string") ? f.options : undefined }))
    });
  }
  function apiPlatformDataCreate(req, res, url, s, body, key) {
    if (!requirePlatformRoute(s, res, url, "write")) return;
    const tidRaw = Number((body && body.tenant_id) || url.searchParams.get("tenant_id")) || null;
    const def = platformEntityDef(key, tidRaw);
    if (!def) return bad(res, "Unknown entity", 404);
    if (!entityPerm(s, def, true)) return bad(res, "Not permitted", 403);
    const tid = platformWriteTenant(def, tidRaw, res); if (tid == null) return;
    const row = { ...(body || {}) }; if (def.storage === "json") delete row.tenant_id;  /* the target tenant is metadata of the write, not a field */
    const r = entity.createEntity(tid, key, row);
    if (r.error) return bad(res, r.error);
    logAction(s, key + ".create", key, r.id, Object.assign({ scope: tid }, row), req);
    json(res, 200, { ok: true, id: r.id });
  }
  function apiPlatformDataUpdate(req, res, url, s, body, key, id) {
    if (!requirePlatformRoute(s, res, url, "write")) return;
    const tidRaw = Number((body && body.tenant_id) || url.searchParams.get("tenant_id")) || null;
    const def = platformEntityDef(key, tidRaw);
    if (!def) return bad(res, "Unknown entity", 404);
    if (!entityPerm(s, def, true)) return bad(res, "Not permitted", 403);
    const tid = platformWriteTenant(def, tidRaw, res); if (tid == null) return;
    const row = { ...(body || {}) }; if (def.storage === "json") delete row.tenant_id;
    const r = entity.updateEntity(tid, key, id, row);
    if (r.error) return bad(res, r.error, r.code || 400);
    logAction(s, key + ".update", key, id, row, req);
    json(res, 200, { ok: true });
  }
  function apiPlatformDataDelete(req, res, url, s, body, key, id) {
    if (!requirePlatformRoute(s, res, url, "write")) return;
    const tidRaw = Number((body && body.tenant_id) || url.searchParams.get("tenant_id")) || null;
    const def = platformEntityDef(key, tidRaw);
    if (!def) return bad(res, "Unknown entity", 404);
    if (!entityPerm(s, def, true)) return bad(res, "Not permitted", 403);
    const tid = platformWriteTenant(def, tidRaw, res); if (tid == null) return;
    if (key === "currency") {
      if (require("../places.js").using("currency", String(id).toUpperCase()).length) return bad(res, "Currency is the official currency of a country entity — reassign that country first");
      if (all("SELECT value FROM settings WHERE key='commerce'").some(r => JSON.stringify(r).includes('"' + String(id) + '"'))) return bad(res, "Currency in use by a store — switch that store's currency first");
    }
    if (key === "country") {
      /* a country is the jurisdiction of stores and the availability anchor of every payment
         provider seeded for it, so the engine's raw FK refusal is replaced by the two facts
         an operator can actually act on */
      /* the stores serving it, or a place in it, are answered by the kernel (lib/stores.js) */
      if (require("../stores.js").serving(String(id).toUpperCase()).length) return bad(res, "A store serves this country — switch that store's jurisdiction and places first");
      /* the availability links to global providers are DERIVED — reconciliation materialised them
         the moment the country was created, so they are not an operator's per-provider choice.
         Blocking deletion on them would make every country undeletable. They are cleaned up here
         instead, and the exemptions an operator set for this country go with it, so removing a
         country leaves no dangling edges for reconciliation to trip over on the next boot */
      const cc = String(id).toUpperCase();
      run("DELETE FROM provider_availability WHERE country_code=?", cc);
      /* a country's subdivisions are derived from it, so they leave with it — no dangling
         jurisdiction rows (an address still pointing at a removed country's state reads its
         stored code; the master it resolved from is simply gone) */
      registry.withdrawCountry(cc);
      try {
        const exRow = get("SELECT value v FROM platform_settings WHERE key='provider_availability_exempt'");
        if (exRow) { const list = JSON.parse(exRow.v || "[]").filter(x => !x.endsWith("|" + cc)); run("INSERT INTO platform_settings(key,value) VALUES('provider_availability_exempt',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", JSON.stringify(list)); }
      } catch (e) { }
    }
    if (governance.isSoft(key) && url.searchParams.get("hard") !== "1") {
      const t = governance.trash(tid, key, id);
      if (t.error) return bad(res, t.error, t.code || 400);
      logAction(s, key + ".trash", key, id, {}, req);
      return json(res, 200, { ok: true, trashed: true });
    }
    const r = entity.deleteEntity(tid, key, id);
    if (r.error) return bad(res, r.error);
    logAction(s, key + ".delete", key, id, {}, req);
    json(res, 200, { ok: true });
  }
  function apiPlatformDataImport(req, res, url, s, body, key) {
    if (!requirePlatformRoute(s, res, url, "write")) return;
    const tidRaw = Number((body && body.tenant_id) || url.searchParams.get("tenant_id")) || null;
    const def = platformEntityDef(key, tidRaw);
    if (!def) return bad(res, "Unknown entity", 404);
    if (!entityPerm(s, def, true)) return bad(res, "Not permitted", 403);
    const tid = platformWriteTenant(def, tidRaw, res); if (tid == null) return;
    const rows = parseImportPayload(body);
    if (!rows || !Array.isArray(rows)) return bad(res, "No records — send a JSON array, {rows:[…]}, {json:\"…\"} or {csv:\"…\"}", 400);
    if (rows.length > 5000) return bad(res, "Import is capped at 5,000 records per call — split the file", 400);
    let imported = 0; const failed = [];
    rows.forEach((raw, i) => {
      if (!raw || typeof raw !== "object" || Array.isArray(raw)) { failed.push({ index: i + 1, error: "not a record object" }); return; }
      const row = { ...raw }; if (def.storage === "json") delete row.tenant_id;
      const r = entity.createEntity(tid, key, row);
      if (r.error) failed.push({ index: i + 1, error: r.error });
      else imported++;
    });
    logAction(s, key + ".import", key, null, { imported, rejected: failed.length, scope: tid }, req);
    json(res, 200, { ok: true, imported, failed });
  }
  function apiPlatformDataExport(req, res, url, s, body, key) {
    if (!requirePlatformRoute(s, res, url, "read")) return;
    const def = platformEntityDef(key, null);
    if (!def) return bad(res, "Unknown entity", 404);
    /* the console's format menu is discovered, not hardcoded: ?format=formats answers the
       registry itself, so a format added above is selectable with no client change */
    const fmtParam = String(url.searchParams.get("format") || "csv").toLowerCase();
    if (fmtParam === "formats" || fmtParam === "list")
      return json(res, 200, { formats: Object.entries(EXPORT_FORMATS).map(([k, v]) => ({ key: k, label: v.label, ext: v.ext })) });
    const fmt = EXPORT_FORMATS[fmtParam] || (/json/i.test(fmtParam) ? EXPORT_FORMATS.json : EXPORT_FORMATS.csv);
    const opts = { q: url.searchParams.get("q") || "", limit: 5000 };
    const hide = governance.isSoft(key) && url.searchParams.get("trash") !== "1";
    if (hide) opts.hideDeleted = true;
    const tenantId = url.searchParams.get("tenant_id");
    if (tenantId) opts.tenantId = tenantId;
    let rows = entity.listEntitiesGlobal(key, opts);
    if (rows === null) return bad(res, "Unknown entity", 404);
    rows = applyExportScope(rows, def, url);
    const cols = exportCols(def);
    const name = String(key).replace(/[^\w.-]/g, "_");
    const out = fmt.render(rows, cols, key, `${rows.length} record${rows.length === 1 ? "" : "s"} · exported ${new Date().toISOString().slice(0, 16).replace("T", " ")} UTC`);
    res.writeHead(200, { "Content-Type": fmt.ct, "Content-Disposition": "attachment; filename=\"" + name + "." + fmt.ext + "\"" });
    res.end(Buffer.isBuffer(out) ? out : String(out));
  }
  function apiPlatformDataSample(req, res, url, s, body, key) {
    if (!requirePlatformRoute(s, res, url, "read")) return;
    const def = platformEntityDef(key, null);
    if (!def || !(def.storage === "json" || def.table)) return bad(res, "Unknown entity", 404);
    const row = {};
    for (const f of def.fields)
      if (!f.readonly) row[f.key] = sampleValueFor(f);
    const pk = def.pk || "id";
    if (!(pk in row) && def.pkType === "text") row[pk] = "SAMPLE";
    const fmt = /json/i.test(String(url.searchParams.get("format"))) ? "json" : "csv";
    const name = String(key).replace(/[^\w.-]/g, "_") + "-sample";
    if (fmt === "json") {
      res.writeHead(200, { "Content-Type": "application/json; charset=utf-8", "Content-Disposition": "attachment; filename=\"" + name + ".json\"" });
      res.end(JSON.stringify([row], null, 1));
      return;
    }
    const cols = exportCols(def);
    res.writeHead(200, { "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": "attachment; filename=\"" + name + ".csv\"" });
    res.end(csvOf([row], cols));
  }
  function apiEntityAttributeList(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    const entity = url.searchParams.get('entity');
    const q = entity ? 'WHERE entity=?' : '';
    const p = entity ? [entity] : [];
    json(res, 200, { attributes: all(`SELECT * FROM entity_attributes ${q} ORDER BY position`, ...p) });
  }
  function apiEntityAttributeAttach(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    if (!body.entity || !body.attribute_key) return bad(res, 'entity and attribute_key required', 400);
    run('INSERT INTO entity_attributes(entity,attribute_key,position) VALUES(?,?,?) ON CONFLICT(entity,attribute_key) DO UPDATE SET position=excluded.position',
      body.entity, body.attribute_key, body.position || 0);
    logAction(s, 'entity_attribute.attach', 'entity_attribute', `${body.entity}:${body.attribute_key}`);
    json(res, 200, { ok: true });
  }
  function apiEntityTags(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    const entity = String(url.searchParams.get("entity") || ""), uid = String(url.searchParams.get("uid") || "");
    const row = get("SELECT tags, meta, notes FROM entity_meta WHERE tenant_id=? AND entity=? AND ref_uid=?", T(s), entity, uid);
    json(res, 200, { entity, uid, tags: row ? J(row.tags, []) : [], meta: row ? J(row.meta, {}) : {}, notes: row ? row.notes : "" });
  }
  function apiEntityTagsSave(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const entity = String(body.entity || ""), uid = String(body.uid || ""); if (!entity || !uid) return bad(res, "entity and uid required");
    run(`INSERT INTO entity_meta(tenant_id,entity,ref_uid,tags,meta,notes,updated_at) VALUES(?,?,?,?,?,?,datetime('now'))
         ON CONFLICT(tenant_id,entity,ref_uid) DO UPDATE SET tags=excluded.tags, meta=excluded.meta, notes=excluded.notes, updated_at=datetime('now')`,
      T(s), entity, uid, JSON.stringify(body.tags || []), JSON.stringify(body.meta || {}), String(body.notes || ""));
    logAction(s, "entity_meta.save", entity, uid); json(res, 200, { ok: true });
  }
  /* ---------- global console (Countries, Currencies, Providers, Plans) ---------- */
  function apiGlobalCountries(req, res, url, s) { if (!requirePlatform(s, res)) return; json(res, 200, { countries: globalmod.listCountries() }); }
  function apiGlobalCountryGet(req, res, url, s) { if (!requirePlatform(s, res)) return; const code = url.searchParams.get("code"); if (!code) return bad(res, "code required", 400); json(res, 200, { country: globalmod.getCountry(code) }); }
  function apiGlobalCountryPost(req, res, url, s, body) { if (!requirePlatformSection(s, res, "geo", "write")) return; if (!body || !body.code) return bad(res, "code required", 400); const r = globalmod.createCountry(body); json(res, r.ok ? 200 : 400, r); }
  function apiGlobalCountryPut(req, res, url, s, body) { if (!requirePlatformSection(s, res, "geo", "write")) return; const code = url.searchParams.get("code"); if (!code || !body) return bad(res, "code and data required", 400); const r = globalmod.updateCountry(code, body); json(res, r.ok ? 200 : 400, r); }
  function apiGlobalCurrencies(req, res, url, s) { if (!requirePlatform(s, res)) return; json(res, 200, { currencies: globalmod.listCurrencies() }); }
  function apiGlobalCurrencyGet(req, res, url, s) { if (!requirePlatform(s, res)) return; const code = url.searchParams.get("code"); if (!code) return bad(res, "code required", 400); json(res, 200, { currency: globalmod.getCurrency(code) }); }
  function apiGlobalCurrencyPost(req, res, url, s, body) { if (!requirePlatformSection(s, res, "geo", "write")) return; if (!body || !body.code) return bad(res, "code required", 400); const r = globalmod.createCurrency(body); json(res, r.ok ? 200 : 400, r); }
  function apiGlobalCurrencyPut(req, res, url, s, body) { if (!requirePlatformSection(s, res, "geo", "write")) return; const code = url.searchParams.get("code"); if (!code || !body) return bad(res, "code and data required", 400); const r = globalmod.updateCurrency(code, body); json(res, r.ok ? 200 : 400, r); }
  function apiGlobalProviders(req, res, url, s) { if (!requirePlatform(s, res)) return; const kind = url.searchParams.get("kind"); json(res, 200, { providers: globalmod.listProviders(kind) }); }
  function apiGlobalProviderGet(req, res, url, s) { if (!requirePlatform(s, res)) return; const id = url.searchParams.get("id"); const kind = url.searchParams.get("kind"); if (!id || !kind) return bad(res, "id and kind required", 400); json(res, 200, { provider: globalmod.getProvider(id, kind) }); }
  function apiGlobalProviderPost(req, res, url, s, body) { if (!requirePlatformSection(s, res, "providers", "write")) return; if (!body || !body.id || !body.kind) return bad(res, "id and kind required", 400); json(res, 200, globalmod.createProvider(body)); }
  function apiGlobalProviderPut(req, res, url, s, body) { if (!requirePlatform(s, res)) return; const id = url.searchParams.get("id"); const kind = url.searchParams.get("kind"); if (!id || !kind || !body) return bad(res, "id, kind, and data required", 400); json(res, 200, globalmod.updateProvider(id, kind, body)); }
  function apiGlobalProviderAvailability(req, res, url, s) { if (!requirePlatform(s, res)) return; const providerId = url.searchParams.get("provider_id"); if (!providerId) return bad(res, "provider_id required", 400); json(res, 200, { availability: globalmod.listProviderAvailability(providerId) }); }
  function apiGlobalProviderEnableCountry(req, res, url, s, body) { if (!requirePlatformSection(s, res, "providers", "write")) return; const providerId = url.searchParams.get("provider_id"); const code = url.searchParams.get("code"); if (!providerId || !code) return bad(res, "provider_id and code required", 400); json(res, 200, globalmod.enableProviderInCountry(providerId, code)); }
  function apiGlobalProviderDisableCountry(req, res, url, s) { if (!requirePlatformSection(s, res, "providers", "write")) return; const providerId = url.searchParams.get("provider_id"); const code = url.searchParams.get("code"); if (!providerId || !code) return bad(res, "provider_id and code required", 400); json(res, 200, globalmod.disableProviderInCountry(providerId, code)); }
  function apiGlobalPlans(req, res, url, s) { if (!requirePlatform(s, res)) return; json(res, 200, { plans: globalmod.listPlans() }); }
  function apiGlobalPlanGet(req, res, url, s) { if (!requirePlatform(s, res)) return; const id = url.searchParams.get("id"); if (!id) return bad(res, "id required", 400); json(res, 200, { plan: globalmod.getPlan(id) }); }
  function apiGlobalPlanPost(req, res, url, s, body) { if (!requirePlatform(s, res)) return; if (!body || !body.name) return bad(res, "name required", 400); json(res, 200, globalmod.createPlan(body)); }
  function apiGlobalPlanPut(req, res, url, s, body) { if (!requirePlatform(s, res)) return; const id = url.searchParams.get("id"); if (!id || !body) return bad(res, "id and data required", 400); json(res, 200, globalmod.updatePlan(id, body)); }
  function apiGlobalTenantConfig(req, res, url, s) { if (!requirePlatform(s, res)) return; const tenantId = url.searchParams.get("tenant_id"); if (!tenantId) return bad(res, "tenant_id required", 400);
    json(res, 200, {
      country: globalmod.getTenantCountry(tenantId),
      currency: globalmod.getTenantCurrency(tenantId),
      providers: globalmod.getTenantProviders(tenantId),
      plan: globalmod.getTenantPlan(tenantId)
    });
  }
  function apiGlobalTenantCountry(req, res, url, s, body) { if (!requirePlatform(s, res)) return; const tenantId = url.searchParams.get("tenant_id"); const code = url.searchParams.get("code"); if (!tenantId || !code) return bad(res, "tenant_id and code required", 400); json(res, 200, globalmod.setTenantCountry(tenantId, code)); }
  function apiGlobalTenantCurrency(req, res, url, s, body) { if (!requirePlatform(s, res)) return; const tenantId = url.searchParams.get("tenant_id"); const code = url.searchParams.get("code"); if (!tenantId || !code) return bad(res, "tenant_id and code required", 400); json(res, 200, globalmod.setTenantCurrency(tenantId, code)); }
  function apiGlobalTenantProviders(req, res, url, s) { if (!requirePlatform(s, res)) return; const tenantId = url.searchParams.get("tenant_id"); const kind = url.searchParams.get("kind"); if (!tenantId) return bad(res, "tenant_id required", 400); json(res, 200, { providers: globalmod.getTenantProviders(tenantId, kind) }); }
  function apiGlobalTenantProviderPost(req, res, url, s, body) { if (!requirePlatform(s, res)) return; const tenantId = url.searchParams.get("tenant_id"); const providerId = url.searchParams.get("provider_id"); const kind = url.searchParams.get("kind") || "payment"; if (!tenantId || !providerId) return bad(res, "tenant_id and provider_id required", 400); json(res, 200, globalmod.addTenantProvider(tenantId, providerId, kind, body || {})); }
  function apiGlobalTenantProviderDelete(req, res, url, s) { if (!requirePlatform(s, res)) return; const tenantId = url.searchParams.get("tenant_id"); const providerId = url.searchParams.get("provider_id"); const kind = url.searchParams.get("kind") || "payment"; if (!tenantId || !providerId) return bad(res, "tenant_id and provider_id required", 400); json(res, 200, globalmod.removeTenantProvider(tenantId, providerId, kind)); }
  function apiGlobalTenantPlan(req, res, url, s, body) { if (!requirePlatform(s, res)) return; const tenantId = url.searchParams.get("tenant_id"); const planId = url.searchParams.get("plan_id"); if (!tenantId || !planId) return bad(res, "tenant_id and plan_id required", 400); json(res, 200, globalmod.assignTenantPlan(tenantId, planId)); }
  function apiRegistriesList(req, res, url, s) {
    const rows = s.user_id
      ? all("SELECT * FROM gift_registries WHERE tenant_id=? AND owner=? ORDER BY id DESC", T(s), ownerFor(s))
      : [];
    json(res, 200, { registries: rows });
  }
  function apiRegistryCreate(req, res, url, s, body) {
    if (!s.user_id) return bad(res, "Sign in to create a registry", 401);
    const name = String(body.name || "").trim();
    if (!name) return bad(res, "Registry name required");
    const events = registry.list("shopEvents").map(x => x.key || x);
    const ref = "REG-" + Date.now().toString(36).toUpperCase().slice(-6);
    const r = run("INSERT INTO gift_registries(tenant_id,ref,owner,name,event,event_date,shipping_address,notes,items,contributors,status) VALUES(?,?,?,?,?,?,?,?, '[]','[]','open')",
      T(s), ref, ownerFor(s), name, events.includes(body.event) ? body.event : "wedding",
      body.event_date || null, String(body.shipping_address || ""), String(body.notes || ""));
    json(res, 200, { registry: get("SELECT * FROM gift_registries WHERE id=?", r.lastInsertRowid) });
  }
  function apiRegistryItem(req, res, url, s, body, id) {
    const reg = get("SELECT * FROM gift_registries WHERE id=? AND tenant_id=? AND owner=?", Number(id), T(s), ownerFor(s));
    if (!reg) return bad(res, "Registry not found", 404);
    const items = JSON.parse(reg.items || "[]");
    const pid = String(body.product_id || "");
    if (body.remove) {
      const next = items.filter(x => x.product_id !== pid);
      run("UPDATE gift_registries SET items=? WHERE id=?", JSON.stringify(next), reg.id);
    } else if (pid && !items.some(x => x.product_id === pid)) {
      items.push({ product_id: pid, qty: Number(body.qty) || 1, purchased: 0 });
      run("UPDATE gift_registries SET items=? WHERE id=?", JSON.stringify(items), reg.id);
    }
    json(res, 200, { registry: get("SELECT * FROM gift_registries WHERE id=?", reg.id) });
  }
  function apiUniverseFields(req, res, url, s, body, key) {
    if (!requirePlatform(s, res)) return;
    json(res, 200, universeFieldsOf(String(key || "")));
  }
  /* ======================================================================
     PLATFORM REGISTRY AUTHORING — every `meta_lists` vocabulary, auto-discovered
     The surface never enumerates list names; lib/registry.js scans the table, so a
     registry created by any engine (or a future seed) is authorable here as soon as
     it exists. This is what turns "add a platform mode" into a console action: the
     registration walk, every gTable select and every engine reads the same rows.
     ====================================================================== */
  function apiPlatformRegistries(req, res, url, s) {
    if (!requirePlatformSection(s, res, "registries", "read")) return;
    const registry = require("../registry.js");
    return json(res, 200, { registries: registry.listAll() });
  }
  function apiPlatformRegistry(req, res, url, s, body) {
    const name = decodeURIComponent(url.pathname.match(/\/registries\/([^/]+)$/)?.[1] || "");
    if (!name) return bad(res, "registry name required", 400);
    const registry = require("../registry.js");
    if (req.method === "GET") {
      if (!requirePlatformSection(s, res, "registries", "read")) return;
      const items = registry.readList(name);
      if (items === null) return bad(res, "Unknown registry", 404);
      return json(res, 200, { name, items, usage: name === "deployModes" || name === "industries" });
    }
    if (req.method === "POST") {
      /* upsert one entry, keyed */
      if (!requirePlatformSection(s, res, "registries", "write")) return;
      const item = body && body.item;
      if (!item) return bad(res, "item required", 400);
      const r = registry.saveItem(name, item, s.platform_admin.email);
      if (!r.ok) return bad(res, r.error, 400);
      audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "registry.entry.save", "registry", name, { key: r.key });
      return json(res, 200, r);
    }
    return bad(res, "Method not allowed", 405);
  }
  /* AUTO-RECOMMEND: a skeleton entry inferred from the list's own live contents, so the
     authoring form is scaffolded from data instead of a hardcoded schema */
  function apiPlatformRegistryRecommend(req, res, url, s, body) {
    if (!requirePlatformSection(s, res, "registries", "read")) return;
    const name = decodeURIComponent(url.pathname.match(/\/registries\/([^/]+)\/recommend$/)?.[1] || "");
    if (!name) return bad(res, "registry name required", 400);
    const registry = require("../registry.js");
    return json(res, 200, { name, item: registry.recommend(name, String((body && body.label) || "")) });
  }
  function apiPlatformRegistryEntryDelete(req, res, url, s, body, name, key) {
    if (!requirePlatformSection(s, res, "registries", "write")) return;
    const registry = require("../registry.js");
    const r = registry.deleteItem(decodeURIComponent(name || ""), decodeURIComponent(key || ""), s.platform_admin.email);
    if (!r.ok) return bad(res, r.error, r.error && /In use/.test(r.error) ? 409 : 400);
    audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "registry.entry.delete", "registry", r.key, { list: name });
    return json(res, 200, r);
  }

  return [
    ["GET /api/registries", apiRegistriesList],
    ["POST /api/registries", apiRegistryCreate],
    ["POST /api/registries/:id/items", (r, re, u, s, b, p) => apiRegistryItem(r, re, u, s, b, p)],
    ["GET /api/meta", apiMeta],
    ["GET /api/meta/entities", apiEntities],
    ["GET /api/meta/entity/:key", (r, re, u, s, b, p) => apiEntityList(r, re, u, s, b, p)],
    ["POST /api/meta/entity/:key", (r, re, u, s, b, p) => apiEntityCreate(r, re, u, s, b, p)],
    ["PUT /api/meta/entity/:key/:id", (r, re, u, s, b, p, i) => apiEntityUpdate(r, re, u, s, b, p, i)],
    ["DELETE /api/meta/entity/:key/:id", (r, re, u, s, b, p, i) => apiEntityDelete(r, re, u, s, b, p, i)],
    ["GET /api/meta/entity-def", apiEntityDefsList],
    ["POST /api/meta/entity-def", apiEntityDefSave],
    ["DELETE /api/meta/entity-def/:key", (r, re, u, s, b, p) => apiEntityDefDelete(r, re, u, s, b, p)],
    ["POST /api/meta/entity-def/:key/enable", (r, re, u, s, b, p) => apiEntityDefEnable(r, re, u, s, b, p)],
    ["POST /api/meta/entity-def/:key/disable", (r, re, u, s, b, p) => apiEntityDefDisable(r, re, u, s, b, p)],
    ["GET /api/tenant/entity-def", apiTenantEntityDefs],
    ["GET /api/platform/universe-fields/:key", (r, re, u, s, b, p) => apiUniverseFields(r, re, u, s, b, p)],
    ["GET /api/platform/entity-types", apiEntityTypeList],
    ["POST /api/platform/entity-types", apiEntityTypeCreate],
    ["PUT /api/platform/entity-types/:entity/:type_key", (r, re, u, s, b, p, t) => apiEntityTypeUpdate(r, re, u, s, b, p, t)],
    ["DELETE /api/platform/entity-types/:entity/:type_key", (r, re, u, s, b, p, q) => apiEntityTypeDelete(r, re, u, s, b, p, q)],
    ["GET /api/platform/data", apiPlatformDataIndex],
    ["GET /api/platform/data/:key", (r, re, u, s, b, p) => apiPlatformDataList(r, re, u, s, b, p)],
    ["GET /api/platform/data/:key/def", (r, re, u, s, b, p) => apiPlatformDataDef(r, re, u, s, b, p)],
    ["GET /api/platform/data/:key/export", (r, re, u, s, b, p) => apiPlatformDataExport(r, re, u, s, b, p)],
    ["GET /api/platform/data/:key/sample", (r, re, u, s, b, p) => apiPlatformDataSample(r, re, u, s, b, p)],
    ["POST /api/platform/data/:key", (r, re, u, s, b, p) => apiPlatformDataCreate(r, re, u, s, b, p)],
    ["PUT /api/platform/data/:key/:id", (r, re, u, s, b, p, i) => apiPlatformDataUpdate(r, re, u, s, b, p, i)],
    ["DELETE /api/platform/data/:key/:id", (r, re, u, s, b, p, i) => apiPlatformDataDelete(r, re, u, s, b, p, i)],
    ["POST /api/platform/data/:key/import", (r, re, u, s, b, p) => apiPlatformDataImport(r, re, u, s, b, p)],
    ["GET /api/platform/entity-attributes", apiEntityAttributeList],
    ["POST /api/platform/entity-attributes", apiEntityAttributeAttach],
    ["GET /api/platform/global/countries", apiGlobalCountries],
    ["GET /api/platform/global/country", apiGlobalCountryGet],
    ["POST /api/platform/global/country", apiGlobalCountryPost],
    ["PUT /api/platform/global/country", apiGlobalCountryPut],
    ["GET /api/platform/global/currencies", apiGlobalCurrencies],
    ["GET /api/platform/global/currency", apiGlobalCurrencyGet],
    ["POST /api/platform/global/currency", apiGlobalCurrencyPost],
    ["PUT /api/platform/global/currency", apiGlobalCurrencyPut],
    ["GET /api/platform/global/providers", apiGlobalProviders],
    ["GET /api/platform/global/provider", apiGlobalProviderGet],
    ["POST /api/platform/global/provider", apiGlobalProviderPost],
    ["PUT /api/platform/global/provider", apiGlobalProviderPut],
    ["GET /api/platform/global/provider/availability", apiGlobalProviderAvailability],
    ["POST /api/platform/global/provider/enable", apiGlobalProviderEnableCountry],
    ["POST /api/platform/global/provider/disable", apiGlobalProviderDisableCountry],
    ["GET /api/platform/global/plans", apiGlobalPlans],
    ["GET /api/platform/global/plan", apiGlobalPlanGet],
    ["POST /api/platform/global/plan", apiGlobalPlanPost],
    ["PUT /api/platform/global/plan", apiGlobalPlanPut],
    ["GET /api/platform/global/tenant", apiGlobalTenantConfig],
    ["POST /api/platform/global/tenant/country", apiGlobalTenantCountry],
    ["POST /api/platform/global/tenant/currency", apiGlobalTenantCurrency],
    ["GET /api/platform/global/tenant/providers", apiGlobalTenantProviders],
    ["POST /api/platform/global/tenant/provider", apiGlobalTenantProviderPost],
    ["DELETE /api/platform/global/tenant/provider", apiGlobalTenantProviderDelete],
    ["POST /api/platform/global/tenant/plan", apiGlobalTenantPlan],
    ["GET /api/platform/registries", apiPlatformRegistries],
    ["GET /api/platform/registries/:name", apiPlatformRegistry],
    ["POST /api/platform/registries/:name", apiPlatformRegistry],
    ["POST /api/platform/registries/:name/recommend", apiPlatformRegistryRecommend],
    ["DELETE /api/platform/registries/:name/:key", apiPlatformRegistryEntryDelete],
    ["GET /api/admin/entity-usage", apiAdminEntityUsage],
    ["GET /api/platform/kinds", apiPlatformKinds],
    ["POST /api/platform/kinds", apiPlatformKindSave],
    ["DELETE /api/platform/kinds/:key", (r, re, u, s, b, p) => apiPlatformKindDelete(r, re, u, s, b, p)],
    ["GET /api/admin/entity-meta", apiEntityTags],
    ["PUT /api/admin/entity-meta", apiEntityTagsSave]
  ];
} };
