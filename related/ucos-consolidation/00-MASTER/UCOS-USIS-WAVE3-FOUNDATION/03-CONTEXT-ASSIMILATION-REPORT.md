# EVO-USIS-W3-FOUNDATION-001 · 03 — Context Assimilation Report

| Field | Value |
|-------|-------|
| ARTIFACT ID | EVO-USIS-W3-F-001-CA (Context Assimilation Report) |
| PROGRAMME | EVO-USIS-W3-FOUNDATION-001 — Wave-3 Constitutional Foundation |
| PROGRAM | UCOS-USIS-001 — Universal Science & Intelligence Substrate |
| CLASSIFICATION | Governed operational-memory determination record. **GOVERNANCE ONLY · READ-ONLY.** Not a corpus artifact. |
| GATE DISCHARGED | **Context Assimilation Gate** — mandatory before any Wave-3 authorization (Reuse-First, LAW USIS-02; Discovery-First) |
| REPOSITORY MUTATION | **OPERATIONAL MEMORY ONLY.** 0 writes to `15-…/`, `00-BOOK/`, frozen streams. |
| AUTHORITY | **NONE — DERIVED.** |
| CONFLICT RULE | Higher frozen/governing instruments prevail. |

> **Purpose.** Discharge the Context Assimilation Gate: enumerate **everything already implemented in the repository that Wave-3 must reuse rather than recreate**, and record an explicit REUSE / EXTEND / NEW decision for every Wave-3 need. Every row is a physical repository observation. Nothing already owned may be re-authored (Knowledge Once, LAW USIS-02; obligations 2/3/8).

---

## PART A — Assimilation scope and method

| Property | Value |
|----------|-------|
| Baseline assimilated | `527485abf00f241a035dbd06062b78c1d9dcde31` (clean tree) |
| Total registered corpus | **1164 artifacts** (`ukb enforce --pre`) |
| USIS corpus | **19 artifacts** (`UCOS-USIS-000001`…`000019`, VOL-024) |
| Graph assimilated | **12,493 edges**, 0 unresolved |
| Software/Infrastructure streams assimilated | 4,425 files across 8 streams (Part D) |
| Operational memory assimilated | `00-MASTER/` (excluded from registration, `config.py:745`) — USIS packages: `UCOS-USIS-001` (14 docs), `WAVE0`, `WAVE1`, `WAVE2` (BPA + 12 blueprints + 9 mission dirs + INTEGRATION + INTEGRATION-READINESS), `WAVE2-AUTH` (5 records) |
| Method | filesystem + registry + graph interrogation; no assumption, no inference from titles alone |

## PART B — Existing reusable **knowledge** (constitutional corpus)

All 19 USIS artifacts are frozen Wave-1/Wave-2 knowledge. Wave-3 **references** them; it may not restate, fork, or re-home any of them.

| Knowledge asset | Universal ID | What Wave-3 reuses from it | Wave-3 decision |
|-----------------|--------------|----------------------------|-----------------|
| USIS-GOV-000 Establishment | `000001` | program standing, founding position, 7th-stream mandate, VOL-024 | **REUSE (reference)** |
| USIS-001 Constitution | `000002` | LAW USIS-00…09, Part D 12-field capability structure, Part E 22-verb contract, Part F 7 invariants | **REUSE** |
| USIS-002 Universe Catalog | `000003` | the 21 universe rows, homes, MIP anchors, concerns, `parent-universe` recursion | **REUSE — this *is* the Universe Registry** |
| USIS-003 Science Catalog | `000005` | the 30 discipline rows + cross-link map | **REUSE — this *is* the Science Registry** |
| USIS-004 Meta-Model | `000004` | 24-tier chain, per-tier contract, conformance rule, agnosticism boundary, Reuse-First rule, recursion guarantee | **REUSE — the single realization spine** |
| USIS-005 Theory/Ontology/Taxonomy | `000006` | theory contract T-1…T-5, ontology framework O-1…O-4 + Ontology Closure rule, taxonomy framework X-1…X-4 + Taxonomy Closure rule, root concept/taxa anchors | **REUSE — per-member instances plug into these rules** |
| USIS-006 Capability Architecture | `000008` | capability node shape, ownership/hierarchy/composition/registration models, lifecycle | **REUSE** |
| USIS-007 Domain Architecture | `000007` | domain/sub-domain node shape, boundaries, ownership closure, recursion, relationship model | **REUSE** |
| USIS-008 Algorithm Architecture | `000010` | algorithm node shape + `binding` boundary | **REUSE** |
| USIS-009 Model Architecture | `000009` | model node shape, versioning, `binding` boundary | **REUSE** |
| USIS-010 Pattern Architecture | `000011` | pattern-as-composition-over-roles | **REUSE** |
| USIS-011 Engine Architecture | `000012` | engine node shape + zero-hard-coding contract | **REUSE** |
| USIS-012 Service Architecture | `000014` | service abstraction/identity/contract/lifecycle/discovery/composition/orchestration | **REUSE** |
| USIS-013 Runtime Architecture | `000013` | runtime node shape, execution semantics, context propagation, governed-autonomy envelope | **REUSE** |
| USIS-014 Validation Architecture | `000017` | Part F obligation classes, Part M 8 cross-layer surfaces, Part O 6 coverage dimensions, verdict semantics | **REUSE — Wave-3 produces records, not architecture** |
| USIS-015 Certification Architecture | `000018` | certification node, gates, authority/SoD, coverage model | **REUSE** |
| USIS-016 Evidence Architecture | `000019` | evidence node, lifecycle, integrity, lineage, retention, traceability | **REUSE** |
| USIS-017 API/SDK Architecture | `000015` | API/SDK node shapes, contract/consumer/provider/versioning/discovery models | **REUSE** |
| USIS-INT-001 Implementation Integration | `000016` | 9-layer → implementation-surface mapping; Part E executable-composition contract | **REUSE — Wave-3 code realizes this contract** |

### B.1 — Reusable operational-memory knowledge (unregistered, governed)
| Asset | Contents Wave-3 reuses | Decision |
|-------|------------------------|----------|
| `00-MASTER/UCOS-USIS-001/05` structure spec | 21-area canonical tree; artifact-sequence table incl. USIS-018/019/020/021; front-matter metadata contract; No-Orphan homing rules | **REUSE (authoritative structure instrument)** |
| `…/06` domain & HI catalog | 42 intelligence domains, 38 HI families, sibling-universe ownership, non-duplication rules | **REUSE (member seed source)** |
| `…/07` operational universes | DAT/ANL/ALG/MDL/LRN/EVO seed member lists; anti-hard-coding rules | **REUSE (member seed source)** |
| `…/09` registry integration manifest | 3-layer registration mechanism; 12 target registries; 12 program registries; No-Orphan proof obligations; determinism/append-only rules | **REUSE (registration contract)** |
| `…/11` proof-obligations register | the 21 fail-closed obligations + check mechanisms + pass criteria | **REUSE (Wave-3 acceptance criteria)** |
| `…/12` roadmap | Wave 0–6 sequence; Wave-3 5-group mission priority; success-criteria mapping | **REUSE (sequencing authority)** |
| `UCOS-USIS-WAVE2/00` BPA record | 14-section blueprint schema; §5.1 ID-namespace resolution; §5.2 VOL-024 governs; §5.3 numbering-vs-dependency-order rule | **REUSE (blueprint schema + collision resolution)** |
| `UCOS-USIS-WAVE2/BLUEPRINTS/*` (12) | constitutional source pattern for each layer | **REUSE (pattern for Wave-3 blueprints)** |
| `UCOS-USIS-WAVE2-AUTH/01–05` | authorization-record pattern; entry preconditions (5 uniform, UCIC-001) | **REUSE (authorization pattern)** |
| `UCOS-USIS-WAVE2/MISSION-*` + `EVO-USIS-014/015/016` | the mission report-set pattern (context delta → structure → implementation → registration → validation → certification → coverage → cross-layer/whole-corpus → repository evidence) | **REUSE (Wave-3 mission deliverable template)** |
| `UCOS-USIS-WAVE0/FREEZE-C4/*` + `freeze_c4_engine.py` | 7-stream execution model; deterministic read-only regeneration | **REUSE (stream closure regeneration)** |
| `UCIC-001` | 15-stage lifecycle, per-stage gates/failure/rollback/evidence, DP-03 forbidden paths, SoD, Output-2/4/5/6 | **REUSE — the sole implementation methodology** |

## PART C — Existing reusable **engines** (executable machinery)

| Engine | Path | Capability observed | Wave-3 decision |
|--------|------|---------------------|-----------------|
| UKB engine | `00-BOOK/tools/ukb.py` | `build` (scan → allocate IDs/pages append-only → emit registries + control tower + graph), `search`, `trace`, `evolve`, `stats`, `validate`, `enforce`, `exec` | **REUSE — sole allocator/registrar. Creating a second allocator is a LAW USIS-02 violation** |
| UKB Advancement engine (Digital Twin) | `00-BOOK/tools/ukbx.py` | `ingest`, `sync`, `twin`, `export`, `search`, `ai`, `intel`, `portal`, `validate`, `certify` | **REUSE — sole twin/certifier** |
| Registration transaction | `00-BOOK/tools/register.sh` | 10-phase atomic all-or-nothing transaction + `--guard` drift gate + `--install-hooks` | **REUSE — sole registration path** |
| Verification entry point | `verify.sh` | ruff gate, pytest+coverage (`--cov-fail-under=90`), coverage report, `enforce --pre`; self-healing venv | **REUSE — sole quality gate** |
| Environment doctor | `doctor.sh`, `scripts/ucos-env.sh` | canonical venv provisioning; single-source ruff gate | **REUSE** |
| Repo operations | `repo-ops.sh`, `repo-operations.json`, `Makefile` | standard operations surface | **REUSE** |
| FREEZE C4 engine | `00-MASTER/UCOS-USIS-WAVE0/freeze_c4_engine.py` | deterministic 7-stream closure regeneration | **REUSE (for stream reconciliation)** |
| Engine stream subsystems | `engine/` — 922 files, **EC-1 certified, frozen (0 writes, DP-03)** | `runtime` 37 py · `knowledge` 30 · `graph` 24 · `compiler` 16 · `factory` 16 · `registry` 16 · `foundation` 12 · `universal_certification` 10 · `certification` 9 · `acceptance` 7 · `discovery` 7 · `governance` 7 · `validation` 7 · `determinism` 4 (+ `tests` 159) | **REUSE BY REFERENCE ONLY — writes forbidden** |
| Platform stream | `platform/` — 1475 files, **EC-2 frozen (0 writes)** | `runtime_platform`, `runtime_operations`, `universal_validation`, `validation_intelligence`, `certification`, `identity`, `generation`, `observability`, `measurement`, `portal`, `universal_portal`, `security`, `coverage`, `repository_operations`, `execution_dashboard`, `artifact_explorer`, `administration`, `blueprints`, `projects` | **REUSE BY REFERENCE ONLY — writes forbidden** |
| Repository Intelligence Engine (RIE) | `intelligence/` — 58 files: `UCOS-RIE-CAPABILITY-CATALOG.json`, `-DEPENDENCY-GRAPH.json`, `-EXECUTION-FRONTIER.json`, `-DIGITAL-TWIN.json`, `-PROGRESS.json`, `-HEALTH.json`, `-MODEL.json`, `-SNAPSHOT.json`, `-AEOS-READINESS.json`, `die/`, `rie/`, `portal.py` | **REUSE — capability catalog + CIOA frontier source for UCIC Stage 1 member selection.** Separate from USIS subject matter (USIS-GOV-000 §5) |

**Determination C.** Wave-3 requires **zero new engines**. Every mechanism Wave-3 needs — identity allocation, registration, classification, graph construction, twin synchronization, validation, certification, portal generation, drift detection, determinism proof, execution registry — already exists and is the sole authority for its concern.

## PART D — Existing reusable **services / runtime / implementation surfaces**

| Stream | Path | Files | Constitutional status (USIS-INT-001 Part B) | Wave-3 decision |
|--------|------|:-----:|---------------------------------------------|-----------------|
| Engine | `engine/` | 922 | EC-1 certified · frozen | **reference only** |
| Platform | `platform/` | 1475 | EC-2 frozen | **reference only** |
| Service | `service/` | 545 | Software stream · referenced | **EXTEND (additive) for tier-19 member code** |
| Infrastructure | `infrastructure/` | 456 | Software stream · referenced | **EXTEND (additive)** |
| Application | `application/` | 457 | Software stream · referenced | **EXTEND (additive)** |
| Intelligence (RIE) | `intelligence/` | 58 | RIE · referenced | **reference only** |
| Knowledge | `knowledge/` | 12 | Software stream · referenced | **EXTEND if required** |
| Data | `data/` | 500 | DATA program + `data/_evidence/<CAP-ID>/` evidence store | **REUSE (evidence store); reference DATA program** |

Runtime hosting for tier 15 is owned by the platform runtime (`08-RUNTIME` / `platform/runtime_platform` / RIE) and is **referenced**, never re-homed (USIS-013 Part P).

## PART E — Existing reusable **governance**

| Instrument | Location | Role Wave-3 reuses | Decision |
|-----------|----------|--------------------|----------|
| UCIC-001 | `00-MASTER/UCIC-001-…md` | **FROZEN v1.0** 15-stage lifecycle; Stage 2 dependency verification; Stage 3 authority + SoD; Stage 4 additive-only/DP-03; Stages 5–9 validation/evidence; Stage 10 certification; Stages 11–15 RIE/twin/registry/commit/production | **REUSE — no capability may bypass it** |
| REG-AUTO-001 | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-REG-AUTO-001-…md` | "Artifact Creation = Artifact Registration"; 7 synchronized registers; §7 Atomic Creation Law | **REUSE** |
| GOV-001-T3 | governance corpus | No-Orphan | **REUSE** |
| GOV-002 | governance corpus | bidirectional traceability | **REUSE** |
| TRACK-001 | governance corpus | fail-closed evidence (absence = NOT-DONE) | **REUSE** |
| STATUS-001 | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-STATUS-001-…md` | status validity gate; non-projection law (existence ≠ completion) | **REUSE** |
| UCI-001 | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-UCI-001-…md` | change intelligence + regeneration standard | **REUSE** |
| AUTH-INF-001 | `00-BOOK/CONTROL-TOWER/UCOS-Ω∞-AUTH-INF-001-…md` | infinite-evolution constitution (CR-INF-001/007/008/009/010) | **REUSE** |
| GOV-INT-001 / GOV-READINESS-001 | `00-BOOK/CONTROL-TOWER/` | single governance architecture; execution readiness | **REUSE** |
| CIOA / CCE | `UCOS-COMP-000000` / `UCOS-COMP-000001` | frontier sequencing / 10 fail-closed certification gates | **REUSE** |
| FREEZE C2/C3/C4 | `99-FREEZE/`, `00-MASTER/UCOS-USIS-WAVE0/FREEZE-C4/` | immutable predecessors + 7-stream successor model | **REUSE (regenerate closure, never edit C2/C3)** |
| CEP instruments | `00-CEP/` (35 registered artifacts) | constitutional evolution protocol incl. CEP-004 validation law, CEP-006 PROVISIONAL tier | **REUSE — frozen, 0 writes** |
| Control Tower | `00-BOOK/CONTROL-TOWER/PROGRAM-CONTROL-TOWER.md`, `UCOS-MASTER-EXECUTION-STATUS-REGISTRY.md`, `UCOS-ROADMAP-RECONCILIATION-REGISTRY.md` | programme status projection | **REUSE (auto-regenerated)** |
| MCP/MCS | `00-MASTER/MCP-001…007`, `MCS-000` | master context/state/execution/decisions/dashboard/traceability/recovery | **REUSE** |
| Operational-memory exclusion | `UCOS-RECON-C1-OPERATIONAL-MEMORY-EXCLUSION.md` + `config.py:745` | governs where programme records may live unregistered | **REUSE — basis for this programme's own placement** |

## PART F — Existing reusable **registries**

| Registry surface | Location | Wave-3 use | Decision |
|------------------|----------|-----------|----------|
| Artifact registry (data) | `00-BOOK/DATA/artifacts.json` (1164 rows) | every member artifact appears here on registration | **REUSE** |
| Identity ledger | `00-BOOK/DATA/id-ledger.json` (append-only, pages to 9489) | universal ID + page allocation | **REUSE — never a second allocator** |
| Relationship graph | `00-BOOK/DATA/relationships.json` (12,493 edges) | Depends-On / Parent / Implements / Authorized-By edges | **REUSE** |
| Control tower / twin / signals / change ledger / volumes / certification | `00-BOOK/DATA/{control-tower,twin,signals,change-ledger,volumes,certification}.json` | synchronized state + certification evidence | **REUSE** |
| Rendered registers | `00-BOOK/REGISTRIES/` — `UNIVERSAL-ARTIFACT`, `UNIVERSAL-PAGE`, `KNOWLEDGE-GRAPH`, `CHANGE-VERSION-LINEAGE`, `VOLUME`, `CERTIFICATION` | human/portal projections | **REUSE (regenerated)** |
| Navigation portal | `00-BOOK/PORTAL/` (per-artifact pages incl. `UCOS-USIS-000001…19`) | no-dead-end navigation | **REUSE (regenerated)** |
| Execution register | EXEC-REG-001 (`.runtime/`, `ukb exec`) — currently **0 executions** | per-member lifecycle instances in the 7th stream | **REUSE + ACTIVATE** |
| Classification rules | `config.py:275` `^15-UNIVERSAL-SCIENCE-INTELLIGENCE/ → USIS/USIS/VOL-024`; `:635` CHAINS; `:671` PROGRAM_ROOTS; `:714` CROSS_PROGRAM | new Wave-3 sub-homes classify automatically — **no config edit needed** for any `15-…/**` path | **REUSE — 0 config.py changes required** |
| USIS Universe Registry | USIS-002 (the catalog *is* the registry) | member rows | **REUSE (append rows in the successor catalog surface / USIS-021)** |
| USIS Science Registry | USIS-003 (the catalog *is* the registry) | member rows | **REUSE** |
| 12 program registries | to live under `15-…/04-REGISTRIES/` | Universe · Science · Domain · Capability · Algorithm · Model · Pattern · Insight · Reasoning-Trace · Dataset · Learned-Change · Self-Evolution | **NEW HOME, REUSED MECHANISM** (Gap G-01/G-03) |

**Critical assimilation result.** Because `config.py` already classifies the entire `15-…/` subtree, every Wave-3 sub-home (`06-UNIVERSES/SCI/`, `07-SCIENCES/MATH/`, `08-DOMAINS/HUMAN/`, …) registers automatically with **zero governed source edits**. This is the constructive proof of obligation 20 (Infinite Extensibility) for Wave-3.

## PART G — Existing reusable **runtime**

| Runtime asset | Location | Wave-3 use | Decision |
|---------------|----------|-----------|----------|
| Platform runtime | `platform/runtime_platform`, `platform/runtime_operations` | hosting surface for tier-15 bindings | **reference (frozen)** |
| Engine runtime | `engine/runtime` (37 py) | execution primitives | **reference (frozen, EC-1)** |
| RIE execution frontier | `intelligence/UCOS-RIE-EXECUTION-FRONTIER.json` | CIOA RUNNABLE frontier for Stage 1 selection | **REUSE** |
| Governance telemetry | `00-BOOK/tools/governance_telemetry.py`, `.runtime/governance/` | enforcement + certification audit trails (runs #467/#468) | **REUSE** |
| Execution stream model | FREEZE C4 — 7 streams incl. "Universal Science & Intelligence" (`science-intelligence-eligible`) | Wave-3 members are the first objects of the 7th stream | **REUSE + POPULATE** |
| Determinism harness | `engine/determinism`, `determinism-evidence/` | byte-stable regeneration proof | **REUSE** |

## PART H — Existing reusable **evidence**

| Evidence asset | Location | Wave-3 use | Decision |
|----------------|----------|-----------|----------|
| Certification evidence | `00-BOOK/DATA/certification.json` (10/10 domains, 1164-artifact scope) | per-mission whole-corpus certification record | **REUSE** |
| Certification audit trail | `.runtime/governance/certification-audit.json` | append-only certification history | **REUSE** |
| Enforcement audit | `.runtime/governance/` (audit runs #467/#468) | registration/classification enforcement history | **REUSE** |
| Change ledger | `00-BOOK/DATA/change-ledger.json` (1272 change events) | change intelligence per member | **REUSE** |
| Signal ledger | `00-BOOK/DATA/signals.json` (15 signals) | connector-derived evidence | **REUSE** |
| Per-capability evidence store | `data/_evidence/<CAP-ID>/`, `service/_evidence/` | UCIC Output-5 bundles | **REUSE** |
| Coverage evidence | `coverage.xml`, `.coverage` (97% TOTAL) | tier-19 implementation coverage proof | **REUSE** |
| Mission evidence pattern | `UCOS-USIS-WAVE1/MISSION-001-USIS-001/evidence/00…10` (enforce-pre, register, trace, ukb-validate, ukb-enforce, ukbx-validate, ukbx-twin, ukbx-certify, determinism, register-run2, guard logs) | the exact per-mission evidence log set Wave-3 missions must produce | **REUSE (template)** |

## PART I — Existing reusable **validation**

| Validator | Surface asserted | Decision |
|-----------|------------------|----------|
| `ukb validate` | append-only ledger, no duplicate IDs/pages, referential integrity, execution-lifecycle forward-only | **REUSE** |
| `ukb enforce --pre` / `enforce` | eligibility → validity → classification → registration parity | **REUSE** |
| `ukbx validate` | signal append-only, subject resolution, provenance, secret-free | **REUSE** |
| `ukbx twin --check` | UKB-014 hard checks C-04/05/07/08/09/10/11 (+ advisory C-02/03/06) | **REUSE** |
| `engine/validation` (EPIC-007) | Software-stream validation | **reference (frozen)** |
| `platform/universal_validation`, `platform/validation`, `platform/validation_intelligence` (EC2-EPIC-010) | Software-stream validation | **reference (frozen)** |
| `verify.sh` stages | lint/format, tests, coverage ≥ 90, governance pre-gate | **REUSE** |
| UCIC-001 Stages 5–9 | per-capability static/dynamic/test/coverage/evidence | **REUSE** |
| USIS-014 Part G validator binding table | maps each obligation to the validator that discharges it | **REUSE — Wave-3 binds `validator_ref`, writes no validator** |

## PART J — Existing reusable **certification**

| Certifier | Scope | Decision |
|-----------|-------|----------|
| `ukbx certify` (UMB-IMP-006) | 10 integrity domains over real repository state + evidence + append-only audit + report | **REUSE — sole certifier** |
| `ukbx twin --check` (UKB-014) | 7 hard digital-twin checks | **REUSE** |
| CCE (`UCOS-COMP-000001`) | 10 fail-closed certification gates + SoD | **REUSE** |
| `engine/certification`, `engine/universal_certification`, `platform/certification` | Software-stream certification | **reference (frozen)** |
| USIS-015 architecture | certification node/lifecycle/authority/coverage contracts | **REUSE — Wave-3 produces records** |
| Whole-corpus certification pattern | `EVO-USIS-01[456]/08-WHOLE-CORPUS-CERTIFICATION-REPORT.md` | per-mission regression-free proof | **REUSE (template)** |

## PART K — Consolidated reuse decision matrix

| Wave-3 need | Canonical existing asset | Decision | Justification |
|-------------|--------------------------|:--------:|---------------|
| Identity allocation | `ukb.py` + `id-ledger.json` | **REUSE** | LAW USIS-02 — never a second allocator (USIS-002 Part D) |
| Registration | `register.sh` (10-phase atomic) | **REUSE** | REG-AUTO-001 §7 |
| Classification of new sub-homes | `config.py:275` path rule + per-artifact front-matter | **REUSE, 0 edits** | obligation 20 constructive proof |
| Graph / traceability | `relationships.json` via `ukb build` | **REUSE** | GOV-002 |
| Ontology core | U24 Knowledge / MIP Part 19, specialized by USIS-005 O-3 | **REUSE** | forking = LAW USIS-02 violation |
| Taxonomy core | USIS-002/003 classification roots via USIS-005 X-1 | **REUSE** | same |
| Capability model | USIS-004 24 tiers + USIS-006 | **REUSE** | LAW USIS-08 |
| Lifecycle / methodology | UCIC-001 (FROZEN v1.0) | **REUSE** | no capability may bypass |
| Member selection | CIOA frontier + RIE `EXECUTION-FRONTIER.json` | **REUSE** | UCIC Stage 1 gate forbids manual sequencing |
| Validation | `ukb`/`ukbx` + engine/platform validators + UCIC 5–9 | **REUSE** | USIS-014 Part R |
| Certification | `ukbx certify` + CCE + SoD | **REUSE** | USIS-015 Part S |
| Evidence | UCIC Output-5 + TRACK-001 + `data/_evidence/` + audits | **REUSE** | USIS-016 |
| Runtime hosting | platform runtime / `08-RUNTIME` / RIE | **REUSE (reference)** | USIS-013 Part P |
| Service machinery | SERVICE program + `service/` | **REUSE (reference), EXTEND additively** | USIS-012 Part P |
| API/SDK transport | SERVICE/PLATFORM machinery | **REUSE (reference)** | USIS-017 |
| Data concerns | `10-DATA` program + U07 | **REUSE (reference)** | USIS-002 Part D |
| Security concerns | `14-SECURITY` | **REUSE (reference)** | `…/06` §1 |
| Simulation | U26 / MIP Part 25 | **REUSE (reference)** | USIS-002 Part D |
| Freeze / stream model | FREEZE C4 + `freeze_c4_engine.py` | **REUSE (regenerate)** | never edit C2/C3 |
| Blueprint schema | 14-section schema (`WAVE2/00` §3) | **REUSE** | Knowledge Once |
| Authorization pattern | `WAVE2-AUTH/01–05` + 5 entry preconditions | **REUSE** | Knowledge Once |
| Mission report set | `EVO-USIS-01[456]/01–09` | **REUSE (template)** | Knowledge Once |
| Areas `02`/`03`/`04`/`19` | — nothing exists | **NEW HOME (mandated by structure spec §2)** | not new knowledge: the areas are already specified and referenced by 12/7 artifacts |
| USIS-018/019/020/021 | — nothing exists | **NEW ARTIFACT (mandated by structure spec §3)** | already named in the authoritative structure instrument; authoring them is completion, not invention |
| Per-member tier instances | — nothing exists | **NEW CONTENT (the substance of Wave-3)** | explicitly deferred by 15 corpus artifacts |

## PART L — Assimilation determination

| Assimilation dimension | Result |
|------------------------|--------|
| Reusable knowledge identified | 19 corpus artifacts + 12 operational-memory instrument classes |
| Reusable engines identified | 8 governance/tooling engines + 2 frozen code streams + RIE |
| Reusable governance identified | 16 instruments |
| Reusable registries identified | 12 surfaces (+ automatic classification) |
| Reusable services / runtime identified | 8 streams (4,425 files); 6 runtime assets |
| Reusable evidence identified | 8 evidence surfaces |
| Reusable validation identified | 9 validators |
| Reusable certification identified | 6 certifiers |
| **New mechanisms required** | **0** |
| **New engines required** | **0** |
| **New registries (mechanism) required** | **0** |
| **New governed source edits (`config.py`) required** | **0** |
| New *homes* required | 4 canonical areas + per-member sub-homes |
| New *artifacts* required | USIS-018/019/020/021 + per-member tier instances + Wave-3 programme records |

**CONTEXT ASSIMILATION GATE: DISCHARGED.** Wave-3 is a **reuse-first, registration-only** wave: it consumes every existing engine, registry, governance instrument, validator, certifier, and evidence surface unchanged, and adds only (a) the four already-specified area homes, (b) the four already-named governance instruments, and (c) per-member instance content that no existing artifact owns.

*END — 03 Context Assimilation Report · EVO-USIS-W3-FOUNDATION-001 · READ-ONLY · AUTHORITY = NONE (DERIVED).*
