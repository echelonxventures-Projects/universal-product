# ADR-0015: UCKP-ART-07 relationships carry validity by consuming the existing temporal type, not a new one

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-08-21 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | UCKP-ART-07, CMG-000002, UCI-001 XVI.5 |
| Supersedes | none |

## Context

`PHASE-4-CAPABILITY-GAP-MATRIX.md` records `P4-F-002`, owner `UCKP ART-07`: *"No relationship representation carries temporal validity, version or supersession (§3)."* ADR-0013 (`03179308`) lists this among findings "referred, not repaired" when the memory-projection extension was built — the finding was located, attributed to its owner, and deliberately left for that owner to act on rather than fixed out-of-authority.

This decision is that owner acting on it. `RELATIONSHIP-TEMPORAL-VALIDITY-DETERMINATION-REPORT.md` (same checkpoint) is the investigation this decision is built on. Its determination: the (source, target, relation) triple in `engine/knowledge/ukip/relationships.py` genuinely carried only one active identity — verified at the actual collapse point in `RelationshipSet.__init__`, not inferred from documentation — and no existing mechanism already solved it. `data/relationship.py`'s content-addressed `version`/`supersedes` chain is a related but distinct capability over a different object. `engine/temporal/` (CMG-000002), however, already provides `ValidityPeriod` and a `compare()` operation that fails closed (`Ordering.INCOMPARABLE`) across reference systems rather than assuming one timeline — and it had no call site anywhere in the repository (the companion finding `P4-F-007`). The gap was real (option A of the investigation's critical question) but the correct remedy was integration with an existing owner's primitive, not invention of a new one (option B), and no capability already closed it end-to-end (not option C).

Temporal note: this decision is anchored to `git HEAD = 03179308` under reference system `logical:git-commit-order@ucos-consolidation`, consistent with ADR-0013's precedent. No wall clock is read anywhere in this change.

## Decision

We extend `RelationDeclaration` (`engine/knowledge/ukip/contracts.py`) and `Relationship`/`RelationshipSet` (`engine/knowledge/ukip/relationships.py`) with an optional `validity: ValidityPeriod | None` field, sourced from `engine.temporal.coordinate.ValidityPeriod` — the canonical type, unmodified. `None` is timeless and is the default, so every existing caller is unaffected.

`RelationshipSet` no longer keeps a single winner per `(source, target, relation)` key unconditionally. Two relationships at that key coexist unless their validity windows are *provably* overlapping (via `compare()`); an incomparable pair — no shared reference system, no declared conversion — is left as two coexisting instances rather than guessed into one. Within a provable overlap, an asserted relationship still beats a derived one, exactly as before this field existed. A new `valid_at(coordinate)` method reconstructs the historical subgraph.

We **refuse** to:
- add a bespoke discriminator field unrelated to `engine/temporal`'s model,
- create a second relationship store or a parallel version table,
- give `data/relationship.py` and `engine/knowledge/ukip/relationships.py` a shared identity — they answer different questions and stay two located owners, per §1 of the determination report,
- build `ValidityPeriod.from_dict`/`TemporalCoordinate.from_dict` inside this module. `RelationDeclaration.from_dict()` fails closed (raises) when a raw record carries a non-null `validity`, because that reconstruction is CMG-000002's capability to add, not UCKP-ART-07's. This is recorded as a referred gap, the same way P4-F-007 was referred to this owner.

## Consequences

Positive: the same relationship triple can now hold a validity-bounded series — creation, a later supersession, a later resurrection, and an open-ended future version are all representable and queryable (`valid_at`) without a new store. `RelationshipSet.compose()` and `.seal()` were corrected in the same change so a temporal series is not silently collapsed to one member during composition or content sealing — both were latent defects the field would otherwise have introduced.

Neutral: `Relationship.key()` keeps its pre-existing meaning (navigational grouping); the new `identity()` method is additive and used only where per-instance uniqueness matters (dedup, seal, composition bookkeeping).

Negative: relationships declared through the raw-dict wire format (`RelationDeclaration.from_dict`) cannot yet carry a validity period — only programmatic construction can — until `engine/temporal` publishes its own deserialization. This is disclosed, not hidden.

Reversible: the field is optional and additive; removing it returns every caller to its pre-existing behavior, since `validity=None` already reproduces it exactly.

## Compliance

- [x] Non-contradiction with the constitutional/EES corpus asserted (CC-02) — no other owner's module was modified; `engine/temporal` was consumed, not re-implemented.
- [x] Rollback / migration path recorded (CC-04) — see Consequences; the field is optional and additive.
- [x] Traceability links to affected artifacts recorded (CC-05) — `RELATIONSHIP-TEMPORAL-VALIDITY-DETERMINATION-REPORT.md`, `PHASE-4-CAPABILITY-GAP-MATRIX.md` (P4-F-002), `engine/knowledge/ukip/contracts.py`, `engine/knowledge/ukip/relationships.py`, `engine/tests/knowledge/ukip/test_relationships.py`.
- [x] No secret material embedded (SEC-04).
