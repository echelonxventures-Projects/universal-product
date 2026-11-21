# ADR-0025: KnowledgeStore archives replaced versions and persists provenance chains

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | 2026-08-21 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | `adr/0019-residual-phase4-finding-disposition.md` (`WP-UCDA-028`), `P4-F-004`, `P4-F-006` |
| Supersedes | none — discharges two more of `WP-UCDA-028`'s six independent sub-obligations |

## Context

`P4-F-004` (UKDA): `KnowledgeStore.save()` fully overwrote `canonical-knowledge.json` on every call, and `KnowledgeBase.replace_object()` dropped the prior same-id object from the returned base — no recovery path existed anywhere (checked directly this session: `id-ledger.json` indexes file *paths*, not `cko_id`; the memory-projection knowledge layer reads the same file `save()` overwrites).

`P4-F-006` (UKIP): `ProvenanceChain` fully round-trips via `to_dict()`/`from_dict()` and hash-verifies, but is never written to disk anywhere — `RegisteredKnowledge` (which carries `.provenance`) is a pure runtime construct.

**A real constraint found during this implementation, not assumed from the prior discovery:** `KnowledgeBase.replace_object()` has three live, non-test callers (`engine/runtime/bridge/bridge.py:368,551`, `engine/knowledge/integration/pipeline.py:153`), all using the identical `if has_object(id): replace_object(obj) else: with_object(obj)` same-identity upsert idiom. Routing replacement through `supersedes`/`superseded_by` (minting a new `cko_id` per version, as the original discovery proposed) would have broken this real, load-bearing pattern — those callers legitimately re-record the *same* identity's updated state, not a new knowledge assertion superseding an old one. The fix therefore moved to the persistence boundary instead, where it addresses `P4-F-004`'s actual wording ("`KnowledgeStore.save()` is a whole-file rewrite") precisely, without touching `KnowledgeBase`'s in-memory contract at all.

## Decision

We **implement**, in `engine/knowledge/store.py`:

1. `KnowledgeStore.save()` now calls `_archive_replaced_versions(base)` before writing `CANON_FILE`. For every object already on disk whose `content_sha256` is about to change (including one dropped from `base` entirely), the prior record is appended to a new sibling file, `canonical-knowledge-history.json`, keyed by `cko_id`. The live `CANON_FILE` is unaffected — it still reflects current state only, exactly as `KnowledgeBase.replace_object()`'s three real callers already depend on.
2. `KnowledgeStore.history(cko_id)` reads that file back as a tuple of `CanonicalKnowledgeObject`, oldest first — empty, not an error, when nothing was ever archived (matching the store's existing fail-soft discipline for `DECISIONS_FILE`).
3. `KnowledgeStore.save_provenance(chains)` / `.load_provenance()` persist `ProvenanceChain` instances to a second new sibling file, `provenance.json`, keyed by each chain's own `subject` field.

We **refuse** to embed either into `CanonicalKnowledgeObject`'s content-addressed core (`cko.py`'s `_core()`): doing so would change every existing CKO's `content_sha256` and duplicate a representation UKIP already owns — the identical reasoning `ADR-0016` applied to knowledge confidence. Both new files reuse `KnowledgeStore`'s existing `_guard_writable()`/`_write_json()`/`_read_json()` machinery — no new store, no new authority.

**A circular import was found and fixed during implementation**, not before: `engine.knowledge.ukip`'s package `__init__` eagerly imports `assimilation.py`, which imports `engine.knowledge.store` — so a module-level `from engine.knowledge.ukip.provenance import ProvenanceChain` in `store.py` failed at import time. `ProvenanceChain` is imported under `TYPE_CHECKING` for the type hints (safe under `from __future__ import annotations`) and locally, inside `load_provenance()`, at call time.

## Consequences

Positive: a knowledge object's prior versions are now recoverable via `history()`, and provenance chains persist across a process restart, closing the two named findings. Neither change altered any existing method's external contract — `replace_object()`, `save()`, and `load()` behave identically to every existing caller.

Neutral: two new files appear in the knowledge store directory only once something is actually archived or provenance is actually saved — an unused store gains nothing new on disk.

Negative: none identified for the implemented scope. The broader "storage-technology abstraction" (`REQ-43`) remains a separate, larger, not-yet-implemented item — this decision does not claim to close it.

Reversible: both additions are new files plus new methods; deleting `_archive_replaced_versions`'s call site and the two provenance methods fully reverts to prior behavior, and no other code depends on either new file existing.

## Compliance

- [x] Non-contradiction with the constitutional/EES corpus asserted (CC-02) — no new authority; UKDA remains sole owner of `KnowledgeStore`.
- [x] Rollback / migration path recorded (CC-04) — see Consequences.
- [x] Traceability links to affected artifacts recorded (CC-05) — `adr/0019`, `engine/knowledge/store.py`, `engine/tests/knowledge/test_store.py`.
- [x] No secret material embedded (SEC-04).

## Validation evidence

- `engine/tests/knowledge/test_store.py` — 21 tests (10 new: archive-on-change, no-archive-when-unchanged, archive-on-drop, multi-save accumulation, empty-history cases, provenance round-trip, provenance isolation from canon/history files, frozen-corpus refusal for provenance writes), all passing.
- `engine/tests/knowledge/` full directory — 618 tests, no regression.
- The three real `replace_object()` callers' own test files (`test_runtime_bridge.py` ×2, `test_pipeline.py`) — 40 tests, no regression, confirming the same-identity upsert idiom is unaffected.
- Circular import confirmed fixed: `from engine.knowledge.store import KnowledgeStore, KnowledgeBase` succeeds standalone.
