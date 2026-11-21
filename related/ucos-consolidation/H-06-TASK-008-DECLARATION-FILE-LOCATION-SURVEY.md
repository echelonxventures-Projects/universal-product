# H-06 TASK-008 DECLARATION FILE LOCATION SURVEY

| Field | Value |
|---|---|
| **ID** | H-06-T008-DFLS |
| **Authority** | SURVEY PLAN ONLY. No declaration files created or modified. |
| **Phase** | Foundation Closure — Gate Purity Implementation — Task-008 |
| **Baseline** | HEAD `1f869865` · branch `integration/recovery-001` |
| **Depends on** | H-06-TASK-002-DECLARATION-SCHEMA-PREPARATION-REPORT.md |
| | H-06-TASK-004-DECLARATION-UPDATE-PREPARATION-PLAN.md §2.2 / §2.4 |
| **Produced** | 2026-08-16 |
| **Status** | SURVEY PLAN COMPLETE — NO FILES CREATED |

---

## 1. Purpose

Task-002 confirmed the schema of existing `*-declaration.json` files and Task-004
identified programmes with confirmed GP behaviour whose declaration files could not
be located under `00-MASTER/`. Before Task-004 execution can write `gate_mode` fields
for these programmes, their declaration files must either be found at an alternate
location or created as new authorised files.

This task defines the discovery procedure, the creation specification for absent
declarations, and the UKB-specific location problem.

---

## 2. Programmes with Declaration File Not Located

### 2.1 One Programme with OBSERVE_WITH_DECLARED_AUDIT_EMISSION

| Programme | IAR-Named Declaration | Last Known Evidence | Priority |
|---|---|---|---|
| UKB | `ukb-declaration.json` | GP-5: `ukb.py:1948` always-on gitignored audit emit | HIGH — blocks Task-004 §4.10 |

### 2.2 Eleven Programmes with Confirmed GP-1 Writes and No Declaration Found

| Programme | Write Evidence | Declaration Status | Priority |
|---|---|---|---|
| UCOS-UCAF-001 | `ucaf_engine.py:2104` | Not found under `00-MASTER/UCOS-UCAF-001/` | HIGH — GP-1 CR-09 |
| UCOS-RIB-001 | `rib_engine.py:3925` | Not found under `00-MASTER/UCOS-RIB-001/` | HIGH — GP-2, blocked by Task-006 |
| URRC-000001 | `urrc_engine.py:2041` | Not found under `00-MASTER/URRC-000001/` | HIGH — GP-2, blocked by Task-006 |
| UCOS-UAR-001 | `uar_engine.py:118-125` | Not found under `00-MASTER/UCOS-UAR-001/` | HIGH — GP-2, blocked by Task-006 |
| UCDA-000001 | `ucda_engine.py:1419` | Not found | MEDIUM |
| UEI-000001 | `uei_engine.py:1367` | Not found | MEDIUM |
| UER-000001 | `uer_engine.py:1043` | Not found | MEDIUM |
| UCEF-000001 | `ucef_engine.py:1519` | Not found | MEDIUM |
| MCOS-000001 | `mcos_engine.py:852` | Not found | MEDIUM |
| UMK-000001 | `umk_engine.py:641` | Not found | MEDIUM |
| UPF-000001 | `upf_engine.py:594` | Not found | MEDIUM |

### 2.3 Three Programmes Requiring Behaviour Survey Before Mode Assignment

| Programme | Issue | Survey Required |
|---|---|---|
| UCOS-RFP-001 | Gate behaviour not measured in GP-1..GP-11 | Read `rfp_engine.py` gate path; identify write pattern |
| UCOS-URR-001 | Gate behaviour not measured | Read `urr_engine.py` gate path |
| UCCEP-000000 | Two-mode behaviour suspected; declaration surface unclear | Measure each tier; locate or create declaration |

---

## 3. Discovery Procedure

### 3.1 Search Pattern

For each programme in §2, execute:

```bash
find /Users/bipin/Desktop/UCOS-CONSOLIDATION/00-MASTER -name "*declaration*" -o -name "*decl*"
find /Users/bipin/Desktop/UCOS-CONSOLIDATION -name "<programme-id>*declaration*"
find /Users/bipin/Desktop/UCOS-CONSOLIDATION -name "*declaration*" | grep -i "<programme-id>"
```

Also check for variant naming patterns:
- `<engine-prefix>-declaration.json`
- `declaration.json` (unnested)
- `programme-declaration.json`
- `<programme-id>.declaration.json`

### 3.2 UKB-Specific Search

UKB is the highest-priority locate task. `ukb.py` exists at a known path;
the declaration file should be co-located or in the same `00-MASTER/` subtree:

```bash
find /Users/bipin/Desktop/UCOS-CONSOLIDATION -name "ukb*"
find /Users/bipin/Desktop/UCOS-CONSOLIDATION -name "ukb-declaration*"
```

If `ukb-declaration.json` does not exist anywhere in the repository, it must be
created. See §4.

### 3.3 UCAF-Specific Note

Task-004 notes that UCAF has no `ucaf-declaration.json` under `00-MASTER/UCOS-UCAF-001/`
but that `ucaf-authority.json` is present (visible in git status). Check whether:
- `ucaf-authority.json` carries any `programme` block with `gate_mode`
- The programme has a declaration file under an alternate authority path

```bash
cat 00-MASTER/UCOS-UCAF-001/ucaf-authority.json | python3 -m json.tool | grep -A5 programme
```

---

## 4. Creation Specification for Absent Declarations

If a declaration file is not found anywhere in the repository, it must be created.
New declaration files are authorised under H-06 scope for programmes with confirmed
GP findings. Every new declaration is minimal: only fields confirmed by measurement.

### 4.1 Minimum Schema (from Task-002 canonical surface)

```json
{
  "schema_version": "1.0",
  "programme": {
    "id": "<PROGRAMME-ID>",
    "gate_mode": "<MODE>",
    "forbidden_write_prefixes": []
  },
  "authority": {
    "constitutional_frame": "UCOS-UCAF-001",
    "validation_required": true
  }
}
```

`forbidden_write_prefixes` is populated with the tracked output paths confirmed
by the GP measurement. For a PRODUCER, this array lists paths that the replay
contract must regenerate. For OBSERVE, the array is empty.

`gate_mode` is populated only after:
- GP behaviour confirmed (Task-003)
- For PRODUCER: replay contract tested (Task-005)
- For OBSERVE_WITH_DECLARED_AUDIT_EMISSION: audit path confirmed gitignored

### 4.2 New Declaration Commit Authority

New declaration files are committed under:
```
H-06: Create <programme-id>-declaration.json (IAR §1.1 — gate_mode:<MODE>)
```

One commit per declaration. No batch creation.

---

## 5. GP-8 UTCE Clarification (Co-located with Task-008)

Task-005 §3.1.3 deferred a question about UCOS-UTCE-001: does the existing
`--check-read-only` flag at `utce_engine.py:855` already satisfy the replay contract?

**Survey procedure:**
```
Read utce_engine.py lines 840-900
Confirm: (a) does --check-read-only regenerate in memory?
         (b) does it byte-compare?
         (c) does it exit non-zero on byte diff?
```

**Outcomes:**
- If YES to all three → `--check-read-only` IS the replay path; declaration uses it
- If NO to any → implement `--replay` flag per Task-005 spec; `--check-read-only` is GP-8

---

## 6. RFP and URR Survey Procedure

### 6.1 UCOS-RFP-001

```
Read rfp_engine.py: locate cmd_gate() or equivalent gate entry point
Identify: write calls on the gate path
Determine: unconditional write (GP-1/PRODUCER), no write (OBSERVE), or conditional
Record findings in: H-06-TASK-008-SUPPLEMENT-RFP-SURVEY.md (if findings warrant)
```

### 6.2 UCOS-URR-001

```
Read urr_engine.py: same procedure as RFP
```

### 6.3 UCCEP-000000

```
Read uccep_engine.py: identify two invocation tiers
For each tier: determine write pattern
Locate any existing declaration or authority file for UCCEP
```

---

## 7. Outcomes Table

| Programme | Expected Outcome | Next Task Enabled |
|---|---|---|
| UKB | `ukb-declaration.json` found or created | Task-004 §4.10 |
| UCOS-UCAF-001 | `ucaf-declaration.json` found or `ucaf-authority.json` carries mode | Task-004 UCAF mode write |
| UCOS-RIB-001 | `rib-declaration.json` found or created (pending Task-006) | Task-004 RIB + Task-005 Tier 3 |
| URRC-000001 | `urrc-declaration.json` found or created (pending Task-006) | Task-004 URRC + Task-005 Tier 3 |
| UCOS-UAR-001 | `uar-declaration.json` found or created (pending Task-006) | Task-004 UAR + Task-005 Tier 3 |
| UCDA, UEI, UER, UCEF, MCOS, UMK, UPF | Declaration found or creation spec confirmed | Task-004 medium-priority writes |
| UCOS-RFP-001, UCOS-URR-001, UCCEP-000000 | GP behaviour measured | Task-003 supplement + Task-004 |
| UCOS-UTCE-001 (GP-8) | `--check-read-only` confirmed or replaced | Task-005 §3.1.3 finalised |

---

## 8. Forbidden Actions

| Action | Status |
|---|---|
| Declaration files created | NONE |
| Declaration files modified | NONE |
| Engine files modified | NONE |
| Commits created | NONE |

This document is a survey plan and specification only.
No file in the repository was modified during its production.

---

*Task-008 declaration file location survey plan complete. Twelve programmes require
location discovery before Task-004 execution can write their `gate_mode` fields.
UKB is highest priority (OBSERVE_WITH_DECLARED_AUDIT_EMISSION). Three GP-2 programmes
(RIB, URRC, UAR) are additionally blocked by Task-006. Three unsurveyed programmes
(RFP, URR, UCCEP) require gate-behaviour measurement before mode assignment.*

---

Task-008 declaration file location survey plan complete.
No file mutation performed.
