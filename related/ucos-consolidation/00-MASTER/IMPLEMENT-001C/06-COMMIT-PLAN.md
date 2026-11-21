# IMPLEMENT-001C · DELIVERABLE 06 — COMMIT PLAN

| Field | Value |
|---|---|
| MISSION | `IMPLEMENT-001C` |
| AUTHORITY | `NONE — DERIVED TRUTH` |
| BASIS | `IMPLEMENT-001B` Deliverable 07 §6, revised for the `IMPLEMENT-001C` surfaces |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier T1 VACANT |

> **Phase 5 is COMMIT PREPARATION.** No `git add`. No `git commit`. No history rewrite. No
> squash. Verified: `git status` reports **0 staged** changes.

---

## 1. DETERMINATION

> ### ✅ **ALL COMMIT PRECONDITIONS DISCHARGED. THE SEQUENCE MAY PROCEED.**

| Precondition (`IMPLEMENT-001B` D07) | Status |
|---|---|
| **`RB-02`** — register the P-7 work package — *blocking for commit* | ✅ **DISCHARGED** — `WP-RO-001`, 4/4 P-7 conditions met |
| **`RB-01`** — reconcile the DP-03 guard — *blocking for push* | ✅ **DISCHARGED** — CI review boundary corrected; negative-path proof executed |

**Zero outstanding preconditions.** Both the commit and the first push are now unblocked.

---

## 2. FILE INVENTORY

| Class | Count |
|---|---|
| **Modified** | **89** (86 inherited + 3 from `IMPLEMENT-001C`) |
| **Added** (untracked) | **42 files** in **13** `git status` entries |
| **Generated** (engine output within the change set) | **57** |
| **Removed** | **0** — 0 deletions, 0 renames; append-only intact |
| **Staged** | **0** |
| Insertions / deletions | +9,918 / −642 |

---

## 3. GROUPS

| Group | Count | Paths |
|---|---|---|
| **A** — Identifier-namespace widening (`RG-09-A`) | **14** | 13 × `00-BOOK/SCHEMAS/*.schema.json` + `00-BOOK/tools/config.py` |
| **B** — Verification + CI + environment | **7** | `verify.sh` · `scripts/ucos-env.sh` · `.gitignore` · **`pyproject.toml`** · `.github/workflows/{ec1-ci,uccep-gate,ucos-registration-gate}.yml` |
| **C** — Repository-operations fail-closed | **7** | `platform/repository_operations/{engine,stages}.py` · 4 × `platform/tests/test_repository_operations_*.py` · `repo-operations.json` |
| **D** — Programme engines + declarations | **4** | `UCCEP-000000/uccep_engine.py` · `UCDA-000001/{ucda_engine.py,ucda-decisions.json}` · **`UCOS-RIB-001/rib_engine.py`** |
| **E** — Regenerated programme projections | **56** | `UCCEP-000000/` ×20 · `UCDA-000001/` ×9 · `UCOS-RIB-001/` ×16 · `URRC-000001/` ×11 |
| **F** — Root determination | **1** | `03-ARCHITECTURAL-DECISION-ASSIMILATION-MATRIX.md` |
| **G** — Authority witness (untracked) | **42** | `BASELINE-001` · `EVOLUTION-001` · `RELEASE-001` · `CAEM-001` · `IMR-001/01-…` · `IMPLEMENT-001{,A,B,C}` · `UCDA-000001/07-…` · `UCOS-{CIOA,CCE,UAR}-001` |

**Bold** = surfaces added by `IMPLEMENT-001C` (`pyproject.toml`, `ucos-registration-gate.yml` → B;
`rib_engine.py` → D).

---

## 4. THE SEQUENCE — five commits

| # | Message | Groups | Files | Rationale |
|---|---|---|---|---|
| **1** | `RG-09-A: widen the identifier namespace ceiling (additive; existing data remains valid)` | **A** | 14 | **Isolated and independently revertable** — the only commit touching registered `00-BOOK` content. Cite `REG-AUTO-001` §2 + §3 P3 and `STATUS-001:122` as the authorizing basis, and record that the widening is **provably admits-only** (0 previously-valid identifiers rejected, verified by exhaustive enumeration). **No `CEP-009` amendment is cited, because CEP-009 II.2/II.5 disclaim freeze jurisdiction and the artifacts are not eligible subjects under V.1.** |
| **2** | `WP-RO-001: make the verification, CI and repository-operations gates fail-closed` | **B** + **C** | 14 | One concern: gates that could not fail now can. Carries the `RB-01` guard reconciliation, the `RB-03` `jsonschema` pin, and the negative-path tests that are `WP-RO-001`'s P-7 condition-(iii) evidence. Message must disclose that `repo-ops.sh` `repository-acceptance` is **expected-FAIL** and that `architecture-freeze` still reports 14 by design. |
| **3** | `UCCEP-000000 · UCDA-000001 · UCOS-RIB-001: disclose out-of-tier checks; assimilate architectural coverage; converge the blueprint model` | **D** + **E** + **F** | 61 | Engines + declarations + their deterministic projections **atomically**. Splitting them re-creates the source/projection split that `CK-REG-DRIFT` exists to detect. Includes the `RB-05` convergence fix and its regenerated `rib.json`. |
| **4** | `BASELINE-001 / EVOLUTION-001 / RELEASE-001 / OAA-001: commit the authority witness` | **G** (partial) | 12 | Discharges `B-1`. These are the instruments every determination in the change set rests on. |
| **5** | `IMPLEMENT-001{,A,B,C} · UCOS-{CIOA,CCE,UAR}-001: commit the mission record` | **G** (remainder) | 30 | The audit → disposition → execution chain, plus the three programme declarations. The `UCOS-UAR-001` message must record its **5 `EB-01` defects** so the partial state is history, not a surprise. |

**Total: 89 modified + 42 added = 131 paths across 5 commits.**

### 4.1 Ordering constraints — binding

| Constraint | Reason |
|---|---|
| **1 → 3** | 56 of group E's files are deterministic projections of state that group A alters (`config.py`'s `CLASSIFY_RULES` and `DERIVED_CATEGORY_MAXLEN` feed the registry). Committing 3 first would drift immediately. |
| **2 → 3** | Group E's `uccep.json` and `rib.json` are projections of gate state that group B/C alter. |
| **4 → 5** | Commit 5's determinations cite commit 4's authorities. |
| **`WP-RO-001` present from commit 2** | P-7 requires the work package to exist for the `platform/**` mutation in group C to be lawful. It lands in commit 5 as a file, but it **already exists on disk now** — the P-7 condition is satisfied at the time of the mutation, which is what the rule requires. **If strict same-commit co-location is preferred, move `00-MASTER/IMPLEMENT-001C/00-WP-RO-001-WORK-PACKAGE.md` into commit 2.** |

### 4.2 Single-commit alternative

Acceptable, not recommended. `REG-AUTO-001`'s atomicity requirement is trivially satisfied by one
commit and no rule forbids it. The reason to split is **reversibility**: group A is the only group
touching registered `00-BOOK` content and group C the only one under the `platform/**` freeze
gate. Bundling means a defect in either forces reverting all 131 paths.

### 4.3 Immediately after commit 5

```bash
./verify.sh          # must stay GREEN                      (AC-5 / RELEASE-001 §4)
make uccep-gate      # must stay blocking=none
make closure-gate    # must stay CLOSED, gaps=0
make rib-gate        # SHOULD NOW PASS — GATE-12 + GATE-04/VAL-02 discharged by the commit
make rfp-gate        # NOW EVALUABLE — CLO-01 no longer aborts on a dirty tree
```

Then record the evolution version in `EVOLUTION-001` §6 and `RELEASE-001` §3.2 as
**`UCOS-EVO-001-W01`**, per `RELEASE-001` §5.1 step 5. That act reaches the `RELEASED` lifecycle
state.

### 4.4 Then — and only then — push

`RB-01` unblocked the CI DP-03 guard, so the first push will pass it. **Configure the remote
first** (`GG-4`, OPEN): `UCOS-BASELINE-001` and 131 uncommitted paths exist on one disk.

---

## 5. WHAT THE COMMIT DISCHARGES

| Condition | Now | After |
|---|---|---|
| `OA-1` · `O-01` · `UCCEP-F-007` · `WP-UCCEP-005` — **P0, "YES — suspensive"** | OPEN | **DISCHARGED** |
| `CK-REG-DRIFT` / `G-07` — *"source split from projections"* | FAIL | **DISCHARGED** |
| **15** registered artifacts with `content_hash` drift | stale | **DISCHARGED** |
| `C-1b` — schema writes unregistered | open | **DISCHARGED** |
| `B-1` — Authority Witness (42 untracked files) | untracked | **DISCHARGED** by `git add` alone; registration is neither required nor possible (`00-MASTER/` exclude) |
| `UCOS-RIB-001` `GATE-12` — `dirty_entries_outside_generated=85` | FAIL | **DISCHARGED** |
| `UCOS-RIB-001` `GATE-04` / `VAL-02` | FAIL | **DISCHARGED** |
| `UCOS-RFP-001` `CLO-01` abort | ABORT | **EVALUABLE** |
| `RELEASED` lifecycle state | not reached | **REACHABLE** |

**One sequence. Nine conditions.**

---

## 6. SAFETY REVIEW — `RELEASE-001` §2.2

| Prohibited action | Present? |
|---|---|
| Force-push | **NO** — `df763bf9` intact |
| Modify frozen corpus | **NO** — `git status -- 00-SOURCE/ 99-FREEZE/ 00-CEP/ 00-CMG/` → **0 entries** |
| Duplicate existing capability | **NO** — 0 duplicate canonical objects |
| Skip `verify.sh` | **NO** — GREEN; CI invokes it directly |
| Self-authorize beyond scope | **NO** — the `platform/**` mutation is now authorized under P-7 via `WP-RO-001` |
| Remove committed artifacts | **NO** — 0 deletions, 0 renames |
| Rewrite history / squash unrelated work | **NO** — five commits preserve the concern boundaries |

**Secrets:** none. Reviewed all 42 untracked files and the 30 hand-authored modified files. No
`.env`, credential store, key material, or token.

---

## 7. DETERMINATION

> ### ✅ **COMMIT SEQUENCE READY — 0 OUTSTANDING PRECONDITIONS**
>
> **89 modified · 42 added · 57 generated · 0 removed · 0 staged.**
>
> Five commits, ordered by projection dependency (§4.1). A single commit is acceptable but less
> reversible.
>
> **`git add`: NOT performed. `git commit`: NOT performed. History: NOT rewritten.**
>
> The sequence discharges nine standing conditions including the repository's own registered
> **P0 suspensive** action `OA-1`, and makes the `RELEASED` lifecycle state reachable.

---

*END — `IMPLEMENT-001C` Deliverable 06 · AUTHORITY = NONE · `CERTIFIED-PROVISIONAL` · Tier T1 VACANT*
