# ADR-0007: Every finite enumeration is disclosed or migrated

| Field | Value |
|-------|-------|
| Status | Proposed |
| Date | 2026-08-21 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | UISD ISD-L-01, ISD-CE-01…11, UCKP-ART-17 |
| Supersedes | none |

## Context

ISD-L-01 states that no enumeration claims completeness silently. Measured: 224 Enum classes exist in non-test `engine/`, `platform/`, `intelligence/` and `data/`; 9 are disclosed. Of the 25 that name entity types, relationship types, technologies, storage models or capability categories, **23 are undisclosed**. Most of the remaining 199 are binary verdicts and make no claim about what can exist.

## Decision

For every finite enumeration we determine whether it is (A) a true closed governance invariant or (B) a current projection that can evolve. Every A is disclosed in `closed_enumeration_disclosures` with its closing invariant and admission path. Every B moves authority to the Entity + Classification + Relationship model per ADR-0006. Enumerations already open by a declared extension mechanism — `ContextKind` and its siblings, which carry `ContextTaxonomy.extend()` — are disclosed as *known sets*, not migrated.

## Consequences

Positive: no silent finite boundary survives. Neutral: disclosure is data; migration is additive. Reversible: disclosures are declarative entries.

## Compliance

- [x] Non-contradiction with the constitutional/EES corpus asserted (CC-02).
- [x] Rollback / migration path recorded (CC-04).
- [x] Traceability links to affected artifacts recorded (CC-05).
- [x] No secret material embedded (SEC-04).
