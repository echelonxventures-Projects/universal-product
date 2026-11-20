# Offers

> Generated from `_registry/business-domains.json`, the code and `docs/source/offer.md` — edit those, then run `node scripts/domain-docs.js`.

## Overview

The offers themselves: every price a buyer pays less or gets more, and every rule about how they apply — the offer record, its types, its scopes, its channels, its funders, its stacking policy and its governance. A coupon, a voucher, a gift card, a cashback, a reward and a group buy are their own domains; this one decides which of them applies.

**Foundation domain:** Commerce · **Used by:** Shopper, Seller, Store administrator, Platform administrator, Partner or affiliate

## Switches and settings

Each is switched on per store under ⚙️ Capabilities; its parameters are that store's settings.

### Deals page & strip (`deals`)

The /deals page, the header deal link and the storefront offers strip.

### Deal countdown (`countdown`)

A live countdown badge on time-limited offers.

### Price match (`price_match`)

A shopper shows the item cheaper elsewhere; staff approve the difference, credited to their wallet (a caseKinds row).

### Trade-in (`exchange_offers`)

A shopper describes what they trade in; staff value it, and the value comes off one item in their bag.

## Architecture

| Module | What it is |
|---|---|
| `lib/goip.js` | GOIP Ω∞ — GLOBAL OFFER INFRASTRUCTURE PLATFORM Universal Incentive · Offer · Reward · Value-Exchange operating system for LUXORA. |
| `lib/grants.js` | the grant registry: where a thing granted is issued. |
| `lib/offers.js` | Central Offers / Coupons / Discounts / Wallet engine. ONE reusable service (like registry.js / ai.js / modules.js) that any surface — storefront cart, checkout, platform subscription billing, AI metering, or a client API — calls to compute discounts, credits, free-shipping and coupon redemptions. Everything (types, scopes, channels, directions, funders, coupon kinds, limits) is DATA in meta_lists; new offer types/scope rules are added without code. Every offer is a row of `offers` — the per-store promotions it once read beside them were moved into it (portPromotions), so there is one record and one evaluation for every offer. |
| `lib/routes/offer.js` | offer domain routes (moved from lib/api.js; _registry/business-domains.json). Each handler answers one route of the offer domain; what it needs from the shared HTTP kit (lib/api.js) is passed in as `kit`. |

**Registry lists** (editable in Data Studio): `offerTypes`, `offerDirections`, `offerChannels`, `offerScopes`, `offerFunders`, `stackingPolicies`, `offerStatuses`

## Data model

### `attribution`

| Column | Type |
|---|---|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT |
| `tenant_id` | INTEGER NOT NULL |
| `order_id` | INTEGER |
| `ad_id` | INTEGER |
| `seller_id` | INTEGER |
| `model` | TEXT DEFAULT 'last_click' |
| `revenue` | REAL DEFAULT 0 |
| `commission` | REAL DEFAULT 0 |
| `created_at` | TEXT NOT NULL DEFAULT (datetime('now')) |

### `offers`

| Column | Type |
|---|---|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT |
| `tenant_id` | INTEGER NOT NULL DEFAULT 0 |
| `scope_level` | TEXT NOT NULL DEFAULT 'tenant' |
| `channel` | TEXT NOT NULL DEFAULT 'commerce' |
| `name` | TEXT NOT NULL |
| `code` | TEXT DEFAULT '' |
| `type` | TEXT NOT NULL |
| `direction` | TEXT NOT NULL DEFAULT 'discount' |
| `value` | REAL DEFAULT 0 |
| `currency` | TEXT |
| `scope_type` | TEXT NOT NULL DEFAULT 'store' |
| `scope_value` | TEXT DEFAULT '{}' |
| `funder` | TEXT NOT NULL DEFAULT 'self' |
| `funder_ref` | TEXT DEFAULT '' |
| `brand_ref` | TEXT DEFAULT '' |
| `min_amount` | REAL DEFAULT 0 |
| `min_qty` | INTEGER DEFAULT 0 |
| `max_discount` | REAL DEFAULT 0 |
| `usage_limit` | INTEGER DEFAULT 0 |
| `per_owner_limit` | INTEGER DEFAULT 0 |
| `used` | INTEGER DEFAULT 0 |
| `stack_group` | TEXT DEFAULT '' |
| `stack_policy` | TEXT DEFAULT 'stack_with_others' |
| `priority` | INTEGER DEFAULT 0 |
| `starts` | TEXT |
| `ends` | TEXT |
| `status` | TEXT DEFAULT 'active' |
| `rules` | TEXT DEFAULT '{}' |
| `summary` | TEXT DEFAULT '' |
| `source` | TEXT DEFAULT 'offer' |
| `created_at` | TEXT NOT NULL DEFAULT (datetime('now')) |
| `deleted_at` | TEXT |
| `domain` | TEXT DEFAULT 'incentive' |
| `benefit` | TEXT DEFAULT '' |
| `reality` | TEXT DEFAULT 'any' |
| `economic_unit` | TEXT DEFAULT '' |
| `temporal_spec` | TEXT DEFAULT '{}' |
| `spatial_spec` | TEXT DEFAULT '{}' |
| `conditions` | TEXT DEFAULT '{}' |
| `distribution` | TEXT DEFAULT '[]' |
| `attribution_model` | TEXT DEFAULT 'last_touch' |
| `funding` | TEXT DEFAULT '{}' |
| `governance` | TEXT DEFAULT '{}' |
| `campaign` | TEXT DEFAULT '' |
| `version` | INTEGER DEFAULT 1 |
| `parent_id` | INTEGER |
| `uid` | TEXT |

### `goip_touchpoints`

| Column | Type |
|---|---|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT |
| `tenant_id` | INTEGER NOT NULL DEFAULT 0 |
| `subject_uid` | TEXT DEFAULT '' |
| `offer_id` | INTEGER |
| `code` | TEXT DEFAULT '' |
| `kind` | TEXT NOT NULL DEFAULT 'view' |
| `party` | TEXT DEFAULT '' |
| `party_type` | TEXT DEFAULT 'customer' |
| `channel` | TEXT DEFAULT 'commerce' |
| `distribution` | TEXT DEFAULT 'in_app' |
| `device` | TEXT DEFAULT '' |
| `owner` | TEXT DEFAULT '' |
| `session` | TEXT DEFAULT '' |
| `order_id` | INTEGER |
| `value` | REAL DEFAULT 0 |
| `unit` | TEXT |
| `context` | TEXT DEFAULT '{}' |
| `created_at` | TEXT NOT NULL DEFAULT (datetime('now')) |
| `uid` | TEXT |

### `goip_budgets`

| Column | Type |
|---|---|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT |
| `tenant_id` | INTEGER NOT NULL DEFAULT 0 |
| `domain` | TEXT NOT NULL DEFAULT 'incentive' |
| `funder` | TEXT NOT NULL DEFAULT 'self' |
| `funder_ref` | TEXT DEFAULT '' |
| `unit` | TEXT NOT NULL |
| `allocated` | REAL DEFAULT 0 |
| `reserved` | REAL DEFAULT 0 |
| `consumed` | REAL DEFAULT 0 |
| `period` | TEXT NOT NULL DEFAULT '' |
| `status` | TEXT NOT NULL DEFAULT 'open' |
| `policy` | TEXT DEFAULT '{}' |
| `created_at` | TEXT NOT NULL DEFAULT (datetime('now')) |
| `updated_at` | TEXT |
| `uid` | TEXT |

### `goip_settlements`

| Column | Type |
|---|---|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT |
| `tenant_id` | INTEGER NOT NULL DEFAULT 0 |
| `period` | TEXT NOT NULL DEFAULT '' |
| `party` | TEXT NOT NULL DEFAULT '' |
| `party_type` | TEXT NOT NULL DEFAULT 'merchant' |
| `unit` | TEXT NOT NULL |
| `gross` | REAL DEFAULT 0 |
| `fees` | REAL DEFAULT 0 |
| `net` | REAL DEFAULT 0 |
| `redemptions` | REAL DEFAULT 0 |
| `status` | TEXT NOT NULL DEFAULT 'accrued' |
| `reference` | TEXT DEFAULT '' |
| `paid_at` | TEXT |
| `meta` | TEXT DEFAULT '{}' |
| `created_at` | TEXT NOT NULL DEFAULT (datetime('now')) |
| `updated_at` | TEXT |
| `uid` | TEXT |

### `goip_entitlements`

| Column | Type |
|---|---|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT |
| `tenant_id` | INTEGER NOT NULL DEFAULT 0 |
| `owner` | TEXT NOT NULL DEFAULT '' |
| `benefit` | TEXT NOT NULL DEFAULT '' |
| `unit` | TEXT DEFAULT '' |
| `qty` | REAL DEFAULT 0 |
| `tier` | TEXT DEFAULT '' |
| `scope` | TEXT DEFAULT '{}' |
| `starts` | TEXT |
| `ends` | TEXT |
| `status` | TEXT NOT NULL DEFAULT 'active' |
| `source_offer` | INTEGER |
| `source_redemption` | INTEGER |
| `meta` | TEXT DEFAULT '{}' |
| `created_at` | TEXT NOT NULL DEFAULT (datetime('now')) |
| `uid` | TEXT |

## API reference

Every call is JSON over HTTPS; store calls carry the store (`?store=`) and the session; mutating calls accept an `Idempotency-Key` header where noted.

| Method and path | Handler | What it does |
|---|---|---|
| `GET /api/offers` | `apiOffersList` | — |
| `POST /api/offers` | `apiOfferSave` | — |
| `PUT /api/offers/:id` | `apiOfferSave` | — |
| `DELETE /api/offers/:id` | `apiOfferDelete` | — |
| `POST /api/offers/preview` | `apiOffersPreview` | — |
| `GET /api/platform/offers` | `apiPlatformOffers` | — |
| `GET /api/goip` | `apiGoipManifest` | — |
| `GET /api/goip/exchanges` | `apiGoipExchanges` | — |
| `GET /api/goip/exchanges/:id` | `apiGoipExchange` | — |
| `GET /api/goip/context` | `apiGoipContext` | — |
| `GET /api/goip/treasury` | `apiGoipTreasury` | — |
| `GET /api/goip/settlements` | `apiGoipSettlements` | — |
| `GET /api/goip/entitlements` | `apiGoipEntitlements` | — |
| `GET /api/goip/touchpoints` | `apiGoipTouchpoints` | — |
| `GET /api/goip/widget` | `apiGoipWidget` | — |
| `GET /api/goip/registry/:name` | `apiGoipRegistry` | — |
| `GET /api/goip/intelligence/:key` | `apiGoipIntelligence` | — |
| `GET /api/goip/feed/:channel` | `apiGoipFeed` | — |
| `POST /api/goip/:capability` | `apiGoipCapability` | — |

## Process flows

Each record's life is a declared state machine (`lib/seed/states.json`): the moves it may make, and the actions that make them.

### Offer settlement (`goip_settlement`)

```mermaid
stateDiagram-v2
  [*] --> accrued
  reconciled --> [*]
```

Actions: 

### Entitlement (`entitlement`)

```mermaid
stateDiagram-v2
  [*] --> active
  consumed --> [*]
  revoked --> [*]
```

Actions: 

### Offer budget (`goip_budget`)

```mermaid
stateDiagram-v2
  [*] --> open
```

Actions: 

### Offer (`offer`)

```mermaid
stateDiagram-v2
  [*] --> draft
```

Actions: 

### Offer governance (`offer_governance`)

```mermaid
stateDiagram-v2
  [*] --> draft
```

Actions: `submit` → submitted · `approve` → approved · `reject` → rejected · `certify` → certified · `publish` → published · `suspend` → suspended · `retire` → retired · `reopen` → draft

## Data flow

```mermaid
flowchart LR
  U([Shopper / Seller / Store administrator / Platform administrator / Partner or affiliate]) --> UI[deals.html, store console, platform console]
  UI --> API[19 API routes]
  API --> ENG[goip.js, grants.js, offers.js, offer.js]
  ENG --> DB[(attribution, offers, goip_touchpoints, goip_budgets, goip_settlements, goip_entitlements)]
  ENG --> SM{{5 state machines}}
```

## User interface

**Pages:** `deals.html`

**Store console:** 🏷️ Price Match · ♻️ Trade-ins

**Platform console:** 🏷️ Offers · Affiliates · ⭐ Loyalty · 🎁 Rewards · 🔗 Referrals · 🏷️ Offers · Affiliates · Ω∞ GOIP · Value Exchange

## User flows

_Not yet written — `docs/source/offer.md`, section `## Flows`._

## Manuals

### Shopper

_Not yet written — `docs/source/offer.md`, section `## Manual: shopper`._

### Seller

_Not yet written — `docs/source/offer.md`, section `## Manual: seller`._

### Store administrator

_Not yet written — `docs/source/offer.md`, section `## Manual: store_admin`._

### Platform administrator

_Not yet written — `docs/source/offer.md`, section `## Manual: platform_admin`._

### Partner or affiliate

_Not yet written — `docs/source/offer.md`, section `## Manual: partner`._

