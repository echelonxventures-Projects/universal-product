# Scope B · Workstream 3 — Universal Lineage Projection · Architecture Determination

| Field | Value |
|---|---|
| MODE | **ARCHITECTURE DETERMINATION ONLY.** No implementation, no repository mutation, no artifact beyond this record. |
| CONSTITUENT AUTHORITY | **NONE** |
| PREDECESSORS | `SCOPE-B-WORKSTREAM-3-LINEAGE-DISCOVERY-DETERMINATION.md` · `F-1-…-DISPOSITION-DETERMINATION.md` · `F-1-…-CORRECTION-REPORT.md` (CERTIFIED) |
| PRIOR BASELINE | `B-01` · `B-02` CERTIFIED — **unmodified** |

---

## 1. Objective

Determine the architecture for a Universal Lineage Projection that answers **"How did this become this?"** while preserving the law that lineage is a derived projection.

The governing constraint is not a preference. `UCL-S-0350` carries it verbatim:

> **"UCI-001 Part XVI.5 — lineage and evolution are DERIVED projections over recorded history; no new store is created."**

**The central architectural finding: almost nothing needs to be built. The relation vocabulary, the family classifier, the acyclicity machinery, the sources and the consistency rule all exist. What is missing is composition and a query surface.**

---

## 2. Existing Lineage Reality

Measured at this baseline.

| Layer | Instrument | Population |
|---|---|---|
| Corpus edge vocabulary | `00-BOOK/tools/config.py` `RELATIONSHIP_TYPES` | **22 types** (44 directed), of which 16 are live |
| Knowledge relation vocabulary | `engine/knowledge/model.py` `RelationType` | **17 types**, checked against `RELATION_TYPE_VOCABULARY` |
| Data-layer classifier | `data/relationship_meta.py` `RelationshipKind` | **3 kinds** + an open free-text `type_tag` |
| **Lineage families** | `engine/knowledge/ukip/relationships.py` `ACYCLIC_FAMILIES` | **4 families**, each acyclicity-checked |
| Live corpus graph | `00-BOOK/DATA/relationships.json` | **12,899 edges** |
| Structural ancestry | `artifacts.json.parent` | 1,232 |
| Supersession ancestry | `change-ledger.lineage` | 1,233 nodes, 5 with predecessors |
| Derivation ancestry | `generated-artifact-registry` `producer` + `input_closure` | 345 |
| Identity history | `id-ledger.history` | 1,264 keys, 1,470 snapshots |
| Constitutional ancestry | `birth-ledger.parent_identity` | 38 births, 36 parented |

**Openness is declared, not assumed.** `UISD` `ISD-CE-02` states: *"relationship_types is deliberately NOT in this list and is therefore **open**."* A `RELATES <Type>` freeform row admits a type with no config edit at all.

**Post-F-1 integrity:** every projected `Parent` edge is backed by a declared parent (1,232/1,232), no artifact carries conflicting ancestry, `Parent`/`Child` are exact inverses.

---

## 3. Architectural Principles

| # | Principle | Enforced by |
|---|---|---|
| P-1 | **Lineage is derived; it is never authored.** No lineage store, no lineage authority. | `UCI-001 XVI.5` |
| P-2 | **Distinct meanings do not collapse.** Containment, derivation, transformation, supersession and dependency are five questions, not five names for one. | family classifier, §4 |
| P-3 | **A projection may not assert what its source does not declare.** | `ukb validate` lineage-consistency rule (F-1) |
| P-4 | **No fourth type space.** Three relation vocabularies already exist; a lineage projection composes over them and declares none of its own. | §5 |
| P-5 | **Deleting the projection changes no verdict**, only the cost of reaching one. | derived-truth test |
| P-6 | **Open by registration.** A new lineage relation is an append, never an amendment. | `ISD-CE-02` |

---

## 4. Projection Model

### 4.1 Lineage object model

A lineage **node** is any object already holding identity — it is **not** a new object kind:

| Plane | Identity | Source |
|---|---|---|
| Corpus artifact | `UCOS-<CAT>-<NNNNNN>` | `artifacts.json` |
| Repository object | same | `id-ledger` / UGA |
| Constitutional object | `urn:ucos:ucko:<ns>:<name>` | `birth-ledger` |
| Assigned identifier | `UCOS-<CODE>-<12hex>` | `UCOS-NUCLEUS-IDENTIFIER-DICTIONARY` (B-02) |

### 4.2 Lineage event model

An event is an existing record, not a new one: `change-ledger.change_events` (`kind`, `at`, `from`, `to`, `snapshot_seq`) · `id-ledger.history` snapshots · `birth-ledger` creation facts · `version_records`.

### 4.3 The five lineage kinds, mapped onto the EXISTING family classifier

`ACYCLIC_FAMILIES` already declares four; transformation is event-shaped rather than edge-shaped.

| Lineage kind | Family | Relations | Source of truth |
|---|---|---|---|
| **Containment** | `structure` | `Parent`/`Child`; knowledge `EXTENDS`/`INHERITS` | `artifacts.json.parent` |
| **Derivation** | `derivation` | `Derived-From`, `Created-From`, `Forked-From`; knowledge `DERIVED_FROM`/`GENERATED_FROM` | `generated-artifact-registry` |
| **Supersession** | `supersession` | `Supersedes`/`Superseded-By`, `Replaced-By`, `Merged-Into`, `Evolves-From`/`Evolves-To` | `change-ledger.lineage` |
| **Dependency** | `dependency` | `Depends-On`/`Required-By`, `Consumes`/`Consumed-By` | declared metadata rows |
| **Transformation** | *(event, not edge)* | — | `change_events` + `history` |

**DETERMINED: the family classifier is reused, not redefined.** Transformation is deliberately left as an event stream: forcing it into an edge family would collapse "what happened to this object" into "what other object it points at" — the exact meaning-collapse P-2 forbids.

### 4.4 Projection model — **ONE projection, typed relations**

| Option | Verdict |
|---|---|
| **One projection with typed relations** | **SELECTED.** One consistency surface, one replay, one query. The families keep meanings distinct *within* it, so unification costs no semantics. |
| Multiple coordinated projections | **REJECTED.** Five projections create ten pairwise consistency obligations and five replay proofs. F-1 was a single divergence between two surfaces; five surfaces multiply exactly that risk. |
| Another evidence-backed model | **REJECTED.** No third form is needed: every input is already an evidence-bearing record. |

### 4.5 Query model

Six questions, each already answerable from a located source (Workstream 3 §4.4):

```
what is this?          → UGA object_class · artifacts.json category
who owns this?         → UGA owner · artifacts.json owner · UOBC owner
where did it come from?→ first_seen · parent · parent_identity · producer
when was it created?   → history[].at · creation_timestamp
what has it become?    → change_events · version_records · successors
what depends on it?    → dependency family (inverse traversal)
```

**Query contract:** every answer cites the source authority it came from and the family it belongs to. An answer that cannot name its source is not returned.

---

## 5. Relationship Ontology

Assessed against the nine types the mandate names.

| Type | Status | Semantics | Source | Ownership | Validation rule |
|---|---|---|---|---|---|
| `Parent` / `Child` | **EXISTS**, live 1,232 | structural containment | `artifacts.json.parent` | UMB-IMP-001 | **F-1 rule: every edge backed by the declared parent; ≤1 parent per child** |
| `Depends-On` / `Required-By` | **EXISTS**, live 4,776 | requires-to-function | declared metadata row | UMB-006 | acyclic (`dependency` family) |
| `Derived-From` / `Derived-Into` | **EXISTS**, unused | produced by transforming a source | `generated-artifact-registry` `input_closure` | `UCOS-GENERATED-ARTIFACT-REGISTRY-001` | acyclic (`derivation`); target must be a declared input |
| `Supersedes` / `Superseded-By` | **EXISTS**, unused | replaces under one lineage | `change-ledger.lineage` | UMB-008 | acyclic (`supersession`); `origin` must terminate |
| `Produces` / `Produced-By` | **EXISTS**, unused | emits an artifact | `generated-artifact-registry.producer` | same | producer must be a registered object |
| `Consumes` / `Consumed-By` | **EXISTS**, live 316 | reads without owning | declared metadata row | UMB-006 | acyclic (`dependency` family) |
| `References` / `Referenced-By` | **EXISTS**, live 6 | cites; carries no obligation | declared metadata row | UMB-006 | referential integrity only |
| **`Evidence-Of`** | **ABSENT** — the only gap | this record evidences that claim | `evidence-universe.json`, UAKOS validation records | UVI / CEP-005 | target must be a declared evidence surface |

**DETERMINED: the ontology needs one registration, not a design.** Eight of nine already exist; `Evidence-Of` is admitted by **append** under `ISD-CE-02` (corpus vocabulary) and by **two-sided registration** in the knowledge layer (`RELATION_TYPE_VOCABULARY` + enum, or the alignment check fails closed). **No amendment, no new authority.**

**Three vocabularies, one composition (P-4):** corpus (22), knowledge (17), data (3 + open tag). The projection **maps** between them and declares none of its own. Introducing a fourth would be the duplicate-registry defect this scope forbids.

---

## 6. Data Flow

```
SOURCE AUTHORITIES                    (unchanged, unmoved, unwrapped)
  artifacts.json          parent          → containment
  change-ledger.json      lineage/events  → supersession + transformation
  generated-artifact-registry.json        → derivation
  id-ledger.json          history         → temporal
  birth-ledger.json       parent_identity → constitutional ancestry
  declared metadata rows                  → dependency
            │
            ▼
  UNIVERSAL LINEAGE PROJECTION            (read-only · derived · families typed)
            │
            ▼
  QUERY SURFACE (six questions)  +  CONSISTENCY VALIDATION (extends ukb validate)
```

No cycle: every projection reads sources; no source reads a projection.

---

## 7. Ownership Model

**Pattern B — distributed governed evidence**, as determined in Workstream 3. Confirmed, not revisited.

| Concern | Owner |
|---|---|
| Containment truth | UMB-IMP-001 / `artifacts.json` |
| Supersession + transformation truth | UMB-008 / `change-ledger.json` |
| Derivation truth | `UCOS-GENERATED-ARTIFACT-REGISTRY-001` |
| Identity history | UCKP-ART-05 persistence binding |
| Constitutional ancestry | `UOBC-000001` |
| Edge vocabulary | `UCOS-UKB-TOOLING` (corpus) · UKIP (knowledge) |
| **The projection itself** | **DERIVED TRUTH, authority NONE** |

**No lineage authority is created. No lifecycle owner is duplicated.** If the projection is ever persisted, it is a `GENERATED_ARTIFACT` under the existing mutation class — the pattern `B-02` certified.

---

## 8. Verification Model

| Capability | Status | Determination |
|---|---|---|
| Projection/source consistency | **EXISTS (F-1)** | `ukb validate` refuses a `Parent` edge not backed by the declared parent, and any child with >1 parent. **Extend the same rule to further families as their sources gain per-artifact fields — no new mechanism.** |
| Relationship type correctness | **PARTIAL** | The corpus vocabulary is checked; the knowledge layer fails closed on vocabulary/enum divergence. Cross-vocabulary mapping is unchecked — **new coverage required**. |
| Ancestry determinism | **EXISTS** | `ukb build` proven byte-identical across runs (F-1 evidence). |
| Lineage completeness | **ABSENT** | Nothing asserts every node reaches a root, or that `ancestor_chain` is closed. **New coverage required.** |
| Lineage replay | **PARTIAL** | Sources regenerate deterministically; no lineage-specific replay proof. |
| Mutation detection | **PARTIAL** | `id-ledger.history` append-only; `LineageLedger` hash-chained with a self-check — neither gated at repository scale. |

**DETERMINED: no new verification gate is justified.**

* Consistency and completeness extend `ukb validate`, already a declared `verify.sh` stage.
* Acyclicity is already computed per family by UKIP.
* A new gate becomes justified **only** if the projection is persisted as an artifact — and then `B-02`'s precedent applies (producer + registration + the existing stage), not a new stage.

---

## 9. Evidence Model

| Proof | Evidence that exists | Sufficiency |
|---|---|---|
| **Origin** | `first_seen` (4,848) · `lineage.birth` (1,233) · `origin` | **SUFFICIENT** |
| **Transformation** | `change_events` (1,358) with `kind`/`from`/`to`/`snapshot_seq` | **SUFFICIENT** |
| **Derivation** | `producer` + classified `input_closure` (345) | **SUFFICIENT** |
| **Certification chain** | `certification.json` · UAKOS `validation-record.json` · UICM registries | **PRESENT but not keyed on lineage** — gap `G6`, pre-existing, owned elsewhere |

**DETERMINED: lineage proof is generated by citation, never by assertion.** Every projected edge carries the source record and the family that produced it — the discipline that made F-1 detectable once the rule existed. `Evidence-Of` (§5) is what would key the certification chain onto lineage and close the shape of `G6` — its disposition remains with its owner.

---

## 10. Dependency Model

| Dependency | Relationship | Risk |
|---|---|---|
| **Entity Evolution Constitution** (`CEP-009`, `UCKP` Article 14, `UAUE-000001`) | Supersession and transformation families read evolution records. Consumed read-only. | **LOW** — no evolution authority is touched |
| **Entity Registry Reality** (`artifacts.json`, UGA, `id-ledger`) | Every node identity and containment edge originates here | **MEDIUM** — the projection is only as consistent as its sources; F-1 proved that, and the F-1 rule now guards it |
| **Capability Reality** | **NONE TODAY** — not implemented. The projection must not assume it. | **LOW**, and a boundary to hold: lineage over capabilities becomes available when capabilities become objects, by registration |
| **Verification Intelligence** (`UVI-000001`) | Any new test object enters selection; no UVI change needed unless a stage is added | **LOW** |
| `UOBC-BSP-001` (B-01) | A persisted projection would be `GENERATED_ARTIFACT` → `MANDATORY_ABSENCE`; `BSP-L-03` refuses a birth record for it | **LOW** — already enforced |
| `UCPA-000001` | Lineage relations reduce to `ONT-03 RELATIONSHIP` under the root ontology | **LOW** |

---

## 11. Implementation Readiness

**READY.** No blocking condition remains.

| Precondition | Status |
|---|---|
| Lineage authority question settled | **YES** — `UCI-001 XVI.5`; Pattern B confirmed |
| F-1 divergence corrected | **YES** — CERTIFIED; 0 unbacked edges, 0 conflicting ancestries |
| Relation vocabulary available | **YES** — 8 of 9 exist; `Evidence-Of` by registration, not amendment |
| Family classifier available | **YES** — `ACYCLIC_FAMILIES`, reused not redefined |
| Sources populated and measured | **YES** — §2 |
| Consistency rule in place | **YES** — the F-1 rule, proven to fail on the defect |
| New authority required | **NONE** |
| New gate required | **NONE** (unless persisted; then B-02's pattern) |

**Scope of the implementable increment**, stated so it cannot drift:

1. A read-only composition over the six sources, typed by the existing families.
2. The six-question query surface, every answer citing its source.
3. Extension of `ukb validate` for completeness and cross-vocabulary mapping.
4. `Evidence-Of` registration **only if** the certification chain is in scope — otherwise deferred with `G6`.

**Explicitly out of scope:** any lineage store, any fourth relation vocabulary, any change to the three existing ones, any capability-lineage assumption, and `G6`.

---

# ARCHITECTURE DETERMINATION COMPLETE
