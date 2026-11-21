# IMR-0000/06 — CIOS NAMESPACE FRAMEWORK

| Field | Value |
|---|---|
| MISSION | `IMR-0000` — CIOS Platform Foundation |
| ARTIFACT | `06` — CIOS Namespace Framework (**deliverable 6**) · directive capability 8 (namespace governance) |
| ARTIFACT KIND | Framework (`CMG-K-05`) — binding declaration + namespace discipline |
| CENTRAL CLAIM | **`IMR-0000` allocates no namespace, no subject token and no identifier family in any located register.** The framework declares the discipline that makes that refusal correct rather than merely cautious. |
| AUTHORITY OF ITS OWN | **NONE.** `CIOS-INV-12` — CIOS holds no identifier space of its own. |
| CONFLICT RULE | Located instrument governs (`CMG-000001`, then `GOV-001` Part 10, then `REG-AUTO-001`); then `IMR-003A-R1/10`; then this artifact. |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. THE THREE NAMESPACE TIERS

Namespace governance in this corpus is not one thing. Conflating the three tiers is what produces parallel identifier systems, so the framework separates them before anything else.

| Tier | What it is | Owner | Present in `id-ledger.json` / `artifacts.json` / `CMG-REGISTRY.json`? | Example |
|---|---|---|---|---|
| **T-C · Corpus namespace** | an identifier space from which **corpus identity** is minted | `CMG-000001` `namespaces` (17) + `REG-AUTO-001` | **YES** | `UCOS-*`, `UPN-*`, `UEDGE-*`, `UKDA-*` |
| **T-P · Programme-scoped declaration space** | identifier families internal to a programme's own declaration, in a **registration-excluded** zone | the programme that declared them | **NO** | `CIOS-E-*`, `CIOS-P-*`, `CIOS-S-*`, `CIOS-ID-*` (13 families, `IMR-003A` OUTPUT 0.4) |
| **T-M · Mission-local declaration space** | slots in a single mission's artifacts | the mission | **NO** | `SS-*`, `UOM-A-*`, `UUP-*`, `REG-*`, `PG-*`, and `IMR-003A-R1`'s `NS-*`, `RC-*`, `V-*` |

**The basis for T-P and T-M being outside corpus identity is mechanical, not asserted:** `00-BOOK/tools/config.py :: EXCLUDE_DIR_PREFIXES → "00-MASTER/"`. Every programme and mission home under `00-MASTER/` is registration-excluded, so nothing declared there consumes corpus identity. Machine-verified for CIOS by `IMR-003A-R1` `V-65`, `V-75`.

| ID | Rule | Basis |
|---|---|---|
| `NF-1` | A T-P or T-M identifier is a **slot in a declaration**, never an allocated identity. It may **never** be presented to `REG-AUTO-001` or entered in `id-ledger.json`. | `NS-3` |
| `NF-2` | Allocating a T-C namespace requires admission to `CMG-REGISTRY.json` by the Registration/Governance Authority. No programme may self-allocate. | `CMG-000001` LXXVI.2; `CEP-002` 7.2 / 14.2; `CEP-009` I.5 |
| `NF-3` | A T-M family is created by declaring it in a mission artifact and stating its cardinality. It requires no admission, because it claims no identity. | precedent: `IMR-003A-R1` `NS-*`, `RC-*`, `V-*`, `U-*`, `CP-*`, `RAC-*` |
| `NF-4` | **No second subject token may be allocated for a subject matter that already has one.** | `NS-1`; `CEP-001` LAW-4; `CIOS-L-09`; `GOV-001` Part 10 |

---

## 2. THE CIOS NAMESPACE, AS ALLOCATED AND POPULATED

Reproduced **by reference**. Source of truth: `IMR-003A` OUTPUT 0.4 + `IMR-003A-R1/10` §4. Restating it as new law would breach `CIOS-L-08`.

| Element | Value |
|---|---|
| Family | `IMR` / `WP-IMR-*`, established by `IMR-001` |
| Subject token | **`CIOS`** — one token, programme-scoped, zero collisions (re-verified) |
| Token home | `00-MASTER/IMR-003A/` |
| Corpus namespace requested | **NONE** |
| Corpus identifier family requested | **NONE** |
| Internal families | **13**, populated: `L`(24) · `INV`(12) · `PL`(4) · `PT`(4) · `E`(24) · `P`(48) · `S`(24) · `Q`(4) · `ID`(22) · `K`(8) · `OR`(2) · `G`(7) · `GAP`(14) |
| Cardinalities fixed by `CIOS-01` Art X.1 | **24 engines / 24 stages / 22 identity fields** — not alterable by data change (`NS-4`) |

### 2.1 The five located namespace invariants, restated by pointer only

| ID | Invariant (owner: `IMR-003A-R1/10` §4.4) | `IMR-0000` conformance |
|---|---|---|
| `NS-1` | No second subject token for CIOS's subject matter | **CONFORMS** — token `CIOS` reused; `UAES`, `UAMR`, `EMP` all refused (`01` §5.1) |
| `NS-2` | Adding a member to a `CIOS-*` family is a data change, never an amendment | **CONFORMS by non-participation** — zero members added (`00` §3.3) |
| `NS-3` | No `CIOS-*` identifier is a corpus identifier | **CONFORMS** — and extended to every `IMR-0000` family (`NF-1`, `IDF-7`) |
| `NS-4` | Art X.1 cardinalities not alterable by data change | **CONFORMS by non-participation** — 24/24/22 untouched |
| `NS-5` | `CIOS-*` identifiers are never reused after retirement | **CONFORMS** — and adopted for `IMR-0000` families (`NF-5` below) |

| ID | Rule | Basis |
|---|---|---|
| `NF-5` | An `IMR-0000` mission-local identifier is never reused after retirement. A retired slot stays retired; successors take new ordinals. | `NS-5`; `AIF-L17` by analogy within the programme zone |
| `NF-6` | An `IMR-0000` family's cardinality is declared in `00` §3.2 and is this mission's own closure test. Changing a declared cardinality is a `CEP-009` III.1 change to the declaring artifact, not a data change. | `NS-4` pattern; `CIOS-01` Art X.1 pattern |

---

## 3. WHY NO NEW TOKEN IS ALLOCATED — THE THIRD REFUSAL

Three tokens have now been proposed for this subject matter and all three are refused. Recording the pattern matters more than any single refusal, because the request recurs.

| Proposed token | Proposed by | Refused by | Reason |
|---|---|---|---|
| `UAES` | `IMR-003A` recovery instruction | `IMR-003A-R1/10` §2 | second canonical name for one subject ⇒ second canonical home |
| `UAMR` | same instruction (as a registry name) | `IMR-003A-R1/10` §3 | resolves to an existing **convention** (`UCCEP-000006` P-5), not a new artifact |
| `EMP` / "Engineering Management Platform" | Context Assimilation Directive, capability 5 | `01` §5.1; this artifact | same act under a third name |

**The invariant behind all three refusals.** A token allocation is not a naming convenience; it is the creation of an identifier space, which under `UUP-01`+`UUP-03` implies a second identity and a second registration for a subject that has one. `CEP-001` LAW-4, `CIOS-L-09`, `GOV-001` Part 10 and `IMR-003A` `AC-3` each independently prohibit it, and the instruction's own commands — *Knowledge Once*, *zero duplication*, *never rename CIOS* — prohibit it a fifth time.

**What is done instead, in every case:** the proposed token is recorded in a **vocabulary resolution table** (`01` §5.2) mapping it onto the located token. The vocabulary survives; the namespace does not.

---

## 4. `IMR-0000`'s OWN NAMESPACE POSTURE

| Question | Determination | Basis |
|---|---|---|
| Subject token allocated | **NONE** | `NF-4`, `NS-1` |
| Corpus namespace requested from `CMG-REGISTRY.json` | **NONE** | `NF-2`; `CIOS-G-02` OPEN |
| Corpus identifier family requested from `REG-AUTO-001` | **NONE** | `NF-1` |
| Corpus identity consumed | **NONE** | `00-BOOK/tools/config.py` exclusion |
| `CIOS-*` family members added | **0** | `00` §3.3 |
| `CIOS-*` families created | **0** — a 14th family (`CIOS-SS-*`) is **proposed** for the located owner of `cios-bindings.json`, gated at `PG-01`, **not created** | `MC-01`; `NS-2` |
| Mission-local families declared | **18** | `00` §3.2 |
| Concern claimed | **NONE** | `CIOS-INV-12`; `CIOS-G-02` |
| Collision with any existing token or family | **ZERO** | §4.1 |

### 4.1 Collision check

| Family declared by `IMR-0000` | Collides with a located family? | Note |
|---|---|---|
| `SS-*` | no located `SS-*` family exists | subsystems |
| `UOM-A-*`, `UOM-R-*` | none | object model |
| `UUP-*` | none | uniqueness clauses |
| `RF-*`, `REG-*` | none — note `IMR-003A-R1` uses `RC-*` for registry **contracts**; `REG-*` here denotes registry **specifications**, and each `REG-*` names the `RC-*` it binds | registry |
| `LX-*`, `LR-*` | none | lifecycle |
| `IF-*`, `IFL-*` | none — `CIOS-P-*` remains the only port family | interfaces |
| `ASC-*`, `TM-*`, `PCK-*`, `PG-*`, `PF-*`, `PGAP-*` | none — deliberately prefixed to avoid `CIOS-G-*`, `CIOS-GAP-*`, `CK-*`, `V-*`, `VR-*`, `GR-*`, `PR-*` | mission records |
| `MC-*`, `AC-*` | `IMR-003A` used `AC-1…AC-12` in its **own** registration record; `IMR-0000`'s `AC-1…AC-14` are mission-local to `IMR-0000` and are never cited without their mission scope | mission constraints and criteria |

> **One near-collision recorded rather than left latent.** `AC-*` is used by both `IMR-003A` and `IMR-0000` for mission-local acceptance criteria. Because both are T-M spaces in registration-excluded homes, no identity collision arises — but a **citation** ambiguity does. Rule: every `AC-*` citation in this mission is written as `IMR-0000` `AC-n`, and `IMR-003A`'s as `IMR-003A` `AC-n`. Recorded as `PF-02` in `23`.

---

## 5. NAMESPACE GOVERNANCE FOR FUTURE PLATFORM MISSIONS

The operative output of this framework: what a future mission may and may not do.

| Act | Permitted? | Route |
|---|---|---|
| Declare a mission-local family in its own artifacts | **YES** | `NF-3` — declare the family and its cardinality; no admission needed |
| Add a member to an existing `CIOS-*` family | **YES**, as a data change | `NS-2` — data change to `cios-bindings.json` by its owner; **never** by editing `CIOS-01` |
| Create a new `CIOS-*` family | **CONDITIONAL** | data change to `cios-bindings.json` by its located owner; `PG-01` is the open instance of this for `CIOS-SS-*` |
| Change a cardinality fixed by `CIOS-01` Art X.1 | **NO**, not by data change | `CEP-009` III.1 change to `CIOS-01` — `PG-02` |
| Allocate a corpus namespace | **CONDITIONAL** | `CMG-000001` LXXVI.2 admission; never self-allocated |
| Allocate a second subject token for a subject that has one | **NEVER** | `NF-4`; four independent prohibitions |
| Present a T-P or T-M identifier to `REG-AUTO-001` | **NEVER** | `NF-1`; `NS-3` |
| Reuse a retired identifier | **NEVER** | `NF-5`; `NS-5` |
| Rename `CIOS` | **NEVER** | `MC-02`; `NS-1` |
| Introduce a name that implies a second platform | **NEVER** | `MC-07`; resolved by vocabulary table instead (`01` §5.2) |

---

## 6. WHAT THIS FRAMEWORK DOES NOT DO

| Not done | Located owner |
|---|---|
| Allocate, reserve or retire any namespace, token or family in a located register | `CMG-000001`; `REG-AUTO-001` |
| Add a `CMG-REGISTRY.json` namespace, kind, family or concern | `CMG-000001`; `CIOS-G-02` OPEN |
| Write `cios-bindings.json` or create a `CIOS-SS-*` family | inside `IMR-003A`; `MC-01`; `PG-01` |
| Restate `IMR-003A` OUTPUT 0.4 or `IMR-003A-R1/10` | bound by pointer; `CIOS-L-08` |
| Alter any `CIOS-01` Art X.1 cardinality | `NS-4`; `PG-02` |
| Adjudicate a namespace dispute | `CEP-009` change route; `CMG-000001` |

---

## AUTHORITY BOUNDARY (MANDATORY)

This framework declares namespace tiers and discipline. **It allocates nothing.** No subject token, corpus namespace, identifier family or concern is created, requested or reserved; no `CIOS-*` family member is added; no located cardinality is altered. Every mission-local family it declares is a set of declaration slots in a registration-excluded home and may never be presented to `REG-AUTO-001`. Every authority named is located in an instrument existing independently at `b26c5bb`. Where this framework and a located canonical instrument disagree, **the located instrument governs and this framework SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `IMR-0000/06` · PROVISIONAL · ADDITIVE · DESIGN-ONLY · AUTHORITY-NEUTRAL**
