# H-06 R-4 GRANDFATHERING POLICY DECISION RECORD

| Field | Value |
|---|---|
| **ID** | H-06-R4-GPDR |
| **Authority** | DECISION RECORD PREPARATION ONLY. No policy selected herein. No implementation authorized. |
| **Phase** | Foundation Closure — Gate Purity Implementation — P-3 Resolution |
| **Baseline** | HEAD `1f869865` · branch `integration/recovery-001` |
| **Resolves** | P-3 — R-4 grandfathering policy selection |
| **Depends on** | H-06-R4-GRANDFATHERING-POLICY-DETERMINATION.md (evidence) |
| | H-06-MUTATION-GOVERNANCE-OWNER-DECISION-RECORD.md §7 (Option B ratified) |
| | H-06-PRE-IMPLEMENTATION-REPOSITORY-STATE-VALIDATION.md (boundary state) |
| | H-06-GATE-OWNERSHIP-MODEL-RESOLUTION-DETERMINATION.md (Class A/B/C/D model) |
| | H-06-OWNERSHIP-DISPOSITION-OWNER-DECISION-RECORD.md r4 §4 (Decision 1 — governing ownership model) |
| | H-06-IMPLEMENTATION-AUTHORIZATION-DECISION-RECORD-UPDATED.md §3.2, §5 (supersession record · Class B exclusion) |
| **Produced** | 2026-08-16 |
| **Status** | AWAITING OWNER SELECTION |
| **Revision** | **r2 — evidence correction 2026-08-16 under correction authority: C-5 and derived creation-act counts corrected from 36 to 23; Class A/B/C/D model and reconciliations added (§3.4); Option 2 cost restated on two grounds; disposition split into the 13 and the 23; §7 acknowledgement restated. No decision field altered — all checkboxes remain unmarked, `Selected By` and `Date` remain blank, and the §6 recommendation direction is unchanged. Pre-correction artifact preserved at `H-06-R4-GRANDFATHERING-POLICY-DECISION-RECORD.pre-r2.md`, sha256 `074582134dbdd248517bfbcee9b2ccc07dc8c780af45127526f5c6dc31ab3acb`.** |

---

## 1. Purpose

This record exists to close P-3. P-3 is one of the two constitutional acts blocking
H-06 Phase 1 (the other being the IADR §8 signature). It governs how **undeclared
mutation-capable gate entry points** are handled during the transition to the ratified
Option B multi-mode model.

The evidence determination
(`H-06-R4-GRANDFATHERING-POLICY-DETERMINATION.md`) established the two options and
their tradeoffs. This record adds the **corrected population measurement** that the
evidence determination lacked, and presents the decision field for owner selection.

---

## 2. Question Restated

Under Option B, every gate must carry a declared `gate_mode`. At the authorized baseline,
almost none do. During the period between authorization and full declaration coverage,
what is the compliance status of an undeclared gate?

- **Option 1 — Temporary Compliance Window:** undeclared gates are tracked as explicitly
  pending, with a deadline and an owner. `verify.sh` continues to pass.
- **Option 2 — Immediate Non-Compliance:** an undeclared gate fails its self-guard the
  moment `gate_mode` enforcement is activated. `verify.sh` fails until coverage is complete.

---

## 3. Corrected Population Measurement

The R-4 evidence determination sized the problem at **24 undeclared mutation paths**
(GP-1: 15 engines, GP-2: 3, GP-3: 6 additional). That figure counts *engines with
confirmed unconditional writes*. It is not the figure that governs the policy choice.

The figure that governs the policy choice is **how many gate entry points would have to
carry a declared mode before enforcement could be activated**, and **how many of those
have a declaration surface at all**. Both were measured directly at HEAD `1f869865`:

### 3.1 Gate Target Population

| Measurement | Value | Method |
|---|---|---|
| Makefile `*-gate` targets **at baseline HEAD** | **45** | `git show HEAD:Makefile \| grep -cE '^[a-z0-9._-]+-gate:'` |
| Makefile `*-gate` targets in **working tree** | 46 | `grep -cE '^[a-z0-9._-]+-gate:' Makefile` |
| Difference | `uaue-gate` | Present only in the uncommitted UAUE delta |

**The "46 gates" figure used throughout the H-06 chain — GP-11, IADR §6, CIEP §6,
ITBP §5 VG-15 — counts a gate target that does not exist at the authorized baseline.**
At `1f869865` the denominator is **45**. The 46th arrives only if the uncommitted UAUE
working-tree delta is committed. This is recorded as defect **D-1** and corrected in
H-06-IAR-AUTHORIZATION-MATRIX-CORRECTION.md.

### 3.2 Declaration Coverage of the Gate Population

| Measurement | Value |
|---|---|
| Baseline `*-gate` targets | 45 |
| Of those, having a same-named `*-declaration.json` | **9** |
| Of those, having **no** `*-declaration.json` | **36** |

The 36 gate targets with no `*-declaration.json`:

```
assimilate  closure  closure-phase2  closure-phase3  closure009
closure009-baseline  cmg  constitution  convergence  corpus
final-closure  foundation  freeze  homing  lifecycle-closure
mcos  publication  research  research-publication  rib
roadmap  rpi  selfaware  uaep  uaie  uapf  uar  ucaf
uccep  ucda  ucef  uei  uer  umk  uprf  urrc
```

### 3.3 Self-Guard Population

| Measurement | Value | Method |
|---|---|---|
| Engines carrying `--check-declaration` | **23** | `grep -rl "check-declaration" 00-MASTER --include="*.py"` (excluding `__pycache__`) |
| Of those, with a `*-declaration.json` in their own programme directory | **9** | Directory cross-reference |
| Of those, with **no** `*-declaration.json` in their own programme directory | **14** | Directory cross-reference |

The 14 engines carrying `--check-declaration` with no co-located `*-declaration.json`
resolve their declaration from a **differently-named** artifact — for example
`rib_engine.py` reads `rib-blueprint.json`, `uaie_engine.py` reads
`uaie-architecture.json`. The declaration surface is heterogeneous. See
H-06-IAR-AUTHORIZATION-MATRIX-CORRECTION.md §3, and §3.4 below for the class model this
heterogeneity produces.

### 3.4 Ownership Class Model and Reconciliation

The 36 targets without a same-named `*-declaration.json` are **not** a single population. Per
`H-06-GATE-OWNERSHIP-MODEL-RESOLUTION-DETERMINATION.md` and ownership disposition Decision 1
(`H-06-OWNERSHIP-DISPOSITION-OWNER-DECISION-RECORD.md` r4 §4, APPROVED by the Mutation
Governance Owner, 2026-08-16T20:10:00+05:30), they partition into two classes:

| Class | Count | Owning surface | Disposition |
|---|--:|---|---|
| **Class A** | **9** | Existing same-named `*-declaration.json` | Declarable — **authorized** |
| **Class B** | **13** | Existing **domain-named** surface — `rib-blueprint.json`, `ucaf-authority.json`, `uei-evolution.json`, `umk-kernel.json`, `uer-resilience.json`, `upf-provider.json`, `ucda-decisions.json`, `mcos-civilization.json`, `ucef-framework.json`, `uccep-bindings.json`, `urrc-bindings.json`, `uaep-platform.json`, `uaie-architecture.json` — differing from Class A **only in filename** | Declarable-eligible — **unauthorized** |
| **Class C** | **11** | No capable owning surface | Governed gap |
| **Class D** | **12** | No capable owning surface | Governed gap |

**Reconciliation.** Both forms derive from the §3.2 enumeration above:

```
Class A 9  +  Class B 13  +  Class C 11  +  Class D 12  =  45
22 declarable/eligible  +  23 governed gaps            =  45
9 authorized-reachable  +  13 eligible-but-unauthorized  +  23 governed gaps  =  45
```

Of the 36 targets enumerated in §3.2: **13 are Class B** and **23 are Class C or D**.

**Eligibility ≠ Authorization.** Eligibility means a capable owning surface exists and a
`--check-declaration` guard would read it. Authorization means the IADR §8 signed scope permits
writing there — the 11 `*-declaration.json` files of IAR §1.1, reaching 9 gate targets. The 13
Class B targets are **eligible and not authorized**: both halves hold simultaneously, and
updated IADR §5 excludes `gate_mode` on Class B surfaces explicitly.

This is consistent with §3.3 above: the declaration surface is heterogeneous, which is precisely
why a filename-based measurement does not establish the absence of a governance surface.

### 3.5 Consequence for the Policy Choice

| Quantity | Evidence Determination Figure | Corrected Measurement |
|---|---|---|
| Population requiring declaration before enforcement | 24 engines | **45 gate targets** (36 without a `*-declaration.json`) |
| Enforcement surface | "24 engines fail self-guard" | **23 engines carry `--check-declaration`**; 14 of them read a non-`*-declaration.json` surface |
| Authorized scope coverage | implied complete | **11 files authorized; covers at most 9 of 45 gate targets** |

**The authorized scope cannot achieve full coverage.** IAR §1.1 authorizes an additive
field on 11 `*-declaration.json` files. Even at perfect execution, that reaches **9 of
45** gate targets. **36 gate targets are outside authorized scope** — of which **13 have a
capable owning surface** (Class B, eligible but unauthorized) and **23 have none** (Class C/D,
governed gaps). See §3.4.

This is the single most important input to the R-4 decision, and it was not available
when the evidence determination was written.

---

## 4. Option Assessment Against Corrected Measurement

### 4.1 Option 2 — Immediate Non-Compliance

**Assessment: INFEASIBLE within the authorized scope.**

Option 2's own stated precondition (R-4 determination §5, Option 2, control 1) is:
"All 24 mode declarations must be prepared as a batch before the `--check-declaration`
enforcement is activated."

Against the corrected measurement, that control requires **45** declarations prepared as
a batch. Of those, **23 have no capable owning surface to write into** (Class C 11 + Class D
12), and a further **13 have a capable owning surface** (Class B) but no authorization to
write into it. Satisfying the control would therefore require creating **23** new declaration
files **and** writing modes to 13 unauthorized surfaces — acts that:

| Conflict | Source |
|---|---|
| Exceeds authorized scope — IAR §1.1 authorizes an *additive field on 11 existing files*, not file creation | IAR §1.1 |
| Is forbidden as creation of a new governance surface | IADR §5 row 2; CIEP §4 row 4 |
| Would require a fresh owner scope-extension decision | IADR §1.2 — "No scope element may be added … at the point of authorization" |
| For the 13 Class B surfaces: `gate_mode` on a Class B surface is explicitly excluded | Updated IADR §5 — Class B exclusion |

Therefore Option 2 cannot be selected without first obtaining an owner scope extension
that H-06 does not currently hold. Selecting Option 2 now would authorize, by
implication, **23** creation acts that the constitutional chain forbids, together with 13
writes to surfaces that authorization does not reach.

**Secondary risk:** if `gate_mode` enforcement were activated in `--check-declaration`
before coverage, **23 engines** would fail their self-guard simultaneously, and
`verify.sh` — which invokes several of them — would fail across the gate surface. Since
the pre-implementation `verify.sh` baseline was never captured (anomaly A-1), there would
be no known-good state to compare the breakage against.

### 4.2 Option 1 — Temporary Compliance Window

**Assessment: FEASIBLE, and the only option executable within the authorized scope.**

Option 1 permits declaration coverage to advance incrementally (9 of 45 within current
scope) while the remainder are tracked as explicitly pending: the **13** Class B targets as
eligible-but-unauthorized pending a scope extension, and the **23** Class C/D governed gaps
with named owners and a deadline. `verify.sh` continues to pass. GP-2 and GP-10 code fixes proceed as P0 — they
are defects under any mode and are not grandfathered.

The mechanism already exists in the repository: the `DECLARED-OPEN` condition pattern
used in UAUE `bootstrap_gaps` tracks a known gap with an explicit owner and discharge
condition. R-4 determination §3 records it as an existing control. Option 1 reuses it
rather than inventing a surface — satisfying the No New Governance Authority boundary.

**The risk the evidence determination named is real and must be controlled.** R-4 §5
Option 1 states: "the history of GP-11 (42/46 undeclared at baseline after years of
development) demonstrates that passive non-enforcement does not produce compliance."
A window without an enforced deadline is indistinguishable from the status quo that
produced GP-11. The controls in §5 below exist to make the window falsifiable.

---

## 5. Required Controls If Option 1 Is Selected

Option 1 is meaningful only with all six controls. Controls 1–4 are carried from the
evidence determination; controls 5–6 are added by the corrected measurement.

| # | Control | Rationale |
|---|---|---|
| C-1 | A `migration_deadline` field accompanies every pending status in a declaration | A window without a date is not a window |
| C-2 | The `--check-declaration` guard rejects the pending value **after** the deadline | Makes the deadline enforceable rather than advisory |
| C-3 | Every pending gate is registered in the existing `ASSESSMENT-CONFLICT-REGISTER.md` with a named owner | Reuses an existing surface; no new registry |
| C-4 | GP-2 and GP-10 code fixes are P0 and are **not** grandfathered | Write-before-verdict and observe-alias mutation are defects under every mode |
| C-5 | The **23 gate targets with no capable owning surface** (Class C 11 + Class D 12) are recorded as an explicit scope gap, not as pending declarations. The **13 Class B gate targets** are recorded as **eligible-but-unauthorized** — a capable owning surface exists for each — not as surface-less | For the 23: a pending status cannot be written into a file that does not exist; recording them as "pending" would fabricate coverage. For the 13: a surface exists, so the obstacle is authorization, not absence — recording them as surface-less would misstate the constitutional obstacle |
| C-6 | `gate_mode` enforcement in `--check-declaration` is **not activated** until the pending vocabulary and deadline check (C-1, C-2) are implemented and tested | Activating enforcement before the pending value is recognised reproduces Option 2's failure mode |

**C-5 is the control the earlier evidence determination could not have specified.**
Without it, Option 1 would appear to cover 45 gates while **23** of them have nowhere to
record the pending state, and a further **13** have a surface but no authorization to write
into it — the coverage claim would be unfalsifiable, which is the exact
defect class H-06 exists to eliminate.

### 5.1 Pending Vocabulary

If Option 1 is selected, the pending value is additive to the ratified vocabulary and does
not alter it. The ratified terminal vocabulary remains exactly:
`OBSERVE` · `PRODUCER` · `EXECUTION` · `OBSERVE_WITH_DECLARED_AUDIT_EMISSION`.

```json
"gate_mode": "UNDECLARED-PENDING-MIGRATION",
"migration_deadline": "<ISO 8601 date>",
"migration_owner": "<named owner>"
```

`UNDECLARED-PENDING-MIGRATION` is a **transitional** value. It is not a mode. No gate may
terminate in it. C-2 makes it self-expiring.

---

## 6. Recommendation

**Option 1 — Temporary Compliance Window, with controls C-1 through C-6 mandatory.**

Basis: Option 2 is infeasible within the authorized scope (§4.1) — its own stated
precondition requires **23** creation acts that IAR §1.1 does not authorize and IADR §5 forbids,
together with 13 writes to Class B surfaces that updated IADR §5 excludes.
Option 1 is executable within the authorized scope, reuses an existing tracking mechanism,
and keeps `verify.sh` measurable while coverage advances.

This is a recommendation on the evidence. **It is not a selection.** The selection is the
owner's act and is recorded in §7.

---

## 7. Owner Decision Field

**R-4 Grandfathering Policy Selection:**

```
[ ] OPTION 1 — Temporary Compliance Window (controls C-1..C-6 mandatory)
[ ] OPTION 2 — Immediate Non-Compliance
```

**If Option 1 selected — migration deadline for the 9 in-scope declarations:**
________________

**If Option 1 selected — disposition of the 36 out-of-scope gate targets.** A pending mode is
recordable for the 13 Class B targets (a surface exists) and is **not** recordable for the 23
Class C/D targets (no surface exists), so each population requires its own disposition:

**(a) The 13 Class B targets — eligible, unauthorized:**

```
[ ] Recorded as eligible-but-unauthorized; deferred to a separate owner scope-extension decision
[ ] Other (specify)
```
________________

**(b) The 23 Class C/D targets — no capable owning surface:**

```
[ ] Recorded as explicit scope gap; deferred to a separate owner scope-extension decision
[ ] Other (specify)
```
________________

**Acknowledgement of corrected measurement:** I have read §3 and accept that the
authorized scope of 11 `*-declaration.json` files reaches at most 9 of the 45 baseline
gate targets, and that 36 gate targets are outside authorized scope — of which **13 (Class B)
have a capable owning surface and are eligible but unauthorized**, and **23 (Class C and D)
have no capable owning surface and are governed gaps**. I accept that eligibility is not
authorization.

```
[ ] ACKNOWLEDGED
```

**Selected By:**
________________

**Date:**
________________

---

## 8. Effect of This Record

| Condition | Effect |
|---|---|
| §7 populated with Option 1 or Option 2, signed and dated | P-3 is closed. One of the two constitutional blockers to Phase 1 is cleared. |
| §7 unpopulated | P-3 remains open. Phase 1 remains blocked regardless of the IADR §8 signature. |

Closing P-3 does **not** authorize implementation. The IADR §8 signature remains an
independent and separate act. Both are required. Neither substitutes for the other.

**Constraint:** selection of Option 2 does not, and cannot, authorize the creation of the
**23** absent declaration files, nor the writing of modes to the 13 Class B surfaces that
authorization does not reach. If Option 2 is selected, implementation remains blocked until
a separate owner scope-extension decision authorizes that creation. This constraint is
constitutional, not procedural — it follows from IADR §1.2 and §5.

---

*This document is a decision record preparation artifact. It presents corrected population
evidence and a decision field for the mutation governance owner. It does not select a
policy, grant authorization, or approximate either. No source file, declaration, registry,
engine, or workflow was modified during its production. Every measurement in §3 was taken
read-only against HEAD `1f869865`.*

---

R-4 grandfathering policy decision record prepared.
Policy not selected.
No implementation executed.
