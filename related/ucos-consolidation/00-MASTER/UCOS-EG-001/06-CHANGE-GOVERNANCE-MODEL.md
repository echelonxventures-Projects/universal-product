# 06 — Change Governance Model

> PROGRAM **UCOS-EG-001** · PHASE-001 · IMPLEMENTATION CONFORMANCE FRAMEWORK
> BASELINE `b67a720` · AUTHORITY = **NONE (DERIVED — READ-ONLY)** · MODE = READ-ONLY · EVIDENCE-ONLY · FAIL-CLOSED.

---

## 0. Purpose

Define how **engineering changes** are proposed and governed. This is the engineering-side complement to AB-001 Change Control (doc 07/14 of AB-001): AB-001 governs *architectural* change; EG governs *implementation* change and routes any architectural impact **back** to AB-001 Change Control (never resolving it in engineering).

## 1. Change Governance Principles

| Principle | Statement |
|---|---|
| Engineering changes implementation, not architecture | An architectural need escalates to AB-001 Change Control. |
| Evidence-before-approval | No change approved without the full change record (§2). |
| Backward-compatibility default | Breaking changes require migration + explicit approval. |
| Fail-closed | Missing field / unmet requirement ⇒ change rejected. |
| Traceable | Every change carries provenance to a governing determination. |

## 2. Mandatory Change Record (every engineering change)

| # | Field | Meaning |
|---|---|---|
| EC-1 | **Affected architecture** | which AB-001 strata/frozen decisions the change touches (if any) |
| EC-2 | **Affected authority** | which authority governs the affected area (doc 06 AB-001 register) |
| EC-3 | **Backward compatibility** | compatible / breaking; interface + contract impact |
| EC-4 | **Migration impact** | data/interface/dependency migration required |
| EC-5 | **Risk** | risk classification + blast radius |
| EC-6 | **Evidence** | conformance re-evaluation evidence (doc 05 gates affected) |
| EC-7 | **Approval** | approving authority decision |
| EC-8 | **Ratification requirements** | whether CEP-006 ratification (and DR-RAT-11 finality) applies |

A change missing any field is not processable (fail-closed).

## 3. Change Classification & Routing

| Class | Touches architecture? | Route |
|---|:---:|---|
| **EGC-ADDITIVE** | no (additive impl on frozen spine) | EG review + admission (docs 03/08) |
| **EGC-INTERFACE** | interface only, compatible | EG Interface Review (R-3) + admission |
| **EGC-BREAKING** | interface/contract breaking | migration plan (EC-4) + Governance Review + admission |
| **EGC-ARCH-IMPACT** | yes (frozen decision) | **escalate to AB-001 Change Control** (defect proof, CEP-009/006) — EG does not resolve it |

## 4. Backward Compatibility & Migration

- **Compatible change:** additive; existing consumers unaffected; admitted through normal conformance.
- **Breaking change:** requires a migration plan (EC-4), a compatibility window where feasible, and explicit approval (EC-7); frozen baselines remain immutable (superseded-by-version, not overwritten — AB-001 doc 08).
- No breaking change is silent; all appear in the change/lineage registry (CG-03 registration).

## 5. Escalation to Architecture Change Control (no redesign in engineering)

If a change would alter a frozen decision (AB-001 FD-01…18), EG **halts** and escalates to AB-001 Change Control (fail-closed). Engineering may not amend architecture. Only a proven constitutional defect (AB-001 doc 07 §4) + CEP-009 amendment + CEP-006 ratification can change the frozen set — with DR-RAT-11 gating finality.

## 6. Determination

**CHANGE GOVERNANCE MODEL IS DEFINED (EC-1…EC-8, classified, fail-closed).** It governs engineering changes, mandates a complete evidenced change record, defaults to backward compatibility, and escalates any architectural impact to AB-001 Change Control — engineering never redefines architecture.

*END — 06 · UCOS-EG-001 · AUTHORITY = NONE (READ-ONLY) · MODIFIES NOTHING.*
