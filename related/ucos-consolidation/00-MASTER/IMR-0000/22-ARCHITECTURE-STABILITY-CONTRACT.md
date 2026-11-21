# IMR-0000/22 — ARCHITECTURE STABILITY CONTRACT v1.0

| Field | Value |
|---|---|
| MISSION | `IMR-0000` — CIOS Platform Foundation |
| ARTIFACT | `22` — Architecture Stability Contract (**deliverable 28**) · directive capability 26 |
| ARTIFACT KIND | Contract (`CMG-K-05`) — **declaration-scoped** |
| SCOPE | The platform architecture declared by `IMR-0000` artifacts `01 … 21`, and nothing else |
| FORM | Modelled on `IMR-003A-R1/09` — CIOS Architecture & Interface Stability Contract v1.0 |
| **WHAT THIS IS NOT** | **NOT a `CEP-007` freeze. NOT a seal. NOT immutability.** `CEP-007` freeze is **unavailable** at `b26c5bb` and an attempt would be **void** (`CEP-007` II.4, IV.4; `GD-10`; `CIOS-GAP-13`). |
| NUMERIC CONTRACT | **10 clauses** `ASC-01 … ASC-10` |
| AUTHORITY OF ITS OWN | **NONE.** A stability contract is a change-routing declaration, not a power. |
| CONFLICT RULE | Located instrument governs; then `IMR-003A`; then this contract. |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |
| VERSION | **v1.0** |

---

## 1. WHY THIS IS A CONTRACT AND NOT A FREEZE

The instruction and the directive both require an **Architecture Freeze**. It cannot be delivered, and the reason is located rather than discretionary.

| Freeze limb | `CEP-007` requirement | State at `b26c5bb` |
|---|---|---|
| ratification | the artifact's standing must exceed PROVISIONAL | **FAILS** — Tier `T1` VACANT (`VAC-01`); no authority competent to ratify (`CEP-006`) |
| active certification | certification must be active, not provisional | **FAILS** — ceiling `CERTIFIED-PROVISIONAL`; 31 of 43 artifacts PROVISIONAL |
| traceability closure | `CEP-001` XVIII rooted-and-closed | **FAILS** — incomplete for all 1198 registered artifacts (`UCCEP-F-002`) |

**Three limbs fail. `CEP-007` IV.4 / II.4 make an attempted freeze void, and `GD-10` places the Program in HALTED if a frozen surface is mutated.** A void freeze is strictly worse than no freeze: it would create a false immutability claim over an architecture that remains changeable, and it would put the corpus into a halted state on the first subsequent edit.

`IMR-003A-R1` faced the identical requirement and resolved it the identical way (`IMR-003A-R1/10` §5.2). This contract follows that precedent rather than inventing a second treatment of the same question.

**What stability means here instead:** the architecture may change **only through a declared route**, never by in-place edit. That is weaker than a seal and stronger than nothing, and it is stated as exactly what it is.

---

## 2. THE CONTRACT — `ASC-01 … ASC-10`

| ID | Clause | Basis |
|---|---|---|
| **`ASC-01`** | **Scope.** This contract covers `IMR-0000/01 … 21`. It covers nothing in `IMR-003A`, `IMR-003A-R1` or any located instrument — those are governed by their own owners and are consumed read-only. | `MC-01`; `ASC-10` |
| **`ASC-02`** | **The public surface is fixed at 20 entries** — 8 platform ports (`IF-01…IF-08`) and 12 located interfaces (`IFL-01…IFL-12`). A downstream mission may rely on these. | `19`; `CIOS-05` §2 |
| **`ASC-03`** | **Internal surfaces carry no guarantee.** The 40 internal ports, and every intermediate declaration in `01…21`, may be refined without notice. A programme binding an internal surface has bound something this contract does not cover. | `CIOS-05` §2; `IC-2` |
| **`ASC-04`** | **Change routes through `CEP-009` III.1** with an impact assessment. **No clause, subsystem, attribute, rule, registry specification, axis or catalogue entry may be edited in place.** | `CEP-009` III.1; `PR-7`; `UUP-08` |
| **`ASC-05`** | **Cardinalities that may not change by data change.** 17 subsystems · 20 object attributes · 9 uniqueness clauses · 11 registry specifications · 4 lifecycle axes · 8 platform ports · 12 located interfaces. Each is a closure test of its declaring artifact; altering one is a `CEP-009` III.1 change to that artifact. | `NS-4` pattern; `UOM-R-9`; `NF-6` |
| **`ASC-06`** | **Cardinalities this contract may never touch at all.** 24 engines · 48 ports · 24 stages · 22 identity fields · 4 planes · 4 partitions · 24 laws · 12 invariants · 4 queues · 8 key elements · 2 override authorities. These are `CIOS-01`'s and `IMR-003A`'s; changing any requires a `CEP-009` III.1 change to **`CIOS-01` itself** (`PG-02`), which `MC-01` forbids this mission from initiating. | `CIOS-01` Art X.1; `NS-4` |
| **`ASC-07`** | **Additive extension only.** A subsystem, attribute, rule, specification or catalogue entry may be **added** by the declared route; none may be **removed or narrowed**, because a downstream mission may already have bound it. | `CIOS-01` I.3; `AIF-L17` |
| **`ASC-08`** | **No clause acquires mechanism ownership.** An amendment that moves a located mechanism into the platform is **void**. | `CIOS-01` VIII.4; `CIOS-L-09`; `CEP-001` LAW-4 |
| **`ASC-09`** | **Correction is by successor.** Where a clause is wrong, a successor states the correction; the erroneous clause is not silently rewritten. Corrections already recorded under this discipline: `PF-01` (attribute count 19 → 20) and the `00A` §2.1 tally (12 → 14). | `AIF-L17`; `UUP-08` |
| **`ASC-10`** | **Subordination.** Where this contract and a located canonical instrument conflict, **the located instrument governs and this contract SHALL be corrected**. Where it and `IMR-003A` conflict, **`IMR-003A` governs**. | `CEP-001` LAW-1, LAW-4; `MC-01` |

---

## 3. WHAT A DOWNSTREAM MISSION MAY RELY ON

The operative purpose of the contract: a statement precise enough to build against.

| May rely on | May **not** rely on |
|---|---|
| the 8 platform ports, their direction, payload class and fail-closed mode | any of the 40 internal ports |
| the 12 located interface bindings (`IFL-01…IFL-12`) | any capability routed *through* the platform that `19` says to bind directly |
| the 17 subsystems' identities, canonical names and engine allocations | a subsystem holding a mechanism, gate, registry or concern — none does, and none will |
| the 20 object attributes and their located producing authorities | a value for any attribute; the platform produces none |
| the 4 lifecycle axes and which located owner governs each | any new state, transition or state machine — there are none |
| the 11 registry specifications as **read contracts** | `REG-05` or `REG-07` existing as registers — they do not |
| `RR-1…RR-6` as **declared types** | any edge instance — none is written |
| the uniqueness clauses and their located enforcers | `UUP-05`, `UUP-06` or active `UUP-07` holding corpus-wide — they do not |
| this mission's PROVISIONAL standing | any ratification, active certification, freeze or seal |

---

## 4. STABILITY PROPERTIES

| Property | Value |
|---|---|
| Contract clauses | **10** |
| Contract version | **v1.0** |
| Scope | `IMR-0000/01 … 21` |
| Artifacts outside scope | `IMR-003A/*`, `IMR-003A-R1/*`, every located instrument |
| Public entries guaranteed | **20** |
| Internal surfaces guaranteed | **0** |
| Change route | `CEP-009` III.1 with impact assessment — **the only route** |
| In-place edits permitted | **0** |
| Removals or narrowings permitted | **0** (`ASC-07`) |
| `CEP-007` freeze declared, implied or recorded | **0** |
| Seals claimed | **0** |
| Immutability claimed | **0** — contracts are change-routed, not sealed |
| Ratification claimed | **0** |
| Corrections recorded under `ASC-09` | **2** |

---

## 5. THE THREE DIVERGENCES THIS CONTRACT PRESERVES

Recorded here because a stability contract that quietly dropped them would be misleading about what it stabilises.

| # | Instruction / directive requirement | What is delivered | Why |
|---|---|---|---|
| 1 | "Architecture Freeze" | **declaration-scoped stability contract** + a freeze **declaration** in `25` | `CEP-007` ineligible on three limbs; an attempt would be **void** |
| 2 | "immutable" architecture | **change-routed** architecture | true immutability requires a seal, which requires freeze, which is unavailable |
| 3 | "validation passes / certification passes" as freeze preconditions | **self-checks pass** (`PCK-01…12`); certification **ceiling-bound** | `CEP-004` validation and active `CEP-005` certification of this mission are unavailable while `VAC-01` is open |

Each divergence is a case where the literal requirement would produce a **void** act under located law. All three are already recorded as `D-3`, `D-4` and `D-6`/`AC-14` in `00` §6, and none is introduced by this contract.

---

## AUTHORITY BOUNDARY (MANDATORY)

This contract declares a change route over an architecture. **It is not a `CEP-007` freeze, declares no freeze, claims no seal and asserts no immutability.** It owns no mechanism, no registry, no gate, no identifier space and no concern; it covers nothing outside `IMR-0000/01 … 21`; it may not be amended to acquire mechanism ownership. Its own standing is PROVISIONAL, capped by Tier `T1` vacancy. Where this contract and a located canonical instrument disagree, **the located instrument governs and this contract SHALL be corrected**; where it and `IMR-003A` disagree, `IMR-003A` governs. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `IMR-0000/22` · v1.0 · PROVISIONAL · ADDITIVE · DESIGN-ONLY · AUTHORITY-NEUTRAL**
