# 11 — Universal Dictionary Catalog

**Anchor** `c6c20fb`

---

## 1 · Determination

> **There is no Universal Dictionary in this repository.**
>
> No canonical dictionary, term registry, controlled vocabulary, or authoritative glossary exists at
> platform scope. This is the **only mandated Wave-1 catalog whose subject is substantively absent**
> — every other catalog (object, capability, repository, identity, registry, dependency) has a
> located canonical owner. Recorded as gap `G-DICT-1` (output 16).

## 2 · What exists instead

### 2.1 Located lexical instruments — 2

| Instrument | Path | Scope | Authority | Assessment |
|---|---|---|---|---|
| Constitutional Glossary | `00-MASTER/UAKOS-CLOSURE-006/CONST-11-CONSTITUTIONAL-GLOSSARY.md` | one programme's constitutional findings vocabulary | AUTHORITY=NONE (operational memory) | **not platform-scope**; buried inside a single closure programme's output set |
| Ontology Register | `01-WORKING/ONTOLOGY-REGISTER.md` | ontology entries | none declared | **lives in `01-WORKING/`** — a working directory, not a canonical zone; no owning programme, no gate |

Neither is referenced by any gate, neither is a registered canonical owner of terminology, and
neither is discoverable from the constitutional stack.

### 2.2 Ontologies — 10 (semantic models, not dictionaries)

| Ontology | Band |
|---|---|
| `RUNTIME-003-UNIVERSAL-RUNTIME-ONTOLOGY.md` | Runtime |
| `PLATFORM-003-UNIVERSAL-PLATFORM-ONTOLOGY.md` | Platform |
| `DATA-003-UNIVERSAL-DATA-ONTOLOGY.md` | Data |
| `SERVICE-003-UNIVERSAL-SERVICE-ONTOLOGY.md` | Service |
| `APPLICATION-003-UNIVERSAL-APPLICATION-ONTOLOGY.md` | Application |
| `INFRASTRUCTURE-003-UNIVERSAL-INFRASTRUCTURE-ONTOLOGY.md` | Infrastructure |
| `SECURITY-003-UNIVERSAL-SECURITY-ONTOLOGY.md` | Security |
| `USIS-ONT-000-SUBSTRATE-ONTOLOGY-HOME-AND-ROOT-CONCEPT-ANCHOR.md` | USIS |
| `USIS-005-THEORY-ONTOLOGY-TAXONOMY-FOUNDATION.md` | USIS |
| `06-IMPLEMENTATION/UCOS-Ω∞-ONTOLOGY-PLATFORM.md` | platform implementation determination |

### 2.3 Taxonomies — 9

`RUNTIME-004` · `PLATFORM-004` · `DATA-004` · `SERVICE-004` · `APPLICATION-004` ·
`INFRASTRUCTURE-004` · `SECURITY-004` · `USIS-TAX-000` · `USIS-005`

### 2.4 Executable semantic surface — 2 modules

| Module | Root | Test coverage |
|---|---|---|
| `engine/context/ontology.py` | `engine.context` (CERTIFIED) | `engine/tests/context/test_taxonomy_ontology.py` |
| `engine/context/taxonomy.py` | `engine.context` (CERTIFIED) | same |

These are the **only executable ontology/taxonomy capability** in the repository, and they are
certified and covered. They implement structure, not vocabulary.

### 2.5 Schema-enforced vocabularies — 19

`00-BOOK/SCHEMAS/`: `artifact` · `build` · `connector` · `control-tower` · `deployment` ·
`environment` · `export-job` · `finding` · `flow` · `journey` · `page` · `production-service` ·
`relationship` · `repository` · `signal` · `status` · `test` · `ui-artifact` · `volume`.

These are the closest thing to a controlled vocabulary the repository has — they constrain field
values structurally. Their enforcement is nonetheless **conditional**: `ukb validate` silently
degrades to structural-only checks when `jsonschema` is unavailable (`UCCEP-F-006`).

### 2.6 De-facto controlled vocabularies (in data, undocumented)

Each of these is an enumerated value set that gates depend on, and **none is declared in a dictionary**:

| Vocabulary | Members | Location |
|---|---|---|
| Lifecycle status | 6 — ACTIVE, COMPLETE, FROZEN, UNDER_REVIEW, FINAL, CERTIFIED | `artifacts.json.status` |
| Edge type | 16 — Depends-On, Required-By, Parent, Child, Consumes, Consumed-By, Authorized-By, Authorizes, Implements, Implemented-By, References, Referenced-By, Traces-To, Traced-From, Evolves-From, Evolves-From-Inverse | `relationships.json.type` |
| Traceability dimension | 13 — requirement, architecture, design, implementation, source_code, unit_test, integration_test, functional_test, security_test, certification, deployment, production, operations | `artifacts.json.traceability` |
| Progress dimension | 15 — architecture, build, certification, deployment, execution, functional_testing, implementation, integration_testing, operational, performance_testing, portfolio, production, release, security, unit_testing | `UCOS-RIE-PROGRESS.json` |
| Concept disposition | 4 — IMPLEMENTED, DEFERRED, SPECIFIED, REJECTED | `closure.json` |
| Decision disposition | 5 (closed set per `CEP-002` Art 28) | `UCDA-000001` |
| Finding disposition | 7 — IMPLEMENTED, REGISTERED, GOVERNED, VALIDATED, CERTIFIED, REJECTED-WITH-EVIDENCE, WORK-PACKAGE | `uccep-bindings.json` |
| Reuse disposition | 4 — REUSE_AS_IS/COMPOSE, REUSE/COMPOSE, REUSE/EXTEND, REALIZE_BY_COMPOSITION | capability catalog |
| Category | **94 in use** (95 allocated) | `artifacts.json.category` |
| Concept family | 26 | `closure.json.families` |

## 3 · Consequence

The absence is not cosmetic. Three measured defects trace directly to it:

1. **Category truncation.** Four category labels are cut at 12 characters (`INFRASTRUCTU`,
   `IMPLEMENTATI`, `ARCHITECTURA`) and several are unexpanded abbreviations (`CON`, `PLT`, `DAT`,
   `SVC`). With 94 categories and no dictionary, there is no authority that says what a category
   label *is*, so truncation is undetectable by any gate.
2. **`native_id` ambiguity.** 7 collision groups / 22 objects (output 09). A term registry binding
   each native identifier to exactly one canonical object would make the collisions a gate failure
   rather than an unnoticed condition.
3. **Duplicate-concept detection is content-hash-based, not term-based.** `DUP-KNOWLEDGE` = 0 is a
   true statement about *content hashes*. It says nothing about two instruments using the same term
   for different things, or different terms for the same thing — which is exactly what a dictionary
   would arbitrate. `phase2.json` carries a `SEMANTIC-EQUIVALENCE-MATRIX`, but its inputs are
   co-occurrence statistics rather than declared definitions.

## 4 · Dictionary catalog verdict

| Criterion | Verdict |
|---|---|
| Canonical universal dictionary exists | **FAIL — absent** |
| Controlled vocabulary declared for enumerated value sets | **FAIL** — 10 de-facto vocabularies, none declared |
| Ontologies present and complete per band | **PASS** — 10 ontologies, all 7 bands covered |
| Taxonomies present and complete per band | **PASS** — 9 taxonomies, all 7 bands covered |
| Executable ontology / taxonomy capability | **PASS** — `engine.context`, certified and covered |
| Schema-enforced vocabularies | **PARTIAL** — 19 schemas exist; enforcement conditional (`UCCEP-F-006`) |
| Glossary at platform scope with an owner and a gate | **FAIL** — one glossary inside a programme, one register in a working directory, neither owned nor gated |

**The corpus has rich *semantics* (ontologies, taxonomies, a 12,851-edge typed graph) and no
*lexicon*. Terminology is the one substrate layer that was never given a canonical home.**
