# IMR-0000/18 — INTELLIGENCE FRAMEWORKS · ENGINEERING · GOVERNANCE · EVOLUTION

| Field | Value |
|---|---|
| MISSION | `IMR-0000` — CIOS Platform Foundation |
| ARTIFACT | `18` — **directive capabilities 22, 23, 24** (Engineering / Governance / Evolution Intelligence frameworks) |
| ARTIFACT KIND | Framework (`CMG-K-05`) — binding declarations |
| CLOSES | `00A` `PGAP-10` — the located intelligence mechanisms exist but no subsystem declares which it consumes, so the platform's intelligence surface is undiscoverable |
| SUBSYSTEMS | `SS-13` `CIOS-EI` (`E-20`, `E-21`) · `SS-14` `CIOS-GI` (`E-09`, `E-18`) · `SS-17` `CIOS-EVO` (**BINDING-ONLY**) |
| CENTRAL CONSTRAINT | **`UCI-001` `IP-1 … IP-6` govern all three.** Intelligence is **derived on demand**, cites its provenance, reads only the four located authoritative stores, and introduces **no store, no engine and no identifier namespace**. |
| AUTHORITY OF ITS OWN | **NONE.** |
| CONFLICT RULE | Located instrument governs (`UCI-001` + `UCI-OPT-001` for intelligence discipline; `CEP-009` for evolution; `CMG-000001`/`CEP-002`/`CEP-010` for governance); then `IMR-003A`; then this artifact. |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. THE COMMON INTELLIGENCE DISCIPLINE

All three frameworks are bound by one located rule set. Restating it three times would breach `CIOS-L-08`; it is stated once here and referenced by each section.

| ID | Located rule | Source |
|---|---|---|
| `IP-1` | intelligence is a **reader**, not an authority | `UCI-001` PART on intelligence principles |
| `IP-2` | intelligence adds no governance of its own | `UCI-001` |
| `IP-3` | **derived intelligence** — predictions, recommendations and scores are generated on demand from stored evidence and **SHALL NOT be persisted as authoritative fact** | `UCI-001` `IP-3` |
| `IP-4` | **provenance** — every intelligence output cites the signals, edges, versions and decisions it derived from | `UCI-001` `IP-4` |
| `IP-5` | **single evidence base** — intelligence reads only the four authoritative stores (**artifact registry, ID ledger, knowledge graph, signal ledger**) and their derived views | `UCI-001` `IP-5` |
| `IP-6` | **no AI registry** — intelligence introduces no store, no engine and no identifier namespace | `UCI-001` `IP-6` |

| ID | Platform rule | Basis |
|---|---|---|
| `IN-1` | An intelligence framework declares **which** located mechanisms a subsystem consumes. It computes nothing and stores nothing. | `IP-1`, `IP-6`; `CIOS-INV-12` |
| `IN-2` | An intelligence output is **evidence, never an act**. Traversing it confers no right. | `PR-6`; `CIOS-L-11` |
| `IN-3` | Where an intelligence question has no located mechanism, it is recorded as a **gap with a named prospective owner** — never filled by the platform. | `CIOS-03` §1.1 ABSENT discipline |

---

## 2. ENGINEERING INTELLIGENCE — `SS-13` `CIOS-EI` *(directive capability 22)*

### 2.1 Mission and scope

**Mission.** Append the record of what became true, emit its traceability binding, and declare the derived engineering picture a programme may read — without persisting any derived value as fact.

**Scope.** Truth append (`E-20`) and traceability emission (`E-21`), plus read-only bindings to the located derived-intelligence surface. **Not** closure regeneration, not ownership of the graph, not persisted prediction.

### 2.2 Located bindings

| Question | Located mechanism | Access |
|---|---|---|
| what became true, and when? | `closure.json` (append via `CIOS-P-40`, `PL-C` only); `AIF-L08`, `L17`; `CEP-008` | **R** + **A** |
| what traces to what? | `relationships.json`; `UMB-007`; `UCCEP-000000` `07-UNIVERSAL-TRACEABILITY-GRAPH.md`; `MCP-006` | **R** + edge emission |
| what is the derived engineering picture? | `intelligence/rie` — `UCOS-RIE-MODEL.json`, `-SNAPSHOT`, `-PROGRESS`, `-HEALTH`, `-EXECUTION-FRONTIER`, `-CAPABILITY-CATALOG`, `-DEPENDENCY-GRAPH`, `-DIGITAL-TWIN`, `-AEOS-READINESS` | **R** |
| what changed, in what version, with what lineage? | `change-ledger.json`; `artifacts.json[*].version` + `content_hash`; `UMB-010` lineage | **R** |
| what is the measured build/test/determinism state? | `CK-VERIFY`, `CK-DETERMINISM-BUILD`, `CK-RIE-DETERMINISM`; `determinism-evidence/`; `coverage.xml` | **R** |

### 2.3 Public interfaces, validation, certification, extension

| Field | Declaration |
|---|---|
| **Public interfaces** | **`CIOS-P-40`** (truth append record) and **`CIOS-P-42`** (traceability edge) — two of the platform's eight public egress ports. `P-39`, `P-41` internal. |
| **Owned objects** | truth append record; traceability edge; `UOM-A-20` traceability slot |
| **Consumed objects** | seal records; `relationships.json`; `intelligence/UCOS-RIE-*.json`; `signals.json` |
| **Validation** | `CEP-004`; `G-14` Implementation Evidence Gate; `CK-VERIFY` |
| **Certification** | `CEP-005`; ceiling `CERTIFIED-PROVISIONAL` |
| **Bound** | **`UCCEP-F-002` / `CIOS-G-06`** — traceability is incomplete for all **1198** registered artifacts. `P-42` failure marks an item **traceability-incomplete** and **does not block the seal**. **No closure is claimed.** |
| **Future extension** | new derived views are admissible; **persisting them as fact is not** (`IP-3`). New edge types route through `PG-05`. |

---

## 3. GOVERNANCE INTELLIGENCE — `SS-14` `CIOS-GI` *(directive capability 23)*

### 3.1 Mission and scope

**Mission.** Produce the impact assessment and the single change classification for every submission, determine evidence sufficiency, and adjudicate the only lawful reach into protected or sealed work.

**Scope.** Impact, classification, governance admission, evidence sufficiency, override adjudication. **Not** the governance rules (all 33 `GR-*` located), not audit execution, not ratification, not certification.

### 3.2 Located bindings

| Question | Located mechanism | Access |
|---|---|---|
| what does this change affect? | `CEP-009` III.1 impact assessment; `UCI-001` PART XII traversal (**derived, never persisted**) | **R** |
| what class of change is it? | `CEP-009` IV.1 classes; **exactly one primary class** (IV.6) | **R** |
| is it constitutionally admissible? | `G-04` Constitution Gate; `G-05` Architecture Admission Gate; `G-09` Governance Gate | **R** |
| is the evidence sufficient, and is the decision dispositioned? | `G-12`; `CEP-002` Article 28; `ucda-decisions.json`; `CK-DECISION-EVIDENCE` | **R** |
| who may reach protected work? | `CIOS-OR-01`, `CIOS-OR-02`; `CEP-009` Art III / Art XX.2 | **R** |
| what does audit say? | `CEP-010` audit and compliance assurance | **R** |
| what is the governance roll-up? | `control-tower.json` dimensions; `CMG-REGISTRY.json` `readiness`, `gaps`, `open_questions` | **R** |

### 3.3 Public interfaces, validation, certification, extension

| Field | Declaration |
|---|---|
| **Public interfaces** | **`CIOS-P-35`** — the sole override ingress, admitting exactly two located authorities. `P-17`, `P-18`, `P-36` internal. |
| **Owned objects** | impact assessment + primary class; adjudication + **mandatory** immutable override record; `UOM-A-13` policy binding |
| **Consumed objects** | `ucda-decisions.json` (**64 decisions, 0 undispositioned, 205 evidence items, seal `8d34d196a80a05b8`**); `CEP-009` evolution registry; `CMG-REGISTRY.json`; `control-tower.json` |
| **Validation** | `CEP-004`; `G-04`, `G-05`, `G-09`, `G-12`; `CK-DECISION-EVIDENCE` |
| **Certification** | `CEP-005`; ceiling `CERTIFIED-PROVISIONAL` |
| **Bound** | **`UCCEP-F-008`** — the disposition obligation is newly gated; the platform binds `CK-DECISION-EVIDENCE` and restates nothing. An undispositioned decision **closes the Implementation Evidence Gate** (`CEP-002` Art 28.14, 28.18). |
| **Future extension** | change classes are `CEP-009` IV.1's enumeration, extensible by its owner. **A third override authority may not be added by the platform** (`CIOS-L-21`). |

---

## 4. EVOLUTION INTELLIGENCE — `SS-17` `CIOS-EVO` *(directive capability 24)* · **BINDING-ONLY**

### 4.1 Mission and scope

**Mission.** Declare the single binding surface for constitutional evolution, amendment, versioning, lineage, regeneration and change intelligence — **without owning an evolution model**.

**Scope.** The binding declaration only. `CIOS-01` VIII.1 is explicit: **CIOS owns no evolution model**; `CEP-009` is the sole owner of the constitutional evolution model, the evolution registry, versioning and lineage.

### 4.2 Located bindings

| Question | Located mechanism | Access |
|---|---|---|
| how does an instrument change? | `CEP-009` Art III (change/migration route), III.1 (impact assessment), Art IV.3 (successor, not in-place edit), Art VI / XVI / XXIV (evolution model, registry, lineage), Art XXIII.10 (unlimited evolution) | **R** |
| what changed and why? | `UCI-001` change/version/impact/knowledge/regeneration/rollback governance; `change-ledger.json`; `UMB-008` change architecture; `UMB-010` lineage | **R** |
| what must be regenerated? | `IEC-001` `07` / C10 / RG-3; `REG-AUTO-001` transaction `T`; `RR-6` | **R** |
| what is superseded? | `Supersedes` / `Superseded-By` edges; `status ∈ {SUPERSEDED, RETIRED}`; `SUPERSESSION-REGISTER` | **R** |
| where is the plan realigned? | `CIOS-12` future-only realignment over `PT-03` (`SS-05`) | **R** |
| what is forbidden to exist? | `UCI-OPT-001` **MUST NOT EXIST** list — no `changes.json`/`knowledge.json`/`regeneration.json`/`rollback.json`/`version.json`/`baseline.json`/`impact.json`/`metrics.json`/`readiness.json`/`compliance.json` as **new namespaces**; no `UCHG`/`UCKA`/`URBK`/`UREG` namespaces; **no second state machine, no second sync pass, no second engine** | **R** |

### 4.3 Public interfaces, validation, certification, extension

| Field | Declaration |
|---|---|
| **Public interfaces** | **none — no engine, no port.** A programme routes change through `CEP-009` III.1 **directly** (`IFL-11`). |
| **Owned objects** | **none** |
| **Consumed objects** | `CEP-009` evolution registry (`RC-08`); `change-ledger.json`; `UCOS-RIE-*` derived views |
| **Validation** | `CEP-004`; `G-09` |
| **Certification** | `CEP-005`; ceiling `CERTIFIED-PROVISIONAL` |
| **Bound** | **`GG-3` / `CIOS-GAP-12`** — registers 8–11 are absent, so register-backed change/knowledge/regeneration/rollback capability is unavailable. Owner: `UCI-001`, `WP-GDR-001`. |
| **Future extension** | **every extension of the platform routes here**: `CEP-009` III.1 with an impact assessment. `PG-01 … PG-09` are the platform's open instances of that route. |

### 4.4 Why the evolution subsystem holds no engine, and why that is correct

An evolution *engine* inside the platform would necessarily either (a) duplicate `CEP-009`'s mechanism — a `CEP-001` LAW-4 breach — or (b) hold discretion over what may change, which engines do not have (`CIOS-03` §1). And it could not exist in any case: the engine count is fixed at 24 by `CIOS-01` Art X.1, and raising it is itself a `CEP-009` III.1 change to `CIOS-01` (`PG-02`). The empty engine set is therefore the **only** lawful configuration, not a deferral.

---

## 5. AGGREGATE PROPERTIES

| Property | Value |
|---|---|
| Intelligence frameworks declared | **3** |
| Subsystems bound | **3** (`SS-13`, `SS-14`, `SS-17`) |
| Engines involved | **4** (`E-09`, `E-18`, `E-20`, `E-21`) |
| Public ports involved | **3** (`CIOS-P-35` ingress; `CIOS-P-40`, `CIOS-P-42` egress) |
| Intelligence stores created | **0** (`IP-6`) |
| Engines or namespaces created | **0** |
| Derived values persisted as fact | **0** (`IP-3`) |
| Outputs without cited provenance | **0** (`IP-4`) |
| Evidence bases read | **4** — artifact registry, ID ledger, knowledge graph, signal ledger (`IP-5`) |
| Governance rules created | **0** |
| Evolution models owned | **0** |
| Inherited bounds carried | **3** — `UCCEP-F-002` (`SS-13`), `UCCEP-F-008` (`SS-14`), `GG-3` (`SS-17`) |

---

## 6. WHAT THIS ARTIFACT DOES NOT DO

| Not done | Located owner |
|---|---|
| Compute, generate or persist any intelligence output | `intelligence/rie`; `UCI-001`; `IP-3` |
| Create an intelligence store, engine, model or identifier namespace | `IP-6`; `CIOS-INV-12` |
| Create any register on `UCI-OPT-001`'s MUST-NOT-EXIST list | expressly prohibited |
| Own or amend an evolution model, or create an evolution entry | `CEP-009` Art VI/XVI/XXIV; `CIOS-01` VIII.1 |
| Create a governance rule, claim a concern, or issue a gate verdict | `CMG-000001`; `CEP-002`; `G-01…G-14` |
| Add a decision or alter a disposition | `UCDA-000001`; `RC-07` |
| Claim traceability closure | `UCCEP-F-002`; `CIOS-17` §5 |
| Add a third override authority | `CIOS-L-21` |
| Discharge `UCCEP-F-002`, `UCCEP-F-008` or `GG-3` | each owner-held |

---

## AUTHORITY BOUNDARY (MANDATORY)

This artifact declares three intelligence **binding surfaces**. **It computes nothing, stores nothing, persists no derived value, creates no store, engine or namespace, owns no evolution model and writes no governance rule.** Intelligence outputs are evidence, never acts. Three inherited findings bound the claims made here and none is discharged. Every mechanism named is located in an instrument existing independently at `b26c5bb`. Where this artifact and a located canonical instrument disagree, **the located instrument governs and this artifact SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `IMR-0000/18` · PROVISIONAL · ADDITIVE · DESIGN-ONLY · AUTHORITY-NEUTRAL**
