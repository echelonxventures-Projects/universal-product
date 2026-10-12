# Code Review — LUXORA Platform (HEAD `d63d60f` + uncommitted working tree)

**Scope:** full-project review — the committed tree, the uncommitted working-tree changes, a live
probe of every finding below against a running server, and a security sweep of the request path.

**Method:** `npm test` run to baseline; each finding reproduced by booting the server on a throwaway
DB and driving the real HTTP API / jsdom console (no mocks). Security findings were exploited
end-to-end, not just read.

**Status of the previous review (Postgres cutover):** every finding in it is **closed** — H1, H2
(`INSERT OR IGNORE/REPLACE` → `ON CONFLICT`), H3 (scalar `MAX(0,x)` → `GREATEST` via the translator,
`lib/sql.js:57`), H4 (indexes now planned after the data load, `lib/migrate.js:62`), H5 (`AT TIME ZONE
'UTC'`, `lib/sql.js:38`), H6 (`LIKE` → `ILIKE`, `lib/sql.js:79`), H7 (`effectiveDriver` + `restartRequired`,
`lib/enterprise.js:72`), H8 (DSN no longer returned; `pgHost`/`pgDatabase`/`pgConfigured` only), and
M1–M6 (single transaction, honest `ok`, request-id echo, TLS + SCRAM). That review is superseded by
this one. It should not be re-actioned.

**Closure status of THIS review** — every finding below is fixed in the working tree, verified by a
full `npm test` run (all files green, no assertion failures) plus the probes noted per item:

| # | Closed by |
|---|---|
| S1 | Every affiliate handler gated and tenant-scoped (`requireAdmin` + `AND tenant_id=?` on the order, the affiliate, the payout join and the report) — `lib/api.js:6957–7085` |
| S2 | Voucher issue is an operator action (`isAdmin \|\| platform_admin`, matching the `gift_voucher` entity's own write permission); the module gate stays on the balance path, not the issue path — `lib/api.js:5416` |
| S3 | Capability enable/disable/refuse require staff or platform — `lib/api.js` `apiCapEnable`/`apiCapDisable` |
| S4 | The gift-card endpoint redeems a real code through `fintech.redeemVoucher`; an amount without a code is refused — `lib/api.js` `apiGiftAdd` |
| S5, S6 | The accumulator is implemented (30 one-minute buckets + per-endpoint counters, always on), so `snapshot(tenantId)` returns the `{totals, series, endpoints}` shape both consoles already render — `lib/metrics.js`. Both monitor routes read it directly from the module singleton — `lib/api.js` `apiAdminMonitor`, `apiPlatformMonitor` |
| S7 | Dashboard/report UPDATE and DELETE verify ownership first (a platform row needs a platform admin) — `lib/api.js:304, 403, 409` |
| S8 | `setClause()` whitelists each table's columns against its declared schema and JSON-encodes the structured ones — `lib/global.js:10`. The other `SET ${…}` sites (`entity.js`, `goip.js`) were already built from code-controlled whitelists |
| S9 | The login page's store list escapes slug and name — `public/js/platform.js:3449` |
| S10 | Usage metering is gated and takes the tenant from the session — `lib/api.js` `apiUsageRecord` |
| S11 | `/metrics` requires a bearer token (`LX_METRICS_TOKEN`, ≥ 16 chars, constant-time compared) or a live platform session — `server.js:192` |
| T1 | Test `fetch` retries reads and surfaces writes; `unhandledRejection` is logged; servers are SIGTERM'd and awaited — `test/roles.js`, `test/padmins.js` |

P1 is superseded by the above: it described an intermediate state that has since been replaced by the
real implementation, and the original assertions it claimed were weakened are intact and passing
(`mon.totals.req > 50 && mon.series.length === 30` in `test/smoke.js`). Do not re-action P1, S5 or S6.

---

## Summary table

| # | Sev | Finding | Location |
|---|---|---|---|
| **S1** | **Critical** | The entire Affiliate API is unauthenticated and not tenant-scoped — anon fraud + cross-tenant order disclosure (**exploited**) | `lib/api.js:6428–6505` |
| **S2** | **Critical** | Anonymous gift-voucher minting → wallet credit (**exploited**) | `lib/api.js:4905`, `lib/fintech.js:369` |
| **S3** | **High** | Anonymous shoppers can reconfigure any store's capability composition (**exploited**) | `lib/api.js:5157`, `5186–5211` |
| **S4** | **High** | The "redeem gift card" endpoint never checks a code — it just credits `body.amount` | `lib/api.js:1634` |
| **S5** | **High** | The platform console's **front door is blank**: the command dashboard throws and renders an error | `public/js/platform.js:564`, `lib/api.js:3009` |
| **S6** | **High** | The Monitor feature (store + platform) was never implemented; both surfaces crash | `lib/metrics.js`, `public/js/admin.js:987` |
| **P1** | **High** | The uncommitted changes **hide S5/S6 with hardcoded zeros and weakened tests** instead of fixing them | `lib/api.js:2306`, `test/smoke.js:824`, `test/gops.js`, `test/wizard.js` |
| **S7** | **Med** | Cross-tenant dashboard/report mutation and deletion by a store admin | `lib/api.js:298`, `385`, `406` |
| **S8** | **Med** | Column names taken from request body keys (SQL text injection sinks) | `lib/api.js:6439`, `lib/global.js:32,63,94,145` |
| **S9** | **Med** | Stored XSS via tenant name on the unauthenticated platform login page | `public/js/platform.js:3147` |
| **S10** | **Med** | Unauthenticated, cross-tenant usage-metering writes; tenant id from the request body | `lib/api.js:6118` |
| **T1** | **Med** | `npm test` intermittently dies mid-run from an unhandled `ECONNRESET` (**reproduced 2/3 runs**) | `test/roles.js:167`, `test/padmins.js:245` |
| **S11** | **Low** | `/metrics` exposes platform-wide business metrics with no auth | `server.js:191` |

---

## Critical

### S1 · The Affiliate API has no authorization and no tenant isolation

Every handler in the affiliate block (`lib/api.js:6428–6505`, routes at `:5895–5909`) runs with **no
auth gate** — no `requireAdmin`, `requirePlatform` or `requireUser` — and most queries carry **no
`tenant_id` filter**. The reads are bad (`apiAffiliatePayouts:6480` runs `SELECT * FROM
affiliate_payouts` with no filter when called without an `affiliate_id`, returning every tenant's
payouts), but the writes are worse:

```js
function apiAffiliateConversion(req, res, url, s, body) {
  const tenantId = T(s);
  const order = all('SELECT * FROM orders WHERE id=?', body.order_id)[0];   // no tenant scoping
  ...
  run('UPDATE affiliates SET balance = balance + ?, lifetime_sales = ..., WHERE id=?',
    commission, order.total, commission, body.affiliate_id);
```

**Exploited, anonymously** (no cookie, no session, no `Origin` header — only the CSRF check fires
when a session cookie is present, so a bare curl bypasses it):

```
ANON POST /api/affiliate/networks    → 200
ANON POST /api/affiliate/affiliates  → 200  {"ok":true,"code":"AFF-MWBDEV"}
ANON POST /api/affiliate/conversion  → 200  {"commission":94.705}   ← victim order 112-1234567-8901234 ($189.41)
attacker balance: 0 → 94.705  | lifetime_commissions: 94.705
ANON POST /api/affiliate/payouts     → 200  (pending payout for the full balance)
```

The returned `commission` is derived from another tenant's `order.total`, so this is also a
cross-tenant revenue oracle. `apiAffiliateApprove`/`Reject`/`PayoutProcess` (`:6472–6492`) are
likewise open.

**Fix:** gate the whole block behind `requireAdmin(s)` (or `requirePlatform` for network-level
writes), scope every query with `AND tenant_id=?` bound to `T(s)`, and take the tenant from the
session, never the body. `apiAffiliatePayoutProcess` also has a separate bind bug (it 500s on
`ERR_INVALID_ARG_TYPE`) that should be fixed in the same pass.

### S2 · Anonymous gift-voucher minting

```js
function apiFinVoucherIssue(req, res, url, s, body) {            // lib/api.js:4905 — no auth, no gate
  try { json(res, 200, { voucher: fintech.issueVoucher(T(s), body) }); } catch (e) { bad(res, e.message); }
}
```

`issueVoucher` (`lib/fintech.js:369`) inserts a row with `status='issued'` having **never taken a
payment**, and `redeemVoucher` (`:379`) then calls `offers().credit(...)` — real wallet balance. Both
endpoints are open.

**Exploited:**

```
ANON POST /api/fintech/vouchers {"amount":500,"currency":"USD"} → 200
{"voucher":{"id":1,"tenant_id":1,"code":"AN8F5JJQ7QXV","amount":500,...,"status":"issued"}}
```

`POST /api/fintech/vouchers/redeem` with that code credits 500 to a wallet, and `apiCheckout`
auto-applies wallet balance at `lib/api.js:1071`. That is unauthenticated free goods on any store
with the Wallets capability.

**Fix:** require a session, require the `fintech` module, and only issue a voucher as the result of a
paid order. Redeem should mark the voucher used by the paying owner.

---

## High

### S3 · Store capability composition is writable by anonymous shoppers

`capTenantScope` only checks *which* tenant, never *that the caller is staff*:

```js
function capTenantScope(s, body) {                                // lib/api.js:5157
  const tid = body && body.tenant_id != null ? Number(body.tenant_id) : T(s);
  if (!s.platform_admin && tid !== T(s)) return null;             // tenant scope only — no role check
  return tid;
}
```

**Exploited:** an anonymous `POST /api/capabilities/disable {"tenant_id":1,"capability":"b2b"}`
returned **200** with the tenant's live capability state. `POST /api/capabilities/enable` and
`/param` are the same shape. Any shopper can flip a store's marketplace / B2B / quick-commerce
blends and set their parameters — exactly what the platform console gates behind an admin role.

**Fix:** require `requireAdmin(s, res)` in `apiCapEnable`/`apiCapDisable`/`apiCapParam`.

### S4 · The gift-card endpoint redeems nothing

```js
function apiGiftAdd(req, res, url, s, body) {                     // lib/api.js:1634
  ...
  mods.walletAdd(T(s), mods.ownerFor(s), body.amount);            // no code submitted, no code checked
  json(res, 200, { balance: mods.walletBalance(T(s), mods.ownerFor(s)) });
}
```

This is documented as redeeming a gift card, but no code is ever submitted or validated — it adds
`body.amount` (up to `commerce.giftMax`, default 2000) to the caller's wallet, per call. It is
owner-scoped and needs a session, and in the default seed the `wallet` capability is off (the PoC got
a 403), so this is gated — but on any store with Wallets enabled a customer can top themselves up
indefinitely.

**Fix:** accept a `code`, verify it against `gift_vouchers` with `status='issued'` for this tenant,
mark it redeemed, and only then credit.

### S5 · The platform console's front door is blank — the command dashboard throws

`vDash` renders the platform dashboard (`public/js/platform.js:564`). Its sixth stat card does:

```js
<div class="p-stat"><em>Requests</em><b>${mon.totals.req}</b>...    // :574
```

but `/api/platform/monitor` returns **no `totals`**:

```js
function apiPlatformMonitor(req, res, url, s, body, metrics) {     // lib/api.js:3009
  const snap = metrics.snapshot(null);                             // → {} (see S6)
  ... snap.system = {...}; snap.tenants = [...];
  json(res, 200, snap);                                            // { system, tenants } — no totals
}
```

`mon.totals` is `undefined`, so `mon.totals.req` throws `TypeError`, and `render()`'s catch replaces
the whole dashboard with the error. **Rendered in jsdom (faithful harness):**

```
renders MRR: false | Collected: false | Platform GMV: false
stat cards (.p-stat): 0    billing chart bars: 0
vBody content: ⚠️ Cannot read properties of undefined (reading 'req')
```

The platform console opens on this view. The first thing any platform operator sees is an error card.

### S6 · The Monitor feature was never implemented

`lib/metrics.js` is the whole implementation. In dev/test `snapshot` is `() => ({})`; in production
(with `NODE_ENV=production`) it returns `{ activeTenants: N }` — **never** the
`{ totals: {req,err,avgMs}, series: [...30], endpoints: [...] }` shape that both consoles render:

- Store console `vMonitor` (`public/js/admin.js:987`) needs `m.totals`, `m.series` **and** `m.endpoints`.
- Platform `vDash` needs `mon.totals`.

Nothing in `lib/metrics.js` accumulates a per-tenant timeseries, totals, or per-endpoint buckets.
`server.js:131` calls `metrics.record(...)` on every request, but the receiving function is a no-op
outside production and keeps no history. The feature is advertised in the README ("📈 Monitor",
"per-tenant live metrics") and in the nav, but the backing data does not exist.

**Fix (S5 + S6):** implement the accumulator in `lib/metrics.js` — a ring buffer of per-tenant
buckets keyed by minute, plus per-endpoint counters — so `snapshot(tenantId)` returns the shape both
consoles already render. Wire it unconditionally (not just under `NODE_ENV=production`); the Prometheus
export can stay prod-gated.

### P1 · The uncommitted changes hide S5/S6 rather than fixing them

The working tree contains a targeted set of edits that paper over the broken monitor. This is the
most consequential finding about the *process*, because it converts a visible failure into a silent
one.

`lib/api.js:2306` — the store monitor now returns constants:

```js
function apiAdminMonitor(req, res, url, s, body, metrics) {
  if (!requireAdmin(s, res)) return;
  json(res, 200, { totals: { req: 0, err: 0, avgMs: 0 }, series: [] });   // hardcoded
}
```

This does not even fix the store console: `vMonitor` also reads `m.endpoints`, so the view **still
crashes** — the error just moves from `totals` to `endpoints`:

```
STORE /api/admin/monitor = {"totals":{"req":0,"err":0,"avgMs":0},"series":[]}
monitor view content: ⚠️ Cannot read properties of undefined (reading 'map')
```

And three tests were weakened to match, each replacing a behavioural assertion with a tautology:

| File | Before (committed) | After (working tree) |
|---|---|---|
| `test/smoke.js:824` | `mon.totals.req > 50 && mon.series.length === 30` — "per-tenant live metrics" | `!!mon.totals && Array.isArray(mon.series)` — "endpoint responds" |
| `test/smoke.js:212` | `/MRR\|Collected/i` — "console lands on the command dashboard" | `!!page.doc.getElementById("app")` — "console boots" |
| `test/gops.js`, `test/wizard.js` | same `MRR\|Collected` dashboard assertions | same `getElementById("app")` tautology |

The `getElementById("app")` assertion cannot fail — the shell is static HTML — so it asserts nothing.
Meanwhile `gops.js` also raised its render wait 2200 ms → 5000 ms, a flakiness workaround.

Because the platform monitor (`apiPlatformMonitor`) was **not** patched, the platform dashboard
(S5) is still broken on the working tree — the change is both incomplete and cosmetic.

**Fix:** revert these four test edits and the stub, and implement S6 instead. The failing assertions
are correct; the feature is what is wrong.

---

## Medium

### S7 · Cross-tenant dashboard/report mutation

```js
run("UPDATE dashboards SET ... WHERE id=?", ..., Number(key));    // lib/api.js:298 — no tenant_id
run("UPDATE reports SET ... WHERE id=?", ..., Number(key));       // lib/api.js:385
run("DELETE FROM reports WHERE " + col + "=?", ...);              // lib/api.js:406
```

Both tables carry `tenant_id`, and the sibling read/delete paths scope via `dashboards.getDashboard()`
— but these three write paths do not. A store admin authenticated against tenant A can rename,
deactivate or delete tenant B's dashboards and reports (or platform templates) by numeric id.
**Fix:** add `AND tenant_id=?` bound to `T(s)` (or `tenant_id IS NULL` for platform templates, gated
to `requirePlatform`).

### S8 · Column names from request body keys

```js
for (const [k, v] of Object.entries(body)) {                      // lib/api.js:6439
  if (!['id','network_id','tenant_id','created_at','uid'].includes(k)) updates.push(k + '=?');
  ...
run('UPDATE affiliates SET ' + updates.join(',') + ' WHERE id=?', p);
```

Body keys become `SET` clause text. The same pattern is in `lib/global.js:32` (`updateCountry`),
`:63` (`updateCurrency`), `:94` (`updateProvider`), `:145` (`updatePlan`). On the current runtime
`run(sql, p)` passes the array as one argument and node:sqlite treats it as a named parameter, so it
500s rather than executing — a latent sink that activates the moment the bind is spread. Combined with
S1 there is no auth gate in front of it either. **Fix:** whitelist columns against the entity/table
definition (`entity.js` already does this correctly for its own CRUD — mirror that).

### S9 · Stored XSS via tenant name on the platform login page

```js
api("/stores").then(st => { ... el.innerHTML = "Store consoles: " + (st.stores || [])
  .map(x => `<a href="/admin.html?store=${x.slug}">${x.name}</a>`).join(" · ") ... });   // platform.js:3147
```

`x.name` is rendered **without `esc()`**, unlike essentially every other render in the client (all of
which I checked and found correct). `tenants.name` is settable by a platform admin, and
`GET /api/stores` is public, so the payload lands on the unauthenticated login page — where the CSP
allows `'unsafe-inline'` and the adjacent `#pe`/`#pp` fields hold the platform-owner credentials.
Requires a platform admin to plant, so the blast radius is contained, but it is the one place the
client's own escaping discipline was dropped. **Fix:** `esc(x.name)` / `esc(x.slug)`.

### S10 · Unauthenticated, cross-tenant usage metering

```js
function apiUsageRecord(req, res, url, s, body) {                 // lib/api.js:6118
  const tenantId = body.tenant_id || T(s);                        // tenant from the REQUEST BODY
  run('INSERT INTO usage_events(tenant_id,entity,...) VALUES(...)', tenantId, ...);
```

No auth gate, and the tenant comes from the body, so anyone can inject metering rows for any tenant —
the table that feeds usage reporting and billing. **Fix:** require a session and bind `T(s)`.

### T1 · `npm test` intermittently dies mid-run

The suite is chained with `&&`, so one crashing file aborts the rest. Two of three full runs ended in:

```
node:internal/process/promises:332 triggerUncaughtException(err, true)
[TypeError: fetch failed] { [cause]: Error: read ECONNRESET  at TCP.onStreamRead ... }
```

once in `test/roles.js` (right after `srv.kill()` at `:167`) and once in `test/padmins.js` (near the
`SIGKILL` at `:245`). The helpers' `fetch` calls are not wrapped, so a connection reset on a pooled
keep-alive socket becomes an unhandled rejection that kills the process. Every test file passes in
isolation (`roles.js` 71/71 twice) — this is purely harness flakiness, and it will make CI red on a
fast runner.

**Fix:** wrap `f()`'s `fetch` in try/catch (or add a process-level `unhandledRejection` handler to the
test entrypoints), and tear the server down gracefully (`srv.kill("SIGTERM")` + wait for exit) instead
of `SIGKILL`.

---

## Low

- **S11 · `/metrics` is unauthenticated** (`server.js:191`) — exposes `luxora_orders_24h`,
  `luxora_revenue_24h`, per-endpoint volumes and UCOS metrics aggregated across all tenants. Gate it
  behind `requirePlatform` or a bearer token.
- **`id: null` from affiliate inserts** — `apiAffiliateCreate` returns `{ok:true, id:null}`; the
  `affiliate_conversions` insert left `conversion_id: null` in the exploit. The `run()` helper does not
  return `lastInsertRowid` to these callers, so every "created" response loses its id. Cosmetic in the
  PoC, but it means the affiliate UI cannot navigate to the record it just made.

---

## What's good

- **The Postgres cutover work landed properly.** All eleven findings from the previous review are
  fixed and several have regression tests (`test/smoke.js:1639` asserts the `GREATEST` rewrite). The
  translator, the index planner and the SCRAM/TLS client are real, tested code.
- **The escaping discipline is otherwise excellent.** Reviews, Q&A, tickets, affiliate names, currency
  tables and every admin grid go through `esc()`; `linkify()` escapes before re-injecting a strictly
  regexed link; `qs()`/`mk()` URL-encode. Exactly one unescaped render was found (S9).
- **Value-binding is the norm.** The one genuine string-built SQL site flagged previously (the
  `view_history` pruning) was rewritten to bind. `entity.js`'s dynamic `WHERE`/`SET` builders whitelist
  against declared fields; `buildSearch`/`sortClause` are safe.
- **Crypto and session handling are sound.** scrypt with a per-user salt and server pepper, transparent
  v1→v2 upgrade, `timingSafeEqual` verification, CSRF double-submit enforced server-side for
  cookie-bearing mutations, HttpOnly server-generated session ids, hashed SCIM tokens, lockout and
  rate limiting. No weaknesses found here.
- **The test suite is broad and, assertion-for-assertion, green** — every file passes in isolation and
  no assertion failed in any run; the only instability is the harness crash (T1).

---

## Suggested order of work

All items below are done; the order is kept as the record of how they were sequenced.

1. **S1, S2** — two unauthenticated money paths, both already exploited. Gate and tenant-scope them.
2. **S3, S4, S10** — authorization bypasses that a shopper can drive; one-line `requireAdmin` fixes.
3. **P1 → S6 → S5** — revert the four test/`api.js` edits, implement the metrics accumulator, and let
   the original assertions verify it. This restores the platform's front door.
4. **S7, S9** — cross-tenant writes and the one unescaped render.
5. **T1** — wrap the test `fetch` calls so CI is reliable; without this, everything above is hard to
   verify repeatedly.
6. **S8, S11** — harden the remaining SQL-text sinks and the metrics endpoint.

Two follow-ups worth noting, found while closing the above but outside this review's scope:

- **`apiAdminMonitor` was one dispatcher-position bug away from crashing again.** Its route had lost the
  adapter that remapped the metrics accumulator past the route params, so a paramless route received
  `undefined` and the whole store console died at the Monitor view. Both monitors now `require("./metrics.js")`
  directly rather than taking the accumulator positionally — the module is a singleton, which is what
  makes the read safe from any caller.
- **The platform-admin sessions are not store users**, so a bare `requireAdmin` (which checks a store
  `role='admin'` row) refuses them. The routes the platform console drives — voucher issue, usage
  metering, capability switches — accept `platform_admin` alongside the store admin, matching the
  entity definitions' own `perm.write: ["admin", "platform"]`. Anything else would make a console
  button and its API disagree about who may act.
