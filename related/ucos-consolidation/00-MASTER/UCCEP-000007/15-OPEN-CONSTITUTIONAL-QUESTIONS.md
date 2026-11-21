# Output 15 — Open Constitutional Questions

> **STATUS DOMAIN:** GOVERNANCE (measurement) · **STATUS BASIS:** `00-CMG/CMG-REGISTRY.json → open_questions[]` and `→ vacancies[]`, reproduced at HEAD `9de85ad`

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000007` · OUTPUT 15 |
| AUTHORITY | **NONE — DERIVED TRUTH** |
| SUBJECT | Open constitutional questions and vacancies **as recorded by their owner**, `CMG-000001`. No question is answered, narrowed, or reinterpreted here. |
| RULE | `CMG-000001` XV.7 requires vacancies to be recorded as first-class entries and states that **concealing a vacancy is prohibited** (`CMG-P-06`). LVII.3 provides that a matter whose nature is genuinely undetermined is held as an open question — *holding IS a valid disposition; silent adoption is not*. |

---

## 1. Open questions (7 recorded, 3 CLOSED, 4 open)

| Id | Question | Requires | Blocks | Status |
|---|---|---|---|---|
| **CMG-OQ-01** | Which authority is competent to ratify `CMG-000001`? | EXPLICIT RATIFICATION | READY certification of `CMG-000001` | **OPEN** |
| **CMG-OQ-02** | Which artifact, if any, occupies Tier T1 (Constitutional Authority over substance)? | EXPLICIT RATIFICATION | Closure of `VAC-01` and non-provisional standing of **every** T2/T1M instrument | **OPEN** |
| **CMG-OQ-03** | Is the meta axis T1M correctly declared orthogonal to the process axis T2 rather than superior or subordinate? | EXPLICIT RATIFICATION | Finality of the precedence lattice | **OPEN** |
| CMG-OQ-04 | Who owns the Deferral Register lifecycle? | OWNERSHIP ALLOCATION BY THE ALLOCATING AUTHORITY | nothing | **CLOSED** — answered: `CEP-002`, by its Article 27 (`CEP-002-AMD-001` under Art 21); allocated by Governance Authority under `CEP-002` 1.2/7.2/14.2; recognized, not allocated, at `CMG-DLG-49` and LXXVIII.8 |
| **CMG-OQ-05** | Who owns program-completion ceremony? | OWNERSHIP ALLOCATION BY THE PROCESS OWNER | Closure of `CMG-GAP-06` | **OPEN** |
| CMG-OQ-06 | Does admission of the CMG namespace and zone require amendment of any located registration or classification instrument? | DETERMINATION BY THE REGISTRATION AUTHORITY | nothing — recognition achieved without editing shared machinery (LVIII.6) | **CLOSED** — closed by `REG-AUTO-001` SECTION 21 |
| **CMG-OQ-07** | Shall `CMG-INV-01…12` be adopted corpus-wide, or remain invariants of the meta layer only? | EXPLICIT RATIFICATION | Extension of meta invariants beyond the CMG namespace | **OPEN** |

Measured corroboration of `CMG-OQ-06`'s closure: `config.py :: RECONCILED_SETS` declares one reconciled set (`CMG`, zone `^00-CMG/`, namespace owner `CMG-000001`, determination `REG-AUTO-001 §21`, closes `CMG-OQ-06`), and the enforcement gate reports **1 reconciled set declared, 0 reconciled-set drift** (M-2 + M-3).

## 2. Vacancy (1 recorded)

| Field | Recorded value |
|---|---|
| Id | **`VAC-01`** |
| Tier | **T1** |
| Declared superior | The ratified UCOS Ω∞ Constitution presupposed at `CEP-000` §5.5 Tier 1 and §6.4 |
| Located | **false** |
| Evidence | *"The referent exists in the repository only as frozen non-normative source material under `00-SOURCE/CONSTITUTIONS/` (`.docx`). No ratified normative artifact occupies the tier."* |
| Closure procedure (`CMG-000001` XVII.4) | (a) record the vacancy; (b) record the determinations rendered provisional; (c) refer identification of the occupying authority to explicit ratification as an open question; (d) re-run authority resolution on closure |
| Open question | `CMG-OQ-02` |
| Gap of record | `CMG-GAP-04` (severity **STRUCTURAL-EXTERNAL**, disposition RECORDED-AS-VACANCY) |
| Aggregate finding | `UCCEP-F-004` |

## 3. Measured consequence of the vacancy

| Consequence | Measured | Method |
|---|---|---|
| Recognized artifacts in state PROVISIONAL | **31 of 43** | M-2 |
| Aggregate constitutional certification | capped at **CERTIFIED-PROVISIONAL** | M-3 |
| Digital-twin certification | CERTIFIED, but the standard itself is declared **non-terminal** (`UMB-017`; `AUTH-INF-001` CR-INF-011) | M-2 |
| Meta-constitutional readiness | **READY-PROVISIONAL** | M-3 |
| `CMG-000001` state in its own registry | **PROVISIONAL** | M-2 |

`CMG-000001` XVII.4 provides that resolution reaching a vacant tier **shall not skip the tier and shall not promote a lower instrument into it**, and that every dependent determination is treated as PROVISIONAL under `CMG-L-12`. `CEP-006` names no existing competent authority, and `UCCEP-000006` records the dependency as `ED-1` — *"external constituent act … **No.** No programme may self-ratify"*.

## 4. Questions this programme does not answer

Every entry above is reproduced with its recorded status and nothing more. This programme has no authority to answer, narrow, defer, or re-scope any of them, and does not do so. Items requiring an authority's decision to advance the consolidation work are listed separately in `16-DECISION-DERIVED-INPUTS.md`.

---

*`UCCEP-000007` Output 15. AUTHORITY = NONE (DERIVED TRUTH). Records what is open; answers nothing. `CERTIFIED-PROVISIONAL`; Tier T1 VACANT.*
