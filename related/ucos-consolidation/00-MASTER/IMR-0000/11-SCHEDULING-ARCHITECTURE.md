# IMR-0000/11 — SCHEDULING ARCHITECTURE

| Field | Value |
|---|---|
| MISSION | `IMR-0000` — CIOS Platform Foundation |
| ARTIFACT | `11` — Scheduling Architecture (**deliverable 21**) · directive capability 13 |
| ARTIFACT KIND | Architecture (`CMG-K-05`) — binding declaration + composition view |
| SUBSYSTEM | `SS-06` `CIOS-SCHED` (engines `E-12` priority derivation, `E-14` quiescent adoption; ports `P-23`/`P-24`, `P-27`/`P-28`, all internal) |
| CENTRAL CLAIM | **The platform owns an order, not a scheduler.** Batch size, tick rate, dispatch timing and the batch-cut boundary are `IEC-001`'s. The located order `wave, family, id` survives **byte-identical** as an initial segment of the platform's order. |
| AUTHORITY OF ITS OWN | **NONE.** |
| CONFLICT RULE | Located instrument governs (`IEC-001` for the scheduler, `IMG-001` for order inputs, `AIF-L04` for the ordinal); then `IMR-003A` (`CIOS-10`); then this artifact. |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. WHAT THE PLATFORM SCHEDULES, AND WHAT IT DOES NOT

| Concern | Owner | Platform role |
|---|---|---|
| the total order over the OPEN partition | `CIOS-10` §2 key vector (Art VII.3 r6) | **derive** (`E-12`) |
| when the staged epoch takes effect | `CIOS-01` VI.2 | **adopt** at the located boundary (`E-14`) |
| the batch-cut boundary itself | **`IEC-001` `05`** | read the signal at `P-27` |
| batch size, tick rate, dispatch timing | **`IEC-001` `05`, §4 loop** | none |
| queue order downstream of handoff | **`IEC-001` `04`** | none — never reordered |
| READY evaluation | **`IEC-001` `03` P1–P7** | none — never re-evaluated |
| dispatch | **`IEC-001` C7 (EC-3 lane)** | none |

**Two rows are the platform's.** The word *scheduler* is deliberately withheld from this architecture: there is one scheduler and it is located.

---

## 2. THE PRIORITY KEY VECTOR — BOUND BY POINTER

`CIOS-10` §2 owns the eight-element vector `CIOS-K-01 … CIOS-K-08`. It is **not restated here** (`CIOS-L-08`). What this artifact records is the platform-level consequence of its two structural locks.

| Lock | Ranks | Why it is locked | Consequence for a future programme |
|---|---|---|---|
| **Located-order preservation** | 1–3 (`wave`, `family`, `located id`) | For two items both bearing a located `id`, the comparison resolves at rank ≤ 3, so ranks 4–8 are never consulted. The relative order of the located 77 is therefore **byte-identical** to `IEC-001` `04`. | A programme may **not** reorder the located backlog by adding a key element. New submissions **append**; they never interleave. |
| **Totality** | 8 (witnessed admission ordinal) | The ordinal is unique within its minting authority (`AIF-L07`), so the comparison always resolves by rank 8 at the latest. This is what makes `CIOS-INV-09` (total order) satisfiable. | A programme may **not** displace rank 8, and may **not** substitute a timestamp — two admissions can share a timestamp, which breaks totality. |
| **Free band** | 4–7 | dependency depth, critical-path membership, blocking degree, change-class rank | Extensible **by data change** to `cios-bindings.json` by its owner; amends no law and alters no engine. |

| ID | Rule | Located basis |
|---|---|---|
| `SA-1` | The located order is an **initial segment** of the platform order, never a competing order. | `CIOS-10` §2.3; `CIOS-01` I.3 |
| `SA-2` | The order is **total**. An unresolved tie is a `CIOS-INV-09` breach and is inadmissible, not a warning. | `CIOS-INV-09`; `CIOS-10` §2.4 |
| `SA-3` | Ordering authority is the **witnessed admission ordinal**. Timestamps are admissible as evidence and are never used as order. | `CIOS-L-15`; `AIF-L04`; `UUP-09` |
| `SA-4` | Ranks, weights, directions and class ranks are **declared data**. Adding a discriminator in the free band is a data change. | `CIOS-L-23` |
| `SA-5` | Adoption is atomic at the located boundary; **no partial epoch exists**. | `CIOS-01` VI.2; `E-14` |
| `SA-6` | No sequence in the scheduling model assumes a finite bound — waves, epochs, queues, submissions and planning cycles are each defined by a successor function. | `CIOS-L-24`; `CIOS-10` §3.3 |

---

## 3. INDEPENDENT CLOCKS

The platform runs four clocks. None is an input to another.

| Clock | Plane | Advances on | Bounded by |
|---|---|---|---|
| assimilation | `PL-A` | submission arrival | nothing (`CIOS-L-24`) |
| execution | `PL-B` | the located controller tick (`IEC-001` §4 loop) | `IEC-001` |
| truth | `PL-C` | terminal-state events | nothing |
| observation | `PL-D` | freely; **may lag arbitrarily** | nothing |

**Independence rests on one structural fact:** there is no edge from `PL-B`, `PL-C` or `PL-D` into `PL-A` (`CIOS-06` §5.1 — the absent back-edge), and `SR-7` forbids the subsystem layer from adding one. `CIOS-10` §5.2 carries the nine-step proof; it is bound here, not restated.

| Consequence | Basis |
|---|---|
| Assimilation may outrun execution without bound; the surplus accumulates lawfully in `CIOS-Q-03`. | `CIOS-09` §4.1 |
| Execution may outrun assimilation; the Ready Queue empties and the service is **idle, never finished**. | `CIOS-L-01` |
| A stalled plane degrades only its own concern (DEGRADED-FUTURE / DEGRADED-PRESENT). | `CIOS-02` §6 |
| No backpressure signal exists in either direction. | a back-edge is prohibited |

---

## 4. THE QUEUE BOUNDARY

The single most important interface fact in the scheduling architecture, because misreading it would create a second queue.

```
CIOS-Q-01 … CIOS-Q-04          ── platform-side, upstream of execution
        │
        │  CIOS-P-30  (public egress, SS-07 · E-15)
        ▼
╔═══════════════════════════════════════════════════════════╗
║  LOCATED Execution Queue — IEC-001 04 · C5 · C7           ║
║  the platform relinquishes ALL control at this line        ║
╚═══════════════════════════════════════════════════════════╝
```

| Property | Value | Basis |
|---|---|---|
| Platform queues | **4** (`CIOS-Q-01 … Q-04`), all strictly upstream | `CIOS-09`; Art VII.3 r1 |
| Located queues reordered | **0** | `RC-11` prohibition |
| Control retained after handoff | **none** | `E-15` `P-30` |
| Items forced into the located queue | **0** — if the queue does not accept, the item stays in `CIOS-Q-04` | `E-15` FAIL mode |
| Queue overlap with `IEC-001` `04` | **0** — `CIOS-19` §3 row 1 resolves this as **disjoint**, not deferred | `CIOS-09` §1 |

---

## 5. PROPERTIES

| Property | Value |
|---|---|
| Schedulers owned | **0** |
| Key elements defined by this artifact | **0** — the vector is `CIOS-10`'s |
| Located order altered | **0** — preserved byte-identical (`SA-1`) |
| Locked ranks | **4** (1, 2, 3, 8) |
| Extensible ranks | **4** (4–7), by data change only |
| Timestamps used as ordering authority | **0** |
| Locks or backpressure signals | **0** |
| Partial epochs possible | **0** |
| Finite bounds assumed | **0** (`SA-6`) |

---

## 6. WHAT THIS ARTIFACT DOES NOT DO

| Not done | Located owner |
|---|---|
| Set batch size, tick rate or dispatch timing | `IEC-001` `05`, §4 loop |
| Define the batch-cut boundary | `IEC-001` `05` |
| Reorder the located queue, or re-evaluate READY | `IEC-001` `04`, `03` |
| Dispatch, or authorize dispatch | `IEC-001` C7 (EC-3 lane); `CMG` T4 |
| Restate the key vector, the wave successor function or the clock proof | `CIOS-10` — bound by pointer; `CIOS-L-08` |
| Mint the witnessed ordinal used as the terminating key | `AIF-L04` |
| Create a queue downstream of `CIOS-P-30` | `CIOS-L-09`; the located queue exists |

---

## AUTHORITY BOUNDARY (MANDATORY)

This artifact declares an ordering and adoption discipline upstream of a scheduler it does not own. It sets no batch size, tick rate or dispatch timing; it defines no boundary; it reorders no located queue; it dispatches nothing and authorizes no dispatch. The located order and the located wave partition are preserved exactly and remain governed by `IEC-001` and `IMG-001`. Every authority named is located in an instrument existing independently at `b26c5bb`. Where this artifact and a located canonical instrument disagree, **the located instrument governs and this artifact SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `IMR-0000/11` · PROVISIONAL · ADDITIVE · DESIGN-ONLY · AUTHORITY-NEUTRAL**
