# U14 — Currency & Unit Universe Constitution

| Field | Value |
|---|---|
| Universe ID | `U14-currency` |
| Layer | L4 Foundation |
| Domain | 01 Foundation |
| Steward | `ucos:org:foundation-money` |
| Version | 0.1.0 (Draft) |
| Delivery phase | P0 |
| Depends on | U04 Meta, U08 Reference Data (`iso4217`, `ucum`/`unece-rec20`), U13 Temporal (rate validity), U12 Geography (jurisdiction default currency) |
| Depended on by | Pricing, Offer, Cart, Order, Payment, Ledger, Tax, Subscription, Marketplace, Product (attribute units), Logistics (weights, dimensions), Inventory |
| Master references | §6.3 (money ruling), §13.3 (money rules), §10.2 (attribute units) |

> This universe owns **amounts and measures**: the `Money` and `Quantity` value types, currency metadata, rounding rules, exchange rates (as temporal facts), units of measure, dimensions and conversions. It does not own prices (U23), balances (U30) or tax (U31).

---

## 1. Constitution & Laws

| ID | Law | Enforcement |
|---|---|---|
| CUR-L1 | Monetary values are never floats. They are `Money { amount: decimal string, currency }`. | META-L3; SDK type; JSON schema pattern `^-?\d{1,18}(\.\d{1,8})?$`. |
| CUR-L2 | Arithmetic between different currencies is a type error unless an explicit `ExchangeRateRef` is supplied. | SDK throws `CUR_CURRENCY_MISMATCH`. |
| CUR-L3 | Rounding is explicit: every rounding names a `RoundingRule`. | SDK API requires it; linter forbids implicit `round()`. |
| CUR-L4 | FX rates are temporal facts with source and validity. A conversion records the rate id used. | `ConvertedMoney` carries `rateRef`. |
| CUR-L5 | Quantities carry units. Conversion is only between units of the same dimension. | `Quantity` type; `CUR_DIMENSION_MISMATCH`. |
| CUR-L6 | Allocation (splitting money) must conserve the total exactly. | `allocate()` algorithm §5.2, property tests. |

**Authorities:** rate sources and rate policies are level 3 (Treasury steward / tenant finance controller). Rounding rules for a jurisdiction are level 3 (Finance steward). Unit definitions are level 3 (Reference steward).

---

## 2. Ontology

- **Concepts:** `Currency` (from refdata + metadata), `Money` (value), `ExchangeRate` (fact), `RateSource`, `RatePolicy` (which source, which mark-up, which time), `RoundingRule`, `Unit`, `Dimension`, `Quantity` (value), `UnitConversion`, `PackagingUnit` (e.g. case of 12).
- **Dimensions:** `length, mass, volume, area, time, temperature, energy, power, data-size, data-rate, count, currency-rate, concentration, pressure, speed, voltage, current, luminous`.
- **Rounding modes:** `half-even` (banker's), `half-up`, `half-down`, `up`, `down`, `ceiling`, `floor`; plus `cash-increment` (e.g. CHF 0.05, AED 0.25 for cash).
- **Rate types:** `mid`, `buy`, `sell`, `official` (central bank), `card-network`, `psp-settlement`, `internal-treasury`.

---

## 3. Objects & Value Types

### 3.1 Value types
```json
Money:          { "amount": "2499.00", "currency": "INR" }
ConvertedMoney: { "amount": "110.41", "currency": "AED", "from": {"amount":"2499.00","currency":"INR"}, "rateRef": "ucos:fx:01J..", "rounding": "ucos:round:aed-standard" }
Quantity:       { "value": "1.250", "unit": "kg" }
Percentage:     { "value": "18.00" }                 // 18% ; decimal string
Dimensions:     { "length": Quantity, "width": Quantity, "height": Quantity }
```
`amount` precision is the currency's minor unit for *settled* amounts, and up to 8 decimals for *intermediate* amounts (unit prices, FX). Amounts are scaled to the minor unit on finalisation, using a RoundingRule.

### 3.2 `ucos.currency.Currency` (extends refdata iso4217 code)
`{ code, minorUnit (0,2,3), symbol (LocalizedText per locale via CLDR), cashIncrement?, defaultRounding: RoundingRuleRef, active: bool, digital: bool (e.g. stablecoins, loyalty points as pseudo-currency 'XPT-<program>') }`

### 3.3 `ucos.currency.ExchangeRate`
| Attribute | Type | Notes |
|---|---|---|
| `id` | UGID (`ucos:fx:`) | |
| `base`, `quote` | iso4217 | 1 base = `rate` quote |
| `rate` | Decimal (≤ 12 dp) | |
| `type` | RateType | |
| `source` | Reference→RateSource | |
| `validity` | TimeRange | |
| `observedAt` | TimePoint | |
| `tenant` | TenantRef or `global` | tenant rates override global |

### 3.4 `RateSource`, `RatePolicy`, `RoundingRule`
```yaml
RateSource: { id, name, adapter: fx.provider.<x>, refresh: TemporalPolicyRef, types: [mid, official] }
RatePolicy:                          # tenant-configurable, used by Pricing/Payment/Ledger
  id: ucos:fxpol:bazaar-display
  purpose: display | pricing | settlement | accounting | reporting
  source: ucos:fxsrc:ecb | ucos:fxsrc:rbi-reference | psp
  type: mid
  markupPercent: "1.50"
  timing: at-transaction | daily-close(Temporal calendar) | month-average
  staleAfter: PT26H
RoundingRule: { id, mode, scale: minorUnit|int, cashIncrement?, jurisdiction?, purpose: display|invoice-line|invoice-total|tax|payment }
```

### 3.5 `Unit`, `UnitConversion`, `PackagingUnit`
`Unit { code (UCUM), unece: rec20 code, dimension, symbol: LocalizedText, system: si|imperial|us|other }`.
`UnitConversion { from, to, factor: Decimal, additiveOffset?: Decimal (temperature scales only; not a time offset) }`; conversions are derived through the SI base unit.
`PackagingUnit { id, name, contains: Quantity(count|unit), of: UnitRef|ProductRef }`, e.g. `case = 12 × each`, owned here and referenced by Inventory.

---

## 4. Commands, Queries, Events, APIs

| Command | Effect / Events |
|---|---|
| `IngestRates(source)` | pull via adapter; validate (bounds vs previous ±10% → flag); store → `currency.rates.updated` |
| `PublishRate` (manual, treasury) | `currency.rate.published` |
| `DefineRatePolicy`, `DefineRoundingRule` | `currency.policy.changed` |
| `RegisterUnit`, `RegisterConversion` | `currency.unit.registered` |

| Query | Notes |
|---|---|
| `Convert(money, toCurrency, ratePolicy, at)` → ConvertedMoney | |
| `GetRate(base, quote, ratePolicy, at)` | |
| `Round(money, roundingRule)` | |
| `Allocate(money, ratios[] | weights[], roundingRule)` → Money[] | §5.2 |
| `ConvertQuantity(q, toUnit)` | |
| `FormatMoney(money, locale, style: standard|accounting|compact)` | CLDR |

```text
GET  /v1/currency/currencies          GET /v1/currency/rates?base=&quote=&at=&policy=
POST /v1/currency/convert             POST /v1/currency/allocate
GET  /v1/currency/units?dimension=    POST /v1/currency/units:convert
```
**Port:** `FxRateProviderPort`. Adapters: ECB, RBI reference rate, Open Exchange Rates, PSP settlement rate feeds, internal treasury.
**Errors:** `CUR_CURRENCY_MISMATCH`, `CUR_RATE_UNAVAILABLE`, `CUR_RATE_STALE`, `CUR_INVALID_AMOUNT`, `CUR_PRECISION_EXCEEDED`, `CUR_DIMENSION_MISMATCH`, `CUR_UNKNOWN_UNIT`.

---

## 5. Algorithms (normative)

### 5.1 Arithmetic
The SDK uses arbitrary-precision decimal (Go `apd`, JVM `BigDecimal`, TS `decimal.js`). Intermediate operations keep 8 dp. `finalize(money, rule)` scales to the currency minor unit.

### 5.2 Allocation (largest remainder)
```text
allocate(total, weights, rule):
  units ← total.amount × 10^minor                       # integer minor units
  raw_i ← units × w_i / Σw
  base_i ← floor(raw_i)
  remainder ← units − Σ base_i
  distribute +1 minor unit to the `remainder` parts with largest (raw_i − base_i),
     ties broken by index order (deterministic)
  return base_i / 10^minor
invariant: Σ result = total (exact); used for: discount pro-ration across lines,
           marketplace commission splits, tax allocation, payment splits, refunds
```

### 5.3 Conversion
`Convert` → choose the rate by `RatePolicy` (source, type, timing) → if older than `staleAfter`, fail with `CUR_RATE_STALE`, unless the policy allows the last known rate with a flag → apply markup → round with the rule → return `ConvertedMoney` with `rateRef`. Ledger postings record both the original and converted amounts (U30).

---

## 6. Security & Compliance
- Rates are `internal`. Tenant treasury rates are `confidential`.
- Writes need the treasury roles.
- Audit covers rate publications and policy changes.
- Compliance: supports accounting-standard FX treatment (IAS 21 timing, via RatePolicy purpose `accounting`) and consumer-law display rules (currency shown with total, via decision `currency.display.required-format` per jurisdiction).

## 7. Validation & Reuse
| Consumer | MUST |
|---|---|
| Any price, fee, tax, balance | `Money` |
| Any weight, dimension, volume, data size | `Quantity` with registered unit |
| Splits/pro-ration | `Allocate` |
| Multi-currency display | `Convert` with a `display` RatePolicy; never persist display conversions as prices |

Certification `ARCH-CUR-01` uses static scans to detect float types for money and `round(` calls without a rule. `ARCH-CUR-02` runs property tests for allocation conservation (1M cases).

## 8. Gaps & Evolution
```prolog
gap(missing_rate_policy, T, P) :- tenant(T), multi_currency(T), purpose(P), not rate_policy(T, P).
gap(missing_rate_source, Q)    :- currency_in_scope(Q), not rate_available(Q).
gap(missing_rounding, J)       :- in_scope(J), cash_payments_enabled(J), not rounding_rule(J, cash).
```
- **Self-healing:** if a rate feed fails, switch to the secondary source when `RatePolicy.fallbackSource` is set. Otherwise the conversion fails closed for `settlement` and `pricing` purposes, and serves stale-with-flag for `display`.
- **Evolution:** CBDCs and tokenised assets become new `Currency` entries with `digital: true`. Loyalty points are pseudo-currencies with their own Ledger accounts.

## 9. AI
- **AI uses:** unit extraction from product text (proposals), and anomaly detection on rate ingestion.
- **Agent tools:** `currency.convert`, `currency.format` (read).
- **Prohibited for agents:** publishing rates.

## 10. Operations
- **Signals:** `fx_rate_age_seconds{pair,policy}`, `fx_ingest_failures_total`, `conversion_requests_total`, `allocation_property_violations_total` (must be 0).
- **SLOs:** convert p99 < 1 ms (cached rates); rate freshness inside each policy's `staleAfter` 99.9% of the time.

## 11. UI
- **Views:** `currency.rate.board`, `currency.rate-policy.editor`, `money.input` (currency-aware decimal entry with locale separators), `quantity.input` (value + unit picker filtered by dimension).
- **UX:** always show the currency code where ambiguity exists ($ for USD, AUD and others). Indian grouping (₹1,23,456.00) follows CLDR.

## 12. Scale & DR
Rates: about 200 pairs × multiple sources × per-minute updates for PSP feeds. Partitioned history; the Platform Twin keeps rate history indefinitely for audit. Tier: T0 for reads (cached in SDK), T1 for ingestion.

## Appendix
- **B. Amendments:** add `RoundingRule`, `RatePolicy`, `RateSource`, `Dimension` and `PackagingUnit` to the U14 "owns" list in master §6.2.
- **C.** 0.1.0.

## Appendix D — Frame extensibility (amendment A-25, from U77)
- `Currency` belongs to a U77 `MonetarySystem`. ISO 4217 codes form the `sovereign-fiat` system. Every other currency (CBDC, stablecoin, crypto, loyalty points, in-game, community, future off-world currencies) uses a namespaced code `X-<systemSlug>-<code>` (e.g. `X-arena1-GOLD`, `X-bazaarpts-PTS`). Each declares `minorUnit` (up to 18 for tokens), its issuer, its settlement rails, and its convertibility.
- `Money.amount` precision limit rises to 38 digits / 18 decimals for digital assets. The ledger still uses exact decimals.
- `RatePolicy` can convert between monetary systems only through registered `convertibility` paths and rate sources (e.g. an in-game currency → USD rate published by the world operator). Conversions that are not allowed are refused.
- `Unit` belongs to a `UnitSystem`. Traditional/regional units (tola, bigha, jin, chi), astronomical units (AU, light-year, parsec) and virtual-world units are registered with conversions to SI. Mixed-system arithmetic always goes through SI.
- Gap rule: `gap(currency_without_system, C) :- currency(C), not monetary_system_of(C, _).`
