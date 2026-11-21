# CIOS-06 — CONTINUOUS IMPLEMENTATION OPERATING SYSTEM · ENGINE DEPENDENCIES

| Field | Value |
|---|---|
| MISSION | `IMR-003A` — CIOS Constitution & Architecture |
| ARTIFACT | `CIOS-06` — Engine Dependencies (mission Output 6) |
| DELIVERED BY | `IMR-003A-R1` gap closure (Phase 4). **Additive**: no recovered artifact mutated. |
| ARTIFACT KIND | Architecture (`CMG-K-05`) |
| DISCHARGES | `CIOS-INV-05` — *the engine dependency graph is acyclic* |
| WHY PROVEN IN-ARTIFACT | `UCCEP-F-003`: the located graph validator reports a dependency cycle while returning `is_valid=true` and exit 0 — it **fails open**. Acyclicity therefore cannot be delegated to it and is proven here and machine-checked independently (`IMR-003A-R1/r1_verify.py`). |
| AUTHORITY OF ITS OWN | **NONE.** |
| CONFLICT RULE | `CIOS-01` governs over this artifact; a located canonical instrument governs over `CIOS-01`'s bindings. |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. EDGE SEMANTICS

Two edge types. Only `DERIVES` participates in the cycle test.

| Type | Meaning | Ordering constraint | In cycle test? |
|---|---|---|---|
| **`DERIVES`** | the source's output is a **required input** to the target within a single derivation pass | strict: source precedes target | **YES** |
| **`OBSERVES`** | the target reads the source's observable state, read-only, with no ordering requirement | none | NO — see §4.2 |

### 1.1 The single-pass scoping rule (essential)

The dependency graph is defined over **one assimilation pass**. This matters because two engines both touch `CIOS-PT-03`:

- `CIOS-E-12` (Priority Derivation) **reads** `CIOS-PT-03` and produces a total order.
- `CIOS-E-13` (Realignment) **writes** `CIOS-PT-03`.

Naively this looks circular. It is not, and the reason is the epoch model:

| Observation | Consequence |
|---|---|
| `E-12` is a pure function of `CIOS-PT-03` membership + the declared key vector. It does **not** consume `E-13`'s output within the same pass. | no edge `E-13 → E-12` |
| `E-13` consumes `E-12`'s order and applies it. | edge `E-12 → E-13` |
| `E-13`'s write to `CIOS-PT-03` is observed by the **next** pass, across a Quiescent Adoption Point. | the write is a *cross-epoch data flow*, not an intra-pass dependency |

`CIOS-01` Art VI (the epoch model) is what makes this sound: `PLAN[n]` is immutable and `PLAN[n+1]` is a separate staged object, so a write in pass *k* cannot alter an input already consumed in pass *k*. **Without the epoch model, this graph would be cyclic.** That is why `CIOS-01` Art IV.2 calls the separation constitutional rather than convenient.

---

## 2. THE `DERIVES` EDGE SET — 25 EDGES

| # | Edge | Reason |
|---|---|---|
| 1 | `E-01 → E-02` | context assimilation consumes the intake record |
| 2 | `E-02 → E-03` | recurrence runs only on a context-cleared submission |
| 3 | `E-03 → E-04` | home resolution consumes the recurrence verdict |
| 4 | `E-04 → E-05` | overlap resolution needs the resolved owner |
| 5 | `E-04 → E-06` | duplication detection needs the resolved home |
| 6 | `E-05 → E-06` | duplication detection needs the surviving owner |
| 7 | `E-04 → E-07` | identity composition binds the home to `CIOS-ID-11` |
| 8 | `E-06 → E-07` | identity is composed only after duplication is cleared |
| 9 | `E-07 → E-08` | dependency admission keys on the identity record |
| 10 | `E-08 → E-09` | impact assessment consumes the dependency position |
| 11 | `E-09 → E-10` | partition assignment requires all upstream verdicts |
| 12 | `E-10 → E-12` | priority derivation runs over `CIOS-PT-03` membership |
| 13 | `E-10 → E-13` | realignment is triggered by new admissions |
| 14 | `E-12 → E-13` | realignment applies the derived order |
| 15 | `E-12 → E-11` | epoch composition consumes the order |
| 16 | `E-13 → E-11` | epoch composition consumes the resequenced partition |
| 17 | `E-11 → E-14` | adoption consumes the staged candidate |
| 18 | `E-14 → E-15` | handoff draws from the adopted plan |
| 19 | `E-15 → E-16` | the dispatch window binds at handoff |
| 20 | `E-16 → E-17` | the guard protects an epoch-bound in-flight item |
| 21 | `E-17 → E-18` | override adjudication is reached only after default-deny |
| 22 | `E-16 → E-19` | seal transition consumes the terminal state of a bound item |
| 23 | `E-18 → E-19` | an admitted override may reach the seal path |
| 24 | `E-19 → E-20` | truth append consumes the seal record |
| 25 | `E-20 → E-21` | traceability emission follows the append |

**Edges: 25. Nodes: 24.**

### 2.1 Graph rendering

```
E-01 ─▶ E-02 ─▶ E-03 ─▶ E-04 ─┬─▶ E-05 ─▶ E-06 ─┐
                              │                  │
                              └──────────────────┴─▶ E-07 ─▶ E-08 ─▶ E-09 ─▶ E-10
                                                                                │
                              ┌─────────────────────────────────────────────────┤
                              ▼                                                 ▼
                            E-12 ───────────────────────────────────────────▶ E-13
                              │                                                 │
                              └────────────────────┬────────────────────────────┘
                                                   ▼
                                                 E-11 ─▶ E-14 ─▶ E-15 ─▶ E-16 ─┬─▶ E-17 ─▶ E-18 ─┐
                                                                               │                  │
                                                                               └──────────────────┴─▶ E-19 ─▶ E-20 ─▶ E-21

  OBSERVES (read-only sinks):  { E-01 … E-21 } ─▶ E-22, E-23, E-24
```

---

## 3. TOPOLOGICAL LAYERING

A valid topological order exists, which is a constructive proof of acyclicity.

| Layer | Engines | In-degree source |
|---|---|---|
| 0 | `E-01` | none — the sole source node (`CIOS-P-01` ingress) |
| 1 | `E-02` | `E-01` |
| 2 | `E-03` | `E-02` |
| 3 | `E-04` | `E-03` |
| 4 | `E-05` | `E-04` |
| 5 | `E-06` | `E-04`, `E-05` |
| 6 | `E-07` | `E-04`, `E-06` |
| 7 | `E-08` | `E-07` |
| 8 | `E-09` | `E-08` |
| 9 | `E-10` | `E-09` |
| 10 | `E-12` | `E-10` |
| 11 | `E-13` | `E-10`, `E-12` |
| 12 | `E-11` | `E-12`, `E-13` |
| 13 | `E-14` | `E-11` |
| 14 | `E-15` | `E-14` |
| 15 | `E-16` | `E-15` |
| 16 | `E-17` | `E-16` |
| 17 | `E-18` | `E-17` |
| 18 | `E-19` | `E-16`, `E-18` |
| 19 | `E-20` | `E-19` |
| 20 | `E-21` | `E-20` |
| 21 | `E-22`, `E-23`, `E-24` | `OBSERVES` only — sinks |

**Layers: 21 under the `DERIVES` scope** (the three observation engines carry no `DERIVES` edge and sit at layer 0 as isolated nodes); **22 under the combined scope**, where `OBSERVES` places them at layer 21. **Longest `DERIVES` path: 20 edges** (`E-01 → E-02 → E-03 → E-04 → E-05 → E-06 → E-07 → E-08 → E-09 → E-10 → E-12 → E-13 → E-11 → E-14 → E-15 → E-16 → E-17 → E-18 → E-19 → E-20 → E-21`). The layer numbers in the table above are the **combined-scope** numbering; see §6 for both.

Every edge in §2 runs strictly from a lower layer to a higher layer. Verify by inspection: edge 22 (`E-16 → E-19`) runs 15 → 18 ✓; edge 23 (`E-18 → E-19`) runs 17 → 18 ✓; edge 16 (`E-13 → E-11`) runs 11 → 12 ✓; edge 15 (`E-12 → E-11`) runs 10 → 12 ✓.

---

## 4. ACYCLICITY PROOF — `CIOS-INV-05`

### 4.1 Proof

| Step | Claim |
|---|---|
| 1 | A directed graph is acyclic **iff** a topological order over its nodes exists. |
| 2 | §3 exhibits an assignment of every one of the 24 nodes to a layer in `0 … 21`. |
| 3 | Every one of the 25 `DERIVES` edges runs from a strictly lower layer to a strictly higher layer (verified edge-by-edge, §3). |
| 4 | A cycle would require an edge from a higher layer to a lower or equal layer. |
| 5 | No such edge exists in the edge set. |
| 6 | **∴ the `DERIVES` graph is acyclic. `CIOS-INV-05` holds.** |

### 4.2 Why `OBSERVES` edges cannot create a cycle

`E-22`, `E-23`, `E-24` have **out-degree 0** in the combined graph: their only outbound ports (`P-44`, `P-46`, `P-48`) emit findings and write nothing (`WS-6`, `PR-5`). A node with out-degree 0 cannot lie on a cycle. The observation plane is therefore structurally incapable of introducing one — a direct consequence of giving it zero write authority.

### 4.3 Machine verification

Because `UCCEP-F-003` makes the located validator fail open, the proof above is checked by independent executable code rather than asserted: `00-MASTER/IMR-003A-R1/r1_verify.py` performs a Kahn topological sort over the edge set declared in `cios-bindings.json` and fails non-zero on any residual node. Its output is committed as evidence in `IMR-003A-R1/08-ARCHITECTURE-VERIFICATION-REPORT.md`.

**Disclosure retained:** this verifies **CIOS's own declared graph**, which is `UCCEP-000000`-style self-check discipline and is permitted by `AC-4`. It does **not** discharge `UCCEP-F-003`, which is owned elsewhere and remains open. `CIOS-INV-05` is *proven for CIOS's graph* and *not machine-enforced corpus-wide*.

---

## 5. CROSS-PLANE DEPENDENCY LEGALITY

Every edge crossing a plane boundary must respect the write scopes in `CIOS-02` §4, or the graph would be legal while the model was not.

| Edge | From plane | To plane | Legal? | Basis |
|---|---|---|---|---|
| `E-14 → E-15` | `PL-A` | `PL-B` | **YES** | the single one-way coupling at the Quiescent Adoption Point (`CIOS-01` VI.2). `PL-A` writes `PLAN[n+1]`; `PL-B` reads the adopted plan. No `PL-A` write reaches `CIOS-PT-02`. |
| `E-16 → E-19` | `PL-B` | `PL-C` | **YES** | `WS-3` — `PL-B` reaches Repository Truth **only** via `PL-C`. This edge is that route. |
| `E-18 → E-19` | `PL-B` | `PL-C` | **YES** | override-admitted seal path, `WS-8`; requires a `CIOS-OR-*` authority and a recorded protocol. |
| `E-01…E-21 → E-22/23/24` | all | `PL-D` | **YES** | read-only (`OBSERVES`); `PL-D` write scope is empty (`WS-6`). |
| any → `PL-A` from `PL-B`/`PL-C`/`PL-D` | — | `PL-A` | **NONE EXIST** | **no back-edge.** This is the structural basis of `CIOS-L-04` (Independent Clocks) — see §5.1. |

### 5.1 The absent back-edge

There is no edge from `CIOS-PL-B`, `CIOS-PL-C` or `CIOS-PL-D` into `CIOS-PL-A`. Consequences, each a law discharged structurally rather than by policy:

| Consequence | Law |
|---|---|
| Assimilation never waits on execution, truth or observation | `CIOS-L-04` Independent Clocks |
| Execution cannot signal assimilation to pause, slow or drain | `CIOS-L-02` Plane Separation |
| No plane can block another | `CIOS-01` Art IV.1 ("May block execution? — No" for `PL-A`, `PL-C`, `PL-D`) |
| An empty Ready Queue is idle, never finished | `CIOS-L-01` Perpetual Operation |

**A back-edge would silently reintroduce the finite-project assumption** that `CIOS-01` P.1–P.3 exists to remove: any signal from execution into assimilation is a mechanism by which execution state could gate admission, which is precisely the halt condition P.2 identifies. Its absence is therefore a constitutional requirement, and any future amendment adding one is void under `CIOS-01` VIII.4.

---

## 6. DEPENDENCY PROPERTIES

Properties are stated under **two explicit scopes**, because conflating them is itself a defect. The `DERIVES` scope is the graph the cycle test runs over; the combined scope is the whole-system view.

| Property | `DERIVES` scope | Combined (`DERIVES` + `OBSERVES`) scope | Basis |
|---|---|---|---|
| Nodes | **24** | **24** | `CIOS-03` |
| Edges | **25** | **88** (25 + 63) | §2 |
| Source nodes (in-degree 0) | **4** — `E-01`, `E-22`, `E-23`, `E-24` | **1** — `E-01` | single work ingress (`CIOS-P-01`) |
| Sink nodes (out-degree 0) | **4** — `E-21`, `E-22`, `E-23`, `E-24` | **3** — `E-22`, `E-23`, `E-24` | terminal emission + observation |
| Isolated nodes | **3** — `E-22`, `E-23`, `E-24` | **0** | observers carry no `DERIVES` edge |
| Topological layers | **21** | **22** | §3 |
| Longest path | **20 edges** | **21 edges** | §3 |
| Cycles | **0** | **0** | §4 |
| Self-loops | **0** | **0** | §2 |
| Back-edges into `PL-A` | **0** | **0** | §5.1 |
| Is a DAG | **YES** | **YES** | §4 |

### 6.1 Why the two scopes differ, and why it matters

The three observation engines carry **no `DERIVES` edge in either direction**. Under the `DERIVES` scope they are therefore *isolated* — simultaneously sources and sinks. Under the combined scope they acquire in-degree 21 and retain out-degree 0, so `E-01` becomes the sole source and `E-21` ceases to be a sink.

Both readings are true of their own scope, and both are acyclic. Stating only one would make the declaration ambiguous for a downstream mission implementing against it — which is why the scope label is part of the contract rather than a footnote. `CIOS-INV-05` is discharged under the **`DERIVES` scope** (§4), because that is the only scope in which a cycle is structurally possible.

The 63 `OBSERVES` edges are 21 non-observer engines × 3 observers. Machine-verified in `IMR-003A-R1/r1_verify.py` (checks `V-29` … `V-32`).

---

## AUTHORITY BOUNDARY (MANDATORY)

This artifact declares a dependency graph and proves it acyclic. It owns no mechanism, no registry, no gate, no identifier space and no concern. Every authority named is located in an instrument existing independently at `b26c5bb`. The acyclicity result is scoped to CIOS's own declared graph and does **not** discharge `UCCEP-F-003`. Where this artifact and a located canonical instrument disagree, **the located instrument governs and this artifact SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `CIOS-06` · PROVISIONAL · ADDITIVE · COMPOSITION-ONLY · AUTHORITY-NEUTRAL**
