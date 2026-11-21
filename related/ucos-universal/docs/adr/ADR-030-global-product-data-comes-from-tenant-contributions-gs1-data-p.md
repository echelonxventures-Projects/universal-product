# ADR-030: Global product data comes from tenant contributions, GS1 data pools and licensed feeds

| Field | Value |
|---|---|
| Status | Accepted (commercial terms before P4) |
| Deciders | Architecture Board (U01 root authority) |
| References | U18 Product Intelligence; open decision U18; ADR-008 |

## Context
The global product master (GPID) needs breadth and quality from day one of P4.

## Decision
Sources, in order of trust: **manufacturer and brand syndication (GS1 data pools where licensed)**, **licensed commercial feeds**, then **tenant contributions** that pass matching and steward review. Each fact carries provenance and licence; facts whose licence forbids cross-tenant display are used for matching only.

## Alternatives considered
- Tenant contributions only: slow to reach coverage.
- Scraping: legally and ethically unacceptable.

## Consequences
**Positive**
- Coverage at launch with traceable provenance.

**Negative / costs**
- Licence costs; commercial workstream must finish before P4.

## Enforcement
ProductFact requires `source` and `licence`; U18 governance.
