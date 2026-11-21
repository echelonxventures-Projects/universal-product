# UCOS Ω∞ — D-a / D-b RELATION TERM AUTHORITY DETERMINATION

**Which authority owns relation semantics, and whether relationships have one identity authority. The measured answer is that semantic authority for the object plane is located, sole and already legislated — and that across the repository as a whole there are three relation-term planes holding 73 distinct terms, and no plane records a relationship identity in the one ledger.**

| Field | Value |
|---|---|
| Artifact | `UCOS-OMEGA-INFINITY-D-A-D-B-RELATION-TERM-AUTHORITY-DETERMINATION.md` |
| Authority | **NONE — DERIVED DETERMINATION.** Declares no relation term, selects no term for any mapping, mints no identity, registers nothing, deprecates nothing, implements nothing. It locates existing authorities and measures the terms they hold. |
| Mode | ANALYSIS ONLY · **NO CODE · NO REGISTRY · NO RELATIONSHIP DATA · NO IDENTITY · NO OWNERSHIP · NO CERTIFICATION · NO COMMIT** |
| Baseline commit (HEAD) | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Baseline branch | `integration/recovery-001` |
| Subject | `D-a` / `D-b` — the relation and class term for the two `EEG-2` mappings — plus `C1-F-1` (relationship identity) and `C1-F-2` (relation vocabulary overlap) |
| **Governing prior determination** | **`UCRD-001-CONSTITUTIONAL-RELATIONSHIP-DETERMINATION.md`.** It legislates the three-tier model and names the Tier-3 owner. Where this determination and `UCRD-001` disagree, **`UCRD-001` governs** — the same subordination `UNIVERSAL-RELATIONSHIP-INTELLIGENCE-FOUNDATION-DETERMINATION.md` declares of itself |
| Method | Read-only measurement at one commit: direct import of `RELATION_TYPE_VOCABULARY`, `RelationType`, `RELATIONSHIP_TYPES`, `RegistryKind`; JSON parses of `CMG-REGISTRY.json`, `relationships.json`, `relationship.schema.json`, `id-ledger.json`; regex classification of all **6,413** ledger ids; source reading of `ukb.py::add_edge`, `allocate`, `allocate_execution` |
| **Central finding** | **Semantic authority for the object plane is not in doubt and needs no determination — `UCRD-001` already legislated it.** `RELATION_TYPE_VOCABULARY` (17 terms) is the Tier-3 owner; `RELATIONSHIP_CLASS_VOCABULARY` (12) is Tier-2. `D-a`/`D-b` draw from these and nowhere else — §7 |
| **Second finding** | **73 distinct relation terms exist across three declaring planes. Exactly 3 appear in all three** — `certifies`, `depends-on`, `supersedes`. Three case conventions, 31 alias tokens, 28 declared-but-never-materialized types — §3 |
| **Third finding — C1-F-1 refined** | **My earlier framing was imprecise.** The ledger's own authority *is* a sequential counter (`category_seq`), so "sequential" was never the defect. Measured: the ledger holds **6,413 ids, 100% `UCOS-<CAT>-NNNNNN`, 0% deterministic-shape**, and `UEDGE-` is **positional over unsorted iteration order** — §4, §8 |
| **Fourth finding** | **A `Term` cannot be deprecated or superseded in place.** It has five fields and no lifecycle. Term supersession requires the object plane — which is exactly `C-1`'s Option D — §9.4 |
| Options evaluated | **A · B · C · D · E** — §6 |
| **Selected** | **Option A, as already legislated by `UCRD-001`**, with `RegistryKind.RELATIONSHIP` supplying identity — §7.1 |
| **Verdict** | **CONDITIONALLY RESOLVED** — §14 |

---

## 1. Current Baseline

### 1.1 Captured before writing

| Field | Value |
|---|---|
| HEAD | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch | `integration/recovery-001` |
| `git status --porcelain` | **361** |
| Tracked modifications | **38** |
| Staged | **0** |
| Untracked | **323** |

### 1.2 Measured substrate

| Surface | Value |
|---|---|
| `uckp.relation-type` | **17** terms |
| `uckp.relationship-class` | **12** terms |
| `engine/knowledge/model.py::RelationType` | **17** enum members |
| `00-BOOK/tools/config.py::RELATIONSHIP_TYPES` | **22** types · **44** with inverses · **31** normalized alias tokens |
| `00-CMG/CMG-REGISTRY.json::relationship_types` | **16** entries · **30** with inverses |
| `00-BOOK/DATA/relationships.json` | **13,361** edges · **16** distinct types |
| `00-BOOK/SCHEMAS/relationship.schema.json` | pattern-constrained `type`, **no `enum`** |
| `RegistryKind` | **29** members, `RELATIONSHIP` → code `REL` |
| `00-BOOK/DATA/id-ledger.json` | **6,413** ids across `by_path` (1,492) · `by_object` (4,914) · `by_observation` (7) |

---

## 2. C-1 Outcome Review

### 2.1 What `C-1` established

| `C-1` finding | Status |
|---|---|
| Inter-vocabulary mappings live on the **object plane** | Stands |
| A term projected as a UCKO carries the mapping as a `Relationship` facet | Stands |
| `require_lawful` validates `relation` against `uckp.relation-type` and `relationship_class` against `uckp.relationship-class`, both fail-closed | **Re-verified** — `ucko.py:391-397` |
| Terms are already projected: 33 facets, 15 stages | Stands |
| `RegistryKind.RELATIONSHIP` exists and mints `UCOS-REL-…` | **Re-verified** — `identity.py:141` |
| `C-1` verdict | `CONDITIONALLY RESOLVED`, conditional on `D-a`, `D-b`, `D-c` |

### 2.2 What `C-1` left to this determination

> *"This determination **does not select** the relation term for either mapping… Choosing among them states what the binding *means*, which is a declaration act, not a measurement."*

**This determination does not select them either, and the reason has sharpened**: §7 shows the selection authority is located, sole and already legislated, and it is not this artifact.

### 2.3 A prior determination this chain had not read

`UCRD-001-CONSTITUTIONAL-RELATIONSHIP-DETERMINATION.md` and `UNIVERSAL-RELATIONSHIP-INTELLIGENCE-FOUNDATION-DETERMINATION.md` both predate this chain and both address relation-term authority directly. Neither was cited by the `EEG` or `C-1` determinations.

`UCRD-001` legislates the model; the Relationship Intelligence determination subordinates itself to it explicitly: *"where this determination and `UCRD-001` disagree, `UCRD-001` governs."* **This determination adopts the same subordination.** Under `ART-18`, locating them is the required first act, and it materially reduces what remains open.

### 2.4 What `UCRD-001` already determined

`engine/uckp/facets.py:8-13`, quoted by `UCRD-001` as *"the single most load-bearing passage"*:

> *"The enumeration is **closed on purpose** while the **vocabularies inside** facets are **open**. Adding a thirty-fourth facet is a **constitutional amendment**… Adding a new knowledge kind, authority tier, persistence technology or **relationship class** is **registration**, and registration must never require an amendment."*

| Tier | Subject | Cardinality | Growth | Authority |
|---|---|---|---|---|
| **1 · Facet** | The question every object must answer | **33 — CLOSED** | **Amendment** | `UCKP-ART-06`; `facets.py:23-58` |
| **2 · Relationship class** | The register a binding belongs to | **12 — OPEN** | **Registration** | `RELATIONSHIP_CLASS_VOCABULARY`, `vocabulary.py:304-323` |
| **3 · Relation type** | **How one object is bound to another** | **17 — OPEN** | **Registration** | `RELATION_TYPE_VOCABULARY`, `vocabulary.py:280-302` |

`UCRD-001` §5.1 disposition 10: *"Any new relationship class or relation type — **REGISTRATION, never amendment**."* `CREATE` count: 0.

**Tier 3 is `D-a`/`D-b`'s authority, and it was settled before this chain began.**

---

## 3. Relation Vocabulary Inventory

### 3.1 The declaring planes

| Plane | Owner | Terms | +Inverses | Case convention | Openness mechanism |
|---|---|---|---:|---|---|
| **P1** | `engine/uckp/vocabulary.py::RELATION_TYPE_VOCABULARY` | **17** | — | `lower-hyphen` | `VocabularyRegistry.extend` |
| **P1′** | `engine/knowledge/model.py::RelationType` | **17** | — | `lower-hyphen` | **CLOSED enum** — a checked projection of P1 |
| **P2** | `00-BOOK/tools/config.py::RELATIONSHIP_TYPES` | **22** | **44** | `TitleCase-Hyphen` | append, **or `RELATES <Type>` with zero edit** |
| **P3** | `00-CMG/CMG-REGISTRY.json::relationship_types` | **16** | **30** | `UPPER-HYPHEN` | append — absent from `closed_enumerations` |
| **P4** | `data/relationship_meta.py::RelationshipKind` | **3** kinds | — | TitleCase | open on free-text `type_tag` |

### 3.2 Total relation terms

| Measure | Value |
|---|---|
| **Total distinct terms, case-folded, P1 ∪ P2 ∪ P3** | **73** |
| P1 exclusive | **7** — `equivalent-to`, `generated-from`, `governs`, `inherits`, `owns`, `related-to`, `validates` |
| P2 exclusive | **31** |
| P3 exclusive | **20** — `amends`, `composes`, `confers-authority-on`, `delegates-to`, `derives-authority-from`, `interprets`, `orthogonal-to`, `owns-for`, `ratifies`, `refines`, `subordinate-to`, `superior-to` and their inverses |
| **Present in all three planes** | **3** — `certifies`, `depends-on`, `supersedes` |

### 3.3 Case-fold collisions

| Pair | Count | Terms |
|---|---:|---|
| P1 ∩ P2 | **8** | `certifies`, `consumes`, `depends-on`, `derived-from`, `implements`, `produces`, `references`, `supersedes` |
| P1 ∩ P3 | **5** | `certifies`, `conflicts-with`, `depends-on`, `extends`, `supersedes` |
| P2 ∩ P3 | **8** | `certified-by`, `certifies`, `depends-on`, `required-by`, `superseded-by`, `supersedes`, `traced-from`, `traces-to` |

**Every collision is a pure case/format difference over an identical concept.** No two planes assign conflicting meanings to the same normalized token — measured, not assumed.

### 3.4 Aliases

**Aliases exist and are a declared, first-class mechanism — on P2 only.**

| Measure | Value |
|---|---|
| Alias-carrying types | **22 of 22** |
| Total alias labels | **40** (all distinct) |
| Normalized alias tokens | **31** |
| Freeform label | `RELATIONSHIP_FREEFORM_LABEL = "RELATES"` |

Examples: `Consumes` ← `CONSUMES`, `USES`, `READS` · `Authorized-By` ← `AUTHORITY`, `AUTHORITIES`, `AUTHORIZED-BY`, `GOVERNED-BY` · `Implements` ← `IMPLEMENTS`, `REALIZES`.

**Alias/canonical clash test: ZERO.** Every alias token that is also a P1 canonical term maps to the P2 type of the same meaning — all 8 of `certifies`, `consumes`, `depends-on`, `derived-from`, `implements`, `produces`, `references`, `supersedes`. **No token means one thing on P1 and another on P2.**

*(I expected `GOVERNED-BY` → `Authorized-By` to clash with P1's `governs`. Measured: it does not — `governed-by` is not a P1 term. Reported because the hypothesis was tested and failed.)*

**P1 has no alias mechanism at all.** `Term` has five fields — `term_id`, `definition`, `rank`, `successors`, `symmetric` — and none carries a synonym.

### 3.5 Deprecated terms

| Plane | Deprecation support | Measured |
|---|---|---|
| P1 | **None.** `Term` has no lifecycle field | 0 deprecated terms |
| P2 | **None declared** | 0 |
| P3 | 5 occurrences of `deprecat*` in `CMG-REGISTRY.json`, none on a `relationship_types` entry | 0 deprecated relation types |

**No relation term is deprecated anywhere, and no plane can express that a term is.** §9.4 determines why and where it would live.

### 3.6 Unmapped and unmaterialized terms

| Measure | Value |
|---|---|
| Materialized types not declared in P2 | **0** — the register is fully consistent with its config |
| P2 terms declared but never materialized | **28 of 44** |
| P1 terms with no P2 or P3 counterpart | **7** |
| P3 terms with no P1 or P2 counterpart | **20** |

`UCRD-001`'s Relationship Intelligence companion reads the 28 correctly: *"A vocabulary that can hold a registered-and-unused member is registration-driven, not usage-derived — **the strongest available evidence that the set is open**."*

### 3.7 Semantic overlaps

Distinct strings naming one concept. These are **not** case-fold collisions and no mechanism detects them.

| # | Terms | Planes | Concern |
|---|---|---|---|
| `SO-1` | `Evolves-To`/`Evolved-From` **and** `Evolves-From`/`Evolves-From-Inverse` | P2 internal | Two type pairs for one direction of one concept; `Evolves-From-Inverse` is a generated name, not an authored one |
| `SO-2` | `Supersedes`/`Superseded-By` **and** `Replaced-By`/`Replaces` | P2 internal | Two pairs for supersession |
| `SO-3` | `owns` (P1) **and** `OWNS-FOR` (P3) | P1/P3 | `UCRD-001`: `owns` = *"is accountable for"*; `OWNS-FOR` is `DELEGATES-TO`'s inverse — related, not identical |
| `SO-4` | `inherits` (P1) **and** `INHERITS-FROM` (P3) | P1/P3 | Same concept, different string; escapes case-folding |
| `SO-5` | `derived-from` (P1), `Derived-From` (P2), `DERIVES-AUTHORITY-FROM` (P3) | all | P3's is authority-scoped; P1/P2 are general |

**Five semantic overlaps, three of them within a single plane.** §9 determines the disposition.

---

## 4. Identity Authority Analysis

### 4.1 The three id-producing mechanisms

| # | Mechanism | Shape | Allocation | In the ledger? |
|---|---|---|---|---|
| `I-1` | `ukb.py::allocate` / `allocate_execution` | `UCOS-<CAT>-NNNNNN` | **Sequential** via `ledger["category_seq"]` | **YES — 6,413** |
| `I-2` | `engine/registry/universal/identity.py::deterministic_id` | `UCOS-<CODE>-<12hex>` | **Derived** — SHA-256 over `(code, namespace, natural_key)` | **NO — 0** |
| `I-3` | `ukb.py::add_edge` | `UEDGE-NNNNNNNNN` | **Sequential** via a build-local `edge_seq` | **NO — 0** |

### 4.2 Ledger composition, measured

Classifying all **6,413** ids in `by_path`, `by_object` and `by_observation`:

```
UCOS-<CAT>-NNNNNN   (sequential)     : 6,413   (100.0%)
UCOS-<CODE>-<12hex> (deterministic)  :     0   (  0.0%)
other shapes                         :     0
UEDGE-* present                      :   False
```

Ledger planes: `by_path`, `by_object`, `by_observation`, plus `history`, `page_cursor`, `category_seq`, `volume_seq`, `discovered_volumes`. **There is no edge plane.**

### 4.3 The correction to `C1-F-1`

My `C-1` determination recorded `C1-F-1` as: *"`edge_id` is a **sequential counter**, not `deterministic_id`… `CAA-INV-04` recognises a second identity authority by the counter it advances."*

**That framing was imprecise, and measurement corrects it.** `allocate_execution`'s own docstring states:

> *"Reuses the **ONE identity authority** (the id-ledger `category_seq` counter) and the `UCOS-<CATEGORY>-NNNNNN` convention; keyed by a stable execution key so re-declaration is idempotent."*

**Sequential allocation *is* the one authority's method.** Being a counter is not the defect. Three things are:

| # | Actual defect | Measured |
|---|---|---|
| `d-1` | `edge_seq` is **build-local**, not `ledger["category_seq"]` | `ukb.py:1020` — `edge_seq = [0]` inside the build function |
| `d-2` | Edge ids are **never recorded** in any ledger plane | `UEDGE-` in ledger: **False** |
| `d-3` | Edge ids are **positional over unsorted iteration order** | `edges` is appended in `CHAINS` traversal order; **no `edges.sort` or `sorted(edges)` exists in `ukb.py`** |

### 4.4 Why `d-3` is the decisive one

`I-1` is sequential **and** keyed — `allocate` is keyed by `relpath`, `allocate_execution` by `exec_key` — so re-running returns the same id and the docstring can say *"re-declaration is idempotent"*.

`I-3` is sequential and **keyed by nothing**. `edge_seq` advances in traversal order. Inserting one artifact earlier in `C.CHAINS` shifts every subsequent `edge_id`.

The schema declares `edge_id` as *"Globally unique, immutable, append-only"*. `UCKP-ART-05`: *"An identity, once minted, **never changes**."*

> **Measured: `edge_id` is a positional serial number over an unsorted, content-dependent traversal. It is not an identity, and the schema's claim that it is one is not supported by its producer.**

`I-2` needs no ledger for the opposite reason: a deterministic id is **recomputable from its inputs**, so it is self-certifying. Its absence from the ledger is a design property, not a gap. `I-3` is neither recomputable nor recorded — the only one of the three that is both.

### 4.5 Governing identity law

| Law | Text | Bearing |
|---|---|---|
| `UCKP-ART-05` | *"Every object receives a globally unique, immutable, canonical, persistent identity… **An identity, once minted, never changes.**"* | `d-3` fails this |
| `CAA-INV-04` | *"**One append-only mint** holds every repository identity, every declared map resolves in it, and the derivation into the object model is total and injective over every id it holds."* | `d-2` — edges resolve in no map |
| `UCKP-ART-13` | *"Every digest, identity, proof and decision is computed through one canonical form."* | `d-3` — position is not a canonical form |
| `ukb.py::allocate` | *"Allocating a permanent identifier is an **EVOLUTION** act… Identity is born by intent, never discovered by a checker."* | `add_edge` mints as a **side effect of regeneration** — the pattern `allocate` exists to prevent |

### 4.6 The precedent for the fix

`allocate_execution` shows a ledger plane being added for a new entity class, reusing the one authority:

```python
ledger.setdefault("by_execution", {})
entry = ledger["by_execution"].get(exec_key)
if entry: return entry["execution_id"]
cat = C.EXECUTION_CATEGORY
seq = ledger["category_seq"].get(cat, 0) + 1
```

**Keyed, idempotent, append-only, under the one counter.** A relationship plane would take the identical shape, keyed by `(from, to, type)` — which `add_edge` **already computes** as its dedup key at `ukb.py:1024`.

---

## 5. Semantic Authority Analysis

### 5.1 Who owns what a relation means

| Question | Owner | Basis |
|---|---|---|
| What relation types may an **object** claim? | **`RELATION_TYPE_VOCABULARY`** (17) | `UCRD-001` Tier 3; enforced by `ucko.py:396` |
| What register does a binding belong to? | **`RELATIONSHIP_CLASS_VOCABULARY`** (12) | `UCRD-001` Tier 2; enforced by `ucko.py:397` |
| What is a relationship, structurally? | **`engine/uckp/facets.py`** — Facet 9 of 33 | `UCKP-ART-06` |
| What edge types may a **book artifact** declare? | `config.py::RELATIONSHIP_TYPES` + `RELATES` | `UMB-006 §3`; `UMB-IMP-002`; `AUTH-INF-001 CR-INF-007` |
| What relation types bind **constitutional instruments**? | `CMG-REGISTRY.json::relationship_types` | `CMG-000001` |
| What kind is a **DATA-layer** relationship? | `data/relationship_meta.py` | `DXH-04`, `DATA-008 §5` |
| Is the model itself sole? | **`UCRD-001`** | Governing prior determination |

### 5.2 `CAA-INV-05` measured against the finding

> *"**One instrument declares what a relationship is**, and every relationship kind any projection emits binds to a class and an article of that model."*

| Clause | Measured |
|---|---|
| One instrument declares what a relationship *is* | **SATISFIED.** `facets.py` Facet 9, sole. `UCRD-001` confirms |
| Every relationship kind **any projection emits** binds to a class and an article | **NOT SATISFIED.** P2 emits 16 materialized types into 13,361 edges; none binds to a `uckp.relationship-class` term or an article. P3's 30 likewise |

**The structural half holds; the projection half does not.** That is `C1-F-2`, stated in the invariant's own words rather than mine.

### 5.3 Is this an `ART-03` duplicate authority?

The honest answer requires distinguishing two claims.

| Claim | Verdict | Basis |
|---|---|---|
| The three planes are **rival definitions of what a relationship is** | **NO** | Facet 9 is sole; `UCRD-001` §5 settles it; `UCRD-001` §5.1 disposition 2 explicitly rejects promoting relationship above facet |
| The three planes are **rival term sets over overlapping subject matter** | **PARTLY YES** | 73 terms, 3 shared, 21 case-fold collisions, 5 semantic overlaps, three conventions, no reconciliation map |
| A projection emits a kind not bound to a class or article | **YES** | `CAA-INV-05` clause 2 — §5.2 |

**Measured position:** the planes are **scope-distinct in subject** — objects, book artifacts, constitutional instruments, DATA rows — which is why `UCRD-001` did not treat them as rivals. What is missing is not a merger; it is the **binding of each plane's kinds back to the sole model**, which `CAA-INV-05` clause 2 already requires and nothing performs.

**This determination reports that gap. It does not dispose of it** — `non_goals[5]`: *"Deciding a conflict between two located instruments… is measured and reported, never disposed of here."*

### 5.4 The admission-path asymmetry

| Plane | Admit a new relation type | Code required? |
|---|---|---|
| **P2** | A `RELATES <Type>` front-matter row | **NO — zero config, zero schema edit** |
| **P3** | Append to `relationship_types` | **NO — DATA** |
| **P1** | `VocabularyRegistry.extend` **plus** a `RelationType` enum member **plus**, if acyclicity-checked, an `ACYCLIC_FAMILIES` entry | **YES** |

`RCL-01`, as the Relationship Intelligence determination records it verbatim:

> *"**Operational consequence, recorded because it is a trap:** registering a new relation type in `RELATION_TYPE_VOCABULARY` **alone will fail the alignment check**. A registration is a **two-sided act** — vocabulary term *and* enum member, in the same change — plus, for any type intended to be acyclicity-checked, a family assignment in `ACYCLIC_FAMILIES`."*

**Verified at this baseline:** `RelationType` has **17** members; `uckp.relation-type` has **17** terms; `verify_vocabulary_alignment()` passes over 9 projections including this pair; `ACYCLIC_FAMILIES` covers **4 families over 7** of the 17 types.

> **On the object plane — the plane `D-a` and `D-b` live on — admitting a new relation type requires a code change. That is measured, and it is the single most consequential fact in this determination for question 3.**

---

## 6. Option Evaluation

Rejection criteria, per the directive: duplicate vocabulary authority · duplicate registry authority · parallel semantic model · hardcoded exception.

### 6.1 Option A — the existing vocabulary registry owns relation semantics

| Test | Result |
|---|---|
| Duplicate vocabulary authority | **NONE** — `RELATION_TYPE_VOCABULARY` and `RELATIONSHIP_CLASS_VOCABULARY` already exist and already govern the object plane |
| Duplicate registry authority | **NONE** — `VocabularyRegistry`, unchanged |
| Parallel semantic model | **NONE** — Tier 2/3 of the model `UCRD-001` legislated |
| Hardcoded exception | **NONE** |
| Already legislated? | **YES** — `UCRD-001` §1, §5.1 disposition 10 |
| Enforced? | **YES** — `ucko.py:396-397`, fail-closed |
| Open? | **YES** — `is_extensible()` **True**; but see `RCL-01` (§5.4) |

**ACCEPTED — and not as a choice.** `UCRD-001` governs, and it already determined this. Selecting anything else would put this determination in conflict with an instrument it is subordinate to.

### 6.2 Option B — a relationship registry owns relation semantics

| Test | Result |
|---|---|
| Duplicate registry authority | **FAIL** — `what_this_forbids` names *"a second registry… or **relationship graph**"* |
| Parallel semantic model | **FAIL** — would sit beside Tier 3 |
| Consistent with `K-8` | **FAIL** — `graph.py`: *"Edges are derived, never authored… there is no second place to update and therefore no second authority (Article 3)"* |
| Consistent with `UCRD-001` | **FAIL** — §5.1 disposition 8: *"`CEP-REL-001` — **DO NOT CREATE**"* |

**REJECTED**, and note it was already rejected by name before this determination existed.

### 6.3 Option C — the UCKO object model owns relation semantics

| Test | Result |
|---|---|
| Duplicate vocabulary authority | **FAIL** — the UCKO *consumes* the vocabularies (`require_term` ×6); it does not declare them |
| Parallel semantic model | **FAIL** — would make Facet 9 both the carrier and the definer |
| Consistent with `UCRD-001` | **FAIL** — §5.1 disposition 2 rejects promoting `relationships` above its station: *"`relationships` is Facet 9 of 33; 8 facets are non-relational"* |

**REJECTED.** The object model is the **enforcement point**, not the semantic owner. `C-1` located it correctly as the *carrier* of inter-vocabulary mappings; it is not their vocabulary.

### 6.4 Option D — a relationship semantic vocabulary object exists / should be extended

| Reading | Verdict |
|---|---|
| *"A vocabulary object exists"* | **TRUE, and confirms Option A.** `constitution.py::vocabulary_object()` projects all **13** vocabularies as UCKOs, each `derived-from → UCKP-ART-17`. `uckp.relation-type` **is** a constitutional object today |
| *"…should be extended"* — i.e. add a term | **Not a determination to make here.** Registration is the mechanism; §11 names the owner |
| *"…should be extended"* — i.e. add a **new** semantic vocabulary | **REJECTED** — `ART-03`; duplicate authority |

**ABSORBED INTO OPTION A.** The vocabulary object exists; its existence is evidence *for* A, not an alternative to it.

### 6.5 Option E — another existing constitutional mechanism discovered

Four mechanisms were located that no prior determination in this chain had cited:

| # | Mechanism | Bearing |
|---|---|---|
| `E-1` | **`UCRD-001`** — the governing determination | Already settled Tier 2/3 ownership |
| `E-2` | **`RELATES <Type>`** freeform admission | A code-free admission path on P2 |
| `E-3` | **`RegistryKind.RELATIONSHIP` → `REL`** with `register_kind` | Relationship identity, already available |
| `E-4` | **`allocate_execution`** | The precedent for a new keyed ledger plane |

**None displaces Option A.** `E-1` confirms it; `E-2` describes a different plane; `E-3` and `E-4` answer identity, not semantics.

### 6.6 Result

| Option | Verdict | Basis |
|---|---|---|
| **A — existing vocabulary registry** | **ACCEPTED** | `UCRD-001` §1 Tier 3; already legislated, enforced, open |
| B — relationship registry | REJECTED | `what_this_forbids`; `UCRD-001` §5.1 disposition 8 |
| C — UCKO object model | REJECTED | Consumer, not declarer; `UCRD-001` §5.1 disposition 2 |
| D — vocabulary object | ABSORBED | Exists; confirms A |
| E — other mechanism | 4 located, none displacing | §6.5 |

---

## 7. Canonical Relation Term Determination

### 7.1 The determination

> **`D-a` and `D-b` draw their `relation` from `uckp.relation-type` (17 terms) and their `relationship_class` from `uckp.relationship-class` (12 terms), and from nowhere else.**
>
> **This is not selected here. `UCRD-001` legislated it, `ucko.py:396-397` enforces it fail-closed, and `UCRD-001` governs this determination.**

### 7.2 Why the object plane's vocabulary and not P2's or P3's

The `EEG-2` mappings are **object-plane** bindings: under `C-1`'s Option D, an `EntityKind` term projected as a UCKO carries a `Relationship`. `require_lawful` then validates that relation against `uckp.relation-type` and no other set.

**A P2 or P3 term would be refused at construction.** `Consumes` (TitleCase) is not a member of `uckp.relation-type`; `require_term` raises `LawViolation`. The plane determines the vocabulary mechanically, not by preference.

### 7.3 The admissible candidates

For information only — **this determination selects none.**

`uckp.relation-type`, plausible for an authorization binding: `governs` (*"holds decision authority over"*) · `owns` (*"is accountable for"*) · `depends-on` (*"cannot exist without"*) · `implements` (*"realises"*) · `references` (*"points at"*).

`uckp.relationship-class`, plausible: `authority` (*"from whom the right to exist is derived"*) · `governance` (*"who decides about the object"*) · `ownership` (*"who is accountable"*) · `semantic` (*"what it means in relation to another meaning"*).

### 7.4 Why the class choice is not cosmetic

`graph.py`: *"Classing edges is what makes the difficult questions answerable separately: **'is authority acyclic?' is a question about one class**, and asking it of all edges at once would be meaningless."*

An `EntityKind → CapabilityGroup` edge classed `semantic` rather than `authority` would silently exempt itself from `INV-06`'s acyclicity check. **A wrong class is not a wrong label; it is a skipped invariant.**

### 7.5 Why this determination does not select

| Reason | Basis |
|---|---|
| Selection states what the binding **means** | A declaration act |
| `REPOSITORY_INTELLIGENCE_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"` | *"confers no constitutional authority"* — may implement a declared criterion, not define one |
| This artifact holds `AUTHORITY = NONE` | Role `DERIVED` — *"records or measures the standing of others and asserts nothing of its own"* |
| The owner is located | §11.1 |

### 7.6 The cost of selecting from `uckp.relation-type`

Under `RCL-01` (§5.4), if the chosen term is **already one of the 17**, admission is free — no registration, no code.

If a *new* term were wanted, it would be a **two-sided act**: vocabulary term + `RelationType` enum member (+ `ACYCLIC_FAMILIES` if acyclicity-checked). **That is a code change.**

> **Determination: `D-a` and `D-b` should be satisfied from the existing 17 and 12 wherever a member expresses the binding, precisely because the 17 are open in principle and two-sided in practice.**

---

## 8. Identity Resolution Determination

### 8.1 The four directive questions

| # | Question | Determination |
|---|---|---|
| 1 | **Is `edge_id` identity?** | **NO.** It is a positional serial over an unsorted, content-dependent traversal (`d-3`). It fails `ART-05` (*"once minted, never changes"*) and `ART-13` (*"one canonical form"*). The schema calls it *"immutable"*; its producer does not make it so |
| 2 | **Is `UCOS-REL-…` identity?** | **YES, structurally.** `RegistryKind.RELATIONSHIP` → code `REL`; `deterministic_id` is a pure function of `(code, namespace, natural_key)`, **version-independent** and recomputable. It is used today for nucleus relationship assignments (`nucleus/model.py:437`), **not** for book edges |
| 3 | **Are both required?** | **NO.** They answer one question — *"which relationship is this?"* — in two incompatible ways. `ART-03`: *"A second definition of an existing primitive is a competing authority and is void"* |
| 4 | **Should one become derived?** | **`edge_id` is the one that must change**, because it is the one that is not an identity. Two lawful shapes exist: **(a)** derive it via `deterministic_id(RELATIONSHIP, ns, key)` — the dedup key `(from, to, type)` already exists at `ukb.py:1024`; **(b)** allocate it through a keyed `by_edge` ledger plane on the `allocate_execution` precedent. **This determination does not choose between them** — §11.4 |

### 8.2 The governing identity law

| Law | Requirement | Current state |
|---|---|---|
| `UCKP-ART-05` | An identity never changes | `edge_id` shifts on insertion — **FAILS** |
| `UCKP-ART-13` | One canonical form for every identity | Position is not a canonical form — **FAILS** |
| `CAA-INV-04` | One append-only mint; every declared map resolves in it | 0 of 13,361 edges resolve in the ledger — **FAILS** |
| `UCKP-ART-14` | Append-only | `edge_id` is regenerated, not appended — **FAILS** |
| `ukb.py::allocate` | *"Identity is born by intent, never discovered by a checker"* | `add_edge` mints during regeneration — **FAILS** |

**Five for five.** This is not a marginal finding.

### 8.3 Scope discipline

`I-2`'s absence from the ledger is **not** a defect: a deterministic id is recomputable, so recording it would be storing a derivable value. Only `I-3` is both non-recomputable and unrecorded.

### 8.4 Determination on `C1-F-1`

> **`C1-F-1` is NOT permanently resolved.** Its correct statement is not *"a sequential counter beside a deterministic mint"* — sequential allocation is the ledger's own method. It is: **`edge_id` is positional, unkeyed, unrecorded, and regenerated, and therefore is not an identity under `ART-05` at all.**
>
> **Two lawful resolutions exist, both on existing mechanisms, neither requiring a new registry, mint or authority. Choosing between them is an identity-authority decision — §11.4.**

### 8.5 Bearing on `D-a` / `D-b`

**None. `C1-F-1` does not block them.** Under `C-1`'s Option D a mapping is a `Relationship` **facet of an already-identified UCKO**: it mints no `edge_id`, writes no register row, and advances no counter. The two are independent, and `D-a`/`D-b` may proceed while `C1-F-1` remains open.

---

## 9. Vocabulary Conflict Resolution Model

### 9.1 Canonical term ownership

| Subject | Canonical owner | Basis |
|---|---|---|
| Relation between **objects** | `uckp.relation-type` | `UCRD-001` Tier 3 |
| Register a binding belongs to | `uckp.relationship-class` | `UCRD-001` Tier 2 |
| Edge type between **book artifacts** | `config.py::RELATIONSHIP_TYPES` + `RELATES` | `UMB-006 §3`, `AUTH-INF-001 CR-INF-007` |
| Relation between **constitutional instruments** | `CMG-REGISTRY.json::relationship_types` | `CMG-000001` |
| Kind of a **DATA-layer** relationship | `data/relationship_meta.py` | `DXH-04` |

**Each plane owns its own subject. `UCRD-001` did not treat them as rivals, and this determination does not either.** What `CAA-INV-05` clause 2 requires — that every emitted kind bind to a class and an article of the sole model — is unperformed, and that is the finding (§5.2).

### 9.2 Alias handling

| Plane | Mechanism | Status |
|---|---|---|
| P2 | `labels` — 40 labels over 22 types, plus `RELATES` | **Present and working** |
| P1 | **None.** `Term` has five fields, no synonym | **Absent** |
| P3 | **None** | **Absent** |

**Measured: zero alias/canonical clashes** (§3.4). The alias mechanism is sound where it exists.

**If a P1 alias were ever wanted**, `Term` cannot carry it, and adding a sixth field would be a Layer Zero amendment made to fit data — `how_to_extend[2]`. The lawful route is the object plane: project the term as a UCKO and relate the synonym with `equivalent-to` (*"the same knowledge as"*, `symmetric=True`) — a term that already exists for exactly this. **No amendment; no new mechanism.**

### 9.3 Supersession mechanism

| Level | Mechanism | Available? |
|---|---|---|
| Between **objects** | relation `supersedes`; class `historical` (*"a binding that held in a prior state"*) | **YES** |
| Between **book artifacts** | `Supersedes`/`Superseded-By`; `Replaced-By`/`Replaces` | **YES** — though `SO-2` notes two pairs for one concept |
| Between **instruments** | `CMG-R-11 SUPERSEDES`/`SUPERSEDED-BY`, `acyclic: true` | **YES** |
| **Between terms** | — | **NO** — §9.4 |

### 9.4 Term supersession — the measured gap and its located home

A `Vocabulary` cannot express that one of its terms supersedes another:

- `Term` has five fields, none a lifecycle. `Vocabulary` has no removal. `extended_with` **refuses redefinition** — correctly, since *"a term whose meaning can change retroactively invalidates every digest computed under the old meaning."*
- `uckp.lifecycle-stage` **does** hold `deprecated` and `superseded`, with declared successors — but lifecycle is a **UCKO facet**, not a `Term` field.

> **Determination: a relation term is deprecated or superseded by projecting it as a UCKO and using its lifecycle facet and a `supersedes` relationship — not by editing the vocabulary.**
>
> **This is `C-1`'s Option D arriving a second time, from a different direction.** The mechanism that represents inter-vocabulary mappings is the same one that represents term supersession, and it needs building once.

### 9.5 Migration approach for the overlaps

**Not authorised here. Recorded as a shape, with its preservation constraints binding.**

| Requirement | How the existing mechanism honours it |
|---|---|
| **Preserve historical relationships** | Nothing is renamed or removed. All 13,361 edges keep their `type` verbatim. Class `historical` exists to carry superseded bindings |
| **Preserve existing evidence** | `ART-19` — assimilation is invertible. `ART-12` — no previous state ever changes |
| **Preserve existing references** | P2 `labels` already absorb spelling variants; the 8 P1∩P2 collisions are format-only, so a binding map is a **projection**, not a rewrite |

**The disposition is a binding map, not a merger.** `CAA-INV-05` clause 2 asks each emitted kind to bind to a class and an article — not for the planes to collapse. `SO-1`…`SO-5` would be recorded as `equivalent-to` relations between term objects, which is what that symmetric term is for.

---

## 10. Infinite Evolution Compliance

### 10.1 The seven required capabilities

For a future unknown relation:

| # | Capability | Mechanism | Plane | Available? |
|---|---|---|---|---|
| 1 | **Register** | `RELATES <Type>` · `RELATIONSHIP_TYPES` append · `relationship_types` append · `VocabularyRegistry.extend` | P2/P3/P1 | **YES — four paths** |
| 2 | **Obtain identity** | `deterministic_id(RegistryKind.RELATIONSHIP, …)`; `register_kind` for a future kind | engine | **YES structurally** — but not used for book edges (§8) |
| 3 | **Define semantics** | `Term.definition`; `type`+`inverse`+`labels` on P2 | all | **YES** |
| 4 | **Connect entities** | `Relationship` facet → `derive_edges` → `UniversalKnowledgeEdge` | object | **YES** |
| 5 | **Evolve meaning** | Object-plane lifecycle facet; `Term` redefinition **refused** by design | object only | **YES via §9.4; NO in-vocabulary** |
| 6 | **Supersede meaning** | relation `supersedes` + class `historical` | object only | **YES via §9.4** |
| 7 | **Remain auditable** | `INV-17`; registry `digest()`; `dangling()`; class-scoped acyclicity | all | **YES** — except the 13,361 edges, which are ungated (`C1-F-3`) |

### 10.2 The four prohibitions, per plane

| Prohibition | P2 (book) | P3 (CMG) | P1 (object) |
|---|---|---|---|
| No code change | **HONOURED** — `RELATES <Type>`, zero edits | **HONOURED** — DATA append | **VIOLATED** — `RCL-01` two-sided act |
| No enum addition | **HONOURED** | **HONOURED** | **VIOLATED** — `RelationType` member required |
| No schema rewrite | **HONOURED** — pattern, no `enum` | **HONOURED** | **HONOURED** |
| No new registry | **HONOURED** | **HONOURED** | **HONOURED** |

### 10.3 The measured answer

> **Infinite relation evolution holds on the book and meta-constitutional planes with no code whatever. It does not hold on the object plane, where `RCL-01` makes admission a two-sided act requiring an enum member.**

`RCL-01` is **disclosed, not hidden** — declared in `uisd-declaration.json` with `admission` naming both sides, and the Relationship Intelligence determination judged the projection *"correct architecture, the two-sided admission path is the disclosure,"* reasoning that fusing the enum away *"would remove the fail-closed guarantee that a projection cannot silently drift from its vocabulary."*

**That reasoning is sound and this determination does not disturb it.** But it means the answer to *"can future relation types evolve without code modification?"* is **plane-dependent, and on the plane `D-a`/`D-b` occupy, it is NO.**

### 10.4 The tension this exposes

`EEG-1`/`EEG-2`'s closure determination proposed exactly this pattern — retain the enum as a checked projection — as the **remedy** for closed enums. `RCL-01` is that remedy already applied to `RelationType`, and its measured cost is that admission became two-sided.

> **The checked-projection pattern converts an *undisclosed* closure into a *disclosed two-sided admission*. It does not produce code-free admission.** Any determination claiming that pattern delivers "no future core code modification" must carry this qualification. `EEG-1`/`EEG-2`'s §1.4 stated the one-time/permanent split correctly; `RCL-01` shows the "permanent" half is code-free only where no fail-closed projection is retained.

---

## 11. Ownership and Governance

**No authority is invented. Each row is a located owner or an explicit "not located."**

### 11.1 Vocabulary admission

| Field | Measured |
|---|---|
| Mechanism | `VocabularyRegistry.extend` — *"This is the **only** extension mechanism"* |
| Rule | `how_to_extend[2]` — a DATA append |
| Constitutional act | **None** |
| Declared **party** | **NOT LOCATED.** The register names a mechanism, not a role. Same shape as `AG-2b` |

### 11.2 Relationship admission

| Plane | Owner |
|---|---|
| Object | `RELATION_TYPE_VOCABULARY` + the `RelationType` projection (two-sided) |
| Book | `UMB-006 §3`, `UMB-IMP-002`, `AUTH-INF-001 CR-INF-007`; mechanism `RELATES` |
| Meta-constitutional | `CMG-000001` via `CMG-REGISTRY.json` |
| Registration authority | `REG-AUTO-001` — `CMG-DLG-13` delegates *"registration, identity allocation, classification"* |

### 11.3 Semantic validation

| Layer | Owner | State |
|---|---|---|
| Term admissibility on objects | `ucko.py::require_lawful` | **Fail-closed, live** |
| Projection alignment | `verify_vocabulary_alignment` | **PASS over 9** |
| Executability | `UniversalKnowledgeGraph.dangling()` | Live |
| Class-scoped acyclicity | `CircularAuthorityError`; `ACYCLIC_FAMILIES` (4 families, 7 of 17 types) | Live, partial by design |
| **The 13,361 edges** | **NONE** | **`C1-F-3` / `ISD-G-04`** |

### 11.4 Identity minting

| Field | Measured |
|---|---|
| The one mint | `00-BOOK/DATA/id-ledger.json` via `category_seq` — *"the ONE identity authority"* |
| Delegated authority | `REG-AUTO-001` (`CMG-DLG-13`) |
| Engine derivation | `deterministic_id` + `register_kind` — recomputable, needs no ledger |
| **Relationship identity** | **`RegistryKind.RELATIONSHIP` exists; no plane records a book-edge identity** |
| **Owner of the §8.1(4) choice** | **`REG-AUTO-001`**, as the delegated identity-allocation authority |

### 11.5 Supersession

| Subject | Owner |
|---|---|
| Object relationships | `ART-12`; `UAUE-000001` `AUE-P-11` |
| Terms | **§9.4 — object plane; no in-vocabulary owner, by design** |
| Instruments | `CEP-007` via `CMG-DLG-07` (*"freeze, supersession"*) |

### 11.6 Decisions that remain

| # | Decision | Owner | Kind |
|---|---|---|---|
| `E-a` | The relation + class term for `EntityKind → CapabilityGroup` | Relation-type vocabulary owner (party not located, §11.1) | **Declaration** |
| `E-b` | The relation + class term for `CapabilityGroup → PortalSection` | Same | **Declaration** |
| `E-c` | Derive `edge_id` or add a keyed `by_edge` plane | `REG-AUTO-001` | **Identity authority** |
| `E-d` | Whether to bind P2/P3 kinds to classes and articles per `CAA-INV-05` cl. 2 | Relationship-model owner | **Referral** |
| `E-e` | Disposition of `SO-1`…`SO-5` | Each plane's owner | **Owner** |

---

## 12. Migration Path

**Sequence and dependency only. Nothing below is authorised by this determination.**

| Step | Act | Depends on | Disposition |
|---|---|---|---|
| `DR-1` | Select the relation + class term for each mapping from the existing 17/12 | — | **DECLARATION** (`E-a`, `E-b`) |
| `DR-2` | If both are existing members, admission is free | `DR-1` | **REUSE** |
| `DR-3` | If a new term is needed: vocabulary term **+** `RelationType` member **+** `ACYCLIC_FAMILIES` if acyclicity-checked — **one change** | `DR-1` | **EXTEND, two-sided** (`RCL-01`) |
| `DR-4` | Project the mapped terms as UCKOs | `C-1` Option D | **EXTEND** — precedent ×2 |
| `DR-5` | Resolve `edge_id` — derive or add `by_edge` | `E-c` | **EXTEND** — `allocate_execution` precedent |
| `DR-6` | Bind P2/P3 emitted kinds to classes and articles | `E-d` | **REFERRAL** |
| `DR-7` | Record `SO-1`…`SO-5` as `equivalent-to` relations between term objects | `DR-4`, `E-e` | **REUSE** |

**`CREATE` count: 0.**

### 12.1 Preservation guarantees

| Requirement | Mechanism |
|---|---|
| Historical relationships preserved | No rename, no removal. All 13,361 edges keep `type` verbatim. Class `historical` carries superseded bindings |
| Existing evidence preserved | `ART-19` invertibility; `ART-12` immutability |
| Existing references preserved | P2 `labels` absorb variants; the 8 P1∩P2 collisions are format-only |
| Rollback before acceptance | A private `VocabularyRegistry`; an undiscovered provider contributes nothing |
| Immutability after acceptance | No removal operation; `extended_with` refuses redefinition; `ART-14` |

---

## 13. Acceptance Criteria

| # | Criterion | Measured by | Status |
|---|---:|---|---|
| `AC-01` | Exactly one authority declares what a relationship **is** | `facets.py` Facet 9; `UCRD-001` | **MET** |
| `AC-02` | Object-plane relations validate against `uckp.relation-type` | `ucko.py:396`, fail-closed | **MET** |
| `AC-03` | Object-plane classes validate against `uckp.relationship-class` | `ucko.py:397`, fail-closed | **MET** |
| `AC-04` | `verify_vocabulary_alignment` passes | Direct call | **MET** — 9 projections |
| `AC-05` | `D-a`/`D-b` terms are selected from the 17/12 | `E-a`, `E-b` | **NOT MET** |
| `AC-06` | Every emitted relationship kind binds to a class and an article | `CAA-INV-05` cl. 2 | **NOT MET** — 46 P2/P3 kinds unbound |
| `AC-07` | Every relationship identity resolves in the one mint | `CAA-INV-04` | **NOT MET** — 0 of 13,361 |
| `AC-08` | `edge_id` is stable across regeneration | `ART-05` | **NOT MET** — positional |
| `AC-09` | The 13,361 edges are gated against their schema | `ISD-G-04` | **NOT MET** |
| `AC-10` | Relation-type admission needs no code | `RCL-01` | **MET on P2/P3 · NOT MET on P1** |
| `AC-11` | Term supersession is expressible | §9.4 | **NOT MET** — needs object-plane projection |
| `AC-12` | No new registry, mint, authority or semantic model | Count | **MET** — 0 of each |

**MET 6 · SPLIT 1 · NOT MET 5.**

---

## 14. Final Determination

### 14.1 Verdict

> # CONDITIONALLY RESOLVED

### 14.2 The four required answers

**1 — Is there exactly one canonical relation semantic authority?**

> **For the object plane — the plane `D-a` and `D-b` occupy — YES, and it was already legislated.** `RELATION_TYPE_VOCABULARY` (17) and `RELATIONSHIP_CLASS_VOCABULARY` (12), under `UCRD-001` Tiers 3 and 2, enforced fail-closed at `ucko.py:396-397`.
>
> **Across the repository as a whole — NO, not in the sense of one term set.** Three planes declare relation terms: **73 distinct**, only **3** shared by all three, **21** case-fold collisions, **5** semantic overlaps, three conventions. The planes are **scope-distinct in subject**, which is why `UCRD-001` did not treat them as rivals — but `CAA-INV-05` clause 2 requires every emitted kind to bind to a class and an article of the sole model, and **46 P2/P3 kinds do not**. That is unperformed work, not a resolved question.

**2 — Is there exactly one identity authority for relationships?**

> **NO.** The one mint is the id-ledger via `category_seq` — **6,413 ids, 100% `UCOS-<CAT>-NNNNNN`**. `RegistryKind.RELATIONSHIP` → `REL` exists and is used for nucleus assignments. **Book edges use neither**: `UEDGE-NNNNNNNNN` is minted by a build-local counter, appears **0 times** in the ledger, and is **positional over unsorted traversal** — failing `ART-05`, `ART-13`, `ART-14`, `CAA-INV-04` and `allocate`'s own stated rule, five for five.

**3 — Can future relation types evolve without code modification?**

> **Plane-dependent, and on the plane that matters here, NO.**
>
> **P2 (book): YES** — a `RELATES <Type>` row admits a type with zero config, schema or code edit. **P3 (CMG): YES** — a DATA append. **P1 (object): NO** — `RCL-01` makes admission a two-sided act: vocabulary term **plus** `RelationType` enum member, plus `ACYCLIC_FAMILIES` if acyclicity-checked.
>
> Where an existing member of the 17 expresses the binding, **no admission is required at all** — which is why §7.6 determines `D-a`/`D-b` should be satisfied from the existing set.

**4 — Are `C1-F-1` and `C1-F-2` permanently resolved?**

> **NO. Neither.**
>
> **`C1-F-1`** — restated correctly (§8.4): not *"sequential vs deterministic"* — sequential is the ledger's own method — but **`edge_id` is positional, unkeyed, unrecorded and regenerated, and is therefore not an identity**. Two lawful resolutions exist on existing mechanisms; choosing is `REG-AUTO-001`'s (`E-c`).
>
> **`C1-F-2`** — refined (§5.3): **not** an `ART-03` duplicate of *what a relationship is* (Facet 9 is sole, `UCRD-001` settles it), but a real **`CAA-INV-05` clause-2 gap** — 46 emitted kinds bound to no class and no article. Disposition is `E-d`, a referral.

### 14.3 Why `CONDITIONALLY RESOLVED`

**Not `PERMANENTLY RESOLVED`:** five acceptance criteria are unmet, questions 2 and 4 answer NO, and question 3 answers NO on the relevant plane.

**Not `NOT RESOLVED`:** the question this determination was posed — *which authority owns relation semantics for `D-a`/`D-b`* — **is answered, definitively and without invention**. `UCRD-001` legislated it; the object plane enforces it fail-closed; the terms exist; no new mechanism is needed. `D-a` and `D-b` are unblocked by everything in §14.2 answers 2 and 4, since an object-plane mapping mints no edge identity and touches no P2/P3 kind.

**The condition:** two declaration decisions (`E-a`, `E-b`) that this artifact holds no authority to make.

### 14.4 Can `D-a`/`D-b` close without creating a duplicate authority, duplicate registry, parallel semantic model or hardcoded exception?

| # | Thing | Answer | Basis |
|---|---|---|---|
| 1 | Duplicate vocabulary authority | **NO — none required** | The 17 and 12 exist and govern |
| 2 | Duplicate registry authority | **NO — none required** | `VocabularyRegistry`, unchanged |
| 3 | Parallel semantic model | **NO — none required** | Tier 2/3 of the sole model; `CEP-REL-001` already refused by `UCRD-001` |
| 4 | Hardcoded exception | **NO — none required** | Both terms come from existing members |

**Four of four: NO.**

### 14.5 Corrections of record

| # | Correction |
|---|---|
| 1 | **`C1-F-1` was framed imprecisely.** I wrote *"a sequential counter, not the deterministic mint,"* implying deterministic minting is the ledger's standard. Measured: the ledger's one authority **is** a sequential counter (`category_seq`), and 100% of its 6,413 ids are sequential. The defect is positional instability, missing keying, and no ledger plane — §4.3 |
| 2 | **`C1-F-2` was over-graded as a probable `ART-03` duplicate.** `UCRD-001` — which governs — determines Facet 9 is sole and the planes are scope-distinct. The real defect is narrower and sharper: a `CAA-INV-05` clause-2 binding gap over 46 kinds — §5.3 |
| 3 | **This chain had not read its governing determination.** `UCRD-001` and its companion predate the `EEG`/`C-1` artifacts and answer part of what they treated as open. `ART-18` requires locating the canonical object first; that step was performed here and should have been performed earlier |

### 14.6 What this determination did not do

| Not done | Under |
|---|---|
| Select the relation or class term for `D-a` or `D-b` | §7.5 — a declaration act |
| Create, register, deprecate or supersede any term | Directive |
| Mint or alter any identity; modify relationship data | Directive |
| Dispose of `C1-F-1`, `C1-F-2`, `C1-F-3`, `SO-1`…`SO-5` | `non_goals[5]` |
| Merge, rename or retire any plane | `non_goals[1]` |
| Disturb `UCRD-001`'s determinations | It governs |

---

## 15. Verification Record

### 15.1 Before / after

| Field | Before | After | Delta |
|---|---|---|---|
| HEAD | `bae59755…5269a` | `bae59755…5269a` | **unchanged** |
| Branch | `integration/recovery-001` | `integration/recovery-001` | **unchanged** |
| `git status --porcelain` | **361** | **362** | **+1 — this artifact** |
| Tracked modifications | **38** | **38** | **unchanged** |
| Staged | **0** | **0** | **unchanged** |
| Untracked | **323** | **324** | +1 |
| Commits | **0** | **0** | **none** |

### 15.2 Required post-write assertions

| Assertion | Result |
|---|---|
| Only one new artifact | **VERIFIED** — porcelain +1 |
| HEAD unchanged | **VERIFIED** |
| Branch unchanged | **VERIFIED** |
| Code unchanged | **VERIFIED** — tracked mods 38, unchanged |
| Registry unchanged | **VERIFIED** — no `00-BOOK/DATA/*`, `00-CMG/*` or `00-BOOK/SCHEMAS/*` in the delta |
| Identity unchanged | **VERIFIED** — `id-ledger.json` not in the delta; no mint invoked for persistence |
| Ownership unchanged | **VERIFIED** |
| Certification unchanged | **VERIFIED** |
| Relationship data unchanged | **VERIFIED** — `relationships.json` read only |
| No commits | **VERIFIED** |

### 15.3 Live measurements

| Measurement | Method | Result |
|---|---|---|
| `uckp.relation-type` / `-class` | Import | **17** / **12** |
| `RelationType` enum | Import | **17** |
| `RELATIONSHIP_TYPES` | Module load | **22** types · **44** with inverses · **40** labels · **31** normalized |
| `RELATIONSHIP_FREEFORM_LABEL` | Module load | `"RELATES"` |
| `CMG relationship_types` | JSON | **16** · **30** with inverses |
| Total distinct terms, case-folded | Set union | **73** |
| In all three planes | Set intersection | **3** — `certifies`, `depends-on`, `supersedes` |
| Case-fold collisions | Set ops | P1∩P2 **8** · P1∩P3 **5** · P2∩P3 **8** |
| Alias/canonical clashes | Normalized comparison | **0** |
| Materialized undeclared | Set difference | **0** |
| Declared unmaterialized | Set difference | **28 of 44** |
| Ledger ids by shape | Regex over 6,413 | **100%** sequential · **0%** deterministic |
| `UEDGE-` in ledger | Membership | **False** |
| Ledger planes | Key inspection | `by_path` 1,492 · `by_object` 4,914 · `by_observation` 7 — **no edge plane** |
| `edge_id` producer | Source read | `ukb.py:1020-1033` — build-local `edge_seq`, keyed by nothing |
| Edge sorting before write | `grep` | **None** — `edges.sort` / `sorted(edges)` absent |
| `RegistryKind.RELATIONSHIP` code | Source read | `"REL"` (`identity.py:141`) |
| `ACYCLIC_FAMILIES` | Source read | **4** families over **7** of 17 types |
| `Term` fields | `dataclasses.fields` | **5** — no lifecycle, no alias |
| Deprecated relation terms | Scan of all three planes | **0** |
| `relationship.schema.json` `type` | JSON | Pattern only, **no `enum`** |

### 15.4 What was not verified

| Not verified | Why |
|---|---|
| That regenerating the corpus renumbers `edge_id` | Would require running `ukb.py`, which writes. `d-3` is established by **reading** the producer: unkeyed counter over unsorted traversal |
| Which term `E-a`/`E-b` should select | A declaration act, not a measurement |
| Whether `C1-F-2`'s binding gap is a live `CAA-INV-05` breach | Requires the relationship-model owner's disposition; `non_goals[5]` |
| Whether P4 (`data/relationship_meta.py`) overlaps P1–P3 | Out of scope; `UCRD-001`'s companion already dispositioned `RCL-02` |
| That three planes are the complete set | Measured across `engine/uckp`, `engine/knowledge`, `00-BOOK/tools`, `00-CMG`, `data/`. A fourth declaring surface elsewhere would not have been seen |
| Current `verify.sh` verdict | Not executed — `ISD-G-11`; this mode forbids surface mutation |

### 15.5 Artifact creation verified

| Check | Result |
|---|---|
| File exists | **Yes** |
| Required sections | **15 of 15, in the specified order** |
| Verdict | **Exactly one permitted value — `CONDITIONALLY RESOLVED`** |
| Four required questions | **All four answered explicitly — §14.2** |
| Git status | `??` untracked — the only delta from 361 |
| Other files changed | **0** |
| Commits | **0** |

---

**End of determination.**

| Field | Value |
|---|---|
| Baseline | `bae59755d7e2d3566c93b89c722b68847145269a` · `integration/recovery-001` |
| Sections | 15 |
| Governing prior determination | `UCRD-001` |
| Relation planes measured | **3** declaring (+1 projection, +1 DATA) |
| Total distinct relation terms | **73** |
| Terms in all three planes | **3** |
| Case-fold collisions | **21** |
| Semantic overlaps | **5** |
| Alias labels | **40** · clashes **0** |
| Ledger ids classified | **6,413** — 100% sequential, 0% deterministic |
| Identity laws failed by `edge_id` | **5** |
| Options evaluated | **5** · accepted **1** · rejected **2** · absorbed **1** |
| Corrections of record | **3** |
| New authorities · registries · models · exceptions | **0 · 0 · 0 · 0** |
| `CREATE` acts | **0** |
| Code changed | **0 files** |
| Registries changed | **0** |
| **Verdict** | **CONDITIONALLY RESOLVED** |
