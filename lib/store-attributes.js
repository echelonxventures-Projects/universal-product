/* LUXORA Platform — a store's attribute definitions (its "columns"), as a read model of the platform
   master (GLOBAL_MASTER.md §1, §6; owner Registry).

   What a store's products may carry is not its own list. It is:
     · the master's attribute definitions that apply where the store sells (bound nowhere, or bound
       to taxonomy nodes under or above its industries), with their types, units and rules;
     · plus the store's own definitions: definition nodes in the store's namespace;
     · with the addenda for the store over them.
   The attribute_defs table is the read model the console's product editor, the validator and search
   read, in the shape they read: a definition's kernel value type is shown as the editor's field type
   by the master's attribute_types vocabulary, a quantity in its dimension's base unit, a one-of rule as
   the options. Nothing edits the table: a store's own definition is a master write in its namespace,
   a change to a master definition a contribution; the platform's own registry writes the master. */
"use strict";

const K = require("./kernel.js");
const M = require("./platform-master.js");
const db = () => require("./db.js");
const fail = (msg, status) => { const e = new Error(msg); e.status = status || 400; throw e; };
const R = () => M.ROLES;
const holder = tid => require("./master-permissions.js").storeHolder(tid);
const L = () => require("./expression.js").SEED.sourceLanguage;
const TYPES = () => M.vocabulary(R().attributeTypes);
/* the editor's field type for a kernel value type (with a one-of rule: the choice type), and back */
const shownAs = (type, constraints) => { const t = TYPES().find(x => x.kernel === type && !!x.choice === !!(constraints && constraints.oneOf)) || TYPES().find(x => x.kernel === type); return t ? t.name : type; };
const kernelOf = shown => { const t = TYPES().find(x => x.name === shown) || fail("Unknown attribute type: " + shown); return t; };

function ensureColumn() {
  const D = db();
  const cols = D.USE_PG ? D.all("SELECT column_name AS name FROM information_schema.columns WHERE table_name='attribute_defs'") : D.all("PRAGMA table_info(attribute_defs)");
  if (!cols.some(c => c.name === "node_uid")) D.exec("ALTER TABLE attribute_defs ADD COLUMN node_uid TEXT");
}
/* a definition as a row of the read model */
function rowOf(d, patch) {
  const a = { ...d, ...(patch || {}) };
  const cons = { ...(a.constraints || {}) };
  const options = cons.oneOf || [];
  delete cons.oneOf;
  const dim = a.unit_dimension ? K.children(R().units, a.unit_dimension, { namespace: M.NAMESPACE }).map(u => K.attributes(u)).find(u => u.factor === 1 && !u.offset) : null;
  const at = (a.at || []).map(M.keyOf).filter(Boolean);
  return { key: a.name, label: K.text(a.title, L()), grp: a.group || "", type: shownAs(a.type, a.constraints), unit: dim ? dim.symbol : "", options, validation: cons,
    industry: at[0] ? at[0].split(".")[0] : "", position: a.position || 0, node_uid: d.uid };
}
/* the definitions the store should have */
function desired(tid) {
  const MC = require("./master-contributions.js");
  const own = holder(tid);
  const inds = require("./store-taxonomy.js").industriesOf(tid);
  const applies = new Set(M.attributeSet({ at: inds }).map(d => d.uid));
  const mine = K.nodes(R().attribute, own).map(u => ({ uid: u, key: M.keyOf(u), ...K.attributes(u) }));
  const out = new Map();
  for (const d of [...M.definitions().filter(d => applies.has(d.uid)), ...mine]) {
    let patch = {}, hidden = false;
    for (const ad of MC.addenda(d.uid)) {
      if (ad.holders && ad.holders.length && !ad.holders.includes(own)) continue;
      if (ad.hidden) hidden = true;
      Object.assign(patch, ad.patch || {});
    }
    if (!hidden) out.set(d.name, rowOf(d, patch));       /* the store's own definition of a name comes last and wins */
  }
  return [...out.values()];
}
/* rebuilds the store's rows: one per definition, by its name; a definition no longer there goes
   (the values products hold under it stay on the products) */
function sync(tid) {
  ensureColumn();
  const D = db(), t = Number(tid);
  const want = desired(t);
  K.internal.tx(() => {
    D.run("DELETE FROM attribute_defs WHERE tenant_id=? AND key NOT IN (" + (want.map(() => "?").join(",") || "''") + ")", t, ...want.map(w => w.key));
    for (const w of want) D.run(`INSERT INTO attribute_defs(tenant_id,key,label,grp,type,unit,options,validation,industry,position,node_uid) VALUES(?,?,?,?,?,?,?,?,?,?,?)
      ON CONFLICT(tenant_id,key) DO UPDATE SET label=excluded.label,grp=excluded.grp,type=excluded.type,unit=excluded.unit,options=excluded.options,validation=excluded.validation,industry=excluded.industry,position=excluded.position,node_uid=excluded.node_uid`,
      t, w.key, w.label, w.grp, w.type, w.unit, JSON.stringify(w.options), JSON.stringify(w.validation), w.industry, w.position, w.node_uid);
  });
  return want.length;
}
/* a definition written from the editor's shape onto the master, in a namespace */
function defineIn(namespace, i, actor, uid) {
  const name = String(i.key || i.name || "").trim().toLowerCase().replace(/[^a-z0-9_]/g, "");
  if (!name || !i.label) fail("Key and label required");
  const t = kernelOf(String(i.type || TYPES().find(x => x.default).name));
  const constraints = { ...(i.validation || {}), ...((t.choice && (i.options || []).length) ? { oneOf: i.options } : {}) };
  const attrs = { name, title: { [L()]: String(i.label) }, type: t.kernel, group: String(i.grp || i.category || ""), constraints, position: Number(i.position) || 0,
    ...(i.industry && M.uidOf(i.industry) ? { at: [M.uidOf(i.industry)] } : {}) };
  if (uid) return K.record(uid, attrs, null, actor);
  const key = (namespace === M.NAMESPACE ? R().attributePrefix : namespace.replace(/[^a-z0-9]/g, ".") + ".") + name;
  if (M.uidOf(key)) fail("That attribute already exists: " + name, 409);
  return K.createNode(R().attribute, { namespace, identifiers: { [M.KEY]: key }, attributes: attrs }, actor);
}
/* an older store's rows: a name the master defines is the master's; any other becomes the store's own */
function adopt(tid) {
  ensureColumn();
  const D = db(), t = Number(tid);
  const rows = D.all("SELECT * FROM attribute_defs WHERE tenant_id=? AND node_uid IS NULL", t);
  if (!rows.length) return 0;
  const master = new Set(M.definitions().map(d => d.name));
  K.internal.tx(() => {
    for (const r of rows) if (!master.has(r.key) && TYPES().some(x => x.name === r.type))
      defineIn(holder(t), { ...r, options: JSON.parse(r.options || "[]"), validation: JSON.parse(r.validation || "{}") }, "migration");
  });
  return rows.length;
}
/* a store's edit: its own definition directly; a master one by contribution */
function save(tid, input, actor) {
  const t = Number(tid);
  const name = String((input && input.key) || "").trim().toLowerCase().replace(/[^a-z0-9_]/g, "");
  const row = db().get("SELECT node_uid FROM attribute_defs WHERE tenant_id=? AND key=?", t, name);
  K.internal.tx(() => {
    if (!row) return defineIn(holder(t), input, actor);
    if (K.internal.nodeRow(row.node_uid).namespace === holder(t)) return defineIn(holder(t), input, actor, row.node_uid);
    const ty = kernelOf(String(input.type || ""));
    return require("./master-contributions.js").propose(holder(t), { action: "modify", object: attributeObject(), target: row.node_uid,
      patch: { title: { [L()]: String(input.label) }, group: String(input.grp || ""), constraints: { ...(input.validation || {}), ...(ty.choice && (input.options || []).length ? { oneOf: input.options } : {}) } } }, actor);
  });
  return sync(t);
}
function remove(tid, key, actor) {
  const t = Number(tid);
  const row = db().get("SELECT node_uid FROM attribute_defs WHERE tenant_id=? AND key=?", t, String(key));
  if (!row) fail("Unknown attribute", 404);
  if (K.internal.nodeRow(row.node_uid).namespace === holder(t)) require("./kernel-lifecycle.js").archive(row.node_uid, actor);
  else require("./master-contributions.js").propose(holder(t), { action: "retire", object: attributeObject(), target: row.node_uid }, actor);
  return sync(t);
}
const attributeObject = () => (M.vocabulary(R().objects).find(t => t.attribute) || {}).name;

/* the platform's own registry: the master's definitions in the editor's shape, and new ones */
const platformList = () => M.definitions().map(d => ({ ...rowOf(d), category: d.group || "" }));
const platformCreate = (input, actor) => defineIn(M.NAMESPACE, input, actor);

/* the generic entity surface writes through here too */
const entityCreate = (tid, row, actor) => { save(tid, row, actor); return { id: String(row.key) }; };
const entityUpdate = (tid, id, row, actor) => { save(tid, { ...row, key: id }, actor); return { ok: true }; };
const entityDelete = (tid, id, actor) => { remove(tid, id, actor); return { ok: true }; };

module.exports = { desired, sync, adopt, save, remove, platformList, platformCreate, entityCreate, entityUpdate, entityDelete };
