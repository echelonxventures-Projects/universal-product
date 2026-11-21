# UCOS Ω∞ — C-1 INTER-VOCABULARY MAPPING REPRESENTATION DETERMINATION

**Whether a total mapping between two registered vocabularies has a permanent constitutional representation. The measured answer is that it has three, all of them already built, already exercised, and already validated — and that the predecessor determination reached the opposite conclusion from a defective probe.**

| Field | Value |
|---|---|
| Artifact | `UCOS-OMEGA-INFINITY-C-1-INTER-VOCABULARY-MAPPING-REPRESENTATION-DETERMINATION.md` |
| Authority | **NONE — DERIVED DETERMINATION.** Legislates nothing, amends nothing, registers nothing, mints nothing, implements nothing, creates no mapping. It measures what exists and reports which of it answers `C-1`. |
| Mode | ANALYSIS ONLY · **NO CODE · NO REGISTRY · NO JSON · NO MAPPING CREATED · NO IDENTITY · NO OWNERSHIP · NO CERTIFICATION · NO COMMIT** |
| Baseline commit (HEAD) | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Baseline branch | `integration/recovery-001` |
| Subject | `C-1` — the representation of a total mapping between two registered vocabularies, raised by `…EEG-1-EEG-2-EVOLUTION-EXTENSIBILITY-CLOSURE-DETERMINATION.md` §8.5 and inherited from `CEP-MOD-002` §12.2 |
| Method | Read-only measurement at one commit, plus in-process construction of the live universe (`build_universe()`) and direct inspection of its nodes, edges and per-object facet bindings. Nothing written |
| **Central finding** | **`C-1` is not an open question. The representation exists at three independent layers and two of them already carry vocabulary terms as first-class objects: `uckp.facet` (33 of 33 terms) and `uckp.evolution-stage` (15 of 15 terms, with a term→term edge).** Every UCKO already carries **six cross-vocabulary bindings**, each validated by `require_term` and each failing closed — §3, §5 |
| **Correction issued** | **The predecessor's §4.6 measurement was wrong.** It probed **bare term ids** (`book`, `capability`, `existence`) against `node_ids()`, got seven `False`, and concluded *"vocabulary terms are not graph nodes."* Terms are projected under **URN local names** — `urn:ucos:ucko:ucos:UCKP-STAGE-observe`. The correct probe finds them. This changes `C-1`'s disposition from *blocked* to *resolvable by an existing pattern* — §2.4 |
| **Relationship entity** | **Already first-class, and not newly proposed.** `RegistryKind.RELATIONSHIP` is one of 29 registered kinds; `relationship.schema.json` is titled *"A first-class, navigable edge"* with an immutable append-only `edge_id`; **13,361** edges are materialized — §7 |
| Options evaluated | **A · B · C · D · E** against **12** criteria — §5 |
| **Selected** | **Option D — the existing three-layer pattern, discovered.** A · B · C rejected on measured constitutional grounds; E rejected because a compliant route exists — §5.7 |
| Findings raised | **4** (`C1-F-1`…`C1-F-4`) · 0 CRITICAL · 2 HIGH · 1 MEDIUM · 1 LOW — §11 |
| **Verdict** | **CONDITIONALLY RESOLVED** — §13 |
| Can `C-1` close without a parallel framework, duplicate registry, temporary workaround or hardcoded exception? | **YES on all four, measured** — §13.3 |

---

## 1. Current Baseline

### 1.1 Captured before writing

| Field | Value |
|---|---|
| HEAD | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch | `integration/recovery-001` |
| `git status --porcelain` | **360** lines |
| Tracked modifications | **38** |
| Staged | **0** |
| Untracked | **322** |

### 1.2 Vocabulary substrate, measured live

| Measure | Value |
|---|---|
| Registered vocabularies | **13** |
| Total registered terms | **204** |
| Terms carrying `successors` | **17** |
| `VocabularyRegistry.is_extensible()` | **True** |
| Registry digest | `7d733fcc2e5551f1` |
| `verify_vocabulary_alignment()` | **PASS** over **9** projections |

| Vocabulary | Terms |
|---|---|
| `uckp.authority-tier` | 4 |
| `uckp.facet` | 33 |
| `uckp.governed-category` | 35 |
| `uckp.knowledge-kind` | 18 |
| `uckp.lifecycle-stage` | 10 |
| `uckp.non-authoritative-category` | 25 |
| `uckp.relation-type` | **17** |
| `uckp.relationship-class` | **12** |
| `ucos.architecture-layer` | 14 |
| `ucos.civilization-stratum` | 9 |
| `ucos.discovery-dimension` | 8 |
| `ucos.projection-kind` | 13 |
| `ucos.ukip-facet` | 6 |

### 1.3 Object and graph substrate, measured live

| Measure | Value |
|---|---|
| `build_universe()` nodes | **6,338** |
| Derived edges | **13,036** |
| Edge classes | `ownership` 6,338 · `authority` 6,337 · `constitutional` 260 · `validation` 56 · `governance` 30 · `evolution` 15 |
| Edge relations | `owns` 6,338 · `derived-from` 6,337 · `depends-on` 192 · `validates` 56 · `governs` 43 · `implements` 30 · `references` 25 · `produces` 15 |
| **Vocabulary UCKO nodes** | **13 of 13** — one per registered vocabulary |
| **Term UCKO nodes (`uckp.facet`)** | **33 of 33** |
| **Term UCKO nodes (`uckp.evolution-stage`)** | **15 of 15** |
| `DEFAULT_DISCOVERY_ROOTS` | `("engine.uckp",)` — **one root** |

### 1.4 Edge register substrate, measured live

| Measure | Value |
|---|---|
| `00-BOOK/DATA/relationships.json` | `count` **13,361**, actual **13,361** — consistent |
| Distinct edge types | **16** |
| Edges carrying `inverse_of` | **5,069** |
| Schema | `00-BOOK/SCHEMAS/relationship.schema.json` |
| `edge_id` pattern | `^UEDGE-[0-9]{9,}$` |
| `edge_id` producer | `00-BOOK/tools/ukb.py:1031` — `f"UEDGE-{edge_seq[0]:09d}"`, **a sequential counter** |
| `UEDGE-` occurrences in `00-BOOK/DATA/id-ledger.json` | **0** |

---

## 2. C-1 Problem Definition

### 2.1 The question as inherited

`C-1` was raised in `…EEG-1-EEG-2-…-DETERMINATION.md` §12.5:

> *"**How is a total mapping between two registered vocabularies represented?** Three located candidates: promote terms to UCKOs and use the existing relationship graph; add a first-class inter-vocabulary relation to Layer Zero; or classify the mapping as Configuration as `CEP-MOD-002` did for `_CATEGORY_LAYER`."*

It was inherited from `CEP-MOD-002` §12.2, which dispositioned the identical case:

> *"H-05 `_CATEGORY_LAYER` mapping — **CEP** — A mapping between term sets has no representation in `Vocabulary`; **requires its own determination**."*

### 2.2 The two mappings that need it

| Mapping | Home | Shape | Total? |
|---|---|---|---|
| `_ENTITY_GROUP` | `platform/portal/contracts.py:214` | `dict[EntityKind, CapabilityGroup]` | **Yes** — 7 = 7 |
| `_SURFACE_TABLE` | `platform/portal/contracts.py:80` | `dict[CapabilityGroup, tuple[str, PortalSection]]` | **Yes** — 16 = 16 |
| `_CATEGORY_LAYER` | `engine/graph/architecture/layers.py` | category → layer | Deferred by `CEP-MOD-002` |

### 2.3 The premise that was accepted without checking

The premise on which `C-1` was opened is **true and remains true**:

> `CEP-MOD-002` §7.1 — *"`Vocabulary` has no representation for a relation between vocabularies — it holds `terms`, and `Term` holds `successors` only within one vocabulary."*

Verified at this baseline: `Term` has exactly five fields — `term_id`, `definition`, `rank`, `successors`, `symmetric`. **No cross-vocabulary field exists.**

**The error was not in the premise. It was in the inference drawn from it** — that because `Vocabulary` cannot represent the mapping, the repository cannot. §3 shows the repository represents it somewhere else, by design.

### 2.4 Correction to the predecessor determination

The predecessor concluded (§4.6):

> *"**Vocabulary terms are not graph nodes at this baseline.** Routing the mapping through the graph would first require promoting terms to UCKOs."*

That conclusion rested on probing seven **bare term ids** — `book`, `capability`, `MetaKernelStratum`, `workspace`, `main`, `existence`, `location` — against `node_ids()`, all returning `False`.

**The probe was wrong.** UCKO ids are URNs; a projected term appears under a URN local name, not under its bare term id. Measured correctly at the same baseline:

```
urn:ucos:ucko:ucos:UCKP-STAGE-observe                → present
urn:ucos:ucko:ucos:UCKP-STAGE-learn                  → present   (15 stages)
urn:ucos:ucko:ucos:uckp.authority-tier               → present   (13 vocabularies)
33 facet terms projected via facet_object()          → present
```

**Terms are already promoted to UCKOs for two vocabularies, and the vocabularies themselves are objects for all thirteen.** The precondition the predecessor called unmet is met. This determination's disposition of `C-1` differs from the predecessor's for that reason and no other.

### 2.5 What `C-1` actually asks, restated

> Given that a mapping between two vocabularies is not representable **inside `Vocabulary`**, is there a located constitutional home for it elsewhere that requires no new mechanism?

---

## 3. Existing Relationship Mechanisms

Five located mechanisms. Each is measured for what it owns and where its edges live.

### 3.1 M-A — `engine/uckp/values.py::Relationship` (Facet 9)

| Field | Measured |
|---|---|
| Shape | `relation: str`, `target: str`, `relationship_class: str` |
| Docstring | *"An executable binding to another object (Facet 9)."* |
| Identity of its own | **None** — it is a facet value, not an entity |
| Target space | UCKO URN |
| Validation | `ucko.py:396-397` — `require_term(RELATION_TYPE, …)` and `require_term(RELATIONSHIP_CLASS, …)`, **both fail closed** |
| Openness | `uckp.relation-type` 17 terms · `uckp.relationship-class` 12 terms, both extensible |

### 3.2 M-B — `engine/uckp/graph.py::UniversalKnowledgeEdge`

| Field | Measured |
|---|---|
| Shape | `source`, `target`, `relation`, `relationship_class`, `scope` |
| Scopes | `OBJECT_SCOPE`, `STATE_SCOPE` |
| Derivation | `derive_edges(obj)` reads **six** facet sources: `dependencies`, `relationships`, `authority.derives_from`, `ownership.owner`, `traceability`, `evolution_history` |
| **Authorship rule, verbatim** | *"Edges are **derived, never authored**… so the graph cannot disagree with the objects — **there is no second place to update and therefore no second authority (Article 3)**. **Adding an edge means changing the object that claims the relationship.**"* |

**This rule is the single most constraining fact in this determination.** It forecloses any option in which edges are authored in their own register beside the objects (§5.3).

### 3.3 M-C — `engine/registry/models.py::Relationship` + `relationship.schema.json`

| Field | Measured |
|---|---|
| Docstring | *"A **first-class** knowledge-graph edge (relationship.schema.json)."* |
| Shape | `edge_id`, `source`, `target`, `type`, `inverse_of`, `note` |
| Schema title | *"UCOS Ω∞ Knowledge Graph Relationship"* |
| Schema description | *"A **first-class, navigable edge** in the Universal Knowledge Graph. Every relationship is directional and reachable from both endpoints."* |
| `edge_id` | *"Globally unique, immutable, **append-only** edge identifier"*, `^UEDGE-[0-9]{9,}$` |
| `type` openness, verbatim | *"**OPEN, append-only vocabulary**… any well-formed TitleCase-hyphenated type is valid, so **unlimited future relationship types are supported without schema redesign. A new relationship type is a new value, never a rewrite.**"* |
| Endpoint pattern | `^UCOS-[A-Z][A-Z0-9]{1,11}-[0-9]{6}$` — **Universal Artifact IDs only** |
| Materialized | **13,361** edges, 16 types, 5,069 with `inverse_of` |

### 3.4 M-D — `engine/kernel/meta.py::Relationship`

| Field | Measured |
|---|---|
| Shape | `relation`, `target` |
| Docstring | *"`relation` names the *kind* of relationship (**itself an open token — new relation kinds need no code change**)."* |
| Scope | Meta-kernel objects |

### 3.5 M-E — `engine/knowledge/ukip/relationships.py::Relationship` + `RelationshipSet`

Knowledge-intelligence plane; validated by `RelationshipsResolvedCheck` and `RelationshipsNavigableCheck`.

### 3.6 The mechanism the predecessor missed — cross-vocabulary field bindings

`engine/uckp/ucko.py:384-397`, `require_lawful`, verbatim docstring:

> *"Fail closed unless every vocabulary-bound facet uses a registered term. **Openness is register-then-use (Article 17)**: an unknown kind, tier, stage, relation or class is admitted by registration and refused until it is."*

```python
vocabularies.require_term(KNOWLEDGE_KIND,   self.taxonomy.kind)
vocabularies.require_term(GOVERNED_CATEGORY, self.taxonomy.category)
vocabularies.require_term(AUTHORITY_TIER,    self.authority.tier)
vocabularies.require_term(LIFECYCLE_STAGE,   self.lifecycle)
for relationship in self.relationships:
    vocabularies.require_term(RELATION_TYPE,       relationship.relation)
    vocabularies.require_term(RELATIONSHIP_CLASS,  relationship.relationship_class)
```

**Every UCKO in this repository already carries six references into six different vocabularies, each validated, each failing closed.** An object *is* the inter-vocabulary mapping structure. It has been all along.

Measured on a live term object:

```
id           : urn:ucos:ucko:ucos:UCKP-STAGE-observe
kind         : pattern        → term of uckp.knowledge-kind
category     : transition     → term of uckp.governed-category
tier         : architectural  → term of uckp.authority-tier
lifecycle    : implemented    → term of uckp.lifecycle-stage
relationship : derived-from → UCKP-ART-14  [authority]
relationship : produces     → UCKP-STAGE-learn [evolution]
```

**Six cross-vocabulary bindings on a single object that is itself a vocabulary term.**

### 3.7 The two term-projection precedents

| Precedent | Producer | Terms projected | Carries a term→term edge? |
|---|---|---|---|
| `uckp.facet` | `constitution.py::facet_object()` | **33 of 33** | No |
| `uckp.evolution-stage` | `capabilities.py::evolution_stage_object()` | **15 of 15** | **Yes** — `Relationship("produces", urn_for(…, f"UCKP-STAGE-{successor}"), "evolution")` |
| All 13 vocabularies | `constitution.py::vocabulary_object()` | 13 vocabulary objects | `derived-from → UCKP-ART-17 [authority]` |

`evolution_stage_object`'s docstring states the purpose verbatim:

> *"The successor relationship is what makes non-termination **visible in the graph**: every stage points at a next stage, so there is no node from which evolution cannot continue (UCKP-INV-13)."*

**A vocabulary's internal relation was made executable by projecting its terms as objects and its relation as an edge.** That is precisely the act `C-1` asks whether it is permitted to perform.

### 3.8 The identity substrate is already open

`engine/registry/universal/identity.py`:

| Field | Measured |
|---|---|
| `RegistryKind` | **29** members, including **`RELATIONSHIP`**, `LOCATION`, `REALITY`, `EXISTENCE`, `UNIVERSE`, `CIVILIZATION`, `KNOWLEDGE`, `CAPABILITY` |
| `register_kind(kind, code)` | *"Admit a future identifier kind. **This is the *only* extension mechanism.**"* Append-only, collision-free, re-registration is a no-op |
| `deterministic_id` docstring | *"`kind` may be a `RegistryKind` or the name of a kind admitted through `register_kind`, so **a future entity kind is minted by this same authority**"* |
| Live mint samples | `RELATIONSHIP` → `UCOS-REL-99790c515fc3` · `LOCATION` → `UCOS-LOC-0da89ce1be0a` |

**A relationship can already be minted an identity by the one authority, and a future entity kind can already join it without code.**

---

## 4. Constitutional Constraints

Every constraint below is quoted, not paraphrased. Together they eliminate three of the five options.

| # | Constraint | Source | Effect on `C-1` |
|---|---|---|---|
| `K-1` | *"Every governed category of entity shall exist **exactly once** as a canonical UCKO. Nothing exists constitutionally until it has become one."* | `ART-02` | `relationship` **is** a governed category (1 of 35). A relationship must be a UCKO to exist constitutionally |
| `K-2` | *"The same knowledge shall not be authored twice… A second definition of an existing primitive is a competing authority and is **void**."* | `ART-03` | Forbids a second relationship model |
| `K-3` | *"Every object is a node, every dependency an edge, and **every relationship is executable**: a relationship that cannot be resolved is not a relationship."* | `ART-07` | The graph is the located home of executable relations |
| `K-4` | *"Nothing shall require manual enumeration. Everything self-registers, self-describes, self-discovers…"* | `ART-08` | Provider discovery, not a hand-kept list |
| `K-5` | *"…an unknown future category is admitted by **registration, never by amendment**."* | `ART-17` | The admission rule for every term |
| `K-6` | *"Before anything is created its canonical object shall be located. If it exists it is reused, extended or referenced. **It is never duplicated and never given a rival.**"* | `ART-18` | Forbids creating a new mechanism where one exists |
| `K-7` | *"It appends; it never rewrites; it never terminates."* | `ART-14` | Append-only history |
| `K-8` | **"Edges are derived, never authored… there is no second place to update and therefore no second authority (Article 3). Adding an edge means changing the object that claims the relationship."** | `graph.py` module docstring | **Forecloses an authored edge register beside the objects** |
| `K-9` | *"`engine/uckp/law.py` is never amended to fit the data (`UCKP-ART-17`)."* | `how_to_extend[2]` | **Forecloses extending `Term`** |
| `K-10` | *"A second registry, engine, lifecycle, identity authority, **relationship graph** or evolution system standing beside the ones that exist."* | `what_this_forbids` | **Forecloses a second relationship graph, by name** |
| `K-11` | *"One append-only mint holds every repository identity, every declared map resolves in it…"* | `CAA-INV-04` | Any edge identity must come from the one mint |
| `K-12` | *"Every vocabulary, adapter set and relationship class admits an unknown future member."* | `INV-14` | Relationship expansion must be infinite |

**`K-8`, `K-9` and `K-10` are decisive.** They eliminate Option C-as-authored-register, Option A, and Option B respectively — each by a rule already written, not by a judgement made here.

---

## 5. Architecture Options Analysis

### 5.1 The twelve evaluation criteria

Applied identically to every option: zero duplicate authority · zero duplicate registry · zero parallel relationship model · Knowledge Once · append-only evolution · infinite vocabulary expansion · infinite relationship expansion · backward compatibility · layer dependency direction · runtime discoverability · auditability · certification capability.

### 5.2 Option A — extend `Term.successors` to carry cross-vocabulary relationships

| Criterion | Verdict | Measurement |
|---|---|---|
| Zero duplicate authority | **FAIL** | `successors` is consumed by `can_transition(source, target)`, which resolves both ends **inside one vocabulary**. Overloading it to mean *"and sometimes a term in another vocabulary"* gives one field two meanings — a second definition of an existing primitive (`K-2`) |
| Zero duplicate registry | PASS | No new registry |
| Zero parallel relationship model | **FAIL** | Creates a second edge representation beside `Relationship`/`UniversalKnowledgeEdge` |
| Knowledge Once | **FAIL** | `uckp.relation-type` (17) already names how one thing binds to another. A bare `successors` string names no relation type, so either the relation is unnamed or it is named twice |
| Append-only evolution | PASS | `extended_with` semantics unchanged |
| Infinite vocabulary expansion | PASS | — |
| Infinite relationship expansion | **FAIL** | `successors` is `tuple[str, ...]` with no class and no relation type. New *kinds* of cross-vocabulary relation could not be expressed |
| Backward compatibility | **FAIL** | 17 terms currently carry `successors` under intra-vocabulary semantics. Redefining the field changes their meaning retroactively — the exact harm `extended_with` refuses: *"a term whose meaning can change retroactively invalidates every digest computed under the old meaning"* |
| Layer dependency direction | PASS | — |
| Runtime discoverability | PARTIAL | Terms are discoverable; the relation's meaning would not be |
| Auditability | **FAIL** | An edge with no class cannot be asked the class-scoped questions `graph.py` exists to answer — *"'is authority acyclic?' is a question about one class"* |
| Certification capability | **FAIL** | No relation type ⇒ nothing to certify against |

**7 FAIL · 4 PASS · 1 PARTIAL. REJECTED**, and additionally barred by `K-9`: it is an amendment to Layer Zero made to fit one consumer.

### 5.3 Option B — a universal Relationship Vocabulary layer

| Criterion | Verdict | Measurement |
|---|---|---|
| Zero duplicate authority | **FAIL** | `uckp.relation-type` (17) and `uckp.relationship-class` (12) **already are** the relationship vocabulary. A third would be `K-2` void |
| Zero duplicate registry | **FAIL** | A "layer" holding edges is a registry beside `VocabularyRegistry` and the graph |
| Zero parallel relationship model | **FAIL** | Directly barred by `K-10`, which names *"relationship graph"* in its forbidden list |
| Knowledge Once | **FAIL** | Same |
| Append-only evolution | PASS | — |
| Infinite vocabulary expansion | PASS | — |
| Infinite relationship expansion | PASS | — |
| Backward compatibility | PARTIAL | Existing edges would need re-homing or dual maintenance |
| Layer dependency direction | PARTIAL | Undetermined without a declared home |
| Runtime discoverability | PASS | — |
| Auditability | **FAIL** | Violates `K-8`: authored edges create *"a second place to update"* |
| Certification capability | PARTIAL | Would need its own gate — `non_goals[4]` forbids adding one |

**5 FAIL · 4 PASS · 3 PARTIAL. REJECTED** — barred by name in `what_this_forbids`.

### 5.4 Option C — extend the Knowledge Graph representation

Two readings must be separated, because they get opposite verdicts.

**C-i — author edges into the graph directly.**

**REJECTED on `K-8`.** *"Edges are derived, never authored… Adding an edge means changing the object that claims the relationship."* An authored edge is the second authority `ART-03` voids.

**C-ii — extend `UniversalKnowledgeEdge` with a third scope (e.g. `TERM_SCOPE`).**

| Criterion | Verdict | Measurement |
|---|---|---|
| Zero duplicate authority | PASS | One graph, one edge type |
| Zero duplicate registry | PASS | — |
| Zero parallel relationship model | PASS | — |
| Knowledge Once | PASS | — |
| Append-only | PASS | — |
| Infinite vocabulary expansion | PASS | — |
| Infinite relationship expansion | PASS | Relation and class stay open |
| Backward compatibility | PASS | `scope` defaults to `OBJECT_SCOPE` |
| Layer dependency direction | PASS | — |
| Runtime discoverability | PASS | — |
| Auditability | PASS | — |
| Certification capability | PASS | — |
| **Necessity** | **FAIL** | **A term projected as a UCKO is already an object.** Its edges are already `OBJECT_SCOPE`, already derived, already validated. A third scope would distinguish a case the mechanism does not need distinguished |

**12 PASS, 1 FAIL on necessity. REJECTED under `K-6`** — *"If it exists it is reused, extended or referenced"*. Adding a scope for a case already covered is a rival to the coverage that exists.

### 5.5 Option D — the existing three-layer pattern, discovered

> **A vocabulary term is projected as a UCKO by a provider module. A mapping between two vocabularies is a `Relationship` on the source term's object, whose `relation` is a term of `uckp.relation-type` and whose `relationship_class` is a term of `uckp.relationship-class`. `derive_edges` turns it into a `UniversalKnowledgeEdge`. `require_lawful` validates both ends against their vocabularies and fails closed.**

| Criterion | Verdict | Measurement |
|---|---|---|
| Zero duplicate authority | **PASS** | Nothing new declared. Six `require_term` bindings already exist at `ucko.py:391-397` |
| Zero duplicate registry | **PASS** | `VocabularyRegistry` + `UniversalKnowledgeRegistry`, both existing |
| Zero parallel relationship model | **PASS** | Reuses M-A and M-B unchanged |
| Knowledge Once | **PASS** | The mapping lives in exactly one place — the source term's object. `K-8` satisfied by construction |
| Append-only evolution | **PASS** | `with_relationships` returns a new object; `ART-12` preserves predecessors |
| Infinite vocabulary expansion | **PASS** | `is_extensible()` **True**; reach widens automatically on registration |
| Infinite relationship expansion | **PASS** | `uckp.relation-type` (17) and `uckp.relationship-class` (12) are themselves extensible vocabularies |
| Backward compatibility | **PASS** | Additive. 33 facet terms and 15 stage terms already projected with no disturbance to 6,338 nodes |
| Layer dependency direction | **PASS** | `registry.discover(*roots)` walks roots **passed to it**. `DEFAULT_DISCOVERY_ROOTS = ("engine.uckp",)` is a default, not a hardcode. A platform provider is discovered by adding a root — **no engine→platform import** |
| Runtime discoverability | **PASS** | `ART-08` provider hook: *"the registry discovers these without enumeration"* |
| Auditability | **PASS** | Edges classed; `dangling()` finds unresolvable targets; `INV-17` audit trail |
| Certification capability | **PASS** | `require_lawful` fails closed; no new gate needed — `non_goals[4]` satisfied |

**12 PASS · 0 FAIL. SELECTED.**

### 5.6 Option E — reject all

**REJECTED.** Option E is warranted only if every route violates a constraint. Option D violates none of the twelve criteria and none of the twelve constitutional constraints, and it is **already executing** for two vocabularies at this baseline.

### 5.7 Comparative result

| Option | PASS | FAIL | Disposition | Barred by |
|---|---:|---:|---|---|
| A — extend `Term.successors` | 4 | 7 | **REJECTED** | `K-2`, `K-9` |
| B — universal Relationship Vocabulary layer | 4 | 5 | **REJECTED** | `K-10` (by name) |
| C-i — author edges into the graph | — | — | **REJECTED** | `K-8` |
| C-ii — a third edge scope | 12 | 1 | **REJECTED** | `K-6` (unnecessary) |
| **D — existing three-layer pattern** | **12** | **0** | **SELECTED** | — |
| E — reject all | — | — | **REJECTED** | A compliant route exists |

---

## 6. Recommended Permanent Model

### 6.1 The model

**No new architecture. The following names the existing one and states its contract for the inter-vocabulary case.**

```
    ┌─ VOCABULARY PLANE ─────────────────────────────────────────────┐
    │  VocabularyRegistry — 13 vocabularies, 204 terms, extensible   │
    │  Term(term_id, definition, rank, successors, symmetric)        │
    │  Owns: WHICH TERMS ARE ADMISSIBLE. Intra-vocabulary only.      │
    └───────────────────────────┬────────────────────────────────────┘
                                │ projected by a provider (ART-08)
                                │ precedent: facet_object ×33,
                                │            evolution_stage_object ×15
                                ▼
    ┌─ OBJECT PLANE ─────────────────────────────────────────────────┐
    │  UCKO — 6,338 nodes                                            │
    │  require_lawful() validates SIX cross-vocabulary bindings:     │
    │     kind→knowledge-kind  category→governed-category            │
    │     tier→authority-tier  lifecycle→lifecycle-stage             │
    │     relation→relation-type  class→relationship-class           │
    │  Owns: HOW TERMS RELATE ACROSS VOCABULARIES.                   │
    └───────────────────────────┬────────────────────────────────────┘
                                │ derive_edges() — derived, never authored
                                ▼
    ┌─ GRAPH PLANE ──────────────────────────────────────────────────┐
    │  UniversalKnowledgeGraph — 13,036 edges, 6 classes             │
    │  Owns: EXECUTABILITY AND REACHABILITY (ART-07).                │
    └────────────────────────────────────────────────────────────────┘
```

### 6.2 The separation of concerns that resolves `C-1`

| Plane | Owns | Does **not** own |
|---|---|---|
| Vocabulary | Which terms are admissible; intra-vocabulary order and succession | Any relation leaving the vocabulary |
| Object | Every cross-vocabulary binding, validated and fail-closed | Executability |
| Graph | Executability, reachability, class-scoped questions | Authorship of any edge |

**`Vocabulary` has no inter-vocabulary representation because inter-vocabulary relations are not its subject.** `CEP-MOD-002` measured the absence correctly and drew the correct local conclusion — *"The mapping half belongs to Configuration"* was one candidate home. The measured home is the **object plane**, which is stronger than Configuration on every criterion: it is validated, classed, executable, auditable and certifiable, and Configuration is none of those.

### 6.3 How the two `EEG-2` mappings land

| Mapping | Representation under Option D |
|---|---|
| `_ENTITY_GROUP` : `EntityKind → CapabilityGroup` | Each `EntityKind` term projected as a UCKO carrying `Relationship(relation=<term of uckp.relation-type>, target=<CapabilityGroup term URN>, relationship_class="authority")` |
| `_SURFACE_TABLE` : `CapabilityGroup → (title, PortalSection)` | Each `CapabilityGroup` term projected as a UCKO. The **section** half is a `Relationship` to the `PortalSection` term URN. The **title** half is not a relation at all — it is the term's `definition`, already a `Term` field |
| `_CATEGORY_LAYER` (`CEP-MOD-002`, deferred) | Same shape — a relation from a category term to an architecture-layer term |

**`_SURFACE_TABLE` decomposes into one relation plus one existing `Term` field.** It was only ever a mapping in its Python shape.

### 6.4 Which relation term applies

This determination **does not select** the relation term for either mapping. `uckp.relation-type` holds 17 candidates including `governs`, `owns`, `depends-on` and `implements`, and `uckp.relationship-class` holds 12 including `authority` and `governance`. Choosing among them states what the binding *means*, which is a declaration act, not a measurement. §9.4 assigns it.

### 6.5 What the model requires that does not yet exist

| Requirement | Status |
|---|---|
| A projection function per contributed vocabulary | **Precedent exists ×2**; not written for the `EEG-1`/`EEG-2` vocabularies |
| Provider discovery reaching those modules | **Mechanism exists.** `DEFAULT_DISCOVERY_ROOTS` is `("engine.uckp",)` — one root. A second root is a call-site argument, not a code change to the registry |
| A relation term chosen per mapping | **Owner decision** — §9.4 |
| New mechanism of any kind | **NONE** |

---

## 7. Relationship Entity Determination

### 7.1 The directive's question

> Should `Entity A —relationship→ Entity B` become a **Relationship Entity** carrying source, target, relationship type, authority, lifecycle, evidence and evolution history?

### 7.2 The measured answer

**It already has, in one of the five mechanisms, and it is not a proposal.**

| Evidence | Measurement |
|---|---|
| `relationship` is a governed category | **Yes** — 1 of 35 in `GOVERNED_CATEGORIES` |
| `ART-02` consequence | A relationship *"shall exist exactly once as a canonical UCKO"* |
| `RegistryKind.RELATIONSHIP` | **Present** — 1 of 29 registered kinds |
| Deterministic mint available | **Yes** — `deterministic_id(RegistryKind.RELATIONSHIP, …)` → `UCOS-REL-99790c515fc3` |
| Schema declares first-class | **Yes** — *"A first-class, navigable edge in the Universal Knowledge Graph"* |
| Own identity | **Yes** — `edge_id`, *"Globally unique, immutable, append-only"* |
| Type openness | **Yes** — *"unlimited future relationship types… A new relationship type is a new value, never a rewrite"* |
| Materialized instances | **13,361** |
| Inverse modelling | **5,069** edges carry `inverse_of` |

### 7.3 The seven requested attributes, measured against what exists

| Attribute | `edge_id` register (M-C) | Object plane (M-A + M-B) |
|---|---|---|
| source | ✔ `from` | ✔ the object claiming it |
| target | ✔ `to` | ✔ `Relationship.target` |
| relationship type | ✔ `type`, open TitleCase | ✔ `relation`, validated against `uckp.relation-type` |
| **authority** | ✖ not carried | ✔ inherited — the claiming object's `authority` facet |
| **lifecycle** | ✖ not carried | ✔ inherited — the claiming object's `lifecycle` facet |
| **evidence** | ✖ only a free-text `note` | ✔ inherited — Facet 16 |
| **evolution history** | ✖ not carried | ✔ inherited — Facet 18 |

**The object plane supplies all seven; the edge register supplies three.** It supplies four of them *by inheritance* rather than duplication — which is `ART-06` operating as designed: every object carries every facet, so an edge derived from an object inherits the object's authority, lifecycle, evidence and evolution history without restating any of them.

### 7.4 Determination

> **"Relationship" is already a first-class universal entity in this repository — it is a governed category under `ART-02`, a registered `RegistryKind`, a schema-declared first-class edge with an immutable append-only identity, and 13,361 instances exist.**
>
> **`C-1` therefore does not require promoting relationships to first-class status. That has been done.**
>
> **What `C-1` requires is narrower: that the *terms being related* be objects, so that the relation between them is derived from an object rather than authored beside one (`K-8`). That is the act, and it has a precedent for 48 terms across two vocabularies.**

### 7.5 The reservation this determination records

Promoting a relationship to a **separately identified** entity — one with its own `edge_id` distinct from the object claiming it — is exactly what the M-C register does, and it sits in tension with `K-8`. Two conditions are measured, neither created by `C-1`:

- `UEDGE-` ids are produced by `00-BOOK/tools/ukb.py:1031` as `f"UEDGE-{edge_seq[0]:09d}"` — **a sequential counter, not the deterministic mint**.
- `UEDGE-` appears **0 times** in `00-BOOK/DATA/id-ledger.json`.

`CAA-INV-04` recognises a second identity authority *by the counter it advances*. This is recorded as `C1-F-1` (§11) and **not disposed of** — `non_goals[5]`. **Option D does not touch it**, because Option D mints no edge identity: the mapping is a facet of an already-identified object.

---

## 8. Infinite Evolution Validation

The directive requires that a future unknown vocabulary be able to do five things without engine modification, schema rewrite, enum addition or code deployment.

### 8.1 The five capabilities

| # | Capability | Mechanism | Code needed after contribution? |
|---|---|---|---|
| 1 | **Register itself** | `VocabularyRegistry.register(vocabulary)` — *"This is the only extension mechanism"* | **No** |
| 2 | **Define relationships** | `Relationship(relation, target, class)` on the term's object; both ends validated by `require_term` | **No** |
| 3 | **Evolve relationships** | `UCKO.with_relationships(*rels)` — merges by `(relation, target, class)` key, returns a **new** object via `create_from_self()` | **No** |
| 4 | **Supersede relationships** | `uckp.relation-type` contains `supersedes`; `ART-12` makes each transition a new state referencing its parent | **No** |
| 5 | **Preserve historical relationships** | `uckp.relationship-class` contains `historical` — *"a binding that held in a prior state"* — and `future` — *"an intended, not-yet-realised binding"* | **No** |

**All five are already served, and capabilities 4 and 5 are served by vocabulary terms that exist for exactly this purpose.** The presence of `historical` and `future` as relationship classes is direct evidence that relationship supersession and forward declaration were designed for, not overlooked.

### 8.2 The four prohibitions

| Prohibition | Honoured? | Basis |
|---|---|---|
| No engine modification | **Yes, after contribution.** The one-time projection function is code; every subsequent admission is `registry.extend()` | Same one-time-code / permanent-data trade as `CEP-MOD-002` M-1…M-5 |
| No schema rewrite | **Yes** | `LEDGER_SCHEMA` unchanged; `relationship.schema.json` untouched; `type` is open by its own declaration |
| No enum addition | **Yes** | Terms are registry members, not enum members. The enum, where retained, is a checked projection |
| No code deployment | **Yes, for admission** | `extend()` is a runtime call over data |

### 8.3 The `is_extensible()` proof, live

`VocabularyRegistry.is_extensible()` — *"Article 17 is proved, not asserted: a probe term is admitted into a copy of each vocabulary."* Measured **True** at this baseline over 13 vocabularies.

`_probe_infinite_extensibility` (`validation.py:746`) checks three distinct failures: refusal, acceptance-without-admission, and **mutation of the original**. It iterates `vocabularies.vocabulary_ids()`, so **a newly registered vocabulary is covered automatically — no probe edit is required.** This is the strongest single piece of evidence that the mechanism was built for open contribution.

### 8.4 Infinite relationship expansion, specifically

| Population | Terms | Extensible? |
|---|---|---|
| `uckp.relation-type` | 17 | **Yes** |
| `uckp.relationship-class` | 12 | **Yes** |
| `relationship.schema.json` `type` | pattern-constrained, not enumerated | **Yes** — *"unlimited future relationship types… without schema redesign"* |

**Relationship expansion is unbounded on both planes.** This matches `UISD-000001` `ISD-AX-03` (`axis: relationship`, `capacity: unbounded`, measured by `ISD-L-06`) and `ISD-L-02`: *"The relationship type space is pattern-constrained, never enumeration-constrained."*

### 8.5 The unknown-vocabulary walkthrough

A vocabulary nobody has yet conceived, admitted at some future time:

```
1. Its module exposes ucko_objects()                        → ART-08 provider hook
2. registry.discover(<its root>)                            → no engine edit; roots are arguments
3. Its vocabulary is registered                             → VocabularyRegistry.register
4. Its terms project as UCKOs                               → facet_object / evolution_stage_object precedent
5. Its cross-vocabulary bindings are Relationships          → validated by require_lawful, fail-closed
6. derive_edges makes them executable                       → ART-07
7. _probe_infinite_extensibility covers it                  → automatically, no probe edit
8. A later term is admitted by registry.extend()            → DATA, forever
9. A superseded binding uses relation `supersedes`,
   class `historical`                                       → existing terms
10. The prior state is preserved                            → ART-12, ART-14
```

**Ten steps. Zero require a mechanism that does not exist.** Steps 1–6 are one-time per vocabulary; steps 7–10 are permanent.

---

## 9. Authority and Governance Determination

**No authority is invented below. Each row is the located owner or an explicit "not located".**

### 9.1 Relationship semantics — who owns what a relation *means*

| Field | Measured |
|---|---|
| Owner | **`engine/uckp/vocabulary.py`** — `RELATION_TYPE_VOCABULARY` (17 terms) and `RELATIONSHIP_CLASS_VOCABULARY` (12 terms) |
| Constitutional superior | `UCKP-ART-07`; `CAA-INV-05` — *"One instrument declares what a relationship is, and every relationship kind any projection emits binds to a class and an article of that model"* |
| Standing | Layer Zero, under `ART-17` |
| Second claimant? | **None located** in the object plane |

### 9.2 Relationship admission — who may admit a new relation type

| Field | Measured |
|---|---|
| Mechanism | `VocabularyRegistry.extend(vocabulary_id, term)` — *"This is the only extension mechanism"* |
| Rule | `how_to_extend[2]` — *"A new vocabulary member, **relationship class**… is one appended entry in DATA"* |
| Constitutional act required | **None** |
| Declared party | **NOT LOCATED.** The register names a *mechanism*, not a party. This is the same shape as the `AG-2b` finding — a mechanism is declared where a role would be needed |

### 9.3 Relationship validation — who checks

| Layer | Owner |
|---|---|
| Term admissibility | `UCKO.require_lawful` → `require_term(RELATION_TYPE / RELATIONSHIP_CLASS)`, fails closed |
| Executability | `UniversalKnowledgeGraph.dangling()` — `ART-07` |
| Acyclicity of authority | `CircularAuthorityError`, class-scoped — `INV-06` |
| Projection alignment | `verify_vocabulary_alignment` — 9 pairs, **live PASS** |
| Invariant reach | `_probe_infinite_extensibility` — `INV-14` |
| Knowledge-plane checks | `RelationshipsResolvedCheck`, `RelationshipsNavigableCheck` |
| **Edge register (M-C)** | **NOT VALIDATED.** `ISD-G-04`: *"relationship edges are materialized and no gate validates them against `relationship.schema.json`"* — measured at this baseline as **13,361** edges |

### 9.4 Relationship evolution — who owns change over time

| Field | Measured |
|---|---|
| Article | `ART-12` — every transition creates a new state referencing its parent |
| Mechanism | `UCKO.with_relationships` → `create_from_self()` |
| Supersession vocabulary | `supersedes` (relation) · `historical`, `future` (classes) |
| Transaction owner | `UAUE-000001` `AUE-P-11` — claims `state-transition` and `continuation` |
| Append-only guarantee | `ART-14`; no removal operation on `VocabularyRegistry` |

### 9.5 Ownership determination

> **Relationship semantics, admission, validation and evolution are all owned, and every owner is located. No authority needs inventing to close `C-1`.**
>
> **Two owner-level gaps are recorded, neither created by `C-1`:** no *party* is declared for relationship-vocabulary admission (§9.2), and the M-C edge register is ungated (§9.3, `ISD-G-04`).

### 9.6 The decisions that remain, and whose they are

| # | Decision | Kind | Why not engineering |
|---|---|---|---|
| `D-a` | Which `uckp.relation-type` term expresses `EntityKind → CapabilityGroup`? | **Declaration** | States what the binding means. `REPOSITORY_INTELLIGENCE_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"` — it may implement a declared criterion, not define one |
| `D-b` | Which term expresses `CapabilityGroup → PortalSection`? | **Declaration** | Same |
| `D-c` | Are the platform roots added to `DEFAULT_DISCOVERY_ROOTS`, or passed per call site? | **Ownership** | A discovery-scope decision affecting every universe build |
| `D-d` | Disposition of `C1-F-1` (edge-id counter) and `C1-F-2` (relation-type divergence) | **Owner / referral** | Pre-existing; `non_goals[5]` forbids disposing here |

---

## 10. Migration / Evolution Path

**Stated as sequence and dependency only. Nothing below is authorised by this determination.**

### 10.1 Prerequisite — already satisfied

| Prerequisite | Status |
|---|---|
| `verify_vocabulary_alignment` exists | **DONE** — `CEP-MOD-002` M-0a; live PASS over 9 pairs |
| A term-projection precedent exists | **DONE ×2** — 33 facets, 15 stages |
| Relation and class vocabularies exist and are open | **DONE** — 17 and 12 terms |
| Identity mint is open to future kinds | **DONE** — `register_kind`, 29 core kinds |
| `INV-14` reaches new vocabularies automatically | **DONE** — no probe edit needed |

**`CEP-MOD-002`'s blocking prerequisite (M-0) is discharged.** `C-1` inherits a built substrate.

### 10.2 Path

| Step | Act | Depends on | Disposition |
|---|---|---|---|
| `C1-S1` | Contribute the `EEG-1`/`EEG-2` term sets (`M-6`…`M-8` of the predecessor) | — | **REUSE** |
| `C1-S2` | Decide `D-a`, `D-b` — the relation and class terms per mapping | `C1-S1` | **DECLARATION** |
| `C1-S3` | Project the terms as UCKOs via a provider exposing `ucko_objects()` | `C1-S1` | **EXTEND** — precedent ×2 |
| `C1-S4` | Express each mapping as a `Relationship` on the source term's object | `C1-S2`, `C1-S3` | **REUSE** |
| `C1-S5` | Decide `D-c` — discovery-root scope | `C1-S3` | **OWNERSHIP** |
| `C1-S6` | Retire the Python `dict` literals in favour of the derived mapping | `C1-S4`, `C1-S5` | **EXTEND** |

**`CREATE` count: 0.**

### 10.3 Backward compatibility

| Mechanism | Effect |
|---|---|
| Append-only extension | No existing term altered; no consumer breaks |
| Retained projection | The `dict` remains a derived view until `C1-S6`; no caller moves |
| Additive projection | 33 facet and 15 stage terms coexist with 6,338 nodes today — the pattern is proven non-disruptive at scale |
| Edge derivation | `derive_edges` is total and deterministic; new edges appear, none change |

### 10.4 Rollback

| What | Reversible? |
|---|---|
| A candidate vocabulary in a private registry | **Fully** — *"Callers that need to admit a term without affecting the whole universe build their own registry"* |
| A projection function before discovery includes its root | **Fully** — an undiscovered provider contributes nothing |
| Consuming code | **Yes** — the `dict` remains until `C1-S6` |
| A registration into the process-wide registry | **No** — no removal operation, by `ART-14` |

**The acceptance boundary is the discovery root (`C1-S5`), not the projection function.** A provider that exists but is not discovered is inert — a stronger rollback position than `CEP-MOD-002` had, where registration at import was the boundary.

### 10.5 Replay and determinism

| Aspect | Impact |
|---|---|
| `derive_edges` | Deterministic and total; edges sorted by `key()` |
| Node count | Rises by the number of projected terms |
| Universe digest | **Moves** — expected and auditable under `INV-17` |
| Vocabulary registry digest | **Moves** from `7d733fcc2e5551f1` |
| Existing edges | **Unchanged** — derivation from existing objects is untouched |

---

## 11. Risks and Remaining Constraints

| Id | Severity | Finding | Owner | Source |
|---|---|---|---|---|
| `C1-F-1` | **HIGH** | **The edge register advances its own counter.** `edge_id` is produced at `00-BOOK/tools/ukb.py:1031` as `f"UEDGE-{edge_seq[0]:09d}"` — sequential, not `deterministic_id`. `UEDGE-` appears **0 times** in `id-ledger.json`, while `RegistryKind.RELATIONSHIP` exists and mints `UCOS-REL-…`. `CAA-INV-04` recognises a second identity authority **by the counter it advances**. **Pre-existing; Option D does not touch it and mints no edge identity** | UKB / identity authority | **Measured here** |
| `C1-F-2` | **HIGH** | **Two relation-type vocabularies coexist with partial overlap.** `uckp.relation-type` holds 17 lower-case-hyphen terms; the edge register uses 16 TitleCase types. After case-folding, **4 overlap** (`consumes`, `depends-on`, `implements`, `references`), **12 are register-only** (incl. 6 explicit inverses: `required-by`, `consumed-by`, `authorized-by`, `implemented-by`, `referenced-by`, `evolves-from-inverse`), **13 are vocabulary-only** (incl. `governs`, `owns`, `supersedes`, `certifies`). `CAA-INV-05` requires *one* instrument declaring what a relationship is | relationship-model owner | **Measured here** |
| `C1-F-3` | MEDIUM | **The edge register is ungated.** 13,361 edges materialized and no gate validates them against `relationship.schema.json`. (`ISD-G-04` recorded 12,899; the figure has moved) | UKB / relationship owner | **Carried from `UISD-000001`, count re-measured** |
| `C1-F-4` | LOW | **No party is declared for relationship-vocabulary admission.** `how_to_extend[2]` names a *mechanism*; no role. Same shape as the `AG-2b` finding | not located | **Measured here** |

### 11.1 Why `C1-F-1` and `C1-F-2` do not block Option D

Both concern the **M-C edge register**, a plane Option D neither uses nor extends. Under Option D a mapping is a **facet of an already-identified object**: it mints no `edge_id`, adds no register row, and advances no counter. The two findings are reported because they sit on the same axis and a future determination that chose M-C as the mapping home would meet them head-on — not because they gate this one.

### 11.2 Constraints that persist after `C-1` closes

| Constraint | Persists | Why it is correct |
|---|---|---|
| `Vocabulary` still cannot represent an inter-vocabulary relation | **Yes** | It is not that plane's subject. §6.2 |
| Registration remains irreversible | **Yes** | `ART-14` |
| A term must be projected as an object before it can carry a relation | **Yes** | `K-8` — edges are derived from objects |
| Relation semantics remain Layer Zero's | **Yes** | `CAA-INV-05` |
| `_SURFACE_TABLE`'s title half is not a relation | **Yes** | It is `Term.definition` — §6.3 |

### 11.3 The single largest risk to a correct implementation

**Projecting terms as objects without a class-correct relation.** `graph.py` states the reason classes exist: *"'is authority acyclic?' is a question about one class, and asking it of all edges at once would be meaningless."* An `EntityKind → CapabilityGroup` edge misclassed as `knowledge` rather than `authority` would silently exempt itself from `INV-06`'s acyclicity check. This is why `D-a` and `D-b` are declaration decisions (§9.6) and not engineering ones.

---

## 12. Acceptance Criteria

`C-1` is closed when **all twelve** hold. Each is measurable.

| # | Criterion | Measured by | Status now |
|---|---:|---|---|
| `AC-01` | Every `EEG-1`/`EEG-2` term set is registered in `VocabularyRegistry` | `vocabulary_ids()` count rises 13 → 17 | **NOT MET** |
| `AC-02` | `is_extensible()` remains `True` | `VocabularyRegistry.is_extensible()` | **MET** (13/13) |
| `AC-03` | `_probe_infinite_extensibility` reports zero findings over the widened set | `INV-14` probe | **MET** for current 13 |
| `AC-04` | Every contributed vocabulary has an alignment pair; `verify_vocabulary_alignment` passes | 9 pairs → 10+ | **MET** for current 9 |
| `AC-05` | Each mapped term is a UCKO reachable in the graph | `node_ids()` | **MET** for 48 terms (33 facets + 15 stages); **NOT MET** for the mapped sets |
| `AC-06` | Every mapping edge carries a registered `relation` **and** `relationship_class` | `require_lawful` fails closed | **Mechanism MET** |
| `AC-07` | `dangling()` returns empty for the new edges | `UniversalKnowledgeGraph.dangling()` | **NOT MEASURED** |
| `AC-08` | No mapping is authored anywhere but on the claiming object | `K-8`; `derive_edges` is the sole edge source | **MET by construction** |
| `AC-09` | The Python `dict` literals are derived, not authoritative | Source inspection after `C1-S6` | **NOT MET** |
| `AC-10` | No new registry, mint, authority, gate or relationship model exists | Count of each | **MET** — Option D creates none |
| `AC-11` | `verify.sh` stage count unchanged at **16** | `grep -c 'run_stage "'` | **MET** |
| `AC-12` | A synthetic unknown term admits through the full path and is refused before registration | The `is_extensible()` / `require()` pair | **Mechanism MET** |

**Met now: 7 · Met by mechanism: 2 · Not met: 3 · Not measured: 1.**

**Every unmet criterion is unmet because the migration has not run — not because a mechanism is missing.**

---

## 13. Final Determination

### 13.1 Verdict

> # CONDITIONALLY RESOLVED

### 13.2 What is resolved, and what the condition is

**RESOLVED — the representation question, completely.**

Inter-vocabulary mappings have a permanent constitutional home: the **object plane**. A vocabulary term is projected as a UCKO by a provider; the mapping is a `Relationship` on that object, its `relation` a term of `uckp.relation-type` and its `relationship_class` a term of `uckp.relationship-class`, both validated by `require_lawful` and both failing closed; `derive_edges` makes it executable. **Twelve of twelve criteria pass. Options A, B, C-i, C-ii and E are rejected on measured constitutional grounds. `CREATE` count is zero.** The pattern is not proposed — it is running, for 48 terms across two vocabularies, at this baseline.

**CONDITIONAL — on three things, none of which is a missing mechanism.**

| Condition | Kind | § |
|---|---|---|
| `D-a`, `D-b` — the relation and class term for each mapping | **Declaration decision.** Engineering may implement a declared criterion, not define one | §9.6 |
| `D-c` — discovery-root scope for the platform providers | **Ownership decision** | §9.6 |
| `AC-01`, `AC-05`, `AC-07`, `AC-09` | **Not yet executed** — the migration has not run | §12 |

**Why not `PERMANENTLY RESOLVED`:** three acceptance criteria are unmet and one unmeasured, and two decisions belong to owners this determination may not speak for. Declaring permanence while `AC-05`, `AC-07` and `AC-09` are open would be a claim beyond measurement.

**Why not `NOT RESOLVED`:** the architecture is determined, complete, precedented twice, and requires nothing to be built. The obstacles are decisions and execution, not representation.

### 13.3 The four explicit questions

> **Can `C-1` be closed permanently without creating any of the following?**

| # | Thing | Answer | Measured basis |
|---|---|---|---|
| 1 | **A new parallel framework** | **NO — none required.** | Option D reuses `VocabularyRegistry`, `UCKO`, `Relationship`, `derive_edges`, `UniversalKnowledgeGraph` and `require_lawful`, all unchanged. `what_this_forbids` names *"relationship graph"* explicitly; none is created |
| 2 | **A duplicate registry** | **NO — none required.** | Two registries are used, both existing: `VocabularyRegistry` (13 vocabularies) and `UniversalKnowledgeRegistry` (6,338 objects). No third |
| 3 | **A temporary workaround** | **NO — none required.** | Every step is `REUSE` or `EXTEND` of a located owner. Nothing is time-boxed or conditioned on later cleanup. The one-time projection function is the same permanent-data trade `CEP-MOD-002` made five times |
| 4 | **A hardcoded exception** | **NO — none required.** | The path is uniform: project the term, class the relation, derive the edge. `_SURFACE_TABLE`'s title half needs no exception either — it is `Term.definition`, an existing field |

**Four of four: NO.**

### 13.4 Consequence for `EEG-1` and `EEG-2`

The predecessor recorded *"six of eight admission paths become permanently data; two remain code."* With `C-1`'s representation determined, **the two remaining paths have a located, compliant, precedented representation.**

| Admission | Predecessor | After this determination |
|---|---|---|
| Binding an entity kind to its authorizing group | *"Yes — code required, until C-1 resolves"* | **Data**, conditional on `D-a` |
| Binding a capability group to its section and title | *"Yes — code required, until C-1 resolves"* | **Data** (relation) + **`Term.definition`** (title), conditional on `D-b` |

**Eight of eight admission paths reach the target state**, conditional on two declaration decisions and one ownership decision — none of which requires a constitutional act, and none of which is blocked.

### 13.5 Correction of record

This determination reverses the predecessor's §8.5 disposition of `C-1` from **BLOCKED** to **RESOLVED-CONDITIONAL**. The reversal rests on one measurement error, stated in §2.4: the predecessor probed bare term ids against `node_ids()` and concluded terms are not graph nodes. Terms are projected under URN local names; 48 of them are nodes at the same baseline. The premise that `Vocabulary` cannot represent an inter-vocabulary relation was and remains correct — the inference that the repository therefore cannot was not.

`CEP-MOD-002` §12.2's referral is now discharged: **the mapping half belongs to the object plane**, which is a stronger home than the Configuration candidate it named, on every one of the twelve criteria.

### 13.6 What this determination did not do

| Not done | Under |
|---|---|
| Create any mapping | Directive; `non_goals` |
| Select the relation term for either mapping | §9.6 — a declaration act |
| Modify code, JSON, registries, identities, ownership or certification | Declared mode |
| Dispose of `C1-F-1`…`C1-F-4` | `non_goals[5]` |
| Authorise `C1-S1`…`C1-S6` | No authority held |
| Amend any article, invariant or stop condition | `non_goals[3]` |

---

## 14. Verification Record

### 14.1 Before / after

| Field | Before | After | Delta |
|---|---|---|---|
| HEAD | `bae59755d7e2d3566c93b89c722b68847145269a` | `bae59755d7e2d3566c93b89c722b68847145269a` | **unchanged** |
| Branch | `integration/recovery-001` | `integration/recovery-001` | **unchanged** |
| `git status --porcelain` | **360** | **361** | **+1 — this artifact** |
| Tracked modifications | **38** | **38** | **unchanged** |
| Staged | **0** | **0** | **unchanged** |
| Untracked | **322** | **323** | +1 |
| Commits | **0** | **0** | **none** |

### 14.2 Required post-write assertions

| Assertion | Result |
|---|---|
| Only one new artifact exists | **VERIFIED** — porcelain +1, the artifact alone |
| HEAD unchanged | **VERIFIED** |
| Branch unchanged | **VERIFIED** |
| Code unchanged | **VERIFIED** — tracked modifications 38, unchanged |
| Registry unchanged | **VERIFIED** — no `00-BOOK/DATA/*` or `00-CMG/*` in the delta |
| Identity unchanged | **VERIFIED** — `id-ledger.json` not in the delta; no mint called for persistence |
| Ownership unchanged | **VERIFIED** — no ownership record touched |
| Certification unchanged | **VERIFIED** — no certificate issued or altered |
| No commits | **VERIFIED** — staged 0, HEAD unchanged |

### 14.3 Live measurements taken

| Measurement | Method | Result |
|---|---|---|
| Vocabulary registry state | `build_vocabulary_registry()` + `digest()` | 13 · 204 terms · extensible · `7d733fcc2e5551f1` |
| Terms carrying `successors` | Iteration over all 13 | **17** |
| `verify_vocabulary_alignment()` | Direct call | **PASS** over 9 projections |
| Universe nodes / edges | `build_universe().graph()` | **6,338** / **13,036** |
| Edge classes and relations | `Counter` over edges | 6 classes · 8 relations |
| Vocabulary UCKO nodes | Node-id filter | **13 of 13** |
| Stage term UCKOs | Node-id filter | **15**, plus 1 unrelated `UCOS-STAGE0-…` |
| A stage object's facet bindings | `g.node(...)` inspection | kind `pattern` · category `transition` · tier `architectural` · lifecycle `implemented` · 2 relationships |
| `uckp.relation-type` ∩ register types | Case-folded set ops | 4 overlap · 12 register-only · 13 vocabulary-only |
| Edge register | JSON parse | **13,361** edges · 16 types · 5,069 with `inverse_of` · `count` consistent |
| `edge_id` producer | `grep` | `ukb.py:1031` — sequential counter |
| `UEDGE-` in id-ledger | `grep -c` | **0** |
| `RegistryKind` members | Import | **29**, including `RELATIONSHIP` |
| Deterministic mint samples | `deterministic_id(...)` | `UCOS-REL-99790c515fc3` · `UCOS-LOC-0da89ce1be0a` |
| `DEFAULT_DISCOVERY_ROOTS` | Source read | `("engine.uckp",)` |
| `require_term` call sites | `grep` | 6 in `ucko.py` · 1 in `assimilation.py` · 1 in `nucleus/registry.py` |
| `relationship` in `GOVERNED_CATEGORIES` | Import | **True** (1 of 35) |

### 14.3.1 Note on read-only universe construction

`build_universe()` was called in-process to inspect nodes and edges. It is a pure assembly over declared providers — `vocabulary_object`, `facet_object`, `article_object` and the UGA projection — and writes nothing: `persistence_base` was left `None` and no `to_document()` output was saved. `git status --porcelain` was **360** before and after these calls, confirming no side effect on the working tree.

### 14.4 What was not verified

| Not verified | Why |
|---|---|
| That an implemented `C1-S3` passes `verify.sh` | Would require implementing it. Out of mode |
| `AC-07` — `dangling()` over edges that do not exist yet | Cannot be measured before the edges exist |
| Whether `D-a`/`D-b` should be `governs`, `depends-on` or another term | A declaration act, not a measurement (§9.6) |
| Whether `C1-F-1` constitutes an actual `CAA-INV-04` breach | Requires the identity authority's disposition; `non_goals[5]` |
| Whether `M-D` and `M-E` are `ART-03` duplicates of `M-A` | Out of `C-1`'s scope. Measured as present, not adjudicated |
| Current `verify.sh` verdict at HEAD | Not executed — `ISD-G-11` records the full pipeline mutates tracked surfaces, which this mode forbids |
| That the five relationship mechanisms are the complete set | `grep` over `class Relationship` found 5 plus 4 error types. A mechanism not matching that name would not have been seen |

### 14.5 Artifact creation verified

| Check | Result |
|---|---|
| File exists | **Yes** — `UCOS-OMEGA-INFINITY-C-1-INTER-VOCABULARY-MAPPING-REPRESENTATION-DETERMINATION.md` |
| Required sections | **14 of 14, in the specified order** |
| Verdict | **Exactly one of the three permitted values — `CONDITIONALLY RESOLVED`** |
| Four explicit questions answered | **Yes — §13.3, all four NO** |
| Git status | `??` untracked — the only delta from 360 |
| Other files changed | **0** |
| Commits | **0** |

---

**End of determination.**

| Field | Value |
|---|---|
| Baseline | `bae59755d7e2d3566c93b89c722b68847145269a` · `integration/recovery-001` |
| Sections | 14 |
| Subject | `C-1` |
| Options evaluated | **5** against **12** criteria |
| Options rejected | **4** (A · B · C · E) |
| Option selected | **D — existing three-layer pattern** |
| Constitutional constraints applied | **12** |
| Relationship mechanisms located | **5** |
| Term-projection precedents | **2** (48 terms) |
| Cross-vocabulary bindings per UCKO | **6** |
| Findings raised | **4** — 2 HIGH · 1 MEDIUM · 1 LOW |
| Predecessor measurements corrected | **1** |
| New frameworks · registries · workarounds · exceptions | **0 · 0 · 0 · 0** |
| `CREATE` acts | **0** |
| Code changed | **0 files** |
| Registries changed | **0** |
| **Verdict** | **CONDITIONALLY RESOLVED** |
