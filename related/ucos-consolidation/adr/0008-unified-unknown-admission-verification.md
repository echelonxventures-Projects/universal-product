# ADR-0008: One verification suite proves unknown admission across every axis

| Field | Value |
|-------|-------|
| Status | Proposed |
| Date | 2026-08-21 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | UCKP-ART-16, UISD ISD-L-11, CEU-038 |
| Supersedes | none |

## Context

Unknown-admission coverage exists but is scattered: `test_unknown_system_type_is_representable`, `test_the_document_stays_open`, `test_the_matrix_stays_open`, and the CEU sufficiency suite. `engine/kernel/compliance.py` already proves eleven non-Earth categories with an unchanged kernel fingerprint. No single suite asserts the property across every axis the principle names.

## Decision

We create one Universal Expansion Verification suite proving admission of an unknown entity, context, relationship, technology, language, currency, measurement, intelligence, platform composition and future concept — each asserting the **kernel source fingerprint is unchanged**, which is the property that distinguishes an open substrate from an extensible one.

## Consequences

Positive: the openness claim becomes one falsifiable measurement. Neutral: the suite reuses the existing `kernel_source_fingerprint` mechanism rather than introducing a new one. Reversible: tests are additive.

## Compliance

- [x] Non-contradiction with the constitutional/EES corpus asserted (CC-02).
- [x] Rollback / migration path recorded (CC-04).
- [x] Traceability links to affected artifacts recorded (CC-05).
- [x] No secret material embedded (SEC-04).
