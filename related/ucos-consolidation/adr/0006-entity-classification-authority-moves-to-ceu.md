# ADR-0006: Entity classification authority moves to CEU; enums become projections

| Field | Value |
|-------|-------|
| Status | Proposed |
| Date | 2026-08-21 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | UCKP-ART-02, UCKP-ART-03, UCKP-ART-18, DATA-015, ENG-000 |
| Supersedes | none |

## Context

`data/entity_meta.py` declares `EntityKind` as a closed five-member enumeration — *"An entity is classified by exactly one kind"* — and `data/` never imports `engine.ceu`. It is a second entity model. `platform/portal/contracts.py` declares a second `EntityKind` with seven members. Both are undisclosed to UISD. The `data/` family are read-only projections of the frozen DF-1/DF-2 specification, whose declared change mode is *"append-only / supersession-only; extension is additive-only"*.

## Decision

We move classification **authority** to CEU classification units. The existing enums remain in place as **derived projections** of that authority, so no reference breaks and no knowledge is authored twice (UCKP-ART-03). Migration is additive and supersession-controlled under ENG-000; no frozen artifact is modified in place.

## Consequences

Positive: one entity model repository-wide; the duplicate authority is removed rather than duplicated. Negative: the `data/` layer gains a dependency direction it did not have; this must be introduced without a cycle. Reversible: projections are derived, so reverting restores the enums as authorities.

## Compliance

- [x] Non-contradiction with the constitutional/EES corpus asserted (CC-02).
- [x] Rollback / migration path recorded (CC-04).
- [x] Traceability links to affected artifacts recorded (CC-05).
- [x] No secret material embedded (SEC-04).
