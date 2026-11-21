# UCOS-CVR-001 · 00 — VERIFICATION ARCHITECTURE REPORT

> **Mission:** UCOS-CVR-001 Coverage & Verification Reconciliation.
> **Mode:** DETERMINATION ONLY. No implementation. Nothing under `engine/`, `platform/`,
> `intelligence/`, `00-BOOK/`, `verify.sh`, `pyproject.toml`, `.github/` or any test was modified.
> **Authority:** NONE (DERIVED TRUTH). This package proposes; it does not legislate.
> **Temporal anchor:** commit `898ef8d`, working tree clean at determination time. No wall-clock
> timestamp appears anywhere in this package — see `04-UNIVERSAL-TEMPORAL-VERIFICATION-SPECIFICATION.md`
> for why a commit anchor is used in place of one.

---

## 1. Executive determination

The repository does not lack verification. It has **more verification machinery than any single
authority can see**. Eleven independent verification authorities exist and each is internally
sound; what does not exist is the **binding** between them, and the **universe** each one is
entitled to speak about.

Consequently three structural defects are present, all of the same shape:

| # | Defect | Mechanism | Measured magnitude |
|---|---|---|---|
| D-1 | **Universe by enumeration** | The coverage universe is a hand-maintained list of 34 `--cov=` entries in `pyproject.toml`, and the test universe is a hand-maintained `testpaths` of 2 directories. | 44 229 statements outside the coverage universe; **4 117 passing tests never executed by any gate** |
| D-2 | **Declared ≠ measured** | A package may be declared in the coverage universe and still produce no coverage data; the report silently omits it instead of failing. | `platform/validation_intelligence` — 842 statements, declared in both `--cov` and `[tool.coverage.run].source`, **absent from `coverage.xml`** |
| D-3 | **Aggregate-only threshold** | One repository-wide `--cov-fail-under=90` with no per-unit floor lets fully-unverified units hide behind well-verified ones. | `engine/graph` 54.5 % · `engine/knowledge` 80.8 % · `engine/knowledge/ukip/cli.py` **0.0 % of 255 lines** (a shipped console script) |

Aggregating D-1..D-3: the gate reports **94.11 % line-rate** over its curated universe. Measured
over the whole production universe with every existing passing test, the same repository is at
**85.85 %** (pytest-cov, branch-inclusive) / **84.83 %** (statement basis). Neither number is
wrong — they answer different questions. The defect is that only one of them is *asked*, and the
question is asked by a hand-edited list rather than by Repository Truth.

**The mission objective follows directly:** the verification universe must become a *derivation*
over the registration/classification substrate that already exists, not a list.

---

## 2. Repository Truth as measured (evidence base)

All figures below are reproducible from commit `898ef8d` with read-only commands.

### 2.1 Artifact universe

| Quantity | Value | Source of truth |
|---|---|---|
| Tracked files | **4 862** | `git ls-files -z` |
| Python files | **1 596** | `git ls-files '*.py'` |
| Test files | **638** | tracked `*.py` under a `tests/` path |
| Registered artifacts | **1 204** | `00-BOOK/DATA/artifacts.json` |
| Registered ∧ tracked | **1 204** (100 %) | — no dangling registration, no drift |
| Eligibility universe | **1 204** (24.8 % of tracked) | `ukb.py::eligibility_universe()` |
| Eligible ∧ unregistered | **0** | registration is *closed over its own universe* |
| Tracked ∧ unregistered | **3 658** (75.2 %) | 2 006 `.md` · **1 596 `.py`** · 37 `.json` · 8 `.sh` · 8 `.yml` |

The registration authority is **not broken — it is bounded**. `config.INCLUDE_EXTENSIONS =
(".md", ".txt", ".docx", ".json")`, so **no source file in this repository is a registered
artifact**. `config.EXCLUDE_DIR_PREFIXES` further removes `00-MASTER/` (operational memory),
`00-BOOK/{tools,DATA,REGISTRIES,VOLUMES,CONTROL-TOWER,PORTAL}/` (generator + generated),
`.github/`, `.kiro/`.

This is the single most consequential fact in this report: **the thing the verification
architecture must classify (code) is invisible to the authority that classifies things
(registration).** Task 1 cannot be satisfied by extending `artifacts.json`; it requires a
classification axis that is *orthogonal* to corpus identity and derived from the same substrate.

### 2.2 Verification universe as executed today

| Gate | Scope actually executed | Scope omitted |
|---|---|---|
| `ucos_ruff_gate` (verify.sh S1, CI, pre-commit) | `ruff check` + `ruff format --check` over `engine platform` | **585 `.py` files** — `service/` 132, `data/` 122, `application/` 112, `infrastructure/` 112, `intelligence/` 71, `00-MASTER/` 21, `00-BOOK/tools/` 13, `scripts/` 1, `00-CMG/` 1 |
| `pytest` (verify.sh S2, CI) | `testpaths = engine/tests, platform/tests` → 4 751 tests | `service/tests` 1 070 · `application/tests` 1 094 · `data/tests` 954 · `infrastructure/tests` 877 · `intelligence/tests` 122 = **4 117 tests, 3 995 of which pass today** |
| `coverage` (verify.sh S3) | 33 measured packages / 37 451 statements | 44 229 statements in 20+ packages |
| `ukb.py enforce --pre` (verify.sh S4, CI) | eligibility · validity · classification · registration over 1 204 corpus artifacts | all code, all operational memory |
| `register.sh --guard` (verify.sh S5 opt-in, CI) | atomic registration transaction + drift | — |
| `determinism.yml` | double-build divergence over `BP-DATA-0001` + 3 test modules | — |
| `uccep / urrc / uer / uei / ucda` gates | declaration-driven self-guards + aggregate gate | — |
| `repo-ops.sh` (`repo-operations.json`) | doctor · verify · coverage.xml ≥ 90 · freeze · acceptance | see §4 D-6 |

### 2.3 Verification authorities that already exist (reuse-before-create inventory)

| Authority | Home | What it is authoritative for |
|---|---|---|
| Eligibility boundary | `git ls-files --cached` via `ukb.py::_repo_artifact_paths()` | what is *in* the repository |
| Classification | `ukb.py::classify()` + `config.CLASSIFY_RULES` + path-derived catch-all | corpus family / category / volume; **total by construction** (`unclassified == 0`) |
| Registration | `00-BOOK/tools/register.sh`, `ukb.py`, `00-BOOK/DATA/*.json` | identity, page allocation, traceability, content hash |
| Registration validation | `engine/registry/universal/` (`ucos-registry`) | registration validity + deterministic evidence |
| Coverage graph | `platform/coverage/` (Universe→Phase→Program→Implementation→Epic→Module→CodeAsset→RuntimeAsset) | **architectural** coverage, reconstructed from committed artifacts, fail-closed on unevidenced edges |
| Measurement | `platform/measurement/` (`ucos-measure`) | measurement over Registry Truth |
| Universal validation | `platform/universal_validation/` (`ucos-validate`) | architecture/implementation/dependency/registry/schema/runtime/quality domains |
| Validation intelligence | `platform/validation_intelligence/` (`ucos-validate-intel`) | cross-capability consistency, compatibility, compliance |
| Assurance policy | `platform/universal_assurance/` + `data/ucos-assurance-policy.json` | **policy-driven** obligation/criterion/gate/metric vocabulary — already zero-enumeration |
| Certification | `engine/certification/`, `engine/universal_certification/`, `platform/certification/` | certification determinations, hash-chained registry |
| Determinism | `engine/determinism/` (`ec1-determinism`) | byte-identical reproducibility |
| Aggregate constitutional gate | `00-MASTER/UCCEP-000000/uccep_engine.py` + `uccep-bindings.json` | binding of all located gates; tiered (boot/standard/full) |
| Repository closure | `00-MASTER/UAKOS-CLOSURE-002/` phases 1–3 | concept↔repository closure, gap register |
| Repository reality | `00-MASTER/URRC-000001/` | derived-vs-declared reality, 8 self-guards |

**Determination:** the verification architecture requires **no new engine**. It requires one
*declaration* and one *derivation* placed on top of this inventory. Every capability named in
Task 2 either exists here or is honestly absent (§4 D-7, D-8).

---

## 3. The architecture determined

Five universes, each a pure function of the one below it. Nothing enumerated; nothing hand-maintained.

```
        ┌────────────────────────────────────────────────────────┐
  U0    │ REPOSITORY UNIVERSE   = git ls-files --cached          │  authority: version control
        └────────────────────────┬───────────────────────────────┘
                                 │ classify(path, metadata, ownership)
        ┌────────────────────────▼───────────────────────────────┐
  U1    │ CLASSIFICATION UNIVERSE = U0 → exactly one of 15 classes│  authority: classification declaration
        └────────────────────────┬───────────────────────────────┘   (fail-closed: Unknown ⇒ gate fails)
                                 │ policy(class) → obligations
        ┌────────────────────────▼───────────────────────────────┐
  U2    │ VERIFICATION UNIVERSE = U1 × 22 verification types      │  authority: verification policy declaration
        └────────────────────────┬───────────────────────────────┘
                                 │ σ(class) = contributes?
        ┌────────────────────────▼───────────────────────────────┐
  U3    │ COVERAGE UNIVERSE = { u ∈ U1 : σ(class(u)) = CONTRIBUTES }│ authority: coverage ontology
        └────────────────────────┬───────────────────────────────┘
                                 │ every mandatory obligation satisfied ∧ evidence resolves
        ┌────────────────────────▼───────────────────────────────┐
  U4    │ CERTIFICATION UNIVERSE = certifiable subset of U2 ∪ U3  │  authority: certification engines
        └────────────────────────────────────────────────────────┘
```

Three invariants make this an *architecture* rather than a configuration:

- **I-1 Totality.** `|U1| = |U0|`. Every tracked path receives exactly one class. An unmatched
  path is classed `Unknown`, and `Unknown ≠ 0` is a hard gate failure. There is no `MISC`
  dead-end and no whitelist. (This mirrors the property `ukb.py::classify()` already guarantees
  for the corpus.)
- **I-2 Derivation.** No verification scope is written as a path, a package name, or a directory
  in any executable file. Scope is always `select(U1, class ∈ …)`. Adding a package, a band, a
  capability or an entire new tree changes **no** code and **no** threshold.
- **I-3 Declared = measured.** Every element of `U3` must appear in the coverage report. A
  declared-but-unmeasured element (D-2) is a gate failure, not an omission.

---

## 4. Findings register

Severity: **B** blocking for implementation · **H** high · **M** medium.

| ID | Sev | Finding | Evidence |
|---|---|---|---|
| D-1 | B | Coverage + test universes are hand-enumerated | `pyproject.toml` 34 × `--cov=`, `testpaths` = 2 dirs |
| D-2 | B | Declared-but-unmeasured is silent | 34 declared cov targets → 33 packages in `coverage.xml`; `platform/validation_intelligence` (842 stmts) missing |
| D-3 | B | No per-unit coverage floor | `engine/graph` 54.5 %, `engine/knowledge` 80.8 %, `engine/knowledge/ukip/cli.py` 0.0 %/255 lines |
| D-4 | B | 4 117 tests are orphaned from every gate; 3 995 pass, so this is unclaimed verification value, not dead code | `pytest --collect-only` per directory |
| D-5 | H | Lint universe ⊂ code universe | `ucos_ruff_gate` scopes `engine platform`; 585 `.py` unlinted |
| D-6 | H | `repo-operations.json` feeds **hand-authored** facts into the acceptance gate: `coverage: [{covered:1,total:1}×6]`, `units[].certified: true`, and `architecture-freeze` with `paths: []` (vacuous stage) | `repo-operations.json` |
| D-7 | H | The **Universal Temporal Framework does not exist.** It is chartered as `SPEC/PLANNED` with owners `UNI-006` (Time) / `DOM-0021` (Calendar); planetary/coordinate/TRS/precision items are tagged `[N]` (net-new) | `00-MASTER/UCOS-NUCLEUS-001/04-TIME-CALENDAR-COMMISSION-SCOPE.md` |
| D-8 | H | Wall-clock is used directly in 17 files, UTC-only, no calendar/frame/location parameter; and the determinism guards of URRC/UER/UEI/UCCEP explicitly assert *"byte-identical rendering across runs, **no timestamps**"* — determinism is currently achieved by **omitting** provenance | `00-BOOK/tools/{ukb,ukbx,config,governance_telemetry}.py`, `engine/{graph,graph/architecture}/evidence.py`, `engine/registry/universal/audit.py`, 9 × `00-MASTER/*/‌*_engine.py` `NOW = datetime.now(timezone.utc)`; `.github/workflows/{urrc,uer,uei}-gate.yml` |
| D-9 | M | Coverage threshold `90` is declared in **three** places — `[tool.pytest.ini_options].addopts --cov-fail-under=90`, `[tool.coverage.report].fail_under=90`, `repo-operations.json.min_percent=90` → duplicate authority | grep `90` |
| D-10 | M | Two coverage *ontologies* coexist with no binding: line/branch coverage (`pyproject`) and architectural coverage (`platform/coverage`, 8 node kinds). Neither references the other | `platform/coverage/repository.py` |
| D-11 | M | `intelligence/tests` writes into `intelligence/` during execution (`test_engine_writes_only_under_intelligence_dir`), so it cannot be admitted to the canonical suite without sandboxing — this is why it was excluded from the probe run | test name + `intelligence/UCOS-RIE-*.json` are tracked outputs |
| D-12 | M | `platform/universal_assurance` (14 modules, policy-driven, `data/ucos-assurance-policy.json`) is bound to **no** gate, has **no** tests, and is in **no** coverage universe | grep across `.github/`, `Makefile`, `platform/tests` |

---

## 5. What this report does **not** claim

- It does not claim the 85.85 % figure is the "real" coverage of a *correct* universe. It is the
  measured coverage of the *widest* universe (all seven code roots, tests omitted). The
  authoritative universe is whatever `01`/`02` of this package ratify.
- It does not claim the orphan suites are correct tests — only that they collect and pass
  (3 995 passed, 0 failed) and are currently unexecuted by every gate.
- It could not verify mutation testing, dynamic analysis, supply-chain validation, performance
  validation or SBOM capability: **no such tooling is present in the repository**, and none is
  declared in `[project.optional-dependencies].dev` (`pytest`, `pytest-cov`, `coverage`, `ruff`
  only). Those rows of Task 2 are therefore determined as *Excluded — capability absent* rather
  than *Optional*, with the honest absence recorded (see `01`, Absence Register).
- No probe mutated the repository: `git status --porcelain` was empty before and after every
  measurement. The coverage probes were written to `/tmp` via `COVERAGE_FILE` and deleted; the
  committed `.coverage`/`coverage.xml` are untouched.

---

## 6. Reading order

| Doc | Answers |
|---|---|
| `01-VERIFICATION-CLASSIFICATION-MATRIX.md` | Tasks 1–2 — the 15 classes and the 15 × 22 policy |
| `02-COVERAGE-DETERMINATION-MATRIX.md` | Tasks 3–4 — what counts, what never counts, how it is discovered |
| `03-VERIFICATION-DEPENDENCY-GRAPH.md` | Task 6 — layers, authorities, acyclicity proof, ownership conflicts |
| `04-UNIVERSAL-TEMPORAL-VERIFICATION-SPECIFICATION.md` | Task 5 — temporal provenance without losing determinism |
| `05-VERIFICATION-CONSTITUTION.md` | Task 7 — the permanent instrument to be ratified |
| `06-IMPLEMENTATION-ROADMAP.md` | Task 8 — waves, gates, exit criteria |
| `07-REPOSITORY-IMPACT-ASSESSMENT.md` | blast radius, migration risk, what breaks |
| `08-FINAL-READINESS-VERDICT.md` | the verdict and the approval questions that must be answered |

*End of 00-VERIFICATION-ARCHITECTURE-REPORT.md*
