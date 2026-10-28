/* LUXORA Platform — money at rest (PR-016).

   Every persisted amount of the payment spine (lib/seed/money.json `store.tables`) is kept as
   EXACT MINOR UNITS: `<column>_minor`, a 64-bit integer (SQLite INTEGER, Postgres BIGINT), at
   the row's `money_scale` (its currency's decimals when it was written), in the row's
   `currency`. That is the financial truth. The REAL column of the same name beside it is a
   PROJECTION — the double whose shortest spelling is the exact decimal — kept for the readers
   that predate this (reports, consoles, exports). It is written only from the minor value, and
   the database refuses any row where the two disagree (SQLite triggers here; Postgres CHECK
   constraints added by lib/migrate.js from the same expression), so it cannot drift.

   Migration money-0001 (`migrate`, run at boot before the server listens, in ONE transaction):
   the columns are added, every existing row is read and classified, and the guard installed.
     exact        the REAL's shortest spelling has no more decimals than the currency: its
                  minor units are that decimal, exactly
     normalized   the REAL is binary noise around exactly one such decimal (0.30000000000000004
                  is 0.3 at 15 significant digits, the precision a double guarantees): converted
                  to it, and recorded in money_quarantine with status `normalized` for audit
     quarantined  the intended amount cannot be told from the stored one — genuinely more
                  decimals than the currency has (10.235 of a 2-decimal currency), no currency,
                  a currency the master does not know, or a value that is not a number. The
                  row keeps its source values, is marked `money_state = 'quarantined'`, and
                  money operations on it are refused until an operator resolves it
                  (`resolve`, scripts/money.js). Nothing is guessed to finish the migration.
   A crash part-way leaves nothing (the transaction rolls back) and the next boot runs it again;
   a finished migration is recorded in money_migrations and never re-run.

   Postgres: the schema and the guard arrive through lib/migrate.js from a migrated SQLite
   database; a Postgres database that has not got them is refused at boot (`assertMigrated`). */
"use strict";
const M = require("./money.js");
const POLICY = require("./seed/money.json");

const SPEC = POLICY.store;
const VERSION = SPEC.migration;
const TABLES = SPEC.tables;
const byTable = Object.fromEntries(TABLES.map(t => [t.table, t]));
/* the words money at rest records its states with are data (lib/seed/money.json store.states) */
const ST = SPEC.states, Q = ST.row.quarantined, OPEN = ST.entry.open, NORMALIZED = ST.entry.normalized, RESOLVED = ST.entry.resolved, RUNNING = ST.migration.running, DONE = ST.migration.done;
let _db = null;
const db = () => _db || (_db = require("./db.js"));
const fail = (m, status, code) => Object.assign(new Error(m), { status: status || 409, code: code || "money_review" });
const specOf = table => { const t = byTable[table]; if (!t) throw new Error("Not a money table: " + table); return t; };
const minorCol = c => c + "_minor";
const hasRefunds = t => !!t.refunds;

/* ---------------- schema ---------------- */
/* the columns each money table gains; ADD COLUMN only, so an existing row is never rewritten */
function columnDdl() {
  const out = [];
  for (const t of TABLES) {
    if (t.addCurrency) out.push([t.table, "currency TEXT"]);
    for (const c of t.amounts) out.push([t.table, minorCol(c) + " INTEGER"]);
    out.push([t.table, "money_scale INTEGER"], [t.table, "money_state TEXT"]);
    if (hasRefunds(t)) out.push([t.table, "refunded_minor INTEGER NOT NULL DEFAULT 0"]);
  }
  return out;
}
const TABLE_DDL = `
CREATE TABLE IF NOT EXISTS money_migrations (
  version TEXT PRIMARY KEY, status TEXT NOT NULL, started_at TEXT NOT NULL DEFAULT (datetime('now')),
  finished_at TEXT, report TEXT NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS money_quarantine (
  id INTEGER PRIMARY KEY AUTOINCREMENT, version TEXT NOT NULL, table_name TEXT NOT NULL, row_key TEXT NOT NULL,
  column_name TEXT NOT NULL, tenant_id INTEGER, source_value TEXT, source_currency TEXT, reason TEXT NOT NULL,
  candidates TEXT NOT NULL DEFAULT '{}', status TEXT NOT NULL,
  resolved_minor INTEGER, resolved_currency TEXT, resolved_scale INTEGER, resolved_by TEXT, resolved_at TEXT, note TEXT DEFAULT '',
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE (version, table_name, row_key, column_name)
);
CREATE INDEX IF NOT EXISTS ix_money_quarantine_open ON money_quarantine(status, table_name);
/* a refund is its own record: how much of a payment went back, in the payment's currency, once
   per idempotency key and once per provider refund id. payments.refunded_minor is the sum of
   the refunds that are pending or done, claimed atomically, so concurrent requests can never
   refund more than was captured */
CREATE TABLE IF NOT EXISTS refunds (
  id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id INTEGER NOT NULL, payment_id INTEGER NOT NULL,
  amount_minor INTEGER NOT NULL CHECK (amount_minor > 0), currency TEXT NOT NULL, money_scale INTEGER NOT NULL,
  status TEXT NOT NULL, source TEXT NOT NULL DEFAULT 'console', reason TEXT DEFAULT '',
  idem_key TEXT NOT NULL, provider_refund_id TEXT, error TEXT, actor TEXT DEFAULT '', attempts INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT (datetime('now')), settled_at TEXT,
  UNIQUE (tenant_id, idem_key)
);
CREATE INDEX IF NOT EXISTS ix_refunds_payment ON refunds(payment_id);
CREATE UNIQUE INDEX IF NOT EXISTS ux_refunds_provider ON refunds(payment_id, provider_refund_id) WHERE provider_refund_id IS NOT NULL;
`;
/* run by lib/db.js during its column migrations, on either engine */
function ensureSchema(execFn) {
  execFn(TABLE_DDL);
  for (const [table, col] of columnDdl().concat([["refunds", "attempts INTEGER NOT NULL DEFAULT 1"]])) { try { execFn("ALTER TABLE " + table + " ADD COLUMN " + col); } catch (e) { /* present */ } }
}

/* ---------------- the database-level guard ---------------- */
/* 10^s as the engine's double, for s = 0…18 */
function pow10(scaleExpr, engine) {
  const real = engine === "pg" ? "DOUBLE PRECISION" : "REAL";
  const arms = []; for (let s = 0; s <= 18; s++) arms.push(`WHEN ${s} THEN CAST(1e${s} AS ${real})`);
  return `(CASE ${scaleExpr} ${arms.join(" ")} END)`;
}
/* true when every amount's projection is exactly its minor value at the row's scale (a double
   division is correctly rounded, so minor / 10^scale is the nearest double to the exact
   decimal — the same double the decimal's spelling parses to) */
function invariant(table, engine, prefix) {
  const t = specOf(table), p = prefix || "", real = engine === "pg" ? "DOUBLE PRECISION" : "REAL";
  const parts = t.amounts.map(c => `((${p}${c} IS NULL AND ${p}${minorCol(c)} IS NULL) OR (${p}${minorCol(c)} IS NOT NULL AND ${p}money_scale IS NOT NULL AND ${p}${c} = CAST(${p}${minorCol(c)} AS ${real}) / ${pow10(p + "money_scale", engine)}))`);
  if (hasRefunds(t)) parts.push(`(${p}refunded_minor >= 0 AND (${p}refunded_minor = 0 OR ${p}refunded_minor <= ${p}amount_minor))`);
  return `(COALESCE(${p}money_state, '') = '${Q}' OR (${parts.join(" AND ")}))`;
}
const guardName = (table, what) => "money" + SPEC.version + "_" + table + "_" + what;
function sqliteGuards(table) {
  const t = specOf(table);
  const watched = [...t.amounts, ...t.amounts.map(minorCol), "money_scale", "money_state", ...(hasRefunds(t) ? ["refunded_minor"] : [])];
  const raise = `SELECT RAISE(ABORT, 'money_projection: ${table} amounts are written as exact minor units (lib/money-store.js)')`;
  return [
    `CREATE TRIGGER IF NOT EXISTS ${guardName(table, "ins")} BEFORE INSERT ON ${table} WHEN NOT COALESCE(${invariant(table, "sqlite", "NEW.")}, 0) BEGIN ${raise}; END`,
    `CREATE TRIGGER IF NOT EXISTS ${guardName(table, "upd")} BEFORE UPDATE OF ${watched.join(", ")} ON ${table} WHEN NOT COALESCE(${invariant(table, "sqlite", "NEW.")}, 0) BEGIN ${raise}; END`
  ];
}
/* lib/migrate.js adds these after the data load on Postgres */
const pgConstraints = () => TABLES.map(t => ({ table: t.table, sql: `ALTER TABLE "${t.table}" ADD CONSTRAINT ${guardName(t.table, "projection")} CHECK ${invariant(t.table, "pg")}` }));

/* ---------------- classification of a stored value ---------------- */
function classify(v, decimals, currency) {
  if (v == null) return { state: "null" };
  let s;
  if (typeof v === "number") s = String(v);
  else if (typeof v === "bigint") s = v.toString();
  else s = String(v).trim();
  let p; try { p = M.normalize(M.parse(s)); } catch (e) { return { state: Q, reason: "not_a_number", source: s }; }
  if (p.scale <= decimals) return { state: "exact", minor: M.toMinor(s, decimals, "down"), source: s };
  if (typeof v === "number") {
    const t = M.numberText(v);
    const q = M.normalize(M.parse(t));
    if (q.scale <= decimals) return { state: "normalized", minor: M.toMinor(t, decimals, "down"), source: s, normalizedTo: t };
  }
  const candidates = {};
  for (const mode of ["half-up", "half-even", "down"]) candidates[mode] = M.toMinor(s, decimals, mode);
  return { state: Q, reason: "excess_precision", source: s, candidates, rule: M.modeFor(currency) };
}

/* ---------------- migration money-0001 ---------------- */
function migrationRow() { try { return db().get("SELECT * FROM money_migrations WHERE version=?", VERSION) || null; } catch (e) { return null; } }
const migrated = () => { const r = migrationRow(); return !!(r && r.status === DONE); };
let doneThisProcess = false;
function assertMigrated() {
  if (migrated()) return true;
  throw Object.assign(new Error("money migration " + VERSION + " has not been applied to this database: migrate it from an upgraded SQLite database (lib/migrate.js) before serving traffic"), { code: "money_unmigrated" });
}
/* the currency a row's amounts are in: its own column, or (order lines, invoice lines) its parent's */
function currencySql(t) {
  if (t.currencyFrom) return `COALESCE(NULLIF(${t.table}.currency, ''), (SELECT p.currency FROM ${t.currencyFrom.table} p WHERE p.id = ${t.table}.${t.currencyFrom.column}))`;
  return `${t.table}.currency`;
}
/* the store a row belongs to, for the quarantine report: its own, or its parent's */
const tenantSql = t => t.noTenant ? `(SELECT p.tenant_id FROM ${t.currencyFrom.table} p WHERE p.id = ${t.table}.${t.currencyFrom.column})` : `${t.table}.tenant_id`;
function backfillTable(t, report, D) {
  /* rows: converted exactly / quarantined (per row); normalizedAmounts and nullAmounts per amount */
  const r = { rows: 0, exact: 0, quarantined: 0, normalizedAmounts: 0, nullAmounts: 0 };
  /* read in key order, a batch at a time, so a large table never sits in memory at once */
  const BATCH = 5000;
  const page = after => D.all(`SELECT ${t.key} AS k, ${currencySql(t)} AS cur, ${tenantSql(t)} AS tid, ${t.amounts.join(", ")} FROM ${t.table} WHERE money_scale IS NULL AND money_state IS NULL AND ${t.key} > ? ORDER BY ${t.key} LIMIT ${BATCH}`, after);
  const note = (row, col, c, extra) => D.run("INSERT OR IGNORE INTO money_quarantine(version,table_name,row_key,column_name,tenant_id,source_value,source_currency,reason,candidates,status) VALUES(?,?,?,?,?,?,?,?,?,?)",
    VERSION, t.table, String(row.k), col, row.tid == null ? null : Number(row.tid), c.source == null ? (row[col] == null ? null : String(row[col])) : c.source, row.cur || null, extra.reason, JSON.stringify(extra.candidates || {}), extra.status);
  /* each amount's minor units and its projection: unchanged for an exact value, the exact double
     for a normalized one (its source value is kept in money_quarantine) */
  const sets = [...t.amounts.map(minorCol), ...t.amounts, "money_scale", "money_state", ...(t.addCurrency ? ["currency"] : [])];
  const upd = `UPDATE ${t.table} SET ${sets.map(c => c + "=?").join(", ")} WHERE ${t.key}=?`;
  for (let rows = page(-1); rows.length; rows = page(rows[rows.length - 1].k)) for (const row of rows) {
    r.rows++;
    const code = row.cur ? String(row.cur).trim().toUpperCase() : "";
    let cur = null, why = null;
    if (!code) why = "currency_missing";
    else { try { cur = M.currencyOf(code); } catch (e) { why = "currency_unknown"; } }
    const minors = {}; let q = false;
    for (const col of t.amounts) {
      if (row[col] == null) { minors[col] = null; r.nullAmounts++; continue; }
      if (!cur) { minors[col] = null; q = true; note(row, col, { source: String(row[col]) }, { reason: why, status: OPEN }); continue; }
      const c = classify(row[col], cur.decimals, cur.code);
      if (c.state === "exact") minors[col] = c.minor;
      else if (c.state === "normalized") { minors[col] = c.minor; r.normalizedAmounts++; note(row, col, c, { reason: "binary_noise", candidates: { normalized: c.normalizedTo, minor: c.minor }, status: NORMALIZED }); }
      else { minors[col] = null; q = true; note(row, col, c, { reason: c.reason, candidates: Object.assign({ rule: c.rule }, c.candidates || {}), status: OPEN }); }
    }
    if (q) r.quarantined++; else r.exact++;
    const proj = t.amounts.map(c => (minors[c] == null ? row[c] : M.fromMinor(minors[c], cur.decimals)));
    D.run(upd, ...t.amounts.map(c => minors[c]), ...proj, cur ? cur.decimals : null, q ? Q : null, ...(t.addCurrency ? [cur ? cur.code : (code || null)] : []), row.k);
  }
  report[t.table] = r;
}
/* the whole migration, once; on SQLite only (Postgres receives the result through lib/migrate.js) */
function migrate() {
  const D = db();
  if (D.USE_PG) return assertMigrated() && { version: VERSION, already: true };
  if (migrated()) { installGuards(D); doneThisProcess = true; return { version: VERSION, already: true }; }
  const started = Date.now();
  const report = {};
  D.exec("BEGIN IMMEDIATE");
  try {
    D.run("INSERT INTO money_migrations(version,status) VALUES(?, ?) ON CONFLICT(version) DO UPDATE SET status=excluded.status, started_at=datetime('now')", VERSION, RUNNING);
    for (const t of TABLES) {
      backfillTable(t, report, D);
      /* test/money-store.js: a process killed part-way through, inside the transaction */
      if (process.env.LX_TEST && process.env.LX_MONEY_CRASH_AFTER === t.table) process.kill(process.pid, "SIGKILL");
    }
    installGuards(D);
    /* the migration checks its own result before it commits: every row satisfies the guard */
    for (const t of TABLES) {
      const bad = D.get(`SELECT COUNT(*) c FROM ${t.table} WHERE NOT COALESCE(${invariant(t.table, "sqlite")}, 0)`).c;
      if (bad) throw new Error("money migration " + VERSION + ": " + bad + " row(s) of " + t.table + " fail the projection check — rolled back");
    }
    report.ms = Date.now() - started;
    D.run("UPDATE money_migrations SET status=?, finished_at=datetime('now'), report=? WHERE version=?", DONE, JSON.stringify(report), VERSION);
    D.exec("COMMIT");
  } catch (e) { try { D.exec("ROLLBACK"); } catch (x) { } throw e; }
  doneThisProcess = true;
  return { version: VERSION, report };
}
function installGuards(D) { for (const t of TABLES) for (const sql of sqliteGuards(t.table)) D.exec(sql); }

/* ---------------- writing ---------------- */
/* the columns of one row's amounts: each Money (or decimal, which must already be exact at the
   currency's scale) as its projection and its minor units, the scale and the currency */
function values(table, currency, amounts) {
  const t = specOf(table);
  const c = M.currencyOf(currency);
  /* every money table carries its currency on the row */
  const out = { currency: c.code, money_scale: c.decimals, money_state: null };
  for (const col of Object.keys(amounts)) {
    if (!t.amounts.includes(col)) throw new Error(col + " is not a money column of " + table);
    const v = amounts[col];
    if (v == null) { out[col] = null; out[minorCol(col)] = null; continue; }
    const m = M.isMoney(v) ? v : M.of(v, c.code);
    if (m.currency !== c.code) throw Object.assign(new Error(`${table}.${col} is ${m.currency}, the row is ${c.code}`), { code: "currency_mismatch" });
    if (m.scale !== c.decimals) throw Object.assign(new Error(`${table}.${col} is at ${m.scale} decimals, ${c.code} has ${c.decimals}`), { code: "scale_mismatch" });
    out[col] = M.toNumber(m); out[minorCol(col)] = M.minorOf(m);
  }
  return out;
}
/* during a first boot, before the master knows any currency and before the guard exists, a
   seed row is written as it always was and the migration that follows classifies it */
const guardLive = () => doneThisProcess || migrated();
function insert(table, row, currency, amounts) {
  /* an amount whose column defaults to 0 and that the row does not state is that exact zero */
  const z = specOf(table).zero || [];
  if (z.some(c => !(c in amounts))) amounts = Object.assign(Object.fromEntries(z.filter(c => !(c in amounts)).map(c => [c, "0"])), amounts);
  let cols;
  try { cols = Object.assign({}, row, values(table, currency, amounts)); }
  catch (e) {
    if (guardLive() || !/currency_unknown|currency_missing/.test(e.code || "")) throw e;
    cols = Object.assign({}, row, { currency: currency || null }, Object.fromEntries(Object.entries(amounts).map(([k, v]) => [k, M.isMoney(v) ? M.toNumber(v) : v])));
  }
  const keys = Object.keys(cols);
  return db().run(`INSERT INTO ${table}(${keys.join(",")}) VALUES(${keys.map(() => "?").join(",")})`, ...keys.map(k => cols[k]));
}
/* change some amounts of one row, in the row's own currency and scale */
function update(table, key, amounts, where) {
  const t = specOf(table);
  const r = db().get(`SELECT currency, money_scale, money_state FROM ${table} WHERE ${t.key}=?`, key);
  if (!r) throw new Error("No " + table + " row " + key);
  if (r.money_state === Q) throw fail(table + " " + key + " has amounts under review (money quarantine); resolve them first");
  const cols = values(table, r.currency, amounts);
  delete cols.currency; delete cols.money_state;
  if (r.money_scale != null && cols.money_scale !== Number(r.money_scale)) throw fail(table + " " + key + " was written at " + r.money_scale + " decimals; its currency now has " + cols.money_scale);
  const keys = Object.keys(cols);
  return db().run(`UPDATE ${table} SET ${keys.map(k => k + "=?").join(", ")} WHERE ${t.key}=?${where ? " AND " + where.sql : ""}`, ...keys.map(k => cols[k]), key, ...((where && where.args) || []));
}

/* ---------------- reading ---------------- */
/* a row's amount as Money, from its minor units — never from the projection */
function amountOf(table, row, col) {
  specOf(table);
  if (!row) throw new Error("No row");
  if (row.money_state === Q) throw fail(table + " row has amounts under review (money quarantine); resolve them first");
  const v = row[minorCol(col)];
  if (v == null) {
    if (row[col] == null) return null;
    throw fail(table + "." + col + " has no exact amount recorded", 409, "money_unmigrated");
  }
  return M.ofMinor(v, row.currency, row.money_scale);
}
const quarantined = row => !!row && row.money_state === Q;
/* what is left to refund on a payment */
function refundable(p) {
  const amount = amountOf("payments", p, "amount");
  return M.sub(amount, M.ofMinor(p.refunded_minor || 0, amount.currency, amount.scale));
}

/* ---------------- reconciliation ---------------- */
/* every money row: its projection equals its minor value, nothing is left unconverted, and
   what is quarantined is listed. The database guard makes a mismatch impossible to write;
   this proves it, on either engine, and is what an operator runs after a restore */
function verify() {
  const D = db(), out = { version: VERSION, migrated: migrated(), ok: true, tables: {}, openQuarantine: 0 };
  for (const t of TABLES) {
    const r = { rows: 0, mismatched: 0, unconverted: 0, quarantined: 0, refundOverflow: 0, samples: [] };
    /* in key order, a batch at a time, so a large table never sits in memory at once */
    const page = after => D.all(`SELECT ${t.key} AS k, currency, money_scale, money_state, ${t.amounts.map(c => `${c}, ${minorCol(c)}`).join(", ")}${hasRefunds(t) ? ", refunded_minor" : ""} FROM ${t.table} WHERE ${t.key} > ? ORDER BY ${t.key} LIMIT 5000`, after);
    for (let rows = page(-1); rows.length; rows = page(rows[rows.length - 1].k)) for (const row of rows) {
      r.rows++;
      if (row.money_state === Q) { r.quarantined++; continue; }
      for (const c of t.amounts) {
        const v = row[c], m = row[minorCol(c)];
        if (v == null && m == null) continue;
        if (m == null || row.money_scale == null) { r.unconverted++; if (r.samples.length < 5) r.samples.push({ key: row.k, column: c, value: v, problem: "no minor" }); continue; }
        if (v == null || Number(v) !== M.fromMinor(m, row.money_scale)) { r.mismatched++; if (r.samples.length < 5) r.samples.push({ key: row.k, column: c, value: v, minor: m, scale: row.money_scale }); }
      }
      if (hasRefunds(t) && (Number(row.refunded_minor) < 0 || (row.amount_minor != null && Number(row.refunded_minor) > Number(row.amount_minor)))) r.refundOverflow++;
    }
    if (r.mismatched || r.unconverted || r.refundOverflow) out.ok = false;
    out.tables[t.table] = r;
  }
  /* each payment's refunded total is the sum of its pending and done refunds */
  const rs = require("./states.js").tagged("refund", "reserved"), inR = "(" + (rs.length ? rs.map(() => "?").join(",") : "NULL") + ")";
  const drift = D.all("SELECT p.id, p.refunded_minor, COALESCE(SUM(CASE WHEN r.status IN " + inR + " THEN r.amount_minor ELSE 0 END),0) s FROM payments p LEFT JOIN refunds r ON r.payment_id=p.id GROUP BY p.id, p.refunded_minor HAVING COALESCE(p.refunded_minor,0) <> COALESCE(SUM(CASE WHEN r.status IN " + inR + " THEN r.amount_minor ELSE 0 END),0)", ...rs, ...rs);
  out.refundLedgerDrift = drift.length; if (drift.length) { out.ok = false; out.refundDriftSamples = drift.slice(0, 5); }
  out.openQuarantine = Number((D.get("SELECT COUNT(*) c FROM money_quarantine WHERE status=?", OPEN) || {}).c || 0);
  return out;
}
function quarantineList(f) {
  f = f || {};
  return db().all("SELECT * FROM money_quarantine WHERE (?='' OR status=?) AND (?='' OR table_name=?) ORDER BY id LIMIT 500", f.status || "", f.status || "", f.table || "", f.table || "")
    .map(r => ({ ...r, candidates: (() => { try { return JSON.parse(r.candidates || "{}"); } catch (e) { return {}; } })() }));
}
/* an operator's decision for one quarantined amount: the exact minor units it is, and its
   currency when the row had none. The source value stays in money_quarantine; the row's
   projection is rewritten from the decision; the row leaves quarantine when nothing on it is
   still open. Audited by the caller. */
function resolve(id, decision) {
  const D = db();
  const q = D.get("SELECT * FROM money_quarantine WHERE id=?", Number(id));
  if (!q) throw fail("Unknown quarantine entry " + id, 404);
  if (q.status !== OPEN) throw fail("Quarantine entry " + id + " is already " + q.status);
  const t = specOf(q.table_name);
  if (!decision || decision.minor == null || !/^-?\d+$/.test(String(decision.minor))) throw fail("A resolution names the exact minor units", 400);
  if (!decision.by) throw fail("A resolution names who decided it", 400);
  return require("./kernel.js").internal.tx(() => {
    const row = D.get(`SELECT * FROM ${t.table} WHERE ${t.key}=?`, q.row_key);
    if (!row) throw fail("The quarantined row no longer exists", 404);
    const code = String(decision.currency || row.currency || (t.currencyFrom ? (D.get(`SELECT currency FROM ${t.currencyFrom.table} WHERE id=?`, row[t.currencyFrom.column]) || {}).currency : "") || "").toUpperCase();
    const cur = M.currencyOf(code);
    if (row.currency && String(row.currency).toUpperCase() !== cur.code && !decision.currency) throw fail("The row's currency is " + row.currency, 400);
    const m = M.ofMinor(String(decision.minor), cur.code, cur.decimals);
    /* the row stays quarantined (so the guard lets this through) until its last open entry */
    D.run(`UPDATE ${t.table} SET ${q.column_name}=?, ${minorCol(q.column_name)}=?, currency=?, money_scale=? WHERE ${t.key}=?`, M.toNumber(m), M.minorOf(m), cur.code, cur.decimals, q.row_key);
    D.run("UPDATE money_quarantine SET status=?, resolved_minor=?, resolved_currency=?, resolved_scale=?, resolved_by=?, resolved_at=datetime('now'), note=? WHERE id=?", RESOLVED, M.minorOf(m), cur.code, cur.decimals, String(decision.by), String(decision.note || ""), q.id);
    const open = D.get("SELECT COUNT(*) c FROM money_quarantine WHERE table_name=? AND row_key=? AND status=?", t.table, q.row_key, OPEN).c;
    if (!open) {
      /* every other amount on the row must already have its minor value (or be null) */
      const fresh = D.get(`SELECT * FROM ${t.table} WHERE ${t.key}=?`, q.row_key);
      const missing = t.amounts.filter(c => fresh[c] != null && fresh[minorCol(c)] == null);
      if (missing.length) throw fail("Still unresolved on this row: " + missing.join(", "));
      D.run(`UPDATE ${t.table} SET money_state=NULL WHERE ${t.key}=?`, q.row_key);
    }
    return { ok: true, table: t.table, key: q.row_key, column: q.column_name, amount: M.toJSON(m), released: !open };
  });
}

module.exports = { VERSION, TABLES, ensureSchema, columnDdl, invariant, sqliteGuards, pgConstraints, classify, migrate, migrated, assertMigrated, values, insert, update, amountOf, quarantined, refundable, verify, quarantineList, resolve, minorCol };
