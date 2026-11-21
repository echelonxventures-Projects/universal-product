# REPOSITORY ASSIMILATION INVENTORY

| Field | Value |
|---|---|
| **ARTIFACT** | `REPOSITORY-ASSIMILATION-INVENTORY.md` |
| **PHASE** | Phase 1 — Repository Assimilation |
| **AUTHORITY** | **NONE — DERIVED TRUTH.** Inventory only. Creates no owner, moves no owner, registers nothing. |
| **CLASSIFICATION** | `EVIDENCE` |
| **BOUNDARY** | Governed by `ASSESSMENT-BOUNDARY-DETERMINATION.md` §2 (evidence hierarchy), §3 (classification), §5 (handling rules) |
| **SNAPSHOT** | `1f869865` + 113 uncommitted entries · 5844 tracked files · 11 463 files on disk |
| **METHOD** | `git ls-files` census (tracked truth) cross-checked against on-disk `find` census; registry counts read from the owning registry, never from prose |

---

## 0. Counting rule

Two populations are counted throughout, and never conflated:

| Population | Size | Meaning |
|---|---|---|
| **TRACKED** | **5844** | The governed boundary. What `UCOS-UGA-001` measures, what a clone receives. |
| **ON DISK** | **11 463** | Tracked + generated + excluded. What the assessor can read. |

Delta = 5619 files, of which 5050 are `.pyc`. Every category table below states which population it counts. A count from a registry (`artifacts.json`, `CMG-REGISTRY.json`, `generated-artifact-registry.json`) is labelled as such, because a registry's population is a *declaration*, which may differ from the filesystem — and where it does, that is a finding, not an error to be smoothed over.

**Tracked file-type census:** `.md` 2985 · `.py` 2027 · `.json` 662 · `.yml` 28 · `.docx` 10 · `.sh` 9 · `.txt` 4 · other 119.

---

## 1. Master inventory

| Category | Count | Location | Status |
|---|---|---|---|
| **Constitutional artifacts** | **44 recognized** (of 165 tracked paths naming CONSTITUTION) | `00-CMG/CMG-REGISTRY.json` (registry) · `00-CMG/` (15) · `00-CEP/` (48) · `00-MASTER/UAKOS-CLOSURE-006/CONST-01…11` · 7 band constitutions `08-RUNTIME`…`14-SECURITY` · `engine/uckp/law.py` | **PARTIAL** — 32 PROVISIONAL, 11 FROZEN, 1 DECLARED. Gate `cmg-gate.sh` **PASS**, 0 findings, but declared ceiling `READY-PROVISIONAL` with 9 gaps, 7 open questions, 1 vacancy (`VAC-01`) |
| **Universe artifacts** | **21** USIS universes · **2** universe-governing registries · **2** universe catalogs | `00-MASTER/UCOS-USIS-001/02-USIS-UNIVERSE-CATALOG.md` · `15-UNIVERSAL-SCIENCE-INTELLIGENCE/04-REGISTRIES/USIS-REG-001-UNIVERSE-REGISTRY.md` · `00-BOOK/DATA/evidence-universe.json` · `00-BOOK/DATA/observation-universe.json` · `02-MASTER/UCOS-Ω∞-UNIVERSAL-UNIVERSE-CATALOG.md` | **PARTIAL** — universes declared (`USIS-U-ALG…USIS-U-UNK`, 21 distinct) with no code root under `15-*`; `evidence-universe.json` has **2 of 5 classes declared empty** (`DEBUG`, `IMPROVEMENT`) |
| **Architecture artifacts** | **196** tracked paths naming ARCHITECTURE · 7 band stacks (`-001` Constitution → `-006+` Architectures) · 20 `00-BOOK/ADVANCEMENT` · 31 `00-BOOK/MASTER-BOOK` | `08-RUNTIME/` (18) · `09-PLATFORM/` (20) · `10-DATA/` (19) · `11-SERVICE/` (19) · `12-APPLICATION/` (22) · `13-INFRASTRUCTURE/` (20) · `14-SECURITY/` (5) · `04-REFERENCE/` · `06-IMPLEMENTATION/` | **PARTIAL** — uniform band pattern present; `14-SECURITY` has 5 documents and **no `security/` code root**; `08-RUNTIME` has 18 documents and **no `runtime/` code root** |
| **Determination artifacts** | **186** tracked paths naming DETERMINATION, of which **62 at repository root** (145 root `*.md` total) | repository root · `00-MASTER/**` · `02-MASTER/` (80) | **REQUIRES REMEDIATION** — exactly **1** artifact repository-wide carries a supersession header (`MCP-001-…md`); `artifacts.json` uses **no** SUPERSEDED/DEPRECATED status across 1233 artifacts; 18 root determinations are unregistered and awaiting VCS binding |
| **Registry artifacts** | **6** knowledge-book registries · **17** `00-BOOK/DATA` registers · **19** JSON schemas · 179 tracked paths naming REGISTER, 61 naming REGISTRY | `00-BOOK/REGISTRIES/` (6) · `00-BOOK/DATA/` (17) · `00-BOOK/SCHEMAS/` (19) · `00-CMG/CMG-REGISTRY.json` · `00-MASTER/**/[0-9][0-9]-*-REGISTER.md` | **VALIDATED** — `ukb.py validate` **PASS**: 1233 artifacts, append-only page ledger intact, referential integrity OK, jsonschema ran |
| **Implementation artifacts** | **2027 tracked `.py`** (2051 on disk) across 8 package roots + 39 tracked `00-MASTER/**/*_engine.py` + 13 `00-BOOK/tools` modules | `platform/` 788 · `engine/` 637 · `service/` 132 · `data/` 122 · `application/` 112 · `infrastructure/` 112 · `intelligence/` 72 · `realization/` 9 (generated) · `knowledge/` 0 (generated) | **PARTIAL** — real code (46 `NotImplementedError` in ~565k LOC, nearly all `# pragma: no cover` abstract markers; 0 TODO/FIXME in 7 of 8 roots). But **0 `.py` entries exist in `artifacts.json`** — 100% of implementation is outside the registered corpus |
| **Validation artifacts** | **814** tracked test files · **12 613** declared `def test_` · 10 independent validation authorities | `engine/tests/` (234 files, 4028 tests) · `platform/tests/` (324, 5568) · `intelligence/tests/` (119) · `application/tests/` (1082) · `service/tests/` (1038) · `data/tests/` (887) · `infrastructure/tests/` (821) · `realization/tests/` (51) | **REQUIRES REMEDIATION** — `pyproject.toml:200` `testpaths = ["engine/tests","platform/tests","intelligence/tests"]`. **3879 test functions** (application+service+data+infrastructure+realization) are collected by **no** gate, no Makefile target and no CI workflow |
| **Certification artifacts** | **1** certification record (10 domains, 25 checks) · 136 tracked paths naming CERTIFICATION · 25 naming CERTIFICATE · 11 certifications with evidence boundary (UGA-INV-07) | `00-BOOK/DATA/certification.json` · `00-BOOK/REGISTRIES/CERTIFICATION-REGISTRY.md` · `00-MASTER/**/[0-9][0-9]-CERTIFICATION-REPORT.md` | **REQUIRES REMEDIATION** — the single record is `UMB-017 Digital Twin`, verdict CERTIFIED 10/10, scope **1233 documentation artifacts and `executions: 0`**. It certifies the knowledge graph, **not** capabilities and **not** code |
| **Evidence artifacts** | **5** declared evidence classes / 10 surfaces · **499** `_evidence/*.json` files · **213** files under `00-MASTER/**/evidence/` (20 dirs) · 46 tracked paths naming EVIDENCE | `00-BOOK/DATA/evidence-universe.json` (governing) · `application/_evidence/` · `service/_evidence/` · `data/_evidence/` · `infrastructure/_evidence/` · `00-MASTER/*/evidence/` | **PARTIAL** — `00-MASTER/**/evidence/` is `.gitignore`d (`EV-PROGRAMME-EXECUTION-LOG`, population 76, `may_affect_certification: false`, "a pristine clone has none of it"); 2 of 5 classes declared empty |
| **Test artifacts** | see Validation | — | see Validation |
| **Operational artifacts** | **28** CI workflows · **213** Makefile targets (**51** gates) · **9** shell entry points · 1 exclusion register (32 rules, 7 classes) · 1 mutation-governance boundary (5 classes, 7 authorities) | `.github/workflows/` (28) · `Makefile` (121 KB) · `verify.sh`, `bootstrap.sh`, `doctor.sh`, `repo-ops.sh`, `scripts/ucos-env.sh`, `scripts/generate-prerequisites.sh`, `00-BOOK/tools/register.sh`, `00-CMG/tools/cmg-gate.sh` | **PARTIAL** — `verify.sh` aggregates 7 of 10 validation authorities; `rib-gate`, `uccep-gate` and the import-acyclicity checker sit **outside** it, so `verify.sh` passing ≠ repository validating |

---

## 2. Directory structure assimilation

### 2.1 Corpus zones (documentation + governance)

| Zone | Tracked files | Role | Status |
|---|---|---|---|
| `00-BOOK/` | 1356 | Universal Master Knowledge Book: 6 REGISTRIES, 17 DATA registers, 19 SCHEMAS, 12 CONTROL-TOWER standards, 20 ADVANCEMENT, 31 MASTER-BOOK, 1240 PORTAL pages, 13 tools | VALIDATED (`ukb.py validate` PASS) |
| `00-MASTER/` | 1259 | Master Context System: **97 program directories**, 39 tracked engines, MCP-001…007, MCS-000, `UCIC-001` | PARTIAL — 40 program engines carry no capability declaration |
| `02-MASTER/` | 80 | Ω∞ technology constitution, universal universe catalog, EC-3 band frameworks | PARTIAL |
| `00-CEP/` | 48 | Constitutional Engineering Programme: `CEP-000…010` (11 instruments, all T2 PROVISIONAL) + stage records | PARTIAL (PROVISIONAL) |
| `00-CMG/` | 18 | Constitutional Meta-Governance: `CMG-000001` v1.2 (86 articles), `CMG-000002…14`, `CMG-REGISTRY.json`, validator | VALIDATED, ceiling READY-PROVISIONAL |
| `08-RUNTIME` … `14-SECURITY` | 121 | 7 band stacks (Constitution/Theory/Ontology/Taxonomy/Meta-Model/Architectures) | PARTIAL — 2 bands have no code root |
| `15-UNIVERSAL-SCIENCE-INTELLIGENCE/` | 36 | 21 numbered subdomains (00-CONSTITUTION … 20-PROJECTS) | PARTIAL — no code root |
| root `*.md` | 145 | 62 DETERMINATION documents + 55 numbered `01-`…`11-` series + guides | REQUIRES REMEDIATION — 18 unregistered, 49 with no status marker |
| `01-WORKING`, `03-CATALOGS`, `04-REFERENCE`, `05-GENERATION`, `06-IMPLEMENTATION`, `07-ENGINEERING`, `00-SOURCE`, `adr`, `99-FREEZE` | 82 | Ontology register, runtime catalog, reference architecture, ADRs, freeze notice | PARTIAL |
| `EVO-USIS-014/015/016`, `IAC-001A…E` | 52 | Mission/increment records | HISTORICAL |

### 2.2 Implementation zones

| Root | Tracked `.py` | Tests collected by `verify.sh`? | In coverage denominator? |
|---|---|---|---|
| `engine/` | 637 | **YES** (`engine/tests`) | 22 of 25 subpackages. **Excluded: `engine/constitution/` (6888 LOC, ships the `ucos-cel` console script), `engine/uicm/` (5343 LOC, untracked)** |
| `platform/` | 788 | **YES** (`platform/tests`) | 37 subpackages (all non-empty) |
| `intelligence/` | 72 | tests YES, **code NOT in `--cov`** | NO |
| `application/` | 112 | **NO** | NO |
| `service/` | 132 | **NO** | NO |
| `data/` | 122 | **NO** | NO |
| `infrastructure/` | 112 | **NO** | NO |
| `realization/` | 9 (generated, `DO NOT EDIT`) | **NO** | NO |
| `knowledge/` | 0 (generated: 10 handbooks + 2 JSON) | n/a | n/a |
| `00-BOOK/tools/` | 13 (`ukb.py` 118 KB, `ukbx.py` 69 KB, `config.py` 91 KB, 9 connectors) | **NO tests exist** | NO |
| `00-MASTER/**` | 39 tracked engines (~57.6k LOC) | **NO tests exist** | NO |

**Assimilated fact:** the coverage gate `--cov-fail-under=90` names 60 explicit `--cov=` targets, all under `engine.*` / `platform.*`. Approximately half of the repository's non-test Python is outside the denominator.

### 2.3 Generated and excluded zones

| Path | Producer | Bootstrap stage | Tracked? |
|---|---|---|---|
| `knowledge/` | `engine/knowledge/seed.py` + `engine.knowledge.cli init/capabilities/docs` | `generate-prerequisites.sh` 1–3 | NO |
| `determinism-evidence/` | `engine.determinism.reproduce` | step 4 | NO |
| `00-MASTER/UAKOS-CLOSURE-002/[0-9][0-9]-*.md`, `closure.json`, `phase2.json`, `phase3.json` | `closure_engine.py`, `phase2_engine.py`, `phase3_engine.py` | steps 5–7 | NO (24 names re-admitted by `!` rules) |
| `intelligence/UCOS-URI-001/`, `UCOS-UPI-001/` | `intelligence.research build`, `intelligence.publication build` | steps 8–9 | NO |
| `00-MASTER/UAKOS-PHASE-001B/provenance.json` | `provenance_engine.py` | step 10 | NO |
| `realization/` | `intelligence.realization realize` (URI-000001) | step 11 | NO |
| `.runtime/repository-intelligence/UCOS-RPI-DEPENDENCY-GRAPH.{json,dot,mmd}` | `platform.repository_intelligence.cli emit` | **none — manual `make rpi` only** | NO |
| `00-MASTER/**/evidence/` | programme engines | — | NO |
| `.coverage*`, `coverage.xml`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`, `.ec1-venv/`, `dist/`, `*.egg-info/` | toolchain | — | NO |

All are classified in `00-BOOK/DATA/exclusion-register.json` (32 entries, 7 classes, 4 invariants; `ignored_unclassified = 0`).

**Assimilated fact:** `generated-artifact-registry.json` declares **344** generated artifacts with 30 producer homes and `bootstrap_gaps: []`. `verify.sh` Stage 1b re-runs **11** producers. The outputs of the remaining ~19 producers on disk are stale observations under boundary rule §5.1(2) and are admitted only as such.

---

## 3. Verification and configuration assimilation

### 3.1 `verify.sh` — the canonical entry point (11 stages)

| # | Stage | Authority |
|---|---|---|
| 0 | venv self-heal (`ucos_ensure_venv`) | `scripts/ucos-env.sh` |
| 1 | ruff lint + format-check (engine + platform) | `ucos_ruff_gate`, CD-01/CD-04 |
| 1b | prerequisite generation (11 producers) | `scripts/generate-prerequisites.sh`, P0-FINAL-CONVERGENCE-001 |
| 2 | pytest + coverage (`--cov-fail-under=90`) | CD-02 |
| 3 | coverage report | coverage CLI |
| 4 | `ukb.py enforce --pre` | UMB-IMP-001 |
| 5 | `ukb.py validate` | CRAP-001 / CAEM-001 S-2 |
| 6 | `cmg-gate.sh` (CMG-INV-01..12) | CMG-000001 Art. L |
| 6b | `uga_engine.py gate` (UGA/CAA/OBS invariants) | UCOS-UGA-001 |
| 6c | `engine.uaue.gate --gate` | UAUE-000001 |
| 6d | `engine.uaue.gate --replay` | UAUE-000001 derived truth |
| 7 | *(opt-in `--full`)* `register.sh --guard` | REG-AUTO-001 |

### 3.2 Validation authorities NOT in `verify.sh`

| Authority | Entry point | Consequence |
|---|---|---|
| `UCOS-RIB-001` (12 gates, incl. GATE-12 repository-clean) | `make rib-gate`, CI `rib-gate.yml` | working-tree contamination invisible to `verify.sh` |
| `UCCEP-000000` (26 gates, 21 programmes, 48 checks) | `make uccep-gate`, CI `uccep-gate.yml` | the aggregate constitutional certifier — and the named source of the freeze blocker |
| Import acyclicity (Tarjan SCC) | `platform/repository_intelligence/graph.py` via `make rpi-gate` | no gate validates the Python import graph; output tree `.runtime/` is gitignored |
| `UCOS-UFEP-001` freeze eligibility | `make freeze-gate` | freeze authority evaluated only on demand |

### 3.3 Configuration

| Artifact | Assimilated fact |
|---|---|
| `pyproject.toml` (19 KB) | `dependencies = []` (stdlib-only, TP-04/TP-05); dev pins pytest 8.3.4 / pytest-cov 6.0.0 / coverage 7.15.2 / ruff 0.8.4 / jsonschema 4.26.0; `testpaths` 3 roots; `omit = ["engine/tests/*","platform/tests/*"]` only; `packages.find include = ["engine*","platform*"]` — six roots are **not packaged** |
| `Makefile` (121 KB) | 213 targets, 51 gate targets; `test:` is bare `pytest`, inheriting the restricted `testpaths` |
| `.gitignore` (13 KB, 214 lines) | every rule classified in `exclusion-register.json`; records two prior failures of the hidden-generated-dependency class |
| `.github/workflows/` | 28 workflows; 20 invoke an untested `00-MASTER/**/*_engine.py`; only `mcos`, `umk`, `uprf` enforce 100% coverage, each on one engine subpackage |
| `99-FREEZE/` | 3 files: `FREEZE-NOTICE.md`, `SOURCE-HASHES.txt`, `SOURCE-FILES.txt` |

---

## 4. Assimilation findings

Findings only; dispositions belong to Phases 2–9.

| # | Finding | Evidence | Class |
|---|---|---|---|
| A-01 | Implementation is entirely outside the registered corpus | `artifacts.json` holds 1233 artifacts and **0 `.py`** entries | REQUIRES REMEDIATION |
| A-02 | 3879 test functions are collected by no gate | `pyproject.toml:200` vs per-root `def test_` census | REQUIRES REMEDIATION |
| A-03 | ~half of non-test Python is outside the coverage denominator | 60 `--cov=` targets vs 8 package roots; `engine/constitution` (6888 LOC) and `engine/uicm` (5343 LOC) unmeasured | REQUIRES REMEDIATION |
| A-04 | Two band stacks have no implementation root | `14-SECURITY/` (5 docs), `08-RUNTIME/` (18 docs); no `security/`, no `runtime/` | PARTIAL |
| A-05 | Supersession vocabulary exists but is unused | `Lifecycle` 10-stage enum enforced in code; 1 supersession header repository-wide; 0 SUPERSEDED/DEPRECATED statuses in 1233 artifacts | REQUIRES REMEDIATION |
| A-06 | 26 eligible artifacts unregistered, 18 awaiting VCS binding | `ukb.py enforce --pre` on this snapshot | PARTIAL |
| A-07 | 8 tracked executable objects have no universal identity | `uga_engine.py gate`: UGA-INV-01 FAIL (8/5844), UGA-INV-10 FAIL (8/4611) | **BLOCKING** |
| A-08 | Working tree carries material implementation absent from HEAD | 113 entries: `engine/uaue/` (19 modules), `engine/uicm/` (untracked), `00-MASTER/UAUE-000001/` (19 registers), 18 root determinations | **BLOCKING** |
| A-09 | The single certification record covers no code and no execution | `certification.json`: scope 1233 doc artifacts, `executions: 0` | REQUIRES REMEDIATION |
| A-10 | Two evidence classes are declared empty | `evidence-universe.json` `declared_empty_classes: {DEBUG, IMPROVEMENT}` | PARTIAL |
| A-11 | Aggregate certifier gates are not read-only | `uccep_engine.py --gate` cascaded writes into `ACEE-000001`, `BASELINE-001`, `UCL-000001`, `UIS-001` (47 files); `ufep/urat/utce/ucaf --gate` each wrote 5–10 artifacts. Measured this session, then restored | PARTIAL |
| A-12 | No dependency gate observes the Python import graph | `platform/repository_intelligence/graph.py` not in `verify.sh`; `code_roots = ("engine","platform")` excludes 6 of 8 roots | REQUIRES REMEDIATION |

**Phase 1 status: COMPLETE.** All eleven mandated categories are inventoried with counts, locations and evidence-backed status. No category is marked COMPLETE, because in every category at least one layer of the §4.1 chain is unmeasured or failing.
