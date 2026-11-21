# IMPLEMENT-001B · DELIVERABLE 06 — APPROVED REMEDIATION BACKLOG

| Field | Value |
|---|---|
| MISSION | `IMPLEMENT-001B` |
| AUTHORITY | `NONE — DERIVED TRUTH` — records approved remediation; authorizes no execution |
| ADMISSION RULE | **Only findings dispositioned `FIX` appear here.** `REJECT` / `WAIVE` / `DEFER`-to-existing-owner items are excluded or carried under their existing identifier. |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier T1 VACANT |

> **PHASE 5 CONSTRAINT OBSERVED: NOTHING IN THIS BACKLOG WAS IMPLEMENTED.**
> This mission wrote 6 report files and modified **0** existing files. Verified:
> `git diff --stat` reports the same 86 files as at mission entry.

---

## 1. ADMISSION RECORD

| Finding | Disposition | Admitted to backlog? | Rationale |
|---|---|---|---|
| C-1a | **REJECT** | **NO** | Invalid — no defect exists |
| C-1b | **ACCEPT** (reclassified) | **NO** | Discharged by `OA-1`, an existing registered P0 action — not new work |
| **C-1c** | **FIX** | **YES → `RB-01`** | New, evidence-backed implementation defect |
| **C-1d** | **FIX** | **YES → `RB-02`** | New, evidence-backed repository defect (P-7 condition unmet) |
| C-2 | **WAIVE** | **partial → `RB-04`** | Code correct; only the disclosure record is owed |
| C-3 | **DEFER** | **YES → `RB-03`**, under existing `WP-UCCEP-004` / `OA-3` | Substance valid; carried under its **existing** identifier, not a new one |
| C-4 | **REJECT** | **NO** — residue merged into `RB-02` | Invalid as reported; residue is `RB-02` content |
| **C-5** | **FIX** | **YES → `RB-05`** | New, evidence-backed implementation defect |

**5 backlog items from 8 findings. 3 new identifiers (`RB-01`, `RB-02`, `RB-05`); 2 carried
under existing ownership.**

---

## 2. THE APPROVED BACKLOG

### `RB-01` — Reconcile the DP-03 guard with its authority chain

| Field | Value |
|---|---|
| **Source** | `C-1c` · conflicts `CF-01`, `CF-02` |
| **Classification** | Implementation defect (tooling over-reach) |
| **Priority** | **P0 — BLOCKING FOR PUSH** (not for commit) |
| **Owner** | `engine/foundation` |
| **Route** | **P-7** corrective mutation — `frozen_paths.py` is in `engine/**` |
| **Scope** | **S** — ~2 lines |
| **Required change** | Either (a) narrow `frozen_paths.py:17` `FROZEN_PREFIXES` to the located scope — `00-SOURCE/`, `99-FREEZE/`, and the authored `00-BOOK` canon (`UCOS-BOOK-000000-*.md`, `MASTER-BOOK/`, `ADVANCEMENT/`) — excluding `SCHEMAS/` and `tools/`; **or** (b) extend `ec1-ci.yml:96-97` to exclude `00-BOOK/(SCHEMAS\|tools)/`, citing `REG-AUTO-001` §2 and `STATUS-001:122`. **(a) is preferred** — it fixes the guard rather than routing around it. |
| **Mandatory proof obligation (P-7)** | Demonstrate the corrected guard **still failing closed** on `00-SOURCE/`, `99-FREEZE/`, and the authored `00-BOOK` canon. Negative-path test required. |
| **Validation** | `verify.sh` GREEN · existing `frozen_paths` tests pass · new negative-path tests pass · `./repo-ops.sh` `architecture-freeze` → PASSED |
| **Certification** | Removes `CF-01` and `CF-02`; unblocks the CI DP-03 step |
| **Discharges** | `C-1c` · `CF-01` · `CF-02` · the `architecture-freeze` half of `C-2` |

> **Why P0-for-push and not P0-for-commit:** the guard runs on `git diff BASE HEAD` in CI. With
> no remote configured (`GG-4` OPEN) it cannot run today. The commit is therefore safe; the
> **push** is not.

---

### `RB-02` — Register the P-7 work package for the freeze-gated gate corrections

| Field | Value |
|---|---|
| **Source** | `C-1d` + the entire valid residue of `C-4` · conflicts `CF-04`, `CF-06` |
| **Classification** | Repository defect — P-7's *"only under an existing work package"* unmet |
| **Priority** | **P0 — BLOCKING FOR COMMIT** |
| **Owner** | change author + Registration Authority |
| **Precedent** | `WP-UCCEP-003` — the P-7 precedent named in the rule itself |
| **Scope** | **S** — one work-package record; **0 lines of code** |
| **Required content** | 1. The work-package identifier, under a token that does **not** shadow `EIP-018` (which already denotes the USIS establishment mission per `UCOS-USIS-001/00:7`, and is cited in committed `config.py:69,265,787`) — discharges `CF-06`/`NF-4`. 2. The `FP-1…FP-14` finding register the 8 comment lines cite — currently undeclared. 3. The declared additive surfaces: `platform/repository_operations/{engine,stages}.py`, 4 test files, `repo-operations.json`. 4. The located gate defects: `FP-13` acceptance-by-fiat (`repo-operations.json` HEAD `:64-71`, six × `covered:1/total:1`); `FP-14` empty freeze subject (HEAD `:23` `"paths": []`); `FP-2`/`FP-3` uccep-gate environment + tier; `FP-7`/`FP-8` CI fail-open guard + gate subsetting. 5. The negative-path evidence already present: `test_freeze_stage_empty_declared_subject_is_fail_closed`, `test_freeze_stage_unknown_subject_source`, measured-coverage-absent fail-closed. 6. Optionally re-cite the 8 comment lines to the new token — **do not delete them** (`GOV-002` `RA5` makes them traceability evidence). |
| **P-7 conditions** | (i) located owner's gate defective ✓ · (ii) `verify.sh` passes ✓ · (iii) negative path demonstrated ✓ · **(iv) existing work package ⛔ ← this item** |
| **Validation** | The work package resolves; every declared surface exists; `verify.sh` GREEN |
| **Certification** | Brings 7 `platform/**` files inside the declared boundary. **The only genuine constitutional deficiency in the change set.** |
| **Discharges** | `C-1d` · `C-4` residue · `CF-04` · `CF-06` |

---

### `RB-03` — Make schema validation mandatory *(carried under existing ownership)*

| Field | Value |
|---|---|
| **Source** | `C-3` · conflict `CF-03` |
| **Existing identifiers** | **`UCCEP-F-006`** (`disposition=REGISTERED`, `blocking=false`) · **`WP-UCCEP-004`** · **`OA-3`** (P2, Blocking: **No**, OPEN) |
| **Classification** | Tooling limitation — pre-existing, already registered |
| **Priority** | **P2** — as determined by its located owner. **Not re-prioritized by this mission** (`X-9`: no cross-programme edits). |
| **Owner** | `00-BOOK/tools/ukb.py` · `.github/workflows/ucos-registration-gate.yml` |
| **Scope** | **S** — 2 lines |
| **Required change** | 1. Add `jsonschema==<pin>` to `pyproject.toml:27-32` — `ucos_expected_deps()` (`scripts/ucos-env.sh:104-120`) derives its expectation from that list and will then require it automatically, so **one edit fixes both** the venv and the gate. 2. Drop `\|\| true` from `ucos-registration-gate.yml:40`. 3. *(optional, and the work package's actual title)* make `ukb.py:1733-1735`'s `ImportError` branch fail-closed. |
| **Validation** | `verify.sh` Stage 5 prints `"jsonschema validation: ran."` on a **clean bootstrap** · `ucos_ensure_venv` installs it |
| **Certification** | Closes `CF-03`. **Required before any unqualified release claim** under `RELEASE-001` §4 (*"Schema + referential integrity PASS"*). |
| **Note** | Also discharges the unfinished half of `CAEM-001` §05 **S-2**. |

---

### `RB-04` — Record the `repository-acceptance` expected-fail disclosure

| Field | Value |
|---|---|
| **Source** | `C-2.1` (the one sub-item surviving the `C-2` WAIVE) |
| **Classification** | Incomplete implementation — disclosure only |
| **Priority** | **P2** |
| **Owner** | `EPIC-PLAT-003` (registered as a `SPECIFICATION_GAP`, `code=Y, cert=N, spec=N`, `UAKOS-PHASE-003/03:55`) |
| **Scope** | **S** — record only; **0 lines of code** |
| **Required content** | 1. `repo-ops.sh` `repository-acceptance` is **expected-FAIL** while `CoverageProfile.REQUIRED` demands 6 dimensions and the coverage toolchain measures 2. 2. State that this is **deliberate** (`stages.py:103-106`: *"an unmeasured dimension is unproven, never 100%"*) and that the prior PASS was vacuous (HEAD declared `covered:1/total:1` × 6). 3. Name the owner for measuring `functions`, `public_api`, `exception_paths`, `repository`. 4. Record that `repo-ops.sh` is bound to **no** gate — absent from `verify.sh`, `RELEASE-001` §4, `G-01…G-15`, `uccep.json`, and all 12 workflows. |
| **Validation** | Record exists and resolves |
| **Certification** | None — `repo-ops.sh` gates nothing |

---

### `RB-05` — Make `rib.json` convergent

| Field | Value |
|---|---|
| **Source** | `C-5` · conflict `CF-07` |
| **Classification** | Implementation defect — self-referential non-convergence |
| **Priority** | **P1** |
| **Owner** | `UCOS-RIB-001` |
| **Scope** | **S** — ~5 lines in `rib_engine.py` |
| **Evidence** | `rib.json` diff was `+129/−30` at `IMPLEMENT-001A`'s measurement and `+137/−30` after — **+8 lines** caused solely by `00-MASTER/IMPLEMENT-001A/` being created between gate runs. The artifact records `untracked: 10` while the tree holds 11, and `IMPLEMENT-001A` is absent from its own `dirty_paths` list. |
| **Required change** | Either exclude `dirty_paths` / `dirty_entries` from the **persisted** artifact (report them to stdout only), or compute them strictly over the committed tree. The gate verdict may still fail on a dirty tree — only the *persisted measurement* must not embed it. |
| **Validation** | Run `make rib-gate` twice on an unchanged dirty tree → `rib.json` **byte-identical**. Then on a clean tree → `GATE-12` and `GATE-04`/`VAL-02` PASS. |
| **Certification** | Restores `RFP-1` compatibility for `UCOS-RIB-001`. `UCOS-RFP-001` is behaving **correctly** by aborting on `CLO-01`; the defect is RIB's. |
| **Note** | Low urgency in practice — the condition self-clears on a clean tree — but it means every gate run on a dirty tree mutates a tracked file, which is exactly what `RFP-1` forbids. |

---

## 3. DEPENDENCY ORDER

```
                          ┌─────────────────────────────────────────┐
                          │  RB-02  register the P-7 work package   │
                          │         (0 lines · BLOCKING FOR COMMIT) │
                          └────────────────┬────────────────────────┘
                                           ▼
                          ╔═════════════════════════════════════════╗
                          ║  OA-1  ATOMIC REGISTRATION COMMIT       ║
                          ║  registered P0 · "YES — suspensive"     ║
                          ║  discharges O-01 · UCCEP-F-007 ·        ║
                          ║  WP-UCCEP-005 · C-1b · RIB GATE-12 ·    ║
                          ║  RIB GATE-04/VAL-02 · RFP CLO-01        ║
                          ╚════════════════┬════════════════════════╝
                                           ▼
                          ┌─────────────────────────────────────────┐
                          │  RB-01  reconcile the DP-03 guard       │
                          │         (~2 lines · BLOCKING FOR PUSH)  │
                          └────────────────┬────────────────────────┘
                                           ▼
                                    ── PUSH (GG-4) ──
                                           │
        ┌──────────────────────────────────┼──────────────────────────────────┐
        ▼                                  ▼                                  ▼
  RB-05  rib.json                    RB-03  jsonschema              RB-04  disclosure
  convergence (P1, ~5 ln)            (P2, 2 ln, WP-UCCEP-004)       (P2, 0 ln)
```

| Order | Item | Why here |
|---|---|---|
| **1** | `RB-02` | P-7 requires the work package to exist **before** the mutation is lawful. 0 lines. |
| **2** | **`OA-1` commit** | The registered **P0 suspensive** act. Discharges `C-1b` and four gate failures. Not a backlog item — an existing registered operator action. |
| **3** | `RB-01` | Must precede any push or the CI DP-03 step rejects the branch. Safe to sequence after the commit because no remote exists. |
| **4** | *push* | `GG-4`. The certified baseline currently exists on one disk. |
| **5–7** | `RB-05` · `RB-03` · `RB-04` | Independent; parallelizable. `RB-03` gates any unqualified release claim (`CF-03`). |

**No cycles.** `RB-01`, `RB-03`, `RB-04`, `RB-05` are mutually independent.

---

## 4. VALIDATION PLAN

| Item | Command | Exit criterion |
|---|---|---|
| `RB-01` | `verify.sh` · `pytest platform/tests engine/tests` · negative-path tests on `00-SOURCE/`/`99-FREEZE/` · `./repo-ops.sh` | GREEN; guard rejects X-1 paths; `architecture-freeze` PASSED |
| `RB-02` | declaration cross-resolution; every declared surface exists | work package resolves; `FP-1…FP-14` register declared |
| `RB-03` | fresh venv → `./verify.sh` | Stage 5 prints `"jsonschema validation: ran."` |
| `RB-04` | record exists | resolves from `repo-operations.json` |
| `RB-05` | `make rib-gate` twice on an unchanged tree; `diff` the artifact | **byte-identical** |
| **All** | `./verify.sh` · `make uccep-gate` · `make closure-gate` | GREEN · blocking=none · CLOSED gaps=0 |

## 5. CERTIFICATION PLAN

| Step | Gate | Exit criterion |
|---|---|---|
| 1 | `verify.sh` | 5/5, exit 0, coverage ≥90% |
| 2 | `make uccep-gate` | `blocking=none`, `unproven=none` |
| 3 | `make closure-gate` | `CLOSED`, gaps=0 |
| 4 | `make ucda-gate` | `ASSIMILATED`, 0 undispositioned |
| 5 | `make rib-gate` | **exit 0** — reachable only post-commit + `RB-05` |
| 6 | `make rfp-gate` | **evaluable** — reachable only post-commit |
| 7 | `RELEASE-001` §4 × 7 | all PASS, Stage 5 unqualified after `RB-03` |
| 8 | record evolution version | `EVOLUTION-001` §6 + `RELEASE-001` §3.2 → `UCOS-EVO-001-W01` |

---

## 6. WHAT IS **NOT** IN THIS BACKLOG

| Excluded | Reason |
|---|---|
| Reverting `00-BOOK/SCHEMAS/*.schema.json` | No instrument freezes them; four Control-Tower standards authorize additive deltas; the widening is provably admits-only; reverting restores **539 schema violations** |
| Reverting `00-BOOK/tools/config.py` | Not a corpus artifact (`REG-AUTO-001` §2); it is a **declared input** to registration (§3 P3); ≥10 prior commits |
| A `CEP-009` amendment | CEP-009 **II.2/II.5** disclaim freeze jurisdiction; **V.1** eligibility unmet; 0 references to schemas or paths |
| Reverting `platform/repository_operations/**` | P-7 substantive conditions met; reverting restores gates that cannot fail |
| Removing the `EIP-018 (FP-N)` comments | `GOV-002` §6/`RA5` treat code citations as traceability evidence to **preserve**; removal is a regression |
| Restoring `coverage: [6 × covered:1/total:1]` | Restores certification by fiat — the defect `FP-13` removed |
| Restoring `"paths": []` | Restores a guard over an empty subject — the defect `FP-14` removed |
| Re-opening `C-3` under a new id | `X-9` forbids cross-programme edits; carried as `RB-03` under `WP-UCCEP-004` |
| Any `EB-01…EB-09` work | Wave-002 scope; out of this mission |

---

## 7. DETERMINATION

> **Approved remediation backlog: 5 items · ~9 lines of code · 3 records · 0 amendments.**
>
> `RB-02` (0 lines) is the only item blocking the commit. `RB-01` (~2 lines) is the only item
> blocking the push. The remaining three are P1/P2 and parallelizable.
>
> **Nothing in the 86-file change set requires revision.** The remediation is entirely additive:
> one guard correction, one work-package record, one dependency pin, one disclosure, one engine
> convergence fix.

---

*END — `IMPLEMENT-001B` Deliverable 06 · AUTHORITY = NONE · `CERTIFIED-PROVISIONAL` · Tier T1 VACANT*
