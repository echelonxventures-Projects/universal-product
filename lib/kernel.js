/* LUXORA Platform — the kernel (FOUNDATIONS K01–K12), first slice: kinds, nodes, identifiers,
   hierarchies, typed attributes, bi-temporal versions and the event log.

   Every domain builds on these parts instead of its own tables: a place, a currency, a language,
   a store or a person is a NODE of a declared KIND; where it sits is a PLACEMENT in a named
   HIERARCHY; its codes are IDENTIFIERS in declared schemes; its facts are ATTRIBUTE versions
   with valid time and recorded time; and every change is one EVENT in one hash-chained log.
   No domain vocabulary appears here — a kind, a scheme or a hierarchy is data a person or an
   agent declares, with no limit on count or depth.

   Recorded time is the event sequence: each write appends its event first and stamps its rows
   with that sequence number, so "what did we believe at T" is "rows recorded at or before the
   last event at T and not yet superseded then". Nothing is overwritten; superseding closes a
   row's recorded interval and writes the replacement.

   The parts have different owners (lib/../_registry/codebase.json): kinds and attributes are
   Registry's, nodes and identifiers Identity's, hierarchies Relationship's, versions
   Evolution's and the event log Runtime's. */
"use strict";

const crypto = require("crypto");
const { exec, run, get, all, USE_PG } = require("./db.js");
const sec = require("./security.js");
const SEED = require("./seed/kernel.json");
const DOMAINS = new Set(require("../_registry/domains.json").domains.map(d => d.name));

const EV = SEED.events;
const KEY_RE = new RegExp(SEED.limits.keyPattern);
const HOLDER_RE = new RegExp(SEED.limits.holderPattern);
const J = (v, d) => { try { return v == null || v === "" ? d : JSON.parse(v); } catch (e) { return d; } };
const fail = msg => { const e = new Error(msg); e.status = 400; throw e; };

/* ============================== storage ============================== */
let ready = false;
function ensureTables() {
  if (ready) return;
  /* Runtime: the event log. seq is recorded time for every other table. */
  run(`CREATE TABLE IF NOT EXISTS k_events (
    seq INTEGER PRIMARY KEY AUTOINCREMENT, at TEXT NOT NULL, type TEXT NOT NULL,
    namespace TEXT NOT NULL, subject TEXT, actor TEXT, payload TEXT NOT NULL DEFAULT '{}',
    prev_hash TEXT NOT NULL, hash TEXT NOT NULL)`);
  run(`CREATE INDEX IF NOT EXISTS ix_k_events_subject ON k_events(subject, seq)`);
  run(`CREATE INDEX IF NOT EXISTS ix_k_events_at ON k_events(at)`);
  /* Registry: kinds (one row per recorded declaration; the open row is current) */
  run(`CREATE TABLE IF NOT EXISTS k_kinds (
    id INTEGER PRIMARY KEY AUTOINCREMENT, namespace TEXT NOT NULL, kind TEXT NOT NULL,
    owner TEXT NOT NULL, spec TEXT NOT NULL, rec_from INTEGER NOT NULL, rec_to INTEGER)`);
  run(`CREATE INDEX IF NOT EXISTS ix_k_kinds ON k_kinds(namespace, kind, rec_to)`);
  /* Identity: nodes and identifiers */
  run(`CREATE TABLE IF NOT EXISTS k_nodes (
    uid TEXT PRIMARY KEY, namespace TEXT NOT NULL, kind TEXT NOT NULL, rec_from INTEGER NOT NULL)`);
  run(`CREATE INDEX IF NOT EXISTS ix_k_nodes_kind ON k_nodes(namespace, kind)`);
  run(`CREATE TABLE IF NOT EXISTS k_identifiers (
    id INTEGER PRIMARY KEY AUTOINCREMENT, node TEXT NOT NULL, scheme TEXT NOT NULL, value TEXT NOT NULL,
    valid_from TEXT NOT NULL, valid_to TEXT, rec_from INTEGER NOT NULL, rec_to INTEGER)`);
  run(`CREATE INDEX IF NOT EXISTS ix_k_ident_value ON k_identifiers(scheme, value, rec_to)`);
  run(`CREATE INDEX IF NOT EXISTS ix_k_ident_node ON k_identifiers(node, rec_to)`);
  /* Relationship: hierarchies and placements */
  run(`CREATE TABLE IF NOT EXISTS k_hierarchies (
    id INTEGER PRIMARY KEY AUTOINCREMENT, namespace TEXT NOT NULL, hierarchy TEXT NOT NULL,
    owner TEXT NOT NULL, spec TEXT NOT NULL, rec_from INTEGER NOT NULL, rec_to INTEGER)`);
  run(`CREATE INDEX IF NOT EXISTS ix_k_hier ON k_hierarchies(namespace, hierarchy, rec_to)`);
  run(`CREATE TABLE IF NOT EXISTS k_placements (
    id INTEGER PRIMARY KEY AUTOINCREMENT, hierarchy TEXT NOT NULL, node TEXT NOT NULL, parent TEXT,
    valid_from TEXT NOT NULL, valid_to TEXT, rec_from INTEGER NOT NULL, rec_to INTEGER)`);
  run(`CREATE INDEX IF NOT EXISTS ix_k_place_parent ON k_placements(hierarchy, parent, rec_to)`);
  run(`CREATE INDEX IF NOT EXISTS ix_k_place_node ON k_placements(hierarchy, node, rec_to)`);
  /* Evolution: attribute versions, bi-temporal */
  run(`CREATE TABLE IF NOT EXISTS k_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, node TEXT NOT NULL, attrs TEXT NOT NULL,
    valid_from TEXT NOT NULL, valid_to TEXT, rec_from INTEGER NOT NULL, rec_to INTEGER)`);
  run(`CREATE INDEX IF NOT EXISTS ix_k_versions ON k_versions(node, rec_to, valid_from)`);
  /* Evolution: a node's own state (active, hidden, archived — lib/seed/kernel.json lifecycle.nodeStates) */
  run(`CREATE TABLE IF NOT EXISTS k_node_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT, node TEXT NOT NULL, state TEXT NOT NULL, rec_from INTEGER NOT NULL, rec_to INTEGER)`);
  run(`CREATE INDEX IF NOT EXISTS ix_k_node_states ON k_node_states(node, rec_to)`);
  /* K11: a kind, a hierarchy or a node may belong to a scope node inside its namespace (a site
     inside a tenant, a region inside a publisher); null is the whole namespace */
  for (const t of ["k_kinds", "k_hierarchies", "k_nodes"]) ensureColumn(t, "scope", "TEXT");
  ready = true;
}
/* adds a column an install that predates it lacks, read from the catalogue — never by a failing
   select, which would abort the surrounding transaction on Postgres */
function ensureColumn(table, col, decl) {
  const cols = USE_PG
    ? all("SELECT column_name AS name FROM information_schema.columns WHERE table_name=?", table)
    : all(`PRAGMA table_info(${table})`);
  if (!cols.some(c => c.name === col)) exec(`ALTER TABLE ${table} ADD COLUMN ${col} ${decl}`);
}

/* one write = one transaction; nested calls join the outer one */
let depth = 0;
function tx(fn) {
  ensureTables();
  if (depth) { depth++; try { return fn(); } finally { depth--; } }
  /* the write lock is taken up front, so two processes sharing a database queue for it instead
     of both reading the log's last hash and one failing at commit */
  exec(USE_PG ? "BEGIN" : "BEGIN IMMEDIATE"); depth = 1;
  try { const out = fn(); exec("COMMIT"); return out; }
  catch (e) { try { exec("ROLLBACK"); } catch (_) { } throw e; }
  finally { depth = 0; }
}

/* a dry run: fn runs in a transaction that is always undone; the answer is its result or its error */
function dryRun(fn) {
  ensureTables();
  if (depth) fail("A dry run cannot start inside another write");
  exec("BEGIN"); depth = 1;
  try { return { ok: true, result: fn() }; }
  catch (e) { return { ok: false, error: e.message }; }
  finally { try { exec("ROLLBACK"); } catch (_) { } depth = 0; }
}

/* ============================== time ============================== */
/* valid time is an ISO-8601 instant; null valid_to is "until further notice" */
function instant(t, label) {
  if (t == null || t === "") return null;
  const d = t instanceof Date ? t : new Date(t);
  if (isNaN(d.getTime())) fail(label + " is not a valid instant: " + t);
  return d.toISOString();
}
const nowIso = () => new Date().toISOString();
const before = (a, b) => b == null ? a != null : a != null && a < b;     /* a < b, null = +∞ */
const minEnd = (a, b) => a == null ? b : b == null ? a : (a < b ? a : b);
const maxStart = (a, b) => a > b ? a : b;
function window(o) {
  const from = instant(o && o.validFrom, "validFrom") || nowIso();
  const to = instant(o && o.validTo, "validTo");
  if (to != null && !before(from, to)) fail("validTo must be after validFrom");
  return { from, to };
}
/* recorded time: a sequence number, or the last event at or before an instant */
function recordedSeq(r) {
  if (r == null) return null;
  if (typeof r === "number") return r;
  const row = get("SELECT MAX(seq) AS s FROM k_events WHERE at<=?", instant(r, "recorded"));
  return row && row.s != null ? row.s : 0;
}
/* the SQL that selects rows believed at recorded seq s (current belief when s is null) */
const believed = s => s == null ? { sql: "rec_to IS NULL", args: [] } : { sql: "rec_from<=? AND (rec_to IS NULL OR rec_to>?)", args: [s, s] };
const validAt = at => ({ sql: "valid_from<=? AND (valid_to IS NULL OR valid_to>?)", args: [at, at] });

/* ============================== K08 events (Runtime) ============================== */
const canon = v => JSON.stringify(v, (k, x) => x && typeof x === "object" && !Array.isArray(x) ? Object.keys(x).sort().reduce((o, key) => (o[key] = x[key], o), {}) : x);
function append(type, o) {
  ensureTables();
  const at = nowIso();
  const space = (o && o.namespace) || SEED.defaultNamespace;
  const payload = canon((o && o.payload) || {});
  const prev = get("SELECT hash FROM k_events ORDER BY seq DESC LIMIT 1");
  const prevHash = prev ? prev.hash : "";
  const hash = crypto.createHash("sha256").update([prevHash, at, type, space, (o && o.subject) || "", (o && o.actor) || "", payload].join("\n")).digest("hex");
  const r = run("INSERT INTO k_events(at,type,namespace,subject,actor,payload,prev_hash,hash) VALUES(?,?,?,?,?,?,?,?)",
    at, String(type), space, (o && o.subject) || null, (o && o.actor) || null, payload, prevHash, hash);
  return Number(r.lastInsertRowid);
}
function events(q) {
  ensureTables();
  q = q || {};
  const where = [], args = [];
  if (q.since != null) { where.push("seq>?"); args.push(Number(q.since)); }
  if (q.subject) { where.push("subject=?"); args.push(String(q.subject)); }
  if (q.type) { where.push("type=?"); args.push(String(q.type)); }
  if (q.namespace) { where.push("namespace=?"); args.push(String(q.namespace)); }
  const limit = Math.min(Number(q.limit) || SEED.limits.eventPage, SEED.limits.eventPage);
  return all(`SELECT * FROM k_events ${where.length ? "WHERE " + where.join(" AND ") : ""} ORDER BY seq LIMIT ${limit}`, ...args)
    .map(e => ({ ...e, payload: J(e.payload, {}) }));
}
/* the chain proves no event was edited, removed or reordered */
function verifyEvents() {
  ensureTables();
  let prevHash = "", count = 0;
  for (const e of all("SELECT * FROM k_events ORDER BY seq")) {
    const hash = crypto.createHash("sha256").update([prevHash, e.at, e.type, e.namespace, e.subject || "", e.actor || "", e.payload].join("\n")).digest("hex");
    if (e.prev_hash !== prevHash || e.hash !== hash) return { ok: false, count, brokenAt: e.seq };
    prevHash = e.hash; count++;
  }
  return { ok: true, count };
}

/* ============================== listing ============================== */
/* listings (node lists, children, subtrees, views, coordinate lookups) show only nodes in a listed
   state; hidden and archived nodes drop out unless o.includeHidden. Paths, ancestors and history
   keep the whole structure, so nothing about the past is lost by hiding. */
const NS_STATES = SEED.lifecycle.nodeStates;
const LISTED = new Set(NS_STATES.listed);
function listed(uids, o) {
  if ((o && o.includeHidden) || !uids.length) return uids;
  ensureTables();
  const b = believed(recordedSeq(o && o.recorded));
  const st = new Map();
  for (let i = 0; i < uids.length; i += 500) {
    const part = uids.slice(i, i + 500);
    for (const r of all(`SELECT node, state FROM k_node_states WHERE node IN (${part.map(() => "?").join(",")}) AND ${b.sql}`, ...part, ...b.args)) st.set(r.node, r.state);
  }
  return uids.filter(u => LISTED.has(st.has(u) ? st.get(u) : NS_STATES.initial));
}

/* ============================== K01 kinds + K06 attributes (Registry) ============================== */
const VALUE_TYPES = new Set(SEED.valueTypes.map(t => t.key));
/* value types whose value is text in many languages, answered in one when a language is asked */
const LOCALISED = new Set(SEED.valueTypes.filter(t => t.localised).map(t => t.key));
const NAMESPACES = new Set(SEED.namespaces);
/* each declared value type's check — the declarations live in lib/seed/kernel.json */
const TYPE_CHECKS = {
  text: v => typeof v === "string",
  number: v => typeof v === "number" && isFinite(v),
  integer: v => Number.isInteger(v),
  boolean: v => typeof v === "boolean",
  instant: v => typeof v === "string" && !isNaN(new Date(v).getTime()),
  node: v => typeof v === "string" && !!get("SELECT 1 AS x FROM k_nodes WHERE uid=?", v),
  list: v => Array.isArray(v),
  record: v => !!v && typeof v === "object" && !Array.isArray(v),
  /* text in languages the Expression registry names; at least one */
  expression: v => !!v && typeof v === "object" && !Array.isArray(v) && Object.keys(v).length > 0
    && Object.entries(v).every(([l, t]) => typeof t === "string" && !!expression().language(l) && expression().base(l) === l),
  /* an amount in a unit, the unit being a node (Measure declares the unit kinds and conversions) */
  quantity: v => !!v && typeof v === "object" && typeof v.amount === "number" && isFinite(v.amount)
    && typeof v.unit === "string" && !!get("SELECT 1 AS x FROM k_nodes WHERE uid=?", v.unit)
};
const expression = () => require("./expression.js");

/* attribute constraints (lib/seed/kernel.json constraints): each declared operator's check, and
   the shape its parameter must have. A check is (value, param, { uid, kind, key }) → true when kept */
const CONSTRAINT_DECL = new Map((SEED.constraints || []).map(c => [c.key, c]));
const PARAM_CHECKS = {
  number: p => typeof p === "number" && isFinite(p),
  integer: p => Number.isInteger(p) && p >= 0,
  pattern: p => { try { new RegExp(p); return typeof p === "string"; } catch (e) { return false; } },
  list: p => Array.isArray(p) && p.length > 0,
  key: p => typeof p === "string" && KEY_RE.test(p),
  boolean: p => p === true
};
/* is the node of the kind, or of a kind extending it? */
function refersToKind(uid, kind) {
  const n = get("SELECT namespace, kind, scope FROM k_nodes WHERE uid=?", uid);
  const k = n && kindOf(n.kind, n.namespace, null, n.scope);
  return !!k && k.lineage.includes(kind);
}
/* does no other current node of the same kind and namespace hold this value? */
function heldOnlyBy(uid, key, v) {
  const n = nodeRow(uid);
  return !all(`SELECT v.attrs FROM k_versions v JOIN k_nodes n ON n.uid=v.node
    WHERE n.namespace=? AND n.kind=? AND v.node<>? AND v.rec_to IS NULL`, n.namespace, n.kind, uid).some(r => J(r.attrs, {})[key] === v);
}
const sizeOf = v => Array.isArray(v) ? v.length : [...String(v)].length;
const CONSTRAINTS = {
  min: (v, p) => v >= p,
  max: (v, p) => v <= p,
  minLength: (v, p) => sizeOf(v) >= p,
  maxLength: (v, p) => sizeOf(v) <= p,
  pattern: (v, p) => new RegExp(p).test(v),
  oneOf: (v, p) => p.includes(v),
  nodeKind: (v, p) => refersToKind(typeof v === "string" ? v : v.unit, p),
  unique: (v, p, c) => heldOnlyBy(c.uid, c.key, v),
  languages: (v, p) => p.every(l => typeof v[l] === "string" && v[l].trim() !== "")
};
/* checks one value against a value type and its rules — the one check every attribute, fact and
   setting goes through. c names the value ({ label }) and, for a node's attribute, the node
   ({ uid, kind, key }) that a rule such as unique needs */
function checkValue(type, constraints, v, c) {
  c = c || {};
  const label = c.label || c.key || "value";
  if (!VALUE_TYPES.has(type) || !TYPE_CHECKS[type]) fail("Unknown value type for " + label + ": " + type);
  if (!TYPE_CHECKS[type](v)) fail(`${label} must be ${type}`);
  for (const [op, param] of Object.entries(constraints || {})) {
    const d = CONSTRAINT_DECL.get(op);
    if (!d || !CONSTRAINTS[op] || !d.types.includes(type) || !PARAM_CHECKS[d.param](param)) fail(`Rule ${op} does not apply to ${label}`);
    if (d.needsNode && !c.uid) fail(`Rule ${op} applies only to a node's own attributes (${label})`);
    if (!CONSTRAINTS[op](v, param, c)) fail(`${label} breaks the rule "${d.label}" (${JSON.stringify(param)})`);
  }
  return v;
}

/* identifier check rules (lib/seed/kernel.json checkRules): each declared rule's check digit */
const digits = v => String(v).replace(/[^0-9X]/gi, "").toUpperCase();
const mod10 = (ds, w) => [...ds].reverse().reduce((t, d, i) => t + Number(d) * w(i), 0) % 10;
const CHECK_RULES = {
  gs1: v => /^\d+$/.test(v) && mod10(v.slice(0, -1), i => i % 2 ? 1 : 3) === (10 - Number(v.slice(-1))) % 10,
  luhn: v => /^\d+$/.test(v) && [...v].reverse().reduce((t, d, i) => { const x = Number(d) * (i % 2 ? 2 : 1); return t + (x > 9 ? x - 9 : x); }, 0) % 10 === 0,
  isbn: v => { const d = digits(v); if (d.length === 13) return CHECK_RULES.gs1(d); if (d.length !== 10) return false;
    return [...d].reduce((t, ch, i) => t + (ch === "X" ? 10 : Number(ch)) * (10 - i), 0) % 11 === 0; },
  issn: v => { const d = digits(v); return d.length === 8 && [...d].reduce((t, ch, i) => t + (ch === "X" ? 10 : Number(ch)) * (8 - i), 0) % 11 === 0; },
  cas: v => { const d = String(v).replace(/-/g, ""); if (!/^\d+$/.test(d)) return false;
    const body = d.slice(0, -1); return [...body].reverse().reduce((t, ch, i) => t + Number(ch) * (i + 1), 0) % 10 === Number(d.slice(-1)); }
};
const CHECK_DECL = new Set((SEED.checkRules || []).map(r => r.key));
/* a scheme's declaration, when one is declared: a node of the declaring kind whose code in the
   declaring scheme is the scheme's key (lib/seed/kernel.json identity.declaredBy) */
function schemeRule(scheme) {
  const by = SEED.identity.declaredBy;
  if (!by || scheme === by) return null;
  const uid = resolveIdentifier(by, scheme);
  return uid ? attributes(uid) : null;
}
function checkCode(scheme, value) {
  const d = schemeRule(scheme);
  if (!d) return;
  if (d.case === "upper" && value !== value.toUpperCase()) fail(`${scheme} ${value} must be upper case`);
  if (d.pattern && !new RegExp(d.pattern).test(value)) fail(`${value} is not a valid ${scheme} code`);
  if (d.check) {
    if (!CHECK_DECL.has(d.check) || !CHECK_RULES[d.check]) fail(`Scheme ${scheme} names an unknown check rule: ${d.check}`);
    if (!CHECK_RULES[d.check](value)) fail(`${value} fails the ${scheme} check digit`);
  }
}
/* a namespace is a declared type, optionally with its holder: "platform", "tenant:42", "publisher:acme" */
const ns = n => {
  const v = String(n || SEED.defaultNamespace), i = v.indexOf(":");
  const type = i < 0 ? v : v.slice(0, i), holder = i < 0 ? "" : v.slice(i + 1);
  if (!NAMESPACES.has(type) || (i >= 0 && !HOLDER_RE.test(holder))) fail("Unknown namespace: " + v);
  return v;
};
const keyOk = (k, label) => { if (typeof k !== "string" || !KEY_RE.test(k)) fail(label + " must match " + SEED.limits.keyPattern + ": " + k); return k; };

function normaliseConstraints(a) {
  const out = {};
  for (const [op, param] of Object.entries(a.constraints || {})) {
    const c = CONSTRAINT_DECL.get(op);
    if (!c || !CONSTRAINTS[op]) fail("Unknown constraint on " + a.key + ": " + op);
    if (!c.types.includes(a.type)) fail(`Constraint ${op} does not apply to ${a.type} (${a.key})`);
    if (!PARAM_CHECKS[c.param](param)) fail(`Constraint ${op} on ${a.key} needs a ${c.param}`);
    if (op === "unique" && a.sensitive) fail("A sensitive attribute cannot be unique: " + a.key);
    out[op] = param;
  }
  return out;
}
function normaliseKind(d) {
  const attributes = (d.attributes || []).map(a => {
    keyOk(a.key, "Attribute key");
    if (!VALUE_TYPES.has(a.type)) fail("Unknown value type for " + a.key + ": " + a.type);
    return { key: a.key, type: a.type, required: !!a.required, sensitive: !!a.sensitive, label: a.label || a.key, constraints: normaliseConstraints(a) };
  });
  const seen = new Set();
  for (const a of attributes) { if (seen.has(a.key)) fail("Attribute declared twice: " + a.key); seen.add(a.key); }
  /* parents, root and schemes left undeclared are inherited from the kind this one extends */
  const parents = d.parents == null ? null : d.parents.map(p => p === "*" ? p : keyOk(p, "Parent kind"));
  const schemes = (d.schemes || []).map(s => keyOk(s, "Identifier scheme"));
  return { label: d.label || d.kind, extends: d.extends == null ? null : keyOk(d.extends, "Extended kind"), attributes, parents, root: d.root == null ? null : d.root !== false, schemes, shape: d.shape == null ? null : !!d.shape };
}
/* a kind's effective declaration: its own over every kind it extends, nearest first. An attribute
   redeclared down the line keeps its type and may only add constraints or become required */
function effective(own, chain) {
  const lineage = [own.kind, ...chain.map(c => c.kind)];
  const byKey = new Map();
  for (const c of [...chain].reverse().concat([own])) for (const a of c.attributes) {
    const was = byKey.get(a.key);
    if (was && was.type !== a.type) fail(`Kind ${own.kind}: ${a.key} is ${was.type} in a kind it extends, so it cannot be ${a.type}`);
    byKey.set(a.key, was ? { ...was, ...a, required: was.required || a.required, sensitive: was.sensitive || a.sensitive, constraints: { ...was.constraints, ...a.constraints } } : a);
  }
  const pick = f => [own, ...chain].map(c => c[f]).find(v => v != null);
  return {
    ...own, lineage, attributes: [...byKey.values()],
    parents: pick("parents") || [], root: pick("root") !== false, shape: !!pick("shape"),
    schemes: [...new Set([own, ...chain].flatMap(c => c.schemes || []))]
  };
}
function defineKind(d, actor) {
  d = d || {};
  const namespace = ns(d.namespace), kind = keyOk(d.kind, "Kind"), scope = scopeOk(d.scope);
  if (!DOMAINS.has(d.owner)) fail("A kind needs an owning domain from the register: " + d.owner);
  const spec = normaliseKind(d);
  if (spec.extends) {
    if (spec.extends === kind) fail("A kind cannot extend itself");
    const base = kindOf(spec.extends, namespace, null, scope);
    if (!base) fail("Unknown kind to extend: " + spec.extends);
    if (base.lineage.includes(kind)) fail(`Kind ${kind} would extend itself through ${spec.extends}`);
    effective({ kind, ...spec }, [base]);     /* a conflicting redeclaration fails before anything is written */
  }
  return tx(() => {
    const seq = append(EV.kindDefined, { namespace, subject: kind, actor, payload: { owner: d.owner, scope, spec } });
    run(`UPDATE k_kinds SET rec_to=? WHERE namespace=? AND kind=? AND ${scope == null ? "scope IS NULL" : "scope=?"} AND rec_to IS NULL`, seq, namespace, kind, ...(scope == null ? [] : [scope]));
    run("INSERT INTO k_kinds(namespace,kind,owner,spec,scope,rec_from) VALUES(?,?,?,?,?,?)", namespace, kind, d.owner, JSON.stringify(spec), scope, seq);
    return kindOf(kind, namespace, null, scope);
  });
}
/* a scope is a node; null is the whole namespace */
function scopeOk(scope) {
  if (scope == null || scope === "") return null;
  if (!nodeRow(scope)) fail("A scope must be a node: " + scope);
  return String(scope);
}
/* the row declaring a kind: at the scope, else across the namespace, else the platform's —
   master kinds belong to the platform and every namespace uses them */
function kindRow(kind, namespace, b, scope) {
  const q = `SELECT * FROM k_kinds WHERE namespace=? AND kind=? AND ${b.sql}`;
  return (scope ? get(q + " AND scope=?", ns(namespace), kind, ...b.args, scope) : null)
    || get(q + " AND scope IS NULL", ns(namespace), kind, ...b.args)
    || get(q + " AND scope IS NULL", SEED.defaultNamespace, kind, ...b.args);
}
const kindOwn = r => ({ namespace: r.namespace, kind: r.kind, owner: r.owner, scope: r.scope || null, ...J(r.spec, {}) });
function kindOf(kind, namespace, recorded, scope) {
  ensureTables();
  const b = believed(recordedSeq(recorded));
  const r = kindRow(kind, namespace, b, scope);
  if (!r) return null;
  const own = kindOwn(r), chain = [];
  for (let next = own.extends; next; ) {
    if (chain.length >= SEED.limits.maxExtends || chain.some(c => c.kind === next) || next === own.kind) fail("Kind " + kind + " extends in a loop");
    const p = kindRow(next, namespace, b, scope);
    if (!p) fail(`Kind ${kind} extends ${next}, which is not declared`);
    const c = kindOwn(p); chain.push(c); next = c.extends;
  }
  return effective(own, chain);
}
/* the kinds declared in a namespace (with o.scope: those across it and those at that scope) */
function kinds(namespace, o) {
  ensureTables();
  const scope = o && o.scope ? String(o.scope) : null;
  return all(`SELECT * FROM k_kinds WHERE namespace=? AND rec_to IS NULL AND (scope IS NULL${scope ? " OR scope=?" : ""}) ORDER BY kind`, ns(namespace), ...(scope ? [scope] : []))
    .map(r => kindOf(r.kind, r.namespace, null, r.scope));
}
/* does a kind extend another (or is it that kind)? */
const isA = (kind, ancestor, namespace, scope) => { const k = kindOf(kind, namespace, null, scope); return !!k && k.lineage.includes(ancestor); };
const ctx = (uid, key) => "kernel:" + uid + ":" + key;
/* validates a patch against the kind; sensitive values are sealed with the node and key as AAD */
function checkAttrs(k, uid, patch, whole) {
  const decl = new Map(k.attributes.map(a => [a.key, a]));
  const out = {};
  for (const [key, v] of Object.entries(patch || {})) {
    const a = decl.get(key);
    if (!a) fail(`Kind ${k.kind} declares no attribute ${key}`);
    if (v === null) { out[key] = null; continue; }
    checkValue(a.type, a.constraints, v, { uid, kind: k.kind, key, label: key });
    out[key] = a.sensitive ? sec.encryptSecret(JSON.stringify(v), ctx(uid, key)) : v;
  }
  if (whole) for (const a of k.attributes) if (a.required && (whole[a.key] == null)) fail(`${a.key} is required for kind ${k.kind}`);
  return out;
}
function openAttrs(k, uid, attrs, lang) {
  const sensitive = new Set(k.attributes.filter(a => a.sensitive).map(a => a.key));
  const spoken = lang ? new Set(k.attributes.filter(a => LOCALISED.has(a.type)).map(a => a.key)) : null;
  const out = {};
  for (const [key, v] of Object.entries(attrs)) {
    if (v === null) continue;
    const open = sensitive.has(key) ? J(sec.safeDecrypt(v, ctx(uid, key)), null) : v;
    out[key] = spoken && spoken.has(key) ? text(open, lang) : open;
  }
  return out;
}
/* multilingual text in one language: the language asked, else the source language, else the
   first the value holds — never an empty answer when the value has any text */
function text(v, lang) {
  if (!v || typeof v !== "object") return v == null ? null : String(v);
  const E = expression(), want = E.base(lang);
  return v[want] != null ? v[want] : v[E.SEED.sourceLanguage] != null ? v[E.SEED.sourceLanguage] : v[Object.keys(v)[0]];
}

/* ============================== K02 nodes + K04 identifiers (Identity) ============================== */
function nodeRow(uid) { ensureTables(); return get("SELECT * FROM k_nodes WHERE uid=?", String(uid)); }
function kindForNode(uid) {
  const n = nodeRow(uid); if (!n) fail("Unknown node: " + uid);
  const k = kindOf(n.kind, n.namespace, null, n.scope); if (!k) fail("Node " + uid + " has no declared kind " + n.kind);
  return { n, k };
}
function createNode(kind, o, actor) {
  o = o || {};
  const namespace = ns(o.namespace), scope = scopeOk(o.scope);
  const k = kindOf(kind, namespace, null, scope);
  if (!k) fail("Unknown kind: " + kind);
  /* a node may adopt a universal ID it already has elsewhere (a row migrating onto the kernel
     keeps its identity); otherwise one is minted */
  const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;
  const uid = o.uid ? String(o.uid).toLowerCase() : crypto.randomUUID();
  if (o.uid && !UUID.test(uid)) fail("A universal ID is a UUID: " + o.uid);
  if (o.uid && nodeRow(uid)) fail("That universal ID already names a node: " + uid);
  const w = window(o);
  return tx(() => {
    const seq = append(EV.nodeCreated, { namespace, subject: uid, actor, payload: scope ? { kind, scope } : { kind } });
    run("INSERT INTO k_nodes(uid,namespace,kind,scope,rec_from) VALUES(?,?,?,?,?)", uid, namespace, kind, scope, seq);
    record(uid, o.attributes || {}, { validFrom: w.from, validTo: w.to }, actor, true);
    for (const [scheme, value] of Object.entries(o.identifiers || {})) assignIdentifier(uid, scheme, value, { validFrom: w.from, validTo: w.to }, actor);
    return uid;
  });
}
/* the nodes of a kind (o.withSubkinds: and of every kind extending it; o.scope: only at that scope) */
function nodes(kind, namespace, o) {
  ensureTables();
  o = o || {};
  const space = ns(namespace);
  const want = o.withSubkinds
    ? [...new Set(all("SELECT DISTINCT kind, scope FROM k_nodes WHERE namespace=?", space).filter(r => isA(r.kind, kind, space, r.scope)).map(r => r.kind))]
    : [kind];
  if (!want.length) return [];
  const sc = o.scope ? " AND scope=?" : "";
  return listed(all(`SELECT uid FROM k_nodes WHERE namespace=? AND kind IN (${want.map(() => "?").join(",")})${sc} ORDER BY rec_from`, space, ...want, ...(o.scope ? [String(o.scope)] : [])).map(r => r.uid), o);
}
function assignIdentifier(uid, scheme, value, o, actor) {
  const { n, k } = kindForNode(uid);
  keyOk(scheme, "Identifier scheme");
  if (!k.schemes.includes(scheme)) fail(`Kind ${k.kind} declares no identifier scheme ${scheme}`);
  value = String(value == null ? "" : value).trim();
  if (!value) fail("An identifier needs a value");
  checkCode(scheme, value);
  const w = window(o);
  return tx(() => {
    /* a code names one node at a time: no other node may hold it in an overlapping window */
    const clash = all("SELECT * FROM k_identifiers WHERE scheme=? AND value=? AND rec_to IS NULL AND node<>?", scheme, value, uid)
      .find(r => before(r.valid_from, w.to) && before(w.from, r.valid_to));
    if (clash) fail(`${scheme} ${value} already names node ${clash.node} in that window`);
    const seq = append(EV.identifierAssigned, { namespace: n.namespace, subject: uid, actor, payload: { scheme, value, validFrom: w.from, validTo: w.to } });
    run("INSERT INTO k_identifiers(node,scheme,value,valid_from,valid_to,rec_from) VALUES(?,?,?,?,?,?)", uid, scheme, value, w.from, w.to, seq);
    return seq;
  });
}
/* ends an identifier at an instant: the open row is superseded by one that stops there */
function endIdentifier(uid, scheme, value, at, actor) {
  const end = instant(at, "at") || nowIso();
  return tx(() => {
    const rows = all("SELECT * FROM k_identifiers WHERE node=? AND scheme=? AND value=? AND rec_to IS NULL", uid, scheme, String(value))
      .filter(r => before(r.valid_from, end) && before(end, r.valid_to));
    if (!rows.length) fail("No identifier to end at " + end);
    const seq = append(EV.identifierEnded, { namespace: nodeRow(uid).namespace, subject: uid, actor, payload: { scheme, value, at: end } });
    for (const r of rows) {
      run("UPDATE k_identifiers SET rec_to=? WHERE id=?", seq, r.id);
      run("INSERT INTO k_identifiers(node,scheme,value,valid_from,valid_to,rec_from) VALUES(?,?,?,?,?,?)", uid, scheme, r.value, r.valid_from, end, seq);
    }
    return seq;
  });
}
function identifiers(uid, o) {
  ensureTables();
  o = o || {};
  const b = believed(recordedSeq(o.recorded)), v = validAt(instant(o.at, "at") || nowIso());
  const out = { [SEED.identity.scheme]: uid };
  for (const r of all(`SELECT scheme, value FROM k_identifiers WHERE node=? AND ${b.sql} AND ${v.sql} ORDER BY id`, uid, ...b.args, ...v.args)) out[r.scheme] = r.value;
  return out;
}
function resolveIdentifier(scheme, value, o) {
  ensureTables();
  o = o || {};
  if (scheme === SEED.identity.scheme) return nodeRow(value) ? value : null;
  const b = believed(recordedSeq(o.recorded)), v = validAt(instant(o.at, "at") || nowIso());
  const r = get(`SELECT node FROM k_identifiers WHERE scheme=? AND value=? AND ${b.sql} AND ${v.sql}`, scheme, String(value), ...b.args, ...v.args);
  return r ? r.node : null;
}

/* ============================== K07 versions (Evolution) ============================== */
/* records a patch over [validFrom, validTo): every believed version that overlaps is
   superseded, and replaced by its untouched edges plus the merged middle; any part of the
   window no version covered gets the patch alone */
function record(uid, patch, o, actor, creating) {
  const { n, k } = kindForNode(uid);
  const w = window(o);
  const clean = checkAttrs(k, uid, patch, null);
  return tx(() => {
    const seq = append(EV.attributesRecorded, { namespace: n.namespace, subject: uid, actor, payload: { keys: Object.keys(clean).sort(), validFrom: w.from, validTo: w.to } });
    const hits = all("SELECT * FROM k_versions WHERE node=? AND rec_to IS NULL ORDER BY valid_from", uid)
      .filter(r => before(r.valid_from, w.to) && before(w.from, r.valid_to));
    const writes = [];
    let cursor = w.from;
    for (const r of hits) {
      const a = J(r.attrs, {});
      run("UPDATE k_versions SET rec_to=? WHERE id=?", seq, r.id);
      if (r.valid_from < w.from) writes.push([a, r.valid_from, w.from]);
      const s = maxStart(r.valid_from, w.from), e = minEnd(r.valid_to, w.to);
      if (cursor < s) writes.push([clean, cursor, s]);
      writes.push([{ ...a, ...clean }, s, e]);
      if (before(w.to, r.valid_to)) writes.push([a, w.to, r.valid_to]);
      cursor = e;
    }
    if (cursor != null && before(cursor, w.to)) writes.push([clean, cursor, w.to]);
    for (const [a, from, to] of writes) {
      /* required attributes hold in every stretch of valid time the node has */
      checkAttrs(k, uid, {}, Object.fromEntries(Object.entries(a).filter(([, v]) => v !== null)));
      run("INSERT INTO k_versions(node,attrs,valid_from,valid_to,rec_from) VALUES(?,?,?,?,?)", uid, JSON.stringify(a), from, to, seq);
    }
    return seq;
  });
}
function attributes(uid, o) {
  o = o || {};
  const { k } = kindForNode(uid);
  const b = believed(recordedSeq(o.recorded)), v = validAt(instant(o.at, "at") || nowIso());
  const r = get(`SELECT attrs FROM k_versions WHERE node=? AND ${b.sql} AND ${v.sql}`, uid, ...b.args, ...v.args);
  return r ? openAttrs(k, uid, J(r.attrs, {}), o.lang) : null;
}
/* the full record of belief: every version ever written, superseded or not */
function history(uid) {
  const { k } = kindForNode(uid);
  return all("SELECT * FROM k_versions WHERE node=? ORDER BY rec_from, valid_from", uid)
    .map(r => ({ validFrom: r.valid_from, validTo: r.valid_to, recordedFrom: r.rec_from, recordedTo: r.rec_to, attributes: openAttrs(k, uid, J(r.attrs, {})) }));
}

/* ============================== K03 hierarchies (Relationship) ============================== */
function defineHierarchy(d, actor) {
  d = d || {};
  const namespace = ns(d.namespace), hierarchy = keyOk(d.hierarchy, "Hierarchy"), scope = scopeOk(d.scope);
  if (!DOMAINS.has(d.owner)) fail("A hierarchy needs an owning domain from the register: " + d.owner);
  const spec = { label: d.label || hierarchy };
  return tx(() => {
    const seq = append(EV.hierarchyDefined, { namespace, subject: hierarchy, actor, payload: { owner: d.owner, scope, spec } });
    run(`UPDATE k_hierarchies SET rec_to=? WHERE namespace=? AND hierarchy=? AND ${scope == null ? "scope IS NULL" : "scope=?"} AND rec_to IS NULL`, seq, namespace, hierarchy, ...(scope == null ? [] : [scope]));
    run("INSERT INTO k_hierarchies(namespace,hierarchy,owner,spec,scope,rec_from) VALUES(?,?,?,?,?,?)", namespace, hierarchy, d.owner, JSON.stringify(spec), scope, seq);
    return hierarchyOf(hierarchy, namespace, scope);
  });
}
function hierarchyOf(hierarchy, namespace, scope) {
  ensureTables();
  /* a hierarchy declared at a scope, else across the namespace, else the platform's */
  const q = "SELECT * FROM k_hierarchies WHERE namespace=? AND hierarchy=? AND rec_to IS NULL";
  const r = (scope ? get(q + " AND scope=?", ns(namespace), hierarchy, String(scope)) : null)
    || get(q + " AND scope IS NULL", ns(namespace), hierarchy) || get(q + " AND scope IS NULL", SEED.defaultNamespace, hierarchy);
  return r ? { namespace: r.namespace, hierarchy: r.hierarchy, owner: r.owner, scope: r.scope || null, ...J(r.spec, {}) } : null;
}
/* hierarchies are addressed as "<namespace>/<key>" in placements (with "@<scope>" for one declared
   at a scope), so one key may exist per namespace and scope; a namespace without its own uses the platform's */
const hid = (h, namespace, scope) => {
  const H = hierarchyOf(h, namespace, scope);
  return (H ? H.namespace : ns(namespace)) + (H && H.scope ? "@" + H.scope : "") + "/" + h;
};
const scopeOf = o => (o && o.scope) || null;
/* edges valid at one instant (o.at), or — with o.during — at any time in a window */
function edges(h, col, val, o) {
  const b = believed(recordedSeq(o && o.recorded));
  const rows = (v) => all(`SELECT * FROM k_placements WHERE hierarchy=? AND ${col} ${val == null ? "IS NULL" : "=?"} AND ${b.sql}${v ? " AND " + v.sql : ""} ORDER BY id`,
    h, ...(val == null ? [] : [val]), ...b.args, ...(v ? v.args : []));
  if (o && o.during) return rows(null).filter(r => before(r.valid_from, o.during.to) && before(o.during.from, r.valid_to));
  return rows(validAt(instant(o && o.at, "at") || nowIso()));
}
function ancestorSet(h, uid, o) {
  const seen = new Set(), stack = [uid];
  while (stack.length) {
    const u = stack.pop();
    for (const e of edges(h, "node", u, o)) if (e.parent && !seen.has(e.parent)) {
      seen.add(e.parent); stack.push(e.parent);
      if (seen.size > SEED.limits.maxDepth) fail("Hierarchy deeper than " + SEED.limits.maxDepth);
    }
  }
  return seen;
}
function place(hierarchy, uid, parent, o, actor) {
  o = o || {};
  const H = hierarchyOf(hierarchy, o.namespace, o.scope);
  if (!H) fail("Unknown hierarchy: " + hierarchy);
  const h = hid(hierarchy, o.namespace, o.scope);
  const { k } = kindForNode(uid);
  const w = window(o);
  if (parent == null) { if (!k.root) fail(`Kind ${k.kind} may not sit at the top of a hierarchy`); }
  else {
    const pk = kindForNode(parent).k;
    if (!k.parents.includes("*") && !pk.lineage.some(l => k.parents.includes(l))) fail(`Kind ${k.kind} may not sit under kind ${pk.kind}`);
    /* a cycle at any moment of the window is a cycle */
    if (parent === uid || ancestorSet(h, parent, { during: w }).has(uid)) fail("That placement would make a cycle");
  }
  return tx(() => {
    const dup = all(`SELECT * FROM k_placements WHERE hierarchy=? AND node=? AND parent ${parent == null ? "IS NULL" : "=?"} AND rec_to IS NULL`, h, uid, ...(parent == null ? [] : [parent]))
      .find(r => before(r.valid_from, w.to) && before(w.from, r.valid_to));
    if (dup) fail("The node already sits there in that window");
    const seq = append(EV.nodePlaced, { namespace: H.namespace, subject: uid, actor, payload: { hierarchy: h, parent: parent || null, validFrom: w.from, validTo: w.to } });
    const r = run("INSERT INTO k_placements(hierarchy,node,parent,valid_from,valid_to,rec_from) VALUES(?,?,?,?,?,?)", h, uid, parent || null, w.from, w.to, seq);
    return Number(r.lastInsertRowid);
  });
}
function endPlacement(hierarchy, uid, parent, at, o, actor) {
  o = o || {};
  const h = hid(hierarchy, o.namespace, o.scope);
  const end = instant(at, "at") || nowIso();
  return tx(() => {
    const rows = all(`SELECT * FROM k_placements WHERE hierarchy=? AND node=? AND parent ${parent == null ? "IS NULL" : "=?"} AND rec_to IS NULL`, h, uid, ...(parent == null ? [] : [parent]))
      .filter(r => before(r.valid_from, end) && before(end, r.valid_to));
    if (!rows.length) fail("No placement to end at " + end);
    const seq = append(EV.placementEnded, { namespace: ns(o.namespace), subject: uid, actor, payload: { hierarchy: h, parent: parent || null, at: end } });
    for (const r of rows) {
      run("UPDATE k_placements SET rec_to=? WHERE id=?", seq, r.id);
      run("INSERT INTO k_placements(hierarchy,node,parent,valid_from,valid_to,rec_from) VALUES(?,?,?,?,?,?)", h, uid, r.parent, r.valid_from, end, seq);
    }
    return seq;
  });
}
/* where a node sits now (or at a time): its parents, with null for the top of the hierarchy */
const placementsOf = (hierarchy, uid, o) => { ensureTables(); return [...new Set(edges(hid(hierarchy, o && o.namespace, scopeOf(o)), "node", uid, o).map(e => e.parent || null))]; };
const children = (hierarchy, uid, o) => { ensureTables(); return listed([...new Set(edges(hid(hierarchy, o && o.namespace, scopeOf(o)), "parent", uid == null ? null : uid, o).map(e => e.node))], o); };
const parents = (hierarchy, uid, o) => { ensureTables(); return [...new Set(edges(hid(hierarchy, o && o.namespace, scopeOf(o)), "node", uid, o).map(e => e.parent).filter(Boolean))]; };
const ancestors = (hierarchy, uid, o) => { ensureTables(); return [...ancestorSet(hid(hierarchy, o && o.namespace, scopeOf(o)), uid, o)]; };
/* every path from a top node down to this one: a node in many places has many paths */
function paths(hierarchy, uid, o) {
  ensureTables();
  const h = hid(hierarchy, o && o.namespace, scopeOf(o));
  const up = (u, seen) => {
    if (seen.size > SEED.limits.maxDepth) fail("Hierarchy deeper than " + SEED.limits.maxDepth);
    const es = edges(h, "node", u, o);
    if (!es.length) return [];
    return es.flatMap(e => e.parent == null ? [[u]] : seen.has(e.parent) ? [] : up(e.parent, new Set([...seen, u])).map(p => [...p, u]));
  };
  return up(uid, new Set());
}
function descendants(hierarchy, uid, o) {
  ensureTables();
  const h = hid(hierarchy, o && o.namespace, scopeOf(o));
  const max = o && o.depth != null ? Number(o.depth) : SEED.limits.maxDepth;
  const seen = new Set(); let level = [uid], d = 0;
  while (level.length && d < max) {
    const next = [];
    for (const u of level) for (const e of edges(h, "parent", u, o)) if (!seen.has(e.node)) { seen.add(e.node); next.push(e.node); }
    level = next; d++;
  }
  /* a hidden node's subtree is still walked: hiding hides that node, not what sits under it */
  return listed([...seen], o);
}

/* the shared machinery the kernel's other parts (lib/kernel-shape.js, lib/kernel-context.js) build on */
const internal = { tx, dryRun, listed, append, fail, instant, nowIso, before, minEnd, maxStart, window, recordedSeq, believed, validAt, ns, keyOk, scopeOk, kindForNode, nodeRow, J, TYPE_CHECKS, VALUE_TYPES, DOMAINS, ensureColumn, checkValue, checkCode };

module.exports = {
  ensureTables, SEED, internal,
  /* K08 */ append, events, verifyEvents,
  /* K01 + K06 */ defineKind, kindOf, kinds, isA, text,
  /* K02 + K04 */ createNode, nodes, assignIdentifier, endIdentifier, identifiers, resolveIdentifier,
  /* K07 */ record, attributes, history,
  /* K03 */ defineHierarchy, hierarchyOf, place, endPlacement, placementsOf, children, parents, ancestors, paths, descendants
};
