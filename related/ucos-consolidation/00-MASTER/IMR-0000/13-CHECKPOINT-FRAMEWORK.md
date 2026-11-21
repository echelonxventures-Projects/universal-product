# IMR-0000/13 — CHECKPOINT FRAMEWORK

| Field | Value |
|---|---|
| MISSION | `IMR-0000` — CIOS Platform Foundation |
| ARTIFACT | `13` — Checkpoint Framework (**deliverable 23**) · directive capability 15 |
| ARTIFACT KIND | Framework (`CMG-K-05`) — binding declaration |
| SUBSYSTEM | `SS-11` `CIOS-RCV` — **BINDING-ONLY** (zero engines, zero ports) |
| CENTRAL CLAIM | **One checkpoint store exists and the platform does not own it.** `MCP-007` §03 owns the checkpoint form; `00-MASTER/CHECKPOINTS/` is the append-only store. The platform declares two *classes* of checkpoint and binds both. |
| AUTHORITY OF ITS OWN | **NONE.** `MCP-007`'s own authority is `NONE — DERIVED TRUTH`; the platform's binding to it confers less, not more. |
| CONFLICT RULE | Located instrument governs (`MCS-000`, then `MCP-007`, then `MCP-002`); then `IMR-003A` (`CIOS-01` Art VI for the adoption point); then this artifact. |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. THE TWO CHECKPOINT CLASSES

The corpus contains two distinct things called *checkpoint*. They are not variants of one mechanism; they answer different questions and have different owners. Conflating them would create a second store.

| Class | Question | Owner | Store | Cardinality at `b26c5bb` |
|---|---|---|---|---|
| **CP-S · Session checkpoint** | how does the next session resume without rediscovering context? | `MCP-007` §03 | `00-MASTER/CHECKPOINTS/CKPT-<UTC>-<HEAD>.md`, **append-only** | **32 records** |
| **CP-A · Adoption point** | at what instant may a staged plan become active? | `CIOS-01` VI.2 | none — it is a **boundary signal**, not a record | not a stored object |

| ID | Rule | Located basis |
|---|---|---|
| `CF-1` | **CP-S is a record; CP-A is an instant.** A CP-A is never persisted as a checkpoint record, and a CP-S never authorizes a plan adoption. | `MCP-007` §03; `CIOS-01` VI.2 |
| `CF-2` | **One checkpoint store.** `00-MASTER/CHECKPOINTS/` is append-only and is the only store. No second store, no rollback registry, no snapshot directory. | `MCP-007`; `GOV-INT-001` §6.1; `UCI-OPT-001` (*net-new persistent structures: ZERO*) |
| `CF-3` | **A checkpoint authors no state.** `MCP-002` owns state; a checkpoint records what was true at a point, and asserts nothing. | `MCP-007` scope statement |
| `CF-4` | **Checkpoints are append-only and forward-only.** A checkpoint is never edited, deleted or superseded in place; a correction is a new checkpoint. | `AIF-L08`, `AIF-L17`; `LR-5` |
| `CF-5` | **One checkpoint per logical capability.** A session that completes a capability writes exactly one CP-S and one commit referencing its governing determination. | `MCS-000` §05/§06; `MCP-007` §01 steps 11–12 |
| `CF-6` | **A checkpoint is evidence, never authority.** It confers no right, discharges no gate and authorizes no continuation on its own. | `MCP-007` AUTHORITY = `NONE — DERIVED TRUTH`; `PR-6` |

---

## 2. WHAT A CP-S RECORDS

Bound from `MCP-007` §03 and from the 32 located records. **Not restated as a new schema** — this is the observed field set, cited so a future programme writes a conformant record rather than inventing one.

| Field class | Content observed in located records |
|---|---|
| session outcome | completion state; boot reconciliation performed |
| repository position | branch; HEAD (base); working-tree disposition; synchronization state |
| work identity | capability worked; governing determination; constitutional anchor |
| lifecycle | state before → after, across `LX-1` and `LX-4` |
| assurance | certification record + ledger sequence; evidence bundle path + content hash |
| artifacts | files committed, enumerated |
| validation | lint, test, coverage, determinism, write-scope results |
| reuse | what was reused rather than redefined |
| continuation | next authorized capability; resume hints; explicit statement of what is **not** complete |

**The last row is the one that makes the store useful.** Every located checkpoint states plainly what remains incomplete (e.g. *"Band 11 IN PROGRESS (~16%) … NOT COMPLETE"*). A checkpoint that recorded only success would defeat its own purpose, because resumption depends on knowing the boundary of what was done.

---

## 3. THE SESSION CONTINUATION CONTRACT

`MCP-007` §01 owns a thirteen-step contract. Bound by pointer; the platform adds no step. What this framework records is which platform subsystem each step touches, so a future programme knows where its obligations sit.

| `MCP-007` §01 step class | Platform binding |
|---|---|
| load context and state (`MCP-001`, `MCP-002`) | `SS-11` |
| verify branch, HEAD, working tree, synchronization | `SS-11`; observed at `b26c5bb` / `programme/evo-usis-005` |
| verify current execution state | `SS-11` + `SS-12` (observation) |
| load the execution ticket (next authorized capability, `MCP-003`) | `SS-03` (programme scope) + `SS-11` |
| continue **only** the authorized capability | `MCS-000` §05/§06 — one logical capability per session |
| update state, transitions, metrics, edges, decisions | `SS-13` (truth, traceability), `SS-14` (decisions) |
| checkpoint | `SS-11` — `CF-5` |
| commit, referencing the governing determination | located; outside the platform's write scope |

| ID | Rule | Located basis |
|---|---|---|
| `CF-7` | The platform adds **no step** to the continuation contract and removes none. | `MCP-007` §01; `CIOS-L-08` |
| `CF-8` | Boot reconciliation is `MCP-007` §04.B's; a divergence between recorded and actual repository position is reconciled by **updating the record forward**, never by rewriting history. | `MCP-007` §04.B; `AIF-L17` |

---

## 4. THE ADOPTION POINT (CP-A)

| Property | Value | Basis |
|---|---|---|
| Definition | the batch-cut boundary of the located scheduler | `CIOS-01` VI.2; `IEC-001` `05` |
| Owner of the boundary | **`IEC-001` `05`** — the platform reads the signal, never defines it | `CIOS-10` §4 |
| Consumed at | `CIOS-P-27` (`E-14` inbound, `SS-06`) | `CIOS-05` |
| Atomicity | adoption is atomic; **no partial epoch exists** | `E-14` FAIL mode |
| Applies to | `CIOS-PT-03` only | `CIOS-01` VI.2 |
| Effect on in-flight work | **none** — items stay bound to their epoch | `CIOS-INV-04` |
| Effect on sealed work | **none** | `CIOS-INV-03` |
| Lock taken | **none** | `10` §2.1 |
| Persisted as a record | **no** | `CF-1` |

---

## 5. PROPERTIES

| Property | Value |
|---|---|
| Checkpoint classes declared | **2** (CP-S, CP-A) |
| Checkpoint stores created | **0** |
| Checkpoint records written by this mission | **0** |
| Checkpoint schemas or formats defined | **0** — the located field set is cited, not re-specified |
| Steps added to the continuation contract | **0** |
| Snapshot, rollback or restore mechanisms defined | **0** — `SS-11` is BINDING-ONLY |
| Located records observed | **32** |
| Public ports on `SS-11` | **0** — programmes bind `MCP-007` **directly** (`IFL-08`) |
| Inherited bound | **`GG-3` / `CIOS-GAP-12`** — change-intelligence registers 8–11 (`changes`/`knowledge`/`regeneration`/`rollback.json`) are **absent**, so register-backed rollback capability is unavailable. Owner: `UCI-001`, `WP-GDR-001`. Undischarged. |
| Inherited bound | **`GG-4`** — the registration anchor lacks off-machine existence, so checkpoint claims are witnessed only in the working tree. Owner: repository operator, `WP-GDR-002`. Undischarged. |

---

## 6. WHAT THIS FRAMEWORK DOES NOT DO

| Not done | Located owner |
|---|---|
| Write, edit or delete a checkpoint | `MCP-007`; the session that authors it |
| Create a checkpoint store, snapshot store or rollback registry | `MCP-007`; `UCI-001`; `GG-3` |
| Define a checkpoint schema, format or identifier scheme | `MCP-007` §03 convention |
| Author or update state | `MCP-002` |
| Define the adoption boundary | `IEC-001` `05` |
| Restore, resume or reconcile a repository | `MCP-007` §04.B; `UCOS-RECON-001` |
| Confer continuation authority on a checkpoint | `CF-6` — a checkpoint is evidence, never authority |
| Discharge `GG-3` or `GG-4` | `UCI-001`; repository operator |

---

## AUTHORITY BOUNDARY (MANDATORY)

This framework binds two checkpoint classes to located owners. **It creates no store, writes no checkpoint, defines no schema, authors no state and restores nothing.** `SS-11` holds no engine, no port and write scope ∅. A checkpoint is evidence and confers no authority. Every owner named is located in an instrument existing independently at `b26c5bb`. Where this framework and a located canonical instrument disagree, **the located instrument governs and this framework SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `IMR-0000/13` · PROVISIONAL · ADDITIVE · DESIGN-ONLY · AUTHORITY-NEUTRAL**
