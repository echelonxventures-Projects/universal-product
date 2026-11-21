# ADR-0005: Measurement enters as a UCXI context kind and CEU entities

| Field | Value |
|-------|-------|
| Status | Proposed |
| Date | 2026-08-21 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | UCXI CXL-02, CXL-10, UCKP-ART-02, UCKP-ART-18 |
| Supersedes | none |

## Context

Fifteen of sixteen universal context kinds exist; `MEASUREMENT` is absent. `measurement` and `scale` are already CEU bootstrap forms, but no unit, dimension or conversion population exists. No `Unit`, `Measure`, `Quantity` or `Dimension` class exists anywhere in the engine, and no SI or ISO-4217 literal appears in engine code.

## Decision

We admit `MEASUREMENT` as the sixteenth context kind through `ContextTaxonomy.extend()` — a data edit under CXL-02, never a call-site invention. Measurement systems, units, dimensions and scales are registered as `ExistenceUnit`s; conversions are relationship instances. **No measurement engine and no measurement authority is created.** No system is privileged: SI, imperial and any future or non-human system are peer entities.

## Consequences

Positive: unit-bearing artifact fields can resolve through a Measurement Context identity rather than a literal. Neutral: CXL-10 bounds the context — it describes, never grants. Reversible: the taxonomy extension returns a new immutable taxonomy; the entity population is append-only and supersedable.

## Compliance

- [x] Non-contradiction with the constitutional/EES corpus asserted (CC-02).
- [x] Rollback / migration path recorded (CC-04).
- [x] Traceability links to affected artifacts recorded (CC-05).
- [x] No secret material embedded (SEC-04).
