# UCOS-AEE-001 — Convergence Certification

| Field | Value |
|---|---|
| PROGRAMME | `UCOS-AEE-001` — Autonomous Evolution Engine v1.0 |
| AUTHORITY | **NONE — DERIVED TRUTH. This programme legislates nothing, registers nothing, certifies nothing and owns no capability. It sequences located owners, reads their sealed determinations, and asserts convergence over what they report.** |
| TIER | `standard` |
| DETERMINATION | **CONVERGED-PROVISIONAL** |
| SEAL | `8ff810a249eb199e3f6cb93a0fe20fcb` |
| REPOSITORY ANCHOR | the containing commit — owned by version control, never restated here |

> Convergence is measured, never asserted. Byte-level repository closure is a different and stronger condition owned by the fixed-point programme and measured by its own gate; this certification does not claim it.

---

| Criterion | Statement | Expect | Measured | Blocking | Verdict |
|---|---|---|---|---|---|
| `CONV-01` | the observation vector is identical across the required number of consecutive iterations | `0` | `0` | yes | SATISFIED |
| `CONV-02` | every blocking observation is satisfied | `0` | `0` | yes | SATISFIED |
| `CONV-03` | every required actuator in the selected tier exits successfully | `0` | `0` | yes | SATISFIED |
| `CONV-04` | every mandate bound by an actuator or an observation resolves in a located mandate source | `0` | `0` | yes | SATISFIED |
| `CONV-05` | every discovered finding carries a class and a decision | `0` | `0` | yes | SATISFIED |
| `CONV-06` | all working-tree residue is attributable to a declared write zone | `0` | `0` | yes | SATISFIED |
| `CONV-07` | every observation pointer resolves in its located source | `0` | `0` | yes | SATISFIED |

## Declared scope boundaries

| Finding | Title | Disposition | Engineering-closable |
|---|---|---|---|
| `AEE-F-001` | A certification ceiling stands: the aggregate certifier reports standing located findings | REGISTERED | **no** |
| `AEE-F-002` | Convergence here is over the observation vector, not over the repository's bytes | GOVERNED | **no** |
| `AEE-F-003` | Cadence is bound to continuous integration, not to a resident process | GOVERNED | **no** |

**Determination: CONVERGED-PROVISIONAL** · gate exit `0`
