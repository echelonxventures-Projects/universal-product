/* LUXORA Platform - Universal Entity Meta Model.
   Every entity (built-in or custom) is described as data: fields, types, validation,
   permissions, list/form rendering hints. The generic engine below performs CRUD,
   validation, tenant scoping and auditing for ALL of them - zero per-entity code. */
"use strict";
/* seed data (lib/seed/entity.json): data, not code — the registries are seeded from it */
const SEED_ENTITY = require("./seed/entity.json");

const crypto = require("crypto");
const { run, get, all } = require("./db.js");

/* field types: text | textarea | number | money | bool | date | select | multi | json | secret | ref:<entity> | readonly */
const F = (key, label, type, o) => ({ key, label, type, ...(o || {}) });

/* notes that lived in the seed literal (now lib/seed/entity.json): */
/* a subdivision is a child of the COUNTRY master, never a child of a store. It is
   platform-level master data (the same noTenant/platformOnly pair countries, currencies
   and the uv_* universes carry) so it is created once and reused by every store, service
   and ERP that needs a jurisdiction — the master itself never gains a tenant_id. A store
   ATTACHES to it by resolving its jurisdiction (settings/checkout/tax), never by owning a
   row. See lib/registry.js reconcileSubdivisions: adding a country materialises its
   states/provinces automatically, at write time and on every boot. */
/* Universal Dashboard & Reporting Engine (Architecture1 §394/§395): a dashboard is a
   runtime object — Identity/Audience/Widgets/Metrics/Filters — stored as entity data, so
   CRUD, validation and forms arrive from this declaration and the engine in
   lib/dashboards.js computes metrics generically. No per-dashboard code anywhere. */
/* an operator edit to a registry list is stamped `edited=1`, which every revisioned
   seed (rb_v2 / reg_v1 / cap_v2…) reads as "the operator owns this row — never
   clobber it". Without the stamp the self-heal would silently revert console edits. */
/* TAX OWNS TAX. A jurisdiction's rates are the tax engine's own master data — one row per
   country — not columns on the country master. This entity is the single source of truth the
   checkout, invoicing and the storefront label all resolve (lib/tax.js ruleFor); a country
   master carries no tax facts, so there is no second copy to drift against. Seeded from the
   engine's registry and re-asserted only where nobody has edited it. */
/* the context primitive: a dimension (grp) holds named profiles (key) with their own
   declarative fields. Seeded from the registry's verticalContexts, but the table is the
   source of truth, so an operator adds a context dimension here and it appears in the
   product view and at checkout with no code change (see api.js context resolution). */
/* the relationship primitive: a typed edge between any two entities by their universal id.
   RELATIONSHIP OWNS RELATIONSHIP — an edge is created once here and reused by every surface
   that relates two things, exactly as a country master is created once and reused by every
   jurisdiction. The product-scoped `relationships` table the storefront reads is a DERIVED
   projection of this (lib/registry.js reconcileLinks), never a second source of truth: the
   old path wrote the projection first and mirrored here best-effort, which left the primitive
   optional and silently absent, so an edge existed in one store's catalogue and in nothing
   else. `links` is noTenant because an edge is platform-level — a store attaches to it by
   owning its endpoints, never by scoping the row. */
/* ---- GOIP Ω∞ stores: the four records no other entity owns ---- */
const ENTITY_DEFS = SEED_ENTITY.ENTITY_DEFS;

/* ============================================================
   UNIVERSAL COMMERCE ENTITIES — each block is one capability,
   expressed purely as entity data: fields, types, options
   from registries (meta_lists). CRUD, validation, forms, lists and
   RBAC gates arrive generically from this declaration — zero
   per-domain code (Architecture3 Article 4.2). Merged into the entity
   set by allEntities() so tenant-defined custom entities can override.
   ============================================================ */
/* notes that lived in the seed literal (now lib/seed/entity.json): */
/* ---------- Quick-commerce ---------- */
/* ---------- Fintech ---------- */
/* ---------- Marketplace ---------- */
/* ---------- B2B trust & trade ---------- */
/* ---------- Shopper experience completions ---------- */
/* ---- E17 · the mobility universe ---- */
/* ---- E18 · the operations universe ---- */
const PARITY_DEFS = SEED_ENTITY.PARITY_DEFS;

/* ---- custom entities (fully data-defined, JSON storage) ---- */
function customEntityDefs(tenantId) {
  const rows = all("SELECT key, def FROM entity_defs WHERE scope='platform' OR (scope='tenant' AND tenant_id=?)", tenantId);
  const out = {};
  for (const r of rows) { try { out[r.key] = JSON.parse(r.def); } catch (e) { } }
  return out;
}
/* the commerce layer ships as
   entity data exactly like every other entity; a tenant-defined custom entity of the
   same key wins, so an operator can reshape any domain from Data Studio. */
function allEntities(tenantId) { return { ...ENTITY_DEFS, ...PARITY_DEFS, ...customEntityDefs(tenantId) }; }

function coerce(field, raw) {
  if (field.upper && typeof raw === "string") raw = raw.toUpperCase();
  switch (field.type) {
    case "number": case "money": return raw === "" || raw == null ? null : Number(raw);
    case "bool": return raw === true || raw === 1 || raw === "1" || raw === "true" || raw === "on" ? 1 : 0;
    case "json": case "multi": return typeof raw === "string" ? raw : JSON.stringify(raw == null ? null : raw);
    default: return raw == null ? null : String(raw);
  }
}
function optionValues(name) {
  if (!name) return null;
  const r = get("SELECT items FROM meta_lists WHERE name=?", name);
  if (!r) return null;
  let j; try { j = JSON.parse(r.items); } catch (e) { return null; }
  if (!Array.isArray(j)) return null;
  return j.map(x => x && typeof x === "object" ? (x.key != null ? x.key : x.id != null ? x.id : x.code != null ? x.code : x.value) : x).filter(x => x != null);
}
function validate(def, row, partial) {
  const errs = [];
  for (const f of def.fields) {
    if (f.readonly) continue;
    const v = row[f.key];
    /* a required field must be present and non-empty. On a PARTIAL update (a console edit
       touching a few fields) only the fields the payload actually names are checked — an
       update must not fail on required columns the caller didn't send. On a full create or
       an import, every required field is checked: an empty name, a missing code, a blank
       currency are rejected here as "required" rather than slipping through as an empty
       string that SQLite accepts against NOT NULL (an import's blank cell is "", not NULL). */
    if (f.required && (v == null || v === "")) {
      if (partial && !(f.key in row)) continue;
      errs.push(f.label + " is required"); continue;
    }
    if ((f.type === "number" || f.type === "money") && v != null && v !== "" && isNaN(Number(v))) errs.push(f.label + " must be a number");
    if (f.type === "select") {
      const opts = Array.isArray(f.options) ? f.options : (typeof f.options === "string" && f.options.indexOf(".") < 0 ? optionValues(f.options) : null);
      if (opts && v != null && v !== "" && !opts.includes(v)) errs.push(f.label + " invalid option");
    }
    if (f.type === "json" && typeof v === "string" && v) { try { JSON.parse(v); } catch (e) { errs.push(f.label + " invalid JSON"); } }
    if (v == null || v === "") continue;
    /* a field may declare the shape its value takes: a `pattern` (with a `patternHint` for
       the message), a named `format` the kernel checks and numeric bounds (`min`, `max`, `gt`).
       The master data (a country's code, its currency, its locale) is checked by its own
       declaration */
    if (f.pattern && !new RegExp(f.pattern).test(String(v))) errs.push(f.label + " must be " + (f.patternHint || "of the form " + f.pattern));
    if (f.format && FORMATS[f.format] && !FORMATS[f.format](v)) errs.push(f.label + " is not a valid " + f.format);
    if (f.min != null && Number(v) < f.min) errs.push(f.label + " must be at least " + f.min);
    if (f.max != null && Number(v) > f.max) errs.push(f.label + " must be at most " + f.max);
    if (f.gt != null && !(Number(v) > f.gt)) errs.push(f.label + " must be greater than " + f.gt);
  }
  return errs;
}
/* kernel: the value formats a field may declare */
const FORMATS = {
  locale: v => { try { return Intl.getCanonicalLocales(String(v)).length === 1; } catch (e) { return false; } }
};
/* a server-side filter is what makes a large catalogue usable: an entity such as `sku`
   grows past any fixed cap once the corpus is activated (~2,000 SKUs on the flagship),
   so the console and API must be able to ask for "the SKUs of THIS product" and get a
   deterministic answer. `q` is a free-text search over the listed columns; `where` is a
   set of equality predicates on declared fields. Both are parameterized and both are
   whitelisted against the entity's own field list, so nothing arbitrary reaches SQL. */
function listEntities(tenantId, key, opts) {
  opts = opts || {};
  const defs = allEntities(tenantId);
  const def = defs[key];
  if (!def) return null;
  const q = opts.q != null ? String(opts.q).trim() : "";
  const whereRaw = opts.where && typeof opts.where === "object" ? opts.where : {};
  if (def.storage === "json") {
    /* a PLATFORM-LEVEL master (a universe, or any platformOnly/noTenant json entity) is
       inherited by every store: its rows live at tenant 0 and are read with no store
       filter, so the master is reusable everywhere and is never duplicated per store.
       A store-scoped entity keeps its own rows plus any NULL-scoped ones — never
       another store's. This is the read half of "master data has no tenant_id" */
    const scoped = !def.platformOnly && !def.noTenant;
    let rows = all("SELECT * FROM entity_data WHERE entity=?" + (scoped ? " AND (tenant_id=? OR tenant_id IS NULL)" : ""), key, ...(scoped ? [tenantId] : []));
    let out = rows.map(r => ({ id: r.id, ...JSON.parse(r.data || "{}"), created_at: r.created_at }));
    const wkeys = Object.keys(whereRaw);
    if (wkeys.length) out = out.filter(r => wkeys.every(k => String(r[k]) === String(whereRaw[k])));
    if (q) { const cols = def.fields.filter(f => f.list && (f.type === "text" || f.type === "textarea")).map(f => f.key);
      if (cols.length) out = out.filter(r => cols.some(c => String(r[c] || "").toLowerCase().includes(q.toLowerCase()))); }
    return out;
  }
  const fieldCols = def.fields.map(f => (f.col || f.key) + (f.col && f.col !== f.key ? " AS " + f.key : ""));
  if (!def.composite && def.pk && !def.fields.some(f => (f.col || f.key) === def.pk)) fieldCols.unshift(def.pk);
  const cols = fieldCols.join(",");
  let sql = `SELECT ${cols}${def.composite ? `,${def.pk2} as _pk2` : ""} FROM ${def.table}`;
  const args = [];
  const clauses = [];
  if (!def.platformOnly && !def.noTenant) { clauses.push("tenant_id=?"); args.push(tenantId); }
  if (opts.hideDeleted) clauses.push("deleted_at IS NULL");
  /* `where` predicates: only declared fields, always parameterized */
  for (const [k, v] of Object.entries(whereRaw)) {
    const col = def.fields.find(f => f.key === k);
    if (col) { clauses.push((col.col || col.key) + "=?"); args.push(v); }
  }
  /* `q`: LIKE over the text columns the entity marks as list-visible */
  if (q) {
    const textCols = def.fields.filter(f => f.list && (f.type === "text" || f.type === "textarea")).map(f => f.col || f.key);
    if (textCols.length) {
      clauses.push("(" + textCols.map(c => "CAST(" + c + " AS TEXT) LIKE ?").join(" OR ") + ")");
      args.push(...textCols.map(() => "%" + q + "%"));
    }
  }
  if (clauses.length) sql += " WHERE " + clauses.join(" AND ");
  sql += ` ORDER BY ${def.composite ? def.pk : def.pkType === "text" ? def.pk : "id"} DESC`;
  /* a filtered query is answering a specific question, so it may need rows that a capped
     scan would miss; an explicit filter lifts the cap, an unfiltered browse keeps it. */
  const filtered = q || Object.keys(whereRaw).length;
  sql += " LIMIT " + (filtered ? Math.min(5000, Math.max(500, opts.limit || 500)) : 500);
  const rows = all(sql, ...args);
  if (def.composite) rows.forEach(r => { r.id = String(r[def.pk]) + "|" + String(r[def.pk2]); });
  return rows;
}
/* The Global Platform mirror of listEntities. Same definitions, same whitelist, same
   parameterization — never a second copy of the field list. Two differences, both
   structural: (1) tenant_id is SELECTed and stamped onto every row so the global console
   can render a Store column, and (2) the tenant predicate is optional, so the platform
   reads *across* stores by default and narrows to one store only when asked. This single
   reader is what makes every entity-backed store capability visible in the Platform
   Console with zero per-capability code (Knowledge-Once). */
function listEntitiesGlobal(key, opts) {
  opts = opts || {};
  const tenantId = opts.tenantId != null ? Number(opts.tenantId) : null;
  const defs = allEntities(tenantId);
  const def = defs[key];
  if (!def) return null;
  const q = opts.q != null ? String(opts.q).trim() : "";
  const whereRaw = opts.where && typeof opts.where === "object" ? { ...opts.where } : {};
  delete whereRaw.tenant_id;
  const multi = !def.platformOnly && !def.noTenant;
  if (def.storage === "json") {
    let rows = all("SELECT * FROM entity_data WHERE entity=? " + (multi ? "AND (tenant_id IS NOT NULL" + (tenantId != null ? " AND tenant_id=?" : "") + ")" : ""), key, ...(multi && tenantId != null ? [tenantId] : []));
    let out = rows.map(r => ({ id: r.id, ...(multi ? { tenant_id: r.tenant_id } : {}), ...JSON.parse(r.data || "{}"), created_at: r.created_at }));
    const wkeys = Object.keys(whereRaw);
    if (wkeys.length) out = out.filter(r => wkeys.every(k => String(r[k]) === String(whereRaw[k])));
    if (q) { const cols = def.fields.filter(f => f.list && (f.type === "text" || f.type === "textarea")).map(f => f.key);
      if (cols.length) out = out.filter(r => cols.some(c => String(r[c] || "").toLowerCase().includes(q.toLowerCase()))); }
    return out;
  }
  const fieldCols = multi ? ["tenant_id"] : [];
  fieldCols.push(...def.fields.map(f => (f.col || f.key) + (f.col && f.col !== f.key ? " AS " + f.key : "")));
  if (!def.composite && def.pk && !def.fields.some(f => (f.col || f.key) === def.pk)) fieldCols.unshift(def.pk);
  const cols = fieldCols.join(",");
  const orderKey = def.composite ? def.pk : def.pkType === "text" ? def.pk : "id";
  /* one shared, parameterized query builder — the filtered and the per-store browse paths
     below resolve to the same SQL, so the whitelist is never duplicated */
  const fetch = (tid, limit) => {
    let sql = `SELECT ${cols}${def.composite ? `,${def.pk2} as _pk2` : ""} FROM ${def.table}`;
    const args = [];
    const clauses = [];
    if (multi && tid != null) { clauses.push("tenant_id=?"); args.push(tid); }
    if (opts.hideDeleted) clauses.push("deleted_at IS NULL");
    for (const [k, v] of Object.entries(whereRaw)) {
      const col = def.fields.find(f => f.key === k);
      if (col) { clauses.push((col.col || col.key) + "=?"); args.push(v); }
    }
    if (q) {
      const textCols = def.fields.filter(f => f.list && (f.type === "text" || f.type === "textarea")).map(f => f.col || f.key);
      if (textCols.length) {
        clauses.push("(" + textCols.map(c => "CAST(" + c + " AS TEXT) LIKE ?").join(" OR ") + ")");
        args.push(...textCols.map(() => "%" + q + "%"));
      }
    }
    if (clauses.length) sql += " WHERE " + clauses.join(" AND ");
    sql += ` ORDER BY ${orderKey} DESC LIMIT ${limit}`;
    return all(sql, ...args);
  };
  const filtered = q || Object.keys(whereRaw).length;
  /* a *global* browse must represent every store: bounding per store (not globally) keeps
     a large catalogue from crowding the other stores out of the platform view. A filtered
     query is answering one specific question, so it scans across stores under one cap. */
  if (multi && tenantId == null && !filtered) {
    const tids = all("SELECT id FROM tenants ORDER BY id").map(r => r.id);
    const per = Math.max(25, Math.min(500, Math.ceil((opts.limit || 500) / Math.max(1, tids.length))));
    let rows = [];
    for (const tid of tids) rows = rows.concat(fetch(tid, per));
    if (def.composite) rows.forEach(r => { r.id = String(r[def.pk]) + "|" + String(r[def.pk2]); });
    return rows;
  }
  const limit = (filtered || tenantId != null) ? Math.min(5000, Math.max(500, opts.limit || 500)) : 500;
  const rows = fetch(tenantId, limit);
  if (def.composite) rows.forEach(r => { r.id = String(r[def.pk]) + "|" + String(r[def.pk2]); });
  return rows;
}
/* Generate structured Universal ID (UID)
 format: PREFIX-TENANT-SEC-UNIQUE
 Example: TXN-LX01-P2-a1b2c3d4e5f6g7h8 */
function generateUID(tenant, prefix, security = 'P2') {
  const unique = crypto.randomBytes(8).toString('hex');
  return `${prefix}-${tenant}-${security}-${unique}`;
}
function createEntity(tenantId, key, row) {
  const def = allEntities(tenantId)[key];
  if (!def) return { error: "Unknown entity" };
  const errs = validate(def, row);
  if (errs.length) return { error: errs.join("; ") };
  if (def.storage === "json") {
    const r = run("INSERT INTO entity_data(tenant_id,entity,data) VALUES(?,?,?)", tenantId, key, JSON.stringify(row));
    return { id: Number(r.lastInsertRowid) };
  }
  const cols = def.noTenant ? [] : ["tenant_id"], vals = def.noTenant ? [] : [tenantId];
  if (def.pkType === "text" || def.composite) {
    if (!row[def.pk]) { 
      if (def.composite) return { error: "Composite key required" }; 
      // Generate UID if uid field exists in entity
      if (def.fields.some(f => f.key === 'uid')) {
        const prefix = def.table === "products" ? "PROD" : def.table === "orders" ? "ORD" : 
                       def.table === "users" ? "USR" : def.table === "invoices" ? "INV" : "ENT";
        const sec = def.sec || 'P2';
        row[def.pk] = generateUID(String(tenantId), prefix, sec);
      } else {
        row[def.pk] = (def.table === "products" ? "LX" : "K") + crypto.randomBytes(4).toString("hex").toUpperCase();
      }
    }
    cols.push(def.pk); vals.push(String(row[def.pk]));
  }
  for (const f of def.fields) {
    if (f.readonly || f.key === def.pk) continue;
    if (row[f.key] !== undefined) { cols.push(f.col || f.key); vals.push(coerce(f, row[f.key])); }
  }
  /* an operator-authored row is owned outright: the seed never rewrites it */
  if (def.editedStamp) { cols.push("edited"); vals.push(1); }
  const ph = cols.map(() => "?").join(",");
  try { run(`INSERT INTO ${def.table}(${cols.join(",")}) VALUES(${ph})`, ...vals); }
  /* an import's bad row must be REPORTED, not fatal. Any integrity error — a NOT NULL the
     console's field list doesn't mirror, a FK the DB enforces but the form can't express —
     becomes a per-row rejection so the good rows still land and the caller sees which row
     failed and why. Throwing here would abort the whole request over one row (import rolled
     back every good record with it) */
  catch (e) {
    if (/UNIQUE/.test(e.message)) return { error: "Record already exists (duplicate key)" };
    if (/(NOT NULL|FOREIGN KEY|CHECK|CONSTRAINT)/i.test(e.message)) return { error: e.message.replace(/^Error: /, "") };
    throw e;
  }
  propagate(key);
  return { id: def.composite ? row[def.pk] + "|" + row[def.pk2] : (def.pkType === "text" ? row[def.pk] : "created") };
}
/* the write path is where a registry entry becomes live everywhere it is needed. Adding a
   country in Country Master used to stop at the `countries` row: its currency, FX quote and
   availability links to every global provider appeared only on the next boot. Reconciling
   here is what makes "add it and it is everywhere" true at the moment of the write.
   Guarded per-key and fault-tolerant — a reconciliation failure must never block the write
   itself, which already succeeded; the next boot reconciles again. */
function propagate(key) {
  try {
    if (key === "country" || key === "currency" || key === "provider_def" || key === "provider_availability")
      require("./registry.js").reconcileDerived();
    /* a link IS the relationship primitive: writing or removing one must re-derive the product
       projection the storefront reads, or an edge created in the platform console appears only
       after a restart. reconcileLinks is idempotent and handles both directions, so this is safe
       on a warm DB and costs a few writes on a cold one. */
    if (key === "link") require("./registry.js").reconcileLinks();
  } catch (e) { console.error("entity reconcile failed:", e.message); }
}
function updateEntity(tenantId, key, id, row) {
  const def = allEntities(tenantId)[key];
  if (!def) return { error: "Unknown entity" };
  const errs = validate(def, row, true);
  if (errs.length) return { error: errs.join("; ") };
  if (def.storage === "json") {
    /* the write half of the read rule: a store-scoped json entity is written only on the
       store's OWN rows — by id alone, one store could rewrite another's. (Json records also
       carry lifecycle keys such as status/certified that are not declared fields, so the
       row is merged as given.) */
    const scoped = !def.platformOnly && !def.noTenant;
    const ex = get("SELECT * FROM entity_data WHERE id=? AND entity=?" + (scoped ? " AND tenant_id=?" : ""), Number(id), key, ...(scoped ? [tenantId] : []));
    if (!ex) return { error: "Not found", code: 404 };
    run("UPDATE entity_data SET data=? WHERE id=?", JSON.stringify({ ...JSON.parse(ex.data || "{}"), ...row }), ex.id);
    return { ok: true };
  }
  const sets = [], vals = [];
  for (const f of def.fields) {
    if (f.readonly || row[f.key] === undefined) continue;
    sets.push((f.col || f.key) + "=?"); vals.push(coerce(f, row[f.key]));
  }
  /* a console write claims the row: revisioned seeds read `edited` and stand down */
  if (def.editedStamp) sets.push("edited=1");
  if (!sets.length) return { ok: true };
  const where = (def.platformOnly || def.noTenant) ? "" : "tenant_id=? AND ";
  const wargs = (def.platformOnly || def.noTenant) ? [] : [tenantId];
  const pkCond = def.composite ? `${def.pk}=? AND ${def.pk2}=?` : `${def.pk}=?`;
  const pkVals = def.composite ? String(id).split("|") : [def.pkType === "text" ? String(id) : Number(id)];
  const r = run(`UPDATE ${def.table} SET ${sets.join(",")} WHERE ${where}${pkCond}`, ...vals, ...wargs, ...pkVals);
  if (!r.changes) return { error: "Not found", code: 404 };
  propagate(key);
  return { ok: true };
}
function deleteEntity(tenantId, key, id) {
  const def = allEntities(tenantId)[key];
  if (!def) return { error: "Unknown entity" };
  if (def.storage === "json") {
    const scoped = !def.platformOnly && !def.noTenant;
    const r = run("DELETE FROM entity_data WHERE id=? AND entity=?" + (scoped ? " AND tenant_id=?" : ""), Number(id), key, ...(scoped ? [tenantId] : []));
    if (!r.changes) return { error: "Not found", code: 404 };
    return { ok: true };
  }
  const where = (def.platformOnly || def.noTenant) ? "" : "tenant_id=? AND ";
  const wargs = (def.platformOnly || def.noTenant) ? [] : [tenantId];
  const pkCond = def.composite ? `${def.pk}=? AND ${def.pk2}=?` : `${def.pk}=?`;
  const pkVals = def.composite ? String(id).split("|") : [def.pkType === "text" ? String(id) : Number(id)];
  run(`DELETE FROM ${def.table} WHERE ${where}${pkCond}`, ...wargs, ...pkVals);
  propagate(key);
  return { ok: true };
}

module.exports = { ENTITY_DEFS, allEntities, customEntityDefs, listEntities, listEntitiesGlobal, createEntity, updateEntity, deleteEntity, validate, coerce };
