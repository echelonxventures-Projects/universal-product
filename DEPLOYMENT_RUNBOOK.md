# Deployment Runbook

How to deploy, verify and roll back LUXORA. Companion documents:
[DATABASE_RECOVERY_RUNBOOK.md](DATABASE_RECOVERY_RUNBOOK.md) (backups, restore, RPO/RTO),
[OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md) (monitoring, alerts, incidents),
[PRODUCTION_READINESS.md](PRODUCTION_READINESS.md) (current status, gaps, go/no-go).

## Supported topology

The release is validated for **one application instance on one host**, with SQLite on a
persistent volume:

```
client ──TLS──▶ reverse proxy (nginx / LB, terminates TLS) ──HTTP──▶ luxora :3000 ──▶ /app/data (volume)
                                                                         └──▶ redis (optional, internal only)
```

Do not run two application instances against one database. SQLite has one writer, the checkout
lock (`CHECKOUT_LOCKS`) is per process, and rate-limit buckets are per process unless
`LX_RATELIMIT=redis`. PostgreSQL is **not** a supported production target in this release
(see PRODUCTION_READINESS.md, PR-007).

Sizing measured on 4 vCPU (PRODUCTION_READINESS.md, Load): about 210 catalogue requests/s and
about 60 completed orders/s from one process. Memory: about 200–330 MB in steady state, **up to about
850 MB** during concurrent sign-ins (the password KDF uses about 128 MiB per hash, four at a
time). Give the container at least 1.5 GB; the compose file sets 2 GB.

## Operator configuration

Values are never written in this document or committed. Store them in the deployment
platform's secret store and inject them as environment variables.

### Required

| Variable | What | How to produce it |
|---|---|---|
| `NODE_ENV` | `production` — turns on every production guard | literal |
| `PLATFORM_PASSWORD` | platform admin (`platform@luxora.shop`) password, used only on the first boot | password manager; a documented default is refused |
| `ADMIN_PASSWORD` | flagship store admin (`admin@luxora.shop`) password, first boot only | as above |
| `LUXORA_MASTER_KEY` | 32-byte key that seals gateway credentials, **64 hex chars** | `openssl rand -hex 32`; anything else refuses to boot |
| `LUXORA_PEPPER` | server-side password pepper | `openssl rand -hex 32` — set **before the first boot**; changing it later invalidates every password |

`LUXORA_MASTER_KEY` may be left unset, in which case a key is generated into
`/app/data/master.json`. That works, but the key then lives next to the data it protects, and
losing the volume loses the key. Prefer the secret store.

### Required behind a reverse proxy

| Variable | What |
|---|---|
| `LX_TRUST_PROXY=1` | take the client IP from `X-Forwarded-For`. Without it every request appears to come from the proxy and the per-IP rate limit throttles all customers as one. Only set it when a proxy you control is the sole way in. |

### Optional

| Variable | Default | What |
|---|---|---|
| `PORT` | 8787 (3000 in the image) | listen port |
| `LX_DB` | `data/luxora.db` | SQLite path — must be on the persistent volume |
| `LX_METRICS_TOKEN` | — | bearer token for `/metrics`, ≥ 16 chars (`openssl rand -hex 24`) |
| `LX_LOG=json` | text | one JSON line per request with `trace`, `tenant`, `status`, `ms` |
| `LX_QUEUE=redis` + `LX_REDIS_URL` | inline | background jobs in Redis (scheduled reports, webhook delivery) |
| `LX_RATELIMIT=redis` | memory | shared rate-limit buckets |
| `LX_SHUTDOWN_MS` | 8000 | maximum drain time on SIGTERM; keep below the orchestrator's stop grace |
| `LUX_TLS=1` + `LUX_TLS_KEY` / `LUX_TLS_CERT` | off | terminate TLS in the process instead of a proxy (HSTS is sent only then) |
| `LX_REGISTRY_KEY`, `LX_REGISTRY_STRICT=1` | generated / off | registry seal key; strict mode refuses to boot on a seal that does not verify |
| `LX_BACKUP_PASSPHRASE`, `LX_BACKUP_DIR` | — | backup encryption and destination (DATABASE_RECOVERY_RUNBOOK.md) |

### Must NOT be set in production

| Variable | Why |
|---|---|
| `LX_ALLOW_SIMULATED_PAYMENTS=1` | lets orders and invoices be marked paid with no money taken. Staging rehearsal only; the server prints a warning at boot when it is set. |
| `LX_OFFLINE=1` | forces every payment, notification and AI call to the simulated path |
| `LUXORA_DEMO_BRANDS=1` | installs demo fixture stores |

### In the consoles, after the first boot

1. **Payment gateway** — Store admin → Payments: connect a provider in `live` mode with real
   credentials. Until then card checkout is **declined** in production (the simulated capture is
   refused); cash on delivery and bank transfer still work as `pending`.
2. **Inbound webhook secret** — Platform → Enterprise → inbound webhooks. Without it every inbound
   webhook is refused with 401 (fail-closed).
3. **Notifications** — Store admin → Notifications: connect a live channel, or order mail is only
   logged.
4. **Plan** — the flagship store starts on *Growth* (2,000 orders/month; checkout returns 402 past
   it). Assign the plan that matches expected volume.
5. **Rotate** the two first-boot admin passwords in the console. Keep `PLATFORM_PASSWORD` /
   `ADMIN_PASSWORD` set: they only create accounts that do not exist yet (rotating in the console
   is not undone by a restart), but the production guard checks that they are set, and not a
   documented default, on every boot.

## Build

```bash
git checkout <release commit>          # the exact SHA recorded in PRODUCTION_READINESS.md
docker build -t luxora:<sha> .
docker image inspect luxora:<sha> --format '{{.Id}}'   # record the image digest
```

The base image is pinned by digest. The image runs as the unprivileged `node` user; only
`/app/data` (volume) and `/app/_registry` (compiled registry, sticky) are writable.

## First deployment

1. Provision the host, a persistent volume for `/app/data`, the reverse proxy with a valid
   certificate, and the secret values above.
2. Start Redis if used — on an internal network only, never published.
3. Start the container with the volume and the environment:
   ```bash
   docker compose up -d        # or the equivalent in your orchestrator
   ```
   The first boot seeds the catalogue and takes about 30 s; the health check allows 90 s.
4. Verify:
   ```bash
   curl -fsS https://<host>/healthz         # liveness
   curl -fsS https://<host>/readyz          # {"ready":true,"db":true,"draining":false,"diskFreeMb":…}
   ```
5. Smoke test (no real money): sign in to `/console.html` with the platform and store
   credentials; place a **cash-on-delivery** order on the storefront and see it in Store admin →
   Orders; confirm a card checkout without a live gateway is declined with
   "simulated capture is disabled in production". With a live gateway in its provider's test mode
   (if it has one), place one test-card order and refund it.
6. Take the first backup and run the restore drill (DATABASE_RECOVERY_RUNBOOK.md) before
   accepting real orders.

## Upgrades

1. Read the release notes for schema changes. Schema is created and evolved at boot by
   `lib/db.js` (`CREATE TABLE IF NOT EXISTS` and additive column checks); there is no separate
   migration step and no down-migration.
2. **Back up** (`npm run backup` in the container or from the host against the volume) and verify
   it (`scripts/restore.js <dir> --verify-only`).
3. Build and tag the new image; deploy it with the same volume and environment.
4. `docker stop` sends SIGTERM: `/readyz` turns 503, the listener closes, in-flight requests
   finish (bounded by `LX_SHUTDOWN_MS`), the process exits 0.
5. Verify `/readyz` and repeat the smoke test.

## Rollback

Schema changes are additive, so the previous image normally runs against the newer database.

1. Redeploy the previous image tag with the same volume.
2. If the previous image fails against the database, stop it and restore the backup taken in
   upgrade step 2 (DATABASE_RECOVERY_RUNBOOK.md → Restore). Orders placed since that backup are
   lost from the database: export them first from Store admin → Orders, or from the
   newer database with the backup tool, and reconcile against the payment provider's records.

Roll back when, within the observation window: `/readyz` is not 200 for 2 minutes, the 5xx rate
is above 1 % for 5 minutes, or checkouts fail that succeeded before the deploy.

## Things this runbook does not cover (not available in this repository)

DNS, certificates, the hosting provider, secret-manager integration, log shipping and alert
routing are environment-specific and must be supplied by the operator (PRODUCTION_READINESS.md,
"Blocked").
