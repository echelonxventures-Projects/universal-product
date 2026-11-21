# UCOS Ω∞ — UNIVERSAL ASSIMILATION COVERAGE DETERMINATION

| Field | Value |
|---|---|
| ARTIFACT | `UCOS-OMEGA-INFINITY-ASSIMILATION-COVERAGE-DETERMINATION.md` |
| CLASSIFICATION | `EVIDENCE` — assimilation determination |
| AUTHORITY | **NONE — DERIVED TRUTH.** Legislates nothing, ratifies nothing, certifies nothing, assigns no ownership, allocates no identity, changes no certification state. Where this determination and a located instrument differ, **the located instrument governs.** |
| DISPOSITION | **ASSIMILATION ONLY.** No artifact deleted, removed, renamed or merged. No source code modified. No registry mutated. No identity minted. No programme ID created. No requirement created. No ADR created. No restructuring. No remediation. |
| SUBJECT | Assimilation state and coverage of fourteen universal dimensions |
| BASELINE | HEAD `bae59755` · branch `integration/recovery-001` · working tree **59 uncommitted entries at open and 59 at close** (verified by `git status --porcelain \| wc -l` at both boundaries) |
| MODE | Read-only. Discovery → Assimilation → Understanding → Classification → Relationship Mapping → Ownership Discovery → Authority Discovery → Evidence Mapping → Gap Identification |
| METHOD | Content search (not filename search) across `engine/`, `platform/`, `intelligence/`, `realization/`, `service/`, `application/`, `infrastructure/`, `data/`, `knowledge/`, `adr/`, `scripts/`, `.github/workflows/`, `00-MASTER/`, `00-BOOK/`, `00-CMG/`, `00-CEP/`, `02-MASTER/`, root determination series · plus **live read-only execution** of five gates and one predicate-coverage validator (§9.2) |
| REFUSES | Declaring a dimension MISSING because no document or module carries its exact name · treating a discovered population count as a universal boundary · creating a fifteenth registry · claiming enforcement without a named executable check |
| STOP CONDITION | Assimilation complete. No implementation, remediation, optimization, refactoring or certification change performed or authorized. |

> **Headline.** Fourteen dimensions assimilated. **None is MISSING. None is DOCUMENTATION ONLY.** Nine are EXISTING IMPLEMENTATION; five are PARTIAL. Every dimension exists in executable code under a **local name that differs from the dimension name** — the repository's vocabulary is `UISD` / `UCKO` / `CEU` / `UCXI` / `UCIC` / `UKIP` / `ULP` / `UEG` / `UCL` / `UVI` / `UGA` / mutation-governance-boundary, not the dimension names as posed. The recurring shape of residual gap is **never absence of capability**. It is one of three things: (i) **absence of a join** — two planes measuring one subject with no declared join key; (ii) **absence of a ratchet** — a real detector that audits only what has already been disclosed to it; (iii) **absence of universality in the enforcement, not in the model** — a correct model enforced per-owner rather than across the whole population. One dimension, Universal Memory Evolution, is partial **by constitutional design**: a store is explicitly forbidden, so partial is the intended terminal state.

---

# PART I — CURRENT REPOSITORY STATE

## 1.1 Measured state

Every count below is a **currently discovered population**, not a boundary. §1.3 states, per count, whether the code *enumerates* it as a closed set or *discovers* it as data — that distinction, not the number, is the governed property.

| Surface | Discovered population | Enumerated or discovered? |
|---|---|---|
| Concepts under closure | **549** (`UAKOS-CLOSURE-002: CLOSED · gaps=0` across 7 gap classes, live at session open) | Discovered — walked from registers |
| Repository Requirements (`RR-<CONCEPT-ID>`) | **549** — 1:1 with concepts | Derived: identity is a total injective function of concept identity |
| Requirements (`REQ-NN`, manual plane) | **49** | Hand-curated markdown; no join key to the 549 (§11 O-9) |
| Generated artifacts | **345** entries · `bootstrap_gaps` **empty** | Discovered — `load()` reads the register |
| Mutation classes / rules | **9 / 9** (R-01…R-09) | Declared as data; **no Python `MutationClass` enum exists** |
| Rule predicates implemented | **8** (R-01…R-08) | Code — and this asymmetry is a live finding (§11 O-14) |
| CI gate workflows | **29** `*-gate.yml` + `determinism.yml` + `ec1-ci.yml` | Files; 27 assert determinism/replay/audit |
| `verify.sh` stage literals | **14** always-run **+1** under `--full` | Re-derived **by regex from source** by the gate — admitting a stage is a data change |
| Universal facets (UCKO) | **33** | **Closed by design**, disclosed as intentional |
| Entity kinds (birth scope) | **10** | Ordered first-match-wins + **mandatory catch-all** → total by construction |
| Seed relationship types | **17** types · **17** topologies | Data rows in `SEED_RELATIONSHIP_TYPES`; type space constrained by *pattern, never enum* |
| Universal context kinds | **15–16** | `ContextTaxonomy.extend()` — bounded open-world, a new taxon names an existing parent |
| Lifecycle stages | **45** (UCL constitutional graph) · **15** (UCIC capability) · **15** (Article 14 evolution) | Data in `ucl-stage-manifest.json`; `verify_manifest_alignment()` fails closed on drift |
| Architectural catalog | **112** universes → **499** domains → **2027** capabilities | Architectural inventory (`ARCH-001/002/003`), authority-neutral |
| Realized capability CKOs | **131** `UCKO-CAP-*` sealed to `knowledge_seal 71c65cf5…` | Generated by `URI-000001` from canonical knowledge |
| Identity ledger entries | **6,178** · `page_cursor` monotonic, never decremented | Sticky UID→page; retired entries retained in `by_path` |
| Working tree | 59 uncommitted entries (27 modified · 32 untracked) | Pre-existing; unchanged by this determination |

## 1.2 The constitutional tri-partition of state

`00-MASTER/UCOS-RECON-C1-OPERATIONAL-MEMORY-EXCLUSION.md` states it verbatim, and it is the single most load-bearing fact for reading any count in this repository:

> "Repository Corpus = knowledge state (registered). Operational Memory = execution state (`00-MASTER/`, never registered). Generated Projections = derived state (regenerated, never authoritative). The three are now never mixed."

Implemented by adding `"00-MASTER/"` to `EXCLUDE_DIR_PREFIXES` in `00-BOOK/tools/config.py`, applied in both `_iter_files()` and `_iter_files_walk()`. Registered artifacts moved 436 → 423. **Fourteen sticky UIDs were RETAINED-BUT-RETIRED** — no renumber, no ID reuse, `by_path` history preserved. Operational Memory therefore *exists as a governed category with a record*; it is simply never a corpus artifact. **Nothing was discarded to achieve the exclusion.**

## 1.3 Interpretation rule, applied

The directive's rule is not commentary here — it is the repository's own doctrine, and it is enforced by executable law.

| Reading to refuse | Correct reading | Enforced by |
|---|---|---|
| "549 requirements" = the maximum | Current discovered requirement population; identity is derived from concept identity, so the population grows when concepts do | `requirement_engine.py:18-20` — identity is "a total, injective, derived function of the existing concept identity" |
| "Python" = the universal runtime | Current execution manifestation | `ISD-L-09` `check_technology_is_evolutionary_state` (`engine/infinite_scope/contract.py:473`): `pyproject.toml` runtime deps must be empty, `requires-python` may carry **no** `<`/`<=`/`==`, every verification-toolchain pin must be disclosed with a reason |
| "Earth" = the universal location model | Current spatial context | `adr/0012-remove-residual-planetary-default.md`; `engine/context/location.py` + `location_assurance.py` |
| "33 facets" = arbitrary closure | Closure **disclosed as intentional** with a closing invariant and an admission path | `ISD-L-01` — the defect is a closure that is *silent*, not a closure |
| "45 stages" = hardcoded lifecycle | Stages are data; the engine holds no stage id | `verify_manifest_alignment()`; `OMEGA-E06` §3 "Stages configurable? **YES**" |
| "17 relationship types" = the closed vocabulary | Seed rows; type space constrained **by pattern, never by enum** | `ISD-L-02` `check_direction_expansion_capacity` |
| "10 entity kinds" = the closed kind set | Ordered classification with a **mandatory final catch-all**, so classification is total for kinds nobody has named | `BSP-L-02` requires the catch-all to exist and to be last |
| "14 verify stages" = a fixed script | Labels are **re-derived by regex from source** and digest-matched | `uisd-gate.yml:266,279-280` |
| "9 mutation classes" = a fixed enum | **No `MutationClass` enum exists.** Classes are strings read from `mutation-governance-boundary.json` | `mutation_classification.py` — "THE RULES ARE DATA, NOT CODE" |
| "345 generated artifacts" = the whole population | Register contents, loaded at runtime | `generated_artifacts.py:170-233` `load()`/`canonical_paths()` |

**Assimilation finding.** The interpretation rule is not merely respected by this determination — it is **already installed as law** in eleven independent places. The repository's own doctrine (`engine/infinite_scope/contract.py:16-20`) is that *closure is not a defect; undisclosed closure is.*

---

# PART II — CURRENT ASSIMILATED STATE

## 2.1 Verdict distribution across fourteen dimensions

| Classification | Count | Dimensions |
|---|---|---|
| **EXISTING IMPLEMENTATION** | **9** | Infinite Expansion · Entity Model · Relationship Evolution · Context Evolution · Knowledge Evolution · Execution Governance¹ · Lifecycle Governance¹ · Verification Governance · Mutation Governance |
| **PARTIAL IMPLEMENTATION** | **5** | Agnostic Architecture · Capability Evolution · Memory Evolution² · Requirement Evolution · Artifact Governance³ |
| **DOCUMENTATION ONLY** | **0** | — |
| **MISSING** | **0** | — |

¹ Existing for its governed population; a named sub-population is uncovered (§11 O-6, O-8).
² Partial **by constitutional design** — `ADR-0013` / `UCI-001 Part XVI.5` forbid a memory store.
³ Model and identity rules are complete and executable; the **drift gate is per-owner, not universal** (§11 O-13).

## 2.2 Assimilation posture per pipeline stage

| Pipeline stage | State | Basis |
|---|---|---|
| Discovery | **COMPLETE for the fourteen** | Every dimension resolved to ≥1 executable owner |
| Assimilation | **COMPLETE** | No dimension remains conversation-only; all are written to this artifact |
| Understanding | **COMPLETE** | §4 states, per dimension, the mechanism — not just the location |
| Classification | **COMPLETE** | §2.1, §4 |
| Relationship mapping | **COMPLETE** | §5 (inter-dimension) and §6 (the six relationship properties tested) |
| Ownership discovery | **COMPLETE** | §8 — every dimension has ≥1 named owner; **no dimension is unowned** |
| Authority discovery | **COMPLETE** | §9 — the four-tier pattern is uniform and self-declared |
| Evidence mapping | **COMPLETE** | §10 — five distinct buckets: code · declaration · CI-gate · test · live-run |
| Gap identification | **COMPLETE** | §11 — 16 open observations, each traced to a named gap id where one exists |
| **Requirement-plane assimilation** | **INCOMPLETE — 25.5% measured live** | §9.2 · 140 of 549 FULLY ASSIMILATED · 12 open gap classes · baseline WITHHELD |

## 2.3 What was preserved

No artifact was deleted, removed, renamed, merged, or restructured. No registry was mutated. No identifier was allocated. No certification state was changed. No historical evidence was altered.

**Full disclosure of the one mutation that occurred and was reverted.** During the prior cycle, `00-MASTER/UAKOS-CLOSURE-009/requirement_engine.py --gate` proved **not** to be read-only: the `--gate` path regenerated eleven registers plus `requirements.json` against live HEAD instead of the recorded baseline. Those twelve files were restored to their committed state with `git checkout --` on exactly those paths; no other path was touched, and the working-tree entry count returned to its pre-invocation value of 59. **The measurement obtained before restoration is retained as evidence in §9.2 — the finding survives; the mutation did not.** This event is itself an assimilated finding: it is a **gate-purity violation by an owner whose own workflow declares a purity step**, and it is recorded as O-11.

---

# PART III — EXISTING CAPABILITY MAPPING

## 3.1 Dimension → located owner → local name → authority

**This is the operative table.** The left column is the query vocabulary; the middle columns are the repository's own.

| # | Dimension as posed | Located canonical name | Owning code | Instrument | Self-declared authority |
|---|---|---|---|---|---|
| 1 | Universal Infinite Expansion | **Universal Infinite Scope and Direction** | `engine/infinite_scope/` | `UISD-000001` · `ADR-0022` UIEP-001 | Declaration-driven; gate fail-closed |
| 2 | Universal Agnostic Architecture | **Universal Agnostic Architecture Principle** | `engine/uckp/persistence.py` · `platform/universal_provider/` · `engine/provider/metatypes.py` | `UAP-001` (`adr/0021`) · `UPF-000001` | **"DESIGN PRINCIPLE — not a certification"** |
| 3 | Universal Entity Model | **Universal Constitutional Knowledge Object** + **Universal Object Birth Contract** | `engine/uckp/ucko.py` · `engine/uckp/identity.py` · `engine/object_birth/` | `UCOS-UCOM-001` · `UOBC-000001` · `UOBC-BSP-001` · `UCOS-UGA-001` | `UniversalIdentity` role **SUPREME** = UCKP-ART-05 |
| 4 | Universal Relationship Evolution | **Relationship as a unit of existence** + **UKIP relationship closure** | `engine/ceu/existence.py` · `engine/knowledge/ukip/relationships.py` · `engine/graph/model.py` · `data/relationship.py` | `UCRD-001` · `UCKP-ART-07` (`adr/0015`) · `adr/0023` | Registry-driven; type set is data |
| 5 | Universal Context Evolution | **Universal Context Intelligence** | `engine/context/` (18 modules) | `UCXI-000001`; bound by `CMG-000012` | Model owns itself; `CMG-000012` owns only the binding |
| 6 | Universal Capability Evolution | **Universal Capability Implementation Contract** + **Universal Autonomous Evolution** | `engine/uaue/` · `engine/uckp/evolution.py` · `engine/registry/universal/` · `realization/` | `UCIC-001` (FROZEN v1.0) · `UAUE-000001` · Article 14 · `URI-000001` | `UCIC-001` = architecture owner |
| 7 | Universal Knowledge Evolution | **UKIP / UCKP / Universal Source Assimilation Framework** | `engine/knowledge/ukip/` · `engine/uckp/` · `platform/universal_assimilation/` | `USAF-001` · `UAKOS-CLOSURE-008` · `UKAP-001` | Knowledge Once Principle |
| 8 | Universal Memory Evolution | **Universal Persistent Evolutionary Graph Memory** (ULP Part 05) | `engine/lineage/memory.py` | `ULP-MEMORY-LAYERS-001` (`adr/0013`) · `UCI-001` XVI.5 | **"NONE — DERIVED TRUTH… CREATES NO MEMORY STORE"** |
| 9 | Universal Requirement Evolution | **Repository Requirement projection** (`RR-<CONCEPT-ID>`) | `00-MASTER/UAKOS-CLOSURE-009/requirement_engine.py` · `engine/uckp/evolution.py` | `UAKOS-CLOSURE-009` · Article 14 · `UCOS-URR-001` **NOT ADMITTED** | Derived; identity is a function of concept identity |
| 10 | Universal Execution Governance | **Execution Environment Governance** + **Runtime Execution Platform** | `engine/execution_environment/` · `engine/runtime/execution/` | `UEG-000001` · `EPIC-RTE-002` | `EXECUTION_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"` |
| 11 | Universal Lifecycle Governance | **Universal Constitutional Lifecycle** | `engine/nucleus/lifecycle.py` · `engine/uckp/evolution.py` | `CMG-000001` → `UCIC-001` → `UCL-000001` → `CEP-009` | `UCL-000001` = **"NONE — DERIVED TRUTH; legislates no lifecycle"** |
| 12 | Universal Verification Governance | **Universal Verification Intelligence** | `engine/verification_intelligence/` · `engine/verification_impact/` · `verify.sh` | `UVI-000001` · `adr/0020` (purity restoration) | `verify.sh` = "Canonical Verification Entry Point"; **"MODES ARE NOT DECLARED HERE"** |
| 13 | Universal Artifact Governance | **Generated Artifact Registry** + **Universal Object Governance** | `platform/repository_intelligence/generated_artifacts.py` · `00-MASTER/UCOS-UGA-001/uga_engine.py` · `00-BOOK/tools/ukb.py` | `UCOS-GENERATED-ARTIFACT-REGISTRY-001` · `UCOS-UGA-001` · `REG-AUTO-001` | **"AUTHORED REPOSITORY TRUTH… upstream of every engine it describes and must never be produced by one of them"** |
| 14 | Universal Mutation Governance | **Mutation Governance Boundary** | `platform/repository_intelligence/mutation_classification.py` · `engine/foundation/guards/frozen_paths.py` · `platform/identity/policy.py` | `00-BOOK/DATA/mutation-governance-boundary.json` · `adr/0027` · `adr/0023/0024/0025` | **"declares the boundary; it does not create a new authority and governs nothing itself"** |
| — | *Universal Assumption Detection* (prior cycle; retained) | **Closed-enumeration disclosure** — *same owner as #1* | `engine/infinite_scope/contract.py` | `UISD-000001` · `adr/0007` | Same as #1 |

## 3.2 Independent corroboration from the repository's own reuse matrix

`OMEGA-E06-STAGE-1-UNIVERSAL-CONSTITUTIONAL-REPOSITORY-DETERMINATION.md` §27 reaches the same conclusion for the overlapping concepts — **18 REUSE, 0 CREATE**:

> "Every constitutional concept in the mission's list has a canonical owner already in Repository Truth."

Rows bearing directly on this determination: `R-01` Universal Lifecycle → `00-MASTER/UCL-000001/` · `R-02` Universal Identity → `engine/uckp/identity.py` · `R-03` Universal Registry → `engine/registry/universal/` · `R-06` Universal Assimilation → `platform/universal_assimilation/` · `R-10` Universal Governance → `engine/governance/` (≈60 gates) · `R-11` Universal Evolution → `engine/uckp/evolution.py` · `R-13` Universal Graphs → `engine/graph/` · `R-14` Universal Taxonomies → `engine/context/taxonomy.py` · `R-16` Universal Knowledge → `engine/knowledge/` · `R-17` Universal Determinism → `engine/determinism/`.

Two further instruments independently reached "already exists, do not create":

- `UNIVERSAL-LIFECYCLE-INHERITANCE-RECONCILIATION-DETERMINATION.md` §1: *"Workstream 1 must not create the five artifacts it proposes. All five already exist under different names, and creating them would install five duplicate authorities in a repository whose gates are specifically built to refuse that."*
- `CMG-000012-IDENTITY-AND-OWNERSHIP-DETERMINATION.md` §1: *"The Universal Context Model already exists as executable law… `CMG-000012` therefore must not define a Universal Context Model."*

**Assimilation finding.** The "locate, do not create" disposition is not this determination's editorial preference. It is the **third independent arrival at the same conclusion**, and it is enforced: `--check-no-parallel-authority` in `ucl-gate.yml:105` makes a rival authority a gate violation.

## 3.3 Enforcement coverage

| # | Dimension | Dedicated CI gate | `verify.sh` stage | Tests | Live verdict (§9.2) |
|---|---|---|---|---|---|
| 1 | Infinite Expansion | ✅ `uisd-gate.yml` | ✅ `:539` | ✅ 117 | ✅ **OPEN, exit 0** |
| 2 | Agnostic Architecture | ⚠️ provider plane only (`uprf-gate.yml`) | — | ✅ per-layer | not gated as a principle |
| 3 | Entity Model | ❌ no `uobc-gate.yml` | ✅ `:502`, `:435` | ✅ | ✅ **exit 0** |
| 4 | Relationship Evolution | ❌ open gap `ISD-G-04` | — | ✅ 119 | — |
| 5 | Context Evolution | ❌ | — | ✅ 13 files | — |
| 6 | Capability Evolution | ✅ `uaue`, `uaep`, `ufc` | — | ✅ 5 suites | ✅ **exit 0** |
| 7 | Knowledge Evolution | ✅ `assimilation`, `corpus-currency` | ✅ | ✅ | ✅ **CLOSED, gaps=0** (qualified) |
| 8 | Memory Evolution | ❌ | — | ✅ structural | — |
| 9 | Requirement Evolution | ✅ `closure009-gate.yml` (`RR-*` only) | — | ✅ | ⛔ **INCOMPLETE 25.5%** |
| 10 | Execution Governance | ✅ `determinism.yml` + 27 gates | ✅ Stage 0 `ucos_env_gate` | ✅ | ✅ **exit 0**, 1 advisory |
| 11 | Lifecycle Governance | ✅ `ucl-gate.yml` | ✅ | ✅ | — |
| 12 | Verification Governance | ✅ `ec1-ci.yml` + purity steps in `uisd-gate.yml` | ✅ (is the entrypoint) | ✅ purity suite | — |
| 13 | Artifact Governance | ✅ ~9 per-owner replay/drift gates + `ucos-registration-gate.yml` | ✅ Stage 6b UGA | ✅ | — |
| 14 | Mutation Governance | ✅ frozen guard `ec1-ci.yml:40,147` | ✅ Stages 4/5 | ✅ | ⛔ **R-09 coverage finding** |

**10 of 14 gate- or `verify.sh`-enforced. 4 test-enforced only** — Agnostic Architecture *as a principle*, Relationship Evolution, Context Evolution, Memory Evolution.

---

# PART IV — PRINCIPLE ALIGNMENT

Per dimension: mechanism (understanding, not just location), and the precise residual gap.

## 4.1 Universal Infinite Expansion — EXISTING

`engine/infinite_scope/` (~1,590 LOC). `contract.py:796` `LAW_CHECKS` binds **11 laws to 11 checks bijectively** — `validate` "refuses to construct a contract whose law names a missing check, or whose check no law claims." The core inversion: **`ISD-L-01` is not "no enumeration is closed" but "no enumeration is closed *silently*"** — every closure must disclose a `closing_invariant`, an `admission` path, and intent-or-gap-id. Two detection mechanisms: a **ratchet scan** (`FreezeScan`/`PreservedSite`, `ISD-L-07`) over declared roots, where class A — "an active declaration forbidding future change with no channel named" — is inadmissible; and a **live admission exercise** (`check_admission_path_exercisability:733`) that actually admits a synthetic member into a declared-open population in memory and re-evaluates every declared consumer, with a **two-way ratchet** `_reconcile:770`: an undeclared refusal fails, *and* a stale declared refusal that no longer occurs also fails. Self-application is mandatory: `ISD-L-03` requires the principle to hold a birth record and declare no independent lifecycle — which binds dimension 1 to dimensions 3 and 11.

**Gap.** Detection is **declaration-bound, not discovery-bound** (`AD-G-01`). `ISD-G-01` records one closure disclosed as unintentional. `INFINITE-EXPANSION-COMPLIANCE-DETERMINATION.md` §1 lists 8 open architectural violations. `FreezeScan` roots are declared, so files outside them are unscanned.

## 4.2 Universal Agnostic Architecture — PARTIAL

Real and tested per plane. **Storage:** `engine/uckp/persistence.py:101` `PersistenceAdapter` — two abstract members, `locator` marked "Advisory: never an identity", `capabilities()` "never consulted by the law"; ten adapters including `FutureStoragePersistence:574` as the literal open extension point. **Provider/vendor:** `platform/universal_provider/framework.py` runs `discover → admit → instantiate → validate → certify → activate` and "contains no provider-specific code"; `engine/provider/metatypes.py` makes a provider *category* a registered kernel meta-type — "Adding a facet, a category, or a provider is therefore a registration, never a framework change." **Technology:** per-layer neutrality invariants `UDL-11` / `DMI-06` / `SMI-06` / `AMI-06`; `engine/uckp/law.py:360` — the law text itself is "technology-, repository-, storage-, runtime- and implementation-agnostic."

**Gap — self-disclosed by its own ADR.** `adr/0021`: status "**DESIGN PRINCIPLE — not a certification**"; and under negative consequences, *"no gate, invariant, or certification currently checks conformance to this statement, and none is created by this document."* It also refuses to blanket-certify: *"No single, blanket 'the architecture is agnostic' claim was, or could honestly be, established."* API/Communication and UI/Experience have **no implementation surface** to evaluate. `PersistenceAdapter` is not shared with `KnowledgeStore`/UKDA (REQ-43 is discovery-only).

## 4.3 Universal Entity Model — EXISTING

`engine/uckp/ucko.py` — the docstring is the intent verbatim: *"The UCKO is the only thing in UCOS Ω∞ that holds authority. Everything else… is a view of one."* All **33 facets as typed immutable fields, one per facet**, making `facet_value` total — "facet completeness is a structural property, not a convention." Content-addressed (`content_sha256`), semantically addressed (`semantic_digest` hashes meaning alone), self-proving (`verify_replay`). `engine/uckp/identity.py` is the **single mint** (role SUPREME); `engine/object_birth/` advances no counter and consumes no serial, so under identity.py's own `second_authority_test` it cannot be a second mint. Birth is "an identity birth event: an object is identified *before* it exists" — 7 stages, 9 mandatory fields, `identity_exists` flipping exactly once, **all as data**, so "admitting a future stage or namespace is an edit to data rather than to control flow." Kind classification is **total by construction**: ordered first-match-wins plus a catch-all `BSP-L-02` requires to exist and be last.

**Gap.** The 33-facet set is **closed by design**, so a new *facet* is a constitutional amendment even though a new *entity kind* is data. Four kinds are `birth_required=true` under `DISCLOSED_ADOPTION`, reporting `EXCEPTION` not `PASS`, because gap `G11` forbids corpus-wide backfill. Two parallel kind vocabularies (`birth-scope-policy.json` vs `engine/uaue` `ObjectKind`) with no reconciling registry. **No `uobc-gate.yml`** — `verify.sh` only.

## 4.4 Universal Relationship Evolution — EXISTING

Four coherent, non-duplicative planes. `engine/ceu/existence.py:918` `RelationshipView` — *"A relationship type is a unit; a relationship is a unit; a topology is a unit… not a second registry."* `relate():951` registers an `ExistenceUnit(form="relationship", …)` under **registry-driven** constraints (`ATTR_SOURCE_FORMS`, `ATTR_ACYCLIC`, `ATTR_SYMMETRIC`, `ATTR_TOPOLOGIES`) where "a constraint applies only if declared". Acyclicity enforced post-assert via `cycle_in()`; symmetric types auto-mirror non-recursively. `engine/knowledge/ukip/relationships.py` adds the temporal algebra: `Relationship.validity`, `identity()` (triple + validity marker) vs `key()` (navigational group), `SEMANTIC_INVERSES`, `COMPOSITION_RULES` with a cited derivation `path`, `ACYCLIC_FAMILIES`, and `RelationshipSet.valid_at()` point-in-time reconstruction — over `engine/temporal/operations.compare()`, which **fails closed on `Ordering.INCOMPARABLE`**: unproven overlap is coexistence, never a guessed collapse.

**Gap.** Temporal validity exists in **one of four planes only** — `RelationshipView.relate()` and `graph.Edge` carry no `ValidityPeriod` (versioned by supersede/resurrect instead). `RelationDeclaration.from_dict()` fail-closed refuses non-null `validity` because `TemporalCoordinate.from_dict` does not exist (documented deferral). **No relationships gate** — `ISD-G-04`, explicitly *"enforcement machinery over a 12,899-edge surface owned by UKB… NOT closed by this cycle."* The four planes are reconciled in prose, with no cross-plane conformance test.

## 4.5 Universal Context Evolution — EXISTING

`engine/context/` — 18 modules, the most complete dedicated package of the fourteen. `resolution.py`: `candidates():112` ordered by namespace specificity → `_merge():122` resolving by (authority, specificity) → **`ContextAmbiguityError` when equally authoritative contexts disagree**; `resolve():149` fails closed on no applicable context, undeclared ontological shape, or missing required dimension. `model.py`: `ContextValue.outranks():109`, `ContextRelationEdge:306` (context-to-context edges), `ResolvedContext.provenance_of():405` — **every resolved dimension keeps its source**. `runtime.py` is the execution-context propagation stack (`bind`/`activate`/`current`/`require`/`provenance`/`frames`/`snapshot`/`restore`/`trace`). `taxonomy.py`: `extend()` is bounded open-world — a future taxon must name an existing parent. Substrate binding `engine/ceu/existence.py:653` `bind_context` requires `frame` + `resolution_digest`, is journaled, and **refuses rebase** — "a registry is bound to one reality."

**Gap.** Inheritance/propagation is **derived** (namespace-prefix specificity, taxon parent chain, runtime frame stack) rather than an explicit inherit-from-parent operation. Ad-hoc context types bypass the universal model: `platform/blueprints/context.py`, `platform/projects/context.py`, `platform/workspace/context.py`, `platform/artifact_explorer/context.py`, `StageContext`, plus `class Context` in `engine/constitution/{gateway,stages}.py`. `MCP-001` master context has no code binding to `ContextRegistry`. **`ContextRegistry` is not persisted** (`P4-F-009`). No dedicated CI gate.

## 4.6 Universal Capability Evolution — PARTIAL

Every constituent exists. `engine/uaue/controller.py`: `discover()`, fail-closed `admit():757`, and `_LOOP:707` — an **11-position table** "rather than eleven inline calls, so the traversal is one loop with no branch in it". `engine/uckp/evolution.py`: append-only `EvolutionLedger:238` where `append()` admits only the next stage — *"skipping is exactly how an unproven claim acquires a certificate"* — with `next_stage()` wrapping and `is_terminated()` always False, so non-termination is **encoded, not promised**. `engine/registry/universal/registries.py`: `TypedRegistry.register(version=…)` + `history():100`. `engine/knowledge/capability.py:388` `assimilate_capabilities()` elevates knowledge → capability with created/updated/unchanged/retired deltas, digest-compared so re-run is a no-op. `engine/nucleus/model.py:300` makes `owner` mandatory — "no orphan capabilities is enforced by the type rather than measured after the fact". `realization/` is the generated realization of the CAPABILITY universe from **131 canonical `UCKO-CAP-*` objects**, sealed to `knowledge_seal 71c65cf5…`.

**Gap — the parts exist; the pipeline does not.** No code path calls `EvolutionController.admit/run` for a `CapabilityRegistry` registration, and no loop position writes a lifecycle transition back onto a `CapabilityRecord`. `CapabilityRegistry` has versioning + `history()` but **no lifecycle field and no admission check** beyond `required_attributes={"summary"}`. Lifecycle is band-local and duplicated across `application/capability_meta.py`, `service/capability.py`, `infrastructure/capability.py`, `platform/foundation/capabilities.py`, `platform/universal_control_plane/registry.py`, `engine/nucleus`, `engine/uicm`. `AEOS-001` conditions AC-1…AC-6 undischarged; `CAPABILITY-COVERAGE-CLOSURE-DETERMINATION.md` D-3.5 measures capability certification coverage of implementation at **0%**.

## 4.7 Universal Knowledge Evolution — EXISTING

Four named owners: `UKIP` (`engine/knowledge/ukip/`), `UCKP` (`engine/uckp/`), `USAF-001` (`platform/universal_assimilation/` — `AssimilationPipeline:112`, *"the single framework through which every source, present or future, is assimilated"*), and the executable closure engine `00-MASTER/UAKOS-CLOSURE-008/assimilation_engine.py`. Concept homing is implemented as **`created_home`** (`ukip/registry.py:91`, `uckp/registry.py:67`, `platform/universal_truth/policy.py:228` `is_canonical_home()`). Knowledge confidence (`ukip/confidence.py`, `adr/0016`) deliberately **adds no field to the CKO** — it projects into the pre-existing `UCXI-000001` `KNOWLEDGE` context kind whose required dimensions are `source`/`provenance`/`confidence`, binds to `(knowledge_id, version)`, and corrects by explicit `resupersede_confidence()` rather than overwrite. Corpus and version history are **separate registries** (`canonical-knowledge.json` vs `canonical-knowledge-history.json`).

**Gap.** The `conversation_only` gap class is measurable only from an external corpus at `REPO.parent/"UCOS"`; absent it, that class *"measures 0 by ABSENCE rather than by closure"* (`closure_engine.py:19-33`) — **so the live `gaps=0` is qualified, not unconditional.** UKIP provenance chains are hash-chained in memory but **not persisted** (`P4-F-006`). `ContextRegistry`, which holds confidence, is not persisted.

## 4.8 Universal Memory Evolution — PARTIAL BY DESIGN

`engine/lineage/memory.py` (556 LOC) is the closest thing to Universal Memory: *"ULP Part 05 — universal persistent evolutionary graph memory, resolved by projection"*, answering "what does the repository remember about this?" over the declared order `identity → context → relationship → knowledge → evidence → decision → evolution`. Its own docstring is emphatic: **"This module is not a memory engine and must never become one. It creates no store, opens no counter, mints no identifier, declares no relation and writes no file."** The seven layers are **data** (`memory-layers.json`, `ULP-MEMORY-LAYERS-001`), each naming owner and record, so an eighth layer is admitted without code change. Access modes are closed and an undeclared mode is refused, so *"an unreadable layer can never masquerade as an empty one."* Open-world: unknown subject → `recorded=False`, distinguishing "owner records nothing" from "record absent". **No clock** — wall-clock strings are carried verbatim, never parsed.

Three-way split, per the tri-partition (§1.2): (a) **governance/knowledge persistence** — real and durable (`GitPersistence:225` content-addressed append-only `journal.jsonl` with parent chaining, "the journal is never rewritten, so a prior recorded universe stays recoverable"; `id-ledger.json` sticky UIDs, monotonic cursor; 36 `CKPT-*.md`). (b) **runtime execution state** — structures exist (`Checkpoint` with deterministic `UCOS-EXEC-CKPT-<sha256[:16]>` id, `-1` reset sentinel, `state_map()`) **but `engine/runtime/execution/persistence.py` only serialises to a string — no file write, no path, no store.** (c) **a general-purpose memory subsystem** — constitutionally forbidden from being a store.

**Gap — mostly self-disclosed in `memory-layers.json` `$disclosures`.** `P4-F-009` no per-subject context binding persisted · `P4-F-006` provenance chains not persisted · `P4-F-002` no temporal validity/version/supersession pointer in the memory plane · `P4-F-008` learning deliberately not a layer, because "a separate layer would imply a learning store that no owner holds." Plus: **runtime `Checkpoint`/`Snapshot` have no durable sink.**

## 4.9 Universal Requirement Evolution — PARTIAL

Two deliberately non-merged planes. **Plane 1, executable and gated:** `requirement_engine.py` projects every constitutionally accepted concept into a governed Repository Requirement and **measures — never estimates** — coverage, maturity, readiness, traceability, gap. Requirement identity is *"a total, injective, derived function of the existing concept identity (`RR-<CONCEPT-ID>`), so no independent requirement identity can ever drift from its concept."* Zone→program classification is read from `00-BOOK/tools/config.py`; unknown zones/families/dimensions are carried generically. **Plane 2, manual and ungated:** the two Ω∞ `REQ-NN` matrices — real traceability matrices, both declaring "Discovery and reconciliation only", with **zero references** from `.github/`, `Makefile`, `verify.sh` or `scripts/`. **Evolution semantics are implemented:** `requirement_evolution_event_vocabulary():163`, `evolution_subject_type_vocabulary():138`, append-only ledger, tested for CREATED/MODIFIED/REFINED/MERGED/SUPERSEDED and ledger querying by subject and event type.

**Gap.** *"49 `REQ-NN` rows in hand-maintained markdown, and 549 `RR-<concept_id>` records in engine-generated JSON. **Nothing in the repository states whether these are the same population.**"* The reconciliation determination holds they are **"not duplicates — different object classes measuring different subjects"** (different derivation, scope, identifier grammar, and incompatible status models: one axis vs seven) that *"can and should coexist as distinct lifecycle objects, joined by a declared relation rather than merged"* — **and that relation has not been declared.** The requested engine *"was already designed, and deliberately refused"*, because a second register over an already-registered population is the competing measurement `UFC-16` forbids; `UCOS-URR-001` stands `PROPOSED — NOT ADMITTED`. `UNIVERSAL-REQUIREMENT-EVOLUTION-CLOSURE-DETERMINATION.md` §1: *"no automatic discovery, no duplicate detection, no conflict resolution, no evolution tracking."* Admission was executed **by hand** for REQ-NEW-01..10. Internal gaps: `ARTIFACT-TRACEABILITY-SCHEMA-UNPOPULATED` (:662), `LIFECYCLE-DIMENSIONS-NOT-OPERATIONAL` (:681).

## 4.10 Universal Execution Governance — EXISTING (two owners) + DOCUMENTATION ONLY (a third)

**Owner 1 — admission control, `UEG-000001`.** `engine/execution_environment/`: eight declared checks, **seven blocking, fail-closed** (EEG-01 repository, EEG-02 venv, EEG-03 interpreter, EEG-04 pytest provenance, EEG-05 plugins, EEG-06 dependency state). `verify.sh:85-124` replaced `ucos_ensure_venv` with `ucos_env_gate`, so **verify.sh may no longer create, install, or reach the network.** The certification records a *live executed* regression: under Homebrew CPython 3.14.4, six refusals and `exit 1`.

**Owner 2 — runtime, `EPIC-RTE-002`.** `engine/runtime/execution/`, 23 modules ≈2,900 LOC. `authorization.py:41-119` refuses unless the composition carries a well-formed EC-1 provisional-state disclosure; `EXECUTION_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"` — authorisation "confers engineering-execution authority only and never constitutional authority or finality (ORL-22)". `auditing.py`: `AuditLog` is frozen and forward-only — `append()` returns a **new** log with monotonically increasing `sequence`, so "an audit trail can never be silently mutated (ORL-07)". `scheduler.py` reuses `composition.plan.steps` and `graph.dependencies_of` **verbatim** — re-derives no ordering. `replay.py:49` reconstructs `requested_outcomes(run)` and re-runs `coordinate()` verbatim, with byte-for-byte fidelity checked by `replay_validation.py`.

**Owner 3 — the UIEC controller / queue / Quality Gate Engine: DOCUMENTATION ONLY.** `09-EXECUTION-GOVERNANCE.md` is headed **"Mode: DESIGN ONLY"** and specifies the C12 governance ledger, the READY predicate vector P1–P7, and a separation-of-authorities table in which the human operator *"cannot select which object executes"*. **No `UIEC`, `ExecutionController` or `QualityGateEngine` class exists** in `engine/` or `platform/`.

**Gap.** No runnable controller selects work from `closure.json` and cuts batches. `engine/runtime/execution/` governs a **modelled** execution — every module states "it records; it executes nothing" (ORL-15) — and dispatches no real work. Because that plane's `persistence.py` serialises only, **the audit trail and checkpoints are never written to a durable store**, so cross-process replay of a real run has no on-disk input.

## 4.11 Universal Lifecycle Governance — EXISTING

`engine/nucleus/lifecycle.py` is the executor, and it is explicitly subject-agnostic: *"Nothing here knows what a nucleus is. The lifecycle applies to nuclei, layers, compositions, capabilities, artifacts, knowledge, registries, policies, evidence, executions, contexts, universes, civilisations and realities alike, because the subject is an opaque identifier and the work is the caller's function."* 45 stages held as **data** (`STAGE_DECLARATIONS:119` → `_chain():96` → `STAGES:168`); `verify_manifest_alignment():204` fails closed on declaration/code divergence — "no second drifting stage list"; `stage_order():179` derives order via `derive_order`, never hardcoded; `LifecycleExecution:295`/`execute():389` run stages over any subject via a caller-supplied function, hash-chained by `_entry_hash():374`, with `replay():460` measuring fixed-point-ness.

Four instruments with **disjoint subjects**, not competing lifecycles: `CMG-000001` (law owner) → `UCIC-001` (capability lifecycle, 15 stages, "no capability may bypass this contract or skip a gate") → `UCL-000001` (constitutional stage graph, 45 stages, `AUTHORITY: NONE — DERIVED TRUTH`) → Article 14 (perpetual evolution, structurally non-terminal) → `CEP-009` (amendment). Lifecycle inheritance is implemented **by reference**, not by duplication: `data/lifecycle_meta.py:49` sets `LifecycleState = DatumState` — "Identical forward-only state machine… so it is reused by reference (no parallel lifecycle model)." `OMEGA-E06` §3 determines: *"One Universal Lifecycle for every object? **YES** · Special-case lifecycles exist? **NO** — 6 owners, one lifecycle, merge forbidden."* Self-application is gated: `ISD-L-04`/`ISD-L-05`.

**Gap — coverage and reference integrity, not architecture.** (a) `UNIVERSAL-ARTIFACT-LIFECYCLE-DETERMINATION.md` (dated 2026-08-22, the most recent instrument): **145 determination documents exist in a governance void — no identity, no ownership, no lifecycle stage, no disposition.** (b) `CMG-000008/9/10` assert inheritance from "Universal Recursive Constitutional Lifecycle Governance v1.0", **which does not exist** — 21 self-certifying, unmeasured claims, because nothing parses their `LIFECYCLE METADATA` block; the determination's own words: *"the certification cannot be false — which makes it worthless as evidence."* (c) State vocabularies differ per plane with no crosswalk beyond `00-MASTER/UCL-000001/04-LIFECYCLE-AUTHORITY-CROSSWALK-REGISTER.md`. (d) `B-02` gap **B-4**, stage `UCL-S-0320`. (e) `LIFECYCLE-DIMENSIONS-NOT-OPERATIONAL`.

## 4.12 Universal Verification Governance — EXISTING

**Verification selection is executable.** `engine/verification_intelligence/selection.py::select():117` computes the test set from a change set across five substrates — identity and dependency **delegated** to `engine.verification_impact` (not reimplemented), then ownership, capability (`_capability_location()` + `_test_mirror()`), and relationship (`_provenance()` deriving `artifact → producers` from registry `produces` edges). `engine/verification_impact/changes.py` resolves a diff base through an ordered fail-closed chain and **raises rather than returning `()`**, so "no base" can never read as "no changes". **Fail-wide is enforced, not documented:** `SELF_PREFIXES:56` escalates any change to the selector itself — *"a change to the verification selector cannot be bounded by the selector itself"*; an owner absent from the capability catalogue escalates; a bounded change reaching no test escalates, "widening rather than skipping"; unregistered test objects are unconditionally selected. If planning faults, `PYTEST_ARGV=(-m pytest)` — the whole suite under the `--cov-fail-under=90` floor.

**Gate purity is enforced three independent ways.** (i) *Behaviourally, by test:* `platform/tests/test_verification_purity.py` — `_snapshot()` digests git status plus `id-ledger.json`, `change-ledger.json`, `artifacts.json`; `test_verification_stage_commands_are_observationally_pure:89` runs each `OBSERVING_STAGES` command and asserts byte-identity; `test_no_verification_path_invokes_the_minting_flag:121` permits `--mint` in exactly one invocation. Its docstring records the original defect: `register.sh --guard` from `./verify.sh --full` *"minted 140 permanent identities… taking `artifacts.json` from 1,233 to 1,373 entries. A verification command performed a migration."* (ii) *In CI, per gate:* `uisd-gate.yml` snapshots `git status --porcelain` before and after two runs and diffs both tree and reports — `"::error::UISD-000001 mutated the working tree — it is declared OBSERVE MODE"` — plus a no-wall-clock regex, because a timestamp would destroy the determinism measurement. (iii) *By declared write scope:* `forbidden_write_prefixes` (§4.14).

**`verify.sh` stability is a three-reader contract, verified.** `uisd-gate.yml:264` reads only the always-run portion; **`:266`** `labels = re.findall(r'^\s*run_stage "([^"]+)"', default, re.M)` re-derives every stage label **from source**; `:274-278` asserts exact ordered list equality against `00-MASTER/UAKOS-CLOSURE-008/validation-record.json`; **`:279-280`** computes `sha256("\n".join(labels))` and errors if `record["contract"]["stages_digest"]` differs. `verify.sh` says so itself: *"those literals are a three-reader contract: this script executes them, `validation-record.json` digests them, and `uisd-gate.yml` re-derives them."* A fourth reader — `platform/tests/test_canonical_validation_evidence.py` — derives the same digest. **Consequence to respect: any edit to a `run_stage` label breaks CI.**

**Gap.** No `gate_mode` field exists anywhere in code or JSON (grep-confirmed absent), so PRODUCER-vs-OBSERVE is **per-gate prose rather than a declared, validated field**. `stages_reading():372` computes stage-level impact but is explicitly "a QUERY, not a scheduler" — not wired into scheduling. Purity is **asymmetric**: it is measured against version control, not the filesystem — Stage 1b deliberately writes gitignored paths, and the purity suite excludes both it and the pytest stage from `OBSERVING_STAGES`.

## 4.13 Universal Artifact Governance — PARTIAL

Two distinct classification vocabularies exist, and conflating them is the trap. **Object class** (`uga_engine.py`, returned at :205/:215, mapped to id prefixes at :249-254): `TEST_OBJECT`, `EXECUTABLE_OBJECT`, `EXCLUDED_DOCUMENT`, with `DOCUMENT_ARTIFACT`/`DATA_OBJECT`/`TOOLING_OBJECT`/`CONFIGURATION_OBJECT` in the ledger. **Input classification** (`generated_artifacts.py:56-91`): `TRACKED_DETERMINISTIC`, `ENVIRONMENTAL`, `OPERATIONAL`, `EXTERNAL`, `UNKNOWN` (fails closed), `EXECUTION_TRANSCRIPT`, `LOCAL_RUNTIME`, `ENVIRONMENTAL_OBSERVATION`, `GENERATED_DETERMINISTIC` — plus `IDENTITY_ROLES = {CANONICAL} | {EXCLUDED, NON_CANONICAL}`.

**"Derived artifacts are never authoritative" is executable, not aspirational.** `validate():240` refuses a `CANONICAL` artifact declaring an `ENVIRONMENTAL`/`EXECUTION_TRANSCRIPT`/`LOCAL_RUNTIME`/`ENVIRONMENTAL_OBSERVATION` input; the escape is to declare it `NON_CANONICAL`, *"because it is then **evidence rather than identity**. Evidence is kept. What it may not do is claim to be repository truth."* **This is the constitutional basis for the directive's own "existing artifacts are knowledge" rule.** Provenance for generated code is a double seal: `realization/UCOS-URI-MANIFEST.json` carries a top-level `content_sha256` plus, per artifact, its own `content_sha256` **and** a `knowledge_seal` binding the *source knowledge* — so bytes and meaning are independently sealed, and `authority: NONE (derived from canonical knowledge)` denies authoritativeness. The register declares itself **upstream**: *"It is deliberately UPSTREAM of every engine it describes… That direction is what keeps the dependency acyclic."*

**Gap — the model is universal; the drift enforcement is not.** Drift gates exist and byte-compare, but **per owner**: `assimilation-gate.yml:33,50`, `closure009-gate.yml:42,61`, `roadmap-gate.yml:48,64,68`, `uaep-gate.yml:103`, `uaie-gate.yml:123`, `uar-gate.yml:88`, `acee-gate.yml:143`, `corpus-currency-gate.yml:61`, `baseline-gate.yml:19`, plus `verify.sh` Stage 6d (`--replay`, byte comparison: *"a projection that only matches after normalisation is a projection whose canonical form nobody is holding to"*). **No single universal gate regenerates all 345 entries and byte-compares.** The universal leg (`UGA-INV-04/05/06/08`) proves *a producer exists and is invocable from the bootstrap path* — not regenerated equality. Also `00-BOOK/tools/config.py::EXCLUDE_DIR_PREFIXES` remains a **second expression** of "this path is generated" alongside the register — the very three-way drift the register's `why_this_exists` says it exists to collapse.

## 4.14 Universal Mutation Governance — EXISTING

**The rules are data.** `mutation_classification.py` docstring: *"**THE RULES ARE DATA, NOT CODE.** This module contains no rule text, no class name ordering and no predicate the register does not declare."* Nine classes and nine rules (R-01…R-09, precedence 1…9) are declared in `00-BOOK/DATA/mutation-governance-boundary.json`, each naming exactly one governing chain (e.g. `SOURCE` → `pre-commit → verify.sh → UCOS-RIB-001 → UCOS-AEE-001 → Phase 8 → Phase 9`). **No Python `MutationClass` enum exists** — grep-confirmed; the class is a string read from data, which is *stronger* than the stale documents that still describe a "fixed count". `validate_rule_coverage():415` refuses **in both directions**: a declared rule with no predicate, *and* a predicate no rule declares — "dead code wearing the appearance of enforcement". `classify():427` walks declared precedence and returns `UNRESOLVED` at the declared terminal: *"UNRESOLVED IS NOT A CLASS… it confers no authority, and it must never be read as a permissive default. Consumers that gate on classification MUST treat it as failure."*

**Write authorization is executable, in two layers.** `engine/foundation/guards/frozen_paths.py`: `FROZEN_PREFIXES = ("00-BOOK/", "00-SOURCE/", "99-FREEZE/")`, `assert_no_frozen_write()` raising `SecurityViolation`, exposed as the `ec1-frozen-guard` CLI and wired into `ec1-ci.yml:40,147`. `platform/identity/policy.py`: four hard invariants evaluated first in fixed order — `_guard_frozen_corpus_write`, `_guard_certification_append_only`, `_guard_read_only_role_mutation`, `_guard_tenant_scope_isolation` — then **default-deny** (`return _deny(request, "no-grant")`), as a pure function with no wall clock.

**Supersession-not-overwrite is stated as the forward channel, in both guards:** *"The forward channel is supersession — a new object carrying new identity and a lineage edge to what it supersedes (CEP-007 XIII), or amendment of the governing instrument (CEP-009)… Identity is immutable, history is append-only, and evolution is unlimited through those channels; only in-place modification of a certified artifact is refused."* Implemented as `adr/0023` (CEU), `adr/0024` (UCDA), `adr/0025` (KnowledgeStore), and `ukb.py:314-417` append-only content-hash history preserving every prior hash.

**Gap — verified live, not inferred.** `RULE_PREDICATES` implements **R-01…R-08 only**; `mutation_class_extension.py` builds the R-09 `GOVERNED_ANALYSIS` class and rule dicts and an `extend_*` function that appends them to the boundary **document**, but registers **no predicate**. Live execution of `validate_rule_coverage()` against the committed register returns:

```
("rule 'R-09' is declared but no predicate implements it",)
```

Because coverage validation is two-sided and fail-closed, this is a genuine finding, not cosmetic (§11 O-14). Additionally: **no CI step runs `classify_all` over a commit's changed paths and fails on `UNRESOLVED`** — the classifier is available to consumers rather than universally applied. And `forbidden_write_prefixes` is absent from **3 of 11** declarations, with enforcement being each programme's own code, so a programme omitting both the field and the check is unenforced.


---

# PART V — RELATIONSHIP COVERAGE

## 5.1 The dimensions are not fourteen independent things

`UISD-000001` already declares eleven expansion axes — `ISD-AX-01…11` — naming *scope, direction, relationship, evolution, lifecycle, capability, technology, temporal, self, lifecycle-vocabulary, population*. **Seven of the fourteen dimensions are therefore already axes of one existing declaration**, which is why extending detection is documented as "declaration entries plus checks in `LAW_CHECKS`", not a new module.

```
                       CMG-000001  — law owner: what counts as constitutional
                                │
        ┌───────────────────────┼──────────────────────────┬─────────────────────┐
        ▼                       ▼                          ▼                     ▼
  UISD-000001              UCIC-001                   CEP-009            UCKP-LAW-0001
engine/infinite_scope/  capability lifecycle    amendment authority     engine/uckp/law.py
  = D1 + assumption        (15 stages)                  │              constitutional superior
     detection                  │                       ▼                of #13 and #14
        │                       │              UCKP Article 14                  │
  ISD-L-02 ─ relationship type space stays open  engine/uckp/evolution.py        ├─► generated-artifact
  ISD-L-03 ─ the principle holds a birth record ──► #3     = #6 + #9 events      │      registry  (#13)
  ISD-L-04 ─ the principle inherits its lifecycle ─► #11   is_terminated()=False └─► mutation-governance
  ISD-L-05 ─ the evolution cycle never terminates ─► #6/#9        │                     boundary  (#14)
  ISD-L-09 ─ technology is an evolutionary state ──► #2           ▼
  ISD-L-10 ─ the capability set declares non-final ► #6      UCL-000001  = #11
        │                                          45-node stage manifest (DERIVED TRUTH)
        │                                                        │
        │                                        verify_manifest_alignment() fails closed
        │                                                        ▼
        │                                        engine/nucleus/lifecycle.py
        │                                        subject-agnostic executor
        ▼
  ┌─────┴───────┬──────────────┬───────────────┬───────────────┬──────────────┐
  ▼             ▼              ▼               ▼               ▼              ▼
UOBC-000001  UCXI-000001    CEU-001        UKIP/UCKP      ULP Part 05     UVI-000001
  = #3          = #5          = #4            = #7           = #8           = #12
birth +      context      relationship    knowledge      memory as      verification
kinds        resolution   as a unit       + confidence   projection      selection
  │             │              │               │               │              │
  └─────────────┴──────────────┴───────────────┴───────────────┘              │
                          bind_context / created_home                          │
                          resolution_digest / (id, version)                    │
                                                                               ▼
                                                      UEG-000001 + EPIC-RTE-002  = #10
                                                      admission → authorization → audit → replay
```

## 5.2 Verified inter-dimension relationships

| Relationship | Direction | Mechanism | Verified at |
|---|---|---|---|
| Expansion **self-applies through** Entity Model | 1 → 3 | `ISD-L-03` requires the principle itself to hold a birth record | `contract.py:247` `check_principle_inherits_itself` |
| Expansion **self-applies through** Lifecycle | 1 → 11 | `ISD-L-04` lifecycle applies to itself; stage graph must not have drifted | `contract.py:280` |
| Expansion **constrains** Relationship type space | 1 → 4 | `ISD-L-02` — type constrained by pattern, **never by enum** | `contract.py:204,343` |
| Expansion **constrains** Capability openness | 1 → 6 | `ISD-L-10` — `contract.capability_final` must be False | `contract.py:518` |
| Expansion **constrains** Agnosticism | 1 → 2 | `ISD-L-09` — deps empty, no version ceiling, pins disclosed | `contract.py:473` |
| Assumption detection **is** Expansion | ≡ | Same owner, same declaration; a second detector is a gate violation | `ARCHITECTURAL-ASSUMPTION-DETECTION-DESIGN-ANALYSIS.md` |
| Entity Model **is bound to** Context | 3 → 5 | `bind_context(fingerprint)` requires `frame` + `resolution_digest`; **refuses rebase** | `ceu/existence.py:653` |
| Relationship **is a form of** Entity | 4 → 3 | A relationship *is* an `ExistenceUnit(form="relationship")` — not a second registry | `ceu/existence.py:951` |
| Knowledge confidence **is a** Context binding | 7 → 5 | Projects into the `KNOWLEDGE` context kind; binds `(knowledge_id, version)` | `ukip/confidence.py`, `adr/0016` |
| Capability **is realized from** Knowledge | 6 ← 7 | `assimilate_capabilities()`; `realization/` generated from 131 `UCKO-CAP-*` | `knowledge/capability.py:388` |
| Requirement **is derived from** Knowledge concept | 9 ← 7 | `RR-<CONCEPT-ID>` — total, injective, derived | `requirement_engine.py:18-20` |
| Memory **projects over** 1/3/4/5/7/9/11 | 8 → many | Seven declared layers, each naming its owner and record; **creates no store** | `lineage/memory-layers.json` |
| Verification **selects over** Capability + Relationship | 12 → 6, 4 | `_capability_location()`/`_test_mirror()`; `_provenance()` over `produces` edges | `selection.py:71-115` |
| Verification **self-escalates** | 12 → 12 | `SELF_PREFIXES` — the selector cannot bound a change to itself | `selection.py:56,185-189` |
| Artifact Governance **is superior to** every engine | 13 → all | The register is upstream; "must never be produced by one of them" | `generated-artifact-registry.json:4` |
| Mutation Governance **joins** Artifact Governance | 14 → 13 | `Repository.generated` → `generated_artifacts.canonical_paths()` | `mutation_classification.py:163-168` |
| Both #13 and #14 **are subordinate to** UCKP-LAW-0001 | → law | `constitutional_superior` blocks name `engine/uckp/law.py`, role PROJECTION/EXECUTION | both registers |
| Execution **is admitted by** Environment Governance | 10 → 10 | `verify.sh` Stage 0 is `ucos_env_gate`, not `ucos_ensure_venv` | `verify.sh:85-124` |

## 5.3 The six relationship properties, tested against evidence

The directive requires explicit verification of six properties. Each is answered from code, with the exact plane in which it does and does not hold.

| Property | Verdict | Evidence | Where it does **not** hold |
|---|---|---|---|
| **Entities are connected through relationships** | ✅ YES | `relate(type, source, target)` registers an `ExistenceUnit` keyed `type:source->target`; admissibility constrained by declared source/target forms and classifications; graph queries `neighbours`/`inbound`/`adjacency`/`reachable`/`participants(topology)`/`dangling` | — |
| **Relationships can evolve** | ✅ YES | Registry-wide `supersede`/`resurrect`/`successors_of`/`ancestry` with a hash-chained `AuditEntry` journal (`adr/0023` append-only history). UKIP plane adds derivation: `COMPOSITION_RULES` produce transitive relationships carrying a cited `path` | Evolution is by supersession, **not** by in-place mutation — by design (§4.14) |
| **Relationships have context** | ⚠️ PARTIAL | The registry holding relationships is context-bound: `bind_context` requires `frame` + `resolution_digest` and refuses rebase; `ContextRelationEdge:306` gives context-to-context edges | **No per-relationship context binding is persisted** — `P4-F-009`. Context applies at registry granularity, not edge granularity |
| **Relationships have validity** | ⚠️ PARTIAL | `Relationship.validity: ValidityPeriod \| None`; `RelationshipSet.valid_at(coordinate)` reconstructs a point in time; `_overlaps`/`_holds_at`; comparison **fails closed** on `INCOMPARABLE` so unproven overlap is coexistence, never a guessed collapse (`adr/0015`) | **Only in the UKIP plane.** CEU relationship units and `graph.Edge` carry no `ValidityPeriod`; `RelationDeclaration.from_dict()` refuses non-null `validity` pending `TemporalCoordinate.from_dict` — `P4-F-002` |
| **Relationships have evidence** | ✅ YES | Hash-chained `AuditEntry` journal per registry action; `to_document()`/`digest()` for sealed projection; derived relationships cite their derivation `path`; `00-MASTER/UCOS-UGA-001/04-RELATIONSHIP-GRAPH.json` as the measured surface | Provenance chains are hash-chained **in memory** and not persisted — `P4-F-006` |
| **Relationships support future unknown types** | ✅ YES — **proven, not asserted** | `engine/tests/expansion/test_universal_expansion_verification.py:74` `test_unknown_relationship_type_needs_no_code_change` admits `ExistenceUnit(form="relationship-type", key="entangles-with")` and asserts `engine.kernel.compliance.kernel_source_fingerprint()` is **byte-identical**. `ISD-L-02` independently forbids closing the type space by schema `enum`. Types are rows in `SEED_RELATIONSHIP_TYPES`, not code | — |

**Assimilation finding.** Four of six properties hold unconditionally. The two partials — context at edge granularity, and validity outside the UKIP plane — are **the same gap seen twice**: the temporal/context enrichment landed in the knowledge-closure plane and has not been propagated to the existence and graph planes. Both are already named gaps (`P4-F-002`, `P4-F-009`) with declared owners. **No new capability is required to close them; propagation is.**

## 5.4 Cross-cutting proof that growth requires no code change

`engine/tests/expansion/test_universal_expansion_verification.py` (12 tests, `WP-UCDA-023` / `ADR-0008`) is the single strongest artefact in the repository for the assimilation question. For each axis it admits a member nobody has named and asserts the kernel source fingerprint stays byte-identical: unknown **entity form** (`declare_form("trans-dimensional-resonance")`), unknown **context kind** (`UNIVERSAL_TAXONOMY.extend(...)`), unknown **relationship type** (`"entangles-with"`), plus technology, language, currency, measurement and platform-composition cases.

This is why dimensions 3, 4 and 5 are classified EXISTING rather than PARTIAL: they are **open substrates with a test that proves the openness**, not fixed schemas with prose claiming openness.

---

# PART VI — EXECUTION GOVERNANCE ASSIMILATION

Reviewed as assimilation only. No change proposed, none authorized.

| Required verification | Verdict | Located mechanism |
|---|---|---|
| **Execution context model** | ✅ EXISTS, plural | `engine/context/runtime.py` `ContextRuntime` is the propagation stack (`bind`/`activate`/`current`/`require`/`provenance`/`frames`/`snapshot`/`restore`). Peers: `engine/runtime/context.py` `RuntimeContext` (reference frames), `engine/factory/factories/base.py:44` `ExecutionContext`, `engine/uaue/controller.py:116` `EvolutionContext`, `engine/uckp/values.py:406` `ContextBinding`. **Observation:** plural is not automatically duplication — but the ad-hoc `platform/*/context.py` classes (§4.5) bypass `UCXI-000001` and are unreconciled |
| **Technology neutrality** | ✅ ENFORCED NEGATIVELY | `ISD-L-09` `check_technology_is_evolutionary_state:473` — `pyproject.toml` runtime deps must be **empty**; `requires-python` may carry **no** `<`/`<=`/`==` (a floor with no ceiling); every verification-toolchain pin must be a `DeclaredPin` with a reason, reconciled two-way. `engine/uckp/law.py:360` — the law text is technology-, repository-, storage-, runtime- and implementation-agnostic. Gate-enforced via `uisd-gate.yml`, live verdict **OPEN** |
| **Runtime neutrality** | ⚠️ PARTIAL | Storage runtime is neutral and tested (`PersistenceAdapter`, 10 adapters incl. `FutureStoragePersistence`); provider runtime is neutral and gated (`uprf-gate.yml`, provider categories as open kernel meta-types). But **Python is the current execution manifestation, not a universal runtime** — and per §1.3 that reading is enforced only *negatively* (no ceiling, no pinned deps). There is no second runtime realization, and `adr/0021` discloses that no gate checks agnosticism as a cross-cutting property |
| **Deterministic validation** | ✅ ENFORCED, multiply | `engine/determinism/{hermetic,reproduce}.py`; `.github/workflows/determinism.yml`; **27 of 29** gate workflows assert determinism/replay/audit; the uniform pattern is an engine run with `--render --gate` (stdlib only, installs nothing) **plus a register drift gate** (`git diff --exit-code`). Cross-process proof: gates are run twice in separate processes and the JSON reports diffed; a wall-clock timestamp in a report is a CI error, because it would destroy the measurement. `verify.sh` Stage 6d does **byte** comparison, not parsed comparison |
| **`verify.sh` stability principle** | ✅ ENFORCED as a three-reader contract | Stage labels are re-derived by regex from source (`uisd-gate.yml:266`), asserted equal in order to `validation-record.json` (`:274-278`), and SHA-256 digest-matched (`:279-280`); a fourth reader derives the same digest in `platform/tests/test_canonical_validation_evidence.py`. `verify.sh` is additionally **forbidden from provisioning** — Stage 0 became `ucos_env_gate`, so it "may no longer create, install, or reach the network." `ec1-ci.yml:151` names `./verify.sh --full` explicitly, with a comment that dropping `--full` "would silently turn this job into a developer check" |

**Assimilation observation, recorded not acted upon.** The stability mechanism is strong enough to be a constraint on any future work: **editing a `run_stage` label breaks CI in four places at once.** Admitting a stage is a data change to `validation-record.json` plus a source change to `verify.sh`, and the two must be committed together. This is noted so that a later authorized cycle does not discover it by breaking it.

---

# PART VII — OWNERSHIP MAPPING

## 7.1 Ownership is total

**Every one of the fourteen dimensions has at least one named owner. No dimension is unowned. No dimension has two owners claiming the same subject.**

| # | Dimension | Primary owner (code) | Declaration home | Co-owners with disjoint subjects |
|---|---|---|---|---|
| 1 | Infinite Expansion | `engine/infinite_scope/` | `00-MASTER/UISD-000001/` | — |
| 2 | Agnostic Architecture | *distributed* — no single module | `adr/0021` | `platform/universal_provider/` (provider) · `engine/uckp/persistence.py` (storage) · per-layer invariants |
| 3 | Entity Model | `engine/uckp/ucko.py` | `UCOS-UCOM-001` | `engine/uckp/identity.py` (identity, SUPREME) · `engine/object_birth/` (birth) · `UCOS-UGA-001` (registry) |
| 4 | Relationship Evolution | `engine/ceu/existence.py` | `UCRD-001` | `engine/knowledge/ukip/relationships.py` (temporal) · `engine/graph/` (projection) · `data/relationship.py` (DATA plane) |
| 5 | Context Evolution | `engine/context/` | `00-MASTER/UCXI-000001/` | `CMG-000012` owns **only** the constitutional binding |
| 6 | Capability Evolution | `engine/uaue/` | `UCIC-001` (architecture owner) | `engine/uckp/evolution.py` (Art 14) · `engine/registry/universal/` (registry) · `URI-000001` (`realization/`) |
| 7 | Knowledge Evolution | `engine/knowledge/ukip/` | `USAF-001` · `UKAP-001` | `engine/uckp/` · `platform/universal_assimilation/` · `UAKOS-CLOSURE-008` |
| 8 | Memory Evolution | `engine/lineage/memory.py` | `ULP-MEMORY-LAYERS-001` | seven layer owners named **in the declaration**, not in code |
| 9 | Requirement Evolution | `00-MASTER/UAKOS-CLOSURE-009/` | `requirements.json` | `engine/uckp/evolution.py` (events) · **`UCOS-URR-001` NOT ADMITTED** |
| 10 | Execution Governance | `engine/execution_environment/` | `00-MASTER/UEG-000001/` | `engine/runtime/execution/` (`EPIC-RTE-002`) · `UCOS-EG-001` (**documents only**) |
| 11 | Lifecycle Governance | `engine/nucleus/lifecycle.py` | `00-MASTER/UCL-000001/` | `CMG-000001` (law) · `UCIC-001` (capability) · `CEP-009` (amendment) · Art 14 (evolution) |
| 12 | Verification Governance | `engine/verification_intelligence/` | `00-MASTER/UVI-000001/` | `engine/verification_impact/` (impact) · `verify.sh` (entrypoint) · `UAKOS-CLOSURE-008` (stage digest) |
| 13 | Artifact Governance | `platform/repository_intelligence/generated_artifacts.py` | `00-BOOK/DATA/generated-artifact-registry.json` | `UCOS-UGA-001` (objects) · `REG-AUTO-001`/`ukb.py` (authored corpus) |
| 14 | Mutation Governance | `platform/repository_intelligence/mutation_classification.py` | `00-BOOK/DATA/mutation-governance-boundary.json` | `engine/foundation/guards/frozen_paths.py` (paths) · `platform/identity/policy.py` (actors) |

## 7.2 How non-duplication is guaranteed rather than hoped for

Three executable mechanisms, all located:

1. **`--check-no-parallel-authority`** (`ucl-gate.yml:105`) — a second lifecycle authority is a **gate violation**, not a review comment. `ARCHITECTURAL-ASSUMPTION-DETECTION-DESIGN-ANALYSIS.md` cites this as the reason it refused to build a second assumption detector.
2. **`CXL-06` Context Once** — "one canonical home per unit of context" is a law *of the model*, so a second Universal Context Model would violate the first-order law of the thing it purports to define. `CAA-INV-07` independently forbids an instrument declaring a rival object model.
3. **Mutation boundary tests** — `test_1_every_mutation_class_names_exactly_one_governing_chain`, `test_2_no_class_is_claimed_by_two_authorities_as_primary`, `test_3_no_mutation_class_is_ungoverned`.

**Assimilation finding.** Plurality in this repository is usually **disjoint subjects, not duplication** — the four-instrument lifecycle stack and the four relationship planes are each explicitly reconciled by a determination. The genuine unreconciled plurality is narrower and specific: the ad-hoc `platform/*/context.py` classes (§4.5), the two entity-kind vocabularies (§4.3), the band-local capability lifecycles (§4.6), the two requirement planes (§4.9), and `EXCLUDE_DIR_PREFIXES` as a second expression of "generated" (§4.13).

---

# PART VIII — AUTHORITY MAPPING

## 8.1 The authority pattern is uniform and self-declared

Reading the `AUTHORITY` line of the owners reveals a consistent four-tier structure. **This is the most important structural fact for anyone extending the system.**

| Tier | Meaning | Instances | Self-declared marker |
|---|---|---|---|
| **LAW** | What counts as constitutional | `CMG-000001` (v1.2) · `UCKP-LAW-0001` (`engine/uckp/law.py`) · `CEP-002/005/007/009` · `UCI-001` | Named as `law_owner` in `ucl.json`; named as `constitutional_superior` by #13 and #14 |
| **SUPREME SINGLETON** | Exactly one mint / one authority for a scarce resource | `engine/uckp/identity.py` — `role: SUPREME — this IS UCKP-ART-05` | Guarded by `second_authority_test`: "a mint is recognised by the counter it advances" |
| **CONTRACT / ARCHITECTURE OWNER** | Binding structure others must satisfy | `UCIC-001` (FROZEN v1.0) · `UOBC-000001` · `UEG-000001` · `UCOS-GENERATED-ARTIFACT-REGISTRY-001` | "no capability may bypass this contract or skip a gate" · "upstream of every engine it describes" |
| **DERIVED TRUTH** | Measures and projects; **legislates nothing** | `UCL-000001` · `UISD-000001` · `ULP Part 05` · `UAKOS-CLOSURE-009` · `UCOS-UGA-001` · every root `*-DETERMINATION.md` · **this artifact** | `AUTHORITY: NONE — DERIVED TRUTH` |

## 8.2 Authority paths — quoted verbatim

| Owner | Self-declared authority |
|---|---|
| `engine/uckp/identity.py` | `role: SUPREME — this IS UCKP-ART-05` |
| `UCL-000001` | "NONE — DERIVED TRUTH … legislates no lifecycle, opens no registry, mints no identifier" |
| `engine/lineage/memory.py` | "NONE — DERIVED TRUTH. This file CREATES NO MEMORY STORE, NO MEMORY ENGINE, NO KNOWLEDGE MEMORY AUTHORITY and NO HISTORY AUTHORITY … this is a RESOLUTION ORDER over those owners" |
| `engine/runtime/execution/authorization.py` | `EXECUTION_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"` — "never constitutional authority or finality (ORL-22)" |
| `generated-artifact-registry.json` | "AUTHORED REPOSITORY TRUTH, HELD AS A PROJECTION UNDER UCKP-LAW-0001 … It is upstream of every engine it describes and must never be produced by one of them" |
| `mutation-governance-boundary.json` | "AUTHORED REPOSITORY TRUTH, HELD SUBORDINATE UNDER UCKP-LAW-0001. This artifact declares the boundary; it does not create a new authority and governs nothing itself" |
| `verify.sh` | "Canonical Verification Entry Point … MODES ARE NOT DECLARED HERE. `00-MASTER/UVI-000001/uvi-declaration.json` holds the Verification Mode Constitution" |
| `adr/0021` (UAP-001) | "DESIGN PRINCIPLE — not a certification … no gate, invariant, or certification currently checks conformance to this statement" |
| `02-MASTER/…CAPABILITY-CATALOG.md` | "CONSTITUENT AUTHORITY: NONE · GOVERNANCE AUTHORITY: NONE · RATIFICATION AUTHORITY: NONE · EC-1 AUTHORITY: NONE" |
| `UCOS-URR-001` | `PROPOSED — NOT ADMITTED` |
| **this determination** | **NONE — DERIVED TRUTH** |

## 8.3 Two authority defects located

1. **A dangling authority (dimension 11).** `CMG-000008`, `CMG-000009` and `CMG-000010` each assert, seven times over, inheritance from *"Universal Recursive Constitutional Lifecycle Governance v1.0"*. **No such instrument exists** — the string appears in exactly the three files that claim to inherit it; there is no declaration, engine, registry entry, gate, or code path that reads it, and **nothing parses those documents' `LIFECYCLE METADATA` block**, so all 21 claims are unmeasured prose. The determination states the consequence precisely: *"each document's own Lifecycle Compliance Declaration certifies conformance to an instrument that cannot be located, so the certification cannot be false — which makes it worthless as evidence."*
2. **An unenforced authority (dimension 2).** `UAP-001` holds authority *as direction* and explicitly holds none *as certification*. Recorded here so that no downstream artifact cites it as evidence of agnosticism.

---

# PART IX — EVIDENCE REFERENCES

## 9.1 Evidence buckets

Evidence is kept in five distinct buckets throughout §4 and is not interchangeable. **A declaration is not an implementation; a test is not a gate; a gate that never ran is not evidence.**

| Bucket | Meaning | Example |
|---|---|---|
| **CODE** | An executable path with symbol + line | `contract.py:733` `check_admission_path_exercisability` |
| **DECLARATION / DATA** | The governed data an engine reads | `00-MASTER/UISD-000001/uisd-declaration.json` |
| **CI-GATE** | A workflow step that blocks | `uisd-gate.yml:279-280` digest match |
| **TEST** | An assertion, ideally non-vacuous | `test_infinite_scope.py:307` |
| **LIVE-RUN** | Executed during this assimilation | §9.2 |

## 9.2 Live read-only measurements taken during this assimilation

All executed with the repository interpreter `.ec1-venv/bin/python` at HEAD `bae59755`.

| Command | Result | Reads as |
|---|---|---|
| `python -m engine.infinite_scope.gate --quiet` | **exit 0** | `OPEN` — no undisclosed finite closure among declared surfaces |
| `python -m engine.object_birth.gate --quiet` | **exit 0** | Birth contract laws hold |
| `python -m engine.uaue.gate --quiet` | **exit 0** | Evolution surface consistent |
| `python -m engine.execution_environment.gate --quiet` | **exit 0**, one advisory: `! EEG-08 no unsupported global executable usage: 38 condition(s)` | Environment admissible; **EEG-08 is the non-blocking eighth check** — 38 conditions is a *currently observed* count, not a bound |
| `validate_rule_coverage(mutation-governance-boundary.json)` | `("rule 'R-09' is declared but no predicate implements it",)` | **Live finding** — O-14 |
| `requirement_engine.py --gate` | `ASSIMILATION GATE FAIL — 409 of 549 requirements are not FULLY ASSIMILATED` · `fully=140 partially=409 not=0 (25.5009%)` · `open_gap_classes=12` · `work_packages=12` · `baseline=WITHHELD(12 preconditions unproven)` | **Requirement-plane assimilation is 25.5% and the baseline is withheld.** Retained as evidence; the twelve files this invocation wrote were restored (§2.3) |
| Session-start hook | `UAKOS-CLOSURE-002: CLOSED \| concepts=549 \| gaps=0` across `conversation_only`, `duplicate_canonical_homes`, `in_repo_unhomed`, `not_homed_concepts`, `orphan_concepts`, `ukda_content_hash_duplicates`, `upload_only` | Knowledge closure holds — **qualified**: `conversation_only` measures 0 by absence when the external corpus is not present |
| `git status --porcelain \| wc -l` before and after | **59 → 59** | No net change to the working tree |

**Reading of the two apparently conflicting results.** `UAKOS-CLOSURE-002` reports `gaps=0` for **concept homing**; `UAKOS-CLOSURE-009` reports **25.5%** for **requirement assimilation**. These do not contradict: every concept is homed (549/549), and the requirement *projection* of those concepts is only 25.5% fully assimilated across its seven dimensions. **Homing is complete; dimensional population is not.** Anyone citing "gaps=0" as evidence of overall completeness would be misreading the scope of that gate.

## 9.3 Primary evidence index

| Dimension | Primary code evidence | Primary declaration | Primary gate | Primary test |
|---|---|---|---|---|
| 1 · Expansion | `engine/infinite_scope/contract.py` | `uisd-declaration.json` | `uisd-gate.yml` | `test_infinite_scope.py` (117) |
| 2 · Agnostic | `engine/uckp/persistence.py:101` | `adr/0021` | `uprf-gate.yml` (partial) | per-layer suites |
| 3 · Entity | `engine/uckp/ucko.py` · `object_birth/scope.py` | `uobc-birth-contract.json` · `birth-scope-policy.json` | `verify.sh:502,435` | `test_object_birth.py` · `test_birth_scope.py` |
| 4 · Relationship | `engine/ceu/existence.py:918` · `ukip/relationships.py` | `UCRD-001` · `adr/0015` | **none** (`ISD-G-04`) | `test_relationships.py` (72) · `test_existence.py` (47) |
| 5 · Context | `engine/context/resolution.py` | `ucxi-declaration.json` · `CMG-000012` | **none** | `engine/tests/context/` (13 files) |
| 6 · Capability | `engine/uaue/controller.py` · `uckp/evolution.py` | `UCIC-001` · `UAUE-000001` | `uaue-gate.yml` · `uaep` · `ufc` | 5 uaue suites |
| 7 · Knowledge | `engine/knowledge/ukip/` · `platform/universal_assimilation/` | `canonical-knowledge.json` + history | `assimilation-gate.yml` · `corpus-currency-gate.yml` | `test_confidence.py` · `test_corpus_currency.py` |
| 8 · Memory | `engine/lineage/memory.py` | `memory-layers.json` · `adr/0013` | **none** | `test_req_43_upeg_certification.py` |
| 9 · Requirement | `requirement_engine.py` · `uckp/evolution.py` | `requirements.json` | `closure009-gate.yml` | `test_closure009_requirement_engine.py` · `test_phase_2_requirement_evolution.py` |
| 10 · Execution | `engine/execution_environment/` · `engine/runtime/execution/` | `ueg-declaration.json` | `determinism.yml` · `verify.sh:85-124` | `test_execution_environment.py` |
| 11 · Lifecycle | `engine/nucleus/lifecycle.py` | `ucl-stage-manifest.json` | `ucl-gate.yml` | `test_lifecycle_validation.py` |
| 12 · Verification | `verification_intelligence/selection.py` | `uvi-declaration.json` · `validation-record.json` | `ec1-ci.yml:151` · `uisd-gate.yml:260-282` | `test_verification_purity.py` |
| 13 · Artifact | `generated_artifacts.py` · `uga_engine.py` | `generated-artifact-registry.json` (345) | `verify.sh` 6b · ~9 replay gates | `test_generated_artifact_registry.py` |
| 14 · Mutation | `mutation_classification.py` · `frozen_paths.py` · `identity/policy.py` | `mutation-governance-boundary.json` | `ec1-ci.yml:40,147` | `test_mutation_classification.py` · `test_mutation_governance_boundary.py` |

---

# PART X — OPEN OBSERVATIONS

Observations, not instructions. No remediation is proposed, sequenced, or authorized.

| ID | Dimension | Observation | Named gap |
|---|---|---|---|
| **O-1** | 1, 12 | Assumption/closure detection is **declaration-bound, not discovery-bound**: `ISD-L-01`/`ISD-L-10` audit only the eleven already-disclosed closures. Nothing sweeps the repository for an *undeclared* `Enum`, `frozenset` or literal tuple, so a closure added tomorrow is invisible until a human discloses it | `AD-G-01` |
| **O-2** | 1 | A live undisclosed-intent closure: `ISD-CE-09`, `KnowledgeCapability` in `ukip/constitution.py`, population 11, `intentional: false`, `closing_invariant: "NONE DECLARED IN CODE"` | `AD-G-05` |
| **O-3** | 2 | Agnosticism has **no cross-cutting gate** — disclosed by `adr/0021` itself. API/Communication and UI/Experience have no implementation surface to evaluate | self-disclosed |
| **O-4** | 3 | Two entity-kind vocabularies coexist (`birth-scope-policy.json` kinds vs `engine/uaue` `ObjectKind`) with no reconciling registry located | — |
| **O-5** | 4, 5 | The **same gap seen twice**: temporal validity and per-subject context binding landed in the knowledge-closure plane and were not propagated to the existence and graph planes | `P4-F-002`, `P4-F-009` |
| **O-6** | 4, 5, 8 | Three dimensions with EXISTING models have **no dedicated CI gate**; a relationships gate is explicitly out of scope for its cycle | `ISD-G-04` |
| **O-7** | 6 | Capability evolution parts exist but are **not wired**: no path takes a registered capability through admission → certification → lifecycle transition; `CapabilityRegistry` has no lifecycle field; capability certification coverage of implementation is measured at **0%** | `AEOS-001` AC-1…AC-6 |
| **O-8** | 8, 10 | Runtime `Checkpoint`/`Snapshot` and the `AuditLog` **have no durable sink** — `engine/runtime/execution/persistence.py` serialises to a string with no path — so cross-process replay of a real run has no on-disk input | — |
| **O-9** | 9 | **Two requirement planes, no join key**: 49 `REQ-NN` (manual, ungated) and 549 `RR-<CONCEPT-ID>` (engine, gated). The reconciliation determination holds they *"should coexist… joined by a declared relation rather than merged"* — **that relation is not declared** | `UCOS-URR-001` NOT ADMITTED |
| **O-10** | 9 | Requirement-plane assimilation measured live at **25.5%** with **baseline WITHHELD (12 preconditions unproven)**; named internal gaps `ARTIFACT-TRACEABILITY-SCHEMA-UNPOPULATED`, `LIFECYCLE-DIMENSIONS-NOT-OPERATIONAL` | 12 gap classes |
| **O-11** | 12, 14 | **A gate-purity violation observed live during this cycle**: `requirement_engine.py --gate` wrote twelve files. `--gate` is the blocking verb and is expected to observe; the writing verb is `--render`. Reverted (§2.3). Structurally this is the same class of defect the purity suite was built for after `register.sh --guard` minted 140 identities from a verification command | related to `adr/0020` |
| **O-12** | 12 | **No `gate_mode` field exists** anywhere in code or JSON, so PRODUCER-vs-OBSERVE is per-gate prose rather than a declared, validated field — which is precisely why O-11 was possible. `stages_reading()` computes stage-level impact but is "a QUERY, not a scheduler". Purity is asymmetric: measured against version control, not the filesystem | `H-06-TASK-002` |
| **O-13** | 13 | Drift enforcement is **per-owner, not universal**: no single gate regenerates all 345 registry entries and byte-compares. An artifact whose owner has no replay workflow is checked only for producer existence and input classification | — |
| **O-14** | 14 | **Verified live**: R-09 `GOVERNED_ANALYSIS` is declared in the boundary register but has **no predicate** in `RULE_PREDICATES` (R-01…R-08 only); `mutation_class_extension.py` builds the class and rule dicts but registers no predicate. Because coverage validation is two-sided and fail-closed, `validate_rule_coverage()` returns a finding. Separately, **no CI step runs `classify_all` over a commit's changed paths and fails on `UNRESOLVED`** | live measurement |
| **O-15** | 11, 13 | **145 determination documents exist in a governance void** — no identity, no ownership, no lifecycle stage, no disposition — per the most recent instrument (2026-08-22). Under §4.13's rule they are `NON_CANONICAL` evidence, which is *kept*; what is absent is their lifecycle binding, not their standing | `UNIVERSAL-ARTIFACT-LIFECYCLE-DETERMINATION` §1 |
| **O-16** | 11 | **A dangling lifecycle authority**: `CMG-000008/9/10` assert inheritance from an instrument that does not exist — 21 unmeasured, self-certifying claims | `CMG-000001` §6.2 crit. 3 |

## 10.1 Potential gaps — distinguished from confirmed

**Confirmed by direct reading or live execution:** O-1 · O-2 · O-3 · O-4 · O-7 · O-8 · O-9 · O-10 · O-11 · O-12 · O-13 · O-14 · O-15 · O-16.

**Potential — asserted by a located instrument but not independently re-measured in this cycle:** O-5 (the `$disclosures` block names `P4-F-002`/`P4-F-006`/`P4-F-009`; I read the disclosures, not each owner's absence of persistence) · O-6 (absence of a workflow file is verified; whether any owner considers a gate *required* is that owner's judgement).

**Explicitly not gaps, recorded to prevent future misreading:**

| Not a gap | Why |
|---|---|
| 33 closed facets | Closure **disclosed as intentional** with a closing invariant. The doctrine is that closure is not a defect; *undisclosed* closure is |
| Memory being a projection rather than a store | `ADR-0013` / `UCI-001 XVI.5` forbid a store. Partial is the **intended terminal state** |
| `00-MASTER/` excluded from the corpus | Constitutional tri-partition; 14 UIDs RETAINED-BUT-RETIRED, **nothing discarded** |
| Four lifecycle instruments | **Disjoint subjects**, reconciled by determination; merge is forbidden by `CMG` LXXVI.6 |
| Four relationship planes | Reconciled by `UCRD-001` §5 — relationships model bindings *between* objects, facets model properties *of* objects; "everything is a relationship" was deliberately rejected |
| `UCOS-URR-001` not admitted | A second register over an already-registered population is the competing measurement `UFC-16` forbids. **Refusal is the governed outcome**, not an omission |
| 145 determinations lacking identity | They are `NON_CANONICAL` **evidence, which is kept**. The gap is lifecycle binding, not standing |
| `UNRESOLVED` mutation verdict | The declared fail-closed terminal. "It confers no authority, and it must never be read as a permissive default" |

---

# PART XI — ASSIMILATION CLOSURE

## 11.1 What this determination establishes

1. **Fourteen dimensions assimilated. Zero missing. Zero documentation-only.** Nine EXISTING, five PARTIAL.
2. **Every dimension exists under a different local name.** §3.1 is the complete naming map. A future cycle that searches for the dimension names will find nothing and may wrongly conclude absence — this is the single highest-value output here.
3. **The residual gap is never absent capability.** It is an absent **join** (O-4, O-9), an absent **ratchet** (O-1, O-13, O-14), or an absent **propagation** (O-5). Each is closable by extending a located owner.
4. **"Locate, do not create" is enforced, not preferred** — `--check-no-parallel-authority`, `CXL-06` Context Once, `CAA-INV-07`, `UFC-16`, and the mutation-boundary tests.
5. **The interpretation rule is already law** in eleven places (§1.3). Counts in this repository are discovered populations; the governed property is whether the code enumerates or discovers them.
6. **Two measurements must not be conflated**: concept homing is complete (549/549, gaps=0, qualified); requirement dimensional assimilation is 25.5% with the baseline withheld.

## 11.2 Preservation statement

No artifact was deleted, removed, renamed, merged, or restructured. No source code was modified. No registry was mutated. No identity was minted. No programme ID, requirement, or ADR was created. No certification state was changed. No historical evidence was altered. The working tree entry count was **59 at open and 59 at close**. The single mutation that occurred (§2.3, O-11) was an unintended write by a gate invocation, was restored to its committed state on exactly the affected paths, and is disclosed rather than concealed — its measurement is retained as evidence.

## 11.3 Stop

**Assimilation complete. This determination stops here.** It performs and authorizes no implementation, remediation, optimization, refactoring, or certification change. The sixteen observations are recorded for a subsequent cycle under explicit authorization; none is a directive, and none has been sequenced into a plan.

---

*END · `UCOS-OMEGA-INFINITY-ASSIMILATION-COVERAGE-DETERMINATION.md` · AUTHORITY = NONE (DERIVED TRUTH) · Where this determination and a located instrument differ, the located instrument governs.*


---
---

# PART XII — SECOND ASSIMILATION PASS: 17-PHASE EXTENSION

| Field | Value |
|---|---|
| STANDING | **Extension of this same artifact, appended not overwritten.** Parts I–XI are unchanged and remain the record of the first pass. Nothing above was edited, deleted, or restructured. |
| TRIGGER | Directive expanded the assimilation from 14 dimensions to a 17-phase programme, adding phases with no prior coverage: intelligence expansion, truth/confidence, self-correction, composition/emergence, boundaries, unknown space, knowledge-source boundary, measurement model, and final classification. |
| BASELINE | HEAD `bae59755` unchanged · working tree **59 pre-existing + this artifact** at open |
| AUTHORITY | NONE — DERIVED TRUTH, as Part 0 |
| CORRECTION TO PART III | §12.10 records one correction to a premise carried in the first pass. |

## 12.1 Phase coverage map

| Phase | Subject | Covered by |
|---|---|---|
| 1 | Infinite expansion — entity, capability, context, relationship, knowledge, **intelligence** | §4.1, 4.3–4.7 · **intelligence: §12.2** |
| 2 | Agnostic architecture — **seven categories** | §4.2 · **per-category: §12.3** |
| 3 | Universal entity + relationship model across all object types | §4.3, 4.4 · §5.3 |
| 4 | Ownership and authority | Part VII, Part VIII |
| 5 | Temporal evolution | §4.4, §5.3 · **§12.4** |
| 6 | **Truth, confidence, evidence** | **§12.5** |
| 7 | Memory and knowledge | §4.7, 4.8 |
| 8 | Requirement evolution | §4.9 |
| 9 | Execution governance | Part VI · **verification cost: §12.6** |
| 10 | **Self-correction** | **§12.7** |
| 11 | **Composition and emergence** | **§12.8** |
| 12 | **Boundaries** | **§12.9** |
| 13 | **Unknown space** | **§12.10** |
| 14 | **Knowledge-source boundary** | **§12.11** |
| 15 | Universal lifecycle (26-step chain) | §4.11 · **§12.12** |
| 16 | **Measurement model** | **§12.13** |
| 17 | **Final classification** | **§12.14** and the companion matrix |

## 12.2 Phase 1 — Infinite Intelligence Expansion

**Classification: EXISTING IMPLEMENTATION for discovery/admission/measurement · GOVERNED CLOSURE for learning and reasoning.**

`intelligence/` is a real package — 55 Python modules across six subpackages: `rie/` (11), `realization/` (16), `publication/` (10), `research/` (8), `kernel/` (9), `die/` (1), plus a 6-file test suite. **RIE = Repository Intelligence Engine**, and it measures the repository as a subject: `UCOS-RIE-MODEL.json`, `-CAPABILITY-CATALOG.json`, `-DIGITAL-TWIN.json`, `-DEPENDENCY-GRAPH.json`, `-EXECUTION-FRONTIER.json`, `-AEOS-READINESS.json`, `-HEALTH.json`, `-PROGRESS.json`, `-SNAPSHOT.json`. `intelligence/realization/` is the URI-000001 generator that produced `realization/` from 131 canonical capability objects (§4.6).

**Intelligence discovery and admission are executable.** `intelligence/rie/discovery.py`, `census.py`, `analysis.py`, `canonical.py`. Admission of an *unforeseen* intelligence form is measured, not asserted: `engine/tests/expansion/test_universal_expansion_verification.py:188` `test_unknown_intelligence_form_needs_no_code_change`.

**Learning and reasoning are adjudicated as already-canonical rather than built.** `adr/0011-self-learning-and-evolution-are-already-canonical.md`, **Status: Accepted**, is dispositive and worth quoting because it settles the question:

> "We record self-learning and self-evolution as **represented by existing canonical capability**. Any additional stage — `ADAPTATION` among them — enters as a declaration against the UCL stage manifest, never as an engine change."
> Consequences: "Positive: no second evolution engine. Neutral: whether `ADAPTATION` should be a named stage is left open; the mechanism to add it exists and is measured."

Its measured basis: `EVOLUTION_CYCLE` declares fifteen stages, **no stage is terminal and the last returns to the first** (`ISD-L-05`), and `ISD-L-04` holds that the stage graph admits a stage without an engine change.

**This reconciles the apparent contradiction with `P4-F-008`.** `engine/lineage/memory-layers.json` deliberately declines a *learning layer* because "a separate layer would imply a learning store that no owner holds." ADR-0011 declines a *learning engine* because the perpetual evolution cycle already is one. **Both refuse to create a learning authority; neither denies the capability.** Learning is therefore correctly classified `GOVERNED CLOSURE` — an approved decision exists and implementation is intentionally pending — not `OPEN GAP`.

**Gap.** `ADAPTATION` is explicitly left open as a named stage. Reasoning has no dedicated executable surface: `engine/verification_intelligence` reasons over change impact and `intelligence/rie/analysis.py` over repository state, but there is no general inference engine, and none is claimed.

## 12.3 Phase 2 — Seven-category neutrality, assessed separately

**3 executable · 2 declaration-only · 2 no surface at all.** The finding `AD-G-03` — "4 of 7 categories have no executable check" — is **confirmed**, and the four are named.

| # | Category | Verdict | Basis |
|---|---|---|---|
| 1 | **ENGINEERING** — languages, frameworks, libraries, compilers, paradigms | **EXECUTABLE CHECK** | `ISD-L-09` `check_technology_is_evolutionary_state` parses `pyproject.toml` with `tomllib` and refuses: any non-empty `project.dependencies` ("a pinned runtime encodes a technology as constitutional truth"), any `<`/`<=`/`==` in `requires-python` ("a ceiling or an exact pin makes the language version a constitutional truth, not a state"), any `==`-pinned optional dep not disclosed in `declared_pins` with a reason, **and** any disclosed pin no longer pinned — bidirectional. CI: `uisd-gate.yml`; `verify.sh:539`. Test: `test_unknown_language_needs_no_code_change` |
| 2 | **SOFTWARE** — applications, services, runtime/deployment models, operating environments | **EXECUTABLE CHECK (partial)** | `test_unknown_platform_nucleus_needs_no_code_change:213` + `engine/tests/expansion/test_platform_composition_verification.py`, backed by `adr/0010`. Local name: *platform nucleus* / *platform composition*. But `11-SERVICE/` (0 `.py`, 19 `.md`) and `12-APPLICATION/` (0 `.py`, 22 `.md`) are **documentation-only trees** |
| 3 | **DATA** — relational, document, graph, vector, object, future forms | **EXECUTABLE CHECK — strongest in the repository** | `PersistenceAdapter(ABC):101` + ten adapters, `InterchangeabilityReport:610`, `universe_digest()` (order- and layout-independent), `build_persistence_suite:656` constructing all ten. **CERTIFIED for `engine/uckp` · GAP elsewhere**: `KnowledgeStore`, `ContextRegistry`, the UCDA register and the id-ledger each do direct file I/O "with no seam a second storage technology could implement against." No vector adapter exists; one would arrive as `FutureStoragePersistence` or a code change |
| 4 | **INFRASTRUCTURE** — local, cloud, edge, distributed, future substrates | **DECLARATION ONLY** | No hardcoded `/tmp/`, no `os.name == "nt"`, no `sys.platform ==` branches in core domain code; paths resolve through dynamic `repo_root()`. "No violation found; no dedicated 'runs identically under a different infrastructure' test exists either." **The one real finding is remediated**: `CloudPersistence(region="planet-earth-1")` is now `region: str \| None = None` (`persistence.py:489`, citing `adr/0012`) — *the "Earth is not universal" case, closed* |
| 5 | **COMMUNICATION** — API models, protocols, messaging, future mechanisms | **NO SURFACE AT ALL** | Grep for `fastapi\|from flask\|http.server\|aiohttp\|@app.route\|uvicorn` across `engine/ platform/ intelligence/ service/ application/` returns only two test/governance files mentioning the strings. **There is no `ProtocolAdapter`/`TransportAdapter` analogue to `PersistenceAdapter`.** Nothing to certify and nothing to violate |
| 6 | **EXPERIENCE** — web, mobile, voice, AR, VR, agent interfaces | **NO SURFACE AT ALL** | Zero `.tsx`/`.jsx`/`.vue` repo-wide; exactly one `.html`, and it is a *published output artifact*. `platform/portal/` and `platform/universal_portal/` are Python domain models (`routing`, `navigation`, `search`, `access`, `health`) with **no rendering layer**. Local name: "experience" exists as *portal*, as a governed service surface, not an interface |
| 7 | **TOOLS** — AI models, IDEs, CLIs, repositories, automation | **DECLARATION ONLY, with a real registration surface** | `engine/provider/metatypes.py` (`PROVIDER_CATEGORY_NS`, `CATEGORY_ROLE`, 11 `PROVIDER_FACETS` as data — "Nothing here names a vendor, a technology, or a concrete provider") + `platform/universal_provider/` (15 modules) + `engine/tests/provider/` (5 suites). **No test admits an unknown AI model / IDE / CLI as a new provider category with an unchanged kernel fingerprint** — the nearest is the intelligence-*form* test, which is a different axis |

**The flat count hides the important structure.** The four unchecked categories split into **two different failure modes**: INFRASTRUCTURE and TOOLS have real implementation surface with no check over it — a check is buildable today. COMMUNICATION and EXPERIENCE have *no surface at all*, so no check is buildable without first building an expression. The located assessment states this and **recommends against manufacturing one**: "building one merely to pass a certification would be manufacturing evidence, not discovering it, and is not recommended." Recorded here as the governed position, not as a gap awaiting closure.

**The authoritative per-dimension table is not in `adr/0021`** (see §12.15) but in `UCOS-ARCHITECTURAL-OPENNESS-ASSESSMENT-REPORT.md:69-79`, and it has **nine** dimensions with a declared rubric — CERTIFIED (a test or gate exists and passes) · SUPPORTED (no violation found, no executable proof) · GAP (a real hardcoded finite assumption, cited) · UNKNOWN (not enough of the layer exists to evaluate): Entity CERTIFIED · Context CERTIFIED · Relationship CERTIFIED · Technology CERTIFIED (scoped) · API/Communication SUPPORTED · UI/Experience **UNKNOWN** · Data/Storage CERTIFIED for `engine/uckp`, **GAP** elsewhere · Infrastructure SUPPORTED · Tool SUPPORTED.

## 12.4 Phase 5 — Temporal evolution: the fail-closed-on-incomparable discipline

Beyond §4.4 and §5.3, one pattern recurs across **six** independent sites and is the repository's characteristic epistemic move: **an unorderable or unmeasurable comparison produces a named third outcome, never a guess.**

| Site | Third outcome |
|---|---|
| `engine/temporal/operations.py:176,181,190` · `coordinate.py:55` | `Ordering.INCOMPARABLE` — "compare across systems fails closed into INCOMPARABLE" (CMG-000002 Law 7); `coordinate.py:41` adds `UNKNOWN` for unqualified precision |
| `engine/knowledge/ukip/relationships.py:204,251,256` | The same branch propagated into the knowledge layer — an unorderable validity window is refused, not assumed |
| `engine/temporal/facets.py:168` | Same branch in the facet projection |
| `00-MASTER/UAKOS-CLOSURE-008/superiority_engine.py:113` | `UNDECIDABLE` — "either side not measurable — recorded as such, **never guessed**" |
| `engine/infinite_scope/gate.py:31-33` | `EXIT_FAULT=2` — "The declaration or contract is unusable. **A FAULT, never a verdict**" |
| `platform/universal_truth/policy.py` | `TruthClass.UNCLASSIFIED` with `rule=RULE_NO_DECLARED_ZONE` — "an honest absence rather than defaulting a locator into Truth" |

**Assimilation finding.** "Nothing exists without temporal understanding" is satisfied in the strong sense for the UKIP plane and in the weak sense elsewhere: where temporal understanding is *absent*, the system is built to say so rather than to substitute a default. That is a stronger property than universal temporal coverage, and it is the reason `P4-F-002` is a propagation gap rather than a correctness defect.

## 12.5 Phase 6 — Truth, confidence and evidence

**Classification: PARTIAL — strong primitives on three separate axes; no unified truth model; no confidence scale.**

**There is no executable truth-type vocabulary.** The string `DERIVED TRUTH` appears in **zero** `.py` files — it is a document convention for "this legislates nothing", an authority posture, not a truth type of a claim. What exists instead is **three unrelated enums on three different axes, with no mapping between them**:

| Axis | Location | Members | Types what |
|---|---|---|---|
| **Provenance stage** — the closest thing to a truth ladder | `engine/knowledge/ukip/provenance.py:38-62` `Stage(str, Enum)` | `OBSERVED · PROVIDED · CLASSIFIED · REGISTERED · CORROBORATED · RELATED · VALIDATED · CERTIFIED · SUPERSEDED` | the stages a **knowledge record** passed through. `REQUIRED_STAGES = (OBSERVED, PROVIDED, CLASSIFIED, REGISTERED)`, with `CORROBORATED` deliberately excluded so single-source knowledge is not penalised. `Stage.coerce()` fails closed |
| **Context authority** | `engine/context/taxonomy.py:117-118` `ContextAuthority` | `OBSERVED · INFERRED` (+ others) | how strongly a **dimension value** is asserted |
| **Repository truth class** | `platform/universal_truth/contracts.py:47-63` `TruthClass(str, Enum)` | `CANONICAL · DECLARATION · EVIDENCE · DERIVED · OPERATIONAL_MEMORY · HISTORICAL · GENERATED · TRANSIENT · UNCLASSIFIED` | **where truth lives** — a custodial class, not an epistemic status |

**`platform/universal_truth/` is not an epistemic-truth engine — it is a custody classifier**, and expecting otherwise is the trap. Owner `UCOS-URTF-001`; its rule: *"Repository Truth SHALL be determined by policy, never by hardcoded paths."* It has **zero path literals**; the repository's directory names appear only in `catalog/ucos-repository-truth.json`. Structural invariant: a class in `NON_HOME_TRUTH_CLASSES = (EVIDENCE, DERIVED, OPERATIONAL_MEMORY, HISTORICAL, TRANSIENT, UNCLASSIFIED)` **may never be declared canonical-home eligible — the declaration itself fails closed.** `TruthPolicy.register()` is idempotent by fingerprint and refuses redefinition of a zone id with a different body. `classify()` is total. `TruthPartition` identity is `UCOS-URTP-<hash[:16]>`, deliberately disjoint "so a classification can never be mistaken for the fact it classifies."

**Confidence is an unvalidated free-form string.** `engine/knowledge/ukip/confidence.py`: `confidence_declaration(record, *, confidence: str, authority=ContextAuthority.INFERRED, note="")` — **no enum, no numeric band, no range check**. Grep for `class .*Confidence`, `ConfidenceBand`, `CONFIDENCE_LEVEL`, `confidence: float` across `engine/ platform/ data/ 00-MASTER/` finds **nothing**. **There is no confidence scale in this repository.** It binds to `f"{knowledge_id}@{version}"`; a different value for the same key raises `DuplicateContextError` under `CXL-06` Context Once, so correction must go through `resupersede_confidence()`. And its own docstring discloses that **no owner persists the `ContextRegistry`** — confidence exists only in memory.

**No uncertainty metric and no general evidence-sufficiency refusal exist.** The nearest are two verification-scoped laws, `no_mode_claims_more_than_it_measures` (`UVI-L-05`) and `no_assurance_reduction`, which enforce "no claim exceeds evidence" **for verification modes only**. Plus `requirement_engine.py:63-67`, which records missing optional inputs as `ABSENT` and "degrade[s] the measurement transparently rather than being silently assumed (Zero Silent Repair / Zero Hidden Assumptions)."

**One place enforces denominator disclosure, and it is the model to cite.** `engine/ceu/possessions.py:237-259` `completeness()`:

> "Completeness is reported as a measured state, never assumed (CEU-018): the ratio is computed from the population actually present, and **the denominator travels with it so a percentage can never be read without knowing what it is a percentage of.**"

It returns `units`, `possessions`, `held`, `required`, `ratio`, and yields `0.0` on an empty population rather than a vacuous 100%. Tested at `engine/tests/ceu/test_possessions.py:160`.

**Gap.** No single truth-type vocabulary; `DERIVED TRUTH` unrepresented in code. Confidence has no scale and **no persistence owner** (self-disclosed). No uncertainty measure. Denominator discipline exists in one module and is not a repository-wide rule.

## 12.6 Phase 9 — Verification cost and the mode constitution

The directive asks whether validation overhead is held under a 60-second target. **The repository solves this differently, and its solution is more honest than a fixed budget: it made the cost explicit per mode rather than capping it.**

`verify.sh` declares **five modes** (`--fast`, `--change` = default, `--integration`, `--full`, plus `--failfast`/`--serial`/`--explain`), and the header states the reasoning:

> "THE DEFAULT CHANGED, AND SAYING SO IS THE POINT. It was the full certification contract; it is now `--change`… certification did not become weaker — it became EXPLICIT: `.github/workflows/ec1-ci.yml` invokes `./verify.sh --full` by name… What changed is that the command a developer types dozens of times a day no longer costs a release certification. **A 47-minute default is a default people route around, and a gate that is routed around is not a gate.**"

**No fixed second-count target exists anywhere**, and one is deliberately not wired: `make verify-cost-model` re-measures the shard cost table and its comment states *"It is a measurement, not a fact about the repository: a stale entry makes a plan slower and never wrong, so this is deliberately not wired into any gate."* Timing is measured and reported per stage (`verify.sh:261-284`, with each subshell recording its **own** elapsed time because "misattributing 440 seconds to a gate that took one is worse than no summary") and totalled at `:308`.

**Modes are not declared in the script** — `00-MASTER/UVI-000001/uvi-declaration.json` holds the Verification Mode Constitution, and `UVI-L-01` measures that the flags the script accepts and the modes the constitution declares are **the same set in both directions**. Four further laws are load-bearing: `UVI-L-04` is a ratchet holding that every stage the old certification default ran must still be a declared stage *and* still admitted by every certification-eligible mode; `UVI-L-05` refuses any mode claiming more than it measures; `UVI-L-06` measures that **nothing anywhere names a test file**; `UVI-L-08` measures that sharding and concurrency change no obligation — shards union to exactly the selection and the coverage floor is evaluated once over combined data.

**Also verified for Phase 9:** verify.sh "verifies the environment; it does not repair it" — self-healing moved to `bootstrap.sh` "because a command that repairs its own subject cannot report on it." No PATH dependence: "a brand-new terminal can run this with NO manual `source .../activate` and NO tribal knowledge… every gate then runs through the venv interpreter by absolute path." No human memory dependence: the default is safe and certification is named explicitly in CI.

## 12.7 Phase 10 — Self-correction

**Classification: EXISTING IMPLEMENTATION — and self-correction structurally cannot bypass governance, because every corrective target is either observe-only or gated.**

Four self-awareness planes exist as Makefile-bound targets, each with a **report / act / gate** triad:

| Plane | Report (read-only) | Act | Gate (fail-closed) |
|---|---|---|---|
| **Capability self-awareness** | `make selfaware-report` → `engine.knowledge.cli capabilities` | `make selfaware` → `capabilities --write` | `make selfaware-gate` → `capabilities --gate`; message: *"SELF-AWARENESS STALE… capability register is behind the repository"* — described as *"the guard that keeps the reuse engine from going blind again"* |
| **Repository intelligence** | `make rpi-report` → `cli scan`, *"persisting nothing"* | `make rpi` → `cli emit` | `make rpi-gate` → `certify` **then** `verify`, fail-closed on **both** halves, *"in the order that reports the more actionable failure first"* |
| **Canonical ownership / homing** | `make homing` (*"Reads only; assigns nothing"*) | — | `make homing-gate` — non-zero while any concept's canonical home is undeclared |
| **Foundation conformance** | `make constitution` | — | `make constitution-gate` — non-zero while any capability fails **or faults** any article |

**Drift detection is executable and distinct from the register drift gates.** `rpi-gate` runs `certify` — which "re-derives the certificate from the live repository, so a NOT-CERTIFIED verdict is a finding about the repository and never a stale file being re-read" — and then `verify`, which "proves the producer is deterministic: two scans of one substrate must yield byte-identical artefacts", **and is fail-closed on an INCONCLUSIVE proof too**, so "a concurrent writer cannot be mistaken for a pass."

**Recovery guidance exists and is deliberately non-binding.** `make homing-recommend` splits the residue three ways — the **RATIFIABLE** residue (a deterministic provider can state the assignment an authority would ratify, with its located basis), the **REMEDIABLE** residue (a named eligibility deficit at a named locator, so what is needed is an act, not a decision), and the **GOVERNANCE MINIMUM** (neither). Its stated reason is a correction of a prior overstatement: *"reporting the second as 'irreducible' billed a mechanical omission as constitutional ambiguity."* And the constitutional guardrail is explicit: **"A recommendation is never ownership and no engine reads one as evidence."** `make homing-draft` emits a document carrying `ratified:false`, "deliberately a separate document from the governed ownership catalogue, so ratification stays an explicit constituent act."

**Self-correction cannot bypass governance — proven by construction in one case.** `make convergence-gate` **fails if a retired module reappears**: the engine-side homing resolver `engine/knowledge/homing.py` was retired because "two determinations over one population reported different numbers, which `UCOS-UFC-001` UFC-16 forbids", and "supersession is enforced, not documented." The converged determination reproduces the retired measurement exactly (151 declared, 390 unresolved over 541 subjects).

**Gap, self-disclosed in the Makefile itself.** The `rpi` comment records an **HONEST LIMIT**: emit writes to `.runtime/repository-intelligence/`, which `.gitignore:12` excludes, so "the artefacts are therefore OUTSIDE Repository Truth — re-running refreshes them locally but commits nothing a clone can reproduce. Staleness returns the moment this is not run." It also records the original defect precisely: *"A producer nobody re-runs does not measure the repository, it measures whenever somebody last remembered to"* — the certificate had gone 142 commits and 500 files stale while still being read as current. These targets close the "nothing re-runs it" half and **cannot close the other half**, which requires a constitutional determination on `.gitignore` against the twelve Truth zones (W0-1).

## 12.8 Phase 11 — Composition and emergence

**Classification: EXISTING IMPLEMENTATION — and "new structures emerge without kernel redesign" is the single best-evidenced claim in the repository.**

**The kernel is provably enum-free.** `engine/kernel/compliance.py:80-88` `kernel_source_fingerprint()` hashes name-and-bytes of **every `*.py` in `engine/kernel/`**, sorted, NUL-delimited. Alongside it, `_kernel_has_no_closed_enum():91` proves that **no source in the kernel package defines a closed `enum.Enum` at all** — "A closed enumeration of kinds is precisely what the meta-kernel must not contain; the absence of *any* Enum subclass in the kernel package is a strong, mechanised proof." It takes `directory` as a parameter **only so the proof is itself testable against a control sample** — i.e. the proof is non-vacuous by construction.

**Eleven concretely alien categories are admitted with the fingerprint unchanged.** `engine/kernel/compliance.py:63-73` is not abstract: `Civilization/Xophar-Collective` (substrate `plasma-lattice`, `known: False`) · `LanguageFamily/Glyphic-Resonance` (modality `electromagnetic`) · `ValueExchangeSystem/Entropy-Credit` (unit `reversible-negentropy`) · `TaxationModel/Gradient-Levy` · `AuditModel/Causal-Witness` (proof `lightcone-attestation`) · `TemporalModel/Branching-Retrocausal` (topology `non-linear`) · `GovernanceModel/Consensus-Swarm` (decision `emergent-quorum`) · `ScientificModel/Trans-Dimensional-Field` · `ProviderCategory/Substrate-Weaver` (realises `unbounded`) · `CapabilityDomain/Reality-Compilation` (scope `cross-universe`) · `ExecutionModelUnknown/Superpositional-Dispatch` (parallelism `amplitude`). Each record asserts `discoverable`, `traceable`, `governed`, and the aggregate verdict is `passed = all_ok and kernel_unchanged`, under `"obligation": "mandatory-architectural-proof"`.

**Ten expansion axes are a closed, enforced contract.** `engine/tests/expansion/test_universal_expansion_verification.py` — `test_unknown_*_needs_no_code_change` for entity form `:29`, context kind `:55`, relationship type `:77`, technology execution kind `:98`, language `:121`, currency `:144`, measurement unit `:167`, intelligence form `:188`, platform nucleus `:213`, future concept `:239`; plus `test_every_admission_is_journalled_and_the_journal_verifies:262` ("Admission of the unknown is RECORDED, not merely permitted") and **`test_suite_proves_every_principle_axis:291`**, which reflects over the module, collects every `test_unknown_*` function, and asserts an explicit axis→test-name map at `:307-316`. **The ten is therefore an enforced contract, not an incidental count** — dropping an axis fails the suite.

**Composition surfaces per layer.** Ordering is derived, never hardcoded: `engine/foundation/composition/ordering.py::derive_order`, consumed by `engine/nucleus/lifecycle.py::stage_order()`. Context composition: `engine/context/composition.py` — `ComposedContext`, `compose()`/`compose_universal()`/`merge()`, `missing_universal()`, `is_universally_complete()`, `can_reference()`, `frames_of()`. Relationship composition: `SEED_TOPOLOGIES` (17 arrangements) as **data rows**, plus `COMPOSITION_RULES` deriving transitive relationships that carry a cited derivation `path`. Capability/entity composition: `service/composition.py`, `application/composition.py`, `platform/universal_generator/`, `platform/blueprints/`.

**Gap.** ADR-0008, which chartered the expansion suite, is still **Status: Proposed** while its suite is fully implemented — the ADR status and the code disagree. There is **no dedicated CI workflow** for `engine/tests/expansion/`; it is enforced only transitively through the repo-wide `run_stage "pytest + coverage gate (--cov-fail-under=90)"` at `verify.sh:380`.

## 12.9 Phase 12 — Boundaries

**Classification: PARTIAL — ten boundary kinds are executable; the eight *governance* boundaries are declaration data whose refusals are asserted rather than computed, with one exception.**

There is no module named `boundary*`. The model is realised under the local names **guard · policy · isolation · federation · zone · frozen prefix · forbidden_write_prefixes · freeze_scan/preserved_sites**.

| # | Boundary kind | Enforcer | Enforced by |
|---|---|---|---|
| 1 | Corpus write | `frozen_paths.py:33` `FROZEN_PREFIXES = ("00-BOOK/","00-SOURCE/","99-FREEZE/")`; `assert_no_frozen_write` → `SecurityViolation`; CLI `ec1-frozen-guard` | **CI** `ec1-ci.yml:132` pipes changed files into `--stdin` |
| 2 | Trust / RBAC | `platform/identity/policy.py` — four ordered fail-closed guards then default-deny | code |
| 3 | Security-zone mutation direction | `platform/security/zones.py` `zone_may_mutate()` (UMB-INV-01: `ZONE_LEVEL[src] <= ZONE_LEVEL[tgt]`, with a `CANON_ZONES` carve-out so ZONE-3/4 never mutate ZONE-0/1/2); append-only `PostureLedger` | code — but **evaluative and non-enacting**: it decides and records, it does not intercept |
| 4 | Context isolation | `engine/context/composition.py:128` `can_reference()`; `compose()` raises on unsatisfied isolation | code |
| 5 | Execution isolation | `engine/runtime/execution/isolation.py` `isolate()`; fails closed on a cross-partition dependency **and** on an unpartitioned universe | code |
| 6 | Federation — the authorised crossing | `federation.py` `federate()`/`assert_federated()`, ENG-005 Federation References | code |
| 7 | Programme write scope | `forbidden_write_prefixes` in `00-MASTER/*/*-declaration.json`, consumed by per-engine `check_write_scope` (`ucef_engine.py:323-328,412-426`), typed at `universal_assurance/policy.py:400,415-418` | declaration + code |
| 8 | Execution-environment containment | `engine/execution_environment/contract.py` EEG-01…EEG-08 | code + `verify.sh` Stage 0 |
| 9 | **Permanence ratchet — the meta-boundary on boundaries** | `check_no_active_permanence_declaration` + `scan_occurrences`/`candidate_files` | code + declaration + `uisd-gate.yml` + test |
| 10 | Mutation boundary of the measuring gate itself (`ISD-BND-08`) | `uisd-gate.yml` runs the gate twice, diffing reports **and** `git status --porcelain` | **CI** |

**Boundaries are extensible by a named-channel rule, and this is the load-bearing doctrine.** `freeze_scan` walks declared roots (`.` depth-0, `00-CEP`, `00-CMG`, `99-FREEZE`, `engine`, `platform`) over six extensions, counting nine permanence phrases plus a `status: FROZEN`-style regex. Five site classes A–E; **class A is verbatim inadmissible**: *"active lifecycle declaration forbidding future change with no channel named — inadmissible."* Class E is exempt from exact-count enforcement with a recorded reason: classification registers legitimately grow, and *"a gate that fires on documentation maintenance gets disabled rather than fixed."* The check is even named to avoid the token it detects, "because a detector that matches its own source is its own first finding."

The channel itself is stated identically in two enforcers — `frozen_paths.py:14-27` and `policy.py:44-50`:

> "It does not place the corpus outside evolution. The forward channel is supersession — a new object carrying new identity and a lineage edge to what it supersedes (CEP-007 XIII), or amendment of the governing instrument (CEP-009), continuing through the Article-14 perpetual cycle. Identity is immutable, history is append-only, and evolution is unlimited through those channels; only in-place modification of a certified artifact is refused."

And the reason it must be stated: *"a prohibition that names no channel reads as a prohibition on change itself."*

**Trust boundary specifics.** `PolicyEngine.evaluate()` runs `_BUILTIN_GUARDS` as a fixed-order 4-tuple, first DENY wins: `_guard_frozen_corpus_write` (`frozen-corpus-write-forbidden`) · `_guard_certification_append_only` (`certification-ledger-append-only`) · `_guard_read_only_role_mutation` · `_guard_tenant_scope_isolation` (`scoped-principal-missing-tenant` / `scoped-request-missing-tenant` / `tenant-scope-violation`) — then `_deny(request,"no-grant")`. `WRITE_PERMISSIONS = {CREATE, EXECUTE, ADMINISTER}`; READ is explicitly non-mutating. The engine holds no clock and no state; identical inputs yield an identical content-addressed `AccessDecision`. Extensible via `PolicyEngine(extra_rules=[NamedPolicyRule(...)])` without editing the builtin tuple.

**Gap.** (i) The frozen-prefix literal is **duplicated** in `frozen_paths.py:33` and `policy.py:50` with no shared constant — two independent literals for one invariant, free to drift. (ii) `ISD-BND-01…07` name owners but carry **no computed refusal**; a violation is caught only if the named owner's own gate catches it. (iii) `platform/security/zones.py` decides but does not intercept. (iv) `ISD-G-05`: a Class-C site awaits an `ARTIFACT-RENAME-DETERMINATION.md` **that does not exist**. (v) `ISD-G-06`: `FROZEN` status values sit on derived generated surfaces inside guarded prefixes and under `00-MASTER`, which is excluded from the scan roots.

## 12.10 Phase 13 — Unknown space

**Classification: EXISTING IMPLEMENTATION. Unknown does not create architectural failure — and the reason is a deliberate two-sided rule, which is the finding that matters.**

**The governing distinction:** the unknown is **admitted at declaration/extension points**, where it arrives as a new declared member with a named admission path and an authority that mints its identity; the unknown is **refused at coercion/read points**, where an unrecognised token arrives inside an already-governed record — because admitting it there would silently widen a vocabulary nobody registered. `engine/ceu/existence.py` holds both halves in one class: `declare_form()` is open, `form_of()` fails closed.

**Open-world sites (unknown admitted):** `ceu/existence.py:357` `declare_form()` — "the open extension point of the substrate", which registers the new form's identity code with the one identity authority "so units of a brand-new form are minted by the same authority as everything else and `parse_kind_name` stays total" · `context/taxonomy.py:516` `extend()` — bounded open-world (CXL-02): must be new, must name an existing classified parent, may not claim a claimed kind, and **may not self-declare `universal`** because "universality is constitutional and cannot be granted by extension" · `taxonomy.py:48-49` — "Absence is expressed as an explicit unknown value, never as a missing kind" · `object_birth/scope.py:591` `BSP-L-02` — exactly one kind declares `catch_all` and it must be **last** · `lineage/memory.py:450-478` `resolve()` — "Open world by construction: an unknown subject yields a complete answer in which every layer is present and empty. It never raises for an unknown subject, and it never invents an entry", with `record_present=False` a distinct fact from an empty tuple · `provider/metatypes.py` — provider category is an open set, "Adding a facet, a category, or a provider is therefore a registration — never a framework change" · `uckp/persistence.py:574` `FutureStoragePersistence` — "A mechanism whose encoding Layer Zero does not understand… satisfies the identical contract regardless" · `persistence.py:474-500` `CloudPersistence(region=None)` — "A caller that does not know where it is asserts no location at all… a locality of a kind not yet described — because nothing here interprets the string" · `security/zones.py:10-12` — free-form future zone/control target.

**Fail-closed sites (unknown refused):** `registry/models.py:47-53` `LifecycleStatus.coerce()` → `RegistryValidationError("unknown lifecycle status")`, called on every record read at `:178` and `:265` · `generated_artifacts.py:281-282` — `input {inp!r} is UNKNOWN — fails closed`, reinforced at `:75`: "**UNKNOWN is absent by design**" from `CANONICAL_SAFE_INPUTS`, and note that `"UNKNOWN"` *is* a member of `INPUT_CLASSIFICATIONS` — the unknown is **representable and simultaneously disqualifying for canonical status**, which is the precise design · `ceu/existence.py` `form_of()` · `context/taxonomy.py:90,137,179,263` (four unknown-token refusals) · `infinite_scope/contract.py` `load_declaration()` — "**a declaration that cannot be read is not a declaration that permits everything**", exit code 2 · `infinite_scope/model.py` two-way closure on laws↔checks and on `ADMISSION_FORMS` · `identity/policy.py` `no-grant` · `runtime/execution/isolation.py`.

**The ability to admit an unknown is *measured*, not asserted — four instruments.** (1) `kernel_source_fingerprint()` before/after in all ten expansion tests; ADR-0008 names this as the discriminating property: an unchanged fingerprint distinguishes "an open substrate from an extensible one." (2) `ISD-L-06` `check_relationship_model_expands` — "proves openness by **performing** an extension in memory on every run, then proving the original vocabulary did not move. **A comment claiming a vocabulary is append-only is not evidence; a non-mutating extension is.**" It asserts the extension is a distinct object, the term is present, the original is unmutated, and the count is exactly `before + 1`; and it refuses shrinkage against a disclosed `population_at_baseline`. (3) `ISD-L-11` admission exercises — three declared: two `document_append` (over the UCL stage manifest and, self-referentially, the UISD declaration itself) and one `reader_document_append` over `uaue-evolution.json` going through **the owner's own declared reader**, "so an admission this form admits has passed the owner's real read path, not merely a dictionary update." The probe is *derived from a declared sibling* rather than written as a literal, "which makes the probe well-formed by construction for a population this engine knows nothing about", runs on `deepcopy` to stay inside `ISD-BND-08`, and must carry a declared id prefix so a probe cannot collide with a real member. Its scope limit is stated honestly: only populations whose admission path claims the change is data alone are exercised — "**a law that demanded exercisability of `ISD-CE-01` would be false, and a false law gets disabled.**" (4) `test_every_admission_is_journalled_and_the_journal_verifies`.

**Correction to a premise carried into the first pass.** ADR-0008's exact status is **Proposed**, not Accepted, though its suite is implemented and passing — recorded so that no downstream artifact cites it as a ratified decision.

## 12.11 Phase 14 — Knowledge-source boundary

**Classification: EXISTING IMPLEMENTATION for origin and lineage · PARTIAL for confidence.**

Origin is tracked as a **first-class classification with fail-closed semantics**, and the vocabulary already distinguishes the source kinds the directive names:

| Directive source kind | Local representation |
|---|---|
| Repository knowledge | `TruthClass.CANONICAL` / `DECLARATION`; `TRACKED_DETERMINISTIC` input class |
| Generated knowledge | `TruthClass.GENERATED`; `GENERATED_DETERMINISTIC` input class — admitted **only** on one enforced condition: declared in `generated_inputs` with a producer **and** a bootstrap path |
| Imported / external knowledge | `EXTERNAL` input class; `UKAP-001` corpus currency ordering ChatGPT exports by **content hash / git commit order, explicitly not filename or mtime** |
| Human knowledge | `Stage.PROVIDED` in the provenance ladder; `AUTHORED_DOCUMENT` mutation class |
| Machine-generated knowledge | `knowledge_seal` + `content_sha256` double seal in `realization/UCOS-URI-MANIFEST.json`; `authority: NONE (derived from canonical knowledge)` |
| Operational / environmental observation | `OPERATIONAL`, `ENVIRONMENTAL`, `EXECUTION_TRANSCRIPT`, `LOCAL_RUNTIME`, `ENVIRONMENTAL_OBSERVATION` — **all disqualifying for CANONICAL identity** |
| Unknown origin | `UNKNOWN` — representable, and fails closed for canonical status |

**Lineage** is hash-chained: `ProvenanceStep.step_sha256` with a `GENESIS` anchor and `ProvenanceChain.verify` (`ukip/provenance.py:38-79`); `00-BOOK/DATA/id-ledger.json` retains retired entries in `by_path`; `canonical-knowledge-history.json` is a separate register from the corpus.

**Authority per source** is the `validate():240` rule in §4.13: a `CANONICAL` artifact may not depend on an environmental/transcript/runtime input; the escape is to declare it `NON_CANONICAL`, "because it is then **evidence rather than identity**. Evidence is kept. What it may not do is claim to be repository truth." **This is the executable basis for the directive's own rule that existing artifacts are knowledge.**

**Gap.** Confidence per source is the unvalidated string of §12.5, with no persistence owner. The `conversation_only` gap class is unmeasurable without the external corpus at `REPO.parent/"UCOS"` and then "measures 0 by ABSENCE rather than by closure."

## 12.12 Phase 15 — The 26-step universal lifecycle chain

The directive's chain (Intent → Context Assimilation → Truth Discovery → … → Certify → Learn → Reason → Challenge → Predict → Simulate → Optimize → Evolve) maps onto **three existing stage sets with disjoint subjects**, not one: the **45-node** UCL constitutional stage graph (`ucl-stage-manifest.json`, data), the **15-stage** UCIC capability lifecycle, and the **15-stage** Article-14 perpetual evolution cycle (non-terminal, wrapping). §4.11 establishes that these are reconciled and that a merge is forbidden.

Coverage of the chain's distinctive tail: **Learn** → `GOVERNED CLOSURE` per ADR-0011 (§12.2) · **Reason** → no dedicated surface (§12.2) · **Challenge** → the closest located mechanism is `00-MASTER/UAKOS-CLOSURE-008/superiority_engine.py`, which compares competing claims and records `UNDECIDABLE` rather than guessing · **Predict / Simulate** → `H-06-DECISION-IMPACT-SIMULATION-DETERMINATION.md` exists as a determination; `engine/graph/architecture/impact.py` computes change impact; no forward-state projector located · **Optimize** → `make verify-cost-model` is the only located optimiser, and it is deliberately ungated · **Evolve** → `engine/uckp/evolution.py`, `is_terminated()` always False.

**Reading:** the chain's first two-thirds are implemented and gated; its final third (Reason, Challenge, Predict, Simulate, Optimize) is **the least-populated region of the entire assimilation** and should be classified `NOT YET ASSESSED` in the honest sense of §12.14 — not absent, not proven.

## 12.13 Phase 16 — Measurement model

**Classification: PARTIAL — the mechanism is EXISTING IMPLEMENTATION and well-factored; the governance rule against undeclared denominators is DOCUMENTATION ONLY, with one code exception (§12.5).**

`platform/measurement/` (`UCOS-EPIC-004` / `UCOS-UMA-001`, 14 modules) declares **four measurement kinds, closed as an enum**: `MeasurementKind = ENUMERATION · METRIC · COVERAGE · GAP` (`contracts.py:34-40`). `Measurement.measurement_id` is a pure function of `(kind, subject, payload)`, so identical measurements over identical Truth collapse to one id; its docstring states the discipline: **"A measurement is derived knowledge: it describes the corpus, it is never part of it."** `Metric.metric_id` identifies the *series* — a function of `(name, kind, labels)` and "never of the observed value". `MeasurementRegistry` is append-only, content-addressed, idempotent on identical body, and **fail-closed on a conflicting duplicate id**, in an identity namespace "disjoint from the Registry's universal ids, so a measurement can never be mistaken for, nor overwrite, a fact — **Measurement consumes Truth and never creates it.**" That disjoint-namespace discipline is the code-level embodiment of UFC-16's spirit even though UFC-16 is never named in code.

**Two unreconciled maturity models coexist.** (1) An **ordered 8-level lattice** in `requirement_engine.py:103-115`, declared "ordered, open-ended… **there is no ceiling in the model, only in the evidence**": `M0 REJECTED · M1 DEFERRED · M2 SPECIFIED · M3 IMPLEMENTED · M4 TEST-EVIDENCED · M5 VALIDATED-OR-VERIFIED · M6 CERTIFIED-PROVISIONAL · M7 RUNTIME-PROVEN`. (2) A **14-axis vector** in `platform/universal_foundation/constitution.py:126-142` `MaturityAxis`: `IMPLEMENTED · INTEGRATED · REGISTERED · DISCOVERABLE · CONFIGURABLE · COMPOSABLE · EXTENSIBLE · VALIDATED · VERIFIED · CERTIFIED · DETERMINISTIC · REPLAY_SAFE · TRACEABLE · GOVERNED`, where "each axis is proven by declared gates (`MATURITY_GATES`) rather than asserted, so 'mature' is a measurement over executed probes and never a status somebody typed." `IMPLEMENTED`, `VALIDATED` and `CERTIFIED` appear in **both** with different arities — a ladder level versus a vector component — and **nothing maps them.**

**The five dimensions the requirement engine measures**, from its own mission statement: *"MEASURE — never estimate — **assimilation coverage, lifecycle maturity, readiness, traceability and gap**."* Its 16 declared inputs are each `required` (fail-closed) or optional (recorded `ABSENT`, degrading the measurement visibly). Gap classes are **computed** by ~16 `add_gap()` calls over measured populations — so their count is a measurement output, not a closed enumeration.

**UFC-16, quoted, and a significant finding about it.** Verbatim: *"One subject population SHALL yield one measurement. Two Foundation surfaces reporting different numbers for the same population under the same policy is a constitutional contradiction and SHALL be converged, never reconciled by note."* It is cited by nine markdown files and one JSON as belonging to `UCOS-UFC-001` — but **`find -type d -name "*UFC*"` returns nothing: there is no `00-MASTER/UCOS-UFC-001/` directory in this tree.** The only place the full text appears is a blockquote inside `00-MASTER/UCOS-URR-001/00-URR-DISPOSITION-DETERMINATION.md:55-58`. **Zero `.py` files mention UFC-16 — it is entirely unenforced by code**, while being the rule most frequently cited to refuse new registers. Two CONFIRMED, undischarged breaches are on record and **deliberately reserved to a governing authority under CEP-002 14.2**: `RU-G-01` (49 `REQ-NN` vs 549 `RR-*`, no join key — "the repository cannot currently tell whether UFC-16 is satisfied or breached") and `PA-G-04` (22 principles in `uccep-bindings.json` vs 5 on the CKO plane).

**A fifth status vocabulary exists only as prose.** `COMPLETION-MEASUREMENT-MODEL-DETERMINATION.md` defines a six-link completion chain (REQUIREMENT → CAPABILITY → IMPLEMENTATION ARTIFACT → VALIDATION TEST → EVIDENCE ARTIFACT → CERTIFICATION STATE) with completion in fixed 20% steps and the rule "No partial certification permitted." **No engine computes this model.** Relatedly, `100-PERCENT-CLAIM-VALIDATION-DETERMINATION.md` **rejects a reported count**: a claim of 59 requirements / 76 items is adjudicated down to **54** (49 existing + 5 admitted of 10 candidates; 5 rejected as governance item ×2, duplicate, principle, derived constraint) — a worked example of the interpretation principle being applied against the repository's own prior claim.

**Gap.** UFC-16 has no source instrument in the tree and no code enforcement; two confirmed population divergences are open and reserved; two unreconciled maturity models; the six-link/20% model is prose that no engine computes; **no gate refuses a completion percentage lacking a declared denominator** — only `engine/ceu/possessions.py` enforces that, on itself.

## 12.14 Phase 17 — Final classification, and the vocabulary it must use

The directive supplies six tokens. **Five are the repository's own; one is not, and saying so is required by the "no assumption-based closure" rule.**

**The canonical vocabulary is declared, and it is declared for exactly this purpose** — `UCOS-OMEGA-INFINITY-COMPLETE-REQUIREMENT-MASTER-INDEX.md:8`, verbatim:

> "**Status vocabulary, strict, one per requirement:** `CERTIFIED` (implementation + executable evidence + validation passes) · `IMPLEMENTED` (implementation exists, evidence incomplete) · `GOVERNED CLOSURE` (approved decision exists, implementation intentionally pending) · `OPEN GAP` (no implementation, no approved decision)."

This is the **only** place in the repository declaring a status vocabulary as a closed, defined set with per-token semantics and a strict one-per-item cardinality. Its transition rules are real and checked by convention: `REQ-43` moved `OPEN GAP → GOVERNED CLOSURE` pending a `CEP-002 Article 28` decision, with the acceptance criterion *"REQ-43 reads `GOVERNED CLOSURE`, never `CERTIFIED`"* and the reason **"It does not become `CERTIFIED` — nothing was built."** `GOVERNED CLOSURE` currently holds 0 items, "retained in the vocabulary line because it remains a legitimate outcome, not because anything currently holds it."

**`NOT YET ASSESSED` does not exist in this repository** — zero hits across `*.md`, `*.py`, `*.json`. The repository's own words for that concept are `TruthClass.UNCLASSIFIED` (code) · `ABSENT` (a missing optional input) · `UNDECIDABLE` ("recorded as such, never guessed") · `WITHHELD` (deliberately not granted) · `FAULT` (no verdict reachable, distinct from a negative verdict). **This determination uses `NOT YET ASSESSED` as the directive requires, and maps it to those tokens in the companion matrix rather than silently introducing a seventh vocabulary.**

**Six vocabularies coexist by adjudicated decision, not by oversight.** `PHASE-VERDICT-VOCABULARY-TAXONOMY-DETERMINATION.md` surveyed **twelve** certification surfaces and determined option **(C) independent vocabularies with documented relationships**, explicitly rejecting (A) a universal verdict taxonomy authority and (B) a translation layer, on the measured ground that **"No consumer anywhere in the repository was found that reads two different surfaces' verdict values and compares, translates, or reconciles them semantically. Every cross-surface dependency found is a black-box pass/fail boolean at the process-exit-code level."** It notes as convergent design intent that CMG (`READY-PROVISIONAL`), AEE (`CONVERGED-PROVISIONAL`) and UCEF (`CERTIFIED-PROVISIONAL`) independently coined `-PROVISIONAL` for "a pass with a known, named structural caveat." **Do not treat the plurality as a gap — the determination forbids it.**

Code-level verdict tokens that genuinely exist: `CertificationStatus` (`certified`/`not-certified`, independently redefined identically in `engine/certification/contracts.py:76-77`, `engine/universal_certification/contracts.py:82-83`, and as `CertStatus` in `engine/knowledge/certification.py:41-42`) · `Outcome`/`Verdict`/`GateStatus` = `PASS`/`FAIL`, `OPEN`/`CLOSED` (`universal_assurance/contracts.py:120-137`) · `EXIT_OPEN/CLOSED/FAULT` (`infinite_scope/gate.py:31-33`) · `VERDICT_CERTIFIED = "CERTIFIED-UNIVERSAL"` (`context/certification.py:44`, a third spelling) · `Ordering.INCOMPARABLE` · `UNDECIDABLE` (a string constant, not an enum) · `CERTIFIED-PROVISIONAL` (a string literal in 4+ engines). **`GOVERNED CLOSURE` and `OPEN GAP` have zero Python representation** — nothing mechanically prevents a document writing `CERTIFIED` where `GOVERNED CLOSURE` is correct.

## 12.15 Corrections to premises carried into the first pass

Recorded rather than silently fixed, per the no-loss-of-history rule.

| # | Premise | Correction |
|---|---|---|
| 1 | `adr/0021` contains a per-dimension agnosticism table | **It does not.** It is ~4 KB of prose naming three buckets and pointing at the report. The nine-dimension table with a declared rubric lives at `UCOS-ARCHITECTURAL-OPENNESS-ASSESSMENT-REPORT.md:69-79` |
| 2 | `adr/0008` is a settled decision | Its status is **Proposed**, though its suite is implemented and passing |
| 3 | `UFC-16` is defined in a locatable instrument | Its source instrument `UCOS-UFC-001` **is not present in this tree**; only a blockquote of it exists, and no code enforces it |
| 4 | `NOT YET ASSESSED` is available as a status | It appears **nowhere** in the repository |
| 5 | `platform/universal_truth/` types claims | It types **locations** (custody), not claims. `DERIVED TRUTH` has no code representation |
| 6 | Confidence is a graded value | It is an **unvalidated free-form string** with no scale and no persistence owner |
| 7 | A 60-second validation budget is a target to verify | **No second-count target exists**, deliberately; the cost model is explicitly ungated. The solution was five explicit modes, not a cap |

## 12.16 Extension closure

Seventeen phases assimilated. Verdicts unchanged from §2.1 for the fourteen dimensions; the phases added here contribute **no new MISSING findings** and one new `GOVERNED CLOSURE` (learning, per ADR-0011), one thinly-populated region (`Reason · Challenge · Predict · Simulate · Optimize`, §12.12), and seven premise corrections (§12.15). Companion artifacts: `UCOS-OMEGA-INFINITY-ASSIMILATION-COVERAGE-MATRIX.md` (item-level classification) and `UCOS-OMEGA-INFINITY-UNIVERSAL-ASSUMPTION-REGISTER.md` (every located closed enumeration, disclosed closure, and measurement assumption).

**Nothing was modified, deleted, renamed, merged or restructured in this pass. Parts I–XI above are byte-unchanged.**

*END OF PART XII · AUTHORITY = NONE (DERIVED TRUTH).*
