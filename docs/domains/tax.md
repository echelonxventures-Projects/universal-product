# Tax

> Generated from `_registry/business-domains.json`, the code and `docs/source/tax.md` — edit those, then run `node scripts/domain-docs.js`.

## Overview

What tax applies and how much: tax modes, rules by place and product, and how tax is shown and charged.

**Foundation domain:** Rule · **Used by:** Store administrator, Platform administrator

## Switches and settings

Each is switched on per store under ⚙️ Capabilities; its parameters are that store's settings.

### Duties at checkout (`duties_at_checkout`)

Import duty paid up front. A rate is for a country and the beginning of an item's customs code; the most particular counts.

## Architecture

| Module | What it is |
|---|---|
| `lib/tax.js` | first-class Tax engine (all configuration, single source of truth for checkout + invoicing + reports). Rates are DATA: a jurisdiction rate registry (taxRules) with classes, plus per-product tax_rule overrides and compliance-based exemptions. Supports inclusive vs exclusive pricing, VAT/GST number validation, nexus, and digital-goods rules — so a store in any market/configures tax by data, not code. |
| `lib/features/duties_at_checkout.js` | duties at checkout: an order to another country pays its import duty up front. A rate is for a destination and the beginning of an item's customs code; the most particular one counts. |
| `lib/routes/tax.js` | tax domain routes (moved from lib/api.js; _registry/business-domains.json). Each handler answers one route of the tax domain. What it needs from the shared HTTP kit (lib/api.js) is passed in as `kit`. |

**Registry lists** (editable in Data Studio): `taxClasses`, `taxRules`, `exemptionReasons`, `taxNumberFormats`

## Data model

### `tax_modes`

| Column | Type |
|---|---|
| `key` | TEXT PRIMARY KEY |
| `label` | TEXT NOT NULL |
| `description` | TEXT |
| `fields` | TEXT DEFAULT '[]' |
| `position` | INTEGER DEFAULT 0 |
| `uid` | TEXT |

### `tax_rules`

| Column | Type |
|---|---|
| `country` | TEXT PRIMARY KEY REFERENCES countries(code) |
| `mode` | TEXT NOT NULL DEFAULT 'manual' |
| `standard` | REAL NOT NULL DEFAULT 0 |
| `reduced` | REAL |
| `digital` | REAL |
| `zero` | REAL |
| `note` | TEXT |

## API reference

Every call is JSON over HTTPS; store calls carry the store (`?store=`) and the session; mutating calls accept an `Idempotency-Key` header where noted.

| Method and path | Handler | What it does |
|---|---|---|
| `GET /api/admin/tax/report` | `apiTaxReport` | — |
| `GET /api/admin/tax` | `apiAdminTaxConfig` | — |
| `POST /api/admin/tax/quote` | `apiAdminTaxQuote` | — |

## Data flow

```mermaid
flowchart LR
  U([Store administrator / Platform administrator]) --> UI[API]
  UI --> API[3 API routes]
  API --> ENG[tax.js, duties_at_checkout.js, tax.js]
  ENG --> DB[(tax_modes, tax_rules)]

```

## User interface

## User flows

_Not yet written — `docs/source/tax.md`, section `## Flows`._

## Manuals

### Store administrator

_Not yet written — `docs/source/tax.md`, section `## Manual: store_admin`._

### Platform administrator

_Not yet written — `docs/source/tax.md`, section `## Manual: platform_admin`._

