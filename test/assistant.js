/* LUXORA Platform — the MCP server (lib/mcp.js) and the AI assistant (lib/assistant.js), reusable by
   every app. In-process with a stand-in for Claude (nothing billed, nothing leaves the machine):
   the request the assistant sends, the tool loop through the platform's MCP tools, the knowledge
   it answers from, refusals. Over HTTP: MCP JSON-RPC, role-scoped MCP keys, the knowledge routes,
   and the assistant answering from approved knowledge alone when the store has no Claude key. */
"use strict";
const path = require("path"), fs = require("fs"), { spawn } = require("child_process");
const DB = path.join(__dirname, "assistant.db");
const clean = () => { for (const x of ["", "-wal", "-shm"]) { try { fs.rmSync(DB + x, { force: true }); } catch (e) { } } };
clean();
process.env.LX_DB = DB;
const quiet = console.log; console.log = () => { };
const db = require("../lib/db.js");
console.log = quiet;
const rag = require("../lib/rag.js"), mcp = require("../lib/mcp.js"), asst = require("../lib/assistant.js"), caps = require("../lib/capabilities.js");
let passed = 0, failed = 0;
const ok = (c, n, x) => { c ? (passed++, console.log("  ✓ " + n)) : (failed++, console.log("  ✗ " + n + (x !== undefined ? " → " + JSON.stringify(x).slice(0, 400) : ""))); };
const T = db.masterTenant().id;
const birth = { date: "1990-03-15", time: "11:00", timeZone: "Asia/Kolkata", latitude: 28.6139, longitude: 77.2090 };

(async () => {
  try {
    caps.enable(T, "astro_engine", {}); caps.enable(T, "ai_assistant", {});
    rag.saveCollection(T, "astro", { label: "Astrology", mode: "self_learning", expertRoles: ["owner"] }, ["owner", "support"]);
    const owner = { roleKey: "owner", name: "Owner" };
    const e1 = rag.addEntry(T, "astro", { title: "Moon in Swati", body: "A Swati Moon is traditionally linked with independence and a love of travel.", tags: ["nakshatra:swati", "planet:moon"] }, owner);

    console.log("▸ MCP — THE PLATFORM'S TOOLS, BY AUDIENCE AND ROLE");
    const shopper = { tenantId: T }, staff = { tenantId: T, roleKey: "owner" };
    const init = mcp.handle(shopper, { jsonrpc: "2.0", id: 1, method: "initialize", params: { protocolVersion: "2025-06-18", capabilities: {}, clientInfo: { name: "t", version: "1" } } });
    ok(init.result.protocolVersion === "2025-06-18" && init.result.capabilities.tools && init.result.serverInfo.name, "initialize answers with the client's protocol version and the tools capability", init.result);
    ok(mcp.handle(shopper, { jsonrpc: "2.0", method: "notifications/initialized" }) === null, "a notification gets no answer");
    const listS = mcp.handle(shopper, { jsonrpc: "2.0", id: 2, method: "tools/list" }).result.tools.map(t => t.name);
    const listT = mcp.handle(staff, { jsonrpc: "2.0", id: 3, method: "tools/list" }).result.tools.map(t => t.name);
    ok(listS.includes("astro_chart") && listS.includes("knowledge_search") && !listS.includes("records_list"), "a shopper sees the shopper tools, not the staff ones", listS);
    ok(listT.includes("records_list"), "a staff role also sees the staff tools");
    const ch = mcp.handle(shopper, { jsonrpc: "2.0", id: 4, method: "tools/call", params: { name: "astro_chart", arguments: birth } }).result;
    ok(!ch.isError && ch.structuredContent.chart.bodies.length === 9, "tools/call computes a chart with the store's settings");
    const badArgs = mcp.handle(shopper, { jsonrpc: "2.0", id: 5, method: "tools/call", params: { name: "astro_chart", arguments: { date: "1990-03-15" } } }).result;
    ok(badArgs.isError && /missing/.test(badArgs.content[0].text), "arguments are checked against the tool's schema", badArgs);
    const hidden = mcp.handle(shopper, { jsonrpc: "2.0", id: 6, method: "tools/call", params: { name: "records_list", arguments: { type: "supplier" } } }).result;
    ok(hidden.isError, "a shopper cannot call a staff tool");
    const ks = mcp.handle(shopper, { jsonrpc: "2.0", id: 7, method: "tools/call", params: { name: "knowledge_search", arguments: { collection: "astro", tags: ["nakshatra:swati"] } } }).result;
    ok(!ks.isError && ks.structuredContent.entries[0].id === e1.id, "knowledge_search returns approved entries");
    ok(mcp.handle(shopper, { jsonrpc: "2.0", id: 8, method: "nope" }).error.code === -32601, "an unknown method is a JSON-RPC error");
    caps.disable(T, "astro_engine");
    ok(!mcp.handle(shopper, { jsonrpc: "2.0", id: 9, method: "tools/list" }).result.tools.some(t => t.name === "astro_chart"), "a tool whose capability the store has off is not offered");
    caps.enable(T, "astro_engine", {});

    console.log("▸ THE ASSISTANT WITH CLAUDE (A STAND-IN; NOTHING BILLED)");
    const sent = [];
    asst.__setClient(() => ({ beta: { messages: { create: async req => {
      sent.push(JSON.parse(JSON.stringify(req)));
      if (sent.length === 1) return { model: req.model, stop_reason: "tool_use", content: [{ type: "text", text: "Let me look at the chart." }, { type: "tool_use", id: "tu_1", name: "astro_chart", input: birth }] };
      return { model: req.model, stop_reason: "end_turn", content: [{ type: "text", text: "Your Moon is in Swati [" + e1.id + "]: independence and travel. Astrology is offered for guidance and reflection, not as medical, legal or financial advice." }] };
    } } } }));
    const a = await asst.ask(T, "astro", { message: "What does my Moon say about me?", birth }, { owner: "t1:s:x" });
    const r0 = sent[0];
    ok(r0.model === "claude-opus-5-5" && r0.fallbacks === "default" && r0.betas.includes("server-side-fallback-2026-07-01"), "Claude Opus 5.5 is asked, with refusal fallbacks on", { model: r0.model, betas: r0.betas });
    ok(r0.thinking.type === "adaptive" && r0.output_config.effort === "medium" && r0.max_tokens >= 16000, "adaptive thinking and the profile's effort", { thinking: r0.thinking, oc: r0.output_config });
    ok(r0.system[0].cache_control && /astrology guide/.test(r0.system[0].text), "the profile's persona is the cached system prompt");
    ok(r0.tools.map(t => t.name).sort().join() === "astro_chart,astro_match,astro_panchang,knowledge_search", "only the profile's tools are offered, from the MCP declarations", r0.tools.map(t => t.name));
    ok(/Moon in Swati/.test(r0.messages[r0.messages.length - 1].content), "the approved knowledge for the person's chart is given to the model");
    const r1 = sent[1], tr = r1.messages[r1.messages.length - 1].content[0];
    ok(tr.type === "tool_result" && tr.tool_use_id === "tu_1" && !tr.is_error && /bodies/.test(JSON.stringify(tr.content)), "the tool call is answered by the platform's MCP tool, in the same loop");
    ok(a.mode === "ai" && /Swati/.test(a.answer) && a.tools.includes("astro_chart") && a.sources.some(s => s.id === e1.id), "the answer names its sources and the tools used", a);
    ok(a.handoff && a.handoff.label === "Talk to an astrologer" && a.disclaimer, "the hand-off to a human astrologer and the disclaimer come with it");

    console.log("▸ REFUSALS, AND A CORRECTION THAT TEACHES THE KNOWLEDGE BASE");
    asst.__setClient(() => ({ beta: { messages: { create: async () => ({ model: "claude-opus-5-5", stop_reason: "refusal", stop_details: { type: "refusal" }, content: [] }) } } }));
    const rf = await asst.ask(T, "astro", { message: "something declined" }, {});
    ok(/can't help/.test(rf.answer) && /astrologer/.test(rf.answer), "a refusal is answered plainly, with the hand-off", rf.answer);
    const rate = asst.rate(T, a.turn, { rating: 2, correction: "Swati also points to diplomacy." }, { name: "a customer" });
    ok(rate.proposed && rag.proposals(T, "astro").some(p => p.source === "learned"), "in a self-learning collection a correction becomes a proposal for the expert", rate);

    console.log("▸ THE AI DRAFTS ONLY WHERE THE MODE ALLOWS");
    asst.__setClient(() => ({ beta: { messages: { create: async () => ({ model: "claude-opus-5-5", stop_reason: "end_turn", content: [{ type: "text", text: "Jupiter in the ninth house is traditionally read as favouring learning and travel." }] }) } } }));
    const d = await asst.draft(T, "astro", { title: "Jupiter in the 9th house", tags: ["planet:jupiter", "house:9"] }, owner);
    ok(d.status === "review" && d.source === "ai", "an AI draft waits for the expert", d);
    rag.saveCollection(T, "astro", { mode: "expert" }, ["owner", "support"]);
    let refused = false; try { await asst.draft(T, "astro", { title: "x" }, owner); } catch (e) { refused = /does not draft/.test(e.message); }
    ok(refused, "in Expert mode the AI may not draft");

    console.log("▸ PROFILES ARE THE STORE'S OWN");
    const saved = asst.saveProfile(T, "astro", { effort: "high", tools: ["astro_chart", "knowledge_search"] });
    ok(saved.effort === "high" && saved.tools.length === 2 && /astrology guide/.test(saved.persona), "a store changes its profile; the rest comes from the template");
    let badTool = false; try { asst.saveProfile(T, "astro", { tools: ["format_disk"] }); } catch (e) { badTool = /Unknown tool/.test(e.message); }
    ok(badTool, "a profile can only name the platform's declared tools");
    const app = asst.saveProfile(T, "legal", { label: "Legal help", persona: "You answer legal questions from the store's knowledge only.", collections: ["legal"], tools: ["knowledge_search"] });
    ok(asst.profiles(T).some(p => p.key === "legal") && app.model === "claude-opus-5-5", "any app gets an assistant by adding a profile — no code");
    asst.__setClient(null);
  } catch (e) { failed++; console.log("  ✗ harness error: " + (e && e.stack || e)); }

  /* ---- over HTTP ---- */
  const PORT = 8844, BASE = "http://localhost:" + PORT;
  const srv = spawn(process.execPath, [path.join(__dirname, "..", "server.js")], { env: { ...process.env, PORT, LX_DB: DB, LX_LOG: "" }, stdio: ["ignore", "ignore", "pipe"] });
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const alive = async () => { try { return (await fetch(BASE + "/healthz")).ok; } catch (e) { return false; } };
  try {
    for (let i = 0; i < 240 && !(await alive()); i++) await sleep(500);
    console.log("▸ OVER HTTP");
    const jar = new Map();
    const f = async (p, m, b, h0) => { const h = Object.assign({ Cookie: [...jar].map(x => x.join("=")).join("; ") }, h0 || {}); if (m && m !== "GET") Object.assign(h, { "x-csrf": jar.get("azc") || "", "Content-Type": "application/json", Origin: BASE });
      const r = await fetch(BASE + p, { method: m || "GET", headers: h, body: b ? JSON.stringify(b) : undefined }); (r.headers.getSetCookie() || []).forEach(k => { const kv = k.split(";")[0], i = kv.indexOf("="); jar.set(kv.slice(0, i), kv.slice(i + 1)); }); return { st: r.status, b: await r.json().catch(() => ({})) }; };
    await f("/api/session");
    const ask0 = await f("/api/assistant/astro/ask", "POST", { message: "Tell me about a Swati Moon" });
    ok(ask0.st === 200 && ask0.b.mode === "knowledge_only" && /Moon in Swati/.test(ask0.b.answer) && /no Claude API key/.test(ask0.b.answer), "with no Claude key the assistant answers from approved knowledge only, and says why", ask0.b);
    ok((await f("/api/kb/astro/search?tags=nakshatra:swati")).b.entries.length >= 1, "a shopper can search the approved knowledge");
    ok((await f("/api/kb/collections")).st === 403, "a shopper cannot manage the knowledge base");
    await f("/api/auth/login", "POST", { email: "admin@luxora.shop", password: "admin123" });
    const cols = await f("/api/kb/collections");
    ok(cols.st === 200 && cols.b.collections.some(c => c.key === "astro") && cols.b.modes.length === 4, "the owner sees the collections and the four modes");
    const key = await f("/api/admin/mcp-keys", "POST", { name: "Claude Desktop", role: "support" });
    ok(key.st === 200 && /^lxm_/.test(key.b.key), "the owner issues an MCP key for the support role (shown once)");
    const B = { Authorization: "Bearer " + key.b.key, "Content-Type": "application/json" };
    const rpc = async m => (await fetch(BASE + "/api/mcp", { method: "POST", headers: B, body: JSON.stringify(m) })).json();
    const tl = await rpc({ jsonrpc: "2.0", id: 1, method: "tools/list" });
    ok(tl.result && tl.result.tools.some(t => t.name === "records_list"), "an MCP client with the key lists the tools its role may use", tl);
    const call = await rpc({ jsonrpc: "2.0", id: 2, method: "tools/call", params: { name: "knowledge_search", arguments: { collection: "astro", q: "Swati" } } });
    ok(call.result && !call.result.isError && call.result.structuredContent.entries.length >= 1, "and calls them over JSON-RPC");
    const bad = await fetch(BASE + "/api/mcp", { method: "POST", headers: { Authorization: "Bearer lxm_" + "0".repeat(48), "Content-Type": "application/json" }, body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: "tools/list" }) });
    ok(bad.status === 401, "an unknown key is refused");
    const ks = (await f("/api/admin/mcp-keys")).b.keys;
    await f("/api/admin/mcp-keys/" + ks[0].id, "DELETE");
    ok((await fetch(BASE + "/api/mcp", { method: "POST", headers: B, body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: "tools/list" }) })).status === 401, "a revoked key stops working at once");
  } catch (e) { failed++; console.log("  ✗ harness error: " + (e && e.stack || e)); }
  finally { srv.kill("SIGTERM"); await sleep(300); clean(); }
  console.log(`\n${passed} passed, ${failed} failed`);
  process.exit(failed ? 1 : 0);
})();
