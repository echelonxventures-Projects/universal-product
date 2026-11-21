# UCOS Ω∞ — PHASE 1 ARCHITECTURE
## Universal Discovery Abstraction Layer

**AUTHORITY = NONE (DERIVED TRUTH).** This document describes an architecture. It issues no
certification, seals no governance artifact and modifies no production governance decision.

**STATUS.** Implemented, tested, verified. Not certified, not sealed, not wired into any gate.

---

## 1. THE FOUR ASSUMPTIONS, AND WHERE EACH ONE LIVED

Phase 1 exists to remove four architectural assumptions. They were not opinions written in a
document — each was a line of executable code with no seam around it.

| Assumption | Where it lived | What it made impossible |
|---|---|---|
| Discovery is `git ls-files` | `engine/universal_discovery/discovery.py:tracked_python` | Any population not held in a git index |
| An artifact is a tracked Python file | `engine/universal_discovery/model.py:Artifact` — 4 of its fields are Python | Describing a document, a dataset, a workflow, an object |
| Storage is a local filesystem | Implicit in every `open(os.path.join(root, path))` | Any content behind a network boundary |
| Scope is a repository root | `root: str = "."` on `build`, `evaluate`, `derived_scope` | A bucket, a registry, a federation, a graph |

The critical property of all four: **they could not be interrogated.** There was no place in the
code where "is this population tracked?" was a *question*, so there was no place a different
answer could be given. An assumption that cannot be asked about cannot be replaced.

### RULE Ω-1, as implemented

> git, Python, "repository" and "filesystem" are now **values inside registries** rather than
> **terms inside control flow.**

Nothing in `engine/omega_infinite/` branches on any of the four. Verified structurally by
`engine/tests/omega_infinite/test_artifact.py::test_the_model_carries_no_language_specific_field`,
which asserts the universal `Artifact` declares none of `module`, `statements`, `callables`,
`imports`, `path`, `root`.

---

## 2. THE LAYER

```
                    ┌──────────────────────────────────────────────┐
                    │              KnowledgeSpace                  │  D5
                    │  the bounded world a measurement is over     │
                    │  REPOSITORY · FILESYSTEM · BUCKET ·          │
                    │  REGISTRY · FEDERATION · GRAPH  (open)       │
                    └────────────────────┬─────────────────────────┘
                                         │ holds a
                    ┌────────────────────▼─────────────────────────┐
                    │             ProviderRegistry                 │  D1
                    │  resolution BY CAPABILITY, never by name     │
                    └────────────────────┬─────────────────────────┘
                                         │ resolves a
                    ┌────────────────────▼─────────────────────────┐
                    │            DiscoveryProvider                 │  D1
                    │  identifier() enumerate()                    │
                    │  metadata()   capabilities()                 │
                    └───────┬──────────────────────────┬───────────┘
                            │                          │            D2
                ┌───────────▼──────────┐  ┌────────────▼──────────┐
                │ GitDiscoveryProvider │  │ FilesystemDiscovery   │
                │ priority 100         │  │ Provider  priority 10 │
                │ TRACKED · VERSIONED  │  │ LOCAL · HASHING       │
                │ LOCAL · HASHING      │  │ (and NOTHING else)    │
                │ AUTHORITY_METADATA   │  │                       │
                └───────────┬──────────┘  └────────────┬──────────┘
                            └────────────┬─────────────┘
                                         │ emits
                    ┌────────────────────▼─────────────────────────┐
                    │                  Artifact                    │  D3
                    │  identifier · location · type · authority    │
                    │  metadata · relationships                    │
                    └────────────────────┬─────────────────────────┘
                                         │ typed by
                    ┌────────────────────▼─────────────────────────┐
                    │          ClassificationPipeline              │  D4
                    │  1 provider-declared   ← strongest           │
                    │  2 content-interpreter                       │
                    │  3 content-structure                         │
                    │  4 suffix              ← WEAKEST, LAST       │
                    │  5 UNKNOWN             ← unconditional       │
                    └──────────────────────────────────────────────┘

        Capability (D6) is orthogonal: every provider self-declares, nothing assumes.
```

### Module map

| Module | Deliverable | Responsibility |
|---|---|---|
| `capability.py` | D6 | What a provider may be *asked*. `Capability`, `CapabilityRegistry`, `CapabilitySet` |
| `artifact.py` | D3 | What is *found*. `Artifact`, `ArtifactType`, `Location`, `Authority`, `Relationship` |
| `classification.py` | D4 | What it *is*. Pipeline of injected classifiers, extension last |
| `provider.py` | D1 | How it is *found*. Contract, `Selector`, registry, capability resolution |
| `git_provider.py` | D2 | Git as **one** provider |
| `filesystem_provider.py` | D2 | Discovery with **no VCS of any kind** |
| `knowledge_space.py` | D5 | *Where*. `KnowledgeSpace` and its kinds |
| `compat.py` | D7 | Proof nothing changed |
| `evidence.py` | — | The five criteria, discharged by execution |
| `__main__.py` | — | Read-only CLI. **No write mode exists** |

---

## 3. THE THREE DESIGN DECISIONS THAT CARRY THE ARCHITECTURE

### 3.1 Registries, not enums

Every vocabulary — capabilities, artifact types, space kinds, relationship kinds, classifiers — is
a **registry of value objects**, never an `Enum`.

An `Enum` member cannot be added at runtime, so an enum would mean that supporting a new kind of
anything requires editing this package. That is the structural limit Phase 1 exists to remove.

**Nothing in the package quantifies over any of the named tuples** (`WELL_KNOWN`, `INITIAL_TYPES`,
`KINDS`). There is no dispatch, no validation, no branch. A value absent from those lists works
identically — which is the property that makes each list *safe to be incomplete*, and each one
permanently is.

Registries are **open for extension, closed to redefinition**: re-declaring a name with a
different description is refused. One name with two meanings makes every requirement on that name
unenforceable, which is worse than two names.

### 3.2 Capability declaration is what makes the abstraction honest

Without `capabilities()`, a caller holding an interface it cannot interrogate must *assume*. The
filesystem provider genuinely cannot offer the eligibility boundary that git provides, and the
correct response is not to forbid it from existing — it is to require it to **say so**:

```python
FilesystemDiscoveryProvider.capabilities().names()
# ('CONTENT_HASHING', 'LOCAL_STORAGE')          ← and NOTHING else

GitDiscoveryProvider.capabilities().names()
# ('AUTHORITY_METADATA', 'CONTENT_HASHING', 'LOCAL_STORAGE',
#  'TRACKED_CONTENT', 'VERSIONED_CONTENT')
```

The difference between those two tuples is **machine-readable**. "What do I lose by discovering
without version control" therefore has a computable answer instead of a prose one, and a
measurement that needs the boundary gets a refusal naming the provider rather than a silent
difference in behaviour between a developer's machine and a clean checkout.

Resolution is **by capability, never by name**. `resolve_capable(TRACKED_CONTENT)` is what a
measurement calls; `resolve("git")` exists for evidence and tests. Selecting by name would
re-introduce the assumption one layer up — the code would once again say "git".

### 3.3 Extension is last, so no classification *depends* on it

The directive requires classification independent from file extension. Independence is not achieved
by deleting extension logic — a suffix is real evidence and discarding it would make the layer
worse. It is achieved by ordering:

1. **provider-declared** — the system of record already knew
2. **content-interpreter** — the bytes name their own interpreter
3. **content-structure** — the bytes have a recognisable shape
4. **suffix** — a name typed by whoever created the artifact
5. **UNKNOWN** — unconditional, and a *named, countable* population

Renaming an artifact can only change its type when nothing stronger had an opinion. That is the
honest amount of authority a filename deserves.

**One vocabulary, two access paths.** The suffix classifier and the interpreter probe read the same
injected `TypeVocabulary`. A hard-coded "shebang mentions python → PYTHON" branch would be a second
language list, disagreeing with the first the moment either changed.

---

## 4. WHAT PHASE 1 DELIBERATELY DOES NOT DO

| Not done | Why that is correct |
|---|---|
| Object storage, registries, federations, graphs | Phase 1's goal is to remove the structural limit, not to support every platform. Each of the four is a **registration**, demonstrated by `knowledge_space.space_of` and `evidence.expansion_probe` |
| Replace `engine/universal_discovery` | Phase 1 is additive. Ω-1 is untouched: same entry points, same population, same dispositions, same ratchets |
| Wire into `verify.sh` or CI | Explicitly forbidden. The CLI surface is registered via `scripts/omega-infinite.sh` without being a gate stage |
| Any writing mode | Forbidden: no certification, no reseal. `__main__.py` has no `--seal`, and nothing in the package opens a file for writing |
| Derive authority | `Authority` is **carried**, not computed. Ω-2's seven-rule chain is repository-specific; a bucket provider will have a different one |
| Count statements | A Python analyser does that and attaches the result through `metadata`. Putting it in the model is what made Ω-1's model Python-only |

---

## 5. VERIFICATION

### 5.1 The five success criteria

Run: `./scripts/omega-infinite.sh` or `python3 -m engine.omega_infinite`

| Criterion | Claim | Experiment |
|---|---|---|
| Ω∞-1 | discovery operates through abstractions | population obtained via resolved space + resolved provider; 2197 artifacts |
| Ω∞-2 | Git is a provider, not a dependency | filesystem provider enumerates with **no git/hg/svn/p4 consulted**, and declares neither `TRACKED_CONTENT` nor `VERSIONED_CONTENT` |
| Ω∞-3 | Python is a type, not an assumption | artifact with **no extension** typed PYTHON from its shebang; universal `Artifact` carries **zero** Python fields |
| Ω∞-4 | repository roots are knowledge spaces | root resolves to a space declaring its kind and guarantees; a non-repository resolves too |
| Ω∞-5 | expansion needs no redesign | a capability, a type, a space kind **and** a provider all registered **at runtime** with zero edits |

Ω∞-5 is the load-bearing one. The first four could be satisfied by a well-factored special case;
the fifth cannot.

### 5.2 Deliverable 7 — measured, not asserted

```
IDENTICAL — 2197 artifacts, same order, same membership.
The abstraction reproduces Ω-1 exactly.
```

`compat.equivalence()` compares `discovery.tracked_python(root)` against
`repository_space(root).discover(Selector(patterns=("*.py",))).locators()` and asserts **tuple**
equality — order is part of the claim, because a set comparison would pass for a population
containing the same files in a different sequence, and every digest in UCOS-OMEGA-001 is computed
over an ordered structure. The comparison is **two-directional**: a one-directional check is
satisfied by a subset and would hide over-collection.

### 5.3 Tests and lint

```
159 passed
coverage of engine.omega_infinite  = 100.00%  (909 stmts, 150 branches, 0 miss)
ruff check (E,F,I,B,UP,S @100)     = All checks passed
ruff format --check                = 20 files already formatted
```

### 5.4 Ω-1 gate under the Phase 1 change set

Measured with a **throwaway git index** (`GIT_INDEX_FILE`), so the real index and the concurrently
running validation were never touched:

```
PASS — all five Ω criteria hold, and none of them consulted a list.
tracked python 2217 (was 2197, +20)   relocation invariance holds for all 2217

IMPROVED   unmeasured_surface_density   0.096989 → 0.096236
IMPROVED   import_entropy               8.007283 → 7.997294
IMPROVED   statement_entropy            6.397527 → 6.382844
HELD       unreachable_artifacts        53.0      (added ZERO unreachable artifacts)
HELD       authority_of_last_resort      0.0
HELD       declared_exemptions          10.0
HELD       unresolved_dynamic_sites     22.0
JUSTIFIED  unexplained_exemptions        2.0      (declared floor)
JUSTIFIED  unnameable_exemptions        49.0      (declared floor)
```

**Three ratchets improved, six held. None regressed. Nothing was resealed.**

### 5.5 The Ω-1 property, demonstrated on this very change

`engine.omega_infinite` entered the coverage denominator (80 → 81 measurable packages) with
**zero edits to `pyproject.toml`**. That is Ω-1's own success criterion — a new tree governed on
the commit that creates it — exercised by the commit that introduces its successor.

---

## 6. ISOLATION GUARANTEE

A full validation run was executing throughout this work. Every one of these held:

- **Zero existing files modified.** `git status --porcelain` non-untracked entries are byte-identical
  to the session-start snapshot.
- Additions are exactly three untracked paths: `engine/omega_infinite/`,
  `engine/tests/omega_infinite/`, `scripts/omega-infinite.sh`.
- **Nothing staged.** The git index was never written, because in-flight tests call
  `gate.evaluate(".")` and `discovery.tracked_python()` against the real index — staging mid-run
  would change what a running test sees.
- Gate verification used a copied throwaway index, since deleted.
- New tests were run with `--no-cov -p no:cacheprovider`, so no `coverage.xml` and no pytest cache
  were written.
- `pyproject.toml`, `verify.sh`, `.github/`, all ratchet files and all coverage configuration:
  untouched.

---

## 7. COMPANION DOCUMENTS

| Document | Contents |
|---|---|
| `PHASE1_PROVIDER_MODEL.md` | D1, D2, D6 — the contract, the two providers, capability declaration |
| `PHASE1_ARTIFACT_MODEL.md` | D3, D4 — the universal artifact and the classification pipeline |
| `PHASE1_KNOWLEDGE_SPACE_MODEL.md` | D5 — knowledge spaces and the six kinds |
| `PHASE1_MIGRATION_PLAN.md` | D7 — how Ω-1 migrates onto the layer, in reversible steps |
