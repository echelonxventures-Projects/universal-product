/* LUXORA Platform — AI capability layer (a PRODUCT, not code).
   Everything (providers, capabilities, plans, per-capability model/limits/price) is DATA:
   providers live in provider_defs(kind='ai') + provider_availability; capabilities, plans and
   cleaning rules live in meta_lists (aiCapabilities / aiPlans / aiCleanRules …); the per-tenant
   model, limits and on/off live in the `ai` settings block. Free tier is ON by default (1st
   priority) via the built-in local engine; premium models are gated by REAL billing state
   (paid subscription plan or the `aiPro` capability) AND by provider credentials being configured.
   Nothing is hard-coded to a model, provider, price, limit or field — those come from registries. */
"use strict";

let _db = null;
const db = () => _db || (_db = require("./db.js"));
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };
const list = (name, dflt) => J((db().get("SELECT items i FROM meta_lists WHERE name=?", name) || {}).i, dflt);

/* ---- SEED DATA (lib/seed/ai.json — written to meta_lists/provider_defs once; the DB is then the
   source of truth). No provider, model or plan is named in code. ---- */
const SEED_AI = require("./seed/ai.json");
const { AI_PROVIDERS, AI_CAPABILITIES, AI_PLANS, CLEAN_RULES, ANALYZE_FIELDS, REPORT_SECTIONS } = SEED_AI;
const ANALYZABLE = new Set(["title", "brand", "dept", "price", "list_price", "rating", "ratings_count", "stock", "type", "lifecycle"]);

function seed() {
  const D = db();
  const ensure = (name, items) => D.run("INSERT OR IGNORE INTO meta_lists(name,label,items) VALUES(?,?,?)", name, name, JSON.stringify(items));
  ensure("aiCapabilities", AI_CAPABILITIES);
  /* a field the seed newly declares (engine, units) reaches an existing install additively —
     an operator's own values are never overwritten */
  require("./registry.js").addFields("aiCapabilities", AI_CAPABILITIES, ["engine", "units", "params"]); ensure("aiPlans", AI_PLANS); ensure("aiCleanRules", CLEAN_RULES);
  ensure("aiCapabilityKeys", AI_CAPABILITIES.map(c => c.key));
  /* the models each provider offers, as a registry list — a model is added (or ruled out
     for a country, segment or capability) as data, never by editing AI_PROVIDERS */
  ensure("aiModels", AI_PROVIDERS.flatMap(p => (p.models || []).map(m => ({ key: m, name: m, provider: p.id, currency: p.currency }))));
  ensure("aiAnalyzeFields", ANALYZE_FIELDS); ensure("aiReportSections", REPORT_SECTIONS);
  ensure("providerKinds", ["payment", "shipping", "notification", "tax", "ai", "marketing"]);
  for (const p of AI_PROVIDERS) {
    D.run(`INSERT INTO provider_defs(id,kind,name,emoji,description,methods,fee_pct,fee_fixed,fields,base_fee,position,enabled)
           VALUES(?,?,?,?,?,?,?,?,?,?,?,1) ON CONFLICT(id,kind) DO NOTHING`,
      p.id, "ai", p.name, p.emoji, p.desc, JSON.stringify(p.capabilities), 0, p.perUnit, JSON.stringify(p.fields), p.perUnit, 600 + AI_PROVIDERS.indexOf(p));
    for (const c of D.all("SELECT code FROM countries")) D.run("INSERT OR IGNORE INTO provider_availability(provider_id,country_code) VALUES(?,?)", p.id, c.code);
  }
}

function tierOf(tenantId) {
  const D = db();
  const plan = D.get("SELECT p.price_month price FROM subscriptions s JOIN plans p ON p.id=s.plan_id WHERE s.tenant_id=? AND s.status='active' ORDER BY s.id DESC", tenantId);
  const hasPaidPlan = !!(plan && Number(plan.price) > 0);
  const hasAiPro = require("./gates.js").on(tenantId, "ai.premium");
  return { premium: hasPaidPlan || hasAiPro, hasPaidPlan, hasAiPro };
}
/* the always-available engine is DATA: the provider of the free AI plan (aiPlans, price 0),
   running the first model the aiModels registry lists for it, priced in that model's (or the
   provider's) currency — no provider or model is named in code */
function fallback() {
  const plans = list("aiPlans", AI_PLANS);
  const free = plans.find(p => Number(p.price) === 0) || plans[0] || {};
  const pid = free.provider;
  const models = list("aiModels", []).filter(m => m && m.provider === pid);
  const def = AI_PROVIDERS.find(p => p.id === pid) || {};
  return { id: pid, model: (models[0] && models[0].key) || (def.models || [])[0] || pid, currency: (models[0] && models[0].currency) || def.currency || free.currency || null };
}
function providerConfigured(tenantId, providerId) {
  const D = db();
  /* a provider that declares no credential fields needs no configuration */
  const pdef = D.get("SELECT fields FROM provider_defs WHERE id=? AND kind='ai'", providerId);
  if (pdef && !J(pdef.fields, []).length) return true;
  const row = D.get("SELECT config FROM tenant_gateways WHERE tenant_id=? AND provider_id=?", tenantId, "ai:" + providerId);
  if (!row) return false;
  const cfg = J(row.config, {});
  return Object.keys(cfg).length > 0;
}

function usageSince(tenantId, sinceExpr) {
  const D = db(); const out = {};
  try { for (const r of D.all(`SELECT capability, COUNT(*) n FROM ai_usage WHERE tenant_id=? AND ${sinceExpr} GROUP BY capability`, tenantId)) out[r.capability] = r.n; } catch (e) { }
  return out;
}

function capabilities(tenantId) {
  const D = db(); const t = tierOf(tenantId);
  const caps = list("aiCapabilities", AI_CAPABILITIES);
  const aiCfg = require("./settings.js").load(tenantId).ai || {};
  const rules = require("./rules.js"); const rctx = rules.at("ai.providers", tenantId);
  const fb = fallback();
  const providers = D.all("SELECT * FROM provider_defs WHERE kind='ai' AND enabled=1 ORDER BY position")
    .filter(p => rules.permitsAt("ai.providers", p.id, rctx))
    .map(p => ({ id: p.id, name: p.name, emoji: p.emoji, perUnit: Number(p.fee_fixed), methods: J(p.methods, []), fields: J(p.fields, []) }));
  const usedToday = usageSince(tenantId, "date('now')");
  return caps.map(c => {
    const cfg = aiCfg[c.key] || {};
    const limits = (t.premium ? c.premiumLimit : c.freeLimit) || c.freeLimit;
    const used = usedToday[c.key] || 0;
    const wantPremium = cfg.premium === true;
    let provider, model, status;
    if (wantPremium) {
      if (!t.premium) { provider = null; model = null; status = "premium_locked"; }
      else {
        const pick = providers.find(p => p.id === cfg.provider && (c.premiumProviders || []).includes(p.id) && providerConfigured(tenantId, p.id))
          || providers.find(p => (c.premiumProviders || []).includes(p.id) && providerConfigured(tenantId, p.id));
        /* the provider's models come from the aiModels registry; the applicability rules
           decide which of them this context may use (the configured one if it may) */
        const models = list("aiModels", []).filter(x => x && x.provider === (pick && pick.id)).map(x => String(x.key)).filter(k => rules.permitsAt("ai.models", k, rctx));
        const want = cfg.model && models.includes(cfg.model) ? cfg.model : models[0];
        if (pick && want) { provider = pick; model = want; status = "available"; }
        else { provider = providers.find(p => p.id === fb.id); model = fb.model; status = "available_fallback_free"; }
      }
    } else { provider = providers.find(p => p.id === fb.id); model = fb.model; status = "available"; }
    /* a capability a rule denies, or one left with no provider a rule permits, is blocked */
    if (!rules.permitsAt("ai.capabilities", c.key, rctx) || !provider) status = "blocked_by_rule";
    return {
      key: c.key, name: c.name, icon: c.icon, unit: c.unit, desc: c.desc, context: c.context,
      enabled: cfg.enabled !== false, tier: t.premium ? "premium" : "free", premium: !!t.premium, params: c.params || [], status,
      provider: provider ? { id: provider.id, name: provider.name, emoji: provider.emoji, perUnit: provider.perUnit } : null,
      model, wantPremium, limits: { perDay: limits.perDay, maxUnits: limits.maxUnits }, usedToday: used, remaining: Math.max(0, limits.perDay - used)
    };
  });
}

function planInfo(tenantId) { const t = tierOf(tenantId); const plans = list("aiPlans", AI_PLANS); return { tier: t.premium ? "premium" : "free", hasPaidPlan: t.hasPaidPlan, hasAiPro: t.hasAiPro, plans }; }

/* ================= REAL engines computed from the store's own data ================= */
function recommend(D, tenantId, params, maxUnits) {
  const id = String(params.product_id || "");
  let rows = id ? D.all(`SELECT p.id, p.title, p.brand, p.dept, p.price, p.rating, COUNT(*) w FROM order_items oi
      JOIN order_items oi2 ON oi.order_id=oi2.order_id
      JOIN orders o ON o.id=oi.order_id AND o.tenant_id=?
      JOIN products p ON p.tenant_id=o.tenant_id AND p.id=oi2.product_id
      WHERE oi.product_id=? AND oi2.product_id!=? AND p.lifecycle='published'
      GROUP BY p.id ORDER BY w DESC LIMIT ?`, tenantId, id, id, maxUnits) : [];
  if (rows.length < 3) {
    const cur = id && D.get("SELECT dept FROM products WHERE tenant_id=? AND id=?", tenantId, id);
    rows = D.all("SELECT id,title,brand,dept,price,rating,0 w FROM products WHERE tenant_id=? AND dept=? AND id!=? AND lifecycle='published' ORDER BY ratings_count DESC LIMIT ?", tenantId, cur ? cur.dept : "", id, maxUnits);
  }
  return { mode: id ? "co_purchase" : "catalog", based_on: id || "all", items: rows.map(r => ({ id: r.id, title: r.title, brand: r.brand, dept: r.dept, price: r.price, rating: r.rating, score: r.w })) };
}
function processImages(D, tenantId, params) {
  const id = String(params.product_id || "");
  const p = D.get("SELECT * FROM products WHERE tenant_id=? AND id=?", tenantId, id);
  if (!p) return { error: "Unknown product" };
  const media = J(p.media, []) || [];
  const sizes = Array.isArray(params.sizes) && params.sizes.length ? params.sizes.slice(0, 6) : [64, 256, 1024];
  const manifest = media.map((m, i) => ({
    index: i, kind: m.kind || "image", label: m.label || ("view " + (i + 1)),
    alt: `${p.title} — ${m.label || m.kind || "image"} by ${p.brand}`.replace(/\s+/g, " ").trim(),
    background: p.hue != null ? `hsl(${p.hue} 30% 95%)` : "#ffffff",
    variants: sizes.map(s => ({ w: s, h: s, name: `${p.id}-${m.kind || "img"}-${s}.webp`, format: "webp" })),
    labels: (p.keywords || "").split(",").map(x => x.trim()).filter(Boolean).slice(0, 8)
  }));
  return { product_id: p.id, title: p.title, images: manifest.length, manifest };
}
function analyze(D, tenantId, params) {
  const defaults = list("aiAnalyzeFields", ANALYZE_FIELDS);
  const cols = Array.isArray(params.columns) && params.columns.length ? params.columns : defaults;
  const total = D.get("SELECT COUNT(*) c FROM products WHERE tenant_id=?", tenantId).c;
  const out = {};
  for (const c of cols) {
    if (!ANALYZABLE.has(c)) { out[c] = { skipped: "field not analyzable" }; continue; }
    const rows = D.all(`SELECT ${c} v FROM products WHERE tenant_id=?`, tenantId);
    const vals = rows.map(r => r.v); const nn = vals.filter(v => v != null && v !== "");
    const numeric = ["price", "list_price", "rating", "ratings_count", "stock"].includes(c);
    const e = { field: c, coverage: total ? +(nn.length / total * 100).toFixed(1) : 0, nulls: total - nn.length, distinct: new Set(nn.map(String)).size };
    if (numeric && nn.length) { const nums = nn.map(Number).filter(n => !isNaN(n)); if (nums.length) { e.min = Math.min(...nums); e.max = Math.max(...nums); e.avg = +(nums.reduce((a, b) => a + b, 0) / nums.length).toFixed(2); } }
    out[c] = e;
  }
  return { population: total, columns: out };
}
function clean(D, tenantId, params) {
  const rules = list("aiCleanRules", CLEAN_RULES);
  const apply = !!params.apply;
  const rows = D.all("SELECT id,title,brand,price,identity FROM products WHERE tenant_id=?", tenantId);
  const issues = []; let fixed = 0; const seen = {};
  for (const r of rows) for (const rule of rules) {
    let bad = false, fix = null; const raw = r[rule.field];
    if (rule.op === "trim") { if (typeof raw === "string" && raw !== raw.trim()) { bad = true; fix = raw.trim(); } }
    else if (rule.op === "maxlen") bad = typeof raw === "string" && raw.length > (rule.value || 90);
    else if (rule.op === "required") bad = raw == null || raw === "";
    else if (rule.op === "positive") bad = !(Number(raw) > 0);
    else if (rule.op === "json_required") { const idn = J(raw, {}) || {}; bad = !idn[rule.jsonKey]; }
    else if (rule.op === "duplicate") { if (seen[r.id]) bad = true; else seen[r.id] = 1; }
    if (bad) { issues.push({ product_id: r.id, rule: rule.key, label: rule.label, field: rule.field }); if (apply && fix != null) { try { D.run(`UPDATE products SET ${rule.field}=? WHERE tenant_id=? AND id=?`, fix, tenantId, r.id); fixed++; } catch (e) { } } }
  }
  return { scanned: rows.length, issues: issues.length, byRule: issues.reduce((o, i) => (o[i.rule] = (o[i.rule] || 0) + 1, o), {}), applied: apply, fixed, sample: issues.slice(0, 40) };
}
/* each report section is an implementation chosen by the section row's `impl` (its key when
   the row is a plain name), so a section is added, reordered or retired as data */
const SECTION_IMPL = {
  summary: (D, t) => { const o = D.get("SELECT COUNT(*) c, COALESCE(SUM(total),0) rev FROM orders WHERE tenant_id=?", t); return { orders: o.c, revenue: +Number(o.rev).toFixed(2), products: D.get("SELECT COUNT(*) c FROM products WHERE tenant_id=?", t).c, customers: D.get("SELECT COUNT(*) c FROM users WHERE tenant_id=? AND role='customer'", t).c }; },
  sales_by_dept: (D, t) => D.all(`SELECT p.dept, SUM(oi.qty) units, SUM(oi.price*oi.qty) rev FROM order_items oi JOIN orders o ON o.id=oi.order_id AND o.tenant_id=? JOIN products p ON p.tenant_id=o.tenant_id AND p.id=oi.product_id GROUP BY p.dept ORDER BY rev DESC`, t).map(r => ({ dept: r.dept, units: r.units, rev: +Number(r.rev).toFixed(2) })),
  top_products: (D, t, maxUnits) => D.all(`SELECT oi.product_id id, p.title, SUM(oi.qty) units, SUM(oi.price*oi.qty) rev FROM order_items oi JOIN orders o ON o.id=oi.order_id AND o.tenant_id=? JOIN products p ON p.tenant_id=o.tenant_id AND p.id=oi.product_id GROUP BY oi.product_id, p.title ORDER BY rev DESC LIMIT ?`, t, Math.min(maxUnits || 6, 20)).map(r => ({ id: r.id, title: r.title, units: r.units, rev: +Number(r.rev).toFixed(2) })),
  orders_by_day: (D, t) => D.all(`SELECT substr(created_at,1,10) AS day, COUNT(*) c FROM orders WHERE tenant_id=? GROUP BY day ORDER BY day DESC LIMIT 14`, t).map(r => ({ day: r.day, orders: r.c }))
};
function report(D, tenantId, params, maxUnits) {
  const rows = list("aiReportSections", REPORT_SECTIONS).map(r => (typeof r === "string" ? { key: r } : r));
  const wanted = Array.isArray(params.sections) && params.sections.length ? params.sections.map(String) : rows.map(r => r.key);
  const out = {};
  for (const k of wanted) { const row = rows.find(r => r.key === k) || { key: k }; const fn = SECTION_IMPL[row.impl || row.key]; if (fn) out[k] = fn(D, tenantId, maxUnits); }
  out.sections = Object.keys(out).filter(k => k !== "sections");
  return out;
}
/* the engines, by the name a capability row declares (`engine`), and how a row counts its
   billable units (`units`: { count: <array field> } · { keys: <object field> } · { field: <number> }) */
const ENGINE_IMPL = {
  recommend: (D, t, p, cap) => recommend(D, t, p, cap.limits.maxUnits),
  images: (D, t, p) => processImages(D, t, p),
  analyze: (D, t, p) => analyze(D, t, p),
  clean: (D, t, p) => clean(D, t, p),
  report: (D, t, p, cap) => report(D, t, p, cap.limits.maxUnits)
};
const ENGINES = Object.fromEntries(AI_CAPABILITIES.map(c => [c.key, c.engine]));
function unitsOf(spec, result) {
  const u = spec || {}; const r = result || {};
  const n = u.count ? (r[u.count] || []).length : u.keys ? Object.keys(r[u.keys] || {}).length : u.field ? Number(r[u.field]) : 1;
  return n || 1;
}

function run(tenantId, capability, params, actor) {
  const D = db();
  const cap = capabilities(tenantId).find(c => c.key === capability);
  if (!cap) return { error: "Unknown AI capability" };
  if (!cap.enabled) return { error: "Capability disabled in store settings", code: 403 };
  if (cap.status === "premium_locked") return { error: "Premium model requires a paid plan or the AI Premium module", code: 402 };
  if (cap.status === "blocked_by_rule") { const rules = require("./rules.js"); return { error: "This AI capability is not available here — " + (rules.decideAt("ai.capabilities", capability, rules.at("ai.capabilities", tenantId)).reasons.join("; ") || "no permitted AI provider"), code: 403 }; }
  if (cap.usedToday >= cap.limits.perDay) return { error: "Daily AI limit reached for this capability", code: 429 };
  const fb = fallback();
  const prov = cap.provider || { id: fb.id, perUnit: 0 };
  let units = 1, result;
  try {
    /* the capability row names its engine and how it counts units — no capability is named here */
    const row = list("aiCapabilities", AI_CAPABILITIES).find(c => c.key === capability) || {};
    const impl = ENGINE_IMPL[row.engine];
    if (!impl) return { error: "No engine for capability" };
    result = impl(D, tenantId, params || {}, cap);
    if (result && result.error) return result;
    units = unitsOf(row.units, result);
  } catch (e) { return { error: "AI engine error: " + e.message }; }
  const cost = +(Number(prov.perUnit || 0) * units).toFixed(4);
  D.run("INSERT INTO ai_usage(tenant_id,capability,provider,model,units,cost,currency,tier,status,actor) VALUES(?,?,?,?,?,?,?,?,?,?)",
    tenantId, capability, prov.id, cap.model || fb.model, units, cost, prov.currency || fb.currency, cap.tier, "ok", actor || "system");
  return { ok: true, capability, tier: cap.tier, provider: prov.id, model: cap.model, units, cost, currency: prov.currency || fb.currency, result };
}

function usage(tenantId) {
  const D = db();
  const rows = D.all(`SELECT capability, provider, tier, SUM(units) units, SUM(cost) cost, COUNT(*) calls, MAX(created_at) last FROM ai_usage WHERE tenant_id=? GROUP BY capability, provider, tier ORDER BY calls DESC`, tenantId);
  const total = D.get(`SELECT COALESCE(SUM(cost),0) c, COUNT(*) calls FROM ai_usage WHERE tenant_id=?`, tenantId);
  return { rows, totalCost: +Number(total.c).toFixed(2), totalCalls: total.calls };
}
function tasks(tenantId) { const D = db(); return D.all("SELECT * FROM ai_tasks WHERE tenant_id=? ORDER BY id DESC LIMIT 200", tenantId).map(r => ({ ...r, params: J(r.params, {}), result: J(r.result, null) })); }
function createTask(tenantId, capability, params, actor) { const D = db(); return Number(D.run("INSERT INTO ai_tasks(tenant_id,capability,status,params,actor) VALUES(?,?,?,?,?)", tenantId, capability, "queued", JSON.stringify(params || {}), actor || "system").lastInsertRowid); }
function processTask(taskId) {
  const D = db(); const t = D.get("SELECT * FROM ai_tasks WHERE id=?", taskId); if (!t) return { error: "No task" };
  if (t.status !== "queued") return { ok: true, skipped: t.status };
  D.run("UPDATE ai_tasks SET status='running' WHERE id=?", taskId);
  const out = run(t.tenant_id, t.capability, J(t.params, {}), t.actor);
  D.run("UPDATE ai_tasks SET status=?, result=?, cost=? WHERE id=?", out.error ? "failed" : "done", JSON.stringify(out.error ? { error: out.error } : out.result), out.cost || 0, taskId);
  return out;
}
function runPending(tenantId) { const D = db(); for (const t of D.all("SELECT id FROM ai_tasks WHERE tenant_id=? AND status='queued'", tenantId)) processTask(t.id); return tasks(tenantId); }

module.exports = { AI_PROVIDERS, AI_CAPABILITIES, AI_PLANS, CLEAN_RULES, ANALYZE_FIELDS, REPORT_SECTIONS, ENGINES, seed, tierOf, capabilities, planInfo, run, usage, providerConfigured, tasks, createTask, processTask, runPending, J };
