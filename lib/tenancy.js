/* LUXORA Platform — universal tenancy hierarchy
   Platform → Tenant → Organization → Business Unit → Brand → Store → Channel.
   Every node is one row; the materialized `path` makes subtree queries a LIKE away,
   mirroring GOIP's hierarchy paths (earth.in.bihar.patna) so operators think one way.
   The hierarchy is also the *config cascade*: a setting resolved at a Store inherits
   from Store → Brand → Business Unit → Organization → Tenant → Platform, deepest wins. */
"use strict";

const { all, run, get } = require("./db.js");
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d || {}; } };

const KINDS = ["organization", "business_unit", "brand", "store", "channel", "website", "mobile_app", "marketplace", "social", "pos", "api_commerce", "region"];
/* the root of every tenant's tree: not a row the operator creates — the tenant itself,
   addressed as path "<slug>" and stored once per tenant on first use */
const ROOT_KIND = "tenant";

function ensureTables() {
  run(`CREATE TABLE IF NOT EXISTS tenancy_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    kind TEXT NOT NULL,
    parent_id INTEGER,
    slug TEXT NOT NULL,
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    profile TEXT DEFAULT '{}',
    config TEXT DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    uid TEXT,
    UNIQUE(tenant_id, path)
  )`);
  run(`CREATE INDEX IF NOT EXISTS ix_tenancy_parent ON tenancy_nodes(tenant_id, parent_id)`);
  run(`CREATE INDEX IF NOT EXISTS ix_tenancy_kind ON tenancy_nodes(tenant_id, kind)`);
  /* resolved config cache: the cascade for (node, key) — invalidated on any write */
  run(`CREATE TABLE IF NOT EXISTS tenancy_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    node_id INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT DEFAULT '{}',
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(tenant_id, node_id, key)
  )`);
}

const slugify = s => String(s || "").trim().toLowerCase().replace(/[^a-z0-9-]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 48);

/* ---------- tree reads ---------- */
function list(tenantId) {
  ensureTables();
  return all("SELECT * FROM tenancy_nodes WHERE tenant_id=? ORDER BY parent_id IS NULL DESC, parent_id, id", Number(tenantId))
    .map(r => ({ ...r, profile: J(r.profile, {}), config: J(r.config, {}) }));
}
function byId(tenantId, id) {
  ensureTables();
  const r = get("SELECT * FROM tenancy_nodes WHERE tenant_id=? AND id=?", Number(tenantId), Number(id));
  return r ? { ...r, profile: J(r.profile, {}), config: J(r.config, {}) } : null;
}
function byPath(tenantId, path) {
  ensureTables();
  const r = get("SELECT * FROM tenancy_nodes WHERE tenant_id=? AND path=?", Number(tenantId), String(path));
  return r ? { ...r, profile: J(r.profile, {}), config: J(r.config, {}) } : null;
}
function root(tenantId) {
  ensureTables();
  let r = get("SELECT * FROM tenancy_nodes WHERE tenant_id=? AND parent_id IS NULL", Number(tenantId));
  if (!r) {
    const t = get("SELECT slug, name FROM tenants WHERE id=?", Number(tenantId));
    if (!t) return null;
    const ins = run("INSERT INTO tenancy_nodes(tenant_id,kind,parent_id,slug,name,path,profile) VALUES(?,?,NULL,?,?,?,?)",
      Number(tenantId), ROOT_KIND, t.slug, t.name, t.slug, "{}");
    r = get("SELECT * FROM tenancy_nodes WHERE id=?", ins.lastInsertRowid);
  }
  return r ? { ...r, profile: J(r.profile, {}), config: J(r.config, {}) } : null;
}
/* nested shape for the console: children hang off their parent */
function tree(tenantId) {
  const rows = list(tenantId);
  const byParent = {};
  rows.forEach(r => (byParent[r.parent_id || 0] = byParent[r.parent_id || 0] || []).push(r));
  const build = p => (byParent[p.id || 0] || []).map(c => ({ ...c, children: build(c) }));
  const rt = rows.find(r => r.parent_id == null) || null;
  return rt ? { ...rt, children: build(rt) } : null;
}

/* ---------- writes ---------- */
function create(tenantId, node) {
  ensureTables();
  const rt = root(tenantId);
  if (!rt) return { error: "no such tenant" };
  const kind = String(node.kind || "").trim();
  if (!KINDS.includes(kind)) return { error: "unknown kind: " + kind };
  const slug = slugify(node.slug || node.name);
  if (!slug) return { error: "slug required" };
  const parent = node.parent_id != null ? byId(tenantId, node.parent_id) : rt;
  if (!parent) return { error: "unknown parent" };
  const path = parent.path + "." + slug;
  if (byPath(tenantId, path)) return { error: "path already taken", status: 409 };
  /* a store/brand/channel may hold runtime state; refuse to create under a suspended node */
  let p = parent;
  while (p) { if (p.status === "suspended") return { error: "parent chain is suspended" }; p = p.parent_id != null ? byId(tenantId, p.parent_id) : null; }
  const ins = run("INSERT INTO tenancy_nodes(tenant_id,kind,parent_id,slug,name,path,profile,config,uid) VALUES(?,?,?,?,?,?,?,?)",
    Number(tenantId), kind, parent.id, slug, String(node.name || slug).slice(0, 80), path,
    JSON.stringify(J(node.profile, {})), JSON.stringify(J(node.config, {})), null);
  const created = byId(tenantId, ins.lastInsertRowid);
  require("./db.js").audit(Number(tenantId), "platform", 0, "system", "tenancy.create", "tenancy_node", created.id, { kind, path });
  return created;
}
function update(tenantId, id, patch) {
  ensureTables();
  const n = byId(tenantId, id);
  if (!n) return { error: "no such node", status: 404 };
  if (patch.name != null) run("UPDATE tenancy_nodes SET name=? WHERE id=?", String(patch.name).slice(0, 80), id);
  if (patch.status != null && ["active", "suspended"].includes(patch.status))
    run("UPDATE tenancy_nodes SET status=? WHERE id=?", patch.status, id);
  if (patch.profile) run("UPDATE tenancy_nodes SET profile=? WHERE id=?", JSON.stringify({ ...n.profile, ...J(patch.profile, {}) }), id);
  if (patch.config) { setConfig(tenantId, id, patch.config); }
  return byId(tenantId, id);
}
/* deleting a node deletes its subtree; the root is immortal */
function del(tenantId, id) {
  ensureTables();
  const n = byId(tenantId, id);
  if (!n) return { error: "no such node", status: 404 };
  if (n.parent_id == null) return { error: "the tenant root cannot be deleted", status: 403 };
  const victims = all("SELECT id FROM tenancy_nodes WHERE tenant_id=? AND path LIKE ?", Number(tenantId), n.path + ".%").map(r => r.id).concat([id]);
  for (const v of victims) run("DELETE FROM tenancy_config WHERE tenant_id=? AND node_id=?", Number(tenantId), v);
  run("DELETE FROM tenancy_nodes WHERE tenant_id=? AND id IN (" + victims.map(() => "?").join(",") + ")", Number(tenantId), ...victims);
  require("./db.js").audit(Number(tenantId), "platform", 0, "system", "tenancy.delete", "tenancy_node", id, { path: n.path, victims });
  return { ok: true, removed: victims.length };
}

/* ---------- the configuration cascade ----------
   Resolve walks root → node, deep-merging each node's config so a value set on a Brand
   reaches every Store beneath it unless that Store overrides it. Deep-merge (not
   replace) is what lets an operator set one nested field without wiping the others. */
function deepMerge(base, over) {
  if (!base || typeof base !== "object" || Array.isArray(base)) return over === undefined ? base : over;
  if (!over || typeof over !== "object" || Array.isArray(over)) return over === undefined ? base : over;
  const out = { ...base };
  for (const k of Object.keys(over)) out[k] = deepMerge(base[k], over[k]);
  return out;
}
function chain(tenantId, nodeId) {
  const n = byId(tenantId, nodeId);
  if (!n) return [];
  const out = [n];
  let cur = n;
  while (cur.parent_id != null) {
    cur = byId(tenantId, cur.parent_id);
    if (!cur) break;
    out.push(cur);
  }
  return out.reverse(); /* root first */
}
function resolve(tenantId, nodeId, key) {
  ensureTables();
  const n = byId(tenantId, nodeId) || root(tenantId);
  if (!n) return null;
  const acc = {};
  for (const node of chain(tenantId, n.id)) {
    const cfg = key ? getConfig(tenantId, node.id, key) : node.config;
    if (cfg) Object.assign(acc, deepMerge(acc, cfg));
  }
  return key ? (key in acc ? acc[key] : undefined) : acc;
}
function getConfig(tenantId, nodeId, key) {
  ensureTables();
  const r = get("SELECT value FROM tenancy_config WHERE tenant_id=? AND node_id=? AND key=?", Number(tenantId), Number(nodeId), String(key));
  return r ? J(r.value, {}) : null;
}
function setConfig(tenantId, nodeId, key, value) {
  ensureTables();
  if (!byId(tenantId, nodeId) && Number(nodeId) !== (root(tenantId) || {}).id) return { error: "no such node", status: 404 };
  run("INSERT INTO tenancy_config(tenant_id,node_id,key,value,updated_at) VALUES(?,?,?,?,datetime('now')) ON CONFLICT(tenant_id,node_id,key) DO UPDATE SET value=excluded.value, updated_at=datetime('now')",
    Number(tenantId), Number(nodeId), String(key), JSON.stringify(value == null ? {} : value));
  require("./db.js").audit(Number(tenantId), "platform", 0, "system", "tenancy.config", "tenancy_node", nodeId, { key });
  return { ok: true };
}

module.exports = { KINDS, ensureTables, list, tree, byId, byPath, root, create, update, del, chain, resolve, getConfig, setConfig, deepMerge };
