# UCOS Ω∞ — CANONICAL KNOWLEDGE TO RUNTIME EXECUTION TRUTH BOUNDARY DETERMINATION

| Field | Value |
|---|---|
| **Classification** | EVIDENCE — DETERMINATION ONLY |
| **Authority** | **NONE — DERIVED TRUTH.** Certifies nothing, ratifies nothing, creates no authority, mints no identifier, registers no kind, authorises no work. |
| **Mode** | READ-ONLY. No code modified, no runtime system modified, no registry modified, no configuration modified, no requirement/ADR/phase created, no fix implemented, no certification altered, no identifier created. |
| **Baseline** | `git HEAD = bae59755d7e2d3566c93b89c722b68847145269a`, branch `integration/recovery-001`, 331 uncommitted working-tree entries at start |
| **Reference system** | `logical:git-commit-order@ucos-consolidation`. No wall clock read for any measurement. |
| **Method** | Static reading **plus direct in-memory measurement**. Nineteen measurements (`M1`…`M19`) executed as pure function evaluations in throwaway `python3` interpreters. Nothing written to the repository, no registry file touched, no gate executed that writes. |
| **Finding markers** | `CR-01`…`CR-24` and contradictions `CX-01`…`CX-18` are **local reading aids scoped to this document**. They register nothing and enter no namespace. |
| **Predecessor** | Continues `UCOS-OMEGA-INFINITY-IDENTITY-DETERMINISTIC-VALIDATION-BOUNDARY-DETERMINATION.md` (same baseline), which established `DV-01`…`DV-17` for the identity capability. This determination tests whether the same defect pattern exists **beyond identity**. |
| **Standing determinations respected** | `RTBD-001` (what Repository Truth is), `CANONICAL-AUTHORITY-DETERMINATION` (authority is tripartite), `CANONICAL-AUTHORITY-RESOLUTION-DETERMINATION` (extend UCAF; a new resolver is Rejected), `GATE-PURITY-DETERMINATION` (gates lack a declared mode). This determination contradicts none of them and proposes no new engine. |

---

## 1. Objective

Determine whether UCOS Ω∞ consistently derives truth from canonical knowledge, or whether runtime execution state — initialization order, mutable memory, caches, or process lifecycle — accidentally becomes an authority.

**Primary question.** For any UCOS Ω∞ concept:

```
Canonical Knowledge → Runtime Interpretation → Validation → Execution
```

is truth derived from canonical knowledge, or does runtime state become an accidental authority?

**Architectural principle under test:**

```
Canonical Knowledge
    ↓
Deterministic Resolver
    ↓
Pure Validation
    ↓
Runtime Projection
    ↓
Execution
```

Runtime **may** cache, optimize, accelerate. Runtime **must not** create truth, change truth, determine validity, or become the only source of knowledge.

**Answer in one paragraph.** Canonical knowledge exists and is real — declarations, constitutions, seed data, schemas, registries and ledgers are all present, and fourteen of seventeen programme declarations are genuinely read by the validators that cite them. But the principle is not universally satisfied. In at least one measured surface the chain that actually executes is:

```
Canonical Knowledge → Runtime Bootstrap → Mutable Module State → Validation Truth
```

with no deterministic resolver and no persisted projection between the second and third steps. The consequence is measurable: the same identifier, at the same commit, on the same machine, is invalid in one process and valid in another. The defect is narrow in mechanism (one pair of module-global dictionaries) and wide in consequence (nine enforcement sites, including the constitutional mutation gateway, the nucleus ownership invariant, and the constitutional legality proof).

**Determination: PARTIALLY PROVEN.** Detail in §15.

---

## 2. Evidence Baseline

### 2.1 Repository state

| Measure | Value |
|---|---|
| `git HEAD` | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch | `integration/recovery-001` |
| Uncommitted working-tree entries at start | 331 |
| Python files in `engine/ platform/ service/ application/ infrastructure/ intelligence/ knowledge/ realization/` | 1942 |
| Interpreter used for all measurements | `.ec1-venv/bin/python` → `3.12.13 (main, Mar 3 2026) [Clang 21.0.0]` |
| Closed `Enum` subclasses across the six code roots | **238** (200 distinct names) |
| CI gate workflows | 29 |
| Programme declarations under `00-MASTER/**/​*-declaration.json` | 17 |

### 2.2 The decisive measurement — identity validity is a function of process history

Executed read-only in three independent interpreters at `HEAD = bae59755`.

**M1 — fresh interpreter, `engine.registry.universal.identity` imported, no CEU bootstrap:**

```
core RegistryKind members: 29
kind_names(): 29
_EXTENSION_KIND_CODES: 0
  is_well_formed(UCOS-CLSS-8966ca9e8d02) = False
  is_well_formed(UCOS-ENTY-abc123def456) = False
  is_well_formed(UCOS-AUTH-aaaabbbbcccc) = False
  is_well_formed(UCOS-MSMT-999988887777) = False
  is_well_formed(UCOS-CAP-111122223333) = True     ← core kind
  is_well_formed(UCOS-NUC-abc123def456) = True     ← core kind
  is_well_formed(UCOS-LOC-abc123def456) = True     ← core kind
```

**M2 — fresh interpreter, `engine.ceu.catalog.bootstrap()` called first:**

```
kind_names(): 72
_EXTENSION_KIND_CODES: 43
total admissible: 72
  is_well_formed(UCOS-CLSS-8966ca9e8d02) = True
  is_well_formed(UCOS-ENTY-abc123def456) = True
  is_well_formed(UCOS-AUTH-aaaabbbbcccc) = True
  is_well_formed(UCOS-MSMT-999988887777) = True
```

The 43 runtime-registered kind codes measured:

```
ARCH AUTH BNDY CAUS CLSS CNSN CNST CNTR DCSN DICT ENTY EPST EVNT EXST FORM
GENR GOAL GOVN INTN KNST MSMT MSYS OBSN OBSV PRED PRPS PRSP PTRN QNTY RCVY
RISK RLTY RSRC RULE SCAL SIML STAT SVRN TMPM TOPO TRST UNIT VALU
```

**The identity case, stated as the directive requires:**

```
Same repository.  Same commit (bae59755).  Same machine.

Before CEU bootstrap:   UCOS-CLSS-8966ca9e8d02  →  INVALID
After  CEU bootstrap:   UCOS-CLSS-8966ca9e8d02  →  VALID

Zero file changes between the two measurements.
```

**Conclusion: identity validation is runtime-state dependent.** 43 of 72 admissible kinds (59.7%) carry this property. This reproduces the predecessor determination exactly and is the primary example this determination generalises from.

### 2.3 The new measurement — the dependency crosses capability boundaries

**M3.** The predecessor established that *import is not sufficient; a call is required*. This measurement establishes something sharper: **the required call need not be an identity call at all.**

```
step 1  fresh import of engine.registry.universal.identity only
        kind_names=29   is_well_formed(UCOS-CLSS-8966ca9e8d02)=False

step 2  import engine.nucleus.authority   (import ONLY, no call)
        kind_names=29   is_well_formed(UCOS-CLSS-8966ca9e8d02)=False

step 3  ask an OWNERSHIP question, unrelated to identity:
        may_own_capability('nucleus') = True
        kind_names=72   is_well_formed(UCOS-CLSS-8966ca9e8d02)=True
```

Asking whether a nucleus may own a capability silently changed the truth value of an identifier. Nothing in `engine/nucleus/authority.py` announces this; nothing in `engine/registry/universal/identity.py` records that its answer just changed. This is the mechanism by which the defect leaves the identity capability and becomes a property of the whole runtime.

### 2.4 The verdict flip reaches a hard refusal

**M6.** Constructing a dictionary entry for an extension-kind identifier:

```
A. fresh process, NO bootstrap:
   RAISED: RegistrationValidationError [REG-PLAT-VALID-400]
           dictionary entries carry identifiers minted by the one authority
           (value='UCOS-CLSS-8966ca9e8d02')

B. same construction AFTER bootstrap, same commit, same machine:
   constructed OK -> UCOS-CLSS-8966ca9e8d02
```

`engine/registry/universal/dictionary.py:57` (`IdentifierEntry.__post_init__`) refuses in one process and accepts in another.

### 2.5 The loader that would close this already exists and already works

**M5.** This is the most consequential new measurement in this determination.

```
Process 1 — bootstrap CEU, project the registry to a document:
  document schema: ucos-constitutional-existence-registry
  units: 195      bytes: 133246      digest: b68559b7b416955d

Process 2 — SEPARATE fresh interpreter that NEVER calls bootstrap():
  pre-load  kind_names: 29
  pre-load  is_well_formed(UCOS-CLSS-8966ca9e8d02): False
  ExistenceRegistry.from_document(doc)  →  SUCCEEDED without bootstrap()
  post-load kind_names: 72
  post-load is_well_formed(UCOS-CLSS-8966ca9e8d02): True
  rebuilt digest: b68559b7b416955d          ← byte-identical round trip
```

`ExistenceRegistry.from_document` (`engine/ceu/existence.py:773`) reads a **document**, registers form codes with the identity authority before minting unit identities, verifies every unit reproduces its own digest, verifies the journal, and restores the full 72-kind space in a process that never executed `bootstrap()`.

**M7.** No such document is committed:

```
git grep -l "ucos-constitutional-existence-registry" -- '*.json'   →  0 files
git grep -l "ucos-constitutional-existence-registry"               →  engine/ceu/existence.py  (only)
```

The reader exists. The writer exists. **The artifact does not.** The canonical-knowledge path is built and unused.

### 2.6 Measurement index

| ID | What it measured | Result |
|---|---|---|
| M1 | Fresh-process kind space and validity | 29 kinds; 4 extension probes all `False` |
| M2 | Post-bootstrap kind space and validity | 72 kinds, 43 extension; all probes `True` |
| M3 | Whether an ownership call flips an identity verdict | **Yes** — 29→72, `False`→`True` |
| M4 | The three other module-global registries at fresh import | All **self-seed**: 1, 2, 8 entries |
| M4b | `unregister_generation_phase` effect | `generation_order()` raises `FAC-PHASE-001` |
| M5 | `ExistenceRegistry.from_document` in a fresh process | **Succeeds**; restores 72 kinds; digest identical |
| M6 | `IdentifierEntry` construction pre/post bootstrap | Raises / succeeds |
| M7 | Committed existence document exists? | **Zero** tracked JSON |
| M8 | Committed identifier dictionary replay in fresh process | `PASS`, `unparsed=0`; only core codes `CAP CMPO LYR NUC` |
| M9 | `roles_holding` cache and runtime extensibility | `misses=1, hits=1`; a registered role is **invisible** |
| M10 | Determinism across `PYTHONHASHSEED` 0/1/42/12345 | All digests identical |
| M11 | Import-order variation (identity-first vs ceu-first) | Both 72/43 |
| M11b | Double bootstrap | 72/43; `digest_a == digest_b` |
| M12 | `closure.json` verdict state and tracking status | `CLOSED`, `gaps=0`, `concepts=549`; **gitignored, untracked** |
| M13 | Enum census | 66 in `engine/`; 238 across six roots |
| M14 | Enforcement-site source reading | `gateway.py:199-209`, `ownership.py:210-215`, `metadata.py:301-303` |
| M15 | Whether constitutional legality inherits by live call | **Yes** — `identity_well_formed` is a live call |
| M16 | Disclosed vs undisclosed closed enumerations | 8 disclosed occurrences; **230 undisclosed** |
| M17/M18 | Gates comparing verdicts across processes | **2 of 29** (`uaue`, `uisd`) |
| M19 | `double_build` process isolation | Single interpreter, shared env/adapter/signer |

---

## 3. Canonical Knowledge Architecture

Canonical knowledge in UCOS Ω∞ exists, is substantial, and is distributed across six surface families. The architecture is genuinely declaration-driven in its dominant pattern: **committed JSON declares, Python reads, gates replay.** Every committed artifact that could be mistaken for an authority carries an explicit `"authority": "NONE — DERIVED TRUTH"` disclaimer naming its canonical source. That discipline is real and it works.

The weakness is not absence of canonical knowledge. It is that **the most load-bearing canonical knowledge is Python source rather than committed data**, and that a small number of surfaces are written and never read.

### 3.1 Surface inventory

| Surface | Instances | Owner | Persistence | Authority | Consumer | Used by a validator? |
|---|---|---|---|---|---|---|
| **Constitutions (prose family)** | `00-MASTER/CMG-000001` … `CMG-000012` | CMG authority (self-declaring) | committed Markdown, prose | asserted source of truth | **NO READER FOUND** — zero hits across `*.py`, `*.yml`, `*.sh` | **No** |
| **Constitutions (machine family)** | `00-CMG/` CMG-000001…014 + `CMG-REGISTRY.json` | CMG authority | committed Markdown + JSON projection | registry self-declares `"authority": "NONE (DERIVED TRUTH)"`, names its canonical `.md` source | `00-CMG/tools/cmg_validate.py:36,85-101,603`; 4 `.runtime/` scripts; `uaie-gate.yml` | **Yes** |
| **Declarations** | 17 under `00-MASTER/**/​*-declaration.json` | per-programme | committed JSON | declared law surface | 14 read by their programme engine; **3 written-only**: `ceu-declaration.json`, `urr-declaration.json`, `ucxi-declaration.json` | 14 yes / 3 no |
| **Seed data** | 24 `SEED_*` constants (17 in `engine/ceu/catalog.py`) | the module that declares them | **Python source** | `catalog.py:18-21` disclaims privilege: *"Nothing here is privileged… The seeds are examples that happen to be useful, not a fixed vocabulary."* | `bootstrap()` at `catalog.py:396`; `platform/universal_pipeline/*` register at import | **Yes, indirectly** |
| **Schemas** | 19 `00-BOOK/SCHEMAS/*.schema.json`; `realization/schema/*`; `00-MASTER/STATE/mcs-state.schema.json` | corpus / realization | committed JSON | validation contracts | `00-BOOK/tools/config.py`, `engine/registry/source.py`, `engine/verification_intelligence/*`, `ec1-ci.yml`. **`mcs-state.schema.json`: no `.py`/`.yml` reader** | mostly yes |
| **Ledgers** | evolution (`engine/uckp/evolution.py`), object birth (`engine/object_birth/ledger.py`), certification, DAG, runtime ops, `00-BOOK/DATA/id-ledger.json` | per-module | mixed: two committed, several in-memory only | `AIF AX-01` recorded plane | schema **enforced on read** at `evolution.py:380-395` and `ledger.py:73-75` | **Yes** for the two enforced |
| **Registries (committed)** | `00-CMG/CMG-REGISTRY.json`, `engine/registry_coverage/declarations.json`, `00-BOOK/DATA/*.json`, UGA object registries | per-programme | committed JSON | every one self-declares derived | read by their engines | **Yes** |
| **Registries (in-memory only)** | identity extension space, `KnowledgeRegistry`, `IdentityRegistry`, UCP capability/ownership, `ExistenceRegistry`, `NucleusRegistry` | per-module | **process memory** | several self-declare *canonical* | in-process callers | **Yes — and this is the defect surface** |
| **Manifests** | `00-SOURCE-MANIFEST/SOURCE-{FILES,HASHES}.txt`, ACEE goal/invariant manifests, UCL stage manifest | per-programme | committed text/JSON | immutability oracle | `engine/tests/unit/test_frozen_paths.py`, `closure_engine.py`, `ec1-ci.yml`. **`02-IMPLEMENTATION-MANIFEST.md`: no reader** | mostly yes |
| **Enumerations** | 238 closed `Enum` subclasses | per-module | Python source | de facto closed truth sets | everywhere | **Yes** |

### 3.2 CR-01 — The largest body of canonical knowledge is Python source, not committed data

- **Finding.** The entire existence universe of every fresh process is constructed from tuples in a `.py` file. `SEED_FORMS` (53 rows), `SEED_CLASSIFICATIONS` (10), `SEED_TOPOLOGIES` (17), `SEED_RELATIONSHIP_TYPES` (17), `SEED_TEMPORAL_MODELS` (7), `SEED_UNITS` (15) and eleven more populations live in `engine/ceu/catalog.py`.
- **Evidence.** `engine/ceu/catalog.py:46,119,141,198,217,230,244,258,269,280,292,301,313,332,347,370,382`; consumed by `bootstrap()` at `:396-473`. The module docstring argues the case for treating them as data (`:18-21`), and the design intent is sound. `engine/nucleus/catalog.py:58,109,483` holds the equivalent for the nucleus population. Measured: `bootstrap()` produces digest `b68559b7b416955d` deterministically (M10, four hash seeds).
- **Current state.** Canonical vocabulary is committed — as source code. Extending it is a `git diff` to a `.py` file.
- **Desired state.** The declared vocabulary is committed data that a validator reads, with the Python seeds retained as one admissible catalogue rather than the only one.
- **Impact.** Two consequences. First, "knowledge evolution rather than code mutation" is not achievable on this axis (§11). Second, because the vocabulary reaches validators only by executing `bootstrap()`, it becomes process state at the moment of use (CR-05).
- **Dependency.** None upstream. `ExistenceRegistry.to_document`/`from_document` already exist and round-trip losslessly (M5).
- **Classification.** **PARTIALLY ASSIMILATED** — the knowledge is committed and deterministic; its form prevents data-only evolution.

### 3.3 CR-02 — Twelve constitutional instruments have no machine reader

- **Finding.** `00-MASTER/CMG-000001` through `CMG-000012` are prose Markdown with zero references from any Python file, workflow, or shell script.
- **Evidence.** `grep -rln "00-MASTER/CMG-0000" --include="*.py" --include="*.yml" --include="*.sh"` returns **zero results**. Each directory contains exactly one `.md` file and no JSON sibling. By contrast the parallel `00-CMG/` family carries `CMG-REGISTRY.json`, which `00-CMG/tools/cmg_validate.py:36` pins as `REGISTRY_RELPATH` and dereferences at `:99-101`, with `canonical_source_version` compared at `:603`.
- **Current state.** Two constitutional families with the same identifier series; one is machine-readable and enforced, one is prose and unenforced.
- **Desired state.** Every instrument that governs a validator is reachable by that validator, or is explicitly declared advisory.
- **Impact.** Governance stated in the prose family cannot bind execution. This is the surface on which clause tokens cited from code (`AC-001`, `AC-009`, `XXXI.5`) have no located text — see CX-13.
- **Dependency.** CR-03.
- **Classification.** **NOT YET ASSIMILATED.**

### 3.4 CR-03 — Three declarations are written and never read

- **Finding.** `00-MASTER/UCOS-CEU-001/ceu-declaration.json`, `00-MASTER/UCOS-URR-001/urr-declaration.json`, and `00-MASTER/UCXI-000001/ucxi-declaration.json` have no Python reader and no gate.
- **Evidence.** No `.py` file mentions any of the three filenames; no `ceu-gate.yml`, `urr-gate.yml` or `ucxi-gate.yml` workflow exists. Two of the three (`ceu`, `ucxi`) are the only declarations that name a `schema` (`ucos-ceu-declaration`, `ucos-ucxi-declaration`) — a schema nothing validates against. The remaining 14 declarations are read and gated; `engine/infinite_scope/contract.py:53` is the reference shape, pinning `00-MASTER/UISD-000001/uisd-declaration.json` and failing closed at `:64-77` (*"a declaration that cannot be read is not a declaration that permits everything"*).
- **Current state.** 14 of 17 declarations bind execution; 3 do not.
- **Desired state.** Either read and gated, or declared advisory.
- **Impact.** The CEU declaration is the one that would most directly govern the defect surface in §4. It declares CEU's ownership, invariants and openness, and no validator consults it.
- **Dependency.** None.
- **Classification.** **PARTIALLY ASSIMILATED** — the mechanism is proven on 14 surfaces and absent on 3.

### 3.5 CR-04 — The canonical projection of the existence registry is implemented, verified, and never written

- **Finding.** `ExistenceRegistry` has a complete, lossless, journal-verifying document projection and loader. No document is ever written to disk.
- **Evidence.** `to_document` at `engine/ceu/existence.py:733` carries the whole journal, reasoned at `:726-728` (*"The whole journal, not just its head. Steering 022: Repository Truth must be sufficient to reconstruct constitutional state"*). `from_document` at `:773` replays verbatim and fails closed on `verify_audit()`. `reconstruct()` at `:868-890` turns losslessness into a measurement. Measured (M5): 195 units, 133 246 bytes, schema `ucos-constitutional-existence-registry`, round-trip digest identical, **and it works in a process that never called `bootstrap()`**. Measured (M7): zero committed JSON carries that schema. The only non-test constructor is `engine/ceu/catalog.py:404`.
- **Current state.** Reader, writer and losslessness proof all exist. The artifact does not.
- **Desired state.** A committed existence document read on the validation path.
- **Impact.** This single gap is the difference between the target architecture and the actual one. It is also why closure is cheap: **nothing needs inventing.**
- **Dependency.** None. This is the root of the dependency structure in §14.
- **Classification.** **NOT YET ASSIMILATED** — but the missing piece is a binding, not a capability.

---

## 4. Runtime Authority Analysis

Method: every module-level mutable container, `global` statement, caching decorator, singleton, registration side effect, temporary-file write, environment read, and nondeterminism source across `engine/ platform/ service/ application/ infrastructure/ intelligence/ realization/` was located and classified as **INTENDED RUNTIME PROJECTION** (cache or optimization only; the same truth remains reachable from committed knowledge), **ACCIDENTAL AUTHORITY** (a validation verdict depends on it and it is not derivable from committed data at the point of use), or **UNKNOWN**.

### 4.1 Headline result

The ambient mutable-state surface is remarkably small: **8 module-level mutable containers, 1 `global` statement, 1 `@cache`, 3 `@lru_cache`, ~18 `@cached_property`** across 1942 files. There is no `random`, no `uuid1`, no builtin `hash()` in a persisted value, and no wall-clock on a verdict path. The repository is disciplined about nondeterminism. **The defect is not nondeterminism. It is statefulness — and no existing guard tests for statefulness.**

### 4.2 Classification table

| Site | State | Class |
|---|---|---|
| `engine/registry/universal/identity.py:156,159` `_EXTENSION_KIND_CODES` / `_EXTENSION_CODE_KINDS` | empty at import; only mutator `register_kind` (`:162-199`); **no persistence writer anywhere** | **ACCIDENTAL AUTHORITY** |
| `engine/provider/selection.py:22` `_STRATEGIES` | **self-seeds at import** — measured 1 entry `['highest-version']` (`:87-88`); rebinding refused; no unregister | INTENDED RUNTIME PROJECTION |
| `engine/foundation/composition/ordering.py:55` `_STRATEGIES` | **self-seeds at import** — measured 2 entries `['dependency-order','parallel-waves']` (`:137-139`); rebinding refused | INTENDED RUNTIME PROJECTION |
| `engine/factory/phases.py:70` `_PHASES` | **self-seeds** via `engine/factory/orchestrator.py:340-349` — measured 8 entries; but `unregister_generation_phase` (`:103-108`) makes it **non-monotonic** | INTENDED PROJECTION, with a withdrawal path (CR-09) |
| `engine/nucleus/authority.py:66` `@cache roles_holding` | caches a pure function of committed seeds; **calls `bootstrap()` inside**, leaking the identity side effect, then suppressing it | INTENDED as a cache; **side-effect leak is the CR-06 vector** |
| `engine/foundation/obs/logging.py:114` `global _configured` | logging handler idempotency; no verdict reads it | INTENDED RUNTIME PROJECTION |
| `engine/constitution/stages.py:115-190` ~18 `@cached_property` | derived once per `Context`; reasoned at `:107-110`; sources are committed JSON + seed registry | INTENDED RUNTIME PROJECTION |
| `platform/repository_intelligence/*.py` `@lru_cache(maxsize=8)` on `load`/`_document` | pure projection of committed JSON keyed on repo path; does not invalidate mid-process | INTENDED, staleness caveat |
| `engine/execution_environment/fingerprint.py:99,152` `.ucos/environment-fingerprint.json` | explicit contract: may skip exactly one measurement, *"may never skip a verdict, never supply a check result, and never answer VALID on its own"*; EEG-01…05 always recomputed; invalidated by `bootstrap.sh` | INTENDED RUNTIME PROJECTION (reference-quality) |
| `engine/verification_intelligence/evidence.py:224` `NamedTemporaryFile` + `os.replace` | atomic cache write keyed on `input_digest`; fail-open by design | INTENDED RUNTIME PROJECTION |
| `engine/execution_environment/discovery.py:371` `os.environ.get("UCOS_VENV_DIR")` | redirects which venv is *declared*; the verdict anchors on `sys.prefix` | **UNKNOWN** |
| `00-MASTER/UAKOS-CLOSURE-002/closure_engine.py:73-74,176-183,344-353` | out-of-repo corpus path, `CLOSURE_SKIP_CORPUS` env gate, explicit reads of gitignored generated trees | **ACCIDENTAL AUTHORITY** (CR-10) |
| `engine/graph/evidence.py:67`, `engine/graph/architecture/evidence.py:78` `generated_at` | wall clock in a document alongside verdict fields; verdict derived from `validate()`, not the timestamp | INTENDED, determinism hazard if digested |
| `engine/registry/universal/audit.py:35` `utc_clock` | injectable `Clock`; deterministic `SequenceClock` alternative at `:38-50`; verdicts use `content_hash` | INTENDED RUNTIME PROJECTION |
| `engine/determinism/hermetic.py:211-221` `os.environ.update` | *removes* nondeterminism (`TZ=UTC`, `PYTHONHASHSEED=0`), restores prior values | INTENDED RUNTIME PROJECTION |

### 4.3 CR-05 — Validation truth is produced by runtime bootstrap, not read from canonical knowledge

- **Finding.** The chain that actually executes for 43 of 72 kinds is `Canonical Knowledge → Runtime Bootstrap → Mutable Module State → Validation Truth`. There is no deterministic resolver and no persisted projection between bootstrap and validation.
- **Evidence.** `engine/registry/universal/identity.py:156-159` (empty mutable globals); `:162-199` `register_kind` writes only to process memory; `:288-301` `parse_kind_name` reads them; `:303-309` `is_well_formed` wraps it. Population path: `engine/ceu/catalog.py:396 bootstrap()` → `engine/ceu/existence.py:356-370 declare_form` → `:898-910 _register_identity_kind` → `register_kind`. Measured M1/M2: 29→72 kinds, four probes flip `False`→`True`. Measured M6: construction raises in one process, succeeds in another. `existence.py:903-905` states the intent honestly — *"The authority owns the name→code mapping; this function never stores one."* The unaddressed consequence: the authority owns it in RAM, for one process lifetime.
- **Current state.** Ephemeral process state is the operative authority for 59.7% of the kind space.
- **Desired state.** `is_well_formed(id)` is a pure function of the identifier plus committed data, evaluable in a fresh interpreter with no prior call.
- **Impact.** Nine non-test enforcement sites inherit a non-deterministic predicate: `engine/constitution/gateway.py:203` (the single authorised mutation path — measured source at `:199-209`), `engine/nucleus/ownership.py:211,215` (NUC-INV-09), `engine/ceu/existence.py:345`, `engine/ceu/possessions.py:151`, `engine/context/location_assurance.py:175,285`, `engine/registry/universal/dictionary.py:57,209,221`, `engine/constitution/metadata.py:303`. The failure direction differs by site and both directions are wrong: `gateway.py:203` would *refuse a legitimate mutation*; `dictionary.py:221` would *report legitimate identifiers as unparseable*, flipping a governance verdict from PASS to FAIL for reasons unrelated to the data.
- **Dependency.** CR-04 (the projection exists and is unwritten), CR-01 (the vocabulary is source, not data).
- **Classification.** **NOT YET ASSIMILATED.**

### 4.4 CR-06 — The dependency crosses capability boundaries: an ownership question mutates an identity verdict

- **Finding.** The call that populates the identity kind space need not be an identity call. Asking `may_own_capability('nucleus')` — an ownership question — silently widens the identity grammar process-globally.
- **Evidence.** Measured (M3): import identity → 29 kinds, `False`; import `engine.nucleus.authority` → still 29, `False`; call `may_own_capability('nucleus')` → 72 kinds, `True`. Mechanism: `engine/nucleus/authority.py:66-76` `@cache roles_holding` calls `bootstrap()` at `:72`; `bootstrap()` constructs an `ExistenceRegistry`, whose `declare_form` calls `register_identifier_kind`. The `@cache` then *suppresses* the side effect on every subsequent call, so the widening happens exactly once and at an unpredictable point.
- **Current state.** Whether the constitutional mutation gateway can accept an extension-kind identity depends on whether some unrelated module asked an ownership question earlier in the same process. No reader of `gateway.py` can see this coupling.
- **Desired state.** No capability's runtime behaviour alters another capability's verdict. Side effects of caching are absent because there are none to cache.
- **Impact.** This is the finding that generalises the predecessor determination. The defect is not confined to identity: it is a property of the process, reachable from at least two unrelated capability surfaces, and invisible at every call site.
- **Dependency.** CR-05.
- **Classification.** **NOT YET ASSIMILATED.**

### 4.5 CR-07 — Constitutional legality inherits the defect by live call, not by stale data

- **Finding.** The constitutional legality proof consults a property that is a live invocation of the runtime-dependent predicate. This closes an edge the predecessor left open.
- **Evidence.** Measured source (M15), `engine/constitution/metadata.py:301-303` verbatim:
  ```python
  @property
  def identity_well_formed(self) -> bool:
      """True iff the universal identifier is one the identity authority could mint."""
      return is_well_formed(self.universal_id)
  ```
  `engine/constitution/legality.py:153-164` `_identity_complete` reads `record.identity_well_formed`. Measured flip: `False` in a fresh process, `True` after bootstrap. `engine/constitution/` does not import `is_well_formed` directly, which is why the propagation was previously unresolved — it propagates through a property on a dataclass.
- **Current state.** `prove(record, graph, population)` at `legality.py:372-403` is otherwise a clean pure function over passed arguments and an in-code `PROOFS` tuple; this single field makes its verdict process-dependent for extension-kind records.
- **Desired state.** Every input to a legality proof is a function of the record and committed knowledge.
- **Impact.** Constitutional legality — the surface that decides whether a mutation is lawful — is not process-independent. `legality.py:389-390` is explicit that *"an unevaluable proof is an unproven proof"*; it has no equivalent guard for a proof whose input silently changed value.
- **Dependency.** CR-05.
- **Classification.** **NOT YET ASSIMILATED.**

### 4.6 CR-08 — Registries that declare themselves canonical hold their truth only in process memory

- **Finding.** Six registries have no durable substrate. Three of them describe themselves as canonical or as Recorded Truth.
- **Evidence.**
  - identity extension space — no writer, no loader, no artifact (`identity.py:156,159`; M7).
  - `KnowledgeRegistry` (`engine/knowledge/ukip/registry.py:363`) — docstring: *"The **canonical**, duplication-proof registry of all knowledge (UKIP Part 06)."* Has `to_document()` at `:663` emitting to stdout; **no `from_document`**; no committed file carries schema `ucos-ukip-knowledge-registry`.
  - `IdentityRegistry` (`platform/foundation/durable_identity.py:257`) — docstring at `:275` calls the committed map *"Recorded Truth"*; `export()` at `:520` and `from_dict()` at `:539` are **dead outside tests**; no exported file exists. The retired-key set that guarantees "never reused" vanishes at process exit. `from_dict` re-mints rather than replaying — the opposite of `ExistenceRegistry.from_document`'s discipline.
  - `CapabilityRegistry` / `OwnershipRegistry` / `DependencyRegistry` / `AgentRegistry` (`platform/universal_control_plane/registry.py:35,78`) — `to_dict()` only, no loader, no artifact.
  - `NucleusRegistry` (`engine/nucleus/registry.py:73`) — `to_document()` at `:573`, **no `from_document`**; its only durable trace is the derived identifier dictionary, which carries identifiers but not roles, assignments, supersessions or vocabulary.
  - `ExistenceRegistry` — lowest risk of the six because the round trip is implemented and proven (M5), but still unwritten (M7).
- **Current state.** Of the registries examined, exactly one (`ArtifactRepository`, `engine/registry/artifacts.py:47-51`) reads its population from a committed data file, and exactly one (`IdentifierDictionary`) writes one.
- **Desired state.** Any registry that decides validity is reconstructible from a committed artifact, fail-closed on read.
- **Impact.** Truth that cannot be reloaded cannot be audited, diffed, replayed or certified. A determination that measured such a registry yesterday cannot re-verify it today except by re-running the same call sequence.
- **Dependency.** CR-04.
- **Classification.** **NOT YET ASSIMILATED.**

### 4.7 CR-09 — One runtime registry is non-monotonic

- **Finding.** `_PHASES` supports withdrawal, so the declared generation-phase graph can shrink within a process and produce a raise where it previously produced an order.
- **Evidence.** Measured (M4/M4b): fresh import yields 8 phases and `generation_order()` succeeds. After `unregister_generation_phase("classify")` (`engine/factory/phases.py:103-108`): `generation_order()` raises `GenerationPhaseError [FAC-PHASE-001] generation phase requires a phase that is not declared (phase='resolve-factory', missing=['classify'])`. `generation_stages()` at `:158-165` feeds what a factory advertises (`engine/factory/factories/base.py:104`). The module claims determinism at `:51` and `:66`.
- **Current state.** Self-seeding makes it benign in practice; the withdrawal path makes it unsound in principle. No verdict currently compares advertised stages against a declaration.
- **Desired state.** Either the phase graph is declared data, or withdrawal is removed, or the advertised set is measured against a declaration.
- **Impact.** Latent, not active. No measured verdict depends on it today.
- **Dependency.** None.
- **Classification.** **PARTIALLY ASSIMILATED.**

### 4.8 CR-10 — The habitually executed closure verdict is a function of environment and generated state

- **Finding.** The `CLOSED | concepts=549 | gaps=0` verdict produced at every session start is not a function of committed repository state alone. Its inputs include an environment variable, an out-of-repository directory, and gitignored generated trees. Its output is itself gitignored and untracked.
- **Evidence.** Measured (M12): `closure.json` reports `scan_mode='repo-only (declared)'`, `population_complete=True`, `determination='CLOSED'`, `gap_total=0`, `concept_total=549`, `sources.corpus_present=False`, `corpus_files=0`. `git check-ignore -v` → `.gitignore:59`; `git ls-files --error-unmatch` → *"did not match any file(s) known to git"*. Four separable runtime dependencies:
  1. **Environment variable.** `00-MASTER/UAKOS-CLOSURE-002/closure_engine.py:176-183` gates the corpus scan on `os.environ.get("CLOSURE_SKIP_CORPUS") == "1"`. `.kiro/hooks/uakos-closure-002.json` hardcodes it and pipes `2>/dev/null | grep UAKOS-CLOSURE-002`, discarding the `scan_mode` line and the `DISCLOSURE — POPULATION INCOMPLETE` stderr block.
  2. **Out-of-repository directory.** `closure_engine.py:73-74` — `CORPUS = REPO.parent / "UCOS"`, resolved by path arithmetic.
  3. **Gitignored generated trees.** `closure_engine.py:344-353` reads `knowledge/canonical-knowledge.json`, `knowledge/decisions.json` and `knowledge/handbooks/**` with the comment *"authoritative Repository Truth even though it is git-ignored"*. `_ukda_hash_dups()` at `:484-497` returns `[]` — reporting *zero duplicates* rather than *unmeasured* — when the store is absent.
  4. **Its own prior output.** `closure.json` is regenerated each session and is the declared `population_document` consumed by the single-click entry point (`closure_engine.py:234-235`; `platform/universal_foundation/service.py:221-227`).

  The repository records the counter-measurement itself. `00-MASTER/MIP-W1-P001/20-WAVE-1-COMPLETION-REPORT.md:125`: *"437/0-gap → **528/91-gap** when the corpus is scanned"*, method *"re-ran the identical engine without `CLOSURE_SKIP_CORPUS=1`"*. Corroborated at `01-EXECUTIVE-SUMMARY.md:58`, `04-KNOWLEDGE-ASSIMILATION-REPORT.md:169`, `16-GAP-ANALYSIS.md:81-86`.

  The engine is honest about the epistemics and deliberately excludes them from the verdict, `closure_engine.py:456-460`: *"Recorded ALONGSIDE the determination and deliberately not folded into it: `closed` above remains the same pure function of the discovered population."* The `--require-complete-population` flag exists at `:740,766-773` and neither the hook nor `make closure-gate` passes it.
- **Current state.** `closed` is a pure function of the *discovered* population; the discovered population is not a pure function of the committed repository. This is `RTBD-001`'s boundary crossed in the reverse direction — a generated product feeding a verdict about Repository Truth.
- **Desired state.** A closure verdict computed over a declared, committed population, with incompleteness blocking or explicitly disclosed in the surfaced line.
- **Impact.** The most frequently surfaced determination in the repository is the least anchored to committed knowledge. This is the clearest non-identity instance of runtime state becoming an authority.
- **Dependency.** `scripts/generate-prerequisites.sh` (CR-13); owner decision recorded as pending at `closure_engine.py:456-460` (AB-6).
- **Classification.** **NOT YET ASSIMILATED.**

### 4.9 CR-11 — What is correctly done: the nondeterminism discipline

- **Finding.** The classic nondeterminism sources are absent from verdict paths, and the exclusions are actively guarded.
- **Evidence.** No `random`, `uuid1`, `time.time()`, or builtin `hash()` in any persisted or compared value. Injectable clock with a deterministic alternative (`engine/registry/universal/audit.py:30,38-50`). Hermetic environment that pins `TZ=UTC` and `PYTHONHASHSEED=0` and restores prior values (`engine/determinism/hermetic.py:211-221`). AST-level guards banning clock and RNG constructs in specific modules: `engine/tests/unit/test_temporal_contract.py:113-118` (*"A now()/utcnow() here would make every coordinate unreplayable"*), `engine/tests/unit/test_closure009_requirement_engine.py:183`, `platform/tests/test_universal_project_state.py:672`. `engine/uicm/validation.py:57` `_FORBIDDEN_MINTS` bans mint calls. Measured (M10): digests identical across four `PYTHONHASHSEED` values.
- **Current state.** Nondeterminism is measured and guarded. **Statefulness is neither.** The guards are scoped to named modules and test for forbidden *constructs*, not for dependence on prior *calls*.
- **Desired state.** The same discipline extended to process state as a named nondeterminism source.
- **Impact.** Explains how the defect drifted in undetected: it is invisible to every guard the repository built, because it is not the kind of defect those guards look for. `engine/registry/universal/identity.py:14-15` names three nondeterminism sources — *"no wall-clock, RNG, or network on the determined path"* — and mutable module state is an unnamed fourth.
- **Dependency.** None.
- **Classification.** **ASSIMILATED** for clock/RNG/network; the gap is the fourth source, recorded as CR-05.

---

## 5. Deterministic Execution Assessment

Test: does *same input + same canonical repository state → same result* hold across a fresh process, an initialized process, different import order, and different execution order?

### 5.1 Measured results

| Variation | Measured | Result |
|---|---|---|
| **Different `PYTHONHASHSEED`** (0, 1, 42, 12345) | M10 | **STABLE.** `ceu_digest=b68559b7b416955d`, `nucleus_digest=46506f2287012463`, `kinds=72`, `own=True` — identical in all four |
| **Different import order** (identity-first vs ceu-first) | M11 | **STABLE.** Both 72 kinds / 43 extension |
| **Repeated initialization** (two `bootstrap()` calls) | M11b | **STABLE.** 72/43; `digest_a == digest_b` |
| **Fresh vs initialized process** | M1 vs M2 | **NOT STABLE.** 29 vs 72 kinds; four probes flip `False`→`True` |
| **Different execution order** (identity question before vs after an unrelated ownership call) | M3 | **NOT STABLE.** `False` before, `True` after |
| **Object construction in fresh vs initialized process** | M6 | **NOT STABLE.** Raises vs succeeds |

**Determination: PARTIALLY DETERMINISTIC.** The system is robust against every classical nondeterminism axis and fragile against exactly one: **call history.**

### 5.2 Surface-level classification

| Surface | Depends only on input + committed data? | Classification |
|---|---|---|
| `parse_kind` (core kinds only, `identity.py:274-286`) | yes — reads `_CODE_KINDS`, built at import from the enum | deterministic |
| `parse_kind_name` / `is_well_formed` (`identity.py:288-309`) | **no** — reads runtime-mutated globals | **runtime dependent** |
| `deterministic_id` minting | yes for 29 core kinds; extension kinds need `resolve_kind_code` (`identity.py:206-213`) | partially deterministic |
| `dictionary.unparsed()` / `verify()["status"]` (`dictionary.py:219-258`) | **no** — inherits `is_well_formed` | **runtime dependent** |
| `IdentifierEntry.__post_init__` (`dictionary.py:57`) | **no** — measured raise/accept flip (M6) | **runtime dependent** |
| `ConstitutionalMetadata.identity_well_formed` (`metadata.py:301-303`) | **no** — live call (M15) | **runtime dependent** |
| `engine/uckp/identity.py` URN plane | yes — pure, no registry consulted | deterministic |
| `engine/kernel/identity.py` UMK plane | yes — regex + digest | deterministic |
| `engine/uckp/alignment.py repository_local_urn` | yes — compiled regex constant | deterministic |
| `engine/validation/` EC-1 checks (`checks.py`, `executor.py`, `gates.py`) | **yes, exactly** — frozen `ValidationSubject` + one regex at `checks.py:31` | deterministic |
| `engine/graph/validation.py validate_graph` | yes — in-code regex `:36-39`; does not call `is_well_formed` | deterministic |
| `engine/object_birth/gate.py measure` | yes — declaration + ledger + policy + context files | deterministic |
| `engine/runtime/execution/lifecycle.py` transitions | yes — module constant table `:39`, no writer | deterministic |
| `engine/temporal/coordinate.py` | yes — frozen dataclasses; no clock reference in file | deterministic |
| `engine/nucleus/authority.py` ownership | yes across processes (M10) — but **not runtime-extensible** (M9) | deterministic, code-bound |
| `00-MASTER/UAKOS-CLOSURE-002/closure_engine.py` | **no** — env var + out-of-repo path + gitignored trees | **runtime dependent** |

### 5.3 CR-12 — The determinism instrumentation cannot observe this defect class, and the two gates that come closest still cannot

This is the finding the directive asks to be stated explicitly.

- **Finding.** The repository has extensive determinism instrumentation. **Two of twenty-nine gates compare verdicts across separate processes.** Both prove *same invocation sequence + same execution path = same result*. Neither proves *different initialization history = same truth value*. Therefore neither can detect runtime-state-dependent truth.
- **Evidence.**
  - **UAUE gate.** `.github/workflows/uaue-gate.yml:188-199`, verbatim comment: *"Two independent processes, not two calls in one process. An in-process replay could pass on a memoised result; a cross-process replay cannot, which is the only form of the claim that is worth making about an artifact meant to survive the process that wrote it."* The step runs:
    ```
    python3 -m engine.uaue.gate --quiet --json > /tmp/uaue-run-a.json
    python3 -m engine.uaue.gate --quiet --json > /tmp/uaue-run-b.json
    diff -q /tmp/uaue-run-a.json /tmp/uaue-run-b.json
    ```
  - **UISD gate.** `.github/workflows/uisd-gate.yml:231-241`, same shape, plus a working-tree comparison before and after: *"UISD-000001: two processes, one report, zero surfaces moved."*
  - **The limitation.** In both cases run A and run B are invocations of the **same entry point** with the **same arguments**, so both execute the **same call sequence** and therefore reach the **same initialization state**. Run A and run B inherit identical module globals. A verdict that depends on whether `bootstrap()` ran will be *equally wrong in both runs* and the `diff` will pass. The measurement is cross-process **reproducibility of one path**; it is not cross-process **independence from initialization history**.
  - **Everything else measures less.** The `--check-determinism` self-guards in `aee-gate.yml:81-82`, `baseline-gate.yml:55-56`, `mcos-gate.yml:61-62`, `rib-gate.yml:59-60`, `rfp-gate.yml:70-71`, `uaep-gate.yml:73-74`, `uaie-gate.yml:87-88`, `uar-gate.yml`, `acee-gate.yml` all compare **two renders inside one process**. `determinism.yml:48-50` invokes `engine.determinism.reproduce`, whose `double_build` (`engine/determinism/reproduce.py:283-320`, measured M19) runs both builds **in one interpreter sharing one `env`, one `document`, one `adapter` and one `signer`**; isolation amounts to `with env.apply():` plus a distinct output directory. A validator whose verdict depends on a populated module global produces identical bytes in build A and build B because both inherit the same populated dict.
  - `grep -rn 'process-independen'` across `engine/ platform/ .github/` returns **zero hits**.
- **Current state.** Zero of twenty-nine gates, and zero tests, require verdict equality across two processes with **different** initialization histories. Zero tests observe the pre-bootstrap state at all: every CEU assertion operates on a registry returned by `bootstrap()`, and the two `unparsed() == []` assertions run in bootstrapped nucleus fixtures. `grep autouse=True` across all 15 `engine/tests/**/conftest.py` returns zero results, so the extension space at test time is whatever imports happened to populate — an undeclared baseline.
- **Desired state.** A measurement analogous to `double_build` but at the **process boundary and across differing call orders**: invoke a validator in two fresh interpreters, one with and one without the initialization call, and require verdict equality.
- **Impact.** The property is unguarded and can regress further, silently. A green test run and a green gate run are not evidence that validity is process-independent — they are evidence that everything runs in the same process state. This is the mechanism by which the defect drifted without detection, and it is why `GATE-PURITY-DETERMINATION`'s remediation would not close it: that determination audits **write** purity (D-3.0: *"The repository does not lack write discipline — it lacks a declared mode"*), and all five of its D-3.5 acceptance criteria concern writes. Adopting all five would leave `is_well_formed` exactly as process-dependent as it is today.
- **Dependency.** None. The UAUE two-process step is the correct pattern to extend; the missing element is *varying the initialization history between the two runs*.
- **Classification.** **PARTIALLY ASSIMILATED** — cross-process comparison exists on 2 of 29 surfaces; initialization independence is measured nowhere.


---

## 6. Bootstrap Dependency Assessment

Test: are `bootstrap()`, `initialize()`, `load()`, `register()`, `discover()` and `hydrate()` functions **(A) performance helpers** or **(B) truth-producing authorities**?

A function is a **truth-producing authority** if, without calling it, some validation or decision path returns a different (wrong) answer, raises, or reports different state. It is a **performance helper** if skipping it only costs time and the same truth remains reachable from committed knowledge.

### 6.1 Structural finding: bootstrap in UCOS is call-graph-driven, not import-driven

A scan of every non-test `__init__.py` under `engine/` and `platform/` for top-level invocations returned **zero matches**. No package performs registration or population at import time. The only import-time mutable state is the five containers in §4.2, of which three self-seed (measured M4) and one — the identity extension space — does not.

This is why the defect is a *call* dependency rather than an *import* dependency, and why it is harder to detect: import order is statically analysable; call order is not. No linter, type checker or import graph can observe that a validator was consulted too early.

### 6.2 Classification

| Function | Location | State it creates | Where the state lives | Class |
|---|---|---|---|---|
| `bootstrap(registry=None)` | `engine/ceu/catalog.py:396` | 6 ordered registration steps over 17 `SEED_*` populations | **returned `ExistenceRegistry`** — plus, as a side effect, the identity module globals | **B** |
| `ExistenceRegistry._bootstrap(root_code)` | `engine/ceu/existence.py:268` (from `__init__` at `:264`) | root form registered as a unit of itself | instance state | **B** |
| `ExistenceRegistry.from_document(doc)` | `engine/ceu/existence.py:773` | full registry + kind space, verbatim replay, journal-verified | returned registry + identity globals | **B — and the only one that reads committed knowledge** (M5) |
| `roles_holding(faculty)` | `engine/nucleus/authority.py:66` `@cache` | memoised frozenset over a private `bootstrap()` | process cache | **A as a cache**, over a **B** answer, with a leaking side effect (CR-06) |
| `register_kind(kind, code)` | `engine/registry/universal/identity.py:162` | name↔code allocation | **module globals, never persisted** | **B** |
| `register_conversions(registry)` | `engine/ceu/catalog.py:476` | unit conversions | passed registry | **optional authority** — `KeyError` if step 6 skipped; deliberately not a bootstrap step |
| `build_seed_base()` | `engine/knowledge/seed.py:56` | *"the founding canonical knowledge base (authored exactly once)"* | returned base, then persisted to `knowledge/` | **B** |
| `build_seed_registry()` | `engine/nucleus/registry.py:594` | nucleus population from hardcoded tuples | returned registry | **B** |
| `require_reality_context(...)` | `engine/context/location.py:710` | nothing (raises) | — | **B** — *"measurement, validation, governance, certification and execution each call this before they read a value"* |
| `register_resolution(...)` | `engine/context/location.py:738` | resolved axis + audit chain | passed registry | **B** — *"This is what makes a resolved axis Repository Truth rather than a computation"* |
| `load_declaration` / `load_contract` / `load_policy` (17 sites) | `engine/infinite_scope/contract.py:61,79`; `engine/object_birth/contract.py:49,67`; `engine/root_ontology/contract.py:41,58`; `engine/verification_intelligence/constitution.py:263`; `engine/registry_coverage/matrix.py:156`; and others | declaration objects from committed JSON | returned objects | **B — correctly so.** The declarations *are* the truth; the loader is the only path to it |
| `discover_*` (8 dimensions) | `engine/discovery/dimensions.py:85,166,214,259,313,391,439,498` | coverage verdict | returned `DimensionResult` | **B, deterministic.** Docstring: *"no regex over paths or content, no `glob`/`fnmatch`, no filesystem walking… The registry is the single source of truth (INV-13)"*; ordering stabilised (`:106 sorted(...)`) |
| `discover(*roots)` | `engine/uckp/registry.py:307` | import-graph scan, **mutates `self`** | instance | **B, environment-dependent.** Import failures are *recorded*, not raised — a missing optional dependency yields a smaller admitted universe with no exception |
| `discover_repo_root(start)` | `platform/coverage/repository.py:141` | walks *up* the filesystem | — | **UNKNOWN.** `verify.sh:100-102` records this class of bug occurring: *"a root misresolution once built a venv in the parent directory and nothing noticed for sixteen days"* |
| `fingerprint.load()` / `store()` | `engine/execution_environment/fingerprint.py:99,152` | `.ucos/environment-fingerprint.json` | gitignored file | **A — reference quality.** *"It may skip exactly one measurement… It may never skip a verdict, never supply a check result, and never answer VALID on its own"*; EEG-01…05 always recomputed |
| `bootstrap_assimilation()` | `platform/universal_assimilation/bootstrap.py:29` | adapters + kind registry + truth policy from in-code defaults | returned composition | **A — no I/O** |
| `scripts/generate-prerequisites.sh` | root script, invoked at `verify.sh:344` | `knowledge/`, `determinism-evidence/`, `00-MASTER/UAKOS-CLOSURE-002/*` | **files on disk (gitignored)** | **B — the strongest in the repository** (CR-13) |
| `ucos_ensure_venv` | `scripts/ucos-env.sh:281` | `.ec1-venv/` | filesystem | **A** — deliberately removed from the verification path (`verify.sh:84-124`) |
| `build_parser()` (×10), `build_*_service()` (~20), `build_traceability`/`build_canonical_*` (~60) | `engine/*/cli.py`, `platform/*/service.py`, `application/`, `service/` | argparse / DI wiring / deterministic projections | returned objects | **A** |

### 6.3 CR-13 — Validation depends on a generation step that nothing used to run, and the repository has already diagnosed it

- **Finding.** Five constitutional gate engines resolve declared references into trees that only `scripts/generate-prerequisites.sh` produces. That script's own header documents the failure mode and quantifies it.
- **Evidence.** `scripts/generate-prerequisites.sh:9-31`, verbatim: *"Nothing ran them. The exclusion asserted a regeneration no entry point performed, so every consumer read them only by accident of local residue. Measured consequences on a clean checkout of 404568e: 51 of 10201 tests failed, and five constitutional gate engines reported a declared reference as unresolvable"* — one being *"UCL-000001 REC-KNOWLEDGE: record owner does not resolve: knowledge/canonical-knowledge.json"*. Lines 44-53: *"Running `init` alone leaves the store at 11 and the handbooks unwritten, so every consumer measured a store truncated to 9% of itself… That made register content depend on WHICH generation steps had been run rather than on repository state alone, which is drift by definition."* Ordering at `:55-63`. `verify.sh:341-342`: *"This stage MUST precede the pytest stage: a prerequisite generated after the gate that consumes it is not a prerequisite."*
- **Current state.** The order constraint is real, documented, and enforced only by shell comment and stage sequencing.
- **Desired state.** Gates resolve declared references against committed knowledge, or the generated prerequisite is itself declared and its absence is a FAULT rather than a silent smaller measurement.
- **Impact.** This is the same defect shape as CR-05 at repository scale rather than process scale: truth reconstructed by execution instead of read from a declaration. The repository's own phrase for it — *"drift by definition"* — is the correct characterisation.
- **Dependency.** CR-10 depends on this.
- **Classification.** **PARTIALLY ASSIMILATED** — the dependency is now declared, ordered and executed; the underlying pattern (verdict over regenerated state) is unchanged.

### 6.4 CR-14 — The reference-quality bootstrap contract already exists

- **Finding.** One initialization helper carries exactly the contract the target architecture requires, and states it explicitly.
- **Evidence.** `engine/execution_environment/fingerprint.py` — the cache *"may skip exactly one measurement: EEG-06's scan… It may never skip a verdict, never supply a check result, and never answer VALID on its own — a hit supplies the previous scan's observed tool records and every check is then computed over them exactly as it would have been over a fresh scan."* And: *"EEG-01 through EEG-05 are recomputed on EVERY invocation regardless of cache state."* Invalidated on install by `scripts/ucos-env.sh:437` (`rm -f .ucos/environment-fingerprint.json`) and forced full rescan by `bootstrap.sh` (`--refresh`, reasoned at `:35-42`).
- **Current state.** One surface distinguishes *projection* from *authority* in its contract, and enforces the distinction.
- **Desired state.** The same contract shape applied to `bootstrap()` and `register_kind`.
- **Impact.** Establishes that no new concept is required — the boundary is already articulated and honoured once.
- **Dependency.** None.
- **Classification.** **ASSIMILATED** for this surface.

---

## 7. Registry Authority Assessment

Test: is each registry **(A) a canonical source**, **(B) a runtime memory projection**, or **(C) mixed**?

| Registry | Population source | Persistence writer (called by non-test code?) | Loader | Committed artifact | Verdict consults | Mutability | Class |
|---|---|---|---|---|---|---|---|
| **Artifact** — `ArtifactRepository`, `engine/registry/artifacts.py:26` | `from_source()` reads committed `00-BOOK/DATA/artifacts.json` | none | `from_source` + `Artifact.from_dict` (`:47-51`) | **YES** (frozen corpus) | the committed file | immutable after construction | **B — the model case** |
| **Identity: kind space** — `identity.py:156,159` | runtime `register_kind()` | **none** | **none** | **none** | in-memory globals; measured flip M1/M2/M6 | append-only, collision-refusing, **process-global** | **Canonical authority held only in process memory** |
| **Identity: dictionary** — `IdentifierDictionary`, `dictionary.py:116` | `dictionary_for(registry)` | `to_document()` → **YES**, `engine/nucleus/cli.py:169-187`; `engine/constitution/stages.py:687` | `from_document()` `:280` | **YES** — `00-MASTER/UCOS-NUCLEUS-001/UCOS-NUCLEUS-IDENTIFIER-DICTIONARY.json` | committed bytes vs fresh re-projection | append-only, refuses re-binding | **B — the one fully persisted, round-trip-proven projection** |
| **Identity: durable** — `IdentityRegistry`, `platform/foundation/durable_identity.py:257` | runtime `prepare/commit/mint/adopt` | `export()` `:520` — **dead outside tests** | `from_dict()` `:539` — **re-mints rather than replays** | **none found** | in-memory maps | append-only; retired keys never re-minted | **Canonical authority held only in process memory** |
| **Capability** — `engine/registry/universal/registries.py:140`; `platform/universal_control_plane/registry.py:35` | runtime `register()` | `to_dict()` on the UCP variant `:64`; `TypedRegistry` has none | none | none | in-memory dicts | append-only, duplicate-refusing | **Canonical in process memory** |
| **Ownership: gate** — `engine/nucleus/ownership.py` | reads a passed `NucleusRegistry` | `OwnershipReport.to_dict()` → stdout via `cli.py:72` | none | none | in-memory registry rebuilt fresh per invocation | stateless | **B — derived verdict** |
| **Ownership: substrate** — `NucleusRegistry`, `engine/nucleus/registry.py:73` | `seed_subjects()` / `seed_capabilities()` — hardcoded tuples in `engine/nucleus/catalog.py:58,109,483` | `to_document()` `:573` — stdout only | **no `from_document`** | none | in-memory | append-only; ownership moves by supersession | **A — canonical, source of truth is Python code** |
| **Ownership: UCP** — `platform/universal_control_plane/registry.py:78` | runtime `register()` | `to_dict()` `:216` | none | none | in-memory | one owner per capability enforced | **Canonical in process memory** |
| **Knowledge** — `KnowledgeRegistry`, `engine/knowledge/ukip/registry.py:363` | constructor records + runtime `submit()` | `to_document()` `:663` → stdout / evidence bundle | **none** | **none** (no file carries `ucos-ukip-knowledge-registry`) | in-memory records | append-only; duplicate home refused | **A — self-declared *canonical*, no durable substrate** |
| **Certification** — `engine/certification/ledger.py`; `platform/universal_assurance/registry.py:173`; `platform/certification/registry.py:51` | runtime `append`/`register` | `to_dict()` only — *"persistence, if any, is the caller's concern via `to_dict`"* (`ledger.py:11-14`) | constructor `entries` argument | `00-BOOK/DATA/certification.json` exists but is a **different producer's** verdict document | in-memory hash chain, `require_intact()` | append-only, hash-chained | **C — mixed** |
| **CEU existence** — `ExistenceRegistry`, `engine/ceu/existence.py:239` | `_bootstrap()` + `register()`; only non-test constructor is `catalog.py:404` | `to_document()` `:733` — never written to a file | **`from_document()` `:773` — verbatim, journal-verifying** | **none** (M7) | in-memory units + audit chain | append-only; supersede/resurrect append snapshots | **A — canonical, round trip proven (M5), artifact absent (M7)** |
| **Registry coverage** — `engine/registry_coverage/matrix.py` | `declarations.json` + filesystem scan + each declared plane's JSON | `rendered()`/`digest()` — pure, no file write | `load_declarations()` `:156` | inputs all committed | committed artifacts only | not a store | **B — self-declared** |

### 7.1 CR-15 — The registry layer is inverted: derived surfaces are rigorous, canonical surfaces are ephemeral

- **Finding.** Of the twelve registries examined, exactly **one** reads its population from a committed data file and exactly **one** writes a committed data file. Every registry that self-declares *derived* is disciplined; several that hold actual truth have no durable substrate.
- **Evidence.** `ArtifactRepository.from_source` (`engine/registry/artifacts.py:47-51`) is the sole committed-file reader. `engine/nucleus/cli.py:185` is the only registry-document writer in `engine/` that touches the filesystem. The derived layer's discipline is genuine: `engine/registry_coverage/matrix.py:294-299` declares *"authority": "NONE — DERIVED COVERAGE INTELLIGENCE. It registers nothing, owns nothing and mints nothing… Deleting it changes no registration and no verdict."* and its module docstring adds *"A matrix that kept its own copy would be the duplicate-catalogue defect it exists to detect — the 141st registry."* `verify()` builds twice and compares `rendered()` and `digest()` — determinism measured, not assumed.
- **Current state.** Truth-holding registries are Python tuples or process memory; truth-describing registries are committed and verified.
- **Desired state.** Symmetry — anything that decides validity is reconstructible from a committed artifact.
- **Impact.** A structural blind spot follows: the coverage matrix judges **files**, so a registry that lives only in process memory is **invisible to it** and can never be reported as unregistered. The instrument built to detect unregistered objects cannot see the objects most at risk.
- **Dependency.** CR-04, CR-08.
- **Classification.** **PARTIALLY ASSIMILATED.**

### 7.2 CR-16 — Round-trip determinism is proven on two registries and absent on the rest

- **Finding.** Two of twelve registries have both directions and prove losslessness. One of those two proves it by re-derivation rather than replay, which is the weaker discipline.
- **Evidence.** `IdentifierDictionary`: `test_two_generations_are_byte_identical`, `test_the_digest_matches_the_regenerated_projection` (`_committed()["digest"] == dictionary_for(registry).digest()`), `test_every_committed_entry_re_mints_from_its_own_tuple`, `test_a_mutated_entry_is_detected` — all in `engine/tests/nucleus/test_identifier_dictionary_persistence.py:200-215`. Measured (M8): the committed dictionary replays in a fresh process, `verify status=PASS`, `unparsed=0`, `parse_coverage=1.0`, 212 entries. `ExistenceRegistry`: `reconstruct()` (`existence.py:868-890`) measures `registry.digest() == rebuilt.digest()`; measured identical (M5). By contrast `IdentityRegistry.from_dict` (`durable_identity.py:539-563`) calls `mint()`/`adopt()` — a re-derivation, which `ExistenceRegistry.from_document` explicitly refuses: *"Re-deriving would let the rebuilt registry differ from the recorded one and still look healthy."*
- **Current state.** The correct discipline exists and is articulated; coverage is 2 of 12.
- **Desired state.** Fail-closed verbatim replay wherever a registry is reloadable.
- **Impact.** Bounded honestly: the committed dictionary uses **only core codes** — measured `CAP`, `CMPO`, `LYR`, `NUC` — so its verdict is process-independent **today**. The exposure is latent: it is a projection of `deterministic_id` entries, so populating it from the CEU registry would make its PASS/FAIL verdict process-dependent.
- **Dependency.** CR-05.
- **Classification.** **PARTIALLY ASSIMILATED.**

---

## 8. Validation Truth Assessment

Test: for each validation surface, is the verdict a pure function of `(input + committed repository state)`?

### 8.1 Three families

Validation in UCOS Ω∞ divides cleanly:

1. **Pure over a passed subject.** `engine/validation/` (EC-1), `engine/graph/validation.py`, `engine/certification/criteria.py`, `engine/universal_certification/rules.py`, `engine/constitution/legality.py`, `engine/context/validation.py`, `engine/runtime/execution/lifecycle.py`. Verdict = `f(frozen subject, in-code constants)`. Deterministic. The canonical knowledge is source code, and the *input's* provenance is where dependence hides.
2. **File-backed declaration plus repository scan.** `engine/object_birth/gate.py`, `engine/infinite_scope/gate.py`, `engine/verification_intelligence/gate.py`. Verdict = `f(declaration JSON, filesystem state)`. This is the closest the repository gets to canonical derivation. Caveat: they read the **working tree**, not `git show HEAD`.
3. **Runtime-registry driven.** CEU entity, CEU relationship, nucleus capability, identity. Verdict = `f(process history)`. This is the defect family.

### 8.2 The reference implementation

`engine/validation/` is the only package that both **declares** purity and structurally **has** it. `engine/validation/checks.py:8-11`, verbatim:

> *"Checks are pure functions of the subject — no secrets, no registry access, no wall-clock — so identical subjects yield identical findings."*

The claim is true as written. Seven checks (`checks.py:66-206`) read only fields off a frozen `ValidationSubject` (`contracts.py:139-198`, `@dataclass(frozen=True, slots=True)`); `ValidationEngine.validate` sorts checks by id for deterministic ordering (`executor.py:38-40`); `enforce_acceptance` (`gates.py:48-73`) is pure over the report. No import from `engine.registry.universal.identity` anywhere in the package.

`engine/object_birth/gate.py:16-20` is the best file-backed shape: *"Read-only and hermetic: it loads the declaration and the ledger, computes, and writes nothing. No clock, no network, no subprocess."* It also distinguishes FAULT (exit 2) from CLOSED (exit 1) at `:41-43`, so an unreadable declaration cannot masquerade as a pass.

### 8.3 CR-17 — Three independent identifier grammars exist, and only the stateful one is authoritative

- **Finding.** Three unrelated regimes decide whether a string is an acceptable identifier. They can disagree about the same string. Only the authority's own grammar is process-dependent — which is why the other two are accidentally immune.
- **Evidence.**
  - `engine/registry/universal/identity.py:288-301` — the authority; consults `_CODE_KINDS` and the runtime-mutated `_EXTENSION_CODE_KINDS`; docstring claims *"This is the total parser: it resolves every identifier this authority can mint."*
  - `engine/graph/validation.py:36-39` — `_IMMUTABLE_ID = re.compile(r"^(UCOS-[A-Z0-9]+-\d+|UEDGE-\d+|USIG-\d+|VOL-\d+|…)$")`. Note it matches `UCOS-<CODE>-<digits>` whereas the authority mints `UCOS-<CODE>-<12 hex>`: a minted id whose digest is all-digits passes, one containing `a`–`f` does not.
  - `engine/validation/checks.py:31` — `_RUNTIME_ID = re.compile(r"^UCOS-RUN-.+-[0-9a-f]{16}$")`.
- **Current state.** One authority, two independent re-implementations, no reconciliation.
- **Desired state.** One declared shape authority, or an explicit declaration that the populations are disjoint.
- **Impact.** The two re-implementations are deterministic **because** they bypass the authority. Their immunity is accidental, not designed, and it means a future consolidation onto the authority would *propagate* the defect to two currently-clean surfaces.
- **Dependency.** CR-05.
- **Classification.** **NOT YET ASSIMILATED.**

### 8.4 CR-18 — Certification validation is structurally pure and structurally unable to detect the defect

- **Finding.** Certification is a re-aggregation of upstream verdicts. It is exactly as canonical as whatever produced its subject, and it cannot observe a runtime-dependent upstream verdict — only relay it.
- **Evidence.** `engine/certification/criteria.py:35-66` defines an abstract `evaluate(self, subject: CertificationSubject)`; `ValidationAcceptedCriterion` (`:68-83`) reads `subject.validation_accepted` / `subject.validation_verdict`; `ValidationEvidencePresentCriterion` (`:85-96`) reads `subject.evidence_present` / `subject.evidence_sha256`. `engine/universal_certification/rules.py:35-226` is the same architecture with 10 rules including `RepositoryTruthConsistentRule` (`:150`). No identity import, no module globals, no bootstrap.
- **Current state.** Pure over its subject; blind to its subject's provenance.
- **Desired state.** Certification either verifies the provenance discipline of its inputs or declares that it does not.
- **Impact.** `validation-accepted` is true because someone else said so. A certification issued in a bootstrapped process over a verdict that would differ in a fresh one is internally consistent and externally wrong, with no surface reporting the difference.
- **Dependency.** CR-05, CR-12.
- **Classification.** **PARTIALLY ASSIMILATED.**

### 8.5 CR-19 — Security validation has no knowledge source to consult

- **Finding.** There is no executable security or permission validator. The question "canonical knowledge or runtime state" does not arise because neither is present.
- **Evidence.** `14-SECURITY/` contains only prose (`SECURITY-001-UNIVERSAL-SECURITY-CONSTITUTION.md` … `SECURITY-004-…-TAXONOMY.md`, `SECURITY-GOV-000-…`). The only authorization code is `engine/runtime/execution/authorization.py:61`: `def authorize(composition: RuntimeComposition, *, subject: str = "engineering") -> Authorization:` — no permission table, no role registry, no policy file; the subject is a hardcoded default string. `require_authorization` at `:96`. Separately, `grep -rniE 'trust|authenticat|authoriz|security|signature' platform/universal_assimilation/*.py` returns **zero matches**, and `require_trusted` has exactly one non-test caller outside its own module (`platform/foundation/admission.py:398`, authority migration — not content admission).
- **Current state.** An authorization function whose subject defaults to a literal grants by construction.
- **Desired state.** A declared policy surface that authorization reads.
- **Impact.** Security is absent, not deferred. This is a gap in a different axis from the rest of this determination and is recorded rather than assessed.
- **Dependency.** None located. `02-CANONICAL-OWNERSHIP-MATRIX.md` records no security owner, and the declared owner (`PHASE-008 SECURITY`) is constitutionally non-enacting.
- **Classification.** **NOT YET ASSIMILATED.**

### 8.6 CR-20 — Requirement validation lives outside the engine and computes its verdict against a surface it just rewrote

- **Finding.** No requirement validator exists under `engine/`. The operative one writes before it measures.
- **Evidence.** `grep requirement` across `engine/` returns only incidental mentions. The validator is `00-MASTER/UAKOS-CLOSURE-009/requirement_engine.py`, invoked by `.github/workflows/closure009-gate.yml:84` (`--gate`). `GATE-PURITY-DETERMINATION.md` §2.4 GP-3 records an unconditional write at `requirement_engine.py:1753-1760`, *"evaluated before the baseline verdict"*. §3 of that determination states the consequence plainly: *"A gate that writes before it compares can only compare a file against itself."*
- **Current state.** Verdict computed over self-rewritten state; knowledge source not established by this determination.
- **Desired state.** Requirement validity derived from a declared requirement universe, measured before any write.
- **Impact.** Same shape as CR-10 and CR-13 — a verdict about state, computed after mutating that state.
- **Dependency.** `GATE-PURITY` findings GP-1/GP-3, blocked on owner decision `H-06` / `CR-09` per that determination.
- **Classification.** **UNKNOWN** — the write-ordering defect is located; the knowledge source is not.

---

## 9. Capability-by-Capability Assessment

The ten domains the directive names, each assessed against the single question: **is the verdict a pure function of input plus committed repository state?**

| # | Domain | Primary validator | Knowledge consulted | Calls `is_well_formed`? | Needs prior bootstrap? | Reads mutable globals? | Verdict = f(input + committed)? | Classification |
|---|---|---|---|---|---|---|---|---|
| 1 | **Identity** | `identity.py:288-309`; `dictionary.py:57,209,221,239-258` | `_CODE_KINDS` (import) + `_EXTENSION_CODE_KINDS` (runtime) | is the source | **yes** | **yes** | **NO** — measured M1/M2/M6 | **NOT YET ASSIMILATED** |
| 2 | **Entity** | CEU: `existence.py:291,333` `register`/`_admit` — RUNTIME. Birth: `object_birth/gate.py:45-95` — CANONICAL | CEU: `self._units` (`:251`) + seed tuples. Birth: declaration + ledger + policy + context files | CEU **yes** at `:345` (`# pragma: no cover — the authority guarantees this`); Birth **no** | CEU **yes** (self-performed at `:263`); Birth **no** | CEU **yes**; Birth **no** | CEU **NO**; Birth **YES** | **PARTIALLY ASSIMILATED** |
| 3 | **Relationship** | Graph: `graph/validation.py:105-140` — CANONICAL. CEU: `existence.py:1028-1076` `_require_type`/`_check_admissible` — RUNTIME | Graph: in-code regex `:36-39`. CEU: passed registry + attributes on registered type units | Graph **no** (own grammar); CEU **yes** transitively | Graph **no**; CEU **yes** | Graph **no**; CEU **yes** | Graph **YES**; CEU **NO** — *"Registry-driven validity (CEU-007): a constraint applies only if declared"* (`:1043`) | **PARTIALLY ASSIMILATED** |
| 4 | **Context** | `context/validation.py:433-470`; `context/location_assurance.py:359,432,557,586` | in-code `VALIDATION_RULES` (`:187-250`) + `CONTEXT_CONSTITUTION`; passed or freshly constructed `FrameRegistry` | core `LOCATION` kind only (`identity.py:132`) — **unaffected** | **no** (self-constructs) | **no** | **YES** over the passed/constructed subject | **ASSIMILATED** for determinism; the subject is constructed, not committed |
| 5 | **Capability** | `nucleus/authority.py:66-97`; projected by `nucleus/law.py:76-80` | private `bootstrap()` over committed Python seeds; memoised in `@cache` (`:66`) | **yes** transitively via `bootstrap()` | **self-performed** | **yes** (`functools.cache`) | **YES across processes** (M10) but **not runtime-extensible** (M9) | **PARTIALLY ASSIMILATED** |
| 6 | **Requirement** | none in `engine/`; `00-MASTER/UAKOS-CLOSURE-009/requirement_engine.py` | not established; writes at `:1753-1760` before the verdict | unknown | unknown | unknown | unknown | **UNKNOWN** |
| 7 | **Lifecycle** | `runtime/execution/lifecycle.py:39,52,57,64`; `context/taxonomy.py:187,197,208,211`; `temporal/coordinate.py:291` | module-level `LIFECYCLE_TRANSITIONS` table; frozen dataclasses; no clock reference in `coordinate.py` | **no** | **no** | tables are `dict` but **no writer exists** | **YES** | **ASSIMILATED** (in-code canonical) |
| 8 | **Security** | `runtime/execution/authorization.py:61,96`; `14-SECURITY/*.md` prose only | **none** — `subject: str = "engineering"` | **no** | **no** | **no** | n/a — no knowledge source exists | **NOT YET ASSIMILATED** |
| 9 | **Certification** | `certification/criteria.py:35-145`; `universal_certification/rules.py:35-226`; `certification/ledger.py` | fields on a frozen `CertificationSubject` + `_DISCLOSURE_CHECK_ID` (`:32`) | **no** | **no** | **no** | **YES over its subject** — but relays upstream verdicts (CR-18) | **PARTIALLY ASSIMILATED** |
| 10 | **Measurement** | `verification_intelligence/gate.py:603,611` `measure`; `verification_impact/impact.py`; `engine/discovery/dimensions.py` | declaration file + static `ast` parse of the repository; discovery is registry-only by contract | **no** | **no** | **no** | **YES — of the working tree**, not `HEAD` | **PARTIALLY ASSIMILATED** |

### 9.1 CR-21 — The defect pattern generalises to three domains, all from one root

- **Finding.** The identity pattern — validity dependent on whether an initialization call ran — exists in **three of ten** domains: identity, entity (CEU half), relationship (CEU half). Capability is a fourth, related but distinct case. All four trace to `engine/ceu/catalog.py:396 bootstrap()` populating the identity extension space.
- **Evidence.** Identity: M1/M2/M6. Entity: `existence.py:345` calls `is_well_formed` with `# pragma: no cover — the authority guarantees this` — the pragma marks the branch as believed unreachable, which is true only under the assumption that `_bootstrap` registered the kind moments earlier in the same process. Relationship: `existence.py:1028-1041 _require_type` fails closed on *"relationship type is not registered"*, so the same `(source, target, type)` triple is admissible or refused depending on what was registered first in this process; every relationship it creates goes through `register` → `_admit` → `is_well_formed`. Capability: measured M9 — the authority answers from its own private `bootstrap()`, so a role registered in any other registry is **invisible** (`holds('tenant','own-capability') = False` after successful registration), and `@cache` freezes even that answer after the first call.
- **Current state.** Four domains inherit the property; six do not.
- **Desired state.** Ten of ten derive from committed knowledge.
- **Impact.** Capability is the most consequential instance and the most subtle. Its verdict *is* deterministic across processes (M10, four hash seeds) because `bootstrap()` is deterministic over committed seeds — so the defect there is not non-determinism but **unextendability**: the ownership authority cannot see a runtime-declared role, and the eight nucleus invariants at `nucleus/law.py:151-208` are evaluated against a population that cannot grow. `engine/nucleus/authority.py:30-33` states the intent honestly: *"If the CEU catalogue stopped declaring `own-capability` on `nucleus`, ownership would stop being granted here — which is the observable difference between an authority and a projection."* The unaddressed corollary is that the catalogue is the *only* thing it will ever read.
- **Dependency.** CR-05, CR-01.
- **Classification.** **PARTIALLY ASSIMILATED** — six domains clean, three defective, one unknown.

### 9.2 Reference patterns located

Four domains are usable as reference shapes and should be preserved rather than changed: `engine/validation/` (declares purity and has it), `engine/object_birth/gate.py` (declaration + ledger, FAULT distinct from CLOSED, writes nothing), `engine/discovery/dimensions.py` (*"no regex over paths or content, no `glob`/`fnmatch`, no filesystem walking… The registry is the single source of truth (INV-13)"*, with sorted ordering), and `engine/runtime/execution/lifecycle.py` (constant transition table, no writer).

---

## 10. Universal Assimilation Alignment

Test: for the single-click chain `Input → Knowledge Discovery → Identity → Context → Ownership → Security → Impact → Validation → Evolution`, can each stage operate from canonical knowledge without hidden runtime preparation?

### 10.1 Structural finding

The nine-stage pipeline is **not one executable artifact**. It is a documentary composition model. The executable pipeline that exists has four steps, and the published single click does not invoke it.

`platform/universal_assimilation/pipeline.py:1-24` documents four steps: Admit → Classify → Normalise → Home. It is genuinely pure — `SourceInput` carries `kind`, `locator`, `payload: bytes` (`:52-66`) with the contract stated at `:53-58`: *"Payload acquisition is the caller's business. The framework never scans a filesystem, opens a network connection, or rediscovers a repository as a side effect of assimilating one of its files."* `bootstrap_assimilation()` (`bootstrap.py:29-40`) composes adapters, kind registry and truth policy from in-code defaults with **no I/O** — a genuine Class A helper.

But `platform/universal_foundation/cli.py:63-66`:

```python
subjects = foundation.project_population(root=args.root)
locators = sorted({locator for subject in subjects for locator in subject.locators})
determination = foundation.determine(subjects=subjects, locators=locators)
```

`sources` is not passed. In `determine` (`service.py:268-301`) that means `report = None`, so the assimilation report is *not measured*. **The single click exercises truth-classification, ownership and measurement, and skips assimilation entirely.**

### 10.2 Per-stage assessment

| Stage | Executable? | What it reads | Hidden runtime preparation required? | Classification |
|---|---|---|---|---|
| **Input / Admit** | **Yes** — `pipeline.py:159 assimilate_source` | a **passed** `SourceInput`; never a filesystem scan (`:53-58`) | **No.** `bootstrap_assimilation()` does no I/O | **ASSIMILATED** — but unexercised by the CLI |
| **Knowledge Discovery** | Yes, three unrelated implementations — `engine/knowledge/integration/discovery.py`, `engine/knowledge/ukip/discovery.py`, operationally `closure_engine.py:171 discover_sources()` | `git ls-files -z` (committed index) **plus** `rglob` of an out-of-repo corpus **plus** explicit reads of gitignored generated files (`:344-353`) | **Yes** — requires `scripts/generate-prerequisites.sh` to have produced `knowledge/` | **NOT YET ASSIMILATED** |
| **Identity** | Yes, two disjoint mints — `engine/uckp/identity.py mint()` (pure), `engine/registry/universal/identity.py deterministic_id()` | pure for the URN plane; extension-kind minting needs `resolve_kind_code` | **Yes** for extension kinds | **PARTIALLY ASSIMILATED** — and **not on the assimilation path**: `pipeline.py` mints nothing and imports neither |
| **Context** | No pipeline stage. Taxonomy exists (`engine/context/taxonomy.py`, 16 `ContextKind`) | — | — | **NOT YET ASSIMILATED** as a stage |
| **Ownership** | **Yes** — `OwnershipDeterminationEngine.determine(subjects)` via `service.py:251-253`; also `closure_engine.py:369 assign()` | passed `Subject` tuples from `project_population` → the declared `population_document`; `assign()` reads in-code `TRUTH_ROOTS`/`CODE_ROOTS`/`SPEC_ROOTS` (`closure_engine.py:74-88`) against scan results | **Yes** — the declared population document is the **gitignored, untracked** `closure.json` (M12) | **NOT YET ASSIMILATED** |
| **Security** | **No code on the path** | — | — | **NOT YET ASSIMILATED** (absent, not deferred — CR-19) |
| **Impact** | Code exists — `engine/graph/architecture/impact.py ArchitectureImpactEngine` | imported only within `engine/graph/architecture/` (`__init__.py:68`, `engine.py:41`, `evidence.py:61`) and its own tests | — | **NOT YET ASSIMILATED** as a stage |
| **Validation** | **Yes** — `PolicyMeasurementEngine.measure(context)` (`service.py:264-266`) | `MeasurementContext.create(...)` (`:288-293`) built in memory from partition/ownership/assimilation/subjects | **No** file I/O in the measure step | **PARTIALLY ASSIMILATED** — pure step, inherits its inputs' provenance |
| **Evolution** | Code exists — `engine/uckp/evolution.py`, `EVOLUTION_CYCLE` 15 stages, ledger schema enforced on read (`:380-395`) | in-code vocabulary + committed ledger | — | **PARTIALLY ASSIMILATED** — not wired to assimilation |

### 10.3 CR-22 — The single click cannot operate from canonical knowledge because its population document is a generated, untracked artifact

- **Finding.** The one stage that runs habitually requires hidden runtime preparation, an environment variable, an out-of-repository directory, and its own prior output; and the declared population document consumed by the single click is not in git.
- **Evidence.** Measured (M12): `closure.json` is matched by `.gitignore:59` and `git ls-files --error-unmatch` reports *"did not match any file(s) known to git"*. It is nevertheless the declared `population_document` (`closure_engine.py:234-235`) consumed by `project_population` (`platform/universal_foundation/service.py:221-227`) at `cli.py:63`. `Makefile:248-279` chains `closure` → `closure-phase2: closure` → `closure-phase3: closure-phase2`, so phases 2 and 3 consume the generated JSON rather than any committed input. Full mechanism and the 437/0 → 528/91 counter-measurement in CR-10.
- **Current state.** The published single-click determination is computed over a regenerated, untracked population.
- **Desired state.** A committed, declared population that the single click reads.
- **Impact.** This is the sharpest non-identity instance of the boundary being crossed. `RTBD-001` §7 states that generated products are *"NOT part of Repository Truth… Including generated products in Repository Truth would create a recursive definition."* The single click's population is exactly such a product.
- **Dependency.** CR-10, CR-13. Owner decision AB-6 recorded pending at `closure_engine.py:456-460`.
- **Classification.** **NOT YET ASSIMILATED.**


---

## 11. Infinite Expansion Assessment

Test: can future entities, realities, dimensions, temporal models, technologies, languages, software versions and unknown existence forms be introduced by **knowledge evolution** (committed data) rather than **code mutation** (Python source)?

### 11.1 Axis assessment

| Axis | Admissible without a code edit? | With durable, fresh-process validity? | Evidence |
|---|---|---|---|
| Unlimited entity kinds | **YES mechanically** — `register_kind` admits any well-formed `(name, code)`; `declare_form` admits a form as data | **NO** — valid only in the process that admitted it | `identity.py:162`; `existence.py:357`; measured M1/M2 |
| New entity forms | YES in-process | **NO** | `declare_form` writes only to `self._units`/`self._by_id` (`existence.py:251-252`) and the identity globals; no filesystem write anywhere in `engine/ceu/` |
| New realities / contexts / universes / civilizations | `REALITY`, `EXISTENCE`, `UNIVERSE`, `CIVILIZATION`, `CONTEXT`, `LOCATION` are **core** kinds → deterministic | YES for the kind; **NO** for a new `ContextKind` | measured M2; `context/taxonomy.py:42,84` — `coerce` raises `TaxonomyError` with `allowed=[...]` |
| New dimensions | **NO** — `ContextKind` (16 members) requires a source edit | **NO** | `taxonomy.py:42`; `ContextTaxonomy.extend` (`:516`) extends the *tree*, not the kind set |
| New temporal models | **NO** — `SEED_TEMPORAL_MODELS` (7 rows) is a Python tuple; `EvolutionStage` (15) requires an enum edit | **NO** | `engine/ceu/catalog.py:280`; `engine/uckp/evolution.py:44` |
| New technologies | **NO** for reader forms — `SUPPORTED_FORMS` (5), `SUPPORTED_OPS` (6) | **NO** | `engine/uaue/authority.py:73,78` — honest comment: *"Declared here because they are **code paths**, not declarations: adding a form means writing a reader for it, so an undeclared form must fail closed"* |
| New value representations | **NO** — `VALUE_TYPES = ("string","number","boolean","list","mapping")`; `:74` raises | **NO** | `engine/context/ontology.py:47,74` — a tensor, amplitude or non-scalar representation is refused |
| New storage / persistence kinds | **YES, best-behaved in the repo** — 10 kinds plus a `FUTURE_STORAGE` sentinel; advisory, not a hard refusal; `verify_interchangeable()` compares `universe_digest()` across all ten | YES | `engine/uckp/persistence.py:59` |
| New facets (questions about existence) | **NO by design** — 33 closed; a 34th is a constitutional amendment | n/a | `engine/uckp/facets.py:24,59` — *"The enumeration is closed on purpose while the vocabularies inside facets are open"* |
| Code space exhaustion | `[A-Z][A-Z0-9]{1,7}` — not a practical bound | — | `identity.py:182` |

### 11.2 CR-23 — 230 closed enumerations are undisclosed, and the law that would detect them structurally cannot

- **Finding.** The declared prohibited condition is *undisclosed closure*. It is present at least 230 times, and `ISD-L-01` — the law that measures scope-expansion capacity — cannot detect a single instance.
- **Evidence.** Measured (M13/M16): **238** closed `Enum` subclasses across the six code roots (200 distinct names). `00-MASTER/UISD-000001/uisd-declaration.json` declares **11** `closed_enumeration_disclosures` (11 expansion axes, 11 laws). Of the 11, only **6 distinct names** are Python enums in the six roots — `ClosureState`, `Facet`, `KnowledgeCapability`, `RegistryKind`, `RelationType`, `RelationshipKind` — accounting for 8 occurrences. **230 closed Python enumerations are undisclosed**, including every one directly relevant to admitting future forms:

  | Undisclosed enum | Location |
  |---|---|
  | `ContextKind` (16) — the reality/observer/temporal/spatial dimension set itself | `engine/context/taxonomy.py:42` |
  | `ContextLifecycle` | `engine/context/taxonomy.py:153` |
  | `EvolutionStage` (15) — the evolution cycle | `engine/uckp/evolution.py:44` |
  | `KnowledgeKind` | `engine/knowledge/model.py:40` |
  | `Lifecycle` | `engine/knowledge/model.py:108` |
  | `CertificationClass` | `engine/universal_certification/contracts.py:86`, `engine/certification/contracts.py:80`, `platform/security/contracts.py:512` |
  | `ComplianceStatus` | `engine/universal_certification/contracts.py:92` |
  | `MeasurementComparator` | `engine/universal_certification/contracts.py:99` |
  | all 12 in `platform/security/contracts.py` | — |

  `ISD-L-01` (`engine/infinite_scope/contract.py:170-201`) iterates **only `contract.closed_enumerations`** — the 11 declared entries — and per entry asserts four things: `closing_invariant` non-blank, `admission` non-blank, `declared_at` exists on disk, and `intentional or gap`. Plus a non-vacuity guard at `:182-186` (*"an empty disclosure list would make this law vacuous rather than satisfied"*). It performs **no AST scan for `Enum` subclasses** (`ast` is used only in `_population_literals`), never counts a disclosed `population` against the actual enum, and cannot distinguish a genuine data-admission path from a source edit — `"Registration under UCKP-ART-17: add the member"` (ISD-CE-07) passes identically to a real one, because both are non-blank strings.

  The declaration pre-empts the objection at `$disclosure_completeness`: *"ISD-L-01 measures that each entry names a closing invariant and an admission path, **not that the list is exhaustive** — a claim of exhaustiveness would be the very finite assumption the principle prohibits."* The reasoning is internally coherent. The consequence is that the prohibited condition is unmeasurable.
- **Current state.** Disclosure discipline is enforced over a self-selected sample of 11 out of ~241 closed sets.
- **Desired state.** Either the disclosure register is populated by discovery rather than by hand, or the law is scoped to what it can measure and the residue is recorded.
- **Impact.** "No enumeration is closed silently" is asserted and is false 230 times. The two genuinely falsifiable laws are L-06 (`check_relationship_model_expands` at `:430` actually performs an extension in memory and proves the original vocabulary did not mutate) and L-11 (`check_admission_path_exercisability` at `:735` appends a synthetic member to a **deep copy** and re-runs declared consumers, reconciling measured against recorded refusals in both directions). L-11's scope is deliberately narrow and it writes nothing — so it proves *a document could be appended to and a reader would accept it*; it never proves *a committed document is read by a fresh validator*.
- **Dependency.** None. This is independently closable by measurement.
- **Classification.** **PARTIALLY ASSIMILATED** — the register, the law and the non-vacuity guard all exist; coverage is ~4.6%.

### 11.3 CR-24 — Data-only admission honoured by a fresh validator: disproved, with one exception that is already built

- **Finding.** There is no committed-data → fresh-process → deterministic-honouring path in production. The one mechanism that would provide it exists, works, and has no committed input.
- **Evidence.**

  | Requirement | Status | Evidence |
  |---|---|---|
  | A substrate that does not branch on form | **MET** | `engine/ceu/existence.py` — one `ExistenceUnit` record type (`:104`), self-describing root (`_bootstrap` at `:268`); *"No function in this module branches on a particular form, classification, topology or relationship type."* |
  | An in-process admission call | **MET** | `declare_form` (`:357`); `register_kind` (`identity.py:162`); `ContextTaxonomy.extend` (`taxonomy.py:516`) |
  | A reader that rehydrates from a document | **MET and MEASURED WORKING** | `from_document` (`:773`); measured M5 — succeeds in a fresh process, restores 72 kinds, digest identical |
  | A **committed document** for that reader | **ABSENT** | measured M7 — zero tracked JSON carries `ucos-constitutional-existence-registry` |
  | A **production loader** wiring committed data → registry | **ABSENT** | `from_document`'s only caller is `reconstruct()` (`:868`), which feeds it `to_document()` — a memory round trip — plus `engine/tests/ceu/test_existence.py:304` |
  | Cross-process persistence of registered kinds | **ABSENT** | `identity.py:156-159`, empty at import |
  | Equivalent for the nucleus population | **ABSENT** | `engine/nucleus/registry.py:607 declarations_from_mapping` — docstring: *"This is the path by which an unlimited number of future nuclei, layers and compositions enter with no code change at all."* Callers: `engine/tests/nucleus/test_registry_and_ownership.py:374` and nothing else. Twin at `engine/context/registry.py:447` has the same profile |

  The openness *tests* prove less than they appear to. `engine/tests/ceu/test_existence.py:102-106 test_a_future_form_needs_no_code_change` and the openness report's cited `test_unknown_entity_form_needs_no_code_change` hash engine source before and after an in-process admission and assert byte-identity. That is true, and it is **not the same claim** as "the admission survives the process." Nothing re-reads a committed artifact afterwards.
- **Current state.** Knowledge evolution can add **units** to a running process. Only code mutation can add **kinds, forms, dimensions or temporal models** to a fresh one.
- **Desired state.** A committed existence document, plus a production path that loads it before any validator runs.
- **Impact.** "Infinite expansion" currently means *the source is easy to extend and the extension is disclosed*, not *the system learns from data*. The openness mechanism and the determinism guarantee are implemented as a trade: `register_kind`'s docstring names the constitutional driver — *"AC-001/AC-009 forbid a closed enumeration: an unknown future entity kind must be admissible without a code change here"* — and satisfies it by using process memory, which is precisely what breaks determinism.
- **Dependency.** CR-04 (root), CR-01.
- **Classification.** **NOT YET ASSIMILATED.**

### 11.4 Reconciliation with the standing openness reports

| Report | Its conclusion | Agreement with measured code |
|---|---|---|
| `INFINITE-EXPANSION-COMPLIANCE-DETERMINATION.md` | *"Substantial compliance… but 8 architectural violations discovered"*; detection rules AA-1 (enum without extension mechanism), AA-2 (undisclosed enumeration), AA-5 (fixed count without qualifier) | **Directionally agrees, materially understates.** By its own AA-1/AA-2 the count is ~230, not 8. `ContextKind`'s docstring *"The sixteen universal context kinds"* is a textbook AA-5 |
| `INFINITE-EXPANSION-COMPLIANCE-ASSESSMENT.md` | 19 COMPLIANT · 12 PARTIAL · 6 VIOLATION · 25 UNPROVEN · 10 UNKNOWN; *"The largest category is UNPROVEN — and the honest reading of that is not 'compliant' but 'no violation found, and no proof built.'"* | **The most accurate of the four**, and it explicitly refuses to over-claim. One caveat: it cites `taxonomy.py:59-62` (*"That the list moved from fifteen to sixteen is itself the evidence the taxonomy is open"*) as evidence of openness; the fifteen→sixteen move was a **source edit**, so it evidences editability, not data-openness |
| `INFINITE-EXPANSION-SAFETY-MODEL-DETERMINATION.md` | *"12 expansion risks identified. 12 prevention mechanisms designed. **Zero unavoidable closures detected.**"* | **Disagrees on the load-bearing word.** `Facet` at 33 is deliberately unavoidable in practice — the UISD declaration itself argues the closure must stay (*"Closure of the QUESTION set is what keeps the ANSWER sets open"*). The claim is also forward-looking (*"can satisfy… if applied"*), i.e. design intention, not measurement |
| `UCOS-ARCHITECTURAL-OPENNESS-ASSESSMENT-REPORT.md` | Entity **CERTIFIED**, Context **CERTIFIED**, Relationship **CERTIFIED**, Technology **CERTIFIED** with caveat, Data/Storage **CERTIFIED for `engine/uckp` only** | **Where code contradicts the report most sharply.** The cited certification evidence proves in-process source-byte stability, not cross-process durability (CR-24). Its own §7 GAP finding — *"`KnowledgeStore`, `ContextRegistry`, UCDA's decision register, the identity ledger — each does direct file I/O with no seam"* — is the same defect described from the storage side |

---

## 12. Contradiction Register

Live, located, mutually inconsistent claims bearing on canonical knowledge versus runtime authority. **None resolved here.**

| # | Claim A | Claim B | Basis | Location |
|---|---|---|---|---|
| **CX-01** | `identity.py:286-291`: *"This is the total parser: it resolves every identifier this authority can mint, which is what makes 'parse covers 100% of minted identifiers' measurable"* | Totality holds only inside the process that registered. Measured `False` vs `True` for the same string (M1/M2) | code vs its own docstring | `identity.py:156,159` vs `:286-301` |
| **CX-02** | `identity.py:130`: *"Each code is unique so `kind` stays recoverable from an id"* | Recoverable only after a call. `parse_kind_name` raises `RegistrationValidationError("unknown identifier kind code")` in a fresh process | declaration vs runtime | `identity.py:130` vs measured M1 |
| **CX-03** | `dictionary.py:220`: *"Identifiers the one grammar cannot parse. **Must always be empty.**"* | Non-empty in any process that has not bootstrapped CEU; wired to `"status": "PASS"/"FAIL"` at `:257` | unconditional claim vs runtime | `dictionary.py:219-221,257` |
| **CX-04** | `identity.py:14-15`: *"no wall-clock, RNG, or network on the determined path (RC-4 determinism)"* | Correct as written and incomplete — mutable module state is an unnamed fourth non-determinism source | declaration vs implementation | `identity.py:14-15` vs `:156-159` |
| **CX-05** | `identity.py:5-8`: the same artifact resolves identically *"regardless of version, wall-clock, machine, or **registration order**"* | `resolve_kind_code`/`parse_kind_name` consult runtime-mutated globals; extension-kind minting fails before registration | docstring vs code | `identity.py:5-8` vs `:206-213,288-301` |
| **CX-06** | `existence.py:903-905`: *"The authority owns the name→code mapping; **this function never stores one.**"* | The authority stores it only in RAM, so no one stores it durably. Measured M7: zero committed artifact | intent vs effect | `existence.py:898-910` vs M7 |
| **CX-07** | `existence.py:726-728`: *"The whole journal, not just its head. Steering 022: Repository Truth must be **sufficient** to reconstruct constitutional state"* | The sufficient document is never written. `from_document` works (M5) and has no production caller | principle vs practice | `existence.py:733,773` vs M7 |
| **CX-08** | `engine/nucleus/authority.py:30-33`: *"which is the observable difference between an authority and a projection"* | The authority reads only its own private `bootstrap()`; a role registered anywhere else is invisible. Measured `holds('tenant','own-capability') = False` after successful registration (M9) | authority claim vs reachability | `authority.py:66-97` vs M9 |
| **CX-09** | `engine/provider/selection.py:5-8`: *"a named, **pure function**… It must be deterministic"*; `ordering.py:30-31`: *"An identical graph therefore yields an identical order in every environment and at every commit"* | Strategy *resolution by name* reads mutable module globals. Benign in practice because both self-seed at import (M4), but the guarantee is a property of that convention, not of the mechanism | purity claim vs mechanism | `selection.py:22`, `ordering.py:55` vs M4 |
| **CX-10** | `phases.py:51`: *"Handlers are registered with their phase and are **never called in a hard-coded order**"*; `:66` *"a **deterministic**, serialisable rendering"* | `unregister_generation_phase` (`:103-108`) makes the phase set non-monotonic. Measured: withdrawal makes `generation_order()` raise `FAC-PHASE-001` (M4b) | determinism claim vs withdrawal path | `phases.py:51,66` vs `:103-108`, M4b |
| **CX-11** | `engine/uckp/identity.py`: *"Two processes on different planets in different centuries mint the same identity for the same name, which is what makes cross-era replay possible at all"* | On the registry plane, two processes **at the same instant on the same machine** disagree about validity (M1/M2) | constitution vs runtime | measured M1/M2 |
| **CX-12** | `00-CMG/CMG-000001` **XII.6**: *"**Derived truth SHALL always be reconciled against repository reality and SHALL never be treated as a source of authority.**"* **LVI.2** names *"derived truth mistaken for source"* a recognised drift risk | `closure.json` is generated, gitignored and untracked (M12), and is the declared `population_document` the single click reads (`service.py:221-227`) | constitution vs implementation | `00-CMG/CMG-000001:369,1288` vs M12 |
| **CX-13** | `00-CMG/CMG-000001` **XII.5**: *"A LATENT artifact… SHALL NOT be cited as constitutional authority… **Latency IS a detectable defect, not a status.**"* | The clause tokens most load-bearing for identity openness have **zero located occurrences** in any `.md` or `.json`: `AC-001`, `AC-009`, `AC-003`, `AC-011`, `AC-012`, and `XXXI.5`. They are cited only from Python comments. `RC-4` resolves to at least three unrelated per-programme meanings | constitution vs citation practice | `identity.py:66,130,153`; `nucleus/law.py:179,224,232`; `nucleus/registry.py:195` |
| **CX-14** | Two distinct instruments both named **CMG-000001**: `00-MASTER/CMG-000001` v1.0 (Laws 1–10) and `00-CMG/CMG-000001` v1.2 (Articles I–LXXXVI) | `00-MASTER/CMG-000001` **Law 10**: `∀ A,B ∈ ConstitutionalInstruments: (A.id = B.id) ⟹ (A = B)`; **Principle 9**: *"No namespace collisions permitted across… Constitutional instruments"* | constitution vs corpus | both files; cited as v1.2 by `CANONICAL-AUTHORITY-DETERMINATION.md:38` |
| **CX-15** | `uisd-declaration.json` prohibits *"UNDISCLOSED CLOSURE — an enumeration closed in code or data while nothing states what closes it or how a member is admitted"*; `ISD-L-01` claims *"no enumeration is closed silently"* | Measured 230 undisclosed closed Python enumerations (M16); `ISD-L-01` iterates only the 11 declared entries and performs no discovery | law vs measurable population | `contract.py:170-201` vs M13/M16 |
| **CX-16** | `.github/workflows/uaue-gate.yml:188-191`: *"Two independent processes, not two calls in one process. An in-process replay could pass on a memoised result; a cross-process replay cannot"* | Both runs invoke the same entry point with the same arguments, so both reach the same initialization state. The gate proves *same invocation sequence = same result*; it does not prove *different initialization history = same truth value* | correct reasoning, insufficient scope | `uaue-gate.yml:188-199`; `uisd-gate.yml:231-241` |
| **CX-17** | `determinism.yml:1-7`: *"the same certified blueprint, compiler, and environment definition must produce byte-identical output every time"*; `reproduce.py:15-18` describes *"two isolated environments (A and B)"* | Both builds run in one interpreter sharing one `env`, one `document`, one `adapter`, one `signer`; isolation is `with env.apply():` plus a distinct output directory (M19). A verdict depending on a populated global is equally wrong in both and the comparison passes | isolation claim vs implementation | `reproduce.py:283-320` |
| **CX-18** | Test suite green on all `is_well_formed` assertions; `engine/tests/nucleus/test_identity_convergence.py:127-138` asserts `not is_well_formed("UCOS-EVO-088bd1337123")` as an invariant | The test's own docstring concedes: *"That is a separate population **today only because no kind is registered under the code `EVO`**."* The assertion measures an empty global. `grep autouse=True` across all 15 `engine/tests/**/conftest.py` returns zero results, so the extension space at test time is an undeclared baseline | tests vs property | `test_identity_convergence.py:127-138` vs `identity.py:156` |

**CX-16 is the crux of this determination.** The repository has built the right instrument twice — cross-process verdict comparison — and reasoned about it correctly in a code comment. What neither instance varies is the one dimension that matters here: the initialization history between the two runs. That is why a defect measurable in three lines of Python has survived 29 gates and a 10 000-test suite.

---

## 13. Reuse and Gap Analysis

Standing rule respected: *"Before creating new capability, prove no existing capability can satisfy."* Governing precedents respected: `CANONICAL-AUTHORITY-RESOLUTION-DETERMINATION` §4 **Rejected** Option B (a new authority resolver) as *"Duplicates UCAF, breaches Zero Parallel Authority"*; `GATE-PURITY-DETERMINATION` **D-3.4**: *"the reference implementations already exist. Adopt, do not invent"*; `02-CANONICAL-OWNERSHIP-MATRIX` addenda record that `CREATE` was unavailable under `00-CMG/CMG-000001` Art LXXVII.2(a) and Art LXXVII.4.

### 13.1 Existing capabilities

| # | Capability | Located implementation | Evidence it does the job | Disposition |
|---|---|---|---|---|
| R-1 | **Deterministic, journal-verifying registry projection and verbatim loader** | `engine/ceu/existence.py:733` `to_document` / `:773` `from_document` / `:868` `reconstruct` | **Measured working in a fresh process** (M5): 195 units, 133 246 bytes, kinds restored 29→72, round-trip digest identical. Refuses re-derivation: *"Re-deriving would let the rebuilt registry differ from the recorded one and still look healthy"* | **REUSE** — this is the answer to CR-05, already built |
| R-2 | **Committed derived artifact + fail-closed re-derivation on read** | `IdentifierDictionary.to_document` (`dictionary.py:262`) / `from_document` (`:280`); writer at `engine/nucleus/cli.py:169-187`; artifact `00-MASTER/UCOS-NUCLEUS-001/UCOS-NUCLEUS-IDENTIFIER-DICTIONARY.json`; self-declaring header at `cli.py:154-167` | Measured (M8): 212 entries replay in a fresh process, `status=PASS`, `unparsed=0`. Four persistence tests including `test_a_mutated_entry_is_detected` | **REUSE as the template** for a declared kind-space artifact |
| R-3 | **Purity enforcement by re-running the deriver** | `platform/foundation/derivation.py:285-330` `derive`/`verify`; contract at `:20-23`: *"enforces purity by **re-running the deriver** and comparing digests — a value that changes across identical runs (hidden state / wall-clock) is rejected as impure (AIF-L18)"*; `canonical.py:206-216` `CanonicalDigest.verify` | Exactly the primitive that rejects hidden state. Already implemented and already reasoned | **REUSE** |
| R-4 | **Cross-process verdict comparison in CI** | `.github/workflows/uaue-gate.yml:188-199`; `uisd-gate.yml:231-241` | The pattern exists and the reasoning is stated correctly. Missing element: **vary the initialization history between run A and run B** | **EXTEND** — the smallest possible change that would make the defect measurable |
| R-5 | **Fail-closed declaration loader with two-way totality** | `engine/infinite_scope/contract.py:60-90`: *"Fail closed: a declaration that cannot be read is not a declaration that permits everything"*; refuses a contract whose law names a missing check **or** whose check no law claims (`:4-6`). Second and third implementations: `engine/uaue/resolution.py:251`, `engine/uckp/resolution.py:150` | Three independent implementations of the correct shape. This is the mechanism CR-03's three unread declarations and CX-13's latent citations would be caught by | **REUSE** |
| R-6 | **Collision-refusing, append-only allocation** | `engine/registry/universal/identity.py:162-199` — *"re-using either half for a different meaning is refused, because an identifier whose kind can change retroactively invalidates every reference minted under the old meaning"*; `engine/factory/phases.py:89-98` | The refusal semantics are correct and correctly reasoned. Only durability is missing | **EXTEND** — add persistence; do not touch the refusal logic |
| R-7 | **Cache contract that distinguishes projection from authority** | `engine/execution_environment/fingerprint.py:99,152` — *"It may never skip a verdict, never supply a check result, and never answer VALID on its own"*; EEG-01…05 always recomputed; invalidated by `bootstrap.sh --refresh` and `ucos-env.sh:437` | The boundary this determination is about, already articulated and enforced once | **REUSE as the contract template** |
| R-8 | **Versioned, append-only schema/format tags enforced on read** | `engine/uckp/evolution.py:107,111` `LEDGER_SCHEMA`/`LEDGER_VERSION`, enforced at `:380-395` including a `cycle_definition` comparison; `engine/object_birth/ledger.py:31,73-75`; `platform/foundation/canonical.py:36,44-80`; `derivation.py:47` | Loading is a verification rather than a deserialization: *"An append-only history that cannot be loaded is an append-only history nobody can falsify"* | **REUSE** |
| R-9 | **Closed-set disclosure register with a non-vacuity guard** | `00-MASTER/UISD-000001/uisd-declaration.json` `closed_enumeration_disclosures`; `engine/infinite_scope/contract.py:170-201` | A working register requiring a `closing_invariant` and an `admission` path per closure, refusing an empty list | **EXTEND** — coverage is 11 of ~241 (CR-23); the register is the right home |
| R-10 | **Recorded / derived plane typing, measured against itself** | `00-MASTER/UIS-001/uis-declaration.json:182`: *"The ledger is the RECORDED plane (AIF AX-01) and the registry is the DERIVED plane; **conflating them is the single defect the AIF forbids**"*; `platform/foundation/derivation.py:53-58` `InputKind.{SOURCE,RECORDED,DERIVED}`; AIF-L20 non-mixing | The canonical-vs-runtime distinction is already a typed, enforced axis | **REUSE** |
| R-11 | **Authority resolution by reading a located instrument** | `00-MASTER/UCOS-UCAF-001/ucaf-authority.json` — 34 authorities, 8 tiers, 61 delegations, 17 competence resolutions; `$resolution_comment`: *"A competence question is answered by READING a located instrument, never by this programme deciding"* | Exists and fails closed. `CANONICAL-AUTHORITY-RESOLUTION` §4 Option A | **EXTEND** (per that determination) |
| R-12 | **Emission modelled as an authority rather than a flag** | `00-MASTER/UCCEP-000000/uccep_engine.py:1360-1365` `emission_authority(...)` → `if authority["authorized"]: written = emit(...)`, else *"OBSERVATION ONLY — emission withheld"* | The only engine that separates canonical read from runtime write as an authority question | **REUSE** |
| R-13 | **Registry-only discovery with stabilised ordering** | `engine/discovery/dimensions.py:1-22`: *"no regex over paths or content, no `glob`/`fnmatch`, no filesystem walking… The registry is the single source of truth (INV-13)"*; `:106 sorted(...)` | Proves discovery need not scan a filesystem to be complete | **REUSE as the template** for CR-10's discovery step |
| R-14 | **Reader accepting two representations losslessly** | `engine/ceu/existence.py:834-848` (`supersession_history` vs legacy `supersessions`); `engine/lineage/memory.py:50-90` `MODE_MAP_OF_LISTS`/`MODE_LIST_MATCH` | Representation evolution without a migration event | **REUSE as the template** |

### 13.2 TRUE MISSING

| ID | Missing capability | Why genuinely absent |
|---|---|---|
| **M-1** | **A committed existence document plus a production path that loads it before any validator runs.** | Both halves exist in isolation and neither is joined. `from_document` is measured working in a fresh process (M5); zero tracked JSON carries its schema (M7); its only caller is `reconstruct()`, which feeds it an in-memory round trip. This single gap is the mechanism behind CR-05, CR-06, CR-07, CR-08, CR-24, CX-01…CX-08 and CX-11. **Nothing needs inventing: R-1 + R-2 + R-5 + R-6 + R-8 composed over the existing document closes it.** |
| **M-2** | **A cross-process verdict-equality measurement across differing initialization histories.** | The two-process comparison exists (R-4) and varies nothing between runs. `double_build` (M19) is single-process. `grep 'process-independen'` returns zero hits. No test observes the pre-bootstrap state; `grep autouse=True` across 15 conftest files returns zero results. This is independently closable by measurement alone and blocks nothing. |
| **M-3** | **Discovery of closed enumerations to populate the disclosure register.** | `ISD-L-01` validates a hand-maintained list of 11 against a measured population of ~241 (CR-23). The register (R-9), the non-vacuity guard, and an AST-scanning capability (`engine/verification_intelligence/gate.py:611` already parses the whole repository with `ast`) all exist; they are not composed. |

**Not missing — explicitly.** Deterministic projection, verbatim loading, purity-by-re-derivation, byte-identical replay gating, cross-process comparison, collision refusal, versioned schema contracts enforced on read, closed-set disclosure, fail-closed declaration loading, recorded/derived typing, authority resolution, emission-as-authority, registry-only discovery, and dual-representation reading **all exist and execute**.

**Refused and must not be created:** a new identity universe, a second identity authority, a third dictionary, a new canonical-knowledge-resolution engine, a new authority resolver, a new registry, a new namespace. **No finding in this determination implies any new engine, authority, registry or namespace.**

---

## 14. Implementation Dependency Impact

Recorded as structure only. **No phase, wave, roadmap, sequence or authorization is created or implied by this section.**

### 14.1 Dependency structure of the findings

```
CR-04  canonical projection implemented, verified, never written      ← ROOT
   │      (M5 works · M7 absent)
   ├── CR-05  validation truth produced by runtime bootstrap
   │     ├── CR-06  the dependency crosses capability boundaries (M3)
   │     ├── CR-07  constitutional legality inherits by live call (M15)
   │     ├── CR-16  round-trip proven on 2 of 12 registries
   │     ├── CR-17  three identifier grammars; only the stateful one is authoritative
   │     ├── CR-18  certification relays an unverifiable provenance
   │     └── CR-21  pattern generalises to 3 of 10 domains + capability
   ├── CR-08  registries declaring themselves canonical hold truth in RAM
   │     └── CR-15  registry layer inverted; coverage matrix structurally blind
   └── CR-24  data-only admission not honoured by a fresh validator
         └── CR-01  canonical vocabulary is Python source, not data

CR-13  validation depends on a generation step nothing used to run
   └── CR-10  closure verdict is a function of env + generated state
         └── CR-22  the single click reads an untracked population document

Independent of every root (closable by measurement alone):
   CR-12  no gate measures initialization independence (2 of 29 come closest)
   CR-23  230 undisclosed closed enumerations; ISD-L-01 cannot detect them

Recorded, separate axis:
   CR-02  twelve constitutional instruments have no machine reader
   CR-03  three declarations written and never read
   CR-09  one runtime registry is non-monotonic
   CR-19  security validation has no knowledge source
   CR-20  requirement validation writes before it measures

Correctly assimilated (preserve, do not change):
   CR-11  nondeterminism discipline for clock / RNG / network
   CR-14  reference-quality bootstrap cache contract
```

**CR-04 is the single root.** It is not blocked upstream: the document schema exists, the writer exists, the loader exists and is measured working in a fresh process, and the round trip is digest-identical. What is absent is the artifact and the wiring.

**CR-12 and CR-23 are independently closable by measurement** and depend on nothing. They are also the two findings that determine whether any of the others can regress silently.

### 14.2 Surfaces that would be affected by any future reconciliation

Recorded for impact awareness only.

| Surface | Sites | Nature of dependence |
|---|---|---|
| Enforcement sites reading `is_well_formed` | 9 non-test | `gateway.py:203`, `ownership.py:211,215`, `existence.py:345`, `possessions.py:151`, `location_assurance.py:175,285`, `dictionary.py:57,209,221`, `metadata.py:303` |
| Verdicts that would change classification | 4 | `dictionary.verify()["status"]`, `IdentifierEntry.__post_init__`, `ConstitutionalMetadata.identity_well_formed`, `legality._identity_complete` |
| Test references to `is_well_formed` | 32 | all evaluate post-bootstrap; none can observe the pre-bootstrap state |
| Gates measuring the affected population | 0 of 29 | UIS-001 `UIL-14`/`UIL-19` measure the ledger plane, which uses no extension kinds |
| Registries with no durable substrate | 6 | identity extension space, `KnowledgeRegistry`, `IdentityRegistry`, UCP capability/ownership, `NucleusRegistry`, `ExistenceRegistry` |
| Domains inheriting the defect | 3 of 10 (+capability) | entity (CEU), relationship (CEU), identity; capability by a related mechanism |
| Undisclosed closed enumerations | 230 | across the six code roots |

### 14.3 Blocked items recorded elsewhere

Not adjudicated here; recorded so this determination does not appear to supersede them.

| Item | Standing |
|---|---|
| Gate mode declaration (`OBSERVE`/`EXECUTION`) | `GATE-PURITY-DETERMINATION` D-3.3; blocked on owner decision `H-06` / `CR-09` |
| Making an incomplete closure population blocking | `closure_engine.py:456-460` — *"the governance act reserved to the EKI owner (AB-6, pending P2 sign-off)"* |
| Capability namespace spanning register | `CANONICAL-AUTHORITY-RESOLUTION-DETERMINATION` §2.5 — *"None. No register spans them."* Acceptance 2: *"Currently: unregistered, unproven"* |
| Ratifying authority | `UCAF-RC-01`…`RC-03` — *"the corpus contains no authority competent to ratify anything"* |
| `GP-6`, `GP-10` | OPEN / APPARENT in `GATE-PURITY-DETERMINATION`; not closed here |

---

## 15. Final Architectural Determination

### 15.1 Primary question

> For any UCOS Ω∞ concept, is truth derived from canonical knowledge, or does runtime state become an accidental authority?

**Determination: truth is derived from canonical knowledge on most surfaces, and runtime state is an accidental authority on a measured minority of them.**

| Sub-question | Answer | Basis |
|---|---|---|
| Does canonical knowledge exist? | **YES** — declarations, constitutions, seed data, schemas, registries, ledgers all present | §3 |
| Is it read by validators? | **MOSTLY** — 14 of 17 declarations; 19 of 20 schemas; 2 ledger schemas enforced on read | §3.1 |
| Does validation depend on module globals? | **YES**, on one pair (`identity.py:156,159`) | M1/M2 |
| Does it depend on bootstrap calls? | **YES** — 43 of 72 kinds | M1/M2 |
| Does it depend on initialization order? | **NO for import order** (M11), **YES for call order** (M3) | M3/M11 |
| Does it depend on process lifecycle? | **YES** | M6 |
| Does it depend on caches? | Indirectly — `@cache` at `authority.py:66` suppresses and leaks the side effect | M3/M9 |
| Does it depend on generated state? | **YES** for the closure verdict — env var + out-of-repo dir + gitignored trees | M12, CR-10 |
| Does it depend on hash seed or import order? | **NO** — identical across four seeds and both orders | M10/M11 |
| Is any of this measured by a gate? | **NO** — 2 of 29 gates compare across processes; neither varies initialization | M17/M18, CR-12 |

### 15.2 The confirmed pattern

Present in identity, CEU entity, CEU relationship, and (in a related form) capability:

```
Canonical Knowledge
        ↓
Runtime Bootstrap
        ↓
Mutable Module State
        ↓
Validation Truth
```

The target:

```
Canonical Knowledge
        ↓
Deterministic Resolver
        ↓
Pure Validation
        ↓
Runtime Projection
        ↓
Execution
```

The gap between them is one artifact and one wire. `ExistenceRegistry.from_document` **is** the deterministic resolver, and it is **measured working in a fresh process** (M5). What is missing is a committed document for it to read and a production path that reads it.

### 15.3 The identity case — the primary example

```
Same repository.  Same commit (bae59755).  Same machine.

Before CEU bootstrap:   UCOS-CLSS-8966ca9e8d02  →  INVALID
After  CEU bootstrap:   UCOS-CLSS-8966ca9e8d02  →  VALID

Zero file changes.  43 of 72 kinds affected (59.7%).
195 CEU identities carry such a kind.
9 non-test enforcement sites inherit the predicate,
including the constitutional mutation gateway,
the nucleus ownership invariant NUC-INV-09,
and the constitutional legality proof.
```

**Conclusion: identity validation is runtime-state dependent.**

And, established newly here: the call that produces the flip **need not be an identity call**. Asking `may_own_capability('nucleus')` — an ownership question — changes the truth value of an identifier (M3). The defect is therefore not a property of the identity capability. It is a property of the process.

### 15.4 The determinism distinction — stated explicitly

The repository contains two gates that compare verdicts across separate operating-system processes:

- **UAUE gate**, `.github/workflows/uaue-gate.yml:188-199`, with the reasoning stated verbatim in the workflow: *"Two independent processes, not two calls in one process. An in-process replay could pass on a memoised result; a cross-process replay cannot."*
- **UISD gate**, `.github/workflows/uisd-gate.yml:231-241`, same shape plus a working-tree comparison.

**What these gates prove:**

```
same process path  +  same invocation sequence  =  same result
```

**What these gates do NOT prove:**

```
different initialization histories  +  different bootstrap states  =  same truth value
```

Run A and run B are invocations of the *same entry point* with the *same arguments*. Both therefore execute the *same call sequence* and reach the *same initialization state*, inheriting identical module globals. A verdict that depends on whether `bootstrap()` ran is **equally wrong in both runs**, and the `diff` passes.

**Therefore neither gate detects runtime-state-dependent truth.** Nor does anything else: every `--check-determinism` self-guard compares two renders inside one process, and `double_build` (`engine/determinism/reproduce.py:283-320`, measured M19) runs both builds in one interpreter sharing one environment, document, adapter and signer. The repository has extensive determinism instrumentation and **all of it measures byte-stability of one path**, not independence from initialization history.

### 15.5 Classification summary

| Finding | Subject | Classification |
|---|---|---|
| CR-01 | Canonical vocabulary is Python source, not data | PARTIALLY ASSIMILATED |
| CR-02 | Twelve constitutional instruments have no machine reader | NOT YET ASSIMILATED |
| CR-03 | Three declarations written and never read | PARTIALLY ASSIMILATED |
| CR-04 | Canonical projection implemented, verified, never written | NOT YET ASSIMILATED |
| CR-05 | Validation truth produced by runtime bootstrap | NOT YET ASSIMILATED |
| CR-06 | Dependency crosses capability boundaries | NOT YET ASSIMILATED |
| CR-07 | Constitutional legality inherits by live call | NOT YET ASSIMILATED |
| CR-08 | Canonical registries hold truth only in process memory | NOT YET ASSIMILATED |
| CR-09 | One runtime registry is non-monotonic | PARTIALLY ASSIMILATED |
| CR-10 | Closure verdict is a function of env + generated state | NOT YET ASSIMILATED |
| CR-11 | Nondeterminism discipline (clock / RNG / network) | ASSIMILATED |
| CR-12 | No gate measures initialization independence | PARTIALLY ASSIMILATED |
| CR-13 | Validation depends on a generation step nothing used to run | PARTIALLY ASSIMILATED |
| CR-14 | Reference-quality bootstrap cache contract | ASSIMILATED |
| CR-15 | Registry layer inverted; coverage matrix blind to memory | PARTIALLY ASSIMILATED |
| CR-16 | Round-trip determinism proven on 2 of 12 registries | PARTIALLY ASSIMILATED |
| CR-17 | Three identifier grammars; only the stateful one authoritative | NOT YET ASSIMILATED |
| CR-18 | Certification relays an unverifiable provenance | PARTIALLY ASSIMILATED |
| CR-19 | Security validation has no knowledge source | NOT YET ASSIMILATED |
| CR-20 | Requirement validation writes before it measures | UNKNOWN |
| CR-21 | Pattern generalises to 3 of 10 domains + capability | PARTIALLY ASSIMILATED |
| CR-22 | Single click reads an untracked population document | NOT YET ASSIMILATED |
| CR-23 | 230 undisclosed closed enumerations | PARTIALLY ASSIMILATED |
| CR-24 | Data-only admission not honoured by a fresh validator | NOT YET ASSIMILATED |

| Classification | Count |
|---|---|
| ASSIMILATED | 2 |
| PARTIALLY ASSIMILATED | 10 |
| NOT YET ASSIMILATED | 11 |
| UNKNOWN | 1 |
| **Total** | **24** |

Per-domain (§9):

| Classification | Domains |
|---|---|
| ASSIMILATED | Context, Lifecycle |
| PARTIALLY ASSIMILATED | Entity, Relationship, Capability, Certification, Measurement |
| NOT YET ASSIMILATED | Identity, Security |
| UNKNOWN | Requirement |

### 15.6 Final architectural test

> **"UCOS Ω∞ derives truth from canonical knowledge. Runtime execution only projects and executes that truth; it never becomes the source of truth."**

## **Determination: PARTIALLY PROVEN**

**Why the first sentence is largely supported.** Canonical knowledge exists and is genuinely operative. Fourteen of seventeen programme declarations are read by the engines that cite them, and gates replay them. Nineteen schemas are read and two ledger schemas are enforced on read with the correct reasoning (*"Loading is therefore a verification rather than a deserialization"*). Every committed artifact that could be mistaken for an authority carries an explicit `"authority": "NONE — DERIVED TRUTH"` disclaimer naming its canonical source. Wall clock, RNG, network and salted hashing are absent from every verdict path, and their absence is actively guarded by AST-level tests. Determinism holds across four `PYTHONHASHSEED` values, both import orders, and repeated initialization (M10, M11, M11b). Two of ten capability domains are fully assimilated, five more partially. `engine/validation/` both declares purity and structurally has it. `engine/execution_environment/fingerprint.py` articulates and enforces exactly the projection-not-authority boundary this test asks about.

**Why the second sentence is disproved on measured surfaces.**

1. **Runtime does become the source of truth for identity validity.** `UCOS-CLSS-8966ca9e8d02` is invalid before CEU bootstrap and valid after, at one commit on one machine with zero file changes. 43 of 72 kinds (59.7%). Nine enforcement sites inherit it, including the single authorised constitutional mutation path.
2. **The dependency is not contained by capability boundaries.** An ownership question mutates an identity verdict (M3). Import is insufficient; a call to a *different capability* is sufficient. No call site can see this.
3. **Truth-holding registries hold their truth only in process memory.** Six registries have no durable substrate; three of them describe themselves as *canonical* or as *Recorded Truth*. Exactly one of twelve reads its population from a committed file.
4. **The most frequently surfaced verdict in the repository is a function of runtime state.** `CLOSED | concepts=549 | gaps=0` depends on an environment variable, an out-of-repository directory, gitignored generated trees, and its own prior untracked output. The repository records the counter-measurement itself: 437/0 → **528/91** when one environment variable is removed.
5. **No instrument can observe any of this.** Zero of twenty-nine gates and zero tests require verdict equality across differing initialization histories. The two gates that compare across processes hold the initialization history constant and therefore cannot detect the defect. The only reproducibility harness runs both builds in one interpreter.

**Therefore:** the statement holds for the UCKP URN plane, the UMK kernel plane, the 29 core registry kinds, the EC-1 validation layer, the graph validator, the object-birth gate, the lifecycle and temporal surfaces, and the discovery engine. It fails for the 43 runtime-registered kinds, the CEU entity and relationship admission paths, the identifier dictionary verdict, the constitutional legality proof, six unpersisted registries, and the closure determination. **Canonical knowledge exists; runtime execution sometimes creates rather than projects it; and validation truth is not universally independent of execution history.**

### 15.7 What the evidence does support, stated precisely

> *UCOS Ω∞ holds real canonical knowledge and reads it on most surfaces. On the surfaces that implement openness, it reconstructs canonical knowledge by execution rather than reading it, and process memory becomes the operative authority. The information required to close this is already committed; the mechanism required to read it — a journal-verifying, digest-identical, verbatim loader — is already implemented and measured working in a fresh interpreter. What is absent is the committed artifact, the wire from it to the validation path, and any measurement that would notice its absence.*

### 15.8 Standing

| Item | State |
|---|---|
| Determination | **COMPLETE** |
| Findings recorded | **24** (`CR-01`…`CR-24`) |
| Contradictions recorded | **18** (`CX-01`…`CX-18`) |
| Findings resolved | **ZERO** |
| Contradictions resolved | **ZERO** |
| Root cause identified | **CR-04** — a canonical projection that is implemented, verified, and never written |
| True missing capabilities | **THREE** — M-1 committed existence document + production loader; M-2 initialization-independence measurement; M-3 closed-enumeration discovery |
| New engines / authorities / registries / namespaces implied | **ZERO** |
| Measurements executed | **19** (`M1`…`M19`), all read-only |
| Code modified | **NONE** |
| Runtime systems modified | **NONE** |
| Registries modified | **NONE** |
| Configuration modified | **NONE** |
| Requirements / ADRs / phases / roadmaps created | **NONE** |
| Implementation sequence created | **NONE** |
| Certification altered | **NONE** |
| Identifiers created | **NONE** |
| Fixes implemented | **NONE** |
| Repository writes | **ONE** — this document |

**Measurement disclosure.** All nineteen measurements were pure in-memory evaluations in throwaway `python3` interpreters. One `register`/`unregister` probe (M4b, M9) mutated only that process's memory and was discarded on exit. One temporary file outside the repository (`/tmp/ucos_ceu_probe.json`) was written and is outside the repository boundary. No gate that writes was executed; `closure_engine.py` was **not** run — `closure.json` was read as it stood from the session-start hook. No tracked file was modified. No registry file, artifact or ledger was written.

**Relationship to the predecessor.** The predecessor determination established `DV-01`…`DV-17` for identity and asked whether the pattern extends. It does: to CEU entity admission, CEU relationship admissibility, and — by a related mechanism — capability ownership. Two findings are newly established here and were not available to the predecessor: **CR-06**, that the dependency crosses capability boundaries so that an ownership question flips an identity verdict; and **CR-04/M5**, that the deterministic resolver the target architecture requires already exists, already works in a fresh process, and already round-trips digest-identical — so the root cause is an unwritten artifact rather than a missing capability. **CR-07** closes an edge the predecessor left open: constitutional legality inherits the defect by live call, not by stale data.

---

**END DETERMINATION — STOPPED AFTER DETERMINATION.**
