# CANONICAL AUTHORITY DETERMINATION

| Field | Value |
|---|---|
| **ARTIFACT** | `CANONICAL-AUTHORITY-DETERMINATION.md` |
| **PHASE** | Phase 2 — Canonical Authority Determination |
| **AUTHORITY** | **NONE — DERIVED TRUTH.** Determines *what the repository already declares* about ownership. Creates no owner, moves no owner, renames nothing, introduces no term. |
| **CLASSIFICATION** | `EVIDENCE` |
| **BOUNDARY** | `ASSESSMENT-BOUNDARY-DETERMINATION.md` §2–§5 |
| **SNAPSHOT** | `1f869865` + 113 uncommitted entries |
| **RESERVED** | Every ownership conflict in §5 is recorded, not resolved. Resolution is reserved to the human authority. |

---

## 1. Canonical authority is tripartite, not singular

The repository has **no single canonical-authority artifact**. Authority is partitioned across three planes, each of which explicitly disclaims the others. This is a measured structural fact, not a defect judgement.

| Plane | Owning artifact | Self-declared authority | Machine-readable? |
|---|---|---|---|
| **Ownership declaration** | `02-CANONICAL-OWNERSHIP-MATRIX.md` | *"Repository Truth is ABSOLUTE. Single Canonical Ownership — each concept has exactly one owner"* | **NO** — §5 (Ω-A02 addendum) states every ownership row "was authored by a human and is unreadable by machine" |
| **Concept truth** | `00-MASTER/UAKOS-CLOSURE-002/closure.json` + ~68 projections | `AUTHORITY = NONE (DERIVED TRUTH)` | YES |
| **Identity + artifact registration** | `00-BOOK/DATA/{id-ledger,artifacts,generated-artifact-registry,exclusion-register,mutation-governance-boundary}.json` | `AUTHORED REPOSITORY TRUTH … upstream of every engine it describes` | YES |
| **Constitutional recognition** | `00-CMG/CMG-REGISTRY.json` | CMG-L-01: an artifact exercises constitutional force *only while recognized here* | YES |

**Determination D-2.1:** the Canonical Ownership Principle is *declared* in one place and *enforced* in another, and the two do not share a key. This is the root of every conflict in §5.

---

## 2. Canonical artifact inventory

Artifacts that own a concept, are registered, and are bound by a check that executes.

### 2.1 Constitutional canon — 44 recognized artifacts

Owner: `00-CMG/CMG-REGISTRY.json`. Enforced by `00-CMG/tools/cmg_validate.py` (CMG-INV-01..12), `verify.sh` Stage 6. **Measured this session: PASS, 0 findings, 86 articles present, 80 mandated sections, 61 concerns allocated (50 delegated / 11 retained).**

| Group | Members | State |
|---|---|---|
| Meta | `00-CMG/CMG-000001` v1.2 (T1M) | DECLARED |
| Constitutional Engineering Programme | `00-CEP/CEP-000…CEP-010` (11) | T2 PROVISIONAL |
| Closure constitutions | `00-MASTER/UAKOS-CLOSURE-006/CONST-01…CONST-11` (11) | **FROZEN** |
| Band constitutions | `08-RUNTIME/RUNTIME-001`, `09-PLATFORM/PLATFORM-001`, `10-DATA/DATA-001`, `11-SERVICE/SERVICE-001`, `12-APPLICATION/APPLICATION-001`, `13-INFRASTRUCTURE/INFRASTRUCTURE-001`, `14-SECURITY/SECURITY-001`, `02-MASTER/UCOS-Ω∞-TECHNOLOGY-CONSTITUTION.md` (8) | PROVISIONAL |
| Control-tower standards | `AUTH-INF-001`, `STATUS-001`, `REG-AUTO-001`, `UCI-001`, `GOV-INT-001` (5) | PROVISIONAL |
| Code constitution | `engine/uckp/law.py` (`UCKP-LAW-0001`, kind CMG-K-14) | the only executable constitution |
| Others | `CAT-000`, `REF-000`, `UCOS-AB-001/07`, `UCOS-EG-001/01`, `UCOS-UMA-001/01`, `UCOS-NUCLEUS-001/02`, `CMG-000002…14` | PROVISIONAL |

States: **32 PROVISIONAL · 11 FROZEN · 1 DECLARED.** Declared ceiling: `READY-PROVISIONAL` (CMG-OQ-01, CMG-OQ-02 open; `VAC-01` unclosed per CMG-000001 LXXX.4).

### 2.2 Registration canon — `00-BOOK/DATA`

| Artifact | Population (measured) | Bound by | Verdict this session |
|---|---|---|---|
| `artifacts.json` | **1233** artifacts (ACTIVE 1132 · COMPLETE 43 · FROZEN 27 · UNDER_REVIEW 15 · FINAL 9 · CERTIFIED 7); **0 `.py`** | `ukb.py validate` | **PASS** |
| `id-ledger.json` | 1264 `by_path` · 4603 `by_object` · 1264 `history` · 7 `by_observation`; scheme `UCOS-<CATEGORY>-<NNNNNN>`, 117 categories | `uga_engine.py` CAA-INV-04 (`EXACTLY_ONE_IDENTITY_AUTHORITY`, measured 5874) | **PASS** |
| `generated-artifact-registry.json` | **344** entries · 18 fields · 9 input classifications · 30 producer homes · 10 generated inputs · **`bootstrap_gaps: []`** · 13 invariants | `uga_engine.py` UGA-INV-04/05/06/08 | **PASS** |
| `exclusion-register.json` | 7 classes · 32 entries · 4 invariants (`ignored_unclassified = 0`) | RIB GATE-12 | GATE-12 **FAIL** (see §5.3) |
| `mutation-governance-boundary.json` | determination `OPTION B` · 7 authorities · 5 mutation classes · 5 invariants | declarative boundary | consistent |
| `observation-universe.json` | 5 observation kinds (4 `FORBIDDEN`, 1 `COMMITTED_CONTENT` permitted) · 5 sources · 8 producer declarations · 9 invariants | OBS-INV-01..08 | **PASS** (8/8) |
| `evidence-universe.json` | 5 classes · 10 surfaces · 7 invariants · **2 classes declared empty** | UGA-INV-07 (measured 11) | **PASS** with declared void |
| `certification.json` | **1** record: `UMB-017`, CERTIFIED 10/10, 25/25 checks, scope 1233 artifacts / **0 executions** | `ukbx.py certify` | see §5.5 |
| `constitutional-authority-alignment.json` | 3 projections incl. `dependency_evidence_index` | CAA-INV-05 | **PASS** |

### 2.3 Model / authority canon — code owners

| Concept | Canonical owner (code) | Protecting invariant | Verdict |
|---|---|---|---|
| Relationship / dependency graph model | `engine/uckp/graph.py` + population `00-MASTER/UCOS-UGA-001/04-RELATIONSHIP-GRAPH.json` | `CAA-INV-05 EXACTLY_ONE_RELATIONSHIP_GRAPH_MODEL_OWNER` (measured 6) | **PASS** |
| Object model | (single) | `CAA-INV-07 NO_INSTRUMENT_DECLARES_A_RIVAL_OBJECT_MODEL` (measured 16) | **PASS** |
| Universal identity | `00-MASTER/UCOS-UGA-001/uga_engine.py` | `CAA-INV-04` (measured 5874) | **PASS** |
| Lifecycle vocabulary | `engine/knowledge/model.py::Lifecycle` (10 stages, enforced transitions) | `require_transition` | present, **unused** (§5.4) |
| Constitutional law | `engine/uckp/law.py` (`UCKP-LAW-0001`) | CMG-K-14 recognition | **PASS** |
| Execution authority realization | `engine/runtime/execution/authorization.py::require_authorization` | `UCAF-RB-01`, vested by `00-CEP/CEP-003` | **the only** constitution→code binding (`realizations: 1/1`) |
| Freeze eligibility | `00-MASTER/UCOS-UFEP-001/ufep_engine.py` | CEP-007 Art. V (`UFEP-PRE-01…05`) | **gate CLOSED** (§5.6) |
| Ratification | `00-MASTER/UCOS-URAT-001/urat_engine.py` | CEP-006 | gate **OPEN**, 5/5 records |
| Traceability closure | `00-MASTER/UCOS-UTCE-001/utce_engine.py` | CEP-001 | gate **OPEN** (1233 artifacts, 12 899 edges, 0 dangling/unrooted/orphans) |
| Authority model | `00-MASTER/UCOS-UCAF-001/ucaf_engine.py` | CEP-000/002/006/008 + CMG-000001 | gate **OPEN**, `reconciliation-required=3`, 1 vacant tier |

---

## 3. Derived artifact inventory

Self-stamped `AUTHORITY = NONE (DERIVED TRUTH)`. Admissible at Priority 6 only, and only with the producer named.

| Derived set | Producer | Regenerated this session? | Population |
|---|---|---|---|
| `00-MASTER/UAKOS-CLOSURE-002/` projections (~68 `.md` + 3 `.json`) | `closure_engine.py`, `phase2_engine.py`, `phase3_engine.py` | **YES** (Stage 1b steps 5–7, plus session-start hook) | 549 concepts |
| `20-CANONICAL-CONCEPT-REGISTER.md`, `22-CANONICAL-HOME-REGISTER.md`, `31-CONCEPT-OWNERSHIP-REGISTER.md` | `phase2_engine.py` | YES | 549 homed / 549 |
| `knowledge/handbooks/*` (10) + `canonical-knowledge.json` + `decisions.json` | `engine.knowledge.cli init/capabilities/docs` | **YES** (steps 1–3) | 121 CKOs |
| `intelligence/UCOS-RIE-*.json` (catalog, health, model, snapshot) | `intelligence/rie/engine.py` | NO — mtime 22:06:58, pre-session | 122 capabilities |
| `intelligence/UCOS-URI-001/`, `UCOS-UPI-001/` | `intelligence.research build`, `intelligence.publication build` | YES (steps 8–9) | — |
| `realization/` (9 `.py`, `DO NOT EDIT`, `knowledge_seal`, 125 `source_ckos`) | `intelligence.realization realize` | YES (step 11) | — |
| `determinism-evidence/` | `engine.determinism.reproduce` | YES (step 4) | — |
| `00-MASTER/UAKOS-PHASE-001B/provenance.json` | `provenance_engine.py` | YES (step 10) | — |
| `00-MASTER/UCCEP-000005…8` report sets (~40 `.md`) | `derive.py`, `emit_views.py` | NO | markdown-only |
| `00-BOOK/REGISTRIES/*` (6, incl. 1.4 MB knowledge graph) | `ukb.py` / `register.sh` | NO — mtime 2026-08-10 | 1233 artifacts / 12 899 edges |
| `.runtime/repository-intelligence/UCOS-RPI-DEPENDENCY-GRAPH.*` | `platform.repository_intelligence.cli emit` | NO — **no bootstrap stage exists** | — |

**Determination D-3.1 (staleness).** `generated-artifact-registry.json` declares **344** artifacts across **30** producer homes. `verify.sh` Stage 1b re-runs **11** producers. The outputs of the remaining ~19 are **stale observations**, admissible only as such. Concretely: `00-BOOK/REGISTRIES/*` and `00-BOOK/DATA/{artifacts,relationships,change-ledger,volumes,control-tower}.json` all carry mtime 2026-08-10, five days before this snapshot, and the digital-twin certification rests on exactly those bytes.

**Determination D-3.2 (headline scope correction).** The session-start line `UAKOS-CLOSURE-002: CLOSED | concepts=549 | gaps=0` is produced by `.kiro/hooks/uakos-closure-002.json`, which invokes the engine with `CLOSURE_SKIP_CORPUS=1`. `closure_engine.py:177,214` then records `scan_mode: "repo-only (declared)"` and `population_complete: true` — complete *within a declared narrowing*, because the external corpus `/Users/bipin/Desktop/UCOS` **does not exist on this machine** (verified: `ls` → No such file or directory). The `conversation_only` gap class is therefore **out of scope by declaration**, not measured to zero. The engine is explicit and honest about this; the headline number is not, and must not be read as an unqualified closure.

---

## 4. Generated and non-authoritative inventories

### 4.1 Generated artifact inventory

Owner: `00-BOOK/DATA/generated-artifact-registry.json` (`UCOS-GENERATED-ARTIFACT-REGISTRY-001` v2.0.0). **This assessment creates no parallel registry.** Measured: 344 entries, 30 producer homes, 31 distinct producers, 10 declared generated inputs each with a `bootstrap_command` and `bootstrap_stage`, 2 environmental artifacts, `bootstrap_gaps: []`, 13 invariants.

Input classification vocabulary (9, `UNKNOWN` fails closed): `TRACKED_DETERMINISTIC`, `GENERATED_DETERMINISTIC`, `ENVIRONMENTAL`, `OPERATIONAL`, `EXTERNAL`, `UNKNOWN`, `EXECUTION_TRANSCRIPT`, `LOCAL_RUNTIME`, `ENVIRONMENTAL_OBSERVATION`.

Verified by `uga_engine.py gate` this session: UGA-INV-04 (input closure, 344) **PASS** · UGA-INV-05 (producer, 10) **PASS** · UGA-INV-06 (bootstrap path, 10) **PASS** · UGA-INV-08 (no unclassified observation, 344) **PASS**.

### 4.2 Non-authoritative artifact inventory

| Set | Count | Basis for non-authority |
|---|---|---|
| Root `01-`…`11-` numbered series | ~55 | pinned to superseded baseline `ab78f35`; current is `1f869865` |
| `03-DEPENDENCY-GRAPH.md`, `03-IMPLEMENTATION-DEPENDENCY-GRAPH.md` + ~18 siblings | ~20 | formally classified EVIDENCE by `constitutional-authority-alignment.json` → `dependency_evidence_index`: *"No historical snapshot listed here may serve as a dependency authority."* |
| `38-DEPENDENCY-REGISTER.md`, `40-EXECUTION-WAVE-REGISTER.md` | 2 | generated at baseline `b67a720`, `AUTHORITY=NONE`, `.gitignore`d, absent from a clean checkout — yet cited as the sole evidence of `05-DEPENDENCY-CLOSURE.md` |
| `00-MASTER/UCCEP-000007/05-CAPABILITY-INVENTORY.md` | 1 | 42 capabilities at HEAD `9de85ad`; current catalog declares 122 |
| Both `PHASE-0.7-DEPENDENCY-GRAPH-*` | 2 | pinned to `ed74d2d9` |
| `MCP-001-MASTER-CONTEXT-AND-EXECUTION-SYSTEM.md` | 1 | `STATUS: REDIRECT POINTER`, `SUPERSEDED BY: 00-MASTER/` — the only true supersession record |
| `CERTIFICATION-ARCHITECTURE-DETERMINATION-DRAFT.md` | 1 | DRAFT in title/filename; contradicted by its use as a completed precondition |
| 49 root `*.md` with no status marker | 49 | no `Authority`/`Status`/`Determination`/`Verdict` line in header |
| 18 root determinations awaiting VCS binding | 18 | `ukb.py enforce --pre` this session |
| `00-MASTER/**/evidence/` (213 files, 20 dirs) | 213 | `may_affect_certification: false`; gitignored |
| `intelligence/die/` | — | no `__init__.py`, no importers, excluded from RC-1 baseline |

### 4.3 Obsolete artifact inventory

**Measured population: 1.**

Only `MCP-001-MASTER-CONTEXT-AND-EXECUTION-SYSTEM.md` carries a self-applied supersession header. Corroborating measurements:
- `artifacts.json`: **zero** `SUPERSEDED` and **zero** `DEPRECATED` status values across 1233 artifacts.
- Grep for a document-scoped `| STATUS | SUPERSEDED |`-style header across `00-MASTER/**/*.md`: **zero** hits.
- `engine/knowledge/model.py::Lifecycle` implements and enforces the full 10-stage vocabulary — it is simply never applied to corpus artifacts.

Section-scoped and item-scoped supersessions do exist and are correctly recorded (`W3-4c-…EVIDENCE.md` §6 "SUPERSEDED BY EVENTS, recorded in full"; `RTBD-001` F-1/F-3 verdicts; `UCOS-UIP-001 → UCOS-USIS-001`; `P0-ASSIMILATION-001` P-26…P-31). These supersede *findings and concepts*, never documents.

---

## 5. Ownership conflicts

Recorded with evidence. **Not resolved** — resolution is reserved to the human authority.

### CONFLICT-01 — Ownership is declared where it cannot be checked

| | |
|---|---|
| Artifacts | `02-CANONICAL-OWNERSHIP-MATRIX.md` (53 concept-domain rows, 7 addenda) vs `knowledge/canonical-knowledge.json` |
| Evidence | Matrix §5 (Ω-A02, 2026-08-05) records that `engine/knowledge/integration/reuse.py::ReuseEngine` read a store holding only **11 founding seed objects** and therefore returned `CREATE` for **12 of 12** capabilities that already existed |
| Current state | Stage 1b now runs `init → capabilities --write → docs`, taking the store to **121 CKOs** (verified byte-identically). The 12-of-12 failure mode is closed for the *store*; the **matrix rows remain machine-unreadable** |
| Type | Declared-but-unenforceable ownership |
| Resolution required | Decide whether the 53 matrix rows become machine-readable data (and if so, under which existing owner) or are formally demoted to EVIDENCE |

### CONFLICT-02 — Two ownership populations, five reported concept counts

| | |
|---|---|
| Artifacts | `02-CANONICAL-OWNERSHIP-MATRIX.md` §3 ("all **431** concepts") vs `closure.json` (**549**) |
| Evidence | The hook line is quoted across the repository with **five** values: 431 (`RA-003/03`, `RA-002/01`, `RTR-001/01`), 434 (`IAC-001A/04`, `UCCEP-000008/02`, `.runtime/…UCIO-000001-integration-report.json`), 437 (`MIP-W1-P001/04`), 440 (`CAEM-001/04`), 549 (`UCOS-ACC-001`). Only 549 matches the current engine output |
| Type | Stale derived value copied into authored documents |
| Resolution required | Accept that any authored document quoting a derived count is stale-by-construction, or bind such counts to a single rendered projection |

### CONFLICT-03 — `duplicate_canonical_homes = 0` is a weak guarantee doing strong work

| | |
|---|---|
| Measurement | `closure_engine.py:427-429`: `dup_home = [r for r in recs if len(r["exact_homes"]) > 1]` — an **exact-basename collision test** |
| Weakness | `22-CANONICAL-HOME-REGISTER.md` rows overwhelmingly read `#Homes = 0` / `(non-filename home)`. For a concept with no filename home, `len(exact_homes) > 1` is **vacuously false** |
| Load-bearing use | It is the sole evidence for "Single canonical ownership (no dual owners) = PASS" in `02-CANONICAL-OWNERSHIP-MATRIX.md:92`, and is cited as authority by at least 12 further artifacts (`03-ARCHITECTURAL-COMPLETENESS.md:20`, `05-CONSTITUTIONAL-CLOSURE-CERTIFICATION.md:54`, `08-QUALITY-GATES.md:25,69`, `UNAF-001:322`, `UCOS-NUCLEUS-001/02:94`, `RA-003/03:64`, `UAKOS-CLOSURE-003/{04,05}`, `IMPLEMENT-001E/{00,01}`, `UCOS-UMA-001/08:76`, `MIP-W1-P001/wave1-baseline.json:622`) |
| Type | Metric-strength / claim-strength mismatch |
| Resolution required | Decide whether semantic duplicate-owner detection is required, or whether the filename test is accepted as the definition |

### CONFLICT-04 — The certified corpus structurally excludes all implementation

| | |
|---|---|
| Evidence | `artifacts.json`: 1233 artifacts, **0 `.py`**. `certification.json`: CERTIFIED 10/10, scope 1233 artifacts, `executions: 0`. `UCOS-RIE-HEALTH.json`: 328 628 LOC across 1795 source files, 13 542 test functions |
| Consequence | The only certification authority that returns CERTIFIED certifies a population containing **none** of the code. The only artifact that sees the code (`UCOS-RIE-CAPABILITY-CATALOG.json`, 122 capabilities) declares `AUTHORITY = NONE` and is certified by nothing |
| Type | Certification-scope gap |
| Resolution required | Decide whether code enters the registered corpus, or whether a second certification authority for code is vested |

### CONFLICT-05 — Aggregate certifier disagrees with its own committed record

| | |
|---|---|
| Committed | `00-MASTER/UCCEP-000000/uccep.json`: `blocking_failures: ["CK-ACEE"]`, tier `full`, 15 PASS / 4 PASS-WITH-ADVISORY / 1 FAIL |
| Measured this session | `uccep_engine.py --gate` → exit 1, `blocking = CK-BASELINE, CK-UCL, CK-UIS`, gates 17/26, programmes 13/21, tier `standard`, seal `8d9038f8f65bc4da`, and *"emission withheld: tier standard is narrower than the recorded tier full"* |
| Type | Committed determination vs current measurement (Priority 1 governs) |
| Resolution required | Re-run at tier `full` and accept the wider determination, or record the three new blockers as current truth |

### CONFLICT-06 — Ten validation authorities, no reconciling verdict

| | |
|---|---|
| Evidence | `verify.sh` aggregates 7 authorities. `UCOS-RIB-001`, `UCCEP-000000` and the import-acyclicity checker are outside it. Measured this session: `verify.sh` stages 1/1b/4/5/6/6c/6d **PASS**, stage 6b **FAIL**; `rib --gate` **FAIL**; `uccep --gate` **FAIL**; `ufep --gate` **FAIL**; `urat/utce/ucaf --gate` **PASS** |
| Type | Distributed validation authority with no single verdict owner |
| Resolution required | Vest one authority to aggregate, or accept that "verify.sh passes" is a partial statement |

### CONFLICT-07 — Aggregate gates mutate the homes they judge

| | |
|---|---|
| Evidence (measured) | `uccep_engine.py --gate` cascaded writes into **4 program homes / 47 tracked files** (`ACEE-000001` 17, `BASELINE-001` 5, `UCL-000001` 15, `UIS-001` 10). `ufep/urat/utce --gate` each wrote 5 artifacts; `ucaf --gate` wrote 10. Working-tree porcelain rose 113 → 186 and was restored to 114 by `git checkout --` |
| Contrast | `uga_engine.py gate`, `cmg-gate.sh`, `ukb.py enforce/validate` and `engine.uaue.gate` wrote nothing, as documented |
| Type | Read-only contract violation in the observation plane |
| Resolution required | Decide whether `--gate` must be write-free for these engines (consistent with `mutation-governance-boundary.json`, which names them as gates rather than producers) |

### CONFLICT-08 — Freeze authority blocked by the certifier, which disagrees with itself

| | |
|---|---|
| Evidence | `ufep_engine.py --gate` → exit 1: `FREEZE-ELIGIBILITY=TRUE CONSTITUTIONAL-COMPLETION=FALSE`, subjects **5/5 eligible**, completion **9/11**, frozen-baseline 13/13 verified, drifted 0, freeze-performed **NO**, gate **CLOSED**. Blocking `UFEP-VAL-14` with `UFEP-CC-01` and `UFEP-CC-02` **unsatisfied**, both sourced from `00-MASTER/UCCEP-000000/uccep.json` (`03-CONSTITUTIONAL-COMPLETION-DETERMINATION.md:29-30`) |
| Chain | freeze blocked ← UFEP-CC-01/02 unsatisfied ← UCCEP reports a failing gate ← CK-BASELINE / CK-UCL / CK-UIS (measured) or CK-ACEE (committed) |
| Type | Transitive freeze blocker with an unstable upstream |
| Resolution required | This is the single decisive freeze blocker. See `FINAL-FREEZE-READINESS-DETERMINATION.md` |

### CONFLICT-09 — 8 tracked executable objects are anonymous

| | |
|---|---|
| Evidence | `uga_engine.py gate`: UGA-INV-01 `EVERY_OBJECT_HAS_UNIVERSAL_ID` **FAIL** (8 violations / 5844 measured); UGA-INV-10 `EVERY_MUTATION_HAS_AUDIT_EVENT` **FAIL** (8 / 4611). Objects: `engine/uckp/resolution.py`, `engine/uckp/uga_projection.py`, `engine/tests/uckp/test_category_integrity.py`, `test_category_ownership_resolution.py`, `test_uga_projection.py`, `platform/tests/test_commercial_cli.py`, `test_repository_intelligence_cli.py`, `test_universal_provider_cli.py` |
| Governing text | `uga_engine.py:210-215` — exclusion from corpus registration "is a statement about which register lists them — never a licence to exist anonymously" |
| Remedy named by the engine | `uga_engine.py run` |
| Type | Identity gap in the version-controlled boundary |
| Resolution required | Mechanical: run the minting producer. No decision needed beyond authorising the write |

### CONFLICT-10 — Supersession is legislated in code and unused in the corpus

| | |
|---|---|
| Evidence | `engine/knowledge/model.py::Lifecycle` enforces `DRAFT → … → SUPERSEDED → ARCHIVED → HISTORICAL`; `artifacts.json` uses none of the terminal states; 1 supersession header repository-wide; 49 root documents carry no status marker; house convention (`POST-STABILIZATION-DETERMINATION-LIFECYCLE-DECISION.md` §3) is explicit retention with **no supersession label** |
| Consequence | Staleness is only derivable from baseline pins, not declared. A reader cannot distinguish current from historical determination without comparing commit hashes |
| Type | Unapplied lifecycle vocabulary |
| Resolution required | Apply `Lifecycle` to corpus artifacts, or formally accept baseline-pin-derived staleness as the mechanism |

---

## 6. Resolution decisions

Decisions the assessment **is** authorised to make (classification and precedence, per boundary §2/§3), separated from those it is not.

### 6.1 Decisions taken

| # | Decision | Basis |
|---|---|---|
| R-01 | Where a committed determination and a current gate measurement disagree, **the measurement governs** and the determination is reclassified HISTORICAL for that claim | Boundary §2 Rule P1. Applied to CONFLICT-05, CONFLICT-06 |
| R-02 | `02-CANONICAL-OWNERSHIP-MATRIX.md` is admitted at **Priority 5** (documentation), not Priority 3, because no executing check binds its rows | Boundary §2 Rule P3 + matrix §5 self-admission |
| R-03 | The root `01-`…`11-` series and ~20 dependency snapshots are classified **HISTORICAL** | baseline pins `ab78f35`/`b67a720`; `dependency_evidence_index` |
| R-04 | `closure.json` 549/0-gaps is admitted **only** with its declared narrowing stated (`CLOSURE_SKIP_CORPUS=1`, corpus absent) | `closure_engine.py:177,214`; `ls /Users/bipin/Desktop/UCOS` fails |
| R-05 | Derived artifacts not regenerated this session (~19 producer homes incl. all of `00-BOOK/REGISTRIES/*`) are **stale observations**, not current evidence | Boundary §5.1(2) |
| R-06 | No new registry, matrix, or ownership artifact is created by this phase; `UCOS-UFEP-001` is reused as the freeze-eligibility owner and `generated-artifact-registry.json` as the generated-artifact owner | Knowledge Once Principle; existing-artifact-reuse-before-creation |
| R-07 | The obsolete population is **1**, not "unknown" — measured, not assumed | marker grep + status census |

### 6.2 Decisions reserved to the human authority

| # | Reserved decision | Conflict |
|---|---|---|
| H-01 | Make matrix ownership machine-readable, or demote it to EVIDENCE | CONFLICT-01 |
| H-02 | Accept or strengthen the basename-collision definition of duplicate ownership | CONFLICT-03 |
| H-03 | Admit code into the registered corpus, or vest a second certification authority for code | CONFLICT-04 |
| H-04 | Re-run UCCEP at tier `full`, or accept the three newly measured blockers | CONFLICT-05 |
| H-05 | Vest a single aggregating validation authority, or accept partial `verify.sh` semantics | CONFLICT-06 |
| H-06 | Require `--gate` to be write-free for the five mutating engines | CONFLICT-07 |
| H-07 | Authorise `uga_engine.py run` to mint the 8 anonymous objects | CONFLICT-09 |
| H-08 | Apply `Lifecycle` to corpus artifacts, or ratify baseline-pin staleness | CONFLICT-10 |

---

## 7. Determination

| Question | Answer | Evidence |
|---|---|---|
| Is canonical ownership declared? | **YES** | `02-CANONICAL-OWNERSHIP-MATRIX.md` (53 domains, 47 OWNED), `CMG-REGISTRY.json` (61 concerns, 50 delegated) |
| Is canonical ownership enforced? | **PARTIAL** | 4 identity/model invariants PASS (CAA-INV-04/05/07, UGA-INV-02/03); ownership *rows* unenforceable; 5 of 61 CMG concerns have `owner: null` (`CMG-DLG-36…40`) |
| Are there duplicate canonical homes? | **0 measured**, weak test | `closure_engine.py:427-429` |
| Are there orphan artifacts? | **0 concepts orphaned**; **26 artifacts unregistered**; **8 objects anonymous**; **21 untracked entries** | `closure.json`, `ukb.py enforce --pre`, `uga gate`, `git status` |
| Are derived artifacts distinguishable from canonical? | **YES** | 344-entry registry, 9 input classifications, 30 producer homes, `bootstrap_gaps: []` |
| Are obsolete artifacts marked? | **NO** — 1 of ~145 root documents | marker grep; 0 SUPERSEDED statuses in 1233 artifacts |
| **Phase 2 verdict** | **PARTIAL — ownership is knowable but not uniformly machine-checkable; 10 conflicts recorded, 8 reserved to human authority** | §5 |
