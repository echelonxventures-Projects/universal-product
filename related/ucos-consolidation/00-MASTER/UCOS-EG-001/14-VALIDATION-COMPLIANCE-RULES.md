# 14 — Validation Compliance Rules

> PROGRAM **UCOS-EG-001** · PHASE-001 · IMPLEMENTATION CONFORMANCE FRAMEWORK
> BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED — READ-ONLY)** · MODE = READ-ONLY · EVIDENCE-ONLY · FAIL-CLOSED.

---

## 0. Purpose

Define validation-compliance rules an implementation SHALL satisfy (CG-09; part of R-6/R-8). Consumes CEP-004 (Validation Constitution), the EC-1 ValidationEngine, and UCIC-001 Stages 5–9; adds no new validation model. Validation ≠ Certification (CONST-01 §3): validation proves structural/behavioral correctness; certification signs it (doc 15).

## 1. Validation Rules (VC)

| # | Rule | UCIC stage | Evidence |
|---|---|---|---|
| VC-1 | **Static validation** PASS (lint + type + `ukb validate` structural/referential/append-only) | 5 | static logs |
| VC-2 | **Dynamic validation** PASS (build/compile + runtime smoke) | 6 | build/smoke log |
| VC-3 | **Test execution** PASS (0 failed; determinism harness where applicable) | 7 | test logs |
| VC-4 | **Coverage verification** meets declared threshold | 8 | coverage report |
| VC-5 | **Evidence generation** — required bundle physically present | 9 | evidence bundle |
| VC-6 | Validation performed by the **EC-1 ValidationEngine** (accepted verdict) | 5–9 | validation record |
| VC-7 | Validation is **deterministic** (re-run reproduces verdict) | 5–9; CG-14 | determinism evidence |

## 2. Validation ≠ Certification

Validation (this doc, CG-09) establishes correctness evidence; **certification** (doc 15, CG-10) is the independent signed determination consuming that evidence. EG keeps them distinct (Prohibition of Conflation): passing validation does not imply certification; certification requires validation to have passed first (UCIC gate ordering VALIDATED → CERTIFIED).

## 3. Fail-Closed Conditions

| Condition | Result |
|---|---|
| Any static/dynamic/test failure | CG-09 FAIL → back to IMPLEMENTED (fail-forward) |
| Coverage below threshold | CG-09 FAIL → add tests |
| Missing evidence bundle | VALIDATED gate not reached → DENY |
| Non-deterministic validation | CG-14 FAIL → DENY |

## 4. Authority Boundary

EG requires validation to be produced by the existing validation authority (CEP-004 / EC-1); EG does **not** perform or redefine validation. EG confirms the validation *evidence* exists and passed (R-6/R-8) as a precondition to admission.

## 5. Determination

**VALIDATION COMPLIANCE RULES ARE DEFINED (VC-1…VC-7, fail-closed).** They require static+dynamic+test+coverage+evidence validation via CEP-004/EC-1 across UCIC Stages 5–9, kept distinct from certification, consuming the existing validation apparatus without redefining it.

*END — 14 · UCOS-EG-001 · AUTHORITY = NONE (READ-ONLY) · MODIFIES NOTHING.*
