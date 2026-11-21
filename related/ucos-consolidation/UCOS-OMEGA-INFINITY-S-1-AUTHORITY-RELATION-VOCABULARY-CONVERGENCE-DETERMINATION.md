# UCOS Ω∞ — S-1 AUTHORITY RELATION VOCABULARY CONVERGENCE DETERMINATION

> **Question:** What canonical relationship vocabulary is required for authority, governance, ownership and evolution?
> **Baseline:** `bae59755d7e2d3566c93b89c722b68847145269a` · **Branch:** `integration/recovery-001` · **515 commits**
> **Working tree at capture:** 382 porcelain entries (38 tracked-modified · 344 untracked) — pre-existing, untouched
> **Predecessors:** existence (1,582) · assimilation (1,436) · first-act authority (1,444) · actor eligibility (1,260)
> **New inputs measured:** `engine/uckp/alignment.py` (797) · `engine/uckp/graph.py` (334) · `CAA.relationship_graph_resolution` · the live 13,361-edge type population
> **Mode:** VOCABULARY CONVERGENCE DETERMINATION ONLY. No vocabulary modified, no term merged, no relation created, no file changed, no commit.
> **Authority:** **NONE (DERIVED TRUTH).** This determination merges nothing, registers no term and creates no relation.
> **Verdict:** **CONVERGENCE MECHANISM EXISTS AND IS UNAPPLIED · SIX VOCABULARIES · FOUR CONVENTIONS · NOT CONVERGED**

**Mandatory principles, as applied**

| Principle | Applied meaning in this determination |
|---|---|
| **One semantic meaning = one canonical source** | Tested term by term. `depends-on` was found in **three** spellings across three homes; `PROJECTION`/`projection` in two; and one live type is named `Evolves-From-Inverse`, which is a manufactured name for a backwards reading |
| **Infinite entities · scopes · directions · contexts · future types** | All five hold under the model, and the mechanism that keeps them holding — a `direction` field on a declared binding — is the one already built and unapplied |
| **No duplicate relation vocabularies** | **Measured breach:** six vocabularies, four case conventions, two divergent fourth members |
| **No parallel authority models** | **HOLDS** — `CAA-INV-05` measures exactly one relationship-model owner, and no rival model exists |
| **No semantic drift** | **Measured breach:** `verify_binding()` returns **0 findings** while the drift sits outside its scope |
| **No hardcoded finite assumptions** | The crosswalk is **DATA** — *"a seventh kind is one appended entry… and never an engine change"* |
| **Zero fixes · patches · shortcuts · temporary solutions · duplication · overlap** | Nothing merged, nothing renamed, nothing registered. §12 presents options and selects none for execution |

---

## 1. Executive Determination

# CONVERGENCE MECHANISM EXISTS AND IS UNAPPLIED · SIX VOCABULARIES · FOUR CONVENTIONS · NOT CONVERGED

**The canonical relationship vocabulary is already determined: `uckp.relation-type` (17 terms) and `uckp.relationship-class` (12 terms), owned by `UCKP-ART-07` at `engine/uckp/graph.py`, with exactly one owner guaranteed by `CAA-INV-05`. The convergence *mechanism* is also already built: `relationship_kind_bindings`, a DATA crosswalk mapping each emitted kind to a model class, a model relation, a `direction` and an article — enforced by `engine.uckp.alignment._vocabulary_findings`. Six relation vocabularies exist in the repository. The crosswalk covers one of them.**

### 1.1 The six vocabularies, measured

| # | Vocabulary | Home | Terms | Convention | Crosswalked to the model |
|---|---|---|---|---|---|
| **V-1** | **`uckp.relation-type`** | `engine/uckp/vocabulary.py` | **17** | `lower-hyphen` | **it *is* the model** |
| **V-2** | **`uckp.relationship-class`** | same | **12** | `lower` | **it *is* the model** |
| **V-3** | **`relationship_kind_bindings`** | `CAA.relationship_graph_resolution` | **6** | `snake_case` | **YES — this is the crosswalk** |
| **V-4** | **`subordination_relations`** | `UCOS-CAA-001` | **4** | `UPPERCASE` | **NO — read by zero Python files** |
| **V-5** | **`ConvergenceRelation`** | `platform/universal_foundation/convergence.py` | **4** | `lower` | **NO** |
| **V-6** | **live edge types** | `00-BOOK/DATA/relationships.json` | **16** | `Title-Case-Hyphen` | **NO — 0 of 16 in the crosswalk** |

**Six vocabularies. Four case conventions. Fifty-nine term instances. One crosswalk, covering six kinds.**

### 1.2 The three measured breaches of "one semantic meaning = one canonical source"

| # | Meaning | Spellings found | Homes |
|---|---|---|---|
| **1** | *depends on* | **`depends-on`** (V-1) · **`depends_on`** (V-3) · **`Depends-On`** (V-6) | three |
| **2** | *is a projection of* | **`PROJECTION`** (V-4) · **`projection`** (V-5) | two |
| **3** | *the fourth subordination relation* | **`ORTHOGONAL`** (V-4, 0 occurrences in the gate) · **`GOVERNED`** (V-5, 0 occurrences in CAA) | two, **divergent in meaning** |

### 1.3 The finding that names the anti-pattern precisely

`CAA.$kind_binding_comment` declares why the crosswalk carries a `direction` field:

> *"`direction` records whether the projection emits the model's edge or its inverse, **because a kind read backwards is still that kind and pretending otherwise would invent a term to avoid saying so.**"*

**Measured in the live edge population: a type named `Evolves-From-Inverse`, 5 edges.**

| Fact | Value |
|---|---|
| Live edge types | **16** |
| Forward/inverse pairs among them | **8 pairs** — `Depends-On`/`Required-By`, `Parent`/`Child`, `Consumes`/`Consumed-By`, `Authorizes`/`Authorized-By`, `Implements`/`Implemented-By`, `References`/`Referenced-By`, `Traces-To`/`Traced-From`, `Evolves-From`/**`Evolves-From-Inverse`** |
| Edges carrying `inverse_of: null` | **8,292 of 13,361** |
| Types named for their own inversion | **1 — `Evolves-From-Inverse`** |

> **The architecture anticipated this exact error, wrote a field to prevent it, explained in prose why the field exists, and the error is present anyway — in a population the crosswalk does not cover. `Evolves-From-Inverse` is a term invented to avoid saying "the same kind, read backwards", which is verbatim what the comment forbids. Eight inverse-named types exist where the model plus a `direction` flag would express eight forward kinds.**

### 1.4 The vacuity: a verifier that passes while the drift stands

| Measurement | Value |
|---|---|
| `verify_binding(CAA document)` findings | **0 — fully aligned** |
| What it checks | the **6** declared `relationship_kind_bindings` against `RELATIONSHIP_CLASS_VOCABULARY`, `RELATION_TYPE_VOCABULARY` and `ROOT_LAW.article_ids()` |
| Whether it checks `subordination_relations` | **NO — the key is read by zero Python files repository-wide** |
| Whether it checks the emitted population against the map | **NO — it checks the map's terms, not the population's kinds** |
| Whether `00-BOOK/DATA/relationships.json` is a declared projection | **NO — the 3 declared projections are UGA, RIE and RPI graphs** |
| Live types appearing in the crosswalk | **0 of 16** |

And the crosswalk's own rule, from `$kind_binding_comment`:

> *"A kind absent from this map is an unmodelled relationship and **fails CAA-INV-05**."*

> **By the crosswalk's own stated rule, sixteen unmodelled relationship kinds are in force across 13,361 edges. `verify_binding()` reports zero findings because the population emitting them is not a declared projection, so its kinds are never presented to the map. The alignment verifier is correct, complete over its scope, and blind precisely where this mission's question lives.**

### 1.5 What is and is not required

| Question | Answer |
|---|---|
| Is a canonical relationship vocabulary determined? | **YES — V-1 + V-2, owned by `ART-07`, `CAA-INV-05` exactly one owner** |
| Is a new relation required? | **NO** |
| Is a new vocabulary required? | **NO** |
| Is a new registry or crosswalk mechanism required? | **NO — `relationship_kind_bindings` is the mechanism** |
| Is a parallel authority model present? | **NO** |
| Are duplicate relation vocabularies present? | **YES — 6 homes, 4 conventions** |
| Is semantic drift present? | **YES — 3 measured breaches** |
| Are hardcoded finite assumptions present? | **NO in the crosswalk (it is DATA); YES in `ConvergenceRelation` (a Python enum)** |
| Is anything merged, renamed or created here? | **NO** |
| Convergence | **NOT ACHIEVED — §15** |

---

## 2. Current Relation Vocabulary Reality

### 2.1 V-1 — `uckp.relation-type`, the model's relation axis

**17 terms**, lowercase-hyphenated:

`certifies` · `conflicts-with` · `consumes` · `depends-on` · `derived-from` · `equivalent-to` · `extends` · `generated-from` · `governs` · `implements` · `inherits` · `owns` · `produces` · `references` · `related-to` · `supersedes` · `validates`

| Property | Value |
|---|---|
| Home | `engine/uckp/vocabulary.py :: RELATION_TYPE_VOCABULARY` |
| Governing article | `UCKP-ART-07` |
| Model home | `engine/uckp/graph.py` (334 lines) |
| Enforcement | `require_lawful()` → `require_term(RELATION_TYPE, relationship.relation)` |
| Openness | register-then-use; open |
| Cardinality guard | `CAA-INV-05` — *"One instrument declares what a relationship is"* |

### 2.2 V-2 — `uckp.relationship-class`, the model's class axis

**12 terms**: `authority` · `constitutional` · `evolution` · `future` · `governance` · `historical` · `knowledge` · `ownership` · `runtime` · `semantic` · `traceability` · `validation`

| Property | Value |
|---|---|
| Enforcement | `require_term(RELATIONSHIP_CLASS, relationship.relationship_class)` |
| Notable member | **`future`** — a declared class for relationships whose nature is not yet decided |

### 2.3 V-3 — `relationship_kind_bindings`, the crosswalk

**6 kinds**, snake_case, each carrying five fields:

| Kind | `uckp_class` | `uckp_relation` | `direction` | `article` |
|---|---|---|---|---|
| `owned_by` | `ownership` | `owns` | **inverse** | `UCKP-ART-06` |
| `produced_by` | `traceability` | `produces` | **inverse** | `UCKP-ART-19` |
| `produces` | `traceability` | `produces` | forward | `UCKP-ART-19` |
| `depends_on` | `constitutional` | `depends-on` | forward | `UCKP-ART-07` |
| `validated_by` | `validation` | `validates` | **inverse** | `UCKP-ART-16` |
| `evidenced_by` | `constitutional` | `references` | forward | `UCKP-ART-12` |

**This is the exemplar. `owned_by` and `owns` are one meaning in one canonical source, distinguished by a declared `direction` rather than by a second term. Three of six bindings use `direction: inverse` and none invents an inverse-named term.**

### 2.4 V-4 — `subordination_relations`, declared and unread

**4 keys**, UPPERCASE: `DELEGATES` · `SUPERSEDED` · `PROJECTION` · `ORTHOGONAL`

| Property | Value |
|---|---|
| Home | `UCOS-CAA-001` |
| Read by Python | **zero files — grep over all `*.py` returns nothing** |
| Checked by `verify_binding()` | **NO** |
| Guarded by `verify_vocabulary_alignment()` | **NO — that guards 9 projections; this is not among them** |
| Declared closure | *"No fourth relation is created"* — while carrying a fourth |

### 2.5 V-5 — `ConvergenceRelation`, executable and divergent

**4 members**, lowercase: `delegates` · `superseded` · `projection` · **`governed`**

| Property | Value |
|---|---|
| Home | `platform/universal_foundation/convergence.py` (991 lines) |
| Form | a **Python `str` Enum** — a hardcoded finite set |
| Enforcement | `FG-15-NO-PARALLEL-AUTHORITY`, executable per relation |
| Guarded by `verify_vocabulary_alignment()` | **NO** |
| `ORTHOGONAL` occurrences | **0** |

### 2.6 V-6 — the live edge population

**16 distinct types across 13,361 edges**, Title-Case-Hyphenated:

| Type | Edges | Type | Edges |
|---|---|---|---|
| `Depends-On` | 4,777 | `Required-By` | 4,700 |
| `Parent` | 1,462 | `Child` | 1,462 |
| `Consumes` | 316 | `Consumed-By` | 316 |
| `Authorized-By` | 100 | `Authorizes` | 100 |
| `Implements` | 48 | `Implemented-By` | 48 |
| `References` | 6 | `Referenced-By` | 6 |
| `Traces-To` | 5 | `Traced-From` | 5 |
| `Evolves-From` | 5 | **`Evolves-From-Inverse`** | 5 |

| Property | Value |
|---|---|
| Is it a declared projection in CAA? | **NO** |
| Live types in the crosswalk | **0 of 16** |
| Types expressible as model term + `direction` | **all 16** |
| Types requiring a model term the model lacks | **0** |

### 2.7 The mapping of all 16 live types onto the model

Recorded to establish that convergence needs **no new term**.

| Live type | Model relation (V-1) | Direction | Model class (V-2) |
|---|---|---|---|
| `Depends-On` / `Required-By` | `depends-on` | forward / inverse | `constitutional` |
| `Parent` / `Child` | `inherits` | inverse / forward | `constitutional` |
| `Consumes` / `Consumed-By` | `consumes` | forward / inverse | `runtime` |
| `Authorizes` / `Authorized-By` | `governs` | forward / inverse | `authority` |
| `Implements` / `Implemented-By` | `implements` | forward / inverse | `knowledge` |
| `References` / `Referenced-By` | `references` | forward / inverse | `constitutional` |
| `Traces-To` / `Traced-From` | `derived-from` | inverse / forward | `traceability` |
| `Evolves-From` / `Evolves-From-Inverse` | `supersedes` | inverse / forward | `evolution` |

**Sixteen live types map onto eight model relations plus a direction flag. Every required model term already exists. Zero new terms are needed, and this is the measured basis for §12.**

### 2.8 Current reality verdict

| Question | Answer |
|---|---|
| How many relation vocabularies exist? | **6** |
| How many case conventions? | **4** |
| Is the canonical one identifiable? | **YES — V-1 + V-2** |
| Do the others crosswalk to it? | **1 of 5 does (V-3)** |
| Do any require a term the model lacks? | **NO — 0** |
| Is convergence achievable without new terms? | **YES** |
| Classification | **SIX VOCABULARIES · ONE MODEL · ONE CROSSWALK · FOUR UNCROSSWALKED** |

---

## 3. CAA Relation Model Assessment

### 3.1 What CAA declares about relationships

`UCOS-CAA-001` carries two distinct relation concerns and they must not be conflated.

| Concern | Block | Terms | Purpose |
|---|---|---|---|
| **Graph relationships** — edges between objects | `relationship_graph_resolution` | 6 crosswalked kinds | binds emitted kinds to the model |
| **Subordination relations** — how an instrument stands to the authority above it | `subordination_relations` | 4 keys | records standing, not edges |

**These are different axes. A subordination relation is a property of a *surface*; a graph relationship is an edge between *objects*. Conflating them would be its own semantic drift, and this determination keeps them separate throughout.**

### 3.2 The graph concern is correctly modelled

| Element | Measured |
|---|---|
| `model_owner.authority` | `UCKP-ART-07` |
| `model_owner.home` | `engine/uckp/graph.py` |
| `model_owner.owns` | *"What a relationship is, what an edge is, what makes an edge resolvable, and the requirement that the authority relation stay acyclic (`UCKP-INV-04`, `05`, `06`)"* |
| `model_term_sources` | points to `RELATIONSHIP_CLASS_VOCABULARY` and `RELATION_TYPE_VOCABULARY` **by reference, not by copy** |
| `model_term_sources.note` | *"These lists are **NOT copied here**. The enforcing engine is stdlib-only by constitutional design and checks kinds against this map; `verify_binding` checks this map against the vocabularies"* |
| `second_model_test` | *"A second relationship model would be a second declaration of what a relationship IS. `CAA-INV-05` measures that exactly one instrument declares the model"* |
| Declared projections | **3** — UGA `04-RELATIONSHIP-GRAPH.json`, RIE `UCOS-RIE-DEPENDENCY-GRAPH.json`, RPI `UCOS-RPI-DEPENDENCY-GRAPH.json`, each `role: PROJECTION` |

> **The graph concern is exemplary and is the pattern §12 reuses. Terms are referenced rather than copied — the block explicitly refuses to duplicate the term lists, which is `ART-18` observed rather than asserted. A two-way check exists: the stdlib engine checks kinds against the map, and `verify_binding` checks the map against the vocabularies.**

### 3.3 The subordination concern is not modelled at all

| Test | Result |
|---|---|
| Does `subordination_relations` reference a term source? | **NO — the 4 definitions are prose, held inline** |
| Are its terms copied or referenced? | **held inline as the only home** |
| Is there a `second_model_test` for it? | **NO** |
| Is it read by any Python file? | **NO — zero** |
| Is it checked by `verify_binding()`? | **NO** |
| Is it in the 9 vocabularies `verify_vocabulary_alignment()` guards? | **NO** |
| Does a rival home exist? | **YES — `ConvergenceRelation`** |

**The asymmetry within one instrument is the finding: the graph relation vocabulary is referenced, crosswalked, two-way checked and guarded; the subordination relation vocabulary is inline, uncrosswalked, unchecked and unguarded — and it is the one governing how authority itself is declared.**

### 3.4 What CAA gets right that must be preserved

| Property | Why it must survive any convergence |
|---|---|
| Terms referenced, never copied | `ART-18`; a copy is a rival |
| `direction` on every binding | prevents inverse-named term invention |
| `article` on every binding | every kind names the law it holds under |
| `meaning` on every binding | prevents silent redefinition |
| The map is **DATA** | *"a seventh kind is one appended entry… never an engine change"* — `ART-17` |
| Absence from the map is a **failure**, not a default | *"A kind absent from this map is an unmodelled relationship and fails `CAA-INV-05`"* |
| Two-way checking | map→vocabulary by `verify_binding`; kind→map by the stdlib engine |

### 3.5 The role vocabulary is crosswalked — the relation vocabulary is not

Measured contrast within the same instrument, and it is decisive for §12.

| | Authority **roles** | Subordination **relations** |
|---|---|---|
| Declared in JSON | 8, with `may_hold_authority` and `cardinality` | 4, with prose definitions |
| Declared in code | **`AUTHORITY_ROLES` — 8 `AuthorityRole` objects in `alignment.py`** | **nothing** |
| Code↔data check | **YES — `_role_findings()`** | **NO** |
| Measured agreement | **8 of 8 match**, `SUPREME`/`True`/`EXACTLY_ONE` and 7 × `False` | **not measurable** |
| Divergence possible undetected | **NO** | **YES — and it has occurred** |

> **Roles and relations sit side by side in one instrument. Roles have a code counterpart and a checker; relations have neither. The divergence found in the relation vocabulary is not bad luck — it is the predictable consequence of the one vocabulary in that instrument that has no crosswalk.**

### 3.6 CAA relation model verdict

| Question | Answer |
|---|---|
| Does CAA declare a relation model? | **NO — it references one; `ART-07` owns it** |
| Is the graph crosswalk sound? | **YES — exemplary; direction, article, meaning, DATA, two-way checked** |
| Is the subordination vocabulary crosswalked? | **NO** |
| Is it read by any code? | **NO** |
| Are roles crosswalked? | **YES — 8 of 8, code↔data** |
| Is the asymmetry the root cause of the divergence? | **YES** |
| Classification | **GRAPH CONCERN EXEMPLARY · SUBORDINATION CONCERN UNCROSSWALKED** |

---

## 4. Convergence Relation Model Assessment

### 4.1 What `ConvergenceRelation` is

| Property | Measured |
|---|---|
| Home | `platform/universal_foundation/convergence.py`, lines 68–77 |
| Form | `class ConvergenceRelation(str, Enum)` — **a hardcoded finite enum** |
| Members | `DELEGATES` · `SUPERSEDED` · `PROJECTION` · **`GOVERNED`** |
| Docstring | *"How a subordinate surface now stands to the canonical owner of its model."* |
| Coercion | `coerce()` — hard-refuses an unregistered value |
| Gates | `FG-15-NO-PARALLEL-AUTHORITY` · `FG-16-ONE-MEASUREMENT` |
| Articles measured | UFC-14 (one owner per model) · UFC-15 (no parallel authority) |

### 4.2 Each member's executable test

| Relation | Test | Failure text |
|---|---|---|
| `SUPERSEDED` | `not path.exists()` | *"PRESENT — a retired implementation that still exists is still a second answer"* |
| `PROJECTION` | `path.suffix != ".py"` | *"EXECUTABLE — a projection may not hold a determination"* |
| `GOVERNED` | `reserved ∩ string_literals(source) == ∅` | *"RESTATES CANONICAL LAW: …"* |
| `DELEGATES` | `model.canonical_package ∈ imported_modules(source)` | *"a surface that claims to delegate but imports nothing from the owner is a parallel authority"* |

**Four relations. Four executable tests. This is the only relation vocabulary in the repository whose every member is mechanically verified against reality rather than against a declaration.**

### 4.3 The strength and the weakness

| Strength | Weakness |
|---|---|
| Every member has a real test | it is a **Python enum** — a closed set requiring a code edit to extend |
| Tests read the filesystem and the AST | `ART-17` says extension is by registration, *"never an engine change"* |
| `coerce()` refuses unknown values | so an unknown future relation is refused rather than registered |
| It is the enforcement layer | and it is **not** among the 9 vocabularies `verify_vocabulary_alignment()` guards |

> **`ConvergenceRelation` is simultaneously the most rigorous and the least extensible relation vocabulary in the repository. Its rigour is that nothing can be claimed without being proven; its finiteness is that a fifth relation requires editing Python, which `extension_rule` bullet 2 forbids for vocabulary members — *"one appended entry in DATA… never an engine change"*.**

### 4.4 Is it a parallel authority model?

| Test | Result |
|---|---|
| Does it declare what a relationship **is**? | **NO — it declares how a *surface stands*, which is the subordination axis** |
| Does it declare a second graph model? | **NO — `CAA-INV-05` is not breached** |
| Does it duplicate `subordination_relations`? | **YES on 3 members, and diverges on the fourth** |
| Is it a parallel **authority model**? | **NO** |
| Is it a parallel **vocabulary** for the identical concept? | **YES — and the CAA comment defines that as a rival** |

**The distinction matters and is preserved: there is no parallel authority model. There is a parallel vocabulary for the subordination axis, which is a lesser but real breach, and it is the one the mission's principle "no duplicate relation vocabularies" names.**

### 4.5 The three shared members, compared verbatim

| Member | `subordination_relations` (V-4) | `ConvergenceRelation` (V-5) | Same meaning |
|---|---|---|---|
| `DELEGATES` | *"still exists and reaches the authority above it rather than answering for itself"* | *"Still present, and must reach the canonical owner rather than answer for itself"* | **YES — near-verbatim** |
| `SUPERSEDED` | *"once held a competing definition and is now gone. A retired definition that still exists is still a second answer"* | *"Retired. Must be absent — a present implementation is a present second answer"* | **YES** |
| `PROJECTION` | *"a derived or authored view of the objects, holding no independent determination"* | *"Derived output of the canonical owner; must hold no executable determination"* | **YES** |

**Three meanings, two sources each. By the mission's first principle — one semantic meaning = one canonical source — this is three breaches, and they are the least ambiguous three in the repository because the definitions are near-verbatim restatements.**

### 4.6 Convergence relation model verdict

| Question | Answer |
|---|---|
| Is `ConvergenceRelation` a relationship model? | **NO — a subordination-standing vocabulary** |
| Is every member executably verified? | **YES — 4 of 4, uniquely** |
| Is it extensible by registration? | **NO — a Python enum; `ART-17` tension** |
| Is it guarded against drift? | **NO — absent from the 9 guarded projections** |
| Is it a parallel authority model? | **NO** |
| Is it a duplicate vocabulary? | **YES — 3 near-verbatim shared members, 1 divergent** |
| Classification | **MOST RIGOROUS · LEAST EXTENSIBLE · UNGUARDED · DUPLICATED** |

---


## 5. GOVERNED Assessment

### 5.1 The term, measured

| Property | Value |
|---|---|
| Home | `ConvergenceRelation.GOVERNED = "governed"` |
| Definition | *"Holds law over a strictly narrower subject. Must restate none of the canonical law."* |
| Occurrences in `UCOS-CAA-001` | **0** |
| Occurrences in `uckp.relation-type` | **0** |
| Occurrences in `uckp.relationship-class` | **0** — though `governance` is a class member |
| Verification | `reserved = {*article_ids(), *gates(), constitution_id}`; fails if `reserved ∩ string_literals(source) ≠ ∅` |
| Code's stated rationale | *"A narrower authority is legitimate precisely while it restates none of the canonical law… what separates 'a second authority over a smaller subject' from 'a second copy of the same law'."* |

### 5.2 What `GOVERNED` means semantically, and whether the model already holds it

This is the test the mission's first principle requires: does a canonical source already carry this meaning?

| Candidate model term | Meaning | Is it `GOVERNED`? |
|---|---|---|
| `governs` (V-1, relation) | X governs Y — an edge asserting governance **over another object** | **NO — different subject; `GOVERNED` is a standing of a surface, not an edge between objects** |
| `governance` (V-2, class) | the class a governance-natured relationship belongs to | **NO — a class, not a relation** |
| `derived-from` (V-1) | X derives from Y | **partially — a `GOVERNED` surface does derive, but `derived-from` carries no narrowness or non-restatement condition** |
| `extends` (V-1) | X extends Y | **NO — extension widens; `GOVERNED` narrows** |
| `inherits` (V-1) | X inherits from Y | **NO** |

> **`GOVERNED` is not a duplicate of any model term. It expresses a composite the model does not: *derives from the canonical law* **and** *holds law over a strictly narrower subject* **and** *restates none of the canonical law*. The third conjunct is the load-bearing one and no relation in `uckp.relation-type` carries a non-restatement condition. `GOVERNED` names a standing on the subordination axis, and the model's 17 relations are all on the graph-edge axis.**

### 5.3 Therefore `GOVERNED` is not the duplication

| Question | Answer |
|---|---|
| Does `GOVERNED` duplicate a model relation? | **NO** |
| Does it duplicate `ORTHOGONAL`? | **NO — §6 shows they are opposite on derivation** |
| Is it a rival to the model? | **NO — it operates on a different axis** |
| Is its home the right home? | **it is the *only* home; whether that home is canonical is §12's question** |
| Is it executably verified? | **YES — uniquely, by source parsing** |

### 5.4 What `GOVERNED` supplies that nothing else does

| Property | Supplied by `GOVERNED` | Supplied elsewhere |
|---|---|---|
| Narrower-subject authority is **permitted** | **YES** | nowhere else |
| The permission is **conditional** | **YES — non-restatement** | nowhere else |
| The condition is **mechanically checked** | **YES — AST string literals** | nowhere else |
| No grantor is required | **YES** | nowhere else |
| The chain still terminates at the root | **YES — it derives** | `ART-01` generally |

**Five properties, all unique to this term. `GOVERNED` is the repository's only mechanism for admitting bounded constitutional authority without an appointing office, which is why the predecessor determination identified it as the eligibility path.**

### 5.5 The gap `GOVERNED` leaves

| Gap | Consequence |
|---|---|
| It is absent from `UCOS-CAA-001` | an instrument cannot declare it in `subordinate_instruments` and have the declaration recognised by the alignment verifier |
| It is a Python enum member | a future fifth standing requires an engine change |
| It is unguarded by `verify_vocabulary_alignment()` | its divergence from CAA went unmeasured until this chain measured it |
| No instrument currently declares it | the gate verifies declared relations; none declares `GOVERNED` |

### 5.6 GOVERNED verdict

| Question | Answer |
|---|---|
| Does `GOVERNED` duplicate any canonical term? | **NO** |
| Is it semantically necessary? | **YES — 5 properties unique to it** |
| Is it on the graph axis or the subordination axis? | **subordination** |
| Is it executably verified? | **YES — the only relation vocabulary member class that is** |
| Is it declared in CAA? | **NO** |
| Is it extensible by registration? | **NO — enum member** |
| Should it be merged away? | **NO — merging is forbidden here and would destroy a unique meaning** |
| Classification | **SEMANTICALLY UNIQUE · MECHANICALLY VERIFIED · ABSENT FROM THE DECLARING INSTRUMENT** |

---

## 6. ORTHOGONAL Assessment

### 6.1 The term, measured in both of its homes

`ORTHOGONAL` appears twice in `UCOS-CAA-001`, on **two different axes**, and this is the source of its trouble.

| Home | Axis | Content |
|---|---|---|
| `authority_roles.ORTHOGONAL` | **role** | `may_hold_authority: **False**` · `cardinality: FEW` · articles `UCKP-ART-01`, also `ART-04` · *"governs a distinct, non-overlapping axis of constitutional responsibility — such as recognition and classification of constitutional instruments"* |
| `subordination_relations.ORTHOGONAL` | **relation** | *"holds **independent, non-overlapping authority** on a different axis and **neither derives from nor answers to** the authority above it; the two are declared non-competing rather than ranked"* |

| Occurrences in `convergence.py` | **0** |
| Occurrences in `uckp.relation-type` / `relationship-class` | **0** |
| Code-side counterpart | **the role exists in `AUTHORITY_ROLES`; the relation has none** |

### 6.2 The internal tension, measured

| Statement | Source | Implication |
|---|---|---|
| `may_hold_authority: False` | `authority_roles.ORTHOGONAL` | an `ORTHOGONAL` instrument **may not hold authority** |
| *"holds independent, non-overlapping **authority**"* | `subordination_relations.ORTHOGONAL` | an `ORTHOGONAL` surface **holds authority** |
| *"neither derives from nor answers to the authority above it"* | same | it has **no terminating chain** |
| *"every other chain terminates at it"* | `UCKP-ART-01` | **every** chain must terminate at the root law |

> **Two clauses in one instrument say opposite things about whether an `ORTHOGONAL` instrument holds authority, and the relation's *"answers to nothing"* clause has no reading under `ART-01` that leaves every chain terminating at the root. The role is measurable and consistent — `CAA-INV-08` requires an explicit bounded scope, and `_role_findings()` checks the role table against code. The relation is neither measurable nor consistent, because no code reads it.**

### 6.3 `ORTHOGONAL` versus `GOVERNED` — they are opposites, not duplicates

| Property | `ORTHOGONAL` | `GOVERNED` |
|---|---|---|
| Derives from the canonical authority | **NO — explicitly** | **YES** |
| Answers to it | **NO — explicitly** | **YES** |
| Subject breadth | a **different** axis | a **narrower** subject on the same axis |
| Ranked against the authority | *"non-competing rather than ranked"* | **subordinate** |
| Non-restatement condition | **none declared** | **required and checked** |
| Mechanically verified | **NO** | **YES** |
| Compatible with `ART-01` chain termination | **tension** | **YES** |

**They are not two spellings of one meaning. They are two different answers to "how does a bounded authority stand to the root?" — one says *beside it*, the other says *beneath it and narrower*. Only the second has a test, and only the second is consistent with `ART-01`.**

### 6.4 Which is correct for a bounded governance capability

| Consideration | Favours |
|---|---|
| `ART-01` — every chain terminates at the root | **`GOVERNED`** |
| `ART-03` — a second root is void | **`GOVERNED`** |
| Mechanical verifiability | **`GOVERNED`** |
| `CAA-INV-08`'s bounded-scope requirement for `ORTHOGONAL` | applies to the **role**, which remains available |
| The existing `ORTHOGONAL` occupant (`CMG-000001`) | its axis question is unresolved and not resolvable here |

**Recorded and not asserted as a resolution: the `ORTHOGONAL` relation's "answers to nothing" reading is the one clause in the relation vocabulary that no article supports. This determination reports it; `UCOS-CAA-001`'s non-goals forbid deciding a conflict between located instruments, and this determination has no authority to.**

### 6.5 Is `ORTHOGONAL` a duplicate vocabulary member?

| Test | Result |
|---|---|
| Does it duplicate `GOVERNED`? | **NO — opposite on derivation** |
| Does it duplicate a model relation? | **NO** |
| Does the **role** duplicate the **relation**? | **they share a name across two axes**, which is itself a drift risk: one name, two meanings, one instrument |
| Is the role sound? | **YES — crosswalked to code, checked, `CAA-INV-08`-bounded** |
| Is the relation sound? | **NO — internally contradictory and unread** |

> **The sharpest statement available: `ORTHOGONAL` is one name carrying two meanings on two axes inside one instrument. The role meaning is checked and consistent. The relation meaning contradicts the role meaning and has no article supporting it. This is not duplication across homes — it is **collision within a home**, and the mission's principle "one semantic meaning = one canonical source" has a mirror case here: one source carrying two semantic meanings.**

### 6.6 ORTHOGONAL verdict

| Question | Answer |
|---|---|
| Is `ORTHOGONAL` a duplicate of `GOVERNED`? | **NO — they are opposites** |
| Is the role sound? | **YES — crosswalked, checked, bounded** |
| Is the relation sound? | **NO — contradicts the role; unsupported by `ART-01`; read by no code** |
| Is one name carrying two meanings? | **YES — role axis and relation axis** |
| Is it merged, renamed or removed here? | **NO** |
| Classification | **ROLE SOUND · RELATION CONTRADICTORY AND UNREAD · NAME COLLIDES ACROSS TWO AXES** |

---

## 7. Authority Chain Relationship Assessment

### 7.1 How an authority chain is expressed today

| Layer | Mechanism | Terms | Crosswalked |
|---|---|---|---|
| Object → its authority | Facet 5 `AuthorityBinding(tier, derives_from, instrument)` | 4 tiers | **YES — `uckp.authority-tier`, checked by `require_lawful()`** |
| Object → object, as an edge | Facet 9 `Relationship(relation, target, relationship_class)` | `derived-from` / `governs` in V-1 | **YES — checked by `require_lawful()`** |
| Instrument → the root law | `constitutional_superior` block | `authority`, `home`, `role`, `relation`, `articles` | **role: YES · relation: NO** |
| Surface → its canonical model owner | `ConvergenceRelation` | 4 members | **NO** |
| Assimilated object → the law | `relationships=(Relationship("derived-from", parent_urn, "authority"),)` | `derived-from` + class `authority` | **YES** |

### 7.2 The measured exemplar

`engine/uckp/assimilation.py` builds every assimilated object's authority chain as:

```
Relationship("derived-from", parent_urn, "authority")
```

with the stated purpose: *"which is what gives the whole assimilated population a chain that terminates at the constitution instead of floating beside it."*

| Property | Value |
|---|---|
| Relation term | `derived-from` — **a V-1 member** |
| Relationship class | `authority` — **a V-2 member** |
| Checked by | `require_lawful()` → `require_term()` on both |
| Fallback when no parent | `root_law_urn()` |
| Scale | applied uniformly across the assimilated population |

**The authority chain, on the object plane, is fully converged: one relation term, one class, both from the canonical vocabulary, both checked at admission. This is what convergence looks like when it is achieved.**

### 7.3 Where the authority chain is not converged

| Gap | Measurement |
|---|---|
| The instrument→root relation term | `subordination_relations`, uncrosswalked, read by no code |
| The surface→model-owner relation term | `ConvergenceRelation`, a Python enum, unguarded |
| The live edge `Authorizes` / `Authorized-By` | **200 edges**, expressing governance, **absent from the crosswalk**, and expressible as `governs` + `direction` |
| `evidenced_by` / `validated_by` in the crosswalk | correctly bound — but to `constitutional` and `validation` classes, not `authority` |

### 7.4 The `Authorizes` measurement

| Fact | Value |
|---|---|
| `Authorizes` edges | **100** |
| `Authorized-By` edges | **100** |
| Model term that carries this meaning | **`governs`** — V-1 member |
| Model class | **`authority`** — V-2 member |
| Present in `relationship_kind_bindings` | **NO** |
| Consequence per the crosswalk's own rule | *"an unmodelled relationship and fails `CAA-INV-05`"* |

> **Two hundred edges assert authority relationships using a term the canonical vocabulary does not contain, in a population the crosswalk does not cover, while the model holds `governs` and the class `authority` ready for exactly this. Authority relationships — the most consequential kind in the repository — are the ones expressed in the least converged vocabulary.**

### 7.5 Does a parallel authority model exist?

| Test | Result |
|---|---|
| Does a second instrument declare what a relationship **is**? | **NO — `CAA-INV-05` holds** |
| Does a second instrument declare the supreme authority? | **NO — `CAA-INV-01` holds** |
| Does a second object model exist? | **NO — `CAA-INV-07` holds** |
| Do multiple vocabularies express authority relations? | **YES — V-1 `governs`, V-6 `Authorizes`, V-4/V-5 subordination standings** |
| Is that a parallel **model**? | **NO** |
| Is it a parallel **vocabulary**? | **YES** |

**The distinction is preserved: no parallel authority model. Multiple vocabularies expressing authority relations, which is the breach the mission names.**

### 7.6 Authority chain relationship verdict

| Question | Answer |
|---|---|
| Is the object-plane authority chain converged? | **YES — `derived-from` + class `authority`, checked** |
| Is the instrument-plane chain converged? | **NO — role yes, relation no** |
| Is the surface-plane chain converged? | **NO — `ConvergenceRelation`, unguarded** |
| Are live authority edges converged? | **NO — 200 `Authorizes`/`Authorized-By` edges, uncrosswalked** |
| Is a parallel authority model present? | **NO** |
| Does the model lack any needed authority term? | **NO — `governs` + `authority` suffice** |
| Classification | **CONVERGED ON THE OBJECT PLANE · UNCONVERGED ON THREE OTHERS** |

---

## 8. Ownership Relationship Assessment

### 8.1 The ownership relation, measured

| Layer | Mechanism | Term | Direction | Crosswalked |
|---|---|---|---|---|
| Object's accountable party | Facet 7 `Ownership(owner, stewards)` | not a relation — a **facet value** | n/a | n/a |
| Ownership as an edge | V-1 `owns` · V-2 class `ownership` | `owns` | forward | **YES** |
| Projection kind | `owned_by` | `owns` | **inverse** | **YES — `article: UCKP-ART-06`** |
| Live edge population | **no ownership edge type exists among the 16** | — | — | **n/a** |

### 8.2 `owned_by` is the exemplar of the whole determination

| Field | Value |
|---|---|
| kind | `owned_by` |
| `uckp_class` | `ownership` |
| `uckp_relation` | **`owns`** |
| `direction` | **`inverse`** |
| `article` | `UCKP-ART-06` |
| `meaning` | *"the accountable owner — the ownership facet, read from the owned…"* |

> **This single binding is the answer to the mission's question, in miniature. Two readings of one relationship — *owns* and *owned by* — are expressed as **one canonical term plus a declared direction**, not as two terms. No `owned-by` member was added to `uckp.relation-type`. The 17-term vocabulary stays at 17 while the projection emits both readings. Compare `Evolves-From-Inverse` in the live population, which solved the identical problem by inventing a term.**

### 8.3 The measured contrast

| Problem | Converged solution | Unconverged solution |
|---|---|---|
| express *owns* and *owned by* | `owns` + `direction: inverse` | — |
| express *depends on* and *required by* | — | **`Depends-On` + `Required-By`** — two types, 9,477 edges |
| express *evolves from* and its inverse | — | **`Evolves-From` + `Evolves-From-Inverse`** — a term named for its own inversion |
| express *authorizes* and *authorized by* | — | **`Authorizes` + `Authorized-By`** — two types, 200 edges |

**One converged pattern exists and is declared. Three unconverged instances exist in the live population, totalling 9,682 edges, each solving the direction problem by term multiplication.**

### 8.4 Ownership relationships in the live population

| Test | Result |
|---|---|
| Ownership edge types among the 16 | **0** |
| Edges with an attested owner | **0 of 13,361** |
| Ownership expressed as an edge anywhere | **NO** |
| Ownership expressed as Facet 7 | **YES — 6,338 objects, 58% path-shaped, 0 stewards** |
| Governed ownership assignments | **0** |

**Ownership is not under-converged in the relation vocabulary — it is absent from it. The crosswalk declares `owned_by` for the UGA projection; the 13,361-edge population carries no ownership edge at all.**

### 8.5 Ownership relationship verdict

| Question | Answer |
|---|---|
| Does the model hold an ownership relation? | **YES — `owns`, class `ownership`** |
| Is the forward/inverse problem solved canonically? | **YES — `owned_by` = `owns` + `direction: inverse`** |
| Is that pattern applied elsewhere? | **NO — 3 unconverged instances, 9,682 edges** |
| Do ownership edges exist in the population? | **NO — 0 of 13,361** |
| Is a new ownership relation required? | **NO** |
| Classification | **CANONICAL PATTERN DECLARED AND EXEMPLARY · APPLIED ONCE · OWNERSHIP EDGES ABSENT** |

---


## 9. Evolution Relationship Assessment

### 9.1 The evolution relations the model holds

| Term | Axis | Meaning |
|---|---|---|
| `supersedes` | V-1 relation | X supersedes Y |
| `derived-from` | V-1 relation | X derives from Y |
| `generated-from` | V-1 relation | X is generated from Y |
| `extends` | V-1 relation | X extends Y |
| `evolution` | V-2 class | the class an evolution-natured relationship belongs to |
| `historical` | V-2 class | the class for retired states |
| **`future`** | V-2 class | **a declared class for relationships whose nature is not yet decided** |

**Seven terms across two axes, including a class explicitly reserved for undetermined future relationships.**

### 9.2 The evolution relation in the live population

| Type | Edges | Model equivalent | Crosswalked |
|---|---|---|---|
| `Evolves-From` | **5** | `supersedes` (inverse) or `derived-from` (forward), class `evolution` | **NO** |
| **`Evolves-From-Inverse`** | **5** | the same kind, read forward | **NO** |

### 9.3 `Evolves-From-Inverse` — the anti-pattern named by the architecture itself

Placed side by side, this is the sharpest measurement in the determination.

| The rule | The instance |
|---|---|
> *"`direction` records whether the projection emits the model's edge or its inverse, **because a kind read backwards is still that kind and pretending otherwise would invent a term to avoid saying so.**"* — `CAA.$kind_binding_comment` | **`Evolves-From-Inverse`** — a live edge type whose name is the word "inverse" appended to another type |

| Assessment | Statement |
|---|---|
| Is this the forbidden pattern? | **YES — verbatim** |
| Does the model lack a term for it? | **NO — `supersedes` + `direction` expresses it** |
| Did the architecture anticipate it? | **YES — and wrote the field and the prose to prevent it** |
| Was the prevention applied to this population? | **NO — the population is not a declared projection** |
| Scale | 5 edges of 13,361 — **small in count, total in principle** |

> **The count is not the finding. The finding is that a mechanism exists, its rationale is written down in the instrument that declares it, and a population outside that instrument's declared scope committed precisely the error the rationale describes. Convergence is not failing because the architecture lacks an answer; it is failing at the boundary of where the answer is declared to apply.**

### 9.4 Evolution as lifecycle versus evolution as relationship

These are two mechanisms and both are converged in isolation.

| Concern | Mechanism | Terms | Converged |
|---|---|---|---|
| An object's own evolution | Facet 10 `lifecycle` + Facet 11 `temporal-history` + Facet 18 `evolution-history` | 10 stages · 20 transitions | **YES — `transition_to()` raises `LawViolation` on an unlawful path** |
| A relationship of evolution between objects | V-1 `supersedes` / `derived-from` + V-2 `evolution` | checked by `require_lawful()` | **YES on the object plane** |
| Retirement of a rival surface | `ConvergenceRelation.SUPERSEDED` | `not path.exists()` | **YES executably — but in an unguarded vocabulary** |
| Evolution edges in the live population | `Evolves-From` / `Evolves-From-Inverse` | uncrosswalked | **NO** |

### 9.5 The three `SUPERSEDED`-family meanings, distinguished

A term-collision risk worth stating explicitly, because three near-identical names sit on three axes:

| Name | Axis | Subject | Meaning |
|---|---|---|---|
| `supersedes` | V-1 graph relation | object → object | this object replaces that one |
| `superseded` | V-5 subordination relation | a **surface** | this implementation is retired and **must be absent** |
| `SUPERSEDED` | V-4 subordination relation | a **surface** | *"once held a competing definition and is now gone"* |
| `superseded` | lifecycle stage | an **object's stage** | reachable from `ratified`, `implemented`, `operational`, `deprecated` |

**Four occurrences, three distinct meanings, four homes. `supersedes` (edge) and `superseded` (stage) are legitimately different concepts sharing a root word. V-4 and V-5 `SUPERSEDED`/`superseded` are the same concept in two homes — the duplication of §4.5.**

### 9.6 Infinite future evolution support

| Requirement | Mechanism | Bounded |
|---|---|---|
| Unlimited future evolution relation types | V-1 open, register-then-use | **unbounded** |
| Unlimited future relationship classes | V-2 open; includes `future` | **unbounded** |
| Unlimited future lifecycle stages | register-then-use; 6 admitted by assimilation | **unbounded** |
| Unlimited future emitted kinds | *"a seventh kind is one appended entry… never an engine change"* | **unbounded** |
| Unlimited future **subordination standings** | **`ConvergenceRelation` is a Python enum** | **BOUNDED — a code edit** |

**Four of five unbounded. The fifth is the subordination axis, and its finiteness is the one hardcoded assumption this determination locates in the relation vocabulary layer.**

### 9.7 Evolution relationship verdict

| Question | Answer |
|---|---|
| Does the model hold evolution relations? | **YES — 4 relations, 3 classes** |
| Is `future` a declared class? | **YES** |
| Is the live evolution edge type converged? | **NO — and it is the named anti-pattern** |
| Is object lifecycle evolution converged? | **YES — enforced transitions** |
| Are the `SUPERSEDED`-family meanings distinct? | **3 distinct meanings across 4 homes; 1 pair is a true duplication** |
| Is future evolution unbounded? | **4 of 5 axes yes; subordination standings no** |
| Classification | **MODEL SUFFICIENT · LIVE POPULATION CARRIES THE FORBIDDEN PATTERN · ONE FINITE AXIS** |

---

## 10. Infinite Relationship Scope Assessment

### 10.1 The five mandatory infinities, tested

| # | Infinity | Mechanism | Measured openness | Holds |
|---|---|---|---|---|
| **1** | **entities** | `ART-07` *"Every object is a node"* · `ART-08` discovery | UCKO population 6,338, grown by provider discovery | **YES** |
| **2** | **scopes** | `UISD` axis `scope` | 11 axes, no upper limit declared | **YES** |
| **3** | **directions** | **`direction` field on every binding** · `inverse_of` on every edge | 3 of 6 bindings use `inverse` | **YES — and this is the converged mechanism** |
| **4** | **contexts** | `UCXI` open taxonomy · Facets 17, 28–33 | `closed_set: false`, `upper_limit: null` | **YES** |
| **5** | **future relationship types** | V-1 + V-2 register-then-use · the crosswalk is DATA | *"a seventh kind is one appended entry (`UCKP-ART-17`) and never an engine change"* | **YES** |

**Five of five hold. Every one is a property of the canonical model or its DATA crosswalk — none depends on any of the four unconverged vocabularies.**

### 10.2 Direction is the infinity the repository already solved correctly

| Approach | Terms required for N relationship kinds read both ways | Scales |
|---|---|---|
| **Canonical — term + `direction`** | **N** | **YES — unbounded** |
| Unconverged — a term per reading | **2N** | **NO — and each inverse term is a new semantic source** |

| Measured | Value |
|---|---|
| Model relations | **17** |
| Live types expressing 8 kinds both ways | **16** |
| Terms the canonical approach would need for those 8 kinds | **8** |
| Terms the live population uses | **16** |
| Excess terms attributable to direction-by-multiplication | **8** |

> **Eight of the sixteen live edge types exist only because a direction was expressed as a term instead of as a flag. Under the canonical pattern the same 13,361 edges need eight relation terms, all eight already in `uckp.relation-type`. Direction-by-multiplication is not merely untidy — it doubles the vocabulary for every new kind, which is a hardcoded finite assumption dressed as expressiveness.**

### 10.3 Where a finite assumption is measurably present

| # | Finite assumption | Location | Extensible by |
|---|---|---|---|
| **1** | `ConvergenceRelation` is a closed Python enum with `coerce()` hard-refusing unknowns | `convergence.py` | **a code edit — `ART-17` tension** |
| **2** | `subordination_relations` declares *"No fourth relation is created"* while carrying a fourth | `UCOS-CAA-001` | unclear — read by no code |
| **3** | Direction-by-multiplication in the live population | `relationships.json` | doubling per kind |

**Three finite assumptions. The crosswalk, the model relation vocabulary, the class vocabulary, the lifecycle vocabulary and the context taxonomy are all open. The finiteness is concentrated entirely on the subordination axis and in the uncrosswalked population.**

### 10.4 What the crosswalk guarantees about scope

| Guarantee | Basis |
|---|---|
| A new emitted kind never edits an engine | *"one appended entry… never an engine change"* |
| A new kind must name its class, relation, direction and article | the 5-field binding shape |
| An unmapped kind is a **failure**, not a default | *"an unmodelled relationship and fails `CAA-INV-05`"* |
| The terms a kind may use stay honest | `verify_binding` checks the map against the vocabularies |
| The vocabularies are not copied into the map | `model_term_sources.note` — *"These lists are NOT copied here"* |

**Five guarantees. All five hold for the six mapped kinds. None applies to the sixteen unmapped live types, because the population is not a declared projection.**

### 10.5 Infinite relationship scope verdict

| Question | Answer |
|---|---|
| Do all five mandatory infinities hold? | **YES — 5 of 5** |
| Is direction handled canonically? | **YES in the crosswalk — NO in the live population** |
| How many excess terms does direction-by-multiplication cost? | **8 of 16 live types** |
| Are hardcoded finite assumptions present? | **YES — 3, all on the subordination axis or in the uncrosswalked population** |
| Does the canonical model impose any limit? | **NO** |
| Classification | **FIVE INFINITIES HOLD · DIRECTION SOLVED CANONICALLY AND APPLIED PARTIALLY** |

---

## 11. Duplicate Vocabulary Assessment

### 11.1 The duplication register

| # | Duplicated meaning | Homes | Kind of duplication | Measured |
|---|---|---|---|---|
| **DV-1** | *delegates* | V-4 `DELEGATES` · V-5 `delegates` | near-verbatim definitions | **breach** |
| **DV-2** | *superseded* | V-4 `SUPERSEDED` · V-5 `superseded` | near-verbatim definitions | **breach** |
| **DV-3** | *projection* | V-4 `PROJECTION` · V-5 `projection` | near-verbatim definitions | **breach** |
| **DV-4** | *depends on* | V-1 `depends-on` · V-3 `depends_on` · V-6 `Depends-On` | **three spellings** — V-3 is a declared crosswalk (lawful), V-6 is not | **1 lawful mapping, 1 breach** |
| **DV-5** | the fourth subordination standing | V-4 `ORTHOGONAL` · V-5 `GOVERNED` | **divergent meanings, not duplicates** | **not a duplication — a contradiction** |
| **DV-6** | `ORTHOGONAL` across two axes in one instrument | `authority_roles` · `subordination_relations` | **one name, two meanings** | **collision within a home** |
| **DV-7** | 8 forward/inverse live type pairs | V-6 | direction-by-multiplication | **breach — 8 excess terms** |

**Seven register entries. Four are true duplications of meaning across homes; one is a contradiction; one is an intra-home name collision; one is systematic direction-by-multiplication.**

### 11.2 What is *not* duplicated — stated to keep the assessment honest

| Not duplicated | Basis |
|---|---|
| The relationship **model** | `CAA-INV-05` — exactly one instrument declares what a relationship is |
| The object model | `CAA-INV-07` — one, repository-wide |
| The supreme authority | `CAA-INV-01` — `EXACTLY_ONE` |
| The identity mint | `CAA-INV-04` — one, append-only |
| `owned_by` versus `owns` | a **declared direction**, not a duplicate |
| `GOVERNED` versus any model relation | different axis; §5.2 |
| `supersedes` (edge) versus `superseded` (lifecycle stage) | genuinely different concepts sharing a root word |
| V-3 versus V-1 | V-3 is a **crosswalk**, which is the sanctioned form of restatement — it maps rather than redefines |

> **The duplication is confined to the subordination axis and to the uncrosswalked live population. Every model-plane vocabulary is singular, guarded and enforced. This matters for §12: the problem is not that the repository has many relation vocabularies — a crosswalk makes many surfaces lawful — it is that four of the six are not crosswalked to the one canonical model.**

### 11.3 Why the duplication went undetected

| Guard | What it covers | Does it cover the breaches |
|---|---|---|
| `require_lawful()` | 6 vocabulary-bound facets on every object | **object plane only** |
| `verify_binding()` → `_vocabulary_findings()` | the 6 declared `relationship_kind_bindings` | **NO — not `subordination_relations`, not the live population** |
| `verify_binding()` → `_role_findings()` | authority roles, code↔data | **roles only, and it passes** |
| `verify_vocabulary_alignment()` | **9** projections of registered vocabularies | **NO — `ConvergenceRelation` is not among the 9** |
| `FG-15-NO-PARALLEL-AUTHORITY` | declared subordinate surfaces | **NO — mutation surfaces and the live population are undeclared** |
| `FG-16-ONE-MEASUREMENT` | one population, one measurement | not engaged here |

**Six guards. `verify_binding()` returns 0 findings. Every breach in §11.1 sits in a gap between guards, and each gap is a scope boundary rather than a defect in any guard.**

### 11.4 The structural cause

| Vocabulary | Has a code counterpart | Has a checker | Diverged |
|---|---|---|---|
| authority roles | **YES — `AUTHORITY_ROLES`, 8** | **YES — `_role_findings()`** | **NO — 8 of 8 match** |
| relationship kinds | **YES — the vocabularies** | **YES — `_vocabulary_findings()`** | **NO** |
| **subordination relations** | **NO** | **NO** | **YES** |

> **Within one instrument, the two vocabularies that have code counterparts and checkers have not diverged, and the one that has neither has. The cause is not carelessness; it is the absence of a crosswalk on exactly one axis. This is the most directly actionable finding in the determination and it is why §12's options are all variants of "apply the existing crosswalk pattern to the axis that lacks it".**

### 11.5 Duplicate vocabulary verdict

| Question | Answer |
|---|---|
| Are duplicate relation vocabularies present? | **YES — 7 register entries** |
| Are duplicate authority **models** present? | **NO** |
| Is semantic drift present? | **YES — 3 spellings of one meaning; 1 contradiction; 1 intra-home collision** |
| Did any guard fail? | **NO — every breach is in a gap between guard scopes** |
| Is the cause identifiable? | **YES — one axis has no crosswalk and no code counterpart** |
| Is anything merged here? | **NO** |
| Classification | **SEVEN BREACHES · ALL IN SCOPE GAPS · ONE STRUCTURAL CAUSE** |

---

## 12. Canonical Resolution Options

Options are presented for a competent authority to decide. **None is selected for execution, and §13 records a direction rather than a decision. The actor competent to decide any of them does not exist (predecessor chain, measured).**

### 12.1 The canonical source, first — because every option presupposes it

| Element | Canonical source | Guard |
|---|---|---|
| What a relationship **is** | `UCKP-ART-07` at `engine/uckp/graph.py` | `CAA-INV-05` |
| Relation terms | `uckp.relation-type` — 17, open | `require_lawful()` |
| Relationship classes | `uckp.relationship-class` — 12, open | `require_lawful()` |
| The crosswalk pattern | `relationship_kind_bindings` — 5 fields per kind, DATA | `_vocabulary_findings()` |

**This is settled and no option changes it. The question is only how the four uncrosswalked vocabularies relate to it.**

### 12.2 The five options

| # | Option | Mechanism | Satisfies "one meaning = one source" | Assessment |
|---|---|---|---|---|
| **O-1** | **Do nothing** | — | **NO** | **REFUSED** — 7 breaches stand; `Evolves-From-Inverse` remains the named anti-pattern in force |
| **O-2** | **Extend `_vocabulary_findings()` to check `subordination_relations`** | a checker change | **PARTIALLY** | **INSUFFICIENT ALONE** — it would measure the V-4/V-5 divergence without resolving which is canonical, and would leave V-6 uncovered |
| **O-3** | **Apply the existing crosswalk pattern to the subordination axis and register the live population as a declared projection** | DATA entries in the existing shape | **YES** | **STRONGEST** — §12.3 |
| **O-4** | **Collapse V-4 and V-5 into a single home** | choose one home, retire the other | **YES for the subordination axis** | **PARTIAL** — leaves V-6's 16 types and the `ORTHOGONAL` intra-home collision unaddressed; and "retire" means the file must be **absent**, per `SUPERSEDED` |
| **O-5** | **Create a unified relation registry above all six** | a new instrument | **NO** | **REFUSED** — `ART-03` voids a second definition of an existing primitive; `extension_rule.what_this_forbids` names a second relationship graph explicitly; it would be a seventh vocabulary |

### 12.3 O-3 examined, because it is the only option that uses no new mechanism

| Component | Existing mechanism reused | New mechanism |
|---|---|---|
| Bind each subordination standing to a model class, relation, direction and article | the 5-field `relationship_kind_bindings` shape | **none** |
| Keep terms referenced, not copied | `model_term_sources.note` — *"NOT copied here"* | **none** |
| Check the bindings against the vocabularies | `_vocabulary_findings()` | **none** |
| Register `00-BOOK/DATA/relationships.json` as a declared projection with its producer and role | the `projections` list — 3 entries today | **none** |
| Bind its 16 types to 8 model relations plus `direction` | §2.7's mapping — all 16 already map | **none** |
| Make an unmapped kind a failure | already the declared rule | **none** |
| Admit a future standing by registration | the map is DATA — *"one appended entry"* | **none** |

| Property | Result under O-3 |
|---|---|
| New relations created | **0** |
| New vocabularies created | **0** |
| Terms merged | **0** — mapping is not merging |
| Terms renamed | **0** |
| `Evolves-From-Inverse` | becomes `supersedes` + `direction`, **as a binding**, without editing the edge population |
| `ConvergenceRelation`'s finiteness | addressed only if its members are bound as DATA rather than enum members |
| The `ORTHOGONAL` role/relation collision | **not resolved** — it is a contradiction, and §6.4 places it outside this determination's competence |

### 12.4 What no option may do

| Forbidden in every option | Basis |
|---|---|
| Merge two terms into one | mission constraint; and merging destroys the `GOVERNED`/`ORTHOGONAL` distinction |
| Rename a live edge type | it would rewrite relationship data |
| Add a relation to `uckp.relation-type` | none is needed — all 16 live types map to existing terms |
| Create a seventh vocabulary | `ART-03`, `ART-18` |
| Copy the term lists into a second home | `model_term_sources.note` refuses exactly this |
| Resolve the `ORTHOGONAL` contradiction | `UCOS-CAA-001` non-goal; no competent instrument |
| Execute any option | no actor exists |

### 12.5 Canonical resolution options verdict

| Question | Answer |
|---|---|
| Is the canonical source determined? | **YES — `ART-07` + V-1 + V-2, unchanged by every option** |
| How many options were assessed? | **5** |
| How many are refused outright? | **2 — O-1, O-5** |
| How many are insufficient alone? | **2 — O-2, O-4** |
| How many use no new mechanism? | **1 — O-3** |
| Is any option selected for execution? | **NO** |
| Is any term merged, renamed or created here? | **NO** |
| Classification | **CANONICAL SOURCE SETTLED · FIVE OPTIONS ASSESSED · NONE EXECUTED** |

---


## 13. Permanent Direction

A **direction**, not a decision. No option from §12 is selected, scheduled or authorized.

### 13.1 The direction in one statement

> **Every relation vocabulary in the repository either *is* the canonical model or *binds to it* through a declared crosswalk carrying a class, a relation, a direction, an article and a meaning. A term is never restated in a second home, a direction is never expressed as a second term, and a kind absent from the crosswalk is a failure rather than a default. The model stays at 17 relations and 12 classes however many surfaces emit however many kinds.**

### 13.2 The permanent invariants

| # | Invariant | Enforced by | Enforced today |
|---|---|---|---|
| **P-01** | Exactly one instrument declares what a relationship is | `CAA-INV-05` | **YES** |
| **P-02** | Every emitted kind binds to a model class and relation | `_vocabulary_findings()` | **6 kinds yes · 16 live types no** |
| **P-03** | Every binding declares a `direction` | the 5-field shape | **6 of 6 yes** |
| **P-04** | A backwards reading is never a new term | `$kind_binding_comment` | **breached — `Evolves-From-Inverse`** |
| **P-05** | Term lists are referenced, never copied | `model_term_sources.note` | **YES** |
| **P-06** | A kind absent from the map is a failure | declared rule | **declared, unmeasured for the live population** |
| **P-07** | Every binding names the article it holds under | the 5-field shape | **6 of 6 yes** |
| **P-08** | A new kind is one appended DATA entry, never an engine change | `ART-17` | **YES for the map · NO for `ConvergenceRelation`** |
| **P-09** | Every vocabulary with a code counterpart is code↔data checked | `_role_findings()` pattern | **roles yes · relations no** |
| **P-10** | One name never carries two meanings in one instrument | mission principle | **breached — `ORTHOGONAL`** |
| **P-11** | A retired vocabulary home must be **absent**, not merely deprecated | `SUPERSEDED` test | **not applicable yet** |
| **P-12** | Every relation vocabulary is guarded against drift | `verify_vocabulary_alignment()` pattern | **9 guarded · `ConvergenceRelation` and `subordination_relations` unguarded** |

**Twelve invariants. Five hold fully, seven hold partially or are breached — and every one of the seven is enforceable by a mechanism that already exists.**

### 13.3 The ordering

| Layer | Act | Requires an actor |
|---|---|---|
| **1** | Decide which home is canonical for the subordination axis | **YES — and no competent instrument exists** |
| **2** | Resolve the `ORTHOGONAL` role/relation contradiction | **YES** |
| **3** | Bind the subordination standings as DATA in the crosswalk shape | **YES** |
| **4** | Register the live population as a declared projection | **YES** |
| **5** | Bind its 16 types to 8 model relations + `direction` | **YES** |
| **6** | Extend the drift guard to cover the subordination vocabularies | **YES** |
| **7** | Verification thereafter | **NO — `_vocabulary_findings()` and `FG-15` run** |

**Six acts require an actor. One is automatic. The actor absence measured across the predecessor chain is unchanged.**

### 13.4 Why this direction is permanent

| Property | Basis |
|---|---|
| Adds no relation | all 16 live types map to existing terms |
| Adds no vocabulary | it binds existing ones |
| Merges no term | mapping preserves both readings and both meanings |
| Renames nothing | no edge data is touched |
| Closes no vocabulary | V-1, V-2 and the map remain open |
| Scales without engine changes | *"one appended entry… never an engine change"* |
| Cannot silently drift once bound | `_vocabulary_findings()` fails closed |
| Survives a new emitting surface | register it as a projection and bind its kinds |
| Preserves the `GOVERNED`/`ORTHOGONAL` distinction | they are opposites, not duplicates; §6.3 |

### 13.5 What the direction explicitly leaves unresolved

| Unresolved | Why |
|---|---|
| Which of V-4 / V-5 is canonical for the subordination axis | requires a competent authority; `UCOS-CAA-001` refuses to decide conflicts between located instruments |
| The `ORTHOGONAL` role/relation contradiction | same, and no article supports the relation's *"answers to nothing"* clause |
| `ConvergenceRelation`'s enum finiteness | requires a decision on whether standings become DATA |
| Whether `00-BOOK/DATA/relationships.json` should be a declared projection | a governed declaration |
| The 8 direction-by-multiplication type pairs in force | binding them is lawful; rewriting them is forbidden |
| Who may perform any of the above | measured absent across four determinations |

---

## 14. Forbidden Actions

| # | Forbidden | Basis |
|---|---|---|
| **F-01** | Merging any two relation terms | mission constraint; and `GOVERNED`/`ORTHOGONAL` are opposites — merging would destroy a distinction |
| **F-02** | Creating a new relation term | **0 needed** — all 16 live types map to existing V-1 members |
| **F-03** | Creating a seventh relation vocabulary | `ART-03` voids a second definition; `extension_rule.what_this_forbids` names a second relationship graph |
| **F-04** | Creating a unified registry above the six | it would be the seventh vocabulary — §12.2 O-5 |
| **F-05** | Copying `RELATION_TYPE_VOCABULARY` or `RELATIONSHIP_CLASS_VOCABULARY` into a second home | `model_term_sources.note` — *"These lists are NOT copied here"*; `ART-18` |
| **F-06** | Adding an inverse-named term for any kind | `$kind_binding_comment` — *"pretending otherwise would invent a term to avoid saying so"* |
| **F-07** | Renaming or rewriting any live edge type | it would modify relationship data |
| **F-08** | Deleting `Evolves-From-Inverse` edges | same |
| **F-09** | Declaring a second relationship model | `CAA-INV-05` |
| **F-10** | Declaring a second supreme authority or object model | `CAA-INV-01`, `CAA-INV-07` |
| **F-11** | Reading `verify_binding()`'s 0 findings as evidence of convergence | it is correct over its scope and blind outside it — §1.4 |
| **F-12** | Treating `subordination_relations` as enforced | read by **zero** Python files |
| **F-13** | Treating `ORTHOGONAL` as a verified standing | 0 occurrences in the verifying gate; internally contradictory |
| **F-14** | Resolving the `ORTHOGONAL` contradiction here | `UCOS-CAA-001` non-goal; no competent instrument |
| **F-15** | Adding a relation to `ConvergenceRelation` by code edit | `ART-17` — extension is by registration, *"never an engine change"* |
| **F-16** | Expressing a direction as a term rather than a flag | `direction` exists for exactly this |
| **F-17** | Registering a projection whose kinds are unmapped | *"a kind absent from this map… fails `CAA-INV-05`"* |
| **F-18** | Binding a kind to a class, relation or article the model does not hold | `_vocabulary_findings()` raises on each |
| **F-19** | Deprecating a rival vocabulary home while leaving the file present | `SUPERSEDED` requires **absence** |
| **F-20** | Executing any §12 option | no competent actor exists |
| **F-21** | Modifying vocabularies, code, registries, identity or relationship data under this determination | mission constraint; §16.5 |
| **F-22** | Treating this determination as a decision, a merge, a registration or an authority | authority **NONE (DERIVED TRUTH)** |
| **F-23** | Presenting any part of this as convergence achieved, completion, closure or certification | §15 |

**Twenty-three prohibitions, each grounded in a cited article, a measured code behaviour or a measured count.**

---

## 15. Readiness Verdict

### 15.1 The question

> What canonical relationship vocabulary is required for authority, governance, ownership and evolution — and is it converged?

### 15.2 The answer

# CONVERGENCE MECHANISM EXISTS AND IS UNAPPLIED · SIX VOCABULARIES · FOUR CONVENTIONS · NOT CONVERGED

### 15.3 The required vocabulary, stated

| Concern | Canonical relation | Canonical class | Both exist |
|---|---|---|---|
| **Authority** | `governs` · `derived-from` | `authority` · `constitutional` | **YES** |
| **Governance** | `governs` | `governance` | **YES** |
| **Ownership** | `owns` (+ `direction: inverse` for *owned by*) | `ownership` | **YES** |
| **Evolution** | `supersedes` · `derived-from` · `generated-from` · `extends` | `evolution` · `historical` · `future` | **YES** |
| **Subordination standing** | `DELEGATES` / `SUPERSEDED` / `PROJECTION` + a fourth | — | **contested — two divergent fourths** |

**Four of five concerns are fully served by the canonical model with zero new terms. The fifth — subordination standing — is the only contested axis, and it is a different axis from the other four.**

### 15.4 Readiness by dimension

| # | Dimension | Ready | Measurement |
|---|---|---|---|
| 1 | A canonical relation model exists | **YES** | `ART-07`, `CAA-INV-05` |
| 2 | Exactly one owner declares it | **YES** | `CAA-INV-05` |
| 3 | The relation vocabulary is open | **YES** | 17 terms, register-then-use |
| 4 | The class vocabulary is open | **YES** | 12 terms, includes `future` |
| 5 | A crosswalk mechanism exists | **YES** | `relationship_kind_bindings`, 5 fields |
| 6 | The crosswalk is DATA, not code | **YES** | *"never an engine change"* |
| 7 | The crosswalk is two-way checked | **YES** | `verify_binding` ↔ stdlib engine |
| 8 | Direction is expressible without a new term | **YES** | `direction` field; `owned_by` exemplar |
| 9 | All five mandatory infinities hold | **YES** | §10.1 |
| 10 | Authority/governance/ownership/evolution terms all exist | **YES** | §15.3 |
| 11 | All 16 live types map to existing terms | **YES** | §2.7 — 0 new terms needed |
| 12 | No parallel authority model exists | **YES** | `CAA-INV-01/05/07` |
| 13 | **All emitting surfaces are crosswalked** | **NO** | 1 of 5 · 0 of 16 live types mapped |
| 14 | **The subordination axis has one canonical home** | **NO** | two, with divergent fourth members |
| 15 | **`subordination_relations` is read by code** | **NO** | zero files |
| 16 | **All relation vocabularies are drift-guarded** | **NO** | 9 guarded; 2 unguarded |
| 17 | **No name carries two meanings in one instrument** | **NO** | `ORTHOGONAL` |
| 18 | **Direction is never expressed as a term** | **NO** | 8 pairs; `Evolves-From-Inverse` |
| 19 | **No hardcoded finite relation set** | **NO** | `ConvergenceRelation` enum |
| 20 | **An actor competent to converge exists** | **NO** | measured absent, four determinations |

**Twelve of twenty ready. All twelve concern the canonical model and its mechanism. All eight unready concern surfaces that do not bind to it, plus the absent actor.**

### 15.5 The finding in one paragraph

> **The repository determined the canonical relationship vocabulary long ago and built the correct convergence mechanism to go with it: a DATA crosswalk in which every emitted kind names a model class, a model relation, a direction, an article and a meaning; in which term lists are referenced rather than copied; in which a backwards reading is a `direction` flag rather than a new term; and in which a kind absent from the map is a declared failure. That mechanism covers six kinds. Five other relation vocabularies exist. One of them — the live 13,361-edge population — emits sixteen types, none of which appears in the map, eight of which exist only because a direction was written as a term, and one of which is literally named `Evolves-From-Inverse`, the exact error the map's own rationale was written to prevent. The alignment verifier reports zero findings, correctly, because none of this is in its scope.**

### 15.6 Why no partial convergence is claimed

| Tempting formulation | Refused because |
|---|---|
| "Converged — one model, `CAA-INV-05` holds" | the model is singular; the **vocabularies** are six, and the mission's principle is about semantic sources, not models |
| "Mostly converged — only 5 edges are wrong" | `Evolves-From-Inverse` is 5 edges and 8 type pairs are 9,682; and the principle is violated by one instance, not by a threshold |
| "`verify_binding()` passes, so it is aligned" | **F-11** — correct over scope, blind outside it |
| "Merge V-4 and V-5 and it is done" | merging is forbidden here, would destroy the `GOVERNED`/`ORTHOGONAL` distinction, and leaves V-6 and the intra-home collision |
| "Just add the missing terms to the model" | **0 terms are missing** — adding any would be the duplication |

### 15.7 Final verdict

| Question | Verdict |
|---|---|
| Is the canonical vocabulary determined? | **YES — V-1 + V-2 under `ART-07`** |
| Are new relations required? | **NO — 0** |
| Is a new vocabulary or registry required? | **NO** |
| Is a convergence mechanism required? | **NO — it exists** |
| Is it applied to all emitting surfaces? | **NO — 1 of 5** |
| Is a parallel authority model present? | **NO** |
| Are duplicate relation vocabularies present? | **YES — 7 register entries** |
| Is semantic drift present? | **YES — 3 spellings of one meaning; 1 contradiction; 1 intra-home collision** |
| Are hardcoded finite assumptions present? | **YES — 3** |
| Was any vocabulary modified, term merged or relation created? | **NO** |
| Convergence | **NOT ACHIEVED** |
| Completion / Closure / Certification | **NOT CLAIMED** |

# VERDICT: NOT CONVERGED

> **Nothing needs inventing. The canonical relation vocabulary is singular, open, guarded and sufficient for authority, governance, ownership and evolution alike — seventeen relations and twelve classes, with every term the four concerns require already present. The convergence mechanism is singular, DATA-driven, two-way checked and exemplary; `owned_by` = `owns` + `direction: inverse` is the whole answer in one line. What is absent is the application of that mechanism to four of the five surfaces that emit relation kinds, and the actor competent to apply it. Convergence here is not a design problem. It is six vocabularies, one crosswalk, and nobody empowered to connect them.**

---

## 16. Verification Record

### 16.1 Baseline captured before this artifact was written

| Field | Value |
|---|---|
| HEAD | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch | `integration/recovery-001` |
| Commits | **515** |
| Porcelain total | **382** |
| Tracked modified | **38** |
| Untracked | **344** |
| Target artifact at capture | **absent** |

**Protected surface digests at capture (SHA-256, first 16):**

| Surface | Digest |
|---|---|
| `00-BOOK/DATA/constitutional-authority-alignment.json` | `aef7b81c1ebab1b5` |
| `engine/uckp/alignment.py` | `1db5e31ad4aead82` |
| `engine/uckp/vocabulary.py` | `cd5fc3ec426f579a` |
| `engine/uckp/graph.py` | `34232f79ec80940b` |
| `platform/universal_foundation/convergence.py` | `1cd29547e54fe8ad` |
| `00-BOOK/DATA/relationships.json` | `31c19f2df2be6cbd` |
| `00-BOOK/DATA/id-ledger.json` | `ea630db9c8c93216` |
| `00-BOOK/DATA/artifacts.json` | `c1f5dc3a1bc58cf9` |
| `00-BOOK/DATA/mutation-governance-boundary.json` | `a7c817151899fb95` |
| `platform/repository_intelligence/mutation_classification.py` | `54ecc7e2c47c6425` |
| `platform/repository_intelligence/mutation_class_extension.py` | `9a742a76294abc6b` |
| `platform/universal_ownership/catalog/ucos-ownership-declarations.json` | `96aa2be26454f7d6` |
| `engine/uckp/law.py` | `1597b041969bc64d` |
| `00-MASTER/UCXI-000001/ucxi-declaration.json` | `2bb7fe3f4efa11c3` |

**Predecessors:** 1,582 · 1,436 · 1,444 · 1,260 lines — all unchanged.

### 16.2 Read-only measurements taken for this determination

| ID | Measurement | Surface | Write? |
|---|---|---|---|
| **R-M1** | `relationship_graph_resolution` declares `model_owner` (`UCKP-ART-07`, `engine/uckp/graph.py`), **3** projections, `model_term_sources` (4 fields), `relationship_kind_bindings` (**6** kinds), `second_model_test`, and a 10-line `$kind_binding_comment` | `constitutional-authority-alignment.json` | **NO** |
| **R-M2** | All 6 bindings measured with `uckp_class`, `uckp_relation`, `direction`, `article`, `meaning`: `owned_by`(ownership/owns/inverse/ART-06) · `produced_by`(traceability/produces/inverse/ART-19) · `produces`(…/forward/…) · `depends_on`(constitutional/depends-on/forward/ART-07) · `validated_by`(validation/validates/inverse/ART-16) · `evidenced_by`(constitutional/references/forward/ART-12) | same | **NO** |
| **R-M3** | `$kind_binding_comment` verbatim: *"`direction` records whether the projection emits the model's edge or its inverse, because a kind read backwards is still that kind and pretending otherwise would invent a term to avoid saying so"* and *"A kind absent from this map is an unmodelled relationship and fails CAA-INV-05… a seventh kind is one appended entry (UCKP-ART-17) and never an engine change"* | same | **NO** |
| **R-M4** | `model_term_sources.note`: *"These lists are **NOT copied here**…"* | same | **NO** |
| **R-M5** | `subordination_relations` — **4** keys `DELEGATES` `SUPERSEDED` `PROJECTION` `ORTHOGONAL`, prose definitions; `$relation_comment` states *"No fourth relation is created"* | same | **NO** |
| **R-M6** | **`subordination_relations` is read by zero Python files** — grep over all `*.py` returns no match | repository-wide grep | **NO** |
| **R-M7** | **`verify_binding(CAA document)` returns 0 findings** | `engine/uckp/alignment.py` | **NO** |
| **R-M8** | `_vocabulary_findings()` checks **only** `relationship_kind_bindings`, against `RELATIONSHIP_CLASS_VOCABULARY`, `RELATION_TYPE_VOCABULARY` and `ROOT_LAW.article_ids()`; its docstring explains the stdlib-only constraint | same | **NO** |
| **R-M9** | Code-side `AUTHORITY_ROLES` holds **8** `AuthorityRole` objects; measured: `SUPREME` `may_hold_authority=True` `EXACTLY_ONE`, and 7 × `False`; `_role_findings()` checks JSON roles against it | same | **NO** |
| **R-M10** | `ConvergenceRelation` — **4** members `DELEGATES` `SUPERSEDED` `PROJECTION` **`GOVERNED`**; a `str` Enum with `coerce()` hard-refusing unknowns; `GOVERNED` = *"Holds law over a strictly narrower subject. Must restate none of the canonical law."* | `convergence.py` | **NO** |
| **R-M11** | **`ORTHOGONAL` occurs 0 times in `convergence.py`; `GOVERNED` occurs 0 times in the CAA document** | grep both ways | **NO** |
| **R-M12** | `uckp.relation-type` **17** terms · `uckp.relationship-class` **12** terms including `future` | `vocabulary.py` via `build_vocabulary_registry()` | **NO** |
| **R-M13** | **`relationships.json` — 13,361 edges, 16 distinct types**, with counts: `Depends-On` 4,777 · `Required-By` 4,700 · `Parent` 1,462 · `Child` 1,462 · `Consumes` 316 · `Consumed-By` 316 · `Authorized-By` 100 · `Authorizes` 100 · `Implements` 48 · `Implemented-By` 48 · `References` 6 · `Referenced-By` 6 · `Traces-To` 5 · `Traced-From` 5 · `Evolves-From` 5 · **`Evolves-From-Inverse` 5** | `relationships.json` | **NO** |
| **R-M14** | **8,292 of 13,361 edges carry `inverse_of: null`** | same | **NO** |
| **R-M15** | **`00-BOOK/DATA/relationships.json` is not among the 3 declared projections**; **0 of its 16 types appear in the 6-kind binding map** | both | **NO** |
| **R-M16** | `ORTHOGONAL` appears on two axes in one instrument: `authority_roles` (`may_hold_authority: False`, `FEW`) and `subordination_relations` (*"holds independent… authority… neither derives from nor answers to"*) | CAA | **NO** |
| **R-M17** | `alignment.py` **797** lines · `graph.py` **334** lines · `convergence.py` **991** lines · CAA **919** lines | `wc -l` | **NO** |
| **R-M18** | Git state: HEAD `bae59755…`, branch `integration/recovery-001`, **515** commits, porcelain **382** | git | **NO** |

**Inherited from the predecessor chain and cited without re-measurement:** 8 authority roles with one `may_hold_authority: True` · 11 bound instruments, 0 competent · 20 articles / 17 invariants / 13 stop conditions · 33 facets · `governance` and `rule` as registered terms · lifecycle 10 stages / 20 transitions · `RuntimeBinding` without an authority field · `ProjectionBinding` / `PersistenceBinding` raising · `register()` raising `DuplicateAuthorityError` both ways · `verify_vocabulary_alignment()` guarding **9** projections · `OWN-REQ-001`…`007` · ownership catalogue `{}` · UCKO population 6,338 with 58% path-shaped owners and 0 stewards · assimilation invertible with 76 terms registered and 0 lines of `law.py` changed · `FG-15` per-relation tests · `UCOS-PROGRAM-CUSTODIAN` at 1,461/1,461 · 0 of 19 mutation subjects registered.

**Every measurement was a read. `build_vocabulary_registry()` and `verify_binding()` were called read-only and construct/inspect in memory only. No vocabulary was registered or extended, no term merged, no relation created, no edge added or retyped, no gate executed against a declared surface.**

### 16.3 Findings contributed beyond the predecessor chain

| # | Finding | Status |
|---|---|---|
| **G-1** | **`relationship_kind_bindings` is a working, enforced, DATA crosswalk** — 6 kinds × 5 fields, checked by `_vocabulary_findings()`; the convergence mechanism already exists | **new · decisive** |
| **G-2** | **`owned_by` = `owns` + `direction: inverse`** — the canonical answer to forward/inverse expressed in one binding, adding no term | **new · decisive** |
| **G-3** | **`subordination_relations` is read by zero Python files** — the vocabulary governing authority declarations is entirely unenforced | **new · decisive** |
| **G-4** | **`verify_binding()` returns 0 findings** while three semantic-drift breaches stand outside its scope | **new · decisive** |
| **G-5** | **Roles are crosswalked code↔data and have not diverged; relations have no code counterpart and have** — the structural cause of the divergence, inside one instrument | **new · decisive** |
| **G-6** | **The live population emits 16 types, 0 of which appear in the crosswalk**, and it is not a declared projection | **new · decisive** |
| **G-7** | **`Evolves-From-Inverse` exists** — the exact anti-pattern `$kind_binding_comment` was written to forbid, verbatim | **new · decisive** |
| **G-8** | **8 of 16 live types are direction-by-multiplication**, costing 8 excess terms; the same 13,361 edges need 8 model relations, all already present | **new** |
| **G-9** | **All 16 live types map onto 8 existing model relations + `direction`** — 0 new terms are needed for convergence | **new** |
| **G-10** | **`GOVERNED` and `ORTHOGONAL` are opposites, not duplicates** — one derives and narrows, the other answers to nothing; merging them would destroy a distinction | **new · corrective** |
| **G-11** | **`ORTHOGONAL` carries two meanings on two axes inside one instrument**, and the relation meaning contradicts the role meaning | **new** |
| **G-12** | **`ART-01` supports no reading of the `ORTHOGONAL` relation's *"answers to nothing"* clause** | **new** |
| **G-13** | **`ConvergenceRelation` is a Python enum with `coerce()` refusing unknowns** — the one hardcoded finite relation set, in tension with `ART-17` | **new** |
| **G-14** | **`model_term_sources.note` explicitly refuses to copy the term lists** — `ART-18` observed as implemented practice | **new** |
| **G-15** | **200 `Authorizes`/`Authorized-By` edges express authority using a non-model term**, while `governs` + class `authority` stand ready | **new** |
| **G-16** | **0 of 13,361 edges are ownership edges**; ownership is absent from the relation population entirely | **new** |
| **G-17** | Six guards exist; **every breach sits in a gap between guard scopes**, and no guard failed | **new** |

### 16.4 Artifact identity

| Field | Value |
|---|---|
| Path | `UCOS-OMEGA-INFINITY-S-1-AUTHORITY-RELATION-VOCABULARY-CONVERGENCE-DETERMINATION.md` |
| Status | Untracked — new artifact |
| Required sections | **16** — `## 1.` … `## 16.`, contiguous, in order |
| Write method | 4 sequential operations — §1–4, §5–8, §9–12, §13–16 |
| Verdict | **CONVERGENCE MECHANISM EXISTS AND IS UNAPPLIED · SIX VOCABULARIES · FOUR CONVENTIONS · NOT CONVERGED** |
| Vocabularies measured | **6** · case conventions **4** · term instances **59** |
| Crosswalked vocabularies | **1 of 5 non-model** |
| Duplication register entries | **7** |
| Live edge types | **16** · mapped to the crosswalk **0** · mappable to existing model terms **16** |
| New relations required | **0** |
| Options assessed | **5** — refused 2 · insufficient 2 · no-new-mechanism 1 · executed **0** |
| Permanent invariants | **12** (`P-01`…`P-12`) — 5 hold, 7 partial or breached |
| Forbidden actions | **23** (`F-01`…`F-23`) |
| Readiness dimensions | **20** — 12 ready (model and mechanism) · 8 unready (unbound surfaces and the actor) |
| Vocabularies modified · terms merged · relations created · edges changed | **0 · 0 · 0 · 0** |
| Convergence / Completion / Closure / Certification | **NOT ACHIEVED · NOT CLAIMED · NOT CLAIMED · NOT CLAIMED** |
| Authority | **NONE (DERIVED TRUTH)** |
| Implementation performed | **NONE** |

### 16.5 Mutation boundary — surfaces confirmed unchanged

| Surface | State |
|---|---|
| Python source | **UNCHANGED** — no `.py` written; `alignment.py`, `vocabulary.py`, `graph.py`, `convergence.py`, `law.py`, both mutation modules match capture |
| JSON | **UNCHANGED** — no `.json` written; all protected digests match |
| Vocabularies | **UNCHANGED** — `uckp.relation-type` still **17** · `uckp.relationship-class` still **12** · nothing registered, nothing extended, nothing merged |
| Crosswalk | **UNCHANGED** — `relationship_kind_bindings` still **6** kinds · `projections` still **3** |
| Subordination relations | **UNCHANGED** — still **4** keys; `ORTHOGONAL` not removed, not renamed |
| `ConvergenceRelation` | **UNCHANGED** — still **4** members; `GOVERNED` not moved, not duplicated |
| Registry | **UNCHANGED** — `artifacts.json` matches; **0 objects admitted** |
| Identity | **UNCHANGED** — `id-ledger.json` matches; no mint, no serial consumed |
| **Relationship data** | **UNCHANGED** — `relationships.json` digest matches; **13,361 edges · 16 types · `Evolves-From-Inverse` still 5 edges** · no edge added, removed, retyped or renamed |
| Ownership | **UNCHANGED** — `assignments` still `{}` |
| Authority alignment | **READ ONLY** — 11 instruments · 8 roles · 4 relations |
| Gates | **NOT EXECUTED** — `FG-15` and `FG-16` not run against any declared surface |
| Tests | **UNCHANGED** — none written or executed |
| Mutation register · classifier · rival module | **READ ONLY** — 9 classes · `RULE_PREDICATES` 8 · rival still present |
| Law · articles · invariants · stop conditions · facets | **UNCHANGED** — 20 · 17 · 13 · 33 |
| Predecessors | **UNCHANGED** — 1,582 · 1,436 · 1,444 · 1,260 lines |
| Commits · tags · pushes · stash · branch | **NONE** |

### 16.6 Verification checklist

Executed after this artifact was written. Reproducible against baseline `bae59755d7e2d3566c93b89c722b68847145269a` on branch `integration/recovery-001`.

| Check | Requirement |
|---|---|
| Artifact exists | yes |
| Section count | **16** |
| Section order | `## 1.` … `## 16.`, ascending, contiguous, no duplicates |
| Line count | recorded in the accompanying verification output |
| HEAD unchanged | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch unchanged | `integration/recovery-001` |
| Commits unchanged | **515** |
| Status delta | exactly one new untracked entry — this artifact; porcelain 382 → 383 |
| Code unchanged | no `.py` delta; all code digests match capture |
| Registry unchanged | no `.json` delta; all protected digests match capture |
| Identity unchanged | `id-ledger.json` digest matches capture |
| Relationship data unchanged | `relationships.json` digest matches capture; 13,361 edges, 16 types |
| Vocabularies unchanged | 17 relation terms · 12 classes · 6 crosswalk kinds · 4 subordination relations · 4 convergence relations |
| No commits | HEAD and commit count unchanged |
| Reversible | nothing written outside this artifact |

---

**END UCOS Ω∞ — S-1 AUTHORITY RELATION VOCABULARY CONVERGENCE DETERMINATION**

**Verdict:** **CONVERGENCE MECHANISM EXISTS AND IS UNAPPLIED · SIX VOCABULARIES · FOUR CONVENTIONS · NOT CONVERGED**
**The canonical vocabulary:** `uckp.relation-type` **17** terms + `uckp.relationship-class` **12** terms · owned by `UCKP-ART-07` at `engine/uckp/graph.py` · exactly one owner by `CAA-INV-05`
**The convergence mechanism:** `relationship_kind_bindings` — **6** kinds × **5** fields (`uckp_class`, `uckp_relation`, `direction`, `article`, `meaning`) · **DATA**, not code · two-way checked by `verify_binding` and the stdlib engine
**The canonical answer in one line:** **`owned_by` = `owns` + `direction: inverse`** — one term, two readings, no second source
**Six vocabularies:** model relation (17) · model class (12) · crosswalk (6) · subordination (4) · convergence (4) · **live edge types (16)** — **four case conventions**
**Crosswalk coverage:** **1 of 5** non-model vocabularies · **0 of 16** live edge types · `relationships.json` is **not a declared projection**
**Duplication register:** **7 entries** — 3 near-verbatim shared members · 1 meaning in 3 spellings · 1 contradiction · 1 intra-home name collision · 8 direction-by-multiplication pairs
**The named anti-pattern, in force:** **`Evolves-From-Inverse`** — 5 edges — against `$kind_binding_comment`'s *"pretending otherwise would invent a term to avoid saying so"*
**`subordination_relations` is read by zero Python files** · **`verify_binding()` returns 0 findings** · every breach sits in a gap between six guard scopes, and **no guard failed**
**Structural cause:** within one instrument, **roles are crosswalked code↔data and have not diverged; relations have no code counterpart and have**
**`GOVERNED` and `ORTHOGONAL` are opposites, not duplicates** — one derives and narrows; the other answers to nothing, which no article supports
**New relations required: 0** — all 16 live types map onto 8 existing model relations plus a direction flag
**Infinite entities · scopes · directions · contexts · future relationship types** — **5 of 5 hold**
**No parallel authority model** — `CAA-INV-01`, `CAA-INV-05`, `CAA-INV-07` all hold
**Options assessed:** 5 · refused 2 · insufficient alone 2 · requiring no new mechanism 1 · **executed 0**
**Zero fixes · Zero patches · Zero shortcuts · Zero temporary solutions · Zero duplication · Zero overlap** — all honoured
**100% systematic · 100% authentic · 100% auditable · 100% secured** — every term, count, binding and edge type read from tracked state at recorded digests
**Changed here:** 0 vocabularies · 0 terms merged · 0 relations created · 0 edges retyped · 0 bindings added · 0 commits
**Authority:** NONE (DERIVED TRUTH) — merges nothing, registers no term, creates no relation, decides no option, ratifies nothing

*This determination modified no vocabulary, no term, no relation, no crosswalk, no Python file, no JSON file, no registry, no identity ledger, no relationship data, no test and no authority binding. It merged no term, renamed nothing, created no relation and selected no resolution option for execution. The seven duplication-register entries it measured stood before this determination was written and stand unchanged after it — including `Evolves-From-Inverse`, which remains five edges of a type named for its own inversion in a population no crosswalk covers.*
