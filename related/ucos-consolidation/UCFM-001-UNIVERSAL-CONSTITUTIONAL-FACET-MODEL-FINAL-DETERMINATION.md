# UCFM-001 — Universal Constitutional Facet Model · Final Determination

**Checkpoint:** `00bd45f` (integration/recovery-001)
**Determination date:** 2026-08-06
**Authority:** Repository Truth only.
**Resumption:** Resumed from the exact interruption point in the DISCOVERY phase. Every prior measurement is reused, not recomputed.
**Posture:** Determination only. No implementation, no migration, no consolidation, no constitution edited, no facet model created. **Zero files modified.**

---

## Preamble — the determination, and a withdrawal

> ## The six facet models are CONSTITUTIONALLY COMPATIBLE.
>
> They are **not** competing authorities. They are **scope-specific models over three distinct subject classes (E)**, of which one set — the four family models — is **a single model expressed as a legislated monotonic inheritance chain (C)**, and both are **projected through one open declaration surface (B)**.
>
> **Answer to the primary objective: E + C + B. Not A. Not D.**

### Withdrawal of B-1

`UCOS-P0-CONVERGENCE-001` recorded **B-1 (CRITICAL)** — *"Six parallel facet models… no two family sets identical… no crosswalk exists."*

**B-1 is WITHDRAWN.** The reasoning was inverted. I treated the fact that no two families declare the same six facets as evidence of conflict. Repository Truth shows the opposite: **each family is required to declare a different six, and the exact difference is legislated by that family's own founding law.** The variance is the proof of correctness, not of conflict.

The crosswalk I reported as missing exists, and is normative: it is `UPL-01`, `UDL-01`, `USL-01`, `UAL-01` and the four `-02` Laws of Foundation Reuse. I had not read them when the convergence determination was written.

---

## OUTPUT 1 — Universal Constitutional Facet Model Determination

### 1.1 Three subject classes, three models — not one contested subject

A facet model is only in competition with another if both govern **the same subject**. Measured, they do not:

| Model | Subject class it governs | Question it answers | Authority |
|---|---|---|---|
| **F-1 · UCKP 33** | A **canonical knowledge object** (UCKO) | *"What must every constitutional object be able to answer about itself?"* | `UCKP-ART-06` |
| **F-2 · UKIP 6** | A **classification decision** | *"What must a complete classification decide?"* (`classification.py:50`) | UKIP |
| **F-3…F-6 · Family 6** | An **architecture concept within a layer** | *"What cross-cuts every concept at this layer?"* | `UPL/UDL/USL/UAL-01` |

Three subjects. Three models. `UCKP-ART-03` (Zero Duplication) forbids authoring *the same knowledge* twice; it does not forbid three models over three subjects. No subject class carries two models.

### 1.2 The family four are one model, inherited — the decisive evidence

Each family constitution declares its founding law, and each law names **(a)** the layer's own defining concern and **(b)** the exact stack of frozen foundations beneath it. Verbatim:

| Law | Text (verbatim) |
|---|---|
| **UPL-01** | *"Law of Platform as **Composition** Layer — Platform SHALL be founded as an architecture layer upon the frozen **EL-1 + RL-F2** foundations"* |
| **UDL-01** | *"Law of Data as **Representation** Layer — founded… upon the frozen **EL-1 + RL-F2 + PL-F2** foundations"* |
| **USL-01** | *"Law of Service as **Operation** Layer — founded… upon the frozen **EL-1 + RL-F2 + PL-F2 + DF-2** foundations"* |
| **UAL-01** | *"Law of Application as **Experience** Layer — founded… upon the frozen **EL-1 + RL-F2 + PL-F2 + DF-2 + SF-2** foundations"* |

Now place the declared facet sets beside the declared foundation stacks:

| Family | Foundation stack (from its -01 law) | Inherited facets (from its §2.1) | Own facets | Total |
|---|---|---|---|---|
| **PLATFORM** | EL-1 + RL-F2 → **2** | Identity (EL-1), Runtime (RL-F2) → **2** | Lifecycle, Intelligence, Quality, Certification → **4** | **6** |
| **DATA** | EL-1 + RL-F2 + PL-F2 → **3** | Identity (EL-1), Runtime (RL-F2), **Composition (PL-F2)** → **3** | Intelligence, Quality, Certification → **3** | **6** |
| **SERVICE** | + DF-2 → **4** | … + **Representation (DF-2)** → **4** | Intelligence, Certification → **2** | **6** |
| **APPLICATION** | + SF-2 → **5** | … + **Operation (SF-2)** → **5** | Certification → **1** | **6** |

**Three exact correspondences, none coincidental:**

1. **Inherited-facet count equals foundation-stack depth**, at every layer: 2, 3, 4, 5.
2. **Own-facet count is the exact complement**: 4, 3, 2, 1. The total is invariant at six.
3. **The facet a layer contributes upward is precisely the concern its own -01 law declares it to be.** Platform is declared the *Composition* Layer → contributes `Composition (PL-F2 reuse)`. Data is the *Representation* Layer → contributes `Representation (DF-2 reuse)`. Service is the *Operation* Layer → contributes `Operation (SF-2 reuse)`.

The parenthetical `(X reuse)` annotations are not commentary. They are **inheritance edges naming their source layer**, and they resolve exactly against the stack that layer's law declares.

**The mechanism is legislated by the `-02` laws.** `UPL-02` — *Law of Foundation Reuse* — requires every construct to reuse the lower layers *"**by reference** and SHALL NOT duplicate, replace, modify, or redefine any of them. Violation: any redefinition is void."* Inheritance by reference, redefinition void. That is the crosswalk.

### 1.3 The third tier — the open declaration surface

`platform/universal_foundation/conformance.py:295-330` supplies what the closed enum cannot:

- `FacetDeclaration(path, status, detail)` — a facet addressed by **dotted path**, so *"the contract can name a facet without knowing how the document happens to be grouped."* A path namespace is open and hierarchical, not enumerated.
- `FacetStatus` = `PRESENT | NOT_APPLICABLE` — *"There is deliberately no third, softer value."*
- Every leaf must carry status **and** reason — evidence when present, rationale when not applicable. *"A leaf that states one without the other is refused at construction: 'somebody wrote a key' is not a determination."*

This is the executable form of `UCKP-ART-06`: *"a facet may be **unattested**, but it may never be **absent**."* `NOT_APPLICABLE`-with-rationale is unattested-but-present. Absence is refused at construction.

### 1.4 Canonical Facet Definition

> A **Facet** is a question a constitutional subject must be able to answer about itself. It is mandatory in *presence* and optional in *attestation*: it may be answered `NOT_APPLICABLE` with rationale, but it may never be absent. Facets are declared at three tiers — the **question tier** (closed, amended), the **layer tier** (inherited by reference), and the **declaration tier** (open, path-addressed) — and are answered through typed carriers on the subject.

---

## OUTPUT 2 — Facet Projection Matrix

Measured executably at `00bd45f`. Every derived artifact is derived, not restated:

| Projection | Source | Derived? | Measured |
|---|---|---|---|
| `REQUIRED_FACETS` | `tuple(Facet)` | **YES** | 33; equality to `tuple(Facet)` = **True** |
| `FACET_ATTRIBUTES` | `facet.attribute for facet in Facet` | **YES** | 33; equality = **True** |
| `FACET_VOCABULARY_INSTANCE` | `Term(facet.value, facet.question) for facet in Facet` | **YES** | 33 terms; term-set equality to enum = **True** |
| `_FACET_QUESTIONS` | declared map | Guarded | Construction-time guard at `facets.py:126-127` raises unless every facet declares its question |
| `NucleusProfile` | declaration document | Open | Path-addressed; PRESENT/NOT_APPLICABLE + reason |
| UCKO carriers | `ucko.py:107-136` | Typed | One typed attribute per facet |

**`UCKP-ART-11` is satisfied**: every representation of the facet set is generated from one source. `facets.py:82-84` states the rule — *"The tuple is derived from the enum rather than restated, so a new facet cannot be added and forgotten (Article 3)."*

**The critical projection property, measured:** the facet **enum** is closed, but its **vocabulary projection is open**. `FACET_VOCABULARY_INSTANCE.extended_with(...)` admitted an unknown future facet term and returned a new vocabulary, original unchanged at 33. This is exactly the tiering `facets.py:8-13` declares: *"The enumeration is closed on purpose while the vocabularies inside facets are open."*

---

## OUTPUT 3 — Facet Scope Matrix

| Model | Scope | Cardinality | Growth mechanism | Overlaps? |
|---|---|---|---|---|
| F-1 UCKP 33 | Every UCKO, universally | 33, closed | **Amendment** (`facets.py:9-11`) | No — sole model for UCKOs |
| F-2 UKIP 6 | A classification decision | 6, closed | Code edit *(a `CEP-MOD-002` H-02 finding)* | No — sole model for classification decisions |
| F-3 PLATFORM | Platform-layer concepts | 6 = 2 inherited + 4 own | Layer law | No — sole model at PL |
| F-4 DATA | Data-layer concepts | 6 = 3 + 3 | Layer law | No — sole model at DF |
| F-5 SERVICE | Service-layer concepts | 6 = 4 + 2 | Layer law | No — sole model at SF |
| F-6 APPLICATION | Application-layer concepts | 6 = 5 + 1 | Layer law | No — sole model at AF |
| Declaration tier | How any capability answers any facet | Open, path-addressed | **Registration** | No — a surface, not a model |

**No two models govern the same subject at the same layer. Overlap count: 0.**

---

## OUTPUT 4 — Facet Authority Matrix

| Model | Canonical owner | Authority | Frozen |
|---|---|---|---|
| F-1 | `engine/uckp/facets.py` | `UCKP-ART-06` — constitutional | No |
| F-2 | `engine/knowledge/ukip/classification.py` | UKIP — engineering | No |
| F-3 | `PLATFORM-001` §2.1 + `UPL-01/02` | Architectural | **PL-F1** |
| F-4 | `DATA-001` §2.1 + `UDL-01/02` | Architectural | **DF-1** |
| F-5 | `SERVICE-001` §2.1 + `USL-01/02` | Architectural | **SF-2** |
| F-6 | `APPLICATION-001` §2.1 + `UAL-01/02` | Architectural | **AF-1** |
| Declaration tier | `platform/universal_foundation/conformance.py` | Engineering | No |

**Authority precedence is already fixed and requires no new rule.** `AUTHORITY_TIER_VOCABULARY` (`vocabulary.py:238-247`) ranks constitutional (0) → architectural (1) → engineering (2) → advisory (3). F-1 is constitutional and outranks all. Each family model is architectural and sole within its layer. The declaration tier is engineering and binds nothing.

**No parallel authority exists**: parallel authority requires two owners over one concern. Every model has exactly one owner, and every concern exactly one model.

---

## OUTPUT 5 — Facet Dependency Matrix

| Dependency | Finding | Evidence |
|---|---|---|
| **Engine — assumes 33?** | **NO** in executable code | Three occurrences of `33`: two docstrings/comments, **two are tests** (`test_layer_zero.py:214`, `test_ucko_graph_registry.py:113`). Zero executable dependencies |
| **Engine — fixed ordering?** | **NO** | Order derives from enum declaration; all projections sorted or enum-derived |
| **Engine — fixed identifiers?** | **YES, by design** | `Facet.coerce` raises on unknown (`facets.py:60-69`) — the amendment tripwire |
| **Engine — fixed cardinality?** | **Only in tests** | The two asserts are the *deliberate* tripwire: a 34th facet fails the suite, forcing amendment to be conscious. This is the mechanism working |
| **Engine — hardcoded names/semantics?** | **NO** | `_FACET_QUESTIONS` is data with a construction-time completeness guard |
| **Generator** | **NONE** | `platform/universal_generator` — *"a declaration is the only input"*; zero facet literals (`UCOS-MOD-001` Output 5) |
| **Runtime** | **NONE structural** | `runtime_bindings` is one facet carrier; runtime depends on fingerprints/contracts (`UCOS-MOD-001` Output 6) |
| **Validation** | INV-04 | *"Every facet is populated"* — zero-ambiguity probe |
| **Verification** | Construction guards | `facets.py:126-127`; `NucleusProfile` refusal of status-without-reason |
| **Certification** | `certification` facet + `Attestation` | `CEP-005` |
| **Replay** | **NEUTRAL** | Facet *set* is not in `universe.fingerprint()` (`CEP-MOD-002` Output 9 — measured). Facet *values* are, via `knowledge_digest` |

**Determination:** the only cardinality locks in the entire repository are two test assertions. That is correct design — `facets.py:9-11` states a 34th facet *"is a constitutional amendment,"* and a failing test is precisely how an amendment is forced to be deliberate rather than accidental.

---

## OUTPUT 6 — Facet Evolution Matrix

| Question (from the original 15) | Determination | Evidence |
|---|---|---|
| 1 · What is a Facet? | A mandatory question a subject answers about itself | §1.4 |
| 2 · Why does it exist? | *"an absent facet is a question with no answer and therefore an ambiguity the law forbids"* | `facets.py:4-6` |
| 3 · Is every Facet mandatory? | **YES in presence, NO in attestation** | `UCKP-ART-06`; `FacetStatus` |
| 4 · Can Facets evolve? | **YES** — question tier by amendment; vocabulary tier by registration | `facets.py:8-13` |
| 5 · Can new Facets be admitted? | **YES, tier-dependent.** Q-tier: amendment. Declaration tier: registration (open paths) | `facets.py:9-11`; `NucleusProfile` |
| 6 · Can Facets be deprecated? | **NO removal mechanism exists.** `Facet` has no deprecation state; `Vocabulary` has no removal | Measured — `vocabulary.py` exposes no delete. Consistent with `UCKP-ART-14` (append-only) |
| 7 · Can Facets be composed? | **YES** — by reference | `UPL/UDL/USL/UAL-02` Law of Foundation Reuse |
| 8 · Can Facets inherit? | **YES — legislated and measured** | §1.2; the 2→3→4→5 chain |
| 9 · Can Facets specialize? | **YES** — each layer specializes its inherited set with its own | §1.2 |
| 10 · Can Facets be discovered? | **YES** — dotted-path addressing; `UCKP-ART-08` | `conformance.py:299-330` |
| 11 · Can Facets be configured? | **YES** — via declaration documents, not code | `NucleusProfile` |
| 12 · Can Facets be versioned? | **Indirectly** — `LAW_VERSION`; no per-facet version | Measured absence |
| 13 · Can Facets be certified? | **YES** — `certification` facet carries `Attestation` | `ucko.py:116` |
| 14 · Can Facets be replayed? | **YES** — `replay` facet; values in `knowledge_digest` | `CEP-MOD-002` Output 9 |
| 15 · Can Facets exist without implementation? | **YES** — that is what `NOT_APPLICABLE` + rationale means | `conformance.py:275-283` |

### Unboundedness

| Capability | Determination |
|---|---|
| Zero facets | **NO** — `REQUIRED_FACETS` is non-empty by construction |
| One facet | **NO** — 33 declared; reduction is amendment |
| Unlimited facets | **YES at declaration tier** (open paths); **amendment-gated at question tier** |
| Unknown future facets | **YES** — measured: facet vocabulary admitted a future term, original unchanged |
| Dynamic / generated | **YES at declaration tier** — profiles are documents |
| Inherited | **YES** — §1.2, legislated |
| Composite | **YES** — dotted paths are hierarchical |
| Conditional / contextual | **YES** — `NOT_APPLICABLE` + rationale; `context` and six `*-context` facets |

---

## OUTPUT 7 — Facet Convergence Matrix

*"Can the six converge without modifying their constitutional meaning?"*

> **They have already converged. No convergence act is required, and none is permitted.**

| Requirement | Satisfied? | How |
|---|---|---|
| One model per subject class | **YES** | 3 subjects, 3 models, 0 overlap (Output 3) |
| Inheritance legislated, not inferred | **YES** | `UPL/UDL/USL/UAL-01` name the stack; `-02` mandates reuse by reference |
| Redefinition forbidden | **YES** | `-02`: *"any redefinition is void to the extent of conflict"* |
| Precedence rule exists | **YES** | `AUTHORITY_TIER_VOCABULARY` rank 0–3 |
| Projections derived, not restated | **YES** | Measured — all three derivations return True |
| Open extension without amendment | **YES** | Declaration tier; measured on the facet vocabulary |
| Frozen artifacts untouched | **YES** | Convergence requires no edit to PL-F1/DF-1/SF-2/AF-1 |

**Why no merge is possible or desirable:** merging F-3…F-6 into one set would erase the inheritance chain, which is the *content* of `UPL/UDL/USL/UAL-01`. Erasing it would redefine four frozen constitutions — void under each family's own `-02` law, and forbidden by `CMG-000001` LXXVI.6 (*"Expansion SHALL NOT be achieved by reinterpretation"*). **The mission's constraint — do not merge — coincides with what Repository Truth already forbids.**

---

## OUTPUT 8 — REUSE / EXTEND / CEP / CREATE Matrix

| # | Universality rule | Located owner | Disposition |
|---|---|---|---|
| 1 | Universal Facet Model | `UCKP-ART-06` + `engine/uckp/facets.py` | **REUSE** |
| 2 | Facet Projection Rules | `UCKP-ART-11`; derived projections (measured) | **REUSE** |
| 3 | Facet Specialization Rules | `UPL/UDL/USL/UAL-01` | **REUSE** |
| 4 | Facet Extension Rules | `facets.py:8-13` (amendment vs registration) | **REUSE** |
| 5 | Facet Composition Rules | `UPL/UDL/USL/UAL-02` Law of Foundation Reuse | **REUSE** |
| 6 | Facet Evolution Rules | `CEP-009` + Addendum B | **REUSE** |
| 7 | Facet Discovery Rules | `UCKP-ART-08`; dotted-path addressing | **REUSE** |
| 8 | Facet Registration Rules | `FacetDeclaration`; `VocabularyRegistry` | **REUSE** |
| 9 | Facet Runtime Rules | `UCKP-ART-10`; `runtime_bindings` | **REUSE** |
| 10 | Facet Certification Rules | `CEP-005`; `certification` facet + `Attestation` | **REUSE** |
| 11 | Facet deprecation/retirement | **No mechanism exists** | **PASS** — consistent with `UCKP-ART-14` append-only. Not a gap unless retirement is required, and Repository Truth nowhere requires it |
| 12 | Per-facet versioning | Absent; `LAW_VERSION` covers the set | **PASS** — no instrument requires per-facet versions |
| 13 | Facet-model crosswalk | `UPL/UDL/USL/UAL-01/02` | **REUSE** — the crosswalk B-1 alleged missing |

**All ten universality rules are ALREADY LEGISLATED. Disposition: REUSE ×10.**

**CEP count: 0. CREATE count: 0. EXTEND count: 0.**

Repository Truth proves **no constitutional absence** in the facet model. Under `UCKP-ART-18` and `CMG-000001` LXXVII.2(a), CREATE is unavailable, and no proposal is warranted.

---

## OUTPUT 9 — Remaining Constitutional Blockers

| # | Blocker | Status after UCFM-001 |
|---|---|---|
| **B-1** | Six parallel facet models | **WITHDRAWN** — compatible; inheritance legislated |
| **B-4** | UCFM-001 incomplete | **CLOSED** — this determination |
| **B-2** | Two vocabulary primitives (`engine/uckp/vocabulary.py` vs `platform/universal_pipeline/vocabulary.py`) | **OPEN — HIGH.** Unaffected by this determination. Same defect `canonical.py` cured for the digest primitive |
| **B-3** | Two `OwnershipRecord` classes, opposite rules | **OPEN — HIGH.** Likely scope-distinct, unproven |
| **B-5** | `verify_vocabulary_alignment` absent; `law` divergence live | **OPEN — MEDIUM.** Resolution authorized |
| **B-6** | Ownership 27.86% closed | **OPEN — MEDIUM.** Closure gap, not convergence |
| **B-7** | UKIP `Facet` closed in a Python `Enum` | **OPEN — LOW.** Already scoped as `CEP-MOD-002` H-02. Not a facet-model defect |

### Revised convergence score

| Axis | Before | After |
|---|---|---|
| **Facets** | NOT CONVERGED | **CONVERGED** |
| Others | unchanged | unchanged |

**Converged or layered-by-declaration: 11 / 14 = 78.6%** *(was 71.4%)*
**Genuine parallel declarations: 2** — Vocabulary, Ownership *(was 3)*
**Axes with no determinable canonical owner: 0** *(was 1)*

---

## OUTPUT 10 — Final Recommendation

**Do not act on the facet model.** It is complete, owned, legislated, projected, inherited, and measured. Every one of the ten universality rules is REUSE. Any proposal touching it would create a rival to a located owner, forbidden by `UCKP-ART-18`.

**Resolve B-2 and B-3 before Foundation Freeze.** Both are outside the facet model. Neither implicates a frozen artifact, which makes both tractable by additive crosswalk or consolidation onto the located owner.

**Proceed with `CEP-MOD-002` M-0a and M-0b.** Unchanged from the convergence determination, and now unblocked on the facet axis.

**Record the two cardinality tests as the amendment tripwire.** `test_layer_zero.py:214` and `test_ucko_graph_registry.py:113` are the only places the number 33 is load-bearing. They should be understood as constitutional instruments — a 34th facet must break them — not as brittle assertions to be relaxed.

---

## EXIT CRITERIA

### 1. Are the six facet models constitutionally compatible?

> # YES.

### 2. The single constitutional model they implement

> **The Universal Constitutional Facet Model** — one model, three tiers, over three subject classes:
>
> **Tier 1 · Question (closed, amended).** 33 facets, `UCKP-ART-06`. What every canonical object must answer. Growth is amendment, because a new question binds every object at once.
>
> **Tier 2 · Layer (inherited by reference).** Each architecture layer inherits one facet from every layer beneath it — the concern that layer's own `-01` law declares it to be — and adds its own. Measured: inherited 2→3→4→5, own 4→3→2→1, total invariant at 6. Governed by `UPL/UDL/USL/UAL-01` and the `-02` Laws of Foundation Reuse, under which redefinition is void.
>
> **Tier 3 · Declaration (open, path-addressed).** `FacetDeclaration` / `NucleusProfile`. How a subject answers a facet: `PRESENT` with evidence, or `NOT_APPLICABLE` with rationale. Never absent. Growth is registration.
>
> Classification decisions (F-2) are governed by their own 6-facet model over a distinct subject and compete with neither tier.

### 3. Repository Truth conflict

> **None.** Zero overlapping subjects, zero competing owners, zero parallel authority. The alleged missing crosswalk is `UPL/UDL/USL/UAL-01/02`.

### 4. May P0 continue toward Foundation Freeze?

> # YES — continue. Foundation Freeze itself remains GATED.
>
> **Continue:** the facet axis is closed. It was the critical blocker and the deepest substrate — ownership, relationships, certification, validation, lifecycle, security, governance and evolution are each a facet, and all now rest on a determined foundation.
>
> **Gated on:** **B-2** (two vocabulary primitives) and **B-3** (two `OwnershipRecord` classes). Neither touches a frozen artifact.
>
> **Not gating:** B-5, B-6, B-7 — proceed in parallel.
>
> **Foundation Freeze may be declared once B-2 and B-3 are resolved by crosswalk or consolidation onto their located owners. No CEP is required for either — both have a located canonical owner already.**

---

**Files modified: none. Repository Truth modified: none. Facet models created: none. Models merged, replaced, or redesigned: none. CEPs drafted: none.**

Repository Truth artifacts cited: 16. Source files inspected: 8. Live measurements executed: 3. Prior determinations reused without recomputation: 5. Prior blockers withdrawn on evidence: 1 (B-1).

Recorded at commit `00bd45f`. `AUTHORITY = NONE — DERIVED TRUTH`. Where this determination and a canonical owner differ, the canonical owner governs.

---

*End of UCFM-001-UNIVERSAL-CONSTITUTIONAL-FACET-MODEL-FINAL-DETERMINATION.md*
