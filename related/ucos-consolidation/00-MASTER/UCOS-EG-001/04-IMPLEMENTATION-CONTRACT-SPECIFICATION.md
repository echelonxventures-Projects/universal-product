# 04 — Implementation Contract Specification

> PROGRAM **UCOS-EG-001** · PHASE-001 · IMPLEMENTATION CONFORMANCE FRAMEWORK
> BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED — READ-ONLY)** · MODE = READ-ONLY · EVIDENCE-ONLY · FAIL-CLOSED.

---

## 0. Purpose

Specify the mandatory **implementation contract** every implementation SHALL declare before it may be reviewed or admitted. This extends UCIC-001 Output 2 (Execution Contract) with the constitutional-conformance fields the mission enumerates. It **consumes** UCIC-001; it does not replace it.

## 1. Contract Completeness Rule

> An implementation is eligible for review only when **every** contract field below is satisfied and evidenced. A missing field ⇒ not eligible (fail-closed).

## 2. The Implementation Contract (mandatory fields)

| # | Field | Meaning | Maps to |
|---|---|---|---|
| IC-1 | **Purpose** | single testable objective | UCIC Output 2 OBJECTIVE |
| IC-2 | **Authority** | governing determination + constitutional anchor authorizing it | CG-05; UCIC Stage 3 |
| IC-3 | **Inputs** | typed inputs consumed (by reference) | CG-01/CG-02 |
| IC-4 | **Outputs** | typed outputs produced (one canonical home) | CG-03/CG-04 |
| IC-5 | **Dependencies** | Depends-On set (terminal-success, acyclic, reference-only) | CG-01; doc 10 |
| IC-6 | **Interfaces** | declared typed interfaces / contracts (reference-only reuse) | R-3; CG-02 |
| IC-7 | **Lifecycle** | forward-only lifecycle states it obeys | CG-07 |
| IC-8 | **Evidence** | the doc-16 evidence subset it will produce | CG-13; UCIC Output 5 |
| IC-9 | **Tests** | test suites + thresholds (unit/integration/functional/security) | CG-09; UCIC Stage 7 |
| IC-10 | **Validation** | static/dynamic/coverage thresholds | CG-09; UCIC Stages 5–8 |
| IC-11 | **Certification** | applicable CCE gates | CG-10; UCIC Stage 10 |
| IC-12 | **Repository Registration** | registries/twin/lineage updates + `ukb enforce` | CG-03; UCIC Stages 11–13 |

## 3. Contract Template (declarative)

```
IMPLEMENTATION CONTRACT
  IC-1  PURPOSE                : <single testable outcome>
  IC-2  AUTHORITY              : <governing determination ID + constitutional anchor>
  IC-3  INPUTS                 : <typed inputs, by reference>
  IC-4  OUTPUTS                : <typed outputs, single canonical home>
  IC-5  DEPENDENCIES           : <Depends-On IDs; terminal-success; acyclic; reference-only>
  IC-6  INTERFACES             : <declared typed interfaces / contracts>
  IC-7  LIFECYCLE              : <forward-only states>
  IC-8  EVIDENCE               : <doc-16 evidence subset>
  IC-9  TESTS                  : <suites + thresholds>
  IC-10 VALIDATION             : <static/dynamic/coverage thresholds>
  IC-11 CERTIFICATION          : <applicable CCE gates>
  IC-12 REPOSITORY REGISTRATION: <registries/twin/lineage + ukb enforce>
```

## 4. Relationship to UCIC-001 Output 2

| UCIC-001 Output 2 field | EG contract field |
|---|---|
| CAPABILITY IDENTIFIER / OBJECTIVE | IC-1 |
| GOVERNING DETERMINATION / CONSTITUTIONAL ANCHOR | IC-2 |
| DEPENDENCIES | IC-5 |
| ADDITIVE SURFACES | (implicit in IC-4 outputs; enforced by CG-01) |
| ACCEPTANCE CRITERIA | IC-1 (testable) |
| EVIDENCE / VALIDATION / CERTIFICATION REQ. | IC-8/IC-10/IC-11 |
| REQUIRED REPO UPDATES | IC-12 |

EG adds explicit **Inputs (IC-3)**, **Interfaces (IC-6)**, and **Lifecycle (IC-7)** as first-class contract fields for interface/dependency/lifecycle reviews (doc 03 R-3/R-4). No UCIC field is removed or altered.

## 5. Contract Immutability & Provenance

A declared contract is recorded immutably at review time; changes to it after admission are engineering changes (doc 06). The contract is the provenance root for the implementation's evidence chain (doc 16) and traceability (CG-13).

## 6. Determination

**IMPLEMENTATION CONTRACT SPECIFICATION IS DEFINED (IC-1…IC-12).** It mandates a complete, evidenced contract as the precondition for review/admission, extending UCIC-001 Output 2 with Inputs/Interfaces/Lifecycle and consuming it otherwise unchanged. Incompleteness is fail-closed.

*END — 04 · UCOS-EG-001 · AUTHORITY = NONE (READ-ONLY) · MODIFIES NOTHING.*
