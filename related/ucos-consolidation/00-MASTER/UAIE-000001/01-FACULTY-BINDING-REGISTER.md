# Architectural Faculty Binding Register

> AUTHORITY = NONE (DERIVED TRUTH). Exactly one canonical owner per faculty,
> and the proof that every bound home and every named symbol resolves in
> Repository Truth.

| ID | Faculty | Disposition | Canonical owner | Homes | Analyses | Catalogue |
|---|---|---|---|---|---|---|
| `UAIE-FAC-01` | Repository Semantic Graph | **COMPOSE** | `engine/graph` | 3/3 | UAR-RIB-01, UAR-RIE-07 | RC-16, RC-51 |
| `UAIE-FAC-02` | Architectural Reasoning Engine | **REUSE** | `engine/graph/architecture` | 3/3 | UAR-VI-04, UAR-RIB-04 | RC-16 |
| `UAIE-FAC-03` | Dependency Intelligence | **REUSE** | `engine/graph/architecture/dependency_intelligence.py` | 2/2 | UAR-RIE-07, UAR-RIB-04 | RC-16, RC-51 |
| `UAIE-FAC-04` | Ownership Intelligence | **REUSE** | `engine/knowledge/integration/ownership.py` | 2/2 | UAR-CL-01, UAR-VI-01 | RC-18, RC-51 |
| `UAIE-FAC-05` | Duplication Intelligence | **REUSE** | `engine/knowledge/integration/duplication.py` | 3/3 | UAR-RIB-02, UAR-CL-02, UAR-CL-06 | RC-18, RC-51 |
| `UAIE-FAC-06` | Gap Intelligence | **REUSE** | `platform/measurement/gaps.py` | 3/3 | UAR-RIB-03, UAR-CL-03 | RC-46, RC-51 |
| `UAIE-FAC-07` | Evolution Intelligence | **REUSE** | `00-MASTER/UEI-000001/uei_engine.py` | 3/3 | UAR-RIE-04, UAR-RIE-03 | RC-33 |
| `UAIE-FAC-08` | Reuse Intelligence | **REUSE** | `engine/knowledge/integration/reuse.py` | 3/3 | UAR-RIB-06, UAR-RIB-05 | RC-18, RC-51 |
| `UAIE-FAC-09` | Constitutional Intelligence | **REUSE** | `engine/knowledge/integration/constitution.py` | 3/3 | UAR-VI-07, UAR-VI-03 | RC-18 |
| `UAIE-FAC-10` | Completion Intelligence | **COMPOSE** | `platform/validation_intelligence/analyzers.py` | 4/4 | UAR-VI-02, UAR-VI-01 | RC-62, RC-07 |

## Reuse rationale, per faculty

### UAIE-FAC-01 — Repository Semantic Graph

- **Disposition:** COMPOSE
- **Canonical owner:** `engine/graph`
- **Objective:** One semantic graph over the entire repository, with every projection derived from it rather than stored beside it.
- **Bound to:** `engine/graph/model.py`, `engine/graph/engine.py`, `platform/repository_intelligence/graph.py`
- **Symbols verified:** `KnowledgeGraph`, `build_core_graph`, `RepositoryGraph`, `build_graph`
- **Registered analyses reused:** UAR-RIB-01, UAR-RIE-07
- **Registers reasoned over:** UAIE-REG-01, UAIE-REG-02, UAIE-REG-04, UAIE-REG-05, UAIE-REG-16
- **Depends on:** — (foundation)
- **Replacement prohibited by catalogue:** true

Already realised twice at two distinct scopes, and both are bound rather than merged. The certified knowledge graph is built over the canonical registers and is the corpus-scope graph; the repository graph is built over the real import surface and is the code-scope graph. The governing knowledge-graph architecture is explicit that there are several roots but one graph, so a third graph store is exactly what must not be created. This programme adds no node kind, no edge kind and no store.

> **Recorded gap.** No single module bears the name used here. The capability is held by two owners at two scopes and is bound to both; the absence of one merged graph module is recorded rather than closed by building a third.

### UAIE-FAC-02 — Architectural Reasoning Engine

- **Disposition:** REUSE
- **Canonical owner:** `engine/graph/architecture`
- **Objective:** Reason across repository artifacts: stratification, layering inversions, blast radius, critical path, impact prediction and reachability.
- **Bound to:** `engine/graph/architecture/engine.py`, `engine/graph/architecture/algorithms.py`, `engine/graph/architecture/layers.py`
- **Symbols verified:** `ArchitectureIntelligenceEngine`, `strongly_connected_components`, `topological_order`, `condensation`, `LayerDependencyGraph`
- **Registered analyses reused:** UAR-VI-04, UAR-RIB-04
- **Registers reasoned over:** UAIE-REG-02, UAIE-REG-06
- **Depends on:** UAIE-FAC-01
- **Replacement prohibited by catalogue:** true

Already realised as the architecture intelligence engine, which exposes layering, dependency intelligence, blast radius, critical path, impact prediction and semantic reachability over the one corpus graph, and carries pure strongly-connected-component, condensation and topological-order algorithms beside it. Those algorithms are reused, never rewritten: a second implementation of reachability would be a second answer to the same question.

### UAIE-FAC-03 — Dependency Intelligence

- **Disposition:** REUSE
- **Canonical owner:** `engine/graph/architecture/dependency_intelligence.py`
- **Objective:** Detect dependency inconsistencies: cycles, unresolvable edges, inverted layers and the closure of what depends on what.
- **Bound to:** `engine/graph/architecture/dependency_intelligence.py`, `platform/repository_intelligence/discovery.py`
- **Symbols verified:** `DependencyIntelligence`, `detect_circular_dependencies`, `discover_dependencies`
- **Registered analyses reused:** UAR-RIE-07, UAR-RIB-04
- **Registers reasoned over:** UAIE-REG-07
- **Depends on:** UAIE-FAC-01
- **Replacement prohibited by catalogue:** true

Already realised. Dependency intelligence derives transitive dependencies, fan-in, fan-out, hubs and circular-dependency reports over the corpus graph, and the repository dependency dimension derives the same closure over the real import graph. The constitutional dependency plane is separately validated by the meta-constitutional validator's acyclicity invariant, which is bound as evidence rather than reimplemented.

### UAIE-FAC-04 — Ownership Intelligence

- **Disposition:** REUSE
- **Canonical owner:** `engine/knowledge/integration/ownership.py`
- **Objective:** Detect ownership conflicts: a concept with two owners, an owner with no concept, and a contested claim.
- **Bound to:** `engine/knowledge/integration/ownership.py`, `platform/repository_intelligence/discovery.py`
- **Symbols verified:** `OwnershipProtocol`, `discover_ownership`
- **Registered analyses reused:** UAR-CL-01, UAR-VI-01
- **Registers reasoned over:** UAIE-REG-08, UAIE-REG-03
- **Depends on:** UAIE-FAC-01
- **Replacement prohibited by catalogue:** true

Already realised twice and both are bound. The ownership protocol is the fail-closed constitutional path: it requires exactly one owner and finds overlaps, refusing rather than defaulting. The repository ownership dimension derives declared owners from the code surface and marks a contested record. The meta-constitutional validator independently enforces injectivity of the concern-to-owner mapping and that every concern has exactly one located owner; that is bound as evidence, not restated.

### UAIE-FAC-05 — Duplication Intelligence

- **Disposition:** REUSE
- **Canonical owner:** `engine/knowledge/integration/duplication.py`
- **Objective:** Detect duplicate concepts before a second home for one concept is created.
- **Bound to:** `engine/knowledge/integration/duplication.py`, `platform/repository_intelligence/discovery.py`, `00-MASTER/UAKOS-CLOSURE-002/closure_engine.py`
- **Symbols verified:** `DuplicatePreventionEngine`, `detect_duplicates`
- **Registered analyses reused:** UAR-RIB-02, UAR-CL-02, UAR-CL-06
- **Registers reasoned over:** UAIE-REG-09, UAIE-REG-14
- **Depends on:** UAIE-FAC-01
- **Replacement prohibited by catalogue:** true

Already realised three times at three scopes, all bound. The duplicate-prevention engine screens a proposed artifact against the knowledge base and refuses on similarity. The repository duplicate dimension detects surface overlap and duplication across modules. The closure engine detects duplicate concepts, duplicate canonical homes and content-hash duplicates across the corpus, and the repository integration blueprint holds the duplicate register. Nothing here is a fourth detector.

### UAIE-FAC-06 — Gap Intelligence

- **Disposition:** REUSE
- **Canonical owner:** `platform/measurement/gaps.py`
- **Objective:** Detect missing abstractions: structural gaps, completeness gaps, convention gaps and orphan units.
- **Bound to:** `platform/measurement/gaps.py`, `platform/repository_intelligence/discovery.py`, `00-MASTER/UCOS-RIB-001/rib_engine.py`
- **Symbols verified:** `GapEngine`, `GapReport`, `discover_gaps`
- **Registered analyses reused:** UAR-RIB-03, UAR-CL-03
- **Registers reasoned over:** UAIE-REG-17, UAIE-REG-01
- **Depends on:** UAIE-FAC-01, UAIE-FAC-05
- **Replacement prohibited by catalogue:** true

Already realised three times, all bound. The gap engine detects structural and completeness gaps over the truth snapshot and fingerprints the report so a gap set is comparable across runs. The repository gap dimension detects convention gaps over the code surface. The repository integration blueprint holds the gap register and classifies dead engines and unreachable entry points. This programme detects no new gap class of its own.

### UAIE-FAC-07 — Evolution Intelligence

- **Disposition:** REUSE
- **Canonical owner:** `00-MASTER/UEI-000001/uei_engine.py`
- **Objective:** Recommend constitutional evolution: what should change next, and under which located owner.
- **Bound to:** `00-MASTER/UEI-000001/uei_engine.py`, `00-MASTER/UCOS-AEE-001/aee_engine.py`, `00-MASTER/UCEF-000001/ucef_engine.py`
- **Symbols verified:** —
- **Registered analyses reused:** UAR-RIE-04, UAR-RIE-03
- **Registers reasoned over:** UAIE-REG-15, UAIE-REG-04, UAIE-REG-18, UAIE-REG-20
- **Depends on:** UAIE-FAC-02, UAIE-FAC-06
- **Replacement prohibited by catalogue:** true

Already realised and registered as its own programme. Universal evolution intelligence binds the evolution capabilities to their homes; the autonomous evolution engine closes the observe-recommend loop over located owners; the constitutional evolution framework measures the fifteen-stage lifecycle any new construct must traverse; and the evolution governance model holds the normative process. A recommendation engine here would be a second voice on the same question.

### UAIE-FAC-08 — Reuse Intelligence

- **Disposition:** REUSE
- **Canonical owner:** `engine/knowledge/integration/reuse.py`
- **Objective:** Recommend reuse before creation, and refuse creation where a located owner already holds the concern.
- **Bound to:** `engine/knowledge/integration/reuse.py`, `engine/knowledge/integration/pipeline.py`, `platform/repository_intelligence/recommendation.py`
- **Symbols verified:** `ReuseEngine`, `ConstitutionalPipeline`, `RepositoryRecommendationEngine`, `build_recommendations`
- **Registered analyses reused:** UAR-RIB-06, UAR-RIB-05
- **Registers reasoned over:** UAIE-REG-09, UAIE-REG-11
- **Depends on:** UAIE-FAC-04, UAIE-FAC-05
- **Replacement prohibited by catalogue:** true

Already realised three times, all bound. The reuse engine assesses a proposed artifact and returns reuse, extend, compose or create; the constitutional pipeline runs that assessment as a mandatory fail-closed stage so creation cannot bypass it; the repository recommendation engine answers the same question over the code surface and returns reuse candidates; and the repository integration blueprint holds the reuse analysis. This programme's own admission determination was produced by applying this faculty, not by inventing another.

### UAIE-FAC-09 — Constitutional Intelligence

- **Disposition:** REUSE
- **Canonical owner:** `engine/knowledge/integration/constitution.py`
- **Objective:** Verify constitutional consistency: that the constitutional plane holds together and that no artifact claims authority it does not have.
- **Bound to:** `engine/knowledge/integration/constitution.py`, `00-CMG/tools/cmg_validate.py`, `00-MASTER/UCOS-UCAF-001/ucaf_engine.py`
- **Symbols verified:** `IntegrationConstitution`, `INTEGRATION_LAWS`
- **Registered analyses reused:** UAR-VI-07, UAR-VI-03
- **Registers reasoned over:** UAIE-REG-03, UAIE-REG-12
- **Depends on:** UAIE-FAC-01, UAIE-FAC-04
- **Replacement prohibited by catalogue:** true

Already realised at three scopes, all bound. The integration constitution holds the laws that bind each stage of the constitutional path and refuses an ungrounded artifact. The meta-constitutional validator enforces twelve invariants over the constitutional registry with zero hardcoded enumeration members. The constitutional authority framework resolves authority and audits authority conflicts, and is the register to consult before any programme claims authority — including this one, which claims none. Adding a fourth constitutional checker would be the parallel machinery the meta layer forbids.

### UAIE-FAC-10 — Completion Intelligence

- **Disposition:** COMPOSE
- **Canonical owner:** `platform/validation_intelligence/analyzers.py`
- **Objective:** Determine repository completeness, and determine it as a computed verdict rather than a claim.
- **Bound to:** `platform/validation_intelligence/analyzers.py`, `00-MASTER/URRC-000001/urrc_engine.py`, `00-MASTER/UCOS-UTCE-001/utce_engine.py`, `00-MASTER/UCOS-UFEP-001/ufep_engine.py`
- **Symbols verified:** `DimensionAnalyzer`, `RepositoryCompletenessAnalyzer`, `CrossCapabilityConsistencyAnalyzer`
- **Registered analyses reused:** UAR-VI-02, UAR-VI-01
- **Registers reasoned over:** UAIE-REG-13, UAIE-REG-10, UAIE-REG-19
- **Depends on:** UAIE-FAC-03, UAIE-FAC-06, UAIE-FAC-09
- **Replacement prohibited by catalogue:** true

Already realised across four owners and bound to all of them, because completeness is answered at four different scopes and no single one of them is the whole answer. The completeness analyzer answers it as a validation dimension over the intelligence target; the reuse, duplication, conflict, gap and completeness verdicts of the reconciliation programme answer it over located owners; traceability closure answers whether every artifact traces with zero orphans; and freeze eligibility answers whether the repository has reached constitutional completion. A fifth completeness verdict would contradict one of the four.

> **Recorded gap.** No single owner answers completeness for the whole repository. Four located owners answer it at four scopes and all four are bound; the absence of one merged verdict is recorded rather than closed by asserting a fifth.
