# UICM — Universal Implementation Closure Matrix · Context Assimilation Report

**Artifact:** `UICM-CONTEXT-ASSIMILATION-REPORT`
**Programme:** UCOS-UICM-000001
**Authority:** NONE — DERIVED TRUTH. This report legislates nothing and creates no capability.
**Determinism:** every row cites a located file. No claim rests on recollection.
**Disposition:** ASSIMILATION ONLY. Nothing is implemented here.

---

## 1. What this report settles

Before any UICM module exists, this report answers one question for each capability UICM
would otherwise be tempted to build: **who already owns it?** Every row therefore ends in
a reuse decision, and `CREATE` appears only where discovery located no owner.

The constraint this discharges is not stylistic. `CMG-INV-02` forbids parallel authority
and `CMG-L-14` forbids parallel machinery; `engine/uckp/validation.py`
`_probe_zero_duplication` enforces non-duplication of the canonical primitive by AST scan
over every module in `engine` and `platform`. A UICM that re-implemented hashing, identity
minting, registration or certification would not merely be redundant — it would fail a
live gate.

## 2. Assimilation result

| # | Capability UICM needs | Canonical owner | Existing implementation | Reuse decision | Gap identified |
|---:|---|---|---|---|---|
| 1 | Canonical serialization + content digest | UCKP Layer Zero (UCKP-LAW-0001 Art-13) | `engine/uckp/canonical.py` — `canonical_json`, `canonical_bytes`, `content_hash`, `digests_match` | **REUSE AS-IS** (import; adding a second definition is a measured violation) | None |
| 2 | Deterministic universal identity + kind vocabulary | Universal Registry Platform | `engine/registry/universal/identity.py` — `deterministic_id`, `RegistryKind` (31 kinds), `register_kind` extension point | **REUSE AS-IS** — extend by registration, never by editing the enum | None |
| 3 | Capability identity | UKDA canonical knowledge | `knowledge/canonical-knowledge.json` — 122 `UCKO-CAP-*` rows, universe `CAPABILITY`; producer `engine/knowledge/capability.py` | **REUSE AS-IS** — UICM reads `cko_id`/`owner`; mints no capability id | None |
| 4 | Artifact identity over the version-controlled boundary | UCOS-UGA-001 | `00-MASTER/UCOS-UGA-001/01-EXECUTABLE-OBJECT-REGISTRY.json` — 4,603 entries with `universal_id`, `owner`, `content_hash`, `certification_status` | **REUSE AS-IS** — UICM reads identity; mints none | 2 tracked `engine/uckp` artifacts absent from the registry (drift against UGA-INV-01) |
| 5 | Implementation intelligence per capability | UCOS-RIE-001 | `intelligence/UCOS-RIE-CAPABILITY-CATALOG.json` — 122 rows, `implementation_status`, `reuse`, `replacement_prohibited` | **REUSE AS DATA** — `engine` may not import `intelligence`; the catalogue is read as JSON | None |
| 6 | Write-side registration, version chains, dedup, audit journal | Universal Registry Platform | `engine/registry/universal/` — `RegistryCore`, 12 typed registries, `AuditJournal` | **REFERENCE ONLY** — UICM opens no registry | None |
| 7 | Read-side Registry Truth | Registry Adapter | `engine/registry/adapter.py` — `RegistryAdapter.open`, `registry.read` contract | **REFERENCE ONLY** | None |
| 8 | Ownership law (capabilities belong to Nuclei) | UCOS-NUC-001 | `engine/nucleus/` — `ownership.py`, `ROLE_KINDS`, `derive_role` | **REUSE** for the ownership question; UICM asserts no ownership | None |
| 9 | Human-authoritative ownership rows | `02-CANONICAL-OWNERSHIP-MATRIX.md` §2 | 4-column markdown table, ~55 rows | **REFERENCE ONLY** — §5 of that file records the rows are *"unreadable by machine"*; UICM must not parse them or treat a derived reading as overriding them | Ownership §2 has no machine crosswalk to `UCKO-CAP-*` |
| 10 | Runtime-unit validation checks | Validation Layer (EPIC-007) | `engine/validation/` — 7 checks, `ValidationEngine`, `ValidationReport` | **REFERENCE ONLY** — different subject (a runtime unit, not a capability) | No validation engine takes a *capability* as its subject |
| 11 | Certification of a validation | Certification Layer (EPIC-008) | `engine/certification/` — `CertificationEngine`, `CertificationRecord`, hash-chained ledger | **REFERENCE ONLY** — subject is a validation report | — |
| 12 | Certification of arbitrary validation + measurement + truth | Universal Certification Engine (UCOS-EPIC-006) | `engine/universal_certification/` — `UniversalCertificationEngine`, `Certificate`, `ComplianceEngine`, `ApprovalWorkflow`, `Measurement`/`MeasurementComparator` | **REUSE** — this is the certifier UICM feeds; UICM supplies the three declared inputs and asserts no verdict of its own | None |
| 13 | Repository-level acceptance gates | EPIC-VAL-002 | `engine/acceptance/gates.py` — 16 gates incl. `ZeroMissingGate`, `ZeroDuplicationGate`, `CoverageGate`, `OwnershipGate` | **REUSE** the gate vocabulary; UICM adds no second acceptance engine | Gates take a `RepositorySubject`, not a per-capability closure matrix |
| 14 | Composition of validation → certification → acceptance | EPIC-VAL-003 | `engine/governance/pipeline.py` — `RepositoryGovernancePipeline` | **REUSE AS PATTERN** — composition over creation is the precedent UICM's controller follows | None |
| 15 | Generic measurement kernel + gap types | UCOS-UMA-001 | `platform/measurement/contracts.py` (`MeasurementKind` = ENUMERATION/METRIC/COVERAGE/GAP), `gaps.py` | **REUSE** the measurement contract and the disjoint measurement-identity rule | Gap types are structural/completeness over the Registry population, not closure dimensions |
| 16 | Hermetic environment + double-build reproducibility | EPIC-004 | `engine/determinism/` — `hermetic_env().apply()`, `double_build`, `compare_builds`, `HermeticEnvironment.order` | **REUSE** for the determinism dimension | No per-capability determinism obligation exists — 54 of 62 capabilities have none |
| 17 | Replay / fixed-point convergence | UCOS-ARE-000001 + per-programme `--replay` | `engine/constitution/replay.py` (`converge`, `require_fixed_point`), `engine/uaue/gate.py --replay` | **REUSE AS PATTERN** — byte replay of rendered registers | — |
| 18 | The 15-stage capability lifecycle | UCIC-001 | `00-MASTER/UCIC-001-UNIVERSAL-CAPABILITY-IMPLEMENTATION-CONTRACT.md`; projected in `UAKOS-CLOSURE-009/requirements.json` `lifecycle_dimensions` | **REUSE — BIND, DO NOT FORK** — UCIC-001 already owns "the single deterministic lifecycle every capability follows"; a second lifecycle was already REFUSED once (Ω-E04) | UICM's 17 closure dimensions must crosswalk to UCIC-001's 15 stages rather than replace them |
| 19 | The 15-stage evolution cycle | UCKP Article 14 | `engine/uckp/evolution.py` — `EvolutionStage`, `EvolutionLedger` | **REFERENCE ONLY** — `engine/uaue` reads it rather than duplicating it; UICM does the same | None |
| 20 | Concept-level closure measurement | UAKOS-CLOSURE-002 | `00-MASTER/UAKOS-CLOSURE-002/closure_engine.py` + `closure.json` (549 concepts, dispositions, 5 traceability tiers, typed gap map) | **REUSE AS-IS** — the *concept* closure layer; UICM does not re-measure concepts | Subject is a concept, never a capability × dimension cell |
| 21 | Requirement maturity lattice | UAKOS-CLOSURE-009 | `requirement_engine.py` `LATTICE` M0–M7; `gap_classes[]`, `baseline_conditions[]` schemas | **REUSE AS-IS** for maturity; reuse the gap-row schema shape | `lifecycle_dimensions` is measured repository-wide, **not per capability** |
| 22 | Capability discovery from the eligibility boundary | UCOS-RIE-001 | `intelligence/rie/discovery.py::discover()` | **REUSE AS DATA** | Unit of capability is the Python package; the ~40 `00-MASTER/*_engine.py` files collapse into one `00-MASTER` row |
| 23 | Reuse-before-create determination | UKIP | `engine/knowledge/integration/reuse.py` `ReuseEngine`; `engine/ceu/sufficiency.py` `assess` | **REUSE AS-IS** — this report is its output | None |
| 24 | Contract publication | Foundation Layer 1 | `engine/foundation/contracts/contract.py` — `Contract`, `Version`, `ContractRegistry` | **REUSE AS-IS** — UICM publishes one `Contract` | None |
| 25 | EC-1 provisional-state disclosure | `DE-05` | `engine/foundation/contracts/disclosure.py` — `build_disclosure`, `disclosure_present` | **REUSE AS-IS** | None |
| 26 | Hash-chained append-only ledger | five existing homes | `engine/registry/universal/audit.py`, `engine/certification/ledger.py`, `engine/universal_certification/audit.py` + `approval.py`, `engine/context/registry.py` | **REUSE the nearest** — a sixth implementation is the duplication Article 3 forbids | None |
| 27 | Identifier families / closed enumerations | CMG-000001 | `00-CMG/CMG-REGISTRY.json` | **REFERENCE ONLY** — UICM is SUBSTANTIVE, so `CMG` Art LXXVI.2(b) forbids it a namespace token; it must *measure* that absence | None |
| 28 | **Capability × closure-dimension matrix** | — | **none located** | **CREATE** | This is the only genuine gap. No artifact anywhere crosses capability × dimension into one grid |
| 29 | **Capability-keyed closure obligation register** | — | **none located** | **CREATE** | Existing registers are keyed by gap class (`RG-A01`) or condition (`BC-01`), never by capability |
| 30 | **Closure state machine (CLOSED/OPEN/BLOCKED/UNKNOWN) with the three closure rules** | — | **none located** | **CREATE** | No enum with these four members exists; nearest analogues are UAUE `EXIT_CLOSED`/`GateReport.open` and UCKP `SATISFIED`/`VIOLATED`/`UNMEASURED` |

## 3. Reuse summary

| Decision | Count | Meaning |
|---|---:|---|
| REUSE AS-IS | 10 | imported or read; UICM adds nothing |
| REUSE (bind / as pattern / as data) | 9 | consumed under a stated constraint |
| REFERENCE ONLY | 8 | cited, never invoked as authority |
| **CREATE** | **3** | the matrix, the capability-keyed obligation register, the closure state machine |

Twenty-seven of thirty capabilities are discharged by an existing owner. The three
`CREATE` rows are the entire justification for UICM's existence: without them there is no
artifact in the repository that answers *"is capability X closed on dimension Y?"*, and
with them UICM still owns no registry, no identity and no governance.

## 4. Constraints UICM inherits

1. **AUTHORITY = NONE — DERIVED TRUTH.** Where a UICM measurement and a located
   instrument differ, the located instrument governs and UICM records a referred finding
   (`UICM-F-###`) rather than editing the other owner's claim.
2. **No namespace token.** UICM is SUBSTANTIVE, so it claims nothing in
   `00-CMG/CMG-REGISTRY.json` and must measure that absence.
3. **Zero enumeration.** No dimension list, capability list, state list or root list may
   live in executable string constants. Every one is read from `uicm.json`.
4. **Zero hard-coded exceptions.** No capability, dimension or gap may be exempted by
   name anywhere in the engine.
5. **`engine` must not import `intelligence`.** The RIE catalogue is consumed as JSON.
6. **Repository Truth = Runtime Truth.** Committed registers must be the byte-exact
   product of the declaration plus tracked content, verified by `--replay`.
7. **No wall clock, no commit identity, no working-tree status** in any emitted byte.
8. **Fail closed.** A probe that cannot execute reports UNKNOWN, and UNKNOWN can never
   become a pass.

## 5. Determination

**ASSIMILATION COMPLETE.** Ninety percent of what UICM needs already exists and is owned.
UICM is admitted as a **measurement and certification layer only**, on three CREATE rows,
consuming the canonical owners named above.

Proceed to population discovery (`UICM-POPULATION-DISCOVERY-REPORT`), then to
implementation.
