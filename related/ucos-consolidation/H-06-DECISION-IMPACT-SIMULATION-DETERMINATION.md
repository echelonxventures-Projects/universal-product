# H-06 DECISION IMPACT SIMULATION DETERMINATION

| Field | Value |
|---|---|
| **Authority** | NONE — SIMULATION ONLY. No policy selected. No implementation authorized. |
| **Phase** | Foundation Closure — Mutation Governance Boundary Resolution |
| **Baseline** | HEAD `1f869865` · branch `integration/recovery-001` |
| **Sources** | GP-1..GP-11 · H-06-MUTATION-GOVERNANCE-OWNER-DECISION-RECORD.md · H-06-OPTION-COMPARISON-MATRIX.md · H-06-DECISION-BOUNDARY-VALIDATION.md |
| **Status** | SIMULATION COMPLETE — AWAITING OWNER DECISION |

---

## 1. Decision Readiness

H-06 is ready for owner decision on the primary question (Option A vs Option B).

**Ready:**
- GP-1 through GP-11 fully assessed with evidence
- Authority surfaces identified and surveyed (mutation-governance-boundary.json, 11 *-declaration.json files, generated-artifact-registry.json)
- No mode field exists in any current declaration — confirmed by survey
- Option A and Option B fully analysed with governance, technical, freeze, and risk dimensions
- Reference implementations for each mode exist in the repository and are cited
- Comparison matrix produced across 10 dimensions without scoring or recommendation

**Not yet resolved (must close before ratification, not before decision):**

| ID | Item | Type |
|---|---|---|
| R-1 | GP-6: stage 1b / `.gitignore` `!`-negation collision unverified | Evidence gap |
| R-2 | EXECUTION audit trail destination unspecified | Sub-decision |
| R-3 | `gate_mode` field name not ratified (record uses this as a placeholder) | Sub-decision |
| R-4 | Grandfathering policy for undeclared-mutation engines during migration window | Sub-decision |

R-1 through R-4 do not block the owner from recording their Option A/B selection. They must be resolved before implementation is authorized.

---

## 2. Option A Consequences — Complete

### Governance

The constitutional rule becomes: `*-gate` = write-free measurement, universally and without exception. The word "gate" in UCOS acquires a single, enforceable meaning. Any entry point that writes is not a gate — it is a producer, executor, or generator, and must be named and declared as such. The rule is enforced by naming convention, not by per-engine declaration discipline.

OBSERVE_WITH_DECLARED_AUDIT_EMISSION becomes the only permitted exception: an always-on, append-only write to a declared gitignored audit path is permissible on a gate path when the exception is listed in the programme's declaration. This is a sub-classification of OBSERVE, not a separate mode.

### Technical Impact

Engines requiring write/gate separation (GP-1 class — 15 confirmed + 3 GP-2):

| Engine | Location | Current defect |
|---|---|---|
| ucl_engine.py | 00-MASTER/UCL-000001/ | GP-1: unconditional write at :3030 |
| ufep_engine.py | 00-MASTER/UCOS-UFEP-001/ | GP-1: unconditional write at :1119 |
| uis_engine.py | 00-MASTER/UIS-001/ | GP-1: unconditional write at :1814 |
| baseline_engine.py | 00-MASTER/BASELINE-001/ | GP-1: unconditional write at :1896 |
| ucaf_engine.py | 00-MASTER/UCOS-UCAF-001/ | GP-1: unconditional write at :2104 |
| urat_engine.py | 00-MASTER/UCOS-URAT-001/ | GP-1: unconditional write at :1009 |
| utce_engine.py | 00-MASTER/UCOS-UTCE-001/ | GP-1: unconditional write at :855 |
| acee_engine.py | 00-MASTER/ACEE-000001/ | GP-1: unconditional write at :3730 |
| ucda_engine.py | 00-MASTER/UCDA-000001/ | GP-1: unconditional write at :1419 |
| uei_engine.py | 00-MASTER/UEI-000001/ | GP-1: unconditional write at :1367 |
| uer_engine.py | 00-MASTER/UER-000001/ | GP-1: unconditional write at :1043 |
| ucef_engine.py | 00-MASTER/UCEF-000001/ | GP-1: unconditional write at :1519 |
| aee_engine.py | 00-MASTER/UCOS-AEE-001/ | GP-1: unconditional write at :1807; GP-10: observe alias |
| mcos_engine.py | 00-MASTER/MCOS-000001/ | GP-1: unconditional write at :852 |
| umk_engine.py | 00-MASTER/UMK-000001/ | GP-1: unconditional write at :641 |
| upf_engine.py | 00-MASTER/UPF-000001/ | GP-1: unconditional write at :594 |
| rib_engine.py | 00-MASTER/UCOS-RIB-001/ | GP-2: write before gate branch at :3925 |
| urrc_engine.py | 00-MASTER/URRC-000001/ | GP-2: write before gate branch at :2041 |
| uar_engine.py | 00-MASTER/UCOS-UAR-001/ | GP-2: write inside gate function _run_gate() |

CI workflows requiring explicit render steps added (GP-3 class — 8 targets, plus workflows for all GP-1 engines): ucl-gate.yml, rib-gate.yml, ucef-gate.yml, mcos-gate.yml, aee-gate.yml, closure009-gate.yml, assimilation-gate.yml, corpus-currency-gate.yml, urat/utce/ucaf gate workflows. Minimum affected: 15. roadmap-gate.yml:81 `git checkout` workaround (GP-7) becomes unnecessary.

verify.sh: stage 1b must be explicitly labelled as a generation stage. Stage 4 label must be corrected to OBSERVE_WITH_DECLARED_AUDIT_EMISSION.

### Freeze Impact

| Condition | After Option A complete | Dependency |
|---|---|---|
| Mutation boundaries declared | YES | All 46 gate targets separated; modes universal |
| Replay integrity proven | YES | Gate/render separation makes replay unambiguous |
| Evidence chain trustworthy | YES | Gate paths write nothing; evidence cannot be self-contaminated |

All three gate-purity freeze conditions become satisfiable after implementation. Timeline depends on implementation authorization and execution of changes in ≥18 engines and ≥15 workflows.

### Evidence Trust

Highest ceiling. A verified OBSERVE gate cannot have measured a state it altered. GP-2 write-before-verdict defect is also closed, so no gate can report a verdict about a state that no longer existed when the verdict was formed.

### Remaining Dependencies After Option A

- GP-2 (3 engines) and GP-10 (aee-observe) require code changes — these are structural defects, not mode questions
- R-1 GP-6 collision verification must be resolved
- R-2 EXECUTION audit trail destination must be specified
- Grandfathering policy required for migration window
- Remaining freeze blockers H-01..H-05 and R-B1..R-B5 are independent

### Hidden Architecture Dependencies

None. Option A requires no new universe, capability, registry, or authority surface. The naming convention is the enforcement mechanism. Existing self-guard (`--check-declaration`) enforces write-scope already; it would enforce write-zero on gate paths without new infrastructure.

---

## 3. Option B Consequences — Complete

### Governance

The constitutional rule becomes: every programme declares exactly one gate mode in its `*-declaration.json`. OBSERVE, PRODUCER, and EXECUTION are valid modes. Undeclared mutation remains the defect class and is prohibited. The word "gate" names the primary entry point; mode is a property of the declaration, not of the name.

PRODUCER mode: the gate path writes deterministic derived artifacts; outputs are registered in `generated-artifact-registry.json`; a replay path exists; the engine is deterministic.

EXECUTION mode: the gate path performs a controlled state transition; mutation class resolves to a named authority in `mutation-governance-boundary.json`; an explicit flag or subcommand is required; an audit trail exists.

OBSERVE_WITH_DECLARED_AUDIT_EMISSION remains a sub-classification of OBSERVE for always-on gitignored audit writes.

### Declaration Model Impact

All 11 existing `*-declaration.json` files require an additive `gate_mode` field. This is a non-breaking extension — no existing field is changed or removed. The `--check-declaration` self-guard already reads the declaration at runtime; enforcement of the new field requires only that the guard validate its presence and value.

Each PRODUCER declaration must additionally name:
- Output scope (which files are written)
- Replay path (how byte-comparison is performed)
- Registration reference (pointer into `generated-artifact-registry.json`)

Each EXECUTION declaration must name:
- Mutation class (resolving to `mutation-governance-boundary.json`)
- Invocation gate (flag or subcommand)
- Audit destination (R-2 — currently unspecified)

### Replay Implications

Replay is a hard co-obligation of PRODUCER classification. If PRODUCER declarations are ratified without simultaneously enforcing replay contracts, Option B formalises the current defect:

- 8 `*-replay` targets currently write before comparing (GP-3) — these must implement regenerate-in-memory + byte-compare
- 3 dead `--render` flags (GP-4: ucl, ufep, uis) must be wired to an actual write-suppressed replay path
- The `baseline-gate.yml` shape (gate writes; explicit replay step compares; `git diff --exit-code`) is the existing reference implementation to adopt

### Technical Impact

Code changes required under Option B (smaller set than Option A):
- GP-2: 3 engines (rib_engine, urrc_engine, uar_engine) — write-before-verdict ordering
- GP-10: aee_engine.py — emit() must be suppressed on `--tier observe`
- GP-3: ≥8 replay targets — regenerate-in-memory path required
- GP-4: 3 engines (ucl, ufep, uis) — dead `--render` flags must be wired

Declaration changes: 11 `*-declaration.json` files — additive field addition.

### Freeze Impact

| Condition | After Option B complete | Dependency |
|---|---|---|
| Mutation boundaries declared | YES — if all 46 gates carry verified mode declarations | Requires declaration changes + enforcement |
| Replay integrity proven | YES — conditional on replay co-obligation enforcement | PRODUCER declarations must include verified replay paths |
| Evidence chain trustworthy | CONDITIONAL | OBSERVE-mode gates: YES. PRODUCER-mode gates: YES if replay verified. Without replay, PARTIAL. |

The conditional on evidence trust is the critical difference from Option A. If replay co-obligation slips, evidence trust for PRODUCER engines remains partial.

### Evidence Trust

Mode-dependent. OBSERVE gates: same ceiling as Option A. PRODUCER gates: trustworthy only when determinism is measured and replay is verified. The gap between "PRODUCER declared" and "PRODUCER evidence trustworthy" requires replay verification to close. This is a process discipline requirement, not an architectural one.

### Remaining Dependencies After Option B

- GP-2 (3 engines) and GP-10 (aee-observe) require code changes regardless
- Replay contracts for all PRODUCER programmes must be implemented as a co-obligation
- R-1 GP-6 collision verification must be resolved
- R-2 EXECUTION audit trail destination must be specified
- R-3 field name must be ratified
- Mode inflation prevention criteria must be defined (what qualifies a gate as PRODUCER vs OBSERVE)
- Remaining freeze blockers H-01..H-05 and R-B1..R-B5 are independent

### Hidden Architecture Dependencies

None. Option B requires no new universe, capability, registry, or authority surface. PRODUCER mode points into existing `generated-artifact-registry.json`. EXECUTION mode points into existing `mutation-governance-boundary.json`. Mode declaration sits in existing `*-declaration.json` files. The only new artifact is an additive field in an existing schema.

---

## 4. Common Requirements

The following apply under either option. They are structural or evidence defects, not policy questions.

| Item | Type | Engines/Files | Notes |
|---|---|---|---|
| GP-2 write-order correction | Code defect | rib_engine.py, urrc_engine.py, uar_engine.py | Write before verdict is wrong under any mode |
| GP-10 aee-observe emit() suppression | Code defect | aee_engine.py | Read-only label is false under any mode |
| GP-5 verify.sh stage 4 label correction | Label correction | verify.sh:139-141 | OBSERVE_WITH_DECLARED_AUDIT_EMISSION |
| GP-3 replay regenerate-before-write | Implementation | ≥8 targets | Required under both options |
| GP-4 dead --render flags wired | Code fix | ucl, ufep, uis engines | Required under both options |
| R-1 GP-6 collision verification | Evidence collection | closure_engine.py | Read-only; no implementation required |
| R-2 EXECUTION audit destination | Sub-decision | Any EXECUTION-mode programme | Must be specified before EXECUTION declared |
| R-3 field name ratification | Sub-decision | All *-declaration.json | Placeholder `gate_mode` must be confirmed |
| Grandfathering policy | Sub-decision | 24 undeclared engines | What is the compliance state during migration? |

---

## 5. Remaining Unknowns

| Unknown | Impact | Blocks owner decision? |
|---|---|---|
| R-1: GP-6 stage 1b collision | If collision exists, stage 1b dirties tracked files on every run; generate-prerequisites.sh claim is false | NO — does not change Option A/B choice |
| R-2: EXECUTION audit destination | No programme can be declared EXECUTION until this is specified | NO — does not change Option A/B choice |
| R-3: gate_mode field name | Placeholder — subject to ratification | NO — naming is a sub-decision after the primary choice |
| R-4: Grandfathering policy | Without it, 24 engines are in violation from day 1 of migration | NO — does not change Option A/B choice |
| Mode inflation criteria (Option B only) | Without qualifying criteria, PRODUCER can be claimed to avoid write discipline | NO — criteria can be defined during ratification |

---

## 6. Freeze Dependency Impact

H-06 decision alone satisfies zero freeze conditions. It enables the implementation authorization that permits satisfaction.

```
H-06 owner decision recorded
        ↓
R-1..R-4 resolved during ratification
        ↓
Mode vocabulary ratified
        ↓
Implementation authorized (separate step)
        ↓
[Option A] ≥18 engine code changes +    [Option B] 11 declaration file updates +
≥15 CI workflow changes                  replay paths per PRODUCER +
                                         GP-2/GP-10 code changes
        ↓
Gate purity freeze conditions assessed:
  (1) Mutation boundaries declared  → YES
  (2) Replay integrity proven        → YES
  (3) Evidence chain trustworthy     → YES (Option A unconditional;
                                           Option B conditional on replay)
        ↓
Foundation Freeze eligibility re-assessed
        ↓
Remaining blockers addressed independently:
H-01..H-05 (CANONICAL-AUTHORITY-DETERMINATION.md §6.2)
R-B1..R-B5 (FINAL-FREEZE-READINESS-DETERMINATION.md §4.1)
```

Gate purity closure satisfies one dimension of Foundation Freeze. The remaining registered decisions are outside the scope of H-06.

---

## 7. Information Required for Owner Decision

The owner already has all information required to record an Option A or Option B selection. For completeness, the following represents the complete package:

**Already available:**
- GP-1 through GP-11 with evidence, classification, and engine-level specifics
- Both options defined with invariants, benefits, risks, migration impact
- Comparison matrix across 10 dimensions (H-06-OPTION-COMPARISON-MATRIX.md)
- Mode vocabulary (OBSERVE, PRODUCER, EXECUTION, OBSERVE_WITH_DECLARED_AUDIT_EMISSION) with definitions and property tables
- Existing authority surface survey (mutation-governance-boundary.json, 11 declarations, generated-artifact-registry.json)
- Confirmation that neither option requires new architecture
- Freeze dependency chain with explicit sequencing
- Confirmation that GP-2 and GP-10 are code defects requiring fixes under either option

**Required before ratification (not before decision):**
- R-1: GP-6 collision verification result
- R-2: EXECUTION audit trail destination specification
- R-3: Confirmed field name for gate mode in declaration schema
- R-4: Grandfathering policy for 24 undeclared-mutation engines during migration

---

No option selected.
No implementation authorized.
Awaiting Mutation Governance Owner decision.
