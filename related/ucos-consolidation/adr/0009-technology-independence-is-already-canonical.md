# ADR-0009: Technology independence is represented by existing canonical capability

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-08-21 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | UCKP-ART-10, UCKP-ART-17, UCKP-ART-20, DATA UDL-15 |
| Supersedes | none |

## Context

The principle requires that no architecture depend on a specific programming language, database, cloud, runtime or infrastructure. Measured: `KNOWN_EXECUTION_KINDS` is documented *"open by registration (Article 17)"*, contains `FUTURE_LANGUAGE`, `FUTURE_COMPUTE`, `AI_AGENT` and `QUANTUM`, and is consumed to **generate** capability projections, never to reject. `data/band10.py:_TECH_MARKERS` **rejects** 28 vendor names fail-closed under UDL-15. Zero hardcoded human languages, currencies or units exist in the scanned surface.

## Decision

We record technology independence as **represented by existing canonical capability**. No new mechanism is created. Technology is Capability Entity + Technology Entity + implementation relationship + evolution history, which the existing execution and capability modules already provide.

## Consequences

Positive: no work is registered for a property already held, and the evidence is named so a future gate can re-measure it. Neutral: the one residual planetary default is handled separately by ADR-0012.

## Compliance

- [x] Non-contradiction with the constitutional/EES corpus asserted (CC-02).
- [x] Rollback / migration path recorded (CC-04).
- [x] Traceability links to affected artifacts recorded (CC-05).
- [x] No secret material embedded (SEC-04).
