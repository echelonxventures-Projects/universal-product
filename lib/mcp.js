/* LUXORA Platform — the platform's MCP server (Model Context Protocol): the platform's capabilities
   as tools any MCP client can call — the platform's own AI assistant, Claude Desktop, an agent, a
   partner's app — over JSON-RPC 2.0 at POST /api/mcp.

   The tools are declared data (lib/seed/mcp.json): name, description, input schema, the engine that
   answers, the capability a store must have on, and the audience. A caller is the store's shopper
   (a browser session or no key), or a store role — a staff session, or an MCP access key a store
   owner issues in Store console → AI → MCP keys, which carries a role key. A tool for staff is
   listed and answered only for a role its grants admit; records come back as the role may see them.
   One definition serves every app and every client: the assistant calls the same tools in-process. */
"use strict";
const crypto = require("crypto");
const SEED = require("./seed/mcp.json");
const db = () => require("./db.js");
const caps = () => require("./capabilities.js");

/* ---------- the engines tools are answered by ---------- */
const ENGINES = {
  knowledge_search: (ctx, a) => ({ entries: require("./rag.js").search(ctx.tenantId, a.collection, { q: a.q, tags: a.tags, limit: a.limit }).map(e => ({ id: e.id, title: e.title, body: e.body, tags: e.tags, rating: e.rating })) }),
  knowledge_collections: ctx => ({ collections: require("./rag.js").collections(ctx.tenantId).map(c => ({ key: c.key, label: c.label })) }),
  astro_chart: (ctx, a) => ({ chart: require("./astro.js").chart(a, caps().cap(ctx.tenantId, "astro_engine")) }),
  astro_panchang: (ctx, a) => ({ panchang: require("./astro.js").panchang(a, caps().cap(ctx.tenantId, "astro_engine")) }),
  astro_match: (ctx, a) => ({ match: require("./astro.js").match(a.first, a.second, caps().cap(ctx.tenantId, "astro_engine")) }),
  records_list: (ctx, a) => {
    const entity = require("./entity.js"), def = entity.allEntities(ctx.tenantId)[String(a.type || "")];
    if (!def) throw toolErr("Unknown data type: " + a.type);
    if (!roleMay(ctx, def.perm, "read")) throw toolErr("Your role may not read " + a.type);
    const hidden = (def.fields || []).filter(f => f.perm && !roleMay(ctx, f.perm, "read")).map(f => f.key);
    const rows = (entity.listEntities(ctx.tenantId, a.type, { q: a.q || "" }) || []).slice(0, 100).map(r => { const o = Object.assign({}, r); for (const k of hidden) delete o[k]; return o; });
    return { type: a.type, rows };
  }
};
function toolErr(m) { const e = new Error(m); e.tool = true; return e; }

/* a role's grant on a type or field: "platform", "admin" (any staff) or the role key itself */
function roleMay(ctx, perm, action) {
  const p = perm || {}, roles = p[action] || (action !== "read" ? p.write : null) || [];
  if (ctx.platform) return roles.includes("platform");
  if (!ctx.roleKey) return false;
  return roles.includes("admin") || roles.includes(ctx.roleKey);
}
/* a tool this caller may see: its audience, and the store's capability when it needs one */
function allowed(ctx, t) {
  if (t.capability && !caps().on(ctx.tenantId, t.capability)) return false;
  if ((SEED.AUDIENCES[t.audience] || {}).anyone) return true;
  return !!(ctx.roleKey || ctx.platform);
}
function tools(ctx) { return SEED.TOOLS.filter(t => allowed(ctx, t)); }
/* minimal JSON-schema check of a call's arguments against the tool's declared input */
function checkArgs(schema, args) {
  const a = args && typeof args === "object" && !Array.isArray(args) ? args : null;
  if (!a) return "arguments must be an object";
  for (const k of schema.required || []) if (a[k] === undefined || a[k] === null || a[k] === "") return "missing " + k;
  for (const [k, v] of Object.entries(a)) {
    const d = (schema.properties || {})[k];
    if (!d) { if (schema.additionalProperties === false) return "unknown argument " + k; continue; }
    const type = Array.isArray(v) ? "array" : typeof v;
    const want = d.type === "integer" ? "number" : d.type;
    if (want && want !== type) return k + " must be " + d.type;
  }
  return null;
}
/* calls a tool: the same path for an outside MCP client and the platform's own assistant */
function call(ctx, name, args) {
  const t = SEED.TOOLS.find(x => x.name === name);
  if (!t || !allowed(ctx, t)) return { isError: true, content: [{ type: "text", text: "Unknown tool or not available to you: " + name }] };
  const bad = checkArgs(t.inputSchema, args || {});
  if (bad) return { isError: true, content: [{ type: "text", text: "Invalid arguments: " + bad }] };
  try {
    const out = ENGINES[t.engine](ctx, args || {});
    return { content: [{ type: "text", text: JSON.stringify(out) }], structuredContent: out };
  } catch (e) { return { isError: true, content: [{ type: "text", text: e.message }] }; }
}

/* ---------- JSON-RPC 2.0 (MCP over HTTP) ---------- */
function rpc(ctx, msg) {
  const reply = result => ({ jsonrpc: "2.0", id: msg.id, result });
  const fail = (code, message) => ({ jsonrpc: "2.0", id: msg && msg.id != null ? msg.id : null, error: { code, message } });
  if (!msg || msg.jsonrpc !== "2.0" || typeof msg.method !== "string") return fail(-32600, "Invalid request");
  const notification = msg.id === undefined;
  if (notification) return null;           /* notifications/initialized and the like: no answer */
  switch (msg.method) {
    case "initialize": {
      const want = msg.params && msg.params.protocolVersion;
      return reply({ protocolVersion: SEED.PROTOCOL_VERSIONS.includes(want) ? want : SEED.PROTOCOL_VERSIONS[0], capabilities: { tools: { listChanged: false } },
        serverInfo: { name: SEED.SERVER.name, title: SEED.SERVER.title, version: "1.0.0" } });
    }
    case "ping": return reply({});
    case "tools/list": return reply({ tools: tools(ctx).map(t => ({ name: t.name, title: t.title, description: t.description, inputSchema: t.inputSchema })) });
    case "tools/call": {
      const p = msg.params || {};
      if (typeof p.name !== "string") return fail(-32602, "params.name is required");
      return reply(call(ctx, p.name, p.arguments || {}));
    }
    default: return fail(-32601, "Method not found: " + msg.method);
  }
}
function handle(ctx, body) {
  if (Array.isArray(body)) { const out = body.map(m => rpc(ctx, m)).filter(Boolean); return out.length ? out : null; }
  return rpc(ctx, body);
}

/* ---------- MCP access keys: issued by a store owner, each carrying one store role ---------- */
const hash = k => crypto.createHash("sha256").update(String(k)).digest("hex");
function issueKey(tenantId, name, roleKey, by) {
  const key = "lxm_" + crypto.randomBytes(24).toString("hex");
  db().run("INSERT INTO mcp_keys(tenant_id,name,key_hash,role_key,created_by) VALUES(?,?,?,?,?)", Number(tenantId), String(name || "MCP key").slice(0, 80), hash(key), String(roleKey), String(by || ""));
  return { key, note: "Shown once. Use it as the Bearer token for the API or an MCP client." };
}
const keys = tenantId => db().all("SELECT id,name,role_key,created_by,created_at,last_used,revoked FROM mcp_keys WHERE tenant_id=? ORDER BY id DESC", Number(tenantId));
const revokeKey = (tenantId, id) => db().run("UPDATE mcp_keys SET revoked=1 WHERE id=? AND tenant_id=?", Number(id), Number(tenantId)).changes > 0;
function byKey(bearer) {
  if (!/^lxm_[0-9a-f]{48}$/.test(String(bearer || ""))) return null;
  const r = db().get("SELECT * FROM mcp_keys WHERE key_hash=? AND revoked=0", hash(bearer));
  if (r) db().run("UPDATE mcp_keys SET last_used=datetime('now') WHERE id=?", r.id);
  return r || null;
}

module.exports = { TOOLS: SEED.TOOLS, tools, call, handle, issueKey, keys, revokeKey, byKey, roleMay };
