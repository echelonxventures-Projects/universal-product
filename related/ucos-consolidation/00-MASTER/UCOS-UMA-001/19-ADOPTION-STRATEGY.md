# 19 — Adoption Strategy

> PROGRAM **UCOS-UMA-001** · PHASE-001 · UNIVERSAL MEASUREMENT AUTHORITY
> BASELINE `b67a720` · AUTHORITY = **NONE (DESIGN ONLY)** · MODE = DESIGN-ONLY · NON-IMPLEMENTING · FAIL-CLOSED.

---

## 0. Purpose

Define how the ecosystem *adopts* UMA as the standing measurement authority: how each consumer (Closure, Validation, Certification, Governance, Digital Twin) transitions to consuming UMA, what "adopted" means, and how adoption is itself measured (by UMA).

## 1. Adoption Principle

> **A consumer has adopted UMA when it no longer produces its own measurements and instead cites a sealed UMA `result_id` for every quantitative claim.**

Adoption is not "UMA exists"; it is "no measurement is produced outside UMA." The success criterion of the whole program (mission) is reached only when this holds across all consumers.

## 2. Consumer-by-Consumer Adoption

| Consumer | Before | After adoption | Adoption evidence |
|---|---|---|---|
| **Closure Programs** | run `closure_engine.py`, read `closure.json` | call `MeasureCoverage/Completeness/Assimilation`; cite result_id in the determination | determination artifact references a UMA result_id |
| **Validation** | ad hoc coverage | call `MeasureValidation` | validation record cites result_id |
| **Certification** | bespoke metric gathering | call `MeasureCertification` bundle | certificate cites result_id + registry_version |
| **Governance** | manual dashboards | call `MeasureGovernance/RepositoryHealth` | governance review cites result_id |
| **Digital Twin** | independent counts | subscribe to sealed metrics | twin renders UMA result_ids |

## 3. Adoption Phases (per consumer)

```
AWARE ─► INTEGRATED (calls API in shadow) ─► DEPENDENT (decisions cite UMA) ─► EXCLUSIVE (no self-measurement)
```

Only at **EXCLUSIVE** is the constitutional goal met for that consumer: "No Closure Program shall own measurement again."

## 4. Adoption is Self-Measured

UMA measures its own adoption via a registered metric:

```
AdoptionRatio = consumers_at_EXCLUSIVE ÷ total_measurement_consumers
```

- Fail-closed: any consumer still self-measuring ⇒ AdoptionRatio < 1 ⇒ program success criterion NOT met.
- This makes adoption an evidenced determination (doc 20), not a claim.

## 5. Enablement (non-code)

- **Contracts published:** doc 09 API + doc 04 envelope are the integration surface; consumers code against contracts.
- **Seed registries available:** consumers immediately get parity coverage (doc 18 M0/M2).
- **Replay tooling:** `ReplayResult` lets any consumer independently verify a cited result — building trust needed for EXCLUSIVE adoption.
- **Governance onboarding:** registering a consumer's needed metrics/namespaces is a governed control-plane event (doc 13).

## 6. Incentives & Guardrails

| Incentive | Mechanism |
|---|---|
| Less duplicated code | consumers delete bespoke measurement logic |
| Trust via replay | cited results are independently reproducible |
| Visibility of gaps | UNCOVERED ledger exposes blind spots consumers previously hid |
| Guardrail | Certification refuses to sign a determination not backed by a UMA result_id (fail-closed adoption gate) |

## 7. Adoption Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Consumer keeps a shadow counter "just in case" | AdoptionRatio metric surfaces it; governance gate |
| New program reinvents measurement | Constitution (doc 01) prohibits; Certification gate enforces |
| Registry lag (new namespace not yet registered) | Discovery proposal workflow (doc 13) + PARTIAL visibility, never silent |

## 8. Definition of Done (adoption)

Adoption is complete when: AdoptionRatio = 1 · every consumer determination cites a UMA result_id · no measurement-producing code exists outside UMA · Certification gate active. Doc 20 assesses readiness for this end-state.

## 9. Dependency Determination

- Adoption drives the RETAIN-as-consumer half of every Dependency Register entry (doc 10 §5) to completion. It modifies no artifact; it is the behavioral contract consumers voluntarily meet under governance.

*END — 19 · UCOS-UMA-001 · AUTHORITY = NONE (DESIGN ONLY) · MODIFIES NOTHING.*
