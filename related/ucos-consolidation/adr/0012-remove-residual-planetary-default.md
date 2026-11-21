# ADR-0012: Remove the residual planetary default from cloud persistence

| Field | Value |
|-------|-------|
| Status | Proposed |
| Date | 2026-08-21 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | UCKP-ART-04, UCKP-ART-09, UCKP-ART-20 |
| Supersedes | none |

## Context

A repository-wide scan of `engine/`, `platform/`, `intelligence/` and `data/` found exactly one genuine hardcoded finite assumption: `engine/uckp/persistence.py:479`, `CloudPersistence.__init__(self, base, region: str = "planet-earth-1")`. Every other location hit is either an anti-Earth-coupling gate, the temporal package's refusal text, or governed build-determinism normalization. UCKP-ART-20 states the law remains valid across *"planetary locations and civilizations"*.

## Decision

We remove the planetary literal as a default. Region becomes a required or context-resolved value, so location is data supplied by the caller rather than an architectural assumption baked into a signature.

## Consequences

Positive: the last hardcoded reality assumption in the scanned surface is removed. Negative: callers relying on the implicit default must supply a region; the constructor is referenced nowhere else in the tree, so the blast radius is the adapter itself. Reversible: a one-line change.

## Compliance

- [x] Non-contradiction with the constitutional/EES corpus asserted (CC-02).
- [x] Rollback / migration path recorded (CC-04).
- [x] Traceability links to affected artifacts recorded (CC-05).
- [x] No secret material embedded (SEC-04).
