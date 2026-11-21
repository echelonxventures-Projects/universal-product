/* LUXORA Platform — the AI assistant, one engine for every app: a profile (lib/seed/assistant.json,
   the store's own copy in its settings) says which knowledge collections it answers from (lib/rag.js),
   which platform tools it may call (the MCP tools, lib/mcp.js, called in-process), who a person is
   handed to, and what it must always say.

   With the store's Claude credentials (Store console → AI gateways, stored encrypted) and the
   official SDK installed (@anthropic-ai/sdk, loaded only here), it asks Claude, which calls the
   tools and answers from the knowledge it was given. Without them it answers from the approved
   knowledge alone — the entries themselves, never invented text — and says so. Every answer is
   kept (assistant_turns) so a person can rate or correct it; in a learning collection a
   correction becomes a proposed revision of the knowledge used. */
"use strict";
const SEED = require("./seed/assistant.json");
const db = () => require("./db.js");
const rag = () => require("./rag.js");
const mcp = () => require("./mcp.js");
const J = (v, d) => { try { return v == null || v === "" ? d : JSON.parse(v); } catch (e) { return d; } };
function httpErr(m, status) { const e = new Error(m); e.status = status; return e; }

/* ---------- profiles: the template, overlaid by the store's saved copy ---------- */
/* the store's own copies live in its settings (the assistant block, saved through Rules' settings writer) */
const settings = () => require("./settings.js");
function storeProfiles(tenantId) { return ((settings().load(Number(tenantId)) || {}).assistant || {}).profiles || {}; }
function profile(tenantId, key) {
  const base = SEED.PROFILES.find(p => p.key === key) || null, own = storeProfiles(tenantId)[key] || null;
  if (!base && !own) return null;
  return Object.assign({ model: SEED.MODEL, effort: SEED.DEFAULT_EFFORT, collections: [], tools: [], disclaimer: "", handoff: null }, base || {}, own || {}, { key });
}
function profiles(tenantId) {
  const keys = [...new Set(SEED.PROFILES.map(p => p.key).concat(Object.keys(storeProfiles(tenantId))))];
  return keys.map(k => profile(tenantId, k));
}
function saveProfile(tenantId, key, p) {
  const k = String(key || "").trim().toLowerCase(); if (!/^[a-z][a-z0-9_]{0,40}$/.test(k)) throw httpErr("A profile key is a-z, 0-9 and _", 400);
  const x = p || {}, toolNames = mcp().TOOLS.map(t => t.name);
  const badTool = [].concat(x.tools || []).find(t => !toolNames.includes(t)); if (badTool) throw httpErr("Unknown tool: " + badTool, 400);
  if (x.effort != null && !SEED.EFFORTS.includes(x.effort)) throw httpErr("effort is " + SEED.EFFORTS.join(", "), 400);
  const keep = ["label", "persona", "collections", "tools", "disclaimer", "handoff", "model", "effort"];
  const cur = storeProfiles(tenantId); cur[k] = Object.assign({}, cur[k] || {}, Object.fromEntries(keep.filter(f => x[f] !== undefined).map(f => [f, x[f]])));
  settings().save(Number(tenantId), { assistant: Object.assign({}, (settings().load(Number(tenantId)) || {}).assistant || {}, { profiles: cur }) });
  try { settings().bust(Number(tenantId)); } catch (e) { }
  return profile(tenantId, k);
}

/* ---------- Claude: the store's credentials, the official SDK ---------- */
let clientFactory = null;     /* tests inject a stand-in; nothing is billed */
function __setClient(f) { clientFactory = f; }
function claudeKey(tenantId) {
  const row = db().get("SELECT config FROM tenant_gateways WHERE tenant_id=? AND provider_id='ai:ai-anthropic' AND enabled=1", Number(tenantId));
  if (!row) return null;
  const cfg = require("./security.js").unsealConfig(Number(tenantId), "ai:ai-anthropic", row.config || "{}");
  return cfg.apiKey || null;
}
function client(tenantId) {
  if (clientFactory) return { client: clientFactory(tenantId) };
  if (process.env.LX_OFFLINE === "1") return { why: "outbound calls are offline" };
  const key = claudeKey(tenantId);
  if (!key) return { why: "no Claude API key is set for this store (Store console → AI gateways → Anthropic Claude)" };
  let Anthropic; try { Anthropic = require("@anthropic-ai/sdk"); } catch (e) { return { why: "the Anthropic SDK is not installed on this server (npm install @anthropic-ai/sdk)" }; }
  const C = Anthropic.default || Anthropic;
  return { client: new C({ apiKey: key }) };
}

/* ---------- the chart's tags: what a person's chart is about, for retrieval ---------- */
function chartTags(chart) {
  if (!chart) return [];
  const t = [];
  for (const b of chart.bodies || []) t.push("planet:" + b.body, "sign:" + b.sign, "house:" + b.house, "nakshatra:" + b.nakshatra, b.body + ":" + b.sign, b.body + ":house_" + b.house);
  if (chart.ascendant) t.push("ascendant:" + chart.ascendant.sign);
  const now = new Date().toISOString().slice(0, 10), md = ((chart.dasha || {}).periods || []).find(p => p.start <= now && p.end > now);
  if (md) t.push("dasha:" + md.lord);
  return [...new Set(t)];
}

/* ---------- asking ---------- */
async function ask(tenantId, profileKey, input, actor) {
  const p = profile(tenantId, profileKey); if (!p) throw httpErr("No assistant profile " + profileKey, 404);
  const x = input || {}, question = String(x.message || "").trim().slice(0, 4000);
  if (!question) throw httpErr("message is required", 400);
  const ctx = { tenantId: Number(tenantId), roleKey: actor && actor.roleKey, platform: !!(actor && actor.platform) };
  /* a birth given with the question: its chart is computed by the platform's own tool, and its tags
     guide which knowledge is retrieved */
  let chart = null;
  if (x.birth && p.tools.includes("astro_chart")) { const r = mcp().call(ctx, "astro_chart", x.birth); if (!r.isError) chart = r.structuredContent.chart; }
  const tags = chartTags(chart);
  const sources = [];
  for (const c of p.collections) for (const e of rag().search(tenantId, c, { q: question, limit: 6 }).concat(tags.length ? rag().search(tenantId, c, { tags, limit: 6 }) : []))
    if (!sources.some(s => s.id === e.id)) sources.push(Object.assign({ collection: c }, e));
  const top = sources.slice(0, 10);
  const conversation = String(x.conversation || "").slice(0, 64) || "c_" + require("crypto").randomBytes(8).toString("hex");
  const handoff = p.handoff ? { label: p.handoff.label, path: p.handoff.path } : null;
  const c = client(tenantId);
  let answer, mode, used = [], model = null;
  if (!c.client) {
    /* no model: the approved entries themselves, never generated text */
    mode = SEED.ANSWER_MODES.knowledge;
    answer = top.length ? top.slice(0, 3).map(e => "• " + e.title + ": " + e.body).join("\n\n") : "I don't have approved knowledge that answers this yet.";
    answer += "\n\n(Answered from the store's approved knowledge only — " + c.why + ".)";
  } else {
    mode = SEED.ANSWER_MODES.model; model = p.model;
    const toolDefs = mcp().tools(ctx).filter(t => p.tools.includes(t.name)).map(t => ({ name: t.name, description: t.description, input_schema: t.inputSchema }));
    const knowledge = top.length ? top.map(e => "[" + e.id + "] " + e.title + "\n" + e.body).join("\n\n") : "(none)";
    const system = [{ type: "text", text: p.persona + "\n\n" + SEED.RULES + (p.disclaimer ? "\n\nAlways end with: " + p.disclaimer : ""), cache_control: { type: "ephemeral" } }];
    const history = (Array.isArray(x.history) ? x.history : []).slice(-12).filter(m => m && (m.role === "user" || m.role === "assistant") && typeof m.content === "string").map(m => ({ role: m.role, content: m.content.slice(0, 4000) }));
    const messages = history.concat([{ role: "user", content: "Store knowledge (approved entries; cite by [id]):\n" + knowledge + (chart ? "\n\nThe person's chart (computed by the platform):\n" + JSON.stringify({ ascendant: chart.ascendant, bodies: chart.bodies, settings: chart.settings }) : "") + "\n\nQuestion: " + question }]);
    let res;
    for (let round = 0; round <= SEED.MAX_TOOL_ROUNDS; round++) {
      res = await c.client.beta.messages.create({
        model: p.model, max_tokens: 16000, betas: ["server-side-fallback-2026-07-01"], fallbacks: "default",
        thinking: { type: "adaptive" }, output_config: { effort: p.effort || SEED.DEFAULT_EFFORT },
        system, tools: toolDefs, messages
      });
      if (res.stop_reason !== "tool_use") break;
      messages.push({ role: "assistant", content: res.content });
      const results = res.content.filter(b => b.type === "tool_use").map(b => {
        used.push(b.name);
        const r = p.tools.includes(b.name) ? mcp().call(ctx, b.name, b.input) : { isError: true, content: [{ type: "text", text: "Tool not available to this assistant" }] };
        return { type: "tool_result", tool_use_id: b.id, content: r.content, is_error: !!r.isError };
      });
      messages.push({ role: "user", content: results });
    }
    if (res.stop_reason === "refusal") answer = "I can't help with that here." + (handoff ? " " + handoff.label + " instead." : "");
    else answer = res.content.filter(b => b.type === "text").map(b => b.text).join("").trim() || "I don't have an answer to that.";
    if (res.stop_reason === "max_tokens") answer += "\n\n(The answer was cut short.)";
    model = res.model || p.model;
  }
  const t = db().run("INSERT INTO assistant_turns(tenant_id,conversation,app,question,answer,sources,tools,model,mode,owner) VALUES(?,?,?,?,?,?,?,?,?,?)",
    Number(tenantId), conversation, p.key, question, answer, JSON.stringify(top.map(e => e.id)), JSON.stringify(used), model, mode, actor && actor.owner ? String(actor.owner) : null);
  return { turn: Number(t.lastInsertRowid), conversation, answer, mode, model, sources: top.map(e => ({ id: e.id, title: e.title, collection: e.collection })), tools: used,
    disclaimer: p.disclaimer || null, handoff };
}

/* a person's rating or correction of an answer: kept with the answer; in a learning collection a
   correction becomes a proposed revision of the knowledge the answer used */
function rate(tenantId, turnId, f, actor) {
  const t = db().get("SELECT * FROM assistant_turns WHERE id=? AND tenant_id=?", Number(turnId), Number(tenantId)); if (!t) throw httpErr("Not found", 404);
  const ids = J(t.sources, []) || [];
  const first = ids.length ? ids[0] : null;
  return rag().feedback(tenantId, { entry_id: first, answer_ref: "turn:" + t.id, rating: f && f.rating, correction: f && f.correction }, actor);
}

/* the AI drafts a knowledge entry for an expert's review (allowed only where the collection's mode lets the AI draft) */
async function draft(tenantId, collectionKey, brief, actor) {
  const c = rag().collection(tenantId, collectionKey); if (!c.exists) throw httpErr("No collection " + collectionKey, 404);
  const mode = rag().MODES.find(m => m.key === c.mode); if (!mode.aiDrafts) throw httpErr("This collection is in " + mode.label + " mode: the AI does not draft entries", 409);
  const b = brief || {}, title = String(b.title || "").trim(); if (!title) throw httpErr("title is required", 400);
  const cl = client(tenantId); if (!cl.client) throw httpErr("The AI cannot draft: " + cl.why, 409);
  const res = await cl.client.beta.messages.create({
    model: b.model || SEED.MODEL, max_tokens: 4000, betas: ["server-side-fallback-2026-07-01"], fallbacks: "default",
    thinking: { type: "adaptive" }, output_config: { effort: SEED.DEFAULT_EFFORT },
    system: "You draft knowledge-base entries for a domain expert to review. Write a clear, accurate, plain-language entry of 80 to 200 words. State the traditional or commonly held view as such, avoid certainty, and add nothing that would harm a reader who acts on it. Reply with the entry text only.",
    messages: [{ role: "user", content: "Collection: " + c.label + "\nEntry title: " + title + (b.notes ? "\nExpert's notes: " + String(b.notes).slice(0, 2000) : "") }]
  });
  if (res.stop_reason === "refusal") throw httpErr("The AI declined to draft this entry", 409);
  const body = res.content.filter(x => x.type === "text").map(x => x.text).join("").trim();
  return rag().addEntry(tenantId, c.key, { title, body, tags: b.tags, source: "ai", confidence: b.confidence }, actor);
}

module.exports = { PROFILES: SEED.PROFILES, profile, profiles, saveProfile, ask, rate, draft, chartTags, __setClient };
