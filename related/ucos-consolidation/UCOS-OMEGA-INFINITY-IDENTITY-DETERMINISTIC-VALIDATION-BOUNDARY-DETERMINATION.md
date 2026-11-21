# UCOS Ω∞ — UNIVERSAL IDENTITY CAPABILITY DETERMINISTIC VALIDATION BOUNDARY DETERMINATION

| Field | Value |
|---|---|
| **Classification** | EVIDENCE — DETERMINATION ONLY |
| **Authority** | **NONE — DERIVED TRUTH.** Certifies nothing, ratifies nothing, creates no authority, mints no identifier, registers no kind. |
| **Mode** | READ-ONLY. No code modified, no validator modified, no CEU bootstrap modified, no registry modified, no identifier format changed, no identity created or migrated, no requirement/ADR/phase created, no certification altered. |
| **Baseline** | `git HEAD = bae59755d7e2d3566c93b89c722b68847145269a`, branch `integration/recovery-001`, 330 uncommitted working-tree entries |
| **Reference system** | `logical:git-commit-order@ucos-consolidation` (CMG-000002). No wall clock read. |
| **Method** | Static reading **plus direct in-memory measurement**. Every measurement is pure function evaluation in a throwaway interpreter. Nothing was written to the repository, no registry file was touched, and one temporary file outside the repository was created and removed. |
| **Finding markers** | `DV-01`…`DV-16` are **local reading aids scoped to this document**. They register nothing and enter no namespace. |
| **Predecessor** | Continues `UCOS-OMEGA-INFINITY-UNIVERSAL-IDENTITY-CAPABILITY-EVOLUTION-DETERMINATION.md` (same baseline). That determination found representation is not separated from semantics. This one examines a deeper property it surfaced. |

---

## 1. Objective

Determine whether UCOS Ω∞ identity **validation** is deterministic, canonical, and independent of process execution state.

**Primary question:** Is identity validity a stable property of the identity itself, or is it dependent on runtime state, bootstrap order, loaded modules, or execution history?

**Answer: identity validity is currently RUNTIME DEPENDENT for 43 of 72 admissible kinds. This is proven by direct measurement, not inferred.**

The same identifier string, at the same commit, on the same machine, returns `True` in one process and `False` in another — differing only in whether one function was called. No file changed between the two measurements.

---

## 2. Evidence Baseline

### 2.1 The decisive measurement — three separate interpreters

Executed at `HEAD = bae59755`, read-only, three independent `python3` processes.

**Process 1** — bootstrap the CEU substrate, enumerate identities whose kind code lives in the extension space:

```
extension-kind identities registered: 195
sample: ['UCOS-CLSS-8966ca9e8d02', 'UCOS-CLSS-4cff7ab89c2a', 'UCOS-CLSS-0644d6f6774e']
```

**Process 2** — fresh interpreter, `engine.registry.universal.identity` imported, **no CEU bootstrap**:

```
is_well_formed(UCOS-CLSS-8966ca9e8d02) = False
is_well_formed(UCOS-CLSS-4cff7ab89c2a) = False
is_well_formed(UCOS-CLSS-0644d6f6774e) = False
```

**Process 3** — fresh interpreter, **with** `bootstrap()` called first:

```
is_well_formed(UCOS-CLSS-8966ca9e8d02) = True
is_well_formed(UCOS-CLSS-4cff7ab89c2a) = True
is_well_formed(UCOS-CLSS-0644d6f6774e) = True
```

**Three identifiers. Two truth values. One commit. Zero file changes.**

### 2.2 The mechanism, isolated

| Process state | `kind_names()` | `_EXTENSION_KIND_CODES` | `is_well_formed("UCOS-ENTY-abc123def456")` |
|---|---|---|---|
| Fresh import of the identity module | 29 | 0 | **False** |
| After `import engine.ceu.existence` and `import engine.ceu.catalog` (**import alone**) | 29 | 0 | **False** |
| After calling `engine.ceu.catalog.bootstrap()` | **72** | **43** | **True** |

`parse_kind_name("UCOS-ENTY-abc123def456")` → raises `RegistrationValidationError` before bootstrap; returns `"ENTITY"` after.

**Importing is not sufficient. A function must be *called*.** This is the sharpest form of the dependency: validity depends on execution history, not merely on module loading.

### 2.3 Kind census — measured

| Measure | Value |
|---|---|
| Core `RegistryKind` members (compile-time, process-independent) | **29** |
| Extension kinds registered by `bootstrap()` (runtime) | **43** |
| Total admissible after bootstrap | **72** |
| Proportion of the kind space that is runtime-dependent | **43/72 = 59.7%** |
| CEU-registered identities carrying an extension kind code | **195** |
| Declared source of the extension kinds (committed data) | `SEED_FORMS` (53 rows) + `SEED_CLASSIFICATIONS` (10 rows), `engine/ceu/catalog.py` |
| Persistence writer for the extension registry | **NONE** |

Token-level confirmation (`ENTITY`/`TEMPORAL`/`IDENTITY` are *not* core kinds):

```
ENGINE     RegistryKind=True  code=ENG
ENTITY     RegistryKind=False code=None
REALITY    RegistryKind=True  code=RLT
EXISTENCE  RegistryKind=True  code=EXT
TEMPORAL   RegistryKind=False code=None
IDENTITY   RegistryKind=False code=None
```

---

## 3. Current Identity Validation Architecture

### 3.1 The validation chain

```
is_well_formed(id)                 engine/registry/universal/identity.py:303-309
        │  try/except wrapper, returns bool
        ▼
parse_kind_name(id)                engine/registry/universal/identity.py:288-301
        │  splits on "-", requires 3 parts, prefix == "UCOS", non-empty tail
        ├── code in _CODE_KINDS            → core kind      (compile-time, 29 entries)
        ├── code in _EXTENSION_CODE_KINDS  → extension kind (RUNTIME, 0→43 entries)
        └── else → raise RegistrationValidationError("unknown identifier kind code")
```

The two lookup tables are **module-global mutable dicts, empty at import** (`identity.py:150-159`, verified verbatim):

```python
_CODE_KINDS: dict[str, RegistryKind] = {code: kind for kind, code in _KIND_CODES.items()}

#: Kinds admitted by **registration** rather than by editing :class:`RegistryKind`.
#: AC-001/AC-009 forbid a closed enumeration: an unknown future entity kind must be
#: admissible without a code change here, so the grammar carries an open extension
#: space alongside the enum. ``kind name → code``.
_EXTENSION_KIND_CODES: dict[str, str] = {}

#: Reverse map for the extension space (``code → kind name``).
_EXTENSION_CODE_KINDS: dict[str, str] = {}
```

The only mutator is `register_kind` (`identity.py:162-199`), documented as *"Admit a future identifier kind. This is the **only** extension mechanism."* It is append-only and collision-refusing within a process, and it **writes only to process memory**.

### 3.2 The population path

```
engine/ceu/catalog.py  SEED_FORMS (53) + SEED_CLASSIFICATIONS (10)   ← committed data
        ▼  bootstrap()
engine/ceu/existence.py:898-910  _register_identity_kind(key, code)
        ▼  register_kind(name, code)            ← alias: register_identifier_kind
engine/registry/universal/identity.py  _EXTENSION_KIND_CODES / _EXTENSION_CODE_KINDS
        ▼
parse_kind_name → is_well_formed
```

`_register_identity_kind` (`existence.py:898-910`) is documented as deliberately *not* storing a mapping:

> *"A name the authority already knows is reused rather than re-registered, so the substrate adds no second grammar and claims no duplicate code. The authority owns the name→code mapping; **this function never stores one.**"*

The design intent is sound — one grammar, one authority. The consequence not addressed is that "the authority owns the mapping" means *the authority owns it in RAM, for the lifetime of this process only*.

### 3.3 The declared invariant that this breaks

`engine/registry/universal/dictionary.py:219-221`, verbatim:

```python
    def unparsed(self) -> tuple[str, ...]:
        """Identifiers the one grammar cannot parse. Must always be empty."""
        return tuple(sorted(k for k in self._entries if not is_well_formed(k)))
```

**"Must always be empty"** is an unconditional claim. It is satisfied or violated depending on whether `bootstrap()` has run. The verdict is wired into a PASS/FAIL status at `dictionary.py:253`:

```python
"status": "PASS" if not (unreproducible or unparsed or duplicated) else "FAIL",
```

and asserted by two tests — `engine/tests/nucleus/test_context_binding.py:292` and `engine/tests/nucleus/test_certification_and_cli.py:105`, both `assert verification["unparsed"] == []`.

---

## 4. Runtime State Dependency Analysis

### DV-01 — Identity validity is a function of process execution history

- **Finding.** `is_well_formed` returns different results for the same input in two processes at the same commit, determined by whether `bootstrap()` was called.
- **Evidence.** §2.1 (three processes, measured), §2.2 (import-alone insufficient), `identity.py:156-159` (empty mutable globals), `identity.py:296-301` (`parse_kind_name` reads them), `identity.py:303-309` (`is_well_formed` wraps it).
- **Impact.** Validity is not a property of the identifier. It is a property of the *interpreter that asks*. Any consumer that validates without first bootstrapping CEU reaches a different verdict from one that does — with no error, no warning, and no way to tell which world it is in.
- **Current state.** 43 of 72 kinds (59.7%) are runtime-registered; 195 measured CEU identities carry such a kind.
- **Desired state.** `is_well_formed(id)` is a pure function of the identifier plus committed declared data, evaluable in a fresh interpreter with no prior call.
- **Dependency.** None upstream. The declared source (`SEED_FORMS`/`SEED_CLASSIFICATIONS`) is already committed data, so the information needed is already in the repository.
- **Classification.** **NOT YET ASSIMILATED.**

### DV-02 — The extension kind registry has no persistence writer

- **Finding.** Nothing writes `_EXTENSION_KIND_CODES` to disk. It is reconstructed by execution on every process start, or not at all.
- **Evidence.** Exhaustive grep for both symbols across all `*.py` returns **11 hits, all inside `engine/registry/universal/identity.py`** (definitions at `:156`/`:159`; reads at `:187`, `:194`, `:203`, `:211-212`, `:298-299`; writes at `:196-197`). No serializer, no `to_document`, no artifact.
- **Impact.** The kind space is not Recorded Truth. It cannot be audited, diffed, replayed, or certified, because it does not exist anywhere except in memory. A determination that measured the kind space yesterday cannot be re-verified today except by re-running the same call sequence.
- **Current state.** Ephemeral process state.
- **Desired state.** Either persisted as a declared artifact, or derived deterministically from committed declarations at validation time (no registration step).
- **Dependency.** DV-01.
- **Classification.** **NOT YET ASSIMILATED.**

### DV-03 — Import is not sufficient; a call is required

- **Finding.** `import engine.ceu.existence` and `import engine.ceu.catalog` leave the extension space empty (29 kinds). Only `bootstrap()` populates it (72 kinds).
- **Evidence.** §2.2, rows 2 and 3 — measured directly in one process.
- **Impact.** This is stronger than an import-order dependency. Import order is at least statically analysable; a *call* dependency is not. No linter, type checker, or import graph can detect that a validator was consulted too early.
- **Current state.** Correctness depends on an unenforced call-before-use protocol.
- **Desired state.** No initialisation protocol required for validation.
- **Dependency.** DV-01.
- **Classification.** **NOT YET ASSIMILATED.**

### DV-04 — Enforcement paths depend on this, including the constitutional mutation gateway

- **Finding.** `is_well_formed` is consulted at nine non-test enforcement sites, including the single authorised mutation path.
- **Evidence.** Measured call sites:

  | Path | Site | What it decides |
  |---|---|---|
  | `engine/constitution/gateway.py:203` | `_registration` | refuses a mutation whose record *"carries no identifier the identity authority could mint"* |
  | `engine/nucleus/ownership.py:211,215` | ownership binding | refuses a subject/capability id |
  | `engine/ceu/existence.py:345` | `_admit` | refuses registration (marked `pragma: no cover — the authority guarantees this`) |
  | `engine/ceu/possessions.py:151` | possession binding | refuses an identifier |
  | `engine/context/location_assurance.py:175,285` | LXV rules | reports a frame/identifier as non-conformant |
  | `engine/registry/universal/dictionary.py:57,221` | entry guard + `unparsed()` | decides dictionary PASS/FAIL |
  | `engine/constitution/metadata.py:303` | record validity | boolean property |

- **Impact.** The failure direction differs by site, and both directions are wrong:
  - **Fail-closed (safer but still wrong):** `gateway.py:203` would *refuse a legitimate mutation* in a process that had not bootstrapped CEU. A valid identity is rejected as unmintable.
  - **False positive (worse):** `dictionary.py:221` would *report legitimate identifiers as unparseable*, flipping a governance verdict from PASS to FAIL for reasons that have nothing to do with the data.
- **Current state.** Nine enforcement sites inherit a non-deterministic predicate.
- **Desired state.** Every enforcement site consults a predicate that cannot vary by process.
- **Dependency.** DV-01.
- **Classification.** **NOT YET ASSIMILATED.**

### DV-05 — The test suite cannot observe this by construction

- **Finding.** All 32 test references to `is_well_formed` evaluate it *after* the fixture has already bootstrapped, so no test can observe the pre-bootstrap state.
- **Evidence.** Every CEU assertion — `engine/tests/ceu/test_existence.py:84,114,134,366`, `engine/tests/ceu/test_catalog_and_sufficiency.py:189,283,355,411` — operates on a registry returned by `bootstrap()`. `engine/tests/context/test_location.py:452-458` calls `deterministic_id` then `is_well_formed` on the result in the same expression, so the kind is necessarily resolvable. The two `unparsed() == []` assertions run in bootstrapped nucleus fixtures. The only negative tests are `engine/tests/kernel/test_identity.py:61-64`, which test a *different* authority (`UMK`), and `engine/tests/context/test_location_assurance_negatives.py:319`, which *monkeypatches* `is_well_formed` to a constant.
- **Impact.** The suite validates the post-bootstrap world exclusively. A green test run is not evidence that validity is process-independent — it is evidence that the tests all live in the same process state. This is the mechanism by which the property drifted without detection.
- **Current state.** Zero tests assert process-independence of validity.
- **Desired state.** A test that validates a known extension-kind identifier in a fresh interpreter with no bootstrap.
- **Dependency.** None. Writable today against existing mechanisms.
- **Classification.** **NOT YET ASSIMILATED.**

### DV-06 — No gate measures this property

- **Finding.** The identity conformance gate does not test process-independence of validation.
- **Evidence.** `.github/workflows/uis-gate.yml` steps are: zero-enumeration proof · self-determinism (byte-identical rendering) · Knowledge Once · `--check-no-identity-minting` · `--check-no-authority` · fail-closed gate. The self-determinism check concerns the *engine's own rendering*, not the *validator's verdict*. `verify.sh` and `Makefile` contain no reference to `ceu`. The UIS-001 twenty laws include `UIL-14 Verifiability` measured by `identities_unverifiable` and `UIL-19 Compatibility` by `identities_failing_declared_grammar` — both computed over the corpus ledger plane (`UCOS-<CATEGORY>-<NNNNNN>`), which uses **no extension kinds**, so neither measure can observe this defect.
- **Impact.** The property is unguarded. It can regress further, silently.
- **Current state.** Unmeasured.
- **Desired state.** A measured, gated property.
- **Dependency.** DV-05.
- **Classification.** **NOT YET ASSIMILATED.**

---

## 5. Identity Determinism Assessment

Against the directive's classification scheme:

| Validation surface | Depends only on canonical rules / committed data? | Classification |
|---|---|---|
| `parse_kind` (core kinds only, `identity.py:274-286`) | yes — reads `_CODE_KINDS`, built at import from the enum | **deterministic** |
| `deterministic_id` **minting** | yes for core kinds; for extension kinds requires `resolve_kind_code` to know the name (`identity.py:206-213`), so **minting is equally state-dependent** | **partially deterministic** |
| `parse_kind_name` / `is_well_formed` | **no** — reads runtime-mutated globals | **runtime dependent** |
| `normalize_namespace`, `normalize_natural_key`, `identity_tuple` | yes — pure regex | **deterministic** |
| `engine/uckp/identity.py` `mint`/`parse`/`verify` (URN plane) | yes — pure, no registry consulted | **deterministic** |
| `engine/kernel/identity.py` `mint`/`is_well_formed` (UMK plane) | yes — regex + digest, no registry | **deterministic** |
| `engine/uckp/alignment.py` `repository_local_urn` (6-digit plane) | yes — a compiled regex constant | **deterministic** |
| `dictionary.unparsed()` / `verify()` status | **no** — inherits `is_well_formed` | **runtime dependent** |

**Overall determination: PARTIALLY DETERMINISTIC.**

Note the asymmetry precisely: the *pure* planes (UCKP URN, UMK kernel, the 6-digit repository regex) are all deterministic. The **only** state-dependent plane is the registry platform's open-kind space — and it is state-dependent *because* it is the one plane that implements openness. **The openness mechanism is the source of the non-determinism.** That is the architectural crux of this determination: the system bought extensibility with process state.

### DV-07 — Minting is state-dependent in the same way as validation

- **Finding.** `deterministic_id` cannot mint an extension-kind identifier before registration either.
- **Evidence.** `identity.py:206-213` `resolve_kind_code` consults `_EXTENSION_KIND_CODES`, then falls through to `RegistryKind.coerce(name)`, which raises for an unregistered name. `deterministic_id` calls `identity_tuple` → `resolve_kind_code`.
- **Impact.** The docstring at `identity.py:1-16` claims the identifier is *"a pure function of an artifact's identity tuple … regardless of version, wall-clock, machine, or registration order."* For the 43 extension kinds, **"regardless of registration order" is false**: registration order determines whether minting succeeds at all, and (per DV-08) which name owns a code.
- **Current state.** The purity claim holds for 29 core kinds and is unproven for 43.
- **Desired state.** Minting and validation both total over the declared kind space without a registration step.
- **Dependency.** DV-01.
- **Classification.** **PARTIALLY ASSIMILATED** (purity holds on the core axis, fails on the extension axis).

---

## 6. Identity Authority Assessment

### DV-08 — Code allocation is order-sensitive, and nothing declares the allocation

- **Finding.** The first claimant of a kind code wins; the second is refused. No committed table declares which name owns which code.
- **Evidence.** Measured directly:

  ```
  register_kind('ENTITY','ENTY')      -> ENTY
  register_kind('ENTERPRISE','ENTY')  -> REFUSED: kind code is already claimed (value='ENTY')
  register_kind('ENTITY','ENTY')      -> ENTY   (idempotent no-op)
  register_kind('REALITY','RLT2')     -> REFUSED: kind is already a core registry kind
  ```

  `register_kind` (`identity.py:180-198`) refuses re-coding and code collision, with the reasoning stated at `:167-171`: *"re-using either half for a different meaning is refused, because an identifier whose kind can change retroactively invalidates every reference minted under the old meaning."*
- **Impact.** The refusal discipline is correct and well-reasoned — it prevents retroactive kind reinterpretation *within a process*. But because the allocation lives only in memory and is rebuilt by execution, the *outcome* is a function of registration order. Today the order is stable because it is driven by the committed, deterministically-ordered `SEED_FORMS` tuple. That stability is a property of one caller's data ordering, **not a property the authority guarantees**. A second registrant reaching the authority first in some other process would produce a different, internally-consistent, equally "valid" kind space.
- **Current state.** Order-stable in practice via a single caller; order-dependent by mechanism; undeclared.
- **Desired state.** A declared, committed name→code allocation that no execution order can alter.
- **Dependency.** DV-02.
- **Classification.** **PARTIALLY ASSIMILATED** (collision refusal is real; allocation authority is undeclared).

### DV-09 — Authority is unified for minting and split for validation

- **Finding.** The registry platform is a genuine single authority for its own plane, but validation authority is effectively shared with whoever calls `register_kind`.
- **Evidence.** `_register_identity_kind` (`existence.py:898-910`) is the sole external registrant, and it is deliberately deferential (*"reuse, not a second grammar"*). But its effect is to determine what the authority will subsequently accept as valid. The authority owns the *grammar*; CEU owns the *vocabulary*, at runtime, unpersisted.
- **Impact.** "One authority" holds for the shape rule and not for the admissible-kind set. Validity is co-authored.
- **Current state.** Grammar centralised; vocabulary distributed and ephemeral.
- **Desired state.** Vocabulary declared in committed data, read by the authority, not injected into it.
- **Dependency.** DV-02, DV-08.
- **Classification.** **PARTIALLY ASSIMILATED.**

### DV-10 — Programme identifiers remain unparseable by the identity authority

- **Finding.** Identifiers of the form `UCOS-<PROG>-001` are refused by the authority, independent of bootstrap state.
- **Evidence.** Measured: `is_well_formed("UCOS-AEE-001") = False`; `is_well_formed("UCOS-ENGINE-001265") = False`; `is_well_formed("UCOS-ENGINE-1000000") = False`. Scanning the committed `00-MASTER/UCOS-NUCLEUS-001/UCOS-NUCLEUS-IDENTIFIER-DICTIONARY.json` for identifier-shaped strings yields 213, of which the 212 real entries use only core codes (`CAP`, `CMPO`, `LYR`, `NUC`) — **so that artifact's verdict is process-independent today** — while the one non-core token is `UCOS-NUCLEUS-001`, the *programme* identifier in the header.
- **Impact.** Confirms, from a second direction, the programme-id/object-id namespace collision recorded in the predecessor determination. It also bounds the present blast radius honestly: the committed dictionary is not currently affected by DV-01. The exposure is latent — the dictionary is a projection of `deterministic_id` entries, so populating it from the CEU registry would make its PASS/FAIL verdict process-dependent.
- **Current state.** Latent, not active, for this artifact.
- **Desired state.** One declared shape authority covering programme and object identifiers, or an explicit declaration that they are disjoint populations.
- **Dependency.** Predecessor finding C-03 / IDF-06.
- **Classification.** **NOT YET ASSIMILATED.**

---

## 7. Identity Kind Registry Assessment

**The directive's question — are identity kinds (A) permanent canonical knowledge or (B) temporary runtime state?**

**Determination: (B) temporary runtime state, for 43 of 72 kinds — with the material qualification that their declared source is committed data.**

| Property | Core kinds (29) | Extension kinds (43) |
|---|---|---|
| Where declared | `RegistryKind` enum, `identity.py:45-107` | `SEED_FORMS`/`SEED_CLASSIFICATIONS`, `engine/ceu/catalog.py` |
| Committed to git | yes | **yes** (the source rows are committed) |
| Available at import | yes | **no** |
| Requires a function call | no | **yes** (`bootstrap()`) |
| Persisted as an artifact | n/a (compile-time) | **no** |
| Survives the process | yes | **no** |
| Auditable / diffable / replayable | yes | **no** |
| Order-dependent allocation | no | **yes** (DV-08) |

### DV-11 — The kind space is derivable from committed data but is not derived

- **Finding.** Everything needed for a deterministic kind space already exists in committed form. The system chooses to reconstruct it by execution instead of reading it.
- **Evidence.** `SEED_FORMS` (53 rows) and `SEED_CLASSIFICATIONS` (10 rows) are committed tuples in `engine/ceu/catalog.py`, each row carrying an explicit code (e.g. `("entity", "ENTY", "Entity", (...))`). `_authority_name` (`existence.py:893-895`) is a pure string transform (`key.replace("-","_").upper()`). So the name→code mapping is a pure function of committed data. Yet it reaches the validator only via `register_kind` side effects into process memory.
- **Impact.** This is the most consequential framing in this determination: **the defect is not missing information — it is an unnecessary indirection through mutable state.** That materially lowers the closure cost and means no new declaration, registry, or authority is required.
- **Current state.** Committed source, ephemeral projection, validator reads the projection.
- **Desired state.** Validator resolves against the committed source (directly or via a deterministically generated artifact).
- **Dependency.** None.
- **Classification.** **NOT YET ASSIMILATED** — but the missing piece is a binding, not knowledge.

---

## 8. Bootstrap Dependency Assessment

**The directive's chain — does identity correctness require `startup → import → bootstrap → validation`?**

**Measured answer: yes for 43 of 72 kinds, and the chain is worse than stated because `import` is not a sufficient link (DV-03). The actual chain is `startup → import → explicit call → validation`.**

### DV-12 — `bootstrap()` is memoised behind one accessor, making first-caller identity load-bearing

- **Finding.** The nucleus layer memoises bootstrap; other consumers do not, and nothing coordinates them.
- **Evidence.** `engine/nucleus/authority.py:66` carries `@cache`, and `authority.py:63,72,81,127` all call `bootstrap()`. `engine/ceu/catalog.py:525` (`to_document`) calls `bootstrap()` when no registry is supplied. Nine enforcement sites (DV-04) call `is_well_formed` with **no** bootstrap guarantee — notably `engine/constitution/gateway.py:203`, which imports only `is_well_formed` (`gateway.py:47`) and never touches CEU.
- **Impact.** Whether the constitutional mutation gateway can accept an extension-kind identity depends on whether some unrelated module happened to call into `engine/nucleus/authority.py` earlier in the same process. That is a coupling no reader of `gateway.py` can see.
- **Current state.** Implicit, undeclared, order-dependent initialisation coupling across module boundaries.
- **Desired state.** No initialisation coupling; validation total without prior calls.
- **Dependency.** DV-01, DV-03.
- **Classification.** **NOT YET ASSIMILATED.**

### DV-13 — Does this violate identity capability principles? Yes, three of them, all located

- **Finding.** The dependency contradicts three properties the repository declares for identity.
- **Evidence.**
  1. **Determinism.** `identity.py:14-15`: *"no wall-clock, RNG, or network on the determined path (RC-4 determinism)."* Correct as written, and incomplete — mutable module state is a fourth non-determinism source it does not name.
  2. **Registration-order independence.** `identity.py:5-8`: *"the same logical artifact always resolves to the same `universal_id` regardless of version, wall-clock, machine, or **registration order**."* Disproved for extension kinds by DV-07/DV-08.
  3. **Cross-era replay.** `engine/uckp/identity.py` docstring: *"Two processes on different planets in different centuries mint the same identity for the same name, which is what makes cross-era replay possible at all."* This holds for the UCKP URN plane. On the registry plane, two processes **at the same instant on the same machine** disagree about whether an identifier is valid (§2.1).
- **Impact.** The property the architecture most explicitly claims — that identity is invariant across execution context — is the property that measurably fails on the one plane implementing openness.
- **Current state.** Declared and contradicted.
- **Desired state.** Declaration and behaviour agree, or the declaration is scoped to the planes where it holds.
- **Dependency.** DV-01.
- **Classification.** **NOT YET ASSIMILATED.**

---

## 9. Universal Identity Capability Alignment

Is **Validation** correctly positioned in the target model?

```
Universal Identity Capability
  ├── Authority        PARTIALLY ASSIMILATED  grammar unified; kind vocabulary co-authored (DV-09)
  ├── Semantics        PARTIALLY ASSIMILATED  pure minting on 3 planes; welded to rendering (predecessor IDF-07)
  ├── Namespace        NOT YET ASSIMILATED    4 incompatible alphabets; 5 unrelated axes (predecessor)
  ├── Context          NOT YET ASSIMILATED    context-free by design; 6 facets hardcoded (predecessor IDF-13)
  ├── Representation   NOT YET ASSIMILATED    no codec, no scheme version (predecessor IDF-08)
  ├── Resolution       PARTIALLY ASSIMILATED  1 multi-shape resolver; no historical resolution
  ├── Validation       NOT YET ASSIMILATED    ← runtime dependent (this determination)
  └── Evolution        PARTIALLY ASSIMILATED  supersession complete in CEU; no migration
```

### DV-14 — Validation is positioned as a peer but implemented as a dependent

- **Finding.** In the target model Validation is a sibling capability. In code it is a *consumer of another capability's runtime side effects*.
- **Evidence.** The validator (`engine/registry/universal/identity.py`) cannot answer correctly until the entity substrate (`engine/ceu/`) has executed. Dependency direction: `engine/ceu/existence.py:68-70` imports `register_kind` from the registry — so the *declared* dependency is CEU → registry, while the *effective* dependency is registry-validation → CEU-execution. **The dependency arrow reverses at runtime.**
- **Impact.** Validation cannot be reasoned about, tested, or certified independently of the entity capability. A hidden cycle exists: registry provides the grammar to CEU; CEU provides the vocabulary back to the registry, by mutation, at runtime.
- **Current state.** Inverted effective dependency; latent import/initialisation cycle.
- **Desired state.** Validation depends only on committed declarations. Both capabilities read the same declared vocabulary; neither injects into the other.
- **Dependency.** DV-11.
- **Classification.** **NOT YET ASSIMILATED.**

---

## 10. Infinite Expansion Assessment

| Axis | Supported without runtime code change? | Evidence |
|---|---|---|
| Unlimited entity kinds | **YES mechanically** — `register_kind` admits any well-formed `(name, code)`; `declare_form` admits a form as data; `engine/tests/ceu/test_existence.py:102-106` `test_a_future_form_needs_no_code_change` proves it | mechanism is real |
| …with **deterministic validity** | **NO** — a newly admitted kind is valid only in processes that admitted it (DV-01) | §2.1 |
| Future entity categories | **YES to admit, NO to validate durably** | as above |
| Unknown future existence forms | **YES to admit, NO to validate durably** | as above |
| New realities / contexts | `REALITY`, `EXISTENCE`, `UNIVERSE`, `CIVILIZATION`, `CONTEXT`, `LOCATION` are **core** kinds → deterministic | measured §2.3 |
| New technologies | not an identity kind axis | — |
| Code space exhaustion | `[A-Z][A-Z0-9]{1,7}` → very large; not a practical bound | `identity.py:182` |

### DV-15 — Openness is real; durable openness is not

- **Finding.** The system can admit an unlimited number of new kinds. It cannot yet make the resulting identifiers verifiable outside the admitting process.
- **Evidence.** `register_kind` docstring: *"Admit a future identifier kind. This is the **only** extension mechanism."* Its rationale at `identity.py:152-155` names the constitutional driver: *"AC-001/AC-009 forbid a closed enumeration: an unknown future entity kind must be admissible without a code change here."* The constraint is honoured. What is not addressed is that admission produces no durable record.
- **Impact.** Infinite expansion is satisfied *within a process lifetime*. Across processes it degrades to the core 29. So the openness guarantee and the determinism guarantee are currently in direct tension, and the openness mechanism is the one that breaks determinism.
- **Current state.** Expansion mechanism present; expansion durability absent.
- **Desired state.** Admission by declaration (committed), so openness and determinism hold simultaneously.
- **Dependency.** DV-02, DV-11.
- **Classification.** **PARTIALLY ASSIMILATED.**

---

## 11. Representation Independence Assessment

Re-evaluated against the predecessor determination; unchanged at this baseline, with one addition.

| Surface | Determination | Evidence |
|---|---|---|
| Six-digit width | **enforced as law, declared as representation** | `alignment.py:89` raises; CMG-000001 XXXI.4 *"makes zero-padding a presentation choice"*. Measured: `is_well_formed("UCOS-ENGINE-1000000") = False` |
| Prefix rules | **58 distinct prefix values, 53 files**; `ID_PREFIX = "UCOS"` hardcoded at `identity.py:32` | predecessor §3.3 |
| URN shape | **stored field, treated as an invariant** — `verify()` re-derives and raises | `engine/uckp/identity.py:130-138` |
| UUID derivation | **`uuid5` over the rendered URN string** → representation change ≡ tamper | `identity.py:58-60` |
| Rendering formats | **no codec, no renderer registry, no scheme version, no migration** | predecessor IDF-08 |
| **Kind code embedded in the identifier** | **new observation** — the code segment is what requires the runtime lookup. Representation choice *causes* the determinism defect | `identity.py:288-301` |

### DV-16 — Encoding the kind into the identifier is what forces a stateful parse

- **Finding.** Because the kind is encoded in the identifier as a short code, parsing requires a code→name table, and that table is the mutable state.
- **Evidence.** `parse_kind_name` (`identity.py:288-301`) must consult `_CODE_KINDS` or `_EXTENSION_CODE_KINDS` to resolve `parts[1]`. Had the identifier not encoded kind, no table lookup — and no state dependency — would be needed to decide well-formedness. Note CMG-000001 **XXXI.5** states: *"An identifier SHALL NOT encode meaning beyond namespace and ordinal. Encoding phase, **kind**, status, owner, or version into an identifier couples identity to mutable fact and IS PROHIBITED."*
- **Impact.** The determinism defect and the XXXI.5 prohibition have the **same root cause**: kind is encoded in the representation. This links two findings previously treated as unrelated, and it means a single reconciliation addresses both.
- **Current state.** Kind encoded; parse stateful; XXXI.5 tension unresolved (`UNKNOWN` pending owner adjudication of the XXXI.1 subseries allowance).
- **Desired state.** Either kind is not identity-bearing, or the code→name allocation is committed declared data.
- **Dependency.** Predecessor C-07, C-08.
- **Classification.** **NOT YET ASSIMILATED.**

---

## 12. External Identity Trust Assessment

### 12.1 `adopt()` — the one external ingestion path

`platform/foundation/durable_identity.py`. Two entry points: `DurableIdentity.adopt` (value, `:158-181`) and `IdentityRegistry.adopt` (sealing, `:438-467`). Purpose, verbatim (`:160-165`):

> *"Import an identity with a pre-existing, frozen `opaque` (A/G7 genesis). Used once to grandfather an existing corpus: the historical opaque is preserved verbatim (Recorded Truth is never recomputed, AX-02) rather than re-derived. The admission key is still validated and namespaced."*

### 12.2 What validation is bypassed

`verify()` (`:186-194`), verbatim:

```python
    def verify(self) -> bool:
        """Return True iff a *natively minted* identity's opaque still recomputes.

        An adopted identity carries a frozen historical opaque that is preserved, not
        recomputed (AX-02), so it is trivially considered intact.
        """
        if self.adopted:
            return True
        return self.compute_opaque(self.authority_id, self.local_key) == self.opaque
```

And `from_dict` (`:207-228`) routes on the flag — a non-adopted import gets tamper detection (*"imported opaque does not match its admission key (tamper detected)"*); setting `"adopted": true` in the record skips it.

**Determination: an adopted identity is permanently unfalsifiable.** `verify()` returns `True` unconditionally. Checks that *do* still apply: 32 lowercase hex chars, a well-formed `(authority_id, local_key)` with no `/`, non-retirement, and no opaque already bound to a different key (`_guard_opaque`, `:495`). Checks that do not: any relationship between the opaque and its admission key.

### 12.3 What is not captured

`DurableIdentity` has six fields (`:126-131`): `authority_id, local_key, opaque, urn, profile, adopted`. There is **no** provenance, no foreign-authority record, no attestation, no signature, no minting-authority reference. `authority_id` is a namespace token, not a claim about an external minter. Adoption emits a structured log line and **no evidence artifact**.

Exhaustive grep for `import_identity|external_id|foreign_id|legacy_id` across all `*.py`: **zero hits.** No federation, DID, or external-issuer protocol exists. `engine/constitution/metadata.py:64` `EXTERNAL_PREFIX = "ext:"` is unrelated — it names external *authorities* in metadata facets to terminate the certification regress (*"It is recorded, it is evidence, and it satisfies the facet — but it is not an edge"*), and ingests no identity.

### DV-17 — External ingestion bypasses integrity verification permanently, and is ungated

- **Finding.** `adopt()` accepts an externally-minted value verbatim, waives its integrity check for all time, captures no provenance, and sits outside the identity gate's measured surface.
- **Evidence.** §12.2, §12.3. Additionally, `platform/foundation/durable_identity.py` is **absent from the six `MECH-*` records** in `00-MASTER/UIS-001/uis-declaration.json`; the declaration assigns plane P2 to `00-BOOK/tools/ukb.py::allocate` instead. So the module owning `adopt()` is not crosswalked to a plane, not classified, and not measured. The gate's `identity_minting_attempts == 0` and `--check-no-identity-minting` refer to the *gate engine's own* behaviour.
- **Impact.** Trust is asserted by a boolean field on the record itself. A record can declare its own trustworthiness and thereby exempt itself from verification — and no gate observes the surface where this happens.
- **Current state.** One narrow, reasoned, self-grandfathering path with a permanent verification waiver and no provenance.
- **Desired state.** Adoption carries provenance and an attestation; the waiver is bounded and measured; the owning module is crosswalked to a plane.
- **Dependency.** DV-06 (gate coverage).
- **Classification.** **PARTIALLY ASSIMILATED** — the path is deliberate, documented and narrow; the trust model is absent.

---

## 13. Contradiction Register

Live, located, mutually inconsistent claims. **None resolved here.**

| # | Claim A | Claim B | Basis |
|---|---|---|---|
| DC-01 | `identity.py:5-8`: the id resolves the same *"regardless of … registration order"* | `resolve_kind_code`/`parse_kind_name` consult runtime-mutated globals; measured divergence §2.1 | code vs code docstring |
| DC-02 | `dictionary.py:220`: *"Identifiers the one grammar cannot parse. **Must always be empty.**"* | Non-empty in any process that has not bootstrapped CEU | declaration vs runtime |
| DC-03 | `identity.py:14-15`: *"no wall-clock, RNG, or network on the determined path (RC-4 determinism)"* | Mutable module state is an unnamed fourth non-determinism source | declaration vs implementation |
| DC-04 | `engine/uckp/identity.py`: *"Two processes on different planets in different centuries mint the same identity"* | Two processes on one machine at one instant disagree on validity (registry plane) | constitution vs runtime |
| DC-05 | `existence.py:903-905`: *"The authority owns the name→code mapping; **this function never stores one**"* | The authority stores it only in RAM, so no one stores it durably | intent vs effect |
| DC-06 | `register_kind` refuses re-coding *"because an identifier whose kind can change retroactively invalidates every reference"* | Across processes the kind space is rebuilt from scratch, so retroactive change is achievable by not registering | rule vs lifecycle |
| DC-07 | CMG-000001 **XXXI.5**: encoding **kind** into an identifier *"IS PROHIBITED"* | Every registry id encodes kind (`UCOS-<CODE>-…`); this is what forces the stateful parse | constitution vs implementation |
| DC-08 | UIS-001 `UIL-14 Verifiability` / `UIL-19 Compatibility` measured `0` violations | Measured over the ledger plane only, which uses no extension kinds — the defect is outside the measured population | measure vs scope |
| DC-09 | Test suite green on 32 `is_well_formed` assertions | All evaluate post-bootstrap; zero can observe the pre-bootstrap state | tests vs property |
| DC-10 | `verify()` — the integrity check | Returns `True` unconditionally when `adopted` is set | check vs bypass |
| DC-11 | UIS-001 declares P2 realized by `ukb.py::allocate` | `platform/foundation/durable_identity.py` claims AIF-L02/L06/L07/L13/L16 in its own docstring and is in no `MECH-*` record | declaration vs code |
| DC-12 | `AC-001/AC-009` forbid a closed enumeration | The open extension space is the sole source of non-deterministic validity — openness and determinism are implemented as a trade | constitution vs constitution |

**DC-12 is the crux.** Two constitutional obligations — open kind admission and deterministic validation — are currently satisfiable only one at a time, because openness was implemented as runtime registration rather than as declaration.

---

## 14. Reuse and Gap Analysis

Per the standing rule (`UNIVERSAL-IDENTITY-DICTIONARY-DETERMINATION.md:24`): *"The operative rule for any extension: **derive, never count.**"*

| Capability needed | Already exists | Disposition |
|---|---|---|
| Committed declaration of every kind and code | `SEED_FORMS` (53) + `SEED_CLASSIFICATIONS` (10), `engine/ceu/catalog.py` | **REUSE** — the source of truth is already committed |
| Pure name derivation | `_authority_name` (`existence.py:893-895`), a pure string transform | **REUSE** |
| Deterministic document projection of a registry | `ExistenceRegistry.to_document`/`from_document` (`existence.py:733-848`); `IdentifierDictionary` with `--write` (`engine/nucleus/cli.py`) and the sealed artifact `00-MASTER/UCOS-NUCLEUS-001/UCOS-NUCLEUS-IDENTIFIER-DICTIONARY.json` (75 KB, 212 entries) | **REUSE as the template** for a declared kind-space artifact |
| Fail-closed re-derivation on read | `IdentifierDictionary.verify()` re-mints every entry; `DurableIdentity.from_dict` refuses a contradicting value | **REUSE** — the correct validity discipline already exists |
| Collision-refusing allocation | `register_kind` (`identity.py:162-199`) | **REUSE** — the rule is right; only its durability is missing |
| Reader accepting two representations | `existence.py:834-848` (`supersession_history` vs `supersessions`, lossless) | **REUSE as the template** for representation evolution |
| Declared two-shape normalisation | `engine/lineage/memory.py:50-90`, `MODE_MAP_OF_LISTS`/`MODE_LIST_MATCH` | **REUSE as the template** |
| Named schema + version contract | `LEDGER_SCHEMA`/`LEDGER_VERSION` (`engine/uckp/evolution.py:103-111`); `SCHEMA_VERSION = 2` (`closure_engine.py:72`) | **EXTEND** — both are written and never read |
| Byte-identical replay gate | `.github/workflows/uis-gate.yml` `--render` + `git diff --exit-code` | **EXTEND** to cover the kind space |
| Closed-set disclosure register | `00-MASTER/UISD-000001/uisd-declaration.json` `closed_enumeration_disclosures` (ISD-CE-01…11) + gate | **EXTEND** — the 29-member core enum and the runtime extension space are undisclosed |
| **A validator that resolves kinds from committed data instead of process memory** | **nothing** | **TRUE MISSING** — the only one |

**Determination for §14: exactly one capability is genuinely missing** — a kind resolution path that reads committed declarations rather than mutable module state. Every supporting mechanism (committed source, pure derivation, deterministic projection, fail-closed re-derivation, replay gating, disclosure register) already exists and is tested.

Four things remain **REFUSED** by standing determinations and must not be created: a new identity universe, a second identity authority, a third dictionary, a 14-component identity stack (`UNIVERSAL-IDENTITY-UNIVERSE-DETERMINATION.md` §6).

**No new engine, authority, registry or namespace is implied by any finding in this determination.**

### Dependency structure

```
DV-11  kind space derivable from committed data but not derived   ← ROOT
   ├── DV-01  validity depends on execution history
   │     ├── DV-03  import insufficient; a call is required
   │     ├── DV-04  9 enforcement sites, incl. constitutional gateway
   │     ├── DV-07  minting equally state-dependent
   │     ├── DV-12  memoised bootstrap; first-caller coupling
   │     ├── DV-13  contradicts 3 declared identity properties
   │     └── DV-14  validation's dependency arrow reverses at runtime
   ├── DV-02  no persistence writer
   │     ├── DV-08  order-sensitive, undeclared allocation
   │     └── DV-15  openness real, durable openness absent
   └── DV-09  authority split: grammar central, vocabulary ephemeral

Independent of the root (closable by measurement alone):
   DV-05  no test observes pre-bootstrap state
   DV-06  no gate measures the property

Linked to the predecessor determination:
   DV-16  kind-in-identifier is the shared root cause of the determinism
          defect AND the XXXI.5 tension  (predecessor C-07, C-08)
   DV-10  programme-id / object-id namespace collision (predecessor IDF-06)
   DV-17  external ingestion trust model absent (predecessor §external)
```

**DV-11 is the single root.** It is not blocked by the authority problem that gates the predecessor determination's findings, because it requires no new declaration — only that the validator read what is already committed.

---

## 15. Final Determination

### 15.1 Primary question

> Is identity validity a stable property of the identity itself, or is it dependent on runtime state, bootstrap order, loaded modules, or execution history?

**Determination: DEPENDENT — on execution history, for 43 of 72 admissible kinds (59.7%).**

| Sub-question | Answer | Basis |
|---|---|---|
| Depends on runtime state? | **YES** | mutable module globals, empty at import (`identity.py:156-159`) |
| Depends on bootstrap order? | **YES** — mechanism is order-sensitive; stable today only via one caller's committed row order | measured `register_kind` collision refusal (DV-08) |
| Depends on loaded modules? | **NO — worse.** Import is insufficient; a *call* is required | measured §2.2 (DV-03) |
| Depends on execution history? | **YES** | measured §2.1, three processes |
| Is context explicitly part of validation? | **NO** | `is_well_formed(universal_id)` takes one argument; no context parameter |

The directive's own stated bar — *"must not be considered valid in one runtime and invalid in another unless the context is explicitly part of validation"* — **is not met.** The same identifier has two truth values, and no context is declared as part of the predicate.

### 15.2 Determinism classification

| Surface | Classification |
|---|---|
| Core-kind validation (29 kinds) | **deterministic** |
| Extension-kind validation (43 kinds) | **runtime dependent** |
| Extension-kind minting | **runtime dependent** |
| UCKP URN plane / UMK kernel plane / 6-digit repository regex | **deterministic** |
| **Overall** | **PARTIALLY DETERMINISTIC** |

### 15.3 Final architectural test

> *"An identity in UCOS Ω∞ has the same truth value regardless of runtime state, bootstrap order, execution history, or current software loading sequence."*

**DISPROVED by direct measurement.**

The counter-example, reproducible at `HEAD = bae59755`:

```
identifier:  UCOS-CLSS-8966ca9e8d02        (a real CEU-minted identity)

process A — fresh interpreter, no CEU bootstrap
  is_well_formed(UCOS-CLSS-8966ca9e8d02) = False

process B — fresh interpreter, bootstrap() called
  is_well_formed(UCOS-CLSS-8966ca9e8d02) = True

same commit · same machine · same instant · zero file changes
195 CEU identities and 43 of 72 kinds are affected
```

The statement holds for the UCKP URN plane, the UMK kernel plane, and the 29 core registry kinds. It fails for the 43 runtime-registered kinds — which are precisely the kinds that exist to satisfy the constitutional prohibition on closed enumeration.

**The honest summary: UCOS Ω∞ purchased infinite kind extensibility with process state, and the receipt is that identity validity is no longer a property of the identity.**

### 15.4 What the evidence does support

> *Identity **minting** is pure and clock-free on every plane. Identity **validation** is pure on three planes and process-dependent on the one plane that implements openness. The information required to make validation deterministic is already committed to the repository; it is reached through mutable module state rather than read from source.*

### 15.5 Standing

| Item | State |
|---|---|
| Determination | **COMPLETE** |
| Findings recorded | **17** (`DV-01`…`DV-17`) |
| Contradictions recorded | **12** (`DC-01`…`DC-12`) |
| Findings resolved | **ZERO** |
| Root cause identified | **DV-11** — a derivable kind space that is not derived |
| True missing capabilities | **ONE** — committed-data kind resolution |
| New engines / authorities / registries implied | **ZERO** |
| Code modified | **NONE** |
| Validators modified | **NONE** |
| CEU bootstrap modified | **NONE** |
| Registries modified | **NONE** |
| Identifier formats changed | **NONE** |
| Identities created or migrated | **NONE** |
| Requirements / ADRs / phases created | **NONE** |
| Certification altered | **NONE** |
| Repository writes | **ONE** — this document. Working tree 330 → 331 entries |

**Measurement disclosure.** All runtime measurements were pure in-memory function evaluations in throwaway interpreters. `register_kind` calls in the order-sensitivity probe (DV-08) mutated only that process's memory and were discarded on exit; no registry file, artifact, or ledger was written. One temporary file outside the repository was created and removed. No tracked file was modified.

**Two findings promoted from the predecessor determination.** DV-16 establishes that the determinism defect and the CMG-000001 XXXI.5 kind-encoding prohibition share one root cause (kind is encoded in the representation), linking findings previously treated as unrelated. DV-10 confirms the programme-id/object-id namespace collision from a second, independent direction.

---

**END DETERMINATION — STOPPED AFTER DETERMINATION.**
