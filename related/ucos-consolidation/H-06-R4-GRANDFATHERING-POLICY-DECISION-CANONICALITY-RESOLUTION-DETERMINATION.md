# H-06 R-4 GRANDFATHERING POLICY DECISION — CANONICALITY RESOLUTION DETERMINATION

| Field | Value |
|---|---|
| **ID** | H-06-R4-GPDCRD |
| **Authority** | READ-ONLY ANALYSIS AND DETERMINATION ONLY. No decision field marked. No R-4 modification. No owner decision record modification. No P-3 selection. |
| **Phase** | Foundation Closure — Gate Purity — P-3 Decision Surface Canonicality |
| **Finding addressed** | **CN-1** — duplicate readable owner decision surfaces for P-3 |
| **Baseline** | HEAD `1f869865d5ff709c03cb4eb595524820d55d0be6` · branch `integration/recovery-001` · 0 commits |
| **Produced** | 2026-08-16 |
| **Determination** | **CANONICAL SURFACE IDENTIFIED — NO OWNER DECISION RECORDED — P-3 PENDING — IMPLEMENTATION GATED** |

---

## 1. Surface Inventory — Measured

All R-4-family artifacts were scanned for decision fields. **The finding is wider than stated: three
field-bearing artifacts exist, not two.**

| # | Artifact | sha256 | Checkboxes | Marked | Field-bearing? |
|---|---|---|--:|--:|---|
| A | `H-06-R4-GRANDFATHERING-POLICY-DECISION-RECORD.md` **r2** | `3f0abe615d32…` | **7** | **0** | **YES** |
| B | `H-06-R4-GRANDFATHERING-POLICY-OWNER-DECISION-RECORD.md` | `707f56abbf9f…` | **13** | **0** | **YES** |
| C | `H-06-R4-GRANDFATHERING-POLICY-DECISION-RECORD.pre-r2.md` | `074582134dbd…` | **5** | **0** | **YES — historical snapshot** |
| D | `H-06-R4-CORRECTION-IMPLEMENTATION-PLAN.md` | `4452b67898c2…` | **0** | 0 | **NO** |
| E | `H-06-R4-CONTROLLED-CORRECTION-EXECUTION-PREPARATION.md` | `8d0c20aa2d26…` | **0** | 0 | **NO** |
| F | `H-06-R4-GRANDFATHERING-POLICY-DETERMINATION.md` | `7d1d878d6fb6…` | **0** | 0 | **NO** |

**Total unmarked decision checkboxes across the family: 25. Marked: 0.**

### 1.1 Correction To The Stated Finding

The request identified surface 1 as "`H-06-R4-CORRECTION-IMPLEMENTATION-PLAN.md` / R-4 §7".
**The plan contains zero checkboxes of any kind** — it is a planning artifact and has never been a
decision surface. The duplication is between **R-4 r2 §7 (A)** and **the owner decision record (B)**,
with **the pre-r2 preservation copy (C)** carrying a third, historical field set that also requires an
explicit non-surface designation.

Stated precisely, so the resolution binds the right artifacts.

### 1.2 Field-Set Comparison

| Decision the owner must make | R-4 r2 §7 (A) | Owner decision record (B) |
|---|---|---|
| Policy selection — Option 1 vs Option 2 | **YES** — 2 boxes | **YES** — §5.3, 2 boxes |
| Class B disposition (13 targets) | **YES** — 2 boxes | **YES** — §5.1, 2 boxes |
| Class C/D disposition (23 targets) | **YES** — 2 boxes | **YES** — §5.2, 2 boxes |
| Acceptance of corrected denominator `9 + 13 + 23 = 45` | **NO** — folded into one combined `ACKNOWLEDGED` box | **YES** — §5.4, discrete field |
| Acknowledgement: Eligibility ≠ Authorization | **NO** — not separately expressible | **YES** — §5.5, discrete field |
| Migration deadline (if Option 1) | YES | YES — §5.3 |
| Migration owner (if Option 1) | **NO** | **YES** — §5.3 |
| Mandatory acknowledgements | 1 combined | **3 discrete** — §6 |
| `Selected By` · `Date` | YES · YES | YES · YES |
| **`Signature`** | **NO — absent** | **YES** — §7 |
| Completion criteria | **NOT STATED** | **YES** — §7.1, 13 conditions |
| Entry log · non-entry log | **NO** | **YES** — §8, §8.1 |
| Validation requirements | **NO** | **YES** — §9, V-1..V-10 |

**A cannot express two of the five required decisions.** Marking A to its fullest extent would leave
Decisions 4 and 5 unrecorded, or would record them by implication through a single combined
acknowledgement — which is inference, not selection.

---

## 2. Canonical Decision Surface

### 2.1 Determination

> **`H-06-R4-GRANDFATHERING-POLICY-OWNER-DECISION-RECORD.md` §5 is the canonical P-3 decision entry
> surface.**

### 2.2 Grounds

| # | Ground | Evidence |
|---|---|---|
| 1 | **Completeness** — it is the only surface that can express all five decisions as discrete fields | §1.2 — A cannot express Decisions 4 and 5 |
| 2 | **Recordability** — it carries completion criteria (13 conditions), an entry log, a non-entry log, and a `Signature` field; A has none of these | §1.2 |
| 3 | **Auditability** — it fixes validation requirements V-1..V-10 **before** values are transmitted, so the standard cannot be adjusted afterward | ODR §9 |
| 4 | **Role separation** — R-4's own authority line reads "DECISION RECORD **PREPARATION ONLY**"; it is the evidence record. Holding evidence and selection in one artifact is what produced this drift | R-4 header |
| 5 | **Chain precedent** — the chain already separates evidence from selection twice: updated IADR (scope/boundary) vs IAODR (owner phase decisions), and ODDP (evidence) vs ODODR (selection). This resolution applies the established pattern | Updated IADR §1.4 · ODODR §1.3 |
| 6 | **Evidence stability** — R-4 r2 is hash-locked at `3f0abe615d32…` and referenced by the correction execution validation determination. Marking it would change that hash and invalidate every reference to the validated evidence state | Correction execution validation determination §1 |

**Ground 6 is decisive on its own.** R-4 r2's hash is the citation anchor for the corrected evidence.
A decision surface must change when marked; an evidence anchor must not. The two roles are
incompatible in one artifact.

### 2.3 Historical Evidence / Reference Designation

| Artifact | Designation | Status |
|---|---|---|
| **A** — R-4 r2 | **EVIDENCE RECORD AND HISTORICAL REFERENCE.** §7 is **retired as a decision surface** | Must remain unmarked |
| **C** — pre-r2 copy | **IMMUTABLE PRESERVATION SNAPSHOT** of r1. Its 5 fields are a historical artifact of the pre-correction state | Must remain unmarked; hash-locked at `074582134dbd…` |
| **D, E, F** | Planning, preparation, and evidence determinations — **never decision surfaces** | No fields; no action |

R-4 r2 retains full force as evidence: §3.1–§3.5 measurements, the 36-name enumeration, the class
model, controls C-1..C-6, and the §6 recommendation. **Only its §7 field set is retired.**

---

## 3. How Duplicate Decision Ambiguity Is Prevented

### 3.1 Void-Ab-Initio Rule

> **A mark placed in any non-canonical surface does not constitute a P-3 selection.** It is void from
> the outset, records nothing, and must be reported as a canonicality violation rather than
> interpreted as intent.

This is the operative safeguard. It means the ambiguity cannot produce a wrong outcome even before
the annotation in §3.2 is applied: no mark in R-4 §7 or in the pre-r2 copy can ever be read as a
decision.

### 3.2 Pending Annotation — CN-1 Closure Requirement

Closing CN-1 fully requires an annotation in R-4 §7 pointing at the canonical surface. **This
determination does not perform it** — modifying R-4 requires correction authority not held here.

| # | Required annotation | Target | Authority |
|---|---|---|---|
| CN-1a | Header status: R-4 is the evidence record; §7 is retired as a decision surface | R-4 r2 header | Correction authority |
| CN-1b | §7 preamble: selection occurs only in `H-06-R4-GRANDFATHERING-POLICY-OWNER-DECISION-RECORD.md` §5; marks here are void | R-4 r2 §7 | Correction authority |
| CN-1c | Note that the pre-r2 copy is an immutable snapshot whose fields are historical | R-4 r2 header or the copy's own header | Correction authority |

**Until CN-1a–c are applied, the §3.1 void-ab-initio rule governs.** CN-1 remains **OPEN**.

### 3.3 Structural Safeguards Already In Place

| # | Safeguard | Where |
|---|---|---|
| S-1 | ODR §0 discloses the duplication and names §5 as authoritative | ODR §0 |
| S-2 | ODR validation **V-7** requires R-4 r2 §7 to carry **0 marks** at any future validation | ODR §9 |
| S-3 | ODR §8 logs zero-mark transmissions as open entries, never decisions | ODR §8 |
| S-4 | ODR §7.1 states 13 completion conditions, so a partial entry records nothing | ODR §7.1 |
| S-5 | Hash-locking: R-4 r2 `3f0abe615d32…` and pre-r2 `074582134dbd…` are cited by determination, so any mark would be detected as a hash change | This determination §4 |

### 3.4 General Rule For The Chain

> Where an evidence record and an owner decision record both exist for one decision, **the owner
> decision record is the canonical selection surface and the evidence record's field set is retired.**
> An artifact cited by hash as an evidence anchor may not also be a decision surface.

Consistent with the existing separations: updated IADR / IAODR, and ODDP / ODODR.

---

## 4. Validation

| # | Check | Required | Measured | Result |
|---|---|---|---|---|
| V-1 | **R-4 hash unchanged** | `3f0abe615d32de48a4f66a0e536f98290ddc2d392a2a8a4d0af45b887966de15` | **identical** | **PASS** |
| V-2 | **Owner decision record hash unchanged** | `707f56abbf9f0003ea089438881389fbe174fe2f22fd67972379b1e46df0c1ae` | **identical** | **PASS** |
| V-3 | Pre-r2 preservation copy unchanged | `074582134dbd…` | **identical** | **PASS** |
| V-4 | **P-3 remains unselected** | 0 marks across all surfaces | **A 0 of 7 · B 0 of 13 · C 0 of 5 — total 0 of 25**; `Selected By`, `Date`, `Signature` blank | **PASS** |
| V-5 | **Zero `gate_mode`** | 0 | **0** — also `replay_path` **0**, `audit_emission` **0** | **PASS** |
| V-6 | **Zero declaration changes** | 0 | **0 of 11** | **PASS** |
| V-7 | **Zero engine changes** | 0 | **0** | **PASS** |
| V-8 | **Zero registry changes** | 0 | **0**; `mutation-governance-boundary.json` clean at `509d1a4d3f9af6e0…`; `generated-artifact-registry.json` untouched | **PASS** |
| V-9 | HEAD and branch unchanged | `1f869865` · `integration/recovery-001` | **identical** · **0** commits | **PASS** |
| V-10 | This determination modified no decision surface | 0 | **0** — only this file was written | **PASS** |

### 4.1 Chain Integrity

| Link | State |
|---|---|
| ODODR | 5 APPROVED · validation PASS |
| IAODR | 5 APPROVED · entry A-1 CLOSED · validation PASS |
| IADR §8 | `[X] AUTHORIZED` · signature validation PASS |
| Original IADR | Immutable — `90e856f6…`, mtime 17:01:26 |
| R-4 correction | r1 → r2 executed and validated, 9 of 9 PASS |

---

## 5. Resulting State

| Property | State |
|---|---|
| Canonical P-3 decision surface | **`H-06-R4-GRANDFATHERING-POLICY-OWNER-DECISION-RECORD.md` §5** |
| Historical evidence / reference | **R-4 r2** (§7 field set retired) · **pre-r2 copy** (immutable snapshot) |
| Ambiguity prevention | §3.1 void-ab-initio rule in force now; §3.2 annotations CN-1a–c pending under correction authority |
| CN-1 | **OPEN** — mitigated by §3.1, closed only by CN-1a–c |
| Owner decision | **NONE RECORDED** — 0 of 25 checkboxes marked across all surfaces |
| P-3 | **ELIGIBLE FOR OWNER DECISION — NOT SELECTED** |
| CIEP v2 Phase 0.2 | **FAIL** |
| Phase 0.4 / 0.5 / 0.6 | **PENDING re-measurement / FAIL / FAIL** |
| Implementation | **GATED** |
| Gate purity | **NOT CLOSED** — GP-1, GP-3, GP-11 OPEN (residual) |
| Files written by this determination | **1** — this document |
| Repository mutation | **NONE** |

### 5.1 Next Act

The next act is the owner's P-3 transmission against **ODR §5** — five marks, conditional fields
where applicable, three acknowledgements, `Selected By`, `Date`, `Signature`. Optionally preceded by
CN-1a–c under correction authority. **Neither is performed here, and no option is recommended.**

*This document is a read-only canonicality determination. It marks no decision field, modifies neither
R-4 nor the owner decision record, selects no policy, and confers no authority. R-4 r2 remains at
sha256 `3f0abe615d32de48a4f66a0e536f98290ddc2d392a2a8a4d0af45b887966de15` and the owner decision
record at `707f56abbf9f0003ea089438881389fbe174fe2f22fd67972379b1e46df0c1ae`. HEAD remains
`1f869865` on `integration/recovery-001`.*

---

Canonical decision surface identified.
No owner decision recorded.
P-3 selection remains pending.
Implementation remains gated.
