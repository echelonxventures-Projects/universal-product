# CIOS-04 — CONTINUOUS IMPLEMENTATION OPERATING SYSTEM · ENGINE RESPONSIBILITIES

| Field | Value |
|---|---|
| MISSION | `IMR-003A` — CIOS Constitution & Architecture |
| ARTIFACT | `CIOS-04` — Engine Responsibilities (mission Output 4) |
| DELIVERED BY | `IMR-003A-R1` gap closure (Phase 4). **Additive**: no recovered artifact mutated. |
| ARTIFACT KIND | Architecture (`CMG-K-05`) |
| DISCHARGES | `CIOS-L-10` (Overlap Prohibition — delegated to `CIOS-E-05` here); responsibility boundary for all 24 engines |
| DISCIPLINE | One engine, one responsibility, one **exclusion list**. The exclusion list is what makes the boundary testable. |
| AUTHORITY OF ITS OWN | **NONE.** |
| CONFLICT RULE | `CIOS-01` governs over this artifact; a located canonical instrument governs over `CIOS-01`'s bindings. |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. RESPONSIBILITY FORM

Each engine is specified as five fields. The **EXCLUDES** field is mandatory and load-bearing: a responsibility without an exclusion boundary cannot be shown non-duplicative, and `CIOS-L-09` requires that it be shown.

| Field | Meaning |
|---|---|
| **OWNS** | the one thing this engine decides or produces |
| **CONSUMES** | what it reads (never writes) |
| **PRODUCES** | what it writes, within its plane's scope (`CIOS-02` §4) |
| **EXCLUDES** | what it explicitly does **not** do, and which owner does it instead |
| **FAIL** | its fail-closed behaviour (`CIOS-L-07`) — every engine defaults to non-admission |

---

## 2. `CIOS-PL-A` — ASSIMILATION PLANE

### `CIOS-E-01` — Submission Intake
- **OWNS** — admission of a submission of any kind into `CIOS-PT-00`, and nothing further.
- **CONSUMES** — the submission; `CIOS-PT-00` membership.
- **PRODUCES** — a `CIOS-PT-00` entry with a provisional handle.
- **EXCLUDES** — assigning identity (`E-07`); judging substance (`E-02`…`E-09`); assigning a wave or priority (`E-12`); minting any identifier (`AIF` / `REG-AUTO-001`). A `CIOS-PT-00` handle is **not** an identity and is discardable without record (`CIOS-01` Art V: INTAKE items are *"freely discarded; outside every plan"*).
- **FAIL** — a submission that cannot be represented in `CIOS-PT-00` is not accepted. No partial intake.

### `CIOS-E-02` — Context Assimilation
- **OWNS** — the determination that the submission's context is fully assimilated before any substantive stage runs.
- **CONSUMES** — the submission; Repository Truth; `UCCEP-000000` `G-01` verdict.
- **PRODUCES** — a stage verdict for `CIOS-S-02`.
- **EXCLUDES** — defining what context assimilation *is* — that is `G-01`'s, wholly. This engine **binds** `G-01`; it does not re-implement it, and it may not pass where `G-01` fails.
- **FAIL** — missing, ambiguous or degraded context ⇒ non-admission.

### `CIOS-E-03` — Knowledge Recurrence
- **OWNS** — the determination that the submission's knowledge does or does not already exist, and the resolution of recurrence to **EXTEND**.
- **CONSUMES** — `UAKOS-CLOSURE-002` closure truth (`concept_total`, `concepts`, the seven gap classes); `CK-CLOSURE-P1`, `CK-CLOSURE-P2`.
- **PRODUCES** — a recurrence verdict: NEW · EXTEND · REJECT.
- **EXCLUDES** — creating a canonical home (`E-04`); deciding overlap between two admitted items (`E-05`); defining the matching algorithm (`UAKOS` `closure_engine.py`, `phase2_engine.py`, `phase3_engine.py`). **CREATE is never emitted for recurring knowledge** — `CIOS-L-08`.
- **FAIL** — an unresolvable match ⇒ non-admission. Ambiguity never resolves to NEW.

### `CIOS-E-04` — Canonical Home Resolution
- **OWNS** — resolution of the **single** canonical home and **single** owner.
- **CONSUMES** — `UAKOS` canonical-home register; `closure.json` (`duplicate_canonical_homes`, `not_homed_concepts`, `in_repo_unhomed`).
- **PRODUCES** — a resolved `(home, owner)` pair bound to identity field `CIOS-ID-11`.
- **EXCLUDES** — detecting a *second* home (`E-06`); minting the home's identifier (`REG-AUTO-001`); writing to the corpus (`WS-7` forbids it absolutely).
- **FAIL** — zero homes, or more than one, ⇒ non-admission. `CIOS-INV-06` breach is inadmissible, not degraded.

### `CIOS-E-05` — Overlap Resolution
> `CIOS-01` `CIOS-L-10` delegates its operative content to this engine. This is that content.

- **OWNS** — resolution of **scope overlap** between the submission and any item already in `CIOS-PT-03`, `CIOS-PT-02` or `CIOS-PT-01`, to exactly one owner, **before** admission.
- **CONSUMES** — the submission's declared scope; the scope of every admitted item; `IAC-001D` §05 Reuse Gate; `UCCEP-000000` `G-03`.
- **PRODUCES** — an overlap verdict and, where overlap exists, the single surviving owner plus a redirect of the submission to EXTEND that owner.
- **EXCLUDES** — artifact-level duplicate detection (`E-06`); scheduling (`E-12`); deferring the overlap to execution — expressly forbidden: *"Unresolved overlap is a non-admission, not a scheduling problem"* (`CIOS-L-10`).
- **FAIL** — overlap that cannot be resolved to a single owner ⇒ **non-admission**. There is no "resolve later" path, and no override.

Resolution order is fixed and total, so the outcome is deterministic (`CIOS-L-17`):

| Rank | Rule | Ground |
|---|---|---|
| 1 | If a located canonical owner exists for the overlapping scope, it survives; the submission becomes EXTEND. | `CEP-001` LAW-4 |
| 2 | Else if one of two CIOS-admitted items is SEALED, the sealed item survives. | `CIOS-L-18`, `CIOS-INV-03` |
| 3 | Else if one is IN-FLIGHT, the in-flight item survives. | `CIOS-L-03`, `CIOS-INV-04` |
| 4 | Else the item with the **lower witnessed admission ordinal** survives. | `CIOS-L-15`; `AIF-L04` |
| 5 | Else — unreachable, since ordinals are unique per authority. | `AIF-L07` |

Rank 4 is why ordering authority must be the ordinal and not a timestamp: two submissions can share a timestamp, and then rank 4 would not be total, and `CIOS-INV-09` would fail.

### `CIOS-E-06` — Duplication Detection
- **OWNS** — detection of any second canonical home, owner, identifier, plan, queue, gate or authority the submission would create.
- **CONSUMES** — `closure.json` gap classes; `CMG-REGISTRY.json`; `artifacts.json`; the `id-ledger`; `06-DUPLICATION-AND-OVERLAP-VERIFICATION.md`.
- **PRODUCES** — a duplication verdict enumerating each duplicate class breached.
- **EXCLUDES** — resolving scope overlap (`E-05`); resolving the home (`E-04`); repairing a pre-existing duplicate — CIOS may not mutate the corpus (`WS-7`), so a pre-existing duplicate is emitted as a **finding**, not fixed.
- **FAIL** — any detected duplicate ⇒ non-admission (`CIOS-L-09`; `GOV-001` Part 10).

### `CIOS-E-07` — Identity Composition
- **OWNS** — composition of the 22-field identity record (`CIOS-ID-01 … CIOS-ID-22`, `CIOS-08`) from fields produced by located minting authorities.
- **CONSUMES** — `AIF` minted fields (`AIF-L02` durable identity, `AIF-L04` witnessed ordinal, `AIF-L05` content digest, `AIF-L06` admission key); `REG-AUTO-001` registration transaction; `00-BOOK/tools/`.
- **PRODUCES** — a complete identity record, all 22 fields resolved.
- **EXCLUDES** — **minting anything** (`CIOS-L-12`, `L-14`; `CIOS-01` I.5); assigning an identifier manually (a **hard rejection** under `CIOS-L-12`); altering a minted field (`CIOS-L-13` — correction is by successor only); creating a parallel identifier system (`GOV-001` Part 10).
- **FAIL** — any unresolved field ⇒ non-admission (`CIOS-INV-07`). A 21-of-22 record is not a degraded record; it is not a record.

### `CIOS-E-08` — Dependency Admission
- **OWNS** — the determination that every declared dependency resolves and that admission introduces no cycle.
- **CONSUMES** — `UCCEP-000000` `G-08`; `CK-GRAPH`; `engine/graph`; `IMG-001` `03` dependency graph.
- **PRODUCES** — a dependency verdict + the submission's position in the partial order.
- **EXCLUDES** — defining the graph model (`engine/graph`, `IMG-001` `03`); scheduling (`E-12`); waving (`IMG-001` `04`).
- **FAIL** — an unresolvable dependency or a detected cycle ⇒ non-admission. **`UCCEP-F-003` bound:** the located validator is known to report a cycle while returning `is_valid=true` and exit 0. This engine therefore treats a *reported* cycle as failure regardless of the returned validity flag, and records the discrepancy as a finding. `CIOS-INV-05` remains **not machine-enforced** until `UCCEP-F-003` is discharged by its owner.

### `CIOS-E-09` — Impact Assessment
- **OWNS** — production of the `CEP-009` III.1 impact assessment and classification to exactly one primary class.
- **CONSUMES** — the submission; Repository Truth; `CEP-009` IV.1 class set.
- **PRODUCES** — an impact assessment + exactly one primary class (`CEP-009` IV.6).
- **EXCLUDES** — defining the classes or the route (`CEP-009`); admitting the change (`CEP-009`'s admission authority); assigning more than one primary class — forbidden by IV.6.
- **FAIL** — no assessable impact, or ambiguous classification, ⇒ non-admission.

### `CIOS-E-10` — Partition Assignment
- **OWNS** — the transition `CIOS-PT-00 → CIOS-PT-03`, and **only** that transition.
- **CONSUMES** — the verdicts of `E-02`…`E-09`.
- **PRODUCES** — a `CIOS-PT-03` membership record.
- **EXCLUDES** — `PT-03 → PT-02` (that is dispatch: `E-15` hands off, `IEC-001` C7 dispatches); `PT-02 → PT-01` (`E-19`); any reverse transition except the located `IEC-001` `06` FAILED→READY retry, which CIOS binds and does not redefine (`CIOS-01` V.3).
- **FAIL** — any upstream non-admission ⇒ the item stays in `CIOS-PT-00`. Fail-closed means it does **not** advance.

### `CIOS-E-11` — Plan Epoch Composition
- **OWNS** — composition of the staged candidate `PLAN[n+1]`.
- **CONSUMES** — `PLAN[n]` (read-only); `CIOS-PT-03` membership; `E-12` order.
- **PRODUCES** — `PLAN[n+1]` as a staged candidate.
- **EXCLUDES** — mutating `PLAN[n]` (**zero** writers, `CIOS-02` §4.3); adopting `PLAN[n+1]` (`E-14`); reaching `CIOS-PT-02` or `PT-01` (`WS-1`).
- **FAIL** — a candidate that cannot be composed leaves `PLAN[n]` active and untouched. This is the `CIOS-L-05` degradation path: future planning degrades, present execution does not.

### `CIOS-E-12` — Priority Derivation
- **OWNS** — derivation of a **total** order over `CIOS-PT-03` from the declared key vector `CIOS-K-01 … CIOS-K-08` (`CIOS-10`).
- **CONSUMES** — `CIOS-PT-03`; `cios-bindings.json` key vector; `IEC-001` `04` order (`wave, family, id`); `IMG-001` `05` topological order.
- **PRODUCES** — a total order.
- **EXCLUDES** — manual selection (**prohibited**, `CIOS-L-16`); altering the located order — the located triple `wave, family, id` is preserved as the **leading elements** of the key vector, so CIOS never reorders what `IEC-001` already ordered; deciding *when* to re-derive (`E-13`).
- **FAIL** — a tie unresolved after the full key vector is a `CIOS-INV-09` breach ⇒ inadmissible. The final key element is therefore the witnessed admission ordinal, which is unique per authority (`AIF-L07`) and makes the order total by construction.

### `CIOS-E-13` — Realignment
- **OWNS** — the decision to resequence `CIOS-PT-03`, and the resequencing itself.
- **CONSUMES** — `CIOS-PT-03`; new admissions; `E-12` order.
- **PRODUCES** — a resequenced `CIOS-PT-03`.
- **EXCLUDES** — touching `CIOS-PT-02` (`CIOS-INV-04`); touching `CIOS-PT-01` (`CIOS-INV-03`); rebinding a dispatched item's plan epoch; altering `PLAN[n]`. **Realignment writes only `CIOS-PT-03`** — `CIOS-L-19`, `CIOS-01` V.2.
- **FAIL** — a realignment that would reach outside `CIOS-PT-03` is rejected in full; there is no partial realignment.

### `CIOS-E-14` — Quiescent Adoption
- **OWNS** — atomic adoption of `PLAN[n+1]` at the Quiescent Adoption Point.
- **CONSUMES** — `PLAN[n+1]`; the located batch-cut boundary (`IEC-001` `05`).
- **PRODUCES** — `PLAN[n+1]` becomes `PLAN[n]`; epoch counter advances (`n := n+1`, `CIOS-01` VI.4).
- **EXCLUDES** — defining the batch-cut boundary (`IEC-001` `05`); adopting mid-batch; applying adoption to anything but `CIOS-PT-03` (`CIOS-01` VI.2); rebinding in-flight items (`CIOS-INV-04`).
- **FAIL** — adoption that cannot complete atomically does not occur; `PLAN[n]` remains active. **No partial epoch exists.**

---

## 3. `CIOS-PL-B` — EXECUTION PLANE

### `CIOS-E-15` — Ready Handoff
- **OWNS** — handing the head of `CIOS-Q-04` to the located Execution Queue.
- **CONSUMES** — `CIOS-Q-04`; `IEC-001` `04` Execution Queue admission conditions.
- **PRODUCES** — a handoff record; the item leaves CIOS's queue family.
- **EXCLUDES** — evaluating the READY predicates (`IEC-001` `03` P1–P7 — located, and CIOS does not re-evaluate them); forming batches (`IEC-001` `05`); dispatching (`IEC-001` C7); any control after handoff — **CIOS relinquishes fully**.
- **FAIL** — an item the located queue will not accept remains in `CIOS-Q-04`. CIOS never forces admission.

### `CIOS-E-16` — Dispatch Window
- **OWNS** — binding a dispatched item to the plan epoch active at dispatch, and holding that binding until terminal state.
- **CONSUMES** — dispatch events; the active epoch.
- **PRODUCES** — an immutable `(item, epoch)` binding.
- **EXCLUDES** — rebinding on adoption (`CIOS-INV-04` forbids); extending the window; dispatching (`IEC-001` C7).
- **FAIL** — an item that cannot be epoch-bound is not dispatched. No unbound in-flight item may exist.

### `CIOS-E-17` — Interruption Guard
- **OWNS** — rejection of every attempt to interrupt, suspend, mutate, reorder or invalidate a dispatched item.
- **CONSUMES** — all interruption attempts, from any plane or source.
- **PRODUCES** — a rejection + a finding per attempt.
- **EXCLUDES** — admitting an override (`E-18`); defining retry (`IEC-001` `06`, bounded by `MAX_RETRY`); blocking assimilation — the guard protects execution **from** assimilation, and never the reverse (`CIOS-L-02`).
- **FAIL** — **default-deny.** An attempt whose authority cannot be established is rejected. `CIOS-L-03` admits no exception; the only lawful reach is via `E-18`.

### `CIOS-E-18` — Override Adjudication
- **OWNS** — admission of a reach into protected or sealed work from a located override authority.
- **CONSUMES** — override requests; `CIOS-OR-01` (Constitutional Migration Authority) / `CIOS-OR-02` (Critical Repository Integrity Authority) credentials; `CEP-009` Art III / Art XX.2 protocol.
- **PRODUCES** — an adjudication + a mandatory immutable record.
- **EXCLUDES** — creating an override authority (both are **located**, `CIOS-L-21`); acting silently — *"Both act by declared, evidenced, recorded protocol; never silently"*; admitting a third authority — **exactly two exist**.
- **FAIL** — default-deny. Missing credential, missing evidence, or missing protocol record ⇒ rejection. An unrecorded override is void.

---

## 4. `CIOS-PL-C` — TRUTH PLANE

### `CIOS-E-19` — Seal Transition
- **OWNS** — the transition `CIOS-PT-02 → CIOS-PT-01`.
- **CONSUMES** — terminal-state events (`IEC-001` `06`); `CEP-007` seal preconditions.
- **PRODUCES** — a `CIOS-PT-01` membership record.
- **EXCLUDES** — declaring a `CEP-007` **freeze** — freeze is a located act, and it is **unavailable** (`GD-10`; `CIOS-01` IX.2); mutating a sealed item (`CIOS-INV-03`); sealing a non-terminal item.
- **FAIL** — any unmet precondition ⇒ the item remains `CIOS-PT-02`. **No partial seal exists.**

> **Disclosure.** `CIOS-PT-01` (SEALED) is a CIOS **mutability partition**, not a `CEP-007` freeze state. An item in `CIOS-PT-01` is immutable *within the CIOS model*; it is not a frozen artifact in the constitutional sense and carries no freeze baseline. Conflating the two would be the category error `GD-10-C5` warns against.

### `CIOS-E-20` — Truth Append
- **OWNS** — appending the record of what became true.
- **CONSUMES** — seal records; `AIF-L08` DAG ledger form.
- **PRODUCES** — an appended truth record.
- **EXCLUDES** — editing or deleting recorded truth (`AIF-L17` — correction is a new event); regenerating `closure.json` (`IEC-001` C10 / `07` owns regeneration); mutating any located register.
- **FAIL** — an append that cannot complete ⇒ no seal (fail-closed, `WS-4`). The system prefers an unsealed truth to a false one.

### `CIOS-E-21` — Traceability Emission
- **OWNS** — emission of the `id → artifact` traceability binding for a sealed item.
- **CONSUMES** — the sealed item; its canonical home; `CEP-008`; `UMB-007`.
- **PRODUCES** — a traceability edge.
- **EXCLUDES** — defining the traceability model (`CEP-008`, `UMB-007`); claiming traceability **closure** — expressly forbidden while `UCCEP-F-002` stands (1198/1198 artifacts incomplete). See `CIOS-17` §5.
- **FAIL** — an unresolvable binding ⇒ finding, and the item is recorded as traceability-incomplete. It does **not** block the seal, because traceability closure is not a CIOS-ownable condition while `UCCEP-F-002` is open.

---

## 5. `CIOS-PL-D` — OBSERVATION PLANE

### `CIOS-E-22` — Invariant Observation
- **OWNS** — evaluation of `CIOS-INV-01 … INV-12` (excluding `INV-10`, which is `E-23`'s) over observable state.
- **CONSUMES** — all planes' observable state; `CK-SELF-DECLARATION`, `CK-SELF-WRITE-SCOPE`, `CK-SELF-NO-ENUMERATION`.
- **PRODUCES** — one finding per breach.
- **EXCLUDES** — **writing anything** (`WS-6`); blocking a transition (that is `IEC-001` C11's, located); acting on its own findings.
- **FAIL** — inability to observe is itself a finding. A blind observer never reports a pass.

### `CIOS-E-23` — Monotonicity Observation
- **OWNS** — observation that the certified set is monotone non-decreasing across epochs (`CIOS-INV-10`).
- **CONSUMES** — the certified set per epoch; `CK-HEALTH`.
- **PRODUCES** — a monotonicity finding.
- **EXCLUDES** — writing; certifying (`CEP-005`); repairing a regression.
- **FAIL** — a detected decrease is a `CIOS-L-20` breach and is emitted as a **maximum-severity** finding for the located authority to act on.

### `CIOS-E-24` — Determinism Observation
- **OWNS** — observation that identical Repository Truth and declared data yield identical admission verdicts, identity derivation (excluding the witnessed ordinal, `AC-10`), plan epoch, priority order and schedule.
- **CONSUMES** — replayed runs; `CK-RIE-DETERMINISM`, `CK-DETERMINISM-BUILD`, `CK-SELF-DETERMINISM`.
- **PRODUCES** — a determinism finding.
- **EXCLUDES** — writing; defining replay tiering (`AIF-L19`, eight replay classes); asserting determinism of located engines — it observes CIOS's own composition only.
- **FAIL** — divergence is a `CIOS-L-17` breach ⇒ finding. The witnessed admission ordinal is **excluded** from the comparison because `AIF-L04` makes it authority-local and non-recomputable.

---

## 6. RESPONSIBILITY COVERAGE

| Check | Result |
|---|---|
| Engines specified | **24 / 24** |
| Engines with exactly one OWNS statement | **24 / 24** |
| Engines with a non-empty EXCLUDES list | **24 / 24** |
| Engines with declared fail-closed behaviour | **24 / 24** (`CIOS-L-07`) |
| Engines claiming authority of their own | **0** (`CIOS-L-11`) |
| Engines minting identity | **0** (`CIOS-L-14`) |
| Engines dispatching | **0** (`CIOS-01` I.4) |
| Engines acting as a gate | **0** (`CIOS-01` I.6) |
| Engines writing outside their plane's scope | **0** (`CIOS-02` §4) |
| Observation-plane engines with write authority | **0** (`WS-6`) |
| Duplicate responsibilities | **0** (`CIOS-03` §5 pairwise analysis) |
| `CIOS-L-10` operative content delivered | **YES** — `E-05`, incl. total resolution order |

---

## AUTHORITY BOUNDARY (MANDATORY)

This artifact assigns responsibilities. It owns no mechanism, no registry, no gate, no identifier space and no concern. No engine holds authority; every authority named is located in an instrument existing independently at `b26c5bb`. Where this artifact and a located canonical instrument disagree, **the located instrument governs and this artifact SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `CIOS-04` · PROVISIONAL · ADDITIVE · COMPOSITION-ONLY · AUTHORITY-NEUTRAL**
