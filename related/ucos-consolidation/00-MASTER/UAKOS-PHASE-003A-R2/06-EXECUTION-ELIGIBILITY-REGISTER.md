# 06 — Execution Eligibility Register

> PROGRAM **UAKOS PHASE-003A-R2** — Universal Realization-Aware Implementation Gap Regeneration · baseline `57d91b7` (branch `governance-reconciliation`) · regenerates the Constitutional Gap Baseline **exclusively** from **FREEZE C2** (`f966c8e0…4668f`) · AUTHORITY = **NONE (DERIVED)** · **READ-ONLY** · derived `2026-07-23`.
>
> Which realization action each realization type is eligible for. Only software-bearing types are eligible for software implementation; every other type completes via ratification, population, or documentation. Reproduces the FREEZE C2 eligibility model against the regenerated baseline.

## Eligibility matrix (23 types, 431 objects)

| Realization type | Objects | SW-impl | Gov-ratify | Reg-populate | Doc-complete | Runtime-deploy | Certify | Validate |
|---|---|---|---|---|---|---|---|---|
| ADMISSION_GATE | 5 | · | ✓ | · | · | · | · | · |
| APPLICATION | 21 | ✓ | · | · | · | ✓ | ✓ | ✓ |
| ARCHITECTURE_SPECIFICATION | 22 | · | · | · | ✓ | · | · | · |
| CONSTITUTIONAL_EVIDENCE_PRINCIPLE | 11 | · | ✓ | · | · | · | · | · |
| CONSTITUTIONAL_EVOLUTION_PROPOSAL | 12 | · | ✓ | · | · | · | · | · |
| CONSTITUTIONAL_FOUNDATION | 6 | · | ✓ | · | · | · | ✓ | · |
| CONSTITUTIONAL_LAW | 21 | · | ✓ | · | · | · | · | · |
| DATA_MODEL | 20 | ✓ | · | · | · | · | ✓ | ✓ |
| EXECUTION_BAND_UNIT | 53 | · | · | ✓ | · | · | ✓ | ✓ |
| GOVERNANCE_DECISION | 3 | · | ✓ | · | · | · | · | · |
| GOVERNANCE_DETERMINATION | 18 | · | ✓ | · | · | · | · | · |
| INFRASTRUCTURE_COMPONENT | 19 | ✓ | · | · | · | ✓ | ✓ | ✓ |
| LIFECYCLE_PHASE | 9 | · | · | · | ✓ | · | · | · |
| MASTER_CONTEXT_PROTOCOL | 9 | · | · | ✓ | · | · | · | · |
| META_MODEL | 91 | · | · | ✓ | · | · | · | · |
| ONTOLOGY | 24 | · | · | ✓ | · | · | · | · |
| PLATFORM_COMPONENT | 19 | ✓ | · | · | · | ✓ | ✓ | ✓ |
| PROGRAM_EPIC | 10 | · | · | · | ✓ | · | · | · |
| RATIFICATION_DETERMINATION | 2 | · | ✓ | · | · | · | · | · |
| RECONCILIATION_DETERMINATION | 4 | · | ✓ | · | · | · | · | · |
| RUNTIME_COMPONENT | 16 | ✓ | · | · | · | ✓ | ✓ | ✓ |
| SERVICE | 19 | ✓ | · | · | · | ✓ | ✓ | ✓ |
| SOFTWARE_ENGINE | 17 | ✓ | · | · | · | · | ✓ | ✓ |
| **Total** | **431** | | | | | | | |

## Eligibility rollup

| Realization action | Eligible types | Eligible objects | Open work under FREEZE C3 |
|---|---|---|---|
| Software implementation | APPLICATION, DATA_MODEL, INFRASTRUCTURE_COMPONENT, PLATFORM_COMPONENT, RUNTIME_COMPONENT, SERVICE, SOFTWARE_ENGINE | 131 | 47 IMPLEMENTATION_GAP + 21 CERTIFICATION_GAP |
| Governance ratification | ADMISSION_GATE, CONSTITUTIONAL_EVIDENCE_PRINCIPLE, CONSTITUTIONAL_EVOLUTION_PROPOSAL, CONSTITUTIONAL_FOUNDATION, CONSTITUTIONAL_LAW, GOVERNANCE_DECISION, GOVERNANCE_DETERMINATION, RATIFICATION_DETERMINATION, RECONCILIATION_DETERMINATION | 82 | 43 RATIFICATION_GAP |
| Registry / knowledge population | EXECUTION_BAND_UNIT, MASTER_CONTEXT_PROTOCOL, META_MODEL, ONTOLOGY | 177 | 7 POPULATION_GAP |
| Documentation completion | ARCHITECTURE_SPECIFICATION, LIFECYCLE_PHASE, PROGRAM_EPIC | 41 | 0 |
| **Total** | | **431** | **118 open** |

## Eligibility invariants (SUCCESS CRITERIA)

- Software-implementation-eligible objects: **131** (software-bearing types only). All 47 IMPLEMENTATION_GAP and 21 CERTIFICATION_GAP objects fall inside this set — **0** implementation/certification gaps outside software-eligible types.
- Non-software-bearing types eligible for software implementation: **0**.
- Every RATIFICATION_GAP object is Gov-ratify eligible: **43/43**.
- Every POPULATION_GAP object is Reg-populate eligible: **7/7**.
- No object is eligible for a realization action outside its lifecycle.

_READ-ONLY: derived from FREEZE C2 only. No repository code, constitution, prior freeze, or knowledge object was modified or created._
