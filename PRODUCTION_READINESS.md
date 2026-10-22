# Production Readiness — LUXORA

Assessment of release readiness, 2026-10-22. Every status below comes from a command that was
run and whose output was read, and the evidence for each is recorded here. Statuses:
**PASS** (verified), **FAIL** (verification failed or the condition is not met), **BLOCKED** (needs
an external decision, credential, service or authorization), **N/A** (justified by scope),
**NOT VERIFIED** (not enough evidence).

Runbooks: [DEPLOYMENT_RUNBOOK.md](DEPLOYMENT_RUNBOOK.md) ·
[DATABASE_RECOVERY_RUNBOOK.md](DATABASE_RECOVERY_RUNBOOK.md) ·
[OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md)

## Decision: NO-GO for production today

Use the repository-side work as the basis for a **staging rehearsal**, not a production launch. The
code no longer has a known critical defect that makes a production deployment unsafe by itself.
Launch is blocked by things this repository cannot supply:

1. **No live payment provider has been verified** (PR-025). In production, card checkout is now
   declined until a live gateway is connected (PR-001), so the store can only take cash on
   delivery and bank transfer until one is.
2. **No staging environment, deployment target, DNS/TLS or secret store** has been named
   (PR-026, PR-027).
3. **Pending payments are never reconciled** (PR-014). Verified inbound webhooks are recorded,
   but nothing moves an order from `pending` to `paid` or handles refunds and chargebacks.
4. **CI has not run on the release commit.** The workflow changes are in this branch, and a run
   is triggered by push or PR (PR-013).
5. **Off-host backups, alerting and on-call** have to be set up in the target environment
   (PR-012, PR-015).

The decision moves to **GO** when every item in "Exit criteria" at the end of this document is
PASS.

## Baseline

| | |
|---|---|
| Repository | `echelonxventures-Projects/universal-product` |
| Baseline commit | `441d772` (= `origin/master`, "Merge pull request #2 … critical-route-audit") |
| Working branch | `claude/exciting-hamilton-kqmbhr`, which started at `441d772` with a clean tree |
| Open PRs not in the baseline | #3 `feat/production-readiness` (51 commits, about 86k lines; last CI run on 2e28c3c **failed**), #4 `claude/modest-babbage-kyejdn` (context-continuity system; last completed CI run on fc8111a **succeeded**, newer run in progress). Neither is merged or assessed here. The `context:*` scripts named in the brief exist only in PR #4 and **are not on master**. |
| CI on the baseline commit | No workflow run found for `master` / `441d772` through the Actions API — **NOT VERIFIED** |
| Runtime | Node `>=22.13` (`node:sqlite`); CI matrix 22.13 / 22 / 24; verified locally on 22.22.0 |
| Architecture | Dependency-free Node HTTP server (`server.js`, `lib/api.js` with about 8,000 lines and 682 routes), SQLite in WAL mode, optional Redis (Bull) queue, static consoles in `public/`, sealed registry in `_registry/` |
| Production database | SQLite on a persistent volume, one instance. PostgreSQL is not production-ready (PR-007). |

### Baseline verification (before any change)

| Check | Result |
|---|---|
| `npm ci` | exit 0; 3 advisories (1 high, dev-only; 2 moderate) |
| `npm test` on `441d772` | **exit 0**, 1,773 passing assertions, 0 failing, 27 min 3 s |
| `npm run registry` | exit 0 — 15 gate checks green, seal verified, no drift |
| Production-mode reproduction | card checkout with no live gateway → `200`, `payment_status: "captured"`, `txn_ref: stripe_sim_…` (PR-001) |

## Requirements and gap register

Severity: P0 = must not ship, High, Medium, Low.

| ID | Sev | Finding | Change | Verification | Status |
|---|---|---|---|---|---|
| PR-001 | P0 | In production, checkout through any card gateway that was not `live` with credentials fell through to a **simulated capture**: the order was recorded as paid and `order.paid` fired with no money taken. The production guard only covered store-invoice payment. Platform invoices had the same problem. | `settlePayment` (`lib/api.js`) refuses a simulated *capture* when `NODE_ENV=production` unless `LX_ALLOW_SIMULATED_PAYMENTS=1`. Pending methods (cash on delivery, bank transfer) and zero-amount (fully wallet-paid) orders are unaffected. Every caller already treats `failed` as a decline. | Reproduced live (200/captured), then 402 after the fix. `test/production.js` covers it, with a mutation check: reverting the fix fails 2 assertions. Verified again in the container. | PASS |
| PR-002 | P0 | The fraud screen fingerprinted a missing card as `"<gateway>:<method>"`, a value shared by **every** customer, and the storefront never sends a card. Card velocity therefore counted the whole store's orders: from the **8th order per hour per payment method, every checkout was blocked** (`fraudScreen` is on by default). | The risk input carries the card only when the caller supplies one (`lib/api.js`, checkout). | Found under load (all checkouts 403). Test: 10 customers paying cash on delivery all succeed. Mutation: orders 7–10 are blocked. | PASS |
| PR-003 | High | With `LUXORA_MASTER_KEY` set, **console key rotation made every sealed credential undecryptable** after the next restart: secrets were re-wrapped under a random key, and the next boot mapped that version to the env key again. | `rotateKey` refuses when the key comes from the environment, and the API answers 409 with the reason. The runbook gives the procedure. Rotation also names the new version after the highest existing one: counting keys gave a keyring holding only `k2` the name `k2` again, overwriting the live key. That surfaced when the mutation check of this fix left exactly such a keyring in the local dev `data/`, and `test/smoke.js` then failed its rotation assertions. | Reproduced in isolation (unseal throws after rotate and restart). Tests: 409 with an env key; rotating a `k2`-only keyring adds `k3` and keeps `k2` readable. Mutations: 200, and `k2` overwritten. `test/smoke.js` passes 760/0 from that keyring with the fix. | PASS |
| PR-004 | High | A non-hex `LUXORA_MASTER_KEY` decoded to a **zero-length key**. Boot succeeded, and every seal or unseal then threw `ERR_CRYPTO_INVALID_KEYLEN` at request time. | Fail fast at boot. A short hex key is refused in production and still zero-padded in development, for compatibility. | Boot exits 1 with a clear message, in a test. | PASS |
| PR-005 | Medium | On SIGTERM the server closed the plain `server` even under TLS, where it had never listened, so nothing drained, and it exited after a hard 2 s. | Closes the real listener, closes idle keep-alives, `/readyz` turns 503, drain bounded by `LX_SHUTDOWN_MS` (8 s). | In-flight request completes with 200 while new connections are refused, exit 0, under HTTP and TLS. In the container, `docker stop` takes 260 ms with exit 0. | PASS |
| PR-006 | Medium | There was no readiness probe; `/healthz` answers even when the database is gone. | `GET /readyz` checks `SELECT 1` and draining, and reports `diskFreeMb`. | 200 in a test and in the container; `diskFreeMb` reads 0 on a full disk. | PASS |
| PR-007 | High | The **PostgreSQL path is not production-ready** (measured against PostgreSQL 16.15). (a) MD5 auth sent the wrong hash, so no password-authenticated server ever accepted it. (b) SCRAM, the default since PG 14 and on managed Postgres, is not implemented. (c) `migrate.apply` claims one transactional connection but opened **103,686 connections**, one per statement, so its BEGIN/ROLLBACK do nothing and a failed run leaves the target half-migrated. (d) The DDL for `dashboard_widgets` fails on the reserved word `column`. (e) The request-path bridge opens a connection per query. (f) Migrating 27 MB / 103k rows took 8.5 min. | (a) fixed (`lib/pg.js`, with a known-vector test; mutation fails). (b)–(f) not changed: Postgres is out of scope for this release. | Run against an isolated local PostgreSQL 16 with a seeded database. | FAIL (out of scope; SQLite is the release database) |
| PR-008 | High | `docker-compose.yml` published Redis, **without a password, on the host's public interfaces** (`6379:6379`). | Removed the port mapping (internal network only), set `appendonly yes`, bound the app to loopback for a TLS proxy, set `stop_grace_period` and `mem_limit`. | `docker compose ps`: Redis `6379/tcp`, not published. Queue worker RUNNING. | PASS |
| PR-009 | Medium | The image ran as **root** on an unpinned base, with a 20 s health start period (first boot takes about 30 s). | `USER node`; code root-owned and read-only; only `/app/data` and the sticky `/app/_registry` are writable; base pinned by digest (`node:22.23.4-alpine@sha256:fe4f6d74…`); start period 90 s. | `id -u` = 1000; writing `server.js` is denied; deleting registry sources is denied; boot, restart and stop are clean. | PASS |
| PR-010 | Medium | The build context shipped **locally compiled registry artifacts** (34 MB, sealed with the build machine's key). In the container they failed verification, and as non-root they could not be replaced, so the registry was recompiled silently on every boot. | `.dockerignore` excludes `_registry/canonical.{lxr,json}` and `backups/`. | After a rebuild, a warm restart logs no "would not verify", and the artifacts are owned by the runtime. | PASS |
| PR-011 | Low | `PLATFORM_PASSWORD=platform123`, set explicitly, passed the production guard. | Documented defaults are refused even when set. Warnings for `LX_ALLOW_SIMULATED_PAYMENTS=1` and an unset `LUXORA_PEPPER`. The guard message now matches the behaviour: it checks on every boot. | Test. | PASS |
| PR-012 | High | There was **no backup or restore mechanism**. | `scripts/backup.js` (`VACUUM INTO`, integrity check, sha256 and row-count manifest, optional AES-256-GCM) and `scripts/restore.js` (verifies checksum, decryption, integrity and row counts before moving into place; never overwrites without `--force`). Added `npm run backup` / `restore` and a CI drill. | Live backup during traffic; restore of a 27 MB encrypted backup with full verification in 0.4 s; production boot on the restored database in 4.7 s with the original credentials working. Wrong passphrase, tampering and no-overwrite are each refused, in tests. | PASS (tooling) / BLOCKED (schedule, off-host copy, alerts need the target environment) |
| PR-013 | Medium | CI did not audit runtime dependencies, did not start the server in production mode, and built the image without running it. | Added: `npm audit --omit=dev --audit-level=high`; `/readyz` in the boot smoke; a backup/restore drill; a container smoke test (refuses seed credentials, boots non-root with secrets, clean stop). | Each step was run locally. | NOT VERIFIED in GitHub Actions until this branch's run completes |
| PR-014 | High | **Asynchronous payment state is not reconciled.** `POST /api/webhooks/inbound/:provider` verifies the HMAC (with a 5-minute window for timestamped schemes, fail-closed without a secret) and records the event, but no handler updates payments or orders. Pending payments stay pending; refunds and chargebacks from the provider are not applied. | None. This is feature work that needs a chosen provider and its sandbox. | Code read; the webhook tests in the suite cover signature handling only. | FAIL (open) |
| PR-015 | Medium | No on-call rota, escalation contacts or alert routing exist. | OPERATIONS_RUNBOOK.md defines the signals, thresholds and procedures. | — | BLOCKED (owner) |
| PR-016 | Medium | Money is computed in JS floating point, rounded with `toFixed(2)`, not in integer minor units. No error was observed, but sums over many lines can drift by a cent. | Not changed: a rewrite of pricing is out of proportion for this pass. | Code read. | OPEN (accepted risk, needs owner sign-off) |
| PR-017 | Medium | A full disk fails **every** API call, reads included, because each request writes the session table. `/readyz` cannot usefully gate on this for a single instance. | `diskFreeMb` reported in `/readyz`; alert thresholds in OPERATIONS_RUNBOOK.md. | Measured: 500 `{"error":"internal"}` with no detail leaked; the process stays up; it recovers by itself when space is freed; `integrity_check` ok. | PASS (mitigated) |
| PR-018 | Medium | The password KDF (scrypt N=2^17, r=8) uses about 128 MiB per hash. Eight concurrent sign-ins took the process to **843 MB**. The 1 GB compose limit first proposed was too tight. | Compose `mem_limit: 2g`; sizing documented. | Load test. | PASS (mitigated) |
| PR-019 | Medium | **Single instance only:** one SQLite writer, a per-process checkout lock, per-process rate limits unless `LX_RATELIMIT=redis`. | Documented as the supported topology. | — | ACCEPTED limitation |
| PR-020 | Low | `npm audit`: `source-map-js` high (dev-only, through jsdom); `uuid` moderate through `bull`. | Lockfile bumps `source-map-js` to 1.2.2. The `uuid` advisory affects only v3/v5/v6 with a `buf` argument, and bull calls only `v4()`; the fix would be a breaking downgrade of bull. | `npm audit --omit=dev --audit-level=high` exits 0. | PASS / ACCEPTED (uuid) |
| PR-021 | Low | Inbound webhooks: no event-id de-duplication (only the time window), and unsigned payloads are stored too (bounded by the API rate limit). There is no effect on state today (PR-014). | None. Must be built together with PR-014. | Code read. | OPEN |
| PR-022 | Low | `/healthz` is public and returns the store slug and product count. | None (low value to an attacker). | — | ACCEPTED |
| PR-023 | — | The security fixes from PR #1 and PR #2 (in the baseline) are covered by `test/security.js` and the route-audit suites, all passing. | — | `npm test` | PASS |
| PR-024 | — | Open PR #3 changes the same core files (`server.js`, `lib/api.js`, `lib/db.js`, Dockerfile, CI). Merging it after this branch, or this branch after it, needs a conflict resolution and a full re-verification. | — | `git diff --stat` | NOTE |
| PR-025 | P0 for launch | **No external provider is live-verified.** Payment, notification, shipping, tax and AI connectors were exercised only on simulated or offline paths. | — | — | BLOCKED (credentials and sandbox accounts) |
| PR-026 | — | No staging environment. | — | — | BLOCKED |
| PR-027 | — | No deployment target, DNS, TLS certificate, secret manager or log/metrics backend. | — | — | BLOCKED |

## Security assessment

Coverage and method: the repository's own security suites (`test/security.js`, `authz`, `tenancy`,
`roles`, `padmins`, `identity*`, `webauthn`, and route audits from earlier reviews) all pass. This
pass added targeted manual review and live probing of payment settlement, risk screening, key
management, the boot guards, the container and compose exposure, inbound webhooks, response
headers and secret exposure in the tracked tree. **No penetration test, DAST or SAST scanner was
run, and no certification is implied.** Tools available and run: `npm audit`, a `git grep` secret
scan, and HTTP probes.

| Area | Finding | Status |
|---|---|---|
| Payment integrity | PR-001 (simulated capture), PR-014 (no reconciliation) | fixed / open |
| Availability abuse | PR-002 (one card fingerprint shared by all customers blocked the store) | fixed |
| Key management | PR-003, PR-004 | fixed |
| Network exposure | PR-008 (unauthenticated Redis published) | fixed |
| Container | PR-009 (root), PR-010 (baked artifacts) | fixed |
| Authentication | scrypt + pepper, lockout, per-IP auth rate limit 30/min, default credentials refused in production, CSRF double-submit, origin check on mutations, `HttpOnly`/`SameSite=Lax` session cookie (`Secure` under TLS) | verified present (suites + probe) |
| Headers | CSP `default-src 'self'` … `frame-ancestors 'none'`, `nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: same-origin`, `Permissions-Policy`; HSTS when TLS terminates in-process | verified by probe |
| Errors and logs | 500 answers `{"error":"internal"}`; the request log carries no bodies or cookies | verified (disk-full test, code read) |
| Secrets in the repository | none. The only match is a fake `sk_live_SUPERSECRET42` test fixture in `test/smoke.js`. Keyrings and databases are gitignored and dockerignored. | verified |
| Dependencies | PR-020 | fixed / accepted |
| Webhooks | HMAC over raw bytes, constant-time compare, 5-minute window, fail-closed; PR-021 | partial |

No unresolved critical or high **exploitable** finding was left silent. The open highs (PR-007,
PR-014) are scope and feature gaps, recorded here, and both block launch only through the exit
criteria below.

## Capability status

| Capability | Status |
|---|---|
| Storefront browse, search, cart | implemented; exercised by the suites and the load test |
| Checkout with cash on delivery or bank transfer | implemented; `pending`; verified end to end in production mode and in the container |
| Checkout with a card gateway | **simulated** outside production; **declined** in production until a live gateway is connected; live capture **not verified** (PR-025) |
| Refunds, payment reconciliation, chargebacks | **not implemented against a provider** (PR-014) |
| Notifications (email/SMS) | logged only unless a live channel is configured; **not verified live** |
| Shipping and tax providers | registry-driven rates and rules; external APIs **not verified live** |
| Redis queue | verified: the worker runs, the app survives a Redis outage, and the queue recovers |
| Multi-tenant isolation, roles | covered by the existing suites (pass) |
| PostgreSQL | **not production-ready** (PR-007) |
| Backups and restore | tooling verified; scheduling environment-specific |

## Load and resilience (measured)

Environment: 4 vCPU sandbox, Node 22.22.0, `NODE_ENV=production`, SQLite on local disk, one
process. The load generator ran on the same host, with distinct clients through
`X-Forwarded-For` and `LX_TRUST_PROXY=1`. Each phase lasted 15–20 s. These are indicative figures,
not a capacity guarantee.

| Workload | Clients | Throughput | p50 | p95 | p99 | 5xx | Peak RSS |
|---|---|---|---|---|---|---|---|
| Browse (list, product, search, config) | 16 | 202 req/s | 70 ms | 147 ms | 182 ms | 0 | 254 MB |
| Browse | 64 | 215 req/s | 268 ms | 392 ms | 600 ms | 0 | 327 MB |
| Checkout (cash on delivery), new customer per order | 8 | 122 req/s (about 61 orders/s) | 55 ms | 123 ms | 144 ms | 0 | 199 MB |
| Checkout | 32 | 155 req/s (orders capped, see below) | 162 ms | 340 ms | 570 ms | 0 | 211 MB |
| Admin sign-in (scrypt) | 8 | 5.6 /s | 1.5 s | 1.66 s | 1.78 s | 0 | **843 MB** |

The 32-client checkout phase hit the store plan's cap of 2,000 orders/month (402, by design). One
64-client browse request took 9.4 s (max); its cause was not isolated.

| Failure | Result |
|---|---|
| Redis stopped under load | app keeps serving (checkout ok); one queue error logged; recovers when Redis returns |
| Disk full | API 500s, process up, recovers when space is freed, `integrity_check` ok (PR-017) |
| SIGTERM with a request in flight | request completes; new connections refused; exit 0 |
| Container restart | session, keyring and registry seal persist on the volume; ready in 7–9 s |
| Missing or default secrets, bad master key | refuses to boot with a clear message |
| Webhook with a bad or missing signature | 401, fail-closed (code and suites) |
| Not tested | database lock contention from a long export, provider timeouts (no live provider), interrupted Postgres migration (out of scope), expired TLS certificate |

## Release evidence

| Item | Value |
|---|---|
| Release candidate | this branch's head commit (recorded in the PR) |
| `npm test`, final tree | **exit 0 — 1,796 passing assertions, 0 failing**, 25 min 7 s, Node 22.22.0. An earlier run of this tree failed 2 rotation assertions in `test/smoke.js`; the cause was a dev keyring corrupted by this pass's own mutation check, and it exposed a real defect, fixed in PR-003. |
| `node test/production.js` | 23 passed, 0 failed (also part of `npm test`); each fix mutation-checked |
| `npm run registry`, final tree | exit 0 — 15 gate checks green, seal verified, no drift |
| Container | built from the final tree (the sandbox build differs only by a proxy CA bind-mount on the `npm ci` step; image `sha256:09ffaa06…`, local). The CI smoke script was run verbatim: refuses seed credentials; ready; uid 1000; backup and verify inside the container; `docker stop` exit 0. Image contents: no `data/`, no compiled registry. Record the CI-built digest at release. |
| Compose | redis + app, worker RUNNING, Redis not published |
| Postgres probe | PostgreSQL 16.15, isolated, local; results in PR-007 |
| Restore drill | 27 MB / 245 tables / 102,933 rows, encrypted; verify and restore 0.4 s; production boot 4.7 s; sign-in ok |
| GitHub Actions on the release commit | NOT VERIFIED (pending the push) |
| Deployment | not performed (not authorized; no target) |

## Exit criteria

| Criterion | Status |
|---|---|
| Repository and release baseline established | PASS |
| Critical functional and architectural defects resolved | PASS for those found (PR-001 to PR-005, PR-008 to PR-012) |
| Tests pass on supported runtimes | PASS on 22.22.0 locally; 22.13 / 22 / 24 NOT VERIFIED until CI runs |
| CI passes on the exact release commit | NOT VERIFIED |
| Security findings assessed; critical and high addressed or recorded | PASS |
| Database strategy validated against the target | PASS for SQLite (single instance); FAIL for Postgres (out of scope) |
| Backup restoration demonstrated | PASS (tooling and drill) |
| Production secrets validated without exposing values | PASS for the format and presence guards; BLOCKED for real values |
| Container and deployment configuration validated | PASS locally |
| Critical end-to-end journeys | PASS for browse, cart, cash-on-delivery checkout and admin sign-in; BLOCKED for live card payment |
| External providers classified | PASS: all simulated or unverified (PR-025) |
| Observability, alerts and runbooks | PASS (documents); BLOCKED (alert wiring) |
| Load and resilience limits | PASS (measured, single host) |
| Staging rehearsal | BLOCKED (PR-026) |
| Release approval and deployment authorization | BLOCKED (not given) |
| Production deployment and smoke tests | N/A (not authorized) |
| Residual risks documented with owners | PASS (this register; the owner must assign names) |

### To reach GO

1. Merge this branch through review. Reconcile it with PR #3 and PR #4 if they land first, then
   re-run the full suite.
2. CI green on the merge commit across 22.13, 22 and 24, including the new container smoke test.
3. Name the deployment target, secret store, DNS and TLS. Deploy to staging with the
   DEPLOYMENT_RUNBOOK.md procedure.
4. Connect one payment provider in its sandbox. Verify capture, decline, refund and the
   webhook-driven state change. This needs PR-014 to be implemented.
5. Schedule backups with an off-host copy; run and record a restore drill in staging.
6. Wire the alerts in OPERATIONS_RUNBOOK.md and name the on-call rota.
7. The owner signs off PR-016 and PR-019 (or schedules them) and gives the production
   authorization.

Missing information needed from the owner: hosting target and region; secret-store mechanism;
domain and certificate source; payment provider and sandbox credentials; notification provider;
expected traffic (orders/day, peak concurrency, catalogue size) to check against the measured
limits; backup destination and retention; on-call contacts.
