# IMR-0000/02 — CIOS SUBSYSTEM ARCHITECTURE

| Field | Value |
|---|---|
| MISSION | `IMR-0000` — CIOS Platform Foundation |
| ARTIFACT | `02` — CIOS Subsystem Architecture (directive capability 6) · declares platform layer **L4** |
| ARTIFACT KIND | Architecture (`CMG-K-05`) |
| CLOSES | `00A` `PGAP-01` — the one genuinely absent architectural layer in the corpus |
| NUMERIC CONTRACT | **exactly 17 subsystems**, `SS-01 … SS-17`, forming a **partition of the 24 engines** `CIOS-E-01 … CIOS-E-24`: pairwise disjoint, jointly exhaustive |
| AUTHORITY OF ITS OWN | **NONE.** A subsystem is a grouping, not an owner. No subsystem holds a mechanism, gate, registry, identifier space or concern (`CIOS-INV-12`). |
| CONFLICT RULE | Located instrument governs; then `IMR-003A`; then this artifact. |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. WHAT A SUBSYSTEM IS, AND IS NOT

| A subsystem **is** | A subsystem **is NOT** |
|---|---|
| a named responsibility domain over a **disjoint subset of the existing 24 engines** | a new engine, or a container that can acquire engines |
| a declared **binding set** — the located owners it consumes read-only | an owner of anything it binds |
| a mission-local declaration (`SS-*`) carrying a CIOS-facing **canonical name** (`CIOS-CORE` …) | a corpus identifier, a `CMG-REGISTRY.json` namespace, or an `id-ledger` entry |
| possibly **BINDING-ONLY** — holding zero engines | permitted to invent a mechanism to fill an empty engine set |
| an architectural role | a process, service, daemon, module, package or deployment unit |

### 1.1 Binding classes

Inherited in form from `CIOS-03` §1.1, applied at subsystem scale.

| Class | Meaning | Count |
|---|---|---|
| **ENGINE-BEARING** | holds ≥1 engine; its responsibility is discharged by those engines plus read-only bindings | **12** |
| **BINDING-ONLY** | holds **zero** engines; its responsibility is discharged **entirely** by located owners it binds read-only | **5** |
| **ABSENT** | mechanism does not exist and no located owner exists | **0** |

**Why five subsystems are BINDING-ONLY, and why that is the correct outcome.** `CIOS-01` Art X.1 fixes the engine count at exactly 24 and makes that count its own closure test; `NS-4` forbids altering it by data change; `MC-01` forbids the `CEP-009` III.1 change to `CIOS-01` that would be required. Therefore `IMR-0000` **cannot** create an engine, and a subsystem whose capability is wholly located elsewhere must hold none. Inventing a COMPOSING engine without one of `CIOS-01` Art VII.3's nine authorizations is precisely the act `CIOS-01` VIII.4 declares void. The empty engine set is compelled, not chosen — and it is recorded here rather than concealed by padding.

### 1.2 Subsystem rules

| ID | Rule | Basis |
|---|---|---|
| `SR-1` | Every engine belongs to **exactly one** subsystem. No engine is shared, and none is unassigned. | §4.1; `PCK-01` |
| `SR-2` | A subsystem owns no mechanism, gate, registry, identifier space or concern. | `CIOS-INV-12`; `PL-R4` |
| `SR-3` | A subsystem's write scope is the **union of its engines' plane scopes**, never wider. A BINDING-ONLY subsystem has write scope **∅**. | `CIOS-INV-02`; `WS-1…WS-9`; `PL-R8` |
| `SR-4` | A subsystem exposes **no new port**. Its interface is exactly its engines' existing ports. | `CIOS-05` `PR-1`; `PL-R3` |
| `SR-5` | A subsystem's **public** interface is the subset of its engines' ports that `CIOS-05` §2 declares public. A subsystem may not promote an internal port. | `CIOS-05` §2 |
| `SR-6` | Subsystem responsibilities are pairwise non-overlapping. Apparent overlap is resolved in §5 or is a defect in this artifact. | `CIOS-L-10`; `CIOS-03` §5 |
| `SR-7` | A subsystem may consume another subsystem's output only along an existing `CIOS-06` `DERIVES` edge. Subsystem composition introduces **no new edge**. | `CIOS-06`; `CIOS-INV-05` |
| `SR-8` | Adding a subsystem is a **data change** to the platform declaration; it amends no law, alters no engine and creates no port. Admission of a `CIOS-SS-*` family to `cios-bindings.json` is `PG-01`. | `CIOS-L-23`; `NS-2` |
| `SR-9` | No subsystem enumerates a domain, technology, vendor, platform, language, protocol or format. | `CIOS-L-22` |
| `SR-10` | Every subsystem field below is either a pointer to a located owner or a statement of absence. No field asserts a capability CIOS holds. | `CIOS-L-11`; `MC-08` |

---

## 2. THE SUBSYSTEM REGISTER

Identity is mission-local and immutable; the canonical name is the CIOS-facing label (`UUP-08`, `UUP-09`).

| Identity | Canonical name | Domain | Class | Engines | Planes |
|---|---|---|---|---|---|
| `SS-01` | **CIOS-CORE** | constitutional kernel · partition algebra | ENGINE-BEARING | `E-10`, `E-19` | `PL-A`, `PL-C` |
| `SS-02` | **CIOS-IDENTITY** | identity composition | ENGINE-BEARING | `E-07` | `PL-A` |
| `SS-03` | **CIOS-PMS** | programme management | **BINDING-ONLY** | — | — |
| `SS-04` | **CIOS-MRS** | mission (submission) registration | ENGINE-BEARING | `E-01`, `E-02` | `PL-A` |
| `SS-05` | **CIOS-PLAN** | plan epoch composition · realignment | ENGINE-BEARING | `E-11`, `E-13` | `PL-A` |
| `SS-06` | **CIOS-SCHED** | priority derivation · quiescent adoption | ENGINE-BEARING | `E-12`, `E-14` | `PL-A` |
| `SS-07` | **CIOS-ORCH** | handoff · dispatch window · interruption guard | ENGINE-BEARING | `E-15`, `E-16`, `E-17` | `PL-B` |
| `SS-08` | **CIOS-DAG** | dependency admission · acyclicity | ENGINE-BEARING | `E-08` | `PL-A` |
| `SS-09` | **CIOS-KG** | knowledge recurrence · canonical home | ENGINE-BEARING | `E-03`, `E-04` | `PL-A` |
| `SS-10` | **CIOS-DT** | digital twin projection | **BINDING-ONLY** | — | — |
| `SS-11` | **CIOS-RCV** | checkpoint · recovery · continuity | **BINDING-ONLY** | — | — |
| `SS-12` | **CIOS-OBS** | observation · findings | ENGINE-BEARING | `E-22`, `E-23`, `E-24` | `PL-D` |
| `SS-13` | **CIOS-EI** | engineering intelligence · truth · traceability | ENGINE-BEARING | `E-20`, `E-21` | `PL-C` |
| `SS-14` | **CIOS-GI** | governance intelligence · impact · override | ENGINE-BEARING | `E-09`, `E-18` | `PL-A`, `PL-B` |
| `SS-15` | **CIOS-VI** | validation intelligence · overlap · duplication | ENGINE-BEARING | `E-05`, `E-06` | `PL-A` |
| `SS-16` | **CIOS-CI** | certification intelligence | **BINDING-ONLY** | — | — |
| `SS-17` | **CIOS-EVO** | evolution intelligence | **BINDING-ONLY** | — | — |

---

## 3. SUBSYSTEM SPECIFICATIONS

Each subsystem declares the ten required fields. **Owned Objects** means *declaration slots this subsystem's engines produce*, never a mechanism or a register. **Validation** and **Certification** name the located authority — no subsystem validates or certifies anything itself.

### `SS-01` · CIOS-CORE — constitutional kernel

| Field | Declaration |
|---|---|
| **Mission** | Hold the partition algebra: admit an object into the work set and seal it out of it, such that `CIOS-INV-01` (disjoint, exhaustive partitions) and `CIOS-INV-03` (sealed items byte-identical) hold at all times. |
| **Responsibilities** | `E-10` — the sole `PT-00 → PT-03` transition. `E-19` — the sole `PT-02 → PT-01` transition. Reject every other transition. |
| **Scope** | The two partition transitions CIOS owns, and nothing else. It does **not** own `PT-03 → PT-02` (that is the located Execution Queue's effect via `SS-07` handoff), nor the retry edge `FAILED → READY` (`IEC-001` `06`). |
| **Public interfaces** | **none.** Ports `P-19`/`P-20` (`E-10`) and `P-37`/`P-38` (`E-19`) are internal. |
| **Dependencies** | ← `SS-15` (`E-05`, `E-06` verdicts), `SS-09`, `SS-08`, `SS-14`, `SS-02` for `E-10`'s precondition (`P-19` requires all `E-02…E-09` verdicts PASS). → `SS-05`, `SS-06`, `SS-13`. |
| **Owned objects** | `PT-03` membership record (`P-20`); `PT-01` membership record (`P-38`); `UOM-A-13` lifecycle-partition slot (`CIOS-ID-18`). |
| **Consumed objects** | verdict set of `E-02…E-09`; terminal-state events from the located execution interval; `CEP-007` freeze registry **read-only, so it is never touched** (`RC-09`). |
| **Validation** | `CEP-004` (located). Self-check `PCK-02` — partition disjointness over this mission's declaration only. |
| **Certification** | `CEP-005` (located). Ceiling `CERTIFIED-PROVISIONAL` (`VAC-01`). |
| **Future extension points** | A further partition, or a further transition, is a **data change** (`SR-8`) — but only if `CIOS-01` Art V is amended by its own owner. `SS-01` may not add one. |

### `SS-02` · CIOS-IDENTITY — identity composition

| Field | Declaration |
|---|---|
| **Mission** | Compose a complete identity record from fields produced by **located** minting authorities, and fail closed on any unresolved field. **Mint nothing.** |
| **Responsibilities** | `E-07` — compose the 22-field record; assert completeness at its declared resolution points (`CIOS-08` §5.1); reject manual assignment as a hard rejection. |
| **Scope** | Composition and completeness assertion. **Not** allocation, not correctness of a minted value, not ordering (that is `AIF-L04`), not the `id-ledger`. |
| **Public interfaces** | **none.** `P-13`/`P-14` internal. |
| **Dependencies** | ← `SS-15` (`P-12` duplication clear). → `SS-01`, `SS-08`, `SS-13`. Located: `AIF`, `REG-AUTO-001`, `00-BOOK/tools/`, `CMG-REGISTRY.json` `kinds`, `UAKOS` homes, `IMG-001` `02` family map. |
| **Owned objects** | the composed identity record instance (a **slot**, not an identifier); `UOM-A-01`, `A-02` binding statements. |
| **Consumed objects** | `CIOS-ID-01…08` minted fields (`RC-12` AIF ledger); `ID-09…17`, `ID-21`, `ID-22` resolved fields. |
| **Validation** | `CEP-004`; `ukb validate` — **inherits `UCCEP-F-006` silent schema degradation** (`CIOS-GAP-05`, `CIOS-G-05` OPEN). |
| **Certification** | `CEP-005`; ceiling `CERTIFIED-PROVISIONAL`. |
| **Future extension points** | A 23rd identity field requires a `CEP-009` III.1 change to `CIOS-01` Art X.1 (`NS-4`) — `PG-02`. New **minting authorities** may be bound by data change without touching the field count. |

### `SS-03` · CIOS-PMS — programme management · **BINDING-ONLY**

| Field | Declaration |
|---|---|
| **Mission** | Declare the single binding surface through which a programme is registered, homed, owned and rolled up — **without creating a second programme register**. |
| **Responsibilities** | Bind, read-only: the programme register (`uccep.json` `programs[]`, `PROGRAM-000001 … PROGRAM-000016`), the programme-home convention (`UCCEP-000006` §1 **P-5**), the artifact register (`CMG-REGISTRY.json` `artifacts[]`, 43), and the portfolio roll-up (`control-tower.json.portfolio`). |
| **Scope** | The binding declaration only. It registers no programme, allocates no `PROGRAM-*` identifier, and writes no register. |
| **Public interfaces** | **none — this subsystem has no engine and therefore no port.** Programmes bind the located owners **directly** (`IFL-01`, `IFL-02`, `IFL-03` in `19`). |
| **Dependencies** | Located only: `UCCEP-000000`, `UCCEP-000006`, `CMG-000001`, `REG-AUTO-001`, `GOV-INT-001` §6. No engine dependency in either direction. |
| **Owned objects** | **none.** `REG-01` is a **contract**, not a register. |
| **Consumed objects** | `uccep.json` `programs[]`; `CMG-REGISTRY.json` `artifacts[]`; `control-tower.json` `portfolio`, `programs[]`; the `00-MASTER/<PROGRAMME-ID>/` home convention. |
| **Validation** | `CEP-004`; `CK-CMG`; `CK-REG-ENFORCE`, `CK-REG-VALIDATE`. |
| **Certification** | `CEP-005`. Observed: `UCCEP-000000` `CERTIFIED-PROVISIONAL`, programmes **6/16 PASS**, blocking none. |
| **Future extension points** | A programme-management **mechanism** owned by CIOS requires (a) an engine, hence `PG-02`, and (b) a concern, hence `CIOS-G-02`. Both are OPEN and owner-held. Until then this subsystem remains BINDING-ONLY **by law, not by omission**. |

### `SS-04` · CIOS-MRS — mission (submission) registration

| Field | Declaration |
|---|---|
| **Mission** | Provide the **sole** entry point for work into the platform, and establish that a submission's context is fully assimilated before any substantive determination runs. |
| **Responsibilities** | `E-01` — accept a submission of any kind into `PT-00`, assign nothing but a provisional handle. `E-02` — obtain the located Context Assimilation verdict. |
| **Scope** | Intake and context clearance (`CIOS-S-01`, `CIOS-S-02`). **Not** knowledge recurrence (`SS-09`), not identity (`SS-02`), not admission (`SS-01`). "Mission" here means **submission** (`01` §5.2). |
| **Public interfaces** | **`CIOS-P-01` — INGRESS, public.** The single door for work into the platform. No side door, no bulk-load bypass (`CEP-001` LAW-5). `P-02`/`P-03`/`P-04` internal. |
| **Dependencies** | ← none (`SS-04` is the graph's source in `PL-A`). → `SS-09`, `SS-15`, `SS-02`, `SS-08`, `SS-14`. Located: `UCCEP-000000` `G-01`, `UAKOS` intake. |
| **Owned objects** | intake record + provisional handle (`P-02`); context verdict (`P-04`). |
| **Consumed objects** | submission descriptor; `G-01` verdict; submitter authority resolution (`AIF-L11`, `CEP-008`). |
| **Validation** | `CEP-004`; `G-01`; `CK-CLOSURE-P1`. |
| **Certification** | `CEP-005`; ceiling `CERTIFIED-PROVISIONAL`. |
| **Future extension points** | Additional submission **kinds** are a data change (`CMG-REGISTRY.json` `kinds` is the located enumeration). A second ingress port is **prohibited** (`CIOS-05` §2.1). |

### `SS-05` · CIOS-PLAN — planning

| Field | Declaration |
|---|---|
| **Mission** | Compose the next plan epoch as a staged candidate without touching the active one, and resequence only the OPEN partition. |
| **Responsibilities** | `E-11` — compose `PLAN[n+1]`, leaving `PLAN[n]` untouched. `E-13` — resequence `PT-03` **only**; never reach `PT-02` or `PT-01`. |
| **Scope** | Epoch composition and future-only realignment (Art VII.3 rows r4, r8). **Not** the backlog, waves, topological order or critical path — all `IMG-001`. **Not** the evolution model — `CEP-009`. |
| **Public interfaces** | **none.** `P-21`/`P-22`, `P-25`/`P-26` internal. |
| **Dependencies** | ← `SS-01` (`P-20`), `SS-06` (`P-24` order). → `SS-06` (`E-14` adoption). Located: `IMG-001` `03`–`09`; `CEP-009`. |
| **Owned objects** | staged candidate `PLAN[n+1]` (`P-22`); resequenced `PT-03` (`P-26`); `UOM-A-08` dependency-order projection. |
| **Consumed objects** | `PT-03` membership; `PLAN[n]` **read-only**; derived order; `IMG-001` backlog/graph/waves/order/critical path (`RC-10`). |
| **Validation** | `CEP-004`; self-check `PCK-04` (epoch isolation, `CIOS-INV-04`). **`UCCEP-F-001` bound: the located planning-closure gate has no reachable PASS state, so no measured planning verdict is obtainable through it.** |
| **Certification** | `CEP-005`; ceiling `CERTIFIED-PROVISIONAL`. |
| **Future extension points** | Realignment **triggers** are declared data. Reaching `PT-02` or `PT-01` is prohibited absolutely (`CIOS-L-19`) and no extension may acquire it. |

### `SS-06` · CIOS-SCHED — scheduling

| Field | Declaration |
|---|---|
| **Mission** | Derive a **total** order over the OPEN partition from the declared key vector, and adopt the staged epoch atomically at the located batch-cut boundary. |
| **Responsibilities** | `E-12` — evaluate `CIOS-K-01 … K-08` to a total order. `E-14` — adopt `PLAN[n+1]` at the Quiescent Adoption Point, applying it to `PT-03` only. |
| **Scope** | Order derivation and epoch adoption. **Not** batch size, tick rate, dispatch timing or the boundary definition — all `IEC-001` `05` / §4 loop. The located order `wave, family, id` is **preserved exactly** as an initial segment (`CIOS-10` §2.3). |
| **Public interfaces** | **none.** `P-23`/`P-24`, `P-27`/`P-28` internal. |
| **Dependencies** | ← `SS-01`, `SS-05`. → `SS-05`, `SS-07`. Located: `IEC-001` `04`, `05`; `IMG-001` `04`, `05`, `07`, `09`; `AIF-L04`. |
| **Owned objects** | the total order over `PT-03` (`P-24`); the adopted epoch (`P-28`); `UOM-A-13` epoch-binding input. |
| **Consumed objects** | key-vector inputs (`RC-10`); batch-cut boundary signal (`RC-11`); witnessed admission ordinal (`AIF-L04`) as the terminating key. |
| **Validation** | `CEP-004`; self-check `PCK-04` (totality, `CIOS-INV-09`). |
| **Certification** | `CEP-005`; ceiling `CERTIFIED-PROVISIONAL`. |
| **Future extension points** | Key elements may be added **between ranks 4 and 7** by data change. Ranks 1–3 are locked by located-order preservation; rank 8 is locked by the totality proof (`CIOS-10` §2.5). |

### `SS-07` · CIOS-ORCH — orchestration

| Field | Declaration |
|---|---|
| **Mission** | Hand work to the located Execution Queue, relinquish all control, hold the epoch binding for the dispatch window, and reject every attempt to interrupt dispatched work. |
| **Responsibilities** | `E-15` — hand off the head of `Q-04` and relinquish control. `E-16` — bind the item to the epoch active at dispatch until terminal state. `E-17` — reject all interruption, default-deny. |
| **Scope** | Handoff and protection. **Not** dispatch (`IEC-001` C7, EC-3 lane), not READY evaluation (`IEC-001` `03` P1–P7), not the state machine (`06`), not quality gates (`08`), not batch formation (`05`). |
| **Public interfaces** | **`CIOS-P-30` — EGRESS, public.** Handoff record to the located Execution Queue. `P-29`, `P-31`–`P-34` internal. |
| **Dependencies** | ← `SS-06`. → `SS-01` (`E-19` seal), `SS-13`. Located: `IEC-001` `04`, C5, C7, C11, `05`, `06`. |
| **Owned objects** | handoff record (`P-30`); the immutable `(item, epoch)` binding (`P-32`); interruption rejections + findings (`P-34`). |
| **Consumed objects** | head of `Q-04`; dispatch events; interruption attempts from any source. |
| **Validation** | `CEP-004`; `IEC-001` Q1–Q8 (located, in the execution interval); self-check `PCK-04` (`CIOS-INV-04`). |
| **Certification** | `CEP-005`; EC-3 certification gate (located); ceiling `CERTIFIED-PROVISIONAL`. |
| **Future extension points** | Interruption classes (`CIOS-IC-01…10`) are declared data and extensible. The **default-deny** posture is not extensible: a narrow-allow path exists only through `SS-14`'s override port. |

### `SS-08` · CIOS-DAG — dependency graph

| Field | Declaration |
|---|---|
| **Mission** | Establish that every declared dependency resolves and that admission introduces no cycle — failing closed on a **reported** cycle regardless of the validator's returned validity flag. |
| **Responsibilities** | `E-08` — dependency resolution (`CIOS-S-13`) and cycle determination (`CIOS-S-14`); emit the partial-order position consumed by `SS-06`. |
| **Scope** | Admission-time dependency determination. **Not** the graph store (`relationships.json`), not the edge vocabulary (`UKB-ADV-000`), not impact traversal (`UCI-001` Part XII), not the backlog graph (`IMG-001` `03`). |
| **Public interfaces** | **none.** `P-15`/`P-16` internal. |
| **Dependencies** | ← `SS-02` (`P-14`). → `SS-14`, `SS-06`. Located: `UCCEP-000000` `G-08`; `CK-GRAPH`; `engine/graph`. |
| **Owned objects** | dependency verdict + partial-order position (`P-16`); `UOM-A-08` dependency slot (`CIOS-ID-15`). |
| **Consumed objects** | declared dependency sets; `artifacts.json[*].dependencies`; `relationships.json`; `UCOS-RIE-DEPENDENCY-GRAPH.json`. |
| **Validation** | `CEP-004`; `G-08`; `CK-GRAPH`. **`UCCEP-F-003` bound: the located validator fails open on a reported cycle, so `CIOS-INV-05` is not machine-enforced corpus-wide** (`CIOS-G-04` OPEN). |
| **Certification** | `CEP-005`; ceiling `CERTIFIED-PROVISIONAL`. |
| **Future extension points** | New **edge types** are admissible on the located graph by data change (`16` §4). A second graph is prohibited (`GOV-INT-001` §2.6). |

### `SS-09` · CIOS-KG — knowledge graph interface

| Field | Declaration |
|---|---|
| **Mission** | Determine whether a submission's knowledge already exists, resolve recurrence to EXTEND rather than CREATE, and resolve exactly one canonical home and one owner. |
| **Responsibilities** | `E-03` — recurrence verdict `NEW \| EXTEND \| REJECT`; never resolve an unresolvable match to `NEW`. `E-04` — resolve the single `(home, owner)` pair. |
| **Scope** | Knowledge recurrence and home/owner resolution at admission. **Not** the knowledge graph store, not closure regeneration (`IEC-001` `07` / C10 / RG-3), not home creation or reassignment — a pre-existing duplicate home is a **finding**, never repaired here. |
| **Public interfaces** | **none.** `P-05`–`P-08` internal. |
| **Dependencies** | ← `SS-04` (`P-04` PASS). → `SS-15`, `SS-02`, `SS-01`. Located: `UAKOS-CLOSURE-002` charter + `closure.json`; `CK-CLOSURE-P1/P2`; `G-02`, `G-03`, `G-06`. |
| **Owned objects** | recurrence verdict (`P-06`); resolved `(home, owner)` (`P-08`); `UOM-A-05`, `A-06` bindings (`CIOS-ID-11`, `ID-12`). |
| **Consumed objects** | `closure.json` (`CLOSED`, 434 concepts, `gap_total = 0`); the UAKOS canonical-home register (`RC-05`); `relationships.json`. |
| **Validation** | `CEP-004`; `G-02`, `G-03`, `G-06`; `CK-CLOSURE-P1`, `CK-CLOSURE-P2`. |
| **Certification** | `CEP-005`; ceiling `CERTIFIED-PROVISIONAL`. |
| **Future extension points** | Recurrence **dispositions** beyond `NEW`/`EXTEND` would require a `UAKOS` charter change by its owner. `CREATE` for recurring knowledge is prohibited absolutely (`CIOS-L-08`). |

### `SS-10` · CIOS-DT — digital twin · **BINDING-ONLY**

| Field | Declaration |
|---|---|
| **Mission** | Declare the single binding surface for the derived, projected state of the platform — **without creating a second twin or any new persistence**. |
| **Responsibilities** | Bind, read-only: `twin.json` + `signals.json` (`RC-*` class; `GOV-INT-001` §6.2 register 4), `UMB-002` Digital Twin Architecture, `UCOS-ADV-000015` Digital Twin Certification Architecture, `UCOS-RIE-DIGITAL-TWIN.json`, `control-tower.json` dimensions. |
| **Scope** | The binding declaration only. It projects nothing, persists nothing, and asserts no twin state. |
| **Public interfaces** | **none — no engine, no port.** Programmes bind the located twin **directly** (`IFL-07`). |
| **Dependencies** | Located only: `REG-AUTO-001`; `UKB-ADV`; `UMB-002`; `intelligence/rie`. |
| **Owned objects** | **none.** |
| **Consumed objects** | `twin.json`; `signals.json`; `UCOS-RIE-DIGITAL-TWIN.json`; `control-tower.json`. |
| **Validation** | `CEP-004`; `ukbx.py validate` / `twin --check` (located). |
| **Certification** | `CEP-005`; `UMB-017`/`UMB-018` twin certification dimension (located). |
| **Future extension points** | New twin **dimensions** are a data change owned by `REG-AUTO-001`/`UKB-ADV`. **`UCI-OPT-001` row 14 governs: the twin is derived state, never a new persistence layer.** `IP-3` forbids persisting derived intelligence as authoritative fact. |

### `SS-11` · CIOS-RCV — checkpoint · recovery · **BINDING-ONLY**

| Field | Declaration |
|---|---|
| **Mission** | Declare the single binding surface for continuity — checkpointing, session/crash resumption, repository reconciliation and lawful reach into protected work — **without creating a second checkpoint store or a rollback registry**. |
| **Responsibilities** | Bind, read-only: `MCP-007` §01 continuation contract and §03 checkpoint form; the append-only checkpoint store `00-MASTER/CHECKPOINTS/` (**32 records observed**); `MCP-002` state; `MCS-000`; the located retry edge `FAILED → READY` bounded by `MAX_RETRY` (`IEC-001` `06`); `UCOS-RECON-001`; `CEP-009` Art III migration route. |
| **Scope** | The binding declaration only. It writes no checkpoint, restores no state, and performs no rollback. |
| **Public interfaces** | **none — no engine, no port.** The lawful reach into protected or sealed work is `SS-14`'s `CIOS-P-35`, **not** this subsystem. |
| **Dependencies** | Located only: `MCP-007`, `MCP-002`, `MCS-000`, `IEC-001` `06`, `CEP-009`, `CEP-010`. |
| **Owned objects** | **none.** |
| **Consumed objects** | `00-MASTER/CHECKPOINTS/CKPT-*`; `00-MASTER/STATE/mcs-state.json`; `MCP-002` §01/§05. |
| **Validation** | `CEP-004`; `MCP-007` §04.B boot reconciliation (located). |
| **Certification** | `CEP-005`; ceiling `CERTIFIED-PROVISIONAL`. |
| **Future extension points** | **`GG-3` bound: change-intelligence registers 8–11 (`changes`/`knowledge`/`regeneration`/`rollback.json`) are absent, so register-backed rollback is unavailable** (`CIOS-GAP-12`). Their creation is `UCI-001`'s act, not this subsystem's. |

### `SS-12` · CIOS-OBS — observation

| Field | Declaration |
|---|---|
| **Mission** | Observe invariants, monotonicity and determinism, and emit a finding per breach — **writing nothing, ever**. |
| **Responsibilities** | `E-22` — evaluate `CIOS-INV-01…12` excluding `INV-10`, one finding per breach. `E-23` — observe that the certified set is monotone non-decreasing. `E-24` — observe replay determinism, excluding the witnessed ordinal. |
| **Scope** | Observation and finding emission. It repairs nothing, blocks nothing, and issues no verdict over a located concern. Inability to observe is **itself a finding** — it never reports a pass. |
| **Public interfaces** | **`CIOS-P-44`, `CIOS-P-46`, `CIOS-P-48` — EGRESS, public** (invariant, monotonicity, determinism findings). Three of the platform's eight public ports. `P-43`, `P-45`, `P-47` internal. |
| **Dependencies** | ← observes all planes; **→ nothing.** Out-degree 0 by construction (`CIOS-06` §4.2). |
| **Owned objects** | findings only. A finding is **evidence, never an act** (`PR-6`). |
| **Consumed objects** | observable state across all planes; certified set per epoch; replayed run pairs; `CK-HEALTH`, `CK-RIE-DETERMINISM`, `CK-DETERMINISM-BUILD`, `CK-SELF-*`. |
| **Validation** | `CEP-004`; `CIOS-15` three validation surfaces. |
| **Certification** | `CEP-005`; ceiling `CERTIFIED-PROVISIONAL`. |
| **Future extension points** | New observations are a data change. **Write authority may never be added** — `WS-6` fixes this plane's scope at ∅ (`SR-3`, `PL-R10`). |

### `SS-13` · CIOS-EI — engineering intelligence · truth · traceability

| Field | Declaration |
|---|---|
| **Mission** | Append the record of what became true, emit the traceability binding for it, and expose the derived engineering-intelligence surface — **appending only, never editing, never deleting**. |
| **Responsibilities** | `E-20` — append the truth record. `E-21` — emit the `id → artifact` traceability edge. Bind the located derived-intelligence surface (`intelligence/rie`) read-only. |
| **Scope** | Truth append and traceability emission. **Not** closure regeneration, not the traceability graph's ownership, not persisted intelligence — `UCI-001` `IP-3` forbids persisting predictions as fact, and `IP-6` forbids a new store. |
| **Public interfaces** | **`CIOS-P-40`, `CIOS-P-42` — EGRESS, public** (truth append record; traceability edge). `P-39`, `P-41` internal. |
| **Dependencies** | ← `SS-01` (`P-38` seal). → nothing. Located: `AIF-L08`, `L17`; `CEP-008`; `UMB-007`; `UCCEP-000000` `07`; `UAKOS` `closure.json` (append via `PL-C` only). |
| **Owned objects** | truth append record (`P-40`); traceability edge (`P-42`); `UOM-A-19` traceability slot. |
| **Consumed objects** | seal records; `relationships.json`; `intelligence/UCOS-RIE-*.json`; `MCP-006`. |
| **Validation** | `CEP-004`; `G-14`; `CK-VERIFY`. |
| **Certification** | `CEP-005`; ceiling `CERTIFIED-PROVISIONAL`. |
| **Future extension points** | New derived intelligence outputs are admissible; **persistence of them as authoritative fact is not** (`IP-3`). **`UCCEP-F-002` bound: traceability closure is not claimable — `P-42` failure marks an item traceability-incomplete and does not block the seal.** |

### `SS-14` · CIOS-GI — governance intelligence

| Field | Declaration |
|---|---|
| **Mission** | Produce the impact assessment and single change classification for every submission, and adjudicate the **only** lawful reach into protected or sealed work. |
| **Responsibilities** | `E-09` — `CEP-009` III.1 impact assessment; exactly one primary change class (IV.6); constitution and architecture admission determinations. `E-18` — admit an override **only** from `CIOS-OR-01` or `CIOS-OR-02` under declared, evidenced, recorded protocol; an unrecorded override is **void**. |
| **Scope** | Impact, classification, governance admission, override adjudication. **Not** the governance rules themselves (all 33 `GR-*` are located), not the evolution model (`CEP-009`), not audit (`CEP-010`). |
| **Public interfaces** | **`CIOS-P-35` — INGRESS, public.** The sole override entry point, admitting exactly two located authorities. `P-17`, `P-18`, `P-36` internal. |
| **Dependencies** | ← `SS-08` (`P-16` PASS). → `SS-01`. Located: `CEP-009` III.1/IV.1/IV.6/Art III/Art XX.2; `CEP-002` Art 28; `CEP-010`; `CMG-000001`; `UCDA-000001`; `G-04`, `G-05`, `G-09`, `G-12`. |
| **Owned objects** | impact assessment + primary class (`P-18`); adjudication + **mandatory** immutable override record (`P-36`); `UOM-A-12` policy binding, `UOM-A-16` evidence binding. |
| **Consumed objects** | `ucda-decisions.json` (**64 decisions, 0 undispositioned, 205 evidence items**); `CEP-009` evolution registry; `CMG-REGISTRY.json` tiers/concerns; `control-tower.json`. |
| **Validation** | `CEP-004`; `G-04`, `G-05`, `G-09`, `G-12`; `CK-DECISION-EVIDENCE`. **`UCCEP-F-008` bound.** |
| **Certification** | `CEP-005`; ceiling `CERTIFIED-PROVISIONAL`. |
| **Future extension points** | Change classes are `CEP-009` IV.1's enumeration — extensible by its owner. **A third override authority may not be added by CIOS** (`CIOS-L-21` fixes exactly two, both located). |

### `SS-15` · CIOS-VI — validation intelligence

| Field | Declaration |
|---|---|
| **Mission** | Resolve scope overlap to a single owner before admission, and detect any second home, owner, identifier, plan, queue, gate or authority a submission would create. |
| **Responsibilities** | `E-05` — overlap resolution; unresolved overlap is a **non-admission, not a scheduling problem**, and no deferral is permitted. `E-06` — duplication detection across all breached classes. |
| **Scope** | Admission-time overlap and duplication determination. **Not** validation execution (`CEP-004`, `engine/validation`, `verify.sh`), not quality gates (`IEC-001` `08`), not repair of a pre-existing duplicate. |
| **Public interfaces** | **none.** `P-09`–`P-12` internal. |
| **Dependencies** | ← `SS-09` (`P-08`). → `SS-02`, `SS-01`. Located: `CEP-001` LAW-4; `06-DUPLICATION-AND-OVERLAP-VERIFICATION.md`; `GOV-001` Part 10; `IAC-001D` §05 Reuse Gate; `G-03`, `G-07`. |
| **Owned objects** | overlap verdict + surviving owner (`P-10`); duplication verdict + breached classes (`P-12`). |
| **Consumed objects** | admitted-item scopes; `id-ledger.json`; `artifacts.json`; `CMG-REGISTRY.json`; `closure.json` duplicate-home counters. |
| **Validation** | `CEP-004`; `G-03`, `G-07`; `CK-REG-VALIDATE`. |
| **Certification** | `CEP-005`; ceiling `CERTIFIED-PROVISIONAL`. |
| **Future extension points** | New duplication **classes** are a data change. The **fail-closed** posture is not extensible (`CIOS-L-07`). |

### `SS-16` · CIOS-CI — certification intelligence · **BINDING-ONLY**

| Field | Declaration |
|---|---|
| **Mission** | Declare the single binding surface for certification, and state the ceiling honestly — **without certifying anything**. |
| **Responsibilities** | Bind, read-only: `CEP-005`; `00-BOOK/DATA/certification.json`; `00-BOOK/REGISTRIES/CERTIFICATION-REGISTRY.md`; the EC-3 certification gate; `IEC-001` Q6/C9/P6; `G-11`; `engine/certification`; `UMB-017`/`UMB-018`; `CIOS-16`'s twelve rules and its ceiling. |
| **Scope** | The binding declaration only. **CIOS certifies nothing** (`CIOS-16` §1). |
| **Public interfaces** | **none — no engine, no port.** Programmes bind `CEP-005` and the certification register **directly** (`IFL-10`). |
| **Dependencies** | Located only: `CEP-005`, `CEP-007`, `engine/certification`, `IEC-001` `08`. |
| **Owned objects** | **none.** |
| **Consumed objects** | `certification.json`; `CERTIFICATION-REGISTRY.md`; `uccep.json` `certification`, `certification_ceiling`; `UCCEP-000000` seal `f10928ff68603bf1`. |
| **Validation** | `CEP-004`; `G-11`. |
| **Certification** | **Ceiling `CERTIFIED-PROVISIONAL`.** Active, non-provisional certification is **unavailable** corpus-wide (`CIOS-GAP-08`; 31 of 43 artifacts PROVISIONAL; `VAC-01`, `UCCEP-F-004`). |
| **Future extension points** | The ceiling lifts only on **closure of `VAC-01`** (`CIOS-G-03`), owned by the `CEP-006` ratification authority. No act of this subsystem can lift it. |

### `SS-17` · CIOS-EVO — evolution intelligence · **BINDING-ONLY**

| Field | Declaration |
|---|---|
| **Mission** | Declare the single binding surface for constitutional evolution, amendment, versioning, lineage and change intelligence — **without owning an evolution model**. |
| **Responsibilities** | Bind, read-only: `CEP-009` Art VI / XVI / XXIII.10 / XXIV (the sole evolution authority); `UCI-001` (change/version/impact/knowledge/regeneration/rollback governance); `change-ledger.json`; `intelligence/rie`; `IEC-001` `07` regeneration; `CIOS-12` future-only realignment discipline. |
| **Scope** | The binding declaration only. **CIOS owns no evolution model** (`CIOS-01` VIII.1), creates no evolution entry, and performs no amendment. |
| **Public interfaces** | **none — no engine, no port.** Programmes route change through `CEP-009` III.1 **directly** (`IFL-11`). |
| **Dependencies** | Located only: `CEP-009`, `UCI-001`, `UCI-OPT-001`, `GOV-INT-001`, `REG-AUTO-001`. |
| **Owned objects** | **none.** |
| **Consumed objects** | `CEP-009` evolution registry (`RC-08`); `change-ledger.json`; `UCOS-RIE-*` derived views. |
| **Validation** | `CEP-004`; `G-09`. |
| **Certification** | `CEP-005`; ceiling `CERTIFIED-PROVISIONAL`. |
| **Future extension points** | Every extension of the platform routes **here**: `CEP-009` III.1 with an impact assessment. `UCI-001`'s `MUST NOT EXIST` list (no `changes.json`/`knowledge.json`/`regeneration.json`/`rollback.json` as new namespaces, no second sync, no second engine) binds every future platform mission. |

---

## 4. RECONCILIATION

### 4.1 Engine partition — disjoint and exhaustive

| Subsystem | Engines | Count |
|---|---|---|
| `SS-01` CIOS-CORE | `E-10`, `E-19` | 2 |
| `SS-02` CIOS-IDENTITY | `E-07` | 1 |
| `SS-03` CIOS-PMS | — | 0 |
| `SS-04` CIOS-MRS | `E-01`, `E-02` | 2 |
| `SS-05` CIOS-PLAN | `E-11`, `E-13` | 2 |
| `SS-06` CIOS-SCHED | `E-12`, `E-14` | 2 |
| `SS-07` CIOS-ORCH | `E-15`, `E-16`, `E-17` | 3 |
| `SS-08` CIOS-DAG | `E-08` | 1 |
| `SS-09` CIOS-KG | `E-03`, `E-04` | 2 |
| `SS-10` CIOS-DT | — | 0 |
| `SS-11` CIOS-RCV | — | 0 |
| `SS-12` CIOS-OBS | `E-22`, `E-23`, `E-24` | 3 |
| `SS-13` CIOS-EI | `E-20`, `E-21` | 2 |
| `SS-14` CIOS-GI | `E-09`, `E-18` | 2 |
| `SS-15` CIOS-VI | `E-05`, `E-06` | 2 |
| `SS-16` CIOS-CI | — | 0 |
| `SS-17` CIOS-EVO | — | 0 |
| **Total** | `E-01 … E-24`, each exactly once | **24** |

| Check | Result |
|---|---|
| Engines assigned | **24 / 24** |
| Engines assigned twice | **0** |
| Engines unassigned | **0** |
| Engines created | **0** |
| Engine set identical to `CIOS-03` §2 | **YES** |

### 4.2 Class and plane reconciliation

| Class | Count | Subsystems |
|---|---|---|
| ENGINE-BEARING | **12** | `SS-01`, `SS-02`, `SS-04`, `SS-05`, `SS-06`, `SS-07`, `SS-08`, `SS-09`, `SS-12`, `SS-13`, `SS-14`, `SS-15` |
| BINDING-ONLY | **5** | `SS-03`, `SS-10`, `SS-11`, `SS-16`, `SS-17` |
| ABSENT | **0** | — |

| Plane | Engines | Subsystems drawing from it |
|---|---|---|
| `PL-A` Assimilation | 14 (`E-01…E-14`) | `SS-01`(`E-10`), `SS-02`, `SS-04`, `SS-05`, `SS-06`, `SS-08`, `SS-09`, `SS-14`(`E-09`), `SS-15` |
| `PL-B` Execution | 4 (`E-15…E-18`) | `SS-07`, `SS-14`(`E-18`) |
| `PL-C` Truth | 3 (`E-19…E-21`) | `SS-01`(`E-19`), `SS-13` |
| `PL-D` Observation | 3 (`E-22…E-24`) | `SS-12` |
| **Total** | **24** | plane-spanning subsystems: **2** (`SS-01`, `SS-14`) |

### 4.3 Port reconciliation — zero new ports

| Subsystem | Ports | Public |
|---|---|---|
| `SS-01` | `P-19`, `P-20`, `P-37`, `P-38` | 0 |
| `SS-02` | `P-13`, `P-14` | 0 |
| `SS-04` | `P-01`, `P-02`, `P-03`, `P-04` | **1** (`P-01`) |
| `SS-05` | `P-21`, `P-22`, `P-25`, `P-26` | 0 |
| `SS-06` | `P-23`, `P-24`, `P-27`, `P-28` | 0 |
| `SS-07` | `P-29` … `P-34` | **1** (`P-30`) |
| `SS-08` | `P-15`, `P-16` | 0 |
| `SS-09` | `P-05` … `P-08` | 0 |
| `SS-12` | `P-43` … `P-48` | **3** (`P-44`, `P-46`, `P-48`) |
| `SS-13` | `P-39` … `P-42` | **2** (`P-40`, `P-42`) |
| `SS-14` | `P-17`, `P-18`, `P-35`, `P-36` | **1** (`P-35`) |
| `SS-15` | `P-09` … `P-12` | 0 |
| `SS-03`, `SS-10`, `SS-11`, `SS-16`, `SS-17` | **none** | 0 |
| **Total** | **48** | **8** |

| Check | Result |
|---|---|
| Ports declared by this artifact | **0 new** — all 48 pre-exist in `CIOS-05` |
| Public ports | **8 / 8** accounted, unchanged |
| Internal ports promoted to public | **0** (`SR-5`) |
| Subsystems exposing a public port | **5** of 17 |
| Subsystems with no port at all | **5** (all BINDING-ONLY) |

### 4.4 Aggregate properties

| Property | Value |
|---|---|
| Subsystems | **17** |
| Subsystems owning a mechanism, gate, registry, identifier space or concern | **0** |
| Registries created | **0** |
| Engines / ports / stages / identity fields created | **0 / 0 / 0 / 0** |
| Subsystems with write scope ∅ | **6** (`SS-12` by `WS-6`; the 5 BINDING-ONLY by having no engine) |
| Subsystem-to-subsystem edges introduced | **0** — all consumption follows existing `CIOS-06` `DERIVES` edges (`SR-7`) |
| Duplicate responsibilities | **0** (§5) |
| Domains / technologies / vendors enumerated | **0** |

---

## 5. NO DUPLICATE RESPONSIBILITIES

Verified pairwise over every boundary where subsystem duplication is plausible. Extends `CIOS-03` §5 to subsystem scale; the engine-level separations proven there are not restated.

| Pair | Apparent overlap | Boundary that separates them |
|---|---|---|
| `SS-09` KG / `SS-15` VI | both concern "already exists" | `SS-09` asks *does this knowledge exist, and where is its one home?* (content + home). `SS-15` asks *would admitting this create a second owner/home/identifier?* (structure). Inherited from `E-03`/`E-06`. |
| `SS-05` PLAN / `SS-06` SCHED | both act on `PT-03` | `SS-05` composes and resequences (what the plan **is**); `SS-06` derives the order and adopts the epoch (what the order **is**, and **when** it takes effect). Compose ≠ order; resequence ≠ adopt. |
| `SS-06` SCHED / `SS-07` ORCH | both concern dispatch | `SS-06` ends at the adopted epoch and the total order. `SS-07` begins at the queue head and **ends at handoff**. Neither dispatches — `IEC-001` C7 does. |
| `SS-01` CORE / `SS-07` ORCH | both concern partition movement | `SS-01` owns `PT-00 → PT-03` and `PT-02 → PT-01`. `SS-07` owns **no** transition; it hands off, and the located queue's acceptance is what makes an item IN-FLIGHT. |
| `SS-01` CORE / `SS-13` EI | both act at seal | `SS-01` `E-19` moves the partition; `SS-13` `E-20`/`E-21` append truth and emit the edge. Transition ≠ record. |
| `SS-07` ORCH / `SS-14` GI | both gate reaches into protected work | `SS-07` `E-17` rejects **all** interruption (default-deny). `SS-14` `E-18` admits **only** the two located override authorities (narrow-allow). |
| `SS-11` RCV / `SS-14` GI | both concern recovery from a bad state | `SS-11` binds **continuity** (resume from persisted state; forward-only). `SS-14` adjudicates **reach into sealed/protected work**. Resuming ≠ reaching. |
| `SS-11` RCV / `SS-17` EVO | both concern rollback | `SS-11` binds session/repository recovery (`MCP-007`). `SS-17` binds constitutional change and forward-only compensation (`CEP-009`, `UCI-001`). A rollback is a **new forward change**, never a reversal (`UCI-OPT-001` row 7). |
| `SS-12` OBS / `SS-13` EI | both emit | `SS-12` emits **findings** and writes nothing. `SS-13` **appends truth** and emits traceability. Advisory ≠ append. |
| `SS-13` EI / `SS-10` DT | both derive intelligence | `SS-13` binds derived engineering views over truth. `SS-10` binds the projected twin. Both are derived; neither persists as fact (`IP-3`); their located stores are distinct (`relationships.json`/`rie` vs `twin.json`/`signals.json`). |
| `SS-15` VI / `SS-16` CI | both sound like assurance | `SS-15` acts at **admission** (overlap/duplication, `PL-A`). `SS-16` binds **certification** of realized work (located, post-execution). Disjoint intervals. |
| `SS-03` PMS / `SS-04` MRS | both "register" | `SS-03` binds the **programme** register (a work package, `WP-*`). `SS-04` intakes a **submission** (a unit of admitted work). The terminology hazard is recorded in `01` §5.2. |

**Duplicate responsibilities: 0. Conflicting subsystem definitions: 0.**

---

## 6. WHAT THIS ARTIFACT DOES NOT DO

| Not done | Located owner / reason |
|---|---|
| Create, rename, split, merge or renumber an engine | `CIOS-01` Art X.1; `PG-02` |
| Create a port, promote an internal port, or alter the public surface | `CIOS-05`; `SR-4`, `SR-5` |
| Create a subsystem registry | `CIOS-INV-12`; contract only at `07` `REG-05`; `PG-03` |
| Add a `CIOS-SS-*` family to `cios-bindings.json` | inside `IMR-003A`; `MC-01`; `PG-01` |
| Assign a mechanism, gate, registry or concern to any subsystem | `CIOS-INV-12`; `SR-2` |
| Widen any plane's write scope | `CIOS-INV-02`; `SR-3` |
| Introduce a subsystem-level dependency edge | `SR-7`; `CIOS-INV-05` |
| Define a process, service, module, package or deployment unit | `CIOS-03` §1; `MC-06` |

---

## AUTHORITY BOUNDARY (MANDATORY)

This artifact declares a subsystem set as a partition of an existing engine set. **No subsystem holds authority.** It owns no mechanism, no registry, no gate, no identifier space and no concern; it creates no engine and no port; it mints nothing and registers nothing. Every authority named is located in an instrument existing independently at `b26c5bb`; `IMR-003A` and `IMR-003A-R1` are consumed read-only and unmodified. Where this artifact and a located canonical instrument disagree, **the located instrument governs and this artifact SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `IMR-0000/02` · PROVISIONAL · ADDITIVE · DESIGN-ONLY · AUTHORITY-NEUTRAL**
