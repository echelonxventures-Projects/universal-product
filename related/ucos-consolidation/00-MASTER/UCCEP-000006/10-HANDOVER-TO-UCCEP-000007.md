# Handover Package → UCCEP-000007

**Repository Controlled Implementation Programme**

| Field | Value |
|---|---|
| FROM | `UCCEP-000006` — Repository Execution Authorization & Operator Transition |
| TO | `UCCEP-000007` — Repository Controlled Implementation Programme |
| TRIGGER | Exit verdict **EXECUTION AUTHORIZED WITH CONDITIONS** |
| AUTHORITY | **NONE — DERIVED TRUTH** |
| CONTROL TRANSFER | **CONDITIONAL** — effective on discharge of **C-1** |
| DATE | 2026-07-26 |

> The programme charter directs transfer on the verdict *EXECUTION AUTHORIZED*. The verdict
> issued is *EXECUTION AUTHORIZED WITH CONDITIONS*, so the package is transferred with the
> authorization **held suspensive**: UCCEP-000007 receives it, may plan against it, and may
> **not** mutate the repository until C-1 is discharged and recorded.

---

## 1. Authorization Certificate

| Field | Value |
|---|---|
| **CERTIFICATE ID** | `UCCEP-000006-AUTH-001` |
| **DETERMINATION** | **AUTHORIZED WITH CONDITIONS** |
| **EXIT VERDICT** | **EXECUTION AUTHORIZED WITH CONDITIONS** |
| ISSUED BY | `UCCEP-000006` · authority **NONE — DERIVED TRUTH** |
| ISSUED TO | `UCCEP-000007` — Repository Controlled Implementation Programme |
| ISSUED AT | 2026-07-26 |
| REPOSITORY | HEAD `527485abf00f241a035dbd06062b78c1d9dcde31` · branch `programme/evo-usis-005` |
| REPOSITORY TRUTH | 1199 artifacts · 25 volumes · 12841 edges · 1224 graph nodes · 4774 `Depends-On` edges · integrity **10/10 CERTIFIED** |
| EXECUTION MODEL | DAG acyclic · `scc_gt1_count` **0** · ordering **1199/1199** · critical path **164** · parallel groups **164** · unorderable **0** |
| GATE BASIS | `G-08` Dependency **PASS** · `G-13` Implementation Authorization **PASS** (full tier) · live aggregate `CERTIFIED-PROVISIONAL`, exit 0, blocking **none** |
| CERTIFICATION STATUS | **`CERTIFIED-PROVISIONAL`** — capped by `UCCEP-F-004` (`CMG-000001` PROVISIONAL, constitutional Tier T1 **VACANT**, no located authority competent to ratify) |
| **SUSPENSIVE CONDITION** | **C-1** — atomic registration commit (`OA-1`). **Authorization does not take effect until discharged** |
| CONTINUING CONDITIONS | **C-2** finding record before any certification claim · **C-3** provisional disclosure on every artifact · **C-4** boundary and cadence observed |
| SCOPE | Controlled, additive implementation along the certified execution model, inside the boundary of `06-IMPLEMENTATION-BOUNDARY-SPECIFICATION.md` |
| EXCLUSIONS | Dependency remediation (closed) · architectural change · redesign or re-scoping · new work packages · protected-area mutation · identifier movement outside the governed path · any claim above `CERTIFIED-PROVISIONAL` |
| VALID WHILE | HEAD lineage descends from the C-1 commit · `G-08` and `CK-GRAPH` remain PASS · the boundary is observed |
| AUTOMATIC SUSPENSION ON | `CK-GRAPH`/`G-08` regression · cycle introduction · protected-area mutation · boundary breach · identifier movement outside the governed path |
| **AUTHORIZATION SEAL** | `f497410c7217b3af57ff86bab451445e5a6a008a354bd9b9d6450435c0f385df` |
| SEAL DERIVATION | `sha256` over the 9 evidence filenames+digests (lexicographic), then HEAD, then the determination string — reproducible from `evidence/authorization-seal.txt` |

**Signature line.** This certificate creates no authority. It applies consequences already
mandated by located instruments and records a determination reached from measured repository
state. It is provisional on its face because every verdict in this corpus is.

## 2. Repository Readiness Report

| Dimension | Verdict | Basis |
|---|---|---|
| Execution readiness | **READY** | 11/11 inputs I-01…I-11 re-confirmed |
| Repository stability | **STABLE** | 7/7 truth digests · 10/10 mutation digests · HEAD unchanged · 0 identifier movements |
| Governance completion | **COMPLETE for execution** | `G-04`,`G-05`,`G-06`,`G-09` PASS · `G-08` PASS · `G-13` PASS |
| Validation completion | **ONE CHECK OUTSTANDING** | `CK-REG-DRIFT` exit 3 → `G-07` FAIL → full-tier exit 1 (non-dependency, operator-owned) |
| Certification constraints | **CAPPED PROVISIONAL** | `UCCEP-F-004`, irreducible in-repository |
| Repository integrity | **INTACT — 0 defects** | 10/10 integrity domains; 0 hidden/duplicate/malformed dependencies |
| Reproducibility | **IN PLACE, NOT FROM COMMITTED HISTORY** | 52 untracked entries — the reason C-1 exists |
| Operational risk | **ACCEPTABLE UNDER CONDITIONS** | 10 risks assessed; the one that could make mutation unrecoverable is neutralised by making C-1 suspensive |

Full detail: `01`…`04` of this programme.

## 3. Operator Action Register

`07-OPERATOR-ACTION-REGISTER.md` — 7 actions, 1 blocking.

| # | Action | Owner | Priority | Blocking |
|---|---|---|---|---|
| **OA-1** | Atomic registration commit + `MCP-002` reconciliation | repository operator | **P0** | **YES** |
| OA-2 | Record `UCCEP-F-003` discharged; regenerate ceiling | UCCEP-000000 / `engine/graph` | P1 | No |
| OA-3 | Install `jsonschema` (full schema validation) | `ukb.py` · CI | P2 | No |
| OA-4 | Close traceability completeness gap | CEP-008 · `platform/measurement` | P2 | No |
| OA-5 | Measured phase-3 closure verdict | UAKOS-CLOSURE successors | P3 | No |
| OA-6 | Constitute Tier T1 authority | external | — | Not actionable in-repository |
| OA-7 | Refresh stale CI signals | MEP-08 | P3 | No |

**OA-1 carries exact steps, verification commands, 8 acceptance criteria and cautions in
Output 7 §2.** It is the sole act standing between this authorization and effect.

## 4. Implementation Boundary

`06-IMPLEMENTATION-BOUNDARY-SPECIFICATION.md`, binding as condition **C-4**.

| Element | Count | Summary |
|---|---|---|
| Permitted mutation scopes | 7 | additive artifacts/source · generated projections · acyclicity-preserving declarations · own outputs · operational-memory reconciliation · gate correction under an existing WP |
| Protected areas | 10 | `00-SOURCE/`+`99-FREEZE/` · `00-CEP/` · `00-CMG/` · `id-ledger.json` · append-only ledgers · FROZEN baselines · CERTIFIED Band-13 constructs · `engine/`+`platform/` · other programmes' outputs · the certified execution model |
| Constraints | 12 | K-01…K-12 |
| Rollback requirements | 7 | RB-1…RB-7 — **RB-1: no mutation before a committed anchor exists** |
| Validation cadence points | 7 | V-0…V-6, all blocking |
| Evidence requirements | 8 | E-1…E-8 |

**First obligation on taking control:** execute **V-0** — confirm C-1 discharged
(`CK-REG-DRIFT` PASS, `G-07` PASS, full-tier exit 0) and record the commit SHA as the
rollback anchor. No mutation before that.

## 5. Risk Register

`08-RISK-ASSESSMENT.md` — 10 risks.

| # | Risk | Severity | Blocking | Treatment |
|---|---|---|---|---|
| R-01 | `UCCEP-F-003` record lag | LOW | No | C-2 / OA-2 |
| **R-02** | **Uncommitted registration** | **HIGH** (raised) | **YES** | **C-1 / OA-1** |
| R-03 | Traceability ≈22.7% | HIGH | No (advisory) | OA-4 · K-08 |
| R-04 | Tier T1 VACANT | STANDING | No | C-3 disclosure |
| R-05 | Constant phase-3 verdict | MEDIUM | No (advisory) | OA-5 · K-12 |
| R-06 | ENG out-of-sequence append | LOW | No | K-10 · fail-closed gate |
| **R-07** | **Mutation before a committed anchor** | **HIGH** | Neutralised | C-1 suspensive · RB-1 · V-0 |
| R-08 | Atomicity regression | MEDIUM | No | K-03 · V-3 · RB-3 |
| R-09 | Cycle reintroduction | MEDIUM | No | K-02 · V-2 · fail-closed gate |
| R-10 | Provisional presented as ratified | MEDIUM | No | C-3 · K-09 · V-5 |

## 6. Outstanding External Dependencies

| # | Dependency | Nature | Effect | Can it be manufactured? |
|---|---|---|---|---|
| **ED-1** | A constitutional **Tier T1 authority** competent to ratify (`UCCEP-F-004`; `CMG-000001` PROVISIONAL) | external constituent act | Caps every verdict, including this authorization, at `CERTIFIED-PROVISIONAL` | **No.** CEP-006 names no existing competent authority. No programme may self-ratify |
| **ED-2** | `jsonschema` availability in the validation environment (`UCCEP-F-006`) | environment/toolchain | `ukb validate` degrades to structural-only checks | Yes — OA-3 |
| **ED-3** | CI signal refresh (signals dated 2026-07-15 predate HEAD) | CI/CD environment | Control-tower signals stale; do not quote them as current | Yes — OA-7 |

## 7. What UCCEP-000007 must not do

| Prohibition | Basis |
|---|---|
| Begin any mutation before C-1 is discharged and the anchor recorded | C-1 suspensive · RB-1 · V-0 |
| Re-run or re-litigate dependency remediation | closed by UCCEP-000005 · K-06 |
| Modify repository architecture, redesign, or re-scope | programme rules · K-07 |
| Create new work packages | K-07 — `WP-UCCEP-001`…`005` are the registered set |
| Mutate a protected area | X-1…X-10 — suspends authorization |
| Edit another programme's declarations (including discharging C-2 itself) | X-9 — C-2 is UCCEP-000000's act |
| Claim certification above `CERTIFIED-PROVISIONAL` | C-3 · ED-1 |
| Report an advisory failure as passing | K-12 |
| Re-derive the execution model to suit convenience | X-10 |

## 8. Package index

| Output | File |
|---|---|
| 1 · Repository Handover Verification Report | `01-REPOSITORY-HANDOVER-VERIFICATION-REPORT.md` |
| 2 · Outstanding Obligations Assessment | `02-OUTSTANDING-OBLIGATIONS-ASSESSMENT.md` |
| 3 · Repository Integrity Report | `03-REPOSITORY-INTEGRITY-REPORT.md` |
| 4 · Implementation Readiness Assessment | `04-IMPLEMENTATION-READINESS-ASSESSMENT.md` |
| 5 · Execution Authorization Decision | `05-EXECUTION-AUTHORIZATION-DECISION.md` |
| 6 · Implementation Boundary Specification | `06-IMPLEMENTATION-BOUNDARY-SPECIFICATION.md` |
| 7 · Operator Action Register | `07-OPERATOR-ACTION-REGISTER.md` |
| 8 · Risk Assessment | `08-RISK-ASSESSMENT.md` |
| 9 · Executive Summary | `09-EXECUTIVE-SUMMARY.md` |
| — · This handover + certificate | `10-HANDOVER-TO-UCCEP-000007.md` |
| — · Evidence | `evidence/` (10 files) |

## 9. Evidence

| File | sha256 |
|---|---|
| `evidence/findings-dispositions.txt` | `a5baf9cbd6bcda8e5e3c28a2179c7877c5ffe241b5e5a6fdf618107e14403e04` |
| `evidence/graph-validate.json` | `00ca33637606a4e8c5d194a38f944e25dbd5e2e8be063a73a70304427bd34897` |
| `evidence/handover-digest-audit.txt` | `f332d888a09476378527e38a271bd8073c902f7df354a27c119d0cd54adb7d86` |
| `evidence/head.txt` | `d66ae791fd9bec80767fe128402e6654c7be407d31a7d1d20ae5740feadfe135` |
| `evidence/mutation-hash-verify.txt` | `99abedfacb2b2b3f9040381c1e0b3bdf2df90a7a21100d3c92fe17c40a6168be` |
| `evidence/register-state.txt` | `d98aa1368cfc8e9c960f5b5982ec89040b2d1a7815c4d767046cdfc7ac07320a` |
| `evidence/truth-hashes.txt` | `a3077a15460e19dc79c5397593c02ce2c1ef8915b9b182a39b57aa7d9af6a729` |
| `evidence/worktree-count.txt` | `6b693b3dcc8bfda1adc72c337731704df77a4d34f059515b161b99722be197e9` |
| `evidence/worktree.txt` | `d259d8e8ab12ae6d1828a89ce7afaee925f8231bd04b0a6de5c31dde2d6395cc` |
| `evidence/authorization-seal.txt` | seal input + `SEAL f497410c7217b3af…` (recomputable) |

Reproduction: `shasum -a 256 -c` against the table above; the graph digest reproduces via
`python3 -m engine.graph.cli validate`; the seal reproduces from
`evidence/authorization-seal.txt`.

---

**CONTROL TRANSFERRED CONDITIONALLY · AUTHORIZATION SUSPENSIVE ON C-1 · NO IMPLEMENTATION
MUTATION PERMITTED UNTIL THE OPERATOR COMMIT (OA-1) IS DISCHARGED AND THE ROLLBACK ANCHOR
RECORDED**
