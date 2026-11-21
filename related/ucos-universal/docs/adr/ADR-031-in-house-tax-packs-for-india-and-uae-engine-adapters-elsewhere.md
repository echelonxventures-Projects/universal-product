# ADR-031: In-house tax packs for India and UAE; engine adapters elsewhere

| Field | Value |
|---|---|
| Status | Accepted |
| Deciders | Architecture Board (U01 root authority) |
| References | U31 Tax; open decision U31 |

## Context
Tax determination must be exact for P1 markets and extensible to others.

## Decision
Build **in-house tax packs for India (GST, e-invoicing, TCS) and UAE (VAT)** in P1, because their rules are well specified and core to the launch. For the US, EU and other regimes, use **certified tax-engine adapters** (Avalara/Vertex class) behind the `tax.determination` port.

## Alternatives considered
- Buy an engine everywhere: weak India e-invoicing support and cost per transaction at small-merchant scale.
- Build everywhere: the US sales-tax rule volume makes it uneconomic.

## Consequences
**Positive**
- Precise control where UCOS launches; breadth elsewhere.

**Negative / costs**
- UCOS maintains the India and UAE rule content under governance.

## Enforcement
Tax rule regression suites; `CMP-MAP-01`.
