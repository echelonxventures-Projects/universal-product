# IMR-0000/07 — CANONICAL REGISTRY FRAMEWORK · ELEVEN REGISTRY SPECIFICATIONS · REGISTRY RELATIONSHIPS

| Field | Value |
|---|---|
| MISSION | `IMR-0000` — CIOS Platform Foundation |
| ARTIFACT | `07` — carries **deliverable 3** (Canonical Registry Framework, §1–§3), **deliverables 7–17** (the eleven registries, §4), and **directive capability 29** (Registry relationships, §6) |
| ARTIFACT KIND | Framework (`CMG-K-05`) + specification set |
| CLOSES | `PGAP-08` (admissibility test) · `PGAP-04` (register relationships) · contracts for `PGAP-02`, `PGAP-03`, `PGAP-05` |
| NUMERIC CONTRACT | **8 framework rules** `RF-1 … RF-8` · **11 registry specifications** `REG-01 … REG-11` · **6 register relationship types** `RR-1 … RR-6` |
| CENTRAL CLAIM | **Zero registries are created, written, or given an entry.** Nine of eleven specifications bind a located register; two are contract-only with a recorded gap and a named prospective owner. |
| AUTHORITY OF ITS OWN | **NONE.** `CIOS-INV-12` — CIOS holds no registry of its own. |
| CONFLICT RULE | Located instrument governs (`GOV-INT-001` §6, then `REG-AUTO-001`); then `IMR-003A` (`CIOS-13`, `IMR-003A-R1/07`); then this artifact. |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. WHY A REGISTRY SPECIFICATION IN THIS MISSION IS A CONTRACT, NOT A REGISTER

The instruction asks for eleven registries. Instantiating any of them would breach four located instruments at once:

| Act | Breach |
|---|---|
| create a register | `CIOS-INV-12` (*no registry of its own*); `IMR-003A` `AC-4` |
| add a second store for something already stored | `GOV-INT-001` §6.1 (*single store, single ledger, single graph*); `UCI-OPT-001` (*net-new persistent structures across all 15: ZERO*) |
| add an entry to a located register | `IMR-003A-R1/07` §3 (*registry entries added: 0*); `REG-AUTO-001` owns transaction `T` |
| name a second owner for a register | `CEP-001` LAW-4; `CIOS-L-09` |

`IMR-003A-R1/07` §5 already established this for CIOS and stated the conclusion plainly: **the read-only posture is compelled, not chosen.** `IMR-0000` inherits that posture unchanged and adds only what was missing — the **admissibility test** (§3) and the **relationship model** (§6).

### 1.1 What each `REG-*` specification is

| A `REG-*` specification **is** | A `REG-*` specification **is NOT** |
|---|---|
| a declaration of which located register answers a platform question | a register, store, file, schema or table |
| a binding to one or more `RC-01 … RC-14` read contracts | a fifteenth read contract |
| a statement of access mode, obligation and prohibition | a grant of write authority |
| where no located register exists: a **contract-only** specification plus a recorded gap and prospective owner | a licence to create the register |

---

## 2. THE LOCATED REGISTER SET

Reproduced **by pointer**. Owner: `GOV-INT-001` §6.2 (the eleven-register unified set) and `REG-AUTO-001`. Observed at `00-BOOK/DATA/` at `b26c5bb`.

| # | Located register | File | Owner | Present at `b26c5bb`? |
|---|---|---|---|---|
| 1 | Artifact Registry | `artifacts.json` | `REG-AUTO-001` | **YES** |
| 2 | Execution Status Registry | roll-up in `control-tower.json` | `REG-AUTO-001` | **YES** |
| 3 | Control Tower | `control-tower.json` | `REG-AUTO-001` | **YES** |
| 4 | Digital Twin | `twin.json` + `signals.json` | `REG-AUTO-001` / `UKB-ADV` | **YES** |
| 5 | Traceability / Knowledge Graph | `relationships.json` | `REG-AUTO-001` | **YES** |
| 6 | Dependency Registry | `artifacts.json[*].dependencies` | `REG-AUTO-001` | **YES** |
| 7 | Page / ID Ledger | `id-ledger.json` | `REG-AUTO-001` | **YES** |
| 8 | Universal Change Registry | `changes.json` | `UCI-001` | **NO** — `GG-3` |
| 9 | Universal Knowledge Registry | `knowledge.json` | `UCI-001` | **NO** — `GG-3` |
| 10 | Regeneration Requirements Registry | `regeneration.json` | `UCI-001` | **NO** — `GG-3` |
| 11 | Rollback Registry | `rollback.json` | `UCI-001` | **NO** — `GG-3` |
| + | Certification | `certification.json` | `CEP-005` / `REG-AUTO-001` | **YES** |
| + | Change ledger | `change-ledger.json` | `UCI-001` / `REG-AUTO-001` | **YES** |
| + | Volumes | `volumes.json` | `REG-AUTO-001` | **YES** |
| + | Connector cursors | `connector-cursors.json` | `REG-AUTO-001` | **YES** |

**Registers 8–11 are absent.** That is `GG-3` / `CIOS-GAP-12`, owned by `UCI-001` and `WP-GDR-001`, undischarged. This mission neither creates them nor claims their absence is closed. Where a `REG-*` specification would depend on one, the dependency is recorded as blocked.

---

## 3. THE ADMISSIBILITY TEST — WHAT MAKES A REGISTER CANONICAL

The framework's substantive contribution. Every rule points to a located owner; **zero net-new law**.

| ID | Rule | Located basis |
|---|---|---|
| `RF-1` | **One question, one register.** A register is canonical only if no other register answers the same question. A proposed register that duplicates an existing answer is refused; the existing register is **extended** instead. | `CEP-001` LAW-4; `CIOS-L-09`; `UCI-OPT-001` (*Change+Knowledge+Dependency+Impact are graph relationships, not stores*) |
| `RF-2` | **One store, one ledger, one graph.** A canonical register lives in the single append-only store; it does not introduce a persistence layer, a second allocator or a second graph. | `GOV-INT-001` §6.1, §2.6 |
| `RF-3` | **One owner.** A register has exactly one owning instrument, named in `CMG-REGISTRY.json` or in a located standard. An unowned register is inadmissible. | `UUP-02`; `CMG-000001`; `GG-6` is the open instance of this failing (`UCIC-001` unowned in the registry) |
| `RF-4` | **One transaction.** Writes occur only through the single located registration transaction `T`. No second synchronization pass exists. | `REG-AUTO-001` §7; `GOV-INT-001` §2.7 |
| `RF-5` | **Append-only.** No read-modify-write, no in-place edit, no delete. Correction is forward-only compensation. | `AIF-L08`, `AIF-L17`; `UUP-08` |
| `RF-6` | **Derived is not recorded.** Anything computable from the store by traversal or projection is a **view**, never a register. Metrics, readiness, compliance, impact, search index and the twin are views. | `AIF-L01`; `UCI-001` `IP-3`; `UCI-OPT-001` "MUST BE DERIVED" |
| `RF-7` | **Human indices are generated.** Rendered registers under `00-BOOK/REGISTRIES/` are generated from the store and never hand-authored; the JSON governs. | `GOV-INT-001` §6.1 |
| `RF-8` | **Fail closed.** A register that cannot be read yields a **non-admission**, never a default, an empty result treated as clean, or a partial answer. | `CIOS-L-07`; `PR-3`, `PR-8` |

### 3.1 Applying the test to the eleven requested registries

| Requested registry | `RF-1` — is the question already answered? | Verdict |
|---|---|---|
| Programme | **YES** — `uccep.json` `programs[]` | bind (`REG-01`) |
| Mission | **PARTLY** — convention answers *where*; nothing answers *which* machine-readably | bind + gap (`REG-02`, `PGAP-05`) |
| Portfolio | **YES** — `control-tower.json.portfolio` | bind (`REG-03`) |
| Capability | **YES** — capability catalogue + `PLATFORM-006` + `UCIC-001` | bind + inherited gap `GG-6` (`REG-04`) |
| Subsystem | **NO** — nothing to answer it, because subsystems are new | **contract only** (`REG-05`, `PGAP-02`) |
| Interface | **YES** — `CIOS-05` port register + `IMR-003A-R1/06` | bind (`REG-06`) |
| Contract | **NO** unified answer — contracts located severally, anchor unowned | **contract only** (`REG-07`, `PGAP-03`) |
| Dependency | **YES** — `artifacts.json[*].dependencies` + `relationships.json` | bind (`REG-08`) |
| Evidence | **YES** — `CEP-008` + `signals.json` + `ucda-decisions.json` | bind (`REG-09`) |
| Validation | **YES** — `uccep.json` `checks` + `engine/validation` | bind (`REG-10`) |
| Certification | **YES** — `certification.json` + `CERTIFICATION-REGISTRY.md` | bind (`REG-11`) |

**Nine bind. Two are contract-only. Zero are created.**

---

## 4. THE ELEVEN REGISTRY SPECIFICATIONS

Access: `R` read-only · `A` append via a located mechanism · `⊘` no access. **No specification carries a write mode**, because no such access exists (`IMR-003A-R1/05` §2 — there is no `→W` symbol).

### `REG-01` — Programme Registry *(deliverable 7)*

| Field | Declaration |
|---|---|
| **Question answered** | Which programmes exist, where is each homed, who owns it, and what is its verdict? |
| **Located register** | `00-MASTER/UCCEP-000000/uccep.json` `programs[]` — `PROGRAM-000001 … PROGRAM-000016`, each with `name`, `checks`, `delegated_to`, `executed`, `failed`, `output`, `verdict` |
| **Supporting located sources** | `UCCEP-000006` §1 **P-5** (programme-home convention `00-MASTER/<PROGRAMME-ID>/`) · `CMG-REGISTRY.json` `artifacts[]` (43) · `control-tower.json` `programs[]` roll-up |
| **Owner** | `UCCEP-000000` owner (register) · Registration/Governance Authority (`CMG-REGISTRY.json`) · `REG-AUTO-001` (roll-up) |
| **Bound read contracts** | `RC-06` (`uccep`), `RC-01` (`CMG-REGISTRY`), `RC-13` (master context) |
| **Access** | **R** |
| **Platform binding** | `SS-03` `CIOS-PMS` (BINDING-ONLY) |
| **UOM attributes served** | `A-01`, `A-02`, `A-05`, `A-06`, `A-14`, `A-15` |
| **Obligation** | A programme SHALL be homed under `00-MASTER/<PROGRAMME-ID>/` and SHALL declare its outputs in a registration record before any output is authored. |
| **Prohibition** | No programme entry added; no `PROGRAM-*` identifier allocated; no verdict altered; no second programme register. |
| **Observed state** | **16 programmes; 6 PASS; blocking failures none** (`uccep.json`, tier `boot`) |
| **Gaps** | none of this mission's; programme verdicts 6/16 is a located measurement, not a gap |

### `REG-02` — Mission Registry *(deliverable 8)*

| Field | Declaration |
|---|---|
| **Question answered** | Which missions (work packages) exist within a programme, what did each undertake to produce, and what is each output's state? |
| **Located register** | **NONE.** The answer exists only as a **convention**: a mission registration record at `00-MASTER/<PROGRAMME-ID>/00-*MISSION-REGISTRATION-RECORD.md`, plus the `WP-*` work-package designation. |
| **Supporting located sources** | `UCCEP-000006` P-5 · `MCP-003` master execution · `MCS-000` · precedent records: `IMR-001`, `IMR-003A/00`, `IMR-003A-R1/00`, `IMR-0000/00` |
| **Owner** | prospective: `REG-AUTO-001` + Registration Authority. **Currently: none** |
| **Bound read contracts** | `RC-13`, `RC-06` |
| **Access** | **R** on the convention's artifacts |
| **Platform binding** | `SS-04` `CIOS-MRS` for submissions; the **programme-level** mission record is `SS-03`'s binding |
| **UOM attributes served** | `A-02`, `A-05`, `A-06`, `A-17`, `A-19` |
| **Obligation** | Every mission SHALL declare, before producing any output: its output register, its authority basis, its constraints, its acceptance criteria and its disclosed divergences. `IMR-003A`'s termination after 2 of 22 declared outputs is the located precedent establishing why the declaration must precede the work. |
| **Prohibition** | No mission register created; no `WP-*` identifier allocated; no mission record of another programme touched. |
| **Observed state** | 4 mission registration records located under `00-MASTER/`; **no machine-readable index of them exists** |
| **Gaps** | **`PGAP-05`** — no machine-readable mission register and no allocator. Integration point: `uccep.json` `programs[]` extension by its owner. Not closable here (`CIOS-INV-12`). |

### `REG-03` — Portfolio Registry *(deliverable 9)*

| Field | Declaration |
|---|---|
| **Question answered** | What is the aggregate state of everything the platform governs? |
| **Located register** | `00-BOOK/DATA/control-tower.json` `portfolio` — `total_artifacts`, `total_pages`, `total_volumes`, `total_edges`, `portfolio_status`, `status_histogram`; plus `programs[]` and `dimensions[]` roll-ups |
| **Supporting located sources** | `control-tower.schema.json` · rendered views `PROGRAM-CONTROL-TOWER.md`, `UCOS-MASTER-EXECUTION-STATUS-REGISTRY.md` (generated, `RF-7`) · `STATUS-001` status determination |
| **Owner** | `REG-AUTO-001` (`CMG-DLG-13`); status semantics `STATUS-001` (`CMG-DLG-14`) |
| **Bound read contracts** | `RC-03`, `RC-13` |
| **Access** | **R** |
| **Platform binding** | `SS-10` `CIOS-DT` (the twin dimension) and `SS-03` `CIOS-PMS` (programme roll-up) |
| **UOM attributes served** | `A-14`, `A-15`, `A-16` — **as views, never as record** (`RF-6`) |
| **Obligation** | Portfolio state SHALL be derived deterministically from the artifact registry and ingested signals; it SHALL NOT be hand-authored. |
| **Prohibition** | No dimension added; no status overridden; no roll-up written; no second portfolio view treated as authoritative. |
| **Observed state** | `portfolio_status = IN_PROGRESS` — *analysis/architecture/generation complete; runtime testing/deployment pending EC-1* |
| **Gaps** | none of this mission's |

### `REG-04` — Capability Registry *(deliverable 10)*

| Field | Declaration |
|---|---|
| **Question answered** | Which capabilities exist, what implements each, and under what contract? |
| **Located register** | `intelligence/UCOS-RIE-CAPABILITY-CATALOG.json` (derived catalogue) |
| **Supporting located sources** | `PLATFORM-006/007/008` (capability/component/service) · `PLATFORM-018` Platform Master Registry · `UCIC-001` Universal Capability Implementation Contract · `artifacts.json` capability artifacts · evidence bundles (e.g. `UCOS-CAPABILITY-ucos.service.capability.foundation-*`) |
| **Owner** | `PLATFORM-001`/`006` (model) · `intelligence/rie` (catalogue, derived) · `UCIC-001` (contract) |
| **Bound read contracts** | `RC-14` (`UCIC-001`), `RC-03`, `RC-10` |
| **Access** | **R** |
| **Platform binding** | `SS-03` for staging; `SS-13` `CIOS-EI` for the derived catalogue |
| **UOM attributes served** | `A-01`, `A-03`, `A-11`, `A-12`, `A-16` |
| **Obligation** | A capability SHALL be staged against a citable implementation contract before implementation is authorized. |
| **Prohibition** | No capability entry added; no contract altered; no catalogue regenerated (that is `intelligence/rie`'s act). |
| **Observed state** | capability catalogue present as a **derived** view; the contract anchor `UCIC-001` is **absent from `CMG-REGISTRY.json`** |
| **Gaps** | **inherited `GG-6` / `CIOS-GAP-11`** — capability staging has no citable owner. Owner: Registration/Governance Authority. Undischarged; not this mission's to close. |

### `REG-05` — Subsystem Registry *(deliverable 11)* · **CONTRACT ONLY**

| Field | Declaration |
|---|---|
| **Question answered** | Which platform subsystems exist, which engines does each hold, and what does each bind? |
| **Located register** | **NONE.** No located register records subsystems, because the subsystem layer did not exist before `02`. |
| **Declaration of record** | `IMR-0000/02` §2 and §4.1, projected machine-readably in `imr-0000-platform-bindings.json` (**DATA ONLY, AUTHORITY NONE**) |
| **Owner** | prospective: the located owner of `cios-bindings.json` (for a `CIOS-SS-*` family) + Registration Authority (for a `CMG-REGISTRY.json` kind) |
| **Bound read contracts** | none — nothing to read |
| **Access** | **⊘** |
| **Platform binding** | the declaration binds all 17 subsystems; **no subsystem binds it** |
| **UOM attributes served** | `A-02`, `A-05`, `A-06`, `A-07`, `A-09`, `A-11` — with `A-01`, `A-03`, `A-04`, `A-14` **declared-inapplicable** (`03` §4.3) |
| **Obligation** | Any future subsystem SHALL be declared as a **disjoint** subset of the existing engine set, SHALL own no mechanism, and SHALL declare its bindings. |
| **Prohibition** | **This mission creates no subsystem register.** Doing so would breach `CIOS-INV-12`. No `CIOS-SS-*` family is created; no `CMG-REGISTRY.json` kind is added. |
| **Gaps** | **`PGAP-02`** — no register exists. Integration point: `GOV-INT-001` §6.2 register set. Gates: **`PG-01`** (family admission to `cios-bindings.json`), **`PG-03`** (register instantiation). Both owner-held. |

### `REG-06` — Interface Registry *(deliverable 12)*

| Field | Declaration |
|---|---|
| **Question answered** | Which interfaces exist, which are public, and what is each one's contract? |
| **Located register** | `IMR-003A/05-CIOS-ENGINE-INTERFACES.md` — the full 48-port register with direction, payload class, pre/post-condition and failure mode; the 8-port public subset |
| **Supporting located sources** | `IMR-003A-R1/06-INTERFACE-MATRIX.md` · `IMR-003A-R1/09` stability contract · `PLATFORM-007/008` · `00-BOOK/SCHEMAS/*.schema.json` |
| **Owner** | `IMR-003A/05` (CIOS ports) · `PLATFORM-007/008` (platform interfaces) |
| **Bound read contracts** | inherits `IMR-003A-R1/06`; no new contract |
| **Access** | **R** |
| **Platform binding** | catalogued in `19`; every subsystem's interface field in `02` §3 points here |
| **UOM attributes served** | `A-11`, `A-12` |
| **Obligation** | Every interface SHALL declare direction, payload **class**, pre-condition, post-condition and a **fail-closed** failure mode. An interface without a declared failure mode is itself a defect (`PR-3`). |
| **Prohibition** | No port created; no internal port promoted to public; no payload class re-specified in terms of a format, protocol or language (`PR-2`, `CIOS-L-22`). |
| **Observed state** | **48 ports; 8 public; 48/48 with declared fail-closed mode; 0 naming a format or protocol; 0 conferring authority** |
| **Gaps** | none of this mission's |

### `REG-07` — Contract Registry *(deliverable 13)* · **CONTRACT ONLY**

| Field | Declaration |
|---|---|
| **Question answered** | Which contracts bind which objects, and what is each contract's version and stability route? |
| **Located register** | **NONE unified.** Contracts are located severally: `UCIC-001` (capability implementation) · `00-BOOK/SCHEMAS/*.schema.json` (structural) · `IMR-003A-R1/09` (architecture & interface stability) · `SERVICE-007` (service contract, `SMC-03`) · `CIOS-05` port contracts |
| **Owner** | prospective: `REG-AUTO-001` + Registration Authority. **Currently: no unified owner** — and the natural anchor `UCIC-001` is itself unregistered |
| **Bound read contracts** | `RC-14`, `RC-03` |
| **Access** | **R** on each located contract severally; **⊘** on a unified register that does not exist |
| **Platform binding** | `SS-03` (capability contracts) · `SS-16` (certification contracts) · `19` (interface contracts) |
| **UOM attributes served** | `A-12`, `A-18` |
| **Obligation** | Every contract SHALL declare its scope, its parties, its version and its change route. A contract change SHALL route through `CEP-009` III.1, never by in-place edit (`PR-7`). |
| **Prohibition** | **This mission creates no contract register.** No contract is altered. No contract is deemed registered by being cited here. |
| **Gaps** | **`PGAP-03`** — no unified register; blocked behind **`GG-6`** (`UCIC-001` absent from `CMG-REGISTRY.json`). Gate: **`PG-04`**. Owner: Registration/Governance Authority. |

### `REG-08` — Dependency Registry *(deliverable 14)*

| Field | Declaration |
|---|---|
| **Question answered** | What does each object depend on, and is the dependency graph acyclic? |
| **Located register** | `00-BOOK/DATA/artifacts.json[*].dependencies` (`GOV-INT-001` §6.2 register 6) + `00-BOOK/DATA/relationships.json` `Depends-On` edges |
| **Supporting located sources** | `engine/graph` · `CK-GRAPH` · `intelligence/UCOS-RIE-DEPENDENCY-GRAPH.json` (derived) · `IMG-001` `03` backlog graph · `CIOS-06` engine graph (25 `DERIVES`) · `IMR-003A-R1/05` (35 located bindings) |
| **Owner** | `REG-AUTO-001` (the field and the graph) · `engine/graph` (evaluation) · `IMG-001` (backlog graph) |
| **Bound read contracts** | `RC-03`, `RC-10`, `RC-06` |
| **Access** | **R** |
| **Platform binding** | `SS-08` `CIOS-DAG` |
| **UOM attributes served** | `A-09`, `A-07`, `A-08`, `A-10` |
| **Obligation** | Every declared dependency SHALL resolve, and admission SHALL introduce no cycle. A **reported** cycle is a non-admission **regardless of the validator's returned validity flag**. |
| **Prohibition** | No dependency added or removed; no edge written; no second dependency store; no second graph. |
| **Observed state** | dependency field and graph present; **35/35 located CIOS bindings resolve; 0 dangling; 0 cyclic** (`IMR-003A-R1/05` §6) |
| **Gaps** | **inherited `UCCEP-F-003` / `CIOS-G-04`** — the located validator **fails open** on a reported cycle, so `CIOS-INV-05` is not machine-enforced corpus-wide. Owner: owner of `engine/graph`. Undischarged. |

### `REG-09` — Evidence Registry *(deliverable 15)*

| Field | Declaration |
|---|---|
| **Question answered** | What evidence discharges each determination, and where is it? |
| **Located register** | `00-BOOK/DATA/signals.json` (append-only signal ledger) + `00-MASTER/UCDA-000001/ucda-decisions.json` (decision evidence) + per-execution evidence bundles (e.g. `service/_evidence/<unit>/`) |
| **Supporting located sources** | `CEP-008` Evidence & Traceability Constitution · `G-12` Evidence Gate · `G-14` Implementation Evidence Gate · `CK-DECISION-EVIDENCE` · `CEP-002` Art 28 · `signal.schema.json` |
| **Owner** | `CEP-008` (evidence law) · `REG-AUTO-001` (ledger) · `UCDA-000001` (decision evidence) |
| **Bound read contracts** | `RC-07`, `RC-03`, `RC-13` |
| **Access** | **R** + **A** (append only, via `CIOS-P-40` on `SS-13`, `PL-C` only) |
| **Platform binding** | `SS-13` `CIOS-EI` (append) · `SS-14` `CIOS-GI` (sufficiency determination at `CIOS-S-18`) |
| **UOM attributes served** | `A-17`, `A-20` |
| **Obligation** | Missing, ambiguous, unresolvable or degraded evidence is a **failure, never a pass** (`CIOS-L-07`). Every governed manual override SHALL carry `override=true` with `actor` and `reason`; unattributed overrides are INVALID. |
| **Prohibition** | No evidence edited or deleted; never read-modify-write; no evidence fabricated, defaulted or inferred. |
| **Observed state** | **205 evidence items; 64 decisions; 0 undispositioned; UCDA gate OPEN; seal `8d34d196a80a05b8`** |
| **Gaps** | **inherited `UCCEP-F-008`** — the disposition obligation is newly gated; the platform binds `CK-DECISION-EVIDENCE` and restates nothing. |

### `REG-10` — Validation Registry *(deliverable 16)*

| Field | Declaration |
|---|---|
| **Question answered** | What validation applies to each object, was it executed, and what was the verdict? |
| **Located register** | `00-MASTER/UCCEP-000000/uccep.json` `checks` (the `CK-*` check register, with `executed` / `not_executed` / `failed` per programme) + `uccep-bindings.json` |
| **Supporting located sources** | `CEP-004` Validation Constitution · `engine/validation` · `verify.sh` · `VERIFICATION-RUNBOOK.md` · `IEC-001` Q5 / C8 / P5 · `G-10` Validation Gate · `CIOS-15` (`VR-01…VR-14`) |
| **Owner** | `CEP-004` (`CMG-DLG-04`) · `UCCEP-000000` owner (check register) |
| **Bound read contracts** | `RC-06` |
| **Access** | **R** |
| **Platform binding** | `SS-15` `CIOS-VI` (admission-time determinations) · `20` (this mission's self-checks) |
| **UOM attributes served** | `A-15` |
| **Obligation** | Validation SHALL be executed by the one located authority and SHALL NOT be bypassed (`CEP-001` LAW-5). A **self-check is not a validation** (`VR-04`). |
| **Prohibition** | No check added to the located register; no verdict issued over a located concern; no gate re-implemented; no PASS asserted for a check not executed. |
| **Observed state** | **gates 6/14 PASS; blocking failures none; `PROGRAM-000001` checks `CK-CLOSURE-P1`/`P2` NOT-EXECUTED** |
| **Gaps** | **inherited `UCCEP-F-006` / `CIOS-G-05`** (schema validation degrades silently) and **`UCCEP-F-001`** (the planning-closure gate has no reachable PASS state). Both owner-held, undischarged. |

### `REG-11` — Certification Registry *(deliverable 17)*

| Field | Declaration |
|---|---|
| **Question answered** | What is certified, by whom, to what standing, and under what ceiling? |
| **Located register** | `00-BOOK/DATA/certification.json` + rendered `00-BOOK/REGISTRIES/CERTIFICATION-REGISTRY.md` (generated, `RF-7`) |
| **Supporting located sources** | `CEP-005` Certification Constitution · EC-3 certification gate · `IEC-001` Q6 / C9 / P6 · `G-11` · `engine/certification` · `UMB-017`/`UMB-018` (twin certification dimension) · `CIOS-16` (12 rules + the ceiling) · `uccep.json` `certification`, `certification_ceiling` |
| **Owner** | `CEP-005` (`CMG-DLG-05`) · `REG-AUTO-001` (store) |
| **Bound read contracts** | `RC-03`, `RC-06`, `RC-09` (freeze registry — **read so it is never touched**) |
| **Access** | **R** |
| **Platform binding** | `SS-16` `CIOS-CI` (BINDING-ONLY) |
| **UOM attributes served** | `A-16` |
| **Obligation** | Certification standing SHALL NOT be claimed above the declared ceiling. **CIOS certifies nothing** (`CIOS-16` §1). |
| **Prohibition** | No certification entry added; no standing asserted; no self-certification; **no freeze registry entry, ever** — such an act is void and places the Program in HALTED (`CEP-007` II.4, IV.4). |
| **Observed state** | **`UCCEP-000000` `CERTIFIED-PROVISIONAL`, tier `boot`, seal `f10928ff68603bf1`**; ceiling `CERTIFIED-PROVISIONAL`; 31 of 43 artifacts PROVISIONAL |
| **Gaps** | **inherited `CIOS-GAP-08`** (active certification unavailable corpus-wide) and **`CIOS-GAP-03`/`CIOS-G-03`** (no competent ratification authority; `VAC-01` OPEN). Owner: `CEP-005`/`CEP-006` authorities. |

---

## 5. AGGREGATE REGISTRY POSTURE

| Property | Value |
|---|---|
| Registry specifications | **11** (`REG-01 … REG-11`) |
| Specifications binding a located register | **9** |
| Specifications that are **contract-only** (no located register) | **2** — `REG-05` Subsystem, `REG-07` Contract |
| Registers **created** by this mission | **0** |
| Registers **written** by this mission | **0** |
| Register **entries added** | **0** |
| Freeze registry entries added | **0** |
| `id-ledger.json` entries created | **0** |
| Read contracts invented beyond the located `RC-01 … RC-14` | **0** |
| Specifications with an **append** right | **1** — `REG-09`, via `CIOS-P-40` on `PL-C` only |
| Specifications with a **write** right | **0** |
| Specifications carrying an inherited, owner-held gap | **5** — `REG-04` (`GG-6`), `REG-08` (`UCCEP-F-003`), `REG-09` (`UCCEP-F-008`), `REG-10` (`UCCEP-F-006`, `UCCEP-F-001`), `REG-11` (`VAC-01`) |
| Specifications with a gap **this mission introduced** | **0** |
| Questions answered by two registers | **0** (`RF-1` satisfied) |
| New stores, schemas, graphs, allocators or formats | **0** (`RF-2`, `RF-6`) |

**Every write the platform might plausibly want is a breach of a located instrument.** That was `IMR-003A-R1/07` §5's conclusion for CIOS; it holds unchanged for the platform, and it is why nine specifications are read contracts and two are specifications of registers that other authorities must decide whether to build.

---

## 6. REGISTRY RELATIONSHIPS *(directive capability 29 · closes `PGAP-04`)*

`relationships.json` records edges between **artifacts**. Nothing records how the **registers themselves** relate — which derives from which, which is authoritative when two disagree, and which must be regenerated when one changes. That absence is `PGAP-04`.

### 6.1 The six relationship types

Expressed as **edge types on the one located graph** (`RF-2`; `GOV-INT-001` §2.6 — *"never a parallel graph"*). This mission declares the types; **instantiating any edge is `REG-AUTO-001`'s act, not this mission's.**

| ID | Type | Meaning | Located basis |
|---|---|---|---|
| `RR-1` | **DERIVES-FROM** | register B is computed from register A; B is a view and is never authoritative against A | `RF-6`; `AIF-L01` |
| `RR-2` | **PROJECTS** | register B renders A for human consumption; the JSON governs | `RF-7`; `GOV-INT-001` §6.1 |
| `RR-3` | **ALLOCATES-FOR** | register A allocates the identity space register B's entries occupy | `REG-AUTO-001`; `UUP-01` |
| `RR-4` | **GATES** | register A's content is a precondition on an entry entering B | `CEP-001` LAW-5; `G-01…G-14` |
| `RR-5` | **EVIDENCES** | register A holds the evidence discharging B's determinations | `CEP-008`; `UUP-05` |
| `RR-6` | **REGENERATED-BY** | a change in A obliges regeneration of B through transaction `T` | `REG-AUTO-001` §7; `IEC-001` `07` / C10 / RG-3 |

### 6.2 The register relationship graph

| From | Type | To | Consequence |
|---|---|---|---|
| `id-ledger.json` | `RR-3` | `artifacts.json` | every artifact identity is allocated once, by one allocator (`UUP-01`) |
| `artifacts.json` | `RR-1` | `control-tower.json` | portfolio and programme status are **views**; they are never hand-authored and never authoritative against `artifacts.json` |
| `artifacts.json` + `signals.json` | `RR-1` | `twin.json` | the twin is derived state, **not a persistence layer** (`UCI-OPT-001` row 14) |
| `artifacts.json[*].dependencies` | `RR-1` | `relationships.json` `Depends-On` | dependency is one fact expressed in one graph, not two stores |
| `relationships.json` | `RR-1` | `UCOS-RIE-DEPENDENCY-GRAPH.json`, `UCOS-RIE-*` | RIE outputs are derived views; `IP-3` forbids persisting them as fact |
| `00-BOOK/DATA/*.json` | `RR-2` | `00-BOOK/REGISTRIES/*.md`, `PROGRAM-CONTROL-TOWER.md` | rendered registries are generated; the JSON governs (`RF-7`) |
| `uccep.json` `checks` | `RR-4` | `artifacts.json` | a gate verdict conditions registration and certification |
| `closure.json` | `RR-4` | `artifacts.json` | Repository Truth (`CLOSED`, 434 concepts, 0 gaps) conditions admission (`G-06`) |
| `signals.json` + `ucda-decisions.json` | `RR-5` | `uccep.json`, `certification.json` | verdicts and certifications are evidenced, never asserted |
| `certification.json` | `RR-4` | `CEP-007` freeze registry | freeze requires active certification — **currently unavailable** (`VAC-01`) |
| `artifacts.json` | `RR-6` | `control-tower.json`, `twin.json`, `relationships.json`, `00-BOOK/REGISTRIES/*` | one change obliges one regeneration pass through transaction `T`; **no second sync exists** |
| `change-ledger.json` | `RR-6` | `artifacts.json` version/`content_hash` | version and lineage are fields plus edges; **there is no version registry** (`UCI-OPT-001` row 6) |

### 6.3 Properties of the relationship model

| Property | Value | Basis |
|---|---|---|
| Relationship types declared | **6** | §6.1 |
| New graphs introduced | **0** | `RF-2` |
| New edge **instances** created by this mission | **0** — types only | `CIOS-INV-12` |
| New edge vocabulary created | **0** — types are proposed **for** `UKB-ADV-000`'s vocabulary, whose owner admits them | `GOV-INT-001` §2.6 |
| Authoritative-vs-derived pairs made explicit | **6** (`RR-1` rows) | `RF-6` |
| Cycles in the register graph | **0** — `RR-1`/`RR-2` edges run store → view only; `RR-6` runs source → regenerated, never back | `CIOS-INV-05` |
| Gate for admission of these edge types | **`PG-05`** | `23` |

**The model's practical value:** it makes the *authoritative-versus-derived* distinction machine-checkable. Six pairs are declared derived, so a future programme that treats `control-tower.json`, `twin.json`, a rendered registry or a RIE output as a source of truth is committing a stateable, detectable error rather than an undocumented one.

---

## 7. WHAT THIS ARTIFACT DOES NOT DO

| Not done | Located owner / reason |
|---|---|
| Create, write, or add an entry to any register | `CIOS-INV-12`; `REG-AUTO-001` owns transaction `T` |
| Create a subsystem register or a contract register | `PGAP-02`, `PGAP-03`; gates `PG-03`, `PG-04` |
| Create registers 8–11 (`changes`/`knowledge`/`regeneration`/`rollback.json`) | `UCI-001`; `GG-3` undischarged |
| Add an edge instance or an edge type to `relationships.json` | `REG-AUTO-001`; `UKB-ADV-000`; `PG-05` |
| Add a 15th read contract | `IMR-003A-R1/07` owns the 14; `CIOS-L-08` |
| Add a check to the validation register or a verdict to any programme | `CEP-004`; `UCCEP-000000` owner |
| Add a certification entry, or any freeze registry entry | `CEP-005`; `CEP-007` — an entry would be **void** |
| Regenerate `closure.json`, `artifacts.json`, `control-tower.json` or `twin.json` | `IEC-001` `07` / C10 / RG-3; `REG-AUTO-001` |
| Discharge `GG-3`, `GG-6`, `UCCEP-F-001`, `UCCEP-F-003`, `UCCEP-F-006`, `UCCEP-F-008` or `VAC-01` | each owner-held; recorded in `23` |

---

## AUTHORITY BOUNDARY (MANDATORY)

This artifact declares a registry admissibility test, eleven registry **specifications** and six register relationship **types**. **It creates no registry, writes to no registry, and adds no entry to any registry.** Two specifications describe registers that do not exist and are recorded as gaps with named prospective owners and open gates; nine bind located registers read-only, with a single append right exercised through a located mechanism. The freeze registry and the FROZEN population are unchanged. No relationship edge is instantiated. Every owner named is located in an instrument existing independently at `b26c5bb`. Where this artifact and a located canonical instrument disagree, **the located instrument governs and this artifact SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `IMR-0000/07` · PROVISIONAL · ADDITIVE · DESIGN-ONLY · AUTHORITY-NEUTRAL**
