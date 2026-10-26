# Observability and Incident Runbook

What to watch, what to alert on, and what to do when it fires. The alerting system, dashboards
and on-call rota are environment-specific and are **not** in this repository — the signals below
are what the application provides for them.

## Signals the application provides

| Signal | Where | Access |
|---|---|---|
| Liveness | `GET /healthz` → 200 while the process serves | public (no secrets; shows store slug and product count) |
| Readiness | `GET /readyz` → 200 `{ready, db, draining, diskFreeMb}`; 503 while draining or when the database does not answer | public; point the load balancer here |
| Prometheus metrics | `GET /metrics` — `luxora_http_requests_total`, `luxora_http_errors_total`, `luxora_http_duration_ms_avg`, per-endpoint and per-tenant request counters, 24 h orders and revenue | `Authorization: Bearer $LX_METRICS_TOKEN`, or a platform session; keep it off the public internet anyway |
| Request log | stdout, one line per request; `LX_LOG=json` gives `{ts, lvl, trace, tenant, method, path, status, ms}` | container logs |
| Correlation | every response carries `X-Request-Id` / `X-Trace-Id` (a valid incoming `X-Request-Id` is reused); orders keep their `trace_id` | — |
| Live monitor | Platform console → Monitor; Store admin → Monitor (30-minute request series, errors, latency, per endpoint) | signed-in staff |
| Security scorecard | `GET /api/platform/security`, audit hash chain `GET /api/platform/chain/verify` | platform admin |
| Queue | `Queue error (redis … unreachable; Bull retries in the background)` in the log | container logs |

Logs carry method, path, status, timing, tenant and trace — not bodies, cookies or headers.
Unhandled errors log `FATAL` with a stack and answer `500 {"error":"internal"}` with no detail.

## Alerts (recommended thresholds)

| Alert | Condition | Severity |
|---|---|---|
| Down | `/healthz` fails from outside for 2 min | page |
| Not ready | `/readyz` not 200 for 2 min | page |
| Error rate | `rate(luxora_http_errors_total[5m]) / rate(luxora_http_requests_total[5m]) > 0.01` for 5 min | page |
| Latency | `luxora_http_duration_ms_avg > 500` for 10 min (measured p50 at 64 concurrent users ≈ 270 ms) | ticket |
| Disk | `/readyz` `diskFreeMb < 1024`, or host volume > 85 % | page at < 512 MB — a full disk fails every API call |
| Memory | container RSS > 1.6 GB (steady state 200–330 MB, sign-in bursts up to ~850 MB) | ticket |
| Backups | backup job failed, or no new backup for 2 h | page |
| Restore drill | none recorded for 35 days | ticket |
| Certificate | TLS certificate expires in < 14 days (proxy or `LUX_TLS_CERT`) | ticket |
| Queue | `Queue error` lines for > 5 min with `LX_QUEUE=redis` | ticket |
| Payments | zero `order.paid` events for a period that normally has orders, or a spike of `402 Payment was declined` | page |
| Audit chain | `/api/platform/chain/verify` not `ok` | page (possible tampering) |

## Incident procedures

**Process down or restarting.** `docker compose logs --tail 200 luxora`. Common causes:
`REFUSING TO START` (a required variable is missing or a documented default — see
DEPLOYMENT_RUNBOOK.md), `LUXORA_MASTER_KEY must be hex`, `Node … is too old`, or an out-of-memory
kill (`docker inspect … .State.OOMKilled`; raise the memory limit). If the last deploy caused it,
roll back (DEPLOYMENT_RUNBOOK.md → Rollback).

**Every API call returns 500.** Check `/readyz` → `diskFreeMb` and `df -h` on the volume. Free
space (old backups, `data/exports`, logs); the server recovers without a restart. Then run
`PRAGMA integrity_check` via a backup (`scripts/backup.js` checks it).

**Checkouts failing.**
- `402 … simulated capture is disabled in production` — no live gateway is connected for that
  payment method. Connect one (Store admin → Payments) or disable the method. Never "fix" this
  with `LX_ALLOW_SIMULATED_PAYMENTS=1` in production.
- `402 Payment was declined by the gateway: …` — the provider refused; check the provider dashboard.
- `402 Monthly order limit reached` — the store's plan cap; change the plan.
- `403 … blocked by our risk system` — Store admin → Risk review queue; resolve or adjust the
  risk thresholds and blocklists.
- `409 A checkout is already in progress` — a duplicate submit from the same bag; transient.

**Database locked / slow writes.** One writer at a time with a 3 s busy timeout. Look for a long
export or report, and for backup jobs overlapping peak hours (`VACUUM INTO` holds a read
transaction, which does not block writers in WAL mode but does use I/O).

**Redis down.** The application keeps serving; queued work (scheduled reports, webhook
deliveries) waits and Bull retries when Redis returns (measured). Restart Redis; its data is
persistent (`appendonly yes`).

**Suspected credential or key compromise.** Rotate the affected admin passwords in the console;
rotate gateway credentials at the provider and re-enter them; verify the audit chain; preserve
logs. Master key: when it lives in `data/master.json`, rotate it from Platform → Security (every
sealed credential is re-wrapped). When it comes from `LUXORA_MASTER_KEY`, console rotation is
refused (409) — replace the value in the secret store, restart, and re-enter every gateway and
connector credential, since nothing sealed under the old key can be opened with the new one.

**Data loss or corruption.** Stop the application and follow DATABASE_RECOVERY_RUNBOOK.md →
Restore.

## Escalation

The repository does not name an on-call rota or escalation contacts. Before go-live the owner
must record: primary and secondary on-call, the payment provider's support channel, the hosting
provider's support channel, and who may authorize a restore that loses data (PRODUCTION_READINESS.md,
PR-015).

## Kill switches

| Need | Switch |
|---|---|
| Stop all outbound payments, notifications and AI calls | `LX_OFFLINE=1` + restart (card checkout is then declined in production) |
| Stop a single integration | disable it in the consoles (gateways, notifiers, webhooks) |
| Stop selling on a store | Platform console → suspend the store (API answers 403 for non-platform callers) |
| Stop background jobs on a node | `LX_WORKER=0` + restart |
