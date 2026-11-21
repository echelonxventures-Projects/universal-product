# ADR-0003: Constitutional binding of UCOS-CEU-001 and UCXI-000001

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-08-21 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | UCKP-ART-02, UCKP-ART-04, UCKP-ART-07, UCKP-ART-13, UCKP-ART-18, CAA-INV-05, CAA-INV-07 |
| Supersedes | none |

## Context

Two substrates the repository already runs on were absent from `constitutional-authority-alignment.json`. `engine/ceu/` has been the existence substrate since `engine/nucleus/authority.py` resolved a prior duplicate ownership in its favour; `engine/context/` has carried the twelve-law Context Constitution. Neither carried a declaration artifact, so the instrument answering *what may exist* was the one instrument no gate could distinguish from an authority nobody vetted.

CAA-INV-05 permits exactly one owner of the relationship model, and CAA-INV-07 requires any instrument declaring object classes to name UCKO as the model it projects. Both are fail-closed. A binding recording CEU as owning relationship *semantics* would have violated them.

## Decision

We recognise both substrates with declaration artifacts and CAA entries under role `PROJECTION`, and we separate **instance** from **model**: CEU owns existence representation including relationship and topology *instances*; UCKP-ART-07 remains the sole owner of relationship semantics; UCKO remains the sole object model, which CEU projects. CEU is additionally recorded as a fourth bounded authority in `existence_resolution`, whose declared model is `MULTIPLE_INDEPENDENT_AUTHORITIES`.

## Consequences

Positive: the two substrates become visible to every gate that reads the alignment register; ownership is unique and explicit. Neutral: both declarations classify UNRESOLVED under the mutation classifier because they fail `engine-consumed` — correct, since they are declarations *about* engines. Reversible: the binding is additive; removing the two entries and two files restores the prior state exactly.

## Compliance

- [x] Non-contradiction with the constitutional/EES corpus asserted (CC-02).
- [x] Rollback / migration path recorded (CC-04).
- [x] Traceability links to affected artifacts recorded (CC-05).
- [x] No secret material embedded (SEC-04).
