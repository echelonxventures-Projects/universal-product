# UCOS-MOD-001 — Constitutional Meta-Ontology Determination

**Checkpoint:** `00bd45f` (integration/recovery-001)
**Determination date:** 2026-08-06
**Authority:** Repository Truth only. Every conclusion cites a Repository Truth artifact.
**Posture:** Determination only. No redesign, refactoring, implementation, renaming, or migration. No artifact was modified.

---

## Preamble — Three findings that govern every conclusion below

**Finding A — The artifact that defines the structural vocabulary declares itself to hold no authority.**

`02-MASTER/UCOS-Ω∞-UNIVERSAL-UNIVERSE-CATALOG.md` (PROGRAM ID `ARCH-001`) is the canonical home of `Universe → Domain → Capability → Component`. Its own header states:

| Field | Value |
|---|---|
| CLASSIFICATION | Foundational Architecture Artifact — **Canonical Inventory** |
| CONSTITUENT AUTHORITY | **NONE** |
| GOVERNANCE AUTHORITY | **NONE** |
| RATIFICATION AUTHORITY | **NONE** |

and its preamble: *"This artifact is an architectural **inventory instrument only**… it **ratifies nothing and confers no authority** on any universe, domain, or actor,"* with all embedded constitutional positions consumed as *"read-only, **provisional**, versioned… and swappable pending EC-1…EC-6."*

An instrument that declares AUTHORITY = NONE and its own contents provisional cannot be the source of a permanent constitutional ontology. This single finding is dispositive.

**Finding B — Three of the four terms have no standing in the executable root law at all.**

`engine/uckp/law.py:424-460` declares `GOVERNED_CATEGORIES` — the categories that Article 2 requires to exist as canonical objects. It contains `capability`, `ontology`, `taxonomy`, `concept`, `relationship`, `registry`, `engine`, `runtime`. It does **not** contain `universe`, `domain`, or `component`. Only `capability` of the four structural terms is a governed category.

**Finding C — Correction to a prior determination.** `UMN-001:265` records ARCH-001 as *"missing from disk."* It is present, at `02-MASTER/UCOS-Ω∞-UNIVERSAL-UNIVERSE-CATALOG.md` (36,166 bytes, 2026-07-21), carrying `PROGRAM ID | ARCH-001`. The vocabulary UMN-001 relied on is physically resident and readable; its §2 table is quoted throughout this determination. This correction strengthens, not weakens, UMN-001's REUSE/EXTEND conclusion — the owner exists.

---

## OUTPUT 1 — Evidence Matrix

| # | Question | Repository Truth evidence | Finding |
|---|---|---|---|
| E-01 | Does any law state Universe/Domain/Capability/Component are permanently immutable? | Exhaustive grep for `(vocabular\|terminolog\|term).* (is\|are\|shall be) (permanent\|immutable\|frozen\|fixed)` across all `.md`/`.py` | **No such clause exists.** Three hits returned, none about structural vocabulary |
| E-02 | What is the owner of the four terms? | `ARCH-001` §2 "Universe Taxonomy Framework" — the eight-row term table + composition chain | ARCH-001 §2, declared AUTHORITY = NONE, provisional |
| E-03 | Standing of the four terms in the root law | `engine/uckp/law.py:424-460` `GOVERNED_CATEGORIES` (35 members) | `capability` governed; `universe`, `domain`, `component` **absent** |
| E-04 | Standing of `Universe` in the meta-constitution | `CMG-000001` XIII.5 | Recognized as Kind `CMG-K-12`; *"their models are **owned elsewhere and consumed by reference**. This Article SHALL NOT restate them"* |
| E-05 | Is the Kind set closed? | `CMG-000001` XIII.2 | *"The Kind set **IS OPEN**… A new Kind SHALL be admitted under Article LXXVI and SHALL NOT require amendment of any existing Kind. Admission of a Kind IS an **append** operation."* |
| E-06 | Is the ontology closed? | `CMG-000001` XIV.7 | *"The ontology **IS OPEN** to new entity types under Article LXXVI, and a new entity type SHALL NOT alter the cardinality of any existing relation."* |
| E-07 | Are `Domain` and `Universe` themselves admissible as new members? | `CMG-000001` LXXVI.1 | Explicitly enumerated: the corpus *"SHALL be capable of admitting, **without structural amendment**… a new… **Domain**, **Universe**, Federation, Repository, Intelligence, and Constitutional artifact"* |
| E-08 | Is expansion bounded in count? | `CMG-000001` LXXVI.5 | *"Expansion SHALL be **unbounded in count**… any apparent limit SHALL be read as a **defect** and recorded as a finiteness risk"* |
| E-09 | May vocabulary evolve by renaming? | `CMG-000001` LXXVI.3, LXXVI.6; `CEP-009` B.7.2 | **No.** Admission is append-only; it *"SHALL NOT renumber, rename, reclassify, or invalidate any existing member."* Reinterpretation is forbidden (LXXVI.6) |
| E-10 | Does the repository forbid closed structural models? | `AUTH-INF-001` Part I.2 | SHALL remove all interpretations implying *"Closed Registries, Closed Universes, Closed Programs, **Closed Domains**, or **Closed Capability Models**"* |
| E-11 | How is "closed"/"final" to be read? | `AUTH-INF-001` CR-INF-001.2-.3 | *"Certification closes scope. Certification **never** closes evolution."* `"final", "complete", "closed", "terminal"` SHALL be read as *complete for current scope*, never *incapable of future extension* |
| E-12 | Is hard-coding of vocabulary permitted? | `AUTH-INF-001` CR-INF-003.1-.2 | No hard maximum *"unless imposed by physical reality"*; *"All limits MUST be externally configurable"* |
| E-13 | Is future extensibility asserted or proved? | `engine/uckp/law.py:174-178` INV-14; `engine/uckp/vocabulary.py:181-193` `is_extensible()` | **Proved.** A probe term `uckp.future-probe` is admitted into a copy of every vocabulary; refusal fails INV-14 |
| E-14 | Does a law forbid foundational redesign on new concepts? | `CEP-009` Addendum B, B.2.1-.3 | *"The constitutional foundation SHALL NOT require redesign for the introduction of any future constitutional construct."* Apparent need for redesign is *"a **defect of the introduction**, not of the foundation"* |
| E-15 | Counter-evidence: closed root sets | `PLATFORM-003` POI-01; `DATA-003` DOI-01; `SERVICE-003` SOI-01; `APPLICATION-003` AOI-01; `RUNTIME-003` ROP-01/ROL-01 | Five **scale-local** closure clauses ("no ninth root", "no eleventh root", eleven runtime concepts) — see Output 8 §8.3 |
| E-16 | Is that asymmetry already on the record? | `UCOS-ACFV-000001` §3 W-5 and W-1 | **Yes.** W-5 records non-uniform root cardinality as *"an asymmetry the self-similarity principle does not explain."* W-1 records that only `PLATFORM-005` PME-01 carries a growth clause |
| E-17 | Does `Universe` mean one thing repository-wide? | `ARCH-001` §2 vs `engine/uckp/universe.py:1-23` vs `engine/runtime/composition.py:1-8` | **No — three distinct senses.** See Output 8 §8.2 |
| E-18 | Is there a Kind for terminology ownership? | `CMG-000001` XIII.1 `CMG-K-23` **Glossary** — *"The canonical terminology of a corpus"* | Kind exists; the only instance found is `00-MASTER/UAKOS-CLOSURE-006/CONST-11-CONSTITUTIONAL-GLOSSARY.md` (program-scoped, not repository-wide) |
| E-19 | Unreconciled universe relations | `UCOS-ACFV-000001` §3 W-4 | `LAW P4-002`/`MCP-001:34` "no universe owns another" vs `LAW USIS-09` "a universe may contain universes" — *"no instrument states the reconciliation normatively"* |

---

## OUTPUT 2 — Current Canonical Vocabulary

The structural vocabulary as Repository Truth presently declares it. Source: `ARCH-001` §2, verbatim.

| Term | ARCH-001 §2 definition | Relationship | Catalog |
|---|---|---|---|
| **Universe** | Top-level architectural container for a coherent reality domain | Root container; composed of Domains | ARCH-001 (112 registered) |
| **Domain** | A bounded subject area within a Universe with its own concepts, rules, and vocabulary | Belongs to exactly one Universe | ARCH-002 |
| **Capability** | A discrete functional ability the platform must provide within a Domain | Realized by Components | ARCH-003 |
| **Component** | A concrete, deployable/reusable technical unit implementing one or more Capabilities | Composed into Services/Applications | ARCH-004 |
| **Application** | A user- or agent-facing product assembled from Components and Services | Delivers Capabilities to actors | ARCH-008 |
| **Platform** | Cross-cutting Services/Components serving many Universes | **Horizontal** | — |
| **Service** | A running, network-addressable unit exposing Capabilities via contracts | Runtime realization of Components | ARCH-006 |
| **Registry** | Authoritative versioned store that **records — never ratifies** | Backbone of traceability | IMP-004 |

**Composition chain (ARCH-001 §2):** `Universe → Domain → Capability → Component → {Service, Application}`, Platform and Registry horizontal.

**Status of this vocabulary:** ACTIVE · **PROVISIONAL** · versioned · swappable · AUTHORITY = NONE (ARCH-001 header + preamble).

**Corroborating restatements** (all derived, none authoritative): `00-CEP/STAGE-02-S2-03:37`; `adr/0002:31`; `03-CATALOGS/…RUNTIME-CATALOG-CONSTITUTION:48`; `03-CATALOGS/…WORKFLOW-CATALOG:49`; `07-ENGINEERING/…IDENTITY-SYSTEM:117`; `00-MASTER/RA-002/02:18`. Per `UCKP-ART-11` these are generated views and hold no truth.

---

## OUTPUT 3 — Permanent Constitutional Ontology

What Repository Truth **does** legislate as permanent. This set is disjoint from Output 2.

### 3.1 The supremacy clause — `engine/uckp/law.py:41-46`

> *"Every constitutional entity shall exist exactly once as a canonical Universal Constitutional Knowledge Object. Every representation, execution environment and persistence mechanism of that entity is a **view** of it and holds **no independent architectural authority**."*

### 3.2 The permanent primitives

| Permanent concept | Authority | Why permanent |
|---|---|---|
| Canonical object (UCKO) — exists exactly once | `UCKP-ART-02`, INV-01/03 | Existence rule, not a name |
| Identity — globally unique, immutable, technology-independent | `UCKP-ART-05` | *"An identity, once minted, never changes"* |
| Facet — every object answers every universal question | `UCKP-ART-06`, INV-04 | *"an absent facet is an unanswerable question"* |
| Relationship — executable edge | `UCKP-ART-07`, INV-04/05/06 | *"a relationship that cannot be resolved is not a relationship"* |
| Authority chain — single parent, acyclic, terminating at root law | `UCKP-ART-01`, INV-02/06 | Structural, name-free |
| Non-authority of representations | `UCKP-ART-04`, INV-08/10 | Binds *"every future technology"* |
| Determinism / canonical form | `UCKP-ART-13` | *"identical inputs always produce identical bytes"* |
| Immutable append-only state | `UCKP-ART-12`, INV-15 | *"No previous state ever changes"* |
| Registration-not-amendment | `UCKP-ART-17`, INV-14 | *"an unknown future category is admitted by **registration, never by amendment**"* |
| Reuse before create | `UCKP-ART-18` | *"It is never duplicated and never given a rival"* |
| Perpetual validity | `UCKP-ART-20` | Valid *"across future languages, storage media, execution models, intelligences, planetary locations and civilizations"* |

### 3.3 The decisive structural property

`UCKP-ART-20` binds the law to remain valid across *future civilizations*. A law that named `Universe`, `Domain`, and `Component` as permanent could not satisfy that clause, because it would presume those four words survive every future civilization. The root law instead legislates **contracts** (identity, facet, relationship, authority chain, determinism) and leaves the **term set open** by Article 17. The permanence is in the shape, never in the noun.

**Determination:** The Permanent Constitutional Ontology consists of object-existence, identity, facet, relationship, authority, determinism, immutability, and open registration. `Universe`, `Domain`, `Capability`, `Component` are **not** members of it.

---

## OUTPUT 4 — Engine Dependency Matrix

Method: literal-string and enum scan across `engine/`, `platform/`, `service/`, `application/`, `data/`, `infrastructure/`, `intelligence/`, `realization/` (295 structural-name literals in non-test source).

### 4.1 Engines that depend on NAMES (hardcoded structural vocabulary)

| # | Location | Hardcoded construct | Owner | Impact | Constitutional authority | Migration path (not executed) |
|---|---|---|---|---|---|---|
| **H-01** | `engine/discovery/contracts.py:64-71` | `class DiscoveryKind(str, Enum)` — `COMPONENT`, `CAPABILITY`, `ONTOLOGY`, `REGISTRY`, `NAMESPACE`, `DOCUMENT`, `DEPENDENCY`, `EVIDENCE`. `coerce()` (`:73-85`) **raises** on any unregistered value | Discovery engine | A new discovery dimension is a **code edit** — i.e. an amendment | Violates the mechanism of `UCKP-ART-17`/INV-14 | Reuse `VocabularyRegistry` (`engine/uckp/vocabulary.py:140`); keep the enum as a **checked projection** exactly as `KnowledgeKind` already is |
| **H-02** | `engine/knowledge/ukip/classification.py:49-57` | `class Facet(str, Enum)` with fixed member `UNIVERSE = "universe"`; `FACETS = tuple(Facet)` | UKIP classification | The six-facet set is closed in code | Same as H-01 | Same as H-01 |
| **H-03** | `engine/knowledge/cko.py:157-159` | `universe` is a **required** field: `_require(record, "universe", at=cko_id)` — a CKO cannot be constructed without one | Knowledge CKO model | Every canonical object is forced to declare a `universe`, making the term structurally load-bearing | `UCKP-ART-06` requires facet *completeness*, not this specific facet | Declare `universe` a facet **term** in the facet vocabulary rather than a required constructor field |
| **H-04** | `engine/civilization/generation.py:80-115` | Hardcoded stratum tuple: `NucleusStratum → UniverseStratum("Universe") → CapabilityStratum("Capability") → ComponentStratum("Component") → SolutionStratum`, each with a literal parent | Civilization generation | The generation lineage **is** the four names, in a fixed chain | `UCKP-ART-15` — *"No conclusion rests on a hardcoded assumption"* | Drive strata from a declared stratum registry |
| **H-05** | `engine/graph/architecture/layers.py:35-60` | `LAYER_ORDER` — a fixed 14-tuple (`book`…`security`) plus `_CATEGORY_LAYER` dict. Docstring self-declares the mapping *"heuristic but explicit"*; unknown categories fall to `UNCLASSIFIED` | Architecture graph | Layer inversion/cycle findings are computed against a hardcoded stack | `AUTH-INF-001` CR-INF-003 (zero hard coding) | Externalize `LAYER_ORDER` to a declaration; the `UNCLASSIFIED` fallback already fails **open**, which is the safer half |
| **H-06** | `engine/graph/projections.py:838`; `engine/graph/architecture/engine.py:67,184-186` | Control flow branching on the literal: `case "capability":`, `DIAGRAM_NAMES = ("layer", "capability", "condensation")` | Graph projection | Behaviour is steered from inside the engine by a structural name | `UCKP-ART-15`; INV-07 | Dispatch on a registered projection kind |

### 4.2 Engines that depend on DECLARATIONS (compliant)

| Location | Mechanism | Evidence |
|---|---|---|
| `engine/uckp/vocabulary.py:1-26` | Vocabularies held as **data with an append-only registry**, explicitly *because* *"a vocabulary frozen into a Python `Enum`… becomes a code edit, and a code edit in Layer Zero is a constitutional amendment"* | The reference implementation |
| `engine/uckp/vocabulary.py:100-127` | `require()` fails closed on unregistered terms; `extended_with()` returns a **new** vocabulary and refuses redefinition | Openness is *"register then use"*, not *"anything goes"* |
| `engine/uckp/vocabulary.py:181-193` | `is_extensible()` **proves** INV-14 by admitting a probe term to every vocabulary | Extensibility measured, not asserted |
| `engine/uckp/universe.py:10-16` | `build_universe()` contains **no list of objects**; it calls `registry.discover()` and admits whatever any provider module offers — *"Adding a new family of constitutional objects therefore means adding a provider module — never editing this one"* | `UCKP-ART-08` |
| `engine/uckp/assimilation.py` | `verify_vocabulary_alignment()` **fails closed** if the `Enum` projections in `engine.knowledge.model` ever diverge from the authoritative vocabularies | One authority, one verified view |

### 4.3 Engine determination

The engine is **split**. Layer Zero (`engine/uckp/`) depends on **declarations** and is the constitutionally correct pattern — it diagnoses this exact hazard in its own docstring and proves its openness with an executable probe. Six engines outside Layer Zero (H-01…H-06) depend on **names**, and in each case the vocabulary is closed by a Python `Enum`, a literal tuple, a required field, or a `case` label. No engine was modified.

---

## OUTPUT 5 — Generator Dependency Matrix

| Generator | Depends on | Evidence | Verdict |
|---|---|---|---|
| `platform/universal_generator/generator.py` | **Declarations** | Module docstring: *"**a declaration is the only input**. The generator never reads… the world other than the declaration it was handed and the targets and templates it was composed with"* | Contract-driven |
| `platform/universal_generator/generator.py:47-76` | **Declarations** | `destination_tokens()` — *"Each token is derived from something the declaration already says, which is what keeps destinations **free of repository knowledge**"*; an unanswerable token *"is a refusal, never a guess"* | Fails closed, no name coupling |
| `platform/universal_generator/registry.py` | **Registries** | `TargetRegister` + `TemplateRegistry` injected via `build_generator()`; `unbound_targets()` reports gaps | Registry-driven |
| `platform/universal_generator/contracts.py:289-301` | **Contracts** | `GENERATION_CONTRACTS` / `generation_contract_names()` | Contract-driven |
| `05-GENERATION/UCOS-Ω∞-UNIVERSAL-GENERATION-FRAMEWORK-CONSTITUTION.md` + 6 family frameworks | Contracts + relationships | Generation constitution governs by contract | Contract-driven |

**Scan result:** grep for `"universe"|"domain"|"capability"|"component"` string literals across `platform/universal_generator/` and `platform/generation/` returns **zero non-test hits**.

**Determination:** Generators depend on **contracts, registries, and relationships — never on names.** They are already vocabulary-agnostic and require no change under any vocabulary evolution.

---

## OUTPUT 6 — Runtime Dependency Matrix

| Runtime surface | Depends on | Evidence |
|---|---|---|
| `engine/runtime/composition.py:1-8` | **Declarations** | The word "Universe" is an explicit **local alias**: the `RuntimeUnit` from `assemble()` is *"**here called** a Universe"* — a naming convenience for an already-assembled unit, not the ARCH-001 Universe |
| `engine/runtime/composition.py:29-33` | **Declarations** | `composition_id` is a SHA-256 over *"the sorted universe fingerprints, coordination class, and federation set"* — identity is derived from **fingerprints**, never from a term |
| `engine/runtime/graph.py:201` | **Declarations** | `{"universe": u, "depends_on": d}` — `u` is a runtime-unit handle; the key is a serialization label |
| `engine/uckp/execution.py` | **Contracts** | `UCKP-ART-10` — *"Every execution technology satisfies one identical constitutional contract. Execution never owns knowledge"* |
| INV-09 / INV-12 | **Contracts** | Two or more execution technologies and runtime bindings satisfy the identical contract; *"no object binds to exactly one runtime"* |

**Determination:** Runtime depends **only on Repository Truth declarations** — fingerprints, contracts, and bindings. It does **not** depend on `Universe`, `Capability`, or `Component` as structural concepts. The single occurrence of "Universe" in the runtime is a documented local alias for `RuntimeUnit` and carries no coupling to ARCH-001.

⚠ **Homonym hazard (non-blocking, recorded):** `Universe` denotes three unrelated things in Repository Truth — see Output 8 §8.2.

---

## OUTPUT 7 — Repository Truth Dependency Matrix

| Constitutional artifact | Does it constrain vocabulary evolution? | Evidence |
|---|---|---|
| `engine/uckp/law.py` (ROOT_LAW, `UCKP-LAW-0001`) | **No — it mandates openness** | ART-17/INV-14; `GOVERNED_CATEGORIES` declared *"open by Article 17"* at `:421-423`, extended via `VocabularyRegistry.extend`, *"not by editing this tuple"* |
| `CMG-000001` (Meta-Governance Constitution) | **No — it legislates admission** | XIII.2 Kind set OPEN; XIV.7 ontology OPEN; LXXVI.1 names Domain and Universe as admissible without structural amendment; LXXVI.5 unbounded in count |
| `CMG-000001` LXXVII (Unknown Future Concepts) | **No — it is total by construction** | LXXVII.1 governs *"concepts that do not yet exist and cannot presently be named"*; LXXVII.3 the five outcomes *"ARE exhaustive by construction"*; LXXVII.6 *"SHALL NOT assume that future concepts will be expressible in its present ontology"* |
| `CEP-009` + Addendum B (Evolution Constitution) | **No — it forbids redesign** | B.2.1 foundation *"SHALL NOT require redesign for the introduction of any future constitutional construct"*; B.2.2 evolution occurs by registration/integration/governance/validation/certification/traceability, *"NEVER… architectural replacement of the foundation"* |
| `AUTH-INF-001` (Unbounded Expansion Constitution) | **No — it forbids closure** | Part I.2 removes interpretations implying Closed Domains / Closed Capability Models; CR-INF-002 numbers are sequence not limit; CR-INF-003 zero hard coding |
| `ARCH-001` §2 (the vocabulary itself) | **No — it holds no authority** | AUTHORITY = NONE ×4; *"provisional… swappable"* |
| `PLATFORM-003` POI-01 | **Locally yes** — "no ninth root" over the 8 **platform** roots | Neither `Universe` nor `Domain` is a platform root; the 8 are Platform/Capability/Component/Service/Experience/Composition/Integration/Governance |
| `DATA-003` DOI-01 · `SERVICE-003` SOI-01 · `APPLICATION-003` AOI-01 | **Locally yes** — "no eleventh root" per family | Each closes only its own 10-concept family set |
| `RUNTIME-003` ROP-01/ROL-01 | **Locally yes** — 11 runtime concepts | *"Runtime Universe Closure"* — scoped to runtime |
| `DATA-015` · `APPLICATION-015` (freeze determinations) | **Constrains modification, not extension** | *"no artifact in DF-1/AF-1 may be modified in place… **extension is additive-only**"* |

**Determination:** **No constitutional artifact prevents Repository Truth from evolving its architectural vocabulary.** Five instruments actively **require** that it be able to. The five closure clauses are scale-local, contain none of the four structural terms as their subject except `Capability`/`Component` within the platform family, and are governed by `AUTH-INF-001` CR-INF-001.3, which fixes "closed" to mean *complete for current scope*.

---

## OUTPUT 8 — Meta-Ontology Determination

### 8.1 The determination

> **A — Current Canonical Repository Vocabulary.**
>
> `Universe`, `Domain`, `Capability`, and `Component` are the **current canonical Repository Truth vocabulary** for structural decomposition. They are **not** a Permanent Constitutional Ontology.

**Proof, from Repository Truth only:**

1. Their sole owner, `ARCH-001` §2, declares CONSTITUENT / GOVERNANCE / RATIFICATION / EC-1 AUTHORITY = **NONE**, and its contents *"read-only, **provisional**, versioned… swappable."* (Finding A)
2. Three of the four are absent from `GOVERNED_CATEGORIES` in the executable root law. (Finding B)
3. No clause anywhere in the repository states that any structural term is permanently immutable. (E-01)
4. `CMG-000001` XIII.5 recognizes `Universe` as a Kind but explicitly declines to own its model — *"owned elsewhere and consumed by reference."* Recognition is not permanence. (E-04)
5. `CMG-000001` LXXVI.1 lists `Domain` and `Universe` among the things admissible **without structural amendment** — a term that can be *added to* is a term in an open set. (E-07)
6. `UCKP-ART-20` binds the law across future civilizations; a law naming four English nouns as permanent could not satisfy it. (§3.3)

### 8.2 The homonym finding (recorded, not legislated)

`Universe` denotes **three unrelated concepts** in Repository Truth:

| Sense | Meaning | Home |
|---|---|---|
| **U-1 · Structural** | Top-level architectural container for a coherent reality domain; 112 registered | `ARCH-001` §2 |
| **U-2 · Constitutional** | The assembled Universal Constitutional Knowledge Universe — the whole of law + registry + graph + timeline | `engine/uckp/universe.py:1-6` |
| **U-3 · Runtime alias** | An assembled `RuntimeUnit` bound to a context — *"here called a Universe"* | `engine/runtime/composition.py:1-8` |

These are not in conflict — they never meet in one authority chain — but they are **three meanings under one token**. `CMG-000001` LXXVI.6 forbids expansion by *reinterpretation* precisely because *"reinterpretation is invisible to validation."* This is disambiguation work for a future determination, not a defect requiring change now. Related, already on record: `UCOS-ACFV-000001` W-4 (E-19).

### 8.3 Reconciliation of the closure clauses

The five "closed ontology" clauses (E-15) are **not** counter-evidence to determination A:

- **Scope.** Each closes only its own family root set (PLATFORM 8, DATA/SERVICE/APPLICATION 10, RUNTIME 11). None closes the repository's structural vocabulary, and `Universe` and `Domain` appear in **none** of them as roots.
- **Reading rule.** `AUTH-INF-001` CR-INF-001.3 is binding and self-executing: `"closed"` SHALL be read as *complete for current scope*, **never** as *incapable of future extension*. CR-INF-001.2: *"Certification closes scope. Certification never closes evolution."*
- **Already recorded.** `UCOS-ACFV-000001` W-5 flags the differing root cardinality as *"an asymmetry the self-similarity principle does not explain"*; W-1 records that only `PLATFORM-005` PME-01 carries an explicit growth clause and that the channel *"exists architecturally… it is unevenly **legislated**."*

The last point is the real finding: the openness is **constitutionally guaranteed but unevenly written down**. That is the gap Output 10 addresses.

### 8.4 Should Repository Truth own the nine meta-ontology concerns?

Determination per concern. **PASS** = already legislated, no action. **REUSE** = an owner exists and shall be used.

| # | Concern | Located canonical owner | Verdict |
|---|---|---|---|
| M-1 | Structural **Vocabulary** | `engine/uckp/vocabulary.py` (`VocabularyRegistry`, append-only, INV-14-proved) + `CMG-K-23` Glossary Kind | **PASS / REUSE** |
| M-2 | Structural **Categories** | `engine/uckp/law.py:424` `GOVERNED_CATEGORIES`, declared open under ART-17 | **PASS / REUSE** |
| M-3 | Structural **Classifications** | `CMG-000001` XIII (Constitution Taxonomy, Kind set OPEN); family `*-004-*-TAXONOMY` artifacts | **PASS / REUSE** |
| M-4 | Structural **Patterns** | `KNOWLEDGE_KIND_VOCABULARY` terms `pattern` / `anti-pattern` (`vocabulary.py:211-236`) | **PASS / REUSE** |
| M-5 | Structural **Relationships** | `RELATION_TYPE_VOCABULARY` (17 terms) + `RELATIONSHIP_CLASS_VOCABULARY` (12 registers); `UCKP-ART-07` | **PASS / REUSE** |
| M-6 | Structural **Topologies** | `engine/uckp/graph.py` `UniversalKnowledgeGraph`; `UCKP-ART-07`; acyclicity/orphan/dangling proofs | **PASS / REUSE** |
| M-7 | Structural **Evolution** | `CEP-009` + Addendum B (canonical 15-stage lifecycle); `UCKP-ART-14`; `AUTH-INF-001` | **PASS / REUSE** |
| M-8 | Structural **Taxonomy** | `CMG-000001` XIII; `taxonomy` is a `GOVERNED_CATEGORY`; `engine/context/taxonomy.py` | **PASS / REUSE** |
| M-9 | Structural **Ontology** | `CMG-000001` XIV (OPEN under XIV.7); `ontology` is a `GOVERNED_CATEGORY`; `01-WORKING/ONTOLOGY-REGISTER.md` | **PASS / REUSE** |

**All nine concerns are already legislated and already owned. CREATE is unavailable for every one of them** under `UCKP-ART-18` (Reuse Before Create) and `CMG-000001` LXXVII.2(a).

**Answer to the mission question — "should Repository Truth own structural vocabulary?"** It **already does**, through `CMG-000001` XIII/XIV (what may be admitted) and `engine/uckp/vocabulary.py` (the executable append-only registry that admits it). No new ownership is required or permitted.

---

## OUTPUT 9 — PASS / REUSE / EXTEND / CEP / CREATE Matrix

| # | Item | Disposition | Authority |
|---|---|---|---|
| D-01 | Structural vocabulary is *current canonical*, not *permanent ontology* | **PASS** | ARCH-001 header; `law.py:424`; E-01 |
| D-02 | Repository Truth permits vocabulary evolution | **PASS** | `CMG` XIII.2, XIV.7, LXXVI.1/.5; ART-17/INV-14 |
| D-03 | Evolution is registration, never amendment or rename | **PASS** | `CMG` LXXVI.3/.6; `CEP-009` B.7.2 |
| D-04 | Foundation needs no redesign for a future construct | **PASS** | `CEP-009` B.2.1-.3 |
| D-05 | Future objects (A1, B2, Ω17, Digital Twins, Quantum Objects, unknown objects) are admissible | **PASS** | `CMG` LXXVII.1/.3/.6-.7 — total admission procedure, exhaustive by construction. **Not legislated here, per mission constraint** |
| D-06 | Meta-ontology concerns M-1…M-9 | **PASS / REUSE ×9** | Output 8 §8.4 |
| D-07 | Generators are vocabulary-agnostic | **PASS** | Output 5 |
| D-08 | Runtime is vocabulary-agnostic | **PASS** | Output 6 |
| D-09 | Layer Zero (`engine/uckp/`) is the compliant reference pattern | **PASS** | Output 4 §4.2 |
| D-10 | Six engines hardcode structural names (H-01…H-06) | **CEP** | Output 4 §4.1. Remediation requires a proposal; **do not modify** |
| D-11 | Openness is guaranteed but unevenly legislated across families | **CEP** | `UCOS-ACFV-000001` W-1, W-5 |
| D-12 | `Universe` carries three meanings under one token | **CEP** | Output 8 §8.2 |
| D-13 | Correction: ARCH-001 is present on disk, not missing | **RECORD** | Finding C |
| D-14 | Any new structural term, category, ontology entity, or vocabulary | **CREATE — UNAVAILABLE** | `UCKP-ART-18`; `CMG` LXXVII.2(a). Every concern has a located owner |

**CREATE count: 0.** No concept examined by this determination lacks a canonical owner.

---

## OUTPUT 10 — Recommended Constitutional Evolution

Three Constitutional Evolution Proposals. All are **recommendations only** — none is enacted, and no frozen vocabulary is touched by any of them.

### CEP-MOD-001 — Declare the structural vocabulary's constitutional status explicitly

**Gap.** `ARCH-001` §2 owns the four terms while declaring AUTHORITY = NONE. Six downstream instruments restate the chain as though it were settled law (Output 2, "Corroborating restatements"). A reader cannot presently tell from any single artifact whether the chain is permanent ontology or current vocabulary — which is why this determination was necessary.

**Proposal.** A `CMG-K-23` **Glossary** instrument recording that the structural vocabulary is *current canonical Repository Truth vocabulary, open under `CMG-000001` XIII.2/XIV.7 and `UCKP-ART-17`*, and naming `ARCH-001` §2 as its located owner.

**Disposition: EXTEND.** The Kind exists (`CMG-K-23`); the concern — repository-wide terminology status — is presently unowned (E-18: the only glossary found is program-scoped). Per `CMG-000001` LXXVII.2(b) this is an extension within an existing owner's scope, not a new authority.

**Constraints honoured:** renames nothing (LXXVI.3), reinterprets nothing (LXXVI.6), creates no registry or namespace (XLI.5), invalidates no frozen artifact.

### CEP-MOD-002 — Bind the six hardcoding sites to the existing vocabulary registry

**Gap.** H-01…H-06 close structural vocabularies in Python `Enum`s, literal tuples, a required constructor field, and `case` labels. `engine/uckp/vocabulary.py:1-9` states the constitutional objection in its own words: *"a vocabulary frozen into a Python `Enum` fails both [Article 15 and Article 17]… the set of admissible… kinds becomes a code edit, and a code edit in Layer Zero is a constitutional amendment."* Six engines outside Layer Zero do exactly that.

**Proposal.** Bind each site to `VocabularyRegistry`, retaining the existing enums as **checked projections** — the pattern `engine/uckp/assimilation.py::verify_vocabulary_alignment` already implements and fails closed on. No new mechanism is invented; the compliant pattern is reused verbatim.

**Disposition: EXTEND (REUSE of mechanism).** Sequence by risk: H-01 (`coerce` raises on unknown — the only site that hard-refuses a future member), then H-04, H-02, H-03, H-06, H-05 (`UNCLASSIFIED` fallback already fails open).

**Constraints honoured:** no rename, no migration, no behavioural change while every current term stays registered. **Not executed — proposal only.**

### CEP-MOD-003 — Legislate the growth clause uniformly across the five family meta-models

**Gap.** `UCOS-ACFV-000001` W-1: only `PLATFORM-005` PME-01 carries an additive-growth clause; `DATA-005`, `SERVICE-005`, `APPLICATION-005`, `RUNTIME-005`, `INFRASTRUCTURE-005` assert closure (`DMI-01`, `SMI-01`, `AMI-01`, `RMP-01`) with no corresponding growth clause. W-5: root cardinality differs across families (8 / 10 / 10 / 10 / 11) with no stated reason. The channel *"exists architecturally… it is unevenly legislated."*

**Proposal.** Extend each family meta-model with a PME-01-equivalent growth clause, stating what `AUTH-INF-001` CR-INF-001.3 already makes binding: the root set is closed **for current scope**, and a future root is admitted by registration under `CMG-000001` LXXVI.

**Disposition: EXTEND.** This adds no root, alters no cardinality (`CMG` XIV.7), and reclassifies nothing. It writes down a property the constitution already guarantees.

**Constraint — freeze interaction.** `DATA-015` and `APPLICATION-015` freeze DF-1/AF-1 as *"IMMUTABLE… no artifact… may be modified in place"* while permitting *"extension is **additive-only**."* CEP-MOD-003 must therefore proceed as an **additive addendum per family**, never as an in-place edit, exactly as `CEP-009` Addendum B did for `CEP-009`.

---

## Closure

| Mission question | Determination |
|---|---|
| 1. Is the vocabulary permanently immutable, or current canonical? | **Current canonical.** No immutability clause exists; the owner declares AUTHORITY = NONE and its contents provisional |
| 2. Would future evolution require new structural concepts, and does Repository Truth permit them? | **Permitted, by five independent instruments.** `CMG` XIII.2/XIV.7/LXXVI.1/LXXVII; `UCKP-ART-17`/INV-14; `AUTH-INF-001`; `CEP-009` B.2.1. No future object was legislated, per mission constraint |
| 3. Does the engine depend on names or declarations? | **Split.** Layer Zero on declarations (and proves it); six engines outside it on names — H-01…H-06 |
| 4. Do generators depend on names, contracts, relationships, or registries? | **Contracts, registries, relationships. Zero name literals** |
| 5. Does runtime depend on Universe/Capability/Component or on declarations? | **Declarations only.** The one "Universe" occurrence is a documented local alias for `RuntimeUnit` |
| 6. Does any artifact prevent vocabulary evolution? | **No.** Five require it. Five scale-local closure clauses are governed by `AUTH-INF-001` CR-INF-001.3 |

**Vocabulary replaced: none. Renamed: none. Parallel terminology introduced: none. Frozen artifacts invalidated: none. Files modified: none. CREATE dispositions: 0.**

Repository Truth artifacts cited: 24. Source files inspected: 19.

This determination is recorded at commit `00bd45f`. Nothing herein is enacted; CEP-MOD-001…003 require ratification before any change.

---

*End of UCOS-MOD-001-CONSTITUTIONAL-META-ONTOLOGY-DETERMINATION.md*
