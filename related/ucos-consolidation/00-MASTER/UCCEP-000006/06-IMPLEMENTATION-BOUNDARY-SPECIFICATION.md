# Output 6 — Implementation Boundary Specification

| Field | Value |
|---|---|
| PROGRAMME | `UCCEP-000006` |
| PHASE | 6 — Implementation Boundary Definition |
| AUTHORITY | **NONE — DERIVED TRUTH.** This boundary restates constraints already imposed by located instruments (REG-AUTO-001, CEP-009, UCIC-001, the freeze notice, `config.py`); it invents none |
| BINDS | `UCCEP-000007` — Repository Controlled Implementation Programme |
| STATUS | Binding condition **C-4** of the authorization in Output 5 |

---

## 1. Permitted mutation scope

Implementation is **additive by default**. Anything not permitted here is protected.

| # | Permitted | Conditions |
|---|---|---|
| **P-1** | New artifacts in the zone assigned to the executing work package | Registered through `register.sh` / `ukb` in the same atomic unit; classification must resolve (0 OTHER/MISC) |
| **P-2** | New implementation source under an owning code tree (e.g. `infrastructure/**` for a Band-13 unit), plus its tests and evidence | Additive only; redefines no CERTIFIED construct; reuses by reference (UIL-02 pattern); EC-1 coverage gate preserved |
| **P-3** | Regenerated projections — `00-BOOK/DATA/*`, `00-BOOK/REGISTRIES/*`, `00-BOOK/CONTROL-TOWER/*`, `00-BOOK/PORTAL/*` | **Generated only.** Never hand-edited. Committed **atomically with their source** (REG-AUTO-001) |
| **P-4** | New `Depends-On` / lineage declarations | Must preserve acyclicity; `ENG-GOV-001` sequence order must be respected for any new `07-ENGINEERING/` artifact (R-06) |
| **P-5** | Programme-owned outputs, evidence and checkpoints under `00-MASTER/<PROGRAMME-ID>/` | Own directory only |
| **P-6** | Operational-memory reconciliation — `MCP-002` §01/§05, `MCP-005`, `mcs-state.json`, checkpoints | Reconciliation only, per MCP-007 §04.B; supersession recorded, lineage retained |
| **P-7** | Corrective mutation of a **freeze-gated** engine surface (`engine/**`, `platform/**`) where a located owner's gate is defective | Only under an existing work package; EC-1 `verify.sh` must pass; the corrected gate must be demonstrated **failing closed** on the negative path — the precedent set by `WP-UCCEP-003` |

## 2. Protected repository areas

Mutation of any of the following is **outside the boundary**. Touching one suspends the
authorization (Output 5 §6).

| # | Protected area | Basis | Rule |
|---|---|---|---|
| **X-1** | `00-SOURCE/` · `00-SOURCE-MANIFEST/` · `99-FREEZE/` | `99-FREEZE/FREEZE-NOTICE.md` — **Status: FROZEN**, 13 source files | **No source document may be modified.** Read-only, absolutely |
| **X-2** | `00-CEP/` constitutional instruments (`CEP-000`…`CEP-010` and ratified stage determinations) | constitutional corpus, VOL-002 | No mutation. Constitutional change is not an implementation act |
| **X-3** | `00-CMG/` meta-constitutional zone | `CMG-000001` (PROVISIONAL); `RECONCILED_SETS` zone `^00-CMG/` | No mutation. Currently **untracked** — must be committed under C-1 before it can be protected meaningfully |
| **X-4** | `00-BOOK/DATA/id-ledger.json` | identity integrity; 0/0/0 preserved across UCCEP-000005 | No hand edit. Identifier allocation only via the governed `ukb` path; never renumber, never release |
| **X-5** | `00-BOOK/DATA/*` page ledger and change ledger | append-only invariant, verified intact | Append-only. Never rewritten, never truncated |
| **X-6** | FROZEN code baselines — Band 12 `application/**` (baseline `beff9ed3…`), and every construct certified FROZEN in earlier bands (`data/**`, `service/**` frozen surfaces) | Band freeze determinations | No modification. Reuse **by reference** only |
| **X-7** | Band 13 `infrastructure/**` CERTIFIED constructs (U01…U11) | `UCOS-CERT-BAND-13-a900722db595b34c`; note Band-13 freeze (U12) is **DEFERRED**, so this tree is certified-complete but not yet frozen | Additive extension only; no redefinition of a CERTIFIED construct |
| **X-8** | `engine/**` · `platform/**` freeze-gated surfaces | EC-1 freeze + coverage gate | No mutation **except** under P-7 |
| **X-9** | Another programme's outputs, registers or declarations — including `00-MASTER/UCCEP-000000/uccep-bindings.json` and `00-MASTER/UCCEP-000005/**` | ownership discipline observed by UCCEP-000005 and by this programme | No cross-programme edits. C-2 is `UCCEP-000000`'s act, not the implementer's |
| **X-10** | The certified execution model — dependency graph, ordering, critical path, parallel matrix | UCCEP-000005 Outputs 7–9; `G-08` PASS | Not re-derived to suit convenience. May only change as a **consequence** of registered artifacts, never as an input choice |

## 3. Implementation constraints

| # | Constraint |
|---|---|
| **K-01** | **Execution order.** Parallel group *n* may execute concurrently in full; groups execute in strictly ascending order. The 96 single-member groups are the sequential spine (= the critical path) and admit no parallelism |
| **K-02** | **Acyclicity is invariant.** `scc_gt1_count` must remain 0 and `dependency_cycle` must remain `[]` after every unit. A cycle is PROHIBITED (CEP-009 Art XV.2) and places the programme in HALTED (Art XX.2) |
| **K-03** | **Atomicity.** Source and projections are committed in one unit. Splitting them is the exact defect O-01 exists to clear (`UCCEP-F-007`); reintroducing it is a boundary breach |
| **K-04** | **Registration parity.** After every unit: eligible on-disk artifacts = registered artifacts, 0 unregistered, 0 unclassified, 0 invalid, 0 reconciled-set drift |
| **K-05** | **Identity preservation.** No renumbering, no release, no out-of-band allocation. `id-ledger.json` moves only forward and only through the governed path |
| **K-06** | **No remediation reopening.** Dependency remediation is closed (UCCEP-000005). Implementation neither re-runs it nor re-litigates it |
| **K-07** | **No new work packages, no redesign, no re-scoping.** `WP-UCCEP-001`…`005` remain the registered set |
| **K-08** | **Traceability must not regress.** Semantic completeness (~22.7%, `UCCEP-F-002`) is already advisory-failing; implementation may improve it and must not lower it |
| **K-09** | **Provisional disclosure.** Every artifact states `CERTIFIED-PROVISIONAL` and the Tier T1 vacancy (condition C-3) |
| **K-10** | **ENG sequence.** Any new `07-ENGINEERING/` artifact respects `ENG-GOV-001` Output 11 Option B ordering (`ENG-000` → `ENG-005`), else it re-opens the R-06 defect class — now caught, because the gate fails closed |
| **K-11** | **Located owners only.** No second graph engine, no parallel validator, no shadow registry. Defects are corrected in the owning component (P-7) |
| **K-12** | **Advisory failures are disclosed, not absorbed.** `CK-HEALTH` and `CK-CLOSURE-P3` remain advisory-FAIL; no unit may report them as passing |

## 4. Rollback requirements

| # | Requirement |
|---|---|
| **RB-1** | **Committed baseline first.** The C-1 commit is the rollback anchor. Its SHA must be recorded in the first UCCEP-000007 output before any mutation. Until it exists, **no mutation is permitted** — there is nothing to roll back to |
| **RB-2** | **Per-unit anchor.** Each unit records the pre-mutation HEAD, the post-mutation HEAD, and the 7 `00-BOOK/DATA/*` digests before and after |
| **RB-3** | **Atomic revert granularity.** One unit = one atomic revert (source + projections + state). No unit may leave the repository in a state where reverting source orphans projections |
| **RB-4** | **Automatic rollback triggers.** `CK-GRAPH` FAIL · `G-08` FAIL · any cycle introduced · `verify.sh` non-zero · registration parity broken · any protected-area mutation detected · any identifier movement outside the governed path |
| **RB-5** | **Forward-only for ledgers.** Append-only ledgers are never rewritten. Rollback of a ledgered act is recorded as a **compensating forward entry**, never as history rewriting |
| **RB-6** | **No destructive git operations.** `reset --hard`, `push --force`, `clean -f`, branch deletion are outside the boundary and require an explicit operator act with its own authorization |
| **RB-7** | **Rollback is itself evidenced.** Any rollback produces a record: trigger, scope, restored digests, verification that the restored state matches the anchor |

## 5. Validation cadence

| Point | Mandatory checks | Blocking |
|---|---|---|
| **V-0 · Before first mutation** | C-1 discharged: `CK-REG-DRIFT` **PASS**, `G-07` **PASS**, full-tier aggregate exit 0; rollback anchor SHA recorded | **YES** |
| **V-1 · Per unit, pre-mutation** | `register.sh --guard` (10/10 integrity, zero drift) · `ukb enforce --pre` · `ukb validate` · record HEAD + 7 digests | **YES** |
| **V-2 · Per unit, post-mutation** | `verify.sh` (EC-1: ruff + pytest + coverage gate + governance enforce) · `engine.graph.cli validate` (`dependency_cycle = []`, `is_valid = true`) · registration parity | **YES** |
| **V-3 · Per unit, post-registration** | regenerate projections · `ukb validate` · confirm atomic source+projection commit · determinism check (second build byte-identical) | **YES** |
| **V-4 · Per parallel group boundary** | `uccep_engine.py --tier standard --gate` exit 0, blocking none · `G-08` PASS | **YES** |
| **V-5 · Per certification claim** | C-2 discharged · `uccep_engine.py --tier full --gate` reviewed · `CK-REG-DRIFT` PASS · ceiling disclosed | **YES** (for the claim) |
| **V-6 · Programme completion** | full re-execution sweep in the UCCEP-000005 pattern: every gate re-run from scratch, counts recomputed from live registers, every cited digest re-verified | **YES** |

Advisory at every point, disclosed and never reported as passing: `CK-HEALTH`,
`CK-CLOSURE-P3`, and the structural-only scope of `ukb validate` (`UCCEP-F-006`).

## 6. Evidence requirements

| # | Requirement |
|---|---|
| **E-1** | Every claim traces to a named evidence file with a sha256. No claim rests on narrative alone |
| **E-2** | Evidence is captured as **process output** (exit codes, logs, JSON), not transcribed from memory |
| **E-3** | Per-unit evidence set: pre-state (HEAD, digests, guard output) · mutation diffs · post-state gate outputs · determinism proof · commit SHAs |
| **E-4** | A per-programme evidence register in the `10-VALIDATION-EVIDENCE-REGISTER.md` pattern: file, digest, producing command, and a claim→evidence traceability table |
| **E-5** | Exit codes recorded verbatim, including expected failures. An expected FAIL is recorded as a FAIL with its reason, never rounded up to PASS |
| **E-6** | Digest stability: any digest cited must still resolve at completion. Digests that legitimately move (content fingerprints) are labelled as fingerprints, not as stability claims — the precision correction UCCEP-000005 made on itself (`13` §7) |
| **E-7** | Mutation register per unit: hand-authored vs generated, corpus artifacts edited (target 0), identifiers allocated/renumbered/released, blast radius |
| **E-8** | Negative-path evidence for any gate correction: the gate must be shown failing closed, not merely passing (the `WP-UCCEP-003` standard) |

## 7. Boundary breach handling

| Breach | Consequence |
|---|---|
| Protected-area mutation (X-1…X-10) | Authorization **suspended**; halt; roll back to the last anchor; record the breach |
| Cycle introduced (K-02) | HALTED per CEP-009 Art XX.2; roll back; the fail-closed gate now enforces this automatically |
| Split source/projection commit (K-03) | Unit rejected; re-commit atomically |
| Certification claim above `CERTIFIED-PROVISIONAL` | Claim void; disclosure corrected |
| Validation cadence skipped | Unit not accepted; V-1…V-3 re-executed in full |

---

**BOUNDARY DEFINED · 7 PERMITTED SCOPES · 10 PROTECTED AREAS · 12 CONSTRAINTS · 7 ROLLBACK
REQUIREMENTS · 7 VALIDATION POINTS · 8 EVIDENCE REQUIREMENTS · BINDING ON UCCEP-000007 AS
CONDITION C-4**
