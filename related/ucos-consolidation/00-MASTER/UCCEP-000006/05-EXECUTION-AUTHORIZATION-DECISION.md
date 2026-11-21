# Output 5 — Execution Authorization Decision

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000006` — Repository Execution Authorization & Operator Transition |
| PHASE | 5 — Execution Authorization Decision |
| AUTHORITY | **NONE — DERIVED TRUTH.** This decision applies consequences already mandated by located instruments; it creates no authority |
| DATE | 2026-07-26 |
| REPOSITORY | HEAD `527485abf00f241a035dbd06062b78c1d9dcde31` · branch `programme/evo-usis-005` · tree DIRTY 127 |
| CERTIFICATION CEILING | `CERTIFIED-PROVISIONAL` (`UCCEP-F-004` — Tier T1 VACANT) — **this decision is itself provisional** |

---

## 1. Determination

> # AUTHORIZED WITH CONDITIONS

Exactly one determination is issued. `AUTHORIZED` (unconditional) and `NOT AUTHORIZED` are
both excluded; the reasoning is in §3.

## 2. Basis

| # | Ground | Evidence |
|---|---|---|
| B-01 | Every dependency precondition of implementation is satisfied | I-01…I-11, 11/11 re-confirmed (Output 4 §2) |
| B-02 | The execution model is complete, acyclic and deterministic | `scc_gt1_count = 0`; ordering 1199/1199; critical path 164; 164 groups, 0 unorderable |
| B-03 | Handover is complete and self-evidencing | 13/13 documents; 35/35 evidence digests; 10/10 mutation digests; 7/7 truth digests (Output 1) |
| B-04 | Repository integrity is intact with zero defects | 10/10 integrity domains; identity untouched; 0 hidden/duplicate/malformed dependencies (Output 3) |
| B-05 | The dependency gate is green **now**, not merely historically | `engine.graph.cli validate` re-run read-only: exit 0, output digest `00ca33637606a4e8…` identical to the digest of record |
| B-06 | `G-13` Implementation Authorization Gate PASS | full-tier run of record, over inputs verified byte-identical |
| B-07 | The live aggregate gate is non-blocking | `boot` tier: `CERTIFIED-PROVISIONAL`, exit 0, blocking **none**, seal `f638046250d4f88a…` |
| B-08 | Every outstanding item is an operator record act or an external constituent act | O-01…O-04 classified (Output 2); **none** is a dependency, architectural or integrity defect |

## 3. Why not the other determinations

| Determination | Excluded because |
|---|---|
| **AUTHORIZED** (unconditional) | `CK-REG-DRIFT` exits 3, `G-07` FAILs, and the full-tier aggregate gate exits 1. More concretely: `00-CMG/`, `00-MASTER/UCCEP-000000/` and **the handover package that justifies this authorization** are untracked. There is therefore no committed baseline to roll back to and no committed record of what implementation was authorized against. Issuing an unconditional authorization over that state would assert a reproducibility the repository does not currently have |
| **NOT AUTHORIZED** | No dependency defect, no architectural defect, no integrity defect and no unmet dependency precondition exists. Every outstanding item is owned elsewhere and none is a remediation failure. Denial would be unsupported by measured state |
| **EXECUTION DEFERRED** (exit verdict) | Deferral is appropriate when readiness cannot yet be determined. Readiness **was** determined: 11/11 inputs satisfied, integrity confirmed, `G-13` PASS. The outstanding items are bounded, named, owned and conditionable — they do not require the question to be re-asked |
| **EXECUTION DENIED** (exit verdict) | Same grounds as NOT AUTHORIZED |

## 4. Conditions

Authorization takes effect subject to the following. Conditions are **not** recommendations.

| # | Condition | Discharges | Owner | Timing | Effect if not met |
|---|---|---|---|---|---|
| **C-1** | Commit source **and** projections **atomically** (REG-AUTO-001) across all 127 working-tree entries — including untracked `00-CMG/`, `00-MASTER/UCCEP-000000/`, `00-MASTER/UCCEP-000005/`, the 37 portal projections, and the `config.py` / `ukb.py` `RECONCILED_SETS` change — then reconcile `MCP-002` §01 to the new HEAD and re-run the full-tier aggregate gate confirming `CK-REG-DRIFT` PASS / `G-07` PASS | O-01 · `UCCEP-F-007` · `WP-UCCEP-005` | repository operator | **BEFORE the first implementation mutation** | **Authorization does not take effect.** No implementation mutation is permitted |
| **C-2** | Update `00-MASTER/UCCEP-000000/uccep-bindings.json` to record `UCCEP-F-003` as discharged, and regenerate the findings register and ceiling | O-02 · `UCCEP-F-003` | UCCEP-000000 / `engine/graph` | **BEFORE the first certification claim** under UCCEP-000007 | Implementation may proceed; **no certification claim may be issued** while the ceiling names a discharged finding |
| **C-3** | Every artifact produced under this authorization discloses on its face that it is `CERTIFIED-PROVISIONAL` and that constitutional Tier T1 is VACANT (`UCCEP-F-004`) | O-04 (disclosure limb) | UCCEP-000007 | continuous | Any claim of ratified certification is void |
| **C-4** | Implementation stays inside the boundary in Output 6; the validation cadence in Output 6 §5 is executed at every stated point | this authorization | UCCEP-000007 | continuous | Authorization is **suspended** on first breach; implementation halts pending re-authorization |

**C-1 is a suspensive condition** — authorization does not take effect until it is discharged.
**C-2, C-3, C-4** are conditions of continued effect.

### 4.1 Why this programme did not discharge C-1 or C-2 itself

Both are explicitly assigned to other owners by the instrument that carried them. C-1 requires
a review-and-commit judgement over 127 entries including an entire uncommitted
meta-constitutional zone — an operator decision, and an irreversible act on shared history.
C-2 is another programme's declaration. This programme's mandate is to *verify prerequisites
and issue authorization*, not to perform other owners' acts. Both are registered in Output 7
with exact commands.

## 5. Scope of what is authorized

| Authorized | Not authorized |
|---|---|
| Transition into **controlled** implementation under UCCEP-000007 | Uncontrolled or unbounded implementation |
| Execution along the derived model — 164 parallel groups in ascending order, critical path as the sequential spine | Any execution order not derivable from the certified graph |
| Additive implementation inside the permitted mutation scope of Output 6 | Any mutation of protected areas (Output 6 §2) |
| Validation, evidence and certification acts at the cadence of Output 6 §5 | Any certification claim above `CERTIFIED-PROVISIONAL` |
| — | Dependency remediation (complete — closed by UCCEP-000005) |
| — | Architectural change, redesign, re-scoping, or new work packages |
| — | Identifier allocation, renumbering or release outside the governed path |

## 6. Duration and revocation

| Item | Value |
|---|---|
| Effective from | discharge of **C-1** |
| Valid while | HEAD lineage is a descendant of the C-1 commit · `G-08` remains PASS · `CK-GRAPH` remains PASS · the boundary of Output 6 is observed |
| Automatically **suspended** on | any `CK-GRAPH` / `G-08` regression · any protected-area mutation · any boundary breach · any identifier movement outside the governed path |
| Revocation authority | `UCCEP-000006`, or any successor gate programme applying a located instrument |
| Re-authorization after suspension | requires a fresh authorization act; implementation halts in the interim |

## 7. Decision record

| Item | Value |
|---|---|
| **Determination (Phase 5)** | **AUTHORIZED WITH CONDITIONS** |
| **Exit verdict** | **EXECUTION AUTHORIZED WITH CONDITIONS** |
| Certificate | Output 10 §1 (`10-HANDOVER-TO-UCCEP-000007.md`) |
| Certification status of this decision | `CERTIFIED-PROVISIONAL` — capped by `UCCEP-F-004`, disclosed not absorbed |
| Conditions | 4 (C-1 suspensive · C-2, C-3, C-4 continuing) |
| Blocking obligations outstanding | 1 — **O-01** |
| Remediation re-opened | **0** |
| Governance determinations repeated | **0** |
| New work packages created | **0** |
| Repository mutations made by this programme | **0** outside `00-MASTER/UCCEP-000006/` (its own outputs and evidence) |

---

**DETERMINATION: AUTHORIZED WITH CONDITIONS · C-1 SUSPENSIVE · NO IMPLEMENTATION MUTATION
PERMITTED UNTIL C-1 IS DISCHARGED**
