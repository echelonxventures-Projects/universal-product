# 07 — Universal Capability Catalog

**Anchor** `c6c20fb` · **Canonical owner** `intelligence/UCOS-RIE-CAPABILITY-CATALOG.json`
**Authority** NONE — bound by pointer; no second capability catalogue is created here.

---

## 1 · Aggregate

| Measure | Value |
|---|---|
| Capabilities | **66** |
| Evidence present | **66 / 66 (100%)** |
| `implementation_status` | IMPLEMENTED 47 · CERTIFIED 17 · **PLANNED 2** |
| `replacement_prohibited` | 45 of 66 (68%) |
| Reuse disposition | `REUSE/COMPOSE` 28 · `REUSE/EXTEND` 19 · `REUSE_AS_IS/COMPOSE` 17 · `REALIZE_BY_COMPOSITION` 2 |
| Capability records resolving to no unit | **0** (RIB `GAP-CAPABILITY`) |
| Implementation units not covered by a record | **0** (RIB GATE-07 PASS) |
| Duplicate capabilities | **0** (RIB `DUP-CAPABILITY`) |

## 2 · Capability catalogue by owning authority

### EC-1 `engine/` — 17 capabilities · CERTIFIED · `REUSE_AS_IS/COMPOSE` · replacement prohibited

| ID | Capability | Purpose |
|---|---|---|
| RC-05 | `engine` | EC-1 Execution Engine root |
| RC-06 | `engine.acceptance` | EPIC-VAL-002 Universal Repository Acceptance |
| RC-07 | `engine.certification` | EPIC-008 deterministic certification |
| RC-08 | `engine.compiler` | EPIC-003 Universal Compiler (IMP-007) |
| RC-09 | `engine.context` | UCXI-000001 Universal Context Intelligence |
| RC-10 | `engine.determinism` | EPIC-004 Determinism Framework |
| RC-11 | `engine.discovery` | UCOS-EPIC-003 Universal Discovery Engine |
| RC-12 | `engine.factory` | EPIC-006 blueprint-typed Factory Layer |
| RC-13 | `engine.foundation` | IMP-001 Foundation layer |
| RC-14 | `engine.governance` | EPIC-VAL-003 Repository Governance Pipeline |
| RC-15 | `engine.graph` | UCOS-EPIC-002 Universal Knowledge Graph |
| RC-16 | `engine.knowledge` | Universal Knowledge & Decision Architecture |
| RC-17 | `engine.registry` | EPIC-002 read-only Registry Adapter |
| RC-18 | `engine.runtime` | EPIC-005 Runtime Assembly (IMP-007 §8) |
| RC-19 | `engine.tests` | EC-1 test surface |
| RC-20 | `engine.universal_certification` | UCOS-EPIC-006 Universal Certification Engine |
| RC-21 | `engine.validation` | EPIC-007 deterministic Validation Layer |

**Consumers:** EC-2 `platform/` (composition), every gate. **Dependencies:** none measured
(RIB `GAP-DEPENDENCY` = 1, member `engine`). **Missing components:** none.
**Readiness:** ready — but 52,668 LOC verified under a 34-package coverage scope only.

### EC-2 `platform/` — 28 capabilities · IMPLEMENTED · EC-2 CLOSED/FROZEN · `REUSE/COMPOSE` · replacement prohibited

| ID | Capability | | ID | Capability |
|---|---|---|---|---|
| RC-31 | `platform` (root) | | RC-45 | `platform.projects` |
| RC-32 | `platform.administration` | | RC-46 | `platform.providers` ○ |
| RC-33 | `platform.artifact_explorer` | | RC-47 | `platform.repository_intelligence` ○ |
| RC-34 | `platform.blueprints` | | RC-48 | `platform.repository_operations` |
| RC-35 | `platform.certification` | | RC-49 | `platform.runtime_operations` |
| RC-36 | `platform.commercial_intelligence` ○ | | RC-50 | `platform.runtime_platform` |
| RC-37 | `platform.coverage` | | RC-51 | `platform.security` |
| RC-38 | `platform.execution_dashboard` | | RC-52 | `platform.tests` |
| RC-39 | `platform.foundation` | | RC-53 | `platform.universal_portal` |
| RC-40 | `platform.generation` | | RC-54 | `platform.universal_provider` ○ |
| RC-41 | `platform.identity` | | RC-55 | `platform.universal_validation` |
| RC-42 | `platform.measurement` | | RC-56 | `platform.validation` |
| RC-43 | `platform.observability` ○ | | RC-57 | `platform.validation_intelligence` |
| RC-44 | `platform.portal` ○ | | RC-58 | `platform.workspace` ○ |

○ = **outside the declared coverage source** (7 of 28).

**Consumers:** EC-3 band realizations, portal, gates. **Dependencies:** EC-1 `engine/`.
**Reuse opportunity:** `platform.observability` carries **16 dependents** — the highest fan-in in
the repository and rank 1 on the implementation queue critical path.

### EC-3 Band realizations — 8 capabilities · IMPLEMENTED · `REUSE/EXTEND` · replacement permitted

| ID | Capability | Band | LOC | Tests | Gate scope |
|---|---|---|---|---|---|
| RC-03 / RC-04 | `data` · `data.tests` | Band 10 (Data) | 23,577 | 887 | **outside** |
| RC-59 / RC-60 | `service` · `service.tests` | Band 11 (Service) | 20,464 | 1,038 | **outside** |
| RC-01 / RC-02 | `application` · `application.tests` | Band 12 (Application) | 23,741 | 1,082 | **outside** |
| RC-22 / RC-23 | `infrastructure` · `infrastructure.tests` | Band 13 (Infrastructure) | 22,599 | 821 | **outside** |

**Current state:** all four bands implemented with completion reports (Band 10: 11 · Band 11: 13 ·
Band 12: 11 · Band 13: 11 = **46 unit completion reports**) and `_evidence/` trees.
**Missing components:** none functionally; **all four are absent from `testpaths`, the coverage
source, and the wheel** — 90,381 LOC and 3,828 test functions unexercised by the canonical gate.
**Readiness:** implementation ready; **verification NOT ready**.

### Intelligence — 7 capabilities · IMPLEMENTED · ADDITIVE (AUTHORITY=NONE) · `REUSE/EXTEND`

| ID | Capability | Purpose |
|---|---|---|
| RC-24 | `intelligence` | additive intelligence subsystem root |
| RC-25 | `intelligence.kernel` | shared kernel for derived truth |
| RC-26 | `intelligence.publication` | UCOS-UPI-001 Universal Publication Intelligence |
| RC-27 | `intelligence.realization` | Universal Realization Intelligence |
| RC-28 | `intelligence.research` | UCOS-URI-001 Universal Research Intelligence |
| RC-29 | `intelligence.rie` | Repository Intelligence Engine |
| RC-30 | `intelligence.tests` | test surface — **only 115 test functions for 15,617 LOC** |

**All 7 are outside the coverage source.** Test density is 0.0074 tests/LOC versus 0.032 for
`platform/` — the thinnest-tested subsystem, and the one that produces the derived truth every
governance determination consumes.

### Automation — 3 capabilities · ACTIVE · `REUSE/EXTEND`

| ID | Capability | Location |
|---|---|---|
| RC-61 | `automation/ukb.py` | `00-BOOK/tools/ukb.py` — registration & enforcement |
| RC-62 | `automation/ukbx.py` | `00-BOOK/tools/ukbx.py` — extended registration |
| RC-63 | `automation/register.sh` | `00-BOOK/tools/register.sh` — atomic registration transaction (REG-AUTO-001) |

RC-63 is the **owner of blocker B-1**'s detection; RC-61 owns `UCCEP-F-006` (silent validation
degradation).

### Operational memory — 1 capability

| ID | Capability | Location | Authority |
|---|---|---|---|
| RC-64 | `master-context-system` | `00-MASTER/` (57 programme directories) | ACTIVE (AUTHORITY=NONE) |

### Orchestration specifications — 2 capabilities · **PLANNED** · `REALIZE_BY_COMPOSITION`

| ID | Capability | Location | State |
|---|---|---|---|
| SPEC-CIOA | Constitutional Implementation Orchestration Authority | `02-MASTER/UCOS-COMP-000000-…` | **specification only — no executable code** |
| SPEC-CCE | Constitutional Completeness Engine | `02-MASTER/UCOS-COMP-000001-…` | **specification only — no executable code** |

These are **layer 5 of an 11-layer architecture** — the control plane for everything above them.
Both unbuilt.

## 3 · Missing capabilities — the AEOS execution spine

Twelve declared gaps (`UCOS-RIE-AEOS-READINESS.json.known_spine_gaps`). None has any implementation.

| Gap | Missing capability | Severity |
|---|---|---|
| G-01 | Executable CCE (completeness runtime) | **HIGH** |
| G-02 | Executable CIOA (state / critical-path / next / forecast runtime) | **HIGH** |
| G-03 | Execution scheduler | **HIGH** |
| G-09 | AI adapter layer (multi-executor) | **HIGH** |
| G-04 | Lease manager (concurrency) | MEDIUM |
| G-05 | Execution transaction manager | MEDIUM |
| G-06 | Recovery + resume managers | MEDIUM |
| G-07 | Git orchestrator | MEDIUM |
| G-08 | Unified event-ledger reader | MEDIUM |
| G-11 | Mission control runtime | MEDIUM |
| G-12 | Universal AEOS CLI | MEDIUM |
| G-10 | Human adapter | LOW |

**Recorded verdict:** `FOUNDATION-READY — AEOS may begin as a separately authorized program; NOT
begun here.` **Execution readiness:** `SUBSTRATE-READY · SPINE-NOT-IMPLEMENTED`.

Ready because: certified capability substrate present (EC-1 + EC-2); orchestration and completeness
fully specified; digital twin + append-only ledgers + execution register present; operational memory
and automation present.

## 4 · Execution frontier

| Field | Value |
|---|---|
| Single active frontier | **EC-3 Band 10 (Data)** |
| Next executable capability | EC-3 Band 10 (Data) realization |
| Why | CIOA/lane authority admitted Band 10 as RUNNABLE root; EC-1/EC-2 predecessors CERTIFIED |
| Ready | 1 |
| Blocked | 2 |
| Critical path length | 5 |
| Data-programme artifacts | 153 |

## 5 · Implementation queue (RIB-derived, `max_parallel` = 26)

| Rank | Unit | Dependents | Disposition | Wave |
|---|---|---|---|---|
| 1 | `platform.observability` | **16** | EXTEND | 1 |
| 2 | `intelligence` | 7 | EXTEND | 1 |
| 3 | `platform.universal_provider` | 2 | EXTEND | 1 |
| 4 | `service` | 1 | EXTEND | 1 |
| 5 | `data` | 1 | EXTEND | 1 |
| 6 | `application` | 1 | EXTEND | 1 |
| 7 | `infrastructure` | 1 | EXTEND | 1 |
| 8 | `platform.commercial_intelligence` | 1 | EXTEND | 1 |

Critical path: `platform.observability` → `platform.workspace` → `intelligence` →
`intelligence.rie` → `intelligence.kernel` → `platform.universal_provider` → `platform.portal` →
`intelligence.research` → `application` → `data`.

## 6 · Non-derivable capability facts (declared, not fabricated)

| ID | Fact that cannot be derived | Owner | Reason |
|---|---|---|---|
| `ND-01` | business benefit in monetary or user terms | `00-MASTER/UCMI-000001` | no substrate records benefit as a measured quantity; every located benefit statement is prose |
| `ND-02` | capability phase as a ratified programme phase | `00-MASTER/MCP-003` | phase is recorded as lifecycle status in one place and as authority in another; the two do not agree |
| `ND-03` | supersession of one capability by another | `UCOS-RIE-CAPABILITY-CATALOG.json` | the typed graph records evolution only between registered corpus artifacts, not between capability units |

Recording these as non-derivable rather than guessing is correct practice and is noted as such.

## 7 · Catalog verdict

| Criterion | Verdict |
|---|---|
| Every capability inventoried with purpose, owner, state, reuse | **PASS** — 66/66, evidence 66/66 |
| Zero duplicate capabilities; zero unresolved records | **PASS** |
| Every implementation unit covered by a capability record | **PASS** — RIB GATE-07 |
| Every capability's dependencies measured | **PARTIAL** — `engine` has none in either direction |
| Every capability verified by the canonical gate | **FAIL** — 17 of 66 (bands + intelligence + 7 platform) outside coverage |
| Control-plane capabilities implemented | **FAIL** — CIOA and CCE `PLANNED` |
| Execution-spine capabilities present | **FAIL** — 12 gaps, 4 HIGH |
