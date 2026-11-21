# IMR-0000/17 — DIGITAL TWIN FRAMEWORK

| Field | Value |
|---|---|
| MISSION | `IMR-0000` — CIOS Platform Foundation |
| ARTIFACT | `17` — Digital Twin Framework (**deliverable 27**) · directive capability 21 |
| ARTIFACT KIND | Framework (`CMG-K-05`) — binding declaration |
| SUBSYSTEM | `SS-10` `CIOS-DT` — **BINDING-ONLY** (zero engines, zero ports, write scope ∅) |
| CENTRAL CLAIM | **The twin is derived state, not a persistence layer.** It is a projection over the located stores. The platform binds it read-only and adds no dimension, no store and no signal. |
| AUTHORITY OF ITS OWN | **NONE.** |
| CONFLICT RULE | Located instrument governs (`REG-AUTO-001`/`UKB-ADV` for the twin, `UCI-OPT-001` for the derived-not-stored determination, `UMB-002` for the architecture); then `IMR-003A`; then this artifact. |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. THE LOCATED TWIN

| Element | Located owner | Where |
|---|---|---|
| twin state | `REG-AUTO-001` / `UKB-ADV` | `00-BOOK/DATA/twin.json` |
| signal ledger (append-only) | `REG-AUTO-001` | `00-BOOK/DATA/signals.json`; `signal.schema.json` |
| twin architecture | `UMB-002` (`UCOS-UMB-000003`) | `00-BOOK/MASTER-BOOK/UMB-002-DIGITAL-TWIN-ARCHITECTURE.md` |
| twin certification architecture | `UCOS-ADV-000015`; `UMB-017`/`UMB-018` | located |
| twin intelligence realization | `UMB-IMP-005`, `UMB-IMP-006` | located |
| roll-up dimensions | `REG-AUTO-001` | `control-tower.json` `dimensions[]` |
| derived engineering twin view | `intelligence/rie` | `intelligence/UCOS-RIE-DIGITAL-TWIN.json` |
| the derived-not-stored determination | **`UCI-OPT-001` row 14** | *"Derived state/projection/relationship/view over S1+S4; **not** a new persistence layer"* |

---

## 2. RULES

| ID | Rule | Located basis |
|---|---|---|
| `DT-1` | **The twin is derived.** It is a projection over the artifact registry and the signal ledger. It is never a source of truth, and never authoritative against `artifacts.json`. | `UCI-OPT-001` row 14; `RR-1`; `RF-6` |
| `DT-2` | **No new persistence.** The twin introduces no store, schema, engine or identifier namespace. Net-new persistent structures: **zero**. | `UCI-OPT-001`; `UCI-001` `IP-6` |
| `DT-3` | **Signals are append-only and evidenced.** Every change emits at least one signal recording observed state, source and evidence. Every governed manual change sets `override=true` with `actor` and `reason`; **unattributed overrides are INVALID**. | `UCI-001` `CL-09`, `CL-10` |
| `DT-4` | **Derived intelligence is not fact.** Predictions, recommendations and scores are generated on demand and cite their provenance; they are never persisted as authoritative. | `UCI-001` `IP-3`, `IP-4` |
| `DT-5` | **Certification is a twin dimension, not a second certifier.** The twin certification dimension reports; `CEP-005` certifies. | `GOV-INT-001` §6.2 note; `UMB-017`/`UMB-018` |
| `DT-6` | **The JSON governs.** Rendered twin and control-tower views are generated; where a rendered view and the JSON disagree, the JSON governs. | `GOV-INT-001` §6.1; `RR-2` |

---

## 3. WHAT THE TWIN ANSWERS FOR THE PLATFORM

| Platform question | Twin surface | Access |
|---|---|---|
| what is the aggregate state of everything governed? | `control-tower.json` `portfolio` (`REG-03`) | **R** |
| what is each programme's roll-up? | `control-tower.json` `programs[]` | **R** |
| what is each dimension's status, and from which signal source? | `control-tower.json` `dimensions[]` | **R** |
| what was observed, when, from where, with what evidence? | `signals.json` | **R** |
| what is the projected state of an object? | `twin.json` | **R** |
| what is the derived engineering picture? | `UCOS-RIE-DIGITAL-TWIN.json`, `UCOS-RIE-*` | **R** |

**Observed state at `b26c5bb`:** `portfolio_status = IN_PROGRESS` — *analysis/architecture/generation complete; runtime testing/deployment pending EC-1*. Located dimension readings include BLOCKED and NOT_STARTED entries; those are located measurements, and the platform neither overrides nor reinterprets them.

---

## 4. THE CONFLATION THIS FRAMEWORK PREVENTS

The twin is the single most likely place for a future programme to introduce a second source of truth, because a twin *looks* like state.

| Mistake | Why it is wrong | Consequence |
|---|---|---|
| treating `twin.json` or `control-tower.json` as authoritative | both are `RR-1` **derived** from `artifacts.json` + `signals.json` | a second source of truth for one fact — `UUP-03` breach |
| persisting a prediction or score into the twin | `IP-3` forbids persisting derived intelligence as fact | fabricated truth with no evidence chain |
| adding a twin store for a new dimension | `DT-2`; dimensions are declared data owned by `REG-AUTO-001`/`UKB-ADV` | net-new persistence, `RF-2` breach |
| reading a rendered `.md` view as governing | `DT-6`; rendered views are generated | stale or divergent decisions |
| treating the twin certification dimension as a certification | `DT-5`; `CEP-005` is the sole certifier | self-certification, `UUP-07` breach |

---

## 5. PROPERTIES

| Property | Value |
|---|---|
| Twins created | **0** |
| Stores, schemas, engines or namespaces created | **0** |
| Dimensions added | **0** |
| Signals emitted or written | **0** |
| Twin state asserted or overridden | **0** |
| Derived values persisted as fact | **0** |
| Engines in `SS-10` | **0** — BINDING-ONLY |
| Ports in `SS-10` | **0** — programmes bind the located twin **directly** (`IFL-07`) |
| Write scope of `SS-10` | **∅** |

---

## 6. WHAT THIS FRAMEWORK DOES NOT DO

| Not done | Located owner |
|---|---|
| Create, write, project or regenerate the twin | `REG-AUTO-001`; `UKB-ADV`; `ukbx.py twin` |
| Emit, ingest or alter a signal | `REG-AUTO-001`; the located connectors |
| Add or remove a dimension, or override a dimension status | `REG-AUTO-001`; `STATUS-001` |
| Certify anything, or treat a twin dimension as certification | `CEP-005`; `DT-5` |
| Persist derived intelligence | `UCI-001` `IP-3` |
| Define a runtime, connector, deployment or infrastructure binding | `MC-05`, `MC-06`; `CIOS-L-22` |

---

## AUTHORITY BOUNDARY (MANDATORY)

This framework binds one located digital twin. **It creates no twin, no store, no schema and no dimension; it emits no signal, asserts no twin state, and persists no derived value.** `SS-10` holds no engine, no port and write scope ∅. The twin is derived state and is never authoritative against the located registers. Every owner named is located in an instrument existing independently at `b26c5bb`. Where this framework and a located canonical instrument disagree, **the located instrument governs and this framework SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `IMR-0000/17` · PROVISIONAL · ADDITIVE · DESIGN-ONLY · AUTHORITY-NEUTRAL**
