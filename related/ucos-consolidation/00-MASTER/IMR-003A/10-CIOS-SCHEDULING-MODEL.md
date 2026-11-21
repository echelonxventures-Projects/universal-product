# CIOS-10 — CONTINUOUS IMPLEMENTATION OPERATING SYSTEM · SCHEDULING MODEL

| Field | Value |
|---|---|
| MISSION | `IMR-003A` — CIOS Constitution & Architecture |
| ARTIFACT | `CIOS-10` — Scheduling Model (mission Output 10) |
| DELIVERED BY | `IMR-003A-R1` gap closure (Phase 4). **Additive**: no recovered artifact mutated. |
| DISCHARGES | `CIOS-L-04` (Independent Clocks — §5) · `CIOS-L-24` (Unbounded Capacity — §3) · `CIOS-INV-09` (total order) · `CIOS-01` Art VII.3 rows r5, r6 · closes `U-2` (the `CIOS-K-*` element set) |
| NUMERIC CONTRACT | **8 key elements**, `CIOS-K-01 … CIOS-K-08` |
| AUTHORITY OF ITS OWN | **NONE.** |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. WHAT THIS ARTIFACT OWNS

Three things `CIOS-01` delegates here and nothing else:

| § | Subject | Delegating clause |
|---|---|---|
| §2 | the declared priority key vector `CIOS-K-01 … CIOS-K-08` | Art VII.3 r6; `CIOS-INV-09` |
| §3 | the unbounded wave successor function | Art VII.3 r5; `CIOS-L-24` |
| §5 | independent clocks | `CIOS-L-04` |

It owns **no** scheduler. Dispatch timing, batch size and tick rate are located in `IEC-001` (`05`, §4 loop) and are bound, never restated.

---

## 2. THE PRIORITY KEY VECTOR — `CIOS-K-01 … CIOS-K-08`

### 2.1 The preservation requirement

`IEC-001` `04` fixes queue order as `wave, family, id`. `CIOS-01` Art VII.3 r6 authorizes CIOS to add *"priority as a declared, extensible key vector"* — and `CIOS-01` I.3 forbids CIOS from narrowing or reinterpreting any located instrument.

**Therefore the located triple must survive intact.** The vector is constructed so that for any item bearing a located `id`, evaluation reduces exactly to `wave, family, id` — the located order, unchanged. Extension applies only where the located order is silent: to submissions that have no located `id` because they did not exist when the located plan was fixed.

### 2.2 The vector

Evaluated left to right; the first element that discriminates decides.

| Rank | ID | Element | Source | Direction | Role |
|---|---|---|---|---|---|
| 1 | `CIOS-K-01` | **wave** | `IMG-001` `04` (W1…W5, extended by §3) | ascending | located — leading element |
| 2 | `CIOS-K-02` | **family** | `IMG-001` `02` family→owner map | located collation | located |
| 3 | `CIOS-K-03` | **located id** — present ⇒ sorts **before** all absent; absent ⇒ sorts last within `(wave, family)` | `IMG-001` `09` backlog | ascending; absent last | located; **preserves the 77 exactly** |
| 4 | `CIOS-K-04` | **dependency depth** — position in the partial order (`CIOS-ID-15`) | `E-08`; `engine/graph` | ascending (shallower first) | extension |
| 5 | `CIOS-K-05` | **critical-path membership** | `IMG-001` `07` critical path | on-path first | extension |
| 6 | `CIOS-K-06` | **blocking degree** — count of items this item blocks | derived from the dependency graph | descending | extension |
| 7 | `CIOS-K-07` | **primary change class rank** (`CIOS-ID-17`) | `cios-bindings.json` declared rank over `CEP-009` IV.1 classes | ascending rank | extension |
| 8 | `CIOS-K-08` | **witnessed admission ordinal** (`CIOS-ID-06`) | `AIF-L04` | ascending | **terminator** — guarantees totality |

### 2.3 Located-order preservation proof

| Claim | Ground |
|---|---|
| For two items both bearing a located `id`, the comparison resolves at rank ≤ 3. | `CIOS-K-03` is unique among located items (`IMG-001` `09` backlog ids are distinct), so ranks 4–8 are never consulted. |
| The resolution at ranks 1–3 is exactly `wave, family, id`. | §2.2 rows 1–3. |
| ∴ the relative order of the located 77 is **byte-identical** to `IEC-001` `04`. | above |
| A submission without a located `id` never displaces a located item within the same `(wave, family)`. | `CIOS-K-03`'s *absent-sorts-last* rule. |
| ∴ new submissions **append**; they never interleave into the located plan. | above |

This is what `CIOS-01` Art VII.3 means by contributing without duplicating: the located order is an **initial segment** of the CIOS order, not a competing order.

### 2.4 Totality proof — `CIOS-INV-09`

| Step | Claim |
|---|---|
| 1 | `CIOS-INV-09` requires the priority order be **total**: no tie may remain unresolved after the full key vector. |
| 2 | `CIOS-K-08` is the witnessed admission ordinal (`CIOS-ID-06`). |
| 3 | The ordinal is unique within its minting authority (`AIF-L07` authority-namespaced uniqueness). |
| 4 | Every admitted item carries exactly one ordinal, minted once (`CIOS-ID-06`, RECORDED-immutable). |
| 5 | ∴ no two items share a `CIOS-K-08` value, so the comparison always resolves by rank 8 at the latest. |
| 6 | **∴ the order is total. `CIOS-INV-09` holds.** |

**A timestamp could not close this proof.** Two admissions can share a timestamp, leaving step 5 false. This is the operative reason `CIOS-L-15` fixes ordering authority as the ordinal — the invariant is unsatisfiable otherwise.

### 2.5 Extensibility

Per `CIOS-L-23`, ranks, weights and directions are **declared data entries** in `cios-bindings.json`. Adding a discriminator is a data change amending no law and altering no engine.

| Permitted by data change | Requires `CEP-009` III.1 change to `CIOS-01` |
|---|---|
| adding an element between ranks 4 and 7 | changing the count from 8 in a way that displaces `CIOS-K-08` |
| changing a direction or a declared class rank | removing `CIOS-K-01 … CIOS-K-03` (would breach `CIOS-01` I.3) |
| adding a change-class to the `CIOS-K-07` rank table | displacing `CIOS-K-08` from the terminal position (would break §2.4) |

Two positions are structurally locked: ranks 1–3 by located-order preservation (§2.3), and rank 8 by totality (§2.4). Everything between them is free.

---

## 3. UNBOUNDED CAPACITY — THE WAVE SUCCESSOR FUNCTION

`CIOS-L-24` forbids assuming a finite number of submissions, items, dependencies, waves, epochs, queues or planning cycles. `IMG-001` `04` enumerates W1–W5 as a finite set and declares a terminal state after Wave-05 — correct for a fixed backlog, closed at the top for a repository that learns continuously (`CIOS-01` P.1).

### 3.1 The function

The wave sequence is defined by a **successor function**, never by an enumerated set (`CIOS-L-24`):

| Element | Definition |
|---|---|
| Initial segment | `W1 … W5` **exactly as `IMG-001` `04` declares them**, including the W0-A assimilation pre-wave. Not altered, not renumbered, not reinterpreted. |
| Successor rule | `next(W_k) = W_{k+1}`, admissible for all `k ∈ ℕ` |
| Membership rule for `W_k`, `k > 5` | an admitted item whose dependency closure is satisfied by `W_1 … W_{k-1}` and which is not a member of any `W_j`, `j < k` |
| Gating rule | unchanged from `IMG-001` `04`: `W_k` opens when `W_{k-1}` is complete. CIOS adds no gate and removes none. |
| Terminal wave | **none exists.** There is no `k` after which no successor is admissible (`CIOS-L-01`). |

### 3.2 Why this is additive, not a replacement

| Test | Result |
|---|---|
| Are `W1 … W5` altered? | **NO** — reproduced by reference; counts (20·15·32·11·12) and the 77 effective implementable are the located figures |
| Is the located layer-gate altered? | **NO** — `IMG-001` `04`'s gating is the successor function's gating rule |
| Is a second wave partition created? | **NO** — one sequence, whose first five members are the located five |
| What is added? | only the statement that `k` is unbounded and that `next` is always defined |

`IMG-001` `04` remains the sole authority on the wave partition (`CIOS-01` VII.2). CIOS states only that the sequence does not terminate — which `IMG-001` does not assert either way, because a finite plan has no need to.

### 3.3 Unbounded sequences

Every sequence in the CIOS model is defined by a successor function. Recorded so no hidden finite assumption survives (`AC-6`; `04-HIDDEN-FINITE-ASSUMPTION-CERTIFICATION.md`):

| Sequence | Domain | Successor | Enumerated anywhere? |
|---|---|---|---|
| Plan epochs `PLAN[n]` | `n ∈ ℕ` | `n := n+1` (`CIOS-01` VI.4) | **no** |
| Waves `W_k` | `k ∈ ℕ` | §3.1 | **no** (first five located; sequence open) |
| Submissions | unbounded | arrival | **no** |
| Queue members | unbounded | `CIOS-09` §4.1 | **no** |
| Dependencies per item | unbounded | declared set | **no** |
| Planning cycles | unbounded | one per epoch | **no** |
| Findings | unbounded | emission | **no** |

Fixed cardinalities in CIOS — 4 planes, 4 partitions, 24 laws, 12 invariants, 24 engines, 48 ports, 24 stages, 22 identity fields, 4 queues, 8 key elements — are **structural** counts of CIOS's own declaration, set by `CIOS-01`. They bound no work set, no capacity and no domain, so they are not hidden finite assumptions.

---

## 4. THE QUIESCENT ADOPTION POINT

| Property | Value |
|---|---|
| Definition | the batch-cut boundary of the located scheduler (`CIOS-01` VI.2; `IEC-001` `05`) |
| Owner of the boundary | **`IEC-001` `05`** — CIOS reads it, does not define it |
| Consumed at | `CIOS-P-27` (`E-14` inbound) |
| Atomicity | adoption is atomic; **no partial epoch exists** (`E-14` FAIL) |
| Applies to | `CIOS-PT-03` **only** (`CIOS-01` VI.2) |
| Effect on in-flight items | **none** — they stay bound to `PLAN[n]` until terminal (`CIOS-INV-04`) |
| Effect on sealed items | **none** (`CIOS-INV-03`) |
| Lock taken | **none** |

**Why no lock is needed.** Adoption writes `CIOS-PT-03`, whose sole writer is `CIOS-PL-A` (`CIOS-02` §4.3). Execution reads `PLAN[n]`, which has **zero** writers. A single-writer target and a zero-writer source cannot contend, so `CIOS-01` VI.3's claim — *"no lock is ever taken on execution, and assimilation never waits for execution"* — follows from the write-scope partition rather than from a synchronisation protocol.

---

## 5. INDEPENDENT CLOCKS — `CIOS-L-04`

`CIOS-L-04` requires that the assimilation and execution planes advance on independent clocks, and that neither clock's rate, backlog or failure is an input to the other's ability to advance.

### 5.1 The clocks

| Clock | Plane | Advances on | Rate | Bounded by |
|---|---|---|---|---|
| assimilation | `PL-A` | submission arrival | unbounded | nothing (`CIOS-L-24`) |
| execution | `PL-B` | located controller tick (`IEC-001` §4 loop) | located | `IEC-001` |
| truth | `PL-C` | terminal-state events | derived from execution | nothing |
| observation | `PL-D` | freely; **may lag arbitrarily** | unbounded | nothing |

### 5.2 Independence proof

| Step | Claim | Ground |
|---|---|---|
| 1 | Independence fails only if one clock's state is an **input** to another's advance condition. | definition, `CIOS-L-04` |
| 2 | Such an input requires an edge from the observed plane to the advancing plane. | `CIOS-06` §1 |
| 3 | There is **no edge** from `PL-B`, `PL-C` or `PL-D` into `PL-A`. | `CIOS-06` §5.1 — the absent back-edge |
| 4 | ∴ no execution, truth or observation state can be an input to assimilation's advance. | 2, 3 |
| 5 | Execution's advance condition is the located tick over `PLAN[n]`, which is complete and immutable before execution reads it. | `CIOS-01` VI.1, VI.3 |
| 6 | ∴ assimilation's rate, backlog and failure cannot be inputs to execution's advance. | 5 |
| 7 | `PL-D` writes nothing and has out-degree 0. | `WS-6`; `CIOS-06` §4.2 |
| 8 | ∴ observation's clock is an input to nothing. | 7 |
| 9 | **∴ the clocks are independent. `CIOS-L-04` holds.** | 4, 6, 8 |

### 5.3 Consequences

| Consequence | Ground |
|---|---|
| Assimilation may outrun execution without bound; the surplus accumulates lawfully in `CIOS-Q-03`. | §5.2; `CIOS-09` §4.1 |
| Execution may outrun assimilation; the Ready Queue empties and the service is **idle, never finished**. | `CIOS-L-01` |
| A stalled assimilation plane does not stall execution — `PLAN[n]` remains active. | `CIOS-02` §6 DEGRADED-FUTURE |
| A stalled execution plane does not stall assimilation — admission continues into `CIOS-PT-03`. | `CIOS-02` §6 DEGRADED-PRESENT |
| A blind observation plane affects nothing. | §5.2 step 8 |
| No backpressure signal exists in either direction. | a back-edge is prohibited (`CIOS-06` §5.1) |

---

## 6. WHAT THIS ARTIFACT DOES NOT DO

| Not done | Located owner |
|---|---|
| Set batch size, tick rate or dispatch timing | `IEC-001` `05`, §4 loop |
| Define the batch-cut boundary | `IEC-001` `05` |
| Alter the located queue order | `IEC-001` `04` — preserved exactly (§2.3) |
| Alter the wave partition W1–W5 | `IMG-001` `04` — preserved exactly (§3.2) |
| Alter the critical path or readiness matrix | `IMG-001` `07`, `08` |
| Evaluate the READY predicates | `IEC-001` `03` P1–P7 |
| Mint the witnessed ordinal used as `CIOS-K-08` | `AIF-L04` |
| Enumerate any domain, technology, platform or format in a key element | prohibited by `CIOS-L-22` |

---

## AUTHORITY BOUNDARY (MANDATORY)

This artifact declares a priority key vector, a wave successor function and a clock model. It owns no scheduler, no queue, no gate, no registry, no identifier space and no concern. The located order and the located wave partition are preserved exactly and remain governed by `IEC-001` and `IMG-001`. Where this artifact and a located canonical instrument disagree, **the located instrument governs and this artifact SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `CIOS-10` · PROVISIONAL · ADDITIVE · COMPOSITION-ONLY · AUTHORITY-NEUTRAL**
