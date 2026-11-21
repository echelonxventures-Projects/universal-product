# EPIC-004 — Determinism Framework — Completion Report

**Program:** EC-1 Execution Engine · **Epic:** EPIC-004 (Determinism Framework)
**Scope executed:** TASK-000031 · TASK-000032 · TASK-000033 (inclusive)
**Authoritative basis:** EC-1 Master Implementation Program; EC-1 Execution
Architecture Determination; Technology Constitution; IMP-000017 (§5 Build Engine —
deterministic + reproducible). Builds on completed EPIC-001 (Foundation),
EPIC-002 (Registry Adapter), EPIC-003 (Compiler Core).
**Status:** ✅ COMPLETE — all three tasks delivered, verified, and gated.

> Additive engineering package `engine/determinism/`. No architecture change, no
> redesign, no writes to the certified corpus. Reuses the Foundation, Registry
> Adapter, and Compiler APIs verbatim. **Determinism is measured, not assumed.**

---

## 1. Objective & mandatory rules — conformance

| # | Mandatory rule | How satisfied | Evidence |
|---|----------------|---------------|----------|
| 1 | No architecture changes | Additive `engine/determinism/`; nothing existing altered | §4 inventory |
| 2 | No redesign | Reuses Foundation obs/config, Registry Adapter, and the Compiler pipeline as-is | `reproduce.py` imports |
| 3 | No modifications to certified corpus | Harness writes only to temp/caller dirs; frozen-path guard clean over the change set | §5 |
| 4 | Reuse existing Foundation/Registry/Compiler APIs | `CompilerPipeline`, `Signer`, `RegistryAdapter`, `serialize/deserialize` reused | `reproduce.py`, `hermetic.py` |
| 5 | Determinism measured, not assumed | `double_build` compiles twice and byte-compares every artifact category | §6 |
| 6 | Every determinism failure generates evidence | Divergence → `reproducibility_report.json`; gate writes `determinism-evidence.json` | §5, §6 |
| 7 | No placeholders | Complete, executable implementation | §4 |
| 8 | No pseudocode | Production Python only | §4 |
| 9 | Production-quality only | Typed, immutable, structured errors, stdlib-only, ruff clean | §5 |
| 10 | Coverage ≥ 90% | **99.52% overall**; **100% on every `engine/determinism` module** | §5 |

---

## 2. Task-by-task delivery

| Task | Deliverable | Module |
|------|-------------|--------|
| **TASK-000031** | Hermetic build controls — `hermetic_env() -> HermeticEnvironment`: pinned toolchain verification, normalized timestamps, deterministic ordering, deterministic serialization validation, environment/locale/timezone/file-ordering normalization, dependency-lock verification | `hermetic.py` (+ `errors.py`) |
| **TASK-000032** | Reproducibility harness — `double_build(bp_id) -> ReproducibilityResult`: isolated A/B builds, byte-compare of generated source + manifests + SBOM + signatures + publication payloads, diff report + `reproducibility_report.json` | `reproduce.py` (+ `blueprints/BP-DATA-0001.json`) |
| **TASK-000033** | Determinism CI gate — reproducibility execution, diff detection, fail-on-divergence, artifact preservation, evidence publication | `.github/workflows/determinism.yml` (+ `reproduce.main` CLI / `ec1-determinism`) |

### Required interfaces

- `hermetic_env() -> HermeticEnvironment` ✅
- `double_build(bp_id) -> ReproducibilityResult` ✅ (PASS ⇒ `byte_identical=True`;
  FAIL ⇒ `byte_identical=False` + `reproducibility_report.json`)

---

## 3. How determinism is achieved (and measured)

The compiler already emits no wall-clock/ambient state and sorts all orderings
(IMP-007 §5). EPIC-004 makes that guarantee **explicit and testable**:

- **Hermetic environment** normalizes `LC_ALL=C`, `LANG=C`, `TZ=UTC`,
  `PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH=0`, applied within a restoring context
  manager, and pins the toolchain (`ucos-imp-007-universal-compiler@1.0.0`,
  Python `>=3.12`). Two independent constructions share one `fingerprint`.
- **Same signing key** for both builds ⇒ byte-identical HMAC-SHA256 signatures.
  Production keys remain by-reference (`env://…`); the harness default key is a
  non-secret determinism fixture.
- **`double_build`** compiles the blueprint twice into isolated output dirs and
  compares every materialised file's SHA-256, grouped into the five required
  categories.

---

## 4. Created directories & files

```
engine/determinism/                          (NEW package)
├── __init__.py                              public API surface
├── errors.py                                TASK-000031  determinism error taxonomy
├── hermetic.py                              TASK-000031  hermetic build controls
├── reproduce.py                             TASK-000032  reproducibility harness + CLI gate
├── blueprints/
│   └── BP-DATA-0001.json                    TASK-000032  canonical BP-DATA reproducibility input
└── EPIC-004-COMPLETION-REPORT.md            this report

engine/tests/
├── unit/test_hermetic.py                    hermetic controls tests
├── unit/test_reproduce.py                   reproducibility harness tests
└── integration/
    ├── __init__.py                          (NEW) integration test package
    └── test_determinism.py                  success criterion + CI-gate behaviour

.github/workflows/determinism.yml            TASK-000033  determinism CI gate
pyproject.toml                               (MODIFIED) coverage scope + ec1-determinism script + package-data
```

> Note on test paths: the mission listed `tests/unit/…` and `tests/integration/…`.
> To honour Mandatory Rules 1 & 2 (no architecture change) the tests are placed
> under the repository's established `engine/tests/` tree (`unit/` and a new
> `integration/`), so they are discovered by the existing `pytest`/coverage
> configuration and gate. No file under `00-BOOK/`, `00-SOURCE/`, or `99-FREEZE/`
> was created or modified.

---

## 5. Verification evidence

Commands run in the pinned dev environment (`pip install -e ".[dev]"`; target
Python 3.12+, executed on 3.14):

**Lint (ruff — CD-01/CD-04):**
```
python -m ruff check engine   →  All checks passed!
```

**Tests + coverage gate (`--cov-fail-under=90`):**
```
281 passed
Required test coverage of 90% reached. Total coverage: 99.52%

engine/determinism/__init__.py     100%
engine/determinism/errors.py       100%
engine/determinism/hermetic.py     100%
engine/determinism/reproduce.py    100%
```

**Build (DE-01):**
```
python -m build → Successfully built ucos_ec1_engine-0.1.0.tar.gz and
                  ucos_ec1_engine-0.1.0-py3-none-any.whl
  (engine/determinism/** + blueprints/BP-DATA-0001.json packaged;
   console script ec1-determinism registered)
```

**Frozen-path guard (DP-03) over the EPIC-004 change set:** exit 0 (clean).

---

## 6. Reproducibility & determinism evidence

**`double_build("BP-DATA-0001")` against the real `00-BOOK` registry:**
```
byte_identical = True
artifact_id (A) == artifact_id (B) = True   →  UCOS-CMP-BP-DATA-0001-5cdc24681ea75f46
files byte-compared = 7   |   divergences = 0
categories:
  generated_source      : identical
  manifests             : identical
  sbom                  : identical
  signatures            : identical
  publication_payloads  : identical
environment_fingerprint = d52bb3e84695c1b38d36879caea1cd25dbef0467a427d8ad286a4506f5ea3e1b
```

**CI gate (`python -m engine.determinism.reproduce BP-DATA-0001`):** exit 0 on
identity; writes `determinism-evidence/determinism-evidence.json` and
`determinism-evidence/BP-DATA-0001-reproducibility_report.json`. On any byte-level
divergence the gate exits 1 (verified by `test_ci_gate_fails_on_divergence` and a
monkeypatched build-B mutation in `test_double_build_detects_injected_divergence`).

---

## 7. Success criteria

Proven: **same blueprint · same compiler · same environment definition ⇒ same
output every time.**

```
double_build("BP-DATA-0001")  →  byte_identical = True
```
with zero differences across generated code, manifests, packages, SBOM,
signatures, and publication payloads.

**STOP — EPIC-004 complete. TASK-000034/000035/000036/000037 and EPIC-005 (and
later) not begun.**
