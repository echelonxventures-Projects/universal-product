# CANONICAL-IMPLEMENTATION-DEPENDENCY-GRAPH-DETERMINATION

| Field | Value |
|---|---|
| Status | **CANONICAL IMPLEMENTATION DEPENDENCY GRAPH — PHASE 3 COMPLETE** |
| Authority | **NONE — DERIVED ANALYSIS** |
| Date | 2026-08-22 |
| Baseline | `03179308` (integration/recovery-001) |
| Directive | UCOS Ω∞ — 100% IMPLEMENTATION READINESS (Phase 3) |

---

## §1 — Executive Summary

**Objective:** Create dependency order by constitutional dependency—not document order, not convenience.

**Scope:** 10 OPEN GAP requirements, ordered by foundation → dependent → validation → certification.

**Key finding:** **5-tier dependency hierarchy identified. Critical path: Constitutional decisions (Tier 1) → Extensions (Tier 2) → Programme creation (Tier 3) → Capabilities (Tier 4) → Certification (Tier 5). Zero circular dependencies detected.**

---

## §2 — Dependency Analysis Framework

### §2.1 — Dependency Types

**Constitutional dependency:** Requires constitutional decision (CEP-002 Article 28, UCRD-001 review)

**Authority dependency:** Requires programme registration (owner must exist)

**Technical dependency:** Requires implementation artifact (code, API, infrastructure)

**Validation dependency:** Requires test/gate evidence

**Certification dependency:** Requires validation evidence + certification criteria

### §2.2 — Dependency Ordering Principles

**Principle 1: Constitutional authority first**
- No programme creation without constitutional decision
- No identity allocation without authority
- No architectural closure without justification

**Principle 2: Foundation before dependent**
- No capability implementation without owner
- No extension without base capability
- No validation without implementation

**Principle 3: Implementation before validation**
- No validation without implementation artifact
- No certification without validation evidence
- No closure without certification

**Principle 4: Evidence-based progression**
- No CERTIFIED status without executable evidence
- No certification without validation tests
- No validation without implementation

---

## §3 — Tier 1: Constitutional Foundation

### §3.1 — TIER 1-A: Constitutional Decisions (No Dependencies)

**Item 1-A-1: KnowledgeKind Extension Decision**

**Requirement:** UCRD-001 constitutional review—reopen `KnowledgeKind` or accept closure

**Dependencies:** ❌ None (constitutional decision is foundation)

**Blocks:**
- REQ-NEW-01 (principle assimilation—needs PRINCIPLE kind)
- REQ-NEW-04 (requirement universe—needs REQUIREMENT kind)
- Canonical knowledge storage for principles/requirements

**Risk:** **CRITICAL** (blocks 2 major capabilities)

**Rollback strategy:** N/A (constitutional decision, not implementation)

**Evidence required:** Constitutional decision document

**Alternatives:**
- **Option A:** Reopen `KnowledgeKind` (add PRINCIPLE, REQUIREMENT, etc.)
- **Option B:** Accept closure, use alternative architecture (principles/requirements as descriptive artifacts, not CKOs)
- **Option C:** Provisional reopening (add kinds, subject to future review)

**Recommended:** Option A (reopen) or Option B (accept + alternative)

**Decision authority:** Constitutional authority (CEU or designated body)

**Timeline:** Constitutional process (weeks to months)

---

### §3.2 — TIER 1-B: Programme Registrations (Depends on 1-A)

**Item 1-B-1: UKAP Programme Registration**

**Requirement:** Register Universal Knowledge Assimilation Programme via CEP-002 Article 28

**Dependencies:**
- ✅ CEP-002 Article 28 exists (operational)
- ⚠️ KnowledgeKind decision (if UKAP stores principles as CKOs)

**Blocks:**
- REQ-NEW-01 (principle assimilation—needs owner)
- REQ-NEW-02 (assumption detection—needs owner)
- REQ-NEW-07 (determination lifecycle—needs owner)
- REQ-NEW-09 (semantic similarity—needs owner)
- Orphan artifact adoption (principles, determinations)

**Risk:** **HIGH** (blocks 4 capabilities + orphan resolution)

**Rollback strategy:** Programme deregistration (reverse CEP-002 Article 28 process)

**Evidence required:**
- Programme dashboard created
- Ownership declared (principles, determinations, architectural assumptions, semantic capabilities)
- CEP-002 Article 28 registration complete

**Implementation prerequisite:**
1. Draft UKAP programme dashboard
2. Define UKAP scope (ownership boundaries)
3. Submit CEP-002 Article 28 registration
4. Await approval

**Validation evidence required:**
- Registration record in ADR or UCDA decision
- Programme dashboard accessible
- Ownership boundaries documented

**Closure criteria:**
- UKAP registered via CEP-002 Article 28
- Dashboard exists (`00-MASTER/UKAP-XXXXXX/00-UKAP-DASHBOARD.md`)
- Ownership declared (principles, determinations, assumption detection, semantic similarity)

**Estimated effort:** ~200 LOC (dashboard creation) + constitutional process

**Timeline:** 1 week (dashboard) + constitutional approval time

---

**Item 1-B-2: UREE Programme Registration**

**Requirement:** Register Universal Requirement Evolution Engine via CEP-002 Article 28

**Dependencies:**
- ✅ CEP-002 Article 28 exists (operational)
- ⚠️ KnowledgeKind decision (if UREE stores requirements as CKOs)

**Blocks:**
- REQ-NEW-04 (requirement universe—needs owner)
- REQ-NEW-10 (requirement evolution—needs owner)
- Orphan artifact adoption (requirements)

**Risk:** **HIGH** (blocks 2 capabilities + orphan resolution)

**Rollback strategy:** Programme deregistration (reverse CEP-002 Article 28 process)

**Evidence required:**
- Programme dashboard created
- Ownership declared (requirements, requirement universe)
- CEP-002 Article 28 registration complete

**Implementation prerequisite:**
1. Draft UREE programme dashboard
2. Define UREE scope (ownership boundaries)
3. Submit CEP-002 Article 28 registration
4. Await approval

**Validation evidence required:**
- Registration record in ADR or UCDA decision
- Programme dashboard accessible
- Ownership boundaries documented

**Closure criteria:**
- UREE registered via CEP-002 Article 28
- Dashboard exists (`00-MASTER/UREE-XXXXXX/00-UREE-DASHBOARD.md`)
- Ownership declared (requirements, requirement evolution)

**Estimated effort:** ~200 LOC (dashboard creation) + constitutional process

**Timeline:** 1 week (dashboard) + constitutional approval time

---

## §4 — Tier 2: Extensions (Depends on Tier 1)

### §4.1 — TIER 2-A: Mutation Classification Extension

**Item 2-A-1: Violation 4 Resolution (MutationClass Extension)**

**Requirement:** Add 9th mutation class (GOVERNED_ANALYSIS) + extension mechanism

**Dependencies:**
- ✅ Repository Intelligence exists (operational)
- ⚠️ UKAP registration (GOVERNED_ANALYSIS owner must exist)

**Blocks:**
- REQ-NEW-07 (determination lifecycle—needs GOVERNED_ANALYSIS classification)

**Risk:** **MEDIUM** (blocks determination governance, but determinations are analysis artifacts)

**Rollback strategy:** Remove 9th class, revert to 8 classes (if no determinations classified yet)

**Evidence required:**
- `MutationClass` enum extended (9 classes)
- Extension mechanism added (UNKNOWN variant or dynamic registration)
- Tests pass (mutation classification with 9 classes)
- `mutation-governance-boundary.json` updated (UKAP as GOVERNED_ANALYSIS owner)

**Implementation prerequisite:**
1. UKAP registered (owner of GOVERNED_ANALYSIS)
2. Read `platform/repository_intelligence/mutation_classification.py`
3. Design extension mechanism (UNKNOWN variant recommended)

**Validation evidence required:**
- Test: Classify determination document → GOVERNED_ANALYSIS
- Test: Add hypothetical 10th class via extension mechanism
- Test: All existing mutation classification tests still pass

**Closure criteria:**
- 9 mutation classes operational
- GOVERNED_ANALYSIS class added
- Extension mechanism operational (UNKNOWN variant or dynamic registration)
- Tests: 49 existing + 3 new = 52 tests pass

**Estimated effort:** ~400 LOC (enum extension, tests, governance boundary update)

**Timeline:** 3 days (implementation + testing)

---

### §4.2 — TIER 2-B: Context Extensibility

**Item 2-B-1: REQ-28 (Universal Context Kind Closure Validation)**

**Requirement:** Validate 16 context kinds are extensible OR add extension mechanism

**Dependencies:**
- ✅ UCKP exists (operational)

**Blocks:** ❌ None (isolated requirement)

**Risk:** **LOW** (16 context kinds sufficient, extensibility nice-to-have)

**Rollback strategy:** N/A (validation or extension, no breaking changes)

**Evidence required:**
- If extensible: Test proving 17th context kind can be added
- If not extensible: Extension mechanism added + test

**Implementation prerequisite:**
1. Read `engine/uckp/universal_context.py` (verify current implementation)
2. If `UniversalContextKind` is enum: Add UNKNOWN variant or dynamic registration
3. If already extensible: Write validation test

**Validation evidence required:**
- Test: Add 17th context kind (hypothetical) via extension mechanism
- Test: Existing context kind operations still work

**Closure criteria:**
- Universal context extensibility proven (test evidence) OR
- Extension mechanism added + test passes

**Estimated effort:** ~200 LOC (if extension needed) or ~50 LOC (if only validation test)

**Timeline:** 1-2 days (verification + testing)

---

### §4.3 — TIER 2-C: Evolution Ledger Extension

**Item 2-C-1: REQ-NEW-10 (Requirement Evolution Tracking)**

**Requirement:** Extend evolution ledger to accept requirements as subject type

**Dependencies:**
- ✅ UAUE exists (operational)
- ⚠️ UREE registration (requirement owner must exist)

**Blocks:**
- REQ-NEW-04 (requirement universe—evolution tracking needed)

**Risk:** **MEDIUM** (requirement universe needs evolution tracking)

**Rollback strategy:** Remove requirement subject type from evolution ledger (if no requirements tracked yet)

**Evidence required:**
- `EvolutionLedger` accepts requirement subject type
- Requirement evolution events defined (added, modified, superseded, obsoleted)
- Tests pass (requirement evolution scenarios)

**Implementation prerequisite:**
1. UREE registered (requirement owner)
2. Read `engine/uckp/evolution.py` (understand subject type model)
3. Define requirement evolution events

**Validation evidence required:**
- Test: Add requirement → evolution record created
- Test: Modify requirement → evolution record created
- Test: Supersede requirement → evolution record created
- Test: Query requirement evolution history

**Closure criteria:**
- Evolution ledger accepts requirements
- Requirement evolution events operational
- Tests: 4 new evolution scenarios pass
- At least 1 requirement tracked in evolution ledger

**Estimated effort:** ~500 LOC (subject type extension, requirement events, tests)

**Timeline:** 1 week (implementation + testing)

---

## §5 — Tier 3: New Capabilities (Depends on Tier 1-2)

### §5.1 — TIER 3-A: Foundation Capabilities

**Item 3-A-1: REQ-NEW-09 (Semantic Similarity Engine)**

**Requirement:** Intent-based duplicate detection (semantic, not string matching)

**Dependencies:**
- ⚠️ UKAP registration (owner must exist)
- ✅ Embedding model approach decision (sentence-transformers recommended)

**Blocks:**
- REQ-NEW-01 (principle assimilation—needs deduplication)
- REQ-NEW-04 (requirement universe—needs deduplication)

**Risk:** **HIGH** (blocks principle + requirement assimilation)

**Rollback strategy:** Remove semantic similarity engine, revert to manual deduplication (if no automated deduplication in use yet)

**Evidence required:**
- Semantic similarity engine operational
- Similarity score 0-100% computed for two statements
- Tests pass (duplicate detection, non-duplicate distinction)

**Implementation prerequisite:**
1. UKAP registered
2. Embedding model choice confirmed (sentence-transformers, OpenAI embeddings, or LLM API)
3. Similarity threshold calibrated (>90% = duplicate, >70% = investigate)

**Validation evidence required:**
- Test: Known duplicate (same intent, different wording) → >90% similarity
- Test: Known non-duplicate (similar wording, different intent) → <70% similarity
- Test: 49 existing requirements scanned → 0 duplicates detected (verify manual audit)
- Performance test: Similarity computation < 1s per comparison

**Closure criteria:**
- Semantic similarity engine operational (API available: `compare_similarity(statement1, statement2) → float`)
- Duplicate detection operational (scan population, identify >90% matches)
- Tests: 10 similarity scenarios pass
- False positive rate < 10%

**Estimated effort:** ~4,000 LOC (embedding model integration, similarity scoring, duplicate detection, tests)

**Timeline:** 2-3 weeks (model integration + testing + calibration)

---

**Item 3-A-2: REQ-NEW-07 (Determination Artifact Lifecycle)**

**Requirement:** 7-stage lifecycle for determination documents (DRAFT → ARCHIVED)

**Dependencies:**
- ⚠️ UKAP registration (owner must exist)
- ✅ Violation 4 resolved (GOVERNED_ANALYSIS class exists)

**Blocks:**
- Determination evolution tracking (part of REQ-NEW-07 scope)

**Risk:** **MEDIUM** (determination governance, not blocking operational capabilities)

**Rollback strategy:** Remove determination lifecycle, revert to untracked state (if no determinations in lifecycle yet)

**Evidence required:**
- Determination lifecycle operational (7 stages: DRAFT → REVIEW → APPROVED → ACTIVE → IMPLEMENTED → SUPERSEDED → ARCHIVED)
- Determination status tracking (which stage is each determination in?)
- Supersession tracking (newer determination supersedes older)

**Implementation prerequisite:**
1. UKAP registered
2. GOVERNED_ANALYSIS mutation class exists
3. Determination registry designed (data structure for tracking)

**Validation evidence required:**
- Test: Determination created → status = DRAFT
- Test: Determination approved → status = APPROVED
- Test: Determination implemented → status = IMPLEMENTED
- Test: Determination superseded → status = SUPERSEDED, links to newer determination
- Test: Determination archived → status = ARCHIVED, retained in registry

**Closure criteria:**
- Determination lifecycle operational (7 stages)
- 13 session determinations assigned lifecycle stage
- Supersession tracking operational
- Tests: 7 lifecycle transition scenarios pass

**Estimated effort:** ~1,000 LOC (lifecycle tracking, status management, supersession, tests)

**Timeline:** 1 week (implementation + testing)

---

### §5.2 — TIER 3-B: Assimilation Capabilities

**Item 3-B-1: REQ-NEW-01 (Universal Principle Assimilation)**

**Requirement:** Discovery → certification pipeline for architectural principles

**Dependencies:**
- ⚠️ UKAP registration (owner must exist)
- ⚠️ REQ-NEW-09 (semantic similarity—for deduplication)
- ⚠️ KnowledgeKind decision (if principles stored as CKOs) OR alternative architecture
- ✅ UAUE evolution ledger (for principle evolution)

**Blocks:**
- Principle enforcement validation (part of assimilation pipeline)

**Risk:** **HIGH** (constitutional principles need governance)

**Rollback strategy:**
- If KnowledgeKind opens: Remove PRINCIPLE kind, delete principle CKOs
- If alternative architecture: Delete principle registry

**Evidence required:**
- Principle assimilation pipeline operational (8 stages: DISCOVERED → EXTRACTED → NORMALIZED → VALIDATED → REGISTERED → IMPLEMENTED → CERTIFIED → ENFORCED)
- UAP-001 and UIEP-001 assimilated
- Principle enforcement mechanisms operational

**Implementation prerequisite:**
1. UKAP registered
2. Semantic similarity engine operational (REQ-NEW-09)
3. KnowledgeKind decision made (open or alternative architecture)
4. Evolution ledger accepts principles (if CKO approach)

**Validation evidence required:**
- Test: Principle discovered from conversation → extracted → registered
- Test: Principle enforcement validated (UAP-001: no entity type privileges)
- Test: Principle evolution tracked
- Integration test: UAP-001 assimilated end-to-end

**Closure criteria:**
- Principle assimilation pipeline operational
- UAP-001 assimilated + certified
- UIEP-001 assimilated + certified
- Tests: 8 pipeline stage scenarios + 2 principle certifications

**Estimated effort:** ~3,000 LOC (discovery, extraction, normalization, validation, registration, enforcement, tests)

**Timeline:** 3-4 weeks (implementation + principle assimilation + testing)

---

**Item 3-B-2: REQ-NEW-04 (Requirement Universe Evolution)**

**Requirement:** Requirements as unbounded universe with automatic discovery

**Dependencies:**
- ⚠️ UREE registration (owner must exist)
- ⚠️ REQ-NEW-09 (semantic similarity—for deduplication)
- ⚠️ REQ-NEW-10 (requirement evolution—evolution tracking)
- ⚠️ KnowledgeKind decision (if requirements stored as CKOs) OR alternative architecture

**Blocks:**
- Coverage matrix generation (requirement → capability mapping)

**Risk:** **HIGH** (requirement governance critical)

**Rollback strategy:**
- Revert to manual requirement index (markdown table)
- Delete requirement universe infrastructure

**Evidence required:**
- Requirement universe operational (discovery → admission → certification)
- 49 existing requirements imported
- Requirement evolution tracked

**Implementation prerequisite:**
1. UREE registered
2. Semantic similarity engine operational (REQ-NEW-09)
3. Evolution ledger accepts requirements (REQ-NEW-10)
4. KnowledgeKind decision made (open or alternative architecture)

**Validation evidence required:**
- Test: Requirement discovered from conversation → extracted → admitted
- Test: Duplicate requirement detected → rejected or merged
- Test: Requirement evolution tracked
- Integration test: All 49 existing requirements imported + 10 new requirements (REQ-NEW-01 through REQ-NEW-10) admitted

**Closure criteria:**
- Requirement universe operational
- 49 existing requirements migrated
- 10 new requirements admitted (REQ-NEW-01 through REQ-NEW-10)
- Requirement evolution operational
- Tests: 13-stage pipeline scenarios + 59 requirement admission

**Estimated effort:** ~4,000 LOC (discovery, extraction, deduplication, conflict detection, admission, tests)

**Timeline:** 4-5 weeks (implementation + requirement migration + testing)

---

**Item 3-B-3: REQ-NEW-02 (Architectural Assumption Detection)**

**Requirement:** Detect hardcoded patterns, fixed ontologies, mandatory claims (AA-1 through AA-5)

**Dependencies:**
- ⚠️ UKAP registration (owner must exist)
- ✅ Verification Intelligence (AST parsing infrastructure—reuse)

**Blocks:**
- Continuous compliance monitoring (assumption detection in CI/CD)

**Risk:** **MEDIUM** (preventive measure, not blocking current work)

**Rollback strategy:** Remove assumption detector (revert to manual architectural reviews)

**Evidence required:**
- Assumption detector operational (AA-1 through AA-5 rules)
- 7 known violations detected (from Phase 6)
- False positive rate < 20%

**Implementation prerequisite:**
1. UKAP registered
2. AA-1 through AA-5 detection rules formalized
3. Verification Intelligence AST parsing available (reuse)

**Validation evidence required:**
- Test: Detect `KnowledgeKind` closure (Violation 1—AA-1 rule)
- Test: Detect `UniversalContextKind` enumeration (Violation 2—AA-2 rule)
- Test: Detect `MutationClass` fixed count (Violation 4—AA-1 rule)
- Test: Detect structural pattern hierarchy claim (Violation 3—AA-4 rule)
- Test: False positive check (legitimate closure not flagged)
- Integration test: Scan entire codebase → 7 violations detected

**Closure criteria:**
- Assumption detector operational
- AA-1 through AA-5 rules implemented
- 7 known violations detected
- Tests: 5 detection rules + 7 violation scenarios + false positive check

**Estimated effort:** ~5,000 LOC (AST analysis, pattern matching, 5 detection rules, tests)

**Timeline:** 4-5 weeks (rule implementation + codebase scanning + testing)

---

### §5.3 — TIER 3-C: Certification Capability

**Item 3-C-1: REQ-43 (Persistent Graph Memory Substrate Certification)**

**Requirement:** Certify UPEG implementation (tests + documentation)

**Dependencies:**
- ✅ UPEG implementation exists (assumed, location TBD)

**Blocks:** ❌ None (isolated requirement)

**Risk:** **LOW** (prototype exists, certification administrative)

**Rollback strategy:** N/A (certification, no breaking changes)

**Evidence required:**
- UPEG tests pass (graph operations: create, query, traverse, persist, restore)
- UPEG documentation complete
- UPEG certified (status = CERTIFIED in requirement index)

**Implementation prerequisite:**
1. Locate UPEG implementation (search codebase for "UPEG", "graph memory", "persistent graph")
2. If tests missing: Write tests
3. If documentation missing: Write documentation

**Validation evidence required:**
- Test: Create graph node → persisted
- Test: Query graph → results returned
- Test: Traverse graph → path found
- Test: Persist graph → saved to disk
- Test: Restore graph → loaded from disk

**Closure criteria:**
- UPEG operational (tests pass)
- UPEG documented (API, usage examples)
- REQ-43 status = CERTIFIED

**Estimated effort:** ~500 LOC (tests + documentation, assumes implementation exists)

**Timeline:** 1 week (locate + test + document)

---

## §6 — Tier 4: Integration Capabilities (Depends on Tier 1-3)

### §6.1 — TIER 4-A: Coverage Matrix

**Item 4-A-1: Coverage Matrix Generation**

**Requirement:** Traceability graph (requirement ↔ capability ↔ code ↔ test ↔ evidence)

**Dependencies:**
- ⚠️ REQ-NEW-04 (requirement universe—requirements must be machine-readable)
- ✅ 45 programmes (capabilities exist)
- ✅ Code artifacts (exist)
- ✅ Test suite (5,400+ tests exist)

**Blocks:**
- Gap detection (automatic gap identification)
- MIP regeneration (work item generation from gaps)

**Risk:** **HIGH** (blocks gap detection and MIP regeneration)

**Rollback strategy:** Remove coverage matrix, revert to manual traceability

**Evidence required:**
- Coverage matrix operational (10 mappings from Phase 7):
  1. Requirement ↔ Capability
  2. Capability ↔ Code
  3. Code ↔ Test
  4. Requirement ↔ Test
  5. Requirement ↔ Gate
  6. Principle ↔ Requirement
  7. Goal ↔ Invariant
  8. Invariant ↔ Requirement
  9. Decision ↔ Requirement
  10. Capability ↔ Programme

**Implementation prerequisite:**
1. Requirement universe operational (REQ-NEW-04)
2. Programme inventory complete (45 programmes)
3. Coverage analysis algorithm designed

**Validation evidence required:**
- Test: Query coverage (REQ-01 → which capabilities implement?)
- Test: Reverse query (capability X → which requirements discharged?)
- Test: Gap detection (requirements with no implementation)
- Test: Orphan detection (code with no requirements)

**Closure criteria:**
- Coverage matrix operational (10 mappings)
- 59 requirements mapped to capabilities
- Tests: 4 coverage query scenarios pass

**Estimated effort:** ~4,000 LOC (coverage analysis, mapping generation, gap detection, tests)

**Timeline:** 4-5 weeks (traceability analysis + testing)

---

### §6.2 — TIER 4-B: Gap Detection

**Item 4-B-1: Automatic Gap Detection**

**Requirement:** Scan coverage matrix, detect unmapped requirements, validation gaps, principle enforcement gaps

**Dependencies:**
- ⚠️ Coverage matrix operational (Item 4-A-1)
- ⚠️ REQ-NEW-01 (principle assimilation—for principle gap detection)

**Blocks:**
- MIP regeneration (gap detection feeds work item generation)

**Risk:** **HIGH** (blocks MIP regeneration)

**Rollback strategy:** Remove gap detector, revert to manual gap identification

**Evidence required:**
- Gap detector operational (5 gap types from Phase 7):
  1. Implementation gap (requirement with no code)
  2. Validation gap (code with no tests)
  3. Coverage gap (capability with unknown requirement discharge)
  4. Principle gap (principle with no enforcement)
  5. Evolution gap (knowledge change, MIP doesn't update)

**Implementation prerequisite:**
1. Coverage matrix operational
2. Principle assimilation operational (for principle gap detection)

**Validation evidence required:**
- Test: Detect implementation gap (requirement X has no code)
- Test: Detect validation gap (code Y has no tests)
- Test: Detect principle gap (UAP-001 enforcement unmeasured)
- Test: Detect current gaps (2 OPEN GAPs: REQ-28, REQ-43—should detect these)

**Closure criteria:**
- Gap detector operational (5 gap types)
- Current gaps detected (2 OPEN GAPs + any new gaps)
- Tests: 5 gap detection scenarios pass

**Estimated effort:** ~3,000 LOC (gap analysis algorithms, 5 gap types, tests)

**Timeline:** 3 weeks (implementation + testing)

---

## §7 — Tier 5: Plan Regeneration (Depends on Tier 1-4)

### §7.1 — TIER 5-A: MIP Regeneration

**Item 5-A-1: Master Implementation Plan Regeneration**

**Requirement:** Automatic MIP regeneration from knowledge universes + coverage matrix + gap detection

**Dependencies:**
- ⚠️ REQ-NEW-01 (principle universe)
- ⚠️ REQ-NEW-04 (requirement universe)
- ⚠️ Coverage matrix (Item 4-A-1)
- ⚠️ Gap detection (Item 4-B-1)

**Blocks:** ❌ None (final tier)

**Risk:** **MEDIUM** (MIP regeneration is continuous improvement, not blocking)

**Rollback strategy:** Remove MIP regeneration, revert to manual planning

**Evidence required:**
- MIP regeneration pipeline operational (8 steps from Phase 7):
  1. Aggregate knowledge sources
  2. Compute coverage matrix
  3. Detect gaps
  4. Generate work items
  5. Prioritize work items
  6. Resolve dependencies
  7. Aggregate evidence
  8. Generate MIP

**Implementation prerequisite:**
1. Principle universe operational (REQ-NEW-01)
2. Requirement universe operational (REQ-NEW-04)
3. Coverage matrix operational (Item 4-A-1)
4. Gap detection operational (Item 4-B-1)

**Validation evidence required:**
- Test: Knowledge universe change → MIP regenerates
- Test: Gap discovered → work item added to MIP
- Test: Gap certified → work item removed from MIP
- Integration test: Full regeneration (aggregate all sources → generate MIP)

**Closure criteria:**
- MIP regeneration operational
- MIP regenerates on knowledge change (trigger-based)
- Generated MIP contains work items (gaps from Phase 1: 10 OPEN GAPs)
- Tests: 8 pipeline steps + integration test

**Estimated effort:** ~9,000 LOC (8-step pipeline, priority algorithm, dependency resolution, evidence aggregation, MIP generation, tests)

**Timeline:** 6-8 weeks (pipeline implementation + testing)

---

## §8 — Dependency Graph Visualization

### §8.1 — Tier Structure

```
TIER 1: CONSTITUTIONAL FOUNDATION (0 dependencies)
├─ 1-A-1: KnowledgeKind decision
├─ 1-B-1: UKAP registration (depends on CEP-002)
└─ 1-B-2: UREE registration (depends on CEP-002)

TIER 2: EXTENSIONS (depends on Tier 1)
├─ 2-A-1: Violation 4 (mutation class extension) → depends on UKAP (1-B-1)
├─ 2-B-1: REQ-28 (context extensibility) → depends on UCKP (exists)
└─ 2-C-1: REQ-NEW-10 (requirement evolution) → depends on UREE (1-B-2), UAUE (exists)

TIER 3: NEW CAPABILITIES (depends on Tier 1-2)
├─ 3-A-1: REQ-NEW-09 (semantic similarity) → depends on UKAP (1-B-1)
├─ 3-A-2: REQ-NEW-07 (determination lifecycle) → depends on UKAP (1-B-1), Violation 4 (2-A-1)
├─ 3-B-1: REQ-NEW-01 (principle assimilation) → depends on UKAP (1-B-1), REQ-NEW-09 (3-A-1), KnowledgeKind (1-A-1)
├─ 3-B-2: REQ-NEW-04 (requirement universe) → depends on UREE (1-B-2), REQ-NEW-09 (3-A-1), REQ-NEW-10 (2-C-1)
├─ 3-B-3: REQ-NEW-02 (assumption detection) → depends on UKAP (1-B-1)
└─ 3-C-1: REQ-43 (UPEG certification) → depends on UPEG (exists)

TIER 4: INTEGRATION (depends on Tier 1-3)
├─ 4-A-1: Coverage matrix → depends on REQ-NEW-04 (3-B-2)
└─ 4-B-1: Gap detection → depends on Coverage matrix (4-A-1), REQ-NEW-01 (3-B-1)

TIER 5: PLAN REGENERATION (depends on Tier 1-4)
└─ 5-A-1: MIP regeneration → depends on REQ-NEW-01 (3-B-1), REQ-NEW-04 (3-B-2), Coverage matrix (4-A-1), Gap detection (4-B-1)
```

### §8.2 — Critical Path

```
KnowledgeKind decision (1-A-1)
    ↓
UKAP registration (1-B-1)
    ↓
Semantic similarity (3-A-1)
    ↓
Principle assimilation (3-B-1)
    ↓
Gap detection (4-B-1)
    ↓
MIP regeneration (5-A-1)
```

**Critical path duration:** ~18 months (from Phase 3/7 estimates)

**Bottleneck:** KnowledgeKind decision (constitutional process—duration uncertain)

---

### §8.3 — Parallel Paths

**Path A (Requirement universe):**
```
UREE registration (1-B-2)
    ↓
Requirement evolution (2-C-1)
    ↓
Requirement universe (3-B-2)
    ↓
Coverage matrix (4-A-1)
```

**Path B (Determination governance):**
```
UKAP registration (1-B-1)
    ↓
Mutation class extension (2-A-1)
    ↓
Determination lifecycle (3-A-2)
```

**Path C (Assumption detection):**
```
UKAP registration (1-B-1)
    ↓
Assumption detection (3-B-3)
```

**Path D (Context + UPEG):**
```
Context extensibility (2-B-1) [parallel, independent]
UPEG certification (3-C-1) [parallel, independent]
```

**Parallel execution opportunity:** Paths A, B, C, D can execute in parallel after Tier 1 complete.

---

## §9 — Risk Analysis per Item

### §9.1 — High-Risk Items (Blocking Multiple Dependencies)

**High-Risk Item 1: KnowledgeKind decision (1-A-1)**
- **Blocks:** 2 capabilities (REQ-NEW-01, REQ-NEW-04)
- **Risk:** Constitutional decision timing uncertain
- **Mitigation:** Parallel implementation of alternative architecture (principles/requirements as descriptive artifacts)

**High-Risk Item 2: UKAP registration (1-B-1)**
- **Blocks:** 4 capabilities (REQ-NEW-01, REQ-NEW-02, REQ-NEW-07, REQ-NEW-09)
- **Risk:** Constitutional approval delay
- **Mitigation:** Prepare UKAP dashboard in advance, expedite approval process

**High-Risk Item 3: Semantic similarity (3-A-1)**
- **Blocks:** 2 capabilities (REQ-NEW-01, REQ-NEW-04)
- **Risk:** Embedding model complexity, performance tuning
- **Mitigation:** Start with simple LLM-based similarity (OpenAI API), optimize later

**High-Risk Item 4: Coverage matrix (4-A-1)**
- **Blocks:** 2 capabilities (gap detection, MIP regeneration)
- **Risk:** Traceability analysis complexity
- **Mitigation:** Start with manual mapping (59 requirements), automate incrementally

### §9.2 — Medium-Risk Items

**Medium-Risk Item 1: Requirement universe (3-B-2)**
- **Risk:** Requirement migration complexity (49 existing requirements)
- **Mitigation:** Incremental migration (10 requirements at a time)

**Medium-Risk Item 2: Principle assimilation (3-B-1)**
- **Risk:** Enforcement validation complexity (how to validate UAP-001?)
- **Mitigation:** Start with measurable principles (UIEP-001: perpetual evolution), defer complex validation

**Medium-Risk Item 3: Gap detection (4-B-1)**
- **Risk:** False positive rate (legitimate gaps vs. noise)
- **Mitigation:** Threshold tuning, manual review of first 100 gaps

### §9.3 — Low-Risk Items

**Low-Risk Item 1: REQ-28 (context extensibility)**
- **Risk:** Minimal (extension or validation test)
- **Mitigation:** N/A (straightforward)

**Low-Risk Item 2: REQ-43 (UPEG certification)**
- **Risk:** Minimal (certification of existing prototype)
- **Mitigation:** N/A (locate + test + document)

**Low-Risk Item 3: Violation 4 (mutation class extension)**
- **Risk:** Minimal (enum extension)
- **Mitigation:** N/A (straightforward)

---

## §10 — Rollback Strategies

### §10.1 — Tier 1 Rollback

**KnowledgeKind decision rollback:**
- **Action:** If reopened, revert to closure (restore UCRD-001 justification)
- **Precondition:** No principles/requirements stored as CKOs yet
- **Impact:** Blocks principle/requirement canonicalization permanently

**UKAP registration rollback:**
- **Action:** Deregister programme (reverse CEP-002 Article 28 process)
- **Precondition:** No capabilities implemented yet, no artifacts adopted yet
- **Impact:** Orphan artifacts remain orphan, capabilities unowned

**UREE registration rollback:**
- **Action:** Deregister programme (reverse CEP-002 Article 28 process)
- **Precondition:** No requirements migrated to UREE yet
- **Impact:** Requirements remain in manual markdown table

### §10.2 — Tier 2 Rollback

**Mutation class extension rollback:**
- **Action:** Remove 9th class (GOVERNED_ANALYSIS), revert to 8 classes
- **Precondition:** No determinations classified as GOVERNED_ANALYSIS yet
- **Impact:** Determination governance blocked

**Context extensibility rollback:**
- **Action:** Remove extension mechanism (if added)
- **Precondition:** No 17th context kind added yet
- **Impact:** 16 context kinds remain fixed

**Requirement evolution rollback:**
- **Action:** Remove requirement subject type from evolution ledger
- **Precondition:** No requirements tracked in evolution ledger yet
- **Impact:** Requirement evolution not tracked

### §10.3 — Tier 3 Rollback

**Semantic similarity rollback:**
- **Action:** Remove semantic similarity engine
- **Precondition:** No automated deduplication in use yet
- **Impact:** Revert to manual deduplication

**Determination lifecycle rollback:**
- **Action:** Remove determination lifecycle
- **Precondition:** No determinations in lifecycle tracking yet
- **Impact:** Determinations remain untracked

**Principle assimilation rollback:**
- **Action:** Delete principle registry (or remove PRINCIPLE kind if CKO approach)
- **Precondition:** No principles assimilated yet
- **Impact:** Principles remain as declarations (UAP-001, UIEP-001)

**Requirement universe rollback:**
- **Action:** Delete requirement universe, revert to markdown table
- **Precondition:** No requirements migrated yet (or export requirements back to markdown)
- **Impact:** Requirements remain manual

**Assumption detection rollback:**
- **Action:** Remove assumption detector
- **Precondition:** No automated compliance monitoring yet
- **Impact:** Revert to manual architectural reviews

### §10.4 — Tier 4 Rollback

**Coverage matrix rollback:**
- **Action:** Remove coverage matrix
- **Precondition:** No gap detection or MIP regeneration in use yet
- **Impact:** Revert to manual traceability

**Gap detection rollback:**
- **Action:** Remove gap detector
- **Precondition:** No automated gap identification in use yet
- **Impact:** Revert to manual gap tracking

### §10.5 — Tier 5 Rollback

**MIP regeneration rollback:**
- **Action:** Remove MIP regeneration pipeline
- **Precondition:** No automated planning in use yet
- **Impact:** Revert to manual MIP curation

---

## §11 — Evidence Requirements per Tier

### §11.1 — Tier 1 Evidence

**KnowledgeKind decision evidence:**
- Constitutional decision document (CEU or designated authority)
- Decision rationale (reopen or accept closure)
- Publication in ADR or UCDA decision

**UKAP registration evidence:**
- Programme dashboard (`00-MASTER/UKAP-XXXXXX/00-UKAP-DASHBOARD.md`)
- CEP-002 Article 28 registration record
- Ownership declaration (principles, determinations, assumption detection, semantic similarity)

**UREE registration evidence:**
- Programme dashboard (`00-MASTER/UREE-XXXXXX/00-UREE-DASHBOARD.md`)
- CEP-002 Article 28 registration record
- Ownership declaration (requirements, requirement universe)

### §11.2 — Tier 2 Evidence

**Mutation class extension evidence:**
- `MutationClass` enum updated (9 classes)
- Tests pass (52 tests: 49 existing + 3 new)
- `mutation-governance-boundary.json` updated

**Context extensibility evidence:**
- Test: Add 17th context kind (pass)
- Existing context operations still work (pass)

**Requirement evolution evidence:**
- Evolution ledger accepts requirements (code + test)
- Requirement evolution scenarios tested (4 tests pass)

### §11.3 — Tier 3 Evidence

**Semantic similarity evidence:**
- Similarity engine operational (API available)
- Duplicate detection tests pass (10 scenarios)
- False positive rate < 10%

**Determination lifecycle evidence:**
- Lifecycle operational (7 stages)
- 13 session determinations tracked
- Lifecycle transition tests pass (7 scenarios)

**Principle assimilation evidence:**
- Assimilation pipeline operational (8 stages)
- UAP-001 + UIEP-001 assimilated
- Enforcement validation tests pass

**Requirement universe evidence:**
- Requirement universe operational
- 59 requirements (49 existing + 10 new) migrated
- Admission pipeline tests pass (13 scenarios)

**Assumption detection evidence:**
- Assumption detector operational (AA-1 through AA-5)
- 7 known violations detected
- False positive check passes

**UPEG certification evidence:**
- UPEG tests pass (5 graph operation tests)
- UPEG documentation complete

### §11.4 — Tier 4 Evidence

**Coverage matrix evidence:**
- Coverage matrix operational (10 mappings)
- 59 requirements mapped to capabilities
- Coverage query tests pass (4 scenarios)

**Gap detection evidence:**
- Gap detector operational (5 gap types)
- Current gaps detected (10 OPEN GAPs from Phase 1)
- Gap detection tests pass (5 scenarios)

### §11.5 — Tier 5 Evidence

**MIP regeneration evidence:**
- MIP regeneration pipeline operational (8 steps)
- Generated MIP contains work items (gaps from Phase 1)
- Regeneration tests pass (8 pipeline steps + integration)

---

## §12 — Validation

### §12.1 — Dependency Completeness

**Claim:** All 10 OPEN GAP requirements have dependency analysis

**Evidence:**
- ✅ REQ-28: Tier 2-B-1
- ✅ REQ-43: Tier 3-C-1
- ✅ REQ-NEW-01: Tier 3-B-1
- ✅ REQ-NEW-02: Tier 3-B-3
- ✅ REQ-NEW-04: Tier 3-B-2
- ✅ REQ-NEW-07: Tier 3-A-2
- ✅ REQ-NEW-09: Tier 3-A-1
- ✅ REQ-NEW-10: Tier 2-C-1
- ✅ Violation 4: Tier 2-A-1
- ✅ Coverage matrix + Gap detection + MIP regeneration: Tiers 4-5

**Validation:** ✅ All requirements covered

### §12.2 — Circular Dependency Check

**Claim:** Zero circular dependencies

**Validation method:** Dependency graph traversal (depth-first search for cycles)

**Result:**
- Tier 1 depends on: nothing
- Tier 2 depends on: Tier 1 only
- Tier 3 depends on: Tier 1-2 only
- Tier 4 depends on: Tier 1-3 only
- Tier 5 depends on: Tier 1-4 only

**Cycle detection:** ❌ **NONE** (DAG confirmed—directed acyclic graph)

**Validation:** ✅ Zero circular dependencies

### §12.3 — Critical Path Validation

**Claim:** Critical path is KnowledgeKind → UKAP → Semantic similarity → Principle assimilation → Gap detection → MIP regeneration

**Validation:**
- KnowledgeKind blocks: REQ-NEW-01 (principle assimilation)
- UKAP blocks: REQ-NEW-09 (semantic similarity), REQ-NEW-01, REQ-NEW-02, REQ-NEW-07
- Semantic similarity blocks: REQ-NEW-01, REQ-NEW-04
- Principle assimilation blocks: Gap detection (principle gap detection)
- Gap detection blocks: MIP regeneration
- MIP regeneration blocks: nothing (final tier)

**Critical path confirmed:** ✅ KnowledgeKind → UKAP → Semantic similarity → Principle assimilation → Gap detection → MIP regeneration

---

## §13 — Recommendations

### §13.1 — Immediate Execution Order

**Phase 1: Constitutional foundation (Weeks 1-4)**
1. KnowledgeKind decision (Week 1-2, constitutional process)
2. UKAP registration (Week 3, parallel with UREE)
3. UREE registration (Week 3, parallel with UKAP)

**Phase 2: Quick wins (Weeks 5-8)**
1. Violation 4 (mutation class extension)—3 days
2. REQ-28 (context extensibility)—1-2 days
3. REQ-43 (UPEG certification)—1 week
4. REQ-NEW-10 (requirement evolution)—1 week

**Phase 3: Foundation capabilities (Weeks 9-20)**
1. REQ-NEW-09 (semantic similarity)—2-3 weeks
2. REQ-NEW-07 (determination lifecycle)—1 week (parallel with semantic similarity)
3. REQ-NEW-02 (assumption detection)—4-5 weeks (start after REQ-NEW-09 begins)

**Phase 4: Assimilation capabilities (Weeks 21-36)**
1. REQ-NEW-01 (principle assimilation)—3-4 weeks
2. REQ-NEW-04 (requirement universe)—4-5 weeks (parallel with REQ-NEW-01)

**Phase 5: Integration (Weeks 37-52)**
1. Coverage matrix—4-5 weeks
2. Gap detection—3 weeks (start after coverage matrix begins)

**Phase 6: Plan regeneration (Weeks 53-70)**
1. MIP regeneration—6-8 weeks

**Total duration:** ~70 weeks (~18 months)

### §13.2 — Parallel Execution Strategy

**Parallel Group 1 (after Tier 1 complete):**
- Violation 4 (mutation class extension)
- REQ-28 (context extensibility)
- REQ-43 (UPEG certification)
- REQ-NEW-10 (requirement evolution)

**Parallel Group 2 (after Semantic similarity starts):**
- REQ-NEW-07 (determination lifecycle)
- REQ-NEW-02 (assumption detection)

**Parallel Group 3 (after Semantic similarity complete):**
- REQ-NEW-01 (principle assimilation)
- REQ-NEW-04 (requirement universe)

### §13.3 — Risk Mitigation Priorities

**Priority 1: KnowledgeKind decision early**
- **Action:** Initiate constitutional review immediately (Week 1)
- **Reason:** Longest lead time, blocks 2 major capabilities

**Priority 2: UKAP/UREE registration parallel**
- **Action:** Prepare dashboards in advance, submit simultaneously
- **Reason:** Registration process may take weeks, parallel saves time

**Priority 3: Semantic similarity early**
- **Action:** Start after UKAP registered (don't wait for other dependencies)
- **Reason:** Blocks 2 assimilation capabilities (REQ-NEW-01, REQ-NEW-04)

---

## §14 — Conclusion

### §14.1 — Phase 3 Summary

**Dependency graph complete:** 5-tier hierarchy (Constitutional → Extensions → Capabilities → Integration → Regeneration)

**Critical path:** KnowledgeKind → UKAP → Semantic similarity → Principle assimilation → Gap detection → MIP regeneration

**Critical path duration:** ~18 months

**Circular dependencies:** 0 (DAG confirmed)

**Parallel execution opportunities:** 4 parallel groups identified

**High-risk items:** 4 (KnowledgeKind decision, UKAP registration, Semantic similarity, Coverage matrix)

**Rollback strategies:** Defined for all 5 tiers

**Evidence requirements:** Defined for all items (constitutional decisions, tests, documentation)

### §14.2 — Next Steps

**Immediate:**
- ✅ Phase 3 determination complete
- **Proceed to Phase 4:** 100% Completion Measurement Model

**No implementation yet:** Awaiting explicit approval

---

**STATUS:** Phase 3 (Canonical Implementation Dependency Graph) complete. Proceeding to Phase 4 (100% Completion Measurement Model).
