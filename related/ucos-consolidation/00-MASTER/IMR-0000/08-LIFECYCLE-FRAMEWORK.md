# IMR-0000/08 — LIFECYCLE FRAMEWORK

| Field | Value |
|---|---|
| MISSION | `IMR-0000` — CIOS Platform Foundation |
| ARTIFACT | `08` — Lifecycle Framework (**deliverable 18**) · directive capability 28 |
| ARTIFACT KIND | Framework (`CMG-K-05`) — **axis reconciliation**, zero new states |
| CLOSES | `00A` `PGAP-09` — five located lifecycle models exist; their orthogonality is asserted pairwise in three artifacts and reconciled in none |
| NUMERIC CONTRACT | **4 axes** `LX-1 … LX-4` · **7 rules** `LR-1 … LR-7` · **0 new states, 0 new transitions** |
| CENTRAL CLAIM | **The platform introduces no lifecycle.** Every state named is located. The framework's contribution is the axis map: which located model answers which question, and how the axes compose without colliding. |
| AUTHORITY OF ITS OWN | **NONE.** |
| CONFLICT RULE | Located instrument governs (`REG-AUTO-001` §5 for the master lifecycle; `IEC-001` `06` for item state; `CMG-000001` for artifact state); then `IMR-003A` (`CIOS-01` Art V, `CIOS-07`); then this artifact. |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. THE PROBLEM: FIVE MODELS, NO MAP

At `b26c5bb` an object can simultaneously be `ACTIVE`, `READY`, `CIOS-PT-03`, at `CIOS-S-19`, and `UNDER_REVIEW`. All five statements can be true at once. Nothing in the corpus says so.

| Located model | Owner | Cardinality | Answers |
|---|---|---|---|
| Master artifact lifecycle | `REG-AUTO-001` §5 | **7** — `DRAFT → GENERATED → REGISTERED → ACTIVE → CERTIFIED → FROZEN → ARCHIVED` | *what is this artifact's standing in the corpus?* |
| `CMG-REGISTRY.json` `states` | `CMG-000001` | **14** states, **22** transitions | *what is this constitutional artifact's governance state?* |
| Item execution state | `IEC-001` `06` | **10** | *where is this work item in execution?* |
| Mutability partition | `CIOS-01` Art V | **4** — `PT-00`, `PT-03`, `PT-02`, `PT-01` | *what may be written?* |
| Admission stage | `CIOS-07` | **24** — `S-01 … S-24` | *what determination has been made?* |

**Three pairwise orthogonality claims exist already** — `CIOS-07` §1 (stage ≠ item state ≠ partition), `CIOS-19` §3 rows 2 and 3 (partition ⊥ item state; stages ⊥ execution lifecycle), and `UCI-OPT-001` row 3 (*"one master lifecycle; change/knowledge/version/rollback are states within it"*). No instrument states the whole. A future programme therefore has to rediscover, for each question it asks, which of five models to consult — and the cheapest wrong answer is to invent a sixth.

**`UUP-04` is the law this framework serves:** *one lifecycle per axis, and the axes are orthogonal, not alternative.* A sixth model would be a second lifecycle on an existing axis, which is a uniqueness breach, not a modelling choice.

---

## 2. THE FOUR AXES

The five located models resolve onto **four axes**. Two of the five occupy the same axis and are reconciled in §2.1.

| Axis | Question | Located owner | States | Applies to |
|---|---|---|---|---|
| **`LX-1` STANDING** | What is this object's standing in the corpus? | `REG-AUTO-001` §5 (7 states) · `CMG-000001` `states` (14) for constitutional artifacts · `STATUS-001` for status determination | 7 / 14 | every canonical object (`UOM-A-14`) |
| **`LX-2` ADMISSION** | What determination has been made about this submission? | `CIOS-07` — `CIOS-S-01 … CIOS-S-24` | 24 | submissions only |
| **`LX-3` MUTABILITY** | What may be written to this object right now? | `CIOS-01` Art V — `CIOS-PT-00`/`03`/`02`/`01` | 4 | submissions and work items |
| **`LX-4` EXECUTION** | Where is this work item in execution? | `IEC-001` `06` | 10 | dispatched work items only |

### 2.1 Why `REG-AUTO-001` §5 and `CMG-REGISTRY.json` `states` share one axis

They are not two axes and not two lifecycles. They are **one axis at two scopes**:

| | `REG-AUTO-001` §5 | `CMG-REGISTRY.json` `states` |
|---|---|---|
| Scope | every registered artifact | constitutional artifacts under `CMG-000001` |
| Cardinality | 7 | 14 states / 22 transitions |
| Relationship | the **general** standing sequence | the **constitutional refinement** of it, adding governance-specific states (`PLANNED`, `UNDER_REVIEW`, `SUPERSEDED`, `RETIRED`, …) |
| Conflict rule | for a constitutional artifact, `CMG-000001` governs; for any other registered artifact, `REG-AUTO-001` §5 governs | — |

`UCI-OPT-001` fixes this reading: *"**One** master lifecycle (`REG-AUTO-001` §5). Change/knowledge/version/rollback/certification are **states within it**, not new machines."* The 14 `CMG` states are a refinement within the one machine, not a second machine. Recorded here because a reader encountering both counts (7 and 14) will otherwise conclude there are two lifecycles — and then reasonably ask which is authoritative.

---

## 3. THE AXIS COMPOSITION MAP

The framework's substantive output: what an object's full lifecycle position looks like, per object kind, and which axes are inapplicable.

| Object kind | `LX-1` STANDING | `LX-2` ADMISSION | `LX-3` MUTABILITY | `LX-4` EXECUTION |
|---|---|---|---|---|
| Programme | ✓ (`CMG` 14 or `REG-AUTO` 7) | — | — | — |
| Mission / work package | ✓ | — | — | — |
| Artifact | ✓ | — | — | — |
| **Submission** | ✓ (once registered) | ✓ **all 24 stages** | ✓ **all 4 partitions** | ✓ **during the located interval only** |
| Capability | ✓ | — | — | ✓ (as a work item) |
| Subsystem | ✓ via its declaring artifact only | — | — | — |
| Interface | ✓ | — | — | — |
| Contract | ✓ | — | — | — |
| Concept | ✓ (`closure.json` determination) | — | — | — |
| Decision | ✓ (disposition state) | — | — | — |
| Evidence item | append-only; no state machine | — | — | — |
| Checkpoint | append-only; no state machine | — | — | — |

**Only submissions occupy all four axes.** That is the reason `CIOS-07`, `CIOS-01` Art V and `IEC-001` `06` all exist and all differ: each answers a different question about the same submission. Every other object kind occupies `LX-1` alone, plus `LX-4` where it is realized as a work item.

### 3.1 The submission's four simultaneous positions

Worked through the located models, to make the orthogonality concrete rather than asserted.

| Point in life | `LX-2` stage | `LX-3` partition | `LX-4` item state | `LX-1` standing |
|---|---|---|---|---|
| submitted | `S-01` | `PT-00` INTAKE | — | — |
| traversing determinations | `S-02 … S-18` | `PT-00` — **still not admitted** | — | — |
| admitted, planned | `S-19 … S-22` | `PT-03` OPEN | — | `REGISTERED` |
| handed off | `S-23` | `PT-02` IN-FLIGHT | `READY` → … | `ACTIVE` |
| **inside the located interval** | **no CIOS stage** (`CIOS-07` §3) | `PT-02` | all 10 states available | `ACTIVE` |
| terminal, sealed | `S-24` | `PT-01` SEALED | terminal | `CERTIFIED` (ceiling-bound) |

**The interval between `S-23` and `S-24` is deliberately empty of CIOS stages.** Declaring a stage there would create a second lifecycle over `IEC-001`'s mechanism — a `CIOS-L-09` and `CEP-001` LAW-4 breach. The emptiness is constitutional, not an omission (`CIOS-07` §3).

---

## 4. LIFECYCLE RULES

| ID | Rule | Located basis |
|---|---|---|
| `LR-1` | **One lifecycle per axis.** An object has exactly one position on each applicable axis. A second model on an existing axis is a uniqueness breach, not an extension. | `UUP-04`; `UCI-OPT-001` row 3 |
| `LR-2` | **Axes are orthogonal, not alternative.** A position on one axis neither implies nor constrains a position on another, except where a located instrument declares a correspondence (`CIOS-07` §4.2 is the one such declaration). | `CIOS-07` §1; `CIOS-19` §3 rows 2–3 |
| `LR-3` | **No new state, no new transition.** The platform introduces none on any axis. A capability that appears to need one is a **state within an existing machine**, or it is a gap for the axis owner. | `UCI-OPT-001` row 3; `RF-1` |
| `LR-4` | **Every transition is gated and recorded.** An ungated or unlogged transition is a `CIOS-INV-08` breach and is inadmissible. | `CIOS-INV-08`; `LT-3` |
| `LR-5` | **Transitions are forward-only.** Correction is by successor; rollback is a **new forward change**, never a reversal. The sole located exception is `IEC-001` `06`'s `FAILED → READY` retry, bounded by `MAX_RETRY`, which the platform binds and does not redefine. | `AIF-L17`; `UCI-OPT-001` row 7; `CIOS-01` V.3; `LT-5` |
| `LR-6` | **`LX-3` governs writability, and nothing else does.** No standing, stage or execution state confers or withholds write authority; only the mutability partition does. | `CIOS-01` Art V; `CIOS-INV-02` |
| `LR-7` | **`FROZEN` on `LX-1` is `CEP-007`'s state and is currently unreachable.** `CIOS-PT-01` SEALED is **not** a `CEP-007` freeze state. Conflating them would make an unauthorized freeze claim. | `CIOS-11` §2.1; `CEP-007`; `GD-10`; `CIOS-GAP-13` |

### 4.1 The two conflations `LR-6` and `LR-7` prevent

Recorded because both are natural mistakes with constitutional consequences.

| Conflation | Why it is wrong | Consequence if made |
|---|---|---|
| "`CERTIFIED` means immutable" | `CERTIFIED` is an `LX-1` standing. Immutability is `LX-3` `PT-01`. An object can be `CERTIFIED` and still resequenceable if it is in `PT-03`. | writes blocked that are lawful, or permitted that are not |
| "`PT-01` SEALED means FROZEN" | `PT-01` is a **mutability partition** owned by `CIOS-01` Art V. `FROZEN` is a `CEP-007` **freeze state**, and freeze is **unavailable** at `b26c5bb`. | an implied freeze claim, which under `CEP-007` II.4 / IV.4 would be **void** and would place the Program in HALTED |

---

## 5. GATE BINDING ACROSS AXES

`LR-4` requires every transition to be gated. Which gate binds which axis:

| Axis | Transition class | Located gate / mechanism |
|---|---|---|
| `LX-1` | `DRAFT → GENERATED → REGISTERED` | `REG-AUTO-001` transaction `T`; `G-07` Registry Gate |
| `LX-1` | `→ ACTIVE` | `STATUS-001` status determination; `G-06` Repository Truth Gate |
| `LX-1` | `→ CERTIFIED` | `CEP-005`; `G-11`; EC-3 certification gate; `IEC-001` Q6/C9 |
| `LX-1` | `→ FROZEN` | `CEP-007` — **unavailable** (`GD-10`); `LR-7` |
| `LX-1` | `→ ARCHIVED` / `SUPERSEDED` / `RETIRED` | `CEP-009` Art IV.3/XI; `UCI-001`; `Supersedes` edges |
| `LX-2` | `S-01 … S-24` | **14 located gates `G-01 … G-14`**, all bound; 20 stages gate-bound, 4 self-check-bound (`CIOS-07` §4) |
| `LX-3` | `PT-00 → PT-03` | `SS-01` `E-10` + `G-06` + self-check `CIOS-CK-PARTITION` |
| `LX-3` | `PT-03 → PT-02` | the located Execution Queue's acceptance (`IEC-001` `04`); `G-13` |
| `LX-3` | `PT-02 → PT-01` | `SS-01` `E-19` + `G-14`; fail closed, **no partial seal** |
| `LX-4` | all 10 states | `IEC-001` `06`; quality gates `Q1 … Q8`; READY predicates `P1 … P7` |

| Property | Value |
|---|---|
| Axes | **4** |
| Located models reconciled | **5** |
| New states introduced | **0** |
| New transitions introduced | **0** |
| New state machines introduced | **0** |
| Located gates bound across axes | **14 / 14** (`G-01 … G-14`) |
| Transitions with no gate | **1** — `S-01` pre-gate intake, which is outside every plan (`CIOS-01` Art V) |
| Axes on which freeze is reachable | **0** (`LR-7`) |

---

## 6. WHAT THIS FRAMEWORK DOES NOT DO

| Not done | Located owner |
|---|---|
| Define, add, rename or remove a state on any axis | `REG-AUTO-001` §5; `CMG-000001`; `IEC-001` `06`; `CIOS-01` Art V; `CIOS-07` |
| Define a transition, or alter a transition's gate | the axis owner; `G-01 … G-14` |
| Evaluate an object's position on any axis | `STATUS-001`; `IEC-001`; `engine/validation` |
| Re-state the 24 admission stages or the 10 item states | `CIOS-07`; `IEC-001` `06` — bound by pointer, `CIOS-L-08` |
| Declare a stage inside the located execution interval | `CIOS-07` §3 — constitutionally empty |
| Assert or imply a freeze on `LX-1` | `CEP-007`; `LR-7`; `CIOS-GAP-13` |
| Create a change, rollback or version state machine | `UCI-OPT-001` — expressly prohibited; those are states within the one machine |

---

## AUTHORITY BOUNDARY (MANDATORY)

This framework reconciles five located lifecycle models onto four orthogonal axes. **It introduces no state, no transition and no state machine.** It evaluates no object's position, gates nothing, and asserts no standing. `CIOS-PT-01` SEALED is expressly **not** a `CEP-007` freeze state, and no freeze is declared, implied or recorded. Every axis owner named is located in an instrument existing independently at `b26c5bb`. Where this framework and a located canonical instrument disagree, **the located instrument governs and this framework SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `IMR-0000/08` · PROVISIONAL · ADDITIVE · DESIGN-ONLY · AUTHORITY-NEUTRAL**
