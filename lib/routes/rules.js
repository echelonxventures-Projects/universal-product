/* LUXORA Platform — rules domain routes (moved from lib/api.js; _registry/business-domains.json).
   Each handler answers one route of the rules domain. What it needs from the shared HTTP kit
   (lib/api.js) is passed in as `kit`. */
"use strict";

module.exports = { domain: "rules", routes(kit) {
  const { CFG, J, POLICY_KEYS, T, actor, all, audit, bad, caps, cleanShipFrom, deployModeOr, get, isAdmin, json, logAction, platGet, registry, requireAdmin, requirePlatform, requirePlatformSection, requireSection, rl, rules, run, sec, settings } = kit;

  function apiAdminSettingsGet(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    json(res, 200, { settings: CFG(s), defaults: settings.DEFAULTS, countries: registry.countries(), taxModes: registry.taxModes(), currencies: registry.currencies() });
  }
  function apiAdminSettingsPut(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    if (!requireSection(s, res, "settings", "write")) return;
    if (body.commerce) for (const k of ["currency", "symbol", "locale", "taxMode", "taxRate", "decimals"]) if (body.commerce[k] === "" || body.commerce[k] == null) body.commerce[k] = null;
    if (body.commerce && body.commerce.currency && !registry.currency(body.commerce.currency)) return bad(res, "Unknown currency — pick from the currencies registry (Geo console)");
    if (body.commerce && body.commerce.country && !require("../places.js").byCode(body.commerce.country)) return bad(res, "Unknown place — a store's jurisdiction is a country or subdivision in the Geo registry");
    if (body.commerce && "shipRates" in body.commerce && !["fixed", "live"].includes(body.commerce.shipRates)) return bad(res, "shipRates is fixed or live");
    if (body.commerce && "parcelWeightKg" in body.commerce && !(Number(body.commerce.parcelWeightKg) > 0 && Number(body.commerce.parcelWeightKg) <= 1000)) return bad(res, "parcelWeightKg must be above 0 and at most 1000");
    if (body.commerce && "shipFrom" in body.commerce) {
      const sf = cleanShipFrom(body.commerce.shipFrom);
      if (sf.error) return bad(res, sf.error);
      /* an address is replaced whole, never merged with a previous one */
      body.commerce.shipFrom = sf.value;
    }
    if (body.features) {
      const pol = sec.policy().provisioning;
      /* an atom the platform policy must allow names its policy flag on its catalogue row */
      for (const [k, v] of Object.entries(body.features)) { const no = v === true && require("../capabilities.js").policyRefusal(k, pol); if (no) return bad(res, no, 403); }
      /* the storefront atoms own their own rows now — route the writes through the
         composition and persist only what is not an atom on the settings row */
      const leftover = caps.applyFeatures(T(s), body.features);
      if (Object.keys(leftover).length) settings.save(T(s), { features: leftover });
      else if (body.features && Object.keys(body.features).length) settings.save(T(s), { features: caps.leftoverFeatures(T(s)) });
    }
    if (body.commerce && body.commerce.currency && !sec.policy().provisioning.currencyOverridesAllowed) {
      const co = registry.country(CFG(s).commerce.country);
      if (body.commerce.currency !== co.currency) return bad(res, "Currency overrides are disabled by platform policy (allow under Platform → Provisioning)", 403);
    }
    const cur0 = CFG(s);
    const merged = {};
    for (const [k, v] of Object.entries(body || {})) merged[k] = settings.deepMerge(cur0[k], v);
    if (body.commerce && "shipFrom" in body.commerce) merged.commerce.shipFrom = body.commerce.shipFrom;
    settings.save(T(s), merged);
    logAction(s, "settings.update", "settings", T(s), { sections: Object.keys(body || {}) });
    json(res, 200, { settings: CFG(s) });
  }
  function apiAdminSettingsReset(req, res, url, s) {
    if (!requireAdmin(s, res)) return;
    if (!requireSection(s, res, "settings", "write")) return;
    settings.reset(T(s));
    logAction(s, "settings.reset", "settings", T(s));
    json(res, 200, { settings: CFG(s) });
  }
  function apiPlatformConfigGet(req, res, url, s) {
    if (!requirePlatform(s, res)) return;
    json(res, 200, { policy: sec.policy(), defaults: sec.DEFAULT_POLICY, provisionedAt: platGet("provisioned_at", null), pepperConfigured: !!process.env.LUXORA_PEPPER, tlsBoot: process.env.LUX_TLS === "1", keyInfo: sec.keyInfo() });
  }
  function apiPlatformConfigPut(req, res, url, s, body) {
    /* the global security policy (CSRF, lockout, password rules, KDF cost) is the security section */
    if (!requirePlatformSection(s, res, "security", "write")) return;
    const patch = {};
    for (const k of POLICY_KEYS) if (body[k] !== undefined) patch[k] = body[k];
    /* KDF cost is clamped: too low weakens every hash, too high turns each login into a DoS */
    const clamp = (v, lo, hi, d) => { const n = Math.floor(Number(v)); return n >= lo && n <= hi ? n : d; };
    if (patch.paymentReconcileMinutes !== undefined) {
      const n = Math.floor(Number(patch.paymentReconcileMinutes));
      if (!(n >= 0 && n <= 1440)) return bad(res, "paymentReconcileMinutes must be a whole number from 0 to 1440");
      patch.paymentReconcileMinutes = n;
    }
    if (patch.shopperSweepMinutes !== undefined) {
      const n = Math.floor(Number(patch.shopperSweepMinutes));
      if (!(n >= 0 && n <= 1440)) return bad(res, "shopperSweepMinutes must be a whole number from 0 to 1440");
      patch.shopperSweepMinutes = n;
    }
    if (patch.cspImgHosts !== undefined) {
      const hs = (Array.isArray(patch.cspImgHosts) ? patch.cspImgHosts : String(patch.cspImgHosts || "").split(/[\s,]+/)).map(h => String(h).trim().toLowerCase()).filter(Boolean);
      const badHost = hs.find(h => !sec.imgHosts({ cspImgHosts: [h] }).length);
      if (badHost) return bad(res, "Not a hostname: " + badHost + " (e.g. cdn.example.com or *.example.com)");
      patch.cspImgHosts = [...new Set(hs)];
    }
    if (body.kdfV2) patch.kdfV2 = { logN: clamp(body.kdfV2.logN, 14, 20, 17), r: clamp(body.kdfV2.r, 8, 16, 8), p: clamp(body.kdfV2.p, 1, 4, 2) };
    /* LAW-023: a policy may tighten the platform's security baseline, never weaken it */
    const below = sec.floorBreaches({ ...patch, kdfV2: patch.kdfV2 });
    if (below.length) return bad(res, "Below the platform's security baseline: " + below.join(", ") + " (a policy may tighten the baseline, never weaken it)", 422);
    /* new-store defaults: each key sent is validated and merged; a key not sent keeps its
       value (a partial update must never reset the rest). Modes and providers must exist
       in their registries; an empty provider means "none" */
    if (body.provisioning && typeof body.provisioning === "object") {
      const bp = body.provisioning, pv = {};
      const has = k => bp[k] !== undefined;
      for (const k of ["seedCatalogByDefault", "sandboxGatewaysByDefault", "currencyOverridesAllowed", "couponsAllowed", "fiscalContextsAllowed", "globalOffersAllowed"]) if (has(k)) pv[k] = !!bp[k];
      if (has("defaultPlanId")) {
        if (!get("SELECT id FROM plans WHERE id=?", Number(bp.defaultPlanId))) return bad(res, "Unknown plan");
        pv.defaultPlanId = Number(bp.defaultPlanId);
      }
      if (has("defaultCountry")) {
        const cc = String(bp.defaultCountry || "").toUpperCase();
        if (!get("SELECT code FROM countries WHERE code=?", cc)) return bad(res, "Unknown country: " + bp.defaultCountry);
        pv.defaultCountry = cc;
      }
      if (has("defaultMode")) {
        if (!rl("deployModes").some(m => m.key === bp.defaultMode)) return bad(res, "Unknown deploy mode: " + bp.defaultMode);
        pv.defaultMode = String(bp.defaultMode);
      }
      for (const [k, kind] of [["cashGateway", "payment"], ["houseShipping", "shipping"]]) if (has(k)) {
        const v = String(bp[k] || "").trim();
        if (v && !registry.providerDefs(kind).some(x => (x.id || x.key) === v)) return bad(res, "Unknown " + kind + " provider: " + v);
        pv[k] = v;
      }
      for (const [k, lo, hi] of [["paymentGatewaysPerStore", 0, 20], ["carriersPerStore", 0, 20], ["shipDaysPriority", 0, 365], ["shipDaysStandard", 0, 365]]) if (has(k)) {
        const n = Math.floor(Number(bp[k]));
        if (!(n >= lo && n <= hi)) return bad(res, k + " must be a whole number from " + lo + " to " + hi);
        pv[k] = n;
      }
      patch.provisioning = pv;
    }
    const first = !platGet("provisioned_at", null);
    const p = sec.setPolicy(patch);
    if (first) run("INSERT INTO platform_settings(key,value) VALUES('provisioned_at',?)", JSON.stringify(new Date().toISOString()));
    logAction(s, "platform.provision", "policy", first ? "initial" : "update", { changed: Object.keys(patch).join(",") }, req);
    json(res, 200, { policy: p, provisionedAt: platGet("provisioned_at", null) });
  }
  /* PLATFORM KINDS — the kinds of platform the operator can launch, any number of each.
     A kind is a deployModes registry row (lib/registry.js normKind); this surface adds what
     the console needs to edit one: how many platforms of each kind exist, the blends a kind
     can start from, and the console sections a kind can include — named as the menu names
     them, with the capabilities that own the rest. */
  /* ---------------- applicability rules (lib/rules.js) ----------------
     the platform owner's layer bounds every platform; each platform narrows its own. The
     vocabularies (subject types, dimensions, services, segments, channels, banks, country
     groups) are registry rows — the console offers whatever they hold. */
  function apiPlatformRules(req, res, url, s) {
    if (!requirePlatformSection(s, res, "applicability", "read")) return;
    json(res, 200, { schema: rules.schema(), rules: rules.listRules(null), platformRules: all("SELECT tenant_id, COUNT(*) n FROM applicability_rules WHERE tenant_id IS NOT NULL GROUP BY tenant_id") });
  }
  function apiPlatformRuleSave(req, res, url, s, body) {
    if (!requirePlatformSection(s, res, "applicability", "write")) return;
    const r = rules.save(body && body.rule || {}, null, s.platform_admin.email);
    if (r.error) return bad(res, r.error, r.status || 400);
    audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "rule.save", "applicability_rule", r.rule.id, { summary: r.rule.summary });
    json(res, 200, r);
  }
  function apiPlatformRuleDelete(req, res, url, s, body, id) {
    if (!requirePlatformSection(s, res, "applicability", "write")) return;
    const r = rules.remove(id, null);
    if (r.error) return bad(res, r.error, r.status || 400);
    audit(null, "platform", s.platform_admin.id, s.platform_admin.email, "rule.delete", "applicability_rule", Number(id), {});
    json(res, 200, r);
  }
  function apiPlatformRuleExplain(req, res, url, s, body) {
    if (!requirePlatformSection(s, res, "applicability", "read")) return;
    const type = String(body && body.type || "");
    if (!rules.schema().subjectTypes.some(t => t.key === type)) return bad(res, "Unknown subject type " + type, 400);
    const ctx = rules.explainContext(null, body && body.context);
    json(res, 200, { context: ctx, results: rules.explain(type, ctx) });
  }
  function apiAdminRules(req, res, url, s) {
    if (!requireSection(s, res, "applicability", "read", "applicability")) return;
    /* the platform rules that can reach this platform, and an editor without the dimensions
       that name a platform's identity (a platform narrows itself only) */
    json(res, 200, { schema: rules.schema({ tenant: true }), rules: rules.listRules(T(s)), inherited: rules.inheritedBy(T(s)), members: rules.members(T(s)), platform: rules.platformFacts(T(s)) });
  }
  /* what a rule can name, per subject type — enumerated by the type's registered source */
  function apiPlatformRuleSubjects(req, res, url, s) {
    if (!requirePlatformSection(s, res, "applicability", "read")) return;
    json(res, 200, { subjects: rules.subjects(String(url.searchParams.get("type") || ""), null) });
  }
  function apiAdminRuleSubjects(req, res, url, s) {
    if (!requireSection(s, res, "applicability", "read", "applicability")) return;
    json(res, 200, { subjects: rules.subjects(String(url.searchParams.get("type") || ""), T(s)) });
  }
  function apiAdminRuleSave(req, res, url, s, body) {
    if (!requireSection(s, res, "applicability", "write", "applicability")) return;
    const r = rules.save(body && body.rule || {}, T(s), actor(s)[2]);
    if (r.error) return bad(res, r.error, r.status || 400);
    logAction(s, "rule.save", "applicability_rule", r.rule.id, { summary: r.rule.summary }, req);
    json(res, 200, r);
  }
  function apiAdminRuleDelete(req, res, url, s, body, id) {
    if (!requireSection(s, res, "applicability", "write", "applicability")) return;
    const r = rules.remove(id, T(s));
    if (r.error) return bad(res, r.error, r.status || 400);
    logAction(s, "rule.delete", "applicability_rule", Number(id), {}, req);
    json(res, 200, r);
  }
  function apiAdminRuleExplain(req, res, url, s, body) {
    if (!requireSection(s, res, "applicability", "read", "applicability")) return;
    const type = String(body && body.type || "");
    if (!rules.schema().subjectTypes.some(t => t.key === type)) return bad(res, "Unknown subject type " + type, 400);
    const ctx = rules.explainContext(T(s), body && body.context, { tenant: true });
    json(res, 200, { context: ctx, results: rules.explain(type, ctx) });
  }
  /* the one question any engine, integration or page — today's or tomorrow's — can ask:
     may <type>/<id> be used in this request's context (plus anything the caller adds)? A
     shopper learns the verdict; console callers also see the reasons. */
  function apiRulesCheck(req, res, url, s, body) {
    const b = body || {};
    const type = String(b.type || ""), id = String(b.id || "");
    if (!type || !id) return bad(res, "type and id required", 400);
    if (!rules.schema().subjectTypes.some(t => t.key === type)) return bad(res, "Unknown subject type " + type, 400);
    /* the caller may state only what a request may state (never a platform's identity, never
       a computed fact such as its own segments) */
    const d = rules.decide(type, id, rules.context(T(s), rules.requestFacts(b.context)));
    const staff = s.platform_admin || isAdmin(s);
    json(res, 200, staff ? d : { ok: d.ok, verdict: d.verdict });
  }
  function apiAdminModePut(req, res, url, s, body) {
    if (!requireAdmin(s, res)) return;
    const mode = deployModeOr(body.mode);
    const inds = Array.isArray(body.industries) ? JSON.stringify(body.industries) : "[]";
    run("UPDATE tenants SET mode=?, industries=? WHERE id=?", mode, inds, T(s));
    s.tenant.mode = mode; s.tenant.industries = inds;
    logAction(s, "tenant.mode", "tenant", T(s), { mode, industries: body.industries });
    json(res, 200, { ok: true, mode, industries: J(inds, []) });
  }

  return [
    ["PUT /api/admin/mode", apiAdminModePut],
    ["GET /api/admin/settings", apiAdminSettingsGet],
    ["PUT /api/admin/settings", apiAdminSettingsPut],
    ["POST /api/admin/settings/reset", apiAdminSettingsReset],
    ["GET /api/platform/config", apiPlatformConfigGet],
    ["PUT /api/platform/config", apiPlatformConfigPut],
    ["GET /api/platform/rules", apiPlatformRules],
    ["POST /api/platform/rules", apiPlatformRuleSave],
    ["POST /api/platform/rules/explain", apiPlatformRuleExplain],
    ["DELETE /api/platform/rules/:id", (r, re, u, s, b, p) => apiPlatformRuleDelete(r, re, u, s, b, p)],
    ["GET /api/admin/rules", apiAdminRules],
    ["GET /api/admin/rules/subjects", apiAdminRuleSubjects],
    ["GET /api/platform/rules/subjects", apiPlatformRuleSubjects],
    ["POST /api/admin/rules", apiAdminRuleSave],
    ["POST /api/admin/rules/explain", apiAdminRuleExplain],
    ["DELETE /api/admin/rules/:id", (r, re, u, s, b, p) => apiAdminRuleDelete(r, re, u, s, b, p)],
    ["POST /api/rules/check", apiRulesCheck]
  ];
} };
