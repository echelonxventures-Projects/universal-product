# Vouchers

> Generated from `_registry/business-domains.json`, the code and `docs/source/voucher.md` — edit those, then run `node scripts/domain-docs.js`.

## Overview

An instrument of value that is not the shop's own discount and not a gift card: a bank voucher, a benefits note, an organisation's credit. Who stands behind it, whether it may be spent in part and how long it lives are its kind's rows; the code it travels on belongs to the Coupon domain.

**Foundation domain:** Commerce · **Used by:** Shopper, Store administrator, Platform administrator, Partner or affiliate

## Architecture

| Module | What it is |
|---|---|
| `lib/vouchers.js` | vouchers (the Voucher domain): an instrument of value that is not money and not a gift card. |

**Registry lists** (editable in Data Studio): `voucherKinds`

## Data model

### `vouchers`

| Column | Type |
|---|---|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT |
| `tenant_id` | INTEGER NOT NULL DEFAULT 0 |
| `code` | TEXT NOT NULL |
| `kind` | TEXT NOT NULL DEFAULT 'bank_voucher' |
| `issued_by` | TEXT DEFAULT '' |
| `offer_id` | INTEGER |
| `value` | REAL DEFAULT 0 |
| `currency` | TEXT DEFAULT 'USD' |
| `issued_to` | TEXT DEFAULT '' |
| `batch` | TEXT DEFAULT '' |
| `starts` | TEXT |
| `ends` | TEXT |
| `status` | TEXT DEFAULT 'active' |
| `note` | TEXT DEFAULT '' |
| `created_at` | TEXT NOT NULL DEFAULT (datetime('now')) |

## Data flow

```mermaid
flowchart LR
  U([Shopper / Store administrator / Platform administrator / Partner or affiliate]) --> UI[API]
  UI --> API[0 API routes]
  API --> ENG[vouchers.js]
  ENG --> DB[(vouchers)]

```

## User interface

## User flows

**Authorise.** A registered issuer defines a voucher kind, value unit, validity and holder scope. The voucher travels through the coupon code writer but remains attributable to its issuing authority.

**Validate and spend.** At checkout the platform validates the issuer, state, dates, tenant and remaining value before applying the voucher. The redemption and funder are recorded for settlement and reconciliation.

**Failure states.** Unknown, expired, revoked, exhausted or out-of-scope vouchers are refused without changing the order or ledger.

## Manuals

### Shopper

Enter an issuer-provided voucher code in the cart. Confirm the issuer, value and resulting discount before placing the order. Contact the issuer if the code is expired or outside its permitted store or audience.

### Store administrator

Accept only voucher kinds and issuers enabled by platform policy. Reconcile voucher redemptions by issuer and funder, and investigate mismatches through the audit trail rather than editing ledger rows.

### Platform administrator

Maintain voucher kinds and issuer permissions in the registry. Configure jurisdiction, unit, validity and settlement rules before granting a partner access to issue or fund vouchers.

### Partner or affiliate

Use the registered voucher contract to issue codes and reconcile redemptions. Keep issuer references stable so every redemption can be attributed and settled.

