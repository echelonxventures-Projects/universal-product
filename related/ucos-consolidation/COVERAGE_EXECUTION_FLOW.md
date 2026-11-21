# COVERAGE EXECUTION FLOW — VERIFIED TRUTH

**Status**: CONTRADICTION RESOLVED  
**Date**: 2026-08-30  
**Evidence Source**: Direct code analysis + execution trace reconstruction

---

## EXECUTIVE SUMMARY

**Previous claim**: Multiple shards wrote `coverage.xml` concurrently, causing a race condition.

**Actual behavior**: Only ONE coverage.xml write occurs per run, and it happens AFTER all shards complete.

**Resolution**: The previous claim was **INCORRECT**. No concurrent XML writers exist in any mode.

---

## COVERAGE GENERATION ARCHITECTURE

### Per-Shard Behavior

**Location**: `engine/verification_intelligence/execution.py:336-349`

Each shard runs with:
```python
env["COVERAGE_FILE"] = os.path.join(data_dir, f".coverage.{shard.index}")
```

**Key facts**:
- Each shard writes to a **distinct** `.coverage.{index}` file
- Data directory is `tempfile.mkdtemp(prefix="uvi-coverage-")` — **outside the repository**
- Files are named: `.coverage.0`, `.coverage.1`, `.coverage.2`, etc.
- No shard ever writes `coverage.xml`
- No shard ever writes `.coverage` (the canonical combined file)

**Evidence**: execution.py:338-339

---

### Wave Execution Model

**Location**: `engine/verification_intelligence/execution.py:329-369`

Waves execute **sequentially**:
```python
for wave in sorted({shard.wave for shard in shards}):
    in_wave = [shard for shard in shards if shard.wave == wave]
    # spawn all shards in this wave
    # wait for all to complete
    # then proceed to next wave
```

**Key facts**:
- Wave 0: exclusive shard (isolated tests)
- Wave 1: concurrent body (remaining shards)
- Wave N completes fully before wave N+1 starts
- No overlap between waves

**Evidence**: execution.py:333-356

---

### Shard Arguments Under Coverage

**Location**: `engine/verification_intelligence/execution.py:266-276`

When `coverage is Coverage.FLOOR_90`:
```python
return [
    python, "-m", "pytest",
    "--cov-fail-under=0",      # floor NOT evaluated per-shard
    "--cov-report=",            # NO report generated per-shard
    "-q",
    *deselect,
    *shard.test_paths,
]
```

**Key facts**:
- `--cov-report=` means: collect data, generate **no reports**
- `--cov` targets come from `pyproject.toml` addopts (not overridden)
- Each shard measures the **same** source set
- Each shard writes only its `.coverage.{index}` data file

**Evidence**: execution.py:271-272

---

### Post-Shard Combine Phase

**Location**: `engine/verification_intelligence/execution.py:375-376, 383-436`

After all waves complete:
```python
if coverage is Coverage.FLOOR_90:
    status = _combine_and_evaluate(interpreter, base, data_dir, out) or status
```

**The combine phase does THREE operations, sequentially**:

#### 1. Combine
```python
env["COVERAGE_FILE"] = os.path.join(base, ".coverage")
combine = _coverage("combine", "--keep", *files)
```
- Reads: `.coverage.0`, `.coverage.1`, ... (from temp dir)
- Writes: `.coverage` (in repository root)
- Single process, no concurrency

**Evidence**: execution.py:406, 418

#### 2. XML Generation
```python
xml = _coverage("xml", "--fail-under=0")
```
- Reads: `.coverage` (just written above)
- Writes: `coverage.xml` (in repository root)
- Single process, no concurrency
- `--fail-under=0` means: don't evaluate floor here

**Evidence**: execution.py:426

#### 3. Floor Evaluation
```python
report = _coverage("report", "--fail-under=90")
```
- Reads: `.coverage` (same combined data)
- Writes: nothing (reports to stdout)
- This is the ONLY place the 90% floor is evaluated

**Evidence**: execution.py:430

**Key facts**:
- All three operations run **after** all shards terminate
- All three operations run **sequentially** (not concurrently)
- Only ONE `coverage.xml` write occurs
- Only ONE `.coverage` write occurs
- Only ONE floor evaluation occurs

---

## BEHAVIOR BY MODE

### Fast Mode (`--fast`)
- Selection: impact-selected
- Coverage: `Coverage.NOT_EVALUATED`
- Shard argv includes: `--no-cov`
- No `.coverage` files written
- No `coverage.xml` written
- No floor evaluated

**Evidence**: execution.py:277-287

### Change Mode (`--change`)
- Selection: impact-selected
- Coverage: `Coverage.NOT_EVALUATED` (unless escalated)
- Same as fast mode unless escalation triggers
- If escalated: behaves like integration mode

**Evidence**: plan.py:147-158

### Integration Mode (`--integration`)
- Selection: `WHOLE_SUITE`
- Coverage: `FLOOR_90`
- All shards write `.coverage.{index}`
- Post-run combine writes `.coverage`
- Post-run combine writes `coverage.xml`
- Floor evaluated once

**Evidence**: plan.py:154, execution.py:375-436

### Full Mode (`--full`)
- Same as integration mode
- Plus: registration observation stage runs

**Evidence**: verify.sh:796-800

---

## CONTRADICTION RESOLUTION

### Previous Claim
> "Multiple shards wrote coverage.xml concurrently"

### Evidence Against
1. No shard command line includes `--cov-report=xml`
2. Shards use `--cov-report=` (empty = no reports)
3. XML generation happens in `_combine_and_evaluate`
4. `_combine_and_evaluate` runs **after** all shards complete
5. `_combine_and_evaluate` is a single-threaded function
6. Only ONE `coverage xml` invocation exists in the entire flow

**Evidence**: execution.py:266-436

### How the Misunderstanding Occurred

**Hypothesis 1**: Observation of partial state
- Viewer saw `.coverage.0`, `.coverage.1`, etc. during execution
- Assumed these were concurrent writes to same file
- Actually: distinct files, no contention

**Hypothesis 2**: Misread of `--cov-report=` argument
- Saw `--cov-report=` in shard argv
- Assumed empty string meant "default behavior"
- Actually: empty string means "no reports"

**Hypothesis 3**: Confusion between data and report
- Shards DO write coverage data concurrently
- But data files are `.coverage.{index}` (distinct)
- Report file `coverage.xml` is written once, later

**Most likely**: Hypothesis 3 — conflation of data collection (concurrent, distinct files) with report generation (sequential, single file).

---

## CURRENT STATE VALIDATION

### Files Present
```
./.coverage          ← combined data from all shards
./coverage.xml       ← XML report, written once after combine
```

**Evidence**: Bash output from initial investigation

### No Race Condition Exists

**Proof by architecture**:
1. Shards write to numbered data files (distinct names)
2. Combine phase runs after all shards exit (temporal separation)
3. XML generation runs after combine completes (sequential dependency)
4. No code path writes `coverage.xml` from multiple locations

**Proof by observation**:
- Current run succeeded
- No coverage corruption observed
- Floor evaluated correctly
- XML artifact present and valid

---

## ANSWERS TO CRITICAL QUESTIONS

### 1. Which shard(s) write coverage.xml?
**NONE**. XML is written by the post-run combine phase, not by any shard.

### 2. Which shard(s) write .coverage files?
**ALL** shards under `FLOOR_90` coverage write `.coverage.{index}` (distinct files).  
**NONE** write `.coverage` (combined file) — that's the combine phase.

### 3. Which shard(s) merge coverage?
**NONE**. The merge is performed by `_combine_and_evaluate`, which runs after all shards complete.

### 4. Whether any concurrent writes occur?
**NO** concurrent writes to any shared file.  
Concurrent writes to **distinct** per-shard data files: YES (by design, no contention).

### 5. Whether behavior differs by mode?
- **Fast/change (no escalation)**: no coverage collection at all
- **Change (escalated)**: same as integration
- **Integration/full**: coverage collected, combined, reported (no race)
- **All modes**: XML generation is post-run, single-threaded, once

---

## IMPLICATIONS

### For Previous Root Causes
Any failure previously attributed to "coverage.xml race" must be re-investigated:
- The race **does not exist**
- The root cause is something else
- Previous remediation plans targeting the race are invalid

### For Current Failures
Current failures (19 observed, 4 stages) are **NOT** caused by coverage races.

### For Readiness Determination
The coverage architecture is **CORRECT AS DESIGNED**:
- No race conditions
- Deterministic
- Floor evaluated once over union
- Topology-neutral (measured by UVI-L-08)

---

## EVIDENCE MANIFEST

| Claim | Evidence | Location |
|-------|----------|----------|
| Shards write distinct data files | `env["COVERAGE_FILE"] = os.path.join(data_dir, f".coverage.{shard.index}")` | execution.py:339 |
| Shards generate no reports | `"--cov-report="` in shard argv | execution.py:272 |
| Waves execute sequentially | `for wave in sorted(...)` with inner wait loop | execution.py:333-356 |
| Combine runs after shards | `status = _combine_and_evaluate(...)` after wave loop | execution.py:376 |
| XML written once | Single `_coverage("xml", ...)` call | execution.py:426 |
| Combine is sequential | `_combine_and_evaluate` is not concurrent | execution.py:383-437 |

---

## CONCLUSION

**The coverage.xml race condition was a misdiagnosis.**

The architecture is:
- ✅ Concurrent data collection (distinct files per shard)
- ✅ Sequential combination (single process)
- ✅ Sequential XML generation (single process)
- ✅ Single floor evaluation (over combined data)
- ✅ No shared file writes during concurrent phase

**No remediation required for coverage architecture.**

**Next phase**: Re-investigate all failures previously attributed to this non-existent race.
