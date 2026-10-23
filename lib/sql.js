/* LUXORA Platform — SQLite→PostgreSQL SQL dialect translator (B-full foundation).
   The app emits a bounded, known set of SQLite idioms. This converts them to PostgreSQL so the
   same SQL runs on either engine; `?` placeholders become `$n`. It is pure + unit-tested — the one
   part of the async migration that can be validated without a live server. PRAGMA / randomblob-uuid
   triggers are SQLite-only and not translated (Postgres uses gen_random_uuid(); see migrate.js). */
"use strict";

function toInterval(mods) {
  // mods: array of '+1 month' | '-30 days' | 'start of month' etc (SQLite modifiers)
  let expr = null, start = false;
  for (let m of mods) {
    m = m.trim();
    const sgn = m[0] === "-" ? "-" : "+";
    let mm = m.replace(/^[+-]/, "").trim();
    if (mm.startsWith("start of month")) { expr = expr ? `date_trunc('month', ${expr})` : `date_trunc('month', current_date)`; start = true; continue; }
    if (mm === "utc") continue;
    mm = mm.replace(/\b(day|month|year|hour|minute|second)s?\b/gi, (_, u) => u + "s");
    if (!/s$/.test(mm)) mm += "s";
    const lit = `${sgn} interval '${mm}'`;
    expr = expr ? `${expr} ${lit}` : `now() ${lit}`; start = false;
  }
  if (expr == null) expr = "now()";
  if (start) expr = `date_trunc('month', ${expr})`;
  return `(${expr})`;
}

/* SQLite stores datetimes as TEXT ('YYYY-MM-DD HH:MM:SS') and compares them lexically. To keep
   every `col > datetime('now')` working unchanged on Postgres, datetime()/date() must yield the
   SAME TEXT shape (not a timestamptz, which has no > operator against a text column).
   H5: SQLite's datetime('now') is UTC, but to_char(now(), ...) renders in the session TimeZone —
   so the conversion must be pinned to UTC or every stored default and every `col > now`
   comparison shifts by the server's offset (report month boundaries, coupon/contract validity,
   dunning buckets all drift). */
function translateDate(sql) {
  /* a modifier passed as a parameter (datetime('now', ?) with '-3 day') is a Postgres interval */
  sql = sql.replace(/\b(datetime|date)\(\s*'now'\s*,\s*\?\s*\)/gi, (_, fn) =>
    `to_char((now() AT TIME ZONE 'UTC') + CAST(? AS interval), '${fn.toLowerCase() === "date" ? "YYYY-MM-DD" : "YYYY-MM-DD HH24:MI:SS"}')`);
  return sql.replace(/\b(datetime|date)\(\s*'now'\s*((?:,\s*'(?:[^']*)')*)\s*\)/gi, (_, fn, rest) => {
    const mods = [...rest.matchAll(/'([^']*)'/g)].map(m => m[1]);
    const raw = toInterval(mods);
    const utc = `${raw} AT TIME ZONE 'UTC'`;
    if (fn.toLowerCase() === "date") return `to_char(${utc}, 'YYYY-MM-DD')`;
    return `to_char(${utc}, 'YYYY-MM-DD HH24:MI:SS')`;
  });
}

function toPg(sql, opts) {
  opts = opts || {};
  let s = sql;
  /* strftime('%fmt', x): a timestamp is stored as text 'YYYY-MM-DD HH:MM:SS', so a format that is
     a prefix of that layout is the text's prefix; any other format formats the parsed timestamp */
  const LAYOUT = "%Y-%m-%d %H:%M:%S";
  const WIDTH = { "%Y": 4, "%Y-%m": 7, "%Y-%m-%d": 10, "%Y-%m-%d %H": 13, "%Y-%m-%d %H:%M": 16, [LAYOUT]: 19 };
  s = s.replace(/\bstrftime\(\s*'([^']+)'\s*,\s*([^)]+?)\s*\)/gi, (_, fmt, col) => {
    const c = col.trim();
    if (/^'now'$/i.test(c)) return `to_char(now() AT TIME ZONE 'UTC', '${fmt.replace(/%Y/, "YYYY").replace(/%m/, "MM").replace(/%d/, "DD").replace(/%H/, "HH24").replace(/%M/, "MI").replace(/%S/, "SS")}')`;
    if (WIDTH[fmt]) return `substr(CAST(${c} AS TEXT), 1, ${WIDTH[fmt]})`;
    return `to_char(CAST(${c} AS timestamp), '${fmt.replace(/%Y/, "YYYY").replace(/%m/, "MM").replace(/%d/, "DD").replace(/%H/, "HH24").replace(/%M/, "MI").replace(/%S/, "SS")}')`;
  });
  /* date(col) of a stored text timestamp is its first ten characters (date('now'…) is translated
     separately, below) */
  s = s.replace(/\bdate\(\s*([A-Za-z_][\w.]*)\s*\)/g, "substr(CAST($1 AS TEXT), 1, 10)");
  // substr(str, a, b) → substring(str from a for b)
  s = s.replace(/\bsubstr\(([^,]+),\s*([0-9$]+),\s*([0-9$]+)\)/gi, "substring($1 from $2 for $3)");
  /* SQLite's IFNULL is Postgres's COALESCE (same meaning for two arguments) */
  s = s.replace(/\bIFNULL\s*\(/gi, "COALESCE(");
  /* the id the session's last INSERT drew (one connection per session, lib/pgworker.js) */
  s = s.replace(/\blast_insert_rowid\(\s*\)/gi, "lastval()");
  s = s.replace(/\bgroup_concat\(([^,]+),\s*'([^']*)'\s*\)/gi, "string_agg($1::text, '$2')");
  s = s.replace(/\bgroup_concat\(([^)]+)\)/gi, "string_agg($1::text, ',')");
  /* H3: SQLite's two-argument MAX is a SCALAR (greatest-of) function; on Postgres MAX is an
     aggregate, so `MAX(0, balance - $1)` is a hard error and breaks the wallet upsert +
     coupon/offer counters. GREATEST is the PG scalar equivalent. Only rewrite the 2+-arg form —
     a single-arg MAX(...) (an aggregate, possibly with DISTINCT) must stay untouched. */
  s = s.replace(/\bMAX\(\s*((?:[^()]|\([^()]*\))+?)\s*,\s*([^()]+)\)/gi, "GREATEST($1, $2)");
  /* H2: SQLite's INSERT OR IGNORE means "skip the row on any conflict". A bare INSERT is NOT
     equivalent — it raises a duplicate-key error, so idempotent seeds and re-saves 500 on PG.
     Rewrite to INSERT … ON CONFLICT DO NOTHING, which is valid on PG (SQLite never emits this
     form, so this only affects the PG request path). Must run BEFORE dollarize and find the
     end of the VALUES(...) group so the clause lands after it, not inside it. */
  s = rewriteIgnoreUpsert(s);
  /* H1: INSERT OR REPLACE is a delete+insert upsert. The conflict target is the table's PK/
     unique constraint, which the translator cannot infer from the statement — and every use in
     this codebase is on view_history whose PK is (owner, product_id). Rewrite to an explicit
     ON CONFLICT upsert with that target. */
  s = s.replace(/\bINSERT\s+OR\s+REPLACE\s+INTO\s+([A-Za-z0-9_."]+)\s*\(([^)]*)\)\s*VALUES\s*\(([^()]*(?:\([^()]*\)[^()]*)*)\)\s*(.*)$/i, (m, tbl, cols, vals, tail) => {
    const colList = cols.split(",").map(c => c.trim());
    const setClause = colList.map(c => `${c} = excluded.${c}`).join(", ");
    return `INSERT INTO ${tbl}(${cols}) VALUES(${vals}) ON CONFLICT(owner, product_id) DO UPDATE SET ${setClause} ${tail}`.trim();
  });
  s = s.replace(/AUTOINCREMENT/gi, "");
  s = s.replace(/\bINTEGER\s+PRIMARY\s+KEY\b/gi, "BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY");
  /* H6: SQLite's LIKE is case-insensitive for ASCII by default; Postgres's is case-sensitive,
     which silently narrows storefront search results. Use ILIKE to preserve SQLite semantics.
     Match LIKE as an operator (not part of a longer identifier) while leaving PL/pgSQL-style
     constructs alone — none are used in this codebase's request path. */
  s = s.replace(/(?<![A-Za-z0-9_])(NOT\s+)?LIKE\s/gi, (m, not) => (not ? "NOT ILIKE " : "ILIKE "));
  s = s.replace(/(?<![A-Za-z0-9_])(NOT\s+)?LIKE\s*\(/gi, (m, not) => (not ? "NOT ILIKE (" : "ILIKE ("));
  // date/datetime modifiers
  s = translateDate(s);
  // `:name` param form used in some upserts (now()/current_date) is already handled.
  // positional ? → $n (skip those inside single-quoted strings)
  if (!opts.noParams) s = dollarize(s);
  return s;
}

function rewriteIgnoreUpsert(sql) {
  const re = /\bINSERT\s+OR\s+IGNORE\s+INTO\b/gi;
  if (!re.test(sql)) return sql;
  re.lastIndex = 0;
  let out = "", last = 0, m;
  while ((m = re.exec(sql))) {
    out += sql.slice(last, m.index) + "INSERT INTO";
    last = m.index + m[0].length;
    /* walk forward to the end of the VALUES(...) group, honouring nested parens and string
       literals, so the conflict clause is appended AFTER the values (a bare "find the closing
       paren" regex breaks on nested calls like datetime('now')). */
    let i = last, depth = 0, inStr = false, seenValues = false;
    while (i < sql.length) {
      const ch = sql[i];
      if (ch === "'") inStr = !inStr;
      else if (!inStr && ch === "(") depth++;
      /* past the last row group: a multi-row VALUES (…),(…) continues after a comma */
      else if (!inStr && ch === ")") { depth--; if (seenValues && depth === 0 && !/^\s*,\s*\(/.test(sql.slice(i + 1))) { i++; break; } }
      else if (!inStr && depth === 0 && /^VALUES\b/i.test(sql.slice(i, i + 7))) seenValues = true;
      i++;
    }
    out += sql.slice(last, i) + " ON CONFLICT DO NOTHING";
    last = i;
  }
  return out + sql.slice(last);
}

function dollarize(sql) {
  let out = "", n = 0, inStr = false;
  for (let i = 0; i < sql.length; i++) {
    const ch = sql[i];
    if (ch === "'") { inStr = !inStr; out += ch; continue; }
    /* a parameter in a string concatenation has no type Postgres can infer: it is text */
    if (ch === "?" && !inStr) { n++; const concat = /\|\|\s*$/.test(out) || /^\s*\|\|/.test(sql.slice(i + 1)); out += "$" + n + (concat ? "::text" : ""); continue; }
    out += ch;
  }
  return out;
}

function ddlToPg(createStmt) {
  let s = createStmt;
  s = s.replace(/\bTEXT\b/gi, "TEXT").replace(/\bINTEGER\b/gi, "BIGINT").replace(/\bREAL\b/gi, "DOUBLE PRECISION");
  s = s.replace(/\bdatetime\('now'\)/gi, "to_char(now(), 'YYYY-MM-DD HH24:MI:SS')");
  s = s.replace(/DEFAULT \x27\x27/gi, "DEFAULT ''");
  s = toPg(s, { noParams: true }).replace(/AUTOINCREMENT/gi, "");
  s = s.replace(/\bBIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY AUTOINCREMENT/gi, "BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY");
  s = s.replace(/\(DEFAULT\s*\)/gi, "DEFAULT false");
  s = s.replace(/\b\d+\s*=\s*\d+\b/gi, m => m); // no-op guard
  s = s.replace(/DEFAULT 1\b/gi, "DEFAULT 1").replace(/DEFAULT 0\b/gi, "DEFAULT 0");
  return s;
}

module.exports = { toPg, dollarize, ddlToPg, toInterval, translateDate };
