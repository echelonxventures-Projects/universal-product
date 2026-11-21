# `WP-RO-001` — REPOSITORY-OPERATIONS GATE CORRECTION WORK PACKAGE

| Field | Value |
|---|---|
| WORK PACKAGE | `WP-RO-001` — Repository-Operations Gate Correction |
| MISSION | `IMPLEMENT-001C` — Approved Remediation Execution |
| BACKLOG ITEM | `RB-02` (`IMPLEMENT-001B` Deliverable 06) |
| DISCHARGES | finding `C-1d` · the valid residue of finding `C-4` · conflicts `CF-04`, `CF-06` |
| AUTHORITY | `NONE — DERIVED TRUTH.` This record authorizes nothing new; it supplies the work-package precondition that **P-7** already requires. |
| ROUTE | **P-7** — corrective mutation of a freeze-gated surface (`00-MASTER/UCCEP-000006/06-IMPLEMENTATION-BOUNDARY-SPECIFICATION.md:27`) |
| PRECEDENT | `WP-UCCEP-003` — the P-7 precedent named in the rule itself |
| HOME | `00-MASTER/IMPLEMENT-001C/` under **P-5** (*"Programme-owned outputs … own directory only"*) |
| BASELINE | `UCOS-BASELINE-001` · `df763bf917943321886c3fc973eac4a1569b6183` · branch `integration/recovery-001` |
| DISCLOSURE | `CERTIFIED-PROVISIONAL`; Tier T1 VACANT |

> **Why this record exists.** `X-8` permits mutation of `platform/**` *"except under **P-7**"*.
> P-7's second and third conditions were already met by the change set; its **first** —
> *"only under an existing work package"* — was not. This is that work package. It adds no
> code and changes no behaviour.

---

## 1. NAMING — and why not `EIP-018`

The change set's 8 comment lines attribute themselves to `EIP-018 (FP-2/3/7/8/13/14)`.
`EIP-018` **already denotes** the USIS establishment mission
(`00-MASTER/UCOS-USIS-001/00-USIS-PROGRAM-ESTABLISHMENT-DETERMINATION.md:7`) and is already
cited for that mission in committed code (`00-BOOK/tools/config.py:69, :265, :787`). One token
for two unrelated subject matters is `NF-4` in spirit (`00-MASTER/IMR-0000/06-CIOS-NAMESPACE-FRAMEWORK.md`).

This work package therefore takes the token **`WP-RO-001`** and its finding register the
prefix **`RO-F-NN`**. Both are `T-M` (mission-local) identifiers under `NF-3`: *"A T-M family
is created by declaring it in a mission artifact and stating its cardinality. It requires no
admission, because it claims no identity."* Neither is presented to `REG-AUTO-001` and neither
enters `id-ledger.json`, per `NF-1`. **Cardinality: `RO-F-01` … `RO-F-06`, closed at 6.**

The existing `EIP-018 (FP-N)` comments are **retained, not deleted** — `GOV-002` §6 / `RA5`
(`02-MASTER/UCOS-GOV-002-…-DETERMINATION.md:64, :245`) treat code-borne identifiers as
traceability evidence to preserve, so removal would be a regression. The mapping in §3 binds
them to this register.

---

## 2. DECLARED ADDITIVE SURFACES

Mutation is confined to these 7 paths. Nothing else under `platform/**` or `engine/**` is touched.

| # | Path | Change |
|---|---|---|
| 1 | `platform/repository_operations/engine.py` | +1 line — pass `measured_coverage=coverage` into `execute_stage` |
| 2 | `platform/repository_operations/stages.py` | +129/−10 — measured-coverage projection, fail-closed acceptance override, git-derived freeze subject, empty-subject rejection |
| 3 | `platform/tests/test_repository_operations_stages.py` | +101/−3 — negative-path tests (the P-7 condition-(iii) evidence) |
| 4 | `platform/tests/test_repository_operations_cli.py` | fixture: `paths: []` → `["engine/a.py"]` |
| 5 | `platform/tests/test_repository_operations_engine.py` | same fixture change |
| 6 | `platform/tests/test_repository_operations_service.py` | same fixture change |
| 7 | `repo-operations.json` | declaration: `coverage_from_measurement: true`, `subject: "working-tree"` |

`repo-operations.json` is at the repository root, outside `X-8`; it is listed for completeness
because it is the declaration the mutated code reads.

---

## 3. THE LOCATED GATE DEFECTS — `RO-F-01` … `RO-F-06`

Each was a gate that **could not fail**. Each is evidenced from the committed `HEAD`
(`df763bf9`), not asserted.

| Id | Legacy citation | Defective gate | Evidence at HEAD | Correction |
|---|---|---|---|---|
| **`RO-F-01`** | `EIP-018 (FP-13)` | `repository-acceptance` declared its own coverage 100% by fiat | `git show HEAD:repo-operations.json:64-71` — six dimensions, each `{"covered": 1, "total": 1}`. `CoverageProfile.complete` was `True` by assertion, never by measurement. | `stages.py:99-118` projects the **measured** report; unmeasurable dimensions are deliberately not synthesised. `stages.py:121-139` raises `StageExecutionError` if a measurement is absent — no silent fallback to self-declaration. |
| **`RO-F-02`** | `EIP-018 (FP-14)` | `architecture-freeze` guarded an **empty subject** | `git show HEAD:repo-operations.json:23` — `"params": { "paths": [] }`. `find_frozen_writes([])` returns `[]`, so the stage passed having examined nothing. | `stages.py:210-283` derives the write set from git (`subject: "working-tree"`), validates the subject source against `FREEZE_SUBJECT_SOURCES`, and rejects an empty declared subject fail-closed. |
| **`RO-F-03`** | `EIP-018 (FP-7)` | CI DP-03 guard **failed open** on unresolved diff base | `ec1-ci.yml` at HEAD: `echo "No resolvable base ref; skipping diff-based guard (no-op)."` and reported SUCCESS — the normal case for a first push to a new branch (`github.event.before` is the all-zero SHA). | Ordered base-ref fallback chain; explicit `exit 1` when nothing resolves; no `\|\| true` on `git`. |
| **`RO-F-04`** | `EIP-018 (FP-8)` | CI re-implemented a **subset** of the canonical gate | `ec1-ci.yml` at HEAD ran `ruff check` + `pytest`, omitting `ruff format --check`, the coverage report, and `ukb.py enforce --pre`. *"verify.sh is green"* and *"CI is green"* were different predicates. | CI now invokes `./verify.sh` directly, making them one predicate by construction. |
| **`RO-F-05`** | `EIP-018 (FP-2)` | `uccep-gate` installed into the wrong environment | `uccep-gate.yml` at HEAD used `pip install -e ".[dev]"` where the engine requires the canonical venv. | `./bootstrap.sh` plus an explicit `test -x .ec1-venv/bin/python` assertion. |
| **`RO-F-06`** | `EIP-018 (FP-3)` | tier ceiling undisclosed | `uccep.json` at HEAD reported `CK-VERIFY`, `CK-DETERMINISM-BUILD`, `CK-REG-DRIFT` as **fabricated `PASS`** while never executing them. | Engine now emits `NOT-EXECUTED, in_scope=false`; `G-07` degrades to `PARTIAL`; `unproven` / `out_of_tier` / `gate_blocking` accounting added. Workflow tier note records it. |

`RO-F-05` and `RO-F-06` touch `.github/workflows/` and `00-MASTER/UCCEP-000000/`, both outside
`X-8`; they are registered here so the `FP-N` citations resolve completely.

---

## 4. P-7 CONDITION SATISFACTION

| P-7 condition | Status | Evidence |
|---|---|---|
| *a located owner's gate is defective* | ✓ **MET** | Six defects, §3, each evidenced from committed `HEAD` |
| **only under an existing work package** | ✓ **MET BY THIS RECORD** | `WP-RO-001` |
| *EC-1 `verify.sh` must pass* | ✓ **MET** | 5/5 stages, exit 0, coverage 94.28% — re-verified in `IMPLEMENT-001C` Phase 6 |
| *the corrected gate demonstrated **failing closed** on the negative path* | ✓ **MET** | `test_freeze_stage_empty_declared_subject_is_fail_closed` · `test_freeze_stage_unknown_subject_source` · measured-coverage-absent `StageExecutionError` test · plus the observed live `FAILED architecture-freeze` and `FAILED repository-acceptance` — the corrected gates are demonstrably capable of failing, which the originals were not |

> **All four P-7 conditions are now satisfied. The `platform/**` mutation is within the
> declared implementation boundary.**

---

## 5. CLASSIFICATION — `EVOLUTION-001` §2

| Surface group | Classification |
|---|---|
| `platform/repository_operations/**` + 4 test files + `repo-operations.json` | **Defect correction** — *"Fixing incorrect behaviour."* Two gates that could not fail now can. |
| `.github/workflows/{ec1-ci,uccep-gate}.yml` | **Defect correction** — fail-open → fail-closed |
| `00-BOOK/SCHEMAS/*.schema.json` ×13 + `00-BOOK/tools/config.py` | **Enhancement** — additive identifier-namespace widening; provably admits-only (0 previously-valid identifiers rejected) |
| `00-MASTER/UCCEP-000000/**`, `00-MASTER/UCDA-000001/**` | **Enhancement** — certification-integrity disclosure + architectural-coverage assimilation |
| `verify.sh`, `scripts/ucos-env.sh`, `.gitignore` | **Infrastructure** |
| `00-MASTER/{BASELINE,EVOLUTION,RELEASE,IMPLEMENT}-001*`, `CAEM-001`, `IMR-001`, `UCOS-{CIOA,CCE,UAR}-001` | **Documentation** / programme records |

This discharges the `CLASSIFIED` lifecycle state (`RELEASE-001` §1) for the change set, which
`IMPLEMENT-001B` Deliverable 08 recorded as `PARTIAL`.

---

## 6. VALIDATION

| Check | Result |
|---|---|
| `verify.sh` | **PASS** 5/5, exit 0 |
| `pytest platform/tests engine/tests` | **PASS**, coverage 94.28% ≥ 90% |
| Every declared surface exists on disk | **7/7** |
| Every `RO-F-NN` resolves to a located defect with HEAD evidence | **6/6** |
| Register cardinality closed | `RO-F-01…06`, **6** declared, **6** used |
| Legacy `EIP-018 (FP-N)` citations mapped | **8/8 lines · 6/6 ids** |
| `id-ledger.json` entries created | **0** |
| `artifacts.json` entries created | **0** |

---

## 7. DETERMINATION

> **`WP-RO-001` ESTABLISHED.** The `platform/**` corrective mutation is authorized under
> **P-7**, its finding register is declared and closed at 6, and every legacy `FP-N` citation
> in the change set now resolves.
>
> `RB-02` **DISCHARGED.** `C-1d` and the valid residue of `C-4` are closed. Conflicts `CF-04`
> and `CF-06` are resolved.

---

*END — `WP-RO-001` · `IMPLEMENT-001C` `RB-02` · AUTHORITY = NONE · `CERTIFIED-PROVISIONAL` · Tier T1 VACANT*
