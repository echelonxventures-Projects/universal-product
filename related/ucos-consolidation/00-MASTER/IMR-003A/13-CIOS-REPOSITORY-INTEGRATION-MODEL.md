# CIOS-13 — CONTINUOUS IMPLEMENTATION OPERATING SYSTEM · REPOSITORY INTEGRATION MODEL

| Field | Value |
|---|---|
| MISSION | `IMR-003A` — CIOS Constitution & Architecture |
| ARTIFACT | `CIOS-13` — Repository Integration Model (mission Output 13) · supplies the **Registry Contracts** required by the recovery instruction |
| DELIVERED BY | `IMR-003A-R1` gap closure (Phase 4). **Additive**: no recovered artifact mutated. |
| DISCHARGES | `AC-9` (write confinement, proven as an artifact) · registry binding surface · `CIOS-INV-12` |
| CENTRAL CLAIM | **CIOS owns no registry.** It binds located registries by pointer and writes to none of them. |
| AUTHORITY OF ITS OWN | **NONE.** |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. WRITE CONFINEMENT — `AC-9`

`AC-9` requires: *"CIOS writes only `00-MASTER/IMR-003A/`. Zero corpus mutation; zero registration drift introduced."* Stated as enforceable rules and then measured.

| ID | Rule |
|---|---|
| `RI-1` | CIOS writes **only** within `00-MASTER/IMR-003A/`. |
| `RI-2` | CIOS mutates **no** corpus artifact, in any zone, for any reason. |
| `RI-3` | CIOS consumes **no** corpus identifier and creates **no** `id-ledger` entry. |
| `RI-4` | CIOS introduces **no** registration drift. |
| `RI-5` | CIOS reads located registries; it writes to none. |
| `RI-6` | CIOS creates **no** registry, gate, validator or identifier space of its own (`CIOS-INV-12`). |
| `RI-7` | A write attempt outside `RI-1` fails closed and is recorded as a finding (`WS-9`). |

### 1.1 The structural basis of confinement

Confinement is not a policy CIOS promises to keep; it is a property of the write-scope matrix. Reading the last row of `CIOS-02` §4.1:

| Target | `PL-A` | `PL-B` | `PL-C` | `PL-D` |
|---|---|---|---|---|
| Located corpus artifacts (outside `00-MASTER/IMR-003A/`) | — | — | — | — |

**No plane has write access to any corpus artifact.** Since every engine belongs to exactly one plane (`CIOS-03` §4), no engine can write outside the mission home. `AC-9` therefore holds by construction rather than by discipline.

### 1.2 Registration-exclusion basis

| Check | Result | Evidence |
|---|---|---|
| Mission home is in a registration-excluded zone | **PASS** | `00-BOOK/tools/config.py :: EXCLUDE_DIR_PREFIXES → "00-MASTER/"` |
| Consequence | CIOS artifacts are invisible to `REG-AUTO-001` automatic registration | no identity allocated, no `id-ledger` entry, no drift |
| Programme standing basis | `UCCEP-000006` §1 **P-5** — programme-owned output under `00-MASTER/<PROGRAMME-ID>/` | precedent: `WP-IMR-001`, `WP-UCCEP-*`, `WP-UCDA-*`, `WP-GDR-*` |
| Corpus identity consumed | **ZERO** — by design, not by omission | `IMR-003A` OUTPUT 0.4 |

**Recorded consequence, not a defect:** because the mission home is registration-excluded, CIOS carries **programme standing, not `REG-AUTO-001` corpus identity**. No `CIOS-*` identifier is a corpus identifier (`NS-3`).

---

## 2. REGISTRY BINDINGS — POINTERS ONLY

Every registry CIOS touches is **read-only**. This table is the registry contract set the recovery instruction requires.

| Registry | Located owner | CIOS reads for | CIOS writes? | Bound by |
|---|---|---|---|---|
| `00-CMG/CMG-REGISTRY.json` | CMG | artifact kinds (`CMG-K-01…24`) → `CIOS-ID-10`; tiers; states; concerns; vacancies (`VAC-01`) | **NO** | `E-06`, `E-07` |
| `id-ledger` (`00-BOOK/tools/`) | `REG-AUTO-001` | duplicate-identifier detection | **NO** | `E-06` |
| `artifacts.json` | `REG-AUTO-001` | registered-artifact population; FROZEN population (27) | **NO** | `E-06` |
| `UAKOS-CLOSURE-002/closure.json` | UAKOS | closure truth; canonical homes; the seven gap classes | **NO** — CIOS does not regenerate it (`E-20` EXCLUDES) | `E-03`, `E-04`, `E-06` |
| UAKOS canonical-home register | UAKOS | `CIOS-ID-11`, `CIOS-ID-12` resolution | **NO** | `E-04` |
| `UCCEP-000000/uccep-bindings.json` + `uccep.json` | UCCEP | gates `G-01…G-14`; checks `CK-*`; findings `UCCEP-F-001…008` | **NO** | `E-02`, `E-05`, `E-06`, `E-08`, `E-09` |
| `UCDA-000001/ucda-decisions.json` | UCDA | decision disposition and evidence obligation | **NO** | `E-09` |
| `CEP-009` evolution registry | `CEP-009` | change classes; lineage | **NO** | `E-09`, `CIOS-OR-01` |
| `CEP-007` freeze registry (Art XVI) | `CEP-007` | the frozen surface, so CIOS never touches it | **NO** — gains **no** entry from CIOS | `E-19`, `OR-10` |
| `IMG-001` backlog / graph / waves / order / critical path | IMG-001 | `CIOS-K-01…K-06` inputs; family→owner map → `CIOS-ID-13` | **NO** | `E-08`, `E-12` |
| `IEC-001` queues / states / gates | IEC-001 | Execution Queue admission; batch-cut boundary | **NO** | `E-14`, `E-15` |
| AIF ledger | AIF | minted identity fields `CIOS-ID-01…ID-08` | **NO** | `E-07` |
| `MCP-001 … MCP-007`, `MCS-000` | MCS/MCP | master context, state, execution, decisions, dashboard, traceability, recovery | **NO** | context binding |
| `UCIC-001` | UCIC-001 | capability implementation contract | **NO** — note `GG-6` (absent from `CMG-REGISTRY.json`) undischarged | `E-09` |

**Registries written by CIOS: 0.** **Registries created by CIOS: 0.** **Registry entries added by CIOS: 0.**

### 2.1 The freeze registry, specifically

`CEP-007` Art XVI's freeze registry gains **no entry** from CIOS, and the FROZEN population in `artifacts.json` (27 artifacts) is unchanged by any CIOS or `IMR-003A-R1` act. This satisfies `GD-10` acceptance criterion 1 and honours `GD-10-C1` and `GD-10-C2`.

---

## 3. REPOSITORY TRUTH INTEGRATION

| Property | Value |
|---|---|
| Authoritative source | `00-MASTER/UAKOS-CLOSURE-002/closure.json` |
| Values relied upon | `determination=CLOSED` · `concept_total=434` · `gap_total=0` · all seven gap classes `0` |
| Re-verified this mission | **YES** — values identical to those `IMR-003A` recorded |
| The seven gap classes | `conversation_only`, `duplicate_canonical_homes`, `in_repo_unhomed`, `not_homed_concepts`, `orphan_concepts`, `ukda_content_hash_duplicates`, `upload_only` — all `0` |
| Read by | `E-03`, `E-04`, `E-06` (`CIOS-PL-A`); `E-22`, `E-23` (`CIOS-PL-D`) |
| Written by | **nothing in CIOS** |
| Regenerated by | `IEC-001` `07` / C10 / RG-3 — **located**, never CIOS (`E-20` EXCLUDES) |
| Appended to by | `CIOS-PL-C` via `CIOS-P-40`, **append-only** (`WS-4`; `AIF-L17`) |

### 3.1 The read/append distinction

CIOS's relationship to Repository Truth is asymmetric and deliberately so:

| Operation | Permitted | Plane | Basis |
|---|---|---|---|
| Read | **YES** | `PL-A`, `PL-B`, `PL-C`, `PL-D` | truth is the input to every derivation (`CIOS-L-16`) |
| **Append** | **YES** | `PL-C` only, via `CIOS-P-40` | `WS-4`; `AIF-L08` DAG ledger |
| Edit | **NO** | none | `AIF-L17` forward-only |
| Delete | **NO** | none | `AIF-L17`; `GD-13` no-deletion |
| Regenerate | **NO** | none | `IEC-001` `07` owns regeneration |
| Read-modify-write | **NO** | none | would be an edit |

`IMR-003A` OUTPUT 0.6 records *"Repository Truth unchanged — `closure.json` neither read-modified nor regenerated"*. That property is preserved by this recovery mission: no artifact of `IMR-003A` or `IMR-003A-R1` writes `closure.json`.

---

## 4. ZONE INTEGRATION MATRIX

CIOS's relationship to every repository zone. `R` = read · `—` = no access · `W` = write.

| Zone | Access | Note |
|---|---|---|
| `00-MASTER/IMR-003A/` | **W** | the **only** writable zone |
| `00-MASTER/IMR-003A-R1/` | **W** | recovery-mission zone (this mission only) |
| `00-CEP/` | R | constitutional instruments; **X-2** observed |
| `00-CMG/` | R | meta-governance + registry |
| `00-BOOK/` | R | control tower, tools, master book |
| `00-MASTER/` (other programmes) | R | UAKOS, UCCEP, UCDA, IMR-001, etc. |
| `02-MASTER/` | R | AIF, GOV-001, GOV-004 |
| repository-root `01-…11-*.md` | R | `IEC-001`, `IMG-001` source files |
| `engine/` | R | located engines |
| `platform/` | R | measurement |
| `intelligence/` | R | RIE |
| `knowledge/` | R | knowledge substrate |
| `application/` | — | **FROZEN** at Band-12 baseline `beff9ed3…` (**X-6**) |
| `data/`, `service/` | — | frozen band surfaces (**X-6**) |
| `infrastructure/` | — | U01…U11 CERTIFIED-not-frozen; U12 freeze DEFERRED (**X-7**) |
| `adr/`, `scripts/`, `dist/`, `.github/` | — | outside CIOS scope |

**Zones CIOS may write: 2, both programme-owned and registration-excluded. Zones CIOS may mutate: 0.**

The frozen and freeze-gated surfaces are listed with **no access** rather than read access, to make `GD-10-C2` structurally unreachable: a mutation there would be void and would place the Program in HALTED (`CEP-007` IX.5).

---

## 5. INTEGRATION WITH THE LOCATED IMPLEMENTATION STACK

| Located layer | Integration point | Direction | Port |
|---|---|---|---|
| `IEC-001` `05` batch-cut boundary | Quiescent Adoption Point | CIOS **reads** | `CIOS-P-27` |
| `IEC-001` `04` Execution Queue | handoff | CIOS **writes a handoff record** and relinquishes control | `CIOS-P-30` |
| `IEC-001` `03` P1–P7 | READY evaluation | **none** — CIOS does not evaluate them | — |
| `IEC-001` `06` state machine | item states | CIOS **reads** terminal-state events | `CIOS-P-37` |
| `IEC-001` `08` Q1–Q8 | quality gates | **none** — located gate authority | — |
| `IEC-001` C7 | dispatch | **none** — CIOS holds no dispatch authority | — |
| `IEC-001` `07` / RG-3 | regeneration | **none** | — |
| `IMG-001` `03`–`09` | backlog, graph, waves, order | CIOS **reads** for `CIOS-K-*` | `CIOS-P-23` |
| `CEP-004` / `verify.sh` | validation | located execution interval | — |
| `CEP-005` / EC-3 gate | certification | located execution interval | — |
| `CEP-008` | evidence & traceability | CIOS **emits** a traceability edge | `CIOS-P-42` |

**Total integration surface: 2 signals in (`P-27`, `P-37`), 1 handoff out (`P-30`), plus truth/traceability append (`P-40`, `P-42`) and findings (`P-44`, `P-46`, `P-48`).** This narrow coupling is what leaves the located stack sovereign (`CIOS-01` VII.1, VII.2).

---

## 6. INTEGRATION PROPERTIES

| Property | Value | Basis |
|---|---|---|
| Writable zones | **2** (mission homes) | §4 |
| Corpus artifacts mutated | **0** | §1.1 |
| Registries written | **0** | §2 |
| Registries created | **0** | `RI-6`; `CIOS-INV-12` |
| Registry entries added | **0** | §2 |
| Freeze registry entries added | **0** | §2.1; `GD-10` AC-1 |
| Corpus identifiers consumed | **0** | §1.2 |
| Registration drift introduced | **0** | §1.2 |
| Frozen surfaces accessed | **0** | §4 |
| `closure.json` writes | **0** | §3 |
| Repository Truth operations available | read + append only | §3.1 |
| Located queues/gates/predicates re-implemented | **0** | §5 |

---

## AUTHORITY BOUNDARY (MANDATORY)

This artifact declares read-only bindings to located registries and proves write confinement. **CIOS owns no registry**, creates none, writes to none, and adds no entry to any. It owns no mechanism, no gate, no identifier space and no concern. No CIOS artifact declares, implies or records a freeze, a freeze baseline or a freeze authorization; the freeze registry and the FROZEN population are unchanged. Where this artifact and a located canonical instrument disagree, **the located instrument governs and this artifact SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `CIOS-13` · PROVISIONAL · ADDITIVE · COMPOSITION-ONLY · AUTHORITY-NEUTRAL**
