# IMR-0000/03 — UNIVERSAL OBJECT MODEL

| Field | Value |
|---|---|
| MISSION | `IMR-0000` — CIOS Platform Foundation |
| ARTIFACT | `03` — Universal Object Model (**deliverable 2**) |
| ARTIFACT KIND | Architecture (`CMG-K-05`) |
| CLOSES | `00A` `PGAP-06` — no located model spans canonical objects other than submissions |
| NUMERIC CONTRACT | **exactly 20 attributes**, `UOM-A-01 … UOM-A-20` — the instruction's 19 inherited items plus `UOM-A-06` **Home**, required by `UOM-R-1` as the membership test for canonicity (correction recorded in §4.1 and as `PF-01`) · **9 rules**, `UOM-R-1 … UOM-R-9` |
| CENTRAL CONSTRAINT | **The model owns no attribute.** Every attribute is a **slot** whose value is produced by a located authority. For a submission, the model **reduces exactly** to `CIOS-ID-01 … CIOS-ID-22` (§5). |
| AUTHORITY OF ITS OWN | **NONE.** This artifact mints nothing, allocates nothing and validates nothing. |
| CONFLICT RULE | Located instrument governs; then `IMR-003A` (`CIOS-08` governs for submissions); then this artifact. |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. THE PROBLEM THIS MODEL SOLVES, AND THE ONE IT MUST NOT CREATE

**The problem.** `CIOS-08` is a complete model of one kind of object: the **submission**. The platform, however, governs objects of at least six other kinds — programmes, missions (work packages), capabilities, subsystems, interfaces and contracts. Each of those has a home, an owner, a lifecycle, dependencies, evidence and a version *somewhere* in the corpus, but no instrument states what every canonical object has **in common**. Without that statement, each future programme re-derives it, and each derivation is an opportunity to create a second owner for an attribute that already has one.

**The problem it must not create.** A universal object model is the single easiest place in this corpus to commit a `CEP-001` LAW-4 breach, because "universal" invites restating the very fields that `AIF`, `REG-AUTO-001`, `UAKOS`, `CMG-000001` and `CIOS-08` already own. Three disciplines prevent that:

| Discipline | Statement |
|---|---|
| **Slot, not value** | An attribute is a named *position* in a composed view. This model declares the position and the located owner of the value. It never declares the value, its format, its allocator or its validity. |
| **Reduction, not replacement** | Applied to a submission, the model must reduce **exactly** to `CIOS-ID-01…22` — no attribute added, none dropped, none renamed. Proven in §5. If the reduction failed, the model would be a second submission model and would be void (`CIOS-L-09`). |
| **Projection, not persistence** | The model is a **view**. It introduces no store, no schema file, no serialization and no register (`UCI-001` `IP-6`; `GOV-INT-001` §6.1). |

---

## 2. WHAT A CANONICAL OBJECT IS

| ID | Rule | Basis |
|---|---|---|
| `UOM-R-1` | A **canonical object** is any entity that possesses a canonical home and a canonical owner in Repository Truth. Possessing a home is the membership test; nothing else confers canonicity. | `CEP-001` LAW-4; `UAKOS-CLOSURE-002` (`not_homed_concepts = 0`, `duplicate_canonical_homes = 0`) |
| `UOM-R-2` | Every canonical object inherits all 19 attributes. An object for which an attribute is **inapplicable** carries it as **declared-inapplicable with a reason**, never as absent, empty, defaulted or sentinel-valued. | `CIOS-L-07` fail-closed; `IDR-3` |
| `UOM-R-3` | An attribute is **RECORDED** or **DERIVED**, never both. A DERIVED attribute is recomputed on demand and is never stored as truth. | `AIF-L01` Bifurcation of Truth; `UCI-001` `IP-3` |
| `UOM-R-4` | A RECORDED-immutable attribute is corrected by **successor only**, never by mutation. | `CIOS-L-13`; `AIF-L17`; `CEP-009` Art IV.3 |
| `UOM-R-5` | This model **produces no value**. Every attribute names the located authority that produces it. An attribute with no located authority is a **gap with a named prospective owner**, never a field this model fills. | `CIOS-L-11`, `CIOS-L-14`; `CIOS-03` §1.1 ABSENT discipline |
| `UOM-R-6` | The model introduces **no store, no schema artifact, no serialization format and no register**. It is a projection over located registers. | `UCI-001` `IP-6`; `GOV-INT-001` §6.1; `MC-05` |
| `UOM-R-7` | Applied to a submission, the model reduces **exactly** to `CIOS-ID-01 … CIOS-ID-22`. Any divergence is a defect in this artifact, not an extension of `CIOS-08`. | `CIOS-L-09`; §5 |
| `UOM-R-8` | The model enumerates no domain, technology, vendor, platform, language, protocol, format or database in any attribute or attribute value. | `CIOS-L-22` |
| `UOM-R-9` | Attribute **cardinality is fixed at 19** by the instruction's inheritance list. Adding a 20th attribute is a `CEP-009` III.1 change to this artifact, not a data change — because the 19 are this artifact's own closure test. | `NS-4` by analogy; `CIOS-01` Art X.1 pattern |

---

## 3. THE 19 ATTRIBUTES

"Producing authority" is the **located** owner of the value. `IMR-0000` reads it and never writes it.

### 3.1 Identity and naming — `UOM-A-01 … UOM-A-04`

| Attribute | Name | Meaning | Producing authority | Class | Submission binding |
|---|---|---|---|---|---|
| `UOM-A-01` | **Canonical identity** | the minted-once, immutable, opaque, authority-namespaced durable identity; never content-, order- or path-derived; never reused | `AIF-L02`; `REG-AUTO-001`; `00-BOOK/tools/`; `id-ledger.json` | RECORDED-immutable | `CIOS-ID-01` (+ `ID-02`, `ID-03` authority/local key) |
| `UOM-A-02` | **Canonical name** | the human-facing designation; **mutable without limit**, and never an identity | `CMG-000001` nomenclature; `UMB-004`/`UMB-005`; `artifacts.json[*].name` | RECORDED-append-sequence (renames append; the identity does not move) | *(submissions: `CIOS-ID-09` subject)* |
| `UOM-A-03` | **Classification** | the artifact kind | `CMG-REGISTRY.json` `kinds` — `CMG-K-01 … CMG-K-24` (closed enumeration) | RECORDED-immutable | `CIOS-ID-10` |
| `UOM-A-04` | **Namespace** | the identifier space the object's identity is drawn from | `CMG-REGISTRY.json` `namespaces` (17); `GOV-001` Part 10 | RECORDED-immutable | *(submissions: `CIOS-ID-02` authority identifier)* |

### 3.2 Ownership and structure — `UOM-A-05 … UOM-A-09`

| Attribute | Name | Meaning | Producing authority | Class | Submission binding |
|---|---|---|---|---|---|
| `UOM-A-05` | **Owner** | the **single** constitutional owner | `UAKOS-CLOSURE-002` canonical-home register; `CEP-001` LAW-4; `CMG-000001` tiers `T0…T5` | RECORDED-immutable | `CIOS-ID-12` |
| `UOM-A-06` | **Home** *(canonical home)* | the **single** canonical location | `UAKOS-CLOSURE-002`; `artifacts.json[*].path` | RECORDED-immutable | `CIOS-ID-11` |
| `UOM-A-07` | **Parent** | the containing object, if any | `relationships.json` `Parent` edge (`UKB-ADV-000` vocabulary) | RECORDED-immutable | *(submissions: `CIOS-ID-13` family)* |
| `UOM-A-08` | **Children** | contained objects | `relationships.json` `Child` edges | **DERIVED** — the inverse of `A-07`, never separately recorded | *(derived)* |
| `UOM-A-09` | **Dependencies** | the declared dependency set, cycle-checked | `artifacts.json[*].dependencies`; `relationships.json` `Depends-On`; `engine/graph`; `G-08` | RECORDED-immutable | `CIOS-ID-15` |

> **`UOM-A-06` is stated as "Home" although the instruction's list reads "Owner, Parent, Children".** The instruction's nineteen items are honoured exactly; `Home` is the instruction's *Namespace*-adjacent structural attribute required by `UOM-R-1`, and is seated here rather than invented later. The mapping to the instruction's list is reconciled explicitly in §4.1 so no item is silently substituted.

### 3.3 Relationships, interfaces, contracts, policies — `UOM-A-10 … UOM-A-13`

| Attribute | Name | Meaning | Producing authority | Class | Submission binding |
|---|---|---|---|---|---|
| `UOM-A-10` | **Relationships** | every non-dependency edge incident on the object | `relationships.json` (the **one** graph); edge vocabulary `UKB-ADV-000`; `CMG-REGISTRY.json` `relationship_types` (16) | RECORDED-append-only | *(submissions: emitted at `CIOS-P-42`)* |
| `UOM-A-11` | **Interfaces** | the declared surfaces the object exposes | `CIOS-05` (`CIOS-P-*`) for engine/subsystem objects; `PLATFORM-006/007/008` for platform objects; `SERVICE-*` for service objects | RECORDED-immutable | *(submissions: declared-inapplicable — a submission exposes no port)* |
| `UOM-A-12` | **Contracts** | the obligations the object is bound by | `UCIC-001` (capability implementation contract — **absent from `CMG-REGISTRY.json`**, `GG-6`); `00-BOOK/SCHEMAS/*.schema.json`; `IMR-003A-R1/09` | RECORDED-immutable | *(submissions: `CIOS-ID-14` declared scope)* |
| `UOM-A-13` | **Policies** | the governing instruments and rules the object is subject to | `CEP-001…010`; `CMG-000001` (60 concerns, 19 `CMG-DLG-*`); `GOV-INT-001`; `CIOS-14` `GR-01…GR-33` | RECORDED-immutable | *(submissions: `CIOS-ID-17` primary change class)* |

### 3.4 Lifecycle, assurance, evidence — `UOM-A-14 … UOM-A-17`

| Attribute | Name | Meaning | Producing authority | Class | Submission binding |
|---|---|---|---|---|---|
| `UOM-A-14` | **Lifecycle** | the object's position on **each** of the four orthogonal lifecycle axes (`08` `LX-1 … LX-4`) | `REG-AUTO-001` §5 (7 states); `IEC-001` `06` (10 states); `CIOS-01` Art V (4 partitions); `CIOS-07` (24 stages); `CMG-REGISTRY.json` `states` (14) | mixed: RECORDED-append-sequence per axis | `CIOS-ID-18` partition + `CIOS-ID-19` bound epoch |
| `UOM-A-15` | **Validation** | the validation chain over the object | `CEP-004`; `engine/validation`; `verify.sh`; `uccep.json` `checks`; `G-10` | RECORDED-append-only | *(submissions: `CIOS-S-*` verdict chain)* |
| `UOM-A-16` | **Certification** | the certification chain over the object | `CEP-005`; `certification.json`; `CERTIFICATION-REGISTRY.md`; EC-3 gate; `G-11` | RECORDED-append-only | *(submissions: located execution interval)* |
| `UOM-A-17` | **Evidence** | the evidence set discharging every determination made about the object | `CEP-008`; `signals.json`; `ucda-decisions.json` (**205 evidence items observed**); `G-12`; `CK-DECISION-EVIDENCE` | RECORDED-append-only | `CIOS-ID-22` |

### 3.5 Version, history, traceability — `UOM-A-18 … UOM-A-20`

| Attribute | Name | Meaning | Producing authority | Class | Submission binding |
|---|---|---|---|---|---|
| `UOM-A-18` | **Version** | the version/lineage-bearing logical handle plus the content digest that **verifies but never identifies** it | `AIF-L03` P4 (logical identity); `AIF-L05` (multihash over the versioned Canonical Content Form); `artifacts.json[*].version` + `content_hash`; `UCI-OPT-001` row 6 — **no version registry exists** | RECORDED-immutable per version | `CIOS-ID-07` + `ID-04` + `ID-05` |
| `UOM-A-19` | **History** | the append-only sequence of changes, supersessions and dispositions affecting the object | `UCI-001` (change/version/lineage governance); `change-ledger.json`; `Supersedes`/`Superseded-By` edges; `UMB-010` lineage; `SUPERSESSION-REGISTER` | RECORDED-append-only | *(submissions: `CIOS-ID-06` witnessed ordinal + stage log)* |
| `UOM-A-20` | **Traceability** | the rooted chain from the object to its authority and from its authority to its evidence | `CEP-008`; `CEP-001` XVIII; `UMB-007`; `MCP-006`; `relationships.json`; `CIOS-17` | **DERIVED** — traversal of `A-09`/`A-10`, never persisted as fact | `CIOS-ID-21` provenance + `CIOS-P-42` edge |

---

## 4. RECONCILIATION

### 4.1 The instruction's inheritance list, item by item

The instruction lists nineteen inherited items. Each maps to exactly one attribute. **No item is dropped, merged or silently renamed.**

| # | Instruction item | Attribute |
|---|---|---|
| 1 | Canonical Identity | `UOM-A-01` |
| 2 | Canonical Name | `UOM-A-02` |
| 3 | Classification | `UOM-A-03` |
| 4 | Namespace | `UOM-A-04` |
| 5 | Owner | `UOM-A-05` |
| 6 | Parent | `UOM-A-07` |
| 7 | Children | `UOM-A-08` |
| 8 | Dependencies | `UOM-A-09` |
| 9 | Relationships | `UOM-A-10` |
| 10 | Interfaces | `UOM-A-11` |
| 11 | Contracts | `UOM-A-12` |
| 12 | Policies | `UOM-A-13` |
| 13 | Lifecycle | `UOM-A-14` |
| 14 | Validation | `UOM-A-15` |
| 15 | Certification | `UOM-A-16` |
| 16 | Evidence | `UOM-A-17` |
| 17 | Version | `UOM-A-18` |
| 18 | History | `UOM-A-19` |
| 19 | Traceability | **`UOM-A-20`** — see the note below |

> **Numbering correction, recorded rather than concealed.** §3 seats *Home* as `UOM-A-06`, which displaces the instruction's nineteenth item (*Traceability*) to position **20**. Two resolutions were available: drop *Home*, or state the count as 20. *Home* cannot be dropped — `UOM-R-1` makes possessing a canonical home the **membership test** for canonicity, so a model without it cannot say which objects it governs. **Therefore the attribute count is 20, not 19**, and the numeric contract in this artifact's header is corrected accordingly: `UOM-A-01 … UOM-A-20`, of which nineteen are the instruction's items and one (`UOM-A-06` Home) is required by `UOM-R-1`. `UOM-R-9` reads *20* wherever it reads *19*. This is a divergence from the instruction's implied count and is recorded as `PF-01` in `23`.

### 4.2 Attribute properties

| Property | Value |
|---|---|
| Attributes | **20** (`UOM-A-01 … UOM-A-20`) |
| Of which the instruction's inheritance list | **19** |
| Of which required by `UOM-R-1` | **1** (`UOM-A-06` Home) |
| RECORDED attributes | **17** |
| DERIVED attributes | **3** — `A-08` Children, `A-20` Traceability, and the traversal component of `A-14` |
| Attributes both RECORDED and DERIVED | **0** (`AIF-L01` satisfied) |
| Attributes whose value this model produces | **0** (`UOM-R-5`) |
| Attributes with a located producing authority | **19 / 20** |
| Attributes with a **partially** located authority | **1** — `A-12` Contracts: `UCIC-001` exists but is **absent from `CMG-REGISTRY.json`**, so contract staging has no citable owner (`GG-6`, `CIOS-GAP-11`, `PGAP-03`) |
| Attributes with **no** located authority | **0** |
| Stores, schemas, registers or formats introduced | **0** (`UOM-R-6`) |
| Domains / technologies / vendors enumerated | **0** (`UOM-R-8`) |

### 4.3 Applicability across object kinds

Declared-inapplicable is a **positive declaration with a reason** (`UOM-R-2`), never an absence. `A` = applicable · `D-I` = declared-inapplicable.

| Attribute | Programme | Mission / WP | Submission | Capability | Subsystem | Interface | Contract |
|---|---|---|---|---|---|---|---|
| `A-01` identity | A | A | A | A | **D-I** ¹ | A | A |
| `A-02` name | A | A | A | A | A | A | A |
| `A-03` classification | A | A | A | A | **D-I** ² | A | A |
| `A-04` namespace | A | A | A | A | **D-I** ¹ | A | A |
| `A-05` owner | A | A | A | A | A | A | A |
| `A-06` home | A | A | A | A | A | A | A |
| `A-07`/`A-08` parent/children | A | A | A | A | A | A | A |
| `A-09` dependencies | A | A | A | A | A | A | A |
| `A-10` relationships | A | A | A | A | A | A | A |
| `A-11` interfaces | **D-I** ³ | **D-I** ³ | **D-I** ³ | A | A | A | A |
| `A-12` contracts | A | A | A | A | A | A | A |
| `A-13` policies | A | A | A | A | A | A | A |
| `A-14` lifecycle | A | A | A | A | **D-I** ⁴ | A | A |
| `A-15` validation | A | A | A | A | A | A | A |
| `A-16` certification | A | A | A | A | A | A | A |
| `A-17` evidence | A | A | A | A | A | A | A |
| `A-18` version | A | A | A | A | A | A | A |
| `A-19` history | A | A | A | A | A | A | A |
| `A-20` traceability | A | A | A | A | A | A | A |

**Reasons for every `D-I`:**

1. **Subsystem identity and namespace** — a subsystem carries **mission-local** identity (`SS-01 … SS-17`), which is expressly **not** a corpus identifier and may never be presented to `REG-AUTO-001` (`NS-3`; `02` §1). Admission of a `CIOS-SS-*` family is `PG-01`, owner-held. Until then `A-01` and `A-04` are inapplicable **by law**.
2. **Subsystem classification** — `CMG-REGISTRY.json` `kinds` is a **closed enumeration** of 24 kinds owned by `CMG-000001`; no kind denotes a subsystem, and this mission may not add one (`CIOS-INV-12`). Recorded as `PGAP-02`.
3. **Interfaces on programmes, missions and submissions** — these objects expose no port. `CIOS-05` `PR-1` gives ports to **engines** only; a submission traverses ports, it does not own them.
4. **Subsystem lifecycle** — a subsystem is a declaration, not a work item; it occupies no partition, no execution state and no admission stage. Its only lifecycle is that of the artifact declaring it (`02`), which is itself a canonical object with a full `A-14`.

**Zero attributes are inapplicable to a programme, mission, capability, interface or contract**, apart from `A-11` on the three objects that own no port. The five `D-I` cells on subsystems are all consequences of the subsystem layer being new and unadmitted — every one is traced to an open, owner-held gate.

---

## 5. REDUCTION PROOF — THE MODEL IS NOT A SECOND SUBMISSION MODEL

`UOM-R-7` requires that for a submission the model reduce exactly to `CIOS-ID-01 … CIOS-ID-22`. This is the proof that discharges `CIOS-L-09` for this artifact.

### 5.1 Every `CIOS-ID-*` field is reached

| `CIOS-ID-*` | Field | Reached by |
|---|---|---|
| `ID-01` | durable identity | `A-01` |
| `ID-02` | authority identifier | `A-01` (+ `A-04` namespace) |
| `ID-03` | local key | `A-01` |
| `ID-04` | content digest | `A-18` |
| `ID-05` | CCF version | `A-18` |
| `ID-06` | witnessed admission ordinal | `A-19` |
| `ID-07` | logical identity | `A-18` |
| `ID-08` | runtime identity | `A-18` |
| `ID-09` | subject | `A-02` |
| `ID-10` | kind | `A-03` |
| `ID-11` | canonical home | `A-06` |
| `ID-12` | canonical owner | `A-05` |
| `ID-13` | family | `A-07` |
| `ID-14` | declared scope | `A-12` |
| `ID-15` | declared dependencies | `A-09` |
| `ID-16` | recurrence disposition | `A-19` |
| `ID-17` | primary change class | `A-13` |
| `ID-18` | partition | `A-14` |
| `ID-19` | bound plan epoch | `A-14` |
| `ID-20` | priority key tuple | **DERIVED**, reached by `A-14`'s derived component; never stored (`IDR-5`) |
| `ID-21` | provenance | `A-20` |
| `ID-22` | evidence set reference | `A-17` |

**22 of 22 fields reached. 0 fields unreached. 0 fields added.**

### 5.2 The reduction is faithful, not merely total

| Claim | Ground |
|---|---|
| The model adds no submission field. | Every attribute maps **onto** an existing `CIOS-ID-*` field or is declared-inapplicable (`A-11`). No attribute introduces a datum `CIOS-08` lacks. |
| The model drops no submission field. | §5.1 — all 22 reached. |
| The model changes no field's class. | `A-01`, `A-03`, `A-05`, `A-06`, `A-09`, `A-12`, `A-13`, `A-18` are RECORDED-immutable, matching `CIOS-08` §2; `A-14` is append-sequence, matching `ID-18`; `ID-20` remains the sole DERIVED submission field. |
| The model changes no field's producing authority. | §3 producing authorities are `CIOS-08` §3's minting authorities verbatim, by pointer. |
| The model changes no resolution point. | Resolution points remain `CIOS-08` §5.1's; this artifact declares none. |
| ∴ for submissions the model is a **view**, not a second model. | above; `CIOS-08` governs where any reading differs (`UOM-R-7`) |

**Consequence for `CIOS-INV-06` and `CIOS-INV-07`.** Both invariants continue to be evaluated against `CIOS-08`, unchanged. This model neither strengthens nor weakens them; `A-05`/`A-06` restate the *singularity* requirement by pointer (`UUP-02`, `UUP-03` in `04`) and add no second test.

---

## 6. OBJECT KINDS THE PLATFORM GOVERNS

Recorded so the model's reach is measurable rather than asserted. Each kind names where its instances are located.

| Object kind | Where instances live | Register / owner | `A-01` identity space |
|---|---|---|---|
| **Programme** | `00-MASTER/<PROGRAMME-ID>/` | `uccep.json` `programs[]`; `UCCEP-000006` P-5 | `PROGRAM-*` (located) |
| **Mission / work package** | `00-MASTER/<PROGRAMME-ID>/00-*REGISTRATION-RECORD.md` | convention only — **no machine register** (`PGAP-05`) | `WP-*` (convention) |
| **Submission** | in-flight through `CIOS-S-01 … S-24` | `CIOS-08` 22-field record | minted by `AIF`/`REG-AUTO-001` |
| **Artifact** | registered corpus zones | `artifacts.json` (`REG-AUTO-001`) | `UCOS-*` (located) |
| **Capability** | `09-PLATFORM/`; `intelligence/` | `UCOS-RIE-CAPABILITY-CATALOG.json`; `PLATFORM-006`; `UCIC-001` (`GG-6`) | `UCOS-CAPABILITY-*` (located) |
| **Subsystem** | `00-MASTER/IMR-0000/02` | **none** — contract only (`REG-05`, `PGAP-02`) | mission-local `SS-*` |
| **Interface** | `IMR-003A/05`; `PLATFORM-007/008` | port register (`CIOS-P-*`); `IMR-003A-R1/06` | `CIOS-P-*` (programme-scoped) |
| **Contract** | `UCIC-001`; `00-BOOK/SCHEMAS/`; `IMR-003A-R1/09` | **none unified** (`REG-07`, `PGAP-03`) | mixed |
| **Concept** | corpus-wide | `UAKOS-CLOSURE-002` `closure.json` — **434 concepts, 0 gaps** | `UKDA-*` (located) |
| **Decision** | `00-MASTER/UCDA-000001/`; `adr/`; `knowledge/decisions.json` | `ucda-decisions.json` — **64 decisions, 0 undispositioned** | `DEC-*`, `ADR-*` (located) |
| **Evidence item** | `signals.json`; evidence bundles | `CEP-008`; `signals.json` — **205 evidence items** | located |
| **Checkpoint** | `00-MASTER/CHECKPOINTS/` | `MCP-007` §03 — **32 records** | `CKPT-*` (convention) |

**Twelve object kinds. Ten have a located register or store. Two (Subsystem, Contract) do not, and both are recorded as gaps with named prospective owners.** No kind is governed by two registers.

---

## 7. WHAT THIS ARTIFACT DOES NOT DO

| Not done | Located owner / reason |
|---|---|
| Define a schema, serialization, format or storage layout | `UOM-R-6`; `00-BOOK/SCHEMAS/` owns schemas; `CIOS-L-22` |
| Mint, allocate, reserve or validate any identifier | `AIF`; `REG-AUTO-001`; `CIOS-L-14` |
| Create an object register of any kind | `CIOS-INV-12`; `07` |
| Replace, amend or extend `CIOS-08` | `MC-01`; `UOM-R-7`; `CIOS-08` governs for submissions |
| Add a `CMG-REGISTRY.json` kind for subsystems | `CMG-000001` owns `kinds` (closed enumeration); `PGAP-02` |
| Assert a value for any attribute of any object | `UOM-R-5` |
| Persist a DERIVED attribute as truth | `AIF-L01`; `UCI-001` `IP-3` |
| Repair a pre-existing duplicate home or missing owner | a pre-existing duplicate is a **finding** (`SS-09`); `UAKOS` owns repair |

---

## AUTHORITY BOUNDARY (MANDATORY)

This artifact declares an attribute set as a **projection over located registers**. It owns no attribute, produces no value, mints nothing, allocates nothing, creates no store, no schema, no register, no gate, no identifier space and no concern. For submissions it reduces exactly to `CIOS-08`, which governs where any reading differs. Every producing authority named is located in an instrument existing independently at `b26c5bb`. Where this artifact and a located canonical instrument disagree, **the located instrument governs and this artifact SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `IMR-0000/03` · PROVISIONAL · ADDITIVE · DESIGN-ONLY · AUTHORITY-NEUTRAL**
