# LUXORA Platform

**Universal, white-label, multi-store commerce platform.** Zero runtime dependencies: Node.js ≥ 22.5 (`node:http`, `node:sqlite`, `node:crypto` only) + vanilla JS frontends. Everything—taxonomy, industries, product types, verticals, contexts, providers, countries, currencies, security policy—is *entity data*, never code.

## Documentation

End‑to‑end guides for every role — **Customers, Store Admins, Support, Marketplace Sellers, and Platform (Super) Admins** — live in **[USER_MANUAL.md](USER_MANUAL.md)** (roles & capability matrix, per‑surface walkthroughs, security, glossary, troubleshooting).

The complete **pictorial flow** of the whole platform — three planes, the 10‑layer request pipeline, multi‑tenant resolution, meta hierarchy, pricing/checkout, B2B (RFQ·Tender·Contract), supply (sellers vs suppliers), serialization, lifecycles, modules, data model and role matrix — is in **[FLOWS.md](FLOWS.md)**.

## Run

```bash
npm start                    # http://localhost:3000
PORT=8787 ./serve.sh         # supervised (auto-restart), writes .luxora.pid
./stop.sh                    # clean stop
npm test                     # syntax + 191-assertion jsdom E2E suite (own DB/port)
```

Env: `PORT`, `LX_DB` (db path), `LUX_TLS=1` (HTTPS; self-signed generated via openssl, or supply `LUX_TLS_KEY`/`LUX_TLS_CERT`), `LUXORA_MASTER_KEY`, `LUXORA_PEPPER`, `LUXORA_DEMO_HINT=0`, `LX_OFFLINE=1` (force all outbound payments/notifications/AI to the offline-simulated path — CI/no-secrets), seed overrides `PLATFORM_EMAIL/PLATFORM_PASSWORD/ADMIN_EMAIL/ADMIN_PASSWORD/DEMO_PASSWORD`.

Runtime backends are **config**, not code — default to in-process (SQLite + memory + inline queue + local disk); switch any of them via `Platform → Runtime` (or `platform_settings.runtime`) / env: `LX_CACHE`, `LX_QUEUE`, `LX_STORAGE`, `LX_RATELIMIT`, `LX_SESSION`, `LX_OUTBOUND`, `LX_DB_DRIVER` (`memory|redis`, `inline|redis|webhook`, `local|s3|webhook`, `sqlite|postgres`, `auto|offline|live`) with connection params `LX_REDIS_URL`, `LX_S3_BUCKET/REGION/ACCESS/SECRET/ENDPOINT`, `LX_PG_URL`, `LX_WEBHOOK_URL/SECRET`, `LX_WORKER=1` (run a Redis queue consumer on this node), `LX_IDEMPOTENCY=0` (disable idempotency); every response carries an `X-Request-Id`/`X-Trace-Id` and mutations accept an `Idempotency-Key` for safe retries. All dependency-free (raw RESP / SigV4 / PG wire over `net`+`fetch`); unconfigured drivers fall back safely. *Note (B):* the async dual-engine + SQLite→Postgres **dialect translator, wire client (`lib/pg.js` extended protocol), and migration planner (`lib/migrate.js`)** are built and tested (`GET /api/platform/db` reports driver/health/plan). The final request-path sync→async cutover needs a live Postgres and is a runbook step (FLOWS §25) — the machinery to make it mechanical is in place.

## Surfaces

| URL | What |
|---|---|
| `/` | Storefront (per tenant). `?store=<slug>` or subdomain `<slug>.localhost` switches |
| `/admin.html` | **Store console**: dashboard, catalog+full product editor, SKUs/inventory, orders, returns, RFQs, sellers, settlements, **contracts & tenders (B2B)**, suppliers & **serialized items**, **compliance & certs**, **localizations (i18n)**, **AI Studio**, promotions, content, taxonomy, attributes, payments, settings, analytics, audit, monitor, Data Studio, **Team & Roles (RBAC staff roles)** |
| `/platform.html` | **Platform console**: provisioning policy, stores (launch wizard: owner, jurisdiction, taxation, categories, gateways, plan), Geo (countries/currencies/tax modes/providers+availability), plans, subscriptions, invoices, provider registry, **AI providers & plans (product + billing)**, monitoring, global audit |

Seed accounts (env-overridable; hints auto-hide when passwords change): platform `platform@luxora.shop/platform123` · store admins `admin@luxora.shop/admin123`, `admin@aurum.shop/aurum123` (INR/GST/Razorpay/UPI/Delhivery), `admin@velora.shop/velora123` (AED/VAT/Tabby, brand mode) · customer `demo@luxora.shop/demo123`.

## The product model

**Meta hierarchy**: domain → industry → category → subcategory → family → model → product → variant/SKU → inventory → serialized items. **33 industries, 23 product types, 16 vertical profiles** (grocery, jewellery, chemical, vehicle, service, rental… — each an editable field schema), EAV attribute engine, **RBAC staff roles + per-section permissions**, **universal identity layer** (GTIN/UPC/EAN/ISBN/MPN/OEM/VIN/IMEI/HSN/UNSPSC/GS1‑GPC/eCl@ss/ETIM — 20 codes), **variant groups** (SKU‑authoritative pricing), **structured compliance & certification records** (issuer/jurisdiction/validity), **per‑object i18n localizations**, **supplier & procurement model** (suppliers, price lists, product‑supplier links, lead time, MOQ, payment terms), **B2B contracts** (fixed/tiered contract pricing applied at cart + checkout) and **tenders** (award → auto‑contract), universal relationships (product relations + `links` graph), media/packaging/UOM/lifecycle engines, **contexts** (`tax / invoice / payment` per industry, validated at checkout, server auto-derived), pluggable providers driven by **declarative request specs** (fill-in-the-blanks JSON in `provider_defs.spec`, no per-provider code — Meta/Google Ads/GA4/TikTok + custom providers are data) including **16 payment incl. country rails: Stripe, Razorpay, UPI, PIX, iDEAL, M-Pesa, Tabby…**, shipping, notifications, tax) with per-country availability as a relation table, **currencies + FX** (entities, rates, history, optional JSON feed sync), tiered/B2B pricing, promotions/coupons with wallet rewards + refund clawback + per-owner/usage limits + funder (bank/brand) split, settlements, RFQs · **first-class Tax engine** (jurisdiction rates, classes, VAT/GST validation, reverse-charge, inclusive/exclusive) and **Billing engine** (line-item + usage-metered invoices, proration, credit notes, refunds-to-wallet, dunning, aging) — all configuration-driven.

**Deployment modes per tenant** (marketplace / industry / brand) — same backend, different configuration. Three stores ship seeded to demonstrate all three.

**Entity engine**: every table is a declared entity (fields, types, validation, permissions, composite keys, universal UUIDs via SQLite triggers). Define *new entities* in Data Studio or via `POST /api/meta/entity-def` — CRUD, validation, audit, and forms appear automatically. Custom providers register as JSON manifests, no code.

## The 10-layer security stack (`GET /api/platform/security` for the live scorecard)

1. **Transport** — per-request CSP (inline-style allowance is itself a policy flag), frame-ancestors none, nosniff, optional TLS/HSTS, hardened cookies
2. **Session** — CSRF double-submit (timing-safe), origin-pinned mutations, tenant-pinned state
3. **Credentials** — scrypt v2 (policy-tunable N/r/p) + pepper, transparent v1→v2 upgrade on login
4. **Password policy** — platform-configured length/classes/blocklist + history reuse guard
5. **At rest** — AES-256-GCM envelope seals on gateway secrets, AAD-bound to tenant|provider|field
6. **Keys** — versioned keyring (`data/master.json`, 0600), rotation API auto-rewraps all seals
7. **Audit** — SHA-256 hash-chained log with verification endpoints (tamper detection)
8. **Abuse** — durable token-bucket rate limits + per-account lockout with exponential backoff
9. **Supply chain** — sha384 SRI injected into every served JS/CSS tag; parameterized SQL; strict schema validation
10. **Isolation** — tenant-scoped data, platformOnly entity guards, role gates, suspended-store blocks, platform-policy gates over store features (coupons, currency overrides, fiscal pickers)

## Enterprise ops (all OFF-by-default, fill-in-the-blank config)

DB→Postgres cutover control plane (status/ping/dry-run/apply/switch), PSP gateway **preview** + verified **inbound webhooks** (HMAC), **SAML/OIDC SSO** + **SCIM 2.0** staff sync (bearer tokens), **regions + CDN/edge**, **Prometheus `/metrics`** + JSON logs + trace ids, **product feeds** (`/api/feeds/<slug>.xml|.csv`), **warehouse stock transfers**, **tax remittance** report, and **RBAC** staff roles + Team/SSO/Trash/Webhooks/AI consoles. Each is enabled only by writing its config; nothing activates silently.

## Architecture

```
server.js            multi-tenant routing, security middleware, SRI, static
lib/db.js            SQLite schema + migrations + universal-UUID triggers + seed
lib/security.js      L1-L10 primitives (AES-GCM, scrypt, chains, limiters, policy)
lib/entity.js        entity engine (23 entities incl. country, currency, provider, link, context_type)
lib/registry.js      live registries (geo, currencies+FX, tax modes, providers, availability, meta lists)
lib/meta.js          seed definitions (industries, types, verticals, contexts, lifecycle)
lib/providers.js     seed definitions (countries, providers, currencies) — data, editable post-seed
lib/api.js           ~110 REST routes; lib/uid.js UUID triggers; lib/metrics.js live traffic
public/              storefront + store console + platform console (no frameworks, no CDN)
data/                luxora.db + master.json (created at first boot)
```

*This is an educational demo project; it is not affiliated with any retailer.*
