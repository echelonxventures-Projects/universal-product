# ADR-0013: Memory is a substrate property resolved by projection, not a memory engine

| Field | Value |
|-------|-------|
| Status | Proposed |
| Date | 2026-08-21 |
| Deciders | Constitutional Authority · UCOS Ω∞ |
| Technology Constitution refs | UCKP-ART-07, UCKP-ART-14, UCI-001 XVI.5, CEU-001, UCDA-000001 |
| Supersedes | none |

## Context

Ten memory capabilities were measured against located owners before anything was built (`PHASE-4-CAPABILITY-GAP-MATRIX.md`). Every one has an owner, and every owner already records history:

- **Entity** — `ExistenceRegistry` carries identity, supersession, resurrection, ancestry and a hash-chained append-only journal (`engine/ceu/existence.py:453-582`, `:672-706`).
- **Evolution** — the Article 14 `EvolutionLedger` enforces stage order and verifies append-only-ness on read (`engine/uckp/evolution.py:188-224`, `:266-303`), persisted as 780 records across 52 cycles and 572 subjects (`00-MASTER/UAUE-000001/UAUE-EVOLUTION-HISTORY.json`).
- **Knowledge** — UKIP provenance is tamper-evident and hash-chained (`engine/knowledge/ukip/provenance.py:1-70`); 142 canonical objects are persisted.
- **Decision** — 123 decisions under a nine-stage lifecycle with a fail-closed gate (`00-MASTER/UCDA-000001/`).
- **Temporal** — a coordinate model that requires a `system_identifier`, admits `SystemType.UNKNOWN`, returns `Ordering.INCOMPARABLE`, and deliberately implements no clock read (`engine/temporal/coordinate.py:28-332`, `operations.py:1-15`).

**Zero of the ten justify CREATE.** The measured gap is not absent memory. It is that **no canonical entity can resolve its own memory across those owners.** `engine/lineage/query.py` answers six questions, but only over artifacts and only from six corpus registers; it cannot reach context, knowledge, evidence, decision or evolution memory. `id-ledger.json` holds a real per-entity version series for 1,264 entities and only element `[0]` is ever read (`engine/lineage/query.py:86-89`).

Temporal note: this decision is anchored to `git HEAD = 7b7d0fd9` under reference system `logical:git-commit-order@ucos-consolidation`. The `Date` row above is a repository-local convenience, not an authority. No planetary, calendar or civilizational frame is asserted, per `engine/temporal/coordinate.py`.

## Decision

Memory is a **substrate property**, resolved by extending the Universal Lineage Projection (`engine/lineage/`) with a seven-layer resolution surface: **identity → context → relationship → knowledge → evidence → decision → evolution**.

We **refuse** to create a memory engine, a graph memory database, a knowledge memory authority or a history authority. A new `engine/memory/` package would be exactly the prohibited engine. `engine/lineage/` already carries the required discipline, citing `UCI-001 Part XVI.5`: *"lineage and evolution are DERIVED projections over recorded history; no new store is created."*

The extension therefore:

1. **Owns nothing it reports.** Every layer names its located owner and cites the governed record each value came from. A value that cannot name its source is not returned.
2. **Creates no store**, mints no identifier, opens no counter and declares no relation.
3. **Declares the layer set as DATA** in `engine/lineage/memory-layers.json`, per ADR-0007, so a future memory layer requires no code change.
4. **Is open-world.** An unknown subject resolves to empty layers marked `recorded: false` — never an error, never a guess.
5. **Keeps the graph a projection of canonical truth, never the source of truth.**
6. **Is append-only in what it reports**: supersession, evolution, lineage and resurrection are surfaced; nothing is presented as deleted.
7. **Reads no clock**, so a resolution is replayable.

Findings that would require amending another owner are **referred, not repaired** — `P4-F-001` through `P4-F-008` in the gap matrix, including the absence of relationship temporal validity (UCKP ART-07), the absence of knowledge confidence (UKDA/UKIP), and the in-place mutation of `_supersessions` (CEU-001).

## Consequences

Positive: any canonical entity becomes able to resolve its full memory across seven owners through one surface, and the openness of that surface is measurable. Neutral: no owner is amended, no authority is created, and no existing gate changes verdict — the extension is additive and derived. Negative: the resolution is only as complete as its owners' records, so layers that owners do not yet persist resolve empty; this is disclosed per layer rather than hidden behind a default. Reversible: deleting the extension removes a way of asking a question and changes no answer the repository already holds.

## Compliance

- [x] Non-contradiction with the constitutional/EES corpus asserted (CC-02).
- [x] Rollback / migration path recorded (CC-04).
- [x] Traceability links to affected artifacts recorded (CC-05).
- [x] No secret material embedded (SEC-04).
