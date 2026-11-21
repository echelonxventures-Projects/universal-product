# H-06 TASK-007 GP-4 DEAD FLAG REMOVAL PLAN

| Field | Value |
|---|---|
| **ID** | H-06-T007-GP4DFP |
| **Authority** | IMPLEMENTATION PLAN ONLY. No engine files modified. |
| **Phase** | Foundation Closure — Gate Purity Implementation — Task-007 |
| **Baseline** | HEAD `1f869865` · branch `integration/recovery-001` |
| **Depends on** | H-06-TASK-003-PROGRAMME-MODE-CLASSIFICATION-REPORT.md (GP-4 findings) |
| **Produced** | 2026-08-16 |
| **Status** | PLAN COMPLETE — NO ENGINE MODIFIED |

---

## 1. Defect Definition

**GP-4: Dead Flag** — A CLI flag is registered in the argument parser but its value
is never read after parsing. The flag has no effect on engine behaviour. Its presence
is misleading: it suggests a code path exists (e.g. a render/replay path) when none
does. Callers who pass the flag receive no error but the flag is silently ignored.

Three engines have a dead `--render` flag that was evidently intended as a replay or
render-only path. Because the flag is never acted upon, it provides no replay contract
and cannot serve as the `replay_path` for a PRODUCER declaration.

The fix is to either:
- **Remove** the flag entirely (if no caller relies on it and no code path is intended), or
- **Implement** the flag (convert it to a functioning `--replay` flag per Task-005 spec)

This task chooses **implement** — converting `--render` to a working `--replay` contract
is the most direct path and avoids breaking any caller that may be passing `--render`
(even if it has no effect today, removing it introduces a parser error for that caller).

---

## 2. Affected Programmes

| Programme | Engine | Dead Flag Line | Flag Name | Declaration Dependency |
|---|---|---|---|---|
| UCL-000001 | `ucl_engine.py` | `:2983` | `--render` | Task-005 UCL replay blocked on this |
| UCOS-UFEP-001 | `ufep_engine.py` | `:1082` | `--render` | Task-005 UFEP replay blocked on this |
| UIS-001 | `uis_engine.py` | `:1777` | `--render` | Task-005 UIS replay blocked on this |

---

## 3. Fix Specification

### 3.1 Option Analysis

| Option | Description | Risk | Selected |
|---|---|---|---|
| Remove `--render` | Delete the parser entry; no code change otherwise | Breaks any caller passing `--render` (parser error) | NO |
| Rename to `--replay` | Delete `--render` entry; add `--replay` per Task-005 spec | Same caller-break risk as remove | NO |
| Implement `--render` as replay | Add action body under `if args.render:` using Task-005 replay contract | No caller break; flag now does what it implies | **YES** |

**Selected approach:** Implement `--render` as a fully functional replay path per the
Task-005 PRODUCER replay contract. The declaration `replay_path` will then name
`--render` (or a Makefile target wrapping it), and the flag becomes live, not dead.

Rationale: converting a dead flag to a working one is a strictly additive change —
existing `--gate` behaviour is unchanged, and callers using `--render` gain a working
path rather than receiving a breaking change.

### 3.2 Universal Implementation Pattern

```python
# In each engine's main() or cmd_gate():
# BEFORE (dead flag — registered but never read):
parser.add_argument("--render", action="store_true")
# ... remainder of function never checks args.render

# AFTER (live replay flag — registered and acted upon):
parser.add_argument("--render", action="store_true",
    help="Regenerate outputs in memory; compare committed bytes; exit 0 on match, 1 on diff")

# in main() or cmd_gate(), after parse_args():
if args.render:
    model = build(args)                      # regenerate without writing
    diffs = compare_to_disk(model)           # byte-compare each output
    if diffs:
        for path, detail in diffs.items():
            print(f"REPLAY DIFF: {path}: {detail}", file=sys.stderr)
        sys.exit(1)
    sys.exit(0)
```

This is the exact Task-005 `--replay` contract, implemented under the existing
`--render` flag name. No parser entry is added; no parser entry is removed.

---

### 3.3 UCL-000001 Fix

**Engine:** `00-MASTER/UCL-000001/ucl_engine.py`

| Item | Detail |
|---|---|
| Dead flag registration | `:2983` `parser.add_argument("--render", ...)` |
| First read of `args.render` | Never (GP-4 confirmed) |
| Precondition read | `:2975-3050` to confirm: (a) flag registration; (b) confirmed never-read; (c) build function name; (d) output paths written by `:3030` |
| Implementation | Add `if args.render:` block in `cmd_gate()` after `args = parser.parse_args()` |
| Proposed `replay_path` | `make ucl-render` (wraps `ucl_engine.py --render`) |
| Makefile entry | `ucl-render: python 00-MASTER/UCL-000001/ucl_engine.py --render` |

**Fix commit message:**
```
H-06: Implement dead --render flag as replay contract in ucl_engine.py

Converts GP-4 dead flag at :2983 to functioning replay path.
--render now regenerates in memory, compares committed bytes, exits 0/1.
No change to --gate behaviour. Unblocks Task-005 UCL replay.

Evidence: H-06-TASK-003 GP-4 §2 ucl_engine.py:2983
Task: H-06-TASK-007
```

---

### 3.4 UCOS-UFEP-001 Fix

**Engine:** `00-MASTER/UCOS-UFEP-001/ufep_engine.py`

| Item | Detail |
|---|---|
| Dead flag registration | `:1082` |
| Precondition read | `:1070-1140` |
| Implementation | Add `if args.render:` block in gate handler after parse |
| Proposed `replay_path` | `make ufep-render` |
| Makefile entry | `ufep-render: python 00-MASTER/UCOS-UFEP-001/ufep_engine.py --render` |

**Fix commit message:**
```
H-06: Implement dead --render flag as replay contract in ufep_engine.py

Converts GP-4 dead flag at :1082 to functioning replay path.
Unblocks Task-005 UFEP replay contract.

Evidence: H-06-TASK-003 GP-4 §2 ufep_engine.py:1082
Task: H-06-TASK-007
```

---

### 3.5 UIS-001 Fix

**Engine:** `00-MASTER/UIS-001/uis_engine.py`

| Item | Detail |
|---|---|
| Dead flag registration | `:1777` |
| Precondition read | `:1765-1840` |
| Implementation | Add `if args.render:` block in gate handler after parse |
| Proposed `replay_path` | `make uis-render` |
| Makefile entry | `uis-render: python 00-MASTER/UIS-001/uis_engine.py --render` |

**Fix commit message:**
```
H-06: Implement dead --render flag as replay contract in uis_engine.py

Converts GP-4 dead flag at :1777 to functioning replay path.
Unblocks Task-005 UIS replay contract.

Evidence: H-06-TASK-003 GP-4 §2 uis_engine.py:1777
Task: H-06-TASK-007
```

---

## 4. Validation Sequence

### Gate VG-13: Flag is now live (no longer dead)

**Test procedure:**
1. Run `<engine> --render` on a clean working tree with committed outputs
2. Confirm: exits 0 (byte match)
3. Introduce a 1-byte synthetic diff to one output file
4. Run `<engine> --render` again
5. Confirm: exits 1, stderr shows diff path
6. Revert synthetic diff
7. Record exit codes as evidence

### Gate VG-11: `--gate` behaviour unchanged

Run `<engine> --gate` before and after the fix with identical inputs.
Confirm: output bytes are identical; exit code is identical.

### Gate VG-14: verify.sh still passes

```bash
bash verify.sh
```

---

## 5. Implementation Order

Each fix is committed independently.

| Order | Programme | Engine | Precondition Read Lines | Unblocks |
|---|---|---|---|---|
| 1 | UCL-000001 | `ucl_engine.py` | `:2975-3050` | Task-005 UCL replay + Task-004 ucl-declaration |
| 2 | UCOS-UFEP-001 | `ufep_engine.py` | `:1070-1140` | Task-005 UFEP replay + Task-004 ufep-declaration |
| 3 | UIS-001 | `uis_engine.py` | `:1765-1840` | Task-005 UIS replay + Task-004 uis-declaration |

---

## 6. Post-Task-007 Enablement

| Downstream | Enabled Action |
|---|---|
| Task-005 Tier 2 | UCL, UFEP, UIS replay contracts can be implemented and tested |
| Task-004 execution | `ucl-declaration.json`, `ufep-declaration.json`, `uis-declaration.json` can receive `gate_mode: PRODUCER` + `replay_path` |

---

## 7. Forbidden Actions

| Action | Status |
|---|---|
| Engine files modified | NONE |
| `--render` flag implemented | NONE |
| Makefile modified | NONE |
| Declaration files modified | NONE |
| Commits created | NONE |

---

*Task-007 GP-4 dead flag removal plan complete. Three engines have a dead `--render`
flag: `ucl_engine.py:2983`, `ufep_engine.py:1082`, `uis_engine.py:1777`. Fix converts
each dead flag to a functioning replay contract per Task-005 spec. Each fix is
independent and committed atomically with VG-13/11/14 validation evidence.*

---

Task-007 GP-4 dead flag implementation plan complete.
No engine mutation performed.
