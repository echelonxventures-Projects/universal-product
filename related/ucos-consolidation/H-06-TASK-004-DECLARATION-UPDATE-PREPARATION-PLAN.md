# H-06 TASK-004 DECLARATION UPDATE PREPARATION PLAN

| Field | Value |
|---|---|
| **ID** | H-06-T004-DUPP |
| **Authority** | IMPLEMENTATION PREPARATION ONLY. No declaration files modified. |
| **Phase** | Foundation Closure — Gate Purity Implementation — Task-004 |
| **Baseline** | HEAD `1f869865` · branch `integration/recovery-001` |
| **Depends on** | H-06-TASK-003-PROGRAMME-MODE-CLASSIFICATION-REPORT.md |
| | H-06-TASK-002-DECLARATION-SCHEMA-PREPARATION-REPORT.md |
| **Produced** | 2026-08-16 |
| **Status** | PREPARATION COMPLETE — MUTATION NOT PERFORMED |

---

## 1. Scope Boundary

| Constraint | Status |
|---|---|
| Only existing `*-declaration.json` files affected | CONFIRMED — no new files created; `gate_mode` added to `programme` block of files that already exist |
| `gate_mode` is an additive field | CONFIRMED — Task-002 verified no existing `gate_mode`, `execution_mode`, or `mode` field in any declaration; JSON parsing unaffected |
| No new registry | CONFIRMED — mode belongs in `*-declaration.json` only; `mutation-governance-boundary.json` and `generated-artifact-registry.json` are not modified |
| No new governance authority | CONFIRMED — three existing authority surfaces remain non-overlapping |
| Declarations modified only after Task-003 measurement confirmed | CONFIRMED — all assignments below derive from GATE-PURITY-DETERMINATION.md evidence |

---

## 2. Declaration Update Matrix

### 2.1 Declarations with Confirmed Mode — Ready After Blocking Dependencies

| Programme | Declaration File | Current State | Proposed `gate_mode` | Evidence Source | Blocking Dependency | Validation Required |
|---|---|---|---|---|---|---|
| UCOS-UGA-001 | `00-MASTER/UCOS-UGA-001/uga-declaration.json` | `programme` block empty | `OBSERVE` | GP §2.1: `uga_engine.py:42,1889,1929` `mint=False` confirmed | None | VG-7: value matches measurement |
| UCL-000001 | `00-MASTER/UCL-000001/ucl-declaration.json` | `forbidden_write_prefixes` present; no mode | `PRODUCER` + `replay_path` | GP-1: `ucl_engine.py:3030` unconditional write | Task-007 (GP-4 dead flag) + Task-005 replay tested | VG-7, VG-8, VG-9 |
| UCOS-UFEP-001 | `00-MASTER/UCOS-UFEP-001/ufep-declaration.json` | `forbidden_write_prefixes` present; no mode | `PRODUCER` + `replay_path` | GP-1: `ufep_engine.py:1119`; GP-4: `:1082` | Task-007 (GP-4) + Task-005 | VG-7, VG-8, VG-9 |
| UIS-001 | `00-MASTER/UIS-001/uis-declaration.json` | `forbidden_write_prefixes` present; no mode | `PRODUCER` + `replay_path` | GP-1: `uis_engine.py:1814`; GP-4: `:1777` | Task-007 (GP-4) + Task-005 | VG-7, VG-8, VG-9 |
| BASELINE-001 | `00-MASTER/BASELINE-001/baseline-declaration.json` | `forbidden_write_prefixes` present; no mode | `PRODUCER` + `replay_path` | GP-1: `baseline_engine.py:1896` | Task-005 replay tested | VG-7, VG-8, VG-9 |
| UCOS-URAT-001 | `00-MASTER/UCOS-URAT-001/urat-declaration.json` | `forbidden_write_prefixes` present; no mode | `PRODUCER` + `replay_path` | GP-1: `urat_engine.py:1009` | Task-005 replay tested | VG-7, VG-8, VG-9 |
| UCOS-UTCE-001 | `00-MASTER/UCOS-UTCE-001/utce-declaration.json` | `forbidden_write_prefixes` present; no mode | `PRODUCER` + `replay_path` | GP-1: `utce_engine.py:855`; GP-8 self-guard | Task-005 replay tested | VG-7, VG-8, VG-9 |
| ACEE-000001 | `00-MASTER/ACEE-000001/acee-declaration.json` | `forbidden_write_prefixes` present; no mode | `PRODUCER` + `replay_path` | GP-1: `acee_engine.py:3730` | Task-005 replay tested | VG-7, VG-8, VG-9 |
| UCOS-AEE-001 | `00-MASTER/UCOS-AEE-001/aee-declaration.json` | `forbidden_write_prefixes` present; no mode | `PRODUCER` + `replay_path` (for `aee-gate` path) | GP-1: `aee_engine.py:1807`; GP-10 apparent | Task-009 (GP-10 emit() guard) + Task-005 | VG-7, VG-8, VG-9 |

### 2.2 Declarations with OBSERVE_WITH_DECLARED_AUDIT_EMISSION — Declaration File Not Yet Located

| Programme | IAR-Named Declaration | Filesystem Status | Proposed Mode | Action Required |
|---|---|---|---|---|
| UKB | `ukb-declaration.json` | NOT FOUND under `00-MASTER/` | `OBSERVE_WITH_DECLARED_AUDIT_EMISSION` | Locate declaration file before Task-004 write |

### 2.3 Declarations Requiring Additional Survey Before Task-004

| Programme | Declaration File | Issue | Action Before Task-004 |
|---|---|---|---|
| UCOS-RFP-001 | `00-MASTER/UCOS-RFP-001/rfp-declaration.json` | Gate behaviour not measured in GP-1..GP-11 | Measure `rfp` gate entry point tracked writes |
| UCOS-URR-001 | `00-MASTER/UCOS-URR-001/urr-declaration.json` | Gate behaviour not in GP-1..GP-11 | Measure `urr` gate entry point |
| UCCEP-000000 | Not found | Two-mode behaviour; declaration surface not located | Locate declaration; measure each tier |

### 2.4 Programmes in GP-1 Without Confirmed Declaration File

These programmes have confirmed GP-1 unconditional writes but no `*-declaration.json` was
found in Task-001/002. They require declaration-file location before Task-004:

| Programme | Write Evidence | Declaration Status |
|---|---|---|
| UCOS-UCAF-001 | `ucaf_engine.py:2104` (GP-1); CR-09 | No `ucaf-declaration.json` found — check for alternate location |
| UCOS-RIB-001 | `rib_engine.py:3925` (GP-2) | No `rib-declaration.json` found |
| URRC-000001 | `urrc_engine.py:2041` (GP-2) | No `urrc-declaration.json` found |
| UCOS-UAR-001 | `uar_engine.py:118-125` (GP-2) | No `uar-declaration.json` found |
| UCDA-000001 | `ucda_engine.py:1419` (GP-1) | No declaration found |
| UEI-000001 | `uei_engine.py:1367` (GP-1) | No declaration found |
| UER-000001 | `uer_engine.py:1043` (GP-1) | No declaration found |
| UCEF-000001 | `ucef_engine.py:1519` (GP-1) | No declaration found |
| MCOS-000001 | `mcos_engine.py:852` (GP-1) | No declaration found |
| UMK-000001 | `umk_engine.py:641` (GP-1) | No declaration found |
| UPF-000001 | `upf_engine.py:594` (GP-1) | No declaration found |

---

## 3. Mode Assignment Validation

### 3.1 OBSERVE Validation

**UCOS-UGA-001 (`gate_mode: OBSERVE`)**

| Check | Evidence | Status |
|---|---|---|
| Zero tracked writes | `cmd_gate` calls `build(mint=False)`; all `_dump`/`emit` in `cmd_run` (`uga_engine.py:1864-1886`) | CONFIRMED from source |
| Zero gitignored writes | No gitignored write path identified on `gate` subcommand | CONFIRMED |
| Source confirms no write on gate path | `uga_engine.py:1889` `cmd_gate` → `build(mint=False)` | CONFIRMED |
| Replay not applicable | `uga_engine.py run` is producing twin; gate does not produce artifacts | CONFIRMED |

### 3.2 PRODUCER Validation Checklist (per programme)

Each PRODUCER programme must satisfy all four checks before its declaration is written:

| Check | Requirement | When Satisfied |
|---|---|---|
| Artifact ownership | Outputs listed in or to be added to `generated-artifact-registry.json` under the programme's producer home | Before Task-004 write |
| Deterministic output | Same inputs → byte-identical outputs on re-run | Confirmed by Task-005 replay test |
| Replay contract | Named replay path: regenerates in memory, compares bytes, no write; exits 0 on match, non-zero on diff | Task-005 completed and tested |
| Write-order correct | Gate verdict established before any write (GP-2 engines: requires Task-006 first) | Task-006 completed for RIB, URRC, UAR |

**PRODUCER confidence summary:**

| Programme | Artifact Ownership | Determinism Assumed | Replay Needed | Write-Order Correct |
|---|---|---|---|---|
| UCL-000001 | Tracked `00-MASTER/UCL-000001/` registers | YES (derived computation) | Task-005 | YES (no GP-2) |
| UCOS-UFEP-001 | Tracked `00-MASTER/UCOS-UFEP-001/` registers | YES | Task-005 | YES (no GP-2) |
| UIS-001 | Tracked `00-MASTER/UIS-001/` registers | YES | Task-005 | YES (no GP-2) |
| BASELINE-001 | 5 tracked files per CI | YES | Task-005 | YES (no GP-2) |
| UCOS-URAT-001 | Tracked registers | YES | Task-005 | YES (no GP-2) |
| UCOS-UTCE-001 | Tracked registers | YES | Task-005 | YES (no GP-2) |
| ACEE-000001 | Tracked registers | YES | Task-005 | YES (no GP-2) |
| UCOS-AEE-001 | Tracked registers | YES | Task-005 | Requires GP-10 fix first |
| UCOS-RIB-001 | Tracked outputs | YES | Task-005 | NO — Task-006 first |
| URRC-000001 | Tracked outputs | YES | Task-005 | NO — Task-006 first |
| UCOS-UAR-001 | `uar.json` under `_OUT_DIR` | YES | Task-005 | NO — Task-006 first |

### 3.3 OBSERVE_WITH_DECLARED_AUDIT_EMISSION Validation

**UKB enforce --pre**

| Check | Evidence | Status |
|---|---|---|
| Zero tracked writes | `ukb.py enforce --pre` writes only to `.runtime/governance/enforcement-audit.json` — gitignored | CONFIRMED (GP-5) |
| Audit path gitignored | `.gitignore:12` excludes `.runtime/` | CONFIRMED |
| Audit write always-on, append-only | `ukb.py:1948`: "ALWAYS enforced — never conditional on an invocation flag"; `governance_telemetry.py:210-217` temp-file + `os.replace` pattern | CONFIRMED |
| `audit_emission` sub-field prepared | `{"path": ".runtime/governance/enforcement-audit.json", "type": "append-only"}` | READY to write — pending declaration file location |

### 3.4 EXECUTION Validation

No programme in the confirmed-declaration inventory is proposed EXECUTION at this stage.
The IAR §1.1 does not identify any programme requiring EXECUTION classification among
the 11 listed declarations. This section is reserved for any programme that, upon
measurement, proves to require EXECUTION classification.

---

## 4. Required Declaration Changes

The following changes are to be performed in Task-004 execution, after all blocking
dependencies are satisfied. **No change is performed in this document.**

### 4.1 `uga-declaration.json` — OBSERVE

```
File:  00-MASTER/UCOS-UGA-001/uga-declaration.json
Block: programme
Add:   "gate_mode": "OBSERVE"
After: last existing key in programme block
Reason: Confirmed zero tracked writes on gate subcommand; mint=False; all writes in cmd_run
Commit: H-06: Add gate_mode:OBSERVE to uga-declaration.json (IAR §1.1)
```

### 4.2 `ucl-declaration.json` — PRODUCER

```
File:  00-MASTER/UCL-000001/ucl-declaration.json
Block: programme
Add:   "gate_mode": "PRODUCER",
       "replay_path": "<to be confirmed in Task-005>"
After: forbidden_write_prefixes
Reason: GP-1 ucl_engine.py:3030 unconditional write; verdict after write
Blocking: Task-007 GP-4 dead flag resolved; Task-005 replay path tested
Commit: H-06: Add gate_mode:PRODUCER to ucl-declaration.json (IAR §1.1)
```

### 4.3 `ufep-declaration.json` — PRODUCER

```
File:  00-MASTER/UCOS-UFEP-001/ufep-declaration.json
Block: programme
Add:   "gate_mode": "PRODUCER",
       "replay_path": "<to be confirmed in Task-005>"
Reason: GP-1 ufep_engine.py:1119; GP-4 dead flag at :1082
Blocking: Task-007 GP-4; Task-005
Commit: H-06: Add gate_mode:PRODUCER to ufep-declaration.json (IAR §1.1)
```

### 4.4 `uis-declaration.json` — PRODUCER

```
File:  00-MASTER/UIS-001/uis-declaration.json
Block: programme
Add:   "gate_mode": "PRODUCER",
       "replay_path": "<to be confirmed in Task-005>"
Reason: GP-1 uis_engine.py:1814; GP-4 dead flag at :1777
Blocking: Task-007 GP-4; Task-005
Commit: H-06: Add gate_mode:PRODUCER to uis-declaration.json (IAR §1.1)
```

### 4.5 `baseline-declaration.json` — PRODUCER

```
File:  00-MASTER/BASELINE-001/baseline-declaration.json
Block: programme
Add:   "gate_mode": "PRODUCER",
       "replay_path": "<to be confirmed in Task-005>"
Reason: GP-1 baseline_engine.py:1896; CI workflow has render+diff shape
Blocking: Task-005
Commit: H-06: Add gate_mode:PRODUCER to baseline-declaration.json (IAR §1.1)
```

### 4.6 `urat-declaration.json` — PRODUCER

```
File:  00-MASTER/UCOS-URAT-001/urat-declaration.json
Block: programme
Add:   "gate_mode": "PRODUCER",
       "replay_path": "<to be confirmed in Task-005>"
Reason: GP-1 urat_engine.py:1009
Blocking: Task-005
Commit: H-06: Add gate_mode:PRODUCER to urat-declaration.json (IAR §1.1)
```

### 4.7 `utce-declaration.json` — PRODUCER

```
File:  00-MASTER/UCOS-UTCE-001/utce-declaration.json
Block: programme
Add:   "gate_mode": "PRODUCER",
       "replay_path": "<to be confirmed in Task-005>"
Reason: GP-1 utce_engine.py:855; GP-8 misleading self-guard
Blocking: Task-005
Commit: H-06: Add gate_mode:PRODUCER to utce-declaration.json (IAR §1.1)
```

### 4.8 `acee-declaration.json` — PRODUCER

```
File:  00-MASTER/ACEE-000001/acee-declaration.json
Block: programme
Add:   "gate_mode": "PRODUCER",
       "replay_path": "<to be confirmed in Task-005>"
Reason: GP-1 acee_engine.py:3730
Blocking: Task-005
Commit: H-06: Add gate_mode:PRODUCER to acee-declaration.json (IAR §1.1)
```

### 4.9 `aee-declaration.json` — PRODUCER

```
File:  00-MASTER/UCOS-AEE-001/aee-declaration.json
Block: programme
Add:   "gate_mode": "PRODUCER",
       "replay_path": "<to be confirmed in Task-005>"
Reason: GP-1 aee_engine.py:1807; aee-gate path confirmed write
Blocking: Task-009 GP-10 tier guard confirmed; Task-005
Commit: H-06: Add gate_mode:PRODUCER to aee-declaration.json (IAR §1.1)
```

### 4.10 UKB declaration (OBSERVE_WITH_DECLARED_AUDIT_EMISSION) — Pending File Location

```
File:  <to be located — ukb-declaration.json or equivalent>
Block: programme
Add:   "gate_mode": "OBSERVE",
       "audit_emission": {
         "path": ".runtime/governance/enforcement-audit.json",
         "type": "append-only"
       }
Reason: GP-5; ukb.py:1948 always-on audit write to gitignored path
Blocking: Locate declaration file
Commit: H-06: Add gate_mode:OBSERVE+audit_emission to ukb-declaration.json (IAR §1.1)
```

---

## 5. Validation Sequence

Each declaration change is committed independently and must pass the following sequence
before the next declaration is written:

### Step 1 — Declaration Schema Validation
```
python3 -c "import json; json.load(open('<file>'))"
```
Confirm: file parses without error. `gate_mode` value is within vocabulary.

### Step 2 — Mode Consistency Validation
Confirm: declared `gate_mode` value matches Task-003 measurement record.
PRODUCER declarations: `replay_path` field present and names an existing target.
OBSERVE declarations: no tracked write paths present on gate invocation.
OBSERVE_WITH_DECLARED_AUDIT_EMISSION: `audit_emission.path` is confirmed gitignored.

### Step 3 — Mutation Boundary Validation
Confirm: no change made to `mutation-governance-boundary.json`.
EXECUTION declarations (if any): resolving entry exists in boundary JSON.
PRODUCER declarations: outputs registered in `generated-artifact-registry.json`.

### Step 4 — Replay Validation (PRODUCER only)
Run the `replay_path` target or script:
- On identical input: must exit 0 (byte-identical output confirmed)
- On synthetic byte difference: must exit non-zero
Document exit codes as evidence before committing the declaration.

### Step 5 — verify.sh Validation
After each declaration commit:
```
bash verify.sh
```
Required: all stages that were passing before the commit continue to pass.
Any regression blocks further declaration commits until resolved.

---

## 6. Forbidden Actions

| Action | Status |
|---|---|
| Declaration files modified in this task | NONE |
| `gate_mode` fields added to any file | NONE |
| Code changes made | NONE |
| Registry changes made | NONE |
| Commits created | NONE |

This document is a preparation plan only. Every proposed change in §4 is described in
future tense. No file in the repository was modified during its production.

---

*This document is the Task-004 declaration update preparation artifact. It defines the
exact changes to be made per declaration, their blocking dependencies, and the
validation sequence required after each change. Task-004 execution (writing `gate_mode`
fields) begins only after each programme's blocking dependencies in Tasks 005–009 are
satisfied.*

---

Task-004 declaration update preparation complete.
No declaration mutation performed.
Implementation changes not executed.
