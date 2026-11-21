# ADR-0023: CEU supersession history becomes append-only, not mutated in place

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-08-21 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | `adr/0019-residual-phase4-finding-disposition.md` (`WP-UCDA-028`), `P4-F-001` |
| Supersedes | none — discharges one of `WP-UCDA-028`'s six independent sub-obligations, per that work package's own stated route: *"Each of the six obligations is independent and may be executed as its own decision at the granularity `ADR-0015`/`0016` used, rather than as one bundled change."* |

## Context

`P4-F-001` (owner CEU-001): `ExistenceRegistry._supersessions` was a `dict[str, dict]` — one mutable slot per subject. `resurrect()` mutated the same dict object in place (`engine/ceu/existence.py:527-535` at the time of discovery), so the record's field values immediately after `supersede()` and before `resurrect()` were unrecoverable — only a hash of the post-mutation state survived in the audit journal. Existing tests confirmed the *action sequence* (`register → supersede → resurrect`) was preserved while the *field-level content* at each step was not — matching `P4-F-001`'s finding exactly, not a stale claim.

This session's Phase 1 discovery (prior turn) determined the minimal fix: widen the container to `dict[str, list[dict]]`, append-only, mirroring two patterns already proven this session — Task 2's non-overlapping-coexistence design for relationship validity windows, and `ContextRegistry`'s replace-not-mutate discipline for context supersession.

## Decision

We **implement** the append-only widening: `_supersessions: dict[str, list[dict[str, Any]]]`. `supersede()` and `resurrect()` each append a new, complete snapshot rather than mutating the sole prior entry. Read paths (`is_superseded()`, `successors_of()`, `supersessions()`) are unchanged in their external contract — each still reports the *current* state, now read as the *last* element of a list rather than the sole dict. A new accessor, `supersession_history(universal_id)`, returns the full sequence. `to_document()` gains an additive `supersession_history` field (a per-subject full history) alongside the unchanged `supersessions` field (current-state summaries only), so the fix survives serialization — `from_document()` rehydrates the full history when present, and falls back to treating an older document's single-entry `supersessions` as a one-record history for backward compatibility.

We **refuse** to build a new audit mechanism — the existing hash-chained `AuditEntry` journal (`ACTION_SUPERSEDE`/`ACTION_RESURRECT`) is unchanged and untouched; only the per-subject state container changed shape.

## Consequences

Positive: field-level supersession/resurrection history is now genuinely reconstructible, not merely hash-provable. `supersession_history()` gives direct access; `to_document()`/`from_document()` round-trip it exactly (verified: `reconstruct()`'s strict digest-equality check, which compares full serialized documents, still passes).

Neutral: `supersessions()`'s external contract (current-state, one row per subject) is completely unchanged — every existing caller and test continues to see identical behavior.

Negative: none identified — the change is strictly additive to what's observable; nothing that previously worked now returns different data for the same query.

Reversible: `git diff engine/ceu/existence.py`; the change is confined to one file, no schema elsewhere depends on the new field, and the old dict-shape read path is not referenced anywhere else in the codebase (confirmed by grep before implementation).

## Compliance

- [x] Non-contradiction with the constitutional/EES corpus asserted (CC-02) — no new authority, no new journal mechanism; CEU-001 remains sole owner.
- [x] Rollback / migration path recorded (CC-04) — see Consequences.
- [x] Traceability links to affected artifacts recorded (CC-05) — `adr/0019`, `engine/ceu/existence.py`, `engine/tests/ceu/test_existence.py`.
- [x] No secret material embedded (SEC-04).

## Validation evidence

- `engine/tests/ceu/test_existence.py` — 53 tests (4 new: `test_resurrection_preserves_the_pre_resurrection_field_values`, `test_a_split_supersede_and_resurrect_cycle_is_fully_reconstructible`, `test_supersession_history_survives_reconstruction`, plus the pre-existing 50), all passing.
- `engine/tests/ceu/` full directory — 267 tests, all passing (no regression).
- `engine/tests/{ceu,nucleus,context,expansion}/` — 867 tests, all passing (no regression to any consumer of `ExistenceRegistry`).
- Strict digest-equality reconstruction (`reconstruct()`, `test_supersession_and_resurrection_survive_reconstruction`, `test_supersession_history_survives_reconstruction`) — confirmed passing, proving `to_document()`'s new field round-trips exactly through `from_document()`.
