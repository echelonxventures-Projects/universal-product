/* LUXORA Platform - runtime registry: geo (countries/currencies), tax modes, provider catalog,
   availability relationships and list registries. All stored in DB tables (seeded once from
   providers.js/meta.js constants) and editable at runtime via the entity engine. */
"use strict";

/* db functions resolved lazily via require() to avoid circular-import partial exports */
const { all, get, run } = (() => {
  let target = null;
  const lazy = {};
  for (const fn of ["all", "get", "run", "exec"]) lazy[fn] = (...a) => (target || (target = require("./db.js")))[fn](...a);
  return lazy;
})();
const providers = require("./providers.js");
const meta = require("./meta.js");
const geo = require("./subdivisions.js");
const VALUE = require("./seed/value.json");

function J(v, d) { try { return JSON.parse(v == null || v === "" ? (d || "{}") : v); } catch (e) { return d || {}; } }

/* ---------- bootstrap seeding (idempotent) ---------- */
/* a currency's minor-unit digits, from the currency seed (ISO 4217): JPY 0, KWD 3, most 2 */
function seedDecimals(code) { const c = providers.CURRENCIES.find(x => x.code === code); return c ? c.decimals : 2; }
/* the seed country codes this install has already been offered, so a country the operator
   deleted is never re-added and one the seed gains later is offered exactly once */
/* every country and subdivision the registry seeds or repairs goes through Geo's write path
   (lib/places.js through): the place is recorded on the kernel first and the row is written in
   the same transaction, exactly as a console edit is. A write Geo refuses throws. */
function viaPlaces(key, row, code, writeRow) {
  const out = require("./places.js").through(false, key, row, code, writeRow);
  if (out && out.error) throw new Error(key + " " + code + ": " + out.error);
  return out;
}
/* a currency a new country names that Value's master does not hold yet: the seed's row when the
   seed declares it, else one from what the writer gave (its symbol, its minor units) with a
   placeholder rate an operator sets. Returns the currency, or null when there is nothing to
   make it from. */
function ensureCurrency(code, given) {
  code = String(code || "").toUpperCase();
  const have = currency(code);
  if (have) return have;
  const g = given || {};
  const sc = providers.CURRENCIES.find(x => x.code === code) || (g.symbol ? { code, name: code, symbol: String(g.symbol), decimals: g.decimals != null && g.decimals !== "" ? Number(g.decimals) : seedDecimals(code), usd: 1 } : null);
  if (!sc) return null;
  run("INSERT OR IGNORE INTO currencies(code,name,symbol,decimals,usd,position) VALUES(?,?,?,?,?,?)", sc.code, sc.name, sc.symbol, sc.decimals, sc.usd, 900);
  run("INSERT OR IGNORE INTO fx_rates(currency,usd,source,note) VALUES(?,?,?,?)", sc.code, sc.usd, "derived", "named by a new country");
  return currency(code);
}
function seenCountries(add) {
  const row = get("SELECT value v FROM platform_settings WHERE key='seed_countries_seen'");
  const seen = new Set(row ? J(row.v, []) : []);
  if (add) { add.forEach(c => seen.add(c)); run("INSERT INTO platform_settings(key,value) VALUES('seed_countries_seen',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", JSON.stringify([...seen])); }
  return seen;
}
/* the country master on an existing install:
   - rows an earlier boot invented for a provider's undeclared code ("SE (auto-registered)",
     currency "SE") take the seed's geography, and the invented currency goes once nothing
     uses it;
   - a country the seed declares that this install has never been offered arrives inactive,
     for an operator to switch on — adding it never changes what shoppers see */
function repairCountries() {
  const seedC = new Map(providers.COUNTRIES.map(c => [c.code, c]));
  const seedCur = new Map(providers.CURRENCIES.map(c => [c.code, c]));
  const addCurrency = (code, active) => { const c = seedCur.get(code); if (c) run("INSERT OR IGNORE INTO currencies(code,name,symbol,decimals,usd,position,active) VALUES(?,?,?,?,?,?,?)", c.code, c.name, c.symbol, c.decimals, c.usd, 900, active); };
  const P = require("./places.js");
  for (const row of all("SELECT code FROM countries WHERE name=code || ' (auto-registered)'")) {
    const c = seedC.get(row.code); if (!c) continue;
    const r = { code: row.code, currency: P.facts(row.code).currency };
    addCurrency(c.currency, 1);
    viaPlaces("country", { name: c.name, currency: c.currency, locale: c.locale }, r.code,
      () => run("UPDATE countries SET name=? WHERE code=?", c.name, r.code));
    if (r.currency && r.currency !== c.currency && !P.using("currency", r.currency).length && get("SELECT 1 ok FROM currencies WHERE code=? AND name=code", r.currency)) {
      run("DELETE FROM fx_rates WHERE currency=?", r.currency);
      run("DELETE FROM currencies WHERE code=?", r.currency);
    }
  }
  const seen = seenCountries();
  const fresh = providers.COUNTRIES.filter(c => !seen.has(c.code));
  if (!fresh.length) return;
  for (const c of fresh) {
    if (get("SELECT 1 ok FROM countries WHERE code=?", c.code)) continue;
    addCurrency(c.currency, 0);
    const row = { code: c.code, name: c.name, currency: c.currency, locale: c.locale, position: 500 + providers.COUNTRIES.indexOf(c), active: 0 };
    viaPlaces("country", row, c.code, () => P.insertCountry(row));
  }
  seenCountries(fresh.map(c => c.code));
}
function seedRegistries() {
  /* currencies first: a country's currency setting names one in Value's master */
  if (get("SELECT COUNT(*) c FROM currencies").c === 0) {
    providers.CURRENCIES.forEach((cur, i) => run("INSERT INTO currencies(code,name,symbol,decimals,usd,position) VALUES(?,?,?,?,?,?)", cur.code, cur.name, cur.symbol, cur.decimals, cur.usd, i));
    if (get("SELECT COUNT(*) c FROM fx_rates").c === 0)
      all("SELECT code, usd FROM currencies").forEach(c => run("INSERT INTO fx_rates(currency,usd,source,note) VALUES(?,?,?,?)", c.code, c.usd, "seed", "initial registry"));
  }
  if (get("SELECT COUNT(*) c FROM countries").c === 0) {
    /* a country master is GEOGRAPHY: its code and name, a place on the kernel. Its currency and
       locale are Value's and Expression's settings at that place, and it carries no tax facts —
       tax is a first-class engine that owns its own jurisdiction rules (taxRules, lib/tax.js) */
    const P = require("./places.js");
    P.batch(() => providers.COUNTRIES.forEach((c, i) => {
      const row = { code: c.code, name: c.name, currency: c.currency, locale: c.locale, position: i, active: 1 };
      viaPlaces("country", row, c.code, () => P.insertCountry(row));
    }));
    seenCountries(providers.COUNTRIES.map(c => c.code));
  } else require("./places.js").importRows();
  repairCountries();
  if (get("SELECT COUNT(*) c FROM tax_modes").c === 0) {
    providers.TAX_PROVIDERS.forEach((t, i) => run("INSERT INTO tax_modes(key,label,description,fields,position) VALUES(?,?,?,?,?)",
      t.id, t.name, t.desc || "", JSON.stringify(t.fields || []), i));
  }
  if (get("SELECT COUNT(*) c FROM provider_defs").c === 0) {
    const put = (kind, list) => list.forEach((p, i) => run(
      "INSERT INTO provider_defs(id,kind,name,emoji,description,methods,fee_pct,fee_fixed,fields,base_fee,eta_min,eta_max,position,global) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
      p.id, kind, p.name, p.emoji || "🔌", p.desc || "", JSON.stringify(p.methods || []), Number(p.feePct) || 0, Number(p.feeFixed) || 0,
      JSON.stringify(p.fields || []), Number(p.baseFee) || 0, p.eta ? p.eta[0] : null, p.eta ? p.eta[1] : null, i, p.countries.includes("*") ? 1 : 0));
    put("payment", providers.PAYMENT_PROVIDERS);
    put("shipping", providers.SHIPPING_PROVIDERS);
    put("notification", providers.NOTIFICATION_PROVIDERS);
  }
  /* specs are DATA (fill-in-the-blanks): attach declarative request specs to every provider, and
     register marketing providers (Meta/Google/GA4/TikTok). Idempotent + self-heals on upgrade. */
  for (const key of Object.keys(providers.PROVIDER_SPECS)) {
    const [kind, id] = key.split(":"); if (!id) continue;
    run("INSERT INTO provider_defs(id,kind,name,emoji,description,methods,fields,spec,enabled,position) VALUES(?,?,?,?,?,'[]','[]',?,1,999) ON CONFLICT(id,kind) DO UPDATE SET spec=excluded.spec", id, kind, id, "🔌", kind, JSON.stringify(providers.PROVIDER_SPECS[key]));
  }
  /* a credential a provider newly declares (a webhook signing secret) reaches an existing
     install: missing fields are appended, an operator's own edits to the others are kept */
  for (const [kind, list] of [["payment", providers.PAYMENT_PROVIDERS], ["shipping", providers.SHIPPING_PROVIDERS], ["notification", providers.NOTIFICATION_PROVIDERS]]) for (const p of list) {
    const row = get("SELECT fields FROM provider_defs WHERE id=? AND kind=?", p.id, kind); if (!row) continue;
    let have = []; try { have = JSON.parse(row.fields || "[]"); } catch (e) { continue; }
    const add = (p.fields || []).filter(f => !have.some(h => h && h.key === f.key));
    if (add.length) run("UPDATE provider_defs SET fields=? WHERE id=? AND kind=?", JSON.stringify(have.concat(add)), p.id, kind);
  }
  for (const m of providers.MARKETING_PROVIDERS) {
    run("INSERT INTO provider_defs(id,kind,name,emoji,description,methods,fields,spec,enabled,position,global) VALUES(?,?,?,?,?,'[]',?,?,1,?,?) ON CONFLICT(id,kind) DO UPDATE SET name=excluded.name, description=excluded.description, fields=excluded.fields, spec=excluded.spec, global=excluded.global",
      m.id, "marketing", m.name, m.emoji, m.desc || "", JSON.stringify(m.fields || []), JSON.stringify(providers.PROVIDER_SPECS["marketing:" + m.id] || {}), m.id.length, m.countries.includes("*") ? 1 : 0);
  }
  /* the global ("*") declaration is data: re-assert it on every boot so a row added at
     runtime reconciles the same way a seeded one does. Only the flag — never the name,
     fees or fields, which an operator may have edited since. Only providers the seed itself
     declares global are touched; a provider limited to a country list stays limited, and a
     provider an operator flipped global in the console keeps that (the flag is never cleared) */
  for (const p of providers.PAYMENT_PROVIDERS.concat(providers.SHIPPING_PROVIDERS, providers.NOTIFICATION_PROVIDERS, providers.MARKETING_PROVIDERS))
    if (p.countries.includes("*")) run("UPDATE provider_defs SET global=1 WHERE id=? AND global=0", p.id);
  /* the context primitive is DATA: each dimension's profiles (tax/invoice/payment and any an
     operator adds) are rows in context_types, editable from the console as the `context_type`
     entity. Seeded additively from the registry's own declaration — INSERT OR IGNORE, so an
     operator's edit or new dimension survives every boot and is never clobbered. */
  {
    let pos = 0;
    for (const [grp, items] of Object.entries(meta.VERTICAL_CONTEXTS)) {
      for (const it of items) {
        run("INSERT OR IGNORE INTO context_types(grp,key,label,type,fields,position) VALUES(?,?,?,?,?,?)",
          grp, it.key, it.label, it.type || grp, JSON.stringify((it.fields || []).map(f => ({ key: f.key, label: f.label, type: f.type, ...(f.options ? { options: f.options } : {}) }))), pos++);
      }
    }
  }
  if (get("SELECT COUNT(*) c FROM provider_availability").c === 0) {
    /* a provider is linked only to countries the master declares. A code the seed lists for a
       provider but not as a country used to be invented here ("SE (auto-registered)", currency
       "SE"); test/geo.js now fails the seed instead, and an undeclared code is skipped */
    const declared = new Set(all("SELECT code FROM countries").map(r => r.code));
    const link = (pid, countries) => countries.forEach(cc => { if (declared.has(cc)) run("INSERT OR IGNORE INTO provider_availability(provider_id,country_code) VALUES(?,?)", pid, cc); });
    providers.PAYMENT_PROVIDERS.concat(providers.SHIPPING_PROVIDERS, providers.NOTIFICATION_PROVIDERS, providers.MARKETING_PROVIDERS).forEach(p => {
      if (p.countries.includes("*")) all("SELECT code FROM countries").forEach(c => link(p.id, [c.code]));
      else link(p.id, p.countries);
    });
  }
  /* the derived projections above were built once, under a COUNT(*)=0 guard, so a country
     added later appeared in the master list but in nothing derived from it — no currency
     row, no FX quote, no availability links, and therefore no payment/shipping at checkout.
     Reconcile instead of seed: fill the gaps an operator's additions left, on every boot.
     Every statement is additive (INSERT OR IGNORE) and never overwrites a row a human owns,
     so this is safe to run on a warm DB and costs a few idempotent writes on a cold one. */
  reconcileDerived();
  {
    const verticalFields = {}; const verticalTypes = { tax: [], invoice: [], payment: [] };
    for (const [vk, v] of Object.entries(meta.VERTICALS)) verticalFields[vk] = v.fields;
    for (const [gk, items] of Object.entries(meta.VERTICAL_CONTEXTS)) for (const it of items) (verticalTypes[gk] = verticalTypes[gk] || []).push({ ...it, group: gk });
    const lists = {
      /* Value's classes of units of value (lib/seed/value.json) */
      [VALUE.classList]: VALUE.classes,
      /* Time's registries (lib/seed/time.json) */
      ...(() => { const T = require("./seed/time.json"); return Object.fromEntries(Object.entries(T.lists).map(([k, name]) => [name, T[k]])); })(),
      industries: meta.INDUSTRIES, productTypes: meta.PRODUCT_TYPES, lifecycle: meta.LIFECYCLE, lifecycleTransitions: meta.LIFECYCLE_TRANSITIONS,
      relTypes: meta.REL_TYPES, mediaKinds: meta.MEDIA_KINDS, packagingLevels: meta.PACKAGING_LEVELS,
      uomUnits: meta.UOM_UNITS, uomConversions: meta.UOM_CONVERSIONS, sellerRoles: meta.SELLER_ROLES,
      promoTypes: meta.PROMO_TYPES, identityFields: meta.IDENTITY_FIELDS, shippingClasses: meta.SHIPPING_CLASSES,
      serializedStatuses: meta.SERIALIZED_STATUSES, serializedConditions: meta.SERIALIZED_CONDITIONS, variantAxes: meta.VARIANT_AXES,
      complianceScopes: meta.COMPLIANCE_SCOPES, complianceKinds: meta.COMPLIANCE_KINDS, complianceStatuses: meta.COMPLIANCE_STATUSES,
      supplierRoles: meta.SUPPLIER_ROLES, supplierStatuses: meta.SUPPLIER_STATUSES, paymentTerms: meta.PAYMENT_TERMS, incoterms: meta.INCOTERMS,
      localizationEntities: meta.LOCALIZATION_ENTITIES, contractStatuses: meta.CONTRACT_STATUSES, tenderStatuses: meta.TENDER_STATUSES, linkStatuses: meta.LINK_STATUSES,
      verticals: meta.VERTICALS, industryVertical: meta.INDUSTRY_VERTICAL, deployModes: meta.DEPLOY_MODES,
      verticalFields, verticalTypes, verticalContexts: meta.VERTICAL_CONTEXTS, verticalTypeOf: meta.VERTICAL_TYPE_OF,
      /* payment methods settled outside the platform (cash at the door, a bank transfer): an
         order paid this way stays pending until someone records the money. Editable in
         Data Studio, so a new offline method — a cheque, a voucher desk — needs no code */
      offlinePaymentMethods: [{ key: "cod", name: "Cash on delivery" }, { key: "bank_transfer", name: "Bank transfer" }],
      capabilityDomains: meta.CAPABILITY_DOMAINS,
      /* Search & Discovery: registry-driven synonyms + boost rules (editable in Data Studio) */
      searchSynonyms: { tv: ["television", "smart tv", "display"], laptop: ["laptop computer", "notebook"], sofa: ["couch", "settee"], airpods: ["earbuds", "headphones"], gold: ["22k gold", "916", "hallmarked"], drill: ["power drill", "impact driver"], wine: ["vintage wine", "red wine"] },
      searchBoosts: [{ id: "LX-ELS-007", reason: "flagship", weight: 0.5 }, { id: "VR-JEW-01", reason: "high-margin", weight: 0.3 }],
      /* applicability rules: the subject types, scope dimensions, services, segments, channels,
         banks and country groups a rule can name (lib/rules.js) */
      ...require("./rules.js").LISTS,
      /* the state machines (lib/states.js): what each state means and what entering it does */
      ...require("./states.js").SEED,
      identityProviderTypes: require("./identity.js").BUILTIN_PROVIDER_TYPES,
      /* how each delivery channel reaches a person (lib/mailer.js) */
      deliveryChannels: require("./mailer.js").CHANNELS,
      /* the storefront's sort orders and the ad events a shopper may report */
      productSortOrders: meta.SORT_ORDERS, adEventKinds: meta.AD_EVENT_KINDS, contextGroups: meta.CONTEXT_GROUPS, fxSources: meta.FX_SOURCES,
      taxonomyLevels: meta.TAXONOMY_LEVELS
    };
    /* The registry lists are the platform's source of truth, not a mirror of JS constants.
       INSERT OR IGNORE would freeze the constants in place forever: an operator's console
       edit survives the first boot and is silently overwritten on the next. Upsert instead —
       the seed re-asserts the canonical defaults only where nobody has configured a value,
       and the corpus's own Configuration-Over-Code principle actually holds at runtime.
       Lists an operator has extended keep their additions; lists they edited keep their
       edits, because the seed never clobbers a row whose content differs from the default. */
    /* v2: deployModes became platform kinds — mobility, operations and fintech rows, and
       each row declares what one is called, its starting blend, what it is provisioned
       with and which console sections apply */
    /* v3: the applicability-rule vocabularies (subject types, dimensions, services, segments,
       channels, banks, country groups) */
    /* v4: the rule vocabularies come from lib/seed/rules.json — generic sources, declared
       fact origins, binding points — and sign-in methods are a registry list */
    /* v5: the state machines (lib/seed/states.json) */
    /* v6: declared behaviour — delivery channels, sign-in types that enrol a shared secret */
    /* v7: the country rule dimension reads the store's jurisdiction on the kernel */
    const stamp = "reg_v7";
    const conf = get("SELECT value v FROM platform_settings WHERE key='registry_seed_stamp'");
    const firstRun = !conf || conf.v !== stamp;
    for (const [k, v] of Object.entries(lists)) {
      if (v === undefined) continue;
      const ex = get("SELECT items, seeded_from, edited FROM meta_lists WHERE name=?", k);
      if (!ex) run("INSERT INTO meta_lists(name,label,items,seeded_from) VALUES(?,?,?,?)", k, k, JSON.stringify(v), stamp);
      /* re-assert defaults only on a first boot or a version bump — never on every restart —
         and only on a row this seed owns that NO OPERATOR HAS EDITED. The `edited` stamp is
         the whole protection: without it a stamp bump would silently revert every console
         change a merchant made to their own registries. */
      /* a row an earlier seed version wrote is still this seed's to revise (as the capability
         catalog does with cap_v*) — matching only the current stamp left every unedited list
         frozen at the version it was first seeded with */
      else if (firstRun && (!ex.seeded_from || /^reg_v\d+$/.test(ex.seeded_from)) && !(Number(ex.edited) > 0))
        run("UPDATE meta_lists SET items=?, seeded_from=? WHERE name=?", JSON.stringify(v), stamp, k);
      /* AUTO-UPGRADE: an operator has edited this list, so a version bump must not
         overwrite it — but it also must not strand the platform on the old defaults.
         New canonical entries arrive additively (keyed); every entry the operator
         has is untouched. This is what makes a registry upgrade safe to ship: the
         operator's vocabulary survives, and the corpus's new vocabulary still lands. */
      /* between version bumps, an entry the seed newly declares (a new state machine, a
         binding, a vocabulary row) still reaches every install: missing keyed entries are
         appended on every boot — additive only, so nothing an operator has is touched */
      else if (!firstRun && Array.isArray(v)) {
        const cur = J(ex.items, []);
        const upgraded = mergeDefaults(cur, v);
        if (Array.isArray(cur) && upgraded.length !== cur.length) run("UPDATE meta_lists SET items=? WHERE name=?", JSON.stringify(upgraded), k);
      }
      else if (firstRun && Number(ex.edited) > 0) {
        const cur = J(ex.items, []);
        const upgraded = mergeDefaults(cur, v);
        if (upgraded.length !== cur.length)
          run("UPDATE meta_lists SET items=? WHERE name=?", JSON.stringify(upgraded), k);
      }
    }
    if (firstRun) run("INSERT INTO platform_settings(key,value) VALUES('registry_seed_stamp',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", stamp);
    /* an operator-edited dimension list still gains the kernel providers its rows declare */
    if (lists.ruleDimensions) addFields("ruleDimensions", lists.ruleDimensions, ["provider"]);
    /* every unit of value Value ships, and those the offer engine's old lists held */
    seedUnits();
    /* rows an operator added to the offer engine's old time lists join Time's */
    require("./time.js").mergeLegacy();
    /* a behaviour field the seed newly declares reaches an operator-edited list too */
    addFields("identityProviderTypes", require("./identity.js").BUILTIN_PROVIDER_TYPES, ["enrol", "protocols"]);
    addFields("productTypes", meta.PRODUCT_TYPES, ["plain", "purchase", "service"]);
    addFields("mediaKinds", meta.MEDIA_KINDS, ["player"]);
    upgradeShape("shippingClasses", meta.SHIPPING_CLASSES); addFields("shippingClasses", meta.SHIPPING_CLASSES, ["default", "surcharge", "surcharge_default"]);
  }
  /* AI product layer: idempotent provider/capability/plan seeding (runs on every boot, safe on upgrade) */
  try { require("./ai.js").seed(); } catch (e) { console.error("ai seed failed:", e.message); }
  /* Central offers/coupons/wallet registries (data-driven, self-heal on upgrade) */
  try { require("./offers.js").seed(); } catch (e) { console.error("offers seed failed:", e.message); }
  try { require("./goip.js").seed(); } catch (e) { console.error("goip seed failed:", e.message); }
  /* Tax engine registries */
  try { require("./tax.js").seed(); } catch (e) { console.error("tax seed failed:", e.message); }
  try { require("./logistics.js").seed(); } catch (e) { console.error("logistics seed failed:", e.message); }
  try { require("./fin.js").seed(); } catch (e) { console.error("fin seed failed:", e.message); }
  try { require("./marketplace.js").seed(); } catch (e) { console.error("marketplace seed failed:", e.message); }
  try { require("./ugc.js").seed(); } catch (e) { console.error("ugc seed failed:", e.message); }
  try { require("./helpdesk.js").seed(); } catch (e) { console.error("helpdesk seed failed:", e.message); }
  try { require("./recurring.js").seed(); } catch (e) { console.error("recurring seed failed:", e.message); }
  try { require("./risk.js").seed(); } catch (e) { console.error("risk seed failed:", e.message); }
  /* compliance & privacy — the named regulations the corpus declares (GDPR · PCI-DSS ·
     HIPAA · SOC 2 · …), their control catalog, the consent purposes and the rights-request
     lifecycle, all as registry rows an operator extends in Data Studio */
  try { require("./compliance.js").seed(); } catch (e) { console.error("compliance seed failed:", e.message); }
  /* the tenancy hierarchy's tables exist in the schema, but the tenant ROOT is created
     lazily on first access (one row per tenant, addressed as path "<slug>") — no seed rows
     of its own, so this only guarantees the structures are present on a warm DB */
  try { require("./tenancy.js").ensureTables(); } catch (e) { console.error("tenancy tables failed:", e.message); }
  try { require("./experiments.js").seed(); } catch (e) { console.error("experiments seed failed:", e.message); }
  try { require("./planning.js").seed(); } catch (e) { console.error("planning seed failed:", e.message); }
  try { require("./affiliate.js").seed(); } catch (e) { console.error("affiliate seed failed:", e.message); }
  try { require("./sitemap.js").seed(); } catch (e) { console.error("sitemap seed failed:", e.message); }
  try { require("./shipping.js").seed(); } catch (e) { console.error("shipping seed failed:", e.message); }
  /* Event catalog (webhook event types) */
  try { require("./events.js").seed(); } catch (e) { console.error("events seed failed:", e.message); }
  /* RBAC staff roles */
  try { require("./rbac.js").seed(); } catch (e) { console.error("rbac seed failed:", e.message); }
  /* universal theme registry — presets are generated from hue anchors, so the gallery
     is unbounded; an operator's theme is one INSERT and it is live (never a deploy) */
  try { require("./themes.js").seed(); } catch (e) { console.error("themes seed failed:", e.message); }
  /* UCOS Ω∞ constitutional registry — parses Architecture1/2.txt into canonical tables.
     DATA, not code: the documents are the single source of truth (Knowledge-Once).
     Drift is recorded BEFORE the rebuild so an operator can see the constitution changed;
     a warm boot with unchanged files skips the whole ~50k-row rewrite. */
  try {
    const ucosMod = require("./ucos.js");
    const mon = require("./ucos-monitor.js");
    const before = mon.driftStatus();
    if (before.drifted && before.stored) {
      console.error("ucos drift: " + before.message);
      try { run("INSERT INTO platform_settings(key,value) VALUES('ucos_drift_log',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        JSON.stringify({ at: new Date().toISOString(), stored: before.stored, live: before.live, action: "auto-reparsed" })); } catch (e) { }
    }
    const seeded = ucosMod.seed({ get, run, all });
    /* UPIP §1 VISION declares the platform's product universe vocabulary — Physical, Digital,
       OTT, Quantum, "Future Unknown Product Types"… It is the corpus's OWN declaration, so the
       registry list is derived from the parse instead of a JS constant (Knowledge-Once): a
       corpus that declares a 27th universe is reflected with no code change. Refreshed when the
       corpus changed (the digest moved, so a warm boot costs nothing) OR when the row is absent
       — a database that predates this vocabulary must not stay without it forever just because
       the corpus never changed. Merged additively: a universe an operator added in the console
       is kept, because the seed never clobbers what the corpus did not declare. */
    const ex = get("SELECT items FROM meta_lists WHERE name='productUniverses'");
    if (!seeded.skipped || !ex) {
      const declared = ucosMod.productUniverses();
      const kept = ex ? J(ex.items, []).filter(it => it && it.key && !declared.some(d => d.key === it.key)) : [];
      run("INSERT INTO meta_lists(name,label,items,seeded_from) VALUES('productUniverses','productUniverses',?,'ucos_corpus') "
        + "ON CONFLICT(name) DO UPDATE SET items=excluded.items, seeded_from=excluded.seeded_from",
        JSON.stringify(declared.concat(kept)));
    }
    /* UCOS Ω∞ universe instantiation — every universe the corpus declares is registered
       as a foundation and instantiated as a live, data-defined entity, so the constitution
       is OPERABLE, not merely readable. Derived from the parse (never hand-listed) and
       idempotent, so a warm boot costs nothing and an edited corpus re-instantiates itself. */
    try {
      const univ = require("./ucos-universes.js");
      const out = univ.instantiateAll();
      if (out.failed) console.error("ucos universes: " + out.failed + " failed to instantiate");
    } catch (e) { console.error("ucos universe instantiation failed:", e.message); }
    /* the frozen registry's own vocabularies — primitives, canonical terms, domains —
       become platform vocabulary (meta_lists), additive like every other registry list,
       so an operator's extension survives a registry upgrade */
    try {
      require("./ucos-registry.js").seedLists({ get, run, all });
    } catch (e) { console.error("ucos registry lists failed:", e.message); }
    /* the last inch: ACTIVATION. Every universe is now operable (a foundation + a live
       entity), but operable is not TRANSACTABLE — the shelf stays empty until a canonical
       offering is published into a tenant catalog. The flagship store ships with the whole
       corpus activated, so a fresh boot presents the universal catalog on its first
       request. This is the platform's fill-in-the-blank convention applied honestly: the
       flagship opts IN on the operator's behalf (it is the demo of the capability), every
       other store opts in with one call when it wants the corpus. Idempotent and bounded —
       a warm boot sees the shelf already stocked and writes nothing. */
    try {
      const cat = require("./ucos-catalog.js");
      /* which store ships with the corpus activated is DATA, never a slug in code: an operator
         names it in platform_settings.ucosActivationStore. Unset → the first store on a paid
         plan, else the first store — a tenant-agnostic rule that names no store. */
      const named = (() => { try { const r = get("SELECT value v FROM platform_settings WHERE key='ucosActivationStore'"); return r ? JSON.parse(r.v || 'null') : null; } catch (e) { return null; } })();
      const flagship = (named ? get("SELECT id FROM tenants WHERE slug=? AND status='active'", named) : null)
        || get("SELECT t.id FROM tenants t JOIN subscriptions s ON s.tenant_id=t.id JOIN plans p ON p.id=s.plan_id WHERE p.price_month>0 AND t.status='active' ORDER BY t.id LIMIT 1")
        || get("SELECT id FROM tenants ORDER BY id LIMIT 1");
      if (flagship) {
        const out = cat.activateComplete(flagship.id, { limit: 500 });
        if (out.remaining > 0) console.error("ucos activation: " + out.remaining + " universes remain on the flagship shelf");
      }
    } catch (e) { console.error("ucos activation failed:", e.message); }
    /* the universal dashboard + reporting engine seeds alongside (Architecture1 §394/§395):
       canonical dashboards and reports are platform templates, idempotent, never clobbering
       an operator's edit. */
    try { require("./dashboards.js").seed(); } catch (e) { console.error("dashboard seed failed:", e.message); }
    /* UPIP §1/§5 — the global platform catalogue. Every universe the corpus declares is
       seeded as ONE canonical platform product (automatic population); an operator adds
       or edits more in the console (manual configuration). Both are just rows, and a
       store may import one only when the platform has permitted it. Idempotent, so a
       warm boot sees the shelf already stocked and writes nothing. */
    try { require("./gcatalog.js").seed(); } catch (e) { console.error("global catalog seed failed:", e.message); }
    /* 17AH.7 — the freeze criteria are a GATE, not a report. Once the registry is seeded,
       the audit runs and its verdict is stored; the constitutional write routes read it and
       refuse while the foundation is unfreezable. Nothing boots past a violated constitution. */
    try { require("./ucos-completeness.js").bootGate(); } catch (e) { console.error("ucos completeness gate failed:", e.message); }
  } catch (e) { console.error("ucos seed failed:", e.message); }
}

/* ---------- derived projection reconciliation ----------
   The registry's own lists (countries, currencies, provider_defs) are the source of truth.
   Everything *derived* from them — a country's currency row, its FX quote, its availability
   links to every provider declared global — used to be written once, under a COUNT(*)=0 guard,
   and never again. So a country added in Country Master showed up in the master list and
   nowhere else: no currency, no FX, no payment or shipping methods, and a store set to it had
   an empty checkout. This pass closes that gap by deriving forward from the registries.

   It is called on every boot and after any country write. It is strictly additive and
   strictly idempotent: INSERT OR IGNORE only, never an UPDATE of a row an operator could own.
   That is what makes it safe to run on a warm DB — it cannot clobber a merchant's prices,
   rates or unlinking, and on a warm boot it writes nothing because the rows already exist.
   Returns a count of what it materialised, so a caller (a test, or the console) can see that
   a new country actually propagated rather than trusting the seed to have run. */
function reconcileDerived() {
  let linked = 0, cur = 0, fx = 0;
  const link = (pid, cc) => { const r = run("INSERT OR IGNORE INTO provider_availability(provider_id,country_code) VALUES(?,?)", pid, cc); if (r.changes) linked++; };
  const codes = all("SELECT code FROM countries ORDER BY position").map(r => r.code);
  /* 1. a country's official currency must be a resolvable currency entity with an FX quote,
     or `fxTo` silently returns 1 (a flat-money bug that prices nothing correctly) */
  const haveCur = new Set(all("SELECT code FROM currencies").map(r => r.code));
  for (const c of countries()) {
    if (!c.currency || haveCur.has(c.currency)) continue;
    /* the seed's row when it declares the currency (its name and rate); a placeholder only
       for a currency nothing declares — an operator sets its rate */
    const sc = providers.CURRENCIES.find(x => x.code === c.currency) || { code: c.currency, name: c.currency, symbol: c.currency, decimals: seedDecimals(c.currency), usd: 1 };
    run("INSERT OR IGNORE INTO currencies(code,name,symbol,decimals,usd,position) VALUES(?,?,?,?,?,?)", sc.code, sc.name, sc.symbol, sc.decimals, sc.usd, 900);
    haveCur.add(c.currency);
    cur++;
  }
  for (const c of all("SELECT code, usd FROM currencies")) {
    const r = run("INSERT OR IGNORE INTO fx_rates(currency,usd,source,note) VALUES(?,?,?,?)", c.code, c.usd, "derived", "registry reconciliation");
    if (r.changes) fx++;
  }
  /* 2. every provider declared global ("*") is available in EVERY country — including the one
     an operator just added. The declaration is a column now, so a provider flipped global in
     the console fans out on the next pass without a code change. Providers limited to a
     country list are never widened here: their availability is an operator's explicit choice.
     An operator's UNLINK is durable too — reconciliation would be useless if re-running it (or
     adding another country) silently restored the edge the console deleted, so exemptions are
     recorded and honoured. That is what makes the enable/disable toggle in the console real. */
  const exRow = get("SELECT value v FROM platform_settings WHERE key='provider_availability_exempt'");
  const exempt = new Set((() => { try { return JSON.parse(exRow ? exRow.v : "[]"); } catch (e) { return []; } })());
  for (const p of all("SELECT id FROM provider_defs WHERE enabled=1 AND global=1")) {
    for (const cc of codes) {
      if (exempt.has(p.id + "|" + cc)) continue;
      link(p.id, cc);
    }
  }
  /* rows the kernel has never seen (an install that predates the place tree) are imported
     first, so every subdivision written below has its country's place to sit under (P09) */
  let places = null;
  try { places = require("./places.js").importRows(); } catch (e) { console.error("place import failed:", e.message); }
  const sub = reconcileSubdivisions();
  const lnk = reconcileLinks();
  /* each country's primary time zone, Time's setting at its place (lib/time.js) */
  let zones = 0;
  try { zones = require("./time.js").assignZones(); } catch (e) { console.error("time zones failed:", e.message); }
  return { linked, currencies: cur, fx, subdivisions: sub.inserted, links: lnk, places, zones };
}

/* ---------- a country's subdivisions (ISO 3166-2) ----------
    Subdivisions are CHILDREN OF THE COUNTRY MASTER, derived from it and never seeded once
    under a guard. The corpus (lib/subdivisions.js) is the declaration; this pass materialises
    every present country's states/provinces/regions into the `subdivisions` table.

    It runs on every boot AND from entity.js propagate() the moment a country is created, which
    is what makes "add a country and its states/provinces appear" true at write time rather
    than at the next restart. Strictly additive and idempotent: INSERT OR IGNORE only, never an
    UPDATE of a row, so an operator's rename, re-level, re-parent, reorder or deactivation in
    the console survives every pass and a warm boot writes nothing. That is the property that
    makes the subdivision entity editable rather than read-only seed data.

    A subdivision is platform-level master data with no store binding — a store attaches to it
    by resolving its jurisdiction, exactly as it attaches to a country or a currency.
    Returns what it materialised so a caller can confirm a new country actually cascaded. */
function reconcileSubdivisions() {
  return require("./places.js").batch(materialiseSubdivisions);
}
function materialiseSubdivisions() {
  let inserted = 0;
  const exists = new Set(all("SELECT code FROM subdivisions").map(r => r.code));
  /* resolve parent codes to numeric ids as the rows are written, so a country's tree nests to
     any depth: children are inserted after their parent in declaration order (the corpus
     declares a parent before its children), and an unresolved parent falls back to NULL
     (directly under the country) rather than failing the pass — a dangling parent must not
     strand the whole country's subdivisions */
  const idOf = new Map(all("SELECT code, rowid id FROM subdivisions").map(r => [r.code, r.id]));
  for (const c of all("SELECT code FROM countries ORDER BY position, code")) {
    const list = geo.forCountry(c.code);
    if (!list.length) continue;
    for (let i = 0; i < list.length; i++) {
      const s = list[i];
      if (exists.has(s.code)) continue;
      const parentId = s.parent && idOf.has(s.parent) ? idOf.get(s.parent) : null;
      const r = viaPlaces("subdivision", { country_code: c.code, name: s.name, level: s.level, parent_id: parentId, active: 1 }, s.code,
        () => run("INSERT OR IGNORE INTO subdivisions(code,country_code,name,level,parent_id,position,active) VALUES(?,?,?,?,?,?,1)",
          s.code, c.code, s.name, s.level, parentId, i));
      if (r.changes) { idOf.set(s.code, Number(r.lastInsertRowid)); inserted++; }
    }
  }
  return { inserted };
}

/* an operator's unlink of a provider from a country is authoritative — record it so neither
   a boot nor the addition of another country silently restores it. Deleting the row directly
   (the console's existing path) is not enough, because reconcileDerived would re-materialise
   it; the exemption is what makes the console's disable durable. Call this instead of a raw
   DELETE on provider_availability. */
function exemptProvider(providerId, countryCode) {
  const cc = String(countryCode || "").toUpperCase();
  const row = get("SELECT value v FROM platform_settings WHERE key='provider_availability_exempt'");
  let list = []; try { list = JSON.parse(row ? row.v : "[]"); } catch (e) { list = []; }
  const key = providerId + "|" + cc;
  if (!list.includes(key)) list.push(key);
  run("INSERT INTO platform_settings(key,value) VALUES('provider_availability_exempt',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", JSON.stringify(list));
  run("DELETE FROM provider_availability WHERE provider_id=? AND country_code=?", providerId, cc);
  return { ok: true, exempt: key };
}
function unexemptProvider(providerId, countryCode) {
  const cc = String(countryCode || "").toUpperCase();
  const row = get("SELECT value v FROM platform_settings WHERE key='provider_availability_exempt'");
  let list = []; try { list = JSON.parse(row ? row.v : "[]"); } catch (e) { list = []; }
  const key = providerId + "|" + cc;
  const next = list.filter(x => x !== key);
  run("INSERT INTO platform_settings(key,value) VALUES('provider_availability_exempt',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", JSON.stringify(next));
  run("DELETE FROM provider_availability WHERE provider_id=? AND country_code=?", providerId, cc);
  return { ok: true };
}

/* ---------- the relationship projection (product→product view of the typed primitive) ----------
   `links` is the relationship primitive: a typed edge between any two entities by universal id,
   created once and reused everywhere. A store's catalogue relates PRODUCTS, so the storefront
   and the admin product view read a product-scoped projection — `relationships` — keyed by the
   store's own product ids. This pass materialises that projection from the primitive.

   It runs on every boot AND from entity.js propagate() the moment a link is created or removed,
   which is what makes "write the edge and it is in the store's catalogue" true at write time
   rather than at the next restart. Strictly idempotent: a projection row is only INSERTed where
   the primitive has an edge the projection lacks, and a projection row whose primitive edge is
   gone is withdrawn, so the two can never drift in either direction. An operator's edge is data
   either way — adding one here is an INSERT, and deleting the primitive row takes its
   projection with it on the next pass. */
function reconcileLinks() {
  let inserted = 0, withdrawn = 0;
  /* a product's uid is only unique within the platform (products' PK is (tenant_id, id)), so
     resolve endpoints through the store that owns them — an edge belongs to exactly one store,
     the one both endpoints live in. A uid that resolves to no product is either a non-product
     endpoint (GOIP's offer/budget/customer edges) or a deleted one; neither gets a projection
     row, and a dangling projection row is withdrawn below. */
  const pByUid = new Map(all("SELECT id, tenant_id, uid FROM products WHERE uid IS NOT NULL").map(r => [r.uid, r]));
  const edges = new Set();
  for (const l of all("SELECT type, from_uid, to_uid, meta FROM links WHERE from_entity='product' AND to_entity='product'")) {
    const from = pByUid.get(l.from_uid), to = pByUid.get(l.to_uid);
    if (!from || !to || from.tenant_id !== to.tenant_id) continue;
    edges.add(from.tenant_id + "|" + from.id + "|" + to.id + "|" + l.type);
    const r = run("INSERT OR IGNORE INTO relationships(tenant_id,from_id,to_id,type) VALUES(?,?,?,?)",
      from.tenant_id, from.id, to.id, l.type);
    if (r.changes) inserted++;
  }
  /* withdraw the projection rows the primitive no longer backs — a deleted edge must not
     outlive its primitive in the store's catalogue */
  for (const r of all("SELECT id, tenant_id, from_id, to_id, type FROM relationships")) {
    if (edges.has(r.tenant_id + "|" + r.from_id + "|" + r.to_id + "|" + r.type)) continue;
    run("DELETE FROM relationships WHERE id=?", r.id); withdrawn++;
  }
  return { inserted, withdrawn };
}

/* an operator's removal of a country is authoritative for its subdivisions too: the children
   are derived FROM the country, so once it is gone they have no master to belong to and
   reconciliation would re-materialise nothing (the corpus declares them only for a country
   that is present). Call this alongside the availability cleanup when a country is deleted,
   so removing one leaves no dangling jurisdiction rows. */
function withdrawCountry(countryCode) {
  const cc = String(countryCode || "").toUpperCase();
  /* the subdivisions' places are archived on the kernel in the same transaction (lib/places.js) */
  return require("./places.js").withdrawSubdivisions(cc, () => { run("DELETE FROM subdivisions WHERE country_code=?", cc); return { ok: true, code: cc }; });
}

/* ---------- read API (DB is source of truth) ---------- */
function list(name) {
  const r = get("SELECT items FROM meta_lists WHERE name=?", name);
  return r ? J(r.items, name.includes("ical") || name === "lifecycleTransitions" || name === "uomConversions" || name === "industryVertical" || name === "verticals" || name === "verticalFields" ? {} : []) : [];
}
/* a country's currency and locale are not columns of the place: they are Value's and
   Expression's settings, assigned at the place's node on the kernel and answered by the resolver
   (lib/places.js facts); its money symbol and decimals are its currency's, from Value's master.
   A legacy column an older install still carries is never read: the kernel answers. */
function withFacts(row) {
  if (!row) return row;
  let f = {};
  try { f = require("./places.js").facts(row.code); } catch (e) { return row; }
  const out = { ...row };
  for (const col of require("./places.js").RETIRED) delete out[col];
  Object.assign(out, f);
  const cur = f.currency ? currency(f.currency) : null;
  if (cur) { out.symbol = cur.symbol; out.decimals = cur.decimals; }
  return out;
}
function countries() { return all("SELECT * FROM countries ORDER BY position").map(withFacts); }
function country(code) { return withFacts(get("SELECT * FROM countries WHERE code=?", code) || get("SELECT * FROM countries ORDER BY position LIMIT 1")); }
function currencies() { return all("SELECT * FROM currencies WHERE active=1 ORDER BY position"); }
/* ---------- Value: every unit of value (lib/seed/value.json) ----------
   The units this platform ships beyond the currency seed arrive switched off, once; units an
   operator added to the offer engine's old list are imported once. A row's class is Value's
   class list's; a row with none is in the default class. */
function seedUnits() {
  const have = new Set(all("SELECT code FROM currencies").map(r => r.code));
  VALUE.units.forEach((u, i) => {
    if (have.has(u.code)) return;
    run("INSERT INTO currencies(code,name,symbol,decimals,usd,position,active,class,settleable) VALUES(?,?,?,?,?,?,0,?,?)", u.code, u.name, u.symbol, u.decimals, u.usd, 1000 + i, u.class, u.settleable ? 1 : 0);
    have.add(u.code);
  });
  const legacy = J((get("SELECT items FROM meta_lists WHERE name=?", VALUE.legacyUnitList) || {}).items, []);
  const re = new RegExp(VALUE.codePattern);
  for (const u of Array.isArray(legacy) ? legacy : []) {
    const code = String((u && u.key) || "").toUpperCase();
    if (!re.test(code) || have.has(code)) continue;
    run("INSERT INTO currencies(code,name,symbol,decimals,usd,position,active,class,settleable) VALUES(?,?,?,?,?,?,0,?,?)", code, u.name || code, code, Number(u.decimals) || 0, Number(u.base_rate) || 0, 1100, u.class || null, u.settleable === false ? 0 : 1);
    have.add(code);
  }
  /* classes an operator added to the offer engine's old class list join Value's */
  const oldClasses = J((get("SELECT items FROM meta_lists WHERE name=?", VALUE.legacyClassList) || {}).items, []);
  const cur = list(VALUE.classList);
  if (Array.isArray(cur) && cur.length && Array.isArray(oldClasses)) {
    const add = oldClasses.filter(c => c && c.key && !cur.some(x => x.key === c.key));
    if (add.length) run("UPDATE meta_lists SET items=? WHERE name=?", JSON.stringify(cur.concat(add)), VALUE.classList);
  }
}
function unitRow(u) {
  return { key: u.code, code: u.code, name: u.name, symbol: u.symbol, class: u.class || VALUE.defaultClass, decimals: u.decimals, base_rate: u.usd, usd: u.usd, settleable: u.settleable !== 0, active: u.active !== 0 };
}
function units() { return all("SELECT * FROM currencies ORDER BY position, code").map(unitRow); }
function unit(code) { const u = currency(code); return u ? unitRow(u) : null; }
function valueClasses() { const l = list(VALUE.classList); return Array.isArray(l) && l.length ? l : VALUE.classes; }
function currency(code) { return get("SELECT * FROM currencies WHERE code=?", String(code || "").toUpperCase()); }
function fxTo(base, target) { const b = currency(base), t = currency(target); if (!b || !t || !t.usd) return 1; return +(b.usd / t.usd).toFixed(6); }
function taxModes() { return all("SELECT * FROM tax_modes ORDER BY position").map(t => ({ ...t, fields: J(t.fields, []) })); }
function providerDefs(kind) {
  const rows = kind ? all("SELECT * FROM provider_defs WHERE kind=? AND enabled=1 ORDER BY position", kind)
    : all("SELECT * FROM provider_defs WHERE enabled=1 ORDER BY kind, position");
  return rows.map(p => ({ id: p.id, name: p.name, emoji: p.emoji, desc: p.description, methods: J(p.methods, []), feePct: p.fee_pct, feeFixed: p.fee_fixed, fields: J(p.fields, []), baseFee: p.base_fee || undefined, eta: p.eta_min != null ? [p.eta_min, p.eta_max] : undefined }));
}
function providersFor(kind, countryCode) {
  return all(`SELECT pd.* FROM provider_availability pa JOIN provider_defs pd ON pd.id=pa.provider_id
              WHERE pa.country_code=? AND pd.kind=? AND pd.enabled=1 ORDER BY pd.position`, countryCode, kind)
    .map(p => ({ id: p.id, name: p.name, emoji: p.emoji, desc: p.description, methods: J(p.methods, []), feePct: p.fee_pct, feeFixed: p.fee_fixed, fields: J(p.fields, []), baseFee: p.base_fee || undefined, eta: p.eta_min != null ? [p.eta_min, p.eta_max] : undefined }));
}
function countryProfile(code) {
  const c = country(code);
  if (!c) return null;
  return {
    code: c.code, name: c.name, currency: c.currency, symbol: c.symbol, locale: c.locale, decimals: c.decimals,
    /* tax is the tax engine's (lib/tax.js), never a column of the country */
    tax: (() => { const t = require("./tax.js").ruleFor(c.code); return t ? { mode: t.mode, rate: t.standard } : null; })(),
    subdivisions: subdivisionsFor(c.code),
    payments: providersFor("payment", c.code), shipping: providersFor("shipping", c.code),
    notifications: providersFor("notification", c.code)
  };
}
/* a country's subdivisions, parents before children (breadth by generation), so any consumer
   rendering a jurisdiction tree or a dependent dropdown reads them in nesting order. Active
   unless the operator deactivated one — the master stays reusable everywhere either way. */
function subdivisionsFor(countryCode) {
  const cc = String(countryCode || "").toUpperCase();
  return all("SELECT code, country_code, name, level, parent_id, position, active FROM subdivisions WHERE country_code=? ORDER BY parent_id IS NOT NULL, parent_id, position, code", cc);
}
function supports(providerId, countryCode) {
  return !!get("SELECT 1 ok FROM provider_availability WHERE provider_id=? AND country_code=?", providerId, countryCode);
}

/* ======================================================================
   AUTO-DISCOVERED REGISTRY AUTHORING
   Every platform vocabulary — deploy modes, industries, statuses, roles,
   provider types — is a `meta_lists` row. This is the console's read/write
   surface over ALL of them. Names are never enumerated in code: the table is
   scanned, so a list created anywhere (a new engine, a future seed) becomes
   authorable here the moment it exists. That is what keeps "add a platform
   mode" a data change rather than a code change, and what makes the surface
   auto-discovering instead of a hand-maintained list that drifts.
   ====================================================================== */

/* per-tenant forks (staffRoles:t12) are store-scoped, not platform vocabulary —
   they are excluded so the surface only authors the lists every store inherits */
const STORE_ROW = /:[tT]\d+$/;
function listAll() {
  return all("SELECT name, label, items, seeded_from, edited FROM meta_lists ORDER BY name")
    .filter(r => !STORE_ROW.test(r.name))
    .map(r => {
      const items = J(r.items, []);
      const arr = Array.isArray(items) ? items : [];
      /* SHAPE: the union of keys across the live entries — the authoring form is
         scaffolded from what the data actually carries, never a schema in code */
      const keys = new Set(); const types = {};
      for (const it of arr) if (it && typeof it === "object") for (const k of Object.keys(it)) {
        keys.add(k);
        const t = Array.isArray(it[k]) ? "array" : typeof it[k];
        if (!(types[k] instanceof Map)) types[k] = new Map();
        types[k].set(t, (types[k].get(t) || 0) + 1);
      }
      return { name: r.name, label: r.label || r.name, count: arr.length,
        edited: Number(r.edited || 0) > 0, seeded_from: r.seeded_from || null,
        shape: [...keys].map(k => ({ key: k, type: mostCommon(types[k]) })) };
    });
}
function mostCommon(counts) {
  if (!counts || !counts.size) return "string";
  let best = "string", n = -1;
  for (const [t, c] of counts) if (c > n) { n = c; best = t; }
  return best === "object" ? "array" : best;
}
function readList(name) {
  const r = get("SELECT items FROM meta_lists WHERE name=?", name);
  if (!r) return null;
  const items = J(r.items, []);
  return Array.isArray(items) ? items : [];
}
/* AUTO-RECOMMEND: infer a new entry from the list's own live contents. Fields the
   existing entries carry are pre-scaffolded with defaults of the observed type, `key`
   is derived from the label, and `name` carries the label through — so authoring never
   depends on a schema written anywhere but the data itself. A list with no items yet
   still yields a sensible { key, name } skeleton. */
function recommend(name, label) {
  const items = readList(name) || [];
  const shape = new Map();
  for (const it of items) if (it && typeof it === "object")
    for (const k of Object.keys(it)) if (!shape.has(k)) shape.set(k, mostCommon((() => { const m = new Map(); m.set(Array.isArray(it[k]) ? "array" : typeof it[k], 1); return m; })()));
  const key = slugify(label);
  const out = {};
  if (!shape.size) { out.key = key; out.name = String(label || ""); return out; }
  for (const [k, t] of shape) {
    if (k === "key") out.key = key;
    else if (k === "name" || k === "label" || k === "description" || k === "desc") out[k] = k === "name" ? String(label || "") : "";
    else if (t === "number") out[k] = 0;
    else if (t === "boolean") out[k] = false;
    else if (t === "array") out[k] = [];
    else out[k] = "";
  }
  if (!out.key) out.key = key;
  return out;
}
function slugify(s) {
  return String(s || "").trim().toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "").slice(0, 40);
}
/* a list's entry is keyed by `key` when its items are objects, or is the string itself */
function entryKey(it) { return (it && typeof it === "object") ? String(it.key != null ? it.key : "") : String(it); }
function saveItem(name, item) {
  const r = get("SELECT items FROM meta_lists WHERE name=?", name);
  if (!r) return { ok: false, error: "Unknown registry" };
  const items = J(r.items, []);
  if (!Array.isArray(items)) return { ok: false, error: "This registry is not a list and cannot be authored item-by-item" };
  const key = entryKey(item);
  if (!key) return { ok: false, error: "An entry needs a key" };
  const invalid = VALIDATE[name] ? VALIDATE[name](item) : null;
  if (invalid) return { ok: false, error: invalid };
  const idx = items.findIndex(x => entryKey(x) === key);
  if (idx >= 0) items[idx] = item; else items.push(item);
  run("UPDATE meta_lists SET items=?, edited=1 WHERE name=?", JSON.stringify(items), name);
  return { ok: true, key, items };
}
/* ---------- platform kinds ----------
   A kind is a `deployModes` row. A row saved before a field existed takes the shipped seed's
   value for its key, and an operator's own row without it takes KIND_DEFAULTS — so an older
   row never loses a behaviour and a new kind needs only a key and a name. */
const KIND_DEFAULTS = { noun: "platform", nounPlural: "platforms", archetype: "", needsIndustries: false,
  provision: { payments: true, shipping: true, warehouse: true, storefront: true }, sections: null };
function normKind(row) {
  if (!row || typeof row !== "object") return null;
  const seed = meta.DEPLOY_MODES.find(m => m.key === row.key) || {};
  const pick = k => row[k] != null ? row[k] : (seed[k] != null ? seed[k] : KIND_DEFAULTS[k]);
  const prov = Object.assign({}, KIND_DEFAULTS.provision, seed.provision || {}, row.provision && typeof row.provision === "object" ? row.provision : {});
  for (const k of Object.keys(prov)) prov[k] = !!prov[k];
  const sections = pick("sections");
  return { ...row, name: row.name || row.key, desc: row.desc || "", noun: String(pick("noun")), nounPlural: String(pick("nounPlural")),
    archetype: String(pick("archetype") || ""), needsIndustries: !!pick("needsIndustries"), provision: prov,
    sections: Array.isArray(sections) ? sections.map(String) : null };
}
function kinds() { const l = list("deployModes"); return (Array.isArray(l) ? l : []).map(normKind).filter(Boolean); }
function kind(key) { return kinds().find(k => k.key === key) || null; }
/* what a saved entry must satisfy, per registry — data about the list, extended by adding a
   row. Answers an error message, or null when the entry is sound. */
const VALIDATE = {
  deployModes: it => {
    if (!/^[a-z][a-z0-9_]{1,39}$/.test(String(it.key || ""))) return "A kind's key is 2–40 lowercase letters, digits or underscores, starting with a letter";
    if (!String(it.name || "").trim()) return "A kind needs a name";
    if (it.archetype && !get("SELECT key FROM capability_presets WHERE key=?", String(it.archetype))) return "Unknown starting blend: " + it.archetype;
    if (it.provision != null && (typeof it.provision !== "object" || Array.isArray(it.provision))) return "provision is an object of on/off switches";
    if (it.sections != null) {
      if (!Array.isArray(it.sections)) return "sections is a list of console sections, or null for all of them";
      let known = null; try { known = new Set(require("./authz.js").SURFACES.store); } catch (e) { }
      const bad = known && known.size ? it.sections.filter(x => !known.has(String(x))) : [];
      if (bad.length) return "Unknown console section(s): " + bad.join(", ");
    }
    return null;
  }
};
/* deleting a vocabulary still in use would leave dangling references — refuse with the
   tenants that keep the entry, so the operator can retire them first. The guard table is
   data about the list, not a switch statement: extend it by adding a row. */
const USAGE = {
  deployModes: k => all("SELECT slug FROM tenants WHERE mode=?", k).map(r => r.slug),
  industries: k => all("SELECT slug FROM tenants WHERE industries LIKE ?", '%"' + String(k).replace(/[%_]/g, c => "\\" + c) + '"%').map(r => r.slug)
};
function usageOf(name, key) { try { const g = USAGE[name]; return g ? g(key) : []; } catch (e) { return []; } }
function deleteItem(name, key) {
  const r = get("SELECT items FROM meta_lists WHERE name=?", name);
  if (!r) return { ok: false, error: "Unknown registry" };
  const items = J(r.items, []);
  if (!Array.isArray(items)) return { ok: false, error: "This registry is not a list and cannot be authored item-by-item" };
  const inUse = usageOf(name, key);
  if (inUse.length) return { ok: false, error: "In use by " + inUse.length + " platform(s): " + inUse.slice(0, 5).join(", ") + (inUse.length > 5 ? "…" : "") + " — reassign them before removing this entry" };
  const next = items.filter(x => entryKey(x) !== key);
  if (next.length === items.length) return { ok: false, error: "No such entry" };
  run("UPDATE meta_lists SET items=?, edited=1 WHERE name=?", JSON.stringify(next), name);
  return { ok: true, key, items: next };
}
/* AUTO-UPGRADE: a registry-seed version bump delivers NEW built-in defaults to a list an
   operator has already edited — additively, keyed by entry. Entries they changed are
   never touched; only canonical entries the list does not yet have arrive. Exported so the
   upgrade contract is testable without a reboot. */
/* the keys of a list whatever its rows' shape (plain names or { key } objects) */
function keys(name) { const l = list(name); return (Array.isArray(l) ? l : []).map(x => (x && typeof x === "object" ? String(x.key) : String(x))); }
/* a list that was seeded as plain names and now declares behaviour on object rows is
   upgraded in place: each name becomes its seed row (or { key, name } when the operator
   added it), so the vocabulary survives and gains its fields */
function upgradeShape(name, seedItems) {
  try {
    const row = get("SELECT items FROM meta_lists WHERE name=?", name); if (!row) return 0;
    const cur = J(row.items, []); if (!Array.isArray(cur) || !cur.some(x => typeof x === "string")) return 0;
    const out = cur.map(x => typeof x === "string" ? Object.assign({ key: x, name: x }, (seedItems || []).find(sd => sd && sd.key === x) || {}) : x);
    run("UPDATE meta_lists SET items=? WHERE name=?", JSON.stringify(out), name);
    return out.length;
  } catch (e) { return 0; }
}
/* a field a seed newly declares on its rows (a behaviour: an engine name, a rate source…)
   reaches an existing install: each row keyed like a seed row gets the field only where it
   has none — an operator's own values are never overwritten */
function addFields(name, seedItems, fields) {
  try {
    const row = get("SELECT items FROM meta_lists WHERE name=?", name); if (!row) return 0;
    const cur = J(row.items, []); if (!Array.isArray(cur)) return 0;
    let n = 0;
    for (const c of cur) {
      if (!c || typeof c !== "object") continue;
      const sd = (seedItems || []).find(x => x && x.key === c.key); if (!sd) continue;
      for (const f of fields) if (c[f] === undefined && sd[f] !== undefined) { c[f] = sd[f]; n++; }
    }
    if (n) run("UPDATE meta_lists SET items=? WHERE name=?", JSON.stringify(cur), name);
    return n;
  } catch (e) { return 0; }
}
function mergeDefaults(current, defaults) {
  if (!Array.isArray(current) || !Array.isArray(defaults)) return current;
  const known = new Set(current.map(entryKey));
  const out = current.slice();
  for (const it of defaults) {
    const k = entryKey(it);
    if (!k || known.has(k)) continue;
    out.push(it); known.add(k);
  }
  return out;
}

module.exports = { units, unit, valueClasses, VALUE, withFacts, ensureCurrency, addFields, upgradeShape, keys, seedRegistries, repairCountries, reconcileDerived, reconcileSubdivisions, reconcileLinks, withdrawCountry, exemptProvider, unexemptProvider, list, countries, country, currencies, currency, fxTo, taxModes, providerDefs, providersFor, subdivisionsFor, countryProfile, supports, J,
  listAll, readList, recommend, saveItem, deleteItem, usageOf, mergeDefaults, kinds, kind, normKind, KIND_DEFAULTS };
