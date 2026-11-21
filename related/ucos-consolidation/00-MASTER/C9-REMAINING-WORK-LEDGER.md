# C9 — REMAINING WORK LEDGER

**Artifact ID**: UCOS-C9-REMAINING-WORK-001  
**Date**: 2026-09-01  
**Authority**: PHASE C7 REPOSITORY-WIDE CLOSURE EXECUTION AUDIT

---

## SCOPE

This ledger enumerates every measured gap between current state (3.0% certified closure) and target state (100% certified closure) for MB7–MB17.

**Total Work Items**: 158 (from 165 applicable threats - 5 certified - 1 verified - 1 implemented)

---

## MB7: GENERATOR AUTHORITY INDEPENDENCE

**Status**: 32/33 producers OPEN

### Required Work Per Producer

1. **Authority Corpus Identification** (30 min)
   - Enumerate input files that constitute generator authority
   - Document their role and constitutional basis
   - Create authority declaration JSON

2. **Independent Validator Implementation** (2-4 hours)
   - Choose validator architecture (provenance, equivalence, or invariant-based)
   - Implement validator that does NOT import/run the generator
   - Write validator tests

3. **Attack Reproducer Creation** (1-2 hours)
   - Create uniform wrong output variants (minimum 3)
   - Measure self-validation pass (should pass if MB7 exists)
   - Measure independent validator fail (should fail, proving independence)

4. **CI Integration** (30 min)
   - Add validator stage to verify.sh
   - Add to UVI stage registry
   - Verify enforcement in all verification modes

5. **Closure Proof** (30 min)
   - Run attack variants in sandbox
   - Document gate_exit=0, verifier_exit=1 results
   - Update generated-artifact-registry.json with independent_validation field

### Per-Producer Work Items

| Producer | Authority ID | Validator | Reproducer | CI | Proof | Total Hours |
|----------|--------------|-----------|------------|----|----|-------------|
| ACEE-000001 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| BASELINE-001 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| MCOS-000001 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| P0-LIFECYCLE-CLOSURE-001 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| UAIE-000001 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| UAKOS-CLOSURE-008 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| UAKOS-CLOSURE-009 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| UAKOS-PHASE-001A-R1 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| UAKOS-PHASE-003R | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| UAUE-000001 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| UCDA-000001 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| UCEF-000001 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| UCL-000001 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| UCOS-AEE-001 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| UCOS-MXR-001 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| UCOS-NUCLEUS-001 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| UCOS-RIB-001 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| UCOS-RIE-001 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| UCOS-UAR-001 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| UCOS-UCAF-001 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| UCOS-UFEP-001 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| UCOS-UGA-001 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| UCOS-URAT-001 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| UCOS-USIS-WAVE0 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| UCOS-UTCE-001 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| UEI-000001 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| UER-000001 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| UIS-001 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| UKAP-001 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| UMK-000001 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| UPF-000001 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |
| URRC-000001 | ☐ | ☐ | ☐ | ☐ | ☐ | 4.5-8.0 |

**MB7 Total**: 144-256 hours (32 producers × 4.5-8.0 hours)

---

## MB14: FRESH-CLONE BOOTSTRAP DEPENDENCY

**Status**: 32/33 producers UNMEASURED

### Required Work Per Producer

1. **Fresh-Clone Test Creation** (1 hour)
   - Create test that runs in pristine checkout
   - Verify no operational state dependencies
   - Measure bootstrap success

2. **CI Integration** (30 min)
   - Add fresh-clone test to CI pipeline
   - Verify enforcement in all verification modes

3. **Bootstrap Path Verification** (30 min)
   - Audit that generator reads only declared inputs
   - Update generated-artifact-registry.json if gaps found

### Per-Producer Work Items

| Producer | Fresh-Clone Test | CI Integration | Bootstrap Audit | Total Hours |
|----------|------------------|----------------|-----------------|-------------|
| ACEE-000001 | ☐ | ☐ | ☐ | 2.0 |
| BASELINE-001 | ☐ | ☐ | ☐ | 2.0 |
| MCOS-000001 | ☐ | ☐ | ☐ | 2.0 |
| P0-LIFECYCLE-CLOSURE-001 | ☐ | ☐ | ☐ | 2.0 |
| UAIE-000001 | ☐ | ☐ | ☐ | 2.0 |
| UAKOS-CLOSURE-008 | ☐ | ☐ | ☐ | 2.0 |
| UAKOS-CLOSURE-009 | ☐ | ☐ | ☐ | 2.0 |
| UAKOS-PHASE-001A-R1 | ☐ | ☐ | ☐ | 2.0 |
| UAKOS-PHASE-003R | ☐ | ☐ | ☐ | 2.0 |
| UAUE-000001 | ☐ | ☐ | ☐ | 2.0 |
| UCDA-000001 | ☐ | ☐ | ☐ | 2.0 |
| UCEF-000001 | ☐ | ☐ | ☐ | 2.0 |
| UCL-000001 | ☐ | ☐ | ☐ | 2.0 |
| UCOS-AEE-001 | ☐ | ☐ | ☐ | 2.0 |
| UCOS-MXR-001 | ☐ | ☐ | ☐ | 2.0 |
| UCOS-NUCLEUS-001 | ☐ | ☐ | ☐ | 2.0 |
| UCOS-RIB-001 | ☐ | ☐ | ☐ | 2.0 |
| UCOS-RIE-001 | ☐ | ☐ | ☐ | 2.0 |
| UCOS-UAR-001 | ☐ | ☐ | ☐ | 2.0 |
| UCOS-UCAF-001 | ☐ | ☐ | ☐ | 2.0 |
| UCOS-UFEP-001 | ☐ | ☐ | ☐ | 2.0 |
| UCOS-UGA-001 | ☐ | ☐ | ☐ | 2.0 |
| UCOS-URAT-001 | ☐ | ☐ | ☐ | 2.0 |
| UCOS-USIS-WAVE0 | ☐ | ☐ | ☐ | 2.0 |
| UCOS-UTCE-001 | ☐ | ☐ | ☐ | 2.0 |
| UEI-000001 | ☐ | ☐ | ☐ | 2.0 |
| UER-000001 | ☐ | ☐ | ☐ | 2.0 |
| UIS-001 | ☐ | ☐ | ☐ | 2.0 |
| UKAP-001 | ☐ | ☐ | ☐ | 2.0 |
| UMK-000001 | ☐ | ☐ | ☐ | 2.0 |
| UPF-000001 | ☐ | ☐ | ☐ | 2.0 |
| URRC-000001 | ☐ | ☐ | ☐ | 2.0 |

**MB14 Total**: 64 hours (32 producers × 2.0 hours)

---

## MB15: TEMPLATE EXPLOSION RISK

**Status**: 32/33 producers OPEN (estimated 15 text-based, 17 non-text N/A)

### Required Work Per Producer (Text-Based Only)

1. **Output Analysis** (30 min)
   - Identify repeated patterns with variable substitutions
   - Count current templates (or implicit template count)

2. **Normalisation Implementation** (1-2 hours)
   - Implement normalise() function
   - Define MIN_SLOT threshold
   - Test normalisation coverage

3. **Template Manifest Creation** (1 hour)
   - Generate normalised template manifest
   - Document allowed_cells and allowed_lines
   - Verify template count is O(1) per pattern

4. **Verification Integration** (30 min)
   - Implement template verification
   - Integrate into CI
   - Measure coverage

### Per-Producer Work Items (Text-Based Generators Only)

**Estimated Text-Based Producers** (requires output inspection to confirm):
- UAIE-000001 (dashboard generator)
- UAKOS-CLOSURE-008 (registers)
- UAKOS-CLOSURE-009 (registers)
- UAKOS-PHASE-001A-R1 (report generator)
- UAKOS-PHASE-003R (report generator)
- UAUE-000001 (evidence generator)
- UCDA-000001 (dashboard)
- UCEF-000001 (execution framework)
- UCOS-AEE-001 (evolution reports)
- UCOS-NUCLEUS-001 (nucleus reports)
- UCOS-RIB-001 (build intelligence)
- UCOS-RIE-001 (intelligence surfaces)
- UCOS-UCAF-001 (capability framework)
- UCOS-UFEP-001 (execution plans)
- UCOS-UGA-001 (governance attestation)

| Producer | Analysis | Normalisation | Manifest | Verification | Total Hours |
|----------|----------|---------------|----------|--------------|-------------|
| UAIE-000001 | ☐ | ☐ | ☐ | ☐ | 3.0-4.0 |
| UAKOS-CLOSURE-008 | ☐ | ☐ | ☐ | ☐ | 3.0-4.0 |
| UAKOS-CLOSURE-009 | ☐ | ☐ | ☐ | ☐ | 3.0-4.0 |
| UAKOS-PHASE-001A-R1 | ☐ | ☐ | ☐ | ☐ | 3.0-4.0 |
| UAKOS-PHASE-003R | ☐ | ☐ | ☐ | ☐ | 3.0-4.0 |
| UAUE-000001 | ☐ | ☐ | ☐ | ☐ | 3.0-4.0 |
| UCDA-000001 | ☐ | ☐ | ☐ | ☐ | 3.0-4.0 |
| UCEF-000001 | ☐ | ☐ | ☐ | ☐ | 3.0-4.0 |
| UCOS-AEE-001 | ☐ | ☐ | ☐ | ☐ | 3.0-4.0 |
| UCOS-NUCLEUS-001 | ☐ | ☐ | ☐ | ☐ | 3.0-4.0 |
| UCOS-RIB-001 | ☐ | ☐ | ☐ | ☐ | 3.0-4.0 |
| UCOS-RIE-001 | ☐ | ☐ | ☐ | ☐ | 3.0-4.0 |
| UCOS-UCAF-001 | ☐ | ☐ | ☐ | ☐ | 3.0-4.0 |
| UCOS-UFEP-001 | ☐ | ☐ | ☐ | ☐ | 3.0-4.0 |
| UCOS-UGA-001 | ☐ | ☐ | ☐ | ☐ | 3.0-4.0 |

**MB15 Total**: 45-60 hours (15 producers × 3.0-4.0 hours)

---

## MB16: SHORT-WORD FALSE MATCH

**Status**: 0/32 applicable (already N/A for 32/33, CLOSED for 1/33)

**No remaining work** (only applicable to template-based validators, implemented for UCOS-UCTX-001)

---

## MB17: AUTHORITY GOVERNANCE GAP

**Status**: 31/33 producers UNMEASURED, 1/33 IMPLEMENTED (UCOS-UGA-001)

### Required Work Per Producer

1. **Authority Source Identification** (1 hour)
   - Enumerate all authority input files
   - Document their role and scope
   - Identify constitutional superior

2. **Authority Declaration Creation** (1 hour)
   - Create authority manifest JSON
   - Document governance requirements
   - Link to constitutional framework

3. **Governance Integration** (30 min)
   - Add to CODEOWNERS or review rules
   - Document review requirements

### Per-Producer Work Items

| Producer | Authority ID | Declaration | Governance | Total Hours |
|----------|--------------|-------------|------------|-------------|
| ACEE-000001 | ☐ | ☐ | ☐ | 2.5 |
| BASELINE-001 | ☐ | ☐ | ☐ | 2.5 |
| MCOS-000001 | ☐ | ☐ | ☐ | 2.5 |
| P0-LIFECYCLE-CLOSURE-001 | ☐ | ☐ | ☐ | 2.5 |
| UAIE-000001 | ☐ | ☐ | ☐ | 2.5 |
| UAKOS-CLOSURE-008 | ☐ | ☐ | ☐ | 2.5 |
| UAKOS-CLOSURE-009 | ☐ | ☐ | ☐ | 2.5 |
| UAKOS-PHASE-001A-R1 | ☐ | ☐ | ☐ | 2.5 |
| UAKOS-PHASE-003R | ☐ | ☐ | ☐ | 2.5 |
| UAUE-000001 | ☐ | ☐ | ☐ | 2.5 |
| UCDA-000001 | ☐ | ☐ | ☐ | 2.5 |
| UCEF-000001 | ☐ | ☐ | ☐ | 2.5 |
| UCL-000001 | ☐ | ☐ | ☐ | 2.5 |
| UCOS-AEE-001 | ☐ | ☐ | ☐ | 2.5 |
| UCOS-MXR-001 | ☐ | ☐ | ☐ | 2.5 |
| UCOS-NUCLEUS-001 | ☐ | ☐ | ☐ | 2.5 |
| UCOS-RIB-001 | ☐ | ☐ | ☐ | 2.5 |
| UCOS-RIE-001 | ☐ | ☐ | ☐ | 2.5 |
| UCOS-UAR-001 | ☐ | ☐ | ☐ | 2.5 |
| UCOS-UCAF-001 | ☐ | ☐ | ☐ | 2.5 |
| UCOS-UFEP-001 | ☐ | ☐ | ☐ | 2.5 |
| UCOS-UGA-001 | ☐ (has declaration) | ☐ (needs independent validator) | ☐ | 4.5-8.0 |
| UCOS-URAT-001 | ☐ | ☐ | ☐ | 2.5 |
| UCOS-USIS-WAVE0 | ☐ | ☐ | ☐ | 2.5 |
| UCOS-UTCE-001 | ☐ | ☐ | ☐ | 2.5 |
| UEI-000001 | ☐ | ☐ | ☐ | 2.5 |
| UER-000001 | ☐ | ☐ | ☐ | 2.5 |
| UIS-001 | ☐ | ☐ | ☐ | 2.5 |
| UKAP-001 | ☐ | ☐ | ☐ | 2.5 |
| UMK-000001 | ☐ | ☐ | ☐ | 2.5 |
| UPF-000001 | ☐ | ☐ | ☐ | 2.5 |
| URRC-000001 | ☐ | ☐ | ☐ | 2.5 |

**MB17 Total**: 81.5-86.0 hours (30 × 2.5 + 1 × 4.5-8.0 for UCOS-UGA-001 upgrade)

---

## AGGREGATE WORK ESTIMATE

| Threat | Producers | Hours per Producer | Total Hours |
|--------|-----------|-------------------|-------------|
| MB7 | 32 | 4.5-8.0 | 144-256 |
| MB14 | 32 | 2.0 | 64 |
| MB15 | 15 | 3.0-4.0 | 45-60 |
| MB16 | 0 | N/A | 0 |
| MB17 | 32 | 2.5-8.0 | 81.5-86 |

**Total Work Remaining**: 334.5-466 hours

**At 8 hours/day**: 42-58 working days  
**At 6 hours/day**: 56-78 working days  
**At 4 hours/day**: 84-117 working days

---

## PHASED IMPLEMENTATION PLAN

### Phase 1: Quick Wins (MB14) — 64 hours

**Goal**: Verify fresh-clone bootstrap for all 32 producers

**Deliverables**:
- 32 fresh-clone tests
- CI integration for all tests
- Bootstrap path verification

**Value**: Validates canonical identity claims, prevents fresh-clone failures

**Timeline**: 8-13 working days (at 5-8 hours/day)

---

### Phase 2: Authority Independence (MB7) — 144-256 hours

**Goal**: Eliminate self-validation loops for all 32 producers

**Deliverables**:
- 32 authority corpus declarations
- 32 independent validators
- 96 attack reproducers (3 per producer)
- CI integration for all validators
- Closure proofs for all producers

**Value**: Proves generator correctness independently, eliminates uniformly-wrong-output risk

**Timeline**: 18-32 working days (at 8 hours/day)

---

### Phase 3: Authority Governance (MB17) — 81.5-86 hours

**Goal**: Document and govern authority sources for all producers

**Deliverables**:
- 32 authority declarations
- Governance integration (CODEOWNERS)
- Constitutional alignment documentation

**Value**: Prevents silent authority corruption, enables review enforcement

**Timeline**: 10-11 working days (at 8 hours/day)

---

### Phase 4: Template Normalisation (MB15) — 45-60 hours

**Goal**: Eliminate template explosion for text-based generators

**Deliverables**:
- 15 normalisation implementations
- 15 template manifests
- CI integration for template verification

**Value**: Reduces maintenance burden, enables O(1) template growth

**Timeline**: 6-8 working days (at 8 hours/day)

---

## PARALLELIZATION OPPORTUNITIES

### Independent Workstreams

1. **MB14 (fresh-clone)** — can proceed independently per producer
2. **MB7 (authority independence)** — can proceed independently per producer
3. **MB17 (authority governance)** — can proceed independently per producer
4. **MB15 (template normalisation)** — can proceed independently per producer

**Maximum Parallelization**: 4 simultaneous workstreams

**With 4 parallel workers**: 42-58 days → 11-15 days

---

## RISK MITIGATION

### High-Risk Producers (Priority for MB7)

Based on artifact count and criticality:

1. **UCOS-RIB-001** (build intelligence) — 50+ artifacts
2. **UCOS-RIE-001** (intelligence surfaces) — 40+ artifacts
3. **UAIE-000001** (evidence dashboard) — 12 artifacts, certification-critical
4. **UCOS-UGA-001** (governance attestation) — constitutional claims, needs independent verification
5. **UCOS-AEE-001** (evolution reports) — 18 artifacts, autonomous operation

**Recommendation**: Prioritize these 5 for Phase 2 (MB7) ahead of others.

---

## CERTIFICATION

**Report Author**: Kiro (Claude Opus 5)  
**Measurement Date**: 2026-09-01  
**Work Estimation Method**: Per-producer task decomposition + historical data from UCOS-UCTX-001 implementation

**Key Assumptions**:
- Effort estimates based on UCOS-UCTX-001 actual time (4-6 hours for complete MB7 closure)
- Text-based producer estimate (15/32) requires output inspection to confirm
- Parallelization assumes independent workstreams with no coordination overhead

**Next Action**: Begin Phase 1 (MB14 fresh-clone bootstrap) or prioritize high-risk producers for Phase 2 (MB7 authority independence).

---

**Status**: ESTIMATED  
**Confidence**: MEDIUM (based on single reference implementation, actual variance may be ±30%)
