# IMR-0000 — CIOS PLATFORM FOUNDATION · MISSION REGISTRATION RECORD

| Field | Value |
|---|---|
| MISSION | `IMR-0000` — CIOS Platform Foundation · Universal Programme Management Foundation |
| WORK PACKAGE | `WP-IMR-0000` |
| MISSION TYPE | CONSTITUTIONAL PLATFORM ARCHITECTURE |
| MISSION MODE | **DESIGN ONLY** — no implementation, no runtime, no execution engine, no code generation, no repository refactor |
| SUBJECT TOKEN | **`CIOS`** — reused, not re-allocated (`NS-1`) |
| MISSION HOME | `00-MASTER/IMR-0000/` (programme-owned; registration-excluded per `00-BOOK/tools/config.py :: EXCLUDE_DIR_PREFIXES → "00-MASTER/"`) |
| HOME CONVENTION | `UCCEP-000006` §1 **P-5** — programme-owned work-package register under `00-MASTER/<PROGRAMME-ID>/` |
| AUTHORITY BASIS | Repository Truth (`UAKOS-CLOSURE-002` `CLOSED`) · `IMR-003A` + `IMR-003A-R1` (COMPLETE, immutable inputs) · `CEP-009` (admission route) · `CEP-001` (supreme operational) · `CMG-000001` (meta-governance) · `GOV-INT-001` §6 / §7.2 / SECTION 8 |
| AUTHORITY OF ITS OWN | **NONE.** `IMR-0000` is a composition-and-specification instrument. It legislates no mechanism, owns no registry, no gate, no identifier space and no concern. |
| BASELINE | `b26c5bb66c37717fe4eb96552bad4b9d8b74d890` (`b26c5bb`) · branch `programme/evo-usis-005` |
| STANDING | **PROVISIONAL** (`CMG-L-12`) · Tier T1 **VACANT** (`VAC-01`) · not validated under `CEP-004` · not certified active under `CEP-005` · not ratified under `CEP-006` · **not frozen** and **not freezable** under `CEP-007` (`CIOS-GAP-13`) |
| CONFLICT RULE | Where `IMR-0000` and a located canonical instrument conflict, **the located instrument governs and `IMR-0000` SHALL be corrected** (`CEP-001` LAW-1, LAW-4). Where `IMR-0000` and `IMR-003A` conflict, **`IMR-003A` governs**. |
| DATE | 2026-07-27 |

---

## SECTION 0 — WHAT THIS MISSION IS

**0.1** `IMR-003A` (recovered and completed by `IMR-003A-R1`) established **CIOS** — the Continuous Implementation Operating System — as a composition instrument governing the *continuity* of implementation: four planes, four partitions, 24 laws, 12 invariants, 24 engines, 48 ports, 24 admission stages, 22 identity fields, 4 queues, 8 priority key elements, 2 override authorities, 7 undischarged gates, 14 gaps.

**0.2** What `IMR-003A` did **not** do is give that engine set a **platform shape**: a declared decomposition into subsystems, a universal object model that reaches objects other than submissions, a registry framework, a uniqueness principle stated as law-with-located-enforcers, and a public catalogue that tells a future programme exactly which surface to bind.

**0.3** `IMR-0000` supplies that shape and nothing else. It is a **structuring mission**, not a capability mission. Its entire contribution is:

| Contribution | Why it is not a duplication |
|---|---|
| A **subsystem decomposition** of the existing 24 engines into 17 declared subsystems | `IMR-003A/03` declares engines and planes; no located instrument groups them into subsystems with declared public surfaces |
| A **Universal Object Model** over *canonical objects* | `CIOS-08` models the **submission** (22 fields). No located instrument states the attribute set every canonical object inherits, or maps each attribute to its located owner |
| The **Universal Uniqueness Principle** as seven singularity clauses, each bound to a located enforcer | The seven singularities exist severally (`CEP-001` LAW-4, `AIF-L02/L07/L17`, `UAKOS` homes, `CEP-008`); no instrument states them as one closed principle |
| A **Canonical Registry Framework** — the admissibility test a register must satisfy to be canonical | `GOV-INT-001` §6 owns the registry *architecture*; `IMR-003A-R1/07` owns CIOS's 14 read contracts. The **conformance test** is derived from both and stated nowhere |
| A **Lifecycle axis reconciliation** — the four orthogonal lifecycle axes and which governs what | Four lifecycle models exist (`REG-AUTO-001` §5, `IEC-001` `06`, `CIOS-PT-*`, `CIOS-S-*`). Their orthogonality is asserted pairwise in three places and never reconciled in one |
| A **Public Interface Catalogue** stating the total consumable surface of the platform | `CIOS-05` §2 declares 8 public ports; the located surfaces a programme must bind *directly* are listed in `CIOS-05` §5 as prose. The catalogue unifies both into one binding table |
| A **Traceability Matrix** over this mission's own deliverables | required by `CEP-008`; scoped to `IMR-0000` |

**0.4** Everything else in this mission is a **pointer**. Where a capability the instruction names already has a located owner, `IMR-0000` binds it read-only and restates nothing (Knowledge Once, `CIOS-L-08`). Where it has no located owner, `IMR-0000` **records a gap with a named prospective owner and an unblocking gate** — it does not invent the mechanism (`CIOS-03` §1.1 ABSENT discipline).

---

## SECTION 1 — MISSION CONSTRAINTS, AS ACCEPTED

The instruction's prohibitions are adopted verbatim as mission law, and each is bound to the located instrument that already enforces it.

| ID | Constraint | Located enforcer |
|---|---|---|
| `MC-01` | **`IMR-003A` SHALL NOT be modified.** No file under `00-MASTER/IMR-003A/` or `00-MASTER/IMR-003A-R1/` is written, edited, moved or superseded. | `CEP-009` Art IV.3; `AIF-L17` |
| `MC-02` | **CIOS SHALL NOT be renamed.** The subject token remains `CIOS`. | `IMR-003A-R1/10` `NS-1` |
| `MC-03` | **No duplicate constitutional identity.** No second subject token, home, owner, identifier space, plan, queue, gate or authority for anything that has one. | `CEP-001` LAW-4; `CIOS-L-09`; `GOV-001` Part 10 |
| `MC-04` | **No duplicated knowledge.** Located content is bound by pointer, never restated. | `CIOS-L-08`; `UAKOS-CLOSURE-002` charter |
| `MC-05` | **No runtime implementation, no executable orchestration, no code generation.** This mission produces specification text and one data-only declaration. | mission mode; `AC-12` precedent (`IMR-003A`) |
| `MC-06` | **No implementation agents, no deployment architecture, no infrastructure bindings.** | `CIOS-L-22` (Zero Enumeration) |
| `MC-07` | **No alternative constitutional platform.** Every platform capability is introduced as a **CIOS subsystem**, never as a peer of CIOS. | instruction; `CEP-001` LAW-4 |
| `MC-08` | **No self-conferred authority.** No subsystem, framework, registry specification or catalogue entry in this mission holds authority. | `CEP-009` I.5; `CIOS-L-11`; `CIOS-INV-12` |
| `MC-09` | **No repository refactor.** No corpus file outside `00-MASTER/IMR-0000/` is written. | `CIOS-13` §1.1; `WS-1 … WS-9` |
| `MC-10` | **Zero enumeration.** No domain, industry, science, vendor, cloud, platform, language, protocol, format, database or infrastructure is enumerated. | `CIOS-L-22`; `CK-SELF-NO-ENUMERATION` |

**Reversibility.** As with `IMR-003A`, deleting `00-MASTER/IMR-0000/` restores `b26c5bb` exactly. No located instrument depends on `IMR-0000`.

---

## SECTION 2 — IMMUTABLE ARCHITECTURAL INPUTS

Consumed **read-only**. None is altered, extended in place, or reinterpreted.

| Input | What is consumed | Alterable by this mission? |
|---|---|---|
| `IMR-003A/01-CIOS-CONSTITUTION.md` | 24 laws · 12 invariants · 4 planes · 4 partitions · epoch model · Art VII.3's nine authorized contributions · Art X.1 numeric contract | **NO** |
| `IMR-003A/02-CIOS-OPERATING-MODEL.md` | write scopes `WS-1 … WS-9`; degradation semantics | **NO** |
| `IMR-003A/03-CIOS-ENGINE-ARCHITECTURE.md` | the 24 engines `CIOS-E-01 … E-24`; binding classes BOUND / COMPOSING / ABSENT | **NO** |
| `IMR-003A/04-CIOS-ENGINE-RESPONSIBILITIES.md` | per-engine OWNS / CONSUMES / PRODUCES / EXCLUDES / FAIL | **NO** |
| `IMR-003A/05-CIOS-ENGINE-INTERFACES.md` | 48 ports; the **8-port public surface**; port rules `PR-1 … PR-8` | **NO** |
| `IMR-003A/06-CIOS-ENGINE-DEPENDENCIES.md` | 25 `DERIVES` edges; acyclicity; the absent back-edge | **NO** |
| `IMR-003A/07-CIOS-LIFECYCLE-MODEL.md` | 24 admission stages; 14 located gates bound; transition rules `LT-1 … LT-8` | **NO** |
| `IMR-003A/08-CIOS-IDENTITY-MODEL.md` | the 22-field Canonical Submission Object; `IDR-1 … IDR-7` | **NO** |
| `IMR-003A/09` · `10` · `11` · `12` | queues `Q-01…04`; key vector `K-01…08` + wave successor; interruption classes + override authorities; future-only realignment | **NO** |
| `IMR-003A/13 … 17` | registry / governance / validation / certification / traceability integration models | **NO** |
| `IMR-003A/18 … 20` | impact assessment; `CIOS-G-01…G-07`; `CIOS-GAP-01…GAP-14`; Art X.1 verification | **NO** |
| `IMR-003A/cios-bindings.json` | 35 located binding paths — **the sole lawful extension surface of CIOS**, and it is **not written by this mission** | **NO** |
| `IMR-003A-R1/05` · `06` · `07` | dependency matrix (35 bindings) · interface matrix · **14 registry contracts, all read-only** | **NO** |
| `IMR-003A-R1/09` · `10` · `11` | Architecture & Interface Stability Contract v1.0 · namespace reconciliation `NS-1…NS-5` · completion report | **NO** |

**Observed Repository Truth at mission start** (session-boot evidence, not this mission's claim):

| Source | Observation |
|---|---|
| `UAKOS-CLOSURE-002` | `CLOSED` · `concept_total = 434` · `gap_total = 0` · all seven gap classes zero |
| `UCCEP-000000` | `CERTIFIED-PROVISIONAL` · tier `boot` · gates 6/14 PASS · programmes 6/16 PASS · blocking none · seal `f10928ff68603bf1` |
| `UCDA-000001` | `ASSIMILATED` · decisions 64 · undispositioned 0 · evidence 205 · gate OPEN · seal `8d34d196a80a05b8` |
| `git` | `b26c5bb` · branch `programme/evo-usis-005` |

---

## SECTION 3 — NAMESPACE DECLARATION

### 3.1 No token is allocated

| Question | Determination | Basis |
|---|---|---|
| Does `IMR-0000` allocate a subject token? | **NO** | `NS-1` — no second token for CIOS's subject matter |
| Does it request a `CMG-REGISTRY.json` namespace? | **NO** | `CIOS-INV-12`; `CIOS-G-02` is the gate that would admit a CIOS concern, and it is **OPEN** |
| Does it request an identifier family from `REG-AUTO-001`? | **NO** | `NS-3` |
| Does it consume corpus identity? | **NO** | `00-BOOK/tools/config.py` excludes `00-MASTER/` |
| Does it write `cios-bindings.json`? | **NO** | `MC-01` — that file is inside `IMR-003A` |
| Does it add a member to any `CIOS-*` family? | **NO** | see §3.3 |

### 3.2 Mission-local declaration families

`IMR-0000` declares its content in **mission-local families**, precedented by `IMR-003A-R1`'s use of `NS-*`, `RC-*`, `V-*`, `U-*`, `R1-F-*`, `RAC-*`, `CP-*`. A mission-local family is a set of **slots in a programme-scoped declaration**. It is not a corpus identifier, is absent from `id-ledger.json`, `artifacts.json` and `CMG-REGISTRY.json`, and may **never** be presented to `REG-AUTO-001`.

| Family | Meaning | Cardinality | Fixed by |
|---|---|---|---|
| `MC-*` | mission constraint | **10** | §1 |
| `AC-*` | acceptance criterion | **14** | §5 |
| `SS-*` | CIOS subsystem | **17** | instruction; `02` |
| `UOM-A-*` | universal object attribute | **19** | instruction; `03` |
| `UOM-R-*` | object model rule | **9** | `03` |
| `UUP-*` | uniqueness clause | **9** | instruction; `04` |
| `RF-*` | registry framework rule | **8** | `07` |
| `REG-*` | canonical registry specification | **11** | instruction; `07` |
| `LX-*` | lifecycle axis | **4** | `08` |
| `LR-*` | lifecycle framework rule | **7** | `08` |
| `IF-*` | public interface catalogue entry | **8** | `18` |
| `IFL-*` | located interface a programme binds directly | **12** | `18` |
| `ASC-*` | stability contract clause | **10** | `19` |
| `TM-*` | traceability matrix row | **30** | `20` |
| `PCK-*` | declared platform self-check (**declared, not implemented**) | **12** | `21` |
| `PG-*` | platform gate — undischarged, externally owned | **9** | `22` |
| `PF-*` | platform finding | **7** | `22` |
| `PGAP-*` | platform gap | **11** | `22` |

### 3.3 Why no `CIOS-*` family is extended

Two of the instruction's requirements would, on a literal reading, extend a `CIOS-*` family:

| Literal reading | Why it is refused | What is done instead |
|---|---|---|
| Declare subsystems as `CIOS-SS-01 … CIOS-SS-17` | `IMR-003A` OUTPUT 0.4 allocated **thirteen** `CIOS-*` families. A fourteenth family is a **namespace extension**, and the sole lawful extension surface (`cios-bindings.json`) is inside `IMR-003A`, which `MC-01` forbids writing. | Subsystems carry **mission-local identity** `SS-01 … SS-17` and **canonical name** `CIOS-CORE … CIOS-EVO`. This is the Universal Uniqueness Principle applied to itself: identity is immutable and mission-scoped; the name is the CIOS-facing label (`UUP-08`, `UUP-09`). Admission of a `CIOS-SS-*` family to `cios-bindings.json` is gate `PG-01`, owned by the located owner of that file. |
| Add gates to `CIOS-G-*` | `CIOS-19` §1.1 records *"Gates declared: 7"*. Adding an eighth member would falsify a count recorded in an artifact this mission may not modify. | Platform gates are declared as `PG-01 … PG-09` in `22`. `CIOS-G-01 … G-07` are inherited **unchanged and undischarged**. |

**Nothing in `IMR-0000` alters a cardinality fixed by `CIOS-01` Art X.1** (24 engines / 24 stages / 22 identity fields), nor any count recorded by `IMR-003A` or `IMR-003A-R1`. `NS-4` is satisfied by non-participation.

### 3.4 Mission identifier provenance

| Observation | Disposition |
|---|---|
| Family `IMR` members at `b26c5bb` are `IMR-001`, `IMR-003A`, `IMR-003A-R1` — three-digit ordinals. `IMR-0000` is four-digit. | Recorded as **disclosed provenance**, not a gap. The mission identifier is fixed by the commissioning instruction; renaming it would breach `AIF-L07`/`CIOS-L-13` if the identifier is treated as minted, and would contradict the instruction if it is not. No renaming is performed. |
| `IMR-002`, `IMR-003` are absent | Pre-existing sequence discontinuity, already recorded by `IMR-003A` OUTPUT 0.1 as provenance, not a gap. |
| `IMR-0000` ordinal `0000` precedes `IMR-001` numerically but **follows** `IMR-003A` causally | Recorded. Ordering authority is the **witnessed admission ordinal**, never the identifier's numeral (`CIOS-L-15`; `AIF-L04`). The numeral carries no order. |

---

## SECTION 4 — DELIVERABLE REGISTER

> **AMENDMENT NOTE (Context Assimilation Gate, 2026-07-27).** The **deliverable list** below is unchanged and remains authoritative — no deliverable was removed, renamed or merged. The **artifact filenames** it points to were renumbered when the Context Assimilation Directive seated six further capabilities (Engineering Management Platform · Engineering / Governance / Evolution Intelligence frameworks · Registry relationships · Platform implementation readiness). The authoritative deliverable→artifact map is `00A-CONTEXT-ASSIMILATION-AND-COVERAGE-DETERMINATION.md` **Output 4**. Where this section's filenames and `00A` Output 4 differ, **`00A` Output 4 governs**. This note is additive; no row below is rewritten.

Thirty required deliverables, mapped to the artifacts that carry them. One artifact may carry several deliverables where they share a single specification form — precedented by `CIOS-05` (Engine Interfaces + Public Interface Specification) and `CIOS-08` (Identity Model + Canonical Mission Object).

| # | Required deliverable | Artifact | Local family |
|---|---|---|---|
| 1 | CIOS Platform Model | `01-CIOS-PLATFORM-MODEL.md` | — |
| 2 | Universal Object Model | `03-UNIVERSAL-OBJECT-MODEL.md` | `UOM-A-*`, `UOM-R-*` |
| 3 | Canonical Registry Framework | `07-CANONICAL-REGISTRY-FRAMEWORK.md` §1–§3 | `RF-*` |
| 4 | Universal Uniqueness Principle Framework | `04-UNIVERSAL-UNIQUENESS-PRINCIPLE-FRAMEWORK.md` | `UUP-*` |
| 5 | CIOS Identity Framework | `05-CIOS-IDENTITY-FRAMEWORK.md` | — |
| 6 | CIOS Namespace Framework | `06-CIOS-NAMESPACE-FRAMEWORK.md` | — |
| 7 | Programme Registry | `07` §4 `REG-01` | `REG-01` |
| 8 | Mission Registry | `07` §4 `REG-02` | `REG-02` |
| 9 | Portfolio Registry | `07` §4 `REG-03` | `REG-03` |
| 10 | Capability Registry | `07` §4 `REG-04` | `REG-04` |
| 11 | Subsystem Registry | `07` §4 `REG-05` | `REG-05` |
| 12 | Interface Registry | `07` §4 `REG-06` | `REG-06` |
| 13 | Contract Registry | `07` §4 `REG-07` | `REG-07` |
| 14 | Dependency Registry | `07` §4 `REG-08` | `REG-08` |
| 15 | Evidence Registry | `07` §4 `REG-09` | `REG-09` |
| 16 | Validation Registry | `07` §4 `REG-10` | `REG-10` |
| 17 | Certification Registry | `07` §4 `REG-11` | `REG-11` |
| 18 | Lifecycle Framework | `08-LIFECYCLE-FRAMEWORK.md` | `LX-*`, `LR-*` |
| 19 | Dependency Graph Architecture | `09-DEPENDENCY-GRAPH-ARCHITECTURE.md` | — |
| 20 | Planning Architecture | `10-PLANNING-ARCHITECTURE.md` | — |
| 21 | Scheduling Architecture | `11-SCHEDULING-ARCHITECTURE.md` | — |
| 22 | Orchestration Architecture | `12-ORCHESTRATION-ARCHITECTURE.md` | — |
| 23 | Checkpoint Framework | `13-CHECKPOINT-FRAMEWORK.md` | — |
| 24 | Recovery Framework | `14-RECOVERY-FRAMEWORK.md` | — |
| 25 | Governance Framework | `15-GOVERNANCE-FRAMEWORK.md` | — |
| 26 | Knowledge Graph Framework | `16-KNOWLEDGE-GRAPH-FRAMEWORK.md` | — |
| 27 | Digital Twin Framework | `17-DIGITAL-TWIN-FRAMEWORK.md` | — |
| 28 | Architecture Stability Contract | `19-ARCHITECTURE-STABILITY-CONTRACT.md` | `ASC-*` |
| 29 | Public Interface Catalogue | `18-PUBLIC-INTERFACE-CATALOGUE.md` | `IF-*`, `IFL-*` |
| 30 | Traceability Matrix | `20-TRACEABILITY-MATRIX.md` | `TM-*` |
| — | CIOS Subsystem Architecture (instruction §CIOS SUBSYSTEMS) | `02-CIOS-SUBSYSTEM-ARCHITECTURE.md` | `SS-*` |
| — | Validation & Certification determination | `21-VALIDATION-AND-CERTIFICATION.md` | `PCK-*` |
| — | Gap analysis, gates, findings | `22-GAP-ANALYSIS-AND-PLATFORM-GATES.md` | `PG-*`, `PF-*`, `PGAP-*` |
| — | Completion report + Architecture Freeze | `23-MISSION-COMPLETION-AND-ARCHITECTURE-FREEZE.md` | — |
| — | Machine-readable projection (**data only, authority none**) | `imr-0000-platform-bindings.json` | — |
| — | Mission index | `README.md` | — |

---

## SECTION 5 — ACCEPTANCE CRITERIA

| ID | Criterion | Verified in |
|---|---|---|
| `AC-1` | Every one of the 30 deliverables exists and is reachable from `README.md` | `20`, `23` |
| `AC-2` | All 17 subsystems are defined with all ten required fields | `02` |
| `AC-3` | The 24 engines are partitioned across subsystems: pairwise disjoint, jointly exhaustive | `02` §4; `21` `PCK-01` |
| `AC-4` | Zero new engines, zero new ports, zero new stages, zero new identity fields | `02` §4; `18` §4 |
| `AC-5` | Zero registries created; every registry specification is a read contract or a recorded gap | `07` §5 |
| `AC-6` | Zero `CIOS-*` family members added; zero `CIOS-01` Art X.1 cardinalities altered | §3.3; `21` `PCK-03` |
| `AC-7` | Every framework rule names a **located** enforcer or is recorded as a gap with an owner | `21` `PCK-05` |
| `AC-8` | Every pointer resolves at `b26c5bb` (`CIOS-INV-11`) | `21` `PCK-06` |
| `AC-9` | No file outside `00-MASTER/IMR-0000/` is written | `21` `PCK-07` |
| `AC-10` | No domain, technology, vendor, platform, language, protocol or format is enumerated | `21` `PCK-08` |
| `AC-11` | No code, script, runtime, agent or executable orchestration is produced | `21` `PCK-09` |
| `AC-12` | Every gap and gate carries a named owner and an unblocking condition | `22` |
| `AC-13` | Internal consistency: every count declared in one artifact matches every restatement of it | `21` §3 |
| `AC-14` | The mission's terminal act is a **declaration-scoped** Architecture Stability Contract, expressly **not** a `CEP-007` freeze | `19`, `23` |

---

## SECTION 6 — DISCLOSED DIVERGENCES FROM THE INSTRUCTION

Recorded plainly. Each is a case where the literal instruction would produce a **void, duplicative or self-conferring** act under located law.

| # | Instruction | Divergence | Reason |
|---|---|---|---|
| `D-1` | *"Produce complete constitutional specifications for … Programme Registry … Certification Registry"* | The eleven registries are specified as **contracts over located registers**, not as new registers. Two (`REG-05` Subsystem, `REG-07` Contract) have **no located owner** and are specified as *contract-only with a recorded gap*, not instantiated. | `CIOS-INV-12` (CIOS owns no registry) · `CEP-001` LAW-4 · `GOV-INT-001` §6 owns the registry architecture · `IMR-003A-R1/07` §5 |
| `D-2` | *"Define the constitutional architecture for CIOS-CORE … CIOS-EVO"* | Subsystems are **groupings of the existing 24 engines**, not new mechanism owners. Five subsystems (`CIOS-PMS`, `CIOS-DT`, `CIOS-RCV`, `CIOS-CI`, `CIOS-EVO`) hold **zero engines** and are declared BINDING-ONLY. | `CIOS-01` Art X.1 fixes the engine count at 24; raising it requires a `CEP-009` III.1 change to `CIOS-01`, which `MC-01` forbids. Recorded as `PG-02`. |
| `D-3` | *"Mission ends with an Architecture Freeze for IMR-0000"* | Delivered as a **declaration-scoped Architecture Stability Contract** plus a Freeze **Declaration**, expressly **not** a `CEP-007` freeze and claiming no seal. | `CEP-007` IV.1 / V.1 / V.5 ineligibility while `VAC-01` is open; an attempt would be **void** under II.4 / IV.4 (`GD-10`; `CIOS-GAP-13`); identical divergence already recorded by `IMR-003A-R1/10` §5.2 |
| `D-4` | *"✓ validation complete"* / *"✓ certification complete"* | Delivered as **declared self-checks over this mission's own declaration** (`PCK-01 … PCK-12`) and an explicit statement that neither `CEP-004` validation nor `CEP-005` active certification is claimed or available. A self-check is not a validation. | `CIOS-15` `VR-04`; `CIOS-16` §1 ceiling; `VAC-01`; `UCCEP-F-004` |
| `D-5` | *"✓ traceability complete"* | Traceability is **complete within this mission's declaration** (30/30 deliverables traced). Corpus traceability closure is **not** claimed. | `UCCEP-F-002` (1198 artifacts traceability-incomplete); `CIOS-17` §5 bound; `CIOS-G-06` |
| `D-6` | *"platform declared ready for implementation missions"* | Declared ready for **architecture and design** missions. **Execution readiness is not declared** and is not this mission's to declare. | `CIOS-19` §4; `GG-3`, `GG-4`, `GG-6`, `IAC-001 B+C` undischarged; dispatch authority is `IEC-001` C7 in the EC-3 lane |
| `D-7` | Deliverables 1–30 as thirty artifacts | Delivered as **24 artifacts + 1 data file**, with an explicit deliverable→artifact map (§4). The eleven registries share one specification form and one artifact; splitting them would restate the form eleven times. | `CIOS-L-08` Knowledge Once; `CMG-K-04` atomicity is preserved at the **section** level |

**No divergence removes a required deliverable.** Each is a change of *form* or *claim strength*, recorded so no reader mistakes a specification for an instantiation, or a self-check for a certification.

---

## SECTION 7 — WHAT THIS MISSION DOES NOT DO

| Not done | Located owner / reason |
|---|---|
| Modify, supersede or extend `IMR-003A` / `IMR-003A-R1` | `MC-01` |
| Write `cios-bindings.json` | inside `IMR-003A`; `MC-01`. The extension **delta** is declared in `imr-0000-platform-bindings.json` as a proposal for the located owner |
| Create, write or add an entry to any registry | `CIOS-INV-12`; `IMR-003A-R1/07` §3 |
| Mint, allocate or reserve any identifier | `AIF`; `REG-AUTO-001`; `CIOS-L-14` |
| Declare, imply or record a freeze or seal | `CEP-007`; unavailable (`GD-10`, `CIOS-GAP-13`) |
| Discharge any gate or finding — CIOS's or inherited | `CIOS-01` IX.4; `CIOS-19` §1 |
| Authorize, schedule or dispatch any execution | `IEC-001` C7 (EC-3 lane); `CMG` T4 |
| Produce code, scripts, runtime, agents, deployment or infrastructure | `MC-05`, `MC-06` |
| Claim supremacy for CIOS or for itself | `CIOS-G-01`, `CIOS-G-02` OPEN; `MC-08` |

---

## AUTHORITY BOUNDARY (MANDATORY)

This record registers a design-only mission in a programme-owned home. It owns no mechanism, no registry, no gate, no identifier space and no concern. It mints nothing, allocates nothing, discharges nothing, freezes nothing and authorizes no execution. `IMR-003A` and `IMR-003A-R1` are consumed **read-only and unmodified**. Every authority named is located in an instrument that exists independently at `b26c5bb`. Where this record and a located canonical instrument disagree, **the located instrument governs and this record SHALL be corrected**.

**END OF ARTIFACT — `IMR-0000/00` · PROVISIONAL · ADDITIVE · DESIGN-ONLY · AUTHORITY-NEUTRAL**
