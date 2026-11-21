# Output 8 — Dependency Inventory

> **STATUS DOMAIN:** GOVERNANCE (measurement) · **STATUS BASIS:** `00-BOOK/DATA/relationships.json` parsed directly (M-2), the `Depends-On` projection independently re-layered by this programme (M-4), and `engine.graph.cli validate` executed at this HEAD (M-3)

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000007` · OUTPUT 8 |
| AUTHORITY | **NONE — DERIVED TRUTH** |
| SUBJECT | The edge population and the `Depends-On` DAG. Ownership of concerns → Output 9. Gate composition → Output 10. |
| EVIDENCE | `evidence/registry-metrics.txt` · `evidence/dag-computed.txt` |

---

## 1. Edge population (12,841 edges, 16 types)

Every type occurs with its inverse at equal count — the graph is stored bidirectionally.

| Type | Count | Inverse | Count |
|---|---|---|---|
| `Depends-On` | **4,774** | `Required-By` | 4,697 |
| `Parent` | 1,206 | `Child` | 1,206 |
| `Consumes` | 316 | `Consumed-By` | 316 |
| `Authorized-By` | 99 | `Authorizes` | 99 |
| `Implements` | 48 | `Implemented-By` | 48 |
| `References` | 6 | `Referenced-By` | 6 |
| `Traces-To` | 5 | `Traced-From` | 5 |
| `Evolves-From` | 5 | `Evolves-From-Inverse` | 5 |

`Depends-On` (4,774) and `Required-By` (4,697) differ by **77**. Measured and recorded in `12-DISCOVERY-OBSERVATIONS.md` OBS-9; not explained and not repaired.

## 2. The `Depends-On` DAG, independently recomputed

Kahn layering over the `Depends-On` projection, computed by this programme from `relationships.json` and `artifacts.json` alone:

| Property | Measured | Method |
|---|---|---|
| `Depends-On` edges | **4,774** | M-4 |
| Nodes in the ordering | **1,199** | M-4 |
| Placed / unorderable | **1,199 / 0** | M-4 |
| Parallel groups (layers) | **164** | M-4 |
| Critical path length (layers) | **164** | M-4 |
| Single-member groups | **112** | M-4 |
| Largest group size | **908** | M-4 |
| Cycle present | **NO** | M-4 |

These figures reproduce the ordering facts recorded independently by `UCCEP-000005` Outputs 7–9 (*"1199/1199 PLACED · 0 UNORDERABLE"*, *"1199/1199 ordered; identical digests across runs"*) and the execution model in the `UCCEP-000006` authorization certificate (*"DAG acyclic · `scc_gt1_count` 0 · ordering 1199/1199 · critical path 164 · parallel groups 164 · unorderable 0"*). Independent recomputation agrees with the located owner on every value.

## 3. Graph validator verdict at this HEAD

`python3 -m engine.graph.cli validate` (M-3):

```
is_valid                  : true
dependency_cycle          : []
duplicate_node_ids        : []
malformed_node_ids        : []
malformed_edge_ids        : []
unversioned_artifacts     : []
dangling_edge_endpoints   : []
node_count                : 1224
edge_count                : 12841
```

`node_count` (1,224) exceeds registered artifacts (1,199) by **25** — the volume nodes (Output 4: 25 volumes) participate in the graph. Measured, recorded in OBS-10.

## 4. Fail-closed semantics as committed

`engine/graph/validation.py` at this HEAD includes `dependency_cycle` in the `is_valid` conjunction. Its own docstring records the reason: *"a gate that reported the cycle while returning valid was fail-open (`UCCEP-F-003`, discharged by `WP-UCCEP-003` T-2 / `UCCEP-000005`)"*. Callers needing to inspect a knowingly-cyclic substrate pass `require_acyclic_dependencies=False`, which leaves the field empty and the invariant unasserted.

The finding's **record** state is separate from its substance and remains open — see `13-KNOWN-GAPS.md` DG-2.

## 5. Declared dependency data

| Fact | Measured | Method |
|---|---|---|
| Artifacts with ≥1 entry in `dependencies` | **190 of 1,199** | M-4 |
| Registers holding dependency data | `artifacts.json[*].dependencies` — register #6 of the eleven-register set (Output 4 §4) | M-2 |
| Programme-level dependency intelligence | `intelligence/UCOS-RIE-DEPENDENCY-GRAPH.json` — `layered_architecture_bottom_up` 11 layers, `program_edges` 16 | M-3 |

4,774 `Depends-On` edges arise from 190 artifacts carrying explicit `dependencies` plus structural edges the generator derives (the sampled edge carries `note: "structural:chain"`). The derivation rule is `config.py :: CHAINS`, whose `ENG` sequence was corrected at this baseline to `ENG-GOV-001` Output 11 Option B. Measured, recorded in OBS-11.

## 6. Acyclicity as an invariant

`CEP-009` Art XV.2 prohibits a lineage forming a cycle; Art XX.2 places the Program in HALTED if one exists. Boundary constraint **K-02** requires `scc_gt1_count = 0` and `dependency_cycle = []` after every unit. Both hold at this HEAD (§2, §3).

---

*`UCCEP-000007` Output 8. AUTHORITY = NONE (DERIVED TRUTH). Recomputed, not asserted. `CERTIFIED-PROVISIONAL`; Tier T1 VACANT.*
