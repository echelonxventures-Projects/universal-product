/* LUXORA Platform - applicability rules: WHERE, FOR WHOM and FOR WHAT anything applies.

   One engine answers "may this subject be used in this context?" for every registered thing —
   a payment gateway, a payment method, a bank, a carrier, a notifier, a capability, a module,
   a service — and every engine that makes a choice asks it. Nothing here names a provider,
   a country or a service: the subject types, the dimensions a rule can be scoped by, the
   services, the segments, the channels, the banks and the country groups are all registry
   rows (meta_lists), editable in the console.

   A rule  = subject (type + id, or "*" for every subject of the type)
           + scope   (any registered dimension: platform kinds, platforms, countries or groups,
                      regions, currencies, services, segments, channels… plus an amount range
                      and a date window; an empty dimension means "any")
           + effect  (allow · deny · prefer) + priority + params (overrides the engine reads).

   Decision, per layer:
     · the most specific matching rule wins (a named subject beats "*", then more dimensions);
       at equal specificity deny beats allow.
     · a subject that has allow rules is ALLOW-LISTED in that layer: outside every one of them
       it is blocked. A subject with no rules is open.
     · a context that does not know a dimension (no buyer yet, no amount yet) is evaluated
       optimistically for allow rules ("available to someone") and never fires a deny on it.
   Layers: the platform owner's rules (tenant_id NULL) bound every platform; a platform's own
   rules (tenant_id = the platform) can only narrow inside them — both must permit. */
"use strict";

const { AsyncLocalStorage } = require("async_hooks");
const db = () => require("./db.js");
const registry = () => require("./registry.js");
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };
const arr = v => Array.isArray(v) ? v : (v == null || v === "" ? [] : [v]);
const S = v => String(v == null ? "" : v);
const EFFECTS = ["allow", "deny", "prefer"];

/* ---------------- registry seeds (rows, not code paths) ---------------- */
const SUBJECT_TYPES = [
  { key: "gateway", name: "Payment gateway", source: "providers:payment" },
  { key: "method", name: "Payment method", source: "methods" },
  { key: "bank", name: "Bank", source: "list:banks" },
  { key: "carrier", name: "Shipping carrier", source: "providers:shipping" },
  { key: "notifier", name: "Notification channel", source: "providers:notification" },
  { key: "marketing", name: "Marketing integration", source: "providers:marketing" },
  { key: "ai", name: "AI provider", source: "providers:ai" },
  { key: "capability", name: "Capability", source: "capabilities" },
  { key: "module", name: "Module capability", source: "modules" },
  { key: "service", name: "Service", source: "list:services" },
  { key: "ai_capability", name: "AI capability", source: "list:aiCapabilities" },
  { key: "ai_model", name: "AI model", source: "list:aiModels" },
  { key: "promotion", name: "Promotion", source: "entity:promotion" },
  { key: "offer", name: "Offer / exchange", source: "rows:offers:id:name" },
  { key: "coupon", name: "Coupon code", source: "rows:coupons:code:code" },
  { key: "login_method", name: "Sign-in method", source: "loginMethods" }
];
/* a subject type's SOURCE is how its subjects are enumerated, and every source is generic:
     providers:<kind>          any provider kind (payment, shipping, ai, a custom kind …)
     list:<registry list>      any registry list (services, banks, aiModels, a list you add)
     entity:<entity key>       any Data Studio entity, built-in or one an operator defines
     rows:<table>:<id>:<label> any table's rows (scoped to the platform when it has tenant_id)
     capabilities · modules · methods · loginMethods
   so a new kind of thing becomes rule-able by adding one registry row. */
const DIMENSIONS = [
  { key: "kinds", name: "Platform kinds", fact: "kind", match: "in", options: "kinds" },
  { key: "platforms", name: "Platforms", fact: "platform", match: "in", options: "platforms" },
  { key: "countries", name: "Countries or groups", fact: "country", match: "country", options: "countries" },
  { key: "regions", name: "States / regions", fact: "region", match: "prefix", options: "subdivisions" },
  { key: "currencies", name: "Currencies", fact: "currency", match: "in", options: "currencies" },
  { key: "services", name: "Services", fact: "service", match: "in", options: "list:services" },
  { key: "segments", name: "Customer segments", fact: "segments", match: "any", options: "segments" },
  { key: "channels", name: "Channels", fact: "channel", match: "in", options: "list:channels" }
];
const SERVICES = [
  { key: "order", name: "Shop orders" }, { key: "subscription", name: "Subscriptions & memberships" },
  { key: "ride", name: "Ride fares" }, { key: "bill_pay", name: "Bill payments" }, { key: "recharge", name: "Mobile recharge" },
  { key: "payout", name: "Bank payouts" }, { key: "transfer", name: "Wallet transfers" }, { key: "upi_collect", name: "UPI collect requests" },
  { key: "payment_link", name: "Payment links" }, { key: "mandate", name: "Recurring mandates" }, { key: "escrow", name: "Escrow holds" },
  { key: "bnpl", name: "Buy now, pay later" }, { key: "loan", name: "Loans" }, { key: "insurance", name: "Insurance" }
];
const SEGMENTS = [
  { key: "retail", name: "Retail customers" }, { key: "wholesale", name: "Wholesale / B2B buyers" },
  { key: "premium", name: "Premium customers" }, { key: "corporate", name: "Corporate accounts" },
  { key: "guest", name: "Guests (not signed in)", auto: "guest" }, { key: "signed_in", name: "Signed-in customers", auto: "signed_in" }
];
const CHANNELS = [{ key: "web", name: "Web" }, { key: "app", name: "Mobile app" }, { key: "pos", name: "Point of sale" }, { key: "api", name: "API / partner" }];
/* a bank is identified by its key, or recognised from an IFSC / SWIFT prefix on an account */
const BANKS = [
  { key: "sbi", name: "State Bank of India", country: "IN", ifsc: "SBIN", swift: "SBIN" },
  { key: "hdfc", name: "HDFC Bank", country: "IN", ifsc: "HDFC", swift: "HDFC" },
  { key: "icici", name: "ICICI Bank", country: "IN", ifsc: "ICIC", swift: "ICIC" },
  { key: "axis", name: "Axis Bank", country: "IN", ifsc: "UTIB", swift: "AXIS" },
  { key: "kotak", name: "Kotak Mahindra Bank", country: "IN", ifsc: "KKBK", swift: "KKBK" },
  { key: "chase", name: "JPMorgan Chase", country: "US", swift: "CHAS" },
  { key: "bofa", name: "Bank of America", country: "US", swift: "BOFA" },
  { key: "wells", name: "Wells Fargo", country: "US", swift: "WFBI" },
  { key: "barclays", name: "Barclays", country: "GB", swift: "BARC" },
  { key: "hsbc", name: "HSBC", country: "GB", swift: "HBUK" },
  { key: "deutsche", name: "Deutsche Bank", country: "DE", swift: "DEUT" },
  { key: "bnp", name: "BNP Paribas", country: "FR", swift: "BNPA" },
  { key: "ing", name: "ING", country: "NL", swift: "INGB" },
  { key: "itau", name: "Itaú Unibanco", country: "BR", swift: "ITAU" },
  { key: "dbs", name: "DBS Bank", country: "SG", swift: "DBSS" },
  { key: "mufg", name: "MUFG Bank", country: "JP", swift: "BOTK" },
  { key: "enbd", name: "Emirates NBD", country: "AE", swift: "EBIL" },
  { key: "equity", name: "Equity Bank", country: "KE", swift: "EQBL" }
];
const COUNTRY_GROUPS = [
  { key: "EU", name: "European Union", countries: ["AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE"] },
  { key: "GCC", name: "Gulf Cooperation Council", countries: ["AE", "SA", "QA", "KW", "BH", "OM"] },
  { key: "NA", name: "North America", countries: ["US", "CA", "MX"] },
  { key: "APAC", name: "Asia-Pacific", countries: ["IN", "SG", "JP", "AU", "CN", "HK", "KR", "ID", "MY", "TH", "PH", "VN", "NZ"] },
  { key: "LATAM", name: "Latin America", countries: ["BR", "MX", "AR", "CL", "CO", "PE"] }
];
const PAYMENT_METHODS = [{ key: "cash", name: "Cash" }, { key: "wallet", name: "Platform wallet" }, { key: "card", name: "Card" }];
const LISTS = { paymentMethods: PAYMENT_METHODS, ruleSubjectTypes: SUBJECT_TYPES, ruleDimensions: DIMENSIONS, services: SERVICES, segments: SEGMENTS, channels: CHANNELS, banks: BANKS, countryGroups: COUNTRY_GROUPS };

/* the vocabularies are read on every decision, so they are memoised briefly; an edit in the
   console reaches the engine within the TTL (and at once through bust()) */
const LIST_CACHE = new Map();
function list(name) {
  const hit = LIST_CACHE.get(name);
  if (hit && Date.now() - hit.at < TTL) return hit.v;
  let v = null;
  try { const l = registry().list(name); if (Array.isArray(l) && l.length) v = l; } catch (e) { }
  v = v || LISTS[name] || [];
  LIST_CACHE.set(name, { at: Date.now(), v });
  return v;
}
const keyOf = x => S(x && typeof x === "object" ? x.key : x);

/* ---------------- storage + cache ---------------- */
let CACHE = null;
const TTL = 5000;
/* a rule change reaches every cached answer at once: the settings snapshot caches the
   platform-level capability decisions, so it is dropped for every platform too */
function bust() { CACHE = null; FACTS.clear(); LIST_CACHE.clear(); try { require("./settings.js").bust(); } catch (e) { } }
function rows() {
  if (CACHE && Date.now() - CACHE.at < TTL) return CACHE.rows;
  let raw = [];
  try { raw = db().all("SELECT * FROM applicability_rules WHERE active=1 ORDER BY id"); } catch (e) { raw = []; }
  const out = raw.map(norm);
  CACHE = { at: Date.now(), rows: out, contextualCaps: out.some(r => (r.subject_type === "capability" || r.subject_type === "module") && buyerScoped(r)) };
  return out;
}
function norm(r) {
  const scope = J(r.scope, {}) || {};
  return { id: r.id, tenant_id: r.tenant_id == null ? null : Number(r.tenant_id), subject_type: S(r.subject_type), subject: S(r.subject || "*"),
    effect: EFFECTS.includes(r.effect) ? r.effect : "allow", priority: Number(r.priority) || 0, scope, params: J(r.params, {}) || {},
    note: S(r.note), active: r.active == null ? 1 : Number(r.active), created_by: r.created_by || null, created_at: r.created_at, updated_at: r.updated_at };
}
/* a rule that depends on who is buying — it can only decide once a buyer context exists */
const BUYER_FACTS = new Set(["segments", "channel", "service", "region"]);
function buyerScoped(r) {
  const sc = r.scope || {};
  if (sc.min_amount != null || sc.max_amount != null) return true;
  return list("ruleDimensions").some(d => BUYER_FACTS.has(d.fact) && arr(sc[d.key]).length);
}

/* ---------------- request context (the buyer behind this request) ---------------- */
const als = new AsyncLocalStorage();
function run(store, fn) { return als.run(store || {}, fn); }
function current() { return als.getStore() || null; }

/* the platform's own facts: its kind, its id/slug, its country and that country's currency */
const FACTS = new Map();
function platformFacts(tenantId) {
  const tid = Number(tenantId) || 0;
  if (!tid) return {};
  const hit = FACTS.get(tid);
  if (hit && Date.now() - hit.at < TTL) return hit.f;
  let t = null; try { t = db().get("SELECT id, slug, mode, country FROM tenants WHERE id=?", tid); } catch (e) { }
  let currency = null;
  if (t && t.country) { try { currency = (db().get("SELECT currency FROM countries WHERE code=?", String(t.country).toUpperCase()) || {}).currency || null; } catch (e) { } }
  const f = t ? { tenant_id: t.id, platform: t.slug, kind: t.mode, country: t.country ? String(t.country).toUpperCase() : null, currency } : { tenant_id: tid };
  FACTS.set(tid, { at: Date.now(), f });
  return f;
}
/* the buyer's segments: explicit memberships, the automatic ones (guest / signed in) and the
   offers engine's computed audiences (new / returning / high value …) */
function segmentsOf(tenantId, owner) {
  const out = new Set();
  const signed = /:u:\d+$/.test(S(owner));
  for (const sg of list("segments")) {
    if (sg && sg.auto === "guest" && owner && !signed) out.add(sg.key);
    if (sg && sg.auto === "signed_in" && signed) out.add(sg.key);
  }
  if (owner) {
    try { for (const r of db().all("SELECT segment FROM segment_members WHERE tenant_id=? AND owner=?", Number(tenantId), S(owner))) out.add(r.segment); } catch (e) { }
    try {
      const o = db().get("SELECT COUNT(*) n, COALESCE(SUM(total),0) v FROM orders WHERE tenant_id=? AND owner=?", Number(tenantId), S(owner)) || {};
      for (const k of require("./goip.js").personalize(Number(tenantId), owner, { orders: o.n || 0, lifetime: o.v || 0 })) out.add(k);
    } catch (e) { }
  }
  return [...out];
}
/* buyer facts from the current request, when it is a shopper's (not staff, not the platform) */
function buyerFacts(tenantId) {
  const st = current();
  if (!st || !st.s) return {};
  const s = st.s;
  if (s.platform_admin || st.staff) return {};
  if (s.tenant && Number(s.tenant.id) !== Number(tenantId)) return {};
  const f = {};
  const hdr = st.req && st.req.headers ? st.req.headers : {};
  const ch = S(hdr["x-channel"] || "").toLowerCase();
  f.channel = ch && list("channels").some(c => keyOf(c) === ch) ? ch : (list("channels")[0] ? keyOf(list("channels")[0]) : "web");
  const owner = s.user_id ? `t${tenantId}:u:${s.user_id}` : (s.sid ? `t${tenantId}:s:${s.sid}` : "");
  /* a dimension an operator declares later reads its fact from the request with no code:
     body.context.<fact>, the x-ctx-<fact> header or the ctx_<fact> query parameter */
  const known = new Set(["kind", "platform", "country", "currency", "segments", "channel", "tenant_id", "at"]);
  const bctx = st.body && typeof st.body === "object" && st.body.context && typeof st.body.context === "object" ? st.body.context : {};
  for (const d of list("ruleDimensions")) {
    const k = S(d.fact); if (!k || known.has(k)) continue;
    const v = bctx[k] != null ? bctx[k] : (hdr["x-ctx-" + k.toLowerCase()] || (st.url && st.url.searchParams ? st.url.searchParams.get("ctx_" + k) : null));
    if (v != null && v !== "") f[k] = Array.isArray(v) ? v.map(S) : S(v).slice(0, 120);
  }
  for (const k of ["country", "region", "currency", "service"]) {
    const v = bctx[k] != null ? bctx[k] : null;
    if (v != null && v !== "") f[k] = k === "region" ? S(v).toUpperCase() : (k === "service" ? S(v) : S(v).toUpperCase());
  }
  Object.defineProperty(f, "segments", { enumerable: true, configurable: true, get() { const v = segmentsOf(tenantId, owner); Object.defineProperty(this, "segments", { value: v, enumerable: true, configurable: true }); return v; } });
  return f;
}
/* the full context a decision is made in. `extra` wins over everything (an explicit country,
   service, amount…); `buyer: false` evaluates the platform alone (cached settings, menus). */
function context(tenantId, extra) {
  const x = extra || {};
  const base = platformFacts(tenantId);
  const ctx = { ...base };
  if (x.buyer !== false) {
    const b = buyerFacts(tenantId);
    for (const k of Object.keys(b)) Object.defineProperty(ctx, k, Object.getOwnPropertyDescriptor(b, k));
  }
  for (const [k, v] of Object.entries(x)) if (k !== "buyer" && v !== undefined && v !== null && v !== "") ctx[k] = k === "country" || k === "currency" ? S(v).toUpperCase() : v;
  if (!ctx.at) ctx.at = new Date().toISOString();
  return ctx;
}

/* ---------------- matching ---------------- */
function groupCountries(key) { const g = list("countryGroups").find(x => keyOf(x).toUpperCase() === S(key).toUpperCase()); return g ? arr(g.countries).map(c => S(c).toUpperCase()) : null; }
/* "yes" · "no" · "maybe" (the context does not know this fact) */
function dimMatch(d, want, fact) {
  if (!want.length) return "yes";
  if (fact === undefined || fact === null || fact === "" || (Array.isArray(fact) && d.match === "any" && fact === undefined)) return "maybe";
  const W = want.map(S);
  switch (d.match) {
    case "any": { const have = arr(fact).map(S); return W.some(w => have.includes(w)) ? "yes" : "no"; }
    case "prefix": { const f = S(fact).toUpperCase(); return W.some(w => f === w.toUpperCase() || f.startsWith(w.toUpperCase() + ".") || f.startsWith(w.toUpperCase() + "-")) ? "yes" : "no"; }
    case "country": { const f = S(fact).toUpperCase(); return W.some(w => w.toUpperCase() === f || (groupCountries(w) || []).includes(f)) ? "yes" : "no"; }
    default: return W.includes(S(fact)) || W.map(w => w.toLowerCase()).includes(S(fact).toLowerCase()) ? "yes" : "no";
  }
}
function amountIn(sc, ctx) {
  if (sc.min_amount == null && sc.max_amount == null) return "yes";
  if (ctx.amount == null || ctx.amount === "") return "maybe";
  let amt = Number(ctx.amount);
  const cur = S(sc.amount_currency).toUpperCase();
  if (cur && ctx.currency && cur !== S(ctx.currency).toUpperCase()) { try { amt = amt * registry().fxTo(ctx.currency, cur); } catch (e) { } }
  if (sc.min_amount != null && sc.min_amount !== "" && amt < Number(sc.min_amount)) return "no";
  if (sc.max_amount != null && sc.max_amount !== "" && amt > Number(sc.max_amount)) return "no";
  return "yes";
}
function windowIn(sc, ctx) {
  const at = S(ctx.at).slice(0, 19);
  if (sc.from && at < S(sc.from).slice(0, 19)) return "no";
  if (sc.to && at > (S(sc.to).length <= 10 ? S(sc.to) + "T23:59:59" : S(sc.to).slice(0, 19))) return "no";
  return "yes";
}
function match(rule, ctx) {
  const sc = rule.scope || {};
  let out = "yes";
  const fold = r => { if (r === "no") out = "no"; else if (r === "maybe" && out === "yes") out = "maybe"; };
  /* a fact is read only when the rule constrains it — segments cost a lookup */
  for (const d of list("ruleDimensions")) { const want = arr(sc[d.key]); if (!want.length) continue; fold(dimMatch(d, want, ctx[d.fact])); if (out === "no") return out; }
  fold(amountIn(sc, ctx)); if (out === "no") return out;
  fold(windowIn(sc, ctx));
  return out;
}
function specificity(rule) {
  const sc = rule.scope || {};
  let n = rule.subject === "*" ? 0 : 100;
  for (const d of list("ruleDimensions")) if (arr(sc[d.key]).length) n++;
  if (sc.min_amount != null || sc.max_amount != null) n++;
  if (sc.from || sc.to) n++;
  return n;
}
function describe(rule) {
  const sc = rule.scope || {}; const bits = [];
  for (const d of list("ruleDimensions")) if (arr(sc[d.key]).length) bits.push(d.name.toLowerCase() + " " + arr(sc[d.key]).join("/"));
  if (sc.min_amount != null && sc.min_amount !== "") bits.push("amount ≥ " + sc.min_amount + (sc.amount_currency ? " " + sc.amount_currency : ""));
  if (sc.max_amount != null && sc.max_amount !== "") bits.push("amount ≤ " + sc.max_amount + (sc.amount_currency ? " " + sc.amount_currency : ""));
  if (sc.from) bits.push("from " + sc.from); if (sc.to) bits.push("until " + sc.to);
  return "#" + rule.id + " " + rule.effect + " " + (rule.subject === "*" ? "every " + rule.subject_type : rule.subject) + (bits.length ? " · " + bits.join(" · ") : " · everywhere");
}

/* one layer's verdict for one subject */
function layer(rules, type, id, ctx, label) {
  const mine = rules.filter(r => r.subject_type === type && (r.subject === "*" || r.subject === S(id)));
  if (!mine.length) return { ok: true, open: true, matched: [], params: {}, priority: 0, reasons: [] };
  const scored = mine.map(r => ({ r, m: match(r, ctx), sp: specificity(r) }));
  const yes = scored.filter(x => x.m === "yes").sort((a, b) => b.sp - a.sp || (a.r.effect === "deny" ? -1 : 1) - (b.r.effect === "deny" ? -1 : 1));
  const params = {}; let priority = 0;
  for (const x of yes.slice().reverse()) if (x.r.effect !== "deny") { Object.assign(params, x.r.params || {}); }
  for (const x of yes) if (x.r.effect === "prefer") priority = Math.max(priority, x.r.priority || 0);
  if (yes.length) {
    const top = yes[0];
    if (top.r.effect === "deny") return { ok: false, matched: [top.r.id], params: {}, priority: 0, reasons: [label + " " + describe(top.r)] };
    return { ok: true, matched: yes.filter(x => x.r.effect !== "deny").map(x => x.r.id), params, priority, reasons: [label + " " + describe(top.r)] };
  }
  const allows = scored.filter(x => x.r.effect !== "deny");
  if (!allows.length) return { ok: true, open: true, matched: [], params: {}, priority: 0, reasons: [] };
  const maybe = allows.filter(x => x.m === "maybe");
  if (maybe.length) return { ok: true, conditional: true, matched: maybe.map(x => x.r.id), params: {}, priority: 0, reasons: [label + " depends on " + describe(maybe[0].r)] };
  return { ok: false, matched: [], params: {}, priority: 0, reasons: [label + " outside every allow rule: " + allows.map(x => describe(x.r)).join("; ")] };
}
/* THE question every engine asks */
const OPEN = Object.freeze({ ok: true, verdict: "open", reasons: [], matched: [], params: {}, priority: 0 });
function decide(type, id, ctx) {
  const c = ctx || {};
  const all = rows();
  if (!all.length || !all.some(r => r.subject_type === type)) return { ...OPEN, params: {} };
  const plat = layer(all.filter(r => r.tenant_id == null), type, id, c, "platform rule");
  const own = c.tenant_id ? layer(all.filter(r => r.tenant_id === Number(c.tenant_id)), type, id, c, "this platform's rule") : { ok: true, open: true, matched: [], params: {}, priority: 0, reasons: [] };
  const ok = plat.ok && own.ok;
  return {
    ok, verdict: !ok ? "blocked" : (plat.conditional || own.conditional) ? "conditional" : (plat.open && own.open) ? "open" : "allowed",
    reasons: [...plat.reasons, ...own.reasons], matched: [...plat.matched, ...own.matched],
    params: ok ? { ...plat.params, ...own.params } : {}, priority: ok ? Math.max(plat.priority, own.priority) : 0
  };
}
function permits(type, id, ctx) { return decide(type, id, ctx).ok; }
/* keep the permitted items, preferred first (a stable sort keeps the engine's own order) */
function filter(type, items, ctx, idOf) {
  const f = idOf || (x => x.id);
  return (items || []).map((it, i) => ({ it, i, d: decide(type, f(it), ctx) })).filter(x => x.d.ok)
    .sort((a, b) => b.d.priority - a.d.priority || a.i - b.i).map(x => ({ it: x.it, d: x.d }));
}
/* throw when a service (and the instruments it uses) is not permitted — the engines call this
   at their entry points, so the API wrappers report the reason as a 4xx */
function guard(tenantId, req) {
  const r = req || {};
  const ctx = context(tenantId, { service: r.service, amount: r.amount, currency: r.currency, country: r.country, region: r.region, channel: r.channel });
  const checks = [["service", r.service], ["gateway", r.gateway], ["method", r.method], ["bank", r.bank]];
  for (const [type, id] of checks) {
    if (!id) continue;
    const d = decide(type, id, ctx);
    if (!d.ok) { const e = new Error(label(type) + " " + id + " is not available here — " + d.reasons.join("; ")); e.status = 403; e.rule = d; throw e; }
  }
  return ctx;
}
function label(type) { const t = list("ruleSubjectTypes").find(x => keyOf(x) === type); return t ? t.name : type; }
/* does any capability/module rule depend on the buyer? (lets the hot paths skip the work) */
function contextualCaps() { rows(); return !!(CACHE && CACHE.contextualCaps); }

/* a bank from its key, or recognised from an IFSC / SWIFT code */
function bankOf(input) {
  const i = input || {};
  const banks = list("banks");
  if (i.bank) { const k = S(i.bank).toLowerCase(); const b = banks.find(x => keyOf(x).toLowerCase() === k); if (b) return keyOf(b); }
  const ifsc = S(i.ifsc).toUpperCase().slice(0, 4), swift = S(i.swift || i.bic).toUpperCase().slice(0, 4);
  const b = banks.find(x => (ifsc && S(x.ifsc).toUpperCase() === ifsc) || (swift && S(x.swift).toUpperCase() === swift));
  return b ? keyOf(b) : (i.bank ? S(i.bank).toLowerCase() : null);
}

/* ---------------- what a rule can name (for the console) ---------------- */
const IDENT = /^[A-Za-z_][A-Za-z0-9_]{0,63}$/;
function subjects(type, tenantId) {
  const t = list("ruleSubjectTypes").find(x => keyOf(x) === type);
  if (!t) return [];
  const src = S(t.source);
  const D = db();
  const tid = tenantId ? Number(tenantId) : null;
  try {
    if (src.startsWith("entity:")) {
      const key = src.slice(7);
      const ent = require("./entity.js");
      const def = ent.allEntities(tid)[key];
      if (!def) return [];
      const pk = def.pk || "id";
      const lab = ["name", "label", "title", "code", "key"].find(f => (def.fields || []).some(x => x.key === f)) || pk;
      const rowsOut = tid ? ent.listEntities(tid, key, { limit: 500 }) : ent.listEntitiesGlobal(key, { limit: 500 });
      const list0 = Array.isArray(rowsOut) ? rowsOut : (rowsOut && (rowsOut.rows || rowsOut.items)) || [];
      return list0.map(r => ({ key: S(r[pk]), name: S(r[lab] != null ? r[lab] : r[pk]) + (!tid && r.tenant_id ? " · platform " + r.tenant_id : "") }));
    }
    if (src.startsWith("rows:")) {
      const [table, idc, labc] = src.slice(5).split(":");
      if (![table, idc, labc || idc].every(x => IDENT.test(S(x)))) return [];
      const cols = D.all("PRAGMA table_info(" + table + ")").map(c => c.name);
      if (!cols.includes(idc) || !cols.includes(labc || idc)) return [];
      const scoped = cols.includes("tenant_id") && tid;
      return D.all("SELECT " + idc + " k, " + (labc || idc) + " n" + (cols.includes("tenant_id") ? ", tenant_id t" : "") + " FROM " + table + (scoped ? " WHERE tenant_id IN (?, 0)" : "") + " ORDER BY " + idc + " LIMIT 1000", ...(scoped ? [tid] : []))
        .map(r => ({ key: S(r.k), name: S(r.n) + (!tid && r.t ? " · platform " + r.t : "") }));
    }
    if (src === "loginMethods") return [{ key: "password", name: "Email / Password" }].concat(require("./identity.js").getProviderTypes().filter(x => x && x.key && x.key !== "password").map(x => ({ key: S(x.key), name: S(x.label || x.key) })));
    if (src.startsWith("providers:")) {
      const kind = src.slice(10);
      return D.all("SELECT id, name, emoji FROM provider_defs WHERE kind=? ORDER BY position, name", kind).map(p => ({ key: p.id, name: (p.emoji ? p.emoji + " " : "") + p.name }));
    }
    if (src.startsWith("list:")) return list(src.slice(5)).map(x => ({ key: keyOf(x), name: S((x && (x.name || x.label)) || keyOf(x)) + (x && x.country ? " · " + x.country : "") }));
    /* every method a payment provider declares, plus the registered method vocabularies
       (offline methods, and methods an engine settles itself — a ride paid in cash) */
    if (src === "methods") {
      const names = new Map();
      for (const x of list("paymentMethods").concat(list("offlinePaymentMethods"))) if (keyOf(x)) names.set(keyOf(x), S(x.name || keyOf(x)));
      for (const p of D.all("SELECT methods FROM provider_defs WHERE kind='payment'")) for (const m of J(p.methods, [])) if (!names.has(S(m))) names.set(S(m), S(m).replace(/_/g, " "));
      return [...names].sort((a, b) => a[0].localeCompare(b[0])).map(([k, n]) => ({ key: k, name: n }));
    }
    if (src === "taxModes") return D.all("SELECT key, label FROM tax_modes ORDER BY position").map(x => ({ key: x.key, name: x.label }));
    if (src === "capabilities") return require("./capabilities.js").catalog().map(c => ({ key: c.key, name: (c.icon ? c.icon + " " : "") + c.label, group: c.domain }));
    if (src === "modules") { const set = new Set(); for (const m of D.all("SELECT manifest FROM modules")) for (const c of arr(J(m.manifest, {}).capabilities)) set.add(S(c)); return [...set].sort().map(k => ({ key: k, name: k })); }
  } catch (e) { }
  return [];
}
function dimensionOptions(d) {
  const src = S(d.options);
  const D = db();
  try {
    if (src === "kinds") return registry().kinds().map(k => ({ key: k.key, name: k.name }));
    if (src === "platforms") return D.all("SELECT slug, name FROM tenants ORDER BY id").map(t => ({ key: t.slug, name: t.name }));
    if (src === "countries") return list("countryGroups").map(g => ({ key: keyOf(g), name: "🌐 " + (g.name || keyOf(g)) })).concat(registry().countries().map(c => ({ key: c.code, name: c.name })));
    if (src === "currencies") return registry().currencies().map(c => ({ key: c.code, name: c.code + " · " + c.name }));
    if (src === "subdivisions") return [];
    if (src === "segments") {
      const seen = new Set(); const out = [];
      for (const x of list("segments").concat(list("goipAudiences"))) { const k = keyOf(x); if (!k || seen.has(k)) continue; seen.add(k); out.push({ key: k, name: S(x.name || k) }); }
      return out;
    }
    if (src.startsWith("list:")) return list(src.slice(5)).map(x => ({ key: keyOf(x), name: S((x && (x.name || x.label)) || keyOf(x)) }));
  } catch (e) { }
  return [];
}
function schema() {
  return {
    effects: EFFECTS,
    subjectTypes: list("ruleSubjectTypes").map(t => ({ key: keyOf(t), name: S(t.name || keyOf(t)), source: t.source })),
    dimensions: list("ruleDimensions").map(d => ({ key: d.key, name: d.name, fact: d.fact, match: d.match, options: dimensionOptions(d) }))
  };
}

/* ---------------- authoring ---------------- */
function validate(input, tenantId) {
  const i = input || {};
  const types = list("ruleSubjectTypes").map(keyOf);
  const type = S(i.subject_type);
  if (!types.includes(type)) return { error: "Unknown subject type: " + type + " (one of " + types.join(", ") + ")" };
  const subject = S(i.subject || "*").trim() || "*";
  if (subject !== "*" && !subjects(type).some(x => x.key === subject)) return { error: "Unknown " + label(type).toLowerCase() + ": " + subject };
  const effect = S(i.effect || "allow");
  if (!EFFECTS.includes(effect)) return { error: "Effect must be one of " + EFFECTS.join(", ") };
  const raw = i.scope && typeof i.scope === "object" ? i.scope : {};
  const scope = {};
  for (const d of list("ruleDimensions")) {
    const v = arr(raw[d.key]).map(x => S(x).trim()).filter(Boolean);
    if (!v.length) continue;
    const opts = dimensionOptions(d);
    if (opts.length) { const bad = v.filter(x => !opts.some(o => S(o.key).toLowerCase() === x.toLowerCase())); if (bad.length) return { error: d.name + ": unknown " + bad.join(", ") }; }
    scope[d.key] = [...new Set(v.map(x => { const o = opts.find(o => S(o.key).toLowerCase() === x.toLowerCase()); return o ? o.key : (d.fact === "country" || d.fact === "currency" || d.fact === "region" ? x.toUpperCase() : x); }))];
  }
  /* a platform narrows itself only: its rules never reach another platform or kind */
  if (tenantId) { delete scope.platforms; delete scope.kinds; }
  for (const k of ["min_amount", "max_amount"]) if (raw[k] != null && raw[k] !== "") { const n = Number(raw[k]); if (!isFinite(n) || n < 0) return { error: k + " must be a non-negative number" }; scope[k] = n; }
  if (scope.min_amount != null && scope.max_amount != null && scope.min_amount > scope.max_amount) return { error: "min_amount is above max_amount" };
  if (raw.amount_currency) { const c = S(raw.amount_currency).toUpperCase(); if (!registry().currency(c)) return { error: "Unknown currency " + c }; scope.amount_currency = c; }
  for (const k of ["from", "to"]) if (raw[k]) { const v = S(raw[k]).trim(); if (isNaN(Date.parse(v))) return { error: k + " is not a date" }; scope[k] = v; }
  const params = i.params && typeof i.params === "object" && !Array.isArray(i.params) ? i.params : {};
  return { rule: { subject_type: type, subject, effect, priority: Math.max(-1000, Math.min(1000, Number(i.priority) || 0)), scope, params, note: S(i.note).slice(0, 300), active: i.active === false || i.active === 0 ? 0 : 1 } };
}
function listRules(tenantId, opts) {
  const o = opts || {};
  const D = db();
  const where = tenantId === null || tenantId === undefined ? "tenant_id IS NULL" : "tenant_id=?";
  const args = tenantId === null || tenantId === undefined ? [] : [Number(tenantId)];
  let out = D.all("SELECT * FROM applicability_rules WHERE " + where + " ORDER BY subject_type, subject, id", ...args).map(norm);
  if (o.subject_type) out = out.filter(r => r.subject_type === o.subject_type);
  return out.map(r => ({ ...r, summary: describe(r) }));
}
function save(input, tenantId, actor) {
  const v = validate(input, tenantId);
  if (v.error) return v;
  const r = v.rule; const D = db();
  const tid = tenantId ? Number(tenantId) : null;
  if (input.id) {
    const ex = D.get("SELECT * FROM applicability_rules WHERE id=?", Number(input.id));
    if (!ex || (ex.tenant_id == null ? null : Number(ex.tenant_id)) !== tid) return { error: "No such rule", status: 404 };
    D.run("UPDATE applicability_rules SET subject_type=?, subject=?, effect=?, priority=?, scope=?, params=?, note=?, active=?, updated_at=datetime('now') WHERE id=?",
      r.subject_type, r.subject, r.effect, r.priority, JSON.stringify(r.scope), JSON.stringify(r.params), r.note, r.active, ex.id);
    bust(); return { rule: get(ex.id) };
  }
  const x = D.run("INSERT INTO applicability_rules(tenant_id,subject_type,subject,effect,priority,scope,params,note,active,created_by) VALUES(?,?,?,?,?,?,?,?,?,?)",
    tid, r.subject_type, r.subject, r.effect, r.priority, JSON.stringify(r.scope), JSON.stringify(r.params), r.note, r.active, actor ? S(actor) : null);
  bust(); return { rule: get(Number(x.lastInsertRowid)) };
}
function get(id) { const r = db().get("SELECT * FROM applicability_rules WHERE id=?", Number(id)); return r ? { ...norm(r), summary: describe(norm(r)) } : null; }
function remove(id, tenantId) {
  const D = db(); const ex = D.get("SELECT tenant_id FROM applicability_rules WHERE id=?", Number(id));
  const tid = tenantId ? Number(tenantId) : null;
  if (!ex || (ex.tenant_id == null ? null : Number(ex.tenant_id)) !== tid) return { error: "No such rule", status: 404 };
  D.run("DELETE FROM applicability_rules WHERE id=?", Number(id)); bust(); return { ok: true };
}
/* every subject of a type, decided in one context — the console's "why" view */
function explain(type, ctx) {
  return subjects(type).map(x => { const d = decide(type, x.key, ctx); return { key: x.key, name: x.name, ok: d.ok, verdict: d.verdict, reasons: d.reasons, priority: d.priority, params: d.params }; });
}
/* segment memberships a platform assigns by hand (computed audiences need no rows) */
function members(tenantId) { try { return db().all("SELECT * FROM segment_members WHERE tenant_id=? ORDER BY segment, owner", Number(tenantId)); } catch (e) { return []; } }
function addMember(tenantId, owner, segment) {
  const seg = S(segment).trim();
  if (!dimensionOptions({ options: "segments" }).some(o => o.key === seg)) return { error: "Unknown segment " + seg };
  if (!S(owner)) return { error: "owner required" };
  db().run("INSERT OR IGNORE INTO segment_members(tenant_id,owner,segment) VALUES(?,?,?)", Number(tenantId), S(owner), seg);
  return { ok: true };
}
function removeMember(tenantId, id) { db().run("DELETE FROM segment_members WHERE tenant_id=? AND id=?", Number(tenantId), Number(id)); return { ok: true }; }

module.exports = {
  LISTS, EFFECTS, run, current, context, platformFacts, segmentsOf, decide, permits, filter, guard, contextualCaps, bankOf,
  subjects, schema, dimensionOptions, validate, listRules, save, get, remove, explain, members, addMember, removeMember, bust, describe
};
