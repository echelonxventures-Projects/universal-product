# Code Review — Postgres cutover (uncommitted working tree)

**Scope reviewed:** the uncommitted changes on `main` — `lib/db.js`, `lib/enterprise.js`, `lib/migrate.js`,
`lib/pg.js`, `lib/sql.js`, `test/smoke.js`, plus the new `lib/pgbridge.js` and `lib/pgworker.js`.
This is the "B" work: making the platform actually run on Postgres via a synchronous bridge.

**Baseline:** `npm test` → **343 passed, 0 failed** (README still advertises 191 — stale).

**Verdict:** the diff fixes several genuine, load-bearing bugs in the PG wire client and the migration
planner, and the bridge is a legitimate stopgap. But the cutover is **not yet safe to run**: there are
three request-path SQL constructs that will hard-fail on Postgres, indexes are silently dropped, and the
migration's success reporting is unreliable. Details below, ordered by severity.

---

## Summary table

| # | Sev | Finding | Location |
|---|---|---|---|
| H1 | **Blocker** | `INSERT OR REPLACE` untranslated → product-view 500s on PG | `lib/api.js:588`, `lib/sql.js:48` |
| H2 | **Blocker** | `INSERT OR IGNORE` loses ignore semantics → 500s + seed failures | `lib/sql.js:48`, `lib/api.js:456,272` |
| H3 | **Blocker** | `MAX(0, x)` is SQLite scalar MAX → invalid on PG | `lib/offers.js:213,214,242` |
| H4 | **High** | 72 indexes (62 UNIQUE) silently not migrated | `lib/migrate.js:52` |
| H5 | **High** | `datetime('now')` translation is timezone-dependent | `lib/sql.js:34-35`, `lib/migrate.js:19-20` |
| H6 | **High** | `LIKE` becomes case-sensitive | `lib/api.js` (12 sites) |
| H7 | **High** | Console "switch to Postgres" doesn't switch; status lies | `lib/db.js:19`, `lib/enterprise.js:45` |
| H8 | **High** | PG connection string + password returned by API and rendered in UI | `lib/enterprise.js:35`, `public/js/platform.js:588-589` |
| M1 | Med | 3 909 separate TCP connections, no transaction, not resumable | `lib/pg.js:76`, `lib/migrate.js:79` |
| M2 | Med | `apply()` reports success even when most statements failed | `lib/migrate.js:76`, `lib/enterprise.js:42` |
| M3 | Med | Bridge blocks the event loop for every query | `lib/pgbridge.js:23` |
| M4 | Med | Timeout race can return the previous query's result | `lib/pgbridge.js:19-30`, `lib/pgworker.js:36` |
| M5 | Med | No TLS, no SCRAM auth in the PG client | `lib/pg.js:45,76` |
| M6 | Med | No friendly failure when PG is selected before migration | `lib/db.js:1109` |
| L1–L8 | Low | rowid→null trap, schema-less `tableHasId`, 16 MB cap, stale DB size, fragile handle detection, dead translator code, `driver === "db"`, string-built SQL | various |
| T1–T5 | Test | The fake transport encoded the same bug as the impl; `queryP` / `apply()` / bridge have **zero** coverage | `test/smoke.js` |

---

## Blockers — these break at runtime on Postgres

### H1 · `INSERT OR REPLACE` is not translated

`lib/api.js:588` (`apiViewed`):

```js
run("INSERT OR REPLACE INTO view_history(owner,product_id,seen_at) VALUES(?,?,datetime('now'))", owner, body.id);
```

`lib/sql.js:48` rewrites only `INSERT OR IGNORE`; `OR REPLACE` passes through untouched. Postgres rejects
it (`syntax error at or near "OR"`), and the handler is not wrapped in try/catch — so **every product-view
POST returns 500** once the app runs on PG.

It is also a semantic mismatch, not just syntax: SQLite's `OR REPLACE` is a delete+insert upsert. The PG
equivalent is `ON CONFLICT(owner,product_id) DO UPDATE SET seen_at = ...` (the PK is `(owner, product_id)`,
`lib/db.js:139-142`).

### H2 · `INSERT OR IGNORE` loses its ignore semantics

`lib/sql.js:48` converts `INSERT OR IGNORE` → a bare `INSERT`, and `test/smoke.js:948` asserts that as
intended behaviour. It is not equivalent — the conflict clause is dropped entirely.

Request path (unwrapped, user-visible 500s):

- `lib/api.js:456` — `apiSavedAdd`; saving an already-saved item → duplicate PK error instead of a no-op.
- `lib/api.js:272` — `moveOwner`; merging two owners into one hits the same thing for `saved_items` /
  `view_history`.

Boot path — 16 seed sites (`lib/registry.js:32,67,89`, `lib/ai.js:52,61`, `lib/offers.js:50`,
`lib/tax.js:47`, `lib/rbac.js:26`, `lib/events.js:18`, `lib/modules.js:85`) all run on every boot against
an **already-populated** PG (the migration copies the rows in). Each one now throws a duplicate-key error.
They're wrapped in try/catch at `lib/registry.js:92-100` and `lib/db.js:1114`, so it degrades into a
cascade of `… seed failed:` log lines rather than a crash — but registry data silently stops self-healing,
which is exactly the property the seeds exist for.

**Fix:** translate to `INSERT … ON CONFLICT DO NOTHING`.

### H3 · `MAX(0, x)` is a SQLite scalar function

`lib/offers.js:213`, `:214`, `:242`. In Postgres `MAX` is an **aggregate**; `MAX(0, balance - $1)` fails with
`function max(integer, double precision) does not exist`. Line 242 is the wallet upsert inside
`credit()`/`debit()`, so coupon clawback and refunds-to-wallet break. PG's two-argument equivalent is
`GREATEST(0, …)`.

---

## High

### H4 · Indexes are not migrated at all

`lib/migrate.js:52` selects `type='table'` only. Measured on the current DB:

```
tables: 80   statements: 3857 (80 DDL + 3777 data)   CREATE INDEX statements: 0
```

72 indexes in the SQLite schema — 62 of them `UNIQUE` — are dropped. Consequences:

- `ux_offers_code` (partial unique on `offers(tenant_id, code) WHERE code<>''`) no longer enforced.
- All `ux_*_uid` uniqueness lost — `uid` becomes a default value with no constraint behind it.
- Every hot-path index (`ix_orders_tenant`, `ix_products_tenant`, `ix_reviews_pid`, …) gone → full table
  scans on the storefront and consoles.

**Credit where due:** the *inline* `PRIMARY KEY` / `UNIQUE` constraints do survive, because they're part of
`CREATE TABLE`. I verified every `ON CONFLICT` target in the codebase resolves to an inline constraint —
`platform_settings(key)` PK, `meta_lists(name)` PK, `provider_defs(id,kind)` PK, `settings(tenant_id,key)` PK,
`tenant_modules(tenant_id,module_id)` PK, `wallets(tenant_id,owner)` PK, `tenant_gateways(tenant_id,provider_id)`
PK, `entity_meta` inline `UNIQUE`, `entity_defs(key,scope,tenant_id)` PK, `sso_connections(tenant_id)` PK. So
upserts will keep working. It's the separately-declared indexes that vanish.

**Fix:** also plan `sqlite_master WHERE type='index' AND sql IS NOT NULL`, and emit `CREATE INDEX` **after**
the data load (much faster than maintaining them during 3 777 inserts).

### H5 · `datetime('now')` translations depend on the server timezone

`lib/sql.js:34-35` and `lib/migrate.js:19-20` emit `to_char(now(), 'YYYY-MM-DD HH24:MI:SS')`.

SQLite's `datetime('now')` is **UTC**. `to_char(now(), …)` renders in the session `TimeZone`. Unless the PG
server/role is set to UTC, every stored default and every `col > datetime('now')` comparison shifts by the
offset. That reaches month boundaries in reports (`lib/api.js:1550`, `lib/api.js:1959`,
`lib/enterprise.js:170`), coupon/contract validity windows, and dunning/aging buckets.

The comment at `lib/sql.js:27-29` correctly identifies the *shape* requirement (TEXT, not `timestamptz`) but
misses the timezone half of it.

**Fix:** `to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS')`, or pin `SET TIME ZONE 'UTC'` on
every connection.

### H6 · `LIKE` becomes case-sensitive

There are 12 `LIKE` uses in `lib/api.js` (storefront search). SQLite's `LIKE` is case-insensitive for ASCII
by default; Postgres's is case-sensitive. Search results will silently narrow. Use `ILIKE` or add a
translator rule.

### H7 · The console "switch to Postgres" doesn't switch anything, and the status endpoint lies

- `lib/db.js:19` — `USE_PG` is decided from **env only**.
- `lib/enterprise.js:45` — `dbSwitch()` writes `platform_settings.runtime`.
- `lib/enterprise.js:35` — `dbStatus().driver` comes from `config.driverOf("db")`, which resolves
  env → stored → default (`lib/config.js:51-66`).

So after clicking Switch: `GET /api/platform/db` reports `driver: "postgres"`, `enabled: true`, and later
`mode: "migrated"` — while the process is still reading and writing SQLite. Same after a restart unless
`LX_DB_DRIVER=postgres` is exported. An operator will believe the cutover happened.

**Fix:** have `lib/db.js` consult the runtime config, or make `dbSwitch` require a restart and report
`effectiveDriver` separately from the requested one.

### H8 · The Postgres connection string (with password) is returned by the API and painted into the DOM

`lib/enterprise.js:35` adds `pgUrl` to the `dbStatus()` payload → served by `lib/api.js:2467` at
`GET /api/platform/db` → `public/js/platform.js:589` fetches it automatically on console load and
`public/js/platform.js:588` does `JSON.stringify(obj, null, 1)` into `#dbOut`.

The platform's own config schema marks this exact value `secret: true` (`lib/config.js:32`), so the API
directly contradicts the product's own classification. The DSN then lives in the DOM, browser devtools,
screenshots, and any reverse-proxy/CDN access log.

It is gated by `requirePlatform` (super-admin), so it isn't anonymous exposure — but a plaintext DB
credential in a response body is still the wrong shape. **Fix:** return `pgHost` / `pgDatabase` /
`pgConfigured` only.

---

## Medium

### M1 · `apply()` opens one TCP connection per statement, with no transaction

`lib/pg.js:76` calls `TR.connect` on every `queryP` invocation, and `lib/migrate.js:79` issues one
`queryP` per statement. Measured plan: 80 DDL + 3 777 data + 52 `setval` = **3 909 connect/auth/query/close
cycles**, serially.

- Over a network that's minutes of pure handshake overhead; against a pooled managed PG it risks exhausting
  `max_connections`.
- No `BEGIN`/`COMMIT`, so a mid-run failure leaves a half-migrated database with no rollback.
- Re-running is not idempotent (duplicate PKs on every copied row), so recovery is manual.

**Fix:** hold one connection for the whole apply, wrap in a transaction, batch the inserts multi-row, and
build indexes after the load.

### M2 · `apply()` reports success when most statements failed

`lib/migrate.js:76` initialises `out.ok = 0` and increments it per success — `ok` is a **count**, not a
boolean. `lib/enterprise.js:42-43` then does:

```js
Object.assign({ ok: r.ok == null ? true : !!r.ok }, r);
```

`Object.assign` copies `r` over the computed value, so the response is `{ ok: 3909, failed: [...500...] }` —
the numeric `ok` reads as success. `mode` is then set to `"migrated"` unconditionally.

**Fix:** return `{ ok: failed.length === 0, applied, failed }` and only set `mode: "migrated"` when
`failed` is empty.

### M3 · The bridge blocks the event loop for the duration of every query

`lib/pgbridge.js:23` uses `Atomics.wait`, and `lib/db.js:22-26` routes every `run`/`get`/`all` through it.
Node permits `Atomics.wait` on the main thread, so this works — but while a query is in flight the process
cannot service any other request, timer, or I/O callback. Concurrency collapses to 1 and throughput becomes
`1 / round-trip-latency`.

That is a defensible stopgap, and it does let the ~800 synchronous call sites run unchanged. It is also the
opposite of what §25 step 2 ("flip the call sites to `await dbpool.*`") was for. Worth an explicit warning
in README/FLOWS that this is a migration crutch, not the target architecture.

### M4 · A timeout can return the *previous* query's result

- The bridge waits `LX_PG_TIMEOUT || 30000` (`lib/db.js:23`), but the worker always uses 60 000
  (`lib/pgworker.js:36-37`) — the bridge never sends `timeoutMs`, so the two are guaranteed to disagree.
- `lib/pgbridge.js:19-30` has no guard against a late reply. After the bridge times out, the abandoned
  reply later sets `ctrl[0] = 1`. The next `call()` stores `0`, posts its message, and then the *stale*
  reply satisfies `Atomics.wait` → the old result is returned as the answer to the new query.
- `Atomics.wait`'s `"not-equal"` return value isn't handled either (only `"timed-out"` is), which is the
  same race surfacing.

**Fix:** put a monotonic request id in the payload, echo it back, and reject replies whose id doesn't match;
align the two timeouts.

### M5 · No TLS and no SCRAM auth

`lib/pg.js` contains no `ssl`/`tls` handling at all; `TR.connect({host, port})` at `:45` and `:76` is plain
TCP. Managed Postgres (RDS, Cloud SQL, Neon, Supabase) requires TLS, and `sslmode=require` in the URL is
silently ignored — so the connection either fails or is established without the encryption the URL asked for.

Auth supports trust / cleartext / MD5 only. Since PG 14, `password_encryption` defaults to `scram-sha-256`,
so a default modern install will refuse the connection. The error message is honest about it
(`lib/pg.js:58`), which is good — but the runbook should say plainly that this currently only works against
a hand-configured trust/md5 server.

Related: the migration emits `gen_random_uuid()`, which needs PG ≥ 13 (or `pgcrypto` on older).

### M6 · No friendly failure if PG is selected before the migration has run

`lib/db.js:1109` calls `bootstrap()` at import time, which probes
`get("SELECT COUNT(*) c FROM tenants")`. Against an empty Postgres that throws unhandled at module load —
the process dies with a raw PG error and no hint that `Platform → Database → apply` must run first.

---

## Low

- **L1 · `lastInsertRowid` silently becomes `null`** (`lib/pgbridge.js:46-51`). The bridge appends
  `RETURNING id` only when `tableHasId()` is true, so composite-PK tables (`saved_items`, `view_history`,
  `settings`, `departments`, `attribute_defs`, `provider_defs`, `tenant_modules`, `wallets`, `entity_defs`,
  `meta_lists`, `provider_availability`, `countries`, `currencies`, `platform_settings`,
  `idempotency_keys`, `sso_states`, …) yield `null`. ~30 call sites do `Number(x.lastInsertRowid)` → `0`.
  Every current caller targets an `id` table, so nothing breaks today — but it's a silent-wrong-value trap.
  Throw instead of returning `null`.
- **L2 · `tableHasId()` ignores the schema** (`lib/pgbridge.js:39`): no `table_schema` filter, so a
  same-named table in another schema produces a false positive and a spurious `RETURNING id`. Add
  `AND table_schema = current_schema()`.
- **L3 · Fixed 16 MB shared buffer** (`lib/pgbridge.js:5`): larger results are replaced with an opaque
  `{error: "pg bridge: result exceeds shared buffer"}` (`:25`). A `SELECT *` over a big table fails
  confusingly. Make it configurable and/or page large reads.
- **L4 · Analytics "DB size" is wrong under PG**: `lib/api.js:1531` stats `DB_PATH`, which still points at
  the stale SQLite file. Report `pg_database_size` when on PG.
- **L5 · Fragile SQLite-handle detection** (`lib/migrate.js:49`):
  `const owned = !(db().db && typeof db().db.prepare === "function" && !process.env.LX_DB_DRIVER)`.
  Setting `LX_DB_DRIVER=sqlite` explicitly makes this open a *second* `DatabaseSync` on the same file; and
  since the bridge also exposes `prepare` (`lib/pgbridge.js:55`), the check only works because of the
  trailing `!process.env.LX_DB_DRIVER` clause rather than by detecting a bridge. Export `USE_PG` from
  `lib/db.js` and branch on it.
- **L6 · Dead / no-op translator code**: `lib/sql.js:74` `replace(/DEFAULT \x27\x27/gi, "DEFAULT ''")` is a
  no-op; `:78` `replace(/\b\d+\s*=\s*\d+\b/gi, m => m)` is explicitly a no-op guard; `:77`
  `(DEFAULT )` → `DEFAULT false` is a guess. More importantly `lib/sql.js:70-81` (`ddlToPg`) maps
  `INTEGER`→`BIGINT` at `:72` *before* `toPg`'s `INTEGER PRIMARY KEY` → identity rule at `:50`, so it never
  produces an identity column. `migrate.js` uses its own `_ddlToPg`, so the live path is unaffected — but
  `sql.ddlToPg` is exported and wrong. Delete it if unused, or fix the ordering.
- **L7 · `lib/config.js:60`** compares a driver name against the concern key: `driver === "db"` can never
  match (the `db` concern's drivers are `sqlite`/`postgres`). Harmless, but it reads like a copy-paste slip.
- **L8 · String-built SQL in a "parameterized SQL only" codebase**: `lib/api.js:589`
  `DELETE FROM view_history WHERE owner=? AND product_id NOT IN ('${ids.join("','")}')`. The values come
  from the DB rather than the request, so it isn't currently exploitable — but it contradicts the README's
  L9 claim and is precisely the pattern that becomes an injection later.

---

## Test and verification gaps

**T1 · The fake transport encoded the same bug as the implementation — this is the most instructive finding
in the diff.** The old fake emitted `"t"` / `"d"` (ParameterDescription / CopyData) and the old client read
`"t"` / `"d"`, so both agreed, the test passed, and the real protocol (`"T"` RowDescription / `"D"` DataRow)
was misread end-to-end. The `Parse` parameter count had the same shape of error (`ci32`, 4 bytes, where the
protocol requires `Int16`). A hand-rolled fake only ever proves internal consistency. **The single highest-value
follow-up is one integration test against a real Postgres** (`services: postgres` in CI) covering
connect → `query` → `queryP` → `plan()`/`apply()` → a boot + checkout smoke.

**T2 · `queryP` has zero coverage.** Grepping `queryP` in `test/smoke.js` returns nothing. That is the
extended protocol used by `migrate.apply()` *and* by every runtime query through the bridge — and it's
where the `i16` fix landed, with no regression test.

**T3 · `migrate.apply()` has zero coverage.** Only the dry-run plan is tested. The `setval` fix, load-order
FK behaviour, and the failure accounting are all unverified.

**T4 · `pgbridge.js` / `pgworker.js` have zero coverage.** No test sets `USE_PG`, so `lib/db.js:22-27` and
both new files are completely dark in `npm test`.

**T5 · The `setval` fix is correct but untested.** `lib/migrate.js:86-90` — `pg_get_serial_sequence('"t"','id')`
with the quoted name is right, and `COALESCE(MAX(id),0)+1, false` is right (the next `nextval` yields
`MAX+1`). An off-by-one here would corrupt every subsequent insert, so it deserves an assertion.

---

## What's good — these are real fixes

- **`"t"`/`"d"` → `"T"`/`"D"`** (`lib/pg.js:60,61` and `:104,105`). A load-bearing wire-protocol fix;
  without it the client never saw a row.
- **`ci32` → `i16` for the Parse parameter count** (`lib/pg.js:84`). Genuine protocol fix — the count field
  is `Int16`, not `Int32`.
- **`normalizeConn`** (`lib/pg.js:34`). `dbPing`/`dbApply` previously passed
  `{connectionString, host:"127.0.0.1"}`, which fell through to the object branch and connected to localhost
  with no user or database. This fixes the whole apply path.
- **`interval` operator fix** (`lib/sql.js:19`). The old code emitted `now() interval '1 months'` for the
  first modifier — invalid SQL, and untested. `now() + interval '1 months'` is correct, and it's now covered.
- **`OVERRIDING SYSTEM VALUE` moved before `VALUES`** (`lib/migrate.js:62`). The old form put it *after*
  `VALUES (…)`, which is invalid. Now asserted.
- **`topoSort` FK ordering** (`lib/migrate.js:26-33`), with a `stack` guard so cycles degrade gracefully
  instead of hanging. Sound.
- **`uid TEXT DEFAULT gen_random_uuid()` replacing the SQLite triggers** (`lib/migrate.js:36-43`) — the right
  translation, since the triggers are engine-specific.
- **`setval` after the load** (`lib/migrate.js:83-90`). The author caught a subtle identity-sequence bug that
  would otherwise make the *first* runtime insert after migration collide with an existing PK.
- **Correctly gated SQLite-only setup.** The schema DDL (`lib/db.js:38`), the 40-odd `ALTER TABLE` column
  migrations (`:506-545`), and `ensureUids` (`:548`) are all behind `if (!USE_PG)` with correct brace
  placement — I checked the boundaries.
- **Test count 191 → 343 assertions, all green**, including new coverage for the translator, `topoSort`,
  `ddlToPg`, and `normalizeConn`.

---

## Suggested order of work

1. **H1, H2, H3** — three SQL constructs; without these the app 500s on contact with Postgres.
2. **H4** — plan indexes; the migration is otherwise lossy and slow.
3. **H5, H6** — semantic divergence that won't throw but will produce wrong data and wrong search results.
4. **H8** — stop returning the DSN.
5. **H7** — make the reported driver match the effective driver.
6. **M1, M2** — make `apply()` atomic, single-connection, and honest about failure.
7. **T1** — one real-Postgres integration test. This is what turns the rest from "looks right" into "verified".
8. **M3, M4, M5** — before treating the bridge as anything more than a local migration crutch.
