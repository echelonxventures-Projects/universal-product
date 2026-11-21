# 07 — Engineering Lifecycle

> PROGRAM **UCOS-EG-001** · PHASE-001 · IMPLEMENTATION CONFORMANCE FRAMEWORK
> BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED — READ-ONLY)** · MODE = READ-ONLY · EVIDENCE-ONLY · FAIL-CLOSED.

---

## 0. Purpose

Define the engineering lifecycle every implementation follows from proposal to admission into Repository Truth. The lifecycle **is** UCIC-001's FROZEN 15-stage lifecycle, overlaid with EG's conformance gates (doc 02), reviews (doc 03), and admission (doc 08). EG **adds no new stage** — it binds governance checkpoints to the existing stages.

## 1. Lifecycle = UCIC-001 (consumed verbatim)

| UCIC stage | UCIC gate | EG overlay (conformance/review) |
|---|---|---|
| 1 Discovery | — | contract IC-1 drafted |
| 2 Dependency Verification | — | CG-01 (deps) · R-4 Dependency Review |
| 3 Authority Verification | READY_TO_IMPLEMENT | CG-05 · R-2 Governance Review; contract IC-2 |
| 4 Implementation | IMPLEMENTED | CG-01 · R-1 Architecture, R-3 Interface, R-7 Runtime |
| 5 Static Validation | — | CG-09 (static) |
| 6 Dynamic Validation | — | CG-09 (dynamic) |
| 7 Test Execution | — | CG-09 (tests) · CG-14 (determinism harness) |
| 8 Coverage Verification | — | CG-09/CG-12 (coverage/quality) · R-6 Quality |
| 9 Evidence Generation | VALIDATED | CG-13 · R-8 Evidence; CG-11 R-5 Security |
| 10 Certification | CERTIFIED | CG-10 · R-9 Certification (CCE ten-gate) |
| 11 Repository Intelligence Update | — | CG-03/CG-13 (registries + trace) |
| 12 Digital Twin Update | — | CG-03 (twin sync) |
| 13 Registry Update | — | CG-03/CG-04 (`ukb enforce`, Knowledge Once) |
| 14 Commit Readiness | READY_TO_COMMIT | **EG ADMISSION decision (doc 08)** |
| 15 Production Readiness | READY_FOR_PRODUCTION | Implementation Readiness Standard (doc 17) |

## 2. The Admission Point

Admission into Repository Truth is evaluated at **UCIC Stage 14 (Commit Readiness)**: an implementation is admitted iff it is CERTIFIED (UCIC Stage 10) **and** Conformant (all CG-01…14) **and** all nine reviews PASS **and** its contract (IC-1…12) is complete. This is the single gate the mission requires "before entering Repository Truth" (doc 08).

## 3. Forward-Only + REOPEN (inherited)

The lifecycle is monotonic (UCIC Output 3): forward through gates only; the sole backward transition is a defect-driven **REOPEN** (CERTIFIED/VALIDATED → ACTIVE) recorded with defect evidence (MCS-000 §05 / MCP-004). EG reviews returning FAIL trigger the same REOPEN, preserving evidence.

## 4. State Alignment

| MCS state | Engineering meaning |
|---|---|
| PLANNED → AUTHORIZED | contract declared + authorized (R-2/R-4) |
| ACTIVE → IMPLEMENTED | additive implementation (R-1/R-3/R-7) |
| VALIDATED | conformance evidence produced (CG-09/11/12/13/14; R-5/R-6/R-8) |
| CERTIFIED | CCE ten-gate PASS (CG-10; R-9) |
| ADMITTED (READY_TO_COMMIT) | **EG admission granted (doc 08)** → enters Repository Truth |

## 5. Determination

**ENGINEERING LIFECYCLE IS DEFINED AS UCIC-001 + EG OVERLAY.** It reuses the FROZEN 15-stage lifecycle without modification, binding conformance gates and reviews to the correct stages and fixing the admission point at Stage 14. No new lifecycle is created (no redesign).

*END — 07 · UCOS-EG-001 · AUTHORITY = NONE (READ-ONLY) · MODIFIES NOTHING.*
