/* LUXORA Platform — a store's category tree, as a read model of the platform master
   (GLOBAL_MASTER.md §6, roadmap P27–P28; owner Semantic).

   A store's categories are not its own copy of a taxonomy. They are:
     · the master's trade taxonomy under the industries the store sells in — its permissions'
       scope, else the industries it was registered with — down to every level;
     · plus the store's own categories: nodes of the same kinds in the store's namespace, placed in
       the same tree (they change nothing for anyone else);
     · with the addenda that apply to the store over them (a local name, an icon, an order, a
       category hidden there) — what the store proposed and the global platform approved.
   The `taxonomy` table is the read model the storefront, the product filters, the offer scopes and
   search read: one row per node, keyed by the node (node_uid), so a row keeps its id however often
   the tree is rebuilt and every product filed under it stays filed. Nothing edits the table: a
   store's edit is a master write (its own category) or a contribution (a master category), then
   the tree is synced. */
"use strict";

const K = require("./kernel.js");
const M = require("./platform-master.js");
const db = () => require("./db.js");
const fail = (msg, status) => { const e = new Error(msg); e.status = status || 400; throw e; };
const R = () => M.ROLES;
const holder = tid => require("./master-permissions.js").storeHolder(tid);
const levels = () => require("./registry.js").list("taxonomyLevels");
const levelOf = kind => (levels().find(l => K.isA(kind, l.kind, M.NAMESPACE)) || {}).key || null;

function ensureColumn() {
  const D = db();
  const cols = D.USE_PG ? D.all("SELECT column_name AS name FROM information_schema.columns WHERE table_name='taxonomy'") : D.all("PRAGMA table_info(taxonomy)");
  if (!cols.some(c => c.name === "node_uid")) D.exec("ALTER TABLE taxonomy ADD COLUMN node_uid TEXT");
}

/* the industries the store sells in: those its permissions on the master cover (an industry, or
   anything above or below one), else those it was registered with; a permission over the whole
   master covers every industry */
function industriesOf(tid) {
  const MP = require("./master-permissions.js");
  const view = MP.of(holder(tid)).filter(p => MP.closure(p.actions).has(R().viewAction));
  const all = require("./registry.js").list("industries").map(i => i.key);
  if (view.some(p => !p.scope.length)) return all;
  const out = new Set();
  for (const p of view) for (const s of p.scope) {
    const up = [s, ...K.ancestors(M.TRADE, s, { namespace: M.NAMESPACE })].map(M.keyOf);
    const hit = up.find(k => all.includes(k));
    if (hit) out.add(hit); else for (const i of all) if (K.ancestors(M.TRADE, M.uidOf(i), { namespace: M.NAMESPACE }).includes(s)) out.add(i);
  }
  if (out.size) return [...out];
  /* no permission says: the store's departments, else the industries it was registered with */
  const deps = db().all("SELECT key FROM departments WHERE tenant_id=?", Number(tid)).map(r => r.key).filter(k => all.includes(k));
  if (deps.length) return deps;
  const row = db().get("SELECT industries FROM tenants WHERE id=?", Number(tid));
  let reg = []; try { reg = JSON.parse((row && row.industries) || "[]"); } catch (e) { }
  return reg.length ? reg.filter(k => all.includes(k)) : all;
}

/* the tree the store should have: [{ uid, parent, key, kind, title, icon, position, hidden }] */
function desired(tid, o) {
  const MC = require("./master-contributions.js");
  const own = holder(tid);
  const out = [];
  const L = (o && o.lang) || require("./expression.js").SEED.sourceLanguage;
  const walk = (uid, parent) => {
    const row = K.internal.nodeRow(uid);
    if (row.namespace !== M.NAMESPACE && row.namespace !== own) return;
    if (!K.isA(row.kind, R().classification, M.NAMESPACE)) return;
    const a = { ...(K.attributes(uid) || {}) };
    let hidden = false;
    for (const ad of MC.addenda(uid)) {
      if (ad.holders && ad.holders.length && !ad.holders.includes(own)) continue;
      if (ad.hidden) hidden = true;
      Object.assign(a, ad.patch || {});
    }
    out.push({ uid, parent, key: M.keyOf(uid), kind: row.kind, title: K.text(a.title, L), icon: a.icon || "", position: a.position || 0, hidden });
    for (const c of K.children(M.TRADE, uid, { namespace: M.NAMESPACE })) walk(c, uid);
  };
  for (const ind of industriesOf(tid)) { const u = M.uidOf(ind); if (u) walk(u, null); }
  return out;
}

/* rebuilds the store's rows from the master: one per node, keyed by the node; a node no longer in
   the tree is deactivated, never deleted (its products stay filed) */
function sync(tid) {
  ensureColumn();
  const D = db(), t = Number(tid);
  const want = desired(t);
  const idOf = new Map(D.all("SELECT id, node_uid FROM taxonomy WHERE tenant_id=? AND node_uid IS NOT NULL", t).map(r => [r.node_uid, r.id]));
  let changed = 0;
  for (const n of want) {
    const parentId = n.parent ? idOf.get(n.parent) || null : null;
    const vals = [parentId, levelOf(n.kind), n.key, n.title, n.icon, n.hidden ? 0 : 1, n.position];
    if (idOf.has(n.uid)) changed += D.run("UPDATE taxonomy SET parent_id=?,level=?,key=?,name=?,icon=?,active=?,position=? WHERE id=? AND (parent_id IS NOT ? OR level IS NOT ? OR key IS NOT ? OR name IS NOT ? OR icon IS NOT ? OR active IS NOT ? OR position IS NOT ?)",
      ...vals, idOf.get(n.uid), ...vals).changes;
    else { idOf.set(n.uid, Number(D.run("INSERT INTO taxonomy(tenant_id,parent_id,level,key,name,icon,active,position,node_uid) VALUES(?,?,?,?,?,?,?,?,?)", t, ...vals, n.uid).lastInsertRowid)); changed++; }
  }
  const keep = new Set(want.map(n => n.uid));
  for (const [uid, id] of idOf) if (!keep.has(uid)) changed += D.run("UPDATE taxonomy SET active=0 WHERE id=? AND active<>0", id).changes;
  return changed;
}

/* a store's rows that predate the master read model are linked to master nodes once: an industry
   by its key, a category by its name under its parent's node; one the master does not have becomes
   the store's own category, in its namespace, so nothing filed under it is lost */
function adopt(tid) {
  ensureColumn();
  const D = db(), t = Number(tid);
  const rows = D.all("SELECT * FROM taxonomy WHERE tenant_id=? AND node_uid IS NULL ORDER BY COALESCE(parent_id,0), id", t);
  if (!rows.length) return 0;
  const uidOfRow = new Map(D.all("SELECT id, node_uid FROM taxonomy WHERE tenant_id=? AND node_uid IS NOT NULL", t).map(r => [r.id, r.node_uid]));
  const lv = levels();
  let n = 0;
  K.internal.tx(() => {
    const pending = [...rows];
    for (let guard = 0; pending.length && guard < rows.length + 1; guard++) {
      for (let i = 0; i < pending.length; i++) {
        const r = pending[i];
        const parentUid = r.parent_id ? uidOfRow.get(r.parent_id) : null;
        if (r.parent_id && !parentUid) continue;                 /* its parent first */
        const norm = s => String(s || "").trim().toLowerCase();
        let uid = M.uidOf(r.key);
        if (!uid && parentUid) uid = K.children(M.TRADE, parentUid, { namespace: M.NAMESPACE }).find(c => norm(K.text((K.attributes(c) || {}).title, require("./expression.js").SEED.sourceLanguage)) === norm(r.name)) || null;
        if (!uid) {
          const level = lv.find(l => l.key === r.level) || lv.find(l => l.key === require("./defaults.js").of("taxonomyLevels"));
          uid = K.createNode(level.kind, { namespace: holder(t), attributes: { title: { [require("./expression.js").SEED.sourceLanguage]: r.name }, ...(r.icon ? { icon: r.icon } : {}), position: Number(r.position) || 0 },
            identifiers: { [M.KEY]: holder(t).replace(/[^a-z0-9]/g, ".") + "." + r.key } }, "migration");
          if (parentUid) K.place(M.TRADE, uid, parentUid, { namespace: M.NAMESPACE }, "migration");
        }
        D.run("UPDATE taxonomy SET node_uid=? WHERE id=?", uid, r.id);
        uidOfRow.set(r.id, uid);
        pending.splice(i--, 1); n++;
      }
    }
  });
  return n;
}

/* ---------- a store's edits: master writes or contributions, then the tree is synced ---------- */
/* the store's own category (in its namespace), or a proposed overlay on a master one */
function save(tid, id, input, actor) {
  const D = db(), t = Number(tid);
  const i = input || {};
  const L = require("./expression.js").SEED.sourceLanguage;
  const row = id ? D.get("SELECT * FROM taxonomy WHERE tenant_id=? AND id=?", t, Number(id)) : null;
  if (id && !row) fail("Unknown category", 404);
  const parent = i.parent_id ? D.get("SELECT node_uid FROM taxonomy WHERE tenant_id=? AND id=?", t, Number(i.parent_id)) : null;
  K.internal.tx(() => {
    if (!row) {
      const level = levels().find(l => l.key === i.level) || levels().find(l => l.key === require("./defaults.js").of("taxonomyLevels"));
      const uid = K.createNode(level.kind, { namespace: holder(t), attributes: { title: { [L]: String(i.name || "") }, ...(i.icon ? { icon: String(i.icon) } : {}), position: Number(i.position) || 0 },
        identifiers: { [M.KEY]: holder(t).replace(/[^a-z0-9]/g, ".") + "." + String(i.key || (level.key + "-" + Date.now().toString(36))).toLowerCase().replace(/[^a-z0-9_.-]/g, "-") } }, actor);
      if (parent && parent.node_uid) K.place(M.TRADE, uid, parent.node_uid, { namespace: M.NAMESPACE }, actor);
      return;
    }
    const patch = { title: { [L]: String(i.name || row.name) }, ...(i.icon != null ? { icon: String(i.icon) } : {}), ...(i.position != null ? { position: Number(i.position) || 0 } : {}) };
    if (K.internal.nodeRow(row.node_uid).namespace === holder(t)) K.record(row.node_uid, patch, null, actor);
    else require("./master-contributions.js").propose(holder(t), { action: "overlay", object: classificationObject(), target: row.node_uid, patch }, actor);
  });
  return sync(t);
}
function remove(tid, id, actor) {
  const D = db(), t = Number(tid);
  const row = D.get("SELECT * FROM taxonomy WHERE tenant_id=? AND id=?", t, Number(id));
  if (!row) fail("Unknown category", 404);
  if (D.get("SELECT COUNT(*) c FROM taxonomy WHERE tenant_id=? AND parent_id=? AND active=1", t, row.id).c > 0) fail("Remove children first");
  if (K.internal.nodeRow(row.node_uid).namespace === holder(t)) require("./kernel-lifecycle.js").archive(row.node_uid, actor);
  else require("./master-contributions.js").propose(holder(t), { action: "retire", object: classificationObject(), target: row.node_uid }, actor);
  return sync(t);
}
const classificationObject = () => (M.vocabulary(R().objects).find(t => t.classification) || {}).name;

/* the generic entity surface (Data Studio) writes through here too: the table is never edited */
const entityCreate = (tid, row, actor) => { save(tid, null, row, actor); return { id: (db().get("SELECT id FROM taxonomy WHERE tenant_id=? ORDER BY id DESC LIMIT 1", Number(tid)) || {}).id }; };
const entityUpdate = (tid, id, row, actor) => { save(tid, id, row, actor); return { ok: true }; };
const entityDelete = (tid, id, actor) => { remove(tid, id, actor); return { ok: true }; };

module.exports = { industriesOf, desired, sync, adopt, save, remove, entityCreate, entityUpdate, entityDelete };
