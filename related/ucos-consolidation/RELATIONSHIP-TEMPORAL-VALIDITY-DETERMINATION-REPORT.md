# RELATIONSHIP TEMPORAL VALIDITY DETERMINATION REPORT

**Checkpoint:** `03179308` (integration/recovery-001)
**Determination date:** 2026-08-21
**Predecessors:** `PHASE-4-CAPABILITY-GAP-MATRIX.md` (P4-F-002), `adr/0013-universal-persistent-evolutionary-graph-memory.md`, `UCRD-001-CONSTITUTIONAL-RELATIONSHIP-DETERMINATION.md`
**Authority:** Repository Truth (code, tests, governance registers) — not the ceremonial-document layer.
**Posture:** Investigation and additive implementation. No new register, store, authority, or discriminator invented.

---

## 1. Current relationship ownership map

| Layer | Owner | Evidence |
|---|---|---|
| Existence of an entity | `CEU-001` (`ExistenceRegistry`) | `engine/ceu/existence.py:453-582` |
| Relationship semantics (UCKP-ART-07) | `engine/uckp/law.py:250-257` (article text) realized by two concrete models: | |
| — content-addressed relationship object, forward-only version chain | `data/relationship.py` `RelationshipObject` (DMC-04) | `data/relationship.py:239-373` |
| — provider-declared, resolved, symmetrically-closed knowledge graph | `engine/knowledge/ukip/relationships.py` `Relationship` / `RelationshipSet` (UKIP Part 07) | this file |
| Generic temporal coordinate/interval model | `engine/temporal/` (CMG-000002) | `coordinate.py`, `operations.py` — real, working, previously orphaned (P4-F-007) |
| Evolution/lineage projection (derived, not a store) | `engine/lineage/`, extended by ADR-0013 | `adr/0013-...md` |

Neither `data/relationship.py` nor `engine/knowledge/ukip/relationships.py` is a duplicate of the other: the former is a content-addressed object with its own version/supersedes chain (a different concern — object identity across edits), the latter is the *derived closure* computed from provider declarations that answers graph-navigation questions ("what does A depend on"). UCKP-ART-07 is realized by the second. The source of truth for a relationship is a provider's `RelationDeclaration` (`engine/knowledge/ukip/contracts.py:190-208`, prior to this change); `RelationshipSet` is a projection over it, consistent with ADR-0013's rule that "the graph is a projection of canonical truth, never the source of truth."

## 2. Existing capabilities (before this change)

| Requirement | Status | Evidence |
|---|---|---|
| Creation | ✔ | `build_relationships()` resolves provider declarations into `Relationship` instances |
| Discovery | ✔ | `RelationshipSet.outbound/inbound/neighbours/transitive` |
| Validation | ✔ | `RelationshipSet.cycles()`, `unnavigable()`, dangling-target reporting |
| Context binding | ✔ (elsewhere) | UCXI-000001 owns context; not part of this gap |
| **Validity period** | **✘ absent** | `RelationDeclaration` carried `relation, target, note` only — no temporal field anywhere in the chain |
| **Historical reconstruction** | **✘ absent** | No point-in-time query existed; `RelationshipSet` had exactly one state |
| Supersession | partial | `RelationType.SUPERSEDES` exists as an assertable edge *type*, but nothing recorded *when* one version stopped holding |
| Resurrection | **✘ absent** | Impossible without a validity period — a re-asserted triple silently overwrote, or (for equal derived/asserted status) was indistinguishable from, the prior one |
| Future evolution | ✔ (structurally) | `RelationshipSet` is immutable and rebuilt from source records each time — a new declaration is additive at the source, never a mutation |

This matches the governance record exactly: `PHASE-4-CAPABILITY-GAP-MATRIX.md:171`, finding `P4-F-002`, owner `UCKP ART-07`: *"No relationship representation carries temporal validity, version or supersession (§3)."* `adr/0013` (HEAD at investigation start) lists this among findings "referred, not repaired" — i.e., previously deferred to this owner, not previously solved.

## 3. Was the single-identity-per-triple limit real?

Yes, and it was verified at the actual point of collapse, not inferred from documentation:

`engine/knowledge/ukip/relationships.py` (`RelationshipSet.__init__`, prior version): a `dict[(source, target, relation), Relationship]` kept exactly one winner per key — an asserted relationship replaced a derived one at the same key, but a second assertion of the same triple (e.g. a corrected or time-bounded claim) silently overwrote the first with no record that anything changed. There was no field anywhere upstream (`RelationDeclaration`) capable of expressing "this held from T1 to T2," so the collapse was not a bug in the merge logic — the *representation itself* could not distinguish two points in time.

## 4. Determination: **A + B, not C**

- **A — real limitation, correctly attributed.** `RelationDeclaration` and `Relationship` genuinely had no temporal field. This is not a misconfiguration; the representation was incomplete.
- **B — but the fix is integration, not invention.** `engine/temporal` (CMG-000002) already provides exactly the primitive needed — `ValidityPeriod`, `TemporalCoordinate`, and a `compare()` operation that fails closed (`Ordering.INCOMPARABLE`) rather than guessing across reference systems. It existed and had no call site (P4-F-007's companion finding). UCKP-ART-07 had simply never been wired to it.
- **Not C.** No existing mechanism already solved this for the UKIP relationship model. `data/relationship.py`'s `version`/`supersedes` chain is a related but distinct capability (content-addressed object versioning), and does not, by itself, give the UKIP closure graph a validity period.

No artificial discriminator, duplicate relationship instance store, or parallel database was required or introduced. The fix consumes the one canonical temporal type that already exists.

## 5. Minimal change implemented

1. `engine/knowledge/ukip/contracts.py` — `RelationDeclaration` gained `validity: ValidityPeriod | None = None` (default preserves every existing caller's behavior exactly).
2. `engine/knowledge/ukip/relationships.py`:
   - `Relationship` gained the same `validity` field, plus `identity()` — a per-instance identity (triple + validity marker) distinct from the existing `key()` (which still means "navigational group," unchanged).
   - `RelationshipSet.__init__` now keeps multiple instances per `(source, target, relation)` key when their validity windows do not provably overlap, instead of always keeping one winner. Overlap is decided via the existing `engine.temporal.operations.compare()`; an unproven (cross-system, no declared conversion) pair is treated as **not** overlapping — coexistence, not a guessed collapse, consistent with Law 7.
   - New `RelationshipSet.valid_at(coordinate)` reconstructs the subgraph that held at a given temporal coordinate — historical reconstruction.
   - `compose()` and `seal()` were updated to use `identity()` instead of `key()` internally so a temporal series is not silently collapsed to its last member during composition, and the seal changes when a temporal version is added (both were latent correctness gaps the naive addition of the field would otherwise have introduced).
   - `build_relationships()` threads `declaration.validity` into the constructed `Relationship`.
3. No change to `data/relationship.py`, `engine/uckp/law.py`, or any other owner. No new store, register, or clock read. `ValidityPeriod.since`/`until` still require an explicit reference system per CMG-000002 — nothing here reads a wall clock.

**Deliberately deferred, not repaired:** `RelationDeclaration.from_dict()` refuses (fail-closed, raises `UnitError`) when a raw record carries a non-null `validity`, because `engine.temporal.coordinate.TemporalCoordinate` has no `from_dict` — inventing one here would be building CMG-000002's capability inside UCKP-ART-07's module, which the governance rules for this task expressly prohibit ("do not create a new relationship authority... unless proven necessary"). Programmatic construction (`RelationDeclaration(validity=...)`) is unaffected. This gap is recorded here for the `engine/temporal` owner, the same way P4-F-007 was recorded for this owner.

## 6. Governance requirement

Registered under CEP-002 Article 28 as `adr/0015-uckp-art-07-relationship-temporal-validity.md`, disposition `IMPLEMENTED`, closing `P4-F-002` in `00-MASTER/UCDA-000001/ucda-decisions.json`. See that entry for evidence links.

## 7. Validation

- `engine/tests/knowledge/ukip/test_relationships.py` — 72 tests (11 new, covering: non-overlapping coexistence, overlapping collapse with asserted-beats-derived preserved, timeless backward-compatibility, incomparable-window non-collapse, `valid_at()` point-in-time reconstruction including the half-open boundary, `valid_at()` refusing an incomparable query, `identity()` vs `key()` distinctness, seal sensitivity to a new temporal version, `compose()` preserving every temporal version of the seed set, and validity threading through `build_relationships()`). All pass.
- Full `engine/tests/knowledge/ukip/` suite (345 tests, unrelated to this change) — all pass, confirming no regression to certification, assimilation, graph, evidence, or validation modules that consume `Relationship`/`RelationshipSet`.
- Broader `engine/tests/{knowledge,uckp,nucleus,unit}` and `platform/tests/` run for regression coverage of downstream evolution/lineage consumers — see `adr/0015` evidence for the recorded result.
