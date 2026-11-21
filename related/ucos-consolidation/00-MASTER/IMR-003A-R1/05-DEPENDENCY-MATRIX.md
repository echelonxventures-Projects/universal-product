# IMR-003A-R1 · OUTPUT 5 — DEPENDENCY MATRIX

| Field | Value |
|---|---|
| MISSION | `IMR-003A-R1` |
| ARTIFACT | Output 5 — Dependency Matrix |
| SCOPE | **CIOS ↔ located corpus** dependencies. The **engine-internal** dependency graph is owned by `IMR-003A/06-CIOS-ENGINE-DEPENDENCIES.md` and is **bound here by pointer, not restated** (Knowledge Once). |
| CHECKPOINT | CP-006 |
| DISCLOSURE | PROVISIONAL; Tier T1 VACANT |
| VERDICT | **ALL DEPENDENCIES VERIFIED.** 35 located bindings resolve; 0 dangling; 0 cyclic; 0 mutating. |

---

## 1. WHAT THIS MATRIX ADDS

Two dependency surfaces exist. Conflating them would duplicate a located model.

| Surface | Owner | Content |
|---|---|---|
| **Engine-internal** — `CIOS-E-nn → CIOS-E-mm` | `IMR-003A/06` | 25 `DERIVES` edges, 63 `OBSERVES` edges, acyclicity proof, both graph scopes |
| **CIOS ↔ located corpus** — this artifact | `IMR-003A-R1/05` | which located instrument each CIOS artifact depends on, in which direction, and whether the dependency mutates |

This artifact owns only the second. For the first, see `IMR-003A/06` (machine-verified by `r1_verify.py` `V-24` … `V-32`).

---

## 2. DIRECTION VOCABULARY

| Symbol | Direction | Meaning |
|---|---|---|
| `→R` | CIOS **reads** the located instrument | pointer binding; located instrument unaware of CIOS |
| `→A` | CIOS **appends** via a located mechanism | append-only; never edit, never delete |
| `→H` | CIOS **hands off** to a located mechanism and relinquishes control | one-way; CIOS retains no authority after |
| `→F` | CIOS **emits a finding** for a located authority to act on | advisory; never an act |
| `⊘` | **no dependency** | recorded to prove absence |

**No row anywhere in this matrix carries a mutating direction.** There is no `→W` symbol, because no such dependency exists (`CIOS-13` §1.1; `r1_verify.py` `V-73`).

---

## 3. PER-ARTIFACT DEPENDENCY MATRIX

| CIOS artifact | Depends on (located) | Dir | Nature of dependency |
|---|---|---|---|
| `00` Registration record | `CEP-009`, `CEP-001`, `CMG-000001`, `GOV-INT-001` §7.2, `UCCEP-000006` P-5 | `→R` | admission route, authority basis, programme-home convention |
| `01` Constitution | `CEP-001`, `CEP-009`, `CMG-000001`, `GOV-INT-001`, + 30 bindings in OUTPUT 0.5 | `→R` | law enforcement for all 24 laws |
| `02` Operating Model | `IEC-001` §4 loop; `AIF-L17`; `CEP-008` | `→R` | plane clocks; append-only basis |
| `03` Engine Architecture | `engine/graph`, `engine/knowledge`, `engine/validation`, `engine/certification`, `platform/measurement`, `intelligence/rie` | `→R` | 11 BOUND engines' located mechanisms |
| `04` Engine Responsibilities | `UAKOS`, `UCCEP` `G-01…G-14`, `AIF`, `REG-AUTO-001`, `CEP-009`, `IAC-001D` §05 | `→R` | per-engine exclusion boundaries |
| `05` Engine Interfaces | `IEC-001` `04` (Execution Queue); `CEP-008` | `→H`, `→A` | `P-30` handoff; `P-40`/`P-42` append |
| `06` Engine Dependencies | `engine/graph`, `CK-GRAPH` | `→R` | acyclicity **not** delegated — `UCCEP-F-003` fails open |
| `07` Lifecycle Model | `UCCEP` `G-01…G-14`; `IEC-001` `02`,`03`,`04`,`05`,`06`,`08` | `→R` | 20 stages gate-bound; located execution interval |
| `08` Identity Model | `AIF-L01…L24`, `REG-AUTO-001`, `00-BOOK/tools/`, `CMG-REGISTRY.json`, `UAKOS`, `IMG-001` `02` | `→R` | 19 of 22 fields minted/resolved externally |
| `09` Queue Model | `IEC-001` `04` | `→H` | boundary at the located Execution Queue |
| `10` Scheduling Model | `IEC-001` `04`,`05`; `IMG-001` `04`,`05`,`07`,`09`; `AIF-L04` | `→R` | `CIOS-K-01…K-06` inputs; batch-cut boundary |
| `11` Protection Model | `CEP-009` Art III/XX.2; `CEP-010`; `CEP-002`; `CEP-007` IX.5 | `→R` | both override authorities located |
| `12` Evolution Model | `CEP-009` Art VI/XVI/XXIII.10/XXIV; `UCI-001`; `intelligence/rie`; `IEC-001` `07` | `→R` | CIOS owns **no** evolution model |
| `13` Repository Integration | 14 registries (§4 below) | `→R` | all read-only |
| `14` Governance Model | `CEP-001…010`, `CMG-000001`, 19 `CMG-DLG-*` delegations | `→R` | all 33 `GR-*` rules externally owned |
| `15` Validation Model | `CEP-004`, `verify.sh`, `engine/validation`, `IEC-001` Q5/C8/P5, `G-10`, `CK-VERIFY` | `→R` | CIOS validates no corpus artifact |
| `16` Certification Model | `CEP-005`, EC-3 gate, `IEC-001` Q6/C9/P6, `G-11`, `engine/certification`, `UMB-017` | `→R` | CIOS certifies **nothing** |
| `17` Traceability Model | `CEP-008`, `CEP-001` XVIII, `UMB-007`, `UCCEP` `07`, `IEC-001` Q7/C12, `AIF-L08/L11/L17` | `→R`, `→A` | emits edges; claims no closure |
| `18` Impact Assessment | `CEP-009` III.1/IV.1/IV.6 | `→R` | route obligation |
| `19` Gap Analysis | `VAC-01`, `UCCEP-F-001…008`, `GG-3/4/6`, `IAC-001 B+C`, `GD-10` | `→R` | 14 gaps, 7 gates, all externally owned |
| `20` Constitutional Verification | all of the above | `→R` | Art X.1 closure test |
| `cios-bindings.json` | 35 located paths | `→R` | machine binding declaration |

---

## 4. REGISTRY AND TRUTH DEPENDENCIES

| Located source | Dir | Read for | Written? |
|---|---|---|---|
| `UAKOS-CLOSURE-002/closure.json` | `→R` | Repository Truth: `CLOSED`, 434, `gap_total=0`, 7 zero classes | **NO** |
| `CMG-REGISTRY.json` | `→R` | kinds, tiers, states, concerns, `VAC-01` | **NO** |
| `artifacts.json` | `→R` | registered population; FROZEN population (27) | **NO** |
| `id-ledger` | `→R` | duplicate-identifier detection | **NO** |
| `uccep-bindings.json` / `uccep.json` | `→R` | `G-01…G-14`, `CK-*`, `UCCEP-F-001…008` | **NO** |
| `ucda-decisions.json` | `→R` | disposition and evidence obligation | **NO** |
| `CEP-009` evolution registry | `→R` | change classes, lineage | **NO** |
| `CEP-007` freeze registry (Art XVI) | `→R` | the frozen surface, so CIOS never touches it | **NO** — gains no entry |
| AIF ledger | `→R` | minted fields `ID-01…ID-08` | **NO** |
| `IMG-001` backlog / graph / waves / order / critical path | `→R` | `CIOS-K-*` inputs; family map | **NO** |
| `IEC-001` queues / states / gates / batch boundary | `→R`, `→H` | admission conditions; boundary signal | **NO** |
| `MCP-001 … MCP-007`, `MCS-000` | `→R` | master context | **NO** |
| `UCIC-001` | `→R` | capability contract (`GG-6` open) | **NO** |
| `00-BOOK/tools/config.py` | `→R` | registration-exclusion basis | **NO** |

**Registries written: 0. Registry entries added: 0. Freeze registry entries added: 0.** Machine-verified `V-72`, `V-73`.

---

## 5. ABSENT DEPENDENCIES (`⊘`)

Recorded because proving absence is what establishes non-duplication.

| Would-be dependency | Status | Why absent |
|---|---|---|
| CIOS → dispatch authority | `⊘` | `IEC-001` C7 dispatches; `CIOS-01` I.4 |
| CIOS → READY predicate evaluation | `⊘` | `IEC-001` `03` P1–P7; CIOS does not re-evaluate |
| CIOS → item state transitions | `⊘` | `IEC-001` `06` |
| CIOS → quality gate verdicts | `⊘` | `IEC-001` `08` Q1–Q8 |
| CIOS → batch formation | `⊘` | `IEC-001` `05` |
| CIOS → identity minting | `⊘` | `AIF` + `REG-AUTO-001`; `CIOS-L-14` |
| CIOS → `closure.json` regeneration | `⊘` | `IEC-001` `07` / C10 / RG-3 |
| CIOS → wave partition definition | `⊘` | `IMG-001` `04`; CIOS extends by successor only |
| CIOS → freeze / seal act | `⊘` | `CEP-007`; unavailable (`GD-10`) |
| CIOS → ratification | `⊘` | `CEP-006`; T1 VACANT |
| CIOS → corpus artifact write | `⊘` | no plane has the scope (`CIOS-13` §1.1) |
| **located instrument → CIOS** | `⊘` | **no located instrument depends on CIOS.** CIOS is purely additive; deleting both mission homes restores `b26c5bb` exactly |

The last row is the operative property: **the dependency is strictly one-directional.** Nothing located would break if CIOS were removed, which is what makes the recovery mission fully reversible (`CIOS-18` §9).

---

## 6. DEPENDENCY VERIFICATION

| Check | Result | Machine check |
|---|---|---|
| Located binding paths declared | **35** | `cios-bindings.json` `located_bindings` |
| Paths that resolve at `b26c5bb` | **35 / 35** | `V-81` |
| Dangling references (`CIOS-INV-11`) | **0** | `V-81` |
| Bindings copied or restated | **0** | `V-82` |
| Engine-internal cycles | **0** (both graph scopes) | `V-27`, `V-28` |
| Back-edges into `CIOS-PL-A` | **0** | `V-56` |
| Mutating dependencies | **0** | `V-73` |
| Located instruments depending on CIOS | **0** | §5 |
| Reversibility | **complete** | `CIOS-18` §9 |

---

## AUTHORITY BOUNDARY (MANDATORY)

This matrix records dependencies. It confers no authority, creates no dependency, mutates nothing, and authorizes no execution. The engine-internal dependency graph is owned by `IMR-003A/06` and is not restated here. Where this matrix and a located canonical instrument disagree, **the located instrument governs and this matrix SHALL be corrected**.

**END OF ARTIFACT — `IMR-003A-R1` OUTPUT 5 · PROVISIONAL · ADDITIVE · AUTHORITY-NEUTRAL**
