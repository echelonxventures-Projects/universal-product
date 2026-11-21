# PHASE 1 — VERIFICATION ARCHITECTURE REPORT

**Protocol**: UCOS Ω∞ Implementation Readiness Recovery  
**Date**: 2026-08-30  
**Source**: verify.sh (HEAD: 77798202)  
**Status**: COMPLETE

---

## EXECUTION ARCHITECTURE

### Entry Point

**Script**: `./verify.sh`  
**Language**: bash  
**Modes**: fast, change, integration, full  
**Flags**: --failfast, --serial, --explain  
**Default mode**: change (commit validation)

### Fail-Safe Design

**Planning failure behavior**: If intelligence faults, fall back to:
- Whole suite execution
- Coverage floor (90%)
- All stages run

**Principle**: Intelligence failure must never reduce verification scope.

---

## VERIFICATION MODES

### Mode Definitions

Source: `00-MASTER/UVI-000001/uvi-declaration.json` (constitution)

#### 1. --fast (developer feedback)
- Selection: impact-selected tests
- Coverage: NOT_EVALUATED
- Gates: lint only
- Purpose: rapid feedback loop

#### 2. --change (DEFAULT, commit validation)
- Selection: impact-selected tests
- Coverage: NOT_EVALUATED (unless escalated)
- Gates: all governance gates
- Purpose: pre-commit validation

#### 3. --integration (merge validation)
- Selection: WHOLE_SUITE
- Coverage: FLOOR_90 (evaluated)
- Gates: all governance gates
- Purpose: merge readiness

#### 4. --full (release certification)
- Selection: WHOLE_SUITE
- Coverage: FLOOR_90 (evaluated)
- Gates: all governance gates + registration observation
- Purpose: release certification

### Escalation Behavior

If impact selection cannot bound a change (declarations, schemas, unregistered files):
- Selection escalates to WHOLE_SUITE
- Coverage escalates to FLOOR_90
- Mode effectively becomes integration

**Principle**: Fail wide, never narrow.

---

## STAGE EXECUTION ORDER

### Stage 0: Environment Integrity (PRE-PLANNING)

**Label**: UEG-000001 environment integrity gate  
**Phase**: OBSERVE  
**Executor**: `ucos_env_gate`  
**Blocking**: YES (must pass before any stage runs)  

**Purpose**: Verify Python environment integrity before trusting it.

**Checks**:
1. Interpreter belongs to this repository
2. sys.prefix is canonical venv
3. Python series matches CI pin
4. pytest resolves
5. pytest_cov / coverage / jsonschema import successfully
6. All pins installed with declared executables
7. Configuration parses
8. Global shadowing detection (non-blocking)

**Why not run_stage**: Must precede planning, cannot execute through $PY.

**Cost**: 0.13-0.17s (budget: 5s)

### Stage 0b: Plan Computation (PRE-EXECUTION)

**Label**: Verification Intelligence Planning  
**Phase**: PLANNING  
**Executor**: `engine.verification_intelligence plan`  
**Blocking**: NO (failures fall back to full execution)

**Produces**: UVI_PLAN (TSV format)

**Plan contents**:
- Stage actions (RUN / SKIP / REUSE)
- Test selection
- Shard topology
- Coverage policy
- Evidence reuse decisions

**Plan digest**: Reproducible, deterministic, machine-comparable

---

## STAGE REGISTRY

### PREFLIGHT Phase (Stages 1-2)

**Characteristic**: Read-only or gitignored writes, safe to overlap.

#### Stage 1
**Label**: ruff lint + format-check (engine + platform)  
**Phase**: PREFLIGHT  
**Executor**: `ucos_ruff_gate`  
**Purpose**: Code quality gate (lint + format)  
**Output**: None (exit code only)  
**Concurrent**: YES

#### Stage 2
**Label**: prerequisite generation (knowledge · determinism · closure 1-3)  
**Phase**: PREFLIGHT  
**Executor**: `scripts/generate-prerequisites.sh`  
**Purpose**: Generate derived views (knowledge, determinism evidence, closure 1-3)  
**Output**: Gitignored paths only  
**Concurrent**: YES

**Writes**:
- `/knowledge/`
- `determinism-evidence/`
- UAKOS-CLOSURE-002 engine outputs

### TESTS Phase (Stage 3)

#### Stage 3
**Label**: pytest + coverage gate (--cov-fail-under=90)  
**Phase**: TESTS  
**Executor**: `engine.verification_intelligence run-tests` (or pytest fallback)  
**Purpose**: Test execution + coverage floor enforcement  
**Output**: `.coverage`, `coverage.xml`  
**Concurrent**: Sharded (13 shards, 12 workers in integration mode)

**Coverage behavior**:
- Shards write `.coverage.{index}` (distinct files)
- Post-run combine writes `.coverage`
- Post-run XML generation writes `coverage.xml`
- Floor evaluated once over union

**Fallback**: If planning failed, runs `pytest` directly (whole suite, floor enforced).

### MAIN Phase (Stages 4-18)

**Characteristic**: Read-only or gitignored writes, safe to overlap with each other.

**Drain point**: Before POST phase.

#### Stage 4
**Label**: omega gate (discovery · authority · reachability · ratchets · disposition)  
**Executor**: `python -m engine.universal_discovery`  
**Purpose**: Universal governance gate (5 phases)  
**Laws**: Ω-1 through Ω-5

#### Stage 5
**Label**: governance enforce --pre  
**Executor**: `ukb.py enforce --pre`  
**Purpose**: Pre-registration eligibility/validity gate

#### Stage 6
**Label**: registry validate (schema + integrity)  
**Executor**: `ukb.py validate`  
**Purpose**: Schema validation + referential integrity

#### Stage 7
**Label**: meta-constitutional conformance (CMG-INV-01..12)  
**Executor**: `00-CMG/tools/cmg-gate.sh`  
**Purpose**: Meta-layer conformance (12 invariants)

#### Stage 8
**Label**: universal object governance (UGA-INV-01..10)  
**Executor**: `uga_engine.py gate`  
**Purpose**: Universal object governance (10 invariants)

#### Stage 9
**Label**: autonomous universal evolution (UAUE gate, every declared obligation)  
**Executor**: `engine.uaue.gate --gate --quiet`  
**Purpose**: Evolution gate (all declared obligations)

#### Stage 10
**Label**: evolution surface replay (history + 18 registers)  
**Executor**: `engine.uaue.gate --replay --quiet`  
**Purpose**: Evolution surface byte-comparison

#### Stage 11
**Label**: universal object birth contract (UOBC-000001, identity before existence)  
**Executor**: `engine.object_birth.gate --gate --quiet`  
**Purpose**: Birth contract (8 laws)

#### Stage 12
**Label**: universal infinite scope and direction (UISD-000001, unbounded and self-applied)  
**Executor**: `engine.infinite_scope.gate --quiet`  
**Purpose**: Unboundedness (11 laws)

#### Stage 13
**Label**: constitutional primitive alignment (UCPA-000001, root ontology measured and reduced)  
**Executor**: `engine.root_ontology.gate --quiet`  
**Purpose**: Primitive reduction (8 laws)

#### Stage 14
**Label**: universal verification intelligence (UVI-000001, selection derived and assurance preserved)  
**Executor**: `engine.verification_intelligence.gate --gate --quiet`  
**Purpose**: Verification intelligence self-measurement (10 laws)

#### Stage 15
**Label**: universal construct foundation (UCON-000001, every construct disposed and nothing silently ignored)  
**Executor**: `engine.construct.gate --gate --quiet`  
**Purpose**: Construct disposition (16 laws)

#### Stage 16
**Label**: universal enforcement closure (UEC-000001, every protection governed, invoked twice and covered)  
**Executor**: `engine.enforcement_closure.gate --gate --quiet`  
**Purpose**: Enforcement surface closure (read-only)

#### Stage 17
**Label**: universal recursive knowledge foundation (URKE-000001, every unknown governed and no mechanism closed against a future domain)  
**Executor**: `engine.recursive_knowledge.gate --gate --quiet`  
**Purpose**: Recursive knowledge foundation (32 laws)

#### Stage 18
**Label**: mutation governance boundary decidability (EX-018, every classification rule implemented, reachable and claiming subjects)  
**Executor**: `platform.repository_intelligence.mutation_gate --gate --quiet`  
**Purpose**: Mutation classification (3 laws)

### POST Phase (Stage 19)

**Characteristic**: Reads MAIN outputs, cannot overlap MAIN.

**Drain required**: MAIN must complete first.

#### Stage 19
**Label**: coverage report  
**Executor**: `python -m coverage report`  
**Purpose**: Coverage summary (reads `.coverage`)  
**Dependency**: Stage 3 (pytest)

**Skipped when**: --fast or --change (unless escalated)

### EXTENDED Phase (Stage 20)

**Characteristic**: Opt-in only, reads POST outputs.

#### Stage 20 (--full only)
**Label**: registration observation (register.sh --observe, read-only)  
**Executor**: `register.sh --observe`  
**Purpose**: Registration drift detection  
**Mode**: Read-only (no minting, no mutation)

---

## CONCURRENCY MODEL

### Scheduling Strategy

**Parallel execution**: Stages in same phase run concurrently (if `--serial` not set).

**Phase transitions**: Automatic drain (wait for phase completion before next phase starts).

**Safety**: Only READ_ONLY or gitignored-write stages overlap.

### Wave Execution (Test Stage)

**Wave 0**: Exclusive shard (isolated tests)  
- 1 shard
- Tests requiring clean tree state
- Runs alone, before concurrent body

**Wave 1**: Concurrent body  
- 12 shards (in integration mode)
- Parallel execution
- Runs after wave 0 completes

**Principle**: Isolation is scheduling, never selection. Isolated tests still run, in exactly one shard.

---

## EVIDENCE REUSE

### Evidence Store

**Location**: Defined in constitution (`evidence_home`)  
**Digest**: SHA-256 over canonical input representation  
**Action**: REUSE when digest matches and previous result was PASS

**Modes permitting reuse**:
- --fast: YES
- --change: YES
- --integration: NO
- --full: NO

**Principle**: Certification-eligible modes cannot reuse evidence.

---

## FAILURE HANDLING

### Fail-Fast Mode

**Flag**: --failfast  
**Behavior**: Stop at first failing stage  
**Summary**: Printed before exit

**Default**: Continue through all stages (report all failures)

### Stage Failure Recording

**Arrays maintained**:
- `STAGES_RUN`: All executed stages
- `STAGES_FAIL`: Failed stages
- `STAGES_SECS`: Execution times

**Evidence recording**: Both PASS and FAIL recorded (cache must know failure occurred)

### Exit Behavior

**Exit 0**: All admitted stages passed  
**Exit 1**: One or more stages failed

**Summary format**:
```
PASS/FAIL  stage-label  duration
```

---

## VERIFICATION GUARANTEES

### UVI Laws Enforced

**UVI-L-01**: Flags accepted = modes declared (both directions)  
**UVI-L-02**: Bare invocation resolves to declared default  
**UVI-L-03**: Stage labels = registry (exactly, in order)  
**UVI-L-04**: Ratchet (certification contract preserved)  
**UVI-L-05**: Modes claim only what they measure  
**UVI-L-06**: Selection is derived (no hardcoded test paths)  
**UVI-L-07**: Fail wide (unbounded changes escalate)  
**UVI-L-08**: Topology neutrality (shards union to selection)  
**UVI-L-09**: No certification-eligible mode can reuse evidence  
**UVI-L-10**: Planning twice produces identical bytes

### Stage Contract

**Three readers**:
1. `verify.sh` (executor)
2. `UAKOS-CLOSURE-008/validation-record.json` (digester)
3. `.github/workflows/uisd-gate.yml` (re-deriver)

**Principle**: One string, one stage, three readers. Must agree.

---

## DEPENDENCIES

### Stage Dependencies (Declared)

**coverage report** depends on **pytest + coverage gate**

**registration observation** depends on **all MAIN gates**

**POST phase** depends on **MAIN phase completion**

### Implicit Dependencies

**All stages** depend on **Stage 0 (environment gate)**

**All stages** depend on **Stage 0b (planning)**

**Shard wave 1** depends on **wave 0 completion**

---

## VERIFICATION EXECUTION GRAPH

```
Stage 0: Environment Gate (blocking, sequential)
    ↓
Stage 0b: Plan Computation (non-blocking)
    ↓
PREFLIGHT Phase (parallel if not --serial)
    ├─ Stage 1: ruff lint + format-check
    └─ Stage 2: prerequisite generation
    ↓ (drain)
TESTS Phase
    └─ Stage 3: pytest + coverage gate
        ├─ Wave 0: exclusive shard (sequential)
        └─ Wave 1: concurrent shards (parallel)
        ↓ (post-shard combine & evaluate)
    ↓ (drain)
MAIN Phase (parallel if not --serial)
    ├─ Stage 4: omega gate
    ├─ Stage 5: governance enforce --pre
    ├─ Stage 6: registry validate
    ├─ Stage 7: meta-constitutional conformance
    ├─ Stage 8: universal object governance
    ├─ Stage 9: autonomous universal evolution
    ├─ Stage 10: evolution surface replay
    ├─ Stage 11: universal object birth contract
    ├─ Stage 12: universal infinite scope and direction
    ├─ Stage 13: constitutional primitive alignment
    ├─ Stage 14: universal verification intelligence
    ├─ Stage 15: universal construct foundation
    ├─ Stage 16: universal enforcement closure
    ├─ Stage 17: universal recursive knowledge foundation
    └─ Stage 18: mutation governance boundary decidability
    ↓ (drain)
POST Phase (sequential)
    └─ Stage 19: coverage report
    ↓ (drain)
EXTENDED Phase (--full only)
    └─ Stage 20: registration observation
    ↓
summarize_and_exit
```

---

## DETERMINISM PROPERTIES

### Reproducibility

**Plan digest**: SHA-256 over canonical JSON  
**No clock**: Plan contains no timestamps  
**No host**: Plan contains no machine paths  
**No randomness**: Shard assignment is deterministic (LPT algorithm)

**Guarantee**: Same state + same mode = same plan digest (on any machine)

### Topology Neutrality

**UVI-L-08**: Shards must union to exactly the selection.

**Assertion**: Before spawning shards, verify:
- No duplicate units
- No missing test objects
- No unselected objects

**Failure mode**: Shard plan that loses a test is rejected before execution.

---

## CURRENT HEAD STAGE COUNT

**Total stages**: 20 stages (21 including Stage 0)

**By phase**:
- PREFLIGHT: 2 stages
- TESTS: 1 stage
- MAIN: 15 stages
- POST: 1 stage
- EXTENDED: 1 stage (--full only)

**Certification path (--full)**: 20 stages executed

---

## OMEGA GATE PRESENCE

**Stage 4**: omega gate (discovery · authority · reachability · ratchets · disposition)

**Executor**: `python -m engine.universal_discovery`

**Status in HEAD**: **STAGED** (not yet committed)

**Implication**: HEAD verification will NOT execute omega gate.

**Staged verification will execute omega gate IF staged changes include stage wiring.**

---

## PHASE 1 CONCLUSIONS

### Architecture Status: WELL-DEFINED

- Stage order is explicit
- Dependencies are declared
- Phases enforce execution barriers
- Concurrency is safe (read-only or isolated writes)
- Fail-safe: planning failure widens scope

### Determinism Status: ENFORCED

- Plan is reproducible
- Shard assignment is deterministic
- No clock/host/random in plan
- Topology neutrality verified before execution

### Stage Contract: MEASURED

- Three-reader agreement enforced
- UVI laws self-measured
- Stage registry governs execution

### Concurrency Status: SAFE

- Phase transitions drain
- MAIN stages are read-only or gitignored-write
- POST reads MAIN outputs (cannot overlap)
- Test shards write distinct files (no contention)

### Coverage Status: CORRECT BY DESIGN

- Per-shard data files (no races)
- Sequential combine (no contention)
- Single XML write (no overwrite)
- Floor evaluated once over union

---

## PHASE 1 DELIVERABLE STATUS

✅ Entry point analyzed  
✅ Modes documented  
✅ Stages enumerated  
✅ Execution order established  
✅ Dependencies mapped  
✅ Concurrency model verified  
✅ Fail-safe behavior confirmed  
✅ Evidence reuse rules documented  
✅ Determinism properties verified  
✅ Execution graph produced

**Phase 1**: COMPLETE

**Next Phase**: Phase 2 — Fresh Verification (on HEAD, then staged)

---

## EVIDENCE CHAIN

All findings derived from:
- `verify.sh` (direct reading, lines 1-802)
- Stage invocations (grep extraction)
- Mode flag parsing (lines 61-86)
- Planning logic (lines 129-169)
- Stage execution machinery (lines 233-293)

No assumptions. Direct code analysis only.
