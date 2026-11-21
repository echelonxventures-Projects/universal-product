# UNIVERSAL RELATIONSHIP INTELLIGENCE FOUNDATION DETERMINATION

> **Mission:** UCOS Ω∞ Universal Infinite Scope, Self-Evolving Constitutional Model Alignment — Workstream 2
> **Baseline:** `bb9c27d2` · **Branch:** `integration/recovery-001` · **Date:** 2026-08-18
> **Temporal coordinate:** `logical:ucos-repository-history@1#485` (CMG-000002)
> **Mode:** Determination. No relationship catalog, no relationship registry, no rival relationship model, no new authority.
> **Authority:** NONE (DERIVED TRUTH). This determination locates the existing relationship model and measures its openness. It declares no relationship type.
> **Governing prior determination:** `UCRD-001-CONSTITUTIONAL-RELATIONSHIP-DETERMINATION.md` — where this determination and UCRD-001 disagree, UCRD-001 governs.

---

## 1. Executive determination

**The relationship model is already a Universal Relationship Intelligence Foundation, and the mission's feared failure mode has already been refused twice by name.**

The mission's concern is that CMG-000013 becomes:

```
Relationship List → Closed forever
```

**Measured: CMG-000013 contains no relationship list.** It is a recommendation register — `R-01…R-10` plus standing guidance `G-1…G-4` — with header `STATUS = UNDER REVIEW · DERIVED · NON-NORMATIVE` and `AUTHORITY = NONE (DERIVED TRUTH) — recommendations bind nobody`. There is no freeze language in it at all.

More to the point, CMG-000013 §5 "WHAT NOT TO DO" already **prohibits the very artifact the mission warns against**, in two rows:

> *"Maintain a hand-written traceability matrix for constitutional relationships — A second source of truth that will drift (CMG-000001 XXXVII.2)"*

> *"Edit shared classification or enforcement configuration to accommodate future zones — a hard-coded enumeration in the sense CMG-L-08 prohibits"*

And `UCRD-001` §7 refuses a rival model by name: **DO NOT CREATE `CEP-REL-001`** — *"It would create a model that already exists … A CEP creating it would be a rival to a located owner"* (`UCKP-ART-18`).

**Determination: no relationship catalog, dictionary, matrix or registry is created. The foundation is located, and its openness is converted from a declared property into a measured one (ISD-L-02, ISD-L-06).**

---

## 2. The located foundation — three tiers, one closed on purpose

From `UCRD-001`, quoting `engine/uckp/facets.py`: *"The enumeration is closed on purpose while the vocabularies inside facets are open. Adding a thirty-fourth facet is a constitutional amendment … Adding a new knowledge kind, authority tier, persistence technology or relationship class is **registration**, and registration must never require an amendment."*

| Tier | Subject | Cardinality | Growth | Owner |
|---|---|---|---|---|
| 1 · Facet | the question every object must answer | **33 — CLOSED on purpose** | amendment | `UCKP-ART-06`, `engine/uckp/facets.py` |
| 2 · Relationship class | the register a binding belongs to | **12 — OPEN** | registration | `RELATIONSHIP_CLASS_VOCABULARY`, `engine/uckp/vocabulary.py` |
| 3 · Relation type | how one object is bound to another | **17 — OPEN** | registration | `RELATION_TYPE_VOCABULARY`, `engine/uckp/vocabulary.py` |

Relationships are **Facet 9**, carried as `relationships: tuple[Relationship, ...]` — multi-valued by construction, so an object's relationship count has no ceiling in the type system.

**Closure of Tier 1 is not a finite assumption; it is what keeps Tiers 2 and 3 infinite.** If the question set were open, every new answer would require a new question, and the model would grow by amendment instead of registration. This is the distinction `ISD-L-01` encodes: the prohibited condition is *undisclosed* closure, not closure.

---

## 3. Openness, measured rather than asserted

Five independent mechanisms, each measured at baseline `bb9c27d2`:

| # | Mechanism | Measurement | Result |
|---|---|---|---|
| M-1 | `00-BOOK/SCHEMAS/relationship.schema.json` `properties.type` | keys present: `type`, `description`, `pattern`, `$comment` | **No `enum`.** Pattern only: `^[A-Z][A-Za-z0-9]*(-[A-Z][A-Za-z0-9]*)*$` — any well-formed TitleCase-hyphenated type validates |
| M-2 | `00-BOOK/tools/config.py` `RELATIONSHIP_FREEFORM_LABEL` | `"RELATES"` | A front-matter row `\| RELATES Federates \| … \|` admits a new type **with zero config edit and zero schema edit** |
| M-3 | `engine/uckp/vocabulary.py` append-only registry | `RELATION_TYPE_VOCABULARY.extended_with(Term(...))` → 17 → 18 terms; original still 17; returned object is not the original | **Extension is non-mutating and requires no amendment** |
| M-4 | `00-CMG/CMG-REGISTRY.json` `closed_enumerations` | `["identifier_families", "invariants", "lifecycle_phases", "unknown_concept_dispositions"]` | `relationship_types` (16 entries) is **deliberately absent** — an open, registration-extensible set |
| M-5 | `00-BOOK/tools/config.py` `RELATIONSHIP_TYPES` vs `00-BOOK/DATA/relationships.json` | **22 declared** types; **16 distinct materialized** across 12,899 edges | Six declared types carry no edge. A vocabulary that can hold a registered-and-unused member is registration-driven, not usage-derived — the strongest available evidence that the set is open |

The schema's own `description` states the constitutional position: *"Relationship type. **OPEN, append-only vocabulary** (UMB-006 §3; UMB-IMP-002; AUTH-INF-001 CR-INF-007): any well-formed TitleCase-hyphenated type is valid, so **unlimited future relationship types are supported without schema redesign**. A new relationship type is a new value, never a rewrite."*

---

## 4. The seven required capabilities — located

`LAW-RELATIONSHIP-∞-001` requires `EvolutionCapacity(relationship) = ∞` **and** `ExpansionCapacity(RelationshipModel) = ∞`. Both hold. The mission's seven required capabilities map to located owners:

| Required capability | Located mechanism | Status |
|---|---|---|
| Discovery of unknown relationships | `parse_relationship_refs` / `read_relationship_rows` (`ukb.py`); `M-2` freeform label admits an undeclared type at discovery time | **PRESENT** |
| Creation of new relationship types | `Vocabulary.extended_with`; `VocabularyRegistry.extend`; `RELATIONSHIP_TYPES` append; `CMG-REGISTRY.json` `relationship_types` append | **PRESENT — four independent paths** |
| Relationship transformation | `inverse_of` on the edge schema; `inverse` on every declared type; materialized `<Type>-Inverse` | **PRESENT** |
| Relationship composition | `UniversalKnowledgeGraph`; `engine/graph/queries.py` closure / ancestors / topo | **PRESENT** |
| Relationship decomposition | Same graph queries, inverted; `engine/knowledge/ukip/relationships.py` `ACYCLIC_FAMILIES` | **PRESENT** |
| Relationship evolution | `Term.successors` on the vocabulary; supersession via `SUPERSEDES` / `Evolves-To` | **PRESENT** |
| Relationship inheritance | `INHERITS-FROM` / `INHERITED-BY` (`CMG-R-08`); `INHERITS` in `RELATION_TYPE_VOCABULARY` | **PRESENT** |

**No capability is missing. No capability is created here.**

---

## 5. The two real closures — disclosed, not silently carried

Openness at the schema and vocabulary layers is not openness everywhere. Two genuine `Enum` closures sit on relationship paths:

### RCL-01 — `engine/knowledge/model.py` `RelationType`

**17 members, fail-closed:** `RelationType.coerce()` raises `RelationshipError("unknown relationship type")` on any value outside the enum. This is a hard blocker on the CKO/UKIP knowledge-graph path.

**It is not, however, undisclosed.** `engine/uckp/vocabulary.py` declares this enum one of nine **checked projections** of the open vocabulary, aligned by `engine.uckp.assimilation.verify_vocabulary_alignment`, which *"fails closed if any projection and its vocabulary ever diverge."*

**Operational consequence, recorded because it is a trap:** registering a new relation type in `RELATION_TYPE_VOCABULARY` **alone will fail the alignment check**. A registration is a two-sided act — vocabulary term *and* enum member, in the same change — plus, for any type intended to be acyclicity-checked, a family assignment in `ACYCLIC_FAMILIES` (`engine/knowledge/ukip/relationships.py`).

**Determination: the projection is correct architecture, the two-sided admission path is the disclosure.** Fusing the enum away would remove the fail-closed guarantee that a projection cannot silently drift from its vocabulary. Declared in `uisd-declaration.json` with `admission` naming both sides.

### RCL-02 — `data/relationship_meta.py` `RelationshipKind`

**3 members:** `Association`, `Composition`, `Reference` (DXH-04, DATA-008 §5). Alongside it: `RelationshipCardinality` admits `1:1`, `1:N`, `N:M` and deliberately **no unbounded member** (DRA-C3).

The apparent contradiction — `DRA-08 "Additive Growth — new relationship types append additively"` beside a 3-member enum — resolves on measurement: in the DATA layer `kind` is a **3-way classifier**, and the open axis is the free-text `type_tag`. `data/relationship_validation.py` `RelationshipTypedCheck` requires `type_tag` non-empty and `kind` present; it **never** checks `type_tag` against any list.

**Determination: the DATA layer is open on `type_tag` and closed on `kind`/`cardinality`, and that is the disclosure.** `N:M` already expresses unbounded multiplicity on both sides; a fourth cardinality member would name no relationship the three cannot express.

---

## 6. The enforcement gap — ISD-G-04

**12,899 relationship edges are materialized and no gate validates them.**

- `verify.sh` contains zero occurrences of "relationship" — no relationships stage exists.
- `ukb.py cmd_validate` loads `artifact.schema.json` only. It never loads `relationships.json`, and `relationship.schema.json` **is never applied by any code path in the repository**.
- What is unvalidated: schema conformance, referential integrity of `from`/`to`, inverse completeness, type-pattern conformance, and acyclicity of the ten types declared `acyclic` in `CMG-REGISTRY.json`.

**Determination: recorded as gap ISD-G-04 and NOT closed by this cycle.** A relationships gate is enforcement machinery over a 12,899-edge surface owned by UKB. Adding it inside a determination cycle whose declared mode is "no new capability" would be the scope violation this programme exists to prevent — and CMG-000013 `R-09` establishes the precedent that adding a stage to the canonical chain is the enforcement owner's call, not a determination's.

**Note on ordering:** ISD-G-04 is an *unmeasured* surface, not a *closed* one. It does not threaten infinite expansion; it means edge correctness rests on the generator being right. Closing it is a coverage improvement, not an unbounding.

---

## 7. Relationship self-application

WS11 requires: *the relationship model can create new relationship models.*

| Level | Mechanism | Measured |
|---|---|---|
| A relationship between two objects | Edge in `relationships.json`, typed from an open vocabulary | 12,899 edges, 16 types |
| A new relationship **type** | `Vocabulary.extended_with` — registration, not amendment | 17 → 18, original untouched |
| A new relationship **class** (a new register of relationships) | `RELATIONSHIP_CLASS_VOCABULARY` — same mechanism, one tier up | 12 classes, same `extended_with` |
| A new relationship **model** | A new class + its types, admitted by the same registration path with no engine change | **The mechanism is tier-agnostic** |

The vocabulary mechanism does not distinguish "a type" from "a class of types" — both are `Term`s in an append-only `Vocabulary`, and `RELATIONSHIP_CLASS_VOCABULARY` is itself the proof that the relationship model already contains a model *of* relationship models. **Self-application holds by construction**, and ISD-L-06 measures it by performing the extension in memory on every gate run.

---

## 8. Determination summary

| Item | Determination |
|---|---|
| CMG-000013 as a closed relationship catalog | **DOES NOT EXIST** — it is a non-normative recommendation register that itself forbids such a catalog |
| Create a relationship catalog / matrix / registry / `CEP-REL-001` | **REFUSED** — UCRD-001 §7, CMG-000013 §5, `UCKP-ART-18` |
| `ExpansionCapacity(RelationshipModel) = ∞` | **MEASURED** — five independent mechanisms (M-1…M-5) |
| `EvolutionCapacity(relationship) = ∞` | **MEASURED** — successors, inverses, supersession, graph composition |
| Seven required relationship capabilities | **ALL PRESENT**, none created |
| Closed `Enum`s on relationship paths | **2 DISCLOSED** — RCL-01 (checked projection, two-sided admission), RCL-02 (open on `type_tag`) |
| Relationship self-application | **HOLDS by construction**, measured by ISD-L-06 |
| Relationship edge enforcement | **GAP ISD-G-04** — recorded, deferred to the UKB owner, not closed here |
| Finite relationship dictionary | **NONE EXISTS** and none is created |

---

**END UNIVERSAL RELATIONSHIP INTELLIGENCE FOUNDATION DETERMINATION**

**Status:** Evolution Baseline Established v1.0
**Certified Temporal Baseline:** `bb9c27d2` · `logical:ucos-repository-history@1#485` (CMG-000002 coordinate; CEP-005 certification channel)
**Lifecycle Authority:** UCIC-001 (owner) · UCL-000001 (derived truth, not supreme) · CMG-000001 (law)
**Relationship Authority:** UCRD-001 · `UCKP-ART-06` facets · `UCKP-ART-17` registration
**Governed Evolution:** ENABLED — CEP-009 amendment · Article-14 perpetual cycle
