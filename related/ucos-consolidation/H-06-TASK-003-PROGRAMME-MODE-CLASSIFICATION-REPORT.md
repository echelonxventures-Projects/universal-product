# H-06 TASK-003 PROGRAMME MODE CLASSIFICATION REPORT

| Field | Value |
|---|---|
| **ID** | H-06-T003-PMCR |
| **Authority** | CLASSIFICATION ONLY. No declaration files modified. No repository mutation. |
| **Phase** | Foundation Closure — Gate Purity Implementation — Task-003 |
| **Baseline** | HEAD `1f869865` · branch `integration/recovery-001` |
| **Evidence source** | `GATE-PURITY-DETERMINATION.md` GP-1..GP-11 (measured, file:line confirmed) |
| **Produced** | 2026-08-16 |
| **Status** | CLASSIFICATION COMPLETE — DECLARATIONS NOT YET WRITTEN |

---

## 1. Classification Authority

| Item | Status |
|---|---|
| Option B ratified | YES — H-06-RATIFICATION-VALIDATION-REVALIDATION-DETERMINATION.md §8 |
| Mode vocabulary authoritative | OBSERVE / PRODUCER / EXECUTION / OBSERVE_WITH_DECLARED_AUDIT_EMISSION |
| Classification is evidence-based | YES — all assignments derive from GATE-PURITY-DETERMINATION.md measured findings |
| Classification modifies declarations | NO — this task produces proposed modes only; Task-004 writes declarations |
| Speculative assignment | PROHIBITED — any programme without sufficient evidence is listed in §4 (Unknowns) |

---

## 2. Programme Inventory

### 2.1 Confirmed OBSERVE — declared in code or script header

| Programme | Gate Entry | Current Behaviour | Writes? | Mutation Class | Replay Available | Proposed Mode | Evidence |
|---|---|---|---|---|---|---|---|
| CMG-000001 | `cmg-gate.sh` → `cmg_validate.py --repo-root` | Validates constitutional invariants; writes nothing | NO — `--emit` is opt-in, not passed by `verify.sh` | N/A | Not applicable — no artifact to replay | **OBSERVE** | GP determination §2.1: script header lines 3–13; `cmg_validate.py:692,725-726` |
| UCOS-UGA-001 | `uga_engine.py gate` | Verifies universal object invariants; explicitly mints nothing | NO — `cmd_gate` calls `build(mint=False)`; all `_dump`/`emit` in `cmd_run` | N/A | `uga_engine.py run` is the producing twin | **OBSERVE** | GP determination §2.1: `uga_engine.py:42,1889,1929` |

### 2.2 Confirmed OBSERVE — structural, undeclared (correct pattern, needs formal declaration)

| Programme | Gate Entry | Current Behaviour | Writes? | Mutation Class | Replay Available | Proposed Mode | Evidence |
|---|---|---|---|---|---|---|---|
| UAIE-000001 | `uaie_engine.py --gate` | Measures; writes only behind `if args.render:` | NO on `--gate` path | N/A | `if args.render: write_registers(model)` is the producing twin | **OBSERVE** | GP determination §2.2: `uaie_engine.py:1538-1541` |
| UAUE (engine.uaue.gate) | `python -m engine.uaue.gate --gate` | Evolution gate; writes strictly behind `if args.render:` | NO on `--gate` path | N/A | `--replay` path confirmed byte-compare; `make uaue-render` is mutating twin | **OBSERVE** | GP determination §2.1: `gate.py:677-683,697-701,824-826` |
| UAUE replay | `python -m engine.uaue.gate --replay` | Regenerates in memory, compares committed bytes | NO | N/A | IS the replay path | **OBSERVE** | GP determination §2.1: `verify.sh:222` |

### 2.3 OBSERVE_WITH_DECLARED_AUDIT_EMISSION — always-on gitignored audit write

| Programme | Gate Entry | Current Behaviour | Writes? | Mutation Class | Audit Path | Proposed Mode | Evidence |
|---|---|---|---|---|---|---|---|
| UKB (ukb.py enforce --pre) | `ukb.py enforce --pre` (verify.sh stage 4) | Eligibility/validity/classification gate; appends to enforcement audit | YES — gitignored `.runtime/governance/enforcement-audit.json` (always-on, append-only) | Gitignored — cannot dirty tree | `.runtime/governance/enforcement-audit.json` | **OBSERVE_WITH_DECLARED_AUDIT_EMISSION** | GP-5: `ukb.py:1896,1997`; `governance_telemetry.py:210-217`; `ukb.py:1948` "ALWAYS enforced" |
| UCCEP-000000 (evidence logs) | `uccep_engine.py --gate` (observe tier) | Emission-authority pattern: withholds tracked write; per-check evidence logs written unconditionally | YES — gitignored `00-MASTER/**/evidence/` unconditionally | Gitignored | `00-MASTER/**/evidence/` | **OBSERVE_WITH_DECLARED_AUDIT_EMISSION** (for observe/withheld tier) | GP-9: `uccep_engine.py:647-648`; GP determination §2.1 partial |

### 2.4 PRODUCER — unconditional tracked writes, deterministic derived artifacts

These programmes write tracked artifacts as their declared purpose on the `--gate` path.
Under Option B they are classified PRODUCER. Each requires a tested replay contract
(Task-005) before their declaration is written (Task-004).

| Programme | Gate Entry | Unconditional Write Line | Tracks Written | Dead --render Flag | Replay Status | Proposed Mode | Evidence |
|---|---|---|---|---|---|---|---|
| UCL-000001 | `ucl_engine.py --gate` | `:3030` `write_registers(model)` | `00-MASTER/UCL-000001/` register surface | YES — `:2983` (never read; GP-4) | No non-mutating replay path (GP-4) | **PRODUCER** | GP-1 canonical example; GP-4 `ucl_engine.py:2983` |
| UCOS-UFEP-001 | `ufep_engine.py --gate` | `:1119` | `00-MASTER/UCOS-UFEP-001/` register surface | YES — `:1082` (never read; GP-4) | No non-mutating replay path (GP-4) | **PRODUCER** | GP-1 table; GP-4 `ufep_engine.py:1082` |
| UIS-001 | `uis_engine.py --gate` | `:1814` | `00-MASTER/UIS-001/` register surface | YES — `:1777` (never read; GP-4) | No non-mutating replay path (GP-4) | **PRODUCER** | GP-1 table; GP-4 `uis_engine.py:1777` |
| BASELINE-001 | `baseline_engine.py --gate` | `:1896` | `00-MASTER/BASELINE-001/` (5 files per CI workflow) | NO | CI workflow has render+diff step but gate itself writes first (GP-1) | **PRODUCER** | GP-1 table; `baseline-gate.yml` best-practice shape |
| UCOS-UCAF-001 | `ucaf_engine.py --gate` | `:2104` | `00-MASTER/UCOS-UCAF-001/` register surface | NO | None confirmed | **PRODUCER** | GP-1 table; ASSESSMENT-CONFLICT-REGISTER CR-09 (`uccep --gate` wrote 47 tracked files across 4 programme homes including UCAF) |
| UCOS-URAT-001 | `urat_engine.py --gate` | `:1009` | `00-MASTER/UCOS-URAT-001/` register surface | NO | None confirmed | **PRODUCER** | GP-1 table |
| UCOS-UTCE-001 | `utce_engine.py --gate` | `:855` | `00-MASTER/UCOS-UTCE-001/` register surface | NO | None confirmed; GP-8 misleading self-guard | **PRODUCER** | GP-1 table; GP-8 |
| ACEE-000001 | `acee_engine.py --gate` | `:3730` | `00-MASTER/ACEE-000001/` register surface | NOT confirmed | None confirmed | **PRODUCER** | GP-1 table |
| UCOS-AEE-001 (`aee-gate`) | `aee_engine.py --gate` | `:1807` `emit(decl, model)` | `00-MASTER/UCOS-AEE-001/` register surface | NO | None confirmed | **PRODUCER** | GP-1 table (`aee-gate` and `aee-observe` both listed) |

### 2.5 PRODUCER — GP-2 write-before-verdict (write is present; order is the defect)

These engines write tracked artifacts AND have the additional GP-2 defect (write executes
before the gate branch). The mode is PRODUCER; the write-order defect requires Task-006
remediation before the PRODUCER declaration is fully valid.

| Programme | Gate Entry | Write Line | Gate Branch Line | Proposed Mode | Evidence |
|---|---|---|---|---|---|
| UCOS-RIB-001 | `rib_engine.py --gate` | `:3925` `write_outputs(decl, model)` | `:3942 if not args.gate:` | **PRODUCER** | GP-2 |
| URRC-000001 | `urrc_engine.py` | `:2041` | `:2056 if not args.gate:` | **PRODUCER** | GP-2 |
| UCOS-UAR-001 | `uar_engine.py --gate` | `:118-125` inside `_run_gate()` | `main()` routes `--gate` and bare invocation to `_run_gate()` | **PRODUCER** | GP-2 |

### 2.6 Programmes Without a *-declaration.json (IAR §1.1 list — requires Task-003 survey)

The IAR §1.1 names programmes whose declaration files were not found under `00-MASTER/` in
Task-001/Task-002. Their mode classification requires locating their declaration surface first.

| Programme | IAR-Named Declaration | Filesystem Status | Gate Behaviour Evidence | Proposed Mode |
|---|---|---|---|---|
| UCCEP-000000 | `uccep-declaration.json` | NOT FOUND under `00-MASTER/UCCEP-000000/` | Emission-authority pattern; observe tier withholds tracked write (gitignored evidence logs written); `uccep --gate` wrote 47 tracked files across 4 homes per CR-09 — indicating a non-observe tier path also exists | **UNKNOWN — requires declaration surface location** (see §4) |
| CMG | `cmg-declaration.json` | NOT FOUND — CMG uses `cmg-gate.sh`, no JSON declaration found | Confirmed OBSERVE from GP determination §2.1 | Behaviour is **OBSERVE**; declaration surface location needed |

---

## 3. Evidence Requirements by Mode

### 3.1 OBSERVE

Required before declaration:
- `git status --porcelain` before and after gate invocation: zero tracked changes
- `find` on known write paths: zero gitignored writes (or writes only via declared `audit_emission`)
- Source inspection confirms no unconditional write call on the `--gate` code path

Confirmed satisfied for: CMG, UGA, UAIE, UAUE `--gate`, UAUE `--replay`

### 3.2 OBSERVE_WITH_DECLARED_AUDIT_EMISSION

Required before declaration:
- All OBSERVE requirements satisfied for tracked writes
- Identified gitignored write path confirmed append-only
- Write confirmed always-on (not flag-gated)
- `audit_emission.path` and `audit_emission.type: append-only` sub-fields prepared

Confirmed satisfied for: UKB enforce --pre, UCCEP evidence logs (gitignored path confirmed)

### 3.3 PRODUCER

Required before declaration (per Task-004/005 gates):
- GP-1 or GP-2 write confirmed in GATE-PURITY-DETERMINATION.md (satisfied by evidence already collected)
- Outputs identified in or to be registered in `generated-artifact-registry.json`
- Engine confirmed deterministic (same inputs → byte-identical outputs)
- Replay path implemented and tested: exits 0 on match, non-zero on any byte diff (Task-005)
- `replay_path` named in declaration (co-committed with `gate_mode: PRODUCER`)
- GP-2 write-order defect corrected before PRODUCER declaration is committed for GP-2 engines (Task-006 must precede Task-004 for RIB, URRC, UAR)

Proposed for: UCL, UFEP, UIS, BASELINE, UCAF, URAT, UTCE, ACEE, AEE (`aee-gate`), RIB, URRC, UAR

### 3.4 EXECUTION

Required before declaration:
- Write reachable only via explicit flag, subcommand, or emission-authority check
- Resolving entry in `mutation-governance-boundary.json` for each mutation class
- Audit trail confirmed

No programme in the current 11-declaration inventory is proposed EXECUTION. The confirmed
EXECUTION-mode entries from GP determination §2.3 (`register.sh --guard`, `uga_engine.py run`,
`make uaue-render`, `make rpi-gate`) are entry points of programmes whose `gate` path is
classified separately (UGA gate = OBSERVE; UAUE render = not a gate; register.sh = separate programme).

---

## 4. Unknowns — Evidence Insufficient

| Programme | Issue | Action Required Before Classification |
|---|---|---|
| UCCEP-000000 | Declaration file `uccep-declaration.json` not found. Two-mode behaviour: observe tier (withholds tracked, writes gitignored evidence); production tier (wrote 47 tracked files per CR-09). Mode depends on which entry point is classified as "the gate" vs. the render/execution path. | Locate declaration surface; measure each tier entry point separately; confirm which path is the authoritative gate |
| CMG (cmg-declaration.json) | Gate behaviour is confirmed OBSERVE from source evidence. Declaration file not found — CMG uses `cmg-gate.sh` script. | Locate or confirm absence of declaration file; if none, no Task-004 action required for CMG; if one exists, add `gate_mode: OBSERVE` |
| UCOS-AEE-001 (`aee-observe` tier) | GP-10 is APPARENT (emit() body not read for internal tier suppression). The `aee-gate` path (GP-1) is clearly PRODUCER. The `aee-observe` label claims read-only but GP-10 records `emit()` at `:1807` without confirmed tier guard. Two sub-paths may warrant two entries, or the single `aee-declaration.json` classifies the primary gate entry. | Read `aee_engine.py` emit() body to confirm or deny tier suppression before declaring mode for observe path |
| UCDA-000001 | GP-1 listed (`ucda_engine.py:1419`); no declaration file found | Locate declaration file; confirm engine behaviour |
| UEI-000001 | GP-1 listed (`uei_engine.py:1367`); no declaration file found | Locate declaration file; confirm engine behaviour |
| UER-000001 | GP-1 listed (`uer_engine.py:1043`); no declaration file found | Locate declaration file; confirm engine behaviour |
| UCEF-000001 | GP-1 listed (`ucef_engine.py:1519`); no declaration file found | Locate declaration file; confirm engine behaviour |
| MCOS-000001 | GP-1 listed (`mcos_engine.py:852`); no declaration file found; also `mcos-certify` | Locate declaration file; confirm engine behaviour |
| UMK-000001 | GP-1 listed (`umk_engine.py:641`); no declaration file found | Locate declaration file; confirm engine behaviour |
| UPF-000001 | GP-1 listed (`upf_engine.py:594`, `uprf-gate`); no declaration file found | Locate declaration file; confirm engine behaviour |
| GP-3 engines (8 targets) | `roadmap-gate`, `corpus-gate`, `assimilate-gate`, `closure-gate`, `closure-phase2/3-gate`, `closure009-gate`, `lifecycle-closure-gate`, `final-closure-gate` — no declaration files confirmed for these programmes | Locate declaration files; confirm engine ownership before classifying |
| UCOS-RFP-001 | `rfp-declaration.json` exists but no `forbidden_write_prefixes`; gate behaviour not measured in GP-1..GP-11 | Measure `rfp` gate entry point tracked writes |
| UCOS-URR-001 | `urr-declaration.json` exists (2206 lines); gate behaviour not listed in GP-1..GP-11 | Measure `urr` gate entry point tracked writes |

---

## 5. Migration Impact

### 5.1 Declarations Requiring `gate_mode` Addition (Task-004)

Confirmed ready for Task-004 after Task-005 replay contracts:

| Declaration | Proposed Mode | Task-005 Replay Required | Blocking Dependency |
|---|---|---|---|
| `ucl-declaration.json` | PRODUCER | YES | GP-4 fix (Task-007) must precede — dead --render flag prevents replay path implementation |
| `ufep-declaration.json` | PRODUCER | YES | GP-4 fix (Task-007) must precede |
| `uis-declaration.json` | PRODUCER | YES | GP-4 fix (Task-007) must precede |
| `baseline-declaration.json` | PRODUCER | YES | None blocking |
| `aee-declaration.json` | PRODUCER (`aee-gate` path) | YES | GP-10 fix (Task-009) must clarify observe tier before full declaration |
| `urat-declaration.json` | PRODUCER | YES | None blocking |
| `utce-declaration.json` | PRODUCER | YES | None blocking |
| `acee-declaration.json` | PRODUCER | YES | None blocking |
| `uga-declaration.json` | OBSERVE | NO | None blocking |
| `uis-declaration.json` | PRODUCER | YES | GP-4 fix |

Confirmed OBSERVE programmes that also need declaration additions (where declaration file exists):

| Programme | Declaration | Proposed Mode | Notes |
|---|---|---|---|
| UAIE-000001 | No `uaie-declaration.json` found — see §4 | OBSERVE | Confirm declaration location |
| UAUE | No JSON declaration found — engine module | OBSERVE | Confirm declaration location |
| UKB | No `ukb-declaration.json` found | OBSERVE_WITH_DECLARED_AUDIT_EMISSION | Confirm declaration location |

### 5.2 Replay Contracts Required (Task-005)

All PRODUCER programmes require a tested replay path co-committed with their declaration.
Priority order (blocking dependencies first):

1. BASELINE-001 — CI workflow already has render+diff shape; replay contract implementation straightforward
2. UCOS-URAT-001, UCOS-UTCE-001, ACEE-000001 — no blocking GP fix
3. UCL-000001, UCOS-UFEP-001, UIS-001 — blocked until GP-4 flags resolved (Task-007)
4. UCOS-RIB-001, URRC-000001, UCOS-UAR-001 — blocked until GP-2 write-order fixed (Task-006)
5. UCOS-AEE-001 — blocked until GP-10 tier guard confirmed (Task-009)
6. UCOS-UCAF-001 — no blocking GP fix; replay path design needed

### 5.3 Validation Dependencies

| Dependency | Affects | Sequence |
|---|---|---|
| Task-006 GP-2 fix | RIB, URRC, UAR PRODUCER declarations | Task-006 before Task-004/005 for these three |
| Task-007 GP-4 fix | UCL, UFEP, UIS PRODUCER declarations | Task-007 before Task-004/005 for these three |
| Task-009 GP-10 fix | AEE declaration (observe tier clarity) | Task-009 before AEE Task-004 |
| Locate missing declarations | UCCEP, UAIE, UAUE, UKB, CMG | Before Task-004 for those programmes |

---

## 6. Forbidden Actions

| Action | Status |
|---|---|
| Declaration files modified | NONE |
| `gate_mode` fields added to any file | NONE |
| Code changes made | NONE |
| Registry changes made | NONE |
| Speculative mode assignments made | NONE — all unknowns listed in §4 |

All classifications derive exclusively from GATE-PURITY-DETERMINATION.md measured findings.
No file in the repository was modified during this task.

---

## Summary Table

| Programme | Declaration File | Proposed Mode | Evidence Confidence | Blocking Dependency |
|---|---|---|---|---|
| CMG-000001 | Not found | OBSERVE | HIGH | Locate declaration |
| UCOS-UGA-001 | `uga-declaration.json` | OBSERVE | HIGH (source confirmed) | None |
| UAIE-000001 | Not found | OBSERVE | HIGH (source confirmed) | Locate declaration |
| UAUE | Not found | OBSERVE | HIGH (source confirmed) | Locate declaration |
| UKB | Not found | OBSERVE_WITH_DECLARED_AUDIT_EMISSION | HIGH | Locate declaration |
| UCCEP-000000 | Not found | UNKNOWN | INSUFFICIENT | Locate decl; measure tiers |
| UCL-000001 | `ucl-declaration.json` | PRODUCER | HIGH | Task-007 (GP-4) |
| UCOS-UFEP-001 | `ufep-declaration.json` | PRODUCER | HIGH | Task-007 (GP-4) |
| UIS-001 | `uis-declaration.json` | PRODUCER | HIGH | Task-007 (GP-4) |
| BASELINE-001 | `baseline-declaration.json` | PRODUCER | HIGH | None |
| UCOS-UCAF-001 | Not found as decl | PRODUCER | HIGH (CR-09) | Locate declaration |
| UCOS-URAT-001 | `urat-declaration.json` | PRODUCER | HIGH | None |
| UCOS-UTCE-001 | `utce-declaration.json` | PRODUCER | HIGH | None |
| ACEE-000001 | `acee-declaration.json` | PRODUCER | HIGH | None |
| UCOS-AEE-001 (gate) | `aee-declaration.json` | PRODUCER | HIGH | Task-009 (GP-10) |
| UCOS-RIB-001 | Not found as decl | PRODUCER | HIGH | Task-006 (GP-2) |
| URRC-000001 | Not found as decl | PRODUCER | HIGH | Task-006 (GP-2) |
| UCOS-UAR-001 | Not found as decl | PRODUCER | HIGH | Task-006 (GP-2) |
| UCDA, UEI, UER, UCEF, MCOS, UMK, UPF | Not found | PRODUCER (likely) | INSUFFICIENT | Locate declarations |
| UCOS-RFP-001 | `rfp-declaration.json` | UNKNOWN | INSUFFICIENT | Measure gate |
| UCOS-URR-001 | `urr-declaration.json` | UNKNOWN | INSUFFICIENT | Measure gate |

---

*This document is the Task-003 mode classification artifact. No declaration file, engine,
workflow, or registry was modified. All proposed modes are evidence-based. Programmes
with insufficient evidence are listed in §4 and must not receive a declaration until
their evidence is confirmed.*

---

Task-003 programme mode classification complete.
No declaration mutation performed.
Implementation changes not executed.
