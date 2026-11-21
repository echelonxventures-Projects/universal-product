# H-06 TASK-010 GATE PURITY CERTIFICATION PLAN

| Field | Value |
|---|---|
| **ID** | H-06-T010-GPCP |
| **Authority** | CERTIFICATION PLAN ONLY. No files modified. |
| **Phase** | Foundation Closure — Gate Purity Implementation — Task-010 |
| **Baseline** | HEAD `1f869865` · branch `integration/recovery-001` |
| **Depends on** | H-06-TASK-004 through H-06-TASK-009 (all complete) |
| **Produced** | 2026-08-16 |
| **Status** | PLAN COMPLETE — CERTIFICATION NOT YET PERFORMED |

---

## 1. Certification Authority

H-06 Gate Purity Implementation is complete when every programme with a confirmed
gate entry point carries a `gate_mode` declaration that is:

1. Supported by measurement evidence (Task-003)
2. For PRODUCER: accompanied by a tested `replay_path` (Task-005)
3. For PRODUCER with GP-2: write-order corrected before declaration (Task-006)
4. For PRODUCER with GP-4: dead flag implemented as replay path (Task-007)
5. For OBSERVE_WITH_DECLARED_AUDIT_EMISSION: `audit_emission` block present and audit path confirmed gitignored
6. Declaration file located or created (Task-008)
7. For UCOS-AEE-001: GP-10 resolved (Task-009)
8. All declarations syntactically valid JSON
9. `bash verify.sh` passes all stages that were passing at baseline `1f869865`
10. No new failing stages introduced by H-06 changes

This document defines the certification checklist, the evidence collection procedure,
and the certification commit structure.

---

## 2. Pre-Certification Completion Checklist

### 2.1 Engine Fixes Complete

| Fix | Task | Engine | Evidence Required |
|---|---|---|---|
| GP-2 RIB write-order | Task-006 | `rib_engine.py` | VG-10 exit codes recorded in commit |
| GP-2 URRC write-order | Task-006 | `urrc_engine.py` | VG-10 exit codes recorded |
| GP-2 UAR write-order | Task-006 | `uar_engine.py` | VG-10 exit codes recorded |
| GP-4 UCL dead flag | Task-007 | `ucl_engine.py` | VG-13 exit codes recorded |
| GP-4 UFEP dead flag | Task-007 | `ufep_engine.py` | VG-13 exit codes recorded |
| GP-4 UIS dead flag | Task-007 | `uis_engine.py` | VG-13 exit codes recorded |
| GP-10 AEE tier guard | Task-009 | `aee_engine.py` | VG-16/17 exit codes recorded or GP-10 closed as false alarm |

### 2.2 Replay Paths Tested

| Programme | Replay Target | VG-8 (exit 0) | VG-9 (exit 1 on diff) | Status |
|---|---|---|---|---|
| UCOS-UGA-001 | N/A (OBSERVE) | — | — | Not applicable |
| BASELINE-001 | `make baseline-replay` | Required | Required | Pending Task-005 Tier 1 |
| UCOS-URAT-001 | `make urat-replay` | Required | Required | Pending Task-005 Tier 1 |
| UCOS-UTCE-001 | `make utce-replay` or `--check-read-only` | Required | Required | Pending GP-8 clarification |
| ACEE-000001 | `make acee-replay` | Required | Required | Pending Task-005 Tier 1 |
| UCL-000001 | `make ucl-render` | Required | Required | Pending Task-007 + Task-005 |
| UCOS-UFEP-001 | `make ufep-render` | Required | Required | Pending Task-007 + Task-005 |
| UIS-001 | `make uis-render` | Required | Required | Pending Task-007 + Task-005 |
| UCOS-RIB-001 | `make rib-replay` | Required | Required | Pending Task-006 + Task-005 |
| URRC-000001 | `make urrc-replay` | Required | Required | Pending Task-006 + Task-005 |
| UCOS-UAR-001 | `make uar-replay` | Required | Required | Pending Task-006 + Task-005 |
| UCOS-AEE-001 | `make aee-replay` | Required | Required | Pending Task-009 + Task-005 |

### 2.3 Declaration Files Present and Valid

| Programme | Declaration File | JSON Valid | `gate_mode` Present | `replay_path` Present (PRODUCER) |
|---|---|---|---|---|
| UCOS-UGA-001 | `uga-declaration.json` | Required | OBSERVE | N/A |
| UCL-000001 | `ucl-declaration.json` | Required | PRODUCER | Required |
| UCOS-UFEP-001 | `ufep-declaration.json` | Required | PRODUCER | Required |
| UIS-001 | `uis-declaration.json` | Required | PRODUCER | Required |
| BASELINE-001 | `baseline-declaration.json` | Required | PRODUCER | Required |
| UCOS-URAT-001 | `urat-declaration.json` | Required | PRODUCER | Required |
| UCOS-UTCE-001 | `utce-declaration.json` | Required | PRODUCER | Required |
| ACEE-000001 | `acee-declaration.json` | Required | PRODUCER | Required |
| UCOS-AEE-001 | `aee-declaration.json` | Required | PRODUCER or OBSERVE | If PRODUCER |
| UKB | `ukb-declaration.json` | Required | OBSERVE_WITH_DECLARED_AUDIT_EMISSION | N/A; `audit_emission` required |
| UCOS-UCAF-001 | `ucaf-declaration.json` | Required | TBD (Task-008) | TBD |
| UCOS-RIB-001 | `rib-declaration.json` | Required | PRODUCER | Required |
| URRC-000001 | `urrc-declaration.json` | Required | PRODUCER | Required |
| UCOS-UAR-001 | `uar-declaration.json` | Required | PRODUCER | Required |

---

## 3. Certification Validation Run

The certification validation is a single sequential run of all validation gates,
performed after every task in §2 is confirmed complete.

### 3.1 Stage 1 — JSON Schema Validation (all declarations)

```bash
find /Users/bipin/Desktop/UCOS-CONSOLIDATION/00-MASTER -name "*declaration*.json" | \
  while read f; do
    python3 -c "import json, sys; json.load(open('$f')); print('OK', '$f')" || echo "FAIL $f"
  done
```

Expected: all files print OK.

### 3.2 Stage 2 — Mode Vocabulary Validation

```bash
find /Users/bipin/Desktop/UCOS-CONSOLIDATION/00-MASTER -name "*declaration*.json" | \
  while read f; do
    python3 -c "
import json, sys
d = json.load(open('$f'))
prog = d.get('programme', {})
mode = prog.get('gate_mode')
vocab = {'OBSERVE', 'PRODUCER', 'EXECUTION', 'OBSERVE_WITH_DECLARED_AUDIT_EMISSION'}
if mode and mode not in vocab:
    print('INVALID MODE', '$f', mode)
    sys.exit(1)
print('OK', '$f', mode or '(no mode)')
"
  done
```

Expected: all files print OK with a valid mode value.

### 3.3 Stage 3 — PRODUCER Replay Path Existence

```bash
python3 - <<'EOF'
import json, os, subprocess, sys
BASE = "/Users/bipin/Desktop/UCOS-CONSOLIDATION/00-MASTER"
errors = []
for root, dirs, files in os.walk(BASE):
    for f in files:
        if "declaration" in f and f.endswith(".json"):
            path = os.path.join(root, f)
            d = json.load(open(path))
            prog = d.get("programme", {})
            if prog.get("gate_mode") == "PRODUCER":
                rp = prog.get("replay_path")
                if not rp:
                    errors.append(f"MISSING replay_path: {path}")
if errors:
    for e in errors:
        print(e)
    sys.exit(1)
print("All PRODUCER declarations have replay_path")
EOF
```

### 3.4 Stage 4 — Replay Path Exit Codes

For each PRODUCER programme, run the named `replay_path` on the committed state:

```bash
make baseline-replay && echo "PASS baseline" || echo "FAIL baseline"
make urat-replay     && echo "PASS urat"     || echo "FAIL urat"
make utce-replay     && echo "PASS utce"     || echo "FAIL utce"
make acee-replay     && echo "PASS acee"     || echo "FAIL acee"
make ucl-render      && echo "PASS ucl"      || echo "FAIL ucl"
make ufep-render     && echo "PASS ufep"     || echo "FAIL ufep"
make uis-render      && echo "PASS uis"      || echo "FAIL uis"
make rib-replay      && echo "PASS rib"      || echo "FAIL rib"
make urrc-replay     && echo "PASS urrc"     || echo "FAIL urrc"
make uar-replay      && echo "PASS uar"      || echo "FAIL uar"
make aee-replay      && echo "PASS aee"      || echo "FAIL aee"
```

Expected: all print PASS.

### 3.5 Stage 5 — verify.sh Full Run

```bash
bash verify.sh 2>&1 | tee H-06-VERIFY-OUTPUT.txt
echo "Exit: $?"
```

Expected: exit 0. All stages passing at baseline `1f869865` still pass.
`H-06-VERIFY-OUTPUT.txt` is the primary evidence for the certification commit.

### 3.6 Stage 6 — Write-Order Confirmation (GP-2 programmes)

For each GP-2 programme, introduce a synthetic gate-fail condition and confirm
no tracked write occurs:

```bash
# Example for RIB — synthetic fail input:
git diff --exit-code  # confirm clean before
python 00-MASTER/UCOS-RIB-001/rib_engine.py --gate --fail-input [...]
git diff --exit-code  # must still be clean — no write on fail
```

Expected: `git diff --exit-code` exits 0 after a failed gate run.

---

## 4. Certification Commit Structure

Gate Purity Implementation is sealed with a single certification commit after
all validation stages pass. This commit adds no new code; it records the
certification evidence.

### 4.1 Certification Commit Files

| File | Content |
|---|---|
| `H-06-GATE-PURITY-CERTIFICATION.md` | Signed certification record (this task's output, populated after validation) |
| `H-06-VERIFY-OUTPUT.txt` | Raw `verify.sh` output from Stage 5 |
| `00-BOOK/DATA/generated-artifact-registry.json` | Updated to include PRODUCER output paths confirmed by H-06 |

### 4.2 Certification Commit Message

```
H-06: Gate Purity Implementation certified

All PRODUCER declarations carry tested replay_path.
All OBSERVE declarations confirmed zero tracked writes.
GP-2 write-order corrected: rib, urrc, uar.
GP-4 dead flags implemented: ucl, ufep, uis.
GP-10 AEE tier guard resolved.
verify.sh exit 0 — all prior-passing stages pass.

Evidence: H-06-VERIFY-OUTPUT.txt
```

---

## 5. Certification Record Template

The following certification record is to be completed after Stage 5 passes and
committed as `H-06-GATE-PURITY-CERTIFICATION.md`:

```markdown
# H-06 Gate Purity Certification

| Field | Value |
|---|---|
| Certified | <DATE> |
| Branch | integration/recovery-001 |
| HEAD at certification | <SHA> |
| verify.sh exit code | 0 |
| Programmes certified | <count> |
| Certifier | H-06 Implementation Programme |

## Certified Declarations

| Programme | Mode | Replay Path | VG-8 | VG-9 | GP Fix |
|---|---|---|---|---|---|
| UCOS-UGA-001 | OBSERVE | N/A | — | — | None |
| BASELINE-001 | PRODUCER | make baseline-replay | 0 | 1 | None |
| UCOS-URAT-001 | PRODUCER | make urat-replay | 0 | 1 | None |
| UCOS-UTCE-001 | PRODUCER | make utce-replay | 0 | 1 | GP-8 resolved |
| ACEE-000001 | PRODUCER | make acee-replay | 0 | 1 | None |
| UCL-000001 | PRODUCER | make ucl-render | 0 | 1 | GP-4 fixed |
| UCOS-UFEP-001 | PRODUCER | make ufep-render | 0 | 1 | GP-4 fixed |
| UIS-001 | PRODUCER | make uis-render | 0 | 1 | GP-4 fixed |
| UCOS-RIB-001 | PRODUCER | make rib-replay | 0 | 1 | GP-2 fixed |
| URRC-000001 | PRODUCER | make urrc-replay | 0 | 1 | GP-2 fixed |
| UCOS-UAR-001 | PRODUCER | make uar-replay | 0 | 1 | GP-2 fixed |
| UCOS-AEE-001 | PRODUCER | make aee-replay | 0 | 1 | GP-10 fixed |
| UKB | OBSERVE+AUDIT_EMISSION | N/A | — | — | None |

## verify.sh Summary

<paste Stage 5 output summary here>

## Certification Determination

All twelve programmes carry a constitutionally valid gate_mode declaration.
All PRODUCER declarations carry a tested replay_path.
Gate Purity Implementation is CERTIFIED.
```

---

## 6. H-06 Programme Closure

After the certification commit is merged to `integration/recovery-001`, the
H-06 Gate Purity Implementation Programme is closed. The following artefacts
constitute the programme record:

| Artefact | File |
|---|---|
| Task-001: Schema baseline | `H-06-TASK-001-DECLARATION-SCHEMA-AUDIT.md` |
| Task-002: Schema preparation | `H-06-TASK-002-DECLARATION-SCHEMA-PREPARATION-REPORT.md` |
| Task-003: Mode classification | `H-06-TASK-003-PROGRAMME-MODE-CLASSIFICATION-REPORT.md` |
| Task-004: Declaration update plan | `H-06-TASK-004-DECLARATION-UPDATE-PREPARATION-PLAN.md` |
| Task-005: Replay contract plan | `H-06-TASK-005-REPLAY-CONTRACT-IMPLEMENTATION-PLAN.md` |
| Task-006: GP-2 fix plan | `H-06-TASK-006-GP2-WRITE-ORDER-FIX-PLAN.md` |
| Task-007: GP-4 fix plan | `H-06-TASK-007-GP4-DEAD-FLAG-REMOVAL-PLAN.md` |
| Task-008: Declaration survey | `H-06-TASK-008-DECLARATION-FILE-LOCATION-SURVEY.md` |
| Task-009: GP-10 fix plan | `H-06-TASK-009-GP10-AEE-TIER-GUARD-FIX-PLAN.md` |
| Task-010: Certification plan | `H-06-TASK-010-GATE-PURITY-CERTIFICATION-PLAN.md` |
| Verification output | `H-06-VERIFY-OUTPUT.txt` |
| Certification record | `H-06-GATE-PURITY-CERTIFICATION.md` |

---

## 7. Forbidden Actions

| Action | Status |
|---|---|
| Engine files modified | NONE |
| Declaration files modified | NONE |
| Commits created | NONE |
| Certification record populated | NONE — template only |

---

*Task-010 gate purity certification plan complete. Ten tasks of planning are now
documented. Execution begins with Task-006 (GP-2 fixes, no external blockers),
Task-007 (GP-4 fixes, no external blockers), and Task-005 Tier 1 (BASELINE, URAT,
UTCE, ACEE replays, no external blockers). All three tracks are independent and
may proceed in parallel. Certification is gated on all tracks completing and
verify.sh exiting 0.*

---

H-06 Task-010 Gate Purity Certification Plan complete.
H-06 planning phase complete (Tasks 001–010).
Execution phase ready to begin.
