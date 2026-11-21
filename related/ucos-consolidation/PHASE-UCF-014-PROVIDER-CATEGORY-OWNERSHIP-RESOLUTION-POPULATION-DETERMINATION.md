# PHASE-UCF-014 — PROVIDER CATEGORY OWNERSHIP RESOLUTION POPULATION DETERMINATION

## 1. Document Identity

| Field | Value |
|---|---|
| Phase | PHASE-UCF-014-PROVIDER-CATEGORY-OWNERSHIP-RESOLUTION-POPULATION-DETERMINATION |
| Mission | Determine whether `category_ownership_resolution` entries can be safely populated, and the exact population model required |
| Mode | **DETERMINATION ONLY.** No ledger write, no resolution-file change, no registry change, no invariant, no constitution change, no certification rule, no authority-model change |
| Date | 2026-08-14 |
| Base | Branch `integration/recovery-001`, HEAD `1f869865`, working tree as recorded in § 4 |
| Predecessor | `PHASE-UCF-013` — reader and consumer implemented; ledger deliberately left unwritten |
| Successor this enables | `PHASE-UCF-015` — the write of `P1` (21 entries), if and only if this determination reads READY |
| Verdict | **READY FOR POPULATION** (§ 15) |

### What this document is allowed to do, and did

It read the repository, ran the engine, and simulated the proposed ledger **in memory** through the production read path. It wrote exactly one file: itself. `00-BOOK/DATA/constitutional-authority-alignment.json` was **read** and **not written**. No file under `engine/`, `00-MASTER/`, `intelligence/` or `00-BOOK/` was modified.

---

## 2. Purpose

`PHASE-UCF-013` built the join between **Measured Reality** (which provider populates which category) and **Recognised Resolution** (what a constitutional resolution says about that population). It shipped live and consuming, against a ledger that does not exist. The repository therefore reports what it reported before: 21 populated categories, 21 `UNKNOWN`, 0 recognitions, 0 conflicts, 0 violations.

`PHASE-UCF-013 § 3` stated precisely why it stopped there: writing the 21 entries requires answering two content questions `PHASE-UCF-012` explicitly declined to answer —

> **Q3.** *What are the 21 `accountable_authority` values?*
> **Q4.** *Is `uga_projection`'s 5,789-object, seven-category footprint one recognition or seven?* — recorded as *"a content question P1 must answer and no measurement can settle."*

This document answers both, **by measurement in both cases**, determines the complete population model, and states the exact package. It does not write it.

---

## 3. Scope

### In scope

- The 21 currently populated `uckp.governed-category` values and their measured provider attribution.
- The 14 governed categories with no population.
- The ownership semantics model (mission § 2, options A–E).
- The resolution data model — the minimum canonical entry, and what must **not** be an entry field.
- Population rules for existing categories, new categories, plurality, `UNKNOWN`, and conflict.
- The UGA projection question, measured rather than assumed.
- Evidence requirements, future-evolution compatibility, certification readiness, gap reassessment.

### Explicitly out of scope

- Writing `category_ownership_resolution` (that is `PHASE-UCF-015` / `P1`).
- `P6` (a conflict-resolution rule) and `P7` (`CAA-INV-09`) — blocking-stage work, unchanged and still deferred.
- The two stale measurements found inside `existence_resolution` (§ 10.4) — a **separate** section, recorded here as a controlled evolution action, deliberately not repaired by this document.
- Any promotion of category integrity from Observational to Advisory or Blocking.

---

## 4. Current Repository Truth

All figures below were produced by running the engine at the state described, not quoted from a prior phase.

### 4.1 Baseline validations, run fresh

| Check | Result |
|---|---|
| `verify_binding()` | **PASS** — 0 findings against `00-BOOK/DATA/constitutional-authority-alignment.json` |
| `discover()` | `modules_scanned: 27`, `providers_found: 4`, `objects_admitted: 5982`, `failures: []` |
| `validate_universe()` | **certified** — invariants 17, satisfied 17, violated 0, unmeasured 0, blocking failures 0 |
| `ukb.py enforce --pre` | **ENFORCEMENT PASSED** |
| `ukb.py validate` | **VALIDATION PASSED** — 1233 artifacts, append-only page ledger intact |

`./verify.sh` was **not** run, per the mission.

### 4.2 Category integrity state, as the engine reports it now

| Measure | Value |
|---|---|
| `governed_categories` | 35 |
| `categories_populated` | 21 |
| `unpopulated_categories` | 14 |
| `categories_multi_provider` | 0 |
| `categories_unattributed` | 0 |
| `category_recognitions` | 0 |
| `categories_recognised` (MATCH) | 0 |
| `categories_ownership_conflict` (CONFLICT) | 0 |
| `categories_ownership_unknown` (UNKNOWN) | 21 |
| `categories_without_declared_owner` | 21 |
| `coverage` | 0.6 |
| gap-reasoner violations | 0 |
| full `report()` | clean — 13 reasoners, 342 findings, **0 violations** |

### 4.3 The ledger's own state

`category_ownership_resolution` is **absent** from the binding. The binding holds 41 top-level keys and six `*_resolution` sections: `identity_authority`, `relationship_graph`, `certification_authority`, `identity_namespace`, `existence`, `lifecycle`. Direct key check, this run.

Absence is a **lawful** state, not a defect: `engine/uckp/intelligence.py::_recognitions` returns no complaint for an absent section, by deliberate design (`PHASE-UCF-013` D-B), and every category correctly reports `UNKNOWN`.

---

## 5. Evidence Reviewed

| # | Source | What it settled |
|---|---|---|
| E1 | `engine/uckp/intelligence.py:196–508` | The consumed field contract, fixed by `PHASE-UCF-013` D-H, and every state/finding rule the ledger will be judged by |
| E2 | `engine/uckp/resolution.py` | The read path: suffix discovery, `PRESENT`/`ABSENT`/`UNREADABLE`, extra keys ignored |
| E3 | `engine/uckp/registry.py:123,167` | `require_lawful()` is called on **every** admission — the live enforcement of the category value space |
| E4 | `engine/uckp/ucko.py:392` | `vocabularies.require_term(GOVERNED_CATEGORY, self.taxonomy.category)` — the exact refusal point |
| E5 | `engine/uckp/vocabulary.py` → `GOVERNED_CATEGORY_VOCABULARY` | 35 registered terms; the closed value space |
| E6 | `engine/uckp/law.py:505,531,599` | `ROOT_LAW.governed_categories` — the vocabulary's declared owner is `UCKP-LAW-0001` |
| E7 | `engine/uckp/uga_projection.py:79–87` (`_CATEGORY_MAP`) | The seven projected category values originate **here**, not in UGA |
| E8 | `00-MASTER/UCOS-UGA-001/02-UNIVERSAL-OBJECT-REGISTRY.json` | 5,789 entries; 16 keys per entry; **no key contains "categ"** — measured, not assumed |
| E9 | `00-MASTER/UCOS-UGA-001/uga_engine.py:914–943` (`scan_authority_claims`) | The authority-claim scan reads a **top-level** `authority` key only (`doc.get(key)`) |
| E10 | `engine/uckp/alignment.py:688–763` (`verify_binding`) | No closed-key check on top-level sections; an appended section is lawful |
| E11 | `00-BOOK/DATA/constitutional-authority-alignment.json` — `extension_rule` | *"A new vocabulary member, relationship class, adapter or authority role is one appended entry in DATA."* |
| E12 | The six sibling `*_resolution` sections | The canonical section form: `model`, `principles`, an entry list, a falsification test |
| E13 | `00-BOOK/SCHEMAS/` | No JSON Schema governs `constitutional-authority-alignment.json`; `ukb.py validate` does not constrain it |
| E14 | **Six in-memory dry runs** of candidate ledgers through the production read path (§ 9.6) | Every population rule below is *measured*, not argued |

### 5.1 Measured category population — the full table

| Category | Populator (measured) | Objects | Unattributed |
|---|---|---:|---:|
| artifact | `engine.uckp.capabilities` | 10 | 0 |
| authority | `engine.uckp.alignment` | 17 | 0 |
| capability | `engine.uckp.capabilities` | 10 | 0 |
| concept | `engine.uckp.uga_projection` | 2,394 | 0 |
| constraint | `engine.uckp.constitution` | 17 | 0 |
| engine | `engine.uckp.uga_projection` | 1,187 | 0 |
| governance | `engine.uckp.capabilities` | 20 | 0 |
| identity | `engine.uckp.alignment` | 1 | 0 |
| knowledge | `engine.uckp.uga_projection` | 1,233 | 0 |
| law | `engine.uckp.constitution` | 1 | 0 |
| metadata | `engine.uckp.constitution` | 33 | 0 |
| observation | `engine.uckp.capabilities` | 13 | 0 |
| policy | `engine.uckp.uga_projection` | 29 | 0 |
| principle | `engine.uckp.constitution` | 20 | 0 |
| runtime | `engine.uckp.capabilities` | 10 | 0 |
| state | `engine.uckp.uga_projection` | 109 | 0 |
| taxonomy | `engine.uckp.constitution` | 13 | 0 |
| transition | `engine.uckp.capabilities` | 15 | 0 |
| validation | `engine.uckp.constitution` | 13 | 0 |
| verification | `engine.uckp.uga_projection` | 801 | 0 |
| workflow | `engine.uckp.uga_projection` | 36 | 0 |
| **Total** | **4 providers** | **5,982** | **0** |

---

## 6. Category Population Analysis

### 6.1 Provider distribution

| Provider | Categories | Objects | Share |
|---|---:|---:|---:|
| `engine.uckp.uga_projection` | 7 | 5,789 | 96.77% |
| `engine.uckp.constitution` | 6 | 97 | 1.62% |
| `engine.uckp.capabilities` | 6 | 78 | 1.30% |
| `engine.uckp.alignment` | 2 | 18 | 0.30% |
| **Total** | **21** | **5,982** | **100%** |

The 21 category footprints are **disjoint**: every category has exactly one provider, and no provider shares a category with another. The provider counts sum to 21 with no overlap — arithmetic verified (7+6+6+2 = 21) and directly measured.

### 6.2 Structural classes present today

| Class | Count | Categories |
|---|---:|---|
| **Single-provider categories** | **21** | all of the above |
| **Multi-provider categories** | **0** | — |
| **Unattributed categories** (any object naming no provider) | **0** | — |
| **Partially attributed categories** | **0** | — |

`categories_multi_provider = 0` and `categories_unattributed = 0` are the two conditions that would make recognition contentious. Neither is present. This is the cleanest state in which a recognitive ledger can be written, and it will not stay this clean by default — which is the argument for writing it now rather than later (§ 15.2).

### 6.3 The 14 unpopulated governed categories

`axiom`, `certification`, `decision`, `dependency`, `event`, `evidence`, `measurement`, `ontology`, `proof`, `registry`, `relationship`, `responsibility`, `simulation`, `timeline`.

Each already produces one `OBSERVATION` finding from `gap_reasoning()`: *"a governed category with no canonical object yet."* That finding is about **population**, not ownership, and is unaffected by anything determined here.

### 6.4 Projected categories from UGA

Seven, all from `_CATEGORY_MAP`: `concept`, `engine`, `knowledge`, `policy`, `state`, `verification`, `workflow`. Analysed in full in § 10.

### 6.5 Classification for recognition

| Class | Count | Members | Basis |
|---|---:|---|---|
| **Safe for recognition** | **21** | every populated category | Single, measured, named populator; zero unattributed objects; category value traceable to a citable code location; measured-clean in dry run (§ 9.6 A) |
| **Requires evidence before recognition** | **0** | — | No populated category lacks an attributable populator |
| **Cannot be recognised yet** | **14** | the unpopulated governed categories | Measured: recognising one produces `CONFLICT`, not `MATCH` (§ 9.6 B). Recognition without population is the grant of a future right — exactly the constitutive act `PHASE-UCF-012 § 6.3` and D6 forbid |

**No category falls into "requires evidence."** That is the substantive readiness finding: the evidentiary prerequisite `PHASE-UCF-009` and `PHASE-UCF-010` named as missing is, for all 21, present and measurable.

---

## 7. Ownership Semantics Determination

### 7.1 The question is partly pre-answered, and that constrains honestly

`PHASE-UCF-013` D-H fixed the entry's consumed field names in exported constants (`RECOGNITION_CATEGORY`, `RECOGNISED_POPULATORS`, `ACCOUNTABLE_AUTHORITY`), because a reader that guessed among several shapes would make two shapes lawful. Every entry therefore already carries **both** a populator *set* and an *accountable authority*. The semantics question is not "which of A–E," but "what relationship does that already-fixed pair denote, and is that pair the right denotation."

### 7.2 The five candidate models, evaluated against measurement

| Option | Model | Verdict | Why |
|---|---|---|---|
| **A** | Category → single provider | **Rejected** | True of all 21 today, and true only by accident of the present population. A cardinality-1 model makes the first lawful plurality a schema change; `PHASE-UCF-012` D14 already fixed plurality's *shape*, which a single-valued field cannot carry. It also encodes the exact assumption `PHASE-UCF-005`'s defect exploited — that one provider per category is the natural order — into the file meant to detect its violation |
| **B** | Category → provider set | **Necessary, insufficient** | This is the measured plane and is exactly `recognised_populators`. Alone it recognises *who populates* and names nobody accountable for the value space they populate into, so the recognition would have no falsifiable authority anchor and no defence against Provider→Owner substitution |
| **C** | Category → producer relationship | **Rejected** | A "producer relationship" is a restatement of `discovery.provider`, which `category_populations()` already measures directly. Writing it into the ledger creates a second, authored copy of a fact measurement already holds — the drift shape that produced `existence_resolution`'s two stale figures (§ 10.4). A recognition must *reference* measurement, never duplicate it |
| **D** | Category → accountable authority | **Necessary, insufficient** | This is the recognised plane and is exactly `accountable_authority`. Alone it declares an authority over a category with no statement of what is actually happening in it — a claim with no measurement to falsify it, which is the definition of a constitutive grant rather than a recognition |
| **E** | **Other — a two-plane join** | **SELECTED** | See below |

### 7.3 Determination D14-1 — the selected model

> **`category_ownership_resolution` recognises, per category, a `(bounded populator set, governed value-space authority)` pair.**
>
> `recognised_populators` is the **measured** plane: the set of providers that, at measurement time, do in fact populate the category. It is a *set* — cardinality 1 today for all 21, without the model asserting cardinality 1.
>
> `accountable_authority` is the **recognised** plane: the instrument already accountable for the value space within which the category exists, and whose enforcement admits or refuses every population of it. It is **not** an owner of the category, **not** an owner of the objects, and **not** a right conferred on anyone.
>
> Neither plane derives the other. The ledger asserts neither. `engine/uckp/intelligence.py::category_integrity()` reports whether they agree.

This is `B ⋈ D`, and neither alone. The named model type for the section is `SINGLE_GOVERNED_VALUE_SPACE_MULTIPLE_BOUNDED_POPULATORS`, formed after the sibling sections' own model declarations (`MULTIPLE_INDEPENDENT_AUTHORITIES`, `MULTIPLE_INDEPENDENT_BOUNDED_NAMESPACES`, `ORTHOGONAL_AXES`).

### 7.4 Determination D14-2 — the `accountable_authority` value (settles `PHASE-UCF-012` Q3)

> **`accountable_authority` is `UCKP-LAW-0001` for all 21 entries.**

`PHASE-UCF-012` Q3 offered two candidate answers — `ucos-constitutional-authority` for all 21, or per-provider entities from `subordinate_instruments` — and declined to choose. Both are rejected, and the choice is made on measured grounds rather than preference:

**Why not a per-provider entity.** That is the Provider→Owner substitution `PHASE-UCF-012` D5 exists to forbid, and `engine/uckp/intelligence.py:493–501` emits a finding for exactly it. Measured: a package naming `engine.uckp.uga_projection` as accountable produces **21 provider-as-owner findings** (§ 9.6 C). Rejected by the engine, not by argument.

**Why not a new or invented entity name.** Naming an instrument that does not exist would be the creation of authority, which the constitutional principle of this phase forbids outright.

**Why `UCKP-LAW-0001`, on evidence.** The accountability being recognised is real, already held, and already enforced, and the chain was measured end to end this run:

1. `engine/uckp/law.py:599` — `ROOT_LAW.governed_categories = GOVERNED_CATEGORIES`. The 35-term value space is a value of the root law.
2. `engine/uckp/vocabulary.py` — registered as vocabulary `uckp.governed-category`, 35 terms.
3. `engine/uckp/ucko.py:392` — `require_lawful()` calls `vocabularies.require_term(GOVERNED_CATEGORY, ...)`.
4. `engine/uckp/registry.py:123,167` — `require_lawful()` runs on **every** admission.
5. Empirically confirmed: minting with `category="not-a-real-category"` and admitting it raises `LawViolation [UCKP-LAW-001] term is not registered in this vocabulary (vocabulary_id='uckp.governed-category', term_id='not-a-real-category')`.

So for every one of the 5,982 objects, the instrument that admitted or could have refused the object's category value is the root law's vocabulary, live, on every run. Recognising that confers nothing; it records a refusal power already exercised 5,982 times.

**The field's exact meaning, stated so it cannot drift.** `accountable_authority` answers *"which instrument's standing governs the value space this category belongs to, and refuses a value outside it?"* It does **not** answer *"who decided that this provider should populate this category?"* — and § 7.5 records that nothing in the repository answers that second question today.

**On uniformity.** All 21 values are identical. That is a measured fact about the present repository — there is exactly one category value space and exactly one instrument owning it — not an evasion. A second differing value would today be a `CAA-INV-01`/`CAA-INV-07` violation. The discriminating variation lives in `recognised_populators`, and the field becomes discriminating the moment a delegated category authority is ever declared, with no schema change (§ 12).

### 7.5 What is deliberately **not** recognised, and must not be inferred

No instrument in this repository claims accountability for *which provider may populate which category*. Measured: the four resolution sections that name authorities (`existence`, `certification_authority`, `identity_namespace`, `relationship_graph`) declare bounded questions about existence, certification, identity and relationships — none about category assignment. `UCKP-COMPLETENESS-REGISTRY`'s bounded question is *"Does this object answer all 33 constitutional completeness facets?"* — facet **presence**, not category **choice**.

> **Determination D14-2a.** The population model must **not** name any instrument as accountable for the provider→category assignment decision, because no such accountability exists to recognise. Recording one would create it. This is carried as a **Future Opportunity**, not a gap (§ 14.3).

### 7.6 The model against the four required properties

| Property | How the model preserves it |
|---|---|
| **No authority creation** | Both planes are pre-existing: the populator set is measured from objects already admitted; the authority is a standing already enforced 5,982 times per run. Measured: the exact package produces 0 provider-as-owner findings and 0 non-`OBSERVATION` findings (§ 9.6 A) |
| **Future extensibility** | `recognised_populators` is a set, so plurality needs no schema change; `accountable_authority` is a free string, so delegation needs none; extra keys are ignored by the reader (measured, § 9.6 F), so new descriptive fields are additive |
| **Infinite provider support** | The model has no provider enumeration anywhere. A provider is discovered (`Article 8`), measured, and then recognised; the ledger never lists providers except inside the category they populate |
| **No false ownership assumptions** | The entry says *populated by* and *accountable value space*. It never says *owns*. `Ownership.owner` (Facet 7, 245 distinct values in UGA alone) is untouched — `PHASE-UCF-012` D4's severance is preserved by naming the field `accountable_authority`, never `owner` |

---

## 8. Resolution Data Model Determination

### 8.1 The minimum canonical entry

| Field | Required? | Type | Determined role |
|---|---|---|---|
| `category` | **Required** — reader contract | non-empty `str` | Category identity. Unique across `recognitions`; a duplicate drops **both** copies (measured, § 9.6 D) |
| `recognised_populators` | **Required** — reader contract | non-empty `list[str]` | The recognised relationship: which providers populate it |
| `accountable_authority` | **Required** — reader contract | non-empty `str` | The governed value-space authority (D14-2) |
| `basis` | **Required** — determined here | `str` | Evidence basis: the citable code location where this category value is declared |

An entry missing any of the first three is **dropped and reported**, leaving its category `UNKNOWN` (`engine/uckp/intelligence.py::_recognition`). `basis` is not read by the engine; it is required by this determination for audit, and its absence is a documentation defect, not a read failure.

### 8.2 Section-level required fields

| Field | Determined role |
|---|---|
| `model` | `{type, declares}` — the form all six sibling sections carry |
| `principles` | The recognitive constraints, so a future editor reads the rule beside the data |
| `value_space` | Vocabulary id, term count, owner, home, article, and the **enforcement pointer** (`ucko.py:392` via `registry.py:123,167`) — this is what makes D14-2 falsifiable rather than asserted |
| `measurement` | The **measurement reference**: `taxonomy.category × discovery.provider`, the reader (`engine/uckp/resolution.py`), the consumer (`engine/uckp/intelligence.py::category_integrity`). A pointer to how to recompute — never a copied result (D14-4) |
| `provenance` | The determinations this content derives from (`PHASE-UCF-007` … `PHASE-UCF-014`) |
| `recognitions` | The 21 entries |
| `unrecognised_categories` | The 14 unpopulated names and the reason they carry no entry — so the file states its own totality rather than being silently partial |
| `second_populator_test` | The falsification test, mirroring the `second_authority_test` five sibling sections carry (`PHASE-UCF-012` D1) |

### 8.3 Determination D14-4 — evidence **pointers**, never copied measurements

> **No entry, and no part of the section, may carry a copied measurement value** — not an object count, not a provider count, not a percentage, not a digest of the population.

This is not a stylistic preference. It is derived from a defect measured **in the same file this section would join** (§ 10.4): `existence_resolution` copied two measurements at write time, and both are now wrong. A ledger of 21 entries carrying 21 object counts would acquire that defect 21 times over, and would acquire it silently, because nothing recomputes them.

Counts belong to `category_populations()`, which recomputes them on every run. The ledger references the measurement; it never mirrors it.

### 8.4 Fields evaluated and **excluded**, with reasons

The mission asked whether `resolution state`, `lifecycle` and `provenance` are required entry fields. Determined: **no**, for three distinct reasons.

| Candidate field | Verdict | Reason |
|---|---|---|
| `resolution_state` (`MATCH`/`CONFLICT`/`UNKNOWN`) | **Excluded from entries** | The state is **computed** by `_category_integrity()` from the two planes. An authored state would be a second answer to a question measurement already answers, and the two could disagree — with no rule to arbitrate. `relationship_graph_resolution` states this discipline in its own words ("two readers, one truth"); this is that discipline applied |
| `lifecycle` (per entry) | **Excluded from entries** | A recognition has exactly two conditions: present or absent. There is no "retired recognition" — a category whose population ends must have its entry **removed**, because leaving it produces `CONFLICT` (measured, § 9.6 B). A lifecycle field would let a dead recognition sit in the file marked `retired` while the engine reported `CONFLICT` about it |
| `provenance` (per entry) | **Moved to section level** | All 21 entries arrive from one determination at one time. Twenty-one identical provenance blocks is duplication, and duplication is what drifts |
| `conflict` / `disposition` | **Excluded entirely** | § 9.5 |
| `measured_objects`, `measured_at`, population digests | **Excluded entirely** | D14-4 |

### 8.5 Determination D14-5 — additional fields are permitted and must stay non-semantic

Measured (§ 9.6 F): the reader ignores keys it does not name, and a 21-entry package carrying three extra keys produced an identical 21-`MATCH` result with zero complaints. So the schema is open for **descriptive** additions. It must not be used for **semantic** ones: any field that a future reader could treat as a second source of truth for state, ownership or population re-opens exactly what D14-4 and § 8.4 close.

---

## 9. Population Rules

Every rule below was measured through the production read path (`ResolutionReader.from_document` → `build_intelligence` → `category_integrity()` / `gap_reasoning()`), never assumed. The measurements are in § 9.6.

### 9.1 Existing categories — when may a category receive a recognition?

> **R1.** A category may receive a recognition when, and only when, **all four** hold:
> 1. It is a registered term of `uckp.governed-category`.
> 2. `category_populations()` measures **at least one** object in it.
> 3. **Every** object in it names a provider (`unattributed == 0` for that category).
> 4. Every measured provider is listed in `recognised_populators`.
>
> All 21 currently populated categories satisfy R1. **0 do not.**

Rule 3 is not decorative. `MATCH` requires the measured side to be non-empty *and* wholly recognised (`PHASE-UCF-013` D-C), but it does **not** inspect `unattributed`. A category with attributed and unattributed objects would report `MATCH` while part of its population was attributable to nobody — the recognition would be true of the part that was measured and silent about the part that was not. The separate `unattributed` finding would still fire, so nothing is hidden; R1.3 keeps the *recognition* from covering ground it never checked. Today the condition is vacuous (`categories_unattributed = 0`) and it must be stated anyway, because a rule that has never been tested by reality is exactly the rule that will be needed first.

### 9.2 New categories — how do future categories enter?

> **R2 — measurement first, recognition second, never the reverse.**
> 1. A category value is registered in `uckp.governed-category` (`Article 17`, register-then-use).
> 2. A provider mints objects into it; admission enforces the vocabulary.
> 3. `category_populations()` measures it; `category_integrity()` reports it `UNKNOWN`; `gap_reasoning()` emits *"an undeclared default, not a decision."*
> 4. **Only then** may a recognition be added.
>
> **R2a.** A recognition must never be written in anticipation of a population. Measured: recognising the unpopulated category `axiom` yields `CONFLICT`, `categories_ownership_conflict = 1` (§ 9.6 B). The engine refuses to read an anticipatory recognition as a pass — which is `PHASE-UCF-012` D6 enforced by mechanism rather than by discipline.

The interval in step 3 is a feature. A new category is visibly `UNKNOWN` and visibly reported until someone recognises it deliberately.

### 9.3 Multiple providers — how does plurality work?

> **R3.** Plurality is representable from day one and is **never** self-reconciling.
>
> `recognised_populators` is a list. A category populated by two providers is recognised by listing both — and `MATCH` is then structurally correct, because both populators genuinely *are* recognised. But `categories_multi_provider` continues to count it, and `_category_findings()` appends, verbatim:
>
> > *"a recognised plurality is reconciled only where the resolution declares a bounded question for each populator, so the plurality stands reported rather than closed."*
>
> **R3a.** A plurality entry that does not declare a distinct bounded question per populator is **listed, not reconciled**. Listing both populators must never be the move that makes a contamination finding disappear (`PHASE-UCF-012` D9; `PHASE-UCF-013` D-E).
>
> **R3b.** The *rule* that adjudicates a legitimate plurality from a contamination remains `P6` — deferred, unchanged, and correctly deferred: there is no actual conflict in the repository to adjudicate (`categories_multi_provider = 0`), and a rule written against a hypothetical conflict would be a rule written against a guess.

### 9.4 Unknown — when must `UNKNOWN` remain?

> **R4.** `UNKNOWN` is a **permanent** state of the model, never a transitional one (`PHASE-UCF-012` D7; `PHASE-UCF-013` D-C). It must remain, and must be reachable, in all of:
> - a populated category with no entry (the default for anything populated after the write);
> - a category whose entry could not be read as a recognition (dropped, reported — measured, § 9.6 D);
> - a category recognised more than once (both copies dropped — measured, § 9.6 D);
> - every category, whenever the section is `UNREADABLE`.
>
> **R4a.** Writing 21 entries must **not** be accompanied by any change that narrows or removes `UNKNOWN`. After the write, `categories_ownership_unknown` reaching 0 means *"every category measured today is recognised"* — it must never come to mean *"the check no longer looks."* Removing the state after a complete backfill would reintroduce `PHASE-UCF-005`'s blind spot one layer up.

### 9.5 Conflict — how are conflicts represented?

> **R5.** Conflicts are **computed, never recorded.** `category_ownership_resolution` has no conflict field, no disposition field, and no exception list, and must never acquire one.

A conflict is precisely a disagreement between the ledger and measurement. A field in the ledger that describes the conflict would be the ledger describing its own disagreement with reality — and the obvious next step, an "accepted conflict" marker, is a disposal mechanism that makes a real divergence stop being reported. That is the exact form `PHASE-UCF-012` D9 forbids, and the analogue of `id-ledger`'s own recorded rule that *"exclusion is not a disposal mechanism."*

Two conflict shapes exist and both are already computed and reported:

| Shape | Cause | Reported as |
|---|---|---|
| Measured-not-recognised | A provider populates a category the entry does not list | `CONFLICT` + a finding naming the unrecognised provider |
| Recognised-not-measured | An entry lists a populator (or a category) nothing populates | `CONFLICT` + *"no object attributes it to any provider"* |

The comparison is total over the **union** of both sides (`PHASE-UCF-013` D-D), so neither shape can hide by being on the side nobody iterated.

### 9.6 The six dry runs — measured, not argued

Each ran the candidate document through `ResolutionReader.from_document` into the live registry of 5,982 objects. **Nothing was written to disk.**

| # | Candidate | MATCH | CONFLICT | UNKNOWN | Complaints | Provider-as-owner | Rule proved |
|---|---|---:|---:|---:|---:|---:|---|
| **A** | The exact 21-entry package (§ 15.3) | **21** | 0 | 0 | **0** | **0** | R1 — the package is clean |
| **B** | A + a recognition of unpopulated `axiom` | 21 | **1** | 0 | 0 | 0 | R2a — anticipatory recognition fails |
| **C** | A, `accountable_authority` = `engine.uckp.uga_projection` | 21 | 0 | 0 | 0 | **21** | D14-2 — provider-as-owner is caught |
| **D** | A + a duplicate `artifact` entry | 20 | 0 | **1** | **1** | 0 | R4 — both copies dropped, category `UNKNOWN` |
| **E** | Section present, `recognitions: []` | 0 | 0 | **21** | **1** | 0 | R6 — an empty section is worse than none |
| **F** | A + three extra keys per entry | **21** | 0 | 0 | 0 | 0 | D14-5 — extra fields are ignored |

Run A additionally reported: `categories_without_declared_owner = 0`, `category_recognitions = 21`, `gap` violations `0`, and full `report()` **clean** — 13 reasoners, 342 findings, **0 violations**.

> **R6 — derived from run E.** The section must **never** be written with an empty `recognitions` list. An absent section is a lawful, silent, recorded-as-deferred state; a *declared and empty* section is a claim that could not be resolved and produces a standing complaint on every reasoning pass. There is no staging step in which the section exists empty. It arrives with all 21 entries or it does not arrive.

---

## 10. UGA Projection Analysis

`PHASE-UCF-012` Q4 asked whether `uga_projection`'s 5,789-object, seven-category footprint is *one recognition or seven*, and recorded it as *"a content question P1 must answer and no measurement can settle."* **Two independent measurements settle it.**

### 10.1 Measurement 1 — UGA has no concept of a UCKP category

`00-MASTER/UCOS-UGA-001/02-UNIVERSAL-OBJECT-REGISTRY.json` holds 5,789 entries with 16 keys each: `certification_status`, `content_hash`, `content_hash_withheld`, `dependencies`, `evidence_boundary`, `evidence_class`, `first_seen`, `identity_authority`, `lifecycle`, `object_class`, `owner`, `path`, `producer`, `produces`, `universal_id`, `validation_contract`.

**No key contains "categ". No UGA value is ever one of the seven category names.** UGA emits seven `object_class` values (`EXCLUDED_DOCUMENT` 2394, `DOCUMENT_ARTIFACT` 1233, `EXECUTABLE_OBJECT` 1187, `TEST_OBJECT` 801, `DATA_OBJECT` 109, `TOOLING_OBJECT` 36, `CONFIGURATION_OBJECT` 29); the mapping onto `concept`, `knowledge`, `engine`, `verification`, `state`, `workflow`, `policy` exists **only** in `engine/uckp/uga_projection.py:79–87`.

> **Determination D14-3a.** The seven projected categories do **not** represent UGA relationships and do **not** inherit any existing relationship. They are **seven independent UCKP-side classification decisions**, recorded in one table, in one provider module, under UCKP's own vocabulary. They require **separate recognition** exactly as the fourteen native categories do — and for the same reason, not a weaker one.

This also disposes of the tempting reading that a projected category's accountable authority ought to be `UGA-EXISTENCE-REGISTRY`. It cannot be: UGA does not know these seven values exist. Naming it would attribute to UGA a decision UGA never made — the same substitution error as naming a provider, one level further out.

### 10.2 Measurement 2 — the recognition unit is fixed by the reader

`_recognitions()` keys recognitions **by category** and enforces uniqueness per category; `_category_integrity()` iterates the union of categories. There is no representation in which one entry covers seven categories: an entry names exactly one `category`. So "one recognition or seven" is not an open content choice at all.

> **Determination D14-3b.** `uga_projection` receives **seven entries**, one per category. `PHASE-UCF-012` Q4 is **closed**, by the reader's own key discipline plus § 10.1, not by preference.

### 10.3 Consequence — the entries are structurally uniform across all four providers

There is no special case for the projected categories. Each of the 21 entries names one category, its measured populator, the value-space authority, and its `basis` pointer. The only difference is what `basis` points at: a `category="..."` literal for the fourteen native categories, and a `_CATEGORY_MAP` row for the seven projected ones. That uniformity is itself the finding: **a projection's categories are not a lesser kind of category.**

### 10.4 A measured staleness in `existence_resolution` — reported, not repaired

Two figures in the sibling section that governs the UGA projection are now wrong:

| Field | States | Measured now | Status |
|---|---|---|---|
| `declared_projections[0].status` | `"DECLARED, NOT YET IMPLEMENTED"` | `engine/uckp/uga_projection.py` implements it and admits 5,789 objects (`PHASE-UCF-005`) | **Stale** |
| `authorities[0].population` (`UCKP-COMPLETENESS-REGISTRY`) | `"193 objects (measured), scoped to providers under engine.uckp by default discover() root"` | `discover()` under that exact root admits **5,982** | **Stale** |

Both were true when written and were falsified by the very implementation this arc produced. Nothing gates on either: `verify_binding()` does not read `existence_resolution`; no test compares them to a measurement; `uga_engine.py` does not read them.

This is **not** repaired here — that would be a resolution-file modification, which this phase forbids, and it is a different section from the one under determination. It is recorded as controlled evolution action **CEA-3** (§ 14.2), and it is the direct empirical source of D14-4 (§ 8.3): the only two copied measurements in the binding are the only two facts in the binding that are wrong.

---

## 11. Evidence Requirements

> **R7.** No entry may be written whose four evidence conditions are not independently confirmable.

| Evidence class | Required? | For the 21 | How confirmed |
|---|---|---|---|
| **Provider observation** | **Required** | Present, all 21 | `discovery.provider` on every object; `providers_found` = 4, `failures: []` |
| **Object population** | **Required** | Present, all 21 | `category_populations()`; ≥ 1 object each, 5,982 total; `unattributed = 0` everywhere |
| **Discovery metadata** | **Required** | Present, all 21 | `discover()` this run: 27 modules scanned, 4 providers, 0 failures |
| **Provenance** | **Required, section level** | Available | `PHASE-UCF-007` → `PHASE-UCF-014`, all present in-tree |
| **Code-location basis** | **Required, per entry** | Present, all 21 | 14 `category="..."` literals + 7 `_CATEGORY_MAP` rows, cited in § 15.3 |
| **Value-space enforcement** | **Required, section level** | Present | `ucko.py:392` via `registry.py:123,167`; refusal reproduced empirically (§ 7.4) |
| **Historical evidence** | **Not required** | n/a | The recognition is of present standing, not of history. `id-ledger.json` holds `first_seen`; duplicating it would be a copied measurement (D14-4) |
| **External authority evidence** | **Not required, and none exists** | n/a | Measured (§ 7.5): no instrument claims accountability for provider→category assignment. Asserting one would create it (D14-2a) |

**Zero unsupported assumptions remain in the package.** Every field of every one of the 21 entries resolves to either a live measurement or a cited code location.

---

## 12. Future Evolution Compatibility

No schema redesign is required for any of the following. Each row states the mechanism and what would be edited.

| Future | Mechanism | Ledger change | Schema change |
|---|---|---|---|
| **A new provider** (`Article 8` discovery, `universe.py` never edited) | Appears in `providers_found`; its categories measured | If it populates a new category → 1 new entry. If it co-populates an existing one → that entry's `recognised_populators` grows and R3a applies | **None** |
| **A new category** | Registered in `uckp.governed-category` (`Article 17`, one appended DATA entry) | 1 new entry, **after** population (R2) | **None** |
| **New objects** in an existing category | Measured continuously | **None** — counts live in measurement, never in the ledger (D14-4) | **None** |
| **A new universe / a second `discover()` root** | `build_universe(roots=...)` already accepts it | Categories measured per assembled universe; recognition remains per category | **None** |
| **A new capability** | A provider module | As "a new provider" | **None** |
| **An unknown future domain** | Register terms, mint, measure, recognise | Entries added by the same rule | **None** |
| **A legitimate plurality** | Two providers, one category | Both listed; R3a keeps it reported until `P6` exists | **None** |
| **A delegated category authority**, if ever declared | An instrument declares a bounded question over a category's population policy | That entry's `accountable_authority` changes from `UCKP-LAW-0001` to it; the field stops being uniform | **None** |
| **A retired category** | Its population ends | Its entry is **removed** (R4/§ 8.4 — no `retired` marker; leaving it yields `CONFLICT`) | **None** |
| **A retired provider** | Stops being discovered | Removed from `recognised_populators`; the entry is deleted if it was the only one | **None** |
| **Descriptive fields** the future wants | Reader ignores unnamed keys (measured, § 9.6 F) | Additive | **None** |

The one thing that **would** require change is a semantic field — a state, a disposition, a copied count. § 8.4 and § 8.5 forbid exactly those, so the model's extensibility is protected by the same rule that protects its integrity.

---

## 13. Certification Readiness

### 13.1 The three stages, and where the write lands

| Stage | Meaning | Status |
|---|---|---|
| **Observational** | Measured and reported; no declared side exists | **Current.** `PHASE-UCF-011` + `PHASE-UCF-013` |
| **Advisory** | Declared side exists; divergence reported at `OBSERVATION`; certification unaffected | **What `P1` reaches.** Not yet |
| **Certified ownership integrity** | Divergence refuses certification | **Not reached.** Requires `P6` + `P7` |

Writing the 21 entries moves Observational → **Advisory**. It does **not** and must not move certification.

### 13.2 `PHASE-UCF-010`'s four promotion conditions, re-measured

| # | Condition | Status |
|---|---|---|
| (a) | `category_ownership_resolution` exists and is populated for all 21 populated categories | **Blocked on `P1` only** — content determined here, dry-run clean |
| (b) | A production reader exposes it to engine code | **MET** — `engine/uckp/resolution.py` (`PHASE-UCF-013`) |
| (c) | The check distinguishes PASS from UNKNOWN, so UNKNOWN's population falls from 21 toward 0 | **MET (mechanism)** — `MATCH`/`CONFLICT`/`UNKNOWN` live; measured to fall 21 → 0 on the package (§ 9.6 A) |
| (d) | A regression fixture pins the real 21-category / 4-provider population, so a new provider cannot silently re-create `PHASE-UCF-005`'s defect | **NOT MET** — carried as **CEA-2** |

### 13.3 What is required before Advisory becomes Certified ownership integrity

| # | Requirement | Kind | Status |
|---|---|---|---|
| C1 | `P1` written; `categories_recognised = 21`, `conflict = 0`, `unknown = 0` | Validation | Determined, unwritten |
| C2 | The regression fixture of (d) | Verification | Not built (**CEA-2**) |
| C3 | `P6` — the rule adjudicating a legitimate plurality from a contamination | Validation rule | Deferred; no conflict exists to adjudicate |
| C4 | `P7` — `CAA-INV-09` in the existing `CAA` family, refusing certification on `CONFLICT` | Certification rule | Deferred, **its own phase**. Mints one object: `authority` 17 → 18, total 5,982 → 5,983 |
| C5 | A recorded interval in which the ledger ran Advisory and produced no false `CONFLICT` | Certification evidence | Cannot exist before C1 |

**C3 and C4 are correctly still deferred.** Promoting to blocking with `categories_multi_provider = 0` would enable a rule that has never once been exercised against a real divergence — the "passes because it never looked" failure `engine/uckp/validation.py`'s own documented caution warns against, and which `PHASE-UCF-009` cited when choosing Observational in the first place.

### 13.4 Certification evidence the write itself must produce

`verify_binding()` PASS · `discover()` 4 providers / 5,982 objects / 0 failures · `validate_universe()` certified 17/17 · `categories_recognised = 21` · `categories_ownership_conflict = 0` · `categories_ownership_unknown = 0` · `report()` clean, 0 violations · `ukb.py enforce --pre` PASS · `ukb.py validate` PASS · `./verify.sh` PASS (required for `P1`, since `P1` writes a governed DATA file — the gate that caught `PHASE-UCF-013`'s UCAF disclosure).

---

## 14. Gap Reassessment

### 14.1 Closed by this determination

| # | Item | Closed by |
|---|---|---|
| G1 | `PHASE-UCF-012` Q3 — the 21 `accountable_authority` values | D14-2: `UCKP-LAW-0001`, on the measured vocabulary-ownership + admission-enforcement chain (§ 7.4) |
| G2 | `PHASE-UCF-012` Q4 — one recognition or seven for `uga_projection` | D14-3a/D14-3b: **seven**, settled by two measurements (§ 10.1, § 10.2) |
| G3 | Whether projected categories inherit UGA relationships | D14-3a: they do not; UGA has no category field at all (§ 10.1) |
| G4 | Whether the resolution data model needs state / lifecycle / per-entry provenance | § 8.4: no, on three distinct grounds |
| G5 | Whether an entry may carry measurements | D14-4: no — evidence pointers only, derived from a defect measured in the same file (§ 10.4) |
| G6 | Whether any populated category "requires evidence" before recognition | § 6.5: none. All 21 are safe; 0 require evidence |
| G7 | Whether the section may be staged empty | R6: no — measured (§ 9.6 E) |
| G8 | Whether appending a 7th section is lawful against `verify_binding()`, `authority_claim_scan` and `ukb.py validate` | § 15.4: yes, all three checked directly |
| G9 | The population rules for existing / new / plural / unknown / conflict | R1–R6, each measured (§ 9) |

**Known architectural gaps = 0.** Every item below is a *managed* action or a *named* opportunity, not an unknown.

### 14.2 Controlled Evolution Actions

| # | Action | Owner phase | Blocking? | Notes |
|---|---|---|---|---|
| **CEA-1** | Write `P1` — the 21-entry section, exactly as § 15.3 | `PHASE-UCF-015` | No | Dry-run clean. Requires `./verify.sh` (writes a governed DATA file) |
| **CEA-2** | The regression fixture pinning 21 categories / 4 providers / 5,982 objects | With or after `P1` | No | `PHASE-UCF-010` (d); the only unmet promotion condition that is not deferred |
| **CEA-3** | Correct the two stale measurements in `existence_resolution` (§ 10.4) | Own phase | No | Deliberately not repaired here — different section, and this phase may not modify resolution files |
| **CEA-4** | `P6` — the plurality-vs-contamination rule | Deferred | Blocking-stage | Correctly deferred: `categories_multi_provider = 0` |
| **CEA-5** | `P7` — `CAA-INV-09` | Deferred, own phase | Blocking-stage | Mints 1 object; 5,982 → 5,983 |
| **CEA-6** | `PHASE-UCF-012` Q2 — bring the four previously-unread sections (`existence`, `lifecycle`, `certification_authority`, `identity_namespace`) under a verifier | Open | No | Now cheap: `resolution.py` already reads all four. § 10.4 is direct evidence that unread sections drift |
| **CEA-7** | Regenerate `00-MASTER/UCOS-UCAF-001/ucaf.json` (one entry stale since `PHASE-UCF-013` D-I: reports `minted_token_classes: 5`, register holds 6) | Its own producer | No | Carried forward from `PHASE-UCF-013 § 5.9`; nothing gates on it |

**Unmanaged evolution actions = 0.** Each of the seven has a named owner phase and a stated blocking status.

### 14.3 Future Opportunities

| # | Opportunity | Note |
|---|---|---|
| F1 | Declare accountability for the provider→category **assignment decision** | No instrument claims it today (§ 7.5). It would be the creation of an authority, so it is an opportunity requiring its own constitutional determination — never a side effect of a ledger write (D14-2a) |
| F2 | Populate any of the 14 unpopulated governed categories | Each already emits its own `OBSERVATION`. Population first, recognition second (R2) |
| F3 | Delegated per-category authorities | The field already supports it; `accountable_authority` stops being uniform with no schema change (§ 12) |
| F4 | `PHASE-UCF-008` Q2 — whether `Ownership.stewards` generalises to delegated category producers | Unresolved and **materially less likely** to be the mechanism: `PHASE-UCF-012` D4 severed the value spaces, and D14-2 anchors accountability in the vocabulary rather than in Facet 7 |

---

## 15. Final Determination

# READY FOR POPULATION

### 15.1 The verdict, stated exactly

Every decision `PHASE-UCF-013 § 3` named as blocking the write is now made on measured grounds: the `accountable_authority` values (D14-2), and the one-or-seven question for `uga_projection` (D14-3). The complete population model is determined (§ 7, § 8), every population rule is measured rather than argued (§ 9), and the exact 21-entry package has been run through the production read path against the live 5,982-object registry with the result **21 MATCH, 0 CONFLICT, 0 UNKNOWN, 0 complaints, 0 provider-as-owner findings, 0 violations, `report()` clean.**

**Missing decisions: none.** `P6` and `P7` are deferred by prior determination and are **blocking-stage** work; neither is a prerequisite of the Advisory-stage write, and § 13.3 states why deferring them remains correct.

### 15.2 Why now rather than later

`categories_multi_provider = 0` and `categories_unattributed = 0` — the population is currently unambiguous. Every recognition written now records a relationship nobody disputes. The same 21 entries written after a fifth provider arrives would have to *arbitrate* rather than *recognise*, which is precisely the constitutive act this arc has avoided at every step.

### 15.3 The exact population package

**Target:** `00-BOOK/DATA/constitutional-authority-alignment.json`, one appended top-level section, placed after `lifecycle_resolution` and before `$truth_comment`, preceded by a `$category_ownership_comment` block matching the six sibling sections' convention.

**Section skeleton** (field roles per § 8.2; `declares` / `principles` / `second_populator_test` prose to be authored in `PHASE-UCF-015` from § 7.3, § 9 and § 15.5):

```json
"category_ownership_resolution": {
  "model": {
    "type": "SINGLE_GOVERNED_VALUE_SPACE_MULTIPLE_BOUNDED_POPULATORS",
    "declares": "<§ 7.3, stated recognitively>"
  },
  "principles": [ "<R1–R6, § 9>" ],
  "value_space": {
    "vocabulary": "uckp.governed-category",
    "terms": 35,
    "owner": "UCKP-LAW-0001",
    "home": "engine/uckp/law.py",
    "article": "UCKP-ART-17",
    "enforcement": "engine/uckp/ucko.py:392 (require_lawful) via engine/uckp/registry.py:123,167 — runs on every admission"
  },
  "measurement": {
    "evidence": "taxonomy.category x discovery.provider",
    "reader": "engine/uckp/resolution.py",
    "consumer": "engine/uckp/intelligence.py::UniversalIntelligence.category_integrity",
    "note": "counts are recomputed, never copied here — see PHASE-UCF-014 § 8.3"
  },
  "provenance": { "determinations": ["PHASE-UCF-007", "…", "PHASE-UCF-014"] },
  "recognitions": [ /* the 21 entries below, verbatim */ ],
  "unrecognised_categories": {
    "count": 14,
    "categories": ["axiom","certification","decision","dependency","event","evidence",
                   "measurement","ontology","proof","registry","relationship",
                   "responsibility","simulation","timeline"],
    "reason": "no object populates them; a recognition without a population is a grant of a future right, not a recognition of present standing (PHASE-UCF-014 R2a, measured)"
  },
  "second_populator_test": "<§ 15.5>"
}
```

**The 21 entries, exact and complete.** `accountable_authority` is `UCKP-LAW-0001` in every entry (D14-2); it is elided from the table for width and is **not** optional.

| # | `category` | `recognised_populators` | `basis` |
|---:|---|---|---|
| 1 | `artifact` | `["engine.uckp.capabilities"]` | `engine/uckp/capabilities.py:120 (category="artifact" literal)` |
| 2 | `authority` | `["engine.uckp.alignment"]` | `engine/uckp/alignment.py:394,431,470 (category="authority" literals)` |
| 3 | `capability` | `["engine.uckp.capabilities"]` | `engine/uckp/capabilities.py:141 (category="capability" literal)` |
| 4 | `concept` | `["engine.uckp.uga_projection"]` | `engine/uckp/uga_projection.py:79-87 (_CATEGORY_MAP["EXCLUDED_DOCUMENT"] -> "concept")` |
| 5 | `constraint` | `["engine.uckp.constitution"]` | `engine/uckp/constitution.py:216 (category="constraint" literal)` |
| 6 | `engine` | `["engine.uckp.uga_projection"]` | `engine/uckp/uga_projection.py:79-87 (_CATEGORY_MAP["EXECUTABLE_OBJECT"] -> "engine")` |
| 7 | `governance` | `["engine.uckp.capabilities"]` | `engine/uckp/capabilities.py:249 (category="governance" literal)` |
| 8 | `identity` | `["engine.uckp.alignment"]` | `engine/uckp/alignment.py:501 (category="identity" literal)` |
| 9 | `knowledge` | `["engine.uckp.uga_projection"]` | `engine/uckp/uga_projection.py:79-87 (_CATEGORY_MAP["DOCUMENT_ARTIFACT"] -> "knowledge")` |
| 10 | `law` | `["engine.uckp.constitution"]` | `engine/uckp/constitution.py:149 (category="law" literal)` |
| 11 | `metadata` | `["engine.uckp.constitution"]` | `engine/uckp/constitution.py:267 (category="metadata" literal)` |
| 12 | `observation` | `["engine.uckp.capabilities"]` | `engine/uckp/capabilities.py:286 (category="observation" literal)` |
| 13 | `policy` | `["engine.uckp.uga_projection"]` | `engine/uckp/uga_projection.py:79-87 (_CATEGORY_MAP["CONFIGURATION_OBJECT"] -> "policy")` |
| 14 | `principle` | `["engine.uckp.constitution"]` | `engine/uckp/constitution.py:184 (category="principle" literal)` |
| 15 | `runtime` | `["engine.uckp.capabilities"]` | `engine/uckp/capabilities.py:162 (category="runtime" literal)` |
| 16 | `state` | `["engine.uckp.uga_projection"]` | `engine/uckp/uga_projection.py:79-87 (_CATEGORY_MAP["DATA_OBJECT"] -> "state")` |
| 17 | `taxonomy` | `["engine.uckp.constitution"]` | `engine/uckp/constitution.py:291 (category="taxonomy" literal)` |
| 18 | `transition` | `["engine.uckp.capabilities"]` | `engine/uckp/capabilities.py:192 (category="transition" literal)` |
| 19 | `validation` | `["engine.uckp.constitution"]` | `engine/uckp/constitution.py:249 (category="validation" literal)` |
| 20 | `verification` | `["engine.uckp.uga_projection"]` | `engine/uckp/uga_projection.py:79-87 (_CATEGORY_MAP["TEST_OBJECT"] -> "verification")` |
| 21 | `workflow` | `["engine.uckp.uga_projection"]` | `engine/uckp/uga_projection.py:79-87 (_CATEGORY_MAP["TOOLING_OBJECT"] -> "workflow")` |

Entries are in category-sorted order — the order `category_populations()` itself emits — so the file's order and the measurement's order cannot drift apart.

### 15.4 Safety of the write, checked directly against three gates

| Gate | Effect of appending the section | Basis |
|---|---|---|
| `verify_binding()` | **None.** It validates named sections and enforces no closed top-level key set; it does not read any `*_resolution` section other than `identity_authority` and `relationship_graph` | `engine/uckp/alignment.py:688–763`, read this run |
| `authority_claim_scan` / `CAA-INV-02` | **None.** The scan reads a **top-level** `authority` string only (`doc.get(key)`); `accountable_authority` is nested inside `recognitions[]` and is a different key name in any case. The file's own top-level `authority` string is untouched | `00-MASTER/UCOS-UGA-001/uga_engine.py:914–943` |
| `ukb.py validate` (jsonschema) | **None.** No schema in `00-BOOK/SCHEMAS/` governs this file | Directory listing + grep, this run |
| `extension_rule` | **Permits it** — *"one appended entry in DATA"* | The binding's own text |

`PHASE-UCF-015` must still run `./verify.sh`: `P1` writes a governed DATA file, and `./verify.sh` is the gate that caught `PHASE-UCF-013`'s unanticipated UCAF disclosure. Nothing in this analysis substitutes for it.

### 15.5 The `second_populator_test`, determined

Every sibling section carries a falsification test. The category analogue, to be written verbatim into the section:

> *A second populator would be a provider minting objects into a category this section recognises, whose module name does not appear in that category's `recognised_populators`. It is recognised by measurement, not by declaration: `discovery.provider` over `taxonomy.category`, computed by `engine/uckp/intelligence.py::category_populations()` on every reasoning pass and compared against this section by `category_integrity()`. Finding one is a `CONFLICT`, and a `CONFLICT` is reported and reconciled — never absorbed by adding the provider to this list. Listing a second populator is legitimate only where the resolution declares a distinct bounded question for each, exactly as `existence_resolution` does for its three authorities; absent that, the plurality stands reported. This section recognises which providers do populate each category; it grants no provider a right to populate anything.*

### 15.6 What must not accompany the write

Stated so `PHASE-UCF-015` cannot widen: no new invariant · no `CAA-INV-09` · no promotion of any finding above `OBSERVATION` · no change to `engine/uckp/intelligence.py` or `engine/uckp/resolution.py` (the contract is fixed by `PHASE-UCF-013` D-H and must be imported, not restated) · no object minted, so the count stays **5,982** · no change to `existence_resolution` (CEA-3 is its own phase) · no removal of the `UNKNOWN` state (R4a) · no empty-section staging step (R6).

---

## Validation Executed

Run against the working tree described in § 4, **after** this document was created. No repository content was modified.

| Check | Result |
|---|---|
| `verify_binding()` | **PASS** — 0 findings |
| `discover()` | `providers: 4` · `objects: 5982` · `failures: 0` · `modules_scanned: 27` |
| `validate_universe()` | **certified** — 17 invariants, 17 satisfied, 0 violated, 0 unmeasured, 0 blocking failures |
| `ukb.py enforce --pre` | **ENFORCEMENT PASSED** |
| `ukb.py validate` | **VALIDATION PASSED** — 1233 artifacts, append-only page ledger intact, referential integrity OK |

`./verify.sh` was **not** run, per the mission.

Stopping after PHASE-UCF-014. No ledger entry was written, no resolution file modified, no registry changed, no invariant added, no constitution modified, no certification rule added, and no authority model changed.
