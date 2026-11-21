# PHASE 4 CAPABILITY DISCOVERY AND GAP DETERMINATION

**Universal Persistent Evolutionary Graph Memory — measurement before construction (Steps 2 and 4)**

| Field | Value |
|-------|-------|
| Report class | Capability discovery + gap determination |
| Authority | NONE — DERIVED TRUTH. This report measures located owners; it creates none and amends none. |
| Temporal anchor | Logical: `git HEAD = 7b7d0fd93fa0188e8b00c48499b4f4e67784e444` |
| Temporal reference system | `logical:git-commit-order@ucos-consolidation` |
| Location / reality context | Repository reality `UCOS-CONSOLIDATION`; no planetary, calendar or civilizational frame asserted |
| Method | Every row carries a `file:line` citation. A row with no citation is recorded as MISSING, never as present. |

---

## 1. Governing constraint

The directive's Step 3 forbids creating a memory engine, a graph memory database, a knowledge memory authority or a history authority. Memory is to be a **substrate property**, resolved through owners that already exist:

| Concern | Owner | Located at |
|---|---|---|
| Entity | CEU-001 | `engine/ceu/existence.py`, `engine/ceu/catalog.py` |
| Relationship semantics | UCKP ART-07 | `engine/uckp/law.py:250-257` |
| Context | UCXI | `00-MASTER/UCXI-000001/ucxi-declaration.json`, `engine/context/` |
| Identity | EPIC / REG-AUTO | `engine/registry/universal/identity.py`, `00-BOOK/DATA/id-ledger.json` |
| Knowledge | UKDA / UKIP | `engine/knowledge/`, `knowledge/canonical-knowledge.json` |
| Evolution | UAUE | `engine/uaue/`, `00-MASTER/UAUE-000001/UAUE-EVOLUTION-HISTORY.json` |
| Decision | UCDA | `00-MASTER/UCDA-000001/ucda-decisions.json` |

Measurement finding that governs the whole phase: **every one of the seven concerns has a located owner, and every owner already records history.** No owner is absent. Therefore no owner may be created, and the lawful disposition for the memory *models* is REUSE, not CREATE.

---

## 2. Entity history (Step 2.1)

Inspected: `engine/ceu/existence.py`, `engine/ceu/catalog.py`, `engine/registry/`.

| Property | State | Evidence |
|---|---|---|
| Identity | **SUPPORTED** | `universal_id_for` / `universal_id` `engine/ceu/existence.py:142-165`; stamped at registration `:315-325` |
| Supersession | **SUPPORTED** | `supersede()` `:453-514` — 0..n successors covering split/merge/transform/deprecate; refuses self-supersession `:481` |
| Resurrection | **SUPPORTED** | `resurrect()` `:515-537`, `ACTION_RESURRECT` `:235` |
| Lineage | **SUPPORTED (two mechanisms)** | CEU `ancestry()` `:563-582`; corpus lineage projection `engine/lineage/projection.py:81-176` |
| Append-only unit register | **SUPPORTED** | `_admit()` `:328-350` refuses a different unit under an existing `(form,key)`; no update or delete method exists |
| Append-only hash-chained journal | **SUPPORTED** | `_append()` `:672-682` chains `prev_hash`; `verify_audit()` `:689-706` re-walks sequence, back-link and digest |
| Permanent historical graph representation | **MISSING** | The registry is in-memory only (`__slots__` `:241`). `to_document()` `:710-731` / `from_document()` `:742-825` / `reconstruct()` `:827-854` exist but **no module calls them against a file** — verified by repo-wide grep, which finds callers only under `engine/tests/`. |

**Determination.** Identity, supersession, resurrection and lineage are ALREADY IMPLEMENTED. The permanent historical graph representation is MISSING — not because a history model is absent, but because the entity register that holds it is a runtime object with no resolution surface into the persisted corpus registers.

### 2.1 One measured defect worth recording

`_supersessions` is the single structure mutated in place: `resurrect()` writes `record["active"] = False` into the live dict (`engine/ceu/existence.py:531-534`). Because the journal records only `(action, subject, content_hash)` (`AuditEntry` `:202-231`) and not the successor list, a supersede → resurrect → supersede sequence is **not reconstructible from the journal alone**. Recorded here as a finding; repairing it is a CEU-001 owner decision and is deliberately **not** taken by this phase.

---

## 3. Relationship history (Step 2.2)

Inspected: `engine/uckp/graph.py`, `engine/graph/model.py`, `engine/registry/models.py`, `engine/ceu/existence.py` `RelationshipView`.

| Property | State | Evidence |
|---|---|---|
| Relationship identity | **SUPPORTED (three schemes)** | CEU relationship-as-unit keyed `type:source->target` `engine/ceu/existence.py:952-961`; `Relationship.edge_id` `engine/registry/models.py:196-227`; `Edge.edge_id` `engine/graph/model.py:110-145`. UCKP edges carry **no** id, only a structural `key()` `engine/uckp/graph.py:57-64` |
| Graph projection | **SUPPORTED, explicitly a projection in all three graphs** | `engine/graph/model.py:12-16` ("the graph is a *read projection* of Registry Truth"); UCKP edges "derived, never authored" `engine/uckp/graph.py:12-16`; ULP "creates no store" `engine/lineage/projection.py:26-30` |
| Relationship evolution | **PARTIAL** | `Evolves-From` / `Evolves-To` exist as **edge type names between entities** (`engine/graph/engine.py:60-61`, `engine/lineage/families.json` supersession family). That is entity evolution expressed as an edge, not evolution *of* a relationship. |
| Permanent relationship memory / historical relationship states | **MISSING** | No temporal-validity field exists on **any** of the four relationship representations: `Relationship` = `edge_id, source, target, type, inverse_of, note` `engine/registry/models.py:191-197`; `Edge` = `edge_id, source, target, type, note, attributes` `engine/graph/model.py:110-118`; `UniversalKnowledgeEdge` = `source, target, relation, relationship_class, scope` `engine/uckp/graph.py:41-47`; CEU relationship attributes = `relationship_type, source, target, topologies, authority` `engine/ceu/existence.py:938-948`. A grep for `valid_from|valid_to|as_of` across these modules returns only `signals` `as_of` at `engine/graph/projections.py:359`. |

**Determination.** Relationship identity and graph projection are ALREADY IMPLEMENTED. Relationship evolution is PARTIAL. Permanent relationship memory and historical relationship states are MISSING.

### 3.1 Structural consequence

CEU relationship keys contain no time or sequence component (`engine/ceu/existence.py:955`), so a given `(type, source, target)` can be asserted exactly once for all time and re-assertion is a silent no-op (`_admit` `:331-333`). There is no "edge instance" concept, and no relationship-history query exists anywhere in the repository.

---

## 4. Knowledge memory (Step 2.3)

Inspected: UKDA (`engine/knowledge/`), UKIP (`engine/knowledge/ukip/`), CKO (`engine/knowledge/cko.py`), UCKO (`engine/uckp/ucko.py`).

| Property | State | Evidence |
|---|---|---|
| Origin | **SUPPORTED** | UKIP `ProvenanceChain` — tamper-evident, append-only, hash-chained, genesis `"0"*64` `engine/knowledge/ukip/provenance.py:34`; ordered stages `OBSERVED → … → SUPERSEDED` `:39-49` |
| Evidence | **SUPPORTED (uneven)** | UCKO `evidence: tuple[EvidenceRef, ...]` `engine/uckp/ucko.py:120`; CKO `evidence` is a tuple of **opaque strings** `engine/knowledge/cko.py:117` |
| Confidence | **MISSING from every knowledge object** | No `confidence` field on `CanonicalKnowledgeObject` `cko.py:96-124`, on `RegisteredKnowledge`, or anywhere in `ucko.py`. The only located `confidence` is on temporal `Provenance` `engine/temporal/coordinate.py:128-152`, plus a reuse floor at `engine/knowledge/integration/reuse.py:246` |
| Lifecycle | **SUPPORTED** | `transition_to` with an enforced transition graph `cko.py:262-276` |
| Reuse | **SUPPORTED (separate capability, not an object field)** | `engine/knowledge/integration/reuse.py:246, 383-391` |
| Graph-integrated memory | **MISSING** | `KnowledgeBase.graph()` `engine/knowledge/store.py:155-158` projects only each CKO's own link topology. Knowledge is **not** reachable from an entity's memory: `engine/lineage/sources.py:109-132` never reads `knowledge/canonical-knowledge.json`, and the UCKP knowledge graph is a separate graph ULP never reads. |
| Append-only persistence | **NOT APPEND-ONLY** | `KnowledgeStore.save()` rewrites whole JSON envelopes via `path.write_text` `engine/knowledge/store.py:274-290`; `replace_object` discards the prior version with no supersession record `:169-175` |

**Determination.** Origin, evidence, lifecycle and reuse are ALREADY IMPLEMENTED. Confidence is MISSING (recorded as a finding for UKDA/UKIP owners, not repaired here). Graph-integrated memory is MISSING — this is a Phase 4 target.

---

## 5. Evolution memory (Step 2.4)

Inspected: `engine/uaue/`, `engine/uckp/evolution.py` (ART-14), `engine/uckp/state.py` (ART-12).

| Property | State | Evidence |
|---|---|---|
| Evolution stages | **SUPPORTED** | 15-stage closed cycle `observe … continuation` `engine/uckp/evolution.py:44-63`; `EVOLUTION_CYCLE` derived from the enum `:76-80` |
| Transitions | **SUPPORTED, enforced** | `append()` refuses anything but the next lawful stage and refuses cycle numbers that do not advance exactly once per cycle `engine/uckp/evolution.py:188-224` |
| Supersession / immutable state | **SUPPORTED** | ART-12 `ConstitutionalTimeline` — append-only, "no update, no delete and no reorder method" `engine/uckp/state.py:1-22`; `parent_state_id` inside the state digest `:1-22` |
| Append-only, verified on read | **SUPPORTED** | `from_document()` replays every record through `append` `engine/uckp/evolution.py:266-303`; `rehydrate_history()` refuses a document not declaring `append_only` `engine/uaue/history.py:206-233` |
| Persisted evolution history | **SUPPORTED** | `00-MASTER/UAUE-000001/UAUE-EVOLUTION-HISTORY.json` — measured: 780 records, 52 cycles, 8,580 findings, **572 distinct subjects**, records shaped `{cycle, digest, findings, outcome, stage, subject}` |
| Contextual (non-wall-clock) time | **SUPPORTED** | "when" is `cycle=N stage=X ordinal=N` — logical time, explicitly never wall-clock `engine/uaue/history.py:43-96` |
| ART-14 law | **DECLARED** | "It appends; it never rewrites; it never terminates." `engine/uckp/law.py:307-315` |
| Universal evolution graph | **MISSING** | Evolution history is keyed by UAUE subject ids (`UCOS-EVO-…`) and is not reachable from a canonical entity identity. No projection joins evolution memory to entity, relationship, knowledge or decision memory. |
| Evolution transaction object | **MISSING in code** | Determined only in root documents `H-06-UNIVERSAL-EVOLUTION-TRANSACTION-OBJECT-DETERMINATION.md`, `H-06-ATOMIC-EVOLUTION-TRANSACTION-AUTHORITY-DETERMINATION.md`; no transaction class located in `engine/uaue/` or `engine/uckp/` |

**Determination.** Evolution stages, transitions and supersession are ALREADY IMPLEMENTED — this is the strongest existing memory in the repository. The universal evolution graph is MISSING.

---

## 6. Temporal memory (Step 2.5)

Inspected: `engine/temporal/coordinate.py`, `operations.py`, `facets.py`.

| Property | State | Evidence |
|---|---|---|
| Past states | **SUPPORTED** | Recorded facets + `ValidityPeriod.until` `engine/temporal/coordinate.py:276-303` |
| Current states | **SUPPORTED** | Open-ended validity (`until=None` means living object, distinct from unknown) `:276-303` |
| Future states | **PARTIAL** | Representable only weakly via `SystemType.UNKNOWN` `:28-45` and open-ended validity. There is **no projected/planned future-state coordinate type** and **no as-of query API** over `TemporalRecord`. |
| Contextual time | **SUPPORTED, and genuinely non-Earth** | `system_identifier` is **required** so no default stands in for a decision `:1-11`; `SystemType` = `PHYSICAL, LOGICAL, CONTEXTUAL, SIMULATED, UNKNOWN` `:28-45`; `Ordering.INCOMPARABLE` `:48-60`; `Precision.resolution` is a free string so "tick" or "block" are representable `:113-125`; bounds in different reference systems are refused `:276-303` |
| No clock assumption | **SUPPORTED** | "get current coordinate" is deliberately **not** implemented as a clock read, because that would make coordinates unreplayable `engine/temporal/operations.py:1-15` |
| Eight temporal facets | **SUPPORTED** | `CREATION, EXISTENCE, VALIDITY, EVOLUTION, CERTIFICATION, RETIREMENT, ARCHIVE, RESTORATION` with a declared precedence graph `engine/temporal/facets.py:30-64`; `with_facet` refuses re-recording a facet at a different coordinate `:129-152` |
| Integration | **MISSING** | The model has **no call site outside `engine/temporal/` and its own tests** — verified by grepping `engine.temporal` across `engine/`. No persisted `TemporalRecord` exists. A weaker rival model competes: UCKO `TemporalEvent` = `sequence, event, state_id, at=TIMELESS` with a bare string `at` and no reference system `engine/uckp/values.py:269-293`. |

**Determination.** The temporal model is ALREADY IMPLEMENTED and is correct on the hardest requirement — it assumes no Earth, no UTC, no single civilization. It is PARTIAL only on future states, and **unintegrated**.

---

## 7. Required gap matrix (Step 4)

Ten capabilities, each against its located owner.

| Capability | Existing Owner | Evidence | Gap | Action |
|---|---|---|---|---|
| **Entity memory** | CEU-001 | `engine/ceu/existence.py:453-582` supersede/resurrect/ancestry; append-only hash-chained journal `:672-706`; `id-ledger.json` history for 1,264 entities | **PARTIAL** — history exists in two disconnected places (runtime journal, corpus ledger) and no surface joins them. `id-ledger.history` is loaded but only element `[0]` is read, at `engine/lineage/query.py:86-89` | **EXTEND** ULP to resolve the full identity version series per subject |
| **Relationship memory** | UCKP ART-07 | `engine/uckp/law.py:250-257`; edges projected at `engine/graph/engine.py:121-130`; `relationships.json` | **MISSING** — no temporal validity, version or supersession pointer on any of four relationship representations (§3) | **EXTEND** ULP to project relationship memory from the governed edge register; **REFER** temporal-validity fields to UCKP ART-07 owner as a finding, do not invent a field |
| **Context memory** | UCXI | `00-MASTER/UCXI-000001/ucxi-declaration.json`; `engine/context/taxonomy.py` 16 universal kinds + root; CEU `bind-context` action `engine/ceu/existence.py:233-236` | **PARTIAL** — context binding is a journal action with no persisted per-entity context history | **EXTEND** ULP to resolve context memory from UCXI; **REFER** persistence to UCXI owner |
| **Knowledge memory** | UKDA / UKIP | `engine/knowledge/cko.py:96-124`; UKIP hash-chained provenance `ukip/provenance.py:1-70`; 142 objects in `knowledge/canonical-knowledge.json` | **MISSING graph integration** — ULP never reads the knowledge register (`engine/lineage/sources.py:109-132`) | **EXTEND** ULP to resolve knowledge memory for a subject |
| **Decision memory** | UCDA | 123 decisions, nine-stage lifecycle, five dispositions, fail-closed gate `00-MASTER/UCDA-000001/ucda_engine.py:1-101` | **PARTIAL** — rich and gated, but not reachable from an entity, and not append-only (supersession is a mutable `superseded_by` field) | **EXTEND** ULP to resolve decision memory; **REFER** append-only form to UCDA owner |
| **Evidence memory** | UKIP / UCKO | `ukip/provenance.py:1-70`; `ucko.py:120` `evidence: tuple[EvidenceRef, ...]` | **PARTIAL** — `KnowledgeRegistry` is in-memory with no writer (`ukip/registry.py:368-512`), so provenance chains are not persisted; CKO evidence is opaque strings | **EXTEND** ULP to resolve evidence memory from the knowledge register's recorded evidence |
| **Validation memory** | engine/validation | `ValidationEvidence` record type `engine/validation/evidence.py:24-34`; `validation` is canonical evolution stage `engine/uckp/evolution.py:53` | **PARTIAL** — a record type with no ledger, chain or store | **REUSE** — validation memory is already carried per-cycle inside the persisted evolution ledger; no extension required |
| **Certification memory** | engine/certification, engine/universal_certification | Append-only hash-chained ledgers with no update/delete `engine/certification/ledger.py:33-79`, `universal_certification/audit.py:32-55` | **PARTIAL** — both explicitly in-memory only, "persistence is the caller's concern" `ledger.py:11-14`; retained only as scattered per-run files under `.runtime/` and `application/_evidence/` | **REUSE** — `certification` is a canonical evolution stage recorded in the persisted ledger; **REFER** repository-wide persistence to the certification owners |
| **Evolution memory** | UAUE | 780 records / 52 cycles / 8,580 findings / 572 subjects at `00-MASTER/UAUE-000001/UAUE-EVOLUTION-HISTORY.json`; ART-14 `engine/uckp/law.py:307-315` | **PARTIAL** — fully persisted and append-only, but keyed by UAUE subject and unreachable from a canonical entity | **EXTEND** ULP to resolve evolution memory per subject |
| **Learning memory** | UAUE | `learn` is canonical stage 2 `engine/uckp/evolution.py:52`; `learning_object()` `engine/uaue/history.py:283-306`; `knowledge-assimilation` is stage 14 `evolution.py:65` | **PARTIAL — thinnest** — no learning object model, no learned-lesson store, no retrieval path. A learned outcome exists only as a `findings` string inside an evolution record | **EXTEND** ULP to surface learning memory from the `learn` and `knowledge-assimilation` stage records; **REFER** a learning object model to UAUE owner |

### 7.1 Classification summary

**Already implemented (REUSE, do not touch):** entity identity · entity supersession · entity resurrection · entity lineage · relationship identity · graph projection · evolution stages · evolution transitions · evolution supersession · knowledge origin · knowledge evidence · knowledge lifecycle · knowledge reuse · contextual time · non-Earth/non-UTC time · append-only evolution ledger · validation-as-evolution-stage · certification-as-evolution-stage.

**Partially implemented (EXTEND by projection):** entity memory · context memory · decision memory · evidence memory · evolution memory · learning memory · relationship evolution · future temporal states.

**Missing (the Phase 4 target):** a **single resolution surface** by which any canonical entity resolves identity → context → relationship → knowledge → evidence → decision → evolution history. Also missing: relationship temporal validity (referred to its owner), knowledge confidence (referred), a learning object model (referred), an evolution transaction object (referred).

### 7.2 The determination that shapes the implementation

> The gap is **not** absent memory. Every layer of memory has a located owner and every owner already records history. The gap is that **no canonical entity can resolve its own memory across those owners.**

Ten capabilities measured; **zero** justify CREATE. Nine are REUSE or EXTEND-by-projection. The tenth — the resolution surface — is an EXTEND of `engine/lineage/` (ULP), which already carries the required discipline: *"lineage and evolution are DERIVED projections over recorded history; no new store is created"* (`UCI-001 Part XVI.5`, cited at `engine/lineage/projection.py:33-36`).

**A new `engine/memory/` package would be the memory engine Step 3 prohibits, and is REFUSED.**

### 7.3 Findings referred to their owners, not repaired here

Repairing any of these would amend an owner this phase has no authority over. Each is recorded so its owner can act.

| Finding | Owner | Detail |
|---|---|---|
| P4-F-001 | CEU-001 | `_supersessions` is mutated in place by `resurrect()` `engine/ceu/existence.py:531-534`; supersession terms over time are not reconstructible from the journal (§2.1) |
| P4-F-002 | UCKP ART-07 | No relationship representation carries temporal validity, version or supersession (§3) |
| P4-F-003 | UKDA / UKIP | No `confidence` field on any knowledge object (§4) |
| P4-F-004 | UKDA | `KnowledgeStore.save()` is a whole-file rewrite and `replace_object` discards the prior version (§4) |
| P4-F-005 | UCDA | The decision register is not append-only; supersession is a mutable field |
| P4-F-006 | UKIP, certification owners | Provenance, certification and audit chains are correct in memory but have no repository-wide persisted store |
| P4-F-007 | engine/temporal owner | The temporal model has no call site outside its own package; a weaker rival `TemporalEvent` competes at `engine/uckp/values.py:269-293` |
| P4-F-008 | UAUE | No learning object model and no evolution transaction object in code |
| P4-F-009 | UCXI | UCXI-000001 owns the context KIND vocabulary but persists no per-subject context binding; CEU's `bind-context` is a runtime journal action (`engine/ceu/existence.py:233-236`) with no corpus record. The context layer therefore resolves the corpus artifact register's governed placement, attributed to that record rather than to UCXI. |
| P4-F-010 | UCL-000001, ACEE-000001 | **Pre-existing derived-artifact drift, measured during Phase 4 gate execution and deliberately NOT repaired.** The committed `00-MASTER/UCL-000001/ucl.json` records `ckos_discovered: 3403`, `knowledge_objects_discovered: 130`, `relations_discovered: 474`, `relationships_without_target_identity: 217`, `unadmitted_target_artifacts: 84` and `blocking_failures: []`. Re-running `00-MASTER/UCL-000001/ucl_engine.py --gate` **at clean `HEAD` 7b7d0fd9, with all Phase 4 changes stashed**, measures 274 and 85 against disclosed bounds of 217 and 84, so `UCL-V-41` and `UCL-V-42` fail and `CK-UCL` drives the aggregate gate FAIL-CLOSED. The counts are byte-identical with and without Phase 4 changes, so the drift is not caused by this phase. Regenerating those artifacts inside this commit would flip two programmes' committed certification verdict from passing to failing — a substantive governance act over programmes Phase 4 has no authority over — so the regenerations were reverted and the drift is referred to the UCL and ACEE owners. |

---

## 8. Determination

Discovery is complete and precedes construction. The lawful Phase 4 action is a **single projection extension to ULP** that resolves seven memory layers for any subject by delegating to located owners, creating no store, minting no identifier and declaring no authority.

The layer set is to be declared as **data**, not code, per `ADR-0007` (disclose every finite enumeration), so a future memory layer requires no code change.

Proceed to Step 5 — governance registration.
