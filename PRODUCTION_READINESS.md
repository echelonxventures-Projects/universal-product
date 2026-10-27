# Production Readiness — LUXORA

Assessment of release readiness, 2026-10-22; **updated 2026-10-27 for the integrated release candidate** (PR #5 + PR #4 + PR #3 + the preserved Offers work — see "Integrated release candidate"). Every status below comes from a command that was
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
3. **Provider-side events are only partly applied** (PR-014). Since PR #3, signed webhooks and a
   lookup sweep move pending payments to captured or failed; refunds issued at the provider and
   chargebacks/disputes are still not applied, and nothing is verified against a live provider.
4. **Money is binary floating point** (PR-016). Rounding differs from any stated policy by a
   cent in reproducible cases. There is no remediation and no owner risk acceptance.
5. **Refunds are full-amount only** (PR-029). Since PR #3 a live payment is refunded through the
   provider (a refusal leaves it unchanged); partial refunds do not exist.
6. **Off-host backups, alerting, on-call, staging and deployment approval** have to be provided
   by the target environment and the owner (PR-012, PR-015, PR-026, PR-027).

CI runs on the draft PR
[echelonxventures-Projects/universal-product#5](https://github.com/echelonxventures-Projects/universal-product/pull/5)
(PR-013). Passing CI is required but does not authorize deployment. The decision changes only when
every gate in "Release gates" at the end of this document is PASS and a named owner authorizes
release.

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

## Integrated release candidate (2026-10-27)

One branch combines the three open PRs and the work that was only in a local working tree.
It is local: nothing is pushed, merged into `master` or deployed.

| | |
|---|---|
| Workspace | fresh clone `/Users/bipin/Workspaces/LUXORA-production-integration-2026-10-27` (outside iCloud; own `.git`) |
| Branch | `integration/luxora-production-go-2026-10-27` from `master` `441d772d661abc6626d4497391c6f6261b086a0a` |
| Sources | PR #5 `9b4dc6ff1263b7acf2d6d81a0548bef209362f56` · PR #4 `28109c4338b5a58a893a157cb80421b052a7ff22` · PR #3 `4ab4800398e798451df8205036ef4350bf008e98` · the local working tree, preserved and checksum-verified in `~/LUXORA-preservation/2026-10-27-phase1-feat-production-readiness-4ab4800` |
| Product backlog | [docs/PROJECT-COMPLETION-TODO.md](docs/PROJECT-COMPLETION-TODO.md) — domain completion work; release findings live only here |
| Context and decisions | `PROJECT-CONTEXT/` (from PR #4), changed only through `npm run context:*` |

| Step | Commit | What | Verified there |
|---|---|---|---|
| 1 | `e778743` | PR #5, no-ff merge, no conflicts | — (PR #5 CI green on its head) |
| 2 | `2dfc884` | PR #4, squashed (its 11 `ctx-test` commits carried real work into the branch; their content is kept); 3 additive conflicts | `context:verify`, `context:restore-check` |
| 3 | `3f83262` | context test accepts a live-diverged README (PR #5 edits it) | full `npm test` **exit 0**, 32 min 48 s, Node 22.21.1 |
| 4 | `b5e8c88` | PR #3, three-way merge, 8 conflicts resolved file by file; PR-031–PR-033 fixed | targeted suites |
| 5 | `63b48d7` | the preserved local work, unchanged (39 files byte-identical, 4 combined) | — (it does not boot: PR-030) |
| 6 | `376f45b` | the Offers split completed: boots, one owner per screen/route, ratchets unchanged | gates + targeted suites |
| 7 | `7e2981f` | PR-028 checked at the gateway boundary | integrations 78/0 + mutation; full chain 162/168 |
| 8 | `532c195` | the six chain failures fixed (PR-038) | targeted suites |
| 9 | `5ed4a76` | Postgres: category-sync SQL, engine-neutral table checks; TASK-REL-0001 | `check:postgres` pass (PR-007) |
| 10 | `b162c4e` | seller roles from the platform master (PR-037) | `test/platform-types.js` 144/0 |
| 11 | `cf65575` | the task record names no other platform | **full chain 168/168** (Release evidence) |

Decisions taken in the merge (each recorded in its commit): backups never carry the keyring
(PR #5's policy) and gain PR #3's retention and off-host upload (encrypted sets only); restore
moves the replaced database aside instead of deleting it; PR #3's `test/production.js` became
`test/delivery.js`; no hard-coded country or currency fallback was taken from either side.

## Requirements and gap register

Severity: P0 = must not ship, High, Medium, Low.

| ID | Sev | Finding | Change | Verification | Status |
|---|---|---|---|---|---|
| PR-001 | P0 | In production, checkout through any card gateway that was not `live` with credentials fell through to a **simulated capture**: the order was recorded as paid and `order.paid` fired with no money taken. The production guard only covered store-invoice payment. Platform invoices had the same problem. | `settlePayment` (`lib/api.js`) refuses a simulated *capture* when `NODE_ENV=production` unless `LX_ALLOW_SIMULATED_PAYMENTS=1`. Pending methods (cash on delivery, bank transfer) and zero-amount (fully wallet-paid) orders are unaffected. Every caller already treats `failed` as a decline. | Reproduced live (200/captured), then 402 after the fix. `test/production.js` covers it, with a mutation check: reverting the fix fails 2 assertions. Verified again in the container. | PASS |
| PR-002 | P0 | The fraud screen fingerprinted a missing card as `"<gateway>:<method>"`, a value shared by **every** customer, and the storefront never sends a card. Card velocity therefore counted the whole store's orders: from the **8th order per hour per payment method, every checkout was blocked** (`fraudScreen` is on by default). | The risk input carries the card only when the caller supplies one (`lib/api.js`, checkout). | Found under load (all checkouts 403). Test: 10 customers paying cash on delivery all succeed. Mutation: orders 7–10 are blocked. | PASS |
| PR-003 | High | With `LUXORA_MASTER_KEY` set, **console key rotation made every sealed credential undecryptable** after the next restart: secrets were re-wrapped under a random key, and the next boot mapped that version to the env key again. | `rotateKey` refuses when the key comes from the environment, and the API answers 409 with the reason. The runbook gives the procedure. Rotation also names the new version after the highest existing one: counting keys gave a keyring holding only `k2` the name `k2` again, overwriting the live key. That surfaced when the mutation check of this fix left exactly such a keyring in the local dev `data/`, and `test/smoke.js` then failed its rotation assertions. | Reproduced in isolation (unseal throws after rotate and restart). Tests: 409 with an env key; rotating a `k2`-only keyring adds `k3` and keeps `k2` readable. Mutations: 200, and `k2` overwritten. `test/smoke.js` passes 760/0 from that keyring with the fix. | PASS |
| PR-004 | High | A non-hex `LUXORA_MASTER_KEY` decoded to a **zero-length key**. Boot succeeded, and every seal or unseal then threw `ERR_CRYPTO_INVALID_KEYLEN` at request time. | Fail fast at boot. A short hex key is refused in production and still zero-padded in development, for compatibility. | Boot exits 1 with a clear message, in a test. | PASS |
| PR-005 | Medium | On SIGTERM the server closed the plain `server` even under TLS, where it had never listened, so nothing drained, and it exited after a hard 2 s. | Closes the real listener, closes idle keep-alives, `/readyz` turns 503, drain bounded by `LX_SHUTDOWN_MS` (8 s). | Tests, HTTP and **TLS**: a request in flight completes with 200 while new connections are refused, exit 0. A request that never finishes holds shutdown only until `LX_SHUTDOWN_MS` (1.5 s in the test). Mutation with the original shutdown code: the TLS in-flight request gets no response, and exit takes 6.3 s. `docker stop`: 260 ms, exit 0. | PASS |
| PR-006 | Medium | There was no readiness probe; `/healthz` answers even when the database is gone. | `GET /readyz` checks `SELECT 1` and draining, and reports `diskFreeMb`. | 200 in a test and in the container; `diskFreeMb` reads 0 on a full disk. | PASS |
| PR-007 | High | The **PostgreSQL path is not production-ready** (measured against PostgreSQL 16.15). (a) MD5 auth sent the wrong hash, so no password-authenticated server ever accepted it. (b) SCRAM, the default since PG 14 and on managed Postgres, is not implemented. (c) `migrate.apply` claims one transactional connection but opened **103,686 connections**, one per statement, so its BEGIN/ROLLBACK do nothing and a failed run leaves the target half-migrated. (d) The DDL for `dashboard_widgets` fails on the reserved word `column`. (e) The request-path bridge opens a connection per query. (f) Migrating 27 MB / 103k rows took 8.5 min. | (a) fixed (`lib/pg.js`, with a known-vector test; mutation fails). (b)–(f) not changed: Postgres is out of scope for this release. | Run against an isolated local PostgreSQL 16 with a seeded database. | PARTIAL — on the candidate (`5ed4a76`) `npm run check:postgres` passes against a local PostgreSQL 16.13 with SCRAM-SHA-256: one-transaction migration (123,615 statements, 0 failed), clean boot, kernel checks, 381 page loads clean (two Postgres-only defects fixed: category-sync SQL, `sqlite_master` probes). (a)–(d) no longer reproduce. **Not verified:** request-path connection handling (e) and migration time at production size (f); no CI run yet. SQLite stays the release database until those are measured |
| PR-008 | High | `docker-compose.yml` published Redis, **without a password, on the host's public interfaces** (`6379:6379`). | Removed the port mapping (internal network only), set `appendonly yes`, bound the app to loopback for a TLS proxy, set `stop_grace_period` and `mem_limit`. | `docker compose ps`: Redis `6379/tcp`, not published. Queue worker RUNNING. | PASS |
| PR-009 | Medium | The image ran as **root** on an unpinned base, with a 20 s health start period (first boot takes about 30 s). | `USER node`; code root-owned and read-only; only `/app/data` and the sticky `/app/_registry` are writable; base pinned by digest (`node:22.23.4-alpine@sha256:fe4f6d74…`); start period 90 s. | `id -u` = 1000; writing `server.js` is denied; deleting registry sources is denied; boot, restart and stop are clean. | PASS |
| PR-010 | Medium | The build context shipped **locally compiled registry artifacts** (34 MB, sealed with the build machine's key). In the container they failed verification, and as non-root they could not be replaced, so the registry was recompiled silently on every boot. | `.dockerignore` excludes `_registry/canonical.{lxr,json}` and `backups/`. | After a rebuild, a warm restart logs no "would not verify", and the artifacts are owned by the runtime. | PASS |
| PR-011 | Low | `PLATFORM_PASSWORD=platform123`, set explicitly, passed the production guard. | Documented defaults are refused even when set. Warnings for `LX_ALLOW_SIMULATED_PAYMENTS=1` and an unset `LUXORA_PEPPER`. The guard message now matches the behaviour: it checks on every boot. | Test. | PASS |
| PR-012 | High | There was **no backup or restore mechanism**. | `scripts/backup.js` (`VACUUM INTO`, integrity check, sha256 and row-count manifest, optional AES-256-GCM) and `scripts/restore.js` (verifies checksum, decryption, integrity and row counts before moving into place; never overwrites without `--force`). Added `npm run backup` / `restore` and a CI drill. | Live backup during traffic; restore of a 27 MB encrypted backup with full verification in 0.4 s; production boot on the restored database in 4.7 s with the original credentials working. Wrong passphrase, tampering and no-overwrite are each refused, in tests. | PASS (tooling) / BLOCKED (schedule, off-host copy, alerts need the target environment) |
| PR-013 | Medium | CI did not audit runtime dependencies, did not start the server in production mode, and built the image without running it. | Added: `npm audit --omit=dev --audit-level=high`, `/readyz` in the boot smoke, a backup/restore drill, and a container smoke test (refuses seed credentials, boots non-root with secrets, clean stop). The audit and Docker steps run once, on the Node 22 job, by design (`if: matrix.node == 22`); they show as skipped on 22.13 and 24. The matrix also ran with the default `fail-fast: true`: on `32f31c3`, run 39873106955's `test (24)` crashed mid-`test/smoke.js` (`fetch failed … other side closed` on a GET), and the other two jobs were **cancelled** mid-suite, leaving that commit with no result on any runtime. Now `fail-fast: false`, and `test/smoke.js` routes every fetch through the repo's T1 retry rule (retry a read once on a network error; surface writes, never resend them). The crash did not reproduce: the same `smoke.js` on the same head passed 760/0 twice on Node 24.22.1 locally, and a targeted keep-alive reproduction failed 0/72 on Node 22 and 24. **The root cause is unconfirmed**; the retry is a mitigation. | GitHub Actions on draft PR #5 — results in Release evidence. | see Release evidence |
| PR-014 | High | **Asynchronous payment state is not reconciled.** `POST /api/webhooks/inbound/:provider` verifies the HMAC (with a 5-minute window for timestamped schemes, fail-closed without a secret) and records the event, but no handler updates payments or orders. Pending payments stay pending; refunds and chargebacks from the provider are not applied. | None. This is feature work that needs a chosen provider and its sandbox. | Code read; the webhook tests in the suite cover signature handling only. | PARTIAL — capture/failure lifecycle implemented by PR #3 (`apiInboundWebhook` → `applyPaymentStatus`, amount checked, atomic claim; `reconcilePending` sweep every `paymentReconcileMinutes`; tested in `test/integrations.js`); provider refunds/disputes not applied; not live-verified (PR-025) |
| PR-015 | Medium | No on-call rota, escalation contacts or alert routing exist. | OPERATIONS_RUNBOOK.md defines the signals, thresholds and procedures. | — | BLOCKED (owner) |
| PR-016 | **High** | **Money is IEEE-754 floating point end to end.** About 60 money columns are SQLite `REAL`; arithmetic is JS `number`; 122 `toFixed(2)` sites across 21 files round it. Measured with the production helpers (`money2`, `tax.r2`): 1.005 → 1.00, 2.675 → 2.67 and 10.235 → 10.23 (neither half-up nor banker's rounding), and three lines of 0.335 give 1.02 rounded per line but 1.01 rounded once. Payments, refunds, wallet balances, commissions and settlements inherit this. | Not changed. See "Money representation" for the migration strategy. | Reproduced (commands in that section). | **FAIL — open; no owner acceptance** |
| PR-017 | Medium | A full disk fails **every** API call, reads included, because each request writes the session table. `/readyz` cannot usefully gate on this for a single instance. | `diskFreeMb` reported in `/readyz`; alert thresholds in OPERATIONS_RUNBOOK.md. | Measured: 500 `{"error":"internal"}` with no detail leaked; the process stays up; it recovers by itself when space is freed; `integrity_check` ok. | PASS (mitigated) |
| PR-018 | Medium | The password KDF (scrypt N=2^17, r=8) uses about 128 MiB per hash. Eight concurrent sign-ins took the process to **843 MB**. The 1 GB compose limit first proposed was too tight. | Compose `mem_limit: 2g`; sizing documented. | Load test. | PASS (mitigated) |
| PR-019 | Medium | **Single instance only:** one SQLite writer, a per-process checkout lock, per-process rate limits unless `LX_RATELIMIT=redis`. | Documented as the supported topology. | — | ACCEPTED limitation |
| PR-020 | Low | `npm audit`: `source-map-js` high (dev-only, through jsdom); `uuid` moderate through `bull`. | Lockfile bumps `source-map-js` to 1.2.2. The `uuid` advisory affects only v3/v5/v6 with a `buf` argument, and bull calls only `v4()`; the fix would be a breaking downgrade of bull. | `npm audit --omit=dev --audit-level=high` exits 0. | PASS / ACCEPTED (uuid) |
| PR-021 | Low | Inbound webhooks: no event-id de-duplication (only the time window), and unsigned payloads are stored too (bounded by the API rate limit). There is no effect on state today (PR-014). | None. Must be built together with PR-014. | Code read. | MITIGATED — re-delivery has no effect: each transition is claimed atomically (`UPDATE … WHERE status IN awaiting`) |
| PR-022 | Low | `/healthz` is public and returns the store slug and product count. | None (low value to an attacker). | — | ACCEPTED |
| PR-023 | — | The security fixes from PR #1 and PR #2 (in the baseline) are covered by `test/security.js` and the route-audit suites, all passing. | — | `npm test` | PASS |
| PR-024 | High (merge risk) | **Open PR #3 overlaps in 13 files, and a trial merge (`git merge-tree`) conflicts in 8:** `ci.yml`, `Dockerfile`, `lib/api.js`, `package.json` and `server.js`, plus add/add conflicts in `scripts/backup.js`, `scripts/restore.js` and `test/production.js`. PR #3 contains **none** of PR-001 to PR-005, PR-028 or the md5 fix (its versions of those paths are the vulnerable originals). Its `backup.js` copies the keyring *into* the backup, the opposite of this branch's policy. PR #4 conflicts mechanically in `ci.yml`, `package.json` and `.gitignore`; its `context:*` scripts exist only on PR #4, so context checks are N/A here. | None (no authority to change #3/#4). Whichever merges second must re-port these fixes, choose one backup key policy, merge the two `test/production.js` files, and re-run the full suite and the container smoke test. | `git merge-tree` against the PR heads `2e28c3c` (#3) and `28109c4` (#4). | RESOLVED — integrated on `integration/luxora-production-go-2026-10-27` (see "Integrated release candidate"); every PR #5 fix re-verified there, mutation-checked |
| PR-028 | **P0** | **A store showing a currency other than its base currency charged the wrong amount.** Checkout settled and recorded `total` (base currency) labelled with the display currency. Live probe: the shopper was shown **60.47 EUR**, and **65.31 EUR** was recorded and sent to `settlePayment`. With base INR and display USD this is about an 80× overcharge. Reachable once the platform enables `currencyOverridesAllowed` (default off). | Checkout charges and records `money2(m, total)` in `m.currency`, exactly what the order row and receipt say. Downstream fee reporting already converts by each payment's own currency. | Probe before and after the fix. Test in `test/production.js`; mutation reproduces 65.31 vs 60.47. | PASS |
| PR-029 | High | **Refunds are ledger entries only.** `POST /api/admin/payments/:id/refund` sets the payment to `refunded`, claws back offer redemptions and emits `order.refunded`, but calls no provider (`lib/connect.js` has no refund operation). Refund is all-or-nothing, with no partial amount. Disputes (`/api/fin/disputes`) are internal records. | None: whether to block it, relabel it "recorded as refunded at provider" or integrate the provider refund is a product decision. Until then, operators must refund in the provider's dashboard first. | Code read (`lib/api.js` `apiAdminPaymentRefund`). | PARTIAL — PR #3 refunds a live payment through the provider spec's `refund` block (`apiAdminPaymentRefund`); full amount only, no partial refunds; not live-verified |
| PR-025 | P0 for launch | **No external provider is live-verified.** Payment, notification, shipping, tax and AI connectors were exercised only on simulated or offline paths. | — | — | BLOCKED (credentials and sandbox accounts) |
| PR-026 | — | No staging environment. | — | — | BLOCKED |
| PR-027 | — | No deployment target, DNS, TLS certificate, secret manager or log/metrics backend. | — | — | BLOCKED |
| PR-030 | **P0** | **The preserved local working tree could not start the server.** `lib/routes/offer.js` still registered `GET /api/offers/analytics → apiOffersAnalytics` after the handler moved to the Coupon domain; requiring `lib/api.js` threw `apiOffersAnalytics is not defined`. Reproduced on `4ab4800` + the preserved patch, and on the integration. | Dangling route removed; the coupon domain owns the route (`376f45b`). | `require("./lib/api.js")` loads; `test/offer.js` 31/0; full chain (Release evidence). | PASS |
| PR-031 | High | **A priced module installed by the platform was booked as paid with a simulated "captured" payment** (`mod_sim_…`), with no provider and no guard, in production too. | In production the invoice is issued open (collectable) and can only be settled by a real capture through `apiPlatformInvoicePay` → `settlePayment` (`b5e8c88`). | `test/production.js`: invoice open, no payment row, paying without a live gateway 402. Mutation (old behaviour) fails both checks. | PASS |
| PR-032 | High | **Base-currency amounts were labelled with the display currency** in offers evaluation and redemption (wallet credits), line terms and the new-order notification; and PR-028 was untested at the gateway boundary (the test read the payment row, written separately from the request). | Base amounts carry the base currency; the notification states the charge (`b5e8c88`). New gateway-boundary check with a display currency ≠ base (`7e2981f`). | `test/integrations.js` 78/0. Mutation (settle `total` in the display currency) sends 4244 "eur" for an order shown as 39.30 EUR and fails. | PASS |
| PR-033 | Medium | **The PR-001 guard compared the literal state name `"captured"`.** A platform that renames its payment states (they are data) would silently lose the guard. | The guard tests the state's meaning (tagged `settled`) and answers with the machine's failure state (`b5e8c88`). | Mutation (a literal that no longer matches) fails three `test/production.js` checks. | PASS |
| PR-034 | Medium | **The Offers split left duplicate owners and literals**: the `promotions`/`goip` screens in `admin/groupbuy.js`, one route in two files, three hard-coded fallbacks, four undocumented domains, and a kernel coverage report that ignored domain-registered offer math. | Screens back in `admin/offer.js`, registry/state lookups for the literals, authored docs for coupon/giftcard/groupbuy/voucher, coverage asks `offers.handlerFor` (`376f45b` and later). No gate or ratchet loosened. | `test/domain-map.js` 35/0, `test/audit-gate.js` 3/0, `test/goip-audit.js` 197/0, registry gate 40/40. | PASS |
| PR-035 | High (operational) | **The original workspace lives on the iCloud-synced Desktop.** Git objects (an 87 MB pack), most of `node_modules` and the context worktree's files were evicted to placeholders; a zero-byte `.git/index.lock` from 2026-10-21 remains; iCloud conflict copies (`index 2`, `canonical 2.json`) sit inside `.git` and `_registry`. | None in the repository. Integration ran in a fresh clone outside iCloud (`/Users/bipin/Workspaces/LUXORA-production-integration-2026-10-27`). | `find -flags +dataless`, `ls -lO` (2026-10-27). | BLOCKED (owner: move the repository out of iCloud or keep it downloaded; remove the stale lock) |
| PR-036 | Medium | **Container and compose re-verified on the candidate** (`d632ecf`, Docker 27.5.1). Observation: the image copies file modes from the build context, so a checkout made under a strict umask (directories `0700`) builds an image whose code the unprivileged user cannot read; it then fails at boot with `Cannot find module './lib/db.js'`. A normal checkout (CI) is unaffected. | None in code; build from a checkout with world-readable directories (`umask 022`), or add `chmod -R a+rX` before `USER node` if builds can come from stricter environments. | CI's smoke script verbatim: seed credentials refused (`REFUSING TO START`); ready in ~40 s; uid 1000; writing `server.js` denied; encrypted backup inside the container verified (298 tables, 122,729 rows); `docker stop` exit 0. `docker compose config`: Redis publishes no port, app bound to 127.0.0.1. | PASS |
| PR-037 | Medium | **Approving a peer listing failed with a 500** (pre-existing on PR #3 `4ab4800`; its CI never reached `test/platform-types.js`). `lib/listings.js` read `sellerRoles` through `parity-registries.js`, but it is a platform-master registry; the list was always empty and the seller was inserted with no role. | Roles read from the master; with none declared the approval is refused with a reason (`b162c4e`). | `test/platform-types.js` 96/2 → 144/0. | PASS |
| PR-038 | Medium | **Six suites failed on the integrated tree** — composition skipped for a demo store (aurum lost its B2B surface), benefit coverage ignoring domain-registered math, a storefront atom lighting a console leaf, a literal funder, option kinds without a capability crashing every options call (latent in PR #3), and tests that assumed one wallet and the pre-split screens. | Fixed at their causes (`532c195`). | smoke 768/0, parity 255/0, navfit 134/0, goip-audit 197/0, defaults 9/0. | PASS |

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
| Refunds, payment reconciliation, chargebacks | captured/failed reconciled from webhooks and lookups; refunds through the provider (full amount); provider-initiated refunds and disputes **not applied**; nothing live-verified (PR-014, PR-029, PR-025) |
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

## Money representation (PR-016) — findings and migration strategy

**Where money lives today.** Prices (`products.p`, `skus.price`), order lines, `orders.sub/ship_fee/tax/gift_used/total`, `payments.amount/fee`, invoices, wallet and offer-credit balances, affiliate commissions, seller settlements and the fintech ledgers are SQLite `REAL` (about 60 columns), computed as JS numbers. Rounding happens at 122 `toFixed(2)` sites in 21 files (most in `lib/fintech.js` 28, `lib/api.js` 14, `lib/mobility.js` 10). Currency conversion is `money2(cm, n) = +(n * fx).toFixed(decimals)` (`lib/api.js:251`). Tax is `tax.r2 = +n.toFixed(2)`, applied once to the order or summed per line (`lib/tax.js:105`).

**What already exists to build on.** Every currency in the registry carries `decimals` (`lib/api.js` `commerceOf`, `lib/goip.js` economic units), so the minor-unit exponent per currency is already data. No integer-minor-unit, decimal or rational type exists anywhere in `lib/`. Since PR #3, the Universal Wallet (`lib/wallet.js`) already keeps exact minor units (`BigInt`, per-unit decimals, journals that sum to zero) — the natural basis for step 4's money module; the rest of the platform is still `REAL`.

**Reproduced discrepancies** (production helpers, Node 22.22):

| Input | Result | Expected (half-up) |
|---|---|---|
| `money2({fx:1,decimals:2}, 1.005)` | 1.00 | 1.01 |
| `money2(…, 2.675)` / `money2(…, 10.235)` | 2.67 / 10.23 | 2.68 / 10.24 |
| three lines of 0.335, rounded per line vs once | 1.02 vs 1.01 | one documented rule |
| ten lines of 0.10 summed | 0.9999999999999999 (rounds to 1.00) | 1.00 exactly |

The errors are a cent per operation. They matter because payments, refunds, settlements and tax filings must reconcile exactly with the provider and the tax authority, and because nothing records which rounding rule produced a stored amount.

**Migration strategy** (not started; needs an owner and review):
1. **Policy first.** Write down, per currency: the minor-unit exponent (from the registry's `decimals`); the rounding mode (half-up or half-even) for prices, tax (per line or per invoice, by jurisdiction) and FX; and where rounding happens (only at line and document boundaries, never in between).
2. **Additive schema.** Add `*_minor INTEGER` columns beside each money `REAL` column, plus an explicit `currency` where it is implied today. Old columns stay; nothing is rewritten in place.
3. **Backfill with an audit trail.** Compute `round(value × 10^decimals)` under the written rule. Record per row whether the backfilled value disagrees with the displayed two-decimal value, and report every disagreement for review before cut-over. Existing records are preserved as they are.
4. **One money module.** Integer minor units, explicit rounding and FX at a stated precision. Checkout, tax, offers, wallet, payments, refunds, settlements and invoices all go through it. Property tests: sums of rounded lines equal the document total under the policy; refunds never exceed the captured amount; currency conversion round-trips within one minor unit.
5. **Dual-write, then switch reads** behind a flag; reconcile daily totals between the old and new columns until they agree; then retire the `REAL` columns.
6. **Provider amounts** are always sent in minor units with the currency code, so they never come from a float.

Until this is done or a business owner accepts the risk under an independently reviewed policy, the release stays **NO-GO**. Recording the risk here does not accept it.

## Release evidence

| Item | Value |
|---|---|
| **Integrated candidate `cf655752cd341548bc25d773248f4689cda407ed`** — full `npm test` chain (local) | **168/168 steps pass, 0 failing**, 59 min, Node 22.21.1, fresh checkout (ignored artifacts removed). Run step by step so no failure can hide behind an earlier one; about 5,760 passing assertions summed from each suite's summary line; no ✗ in any step log. |
| Candidate — earlier full runs | `3f83262` (PR #5 + PR #4): `npm test` exit 0, 32 min 48 s. `7e2981f`: 162/168 — the six failures are PR-038 and PR-037, fixed in `532c195`/`b162c4e` |
| Candidate — mutation checks | PR-001 guard (literal state name), PR-031 module billing, PR-028 at the gateway boundary, PR-002 card fingerprint: each reverted alone, each makes its test fail |
| Candidate — Postgres (local) | `npm run check:postgres` on `5ed4a76` against PostgreSQL 16.13, SCRAM-SHA-256: pass (PR-007) |
| Candidate — gates | `npm run registry` 40/40, seal verified, no drift; `npm run context:verify` 0 errors; `test/audit-gate.js`, `test/domain-map.js`, `test/white-label.js` pass |
| Candidate — browser and container | `npm run check:browser` (SQLite): 381 page loads clean, UI suites 31/0, 21/0, 51/0. Docker build + CI production smoke on `d632ecf`: pass (PR-036) |
| Candidate — CI | **none**: the branch is not pushed (needs owner authorization) |
| Draft PR | [echelonxventures-Projects/universal-product#5](https://github.com/echelonxventures-Projects/universal-product/pull/5), `claude/exciting-hamilton-kqmbhr` → `master` (`441d772d661abc6626d4497391c6f6261b086a0a`) |
| CI, first head `2a9089655bdad93991d1620e035cbc2b525dffd9` | [run 39869509372](https://github.com/echelonxventures-Projects/universal-product/actions/runs/39869509372): **success** on all three jobs, `test (22.13)`, `test (22)` and `test (24)`. Every step succeeded, including the full suite on each runtime (`test/security.js` 158/0, `test/production.js` 23/0 in the log), boot smoke with `/readyz`, and the backup/restore drill (245 tables, integrity ok). On `test (22)`, the audit, the Docker build (pinned digest resolved) and the Docker production smoke (seed credentials refused; `/readyz` ready; non-root; clean stop) also ran. The audit and Docker steps were skipped on 22.13 and 24 by `if: matrix.node == 22`. |
| CI, final head | recorded on PR #5: a file cannot carry the CI result of the commit that adds it |
| `npm test`, final tree (local) | exit 0 — **1,800 passing, 0 failing**, 26 min 38 s, Node 22.22.0 (includes the currency and TLS-shutdown tests) |
| `npm test`, `2a90896` (local) | exit 0 — 1,796 passing, 0 failing, 25 min 7 s, Node 22.22.0 |
| `npm test`, baseline `441d772` (local) | exit 0 — 1,773 passing, 0 failing, 27 min 3 s |
| `npm run registry` | exit 0 — 15 gate checks green, seal verified, no drift |
| Container (local) | built from `2a90896`; the sandbox build differs only by a proxy CA bind-mount on `npm ci`. The CI container smoke script was run verbatim: refuses seed credentials; ready; uid 1000; backup and verify inside the container; `docker stop` exit 0. No `data/` or compiled registry in the image. |
| Compose (local) | Redis not published (`6379/tcp` internal only); worker RUNNING; app survives a Redis stop and recovers |
| Postgres probe | PostgreSQL 16.15, isolated, local — PR-007 |
| Restore drill (local) | 27 MB / 245 tables / 102,933 rows, encrypted: verify and restore 0.4 s; production boot on the restored database 4.7 s; sign-in ok |
| Deployment | **not performed** — not authorized, and no target |

Performance figures (Load and resilience) come from one 4-vCPU sandbox with the load generator on the same host, phases of 15–20 s. They were not re-measured in this pass. They indicate relative behaviour and the single-process ceiling. They are **not** evidence of production capacity.

## Release gates

Owner "—" means not named in the repository; the business owner must assign one.

| # | Gate | Evidence | Status | Risk if unresolved | Remediation / evidence to close | Owner |
|---|---|---|---|---|---|---|
| 1 | CI passes on the final PR SHA | PR #5 `2a90896`: run 39869509372 success. Integrated candidate: **not pushed**, so no CI run exists for it; local full chain in Release evidence. | NOT VERIFIED (candidate) | unverified code reaches master | push the candidate (owner authorization) and get every job green, including `browser` and `postgres` | PR author |
| 2 | Payment provider provisioned and tested in its test environment | none; card checkout is declined in production (PR-001) | BLOCKED | cannot take card payments | sandbox credentials; capture, decline, 3DS, refund runs recorded | — |
| 3 | Webhook lifecycle: success, failure, refunds, disputes, chargebacks | since PR #3: signed webhooks and a lookup sweep apply captured/failed with an amount check (`test/integrations.js` 78/0, stand-in gateway); provider refunds of a live payment go through the provider (full amount); provider-initiated refunds and disputes are not applied | PARTIAL | refunds/chargebacks made at the provider are not reflected | apply refund and dispute events; partial refunds; run the lifecycle against the chosen provider's sandbox | — |
| 4 | Financial arithmetic and rounding policy | PR-016 reproductions above | FAIL | cent-level mismatches against provider and tax records | written policy plus minor-unit migration, or a reviewed owner acceptance | — |
| 5 | Explicitly supported database configuration | SQLite, single instance, documented; Postgres PARTIAL (PR-007): `check:postgres` passes locally on PG 16 + SCRAM, pooling and scale unmeasured | PASS (SQLite) | — | measure the Postgres request path (connections, latency) and a production-size migration before supporting it | — |
| 6 | Migrations and rollback/recovery | additive boot-time DDL (48 `ADD COLUMN`, no destructive DDL); backup before upgrade; restore verified | PASS (procedure) / NOT VERIFIED (staging upgrade) | a failed upgrade without a backup | rehearse upgrade and rollback in staging | — |
| 7 | Staging with production-equivalent configuration | none | BLOCKED | first real deploy is the rehearsal | provision staging and run DEPLOYMENT_RUNBOOK.md end to end | — |
| 8 | Deployment target and documented rollback | rollback documented; no target | BLOCKED | — | name the target; rehearse rollback | — |
| 9 | TLS, domain, secrets management, security headers | headers verified by probe; HSTS only under in-process TLS; no domain, certificate or secret manager | BLOCKED (headers PASS) | credential exposure, MITM | proxy TLS config, HSTS at the proxy, secret-manager injection | — |
| 10 | Authorization, sessions, CSRF, input validation, rate limits | `test/security.js`, `authz`, `tenancy`, `roles` and others all pass; per-IP and auth limits verified under load | PASS (test evidence; no external pentest) | — | independent penetration test before launch is recommended | — |
| 11 | Dependency and container vulnerability assessment | `npm audit --omit=dev` clean at high; one moderate `uuid` advisory, not applicable; non-root, pinned base. **No image CVE scanner was run** (none available). | NOT VERIFIED (image CVEs) | unpatched OS packages in the base | run an image scanner on the CI-built image; schedule base-digest bumps | — |
| 12 | Database encryption and backup-key recovery | gateway secrets sealed with AES-256-GCM; the database file itself is not encrypted at rest; backups encrypted with a passphrase; keys kept out of backups by design | NOT VERIFIED (volume encryption, key escrow) | data readable from a stolen disk; lost keys make credentials unrecoverable | encrypted volume; secret-store escrow for the master key, pepper and backup passphrase; key-loss drill | — |
| 13 | Automated backups and independent off-site copies | tooling verified; retention (`--keep`) and encrypted-only S3 upload added in the integration (`test/backup.js` 18/0); systemd unit reads its secrets from `/etc/luxora/backup.env`; no schedule or destination chosen | BLOCKED | data loss beyond RPO | enable the timer or cron with a passphrase and an off-account bucket; alert on failure | — |
| 14 | Rehearsed disaster recovery | local restore drill verified; not from an off-site copy, not in staging | NOT VERIFIED | untested recovery | restore drill from the off-site copy into staging, timed and recorded | — |
| 15 | Observability: logs, metrics, health, readiness | JSON logs with trace IDs, `/metrics` with a token, `/healthz`, `/readyz` (verified); no tracing backend | PASS (application side) | — | connect a log and metrics backend | — |
| 16 | Actionable alerts with verified delivery | thresholds documented in OPERATIONS_RUNBOOK.md; nothing wired | BLOCKED | outages go unnoticed | wire the alerts; fire a test alert end to end | — |
| 17 | On-call ownership and incident runbooks | runbooks written; no rota | BLOCKED | — | name primary and secondary on-call and the escalation chain | — |
| 18 | Performance objectives and capacity headroom | sandbox measurements only; no SLOs, no expected-traffic figures | NOT VERIFIED | saturation at peak (one process, about 210 req/s browse) | define SLOs and expected load; load test in staging | — |
| 19 | Data retention, privacy, regulatory obligations | consent, data-subject request, erasure and retention endpoints exist and are exercised by `test/security.js` / `test/smoke.js`; jurisdiction, DPA, retention periods and PCI scope not assessed | NOT VERIFIED | regulatory exposure | legal and compliance review; PCI SAQ once a card provider is chosen | — |
| 20 | Deployment approval and rollback authorization | none | BLOCKED | — | named approver signs off after gates 1–19 | — |

Missing information needed from the owner: hosting target and region; secret-store mechanism;
domain and certificate source; payment provider and sandbox credentials; notification provider;
expected traffic (orders/day, peak concurrency, catalogue size); backup destination and retention;
on-call contacts; rounding policy per currency and jurisdiction; refund handling decision (PR-029).
