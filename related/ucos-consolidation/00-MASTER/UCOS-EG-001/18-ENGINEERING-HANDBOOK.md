# 18 — Engineering Handbook

> PROGRAM **UCOS-EG-001** · PHASE-001 · IMPLEMENTATION CONFORMANCE FRAMEWORK
> BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED — READ-ONLY)** · MODE = READ-ONLY · EVIDENCE-ONLY · FAIL-CLOSED.

---

## 0. Purpose

Practical handbook for engineers operating under EG-001: how to take an implementation from proposal to admission into Repository Truth. Navigates the other 19 documents; introduces no new rule.

## 1. Document Map

| Need | Read |
|---|---|
| What governs engineering? | 01 Governance Constitution |
| What must I conform to? | 02 Conformance Standard · 05 Conformance Matrix |
| What reviews apply? | 03 Review Framework |
| What must my implementation declare? | 04 Implementation Contract |
| How do I propose a change? | 06 Change Governance |
| What lifecycle do I follow? | 07 Engineering Lifecycle (= UCIC-001 + overlay) |
| How do I get admitted? | 08 Admission Policy |
| How do I integrate into the repo? | 09 Repository Integration Rules |
| Dependency / runtime / security / quality / validation / certification rules | 10 · 11 · 12 · 13 · 14 · 15 |
| What evidence do I produce? | 16 Evidence Model |
| Am I ready? | 17 Readiness Standard |
| Executive overview | 19 Executive Summary |
| Final verdict | 20 Final Engineering Determination |

## 2. The Engineer's Workflow (proposal → Repository Truth)

```
1. Declare the Implementation Contract (doc 04, IC-1…12).
2. Follow the Engineering Lifecycle = UCIC-001 15 stages (doc 07).
3. Pass the 14 Conformance Gates (doc 05) — evidence-backed.
4. Pass the 9 Engineering Reviews (doc 03) — SoD.
5. Get CCE-certified (doc 15) — certifier ≠ you.
6. Satisfy Repository Integration Rules (doc 09) — validate/enforce/guard/twin.
7. Meet the Admission Predicate (doc 08) → ADMITTED → UKB entry.
```

## 3. Golden Rules

1. **Consume the architecture; never redesign it** (AB-001 is frozen).
2. **Additive-only**; never mutate frozen artifacts (RI-8).
3. **Reference, don't redefine** dependencies (DC-3).
4. **Evidence before conclusion**; absence = NOT-DONE (doc 16).
5. **Fail-closed**; unproven = not admitted (doc 08).
6. **Analysis ≠ Authority**: engineering decides conformance; UKB owns truth; CEP-005 signs certificates.
7. **Architectural need → AB-001 Change Control** (doc 06); never resolve it in engineering.

## 4. Common Failure Modes → Fix

| Symptom | Cause | Fix |
|---|---|---|
| DENY at admission | a conformance gate UNKNOWN | produce the missing evidence (doc 16) |
| Forbidden-path write | wrote to frozen surface | revert; keep additive (RI-8) |
| CCE gate FAIL | validation gap | REOPEN → fix → re-certify |
| Duplicate home | Knowledge Once violation | consolidate to single canonical home (CG-04) |
| Cycle detected | dependency inversion | restructure to respect the spine (DC-2/DC-4) |
| Embedded secret | security hygiene | remove; reference by classification (SC-4) |

## 5. What EG Grants / Withholds

| Grants | Withholds |
|---|---|
| A single standard to evaluate any implementation before Repository Truth | Authority to change architecture (AB-001 Change Control only) |
| A deterministic, fail-closed admission decision | Production go-live (parallel track, doc 17) |
| Consumption of UCIC-001 / CCE / CEP authorities | New authority (EG is AUTHORITY = NONE) |

## 6. Determination

**ENGINEERING HANDBOOK PROVIDES COMPLETE NAVIGATION OF EG-001.** It maps all 20 documents to needs, gives the proposal→admission workflow, golden rules, and failure-mode fixes — introducing no new rule and consuming the frozen apparatus.

*END — 18 · UCOS-EG-001 · AUTHORITY = NONE (READ-ONLY) · MODIFIES NOTHING.*
