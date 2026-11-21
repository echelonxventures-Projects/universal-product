# UCOS-AEE-001 — Decision Register

| Field | Value |
|---|---|
| PROGRAMME | `UCOS-AEE-001` — Autonomous Evolution Engine v1.0 |
| AUTHORITY | **NONE — DERIVED TRUTH. This programme legislates nothing, registers nothing, certifies nothing and owns no capability. It sequences located owners, reads their sealed determinations, and asserts convergence over what they report.** |
| TIER | `standard` |
| DETERMINATION | **CONVERGED-PROVISIONAL** |
| SEAL | `8ff810a249eb199e3f6cb93a0fe20fcb` |
| REPOSITORY ANCHOR | the containing commit — owned by version control, never restated here |

> Every finding receives a decision from the declared rules, with the located evidence that justifies it. A decision whose evidence obligation is unmet is withheld rather than asserted.

---

## Decision values

| Decision | Definition |
|---|---|
| `IMPLEMENT` | Engineering work inside constitutional scope closes the finding. |
| `REUSE` | A located capability already satisfies the finding; bind to it rather than build. |
| `COMPOSE` | Several located capabilities together satisfy the finding. |
| `EXTEND` | A located capability satisfies the finding once its declared scope is widened. |
| `MERGE` | Two homes hold the same concept; one absorbs the other. |
| `DEPRECATE` | The subject is superseded and retires by append-only succession. |
| `REPLACE` | The subject is superseded by a successor that assumes its authority. |
| `IGNORE` | The reading is a false positive against Repository Truth. |
| `REJECT` | The finding is refused with recorded evidence. |
| `ESCALATE` | Closure requires an authority this repository does not contain; no engineering act can discharge it. |
| `DEFER` | Closure is admissible but blocked by a declared dependency; it waits on that dependency and on nothing else. |

## Adjudication

### `OBS-AGGREGATE-CEILING` — No standing finding bounds the attainable certification

| Field | Value |
|---|---|
| DECISION | **ESCALATE** |
| CLASS | Constitutional amendment |
| MATCHED RULE | `CR-ESCALATED-CEILING` |
| LOCATED OWNER | `00-MASTER/UCCEP-000000/uccep_engine.py` |
| GOVERNING FINDING | `AEE-F-001` |
| EVIDENCE | `00-MASTER/UCCEP-000000/uccep-bindings.json`, `00-MASTER/UCCEP-000000/uccep.json` |
| MEASURED | `["`UCCEP-F-004` — Constitutional finality is reserved to an ou…"]` |

The governing finding records that no located authority is competent to close the subject. An engineering act cannot discharge a vacancy of authority, so the finding leaves engineering scope and stands as a disclosed ceiling.

