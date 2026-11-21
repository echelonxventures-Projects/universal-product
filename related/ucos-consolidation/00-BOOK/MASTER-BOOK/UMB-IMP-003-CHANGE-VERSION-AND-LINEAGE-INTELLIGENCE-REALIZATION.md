# UCOS Ω∞ — UMB-IMP-003 · CHANGE, VERSION, AND LINEAGE INTELLIGENCE REALIZATION

> **STATUS DOMAIN:** IMPLEMENTATION (DOMAIN-C — code that exists and runs)
> **STATUS BASIS:** The realized machinery in `00-BOOK/tools/{config.py,ukb.py}` (append-only ledger snapshot history + metadata-driven change/version/lineage/evolution derivation + `ukb evolve` navigation) and the generated views `00-BOOK/DATA/change-ledger.json` + `00-BOOK/REGISTRIES/CHANGE-VERSION-LINEAGE-REGISTRY.md` — plus live execution this session (full `register.sh` transaction `CERTIFIED (hard checks 7/7)`, `ukb build` emitting change events + version records + lineage chains, `ukb validate` referential integrity OK, `ukbx validate`, `ukb evolve` bidirectional change/version/lineage navigation, idempotent-rebuild proof, scheme-agnostic version proof, and an isolated multi-snapshot derivation test). Evidence only; no projection.

| Field | Value |
|-------|-------|
| ARTIFACT ID | UMB-IMP-003 |
| ARTIFACT | Change, Version, and Lineage Intelligence Realization |
| PROGRAM | UCOS Ω∞ Universal Master Book Architecture Program (UMB) |
| CLASSIFICATION | Implementation Realization — the third operational capability of the UMB architecture: transforming the append-only ledger + typed knowledge graph into a Change / Version / Lineage / Evolution intelligence surface, all metadata-driven and derived |
| STATUS | ACTIVE · IMPLEMENTATION |
| PARENT | UMB-000 |
| DEPENDS-ON | UMB-READINESS-001 (gap source, P3); UMB-IMP-001 (auto-registration); UMB-IMP-002 (typed graph + spine); UMB-008/009/010 (read-only targets); STATUS-001; REG-AUTO-001; UCI-001; AUTH-INF-001; UMB-000 |
| IMPLEMENTS | UMB-008; UMB-009; UMB-010 |
| CONSUMES (read-only) | UMB-000…020; UMB-READINESS-001; UMB-IMP-001; UMB-IMP-002 |
| TRACES-TO | UMB-008 |
| RELATES Evolves-From | UMB-IMP-002 |
| PRODUCES (append-only, machinery — not registered artifacts) | `config.py` UMB-IMP-003 block (version keys, change-event vocabulary, appended lineage relationship types, lineage edge-direction sets); `ukb.py` `read_version()`/`_git_last_commit()`/`record_snapshots()`/`derive_change_events()`/`derive_version_records()`/`derive_lineage()`/`build_change_ledger()`/`write_change_registry()`/`cmd_evolve()` + `cmd_build` snapshot & derivation pass; generated views `DATA/change-ledger.json` + `REGISTRIES/CHANGE-VERSION-LINEAGE-REGISTRY.md` |
| CONSTITUENT / GOVERNANCE / RATIFICATION / EC-1 AUTHORITY | NONE |
| VOLUME | VOL-022 (MASTER BOOK ARCHITECTURE) |
| BASELINE DATE | 2026-07-16 |

*This is an implementation artifact. It realizes — in reusable, standard-library machinery — the single capability UMB-READINESS-001 identified as the next unlock after the typed graph (P3): converting the append-only identity ledger and the typed knowledge graph into a **Change / Version / Lineage / Evolution intelligence surface**, so any artifact automatically participates in change history, version history, lineage chains, evolution timeline, impact analysis, and bidirectional knowledge navigation without manual graph engineering. It creates no new architecture family, no new registry, no new identifier namespace, and no lifecycle; it reuses the existing engines (`ukb.py`, `ukbx.py`), the existing immutable identity ledger (`id-ledger.json`), the existing typed knowledge graph (`relationships.json`), the existing `version`/`content_hash`/`first_seen` fields, and the existing Atomic Registration Transaction (`register.sh`) exclusively. It is append-only and authority-neutral, subordinate to the frozen constitutional corpus, STATUS-001, REG-AUTO-001, UCI-001, AUTH-INF-001, and UMB-000…020; where any statement conflicts with a higher instrument, the higher instrument governs and the statement is void to the extent of the conflict.*

---

## SECTION 1 — IMPLEMENTATION SCOPE

**In scope (realized by this artifact).**
1. **Change Intelligence.** Automatic detection and recording of change events — Created, Modified, Moved, Renamed, Version-Incremented, Deprecated, Superseded, Retired, Restored, Reactivated, and (design) Deletion-Attempted — derived by comparing consecutive append-only snapshots of the same Universal ID, each bound to its subject node (graph-participating) and evidence-bound to the causing git commit when the file is tracked.
2. **Version Intelligence.** Version discovery (scheme-agnostic, self-declared), append-only version history (every prior `version` + `content_hash` preserved), version lineage, and version navigation — with **no hard-coded version format** (semver, calendar, revision, tag, or any future scheme).
3. **Lineage Intelligence.** Automatic construction of bidirectional lineage chains — Created-From, Derived-From, Evolves-From/Evolved-From, Supersedes/Superseded-By, Replaced-By, Forked-From, Merged-Into — as a projection of the one typed graph, navigable backward (to origin/birth) and forward (to every successor).
4. **Evolution Intelligence.** The append-only, ordered evolution timeline — the institutional memory of every state each entity held — enabling determination of *what changed, when, why (git causation), and what is impacted.*
5. **Impact + Knowledge Navigation.** `ukb evolve <id>` navigates from any artifact to its change history, version history, lineage (both directions), evolution path, and change-impact surface (inbound typed edges).

**Out of scope (explicitly not built here; unchanged).** Live connectors + real signals (UMB-012/002), semantic-embedding search (UMB-013), binary publication formats (UMB-011), predictive AI (UMB-014), security-zone enforcement (UMB-015), and regeneration engines (UCI-001 Part XV — derived at request time to existing generators, never a new engine). These remain future work per UMB-READINESS-001 §§6/8 (P2/P4/P5) and are neither claimed nor implied here (STATUS-001 §2 non-projection).

**Governing constraint.** Exactly **one** registered artifact is created by this mission (this document). All executable changes are made to the generator *machinery* under `00-BOOK/tools/` (excluded from registration by `config.py::EXCLUDE_DIR_PREFIXES`). The derived views (`change-ledger.json`, `CHANGE-VERSION-LINEAGE-REGISTRY.md`) are generated outputs under already-excluded `DATA/`/`REGISTRIES/` — no new registered artifact and no new authoritative store.

---

## SECTION 2 — CURRENT-STATE ANALYSIS

Direct inspection + live execution established the pre-implementation state (consistent with UMB-READINESS-001 §2 items UMB-008/009/010, §6 items A.4/B.5, §8 P3):

| Capability | Pre-state | Evidence |
|-----------|-----------|----------|
| Change engine | **ARCHITECTURE ONLY** — no change events, no change command; `ukbx ai change` only bundled existing neighbours | UMB-READINESS-001 §2 (UMB-008) |
| Version history | **PARTIALLY REALIZED (birth-only)** — `content_hash` real in 292/292 but `version` = `1.0.0` in **all** 292; no version history, no supersession, no rollback | `artifacts.json` (`version` histogram = `{1.0.0: 292}`) |
| Prior-hash preservation | **ABSENT** — the ledger recorded `first_seen` per path but **no prior `content_hash`/`version`**, so UMB-009 §2 "preserves every prior content_hash" had no store | `id-ledger.json` (`by_path` entries carry `first_seen` only) |
| Lineage chains | **BIRTH-ONLY** — `first_seen` real; the `Supersedes`/`Evolved-From` edge *vocabulary* existed (UMB-IMP-002) but only **one** live lineage edge (`Evolves-From` UMB-IMP-002→UMB-IMP-001) and **no lineage projection/navigation** | `relationships.json` (`Evolves-From:1`) |
| Evolution timeline | **ABSENT** — no ordered institutional-memory record of state transitions | — |
| Change/version/lineage navigation | **ABSENT** — `ukb trace` showed structural + typed edges + spine, but no change/version/lineage view | `ukb.py::cmd_trace` (pre-state) |

**Proof of the gap (observed live).** At session start `ukb build` emitted 9,482 edges of 12 types with exactly **one** lineage edge; `artifacts.json` carried `version=1.0.0` in every one of the 292 records; and the ledger held no prior `content_hash` — the exact "structural graph, empty change/version/lineage surface" state UMB-READINESS-001 attributes to UMB-008/009/010.

---

## SECTION 3 — REUSE ANALYSIS

Per the mission's "reuse existing registries / identities / graph / traceability structures; do not replace existing mechanisms — extend them," every requirement maps to an existing mechanism; only thin, additive layers were written. No engine was replaced; no registry, identifier namespace, lifecycle, or change/version/lineage store was created (UCI-001 INTEGRATION MODEL / Part XVII.4 preserved; UMB-008 §2/§3, UMB-009 §1, UMB-010 §1).

| Requirement | Reused existing mechanism | Net-new (additive) |
|-------------|---------------------------|--------------------|
| Prior-hash / prior-version preservation | the **immutable identity ledger** `id-ledger.json` (already append-only, already holds `first_seen`, already extended once by UMB-IMP-001 with `discovered_volumes`) | append-only `history` snapshots (`content_hash`/`version`/`status`/`path`/`name` per Universal ID) — **not a new store**, an extension of the existing ledger |
| Change events | comparison of consecutive ledger snapshots + `content_hash` (already computed) | `derive_change_events` (pure projection; UCHG ids bound to subject nodes) |
| Change causation (why/when/who) | **git history** (UMB-009 §2 basis) | `_git_last_commit` best-effort read (evidence-bound; no fabrication) |
| Version model | existing `version` field + `content_hash` + ledger `first_seen` (UMB-009 §2) | `read_version` (scheme-agnostic) + `derive_version_records` (projection) |
| Lineage / evolution | existing **typed graph** `Supersedes`/`Evolved-From` edges + `first_seen` (UMB-010 §2) | `derive_lineage` projection over appended lineage edge types; no lineage store |
| Metadata reading | `ukb.py::read_metadata`/`read_relationship_rows`/`_read_head` (UMB-IMP-001/002) | `read_version` (same front-matter, one more row) |
| Relationship vocabulary | `config.py::RELATIONSHIP_TYPES` open, append-only (UMB-IMP-002) | 6 appended lineage types (Evolves-From/Created-From/Derived-From/Forked-From/Replaced-By/Merged-Into) |
| Registration / synchronization | `register.sh` Atomic Transaction `T` (UMB-IMP-001 gated) | none — reused verbatim; derivation runs inside `ukb build` (Phase 1) |
| Certification | `ukbx twin --check` (C-05 referential, C-07 acyclic, C-08 navigation) | none — reused verbatim as the correctness gate |
| Navigation / impact | `ukb trace`, `ukbx ai impact`, typed inbound edges (UMB-IMP-002) | `ukb evolve` (change/version/lineage/evolution/impact view) |

---

## SECTION 4 — CHANGE INTELLIGENCE DESIGN

Change intelligence is realized as UMB-008 specifies — **derived, not stored** (§3), with each change event a first-class, node-bound, navigable entity (§2) that introduces **no** dangling graph endpoint (UMB-017 C-05 preserved).

**4.1 Append-only snapshot history (the one filled gap).** `record_snapshots` writes, into the existing immutable ledger, a snapshot `{seq, at, content_hash, version, status, path, name}` for a Universal ID **only when it differs** from that ID's last recorded snapshot. This preserves every prior `content_hash` and `version` (UMB-009 §2) as append-only fact — the single missing datum — while remaining idempotent: a no-op rebuild appends nothing. The **first** snapshot is anchored to the ledger's recorded `first_seen`, so the Created event is historically accurate (UMB-010 §2 birth).

**4.2 Change-event derivation (`derive_change_events`).** Consecutive snapshots of the same ID yield events by delta: first snapshot → **Created**; `content_hash` delta → **Modified**; `path` delta → **Moved**; `name` delta → **Renamed**; `version` delta → **Version-Incremented**; transition into `SUPERSEDED`/`RETIRED`/`DEPRECATED` → **Superseded**/**Retired**/**Deprecated**; transition *out* of a terminal status → **Reactivated**/**Restored**. Each event carries evidence: snapshot `seq`, before/after values, and — for Created/Modified/Moved/Renamed — the causing git commit (`_git_last_commit`) when the file is tracked. **Deletion-Attempted** is defined for a previously-registered artifact that disappears from disk (the append-only ledger never deletes its identity).

**4.3 Graph participation without dangling edges.** Every change event is bound to a subject Universal ID (a real node), assigned a deterministic `UCHG-NNNNNNNNN` id by stable `(at, subject, seq, kind)` ordering (stable across rebuilds). It is navigable from its node via `ukb evolve`, satisfying "change events shall become graph-participating entities" **without** writing a non-resolving endpoint into `relationships.json` (which would break C-05). The **four UMB-008 §3 engines** (Change Intelligence, Impact, Dependency, Supersession) are all derived views recomputed on demand.

**4.4 Zero hard coding / infinite expansion.** `config.py::CHANGE_EVENT_TYPES` declares event *kinds* and their *triggers* only — no program, artifact, domain, or format. A future kind is a new append-only entry (AUTH-INF-001 CR-INF-007); unlimited change events accrue with no ceiling (CR-INF-010).

**Live result.** `ukb build` derives **293** change events across the corpus (292 historical `Created` baselines + this artifact's own `Created`), each bound to its node; re-running appends none (idempotent).

---

## SECTION 5 — VERSION INTELLIGENCE DESIGN

Version intelligence is realized exactly as UMB-009 §2 specifies — **version identity is `universal_id` + `version`, derived from existing fields, never a new store** (§1).

**5.1 Scheme-agnostic discovery (`read_version`).** An artifact self-declares its version in front-matter (`VERSION`/`UCOS-VERSION`/`ARTIFACT VERSION`); the token is captured **verbatim** — semver `1.4.2`, calendar `2026.07.16`, revision `REV-C`, tag `v3`, or any future scheme. **No version format is compiled in** (UMB-009 §6; AUTH-INF-001 CR-INF-008). The schema-constrained `artifact.version` field is populated only when the declared token is a valid semver; the raw token is always preserved in the snapshot history, so the version engine supports every existing and future scheme without a schema change.

**5.2 Append-only version history (`derive_version_records`).** From the snapshot history: the ordered list of distinct versions (each with its `content_hash` baseline and timestamp), the current version, the first version, and the version depth — for every artifact. History preserves every prior version and hash (UMB-009 §2); a content change without a new `content_hash` is impossible here because the hash is recomputed each build (CL-04).

**5.3 Version lineage, navigation, certification traceability.** Each version is reverse-traceable to the change that produced it (§4), to its predecessor via the lineage projection (§6), and to its allocation via `first_seen`. `ukb evolve <id>` prints the full version history; certification traceability is the `certification`-lane spine (UMB-IMP-002) composed with the version baseline. **Configuration baseline / drift / rollback** (UMB-009 §3/§4) are realized by the existing pinned-`content_hash` + `register.sh --guard` drift gate and the forward-only supersession model — no config/rollback store is created.

**5.4 Infinite scale.** Unlimited versions per entity; no ceiling on version count or scheme (CR-INF-010).

**Live result.** 293 version records; corpus version depth is 1 (all `1.0.0`, truthfully — no supersession chains exist in the corpus yet), while the engine supports unlimited depth across mixed schemes, proven by the isolated multi-snapshot test (Section 11: `1.0.0 → 1.1.0 → 2026.04-CAL`, depth 3).

---

## SECTION 6 — LINEAGE INTELLIGENCE DESIGN

Lineage is realized as UMB-010 §2 specifies — **identity-anchored and a projection of the one typed graph**, never a new store (§1).

**6.1 Lineage vocabulary (appended, open).** Six lineage relationship types are appended to the open `RELATIONSHIP_TYPES` (Evolves-From, Created-From, Derived-From, Forked-From, Replaced-By, Merged-Into), joining the pre-existing Supersedes/Superseded-By and Evolves-To/Evolved-From. Each materializes a bidirectional inverse, so a chain is navigable regardless of which end declared it (UMB-010 §6). No existing type is modified (append-only; CR-INF-007).

**6.2 Chain construction (`derive_lineage`).** Two config sets — `LINEAGE_ANCESTOR_EDGE_TYPES` (points to a predecessor/origin) and `LINEAGE_DESCENDANT_EDGE_TYPES` (points to a successor/derivative) — tell the engine how to walk the materialized edges. For any artifact it computes: immediate predecessors, immediate successors, the full backward ancestry chain (to `origin`), the full forward descendant chain, and `birth` (first snapshot / `first_seen`). Because identity is stable and never reused, a chain survives renaming, reclassification, relocation, versioning, refactoring, and federation (UMB-010 §2; AUTH-INF-001 CR-INF-005).

**6.3 Bidirectional navigation.** `ukb evolve <id>` prints predecessors, successors, backward ancestry, and forward evolution — the bidirectional lineage guarantee (UMB-010 §6).

**Live result.** This artifact declares `RELATES Evolves-From | UMB-IMP-002`; combined with the pre-existing `Evolves-From` UMB-IMP-002→UMB-IMP-001, registration materializes a real **3-node lineage chain UMB-IMP-003 → UMB-IMP-002 → UMB-IMP-001**, backward-navigable to origin `UMB-IMP-001` and forward-navigable from it — with zero manual graph engineering.

---

## SECTION 7 — EVOLUTION INTELLIGENCE DESIGN

The Universal Evolution surface (UMB-010 §3) is the **append-only, ordered union of every change event** — the permanent institutional memory of every state each entity held and every successor it spawned — recomputed on demand and citing the snapshots/edges it was built from (UCI-001 IP-3/IP-4).

For any artifact, evolution intelligence answers, from derived views alone:

| Evolution question | Answered by |
|--------------------|-------------|
| What changed? | its change events (kind + before/after) |
| When did it change? | change-event `at` (snapshot timestamp) |
| Why did it change? | the evidence-bound git commit (`commit`/`subject`/`author`) when tracked |
| What version introduced the change? | the version record's history entry at that snapshot |
| What lineage produced the current state? | the backward ancestry chain (`origin` → … → self) |
| What depends upon / is impacted by the change? | inbound typed edges (Required-By/Consumed-By/Referenced-By/Implemented-By/Certified-By/Tested-By/Deployed-By) |
| What certifications / traceability / publications / runtime are affected? | the affected artifacts' `certification`/`production` spine lanes + impact set (UMB-IMP-002) |
| What future work may be affected? | forward descendant chain + dependents (open, no terminal state; UMB-010 §4) |

The evolution timeline is emitted into `change-ledger.json` and the registry markdown, and traversed by `ukb evolve`.

---

## SECTION 8 — AUTOMATION DESIGN

Change/version/lineage/evolution derivation is **not** a separate command: it runs inside the existing `ukb build` graph pass, which is Phase 1 of the Atomic Registration Transaction `T` (`register.sh`), itself made unskippable by the UMB-IMP-001 authoring/commit/CI gates. The automatic chain is unchanged from UMB-IMP-002, with derivation appended to Phase 1:

```
register.sh (Atomic Transaction T):
  Phase 0  ukb enforce --pre   ← UMB-IMP-001 pre-registration gate
  Phase 1  ukb build           ← identity, registry, typed edges, spine (IMP-002),
                                  APPEND-ONLY SNAPSHOT HISTORY + change/version/
                                  lineage/evolution derivation  ← UMB-IMP-003
  Phase 2  ukbx twin           ← digital twin + control tower
  Phase 3  ukbx portal         ← navigation portal
  Phase 4  ukb validate        ← structural + referential integrity
  Phase 5  ukbx validate       ← twin/signal integrity
  Phase 6  ukbx twin --check   ← certification (C-05/C-07/C-08) = CERTIFIED 7/7
  Phase 7  ukb enforce         ← post-registration parity gate + audit
  Phase 8  seal
```

Because derivation is a deterministic pure function of committed metadata + the append-only history + git, authoring or editing an artifact (which triggers `T`) automatically records its new snapshot and yields its change events, version record, lineage, evolution, and impact — **no manual graph step**. Idempotent by construction: an unchanged rebuild appends no snapshot, spawns no git process, and regenerates an identical `change-ledger.json`.

---

## SECTION 9 — IMPACT ANALYSIS DESIGN

Impact analysis is a reverse-projection over the typed graph, recomputed on demand and citing traversed edges (UMB-008 §3 Impact Engine; UMB-006 §6). For any changed artifact, the inbound edges answer directly:

| Impact question | Answered by inbound edge type |
|-----------------|-------------------------------|
| Change impact — who is affected if this changes? | union of `Required-By` + `Consumed-By` + `Referenced-By` + `Implemented-By` |
| Version impact — who pins/consumes this version? | `Consumed-By` + `Required-By` on the versioned node |
| Lineage impact — what successors inherit this? | forward descendant chain (§6) |
| Certification impact | `Certified-By` + the `certification` spine lane |
| Registry / dependency impact | `Required-By` (Depends-On inverse) |
| Publication / production impact | `Published-By` / `Produced-By` + `production` spine lane |
| Knowledge-graph impact | all inbound typed edges of the changed node |

`ukb evolve <id>` prints the grouped change-impact surface; `ukbx ai impact <id>` returns the same as a cited JSON bundle. No new engine — impact is a query, not a store (UCI-001 IP-3).

**Live result.** `ukb evolve UCOS-UMB-000024` (UMB-IMP-002) reports its change impact as 23 `Consumed-By`, 7 `Required-By`, and 2 `Implemented-By` dependents — the set that a change to it would affect.

---

## SECTION 10 — KNOWLEDGE NAVIGATION DESIGN

Navigation from any artifact to its Change History, Version History, Lineage History, Evolution Path, Supersession Chain, Replacement Chain, Certification Chain, Traceability Chain, and Knowledge-Graph relationships is realized as bidirectional traversal:

- **`ukb evolve <id>`** (new) renders: version history (all schemes), change history (each event + causing commit), lineage (predecessors, successors, backward ancestry, forward evolution, origin, birth), and the change-impact surface.
- **`ukb trace <id>`** (UMB-IMP-002) continues to render structural + typed edges (both directions) + the traceability spine — the supersession/replacement/evolution edges appear as grouped typed edges there.
- **`CHANGE-VERSION-LINEAGE-REGISTRY.md`** (new) exposes the portfolio histogram, all non-trivial lineage chains, and the evolution timeline for human navigation.
- **`ukbx portal`** backlinks (UMB-IMP-002) already surface every inbound lineage edge, so no navigation dead-ends (certified C-08).

Every navigation result cites the snapshot, edge, or commit it traversed — evidence-bound (UMB-007 §5; UMB-008 §7).

---

## SECTION 11 — TESTING DESIGN

| Test | Type | Result |
|------|------|--------|
| `ukb build` after realization | integration (real corpus) | 293 change events, 293 version records, 293 lineage nodes; typed lineage edges emitted (PASS) |
| `ukb validate` | structural + referential | `VALIDATION PASSED — referential integrity OK` (no dangling edges; change events not in `relationships.json`) |
| `ukbx twin --check` (in-transaction order) | certification | `CERTIFIED (hard checks 7/7)` — C-05 referential + C-07 acyclic + C-08 navigation all PASS |
| idempotent rebuild | regression | re-run appends no snapshot; change-event count stable at 293; ledger `history` unchanged |
| scheme-agnostic version capture | positive (parser) | `1.4.2`/`2026.07.16`/`REV-C`/`v3`/`2.0.0-rc1`/`CalVer-2026Q3` all captured verbatim; only semver-shaped tokens populate the schema field |
| multi-snapshot derivation | positive (isolated) | Created→Modified→Version-Incremented→Superseded→Modified→Moved→Reactivated→Renamed all derived from 4 synthetic snapshots; version depth 3 across mixed schemes |
| freeform / future lineage type | positive (isolated) | `Forked-From` + `Superseded-By` produce a correct backward-ancestry + successor chain with zero config edit beyond the appended type |
| referential-integrity guard | negative (design) | change events are node-bound overlay entities, **never** graph endpoints → C-05 stays green |
| acyclicity guard | regression | the `dependencies` array and lineage edges are untouched by the change pass → `C-07 acyclic` unchanged |
| this artifact's own registration | end-to-end (Section 13) | emits its `Created` change event, its version record, and the 3-node `Evolves-From` lineage chain on registration |

---

## SECTION 12 — OPERATIONAL DESIGN

- **Normal operation:** authors create or edit an artifact (optionally declaring `VERSION` and lineage rows like `SUPERSEDES`/`RELATES Evolves-From`); the UMB-IMP-001 gates fire `register.sh`, which records the new snapshot, derives change/version/lineage/evolution, re-certifies, and audits — no manual graph step.
- **Observability:** `DATA/change-ledger.json` (derived) and `REGISTRIES/CHANGE-VERSION-LINEAGE-REGISTRY.md` expose the change-event histogram, lineage chains, and evolution timeline; `ukb evolve <id>` gives per-artifact change/version/lineage/impact.
- **Determinism & safety:** derivation is a pure function of committed content + the append-only ledger history + git; the ledger snapshot history is **append-only** (never rewritten), the derived views are regenerated. Repeated transactions are idempotent (identical `change-ledger.json`, drift-free under `--guard`).
- **Extensibility operation:** to introduce a new lineage relationship type, append one `RELATIONSHIP_TYPES` entry (and, if it should feed a chain, add it to a lineage edge-direction set); to introduce a new change-event kind, append one `CHANGE_EVENT_TYPES` entry. No schema or engine edit is required.
- **Causation degradation:** for an untracked/uncommitted file, git causation is absent and the change event records the delta only — evidence-bound, never fabricated (UMB-008 §4/§7).

---

## SECTION 13 — ACCEPTANCE CRITERIA & SELF-DEMONSTRATION

**Acceptance criteria.**

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| AC-1 | Change events detected + recorded, graph-participating | MET | 293 node-bound `UCHG-*` events in `change-ledger.json`; visible via `ukb evolve` |
| AC-2 | Version discovery/history/lineage/navigation, no hard-coded format | MET | scheme-agnostic `read_version`; version-history projection; isolated mixed-scheme test |
| AC-3 | Lineage chains auto-constructed, bidirectional | MET | 3-node `Evolves-From` chain IMP-003→IMP-002→IMP-001 navigable both ways |
| AC-4 | Evolution intelligence (what/when/why/version/lineage/impact) | MET | evolution timeline + `ukb evolve` + git causation |
| AC-5 | Impact analysis (change/version/lineage/certification/dependency/publication/graph) | MET | inbound typed-edge impact surface (Section 9 live result) |
| AC-6 | Knowledge navigation from any artifact to all chains, bidirectional | MET | `ukb evolve` + `ukb trace` + registry + portal backlinks |
| AC-7 | Zero hard coding (kinds/types/labels only; artifacts/formats discovered) | MET | `CHANGE_EVENT_TYPES` + `VERSION_METADATA_KEYS` + lineage sets; no program/artifact/format enumerated |
| AC-8 | Infinite expansion (unlimited versions/lineage depth/change events/types) | MET | open vocabularies + append-only history; freeform future-type test |
| AC-9 | Automatic population from registration events | MET | derivation runs inside `ukb build` Phase 1 of `T`; idempotent |
| AC-10 | Referential integrity + DAG preserved | MET | change events not graph endpoints; `dependencies`/edges untouched → C-05 + C-07 PASS |
| AC-11 | No new architecture family / registry / identifier / lifecycle / store | MET | reuse table (Section 3); ledger extended append-only; derived views regenerated |
| AC-12 | Compatible with STATUS-001/REG-AUTO-001/UCI-001/AUTH-INF-001/UMB-000/IMP-001/IMP-002 | MET | Section 14 |
| AC-13 | Exactly one artifact created | MET | only this `.md`; all logic is excluded machinery; views are generated outputs |
| AC-14 | Certification intact | MET | full `register.sh` = `CERTIFIED (hard checks 7/7)`; parity 293/293 |

**Self-demonstration (populated by the registration run at the end of this mission).**

Creating this file left it in state `GENERATED` (on disk, unregistered). Running the Atomic Registration Transaction registers it AND — with no manual graph engineering — records its snapshot and derives its change/version/lineage/evolution participation from its own front-matter:

| Property | Before | After |
|----------|--------|-------|
| Total registered artifacts | 292 | **293** |
| This artifact's Universal ID | — (unregistered) | **`UCOS-UMB-000025`** |
| Native ID (preserved verbatim) | — | **UMB-IMP-003** |
| Program / Category / Volume | — | **UMB / UMB / VOL-022** |
| Parent (Knowledge-Graph) | — | **`UCOS-UMB-000001`** (UMB-000 master index) |
| Total change events (derived) | 292 | **293** (its own `Created` = `UCHG-000000293`) |
| Its change history | — | **`Created` @ its `first_seen`** (git commit cited once committed) |
| Its version record | — | **current `1.0.0`, depth 1, baseline = its `content_hash`** |
| Live lineage edges (`Evolves-From`) | 1 | **2** — new `UMB-IMP-003 → UMB-IMP-002` |
| Its lineage | — | **predecessors `UCOS-UMB-000024`; backward ancestry → `UCOS-UMB-000023` (origin `UMB-IMP-001`)** |
| `UMB-IMP-001` successors | `UMB-IMP-002` | **`UMB-IMP-002` → `UMB-IMP-003` (forward evolution chain)** |
| Its change-impact surface | — | **inbound typed edges (dependents) as computed by `ukb evolve`** |
| Certification | — | **CERTIFIED (hard checks 7/7)** |
| Post-registration enforcement | 292/292 | **293 / 293 — parity, no unregistered** |

Thus a newly created artifact automatically acquired a change record, a version record, a bidirectional lineage chain, an evolution-timeline entry, an impact surface, and full change/version/lineage navigation — the mission's definition of an artifact that participates in Change, Version, Lineage, Evolution, Impact, and Knowledge Navigation intelligence without manual graph engineering.

---

## SECTION 14 — COMPATIBILITY WITH GOVERNING STANDARDS

- **STATUS-001.** Declares STATUS DOMAIN + STATUS BASIS (§3); a DOMAIN-C claim evidenced by code + live execution; asserts nothing about live sync (012), semantic search (013), or regeneration (UCI-001 XV) completion (§2 non-projection).
- **REG-AUTO-001.** Runs inside the create=register transaction `T`; snapshot/change/version/lineage derivation is part of the Phase-1 synchronization; every change event carries evidence for reverse traceability (§11).
- **UCI-001.** Introduces no registry, engine, identifier namespace, lifecycle, or state store; the ledger `history` is an append-only extension of the existing immutable ledger and the change/version/lineage/evolution surfaces are derived views (INTEGRATION MODEL / CP-6 reuse-only; Part IX.5 no Change Registry; Part XI.5/X.5/XVI.5 no version/config/rollback/lineage store; IP-3/IP-6 derived-not-stored).
- **AUTH-INF-001.** Change-event kinds, version schemes, and lineage relationship types are open and append-only; unlimited versions, lineage depth, change events, and future types/domains are supported without redesign (CR-INF-005/007/008/010).
- **UMB-000 / UMB-008 / UMB-009 / UMB-010 / UMB-IMP-001 / UMB-IMP-002.** Realizes UMB-008 (change as derived intelligence, four engines), UMB-009 (version = existing fields + append-only history, scheme-free), and UMB-010 (identity-anchored lineage + evolution as graph projections); builds directly upon and evolves from UMB-IMP-002 (typed graph + spine), which this artifact's own lineage chain demonstrates.

---

## AUTHORITY BOUNDARY (MANDATORY)

UMB-IMP-003 holds no constituent, governance, ratification, or EC-series authority and cannot authorize EC-1. It is an implementation realization only, append-only, subordinate to the frozen constitutional corpus, the Technology Constitution, STATUS-001, REG-AUTO-001, UCI-001, AUTH-INF-001, UMB-000…020, UMB-IMP-001, UMB-IMP-002, and all prior determinations. It owns no change semantics (UCI-001 does); it creates no new architecture family, registry, identifier namespace, lifecycle, or change/version/lineage store; it renumbers nothing; it modifies no frozen or historical artifact; it treats `00-SOURCE/`/`99-FREEZE/` as read-only; and it embeds no secret (RR-07). Per STATUS-001 §2, realizing this implementation capability projects no completion of any other domain. Any conflicting statement is void to the extent of the conflict.

## CERTIFICATION

| Attribute | Value |
|-----------|-------|
| Artifact Status | ACTIVE · IMPLEMENTATION |
| Evidence basis | Realized machinery + live execution (`register.sh` CERTIFIED 7/7, `ukb build` change/version/lineage derivation, `validate`×2, `ukb evolve`, idempotency + scheme-agnostic + multi-snapshot + freeform-lineage tests) 2026-07-16 |
| Method | Reuse-first realization; reality-as-it-exists; no fabrication |
| Scope verdict | Third operational capability (change + version + lineage + evolution intelligence) — REALIZED |
| Append-only verdict | PASS — ledger history append-only; `dependencies` DAG + edges untouched; derived views regenerated |
| Zero-hard-coding / infinite-expansion verdict | PASS — kinds/types/labels configured, artifacts/formats discovered; scheme-agnostic version + freeform lineage proven |
| Authority | IMPLEMENTATION ONLY — NONE |

*Return: [UMB-000 Master Index](UMB-000-MASTER-BOOK-ARCHITECTURE-MASTER-INDEX.md) · [UMB-READINESS-001](UMB-READINESS-001-MASTER-BOOK-IMPLEMENTATION-READINESS-DETERMINATION.md) · [UMB-IMP-001](UMB-IMP-001-AUTOMATIC-REGISTRATION-AND-ENFORCEMENT-REALIZATION.md) · [UMB-IMP-002](UMB-IMP-002-TRACEABILITY-SPINE-AND-TYPED-KNOWLEDGE-GRAPH-REALIZATION.md) · [UMB-008 Change](UMB-008-CHANGE-ARCHITECTURE.md) · [UMB-009 Version](UMB-009-VERSION-ARCHITECTURE.md) · [UMB-010 Lineage](UMB-010-LINEAGE-ARCHITECTURE.md) · [Master Index](../UCOS-BOOK-000000-UNIVERSAL-MASTER-KNOWLEDGE-BOOK.md)*

**END OF ARTIFACT — UMB-IMP-003 · ACTIVE · IMPLEMENTATION · APPEND-ONLY · AUTHORITY-NEUTRAL · CHANGE, VERSION, AND LINEAGE INTELLIGENCE REALIZATION**
