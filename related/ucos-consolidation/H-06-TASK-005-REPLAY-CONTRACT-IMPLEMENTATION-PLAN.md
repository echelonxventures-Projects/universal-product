# H-06 TASK-005 REPLAY CONTRACT IMPLEMENTATION PLAN

| Field | Value |
|---|---|
| **ID** | H-06-T005-RCIP |
| **Authority** | IMPLEMENTATION PLAN ONLY. No engine files modified. No replay paths committed. |
| **Phase** | Foundation Closure — Gate Purity Implementation — Task-005 |
| **Baseline** | HEAD `1f869865` · branch `integration/recovery-001` |
| **Depends on** | H-06-TASK-004-DECLARATION-UPDATE-PREPARATION-PLAN.md |
| | H-06-TASK-003-PROGRAMME-MODE-CLASSIFICATION-REPORT.md |
| **Produced** | 2026-08-16 |
| **Status** | PLAN COMPLETE — NO REPLAY PATHS IMPLEMENTED |

---

## 1. Scope and Authority

A PRODUCER declaration is constitutionally incomplete without a tested `replay_path`.
This task defines the replay contract design for each PRODUCER programme, specifying:

1. The exact invocation that constitutes the replay path
2. The byte-comparison contract the replay must satisfy
3. The exit-code contract (0 on match; non-zero on any byte diff)
4. The implementation location (new subcommand, `--replay` flag, or Makefile target)
5. The test procedure to run before the declaration is committed

No engine file is modified in this document. Every replay path described below is
a proposed design. Actual implementation and testing occur in Task-005 execution.

---

## 2. Replay Contract Definition

### 2.1 Universal Contract (applies to all PRODUCER replay paths)

| Requirement | Specification |
|---|---|
| Invocation | Single command invocable from repository root |
| Behaviour | Regenerate all engine outputs **in memory only**; load committed bytes from disk; compare byte-for-byte |
| Exit 0 | Every regenerated output matches every committed byte |
| Exit non-zero | Any regenerated output differs from any committed byte |
| No write | Replay path MUST NOT write to any tracked or gitignored path |
| Idempotent | Same invocation from any clean state produces same exit code |
| Input scope | Same input data as the gate invocation; no synthetic injection |

The `replay_path` field in the declaration names the command that satisfies this
contract. The command must be stable — renaming it after declaration is committed
requires a co-update of the declaration.

### 2.2 Implementation Patterns

Three implementation patterns are available. The correct pattern is determined per
programme by existing engine structure:

| Pattern | Description | When to Use |
|---|---|---|
| `--replay` flag | Add `--replay` to the existing gate parser; branch on `args.replay` to regenerate in memory, compare, print diff summary, exit accordingly | Engines with a single `main()` and a clear `--gate` flag — most engines |
| `make <target>-replay` | Makefile target that invokes the engine with `--replay`; Makefile target is what the declaration `replay_path` names | Programmes already referenced via Makefile targets (UAUE precedent) |
| Dedicated `replay.py` | Separate script; imports engine internals; calls generator, compares bytes | Only when engine structure does not support flag-based dispatch cleanly |

**Preferred pattern: `--replay` flag**, then expose via `make <programme>-replay` for
declaration naming stability. UAUE is the existing precedent: `verify.sh:222` invokes
`python -m engine.uaue.gate --replay` — that pattern is already proven in this repo.

---

## 3. Per-Programme Replay Design

### 3.1 Tier 1 — No Blocking Dependency (implement first)

#### 3.1.1 BASELINE-001

| Field | Value |
|---|---|
| Engine | `00-MASTER/BASELINE-001/baseline_engine.py` |
| GP Evidence | GP-1 `:1896` `write_registers(model)` |
| Gate invocation | `baseline_engine.py --gate` |
| CI workflow | `baseline-gate.yml` has render+diff step — confirms deterministic shape |
| Output surface | 5 tracked files under `00-MASTER/BASELINE-001/` per CI workflow |
| Replay pattern | `--replay` flag → regenerate all 5 outputs in memory → load from disk → compare bytes |
| Proposed `replay_path` | `make baseline-replay` |
| Makefile target | `baseline-replay: python 00-MASTER/BASELINE-001/baseline_engine.py --replay` |
| Blocking | None |

**Replay implementation spec:**
```python
# baseline_engine.py  — add to argument parser:
parser.add_argument("--replay", action="store_true",
    help="Regenerate outputs in memory; compare committed bytes; exit 0 on match")

# in main():
if args.replay:
    model = build(mint=False)       # regenerate without writing
    diffs = compare_to_disk(model)  # load committed bytes, byte-compare each output
    if diffs:
        for path, detail in diffs.items():
            print(f"REPLAY DIFF: {path}: {detail}", file=sys.stderr)
        sys.exit(1)
    sys.exit(0)
```

`compare_to_disk(model)` loads each file that `write_registers` would write, compares
bytes, returns `{}` on exact match or `{path: "byte N differs"}` on any mismatch.
The implementation must produce the same outputs as `--gate` does today without calling
any write function.

**Validation procedure:**
1. Run `make baseline-replay` on clean committed state → confirm exit 0
2. Introduce a 1-byte change to one output file → run again → confirm exit 1, stderr shows diff
3. Revert synthetic change → confirm exit 0 again
4. Record exit codes as evidence in declaration commit message

---

#### 3.1.2 UCOS-URAT-001

| Field | Value |
|---|---|
| Engine | `00-MASTER/UCOS-URAT-001/urat_engine.py` |
| GP Evidence | GP-1 `:1009` |
| Gate invocation | `urat_engine.py --gate` |
| Output surface | `00-MASTER/UCOS-URAT-001/` register surface |
| Replay pattern | `--replay` flag |
| Proposed `replay_path` | `make urat-replay` |
| Blocking | None |

**Replay implementation spec:** Same pattern as BASELINE-001. Identify all paths
written by `write_registers` (or equivalent) at `:1009`; regenerate in memory;
byte-compare; exit 0 on match, exit 1 on diff.

---

#### 3.1.3 UCOS-UTCE-001

| Field | Value |
|---|---|
| Engine | `00-MASTER/UCOS-UTCE-001/utce_engine.py` |
| GP Evidence | GP-1 `:855`; GP-8 misleading `--check-read-only` self-guard |
| Gate invocation | `utce_engine.py --gate` |
| Output surface | `00-MASTER/UCOS-UTCE-001/` register surface |
| Replay pattern | `--replay` flag |
| Proposed `replay_path` | `make utce-replay` |
| Blocking | None |
| Note | GP-8: The `--check-read-only` flag creates a false impression of an existing replay path. Confirm at implementation time that `--check-read-only` does NOT satisfy the byte-compare contract. If it does, reuse it; if not, add `--replay`. |

**GP-8 clarification required before implementation:**
Read `utce_engine.py` around `:855` to determine:
- Does `--check-read-only` regenerate in memory and compare bytes?
- Does it exit non-zero on byte difference?
- If YES to both → `--check-read-only` IS the replay path; name it in the declaration.
- If NO → add `--replay` per standard pattern.

---

#### 3.1.4 ACEE-000001

| Field | Value |
|---|---|
| Engine | `00-MASTER/ACEE-000001/acee_engine.py` |
| GP Evidence | GP-1 `:3730` |
| Gate invocation | `acee_engine.py --gate` |
| Output surface | `00-MASTER/ACEE-000001/` register surface |
| Replay pattern | `--replay` flag |
| Proposed `replay_path` | `make acee-replay` |
| Blocking | None |

---

### 3.2 Tier 2 — Blocked by Task-007 (GP-4 Dead Flag)

#### 3.2.1 UCL-000001

| Field | Value |
|---|---|
| Engine | `00-MASTER/UCL-000001/ucl_engine.py` |
| GP Evidence | GP-1 `:3030`; GP-4 `:2983` dead `--render` flag (never read after parse) |
| Gate invocation | `ucl_engine.py --gate` |
| Output surface | `00-MASTER/UCL-000001/` register surface |
| GP-4 impact | `--render` was presumably intended as the replay/render path but is never read. Any attempt to implement `--replay` must first remove or repair the dead `--render` flag (Task-007). |
| Proposed `replay_path` | `make ucl-replay` (after Task-007 removes `--render` or converts it) |
| Blocking | Task-007 GP-4 fix must complete before replay path can be validly designed and tested |

**Task-007 prerequisite for UCL replay:**
Option A (preferred): Remove `--render` at `:2983` entirely; add `--replay` per standard pattern.
Option B: Repurpose `--render` as the replay flag if the naming is recoverable. Requires
confirming the flag is truly never read (confirmed GP-4 finding) and that no external caller
relies on it.

---

#### 3.2.2 UCOS-UFEP-001

| Field | Value |
|---|---|
| Engine | `00-MASTER/UCOS-UFEP-001/ufep_engine.py` |
| GP Evidence | GP-1 `:1119`; GP-4 `:1082` dead `--render` flag |
| Proposed `replay_path` | `make ufep-replay` (after Task-007) |
| Blocking | Task-007 |

---

#### 3.2.3 UIS-001

| Field | Value |
|---|---|
| Engine | `00-MASTER/UIS-001/uis_engine.py` |
| GP Evidence | GP-1 `:1814`; GP-4 `:1777` dead `--render` flag |
| Proposed `replay_path` | `make uis-replay` (after Task-007) |
| Blocking | Task-007 |

---

### 3.3 Tier 3 — Blocked by Task-006 (GP-2 Write-Before-Verdict)

#### 3.3.1 UCOS-RIB-001

| Field | Value |
|---|---|
| Engine | `00-MASTER/UCOS-RIB-001/rib_engine.py` |
| GP Evidence | GP-2 `:3925` write before `:3942` gate branch |
| Write-order defect | Write happens unconditionally; gate branch at `:3942` is never reached to prevent it |
| Task-006 fix | Move write call to inside the `if not args.gate:` block at `:3942` |
| Replay pattern | After Task-006: `--replay` flag |
| Proposed `replay_path` | `make rib-replay` (after Task-006 + Task-007 if GP-4 present) |
| Blocking | Task-006 must complete first; declare PRODUCER only after write-order is correct |

**Replay design note for GP-2 engines:**
The write-before-verdict defect means the current `--gate` path ALWAYS writes,
regardless of gate outcome. The replay path cannot be implemented without first fixing
the write-order (Task-006), because a correct replay path requires the ability to
call the generation logic without triggering the write path — which is impossible
while the write is unconditional.

---

#### 3.3.2 URRC-000001

| Field | Value |
|---|---|
| Engine | `00-MASTER/URRC-000001/urrc_engine.py` |
| GP Evidence | GP-2 `:2041` write before `:2056` gate branch |
| Proposed `replay_path` | `make urrc-replay` (after Task-006) |
| Blocking | Task-006 |

---

#### 3.3.3 UCOS-UAR-001

| Field | Value |
|---|---|
| Engine | `00-MASTER/UCOS-UAR-001/uar_engine.py` |
| GP Evidence | GP-2 `:118-125` write inside `_run_gate()` |
| Proposed `replay_path` | `make uar-replay` (after Task-006) |
| Blocking | Task-006 |
| Note | `main()` routes both `--gate` and bare invocation to `_run_gate()` — fix must ensure replay path is reachable without the unconditional write. |

---

### 3.4 Tier 4 — Blocked by Task-009 (GP-10 AEE Tier Guard)

#### 3.4.1 UCOS-AEE-001

| Field | Value |
|---|---|
| Engine | `00-MASTER/UCOS-AEE-001/aee_engine.py` |
| GP Evidence | GP-1 `:1807` `emit(decl, model)` unconditional; GP-10 APPARENT |
| Task-009 prerequisite | Read `emit()` body to confirm whether tier guard exists. If `emit()` contains an internal check that suppresses output on the `aee-observe` path, the `aee-gate` path is still PRODUCER. If no tier guard exists in `emit()`, then both `aee-gate` and `aee-observe` write tracked files — both PRODUCER. |
| Replay target | `aee-gate` path: `make aee-replay` |
| Blocking | Task-009 clarification of `emit()` tier guard before designing replay; a replay that covers the wrong tier is invalid evidence |

---

## 4. Makefile Target Inventory

Proposed Makefile entries for all PRODUCER replay paths. All entries follow the
pattern confirmed by UAUE precedent in `verify.sh:222`.

```makefile
# H-06: PRODUCER replay targets
# Each target: regenerate in memory, compare committed bytes, exit 0/1

baseline-replay:
	python 00-MASTER/BASELINE-001/baseline_engine.py --replay

urat-replay:
	python 00-MASTER/UCOS-URAT-001/urat_engine.py --replay

utce-replay:
	python 00-MASTER/UCOS-UTCE-001/utce_engine.py --replay

acee-replay:
	python 00-MASTER/ACEE-000001/acee_engine.py --replay

# After Task-007 (GP-4 fix):
ucl-replay:
	python 00-MASTER/UCL-000001/ucl_engine.py --replay

ufep-replay:
	python 00-MASTER/UCOS-UFEP-001/ufep_engine.py --replay

uis-replay:
	python 00-MASTER/UIS-001/uis_engine.py --replay

# After Task-006 (GP-2 fix):
rib-replay:
	python 00-MASTER/UCOS-RIB-001/rib_engine.py --replay

urrc-replay:
	python 00-MASTER/URRC-000001/urrc_engine.py --replay

uar-replay:
	python 00-MASTER/UCOS-UAR-001/uar_engine.py --replay

# After Task-009 (GP-10 fix):
aee-replay:
	python 00-MASTER/UCOS-AEE-001/aee_engine.py --gate --replay
```

---

## 5. Implementation Sequence

Each replay path must be implemented, tested, and committed independently.
The commit for a replay path co-commits the `replay_path` field in the
corresponding declaration (Task-004 execution). They are a single atomic commit.

| Step | Order | Programme | Blocking | Co-committed declaration |
|---|---|---|---|---|
| 1 | First | BASELINE-001 | None | `baseline-declaration.json` + `gate_mode: PRODUCER` + `replay_path: make baseline-replay` |
| 2 | Second | UCOS-URAT-001 | None | `urat-declaration.json` |
| 3 | Third | UCOS-UTCE-001 | GP-8 clarification only | `utce-declaration.json` |
| 4 | Fourth | ACEE-000001 | None | `acee-declaration.json` |
| 5 | After Task-007 | UCL-000001 | Task-007 complete | `ucl-declaration.json` |
| 6 | After Task-007 | UCOS-UFEP-001 | Task-007 complete | `ufep-declaration.json` |
| 7 | After Task-007 | UIS-001 | Task-007 complete | `uis-declaration.json` |
| 8 | After Task-006 | UCOS-RIB-001 | Task-006 complete | pending declaration location |
| 9 | After Task-006 | URRC-000001 | Task-006 complete | pending declaration location |
| 10 | After Task-006 | UCOS-UAR-001 | Task-006 complete | pending declaration location |
| 11 | After Task-009 | UCOS-AEE-001 | Task-009 complete | `aee-declaration.json` |

---

## 6. Validation Matrix

Each implemented replay path must satisfy all gates before the co-committed
declaration is pushed:

| Gate | Description | Tool |
|---|---|---|
| VG-8 | `make <programme>-replay` exits 0 on current committed state | `echo $?` after replay invocation |
| VG-9 | `make <programme>-replay` exits 1 after 1-byte modification to any output file | Introduce synthetic diff; run; confirm exit 1; revert |
| VG-7 | Declared `gate_mode` value matches Task-003 measurement | Cross-check Task-003 §2 table |
| VG-14 | `bash verify.sh` all prior-passing stages still pass after commit | verify.sh run (full) |
| VG-15 | Declaration now contains both `gate_mode: PRODUCER` and `replay_path` | `python3 -c "import json; d=json.load(open(f)); assert d['programme']['gate_mode']=='PRODUCER'"` |

---

## 7. Precondition Read Required Before Each Implementation

Before implementing each engine's `--replay` flag, read the engine to confirm:

1. Location of all write calls on the `--gate` path (to know what outputs to regenerate)
2. The build/compute function(s) that produce the outputs (to call without writing)
3. Any existing `--replay` or `--render` flag that might conflict or be reusable
4. The output paths written by `write_registers` or equivalent

This read is a gate on starting implementation, not on writing this plan.

---

## 8. Forbidden Actions

| Action | Status |
|---|---|
| Engine files modified in this task | NONE |
| `--replay` flags added to any engine | NONE |
| Makefile modified | NONE |
| Declaration files modified | NONE |
| Replay paths tested | NONE |
| Commits created | NONE |

This document is a design and implementation plan only. Every proposed change
is in future tense. No file in the repository was modified during its production.

---

*This document is the Task-005 replay contract implementation plan. It defines the
replay contract design for all PRODUCER programmes, their blocking dependencies,
and the per-engine implementation specifications. Tier 1 implementations (BASELINE,
URAT, UTCE, ACEE) are ready to proceed. Tiers 2–4 are blocked pending Tasks 007,
006, and 009 respectively.*

---

Task-005 replay contract implementation plan complete.
No engine or declaration mutation performed.
Implementation changes not executed.
