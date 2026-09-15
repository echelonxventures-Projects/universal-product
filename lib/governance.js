/* LUXORA Platform — governance: soft-delete (Trash), restore, retention purge.
   Works across ANY soft-deletable entity via the entity definition registry (table + pk + tenant
   scoping) — no per-entity code. A `deleted_at` timestamp is the only column added; reads filter it
   out, the Trash view lists + restores, and retention purges (hard-deletes) tombstoned rows older
   than a policy (data-driven per tenant + platform default). PII/GDPR: purge is the erasure path. */
"use strict";

let _db = null, _entity = null;
const db = () => _db || (_db = require("./db.js"));
const entity = () => _entity || (_entity = require("./entity.js"));
const J = (v, d) => { try { return v == null || v === "" ? d : (typeof v === "string" ? JSON.parse(v) : v); } catch (e) { return d; } };

/* entity KEYS that carry a deleted_at column (soft-deletable). */
const SOFT = new Set(["product", "promotion", "order", "ret", "review", "supplier", "seller", "warehouse", "department", "attribute", "taxonomy", "serialized", "variant_group", "compliance", "localization", "contract", "tender", "product_supplier", "banner", "card"]);

function isSoft(entityKey) { return SOFT.has(entityKey); }
function def(entityKey) { return entity().allEntities(0)[entityKey] || entity().allEntities(1)[entityKey]; }

function whereFor(D, defObj, id, tenantId) {
  if (defObj.platformOnly || defObj.noTenant) return { sql: "", args: [] };
  return { sql: "tenant_id=? AND ", args: [tenantId] };
}
function keyCond(D, defObj, id) {
  if (defObj.composite) { const parts = String(id).split("|"); return { sql: `${defObj.pk}=? AND ${defObj.pk2}=?`, args: parts }; }
  return { sql: `${defObj.pk}=?`, args: [defObj.pkType === "text" ? String(id) : Number(id)] };
}

function trash(tenantId, entityKey, id) {
  const d = def(entityKey); if (!d || !isSoft(entityKey)) return { error: "not soft-deletable" };
  const D = db(); const kc = keyCond(D, d, id); const w = whereFor(D, d, id, tenantId);
  const r = D.run(`UPDATE ${d.table} SET deleted_at=datetime('now') WHERE ${w.sql}${kc.sql} AND deleted_at IS NULL`, ...w.args, ...kc.args);
  if (!r.changes) return { error: "not found or already trashed", code: 404 };
  return { ok: true };
}
function restore(tenantId, entityKey, id) {
  const d = def(entityKey); if (!d) return { error: "unknown entity" };
  const D = db(); const kc = keyCond(D, d, id); const w = whereFor(D, d, id, tenantId);
  const r = D.run(`UPDATE ${d.table} SET deleted_at=NULL WHERE ${w.sql}${kc.sql}`, ...w.args, ...kc.args);
  if (!r.changes) return { error: "not found", code: 404 }; return { ok: true };
}
function listTrash(tenantId, limit) {
  const D = db(); const out = [];
  for (const key of SOFT) {
    const d = def(key); if (!d) continue;
    const w = whereFor(D, d, null, tenantId);
    try {
      const rows = D.all(`SELECT ${[...d.fields.map(f => f.col || f.key), d.pk].filter((v,i,a)=>a.indexOf(v)===i).join(",")}, deleted_at FROM ${d.table} WHERE ${w.sql}deleted_at IS NOT NULL ORDER BY deleted_at DESC LIMIT ?`, ...w.args, limit || 50)
        .map(r => ({ entity: key, id: String(r[d.pk]), deleted_at: r.deleted_at }));
      for (const r of rows) out.push(r);
    } catch (e) { }
  }
  return out;
}
function counts(tenantId) {
  const D = db(); const c = {};
  for (const key of SOFT) { const d = def(key); if (!d) continue; const w = whereFor(D, d, null, tenantId); try { c[key] = D.get(`SELECT COUNT(*) n FROM ${d.table} WHERE ${w.sql}deleted_at IS NOT NULL`, ...w.args).n; } catch (e) { } }
  return c;
}

/* retention (data): per-entity days; 0 = never purge; platform default. */
function defaultRetention() { return { _default: 30, orders: 0, products: 30, reviews: 90, offers: 30, coupons: 30 }; }
function getRetention(tenantId) {
  const D = db(); let saved = {};
  try { const p = D.get("SELECT value FROM platform_settings WHERE key='retention'"); if (p) saved = J(p.value, {}); } catch (e) { }
  let own = {}; try { const r = D.get("SELECT value FROM settings WHERE tenant_id=? AND key='retention'", tenantId); if (r) own = J(r.value, {}); } catch (e) { }
  return Object.assign(defaultRetention(), saved, own);
}
function setRetention(tenantId, patch) {
  const D = db();
  if (!tenantId) { const cur = (() => { try { const p = D.get("SELECT value FROM platform_settings WHERE key='retention'"); return p ? J(p.value, {}) : {}; } catch (e) { return {}; } })(); Object.assign(cur, patch); D.run("INSERT INTO platform_settings(key,value) VALUES('retention',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", JSON.stringify(cur)); return cur; }
  D.run("INSERT INTO settings(tenant_id,key,value) VALUES(?,?,?) ON CONFLICT(tenant_id,key) DO UPDATE SET value=excluded.value", tenantId, "retention", JSON.stringify(patch)); return patch;
}
/* purge: hard-delete soft-deleted rows older than their retention (0/absent = keep forever) */
function purge(tenantId) {
  const D = db(); const pol = getRetention(tenantId); const report = {};
  for (const key of SOFT) {
    const d = def(key); if (!d) continue;
    const days = pol[key] != null ? pol[key] : pol._default;
    if (!days || days <= 0) continue; // never purge
    const w = whereFor(D, d, null, tenantId);
    try { const r = D.run(`DELETE FROM ${d.table} WHERE ${w.sql}deleted_at IS NOT NULL AND deleted_at < datetime('now', ?)`, ...w.args, `-${days} day`); if (r.changes) report[key] = r.changes; } catch (e) { }
  }
  return { ok: true, purged: report };
}

module.exports = { SOFT, isSoft, trash, restore, listTrash, counts, getRetention, setRetention, purge, defaultRetention };
