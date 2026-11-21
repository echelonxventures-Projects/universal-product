# Output 1 — Decision Family **GDR-A** · Execution Ownership and Generator Architecture

> **STATUS DOMAIN:** GOVERNANCE (determination) · **STATUS BASIS:** located clauses of `GOV-INT-001` (`CMG-DLG-16`) and `REG-AUTO-001` (`CMG-DLG-13`), plus repository evidence resolving at HEAD `9de85ad`

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000008` · OUTPUT 1 |
| FAMILY | **GDR-A** — Execution Ownership and Generator Architecture |
| DECISIONS | `GD-01` (DDI-01) · `GD-02` (DDI-04) · `GD-03` (DDI-07) · `GD-04` (DDI-11) |
| FAMILY SUBJECT | Which single instrument owns consolidated execution; whether UCCEP may be that instrument; which generator owns which output; whether new generators may be created. |
| AUTHORITY | None of its own. Each decision is rendered within the located Owner's already-declared law (Output 0 §2). |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier T1 VACANT; every determination PROVISIONAL under `CMG-L-12` (condition **C-3**, constraint **K-09**). |

---

## GD-01 — Single execution ownership

| Field | Record |
|---|---|
| **Decision ID** | `GD-01` |
| **Title** | Single execution ownership of consolidated execution |
| **Resolves** | `DDI-01` |
| **Family** | GDR-A |

### Problem Statement

`UCCEP-000007` Output 16 records that which single instrument owns consolidated execution has no repository trace: `GOV-INT-001` §2.15 and SECTION 8 already fix **one** execution architecture, and whether that stands, is extended, or is superseded by the consolidation is a determination its owner must make. Measurement cannot choose among lawful alternatives.

### Repository Evidence

| Evidence | What it establishes | Located at |
|---|---|---|
| `GOV-INT-001` §2.15 *"Execution Architecture (Analysis 15) — ONE ARCHITECTURE"* — `ukb.py build/validate` · `ukbx.py twin/portal/validate/twin --check` · `register.sh` (transaction `T`, extended) · `connectors/`; *"No new engine is introduced"* | One execution architecture is already declared and closed | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-GOV-INT-001-GOVERNANCE-INTEGRATION-AND-EXECUTION-ARCHITECTURE-DETERMINATION.md` |
| `GOV-INT-001` SECTION 8 — transaction `T`, Phases 0–7, *"One transaction, atomic, idempotent, guarded by the existing three gates. **No second engine, no second sync.**"* | The one execution path, with its phase decomposition | same |
| The toolchain exists on disk | The architecture is realized, not aspirational | `00-BOOK/tools/ukb.py` · `00-BOOK/tools/ukbx.py` · `00-BOOK/tools/register.sh` · `00-BOOK/tools/connectors/` |
| `CMG-REGISTRY.json → concerns[]` `CMG-DLG-16` — concern `governance-integration-and-execution-architecture`, owner `GOV-INT-001`, disposition REUSE | Exactly one Owner resolves; lookup terminates at XVII.2 Step 1 | `00-CMG/CMG-REGISTRY.json` |
| `CMG-REGISTRY.json → concerns[]` `CMG-DLG-03` — concern `execution-operation`, owner `CEP-003` | Execution *operation* is a distinct concern with a distinct Owner | same |

### Constitutional Authority

`GOV-INT-001` (`CMG-DLG-16`) for execution **architecture**; `CEP-003` (`CMG-DLG-03`) for execution **operation** — authorization, dispatch, sequencing, concurrency, checkpointing, suspension, resumption, failure, recovery entry, handoff, completion. Resolution by `CMG-000001` XVII.2 Step 1. Prohibition on a second engine: `CMG-000001` X.14 (`CMG-L-14`) and `CEP-002` 8.3.

### Decision

**The single instrument that owns consolidated execution IS the located execution architecture declared at `GOV-INT-001` §2.15 and SECTION 8 — `ukb.py` · `ukbx.py` · `register.sh` (transaction `T`) · `connectors/` — and the consolidation introduces no execution owner, no second engine, and no second synchronization path.**

Operation of that architecture — authorization, dispatch, sequencing, checkpointing, failure and recovery — remains `CEP-003`'s concern and is not altered.

The architecture **stands**. It is neither extended into a new instrument nor superseded. Where consolidation requires a new derivation step, it is an **append-only phase of transaction `T`** in the form `GOV-INT-001` SECTION 8 Phase 0 already establishes, not a new execution owner.

### Rationale

The determination the owner must make has, in substance, already been made by that owner and recorded: `GOV-INT-001` §2.15 declares ONE architecture and states *"No new engine is introduced"*; SECTION 8 closes the question with *"No second engine, no second sync."* Choosing any other alternative would require creating parallel execution machinery, which `CMG-L-14` prohibits outright and `CEP-002` 8.3 prohibits independently. The remaining lawful content of the decision is therefore its **scope binding**: that the consolidation is inside the existing architecture rather than beside it. That binding is a recognition, not new law, so it requires no authority beyond the clause recognized.

Separating architecture (`CMG-DLG-16`) from operation (`CMG-DLG-03`) is not a refinement introduced here — it is how `CMG-REGISTRY.json` already allocates the two concerns, and conflating them would create a jurisdiction overlap barred by `CEP-002` 4.3 and `CMG-INV-02`.

### Dependencies

| Direction | Item | Nature |
|---|---|---|
| Depends on | `GD-04` (no-new-generators) | Co-determinative: `GD-01` fixes the owner, `GD-04` fixes that no rival is created |
| Depends on | `GD-21` / `DEF-02` (Tier T1 vacancy) | `GOV-INT-001` is PROVISIONAL; this recognition inherits that standing under `CMG-L-12` |
| Depended on by | `GD-02` | `GD-02`'s rejection rests in part on the architecture `GD-01` recognizes |
| Depended on by | `GD-03`, `GD-06`, `GD-14`, `GD-15` | Each presupposes a single execution architecture |
| Blocks | nothing | The decision requires no realization |

### Affected Programmes

`UCCEP-000000` (its bound gates run inside `T` and are unchanged) · `UCDA-000001` and every `00-MASTER/` programme engine (each continues to run in its own write scope, unchanged) · the consolidation itself, which is bound by this decision. **No programme is re-homed, merged, retired, or given execution ownership.**

### Affected Registries

None mutated. The seven located registers (`artifacts.json`, `relationships.json`, `id-ledger.json`, `control-tower.json`, `volumes.json`, `change-ledger.json`, `certification.json`) and the twin/signals pair continue to be written only by the phases of `T` that already write them.

### Affected Constitutions

None amended. `GOV-INT-001` is **cited**, not edited. `CEP-003`, `CMG-000001` X.14 and `CEP-002` 8.3 are cited as the prohibitions relied upon.

### Affected Implementations

None. No code, no tool, no configuration is changed. `00-BOOK/tools/` is read as evidence only.

### Constraints

| Id | Constraint |
|---|---|
| `GD-01-C1` | Any consolidated execution step SHALL be an append-only phase of transaction `T`; it SHALL NOT be a new engine, sync path, scheduler, or daemon. |
| `GD-01-C2` | This decision SHALL NOT be read as ratifying `GOV-INT-001`. `GOV-INT-001` is recorded `PROVISIONAL` / `CMG-K-17` in `CMG-REGISTRY.json` and remains so. |
| `GD-01-C3` | This decision confers no execution authority on this programme, on `UCCEP-000008`, or on any consolidation artifact (`CEP-003` I.5 standard: execution authority is never self-conferred). |

### Acceptance Criteria

1. `grep` of the consolidation's own artifacts yields **no** declaration of an execution owner other than the `GOV-INT-001` §2.15 toolchain.
2. `00-BOOK/tools/` gains no new engine entry point attributable to the consolidation.
3. The located enforcement chain (`CMG-DLG-40`: `Makefile`, `verify.sh`, `repo-ops.sh`, `00-BOOK/tools/`, `.github/workflows/`) continues to pass unchanged, with the same gate count and no new gate.
4. Any future consolidated derivation is discoverable as a phase of `T`, not as a sibling of `T`.

### Traceability

`DDI-01` → `GD-01`. Upstream: `UCCEP-000007/16-DECISION-DERIVED-INPUTS.md` §2 row DDI-01; `UCCEP-000007/07-GENERATED-ARTIFACT-INVENTORY.md` §3 (the measured generator map). Authority chain: `CMG-000001` XVII.2 → `CMG-REGISTRY.json → concerns[] CMG-DLG-16` → `GOV-INT-001` §2.15 / SECTION 8. Onward: `08-DISPOSITION-ROUTING-TABLE.md` row `GD-01`.

### Future Impact

Permanent and load-bearing. Every later consolidation step inherits a single execution path, which is what makes determinism, idempotence and rollback claims meaningful (`GOV-INT-001` SECTION 8 Phase 7). If `GOV-INT-001` is ever superseded under `CEP-007` XIII, this recognition follows the successor by reference and requires no amendment here — that is the point of binding by reference rather than by copy (`GD-09`).

### Disposition

**`CEP-002` 28.13(b) — REPRESENTED BY AN EXISTING CANONICAL CAPABILITY.**
Single canonical owner: **`GOV-INT-001`** (`00-BOOK/CONTROL-TOWER/UCOS-Ω∞-GOV-INT-001-…-DETERMINATION.md`). Evidence: §2.15, SECTION 8, and the located toolchain. No further realization is required, so the lifecycle stage reached is **REPOSITORY MAPPING**, which is the minimum stage 28.13(b) requires. Exactly one canonical owner is named; `CEP-002` 14.3 (duplication finding) is not engaged.

---

## GD-02 — UCCEP as consolidated execution generator

| Field | Record |
|---|---|
| **Decision ID** | `GD-02` |
| **Title** | Whether UCCEP is constituted as the consolidated execution generator |
| **Resolves** | `DDI-04` |
| **Family** | GDR-A |

### Problem Statement

`UCCEP-000007` Output 16 records a **measured tension**: `GOV-INT-001` §2.15 names the `ukb` toolchain as the one execution architecture, while `UCCEP-000000`'s own charter declares `AUTHORITY = NONE`, *"binding and aggregation only"*, and `UCCEP-000000` is **absent** from `CMG-REGISTRY.json`. Whether UCCEP becomes the consolidated execution generator is a determination — and, per `CMG-000001` XVII.8, expressly **not** one UCCEP may make for itself.

### Repository Evidence

| Evidence | What it establishes | Located at |
|---|---|---|
| `UCCEP-000000` is absent from the 51 `artifacts[]` entries of the registry (zero occurrences of the string in the file) | It is not a recognized artifact | `00-CMG/CMG-REGISTRY.json` |
| `CMG-000001` X.1 `CMG-L-01` — *"An unrecognized artifact SHALL NOT be cited as constitutional authority."* | An unrecognized instrument cannot be the authority for an architecture | `00-CMG/CMG-000001-…md` |
| `UCCEP-000000`'s own declaration: `AUTHORITY = NONE`, binding and aggregation only | It claims no such authority itself | `00-MASTER/UCCEP-000000/` (charter and `uccep-bindings.json`) |
| `GOV-INT-001` §2.15 / SECTION 8 — one architecture; *"No second engine, no second sync."* | The role sought is already occupied | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-GOV-INT-001-…md` |
| `CMG-000001` XVII.8 — *"An instrument SHALL NOT determine its own jurisdiction in a contested case"* | UCCEP cannot self-appoint; and this determination is rendered under `CMG-DLG-16`, not by UCCEP | `00-CMG/CMG-000001-…md` |
| `CMG-000001` X.14 `CMG-L-14` — no second registry, lifecycle, traceability store, evidence store, validation engine, certification engine, ratification mechanism or governance body where one exists | A rival generator would be parallel machinery | same |
| `UCCEP-000007` Output 7 §3 — `uccep_engine.py` writes 20 artifacts **within its own directory**, under a fail-closed write-scope guard | Its measured scope is its own outputs, not corpus execution | `00-MASTER/UCCEP-000007/07-GENERATED-ARTIFACT-INVENTORY.md` |

### Constitutional Authority

`GOV-INT-001` (`CMG-DLG-16`) as the Owner of the execution-architecture concern; `CMG-000001` XVII.8 (no self-determined jurisdiction), X.1 `CMG-L-01` (recognition), X.14 `CMG-L-14` (no parallel machinery); `CEP-002` 8.3 (no second pipeline).

### Decision

**REJECTED.** UCCEP — and specifically `UCCEP-000000` — **SHALL NOT** be constituted as the consolidated execution generator, and no UCCEP-family artifact SHALL be cited as the constitutional authority for the execution architecture.

What UCCEP-000000 already owns is **unchanged and retained**: the binding declaration, programme aggregation, the gate and check declarations of `uccep-bindings.json`, and the aggregate certification roll-up. Those are aggregation acts, not execution-generation acts, and nothing in this decision narrows them.

The consolidated execution generator remains the located toolchain recognized in `GD-01`.

### Rationale

Four independent located grounds each dispose of the proposition, and any one suffices:

1. **Recognition.** `CMG-L-01` bars citing an unrecognized artifact as constitutional authority. `UCCEP-000000` has zero entries in `CMG-REGISTRY.json`. Constituting it as the execution generator would require citing it as exactly that.
2. **Self-declaration.** It declares `AUTHORITY = NONE`. `CMG-000001` `CMG-L-12` bars an artifact from declaring a standing higher than a located authority confers; there is no located authority conferring execution generation on it.
3. **Jurisdiction.** XVII.8 forbids an instrument determining its own jurisdiction in a contested case. The case is contested precisely because `GOV-INT-001` §2.15 already occupies the role. Accordingly this rejection is rendered under `CMG-DLG-16`, whose Owner is `GOV-INT-001`, and **not** by UCCEP.
4. **Non-proliferation.** A second execution generator is parallel machinery under `CMG-L-14` and a second pipeline under `CEP-002` 8.3.

The tension `UCCEP-000007` measured is therefore not a genuine contradiction requiring an open question: it is a proposition that located law already forbids. Holding it open would violate LVII.3's converse — a matter that **is** decidable by a located authority is decided, not held.

### Dependencies

| Direction | Item | Nature |
|---|---|---|
| Depends on | `GD-01` | The role is occupied by the architecture `GD-01` recognizes |
| Depends on | `GD-04`, `GD-12` | Same non-proliferation principle applied to generators and registries |
| Related to | `GD-08` / `DEF-01` | Both concern the `AUTHORITY = NONE` convention, but on different facts: `GD-08` concerns *recorded Owners* that declare it; `GD-02` concerns an *unrecorded* artifact. `GD-02` does not resolve, prejudge, or narrow `DEF-01`. |
| Blocks | nothing | A rejection requires no realization (`CEP-002` 28.10) |

### Affected Programmes

`UCCEP-000000` — its scope is confirmed as binding, aggregation and gate declaration; it acquires nothing. `UCCEP-000005` … `000008` — unaffected; each remains a programme writing only its own outputs. No programme is halted, retired, or re-scoped.

### Affected Registries

None. In particular `uccep-bindings.json` is **not** edited — boundary **X-9** forbids it, and this decision requires no change to it.

### Affected Constitutions

None amended. `CMG-000001` XVII.8, X.1, X.14 and `CEP-002` 8.3 are the cited bases of rejection, as `CEP-002` 28.13(d) requires (*"A rejection without a cited basis IS not a disposition"*).

### Affected Implementations

None. `00-MASTER/UCCEP-000000/uccep_engine.py` is unchanged and its write scope is unchanged.

### Constraints

| Id | Constraint |
|---|---|
| `GD-02-C1` | No consolidation artifact SHALL cite any UCCEP-family artifact as constitutional authority for execution architecture, generation, or registration. |
| `GD-02-C2` | This rejection SHALL NOT be read as a finding against `UCCEP-000000`, nor as narrowing its located binding and aggregation role. |
| `GD-02-C3` | Should `UCCEP-000000` ever be admitted to `CMG-REGISTRY.json`, this decision does **not** thereby reverse: reversal would require a fresh determination by the Owner of `CMG-DLG-16`, since grounds 1, 3 and 4 rest on distinct clauses and ground 4 would still stand. |

### Acceptance Criteria

1. No artifact of the consolidation names a UCCEP artifact as execution generator or as constitutional authority.
2. `UCCEP-000000`'s recorded scope in `uccep-bindings.json` is byte-identical before and after this programme.
3. The rejection carries a cited constitutional basis (satisfied: XVII.8, `CMG-L-01`, `CMG-L-14`, `CEP-002` 8.3), so `CEP-002` 28.13(d) is met and the decision is not undispositioned under 28.14.

### Traceability

`DDI-04` → `GD-02`. Upstream: `UCCEP-000007/16-DECISION-DERIVED-INPUTS.md` §2 row DDI-04; `UCCEP-000007/07-GENERATED-ARTIFACT-INVENTORY.md` §3; `UCCEP-000007/03-CONSTITUTION-INVENTORY.md` (recognized artifact set). Authority chain: `CMG-000001` XVII.2 → `CMG-DLG-16` → `GOV-INT-001`; prohibitions from `CMG-000001` X.1 / X.14 / XVII.8 and `CEP-002` 8.3. Onward: `08-DISPOSITION-ROUTING-TABLE.md` row `GD-02`.

### Future Impact

Closes, on located grounds, the largest architectural ambiguity `UCCEP-000007` measured. It fixes the shape of every later consolidation step: consolidation is expressed as **declarations consumed by the existing toolchain**, never as a new generator. It also establishes the reusable test for any future candidate: recognition in the registry, a located authority conferring the standing claimed, no self-determined jurisdiction, and no parallel machinery.

### Disposition

**`CEP-002` 28.13(d) — REJECTED WITH CONSTITUTIONAL JUSTIFICATION.**
Cited basis: `CMG-000001` XVII.8, X.1 (`CMG-L-01`), X.14 (`CMG-L-14`); `CEP-002` 8.3. Justification: the four independent grounds above. Per 28.10 the decision passes from REPOSITORY MAPPING directly toward closure; no realization is required.

---

## GD-03 — Generator responsibilities after consolidation

| Field | Record |
|---|---|
| **Decision ID** | `GD-03` |
| **Title** | Which generator owns which output after consolidation |
| **Resolves** | `DDI-07` |
| **Family** | GDR-A |

### Problem Statement

`UCCEP-000007` Output 7 measures the present generator→output map exhaustively. Whether the consolidation **reassigns** any output to a different generator is a determination; measurement records only the current state.

### Repository Evidence

| Evidence | What it establishes | Located at |
|---|---|---|
| Output 7 §3 — the full measured map: `ukb.py build` → the seven `00-BOOK/DATA/*.json` registers + `00-BOOK/REGISTRIES/*`; `ukbx.py twin/portal/certify` → `twin.json`, `signals.json`, `00-BOOK/PORTAL/*`, certification; `register.sh` → transaction `T` (10 phases); `cmg-gate.sh`/`cmg_validate.py` → validation report and `CMG-REGISTRY.json` only with `--emit`; `uccep_engine.py` → 20 own artifacts; `ucda_engine.py` → 9 own artifacts; the `UAKOS`/`UCCEP-000005` engines → their own registers; `intelligence/rie` → `intelligence/*` | A complete, non-overlapping map already exists, each generator confined to its own zone | `00-MASTER/UCCEP-000007/07-GENERATED-ARTIFACT-INVENTORY.md` |
| Output 7 §5 — regeneration idempotent, digests byte-identical, tree CLEAN; both master engines PASS `--check-determinism`, `--check-write-scope`, `--check-no-enumeration` | The map is mechanically enforced, not merely documented | same |
| `REG-AUTO-001` §7 Atomic Creation Law; §2 seven-register table; §16 enforcement gates | The registration transaction defines what each phase writes | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-REG-AUTO-001-…md` |
| `CMG-REGISTRY.json → concerns[]` `CMG-DLG-13` (registration/identity/classification → `REG-AUTO-001`) and `CMG-DLG-40` (enforcement machinery → the located chain) | The Owners of the map and of its enforcement | `00-CMG/CMG-REGISTRY.json` |
| `GOV-INT-001` SECTION 8 Phases 0–7 | The architectural reference for which generator runs when | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-GOV-INT-001-…md` |

### Constitutional Authority

**`REG-AUTO-001`** (`CMG-DLG-13`) — sole canonical owner for this decision, as the instrument whose §7 Atomic Creation Law and §2 register table define generator responsibility for the register set. `GOV-INT-001` SECTION 8 is cited as the **architectural reference** for phase ordering; citing it as a reference does not make it a second owner (`CEP-002` 14.3 is not engaged). Enforcement is `CMG-DLG-40`'s located chain.

### Decision

**The generator→output map measured at `UCCEP-000007` Output 7 §3 IS the consolidated map. No output is reassigned; no generator is merged, split, retired, or added.**

Three properties are bound for the consolidation:

1. **Exclusive write scope.** Each generator writes only the outputs the measured map attributes to it. A programme engine writes only within its own `00-MASTER/<PROGRAMME-ID>/` home.
2. **Derived outputs are never hand-authored.** Any file the map attributes to a generator is regenerated, never edited in place.
3. **Enforcement is the existing guard set.** `--check-write-scope`, `--check-determinism`, `--check-no-enumeration`, the classification/drift gate, and the `CMG-DLG-40` chain remain the sole enforcement. No new guard is created.

### Rationale

Reassignment has no located justification and three located costs. The measured map is already **total** (every generated artifact has exactly one generator) and already **enforced** (write-scope and determinism guards pass, regeneration is byte-identical). Reassigning an output would (i) require editing another programme's generator, barred by **X-9**; (ii) break the byte-identical regeneration property on which `CEP-001` XX determinism and every seal depends; and (iii) create, at least transiently, two writers for one output — the duplication `CEP-002` 14.3 makes a finding and `CMG-L-14` prohibits.

The lawful content of the decision is therefore its **binding of the measured map as the governing map**, converting a measurement into a constraint the consolidation must satisfy. That is recognition, not reassignment.

### Dependencies

| Direction | Item | Nature |
|---|---|---|
| Depends on | `GD-01` | Generators run inside the one architecture |
| Depends on | `GD-04` | No new generator may enter the map |
| Depends on | `GD-13` | Regeneration-not-editing presupposes append-only/no-deletion |
| Depended on by | `GD-19` | Registers 8–11, when realized, must attach to an existing generator under this map |
| Depended on by | `GD-06` | Identity mapping of programmes presupposes each engine keeps its own zone |

### Affected Programmes

Every programme owning an engine: `UCCEP-000000`, `UCCEP-000005`, `UCDA-000001`, the eight `UAKOS-PHASE-*`/`UAKOS-CLOSURE-*` engines. Each keeps exactly what it has. **No engine is edited by this decision.**

### Affected Registries

None mutated. The seven located registers plus `twin.json`/`signals.json` keep their existing writers. `changes.json`, `knowledge.json`, `regeneration.json`, `rollback.json` do not yet exist; their writer is decided in `GD-19`, not here.

### Affected Constitutions

None amended. `REG-AUTO-001` §2/§7/§16 and `GOV-INT-001` SECTION 8 are cited.

### Affected Implementations

None. No generator source file is modified. `00-BOOK/tools/` and every `00-MASTER/<PROGRAMME-ID>/*_engine.py` are read as evidence only.

### Constraints

| Id | Constraint |
|---|---|
| `GD-03-C1` | A consolidation act SHALL NOT hand-edit any artifact the measured map attributes to a generator. |
| `GD-03-C2` | A consolidation act SHALL NOT widen any generator's write scope, and SHALL NOT introduce a second writer for any output. |
| `GD-03-C3` | Any new derived output SHALL be attached to an existing generator by declaration (a data entry), never by a new generator (`GD-04`). |
| `GD-03-C4` | `00-MASTER/UCCEP-000008/` outputs are **hand-authored governance determinations**, not generated artifacts, and SHALL NOT be attributed to any generator or claimed as regenerable. |

### Acceptance Criteria

1. `UCCEP-000007` Output 7 §3's map, re-derived at any later HEAD, contains the same generator set with no additions attributable to the consolidation.
2. `--check-write-scope` and `--check-determinism` continue to PASS for every engine.
3. Regeneration of any derived artifact remains byte-identical (Output 7 §5 property preserved).
4. No output has two writers.

### Traceability

`DDI-07` → `GD-03`. Upstream: Output 16 §2 row DDI-07; `UCCEP-000007/07-GENERATED-ARTIFACT-INVENTORY.md` §3 and §5; `UCCEP-000007/10-VALIDATION-INVENTORY.md` (the enforcement chain). Authority chain: `CMG-000001` XVII.2 → `CMG-DLG-13` → `REG-AUTO-001` §2/§7. Onward: `08-DISPOSITION-ROUTING-TABLE.md` row `GD-03`; `GD-19` for the only pending attachment.

### Future Impact

Makes generator responsibility a **stable invariant** across the consolidation, which is the precondition for every determinism, idempotence and seal-reproducibility claim later relied upon (`GD-17` in particular, which substitutes deterministic regeneration for committed evidence). It also fixes the mechanism for future growth: new outputs arrive as declarations inside existing generators, so the map grows in rows, never in generators.

### Disposition

**`CEP-002` 28.13(b) — REPRESENTED BY AN EXISTING CANONICAL CAPABILITY.**
Single canonical owner: **`REG-AUTO-001`** (`00-BOOK/CONTROL-TOWER/UCOS-Ω∞-REG-AUTO-001-AUTOMATIC-ARTIFACT-REGISTRATION-STANDARD.md`). Evidence: `REG-AUTO-001` §2/§7/§16; `UCCEP-000007` Output 7 §3 and §5. No further realization required; stage reached is REPOSITORY MAPPING.

---

## GD-04 — No-new-generators policy

| Field | Record |
|---|---|
| **Decision ID** | `GD-04` |
| **Title** | Adoption of the no-new-generators policy as a binding consolidation constraint |
| **Resolves** | `DDI-11` |
| **Family** | GDR-A |

### Problem Statement

Output 16 records that the principle is **located** — `GOV-INT-001` §2.15/SECTION 8 and the `CMG-DLG-40` enforcement chain — but its **adoption as a consolidation policy, and its scope,** is unrecorded.

### Repository Evidence

| Evidence | What it establishes | Located at |
|---|---|---|
| `GOV-INT-001` §2.15 — *"No new engine is introduced by UCI-001. UCI-001 is normative; execution is the existing toolchain."* | The principle, applied by its owner to the largest pending standard | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-GOV-INT-001-…md` |
| `GOV-INT-001` SECTION 8 — *"No second engine, no second sync."*; SECTION 11 — *"Execution engines … READY — no new engine required; append-only extension to `T`"* | The principle as a readiness conclusion, not an aspiration | same |
| `CMG-000001` X.14 `CMG-L-14` | Corpus-level prohibition on parallel machinery | `00-CMG/CMG-000001-…md` |
| `CEP-002` 28.19 — *"No new gate, pipeline, scheduler, or daemon IS created for this purpose"* | The same prohibition applied by the governance constitution to its own newest gate | `00-CEP/CEP-002-…md` |
| `REG-AUTO-001` §21.3 — the reconciled-set record is *"record only"*, never consulted by `classify()`, *"not a register, not a compatibility layer"* | The located precedent for answering a new requirement with a **declaration** instead of machinery | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-REG-AUTO-001-…md` |
| `CMG-DLG-40` owner paths: `Makefile`, `verify.sh`, `repo-ops.sh`, `00-BOOK/tools/`, `.github/workflows/` | The enforcement chain that would have to be duplicated | `00-CMG/CMG-REGISTRY.json` |

### Constitutional Authority

`GOV-INT-001` (`CMG-DLG-16`) §2.15 / SECTION 8 / SECTION 11 as sole canonical owner; `CMG-000001` X.14 (`CMG-L-14`) and `CEP-002` 28.19 / 8.3 as the corpus-level prohibitions; `CMG-DLG-40` as the enforcement locus.

### Decision

**ADOPTED, by reference, as a binding constraint over the entire consolidation scope.**

For the whole of the consolidation and everything it authorizes:

1. **No new generator, engine, pipeline, sync path, gate apparatus, scheduler or daemon SHALL be created.**
2. A new requirement SHALL be met by an **append-only declaration consumed by an existing generator** — a data entry, a schema, a `config.py` family declaration, or an additional phase of transaction `T` — following the located precedent of `REG-AUTO-001` §21.3 and `GOV-INT-001` SECTION 8 Phase 0.
3. **Scope** is explicit: every artifact, declaration and act of the consolidation, at every later mission, including `M-1A` and its successors. The policy is not stage-limited.
4. The policy binds **additively**: it adds no prohibition that `CMG-L-14`, `CEP-002` 8.3 and 28.19 do not already impose. It fixes their **application** to the consolidation, which is the part that was unrecorded.

### Rationale

Output 16's characterization is exact: the principle is located, its adoption is not. Adoption is therefore the whole lawful content of the decision, and adoption of an existing prohibition is a recognition requiring no new authority. Declining to adopt would not create freedom — `CMG-L-14` binds regardless — it would only leave the consolidation without a stated, testable constraint, which is precisely the defect Output 16 records.

The mechanism named in clause 2 is not invented here. `REG-AUTO-001` §21 answered an open constitutional question (`CMG-OQ-06`) by appending a **record**, explicitly not a register and explicitly never consulted by the classifier, and closed the question with zero new machinery and zero drift. That is the located pattern the consolidation inherits.

### Dependencies

| Direction | Item | Nature |
|---|---|---|
| Depends on | `GD-01`, `GD-03` | The architecture and the map this policy protects |
| Co-determinative with | `GD-11`, `GD-12`, `GD-13` | The four non-proliferation/preservation policies form one coherent set (see `03-GDR-C…`) |
| Depended on by | `GD-02` | Ground 4 of that rejection is this policy's premise |
| Depended on by | `GD-19` | Registers 8–11 must be realized as schemas + declarations, **not** as a new engine |
| Depended on by | `GD-14` | A migration engine is barred by this policy as well as by `CEP-009` |

### Affected Programmes

All. Every current and future programme of the consolidation is bound. No existing programme loses a capability, because none currently holds a generator the policy would remove.

### Affected Registries

None mutated. The policy constrains *future* register creation, which is `GD-12`'s subject; here it constrains future *writer* creation.

### Affected Constitutions

None amended. `GOV-INT-001`, `CMG-000001` X.14, `CEP-002` 28.19/8.3 are cited.

### Affected Implementations

None. No tool is added, removed, or modified.

### Constraints

| Id | Constraint |
|---|---|
| `GD-04-C1` | A consolidation act that requires new derivation SHALL express it as a declaration consumed by an existing generator, and SHALL record which generator and which declaration file. |
| `GD-04-C2` | A new schema file is permitted (it is data, not machinery) provided its consumer is an existing generator; a new executable entry point is not. |
| `GD-04-C3` | This policy SHALL NOT be waived, deferred, or scoped down by any later consolidation act, mirroring the non-waiver standard of `CEP-002` 8.5 / 24.4. |
| `GD-04-C4` | `00-MASTER/UCCEP-000008/` introduces no generator, and its outputs are hand-authored; compliance with this policy by the programme that adopts it is recorded, not assumed. |

### Acceptance Criteria

1. At any later HEAD, the generator set of `UCCEP-000007` Output 7 §3 has gained no member attributable to the consolidation.
2. `00-BOOK/tools/` gains no new executable entry point; `.github/workflows/` gains no new pipeline attributable to the consolidation.
3. Every new derived output introduced by the consolidation cites the existing generator that produces it and the declaration that drives it.
4. `verify.sh` and the `CMG-DLG-40` chain pass with an unchanged component inventory.

### Traceability

`DDI-11` → `GD-04`. Upstream: Output 16 §2 row DDI-11; `UCCEP-000007/07-GENERATED-ARTIFACT-INVENTORY.md`; `UCCEP-000007/10-VALIDATION-INVENTORY.md`. Authority chain: `CMG-000001` XVII.2 → `CMG-DLG-16` → `GOV-INT-001` §2.15/SECTION 8/SECTION 11; prohibitions `CMG-L-14`, `CEP-002` 8.3/28.19; precedent `REG-AUTO-001` §21.3. Onward: `08-DISPOSITION-ROUTING-TABLE.md` row `GD-04`; constrains `GD-19`'s work package `WP-GDR-001`.

### Future Impact

The single most constraining decision of this family for future work: it fixes that the consolidation grows by **declaration**, not by **machinery**. Combined with `GD-11` (no undiscovered documents), `GD-12` (no new registries) and `GD-13` (no deletion), it bounds the consolidation's blast radius to append-only data changes inside an unchanged toolchain — which is what makes the rollback anchor `1c6e750e…` a meaningful recovery point.

### Disposition

**`CEP-002` 28.13(b) — REPRESENTED BY AN EXISTING CANONICAL CAPABILITY.**
Single canonical owner: **`GOV-INT-001`**. Evidence: §2.15, SECTION 8, SECTION 11; `CMG-000001` X.14; `CEP-002` 28.19. No realization required; stage reached is REPOSITORY MAPPING.

---

## Family summary — GDR-A

| GD | DDI | Decision in one line | Disposition | Realization required |
|---|---|---|---|---|
| `GD-01` | DDI-01 | The located `GOV-INT-001` §2.15 toolchain owns consolidated execution; nothing is added beside it | (b) | none |
| `GD-02` | DDI-04 | UCCEP is **not** the consolidated execution generator; its binding/aggregation role is retained | (d) | none |
| `GD-03` | DDI-07 | The measured generator→output map is the consolidated map; no output is reassigned | (b) | none |
| `GD-04` | DDI-11 | No-new-generators is adopted as a binding constraint over the whole consolidation scope | (b) | none |

**Family properties:** 4 decisions · 3 recognitions + 1 rejection · **zero** work packages · **zero** repository mutations · zero constitutions amended · zero registries touched. Every disposition's evidence resolves at HEAD `9de85ad` (verified in `09-TRACEABILITY-VERIFICATION.md` §3).

---

*`UCCEP-000008` Output 1, family GDR-A. Decisions rendered within the located law of `GOV-INT-001` (`CMG-DLG-16`) and `REG-AUTO-001` (`CMG-DLG-13`). No authority created, no law legislated, no implementation performed. `CERTIFIED-PROVISIONAL`; Tier T1 VACANT; PROVISIONAL under `CMG-L-12`.*
