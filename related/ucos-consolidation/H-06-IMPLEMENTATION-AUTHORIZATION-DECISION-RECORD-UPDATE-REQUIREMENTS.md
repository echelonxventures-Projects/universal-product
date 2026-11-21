# H-06 IMPLEMENTATION AUTHORIZATION DECISION RECORD — UPDATE REQUIREMENTS

| Field | Value |
|---|---|
| **ID** | H-06-IADR-UR |
| **Authority** | GOVERNANCE PREPARATION ONLY. No authorization created. No signature prepared. No implementation authorized. |
| **Phase** | Foundation Closure — Gate Purity — Post-Ownership-Disposition Authorization Preparation |
| **Prepares** | Update requirements for `H-06-IMPLEMENTATION-AUTHORIZATION-DECISION-RECORD.md` (IADR) |
| **Trigger** | Ownership disposition decision recorded — ODODR r4, five APPROVED, Bipin Kumar, 2026-08-16T20:10:00+05:30 |
| **Baseline** | HEAD `1f869865` · branch `integration/recovery-001` |
| **Produced** | 2026-08-16 |
| **Determination** | **IADR UPDATE REQUIRED BEFORE §8 SIGNATURE CAN BE VALIDLY PRESENTED — 5 BLOCKERS OPEN, 1 ELIGIBLE FOR RE-MEASUREMENT** |

---

## 1. Why This Artifact, and Not the §8 Signature Package

Both candidate next actions were assessed. The IADR update is the correct one, and it is a
**strict prerequisite** of the signature package, for one measured reason:

> **The IADR contains zero references to the ownership disposition decision.**
> `grep -ci 'ownership disposition|ODODR'` → **0**. IADR mtime **17:01:26**; ODODR r4 recorded
> at **20:10:00+05:30**. The IADR was authored three hours before the decision that changed the
> ownership model, the GP-11 closure criteria, and the freeze criteria.

Presenting §8 for signature in this state would ask the implementation authority to authorize
against a governance chain that omits the most recent constitutional act. That is the stale-basis
defect class the chain has repeatedly corrected — the rebase §2.3 finding (counts measured
against one tree then inherited as fact in another) in a different guise.

**Sequence.** IADR update → update validation → *then* §8 signature package. §5 states the
signature-package requirements so the downstream act is visible, but it is not prepared here.

---

## 2. Task 1 — H-06 Ownership Decision Completion State

### 2.1 Verified Complete

| Property | Measured |
|---|---|
| Record | `H-06-OWNERSHIP-DISPOSITION-OWNER-DECISION-RECORD.md` r4 · sha256 `277369a9…` · 699 lines |
| Decision fields | 5 · **all marked** |
| `APPROVED` / `REJECTED` | **5 / 0** |
| Double-marked / unmarked fields | **0 / 0** |
| Acknowledgements | **3 of 3** |
| `Decided By` · `Date` | **Bipin Kumar** · **2026-08-16T20:10:00+05:30** |
| Entry | **E-3 — CLOSED** (E-1, E-2 logged zero-mark OPEN) |
| §9.7 completion conditions | **10 of 10** |
| Validation | `H-06-OWNERSHIP-DISPOSITION-OWNER-DECISION-VALIDATION-DETERMINATION.md` — 5 of 5 checks **PASS** |

**Chain state: CLOSED.** The ownership disposition decision is complete and validated.

### 2.2 What It Resolved

| Item | State |
|---|---|
| O-3 — Class A/B scope extension | **RESOLVED** |
| O-6 — no new surface creation | **RESOLVED** |
| O-7 — acceptance criteria A-1..A-7 | **RESOLVED** |
| ODDP D-1..D-5 | **RESOLVED** |
| Ownership model | **ADOPTED** — 22 declarable · 23 governed gaps · 45 of 45 dispositioned |
| Freeze criteria | **F-5 · F-6 added** to F-1..F-4 |

### 2.3 What It Explicitly Did Not Do

Recorded by the owner's own acknowledgements, which are marked:

| Acknowledgement | Effect |
|---|---|
| 1 | Approval grants **no** implementation authority; IADR §8 unsigned, P-3 unselected |
| 2 | Gate purity **does not close** — GP-1/GP-3/GP-11 terminate OPEN (residual) |
| 3 | `uar-gate` asymmetry stands unresolved |

---

## 3. Task 2 — Remaining Blockers for Implementation Authorization

### 3.1 Phase 0 Gate — Current Measured State

CIEP v2 Phase 0 requires **all six** conditions to pass before any phase begins.

| # | Condition | State | Owner of the act |
|---|---|---|---|
| 0.1 | IADR §8 AUTHORIZED — signed and dated | **FAIL — unsigned** (both boxes empty, `Authorized By` blank, `Date` blank) | Implementation authority |
| 0.2 | P-3 R-4 policy selected | **FAIL — unselected** (Options 1/2 both empty · scope-gap sub-field empty · acknowledgement unmarked · `Selected By`/`Date` blank) | Owner |
| 0.3 | Baseline confirmed | **PASS** — HEAD `1f869865`, branch `integration/recovery-001`, re-measured | — |
| 0.4 | Corrected success criteria accepted (O-7) | **ELIGIBLE FOR RE-MEASUREMENT** — see §3.2 | Owner |
| 0.5 | `verify.sh` baseline captured (A-1) | **FAIL — never captured** | Implementation authority (preparatory) |
| 0.6 | Unrelated deltas isolated | **FAIL** — `verify.sh` +45/−0 dirty · `generated-artifact-registry.json` +864/−0 dirty | Owning programmes (UAUE et al.) — H-06 has no authority to commit their work |

**Net: 1 PASS · 4 FAIL · 1 eligible for re-measurement.**

### 3.2 The One Blocker the Ownership Decision Actually Cleared

Condition 0.4 requires "Owner acceptance of AMC §5, incl. GP-11 terminating OPEN (residual)".
ODODR Decision 2 (**APPROVED**) adopted the GP-11a/GP-11b model with acceptance criteria
A-1..A-7 and resolved O-7; acknowledgement 2 (**marked**) accepts GP-11 terminating OPEN
(residual). Both halves of 0.4 now have explicit owner acceptance.

**This determination does not flip 0.4 to PASS.** Re-measurement of an owner-act condition is
an owner act. What is established is that the substantive basis for 0.4 now exists on the
record, where before it did not. The IADR update must present 0.4 for re-measurement with
ODODR §5 and acknowledgement 2 cited as the evidence.

### 3.3 Blockers Not Numbered in Phase 0

| # | Blocker | Severity |
|---|---|---|
| **B-A** | **IADR chain predates ODODR** — §2 cites five sources, none of them the ownership disposition decision; §3 preconditions omit it entirely | **Blocking** — signature would rest on a stale chain |
| **B-B** | **R-4 record now carries a superseded measurement** in the field the owner must acknowledge — §4.2 | **Blocking 0.2** — selection would ratify a false population statement |
| **B-C** | **Denominator ambiguity** — four different coverage numbers are live across the chain (§4.3) | **Blocking clarity of §4/§6** |

### 3.4 Sequenced, Not Authorization-Blocking

Per IADR §3, these are satisfied progressively during implementation and do **not** block the
signature: P-2 (per-programme behaviour measurement, before each declaration), P-4 (GP-2 engine
identities), P-5 (GP-4 engine identities), P-6 (PRODUCER replay contract design per engine).
The IADR update should restate them unchanged, so the update is not misread as expanding them.

---

## 4. Task 3 — IADR Update Requirements

Eight requirements, **U-1 … U-8**. None creates authorization. None marks §8.

### 4.1 U-1 — Add the Ownership Disposition Decision to §2 and §3

**Defect.** §2 confirms a five-row chain ending at P-1; §3 lists eight satisfied preconditions.
Neither mentions ODODR. The §3 row "H-06 owner decision recorded" points at the **mutation
governance** decision (Option B) — a different decision, on a different record.

**Required.** Add to §2:

| Check | Source | Status |
|---|---|---|
| Ownership disposition decision recorded — 5 of 5 APPROVED | `H-06-OWNERSHIP-DISPOSITION-OWNER-DECISION-RECORD.md` r4 §9, §14 — Bipin Kumar, 2026-08-16T20:10:00+05:30 | CONFIRMED |
| Ownership disposition decision validated | `H-06-OWNERSHIP-DISPOSITION-OWNER-DECISION-VALIDATION-DETERMINATION.md` §9 — 5 of 5 PASS | CONFIRMED |
| Record canonicality corrected before entry | `H-06-OWNERSHIP-DISPOSITION-DECISION-RECORD-CANONICALITY-CORRECTION-DETERMINATION.md` | CONFIRMED |

And disambiguate the existing §3 row to read "H-06 **mutation governance** owner decision
recorded — Option B", so the two owner decisions are not conflated.

### 4.2 U-2 — Record That R-4's Population Statement Is Superseded (highest priority)

**Defect.** R-4 §7 asks the owner to acknowledge that "the authorized scope of 11
`*-declaration.json` files reaches at most **9 of the 45** baseline gate targets, and that **36**
gate targets are outside authorized scope." R-4 control **C-5** characterises those 36 as "the 36
gate targets **with no declaration surface**."

Decision 1 measured otherwise. Of those 36:

| Population | Count | Has a capable owning surface | Authorized to declare |
|---|--:|---|---|
| Class B — domain-named surfaces (`rib-blueprint.json`, `ucaf-authority.json`, `uei-evolution.json`, `umk-kernel.json`, `uer-resilience.json`, `upf-provider.json`, `ucda-decisions.json`, `mcos-civilization.json`, `ucef-framework.json`, `uccep-bindings.json`, `urrc-bindings.json`, `uaep-platform.json`, `uaie-architecture.json`) | **13** | **YES** | **NO** |
| Class C + Class D — governed gaps | **23** | **NO** | **NO** |

**C-5 as written is now factually wrong for 13 of the 36.** They are not surface-less; they are
surface-capable and merely unauthorized.

**Required.** The IADR update must record that R-4 §7's acknowledgement text and C-5's
characterisation are superseded by ODODR Decision 1, and that **R-4 must be corrected before the
P-3 selection is transmitted.** Selecting P-3 against the present wording would have the owner
acknowledge a population statement the owner's own later decision contradicts.

**This is a requirement to correct R-4, not authority to correct it.** R-4 is untouched here.

### 4.3 U-3 — State Which Denominator Governs Which Claim

**Defect.** Four coverage figures are live and mutually consistent only once their scopes are
distinguished. Left unstated, any pair reads as a contradiction:

| Figure | Meaning | Source |
|---|--:|---|
| **2 of 45** | modes committed at HEAD | Rebase §2.4 |
| **4 of 45** | declarations authorized under current scope | ODODR §3.3, §8.4 |
| **9 of 45** | gate targets reachable by the authorized 11 declaration files | R-4 §3.2 |
| **22 of 45** | targets **eligible** under Decision 1 | ODODR §4.1 |

**Reconciliation to be stated verbatim in the IADR:**

```
9 authorized-reachable + 13 eligible-but-unauthorized + 23 governed gaps = 45
```

**Required.** §4 must state that eligibility (22) is **not** authorization (≤9), and §6 must
state which figure each closure claim uses. Also record why 11 files reach only 9 targets:
`uga-declaration.json` and `urr-declaration.json` own no `*-gate` target — UGA gates via a
subcommand, URR has no gate target — per ODODR §10.2, which is also why O-4 and O-5 stay off the
critical path.

### 4.4 U-4 — Bind §4.8 Verification to GP-11a / GP-11b

**Required.** §4.8 predates the split finding. Rebase it onto Decision 2: GP-11a (`*-gate` plane,
45 targets — disposition coverage **and** declaration integrity where applicable) and GP-11b
(`*-self` plane, 26 guard families). Acceptance criteria A-1..A-7 govern closure. Record that
GP-11 terminates **OPEN (residual — scope-bounded)** after authorized execution, with the
numbers stated rather than implied.

### 4.5 U-5 — Add Freeze Criteria F-5 and F-6

**Required.** Decision 3 added F-5 (ownership completeness) and F-6 (declared mode enforcement)
to F-1..F-4. §4.8 and §6 must carry both. F-6 is the one that binds implementation directly:
**a declared mode must be enforcement-reachable**, so no `gate_mode` may be written to a surface
whose engine carries no `--check-declaration` guard. Under the authorized 9, the applicable and
reachable sets coincide, so F-6 costs nothing to satisfy — but it must be stated as a condition,
not assumed.

### 4.6 U-6 — Carry Decision 5 Into §4 and §6 Explicitly

**Required.** Decision 5 holds that GP-1/GP-2/GP-3/GP-4/GP-10 are behavioural defects **not**
discharged by declaring a mode or registering a governed gap. The IADR must state, in §4 and
again in §6:

- A `PRODUCER` declaration without a **tested replay path** is reclassification-as-conformance,
  refused by GATE-PURITY D-3.6. The replay contract is a hard co-obligation of every PRODUCER
  declaration, not a follow-on task.
- Expected terminal states after authorized execution: GP-2 **CLOSED** (3 engines) · GP-4
  **CLOSED** (3) · GP-10 **CLOSED** (1) · GP-1 **OPEN (residual)** · GP-3 **OPEN (residual)** ·
  GP-11 **OPEN (residual)**.
- Executing the full authorized scope **does not close gate purity**, matching the owner's
  marked acknowledgement 2.

### 4.7 U-7 — Confirm §5 Exclusions Against Decision 4, and Extend

**Assessment.** §5's thirteen exclusion rows are **already consistent** with Decision 4 (no new
registry, no new governance surface or authority layer, no `mutation-governance-boundary.json`
modification). No relaxation is needed or permitted.

**Required additions**, to make Decision 4 explicit rather than merely compatible:

| Exclusion to add | Basis |
|---|---|
| No `gate_mode` on any Class B surface — eligible under Decision 1 but **unauthorized** | Decision 1 + IAR §1.1 scope of 11 files |
| No `gate_mode` on any Class C or Class D target — governed gaps only | Decision 1 |
| No new governance surface **class**; instantiating an existing class is not exercised under this authorization | Decision 4 · ODODR §7.2 |
| No `gate_mode` on a surface whose engine lacks a `--check-declaration` guard | F-6 |

### 4.8 U-8 — Restate Sequenced Preconditions Unchanged

**Required.** Restate P-2, P-4, P-5, P-6 verbatim with their sequence positions, and restate that
P-3 must be selected **before implementation begins**. The update must not convert any sequenced
precondition into a satisfied one.

### 4.9 Requirements Traceability

| # | Requirement | Source decision | IADR sections |
|---|---|---|---|
| U-1 | Add ownership disposition decision to chain | ODODR r4 (all five) | §2, §3 |
| U-2 | Record R-4 population statement as superseded | Decision 1 | §3 (P-3 row), new note |
| U-3 | State governing denominators | Decision 1 | §4, §6 |
| U-4 | Bind verification to GP-11a/GP-11b | Decision 2 | §4.8, §6 |
| U-5 | Add F-5, F-6 | Decision 3 | §4.8, §6 |
| U-6 | Findings not discharged by declaration | Decision 5 | §4, §6 |
| U-7 | Confirm and extend exclusions | Decision 4 | §5 |
| U-8 | Restate sequenced preconditions | IADR §3 | §3 |

---

## 5. Downstream — What the §8 Signature Package Will Require

Listed so the sequence is visible. **Not prepared here.** No signature field is drafted, and no
value is suggested for one.

| # | Condition on the signature package |
|---|---|
| S-1 | IADR update U-1..U-8 applied, and validated by a determination |
| S-2 | R-4 corrected per U-2, **then** P-3 selected by the owner as a separate act on its own record |
| S-3 | Phase 0.4 re-measured by owner act, citing ODODR §5 and acknowledgement 2 |
| S-4 | Phase 0.5 `verify.sh` baseline captured and committed as a dated log |
| S-5 | Phase 0.6 isolation achieved — requires UAUE et al. to commit their own work; H-06 cannot do it |
| S-6 | §8 presented with both boxes empty, `Authorized By` and `Date` blank, and no recommendation permitted to populate them |
| S-7 | Signature validated by a separate determination before any phase begins |

**Ordering constraint.** S-2 depends on U-2; presenting P-3 before R-4 is corrected would repeat
the defect U-2 exists to prevent.

---

## 6. Boundary Attestation

Measured after producing this artifact:

| Check | Result |
|---|---|
| Authorization created | **NO** — IADR §8 both boxes empty, `Authorized By` blank, `Date` blank |
| IADR modified | **NO** — this artifact states requirements; it applies none |
| R-4 modified | **NO** — correction required, not performed |
| Declarations modified | **NO** — 0 `*-declaration.json` changed |
| `gate_mode` added | **NO** — 0 occurrences in any JSON repository-wide |
| Engines modified | **NO** |
| Registries modified | **NO** |
| `mutation-governance-boundary.json` | **UNCHANGED** — clean status · sha256 `509d1a4d…` · mtime 2026-08-12 |
| HEAD | `1f869865` · `integration/recovery-001` — no commit, stage, or index operation |
| Files written | **1** — this artifact |

---

## 7. Determination

The H-06 ownership disposition decision chain is **complete and validated**: five APPROVED marks,
three acknowledgements, attribution and date populated, entry E-3 closed, §9.7 satisfied 10 of 10.

Implementation authorization remains **blocked by five open conditions** — IADR §8 unsigned (0.1),
P-3 unselected (0.2), `verify.sh` baseline uncaptured (0.5), unrelated deltas not isolated (0.6),
and the IADR's own chain predating the decision (B-A) — with Phase 0.4 now **eligible for
re-measurement** on the strength of Decision 2 and acknowledgement 2.

The next governance action is the **IADR update U-1..U-8**, with **U-2 first**: R-4's population
statement must be corrected before the P-3 selection is transmitted, or the owner would be asked
to acknowledge a measurement their own decision has superseded.

---

H-06 ownership disposition closure acknowledged.
Implementation authorization remains pending.
No repository mutation performed.
