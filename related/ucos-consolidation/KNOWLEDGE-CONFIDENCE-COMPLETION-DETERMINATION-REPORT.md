# KNOWLEDGE CONFIDENCE COMPLETION DETERMINATION REPORT

**Checkpoint:** `03179308` (integration/recovery-001), post ADR-0015
**Determination date:** 2026-08-21
**Predecessors:** `PHASE-4-CAPABILITY-GAP-MATRIX.md` (P4-F-003, P4-F-004, P4-F-006, P4-F-009), `adr/0013-universal-persistent-evolutionary-graph-memory.md`, `RELATIONSHIP-TEMPORAL-VALIDITY-DETERMINATION-REPORT.md`
**Authority:** Repository Truth (code, tests, governance registers) — not the ceremonial-document layer.
**Posture:** Investigation and additive implementation. No new knowledge authority, registry, provenance system, confidence engine, or evidence store invented.

---

## 1. Knowledge ownership map

| Concern | Canonical owner | Evidence |
|---|---|---|
| Identity | UKDA — `CanonicalKnowledgeObject` (content-addressed `cko_id`, `content_sha256`) | `engine/knowledge/cko.py:99-128` |
| Provenance | UKIP — `ProvenanceChain`/`ProvenanceLedger` (hash-chained, stage-ordered) | `engine/knowledge/ukip/provenance.py` |
| Evidence | UKIP — `SourceRef` (content-addressed citation) + `CKO.evidence: tuple[str,...]` | `engine/knowledge/ukip/contracts.py`, `cko.py:123` |
| **Confidence** | **UCXI-000001** — `ContextKind.KNOWLEDGE` dimension `confidence`, in `ContextRegistry` | `engine/context/ontology.py:193-198`, `engine/context/registry.py` |
| Context binding (general) | UCXI-000001 — `ContextRegistry`/`ContextRecord` | `engine/context/registry.py:109-445` |
| Lifecycle | UKDA — `Lifecycle` enum + transition graph | `engine/knowledge/model.py:108-183` |
| Evolution history (object identity) | UKDA — `CKO.supersedes`/`superseded_by`; corpus-wide series in `00-BOOK/DATA/id-ledger.json` (identity layer, ADR-0013) | `cko.py:116-117` |
| Certification state | UKIP — `KnowledgeCertificate`, computed over a registry, referenced by `CKO.certification: str \| None` | `engine/knowledge/ukip/certification.py`, `cko.py:124` |

`KnowledgeAuthority` (`engine/knowledge/model.py:73-97`) is a rank-ordered accountability tier (constitutional > architectural > engineering > advisory) — verified **not** a confidence proxy; it answers "who is accountable," a distinct concern from "how strongly is this held."

## 2. Determination: confidence is **(B) — represented through existing epistemic state**, not missing

`engine/context/ontology.py:193-198` already declares the `KNOWLEDGE` context kind with three *required* dimensions: `source`, `provenance`, `confidence` — asserted together, not confidence in isolation. `engine/context/registry.py`'s `ContextRegistry` is a real, working, append-only, hash-chain-audited registration authority for exactly this shape — supersession, lifecycle, and Context Once (no silent duplicate) are already enforced there. Before this change, `grep -rln "engine.context" engine/knowledge/` returned nothing: zero call sites. This is architecturally identical to Task 2's finding for relationship temporal validity — a correct, complete, working owner-mechanism with no integration — except the owner here is UCXI (context), not CMG-000002 (temporal).

No knowledge object (`CanonicalKnowledgeObject`, `RegisteredKnowledge`, `KnowledgeUnit`) carries a bare `confidence` field, and none was added — P4-F-003's literal wording ("no confidence field on any knowledge object") is true and stays true by design: confidence is not knowledge-object *identity*, it is a *context binding about* a knowledge object, owned by UCXI, exactly as the ontology already models it.

## 3. Minimal change implemented

New module `engine/knowledge/ukip/confidence.py` (UKIP Part 13) — pure integration, no new state model:

- `confidence_declaration(record, *, confidence, ...)` builds a `ContextDeclaration(kind=ContextKind.KNOWLEDGE, ...)` whose `source` and `provenance` dimensions are **projected from the record's own existing** `RegisteredKnowledge.canonical_source` and `.provenance.seal` — not invented. Only `confidence` is a new asserted fact.
- `bind_confidence(context_registry, record, *, confidence)` registers it through the real `ContextRegistry.register()` — Context Once (CXL-06) refuses a silent overwrite if a different confidence is asserted for the same `(knowledge_id, version)`.
- `resupersede_confidence(...)` performs an explicit, append-only correction via `ContextRegistry.supersede()` — the predecessor is retained and marked superseded, never deleted.
- `confidence_of(...)` / `confidence_history(...)` — point lookup and full temporal reconstruction (ordered by the registry's own hash-chained audit sequence, never a clock).

Binding to `(knowledge_id, version)` — not `knowledge_id` alone — means a new version of a knowledge object gets its own confidence context by construction, and reassessing confidence for the *same* version is a deliberate act through `resupersede_confidence`, never a silent overwrite.

**Deliberately not done, and why:**
- **No field added to `CanonicalKnowledgeObject`.** Embedding confidence in `CKO._core()` would change every existing CKO's `content_sha256` and would create a second representation of something UCXI already fully owns — the CAA-INV-07 invariant ("no instrument declares a rival object model") is exactly what this would risk.
- **No `KnowledgeCapability.CONFIDENCE` added** to `engine/knowledge/ukip/constitution.py`'s eleven-member enum. That enumeration reads as a closed, amendment-tier vocabulary in the same style as the Universal Facet Model (`UCRD-001`); adding a member is a larger constitutional action this task does not need to take, since confidence's owner is UCXI, not a twelfth UKIP capability.
- **No persistence store built for `ContextRegistry`.** It has none anywhere in the repository today — confirmed by the same grep that found zero call sites. This is a distinct, deeper, already-disclosed gap: `engine/lineage/memory-layers.json`'s own "context" layer note (companion to P4-F-009) states UCXI "persists NO per-subject context binding." Building that store here would be inventing a capability that belongs to UCXI, the same reasoning Task 2 applied when it refused to build `TemporalCoordinate.from_dict` inside UKIP. It is referred, not repaired.

## 4. Other open findings, re-verified against current code

- **P4-F-004** (`KnowledgeStore.save()`/`replace_object()` — whole-file rewrite, discards the prior version on disk) — **confirmed still true** (`engine/knowledge/store.py:175-180`, `:287-293`). Object-level evolution history (which CKO superseded which) remains representable through `CKO.supersedes`/`superseded_by` and the corpus-wide identity series in `00-BOOK/DATA/id-ledger.json` regardless, per ADR-0013's memory projection — but the store's own disk persistence is still destructive. Out of this task's scope: fixing it is a larger, separate change to UKDA's persistence mechanics, not a knowledge-confidence concern, and is left referred.
- **P4-F-006** (provenance/certification chains correct in memory, not persisted repository-wide) — unchanged, unaffected by this work.
- **P4-F-009** — the corpus-placement "context" layer disclosure is unaffected (different context kind, different subject). The narrower claim it also carried — that UCXI has no per-subject binding *at all* — is now partially superseded for the `KNOWLEDGE` kind specifically: a real per-subject binding mechanism is wired and tested as of this change, though still unpersisted to disk (see above).

## 5. Governance requirement

Registered under CEP-002 Article 28 as `adr/0016-uckp-knowledge-confidence-via-ucxi-context.md`, disposition `IMPLEMENTED`, in `00-MASTER/UCDA-000001/ucda-decisions.json`.

## 6. Validation

- `engine/tests/knowledge/ukip/test_confidence.py` — 13 new tests: declaration projection from real source/provenance, bind/query round-trip, Context Once refusal on a differing same-version confidence, explicit append-only correction via `resupersede_confidence` (predecessor retained and marked superseded), audit-chain integrity through a correction, full historical reconstruction ordered by audit sequence, and no cross-subject leakage. All pass.
- Full `engine/tests/knowledge/` + `engine/tests/context/` suites — 884 tests, all pass (no regression to CKO, store, provenance, certification, or the context registry/taxonomy/ontology itself).
- Broader regression (`engine/tests/{knowledge,context,uckp,nucleus,unit}`, `platform/tests/`): 10,397 passed, 3 skipped, 3 failed — the same 3 pre-existing, unrelated failures identified and stash-verified during Task 2 (`test_the_shards_collect_exactly_the_tests_the_whole_suite_collects`, `test_the_uga_gate_enforces_every_alignment_invariant`, `test_the_governance_gate_enforces_every_invariant`), concerning UGA-INV-01/UGA-INV-10 gate findings over CEU/UCXI declaration files and `adr/0003-0006` — none of which this change touches.
