# LUXORA Platform

**The Master Global Platform — one platform, configured into any platform.** The default boot is dependency-free: Node.js ≥ 22.13 (`node:http`, `node:sqlite`, `node:crypto` only) + vanilla JS frontends. The optional Redis queue (`LX_QUEUE=redis`: `bull`, `ioredis`) and Prometheus client (`prom-client`) are the only npm runtime packages, loaded only when configured; the test suite needs `npm ci` for `jsdom`. Everything—taxonomy, industries, product types, verticals, contexts, providers, countries, currencies, security policy—is *entity data*, never code.

**The master is alone.** A first boot seeds exactly one deployment — the platform's own — and the platform *is* that deployment. Configuring "the 1st e-commerce platform" means switching the marketplace atoms on; the 1st ERP platform, the workforce/procurement atoms; the 1st Uber platform, ride-hailing/dispatch; the 1st consultancy platform, the consultancy atoms. Every capability lives inside the master, and because the catalog is authorable, *any* platform type is a declaration plus a composition — never new code. The demo storefronts (aurum, velora) are fixtures that illustrate what composition produces, opt-in via `LUXORA_DEMO_BRANDS=1`, never the default population. Which deployment is the master's own is a marked platform fact (`platform_settings.master_deployment`), so a bare-host request, the console and every engine resolve to it without enumerating peers.

**Nothing is a bundle.** There is no "marketplace" or "commerce" entity — those are *compositions*. The only thing that exists is a **capability atom**: one individually switchable, individually tunable function (`buy_box`, `escrow`, `reviews`, `gift_cards`, `rfq_bidding`…) declared as a row in `platform_capabilities` with typed params and the console sections it governs. A store *is* the set of atoms it switched on (`GET /api/capabilities` → `composition`). Named blends (`blend_marketplace`, `blend_quick_commerce`…) and purchasable archetypes are convenience references to atoms — never the gate. The grant engine derives the console surface from the live composition (`lib/authz.js`), so nothing is ever granted as a package. **This holds platform-wide**: the 18 former `settings.features.*` booleans (reviews, Q&A, deals, coupons, gift cards, memberships, risk screening…) are atoms in the same catalog, switched and tuned exactly the way `buy_box` is — one switch, one vocabulary, shopper-facing *and* commerce-facing alike.

## Documentation

End‑to‑end guides for every role — **Customers, Store Admins, Support, Marketplace Sellers, and Platform (Super) Admins** — live in **[USER_MANUAL.md](USER_MANUAL.md)** (roles & capability matrix, per‑surface walkthroughs, security, glossary, troubleshooting).

The complete **pictorial flow** of the whole platform — three planes, the 10‑layer request pipeline, multi‑tenant resolution, meta hierarchy, pricing/checkout, B2B (RFQ·Tender·Contract), supply (sellers vs suppliers), serialization, lifecycles, modules, data model and role matrix — is in **[FLOWS.md](FLOWS.md)**.

## Run

```bash
npm start                    # http://localhost:3000
PORT=8787 ./serve.sh         # supervised (auto-restart), writes .luxora.pid
./stop.sh                    # clean stop
npm test                     # syntax + 620-assertion jsdom E2E suite (+197 GOIP + 724 UCOS Ω∞/theme/global-catalog audits: 100% universe instantiation, freeze criteria, catalog activation to 100% across 267 families, per-domain state machines, universal theming, the §394/§395 dashboard & reporting engines, the §1/§5 global catalog & permission-gated store import) (own DB/port)
```

Env: `PORT`, `LX_DB` (db path), `LUX_TLS=1` (HTTPS; self-signed generated via openssl, or supply `LUX_TLS_KEY`/`LUX_TLS_CERT`), `LUXORA_MASTER_KEY`, `LUXORA_PEPPER`, `LUXORA_DEMO_HINT=0`, `LUXORA_DEMO_BRANDS=1` (install the demo-brand fixtures — aurum the industry marketplace, velora the brand house — alongside the master's own deployment; a default boot seeds the master alone), `LX_OFFLINE=1` (force all outbound payments/notifications/AI to the offline-simulated path — CI/no-secrets), seed overrides `PLATFORM_EMAIL/PLATFORM_PASSWORD/ADMIN_EMAIL/ADMIN_PASSWORD/DEMO_PASSWORD`.

### Production

The runtime needs **Node ≥ 22.13** — `lib/db.js` uses the built-in `node:sqlite`, which is unavailable (22.5–22.12: behind `--experimental-sqlite`) before that. The boot checks the version before loading the database layer and exits with the required one rather than a bare module error.

Behind a reverse proxy or load balancer, set `LX_TRUST_PROXY=1` so per-client rate limits and audit IPs use `X-Forwarded-For` (without it the header is ignored, since a client could forge it). Request bodies are capped at 1 MB (413 beyond).

**Email and SMS.** Sign-in codes, magic links, password resets, order confirmations and shipping notices go to the person's own email/phone. Each store can use its own live notification gateway (SMTP, SendGrid, Resend, Twilio); every other store uses the platform default:

| Variable | Meaning |
|---|---|
| `LX_MAIL_PROVIDER` | `smtp`, `sendgrid` or `resend` |
| `LX_MAIL_FROM` | sender, e.g. `Shop <no-reply@shop.example>` |
| `LX_SMTP_URL` | `smtps://user:pass@host:465` or `smtp://user:pass@host:587` (STARTTLS is required on 587; `LX_SMTP_ALLOW_PLAINTEXT=1` only for a local relay) |
| `LX_MAIL_API_KEY` | API key for `sendgrid` / `resend` |
| `LX_SMS_PROVIDER=twilio`, `LX_SMS_ACCOUNT_SID`, `LX_SMS_AUTH_TOKEN`, `LX_SMS_FROM` | SMS codes |
| `LX_PUBLIC_URL` | the address emailed links point at, e.g. `https://shop.example` (else the store's own domain). Links are never built from the request's `Host` header in production. |

A production boot without a platform email transport logs a warning: password resets then only work for stores that configured their own gateway.

```bash
docker compose up --build     # http://localhost:3000 (data/ and redis persisted as volumes)
```

Four things are required of a production boot, and two are enforced at startup:

- **`PLATFORM_PASSWORD` and `ADMIN_PASSWORD` must be set.** The seed defaults (`platform123` / `admin123`) exist so a first local boot is observable; with `NODE_ENV=production` the platform **refuses to start** until both are set, printing the two accounts that would otherwise boot with a documented default. (An already-seeded DB is unaffected — the gate only blocks the first boot that would create the accounts.)
- **Persist `data/`.** The encryption keyring (`master.json`) and the registry seal (`registry.json`) live there. A redeploy without the volume loses the ability to decrypt sealed gateway credentials and to verify the registry seal.
- **Set `LX_METRICS_TOKEN` (≥ 16 chars)** if a scraper reads `/metrics` — otherwise the endpoint answers only to a live platform-admin session and returns 401 to everything else.
- **Rotate the seeded passwords** even when set via env (`Platform → Administration`, `Store → Team`).

`docker compose` wires all four: the two passwords are required (`${VAR:?…}`), the token is passed through, and `data/` is a named volume. `/healthz` is the container `HEALTHCHECK`.

Runtime backends are **config**, not code — default to in-process (SQLite + memory + inline queue + local disk); switch any of them via `Platform → Runtime` (or `platform_settings.runtime`) / env: `LX_CACHE`, `LX_QUEUE`, `LX_STORAGE`, `LX_RATELIMIT`, `LX_SESSION`, `LX_OUTBOUND`, `LX_DB_DRIVER` (`memory|redis`, `inline|redis|webhook`, `local|s3|webhook`, `sqlite|postgres`, `auto|offline|live`) with connection params `LX_REDIS_URL`, `LX_S3_BUCKET/REGION/ACCESS/SECRET/ENDPOINT`, `LX_PG_URL`, `LX_WEBHOOK_URL/SECRET`, `LX_WORKER=1` (run a Redis queue consumer on this node), `LX_IDEMPOTENCY=0` (disable idempotency); every response carries an `X-Request-Id`/`X-Trace-Id` and mutations accept an `Idempotency-Key` for safe retries. All dependency-free (raw RESP / SigV4 / PG wire over `net`+`fetch`); unconfigured drivers fall back safely. *Note (B):* the async dual-engine + SQLite→Postgres **dialect translator, wire client (`lib/pg.js` extended protocol), and migration planner (`lib/migrate.js`)** are built and tested (`GET /api/platform/db` reports driver/health/plan). The final request-path sync→async cutover needs a live Postgres and is a runbook step (FLOWS §25) — the machinery to make it mechanical is in place.

## Surfaces

| URL | What |
|---|---|
| `/` | Storefront (per tenant). `?store=<slug>` or subdomain `<slug>.localhost` switches |
| `/admin.html` | **Store console**: dashboard, catalog+full product editor, SKUs/inventory, orders, returns, RFQs, sellers, settlements, **contracts & tenders (B2B)**, suppliers & **serialized items**, **compliance & certs**, **localizations (i18n)**, **AI Studio**, promotions, content, taxonomy, attributes, payments, settings, analytics, audit, monitor, Data Studio, **Team & Roles (RBAC staff roles)** |
| `/platform.html` | **Platform console** — the platform's own backend, organized as the UCOS Ω∞ constitution declares: **12 canonical sections** (Foundation → Knowledge → Business → Commerce → Operations → Experience → Intelligence → Governance → Platform → Observability → Administration → Architecture), collapsible in the sidebar, opening on **◈ Command**. Every capability has exactly one home — 295 leaves, zero duplicates, zero orphans — and each leaf resolves to a dedicated surface, a platform dataset, or a universe registry record, so navigation never dead-ends. Tenants are authored in a single modal (the guided store wizard is gone); stores are no longer the console's organizing principle. |

Seed accounts (env-overridable; hints auto-hide when passwords change): platform `platform@luxora.shop/platform123` · store admins `admin@luxora.shop/admin123`, `admin@aurum.shop/aurum123` (INR/GST/Razorpay/UPI/Delhivery), `admin@velora.shop/velora123` (AED/VAT/Tabby, brand mode) · customer `demo@luxora.shop/demo123`.

## The product model

**Meta hierarchy**: domain → industry → category → subcategory → family → model → product → variant/SKU → inventory → serialized items. **33 industries, 23 product types, 16 vertical profiles** (grocery, jewellery, chemical, vehicle, service, rental… — each an editable field schema), EAV attribute engine, **RBAC staff roles + per-section permissions**, **universal identity layer** (GTIN/UPC/EAN/ISBN/MPN/OEM/VIN/IMEI/HSN/UNSPSC/GS1‑GPC/eCl@ss/ETIM — 20 codes), **variant groups** (SKU‑authoritative pricing), **structured compliance & certification records** (issuer/jurisdiction/validity), **per‑object i18n localizations**, **supplier & procurement model** (suppliers, price lists, product‑supplier links, lead time, MOQ, payment terms), **B2B contracts** (fixed/tiered contract pricing applied at cart + checkout) and **tenders** (award → auto‑contract), universal relationships (product relations + `links` graph), media/packaging/UOM/lifecycle engines, **contexts** (`tax / invoice / payment` per industry, validated at checkout, server auto-derived), pluggable providers driven by **declarative request specs** (fill-in-the-blanks JSON in `provider_defs.spec`, no per-provider code — Meta/Google Ads/GA4/TikTok + custom providers are data) including **16 payment incl. country rails: Stripe, Razorpay, UPI, PIX, iDEAL, M-Pesa, Tabby…**, shipping, notifications, tax) with per-country availability as a relation table, **currencies + FX** (entities, rates, history, optional JSON feed sync), tiered/B2B pricing, promotions/coupons with wallet rewards + refund clawback + per-owner/usage limits + funder (bank/brand) split, settlements, RFQs · **first-class Tax engine** (jurisdiction rates, classes, VAT/GST validation, reverse-charge, inclusive/exclusive) and **Billing engine** (line-item + usage-metered invoices, proration, credit notes, refunds-to-wallet, dunning, aging) — all configuration-driven.

**Deployment modes per tenant** (marketplace / industry / brand) — same backend, different configuration. Three stores ship seeded to demonstrate all three.

**Entity engine**: every table is a declared entity (fields, types, validation, permissions, composite keys, universal UUIDs via SQLite triggers). Define *new entities* in Data Studio or via `POST /api/meta/entity-def` — CRUD, validation, audit, and forms appear automatically. Custom providers register as JSON manifests, no code.

## GOIP Ω∞ — Global Offer Infrastructure Platform

The platform's incentive layer is not a coupon feature; it is a **constitution**. `GET /api/goip` returns it, and the platform console's **Ω∞ GOIP** screen renders it live.

One record — a **value exchange** — walks one chain: **value exchange → context → conditions → eligibility → benefit → execution → settlement → audit**. Everything a business calls a coupon, cashback, reward, gift card, voucher, discount, subsidy, commission, membership, tier, grant, entitlement or future economic instrument is an *instance* of that record.

**Consumers speak 22 capabilities and nothing else** — `create · clone · publish · discover · search · compare · validate · reserve · activate · issue · track · attribute · apply · redeem · settle · fund · pay · optimize · forecast · simulate · govern · audit` — through one entry point: `POST /api/goip/<capability>`. They never learn the words coupon, cashback or gift card. Each capability declares its stage, its engine, the single store it writes, the meter it bills, and its scope (`any` shopper session · `tenant` store admin · `platform` super admin).

| Layer | What it is | Count |
|---|---|---|
| Constitution | the 8-stage chain every exchange walks | 8 |
| Capability layer | the only vocabulary a consumer needs | 22 |
| Decision fabric | engines with exactly one job each (context resolution, eligibility, qualification, decision, discovery, benefit resolution, conflict, stacking, ranking, optimization, recommendation, personalization, pricing, simulation, forecasting, fraud, risk, governance) | 18 |
| Context fabric | dimensions resolved on **every** decision (reality, temporal, spatial, economic, governance, audience, identity, behavioural, product, catalog, cart, session, device, market, inventory, risk, organization, merchant, provider, partner, creator, channel, event, campaign, AI) | 25 |
| Domain ecosystem | constitutional domains, each with one owner store and one discriminator | 67 |
| Benefit fabric | value constructs, each bound to the single math engine in `lib/offers.js` | 25 |
| Distribution · attribution · funding · settlement · intelligence · governance | the operating fabrics | 16 · 12 · 12 · 11 · 15 · 10 |
| Incentive graph | node kinds · relationships, projected onto the existing `links` table | 21 · 14 |
| Commercialization | deployment models · billing models · meters | 11 · 12 · 17 |

**Nothing about time, place or money is assumed.** Calendars (Gregorian, fiscal, academic, Islamic, Hebrew, lunar, **Mars Darian**, Federation, custom planetary), chronologies, temporal units, spatial systems (Earth administrative, Mars territorial, lunar colonial, galactic zonal, virtual), coordinate systems, hierarchy paths (`earth.in.bihar.patna`, `mars.olympus.sector-7`, `moon.alpha`, `galaxy-7.zone-22`), economic units (USD/EUR/INR, Mars credits, lunar tokens, federation credits, carbon/energy/resource units, points, coins, tokens) and reality models are **registry rows in `meta_lists`** — add a planet, a calendar, a currency or an entire civilization in Data Studio and every engine obeys it on the next request. No redesign, no redeploy.

**Zero duplicate · zero overlap by construction.** GOIP owns only what had no home: the constitution, context resolution, the temporal/spatial/economic/reality domains, the condition engine, attribution, funding budgets, settlement runs, entitlements, intelligence, governance state and commercialization — four tables (`goip_touchpoints`, `goip_budgets`, `goip_settlements`, `goip_entitlements`). Benefit math stays in `offers.HANDLERS` (GOIP registers its 25 benefits there rather than forking it), money stays in `wallets`/`wallet_entries`, codes stay in `coupons`, the redemption ledger stays in `coupon_redemptions`, metering stays in `billing.js` → `usage_records`, the graph stays in `links`, registries stay in `meta_lists`, audit stays on the hash chain. Every domain names the exact discriminator that isolates its rows — `GET /api/goip` reports `domains.overlapping: 0` and fails loudly if that ever stops being true.

**Ships wired and testable.** First boot seeds seven global value exchanges that exercise every axis — `GOIPWELCOME` (condition-gated), `GOIPBANK` (multi-party funded 70/30 bank+brand), `GOIPSOL` (Mars Credits, Olympus Territory, Darian calendar), `GOIPGOV` (state subsidy, jurisdiction-restricted), `GOIPPOINTS` (points ledger), `GOIPGOLD` (entitlement grant), `GOIPDEFER` (deferred value) — plus funding budgets in two economic units and a touchpoint path. None of them auto-applies to a cart. The flagship store ships with the module installed; the platform console's **Ω∞ GOIP** screen, the store console's **Ω∞ GOIP** screen (with a decision tester that shows *why* something did not apply) and the storefront's offer strip on `/deals.html` are all live against it.

**Sellable and billable.** GOIP is a marketplace module (`goip`, plus `goip-agent` for agent/MCP access). Every capability invocation meters into the billing engine — per tenant, merchant, provider, offer, redemption, settlement, payout, API call, active user, campaign, revenue share or hybrid — and rides the existing invoice run. Stores without the module are metered at zero.

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
lib/capabilities.js  THE capability layer — the atom catalog (marketplace, fintech,
                     quick-commerce, B2B-trade + the 18 storefront features that were
                     settings booleans), blends, per-tenant composition, one gate
lib/settings.js      per-tenant settings; `features` is DERIVED from the composition
lib/registry.js      live registries (geo, currencies+FX, tax modes, providers, availability, meta lists)
lib/meta.js          seed definitions (industries, types, verticals, contexts, lifecycle)
lib/providers.js     seed definitions (countries, providers, currencies) — data, editable post-seed
lib/goip.js          GOIP Ω∞ — the value-exchange constitution: capability router, context/
                     temporal/spatial/economic/reality domains, 67-domain map, fabrics, graph
lib/offers.js        the ONE benefit-math engine GOIP resolves benefits through
lib/api.js           ~140 REST routes (incl. /api/goip/*, /api/dashboards/*, /api/reports/*); lib/uid.js UUID triggers; lib/metrics.js live traffic
lib/dashboards.js    Architecture1 §394/§395 — the universal dashboard & reporting engine:
                     dashboards, widgets and reports are rows; one generic aggregate
                     computes any metric over native entities or corpus universes
lib/gcatalog.js      UPIP §1/§5 — the universal global catalog: every product archetype
                     (Physical…Quantum, Future Unknown) is seeded automatically from the
                     corpus as platform data; stores import one only when permitted
public/              storefront + store console + platform console (no frameworks, no CDN)
data/                luxora.db + master.json (created at first boot)
```

**Global Operations — one cross-store surface, zero duplicated logic.** The Store Console
edits one tenant; the Platform Console watches all of them. Two generic primitives back it
(`test/gops.js`, 66 assertions):

- **The cross-tenant reader** — `entity.listEntitiesGlobal` runs the *same* entity
  definitions, field whitelist and parameterized predicates as the store reader
  (`/api/meta/entity/:key`), only with `tenant_id` SELECTed and the tenant predicate
  optional, behind `GET /api/platform/data/:key`. An unfiltered browse bounds *per store*
  so a large catalogue never crowds the other stores out.
- **The fan-out executor** — `GET /api/platform/fanout?path=<route>` resolves an existing
  read-only Store Console route from the *same* route table and runs it once per store
  under a scoped synthetic session, then merges (arrays concatenate with the store stamped
  on every row, numbers sum). Not one composite handler is re-implemented, so the platform
  and the store cannot drift. The allowlist is the security boundary and is data — a
  `meta_lists` row `platformFanout` opens or closes a capability from Data Studio.

Building it surfaced and fixed three latent defects that were silently breaking the Store
Console too: `view_history` queried for a non-existent `tenant_id` (analytics), a stray
`GROUP BY` returning no row for an order-less store (seller KPIs), and a bound-but-unused
period placeholder ("column index out of range").

*The flagship store ships with the whole corpus activated — every universe is
shopper-transactable on first boot (idempotent; other stores opt in with one call).*

*This is an educational demo project; it is not affiliated with any retailer.*
