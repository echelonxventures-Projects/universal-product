# H-06 OWNERSHIP DISPOSITION OWNER DECISION RECORD

| Field | Value |
|---|---|
| **ID** | H-06-ODODR |
| **Authority** | OWNER DECISION PREPARATION ONLY. No decision selected herein. No implementation authorized. |
| **Phase** | Foundation Closure — Gate Purity — Ownership Disposition Decision |
| **Baseline** | HEAD `1f869865` · branch `integration/recovery-001` · working tree DIRTY |
| **Decision Authority** | Mutation Governance Owner |
| **Depends on** | H-06-OWNERSHIP-DISPOSITION-DECISION-PACKAGE.md (register and decision fields) |
| | H-06-GATE-OWNERSHIP-MODEL-RESOLUTION-DETERMINATION.md (ownership classes, surface analysis) |
| | H-06-SUCCESS-CRITERIA-REBASE-DETERMINATION.md (corrected denominator, GP-11 defects) |
| | H-06-MUTATION-GOVERNANCE-OWNER-DECISION-RECORD.md §7 (Option B ratified) |
| **Produced** | 2026-08-16 |
| **Status** | **DECISION RECORDED — FIVE OF FIVE APPROVED — ENTRY E-3, 2026-08-16 — IMPLEMENTATION STILL NOT AUTHORIZED** |
| **Revision** | r4 — owner decision recorded 2026-08-16 under OWNER DECISION ENTRY authority: entry E-3 transmitted five APPROVED marks, acknowledgements acknowledged, `Decided By` Bipin Kumar, `Date` 2026-08-16T20:10:00+05:30. Recorded exactly as transmitted. **Governance direction only — IADR §8 remains unsigned and P-3 remains unselected.** |
| | r3 — canonicality correction 2026-08-16 under DOCUMENT CORRECTION ONLY authority: terminal status statement corrected to match measured state; §13 entry log extended with E-2 and non-entry action log (§13.3); §14 attestation extended. **No decision field was altered at r3 — all five were unmarked as at that revision.** |
| | r2 — decision entry processed 2026-08-16; field titles aligned to owner wording; entry log added (§13) |

---

## 1. Authority and Limits of This Record

### 1.1 What This Record Is

This record presents five decisions to the mutation governance owner and captures their
disposition. Each decision is stated, its evidence basis given, its consequence on approval
and on rejection stated, and a decision field provided.

### 1.2 What This Record Is Not

It selects nothing. Every field in §9 is unpopulated. This record does not, and cannot:

| Not authorized by this record | Requires |
|---|---|
| Writing any `gate_mode` to any surface | H-06-IADR §8 signature |
| Beginning any implementation phase | H-06-IADR §8 signature **and** P-3 (R-4 policy) |
| Modifying any engine, declaration, or registry | IADR §8 signature and per-phase gates |
| Selecting the R-4 grandfathering policy | H-06-R4-GRANDFATHERING-POLICY-DECISION-RECORD.md §7 |

**Approving all five decisions below leaves implementation blocked.** These decisions
establish *what the ownership model is*. They do not authorize acting on it. That separation
is deliberate and mirrors IADR §1.3: the owner decision establishes constitutional policy;
implementation authorization is a distinct act.

### 1.3 Relationship to the Decision Package

Decision 1 of this record subsumes decision fields **D-1** (Class B extension) and **D-2**
(Class A remainder) of H-06-OWNERSHIP-DISPOSITION-DECISION-PACKAGE.md, and resolves the
open owner decision recorded as **O-3** in H-06-IAR-AUTHORIZATION-MATRIX-CORRECTION.md §6.
Decisions 3 and 5 resolve **O-7**. Decision 4 resolves **O-6**.

---

## 2. Governance Chain Confirmation

| Check | Source | Status |
|---|---|---|
| Option B — Explicit Multi-Mode Gate Model ratified | Owner decision record §7 — Bipin Kumar, 2026-08-16 | **CONFIRMED** |
| Ratification valid | RRVD §8 — all 5 checks PASS | **CONFIRMED** |
| Mode vocabulary authoritative | `OBSERVE` · `PRODUCER` · `EXECUTION` · `OBSERVE_WITH_DECLARED_AUDIT_EMISSION` | **CONFIRMED** |
| Baseline intact — no unauthorized mutation | H-06-PIRSV §2, §5 — re-verified at each subsequent determination | **CONFIRMED** |
| Corrected denominator — 45, not 46 | Rebase §2.2 — HEAD 166 + 4 uncommitted UAUE targets = 170 | **CONFIRMED** |
| Ownership model resolved | GOMRD §2–§6 — Class A 9 · B 13 · C 11 · D 12 | **CONFIRMED** |
| Enforcement boundary measured | ODDP §4.3 — 23 `--check-declaration` engines = A ∪ B ∪ {`uar-gate`} | **CONFIRMED** |
| IADR §8 | Unsigned — both checkboxes empty | **BLOCKED** |
| P-3 / R-4 policy | Unselected | **BLOCKED** |

---

## 3. Evidence Basis in Brief

Three measured facts carry all five decisions.

### 3.1 The Declarable Set and the Enforceable Set Are Identical

The 23 engines carrying a `--check-declaration` guard are **exactly** Class A (9) ∪ Class B
(13) ∪ {`uar-gate`}. The 22 targets with a capable owning surface are **exactly** Class A ∪
Class B.

| Population | Count | Overlap with guard set |
|---|--:|--:|
| Class A ∪ Class B — capable owning surface | 22 | **22 of 22** |
| Class C | 11 | 1 (`uar-gate`, string-blocked) |
| Class D | 12 | **0** |

**Consequence.** A `gate_mode` declared on any of the other 22 gate targets would be read by
nothing. That is the GP-5 defect class — `verify.sh` stage 4's "Read-only" label was false and
undetected precisely because no guard read it. The repository has already drawn the boundary
this decision needs.

### 3.2 The GP Findings Align With That Boundary

Measured mapping of every GP finding population against ownership class:

| Finding | Population | Class A | Class B | Class C | Class D | Declarable |
|---|--:|--:|--:|--:|--:|---|
| **GP-1** | 16 engines | 8 | 8 | 0 | 0 | **16 of 16 — 100%** |
| **GP-2** | 3 engines | 0 | 2 | 1 | 0 | 2 of 3 |
| **GP-3** | 10 targets | 0 | 0 | **10** | 0 | **0 of 10 — 0%** |
| **GP-4** | 3 engines | 3 | 0 | 0 | 0 | **3 of 3 — 100%** |
| **GP-10** | 1 engine | 1 | 0 | 0 | 0 | **1 of 1 — 100%** |

And exactly: **Class C = GP-3's 10 targets + `uar-gate`.** Verified — the set difference in
both directions is `{uar}` and `{}` respectively.

**Consequence.** The proposed disposition is not an arbitrary cut. The declarable set contains
100% of GP-1, GP-4 and GP-10 and two thirds of GP-2. The governed-gap set contains 100% of
GP-3 and the one GP-2 engine that cannot be declared. The model covers every finding that
declaration *can* address and gaps exactly the population it cannot.

### 3.3 Coverage Is Bounded By Disposition, Not Declaration

| Path | Declared | Governed gaps | Freeze F-1 / F-5 |
|---|--:|--:|---|
| Reject Decision 1 | 4 | 41 | **NO** |
| Approve Decision 1 | **22** | **23** | **YES** — all 45 dispositioned |

Freeze conditions F-1 and F-5 reach YES in any configuration where all 45 targets have a
disposition, because a governed gap is a valid disposition. **The binding constraint is
dispositioning all 45, not declaring all 45.**

---

## 4. Decision 1 — Ownership Disposition Model

### 4.1 Statement

> **22 gate targets are eligible for declared mode governance.** These are Class A (9
> `*-declaration.json` surfaces) and Class B (13 domain-named surfaces:
> `rib-blueprint.json`, `ucaf-authority.json`, `uei-evolution.json`, `umk-kernel.json`,
> `uer-resilience.json`, `upf-provider.json`, `ucda-decisions.json`,
> `mcos-civilization.json`, `ucef-framework.json`, `uccep-bindings.json`,
> `urrc-bindings.json`, `uaep-platform.json`, `uaie-architecture.json`).
>
> **23 gate targets are recorded as governed gaps** — Class C (11) and Class D (12) — each
> with a named owner, reason group, blocking condition, and escalation path in
> `ASSESSMENT-CONFLICT-REGISTER.md`.

### 4.2 Basis

| # | Ground | Evidence |
|---|---|---|
| 1 | All 22 satisfy the three-part applicability test: authored non-generated surface · `programme` **object** · `--check-declaration` guard present | ODDP §4.2 |
| 2 | Class B differs from Class A only in filename; the surface kind, structure, and guard are identical | GOMRD §3.2, §5.1 |
| 3 | All 23 gap candidates fail at least one test; 22 of them have **no guard at all**, so a declaration there would be unverifiable | ODDP §4.3 |
| 4 | Governed gaps use the existing `ASSESSMENT-CONFLICT-REGISTER.md` mechanism — no surface created | GOMRD §6.3 option D-β |
| 5 | The cut aligns with the GP finding structure — §3.2 | Measured |

### 4.3 Consequence

| On approval | On rejection |
|---|---|
| Declarable coverage rises from 4 to **22 of 45** | Declarable coverage stays at **4 of 45** |
| All 45 targets receive a disposition | 41 targets remain undispositioned |
| GP-1 becomes fully addressable (16 of 16 in scope) | GP-1 remains 4 of 16 addressable |
| Freeze F-1 and F-5 become reachable | Freeze F-1 and F-5 remain unreachable |
| Resolves O-3; supersedes ODDP D-1 and D-2 | O-3 remains open |

### 4.4 Recommendation

**APPROVE.** Rejecting leaves 18 gate targets undeclared for a filename reason alone, while
their surfaces, structures, and guards are indistinguishable from the 4 already authorized.
The governed-gap half is not a concession — for 22 of the 23 it is the only honest option,
because nothing exists to read a declaration.

### 4.5 Known Limitation Disclosed

`uar-gate` is a governed gap for a reason distinct from the rest: its surface
`uar-analyses.json` exists and is authored, **and** its engine carries a `--check-declaration`
guard — the only Class C target where enforcement can reach. It is blocked solely because its
`programme` value is a JSON **string**, so no field is insertable without a structural change
that IADR §5 forbids. It is also a GP-2 engine, so its **code fix is authorized while its
declaration is not.** This asymmetry is disclosed, not resolved.

---

## 5. Decision 2 — Revised GP-11 Model

### 5.1 Statement

> GP-11 is split into two findings with distinct populations and criteria:
>
> **GP-11a — `*-gate` plane (45 targets).** Closure requires (i) **ownership disposition
> coverage**: every one of the 45 targets is either declared or a governed gap, summing to 45
> with no overlap and no omission; and (ii) **declaration integrity where applicable**: every
> one of the 22 declared modes is within the ratified vocabulary, matches measured behaviour,
> is enforcement-reachable, and — where PRODUCER — names a replay path tested in both
> directions.
>
> **GP-11b — `*-self` plane (26 guard families).** Each family is declared read-only or
> registered as a governed gap. No behavioural change required.

### 5.2 Basis — Six Defects in the Original

| # | Defect | Source |
|---|---|---|
| 1 | Denominator wrong — 46 counts uncommitted `uaue-gate`; HEAD is 45 | Rebase §2.2 |
| 2 | Numerator wrong — 2 of 4 credited modes are uncommitted; 2 are not `*-gate` targets. At HEAD: 2 of 45 | Rebase §2.4 |
| 3 | Two planes conflated in one finding with one criterion (45 vs 26) | Rebase §2.1 |
| 4 | Closure unreachable — 23 of 45 have no surface that can carry the field | GOMRD §4.3 |
| 5 | Presumes a uniform ownership model that does not exist | GOMRD D-7.1 |
| 6 | Credits declarations that nothing reads — measures the wrong thing | ODDP D-7.1 |

### 5.3 Why the Revised Model Is Satisfiable

The original criterion — "46/46 carry verified mode" — cannot be made true by any permitted
action. The revised criterion accepts a **registered, owned gap** as a valid terminal state.
A declared mode and an owned, named absence are both honest statements about a gate. A
fabricated mode is neither.

### 5.4 Consequence

| On approval | On rejection |
|---|---|
| GP-11a/GP-11b become measurable and satisfiable | GP-11 remains unsatisfiable as written |
| GP-11 terminates **OPEN (residual — scope-bounded)** under current authorization, with stated numbers | GP-11 has no honest terminal state |
| Acceptance criteria A-1..A-7 (ODDP §7.3) govern closure | No agreed criteria |

### 5.5 Recommendation

**APPROVE.** A criterion that cannot be satisfied by permitted action is not a criterion. The
split also separates two genuinely different remediation problems that the single finding
conflated.

---

## 6. Decision 3 — Freeze Criteria Additions F-5 and F-6

### 6.1 Statement

> Two conditions are added to the Foundation Freeze gate-purity criteria:
>
> **F-5 — Ownership completeness.** Every gate target has a resolved ownership disposition:
> declared · declarable-and-authorized · explicitly excluded as a governed gap. No target
> unclassified.
>
> **F-6 — Declared mode enforcement.** Every declared mode is enforcement-reachable: the
> owning engine carries a guard that reads the declaration.

### 6.2 Basis

**F-5.** Existing condition F-1 counts declarations and gaps but never requires that a gap be
*resolvable*. Without F-5 a target may sit indefinitely as an unexamined gap — which is how
GP-11 reached 42 undeclared, as the R-4 evidence determination records: "passive
non-enforcement does not produce compliance." F-5 forces each target to a disposition;
"explicitly excluded" is acceptable, unexamined is not.

**F-6.** F-1 and F-5 count dispositions; neither requires that a declaration be *read*.
Without F-6, the freeze could be satisfied by declaring modes for gates nothing verifies —
GP-5 at scale. F-6 costs nothing to satisfy under Decision 1, because the applicable set and
the reachable set are identical (§3.1), but it forecloses the failure mode permanently.

### 6.3 The Full Rebased Condition Set

| # | Condition | Status |
|---|---|---|
| F-1 | Mutation boundaries declared **or explicitly owned as absent**, population stated | Restated (rebase §7.3) |
| F-2 | Replay integrity proven for every declared PRODUCER — **never inferred** from the registry's `deterministic` field | Strengthened |
| F-3 | Evidence chain trustworthy over the declared set, **with the undeclared remainder reported** | De-inverted |
| F-4 | No gate-purity claim rests on uncommitted work | Added (rebase §7.3) |
| **F-5** | **Ownership completeness** | **This decision** |
| **F-6** | **Declared mode enforcement** | **This decision** |

F-3's original phrasing — "trustworthy for all declared surfaces" — was **inverted**: it read
YES more easily the less was declared. F-4 exists because GATE-PURITY §1's counts and two of
its four declared modes are uncommitted.

### 6.4 Consequence

| On approval | On rejection |
|---|---|
| Freeze cannot be satisfied by unexamined gaps or unenforceable declarations | Both loopholes remain open |
| F-1 and F-5 reach YES under Decision 1 with zero new surfaces | Freeze criteria remain as rebased (F-1..F-4 only) |

### 6.5 Recommendation

**APPROVE.** F-5 closes the mechanism that produced GP-11. F-6 closes the mechanism that
produced GP-5. Both are free to satisfy under Decision 1.

---

## 7. Decision 4 — No New Governance Surface Creation

### 7.1 Statement

> No new governance surface **class** — no new registry, authority layer, schema family, or
> constitutional document — is created for H-06 gate mode governance. Mode is recorded only in
> a programme's existing canonical owning surface. Targets without such a surface are governed
> gaps, not new surfaces.

### 7.2 Basis

Four candidate shared hosts were examined directly and each refused:

| Candidate | Refusal ground | Source |
|---|---|---|
| `mutation-governance-boundary.json` | Keyed by **authority** (7 entries, 6 implementations), not by gate. Covers ≤3 of 45. No per-gate slot; hosting modes needs a new collection = structural change | GOMRD §5.2.1 |
| `generated-artifact-registry.json` | Assigned exactly one role — generated artifact registration. It is the **evidence** surface for PRODUCER classification, not the **declaration** surface. GATE-PURITY D-3.6 refuses producer reclassification there as a conformance device | GOMRD §5.2.2 |
| Makefile comments / script headers | **GP-5 is the counter-proof.** `verify.sh` stage 4's header declared "Read-only" and was false, undetected, because no guard reads a comment. Extending this to 23 targets creates 23 unverified claims | GOMRD §5.2.3 |
| `platform/providers/catalog/declared-providers.json` | Governs external data providers, not gates. Category error — though cited as precedent that declared `effects` (`net:read`, `api:read`, `fs:read`, `net:send`) is a native repository pattern | GOMRD §5.2.4 |

**And the determinative distinction:** instantiating an existing surface class is not creating
a new governance surface. The `*-declaration.json` class exists, is instantiated 11 times, and
is read by 23 engines. That distinction is preserved but **not exercised** here — Decision 1
disposes Class C as governed gaps rather than authorizing instantiation.

### 7.3 Consequence

| On approval | On rejection |
|---|---|
| Knowledge Once and Canonical Ownership preserved | A new surface class becomes permissible; duplicate mode authority becomes possible |
| Class C/D coverage is by governed gap only | Class D coverage via a new per-module model becomes available (12 targets), at the cost of a new surface class |

### 7.4 Recommendation

**APPROVE.** The complete model requires nothing new: 22 declared on existing surfaces, 23
governed gaps in an existing register. Creating a surface class to reach 12 Class D targets
would introduce the duplicate-governance condition Option B was ratified to eliminate.

---

## 8. Decision 5 — GP-1, GP-2, GP-3, GP-4, GP-10 Remain Implementation Findings

### 8.1 Statement

> GP-1, GP-2, GP-3, GP-4 and GP-10 are **behavioural defects requiring code remediation**.
> They are not resolved, closed, or discharged by this ownership disposition decision, by
> declaring a `gate_mode`, or by registering a governed gap.

### 8.2 Basis — Per Finding

| Finding | Defect | Resolved by declaration alone? | Character |
|---|---|---|---|
| **GP-1** (16 engines) | Write called unconditionally in `main()`; gate verdict returned after the write | **NO — partially** | Option B legitimizes the *write* via PRODUCER, but the **replay contract is a hard co-obligation** and is implementation work. Declaration without a tested replay path leaves GP-1 constitutionally incomplete. |
| **GP-2** (3 engines) | Write executes before the gate branch, or inside the gate function | **NO** | Pure code fix — write-order resequencing. Authorized (IAR §1.3). |
| **GP-3** (10 targets) | `--render`-mode gates still rewrite the register surface | **NO** | Pure code fix — separate render from gate. **All 10 are Class C** — none declarable; not authorized. |
| **GP-4** (3 engines) | `--render` declared and never read; replay ≡ gate | **NO** | Pure code fix — wire or remove. Authorized (IAR §1.4). |
| **GP-10** (1 engine) | `aee-observe` labelled read-only; `emit()` unconditional at `main` indentation | **NO** | Pure code fix — call-site tier guard. Authorized (IAR §1.2). **Status advanced APPARENT → CONFIRMED** (rebase §8): `emit(decl, model)` takes no tier parameter and references `tier` nowhere in its body. |

### 8.3 Why This Decision Matters

Without it, approving Decisions 1–4 could be read as closing gate purity. It does not. A
declared mode records *what a gate is permitted to do*. It does not stop a gate writing before
it decides (GP-2), does not connect an unread flag (GP-4), does not suppress an unguarded
`emit()` (GP-10), and does not separate render from gate (GP-3).

**GP-1 requires the sharpest care.** Under Option B, declaring an engine `PRODUCER`
*legitimizes* its write — that is the purpose of the mode. But GATE-PURITY D-3.6 explicitly
refuses "reclassifying the 24 engines as producers as a way of making the current behaviour
conformant." The reconciliation: PRODUCER classification is legitimate **only when the replay
co-obligation is discharged** — a named path that regenerates in memory, compares committed
bytes without writing first, and fails on any difference. **A PRODUCER declaration without a
tested replay path is reclassification-as-conformance, which is refused.**

### 8.4 Authorization Status Per Finding

| Finding | In authorized H-06 scope | Expected terminal state after authorized execution |
|---|---|---|
| GP-1 (16) | Only via 4 authorized declarations + their replay contracts | **OPEN (residual)** |
| GP-2 (3) | **YES** — 3 engines | CLOSED |
| GP-3 (10) | **NO** | **OPEN (residual)** |
| GP-4 (3) | **YES** — 3 engines | CLOSED |
| GP-10 (1) | **YES** — 1 engine | CLOSED |

### 8.5 Consequence

| On approval | On rejection |
|---|---|
| Ownership disposition and behavioural remediation stay distinct; neither is reported as the other | Declaring a mode could be mistaken for closing a defect — the precise error GATE-PURITY D-3.6 refuses |
| Gate purity closure requires both tracks | Gate purity could be claimed on declaration alone |

### 8.6 Recommendation

**APPROVE.** This is the decision that keeps the ownership model honest. It costs nothing and
prevents the misreading that would undo the value of the other four.

---

## 9. Owner Decision Fields

**ENTRY STATE: DECISION RECORDED — ENTRY E-3, 2026-08-16.** All five fields carry exactly one
mark, all three acknowledgements are marked, and `Decided By` and `Date` are populated. The
values below are those transmitted by the Mutation Governance Owner and were recorded exactly
as transmitted; none was inferred, defaulted, or supplied on the owner's behalf. Entries E-1
and E-2 (§13) each transmitted all five fields with both checkboxes empty and recorded no
selection; E-3 is the entry that recorded the decision.

**Recording constraint.** Approval of any or all fields records **governance direction
only**. It does not authorize implementation, declaration mutation, engine modification,
or registry modification. See §9.6.

### Decision 1 — Ownership Disposition Model

22 targets eligible for declared mode governance (Class A 9 + Class B 13) · 23 targets
recorded as governed gaps (Class C 11 + Class D 12). Basis §4. Recommendation: APPROVE.

**Selection:**
```
[X] APPROVED
[ ] REJECTED
```

### Decision 2 — Revised GP-11 Ownership Disposition Closure Model

GP-11a (ownership disposition coverage + declaration integrity where applicable) /
GP-11b (`*-self` plane), with acceptance criteria A-1..A-7. Basis §5. Recommendation: APPROVE.

**Selection:**
```
[X] APPROVED
[ ] REJECTED
```

### Decision 3 — Freeze Criteria F-5 and F-6

F-5 ownership completeness · F-6 declared mode enforcement. Basis §6. Recommendation: APPROVE.

**Selection:**
```
[X] APPROVED
[ ] REJECTED
```

### Decision 4 — No New Governance Surface Principle

No new registry, authority layer, schema family, or constitutional document for gate mode
governance. Basis §7. Recommendation: APPROVE.

**Selection:**
```
[X] APPROVED
[ ] REJECTED
```

### Decision 5 — Findings Classification Model

GP-1, GP-2, GP-3, GP-4, GP-10 are behavioural defects requiring code remediation, not
discharged by declaration or by governed-gap registration. Basis §8. Recommendation: APPROVE.

**Selection:**
```
[X] APPROVED
[ ] REJECTED
```

### Acknowledgements

```
[X] I acknowledge that approving all five decisions does NOT authorize implementation.
    IADR §8 remains unsigned and P-3 (R-4 grandfathering policy) remains unselected.

[X] I acknowledge that gate purity will NOT be closed by executing H-06 as authorized:
    4 of 45 declared, GP-1/GP-3/GP-11 terminating OPEN (residual).

[X] I acknowledge the uar-gate asymmetry (§4.5): its GP-2 code fix is authorized while its
    mode declaration is structurally blocked.
```

**Decision Authority:** Mutation Governance Owner

**Decided By:** Bipin Kumar

**Date:** 2026-08-16T20:10:00+05:30

### 9.6 Recording Constraint — What Approval Does Not Authorize

Approval of any or all five fields records **governance direction only**. It confers no
authority to act. Explicitly, approval does **not** authorize:

| Not authorized by approval | Still required |
|---|---|
| **Implementation** — no phase of CIEP v2 may begin | IADR §8 signature · P-3 (R-4 policy) · Phase 0 conditions 0.4–0.6 |
| **Declaration mutation** — no `gate_mode`, `replay_path`, or `audit_emission` written to any surface | IADR §8 signature, then per-programme Phase 3 measurement |
| **Engine modification** — no GP-2, GP-4, GP-5 or GP-10 code change | IADR §8 signature, then P-4 / P-5 identity confirmation |
| **Registry modification** — `generated-artifact-registry.json` and `mutation-governance-boundary.json` remain unchanged | Not authorized under H-06 at all (IADR §5) |

**Approval establishes what the ownership model is. It does not permit acting on it.**
This mirrors IADR §1.3: the owner decision establishes constitutional policy; implementation
authorization is a separate and later act.

### 9.7 Completion Requirement

The entry is complete only when **all five Selection blocks carry exactly one mark**, the
three Acknowledgements are marked, and `Decided By` and `Date` are populated. A partially
marked entry records no decision — mixed states are not interpolated. Per §10.3, rejection
of Decision 1 leaves gate purity with no available path, since the alternatives are refused
by Decisions 3 and 4; a rejection should therefore be accompanied by the substitute direction
the owner intends.

---

## 10. Effect of This Record

### 10.1 On Approval of All Five

| Resolved | Still blocked |
|---|---|
| O-3 — Class A/B scope extension | IADR §8 signature |
| O-6 — no new surface creation | P-3 — R-4 grandfathering policy |
| O-7 — acceptance criteria | Phase 0 conditions 0.4, 0.5, 0.6 (CIEP v2) |
| ODDP D-1, D-2, D-3, D-4, D-5 | O-4 (UGA), O-5 (URR) — but see §10.2 |

The ownership model becomes complete and coherent: 45 targets, 22 declarable on existing
surfaces, 23 governed gaps in an existing register, zero new surfaces.

### 10.2 O-4 and O-5 Become Low Priority

`uga-declaration.json` and `urr-declaration.json` own **no** `*-gate` target — UGA gates
through a subcommand; URR has no gate target. Resolving O-4 and O-5 would raise `*-gate`
coverage by **zero**. They remain open but are not on the critical path.

### 10.3 On Rejection of Decision 1

Declarable coverage stays at 4 of 45 and 41 targets remain undispositioned. Freeze F-1 and
F-5 stay unreachable. Gate purity remains blocked with no available path — because the
alternatives (new surface class, or declaring modes nothing reads) are refused by Decisions 4
and 3 respectively.

---

## 11. Corrections to Canonical Evidence

Two count defects in `GATE-PURITY-DETERMINATION.md`'s findings register were measured during
preparation. Both are recorded, neither corrected — this record modifies no file.

| # | Register states | Measured | Evidence |
|---|---|---|---|
| 1 | GP-1 affects **15 engines** | **16** | The "same shape, same conclusion" table has 15 rows; `UCL-000001` is documented separately at line 101 as the "canonical, fully verified example" and does not appear in the table. Confirmed at HEAD: `ucl_engine.py:3030 written = write_registers(model)` unconditional; `:3058 if args.gate and model["gate"] != "OPEN": return 1` — verdict after the write. |
| 2 | GP-3 affects **8 targets** | **10** | The GP-3 paragraph enumerates `roadmap-gate`, `corpus-gate`, `assimilate-gate`, `closure-gate`, `closure-phase2-gate`, `closure-phase3-gate`, `closure009-gate`, `closure009-baseline-gate`, `lifecycle-closure-gate`, `final-closure-gate` — 10 distinct gate targets. |

Both are the same class as the mixed-baseline plane counts (rebase §2.3): **GATE-PURITY's
evidence is sound; its counts are not.** All three must be corrected together when the
document is updated at Task-010, per rebase criterion R-7.

Neither correction changes any authorized action. GP-1 and GP-3 remediation are outside
authorized scope.

---

## 12. Decision Summary

| # | Decision | Recommendation | Basis |
|---|---|---|---|
| 1 | Ownership disposition — 22 declarable / 23 governed gaps | **APPROVE** | Declarable set and enforceable set are **identical** (22 of 22). 22 of the 23 gaps have no guard, so a declaration there would be unverifiable. |
| 2 | Revised GP-11 — disposition coverage + declaration integrity | **APPROVE** | Six defects in the original; the revised criterion is satisfiable because it accepts an owned gap as a terminal state. |
| 3 | Freeze F-5 ownership completeness · F-6 declared mode enforcement | **APPROVE** | F-5 closes the mechanism that produced GP-11; F-6 closes the mechanism that produced GP-5. Both free to satisfy under Decision 1. |
| 4 | No new governance surface creation | **APPROVE** | Four candidate hosts examined and refused. The complete model requires nothing new. |
| 5 | GP-1/2/3/4/10 remain implementation findings | **APPROVE** | Declaration records permission; it does not fix write-order, dead flags, unguarded emit, or render/gate coupling. PRODUCER without a tested replay path is reclassification-as-conformance, refused by GATE-PURITY D-3.6. |

### 12.1 The Decision In One Paragraph

Forty-five gate targets. Twenty-two have both a surface that can carry a mode and a guard that
would read it — and those two sets are exactly the same twenty-two, which is why this cut is
the repository's own boundary rather than an imposed one. Twenty-three cannot be declared
honestly and become governed gaps with named owners. The declarable half contains all of GP-1,
GP-4 and GP-10 and two thirds of GP-2; the gap half contains all of GP-3 and the one GP-2
engine that is structurally blocked. Nothing new is created. Gate purity does not close — the
five behavioural findings remain implementation work — but the ownership model becomes
complete, and for the first time closure becomes reachable.

---

## 13. Decision Entry Log

Every entry attempt against §9 is logged here, whether or not it recorded a selection. This
makes the *absence* of a decision as auditable as its presence.

**Logging rule.** A transmission that carries zero marks is logged as an **open entry**, not as
a decision. No entry in this log implies completion, and completion is never inferred from the
fact that an entry occurred. An entry is recorded as completing the decision only when it
satisfies §9.7 in full: five marks, three acknowledgements, `Decided By`, and `Date`.

| # | Date | Authority under which transmitted | Fields transmitted | Marks received | Recorded | Entry state |
|---|---|---|---|---|---|---|
| E-1 | 2026-08-16 | "OWNER DECISION RECORDING ONLY" | 5 of 5 | **0** — every field arrived with both `APPROVED` and `REJECTED` unmarked | **NO SELECTION RECORDED** | **OPEN** |
| E-2 | 2026-08-16 | "OWNER DECISION ENTRY ONLY" | 5 of 5 | **0** — no owner value supplied for any field; `Decided By` and `Date` not transmitted | **NO SELECTION RECORDED** | **OPEN** |
| E-3 | 2026-08-16 | "OWNER DECISION ENTRY" — owner values transmitted | 5 of 5 | **5** — `APPROVED` on Decisions 1, 2, 3, 4, 5 · `REJECTED` on none · acknowledgements **Acknowledged** (3 of 3) · `Decided By` **Bipin Kumar** · `Date` **2026-08-16T20:10:00+05:30** | **DECISION RECORDED — 5 APPROVED / 0 REJECTED** | **CLOSED** |

**Cumulative state: 3 entries processed · E-1 and E-2 zero-mark and OPEN · E-3 recorded the
decision — 5 of 5 fields selected, all APPROVED, §9.7 satisfied in full.** No mark in E-3 was
inferred, defaulted, or interpolated; each was transmitted explicitly. Validation of E-2 is
recorded at `H-06-OWNERSHIP-DISPOSITION-OWNER-DECISION-ENTRY-VALIDATION-DETERMINATION.md` §4;
validation of E-3 is recorded at
`H-06-OWNERSHIP-DISPOSITION-OWNER-DECISION-VALIDATION-DETERMINATION.md`.

### 13.1 Disposition of Entries E-1 and E-2

Both entries instructed that the owner's decision be processed for all five fields. The
transmitted fields carried no marks in either case. **No selection was recorded, and none was
inferred.**

**Why no selection was inferred.** Marking a field the owner left blank would fabricate a
constitutional act. It is the same defect class this determination chain exists to correct:

| Precedent | Defect | Discipline applied |
|---|---|---|
| GP-5 | `verify.sh` stage 4 declared "Read-only"; the stage writes. An unverified claim recorded as fact. | A claim must be verified, not asserted |
| Rebase §2.3 | GATE-PURITY plane counts measured against the dirty tree, then inherited as baseline fact | Measure the thing you cite |
| IADR §8 | Unsigned throughout the chain; every determination recorded it as unsigned rather than assuming intent | An unpopulated field is not a decision |

The IADR §8 precedent is directly controlling. That field has remained unsigned across nine
determinations, and each recorded it as unsigned —
H-06-IMPLEMENTATION-AUTHORIZATION-SIGNATURE-VALIDATION-DETERMINATION.md §5: *"Until §8 is
signed and dated, no implementation may begin."* The same standard applies to §9. A blank
field is a blank field regardless of what the accompanying recommendation says.

**Note on recommendations.** §12 recommends APPROVE for all five, and §3 sets out the
measured basis. A recommendation is not a decision. The record would be unsound if the
recommendation were allowed to populate the field it recommends on.

### 13.2 What Completes Entry E-3

To record the decision, transmit one mark per field. Any unambiguous form is sufficient. The
shape below is a **template with placeholders, not a decision** — every value is a slot:

```
Decision 1: APPROVED
Decision 2: APPROVED
Decision 3: APPROVED
Decision 4: APPROVED
Decision 5: APPROVED
Acknowledgements: acknowledged
Decided By: Bipin Kumar
Date: 2026-08-16T20:10:00+05:30
```

The placeholders are deliberate. Per H-06-DOCUMENT-CANONICALITY-CLEANUP-DETERMINATION.md
§2.4, a governance record must not contain a second readable version of a decision — a filled
example alongside an unmarked field is precisely that ambiguity, and it is what the `.save`
finding was raised to prevent.

§10.3 states the consequence of rejecting Decision 1. On receipt, §9 is marked exactly as
transmitted, §13 gains entry E-3, and the header status changes to `DECISION RECORDED`. Until
then the header status remains `DECISION ENTRY OPEN`.

### 13.3 Non-Entry Actions Against This Record

Actions taken against this record that were **not** entries against §9 are logged separately,
so that no correction, validation, or maintenance action can be mistaken for a decision entry.

| # | Date | Authority | Action | Decision fields touched | Marks changed |
|---|---|---|---|---|---|
| C-1 | 2026-08-16 | "DOCUMENT CORRECTION ONLY" | Canonicality correction r3: terminal status statement corrected from `decision recorded` to `decision entry remains open · no owner decision recorded`; §13 log extended with E-2, logging rule, and this non-entry table; §14 attestation extended | **NONE** | **NONE — 0 before, 0 after** |

Action C-1 corrected a **status statement about** the decision. It did not touch the decision.
The defect it corrected, and the verification of the correction, are recorded at
`H-06-OWNERSHIP-DISPOSITION-DECISION-RECORD-CANONICALITY-CORRECTION-DETERMINATION.md`.

---

## 14. Record State Attestation

| Property | State |
|---|---|
| Fields presented | 5 |
| Fields marked | **5** |
| `APPROVED` marks | **5** — Decisions 1, 2, 3, 4, 5 |
| `REJECTED` marks | **0** |
| Unmarked fields | **0 of 5** |
| Acknowledgements marked | **3 of 3** |
| `Decided By` | **Bipin Kumar** |
| `Date` | **2026-08-16T20:10:00+05:30** |
| Owner signature | **recorded — attribution and date populated per §9.7** |
| Entries processed (§13) | **3 — E-1, E-2 zero-mark OPEN · E-3 RECORDED** |
| Decision entry state | **CLOSED — decision recorded at E-3** |
| §9.7 completion conditions | **10 of 10 satisfied** |
| Governance direction established | **YES — ownership disposition model adopted as stated in Decisions 1–5** |
| Ownership disposition model adopted | **YES** — 22 declarable · 23 governed gaps · 45 dispositioned |
| O-3 / O-6 / O-7 | **RESOLVED by this decision** |
| O-4 (UGA) / O-5 (URR) | **remain open** — off critical path per §10.2 |
| Implementation authorized | **NO** — IADR §8 unsigned · P-3 unselected · CIEP v2 Phase 0 conditions 0.4–0.6 unsatisfied |
| Gate purity closed | **NO** — GP-1/GP-3/GP-11 terminate OPEN (residual) per §8.4 |
| Terminal statement consistent with measured state | **YES — updated at r4** |
| Repository mutation performed | **NONE** — no declaration modified · no `gate_mode` added · no engine modified · no registry modified · `mutation-governance-boundary.json` unchanged. The r4 entry altered only §9 decision fields and this record's own status and log sections. |

**The ownership disposition model is adopted. Implementation remains unauthorized.** The
decision establishes what the ownership model is; it does not permit acting on it. Per §1.2 and
§9.6, implementation requires the IADR §8 signature and the P-3 (R-4 grandfathering policy)
selection, both of which remain outstanding and neither of which is affected by this decision.

---

*This document is an owner decision record. As of revision r4 it carries the owner's selection:
five APPROVED marks, zero REJECTED marks, three acknowledgements, `Decided By` Bipin Kumar,
`Date` 2026-08-16T20:10:00+05:30, recorded at entry E-3. Every value was transmitted explicitly
by the Mutation Governance Owner and recorded exactly as transmitted; none was inferred,
defaulted, or supplied on the owner's behalf, and the §12 recommendations were not permitted to
populate any field. Entries E-1 and E-2 were each recorded as transmitting no marks and remain
logged as OPEN. No repository file outside this record was modified in the course of this entry:
no `gate_mode` added, no declaration modified, no engine modified, no registry created or
altered, `mutation-governance-boundary.json` unchanged. HEAD remains `1f869865` on
`integration/recovery-001`.*

---

H-06 ownership disposition decision recorded.
No implementation authorized.
No repository mutation performed.
