# CIOS-01 — CONTINUOUS IMPLEMENTATION OPERATING SYSTEM · CONSTITUTION

| Field | Value |
|---|---|
| MISSION | `IMR-003A` — Continuous Implementation Operating System · Constitution & Architecture |
| ARTIFACT | `CIOS-01` — Constitution (mission Output 1) |
| ARTIFACT KIND | Constitution (`CMG-K-03`) — **composition instrument**, substantive only over continuity, partitioning, protection and realignment |
| CLASSIFICATION | GOVERNANCE · additive-only · programme-owned under `00-MASTER/IMR-003A/` |
| DERIVES AUTHORITY FROM | `CEP-001` (supreme operational) · `CEP-009` (admission route) · `CMG-000001` (meta-governance) · `GOV-INT-001` §2.15 / §7.2 / SECTION 8 (located execution architecture) |
| AUTHORITY OF ITS OWN | **Composition only.** CIOS legislates the *continuity* of implementation. It legislates **no mechanism**. Every mechanism is a pointer to a located owner. |
| SCOPE OF GOVERNANCE | The perpetual operation of implementation: submission admission, plan partitioning, execution protection, and future-only realignment |
| CONFLICT RULE | Where CIOS and a located canonical instrument conflict, **the located instrument governs** and CIOS SHALL be corrected (`CEP-001` LAW-1, LAW-4) |
| BASELINE | `b26c5bb` · branch `programme/evo-usis-005` |
| STANDING | PROVISIONAL (`CMG-L-12`); Tier T1 **VACANT** (`VAC-01`); **supremacy deferred** behind `CIOS-G-01` |
| MODE | CONSTITUTION & ARCHITECTURE ONLY. No functional implementation. |

---

## PREAMBLE

**P.1** Implementation in this repository has until now been constituted as a **finite project**: a fixed backlog of 77 executable objects, a fixed order, five waves, and a terminal state after Wave-05. The located instruments that express this — `IMG-001` and `IEC-001` — are correct, certified-provisional, and remain canonical. They are also, by construction, **closed at the top**: they describe how to finish a known set of work.

**P.2** A repository that continuously discovers knowledge cannot be governed by an instrument that assumes the work is known. New knowledge arrives after the plan is fixed. If admission of new knowledge requires the plan to stop, then implementation halts every time the repository learns something — and the repository learns continuously.

**P.3** CIOS therefore constitutes implementation as a **perpetual operating system** rather than a project. It does this by adding exactly one thing the repository does not have: a **law of continuity** — a formal separation between the plane on which future work is prepared and the plane on which present work executes, such that neither can block the other.

**P.4** CIOS adds nothing else. It does not re-author the state machine, the queues, the waves, the dependency graph, the gates, the identity allocator, the evolution model, the validation authority, the certification authority, or the traceability model. All of these are **located and canonical**, and Knowledge Once forbids their restatement. CIOS **binds** them and governs only their *continuous composition*.

**P.5** CIOS claims no supremacy by self-declaration. `CEP-009` I.5 forbids self-conferred authority; `GOV-001` Part 10 forbids a parallel identifier system; `GOV-001` Part 11 requires a migration determination before any instrument replaces the located implementation authority. CIOS is therefore established as an **additive composition layer**, and its governing supremacy over every future implementation mission is **deferred** behind `CIOS-G-01`.

**P.6** Every determination in this constitution is **PROVISIONAL**. Tier T1 (Constitutional Authority) is VACANT (`VAC-01`, `CMG-OQ-02`, `UCCEP-F-004`); no located authority is competent to ratify. Nothing in CIOS is ratified, final, or frozen.

---

## ARTICLE I — NATURE AND STANDING

**I.1** CIOS is a **composition instrument**. Its substantive content is confined to four subjects: *plane separation*, *work-set partitioning*, *implementation protection*, and *future-only realignment*.

**I.2** CIOS is **additive** over `IEC-001`, `IMG-001`, `UAKOS`, `UCDA`, `UCCEP`, `AIF`/`REG-AUTO-001`, `CEP-001…010`, `CMG-000001`, `UCI-001`, `RIE` and every other located owner named in `cios-bindings.json`.

**I.3** CIOS **subordinates nothing**. It does not deprecate, supersede, amend, reinterpret or narrow any located instrument.

**I.4** CIOS holds **no execution authority**. Dispatch authority remains with the located Execution Authority (`CMG` tier T4) exercised through the located controller (`IEC-001` C7) in the EC-3 lane.

**I.5** CIOS holds **no identity authority**. Minting remains with the located identity authority (`AIF` + `REG-AUTO-001` + `00-BOOK/tools/`).

**I.6** CIOS holds **no gate authority**. Every gate is located; CIOS declares only which located gates bind which lifecycle stage.

**I.7** CIOS's supremacy as *the* constitutional authority governing every future implementation mission is **NOT CONFERRED** by this constitution. It is contingent on `CIOS-G-01` (a `GOV-001` Part 11 migration determination) and on `CIOS-G-02` (admission of the CIOS concern to `CMG-REGISTRY.json`). Until both are discharged by their located owners, CIOS governs **by composition and reference**, not by supremacy.

---

## ARTICLE II — CONSTITUTIONAL LAWS

Twenty-four laws. Each law is atomic (`CMG-K-04`), enforced by a located owner, and bound to enforcement in `cios-bindings.json`. A law that names no located enforcer is itself a finding.

### Continuity laws

| ID | Law | Statement | Located enforcer |
|---|---|---|---|
| **CIOS-L-01** | **Perpetual Operation** | Implementation has no terminal state. There is no condition under which the implementation service is *complete*; there are only work sets that are momentarily empty. An empty Ready Queue is an idle service, never a finished one. | `CEP-009` Art XXIII.10 (Unlimited Evolution); `IEC-001` §4 tick loop |
| **CIOS-L-02** | **Plane Separation** | Preparation of future work and execution of present work occur on **separate planes** with disjoint write scopes. No plane may block, pause, preempt or await another. | this constitution; `CIOS-02` §2 |
| **CIOS-L-03** | **Non-Interruption** | No admission, plan, enhancement, idea, discovery, optimization, governance improvement, repository evolution or architecture evolution may interrupt, suspend, mutate, reorder, or invalidate an implementation already dispatched. | `CIOS-11`; `IEC-001` C11 gate composition |
| **CIOS-L-04** | **Independent Clocks** | The assimilation plane and the execution plane advance on independent clocks. Neither clock's rate, backlog, or failure is an input to the other's ability to advance. | `CIOS-10` §5 |
| **CIOS-L-05** | **Bounded Assimilation** | Assimilation is unbounded in *volume* and bounded in *effect*: it may write only the OPEN partition and its own operational memory. Assimilation failure degrades future planning, never present execution. | `CIOS-02` §4 write scopes |

### Admission laws

| ID | Law | Statement | Located enforcer |
|---|---|---|---|
| **CIOS-L-06** | **Stage Completeness** | Every submission traverses every lifecycle stage `CIOS-S-01 … CIOS-S-24` in order. No stage may be skipped, merged, reordered, or waived. A stage without a resolved verdict is a non-admission. | `CIOS-07`; `CEP-001` LAW-5 (Non-Bypass) |
| **CIOS-L-07** | **Fail-Closed Admission** | Missing, ambiguous, unresolvable or degraded evidence is a **failure**, never a pass. Admission defaults to non-admission. | `CEP-001` LAW-2 (Evidence); `IEC-001` `08` §fail-closed |
| **CIOS-L-08** | **Knowledge Once** | No admitted item may introduce knowledge that already exists in the repository. Recurrence resolves to the located canonical owner as EXTEND, never as CREATE. | `UAKOS-CLOSURE-002` charter; `CK-CLOSURE-P1`, `CK-CLOSURE-P2` |
| **CIOS-L-09** | **Zero Duplication** | No admitted item may create a second canonical home, a second owner, a second identifier, a second plan, a second queue, a second gate, or a second authority for anything that already has one. | `CEP-001` LAW-4 (Single Canonicity); `06-DUPLICATION-AND-OVERLAP-VERIFICATION.md`; `GOV-001` Part 10 |
| **CIOS-L-10** | **Overlap Prohibition** | Where two admitted items overlap in scope, the overlap SHALL be resolved to a single owner before admission. Unresolved overlap is a non-admission, not a scheduling problem. | `CIOS-04` `CIOS-E-05`; `IAC-001D` §05 Reuse Gate |
| **CIOS-L-11** | **Located Authority** | No CIOS engine may confer authority on itself. Every engine's authority is located in an instrument that exists independently of CIOS. | `CEP-009` I.5 |

### Identity laws

| ID | Law | Statement | Located enforcer |
|---|---|---|---|
| **CIOS-L-12** | **Automatic Identity** | Identity is minted by the system at admission. Manual assignment of any identifier is prohibited and is a hard rejection. | `AIF`; `REG-AUTO-001` §"Artifact Creation = Artifact Registration" |
| **CIOS-L-13** | **Immutable Identity** | Once minted, no identity field may be altered. Correction proceeds only by successor, never by mutation. | `CEP-009` Art IV.3 / Art XI; `AIF-L07` |
| **CIOS-L-14** | **Single Identity Authority** | CIOS mints nothing. It composes an identity record from fields produced by located authorities. No parallel identifier system exists. | `GOV-001` Part 10; `REG-AUTO-001` |
| **CIOS-L-15** | **Ordinal Ordering** | Ordering authority is the **witnessed admission ordinal**, never a timestamp. Timestamps are evidence; ordinals are order. | `AIF-L04` |

### Execution laws

| ID | Law | Statement | Located enforcer |
|---|---|---|---|
| **CIOS-L-16** | **Derived Selection** | Work is never manually selected. Selection is a pure function of Repository Truth and declared rules. | `IEC-001` §2 prime directive, §5 |
| **CIOS-L-17** | **Determinism** | Identical Repository Truth and identical declared data yield identical admission verdicts, identity derivation, plan epoch, priority order and schedule. | `CEP-001` LAW-8; `CK-RIE-DETERMINISM`, `CK-DETERMINISM-BUILD` |
| **CIOS-L-18** | **Completed Immutability** | Completed and certified implementation is SEALED. It is never resequenced, replanned, reprioritized, or rewritten. | `CEP-007`; `CIOS-11` §2 |
| **CIOS-L-19** | **Future-Only Realignment** | Realignment may alter only the OPEN partition. In-flight work retains its bound plan epoch; sealed work is untouched. | `CIOS-12` §3 |
| **CIOS-L-20** | **Monotone Progress** | The certified set is monotone non-decreasing across epochs. No admission may reduce it. No repository regression is admissible. | `CEP-001` LAW-7 (Preservation); `CK-HEALTH` |
| **CIOS-L-21** | **Exclusive Override** | Only two authorities may reach protected or sealed work: the **Constitutional Migration Authority** (`CEP-009` change/migration route) and the **Critical Repository Integrity Authority**. Both act by declared, evidenced, recorded protocol; never silently. | `CIOS-11` §4; `CEP-009` Art III / Art XX.2 |

### Extensibility laws

| ID | Law | Statement | Located enforcer |
|---|---|---|---|
| **CIOS-L-22** | **Zero Enumeration** | CIOS enumerates no domain, industry, science, technology, vendor, cloud, platform, language, protocol, serialization format, database or infrastructure. Any such enumeration in CIOS is a violation of CIOS. | `PR-07`, `PR-19`; `04-HIDDEN-FINITE-ASSUMPTION-CERTIFICATION.md`; `CK-SELF-NO-ENUMERATION` pattern |
| **CIOS-L-23** | **No Hard Coding** | Every engine, stage, port, queue, partition, rank, weight, threshold and ordering key is a **declared data entry**. Adding one is a data change; it requires no amendment of CIOS law and no change to any engine. | `cios-bindings.json`; `UCCEP-000000` Infinite Extensibility precedent |
| **CIOS-L-24** | **Unbounded Capacity** | No CIOS model may assume a finite number of submissions, items, dependencies, waves, epochs, queues, or planning cycles. Every sequence is defined by a successor function, never by an enumerated set. | `03-CONSTITUTIONAL-UNBOUNDEDNESS-CERTIFICATION.md`; `CIOS-10` §3 |

---

## ARTICLE III — CONSTITUTIONAL INVARIANTS

Invariants are **absolute** (`CMG-K-06`): a state violating an invariant is not a degraded state, it is an inadmissible one.

| ID | Invariant | Violation condition |
|---|---|---|
| **CIOS-INV-01** | Partitions are pairwise disjoint and jointly exhaustive over the work set | an item in two partitions, or in none |
| **CIOS-INV-02** | No write crosses a plane's declared write scope | any plane writing outside its scope |
| **CIOS-INV-03** | SEALED items are byte-identical across epochs | any diff to a sealed item without a migration record |
| **CIOS-INV-04** | IN-FLIGHT items retain their bound plan epoch until terminal state | plan rebinding of an in-flight item |
| **CIOS-INV-05** | The engine dependency graph is acyclic | any cycle (`CEP-009` Art XV.2 prohibits; Art XX.2 ⇒ HALTED) |
| **CIOS-INV-06** | Every admitted item has exactly one canonical home and exactly one owner | `duplicate_canonical_homes > 0` or multiple owners |
| **CIOS-INV-07** | Every admitted item carries a complete identity record (all 22 fields resolved) | any unresolved identity field |
| **CIOS-INV-08** | Every lifecycle stage transition is gated and recorded | an ungated or unlogged transition |
| **CIOS-INV-09** | The priority order is a **total** order | any tie unresolved after the full key vector |
| **CIOS-INV-10** | The certified set never shrinks | monotonicity breach |
| **CIOS-INV-11** | Every CIOS reference resolves at the stated baseline | a dangling pointer |
| **CIOS-INV-12** | CIOS holds no concern, no gate, no registry and no identifier space of its own | any self-conferred authority |

---

## ARTICLE IV — THE FOUR PLANES

**IV.1** The implementation operating system is constituted as four planes with disjoint write scopes. Detailed in `CIOS-02`.

| ID | Plane | Function | Write scope | May block execution? |
|---|---|---|---|---|
| **CIOS-PL-A** | Assimilation | prepare future work | OPEN partition + own operational memory | **No** |
| **CIOS-PL-B** | Execution | realize present work | IN-FLIGHT state; Truth only via `CIOS-PL-C` | — |
| **CIOS-PL-C** | Truth | record what became true | append-only to Repository Truth | **No** |
| **CIOS-PL-D** | Observation | measure and report | nothing; emits findings only | **No** |

**IV.2** Plane separation is the sole mechanism by which `CIOS-L-01` (Perpetual Operation) and `CIOS-L-03` (Non-Interruption) are simultaneously satisfiable. It is therefore constitutional, not architectural convenience.

---

## ARTICLE V — THE THREE-PLUS-ONE PARTITIONS

**V.1** The work set is partitioned. Partition membership, not process state, determines what may be written.

| ID | Partition | Membership | Mutability |
|---|---|---|---|
| **CIOS-PT-00** | INTAKE | submitted, not admitted | freely discarded; outside every plan |
| **CIOS-PT-03** | OPEN | admitted, not dispatched | freely resequenceable by realignment |
| **CIOS-PT-02** | IN-FLIGHT | dispatched, not terminal | frozen for the dispatch window |
| **CIOS-PT-01** | SEALED | certified or terminally archived | immutable; successor-only |

**V.2** Realignment writes **only** `CIOS-PT-03`. This single restriction is what makes continuous replanning safe (`CIOS-L-19`).

**V.3** Partition transitions are one-way: `INTAKE → OPEN → IN-FLIGHT → SEALED`. The sole exception is a failed in-flight item returning to OPEN under the located retry rule (`IEC-001` `06` FAILED→READY, bounded by MAX_RETRY), which is a located mechanism CIOS binds and does not redefine.

---

## ARTICLE VI — THE EPOCH MODEL

**VI.1** Planning is **versioned by epoch**, not mutated in place. `PLAN[n]` is the active epoch; assimilation composes `PLAN[n+1]` as a staged candidate.

**VI.2** Adoption of `PLAN[n+1]` occurs only at a **Quiescent Adoption Point** — the batch-cut boundary of the located scheduler. Adoption is atomic and applies only to `CIOS-PT-03`.

**VI.3** An item dispatched under `PLAN[n]` remains bound to `PLAN[n]` until terminal state (`CIOS-INV-04`). Consequently no lock is ever taken on execution, and assimilation never waits for execution.

**VI.4** Epochs are unbounded: `n ∈ ℕ`, defined by a successor function (`CIOS-L-24`).

---

## ARTICLE VII — RELATIONSHIP TO THE LOCATED IMPLEMENTATION AUTHORITY

**VII.1** `IEC-001` remains the sole authority on: the controller, the lifecycle trigger taxonomy, the seven READY predicates, the execution/ready/blocked/excluded queues, the ten-state machine, the eight quality gates, batch formation, and execution governance.

**VII.2** `IMG-001` remains the sole authority on: the backlog, the dependency graph, the wave partition, the topological order, the critical path, and the readiness matrix.

**VII.3** CIOS contributes, and may only contribute, the following to that stack:

| CIOS contribution | Why it is not a duplication |
|---|---|
| The pre-Execution-Queue queue family (`CIOS-Q-01 … CIOS-Q-04`) | `IEC-001` `04` begins at the Execution Queue; the queues upstream of it are undefined in the repository |
| Plane separation and write-scope confinement | no located instrument partitions write authority by plane |
| Work-set partitioning (SEALED / IN-FLIGHT / OPEN / INTAKE) | `IEC-001` `06` defines *item states*; no instrument defines *mutability partitions* |
| Epoch / copy-on-write plan adoption | no located instrument versions the plan or defines an adoption boundary |
| The unbounded wave successor function | `IMG-001` `04` enumerates W1–W5 as a finite set; the successor function generalizes it without altering W1–W5 |
| The declared priority key vector | `IEC-001` `04` fixes order as `wave, family, id`; priority as a declared, extensible key vector is absent |
| The implementation protection model | interruption classes, override authorities and the quiesce protocol are absent from the repository |
| The future-only realignment function | absent from the repository |
| The 24-stage admission lifecycle binding | `IEC-001` `02` covers execution lifecycle; the pre-admission stages are distributed across UAKOS/UCDA/UCCEP with no single binding |

**VII.4** Where CIOS's contribution and a located model appear to overlap, `CIOS-19` (Gap Analysis) records the located owner and CIOS defers. Overlap that cannot be resolved by deferral is a defect in CIOS.

---

## ARTICLE VIII — AMENDMENT AND EVOLUTION

**VIII.1** CIOS owns no evolution model. `CEP-009` (Art VI, XVI, XXIV) is the sole owner of the constitutional evolution model, the evolution registry, versioning and lineage. CIOS evolves through that route only.

**VIII.2** Adding an engine, stage, port, queue, partition, key element, override authority or identity field is a **data change** to `cios-bindings.json` (`CIOS-L-23`). It amends no law and requires no successor constitution.

**VIII.3** Altering a law, invariant, plane or partition requires a `CEP-009` III.1 change with an impact assessment, and — because these are the only substantive content CIOS holds — a successor instrument rather than an in-place edit where the located instrument is frozen (`CEP-009` Art IV.3).

**VIII.4** CIOS may never be amended to acquire mechanism ownership. An amendment that moves a located mechanism into CIOS violates `CIOS-L-09` and `CEP-001` LAW-4 and is void.

---

## ARTICLE IX — DISCLOSURE AND STANDING LIMITS

**IX.1** Tier T1 (Constitutional Authority) is **VACANT** (`VAC-01`, `CMG-OQ-02`, `UCCEP-F-004`). No located authority is competent to ratify. Every CIOS determination is capped at **PROVISIONAL** (`CMG-L-12`).

**IX.2** Freeze is **unavailable** (`GD-10` / `CEP-007`). CIOS claims no seal.

**IX.3** CIOS inherits the following located findings as **bounds on its claims**, not as its own defects. Each is owned and discharged elsewhere.

| Finding | Bound it places on CIOS |
|---|---|
| `UCCEP-F-001` | the located planning-closure gate has no reachable PASS state; CIOS may not claim a measured planning verdict through it |
| `UCCEP-F-002` | traceability is incomplete for all 1198 registered artifacts; CIOS may not claim traceability closure (`CIOS-17` §5) |
| `UCCEP-F-003` | the located graph validator fails open on a reported cycle; `CIOS-INV-05` cannot be considered machine-enforced until discharged |
| `UCCEP-F-004` | T1 vacancy caps every verdict at PROVISIONAL |
| `UCCEP-F-005` | historical gate bypassability; CIOS relies on gates now bound in CI |
| `UCCEP-F-006` | schema validation degrades silently; identity-record validation inherits that degradation |
| `UCCEP-F-007` | working-tree registration drift exists at establishment; CIOS adds none but does not clear it |
| `UCCEP-F-008` | decision disposition obligation is newly gated; CIOS binds `CK-DECISION-EVIDENCE` rather than restating it |

**IX.4** CIOS asserts no discharge of any inherited finding, and no discharge of `GG-3`, `GG-4`, `GG-6`, or `IAC-001` B+C.

---

## ARTICLE X — CONSTITUTIONAL CLOSURE OF THIS INSTRUMENT

**X.1** CIOS is complete with respect to its own scope when, and only when, all of the following hold: the four planes are declared; the partitions are declared and disjoint; twenty-four laws each name a located enforcer; twelve invariants are stated; twenty-four engines are bound to located owners or recorded as absent; twenty-four stages are bound to gates and states; twenty-two identity fields are bound to minting authorities; and every gap is recorded with a named owner. `CIOS-20` verifies each.

**X.2** CIOS is **not** complete as a governing authority, and does not claim to be, until `CIOS-G-01` and `CIOS-G-02` are discharged.

---

## AUTHORITY BOUNDARY (MANDATORY)

This constitution governs **continuity, partitioning, protection and realignment** and nothing else. It owns no mechanism, no registry, no gate, no identifier space and no concern. Every authority it names is located in an instrument that exists independently at `b26c5bb`. Where this instrument and a located canonical instrument disagree, **the located instrument governs and this instrument SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `CIOS-01` · PROVISIONAL · ADDITIVE · COMPOSITION-ONLY · AUTHORITY-NEUTRAL**
