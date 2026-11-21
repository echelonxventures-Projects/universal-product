# IMR-0000/10 — PLANNING ARCHITECTURE

| Field | Value |
|---|---|
| MISSION | `IMR-0000` — CIOS Platform Foundation |
| ARTIFACT | `10` — Planning Architecture (**deliverable 20**) · directive capability 11 |
| ARTIFACT KIND | Architecture (`CMG-K-05`) — binding declaration + composition view |
| SUBSYSTEM | `SS-05` `CIOS-PLAN` (engines `E-11` plan epoch composition, `E-13` realignment; ports `P-21`/`P-22`, `P-25`/`P-26`, all internal) |
| CENTRAL CLAIM | **The platform owns the epoch, not the plan.** `IMG-001` remains the sole authority on backlog, waves, order and critical path. The platform's contribution is that planning is **versioned rather than mutated**, and that replanning can only reach the OPEN partition. |
| AUTHORITY OF ITS OWN | **NONE.** |
| CONFLICT RULE | Located instrument governs (`IMG-001` for the plan, `CEP-009` for evolution, `IEC-001` for the adoption boundary); then `IMR-003A` (`CIOS-01` Art VI, `CIOS-11`, `CIOS-12`); then this artifact. |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. THE PLANNING DIVISION OF AUTHORITY

| Planning question | Owner | Platform role |
|---|---|---|
| What work exists? | `IMG-001` `09` backlog | **read** |
| In what order can it be built? | `IMG-001` `05` topological order | **read** |
| What are the waves? | `IMG-001` `04` (W1–W5) | **read**; extended only by the successor function (`CIOS-10` §3) |
| What is the critical path? | `IMG-001` `07` | **read** |
| Which items are ready? | `IEC-001` `03` P1–P7 | **read**; never re-evaluated |
| **When does a new plan take effect?** | `CIOS-01` Art VI (epoch model) | **compose + adopt** (`SS-05`, `SS-06`) |
| **What may replanning touch?** | `CIOS-L-19` (future-only realignment) | **enforce by scope** |
| How does a plan change constitutionally? | `CEP-009` Art VI/XVI/XXIV | **route to** — the platform owns no evolution model |

**Two rows are the platform's.** Everything else is `IMG-001`'s, `IEC-001`'s or `CEP-009`'s and is bound read-only. `CIOS-01` Art VII.3 rows r4 and r8 are the only authorizations this artifact relies on.

---

## 2. THE EPOCH MODEL

| ID | Rule | Located basis |
|---|---|---|
| `PA-1` | **Plans are versioned, not mutated.** `PLAN[n]` is active; `PLAN[n+1]` is composed as a staged candidate. `PLAN[n]` is never written. | `CIOS-01` VI.1; `E-11` `P-22` |
| `PA-2` | **Adoption is atomic, at a located boundary.** `PLAN[n+1]` is adopted only at the Quiescent Adoption Point — the batch-cut boundary owned by `IEC-001` `05`. **No partial epoch exists.** | `CIOS-01` VI.2; `E-14` |
| `PA-3` | **Adoption applies to `PT-03` only.** In-flight items keep their bound epoch until terminal state; sealed items are untouched. | `CIOS-INV-04`, `CIOS-INV-03`; `E-16` |
| `PA-4` | **Realignment writes `PT-03` and nothing else.** A reach outside `PT-03` is a **full rejection, with no partial application**. | `CIOS-L-19`; `E-13` `P-26` |
| `PA-5` | **Epochs are unbounded.** `n ∈ ℕ`, defined by a successor function; there is no terminal epoch and no terminal wave. | `CIOS-L-24`; `CIOS-10` §3 |
| `PA-6` | **No lock is taken on execution, ever.** Assimilation never waits for execution, and execution never waits for assimilation. | `CIOS-01` VI.3; `CIOS-10` §4 |

### 2.1 Why no lock is needed

The claim is structural rather than protocol-based, which is why it holds without a synchronization mechanism:

| Step | Statement | Basis |
|---|---|---|
| 1 | Adoption writes `PT-03`. | `PA-3` |
| 2 | `PT-03` has exactly **one** writer: the assimilation plane. | `CIOS-02` §4.3; `WS-*` |
| 3 | Execution reads `PLAN[n]`, which has **zero** writers once active. | `PA-1` |
| 4 | A single-writer target and a zero-writer source cannot contend. | 2, 3 |
| 5 | ∴ no lock, no backpressure, no wait — in either direction. | `PA-6`; `CIOS-10` §5.3 |

**A back-edge would break this.** `CIOS-06` §5.1 records that no edge exists from the execution, truth or observation planes into assimilation, and `SR-7` forbids the subsystem layer from adding one. The absence is what makes the no-lock property true rather than merely intended.

---

## 3. PLANNING DEGRADATION

What happens when planning fails, stated so a future programme does not treat a planning failure as an execution blocker.

| Condition | Effect on future work | Effect on present work | Located basis |
|---|---|---|---|
| `E-11` cannot compose `PLAN[n+1]` | **DEGRADED-FUTURE** — `PLAN[n]` remains active | **none** | `CIOS-02` §6 |
| `E-13` attempts a reach outside `PT-03` | realignment **fully rejected**; no partial resequencing | **none** | `PA-4` |
| `E-14` cannot adopt at the boundary | no adoption; **no partial epoch** | **none** | `PA-2` |
| assimilation stalls entirely | future planning stalls | **none** — `PLAN[n]` continues to be executed | `CIOS-L-05` |
| execution stalls entirely | **none** — admission continues into `PT-03` | DEGRADED-PRESENT | `CIOS-02` §6 |

**This is the law of continuity in operational form** (`CIOS-01` P.3): neither plane can block the other, so a repository that learns continuously never has to stop implementing in order to replan.

---

## 4. THE WAVE SUCCESSOR FUNCTION — BOUND, NOT REDEFINED

| Element | Status |
|---|---|
| `W1 … W5` and the W0-A assimilation pre-wave | **`IMG-001` `04`'s, unchanged** — reproduced by reference; counts and gating untouched |
| Successor rule `next(W_k) = W_{k+1}`, `k ∈ ℕ` | `CIOS-10` §3.1 — a **declared function**, not an engine |
| Gating rule for `W_k` | unchanged from `IMG-001` `04`: `W_k` opens when `W_{k-1}` is complete |
| Terminal wave | **none exists** (`CIOS-L-01`) |
| Second wave partition created | **0** |

`CIOS-19` §3 row 5 records this as an **overlap resolved by deferral**: `IMG-001` remains the sole wave authority, and the platform states only that the sequence does not terminate. This artifact adds nothing to that and re-states none of it.

---

## 5. PROPERTIES

| Property | Value |
|---|---|
| Plans owned by the platform | **0** |
| Backlogs, waves, orders or critical paths defined | **0** |
| Epoch mechanics bound | `PLAN[n]` / `PLAN[n+1]` / Quiescent Adoption Point |
| Partitions writable by realignment | **1** (`PT-03`) |
| Locks taken on execution | **0** |
| Backpressure signals in either direction | **0** |
| Terminal epoch / terminal wave | **none** |
| Evolution models owned | **0** — `CEP-009` is the sole owner |
| Inherited bound | `UCCEP-F-001` — the located planning-closure gate has **no reachable PASS state**, so **no measured planning verdict is obtainable through it** (`CIOS-GAP-07`, owner: owner of `phase3_engine.py`) |

---

## 6. WHAT THIS ARTIFACT DOES NOT DO

| Not done | Located owner |
|---|---|
| Define the backlog, waves, topological order, critical path or readiness matrix | `IMG-001` `03`–`09` |
| Alter the located queue order or the wave partition | `IEC-001` `04`; `IMG-001` `04` — both preserved exactly |
| Evaluate READY predicates or form batches | `IEC-001` `03`, `05` |
| Define the batch-cut boundary, tick rate or dispatch timing | `IEC-001` `05`, §4 loop |
| Own an evolution model, or create an evolution registry entry | `CEP-009` Art VI/XVI/XXIV; `CIOS-01` VIII.1 |
| Reach `PT-02` or `PT-01` by any means | `CIOS-L-19`; prohibited absolutely |
| Claim a measured planning verdict | `UCCEP-F-001` — no reachable PASS state |

---

## AUTHORITY BOUNDARY (MANDATORY)

This artifact declares an epoch and realignment discipline over a plan it does not own. It defines no backlog, wave, order, critical path or readiness rule; it evaluates no predicate, forms no batch and dispatches nothing; it owns no evolution model and creates no evolution entry. Realignment reaches the OPEN partition only. Every authority named is located in an instrument existing independently at `b26c5bb`; `IMG-001` and `IEC-001` govern their own models where any reading differs. Where this artifact and a located canonical instrument disagree, **the located instrument governs and this artifact SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `IMR-0000/10` · PROVISIONAL · ADDITIVE · DESIGN-ONLY · AUTHORITY-NEUTRAL**
