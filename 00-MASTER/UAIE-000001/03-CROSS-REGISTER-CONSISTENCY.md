# Cross-Register Consistency

> This is the one measurement no located owner performed before this programme.
> Each owner validates its own register; none reads one register's references
> against what the repository still holds. A register that drifts while its own
> owner stays green is invisible individually and visible only across them.

**References checked:** 1954 · **unresolved:** 0

| Register | Path | Owner | Refs | Broken | Status |
|---|---|---|---|---|---|
| `UAIE-REG-01` | `00-BOOK/DATA/artifacts.json` | `00-BOOK/tools/ukb.py` | 1691 | 0 | **CONSISTENT** |
| `UAIE-REG-03` | `00-CMG/CMG-REGISTRY.json` | `00-CMG/tools/cmg_validate.py` | 45 | 0 | **CONSISTENT** |
| `UAIE-REG-09` | `intelligence/UCOS-RIE-CAPABILITY-CATALOG.json` | `intelligence/rie/engine.py` | 148 | 0 | **CONSISTENT** |
| `UAIE-REG-10` | `00-MASTER/UCOS-UAR-001/uar-analyses.json` | `00-MASTER/UCOS-UAR-001/uar_engine.py` | 45 | 0 | **CONSISTENT** |
| `UAIE-REG-11` | `00-MASTER/UAEP-000001/uaep-platform.json` | `00-MASTER/UAEP-000001/uaep_engine.py` | 25 | 0 | **CONSISTENT** |

No register references an artifact the repository has lost.

## Analyses this programme contributes

> Everything else on this page is reused. These are the only capabilities added, and
> each is an entry in the located analysis registry rather than a new registry.

| ID | Name | Kind | Registry status | Name collisions |
|---|---|---|---|---|
| `UAR-AIE-01` | `register-plane-consistency` | architectural-intelligence-analysis | **REGISTERED** | none |
| `UAR-AIE-02` | `faculty-binding-resolution` | architectural-intelligence-analysis | **REGISTERED** | none |
| `UAR-AIE-03` | `architectural-faculty-closure` | architectural-intelligence-analysis | **REGISTERED** | none |

### `UAR-AIE-01` — register-plane-consistency

- **Objective:** Measure every path referenced by every declared register of the register plane and report the ones that no longer resolve.
- **Why this is not already owned:** Each located analysis reasons within one substrate: the artifact registry validator checks the artifact registry, the meta-constitutional validator checks the constitutional registry, the platform binding engine checks its own bindings, and the analysis registry engine checks its own homes. None reads the registers against each other, so a register that drifts while its own owner stays green is invisible. This analysis is that cross-register reading and nothing more; it re-derives no substrate and duplicates no owner's verdict.

### `UAR-AIE-02` — faculty-binding-resolution

- **Objective:** Measure whether every named architectural faculty still resolves to a home and a symbol that exist, and to at least one analysis registered in the located analysis registry.
- **Why this is not already owned:** The capability catalogue records that a capability exists and where it lives; the analysis registry records that an analysis exists and who owns it. Neither answers whether a named architectural faculty is realised by a registered analysis at a resolving home, which is the join across the two. The platform binding engine performs the analogous join for platform capabilities but is scoped to that agreement and must not be widened to cover a different faculty set.

### `UAR-AIE-03` — architectural-faculty-closure

- **Objective:** Measure whether the faculty dependency relation is closed and acyclic and whether every declared register of the plane is claimed by at least one faculty.
- **Why this is not already owned:** Dependency closure is owned at the artifact, program and constitutional planes by three located owners. None of them holds a faculty plane, because none of them names faculties. This analysis measures closure over the faculty relation this programme declares, and asserts nothing about the planes those owners already own.
