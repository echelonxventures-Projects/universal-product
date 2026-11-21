# REPOSITORY CLOSURE WAVES

**Artifact ID**: UCOS-CLOSURE-WAVES-001  
**Date**: 2026-09-01  
**Authority**: PHASE E3 — CLOSURE WAVES  
**Scope**: All 33 producers organized into executable waves

---

## OBJECTIVE

Create executable closure waves that convert all 33 producers from OPEN → CERTIFIED.

**Wave Principles**:
1. Every producer belongs to exactly one wave
2. Waves execute sequentially (wave N+1 cannot start until wave N completes)
3. Producers within a wave execute in parallel
4. Dependencies between waves are explicit and measurable

---

## WAVE STRUCTURE

### Wave 0: Governance Prerequisites

**Goal**: Establish governance infrastructure that all subsequent waves depend on

**Scope**: Repository-wide governance mechanisms

**Deliverables**:
1. **CODEOWNERS for authority files** (2 hours)
   - Add entries for all authority sources
   - Ensure constitutional files require review

2. **Registry invariant enforcement** (4-8 hours)
   - Implement stage-registry-invariants in verify.sh
   - Enforce MB19, MB21 (false positives but prevent future violations)
   - Foundation for MB18, MB20, MB24 detection

3. **Evidence-universe.json audit** (8-12 hours)
   - Complete MB20 measurement (certification vs evidence class)
   - Classify all evidence surfaces
   - Enable evidence-based validation

**Duration**: 14-22 hours

**Blockers**: None

**Outcome**: Governance infrastructure ready for producer-specific work

**Status**: NOT STARTED

---

### Wave 1: Authority Externalization

**Goal**: Identify and document authority sources for all 32 OPEN producers

**Scope**: All producers except UCOS-UCTX-001 (already complete)

**Work Per Producer** (2-4 hours):
1. Enumerate input files that define correct output
2. Classify as AUTHORED vs GENERATED authority
3. Document constitutional superior (if applicable)
4. Create authority manifest (JSON)

**Producers** (32):
- ACEE-000001, BASELINE-001, MCOS-000001, P0-LIFECYCLE-CLOSURE-001
- UAIE-000001, UAKOS-CLOSURE-008, UAKOS-CLOSURE-009, UAKOS-PHASE-001A-R1
- UAKOS-PHASE-003R, UAUE-000001, UCDA-000001, UCEF-000001
- UCL-000001, UCOS-AEE-001, UCOS-MXR-001, UCOS-NUCLEUS-001
- UCOS-RIB-001, UCOS-RIE-001, UCOS-UAR-001, UCOS-UCAF-001
- UCOS-UFEP-001, UCOS-UGA-001, UCOS-URAT-001, UCOS-USIS-WAVE0
- UCOS-UTCE-001, UEI-000001, UER-000001, UIS-001
- UKAP-001, UMK-000001, UPF-000001, URRC-000001

**Duration**: 64-128 hours (32 producers × 2-4 hours)

**Parallelization**: 4 workers = 16-32 hours = 2-4 working days

**Dependencies**: Wave 0 (CODEOWNERS established)

**Outcome**: Every producer has documented authority corpus

**Status**: NOT STARTED

---

### Wave 2: Independent Validator Creation (MB7 Closure)

**Goal**: Create independent validators for all 32 OPEN producers

**Scope**: All producers except UCOS-UCTX-001

**Work Per Producer** (6-10 hours):
1. Choose validator architecture (provenance, equivalence, or invariant)
2. Implement validator (does not import/run generator)
3. Write validator tests
4. Document validation strategy

**Producer Groups**:

**Group 2A: CRITICAL (2 producers)**
- UCOS-RIB-001 (50+ artifacts, build intelligence)
- UCOS-RIE-001 (40+ artifacts, intelligence surfaces)

**Group 2B: HIGH (5 producers)**
- UAIE-000001 (architectural intelligence, 12 artifacts)
- UCOS-AEE-001 (evolution engine, 18 artifacts)
- UCOS-UGA-001 (governance attestation, constitutional claims)
- UCOS-UAR-001 (artifact registry, 12 artifacts)
- UCOS-URAT-001 (relationship registry, 12 artifacts)

**Group 2C: MEDIUM (18 producers)**
- ACEE-000001, MCOS-000001, P0-LIFECYCLE-CLOSURE-001
- UAKOS-CLOSURE-008, UAKOS-CLOSURE-009, UAKOS-PHASE-001A-R1
- UAKOS-PHASE-003R, UAUE-000001, UCL-000001
- UCOS-MXR-001, UCOS-NUCLEUS-001, UCOS-UCAF-001
- UCOS-USIS-WAVE0, UCOS-UTCE-001
- UEI-000001, UER-000001, UMK-000001, URRC-000001

**Group 2D: LOW (7 producers)**
- BASELINE-001, UCDA-000001, UCEF-000001
- UCOS-UFEP-001, UIS-001, UKAP-001, UPF-000001

**Duration**: 192-320 hours (32 producers × 6-10 hours)

**Parallelization**: 4 workers = 48-80 hours = 6-10 working days

**Dependencies**: Wave 1 (authority corpus identified)

**Outcome**: 32 independent validators exist

**Status**: NOT STARTED

---

### Wave 3: Attack Reproduction and Verification (MB7 Completion)

**Goal**: Prove independent validators catch uniform wrong output

**Scope**: All 32 newly created validators

**Work Per Producer** (3-5 hours):
1. Create 3 attack variants (invented content, permuted data, truncated output)
2. Run attacks in sandbox
3. Measure self-validation passes (gate_exit=0)
4. Measure independent validator fails (verifier_exit=1)
5. Document closure proof

**Duration**: 96-160 hours (32 producers × 3-5 hours)

**Parallelization**: 4 workers = 24-40 hours = 3-5 working days

**Dependencies**: Wave 2 (validators implemented)

**Outcome**: MB7 closed for all 32 producers (with evidence)

**Status**: NOT STARTED

---

### Wave 4: Bootstrap Integrity Suite (MB14, MB18, MB22, MB23)

**Goal**: Verify reproducibility, regeneration commands, and determinism

**Scope**: All 32 OPEN producers + cross-cutting infrastructure

**Subwave 4A: Bootstrap Graph Construction (MB18)**

**Duration**: 40-60 hours
- Build global dependency graph for GENERATED_DETERMINISTIC inputs
- Detect cycles
- Verify bootstrap completeness
- Implement graph validator

**Parallelization**: 1-2 workers (global analysis)

**Subwave 4B: Fresh-Clone Bootstrap Tests (MB14)**

**Duration**: 64 hours (32 producers × 2 hours)
- Create fresh-clone test per producer
- Verify bootstrap from tracked inputs only
- CI integration

**Parallelization**: 4 workers = 16 hours = 2 working days

**Subwave 4C: Regeneration Command Verification (MB22)**

**Duration**: 96-128 hours (32 producers × 3-4 hours)
- Run regeneration command per producer
- Diff output against current
- Fix discrepancies or update commands
- CI integration

**Parallelization**: 4 workers = 24-32 hours = 3-4 working days

**Subwave 4D: Determinism Verification (MB23)**

**Duration**: 64-96 hours (32 producers × 2-3 hours)
- Run generator twice per producer
- Compare bytes
- Fix non-determinism or downgrade claims
- CI integration

**Parallelization**: 4 workers = 16-24 hours = 2-3 working days

**Total Duration**: 264-348 hours

**Parallelization**: 66-87 hours = 8-11 working days (subwaves partially sequential)

**Dependencies**: Wave 2 (validators exist), Wave 3 (MB7 closed)

**Outcome**: MB14, MB18, MB22, MB23 closed for all producers

**Status**: NOT STARTED

---

### Wave 5: Constitutional Alignment (MB24)

**Goal**: Verify constitutional superior claims

**Scope**: Producers declaring constitutional_superior (~10 producers)

**Identified Producers**:
- UCOS-UGA-001 (constitutional-authority-alignment.json)
- UCOS-UCTX-001 (already complete)
- Registry itself (declares UCKP-LAW-0001)
- Others TBD (requires Wave 1 authority externalization)

**Work Per Producer** (4-8 hours):
1. Identify constitutional_superior declaration
2. Implement alignment verifier
3. Verify claims against superior authority
4. CI integration

**Duration**: 40-80 hours (~10 producers × 4-8 hours)

**Parallelization**: 2 workers = 20-40 hours = 3-5 working days

**Dependencies**: Wave 1 (constitutional superiors identified), Wave 2 (validators exist)

**Outcome**: MB24 closed for all producers with constitutional claims

**Status**: NOT STARTED

---

### Wave 6: CI Integration and Enforcement

**Goal**: Integrate all validators into CI enforcement chain

**Scope**: All 32 newly created validators + cross-cutting stages

**Work**:

1. **Per-Producer CI Stages** (32 producers × 1 hour = 32 hours)
   - Add validator stage to verify.sh
   - Configure stage dependencies
   - Set failure behavior

2. **Cross-Cutting CI Stages** (16-24 hours)
   - stage-registry-invariants (MB18, MB19, MB20, MB21)
   - stage-bootstrap-integrity (MB14, MB18)
   - stage-determinism (MB23)
   - stage-constitutional-alignment (MB24)

3. **UVI Registry Updates** (8-12 hours)
   - Add all stages to UVI-000001/uvi-declaration.json
   - Document stage dependencies
   - Update verification mode definitions

4. **Verification Mode Testing** (16-24 hours)
   - Test --fast, --change, --integration, --full
   - Verify stage selection logic
   - Measure impact on CI runtime

**Total Duration**: 72-92 hours

**Parallelization**: 2 workers = 36-46 hours = 5-6 working days

**Dependencies**: Wave 2 (validators exist), Wave 3 (verified), Wave 4 (bootstrap integrity), Wave 5 (constitutional alignment)

**Outcome**: All validators CI-enforced, cannot be bypassed

**Status**: NOT STARTED

---

### Wave 7: Certification and Documentation

**Goal**: Update registry, produce closure proofs, certify completion

**Scope**: All 32 producers + repository-wide artifacts

**Work**:

1. **Registry Updates** (32-48 hours)
   - Add independent_validation field to all 367 artifacts
   - Document validation strategies
   - Update threat closure status

2. **Closure Proof Documentation** (48-64 hours)
   - Compile attack results per producer
   - Document gate_exit vs verifier_exit outcomes
   - Create per-producer closure certificates

3. **Repository Certification** (24-32 hours)
   - Run full verification suite
   - Measure coverage
   - Generate certification report
   - Update threat registry (MB7-MB24 status)

4. **Knowledge Base Updates** (16-24 hours)
   - Update 00-BOOK registries
   - Document new validation architecture
   - Create operator runbooks

**Total Duration**: 120-168 hours

**Parallelization**: 2 workers = 60-84 hours = 8-11 working days

**Dependencies**: All previous waves (work must be complete before certification)

**Outcome**: Repository certified, all 33 producers CERTIFIED

**Status**: NOT STARTED

---

## WAVE DEPENDENCIES

```
Wave 0 (Governance Prerequisites)
  ↓
Wave 1 (Authority Externalization)
  ↓
Wave 2 (Independent Validators) ──→ Wave 5 (Constitutional Alignment)
  ↓                                      ↓
Wave 3 (Attack Verification)            ↓
  ↓                                      ↓
Wave 4 (Bootstrap Integrity) ───────────┘
  ↓
Wave 6 (CI Integration)
  ↓
Wave 7 (Certification)
```

**Critical Path**: Wave 0 → 1 → 2 → 3 → 4 → 6 → 7  
**Parallel Path**: Wave 5 can run alongside Wave 4

---

## TIMELINE ESTIMATES

### Serial Execution (1 worker)

| Wave | Duration | Days @ 8hr |
|------|----------|------------|
| 0 | 14-22 hrs | 2-3 |
| 1 | 64-128 hrs | 8-16 |
| 2 | 192-320 hrs | 24-40 |
| 3 | 96-160 hrs | 12-20 |
| 4 | 264-348 hrs | 33-44 |
| 5 | 40-80 hrs | 5-10 |
| 6 | 72-92 hrs | 9-12 |
| 7 | 120-168 hrs | 15-21 |

**Total**: 862-1,318 hours = 108-165 working days

---

### Parallel Execution (4 workers)

| Wave | Duration | Days @ 8hr/worker |
|------|----------|-------------------|
| 0 | 14-22 hrs | 2-3 |
| 1 | 16-32 hrs | 2-4 |
| 2 | 48-80 hrs | 6-10 |
| 3 | 24-40 hrs | 3-5 |
| 4 | 66-87 hrs | 8-11 |
| 5 | 20-40 hrs | 3-5 (parallel with Wave 4) |
| 6 | 36-46 hrs | 5-6 |
| 7 | 60-84 hrs | 8-11 |

**Total**: 264-391 hours = 33-49 working days (4 workers)

---

### Aggressive Parallel (8 workers)

| Wave | Duration | Days @ 8hr/worker |
|------|----------|-------------------|
| 0 | 14-22 hrs | 2-3 |
| 1 | 8-16 hrs | 1-2 |
| 2 | 24-40 hrs | 3-5 |
| 3 | 12-20 hrs | 2-3 |
| 4 | 33-44 hrs | 4-6 |
| 5 | 10-20 hrs | 1-3 (parallel with Wave 4) |
| 6 | 18-23 hrs | 2-3 |
| 7 | 30-42 hrs | 4-6 |

**Total**: 149-227 hours = 19-28 working days (8 workers)

---

## RISK MITIGATION

### Wave Failure Scenarios

**Wave 0 Failure**: Governance infrastructure incomplete
- Impact: All subsequent waves blocked
- Mitigation: Simple infrastructure work, low risk
- Recovery: 1-2 days to fix

**Wave 1 Failure**: Authority corpus incomplete or incorrect
- Impact: Wave 2 validators may miss authority sources
- Mitigation: Peer review per producer
- Recovery: Iterate on incorrect producers only

**Wave 2 Failure**: Validator implementation bugs
- Impact: Wave 3 attacks may not be caught
- Mitigation: Validator testing before attack phase
- Recovery: Fix validators, re-run Wave 3

**Wave 3 Failure**: Attacks not caught by validators
- Impact: MB7 not actually closed
- Mitigation: Re-examine validator logic, strengthen attacks
- Recovery: Iterate on failing producers only

**Wave 4 Failure**: Bootstrap/determinism issues discovered
- Impact: Some producers cannot reach CERTIFIED
- Mitigation: Fix generators or downgrade claims
- Recovery: Per-producer remediation

**Wave 6 Failure**: CI integration breaks existing pipelines
- Impact: Repository CI unstable
- Mitigation: Staged rollout, feature flags
- Recovery: Rollback, fix, re-deploy

---

## COORDINATION REQUIREMENTS

### Cross-Wave Communication

- Wave 1 → Wave 2: Authority corpus files must be accessible
- Wave 2 → Wave 3: Validator locations and invocation commands
- Wave 4 → Wave 6: Bootstrap and determinism test commands
- All waves → Wave 7: Closure evidence for certification

### Tooling Requirements

- **Wave 0**: Git, verify.sh modification
- **Wave 1**: JSON editing, documentation
- **Wave 2**: Python development, testing framework
- **Wave 3**: Sandbox environment, diff tools
- **Wave 4**: Test harness, graph analysis tools
- **Wave 6**: CI/CD pipeline access
- **Wave 7**: Documentation generators, registry updaters

---

## SUCCESS METRICS

### Per-Wave Metrics

**Wave 0**: 
- ✓ CODEOWNERS entries added for all authority files
- ✓ stage-registry-invariants passing
- ✓ MB19, MB21 enforced

**Wave 1**:
- ✓ 32/32 producers have authority manifests
- ✓ All manifests peer-reviewed

**Wave 2**:
- ✓ 32/32 producers have independent validators
- ✓ All validators pass their own test suites

**Wave 3**:
- ✓ 32/32 producers have attack reproducers (3 variants each)
- ✓ 96/96 attacks show gate_exit=0, verifier_exit=1

**Wave 4**:
- ✓ Bootstrap graph complete, no cycles
- ✓ 32/32 fresh-clone tests passing
- ✓ 367/367 regeneration commands verified
- ✓ 383/383 determinism claims verified

**Wave 5**:
- ✓ All constitutional_superior declarations verified
- ✓ Alignment verifiers passing

**Wave 6**:
- ✓ 32 validator stages integrated into verify.sh
- ✓ Cross-cutting stages operational
- ✓ All verification modes tested

**Wave 7**:
- ✓ Registry updated with independent_validation fields
- ✓ Closure proofs documented
- ✓ Repository certification report generated
- ✓ 33/33 producers CERTIFIED

---

## REPOSITORY STATE TRANSITIONS

### Start State (Current)

- Producers CERTIFIED: 1/33 (3.0%)
- Producers OPEN: 32/33 (97.0%)
- Independent validators: 1
- CI enforcement stages: 1 (ukctx_verify)

### After Wave 3

- Producers CERTIFIED: 1/33 (still, awaiting CI integration)
- Producers with independent validators: 33/33
- Validators verified: 33/33
- MB7 closed: 33/33

### After Wave 4

- MB14 closed: 33/33
- MB18 closed: 33/33
- MB22 closed: 33/33
- MB23 closed: 33/33

### After Wave 6

- Producers CERTIFIED: 33/33 (100%)
- CI enforcement stages: 33+ (per-producer + cross-cutting)

### Final State (After Wave 7)

- Repository closure rate: 100%
- Threat registry: MB7-MB24 all CLOSED
- Documentation: Complete
- Certification: Repository-wide

---

## WAVE EXECUTION STRATEGY

### Recommended Approach: Parallel 4-Worker Model

**Rationale**:
- Balances speed (33-49 days) vs coordination overhead
- Realistic team size for code review and validation
- Allows staged rollout with early feedback

**Team Structure**:
- Worker 1: CRITICAL producers (UCOS-RIB-001, UCOS-RIE-001)
- Worker 2: HIGH producers (UAIE-000001, UCOS-AEE-001, UCOS-UGA-001, etc.)
- Worker 3: MEDIUM producers (group A)
- Worker 4: MEDIUM producers (group B) + LOW producers

**Weekly Checkpoints**:
- End of Week 1: Wave 0, Wave 1 complete
- End of Week 3: Wave 2 complete
- End of Week 4: Wave 3 complete
- End of Week 6: Wave 4, Wave 5 complete
- End of Week 7: Wave 6 complete
- End of Week 9: Wave 7 complete, repository CERTIFIED

---

## CERTIFICATION

**Wave Design Author**: Kiro (Claude Opus 5)  
**Design Date**: 2026-09-01  
**Method**: Dependency analysis + effort estimation

**Key Principles Maintained**:
- No producer left ambiguous (all 33 assigned)
- Dependencies explicit and measurable
- Parallelization opportunities maximized
- Risk mitigation strategies defined

**Status**: PHASE E3 COMPLETE ✓  
**Next Phase**: E4 — DEPENDENCY DAG
