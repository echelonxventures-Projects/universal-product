# IMR-0000/09 — DEPENDENCY GRAPH ARCHITECTURE

| Field | Value |
|---|---|
| MISSION | `IMR-0000` — CIOS Platform Foundation |
| ARTIFACT | `09` — Dependency Graph Architecture (**deliverable 19**) · directive capability 12 |
| ARTIFACT KIND | Architecture (`CMG-K-05`) — binding declaration + scope map |
| SUBSYSTEM | `SS-08` `CIOS-DAG` (engine `E-08`, ports `P-15`/`P-16`, both internal) |
| CENTRAL CLAIM | **One graph, one store, one edge vocabulary.** The platform declares five *scopes* over that one graph and creates no second graph, no second store and no edge instance. |
| AUTHORITY OF ITS OWN | **NONE.** |
| CONFLICT RULE | Located instrument governs (`REG-AUTO-001` for the store, `GOV-INT-001` §2.6 for the single-graph rule, `engine/graph` for evaluation, `IMG-001` for the backlog graph); then `IMR-003A` (`CIOS-06`); then this artifact. |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. THE SINGLE-GRAPH RULE

| ID | Rule | Located basis |
|---|---|---|
| `DG-1` | **One graph.** All dependency, traceability, impact and relationship facts live in `relationships.json` with one edge vocabulary. A parallel graph is prohibited. | `GOV-INT-001` §2.6 (*"never a parallel graph"*), §6.1; `UCI-OPT-001` row 5 |
| `DG-2` | **One dependency field.** Artifact-level dependencies are `artifacts.json[*].dependencies` (`GOV-INT-001` §6.2 register 6). No second dependency store exists. | `REG-AUTO-001` |
| `DG-3` | **Impact is derived, never stored.** Impact is computed by traversal from the changed object along `Depends-On`, `Uses`, `References`, `Implements`, `Tests`, `Deploys`, `Parent`, `Child`. It is never persisted as fact. | `UCI-001` Part XII, `IL-11`, `IP-3` |
| `DG-4` | **Bidirectional traversability.** Every edge is traversable in both directions by its located inverse. **No orphan node exists.** | `UCI-001` `CL-08`; `UUP-05` |
| `DG-5` | **Acyclicity, fail-closed.** A **reported** cycle is a non-admission **regardless of the validator's returned validity flag**. | `CIOS-INV-05`; `CIOS-04` `E-08`; the `UCCEP-F-003` bound |
| `DG-6` | **New edge types, never a new graph.** A dependency relation the vocabulary lacks is admitted as a new **edge type** by the vocabulary's owner — never as a new store. | `UCI-OPT-001` OUTPUT 4; `PG-05` |

---

## 2. THE FIVE DEPENDENCY SCOPES

Five distinct dependency questions exist in this corpus. Each has one owner. Conflating them is what would produce a second graph.

| Scope | Question | Located owner | Store / expression |
|---|---|---|---|
| **S-1 · Artifact** | what does this artifact depend on? | `REG-AUTO-001` | `artifacts.json[*].dependencies` + `relationships.json` `Depends-On` |
| **S-2 · Backlog** | in what order can the implementation backlog be built? | `IMG-001` `03` (graph), `05` (topological order), `07` (critical path) | `IMG-001` artifacts; 77 effective implementable |
| **S-3 · Engine** | which CIOS engine derives from which? | `IMR-003A/06` | 25 `DERIVES` edges + 63 `OBSERVES` edges; acyclicity proven in-artifact |
| **S-4 · Corpus binding** | which located instrument does a CIOS artifact depend on? | `IMR-003A-R1/05` | 35 located binding paths; `→R`/`→A`/`→H`/`→F`; **no `→W` exists** |
| **S-5 · Register** | which register derives from which? | `IMR-0000/07` §6 | `RR-1 … RR-6` **types only**; 0 instances created |

### 2.1 Scope separation, proven

| Pair | Apparent overlap | Boundary |
|---|---|---|
| S-1 / S-2 | both order work | S-1 is a **fact about an artifact**; S-2 is a **plan over a backlog**. `IMG-001` remains the sole authority on backlog order (`CIOS-01` VII.2) |
| S-1 / S-3 | both are dependency graphs | S-1 is over corpus artifacts; S-3 is over **programme-scoped declaration slots** (`CIOS-E-*`), which are not corpus objects (`RC-04` §4) |
| S-3 / S-4 | both concern CIOS | S-3 is engine→engine (internal); S-4 is CIOS artifact→located instrument (external). `IMR-003A-R1/05` §2 states the split explicitly to avoid restating S-3 |
| S-4 / S-5 | both are external bindings | S-4 binds **instruments**; S-5 relates **registers**. Distinct object kinds |
| S-2 / S-5 | both are derivation orders | S-2 orders **work**; S-5 orders **regeneration** (`RR-6`) |

**The platform's contribution is S-5 alone**, and only as types. S-1 through S-4 are bound read-only and restated nowhere.

---

## 3. WHAT `SS-08` DOES AT ADMISSION

| Determination | Stage | Gate | On failure |
|---|---|---|---|
| every declared dependency resolves | `CIOS-S-13` | `G-08` Dependency Gate | non-admission |
| admission introduces no cycle | `CIOS-S-14` | `G-08` + `CK-GRAPH` | non-admission on a **reported** cycle, regardless of the returned flag |
| partial-order position emitted | `P-16` | — | consumed by `SS-06` as `CIOS-K-04` dependency depth |

`SS-08` does **not**: own the graph, write an edge, define the vocabulary, compute impact, order the backlog, or evaluate READY predicates.

---

## 4. ACYCLICITY — WHAT IS PROVEN AND WHAT IS NOT

Stated precisely, because the difference determines what a future programme may rely on.

| Claim | Status | Basis |
|---|---|---|
| The CIOS engine graph (S-3) is acyclic | **PROVEN in-artifact**, both graph scopes; 0 cycles; 0 back-edges into `PL-A` | `CIOS-06` §4; `IMR-003A-R1` `V-27`, `V-28`, `V-56` |
| The 35 located bindings (S-4) are acyclic and one-directional | **PROVEN**; 0 dangling, 0 cyclic, 0 mutating; **no located instrument depends on CIOS** | `IMR-003A-R1/05` §5, §6 |
| The register graph (S-5) is acyclic | **DECLARED** — `RR-1`/`RR-2` run store→view, `RR-6` runs source→regenerated, never back | `07` §6.3 |
| The subsystem layer introduces no edge | **DECLARED** — all consumption follows existing `CIOS-06` `DERIVES` edges | `SR-7`; `02` §4.4 |
| `CIOS-INV-05` is **machine-enforced corpus-wide** | **NOT ACHIEVED** | `UCCEP-F-003` — the located validator **fails open** on a reported cycle |

**The consequence of the last row is the operative one.** Because the located validator fails open, `E-08`'s rule is written to fail closed on the *report* rather than on the *verdict* (`DG-5`). That is a defensive binding, not a discharge: `CIOS-G-04` remains **OPEN**, owned by the owner of `engine/graph` / `CK-GRAPH`, and neither `IMR-003A` nor `IMR-0000` discharges it (`CIOS-GAP-04`).

---

## 5. PROPERTIES

| Property | Value |
|---|---|
| Dependency scopes declared | **5** |
| Scopes owned by the platform | **1** (S-5, types only) |
| Graphs created | **0** |
| Stores created | **0** |
| Edge **types** declared | **6** (`RR-1 … RR-6`), proposed for the located vocabulary's owner (`PG-05`) |
| Edge **instances** created | **0** |
| Edge vocabulary created | **0** |
| Located bindings that resolve | **35 / 35**; dangling **0** |
| Cycles in any scope the platform declares | **0** |
| Impact computations persisted as fact | **0** (`DG-3`; `IP-3`) |
| Inherited undischarged gate | **1** — `CIOS-G-04` (`UCCEP-F-003`) |

---

## 6. WHAT THIS ARTIFACT DOES NOT DO

| Not done | Located owner |
|---|---|
| Create a graph, a store, an edge instance or an edge vocabulary | `REG-AUTO-001`; `UKB-ADV-000`; `PG-05` |
| Add or remove any object's dependency | `REG-AUTO-001`; the object's owner |
| Evaluate acyclicity or compute impact | `engine/graph`; `CK-GRAPH`; `UCI-001` Part XII |
| Alter the backlog graph, topological order, critical path or wave partition | `IMG-001` `03`–`09` |
| Restate `CIOS-06`'s 25 `DERIVES` edges or `IMR-003A-R1/05`'s 35 bindings | bound by pointer; `CIOS-L-08` |
| Discharge `UCCEP-F-003` / `CIOS-G-04` | owner of `engine/graph` |

---

## AUTHORITY BOUNDARY (MANDATORY)

This artifact declares dependency **scopes** over one located graph. It creates no graph, no store, no edge instance and no edge vocabulary; it evaluates nothing and computes no impact. Acyclicity is proven only where stated, and corpus-wide machine enforcement of `CIOS-INV-05` is expressly **not** claimed — that remains an inherited, owner-held, undischarged gate. Every owner named is located in an instrument existing independently at `b26c5bb`. Where this artifact and a located canonical instrument disagree, **the located instrument governs and this artifact SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `IMR-0000/09` · PROVISIONAL · ADDITIVE · DESIGN-ONLY · AUTHORITY-NEUTRAL**
