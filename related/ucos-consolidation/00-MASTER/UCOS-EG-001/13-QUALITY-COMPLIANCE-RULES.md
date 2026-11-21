# 13 — Quality Compliance Rules

> PROGRAM **UCOS-EG-001** · PHASE-001 · IMPLEMENTATION CONFORMANCE FRAMEWORK
> BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED — READ-ONLY)** · MODE = READ-ONLY · EVIDENCE-ONLY · FAIL-CLOSED.

---

## 0. Purpose

Define quality-compliance rules an implementation SHALL satisfy (Quality Review R-6; CG-12). Consumes the Universal Architectural Quality + Testing-Quality Constitutions and the existing coverage/freeze-gate apparatus; adds no new quality model.

## 1. Quality Rules (QC)

| # | Rule | Basis | Evidence |
|---|---|---|---|
| QC-1 | Coverage meets the declared threshold (fail-closed; e.g. 100% for SEC-class) | UCIC Stage 8 | `coverage.xml` |
| QC-2 | Static analysis clean (lint + type) on source surfaces | UCIC Stage 5 | lint/type logs |
| QC-3 | All applicable tests PASS (unit/integration/functional/security) | UCIC Stage 7 | test logs |
| QC-4 | The **freeze gate** (2,847-test / 100% cov) is **preserved** (no regression) | band precedent | freeze-gate result |
| QC-5 | Quality is **measured, not asserted** (decidable, evidence-backed) | Quality Constitution; UMA doc 16 | quality metrics |
| QC-6 | Thresholds are declared in the contract (IC-9/IC-10) and honored | doc 04 | threshold record |
| QC-7 | No quality regression across the repository (determinism preserved) | CG-14 | regression check |

## 2. Measured, Not Opinion

Quality is a set of registered, deterministic checks (coverage, lint, type, test-pass, freeze-gate preservation) — never subjective judgment. This aligns with UMA's Quality Model (metric 3.12): a check that cannot be computed deterministically from evidence is inadmissible.

## 3. Threshold Governance

Thresholds (e.g., SEC-class 100% coverage) are declared per implementation in the contract (IC-10) and are versioned governed data — not ad hoc. R-6 confirms the declared threshold is met; a lower-than-declared result is a FAIL (fail-closed).

## 4. Fail-Closed Conditions

| Condition | Result |
|---|---|
| Coverage below declared threshold | CG-12 FAIL → DENY |
| Lint/type errors on source | QC-2 FAIL → DENY |
| Any failing test | QC-3 FAIL → DENY |
| Freeze-gate regression | QC-4 FAIL → DENY |
| Quality asserted without measurement | QC-5 FAIL → DENY |

## 5. Determination

**QUALITY COMPLIANCE RULES ARE DEFINED (QC-1…QC-7, fail-closed).** They require measured (not asserted) quality, declared-threshold coverage, clean static analysis, passing tests, and freeze-gate preservation — consuming the existing quality apparatus without redefining it.

*END — 13 · UCOS-EG-001 · AUTHORITY = NONE (READ-ONLY) · MODIFIES NOTHING.*
