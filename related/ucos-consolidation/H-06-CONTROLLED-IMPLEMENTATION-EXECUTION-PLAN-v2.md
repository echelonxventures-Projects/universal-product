# H-06 CONTROLLED IMPLEMENTATION EXECUTION PLAN — v2

| Field | Value |
|---|---|
| **ID** | H-06-CIEP-v2 |
| **Authority** | PLANNING ONLY. No implementation authorized in this document. |
| **Phase** | Foundation Closure — Gate Purity Controlled Implementation |
| **Baseline** | HEAD `1f869865` · branch `integration/recovery-001` |
| **Supersedes** | H-06-CONTROLLED-IMPLEMENTATION-EXECUTION-PLAN.md (v1) — see §0 |
| **Depends on** | H-06-IAR-AUTHORIZATION-MATRIX-CORRECTION.md (corrected inventory and matrix) |
| | H-06-R4-GRANDFATHERING-POLICY-DECISION-RECORD.md (P-3, unsigned) |
| | H-06-IMPLEMENTATION-AUTHORIZATION-DECISION-RECORD.md (§8 unsigned) |
| | H-06-PRE-IMPLEMENTATION-REPOSITORY-STATE-VALIDATION.md (boundary state) |
| **Status** | PLAN PREPARED — EXECUTION NOT STARTED — BLOCKED ON O-1, O-2, O-7 |

---

## 0. Why v2 Exists

v1 cannot be executed as written. Its Phase 1 discovery command targets a directory that
contains no declaration files, its programme inventory names six files that do not exist,
its schema placement rule is impossible for two files, and its success criterion is
arithmetically unreachable. v2 corrects each defect against measured repository state.

| v1 Defect | v1 Text | v2 Correction | § |
|---|---|---|---|
| D-2 | `find 00-BOOK -name "*-declaration.json"` | `find 00-MASTER -name "*-declaration.json"` | §3 Phase 1 |
| D-2 | `grep -l "gate_mode" 00-BOOK/**/*-declaration.json` | `find 00-MASTER … -exec grep -l … +` | §3 Phase 6.1 |
| D-3 | 11-programme table (6 nonexistent) | Tier A/B/C/D inventory | §2 |
| D-4/D-5 | "`gate_mode` inside `programme` block" for all 11 | 9 capable; `uga`/`urr` blocked | §3 Phase 2 |
| D-1 | "46 gates" | **45** at baseline | §2.3 |
| D-10 | "All 46 gates carry declared modes" | 4 authorized; 41 recorded as gap | §6 |
| D-8 | Task-008 §4 file creation "authorised" | **REFUSED** | §5 |
| A-1 | `verify.sh` baseline assumed 10/10 | Baseline capture is a hard gate | §3 Phase 0 |
| D-11 | "10/10 PASS" matches no measured stage count (9 at baseline, 11 in tree) | Denominator taken from the Phase 0.5 log | §3 Phase 6.3 |
| A-4 | Dirty tree "does not block" | Isolation required before Phase 6.2 | §3 Phase 0 |

v1 remains valid as the record of the original plan. It must not be executed.

---

## 1. Authority Boundary

### 1.1 Ratified Decision

Option B — Explicit Multi-Mode Gate Model is ratified
(H-06-RATIFICATION-VALIDATION-REVALIDATION-DETERMINATION.md §8, all 5 checks PASS).
Terminal mode vocabulary, unchanged by this document:
`OBSERVE` · `PRODUCER` · `EXECUTION` · `OBSERVE_WITH_DECLARED_AUDIT_EMISSION`.

### 1.2 Corrected Authorization Scope

Scope is the **Tier A** and **Tier E** rows of
H-06-IAR-AUTHORIZATION-MATRIX-CORRECTION.md §4 — 12 actions. Tiers B, C, D and all
file creation are **outside** authorized scope and appear in this plan only as
blocked items awaiting owner decisions O-3..O-6.

Permitted changes under existing authorization:

| # | Change | Count |
|---|---|---|
| 1 | Additive `gate_mode` on Tier A declarations | 4 files |
| 2 | PRODUCER replay contracts for Tier A programmes classified PRODUCER | ≤4 |
| 3 | GP-2 write-order correction | 3 engines |
| 4 | GP-4 dead flag resolution | 3 engines |
| 5 | GP-5 `verify.sh` stage 4 label correction | 1 line |
| 6 | GP-10 `aee_engine.py:1807` tier guard | 1 guard |
| 7 | GP-9 `audit_emission` sub-field on Tier A OBSERVE declarations | as measured |
| 8 | `GATE-PURITY-DETERMINATION.md` re-assessment | 1 file |

### 1.3 No New Architecture, No New Registry, No New Authority

No new registry, governance surface, authority layer, or constitutional document is created.
`gate_mode` is recorded **only** in a programme's declaration file — Knowledge Once observed.
The three authority surfaces remain non-overlapping:

- `00-BOOK/DATA/mutation-governance-boundary.json` — mutation class governance
- `00-BOOK/DATA/generated-artifact-registry.json` — generated artifact registration
- per-programme declaration file — execution mode declaration

### 1.4 Forbidden Write Targets — Corrected

`<prefix>.json` artifacts (`rib.json`, `ucaf.json`, `uaie.json`, `urrc.json`, `uar.json`)
are **registered generated artifacts**, confirmed present in
`generated-artifact-registry.json`. They are derived truth and must never receive a
`gate_mode` field. Any step that appears to require writing a declaration into one of them
is a defect in that step, not a permission.

---

## 2. Corrected Programme Inventory

### 2.1 Authoritative Discovery Command

```bash
find 00-MASTER -name "*-declaration.json" | sort
```

Returns exactly **11** files. `find 00-BOOK -name "*-declaration.json"` returns **0** and
must not be used.

### 2.2 Tiered Inventory

**Tier A — authorized and executable (4):**

| File | Programme | Gate target |
|---|---|---|
| `00-MASTER/UCL-000001/ucl-declaration.json` | `UCL-000001` | `ucl-gate` |
| `00-MASTER/UCOS-UFEP-001/ufep-declaration.json` | `UCOS-UFEP-001` | `ufep-gate` |
| `00-MASTER/UCOS-URAT-001/urat-declaration.json` | `UCOS-URAT-001` | `urat-gate` |
| `00-MASTER/UCOS-UTCE-001/utce-declaration.json` | `UCOS-UTCE-001` | `utce-gate` |

**Tier B — structurally blocked (1):** `uga-declaration.json` — no `programme` block (D-4).
Blocked pending O-4.

**Tier C — IAR-named, nonexistent (6):** `ucaf`, `uaie`, `uaue`, `uccep`, `cmg`, `ukb`.
Blocked pending O-3/O-6. Actual surfaces for the first four are
`ucaf-authority.json`, `uaie-architecture.json`, `uaue-evolution.json`,
`uccep-bindings.json`; `cmg` and `ukb` surfaces are unlocated.

**Tier D — exists, not IAR-named (6):** `aee` (GP-10 programme), `uis` (GP-4 programme),
`acee`, `baseline`, `rfp`, `urr` (structurally blocked, D-5). Blocked pending O-3.

### 2.3 Gate Target Denominator

**45** at baseline HEAD. Verify before any coverage claim:

```bash
git show HEAD:Makefile | grep -cE '^[a-z0-9._-]+-gate:'    # expect 45
grep -cE '^[a-z0-9._-]+-gate:' Makefile                     # 46 — includes uncommitted uaue-gate
```

All coverage arithmetic uses 45. Never 46, unless the UAUE delta is committed under UAUE
authority first.

---

## 3. Implementation Phases

### Phase 0 — Boundary Correction Preconditions (NEW in v2)

v1 had a three-condition Pre-Condition Gate. Two of the three failed at validation, and
three further preconditions were missing. Phase 0 is the complete gate.

| # | Condition | Verification | Current State |
|---|---|---|---|
| 0.1 | IADR §8 AUTHORIZED — signed and dated | Read IADR §8 | **FAIL — unsigned** |
| 0.2 | P-3 R-4 policy selected | Read H-06-R4-GRANDFATHERING-POLICY-DECISION-RECORD.md §7 | **FAIL — unselected** |
| 0.3 | Baseline confirmed | `git rev-parse HEAD` = `1f869865…`; `git rev-parse --abbrev-ref HEAD` = `integration/recovery-001` | **PASS** |
| 0.4 | Corrected success criteria accepted (O-7) | Owner acceptance of AMC §5, incl. GP-11 terminating OPEN (residual) | **FAIL — not accepted** |
| 0.5 | `verify.sh` pre-implementation baseline captured (A-1) | Baseline result recorded with adequate timeout | **FAIL — never captured** |
| 0.6 | Unrelated deltas isolated on H-06-scoped files | `verify.sh` and `generated-artifact-registry.json` free of unrelated uncommitted changes | **FAIL — both dirty** |

**No phase begins until all six conditions pass.** 0.1, 0.2, 0.4 are owner acts. 0.5 and
0.6 are preparatory and may be done by the implementation authority. 0.6 requires the
owning programmes (UAUE et al.) to commit their own work — H-06 has no authority to do it.

#### 0.5 — Baseline Capture Procedure

v1 Phase 1.7 said "Run `verify.sh` at baseline. Record 10/10 PASS." It timed out at 120s
and was never captured. Corrected:

```bash
# Long-running: allow generous timeout, capture full output, do not discard on failure.
bash verify.sh 2>&1 | tee H-06-VERIFY-BASELINE-1f869865.log
echo "exit=${PIPESTATUS[0]}"
```

Record the **actual** result, pass or fail. A failing baseline is still a valid baseline —
it is the comparand. Do not assert 10/10 without the log.

#### 0.6 — Isolation Verification

```bash
git diff --name-only -- verify.sh 00-BOOK/DATA/generated-artifact-registry.json
# must return nothing before H-06 touches either file
```

---

### Phase 1 — Discovery and Baseline Evidence

**Purpose:** evidenced starting state. Read-only.

**1.1 Confirm baseline**

```bash
git rev-parse HEAD                  # 1f869865d5ff709c03cb4eb595524820d55d0be6
git rev-parse --abbrev-ref HEAD     # integration/recovery-001
git status --porcelain | wc -l      # record; dirty state is expected and documented
```

**1.2 Inventory declarations — CORRECTED PATH**

```bash
find 00-MASTER -name "*-declaration.json" | sort          # expect 11
```

**1.3 Confirm `gate_mode` absent — CORRECTED, portable**

```bash
find 00-MASTER -name "*-declaration.json" \
  -exec grep -l '"gate_mode"\|"execution_mode"\|"audit_emission"\|"replay_path"' {} +
# expect: no output (0 files)
```

v1's `grep -l "gate_mode" 00-BOOK/**/*-declaration.json` fails twice over: wrong directory,
and under `zsh` the unmatched glob raises `no matches found` rather than reporting zero.

**1.4 Confirm structural capability per file**

```bash
python3 - <<'PY'
import json, glob, os
for f in sorted(glob.glob('00-MASTER/*/*-declaration.json')):
    d = json.load(open(f)); p = d.get('programme')
    print(f"{os.path.basename(f):28} programme={type(p).__name__:9} "
          f"fwp={isinstance(p,dict) and 'forbidden_write_prefixes' in p}")
PY
```

Expected: 8 `dict` with `fwp=True`; `rfp` `dict`/`False`; `uga` `NoneType`; `urr` `str`.
Any deviation halts Phase 1.

**1.5 Confirm GP-2 targets** — `rib_engine.py:3925`/`:3942`,
`urrc_engine.py:2041`/`:2056`, `uar_engine.py:118-125`.

**1.6 Confirm GP-4 targets**

```bash
grep -n '"--render"' 00-MASTER/UCL-000001/ucl_engine.py \
  00-MASTER/UCOS-UFEP-001/ufep_engine.py 00-MASTER/UIS-001/uis_engine.py
# expect :2983, :1082, :1777
```

**1.7 Confirm GP-10 target**

```bash
sed -n '1805,1809p' 00-MASTER/UCOS-AEE-001/aee_engine.py
# expect: written = emit(decl, model)   — unguarded
```

**1.8 Confirm GP-5 target**

```bash
sed -n '123p' verify.sh
# expect: # Read-only eligibility/validity/classification gate (same gate CI runs first).
```

**1.9 Confirm gate denominator** — §2.3 commands; expect 45.

**Gate:** all of 1.1–1.9 confirmed. Phase 0 already passed.

---

### Phase 2 — Declaration Schema Preparation

**Purpose:** confirm the additive field is compatible. No declaration modified.

**2.1 Placement rule — CORRECTED**

`gate_mode` is added inside the `programme` **object**. It may be added only where
`programme` is a JSON object.

| Declaration | `programme` | Placement |
|---|---|---|
| Tier A (4) + `acee`, `aee`, `baseline`, `uis` | object, has `fwp` | inside `programme`, adjacent to `forbidden_write_prefixes` |
| `rfp` | object, no `fwp` | inside `programme`; **no `fwp` anchor** — place after `id` |
| `uga` | **absent** | **IMPOSSIBLE** — Tier B, blocked (D-4) |
| `urr` | **string** | **IMPOSSIBLE** — Tier D, blocked (D-5) |

v1 §2.1's unconditional "alongside `forbidden_write_prefixes`" holds for 8 of 11 files only.

**2.2 Schema addition**

```json
"gate_mode": "OBSERVE | PRODUCER | EXECUTION",

// PRODUCER only — hard co-obligation:
"replay_path": "<make target or engine flag>",

// OBSERVE_WITH_DECLARED_AUDIT_EMISSION only:
"audit_emission": { "path": "<gitignored path>", "type": "append-only" }
```

If R-4 Option 1 is selected, the transitional value and its controls are as specified in
H-06-R4-GRANDFATHERING-POLICY-DECISION-RECORD.md §5.1. The terminal vocabulary is unchanged.

**2.3 Enforcement compatibility**

```bash
grep -rl "check-declaration" 00-MASTER --include="*.py" | grep -v __pycache__ | wc -l
# 23 engines carry the self-guard
```

Confirm no engine rejects an unknown additive key before all in-scope declarations are
updated. **Do not activate `gate_mode` enforcement in Phase 2** — activation is governed by
R-4 control C-6.

**2.4** No declaration file is modified in this phase.

**Gate:** placement rule confirmed per file; enforcement confirmed non-breaking.

---

### Phase 3 — Programme Mode Classification (Tier A only)

**Purpose:** measure actual gate behaviour. No mode declared speculatively.

Per Tier A programme, in order:

| Step | Action |
|---|---|
| 3.x.1 | `git status --porcelain > /tmp/before.txt` |
| 3.x.2 | Run the programme's gate entry point (`make <prog>-gate`) |
| 3.x.3 | `git status --porcelain > /tmp/after.txt; diff /tmp/before.txt /tmp/after.txt` |
| 3.x.4 | Capture gitignored writes: targeted `find` on known write paths + `.runtime/` |
| 3.x.5 | Assign mode from evidence |
| 3.x.6 | Record the measurement; **do not write the declaration yet** |

Assignment criteria (unchanged from v1):

| Measured Behaviour | Mode |
|---|---|
| Zero tracked, zero gitignored writes | OBSERVE |
| Zero tracked; always-on gitignored append-only audit write | OBSERVE_WITH_DECLARED_AUDIT_EMISSION |
| Writes deterministic tracked artifacts as declared purpose | PRODUCER |
| Writes via explicit flag/subcommand as authorized governance act | EXECUTION |

**Pre-measurement indications** (from GATE-PURITY-DETERMINATION.md — **not** assignments):

| Programme | Indication |
|---|---|
| `UCL-000001` | GP-1 unconditional write (`ucl_engine.py:3030`); GP-4 dead `--render` — likely PRODUCER |
| `UCOS-UFEP-001` | GP-1 (`ufep_engine.py:1119`); GP-4 dead `--render` — likely PRODUCER |
| `UCOS-URAT-001` | GP-1 (`urat_engine.py:1009`) — likely PRODUCER |
| `UCOS-UTCE-001` | GP-1 (`utce_engine.py:855`); GP-8 `--check-read-only` may already be the replay path |

**Measurement-order dependency (NEW in v2):** UCL and UFEP are **both** GP-4 targets.
Measuring their gate behaviour before the GP-4 fix measures the *pre-fix* behaviour. Since
the GP-4 fix may wire `--render` to a render path, the measurement must either follow
Phase 5.3 for those two engines or be explicitly recorded as pre-fix and re-measured after.
v1 had no such dependency and would have produced a mode declaration describing behaviour
the implementation then changed.

**Gate:** each Tier A programme has an evidenced measurement record before Phase 4.

---

### Phase 4 — Declaration Writes and Replay Contracts

**Purpose:** write measured modes; satisfy the PRODUCER co-obligation.

Per Tier A programme:

4.x.1 Confirm the Phase 3 measurement record exists.
4.x.2 Add `"gate_mode": "<measured>"` inside the `programme` object.
4.x.3 If OBSERVE_WITH_DECLARED_AUDIT_EMISSION: add `audit_emission`; confirm path gitignored.
4.x.4 **If PRODUCER**, before committing anything:
  - identify committed outputs in `generated-artifact-registry.json`
  - implement/locate in-memory regeneration — **no disk write first**
  - implement byte-comparison; exit non-zero on any difference
  - test: replay against committed artifacts → exit 0
  - test: inject a synthetic byte difference → exit non-zero
  - add `"replay_path": "<target>"`
4.x.5 Commit declaration **and** replay path in **one** commit.
4.x.6 Message: `H-06: gate_mode:<VALUE> — <file> (IAR §1.1, AMC Tier A)`

**Hard rules:** no PRODUCER declaration is committed without a tested replay path in the
same commit. Non-determinism in a PRODUCER is a blocking defect, resolved before declaring.
One commit per programme; no batching.

**Gate:** each committed declaration matches its measurement exactly; every PRODUCER names a
tested replay path.

---

### Phase 5 — Defect Remediation (Tier E)

Independent of Phases 3–4. **May proceed in parallel with them** once Phase 0 and Phase 1
pass — Tier E is keyed to `file:line` evidence, not to the declaration inventory.

**Ordering: GP-10 and GP-2 are P0.** Write-before-verdict and observe-alias mutation are
defects under every mode and are never grandfathered (R-4 control C-4).

#### 5.1 GP-10 — `aee_engine.py:1807` tier guard (P0, first)

Confirm the `args` namespace and tier flag name by reading surrounding context, then guard
the `emit()` call so it does not execute under `--tier observe`. The exact guard expression
is confirmed at implementation time, not pre-written.

Verify: run with `--tier observe`; `git status --porcelain` shows zero new tracked writes.
Verify: normal invocation unaffected. Commit independently.

#### 5.2 GP-2 — write-order correction, 3 engines (P0)

P-4 first: re-confirm each engine identity and line numbers against GATE-PURITY GP-2.
Per engine: resequence so the gate verdict is established before any write. Commit per engine.
Verify per engine: no write occurs before the verdict on the corrected path.

#### 5.3 GP-4 — dead flag resolution, 3 engines

P-5 first: re-confirm identities. Per engine, determine whether `--render` has an intended
path (wire it) or is vestigial (remove it and all dead references). No parser flag may remain
unreachable. Commit per engine.

**Feeds back into Phase 3** for UCL and UFEP — see the Phase 3 measurement-order dependency.

#### 5.4 GP-5 — `verify.sh` stage 4 label

**Precondition:** Phase 0.6 — `git diff --name-only -- verify.sh` returns nothing.

Correct the line 123 label to `OBSERVE_WITH_DECLARED_AUDIT_EMISSION`. Commit independently.

```bash
grep -n "OBSERVE_WITH_DECLARED_AUDIT_EMISSION" verify.sh   # expect the corrected line
```

#### 5.5 GP-9 — gitignored audit path classification

For Tier A programmes measured as carrying always-on append-only gitignored audit writes:
confirm the path is gitignored, confirm append-only, add `audit_emission` in Phase 4.
Declaration addition only — no new governance surface.

---

### Phase 6 — Verification

#### 6.1 Structural Validation — CORRECTED COMMANDS

```bash
# Declarations carrying gate_mode (expect 4 for Tier A completion)
find 00-MASTER -name "*-declaration.json" -exec grep -l '"gate_mode"' {} + | sort

# Vocabulary + co-obligation audit
python3 - <<'PY'
import json, glob, os
OK = {"OBSERVE","PRODUCER","EXECUTION","OBSERVE_WITH_DECLARED_AUDIT_EMISSION"}
for f in sorted(glob.glob('00-MASTER/*/*-declaration.json')):
    d = json.load(open(f)); p = d.get('programme')
    if not isinstance(p, dict) or 'gate_mode' not in p: continue
    m = p['gate_mode']
    print(os.path.basename(f), m,
          "VOCAB-FAIL" if m not in OK else "",
          "REPLAY-MISSING" if m == "PRODUCER" and 'replay_path' not in p else "",
          "AUDIT-MISSING" if m == "OBSERVE_WITH_DECLARED_AUDIT_EMISSION"
                             and 'audit_emission' not in p else "")
PY
```

| Check | Expected |
|---|---|
| Tier A declarations carry `gate_mode` | 4 of 4 |
| No value outside vocabulary | 0 violations |
| Every PRODUCER names `replay_path` | 0 `REPLAY-MISSING` |
| Every EXECUTION resolves in `mutation-governance-boundary.json` | cross-reference per programme |
| Every `audit_emission` path is gitignored | `git check-ignore -v <path>` per entry |
| `<prefix>.json` files carry **no** `gate_mode` | 0 hits — forbidden write targets (§1.4) |

#### 6.2 Behaviour Validation

**Precondition — Phase 0.6 isolation.** Before/after `git status --porcelain` comparison is
only meaningful on a tracked surface free of unrelated churn. With 31 unstaged generated-artifact
modifications present, a zero-tracked-writes claim is unfalsifiable. This is the reason
0.6 is a hard gate rather than advice.

| Check | Method |
|---|---|
| `aee_engine.py --tier observe` → zero tracked writes | `git status --porcelain` before/after |
| GP-2 engines: verdict before write | trace corrected path per engine |
| GP-4 engines: flag reaches path or is absent | invoke flag; confirm path or parser absence |
| `verify.sh` stage 4 label | `grep -n OBSERVE_WITH_DECLARED_AUDIT_EMISSION verify.sh` |
| PRODUCER replay byte-identical | run replay; exit 0 on committed bytes, non-zero on injected diff |

#### 6.3 Verification Run — CORRECTED CRITERION

```bash
bash verify.sh 2>&1 | tee H-06-VERIFY-POST-IMPLEMENTATION.log
echo "exit=${PIPESTATUS[0]}"
```

**Required result: no regression against the Phase 0.5 captured baseline.**

v1 required "10/10 PASS" absolutely. That cannot be evaluated without a pre-implementation
comparand, and none exists (A-1). If the Phase 0.5 baseline is 10/10, then 10/10 is required.
If it is not, the requirement is no new failing stage. **Do not assert 10/10 without the
baseline log.**

**The "10/10" figure does not match the measured stage count.** Direct measurement:

```bash
git show HEAD:verify.sh | grep -c '^run_stage'   # 9  at baseline
grep -c '^run_stage' verify.sh                    # 11 in working tree (UAUE 6c/6d added)
```

The baseline invokes **9** `run_stage` calls, not 10; the working tree invokes **11**. The
"10/10 PASS" requirement repeated throughout the H-06 chain matches neither. It appears to
derive from the 10-row stage *inventory* in H-06-TASK-001-BASELINE-CAPTURE-REPORT.md §2,
which counts opt-in stage 7 (`--full` only) and sub-stage 3b as numbered stages. **Take the
denominator from the Phase 0.5 log, not from any document.** Recorded as defect D-11.

#### 6.4 Gate Purity Re-Assessment

Re-measure each finding. No finding is marked CLOSED without re-measurement.

| Finding | Expected Outcome Under Corrected Scope |
|---|---|
| GP-1 (15 unconditional writes) | **OPEN (residual)** — only Tier A programmes declared; most GP-1 engines are outside authorized scope |
| GP-2 (write before gate branch) | **CLOSED** — 3 engines corrected |
| GP-3 (8 replay targets write before compare) | CLOSED or OPEN (residual) per engine |
| GP-4 (3 dead `--render` flags) | **CLOSED** — wired or removed |
| GP-5 (false read-only label) | **CLOSED** — label corrected |
| GP-6 (stage 1b vs gitignore negation) | re-measure; likely OPEN (residual) |
| GP-7 (CI reverts mutation) | re-assess after write-order fixes |
| GP-8 (misleading self-guard) | re-assess; UTCE `--check-read-only` resolved in Phase 4 |
| GP-9 (undeclared gitignored writes) | CLOSED for Tier A; OPEN (residual) elsewhere |
| GP-10 (aee-observe unconditional emit) | **CLOSED** — tier guard verified |
| GP-11 (undeclared modes) | **OPEN (residual — scope-bounded)**. 4 of 45 declared. **Must not be marked CLOSED.** |

---

## 4. Corrected Phase Dependency Graph

```
        ┌─────────────── OWNER ACTS (blocking) ───────────────┐
        │  O-1  R-4 policy selected      (P-3)                │
        │  O-2  IADR §8 signed                                │
        │  O-7  corrected success criteria accepted           │
        └──────────────────────┬──────────────────────────────┘
                               ↓
   Phase 0 — Boundary Correction Preconditions  (0.1 … 0.6)
        0.5 verify.sh baseline captured   ← NEW, hard gate
        0.6 unrelated deltas isolated     ← NEW, hard gate
                               ↓
   Phase 1 — Discovery and Baseline Evidence  (corrected paths)
                               ↓
   Phase 2 — Schema Preparation  (per-file placement capability)
                               ↓
          ┌────────────────────┴────────────────────┐
          ↓                                         ↓
  Phase 5 — Tier E fixes                   Phase 3 — Tier A measurement
  (P0: 5.1 GP-10, 5.2 GP-2)                        │
          │                                         │
  5.3 GP-4 (ucl, ufep, uis) ──── feeds ────────────►│  re-measure UCL/UFEP
          │                                         ↓
  5.4 GP-5 (needs 0.6)              Phase 4 — declaration + replay commits
  5.5 GP-9                                          │
          └────────────────────┬────────────────────┘
                               ↓
   Phase 6 — Verification  (6.1 → 6.2 needs 0.6 → 6.3 vs baseline → 6.4)
```

### 4.1 Dependency Corrections vs v1

| # | v1 | v2 |
|---|---|---|
| 1 | Phases strictly linear 1→6 | Phase 5 (Tier E) parallel with Phases 3–4; keyed to `file:line`, not inventory |
| 2 | No GP-4 → Phase 3 feedback | GP-4 fix changes UCL/UFEP gate behaviour; measurement must follow or re-run |
| 3 | `verify.sh` baseline inside Phase 1 (step 1.7), skippable | Phase 0.5 hard gate before Phase 1 |
| 4 | Dirty tree "does not block" | Phase 0.6 hard gate; Phase 6.2 unfalsifiable without it |
| 5 | GP-5 had no isolation precondition | Phase 5.4 requires 0.6 on `verify.sh` |
| 6 | Phase 6.3 absolute 10/10 | Regression comparison against 0.5 baseline |
| 7 | ITBP Task-009 "may parallelize" only informally | GP-10 is P0 and explicitly first in Phase 5 |

---

## 5. Forbidden Actions

Additions in v2 are marked **[v2]**.

| Forbidden Action | Basis |
|---|---|
| Creating any new `*-declaration.json` **[v2]** | No authorization exists; AMC §4.6 refuses ITBP Task-008 §4 |
| Writing `gate_mode` into any `<prefix>.json` (`rib.json`, `ucaf.json`, `uaie.json`, `urrc.json`, `uar.json`) **[v2]** | Registered generated artifacts — derived truth |
| Adding a `programme` block to `uga-declaration.json` **[v2]** | Structural change; IADR §5, §1.3 |
| Restructuring `urr-declaration.json` `programme` string→object **[v2]** | Structural change; requires O-5 |
| Writing `gate_mode` to any Tier B/C/D surface **[v2]** | Outside authorized scope pending O-3..O-6 |
| Asserting "46 gates" in any coverage claim **[v2]** | Baseline denominator is 45 |
| Marking GP-11 CLOSED **[v2]** | Unreachable under authorized scope; AMC §5 |
| Asserting `verify.sh` 10/10 without the Phase 0.5 baseline log **[v2]** | A-1 unresolved |
| Committing `H-06-MUTATION-GOVERNANCE-OWNER-DECISION-RECORD.md.save` **[v2]** | Duplicate unsigned constitutional snapshot |
| Committing UAUE / UAIE / UCKP / UGA / UICM deltas under H-06 authority **[v2]** | H-06 holds no authority over them |
| Activating `gate_mode` enforcement before R-4 controls C-1/C-2 exist **[v2]** | R-4 control C-6 |
| Declaring a mode before measurement | Evidence before conclusion |
| Declaring PRODUCER without a tested replay path in the same commit | Hard co-obligation |
| Declaring EXECUTION without a resolving `mutation-governance-boundary.json` entry | Option B invariant 4 |
| Modifying `mutation-governance-boundary.json` authority chains | IAR §4; IADR §5 |
| Creating any new registry, governance surface, or authority layer | Knowledge Once; Canonical Ownership |
| Modifying `00-BOOK/DATA/` beyond approved scope | IAR §4 |
| Modifying UICO or UICM artifacts | Standing constraint |
| Modifying H-01..H-05 or R-B1..R-B5 scope | Outside H-06 |
| Skipping any phase gate in §3 | Each gate is a hard dependency |
| Batching unrelated changes in one commit | Rollback isolation |

---

## 6. Corrected Success Criteria

| # | Criterion | Confirmation | Required |
|---|---|---|---|
| S-1 | Tier A coverage | 4 of 4 Tier A declarations carry a measured `gate_mode` | YES |
| S-2 | Scope gap recorded | 41 of 45 gate targets recorded in `ASSESSMENT-CONFLICT-REGISTER.md` with named owners (R-4 C-5) | YES |
| S-3 | PRODUCER obligations | every PRODUCER names a tested replay path, co-committed | YES |
| S-4 | Tier E complete | GP-2 (3), GP-4 (3), GP-5 (1), GP-10 (1) all corrected and verified | YES |
| S-5 | No verification regression | Phase 6.3 vs Phase 0.5 baseline | YES |
| S-6 | GP re-assessment | GP-2, GP-4, GP-5, GP-10 → CLOSED; GP-1, GP-11 → OPEN (residual — scope-bounded) | YES |
| S-7 | Honest closure statement | Gate purity dimension recorded **NOT CLOSED**; Foundation Freeze remains blocked on it | YES |

### 6.1 What Authorized H-06 Execution Achieves

**It does not close gate purity.** Completing every authorized action declares 4 of 45 gate
targets. Freeze condition (1) "mutation boundaries declared" remains **NO**.

The supportable closure statement is:

> GP-2, GP-4, GP-5, GP-10 CLOSED. GP-1 and GP-11 OPEN (residual — 41 of 45 gate targets
> outside authorized scope). Gate purity dimension NOT closed. Foundation Freeze remains
> blocked on gate purity pending owner decisions O-3 through O-6.

H-01..H-05 and R-B1..R-B5 remain independent and outside this scope.

---

## 7. Rollback Strategy

### 7.1 Evidence Preservation

Before Phase 1: baseline SHA recorded; Phase 0.5 `verify.sh` log committed as a dated
artifact; Phase 1 evidence snapshot produced. During implementation: one commit per
programme / per engine / per fix; messages reference the IAR section, GP finding, and AMC
tier. No batching.

### 7.2 Recovery

`git revert` is preferred over `git reset --hard`. Each change is independently reversible:

| Change | Recovery |
|---|---|
| `gate_mode` on a declaration | `git revert` — additive field removed, no schema breakage |
| PRODUCER declaration + replay path | `git revert` — both together, as committed |
| GP-10 tier guard | `git revert` — single conditional |
| GP-2 write-order (per engine) | `git revert` |
| GP-4 flag wiring/removal (per engine) | `git revert` |
| GP-5 label | `git revert` — single string |
| GP-9 `audit_emission` | `git revert` — additive field |

Reverting one commit must not be assumed to revert others.

### 7.3 Rollback Triggers

| Trigger | Scope |
|---|---|
| New failing `verify.sh` stage vs Phase 0.5 baseline, unresolvable in scope | revert the introducing commit |
| Declared mode contradicts measured behaviour | revert the declaration; re-measure before re-declaring |
| PRODUCER replay fails byte-comparison | revert the PRODUCER commit; fix replay first |
| Any action outside AMC Tier A/E | revert immediately |
| Any Tier B/C/D surface written without owner extension **[v2]** | revert immediately; record as boundary violation |

### 7.4 Failed Classification

If a Tier A programme's behaviour is not covered by the vocabulary: do not declare a mode;
document the anomaly against the relevant GP finding; do not block other programmes;
escalate for a scope-extension decision.

If verification regresses and cannot be resolved in scope: stop. Do not declare gate purity
closure. Record OPEN (residual) and escalate.

---

*This document is a planning artifact. It corrects the v1 execution plan against measured
repository state and does not authorize any implementation action. Execution requires owner
acts O-1, O-2, and O-7, and satisfaction of all six Phase 0 conditions. Every command in
this plan was executed read-only against HEAD `1f869865` and produced the stated result. No
source file, declaration, registry, engine, or workflow was modified during its production.*

---

Controlled implementation execution plan v2 prepared.
Execution not started.
Repository mutation not performed.
