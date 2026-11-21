# UCOS Ω∞ — CONSTITUTIONAL EXECUTION CONSTITUTION

| Field | Value |
|-------|-------|
| ARTIFACT ID | CEP-003 |
| ARTIFACT | UCOS Ω∞ Constitutional Execution Constitution |
| CLASSIFICATION | Constitutional Engineering Program (CEP) — Execution Constitution |
| STATUS | RATIFIED (program-governance level) · NORMATIVE · LIVING-UNTIL-FROZEN |
| STAGE | Stage 01 · Prompt 05 |
| VERSION | 1.0 |
| DERIVES AUTHORITY FROM | CEP-000 (Charter), CEP-001 (Constitution), CEP-002 (Governance Constitution) |
| AUTHORITY | Supreme over all execution operation of the Program; subordinate to CEP-000, CEP-001, and CEP-002 |
| SCOPE OF GOVERNANCE | HOW constitutional engineering executes — execution only |
| CANONICAL FORM | This Markdown file |
| CONFLICT RULE | This instrument governs all execution operation. Where it conflicts with CEP-002, CEP-001, or CEP-000, the higher instrument governs in that order. |

> This document is normative constitutional law legislating execution only. It inherits and references CEP-000, CEP-001, and CEP-002 and SHALL NOT rewrite, duplicate, or restate them. It SHALL NOT legislate governance, validation, certification, evidence, or repository content; those are reserved to their respective constitutions.

---

## PREAMBLE

P.1 This instrument IS the permanent constitutional execution instrument of the UCOS Ω∞ Constitutional Engineering Program.

P.2 This instrument SHALL legislate how the Program executes, and SHALL NOT legislate governance (reserved to CEP-002), validation, certification, or evidence (reserved to CEP-001 and later constitutions).

P.3 This instrument refines the general Execution Model of CEP-001 Article IX and the State Model of CEP-001 Article VIII at the level of the individual execution unit, and SHALL remain consistent with both.

P.4 This instrument SHALL bind every execution act of the Program until amended or frozen under its own rules.

---

## ARTICLE I — EXECUTION AUTHORITY

I.1 Execution Authority SHALL vest as defined by CEP-000 §5.5 (Tier 3) and SHALL act only within a stage that is in the EXECUTING condition.

I.2 Execution Authority SHALL perform exactly the single next authorized action and SHALL write only to the declared write area of the active stage.

I.3 Execution Authority SHALL NOT govern, ratify, decide constitutional content, or exercise a power reserved to a higher tier.

I.4 Execution Authority SHALL NEVER self-authorize an action, and SHALL act only upon an authorization granted under Article VIII.

---

## ARTICLE II — EXECUTION SCOPE

II.1 This instrument SHALL legislate the execution lifecycle, states, transitions, sequencing, dependencies, authorization, permissions, coordination, orchestration, checkpointing, suspension, resumption, restart, failure handling, recovery entry, isolation, concurrency, serialization, determinism, completion, and handoff.

II.2 This instrument SHALL NOT legislate governance, validation criteria, certification method, evidence content, or repository content.

II.3 Every execution act SHALL be attributable to exactly one execution unit, one stage, and one write area.

II.4 An act outside a stage in the EXECUTING condition IS PROHIBITED and SHALL be void.

---

## ARTICLE III — EXECUTION LIFECYCLE

III.1 The execution unit SHALL be the atomic granted work of execution: the single next authorized action of the active stage.

III.2 The execution lifecycle SHALL be uniform for every execution unit: authorize, dispatch, run within isolation, then either complete-and-hand-off or fail-and-recover, with suspension and resumption permitted during running.

III.3 No second execution unit SHALL enter RUNNING before the current unit reaches a terminal state.

III.4 Every execution unit SHALL conclude at exactly one terminal state and SHALL emit exactly one next authorized action or a halt.

---

## ARTICLE IV — EXECUTION STATE MACHINE

IV.1 The execution-unit states SHALL be: AUTHORIZED, DISPATCHED, RUNNING, SUSPENDED, COMPLETED, FAILED, RECOVERING, HANDED_OFF, TERMINATED.

IV.2 The initial state of every execution unit SHALL be AUTHORIZED.

IV.3 The terminal states SHALL be HANDED_OFF and TERMINATED. No transition SHALL depart a terminal state.

IV.4 Every non-terminal state SHALL have at least one defined outgoing transition, and every state SHALL be reachable from AUTHORIZED.

IV.5 Execution-unit states SHALL correspond to CEP-001 stage states as follows: RUNNING corresponds to the stage condition EXECUTING; COMPLETED and HANDED_OFF correspond to the stage progression CHECKPOINTED to EXITED. This instrument SHALL NOT redefine the stage or program states of CEP-001 Article VIII.

---

## ARTICLE V — EXECUTION TRANSITION RULES

V.1 The legal execution-unit transitions SHALL be exactly:
- AUTHORIZED → DISPATCHED.
- DISPATCHED → RUNNING.
- RUNNING → SUSPENDED.
- RUNNING → COMPLETED.
- RUNNING → FAILED.
- SUSPENDED → RUNNING.
- SUSPENDED → TERMINATED.
- COMPLETED → HANDED_OFF.
- FAILED → RECOVERING.
- RECOVERING → DISPATCHED.
- RECOVERING → TERMINATED.

V.2 Any transition not enumerated in V.1 IS PROHIBITED and SHALL be treated as an illegal transition.

V.3 An attempted illegal transition SHALL place the Program in HALTED and SHALL emit a finding.

V.4 Every transition SHALL be recorded with its origin state, destination state, and trigger, such that it is auditable and reproducible.

V.5 A transition SHALL be atomic; a partially applied transition SHALL be resolved by the Recovery Model (CEP-001 Article XXI) and SHALL NEVER be recorded as complete.

---

## ARTICLE VI — EXECUTION SEQUENCING

VI.1 Execution SHALL proceed along the governed forward stage graph of CEP-001 §7.1 in topological order.

VI.2 Within a stage, execution units SHALL be sequenced deterministically; where two units are independent, they SHALL be ordered by a canonical, reproducible ordering.

VI.3 Sequencing SHALL NEVER skip a gate and SHALL NEVER reorder a unit ahead of a unit it depends upon.

VI.4 Backward sequencing SHALL occur only through the Amendment Model of CEP-001 Article XV and only upon a logged finding.

---

## ARTICLE VII — EXECUTION DEPENDENCY MODEL

VII.1 Every execution dependency SHALL be declared; an undeclared dependency IS PROHIBITED.

VII.2 The execution dependency graph SHALL be acyclic; a dependency that would form a cycle IS PROHIBITED.

VII.3 An execution unit SHALL NOT enter DISPATCHED until every unit it depends upon has reached HANDED_OFF.

VII.4 A dependency SHALL be satisfied by reference to a completed unit's output and SHALL NEVER be satisfied by mutating that output.

VII.5 A discovered circular execution dependency SHALL place the Program in HALTED until eliminated.

---

## ARTICLE VIII — EXECUTION AUTHORIZATION

VIII.1 An execution unit SHALL enter AUTHORIZED only upon an authorization derived from program state, never from conversational instruction (per CEP-000 §19).

VIII.2 Authorization SHALL grant exactly one next authorized action and SHALL bind it to one stage and one write area.

VIII.3 Authorization SHALL be denied when the active stage's entry criteria do not hold; a denied authorization SHALL place the Program in HALTED.

VIII.4 Authorization SHALL NEVER be self-conferred by Execution Authority and SHALL NEVER bypass a gate, a governance control, or a preservation rule.

---

## ARTICLE IX — EXECUTION PERMISSIONS

IX.1 An authorized execution unit SHALL be permitted to read referenced frozen and referenceable inputs and to write only to its declared write area.

IX.2 Permission SHALL NOT extend to any area outside the declared write area; a cross-area write IS PROHIBITED and SHALL be void.

IX.3 Permission SHALL NOT extend to mutating frozen work; frozen work SHALL be changed only by supersession under CEP-001 Article XV.

IX.4 Permission SHALL be scoped to the lifetime of the execution unit and SHALL lapse upon reaching a terminal state.

---

## ARTICLE X — EXECUTION COORDINATION

X.1 Coordination between execution units SHALL occur only through completed outputs consumed by reference and through the checkpoint and handoff mechanisms.

X.2 Coordination SHALL NEVER occur through shared mutable state.

X.3 Handoff of control SHALL pass from a unit in HANDED_OFF to the next authorized unit through a checkpoint that emits exactly one next authorized action.

X.4 A coordination act that cannot be recorded and reproduced SHALL be treated as if it did not lawfully occur.

---

## ARTICLE XI — EXECUTION ORCHESTRATION

XI.1 Orchestration SHALL arrange execution units in accordance with the sequencing rules (Article VI) and the dependency model (Article VII).

XI.2 Orchestration SHALL produce a single, deterministic, reproducible execution order for any given program state.

XI.3 Orchestration SHALL NEVER introduce a hidden execution path, a non-deterministic ordering, or an implicit dependency.

XI.4 Orchestration SHALL halt and report rather than proceed when a deterministic order cannot be derived.

---

## ARTICLE XII — EXECUTION CHECKPOINT MODEL

XII.1 A checkpoint SHALL be written at every execution-unit terminal transition and at every stage gate transition, consistent with CEP-001 and CEP-000 §19.3.

XII.2 A checkpoint SHALL record the current stage, the execution-unit state, the last completed action, the next authorized action, the program-state hash, and the repository anchor.

XII.3 A checkpoint SHALL be append-only and content-addressed and SHALL assert nothing authoritative; it SHALL be reconciled against repository truth at boot.

XII.4 A checkpoint SHALL emit exactly one next authorized action.

---

## ARTICLE XIII — EXECUTION SUSPENSION

XIII.1 A RUNNING execution unit MAY transition to SUSPENDED, preserving its execution state such that it is resumable without loss.

XIII.2 Suspension SHALL be recorded and SHALL preserve all referenced inputs and partial outputs in a recoverable form; a partial output SHALL NEVER be recorded as complete.

XIII.3 A SUSPENDED unit SHALL NOT perform any act until it resumes or terminates.

XIII.4 Suspension SHALL NOT release the unit's write area to any other unit.

---

## ARTICLE XIV — EXECUTION RESUME MODEL

XIV.1 A SUSPENDED execution unit SHALL resume by transitioning to RUNNING from the preserved execution state.

XIV.2 Resumption SHALL be preceded by boot reconciliation (CEP-001 Article XXI) and SHALL correct program state against repository truth before any act.

XIV.3 Resumption SHALL be idempotent and SHALL NEVER alter a result already recorded as complete.

XIV.4 A unit that cannot be resumed deterministically SHALL transition to FAILED and enter the Failure Model.

---

## ARTICLE XV — EXECUTION RESTART MODEL

XV.1 Restart SHALL occur only from RECOVERING and SHALL transition to DISPATCHED.

XV.2 Restart SHALL discard any partial, non-terminal output of the failed attempt and SHALL NEVER carry partial state forward as truth.

XV.3 A restarted execution unit SHALL reproduce byte-identical output for identical inputs (per CEP-001 Article XX).

XV.4 Restart SHALL NEVER re-run a unit already in HANDED_OFF and SHALL NEVER mutate a completed output.

---

## ARTICLE XVI — EXECUTION FAILURE MODEL

XVI.1 A RUNNING execution unit SHALL transition to FAILED upon any failed criterion, illegal transition, non-determinism, or discovered contradiction.

XVI.2 A FAILED unit SHALL place the Program in HALTED and SHALL emit a finding.

XVI.3 A FAILED unit SHALL transition only to RECOVERING; it SHALL NOT transition directly to COMPLETED or HANDED_OFF.

XVI.4 A failure SHALL never be silently absorbed; it SHALL be recorded, routed, and remediated or terminated.

---

## ARTICLE XVII — EXECUTION RECOVERY ENTRY

XVII.1 Recovery SHALL be entered only from FAILED, by transition to RECOVERING.

XVII.2 Recovery entry SHALL invoke the Recovery Model of CEP-001 Article XXI and SHALL reconcile program state against repository truth.

XVII.3 From RECOVERING, the unit SHALL transition to DISPATCHED (restart) when deterministic reproduction is possible, or to TERMINATED when it is not.

XVII.4 Recovery SHALL be non-destructive and SHALL NEVER roll back ratified or frozen work; such work SHALL be changed only by supersession.

---

## ARTICLE XVIII — EXECUTION ISOLATION

XVIII.1 Every execution unit SHALL execute in isolation, confined to its declared write area.

XVIII.2 One execution unit SHALL NOT read the uncommitted, non-terminal output of another.

XVIII.3 Isolation SHALL prevent any interference between units that would compromise determinism.

XVIII.4 A breach of isolation SHALL place the Program in HALTED and SHALL emit a finding.

---

## ARTICLE XIX — EXECUTION CONCURRENCY

XIX.1 Execution SHALL be single-unit by default; exactly one execution unit SHALL be RUNNING at any time within a stage.

XIX.2 Concurrent execution units MAY proceed only when they share no write area and no dependency and are fully isolated.

XIX.3 Concurrent units SHALL produce results that are independent of their relative timing; timing-dependent results ARE PROHIBITED.

XIX.4 The effects of concurrent units SHALL be serialized into a single canonical order (Article XX) before any dependent unit is dispatched.

---

## ARTICLE XX — EXECUTION SERIALIZATION

XX.1 The effects of all execution units SHALL be serializable into a single, deterministic, reproducible order.

XX.2 The serialization order SHALL be canonical such that identical program states yield an identical order.

XX.3 Serialization SHALL resolve any independent-unit ordering deterministically and SHALL NEVER depend on wall-clock time, arrival order, or nondeterministic identifiers.

XX.4 A set of effects that cannot be serialized deterministically SHALL place the Program in HALTED.

---

## ARTICLE XXI — EXECUTION DETERMINISM

XXI.1 Execution SHALL be deterministic: identical program state SHALL yield an identical execution order, identical transitions, and byte-identical reproducible outputs, consistent with CEP-001 Article XX.

XXI.2 Every execution decision SHALL be a function of program state and declared inputs only.

XXI.3 Execution SHALL introduce no source of nondeterminism into any reproducible output.

XXI.4 A determinism failure SHALL transition the affected unit to FAILED.

---

## ARTICLE XXII — EXECUTION COMPLETION

XXII.1 An execution unit SHALL reach COMPLETED only when its action is performed, validated at the applicable gate, and checkpointed.

XXII.2 A COMPLETED unit SHALL transition to HANDED_OFF, passing control through a checkpoint that emits exactly one next authorized action.

XXII.3 Execution completion of a unit SHALL be distinct from stage completion and program completion, which are governed by CEP-001 Article XXII.

XXII.4 No unit SHALL be declared COMPLETED while any blocking finding against it is unresolved.

---

## ARTICLE XXIII — EXECUTION ENFORCEMENT

XXIII.1 Execution law SHALL be enforced at execution transitions and at gates through the general Enforcement Model of CEP-001 Article XXIII.

XXIII.2 An execution violation — an illegal transition, an unauthorized act, a cross-area write, an isolation breach, a circular dependency, or a determinism failure — SHALL place the Program in HALTED, emit a finding, and require remediation, restart, or termination before ADVANCING resumes.

XXIII.3 A void act SHALL have no effect and SHALL be recorded as void.

XXIII.4 Execution enforcement SHALL NEVER be waived, deferred, or overridden by any authority tier.

XXIII.5 Execution enforcement records SHALL be append-only, content-addressed, and auditable.

---

## ARTICLE XXIV — EXECUTION SUPREMACY

XXIV.1 This instrument IS supreme over all execution operation and over every subordinate execution instrument.

XXIV.2 This instrument derives from CEP-000, CEP-001, and CEP-002 and IS subordinate to all three; conflicts resolve in favor of the higher instrument in the order CEP-000, CEP-001, CEP-002.

XXIV.3 This instrument SHALL NOT govern, validate, certify, or legislate evidence or repository content.

XXIV.4 This instrument SHALL bind every remaining Stage of the Program until amended or frozen under its own rules.

---

## ARTICLE XXV — EXECUTION VERSIONING

XXV.1 This instrument carries an explicit version; the present version IS 1.0.

XXV.2 Any change SHALL occur only through the Amendment Model of CEP-001 Article XV and SHALL increment the version.

XXV.3 A superseded version SHALL be retained for lineage and marked superseded; a frozen version SHALL be immutable and content-addressed.

XXV.4 Every subordinate execution instrument SHALL cite the version of this instrument under which it was produced.

---

*END OF ARTIFACT — CEP-003 · CONSTITUTIONAL EXECUTION CONSTITUTION · VERSION 1.0 · NORMATIVE · EXECUTION ONLY · DERIVES FROM CEP-000, CEP-001, CEP-002*
