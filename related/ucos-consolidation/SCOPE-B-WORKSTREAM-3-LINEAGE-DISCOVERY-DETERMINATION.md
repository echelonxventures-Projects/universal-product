# Scope B · Workstream 3 — Universal Lineage Projection · Discovery Determination

| Field | Value |
|---|---|
| WORKSTREAM | Scope B · Workstream 3 — Universal Lineage Projection |
| MODE | **DISCOVERY ONLY.** No implementation, no repository mutation beyond this record, no architecture change, no authority created. |
| CONSTITUENT AUTHORITY | **NONE** |
| PRIOR BASELINE | `B-01` CERTIFIED · `B-02` CERTIFIED — both **unmodified** |
| BINDING PRIOR | `SCOPE-B-IDENTITY-CONTAINMENT-DETERMINATION.md` §4 — lineage composition |

---

## 1. Discovery Objective

Determine how UCOS Ω∞ answers **"How did this become this?"** today — as distinct from identity's **"What is this?"** — without creating a duplicate authority.

Every number below was measured against the repository at this baseline, not quoted.

---

## 2. Existing Lineage Inventory

| # | Artifact / Component | Owner | Purpose | Authority type | Current state |
|---|---|---|---|---|---|
| L-1 | `00-BOOK/DATA/change-ledger.json` → `lineage` | UMB-008 Change Architecture | Version ancestry: `predecessors`, `successors`, `ancestor_chain`, `descendant_chain`, `origin`, `birth` | **DERIVED PROJECTION** (`generated_at`, `generator_version`) | **1,233 nodes**; 5 with predecessors, 5 with successors |
| L-2 | `…change-ledger.json` → `change_events` | same | What happened, in order | DERIVED PROJECTION | **1,353 events**; `Created` 1,233 · `Modified` 115 · `Version-Incremented` 5 |
| L-3 | `…change-ledger.json` → `version_records` | same | `current_version`, `first_version`, `version_depth`, `content_baseline`, `history[]` | DERIVED PROJECTION | **1,233 records** |
| L-4 | `…change-ledger.json` → `evolution_timeline` | same | Ordered evolution view | DERIVED PROJECTION | **1,353 entries** |
| L-5 | `00-BOOK/DATA/artifacts.json` → `parent` | UMB-IMP-001 | **Structural containment** ancestry | **SOURCE AUTHORITY** for corpus artifacts | **1,232 / 1,233** (1 declared root) |
| L-6 | `00-BOOK/DATA/relationships.json` | UMB-006 Knowledge Graph | Typed edge graph | **DERIVED PROJECTION** (`generated_at`) | **12,899 edges**: Depends-On 4,774 · Required-By 4,697 · Parent 1,234 · Child 1,234 · Consumes/Consumed-By 316 each · Authorized-By/Authorizes 100 each · Implements/Implemented-By 48 each |
| L-7 | `00-BOOK/DATA/id-ledger.json` → `history` | UCKP-ART-05 persistence binding | Append-only content snapshots keyed by identity | **SOURCE AUTHORITY** (append-only record) | **1,264 keys, 1,470 snapshots**; depth histogram 1:1170 … 10:1 |
| L-8 | `…id-ledger.json` → `by_object.first_seen` | same | Origin commit per object | SOURCE AUTHORITY | **4,848** path-keyed records |
| L-9 | `00-MASTER/UOBC-000001/birth-ledger.json` → `parent_identity` | `UOBC-000001` | Constitutional-plane ancestry (`UOBC-F-06`) | **SOURCE AUTHORITY** | **38 births, 36 with a parent, 2 declared roots** |
| L-10 | `00-BOOK/DATA/generated-artifact-registry.json` → `producer` + `input_closure` | `UCOS-GENERATED-ARTIFACT-REGISTRY-001` | **Derivation** ancestry: what produced this, from what | **SOURCE AUTHORITY** (authored) | **345 artifacts**, each with a producer and a classified input closure |
| L-11 | `engine/nucleus/lineage.py` `LineageLedger` | `UCOS-NUC-001` | Append-only **hash-chained** lineage events; `head()`, integrity self-check | SOURCE AUTHORITY (in-memory, per-run) | Executable; not persisted |
| L-12 | `IdentifierEntry.lineage` | `UCOS-NUCLEUS-001` (B-02) | Owner/frame lineage on each assigned identifier | **DERIVED PROJECTION** | **129 of 212** entries carry lineage |
| L-13 | UGA `dependencies` / `produces` | `UCOS-UGA-001` | Object-level dependency + production edges | **DERIVED PROJECTION** | 6,094 objects: 1,923 with dependencies, 42 with produces |
| L-14 | `engine/uckp/evolution.py` Article-14 ledger | UCKP | Constitutional evolution states | SOURCE AUTHORITY | Executable |
| L-15 | `00-MASTER/UAUE-000001/UAUE-EVOLUTION-HISTORY.json` | `UAUE-000001` | Autonomous evolution history | DERIVED PROJECTION | Producer-owned |

---

## 3. Current Architecture Reality

**Three distinct ancestry relations exist, and they are correctly distinguished — not competing answers to one question:**

| Relation | Question answered | Store | Population |
|---|---|---|---|
| **Structural containment** | "what contains this?" | `artifacts.json.parent`, projected as `Parent`/`Child` edges | 1,232 |
| **Version supersession** | "what did this replace?" | `change-ledger.lineage.predecessors/successors` | **5** |
| **Derivation** | "what produced this, from what?" | `generated-artifact-registry.producer` + `input_closure` | 345 |

**`artifacts_with_predecessors: 5` is not a gap.** Measured: the only supersession chain in the corpus is `UCOS-UMB-000023 → 24 → 25 → 26 → 27 → 28`, and all five successors correctly carry `origin: UCOS-UMB-000023`. Five is the true count of superseded artifacts, not a shortfall.

**`Parent`/`Child` edges are exact inverses** — verified as a set identity over all 2,468 edges.

---

## 4. Authority Determination

The question is already answered by ratified law. `UCL-000001` stage `UCL-S-0350` "Update Universal Lineage" carries its authority verbatim:

> **"UCI-001 Part XVI.5 — lineage and evolution are DERIVED projections over recorded history; no new store is created."**
> *(authority owner: `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-UCI-001-…-STANDARD.md`)*

**DETERMINED: lineage truth is not owned by a lineage authority. It is owned, per relation, by the instrument that records the event — and every lineage view is a derived projection over those records.**

| Component | Classification |
|---|---|
| `artifacts.json` (`parent`) | **SOURCE AUTHORITY** |
| `id-ledger.json` (`history`, `first_seen`) | **SOURCE AUTHORITY** |
| `birth-ledger.json` (`parent_identity`) | **SOURCE AUTHORITY** |
| `generated-artifact-registry.json` (`producer`, `input_closure`) | **SOURCE AUTHORITY** |
| `engine/uckp/evolution.py`, `engine/nucleus/lineage.py` | **SOURCE AUTHORITY** (executable) |
| `change-ledger.json` (all four sections) | **DERIVED PROJECTION** |
| `relationships.json` | **DERIVED PROJECTION** |
| UGA `dependencies`/`produces`, `IdentifierEntry.lineage`, `UAUE-EVOLUTION-HISTORY.json` | **DERIVED PROJECTION** |
| `00-BOOK/DATA/certification.json`, UICM closure registries | **EVIDENCE ONLY** |

---

## 5. Ownership Model — Pattern B

**DETERMINED: the repository implements Pattern B — distributed governed evidence.**

```
artifacts.json · id-ledger.json · birth-ledger.json · generated-artifact-registry.json
        (multiple governed records, each owning one relation)
                              ↓
        change-ledger.json · relationships.json · UGA edges
                     (derived lineage projections)
```

Pattern A is **not** present and is **not** proposed: there is no canonical lineage source, and `UCI-001 XVI.5` forbids creating one. This is a determination of current reality, not a design selection.

---

## 6. Dependency Map

```
artifacts.json ──┬──► relationships.json (Parent/Child, Depends-On, …)
                 └──► change-ledger.json (lineage · version_records · change_events · timeline)
id-ledger.json ──────► change-ledger.json (birth, snapshot_seq, content_baseline)
generated-artifact-registry.json ──► producer/input_closure derivation chains
birth-ledger.json ───► constitutional-plane ancestry (independent of the corpus plane)
nucleus registry ────► IdentifierEntry.lineage (B-02 artifact)
```

No cycle. Every projection reads sources; no source reads a projection.

---

## 7. Duplication Findings

### F-1 — Two conflicting `Parent` edges for one child *(CONFIRMED DEFECT)*

* **Location** — `00-BOOK/DATA/relationships.json`.
  ```
  UCOS-EVOUSIS015-000002 → UCOS-USIS-000001  (note: structural:program-root)
  UCOS-EVOUSIS015-000002 → UCOS-USIS-000017  (note: metadata:PARENT)
  UCOS-EVOUSIS016-000002 → UCOS-USIS-000001  (note: structural:program-root)
  UCOS-EVOUSIS016-000002 → UCOS-USIS-000018  (note: metadata:PARENT)
  ```
  Both children declare `parent: UCOS-USIS-000001` in `artifacts.json`. The `metadata:PARENT` rule fires **exactly twice in 12,899 edges**.
* **Impact** — an ancestor-chain query over these 2 artifacts has **two answers**. 1,232 of 1,234 `Parent` edges are backed by a declared parent; **2 are not**.
* **Authority risk** — **LOW–MODERATE.** `relationships.json` is a derived projection and cannot override `artifacts.json`, which remains the source. The risk is that a *projection asserts an ancestry its source does not declare*, and nothing currently detects the divergence.

### F-2 — Two derivation rules in one generator, undeclared precedence
* **Location** — the relationships generator: `structural:program-root` (520 edges) and `metadata:PARENT` (2 edges) both emit `Parent`.
* **Impact** — no declared precedence between structural position and document metadata when they disagree.
* **Authority risk** — **LOW.** Bounded to 2 artifacts; both rules are recorded in the edge `note`, so the divergence is disclosed in the data even though nothing measures it.

### F-3 — No duplicate lineage authority found
Searched across all fifteen inventory items: **no hidden lineage store, no manual lineage declaration, no second ancestry authority.** `engine/nucleus/lineage.py` is per-run and in-memory; it persists nothing and competes with nothing. The three ancestry relations are distinct questions, not duplicate answers.

---

## 8. Verification Coverage

| Property | Coverage | Evidence |
|---|---|---|
| Lineage **correctness** (referential) | **PARTIAL** | `ukb.py:1832-1836` validates `parent` resolves to a known id — existence only |
| Lineage **consistency across stores** | **ABSENT** | Nothing compares `artifacts.json.parent` against `relationships.json` `Parent` edges. **F-1 survived 11,914 tests, which is the proof of this gap** |
| Lineage **completeness** | **ABSENT** | Nothing asserts every artifact resolves to a root, or that `ancestor_chain` is closed |
| Lineage **replay** | **PARTIAL** | `change-ledger.json` and `relationships.json` are regenerated, but `verify.sh` contains **zero** references to lineage — no dedicated stage |
| Lineage **immutability** | **PARTIAL** | `id-ledger.history` is append-only and `LineageLedger` is hash-chained with a self-check, but no gate measures either at repository scale |
| Lineage **evolution** | **PARTIAL** | UAUE covers evolution surfaces; ancestry evolution is not separately gated |

97 tests reference lineage; none performs a cross-store ancestry reconciliation.

---

## 9. Evidence Coverage

| Question | Evidence that exists | State |
|---|---|---|
| **Origin** | `id-ledger.by_object.first_seen` (4,848) · `change-ledger.lineage.birth` (1,233) · `origin` field | **STRONG** |
| **Transformation** | `change_events` (1,353) with `kind`, `from`, `to`, `snapshot_seq` | **STRONG** |
| **Derivation** | `generated-artifact-registry` `producer` + classified `input_closure` (345) | **STRONG** |
| **Ownership** | UGA `owner` 6,094/6,094 · `artifacts.json.owner` 1,233/1,233 | **STRONG** |
| **Mutation history** | `id-ledger.history` 1,470 snapshots · `version_records` with `version_depth` | **STRONG** |
| **Certification path** | `certification.json` · UAKOS `validation-record.json` · UICM closure registries | **PRESENT, not keyed on lineage** — gap `G6` (pre-existing, owned elsewhere) |

---

## 10. Identified Gaps

| ID | Gap | Class |
|---|---|---|
| **W3-G1** | No cross-store lineage consistency check; `F-1` is live and undetected | **NEW** |
| **W3-G2** | No declared precedence between the two `Parent` derivation rules | **NEW** |
| **W3-G3** | No unified query answering "how did this become this?" across the three relations and four sources — `GAP B-1` restated with measurements | **NEW** (already recorded) |
| **W3-G4** | No lineage stage in `verify.sh`; completeness and immutability unmeasured at repository scale | **NEW** |
| G6 | Certification not keyed on `universal_id`/lineage | pre-existing, out of scope |

---

## 11. Implementation Readiness Determination

**READY, with one precondition.**

* Authority is **settled and needs no decision**: `UCI-001 XVI.5` already forbids a new lineage store, and Pattern B is what exists. A lineage projection is therefore composition over four source authorities — no new authority, registry, lifecycle or evidence owner.
* Sources are **populated and measured**: 1,233 structural parents · 5 supersession chains · 345 derivation closures · 1,470 identity snapshots · 38 constitutional births.
* **Precondition:** `F-1` must be dispositioned **before** any projection is built. A unified lineage view constructed today would inherit a two-answer ancestry for 2 artifacts and would either hide the conflict or propagate it. Its disposition belongs to the owner of the relationships generator (UMB-006 / UMB-IMP-001), not to this workstream.

No implementation, no architecture change, and no artifact other than this record was produced.

---

# DISCOVERY COMPLETE
