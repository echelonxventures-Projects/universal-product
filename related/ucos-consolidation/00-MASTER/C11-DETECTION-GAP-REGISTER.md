# C11 — DETECTION GAP REGISTER

**Artifact ID**: UCOS-C11-DETECTION-GAP-001  
**Date**: 2026-09-01  
**Authority**: PHASE C11 — REPOSITORY CLOSURE REALITY AUDIT  
**Method**: Identify failures that could occur without detection

---

## CATEGORY B — DETECTION GAPS

**Definition**: System behavior remains correct currently, but a failure could occur without being detected.

---

### GAP B-001: MB18 (Bootstrap Circularity)

**Threat ID**: MB18

**Current Status**: OPEN (undetected)

**Evidence**:
- 560 GENERATED_DETERMINISTIC references exist in registry
- ~80-100 artifacts depend on GENERATED_DETERMINISTIC inputs (estimated)
- No bootstrap graph exists
- No cycle detection runs
- No verification of bootstrap completeness

**Current System Behavior**: UNKNOWN
- Bootstrap MAY be acyclic (system works today)
- Bootstrap MAY contain cycles (undiscovered)
- No measurement exists

**If Failure Occurs**:
- Fresh clone fails to regenerate artifacts
- Bootstrap hangs in circular dependency
- Operator discovers failure manually

**Detection Status**: UNDETECTED
- No CI stage scans for cycles
- No graph builder exists
- Failure would be discovered by operator attempt, not automated detection

**Why This Is Category B, Not Category A**:
- No evidence of CURRENT bootstrap failure
- UCOS-UCTX-001 proves fresh-clone bootstrap CAN work
- System operates today (CI passes, generation works)
- But IF circularity exists, no detector would catch it

**Required Detector**:
- Bootstrap graph builder (`bootstrap_graph.py`)
- Cycle detection algorithm
- CI enforcement (verify.sh stage)

**Effort to Detect**: 50-60 hours (per EXECUTION-BACKLOG.json W4A)

**Category**: **CATEGORY B — DETECTION GAP**

**Rationale**: System behavior is currently correct (no bootstrap failure observed), but if circularity exists or is introduced, no detector exists. This is a detection gap, not an active defect.

---

### GAP B-002: MB14 (Fresh-Clone Bootstrap Dependency)

**Threat ID**: MB14

**Current Status**: OPEN for 32/33 producers (undetected)

**Evidence**:
- UCOS-UCTX-001 passes fresh-clone test (CI evidence)
- Other 32 producers: NEVER TESTED in fresh-clone environment
- No systematic fresh-clone validation exists

**Current System Behavior**: UNKNOWN for 32/33 producers
- May bootstrap correctly (no evidence of failure)
- May fail fresh-clone (never tested)
- UCOS-UCTX-001 proves feasibility, but doesn't prove others work

**If Failure Occurs**:
- Fresh clone cannot regenerate artifacts
- Missing operational state (files, environment, tool state)
- Operator discovers manually during bootstrap attempt

**Detection Status**: UNDETECTED
- No CI stage tests fresh-clone for 32 producers
- No automated verification
- Failure discovered by manual attempt only

**Why This Is Category B, Not Category A**:
- No evidence of CURRENT failure (32 producers not tested, but not proven broken)
- CI runs in pristine environment and passes (suggests bootstrap may work)
- But absence of test = absence of detection, not absence of defect

**Required Detector**:
- Fresh-clone test suite (per-producer tests)
- Isolated environment execution
- CI enforcement

**Effort to Detect**: 64 hours (per EXECUTION-BACKLOG.json W4B)

**Category**: **CATEGORY B — DETECTION GAP**

**Rationale**: No evidence of bootstrap failure, but also no detection mechanism. If failure exists, it goes undetected.

---

### GAP B-003: Registry Invariant Violations (MB19, MB21 prevention)

**Threat ID**: MB19, MB21

**Current Status**: No violations exist (verified), but no detector prevents future violations

**Evidence**:
- MB19: 0 canonical artifacts with ENVIRONMENTAL_OBSERVATION inputs (scan confirmed)
- MB21: 0 artifacts without validation_owner (scan confirmed)
- Current state is CORRECT
- But no CI stage enforces invariants

**Current System Behavior**: CORRECT
- No invariant violations exist
- Registry is structurally sound

**If Failure Occurs**:
- New artifact added with forbidden input classification
- New artifact added without validation_owner
- Invalid entry accepted into registry
- Violation goes undetected until manual audit

**Detection Status**: UNDETECTED
- No verify.sh stage scans registry invariants
- No automated enforcement
- Manual scan required to detect violations

**Why This Is Category B, Not Category A**:
- Current registry state is CORRECT (0 violations measured)
- No active defect exists today
- But future violations would go undetected

**Required Detector**:
- Registry invariant scanner (W0-002 in backlog)
- CI enforcement

**Effort to Detect**: 6 hours (per EXECUTION-BACKLOG.json W0-002)

**Category**: **CATEGORY B — DETECTION GAP**

**Rationale**: System is currently correct, but lacks automated detection of future violations. This is defensive infrastructure, not defect remediation.

---

### GAP B-004: Template Explosion Risk (MB15)

**Threat ID**: MB15

**Current Status**: OPEN (undetected for 31/33 producers)

**Evidence**:
- UCOS-UCTX-001 proves normalisation prevents explosion (56 templates cover 23 surfaces)
- Other 31 text-based producers: NO MEASUREMENT
- No template manifest exists for other producers
- No verification of O(1) template growth

**Current System Behavior**: UNKNOWN for 31/33
- May have O(1) template growth (no explosion observed)
- May have O(n) or O(n²) explosion (never measured)
- UCOS-UCTX-001 proves prevention is possible, not that others implement it

**If Failure Occurs**:
- New producer instance requires new template
- Template count grows linearly or quadratically
- Maintenance burden increases
- Operator discovers during template maintenance

**Detection Status**: UNDETECTED
- No CI stage measures template growth rate
- No automated verification
- Manual inspection required

**Why This Is Category B, Not Category A**:
- No evidence of CURRENT explosion (system operates today)
- UCOS-UCTX-001 proves prevention works
- But 31 producers unmeasured

**Required Detector**:
- Template coverage measurement (part of W2 validators)
- Normalisation verification
- CI enforcement

**Effort to Detect**: Implicit in W2 (validator implementation includes normalisation)

**Category**: **CATEGORY B — DETECTION GAP**

**Rationale**: No evidence of explosion, but also no measurement for 31/33 producers. Detection gap, not active defect.

---

### GAP B-005: Short-Word False Match (MB16)

**Threat ID**: MB16

**Current Status**: OPEN (undetected for 31/33 producers)

**Evidence**:
- UCOS-UCTX-001 proves MIN_SLOT=6 prevents false matches
- Other 31 text-based producers: NO MEASUREMENT
- No verification of MIN_SLOT enforcement
- No test for short-word false positives

**Current System Behavior**: UNKNOWN for 31/33
- May enforce MIN_SLOT (no false matches observed)
- May allow short-word matches (never tested)
- UCOS-UCTX-001 proves prevention works, not that others implement it

**If Failure Occurs**:
- Validator accepts text with common short words ("the", "is", "a")
- False positive match occurs
- Unprovenanced text passes validation
- Operator discovers during attack test or audit

**Detection Status**: UNDETECTED
- No CI stage tests short-word rejection
- No automated verification
- Manual attack test required

**Why This Is Category B, Not Category A**:
- No evidence of CURRENT false matches
- UCOS-UCTX-001 proves prevention works
- But 31 producers unmeasured

**Required Detector**:
- Short-word attack test (part of W3 attack suite)
- MIN_SLOT enforcement verification
- CI enforcement

**Effort to Detect**: Implicit in W3 (attack verification includes short-word test)

**Category**: **CATEGORY B — DETECTION GAP**

**Rationale**: No evidence of false matches, but also no detection. If failure occurs, it goes unnoticed until attack test.

---

## SUMMARY

**Total CATEGORY B Gaps**: 5

| Gap | Threat | Current Status | Detection Exists | If Failure Occurs |
|-----|--------|----------------|------------------|-------------------|
| B-001 | MB18 | Unknown (unmeasured) | NO | Manual discovery |
| B-002 | MB14 | Unknown (untested) | NO | Manual discovery |
| B-003 | MB19/MB21 | Correct (verified) | NO | Manual scan required |
| B-004 | MB15 | Unknown (unmeasured) | NO | Manual inspection |
| B-005 | MB16 | Unknown (unmeasured) | NO | Attack test required |

---

## DETECTION GAP CRITERIA

A gap qualifies as CATEGORY B only if:

1. **No Current Evidence of Failure**: System appears to work today
2. **No Automated Detection**: If failure occurs, no CI stage catches it
3. **Manual Discovery Required**: Operator finds failure by accident or manual test

AND:

4. **Plausible Failure Mode**: Failure is structurally possible (not purely theoretical)

---

## CATEGORY B vs CATEGORY A DISTINCTION

**Category A (Active Defect)**:
- Evidence of CURRENT incorrectness
- OR: Critical path NEVER TESTED (like regeneration commands)
- Impact is OPERATIONAL today

**Category B (Detection Gap)**:
- No evidence of CURRENT incorrectness
- System appears to work
- But IF failure exists or occurs, no detector catches it
- Impact is CONDITIONAL on failure occurring

**Example**:
- MB7 is Category A: UCOS-UCTX-001 PROVES self-validation accepts wrong output (measured defect)
- MB18 is Category B: No evidence of circularity, but also no detector (detection gap)

---

## VERIFICATION STATUS

| Gap | Current Behavior | Evidence Type | Detection Status |
|-----|------------------|---------------|------------------|
| B-001 | Unknown | Structural (560 refs exist) | None |
| B-002 | Unknown | Partial (1/33 tested) | None |
| B-003 | Correct | Measured (0 violations) | None |
| B-004 | Unknown | Partial (1/33 measured) | None |
| B-005 | Unknown | Partial (1/33 tested) | None |

---

**Status**: C11-B COMPLETE ✓  
**Result**: 5 DETECTION GAPS identified  
**All Impact**: CONDITIONAL (depends on failure occurring)
