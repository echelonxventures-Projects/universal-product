# Open-ended environments: the plan (LXM-REQ-000238)

**Source:** the owner, 2026-10-31: "Plan like there must be infinite environment option on configuration" (SRC-0029 §0.2).
**Prepared by:** `amazon-44`, 2026-10-31. **Built by:** amazon-62, the sole repository writer, step by step under LXM-REQ-000237.
**Status:** plan. The checks that measure it already run (code adapter: `environment-branch`, `environment-name`).

## 1. Principle

An environment is data, never code. There is no fixed list of environments: development, staging and production are only the first registrations, and any number more (per region, per tenant, per provider sandbox, per experiment, short-lived review environments) is added by registration alone. Code never asks *which* environment it runs in; it reads the **settings** the active environment sets.

## 2. What the candidate already has (39ed4d6)

The registry already exists: `lib/env.js` holds unlimited environments as data (drivers, connection parameters with secrets sealed, feature flags with percentage rollout, tenant routing), activates one, and imports and exports them as JSON. It is stored in `platform_settings`, outside the kernel.

What breaks the principle today: **12 code sites in 8 files** branch on `NODE_ENV === "production"`, and **32 sites in 15 files** write an environment name (mostly `"sandbox"` as a provider mode). The code adapter finds both, and readiness blocks on them.

## 3. The model

| Part | Meaning | Rule |
|---|---|---|
| Identity | Universal ID, a free name, a purpose, an owner | The name is a label; nothing compares it |
| Inheritance | Layered overlays: platform defaults → environment → tenant → market → … | Any depth; the resolution order is itself configuration |
| Settings | Every behaviour that may differ between environments, declared once with a default | Code reads the setting, never the environment |
| Secrets | References to the secret store, never values | Missing secret = the environment fails validation, not at runtime |
| Data isolation | Its own database, storage and queues | Validation refuses an environment that shares another's data unless declared |
| Providers | Per concern, the provider and its *mode* (test, live, …) | A provider mode is a provider setting, not an environment name |
| Gates | Which release gates apply, and their evidence | Readiness is computed per (candidate, environment) |
| Promotion | Edges from one environment to the next, any graph | A promotion is a governed change (approval, rollback) |
| Time | Valid from and to (bitemporal) | Retired environments stay in history |

Selection: the process receives one bootstrap value, the environment's **ID**, and resolves everything else from the registry. That value is the only environment input; code never compares it with a literal.

## 4. The 12 sites as declared settings

| Site | Today | Becomes the setting |
|---|---|---|
| `lib/api.js:360`, `lib/fintech.js:46` (the same body twice) | simulated payments unless production | `payments.simulation_allowed` |
| `lib/api.js:804` | storefront origin rule in production | `storefront.origin_mode` |
| `lib/api.js:2552`, `lib/dashboards.js:310` | demo hints outside production | `experience.demo_hints` |
| `lib/logger.js:4` | log format in production | `observability.log_format` |
| `lib/metrics.js:22` | metrics behaviour in production | `observability.metrics_mode` |
| `lib/mailer.js:125`, `:139` | console echo of messages; delivery-failure reporting | `messaging.echo_to_console`, `messaging.report_failures` |
| `lib/security.js:57` | master-key length enforced in production | `security.require_full_master_key` |
| `server.js:329`, `:356` | startup checks in production | `operations.startup_checks` |

Each setting is declared (so the configuration adapter proves it is read), defaulted to the **safe** value (simulation off, full key required, failures reported), and set per environment.

## 5. Order of work (each step: tests green, `step_commit.py`, clean tree)

1. Declare the settings of §4 with safe defaults; add them to the configuration adapter's declarations.
2. Replace the 12 `NODE_ENV` branches with the settings; remove the duplicate simulation check. Ratchet `environment-branch` to 0.
3. Move provider modes (`"sandbox"`) into provider settings; ratchet `environment-name` to 0.
4. Move the environment registry into the kernel (entity, versions, relationships for inheritance and promotion), per LXM-REQ-000232.
5. Validation on registration: secrets present, data isolated, gates named, promotion edges acyclic where required.
6. Readiness per environment: `readiness.py` takes the target environment; GO is for one candidate in one environment.
7. Test: two environments with arbitrary new names (none of development, staging or production) produce every behaviour from their settings alone.

## 6. Done means

`environment-branch` and `environment-name` are 0; every §4 setting is declared and read at runtime; the test in step 7 passes; adding an environment needs no code change.
