# H-06 IMPLEMENTATION AUTHORIZATION REQUEST

| Field | Value |
|---|---|
| **ID** | H-06-IAR |
| **Depends on** | H-06-MUTATION-GOVERNANCE-OWNER-DECISION-RECORD.md · H-06-RATIFICATION-VALIDATION-DETERMINATION.md |
| **Authority** | REQUEST PREPARATION ONLY. No implementation authorized. |
| **Phase** | Foundation Closure — Gate Purity Implementation Authorization |
| **Baseline** | HEAD `1f869865` · branch `integration/recovery-001` |
| **Owner Decision** | Option B — Explicit Multi-Mode Gate Model |
| **Decision Recorded By** | Bipin Kumar · 2026-08-16 |
| **Status** | PENDING APPROVAL |

---

## 1. Authorized Scope Requested

This request seeks authorization to implement the following changes, and only these changes,
in accordance with the Option B governance model ratified in H-06-MUTATION-GOVERNANCE-OWNER-DECISION-RECORD.md.

### 1.1 Declaration Schema Extension

Add an additive `gate_mode` field to the programme block of each `*-declaration.json` file.

**Permitted values:** `OBSERVE` · `PRODUCER` · `EXECUTION`

**Sub-classification:** An `audit_emission` sub-field may be added alongside `gate_mode: OBSERVE`
for programmes that carry always-on, append-only gitignored audit writes
(OBSERVE_WITH_DECLARED_AUDIT_EMISSION class).

**Affected files (11):**

| File | Location |
|---|---|
| `uccep-declaration.json` | `00-BOOK/` subtree |
| `ucaf-declaration.json` | `00-BOOK/` subtree |
| `ucl-declaration.json` | `00-BOOK/` subtree |
| `uga-declaration.json` | `00-BOOK/` subtree |
| `uaie-declaration.json` | `00-BOOK/` subtree |
| `uaue-declaration.json` | `00-BOOK/` subtree |
| `ukb-declaration.json` | `00-BOOK/` subtree |
| `ufep-declaration.json` | `00-BOOK/` subtree |
| `urat-declaration.json` | `00-BOOK/` subtree |
| `utce-declaration.json` | `00-BOOK/` subtree |
| `cmg-declaration.json` | `00-BOOK/` subtree |

Each mode value must be supported by measured behaviour evidence before the declaration
is written. No mode may be declared speculatively.

### 1.2 GP-10 Code Fix — aee_engine.py emit() Suppression

Suppress the unconditional `emit()` call at `aee_engine.py:1807` when invoked under
`--tier observe`. The call currently executes regardless of tier, producing tracked writes
on what the label represents as an observation path. The fix is a tier guard on the
`emit()` invocation.

**Affected file:** `00-MASTER/UCOS-AEE-001/aee_engine.py`

### 1.3 GP-2 Write-Order Correction — 3 Engines

For each of the three engines that write before reaching the gate branch, reorder
operations so the write does not occur before the gate verdict is established. The
gate must be able to report a pre-write verdict.

**Affected engines:** to be confirmed by per-engine measurement at implementation time.
The implementation owner must verify file identity against Gate Purity finding GP-2
before modifying any file.

### 1.4 GP-4 Dead Flag Removal or Wiring — 3 Engines

For each of the three engines carrying unread `--render` flags, either wire the flag
to its intended path or remove it. No flag declared in a parser may be unreachable.

**Affected engines:** to be confirmed by per-engine measurement at implementation time.
The implementation owner must verify file identity against Gate Purity finding GP-4
before modifying any file.

### 1.5 GP-5 Label Correction — verify.sh Stage 4

Correct the label of `verify.sh` stage 4 from "Read-only" to
`OBSERVE_WITH_DECLARED_AUDIT_EMISSION` to reflect that it performs an always-on
enforcement audit write to `.runtime/governance/`.

**Affected file:** `verify.sh`

### 1.6 PRODUCER Replay Contract Addition

For each programme classified as `gate_mode: PRODUCER`, add a named replay path that:
- regenerates outputs in memory,
- compares committed bytes without writing first,
- is named in the programme's `*-declaration.json`.

This is a hard co-obligation of PRODUCER classification. A PRODUCER declaration without
a tested replay path is constitutionally incomplete.

---

## 2. Preconditions Already Satisfied

| Precondition | Evidence |
|---|---|
| H-06 decision recorded | H-06-MUTATION-GOVERNANCE-OWNER-DECISION-RECORD.md §7 — Option B, Bipin Kumar, 2026-08-16 |
| Mode vocabulary defined | H-06-MUTATION-GOVERNANCE-OWNER-DECISION-RECORD.md §4 — OBSERVE / PRODUCER / EXECUTION / OBSERVE_WITH_DECLARED_AUDIT_EMISSION |
| `gate_mode` field name confirmed | H-06-R3-GATE-MODE-FIELD-CANONICAL-DETERMINATION.md — RESOLVED |
| No filename collision | H-06-R1-GATE-FILENAME-COLLISION-DETERMINATION.md — Set A ∩ Set B = ∅ |
| EXECUTION audit destination confirmed | H-06-R2-EXECUTION-AUDIT-TRAIL-DESTINATION-DETERMINATION.md — `.runtime/governance/` |
| Existing authority surfaces sufficient | No new registry required; `mutation-governance-boundary.json` and `generated-artifact-registry.json` are reused |
| Knowledge Once Principle preserved | `gate_mode` field is additive to `*-declaration.json`; no duplication on existing surfaces |
| Canonical Ownership Principle preserved | Three authority surfaces remain non-overlapping |
| GP evidence collected | `GATE-PURITY-DETERMINATION.md` GP-1..GP-11 with file:line evidence |
| `gate_mode` field is additive | Survey of all 11 declaration files confirmed: no existing `gate_mode`, `execution_mode`, or `mode` field |

---

## 3. Preconditions Remaining

The following must be satisfied before this request may be approved and implementation
may begin.

| # | Precondition | Status | Action Required |
|---|---|---|---|
| P-1 | Ratification validation passes | REQUIRES CONFIRMATION | Re-run H-06-RATIFICATION-VALIDATION-DETERMINATION.md against recorded Option B decision |
| P-2 | Per-programme behaviour measurements confirmed | NOT DONE | Each engine's actual mode must be measured before its declaration is written |
| P-3 | Grandfathering policy for undeclared engines during transition | OWNER SELECTS | H-06-R4-GRANDFATHERING-POLICY-DETERMINATION.md — evidence complete, owner decision pending |
| P-4 | GP-2 engine identities confirmed | NOT DONE | File identity verification required before code change |
| P-5 | GP-4 engine identities confirmed | NOT DONE | File identity verification required before code change |
| P-6 | PRODUCER replay contract design per engine | NOT DONE | Each PRODUCER-classified engine requires a named replay path before its declaration is written |

P-1 is the immediate gate. P-2 through P-6 are sequenced after P-1.

---

## 4. Exact Implementation Boundaries

### In Scope

- Additive `gate_mode` field on 11 `*-declaration.json` files
- Optional `audit_emission` sub-field alongside `gate_mode: OBSERVE` where applicable
- `aee_engine.py` tier guard on `emit()` at line 1807 (GP-10)
- Write-order resequencing in 3 GP-2 engines
- Dead flag wiring or removal in 3 GP-4 engines
- `verify.sh` stage 4 label correction (GP-5)
- Replay path implementation for each PRODUCER-classified programme

### Out of Scope

- Any change to `mutation-governance-boundary.json`
- Any change to `generated-artifact-registry.json`
- Any change to `00-BOOK/DATA/` contents not required by the above
- Any new registry, authority surface, or governance file
- Any change to H-01 through H-05 scope
- Any change to R-B1 through R-B5 scope
- Any engine not listed in GP-1..GP-11 findings
- Any CI workflow change beyond those strictly required by GP-2 or GP-4 fixes
- Foundation Freeze declaration (H-06 implementation does not itself close the freeze)

---

## 5. Forbidden Actions

The following actions are explicitly forbidden during and after implementation:

| Forbidden Action | Reason |
|---|---|
| Declaring a mode for an engine before measuring its behaviour | Violates Evidence before conclusion principle |
| Declaring `gate_mode: PRODUCER` without a named replay path | Replay contract is a hard co-obligation |
| Declaring `gate_mode: EXECUTION` without a resolving entry in `mutation-governance-boundary.json` | Option B invariant 5 |
| Modifying `mutation-governance-boundary.json` authority chains | Outside H-06 implementation scope |
| Creating a new mode registry or authority surface | Violates Knowledge Once and Canonical Ownership principles |
| Modifying UICO or UICM artifacts | Explicitly excluded by standing governance constraints |
| Running any implementation step before this request is approved | No implementation authorized |
| Treating this document as implementation authorization | This is a request; authorization requires a separate approval action |
| Skipping any step in the Section 6 closure sequence | Each step is a hard dependency |

---

## 6. Validation Requirements After Implementation

Implementation is not complete until all of the following are confirmed:

### 6.1 Structural Validation

| Check | Requirement |
|---|---|
| All 11 `*-declaration.json` files carry `gate_mode` | Verified by script or manual audit |
| No `gate_mode` value outside `OBSERVE`, `PRODUCER`, `EXECUTION` | Schema enforcement |
| Every `gate_mode: PRODUCER` declaration names a replay path | Manual audit |
| Every `gate_mode: EXECUTION` declaration has a resolving `mutation-governance-boundary.json` entry | Cross-reference check |
| Every `gate_mode: OBSERVE` + `audit_emission` declaration names a gitignored path | Manual audit |

### 6.2 Behaviour Validation

| Check | Requirement |
|---|---|
| `aee_engine.py --tier observe` produces zero tracked writes | Measured post-fix |
| GP-2 engines: gate verdict established before any write | Measured post-fix |
| GP-4 engines: `--render` flag reaches its declared path | Measured post-fix |
| `verify.sh` stage 4 label reads `OBSERVE_WITH_DECLARED_AUDIT_EMISSION` | Visual + grep confirmation |
| PRODUCER replay paths: byte-identical output on identical input | Tested per engine |

### 6.3 Verification Run

`verify.sh` must complete **10/10 PASS** at baseline `HEAD` post-implementation.

Any stage failure blocks closure.

### 6.4 Gate Purity Re-Assessment

After all validation checks pass, GP-1 through GP-11 must be re-assessed individually
and each finding updated to `CLOSED` or `OPEN (residual)` in `GATE-PURITY-DETERMINATION.md`.
No finding may be assumed closed without re-measurement.

---

## 7. Rollback Requirements

### 7.1 Rollback Trigger

Rollback is required if:
- Any `verify.sh` stage fails post-implementation and cannot be resolved within the
  authorized implementation scope
- A mode declaration is found to contradict measured engine behaviour
- A PRODUCER replay path fails byte-comparison
- Any implementation action was taken outside the boundaries defined in Section 4

### 7.2 Rollback Method

Each change is independently reversible by `git revert` of the commit(s) that introduced it:

| Change | Rollback |
|---|---|
| `gate_mode` field additions to `*-declaration.json` | `git revert <commit>` — additive field removal; no schema breakage |
| `aee_engine.py` tier guard | `git revert <commit>` — single conditional addition |
| GP-2 write-order resequencing | `git revert <commit>` per engine |
| GP-4 flag wiring/removal | `git revert <commit>` per engine |
| `verify.sh` label correction | `git revert <commit>` — single string change |
| PRODUCER replay path additions | `git revert <commit>` per programme |

No rollback action causes state loss. All changes are declaration additions, label
corrections, or code separations. Repository Truth is unaffected by reverting any
of these changes.

### 7.3 Rollback Scope

Rollback of any individual change must not be assumed to rollback others. Each change
is independently committed and independently reversible.

---

## 8. Post-Implementation Closure Sequence

Upon successful validation (Section 6), the following sequence applies:

```
GP-1 through GP-11 re-assessed (Section 6.4)
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

Gate purity closure satisfies one dimension of Foundation Freeze only. It does not
satisfy H-01 through H-05 or R-B1 through R-B5.

---

*This document is a governance request preparation artifact. It defines the scope,
boundaries, and validation requirements for H-06 implementation. It does not authorize
any implementation action. No implementation may begin until this request receives
explicit approval through a separate constitutional authorization step.*

---

Implementation Authorization:
PENDING APPROVAL

No implementation authorized.
