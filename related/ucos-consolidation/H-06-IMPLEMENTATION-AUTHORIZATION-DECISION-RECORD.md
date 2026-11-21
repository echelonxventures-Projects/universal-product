# H-06 IMPLEMENTATION AUTHORIZATION DECISION RECORD

| Field | Value |
|---|---|
| **ID** | H-06-IADR |
| **Phase** | Foundation Closure — Gate Purity Implementation Authorization |
| **Baseline** | HEAD `1f869865` · branch `integration/recovery-001` |
| **Depends on** | H-06-MUTATION-GOVERNANCE-OWNER-DECISION-RECORD.md |
| | H-06-RATIFICATION-VALIDATION-REVALIDATION-DETERMINATION.md |
| | H-06-IMPLEMENTATION-AUTHORIZATION-REQUEST.md |
| | H-06-IMPLEMENTATION-AUTHORIZATION-REQUEST-VALIDATION-DETERMINATION.md |
| **Produced** | 2026-08-16 |
| **Status** | AWAITING AUTHORIZATION DECISION |

---

## 1. Authority

### 1.1 Decision Authority

Implementation authorization is an act of the implementation governance authority —
the party with constitutional standing to bind implementation resources and scope.
This record captures that act.

### 1.2 Scope Authority

The authorized scope is defined exclusively by H-06-IMPLEMENTATION-AUTHORIZATION-REQUEST.md
§§1 and 4, as validated by H-06-IMPLEMENTATION-AUTHORIZATION-REQUEST-VALIDATION-DETERMINATION.md.
No scope element may be added, removed, or reinterpreted at the point of authorization.
The IAR and its validation determination are the definitive scope reference.

### 1.3 Separation of Owner Decision and Implementation Authorization

The owner decision (Option B, recorded by Bipin Kumar, 2026-08-16) established the
constitutional policy. It did not authorize implementation. These are distinct acts
by design:

| Act | Document | Effect |
|---|---|---|
| Owner decision | H-06-MUTATION-GOVERNANCE-OWNER-DECISION-RECORD.md §7 | Establishes mode vocabulary and constitutional model |
| Ratification | H-06-RATIFICATION-VALIDATION-REVALIDATION-DETERMINATION.md | Confirms decision validity and evidence sufficiency |
| IAR validation | H-06-IMPLEMENTATION-AUTHORIZATION-REQUEST-VALIDATION-DETERMINATION.md | Confirms request is correctly scoped and bounded |
| **Implementation authorization** | **This document** | **Grants permission to begin implementation** |

Authorization given here does not expand, amend, or reinterpret the owner decision.
It permits execution within the already-ratified scope.

---

## 2. Governance Chain Confirmation

| Check | Source | Status |
|---|---|---|
| H-06 owner decision recorded — Option B | H-06-MUTATION-GOVERNANCE-OWNER-DECISION-RECORD.md §7 | CONFIRMED |
| Ratification valid | H-06-RATIFICATION-VALIDATION-REVALIDATION-DETERMINATION.md §8 | CONFIRMED |
| IAR structurally valid and correctly scoped | H-06-IMPLEMENTATION-AUTHORIZATION-REQUEST-VALIDATION-DETERMINATION.md §9 | CONFIRMED — all 7 checks PASS |
| No implementation occurred before authorization | H-06-IMPLEMENTATION-AUTHORIZATION-REQUEST-VALIDATION-DETERMINATION.md §5 (Check 4) | CONFIRMED |
| P-1 (ratification validation) resolved | H-06-RATIFICATION-VALIDATION-REVALIDATION-DETERMINATION.md | CONFIRMED — sole blocking condition cleared |

---

## 3. Preconditions

The following preconditions to authorization are confirmed as satisfied:

| Precondition | Evidence | Status |
|---|---|---|
| H-06 owner decision recorded | Decision record §7 — Option B, Bipin Kumar, 2026-08-16 | SATISFIED |
| Ratification valid | H-06-RATIFICATION-VALIDATION-REVALIDATION-DETERMINATION.md — all 5 checks PASS | SATISFIED |
| IAR validation complete | H-06-IMPLEMENTATION-AUTHORIZATION-REQUEST-VALIDATION-DETERMINATION.md — all 7 checks PASS | SATISFIED |
| Mode vocabulary ratified | OBSERVE / PRODUCER / EXECUTION / OBSERVE_WITH_DECLARED_AUDIT_EMISSION | SATISFIED |
| `gate_mode` field name confirmed | H-06-R3-GATE-MODE-FIELD-CANONICAL-DETERMINATION.md — RESOLVED | SATISFIED |
| No filename collision | H-06-R1-GATE-FILENAME-COLLISION-DETERMINATION.md — RESOLVED | SATISFIED |
| EXECUTION audit destination confirmed | H-06-R2 — `.runtime/governance/` | SATISFIED |
| Implementation boundary intact | No engine, declaration, or workflow modified since baseline | SATISFIED |

The following preconditions are confirmed as remaining (implementation-sequenced, not
authorization-blocking):

| Precondition | Status | Sequence Position |
|---|---|---|
| P-2 — per-programme behaviour measurements | NOT DONE | Before each declaration is written |
| P-3 — R-4 grandfathering policy selected | PENDING owner selection | Before implementation begins |
| P-4 — GP-2 engine identities confirmed | NOT DONE | Before GP-2 code changes |
| P-5 — GP-4 engine identities confirmed | NOT DONE | Before GP-4 code changes |
| P-6 — PRODUCER replay contract design per engine | NOT DONE | Before each PRODUCER declaration is written |

P-3 requires owner selection before implementation begins. P-2, P-4, P-5, and P-6
are satisfied progressively during the implementation sequence as each change is approached.

---

## 4. Approved Scope

Authorization, when granted, covers exactly and only the following:

### 4.1 Declaration Schema Extension (`gate_mode`)

Additive `gate_mode` field on the programme block of each of the 11 `*-declaration.json`
files listed in IAR §1.1. Permitted values: `OBSERVE`, `PRODUCER`, `EXECUTION`.
Optional `audit_emission` sub-field for `OBSERVE_WITH_DECLARED_AUDIT_EMISSION` programmes.

No mode may be declared before the engine's behaviour is measured (P-2).

### 4.2 Mode Declaration Updates

Per-programme `gate_mode` values written into the 11 declarations after P-2 measurement
is complete for each engine.

### 4.3 Replay Contract Implementation

For each programme classified as `gate_mode: PRODUCER`: a named replay path that
regenerates in memory, compares committed bytes without writing first, and is named in
the programme's `*-declaration.json`. This is a hard co-obligation of PRODUCER
classification and may not be deferred.

### 4.4 GP-2 Remediation — Write-Order Correction

Write-order resequencing in the 3 engines identified by Gate Purity finding GP-2,
so the gate verdict is established before any write occurs. Engine identities confirmed
per P-4 before modification.

### 4.5 GP-4 Remediation — Dead Flag Resolution

For each of the 3 engines carrying unread `--render` flags: wire the flag to its
intended path or remove it. Engine identities confirmed per P-5 before modification.

### 4.6 GP-5 / GP-9 Audit Classification Correction

Correction of the `verify.sh` stage 4 label from "Read-only" to
`OBSERVE_WITH_DECLARED_AUDIT_EMISSION`. Applies to gitignored audit write paths
in the GP-9 class as identified per programme.

### 4.7 GP-10 Correction — `aee_engine.py` emit() Suppression

Tier guard on the `emit()` call at `aee_engine.py:1807` to suppress unconditional
execution when invoked under `--tier observe`.

### 4.8 Required Verification

Post-implementation validation as defined in IAR §6:
- Structural validation (§6.1) — all 11 declarations carry `gate_mode`; values within vocabulary; replay paths named; EXECUTION entries resolve; audit paths gitignored
- Behaviour validation (§6.2) — zero tracked writes on observe tier; write order corrected; flags reach declared path; label confirmed; replay byte-identical
- Verification run (§6.3) — `verify.sh` 10/10 PASS
- Gate purity re-assessment (§6.4) — GP-1 through GP-11 individually re-assessed

---

## 5. Excluded Scope

The following are explicitly outside the authorized scope and may not be performed
under this authorization:

| Excluded Action | Basis |
|---|---|
| Creation of any new registry | Violates Knowledge Once and No duplicate governance surfaces principles |
| Creation of any new governance surface or authority layer | Same basis; IAR §4 Out of Scope |
| Modification of `mutation-governance-boundary.json` authority chains | IAR §4 Out of Scope; IAR §5 Forbidden |
| Modification of `generated-artifact-registry.json` beyond what GP-2/GP-4 fixes strictly require | IAR §4 Out of Scope |
| Architecture changes not required by GP-2, GP-4, GP-5, GP-10, or declaration additions | IAR §4 Out of Scope |
| Any change to `00-BOOK/DATA/` contents not required by approved scope | IAR §4 Out of Scope |
| Any change to H-01 through H-05 scope | IAR §4 Out of Scope |
| Any change to R-B1 through R-B5 scope | IAR §4 Out of Scope |
| Any engine not listed in GP-1..GP-11 findings | IAR §4 Out of Scope |
| CI workflow changes beyond those strictly required by GP-2 or GP-4 fixes | IAR §4 Out of Scope |
| Foundation Freeze declaration | H-06 implementation does not itself close the freeze |
| Modification of UICO or UICM artifacts | Standing governance constraint |
| Any action listed in IAR §5 Forbidden Actions | IAR §5 — all nine rows |

---

## 6. Post-Implementation Closure Sequence

Upon successful completion of all validation in §4.8, the following sequence applies
(from IAR §8):

```
GP-1 through GP-11 re-assessed individually
        ↓
Gate purity dimension confirmed as closed
        ↓
Foundation Freeze gate-purity conditions re-assessed:
  (1) Mutation boundaries declared        → YES (all 46 gates carry verified mode)
  (2) Replay integrity proven             → YES (all PRODUCER gates have tested replay)
  (3) Evidence chain trustworthy          → YES (all declared surfaces)
        ↓
Remaining freeze blockers (H-01..H-05, R-B1..R-B5) addressed
through their own governance sequences
```

Gate purity closure satisfies one dimension of Foundation Freeze only.

---

## 7. Rollback

If any rollback trigger defined in IAR §7.1 occurs, each change is independently
reversible by `git revert` of the commit(s) that introduced it. No rollback causes
state loss. Rollback of any individual change must not be assumed to rollback others.

---

## 8. Authorization Field

**Implementation Authorization:**

```
[ ] AUTHORIZED
[ ] NOT AUTHORIZED
```

**Authorized By:**
________________

**Date:**
________________

**Scope Reference:** H-06-IMPLEMENTATION-AUTHORIZATION-REQUEST.md (validated by
H-06-IMPLEMENTATION-AUTHORIZATION-REQUEST-VALIDATION-DETERMINATION.md)

**Constraint:** Authorization is limited to the scope defined in §4 of this document.
No action listed in §5 is authorized regardless of any other instruction or artifact.
P-3 (R-4 grandfathering policy) must be selected by the owner before implementation begins.

---

*This document is a governance authorization preparation artifact. It captures the
constitutional chain and presents the authorization decision field for the implementation
authority to complete. Until the Authorization Field in §8 is populated with an explicit
AUTHORIZED decision, signed, and dated, no implementation may begin.*

*Authorization by the implementation authority does not expand, reinterpret, or amend
the owner decision or the ratified mode vocabulary. It permits execution within the
already-bounded scope.*

---

No implementation executed.
Authorization decision recorded separately.
