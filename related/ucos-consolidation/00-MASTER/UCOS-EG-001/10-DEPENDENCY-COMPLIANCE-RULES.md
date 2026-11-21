# 10 — Dependency Compliance Rules

> PROGRAM **UCOS-EG-001** · PHASE-001 · IMPLEMENTATION CONFORMANCE FRAMEWORK
> BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED — READ-ONLY)** · MODE = READ-ONLY · EVIDENCE-ONLY · FAIL-CLOSED.

---

## 0. Purpose

Define the dependency-compliance rules an implementation SHALL satisfy (Dependency Review R-4; part of CG-01). Consumes the AB-001 dependency graph (doc 05) and UCIC-001 Stage 2; adds no new dependency model.

## 1. Dependency Rules (DC)

| # | Rule | Enforcement | Evidence |
|---|---|---|---|
| DC-1 | Every dependency is in a **terminal-success** state (CERTIFIED/FROZEN) | UCIC Stage 2 | dependency-satisfaction record |
| DC-2 | The dependency graph is **acyclic** (CIOA-enforced; three-colour DFS) | AB-001 doc 05; band precedent | acyclicity proof |
| DC-3 | Reuse is **by reference** (ENG-005); **no redefinition** of a dependency | AB-001 FD-07 | reference-only diff |
| DC-4 | Dependencies respect the **downward-only realization spine** (EL-1→…→Band-13) | AB-001 doc 05 | spine placement |
| DC-5 | No dependency on an **unadmitted / uncertified** implementation | doc 08 | dependency states |
| DC-6 | No dependency on a **PLANNED / not-instantiated** component as if realized (e.g., UMA runtime) | doc 03 AB-001 | dependency states |
| DC-7 | Cross-layer dependencies cross only via **declared interfaces/contracts** (doc 04 IC-6) | R-3 | interface record |
| DC-8 | Dependency changes are governed (doc 06 EC-3/EC-4 for breaking) | doc 06 | change record |

## 2. Acyclicity & Spine Conformance

- The implementation's `Depends-On` set MUST resolve within the frozen spine order; a dependency that would invert the spine (e.g., data depending on application) is rejected (fail-closed).
- Founding edges introduced by the implementation MUST be proven acyclic (inherited discipline: every band unit certifies "founding graph acyclic", AB-001 FD-08).

## 3. Reference-Only Reuse (no redefinition)

A dependency is consumed by ENG-005 reference; the implementation MUST NOT redefine, fork, or shadow a lower-layer construct (AB-001 FD-07; UIL/UAL/USL-02 discipline). Violation ⇒ CG-01 FAIL ⇒ DENY.

## 4. Fail-Closed Conditions

| Condition | Result |
|---|---|
| Unmet/uncertified dependency | not eligible (UCIC Stage 2 return) |
| Cycle detected | DENY (DC-2) |
| Redefinition of a dependency | CG-01 FAIL → DENY |
| Dependency on PLANNED-as-realized | DENY (DC-6) |

## 5. Determination

**DEPENDENCY COMPLIANCE RULES ARE DEFINED (DC-1…DC-8, fail-closed).** They require terminal-success, acyclic, reference-only, spine-respecting dependencies, consuming the AB-001 dependency graph and UCIC Stage 2 without introducing a new dependency model.

*END — 10 · UCOS-EG-001 · AUTHORITY = NONE (READ-ONLY) · MODIFIES NOTHING.*
