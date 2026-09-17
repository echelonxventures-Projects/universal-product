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
   SAME TEXT shape (not a timestamptz, which has no > operator against a text column). */
function translateDate(sql) {
  return sql.replace(/\b(datetime|date)\(\s*'now'\s*((?:,\s*'(?:[^']*)')*)\s*\)/gi, (_, fn, rest) => {
    const mods = [...rest.matchAll(/'([^']*)'/g)].map(m => m[1]);
    const raw = toInterval(mods);
    if (fn.toLowerCase() === "date") return `to_char(${raw}, 'YYYY-MM-DD')`;
    return `to_char(${raw}, 'YYYY-MM-DD HH24:MI:SS')`;
  });
}

function toPg(sql, opts) {
  opts = opts || {};
  let s = sql;
  // strftime('%fmt', x) → to_char(x, 'pgfmt')
  s = s.replace(/\bstrftime\(\s*'([^']+)'\s*,\s*([^)]+?)\s*\)/gi, (_, fmt, col) => `to_char(${col.trim()}, '${fmt.replace(/%Y/, "YYYY").replace(/%m/, "MM").replace(/%d/, "DD").replace(/%H/, "HH").replace(/%M/, "MI").replace(/%S/, "SS")}')`);
  // substr(str, a, b) → substring(str from a for b)
  s = s.replace(/\bsubstr\(([^,]+),\s*([0-9$]+),\s*([0-9$]+)\)/gi, "substring($1 from $2 for $3)");
  s = s.replace(/\bgroup_concat\(([^,]+),\s*'([^']*)'\s*\)/gi, "string_agg($1::text, '$2')");
  s = s.replace(/\bgroup_concat\(([^)]+)\)/gi, "string_agg($1::text, ',')");
  s = s.replace(/\bINSERT\s+OR\s+IGNORE\b/gi, "INSERT");
  s = s.replace(/AUTOINCREMENT/gi, "");
  s = s.replace(/\bINTEGER\s+PRIMARY\s+KEY\b/gi, "BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY");
  // date/datetime modifiers
  s = translateDate(s);
  // `:name` param form used in some upserts (now()/current_date) is already handled.
  // positional ? → $n (skip those inside single-quoted strings)
  if (!opts.noParams) s = dollarize(s);
  return s;
}

function dollarize(sql) {
  let out = "", n = 0, inStr = false;
  for (let i = 0; i < sql.length; i++) {
    const ch = sql[i];
    if (ch === "'") { inStr = !inStr; out += ch; continue; }
    if (ch === "?" && !inStr) { n++; out += "$" + n; continue; }
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
