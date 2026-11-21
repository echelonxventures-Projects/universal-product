# ADR-0006: KnowledgeKind Closure Affirmation and Alternative Architecture

| Field | Value |
|---|---|
| Status | ACCEPTED |
| Date | 2026-08-22 |
| Authority | UCRD-001 (KnowledgeKind closure decision) |
| Supersedes | None |
| Related | UCRD-001, REQ-46, REQ-47, REQ-15 through REQ-20 |
| Mutation Class | CONSTITUTIONAL_TRUTH |

---

## Context

During Phase 1A execution (UCOS Ω∞ 100% Implementation Readiness), we evaluated whether to reopen KnowledgeKind to add PRINCIPLE and REQUIREMENT kinds, or to accept the existing closure decision (UCRD-001) and continue with alternative architecture.

**Background:**
- UCRD-001 closed KnowledgeKind enumeration to prevent unbounded growth
- Current system has 16 context kinds (MEASUREMENT added post-closure)
- Principles exist as architectural declarations (UAP-001, UIEP-001 → REQ-46, REQ-47)
- Requirements exist as tracked items with programme ownership (54 requirements mapped to programmes)
- Determinations exist as analysis records (158+ documents, Git-tracked)

**Need:**
- REQ-50 (principle assimilation), REQ-52 (requirement universe), REQ-53 (determination lifecycle) require artifact representation
- Question: Should these be CKO kinds (reopen KnowledgeKind) or alternative architecture?

---

## Decision

**We affirm UCRD-001 KnowledgeKind closure and adopt alternative architecture for principles, requirements, and determinations.**

Principles, requirements, and determinations will NOT be added as KnowledgeKind enum values. Instead, they will use descriptive artifact architecture:

1. **Principles** remain architectural declarations (documented, referenced, enforced via architecture)
2. **Requirements** remain programme-owned tracked items (mapped to capabilities, validated via tests)
3. **Determinations** remain analysis records (Git-tracked, immutable, point-in-time)

---

## Rationale

### 1. Blocker Elimination Validated Current Approach

The blocker elimination analysis (BLOCKER-ELIMINATION-DETERMINATION.md) demonstrated that the current architecture is operational:

- **Principles (UAP-001, UIEP-001):** Function as architectural declarations (REQ-46, REQ-47 CERTIFIED)
- **Requirements (54 items):** Mapped to programme owners, complete ownership (blocker §2.6 validation)
- **Determinations (158+ items):** Preserved as analysis records, Git provides evolution control (blocker §3.6 validation)

**Evidence:** Zero operational artifacts lack representation. Current architecture satisfies all functional needs.

### 2. Infinite Expansion Compliance

Reopening KnowledgeKind violates infinite expansion principles:

- **Risk:** Adding PRINCIPLE, REQUIREMENT creates precedent for future additions (ASSUMPTION, CONSTRAINT, GOAL, etc.)
- **Closure pressure:** Each addition increases pressure to close again (bounded enumeration)
- **Alternative:** Descriptive architecture uses metadata, vocabularies, registries (unbounded)

**UAP-001 (Universal Agnostic Architecture):** No entity type should have architectural privilege. Principles-as-kinds privileges principles over other artifact types.

**UIEP-001 (Universal Infinite Evolution Principle):** System must support perpetual evolution. Fixed enum prevents unbounded artifact type evolution.

### 3. Constitutional Consistency

UCRD-001 closed KnowledgeKind for valid architectural reasons:

- Prevent unbounded enum growth
- Encourage descriptive metadata over type proliferation
- Maintain architectural agility (new artifact types without schema migration)

**Reopening contradicts UCRD-001 rationale.** If principles/requirements warrant kinds, then goals, invariants, constraints, assumptions, and future artifact types also warrant kinds → enum explosion.

### 4. Implementation Simplicity

**Current architecture:**
- Zero code change required
- Principles referenced in 45+ programme dashboards
- Requirements mapped to programmes (ownership model operational)
- Determinations preserved in repository (Git tracking operational)

**Reopening requires:**
- Modify `engine/knowledge/cko.py` (add PRINCIPLE, REQUIREMENT to enum)
- Migrate 54 requirements to CKO storage
- Migrate 2 principles to CKO storage
- Migrate 158+ determinations to CKO storage
- Update all references (45+ dashboards, test files, documentation)

**Risk:** Migration complexity, potential data loss, breaking changes to existing capabilities.

### 5. Separation of Concerns

**CKO (Canonical Knowledge Object):** Structured knowledge with provenance, content-addressed storage, graph relationships.

**Principles:** Architectural guidance (declarative, stable, enforcement via architecture)

**Requirements:** System contracts (operational, validated via tests, owned by capabilities)

**Determinations:** Analysis records (point-in-time, immutable, historical reference)

**Assessment:** Principles, requirements, determinations have fundamentally different semantics than CKOs (programmes, capabilities, modules, decisions). Forcing into CKO model creates impedance mismatch.

---

## Consequences

### Positive

✅ **Affirms UCRD-001 closure** — maintains constitutional consistency

✅ **Preserves infinite expansion** — descriptive architecture unbounded

✅ **Zero migration risk** — current architecture operational

✅ **Separation of concerns** — artifacts use appropriate representation

✅ **Implementation simplicity** — no code modification required

### Negative

⚠️ **Heterogeneous architecture** — principles/requirements/determinations not in CKO graph

⚠️ **Different query mechanisms** — CKOs use graph traversal, requirements use programme mapping, determinations use Git

⚠️ **No unified provenance** — CKO provenance model doesn't extend to principles/requirements/determinations

### Mitigations

**Heterogeneous architecture:**
- Document architecture decision (this ADR)
- Explicit artifact type taxonomy (CKO vs. declaration vs. tracked item vs. analysis record)

**Different query mechanisms:**
- Each mechanism appropriate for artifact type (graph for CKOs, ownership for requirements, Git for determinations)
- No need for artificial unification

**No unified provenance:**
- Git provides provenance for file-based artifacts (requirements, determinations, principles in documentation)
- CKO provenance for CKO artifacts
- Accept multi-mechanism provenance as architectural reality

---

## Alternative Architecture Details

### Principles

**Representation:** Architectural declarations in documentation

**Examples:** UAP-001 (no entity privileges), UIEP-001 (perpetual evolution)

**Ownership:** Architecture itself (referenced by programmes, not owned by programmes)

**Lifecycle:** Stable (architectural foundations change rarely)

**Validation:** Enforcement via architecture (assumption detector validates UAP-001, evolution ledger validates UIEP-001)

**Evolution:** Git tracks changes to principle documentation

**Requirements covered:** REQ-46 (UAP-001 enforcement), REQ-47 (UIEP-001 enforcement)

### Requirements

**Representation:** Programme-owned tracked items (requirement index + programme ownership mapping)

**Examples:** REQ-01 (identity allocation), REQ-08 (decision lifecycle), REQ-50 (principle assimilation)

**Ownership:** Programme ownership model (54 requirements mapped to 45+ programmes)

**Lifecycle:** Discovery → Admission → Implementation → Validation → Certification → Closure

**Validation:** Tests validate requirement satisfaction (5,400+ tests)

**Evolution:** Git tracks requirement index changes, evolution ledger extension (REQ-23 work item) for machine-readable evolution

**Requirements covered:** REQ-52 (requirement universe) will manage requirements as tracked items, not CKOs

### Determinations

**Representation:** Analysis records (immutable documents, Git-tracked)

**Examples:** IMPLEMENTATION-READINESS-ASSESSMENT-DETERMINATION.md, BLOCKER-ELIMINATION-DETERMINATION.md

**Ownership:** Repository (no programme owns analysis artifacts)

**Lifecycle:** Point-in-time analysis (superseded, not evolved)

**Validation:** Analysis validation (evidence-based, references executable validation)

**Evolution:** Git tracks creation + supersession (new determinations supersede old)

**Requirements covered:** REQ-53 (determination lifecycle) will manage determinations as analysis records with lifecycle states (DRAFT → ACTIVE → SUPERSEDED → ARCHIVED)

---

## Implementation Guidance

### For Principle Assimilation (REQ-50)

**Do NOT:** Store principles as CKOs

**DO:** 
- Maintain principle registry (principle metadata, enforcement rules)
- Reference principles in documentation
- Validate principle enforcement via assumption detector (REQ-51)
- Track principle evolution via Git

### For Requirement Universe (REQ-52)

**Do NOT:** Store requirements as CKOs

**DO:**
- Maintain requirement registry (requirement metadata, ownership, lifecycle state)
- Map requirements to programme owners
- Validate requirements via tests
- Track requirement evolution via evolution ledger extension (REQ-23 work item)

### For Determination Lifecycle (REQ-53)

**Do NOT:** Store determinations as CKOs

**DO:**
- Maintain determination registry (determination metadata, lifecycle state)
- Preserve determinations as immutable analysis records
- Track supersession relationships (newer determination supersedes older)
- Track determination evolution via Git

---

## Validation

**This decision satisfies:**

✅ **KnowledgeKind decision requirement** (Phase 1A item 1)

✅ **Infinite expansion compliance** (Phase 6 validation)

✅ **Constitutional consistency** (UCRD-001 affirmation)

✅ **Blocker elimination validation** (current architecture operational)

**This decision enables:**

✅ **REQ-50 (principle assimilation)** — principles as declarations with enforcement validation

✅ **REQ-52 (requirement universe)** — requirements as tracked items with programme ownership

✅ **REQ-53 (determination lifecycle)** — determinations as analysis records with lifecycle states

**This decision defers:**

⚠️ **UKAP registration** — defer to Phase 3 (when REQ-50, REQ-51, REQ-53, REQ-54 implementation begins)

⚠️ **UREE registration** — defer to Phase 4 (when REQ-52 implementation begins)

---

## References

- UCRD-001: KnowledgeKind closure decision (original closure)
- REQ-15 through REQ-20: UCKP requirements (CKO model CERTIFIED)
- REQ-46: UAP-001 principle (SUPPORTED)
- REQ-47: UIEP-001 principle (CERTIFIED)
- REQ-50: Principle assimilation (OPEN GAP → implementation uses alternative architecture)
- REQ-52: Requirement universe (OPEN GAP → implementation uses alternative architecture)
- REQ-53: Determination lifecycle (OPEN GAP → implementation uses alternative architecture)
- BLOCKER-ELIMINATION-DETERMINATION.md: Validates current architecture operational
- INFINITE-EXPANSION-SAFETY-MODEL-DETERMINATION.md: Validates infinite expansion compliance

---

## Approval

**Status:** ACCEPTED (2026-08-22)

**Authority:** Constitutional architecture decision (ADR process)

**Supersedes:** None (affirms UCRD-001)

**Effective:** Immediate

---

**Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>**
