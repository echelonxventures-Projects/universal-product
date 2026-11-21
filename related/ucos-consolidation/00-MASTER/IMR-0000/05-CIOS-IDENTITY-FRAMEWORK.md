# IMR-0000/05 — CIOS IDENTITY FRAMEWORK

| Field | Value |
|---|---|
| MISSION | `IMR-0000` — CIOS Platform Foundation |
| ARTIFACT | `05` — CIOS Identity Framework (**deliverable 5**) · directive capability 7 (identity governance) |
| ARTIFACT KIND | Framework (`CMG-K-05`) — binding declaration |
| SUBSYSTEM | `SS-02` `CIOS-IDENTITY` (engine `E-07`, ports `P-13`/`P-14`, both internal) |
| CENTRAL CONSTRAINT | **The platform mints nothing.** Identity is minted by located authorities; the platform composes, asserts completeness, and fails closed. |
| AUTHORITY OF ITS OWN | **NONE.** `CIOS-01` I.5 — CIOS holds no identity authority. |
| CONFLICT RULE | Located instrument governs (`AIF`, then `REG-AUTO-001`); then `IMR-003A` (`CIOS-08` governs the submission record); then this artifact. |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. THE LOCATED IDENTITY AUTHORITY

| Authority | Home | What it owns |
|---|---|---|
| **`AIF`** — Absolute Identity Federation & Continuity Constitution | `02-MASTER/UCOS-Ω∞-ABSOLUTE-IDENTITY-FEDERATION-AND-CONTINUITY-CONSTITUTION.md` | the five orthogonal identity planes (`AIF-L03`); bifurcation of truth (`AIF-L01`); durable identity (`L02`); ordering authority (`L04`); content digest semantics (`L05`); authority/local key (`L06`); uniqueness (`L07`); append-only truth (`L08`); signed events (`L11`); forward-only compensation (`L17`) |
| **`REG-AUTO-001`** — Automatic Artifact Registration Standard | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-REG-AUTO-001-…` | *"Artifact Creation = Artifact Registration"*; the single registration transaction `T`; `id-ledger.json` allocation; `artifacts.json` |
| **`00-BOOK/tools/`** | tooling | the allocator implementation and the registration-exclusion configuration (`config.py :: EXCLUDE_DIR_PREFIXES`) |
| **`CMG-000001`** | `00-CMG/` | `identifier_families` (11); `namespaces` (17); `kinds` (24) — the closed enumerations identity is drawn against |
| **`GOV-001` Part 10** | governance | the prohibition on a parallel identifier system |

**Nothing in this framework is added to that list.** The platform's identity role is confined to composition (§3).

---

## 2. THE FIVE IDENTITY PLANES

`AIF-L03` declares five orthogonal, **non-substitutable** planes. Non-substitutable is the operative word: no plane's value may stand in for another's, and no plane may be derived from another.

| Plane | Bears | Mutability | Platform attribute | Submission field |
|---|---|---|---|---|
| **P1** content | the multihash over the versioned Canonical Content Form — **verifies, never identifies** | recomputed per version | `UOM-A-18` | `CIOS-ID-04`, `ID-05` |
| **P2** durable | the minted-once, opaque, authority-namespaced identity | **immutable, never reused** | `UOM-A-01` | `CIOS-ID-01` (+ `ID-02`, `ID-03`) |
| **P3** order | the witnessed admission ordinal — authority-local, recorded at mint, **never recomputed, not globally monotonic** | immutable | `UOM-A-19` | `CIOS-ID-06` |
| **P4** logical | the version/lineage-bearing logical handle | advances by successor | `UOM-A-18` | `CIOS-ID-07` |
| **P5** runtime | the runtime-scoped handle, if any | scoped to a runtime | `UOM-A-18` | `CIOS-ID-08` |

### 2.1 The four substitution errors the planes prevent

Recorded because each is a plausible design mistake that the plane separation forecloses.

| Error | Why it fails | Enforcer |
|---|---|---|
| using the **content digest** as identity | two byte-identical artifacts would collapse to one entity; a reformat would change identity | `AIF-L05` — digest *verifies*, never identifies |
| using the **ordinal** as identity | the ordinal is authority-local and not globally unique across authorities | `AIF-L04` |
| using a **timestamp** for order | two admissions can share a timestamp, so no total order exists; and timestamps are recomputable, hence forgeable by reordering | `CIOS-L-15`; `CIOS-10` §2.4 |
| using the **name** as identity | names are mutable without limit (`UUP-09`) | `AIF-L03` P2 ⊥ P4; `CIOS-L-13` |

---

## 3. THE COMPOSITION RULE

| ID | Rule | Basis |
|---|---|---|
| `IDF-1` | The platform **composes** an identity record from fields produced by located authorities. It mints nothing, allocates nothing, and reserves nothing. | `CIOS-L-14`; `CIOS-01` I.5; `CIOS-08` §1 |
| `IDF-2` | Identity is minted **by the system at admission**. Manual assignment of any identifier is a **hard rejection**, not a warning. | `CIOS-L-12`; `REG-AUTO-001` |
| `IDF-3` | The platform SHALL NOT supply a default, placeholder, sentinel or derived substitute for an unresolved **minted** field. | `IDR-3`; `CIOS-L-07` |
| `IDF-4` | A record missing any field at its declared resolution point is **not a degraded record; it is not a record**. Non-admission. | `IDR-2`; `CIOS-INV-07` |
| `IDF-5` | Correction of any RECORDED-immutable field proceeds by **successor only**. | `UUP-08`; `AIF-L17` |
| `IDF-6` | Ordering authority is the **witnessed admission ordinal**, never a timestamp, never a name, never a content digest. | `CIOS-L-15`; `AIF-L04` |
| `IDF-7` | No mission-local identifier (`SS-*`, `UOM-A-*`, `UUP-*`, `REG-*`, `PG-*`, …) is a corpus identifier. **None may be presented to `REG-AUTO-001` or entered in `id-ledger.json`.** | `NS-3` |
| `IDF-8` | No second identifier system exists. Every platform identity draws from a located namespace or is mission-local and declared as such. | `GOV-001` Part 10; `CIOS-L-14` |

### 3.1 Composition, not minting — the boundary in one table

| The platform **does** | The platform **does NOT** |
|---|---|
| read minted fields from the `AIF` ledger and `id-ledger.json` | allocate an identifier |
| assert completeness at declared resolution points | assert correctness of a minted value |
| fail closed on any unresolved field | substitute, default or infer a missing minted field |
| reject manual assignment | adjudicate a disputed identity |
| record which located authority produced which field | become that authority |

---

## 4. IDENTITY ACROSS OBJECT KINDS

Every platform object kind, and where its identity comes from. This is the practical content of "identity governance".

| Object kind | Identity source | Space | Minted by | Mission-local? |
|---|---|---|---|---|
| Programme | `uccep.json` `programs[].id` | `PROGRAM-*` | `UCCEP-000000` owner | no |
| Mission / work package | registration record + `WP-<PROGRAMME-ID>` convention | `WP-*` | convention (`UCCEP-000006` P-5) — **no allocator** (`PGAP-05`) | no |
| Submission | 22-field record, `CIOS-ID-01…08` minted | located | `AIF` + `REG-AUTO-001` | no |
| Artifact | `artifacts.json[*].id` | `UCOS-*` | `REG-AUTO-001` | no |
| Page | `id-ledger.json` cursor | `UPN-*` | `REG-AUTO-001` | no |
| Capability | capability catalogue entry | `UCOS-CAPABILITY-*` | located (`intelligence/rie`; `PLATFORM-006`) | no |
| Concept | closure register | `UKDA-*` | `UAKOS` | no |
| Decision | decision store | `DEC-*`, `ADR-*` | `UCDA-000001`; `adr/` | no |
| Edge / relationship | `relationships.json` | `UEDGE-*` | `REG-AUTO-001` | no |
| Checkpoint | `CKPT-<UTC>-<HEAD>` | `CKPT-*` | `MCP-007` §03 convention | no |
| Engine / port / stage / partition / plane | `IMR-003A` declaration | `CIOS-E/P/S/PT/PL-*` | **programme-scoped declaration** — not corpus identity (`RC-04` §4) | yes (programme) |
| **Subsystem** | `IMR-0000` declaration | `SS-*` | **mission-local declaration** — `CIOS-SS-*` admission is `PG-01` | **yes** |

**Two kinds have no allocator: missions (convention only, `PGAP-05`) and subsystems (mission-local, `PG-01`).** Both are recorded; neither is given an allocator by this framework, because allocating one would be the parallel-identifier act `GOV-001` Part 10 prohibits.

---

## 5. WHAT THE PLATFORM'S IDENTITY SURFACE EXPOSES

| Surface | Consumed from | Access |
|---|---|---|
| minted durable identity, authority id, local key | `AIF` ledger (`RC-12`) | **R** |
| identifier uniqueness check | `id-ledger.json` (`RC-02`) | **R** |
| registered-artifact population | `artifacts.json` (`RC-03`) | **R** — the 27 FROZEN entries never touched |
| kinds, namespaces, families | `CMG-REGISTRY.json` (`RC-01`) | **R** |
| canonical home and owner | `UAKOS` home register (`RC-05`) | **R** |
| family → owner map | `IMG-001` `02` (`RC-10`) | **R** |

| Property | Value |
|---|---|
| Identifiers minted by the platform | **0** |
| Identifiers allocated or reserved | **0** |
| `id-ledger.json` entries created | **0** |
| Corpus identifiers consumed | **0** |
| Parallel identifier systems created | **0** |
| Registers written | **0** |
| Public ports on `SS-02` | **0** — `P-13`/`P-14` internal; programmes bind `AIF`/`REG-AUTO-001` **directly** (`IFL-04`) |

---

## 6. INHERITED DEFECTS BOUNDING THIS FRAMEWORK

Recorded as bounds on claims, not as this framework's defects. Each is owned elsewhere.

| Finding / gate | Bound placed on identity governance |
|---|---|
| `UCCEP-F-006` / `CIOS-G-05` **OPEN** | Schema validation degrades silently to structural-only checks, so **identity-record validation inherits that degradation**. Completeness assertions are sound only to the degree the located validator is (`CIOS-GAP-05`) |
| `UCCEP-F-007` | Working-tree registration drift exists at establishment. The platform adds none and clears none (`CIOS-GAP-09`) |
| `PGAP-05` | Missions have no machine-readable register and no allocator; mission identity is convention-borne |
| `PG-01` | Subsystem identity is mission-local until a `CIOS-SS-*` family is admitted to `cios-bindings.json` by its owner |
| `GG-4` | The registration anchor lacks off-machine existence; identity claims are witnessed only in the working tree |

---

## 7. WHAT THIS FRAMEWORK DOES NOT DO

| Not done | Located owner |
|---|---|
| Mint, allocate, reserve or retire an identifier | `AIF`; `REG-AUTO-001`; `00-BOOK/tools/` |
| Define an identifier format, encoding, digest algorithm or ordinal scheme | `AIF-L02`, `L04`, `L05` |
| Create or write `id-ledger.json`, `artifacts.json` or any register | `REG-AUTO-001`; `CIOS-INV-12` |
| Add a namespace, kind or identifier family to `CMG-REGISTRY.json` | `CMG-000001`; `CIOS-G-02` OPEN |
| Adjudicate a disputed or drifted identity | `CEP-009` change route; `UCDA` disposition |
| Re-state `CIOS-08`'s 22 fields or its resolution points | `CIOS-08` — bound by pointer (`03` §5) |
| Discharge `CIOS-G-05` or clear registration drift | owner of `ukb validate`; repository operator |

---

## AUTHORITY BOUNDARY (MANDATORY)

This framework declares how identity is **composed** and which located authority produces each field. It mints nothing, allocates nothing, reserves nothing, writes no register, adds no namespace and adjudicates no identity. No mission-local identifier is a corpus identifier, and none may be presented to `REG-AUTO-001`. Every authority named is located in an instrument existing independently at `b26c5bb`; `CIOS-08` governs the submission record where any reading differs. Where this framework and a located canonical instrument disagree, **the located instrument governs and this framework SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `IMR-0000/05` · PROVISIONAL · ADDITIVE · DESIGN-ONLY · AUTHORITY-NEUTRAL**
