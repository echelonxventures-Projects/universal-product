# MB18-MB25 CANDIDATE REGISTRY

**Artifact ID**: UCOS-MB18-MB25-REGISTRY-001  
**Date**: 2026-09-01  
**Authority**: PHASE C7 REPOSITORY-WIDE CLOSURE EXECUTION AUDIT  
**Discovery Method**: Structural analysis of generated-artifact-registry.json, CI configuration, test patterns, and cross-cutting concerns

---

## DISCOVERY METHODOLOGY

1. **Structural Analysis**: Examined generated-artifact-registry.json for contradictions, gaps, and unenforceable claims
2. **CI Configuration Review**: Analyzed verify.sh and .github/workflows for enforcement gaps
3. **Test Pattern Analysis**: Surveyed 330 test files for validation architecture patterns
4. **Cross-Cutting Concerns**: Identified failure modes that span multiple producers or subsystems

**Key Principle**: Only failures that are structurally distinct from MB7-MB17 are assigned new identifiers.

---

## MB18: GENERATED_DETERMINISTIC INPUT CIRCULARITY

**Name**: Generated-Deterministic Input Circularity

**Definition**: An artifact declares `deterministic: true` and depends on `GENERATED_DETERMINISTIC` inputs, but those inputs' bootstrap paths form a cycle or are incomplete, making the deterministic claim unverifiable in a fresh clone.

**Structural Signature**: 
```json
"deterministic": true,
"input_classification": {
  "some_input": "GENERATED_DETERMINISTIC"
}
```
Without verifiable bootstrap path for `some_input`.

**Discovery Evidence**: Registry declares "GENERATED_INPUT_HAS_PRODUCER_AND_BOOTSTRAP — every GENERATED_DETERMINISTIC input resolves to a generated_inputs entry carrying a producer and a bootstrap path" as an invariant, but no CI stage enforces this.

**Affected Scope**: Estimated 50-100 artifacts (any artifact consuming generated inputs)

**Severity**: HIGH (breaks canonical identity claims)

**Relation to Known Threats**: 
- Related to MB14 (fresh-clone bootstrap) but specifically about transitive dependencies
- MB14 measures direct bootstrap, MB18 measures bootstrap closure

**Closure Requirement**:
1. Bootstrap path graph builder
2. Cycle detector
3. Completeness verifier (every GENERATED_DETERMINISTIC input has valid bootstrap)
4. CI enforcement

---

## MB19: ENVIRONMENTAL_OBSERVATION IN CANONICAL ARTIFACTS

**Name**: Environmental-Observation Input in Canonical Artifacts

**Definition**: An artifact claims `canonical_identity_role: CANONICAL` but depends on ENVIRONMENTAL_OBSERVATION, EXECUTION_TRANSCRIPT, or LOCAL_RUNTIME inputs, violating the principle that canonical identity must be reproducible from tracked sources.

**Structural Signature**:
```json
"canonical_identity_role": "CANONICAL",
"input_classification": {
  "some_input": "EXECUTION_TRANSCRIPT" | "LOCAL_RUNTIME" | "ENVIRONMENTAL_OBSERVATION"
}
```

**Discovery Evidence**: Registry declares "CANONICAL_ARTIFACT_INPUT_CLASSIFICATION — a CANONICAL artifact may not declare an EXECUTION_TRANSCRIPT, LOCAL_RUNTIME or ENVIRONMENTAL_OBSERVATION input" as an invariant, but no CI stage enforces this.

**Affected Scope**: Unknown (requires registry scan)

**Severity**: CRITICAL (violates canonical identity definition)

**Relation to Known Threats**: 
- Orthogonal to MB7-MB17
- Structural integrity violation rather than validation defect

**Closure Requirement**:
1. Registry scanner for canonical artifacts with environmental inputs
2. Classification validator
3. CI enforcement

---

## MB20: CERTIFICATION_ROLE vs EVIDENCE_CLASS MISMATCH

**Name**: Certification-Role Evidence-Class Mismatch

**Definition**: An artifact with `certification_role` (used for release decisions) consumes DEBUG or IMPROVEMENT evidence surfaces, violating the rule that certification evidence must be stable and production-grade.

**Structural Signature**:
```json
"certification_role": "PROGRAMME_DELIVERABLE" | "QUALITY_GATE_ONLY",
"input_closure": ["some_evidence_surface"]
```
Where `some_evidence_surface` is classified as DEBUG or IMPROVEMENT in evidence-universe.json.

**Discovery Evidence**: Registry declares "CERTIFICATION_EVIDENCE_CLASS — no artifact carrying a certification role consumes a DEBUG or IMPROVEMENT evidence surface (R-EV-4)" as an invariant, but no CI stage enforces this.

**Affected Scope**: Unknown (requires cross-reference with evidence-universe.json)

**Severity**: HIGH (certification based on unstable evidence)

**Relation to Known Threats**: 
- Orthogonal to MB7-MB17
- Evidence governance gap

**Closure Requirement**:
1. Evidence classification loader
2. Certification artifact scanner
3. Cross-reference validator
4. CI enforcement

---

## MB21: VALIDATION_OWNER UNDECLARED

**Name**: Validation-Owner Undeclared

**Definition**: An artifact has no `validation_owner` and no `independent_validation`, meaning no one is declared responsible for verifying correctness.

**Structural Signature**:
```json
{
  "artifact_id": "...",
  "owner": "...",
  // validation_owner field absent
  // independent_validation field absent
}
```

**Discovery Evidence**: Found while scanning registry structure. Estimated 2 environmental artifacts (coverage.xml, .coverage) have validation_owner but may have gaps.

**Affected Scope**: Estimated 0-5 artifacts (most declare validation_owner)

**Severity**: MEDIUM (validation responsibility unclear)

**Relation to Known Threats**: 
- Related to MB7 but specifically about responsibility declaration, not validation architecture
- MB7 measures independence, MB21 measures whether anyone is declared at all

**Closure Requirement**:
1. Registry completeness scanner
2. Validation responsibility rule
3. CI enforcement

---

## MB22: REGENERATION_COMMAND UNVERIFIED

**Name**: Regeneration-Command Unverified

**Definition**: An artifact declares `lifecycle: REGENERATED` and provides a `regeneration_command`, but no test verifies the command actually produces the declared output.

**Structural Signature**:
```json
"lifecycle": "REGENERATED",
"regeneration_command": "some_command"
```
Without corresponding test that runs `some_command` and verifies output matches.

**Discovery Evidence**: All 368 artifacts declare regeneration_command, but only UCOS-UCTX-001 has measured regeneration in CI (verify.sh stage 6).

**Affected Scope**: 367/368 artifacts (all except UCOS-UCTX-001)

**Severity**: HIGH (regeneration commands may be stale, incorrect, or incomplete)

**Relation to Known Threats**: 
- Related to MB14 but specifically about command correctness
- MB14 measures bootstrap success, MB22 measures command accuracy

**Closure Requirement**:
1. Per-artifact regeneration test
2. Output diff verification
3. CI enforcement for all producers

---

## MB23: DETERMINISTIC CLAIM WITHOUT EVIDENCE

**Name**: Deterministic Claim Without Evidence

**Definition**: An artifact claims `deterministic: true` but no test verifies that two independent runs produce identical output.

**Structural Signature**:
```json
"deterministic": true
```
Without corresponding determinism test measuring byte-for-byte reproducibility.

**Discovery Evidence**: 384 artifacts claim deterministic:true. Only UCOS-UCTX-001 has measured determinism in the MB7 attack tests (uniform wrong output variants produce consistent results).

**Affected Scope**: 383/384 artifacts (all except UCOS-UCTX-001)

**Severity**: MEDIUM (determinism claims may be false)

**Relation to Known Threats**: 
- Orthogonal to MB7-MB17
- Determinism is assumed, not verified

**Closure Requirement**:
1. Per-artifact determinism test (run twice, compare bytes)
2. CI enforcement
3. Reproducibility dashboard

---

## MB24: CONSTITUTIONAL_SUPERIOR UNENFORCED

**Name**: Constitutional-Superior Unenforced

**Definition**: An artifact declares a `constitutional_superior` but no validator verifies that the artifact's claims align with the superior's authority.

**Structural Signature**:
```json
"constitutional_superior": {
  "authority": "SOME-LAW",
  "home": "some/path.py"
}
```
Without independent validator checking alignment.

**Discovery Evidence**: Found in generated-artifact-registry.json header (declares UCKP-LAW-0001 as superior) and in individual UCOS-UCTX-001 context outputs. UCOS-UGA-001 has constitutional-authority-alignment.json but only self-validates.

**Affected Scope**: Estimated 10-20 artifacts declare constitutional superiors

**Severity**: HIGH (constitutional claims unverified)

**Relation to Known Threats**: 
- Superset of MB17 (authority governance)
- MB17 measures authority file governance, MB24 measures alignment verification

**Closure Requirement**:
1. Constitutional alignment scanner
2. Independent verifier for each constitutional claim
3. CI enforcement

---

## MB25: INPUT_CLASSIFICATION DRIFT

**Name**: Input-Classification Drift

**Definition**: An artifact declares input classifications in the registry, but the generator actually reads additional files not declared in `input_closure`, or the classifications are incorrect.

**Structural Signature**:
```json
"input_closure": ["file1", "file2"],
"input_classification": {
  "file1": "TRACKED_DETERMINISTIC",
  "file2": "GENERATED_DETERMINISTIC"
}
```
But generator code reads `file3` at runtime.

**Discovery Evidence**: No enforcement mechanism exists. Registry declarations are trusted without verification.

**Affected Scope**: Unknown (requires generator instrumentation or static analysis)

**Severity**: CRITICAL (input closure claims may be false, breaking canonical identity)

**Relation to Known Threats**: 
- Related to MB14 but specifically about hidden dependencies
- MB14 assumes declared input_closure is complete, MB25 questions that assumption

**Closure Requirement**:
1. Generator instrumentation (file access logging)
2. Static analysis of generator imports and file reads
3. Input closure completeness verifier
4. CI enforcement

---

## THREAT CLUSTERING

### Cluster 1: Bootstrap Integrity (MB14, MB18, MB22, MB25)

**Common Theme**: Fresh-clone reproducibility and input closure completeness

**Relationships**:
- MB14: Direct bootstrap works
- MB18: Transitive bootstrap (generated inputs) works
- MB22: Declared command matches reality
- MB25: Declared inputs match reality

**Unified Closure**: Bootstrap integrity suite that measures end-to-end reproducibility with input tracking.

---

### Cluster 2: Canonical Identity Governance (MB19, MB23)

**Common Theme**: What qualifies as "canonical" vs "environmental"

**Relationships**:
- MB19: Canonical artifacts don't depend on environmental observations
- MB23: Deterministic claims are verified, not assumed

**Unified Closure**: Canonical identity validator that enforces determinism + tracked-input-only requirements.

---

### Cluster 3: Authority Alignment (MB7, MB17, MB24)

**Common Theme**: Generator output derives from declared authorities and aligns with constitutional superiors

**Relationships**:
- MB7: Output provenance (independent validation)
- MB17: Authority file governance
- MB24: Constitutional alignment verification

**Unified Closure**: Authority governance framework with provenance + alignment + governance.

---

### Cluster 4: Evidence Integrity (MB20, MB21)

**Common Theme**: Validation and certification use appropriate evidence

**Relationships**:
- MB20: Certification doesn't use debug evidence
- MB21: Every artifact has declared validator

**Unified Closure**: Evidence classification + validation responsibility framework.

---

## SEVERITY CLASSIFICATION

| Threat | Severity | Rationale |
|--------|----------|-----------|
| MB18 | HIGH | Breaks canonical identity closure |
| MB19 | CRITICAL | Structural violation of canonical definition |
| MB20 | HIGH | Certification based on unstable evidence |
| MB21 | MEDIUM | Responsibility unclear but not immediately dangerous |
| MB22 | HIGH | Commands may be wrong, blocking regeneration |
| MB23 | MEDIUM | Claims may be false but doesn't break immediately |
| MB24 | HIGH | Constitutional claims unverified |
| MB25 | CRITICAL | Hidden dependencies break reproducibility |

---

## ESTIMATED AFFECTED SCOPE

| Threat | Artifacts Affected | Producers Affected | Measurement Status |
|--------|-------------------|-------------------|-------------------|
| MB18 | 50-100 (est) | 15-20 (est) | UNMEASURED |
| MB19 | 0-10 (est) | 0-5 (est) | UNMEASURED |
| MB20 | 0-20 (est) | 0-10 (est) | UNMEASURED |
| MB21 | 0-5 (est) | 0-3 (est) | UNMEASURED |
| MB22 | 367/368 | 32/33 | PARTIALLY MEASURED (1 CLOSED) |
| MB23 | 383/384 | 32/33 | PARTIALLY MEASURED (1 CLOSED) |
| MB24 | 10-20 (est) | 5-10 (est) | UNMEASURED |
| MB25 | Unknown | Unknown | UNMEASURED |

---

## IMPLEMENTATION PRIORITY

### Tier 1: Critical Infrastructure (MB19, MB25)

**Risk**: CRITICAL (structural violations of canonical identity)  
**Effort**: Medium (MB19), High (MB25)  
**Priority**: IMMEDIATE

**Rationale**: These break the foundational claims of the repository. MB19 is structurally enforceable (registry scan), MB25 requires instrumentation.

---

### Tier 2: High-Value Verification (MB18, MB22, MB24)

**Risk**: HIGH (breaks reproducibility and constitutional claims)  
**Effort**: Medium (each ~40-80 hours)  
**Priority**: HIGH

**Rationale**: These threaten core capabilities but are detectable and fixable systematically.

---

### Tier 3: Governance Hygiene (MB20, MB21, MB23)

**Risk**: MEDIUM-HIGH (quality and confidence issues)  
**Effort**: Low-Medium (each ~20-40 hours)  
**Priority**: MEDIUM

**Rationale**: These don't break immediately but erode confidence and create technical debt.

---

## CROSS-CUTTING ENFORCEMENT

### New CI Stages Required

1. **stage-registry-invariants** (enforces MB18, MB19, MB20, MB21)
   - Scans registry for structural violations
   - ~4 hours to implement
   - Covers 4 threats at once

2. **stage-bootstrap-integrity** (enforces MB14, MB18, MB22, MB25)
   - Measures end-to-end reproducibility with input tracking
   - ~80-120 hours to implement (instrumentation + per-producer tests)
   - Covers 4 threats at once

3. **stage-determinism-verification** (enforces MB23)
   - Runs each generator twice, compares output
   - ~40-60 hours to implement
   - Covers 1 threat

4. **stage-constitutional-alignment** (enforces MB17, MB24)
   - Verifies authority governance + alignment claims
   - ~60-80 hours to implement
   - Covers 2 threats

---

## CERTIFICATION

**Discovery Author**: Kiro (Claude Opus 5)  
**Discovery Date**: 2026-09-01  
**Method**: Structural analysis + registry invariant correlation

**Key Findings**:
- 8 new threat classes discovered (MB18-MB25)
- 4 threat clusters identified
- Estimated 450-700 additional closure hours required
- Critical threats (MB19, MB25) require immediate attention

**Confidence**: 
- HIGH for MB18-MB24 (structural evidence clear)
- MEDIUM for MB25 (requires instrumentation to measure actual scope)

**Limitations**:
- Actual affected artifact counts are estimates (require systematic scans)
- Some threats may overlap with future discoveries
- Severity assessments are based on potential impact, not measured incidents

---

## NEXT ACTIONS

1. **Immediate**: Implement stage-registry-invariants (4 hours) to measure MB18, MB19, MB20, MB21 actual scope
2. **Short-term**: Design bootstrap-integrity instrumentation for MB25 measurement
3. **Medium-term**: Execute Tier 1 closures (MB19, MB25)
4. **Long-term**: Integrate into phased closure plan from C9-REMAINING-WORK-LEDGER.md

---

**Status**: DISCOVERED  
**Measurement Status**: UNMEASURED (estimates only, require systematic scans)  
**Closure Status**: OPEN (0/8 threats closed)
