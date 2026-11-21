# 08 — Engineering Admission Policy

> PROGRAM **UCOS-EG-001** · PHASE-001 · IMPLEMENTATION CONFORMANCE FRAMEWORK
> BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED — READ-ONLY)** · MODE = READ-ONLY · EVIDENCE-ONLY · FAIL-CLOSED.

---

## 0. Purpose

Define the **admission criteria** an implementation SHALL satisfy to enter Repository Truth. Admission is the single fail-closed decision the entire framework converges on. Default is **DENY**.

## 1. The Admission Predicate

```
ADMIT(impl)  ⇔
      CONTRACT_COMPLETE(impl)         # IC-1…IC-12 satisfied (doc 04)
   ∧  CONFORMANT(impl)                # CG-01…CG-14 all PASS  (doc 05)
   ∧  REVIEWS_PASSED(impl)            # R-1…R-9 all PASS      (doc 03)
   ∧  CERTIFIED(impl)                 # UCIC Stage 10 / CCE ten-gate (doc 15)
   ∧  EVIDENCE_COMPLETE(impl)         # doc 16 bundle physical & sufficient
   ∧  CHANGE_GOVERNED(impl)           # if a change: doc 06 record complete/approved

Otherwise → DENY (fail-closed).
```

No single condition is sufficient; **all** are necessary. Absence of evidence for any condition ⇒ DENY (never admit-by-default).

## 2. Mandatory Admission Checklist

| # | Requirement | Source | Verdict must be |
|---|---|---|:---:|
| A-1 | Contract complete (IC-1…12) | doc 04 | COMPLETE |
| A-2 | All 14 conformance gates PASS | doc 05 | PASS ×14 |
| A-3 | All 9 engineering reviews PASS | doc 03 | PASS ×9 |
| A-4 | CCE ten-gate certified; certifier ≠ executor | doc 15 | CERTIFIED |
| A-5 | Evidence bundle physical + sufficient | doc 16 | COMPLETE |
| A-6 | Repository Truth checks (validate/enforce) PASS | CG-03/CG-04 | PASS |
| A-7 | Traceability rooted + closed (No-Orphan) | CG-13 | CLOSED |
| A-8 | Determinism (byte-identical regeneration) | CG-14 | PASS |
| A-9 | If a change: change record complete + approved | doc 06 | APPROVED |
| A-10 | No forbidden-path write; additive-only | CG-01 | CLEAN |

Any row ≠ required verdict ⇒ **NOT ADMITTED**.

## 3. Admission Verdicts

| Verdict | Meaning | Effect |
|---|---|---|
| **ADMITTED** | all A-1…A-10 satisfied | enters Repository Truth (UKB registration; UCIC Stages 11–14) |
| **DENIED** | ≥1 requirement unmet | not admitted; remediate + re-evaluate |
| **RETURNED** | remediable gap | fail-forward to relevant UCIC stage |
| **BLOCKED** | dependency on out-of-scope act (e.g., DR-RAT-11 for finality-scoped items) | recorded; scoped-blocked; engineering-scope admission unaffected |

## 4. Fail-Closed Doctrine (mandatory)

- **Default deny:** an implementation is not admitted until it *proves* every requirement. Silence, ambiguity, or missing evidence = DENY.
- **No waivers:** no admission requirement may be waived. A genuinely N/A dimension is recorded as N/A with rationale + evidence (doc 05 §2) and does not count against admission.
- **No self-attestation:** every verdict cites a physical evidence artifact (doc 16); a claim without evidence is treated as UNKNOWN = DENY.

## 5. Admission Authority & Separation

- EG computes the admission *determination* (AUTHORITY = NONE, derived); **UKB** performs the actual entry into Repository Truth (registration). Analysis ≠ Authority preserved: EG decides conformance/admission-readiness; UKB owns truth.
- SoD: the admitting reviewer (R-9 / admission) ≠ the implementer (UCIC executor) ≠ CCE certifier.

## 6. Admission Record (evidence)

Admission emits an immutable record: `{impl_id, verdict, A-1…A-10 results, gate/review refs, cert id, evidence bundle hash, baseline, decider role}` into the engineering evidence store (doc 16), traceable in MCP-006. No entry into Repository Truth occurs without a matching ADMITTED record.

## 7. Determination

**ENGINEERING ADMISSION POLICY IS DEFINED (ADMIT predicate, A-1…A-10, default-DENY, fail-closed).** It is the single constitutional decision governing entry to Repository Truth: an implementation is admitted only when it is contract-complete, conformant, reviewed, certified, evidenced, and (if a change) governed. UKB performs entry; EG never becomes truth.

*END — 08 · UCOS-EG-001 · AUTHORITY = NONE (READ-ONLY) · MODIFIES NOTHING.*
