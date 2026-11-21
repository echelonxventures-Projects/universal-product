# 18 — Architecture Baseline Handbook

> PROGRAM **UCOS-AB-001** · PHASE-001 · ARCHITECTURE BASELINE v1.0
> BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED TRUTH — READ-ONLY)** · MODE = READ-ONLY · EVIDENCE-ONLY · FAIL-CLOSED.

---

## 0. Purpose

The practical handbook for operating under baseline v1.0 — how implementers, reviewers, and governance actors use the baseline day-to-day. It navigates the other 19 documents; it introduces no new rule.

## 1. Document Map (how to use UCOS-AB-001)

| Need | Read |
|---|---|
| What is the baseline? | 01 Architecture Baseline |
| What is frozen / active / planned? | 02 Frozen · 03 Active |
| What programs exist and their status? | 04 Program Inventory |
| What depends on what? | 05 Dependency Graph |
| Who governs / who owns? | 06 Governance Register · 09 Ownership Matrix |
| How do I change architecture? | 07 Change Control · 14 Change Policy |
| What version am I on? | 08 Version Register |
| Can implementation start? | 10 Entry Criteria · 16 Readiness |
| How does design→implementation work? | 11 Transition |
| Where is the approved architecture? | 12 Approved Catalog |
| What must I not revisit? | 13 Frozen Decision Register |
| Is the baseline certified? | 15 Baseline Certification |
| How is the baseline reproduced? | 17 Repository Baseline Record |
| Executive overview | 19 Executive Summary |
| Final verdicts | 20 Final Baseline Determination |

## 2. Day-to-Day Workflows

### 2.1 "I want to build a product/service."
1. Confirm engineering-scope entry is AUTHORIZED (doc 10 §2).
2. Consume the frozen spine + approved catalog (docs 05, 12) — reuse by reference, redefine nothing (FD-07).
3. Realize additively via UCIC-001 + CCE ten-gate (FD-16); validate + certify before "done".
4. Never mutate frozen artifacts (P-7); never redesign (P-2).

### 2.2 "I think the architecture must change."
1. Do **not** edit anything. Open a Change Control Proposal (doc 07 step 1).
2. Provide Impact + Repository-Truth + Measurement evidence (steps 2–5).
3. If it touches a frozen decision (doc 13), prove a constitutional defect (doc 07 §4) and route to CEP-009 amendment + CEP-006 ratification.
4. On approval, receive a new baseline version (doc 08) before implementing.

### 2.3 "I need to freeze an ACTIVE component."
1. Confirm exit criteria closed (doc 03).
2. Route a C-FREEZE change (doc 14) to CEP-007.
3. Record the new frozen baseline digest (doc 08 / 17 pattern).

## 3. Golden Rules (memorize)

1. UKB is truth; everything else is derived (FD-01).
2. Consume, don't redesign (P-2).
3. Additive by default; supersede with versioning (P-5).
4. No change without evidence + approval (P-9, fail-closed).
5. Frozen means frozen — defect proof + amendment + ratification only (P-3/P-4).
6. Measurement ≠ decision ≠ truth (FD-05/FD-17).

## 4. What v1.0 Does and Does Not Grant

| Grants | Does NOT grant |
|---|---|
| Engineering implementation entry (doc 10 §2) | Production go-live (doc 16) |
| Change Control operation (doc 07) | Constitutional finality (DR-RAT-11) |
| A stable, versioned reference point | Authority to mutate frozen artifacts |
| A path to UMA measurement migration | An instantiated UMA (still design) |

## 5. Escalation & Authorities Quick-Reference

| Question | Authority (doc 06) |
|---|---|
| Truth / canonical home | UKB |
| Amend a constitution | CEP-009 |
| Freeze a component | CEP-007 |
| Certify | CEP-005 |
| Ratify finality | Ratification (DR-RAT-11 — BLOCKED) |
| Measurement | interim engines → UMA |

## 6. Determination

**HANDBOOK PROVIDES COMPLETE, EVIDENCE-BASED NAVIGATION OF BASELINE v1.0.** It maps all 20 documents to needs, gives day-to-day workflows and golden rules, and states exactly what v1.0 grants and withholds — without introducing any new rule.

*END — 18 · UCOS-AB-001 · AUTHORITY = NONE (READ-ONLY) · MODIFIES NOTHING.*
