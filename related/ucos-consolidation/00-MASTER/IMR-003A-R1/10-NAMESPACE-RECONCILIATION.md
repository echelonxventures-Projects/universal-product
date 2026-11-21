# IMR-003A-R1 · OUTPUT 9 — MISSION NAMESPACE SPECIFICATION & RECONCILIATION

| Field | Value |
|---|---|
| MISSION | `IMR-003A-R1` |
| ARTIFACT | Required output 9 — Mission Namespace Specification (delivered as a reconciliation, per `R1.5`) |
| SUBJECT | The relationship between the recovery instruction's vocabulary (`UAMR`, `UAES`, "Mission Object") and the namespace `IMR-003A` OUTPUT 0.4 actually allocated (`CIOS`) |
| DISCLOSURE | PROVISIONAL; Tier T1 VACANT |
| VERDICT | **NO NEW NAMESPACE ALLOCATED.** `UAES` and `UAMR` are recorded as **external vocabulary aliases**, not as repository tokens. |

---

## 1. THE DIVERGENCE, MEASURED

The recovery instruction is headed `UAMR (Universal Autonomous Mission Registry)` and requires `UAES Architecture Freeze v1.0`. Neither token exists in the repository.

| Token | Occurrences at working-tree state over `b26c5bb` | Method |
|---|---|---|
| `UAES` | **0** | `grep -ril "UAES" --include=*.md --include=*.json --include=*.py` (`.git` excluded) |
| `UAMR` | **0** | `grep -ril "UAMR" --include=*.md --include=*.json` (`.git` excluded) |
| `CIOS` | **2 files, both inside `00-MASTER/IMR-003A/`** | same method |
| "Continuous Implementation Operating System" | same 2 files | same method |

`IMR-003A` OUTPUT 0.4 allocated exactly one subject token — **`CIOS`** — and verified it at zero prior occurrence. That allocation is COMPLETE and audited (`04-GAP-ANALYSIS-MATRIX.md` row 6).

---

## 2. WHY NO `UAES` NAMESPACE IS ALLOCATED

Allocating `UAES` as a second subject token for the same subject matter would breach four located and recovered instruments simultaneously:

| Instrument | Clause | Breach |
|---|---|---|
| `CEP-001` | LAW-4 Single Canonicity | two canonical names for one subject ⇒ two canonical homes |
| `CIOS-L-09` | Zero Duplication | *"no second canonical home, second owner, second identifier … for anything that already has one"* |
| `GOV-001` | Part 10 | prohibition on a parallel identifier system |
| `IMR-003A` `AC-3` | *"No parallel identifier system. All identity is minted by the located identity authority."* | direct violation |

The recovery instruction additionally and expressly commands: *"DO NOT restart IMR-003A"*, *"Maintain Knowledge Once"*, *"Maintain zero duplication"*. Allocating `UAES` **is** a restart under a new name — the precise act prohibited.

**Determination: `UAES` is NOT allocated. `UAMR` is NOT allocated.** They are recorded here as instruction-level vocabulary, resolved onto the located token.

---

## 3. VOCABULARY RESOLUTION TABLE

Binding for every artifact of this mission and every downstream mission. The left column may appear in instructions and conversation; only the right column may appear as a repository identifier.

| Instruction vocabulary | Resolves to (repository truth) | Located home |
|---|---|---|
| `UAMR` — Universal Autonomous Mission Registry | the **mission registration convention** itself: programme-owned work-package register under `00-MASTER/<PROGRAMME-ID>/` per `UCCEP-000006` §1 **P-5**. Not an artifact; a convention already in force. | `UCCEP-000006` P-5 |
| `UAES` — (autonomous execution system) | **`CIOS`** — Continuous Implementation Operating System | `00-MASTER/IMR-003A/` |
| "UAES Architecture Freeze v1.0" | **CIOS Architecture & Interface Stability Contract v1.0** — declaration-scoped, **not** a `CEP-007` freeze (`R1.4`) | `09-ARCHITECTURE-INTERFACE-FREEZE-REPORT.md` |
| "Canonical Mission Object" | **CIOS Canonical Submission Object** — the 22-field identity record `CIOS-ID-01…22` | `IMR-003A/08-CIOS-IDENTITY-MODEL.md` |
| "Mission Namespace" | the `CIOS` subject token + 13 internal identifier families | `IMR-003A` OUTPUT 0.4 + this artifact |
| "Mission Lifecycle" | the 24 admission stages `CIOS-S-01…24` | `IMR-003A/07-CIOS-LIFECYCLE-MODEL.md` |
| "State Machine" | two orthogonal machines: **mutability partitions** `CIOS-PT-*` (CIOS-owned) and **item states** (10, `IEC-001` `06`, located) | `CIOS-01` Art V; `IEC-001` `06` |
| "Engine Contracts" | `CIOS-E-01…24` × ports `CIOS-P-*` | `IMR-003A/03`, `04`, `05` |
| "Registry Contracts" | binding declarations to located registries; **CIOS owns no registry** (`CIOS-INV-12`) | `IMR-003A/13`; `07-REGISTRY-MATRIX.md` |
| "Mission" (as a work unit) | **submission** — the unit admitted through `CIOS-S-01…24`. Distinguished from "mission" as a programme (`IMR-003A`), to prevent conflation. | `CIOS-01` Art V |

**Terminology hazard recorded.** The instruction uses "mission" for both a *programme* (`IMR-003A`) and a *unit of admitted work*. CIOS artifacts use **submission** for the latter throughout. Any downstream artifact using "mission object" must be read as "submission object".

---

## 4. MISSION NAMESPACE SPECIFICATION (RECOVERED + RELIED UPON)

Reproduced **by reference**, not restated as new law. Source of truth: `IMR-003A` OUTPUT 0.4.

### 4.1 Mission family

| Field | Value |
|---|---|
| Family | `IMR` / `WP-IMR-*` |
| Established by | `IMR-001` (`00-MASTER/IMR-001/`) |
| Members | `WP-IMR-001` (M-1A) · `WP-IMR-003A` · `WP-IMR-003A-R1` |
| Sequence discontinuity | `IMR-002`, `IMR-003` absent — recorded as provenance, **not** a gap (`IMR-003A` OUTPUT 0.1) |
| Recovery suffix form | `-R<n>`; precedent `UAKOS-PHASE-001A-R1`, `UAKOS-PHASE-003A-R2` |
| New family allocated by this mission | **NONE** |

### 4.2 Subject token

| Field | Value |
|---|---|
| Token | **`CIOS`** |
| Scope | programme-scoped subject token under family `IMR` |
| Home | `00-MASTER/IMR-003A/` (registration-excluded per `00-BOOK/tools/config.py :: EXCLUDE_DIR_PREFIXES → "00-MASTER/"`) |
| Corpus namespace requested from `CMG-REGISTRY.json` | **NONE** |
| Corpus identifier family requested from `REG-AUTO-001` | **NONE** |
| Corpus identity consumed | **NONE** |
| Collision | **ZERO** (re-verified this mission) |

### 4.3 Internal identifier families — allocation and population state

Thirteen families declared in OUTPUT 0.4. This mission **populates** them; it allocates none.

| Family | Meaning | Declared | Populated @ recovery | Populated post-closure | Cardinality authority |
|---|---|---|---|---|---|
| `CIOS-L-*` | law | ✓ | **24** | 24 (unchanged) | `CIOS-01` Art II |
| `CIOS-INV-*` | invariant | ✓ | **12** | 12 (unchanged) | `CIOS-01` Art III |
| `CIOS-PL-*` | plane | ✓ | **4** (`A`–`D`) | 4 (unchanged) | `CIOS-01` Art IV |
| `CIOS-PT-*` | partition | ✓ | **4** (`00`,`01`,`02`,`03`) | 4 (unchanged) | `CIOS-01` Art V |
| `CIOS-E-*` | engine | ✓ | **0** | **24** | `CIOS-01` Art X.1 |
| `CIOS-P-*` | port | ✓ | **0** | **48** (2 per engine) | `IMR-003A/05` |
| `CIOS-S-*` | lifecycle stage | ✓ | **0** | **24** | `CIOS-01` Art X.1 |
| `CIOS-Q-*` | queue | ✓ | **0** | **4** | `CIOS-01` Art VII.3 |
| `CIOS-ID-*` | identity field | ✓ | **0** | **22** | `CIOS-01` Art X.1 |
| `CIOS-K-*` | priority key element | ✓ | **0** | **8** | `IMR-003A/10` (closes `U-2`) |
| `CIOS-OR-*` | override authority | ✓ | **0** | **2** | `CIOS-L-21` (closes `U-3`) |
| `CIOS-G-*` | undischarged gate | ✓ | **2** (`G-01`, `G-02`) | **7** (`G-01…G-07`) | OUTPUT 0.2 (closes `U-1`) |
| `CIOS-GAP-*` | gap | ✓ | **0** | **14** | `IMR-003A/19` |

Every count in the "post-closure" column is fixed by a recovered authority, not chosen by this mission. Where `CIOS-01` Art X.1 states a number (24 engines, 24 stages, 22 identity fields), that number is a **hard contract**.

### 4.4 Namespace invariants (binding on all downstream missions)

| ID | Invariant |
|---|---|
| `NS-1` | No downstream mission may allocate a second subject token for CIOS's subject matter. `UAES` is not a token. |
| `NS-2` | Adding a member to any `CIOS-*` family is a **data change** to `cios-bindings.json` (`CIOS-L-23`), never an amendment of `CIOS-01`. |
| `NS-3` | No `CIOS-*` identifier is a corpus identifier. None may be presented to `REG-AUTO-001` or entered in the `id-ledger`. |
| `NS-4` | Cardinalities fixed by `CIOS-01` Art X.1 (24 / 24 / 22) may not be altered by data change; altering them requires a `CEP-009` III.1 change to `CIOS-01`. |
| `NS-5` | `CIOS-*` identifiers are never reused after retirement (`AIF-L17` forward-only compensation, applied by analogy within the programme zone). |

---

## 5. DISCLOSED DIVERGENCE FROM THE INSTRUCTION

Recorded plainly, as required by `RAC-2` and `RAC-6`:

1. **The instruction's `UAES` token is not created.** Deliverables carry the `CIOS` token. Reason: `CEP-001` LAW-4, `CIOS-L-09`, `GOV-001` Part 10, `IMR-003A` `AC-3`, and the instruction's own Knowledge-Once and zero-duplication commands.
2. **"Freeze" is delivered as a declaration-scoped stability contract**, not a `CEP-007` freeze. Reason: `CEP-007` IV.1 / V.1 / V.5 ineligibility while `VAC-01` is open; IV.4 / II.4 would make an attempt **void**. Detail in `R1.4` and `09-ARCHITECTURE-INTERFACE-FREEZE-REPORT.md`.
3. **"Immutable" is delivered as change-routed.** Contracts may change only via `CEP-009` III.1, never by in-place edit. True immutability requires a seal, which requires freeze, which is unavailable.

Each divergence is a case where the literal instruction would produce a **void or duplicative** act under located law. Recorded as `CIOS-GAP-13` (freeze) and resolved here (namespace).

---

## AUTHORITY BOUNDARY (MANDATORY)

This artifact **reconciles vocabulary**. It allocates nothing, mints nothing, confers no authority, discharges no gate, and authorizes no execution. Where it and a located canonical instrument disagree, **the located instrument governs and this artifact SHALL be corrected**.

**END OF ARTIFACT — `IMR-003A-R1` OUTPUT 9 · PROVISIONAL · ADDITIVE · AUTHORITY-NEUTRAL**
