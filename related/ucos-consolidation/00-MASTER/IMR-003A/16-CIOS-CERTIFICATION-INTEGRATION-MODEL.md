# CIOS-16 — CONTINUOUS IMPLEMENTATION OPERATING SYSTEM · CERTIFICATION INTEGRATION MODEL

| Field | Value |
|---|---|
| MISSION | `IMR-003A` — CIOS Constitution & Architecture |
| ARTIFACT | `CIOS-16` — Certification Integration Model (mission Output 16) · **also the Certification Specification** (required output 15) |
| DELIVERED BY | `IMR-003A-R1` gap closure (Phase 4). **Additive**: no recovered artifact mutated. |
| OBLIGATION DISCHARGED | recovery instruction: *"Every certification rule is documented."* |
| CENTRAL LIMIT | CIOS holds **no certification authority**. `CEP-005` (`CMG-DLG-05`) is the certification authority. CIOS **certifies nothing** — not a corpus artifact, not an implementation, not itself. |
| AUTHORITY OF ITS OWN | **NONE.** |
| BASELINE | `b26c5bb` |
| STANDING | PROVISIONAL; Tier T1 VACANT |

---

## 1. THE CERTIFICATION CEILING

Everything in this artifact is bounded by a single measured fact:

| Fact | Evidence |
|---|---|
| Aggregate certification is capped at **`CERTIFIED-PROVISIONAL`** | `CMG-REGISTRY.json` `readiness.ceiling_reason`: *"`CMG-OQ-01` and `CMG-OQ-02` remain open; `VAC-01` is unclosed (`CMG-000001` LXXX.4)"* |
| Cause | Tier **T1 VACANT** (`VAC-01`, `located: false`); `CEP-006` names no competent authority; *"No programme may self-ratify"* (`UCCEP-000006` **ED-1**) |
| Population | 31 of 43 recognized artifacts are PROVISIONAL |
| Consequence for `CEP-005` | **active, non-provisional certification is unavailable corpus-wide** |
| Consequence for `CEP-007` | the IV.1 certification limb cannot be satisfied ⇒ freeze ineligible (`GD-10`) |

**No act of CIOS or of this recovery mission raises this ceiling.** Every certification-adjacent statement below is capped at PROVISIONAL, and the cap is a located fact, not a CIOS choice.

---

## 2. LOCATED CERTIFICATION MACHINERY (BOUND)

| Located mechanism | Concern | Where it acts | CIOS |
|---|---|---|---|
| `CEP-005` | certification authority, certification lifecycle, active certification | corpus-wide | binds |
| **EC-3 gate** | the certification owner for implementation objects | located execution interval | binds; located predicate `P6` requires it be defined |
| `IEC-001` C9 | Certification Trigger — fires EC-3 certification on VALIDATED objects | located execution interval | binds |
| `IEC-001` `08` **Q6** | invalid-certification gate: EC-3 owner present; object VALIDATED before CERTIFIED; `certified=true` only after gate pass | `VALIDATED → CERTIFIED` | binds |
| `IEC-001` `03` **P6** | `certification_owner_exists` READY predicate | READY evaluation | binds |
| `UCCEP-000000` **`G-11`** | Certification Gate | constitutional | binds |
| `engine/certification` | certification engine | located | binds |
| `UCCEP-000000` `12-CERTIFICATION-INTELLIGENCE.md` | certification intelligence | located | binds |
| `UMB-017` | certification architecture | located | binds |
| `CEP-006` | ratification — the limb that lifts the ceiling | corpus-wide | binds — **unavailable** |

**Where certification acts.** Entirely inside the located execution interval between `CIOS-S-23` and `CIOS-S-24` (`CIOS-07` §3), where CIOS declares **zero** stages. CIOS cannot precede, replace, duplicate or shortcut it.

---

## 3. CERTIFICATION RULES

| ID | Rule | Basis |
|---|---|---|
| `CR-01` | CIOS certifies **nothing** — no corpus artifact, no implementation, no submission, and not itself. | `CEP-005`; `CIOS-INV-12` |
| `CR-02` | Certification of an implementation object is performed by the located EC-3 gate, triggered by `IEC-001` C9, gated by Q6. | `IEC-001` |
| `CR-03` | An object reaches `CERTIFIED` only from `VALIDATED`; `certified=true` only after the located gate passes. | `IEC-001` `06`, Q6 |
| `CR-04` | CIOS does not seal an item that has not reached a terminal state, and `IEC-001` `06` reaches terminal only through the located certification path. | `E-19`; `CIOS-S-24` |
| `CR-05` | **`CIOS-PT-01` SEALED is not a certification status.** An item may be SEALED as terminally archived without being CERTIFIED. | `CIOS-01` Art V |
| `CR-06` | The certified set is monotone non-decreasing across epochs. No admission, realignment, adoption or override may reduce it. | `CIOS-L-20`; `CIOS-INV-10`; `CEP-001` LAW-7 |
| `CR-07` | CIOS **observes** monotonicity (`E-23`) and cannot enforce it. Remedy is `CIOS-OR-02`'s. | `CIOS-12` §5 `MP-5` |
| `CR-08` | Every CIOS determination is capped at PROVISIONAL. No CIOS artifact claims active, final or ratified certification. | `CMG-L-12`; `UCCEP-F-004`; §1 |
| `CR-09` | No CIOS artifact claims `CEP-005` certification for itself by virtue of any self-check passing. | `VR-11`; `AC-4` |
| `CR-10` | No CIOS artifact declares, implies or records a freeze, freeze baseline or freeze authorization — including by presenting certification as freeze-eligibility. | `CEP-007` II.4, IV.4; `GD-10-C1`; `GR-32` |
| `CR-11` | CIOS creates no certification gate, no certification registry and no certification status vocabulary. | `AC-4`; `CIOS-INV-12` |
| `CR-12` | CIOS discharges no certification-related finding and no `GG-*` or `CIOS-G-*` gate. | `CIOS-01` IX.4 |

### 3.1 `CR-05`, expanded

The distinction matters because a naive reading equates "sealed" with "certified" and would silently inflate the certified set:

| Route into `CIOS-PT-01` | Certified? | Located basis |
|---|---|---|
| terminal state `CERTIFIED` | **yes** | `IEC-001` `06`; EC-3 gate |
| terminal state `ARCHIVED` (not-required sentinel, deferred park) | **no** | `IEC-001` `06` |
| terminal state `ARCHIVED` after retries exhausted | **no** | `IEC-001` `06`; escalated per `09` |
| terminal state `SUPERSEDED` → `ARCHIVED` | **no** | `IEC-001` `06` |

`CIOS-PT-01` membership is therefore a **superset** of the certified set. `E-23` observes the certified set specifically (`CIOS-INV-10`), never `CIOS-PT-01` cardinality, or monotonicity would be trivially satisfiable by archiving failures.

---

## 4. CIOS'S OWN CERTIFICATION STANDING

| Question | Answer | Basis |
|---|---|---|
| Is CIOS certified? | **No.** It carries `CERTIFIED-PROVISIONAL` disclosure as a programme, not an artifact certification. | `CMG-L-12`; §1 |
| Is CIOS validated under `CEP-004`? | **No.** | `VR-04` |
| Is CIOS ratified under `CEP-006`? | **No.** T1 VACANT; no competent authority. | `VAC-01`; `CMG-OQ-02` |
| Is CIOS freeze-eligible under `CEP-007` IV.1? | **No.** Three limbs fail: ratification, active certification, rooted-and-closed traceability. | `GD-10` |
| Can any CIOS act change these answers? | **No.** All four require located authorities that do not currently exist or are unavailable. | `UCCEP-000006` **ED-1** |
| What is the unblocking condition? | **closure of `VAC-01`** — an external constituent act, reserved to `CEP-007`'s and `CEP-006`'s owners. | `GD-10-C4` |

Recorded as `CIOS-GAP-13` with the owner named. This is the residue the recovery mission cannot close, and it is stated rather than absorbed.

---

## 5. WHAT THE ARCHITECTURE FREEZE DOES *NOT* CLAIM

Stated here because certification is the limb most likely to be misread as satisfied once the architecture is complete. Cross-referenced from `IMR-003A-R1/04-GAP-ANALYSIS-MATRIX.md` §5.

| Claim | Made by the stability contract? |
|---|---|
| The architecture is complete | **YES** |
| Interfaces are stable and downstream missions may rely on them | **YES** |
| Change is routed through `CEP-009` III.1 rather than in-place edit | **YES** |
| The architecture is implementation-ready | **YES** |
| CIOS is VALIDATED (`CEP-004`) | **NO** |
| CIOS is CERTIFIED-active (`CEP-005`) | **NO** |
| CIOS is RATIFIED (`CEP-006`) | **NO** |
| CIOS is FROZEN (`CEP-007`) | **NO** |
| CIOS artifacts are immutable in the constitutional sense | **NO** |
| A freeze baseline exists | **NO** |
| `VAC-01` is closed or affected | **NO** |
| Any `UCCEP-F-*`, `GG-*`, `IAC-001 B+C` or `CIOS-G-*` gate is discharged | **NO** |

---

## 6. CERTIFICATION PROPERTIES

| Property | Value |
|---|---|
| Certification rules documented | **12** (`CR-01 … CR-12`) |
| Located certification mechanisms bound | **10** |
| Artifacts certified by CIOS | **0** |
| Certification gates created by CIOS | **0** |
| Certification registries created by CIOS | **0** |
| `CEP-005` statuses claimed by CIOS | **0** |
| Certification ceiling raised | **NO** — capped at `CERTIFIED-PROVISIONAL` |
| Freeze eligibility claimed | **NO** — ineligible on three limbs |
| Findings or gates discharged | **0** |

---

## AUTHORITY BOUNDARY (MANDATORY)

This artifact documents certification rules and binds each to a **located** certification mechanism. **CIOS certifies nothing.** It holds no certification authority, creates no certification gate or registry, claims no `CEP-005` status, raises no certification ceiling, and asserts no freeze eligibility. Nothing here declares, implies or records a freeze, a freeze baseline or a freeze authorization. Where this artifact and a located canonical instrument disagree, **the located instrument governs and this artifact SHALL be corrected**. It confers no authority on itself and authorizes no execution.

**END OF ARTIFACT — `CIOS-16` · PROVISIONAL · ADDITIVE · COMPOSITION-ONLY · AUTHORITY-NEUTRAL**
