# UCOS Ω∞ — UNIVERSAL TRUTH AUTHORITY AND RUNTIME INDEPENDENCE DETERMINATION

| Field | Value |
|---|---|
| **Classification** | EVIDENCE — DETERMINATION ONLY |
| **Authority** | **NONE — DERIVED TRUTH.** Certifies nothing, ratifies nothing, creates no authority, allocates no ownership, mints no identifier, registers no kind, authorises no work. |
| **Mode** | READ-ONLY. No code modified, no runtime system modified, no registry modified, no configuration modified, no requirement/ADR/phase/roadmap created, no fix implemented, no certification altered, no owner row created. |
| **Baseline** | `git HEAD = bae59755d7e2d3566c93b89c722b68847145269a`, branch `integration/recovery-001` |
| **Reference system** | `logical:git-commit-order@ucos-consolidation`. No wall clock read for any measurement. |
| **Method** | Static reading **plus direct in-memory measurement**. Twenty-seven measurements: `M1`…`M19` carried from the predecessor determination at the same baseline, and `N1`…`N8` new to this determination. Every measurement is a pure function evaluation in a throwaway interpreter. Nothing written to the repository. |
| **Finding markers** | `TA-01`…`TA-26` and contradictions `TX-01`…`TX-20` are **local reading aids scoped to this document**. They register nothing and enter no namespace. |
| **Predecessors** | `UCOS-OMEGA-INFINITY-IDENTITY-DETERMINISTIC-VALIDATION-BOUNDARY-DETERMINATION.md` (`DV-01`…`DV-17`) established the defect for identity. `UCOS-OMEGA-INFINITY-CANONICAL-KNOWLEDGE-RUNTIME-TRUTH-BOUNDARY-DETERMINATION.md` (`CR-01`…`CR-24`, verdict **PARTIALLY PROVEN**) established that the pattern extends to CEU entity, CEU relationship and capability. This determination asks the broader question: is there a *universal truth authority model* at all? |
| **Standing determinations respected** | `RTBD-001`, `CANONICAL-AUTHORITY-DETERMINATION`, `CANONICAL-AUTHORITY-RESOLUTION-DETERMINATION` (Option B **Rejected**), `GATE-PURITY-DETERMINATION` (D-3.4 *"Adopt, do not invent"*), `02-CANONICAL-OWNERSHIP-MATRIX` (`CREATE` unavailable), `GOVERNED-EVOLUTION-STATE-DETERMINATION` (defines, does not reclassify). This determination contradicts none of them, proposes no new engine, and creates no owner row. |

---

## 1. Objective

Determine whether UCOS Ω∞ has a **universal truth authority model** in which all truth originates from canonical knowledge, runtime only projects and executes that truth, and no runtime state can become an accidental authority.

Three questions, in order:

1. **Inventory.** What are all the possible truth sources, and for each: is it canonical, is it persistent, who owns it, who consumes it, and can it change truth?
2. **Detection.** Where does runtime state influence validity, ownership, identity, capability existence, relationship existence, lifecycle state, certification state, or compliance state?
3. **Model.** Does the repository support `Canonical Knowledge → Deterministic Reconstruction → Validation → Runtime Projection`, or `Canonical Knowledge → Bootstrap → Mutable Runtime State → Validation`?

**Answer in one paragraph.** There is no single universal truth authority model; there are two coexisting models, and the repository does not declare which one governs. The target chain is implemented, proven, and measured working for **two** truth objects out of seven examined. The defective chain is implemented for **two process-global mutable authorities** — one previously known (the identity kind space) and one newly established here (`DEFAULT_VOCABULARIES`) — and both leak across capability boundaries in the same measured way. Beneath both sits a deeper finding: **twelve truth facets have no declared owner at all**, and the authority register that would bind deciders to authorities contains exactly one binding out of fourteen declared capabilities, so the modules that actually decide existence, classification, relationship validity, context, trust and integrity exercise no located authority.

**Determination: PARTIALLY PROVEN.** Detail in §15.

---

## 2. Evidence Baseline

### 2.1 Repository state

| Measure | Value |
|---|---|
| `git HEAD` | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch | `integration/recovery-001` |
| Interpreter | `.ec1-venv/bin/python` → `3.12.13 (main, Mar 3 2026) [Clang 21.0.0]` |
| Python files in the six code roots | 1942 |
| Closed `Enum` subclasses across the six roots | 238 (200 distinct names) |
| `from_document` / `from_dict` definitions (non-test) | 105 |
| Module-level mutable containers in `engine/` | **8** (independently re-confirmed) |
| Process-global **mutable authorities** | **2** (§5) |
| Databases | **0** (§3.9) |
| UCAF declared capabilities / resolutions / reconciliations / **realization bindings** | 14 / 17 / 3 / **1** |
| Truth facets with no row in the ownership matrix | **12** (§7) |

### 2.2 Carried measurements (`M1`…`M19`, predecessor, same baseline)

Reproduced and relied upon without re-derivation. The load-bearing ones:

```
M1/M2   29 core RegistryKind + 43 runtime-registered = 72 admissible kinds.
        Fresh process:  is_well_formed(UCOS-CLSS-8966ca9e8d02) = False
        After bootstrap: is_well_formed(UCOS-CLSS-8966ca9e8d02) = True
        Same commit. Same machine. Zero file changes.

M3      Calling may_own_capability('nucleus') — an OWNERSHIP question —
        raised kind_names() 29 → 72 and flipped the identity verdict to True.

M5      ExistenceRegistry.from_document SUCCEEDS in a fresh interpreter that
        never called bootstrap(); restores 72 kinds; round-trip digest
        b68559b7b416955d IDENTICAL.
M7      Zero committed JSON carries schema ucos-constitutional-existence-registry.

M6      IdentifierEntry('UCOS-CLSS-8966ca9e8d02') RAISES in a fresh process,
        constructs OK after bootstrap.
M8      The committed identifier dictionary (212 entries) replays in a fresh
        process, status=PASS, unparsed=0 — it uses only core codes CAP CMPO LYR NUC.

M10/M11 Determinism holds across PYTHONHASHSEED 0/1/42/12345, both import
        orders, and double bootstrap. The system is robust against every
        classical nondeterminism axis and fragile against call history alone.

M12     closure.json: CLOSED, gaps=0, concepts=549, corpus_present=False.
        Gitignored (.gitignore:59) and untracked.
M15     metadata.py:301-303 identity_well_formed is a LIVE call; constitutional
        legality inherits the defect by call, not by stale data.
M17/M18 2 of 29 gates compare verdicts across processes (uaue, uisd); both hold
        the initialization history constant, so neither can detect the defect.
M19     double_build runs both builds in ONE interpreter sharing env/adapter/signer.
```

### 2.3 New measurements — a second process-global mutable authority

This is the principal new finding of this determination.

**N1 — the singleton and its only mutator.** `engine/uckp/vocabulary.py:542`:

```python
DEFAULT_VOCABULARIES = build_vocabulary_registry()
```

`VocabularyRegistry.extend`, read verbatim from the running module:

```python
def extend(self, vocabulary_id: str, term: Term) -> Vocabulary:
    """Admit a previously unknown term. This is the *only* extension mechanism."""
    vocabulary = self.require(vocabulary_id)
    extended = vocabulary.extended_with(term)
    self._vocabularies[vocabulary_id] = extended
    return extended
```

The docstring is the same sentence pattern as `register_kind` — *"This is the **only** extension mechanism"* — and the body mutates the module-level singleton in place.

**N1b — lawfulness changes process-wide, measured:**

```
BEFORE   require_term(KNOWLEDGE_KIND, 'probe-kind-xyz') -> REFUSED (LawViolation)
         [UCKP-LAW-001] term is not registered in this vocabulary
         (vocabulary_id='uckp.knowledge-kind')
  --- DEFAULT_VOCABULARIES.extend(KNOWLEDGE_KIND, Term('probe-kind-xyz', ...)) ---
AFTER    require_term(KNOWLEDGE_KIND, 'probe-kind-xyz') -> ACCEPTED
```

The binding into the admission path, `engine/uckp/registry.py`:

```
:36   from engine.uckp.vocabulary import DEFAULT_VOCABULARIES, VocabularyRegistry
:114  self._vocabularies = vocabularies or DEFAULT_VOCABULARIES
:123  obj.require_lawful(self._vocabularies)
:167  obj.require_lawful(self._vocabularies)
```

So UCKO *lawfulness* — a validity verdict — is decided against a mutable process singleton for every registry that did not pass its own vocabulary.

**N6 — and it leaks across capability boundaries, exactly as identity does:**

```
seed_layers()    BEFORE extend: 14 layers
seed_subjects()  BEFORE extend: 83 subjects
  --- DEFAULT_VOCABULARIES.extend(ARCHITECTURE_LAYER, Term('probe-layer', ...)) ---
seed_layers()    AFTER  extend: 15 layers
seed_subjects()  AFTER  extend: 84 subjects

nucleus subject population changed by mutating a UCKP vocabulary: True
```

Mechanism: `engine/nucleus/catalog.py:39` imports it and `:473` reads it — `vocabulary = DEFAULT_VOCABULARIES.require(ARCHITECTURE_LAYER)`. The nucleus structural population is therefore a function of a UCKP vocabulary's runtime contents.

**Two authorities, one shape.** The identity defect (`M3`) and the vocabulary defect (`N6`) are the same architecture: a module-global mutable container, a single documented extension mechanism that writes only to process memory, no persistence, no loader, and a consumer in a *different* capability whose verdict silently changes.

### 2.4 New measurements — reconstruction, certification, and authority binding

**N5 — the reconstruction test applied to seven truth objects** (delete runtime memory → reload canonical → reconstruct → compare):

| Truth object | Loader | Round trip | Note |
|---|---|---|---|
| CEU `ExistenceRegistry` | `from_document` | **IDENTICAL** | no committed artifact (`M7`) |
| `IdentifierDictionary` | `from_document` | **PASS** | **committed artifact exists** |
| Evolution ledger | `from_document` | — | schema enforced on read |
| `NucleusRegistry` | **NONE** | — | `to_document` only |
| `KnowledgeRegistry` | **NONE** | — | self-declared *canonical* |
| `CertificationLedger` | **NONE** | — | `__init__(self)` — no load path at all |
| `IdentityRegistry` | `from_dict` | — | **re-mints rather than replays** |

**N4 — loader absence, counted:** `to_document` present and `from_document` absent for `engine/nucleus/registry.py`, `engine/knowledge/ukip/registry.py`, `engine/ceu/catalog.py`; neither present for `platform/universal_control_plane/registry.py`.

**N2 — the certification chain is not verified on load.** `platform/universal_assurance/registry.py:178-182` verbatim:

```python
def __init__(self, registry_id: str, entries: Iterable[RegistryEntry] = ()) -> None:
    if not isinstance(registry_id, str) or not registry_id:
        raise AssuranceRegistryError("a certification registry requires a non-empty id")
    self._registry_id = registry_id
    self._entries: list[RegistryEntry] = list(entries)
```

No chain verification. `require_intact()` is called only on write (`register`, `:235`). A read-only consumer that calls `get`/`by_subject`/`count_by_status` never validates the chain it was handed. `engine/certification/ledger.py:82` takes no `entries` at all — `__init__(self) -> None` — so there is no load path, and the module says so: *"It holds only in-memory records and **never writes to the certified corpus** (DP-03); persistence, if any, is the caller's concern via `to_dict`."*

**N3 — the four lifecycle transition tables are plain mutable module containers:**

```
engine/runtime/execution/lifecycle.py  LIFECYCLE_TRANSITIONS  type=dict  (7 states)
engine/context/taxonomy.py             _LIFECYCLE_TRANSITIONS type=dict
engine/uicm/model.py                   _TRANSITIONS           type=dict
engine/uckp/evolution.py               EVOLUTION_CYCLE        type=tuple len=15
```

No writer exists in `engine/` or `platform/`. Latent capability, not exercised.

**N7 — a relationship is registered before it is refused.** `engine/ceu/existence.py:989-1006`: `unit = self._registry.register(ExistenceUnit(...))` executes, *then* `if declared.attribute(ATTR_ACYCLIC): cycle = self.cycle_in(...)` raises `TopologyCycleError`. The offending edge remains registered after the refusal.

**N8 — the authority register binds one decider out of fourteen capabilities.** `00-MASTER/UCOS-UCAF-001/ucaf-authority.json`:

```
capabilities:          14
resolutions:           17
reconciliations:        3
realization_bindings:   1     ← UCAF-RB-01, Execution Authority
```

The single binding is Execution Authority → `engine/runtime/execution/authorization.py`. By UCAF's own accounting, `engine/ceu/*`, `engine/nucleus/*`, `engine/registry/universal/identity.py` and `engine/uckp/*` exercise **no located authority** while being the de facto deciders for at least twelve facets (§7).

---

## 3. Universal Truth Authority Model

### 3.1 The complete truth-source inventory

Thirteen classes of truth source exist. For each: canonical, persistent, owner, consumer, and whether it can change truth.

| # | Truth source | Canonical? | Persistent? | Owner | Consumer | Can change truth? |
|---|---|---|---|---|---|---|
| 1 | **Constitution — prose family** `00-MASTER/CMG-000001…012` | asserted YES | YES (git) | CMG authority (self-declaring) | **NO READER** — zero hits in `*.py`, `*.yml`, `*.sh` | **NO** — cannot reach execution |
| 2 | **Constitution — machine family** `00-CMG/` + `CMG-REGISTRY.json` | registry self-declares `"authority": "NONE (DERIVED TRUTH)"`, names its canonical `.md` | YES | CMG authority | `00-CMG/tools/cmg_validate.py:36,85-101,603`; `uaie-gate.yml` | **YES** — the validator derives every enumeration from it |
| 3 | **Declarations** — 17 `*-declaration.json` | YES | YES | per-programme | 14 read by their engine; **3 unread** (`ceu`, `urr`, `ucxi`) | **YES for 14, NO for 3** |
| 4 | **Seed data** — 24 `SEED_*` constants, 17 in `engine/ceu/catalog.py` | committed **as Python source**; `catalog.py:18-21` disclaims privilege | YES (git) | the declaring module | `bootstrap()` `catalog.py:396`; import-time registration in `platform/universal_pipeline/*` | **YES** — the entire existence universe of every fresh process |
| 5 | **Schemas** — 19 `00-BOOK/SCHEMAS/*.schema.json`, `realization/schema/*`, `mcs-state.schema.json` | YES | YES | corpus / realization | most read; `mcs-state.schema.json` has **no `.py`/`.yml` reader** | **YES** for those read |
| 6 | **Registries — committed** `CMG-REGISTRY.json`, `registry_coverage/declarations.json`, `00-BOOK/DATA/*.json`, UGA object registries | every one self-declares derived | YES | per-programme | their engines | **YES** |
| 7 | **Registries — process memory** identity extension space, `KnowledgeRegistry`, `IdentityRegistry`, UCP capability/ownership, `ExistenceRegistry`, `NucleusRegistry` | several self-declare **canonical** | **NO** | the constructing module | in-process callers | **YES — and this is the defect surface** |
| 8 | **Ledgers** evolution, object birth, certification, DAG, runtime ops, `id-ledger.json` | `AIF AX-01` recorded plane | 2 committed and schema-enforced on read; the rest **memory only** | per-module | `from_document` for 2; nothing for the rest | **YES** |
| 9 | **Configuration** `pyproject.toml`, `repo-operations.json`, `.gitignore`, `exclusion-register.json`, `generated-artifact-registry.json` | YES | YES | authored | `ucos-env.sh:131`, `repo-ops.sh:25`, `mutation_classification.py:56`, `contamination.py:46`, `generated_artifacts.py:51` | **YES — four independent ways for `pyproject.toml` alone** (§3.7) |
| 10 | **Environment variables** ~20 distinct | **NO** | NO | ambient | `os.environ` reads + wholesale `dict(os.environ)` inheritance | **YES for 9 of them** (§3.8) |
| 11 | **Database** | — | — | — | — | **NONE EXISTS** (§3.9) |
| 12 | **Generated artifacts** `knowledge/`, `closure.json`, `coverage.xml`, `realization/`, `.runtime/`, `determinism-evidence/` | declared **NOT** Repository Truth by `.gitignore` and `RTBD-001` | per-clone, untracked | the generating engine | read by 10+ engines/gates | **YES — `coverage.xml` decides a PASS/FAIL** (§3.10) |
| 13 | **Caches** `.ucos/environment-fingerprint.json`, `.ucos-verification-evidence/`, `.mypy_cache`, `.ruff_cache`, `.pytest_cache`, `__pycache__` | NO | YES | the owning engine / tooling | their engines | **NO — and both designed caches enforce this structurally** (§3.11) |

### 3.2 The two coexisting models

Both chains are implemented. Neither is declared as governing.

**Model A — the target, implemented and measured working:**

```
Canonical Knowledge (committed document)
    ↓  from_document — verbatim, journal-verifying, fail-closed
Deterministic Reconstruction
    ↓
Validation
    ↓
Runtime Projection
```

Occurrences: `IdentifierDictionary` (committed artifact + loader + four persistence tests + `M8` fresh-process `PASS`); `ExistenceRegistry.from_document` (`M5` — works in a fresh process, digest identical — but **no committed artifact**, `M7`); the evolution ledger and object-birth ledger (schema enforced on read, `evolution.py:380-395`, `ledger.py:73-75`); `ArtifactRepository.from_source` (reads committed `00-BOOK/DATA/artifacts.json`); the 14 read declarations via fail-closed loaders (`engine/infinite_scope/contract.py:60-90`).

**Model B — the defect, also implemented:**

```
Canonical Knowledge (Python tuples / in-code seeds)
    ↓  bootstrap() / extend() — writes to process memory, no persistence
Mutable Runtime State
    ↓
Validation
```

Occurrences: identity kind space (`identity.py:156,159` ← `bootstrap()` ← `SEED_FORMS`); `DEFAULT_VOCABULARIES` (`vocabulary.py:542` ← `extend()`); the certification chain (`registry.py:178-182` — order-defined, unverified on load); the closure population (env var + out-of-repo path + gitignored trees).

### 3.3 TA-01 — Two truth models coexist and neither is declared as governing

- **Finding.** The repository implements both the target chain and the defective chain. No declaration states which applies to which truth object, and no gate measures which one a given verdict travelled through.
- **Evidence.** Model A occurrences listed in §3.2, each with a loader and (for two) a committed artifact. Model B occurrences listed in §3.2, each measured: `M1/M2/M3/M6` for identity, `N1b/N6` for vocabularies, `N2` for certification, `M12` for closure. No `*-declaration.json` carries a field naming a truth object's reconstruction discipline. `grep 'process-independen'` across `engine/ platform/ .github/` → zero hits.
- **Current state.** Two models, undeclared, mixed within single capabilities (CEU has `from_document` **and** the `bootstrap()` path; UCKP has committed ledger schemas **and** the mutable singleton).
- **Desired state.** One declared model per truth object, with the reconstruction discipline named in the owning declaration.
- **Impact.** A reader cannot determine from any committed instrument whether a given verdict is reconstructible. The distinction is discoverable only by measurement, which is how both defects survived.
- **Dependency.** TA-05 (no committed artifact for the CEU document), TA-12 (no declared reconstruction contract).
- **Classification.** **PARTIALLY ASSIMILATED.**

### 3.4 TA-02 — The prose constitutional family cannot reach execution

- **Finding.** Twelve constitutional instruments have zero machine readers; a parallel family with the same identifier series is machine-readable and enforced.
- **Evidence.** `grep -rln "00-MASTER/CMG-0000" --include="*.py" --include="*.yml" --include="*.sh"` → zero. Each `00-MASTER/CMG-0000NN/` holds exactly one `.md` and no JSON sibling. By contrast `00-CMG/CMG-REGISTRY.json:1-12` declares itself a projection — `"authority": "NONE (DERIVED TRUTH) — this file asserts nothing. It is the machine-readable projection of CMG-000001 … Where this file and the canonical source disagree, the canonical source governs"` — and is read at `cmg_validate.py:36,85-101,603`, whose notes add: *"Zero hard coding: the validator contains no member of any enumeration below."*
- **Current state.** Governance stated in the prose family is unenforceable; the machine family is enforced and correctly subordinated.
- **Desired state.** Every instrument governing a validator is reachable by it, or explicitly advisory.
- **Impact.** This is the surface on which clause tokens cited from code have no located text — `AC-001`, `AC-009`, `XXXI.5` (TX-13).
- **Dependency.** None.
- **Classification.** **NOT YET ASSIMILATED.**

### 3.5 TA-03 — Truth-holding registries are Python source or process memory; only one reads a committed file

- **Finding.** Of twelve registries examined across two determinations, exactly one reads its population from a committed data file and exactly one writes one.
- **Evidence.** Reader: `ArtifactRepository.from_source` (`engine/registry/artifacts.py:47-51`) over `00-BOOK/DATA/artifacts.json`. Writer: `engine/nucleus/cli.py:185` (the identifier dictionary). Everything else: `NucleusRegistry` population from hardcoded tuples (`engine/nucleus/catalog.py:58,109,483`); `ExistenceRegistry` from `SEED_*` (`catalog.py:46-395`); `KnowledgeRegistry` self-declared *"The **canonical**, duplication-proof registry of all knowledge (UKIP Part 06)"* with `to_document` to stdout and **no** `from_document` (`N4`); `IdentityRegistry` whose `export()`/`from_dict()` are dead outside tests.
- **Current state.** The derived layer is rigorous; the canonical layer is ephemeral or compiled.
- **Desired state.** Anything that decides validity is reconstructible from a committed artifact.
- **Impact.** A structural blind spot follows: `engine/registry_coverage/matrix.py` judges *files* and self-declares *"authority": "NONE — DERIVED COVERAGE INTELLIGENCE"*, so a registry living only in process memory is **invisible to the instrument built to detect unregistered objects**.
- **Dependency.** TA-05.
- **Classification.** **PARTIALLY ASSIMILATED.**

### 3.6 TA-04 — Three declarations are written and never read

- **Finding.** `ceu-declaration.json`, `urr-declaration.json` and `ucxi-declaration.json` have no Python reader and no gate.
- **Evidence.** No `.py` mentions any of the three filenames; no `ceu-gate.yml`, `urr-gate.yml` or `ucxi-gate.yml` exists. Two of the three are the only declarations naming a `schema` (`ucos-ceu-declaration`, `ucos-ucxi-declaration`) — schemas nothing validates against. The other 14 are read and gated.
- **Current state.** The CEU declaration — the instrument that would govern the largest defect surface in this determination — binds nothing.
- **Desired state.** Read and gated, or declared advisory.
- **Impact.** CEU's declared ownership, invariants and openness statements have no enforcement path.
- **Dependency.** None.
- **Classification.** **PARTIALLY ASSIMILATED.**

### 3.7 TA-05 — Configuration can change a verdict four independent ways

- **Finding.** `pyproject.toml` and `repo-operations.json` are verdict-bearing configuration, and one of them pre-declares acceptance facts rather than measuring them.
- **Evidence.** `pyproject.toml`: `[tool.coverage.report] fail_under = 90` (`:345`) is a hard threshold; `[tool.coverage.run] source = [...]` (`:343`) **is** the coverage denominator; `[tool.pytest.ini_options] testpaths` (`:200`) decides what is collected at all, and the file records the measured consequence — *"the coverage-isolation regression added at be46a300 lived in `intelligence/tests/test_rie.py` and was therefore collected by NOTHING — not ./verify.sh, not CI, not the certification pipeline"*; `[project.optional-dependencies] dev` pins are read by `ucos_deps_ok` and a mismatch is an EEG refusal. `repo-operations.json` declares `{"stage_id": "coverage-report", "params": {"path": "coverage.xml", "min_percent": 90}}` **and** pre-declares `"implemented": true, "validated": true, "certified": true, "registered": true`, `"architecture_violations": []`, `"freeze_blockers": []`. `platform/tests/test_repository_operations_stages.py:171` records the failure mode: *"``repo-operations.json`` — configured with ``paths: []`` — was a guaranteed pass over ..."*. `UCOS_REPO_OPS_CONFIG` (`repo-ops.sh:25`) can swap the whole file.
- **Current state.** Part of the acceptance verdict is read from configuration, not measured.
- **Desired state.** Acceptance facts measured; configuration limited to thresholds and scope, with scope changes disclosed in the verdict.
- **Impact.** A verdict that reads its own success criteria from a swappable file is not a measurement of the system.
- **Dependency.** None.
- **Classification.** **NOT YET ASSIMILATED.**

### 3.8 TA-06 — Nine environment variables can change a verdict, and every gate subprocess inherits the whole environment

- **Finding.** The environment surface is small but nine variables are verdict-bearing, and ambient inheritance is unfiltered in production paths.
- **Evidence.** Verdict-bearing: `CLOSURE_SKIP_CORPUS` (`closure_engine.py:177`), `UCOS_VENV_DIR` (`discovery.py:371` — redirects the subject of EEG-01…06), `UCOS_PYTHON_SERIES` (`doctor.sh:56-60` reports `DRIFT`), `UCOS_PYTHON`, `UCOS_ALLOW_RECREATE` (the script records: *"a run that was supposed to DETECT toolchain drift would instead `rm -rf` the drifted venv, rebuild it and report green — the drift detected was the drift erased"*), `UCOS_ALLOW_PYTHON_MISMATCH`, `UCOS_REPO`, `UCOS_REPO_OPS_CONFIG`, `UKAP_CORPUS_ROOTS` / `UAKOS_EVIDENCE_ROOT`. Open-ended injection: `engine/foundation/config/config.py:255-257` maps **every** `UCOS_`-prefixed variable into config at highest precedence; `:98` is the `env://` scheme, `return os.environ[self.locator]`. Wholesale inheritance: `engine/verification_intelligence/execution.py:337,405`, `engine/determinism/reproduce.py:397`, `aee_engine.py:465`, `uccep_engine.py:633`, `rfp_engine.py:225` all pass `dict(os.environ)` to children. `COV_CORE*`/`COVERAGE*` are stripped only in determinism *tests*, never in gates. Pure toggles: `UVI_WORKERS` (fails loudly on a bad value), `UVI_PARALLEL`. Written-not-read: `PYTHONHASHSEED`, `TZ`, `LC_ALL`, `SOURCE_DATE_EPOCH` — set by `hermetic.py:211-221` *to remove* nondeterminism, inside a restoring context manager.
- **Current state.** Ambient state reaches verdicts through a documented and an undocumented channel.
- **Desired state.** Verdict-bearing variables declared and disclosed in the verdict; gate subprocesses given a filtered environment.
- **Impact.** The determinism layer that exists to eliminate ambient state (`hermetic.py`) is not applied to the gates.
- **Dependency.** TA-07.
- **Classification.** **PARTIALLY ASSIMILATED.**

### 3.9 TA-07 — There is no database; persistence is git objects plus JSON

- **Finding.** No datastore of system state exists anywhere.
- **Evidence.** `sqlite3` is imported at exactly one place, `engine/uckp/persistence.py:36`, used only by `DatabasePersistence` (`:288-320`) — one of **ten interchangeable adapters**, default `":memory:"`, whose purpose is stated as *":func:`verify_interchangeable` runs the identical contract against all of them and compares digests."* `psycopg`, `sqlalchemy`, `pymongo`, `redis` are never imported — they appear only as classification vocabulary strings. `DATABASE_URL`: zero occurrences. `.mypy_cache/*.db` are mypy's own incremental caches, read by nothing in the repository.
- **Current state.** Storage is git plus JSON files. This is a strength: it makes canonical knowledge diffable and replayable in principle.
- **Desired state.** Unchanged.
- **Impact.** Removes an entire class of hidden authority. Notable as the clearest architectural success in this inventory.
- **Dependency.** None.
- **Classification.** **ASSIMILATED.**

### 3.10 TA-08 — A gitignored artifact decides a PASS/FAIL, and the exclusion authority is itself a gate input

- **Finding.** Generated, untracked artifacts carry verdicts, and `.gitignore` is simultaneously the exclusion authority and an input to the gates that police exclusion.
- **Evidence.** `coverage.xml` is gitignored and is read by the `coverage-report` stage against `min_percent: 90`. `closure.json` is gitignored, untracked (`M12`), and is the declared `population_document` the single click reads. `knowledge/` is declared *"deterministically re-derivable output … a GENERATED ARTIFACT (GOV-005 §5.3)"* while `engine/uicm/matrix.py:13` names it the source of **capability identity** and `intelligence/kernel/substrate.py:42,51` registers it as a locator; `closure_engine.py:344-346` reads it as *"authoritative Repository Truth even though it is git-ignored"*. `.gitignore` documents its own defect verbatim: the withdrawn `* [2-9]` block *"manufactured cleanliness … adding these two lines removed 41 physically-present files from the gate's observation surface, flipping GATE-12 and GATE-04, opening `rib.json:gate`, satisfying AEE `OBS-BLUEPRINT-GATE` and clearing `CONV-02` — on a repository that still held every contaminating file. An exclusion rule must never be an input to the gate that polices the excluded state."* Twenty-four authored files under `00-MASTER/UAKOS-CLOSURE-002/` had to be re-admitted by name because *"the ignore rule hid AUTHORED Repository Truth that TRACKED declarations depend on"*, with the consequence recorded: *"A fresh clone could never resolve them, and `test_constitutional_convergence.py[urat]` failed with 'exclusion path does not resolve' on every clean checkout while passing locally off stale residue."*
- **Current state.** `RTBD-001` §7 holds that generated products are *"NOT part of Repository Truth"*; several verdicts nevertheless rest on them.
- **Desired state.** Verdicts computed over committed state; generated inputs declared and their absence a FAULT rather than a smaller measurement.
- **Impact.** Truth flowing from untracked residue is not reproducible from a fresh clone — the repository has measured this twice.
- **Dependency.** TA-06.
- **Classification.** **NOT YET ASSIMILATED.**

### 3.11 TA-09 — The two designed caches are the reference contract and should be preserved

- **Finding.** Both purpose-built caches declare themselves caches first, enumerate what they may skip, state their proxy's honest limit, and encode structural refusals. No other truth surface carries this discipline.
- **Evidence.** `engine/execution_environment/fingerprint.py:3-12`: *"It may skip exactly one measurement: EEG-06's scan of every pinned distribution's ``RECORD`` … It may never skip a verdict, never supply a check result, and never answer VALID on its own … EEG-01 through EEG-05 are recomputed on EVERY invocation regardless of cache state … they are the checks that catch a wrong interpreter — the one condition a cache must never be able to hide."* Its limit is stated (`:14-24`) and closed two ways (`ucos_env_cache_invalidate`; `--refresh`). `engine/verification_intelligence/evidence.py:1-36` opens *"A CACHE, and the docstring says so first because everything else follows from it … deleting the whole store changes no verdict"* and enforces three refusals: certification-eligible modes never reuse (`:257`, reasoned *"a certification that can be made to depend on the contents of a cache directory is not a certification"*), an unhashed input is never a hit (`:263-265`), an unresolvable command is never a hit (*"Unknown widens; it never narrows"*, `:261-262`).
- **Current state.** Two surfaces distinguish projection from authority and enforce it.
- **Desired state.** The same contract shape applied to `bootstrap()`, `register_kind` and `extend`.
- **Impact.** Establishes that no new concept is needed — the boundary is already articulated and honoured twice.
- **Dependency.** None.
- **Classification.** **ASSIMILATED** for these surfaces.

---

## 4. Canonical Knowledge Assessment

### 4.1 What canonical knowledge exists and reaches validation

| Surface | Reaches a validator? | Mechanism |
|---|---|---|
| 14 of 17 programme declarations | **YES** | fail-closed loaders; `--check-declaration` gates; replay-drift steps |
| `00-CMG/CMG-REGISTRY.json` | **YES** | `cmg_validate.py`, zero-hard-coding validator |
| 19 `00-BOOK/SCHEMAS/*.schema.json` | **YES** | registry source, verification intelligence, `ec1-ci.yml` |
| 2 ledger schemas | **YES — enforced on read** | `evolution.py:380-395` refuses on schema **and** `cycle_definition` mismatch; `ledger.py:73-75` |
| `00-SOURCE-MANIFEST/SOURCE-HASHES.txt` | **YES** | `test_frozen_paths.py` treats it as the immutability oracle |
| `engine/registry_coverage/declarations.json` | **YES** | `matrix.py:39,156` |
| `00-BOOK/DATA/artifacts.json` | **YES** | `ArtifactRepository.from_source` |
| Committed identifier dictionary | **YES** | `from_document` + four persistence tests; `M8` fresh-process `PASS` |
| 24 `SEED_*` constants | **YES, as Python source** | `bootstrap()` / import-time registration |
| 12 prose constitutions | **NO** | no reader (TA-02) |
| 3 declarations | **NO** | no reader (TA-04) |
| `mcs-state.schema.json`, `02-IMPLEMENTATION-MANIFEST.md` | **NO** | no reader |

### 4.2 TA-10 — The dominant pattern is correct and works

- **Finding.** The declaration-driven pattern — committed JSON declares, Python reads with a fail-closed loader, a gate replays — is real, widespread, and correctly reasoned.
- **Evidence.** `engine/infinite_scope/contract.py:60-90` is the reference: *"Fail closed: a declaration that cannot be read is not a declaration that permits everything"*, and it refuses to construct a contract whose law names a missing check **or** whose check no law claims (`:4-6`) — two-way totality. Two further independent implementations at `engine/uaue/resolution.py:251` and `engine/uckp/resolution.py:150`. Gate side: `.github/workflows/aee-gate.yml:13-16` — *"They are READ at run time from the declarations … this workflow never needs to change"*; `acee-gate.yml:142` fails on *"REPLAY DRIFT — committed registers are not the product of the declaration"*. Every committed artifact that could be mistaken for an authority carries an explicit derived-truth disclaimer naming its canonical source.
- **Current state.** 14 of 17 declarations, 19 of 20 schemas, 2 of 2 enforced ledger schemas.
- **Desired state.** Complete coverage.
- **Impact.** This is the architecture's strongest property, and it is why the defects are narrow rather than pervasive.
- **Dependency.** None.
- **Classification.** **ASSIMILATED** for the surfaces it covers.

### 4.3 TA-11 — The canonical vocabulary that governs existence is compiled, not declared

- **Finding.** The entire existence universe of every fresh process is built from tuples in a `.py` file, and the file itself declines the authority it holds.
- **Evidence.** `engine/ceu/catalog.py:18-21` verbatim: *"Nothing here is privileged. This file is one catalogue; a deployment may register a different one, register none, or supersede every row in it. The seeds are examples that happen to be useful, not a fixed vocabulary."* `bootstrap()` (`:396-473`) is the only non-test construction path. Measured (`M10`): deterministic — digest `b68559b7b416955d` across four hash seeds. `SEED_CLASSIFICATIONS` (`:198`) is what grants `own-capability`, so ownership truth reduces to a Python tuple. Same shape for the nucleus at `engine/nucleus/catalog.py:58,109,483`.
- **Current state.** Deterministic and committed — as source code. A file that disclaims being the authority is the only authority.
- **Desired state.** Declared vocabulary as committed data, with the Python seeds retained as one admissible catalogue.
- **Impact.** Two consequences: knowledge-only evolution is impossible on this axis (§10), and because the vocabulary reaches validators only by executing `bootstrap()`, it becomes process state at the point of use (TA-13).
- **Dependency.** TA-05 / TA-12.
- **Classification.** **PARTIALLY ASSIMILATED.**

### 4.4 TA-12 — No truth object declares its reconstruction contract

- **Finding.** No declaration names, for any truth object, whether it is reconstructible, from what artifact, and under what verification discipline.
- **Evidence.** The 17 declarations carry `forbidden_write_prefixes`, `closed_enumeration_disclosures`, `identity_planes`, `ledger_source`, `registry_source` — but no reconstruction or replay-discipline field. Measured (`N5`): the seven truth objects examined divide 2 reconstructible-and-proven, 1 reconstructible-but-re-minting, 4 with no loader — and nothing declares which. `GATE-PURITY-DETERMINATION` D-3.3 establishes the precedent that such a field *"belongs there, beside the scope it complements. No new registry, no new authority, no new schema family."*
- **Current state.** Reconstruction discipline is discoverable only by reading code.
- **Desired state.** A declared reconstruction contract per truth object inside the existing declaration surface.
- **Impact.** Without it, TA-01's two models remain indistinguishable from outside, and no gate can measure which one a verdict used.
- **Dependency.** Governance — the declaration surface belongs to each programme owner (§14).
- **Classification.** **NOT YET ASSIMILATED.**

---

## 5. Runtime Authority Assessment

### 5.1 The complete ambient-state surface

Eight module-level mutable containers exist in `engine/`. Classified:

| # | Container | file:line | Class |
|---|---|---|---|
| 1 | `_EXTENSION_KIND_CODES` | `engine/registry/universal/identity.py:156` | **ACCIDENTAL AUTHORITY** |
| 2 | `_EXTENSION_CODE_KINDS` | `engine/registry/universal/identity.py:159` | **ACCIDENTAL AUTHORITY** |
| 3 | `_STRATEGIES` (provider selection) | `engine/provider/selection.py:22` | PROJECTION — self-seeds at import (measured: 1 entry) |
| 4 | `_STRATEGIES` (composition ordering) | `engine/foundation/composition/ordering.py:55` | PROJECTION — self-seeds (measured: 2 entries) |
| 5 | `_PHASES` | `engine/factory/phases.py:70` | PROJECTION — self-seeds (measured: 8); **non-monotonic** (TA-17) |
| 6 | `_counters` | `engine/foundation/obs/telemetry.py:33` | OPTIMIZATION / observability |
| 7 | `_gauges` | `engine/foundation/obs/telemetry.py:34` | OPTIMIZATION / observability |
| 8 | `_histograms` | `engine/foundation/obs/telemetry.py:35` | OPTIMIZATION / observability |

Plus one module-level **object** that is the second authority:

| Container | file:line | Class |
|---|---|---|
| `DEFAULT_VOCABULARIES` | `engine/uckp/vocabulary.py:542` | **ACCIDENTAL AUTHORITY** |

And four outside `engine/`: `_SELECTOR_CACHE`, `_TRACKED_SET`, `_TRACKED_DIRS` (`00-MASTER/UCOS-RIB-001/rib_engine.py:287-289`, memoising the tracked-file set for the process lifetime), `REGISTRY` (`00-BOOK/tools/connectors/__init__.py:21`), `_DISCOVERED_VOLUMES` (`00-BOOK/tools/ukb.py:497`).

### 5.2 Runtime authority across the eight truth categories

| # | Category | Deciding function | Knowledge read | Prior call needed? | Class |
|---|---|---|---|---|---|
| 1 | **Validity** (identity) | `is_well_formed` `identity.py:303` → `parse_kind_name:286` | mutable globals `:156,159` | **YES** | **ACCIDENTAL AUTHORITY** |
| 1b | **Validity** (UCKP lawfulness) | `UCKO.require_lawful` `engine/uckp/ucko.py:384` bound at `registry.py:114,123,167` | mutable singleton `vocabulary.py:542` | **YES** | **ACCIDENTAL AUTHORITY** |
| 1c | **Validity** (EC-1, knowledge, context) | `enforce_acceptance` `gates.py:48`; `ContextValidator` `context/validation.py:433`; `KnowledgeValidator` `knowledge/validation.py:277` | the passed frozen subject + in-code constants | NO | **PROJECTION ONLY** |
| 2 | **Ownership** | `may_own_capability` `authority.py:95` → `roles_holding:66` `@cache` | private `bootstrap()` over `SEED_CLASSIFICATIONS` | no (self-populates) | **OPTIMIZATION ONLY** — but see TA-15 |
| 3 | **Identity** | as (1) | as (1) | **YES** | **ACCIDENTAL AUTHORITY** |
| 4 | **Capability existence** | `NucleusRegistry.register_capability:261`; lookup `capability():469` | per-instance `self._capabilities:97`, seeded from constants | yes — a registry must be built | **PROJECTION ONLY**, with a leak (TA-16) |
| 5 | **Relationship existence** | `RelationshipView._check_admissible` `existence.py:1041`; `_require_type:1024` | the passed registry only | yes — types must be registered | **PROJECTION ONLY**, with an ordering defect (TA-18) |
| 6 | **Lifecycle state** | `require_transition` `lifecycle.py:60`; `ClosureState.may_transition_to` `uicm/model.py:149`; `next_stage` `evolution.py:81` | frozen module tables (measured `N3`: plain dicts, no writer) | NO | **PROJECTION ONLY** |
| 6b | **Lifecycle state** (UCKP + control plane) | `UCKO.transition_to` `ucko.py:401`; `StateEngine.register_transition` `platform/universal_control_plane/state.py:79` | `Term.successors` in the mutable singleton; per-instance dict that **overwrites** prior bindings | **YES** | **ACCIDENTAL AUTHORITY** |
| 7 | **Certification** (verdict) | `CertificationEngine.certify` `engine/certification/engine.py:104` | the frozen `CertificationSubject` + a constant disclosure literal | NO | **PROJECTION ONLY** |
| 7b | **Certification** (chain) | `CertificationLedger.append:97`; `CertificationRegistry.register:200`, `__init__:178` | in-memory `_entries`; `entry_hash` binds `sequence` + `prev_hash` | yes — **append order is the hash** | **ACCIDENTAL AUTHORITY** |
| 8 | **Compliance** | `ComplianceEngine.evaluate` `compliance.py:222`; five frames `:73-152` | only the `UniversalCertificationSubject` | NO | **PROJECTION ONLY** |

### 5.3 TA-13 — Identity validity is produced by runtime bootstrap (carried, re-confirmed)

- **Finding.** For 43 of 72 admissible kinds, identity validity is a function of process execution history rather than of the identifier plus committed knowledge.
- **Evidence.** Measured `M1`/`M2`: fresh process 29 kinds, all extension probes `False`; after `bootstrap()` 72 kinds, all `True`. Same commit, same machine, zero file changes. `M6`: `IdentifierEntry` raises `RegistrationValidationError [REG-PLAT-VALID-400]` in one process and constructs in another. `M15`: `metadata.py:301-303` `identity_well_formed` is a live call, so constitutional legality inherits it. Nine non-test enforcement sites, including `engine/constitution/gateway.py:203` (the single authorised mutation path) and `engine/nucleus/ownership.py:211,215` (NUC-INV-09).
- **Current state.** 59.7% of the kind space is runtime-dependent; no persistence writer exists.
- **Desired state.** Validity a pure function of the identifier plus committed data.
- **Impact.** Both failure directions are wrong: `gateway.py:203` would refuse a legitimate mutation; `dictionary.py:221` would report legitimate identifiers as unparseable and flip a governance verdict.
- **Dependency.** TA-05 (no committed CEU artifact), TA-11.
- **Classification.** **NOT YET ASSIMILATED.**

### 5.4 TA-14 — A second process-global mutable authority exists, and it leaks across capabilities identically

- **Finding.** `DEFAULT_VOCABULARIES` is a module-level mutable singleton whose only extension mechanism writes to process memory, whose contents decide UCKO lawfulness and UCKP lifecycle transitions, and whose mutation changes the **nucleus** structural population.
- **Evidence.** Declaration `engine/uckp/vocabulary.py:542`. Mutator read verbatim: *"Admit a previously unknown term. This is the **only** extension mechanism."* with body `self._vocabularies[vocabulary_id] = extended`. Measured `N1b`: `require_term(KNOWLEDGE_KIND, 'probe-kind-xyz')` → `REFUSED (LawViolation UCKP-LAW-001)` before, `ACCEPTED` after. Binding `engine/uckp/registry.py:114` `self._vocabularies = vocabularies or DEFAULT_VOCABULARIES`, consumed at `:123` and `:167` `obj.require_lawful(self._vocabularies)`. Lifecycle path: `UCKO.transition_to` (`ucko.py:401`) resolves the transition table from the same singleton. **Cross-capability leak measured (`N6`):** `seed_layers()` 14 → 15 and `seed_subjects()` 83 → 84 after extending `ARCHITECTURE_LAYER`, via `engine/nucleus/catalog.py:473` `vocabulary = DEFAULT_VOCABULARIES.require(ARCHITECTURE_LAYER)`. Bounded by append-only semantics — `extended_with` refuses redefinition — so the drift is one-way widening, not re-meaning.
- **Current state.** Two independent ambient authorities with the same architecture; the second was previously unrecorded.
- **Desired state.** Vocabularies resolved from committed declarations; extension by declaration rather than by mutation.
- **Impact.** Establishes that the defect is a *repeated architectural pattern*, not a single site. Each was introduced to satisfy an openness obligation, and each purchased openness with process state. Both leak into a different capability than the one that owns them.
- **Dependency.** TA-12.
- **Classification.** **NOT YET ASSIMILATED.**

### 5.5 TA-15 — The ownership cache is a genuine cache and also a hidden bootstrap trigger

- **Finding.** `roles_holding` caches a pure function of committed seeds — so the ownership verdict is deterministic across processes — but the call inside it populates the identity globals as a side effect, which the cache then suppresses.
- **Evidence.** `engine/nucleus/authority.py:66-76` `@cache`, reasoned *"Cached because the seeded catalogue is deterministic; the cached value is immutable."* Measured `M10`: `may_own_capability('nucleus') = True` and `nucleus_digest = 46506f2287012463` identical across four hash seeds — deterministic. Measured `M9`: `CacheInfo(misses=1)` then `hits=1`; a role registered in a bootstrapped registry gives `holds('tenant','own-capability') = False`, because the authority answers from its **own private** `bootstrap()`. Measured `M3`: the same call raised `kind_names()` 29 → 72. `ownership_authority()` (`:57`) deliberately returns a fresh registry per call so no caller receives a shared mutable one.
- **Current state.** Correct as a cache; the side effect is undeclared and the cache makes it happen exactly once at an unpredictable point.
- **Desired state.** No capability's runtime behaviour alters another capability's verdict.
- **Impact.** Two distinct problems in one site. The *verdict* is sound. The *coupling* is what makes TA-13 intermittently invisible: exercising `engine.nucleus` happens to warm identity validity. And because the authority reads only its own catalogue, capability ownership is deterministic but **not runtime-extensible** — a registered role is invisible to it.
- **Dependency.** TA-13.
- **Classification.** **PARTIALLY ASSIMILATED.**

### 5.6 TA-16 — Certification chain state is order-defined and unverified on load

- **Finding.** The certification hash chain is a function of append order in one process; one implementation accepts a chain without verifying it, the other cannot be loaded at all.
- **Evidence.** Measured `N2`. `platform/universal_assurance/registry.py:178-182` sets `self._entries = list(entries)` with no verification; `require_intact()` runs only on write (`register`, `:235`), so a read-only consumer calling `get`/`by_subject`/`count_by_status` never validates the chain it was handed. `engine/certification/ledger.py:82` is `__init__(self) -> None` — no `entries` parameter, therefore no load path — and `:11-14` states *"It holds only in-memory records and **never writes to the certified corpus** (DP-03); persistence, if any, is the caller's concern via `to_dict`."* `append` (`:97-127`) derives `entry_hash` from `sequence = len(self._entries)` and `prev_hash = self.head_hash`. Meanwhile `00-BOOK/DATA/certification.json` is a committed `"verdict": "CERTIFIED"` document from a **different** producer carrying a `generated_at` wall clock.
- **Current state.** Certification state is process-local, append-order-defined, unverified at construction, and disconnected from the one committed certification artifact.
- **Desired state.** Chain verified on load, fail-closed, against a committed artifact.
- **Impact.** The certification *verdict* is pure (§5.2 row 7) and its *record* is not reconstructible. A chain that only verifies on write cannot detect a forged chain that is only read.
- **Dependency.** TA-12.
- **Classification.** **NOT YET ASSIMILATED.**

### 5.7 TA-17 — One runtime registry is non-monotonic

- **Finding.** `_PHASES` supports withdrawal, so a declared phase graph can shrink within a process.
- **Evidence.** Measured `M4b`: after `unregister_generation_phase("classify")` (`engine/factory/phases.py:103-108`), `generation_order()` raises `GenerationPhaseError [FAC-PHASE-001] generation phase requires a phase that is not declared (phase='resolve-factory', missing=['classify'])`. The module claims determinism at `:51` and `:66`. Self-seeding via `engine/factory/orchestrator.py:340-349` makes it benign in practice (measured: 8 phases at fresh import).
- **Current state.** Benign by convention, unsound by mechanism. No verdict currently compares advertised stages against a declaration.
- **Desired state.** Declared phase graph, or withdrawal removed, or the advertised set measured.
- **Impact.** Latent. It is the only *shrinking* mutable authority; the other two only widen.
- **Dependency.** None.
- **Classification.** **PARTIALLY ASSIMILATED.**

### 5.8 TA-18 — A relationship is registered before it is refused

- **Finding.** `relate()` registers the unit, then raises on the acyclicity check, leaving the refused edge in the registry.
- **Evidence.** Measured source, `engine/ceu/existence.py:989-1006`: `unit = self._registry.register(ExistenceUnit(...))` executes; then `if declared.attribute(ATTR_ACYCLIC): cycle = self.cycle_in(declared.key)` → `raise TopologyCycleError("this relationship type is acyclic and this edge closes a cycle", ...)`.
- **Current state.** A caller that catches the error sees a registry containing an edge the admission path claims to have refused; whole-registry gates will subsequently observe it.
- **Desired state.** Admission checks complete before the append.
- **Impact.** Relationship existence can disagree with relationship admissibility within one process. Because `ExistenceRegistry` is append-only by design, the spurious edge cannot be withdrawn.
- **Dependency.** None.
- **Classification.** **NOT YET ASSIMILATED.**

### 5.9 TA-19 — Nondeterminism discipline is correct; statefulness is unguarded

- **Finding.** Clock, RNG, network and salted hashing are absent from verdict paths and actively guarded. Process state is named nowhere as a nondeterminism source.
- **Evidence.** Injectable clock with a deterministic `SequenceClock` (`engine/registry/universal/audit.py:30,38-50`). `hermetic.py:211-221` pins `TZ=UTC`, `LC_ALL=C`, `PYTHONHASHSEED=0`, `SOURCE_DATE_EPOCH` and restores prior values. AST guards: `engine/tests/unit/test_temporal_contract.py:113-118` (*"A now()/utcnow() here would make every coordinate unreplayable"*), `test_closure009_requirement_engine.py:183`, `platform/tests/test_universal_project_state.py:672`; `engine/uicm/validation.py:57` `_FORBIDDEN_MINTS`. Measured `M10`: identical digests across four hash seeds. Against this, `engine/registry/universal/identity.py:14-15` names exactly three sources — *"no wall-clock, RNG, or network on the determined path"* — and mutable module state is an unnamed fourth.
- **Current state.** Three of four nondeterminism sources measured and guarded.
- **Desired state.** Process state named and guarded as the fourth.
- **Impact.** Explains why two independent ambient authorities drifted in undetected: they are invisible to every guard the repository built, because the guards test for forbidden *constructs*, not dependence on prior *calls*.
- **Dependency.** None.
- **Classification.** **PARTIALLY ASSIMILATED.**


---

## 6. Deterministic Reconstruction Assessment

Test as the directive specifies: **delete runtime memory → reload canonical sources → reconstruct → compare result.**

### 6.1 Results per truth object (measured, `N5`)

| Truth object | Committed artifact? | Loader | Verification on load | Round trip | Reconstruction |
|---|---|---|---|---|---|
| `IdentifierDictionary` | **YES** — `00-MASTER/UCOS-NUCLEUS-001/UCOS-NUCLEUS-IDENTIFIER-DICTIONARY.json` | `from_document` `:280` | re-mints every entry from its own tuple | **PASS**, `unparsed=0`, `parse_coverage=1.0` (fresh process, `M8`) | **SUPPORTED** |
| Evolution ledger | via `to_document`/`from_document` | `from_document` `:346` | **schema + `cycle_definition` enforced** `:380-395` | replay through `append()` per record | **SUPPORTED** |
| Object birth ledger | `00-MASTER/UOBC-000001/birth-ledger.json` | `load_ledger` | schema enforced `:73-75` | — | **SUPPORTED** |
| Artifact repository | **YES** — `00-BOOK/DATA/artifacts.json` | `from_source` `:47-51` | read-only resolver, path-escape refused | immutable after construction | **SUPPORTED** |
| CEU `ExistenceRegistry` | **NO** (`M7`) | `from_document` `:773` | unit digests + `verify_audit()`, fail-closed | digest **IDENTICAL** in a fresh process (`M5`) | **PARTIALLY SUPPORTED** — mechanism proven, artifact absent |
| `IdentityRegistry` | **NO** | `from_dict` `:539` | **re-mints rather than replays** | not a replay | **PARTIALLY SUPPORTED** |
| `NucleusRegistry` | **NO** | **NONE** (`N4`) | — | — | **UNSUPPORTED** |
| `KnowledgeRegistry` | **NO** | **NONE** (`N4`) | — | — | **UNSUPPORTED** |
| `CertificationLedger` | **NO** | **NONE** — `__init__(self)` | — | — | **UNSUPPORTED** |
| `CertificationRegistry` (assurance) | **NO** | constructor `entries` | **NONE on load** (`N2`) | — | **UNSUPPORTED** |
| UCP capability / ownership / dependency / agent registries | **NO** | **NONE** | — | — | **UNSUPPORTED** |
| Identity kind space | **NO** | **NONE** | — | — | **UNSUPPORTED** |
| `DEFAULT_VOCABULARIES` | **NO** | **NONE** | — | — | **UNSUPPORTED** |

**Aggregate: 4 SUPPORTED · 2 PARTIALLY SUPPORTED · 7 UNSUPPORTED.**

### 6.2 TA-20 — Deterministic reconstruction is PARTIALLY SUPPORTED, and the discipline is correctly articulated where it exists

- **Finding.** Four truth objects survive the delete-reload-reconstruct-compare test. Two have the mechanism but no committed artifact. Seven cannot be reconstructed at all.
- **Evidence.** §6.1, measured `N5`, `M5`, `M8`, `N2`, `N4`. The correct discipline is stated by the best implementation, `engine/ceu/existence.py:726-728`: *"The whole journal, not just its head. Steering 022: Repository Truth must be **sufficient** to reconstruct constitutional state"*, and `from_document` explicitly refuses the weaker alternative — *"Re-deriving would let the rebuilt registry differ from the recorded one and still look healthy."* The evolution ledger states the same principle from the read side: *"Loading is therefore a verification rather than a deserialization … An append-only history that cannot be loaded is an append-only history nobody can falsify."*
- **Current state.** The discipline is understood, articulated and implemented — on a minority of truth objects.
- **Desired state.** Every truth object that decides validity reconstructible and fail-closed on read.
- **Impact.** For the seven unsupported objects, a determination that measured them at one commit cannot re-verify them at the same commit except by re-running the same call sequence. That is the definition of a verdict that is not Repository Truth.
- **Dependency.** TA-12 (no declared reconstruction contract), TA-05.
- **Classification.** **PARTIALLY ASSIMILATED.**

### 6.3 TA-21 — Round-trip re-derivation is not replay, and one implementation confuses them

- **Finding.** `IdentityRegistry.from_dict` re-mints identities rather than loading them verbatim, which is the discipline `ExistenceRegistry.from_document` explicitly refuses.
- **Evidence.** `platform/foundation/durable_identity.py:539-563` calls `registry.mint(...)` / `adopt(...)` on load. Contrast `engine/ceu/existence.py:773` which replays verbatim and verifies each unit's `is_intact()`. Compounding this, `verify()` (`durable_identity.py:186-194`) returns `True` unconditionally when `adopted` is set — *"An adopted identity carries a frozen historical opaque that is preserved, not recomputed (AX-02), so it is trivially considered intact"* — and `from_dict` routes on that flag, so a record can declare its own trustworthiness.
- **Current state.** A load path that reconstructs by recomputation, plus a permanent verification waiver reachable from the record itself.
- **Desired state.** Verbatim replay with fail-closed verification; adoption carrying provenance and an attestation.
- **Impact.** A rebuilt identity registry can differ from the recorded one and still report healthy — the exact failure `ExistenceRegistry` was written to avoid.
- **Dependency.** TA-20.
- **Classification.** **PARTIALLY ASSIMILATED.**

---

## 7. Capability Truth Ownership Assessment

Test: for each truth facet, who owns it — as **declared** in a committed ownership instrument, and as **decided** in code?

### 7.1 The two ownership instruments and what they cover

`02-CANONICAL-OWNERSHIP-MATRIX.md` covers **artifact and document concepts** (platforms, baselines, decisions, identity-as-law) across ~52 rows plus seven addenda. `00-MASTER/UCOS-UCAF-001/ucaf-authority.json` covers **constitutional authority** — 14 capabilities, 17 scope rules, 17 competence resolutions, 3 reconciliations. Neither covers the **ontological facets** the engine decides at runtime.

Measured (`N8`): `realization_bindings: 1`. The single binding is `UCAF-RB-01` Execution Authority → `engine/runtime/execution/authorization.py`.

### 7.2 Per-facet ownership

| Facet | Declared owner | De facto decider | Match |
|---|---|---|---|
| **Identity — meaning** | AIF Part II / Part III A/G-AUTH: *"exactly one identity authority"* | four minters: `registry/universal/identity.py:257`, `kernel/identity.py:87`, `uckp/identity.py:73`, `uckp/ucko.py:174` | **NO — 4 grammars** |
| **Identity — validity** | ENG-001 D15; measured by UIS-001 (`AUTHORITY = NONE`) | `identity.py:39` `_NAMESPACE_RE`; `existence.py:121-127`; `is_intact:171-180` | **NO** |
| **Identity — namespace** | UMB-004 §2–§5 (*"zero hard-coding"*) | five hardcoded constants: `existence.py:81`, `identity.py:39`, `uckp/identity.py:44`, `object_birth/model.py:252`, `ceu/context_binding.py:28` | **NO — 5-way** |
| **Identity — representation** | **NO ROW** | `identity.py:32` `ID_PREFIX`, `:35` `_ID_DIGEST_LEN`; three more prefix/width constants | **UNOWNED** |
| **Entity — existence** | **NO ROW** | `ExistenceRegistry.register:291` → `_admit:333`; *"registration creates existence"*; restated as `nucleus/law.py:214-221` NL-09 | **UNOWNED — 2 sites** |
| **Entity — classification** | generic: *"Ontology / taxonomy"* → per-family `*-003`/`*-004` | `catalog.py:198-209` `SEED_CLASSIFICATIONS`; enforced `existence.py:308-325` | **NO** |
| **Entity — lifecycle** | Ω-E04 addendum crosswalks **six** owners | `existence.py:458` `supersede`, `:524` `resurrect` — **not one of the six** | **NO — a seventh lifecycle** |
| **Relationship — validity** | **NO ROW** | `RelationshipView.relate:951`, `_check_admissible:1041` | **UNOWNED** |
| **Relationship — types** | partial: `CMG-R-08` INHERITS-FROM | `catalog.py:147-193` — 17 types | **NO — 2 registers** |
| **Relationship — history** | generic: versioning · lineage | `existence.py:215-245` `AuditEntry` hash chain; `:578` `supersession_history` | **NO** |
| **Context — spatial** | **NO ROW** | `catalog.py:270-278` `SEED_SCALES` | **UNOWNED** |
| **Context — temporal** | **NO ROW** | `catalog.py:280-288` `SEED_TEMPORAL_MODELS` (7 models) | **UNOWNED** |
| **Context — reality** | **NO ROW** | `catalog.py:104-107` forms `reality`/`universe`/`civilization` | **UNOWNED** |
| **Context — observer** | **NO ROW** | `catalog.py:211-222` `SEED_OBSERVERS` (9) | **UNOWNED** |
| **Context — existence context** | **NO ROW** | `existence.py:653` `bind_context`; `ceu/context_binding.py:43,52,98,221` | **UNOWNED** |
| **Capability — existence** | PLATFORM-006/007/008; §5 `engine/knowledge/capability.py`, `intelligence/rie` | `nucleus/law.py:214-221` NL-09 + `existence.py:291`; RIE discovery | **PARTIAL — 3 registers** |
| **Capability — composition** | PLATFORM-010 + universal compiler | `law.py:159-172,207-213`; `authority.py:104` `may_select_units` ← faculty string in `catalog.py:203-207` | **NO** |
| **Capability — evolution** | CEP-009 (+ADDENDUM B); UEI-000001 §17 | `existence.py:458` `supersede` | **NO** |
| **Ownership — authority assignment** | `UCAF-R-08` → CEP-002, anchor *"registered in the Governance Registry"* | `authority.py:95-97` → `holds:87` → `roles_holding:66` → `existence.py:643` → `catalog.py:199` `ATTR_FACULTIES` | **NO** |
| **Ownership — ownership truth** | §2 of the matrix itself | `engine/knowledge/integration/reuse.py` `ReuseEngine` returns ranked candidates and **refuses to assert a single owner** | **NO** |
| **Security — trust** | **NO ROW** | `catalog.py:96` form `trust`; relationship type `trusts` with an **empty** attribute dict | **UNOWNED** |
| **Security — integrity** | **NO ROW** (nearest `CMG-INV-11`) | `existence.py:171-180` `is_intact`; `AuditEntry.expected_hash:215-245`; `uckp.canonical.content_hash` | **UNOWNED** |
| **Security — admission safety** | CMG-000001 LXXVI–LXXVII via CEP-009 ADDENDUM B (constitutional constructs) | `existence.py:291-331` `register` (runtime units); `authority.py:87-92` *"Fails closed"*; `law.py:88-106` *"or fail closed (never default)"* | **NO — two different senses of "admission"** |
| **Lifecycle — stages** | UCIC-001: fifteen mandatory stages | UCL-000001 discovers **45** (`AUTHORITY = NONE`); `existence.py:232-238` action vocabulary | **PARTIAL — 15 declared vs 45 discovered** |
| **Lifecycle — transitions** | **NO ROW** | four module tables (`N3`); `engine/uckp/state.py` delta registers | **UNOWNED** |
| **Lifecycle — evolution rules** | CEP-009 ADDENDUM B: 15 stages + 16 acceptance properties | `existence.py:458` `supersede` (*"One call covers every construct"*); `law.py:222-230` NL-10 | **NO** |
| **Certification — truth** | CEP-005 + CERTIFICATION-REGISTRY | `engine/certification/engine.py:104` `certify`; chain per TA-16 | **UNRESOLVED** — `UCAF-RC-01` records the ratification claim as `RECONCILIATION-REQUIRED` |
| **Certification — evidence acceptance** | CEP-008; `UCAF-CAP-08` | `catalog.py:83` form `evidence`; `:265-272` `SEED_EPISTEMIC_STATES` (unknown, unobserved, unmeasured, unverified, contradicted, impossible) | **NO** |
| **Measurement — metrics** | fragment only: `platform/measurement` inside the architectural-intelligence row, scoped to *"gaps"* | `catalog.py:84-86,291-353` forms + quantities + measurement systems + units + conversions; governing decision `ADR-0005` | **NO** |
| **Measurement — evaluation truth** | **NO ROW** | ~40 `00-MASTER/<PROGRAMME>/*_engine.py`, **every one** stamped `AUTHORITY = NONE — DERIVED TRUTH` | **UNOWNED BY CONSTRUCTION** |

### 7.3 TA-22 — Twelve truth facets have no declared owner

- **Finding.** Twelve facets that the engine decides at runtime have no row in the ownership matrix and no competence resolution in UCAF. They are owned, in practice, by whatever code happens to decide them.
- **Evidence.** The twelve: identity representation · existence · relationship validity · context spatial · context temporal · context reality · context observer · context existence-context · trust · integrity · lifecycle transitions · evaluation truth. Seven more are declared only generically (entity classification, entity lifecycle, relationship types, relationship history, metrics, evidence acceptance, admission safety). Only `UCAF-R-08` (*"Which authority allocates canonical ownership of a concern?"*) and `UCAF-R-10` (*"Which authority resolves a contested authority over the same artifact?"*) touch any facet, and both answer at the meta level. The matrix records the precedent for this gap in its own Ω-E03 addendum: *"`02-CANONICAL-OWNERSHIP-MATRIX.md` contained **zero occurrences of the word identity** — seven authorities, no rows."* Six identity rows were added by that wave; no equivalent wave has been run for entity, relationship, context, security or measurement.
- **Current state.** The matrix asserts `orphan_concepts = 0` for 431 concepts in §3. That measures concepts the matrix enumerates, not facets the code decides.
- **Desired state.** Every facet a validator decides has a declared owner.
- **Impact.** This is the deepest finding in this determination. Runtime authority is not merely an implementation defect — for twelve facets there is *no declared authority for runtime to usurp*. The question "does runtime become an accidental authority?" cannot be answered for them, because no other authority is declared.
- **Dependency.** **Governance — blocked.** Adding a row requires a `CMG-000001` Art LXXVII disposition of `CREATE`, recorded as unavailable (§14).
- **Classification.** **NOT YET ASSIMILATED.**

### 7.4 TA-23 — The deciding modules exercise no located authority

- **Finding.** By the authority register's own accounting, the modules that decide existence, classification, identity, relationship validity, context, capability composition and ownership are bound to no authority.
- **Evidence.** Measured `N8`: `realization_bindings: 1` against `capabilities: 14`. The one binding is Execution Authority → `engine/runtime/execution/authorization.py`. `engine/ceu/*`, `engine/nucleus/*`, `engine/registry/universal/identity.py` and `engine/uckp/*` appear in `ucaf-authority.json` only under `realization_token_classes` — i.e. they were detected minting `*AUTHORITY`-shaped symbols and had to be classified as *not* authorities.
- **Current state.** The authority model is complete for constitutional authority and empty for ontological authority.
- **Desired state.** Every decider bound to a located authority, or explicitly declared as a projection of one.
- **Impact.** Compounds TA-22: the facets have no declared owner **and** their deciders have no declared authority. `engine/nucleus/law.py:9-19` is candid about the consequence — *"A repository-wide search returned no **negative** clause … Both absences are enforceable gaps … This module supplies exactly those missing clauses and nothing else."* A Python module authoring the constitutional clauses it then enforces is the terminal form of code becoming the authority.
- **Dependency.** Governance (§14) — UCAF extension is Option A, recommended, `IMPLEMENTATION-NOT-AUTHORIZED`.
- **Classification.** **NOT YET ASSIMILATED.**

### 7.5 TA-24 — Capability ownership was contested, was diagnosed, and is now half-closed

- **Finding.** The single-authority breach in capability ownership was found in-repo and corrected in one direction; the legislating clause that contradicts the correction still executes.
- **Evidence.** `engine/nucleus/authority.py:9-22` verbatim: *"Ownership was decided by `StructuralRole.may_own_capability`, whose whole body was `return self is StructuralRole.NUCLEUS`. That made the **source code** the ownership authority … Meanwhile `engine.ceu` already held the same fact properly … **Two authorities over one question, which the Single Authority Principle forbids.** This module removes the second one."* Derivation direction asserted and testable (`:31-37`); `law.py:53-70` demotes `StructuralRole` to *"a **projection** of the CEU classifications … no longer an authority"*. **But** `law.py:41-45` `SUPREMACY_CLAUSE` still legislates *"Capabilities are owned by Nuclei and by nothing else … or the repository is in violation"*, which contradicts the faculty-derived model: `law.py` says ownership cannot be regranted by registration; `authority.py`/`catalog.py:196-197` say it is whatever `ATTR_FACULTIES` grants. Residual defect recorded by the code itself: the enum is closed at 3 members while CEU registers 10 classifications, so *"a fourth classification … cannot yet be carried by a legacy `SubjectRecord`."*
- **Current state.** One authority removed; two answers to "can ownership be regranted by registration?" still execute.
- **Desired state.** One answer.
- **Impact.** Demonstrates the repository can diagnose and close this defect class from inside — the most encouraging evidence in this determination — and that closure was partial.
- **Dependency.** TA-22.
- **Classification.** **PARTIALLY ASSIMILATED.**

---

## 8. Runtime Independence Assessment

Test: is a truth value independent of runtime initialization history?

### 8.1 What is independent and what is not

| Axis of variation | Result | Evidence |
|---|---|---|
| `PYTHONHASHSEED` (0, 1, 42, 12345) | **INDEPENDENT** | `M10` — all digests identical |
| Import order | **INDEPENDENT** | `M11` — 72/43 both orders |
| Repeated initialization | **INDEPENDENT** | `M11b` — `digest_a == digest_b` |
| Wall clock / RNG / network | **INDEPENDENT** | `TA-19` — absent from verdict paths, AST-guarded |
| Database state | **INDEPENDENT** | `TA-07` — no database exists |
| **Call history — did `bootstrap()` run?** | **DEPENDENT** | `M1`/`M2`/`M6` |
| **Call history — did a *different capability* get asked?** | **DEPENDENT** | `M3` — ownership question flips identity |
| **Call history — did `extend()` run?** | **DEPENDENT** | `N1b` — lawfulness `REFUSED` → `ACCEPTED` |
| **Call history — cross-capability vocabulary mutation** | **DEPENDENT** | `N6` — nucleus population 83 → 84 |
| **Append order** (certification chain) | **DEPENDENT** | `N2` — `entry_hash` binds `sequence` |
| **Environment** (9 variables) | **DEPENDENT** | `TA-06` |
| **Generated-artifact presence** | **DEPENDENT** | `TA-08`, `M12` |

### 8.2 TA-25 — Runtime independence holds on every classical axis and fails on call history

- **Finding.** The system is robust against every nondeterminism axis the industry normally worries about, and fragile against exactly one it does not: the order and identity of prior calls.
- **Evidence.** §8.1. Six axes independent, six dependent — and all six dependent axes reduce to *what happened earlier in this process or environment*, not to *what is committed*.
- **Current state.** Runtime independence is real for the axes that are measured and absent for the axis that is not.
- **Desired state.** Truth value independent of call history.
- **Impact.** A verdict is reproducible by re-running the same sequence and not reproducible by reading the repository. Those are different properties, and only the first is currently demonstrated.
- **Dependency.** TA-13, TA-14, TA-16.
- **Classification.** **PARTIALLY ASSIMILATED.**

### 8.3 TA-26 — The two cross-process gates prove reproducibility of one path, not initialization independence

This is the distinction the directive requires stated explicitly.

- **Finding.** Two of twenty-nine gates compare verdicts across separate operating-system processes. Both hold the initialization history constant between the two runs. Therefore neither can detect runtime-state-dependent truth.
- **Evidence.**
  - **UAUE gate**, `.github/workflows/uaue-gate.yml:188-199`, reasoning stated verbatim in the workflow: *"Two independent processes, not two calls in one process. An in-process replay could pass on a memoised result; a cross-process replay cannot, which is the only form of the claim that is worth making about an artifact meant to survive the process that wrote it."* The step:
    ```
    python3 -m engine.uaue.gate --quiet --json > /tmp/uaue-run-a.json
    python3 -m engine.uaue.gate --quiet --json > /tmp/uaue-run-b.json
    diff -q /tmp/uaue-run-a.json /tmp/uaue-run-b.json
    ```
  - **UISD gate**, `.github/workflows/uisd-gate.yml:231-241`, same shape plus a working-tree comparison: *"UISD-000001: two processes, one report, zero surfaces moved."*
  - **What they prove:**
    ```
    same process path + same invocation sequence  =  same result
    ```
  - **What they do NOT prove:**
    ```
    different runtime initialization history + different bootstrap states  =  same truth value
    ```
  - **Why.** Run A and run B invoke the **same entry point** with the **same arguments**. Both therefore execute the **same call sequence** and reach the **same initialization state**, inheriting identical module globals and an identically-populated `DEFAULT_VOCABULARIES`. A verdict that depends on whether `bootstrap()` or `extend()` ran is **equally wrong in both runs**, and the `diff` passes.
  - **Everything else measures less.** Nine `--check-determinism` self-guards (`aee`, `baseline`, `mcos`, `rib`, `rfp`, `uaep`, `uaie`, `uar`, `acee`) compare two renders **inside one process**. `determinism.yml:48-50` invokes `engine.determinism.reproduce`, whose `double_build` (`reproduce.py:283-320`, measured `M19`) runs both builds **in one interpreter sharing one `env`, one `document`, one `adapter`, one `signer`**; isolation is `with env.apply():` plus a distinct output directory. `grep -rn 'process-independen'` across `engine/ platform/ .github/` → **zero hits**.
- **Current state.** Cross-process comparison exists on 2 of 29 surfaces. Initialization independence is measured nowhere. No test observes the pre-bootstrap state: `grep autouse=True` across all 15 `engine/tests/**/conftest.py` → zero results, so the extension space at test time is an undeclared baseline, and `engine/tests/nucleus/test_identity_convergence.py:127-138` asserts an invariant whose own docstring concedes it holds *"today only because no kind is registered under the code `EVO`"*.
- **Desired state.** A measurement analogous to `double_build` at the **process boundary and across differing call orders** — invoke a validator in two fresh interpreters, one with and one without the initialization call, and require verdict equality.
- **Impact.** The correct instrument exists and is correctly reasoned about in a code comment; what it does not do is vary the one dimension that matters. This is why two independent ambient authorities survived 29 gates and a 10 000-test suite. It is also why `GATE-PURITY-DETERMINATION`'s remediation would not close this: that determination audits **write** purity (D-3.0 — *"it lacks a declared mode"*) and all five D-3.5 acceptance criteria concern writes.
- **Dependency.** None. The UAUE step is the pattern to extend; the missing element is varying initialization between runs.
- **Classification.** **PARTIALLY ASSIMILATED.**

---

## 9. Single Click Assimilation Alignment

Target chain: `Any Input → Knowledge Assimilation → Truth Resolution → Identity → Context → Ownership → Security → Impact → Validation → Execution → Evolution`.

Test: does every stage have a truth owner?

### 9.1 Per-stage alignment

| Stage | Executable? | Truth owner (declared) | Truth owner (de facto) | Canonical-knowledge sufficient? |
|---|---|---|---|---|
| **Any Input** | **YES** — `platform/universal_assimilation/pipeline.py:159` `assimilate_source` | none located | the caller (payload passed as bytes) | **YES** — *"The framework never scans a filesystem, opens a network connection, or rediscovers a repository as a side effect of assimilating one of its files"* (`:53-58`) |
| **Knowledge Assimilation** | **YES, 4 steps not 9** — Admit → Classify → Normalise → Home | none — the fabric is unowned | `pipeline.py` | **YES for the pipeline** — but **not invoked by the single click** |
| **Truth Resolution** | partial | `UCAF-R-08`/`R-10` at meta level only | `closure_engine.py` + `ReuseEngine` (which refuses to assert an owner) | **NO** — reads a gitignored, untracked population document |
| **Identity** | YES | AIF Part II — *"exactly one identity authority"* | four minters (TA-22) | **NO** for 43 of 72 kinds; **not on the assimilation path** |
| **Context** | no stage | **NO OWNER — all 5 axes unowned** | `SEED_*` tuples | **NO — stage absent** |
| **Ownership** | YES — `service.py:251-253` | `UCAF-R-08` → CEP-002 Governance Registry | `authority.py:95` ← a Python faculty tuple | **NO** — input population is generated |
| **Security** | **NO CODE ON THE PATH** | **NO OWNER** | none | **ABSENT, not deferred** |
| **Impact** | code exists — `engine/graph/architecture/impact.py` | none located | imported only within its own package | **NOT WIRED** |
| **Validation** | YES — `PolicyMeasurementEngine.measure` `service.py:264-266` | ENG-001 D15 (identity validation only) | the measure step, pure over its context | **YES for the step**; inherits its inputs' provenance |
| **Execution** | YES | **`UCAF-RB-01` Execution Authority — the ONE bound authority** | `engine/runtime/execution/authorization.py:61` | **NO** — `subject: str = "engineering"` default; no policy source |
| **Evolution** | code exists — `engine/uckp/evolution.py`, ledger schema enforced on read | CEP-009 (+ADDENDUM B) — one of **seven** lifecycles | `existence.py:458` `supersede` | **PARTIALLY** — not wired to assimilation |

### 9.2 TA-27 — Four of eleven stages have no truth owner, and the one fully-owned stage has no knowledge source

- **Finding.** Context (all five axes), Security, Impact and Truth Resolution have no declared truth owner. Execution is the only stage with a bound authority, and it reads no policy.
- **Evidence.** Ownership gaps per §7.2. Security: `grep -rniE 'trust|authenticat|authoriz|security|signature' platform/universal_assimilation/*.py` → **zero matches**; `14-SECURITY/` is prose only; `require_trusted` has exactly one non-test caller outside its own module (`platform/foundation/admission.py:398`, authority migration). Execution: `UCAF-RB-01` binds `engine/runtime/execution/authorization.py`, whose entry point is `def authorize(composition, *, subject: str = "engineering") -> Authorization:` (`:61`) — no permission table, no role registry, no policy file. Single click: `platform/universal_foundation/cli.py:63-66` passes only `subjects` and `locators`, never `sources`, so `determine` (`service.py:268-301`) sets `report = None` and the assimilation report is **not measured**.
- **Current state.** The published single click composes truth-classification, ownership and measurement over a generated population, and skips assimilation, identity, context, security, impact and evolution.
- **Desired state.** Every stage owned, wired, and operating from committed knowledge.
- **Impact.** "Single-click assimilation" is currently a documentary composition model, not an executable chain. The one pure component (`pipeline.py`) is unexercised; the one component that runs habitually (`closure_engine.py`) is the least anchored to committed knowledge.
- **Dependency.** TA-22, TA-23, and governance (§14).
- **Classification.** **NOT YET ASSIMILATED.**

---

## 10. Infinite Expansion Assessment

Test: can future entities, realities, dimensions, temporal models, technologies, software languages and AI systems be introduced through knowledge expansion **without making runtime code the authority**?

### 10.1 Axis assessment

| Axis | Admissible without a code edit? | Durable in a fresh process? |
|---|---|---|
| New entity kinds | **YES** — `register_kind` admits any well-formed `(name, code)` | **NO** — valid only in the admitting process (`M1`/`M2`) |
| New entity forms | **YES** in-process — `declare_form` | **NO** — no filesystem write anywhere in `engine/ceu/` |
| New knowledge kinds / relations / classes | **YES** in-process — `DEFAULT_VOCABULARIES.extend` | **NO** — measured `N1b` |
| New realities / universes / civilizations | **YES** — these are **core** kinds | YES for the kind |
| New dimensions | **NO** — `ContextKind` (16) requires an enum edit; `coerce` raises with `allowed=[...]` | **NO** |
| New temporal models | **NO** — `SEED_TEMPORAL_MODELS` (7) is a Python tuple; `EvolutionStage` (15) an enum | **NO** |
| New technologies | **NO** — `SUPPORTED_FORMS` (5), `SUPPORTED_OPS` (6), with the honest comment *"Declared here because they are **code paths**, not declarations: adding a form means writing a reader for it"* | **NO** |
| New value representations | **NO** — `VALUE_TYPES = ("string","number","boolean","list","mapping")`, `:74` raises | **NO** |
| New software languages | **NO** — no language axis exists as data | — |
| New AI systems | **YES as an observer** — `SEED_OBSERVERS` includes `ai`, `collective-intelligence`, `unknown` | in-process only |
| New storage kinds | **YES — best-behaved** — 10 adapters plus a `FUTURE_STORAGE` sentinel, advisory not refusing; `verify_interchangeable()` compares `universe_digest()` across all ten | YES |
| New facets (questions about existence) | **NO by design** — 33 closed; a 34th is a constitutional amendment | n/a |

### 10.2 TA-28 — 230 closed enumerations are undisclosed and the governing law cannot detect them

- **Finding.** The declared prohibited condition is *undisclosed closure*. It is present at least 230 times, and `ISD-L-01` cannot detect one instance.
- **Evidence.** Measured `M13`/`M16`: **238** closed `Enum` subclasses across the six roots; `00-MASTER/UISD-000001/uisd-declaration.json` declares **11** `closed_enumeration_disclosures`, of which only **6 distinct names** are Python enums in those roots (`ClosureState`, `Facet`, `KnowledgeCapability`, `RegistryKind`, `RelationType`, `RelationshipKind`) = 8 occurrences → **230 undisclosed**. Undisclosed include every enum relevant to this determination: `ContextKind` (`taxonomy.py:42`), `ContextLifecycle` (`:153`), `EvolutionStage` (`evolution.py:44`), `KnowledgeKind` (`model.py:40`), `Lifecycle` (`:108`), `CertificationClass`, `ComplianceStatus`, `MeasurementComparator`. `ISD-L-01` (`engine/infinite_scope/contract.py:170-201`) iterates **only** the 11 declared entries and asserts four string/path properties per entry; it performs no AST scan for `Enum` subclasses, never counts a disclosed `population` against the actual enum, and cannot distinguish a data-admission path from a source edit — `"Registration under UCKP-ART-17: add the member"` passes identically to a real one. The declaration pre-empts the objection at `$disclosure_completeness`: *"ISD-L-01 measures that each entry names a closing invariant and an admission path, **not that the list is exhaustive** — a claim of exhaustiveness would be the very finite assumption the principle prohibits."*
- **Current state.** Disclosure discipline enforced over ~4.6% of the closed sets.
- **Desired state.** The register populated by discovery, or the law scoped to what it can measure with the residue recorded.
- **Impact.** *"No enumeration is closed silently"* is asserted and is false 230 times. The two genuinely falsifiable laws are L-06 (performs an extension in memory and proves the original vocabulary did not mutate) and L-11 (appends to a **deep copy** and re-runs declared consumers, reconciling refusals both ways) — and L-11 writes nothing, so it proves a document *could* be appended to, never that a committed document is read by a fresh validator.
- **Dependency.** None — independently closable by measurement.
- **Classification.** **PARTIALLY ASSIMILATED.**

### 10.3 TA-29 — Expansion by knowledge is disproved; both extension mechanisms make runtime the authority

- **Finding.** Every located extension mechanism admits new knowledge **into a process** and none makes it durable. Both are documented as *"the only extension mechanism"*, and both write only to process memory.
- **Evidence.**

  | Requirement | Status |
  |---|---|
  | A substrate that does not branch on form | **MET** — `engine/ceu/existence.py`, one `ExistenceUnit`, self-describing root; *"No function in this module branches on a particular form, classification, topology or relationship type"* |
  | An in-process admission call | **MET** — `declare_form:357`, `register_kind:162`, `DEFAULT_VOCABULARIES.extend:161`, `ContextTaxonomy.extend:516` |
  | A reader that rehydrates from a document | **MET and MEASURED WORKING** — `from_document:773` (`M5`) |
  | A **committed document** for that reader | **ABSENT** (`M7`) |
  | A **production loader** wiring committed data → registry | **ABSENT** — `from_document`'s only caller is `reconstruct()`, fed an in-memory round trip |
  | Cross-process persistence of registered kinds | **ABSENT** (`identity.py:156-159`) |
  | Cross-process persistence of vocabulary terms | **ABSENT** (`vocabulary.py:542`, `N1b`) |
  | Equivalent for the nucleus population | **ABSENT** — `declarations_from_mapping` (`nucleus/registry.py:607`), documented as *"the path by which an unlimited number of future nuclei, layers and compositions enter with no code change at all"*, has exactly one caller: a test |

  The openness tests prove less than they appear to: `test_a_future_form_needs_no_code_change` hashes engine source before and after an in-process admission and asserts byte-identity. True — and not the same claim as *the admission survives the process*.
- **Current state.** Knowledge evolution can add **units and terms** to a running process. Only code mutation can add **kinds, forms, dimensions or temporal models** to a fresh one.
- **Desired state.** Admission by committed declaration, honoured deterministically by a fresh validator.
- **Impact.** Answers the directive's question directly: **future unknowns cannot currently evolve through knowledge expansion without making runtime code the authority** — because the two mechanisms that implement openness *are* runtime authorities. Openness and determinism are implemented as a trade, twice.
- **Dependency.** TA-05, TA-12.
- **Classification.** **NOT YET ASSIMILATED.**


---

## 11. Contradiction Register

Live, located, mutually inconsistent claims bearing on truth authority and runtime independence. **None resolved here.**

| # | Claim A | Claim B | Basis | Location |
|---|---|---|---|---|
| **TX-01** | `identity.py:286-291`: *"This is the total parser: it resolves every identifier this authority can mint, which is what makes 'parse covers 100% of minted identifiers' measurable"* | Totality holds only inside the process that registered. Measured `False` vs `True` for one string | code vs its own docstring | `identity.py:156,159` vs `:286-301`; `M1`/`M2` |
| **TX-02** | `identity.py:5-8`: the id resolves identically *"regardless of version, wall-clock, machine, or **registration order**"* | `resolve_kind_code`/`parse_kind_name` read runtime-mutated globals; extension-kind minting fails before registration | docstring vs code | `identity.py:5-8` vs `:206-213,288-301` |
| **TX-03** | `identity.py:14-15`: *"no wall-clock, RNG, or network on the determined path (RC-4 determinism)"* | Correct and incomplete — mutable module state is an unnamed fourth source, and there are now **two** of them | declaration vs implementation | `identity.py:14-15` vs `:156-159`, `vocabulary.py:542` |
| **TX-04** | `dictionary.py:220`: *"Identifiers the one grammar cannot parse. **Must always be empty.**"* | Non-empty in any process that has not bootstrapped CEU; wired to `"status": "PASS"/"FAIL"` at `:257` | unconditional claim vs runtime | `dictionary.py:219-221,257`; `M6` |
| **TX-05** | `vocabulary.py` `extend`: *"Admit a previously unknown term. This is the **only** extension mechanism."* | The admission is not persisted anywhere, so a term admitted in one process is unknown in the next | intent vs effect | `vocabulary.py:161-166,542`; `N1b` |
| **TX-06** | `engine/uckp/ucko.py:384-388` `require_lawful`: *"Openness is register-then-use (Article 17): an unknown kind, tier, stage, relation or class is admitted by registration and refused until it is"* | Registration widens lawfulness process-globally and durably nowhere; `require_term` `REFUSED` → `ACCEPTED` measured | law vs durability | `N1b` |
| **TX-07** | `engine/nucleus/catalog.py:473` intent: *"A layer added to the vocabulary appears here with no edit"* | Measured: `seed_layers()` 14 → 15 and `seed_subjects()` 83 → 84 — the **nucleus** population is mutated by a **UCKP** vocabulary call | designed openness vs cross-capability authority | `N6` |
| **TX-08** | `engine/ceu/catalog.py:18-21`: *"Nothing here is privileged. This file is one catalogue … The seeds are examples that happen to be useful, not a fixed vocabulary."* | It is the only catalogue any fresh process ever loads; `bootstrap()` is the sole non-test construction path | disclaimer vs sole authority | `catalog.py:18-21,396-473`, `:404` |
| **TX-09** | `existence.py:903-905`: *"The authority owns the name→code mapping; **this function never stores one.**"* | The authority stores it only in RAM, so nobody stores it durably | intent vs effect | `existence.py:898-910` vs `M7` |
| **TX-10** | `existence.py:726-728`: *"Repository Truth must be **sufficient** to reconstruct constitutional state"* | The sufficient document is never written. `from_document` works (`M5`) and has no production caller | principle vs practice | `existence.py:733,773` vs `M7` |
| **TX-11** | `engine/certification/ledger.py:129-152` `verify()` / `require_intact()` recompute the whole chain | There is no load path (`__init__(self)`), so nothing can be verified on load; and `platform/universal_assurance/registry.py:178-182` accepts entries **without** verifying | check vs reachability | `N2` |
| **TX-12** | `02-CANONICAL-OWNERSHIP-MATRIX.md` §3: `orphan_concepts = 0` for all 431 concepts; header *"Repository Truth is **ABSOLUTE**. Single Canonical Ownership"* | Twelve truth facets the engine decides have **no row**; §5 concedes the matrix *"was authored by a human and is unreadable by machine"* | assertion vs measured facets | §7.2; matrix §3, §5 |
| **TX-13** | `00-CMG/CMG-000001` **XII.5**: *"A LATENT artifact … SHALL NOT be cited as constitutional authority … **Latency IS a detectable defect, not a status.**"* | The clause tokens most load-bearing for openness have **zero located occurrences** in any `.md` or `.json`: `AC-001`, `AC-009`, `AC-003`, `AC-011`, `AC-012`, `XXXI.5`. They are cited only from Python comments | constitution vs citation practice | `identity.py:66,130,153`; `nucleus/law.py:179,224,232` |
| **TX-14** | `engine/nucleus/law.py:41-45` `SUPREMACY_CLAUSE`: *"Capabilities are owned by Nuclei and by nothing else … or the repository is in violation"* | `authority.py`/`catalog.py:196-197`: ownership is whatever `ATTR_FACULTIES` grants, and *"neither is privileged by anything except what this data says"*. Two answers to "can ownership be regranted by registration?" — both execute | code vs code | `law.py:41-45` vs `authority.py:95-97`, `catalog.py:196-207` |
| **TX-15** | `engine/nucleus/law.py:9-19` admits: *"A repository-wide search returned no **negative** clause … Both absences are enforceable gaps … **This module supplies exactly those missing clauses and nothing else.**"* | `00-CMG/CMG-000001` XII.6: *"Derived truth SHALL always be reconciled against repository reality and SHALL never be treated as a source of authority"*; UCAF binds this module to no authority (`N8`) | code legislating vs constitution | `law.py:9-19,137-230` vs `N8` |
| **TX-16** | UCAF declares 14 capabilities including realization, tier governance and admission | `realization_bindings: 1` — only Execution Authority. The deciders for existence, identity, classification, relationship, context, trust and integrity are bound to nothing | declaration vs coverage | `N8` |
| **TX-17** | `.gitignore` rationale: *"An exclusion rule must never be an input to the gate that polices the excluded state"* | `.gitignore` **is** an input: `mutation_classification.py:56` `_EXCLUSION_INSTRUMENTS = frozenset({".gitignore", ...})`; two ignore lines flipped GATE-12, GATE-04, `rib.json:gate`, AEE `OBS-BLUEPRINT-GATE` and `CONV-02` on an unchanged repository | stated rule vs mechanism | `.gitignore` vs `mutation_classification.py:56` |
| **TX-18** | `RTBD-001` §7: generated products are *"NOT part of Repository Truth… Including generated products in Repository Truth would create a **recursive definition**"* | `closure_engine.py:344-346` reads gitignored `knowledge/` as *"authoritative Repository Truth even though it is git-ignored"*; `coverage.xml` (gitignored) decides a PASS/FAIL; `closure.json` (untracked) is the declared `population_document` | determination vs implementation | `M12`, TA-08 |
| **TX-19** | `repo-operations.json` is a pipeline **measurement** declaration | It pre-declares the acceptance facts it should measure: `"implemented": true, "validated": true, "certified": true, "registered": true`, `"architecture_violations": []`, `"freeze_blockers": []` | measurement vs assertion | TA-05; `platform/tests/test_repository_operations_stages.py:171` |
| **TX-20** | `uaue-gate.yml:188-191`: *"Two independent processes, not two calls in one process. An in-process replay could pass on a memoised result; a cross-process replay cannot"* | Both runs invoke the same entry point with the same arguments, so both reach the same initialization state. The gate proves *same invocation sequence = same result*, not *different initialization history = same truth value* | correct reasoning, insufficient scope | `uaue-gate.yml:188-199`; `uisd-gate.yml:231-241` |

**TX-16 is the deepest contradiction, and TX-20 is the one that explains the others' survival.** TX-16: an authority model that declares fourteen capabilities and binds one decider cannot answer "who owns this truth?" for the facets that matter. TX-20: the repository built the right instrument, reasoned about it correctly in a workflow comment, and did not vary the dimension that would have caught either ambient authority.

---

## 12. Reuse and Gap Analysis

Governing precedents respected: `CANONICAL-AUTHORITY-RESOLUTION-DETERMINATION` §4 — Option B (a new authority resolver) **Rejected** as *"Duplicates UCAF, breaches Zero Parallel Authority, and would itself need an authority to charter it — which §3 shows is absent"*; `GATE-PURITY-DETERMINATION` **D-3.4** — *"the reference implementations already exist. Adopt, do not invent"*; `02-CANONICAL-OWNERSHIP-MATRIX` — `CREATE` unavailable under `CMG-000001` Art LXXVII.2(a)/LXXVII.4.

### 12.1 Existing capabilities

| # | Capability | Located implementation | Evidence | Disposition |
|---|---|---|---|---|
| R-1 | **Verbatim, journal-verifying registry loader** | `engine/ceu/existence.py:733` `to_document` / `:773` `from_document` / `:868` `reconstruct` | **Measured working in a fresh process** (`M5`): 195 units, 133 246 bytes, kinds restored 29→72, digest identical. Refuses re-derivation: *"Re-deriving would let the rebuilt registry differ from the recorded one and still look healthy"* | **REUSE** — this is the deterministic reconstruction the target model requires |
| R-2 | **Committed derived artifact + fail-closed replay** | `IdentifierDictionary` `to_document:262`/`from_document:280`; writer `engine/nucleus/cli.py:169-187`; artifact `00-MASTER/UCOS-NUCLEUS-001/UCOS-NUCLEUS-IDENTIFIER-DICTIONARY.json`; self-declaring header `cli.py:154-167` | Measured (`M8`): 212 entries replay in a fresh process, `PASS`, `unparsed=0`. Four persistence tests including `test_a_mutated_entry_is_detected` | **REUSE as the template** for a declared kind-space and vocabulary artifact |
| R-3 | **Purity enforcement by re-running the deriver** | `platform/foundation/derivation.py:285-330` `derive`/`verify`; contract `:20-23`: *"enforces purity by **re-running the deriver** and comparing digests — a value that changes across identical runs (hidden state / wall-clock) is rejected as impure (AIF-L18)"*; `canonical.py:206-216` | Exactly the primitive that rejects hidden state, already implemented | **REUSE** |
| R-4 | **Cross-process verdict comparison** | `.github/workflows/uaue-gate.yml:188-199`; `uisd-gate.yml:231-241` | The pattern and the reasoning both exist. Missing element: **vary the initialization history between run A and run B** | **EXTEND** — the smallest change that makes both ambient authorities measurable |
| R-5 | **Fail-closed declaration loader with two-way totality** | `engine/infinite_scope/contract.py:60-90`; also `engine/uaue/resolution.py:251`, `engine/uckp/resolution.py:150` | *"Fail closed: a declaration that cannot be read is not a declaration that permits everything"*; refuses a contract whose law names a missing check **or** whose check no law claims | **REUSE** — the mechanism for TA-04's unread declarations and TA-12's missing reconstruction contract |
| R-6 | **Collision-refusing, append-only allocation** | `identity.py:162-199` `register_kind`; `vocabulary.py:113-123` `extended_with` (refuses redefinition); `phases.py:89-98` | Both ambient authorities already refuse re-meaning; only durability is absent | **EXTEND** — add persistence; do not touch the refusal logic |
| R-7 | **Cache contract that separates projection from authority** | `engine/execution_environment/fingerprint.py:3-24`; `engine/verification_intelligence/evidence.py:1-36,250-265` | *"It may never skip a verdict, never supply a check result, and never answer VALID on its own"*; *"a certification that can be made to depend on the contents of a cache directory is not a certification"*; *"Unknown widens; it never narrows"* | **REUSE as the contract template** for `bootstrap()`, `register_kind`, `extend` |
| R-8 | **Schema/version contract enforced on read** | `engine/uckp/evolution.py:107,111` enforced `:380-395` (schema **and** `cycle_definition`); `engine/object_birth/ledger.py:31,73-75`; `platform/foundation/canonical.py:36,44-80` | *"Loading is therefore a verification rather than a deserialization"* | **REUSE** — the discipline TA-16's chain lacks |
| R-9 | **Closed-set disclosure register with non-vacuity guard** | `uisd-declaration.json` `closed_enumeration_disclosures`; `engine/infinite_scope/contract.py:170-201` | Requires a `closing_invariant` and an `admission` path per closure; refuses an empty list | **EXTEND** — coverage 11 of ~241 (TA-28) |
| R-10 | **Repository-wide AST scan** | `engine/verification_intelligence/gate.py:611 measure` already parses the whole repository with `ast` | The discovery capability TA-28 needs already exists in another programme | **COMPOSE** with R-9 |
| R-11 | **Recorded / derived plane typing** | `uis-declaration.json:182`: *"The ledger is the RECORDED plane (AIF AX-01) and the registry is the DERIVED plane; **conflating them is the single defect the AIF forbids**"*; `derivation.py:53-58` `InputKind.{SOURCE,RECORDED,DERIVED}`; AIF-L20 | The canonical-vs-runtime distinction is already a typed, enforced axis | **REUSE** |
| R-12 | **Authority resolution by reading a located instrument** | `ucaf-authority.json` — 14 capabilities, 17 resolutions, discovered (not restated) authority sources; *"A competence question is answered by READING a located instrument, never by this programme deciding"* | Exists and fails closed. Option A of `CANONICAL-AUTHORITY-RESOLUTION` | **EXTEND** — 1 of 14 realization bindings (TA-23) |
| R-13 | **Emission modelled as an authority, not a flag** | `00-MASTER/UCCEP-000000/uccep_engine.py:1360-1365` `emission_authority(...)` → `if authority["authorized"]: emit(...)`, else *"OBSERVATION ONLY — emission withheld"* | The only engine separating canonical read from runtime write as an authority question | **REUSE** |
| R-14 | **Registry-only discovery with stabilised ordering** | `engine/discovery/dimensions.py:1-22`: *"no regex over paths or content, no `glob`/`fnmatch`, no filesystem walking… The registry is the single source of truth (INV-13)"*; sorted iteration `:106` | Proves discovery need not scan a filesystem to be complete — the template for TA-08's closure discovery | **REUSE** |
| R-15 | **Fail-closed lever already built and default-off** | `00-MASTER/UAKOS-CLOSURE-002/closure_engine.py:740,766-773` `--require-complete-population` | The lever for TA-08 exists, is fail-closed, and awaits a governance act — not engineering | **HOLD** — reserved to the EKI owner (§14) |
| R-16 | **Interchangeability proof across adapters** | `engine/uckp/persistence.py` — 10 adapters, `verify_interchangeable()` compares `universe_digest()` across all ten, plus a `FUTURE_STORAGE` sentinel that is advisory not refusing | The only axis in the repository where openness and determinism hold **simultaneously** | **REUSE as the proof-of-concept** that the trade in TA-29 is avoidable |

### 12.2 TRUE MISSING

| ID | Missing capability | Why genuinely absent |
|---|---|---|
| **M-1** | **A committed artifact plus a production loader for each ambient authority** — the CEU existence document (for the identity kind space) and a vocabulary document (for `DEFAULT_VOCABULARIES`). | Both halves exist in isolation for CEU and neither is joined: `from_document` measured working in a fresh process (`M5`), zero tracked JSON carries its schema (`M7`), only caller is `reconstruct()` fed a memory round trip. For vocabularies not even the loader exists. This single gap is the mechanism behind TA-13, TA-14, TA-20, TA-29, TX-01…TX-10. **R-1 + R-2 + R-5 + R-6 + R-8 composed over the existing document closes it. Nothing needs inventing.** |
| **M-2** | **A cross-process verdict-equality measurement across differing initialization histories.** | R-4 exists and varies nothing between runs; `double_build` is single-process (`M19`); `grep 'process-independen'` → zero hits; no test observes the pre-bootstrap state (`autouse=True` → zero results across 15 conftest files). Independently closable by measurement; blocks nothing. |
| **M-3** | **Discovery-populated closed-enumeration disclosure.** | R-9 validates a hand-maintained list of 11 against a measured population of ~241 (TA-28). R-10 (repository-wide AST scan) already exists in another programme. The two are not composed. |
| **M-4** | **A declared reconstruction contract per truth object.** | No declaration carries a reconstruction or replay-discipline field (TA-12). `GATE-PURITY` D-3.3 establishes the precedent that such a field belongs in the existing `*-declaration.json` — *"No new registry, no new authority, no new schema family."* |
| **M-5** | **Declared ownership for twelve truth facets, and UCAF realization bindings for their deciders.** | TA-22, TA-23, TX-12, TX-16. **This one is not an engineering gap — it is a governance gap.** Adding a matrix row requires a `CREATE` disposition recorded as unavailable; extending UCAF is Option A, recommended, and `IMPLEMENTATION-NOT-AUTHORIZED` (§14). |

**Not missing — explicitly.** Verbatim journal-verifying loading, committed derived artifacts with fail-closed replay, purity-by-re-derivation, cross-process comparison, fail-closed declaration loading with two-way totality, collision-refusing allocation, cache contracts that bound themselves away from truth, schema/version enforcement on read, closed-set disclosure with non-vacuity, repository-wide AST scanning, recorded/derived plane typing, authority resolution by reading, emission-as-authority, registry-only discovery, and multi-adapter interchangeability proof **all exist and execute**.

**Refused and must not be created:** a new truth authority, a new authority resolver, a second identity authority, a third dictionary, a new canonical-knowledge-resolution engine, a new registry, a new namespace, a new owner row minted by a determination. **No finding in this determination implies any CREATE.**

---

## 13. Implementation Dependency Impact

Recorded as structure only. **No phase, wave, roadmap, sequence or authorization is created or implied.**

### 13.1 Dependency structure

```
M-5  twelve facets unowned + deciders unbound              ← GOVERNANCE ROOT
  │    (TA-22, TA-23, TX-12, TX-16)  — blocked, see §14
  │
  ├── TA-24  capability ownership contested, half-closed
  └── TA-27  four assimilation stages have no truth owner

M-1  committed artifact + production loader absent          ← ENGINEERING ROOT
  │    (TA-05 / TX-10 — mechanism proven M5, artifact absent M7)
  ├── TA-13  identity validity produced by runtime bootstrap
  │     ├── TA-15  ownership cache is also a hidden bootstrap trigger
  │     └── (9 enforcement sites, incl. the constitutional gateway)
  ├── TA-14  DEFAULT_VOCABULARIES — second ambient authority, leaks to nucleus
  ├── TA-20  reconstruction: 4 supported / 2 partial / 7 unsupported
  │     └── TA-21  one loader re-mints rather than replays
  ├── TA-16  certification chain order-defined, unverified on load
  ├── TA-29  expansion by knowledge disproved
  └── TA-11  canonical vocabulary compiled, not declared

M-4  no declared reconstruction contract                    ← DECLARATION ROOT
  └── TA-01  two truth models coexist, neither declared as governing

Independent of every root (closable by measurement alone):
   M-2 / TA-26  no gate measures initialization independence
   M-3 / TA-28  230 undisclosed closed enumerations
   TA-17        _PHASES is non-monotonic
   TA-18        a relationship is registered before it is refused

Recorded, separate axis:
   TA-02  twelve prose constitutions have no machine reader
   TA-04  three declarations written and never read
   TA-05  configuration pre-declares acceptance facts
   TA-06  nine verdict-bearing environment variables; unfiltered inheritance
   TA-08  gitignored artifacts carry verdicts; exclusion authority is a gate input

Correctly assimilated (preserve, do not change):
   TA-07  no database exists
   TA-09  two cache contracts that bound themselves away from truth
   TA-10  the declaration-driven pattern on 14 declarations / 19 schemas
   TA-19  clock / RNG / network discipline
```

**Two independent roots.** `M-1` is an engineering root and is not blocked upstream: the document schema, writer, loader and losslessness proof all exist and are measured working. `M-5` is a governance root and **is** blocked (§14). They are separable: closing `M-1` would make identity and vocabulary validity reconstructible without touching ownership; closing `M-5` requires an act the corpus records as unavailable.

### 13.2 Affected surfaces, recorded for impact awareness

| Surface | Count | Nature |
|---|---|---|
| Enforcement sites reading `is_well_formed` | 9 non-test | `gateway.py:203`, `ownership.py:211,215`, `existence.py:345`, `possessions.py:151`, `location_assurance.py:175,285`, `dictionary.py:57,209,221`, `metadata.py:303` |
| Sites reading `DEFAULT_VOCABULARIES` | 3 non-test | `uckp/registry.py:114` (admission `:123,:167`), `nucleus/catalog.py:473`, `ucko.py:401` |
| Verdicts that would change classification | 6 | `dictionary.verify()["status"]`, `IdentifierEntry.__post_init__`, `ConstitutionalMetadata.identity_well_formed`, `legality._identity_complete`, `UCKO.require_lawful`, `UCKO.transition_to` |
| Truth objects with no reconstruction | 7 of 13 | §6.1 |
| Truth facets with no declared owner | 12 | §7.2 |
| Deciders with no UCAF realization binding | 13 of 14 capabilities | `N8` |
| Undisclosed closed enumerations | 230 | `M16` |
| Gates measuring initialization independence | 0 of 29 | `M17`/`M18` |
| Assimilation stages with no truth owner | 4 of 11 | §9.1 |

---

## 14. Governance Dependency Impact

Recorded, not adjudicated. This section exists because a determination's correctness is necessary but not sufficient for it to be actionable.

### 14.1 Two levels of governance dependency, failing differently

**Level 1 — the implementation gate. Has an owner; not fully discharged.**

The single named implementation decision is `H-06`, owned by **Bipin Kumar** as Mutation Governance Owner and implementation authority. Everything else in the chain self-declares `AUTHORITY: NONE — DERIVED TRUTH` and cannot substitute — `H-06-IMPLEMENTATION-AUTHORIZATION-OWNER-DECISION-RECORD.md:49`: *"**No field in this record substitutes for the IADR §8 signature.**"*

Four blockers are recorded as `PENDING` (`ODR §4.4:183-195`): the IADR §8 signature, the R-4 correction, P-3 selection, and the six Phase-0 conditions. Phase-0 state (`IADR-U §8.1:417-431`): `0.3 PASS`; `0.2 FAIL — unselected; blocked by §3.2`; `0.5 FAIL — never captured`; `0.6 FAIL`; `0.4 ELIGIBLE FOR RE-MEASUREMENT — Re-measurement is an owner act and is not performed here`. The rule: *"**No phase begins until all six pass.**"*

**A defect inside Level 1, recorded.** The canonical §8 authorization state is inconsistent within one file. `H-06-IMPLEMENTATION-AUTHORIZATION-DECISION-RECORD-UPDATED.md:18` reads `**§8 SIGNED — AUTHORIZED — Bipin Kumar, 2026-08-16T20:10:00+05:30 (entry S-1)**` with `[X] AUTHORIZED` at `:388`, while the same file's Authority field (`:7`) and closing lines (`:452`) assert `§8 is unsigned`. The paired owner-decision record independently reports `PENDING — UNSIGNED` with *"0 marked boxes, Authorized By blank, Date blank"*. Both readings converge on the operative outcome — `IMPLEMENTATION STILL GATED` — because P-3 and Phase 0 fail either way.

**Level 2 — the ratification vacuum. Has no owner and cannot acquire one from inside.**

Three located instruments independently record the absence (`CANONICAL-AUTHORITY-RESOLUTION-DETERMINATION.md:127-131`):

> `UCAF-RC-01` — *"no located authority is competent to ratify"* (source `uccep-bindings.json`)
> `UCAF-RC-02` — *"no ratified normative artifact occupies the vacant constitutional tier"* (source `CMG-REGISTRY.json`)
> `UCAF-RC-03` — *"the corpus contains no authority competent to ratify anything"* (source `00-CMG/README.md`)

Classified `UCAF-F-002` as a `STANDING-CONSTITUTIONAL-CONFLICT`; `UCAF-F-003` holds that *"Competence to ratify and the ratifying act are distinct, and only the first is closable by measurement."* Tier T1 is `VACANT` (`VAC-01`); `CMG-OQ-01` and `CMG-OQ-02` are open; promotion into the vacancy is forbidden by `CMG-000001` XVII.4 and voided by LXXXI.5; constituting T1 is `OA-6`, `NOT ACTIONABLE IN-REPOSITORY`. The operational consequence is recorded as accepted, not as a defect: *"Operate at CERTIFIED-PROVISIONAL indefinitely; this is a known, recorded ceiling, not a defect to engineer around."*

The consequence the resolution determination states verbatim (`:135`): *"Every 'reserved' disposition in this session should be read as **awaiting owner decision**, not awaiting a repository process."*

### 14.2 What can and cannot be acted upon

| Act | Competence | Status |
|---|---|---|
| **Authorize implementation** within a pre-declared scope | **PRESENT** — IADR §8, Bipin Kumar | exercisable, bounded, non-delegable: *"Authorization by the implementation authority does not expand, reinterpret, or amend either owner decision or the ratified mode vocabulary"* |
| **Amend or ratify a constitutional instrument** | **ABSENT** | `UCAF-RC-01/02/03`; external constituent act; `NOT ACTIONABLE IN-REPOSITORY` |
| **Create a new canonical owner row** | **ABSENT** | every matrix addendum records `CREATE` unavailable under `CMG-000001` Art LXXVII.2(a)/LXXVII.4; `--check-no-authority` **fails closed if any capability is ever dispositioned CREATE**; recorded dispositions are *"48 REUSE and 6 EXTEND, with zero CREATE"* |
| **Make an incomplete closure population blocking** | **RESERVED** — EKI owner, pending P2 sign-off | `closure_engine.py:44-51`: *"Making an incomplete population BLOCKING is a verdict-changing governance act, recorded as AB-6 … and reserved to the EKI owner pending P2 sign-off; a measurement engine may not confer that on itself."* Lever `--require-complete-population` provided *"fail-closed and default-off"* |
| **Select the gate-mode policy (Option A/B)** | owner — `H-06` = `CR-09` | `GATE-PURITY-DETERMINATION`: *"the owner's choice, not a measurement's. Recorded, not selected."* |

### 14.3 TA-30 — Five of this determination's findings are governance-blocked, not engineering-blocked

- **Finding.** The findings that would close the deepest gaps require acts the corpus records as unavailable or reserved.
- **Evidence.** `M-5` (declared ownership for twelve facets) requires a `CREATE` disposition — recorded unavailable, with a gate that fails closed if attempted. UCAF realization bindings for the deciders are Option A of `CANONICAL-AUTHORITY-RESOLUTION`, whose standing is `DETERMINATION-COMPLETE · SEVEN CATEGORIES RECORDED · ZERO RESOLVED · IMPLEMENTATION-NOT-AUTHORIZED`. TA-08's closure lever is reserved to the EKI owner pending P2 sign-off. TA-01/TA-12's declared reconstruction contract lives in the `*-declaration.json` surface, which per `GATE-PURITY` D-3.3 belongs to each programme owner and is blocked on `H-06`/`CR-09`. Everything touching gate behaviour is blocked on the same decision.
- **Current state.** `M-1`, `M-2` and `M-3` are engineering-closable and unblocked by governance. `M-4` and `M-5` are not.
- **Desired state.** The distinction recorded, so effort is not spent on the blocked half.
- **Impact.** A determination can be correct and unactionable. The honest reading is that the two ambient authorities (TA-13, TA-14) and the measurement gap (TA-26) can be closed inside the existing owner's scope, while the twelve unowned facets cannot be closed at all from inside the repository.
- **Dependency.** External to this determination.
- **Classification.** **UNKNOWN** — the governance position is recorded; its resolution is not a measurement.

### 14.4 What this determination is permitted to do, and did

Per `POST-STABILIZATION-DETERMINATION-LIFECYCLE-DECISION.md` and `GOVERNED-EVOLUTION-STATE-DETERMINATION.md` (*"Defines a category and its rules. Legislates nothing and reclassifies nothing"*), determinations in this corpus may measure, record and refer. They may not decide, reclassify, legislate, allocate ownership, or commit. This determination measured, recorded and referred. It selected no option, allocated no ownership, reclassified nothing, and resolved no contradiction.

---

## 15. Final Architectural Determination

### 15.1 The three questions answered

**1. Truth authority inventory.** Thirteen classes of truth source exist (§3.1). Nine can change truth. One class — the database — does not exist at all, which removes an entire category of hidden authority. Two classes are canonical and read (declarations, committed schemas/ledgers/registries). Two classes are canonical and **not** read (twelve prose constitutions, three declarations). Four classes can change truth while being declared *not* Repository Truth (generated artifacts, configuration, environment, process memory).

**2. Runtime authority detection.** Across the eight truth categories: **four are ACCIDENTAL AUTHORITY** (identity validity; UCKP lawfulness; UCKP lifecycle transitions; the certification chain), **one is OPTIMIZATION ONLY with a side-effect leak** (ownership), and **six are PROJECTION ONLY** (EC-1/knowledge/context validity, capability existence, relationship existence, core lifecycle, certification verdict, compliance). Two process-global mutable authorities exist, not one: `identity.py:156,159` and `vocabulary.py:542`. Both are documented as *"the only extension mechanism"*, both write only to process memory, and **both leak into a capability other than the one that owns them** — measured at `M3` and `N6`.

**3. The truth boundary model.** Both chains are implemented and neither is declared as governing:

```
IMPLEMENTED (target):  Canonical Knowledge → Deterministic Reconstruction → Validation → Runtime Projection
                       4 truth objects fully · 2 partially · mechanism measured working (M5)

IMPLEMENTED (defect):  Canonical Knowledge → Bootstrap/extend → Mutable Runtime State → Validation
                       identity kind space · DEFAULT_VOCABULARIES · certification chain · closure population
```

### 15.2 Classification summary

| Finding | Subject | Classification |
|---|---|---|
| TA-01 | Two truth models coexist, neither declared as governing | PARTIALLY ASSIMILATED |
| TA-02 | Twelve prose constitutions have no machine reader | NOT YET ASSIMILATED |
| TA-03 | Truth-holding registries compiled or ephemeral; one reads a committed file | PARTIALLY ASSIMILATED |
| TA-04 | Three declarations written and never read | PARTIALLY ASSIMILATED |
| TA-05 | Configuration changes verdicts four ways; pre-declares acceptance facts | NOT YET ASSIMILATED |
| TA-06 | Nine verdict-bearing environment variables; unfiltered subprocess inheritance | PARTIALLY ASSIMILATED |
| TA-07 | No database exists; persistence is git plus JSON | **ASSIMILATED** |
| TA-08 | Gitignored artifacts carry verdicts; exclusion authority is a gate input | NOT YET ASSIMILATED |
| TA-09 | Two cache contracts bound themselves away from truth | **ASSIMILATED** |
| TA-10 | The declaration-driven pattern is correct and works | **ASSIMILATED** |
| TA-11 | Canonical vocabulary governing existence is compiled, not declared | PARTIALLY ASSIMILATED |
| TA-12 | No truth object declares its reconstruction contract | NOT YET ASSIMILATED |
| TA-13 | Identity validity produced by runtime bootstrap | NOT YET ASSIMILATED |
| TA-14 | A second process-global mutable authority, leaking across capabilities | NOT YET ASSIMILATED |
| TA-15 | Ownership cache is a genuine cache and a hidden bootstrap trigger | PARTIALLY ASSIMILATED |
| TA-16 | Certification chain order-defined, unverified on load | NOT YET ASSIMILATED |
| TA-17 | One runtime registry is non-monotonic | PARTIALLY ASSIMILATED |
| TA-18 | A relationship is registered before it is refused | NOT YET ASSIMILATED |
| TA-19 | Nondeterminism discipline correct; statefulness unguarded | PARTIALLY ASSIMILATED |
| TA-20 | Reconstruction: 4 supported / 2 partial / 7 unsupported | PARTIALLY ASSIMILATED |
| TA-21 | One loader re-mints rather than replays | PARTIALLY ASSIMILATED |
| TA-22 | Twelve truth facets have no declared owner | NOT YET ASSIMILATED |
| TA-23 | The deciding modules exercise no located authority | NOT YET ASSIMILATED |
| TA-24 | Capability ownership contested, diagnosed, half-closed | PARTIALLY ASSIMILATED |
| TA-25 | Independence holds on every classical axis, fails on call history | PARTIALLY ASSIMILATED |
| TA-26 | Two cross-process gates prove path reproducibility, not initialization independence | PARTIALLY ASSIMILATED |
| TA-27 | Four of eleven assimilation stages have no truth owner | NOT YET ASSIMILATED |
| TA-28 | 230 closed enumerations undisclosed; the governing law cannot detect them | PARTIALLY ASSIMILATED |
| TA-29 | Expansion by knowledge disproved; both extension mechanisms are runtime authorities | NOT YET ASSIMILATED |
| TA-30 | Five findings are governance-blocked, not engineering-blocked | UNKNOWN |

| Classification | Count |
|---|---|
| ASSIMILATED | 3 |
| PARTIALLY ASSIMILATED | 14 |
| NOT YET ASSIMILATED | 12 |
| UNKNOWN | 1 |
| **Total** | **30** |

Per capability domain:

| Classification | Domains |
|---|---|
| ASSIMILATED | Context (determinism only — ownership absent), Lifecycle (core tables only) |
| PARTIALLY ASSIMILATED | Entity, Relationship, Capability, Certification, Measurement, Ownership |
| NOT YET ASSIMILATED | Identity, Security |
| UNKNOWN | Requirement |

### 15.3 The identity case — the primary example

```
Same repository.  Same commit (bae59755).  Same machine.

Before CEU bootstrap:   UCOS-CLSS-8966ca9e8d02  →  INVALID
After  CEU bootstrap:   UCOS-CLSS-8966ca9e8d02  →  VALID

Zero file changes.  43 of 72 kinds affected.
9 enforcement sites inherit the predicate, including the constitutional
mutation gateway, NUC-INV-09, and the constitutional legality proof.
```

**Identity validation is runtime-state dependent.**

And the same shape a second time, newly established here:

```
Before DEFAULT_VOCABULARIES.extend:  require_term(...) →  REFUSED (LawViolation)
After  DEFAULT_VOCABULARIES.extend:  require_term(...) →  ACCEPTED

seed_layers()   14 → 15
seed_subjects() 83 → 84      ← the NUCLEUS population changed because a
                               UCKP vocabulary was mutated
```

**UCKP lawfulness is runtime-state dependent, and it leaks into the nucleus.**

### 15.4 The determinism distinction — stated explicitly

Two of twenty-nine gates compare verdicts across separate processes: **UAUE** (`uaue-gate.yml:188-199`) and **UISD** (`uisd-gate.yml:231-241`). The UAUE workflow states the principle correctly in its own comment: *"An in-process replay could pass on a memoised result; a cross-process replay cannot."*

**These gates prove:**

```
same invocation sequence  +  same execution path  =  same result
```

**These gates do NOT prove:**

```
different runtime initialization history  =  same truth value
```

Run A and run B invoke the same entry point with the same arguments. Both therefore reach the same initialization state and inherit identical module globals and an identically-populated vocabulary singleton. A verdict that depends on whether `bootstrap()` or `extend()` ran is equally wrong in both runs, and the `diff` passes. **Therefore neither gate detects runtime-state-dependent truth**, and nothing else does either: nine self-guards compare two renders inside one process, and `double_build` runs both builds in one interpreter sharing one environment, adapter and signer.

### 15.5 Final architectural test

> **"UCOS Ω∞ has a universal truth authority model where all truth originates from canonical knowledge, runtime only projects and executes that truth, and no runtime state can become an accidental authority."**

## **Determination: PARTIALLY PROVEN**

**Clause 1 — "all truth originates from canonical knowledge": PARTIALLY PROVEN.** Canonical knowledge exists across all six declared surface families and is genuinely operative: 14 of 17 declarations are read by the engines that cite them, 19 schemas are read, two ledger schemas are enforced on read with the correct reasoning (*"Loading is therefore a verification rather than a deserialization"*), and every committed artifact that could be mistaken for an authority carries an explicit derived-truth disclaimer naming its canonical source. Against this: the canonical vocabulary that governs existence is Python source rather than data, twelve prose constitutions and three declarations reach no validator, and part of the acceptance verdict is read from a swappable configuration file rather than measured.

**Clause 2 — "runtime only projects and executes that truth": PARTIALLY PROVEN.** Six of twelve truth surfaces are projection-only. Four truth objects survive the delete-reload-reconstruct-compare test, and the mechanism for a fifth is measured working in a fresh interpreter with a digest-identical round trip. Two caches state and enforce exactly the projection-not-authority contract this clause requires. Against this: seven of thirteen truth objects cannot be reconstructed at all, one load path re-mints rather than replays, and the certification chain is defined by append order and unverified on load.

**Clause 3 — "no runtime state can become an accidental authority": DISPROVEN.** Two process-global mutable authorities exist. Each is documented as *the only extension mechanism* for its capability, each writes only to process memory with no persistence and no loader, and each was measured changing a validity verdict — `is_well_formed` `False`→`True`, `require_term` `REFUSED`→`ACCEPTED`. Both leak across capability boundaries: an ownership question flips an identity verdict; a UCKP vocabulary mutation changes the nucleus structural population. Neither is measurable by any of the 29 gates.

**And a fourth clause the statement presupposes — that there is a *universal truth authority model* at all: DISPROVEN as stated.** Twelve truth facets have no declared owner in either ownership instrument, and the authority register that would bind deciders to authorities contains **one** realization binding against **fourteen** declared capabilities. For those twelve facets the question "can runtime become an accidental authority?" has no answer, because no other authority is declared for runtime to usurp. `engine/nucleus/law.py:9-19` states the terminal form of this plainly: having found no located clause, *"This module supplies exactly those missing clauses and nothing else."*

### 15.6 What the evidence does support, stated precisely

> *UCOS Ω∞ has a rigorous truth authority model for **constitutional authority** and no truth authority model for **ontological authority**. Where a truth object is declared, read, and reconstructible, the target chain holds and is measurably deterministic. Where openness was required, it was purchased twice with process memory, and in both cases the resulting authority leaks into a capability that does not own it. The information and every mechanism required to close the engineering half — a verbatim journal-verifying loader, a committed derived artifact with fail-closed replay, purity by re-derivation, cross-process comparison, collision-refusing allocation, schema enforcement on read — already exist and execute. What is absent is two committed artifacts, the wire from them to the validation path, one measurement that varies initialization history, and — for twelve facets — a declared owner that the corpus records itself as having no competence to create.*

### 15.7 Standing

| Item | State |
|---|---|
| Determination | **COMPLETE** |
| Findings recorded | **30** (`TA-01`…`TA-30`) |
| Contradictions recorded | **20** (`TX-01`…`TX-20`) |
| Findings resolved | **ZERO** |
| Contradictions resolved | **ZERO** |
| Engineering root cause | **M-1** — committed artifact and production loader absent for both ambient authorities |
| Governance root cause | **M-5** — twelve facets unowned, deciders unbound; `CREATE` unavailable |
| True missing capabilities | **FIVE** (`M-1`…`M-5`), of which **three** are engineering-closable and **two** are governance-blocked |
| Measurements executed | **27** — `M1`…`M19` carried, `N1`…`N8` new; all read-only |
| New engines / authorities / registries / namespaces implied | **ZERO** |
| `CREATE` dispositions implied | **ZERO** |
| Code modified | **NONE** |
| Runtime systems modified | **NONE** |
| Registries modified | **NONE** |
| Configuration modified | **NONE** |
| Ownership allocated or reclassified | **NONE** |
| Requirements / ADRs / phases / roadmaps created | **NONE** |
| Certification altered | **NONE** |
| Options selected | **NONE** |
| Repository writes | **ONE** — this document |

**Measurement disclosure.** All twenty-seven measurements were pure in-memory evaluations in throwaway interpreters. Registration probes (`M4b`, `M9`, `N1b`, `N6`) mutated only that process's memory and were discarded on exit. No gate that writes was executed; `closure_engine.py` was **not** run — `closure.json` was read as it stood. No tracked file was modified. No registry file, artifact or ledger was written.

**Relationship to the predecessors.** The identity determination (`DV-01`…`DV-17`) established the defect for one capability. The canonical-knowledge determination (`CR-01`…`CR-24`, **PARTIALLY PROVEN**) established that the pattern extends to CEU entity, CEU relationship and capability, and that the deterministic resolver already exists unwired. This determination establishes three things neither could: **TA-14**, that a second, independent process-global mutable authority exists and leaks across capabilities in the identical measured way — making this a repeated architectural pattern rather than a single site; **TA-22/TA-23**, that beneath the runtime-authority defect lies an ownership vacuum in which twelve truth facets have no declared owner and their deciders no located authority; and **TA-26**, the precise scope of the two cross-process gates — they prove reproducibility of one execution path and cannot, by construction, prove independence from initialization history.

---

**END DETERMINATION — STOPPED AFTER DETERMINATION.**
