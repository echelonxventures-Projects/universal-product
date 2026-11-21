# IMR-0000/01 — CIOS PLATFORM MODEL

| Field | Value |
|---|---|
| MISSION | `IMR-0000` — CIOS Platform Foundation |
| ARTIFACT | `01` — CIOS Platform Model (**deliverable 1**) · also the resolution of *"Engineering Management Platform"* (directive capability 5) |
| ARTIFACT KIND | Architecture (`CMG-K-05`) |
| CLOSES | `00A` `RU-05` · directive capability 5 |
| AUTHORITY OF ITS OWN | **NONE.** This artifact declares a shape, not a power. Every mechanism named is a pointer to a located owner. |
| CONFLICT RULE | Located instrument governs; then `IMR-003A`; then this artifact. |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. WHAT "PLATFORM" MEANS HERE, AND WHAT IT DOES NOT

The word *platform* is load-bearing and easy to over-read. Its meaning in `IMR-0000` is fixed by four negations before any affirmation.

| A CIOS platform **is** | A CIOS platform **is NOT** |
|---|---|
| a declared decomposition of the 24 existing `CIOS-E-*` engines into named subsystems with declared surfaces | a runtime, service mesh, framework, library, SDK, control plane or deployment target |
| a **binding surface**: for each capability, the single located owner a programme must consume | an owner of the capabilities it binds |
| reusable by every future engineering programme **by reference** | instantiated per programme; there is exactly one CIOS |
| a composition instrument, additive over `IMR-003A` | a successor to, replacement of, or peer of `IMR-003A` |

**The affirmation.** The CIOS platform is *the set of declared subsystems, object model, registry contracts, lifecycle axes, interfaces and gates through which any future engineering programme is registered, planned, admitted, executed by located authorities, evidenced, validated, certified and traced — without any programme having to rediscover, redesign or duplicate any of it.*

**The load it carries.** `CIOS-01` P.2 records the problem: a repository that continuously discovers knowledge cannot be governed by an instrument that assumes the work is known. `IMR-003A` solved that for *continuity*. `IMR-0000` solves the adjacent problem: a programme that must rediscover the platform on every mission pays the discovery cost repeatedly, and each rediscovery is an opportunity to duplicate an owner. The platform model is the artifact that makes rediscovery unnecessary.

---

## 2. THE FIVE-LAYER PLATFORM MODEL

The platform is stratified into five layers. A layer may consume only downward. This is the platform's single structural rule and it is what keeps `CIOS-INV-05` (acyclicity) intact at the subsystem scale.

```
┌──────────────────────────────────────────────────────────────────────────┐
│ L5  PROGRAMME LAYER            future engineering programmes             │
│     consumes: the 8 public ports + the 12 located interfaces (19)        │
│     owns: its own work packages, missions, artifacts                     │
│     may NOT: re-implement any L1–L4 mechanism                            │
├──────────────────────────────────────────────────────────────────────────┤
│ L4  SUBSYSTEM LAYER            SS-01 … SS-17  (CIOS-CORE … CIOS-EVO)     │
│     consumes: engines, ports, located registers                          │
│     owns: NOTHING mechanical — subsystems are groupings, not owners       │
│     introduced by: IMR-0000/02   (this is the layer the corpus lacked)    │
├──────────────────────────────────────────────────────────────────────────┤
│ L3  ENGINE LAYER               CIOS-E-01 … CIOS-E-24 · CIOS-P-01 … P-48  │
│     owner: IMR-003A/03, /04, /05, /06          IMMUTABLE INPUT           │
├──────────────────────────────────────────────────────────────────────────┤
│ L2  CONSTITUTIONAL LAYER       4 planes · 4 partitions · 24 laws ·        │
│                                12 invariants · epoch model               │
│     owner: IMR-003A/01, /02                    IMMUTABLE INPUT           │
├──────────────────────────────────────────────────────────────────────────┤
│ L1  LOCATED AUTHORITY LAYER    CEP-001…010 · CMG-000001 · GOV-INT-001 ·  │
│                                REG-AUTO-001 · AIF · STATUS-001 ·         │
│                                UCI-001 · IEC-001 · IMG-001 · UAKOS ·     │
│                                UCCEP · UCDA · MCS-000/MCP-001…007        │
│     owner: each instrument, independently of CIOS   NEVER RESTATED       │
└──────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Layer rules

| ID | Rule | Basis |
|---|---|---|
| `PL-R1` | A layer consumes only **downward**. No upward or lateral dependency exists between subsystems and engines, or between L1 and anything above it. | `CIOS-06` §5.1 (the absent back-edge); `CIOS-INV-05` |
| `PL-R2` | **L1 and L2 are immutable inputs.** `IMR-0000` writes neither. | `MC-01`; `CEP-009` Art IV.3 |
| `PL-R3` | **L3 is fixed in cardinality.** 24 engines, 48 ports. Raising either requires a `CEP-009` III.1 change to `CIOS-01` Art X.1 — recorded as `PG-02`, not performed. | `CIOS-01` Art X.1; `NS-4` |
| `PL-R4` | **L4 owns no mechanism.** A subsystem is a *name for a set of engines plus a declared binding set*. It holds no gate, registry, identifier space or concern. | `CIOS-INV-12`; `MC-08` |
| `PL-R5` | **L5 binds L4's declared surface only.** A programme that binds an internal port has bound something CIOS does not guarantee. | `CIOS-05` §2 |
| `PL-R6` | No layer may introduce a second owner for a capability owned at a lower layer. | `CEP-001` LAW-4; `CIOS-L-09` |
| `PL-R7` | The platform enumerates no domain, technology, vendor, language, protocol or format at any layer. | `CIOS-L-22` |

### 2.2 Why exactly one layer is new

| Layer | Pre-existing at `b26c5bb`? | `IMR-0000`'s act |
|---|---|---|
| L1 | **YES** — every instrument located and canonical | bind read-only |
| L2 | **YES** — `IMR-003A/01`, `/02` | bind read-only |
| L3 | **YES** — `IMR-003A/03`–`/06` | bind read-only; **partition** in `02` |
| **L4** | **NO** — genuinely absent (`00A` `PGAP-01`) | **declare** |
| L5 | **YES** as a practice (`IMR-001`, `IMR-003A`, `UAKOS-*`, `UCCEP-*` are L5 programmes) | give it a catalogue to bind (`19`) |

**One new layer, and it owns nothing.** That is the entire structural footprint of this mission. Every other artifact of `IMR-0000` either populates L4's declaration or documents an L1–L3 binding.

---

## 3. THE PLATFORM'S FOUR PLANES ARE UNCHANGED

The platform does not introduce a plane. Subsystems inherit plane membership from their engines, and a subsystem's write scope is the **union** of its engines' plane scopes — never wider.

| Plane | Function | Write scope | Subsystems drawing engines from it |
|---|---|---|---|
| `CIOS-PL-A` Assimilation | prepare future work | OPEN partition + own operational memory | `SS-01`, `SS-02`, `SS-04`, `SS-05`, `SS-06`, `SS-08`, `SS-09`, `SS-14`, `SS-15` |
| `CIOS-PL-B` Execution | realize present work | IN-FLIGHT state; Truth only via `PL-C` | `SS-07`, `SS-14` |
| `CIOS-PL-C` Truth | record what became true | append-only to Repository Truth | `SS-01`, `SS-13` |
| `CIOS-PL-D` Observation | measure and report | **nothing**; emits findings only | `SS-12` |

| ID | Rule | Basis |
|---|---|---|
| `PL-R8` | A subsystem's write scope is the union of its engines' plane scopes. It may never exceed it. | `CIOS-INV-02`; `WS-1 … WS-9` |
| `PL-R9` | A subsystem spanning two planes (`SS-01`, `SS-14`) does **not** merge them: each of its engines retains its own plane and its own scope. Spanning is a naming convenience, never a scope widening. | `CIOS-03` §4 "Single plane" |
| `PL-R10` | `SS-12` (`CIOS-OBS`) has write scope **∅** and out-degree 0. | `PR-5`; `WS-6` |

**Plane-spanning subsystems are recorded, not hidden.** Exactly two of seventeen span planes: `SS-01` `CIOS-CORE` (`E-10` in `PL-A`, `E-19` in `PL-C`) and `SS-14` `CIOS-GI` (`E-09` in `PL-A`, `E-18` in `PL-B`). Both are recorded in `02` with their per-engine scopes stated separately, so no reader can infer a widened scope from the grouping.

---

## 4. WHAT THE PLATFORM GOVERNS, AND WHO OWNS EACH PART

The instruction lists twelve platform concerns. Each resolves to a located owner; the platform's contribution is the **binding**, never the mechanism.

| Concern | Located owner (L1/L2/L3) | Platform subsystem (L4) | `IMR-0000` artifact |
|---|---|---|---|
| programme management | `uccep.json` `programs[]` · `UCCEP-000006` P-5 · `CMG-REGISTRY.json` `artifacts[]` | `SS-03` `CIOS-PMS` | `07` `REG-01` |
| mission management | mission-registration convention · `CIOS-07` stages · `E-01`, `E-02` | `SS-04` `CIOS-MRS` | `07` `REG-02` |
| identity | `AIF` · `REG-AUTO-001` · `id-ledger.json` · `E-07` | `SS-02` `CIOS-IDENTITY` | `05` |
| planning | `IMG-001` `03`–`09` · `CIOS-11`, `CIOS-12` · `E-11`, `E-13` | `SS-05` `CIOS-PLAN` | `10` |
| scheduling | `IEC-001` `04`, `05` · `CIOS-10` · `E-12`, `E-14` | `SS-06` `CIOS-SCHED` | `11` |
| orchestration | `IEC-001` C1–C12 · `GOV-INT-001` SECTION 8 · `E-15`–`E-17` | `SS-07` `CIOS-ORCH` | `12` |
| dependency management | `engine/graph` · `relationships.json` · `CIOS-06` · `E-08` | `SS-08` `CIOS-DAG` | `09` |
| checkpointing | `MCP-007` §03 · `00-MASTER/CHECKPOINTS/` | `SS-11` `CIOS-RCV` | `13` |
| recovery | `MCP-007` · `IEC-001` `06` retry · `CEP-009` Art III · `E-18` | `SS-11` `CIOS-RCV` | `14` |
| validation | `CEP-004` · `engine/validation` · `CIOS-15` · `E-05`, `E-06` | `SS-15` `CIOS-VI` | `20` |
| certification | `CEP-005` · `certification.json` · `CIOS-16` | `SS-16` `CIOS-CI` | `20` |
| governance | `CMG-000001` · `CEP-002` · `GOV-INT-001` · `CIOS-14` · `E-09`, `E-18` | `SS-14` `CIOS-GI` | `15` |
| traceability | `CEP-008` · `relationships.json` · `MCP-006` · `CIOS-17` · `E-21` | `SS-13` `CIOS-EI` | `21` |

**Zero rows have no owner. Zero rows have two owners.** That is the platform model's substantive claim, and it is checked in `20` (`PCK-05`) and traced in `21`.

---

## 5. "ENGINEERING MANAGEMENT PLATFORM" — VOCABULARY RESOLUTION

The Context Assimilation Directive names an **Engineering Management Platform** as required capability 5. No such token exists at `b26c5bb`.

### 5.1 Determination

| Question | Determination |
|---|---|
| Is `EMP` (or any equivalent token) allocated? | **NO** |
| Why not? | Allocating a second token for a subject matter that already has one breaches `CEP-001` LAW-4 (Single Canonicity), `CIOS-L-09` (Zero Duplication), `GOV-001` Part 10 (no parallel identifier system), `IMR-003A` `AC-3`, and `NS-1`. It is the identical act refused for `UAES` by `IMR-003A-R1/10` §2. |
| What does the capability resolve to? | **The CIOS platform as composed in §2 and §4 of this artifact** — specifically the programme/mission subsystems (`SS-03`, `SS-04`) together with the planning, scheduling and orchestration subsystems (`SS-05`, `SS-06`, `SS-07`) over the located authorities `IMG-001`, `IEC-001`, `UCCEP-000006` P-5 and `MCS-000`. |
| Is the capability therefore missing? | **NO.** It is `PRESENT UNDER ANOTHER NAME` (`00A` Output 2, row 5). |

### 5.2 Vocabulary resolution table

Extends `IMR-003A-R1/10` §3 in form. The left column may appear in instructions and conversation; **only the right column may appear as a repository identifier.**

| Directive / instruction vocabulary | Resolves to (repository truth) | Located home |
|---|---|---|
| "Engineering Management Platform" | the **CIOS platform** — L1–L4 of §2, bound through `SS-03`…`SS-07` | `00-MASTER/IMR-003A/` + `00-MASTER/IMR-0000/` |
| "Universal Programme Management Foundation" | the same platform, viewed from `SS-03` `CIOS-PMS` | `07` `REG-01` |
| "platform capability" | a **subsystem** (`SS-*`) binding located mechanisms — never a new mechanism | `02` |
| "Engineering Intelligence" | `SS-13` `CIOS-EI` binding `intelligence/rie`, `CEP-008`, `relationships.json` | `18` §2 |
| "Governance Intelligence" | `SS-14` `CIOS-GI` binding `CMG-000001`, `CEP-002`, `CEP-010`, `UCDA-000001` | `18` §3 |
| "Evolution Intelligence" | `SS-17` `CIOS-EVO` binding `CEP-009`, `UCI-001`, `change-ledger.json` | `18` §4 |
| "registry" (in this mission) | a **read contract** over a located register — never a new store | `07` |
| "platform freeze" / "Architecture Freeze" | a **declaration-scoped Architecture Stability Contract**; **not** a `CEP-007` freeze | `22`, `25` |
| "mission" (unit of admitted work) | **submission** (`CIOS-01` Art V) | `IMR-003A-R1/10` §3 |
| "mission" (programme work package) | `WP-<PROGRAMME-ID>` under `00-MASTER/<PROGRAMME-ID>/` | `UCCEP-000006` P-5 |

**Terminology hazard, restated because it recurs.** "Mission" denotes both a programme (`IMR-0000`) and a unit of admitted work. CIOS artifacts use **submission** for the latter. `SS-04` is named `CIOS-MRS` — *Mission Registration Subsystem* — and governs **submissions**; its name is retained because the instruction fixes it, and the hazard is recorded here rather than resolved by renaming.

---

## 6. PLATFORM PROPERTIES

| Property | Value | Basis |
|---|---|---|
| Layers | **5** | §2 |
| Layers newly declared by `IMR-0000` | **1** (L4) | §2.2 |
| Planes | **4** — unchanged | `CIOS-01` Art IV |
| Partitions | **4** — unchanged | `CIOS-01` Art V |
| Engines | **24** — unchanged | `CIOS-01` Art X.1 |
| Ports | **48**, of which **8** public — unchanged | `CIOS-05` |
| Subsystems | **17** | `02` |
| Subsystems owning a mechanism | **0** | `PL-R4`; `CIOS-INV-12` |
| Registries created | **0** | `07` §5 |
| Identifiers minted | **0** | `CIOS-L-14` |
| Tokens allocated | **0** | §5.1; `NS-1` |
| Concerns claimed in `CMG-REGISTRY.json` | **0** | `CIOS-G-02` OPEN |
| Gates owned | **0** | `CIOS-01` I.6 |
| Located capabilities with two owners | **0** | §4 |
| Located capabilities with no owner | **0** | §4 |
| Domains / technologies / vendors enumerated | **0** | `CIOS-L-22` |
| Executable artifacts produced | **0** | `MC-05` |
| Reversibility | **complete** — deleting `00-MASTER/IMR-0000/` restores `b26c5bb` | `00` §1 |

---

## 7. WHAT THE PLATFORM MODEL DOES NOT DO

| Not done | Located owner / reason |
|---|---|
| Replace, subordinate or supersede `IMR-003A` | `MC-01`; `CIOS-01` I.3 |
| Confer supremacy on CIOS or on the platform | `CIOS-G-01`, `CIOS-G-02` **OPEN**; `CEP-009` I.5 |
| Add, remove or renumber an engine, port, stage, partition, plane or identity field | `CIOS-01` Art X.1; `PG-02` |
| Define a process, service, daemon, thread or deployment unit | `CIOS-03` §1; `MC-06` |
| Define a runtime, execution engine or orchestration executable | `MC-05`; `IEC-001` owns execution |
| Authorize dispatch or execution | `IEC-001` C7 (EC-3 lane); `CMG` T4 |
| Claim validation, certification, ratification or freeze | `CEP-004`/`005`/`006`/`007`; `VAC-01`; `D-3`, `D-4` |
| Assert readiness for implementation missions | deferred to `24`; `D-6` |

---

## AUTHORITY BOUNDARY (MANDATORY)

This artifact declares a layered platform shape and a vocabulary resolution. It owns no mechanism, no registry, no gate, no identifier space and no concern. It allocates no token and mints nothing. Every authority named is located in an instrument existing independently at `b26c5bb`; `IMR-003A` and `IMR-003A-R1` are consumed read-only and unmodified. Where this artifact and a located canonical instrument disagree, **the located instrument governs and this artifact SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `IMR-0000/01` · PROVISIONAL · ADDITIVE · DESIGN-ONLY · AUTHORITY-NEUTRAL**
