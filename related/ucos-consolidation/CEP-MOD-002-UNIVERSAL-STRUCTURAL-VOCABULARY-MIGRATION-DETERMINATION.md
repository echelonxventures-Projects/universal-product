# CEP-MOD-002 — Universal Structural Vocabulary Migration Determination

**Checkpoint:** `00bd45f` (integration/recovery-001)
**Determination date:** 2026-08-06
**Predecessor:** `UCOS-MOD-001-CONSTITUTIONAL-META-ONTOLOGY-DETERMINATION.md` (D-10)
**Authority:** Repository Truth only.
**Posture:** Design only. No implementation, no code change, no refactoring, no replay regeneration, no generator modification, no runtime modification. **Zero files modified.**

---

## Preamble — Two measured findings that change the migration design

Both were discovered while designing this migration, and both correct the predecessor determination.

### Finding α — The guard that this migration was going to reuse does not exist

`engine/uckp/vocabulary.py:20-25` states that the `Enum` vocabularies in `engine.knowledge.model` are *"a **checked projection**"* of the authoritative vocabularies, and that:

> *"`engine.uckp.assimilation.verify_vocabulary_alignment` **fails closed** if the two ever diverge, so there is one authority and one verified view rather than two competing declarations."*

**`verify_vocabulary_alignment` does not exist.** Repository-wide grep across every `.py` returns exactly one hit — the docstring sentence above. No such function is defined in `engine/uckp/assimilation.py` or anywhere else.

`UCOS-MOD-001` §CEP-MOD-002 asserted this pattern *"already implements and fails closed on."* That was read from the docstring and is **wrong**. The pattern is designated, named, and unbuilt.

### Finding β — The projection has already diverged, and nothing detected it

Measured live at `00bd45f`:

| Vocabulary | Authoritative terms | Enum members | Vocabulary-only | Enum-only |
|---|---|---|---|---|
| `uckp.knowledge-kind` → `KnowledgeKind` | 18 | 17 | **`law`** | — |
| `uckp.authority-tier` → `KnowledgeAuthority` | 4 | 4 | — | — |
| `uckp.lifecycle-stage` → `Lifecycle` | 10 | 10 | — | — |
| `uckp.relation-type` → `RelationType` | 17 | 17 | — | — |

`KNOWLEDGE_KIND_VOCABULARY` declares `law` — *"a supreme, non-derogable rule"* (`vocabulary.py:226`). `KnowledgeKind` has no `LAW` member. The divergence the docstring promised would fail closed is **already present and silent**, because the verifier that would have caught it was never written.

**Consequence for this migration.** The pattern this migration proposes to apply six times is a pattern that has never once been enforced. Phase 2 must therefore *build the verifier before it is relied upon*, and the migration's own first act must be to close the divergence it just discovered. This reorders the plan (§Output 3) and adds one step (`M-0`) that did not appear in `UCOS-MOD-001`.

---

## OUTPUT 1 — Migration Architecture

### 1.1 The single constitutional migration

> **Every downstream engine shall cease to *declare* its structural vocabulary and shall instead *contribute* it to the one Repository Truth Vocabulary Registry, retaining its existing local type as a checked projection guarded by an alignment verifier that fails closed.**

One act. Four steps. Applied identically at every site:

```
DECLARE  →  CONTRIBUTE  →  PROJECT  →  VERIFY
   │            │             │           │
   │            │             │           └─ alignment verifier fails closed on divergence
   │            │             └─ existing Enum/tuple retained, unchanged, as a derived view
   │            └─ registry.register(Vocabulary(...)) at module import
   └─ term set expressed as Vocabulary(term_id, definition, rank, successors)
```

### 1.2 Why this is one migration and not six

Verified by import analysis: **none of the six sites imports any other of the six.** They are mutually independent leaves. What makes them one migration is not coupling — it is that all six exhibit the *identical constitutional defect* and admit the *identical remedy*.

`engine/discovery/contracts.py` already imports `engine.uckp.canonical`, proving Layer Zero is reachable from a downstream engine without a dependency cycle. `engine/uckp/canonical.py:28-33` guarantees this structurally: it *"imports the standard library only — not even the Layer Zero error taxonomy — so that any module in the repository, at any layer, can depend on it without creating a cycle."*

### 1.3 The enabling mechanism already exists — do not invent one

| Required capability | Located owner | Evidence |
|---|---|---|
| Append-only term set | `Vocabulary.extended_with` | `vocabulary.py:111-123` — returns a new vocabulary; refuses redefinition |
| Fail-closed term lookup | `Vocabulary.require` | `vocabulary.py:100-109` — *"openness is register-then-use"* |
| Registry of all vocabularies | `VocabularyRegistry` | `vocabulary.py:140-204` |
| **Contribution from outside the Layer Zero seed** | `_contribute_evolution_stage_vocabulary` | `universe.py:303-325` — **the working precedent.** The evolution layer *"contributes its own vocabulary here"* because it sits below the seed in layer order; identical re-registration is reused, a *different* vocabulary under the same id fails closed |
| Ordering / ranking within a term set | `Term.rank` | Used by `AUTHORITY_TIER_VOCABULARY` (`vocabulary.py:238-247`) |
| Ordered chains with lawful successors | `Term.successors` | Used by `LIFECYCLE_STAGE_VOCABULARY` (`vocabulary.py:249-278`) |
| Source-tree scanning probe | `_probe_zero_duplication` | `validation.py:395-402` — *"it is invisible to any check that only looks at objects — so this probe **reads the source tree**"* |

`_contribute_evolution_stage_vocabulary` is the decisive precedent: it is a module **outside** `build_vocabulary_registry`'s seed contributing a vocabulary into the live registry, with a digest-equality guard. That is exactly what all six sites must do. **The migration adds no mechanism.**

---

## OUTPUT 2 — Dependency Graph

### 2.1 Site-to-site dependencies

```
H-01 discovery/contracts.py ──┐
H-02 ukip/classification.py ──┤
H-03 knowledge/cko.py ────────┼── NO EDGES BETWEEN SITES (verified by import scan)
H-04 civilization/generation ─┤
H-05 graph/architecture/layers┤
H-06 graph/projections.py ────┘
```

**All six are mutually independent.** No site imports another. This is the single most de-risking fact in the migration: ordering is **not** constrained by inter-site dependencies, so sequencing is free and may be chosen purely by risk.

### 2.2 Substrate dependency (what every site depends on)

```
                    engine/uckp/canonical.py          [stdlib only — bottom of order]
                              ↑
                    engine/uckp/errors.py
                              ↑
                    engine/uckp/vocabulary.py         [VocabularyRegistry — THE OWNER]
                              ↑
        ┌──────────┬──────────┼──────────┬──────────┬──────────┐
      H-01       H-02       H-03       H-04       H-05       H-06
```

### 2.3 Consumer blast radius (measured)

| Site | Files referencing | of which tests | Source files | Reaches runtime? |
|---|---|---|---|---|
| H-04 `UniverseStratum` | 1 | 0 | **1** | No |
| H-05 `LAYER_ORDER` | 2 | 0 | 2 | No |
| H-06 `DIAGRAM_NAMES` | 2 | 0 | 2 | No |
| H-02 `ukip.classification` | 6 | 2 | 4 | No |
| H-01 `DiscoveryKind` | 9 | 4 | 5 | No |
| **H-03 `knowledge.cko`** | **31** | 7 | **24** | **Yes** — `engine/runtime/bridge/bridge.py`, `engine/runtime/bridge/contracts.py` |

H-03 is an order of magnitude larger than any other site and is the only one that reaches the runtime bridge. It migrates last.

---

## OUTPUT 3 — Migration Order

Ordering is by **measured blast radius ascending**, because §2.1 proves no dependency constrains it. Each step is independently revertible and independently certifiable.

| Step | Site | Source files | Rationale |
|---|---|---|---|
| **M-0** | **Close the `law` divergence + build the verifier** | 2 | **Prerequisite to every other step.** Finding α/β: the pattern all six will adopt has never been enforced, and is already broken. Nothing may be migrated onto an unenforced pattern |
| M-1 | H-04 `civilization/generation.py` | 1 | Smallest possible pilot. Proves the pattern end-to-end at minimum risk |
| M-2 | H-05 `graph/architecture/layers.py` | 2 | `UNCLASSIFIED` fallback already fails **open** — safest failure mode of the remaining set |
| M-3 | H-06 `graph/projections.py` + `architecture/engine.py` | 2 | `KNOWN_PROJECTION_KINDS` already exists in `projection.py` — partial owner located |
| M-4 | H-02 `ukip/classification.py` | 4 | Depends on `engine.knowledge.model`, stabilised by M-0 |
| M-5 | H-01 `discovery/contracts.py` | 5 | Highest constitutional severity (`coerce()` hard-refuses a future member) but contained blast radius |
| M-6 | H-03 `knowledge/cko.py` | 24 | Largest radius; only runtime-coupled site; **not a term-set problem** (see Output 6, H-03) |

**Rule satisfied:** *no engine migrates before its dependencies.* Every site depends only on `engine/uckp/vocabulary.py`, which is established at M-0 and unchanged thereafter.

---

## OUTPUT 4 — Canonical Owner

Located from Repository Truth. Ownership is **three-layer**, and conflating the layers is what produced the current defect.

| Layer | Owner | What it owns | Evidence |
|---|---|---|---|
| **Admission authority** | `CMG-000001` Articles XIII, XIV, LXXVI | What may be admitted as a Kind, ontology entity, or term, and by what procedure | XIII.2 *"The Kind set IS OPEN… Admission of a Kind IS an **append** operation"*; XIV.7 *"The ontology IS OPEN to new entity types"*; LXXVI.2 admission procedure; LXXVI.3 append-only |
| **Executable registry (THE canonical owner)** | `engine/uckp/vocabulary.py::VocabularyRegistry` | The one live, append-only, digest-bearing store of every admissible term set | `vocabulary.py:140-141` — *"The registry of **every vocabulary** in the Constitutional Knowledge Universe"*; `:159-160` `extend()` is *"the **only** extension mechanism"* |
| **Current structural term content** | `ARCH-001` §2 (`02-MASTER/UCOS-Ω∞-UNIVERSAL-UNIVERSE-CATALOG.md`) | The present `Universe → Domain → Capability → Component` term set | Declares CONSTITUENT / GOVERNANCE / RATIFICATION / EC-1 AUTHORITY = **NONE**; contents *"read-only, provisional, versioned… swappable"* |

**Determination:** the canonical owner of structural vocabulary is **`engine/uckp/vocabulary.py::VocabularyRegistry`**, operating under the admission authority of `CMG-000001` XIII.2 / XIV.7 / LXXVI. `ARCH-001` §2 is the current *content*, not the *owner* — it holds no authority by its own declaration.

Corroborating: `law.py:421-423` states `GOVERNED_CATEGORIES` is *"Open by Article 17: an unknown future category is admitted through `VocabularyRegistry.extend`, **not by editing this tuple**."* Repository Truth names the registry as the admission point in the root law's own comments.

**No new owner is created by this migration.** `UCKP-ART-18` (Reuse Before Create) forbids it, and every capability required has a located owner (Output 1 §1.3).

---

## OUTPUT 5 — Vocabulary Registry Design

No new design. The existing `VocabularyRegistry` is used as-is. What follows is the **registration schedule** — the six term sets expressed in the existing `Vocabulary`/`Term` types.

| Vocabulary id | Terms | Existing `Term` fields used | Contributed by | Replaces |
|---|---|---|---|---|
| `ucos.discovery-dimension` | 8 (`namespace`, `document`, `registry`, `component`, `dependency`, `evidence`, `ontology`, `capability`) | `term_id`, `definition` | `engine.discovery.contracts` | `DiscoveryKind` enum members |
| `ucos.ukip-facet` | 6 (`kind`, `authority`, `lifecycle`, `universe`, `owner`, `version`) | `term_id`, `definition` | `engine.knowledge.ukip.classification` | `Facet` enum members |
| `ucos.civilization-stratum` | 7 (`…Blueprint`, `OperatingSystem`, `Nucleus`, `Universe`, `Capability`, `Component`, `Solution`) | `term_id`, `definition`, **`successors`** (the parent chain) | `engine.civilization.generation` | the literal stratum tuple |
| `ucos.architecture-layer` | 14 (`book`…`security`) | `term_id`, `definition`, **`rank`** (= stack depth) | `engine.graph.architecture.layers` | `LAYER_ORDER` tuple |
| `ucos.projection-kind` | existing `KNOWN_PROJECTION_KINDS` ∪ `DIAGRAM_NAMES` | `term_id`, `definition` | `engine.graph.projections` | `DIAGRAM_NAMES`, `case` labels |
| *(none — see Output 6)* | — | — | — | H-03 is not a term set |

**Every field required already exists.** `rank` is exercised by `AUTHORITY_TIER_VOCABULARY`; `successors` by `LIFECYCLE_STAGE_VOCABULARY`. No extension of `Term` or `Vocabulary` is required — this is the strongest available proof that the migration is REUSE and not EXTEND at the mechanism layer.

**Contribution pattern** (verbatim shape of `universe.py:303-325`): each module registers its vocabulary at import; an identical re-registration is reused; a *different* vocabulary under the same id fails closed.

**The one thing that must be built: the alignment verifier.**

- **Designated name and home:** `engine.uckp.assimilation.verify_vocabulary_alignment` — named by Repository Truth at `vocabulary.py:23`.
- **Disposition: EXTEND, not CREATE.** The owner module exists and already performs vocabulary work (`register_native_vocabularies`, `_register_or_reuse` at `assimilation.py:243-320`); the function is designated but unwritten. Completing a designated-but-unbuilt member of an existing owner is EXTEND under `CMG-000001` LXXVII.2(b). CREATE is unavailable under `UCKP-ART-18`.
- **Contract:** for each (vocabulary, projected type) pair, fail closed if the term sets differ in either direction.
- **First act on being built:** it fails, on `KnowledgeKind` vs `law` (Finding β). That failure is the migration's proof-of-life.

---

## OUTPUT 6 — Engine Impact Matrix

Per-site determination across the twelve dimensions the mission specifies.

### H-01 · `engine/discovery/contracts.py:64-85` — `DiscoveryKind`

| Dimension | Determination |
|---|---|
| Owner | Discovery engine (`engine/discovery/`) |
| Authority | None. A derived engine; `UCKP-ART-04` makes it a view |
| Purpose | The eight dimensions along which the corpus is discovered |
| Dependency | `engine.uckp.canonical` (already), `engine.discovery.errors` |
| **Risk** | **Highest constitutional severity of the six.** `coerce()` **raises** `DiscoveryDimensionError` on any unregistered value — the only site that *hard-refuses* an unknown future member |
| Migration complexity | Low — 5 source files, 4 test files |
| Constitutional impact | Removes a closed vocabulary that contradicts the mechanism of `UCKP-ART-17`/INV-14 |
| Replay impact | **None** — measured (Output 9) |
| Generator impact | **None** — generators do not import discovery |
| Runtime impact | **None** — no runtime consumer |
| Validation impact | Brings 8 previously invisible terms into INV-14's reach |
| Verification impact | `coerce()` behaviour preserved exactly: `Vocabulary.require` also fails closed on an unregistered term |
| Certification impact | Indirect only, via the INV-14 verdict |
| Category (Output 7) | **Vocabulary Registry** |

### H-02 · `engine/knowledge/ukip/classification.py:49-61` — `Facet`

| Dimension | Determination |
|---|---|
| Owner | UKIP classification |
| Authority | None — derived |
| Purpose | The six facets a complete classification decides |
| Dependency | `engine.knowledge.model` (the **already-divergent** projection — Finding β) |
| Risk | Medium — inherits the divergence M-0 must close first |
| Migration complexity | Low — 4 source files |
| Constitutional impact | Same class as H-01 |
| Replay impact | **None** |
| Generator impact | **None** |
| Runtime impact | **None** |
| Validation impact | +6 terms into INV-14 reach |
| Verification impact | `FACETS = tuple(Facet)` becomes `vocabulary.term_ids()` — ordering preserved (both sorted) |
| Certification impact | `ukip/certification.py` consumes classification — must be re-certified after M-4 |
| Category | **Vocabulary Registry** |
| ⚠ Note | Do **not** merge with the existing `uckp.facet` vocabulary. That is a *different* facet set (`engine/uckp/facets.py`). Merging two distinct sets under one id is the ambiguity `universe.py:320-325` fails closed on. Co-register; never merge |

### H-03 · `engine/knowledge/cko.py:157-159` — required `universe` field

| Dimension | Determination |
|---|---|
| Owner | Knowledge CKO model |
| Authority | None — derived |
| Purpose | Every CKO declares the universe it is filed under |
| Dependency | `engine.knowledge.model`, `engine.knowledge.errors` |
| **Risk** | **Highest blast radius: 24 source files + 7 test files; the only site reaching `engine/runtime/bridge/`** |
| Migration complexity | **High** |
| Constitutional impact | `UCKP-ART-06` requires facet *completeness*, not this *specific* required field. A facet *"may be unattested, but it may never be absent"* — the law permits an unattested `universe`, the code does not |
| Replay impact | **Non-zero and unique to this site.** `universe` participates in `_recompute()`, so every CKO content hash embeds it. Changing the field's *requiredness* must not change any existing CKO's serialized value |
| Generator impact | **None** |
| Runtime impact | **Yes** — `engine/runtime/bridge/{bridge,contracts}.py` carry `universe_id` (though in the U-3 runtime-alias sense, not ARCH-001's) |
| Validation impact | Not an INV-14 subject — this is a schema obligation, not a term set |
| Verification impact | Requires a round-trip proof that existing records reconstruct byte-identically |
| Certification impact | Widest of the six; `engine/knowledge/certification.py` is a direct consumer |
| Category | **Repository Truth** (schema/cardinality), **not** Vocabulary Registry |
| **Determination** | **H-03 is not a vocabulary-closure defect and shall not be migrated as one.** It is a required-field cardinality obligation. Its correct remedy is to declare `universe` an *attestable facet* per `UCKP-ART-06`, which is a schema determination requiring its own CEP. **Recommend deferring H-03 out of CEP-MOD-002 entirely** |

### H-04 · `engine/civilization/generation.py:80-115` — stratum chain

| Dimension | Determination |
|---|---|
| Owner | Civilization generation |
| Authority | None — derived |
| Purpose | The generation lineage Blueprint → … → Solution |
| Dependency | `engine.kernel.*`, `engine.civilization.*` |
| Risk | **Lowest — 1 source file, 0 test files** |
| Migration complexity | **Lowest.** Recommended pilot (M-1) |
| Constitutional impact | `UCKP-ART-15` — *"No conclusion rests on a hardcoded assumption"* |
| Replay impact | **None** |
| Generator impact | **None** — this is *civilization* generation, not `platform/universal_generator` (verified: no import path between them) |
| Runtime impact | **None** |
| Validation impact | +7 terms into INV-14 reach |
| Verification impact | Parent chain maps to `Term.successors`, already exercised by `LIFECYCLE_STAGE_VOCABULARY` |
| Certification impact | **None** |
| Category | **Vocabulary Registry** |

### H-05 · `engine/graph/architecture/layers.py:35-60` — `LAYER_ORDER` + `_CATEGORY_LAYER`

| Dimension | Determination |
|---|---|
| Owner | Architecture graph |
| Authority | None — derived; docstring self-declares the mapping *"heuristic but explicit and stable"* |
| Purpose | Classify artifacts into a layer stack; detect inversions and cycles |
| Dependency | `engine.graph.{engine,model}`, `architecture.algorithms` |
| Risk | **Low — `UNCLASSIFIED` fallback already fails open**, so an unknown category degrades rather than refuses |
| Migration complexity | Low — 2 source files |
| Constitutional impact | `AUTH-INF-001` CR-INF-003 — *"All limits MUST be externally configurable"* |
| Replay impact | **None** |
| Generator impact | **None** |
| Runtime impact | **None** |
| Validation impact | +14 layer terms into INV-14 reach |
| Verification impact | Stack depth maps to `Term.rank`; inversion logic reads rank instead of tuple index |
| Certification impact | **None** |
| Category | **Split — Vocabulary Registry** (the 14-layer term set) **+ Configuration** (the `_CATEGORY_LAYER` mapping) |
| ⚠ Note | A mapping is not a term set. `Vocabulary` holds terms, not relations between two term sets. The mapping half belongs to Configuration/Registry and is **outside** this migration's single act |

### H-06 · `engine/graph/projections.py:838`, `architecture/engine.py:67,184-186`

| Dimension | Determination |
|---|---|
| Owner | Graph projection |
| Authority | None — derived |
| Purpose | Dispatch projections and diagram kinds |
| Dependency | `engine.graph.{engine,model,queries}` |
| Risk | Low — 2 source files |
| Migration complexity | Low. **Partial owner already located:** `KNOWN_PROJECTION_KINDS` in `engine/uckp/projection.py` |
| Constitutional impact | `UCKP-ART-15`; INV-07 — behaviour steered from inside the engine by a literal |
| Replay impact | **None** |
| Generator impact | **None** |
| Runtime impact | **None** |
| Validation impact | Brings diagram kinds into INV-14 reach |
| Verification impact | `case "capability":` becomes registry dispatch; `projections.require_covers(KNOWN_PROJECTION_KINDS)` already exists as the coverage guard (`universe.py:351-352`) |
| Certification impact | **None** |
| Category | **Vocabulary Registry** |

---

## OUTPUT 7 — Category Determination + Generator Impact Matrix

### 7.1 Category of every hardcoded occurrence (mission question 2)

| Site | Configuration | Repository Truth | Registry | **Vocabulary Registry** | Generator | Runtime | Validation | Other |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| H-01 DiscoveryKind | | | | **✔** | | | | |
| H-02 UKIP Facet | | | | **✔** | | | | |
| H-03 cko `universe` | | **✔** | | | | | | |
| H-04 stratum chain | | | | **✔** | | | | |
| H-05 LAYER_ORDER | ✔ *(mapping half)* | | | **✔** *(term-set half)* | | | | |
| H-06 projection kinds | | | | **✔** | | | | |

**Determination on mission question 3 — can all six consume a single Vocabulary Registry?**

**No. Five can; one cannot; one is split.** Proven:

- **H-01, H-02, H-04, H-06 — yes, fully.** Each is a flat set of named terms with definitions; each maps onto `Vocabulary`/`Term` with no field extension.
- **H-05 — partially.** Its 14-layer term set maps cleanly (via `Term.rank`). Its `_CATEGORY_LAYER` dict is a **mapping between two term sets**, and `Vocabulary` has no representation for a relation between vocabularies — it holds `terms`, and `Term` holds `successors` only *within* one vocabulary. The mapping half belongs to Configuration.
- **H-03 — no.** It is not a vocabulary at all. `universe` on a CKO is a **required field** — a schema cardinality obligation, not a member of an admissible term set. Forcing it into the Vocabulary Registry would be expansion by reinterpretation, which `CMG-000001` LXXVI.6 forbids: *"Reinterpretation is invisible to validation; admission is visible."*

This is the mission's *"if not, prove why"* — and the proof is that two of the six defects are **misclassified as vocabulary defects in the predecessor determination**. `UCOS-MOD-001` grouped all six under one remedy; that grouping is corrected here.

### 7.2 Generator Impact Matrix

| Generator surface | Impact | Evidence |
|---|---|---|
| `platform/universal_generator/generator.py` | **NONE** | *"a declaration is the only input… never reads the world other than the declaration it was handed"* |
| `platform/universal_generator/{registry,contracts,templates}.py` | **NONE** | Registry/contract-driven; zero structural name literals |
| `platform/universal_generator/catalog/` | **NONE** | Same |
| `05-GENERATION/` framework constitution + 6 family frameworks | **NONE** | Govern by contract |
| `engine/civilization/generation.py` | **Migrated at M-1** | ⚠ Distinct from `platform/universal_generator` — no import path between them |

**Determination: Phase 3 (Generator evolution) is a NO-OP.** Generators were proven vocabulary-agnostic in `UCOS-MOD-001` Output 5 (zero structural name literals across `platform/universal_generator/`), and nothing in this migration changes their inputs. The mission constraint *"no generator modification"* is satisfied **constitutionally**, not merely procedurally — there is nothing in a generator to modify.

---

## OUTPUT 8 — Runtime Impact Matrix

| Runtime surface | Impact | Evidence |
|---|---|---|
| `engine/runtime/composition.py` | **NONE** | `composition_id` is SHA-256 over *"sorted universe fingerprints, coordination class, and federation set"* — derived from fingerprints, never from a term |
| `engine/runtime/graph.py` | **NONE** | `{"universe": u, …}` — `u` is a runtime-unit handle; the key is a serialization label |
| `engine/runtime/assembly.py`, `planner.py`, `context.py` | **NONE** | No structural vocabulary literal |
| `engine/uckp/execution.py` | **NONE** | `UCKP-ART-10` — *"Execution never owns knowledge"* |
| **`engine/runtime/bridge/{bridge,contracts}.py`** | **Deferred with H-03** | Carries `universe_id: str`; consumes `engine.knowledge.cko`. The only runtime coupling in the entire migration — and it belongs to the site being deferred out of scope |

**Determination: Phase 5 (Runtime evolution) is a NO-OP for M-0…M-5.** The sole runtime coupling is via H-03, which §Output 6 defers. With H-03 out of scope, the mission constraint *"no runtime modification"* is satisfied with zero residual risk.

---

## OUTPUT 9 — Replay Impact

### 9.1 The measurement

Executed live at `00bd45f` against a fully built universe (170 objects). An unknown future term was admitted into a live vocabulary, and every replay-bearing digest was compared before and after:

| Digest | Before → After | Changed? |
|---|---|---|
| `law.digest()` | `d4f7a8bd9da0ce38…` | **No** |
| `vocabularies().digest()` | `976859cc709ad51d…` → `f66c4fb74dd1ce32…` | **Yes** |
| `knowledge_digest()` | — | **No** |
| `registry.seal()` | — | **No** |
| **`universe.fingerprint()`** | — | **No** |

### 9.2 Determination

> **Replay remains deterministic. Vocabulary extension is replay-neutral.**

**How** — structurally, from `universe.py:128-138`. `fingerprint()` is a content hash over exactly five inputs: `law`, `knowledge`, `graph`, `timeline`, `evolution`. **The vocabulary registry digest is not among them.** Registering a term therefore cannot perturb the universe fingerprint, and `ConstitutionalState` (`state.py:145,151`) binds `knowledge_digest` and `replay_proof` — neither of which is vocabulary-derived.

**Three consequences:**

1. **No replay proof requires regeneration.** Every prior replay proof remains valid byte-for-byte across the entire migration. The mission constraint *"no replay regeneration"* is satisfied **by construction**, not by care.
2. **The extension is nonetheless auditable.** The vocabulary digest *does* change, so which vocabulary state was in force at any point is provable — satisfying `UCKP-ART-17` (auditability) without disturbing `UCKP-ART-13` (determinism). Openness and determinism are carried on separate digests, which is precisely why both hold.
3. **One site is exempt from this guarantee.** H-03's `universe` field participates in `CanonicalKnowledgeObject._recompute()`, so it *is* inside the knowledge digest. This is independent grounds — beyond blast radius — for deferring H-03 out of this migration.

---

## OUTPUT 10 — Certification Impact

| Layer | Impact | Evidence |
|---|---|---|
| `engine/uckp/validation.py` — 17 invariant probes | **INV-14's reach widens** | `_probe_infinite_extensibility` iterates `vocabularies.vocabulary_ids()`. Today the six closed vocabularies are **outside that loop**, so INV-14 reports green while six closed vocabularies exist. Registration brings them inside |
| INV-03 `_probe_zero_duplication` | **Precedent, unchanged** | Already *"reads the source tree"* — the located pattern a vocabulary-closure scan would extend |
| INV-07 `_probe_zero_hardcoded_knowledge` | **Unchanged** | Checks UCKO provenance only; does not scan source. Not widened by this migration |
| `engine/certification/contracts.py` | **Indirect** | `CertificationSubject` binds `validation_verdict`, `checks_run`, `blocking_failures` — vocabulary is not bound directly |
| `engine/universal_certification/` | **Indirect** | Same |
| Existing certification records | **Remain valid** | Bind `target_id`/`blueprint_id`/`version`/verdict — none vocabulary-derived |

### The measurement blind spot — the finding that justifies the whole migration

`_probe_infinite_extensibility` (`validation.py:746-771`) proves INV-14 *"by actually admitting one"* — a genuine executable proof. But it proves it **only over vocabularies registered in the `VocabularyRegistry`.**

The six downstream engines' closed vocabularies are not registered. They are therefore **invisible to the invariant that exists to detect exactly this defect.** INV-14 currently returns satisfied while six vocabularies in the same repository hard-refuse an unknown future member — one of them (`DiscoveryKind.coerce`) by raising.

**This is the constitutional justification for CEP-MOD-002.** The migration's real product is not tidier code; it is **bringing six closed vocabularies inside the reach of the invariant that measures closure.** After migration, INV-14 measures what it was written to measure. Before migration, it measures a subset and reports on the whole.

**Certification determination:** no certification record is invalidated; certification *coverage* increases. Re-certification is required only for H-02 (via `ukip/certification.py`), and — were it in scope — H-03 (via `knowledge/certification.py`).

---

## OUTPUT 11 — Implementation Plan

**Phases 1–6 are design/enablement. Phase 7 is the only phase that touches an engine, and nothing in it is authorised by this determination.**

| Phase | Act | Scope | Constraint honoured |
|---|---|---|---|
| **1 · Repository Truth evolution** | Declare the five migratable term sets as data (Output 5 schedule). Record `ARCH-001` §2's status per CEP-MOD-001 | No code | Additive; renames nothing (`CMG` LXXVI.3) |
| **2 · Vocabulary Registry evolution** | (a) Build `verify_vocabulary_alignment`; (b) close the `law` divergence; (c) register the five vocabularies via the `_contribute_evolution_stage_vocabulary` pattern | `engine/uckp/` only | No mechanism invented — all reused |
| **3 · Generator evolution** | **NO-OP** | — | *"no generator modification"* — nothing to modify |
| **4 · Validation evolution** | Widen INV-14's reach to the contributed vocabularies; optionally extend the INV-03 source-scan pattern to detect closed vocabularies in source | `engine/uckp/validation.py` | Probe added to an existing suite; no invariant redeclared (`law.py` remains sole declarant) |
| **5 · Runtime evolution** | **NO-OP** (sole coupling is H-03, deferred) | — | *"no runtime modification"* |
| **6 · Certification evolution** | Re-certify H-02's consumer. Record that INV-14 coverage widened | `ukip/certification.py` | No record invalidated |
| **7 · Implementation** | M-0 → M-1 → M-2 → M-3 → M-4 → M-5. **H-03 excluded** | Six sites, ~14 source files | Each step independently revertible |

### Backward compatibility (mission question 8)

> **Yes. Old and new Repository Truth coexist, by construction.**

Three independent mechanisms:

1. **Append-only extension.** `Vocabulary.extended_with` (`vocabulary.py:111-123`) returns a new vocabulary and **refuses redefinition** — *"a term whose meaning can change retroactively invalidates every digest computed under the old meaning."* No existing term can be altered, so no existing consumer can break.
2. **The projection is retained.** Every enum and tuple stays in place as a derived view. No caller moves, no import changes. This is the pattern `canonical.py:15-19` already used when nine modules were consolidated: *"their public names are unchanged, so no consumer had to move."*
3. **Replay-neutrality.** Output 9 — the universe fingerprint does not move, so old proofs and new state coexist without reconciliation.

### Rollback (mission question 9)

> **Partially. Consumption is reversible; registration is not — and that is correct, not a defect.**

| What | Reversible? | Why |
|---|---|---|
| Code that *consumes* the registry | **Yes** — fully | Each step touches 1–5 source files; the enum remains throughout, so reverting restores the prior path exactly |
| The *registration* of a term | **No** | `VocabularyRegistry` exposes `register`, `extend`, `get`, `require`, `require_term`, `vocabulary_ids`, `is_extensible`, `to_document`, `digest` — **and no removal operation** |

The absence of removal is **deliberate and constitutional**, not an oversight: `UCKP-ART-14` — *"It appends; it never rewrites; it never terminates"* — and INV-13 (append-only evolution, no terminal stage).

**Practical rollback semantics:** revert the consuming code; the registered term remains as an unused, harmless member. Since `require()` is only reached for terms a caller actually asks for, an unconsumed term is inert. **Rollback restores behaviour without restoring the closed vocabulary** — which is the correct outcome, because the closure was the defect.

---

## OUTPUT 12 — Final Constitutional Determination

### 12.1 The single migration

> Every downstream engine shall **contribute** its structural vocabulary to `engine/uckp/vocabulary.py::VocabularyRegistry` and **retain** its existing local type as a checked projection guarded by `verify_vocabulary_alignment`, which shall fail closed.
>
> **Five sites follow it. One (H-05) follows it partially. One (H-03) is not a vocabulary defect and is excluded.**

### 12.2 Disposition matrix — every migration step

| Step | Act | Disposition | Authority |
|---|---|---|---|
| M-0a | Build `verify_vocabulary_alignment` | **EXTEND** | Designated by Repository Truth at `vocabulary.py:23`; owner module exists and already registers vocabularies. CREATE unavailable under `UCKP-ART-18` |
| M-0b | Close the `law` divergence in `KnowledgeKind` | **EXTEND** | Append a member to a projection to match its declared authority. `CMG` LXXVI.3 — append-only, renames nothing |
| M-1…M-5 | Contribute five vocabularies | **REUSE** | Mechanism exists entire (Output 1 §1.3); precedent is `universe.py:303-325` |
| Phase 3 Generator | — | **PASS** | Proven vocabulary-agnostic; nothing to do |
| Phase 5 Runtime | — | **PASS** | Sole coupling deferred with H-03 |
| Replay handling | — | **PASS** | Measured neutral (Output 9); no act required |
| Backward compatibility | — | **PASS** | Guaranteed by append-only + retained projection |
| INV-14 reach widening | **EXTEND** | Widens an existing probe; declares no new invariant |
| H-05 `_CATEGORY_LAYER` mapping | **CEP** | A mapping between term sets has no representation in `Vocabulary`; requires its own determination |
| **H-03 `universe` required field** | **CEP — separate proposal** | Schema cardinality, not vocabulary. Forcing it here would be reinterpretation, forbidden by `CMG` LXXVI.6 |
| Any new vocabulary mechanism | **CREATE — UNAVAILABLE** | `UCKP-ART-18`; every capability has a located owner |

**CREATE count: 0.**

### 12.3 Findings that must be carried forward

1. **`verify_vocabulary_alignment` does not exist.** The pattern this migration applies six times has never been enforced once. It must be built before it is relied upon — hence M-0 precedes every site.
2. **The projection has already diverged** (`KnowledgeKind` lacks `law`), silently, for exactly the reason the docstring predicted. This is not a hypothetical risk; it is a measured live defect.
3. **INV-14 has a measurement blind spot.** It reports green while six closed vocabularies sit outside its loop. This is the migration's true justification.
4. **H-03 was misclassified** by `UCOS-MOD-001` as a vocabulary defect. It is a schema obligation and is excluded here.
5. **All six sites are mutually independent** — ordering is free, so sequencing was chosen purely by measured blast radius.
6. **Replay is provably unaffected** — measured, not argued.

### 12.4 Readiness

| Gate | Verdict |
|---|---|
| Canonical owner located | **PASS** — `VocabularyRegistry`, under `CMG-000001` XIII.2/XIV.7/LXXVI |
| Mechanism exists without invention | **PASS** — every required field and pattern located |
| Migration order satisfies dependencies | **PASS** — no inter-site edges; order by blast radius |
| Replay determinism preserved | **PASS** — measured |
| Backward compatibility | **PASS** — append-only + retained projection |
| Rollback | **PARTIAL** — consumption reversible; registration append-only by law |
| Generator untouched | **PASS** |
| Runtime untouched | **PASS** (with H-03 excluded) |
| Certification preserved | **PASS** — coverage widens; no record invalidated |
| **Blocking prerequisite** | **M-0 — the alignment verifier must exist and the `law` divergence must close before any site migrates** |

**IMPLEMENTATION READINESS: READY, BLOCKED ON M-0.**

---

**Files modified: none. Code changed: none. Engines edited: none. Vocabulary replaced: none. Replay regenerated: none.**

Repository Truth artifacts cited: 14. Source files inspected: 21. Live measurements executed: 3 (projection alignment, vocabulary extensibility, replay sensitivity).

This determination is recorded at commit `00bd45f`. Nothing herein is enacted. Phase 7 requires ratification; M-0 requires ratification before M-1.

---

*End of CEP-MOD-002-UNIVERSAL-STRUCTURAL-VOCABULARY-MIGRATION-DETERMINATION.md*
