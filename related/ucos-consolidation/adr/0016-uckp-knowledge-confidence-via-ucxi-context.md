# ADR-0016: Knowledge confidence is a UCXI context binding, not a new knowledge field

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-08-21 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | UKDA, UKIP, UCXI-000001, UCI-001 XVI.5 |
| Supersedes | none |

## Context

`PHASE-4-CAPABILITY-GAP-MATRIX.md` records `P4-F-003`, owner `UKDA / UKIP`: *"No `confidence` field on any knowledge object (§4)."* `KNOWLEDGE-CONFIDENCE-COMPLETION-DETERMINATION-REPORT.md` (same checkpoint) is the investigation this decision is built on, following the same method Task 2 used for relationship temporal validity (ADR-0015): locate the canonical owner before writing any code.

The determination: no knowledge object carries a confidence field, and none should — `engine/context/ontology.py:193-198` already declares the `KNOWLEDGE` context kind with three required dimensions, `source`, `provenance` and `confidence`, asserted together. `engine/context/registry.py`'s `ContextRegistry` is a real, complete, append-only, audited registration authority for exactly that shape, with supersession and Context Once already enforced. It had zero call sites anywhere in `engine/knowledge/` before this change — the identical shape of gap Task 2 found in `engine/temporal`, this time owned by UCXI-000001 rather than CMG-000002.

`KnowledgeAuthority` was checked and confirmed **not** a confidence proxy: it is a rank-ordered accountability tier (who is responsible), a distinct concern from epistemic strength (how strongly the claim is held).

Temporal note: this decision is anchored to `git HEAD = 03179308` (post ADR-0015) under reference system `logical:git-commit-order@ucos-consolidation`. No wall clock is read anywhere in this change.

## Decision

We add `engine/knowledge/ukip/confidence.py` (UKIP Part 13) as a pure integration layer: it projects a `RegisteredKnowledge`'s own existing `canonical_source` and `provenance.seal` into UCXI's `KNOWLEDGE` context shape, and lets a caller assert the `confidence` dimension alongside them through `ContextRegistry.register()`. Binding is keyed to `(knowledge_id, version)`, so a knowledge revision gets its own confidence context by construction, and correcting confidence for the same version goes through an explicit `resupersede_confidence()` — an append-only correction, never a silent overwrite; `ContextRegistry`'s own Context Once rule (CXL-06) refuses the silent case for us.

We **refuse** to:
- add a `confidence` field to `CanonicalKnowledgeObject`'s content-addressed core — that would change every existing CKO's `content_sha256` and duplicate a representation UCXI already owns (risking CAA-INV-07, "no instrument declares a rival object model"),
- add a twelfth member to `KnowledgeCapability` (`engine/knowledge/ukip/constitution.py`) — that enum reads as closed/amendment-tier in the same style as the Universal Facet Model, and confidence's owner is UCXI, not a new UKIP capability,
- build a persistence store for `ContextRegistry`. None exists anywhere in the repository today (confirmed by the same call-site search that found the integration gap). This is a separate, deeper, already-disclosed gap — `engine/lineage/memory-layers.json`'s "context" layer note, companion to `P4-F-009`, already states UCXI persists no per-subject context binding. Building that store here would be inventing UCXI's capability inside UKIP, the same reasoning ADR-0015 applied to `TemporalCoordinate.from_dict`. Referred, not repaired.

## Consequences

Positive: a knowledge object's confidence is now representable, queryable, correctable (append-only), and historically reconstructible (`confidence_history`, ordered by the registry's own audit sequence) — without a new store, field, or authority. The same mechanism that already governs every other UCXI context — taxonomy conformance, ontology shape validation, Context Once, hash-chained audit — governs this one too, for free.

Neutral: `CanonicalKnowledgeObject.content_sha256` is unaffected by any confidence assertion; existing CKOs, their hashes, and every caller that reads them are untouched.

Negative: confidence bindings live only in the `ContextRegistry` instance a caller supplies, which is not persisted to disk anywhere yet. This is disclosed, not hidden, and matches the existing disclosed state of every other UCXI context binding.

Reversible: `engine/knowledge/ukip/confidence.py` is additive and calls only public methods of `ContextRegistry`; deleting it removes a way of asking a question about confidence and changes no other owner's data.

## Compliance

- [x] Non-contradiction with the constitutional/EES corpus asserted (CC-02) — no other owner's module was modified; UCXI's `ContextRegistry` was consumed, not re-implemented; `KnowledgeCapability` was not amended.
- [x] Rollback / migration path recorded (CC-04) — see Consequences; the module is additive and self-contained.
- [x] Traceability links to affected artifacts recorded (CC-05) — `KNOWLEDGE-CONFIDENCE-COMPLETION-DETERMINATION-REPORT.md`, `PHASE-4-CAPABILITY-GAP-MATRIX.md` (P4-F-003), `engine/knowledge/ukip/confidence.py`, `engine/tests/knowledge/ukip/test_confidence.py`.
- [x] No secret material embedded (SEC-04).
