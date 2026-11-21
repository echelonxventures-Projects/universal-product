# IMR-0000/21 — TRACEABILITY FRAMEWORK AND MATRIX

| Field | Value |
|---|---|
| MISSION | `IMR-0000` — CIOS Platform Foundation |
| ARTIFACT | `21` — Traceability Matrix (**deliverable 30**) + Traceability Framework (directive capability 27) |
| ARTIFACT KIND | Framework (`CMG-K-05`) + traceability matrix |
| NUMERIC CONTRACT | **36 matrix rows** `TM-01 … TM-36` — the 30 required deliverables plus the 6 capabilities the Context Assimilation Directive added |
| CENTRAL DISCLOSURE | Traceability is complete **within this mission's declaration**. **Corpus traceability closure is not claimed** — it is incomplete for all **1198** registered artifacts (`UCCEP-F-002`). |
| AUTHORITY OF ITS OWN | **NONE.** |
| CONFLICT RULE | Located instrument governs (`CEP-008`, then `CEP-001` XVIII, then `UMB-007`); then `IMR-003A` (`CIOS-17`); then this artifact. |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. TRACEABILITY FRAMEWORK

| ID | Rule | Located basis |
|---|---|---|
| `TF-1` | **One graph, one chain.** Every traceability fact is an edge on `relationships.json`. No parallel traceability store, and no second chain for one object. | `GOV-INT-001` §2.6; `UUP-05`; `KG-1` |
| `TF-2` | **Rooted and closed is the standard; neither is claimed here.** `CEP-001` XVIII requires rooted-and-closed traceability corpus-wide; that standard is **unmet** at `b26c5bb`. | `CEP-001` XVIII; `UCCEP-F-002` |
| `TF-3` | **Emission never blocks the seal.** A traceability failure marks an item traceability-incomplete and emits a finding; it does not prevent `PT-02 → PT-01`. | `CIOS-05` `P-42`; `CIOS-17` §5 |
| `TF-4` | **Traceability is derived, not recorded.** The chain is a traversal of dependencies and relationships; it is never persisted as a separate fact. | `UOM-A-20`; `AIF-L01`; `IP-3` |
| `TF-5` | **Bidirectional, no orphans.** Every edge is traversable both ways; no orphan node exists. | `UCI-001` `CL-08` |
| `TF-6` | **Every determination traces to its evidence and its authority.** A determination that traces to neither is not a determination. | `CEP-008`; `CEP-001` LAW-2; `CIOS-L-07` |
| `TF-7` | A mission-scoped matrix (this artifact) is **evidence of internal completeness only**. It confers no corpus closure. | `TF-2`; `CIOS-17` §5 |

### 1.1 The four traceability scopes

| Scope | What it traces | Owner | Complete at `b26c5bb`? |
|---|---|---|---|
| **corpus** | every registered artifact → its authority and evidence | `CEP-008`; `relationships.json`; `UCCEP-000000` `07` | **NO** — incomplete for 1198 artifacts (`UCCEP-F-002`, `CIOS-G-06` OPEN) |
| **decision** | every decision → its disposition and evidence | `UCDA-000001`; `CEP-002` Art 28 | **YES, as measured** — 64 decisions, 0 undispositioned, 205 evidence items |
| **concept** | every concept → its canonical home and owner | `UAKOS-CLOSURE-002` | **YES** — 434 concepts, `gap_total = 0`, all seven gap classes zero |
| **mission** (this artifact) | every deliverable → its artifact, authority, subsystem, validation and certification | `IMR-0000` | **YES** — 36 / 36 (§2) |

**Two of four scopes are complete; the corpus scope is not, and that is the one `CEP-001` XVIII cares about.** This mission adds no incompleteness to it and closes none of it.

---

## 2. THE TRACEABILITY MATRIX — 36 ROWS

**Legend.** *Artifact* = where the deliverable is discharged · *Located authority* = the instrument that owns the mechanism · *Subsystem* = the platform binding · *V* = validation route · *C* = certification route. `V`/`C` are `CEP-004`/`CEP-005` throughout, so the columns record the **specific located gate or check**, not the constitution.

### 2.1 The 30 required deliverables

| ID | Deliverable | Artifact | Located authority | Subsystem | V | C |
|---|---|---|---|---|---|---|
| `TM-01` | CIOS Platform Model | `01` | `CIOS-01` Art I–VII; `CEP-001` LAW-4 | all 17 | `PCK-05` | ceiling |
| `TM-02` | Universal Object Model | `03` | `AIF-L01`/`L03`; `CMG-REGISTRY.json` kinds; `CIOS-08` | `SS-02` | `PCK-04`, `PCK-12` | ceiling |
| `TM-03` | Canonical Registry Framework | `07` §1–§3 | `GOV-INT-001` §6; `REG-AUTO-001` | `SS-03` | `PCK-05` | ceiling |
| `TM-04` | Universal Uniqueness Principle Framework | `04` | `CEP-001` LAW-4; `AIF-L02/L07/L17`; `UAKOS` | all 17 | `PCK-05` | ceiling |
| `TM-05` | CIOS Identity Framework | `05` | `AIF`; `REG-AUTO-001`; `id-ledger.json` | `SS-02` | `G-07`; `PCK-03` | ceiling |
| `TM-06` | CIOS Namespace Framework | `06` | `CMG-000001` namespaces; `GOV-001` Part 10; `NS-1…5` | `SS-02` | `PCK-03` | ceiling |
| `TM-07` | Programme Registry | `07` §4 `REG-01` | `uccep.json` `programs[]`; `UCCEP-000006` P-5 | `SS-03` | `CK-CMG` | `UCCEP` seal |
| `TM-08` | Mission Registry | `07` §4 `REG-02` | convention `UCCEP-000006` P-5 — **no register** | `SS-03`, `SS-04` | — (`PGAP-05`) | ceiling |
| `TM-09` | Portfolio Registry | `07` §4 `REG-03` | `control-tower.json`; `STATUS-001` | `SS-10`, `SS-03` | `CK-REG-VALIDATE` | ceiling |
| `TM-10` | Capability Registry | `07` §4 `REG-04` | capability catalogue; `PLATFORM-006`; `UCIC-001` | `SS-03`, `SS-13` | `GG-6` **open** | ceiling |
| `TM-11` | Subsystem Registry | `07` §4 `REG-05` | **none** — prospective `REG-AUTO-001` | `SS-*` (declares) | — (`PGAP-02`) | — |
| `TM-12` | Interface Registry | `07` §4 `REG-06` | `CIOS-05`; `IMR-003A-R1/06` | all with ports | `PCK-03` | ceiling |
| `TM-13` | Contract Registry | `07` §4 `REG-07` | **none unified** — `UCIC-001` unregistered | `SS-03`, `SS-16` | — (`PGAP-03`) | — |
| `TM-14` | Dependency Registry | `07` §4 `REG-08` | `artifacts.json[*].dependencies`; `relationships.json`; `engine/graph` | `SS-08` | `G-08`, `CK-GRAPH` | ceiling |
| `TM-15` | Evidence Registry | `07` §4 `REG-09` | `CEP-008`; `signals.json`; `ucda-decisions.json` | `SS-13`, `SS-14` | `G-12`, `CK-DECISION-EVIDENCE` | ceiling |
| `TM-16` | Validation Registry | `07` §4 `REG-10` | `uccep.json` `checks`; `engine/validation` | `SS-15` | `G-10` | ceiling |
| `TM-17` | Certification Registry | `07` §4 `REG-11` | `certification.json`; `CERTIFICATION-REGISTRY.md` | `SS-16` | `G-11` | **`CERTIFIED-PROVISIONAL`** |
| `TM-18` | Lifecycle Framework | `08` | `REG-AUTO-001` §5; `CMG` states; `IEC-001` `06`; `CIOS-01` Art V; `CIOS-07` | `SS-01` | `G-01…G-14` (all bound) | ceiling |
| `TM-19` | Dependency Graph Architecture | `09` | `engine/graph`; `relationships.json`; `CIOS-06` | `SS-08` | `CK-GRAPH` (**fails open**, `UCCEP-F-003`) | ceiling |
| `TM-20` | Planning Architecture | `10` | `IMG-001` `03`–`09`; `CIOS-01` Art VI; `CIOS-12` | `SS-05` | `UCCEP-F-001` **bound** | ceiling |
| `TM-21` | Scheduling Architecture | `11` | `IEC-001` `04`, `05`; `CIOS-10`; `AIF-L04` | `SS-06` | `PCK-04` | ceiling |
| `TM-22` | Orchestration Architecture | `12` | `IEC-001` C1–C12; `GOV-INT-001` §8; `CIOS-11` | `SS-07` | `IEC-001` Q1–Q8 | EC-3 gate |
| `TM-23` | Checkpoint Framework | `13` | `MCP-007` §03; `00-MASTER/CHECKPOINTS/` | `SS-11` | `MCP-007` §04.B | ceiling |
| `TM-24` | Recovery Framework | `14` | `MCP-007`; `IEC-001` `06` retry; `CEP-009` Art III | `SS-11`, `SS-14` | `GG-3` **open** | ceiling |
| `TM-25` | Governance Framework | `15` | `CMG-000001`; `CEP-001…010`; `GOV-INT-001`; `CIOS-14` | `SS-14` | `G-09` | ceiling |
| `TM-26` | Knowledge Graph Framework | `16` | `relationships.json`; `UKB-ADV-000`; `UAKOS-CLOSURE-002` | `SS-09` | `CK-CLOSURE-P1/P2` (**NOT-EXECUTED**) | ceiling |
| `TM-27` | Digital Twin Framework | `17` | `twin.json`; `signals.json`; `UMB-002`; `UCI-OPT-001` row 14 | `SS-10` | `ukbx twin --check` | twin dimension |
| `TM-28` | Architecture Stability Contract | `22` | `IMR-003A-R1/09` form; `CEP-009` III.1 route | all 17 | `PCK-11` | **not a `CEP-007` freeze** |
| `TM-29` | Public Interface Catalogue | `19` | `CIOS-05` §2, §5 | 5 with public ports | `PCK-03` | ceiling |
| `TM-30` | Traceability Matrix | `21` (this artifact) | `CEP-008`; `CEP-001` XVIII; `CIOS-17` | `SS-13` | `PCK-11` | **no closure claimed** |

### 2.2 The 6 capabilities added by the Context Assimilation Directive

| ID | Capability | Artifact | Located authority | Subsystem | V | C |
|---|---|---|---|---|---|---|
| `TM-31` | Engineering Management Platform | `01` §5 (vocabulary resolution) | `CIOS`; `IMG-001`; `IEC-001`; `UCCEP-000006` P-5; `MCS-000` | `SS-03`–`SS-07` | `PCK-05` | ceiling |
| `TM-32` | CIOS subsystem architecture | `02` | **none located** — `PGAP-01`, closed by this mission as specification | all 17 | `PCK-01` | ceiling |
| `TM-33` | Engineering Intelligence framework | `18` §2 | `intelligence/rie`; `CEP-008`; `relationships.json` | `SS-13` | `CK-VERIFY` | ceiling |
| `TM-34` | Governance Intelligence framework | `18` §3 | `CMG-000001`; `CEP-002` Art 28; `CEP-010`; `UCDA-000001` | `SS-14` | `CK-DECISION-EVIDENCE` | ceiling |
| `TM-35` | Evolution Intelligence framework | `18` §4 | `CEP-009` Art VI/XVI/XXIV; `UCI-001`; `change-ledger.json` | `SS-17` | `G-09` | ceiling |
| `TM-36` | Registry relationships | `07` §6 | **none located** — `PGAP-04`; types proposed to `UKB-ADV-000` | all with registers | `PCK-05` | ceiling |

> Note: capabilities 29 and 30 of the directive's list are `TM-36` (registry relationships) and **`24`** (platform implementation readiness, traced at `TM-37` below as an artifact-level row rather than a deliverable, since it is an assessment of the other 36).

| ID | Capability | Artifact | Located authority | Subsystem | V | C |
|---|---|---|---|---|---|---|
| `TM-37` | Platform implementation readiness | `24` | `CMG-REGISTRY.json` `readiness`; `CMG-000012`; `CIOS-19` §4 | all 17 | `PCK-11` | ceiling |

---

## 3. MATRIX RECONCILIATION

| Property | Value |
|---|---|
| Required deliverables traced | **30 / 30** |
| Directive capabilities traced | **30 / 30** (the six newly named are `TM-31` … `TM-36`; the other 24 map onto `TM-01 … TM-30`) |
| Matrix rows | **37** (`TM-01 … TM-37`) |
| Rows with a named located authority | **35 / 37** |
| Rows with **no** located authority | **2** — `TM-11` (Subsystem Registry, `PGAP-02`), `TM-13` (Contract Registry, `PGAP-03`); both recorded with prospective owners and open gates |
| Rows with a subsystem binding | **37 / 37** |
| Rows with a validation route | **34 / 37** — three (`TM-08`, `TM-11`, `TM-13`) have none because the register they would validate does not exist |
| Rows certified active | **0** — every row is ceiling-bound at `CERTIFIED-PROVISIONAL` |
| Orphan artifacts (artifact with no traced deliverable) | **0** |
| Deliverables with no artifact | **0** |
| Rows carrying an inherited, owner-held defect | **8** — `TM-10` (`GG-6`), `TM-19` (`UCCEP-F-003`), `TM-20` (`UCCEP-F-001`), `TM-24` (`GG-3`), `TM-26` (`CK-CLOSURE-*` NOT-EXECUTED), `TM-17`/`TM-28`/`TM-30` (`VAC-01`, `UCCEP-F-002`) |

---

## 4. WHAT IS NOT TRACED, AND WHY

| Not traced | Reason |
|---|---|
| corpus traceability closure | **incomplete for 1198 registered artifacts** (`UCCEP-F-002`); `CIOS-G-06` OPEN, owner `CEP-008` |
| this mission's artifacts → corpus identity | `00-MASTER/` is registration-excluded; mission artifacts hold no corpus identity (`NS-3`) |
| this mission's home → a commit | `00-MASTER/IMR-0000/` is **untracked** at `b26c5bb`, as `IMR-003A/` is (`CIOS-GAP-14`; this mission's instance is `PF-03`) |
| edges instantiated on the located graph | **0 written** — this mission emits no edge (`16` §4) |
| decision entries in `ucda-decisions.json` | **0 added** — whether `D-1…D-7` require entries is `UCDA-000001`'s determination (`PF-04`) |

---

## 5. WHAT THIS ARTIFACT DOES NOT DO

| Not done | Located owner |
|---|---|
| Claim corpus traceability closure | `CEP-008`; `UCCEP-F-002`; `CIOS-17` §5 |
| Create a traceability store, graph or chain | `relationships.json`; `TF-1` |
| Write, emit or instantiate an edge | `REG-AUTO-001`; runtime emission is `CIOS-P-42`'s |
| Persist a derived chain as fact | `TF-4`; `IP-3` |
| Discharge `UCCEP-F-002` / `CIOS-G-06` | located traceability authority |
| Certify any row, or assert standing above the ceiling | `CEP-005`; `CF-C3` |

---

## AUTHORITY BOUNDARY (MANDATORY)

This artifact traces this mission's own deliverables and binds the located traceability authority. **It claims no corpus traceability closure**, creates no store, no graph and no chain, and writes no edge. Two matrix rows have no located authority and are recorded as gaps with prospective owners and open gates; eight carry inherited, owner-held defects. Every row is certification-ceiling-bound at `CERTIFIED-PROVISIONAL`. Where this artifact and a located canonical instrument disagree, **the located instrument governs and this artifact SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `IMR-0000/21` · PROVISIONAL · ADDITIVE · DESIGN-ONLY · AUTHORITY-NEUTRAL**
