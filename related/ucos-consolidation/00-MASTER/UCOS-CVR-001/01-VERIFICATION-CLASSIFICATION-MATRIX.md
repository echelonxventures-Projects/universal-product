# UCOS-CVR-001 · 01 — VERIFICATION CLASSIFICATION MATRIX

> **Satisfies:** Task 1 (canonical production universe) and Task 2 (verification policy).
> **Authority:** NONE (DERIVED TRUTH) until ratified. **Anchor:** commit `898ef8d`.

---

## PART A — TASK 1 · THE FIFTEEN CLASSES

`class : U0 → C`, `|C| = 15`, total and single-valued. `U0` is the version-controlled corpus
(`git ls-files --cached`) — the same boundary `ukb.py::_repo_artifact_paths()` already declares,
so eligibility and classification share one authority.

**Discrimination is by evidence, in strict precedence order.** The first rule that matches wins;
the ordering itself is the guarantee of single-valuedness. Rules cite *evidence kinds*, never
paths.

| # | Class | Discriminating evidence (in precedence order) | Measured (probe) |
|---|---|---|---|
| 1 | **Production Runtime** | importable module whose package declares a runtime/execution contract (`runtime`, `execution`, `lifecycle`, `service`, `orchestration` capability binding in the registry) **and** is reachable from a declared entry point | ⊂ Production Library — see note P-1 |
| 2 | **Production Library** | tracked `*.py` under a declared production package root, not test, not generator, not CLI | **907** |
| 3 | **Production CLI** | module named by a `[project.scripts]` entry point, or by a documented `python -m` invocation | **15** (13 declared console scripts + `__main__` surfaces) |
| 4 | **Production Generator** | module that writes tracked files (declares a write-scope guard, or is bound as a generator in a programme declaration) | **42** |
| 5 | **Generated Output** | file whose byte content is reproducible by a Production Generator (regeneration equality holds) | **2 094** |
| 6 | **Evidence** | content-addressed artifact emitted by a verification/certification run; carries a digest and a producer reference | ⊂ Generated Output — see note P-2 |
| 7 | **Documentation** | human-authored prose artifact of an included type, not a governance or certification instrument | **596** |
| 8 | **Configuration** | machine-readable declaration consumed by code (`*.json` declarations, schemas, `pyproject.toml`, workflow inputs) | **528** |
| 9 | **Tooling** | developer/operator automation not shipped as product (`*.sh`, `Makefile`, `.kiro/hooks/*`) | **14** |
| 10 | **Governance** | constitutional / policy / CI-enforcement instrument (`00-CEP`, `00-CMG`, `.github/workflows`, `99-FREEZE`) | **26** |
| 11 | **Certification** | certificate, determination, or verdict artifact asserting a state | ⊂ Documentation / Generated Output — see note P-3 |
| 12 | **Tests** | module under a test root, or matching the test-name convention | **638** |
| 13 | **Examples** | fixture, sample, or demonstration artifact referenced only by tests or documentation | **0 discriminated today** — see note P-4 |
| 14 | **Temporary** | environment/build/cache output; bounded by the ignore authority, therefore **must not be tracked** | **0 tracked** (correct) |
| 15 | **Unknown** | anything reaching the end of the rule chain | **2** (`.gitignore`, `LICENSE`-class extensionless files) → **fail-closed** |

### Notes on the probe (honesty markers)

- **P-1** The probe could not separate *Production Runtime* from *Production Library* from paths
  alone. Runtime-ness is a **capability property**, not a path property: it must come from the
  registry/capability binding. Until `REG` supplies it, class 1 collapses into class 2. This is a
  **known derivation gap**, listed as roadmap item W2-3 — it is not fudged here.
- **P-2 / P-3** *Evidence* and *Certification* are likewise semantic subsets of *Generated
  Output* / *Documentation*. They are separable **only** by producer declaration (which engine
  emitted them, under which obligation). The probe deliberately did not guess.
- **P-4** *Examples* returned zero because no artifact in the tree self-declares as an example.
  Either the class is genuinely empty (acceptable) or fixtures inside `*/tests/` absorb it
  (likely). Ratification must choose; the class is retained because the taxonomy must be open.
- The probe's 2 `Unknown` results prove the fail-closed path is reachable and that totality is
  **not** yet satisfied by any existing authority — exactly the condition I-1 must remove.

### Consequence for the classification authority

`ukb.py::classify()` is total and rule-ordered and **must be reused as the pattern**, but its
codomain is *corpus identity* (`program`, `category`, `volume` — BOOK/CEP/ENG/PLT/…), not
verification class. The two axes are orthogonal:

```
corpus identity   (WHO owns it, WHERE it lives in the Book)   ← ukb.classify()   EXISTS, total
verification class(WHAT verification it owes)                 ← class()          MISSING
```

**Determination:** do **not** overload `ukb.classify()`. Introduce the verification class as a
second projection over the *same* substrate, so a single path yields `(program, category, volume,
verification_class)` and the two authorities can never disagree about *which files exist*.

---

## PART B — TASK 2 · THE 15 × 22 POLICY MATRIX

**Legend** — `M` Mandatory · `O` Optional (run when applicable; never blocks) · `X` Excluded
(categorically inapplicable) · `X*` Excluded **because the capability is absent from the
repository** (becomes `O`/`M` only by ratified admission of tooling — see Absence Register).

| Class \ Type | LNT | UT | IT | ST | COV | CRT | RTV | SEC | CMP | PRF | MUT | SAS | DAS | DEP | SUP | ARC | TWN | REP | REG | KNW | CTX | TMP |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 Production Runtime | M | M | M | M | **M** | M | M | M | M | X* | X* | M | X* | M | X* | M | M | M | M | O | M | M |
| 2 Production Library | M | M | M | O | **M** | M | O | M | M | X* | X* | M | X* | M | X* | M | M | M | M | O | O | M |
| 3 Production CLI | M | M | M | M | **M** | M | M | M | M | X* | X* | M | X* | M | X* | M | M | M | M | X | O | M |
| 4 Production Generator | M | M | M | M | **M** | M | M | M | M | X* | X* | M | X* | M | X* | M | M | M | M | M | M | M |
| 5 Generated Output | X | X | X | X | **X** | M | X | O | M | X | X | X | X | X | X | X | M | M | M | O | X | M |
| 6 Evidence | X | X | X | X | **X** | M | X | O | M | X | X | X | X | X | X | X | M | M | M | O | X | M |
| 7 Documentation | X | X | X | X | **X** | O | X | X | M | X | X | X | X | X | X | X | O | M | M | M | O | O |
| 8 Configuration | X | X | O | X | **X** | M | O | M | M | X | X | M | X | M | X* | M | O | M | M | O | O | O |
| 9 Tooling | M | O | O | X | **X** | O | O | M | O | X | X | M | X | M | X* | O | X | M | O | X | X | O |
| 10 Governance | X | X | X | X | **X** | M | X | M | M | X | X | X | X | X | X | M | M | M | M | M | M | M |
| 11 Certification | X | X | X | X | **X** | M | X | X | M | X | X | X | X | X | X | X | M | M | M | O | X | M |
| 12 Tests | M | X | X | X | **X** | X | X | M | M | X | X | M | X | M | X* | M | X | M | O | X | X | M |
| 13 Examples | M | O | O | X | **X** | O | X | M | O | X | X | M | X | O | X | O | X | M | M | X | X | O |
| 14 Temporary | X | X | X | X | **X** | X | X | X | X | X | X | X | X | X | X | X | X | **M** | X | X | X | X |
| 15 Unknown | X | X | X | X | **X** | X | X | X | X | X | X | X | X | X | X | X | X | **M** | X | X | X | X |

Two cells carry the whole fail-closed discipline:

- **(14, REP) = M** — Repository Validation must prove no `Temporary` artifact is tracked. The
  only verification a temporary artifact owes is its own absence.
- **(15, REP) = M** — Repository Validation must prove `count(Unknown) == 0`. Any other verdict is
  a hard failure. **This is the only mechanism by which "nothing remains unclassified" is
  enforceable** rather than merely asserted.

---

## PART C — TASK 2 · PER-TYPE AUTHORITY, DEFAULT POSTURE, REASON

Per-cell prose for 330 cells would be unmaintainable and would itself become hand-maintained
truth. The honest decomposition is: **posture** is per cell (Part B); **authority** and **reason**
are per type (below) — because a verification type has exactly one owner regardless of what it is
applied to. That is also what makes "no duplicate authority" (Task 6) checkable.

| Code | Verification type | Authority (single owner) | Default posture | Reason |
|---|---|---|---|---|
| LNT | Lint | `ucos_ruff_gate` (`scripts/ucos-env.sh`) — one gate shared by verify.sh, CI, pre-commit | M for all code classes | Style/format drift is the cheapest defect class to eliminate; the gate already exists and is drift-free by construction. Scope must become `class ∈ {1,2,3,4,9,12,13}` instead of `engine platform`. |
| UT | Unit Test | `pytest` over the derived test universe | M for production code | Smallest unit of behavioural proof. |
| IT | Integration Test | `pytest` (integration markers) | M for production code | Contract-crossing behaviour cannot be proven by unit tests. |
| ST | System Test | `pytest` + `platform/runtime_operations` | M for runtime/CLI/generator | Only an end-to-end path proves an entry point works. |
| COV | Coverage | `coverage` + `pytest-cov`, universe from classification | **M for classes 1–4 only, X for all others** | See `02-COVERAGE-DETERMINATION-MATRIX.md`. |
| CRT | Certification | `engine/universal_certification`, `engine/certification`, `platform/certification` | M where a state is asserted | A determination without a certificate is an opinion. |
| RTV | Runtime Validation | `platform/runtime_operations`, `platform/runtime_platform` | M for runtime/CLI/generator | Health/lifecycle correctness is observable only at run time. |
| SEC | Security Validation | `ruff` S-rules + `platform/security` | M for all code + config | `select = [… "S"]` already active; scope must follow classification. |
| CMP | Compliance Validation | `platform/validation_intelligence` (compliance reports) | M nearly universally | Every artifact owes authority/status/disclosure conformance. |
| PRF | Performance Validation | **NONE — capability absent** | `X*` | No benchmark harness, no budget declaration, no perf dependency in `[dev]`. Declaring it Optional would create unverifiable policy. |
| MUT | Mutation Testing | **NONE — capability absent** | `X*` | No mutation tool pinned. High-value future admission for classes 1–4 (it is the only defence against assertion-free tests). |
| SAS | Static Analysis | `ruff` (E,F,I,B,UP,S) + `engine/graph/architecture` | M for code + config | Present and pinned. |
| DAS | Dynamic Analysis | **NONE — capability absent** | `X*` | No tracing/fuzzing/instrumented run exists. `platform/observability` (680 stmts) is the natural future owner. |
| DEP | Dependency Validation | `pyproject` pins + `platform/universal_validation` (dependency domain) | M | Runtime deps are empty by constitutional intent (stdlib-only); the pinned `[dev]` set is the whole attack surface. |
| SUP | Supply Chain Validation | **NONE — capability absent** | `X*` | No SBOM, no hash-pinned installs (`pip install -e ".[dev]"` resolves from the index at CI time), no provenance attestation. Recorded, not pretended. |
| ARC | Architecture Validation | `engine/graph/architecture`, `platform/universal_validation` (architecture domain) | M | Layer/ownership violations are structural, not stylistic. |
| TWN | Digital Twin Validation | `00-BOOK/DATA/twin.json` + `platform/repository_intelligence` | M for generated/governance/certification | The twin is the machine-readable mirror; if it diverges, every derived verdict is stale. |
| REP | Repository Validation | `ukb.py enforce` + `register.sh --guard` + `platform/repository_operations` | **M for all 15 classes** | The only type with no exclusions: every artifact owes the repository its existence, classification and cleanliness. |
| REG | Registration Validation | `engine/registry/universal` over `00-BOOK/DATA/*.json` | M except Temporary/Unknown | Unregistered ⇒ undiscoverable ⇒ unverifiable. |
| KNW | Knowledge Validation | `engine/knowledge` (UKDA/UKIP) + `UAKOS-CLOSURE-002` | M for docs/governance/generators | Knowledge-Once: a concept must be homed exactly once. Already gated (`concepts=437, gaps=0`). |
| CTX | Context Validation | `engine/context` (UCXI-000001, 15 context kinds) | M for runtime/generator/governance | A verification run that cannot state its own context is not reproducible. |
| TMP | Temporal Validation | **PARTIAL — framework absent, owners declared** (`UNI-006`/`DOM-0021`) | M for every evidence-bearing class | See `04-UNIVERSAL-TEMPORAL-VERIFICATION-SPECIFICATION.md`. Currently satisfiable only in its degenerate form (*absence* of wall-clock). |

### Absence Register (fail-closed honesty)

| Type | Status | What would be required to move it out of `X*` |
|---|---|---|
| PRF | ABSENT | a pinned benchmark harness + per-capability performance budgets declared as data |
| MUT | ABSENT | a pinned mutation engine + a survival-threshold declaration per class |
| DAS | ABSENT | instrumented execution owned by `platform/observability` + a trace assertion vocabulary |
| SUP | ABSENT | SBOM generation, hash-pinned dependency installation, provenance attestation |
| TMP | PARTIAL | the Universal Temporal Framework itself (`UNI-006` EXTEND + `DOM-0021` EXTEND, `[N]` items) |

**Rule:** an absent capability is `X*` with a named owner-to-be. It is never silently `O`. A
policy that cannot be executed must not be declared satisfied — this is the same discipline
`URRC-000001 --check-no-fabrication` already enforces for derived records.

---

## PART D — WHAT CHANGES vs TODAY (per class)

| Class | Today | Under this matrix |
|---|---|---|
| 1–2 Runtime / Library | 33 of ~53 packages verified; 44 229 stmts invisible | all production packages, derived; per-unit floor applies |
| 3 CLI | 13 console scripts, 2 effectively unverified (`ukip/cli.py` 0 %/255, `validation_intelligence` unmeasured) | CLI becomes a first-class class with `ST` + `COV` mandatory |
| 4 Generator | generators verified incidentally, by being inside `engine`/`platform` | generator class gains mandatory `KNW` + `CTX` + regeneration equality |
| 5–6 Generated / Evidence | excluded implicitly (never in `--cov`) | excluded **explicitly and provably** (σ = NEVER), with drift + twin obligations instead |
| 12 Tests | linted, never coverage-measured (correct), `omit = */tests/*` | unchanged posture, now *derived* rather than hard-coded in `[tool.coverage.run].omit` |
| 14 Temporary | excluded by `.gitignore` | additionally *proven* absent by `REP` |
| 15 Unknown | **no such concept** | exists, counted, and blocks the gate at `> 0` |

*End of 01-VERIFICATION-CLASSIFICATION-MATRIX.md*
