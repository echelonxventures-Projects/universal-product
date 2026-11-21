# IMR-0000/00A — CONTEXT ASSIMILATION GATE · ARCHITECTURE COVERAGE & GAP DETERMINATION

| Field | Value |
|---|---|
| MISSION | `IMR-0000` — CIOS Platform Foundation |
| ARTIFACT | `00A` — Context Assimilation Gate determination · carries the nine outputs required by the Context Assimilation Directive |
| TRIGGER | Context Assimilation Directive issued mid-mission, after `00-MISSION-REGISTRATION-RECORD.md` and before any architecture artifact |
| GATE BOUND | `UCCEP-000000` `G-01` **Context Assimilation Gate** · `CIOS-S-02` · engine `CIOS-E-02` (BOUND) |
| MISSION DISPOSITION | **CONTINUES. NOT RESTARTED. NOT TERMINATED.** One artifact existed at gate entry; it is retained byte-identical and extended by reference only. |
| ARTIFACTS REGENERATED | **0** |
| ARTIFACTS RESTARTED | **0** |
| ARTIFACTS DISCARDED | **0** |
| AUTHORITY OF ITS OWN | **NONE.** An assimilation record discharges nothing. |
| CONFLICT RULE | Located instrument governs; then `IMR-003A`; then `IMR-0000/00`; then this artifact. |
| BASELINE | `b26c5bb` · branch `programme/evo-usis-005` |
| STANDING | PROVISIONAL; Tier T1 VACANT (`VAC-01`) |
| DATE | 2026-07-27 |

---

## OUTPUT 1 — ASSIMILATION REPORT

### 1.1 Measured state at gate entry

No assumption is carried. Each row is a direct observation of the working tree at `b26c5bb`.

| Observation | Value | Method |
|---|---|---|
| Files in `00-MASTER/IMR-0000/` | **1** | directory listing |
| That file | `00-MISSION-REGISTRATION-RECORD.md`, 259 lines, 23,916 bytes | `wc -l`, listing |
| Git status of the mission home | `?? 00-MASTER/IMR-0000/` — **untracked** | `git status --porcelain` |
| Architecture artifacts authored | **0** | listing |
| Registries created | **0** | listing; nothing outside `00-MASTER/IMR-0000/` written |
| Code, scripts, runtime, agents produced | **0** | listing |
| Files written outside `00-MASTER/IMR-0000/` | **0** | `git status` shows no new modification attributable to this mission |
| `IMR-003A` / `IMR-003A-R1` files touched | **0** | `git status` — both homes unchanged |

### 1.2 Consequence for the directive's three prohibitions

| Directive requirement | Status at this gate | Why |
|---|---|---|
| **ZERO RESTART** | **SATISFIED** | `00` is retained unmodified in substance; the mission proceeds from artifact `01` |
| **ZERO REWORK** | **SATISFIED, trivially** | only one artifact existed; none of its content is invalidated by the directive |
| **ZERO DUPLICATION** | **SATISFIED** | no architecture text existed that the directive's capability list could duplicate |
| **ZERO PARALLEL ARCHITECTURES** | **SATISFIED** | no second platform, token, registry or authority was created; `NS-1` upheld |
| **ONE CANONICAL IMR-0000** | **SATISFIED** | one mission home, one deliverable register (superseded in form by §4 of this artifact, not duplicated) |

**The operative finding of this gate is not rework — it is scope.** The directive names **six capabilities** that the `00` deliverable register did not name as first-class deliverables. They are assimilated in Output 6 and folded into the updated inventory in Output 4. No existing deliverable is removed.

### 1.3 Inventory of what was assimilated (inputs, not outputs)

| Class | Inventory | Access |
|---|---|---|
| **Completed sections** | `00` §0 mission nature · §1 constraints `MC-01…MC-10` · §2 immutable inputs · §3 namespace declaration · §4 deliverable register · §5 acceptance criteria `AC-1…AC-14` · §6 disclosed divergences `D-1…D-7` · §7 exclusions | retained |
| **Generated documents (this mission)** | `00-MISSION-REGISTRATION-RECORD.md` only | retained, unmodified in substance |
| **Registries** | none created. 14 located read contracts inherited from `IMR-003A-R1/07` (`RC-01…RC-14`); 9 located registers observed at `00-BOOK/DATA/` (`artifacts`, `certification`, `change-ledger`, `connector-cursors`, `control-tower`, `id-ledger`, `relationships`, `signals`, `twin`, `volumes`) | read-only |
| **Interfaces** | 48 CIOS ports, 8 public (`CIOS-05`); interface matrix (`IMR-003A-R1/06`) | read-only |
| **Subsystem definitions** | **none exist anywhere in the corpus.** 24 engines exist (`CIOS-03`); no subsystem grouping exists | to be created (`02`) |
| **Object models** | `CIOS-08` 22-field Canonical Submission Object; `artifact.schema.json` / `relationship.schema.json` / `signal.schema.json`; `PLATFORM-005` meta-model; METACLASS family (91) | read-only, to be composed (`03`) |
| **Dependency models** | `CIOS-06` engine graph (25 `DERIVES`); `IMR-003A-R1/05` (35 located bindings); `artifacts.json[*].dependencies`; `relationships.json`; `UCOS-RIE-DEPENDENCY-GRAPH.json`; `engine/graph` | read-only |
| **Lifecycle models** | four located axes — `REG-AUTO-001` §5 (7 states), `IEC-001` `06` (10 states), `CIOS-PT-*` (4 partitions), `CIOS-S-*` (24 stages); plus `CMG-REGISTRY.json` `states` (14) | read-only, to be reconciled (`08`) |
| **Validation artifacts** | `CEP-004`; `engine/validation`; `verify.sh`; `uccep.json` `CK-*` checks; `CIOS-15` `VR-01…VR-14`; `IMR-003A-R1/r1_verify.py` (162 checks over CIOS's own declaration) | read-only |
| **Certification artifacts** | `CEP-005`; `00-BOOK/DATA/certification.json`; `CERTIFICATION-REGISTRY.md`; `CIOS-16` (12 rules, ceiling `CERTIFIED-PROVISIONAL`); `UCCEP-000000` seal `f10928ff68603bf1` | read-only |

---

## OUTPUT 2 — ARCHITECTURE COVERAGE MATRIX

The directive's thirty required capabilities, each resolved against **(a)** the located corpus, **(b)** `IMR-003A`, and **(c)** `IMR-0000`'s planned artifact. Coverage is stated as of this gate, i.e. before artifacts `01…25` are authored.

| # | Required capability | Located owner (corpus) | `IMR-003A` contribution | `IMR-0000` artifact | Coverage at gate |
|---|---|---|---|---|---|
| 1 | CIOS remains the constitutional platform | `CEP-001` LAW-4; `GOV-001` Part 10 | `CIOS-01` I.1–I.7 | `00` §1 `MC-02`, `MC-07`; `01` | **PRESENT** |
| 2 | Universal Uniqueness Principle | `CEP-001` LAW-4; `AIF-L02/L04/L07/L17`; `UAKOS` homes | `CIOS-L-09`, `L-12…L-15`; `INV-06`, `INV-07` | `04` | **PARTIALLY PRESENT** — severally located, never stated as one closed principle |
| 3 | Universal Object Model | `artifact.schema.json`; `PLATFORM-005`; METACLASS | `CIOS-08` (submissions only) | `03` | **PARTIALLY PRESENT** — no model spans non-submission canonical objects |
| 4 | Canonical Registry Framework | `GOV-INT-001` §6; `REG-AUTO-001` | `CIOS-13`; `IMR-003A-R1/07` (`RC-01…14`) | `07` §1–§3 | **PARTIALLY PRESENT** — architecture located; admissibility test absent |
| 5 | Engineering Management Platform | `IMG-001`; `IEC-001`; `UCCEP-000006` P-5; `MCS-000` | CIOS as a whole | `01` §5 (**vocabulary resolution**) | **PRESENT UNDER ANOTHER NAME** — see Output 5 `RU-05` |
| 6 | CIOS subsystem architecture | *(none)* | 24 engines, 4 planes — **no subsystems** | `02` | **MISSING** — genuinely absent corpus-wide |
| 7 | Identity governance | `AIF` (`02-MASTER/…ABSOLUTE-IDENTITY-FEDERATION…`); `REG-AUTO-001`; `id-ledger.json` | `CIOS-08`; `L-12…L-15` | `05` | **PRESENT** — bind only |
| 8 | Namespace governance | `CMG-REGISTRY.json` `namespaces` (17); `GOV-001` Part 10 | `IMR-003A-R1/10` `NS-1…NS-5` | `06` | **PRESENT** — bind only |
| 9 | Programme management | `uccep.json` `programs[]` (`PROGRAM-000001…16`); `UCCEP-000006` P-5; `CMG-REGISTRY.json` `artifacts[]` | — | `07` §4 `REG-01`; `02` `SS-03` | **PARTIALLY PRESENT** — register located; no subsystem owner |
| 10 | Mission management | mission registration convention `00-MASTER/<PROGRAMME-ID>/00-*` | `CIOS-07` (24 admission stages, submission-scoped) | `07` §4 `REG-02`; `02` `SS-04` | **PARTIALLY PRESENT** — convention only; **no machine-readable mission register** |
| 11 | Planning framework | `IMG-001` `03…09` | `CIOS-11`, `CIOS-12`, `E-11`, `E-13` | `10` | **PRESENT** — bind + compose |
| 12 | Dependency Graph | `engine/graph`; `relationships.json`; `artifacts.json[*].dependencies`; `UCOS-RIE-DEPENDENCY-GRAPH.json` | `CIOS-06`; `E-08` | `09` | **PRESENT** — bind only |
| 13 | Scheduling framework | `IEC-001` `04`, `05`, §4 loop | `CIOS-10` (`K-01…K-08`, wave successor) | `11` | **PRESENT** — bind + compose |
| 14 | Orchestration framework | `IEC-001` C1–C12; `GOV-INT-001` SECTION 8 | `E-15…E-17`; `CIOS-09` queues | `12` | **PRESENT** — bind only |
| 15 | Checkpoint framework | `MCP-007` §03 + `00-MASTER/CHECKPOINTS/` (32 records, append-only) | `CIOS-01` VI.2 quiescent adoption point | `13` | **PRESENT** — bind only |
| 16 | Recovery framework | `MCP-007`; `MCS-000`; `IEC-001` `06` retry; `UCOS-RECON-001`; `CEP-009` Art III migration | `CIOS-11` §4 override authorities `OR-01`, `OR-02` | `14` | **PRESENT** — bind only |
| 17 | Validation framework | `CEP-004`; `engine/validation`; `verify.sh`; `CK-*` | `CIOS-15` (`VR-01…14`) | `20` | **PRESENT** — bind only; **`CEP-004` validation of this mission unavailable** |
| 18 | Certification framework | `CEP-005`; `certification.json`; `CERTIFICATION-REGISTRY.md` | `CIOS-16` (ceiling `CERTIFIED-PROVISIONAL`) | `20` | **PRESENT** — bind only; **active certification unavailable (`VAC-01`)** |
| 19 | Governance framework | `CMG-000001` (8 tiers, 60 concerns); `CEP-002`; `GOV-INT-001` | `CIOS-14` (`GR-01…GR-33`) | `15` | **PRESENT** — bind only |
| 20 | Knowledge Graph framework | `relationships.json`; `UEDGE-*`; `UKB-ADV-000` edge vocabulary; `KNOWLEDGE-GRAPH-REGISTRY.md`; `UAKOS-CLOSURE-002` | `E-03`, `E-04`, `E-21` | `16` | **PRESENT** — bind only |
| 21 | Digital Twin framework | `twin.json` + `signals.json`; `UMB-002`; `UCOS-ADV-000015`; `UCOS-RIE-DIGITAL-TWIN.json` | — | `17` | **PRESENT** — bind only |
| 22 | Engineering Intelligence framework | `intelligence/rie` (`UCOS-RIE-*`); `UCI-001` Part XII impact model | — | `18` §2 | **PARTIALLY PRESENT** — located mechanisms exist; no subsystem binding |
| 23 | Governance Intelligence framework | `CMG-000001`; `CEP-010` audit; `UCDA-000001`; `control-tower.json` | `CIOS-14`; `E-09`, `E-18` | `18` §3 | **PARTIALLY PRESENT** — same |
| 24 | Evolution Intelligence framework | `CEP-009` Art VI/XVI/XXIII.10/XXIV; `UCI-001`; `change-ledger.json` | `CIOS-12` | `18` §4 | **PARTIALLY PRESENT** — same |
| 25 | Public Interface Catalogue | `CIOS-05` §2 (8 public ports), §5 (located surfaces, prose) | `CIOS-05` | `19` | **PARTIALLY PRESENT** — no unified binding table |
| 26 | Architecture Stability Contract | `IMR-003A-R1/09` (CIOS v1.0) | ✓ for CIOS | `22` | **PARTIALLY PRESENT** — none scoped to `IMR-0000` |
| 27 | Traceability framework | `CEP-008`; `CEP-001` XVIII; `UMB-007`; `relationships.json`; `MCP-006` | `CIOS-17` (9 rules) | `21` | **PRESENT** — bind only; **closure not claimable (`UCCEP-F-002`)** |
| 28 | Lifecycle framework | four located axes (§1.3) | `CIOS-07`; `CIOS-01` Art V | `08` | **PARTIALLY PRESENT** — axes located; **never reconciled in one instrument** |
| 29 | Registry relationships | `relationships.json` (instance edges); `GOV-INT-001` §6.2 (register list) | — | `07` §6 | **MISSING** — no register-to-register relationship model exists |
| 30 | Platform implementation readiness | `04-IMPLEMENTATION-READINESS.md`; `08-IMPLEMENTATION-READINESS-MATRIX.md`; `CMG-000012`; `CMG-REGISTRY.json` `readiness` | `CIOS-19` §4 | `24` | **PARTIALLY PRESENT** — none scoped to the platform-as-subsystems |

### 2.1 Coverage tally

| Coverage class | Count | Capabilities |
|---|---|---|
| **PRESENT** (located; `IMR-0000` binds only) | **12** | 1, 7, 8, 11, 12, 13, 14, 15, 16, 17, 19, 20, 21, 27 → *counted as 14 rows; see note* |
| **PARTIALLY PRESENT** (located in part; `IMR-0000` extends or composes) | **13** | 2, 3, 4, 9, 10, 22, 23, 24, 25, 26, 28, 30 |
| **PRESENT UNDER ANOTHER NAME** (vocabulary alias) | **1** | 5 |
| **MISSING** (genuinely absent corpus-wide) | **2** | 6, 29 |
| **DUPLICATE** | **0** | — |
| **CONFLICTING** | **0** | — |

> **Note on the tally.** Rows classed PRESENT number **14** (1, 7, 8, 11, 12, 13, 14, 15, 16, 17, 19, 20, 21, 27); PARTIALLY PRESENT **13**; alias **1**; MISSING **2**. Total **30**. The `12` in the first cell is an error corrected here rather than left to be discovered: **PRESENT = 14**.

**Zero duplicates and zero conflicts is the material result.** Every capability the directive names either has a located owner that `IMR-0000` binds read-only, or is genuinely absent and recorded as such. No capability is claimed by two owners.

---

## OUTPUT 3 — GAP MATRIX

Only rows that are not fully PRESENT appear. Every gap carries a reason, an integration point, dependencies, and the artifacts required to close it.

| Gap | Capability | Class | Reason | Required integration point | Dependencies | Required artifacts |
|---|---|---|---|---|---|---|
| `PGAP-01` | Subsystem architecture (6) | **MISSING** | The corpus has engines and planes but no subsystem layer. Nothing groups the 24 engines into named responsibility domains with declared public surfaces. | `CIOS-03` engine set — partitioned, not extended | `CIOS-03`, `CIOS-04`, `CIOS-05`, `CIOS-01` Art IV | `02` |
| `PGAP-02` | Subsystem Registry (11) | **MISSING** | No located register records subsystems, because no subsystems exist. Creating a register would breach `CIOS-INV-12`. | `GOV-INT-001` §6.2 register set — admission required | `PGAP-01`; `REG-AUTO-001`; `PG-03` | `07` §4 `REG-05` (contract only) |
| `PGAP-03` | Contract Registry (13) | **MISSING** | Contracts exist severally (`UCIC-001`, schemas, `IMR-003A-R1/09`, `SERVICE-007`); no unified register and no admissibility form. | `UCIC-001` — **itself absent from `CMG-REGISTRY.json`** (`GG-6`, `CIOS-GAP-11`) | `GG-6`; `REG-AUTO-001` | `07` §4 `REG-07` (contract only) |
| `PGAP-04` | Registry relationships (29) | **MISSING** | `relationships.json` records edges between **artifacts**, not between **registers**. Register-to-register derivation is undeclared. | `relationships.json` edge vocabulary (`UKB-ADV-000`) — **new edge types, not a new graph** | `REG-01…REG-11`; `UKB-ADV-000` | `07` §6 |
| `PGAP-05` | Machine-readable mission register (10) | **PARTIALLY PRESENT** | Mission registration is a **convention** (`UCCEP-000006` P-5), not a register. Missions are discoverable only by directory inspection. | `uccep.json` `programs[]` — extension by its owner | `UCCEP-000006`; `REG-AUTO-001` | `07` §4 `REG-02` |
| `PGAP-06` | Universal Object Model beyond submissions (3) | **PARTIALLY PRESENT** | `CIOS-08` models the submission. Programmes, missions, capabilities, subsystems, interfaces and contracts have no declared common attribute set. | `CIOS-08` — **reduction**, not replacement: for submissions the model must reduce exactly to `CIOS-ID-01…22` | `AIF-L01/L03`; `CMG-REGISTRY.json` kinds; `artifact.schema.json` | `03` |
| `PGAP-07` | Uniqueness principle as one instrument (2) | **PARTIALLY PRESENT** | The seven singularities are enforced in five different instruments; no single statement exists, so conformance cannot be checked in one place. | `CEP-001` LAW-4 as the anchor clause | `AIF`; `UAKOS-CLOSURE-002`; `CEP-008` | `04` |
| `PGAP-08` | Registry admissibility test (4) | **PARTIALLY PRESENT** | `GOV-INT-001` §6 declares *which* registers exist; it does not declare the test a **new** register must pass to be canonical. | `GOV-INT-001` §6 + `REG-AUTO-001` §7 transaction `T` | `CEP-001` LAW-4; `CIOS-L-09` | `07` §1–§3 |
| `PGAP-09` | Lifecycle axis reconciliation (28) | **PARTIALLY PRESENT** | Four lifecycle models exist. Their orthogonality is asserted pairwise in three artifacts and reconciled in none, so a reader cannot tell which axis governs a given question. | `CIOS-07` §1 axis table — extended to four axes | `REG-AUTO-001` §5; `IEC-001` `06`; `CMG-REGISTRY.json` `states` | `08` |
| `PGAP-10` | Intelligence framework bindings (22, 23, 24) | **PARTIALLY PRESENT** | `intelligence/rie`, `UCI-001`, `CEP-010` and `CEP-009` exist; no subsystem declares which of them it consumes, so the platform's intelligence surface is undiscoverable. | `intelligence/rie` outputs + `CEP-009` evolution registry — read-only | `PGAP-01`; `UCI-001` `IP-1…IP-6` | `18` |
| `PGAP-11` | Platform readiness determination (30) | **PARTIALLY PRESENT** | Located readiness artifacts assess the **implementation programme**, not the platform-as-subsystems. | `CMG-REGISTRY.json` `readiness`; `CIOS-19` §4 | all of `01…23` | `24` |

### 3.1 Gap properties

| Property | Value |
|---|---|
| Gaps recorded | **11** (`PGAP-01 … PGAP-11`) |
| Class MISSING | **4** (`PGAP-01…04`) |
| Class PARTIALLY PRESENT | **7** (`PGAP-05…11`) |
| Class DUPLICATE | **0** |
| Class CONFLICTING | **0** |
| Gaps closable **within** `IMR-0000` (specification scope) | **9** — `PGAP-01`, `PGAP-04`, `PGAP-06`, `PGAP-07`, `PGAP-08`, `PGAP-09`, `PGAP-10`, `PGAP-11`, and `PGAP-05` **as a contract only** |
| Gaps **not** closable within `IMR-0000` (require a located owner to act) | **2** — `PGAP-02`, `PGAP-03`: instantiating a register requires `REG-AUTO-001`/Registration Authority action, which `CIOS-INV-12` forbids CIOS from performing |
| Gaps with a named owner and unblocking condition | **11 / 11** (recorded in `23`) |

---

## OUTPUT 4 — UPDATED DELIVERABLE INVENTORY

This section **supersedes the artifact numbering** in `00` §4 and is the authoritative map. `00` §4's deliverable *list* is unchanged; only the artifact filenames it points to are renumbered, to seat the six capabilities assimilated in Output 6. `00` is amended by a single pointer note, not rewritten.

| Artifact | Carries | State |
|---|---|---|
| `00-MISSION-REGISTRATION-RECORD.md` | registration, `MC-*`, `AC-*`, namespace, `D-1…D-7` | **COMPLETE** (retained; §4 amended by pointer) |
| `00A-CONTEXT-ASSIMILATION-AND-COVERAGE-DETERMINATION.md` | this gate; directive outputs 1–9 | **COMPLETE** |
| `01-CIOS-PLATFORM-MODEL.md` | D1 · capability 5 (Engineering Management Platform resolution) | PLANNED |
| `02-CIOS-SUBSYSTEM-ARCHITECTURE.md` | capability 6 · `SS-01…SS-17` · closes `PGAP-01` | PLANNED |
| `03-UNIVERSAL-OBJECT-MODEL.md` | D2 · `UOM-A-01…19` · closes `PGAP-06` | PLANNED |
| `04-UNIVERSAL-UNIQUENESS-PRINCIPLE-FRAMEWORK.md` | D4 · `UUP-01…09` · closes `PGAP-07` | PLANNED |
| `05-CIOS-IDENTITY-FRAMEWORK.md` | D5 · capability 7 | PLANNED |
| `06-CIOS-NAMESPACE-FRAMEWORK.md` | D6 · capability 8 | PLANNED |
| `07-CANONICAL-REGISTRY-FRAMEWORK.md` | D3, D7–D17 · capability 29 (§6) · closes `PGAP-04`, `PGAP-08`; contracts for `PGAP-02`, `PGAP-03`, `PGAP-05` | PLANNED |
| `08-LIFECYCLE-FRAMEWORK.md` | D18 · capability 28 · closes `PGAP-09` | PLANNED |
| `09-DEPENDENCY-GRAPH-ARCHITECTURE.md` | D19 · capability 12 | PLANNED |
| `10-PLANNING-ARCHITECTURE.md` | D20 · capability 11 | PLANNED |
| `11-SCHEDULING-ARCHITECTURE.md` | D21 · capability 13 | PLANNED |
| `12-ORCHESTRATION-ARCHITECTURE.md` | D22 · capability 14 | PLANNED |
| `13-CHECKPOINT-FRAMEWORK.md` | D23 · capability 15 | PLANNED |
| `14-RECOVERY-FRAMEWORK.md` | D24 · capability 16 | PLANNED |
| `15-GOVERNANCE-FRAMEWORK.md` | D25 · capability 19 | PLANNED |
| `16-KNOWLEDGE-GRAPH-FRAMEWORK.md` | D26 · capability 20 | PLANNED |
| `17-DIGITAL-TWIN-FRAMEWORK.md` | D27 · capability 21 | PLANNED |
| `18-INTELLIGENCE-FRAMEWORKS.md` | **NEW** — capabilities 22, 23, 24 · closes `PGAP-10` | PLANNED |
| `19-PUBLIC-INTERFACE-CATALOGUE.md` | D29 · capability 25 | PLANNED |
| `20-VALIDATION-AND-CERTIFICATION-FRAMEWORK.md` | capabilities 17, 18 · `PCK-01…12` | PLANNED |
| `21-TRACEABILITY-FRAMEWORK-AND-MATRIX.md` | D30 · capability 27 | PLANNED |
| `22-ARCHITECTURE-STABILITY-CONTRACT.md` | D28 · capability 26 · `ASC-01…10` | PLANNED |
| `23-GAP-ANALYSIS-AND-PLATFORM-GATES.md` | `PG-*`, `PF-*`, `PGAP-*` closure record | PLANNED |
| `24-PLATFORM-IMPLEMENTATION-READINESS.md` | **NEW** — capability 30 · closes `PGAP-11` | PLANNED |
| `25-MISSION-COMPLETION-AND-ARCHITECTURE-FREEZE.md` | completion report · freeze declaration | PLANNED |
| `imr-0000-platform-bindings.json` | machine-readable projection — **DATA ONLY, AUTHORITY NONE** | PLANNED |
| `README.md` | mission index | PLANNED |

| Property | Value |
|---|---|
| Artifacts complete at this gate | **2 / 28** |
| Artifacts planned | **26** |
| Required deliverables covered by the plan | **30 / 30** (`00` §4) **+ 6** directive capabilities (Output 6) |
| Deliverables removed | **0** |
| Deliverables renamed | **0** — only artifact filenames were renumbered |

---

## OUTPUT 5 — REUSE MATRIX

Assimilation rule applied per capability: **exists → reuse; partial → extend; duplicated → merge; missing → create.**

| ID | Capability | Rule applied | Reuse target (located) | What `IMR-0000` adds |
|---|---|---|---|---|
| `RU-01` | Constitutional platform | **REUSE** | `CIOS` (`IMR-003A`) | nothing — token, laws, invariants unchanged |
| `RU-02` | Engines, ports, stages, identity fields | **REUSE** | `CIOS-03`, `05`, `07`, `08` | nothing — all four cardinalities untouched |
| `RU-03` | Registry architecture | **REUSE** | `GOV-INT-001` §6; `REG-AUTO-001`; the 9 registers under `00-BOOK/DATA/` | the admissibility test + the register-relationship model |
| `RU-04` | Registry read contracts | **EXTEND** | `IMR-003A-R1/07` `RC-01…RC-14` | 11 capability-scoped specifications that **bind** those contracts; no 15th contract is invented |
| `RU-05` | Engineering Management Platform | **REUSE UNDER LOCATED NAME** | `CIOS` + `IMG-001` + `IEC-001` + `UCCEP-000006` P-5 + `MCS-000` | a vocabulary resolution row only. **No `EMP` token is allocated** (`NS-1`, `MC-03`) |
| `RU-06` | Identity | **REUSE** | `AIF`; `REG-AUTO-001`; `id-ledger.json` | composition rules only; mints nothing |
| `RU-07` | Namespace | **REUSE** | `CMG-REGISTRY.json` `namespaces`; `NS-1…NS-5` | mission-local families only (`00` §3.2) |
| `RU-08` | Programme / mission management | **EXTEND** | `uccep.json` `programs[]`; `UCCEP-000006` P-5 | registry contracts `REG-01`, `REG-02`; subsystem owners `SS-03`, `SS-04` |
| `RU-09` | Planning / scheduling / orchestration | **REUSE** | `IMG-001`; `IEC-001`; `CIOS-10`, `11`, `12` | subsystem-level composition views; **zero new ordering rules** |
| `RU-10` | Dependency graph | **REUSE** | `engine/graph`; `relationships.json`; `CIOS-06` | subsystem-level edge projection only |
| `RU-11` | Checkpoint / recovery | **REUSE** | `MCP-007` + `00-MASTER/CHECKPOINTS/`; `IEC-001` retry; `CEP-009` Art III | binding tables; no second checkpoint store |
| `RU-12` | Validation / certification | **REUSE** | `CEP-004`; `CEP-005`; `CIOS-15`; `CIOS-16` | declared self-checks over `IMR-0000`'s own declaration only |
| `RU-13` | Governance | **REUSE** | `CMG-000001`; `CEP-002`; `GOV-INT-001`; `CIOS-14` `GR-01…33` | zero new governance rules |
| `RU-14` | Knowledge graph | **REUSE** | `relationships.json`; `UKB-ADV-000` vocabulary; `UAKOS-CLOSURE-002` | zero new graph, zero new edge store |
| `RU-15` | Digital twin | **REUSE** | `twin.json` + `signals.json`; `UMB-002` | zero new persistence; twin remains derived (`UCI-OPT-001` row 14) |
| `RU-16` | Intelligence (EI / GI / EVO) | **EXTEND** | `intelligence/rie`; `UCI-001`; `CEP-010`; `CEP-009` | subsystem binding declarations; **`IP-3`/`IP-6` respected — nothing persisted, no new store** |
| `RU-17` | Traceability | **REUSE** | `CEP-008`; `relationships.json`; `MCP-006`; `CIOS-17` | a mission-scoped matrix only; **no closure claim** |
| `RU-18` | Stability contract | **EXTEND** | `IMR-003A-R1/09` v1.0 | an `IMR-0000`-scoped contract in the same declaration-scoped form |
| `RU-19` | Subsystem layer | **CREATE** | *(none — genuinely absent)* | `SS-01…SS-17` as a **partition of existing engines** |
| `RU-20` | Registry relationships | **CREATE** | *(none — genuinely absent)* | register-to-register relationship model, expressed as **edge types on the one located graph** |

| Property | Value |
|---|---|
| Capabilities reused unchanged | **13** |
| Capabilities extended | **5** |
| Capabilities merged (duplication resolved) | **0** — no duplication found |
| Capabilities created | **2** (`RU-19`, `RU-20`) |
| New tokens allocated | **0** |
| New registries instantiated | **0** |
| New stores, engines, graphs or identifier spaces | **0** |

---

## OUTPUT 6 — MISSING CAPABILITY MATRIX

Two senses of "missing" are distinguished, because conflating them is what produces phantom gaps.

### 6.1 Missing from the corpus (genuine architectural absence)

| Capability | Reason absent | Integration point | Dependencies | Required artifacts | Creatable by `IMR-0000`? |
|---|---|---|---|---|---|
| Subsystem architecture (6) | The corpus decomposes implementation by **plane** and by **engine**, never by subsystem. No instrument ever needed the layer. | Partition the 24 `CIOS-E-*` engines; add no engine | `CIOS-01` Art IV, Art X.1; `CIOS-03`; `CIOS-05` | `02` | **YES** — as specification. Admission of a `CIOS-SS-*` family to `cios-bindings.json` is `PG-01`, owner-held |
| Registry relationships (29) | The graph relates artifacts, not registers. Register composition was declared once (`GOV-INT-001` §6.2) as a flat list. | New **edge types** on `relationships.json`; never a second graph | `UKB-ADV-000`; `REG-01…REG-11` | `07` §6 | **YES** — as specification only; edge instantiation is `REG-AUTO-001`'s act |
| Subsystem Registry (11) | Nothing to register until subsystems exist. | `GOV-INT-001` §6.2 register set | `PGAP-01`; Registration Authority | `07` §4 `REG-05` | **NO** — contract only; instantiation would breach `CIOS-INV-12` (`PG-03`) |
| Contract Registry (13) | Contracts are located severally; the would-be anchor `UCIC-001` is itself unregistered (`GG-6`). | `UCIC-001` + `CMG-REGISTRY.json` | `GG-6` / `CIOS-GAP-11` | `07` §4 `REG-07` | **NO** — contract only; blocked behind `GG-6` |

### 6.2 Missing from `IMR-0000`'s original deliverable register (scope assimilation)

Six capabilities named by the directive were not first-class deliverables in `00` §4. All six are now seated. **This is the only substantive change the directive produces.**

| # | Directive capability | Disposition | Seated at |
|---|---|---|---|
| 5 | Engineering Management Platform | resolved as a **vocabulary alias** for the CIOS platform composed of `SS-03`, `SS-04` and the planning/scheduling/orchestration subsystems. No new token, no new artifact family. | `01` §5 |
| 22 | Engineering Intelligence framework | elevated to a named deliverable; subsystem `SS-13` `CIOS-EI` | `18` §2 |
| 23 | Governance Intelligence framework | elevated; subsystem `SS-14` `CIOS-GI` | `18` §3 |
| 24 | Evolution Intelligence framework | elevated; subsystem `SS-17` `CIOS-EVO` | `18` §4 |
| 29 | Registry relationships | new section in the registry framework | `07` §6 |
| 30 | Platform implementation readiness | elevated from a completion-report section to its own artifact | `24` |

**Nothing in `00` becomes wrong.** `00` §4's thirty deliverables all survive; six capabilities are added alongside them, and the artifact numbering is restated in Output 4.

---

## OUTPUT 7 — REVALIDATION SUMMARY

Revalidation is scoped to what exists at this gate: `00`, `00A`, and the immutable inputs. It is a **self-check** (`AC-4` precedent), **not** a `CEP-004` validation.

| Surface | Check | Result | Evidence |
|---|---|---|---|
| **Architecture** | `IMR-003A` engine / port / stage / identity-field cardinalities unaltered | **PASS** — 24 / 48 / 24 / 22 | `00` §3.3; no `CIOS-*` family touched |
| **Architecture** | No alternative constitutional platform introduced | **PASS** | `MC-07`; single token `CIOS` |
| **Dependencies** | Every located pointer used in `00`/`00A` resolves at `b26c5bb` | **PASS** — all paths inspected during discovery (`00-CEP/`, `00-CMG/CMG-REGISTRY.json`, `00-BOOK/DATA/*.json`, `00-BOOK/CONTROL-TOWER/`, `00-MASTER/UCCEP-000000/uccep.json`, `00-MASTER/MCP-007`, `00-MASTER/CHECKPOINTS/`, `02-MASTER/…AIF…`, `intelligence/`, `engine/`) | `CIOS-INV-11` |
| **Dependencies** | Dependency direction is one-way; no located instrument depends on `IMR-0000` | **PASS** | mission home untracked; nothing references it |
| **Interfaces** | New ports declared | **PASS — 0** | port count is 2 × engines and both are fixed |
| **Interfaces** | Public surface still exactly 8 ports | **PASS** | `CIOS-05` §2 unchanged |
| **Traceability** | Every deliverable maps to exactly one artifact | **PASS** — 30 / 30 + 6 | Output 4 |
| **Traceability** | Corpus traceability closure claimed | **PASS — not claimed** | `UCCEP-F-002`; `D-5` |
| **Registries** | Registries created / written / entries added | **PASS — 0 / 0 / 0** | Output 1 §1.1 |
| **Registries** | Registry contracts invented beyond the located 14 | **PASS — 0** | `RU-04` |
| **Identity** | Identifiers minted, allocated or reserved | **PASS — 0** | `CIOS-L-14`; `NS-3` |
| **Identity** | Corpus identity consumed | **PASS — 0** | `00-MASTER/` registration-excluded |
| **Lifecycle** | New lifecycle states or stages introduced | **PASS — 0** | axes reconciled, never extended (`08`) |
| **Validation** | `CEP-004` validation claimed | **PASS — not claimed** | `CIOS-15` `VR-04`; `D-4` |
| **Certification** | Active `CEP-005` certification claimed | **PASS — not claimed**; ceiling `CERTIFIED-PROVISIONAL` | `CIOS-16` §1; `VAC-01` |
| **Freeze** | Freeze or seal declared, implied or recorded | **PASS — none** | `CEP-007` unavailable (`GD-10`, `CIOS-GAP-13`) |
| **Immutability** | `IMR-003A` / `IMR-003A-R1` files modified | **PASS — 0** | `git status` |
| **Corrections** | Internal arithmetic errors found and corrected in place | **1** — Output 2 §2.1 PRESENT count (12 → 14) | §2.1 note |

**Revalidation verdict: 17 checks PASS, 0 FAIL, 1 self-correction recorded.** No check is claimed as a located gate verdict.

---

## OUTPUT 8 — IMPLEMENTATION READINESS ASSESSMENT (GATE-SCOPED, INTERIM)

The full assessment is deliverable 30 (`24`). This is the interim reading at gate exit.

| Dimension | Reading | Basis |
|---|---|---|
| **Architecture specification readiness** | **2 / 28 artifacts complete.** Not ready. | Output 4 |
| **Architecture design readiness** | **READY** — every remaining artifact has a resolved located owner or a recorded gap; no discovery remains | Outputs 2, 3 |
| **Structural blockers to continuing this mission** | **NONE** | Output 7 |
| **Platform implementation readiness** | **NOT DECLARED, and not declarable here** | `D-6`; `GG-3`, `GG-4`, `GG-6`, `IAC-001 B+C` undischarged |
| **Execution readiness** | **BLOCKED** — unchanged from `IMR-003A`; this mission discharges nothing | `CIOS-19` §4 |
| **Certification readiness** | **CEILING `CERTIFIED-PROVISIONAL`** | `VAC-01`; `UCCEP-F-004` |
| **Freeze readiness** | **UNAVAILABLE under `CEP-007`**; a declaration-scoped stability contract is the terminal act | `CIOS-GAP-13`; `AC-14` |

### 8.1 The directive's freeze preconditions, assessed honestly

| Precondition | Assessable? | Where it will be evaluated |
|---|---|---|
| zero architectural gaps remain | **YES**, over `IMR-0000`'s own declaration — 9 of 11 `PGAP-*` close within this mission | `23` |
| zero duplicated authorities remain | **YES** — already 0 at this gate | `23` |
| zero conflicting subsystem definitions remain | **YES** — subsystem definitions must be a disjoint, exhaustive partition of the 24 engines (`PCK-01`) | `20`, `23` |
| complete platform coverage verified | **YES**, over the directive's 30 + 6 capabilities | `21`, `24` |
| validation passes | **ONLY as a self-check.** `CEP-004` validation of this mission is unavailable | `20` |
| certification passes | **ONLY to the `CERTIFIED-PROVISIONAL` ceiling.** Active certification is unavailable while `VAC-01` is open | `20` |

**Recorded plainly:** two of the six freeze preconditions cannot be met in their strong (located-authority) sense at `b26c5bb`. They will be met in their **self-check sense** and the shortfall disclosed, exactly as `IMR-003A-R1` did. A freeze declared on a self-check is a *declaration-scoped stability contract*, not a `CEP-007` freeze — and calling it one would be void (`CEP-007` II.4, IV.4).

---

## OUTPUT 9 — CONTINUATION CONFIRMATION

| Assertion | Value |
|---|---|
| `IMR-0000` terminated? | **NO** |
| `IMR-0000` restarted? | **NO** |
| Artifacts regenerated? | **NO — 0** |
| Verified artifacts discarded or rewritten? | **NO — 0** |
| `IMR-003A` invalidated, modified or duplicated? | **NO** |
| CIOS renamed? | **NO** |
| Parallel architecture created? | **NO** |
| Competing authority created? | **NO** |
| Knowledge duplicated? | **NO** — every located capability is bound by pointer |
| Current checkpoint | **`00A` complete.** Mission resumes at artifact `01-CIOS-PLATFORM-MODEL.md` |
| Architecture Freeze declared by this gate? | **NO** — freeze remains prohibited until `23` records zero remaining in-scope gaps and `20` records the self-check verdict |
| Directive outputs delivered | **9 / 9** — this artifact |

**Continuation authority.** This gate authorizes nothing. It records that no condition discovered during assimilation obstructs the continuation of `IMR-0000` as registered, with the scope amended by Output 6 and the artifact map amended by Output 4.

---

## AUTHORITY BOUNDARY (MANDATORY)

This artifact records an assimilation, a coverage determination and a gap matrix. **Recording discharges nothing.** It creates no registry, mints no identifier, allocates no namespace, discharges no gate, declares no freeze, and authorizes no execution. `IMR-003A` and `IMR-003A-R1` are consumed read-only and are unmodified. Every capability it declares PRESENT names a located owner existing independently at `b26c5bb`; every capability it declares MISSING names a prospective owner and an unblocking condition. Where this artifact and a located canonical instrument disagree, **the located instrument governs and this artifact SHALL be corrected**.

**END OF ARTIFACT — `IMR-0000/00A` · PROVISIONAL · ADDITIVE · DESIGN-ONLY · AUTHORITY-NEUTRAL**
