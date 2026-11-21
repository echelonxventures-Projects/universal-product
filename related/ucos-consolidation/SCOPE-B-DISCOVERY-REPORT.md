# SCOPE B — Repository Authority Stabilization · Discovery Report

**Phase:** PHASE 1 — FOUNDATION COMPLETION · Scope B
**Predecessor:** Scope A / `UCPA-000001` — CERTIFIED (15/15 stages, 11,836 tests, 97% coverage). Not reopened.
**Posture:** DISCOVERY ONLY. No artifact modified, no code written, no identifier minted, no registry regenerated.
**Baseline:** working tree at Scope A certification, `integration/recovery-001`.
**Authority:** Repository Truth. Every number below was measured, not quoted.

---

## 0. Two measurement errors made and corrected during this discovery

Recorded because a discovery report that hides its own false starts cannot be trusted on the numbers it keeps.

| # | Wrong reading | Cause | Corrected reading |
|---|---|---|---|
| M-1 | "20 ledger paths are untracked, 18 with `Ω∞` in the name" | `git ls-files` applies `core.quotePath` and escapes non-ASCII, so 18 tracked files failed a string comparison | **2** untracked ledger paths. Re-measured with `-c core.quotePath=false -z` |
| M-2 | "namespace is missing on all 6,079 governed objects" | Looked for a stored `namespace` field. The repository plane *derives* it | Namespace is **derivable for 6,079/6,079**, verified by executing `engine.uckp.alignment.repository_local_urn` over the whole population |

Both corrections weakened findings I had already drafted. Neither is a defect in the repository.

---

## 1. The five named surfaces

| Named in mandate | Status | Actual location |
|---|---|---|
| `engine/uckp/` | PRESENT | `identity.py` (165), `registry.py` (422) + 27 modules |
| `engine/registry/` | PRESENT | incl. `registry/universal/` (2,353 lines, 9 modules) |
| `engine/object_birth/` | PRESENT | 1,204 lines, 6 modules |
| `engine/uga/` | **ABSENT** | UGA is not an engine package. It lives at `00-MASTER/UCOS-UGA-001/uga_engine.py` + 10 emitted surfaces |
| `engine/verification_intelligence/` | PRESENT | 3,158 lines |

**`engine/uga/` must not be created.** UGA is a programme with a declaration and an engine in Operational Memory, exactly like UAIE, UCAF and UAKOS. Creating an engine package of that name would be the parallel-authority defect the mandate forbids.

---

## 2. Current authority — the identity planes

`00-BOOK/DATA/constitutional-authority-alignment.json` → `identity_authority_resolution` is the located owner of this question, and it is unambiguous:

> `one_authority`: "UCKP-ART-05 — Universal Identity. **Every other identity mechanism in the repository is a persistence or projection binding of it.**"

| Plane | Home | Shape | Role |
|---|---|---|---|
| `CONSTITUTIONAL_OBJECT` | `engine/uckp/identity.py` | `urn:ucos:ucko:<namespace>:<local_name>` | **SUPREME — this IS UCKP-ART-05.** Pure, total, clock-free, storage-free, repository-free |
| `REPOSITORY_OBJECT` | `00-BOOK/DATA/id-ledger.json` | `UCOS-<CATEGORY>-<NNNNNN>` | **PERSISTENCE — the ONE such binding.** Append-only; `first_seen` frozen; never reissued |

The two planes are joined by a **declared, executable** derivation:

```
engine.uckp.alignment.repository_local_urn
UCOS-ENGINE-000496  ->  urn:ucos:ucko:ucos-repository:UCOS-ENGINE-000496
```

**Measured: the join succeeds for 6,079 of 6,079 governed objects, 0 failures.**

`second_authority_test`: a second identity authority is recognised by *the counter it advances*; declared `mint_markers` = `["category_seq"]`. Any Scope B extension must therefore **derive, never count**.

---

## 3. Object population containment — measured (Workstream 1)

### 3.1 The populations

| # | Population | Home | Count | Relationship |
|---|---|---|---|---|
| A | UGA universal object registry | `…/02-UNIVERSAL-OBJECT-REGISTRY.json` | **6,079** | **AUTHORITY** (current state) — derived truth, producer-owned |
| A | UGA executable object registry | `…/01-EXECUTABLE-OBJECT-REGISTRY.json` | 4,846 | **PROJECTION** of A, filtered |
| A | UGA relationship graph | `…/04-RELATIONSHIP-GRAPH.json` | — | **PROJECTION** |
| B | id-ledger `by_object` | `00-BOOK/DATA/id-ledger.json` | 4,848 | **HISTORICAL RECORD** — append-only |
| B | id-ledger `by_path` / `history` | same | 1,264 / 1,264 | **INDEX** / **HISTORICAL RECORD** (keyed by identity) |
| B | id-ledger `category_seq` | same | 117 counters | **AUTHORITY** (the one mint marker) |
| C | Book artifacts | `00-BOOK/DATA/artifacts.json` | **1,233** | **AUTHORITY** for `DOCUMENT_ARTIFACT`, owned by UMB-IMP-001 |
| C | Book relationships | `00-BOOK/DATA/relationships.json` | 12,899 edges | **DERIVED VIEW** |
| D–G | executable / test / config / data / tooling / excluded | UGA classes | see §3.3 | subsets of A |
| H | Generated artifacts | `00-BOOK/DATA/generated-artifact-registry.json` | — | **PROJECTION**, declared |
| — | Birth ledger | `00-MASTER/UOBC-000001/birth-ledger.json` | **35** | **AUTHORITY** on the constitutional plane |
| — | Capability catalogue | `intelligence/UCOS-RIE-CAPABILITY-CATALOG.json` | 129 | **DERIVED VIEW** |

### 3.2 The 4,848 vs 4,846 difference is correct, and here is why

Exactly **2** ledger paths are absent from the current registry:

| Path | On disk | Reason |
|---|---|---|
| `.ucos-verification-evidence/ruff/9b37e224….json` | yes | gitignored verification-evidence cache; outside the UGA eligibility boundary |
| `CURRENT-REPOSITORY-STATE.txt` | **no** | deleted |

Both are `RETIRED` — a **declared** lifecycle state: *"Previously minted an identity, no longer carried by version control. Identity is retained (append-only) and never reissued."*

**This is not drift.** It is the ledger behaving as a historical record while the registry behaves as current-state authority. The difference is the proof that the two are correctly *different kinds of thing*.

### 3.3 The six required invariants, measured over all 6,079

| Invariant | Coverage | Mechanism |
|---|---|---|
| **Universal ID** | **6,079 / 6,079** | `universal_id` |
| **Owner** | **6,079 / 6,079** | `owner`; 5 ownership rules ending in a total catch-all (`<file> at root → UCOS-REPOSITORY-ROOT`) |
| **Namespace** | **6,079 / 6,079 (derived)** | `repository_local_urn` → `ucos-repository`. Executed over the whole population, 0 failures. Not stored per-entry, correctly — a derivable fact stored redundantly is a second truth |
| **Type** | **6,079 / 6,079** | `object_class`, 7 declared classes |
| **Lifecycle** | **6,079 / 6,079** | `AUTHORED` 5,735 · `GENERATED` 344 (+ `RETIRED` retained in ledger) |
| **Lineage** | **PLANE-SPLIT — see §3.4** | three different shapes |

Class distribution: `EXCLUDED_DOCUMENT` 2,582 · `EXECUTABLE_OBJECT` 1,254 · `DOCUMENT_ARTIFACT` 1,233 · `TEST_OBJECT` 821 · `DATA_OBJECT` 122 · `TOOLING_OBJECT` 36 · `CONFIGURATION_OBJECT` 31.

### 3.4 Lineage is not absent — it is three-shaped, and that is the finding

| Population | Lineage mechanism | Coverage |
|---|---|---|
| `DOCUMENT_ARTIFACT` (1,233) | `parent` in `artifacts.json` | **1,232 / 1,233** (the 1 is the declared root, `UCOS-BOOK-000000`) |
| Repository plane (4,846) | `first_seen` origin + `dependencies` (1,920) / `produces` (41) + 12,899 relationship edges | origin **4,846 / 4,846** |
| Constitutional plane (35 births) | `parent_identity` (`UOBC-F-06`) | **35 / 35** |

`first_seen` is absent for exactly **1,233** objects, and that set is **exactly** the `DOCUMENT_ARTIFACT` class — the one class UGA declares it does not mint for (*"governed_by UMB-IMP-001 (pre-existing). This programme registers NOTHING here"*). The absence aligns precisely with a declared plane boundary rather than cutting across it.

**GAP B-1 (the real one): there is no single query that answers lineage — or any identity question — uniformly across the three planes.** Each plane answers correctly in its own shape; nothing composes them. This is precisely Workstream 3's requirement, and it is a **composition over existing authorities**, not a new authority.

---

## 4. Birth governance — current reach (Workstream 2)

- Birth records: **35**. Governed objects: **6,079**.
- `UOBC` declares 7 stages, 9 mandatory fields, 4 namespaces, 8 laws — all **8 PASS**.
- Identity comes into being at `UOBC-S-04` (ordinal 40); `UOBC-L-01` refuses any stage instantiating an artifact at or below it.

**This is not 6,044 missing birth records.** `UNIVERSAL-IDENTITY-MIGRATION-DETERMINATION.md` already measured the population and found **0 anonymous objects** — every unregistered artifact holds UGA identity as `EXCLUDED_DOCUMENT`. Corpus-wide birth adoption is pre-existing gap **G11**, and its disposition is **already determined**: an explicit `register.sh` migration transaction, **not a verification-time backfill**.

**Workstream 2 is therefore a scoping determination — which object classes require birth records — not a generation run.** The mandate's own words: *"Do not blindly generate."*

---

## 5. Registry coverage — first pass (Workstream 5)

38 registry-shaped artifacts located. Authority declaration is **not uniformly shaped**:

| Shape | Examples |
|---|---|
| Top-level `authority` | UGA surfaces, `birth-ledger.json`, RIE catalogue, `canonical-observation-audit.json`, `generated-artifact-registry.json`, `exclusion-register.json` |
| Domain-specific key | `uis-declaration.json` (`classification_authority`), `ucl-declaration.json` (`lifecycle_authorities`), `ucaf-authority.json` (`authority_sources`) |
| **None in-file** | `artifacts.json`, `id-ledger.json`, `relationships.json`, `volumes.json` |

**Correction to a finding I initially drafted:** `id-ledger.json` is *not* an undeclared authority. Its standing is declared **externally and precisely**, in `constitutional-authority-alignment.json` → `identity_authority_resolution.planes[REPOSITORY_OBJECT]`, role `PERSISTENCE`. The same holds for `artifacts.json` via UMB-IMP-001.

**GAP B-2: authority standing is declared in three different places and three different shapes.** No single instrument answers "what is this registry, who owns it, what is its standing" for all 38. That is the `REGISTRY-COVERAGE-MATRIX` deliverable.

---

## 6. Prior determinations that bind this scope

| Determination | What it fixes for Scope B |
|---|---|
| `UNIVERSAL-IDENTITY-UNIVERSE-DETERMINATION.md` §6 | Refuses by name: a new identity universe, a second identity authority, **a third dictionary**, a 14-component identity stack. **All four refusals stand.** |
| `UNIVERSAL-IDENTITY-DICTIONARY-DETERMINATION.md` §3 | The UID Dictionary **already exists** — `engine/registry/universal/dictionary.py`, `IdentifierDictionary`, 346 lines, schema `ucos-universal-identifier-dictionary`. It is **in-memory only**. |
| same, §"What is deliberately NOT determined here" | **G3** (persist the dictionary), **G4** (temporal/lifecycle/evolution/certification state on an entry), **G9** (child index) are declared **the sanctioned extension points**, deliberately not exercised, each requiring *its own determination and mutation-class registration*. |
| `UNIVERSAL-IDENTITY-MIGRATION-DETERMINATION.md` | 0 anonymous objects; G11 disposition = explicit migration transaction. |

**Workstream 4 says "Create only if missing." It is not missing.** The correct action is to exercise **G3**, which is already sanctioned and already carries a stated compliance path: a persisted dictionary is either derived truth (⇒ replay-gated, byte-stable, producer-owned) or governed evolution state (⇒ declared in `mutation-governance-boundary.json` with a named transaction owner).

---

## 7. Gap register

| ID | Gap | Class | Disposition |
|---|---|---|---|
| **B-1** | No uniform cross-plane identity query ("what/who/whence/when/what-became/what-depends") | **NEW — in scope** | Workstream 3: compose over existing authorities; mint nothing, count nothing |
| **B-2** | Registry standing declared in 3 shapes across 3 locations; no single matrix | **NEW — in scope** | Workstream 5: `REGISTRY-COVERAGE-MATRIX` |
| **B-3** | Which object classes *require* birth records is undetermined | **NEW — in scope** | Workstream 2: scoping determination |
| G3 | Dictionary not persisted | pre-existing, **sanctioned** | Workstream 4 candidate — requires its own mutation-class registration |
| G4 | Entry lacks temporal/lifecycle/evolution/certification state | pre-existing, sanctioned | stacked on G3 |
| G9 | No child index on identifier plane | pre-existing, sanctioned | stacked on G3 |
| G6 | Certification not keyed on `universal_id` | pre-existing | **out of scope**, owned elsewhere |
| G8 | No vector/temporal index over identity population | pre-existing | **out of scope** |
| G11 | Corpus-wide birth adoption | pre-existing | **out of scope** — disposition already determined |

---

## 8. Discovery sequence — completion record

| Step | Status |
|---|---|
| Repository Truth Discovery | COMPLETE — 5 surfaces located, 1 (`engine/uga/`) proven absent by design |
| Existing Capability Discovery | COMPLETE — `IdentifierDictionary` located; Workstream 4 is EXTEND, not CREATE |
| Existing Implementation Discovery | COMPLETE — 2 planes, 1 declared join, executable on 6,079/6,079 |
| Reuse Analysis | COMPLETE — §2, §6 |
| Duplicate Detection | COMPLETE — no duplicate identity authority found; `category_seq` is the sole mint marker |
| Ownership Verification | COMPLETE — owner 6,079/6,079; registry standing split (B-2) |
| Dependency Analysis | COMPLETE — 12,899 relationship edges; 1,920 dependency-bearing objects |
| Gap Determination | COMPLETE — B-1…B-3 new; G3/G4/G9 sanctioned; G6/G8/G11 out of scope |
| Implementation Decision | **DEFERRED** — no code written |

---

## 9. Quality-gate pre-check

| Gate | Pre-implementation status |
|---|---|
| Zero duplicate authority | **HOLDS** — one identity authority, one mint marker, one persistence binding |
| Zero duplicate registry | **HOLDS** — 38 registries, each with a distinct located subject |
| Zero identity ambiguity | **HOLDS** — join executes 6,079/6,079, 0 failures |
| Zero hidden objects | **HOLDS** — 6,079 governed = 6,079 tracked files |
| Zero orphan artifacts | **HOLDS** — 0 anonymous (migration determination); 2 RETIRED are declared |
| Zero unowned capabilities | **HOLDS** — owner 6,079/6,079 |
| Zero undocumented exceptions | **AT RISK** — B-2 |

---

*End of SCOPE-B-DISCOVERY-REPORT.md*
