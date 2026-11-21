# Output 16 — Decision-Derived Inputs

> **STATUS DOMAIN:** GOVERNANCE (measurement) · **STATUS BASIS:** measured absence of repository evidence, established by exhaustive search at HEAD `9de85ad`; owning authorities resolved from `00-CMG/CMG-REGISTRY.json → concerns[]` per `CMG-000001` Article XVII.2

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000007` · OUTPUT 16 |
| AUTHORITY | **NONE — DERIVED TRUTH** |
| SUBJECT | Items that **cannot be resolved from repository evidence**. Each is recorded with the required decision, the missing evidence, the owning authority, and why measurement cannot settle it. |
| BINDING RULE | **Nothing in this output is resolved.** `CEP-002` Art 28.5 provides that conversational assertion, recollection, restatement and summary are **not evidence**, and that a decision whose only trace is conversational is *not recorded*. A measuring programme that supplied the missing substance would be manufacturing exactly that defect. |

---

## 1. Measured basis for the absence

| Search | Result | Method |
|---|---|---|
| `grep -rn "M-1\b" --include="*.md" --include="*.json"` filtered for `migrat\|consolidat\|step` | **0 hits** | M-2 |
| `grep -rln "no new generators\|single execution owner\|consolidated execution generator\|MIGRATION SEQUENCE\|reference-only policy\|freeze policy"` across all `*.md` / `*.json` | 2 hits, both in `07-ENGINEERING/` and both concerning the Engineering Program's own roadmap and freeze policy — neither concerns UCCEP/UCDA consolidation | M-2 |
| Enumeration of every candidate host: `/01-REPOSITORY-DISCOVERY-REPORT.md` *(repository root)*, `00-MASTER/UCOS-ACE-001/`, `UCOS-CCD-001/`, `UCOS-ACFV-000001-…md`, `00-MASTER/CHECKPOINTS/` (latest `CKPT-2026-07-21-STATE-SYNC-001.md`), `.kiro/` | no consolidation-discovery artifact present | M-2 |
| `00-MASTER/UCCEP-000001` … `000004` | **no directory exists** (→ OBS-2) | M-1 |

The word "consolidation" elsewhere in the corpus refers to the historical **Constitutional Consolidation Program** (`02-MASTER/UCOS-Ω∞-CONSOLIDATION-PROGRAM-MASTER-INDEX.md`, Phases 0–9, recorded CLOSED WITH CONDITIONS) — a different, completed subject.

## 2. The thirteen consolidation determinations

Their **titles** are known from the authority's mission instruction; their **substance** has no repository trace. Under Art 28.5 a title conveyed conversationally is not evidence of a decision, so each is recorded below as an unresolved required decision.

For every item: **Missing evidence** = the decision statement, rationale, scope, dependency and located evidence references. **Why measurement cannot resolve it** = the subject is a choice among lawful alternatives, and no repository artifact records which alternative was chosen.

| # | Required decision | Owning constitutional authority (concern → owner) | Why repository evidence is insufficient |
|---|---|---|---|
| **DDI-01** | **Single execution ownership** — which single instrument owns consolidated execution | `GOV-INT-001` (`CMG-DLG-16` governance-integration-and-execution-architecture); execution *operation* remains `CEP-003` (`CMG-DLG-03`) | `GOV-INT-001` §2.15/§8 already fix one execution architecture as `ukb.py · ukbx.py · register.sh · connectors`. Whether that stands, is extended, or is superseded is a determination its owner must make; measurement cannot choose between them |
| **DDI-02** | **Ownership matrix** — the consolidated ownership rows and their canonical owners | the owner of each affected concern, per `CMG-000001` XX.7 (disagreements are findings disposed by the concern owner, never by a measuring instrument) | The located records (`/02-CANONICAL-OWNERSHIP-MATRIX.md` *(repository root)*, `CMG-REGISTRY.json → concerns[]`, `artifacts.json[*].owner`) are reproduced in Output 9. Which rows the consolidation *adds or changes* is nowhere recorded |
| **DDI-03** | **Consolidation mapping** — which programmes/trackers map onto which canonical owner | `GOV-INT-001` (`CMG-DLG-16`), with each mapped concern's owner concurring | No artifact records a source→target mapping. Output 2 measures 45 programme directories and Output 4 measures the register set; the mapping between them is a decision, not a measurement |
| **DDI-04** | **UCCEP as consolidated execution generator** | `GOV-INT-001` (`CMG-DLG-16`) — and, per `CMG-000001` **XVII.8**, *not* UCCEP itself: an instrument may not determine its own jurisdiction in a contested case | Measured tension: `GOV-INT-001` §2.15 names the `ukb` toolchain as the one execution architecture, while `UCCEP-000000`'s own charter declares `AUTHORITY = NONE`, "binding and aggregation only", and it is **absent from `CMG-REGISTRY.json`** (43 artifacts), so `CMG-L-01` bars citing it as constitutional authority. Whether that changes is a determination |
| **DDI-05** | **Reference-only policy** — what becomes reference-only and on what terms | `GOV-INT-001` §2.14 (single inheritance by reference) for execution architecture; `CEP-007` (`CMG-DLG-07`) where supersession is involved | The mechanism exists and is declared; its *application* to named programmes is unrecorded |
| **DDI-06** | **Freeze policy** — what is frozen, when, and by which baseline | `CEP-007` (`CMG-DLG-07` freeze-immutability-baselines-and-supersession-mechanics) | Output 6 §4 measures which surfaces are already declared FROZEN. Extending freeze to further programmes is an act reserved to the freeze owner |
| **DDI-07** | **Generator responsibilities** — which generator owns which output after consolidation | `REG-AUTO-001` (`CMG-DLG-13`) for registration/identity; `CMG-DLG-40` for the enforcement chain; `GOV-INT-001` for execution architecture | Output 7 measures the present generator→output map exhaustively. Reassignment is a determination; measurement records only the current state |
| **DDI-08** | **Migration sequence** (`M-1` … `M-n`) | `CEP-009` (`CMG-DLG-09` amendment-and-evolution-operation), with `GOV-INT-001` §7.2 as the located precedent form for an implementation sequence | **Zero repository hits** for any migration sequence. A sequence is decisional content (kind `CMG-K-17`, *Decisional* binding) and is inadmissible in an evidence artifact |
| **DDI-09** | **Implementation ordering** | `CEP-009` (`CMG-DLG-09`); `CMG-DLG-37` implementation-orchestration-and-realization (`06-IMPLEMENTATION` zone); `UCIC-001` for capability staging | Output 8 measures a *technical* ordering (164 layers, 1,199/1,199 placed). Which units a consolidation programme executes in which order is a separate, unrecorded decision |
| **DDI-10** | **No-new-documents policy** | `REG-AUTO-001` (`CMG-DLG-13`) for artifact creation; `CMG-000001` LXXVI.2(c) for the admission disposition (EXTEND is the declared default; CREATE requires recorded discovery) | The constraint form exists in law. Whether the consolidation adopts it as a binding policy, and over what scope, is unrecorded |
| **DDI-11** | **No-new-generators policy** | `GOV-INT-001` §2.15/§8; `CMG-DLG-40` (enforcement machinery) | Same as DDI-10: the principle is located; its adoption as a consolidation policy is not |
| **DDI-12** | **No-new-registries policy** | `CEP-002` Art 28.3 (a second decision register is PROHIBITED); `CMG-000001` X.14 `CMG-L-14` (no parallel machinery); `REG-AUTO-001` (`CMG-DLG-13`) | The prohibitions are located and measured. Their *extension* into a consolidation-wide policy is a determination |
| **DDI-13** | **No-deletion policy** | `CEP-007` (`CMG-DLG-07`); `CEP-002` Art 28.15 (a disposition is never deleted or overwritten); `REG-AUTO-001` L5 (forward-only, history never deleted) | Append-only is already law in three located instruments. Whether the consolidation restates it as its own policy, and over what scope, is unrecorded |

## 3. Further decision-derived inputs measured by this programme

| Id | Required decision | Owning authority | Why measurement cannot resolve it |
|---|---|---|---|
| **DDI-14** | Where the consolidation determination is authored, and in what form | resolved by concern lookup to `GOV-INT-001` (`CMG-DLG-16`, disposition REUSE) under `CMG-000001` XVII.2, which terminates at Step 1 | Location authority is resolvable from Repository Truth and was resolved. The **content** is not, which is why DDI-01…13 remain open |
| **DDI-15** | Disposition of the `AUTHORITY = NONE` vs Registry-Owner tension (→ DG-6) | the owner of each affected concern, per `CMG-000001` XX.7 and Article LII — explicitly *"never by this instrument"* and, by the same reasoning, never by a measuring programme | A disagreement among located ownership records is a finding for disposition, not a fact to be measured true or false |
| **DDI-16** | Whether `UCCEP-F-003`'s record is updated to reflect its discharged substance (→ DG-2) | `UCCEP-000000` / `engine/graph`; recorded as **OA-2** under condition **C-2** | The binding is another programme's declaration; boundary **X-9** forbids cross-programme edits |
| **DDI-17** | Whether the ignore policy `00-MASTER/**/evidence/` is retained, so prior authorization seals remain unreproducible from committed history (→ DG-8, DR-2) | the ignore authority's owner — `REG-AUTO-001` (`CMG-DLG-13`) / repository operator | The policy is deliberate and comment-scoped in `.gitignore`. Changing or keeping it is a choice, not a measurement |
| **DDI-18** | Whether `UCCEP-000001` … `000004` are intentionally absent, reserved, or retired (→ OBS-2) | `UCCEP-000000` (programme lineage) | Absence is measurable; its meaning is not |
| **DDI-19** | Whether registers 8–11 of the eleven-register set are to be realized (→ DG-1, OBS-16) | `UCI-001` (`CMG-DLG-15` change-intelligence-regeneration-and-synchronization) | `GOV-INT-001` §11 records them "READY TO ADD"; readiness is not a decision to add |
| **DDI-20** | Whether the OA-1 baseline is pushed to `origin`, giving the anchor existence off this machine (→ DR-1, OBS-12) | repository operator | No upstream is configured; whether to configure one is an operator act |
| **DDI-21** | Which authority occupies Tier T1 | **external constituent act** — `CEP-006` names no existing competent authority; `UCCEP-000006` records it as `ED-1`, *not manufacturable* | Recorded as `CMG-OQ-02` / `VAC-01`; no in-repository act can substitute (Output 15) |

## 4. What an authority must supply for M-1A to proceed

Recorded as an information requirement, **not** as a recommendation or a plan.

For each of **DDI-01 … DDI-13**: the decision statement, its rationale, its constitutional basis, its scope, its dependencies, its intended disposition from the closed set of `CEP-002` Art 28.13, and the located repository evidence each disposition requires. Absent that, any registration of these decisions would fail `CEP-002` Art 28.14 (a disposition whose required evidence does not resolve is **undispositioned**) and would close the Implementation Evidence Gate that is currently **OPEN** (Output 11 §7).

---

*`UCCEP-000007` Output 16. AUTHORITY = NONE (DERIVED TRUTH). Records what only an authority can decide; decides nothing, resolves nothing, and recommends nothing. `CERTIFIED-PROVISIONAL`; Tier T1 VACANT.*
