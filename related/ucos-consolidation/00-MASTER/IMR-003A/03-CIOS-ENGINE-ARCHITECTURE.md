# CIOS-03 — CONTINUOUS IMPLEMENTATION OPERATING SYSTEM · ENGINE ARCHITECTURE

| Field | Value |
|---|---|
| MISSION | `IMR-003A` — CIOS Constitution & Architecture |
| ARTIFACT | `CIOS-03` — Engine Architecture (mission Output 3) |
| DELIVERED BY | `IMR-003A-R1` gap closure (Phase 4). **Additive**: no recovered artifact mutated. |
| ARTIFACT KIND | Architecture (`CMG-K-05`) |
| DISCHARGES | `CIOS-01` Art X.1 limb 5 — *"twenty-four engines are bound to located owners or recorded as absent"* |
| NUMERIC CONTRACT | **exactly 24 engines**, `CIOS-E-01 … CIOS-E-24`. Fixed by `CIOS-01` Art X.1; not alterable by data change (`NS-4`). |
| AUTHORITY OF ITS OWN | **NONE.** No engine confers authority on itself (`CIOS-L-11`). |
| CONFLICT RULE | `CIOS-01` governs over this artifact; a located canonical instrument governs over `CIOS-01`'s bindings. |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. WHAT AN ENGINE IS, AND IS NOT

| An engine **is** | An engine **is NOT** |
|---|---|
| a named unit of derivation with one responsibility | an authority |
| a pure function of Repository Truth + declared data (`CIOS-L-16`, `CIOS-L-17`) | a decision-maker with discretion |
| assigned to exactly one plane | a process, service, daemon, thread or deployment unit |
| bound to a located owner **or** recorded as absent-with-owner | a gate, a registry, a validator or an identity minter |
| a **declared data entry** (`CIOS-L-23`) — addable without amending law | code — CIOS creates none (`AC-12`) |

**Engines are architectural roles, not runtime artifacts.** `CIOS-01` I.1 confines CIOS to composition; an engine is the unit in which that composition is expressed. Nothing in this artifact implies a process model, a language, a protocol or an infrastructure — all of which `CIOS-L-22` forbids CIOS from enumerating.

### 1.1 Binding classes

Every engine carries exactly one:

| Class | Meaning | Consequence |
|---|---|---|
| **BOUND** | the engine's mechanism is wholly owned by a located instrument; CIOS composes, adds nothing | zero duplication risk; the located owner governs |
| **COMPOSING** | the engine sequences or confines located mechanisms; the *composition* is CIOS's contribution, justified by `CIOS-01` Art VII.3 | must cite the Art VII.3 row that authorizes it |
| **ABSENT** | the mechanism does not exist in the repository; recorded as a gap with a named owner | recorded in `CIOS-19`; **never** silently invented |

`CIOS-01` Art VII.3 authorizes exactly nine CIOS contributions. **No engine may be COMPOSING without citing one of those nine rows.** This is the structural guard against CIOS acquiring mechanism ownership (`CIOS-01` VIII.4).

---

## 2. THE 24 ENGINES

Engine `CIOS-E-nn` holds ports `CIOS-P-(2n-1)` inbound and `CIOS-P-(2n)` outbound (48 ports total; see `CIOS-05`).

### 2.1 `CIOS-PL-A` — ASSIMILATION PLANE · `CIOS-E-01 … CIOS-E-14`

| ID | Engine | Responsibility (one sentence) | Class | Located owner / basis |
|---|---|---|---|---|
| `CIOS-E-01` | **Submission Intake** | Accept a submission of any kind into `CIOS-PT-00` and assign it nothing but a provisional handle. | COMPOSING (VII.3 r9) | `UCCEP-000000` `G-01`; `UAKOS` intake |
| `CIOS-E-02` | **Context Assimilation** | Establish that the submission's context is fully assimilated before any substantive stage runs. | BOUND | `UCCEP-000000` `G-01` Context Assimilation Gate |
| `CIOS-E-03` | **Knowledge Recurrence** | Determine whether the submission's knowledge already exists; resolve recurrence to EXTEND, never CREATE. | BOUND | `UAKOS-CLOSURE-002` charter; `CK-CLOSURE-P1`, `CK-CLOSURE-P2`; `G-02` |
| `CIOS-E-04` | **Canonical Home Resolution** | Resolve the single canonical home and single owner for the submission. | BOUND | `UAKOS-CLOSURE-002` (`duplicate_canonical_homes`, `not_homed_concepts`); `CEP-001` LAW-4 |
| `CIOS-E-05` | **Overlap Resolution** | Resolve scope overlap between the submission and any admitted item to a single owner before admission; unresolved overlap is a non-admission. | BOUND | `CIOS-L-10`; `IAC-001D` §05 Reuse Gate; `UCCEP-000000` `G-03` Reuse Gate |
| `CIOS-E-06` | **Duplication Detection** | Detect any second canonical home, owner, identifier, plan, queue, gate or authority the submission would create. | BOUND | `CEP-001` LAW-4; `06-DUPLICATION-AND-OVERLAP-VERIFICATION.md`; `GOV-001` Part 10 |
| `CIOS-E-07` | **Identity Composition** | Compose the 22-field identity record from fields produced by located minting authorities; **mint nothing**. | COMPOSING (VII.3 r9) | `AIF` (`AIF-L02`, `L04`, `L06`, `L07`, `L14`); `REG-AUTO-001`; `00-BOOK/tools/` |
| `CIOS-E-08` | **Dependency Admission** | Establish that every declared dependency of the submission resolves and introduces no cycle. | BOUND | `UCCEP-000000` `G-08` Dependency Gate; `CK-GRAPH`; `engine/graph` |
| `CIOS-E-09` | **Impact Assessment** | Produce the `CEP-009` III.1 impact assessment for the submission and classify it to exactly one primary class. | BOUND | `CEP-009` III.1, IV.1, IV.6 |
| `CIOS-E-10` | **Partition Assignment** | Move an admitted submission `CIOS-PT-00 → CIOS-PT-03`; reject any other transition. | COMPOSING (VII.3 r3) | `CIOS-01` Art V |
| `CIOS-E-11` | **Plan Epoch Composition** | Compose the staged candidate `PLAN[n+1]` without touching `PLAN[n]`. | COMPOSING (VII.3 r4) | `CIOS-01` Art VI |
| `CIOS-E-12` | **Priority Derivation** | Derive a **total** order over `CIOS-PT-03` from the declared key vector `CIOS-K-*`. | COMPOSING (VII.3 r6) | `IEC-001` `04` (`wave, family, id` preserved as leading elements); `IMG-001` `05` |
| `CIOS-E-13` | **Realignment** | Resequence `CIOS-PT-03` **only**; never reach `CIOS-PT-02` or `CIOS-PT-01`. | COMPOSING (VII.3 r8) | `CIOS-L-19`; `CIOS-12` |
| `CIOS-E-14` | **Quiescent Adoption** | Adopt `PLAN[n+1]` atomically at the located batch-cut boundary, applying it only to `CIOS-PT-03`. | COMPOSING (VII.3 r4) | `CIOS-01` VI.2; `IEC-001` `05` batch-cut boundary |

### 2.2 `CIOS-PL-B` — EXECUTION PLANE · `CIOS-E-15 … CIOS-E-18`

| ID | Engine | Responsibility | Class | Located owner / basis |
|---|---|---|---|---|
| `CIOS-E-15` | **Ready Handoff** | Hand the head of `CIOS-Q-04` to the located Execution Queue and relinquish all further control. | COMPOSING (VII.3 r1) | `IEC-001` `04` Execution Queue; C5 Queue Manager |
| `CIOS-E-16` | **Dispatch Window** | Bind the dispatched item to the plan epoch active at dispatch and hold that binding until terminal state. | COMPOSING (VII.3 r4) | `CIOS-INV-04`; `IEC-001` C7, `05` |
| `CIOS-E-17` | **Interruption Guard** | Reject every attempt to interrupt, suspend, mutate, reorder or invalidate a dispatched item. | COMPOSING (VII.3 r7) | `CIOS-L-03`; `IEC-001` C11 gate composition |
| `CIOS-E-18` | **Override Adjudication** | Admit a reach into protected or sealed work **only** from a located override authority (`CIOS-OR-01`, `CIOS-OR-02`) under declared, evidenced, recorded protocol. | COMPOSING (VII.3 r7) | `CIOS-L-21`; `CEP-009` Art III / Art XX.2; `CIOS-11` §4 |

### 2.3 `CIOS-PL-C` — TRUTH PLANE · `CIOS-E-19 … CIOS-E-21`

| ID | Engine | Responsibility | Class | Located owner / basis |
|---|---|---|---|---|
| `CIOS-E-19` | **Seal Transition** | Move a terminal item `CIOS-PT-02 → CIOS-PT-01`; fail closed if any precondition is unmet. | COMPOSING (VII.3 r3) | `CEP-007` (seal authority — located); `IEC-001` `06` terminal states |
| `CIOS-E-20` | **Truth Append** | Append the record of what became true; never edit, never delete. | BOUND | `AIF-L08`, `AIF-L17`; `CEP-008`; `UAKOS` `closure.json` |
| `CIOS-E-21` | **Traceability Emission** | Emit the `id → artifact` traceability binding for the sealed item. | BOUND | `CEP-008`; `UMB-007`; `UCCEP-000000` `07-UNIVERSAL-TRACEABILITY-GRAPH.md` |

### 2.4 `CIOS-PL-D` — OBSERVATION PLANE · `CIOS-E-22 … CIOS-E-24`

| ID | Engine | Responsibility | Class | Located owner / basis |
|---|---|---|---|---|
| `CIOS-E-22` | **Invariant Observation** | Evaluate `CIOS-INV-01 … INV-12` over observable state and emit a finding per breach. | COMPOSING (VII.3 r2) | `CIOS-01` Art III; `CK-SELF-DECLARATION`, `CK-SELF-WRITE-SCOPE` |
| `CIOS-E-23` | **Monotonicity Observation** | Observe that the certified set is monotone non-decreasing across epochs. | BOUND | `CEP-001` LAW-7; `CK-HEALTH`; `CIOS-L-20`, `CIOS-INV-10` |
| `CIOS-E-24` | **Determinism Observation** | Observe that identical Repository Truth and declared data yield identical verdicts, order, epoch and schedule. | BOUND | `CEP-001` LAW-8; `CK-RIE-DETERMINISM`, `CK-DETERMINISM-BUILD`, `CK-SELF-DETERMINISM` |

---

## 3. ENGINE COUNT AND CLASS RECONCILIATION

| Plane | Engines | Range |
|---|---|---|
| `CIOS-PL-A` Assimilation | **14** | `E-01 … E-14` |
| `CIOS-PL-B` Execution | **4** | `E-15 … E-18` |
| `CIOS-PL-C` Truth | **3** | `E-19 … E-21` |
| `CIOS-PL-D` Observation | **3** | `E-22 … E-24` |
| **Total** | **24** | matches `CIOS-01` Art X.1 |

| Class | Count | Engines |
|---|---|---|
| **BOUND** | **11** | `E-02`, `E-03`, `E-04`, `E-05`, `E-06`, `E-08`, `E-09`, `E-20`, `E-21`, `E-23`, `E-24` |
| **COMPOSING** | **13** | `E-01`, `E-07`, `E-10`, `E-11`, `E-12`, `E-13`, `E-14`, `E-15`, `E-16`, `E-17`, `E-18`, `E-19`, `E-22` |
| **ABSENT** | **0** | — |
| **Total** | **24** | |

**Zero engines are ABSENT.** Every engine either binds a located mechanism or composes located mechanisms under an Art VII.3 authorization. This is the strongest available evidence that CIOS acquired no mechanism ownership.

### 3.1 COMPOSING engines mapped to their Art VII.3 authorization

Each of the nine authorized contributions is claimed by at least one engine, and no engine claims an unauthorized contribution.

| Art VII.3 row | Contribution | Claimed by |
|---|---|---|
| r1 | pre-Execution-Queue queue family `CIOS-Q-01…04` | `E-15` |
| r2 | plane separation and write-scope confinement | `E-22` |
| r3 | work-set partitioning (mutability partitions) | `E-10`, `E-19` |
| r4 | epoch / copy-on-write plan adoption | `E-11`, `E-14`, `E-16` |
| r5 | unbounded wave successor function | *(`CIOS-10` §3 — a declared function, not an engine)* |
| r6 | declared priority key vector | `E-12` |
| r7 | implementation protection model | `E-17`, `E-18` |
| r8 | future-only realignment function | `E-13` |
| r9 | 24-stage admission lifecycle binding | `E-01`, `E-07` |

Row r5 is discharged by a declared function in `CIOS-10` §3 rather than by an engine; recorded here so the mapping is exhaustive and no row is silently dropped.

---

## 4. STRUCTURAL PROPERTIES

| Property | Statement | Enforced by |
|---|---|---|
| **Single plane** | Every engine belongs to exactly one plane. | §2; `CIOS-INV-02` |
| **Single responsibility** | Every engine has exactly one responsibility statement. | `CIOS-04` |
| **No self-authority** | No engine confers authority on itself. | `CIOS-L-11`; §1.1 |
| **No engine is a gate** | Engines evaluate and compose; gates are located. | `CIOS-01` I.6; `AC-4` |
| **No engine mints identity** | `E-07` composes only. | `CIOS-L-12`, `L-14`; `CIOS-01` I.5 |
| **No engine dispatches** | `E-15` hands off; `IEC-001` C7 dispatches. | `CIOS-01` I.4 |
| **Acyclic** | The engine dependency graph is a DAG. | `CIOS-INV-05`; proven in `CIOS-06` |
| **Declared, not hard-coded** | The engine set is a data entry in `cios-bindings.json`. | `CIOS-L-23` |
| **Zero enumeration** | No engine names a domain, technology, vendor, platform, language, protocol or format. | `CIOS-L-22`; `CK-SELF-NO-ENUMERATION` |
| **Deterministic** | Every engine is a pure function of Repository Truth + declared data. | `CIOS-L-17`; `E-24` observes |

### 4.1 Cardinality is fixed, membership is declared

A subtlety that matters for `CIOS-L-23` and `NS-4`:

- **Adding a member** to a declared family (a queue, a key element, a gap) is a **data change** to `cios-bindings.json`; it amends no law.
- **Changing the count of engines, stages or identity fields** is **not** a data change, because `CIOS-01` Art X.1 fixes those three numbers as its own closure test. Altering them requires a `CEP-009` III.1 change to `CIOS-01` itself.

This is why `CIOS-01` Art X.1 is the numeric contract and this artifact conforms to it rather than choosing its own counts.

---

## 5. NO DUPLICATE RESPONSIBILITIES

The recovery instruction requires that no duplicate responsibilities remain. Verified pairwise over the boundaries where duplication is plausible:

| Engine pair | Apparent overlap | Boundary that separates them |
|---|---|---|
| `E-03` Knowledge Recurrence / `E-06` Duplication Detection | both concern "already exists" | `E-03` asks *does this knowledge exist?* (content); `E-06` asks *would this create a second owner/home/identifier?* (structure) |
| `E-04` Canonical Home / `E-06` Duplication | both concern homes | `E-04` **resolves** the one home; `E-06` **detects** a second one |
| `E-05` Overlap / `E-06` Duplication | both concern collision | `E-05` resolves *scope* overlap between two admitted items; `E-06` detects *artifact-level* duplication |
| `E-10` Partition Assignment / `E-19` Seal Transition | both move partitions | `E-10` owns `PT-00 → PT-03` only; `E-19` owns `PT-02 → PT-01` only. Disjoint transitions. |
| `E-11` Plan Epoch / `E-14` Quiescent Adoption | both concern epochs | `E-11` **composes** the candidate; `E-14` **adopts** it. Compose ≠ adopt. |
| `E-12` Priority Derivation / `E-13` Realignment | both order `PT-03` | `E-12` derives the order from the key vector; `E-13` decides *when* to re-derive. Function vs trigger. |
| `E-17` Interruption Guard / `E-18` Override Adjudication | both gate reaches into protected work | `E-17` rejects **all** interruption; `E-18` admits **only** the two located override authorities. Default-deny vs narrow-allow. |
| `E-22` Invariant / `E-23` Monotonicity | both observe | `E-23` observes exactly `CIOS-INV-10`; `E-22` observes the other eleven. Disjoint by construction. |

**Duplicate responsibilities: 0.**

---

## AUTHORITY BOUNDARY (MANDATORY)

This artifact declares an engine set. It owns no mechanism, no registry, no gate, no identifier space and no concern. No engine described here holds authority; every authority named is located in an instrument existing independently at `b26c5bb`. Where this artifact and a located canonical instrument disagree, **the located instrument governs and this artifact SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `CIOS-03` · PROVISIONAL · ADDITIVE · COMPOSITION-ONLY · AUTHORITY-NEUTRAL**
