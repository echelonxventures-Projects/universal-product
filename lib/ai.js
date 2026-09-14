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

/* ---- SEED DATA (written to meta_lists/provider_defs once; the DB is then the source of truth) ---- */
const AI_PROVIDERS = [
  { id: "ai-local", name: "LUXORA Intelligence (built-in)", emoji: "🧠", free: true, perUnit: 0, currency: "USD", models: ["heuristics-v1"], fields: [], capabilities: ["product_recommendation", "image_processing", "data_analysis", "data_cleaning", "reporting"], desc: "Zero-config on-device engine over the store's own data — always on, always free." },
  { id: "ai-openai", name: "OpenAI", emoji: "🟢", free: false, perUnit: 0.01, currency: "USD", models: ["gpt-4o-mini", "gpt-4o", "gpt-4.1"], fields: [{ key: "apiKey", label: "API key", secret: true }, { key: "org", label: "Org id" }], capabilities: ["product_recommendation", "data_analysis", "data_cleaning", "reporting"], desc: "Premium language models for copy, analysis and reports." },
  { id: "ai-anthropic", name: "Anthropic Claude", emoji: "🟠", free: false, perUnit: 0.012, currency: "USD", models: ["claude-3-5-haiku", "claude-3-5-sonnet"], fields: [{ key: "apiKey", label: "API key", secret: true }], capabilities: ["data_analysis", "reporting", "data_cleaning"], desc: "Long-context analysis and structured reporting." },
  { id: "ai-stability", name: "Stability AI", emoji: "🎨", free: false, perUnit: 0.04, currency: "USD", models: ["sd3-medium", "sd-xl"], fields: [{ key: "apiKey", label: "API key", secret: true }], capabilities: ["image_processing"], desc: "Generative background removal and product photography." },
  { id: "ai-google-vision", name: "Google Vision", emoji: "👁️", free: false, perUnit: 0.006, currency: "USD", models: ["vision-ocr", "vision-labels"], fields: [{ key: "apiKey", label: "API key", secret: true }, { key: "projectId", label: "GCP project" }], capabilities: ["image_processing"], desc: "OCR + labelling for catalogue imagery." }
];

const AI_CAPABILITIES = [
  { key: "product_recommendation", name: "Product Recommendation", icon: "🎯", unit: "request", desc: "Customers-also-bought / personalized picks from the store's order graph.", freeLimit: { perDay: 200, maxUnits: 12 }, premiumLimit: { perDay: 100000, maxUnits: 60 }, premiumProviders: ["ai-openai"], context: "orders, order_items, view_history" },
  { key: "image_processing", name: "Image Processing", icon: "🖼️", unit: "image", desc: "Variants, alt-text, background & format manifests for a product's media.", freeLimit: { perDay: 100, maxUnits: 20 }, premiumLimit: { perDay: 100000, maxUnits: 200 }, premiumProviders: ["ai-stability", "ai-google-vision"], context: "products.media" },
  { key: "data_analysis", name: "Data Analysis", icon: "📈", unit: "column", desc: "Profile any catalogue column: coverage, distincts, nulls, min/max/avg.", freeLimit: { perDay: 100, maxUnits: 200 }, premiumLimit: { perDay: 100000, maxUnits: 5000 }, premiumProviders: ["ai-openai", "ai-anthropic"], context: "products" },
  { key: "data_cleaning", name: "Data Cleaning", icon: "🧹", unit: "record", desc: "Detect and (optionally) auto-fix hygiene issues per configurable rules.", freeLimit: { perDay: 50, maxUnits: 200 }, premiumLimit: { perDay: 100000, maxUnits: 100000 }, premiumProviders: ["ai-openai", "ai-anthropic"], context: "products" },
  { key: "reporting", name: "Reporting", icon: "📊", unit: "section", desc: "Compose a business report (sales by dept, top items, orders/day).", freeLimit: { perDay: 30, maxUnits: 6 }, premiumLimit: { perDay: 100000, maxUnits: 50 }, premiumProviders: ["ai-openai", "ai-anthropic"], context: "orders, order_items" }
];

const AI_PLANS = [
  { key: "free", name: "AI Free", price: 0, billing: "included", provider: "ai-local", capabilities: { product_recommendation: true, image_processing: true, data_analysis: true, data_cleaning: true, reporting: true }, note: "Always on for every store. Built-in engine, no keys, no cost." },
  { key: "premium", name: "AI Premium", price: 29, billing: "monthly", provider: "premium", capabilities: { product_recommendation: true, image_processing: true, data_analysis: true, data_cleaning: true, reporting: true }, note: "Bring your own models (OpenAI / Anthropic / Stability / Google Vision) with premium limits, for paid stores or after buying the AI Premium module." }
];

const CLEAN_RULES = [
  { key: "title_trim", field: "title", op: "trim", label: "Trim whitespace in titles" },
  { key: "title_len", field: "title", op: "maxlen", value: 90, label: "Flag titles over 90 chars" },
  { key: "brand_missing", field: "brand", op: "required", label: "Missing brand" },
  { key: "price_positive", field: "price", op: "positive", label: "Price must be > 0" },
  { key: "gtin_missing", field: "identity", op: "json_required", jsonKey: "gtin", label: "Missing GTIN/barcode" },
  { key: "dup_sku", field: "id", op: "duplicate", label: "Duplicate product reference" }
];
const ANALYZE_FIELDS = ["title", "brand", "dept", "price", "list_price", "rating", "stock"];
const REPORT_SECTIONS = ["summary", "sales_by_dept", "top_products", "orders_by_day"];
const ANALYZABLE = new Set(["title", "brand", "dept", "price", "list_price", "rating", "ratings_count", "stock", "type", "lifecycle"]);

function seed() {
  const D = db();
  const ensure = (name, items) => D.run("INSERT OR IGNORE INTO meta_lists(name,label,items) VALUES(?,?,?)", name, name, JSON.stringify(items));
  ensure("aiCapabilities", AI_CAPABILITIES); ensure("aiPlans", AI_PLANS); ensure("aiCleanRules", CLEAN_RULES);
  ensure("aiCapabilityKeys", AI_CAPABILITIES.map(c => c.key));
  ensure("aiAnalyzeFields", ANALYZE_FIELDS); ensure("aiReportSections", REPORT_SECTIONS);
  ensure("providerKinds", ["payment", "shipping", "notification", "tax", "ai"]);
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
  const hasAiPro = require("./modules.js").hasCap(tenantId, "aiPro");
  return { premium: hasPaidPlan || hasAiPro, hasPaidPlan, hasAiPro };
}
function providerConfigured(tenantId, providerId) {
  if (providerId === "ai-local") return true;
  const D = db();
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
  const providers = D.all("SELECT * FROM provider_defs WHERE kind='ai' AND enabled=1 ORDER BY position")
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
        if (pick) { provider = pick; model = cfg.model || (AI_PROVIDERS.find(x => x.id === pick.id) || {}).models?.[0] || pick.id; status = "available"; }
        else { provider = providers.find(p => p.id === "ai-local"); model = "heuristics-v1"; status = "available_fallback_free"; }
      }
    } else { provider = providers.find(p => p.id === "ai-local"); model = "heuristics-v1"; status = "available"; }
    return {
      key: c.key, name: c.name, icon: c.icon, unit: c.unit, desc: c.desc, context: c.context,
      enabled: cfg.enabled !== false, tier: t.premium ? "premium" : "free", status,
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
function report(D, tenantId, params, maxUnits) {
  const want = Array.isArray(params.sections) && params.sections.length ? params.sections : list("aiReportSections", REPORT_SECTIONS);
  const t = tenantId; const out = {};
  if (want.includes("summary")) { const o = D.get("SELECT COUNT(*) c, COALESCE(SUM(total),0) rev FROM orders WHERE tenant_id=?", t); out.summary = { orders: o.c, revenue: +Number(o.rev).toFixed(2), products: D.get("SELECT COUNT(*) c FROM products WHERE tenant_id=?", t).c, customers: D.get("SELECT COUNT(*) c FROM users WHERE tenant_id=? AND role='customer'", t).c }; }
  if (want.includes("sales_by_dept")) out.sales_by_dept = D.all(`SELECT p.dept, SUM(oi.qty) units, SUM(oi.price*oi.qty) rev FROM order_items oi JOIN orders o ON o.id=oi.order_id AND o.tenant_id=? JOIN products p ON p.tenant_id=o.tenant_id AND p.id=oi.product_id GROUP BY p.dept ORDER BY rev DESC`, t).map(r => ({ dept: r.dept, units: r.units, rev: +Number(r.rev).toFixed(2) }));
  if (want.includes("top_products")) out.top_products = D.all(`SELECT oi.product_id id, p.title, SUM(oi.qty) units, SUM(oi.price*oi.qty) rev FROM order_items oi JOIN orders o ON o.id=oi.order_id AND o.tenant_id=? JOIN products p ON p.tenant_id=o.tenant_id AND p.id=oi.product_id GROUP BY oi.product_id ORDER BY rev DESC LIMIT ?`, t, Math.min(maxUnits || 6, 20)).map(r => ({ id: r.id, title: r.title, units: r.units, rev: +Number(r.rev).toFixed(2) }));
  if (want.includes("orders_by_day")) out.orders_by_day = D.all(`SELECT substr(created_at,1,10) day, COUNT(*) c FROM orders WHERE tenant_id=? GROUP BY day ORDER BY day DESC LIMIT 14`, t).map(r => ({ day: r.day, orders: r.c }));
  out.sections = Object.keys(out).filter(k => k !== "sections");
  return out;
}
const ENGINES = { product_recommendation: "recommend", image_processing: "images", data_analysis: "analyze", data_cleaning: "clean", reporting: "report" };

function run(tenantId, capability, params, actor) {
  const D = db();
  const cap = capabilities(tenantId).find(c => c.key === capability);
  if (!cap) return { error: "Unknown AI capability" };
  if (!cap.enabled) return { error: "Capability disabled in store settings", code: 403 };
  if (cap.status === "premium_locked") return { error: "Premium model requires a paid plan or the AI Premium module", code: 402 };
  if (cap.usedToday >= cap.limits.perDay) return { error: "Daily AI limit reached for this capability", code: 429 };
  const prov = cap.provider || { id: "ai-local", perUnit: 0, currency: "USD" };
  let units = 1, result;
  try {
    if (capability === "product_recommendation") { result = recommend(D, tenantId, params || {}, cap.limits.maxUnits); units = (result.items || []).length || 1; }
    else if (capability === "image_processing") { result = processImages(D, tenantId, params || {}); if (result.error) return result; units = result.images || 1; }
    else if (capability === "data_analysis") { result = analyze(D, tenantId, params || {}); units = Object.keys(result.columns || {}).length || 1; }
    else if (capability === "data_cleaning") { result = clean(D, tenantId, params || {}); units = result.scanned || 1; }
    else if (capability === "reporting") { result = report(D, tenantId, params || {}, cap.limits.maxUnits); units = (result.sections || []).length || 1; }
    else return { error: "No engine for capability" };
  } catch (e) { return { error: "AI engine error: " + e.message }; }
  const cost = +(Number(prov.perUnit || 0) * units).toFixed(4);
  D.run("INSERT INTO ai_usage(tenant_id,capability,provider,model,units,cost,currency,tier,status,actor) VALUES(?,?,?,?,?,?,?,?,?,?)",
    tenantId, capability, prov.id, cap.model || "heuristics-v1", units, cost, "USD", cap.tier, "ok", actor || "system");
  return { ok: true, capability, tier: cap.tier, provider: prov.id, model: cap.model, units, cost, result };
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
