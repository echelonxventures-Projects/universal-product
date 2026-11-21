# Output 9 — Ownership Inventory

> **STATUS DOMAIN:** GOVERNANCE (measurement) · **STATUS BASIS:** `00-CMG/CMG-REGISTRY.json` → `concerns[]` parsed at HEAD `9de85ad`, consumed per `CMG-000001` XX.7 which directs instruments to consume located ownership records and not restate them

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000007` · OUTPUT 9 |
| AUTHORITY | **NONE — DERIVED TRUTH** |
| SUBJECT | The concern → owner allocation as located. Constitutional meta-facts about the owners → Output 3. |
| EVIDENCE | `evidence/cmg-ucda-rie.txt` |

---

## 1. Ownership rules being measured

`CMG-000001` XIV.3 makes Concern the pivot of the ontology; XIV.2 fixes `Concern → Owner` at **N:1** under `CMG-INV-02`; XIV.4 requires every Concern to be named, atomic and non-overlapping. XX.3 requires ownership to be discoverable from the Registry without reading the owning artifact. XX.7 names the located ownership records — the canonical ownership matrix, the concept-ownership register, the canonical-home register and the artifact registry — as the ownership facts, to be consumed and never restated.

| Fact | Measured | Method |
|---|---|---|
| Concerns allocated | **60** | M-2 |
| Delegated (`REUSE`) | **49** | M-2 |
| Retained by `CMG-000001` (`RETAIN`) | **11** | M-2 |
| Concerns with more than one owner | **0** — `CMG-INV-02` holds | M-4 |
| Findings from the meta-constitutional gate | **0** | M-3 |

## 2. Delegated concerns (49) — concern → owner

| Id | Concern | Owner |
|---|---|---|
| CMG-DLG-01 | constitutional-engineering-process-and-program-authority | `CEP-000` |
| CMG-DLG-02 | governance-operation-jurisdiction-ownership-assignment-escalation-and-conflict-resolution | `CEP-002` |
| CMG-DLG-03 | execution-operation | `CEP-003` |
| CMG-DLG-04 | validation-operation | `CEP-004` |
| CMG-DLG-05 | certification-operation | `CEP-005` |
| CMG-DLG-06 | ratification-operation-and-finality | `CEP-006` |
| CMG-DLG-07 | freeze-immutability-baselines-and-supersession-mechanics | `CEP-007` |
| CMG-DLG-08 | evidence-and-traceability-operation | `CEP-008` |
| CMG-DLG-09 | amendment-and-evolution-operation | `CEP-009` |
| CMG-DLG-10 | compliance-monitoring-and-assurance-operation | `CEP-010` |
| CMG-DLG-11 | audit-operation-drift-and-contradiction-detection | `CEP-010` |
| CMG-DLG-12 | constitutional-interpretation | `AUTH-INF-001` |
| CMG-DLG-13 | artifact-registration-identity-allocation-and-classification | `REG-AUTO-001` |
| CMG-DLG-14 | status-determination-and-validity | `STATUS-001` |
| CMG-DLG-15 | change-intelligence-regeneration-and-synchronization | `UCI-001` |
| CMG-DLG-16 | governance-integration-and-execution-architecture | `GOV-INT-001` |
| CMG-DLG-17 | repository-truth-knowledge-content-and-canonical-homes | `UCOS-BOOK-000000` |
| CMG-DLG-18 | repository-closure-specification | `CONST-01` |
| CMG-DLG-19 | successor-governance-and-program-remit-separation | `CONST-07` |
| CMG-DLG-20 | long-term-evolution-admissible-path-for-architectural-ideas | `CONST-10` |
| CMG-DLG-21 | constitutional-glossary-and-frozen-terminology | `CONST-11` |
| CMG-DLG-22 | architecture-baseline-change-control | `AB-001-07` |
| CMG-DLG-23 | engineering-governance-and-implementation-admission | `EG-001-01` |
| CMG-DLG-24 | measurement-authority | `UMA-001-01` |
| CMG-DLG-25 | technology-selection-and-constraint | `TECH-CONST-001` |
| CMG-DLG-26 | nucleus-and-universe-composition-model | `NUCLEUS-001-02` |
| CMG-DLG-27…33 | domain-substance: data · runtime · application · infrastructure · service · platform · security | `DATA-001` · `RUNTIME-001` · `APPLICATION-001` · `INFRASTRUCTURE-001` · `SERVICE-001` · `PLATFORM-001` · `SECURITY-001` |
| CMG-DLG-34 | canonical-runtime-catalog-model | `CAT-000` |
| CMG-DLG-35 | universal-reference-architecture-model | `REF-000` |
| CMG-DLG-36 | generation-frameworks | `05-GENERATION` (zone) |
| CMG-DLG-37 | implementation-orchestration-and-realization | `06-IMPLEMENTATION` (zone) |
| CMG-DLG-38 | engineering-foundation-identity-object-type-and-relationship-architectures | four `07-ENGINEERING/` instruments |
| CMG-DLG-39 | intelligence-substrate-sciences-universes-and-intelligence-registries | `15-UNIVERSAL-SCIENCE-INTELLIGENCE` (zone) |
| CMG-DLG-40 | enforcement-machinery-gates-and-guards | located enforcement chain: `Makefile` · `verify.sh` · `repo-ops.sh` · `ukb.py` · `register.sh` · 3 workflows |
| CMG-DLG-41…47 | repository-integrity · vision-assimilation · architectural-completeness-as-distinct-from-closure · repository-state-machine · closure-metrics-computation · single-canonical-closure-pipeline · repository-lifecycle | `CONST-02` · `CONST-03` · `CONST-04` · `CONST-05` · `CONST-06` · `CONST-08` · `CONST-09` |
| CMG-DLG-48 | constitutional-engineering-operational-law-invariants-and-artifact-state-model | `CEP-001` |
| CMG-DLG-49 | deferral-register-lifecycle-states-entry-exit-review-cadence-and-custody | `CEP-002` |

## 3. Retained concerns (11) — owner `CMG-000001`

`CMG-RET-01` definition of constitution · `-02` recognition and the Constitution Registry · `-03` classification taxonomy and ontology · `-04` precedence lattice and authority resolution · `-05` allocation of concerns to owners and the delegation register · `-06` recording of vacancies, gaps and open questions · `-07` meta-level identity, identifier and namespace rules · `-08` meta-lifecycle phase model · `-09` admission of new constitutional kinds and unknown future concepts · `-10` meta-constitutional completeness verification and readiness criteria · `-11` meta-constitutional invariants and their mechanical verification.

`CMG-000001` XVIII.1 states delegation here is **recognition, not transfer**: each entry reads *"this concern is already owned by X, and this instrument binds to X"*.

## 4. Located ownership records (consumed, not restated)

| Record | Path | Role as declared |
|---|---|---|
| Canonical Ownership Matrix | `/02-CANONICAL-OWNERSHIP-MATRIX.md` *(repository root)* | single canonical owner per concept domain; `duplicate_canonical_homes = 0`, `orphan_concepts = 0` |
| Architectural Decision Assimilation Matrix | `/03-ARCHITECTURAL-DECISION-ASSIMILATION-MATRIX.md` *(repository root)* | integration method per decision (REUSE/EXTEND/MERGE/REFERENCE/NEW) |
| Artifact Registry | `00-BOOK/DATA/artifacts.json` | per-artifact `owner` field over 1,199 artifacts |
| Canonical-home register | `00-MASTER/UAKOS-CLOSURE-002` outputs | concept → canonical home |

## 5. A measured tension in the ownership records

`CMG-000001` XX.8 states that the `AUTHORITY = NONE (DERIVED TRUTH)` convention declares **no ownership**, and that *"a derived-truth artifact owns no concern and SHALL NOT appear as an Owner in the Registry."*

Measured: four owners in §2 declare `AUTHORITY = NONE` in their own header tables — `STATUS-001` (CMG-DLG-14), `REG-AUTO-001` (CMG-DLG-13), `UCI-001` (CMG-DLG-15) and `GOV-INT-001` (CMG-DLG-16) — and all four appear as Owner in the Registry (M-2 + M-3).

`CMG-000001` XX.7 provides that a disagreement among located ownership records **is a finding under Article LII to be disposed by the owner of the affected concern, never by `CMG-000001`** — and, by the same reasoning, never by this measuring programme. Recorded as `DG-6` in `13-KNOWN-GAPS.md`. Not resolved here.

## 6. Decision ownership (measured, not evaluated)

| Fact | Value | Source |
|---|---|---|
| Located decision registers (`CEP-002` Art 28.3) | 5: `02-MASTER/UCOS-Ω∞-CONSTITUTIONAL-DECISION-REGISTER.md` · `adr/` · `knowledge/decisions.json` · `/03-ARCHITECTURAL-DECISION-ASSIMILATION-MATRIX.md` *(repository root)* · `00-MASTER/MCP-004-MASTER-DECISIONS.md` | M-2 |
| Decisions carrying a disposition | **64**, 0 undispositioned, 0 conversation-only | M-3 (`ucda.json`) |
| Disposition distribution | REPRESENTED-BY-EXISTING-CANONICAL-CAPABILITY 28 · IMPLEMENTED 22 · REGISTERED-AS-IMPLEMENTATION-WORK-PACKAGE 8 · SUPERSEDED 4 · REJECTED-WITH-CONSTITUTIONAL-JUSTIFICATION 2 | M-3 |
| Lifecycle occupancy | REPOSITORY-TRUTH-UPDATE 28 · REPOSITORY-MAPPING 26 · CLOSURE 10 | M-3 |
| Evidence references resolved | **205** | M-3 |
| A second decision register | **PROHIBITED** by `CEP-002` Art 28.3 | M-2 |

---

*`UCCEP-000007` Output 9. AUTHORITY = NONE (DERIVED TRUTH). Consumes located ownership records; allocates nothing. `CERTIFIED-PROVISIONAL`; Tier T1 VACANT.*
