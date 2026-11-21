# PHASE-UCF-012 — PROVIDER CATEGORY OWNERSHIP RESOLUTION INTEGRATION DETERMINATION

## 1. Document Identity

| Field | Value |
|---|---|
| Determination | PHASE-UCF-012-PROVIDER-CATEGORY-OWNERSHIP-RESOLUTION-INTEGRATION-DETERMINATION |
| Mission | Determine how category ownership governance integrates with the repository's existing constitutional resolution patterns **without creating a duplicate authority system** |
| Mode | Determination only. Zero code, zero test changes, zero registry mutation, zero constitution changes, zero invariants, zero ledger writes. |
| Date | 2026-08-14 |
| HEAD | `1f869865`, working tree as recorded in `PHASE-UCF-011 § Validation Results` |

## 2. Purpose

`PHASE-UCF-008` determined that category ownership should be recorded through the repository's existing `*_resolution` governance-ledger pattern. `PHASE-UCF-010` then found that three of the four sections `PHASE-UCF-008` cited as that pattern's precedent have **no machine reader at all**, and `PHASE-UCF-011` built the observational half of the capability, leaving eight named prerequisites (B1–B8).

Those three documents settled *what* to record and *where*. None of them asked the question this one exists to answer: **when a `category_ownership_resolution` section is added to a file that already holds six resolution sections, eight authority roles, and eight alignment invariants, does it join that system or start a second one beside it?**

That question is not decorative. The binding's own `non_goals` forbid it from "creating an authority", and `extension_rule.what_this_forbids` names "a second registry, engine, lifecycle, identity authority, relationship graph or evolution system standing beside the ones that exist." A category-ownership mechanism that declared its own authority model, its own reader, and its own invariant family would be exactly that — and would be built by an arc whose entire premise is that an undeclared second authority is the defect.

## 3. Scope

In scope: discovery and classification of every existing `*_resolution` structure, alignment of the category-ownership model against them, the Provider/Owner/Authority separation and its required relationships, ledger readiness, backfill requirements, advisory- and blocking-stage requirements, testing strategy, and governance impact.

Out of scope, per explicit instruction: implementing anything, modifying code, tests, registries, or constitutions, writing the ledger section, and running `./verify.sh`.

`PHASE-UCF-005` through `011` are treated as settled inputs. Where direct measurement in this pass **refines** a figure or a conclusion those documents carried, the refinement is stated explicitly (§ 5.1, § 9.2) rather than silently absorbed.

---

## 4. Current Repository Truth

Measured fresh in this pass, not cited from prior turns. Full results in § 14.

| Check | Result |
|---|---|
| `verify_binding(constitutional-authority-alignment.json)` | `()` — **PASS** |
| `build_universe().registry.discover()` | 4 providers, **5,982** objects, **0** failures |
| `validate_universe(build_universe())` | `verdict='certified'`, `certified=True` |
| `00-BOOK/tools/ukb.py enforce --pre` | **PASS** |
| `00-BOOK/tools/ukb.py validate` | **PASS** — 1,233 artifacts |

Newly measured in this pass — the facts the integration question actually turns on:

| Measurement | Value |
|---|---|
| `*_resolution` sections in the alignment binding | **6** |
| `*_resolution` keys anywhere else in the repository's JSON | **2**, both `relationship_model.target_identity_resolution` in `ACEE-000001` / `UCL-000001` declarations — a two-element list of strings, not the ledger pattern (§ 6.2) |
| Resolution sections with a machine reader | **2 of 6** — `identity_authority`, `relationship_graph` |
| Resolution sections that **assign** a right rather than recognise a standing | **0 of 6** (§ 6.3 — the load-bearing finding) |
| `CAA` alignment rules declared in `engine/uckp/alignment.py` | **8** (`CAA-INV-01`…`08`) |
| Of those, measured by the stdlib engine `uga_engine.py` | **7** (`01`…`07`) |
| Of those, measured in Layer Zero by `alignment.py` itself | **1** (`CAA-INV-08`) |
| Production (non-test) code paths that open the alignment binding | **0** |
| Callers of `alignment.require_aligned()` anywhere | **0** |
| Populated categories | **21**, every one of them a lawful `GOVERNED_CATEGORIES` member |
| Governed categories with zero population | **14** — `axiom`, `certification`, `decision`, `dependency`, `event`, `evidence`, `measurement`, `ontology`, `proof`, `registry`, `relationship`, `responsibility`, `simulation`, `timeline` |
| Categories with more than one populating provider | **0** |
| Distinct `ownership.owner` values across the population (Facet 7) | **246** |
| Categories whose objects carry **more than one** distinct `ownership.owner` | **7** — `concept` (94), `engine` (116), `knowledge` (106), `state` (40), `verification` (7), `policy` (2), `workflow` (1 non-constitutional owner) |

The last two rows are new to this determination and are load-bearing for § 8.

---

## 5. Evidence Reviewed

- `00-BOOK/DATA/constitutional-authority-alignment.json` — **full structural read of all six `*_resolution` sections**, key by key, plus `authority_roles`, `invariants`, `extension_rule`, `non_goals`, `object_model`, `subordinate_instruments`.
- `engine/uckp/alignment.py` — **full read**: `AUTHORITY_ROLES` (8), `ALIGNMENT_RULES` (8), `repository_local_urn`, `alignment_objects()`, `_rule_findings`, `_role_findings`, `_vocabulary_findings`, `_derivation_findings`, `verify_binding`, `require_aligned`.
- `00-MASTER/UCOS-UGA-001/uga_engine.py:60-90, 940-1015, 1155-1165, 1340-1500, 1650-1760` — every read it performs against the binding, and every `CAA-INV` it measures; the module docstring's stdlib-only discipline.
- `00-MASTER/UCOS-UGA-001/uga-declaration.json` — `alignment_invariants` (7 entries, `CAA-INV-01…07`), `invariants` (10).
- `platform/tests/test_constitutional_authority_alignment.py:39-60, 90-120, 170-235, 295-315` — the only place `verify_binding()` is invoked outside `engine/tests/`, and the assertion form of `ALIGNMENT_INVARIANTS` (per-id substring over `uga_engine.py gate` stdout — a subset check, not set equality).
- `engine/tests/uckp/test_alignment.py:20-90, 210-230` — confirms the rule/role suites **iterate** rather than pin a count.
- `engine/uckp/intelligence.py:60-105, 500-580` — `VIOLATION`/`OBSERVATION` (the complete severity set — two strings, on a plain `str` field, not an enum), `ReasoningResult.clean`, and `gap_reasoning()` as `PHASE-UCF-011` left it.
- `engine/uckp/law.py:420-470, 500-610` — `GOVERNED_CATEGORIES` (35), `NON_AUTHORITATIVE_CATEGORIES`, `governs()`, `is_non_authoritative()`.
- `engine/uckp/values.py:153-233, 604-628` — `AuthorityBinding` (Facet 5), `Ownership` (Facet 7), `DiscoveryDescriptor` (Facet 21). Re-read, not cited.
- `00-BOOK/DATA/exclusion-register.json` and its three production readers (`platform/repository_intelligence/contamination.py`, `evidence_universe.py`, `00-MASTER/UCOS-RIB-001/rib_engine.py`) — the repository's one **complete** DATA-register-with-per-entry-owner precedent (§ 6.4).
- `00-BOOK/SCHEMAS/finding.schema.json` — the `UCOS-FND` entity with `state: OPEN|IN_PROGRESS|ACCEPTED|RESOLVED|FALSE_POSITIVE`, `approver`, `expires`; the repository's one existing finding-resolution state machine (§ 11.3).
- `00-BOOK/DATA/id-ledger.json` — confirms the binding file itself is a UGA-governed object, `UCOS-TOOLING-000035`, not a corpus artifact.
- `PHASE-CAA-INV-08-ENFORCEMENT-COMPLETENESS-DETERMINATION.md` — located during validation, read in full. An **independent, prior determination** that reached verdict (C) on exactly the mechanism § 12.2 relies on: `CAA-INV-08` is enforced in production, fail-closed, on the live binding, by `verify_binding()` in `verify.sh`'s pytest stage — a deliberate design choice to measure a rule "at the one place structurally equipped to read it", not an enforcement gap. § 9.2 and § 12.2 cite it rather than re-deriving it.
- Live measurement over `build_universe()` for every count in § 4.

### 5.1 One figure carried forward, corrected

`PHASE-UCF-011 § Validation Results` reports "Every invariant family reported zero violations: `UGA-INV-01..10`, `OBS-INV-01..13`, `CAA-INV-01..07`". The `CAA` family holds **eight** rules, not seven; `CAA-INV-08` (`ORTHOGONAL_ROLE_IS_SCOPE_BOUNDED_AND_NON_SUPREME`) is declared in `alignment.py:281-291` and in the binding's `invariants` list, and is measured by `verify_binding()` rather than by `uga_engine.py` — which is why it does not appear in that gate's output. The eighth rule was not missed by `PHASE-UCF-011`'s validation; it was measured in a different stage. **This correction is not cosmetic: `CAA-INV-08` is the precedent the whole of § 12 rests on.**

---

## 6. § 1 — Existing Resolution Pattern Discovery

### 6.1 The population

Six sections, all in `00-BOOK/DATA/constitutional-authority-alignment.json`. Each was read in full; none is summarised from a prior document.

| # | Section | Purpose (the bounded question it closes) | Authority model | Storage model |
|---|---|---|---|---|
| R1 | `identity_authority_resolution` | Is there more than one thing minting repository identities? | `one_authority` + 2 `planes` (SUPREME / PERSISTENCE) | `planes[]`, `derivation{}`, `mint_markers[]`, `second_authority_test` |
| R2 | `relationship_graph_resolution` | Who defines what a relationship is, and what may the projections of it declare? | `model_owner` + 3 `projections` | `model_owner{}`, `projections[]`, `relationship_kind_bindings{}`, `model_term_sources{}`, `second_model_test` |
| R3 | `certification_authority_resolution` | Which certification surface answers which certification question? | `MULTIPLE_INDEPENDENT_AUTHORITIES` | `model{}`, `principles[]`, `surfaces[]` (14), `second_authority_test` |
| R4 | `identity_namespace_resolution` | Do two identifier schemes sharing a digest primitive constitute one namespace or two? | `MULTIPLE_INDEPENDENT_BOUNDED_NAMESPACES` | `model{}`, `principles[]`, `shared_primitive{}`, `namespaces[]` (2), `canonical_pattern_ownership[]` (3), `second_authority_test` |
| R5 | `existence_resolution` | Which registry answers which "what exists" question? | `MULTIPLE_INDEPENDENT_AUTHORITIES` | `model{}`, `authorities[]` (3), `shared_primitive{}`, `declared_projections[]` (1), `second_authority_test` |
| R6 | `lifecycle_resolution` | Is a process lifecycle the same thing as a state lifecycle? | `ORTHOGONAL_AXES` | `model{}`, `axes[]` (2), `already_declared_composition{}`, `open_item{}`, `second_authority_test` |

### 6.2 Readers, validators, and classification

Traced by direct search across every `.py` in the repository, then read at each hit.

| # | Section | Production reader | Validator | Ownership semantics carried | **Classification** |
|---|---|---|---|---|---|
| R1 | `identity_authority_resolution` | `uga_engine.py:976, 984, 1009-1010, 1402` (stdlib engine, measures `CAA-INV-04`) | `alignment.py::_derivation_findings` → `verify_binding` | Implicit — a plane *holds* the mint; no `owner` field | **Existing** |
| R2 | `relationship_graph_resolution` | `uga_engine.py:1161, 1419, 1737` (measures `CAA-INV-05`) | `alignment.py::_vocabulary_findings` → `verify_binding` | **Explicit** — `model_owner{authority, home, owns}` | **Existing** |
| R3 | `certification_authority_resolution` | **None** | **None** | Role-based (`AUTHORITY` / `PROJECTION` per surface); no owner field | **Partial** |
| R4 | `identity_namespace_resolution` | **None** | **None** | **Explicit** — `canonical_pattern_ownership[].owner`, one of which self-reports `validated_by: "none — informal convention, recorded here as fact, not newly enforced by this binding"` | **Partial** |
| R5 | `existence_resolution` | **None.** Cited in prose by `engine/uckp/uga_projection.py:1-14`; its `declared_projections` entry was *implemented as code* without ever being *read* as data | **None** | Role-based; no owner field | **Partial** |
| R6 | `lifecycle_resolution` | **None** | **None** | Role-based; carries an `open_item` marked `NOT RESOLVED` | **Partial** |
| — | `category_ownership_resolution` | — | — | — | **Missing** |

Two further `*_resolution` keys exist in the repository (`00-MASTER/ACEE-000001/acee-declaration.json` and `00-MASTER/UCL-000001/ucl-declaration.json`, both `relationship_model.target_identity_resolution`). Both are a **two-element list of strings** (`["cko", "registry"]`) nested inside a declaration — a naming coincidence, not an instance of the pattern. Recorded here so a future implementer does not have to re-establish that they are unrelated.

**Summary: Existing 2, Partial 4, Missing 1.**

### 6.3 The load-bearing structural finding — the pattern is recognitive, not constitutive

Every one of the six sections does the same thing, and it is **not** what "ownership" usually means:

> Each section takes a set of instruments that *already exist and already act*, and declares that their apparent rivalry is in fact a bounded, orthogonal, or projective relationship — then states the test that would falsify that declaration.

The falsification test is present in five of six sections under a near-identical name (`second_authority_test` ×4, `second_model_test` ×1), and R2 carries the equivalent inline. Not one section **grants** a right, **assigns** a monopoly, or **forbids** a future actor from acting. Every one **recognises** a standing that measurement already shows to hold, and pins the measurement that would show it had stopped holding.

This is enforced by the binding's own text, in two places read directly:

- `non_goals` — the binding must not be "creating an authority"; `platform/tests/test_constitutional_authority_alignment.py:104` asserts that string is present, so the property is tested, not merely stated.
- `extension_rule.what_this_forbids` — "A second registry, engine, lifecycle, identity authority, relationship graph or evolution system standing beside the ones that exist."

**Consequence for this determination.** `PHASE-UCF-007`/`008` posed category ownership prospectively — *who is entitled to populate a category*. Written that way, a `category_ownership_resolution` entry would be the **first constitutive claim in the file**: a grant of exclusive right, arbitrating future conduct rather than recognising present standing. That is a different kind of object wearing the pattern's clothes, and it is precisely how a second authority system gets built inside the file that exists to forbid one.

**Determination D1: `category_ownership_resolution` must be written in recognitive form.** It records, per populated category, the provider that *does* populate it and the accountable party for that population, together with a `second_populator_test` stating exactly what a second populator would look like and what it would mean. The prohibition ("no undeclared second populator") is then a property of the **recognition drifting from measurement**, not a right conferred on a provider — structurally identical to `CAA-INV-05`, which does not grant `graph.py` a monopoly on relationships but measures that every projection's kinds still bind into the model it owns.

### 6.4 A complete precedent that is not in this file

`00-BOOK/DATA/exclusion-register.json` is the repository's one fully-realised instance of the shape category ownership needs, and no prior determination cites it: a DATA register whose 32 `entries[]` each carry `{rule, class, owner, producer, rationale}`, governed by its own declared `invariants[]`, and **actually read by three production modules** (`platform/repository_intelligence/contamination.py`, `evidence_universe.py`, `00-MASTER/UCOS-RIB-001/rib_engine.py`) plus a dedicated test module.

It is worth naming for one reason: it demonstrates that a per-entry `owner` + `rationale` register with real readers is an established, working repository form — so a `category_ownership_resolution` with readers is not novel infrastructure in the repository, only novel *in this file*. Its `invariants[]` also model the discipline § 12 will need: *"No entry may be added for a path whose correct disposition is deletion — exclusion is not a disposal mechanism."* The category analogue is stated as D9 (§ 10.3).

---

## 7. § 2 — Category Ownership Model Alignment

### 7.1 Mapping to `PHASE-UCF-008`'s options

The mission's five options are lettered differently from `PHASE-UCF-008`'s. Mapped explicitly so neither document is misread:

| This mission | `PHASE-UCF-008` | Status there |
|---|---|---|
| A. Existing resolution ledger | Option D / 4 | **Selected** |
| B. Ownership facet extension | *(not evaluated — new to this mission)* | — |
| C. Provider declaration | Option B / 2 | Rejected |
| D. New binding object | Option C / 3 | Correct future evolution |
| E. Hybrid approach | *(not evaluated)* | — |

`PHASE-UCF-008`'s Option A (a property of the `Term` primitive) is not among this mission's five and is not reopened; its disqualification on blast radius stands.

### 7.2 Evaluation

| Option | Authority correctness | Duplication risk | Schema impact | Future scalability |
|---|---|---|---|---|
| **A. Existing resolution ledger** | **Correct, conditionally** — correct *iff* written recognitively (D1). The file already answers "which authority holds which bounded question" five times over; a sixth answer joins that system rather than beginning one | **Lowest** — no new file, no new authority model, no new invariant family (§ 12.2), no new reader pattern; `verify_binding` ignores unknown top-level keys, so the section lands without perturbing any existing check | One appended top-level section. Zero Layer Zero primitives touched | Sufficient at 4 providers / 35 categories, and the `MULTIPLE_INDEPENDENT_AUTHORITIES` shape already proves declared plurality works here |
| **B. Ownership facet extension** | **Wrong grain, and now disproven by measurement.** Facet 7 is per-object accountability. The population carries **246 distinct owners**, and 7 of the 21 categories hold objects with many owners each — `engine` alone has 116. There is no aggregation of Facet 7 that yields one category owner, and asserting one would overwrite a fact 5,982 objects already answer correctly | **High** — a category-grain assertion replicated onto every object drifts the moment one object is re-minted | Changes a Layer Zero value type consumed by `registry.by_owner()`, `intelligence.risk_reasoning()`, `governance._who_owns()`, and `graph.derive_edges()` | Poor — cost grows with the population, not with the category count |
| **C. Provider declaration** | **Wrong** — unchanged from `PHASE-UCF-008 § Option B`: self-declaration cannot arbitrate a collision between two self-declarers, and the interested party would adjudicate its own claim | **High by construction** | A federation contract nothing consumes | Poor |
| **D. New binding object** | **Correct eventually** — a `relationship`-category UCKO would gain lifecycle, provenance, evidence chain and certification for free, and `relationship` is a declared, zero-population `GOVERNED_CATEGORY` awaiting exactly this | **Moderate today** — it would be the **first** object-plane answer to a question the file answers on the data plane five times, i.e. two homes for one class of fact | New object family, new provider or an extension to `alignment.py`'s object set | Best long-run |
| **E. Hybrid** | **Already true in the weak sense, and correct** — the declaration on the data plane (A) and the measurement in Layer Zero (`intelligence.py`, built by `PHASE-UCF-011`) is *precisely* the "two readers, one truth" discipline `relationship_graph_resolution.model_term_sources` states in its own words: *"These lists are NOT copied here… verify_binding checks this map against the vocabularies, so there is one truth and a test between the planes rather than two lists that can drift."* | Low — provided the ledger **declares owners and never copies the measured population** | None beyond A | Same as A |

### 7.3 Determination

**D2: Option A, in the hybrid arrangement the file already uses (E) — and explicitly not a second mechanism.**

- The **declaration** lives in `category_ownership_resolution`, a seventh section of the existing binding, recognitive in form (D1).
- The **measurement** stays where `PHASE-UCF-011` put it: `intelligence.category_populations()` in Layer Zero. The ledger never restates the 21-row population map; it declares owners, and a verifier resolves the two.
- **D3: the ledger must not copy measured facts.** Object counts, provider names per category, and the populated-category list are all measurements. A ledger that copied them would create the second truth `model_term_sources` exists to refuse, and would be stale the day a provider adds an object.
- Option D is reaffirmed as the correct future evolution, unblocked by nothing this determination requires. Options B and C are rejected — B now with direct measurement behind the rejection rather than argument.

---

## 8. § 3 — Ownership vs Authority vs Provider

### 8.1 The three, as the codebase already holds them

| Concept | Facet | Where it lives | Grain | Cardinality | Derived or declared |
|---|---|---|---|---|---|
| **Provider** — creates or supplies objects | 21 | `DiscoveryDescriptor.provider` | Per object | 4 live values; **plural-capable per category by construction** | **Measured.** Never declared |
| **Owner** — the responsible entity | 7 | `Ownership.owner` | Per object | **246 live values** | Set at mint |
| **Authority** — the governing decision source | 5 | `AuthorityBinding.derives_from` | Per object | Strictly single-parent by design | Set at mint |

### 8.2 What each means at *category* grain — the separation this determination fixes

**Provider (category grain): measured, plural-capable, and never authoritative.** The provider set of a category is a fact about what happened, computed by `category_populations()`. `PHASE-UCF-005`'s defect was this fact being read as if it settled entitlement. It settles nothing.

**Owner (category grain): declared, singular, and *not* a value from Facet 7's value space.** This is the determination's second measurement-backed finding. If a category owner were drawn from the same value space as `Ownership.owner`, then the owner of `engine` would have to be chosen among **116** live candidates, `knowledge` among 106, `concept` among 94 — an adjudication no evidence supports and no one has asked for. A category owner is therefore a **governance entity accountable for the category's population policy** (the natural values being `ucos-constitutional-authority`, or a named instrument already bound in `subordinate_instruments`), not an aggregate of the owners of the objects inside it.

**D4: the ledger's `owner` field is distinct in kind from `Ownership.owner` and must be named so it cannot be confused with it** — e.g. `accountable_authority`, never a bare `owner` that invites aggregation from Facet 7.

**Authority (category grain): already resolved, and must not be re-declared.** What a category *is*, and which categories are governed, is `GOVERNED_CATEGORIES` in `engine/uckp/law.py`, under Article 17. The root law is the decision source; `ROOT_LAW.governs()` is its reader; `constitutional_reasoning()` already adjudicates every object's `taxonomy.category` against it. **There is no vacancy here.** A ledger section that declared an "authority" over categories would create the rival Article 3 makes void.

### 8.3 Required relationships

| Relationship | Determination |
|---|---|
| Authority → Category | **Exists, closed.** `ROOT_LAW` / Article 17. The ledger cites it and adds nothing |
| Owner → Category | **The one fact the ledger declares.** Exactly one accountable authority per entry (plurality expressed as a declared reconciliation, per R3/R5's `MULTIPLE_INDEPENDENT_AUTHORITIES` shape, never as two competing entries) |
| Provider → Category | **Measured only.** Never declared, never entered in the ledger (D3) |
| Provider → Owner | **A recognition, not an identity.** An entry may state that the accountable authority recognises a provider as the category's populator. It must never state that the provider *is* the owner — that substitution is `PHASE-UCF-005`'s defect written into governance |
| Owner → Object owner (Facet 7) | **No relationship.** Explicitly severed by D4. Different grain, different value space, different question |

**D5: three prohibitions, to be enforceable by the eventual verifier.** The ledger may not (i) name a provider as an owner, (ii) declare authority over what a category is, (iii) restate any measured population fact.

---

## 9. § 4 — Ledger Readiness

| Question | Answer | Evidence |
|---|---|---|
| Does the required ledger section exist? | **No** | Direct key check: the binding's six `*_resolution` keys do not include `category_ownership_resolution`; the string appears nowhere in the repository outside `PHASE-UCF-*` documents and one comment in `test_category_integrity.py:18` |
| Does a production reader exist? | **No** — and the gap is wider than `PHASE-UCF-010`'s B3 stated | § 9.1 |
| Does a validator exist? | **Partially — the machinery exists; the moment does not** | § 9.2 |
| What is missing? | Five distinct things | § 9.3 |

### 9.1 Reader — confirmed absent, and the absence is repository-wide

No file under `engine/` opens `00-BOOK/DATA/constitutional-authority-alignment.json`. `alignment.py` declares `ALIGNMENT_BINDING_PATH` as a string and embeds it as object metadata (line 405) but never opens it. The only loads in the repository are `engine/tests/uckp/test_alignment.py:49` (test scope), `platform/tests/test_constitutional_authority_alignment.py:39` (test scope), and `uga_engine.py:1593` (a separate, stdlib-only process that cannot import Layer Zero).

This confirms `PHASE-UCF-010` D4 and extends it: the missing reader is not specific to the new section. **Four of six existing sections are unread by anything**, and the two that are read are read by a process that cannot see the object population at all.

### 9.2 Validator — a refinement of `PHASE-UCF-010`

`verify_binding()` is a complete, fail-closed validator: it checks the supreme authority, all 8 roles, all 8 rules, the relationship-kind bindings against the live vocabularies, and the identity derivation against the live function. It is the right machinery.

**But it has no production invocation.** `require_aligned()` — the fail-closed wrapper — has **zero callers anywhere in the repository**. `verify_binding()` is called from exactly two test modules. The binding is therefore validated in the pytest stage of `verify.sh` and nowhere else.

This is not a defect to fix here, and it does not weaken `verify.sh`. `PHASE-CAA-INV-08-ENFORCEMENT-COMPLETENESS-DETERMINATION` settled that point independently: the pytest stage is Stage 2 of the same fail-closed pipeline, it runs on the live on-disk binding, and `uga_engine.py gate` (Stage 6b) has no invocation path that does not pass through it first — so a `verify_binding()` finding is *exactly as blocking* as a UGA gate failure, and reaches the binding earlier. It is stated here because it changes what "add a validator" means for category ownership: the work is **adding a finding function to an existing validator that already runs in a gate**, not building a validation path. That is materially smaller than `PHASE-UCF-010` B8's phrasing suggested.

### 9.3 What is missing, precisely

| # | Missing element | Size |
|---|---|---|
| L1 | The `category_ownership_resolution` section itself | One appended JSON section |
| L2 | A loader that gives engine code the binding document | One function; **the only genuinely new infrastructure** (§ 15 Q1 is where it lives) |
| L3 | A `_category_ownership_findings()` inside `verify_binding()` | One function beside the four that exist |
| L4 | The join between declared owners (L1) and measured populations (`category_populations()`) | One function; the PASS/UNKNOWN/CONTAMINATION discriminator `PHASE-UCF-011` could not build |
| L5 | A `CAA-INV-09` rule id, **only if** the check is to be gated rather than advisory | Two appended entries (§ 12.2) |

---

## 10. § 5 — Category Backfill Requirements

### 10.1 Required entries

**21 entries — one per populated category.** All 21 are lawful `GOVERNED_CATEGORIES` members (measured this pass; no populated category is un-governed or non-authoritative), so no entry requires a vocabulary change.

| Provider | Categories it solely populates | Objects |
|---|---|---|
| `engine.uckp.constitution` | `constraint`, `law`, `metadata`, `principle`, `taxonomy`, `validation` | 97 |
| `engine.uckp.capabilities` | `artifact`, `capability`, `governance`, `observation`, `runtime`, `transition` | 78 |
| `engine.uckp.alignment` | `authority`, `identity` | 18 |
| `engine.uckp.uga_projection` | `concept`, `engine`, `knowledge`, `policy`, `state`, `verification`, `workflow` | 5,789 |

**D6: the 14 governed-but-unpopulated categories get no entry.** `axiom`, `certification`, `decision`, `dependency`, `event`, `evidence`, `measurement`, `ontology`, `proof`, `registry`, `relationship`, `responsibility`, `simulation`, `timeline` have no populator to recognise. Declaring an owner for an empty category would be constitutive (§ 6.3) — granting a future right — and would also pre-empt `relationship`, the very category `PHASE-UCF-008` identified as the future home of the ownership binding UCKO. `gap_reasoning()` already reports all 14 as unpopulated; that is the correct and sufficient treatment.

### 10.2 Unknown-state handling

`PHASE-UCF-011` collapses PASS into UNKNOWN because no declaration exists. After backfill, three states become distinguishable, and **UNKNOWN must survive as a state** rather than being defined away:

| State | Condition after backfill | Count today | Count after a complete backfill |
|---|---|---|---|
| PASS | declared owner, measured providers ⊆ recognised populators | 0 | 21 |
| UNKNOWN | populated, no entry | 21 | 0 — but **must remain reachable**, because a 22nd category can be populated tomorrow by a new provider before anyone declares it |
| CONTAMINATION | measured providers ⊄ recognised populators | 0 | 0 |

**D7: UNKNOWN is a permanent state of the model, not a transitional one.** Removing it once the backfill completes would make the check silently pass for any category invented after the ledger was written — reintroducing `PHASE-UCF-005`'s exact blind spot one layer up.

### 10.3 Migration requirements

**D8: the backfill is a mechanical recognition, not an adjudication — and this is its lowest-risk moment.** Zero categories are contested; every one of the 21 has exactly one populator. The migration therefore contains no decision that could be got wrong, only a transcription that a verifier can immediately check against measurement.

**D9: the backfill must not be used to legitimise a contamination.** Borrowing the exclusion-register's own discipline (*"exclusion is not a disposal mechanism"*): if a category ever holds two providers at backfill time, the entry may not simply recognise both. Recognising a plurality is a `MULTIPLE_INDEPENDENT_AUTHORITIES`-shaped declaration requiring the same `bounded_question`-per-authority justification R3 and R5 carry — not a shortcut to make a finding disappear.

**Migration steps (specification only; nothing performed here):** append the section with 21 recognitive entries and a `second_populator_test` → add the loader (L2) → add the join (L4) → observe the count fall from 21 UNKNOWN to 21 PASS → then, and only then, consider gating. The `test_no_declared_owner_exists_for_any_category_yet` tripwire `PHASE-UCF-011` installed fires at step 4 by design.

---

## 11. § 6 — Advisory Governance Readiness

The required flow: **Observation → Advisory Finding → Human/System Resolution → Ledger Update.**

### 11.1 Stage-by-stage readiness

| Stage | Mechanism that would serve it | Status |
|---|---|---|
| **Observation** | `intelligence.category_populations()` + `gap_reasoning()` | **Present** — built by `PHASE-UCF-011`; 21 observations live |
| **Advisory Finding** | `Finding(reasoning, severity, subject, statement)` → `report()` → `ucos-uckp reason --json` | **Present in form; missing its content** — the finding cannot yet name *which* declaration is missing or violated, because L1/L2/L4 do not exist |
| **Human/System Resolution** | See § 11.3 | **Present, and already in use — no new mechanism required** |
| **Ledger Update** | Append to the binding; `change-ledger.json` already records change events by subject; Article 12 forbids mutation of prior state, so a correction is a new appended fact | **Present** |

### 11.2 No new severity tier is required

The complete severity vocabulary is two strings — `VIOLATION` and `OBSERVATION` (`intelligence.py:66-67`) — on a plain `str` field, not a closed enum. A third value is therefore mechanically additive.

**D10: do not add one.** `ReasoningResult.clean` is `not violations`, so an "advisory" severity would be exactly as non-gating as `OBSERVATION` while adding a tier whose only consumer is this one check. The distinction that actually matters is not severity but **state** — PASS vs UNKNOWN vs CONTAMINATION — and that is carried by the finding's content and by the `observations` metrics `PHASE-UCF-011` already emits. The advisory stage is reached when a finding becomes *actionable* (it names the missing or contradicted declaration), not when a new tier is invented. Recorded as reversible: because `severity` is an open string, evidence could later justify a third value without a structural change.

### 11.3 The human-resolution step already exists, and inventing one would duplicate it

Three candidate mechanisms were examined:

- **`UCOS-FND` findings** (`00-BOOK/SCHEMAS/finding.schema.json`) — a real state machine (`OPEN → IN_PROGRESS → ACCEPTED/RESOLVED/FALSE_POSITIVE`) with `approver`, `evidence`, and time-boxed `expires`. **Rejected as the host:** it is the security-intelligence entity family (UKB-005), corpus-registered and scoped to vulnerabilities and controls. Bending it to constitutional category governance would give one schema two unrelated authorities.
- **`exclusion-register.json`** — per-entry `owner` + `rationale`, real readers. **Rejected as the host** for the same reason (it governs ignored paths), but retained as the **structural model** (§ 6.4).
- **The determination document + ledger append** — twelve `PHASE-UCF-*` documents, each recording a bounded question, the evidence, the decision, and the resulting repository change. **Selected.**

**D11: the human-resolution mechanism is the determination-document-and-append pattern this arc has used twelve times.** A workflow object, an approval state machine, or a resolution queue for category ownership would be a governance system standing beside the one the repository demonstrably already runs — the exact thing `extension_rule.what_this_forbids` names. The advisory stage needs **no** new resolution machinery.

### 11.4 Advisory-stage requirements, complete

| # | Requirement | Present? |
|---|---|---|
| A1 | `category_ownership_resolution` exists, 21 recognitive entries (L1, D1, D6) | No |
| A2 | A loader exposing the binding to engine code (L2) | No |
| A3 | The declared-vs-measured join (L4), preserving all three states (D7) | No |
| A4 | Findings name the specific missing or contradicted declaration | No — blocked on A1–A3 |
| A5 | Non-gating: `clean` and `certified` unmoved | **Yes** — `validation.py` has zero references to `intelligence`; `clean` is `not violations` |
| A6 | A regression fixture pinning the live population (`PHASE-UCF-010` B4) | **Yes** — `test_no_category_in_this_repository_is_populated_by_two_providers` |
| A7 | A resolution mechanism | **Yes** — D11, already in use |

**Advisory stage: 4 of 7 requirements outstanding, all four being A1–A4, all four mechanical.**

---

## 12. § 7 — Blocking Governance Readiness

Blocking means a category-ownership finding can fail a gate. Six requirements, stated exactly.

### 12.1 Evidence threshold

**D12: three conditions, all necessary.**

1. **Totality** — the join must cover every populated category. A check that skips a category it could not read has "passed because it never looked."
2. **Fail-closed on unreadable evidence** — an absent, malformed, or unparseable ledger must produce a finding, never a pass. `verify_binding()`'s own contract already sets this precedent (*"a binding that cannot be read as a mapping is a finding, never a pass"*) and `require_aligned()` is the existing wrapper for it.
3. **Recomputability** — the evidence behind any blocking finding must be reconstructible by its reader from the two facets `CATEGORY_EVIDENCE` names. `PHASE-UCF-011` already established and tested this property; blocking must not weaken it.

### 12.2 Validator integration — and the finding that removes `PHASE-UCF-010` B7

`PHASE-UCF-009` and `PHASE-UCF-010` (B7) both determined that blocking requires "a sibling invariant family inside `engine/uckp/`, separately namespaced, because `UCKP_INVARIANTS` is a closed 17-member tuple with a 1:1 probe dict and `orphan_probes()` guarding both directions." That analysis of `UCKP_INVARIANTS` is correct and unchanged.

**The conclusion drawn from it is now refined by direct measurement: the sibling family already exists.**

`ALIGNMENT_RULES` in `engine/uckp/alignment.py` **is** a separately-namespaced invariant family (`CAA-INV-*`) living inside `engine/uckp/`, enforcing articles the law already holds and adding none. Measured properties that make it the correct host:

| Property | Measured evidence |
|---|---|
| It is **not** a closed, count-pinned enumeration | It has already grown from 7 to 8 (`CAA-INV-08`, added in the CMG/UCKP reconciliation per `conftest.py:196`). No test anywhere asserts `len(ALIGNMENT_RULES)`; `test_alignment.py` iterates the tuple rather than counting it |
| It already supports **two measurement homes** | `CAA-INV-01…07` are measured by the stdlib `uga_engine.py`; **`CAA-INV-08` is measured in Layer Zero by `verify_binding()` itself** (`uga_engine.py:964` states this explicitly) and is correspondingly **absent** from `uga-declaration.json`'s `alignment_invariants` list |
| A Layer-Zero-measured rule perturbs no other gate | `uga_engine.py`'s structural fingerprint (line 1158-1159) draws from `uga-declaration.json`'s `invariants` and `alignment_invariants`, not from the CAA binding's `invariants` list. `platform/tests`' `ALIGNMENT_INVARIANTS` tuple is a per-id substring check over the gate's stdout — a subset assertion, so an id measured elsewhere does not break it |
| It runs inside an existing gate | `verify_binding()` executes in `verify.sh`'s pytest stage via two test modules |

**D13: `CAA-INV-09 — EVERY_POPULATED_CATEGORY_RECOGNISES_ITS_POPULATOR` is the correct blocking home, and no new invariant family should be created.** `CAA-INV-08` is the exact precedent: a rule whose subject the stdlib engine cannot see, declared in `alignment.py`, measured in Layer Zero, absent from the UGA declaration. Provider×category population is likewise invisible to a stdlib process — it requires `build_universe()` — so it belongs on the same footing.

This is not an inference drawn only here. `PHASE-CAA-INV-08-ENFORCEMENT-COMPLETENESS-DETERMINATION` examined that rule's split measurement home directly and determined (verdict C) that it is *"not an enforcement gap… measured at a different, already-mandatory point in the same fail-closed pipeline, for a structural reason documented in `uga_engine.py`'s own source"* — and rejected duplicating it into the stdlib engine as *"a second implementation of an already-enforced check."* A category-ownership rule measured in Layer Zero therefore lands on a footing the repository has already examined and ratified, and the same reasoning forbids the mirror-image mistake of building a third invariant family to house it.

**This closes `PHASE-UCF-010` B7 as already satisfied.** Creating a third family beside `UCKP-INV` and `CAA-INV` for one rule would be the duplicate authority system this determination exists to prevent.

### 12.3 Conflict resolution

**D14: a conflict rule is required before blocking, and is still deferred — with its form now fixed.** Zero categories are contested, so specifying adjudication remains speculative. But its *shape* is determined: a legitimate plurality is declared exactly as R3 and R5 declare theirs — an explicit `MULTIPLE_INDEPENDENT_AUTHORITIES`-shaped model with a distinct `bounded_question` per populator, plus the `second_populator_test` that would falsify it. An unreconciled plurality is CONTAMINATION. There is no third disposition, and D9 forbids using an entry to make a finding disappear.

### 12.4 Migration completeness, and the remaining two

| # | Requirement | Status |
|---|---|---|
| B-1 | Advisory stage complete (A1–A4) | Outstanding |
| B-2 | UNKNOWN empty — all 21 categories declared, with UNKNOWN still *reachable* (D7) | Outstanding |
| B-3 | Conflict-resolution rule exists (D14) | Deferred; shape fixed |
| B-4 | Evidence threshold met (D12) | Outstanding |
| B-5 | Validator integration via `CAA-INV-09` (D13) | Outstanding; **no new family needed** |
| B-6 | The ledger itself under a verifier so the gate does not rest on unverified evidence (`PHASE-UCF-010` B8) | **Reduced to L3** — a finding function inside a validator that already runs in a gate (§ 9.2) |

---

## 13. § 8 — Testing Strategy

No tests are written, designed in code, or modified here. `PHASE-UCF-011`'s 23 tests are unaffected by everything below; every scenario is additive.

| Scenario | What it must prove | Constructible today? |
|---|---|---|
| **Declared ownership success** | A category whose declared populator matches its measured providers reports PASS, and PASS is distinguishable from UNKNOWN in the finding, not merely absent from it | **No** — needs A1–A3. Then: `mint_object(category=X, provider=P)` + `RegistryView` + a ledger-document fixture |
| **Missing ownership** | A populated category with no entry stays UNKNOWN and is never silently upgraded to PASS | **Partly** — the UNKNOWN half is live today (21 findings); the "never silently upgraded" half needs the join |
| **Conflicting ownership** | Two entries claiming one category, or one entry naming two unreconciled populators, is a finding — and a *reconciled* plurality with distinct `bounded_question`s is not | **No** — the only scenario `PHASE-UCF-011` named as unconstructible; needs A1–A3 |
| **Provider misuse** | A provider populating a category recognised for another reports CONTAMINATION, and the finding names both the measured and the declared side | **Half** — contamination detection is live and tested; the declared side needs A1–A3 |
| **Category extension** | A newly populated 22nd category with no entry reports UNKNOWN rather than passing by omission (D7); and a governed-but-unpopulated category gets no entry and no PASS (D6) | **Yes for the D6 half** (`test_an_unpopulated_governed_category_is_not_reported_as_undeclared`); the D7 half needs the join |

**Additional tests this determination's own findings require:**

| # | Test | Guards |
|---|---|---|
| T1 | The ledger names no provider as an owner | D5(i) |
| T2 | The ledger restates no measured fact — no object counts, no provider lists | D3, D5(iii) |
| T3 | Every ledger entry names a populated category; no entry names one of the 14 empty ones | D6 |
| T4 | An unreadable or absent ledger produces a finding, not a pass | D12(2) |
| T5 | The ledger's `accountable_authority` values are never drawn from the Facet-7 owner space | D4 |

**Required new fixture: one** — a ledger-document fixture. Every other harness element (`mint_object`, `RegistryView`, `registry_of`, `_reason()`, the `universe` session fixture) already exists and is proven by `PHASE-UCF-011`'s suite.

---

## 14. § 9 — Governance Impact

### 14.1 By stage

| Requirement | Ledger + reader (Advisory) | Blocking (`CAA-INV-09`) |
|---|---|---|
| **Constitutional change** | **Not required.** No article, invariant, or stop condition moves; `verify_binding()`'s counts (20/17/13) derive from `ROOT_LAW`, untouched | **Not required** — a `CAA` rule enforces an article that already exists (Article 17 for what a category is; Article 1 for the no-second-authority property). This is the whole design of the family |
| **New invariant family** | Not required | **Not required — refines `PHASE-UCF-010` B7.** `CAA-INV-*` is the existing sibling family and it is open (D13) |
| **Authority update** | **Not required.** Ownership of this question was settled by `PHASE-UCF-007` and is unchanged | Not required |
| **Registry change** | **Yes — one JSON section appended.** No canonical object is minted; `verify_binding()` ignores unknown top-level keys, and `uga_engine.py`'s structural fingerprint does not draw from the section list, so the append perturbs no existing check | **Yes, and measurable — see § 14.2** |
| **Governance registration** | The binding file is already governed as `UCOS-TOOLING-000035` (`id-ledger.json` `by_object`); an edit needs no new registration | Same |

### 14.2 The registry change blocking would cause, quantified

This is stated because no prior determination measured it. `alignment.py::alignment_objects()` mints one `rule_object` **per** `ALIGNMENT_RULES` member, and `alignment_object()`'s own `definition` string interpolates `len(ALIGNMENT_RULES)`. Today `authority` holds 17 objects = 8 roles + 8 rules + 1 binding object.

Adding `CAA-INV-09` therefore:

- adds one canonical object: `authority` **17 → 18**, total admitted **5,982 → 5,983**;
- changes the alignment object's `definition` text, hence its content hash and semantic digest;
- requires the rule in **two** places (`ALIGNMENT_RULES` and the binding's `invariants` list) and, per the `CAA-INV-08` precedent, **not** in `uga-declaration.json`.

Three tests pin counts that would move (`PHASE-UCF-011 § Validation Results` records `CAA-INV-04` measuring 5,827 and the UGA counts). **This is a real, if small, canonical-state change and must be scoped as its own step — not folded into the ledger append**, which changes nothing canonical at all.

**D15: the ledger + reader + join (Advisory) and the `CAA-INV-09` rule (Blocking) are two separate phases.** The first mints nothing and moves no count; the second mints an object and moves several. Landing them together would make a governance edit and a canonical-state change indistinguishable in one diff.

---

## 15. Validation Results

Run after this document was created, per instruction. `./verify.sh` was **not** run.

| Check | Result |
|---|---|
| `verify_binding(constitutional-authority-alignment.json)` | `()` — **PASS** |
| `build_universe().registry.discover()` | `providers_found=('engine.uckp.alignment', 'engine.uckp.capabilities', 'engine.uckp.constitution', 'engine.uckp.uga_projection')`, `objects_admitted=5982`, `failures=()` |
| `validate_universe(build_universe())` | `verdict='certified'`, `certified=True`, `blocking_failures=()` |
| `00-BOOK/tools/ukb.py enforce --pre` | **PASS** — 1,259 eligible, 1,233 registered, 26 unregistered-eligible, 0 unclassified, 0 invalid, 0 gated |
| `00-BOOK/tools/ukb.py validate` | **PASS** — 1,233 artifacts, append-only page ledger intact, referential integrity OK, 0 executions |

Identical to `PHASE-UCF-011`'s post-implementation baseline. No drift, no corruption, nothing changed by producing this document. The 26 unregistered-eligible artifacts are the untracked `PHASE-*` determination documents awaiting `git add` — a pre-existing, reported (not gated) condition unchanged since `PHASE-UCF-008 § Current Repository Truth`.

---

## 16. Gap Reassessment

| Gap | Prior classification | This determination | Basis |
|---|---|---|---|
| `category_ownership_resolution` section absent (B1) | Required — Advisory | **Required — unchanged**, form now fixed as recognitive (D1) and scoped to 21 entries (D6) | § 6.3, § 10.1 |
| Ledger unpopulated for 21 categories (B2) | Required — Advisory | **Required — unchanged.** Lowest-risk moment confirmed again: 0 contested | § 10.3 |
| No production reader (B3) | Required — Advisory | **Required — unchanged.** The one genuinely new piece of infrastructure (L2) | § 9.1 |
| PASS indistinguishable from UNKNOWN | Required — Advisory | **Required — unchanged** (L4), with UNKNOWN determined permanent (D7) | § 10.2 |
| No conflict-resolution rule (B6) | Deferred | **Deferred — shape now fixed** (D14): `MULTIPLE_INDEPENDENT_AUTHORITIES` with per-populator `bounded_question`, or CONTAMINATION. No third disposition | § 12.3 |
| **No sibling invariant family inside `engine/uckp/` (B7)** | Required — Blocking | **CLOSED — the family already exists.** `CAA-INV-*` in `alignment.py` is separately namespaced, already grown once, count-unpinned, and already supports a Layer-Zero measurement home (`CAA-INV-08`) | § 12.2, D13 |
| Ledger not under a verifier (B8) | Required — Blocking | **Reduced** — `verify_binding()` is the validator and already runs in a gate; the work is one finding function (L3), not a validation path | § 9.2, § 12.4 |
| **New: the resolution pattern is recognitive, never constitutive** | *(not previously named)* | **Required — governs the section's form.** All 6 sections recognise standing and carry a falsification test; none grants a right | § 6.3 |
| **New: a category owner cannot be derived from Facet 7** | *(not previously named)* | **Required — governs the field's naming and value space (D4).** 246 distinct owners live; `engine` alone has 116 | § 4, § 8.2 |
| **New: `require_aligned()` has zero callers; `verify_binding()` is pytest-only** | *(not previously named)* | **Observational.** Not a defect (pytest is a gate stage); it correctly sizes the B8 work | § 9.2 |
| **New: `CAA-INV-08` is measured in Layer Zero, not by the stdlib engine** | *(not previously named)* | **Closed** — it is the precedent D13 rests on, and corrects `PHASE-UCF-011`'s "`CAA-INV-01..07`" phrasing | § 5.1, § 12.2 |
| **New: adding a `CAA` rule mints a canonical object (+1, `authority` 17→18)** | *(not previously named)* | **Required — forces the two-phase split (D15)** | § 14.2 |
| **New: `exclusion-register.json` is the complete DATA-register-with-owner precedent** | *(not previously named)* | **Observational.** Structural model for the section; its "exclusion is not a disposal mechanism" invariant is adopted as D9 | § 6.4 |
| **New: no advisory severity tier exists, and none should be added** | *(not previously named)* | **Closed** (D10). Two severities live, on an open `str` field; state, not severity, is the distinction that matters | § 11.2 |
| **New: the human-resolution step already exists** | *(not previously named)* | **Closed** (D11). The determination-document-and-append pattern, used twelve times in this arc | § 11.3 |
| The 14 governed-but-unpopulated categories | Observational | **Observational — and now explicitly excluded from backfill** (D6) | § 10.1 |
| `"relationship"` is the future home for an ownership-binding UCKO | Observational | **Observational — unchanged**, and D6 protects it from being pre-empted by an empty-category entry | § 10.1 |
| Four `*_resolution` sections with no machine reader | Observational (`UCF-010` Q3) | **Observational — measured again and unchanged at 4 of 6.** Still outside this arc | § 6.2 |
| Semantic-duplicate category registration | Deferred | **Deferred — unchanged** | `UCF-007` |
| Provider certification / pre-flight checklist | Deferred | **Deferred — unchanged** | `UCF-008` |
| Onboarding documentation | Deferred | **Deferred — unchanged** | `UCF-007` |
| Vocabulary-term registration has no registrar capture | Observational | **Observational — unchanged** | `UCF-008` |
| `Ownership.stewards` for delegated producers | Observational | **Observational — and now less likely to be the answer**, since D4 severs the category-owner value space from Facet 7 entirely | § 8.2 |

**Required: 4** (L1, L2, L3+L4, and the ledger content). **Deferred: 4. Observational: 7. Closed: 5** — including B7, which no longer requires any work.

---

## 17. Final Determination

# CONDITIONALLY READY

The condition is **form and sequence, not capability.** Every mechanism category ownership governance needs already exists in this repository; none of them needs to be duplicated. What is not yet settled is content (the 21 entries) and three small pieces of wiring.

### The integration answer, stated directly

Category ownership joins the existing constitutional resolution system as a **seventh `*_resolution` section of `00-BOOK/DATA/constitutional-authority-alignment.json`**, written **recognitively** — recording the populator each category already has and the authority accountable for it, with a `second_populator_test` mirroring the `second_authority_test` that five of the six existing sections carry. It declares no right, arbitrates no future conduct, and creates no authority, because not one of the six sections beside it does either.

It is **read** by the same `verify_binding()` that already validates the two sections which have readers, through one added finding function. It is **measured** by `intelligence.category_populations()`, built in `PHASE-UCF-011` — the declaration on the data plane and the measurement in Layer Zero, which is exactly the "two readers, one truth" discipline `relationship_graph_resolution` states in its own words. It is **enforced**, if and when enforcement is justified, as **`CAA-INV-09` in the existing `CAA` family** — not a new invariant family, because `CAA-INV-08` already proves that family accepts a rule measured in Layer Zero rather than by the stdlib engine.

**No duplicate authority system is required at any stage. `PHASE-UCF-010`'s B7 is closed by measurement rather than by construction.**

### Implementation prerequisites

| # | Prerequisite | Stage | Notes |
|---|---|---|---|
| P1 | Append `category_ownership_resolution` with **21** recognitive entries and a `second_populator_test` | Advisory | D1, D3, D5, D6. Mints nothing; moves no count |
| P2 | A loader exposing the binding document to engine code | Advisory | L2 — the only new infrastructure. Location unresolved (Q1) |
| P3 | `_category_ownership_findings()` inside `verify_binding()` | Advisory | L3. Fail-closed on an unreadable ledger (D12) |
| P4 | The declared-vs-measured join, preserving PASS / UNKNOWN / CONTAMINATION | Advisory | L4, D7 |
| P5 | Tests T1–T5 plus the four mission scenarios | Advisory | One new fixture (a ledger document); everything else exists |
| P6 | A conflict-resolution rule | Blocking | D14 — form fixed, content still deferred pending an actual conflict |
| P7 | `CAA-INV-09`, **as its own phase** | Blocking | D13, D15. Mints one object; `authority` 17 → 18, total 5,982 → 5,983 |

### Remaining gaps

Four Required (P1–P4, with P5 as their test obligation), four Deferred, seven Observational. Full table in § 16. The single largest change from the prior determination is subtractive: the new invariant family `PHASE-UCF-009` and `PHASE-UCF-010` both required does not need to be built.

### Unresolved architectural questions, carried forward

1. **Where does the loader (P2) live?** `alignment.py` owns the binding's contract and declares its path but is deliberately pure-functional over a caller-supplied mapping; adding file I/O changes its character. Open since `PHASE-UCF-010`. This determination adds one input: the loader would serve **all six** existing sections, not only the seventh, which argues for a location chosen for the file rather than for this capability.
2. **Should the four unread sections (`existence`, `lifecycle`, `certification_authority`, `identity_namespace`) come under a reader at the same time?** P2 makes them readable for the first time. Solving reader coverage once for `category_ownership_resolution` alone leaves four sections declared and unchecked. Raised in `PHASE-UCF-010 § 5.2`; still outside this arc's scope, but P2 is the moment the choice becomes cheap.
3. **What are the 21 `accountable_authority` values?** D4 severs them from the Facet-7 owner space and D1 requires them to be recognitive, but the actual values — `ucos-constitutional-authority` for all 21, or per-provider entities already bound in `subordinate_instruments` — are a content decision this determination deliberately does not make, because making it here would be the constitutive act § 6.3 rules out.
4. **Is `uga_projection`'s 5,789-object, seven-category footprint one recognition or seven?** It populates a third of the category space through a single declared projection. Whether that is one accountable standing or seven independent ones is a content question P1 must answer and no measurement can settle.
5. `PHASE-UCF-008`'s open question 2 — whether `Ownership.stewards` generalises to delegated category producers — remains unresolved, and D4 makes it materially less likely to be the right mechanism.

---

Stopping after PHASE-UCF-012, as instructed. Minimum validation (`verify_binding()`, `discover()`, `validate_universe()`, `ukb.py enforce --pre`, `ukb.py validate`) run fresh and reported in § 15. `./verify.sh` was not run. No code, test, registry, schema, invariant, ledger, or constitutional document was created or modified.
