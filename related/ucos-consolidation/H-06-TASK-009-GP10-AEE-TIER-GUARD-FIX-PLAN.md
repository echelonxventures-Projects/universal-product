# H-06 TASK-009 GP-10 AEE TIER GUARD FIX PLAN

| Field | Value |
|---|---|
| **ID** | H-06-T009-GP10ATGP |
| **Authority** | IMPLEMENTATION PLAN ONLY. No engine files modified. |
| **Phase** | Foundation Closure — Gate Purity Implementation — Task-009 |
| **Baseline** | HEAD `1f869865` · branch `integration/recovery-001` |
| **Depends on** | H-06-TASK-003-PROGRAMME-MODE-CLASSIFICATION-REPORT.md (GP-10 finding) |
| **Produced** | 2026-08-16 |
| **Status** | PLAN COMPLETE — NO ENGINE MODIFIED |

---

## 1. Defect Definition

**GP-10: Apparent Tier Guard** — `aee_engine.py:1807` calls `emit(decl, model)`
unconditionally on the gate path. The name `aee-gate` vs `aee-observe` suggests a
two-tier design where `aee-observe` should produce no tracked writes and `aee-gate`
should produce writes as a PRODUCER. However, the `emit()` function body has not been
confirmed to contain an internal tier check that suppresses writes on the `aee-observe`
path.

Until `emit()` is read and the tier check confirmed, the classification of
UCOS-AEE-001 remains provisional:

| Scenario | `emit()` Internal State | Correct Mode | Declaration Action |
|---|---|---|---|
| A | `emit()` checks calling tier; suppresses write on `aee-observe` | `aee-gate`: PRODUCER; `aee-observe`: OBSERVE | Separate declarations per tier, or single declaration with tier field |
| B | `emit()` writes unconditionally regardless of tier | Both tiers: PRODUCER | Single PRODUCER declaration; `aee-observe` name is misleading |
| C | `emit()` suppresses ALL writes (reads only) | Both tiers: OBSERVE | Single OBSERVE declaration |

GP-10 was filed as "apparent" because the tier guard may or may not exist.
This task resolves the ambiguity by reading `emit()` and specifying the fix.

---

## 2. Pre-Fix Read Requirement

Before any fix can be specified, read `aee_engine.py` to confirm:

```
Read aee_engine.py: locate emit() definition (referenced at :1807)
Questions to answer:
  1. Does emit() accept a tier or mode parameter?
  2. Does emit() inspect a global or context flag for current invocation mode?
  3. Does emit() call write() / open() / json.dump() unconditionally?
  4. Are there any conditional branches inside emit() that suppress writes?
  5. What are the tracked output paths written by emit()?
  6. Is there a separate aee-observe entry point; if so, does it call emit()?
```

The answer to these questions determines which scenario (A, B, or C) applies
and which fix path below is executed.

---

## 3. Fix Specification by Scenario

### 3.1 Scenario A — emit() Has Internal Tier Guard

**Condition:** `emit()` checks a tier flag and suppresses writes when called on
the `aee-observe` path.

**Finding:** GP-10 is a false alarm. The tier guard already exists. No fix required.

**Action:**
- Close GP-10 as resolved
- Document the tier guard evidence in the Task-009 closure note
- `aee-gate` path: PRODUCER — proceed to Task-005 Tier 4 replay implementation
- `aee-observe` path: OBSERVE — confirm declaration separately
- Task-004 §4.9: `aee-declaration.json` receives `gate_mode: PRODUCER` for the `aee-gate` tier
- Blocking on Task-009 is lifted immediately

---

### 3.2 Scenario B — emit() Writes Unconditionally

**Condition:** `emit()` has no tier check; writes tracked files regardless of
which tier invoked it.

**Finding:** GP-10 confirmed. Both `aee-gate` and `aee-observe` are PRODUCER.
The name `aee-observe` is misleading — this is a naming defect, not a behaviour defect.

**Fix options:**

| Option | Description | Selected |
|---|---|---|
| B1 | Add tier guard inside `emit()`: accept a `write` boolean param; pass `write=True` from `aee-gate`, `write=False` from `aee-observe` | **YES** — minimal, explicit |
| B2 | Rename `aee-observe` to `aee-replay` and convert it to the replay contract | NO — changes CLI surface |
| B3 | Leave both as PRODUCER; document `aee-observe` name as legacy | NO — misleading classification |

**Option B1 implementation:**

```python
# aee_engine.py — in emit():
def emit(decl, model, write=True):
    result = generate(decl, model)          # always generate in memory
    if not write:
        return result                        # aee-observe path: no write
    # existing write logic follows unchanged
    dump_to_tracked_paths(result)
    return result

# In cmd_aee_gate():
emit(decl, model, write=True)               # PRODUCER: writes on gate

# In cmd_aee_observe() (if it calls emit):
emit(decl, model, write=False)              # OBSERVE: generates but does not write
```

**Declaration outcome:**
- `aee-gate` path: `gate_mode: PRODUCER` + replay path (Task-005 Tier 4)
- `aee-observe` path: `gate_mode: OBSERVE` — now confirmed, not just asserted

**Fix commit message:**
```
H-06: Fix GP-10 tier guard in aee_engine.py (emit write param)

Add write=True/False parameter to emit().
aee-observe path passes write=False; no tracked write occurs.
aee-gate path passes write=True; PRODUCER behaviour unchanged.

Evidence: H-06-TASK-003 GP-10 §2 aee_engine.py:1807
Task: H-06-TASK-009
```

---

### 3.3 Scenario C — emit() Suppresses All Writes

**Condition:** `emit()` never writes tracked files; writes only to gitignored or
in-memory paths.

**Finding:** GP-10 misclassification. `aee_engine.py` is OBSERVE (or
OBSERVE_WITH_DECLARED_AUDIT_EMISSION if emit writes to a gitignored audit path).

**Action:**
- Close GP-1 evidence for AEE as incorrect (re-read `:1807` context)
- Reclassify UCOS-AEE-001 as OBSERVE in Task-004
- No fix required in engine code
- Document the misclassification evidence in Task-009 closure note

---

## 4. Replay Path Impact

Scenario A or B leads to a PRODUCER classification for the `aee-gate` tier.
The Task-005 Tier 4 replay contract for UCOS-AEE-001 depends on this task:

| Scenario | Tier 4 Replay Impact |
|---|---|
| A (guard exists) | Replay needed for `aee-gate` path. `emit()` with write=True is already guarded; replay calls with write=False |
| B (guard added) | Same as A after fix |
| C (no writes) | No replay needed; reclassify as OBSERVE; remove from Task-005 Tier 4 |

For Scenario A or B, the Task-005 replay contract for AEE reuses the emit(write=False)
path as the in-memory generation call:

```python
# aee_engine.py --replay:
if args.replay:
    result = emit(decl, model, write=False)    # generate without writing
    diffs = compare_result_to_disk(result)     # byte-compare
    sys.exit(1 if diffs else 0)
```

---

## 5. Validation Sequence

### Gate VG-16: aee-observe produces no tracked writes (Scenario A or B)

```bash
git stash          # clean state
python aee_engine.py aee-observe [inputs]
git diff --exit-code   # must be clean
```

### Gate VG-17: aee-gate still writes on passing gate (Scenario A or B)

```bash
python aee_engine.py aee-gate [inputs]
git diff --name-only   # must list expected output files
```

### Gate VG-18: emit(write=False) returns byte-identical result to emit(write=True) (Scenario B)

Test that in-memory generation is deterministic by comparing the returned value
across two calls with the same inputs.

### Gate VG-14: verify.sh still passes

```bash
bash verify.sh
```

---

## 6. Post-Task-009 Enablement

| Downstream | Enabled Action |
|---|---|
| Task-005 Tier 4 | AEE replay contract can be implemented and tested |
| Task-004 §4.9 | `aee-declaration.json` can receive `gate_mode: PRODUCER` + `replay_path` |
| GP-10 | Closed with evidence |

---

## 7. Forbidden Actions

| Action | Status |
|---|---|
| `aee_engine.py` modified | NONE |
| `emit()` function modified | NONE |
| Declaration files modified | NONE |
| Commits created | NONE |

---

*Task-009 GP-10 AEE tier guard fix plan complete. Three scenarios are possible:
A (guard exists — no code fix), B (guard absent — add write=True/False param to emit()),
C (no tracked writes — reclassify as OBSERVE). Pre-fix read of `emit()` body
determines the scenario. Scenario A or B unblocks Task-005 Tier 4 replay contract
and Task-004 §4.9 declaration write.*

---

Task-009 GP-10 AEE tier guard fix plan complete.
No engine mutation performed.
