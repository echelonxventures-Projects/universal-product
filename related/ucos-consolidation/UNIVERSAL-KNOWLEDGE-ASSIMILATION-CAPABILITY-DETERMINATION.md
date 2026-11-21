# UNIVERSAL-KNOWLEDGE-ASSIMILATION-CAPABILITY-DETERMINATION

| Field | Value |
|---|---|
| Status | **CAPABILITY DETERMINATION — PHASE 3 COMPLETE** |
| Authority | **NONE — DERIVED ANALYSIS** |
| Date | 2026-08-22 |
| Baseline | `03179308` (integration/recovery-001) |
| Directive | UCOS Ω∞ — COMPLETE ASSIMILATION CLOSURE (Phase 3) |

---

## §1 — Executive Summary

**Objective:** Determine the complete required capability for universal knowledge assimilation—from discovery through certification and evolution.

**Scope:** Discovery, extraction, normalization, classification, duplicate detection, conflict detection, authority resolution, canonical ownership, requirement binding, implementation binding, validation, certification, evolution.

**Key finding:** **Substantial reusable infrastructure exists. Core capability gap: unified assimilation engine integrating scattered components.**

---

## §2 — Universal Assimilation Pipeline Architecture

### §2.1 — Thirteen-Stage Canonical Pipeline

```
1. DISCOVERY
   ↓
2. EXTRACTION
   ↓
3. NORMALIZATION
   ↓
4. CLASSIFICATION
   ↓
5. DUPLICATE DETECTION
   ↓
6. CONFLICT DETECTION
   ↓
7. AUTHORITY RESOLUTION
   ↓
8. CANONICAL OWNERSHIP
   ↓
9. REQUIREMENT BINDING
   ↓
10. IMPLEMENTATION BINDING
   ↓
11. VALIDATION
   ↓
12. CERTIFICATION
   ↓
13. EVOLUTION
```

**Rationale for 13 stages:** Matches analysis from UNIVERSAL-PRINCIPLE-ASSIMILATION-ANALYSIS.md and REQUIREMENT-UNIVERSE-INTEGRATION-DESIGN-ANALYSIS.md, incorporating both principle and requirement assimilation needs.

### §2.2 — Stage Ownership Mapping

| Stage | Existing Owner | Reusable? | Gap |
|---|---|---|---|
| **1. Discovery** | None (manual) | ❌ No | **GAP:** Automatic discovery from conversation, implementation, tests |
| **2. Extraction** | None (manual) | ❌ No | **GAP:** Structured extraction from unstructured sources |
| **3. Normalization** | Partial (`engine/uckp/vocabulary.py` for vocabularies) | ⚠️ Partial | **GAP:** Semantic normalization for principles/requirements |
| **4. Classification** | UCDA (decisions), REQ index (requirements) | ⚠️ Partial | **GAP:** Unified classification across all knowledge types |
| **5. Duplicate Detection** | None | ❌ No | **GAP:** Intent-based deduplication |
| **6. Conflict Detection** | None | ❌ No | **GAP:** Contradiction detection |
| **7. Authority Resolution** | UCDA (decisions), multiple (scattered) | ⚠️ Fragmented | **GAP:** Unified authority resolution |
| **8. Canonical Ownership** | Programmes (via dashboards) | ✅ Yes | **Minor refinement:** Link to assimilation |
| **9. Requirement Binding** | Manual (in requirement index) | ❌ No | **GAP:** Automatic requirement linkage |
| **10. Implementation Binding** | UCDA (decision → implementation) | ⚠️ Partial | **GAP:** Broader than decisions |
| **11. Validation** | Tests, gates | ✅ Yes | **Minor refinement:** Link to assimilation |
| **12. Certification** | `engine/knowledge/certification.py`, gates | ✅ Yes | **Minor refinement:** Link to assimilation |
| **13. Evolution** | `engine/uckp/evolution.py`, UAUE | ✅ Yes | **Minor refinement:** Accept assimilated objects |

**Summary:** Stages 8, 11, 12, 13 have strong existing owners. Stages 1-7, 9-10 have gaps.

---

## §3 — Stage-by-Stage Capability Analysis

### §3.1 — Stage 1: Discovery

**Purpose:** Identify new knowledge from all sources.

**Discovery sources:**
1. **Conversation** — Principles/requirements discussed in sessions
2. **Implementation** — Constraints discovered during coding
3. **Tests** — Requirements encoded in test assertions
4. **Failures** — Gaps revealed by test/gate failures
5. **Audits** — Findings from architecture reviews
6. **Incidents** — Requirements from production issues (if tracked)
7. **ADRs** — Decisions that imply principles/requirements
8. **Determinations** — Analysis documents revealing gaps
9. **Code comments** — Embedded constraints/assumptions
10. **Documentation** — Principles stated in prose

**Existing capability:**
- ✅ **Manual discovery:** Effective (49 requirements, 2 principles discovered manually)
- ❌ **Automatic discovery:** None

**Gap:** No automatic extraction from conversation transcripts, test code, implementation, or documentation.

**Required components:**
- Conversation analyzer (NLP/LLM-based pattern matching)
- Test assertion analyzer (AST parsing for implicit requirements)
- Code comment analyzer (docstring/comment scanning)
- Documentation scanner (markdown analysis for principles/constraints)

**Implementation complexity:** **HIGH** (NLP/semantic analysis)

### §3.2 — Stage 2: Extraction

**Purpose:** Extract structured knowledge from discovered sources.

**Extraction targets:**
- **Statement:** What must be true / what is the principle
- **Rationale:** Why this matters
- **Scope:** What it applies to
- **Authority:** Who owns this
- **Evidence:** How to validate

**Existing capability:**
- ✅ **Manual extraction:** Effective (analysis documents demonstrate this)
- ❌ **Automatic extraction:** None

**Gap:** No structured extraction from unstructured text.

**Required components:**
- Template matching (for well-structured sources like ADRs)
- NLP extraction (for prose sources like determinations)
- Pattern recognition (for common phrasings: "must", "shall", "require")

**Implementation complexity:** **HIGH** (semantic understanding required)

### §3.3 — Stage 3: Normalization

**Purpose:** Convert variations of same concept to canonical form.

**Normalization targets:**
- **Vocabulary alignment:** "Unknown entity admission" = "Future entity extensibility"
- **Phrasing alignment:** "Must not X" ↔ "Shall avoid X"
- **Scope alignment:** Universal vs. domain-specific
- **Intent alignment:** Same goal, different wording

**Existing capability:**
- ✅ **Vocabulary normalization:** `engine/uckp/vocabulary.py` handles vocabulary terms
- ⚠️ **Semantic normalization:** Partial (manual, no automatic semantic similarity)

**Gap:** No intent-based semantic normalization.

**Required components:**
- Intent extraction (extract core meaning from statement)
- Semantic similarity (compare intents, not strings)
- Canonicalization rules (standard phrasings for common patterns)

**Implementation complexity:** **MEDIUM-HIGH** (embedding model or LLM required)

### §3.4 — Stage 4: Classification

**Purpose:** Determine knowledge type, scope, authority tier.

**Classification dimensions:**
1. **Type:** Principle / Requirement / Constraint / Invariant / Rule / Decision
2. **Scope:** Universal / Domain / Capability / Nucleus / Implementation
3. **Authority:** Constitutional / Architectural / Operational
4. **Binding:** Mandatory / Recommended / Optional
5. **Origin:** Conversation / Implementation / Test / Audit / Incident

**Existing capability:**
- ✅ **Decision classification:** UCDA handles this for decisions
- ✅ **Requirement classification:** Manual categories (A-O) in requirement index
- ❌ **Principle classification:** No systematic classification

**Gap:** No unified classification across all knowledge types.

**Required components:**
- Classification rules (decision tree or rule-based)
- Scope analyzer (determine what artifact applies to)
- Authority analyzer (determine governance tier)

**Implementation complexity:** **MEDIUM** (rule-based, with some semantic analysis)

### §3.5 — Stage 5: Duplicate Detection

**Purpose:** Identify semantically identical knowledge stated differently.

**Duplication types:**
1. **Exact duplicates:** Same wording
2. **Semantic duplicates:** Same intent, different wording
3. **Subset duplicates:** One subsumes the other
4. **Overlapping duplicates:** Partial overlap

**Existing capability:**
- ✅ **Manual deduplication:** Performed (49 requirements, no obvious duplicates)
- ❌ **Automatic deduplication:** None

**Gap:** No intent-based duplicate detection.

**Required components:**
- Intent hashing (content-addressed intent representation)
- Similarity scoring (compare intent similarity 0-100%)
- Merge rules (how to combine duplicates)

**Implementation complexity:** **MEDIUM-HIGH** (semantic similarity required)

### §3.6 — Stage 6: Conflict Detection

**Purpose:** Identify contradictory knowledge.

**Conflict types:**
1. **Direct contradiction:** REQ-A says X must be true, REQ-B says X must be false
2. **Scope conflict:** Universal requirement contradicts domain-specific requirement
3. **Authority conflict:** Two equal-authority sources mandate opposite behavior
4. **Implementation conflict:** Two requirements impossible to satisfy simultaneously

**Existing capability:**
- ✅ **Manual conflict detection:** Performed (no conflicts found in 49 requirements)
- ❌ **Automatic conflict detection:** None

**Gap:** No automatic contradiction detection.

**Required components:**
- Contradiction analyzer (logical inference or pattern matching)
- Scope conflict detector (hierarchical scope checking)
- Constraint solver (determine if requirements are mutually satisfiable)

**Implementation complexity:** **MEDIUM** (logic-based, some constraint solving)

### §3.7 — Stage 7: Authority Resolution

**Purpose:** Determine who owns this knowledge, what tier it belongs to.

**Authority resolution:**
1. **Identify potential owners:** Which programmes/capabilities relate to this knowledge?
2. **Resolve conflicts:** If multiple owners, who has priority?
3. **Assign tier:** Constitutional / Architectural / Operational?
4. **Determine binding:** Mandatory / Recommended / Optional?

**Existing capability:**
- ✅ **Programme authority:** 45 programmes declare ownership
- ✅ **Constitutional authority:** CEP-002 Article 28, CMG
- ⚠️ **Authority resolution:** Fragmented across UCDA, ACEE, manual assignment

**Gap:** No unified authority resolution algorithm.

**Required components:**
- Owner lookup (which programme/capability owns this domain?)
- Conflict resolution rules (priority ordering: constitutional > architectural > operational)
- Authority assignment (based on scope and impact)

**Implementation complexity:** **MEDIUM** (rule-based with some heuristics)

### §3.8 — Stage 8: Canonical Ownership

**Purpose:** Assign knowledge to its canonical owner programme/capability.

**Existing capability:**
- ✅ **Programme ownership:** Well-established
  - UCDA owns decisions
  - ACEE owns goals/invariants
  - UCL owns lifecycle
  - REG-AUTO-001 owns identity
  - Each programme declares its ownership domain

**Gap:** **MINOR** — Need to link assimilated knowledge to owners.

**Required components:**
- Owner assignment (result from Stage 7)
- Ownership record (document who owns what)

**Implementation complexity:** **LOW** (data structure, reuse existing ownership model)

### §3.9 — Stage 9: Requirement Binding

**Purpose:** Link knowledge to requirements it supports/discharges.

**Binding types:**
1. **Principle → Requirements:** Which requirements does this principle imply?
2. **Decision → Requirements:** Which requirements does this decision discharge?
3. **Capability → Requirements:** Which requirements does this capability satisfy?
4. **Test → Requirements:** Which requirements does this test validate?

**Existing capability:**
- ⚠️ **Manual binding:** Present in requirement index (implementation location column)
- ⚠️ **UCDA partial binding:** Decisions link to some requirements informally

**Gap:** No automatic requirement binding.

**Required components:**
- Requirement matcher (which requirements relate to this knowledge?)
- Traceability links (bidirectional: requirement ↔ knowledge)
- Coverage analyzer (which requirements are covered, which are gaps?)

**Implementation complexity:** **MEDIUM** (graph-based traceability)

### §3.10 — Stage 10: Implementation Binding

**Purpose:** Link knowledge to its implementation (code, configuration, documentation).

**Binding types:**
1. **Requirement → Code:** Which code implements this requirement?
2. **Principle → Architecture:** Which architectural elements embody this principle?
3. **Decision → Changeset:** Which commits implemented this decision?
4. **Invariant → Validation:** Which gates check this invariant?

**Existing capability:**
- ✅ **Requirement → Implementation:** Manual links in requirement index (evidence column)
- ✅ **Decision → Implementation:** UCDA tracks this
- ⚠️ **Principle → Implementation:** No systematic tracking

**Gap:** Partial (principles and some requirements not linked to implementation).

**Required components:**
- Code mapper (which files/functions implement this?)
- Architectural mapper (which components embody this?)
- Validation mapper (which tests/gates check this?)

**Implementation complexity:** **MEDIUM-HIGH** (static analysis + traceability graph)

### §3.11 — Stage 11: Validation

**Purpose:** Verify that knowledge is correctly implemented.

**Existing capability:**
- ✅ **Test validation:** 5,400+ tests validate implementation
- ✅ **Gate validation:** 10+ gates validate invariants
- ✅ **Programme validation:** Validation reports in programme dashboards

**Gap:** **MINOR** — Need to link validation results to assimilated knowledge.

**Required components:**
- Validation mapper (which tests validate which knowledge?)
- Evidence collector (gather validation results)
- Pass/fail tracking (which knowledge is validated, which isn't?)

**Implementation complexity:** **LOW** (data collection + mapping)

### §3.12 — Stage 12: Certification

**Purpose:** Certify that knowledge is correctly implemented and validated.

**Existing capability:**
- ✅ **Certification framework:** `engine/knowledge/certification.py`
- ✅ **Gate-based certification:** Multiple gates provide certification
- ✅ **Requirement certification:** 43/49 requirements CERTIFIED

**Gap:** **MINOR** — Need to certify principles (currently only declared, not certified as enforced).

**Required components:**
- Certification criteria (what must be true for knowledge to be certified?)
- Evidence aggregator (collect implementation + validation evidence)
- Certification status tracking (CERTIFIED / IMPLEMENTED / OPEN GAP / etc.)

**Implementation complexity:** **LOW** (reuse existing certification framework)

### §3.13 — Stage 13: Evolution

**Purpose:** Track evolution of knowledge over time.

**Existing capability:**
- ✅ **Evolution tracking:** `engine/uckp/evolution.py` with 15-stage cycle
- ✅ **Append-only ledger:** 780 evolution records
- ✅ **UAUE operational:** Full evolution infrastructure

**Gap:** **NONE** — Evolution infrastructure is complete.

**Required components:**
- Evolution subject extension (accept principle/requirement as evolution subject)
- Evolution record (append-only history of knowledge changes)

**Implementation complexity:** **LOW** (extend existing `EvolutionLedger`)

---

## §4 — Existing Reusable Capabilities

### §4.1 — Strong Reusable Infrastructure

**✅ UCDA-000001 (Decision Assimilation):**
- **Reusable:** Decision lifecycle (9 stages), disposition framework, traceability
- **Components:** `ucda_engine.py`, `ucda-decisions.json`, lifecycle stages
- **Status:** Operational (136 decisions)
- **Adaptation needed:** Extend to handle principles/requirements

**✅ ACEE-000001 (Autonomous Engineering):**
- **Reusable:** Goal → obligation → invariant binding
- **Components:** `acee.py`, goal register, invariant register
- **Status:** Operational (6 goals, 48 invariants)
- **Adaptation needed:** Crosswalk to requirements/principles

**✅ UCL-000001 (Universal Lifecycle):**
- **Reusable:** 49-stage lifecycle, stage graph
- **Components:** `ucl-stage-manifest.json`, lifecycle engine
- **Status:** Operational
- **Adaptation needed:** Map assimilation pipeline stages to UCL stages

**✅ `engine/uckp/evolution.py` (Evolution Ledger):**
- **Reusable:** 15-stage perpetual cycle, append-only ledger
- **Components:** `EvolutionLedger`, `EvolutionRecord`, `EvolutionStage`
- **Status:** Operational (780 records)
- **Adaptation needed:** Accept principle/requirement as subject

**✅ `engine/knowledge/cko.py` (Canonical Knowledge Object):**
- **Reusable:** Knowledge object model, content addressing, provenance
- **Components:** `CanonicalKnowledgeObject`, `DecisionRecord`
- **Status:** Operational (3,513 CKOs)
- **Adaptation needed:** Extend `KnowledgeKind` (blocked by UCRD-001)

**✅ `engine/uckp/vocabulary.py` (Vocabulary Registry):**
- **Reusable:** Open vocabulary model, extensibility testing
- **Components:** `VocabularyRegistry`, `Vocabulary`, `Term`
- **Status:** Operational (154 tests)
- **Adaptation needed:** Register new vocabularies (principle types, etc.)

**✅ REG-AUTO-001 (Identity Minting):**
- **Reusable:** Identity allocation, append-only ledger
- **Components:** `ukb.py`, `id-ledger.json`, `deterministic_id()`
- **Status:** Operational (6,178 IDs)
- **Adaptation needed:** Mint IDs for assimilated knowledge (if eligible)

### §4.2 — Partial Reusable Infrastructure

**⚠️ Requirement index (UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md):**
- **Reusable:** Status vocabulary, category structure, evidence links
- **Components:** Markdown table with 49 requirements
- **Status:** Manual curation
- **Adaptation needed:** Convert to machine-readable, enable automatic updates

**⚠️ `engine/verification_intelligence/` (Impact Analysis):**
- **Reusable:** Dependency graph, coupling detection, escalation rules
- **Components:** `ImpactGraph`, `analyse()`, coupling detection
- **Status:** Operational (57 tests)
- **Adaptation needed:** Extend to map knowledge → affected surfaces

**⚠️ `platform/repository_intelligence/mutation_classification.py`:**
- **Reusable:** Classification engine, rule-based governance
- **Components:** `classify()`, `mutation-governance-boundary.json`
- **Status:** Operational (49 tests, 8 classes)
- **Adaptation needed:** Extend to classify knowledge artifacts

---

## §5 — Missing Capabilities

### §5.1 — High-Priority Missing Capabilities

**❌ Semantic Similarity Engine:**
- **Purpose:** Compare intent of two knowledge statements
- **Use:** Duplicate detection (Stage 5), normalization (Stage 3)
- **Complexity:** HIGH (requires embedding model or LLM)
- **Blocker:** No semantic similarity capability exists in repository

**❌ Conversation Knowledge Extractor:**
- **Purpose:** Extract principles/requirements from conversation transcripts
- **Use:** Discovery (Stage 1), extraction (Stage 2)
- **Complexity:** HIGH (NLP/LLM required)
- **Blocker:** No conversation analysis capability exists

**❌ Test → Requirement Analyzer:**
- **Purpose:** Extract implicit requirements from test code
- **Use:** Discovery (Stage 1), requirement binding (Stage 9)
- **Complexity:** MEDIUM-HIGH (AST analysis + semantic understanding)
- **Blocker:** No test analysis capability beyond manual review

**❌ Conflict Detector:**
- **Purpose:** Identify contradictory knowledge
- **Use:** Conflict detection (Stage 6)
- **Complexity:** MEDIUM (logical inference + pattern matching)
- **Blocker:** No automatic conflict detection capability

### §5.2 — Medium-Priority Missing Capabilities

**❌ Code → Knowledge Analyzer:**
- **Purpose:** Extract architectural constraints from code
- **Use:** Discovery (Stage 1), implementation binding (Stage 10)
- **Complexity:** HIGH (static analysis + semantic understanding)
- **Blocker:** No code analysis for implicit knowledge extraction

**❌ Architectural Assumption Scanner:**
- **Purpose:** Detect hardcoded patterns, mandatory claims
- **Use:** Discovery (Stage 1), principle validation
- **Complexity:** MEDIUM (AST + pattern matching)
- **Blocker:** Proposed in UAAD but not implemented

**❌ Coverage Matrix Generator:**
- **Purpose:** Map knowledge → capability → implementation → test → evidence
- **Use:** Implementation binding (Stage 10), validation (Stage 11)
- **Complexity:** MEDIUM (graph-based traceability)
- **Blocker:** No automatic coverage matrix generation

---

## §6 — Required Components Summary

### §6.1 — New Components Required

| Component | Purpose | Stages Used | Complexity | Dependency |
|---|---|---|---|---|
| **Semantic Similarity Engine** | Intent comparison | 3, 5 | HIGH | Embedding model or LLM |
| **Conversation Extractor** | Extract from transcripts | 1, 2 | HIGH | NLP/LLM |
| **Test Analyzer** | Extract requirements from tests | 1, 9 | MEDIUM-HIGH | AST parser |
| **Conflict Detector** | Find contradictions | 6 | MEDIUM | Logic engine |
| **Authority Resolver** | Assign ownership | 7 | MEDIUM | Rule engine |
| **Requirement Binder** | Link knowledge ↔ requirements | 9 | MEDIUM | Graph database |
| **Implementation Binder** | Link knowledge ↔ code | 10 | MEDIUM-HIGH | Static analysis |
| **Coverage Matrix** | Traceability graph | 9, 10, 11 | MEDIUM | Graph database |
| **Knowledge Classifier** | Type/scope/authority | 4 | MEDIUM | Rule engine |
| **Intent Normalizer** | Canonical form | 3 | MEDIUM-HIGH | Semantic similarity |

### §6.2 — Existing Components to Extend

| Component | Extension Needed | Complexity | Blocker |
|---|---|---|---|
| **`CanonicalKnowledgeObject`** | Add `PRINCIPLE`, `REQUIREMENT` to `KnowledgeKind` | LOW | UCRD-001 review |
| **`EvolutionLedger`** | Accept principle/requirement as subject | LOW | None |
| **`VocabularyRegistry`** | Register 6+ new vocabularies | LOW | None |
| **UCDA lifecycle** | Extend to principles/requirements | MEDIUM | Design integration |
| **Requirement index** | Convert to machine-readable | LOW | None |

---

## §7 — Implementation Sequencing

### §7.1 — Phase 1: Foundation (Months 1-2)

**Prerequisites:**
1. `KnowledgeKind` extension decision (UCRD-001 review)
2. Vocabulary registration authority

**Deliverables:**
1. Extend `CanonicalKnowledgeObject` with `PRINCIPLE`, `REQUIREMENT` kinds
2. Register 6+ new vocabularies (principle types, requirement types, etc.)
3. Convert requirement index to machine-readable format
4. Design unified assimilation architecture

**Effort:** ~2,000 LOC

### §7.2 — Phase 2: Manual Assimilation (Months 3-4)

**Prerequisites:**
1. Phase 1 complete

**Deliverables:**
1. Manual principle assimilation (UAP-001, UIEP-001, + conversation principles)
2. Manual requirement assimilation (import 49 existing requirements)
3. Authority resolution rules
4. Classification rules
5. Basic duplicate detection (exact matches)

**Effort:** ~3,000 LOC

### §7.3 — Phase 3: Semantic Capabilities (Months 5-7)

**Prerequisites:**
1. Phase 2 complete
2. Semantic similarity approach decided (embedding model or LLM)

**Deliverables:**
1. Semantic similarity engine
2. Intent-based duplicate detection
3. Semantic normalization
4. Conflict detection (basic)

**Effort:** ~4,000 LOC

### §7.4 — Phase 4: Automatic Discovery (Months 8-10)

**Prerequisites:**
1. Phase 3 complete

**Deliverables:**
1. Conversation extractor
2. Test analyzer (AST-based requirement extraction)
3. Code analyzer (architectural constraint extraction)
4. Integration with assimilation pipeline

**Effort:** ~5,000 LOC

### §7.5 — Phase 5: Traceability & Coverage (Months 11-12)

**Prerequisites:**
1. Phase 4 complete

**Deliverables:**
1. Requirement binding (knowledge ↔ requirements)
2. Implementation binding (knowledge ↔ code)
3. Coverage matrix generator
4. Gap analysis automation
5. MIP regeneration integration

**Effort:** ~4,000 LOC

**Total estimated effort:** ~18,000 LOC over 12 months

---

## §8 — Dependencies

### §8.1 — Critical Path

```
KnowledgeKind decision (UCRD-001)
    ↓
Vocabulary registration
    ↓
CKO extension (PRINCIPLE, REQUIREMENT kinds)
    ↓
Manual assimilation (Phase 2)
    ↓
Semantic similarity decision
    ↓
Semantic capabilities (Phase 3)
    ↓
Automatic discovery (Phase 4)
    ↓
Traceability & Coverage (Phase 5)
```

### §8.2 — Blocking Dependencies

**Blocker 1: `KnowledgeKind` extension**
- **Blocks:** All principle/requirement assimilation
- **Decision needed:** UCRD-001 review to open `KnowledgeKind`
- **Alternative:** Use descriptive artifact naming (no canonical representation)

**Blocker 2: Semantic similarity approach**
- **Blocks:** Duplicate detection, normalization, conflict detection
- **Decision needed:** Embedding model vs. LLM vs. rule-based
- **Alternative:** Manual deduplication (current state)

**Blocker 3: Conversation access**
- **Blocks:** Conversation knowledge extraction
- **Decision needed:** How to access session transcripts
- **Alternative:** Manual extraction (current state)

### §8.3 — Non-Blocking Dependencies

**Nice-to-have 1: Static analysis tooling**
- **Enhances:** Code → knowledge extraction, implementation binding
- **Not blocking:** Can do manual code review

**Nice-to-have 2: Graph database**
- **Enhances:** Traceability, coverage matrix
- **Not blocking:** Can use in-memory graphs or simple data structures

---

## §9 — Validation

### §9.1 — Acceptance Criteria

**For universal knowledge assimilation capability to be OPERATIONAL:**

1. ✅ **13-stage pipeline defined:** Discovery → Evolution stages identified
2. ✅ **Existing capabilities mapped:** Reusable infrastructure identified
3. ✅ **Missing capabilities identified:** 10 new components + 5 extensions required
4. ✅ **Dependencies mapped:** Critical path identified
5. ✅ **Implementation sequence:** 5-phase plan with effort estimates
6. ⚠️ **No implementation performed:** Analysis only (as directed)

**Current status:** **CAPABILITY DETERMINATION COMPLETE**

### §9.2 — Evidence

| Claim | Evidence | Status |
|---|---|---|
| "Substantial reusable infrastructure exists" | 7 operational capabilities identified (§4.1) | ✅ VERIFIED |
| "10 new components required" | Detailed component list (§6.1) | ✅ DOCUMENTED |
| "`KnowledgeKind` blocks implementation" | UCRD-001 adjudication, closed by design | ✅ VERIFIED |
| "18,000 LOC estimated" | Phase-by-phase breakdown (§7) | ⚠️ ESTIMATE |

---

## §10 — Risk Assessment

| Risk | Severity | Mitigation |
|---|---|---|
| **`KnowledgeKind` remains closed** | **CRITICAL** | Alternative: descriptive artifact naming, no canonical representation |
| **Semantic similarity too expensive** | HIGH | Alternative: rule-based matching, accept lower recall |
| **Conversation access unavailable** | MEDIUM | Alternative: manual extraction (current state) |
| **Implementation too complex** | MEDIUM | Phased rollout, start with manual assimilation |
| **NLP/LLM integration challenges** | MEDIUM | Start with simpler pattern matching, enhance later |

---

## §11 — Recommendations

### §11.1 — Immediate (No Implementation)

1. ✅ **Phase 3 complete:** This determination document
2. **Proceed to Phases 4-7:** Produce remaining 4 determination documents
3. **No implementation yet:** Wait for explicit approval

### §11.2 — If Approved to Implement

**Priority 1 (Essential):**
- `KnowledgeKind` extension decision
- Manual principle/requirement assimilation (Phase 2)
- Authority resolution rules

**Priority 2 (High Value):**
- Semantic similarity engine
- Intent-based duplicate detection
- Basic conflict detection

**Priority 3 (Nice to Have):**
- Automatic conversation extraction
- Test → requirement analysis
- Full coverage matrix

**Deferrable:**
- Code → knowledge extraction (limited ROI)
- Incident → requirement pipeline (no incident tracking exists)

---

## §12 — Conclusion

**Phase 3 finding:** Universal knowledge assimilation requires 13-stage pipeline. Substantial reusable infrastructure exists (UCDA, ACEE, UCL, Evolution, CKO). Core capability gaps: semantic similarity, automatic discovery, conflict detection.

**Critical dependency:** `KnowledgeKind` extension decision blocks canonical representation of principles/requirements.

**Implementation path:** 5 phases over 12 months, ~18,000 LOC. Start with manual assimilation, add semantic capabilities, then automatic discovery, finally traceability/coverage.

**Next step:** Proceed to Phase 4 (Universal Artifact Lifecycle Determination).

---

**STATUS:** Phase 3 complete. Proceeding to Phase 4.
