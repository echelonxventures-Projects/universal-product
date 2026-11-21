/* LUXORA Platform — stores domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the stores domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "stores", routes(kit) {
  const { J, SUX, T, all, applyCountryAndTax, audit, bad, billing, branding, caps, compose, crypto, enterprise, entity, fanoutAllowed, get, json, logAction, mailer, modeNeedsIndustries, mods, newUser, options, platSetting, provisionGateways, registry, requireAdmin, requirePlatform, requirePlatformSection, requireSection, requireStore, routes, run, sec, seedMeta, seedTaxonomy, seedTenantBrands, seedTenantCatalog, seedTenantDepartments, seedTenantHome, setUserPassword, settings, setupStatus, stIn, stIs, states, storeFacts, tenancy, tenantPayload, themes } = kit;

  /* the store's own view of its setup checklist — the same steps the platform sees (setupStatus) */
  function apiAdminSetup(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    const st = setupStatus(get("SELECT * FROM tenants WHERE id=?", T(s)));
    if (!st) return bad(res, "Unknown store", 404);
    json(res, 200, { steps: st.steps, done: st.done, total: st.total, available: st.available });
  }

  /* ---------------- public config & providers ---------------- */
  function apiStores(req, res) {
    const op = stIn("tenant", "operating");
    json(res, 200, { stores: all("SELECT slug,name,domain FROM tenants WHERE status IN " + op.sql + " ORDER BY id", ...op.args) });
  }
  /* ---------------- tenancy hierarchy (org → BU → brand → store → channel) ----------------
     Every node is data; the materialized path makes a subtree one LIKE away and the tree is
     the config cascade. Reads + writes are store-admin scoped to the session's own tenant, so
     an operator reorganises their own business and the platform sees the same shape via the
     generic cross-store reader. */
  function apiTenancyTree(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    const t = tenancy.tree(T(s)) || tenancy.root(T(s));
    json(res, 200, { tree: t, kinds: tenancy.KINDS });
  }
  function apiTenancyList(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { nodes: tenancy.list(T(s)) });
  }
  function apiTenancyCreate(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const out = tenancy.create(T(s), body || {});
    if (out.error) return bad(res, out.error, out.status || 400);
    logAction(s, "tenancy.create", "tenancy_node", out.path, out, req);
    json(res, 201, out);
  }
  function apiTenancyUpdate(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    const out = tenancy.update(T(s), Number(id), body || {});
    if (out.error) return bad(res, out.error, out.status || 400);
    logAction(s, "tenancy.update", "tenancy_node", out.path, out, req);
    json(res, 200, out);
  }
  function apiTenancyDelete(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    const out = tenancy.del(T(s), Number(id));
    if (out.error) return bad(res, out.error, out.status || 400);
    logAction(s, "tenancy.delete", "tenancy_node", id, out, req);
    json(res, 200, out);
  }
  /* resolve one config key up the cascade (Store → Brand → BU → Org → Tenant, deepest wins);
     the console's inspector shows an operator exactly which node a value came from */
  function apiTenancyResolve(req, res, url, s, body, id) {
    if (!requireAdmin(s, res)) return;
    const key = url.searchParams.get("key") || "";
    const node = tenancy.byId(T(s), Number(id)) || tenancy.root(T(s));
    if (!node) return bad(res, "no such node", 404);
    const chain = tenancy.chain(T(s), node.id);
    const perNode = chain.map(n => ({ id: n.id, path: n.path, kind: n.kind, value: key ? tenancy.getConfig(T(s), n.id, key) : n.config }));
    json(res, 200, { node, key, resolved: tenancy.resolve(T(s), node.id, key || null), chain: perNode });
  }
  function apiTenancyConfigSet(req, res, url, s, body, id, key) {
    if (!requireAdmin(s, res)) return;
    const out = tenancy.setConfig(T(s), Number(id), String(key || url.searchParams.get("key") || ""), body == null ? {} : body);
    if (out.error) return bad(res, out.error, out.status || 400);
    logAction(s, "tenancy.config", "tenancy_node", id, { key }, req);
    json(res, 200, out);
  }
  /* ---------------- the composition engine (Application = Capability Composition) ----------------
     The constitution's central claim made mechanical: compose() takes ANY declared capability
     and materializes its full application surface — data model, API, workflow, UI, dashboard,
     security — with no per-capability code. This surface is the platform's build tool: reads
     are open to a platform operator, and only a platform operator composes, because a composed
     capability becomes platform-wide machinery the moment it exists. */
  function apiComposeCandidates(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    json(res, 200, compose.candidates());
  }
  function apiComposeManifest(req, res, url, s, body, key) {
    if (!requirePlatform(s, res)) return;
    const m = compose.manifest(String(key || ""));
    if (!m) return bad(res, "nothing composed for " + key, 404);
    json(res, 200, m);
  }
  function apiComposeLedger(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    json(res, 200, { ledger: compose.ledger() });
  }
  function apiCompose(req, res, url, s, body, key) {
    if (!requirePlatform(s, res)) return;
    const out = compose.compose(String(key || ""), body || {});
    if (!out.ok) return bad(res, out.error, 400);
    logAction(s, "compose.create", "composition", out.model.key, { capability: out.capability.label, source: out.capability.source }, req);
    json(res, 201, out);
  }
  function apiRecompose(req, res, url, s, body, key) {
    if (!requirePlatform(s, res)) return;
    const out = compose.recompose(String(key || ""));
    if (!out.ok) return bad(res, out.error, 400);
    logAction(s, "compose.recompose", "composition", out.model.key, { capability: out.capability.label }, req);
    json(res, 200, out);
  }
  function apiAdminDepartments(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { departments: all("SELECT * FROM departments WHERE tenant_id=? ORDER BY position", T(s)) });
  }
  function apiAdminDeptSave(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const t = T(s);
    const key = String(body.key || "").trim().toLowerCase().replace(/[^a-z0-9_]/g, "");
    if (!key || !body.label) return bad(res, "Key and label required");
    const ex = get("SELECT key FROM departments WHERE tenant_id=? AND key=?", t, key);
    if (ex) run("UPDATE departments SET label=?, icon=?, active=?, position=? WHERE tenant_id=? AND key=?", String(body.label), String(body.icon || "🏷️"), body.active === 0 ? 0 : 1, Number(body.position) || 0, t, key);
    else run("INSERT INTO departments(tenant_id,key,label,icon,active,position) VALUES(?,?,?,?,?,?)", t, key, String(body.label), String(body.icon || "🏷️"), body.active === 0 ? 0 : 1, get("SELECT COALESCE(MAX(position),0) m FROM departments WHERE tenant_id=?", t).m + 1);
    logAction(s, "department.save", "department", key);
    json(res, 200, { departments: all("SELECT * FROM departments WHERE tenant_id=? ORDER BY position", t) });
  }
  function apiAdminDeptDelete(req, res, url, s, body, key) {
    if (!requireAdmin(s, res)) return;
    if (get("SELECT COUNT(*) c FROM products WHERE tenant_id=? AND dept=?", T(s), key).c > 0) return bad(res, "Department still has products — move them first");
    run("DELETE FROM departments WHERE tenant_id=? AND key=?", T(s), key);
    logAction(s, "department.delete", "department", key);
    json(res, 200, { ok: true });
  }
  function apiPlatformTenants(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    const tenants = all(`SELECT t.*, (SELECT COUNT(*) FROM products p WHERE p.tenant_id=t.id) products, (SELECT COUNT(*) FROM orders o WHERE o.tenant_id=t.id) orders,
      (SELECT COALESCE(SUM(o.total),0) FROM orders o WHERE o.tenant_id=t.id) gmv,
      (SELECT p.name FROM subscriptions s JOIN plans p ON p.id=s.plan_id WHERE s.tenant_id=t.id ORDER BY s.id DESC) plan,
      (SELECT s.status FROM subscriptions s WHERE s.tenant_id=t.id ORDER BY s.id DESC) sub_status
      FROM tenants t ORDER BY t.id`);
    const ks = Object.fromEntries(registry.kinds().map(k => [k.key, k]));
    tenants.forEach(t => { Object.assign(t, storeFacts(t.id)); t.profile = J(t.profile, {}); const k = ks[t.mode]; t.kind = k ? { key: k.key, name: k.name, noun: k.noun } : { key: t.mode, name: t.mode, noun: registry.KIND_DEFAULTS.noun }; });
    /* what each platform's state means, so the console labels suspend / resume by meaning */
    tenants.forEach(t => { t.operating = stIs("tenant", t.status, "operating"); });
    json(res, 200, { tenants });
  }
  function apiPlatformTenantSetup(req, res, url, s, body, id) {
    if (!requirePlatform(s, res)) return;
    const st = setupStatus(get("SELECT * FROM tenants WHERE id=?", Number(id)));
    if (!st) return bad(res, "Unknown tenant", 404);
    const { t, prof, c, kd } = st;
    json(res, 200, { tenant: { ...t, profile: prof }, kind: { key: kd.key, name: kd.name, noun: kd.noun, provision: kd.provision }, settings: { brand: c.brand, theme: c.theme, commerce: c.commerce, features: c.features }, gateways: { pay: st.payGw, ship: st.shipGw }, steps: st.steps, done: st.done, total: st.total, available: st.available });
  }
  function apiSetupSteps(req, res, url, s) {
    if (!requirePlatformSection(s, res, "tenants", "read")) return;
    try { json(res, 200, { steps: SUX().describe().map(st => ({ ...st, options: SUX().options(st.step) })) }); } catch (e) { bad(res, e.message, e.status || 400); }
  }
  function apiSetupDiscover(req, res, url, s, body) {
    if (!requirePlatformSection(s, res, "tenants", "read")) return;
    try { json(res, 200, { discovery: require("../platform-discovery.js").discover((body && body.answers) || {}) }); } catch (e) { bad(res, e.message, e.status || 400); }
  }
  function apiTenantBlueprint(req, res, url, s, body, id) {
    const tid = Number(id);
    if (!get("SELECT id FROM tenants WHERE id=?", tid)) return bad(res, "Unknown tenant", 404);
    if (req.method === "GET") {
      if (!requirePlatformSection(s, res, "tenants", "read")) return;
      try { return json(res, 200, SUX().state(tid)); } catch (e) { return bad(res, e.message, e.status || 400); }
    }
    if (!requirePlatformSection(s, res, "tenants", "write")) return;
    try {
      const r = SUX().answer(tid, (body && body.answers) || {}, { at: body && body.at, partial: !!(body && body.partial) }, s.platform_admin.email);
      audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.blueprint", "tenant", tid, { from: r.from, answered: Object.keys((body && body.answers) || {}) });
      json(res, 200, { ok: true, from: r.from, applied: r.applied ? { changed: r.applied.changed, enabled: r.applied.enabled, requested: r.applied.requested } : null });
    } catch (e) { bad(res, e.message, e.status || 400); }
  }
  function apiTenantRequests(req, res, url, s, body, id) {
    if (!requirePlatformSection(s, res, "tenants", "write")) return;
    try { SUX().setRequests(Number(id), (body && body.requests) || [], s.platform_admin.email); json(res, 200, { ok: true, requested: SUX().state(Number(id)).applied.requested }); }
    catch (e) { bad(res, e.message, e.status || 400); }
  }
  function apiPlatformTenantCreate(req, res, url, s, body) {
    if (!requirePlatformSection(s, res, "tenants", "write")) return;
    
    // Enhanced branding & config
    const branding = {
      name: String(body.brand?.name || body.name || "Store"),
      logo: body.brand?.logo || null,
      tagline: body.brand?.tagline || body.tagline || "A new storefront on LUXORA Platform",
      colors: JSON.stringify(body.brand?.colors || {})
    };
    
    const slug = String(body.slug || "").trim().toLowerCase().replace(/[^a-z0-9-]/g, "-").slice(0, 30);
    if (!slug || !body.name) return bad(res, "Store name and slug are required");
    if (get("SELECT id FROM tenants WHERE slug=?", slug)) return bad(res, "Slug already taken", 409);
    const p = tenantPayload(body);
    if (!p.country) return bad(res, "Pick a valid jurisdiction country — available: " + registry.countries().map(c => c.code).join(", "));
    if (modeNeedsIndustries(p.mode) && !p.industries.length) return bad(res, "Select at least one industry (product categories) for a " + p.mode + " store");
    if (p.owner && p.owner.email) {
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(p.owner.email) || String(p.owner.name || "").trim().length < 2)
        return bad(res, "Owner needs a full name and a valid email");
      /* the owner's password meets the platform's own credential policy, like every other */
      const weak = sec.checkPassword(String(p.owner.password || ""), p.owner.email);
      if (weak) return bad(res, "Owner password: " + weak);
    }
    const prov = sec.policy().provisioning;
    /* the kind of platform this is is a starter package: it pre-fills the setup answers (selling
       model, what it sells, how it delivers, its blend's features). Answers the registration gives
       override them; when it gives any, what the platform is provisioned with follows from its
       answers rather than from its kind */
    const kind0 = registry.kind(p.mode) || registry.normKind({ key: p.mode });
    const SU = require("../platform-setup.js");
    const answers = { ...SU.starterAnswers(kind0, { official: p.country.code, industries: p.industries }), ...(body.answers || {}) };
    if (body.answers) { try { SU.check(answers); } catch (e) { return bad(res, e.message, 400); } }
    const kd = body.answers ? { ...kind0, provision: SU.provisionFor(answers) } : kind0;
    if (body.seedCatalog == null) body.seedCatalog = kd.provision.storefront ? prov.seedCatalogByDefault : false;
    const planId = p.planId || prov.defaultPlanId;
    if (!get("SELECT id FROM plans WHERE id=?", planId)) return bad(res, "Unknown plan");
    /* the registration composes a whole platform, not a shell: an archetype writes the
       store's capability rows in one call. Validated BEFORE any write so an unknown
       archetype never leaves a half-created tenant behind. */
    /* a registration that names no archetype takes its kind's starting blend; an explicit
       empty choice ("" / null) means none — composed by hand afterwards */
    const arch = body.archetype !== undefined ? (String(body.archetype == null ? "" : body.archetype).trim() || null) : (kd.archetype || null);
    if (arch && !get("SELECT key FROM capability_presets WHERE key=?", arch))
      return bad(res, "Unknown archetype: " + arch + (body.archetype === undefined ? " (the starting blend of the " + kd.name + " kind)" : "") + " — available: " + all("SELECT key FROM capability_presets ORDER BY key").map(r => r.key).join(", "), 400);
    /* identity is chosen in the same pass, from the same kind of registry: an unknown
       template id is refused before any write, and an omitted choice resolves to the
       registry's own default — so a platform is never registered without a deliberate,
       complete authentication policy. */
    const identity = require("../identity.js");
    let idTemplate = body.identity_template ? Number(body.identity_template) : null;
    if (idTemplate && !get("SELECT id FROM platform_identity_templates WHERE id=?", idTemplate))
      return bad(res, "Unknown identity template", 400);
    if (!idTemplate) {
      const dflt = identity.defaultIdentityTemplate();
      if (dflt) idTemplate = dflt.id;
    }
    const profile = {
      legalName: String(p.j.legalName || body.name).slice(0, 80), taxId: String(p.j.taxId || "").slice(0, 40),
      registrationAddress: String(p.j.registrationAddress || "").slice(0, 160), state: String(p.j.state || ""),
      ownerName: p.owner ? String(p.owner.name || "").trim() : "", ownerEmail: p.owner ? String(p.owner.email || "").toLowerCase() : "", ownerPhone: p.owner ? String(p.owner.phone || "") : "",
      locale: String(body.language || body.locale || "").slice(0, 10)
    };
    const r = run("INSERT INTO tenants(slug,name,domain,status,mode,industries,profile) VALUES(?,?,?,?,?,?,?)",
      slug, String(body.name).slice(0, 60), String(body.domain || slug + ".localhost"), states.initial("tenant"), p.mode, JSON.stringify(p.industries), JSON.stringify(profile));
    const tid = Number(r.lastInsertRowid);
    /* the two policy-gated features start on the composition (their atoms), not a
       settings row — the platform policy is the authority either way */
    caps.applyFeatures(tid, caps.policyFeatures(sec.policy().provisioning));
    settings.save(tid, { brand: { name: branding.name, wordmark: branding.name, logo: branding.logo, tagline: branding.tagline, colors: JSON.parse(branding.colors) } });
    applyCountryAndTax(tid, p.country, p.tax);
    if (body.shipping) {
      /* merge, never replace: applyCountryAndTax just wrote currency/tax into commerce */
      const cc = settings.load(tid).commerce;
      settings.save(tid, { commerce: { ...cc, freeShipThreshold: Number(body.shipping.freeShipThreshold) || 0, shipFee: Number(body.shipping.shipFee) || 0, daysPriority: Number(body.shipping.daysPriority) || Number(sec.policy().provisioning.shipDaysPriority) || 2, daysStandard: Number(body.shipping.daysStandard) || Number(sec.policy().provisioning.shipDaysStandard) || 5 } });
    }
    /* brand colours → theme tokens, because the storefront paints from CSS vars, and a
       theme assignment (if any) still wins over settings.theme. */
    const col = body.brand && body.brand.colors ? body.brand.colors : null;
    if (col) themes.unassign("tenant", tid);
    if (col) {
      const ct = settings.load(tid).theme;
      settings.save(tid, { theme: { ...ct, header: col.primary || ct.header, accent: col.accent || col.secondary || ct.accent } });
    }
    if (body.theme) themes.assign("tenant", tid, String(body.theme));
    if (body.features) {
      const pol = sec.policy().provisioning;
      const feats = {};
      for (const [k, v] of Object.entries(body.features)) {
        if (v && require("../capabilities.js").policyRefusal(k, pol)) continue;
        feats[k] = !!v;
      }
      /* atoms absorb the storefront keys; whatever is left stays on the settings row */
      const leftover = caps.applyFeatures(tid, feats);
      if (Object.keys(leftover).length) settings.save(tid, { features: leftover });
    }
    if (kd.provision.storefront) {
      seedTenantDepartments(tid, p.industries.length ? p.industries : null);
      seedTenantHome(tid, p.industries.length ? p.industries : null);
    }
    /* the platform's own warehouse, in its own country, before the demo seed — which only
       adds its sample warehouses to a tenant that has none */
    if (kd.provision.warehouse) run("INSERT INTO warehouses(tenant_id,name,code,country,region) VALUES(?,?,?,?,?)", tid, "Main DC-" + p.country.code, "DC-" + p.country.code, p.country.code, profile.state);
    seedMeta(tid, p.industries.length ? p.industries : null, { warehouses: false, storefront: kd.provision.storefront });
    if (body.seedCatalog) seedTenantCatalog(tid, p.industries.length ? p.industries : null,
      { size: Number(body.seedSize) || 0, price: body.seedPrice || {} });
    if (body.seedBrands || body.seedCatalog) seedTenantBrands(tid);
    // Apply the chosen identity template (the registry's default when none was named)
    let appliedIdentity = null;
    if (idTemplate) {
      const tmpl = get("SELECT id,name,config FROM platform_identity_templates WHERE id=?", idTemplate);
      if (tmpl) {
        const config = J(tmpl.config, {});
        identity.setIdentitySettings(tid, config);
        // Apply providers from template
        if (Array.isArray(config.providers)) for (const pr of config.providers) {
          try { identity.upsertIdentityProvider(tid, pr); } catch (e) { /* a bad provider row is skipped, not fatal */ }
        }
        appliedIdentity = { id: tmpl.id, name: tmpl.name, settings: identity.getIdentitySettings(tid) };
      }
    }
    const pays = provisionGateways(tid, p.country, p.gateways, { shipping: !kd.provision.shipping ? false : (Array.isArray(body.shippingCarriers) ? body.shippingCarriers : null), payments: kd.provision.payments });
    { const ln = mailer.localNotifier(); if (ln) run("INSERT INTO tenant_gateways(tenant_id,provider_id,is_primary,mode,config,position) VALUES(?, ?, 1, 'live', '{}', 0)", tid, "notify:" + ln); }
    if (p.owner && p.owner.email) newUser(tid, profile.ownerName, profile.ownerEmail, String(p.owner.password), "admin");
    run("INSERT INTO subscriptions(tenant_id,plan_id,status) VALUES(?,?,?)", tid, planId, states.initial("plan_subscription"));
    mods.ensureBaselines();
    /* the registration composition lands here: an archetype writes the store's capability
       rows in one call, explicit atoms extend or override it, and the chosen universes
       publish catalog content — so a marketplace, an ERP or a ride-hailing platform is
       registered complete, not created empty and configured one screen at a time */
    if (arch) caps.applyPreset(tid, arch);
    if (body.capabilities && typeof body.capabilities === "object") {
      for (const [key, entry] of Object.entries(body.capabilities)) {
        if (!entry || entry.enabled === false) continue;
        try { caps.enable(tid, String(key), (entry && entry.params) || {}); } catch (e) { /* an unknown atom is skipped, not fatal */ }
      }
    }
    /* catalog content: activate the chosen universes into the new store. With none named
       and an archetype chosen, the platform type picks a canonical set — a mobility store
       opens with ride-hailing and fleet content, an ERP with payroll and procurement. */
    let universeKeys = Array.isArray(body.universes) ? body.universes.map(String) : null;
    if (!universeKeys && arch && body.seedUniverses !== false) {
      const row = get("SELECT universes FROM capability_presets WHERE key=?", arch);
      universeKeys = (row && J(row.universes, [])) || [];
    }
    const activated = [];
    if (universeKeys && universeKeys.length) {
      const uc = require("../ucos-catalog.js");
      for (const key of universeKeys) {
        try { const r = uc.activate(tid, key); if (r && r.published) activated.push({ key, published: r.published }); }
        catch (e) { /* a universe that cannot activate is skipped, not fatal to registration */ }
      }
    }
    /* the setup steps answered at registration are given now and applied: discovery decides the
       capabilities on top of whatever starter package the kind pre-filled */
    let setup = null;
    try { const r = SU.answer(tid, answers, { at: body.answersAt, partial: !body.answers }, s.platform_admin.email); setup = { from: r.from, enabled: r.applied ? r.applied.enabled : [], requested: r.applied ? r.applied.requested : [] }; }
    catch (e) { setup = { error: e.message }; }
    audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.create", "tenant", tid, { slug, kind: kd.key, country: p.country.code, industries: p.industries, gateways: pays, archetype: arch, identity_template: appliedIdentity ? appliedIdentity.name : null, universes: activated.map(a => a.key), setup: !!setup });
    const t = get("SELECT * FROM tenants WHERE id=?", tid);
    json(res, 200, { tenant: { ...t, ...storeFacts(t.id), profile: J(t.profile, {}) }, kind: { key: kd.key, name: kd.name, noun: kd.noun, provision: kd.provision }, storeUrl: kd.provision.storefront ? "/index.html?store=" + slug : null, adminUrl: "/console.html?scope=store&store=" + slug, archetype: arch, identity: appliedIdentity, composition: caps.compositionOf(tid), activated: activated, setup });
  }
  function apiPlatformTenantUpdate(req, res, url, s, body, id) {
    if (!requirePlatformSection(s, res, "tenants", "write")) return;
    const t = get("SELECT * FROM tenants WHERE id=?", Number(id));
    if (!t) return bad(res, "Unknown tenant", 404);
    const tid = t.id;
    if (body.name != null) run("UPDATE tenants SET name=? WHERE id=?", String(body.name).slice(0, 60), tid);
    /* the store's public address (a host name, no scheme or path): emailed links, payment returns
       and the sitemap are built on it; on the platform's own store it is the platform's address */
    if (body.domain != null) {
      const d = String(body.domain).trim().toLowerCase().replace(/^https?:\/\//, "").replace(/\/+$/, "");
      if (d && !/^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+(:\d{1,5})?$/.test(d)) return bad(res, "Domain must be a host name such as shop.example.com");
      run("UPDATE tenants SET domain=? WHERE id=?", d || null, tid);
    }
    if (body.status != null) {
      const st = states.has("tenant", body.status) ? body.status : t.status;
      run("UPDATE tenants SET status=? WHERE id=?", st, tid);
      audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.status", "tenant", tid, { status: st });
    }
    const p = tenantPayload({ ...body, jurisdiction: body.jurisdiction || undefined });
    if (body.jurisdiction || body.tax != null || body.country) {
      if (!p.country) return bad(res, "Unknown jurisdiction country");
      applyCountryAndTax(tid, p.country, body.tax != null ? body.tax : null);
      if (body.jurisdiction) {
        const prof = J(t.profile, {});
        Object.assign(prof, { legalName: String(body.jurisdiction.legalName || prof.legalName || ""), taxId: String(body.jurisdiction.taxId != null ? body.jurisdiction.taxId : prof.taxId || ""), registrationAddress: String(body.jurisdiction.registrationAddress != null ? body.jurisdiction.registrationAddress : prof.registrationAddress || ""), state: String(body.jurisdiction.state != null ? body.jurisdiction.state : prof.state || "") });
        run("UPDATE tenants SET profile=? WHERE id=?", JSON.stringify(prof), tid);
      }
      audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.jurisdiction", "tenant", tid, { country: p.country.code, tax: body.tax || null });
    }
    if (Array.isArray(body.industries)) {
      const inds = body.industries.filter(k => registry.list("industries").some(i => i.key === k));
      run("UPDATE tenants SET industries=? WHERE id=?", JSON.stringify(inds), tid);
      inds.forEach((k, i) => { const ind = registry.list("industries").find(x => x.key === k); run("INSERT OR IGNORE INTO departments(tenant_id,key,label,icon,position) VALUES(?,?,?,?,?)", tid, k, ind.name, ind.icon, i); });
      seedTaxonomy(tid, inds);
      audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.industries", "tenant", tid, { industries: inds });
    }
    /* gateways and carriers are independent: an operator may re-pick carriers without
       touching payment providers (the wizard's shipping step does exactly that). */
    if (body.gateways || Array.isArray(body.shippingCarriers)) {
      const country = registry.country(require("../stores.js").country(tid)) || p.country;
      if (country) {
        const pays = provisionGateways(tid, country, body.gateways, { shipping: Array.isArray(body.shippingCarriers) ? body.shippingCarriers : null });
        audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.gateways", "tenant", tid, { gateways: pays });
      }
    }
    if (body.shipping) {
      const cc = settings.load(tid).commerce;
      settings.save(tid, { commerce: { ...cc, freeShipThreshold: Number(body.shipping.freeShipThreshold) || 0, shipFee: Number(body.shipping.shipFee) || 0, daysPriority: Number(body.shipping.daysPriority) || Number(sec.policy().provisioning.shipDaysPriority) || 2, daysStandard: Number(body.shipping.daysStandard) || Number(sec.policy().provisioning.shipDaysStandard) || 5 } });
      audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.shipping", "tenant", tid, { shipping: body.shipping });
    }
    const col = body.brand && body.brand.colors ? body.brand.colors : null;
    if (col) {
      themes.unassign("tenant", tid);
      const ct = settings.load(tid).theme;
      settings.save(tid, { theme: { ...ct, header: col.primary || ct.header, accent: col.accent || col.secondary || ct.accent } });
    }
    if (body.theme) { themes.assign("tenant", tid, String(body.theme)); audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.theme", "tenant", tid, { theme: body.theme }); }
    if (body.features) {
      const pol = sec.policy().provisioning;
      const feats = {};
      for (const [k, v] of Object.entries(body.features)) {
        if (v && require("../capabilities.js").policyRefusal(k, pol)) continue;
        feats[k] = !!v;
      }
      const leftover = caps.applyFeatures(tid, feats);
      if (Object.keys(leftover).length) settings.save(tid, { features: leftover });
      audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.features", "tenant", tid, { features: feats });
    }
    if (p.planId) {
      if (!get("SELECT id FROM plans WHERE id=?", p.planId)) return bad(res, "Unknown plan");
      const ex = get("SELECT id FROM subscriptions WHERE tenant_id=? ORDER BY id DESC LIMIT 1", tid);
      if (ex) run("UPDATE subscriptions SET plan_id=?, status=? WHERE id=?", p.planId, states.first("plan_subscription", "paying"), ex.id);
      else run("INSERT INTO subscriptions(tenant_id,plan_id,status) VALUES(?,?,?)", tid, p.planId, states.first("plan_subscription", "paying"));
      audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.plan", "tenant", tid, { plan_id: p.planId });
    }
    if (body.owner && body.owner.email) {
      const prof = J(get("SELECT profile FROM tenants WHERE id=?", tid).profile, {});
      const existing = get("SELECT id FROM users WHERE tenant_id=? AND role='admin' ORDER BY id LIMIT 1", tid);
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(body.owner.email)) return bad(res, "New owner needs a valid email");
      const weak = sec.checkPassword(String(body.owner.password || ""), body.owner.email);
      if (weak) return bad(res, "New owner password: " + weak);
      if (existing) {
        setUserPassword(existing.id, String(body.owner.password), body.owner.email.toLowerCase());
        run("UPDATE users SET email=?, name=? WHERE id=?", body.owner.email.toLowerCase(), String(body.owner.name || prof.ownerName || "Store Admin"), existing.id);
      } else newUser(tid, String(body.owner.name || "Store Admin"), body.owner.email, String(body.owner.password), "admin");
      prof.ownerEmail = body.owner.email.toLowerCase(); prof.ownerName = String(body.owner.name || prof.ownerName || ""); prof.ownerPhone = String(body.owner.phone || prof.ownerPhone || "");
      run("UPDATE tenants SET profile=? WHERE id=?", JSON.stringify(prof), tid);
      audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.owner", "tenant", tid, { email: prof.ownerEmail });
    }
    const out = get("SELECT * FROM tenants WHERE id=?", tid);
    json(res, 200, { tenant: { ...out, ...storeFacts(out.id), profile: J(out.profile, {}) } });
  }
  function apiPlatformTenantDelete(req, res, url, s, body, id) {
    if (!requirePlatformSection(s, res, "tenants", "write")) return;
    const tid = Number(id);
    const row = get("SELECT id, slug FROM tenants WHERE id=?", tid);
    if (!row) return bad(res, 'store not found', 404);
    /* Store protection is DATA, never a slug in code: an operator lists the protected stores
       in platform_settings.protectedStores and edits it at will. When that row is absent the
       platform's FIRST store is protected by structure (it is the console's own demo tenant),
       never by name — no code path depends on any particular store. */
    const list = platSetting('protectedStores', null);
    const firstId = Number((get("SELECT id FROM tenants ORDER BY id LIMIT 1") || {}).id);
    if ((list ? list.includes(row.slug) : tid === firstId))
      return bad(res, 'This store is protected from deletion. Remove its slug from platform_settings.protectedStores to proceed.');
    /* the store's node is archived on the kernel in the same transaction as its rows (lib/stores.js) */
    require("../stores.js").withdraw(tid, () => {
      for (const q of ["DELETE FROM products WHERE tenant_id=?", "DELETE FROM product_bullets WHERE tenant_id=?", "DELETE FROM departments WHERE tenant_id=?", "DELETE FROM home_banners WHERE tenant_id=?", "DELETE FROM home_cards WHERE tenant_id=?", "DELETE FROM settings WHERE tenant_id=?", "DELETE FROM tenant_gateways WHERE tenant_id=?", "DELETE FROM reviews WHERE tenant_id=?", "DELETE FROM payments WHERE tenant_id=?", "DELETE FROM invoices WHERE tenant_id=?", "DELETE FROM subscriptions WHERE tenant_id=?", "DELETE FROM users WHERE tenant_id=?", "DELETE FROM tenants WHERE id=?"]) run(q, tid);
    });
    audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.delete", "tenant", tid);
    json(res, 200, { ok: true });
  }
  function apiPlatformImpersonate(req, res, url, s, body, id) {
    if (!requirePlatformSection(s, res, "tenants", "write")) return;
    const tid = Number(id);
    if (!get("SELECT id FROM tenants WHERE id=?", tid)) return bad(res, "Unknown store", 404);
    let admin = get("SELECT id FROM users WHERE tenant_id=? AND role='admin' ORDER BY id LIMIT 1", tid);
    if (!admin) { const uid = newUser(tid, "Platform Impersonator", "impersonate+" + tid + "@luxora.shop", crypto.randomBytes(8).toString("hex"), "admin"); admin = { id: uid }; }
    const token = crypto.randomBytes(16).toString("hex");
    run("INSERT INTO tokens(token,tenant_id,user_id,expires_at) VALUES(?,?,?,datetime('now','+10 minutes'))", token, tid, admin.id);
    const t = get("SELECT slug FROM tenants WHERE id=?", tid);
    audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "tenant.impersonate", "tenant", tid);
    json(res, 200, { url: `/console.html?store=${t.slug}&scope=store&token=${token}` });
  }
  function apiPlatformSubscribe(req, res, url, s, body, id) {
    if (!requirePlatformSection(s, res, "subs", "write")) return;
    if (!get("SELECT id FROM tenants WHERE id=?", Number(id))) return bad(res, "Unknown store", 404);
    const plan = get("SELECT * FROM plans WHERE id=?", Number(body.plan_id));
    if (!plan) return bad(res, "Unknown plan", 404);
    const ex = get("SELECT id FROM subscriptions WHERE tenant_id=? ORDER BY id DESC LIMIT 1", Number(id));
    if (ex) run("UPDATE subscriptions SET plan_id=?, status=?, renews_at=datetime('now','+1 month') WHERE id=?", plan.id, states.first("plan_subscription", "paying"), ex.id);
    else run("INSERT INTO subscriptions(tenant_id,plan_id,status) VALUES(?,?,?)", Number(id), plan.id, states.first("plan_subscription", "paying"));
    audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "subscription.assign", "tenant", id, { plan: plan.name });
    json(res, 200, { ok: true });
  }
  function apiPlatformInvoiceGenerate(req, res, url, s, body, id) {
    return (async () => {
    if (!requirePlatformSection(s, res, "invoices", "write")) return;
    const t = get("SELECT * FROM tenants WHERE id=?", Number(id));
    if (!t) return bad(res, "Unknown store", 404);
    const sub = get("SELECT p.* FROM subscriptions s JOIN plans p ON p.id=s.plan_id WHERE s.tenant_id=? ORDER BY s.id DESC", t.id);
    if (!sub) return bad(res, "Tenant has no subscription", 400);
    let r; try { r = billing.issueInvoice(t.id, { tax: true, note: `${sub.name} plan — monthly` }); } catch (e) { console.error("billing:", e.message); return bad(res, "Billing engine error: " + e.message, 500); }
    audit(T(s) || null, "platform", s.platform_admin.id, s.platform_admin.email, "invoice.generate", "invoice", r.number, { tenant: t.slug, amount: r.amount });
    json(res, 200, { ok: true, invoice: r });
    })();
  }
  function apiTenantEntityList(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    const tenantId = url.searchParams.get('tenant_id');
    const q = tenantId ? 'WHERE tenant_id=?' : '';
    const p = tenantId ? [tenantId] : [];
    json(res, 200, { entities: all(`SELECT * FROM tenant_entities ${q} ORDER BY entity`, ...p) });
  }
  function apiTenantEntityConfig(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    if (!body.tenant_id || !body.entity) return bad(res, 'tenant_id and entity required', 400);
    run('INSERT INTO tenant_entities(tenant_id,entity,enabled,requirement,custom_name,config) VALUES(?,?,?,?,?,?) ON CONFLICT(tenant_id,entity) DO UPDATE SET enabled=excluded.enabled,requirement=excluded.requirement,custom_name=excluded.custom_name,config=excluded.config',
      body.tenant_id, body.entity, body.enabled !== false ? 1 : 0, body.requirement || 'optional', body.custom_name || null, JSON.stringify(body.config || {}));
    logAction(s, 'tenant_entity.configure', 'tenant_entity', `${body.tenant_id}:${body.entity}`);
    json(res, 200, { ok: true });
  }
  function apiTenantFieldConfig(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    if (!body.tenant_id || !body.entity || !body.field_key) return bad(res, 'tenant_id, entity and field_key required', 400);
    run('INSERT INTO entity_field_config(tenant_id,entity,field_key,required,hidden,config) VALUES(?,?,?,?,?,?) ON CONFLICT(tenant_id,entity,field_key) DO UPDATE SET required=excluded.required,hidden=excluded.hidden,config=excluded.config',
      body.tenant_id, body.entity, body.field_key, body.required ? 1 : 0, body.hidden ? 1 : 0, JSON.stringify(body.config || {}));
    logAction(s, 'entity_field.configure', 'entity_field', `${body.tenant_id}:${body.entity}:${body.field_key}`);
    json(res, 200, { ok: true });
  }
  function apiPlatformFanout(req, res, url, s, body, p1, p2, metrics) {
    if (!requirePlatformSection(s, res, "gops", "read")) return;
    const path = url.searchParams.get("path") || "";
    const routeKey = "GET " + path;
    const entry = routes.find(([k]) => k === routeKey);
    if (!entry || !fanoutAllowed(path)) return bad(res, "Capability not available for cross-store aggregation", 404);
    /* the query the store handler sees is the platform's own query minus the fan-out
       control params — nothing about the request is invented */
    const u2 = new URL(url.toString());
    u2.pathname = path;
    ["path", "flat", "tenant_id"].forEach(k => u2.searchParams.delete(k));
    const tid = url.searchParams.get("tenant_id");
    const tenants = tid ? all("SELECT id,name,slug FROM tenants WHERE id=? ORDER BY name", Number(tid)) : all("SELECT id,name,slug FROM tenants ORDER BY name");
    const results = [];
    for (const t of tenants) {
      /* a scoped synthetic session: the handler resolves to THIS store and sees its own
         admin, so requireAdmin/requireSection pass exactly as they would for the store's
         operator. The platform's own privileges never cross the boundary. */
      const adm = get("SELECT id FROM users WHERE tenant_id=? AND role='admin' ORDER BY id LIMIT 1", t.id);
      const cap = { code: 0, body: "" };
      const sres = { writeHead: c => { cap.code = c; }, end: b => { cap.body = String(b); } };
      const ssess = { tenant: { id: t.id }, user_id: adm ? adm.id : null, platform_admin: null, sid: s.sid, trace: s.trace };
      try {
        /* the full router call signature, metrics included — handlers such as the store
           monitor read `metrics.snapshot`, so a fan-out must look exactly like a routed
           request to the capability, not a stripped-down one */
        entry[1](req, sres, u2, ssess, {}, null, null, metrics);
        let data = null, err = null;
        try { const j = JSON.parse(cap.body); if (j && j.error) err = j.error; else data = j; } catch (e) { err = "unparsable response"; }
        results.push({ tenant_id: t.id, name: t.name, slug: t.slug, ok: !err && cap.code < 400, ...(err ? { error: err } : { data }) });
      } catch (e) { results.push({ tenant_id: t.id, name: t.name, slug: t.slug, ok: false, error: e.message }); }
    }
    /* `flat` merges the per-store payloads by one uniform rule — arrays concatenate with the
       store stamped on every object, numbers sum, other values keep the first store's — so a
       console view can render one cross-store table without knowing each payload's shape. */
    const flat = url.searchParams.get("flat") === "1";
    const merged = { capability: path.replace(/^\/api\//, ""), count: results.length, results };
    if (flat) {
      const acc = {};
      for (const r of results) {
        if (!r.ok || !r.data || typeof r.data !== "object") continue;
        for (const [k, v] of Object.entries(r.data)) {
          if (Array.isArray(v)) {
            const stamped = v.map(x => (x && typeof x === "object" && !Array.isArray(x)) ? { tenant_id: r.tenant_id, store: r.name, ...x } : x);
            acc[k] = (acc[k] || []).concat(stamped);
          } else if (typeof v === "number" && isFinite(v)) acc[k] = (acc[k] || 0) + v;
          else if (!(k in acc)) acc[k] = v;
        }
      }
      merged.merged = acc;
    }
    logAction(s, "platform.fanout", "fanout", path, { stores: results.length, flat });
    json(res, 200, merged);
  }
  function apiRegionsGet(req, res, url, s) { if (!requirePlatform(s, res)) return; json(res, 200, enterprise.regionConfig()); }
  function apiRegionsSet(req, res, url, s, body) { if (!requirePlatform(s, res)) return; json(res, 200, enterprise.setRegions(body || {})); }
  /* ========== Branding System APIs ========== */
  function apiPlatformBranding(req, res, url, s, body) {
    if (!requirePlatform(s, res)) return;
    body = body || {};
    if (req.method === 'GET') return json(res, 200, { branding: branding.getGlobalBranding() });
    if (req.method === 'PUT') {
      const b = body;
      if (!b.name && !b.logo && !b.colors && !b.fonts) return bad(res, 'No branding data', 400);
      return json(res, 200, { branding: branding.setGlobalBranding(b) });
    }
    return bad(res, 'Method not allowed', 405);
  }
  function apiStoreBranding(req, res, url, s, body) {
    body = body || {};
    if (!requireStore(s, res)) return;
    /* reading the effective brand is public (the storefront renders it); changing it is a
       store-settings write — the platform's permission flags limit WHICH fields a store may
       change, they never stood in for "who is asking" */
    if (req.method === 'PUT' && !requireSection(s, res, "settings", "write")) return;
    const tenantId = T(s);
    if (req.method === 'GET') {
      const b = branding.getEffectiveBranding(tenantId);
      return json(res, 200, { branding: b });
    }
    if (req.method === 'PUT') {
      const result = branding.setStoreBranding(tenantId, branding.getStorePermissions(tenantId), body);
      if (result.error) return bad(res, result.error, result.code);
      return json(res, 200, { branding: result });
    }
    return bad(res, 'Method not allowed', 405);
  }

  return [
    ["GET /api/stores", apiStores],
    ["GET /api/platform/tenant-entities", apiTenantEntityList],
    ["POST /api/platform/tenant-entities", apiTenantEntityConfig],
    ["POST /api/platform/tenant-fields", apiTenantFieldConfig],
    ["GET /api/platform/fanout", apiPlatformFanout],
    ["GET /api/tenancy/tree", apiTenancyTree],
    ["GET /api/tenancy/nodes", apiTenancyList],
    ["POST /api/tenancy/node", apiTenancyCreate],
    ["PUT /api/tenancy/node/:id", apiTenancyUpdate],
    ["DELETE /api/tenancy/node/:id", apiTenancyDelete],
    ["GET /api/tenancy/resolve/:id", apiTenancyResolve],
    ["POST /api/tenancy/config/:id/:key", apiTenancyConfigSet],
    ["GET /api/compose/candidates", apiComposeCandidates],
    ["GET /api/compose/ledger", apiComposeLedger],
    ["GET /api/compose/:key", apiComposeManifest],
    ["POST /api/compose/:key", apiCompose],
    ["POST /api/compose/:key/recompose", apiRecompose],
    ["GET /api/admin/departments", apiAdminDepartments],
    ["POST /api/admin/departments", apiAdminDeptSave],
    ["DELETE /api/admin/departments/:key", (r, re, u, s, b, p) => apiAdminDeptDelete(r, re, u, s, b, p)],
    ["GET /api/branding", apiStoreBranding],
    ["PUT /api/branding", apiStoreBranding],
    ["GET /api/platform/branding", apiPlatformBranding],
    ["PUT /api/platform/branding", apiPlatformBranding],
    ["GET /api/platform/regions", apiRegionsGet],
    ["PUT /api/platform/regions", apiRegionsSet],
    ["GET /api/platform/tenants", apiPlatformTenants],
    ["GET /api/platform/tenants/:id/setup", (r, re, u, s, b, p) => apiPlatformTenantSetup(r, re, u, s, b, p)],
    ["POST /api/platform/tenants", apiPlatformTenantCreate],
    ["GET /api/platform/setup/steps", apiSetupSteps],
    ["POST /api/platform/setup/discover", apiSetupDiscover],
    ["GET /api/platform/tenants/:id/blueprint", (r, re, u, s, b, p) => apiTenantBlueprint(r, re, u, s, b, p)],
    ["POST /api/platform/tenants/:id/blueprint", (r, re, u, s, b, p) => apiTenantBlueprint(r, re, u, s, b, p)],
    ["POST /api/platform/tenants/:id/requests", (r, re, u, s, b, p) => apiTenantRequests(r, re, u, s, b, p)],
    ["PUT /api/platform/tenants/:id", (r, re, u, s, b, p) => apiPlatformTenantUpdate(r, re, u, s, b, p)],
    ["DELETE /api/platform/tenants/:id", (r, re, u, s, b, p) => apiPlatformTenantDelete(r, re, u, s, b, p)],
    ["POST /api/platform/tenants/:id/impersonate", (r, re, u, s, b, p) => apiPlatformImpersonate(r, re, u, s, b, p)],
    ["POST /api/platform/tenants/:id/subscribe", (r, re, u, s, b, p) => apiPlatformSubscribe(r, re, u, s, b, p)],
    ["POST /api/platform/tenants/:id/invoice", (r, re, u, s, b, p) => apiPlatformInvoiceGenerate(r, re, u, s, b, p)],
    ["GET /api/admin/setup", apiAdminSetup]
  ];
} };
