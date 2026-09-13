# LUXORA Platform

**Universal, white-label, multi-store commerce platform.** Zero runtime dependencies: Node.js ≥ 22.5 (`node:http`, `node:sqlite`, `node:crypto` only) + vanilla JS frontends. Everything—taxonomy, industries, product types, verticals, contexts, providers, countries, currencies, security policy—is *entity data*, never code.

## Run

```bash
npm start                    # http://localhost:3000
PORT=8787 ./serve.sh         # supervised (auto-restart), writes .luxora.pid
./stop.sh                    # clean stop
npm test                     # syntax + 135-assertion jsdom E2E suite (own DB/port)
```

Env: `PORT`, `LX_DB` (db path), `LUX_TLS=1` (HTTPS; self-signed generated via openssl, or supply `LUX_TLS_KEY`/`LUX_TLS_CERT`), `LUXORA_MASTER_KEY`, `LUXORA_PEPPER`, `LUXORA_DEMO_HINT=0`, seed overrides `PLATFORM_EMAIL/PLATFORM_PASSWORD/ADMIN_EMAIL/ADMIN_PASSWORD/DEMO_PASSWORD`.

## Surfaces

| URL | What |
|---|---|
| `/` | Storefront (per tenant). `?store=<slug>` or subdomain `<slug>.localhost` switches |
| `/admin.html` | **Store console**: dashboard, catalog+full product editor, SKUs/inventory, orders, returns, RFQs, sellers, settlements, promotions, content, taxonomy, attributes, payments, settings, analytics, audit, monitor, Data Studio |
| `/platform.html` | **Platform console**: provisioning policy, stores (launch wizard: owner, jurisdiction, taxation, categories, gateways, plan), Geo (countries/currencies/tax modes/providers+availability), plans, subscriptions, invoices, provider registry, monitoring, global audit |

Seed accounts (env-overridable; hints auto-hide when passwords change): platform `platform@luxora.shop/platform123` · store admins `admin@luxora.shop/admin123`, `admin@aurum.shop/aurum123` (INR/GST/Razorpay/UPI/Delhivery), `admin@velora.shop/velora123` (AED/VAT/Tabby, brand mode) · customer `demo@luxora.shop/demo123`.

## The product model

**Meta hierarchy**: domain → industry → category → subcategory → family → model → product → variant/SKU → inventory → serialized items. **33 industries, 23 product types, 16 vertical profiles** (grocery, jewellery, chemical, vehicle, service, rental… — each an editable field schema), EAV attribute engine, universal relationships (product relations + `links` graph), media/packaging/UOM/lifecycle engines, **contexts** (`tax / invoice / payment` per industry, validated at checkout, server auto-derived), pluggable providers (**16 payment incl. country rails: Stripe, Razorpay, UPI, PIX, iDEAL, M-Pesa, Tabby…**, shipping, notifications, tax) with per-country availability as a relation table, **currencies + FX** (entities, rates, history, optional JSON feed sync), tiered/B2B pricing, promotions with coupon redemption, settlements, RFQs.

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
