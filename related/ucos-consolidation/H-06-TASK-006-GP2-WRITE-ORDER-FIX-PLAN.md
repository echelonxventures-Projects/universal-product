# H-06 TASK-006 GP-2 WRITE-ORDER FIX PLAN

| Field | Value |
|---|---|
| **ID** | H-06-T006-GP2WOP |
| **Authority** | IMPLEMENTATION PLAN ONLY. No engine files modified. |
| **Phase** | Foundation Closure — Gate Purity Implementation — Task-006 |
| **Baseline** | HEAD `1f869865` · branch `integration/recovery-001` |
| **Depends on** | H-06-TASK-003-PROGRAMME-MODE-CLASSIFICATION-REPORT.md (GP-2 findings) |
| **Produced** | 2026-08-16 |
| **Status** | PLAN COMPLETE — NO ENGINE MODIFIED |

---

## 1. Defect Definition

**GP-2: Write Before Verdict** — The engine writes tracked output files unconditionally
before evaluating the gate outcome. The gate branch (the conditional block that decides
pass/fail) exists at a later line but is never reached because the write has already
occurred. This means every `--gate` invocation produces a tracked write, regardless of
whether the gate passed or failed, violating the PRODUCER invariant that writes are
controlled outputs subject to gate verdict.

A PRODUCER programme may write on a passing gate. It must not write on a failing gate.
An engine with GP-2 always writes; therefore it cannot be declared PRODUCER until the
write-order defect is corrected.

---

## 2. Affected Programmes

| Programme | Engine | Write Line | Gate Branch Line | Write-Order Status |
|---|---|---|---|---|
| UCOS-RIB-001 | `rib_engine.py` | `:3925` | `:3942` | Write precedes gate branch by 17 lines |
| URRC-000001 | `urrc_engine.py` | `:2041` | `:2056` | Write precedes gate branch by 15 lines |
| UCOS-UAR-001 | `uar_engine.py` | `:118-125` (inside `_run_gate()`) | main() gate dispatch | Write inside helper called unconditionally |

---

## 3. Fix Specification

### 3.1 Universal Fix Pattern

The fix for GP-2 is structurally identical across all three engines:

**Before (defective pattern):**
```python
def cmd_gate(args):
    model = build(args)
    write_registers(model)          # GP-2: unconditional write
    verdict = evaluate_gate(model)
    if not verdict.passed:
        sys.exit(1)
    # write already happened regardless of verdict
```

**After (corrected pattern):**
```python
def cmd_gate(args):
    model = build(args)
    verdict = evaluate_gate(model)
    if not verdict.passed:
        sys.exit(1)                 # exit before any write
    write_registers(model)          # write only on passing gate
```

The fix is a line-order change: move the write call to after the verdict check.
No logic is changed. No output format is changed. The write still occurs on pass;
it is suppressed on fail.

---

### 3.2 UCOS-RIB-001 Fix

**Engine:** `00-MASTER/UCOS-RIB-001/rib_engine.py`

| Item | Detail |
|---|---|
| Write call | `:3925` — `write_registers(model)` or equivalent |
| Gate branch | `:3942` — `if not verdict.passed: sys.exit(1)` or equivalent |
| Gap | 17 lines; write call is between build and gate evaluation |
| Fix | Move write call from `:3925` to after `:3942` verdict check |
| Precondition read | Read `:3910-3960` to confirm exact function names before moving |

**Pre-fix read required:**
```
Read rib_engine.py lines 3910-3960
Confirm: (a) write function name at :3925; (b) verdict check at :3942;
         (c) no intermediate step between write and verdict that depends on write output
```

**Fix commit message:**
```
H-06: Fix GP-2 write-order in rib_engine.py (gate write after verdict)

Move write_registers() call from before gate verdict to after.
Gate now exits non-zero before writing on fail.
No output format or logic change.

Evidence: H-06-TASK-003 GP-2 §2 rib_engine.py:3925,3942
Task: H-06-TASK-006
```

---

### 3.3 URRC-000001 Fix

**Engine:** `00-MASTER/URRC-000001/urrc_engine.py`

| Item | Detail |
|---|---|
| Write call | `:2041` |
| Gate branch | `:2056` |
| Gap | 15 lines |
| Fix | Move write call to after `:2056` verdict check |
| Precondition read | Read `:2025-2070` |

**Fix commit message:**
```
H-06: Fix GP-2 write-order in urrc_engine.py (gate write after verdict)

Move write call from :2041 to after gate verdict at :2056.
Gate exits non-zero before write on fail.

Evidence: H-06-TASK-003 GP-2 §2 urrc_engine.py:2041,2056
Task: H-06-TASK-006
```

---

### 3.4 UCOS-UAR-001 Fix

**Engine:** `00-MASTER/UCOS-UAR-001/uar_engine.py`

| Item | Detail |
|---|---|
| Write location | `:118-125` inside `_run_gate()` helper |
| Dispatch | `main()` calls `_run_gate()` for both `--gate` and bare invocation |
| Structural issue | Write is inside `_run_gate()` which is invoked before any gate verdict; split required |
| Fix options | Option A: Split `_run_gate()` into build+evaluate + write; call write only after verdict. Option B: Pass `gate_mode` flag into `_run_gate()`; suppress write when `gate_mode=True` and verdict fails. |
| Preferred fix | Option A — cleaner separation; no flag threading |

**Option A implementation:**
```python
# Before:
def _run_gate(args):
    model = build(args)
    write_output(model)          # :118-125 — unconditional
    verdict = evaluate(model)
    return verdict

def main():
    args = parse()
    _run_gate(args)

# After:
def _build_model(args):
    return build(args)

def _run_gate(args):
    model = _build_model(args)
    verdict = evaluate(model)
    if verdict.passed:
        write_output(model)      # write only on pass
    return verdict

def main():
    args = parse()
    _run_gate(args)
```

**Precondition read:** Read `:100-145` to confirm `_run_gate()` structure, exact
write function name, and whether `main()` uses the return value of `_run_gate()`.

**Fix commit message:**
```
H-06: Fix GP-2 write-order in uar_engine.py (_run_gate write after verdict)

Move write_output() call inside _run_gate() to after gate verdict.
Gate path no longer writes on fail.

Evidence: H-06-TASK-003 GP-2 §2 uar_engine.py:118-125
Task: H-06-TASK-006
```

---

## 4. Validation Sequence

Each fix is committed independently and must pass all validation gates:

### Gate VG-10: No write on failing gate

**Test procedure (per engine):**
1. Identify at least one input that produces a gate-fail verdict
2. Run `<engine> --gate` with that input on a clean working tree
3. Confirm: no tracked file is modified (`git diff --exit-code` exits 0)
4. Record as evidence in commit message

### Gate VG-11: Write still occurs on passing gate

**Test procedure (per engine):**
1. Run `<engine> --gate` with a known-passing input on a clean working tree
2. Confirm: expected output files are written (`git diff --name-only` lists them)
3. This confirms the fix did not suppress all writes

### Gate VG-12: Output unchanged for passing case

**Test procedure:**
1. Run `<engine> --gate` pre-fix → capture output bytes
2. Apply fix, run again → capture output bytes
3. Confirm: bytes are identical for the passing case

### Gate VG-14: verify.sh still passes

```bash
bash verify.sh
```
All stages passing before the fix must still pass after.

---

## 5. Implementation Order

GP-2 fixes are independent of each other and may be implemented in parallel,
but each fix must be committed separately with its own validation evidence.

| Order | Programme | Engine | Precondition Read | Test Input Source |
|---|---|---|---|---|
| 1 | UCOS-RIB-001 | `rib_engine.py` | `:3910-3960` | Existing test fixtures or CI inputs |
| 2 | URRC-000001 | `urrc_engine.py` | `:2025-2070` | Existing test fixtures or CI inputs |
| 3 | UCOS-UAR-001 | `uar_engine.py` | `:100-145` | Existing test fixtures or CI inputs |

After all three are committed and verified, Task-005 Tier 3 replay contracts
(RIB, URRC, UAR) become unblocked.

---

## 6. Post-Task-006 Enablement

Completing Task-006 unblocks the following downstream tasks:

| Downstream | Enabled Action |
|---|---|
| Task-005 Tier 3 | Replay contract implementation for RIB, URRC, UAR |
| Task-004 execution (partial) | `rib-declaration.json`, `urrc-declaration.json`, `uar-declaration.json` can receive `gate_mode: PRODUCER` once declaration files are located |

---

## 7. Forbidden Actions

| Action | Status |
|---|---|
| Engine files modified in this task | NONE |
| Write-order changes applied | NONE |
| Tests run | NONE |
| Commits created | NONE |

This document is an implementation plan only. No repository file was modified
during its production.

---

*Task-006 GP-2 write-order fix plan complete. Three engines require line-order
correction: `rib_engine.py:3925→after:3942`, `urrc_engine.py:2041→after:2056`,
`uar_engine.py:118-125→inside _run_gate() after verdict`. Each fix is independent,
atomic, and validated by VG-10/11/12/14 before the next proceeds.*

---

Task-006 GP-2 write-order fix plan complete.
No engine mutation performed.
Implementation changes not executed.
