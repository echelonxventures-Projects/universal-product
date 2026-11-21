# CIOS-02 — CONTINUOUS IMPLEMENTATION OPERATING SYSTEM · OPERATING MODEL

| Field | Value |
|---|---|
| MISSION | `IMR-003A` — CIOS Constitution & Architecture |
| ARTIFACT | `CIOS-02` — Operating Model (mission Output 2) |
| DELIVERED BY | `IMR-003A-R1` gap closure (Phase 4). **Additive**: no recovered artifact mutated. |
| ARTIFACT KIND | Architecture (`CMG-K-05`) — operating model of a composition instrument |
| CLASSIFICATION | GOVERNANCE · additive-only · programme-owned under `00-MASTER/IMR-003A/` |
| GOVERNED BY | `CIOS-01` Art IV (planes), Art V (partitions), Art VI (epochs) — **authoritative input, not restated as new law** |
| DISCHARGES | `CIOS-L-02` (Plane Separation, §2 + §4) · `CIOS-L-05` (Bounded Assimilation, §4) · `CIOS-INV-02` (write-scope confinement) |
| AUTHORITY OF ITS OWN | **NONE.** Detail only. Every mechanism is a pointer to a located owner. |
| CONFLICT RULE | Where this artifact and `CIOS-01` differ, **`CIOS-01` governs**. Where this artifact and a located canonical instrument differ, **the located instrument governs** and this artifact SHALL be corrected. |
| BASELINE | `b26c5bb` · branch `programme/evo-usis-005` |
| STANDING | PROVISIONAL (`CMG-L-12`); Tier T1 VACANT |

---

## 1. WHAT THIS ARTIFACT OWNS

`CIOS-01` Art IV.1 declares four planes and delegates their detail here. `CIOS-L-02` and `CIOS-L-05` delegate their **operative content** — write scopes — to `§4`. Until `§4` existed, `CIOS-INV-02` was unenforceable.

This artifact owns exactly three things:

1. the **plane detail** (§2) — function, membership, clock, failure semantics;
2. the **write scopes** (§4) — the enforceable content of `CIOS-INV-02`;
3. the **non-blocking proof** (§5) — the argument that `CIOS-L-01` and `CIOS-L-03` are simultaneously satisfiable.

It owns **no** mechanism. The controller, queues, states, gates, predicates, waves and identity allocator are located elsewhere and are bound, never restated.

---

## 2. THE FOUR PLANES — DETAIL

Plane identity, function, write scope and block-authority are fixed by `CIOS-01` Art IV.1 and reproduced here **by reference**. This section adds only detail Art IV.1 delegates.

### 2.1 `CIOS-PL-A` — ASSIMILATION PLANE

| Property | Value |
|---|---|
| Function | prepare **future** work |
| Engines | `CIOS-E-01 … CIOS-E-14` (14) |
| Write scope | `CIOS-PT-03` (OPEN) + own operational memory — **see §4** |
| May block execution? | **NO** (`CIOS-01` Art IV.1) |
| Clock | assimilation clock — advances on submission arrival; rate unbounded (`CIOS-L-24`) |
| Input | submissions from any source: knowledge, decision, idea, discovery, enhancement, optimization, governance improvement, repository evolution, architecture evolution |
| Output | admitted items placed in `CIOS-PT-03`; a staged candidate epoch `PLAN[n+1]` |
| Failure semantics | **degrades future planning only.** An assimilation failure leaves `PLAN[n]` active and every in-flight item untouched (`CIOS-L-05`). |
| Bound located owners | `UAKOS-CLOSURE-002` (knowledge intake, canonical matching, canonical home); `UCDA-000001` (decision assimilation, disposition obligation); `UCCEP-000000` G-01…G-09 (admission gates); `AIF` + `REG-AUTO-001` (identity minting) |

Assimilation is **unbounded in volume and bounded in effect**. This asymmetry is the whole of `CIOS-L-05`: the plane may receive any quantity of submissions at any rate, and can affect nothing except the partition that has not yet been dispatched.

### 2.2 `CIOS-PL-B` — EXECUTION PLANE

| Property | Value |
|---|---|
| Function | realize **present** work |
| Engines | `CIOS-E-15 … CIOS-E-18` (4) |
| Write scope | `CIOS-PT-02` (IN-FLIGHT) state; Repository Truth **only** via `CIOS-PL-C` — see §4 |
| May block execution? | — (it *is* execution) |
| Clock | execution clock — advances on the located controller's tick (`IEC-001` §4 loop) |
| Input | the head of `CIOS-Q-04` handed to the located Execution Queue |
| Output | items reaching a terminal state; seal requests to `CIOS-PL-C` |
| Failure semantics | a failed item follows the **located** retry rule (`IEC-001` `06` FAILED→READY, bounded by `MAX_RETRY`). CIOS does not redefine it. |
| Bound located owners | `IEC-001` C1–C12 (controller), `03` P1–P7 (READY predicates), `04` (Execution/Ready/Blocked/Excluded queues), `05` (batch formation), `06` (10-state machine), `08` Q1–Q8 (quality gates), `09` (execution governance); `IMG-001` `03`–`09` (backlog, graph, waves, order, critical path, readiness) |

**Dispatch authority is not CIOS's** (`CIOS-01` I.4). It remains with the located Execution Authority (`CMG` T4) exercised through `IEC-001` C7 in the EC-3 lane. `CIOS-PL-B` composes what reaches the located queue and protects what is already in flight; it does not dispatch.

### 2.3 `CIOS-PL-C` — TRUTH PLANE

| Property | Value |
|---|---|
| Function | record what **became** true |
| Engines | `CIOS-E-19 … CIOS-E-21` (3) |
| Write scope | **append-only** to Repository Truth — see §4 |
| May block execution? | **NO** |
| Clock | truth clock — advances on terminal-state events |
| Input | seal requests from `CIOS-PL-B` |
| Output | appended truth records; traceability emissions |
| Failure semantics | a truth-append failure **fails closed** (`CIOS-L-07`): the item does not become SEALED and remains IN-FLIGHT. No partial seal exists. |
| Bound located owners | `CEP-008` (evidence & traceability); `CEP-007` (freeze/seal authority); `UAKOS-CLOSURE-002` `closure.json` (closure truth); `AIF-L08` (DAG ledger), `AIF-L14` (atomic admission), `AIF-L17` (forward-only compensation) |

Append-only is not a CIOS invention. It is `AIF-L17` (*no deletion or edit of Recorded Truth; correction is a new event*), bound here and not restated.

### 2.4 `CIOS-PL-D` — OBSERVATION PLANE

| Property | Value |
|---|---|
| Function | measure and report |
| Engines | `CIOS-E-22 … CIOS-E-24` (3) |
| Write scope | **nothing.** Emits findings only. — see §4 |
| May block execution? | **NO** |
| Clock | observation clock — advances freely; may lag arbitrarily |
| Input | the observable state of all planes |
| Output | findings. **Never** a mutation, never a gate verdict, never a block. |
| Failure semantics | observation failure is **invisible** to every other plane. A blind observer does not stop the system. |
| Bound located owners | `platform/measurement` (health measurement); `intelligence/rie` (repository evolution & drift intelligence); `CEP-010` (audit & compliance); `UCCEP-000000` `17-ASSIMILATION-FINDINGS-REGISTER.md` (findings register form) |

**Observation has no authority.** A finding is evidence for a located authority to act on, never an act. This is what prevents the observation plane from becoming a shadow gate (`AC-4`).

---

## 3. PLANE COMPOSITION

The planes compose as a **pipeline with one one-way coupling and three feedback-free emissions**. There is no cycle, which is why no plane can wait on another.

```
                    submissions (unbounded rate, any source)
                             │
                             ▼
   ┌──────────────────────────────────────────────┐
   │ CIOS-PL-A  ASSIMILATION      E-01 … E-14     │  writes: CIOS-PT-03 + own memory
   │   admits · homes · identifies · partitions   │
   │   composes PLAN[n+1]                         │
   └───────────────────┬──────────────────────────┘
                       │ Quiescent Adoption Point (CIOS-01 VI.2)
                       │ atomic · applies ONLY to CIOS-PT-03
                       ▼
   ┌──────────────────────────────────────────────┐
   │ CIOS-PL-B  EXECUTION         E-15 … E-18     │  writes: CIOS-PT-02 state
   │   hands off to IEC-001 · binds epoch         │
   │   guards interruption · adjudicates override  │
   └───────────────────┬──────────────────────────┘
                       │ seal request (terminal state reached)
                       ▼
   ┌──────────────────────────────────────────────┐
   │ CIOS-PL-C  TRUTH             E-19 … E-21     │  writes: Repository Truth (append-only)
   │   seals · appends · emits traceability       │
   └───────────────────┬──────────────────────────┘
                       │ (read-only observation of all planes)
                       ▼
   ┌──────────────────────────────────────────────┐
   │ CIOS-PL-D  OBSERVATION       E-22 … E-24     │  writes: NOTHING — findings only
   └──────────────────────────────────────────────┘
```

**The one-way coupling** is `PL-A → PL-B` at the Quiescent Adoption Point. It is one-way because adoption applies **only** to `CIOS-PT-03` (`CIOS-01` V.2), and no item in `CIOS-PT-02` or `CIOS-PT-01` is reachable from it (`CIOS-INV-04`, `CIOS-INV-03`).

**There is no back-edge.** `PL-B` never signals `PL-A` to slow, pause or wait. `PL-C` never signals `PL-B`. `PL-D` signals nothing at all. Absence of a back-edge is what makes `CIOS-L-04` (Independent Clocks) structurally true rather than a policy aspiration.

---

## 4. WRITE SCOPES — THE ENFORCEABLE CONTENT OF `CIOS-INV-02`

This section is the operative content `CIOS-L-02` and `CIOS-L-05` delegate here. A write outside the declared scope is not a degraded state; it is **inadmissible** (`CIOS-01` Art III).

### 4.1 Write-scope matrix

`W` = may write · `R` = may read · `—` = no access · `A` = append-only

| Target | `PL-A` | `PL-B` | `PL-C` | `PL-D` |
|---|---|---|---|---|
| `CIOS-PT-00` INTAKE | **W** | — | — | R |
| `CIOS-PT-03` OPEN | **W** | R | — | R |
| `CIOS-PT-02` IN-FLIGHT | — | **W** | R | R |
| `CIOS-PT-01` SEALED | R | R | **A** | R |
| `PLAN[n]` (active epoch) | R | R | — | R |
| `PLAN[n+1]` (staged candidate) | **W** | — | — | R |
| Repository Truth (`closure.json` and located registers) | R | — | **A** | R |
| Plane's own operational memory | **W** | **W** | **W** | **W** |
| Located corpus artifacts (outside `00-MASTER/IMR-003A/`) | — | — | — | — |
| Findings channel | — | — | — | **W** |

### 4.2 Write-scope rules

| ID | Rule | Enforces |
|---|---|---|
| `WS-1` | `PL-A` SHALL NOT write `CIOS-PT-02`, `CIOS-PT-01`, or `PLAN[n]`. | `CIOS-L-03`, `CIOS-L-05`, `CIOS-L-18`, `CIOS-L-19` |
| `WS-2` | `PL-B` SHALL NOT write `CIOS-PT-03` or `PLAN[n+1]`. Execution does not replan. | `CIOS-L-16` (Derived Selection) |
| `WS-3` | `PL-B` SHALL NOT write Repository Truth directly. All truth transits `PL-C`. | `CIOS-01` Art IV.1 |
| `WS-4` | `PL-C` writes Repository Truth **append-only**. No edit, no delete, no in-place correction. | `AIF-L17`; `CEP-008` |
| `WS-5` | `PL-C` SHALL NOT write `CIOS-PT-03` or `PLAN[n+1]`. Recording truth does not replan. | `CIOS-L-19` |
| `WS-6` | `PL-D` SHALL NOT write any partition, any plan, or Repository Truth. **Zero write authority.** | `AC-4`; `CIOS-INV-12` |
| `WS-7` | No plane writes any artifact outside `00-MASTER/IMR-003A/`. | `AC-9`; `CIOS-INV-12` |
| `WS-8` | `CIOS-PT-01` (SEALED) is writable **only** by `PL-C`, **only** by append, and **only** on a `CIOS-PL-B` terminal-state event — or by a located override authority under `CIOS-11` §4. | `CIOS-INV-03`; `CIOS-L-21` |
| `WS-9` | A write attempt outside scope **fails closed** and is recorded as a finding. It is never retried into success. | `CIOS-L-07`; `CIOS-INV-02` |

### 4.3 Disjointness proof for `CIOS-INV-02`

`CIOS-INV-01` requires the partitions be pairwise disjoint and jointly exhaustive; `CIOS-INV-02` requires no write cross a plane's scope. Reading down each partition column of §4.1:

| Partition | Planes with `W`/`A` | Count | Disjoint writer? |
|---|---|---|---|
| `CIOS-PT-00` INTAKE | `PL-A` | 1 | **YES** |
| `CIOS-PT-03` OPEN | `PL-A` | 1 | **YES** |
| `CIOS-PT-02` IN-FLIGHT | `PL-B` | 1 | **YES** |
| `CIOS-PT-01` SEALED | `PL-C` (append) | 1 | **YES** |
| `PLAN[n]` | none | 0 | **YES** — the active epoch is immutable by construction (`CIOS-01` VI.1) |
| `PLAN[n+1]` | `PL-A` | 1 | **YES** |
| Repository Truth | `PL-C` (append) | 1 | **YES** |

**Every mutable target has exactly one writer.** No lock is required anywhere in the model, and no two planes can contend. This single-writer property is the mechanism by which `CIOS-INV-02` is checkable rather than aspirational, and it is why `CIOS-01` Art IV.2 calls plane separation *constitutional, not architectural convenience*.

---

## 5. NON-BLOCKING PROOF — `CIOS-L-01` ∧ `CIOS-L-03`

`CIOS-01` P.2 states the problem: if admitting new knowledge requires the plan to stop, implementation halts every time the repository learns. The claim to be discharged is that Perpetual Operation (`CIOS-L-01`) and Non-Interruption (`CIOS-L-03`) hold **together**.

| Step | Claim | Ground |
|---|---|---|
| 1 | Assimilation can always proceed. | Its write scope (`CIOS-PT-03`, `PLAN[n+1]`, own memory) has no other writer (§4.3) ⇒ it never waits on a lock. |
| 2 | Assimilation can never reach in-flight work. | `WS-1` — `PL-A` has no write access to `CIOS-PT-02`. |
| 3 | Assimilation can never reach sealed work. | `WS-1`, `WS-8` — `PL-A` has read-only access to `CIOS-PT-01`. |
| 4 | Assimilation can never alter the active plan. | `PLAN[n]` has **zero** writers (§4.3); assimilation writes only the candidate `PLAN[n+1]`. |
| 5 | Adoption cannot preempt a dispatched item. | Adoption is atomic at the Quiescent Adoption Point and applies **only** to `CIOS-PT-03` (`CIOS-01` VI.2); a dispatched item is in `CIOS-PT-02` and stays bound to `PLAN[n]` until terminal (`CIOS-INV-04`). |
| 6 | Execution never waits on assimilation. | Execution reads `PLAN[n]`, which is already complete and immutable; it requires nothing from `PL-A`. |
| 7 | Therefore neither plane blocks the other. | 1–6. |
| 8 | Therefore an empty Ready Queue is idle, never finished. | `CIOS-L-01`: assimilation may add to `CIOS-PT-03` at any time by step 1, so no state is terminal. |

**Consequence recorded explicitly:** no lock, semaphore, barrier, drain or stop-the-world step appears anywhere in the CIOS model. Where a naive design would need one, the write-scope partition supplies the guarantee structurally. `CIOS-11` §3 defines the **one** deliberate exception — the quiesce protocol — which is available only to the two located override authorities and is never used for routine assimilation.

---

## 6. DEGRADATION SEMANTICS

`CIOS-L-05` requires that assimilation failure degrade future planning and never present execution. Stated per plane so the claim is testable:

| Failing plane | Effect on `PL-A` | Effect on `PL-B` | Effect on `PL-C` | Effect on `PL-D` | System verdict |
|---|---|---|---|---|---|
| `PL-A` | halted | **none** — `PLAN[n]` intact, in-flight untouched | none | observes | **DEGRADED-FUTURE**: present work completes; no new work is admitted |
| `PL-B` | **none** — continues admitting into `CIOS-PT-03` | halted | idle (no seal requests) | observes | **DEGRADED-PRESENT**: backlog accumulates lawfully in OPEN |
| `PL-C` | none | items reach terminal but **cannot seal** (fail-closed, `WS-4`) | halted | observes | **DEGRADED-TRUTH**: `CIOS-PT-02` grows; no false seal is recorded |
| `PL-D` | none | none | none | blind | **DEGRADED-OBSERVATION**: system runs unobserved; **no** functional impact |

Three properties hold in every row and are the point of the table:

- **No cascade.** No single plane's failure halts more than itself plus its strictly-downstream consumers.
- **No false progress.** Every failure mode is fail-closed (`CIOS-L-07`); none produces a spurious seal, a spurious admission or a spurious certification.
- **No regression.** No failure mode reduces the certified set (`CIOS-L-20`, `CIOS-INV-10`) or mutates a sealed item (`CIOS-INV-03`).

---

## 7. WHAT THIS ARTIFACT DOES NOT DO

| Not done | Located owner |
|---|---|
| Define the controller or dispatch | `IEC-001` C1–C12 |
| Define item states or transitions | `IEC-001` `06` (10 states) |
| Define READY predicates | `IEC-001` `03` P1–P7 |
| Define quality gates | `IEC-001` `08` Q1–Q8 |
| Define waves, backlog, order, critical path | `IMG-001` `03`–`09` |
| Mint identity | `AIF` + `REG-AUTO-001` |
| Define constitutional gates | `UCCEP-000000` G-01…G-14 |
| Declare a freeze or seal authority | `CEP-007` — and freeze is **unavailable** (`GD-10`; `CIOS-01` IX.2) |
| Enumerate any domain, technology, vendor, platform, language, protocol or format | prohibited by `CIOS-L-22` |

---

## AUTHORITY BOUNDARY (MANDATORY)

This artifact supplies **detail** delegated to it by `CIOS-01` Art IV. It owns no mechanism, no registry, no gate, no identifier space and no concern. Every authority it names is located in an instrument existing independently at `b26c5bb`. Where this artifact and a located canonical instrument disagree, **the located instrument governs and this artifact SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `CIOS-02` · PROVISIONAL · ADDITIVE · COMPOSITION-ONLY · AUTHORITY-NEUTRAL**
