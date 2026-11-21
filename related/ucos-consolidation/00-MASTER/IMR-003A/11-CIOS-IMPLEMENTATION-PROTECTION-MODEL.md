# CIOS-11 — CONTINUOUS IMPLEMENTATION OPERATING SYSTEM · IMPLEMENTATION PROTECTION MODEL

| Field | Value |
|---|---|
| MISSION | `IMR-003A` — CIOS Constitution & Architecture |
| ARTIFACT | `CIOS-11` — Implementation Protection Model (mission Output 11) |
| DELIVERED BY | `IMR-003A-R1` gap closure (Phase 4). **Additive**: no recovered artifact mutated. |
| DISCHARGES | `CIOS-L-03` (Non-Interruption) · `CIOS-L-18` (Completed Immutability — §2) · `CIOS-L-21` (Exclusive Override — §4) · `CIOS-INV-03`, `CIOS-INV-04` · closes `U-3` (the `CIOS-OR-*` set) |
| NUMERIC CONTRACT | **2 override authorities**, `CIOS-OR-01` and `CIOS-OR-02` — `CIOS-L-21` names exactly two; a third is void |
| BASIS | `CIOS-01` Art VII.3 row r7 — *"interruption classes, override authorities and the quiesce protocol are absent from the repository"* |
| AUTHORITY OF ITS OWN | **NONE.** Both override authorities are **located**; CIOS creates neither. |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. INTERRUPTION CLASSES

`CIOS-L-03` prohibits interruption of a dispatched implementation by *"admission, plan, enhancement, idea, discovery, optimization, governance improvement, repository evolution or architecture evolution"*. That list is a set of **sources**. Protection requires classifying by **effect**, because a source is harmless until it attempts something.

| ID | Class | Attempted effect on a dispatched item | Verdict | Engine |
|---|---|---|---|---|
| `CIOS-IC-01` | **Interrupt** | halt mid-execution | **REJECT** | `E-17` |
| `CIOS-IC-02` | **Suspend** | pause, awaiting a condition | **REJECT** | `E-17` |
| `CIOS-IC-03` | **Preempt** | displace in favour of higher-priority work | **REJECT** | `E-17` |
| `CIOS-IC-04` | **Mutate** | alter the item's specification, target or identity | **REJECT** | `E-17` |
| `CIOS-IC-05` | **Reorder** | change its position or dispatch sequence | **REJECT** | `E-17` |
| `CIOS-IC-06` | **Invalidate** | declare the in-flight work void | **REJECT** | `E-17` |
| `CIOS-IC-07` | **Rebind** | rebind it to a different plan epoch | **REJECT** | `E-17` (`CIOS-INV-04`) |
| `CIOS-IC-08` | **Resequence-sealed** | resequence, replan or reprioritize sealed work | **REJECT** | `E-17` (`CIOS-L-18`) |
| `CIOS-IC-09` | **Rewrite-sealed** | alter a sealed artifact | **REJECT** | `E-17` (`CIOS-INV-03`) |
| `CIOS-IC-10` | **Await** | require the item to wait on an assimilation-plane outcome | **REJECT** | `E-17` (`CIOS-L-02`) |

**All ten classes reject by default.** `E-17` is default-deny (`CIOS-04` §3): an attempt whose authority cannot be established is rejected, and `CIOS-L-03` admits no exception. The only lawful reach is `§4`.

### 1.1 What is *not* an interruption

Distinguished so that protection does not accidentally forbid lawful operation:

| Act | Interruption? | Why |
|---|---|---|
| Admitting new work into `CIOS-PT-03` | **NO** | `PL-A` write scope; cannot reach `CIOS-PT-02` (`WS-1`) |
| Composing `PLAN[n+1]` | **NO** | writes only the candidate; `PLAN[n]` has zero writers |
| Adopting `PLAN[n+1]` | **NO** | applies only to `CIOS-PT-03` (`CIOS-01` VI.2) |
| Realigning `CIOS-PT-03` | **NO** | writes only `CIOS-PT-03` (`CIOS-L-19`) |
| A located `IEC-001` `06` FAILED→READY retry | **NO** | located mechanism, bounded by `MAX_RETRY`; CIOS binds and does not redefine it (`CIOS-01` V.3) |
| Emitting a finding about an in-flight item | **NO** | `PL-D` writes nothing (`WS-6`); a finding is evidence, not an act |
| A located quality gate rejecting a transition | **NO** | `IEC-001` `08` Q1–Q8 is the located gate authority (`CIOS-01` I.6) |

The boundary is exactly the write-scope partition. **Anything that cannot write `CIOS-PT-02` or `CIOS-PT-01` cannot interrupt**, which is why `CIOS-02` §4 is the enforceable core of this model rather than this artifact's prose.

---

## 2. COMPLETED IMMUTABILITY — `CIOS-L-18`

| ID | Rule | Basis |
|---|---|---|
| `PM-1` | An item in `CIOS-PT-01` is SEALED: never resequenced, replanned, reprioritized or rewritten. | `CIOS-L-18` |
| `PM-2` | SEALED items are byte-identical across epochs. Any diff without a migration record is a `CIOS-INV-03` breach and is **inadmissible**, not degraded. | `CIOS-INV-03` |
| `PM-3` | Correction of sealed work proceeds by **successor only**, never by mutation. | `CIOS-L-13`; `AIF-L17`; `CEP-009` Art IV.3 / Art XI |
| `PM-4` | `CIOS-PT-01` is writable only by `CIOS-PL-C`, only by append, and only on a terminal-state event — or via `§4`. | `WS-8` |
| `PM-5` | The certified set is monotone non-decreasing across epochs. No admission may reduce it. | `CIOS-L-20`; `CIOS-INV-10`; `CEP-001` LAW-7 |

### 2.1 `CIOS-PT-01` is not a `CEP-007` freeze — mandatory disclosure

Repeated from `CIOS-04` §4 because misreading it would be a serious category error:

| | `CIOS-PT-01` SEALED | `CEP-007` FROZEN |
|---|---|---|
| Nature | a CIOS **mutability partition** | a constitutional **act** with statutory preconditions |
| Owner | CIOS (Art VII.3 r3) | `CEP-007` freeze authority |
| Scope | CIOS's own work-set model | corpus artifacts |
| Carries a freeze baseline? | **NO** | yes (`CEP-007` VIII) |
| Available at `b26c5bb`? | yes | **NO** — ineligible; three limbs of IV.1/V.1 fail (`GD-10`) |
| Attempted without eligibility | n/a | **VOID** (`CEP-007` IV.4, II.4) |

An item in `CIOS-PT-01` is immutable *within the CIOS model*. It is **not** a frozen artifact, and no CIOS artifact may present it as one (`GD-10-C1`, `GD-10-C5`).

---

## 3. THE QUIESCE PROTOCOL

`CIOS-02` §5 establishes that CIOS requires **no** lock, barrier or drain for routine operation. The quiesce protocol is therefore not a scheduling mechanism; it is the **precondition of a lawful override** and exists solely to serve `§4`.

| Property | Value |
|---|---|
| Purpose | bring the system to a state in which a located override authority may lawfully act |
| Invocable by | **only** `CIOS-OR-01` or `CIOS-OR-02` — never by an engine, a plane, a submitter, or a scheduling need |
| Invocable for routine assimilation, realignment or replanning | **NEVER** — those require no quiesce (`CIOS-02` §5) |
| Effect on `CIOS-PL-A` | **none.** Assimilation continues throughout. Quiescing assimilation would breach `CIOS-L-01`. |
| Effect on `CIOS-PL-D` | **none.** Observation continues. |
| Atomicity | the protocol either completes or leaves the system unchanged |

### 3.1 Protocol steps

| Step | Action | Failure verdict |
|---|---|---|
| `QP-1` | The invoking authority is authenticated as `CIOS-OR-01` or `CIOS-OR-02`. | **default-deny** — abort |
| `QP-2` | The declared, evidenced protocol record is presented and written **before** any effect. | abort; an unrecorded override is **void** (`CIOS-L-21`) |
| `QP-3` | No new dispatch occurs — `E-15` stops handing off. Items already in `CIOS-PT-02` are **not** halted. | abort |
| `QP-4` | In-flight items run to terminal state under their bound epoch (`CIOS-INV-04`). **They are never truncated.** | abort |
| `QP-5` | `CIOS-PT-02` reaches empty by natural completion. | abort on timeout — and abort means *resume normal operation*, never *force* |
| `QP-6` | The override authority acts within its declared scope (`§4`). | reject the act |
| `QP-7` | The act and its outcome are recorded immutably; `E-15` resumes handoff. | the act is void if unrecorded |

**`QP-4` is the constitutional core.** Quiesce **drains** rather than **interrupts**: it stops the *inflow* of dispatch and waits for in-flight work to finish. This is what allows a protocol that reaches protected work to coexist with `CIOS-L-03`, which forbids interrupting it. A protocol that truncated in-flight work would be a `CIOS-IC-01` interrupt performed under an official name.

---

## 4. THE TWO OVERRIDE AUTHORITIES — `CIOS-OR-01`, `CIOS-OR-02`

`CIOS-L-21` states that *only two* authorities may reach protected or sealed work, and that *"Both act by declared, evidenced, recorded protocol; never silently."* This section assigns them identifiers (closing `U-3`) and declares their scope. **Both are located. CIOS creates neither and may not.**

### `CIOS-OR-01` — Constitutional Migration Authority

| Field | Value |
|---|---|
| Located in | `CEP-009` — change / evolution / migration lifecycle (`CMG-DLG-09`) |
| Route | `CEP-009` Art III (change route); Art XX.2 |
| May reach | `CIOS-PT-02` IN-FLIGHT · `CIOS-PT-01` SEALED |
| Permitted acts | constitutional migration of a sealed or in-flight item; supersession by successor; lineage correction |
| **Prohibited acts** | mutation in place (`AIF-L17` forward-only); silent action; acting without an impact assessment (`CEP-009` III.1); self-conferral (`CEP-009` I.5) |
| Evidence required | `CEP-009` III.1 impact assessment · exactly one primary class (IV.6) · migration determination · immutable protocol record |
| Adjudicated by | `E-18` at `CIOS-P-35` |
| Relationship to `CIOS-G-01` | This is the same authority that owes the `GOV-001` Part 11 migration determination on which CIOS supremacy is deferred. It is **not** exercised by CIOS's existence. |

### `CIOS-OR-02` — Critical Repository Integrity Authority

| Field | Value |
|---|---|
| Located in | `CEP-010` (audit & compliance assurance) with `CEP-002` (governance escalation, `CMG-DLG-02`); the located Execution Authority (`CMG` T4) executes |
| Route | `CEP-002` escalation; `CEP-010` audit finding → remediation |
| May reach | `CIOS-PT-02` IN-FLIGHT · `CIOS-PT-01` SEALED |
| Permitted acts | remediation of a repository-integrity breach that makes continued operation unsafe — a detected cycle (`CIOS-INV-05`), a duplicate canonical home (`CIOS-INV-06`), a monotonicity regression (`CIOS-INV-10`), a write-scope breach (`CIOS-INV-02`) |
| **Prohibited acts** | acting on convenience, schedule pressure, priority or preference; acting without a recorded integrity finding; mutating a `CEP-007`-frozen artifact — **void, and places the Program in HALTED** (`CEP-007` IX.5; `GD-10-C2`) |
| Evidence required | a recorded integrity finding (typically from `CIOS-PL-D` via `CIOS-P-44`/`P-46`/`P-48`) · the breached invariant · remediation scope · immutable protocol record |
| Adjudicated by | `E-18` at `CIOS-P-35` |

### 4.1 Override rules

| ID | Rule | Basis |
|---|---|---|
| `OR-1` | **Exactly two** override authorities exist. A third is void, whatever its claimed basis. | `CIOS-L-21` |
| `OR-2` | Neither is created, conferred or hosted by CIOS. Both are located. | `CIOS-L-11`; `CIOS-01` I.7 |
| `OR-3` | Every override traverses `CIOS-P-35` and is adjudicated by `E-18`. There is no second entry point. | `CIOS-05` §2 |
| `OR-4` | `E-18` is **default-deny**: missing credential, missing evidence, or missing protocol record ⇒ rejection. | `CIOS-L-07` |
| `OR-5` | An **unrecorded** override is **void**, not merely irregular. | `CIOS-L-21` |
| `OR-6` | An override never authorizes mutation in place. Correction is forward-only, by successor. | `AIF-L17`; `CIOS-L-13` |
| `OR-7` | An override may not be used to interrupt in-flight work. It acts after quiesce drains (`QP-4`). | `CIOS-L-03` |
| `OR-8` | An override may not reduce the certified set. | `CIOS-L-20`; `CIOS-INV-10` |
| `OR-9` | Neither authority may exercise the other's scope. `CIOS-OR-01` migrates; `CIOS-OR-02` remediates. | `CEP-007` I.3 (single authority per artifact), by analogy |
| `OR-10` | No override reaches a `CEP-007`-frozen artifact. That surface is untouchable by CIOS and by both authorities acting through CIOS. | `CEP-007` IX.5; `GD-10-C2` |

### 4.2 Why exactly two, and why these two

The two correspond to the only two reasons protected work may legitimately need reaching: **the law changed** (`CIOS-OR-01`) or **the repository is broken** (`CIOS-OR-02`). Every other motive — priority, schedule, preference, optimization, a better idea — is precisely what `CIOS-L-03` exists to refuse, and each is already served by the lawful path of admitting new work into `CIOS-PT-03`, which needs no override at all.

---

## 5. PROTECTION PROPERTIES

| Property | Value | Basis |
|---|---|---|
| Interruption classes | **10** (`CIOS-IC-01 … IC-10`) | §1 |
| Classes admitted by default | **0** | `E-17` default-deny |
| Override authorities | **2** | `CIOS-L-21` |
| Override entry points | **1** (`CIOS-P-35`) | `OR-3` |
| Overrides admissible without a recorded protocol | **0** | `OR-5` |
| Overrides that may interrupt in-flight work | **0** | `OR-7`, `QP-4` |
| Overrides that may reduce the certified set | **0** | `OR-8` |
| Overrides that may reach a `CEP-007`-frozen artifact | **0** | `OR-10` |
| Quiesce invocations available to engines/planes/submitters | **0** | §3 |
| Quiesce effect on assimilation | **none** | §3 |
| Planes able to write `CIOS-PT-02` | **1** (`PL-B`) | `CIOS-02` §4.3 |
| Planes able to write `CIOS-PT-01` | **1** (`PL-C`, append) | `WS-8` |

---

## AUTHORITY BOUNDARY (MANDATORY)

This artifact declares interruption classes, a quiesce protocol and the identifiers of two **located** override authorities. It creates no authority, owns no mechanism, no registry, no gate, no identifier space and no concern. `CIOS-PT-01` is a CIOS mutability partition and is **not** a `CEP-007` freeze state; nothing here declares, implies or records a freeze, a freeze baseline or a freeze authorization. Where this artifact and a located canonical instrument disagree, **the located instrument governs and this artifact SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `CIOS-11` · PROVISIONAL · ADDITIVE · COMPOSITION-ONLY · AUTHORITY-NEUTRAL**
