# PHASE-UCF-007 — PROVIDER CATEGORY GOVERNANCE DETERMINATION

## Document Identity

| Field | Value |
|---|---|
| Determination | PHASE-UCF-007-PROVIDER-CATEGORY-GOVERNANCE-DETERMINATION |
| Mission | Determine constitutional ownership, governance boundary, and enforcement strategy for provider category exclusivity |
| Mode | Discovery and determination only. Zero implementation, zero invariants added, zero code/constitution changes. |
| Date | 2026-08-14 |
| HEAD | `1f869865`, working tree as recorded in `PHASE-UCF-006 § Current Truth`, unchanged by this document |

## Purpose

`PHASE-UCF-006` classified "no general invariant guards provider category exclusivity" as a **Required** gap, evidenced by `PHASE-UCF-005`'s real category-contamination defect. This determination asks the questions that must be answered *before* any such invariant could correctly be designed: who owns a category, what a provider may lawfully do with one, what "contamination" precisely means, and where enforcement constitutionally belongs.

## Scope

In scope: category ownership, authority, contamination boundaries, enforcement-layer selection, and the conceptual shape of a possible invariant. Out of scope, per explicit instruction: writing that invariant, changing `law.py` or `vocabulary.py`, adding tests, or mutating any registry or governance binding.

## Context

Tenth and eleventh determinations respectively in the Universal Completeness Foundation arc are `PHASE-UCF-005` (the provider that surfaced this gap by accident) and `PHASE-UCF-006` (the review that classified it). Neither is reopened here. This document treats both as settled fact and analyzes forward from them.

---

## Current Repository Truth

Re-confirmed, not assumed:

- `engine/uckp/law.py::GOVERNED_CATEGORIES` — a 34-member, open tuple (Article 2, Article 17).
- `engine/uckp/vocabulary.py::GOVERNED_CATEGORY_VOCABULARY` — the controlled vocabulary built from that tuple.
- Four providers registered: `engine.uckp.alignment`, `engine.uckp.capabilities`, `engine.uckp.constitution`, `engine.uckp.uga_projection`. 5,982 objects admitted, `discover()` failures `()`.
- Native (pre-`uga_projection`) category histogram, measured directly: `artifact=10, authority=17, capability=10, constraint=17, governance=20, identity=1, law=1, metadata=33, observation=13, principle=20, runtime=10, taxonomy=13, transition=15, validation=13` — 14 of 34 declared categories in active use.

---

## Evidence Reviewed

- `engine/uckp/law.py:208-223` — Articles 2 (Canonical Existence) and 3 (Zero Duplication), read in full.
- `engine/uckp/law.py:333-340` — Article 17 (Universal Compatibility): *"an unknown future category is admitted by registration, never by amendment."*
- `engine/uckp/vocabulary.py:333-340` — `GOVERNED_CATEGORY_VOCABULARY`'s construction: `Term(category, "shall exist exactly once as a UCKO") for category in ROOT_LAW.governed_categories` — every term's definition is the same boilerplate restatement of Article 2, not a category-specific rule.
- `engine/uckp/vocabulary.py:113-125` — `Vocabulary.extended_with()`: append-only; raises `LawViolation` **only** if the exact `term_id` already exists with a different definition. No check for two different `term_id`s with overlapping meaning.
- `engine/uckp/ucko.py` (`require_lawful()`): `vocabularies.require_term(GOVERNED_CATEGORY, self.taxonomy.category)` — confirmed by direct read to check **membership only** (is this a registered term), never **usage authorization** (is this provider allowed to use it).
- Direct measurement: the `taxonomy`-category population (13 native objects) consists of one canonical object *per vocabulary itself* (`uckp.authority-tier`, `uckp.facet`, `uckp.governed-category`, `uckp.knowledge-kind`, `uckp.lifecycle-stage`, and others) — the **vocabulary as a whole** is canonically represented once; **individual category values within it are not** separately minted as canonical, ownership-bearing objects.
- `grep -rn "extended_with\|\.extend(" engine/uckp/` — the only live call sites are internal to `assimilation.py` (widening vocabularies from discovered artifact statuses/programmes) and `validation.py`'s own probes (testing extensibility, not performing a real extension). No provider has ever registered a genuinely new `GOVERNED_CATEGORY` term.

---

## Category Ownership Discovery

**Where are categories defined?** `engine/uckp/law.py::GOVERNED_CATEGORIES`, a flat, open tuple — the single canonical declaration.

**Who owns category vocabulary?** `engine/uckp/vocabulary.py::GOVERNED_CATEGORY_VOCABULARY`, held inside a `VocabularyRegistry` instance built by `build_vocabulary_registry()`. This is a **registry entity** (the vocabulary is registered, versioned by append-only extension) whose **existence** is a canonical object (one UCKO per vocabulary, category=`taxonomy`) but whose **individual term values** are not.

**How are categories registered?** Two, structurally different mechanisms exist and must not be conflated:
1. *Declaring* a category as constitutionally governed — editing `GOVERNED_CATEGORIES` in `law.py` (a law amendment, Article 11-protected, not something a provider does).
2. *Registering a genuinely new term* into the vocabulary at runtime — `Vocabulary.extended_with()`, Article 17's "admitted by registration, never by amendment" path. This is theoretically available to any caller holding a `VocabularyRegistry`, but no provider has ever exercised it.

**Are categories canonical objects, taxonomy entries, provider metadata, or registry entities?** All four, at different grains, and this determination's central finding is that the grains are not equally governed:
- **Registry entity** — yes, the vocabulary itself, append-only, governed.
- **Canonical object** — yes, but only for the vocabulary's existence as a whole, not for each term.
- **Taxonomy entry** — yes, each `GOVERNED_CATEGORY` value is a `Term` inside that vocabulary, checked for membership on every object.
- **Provider metadata** — yes, in the sense that *which* categories a given provider actually populates is knowable only by reading that provider's own minting code (or, as `PHASE-UCF-005` demonstrated, by running the test suite against it) — **there is no governance record of "provider X populates categories {a, b, c}" anywhere in the repository.** Ownership of a category's *population* (as opposed to the category's *membership in the vocabulary*) is currently a fact that exists only in source code, nowhere declared.

---

## Authority Analysis

| Can a provider... | Classification | Evidence |
|---|---|---|
| **A. Create new categories?** | **Mechanically allowed, ungated** | `Vocabulary.extended_with()` exists and would succeed for a genuinely new `term_id`; no certification, review, or approval step wraps it. Never exercised in practice (Evidence, above). |
| **B. Reuse existing categories?** | **Allowed, unconditionally** | `require_term()` checks only vocabulary membership. This is the exact permission `PHASE-UCF-005`'s first draft exercised when it selected `"metadata"` — a lawful act under the current model, and the direct cause of the contamination it produced. |
| **C. Extend existing categories?** | **Not a distinct operation in the current model** | `GOVERNED_CATEGORY` terms carry no `successors` (every term: `rank=0, successors=()`) — categories are flat, not a hierarchy with a declared extension/transition semantic the way `LIFECYCLE_STAGE` terms are. "Extending" a category collapses into "reusing" it (B); there is no separate mechanism to analyze. |
| **D. Claim ownership of existing categories?** | **Missing entirely — neither allowed nor forbidden, because the concept does not exist** | No field, API, or governance record supports declaring "this category is mine, exclusively." This is not a permission gap; it is a *conceptual* gap — the authority model has no vocabulary for the question. |

---

## Contamination Boundary Analysis

**Definition, precise:** category contamination occurs when a `GOVERNED_CATEGORY` value that one provider's design relies on for a closed-population property (a specific count, an exhaustiveness claim, an implicit one-owner assumption) is populated by a second, unrelated provider, without either provider's code or any governance record ever declaring the two are sharing the category intentionally.

| Case | Analysis | Governance outcome |
|---|---|---|
| **1. Provider emits a category another authority already exclusively populates** | The demonstrated case — `PHASE-UCF-005`'s first attempt used `"metadata"`, already exclusively populated 33-to-1 with `Facet` members by `capabilities.py`. Currently detectable only by incidental test coverage, not by any general mechanism. | **Real, evidenced defect class. Governance gap — requires resolution.** |
| **2. Provider creates a duplicate semantic category** (a new `term_id` meaning the same thing as an existing one, e.g. registering `"config"` alongside the existing `"metadata"` or `"policy"`) | Structurally possible under Article 17's registration path; `extended_with()`'s only check is exact-`term_id` collision, never semantic overlap. **No instance of this has occurred** — no provider has ever registered a new category term at all. | **Plausible, ungated, but not evidenced.** Distinguished from Case 1 precisely because Case 1 happened and this has not. |
| **3. Provider extends a canonical category** | Per Authority Analysis (C), this is not a distinct operation the current model supports — categories have no extension/successor semantic. This case is **not applicable** as stated; any attempt to "extend" a category is, mechanically, Case 1 (reuse) or Case 4 (new registration), never a third thing. | **Not applicable under current architecture.** |
| **4. Provider creates a new, independent category** | The one case Article 17 was explicitly designed for, and the clean case: a genuinely new category value cannot collide with existing usage by definition of being new. No contamination risk, *provided* Case 2's semantic-duplication risk is separately addressed (a new category can still be a duplicate-in-meaning of an old one even though it is not a duplicate-in-`term_id`). | **Structurally safe for exclusivity; not safe for semantic duplication (see Case 2).** |

---

## Enforcement Ownership Analysis

| Candidate | Authority correctness | Dependency impact | Duplication risk | Architectural alignment | Verdict |
|---|---|---|---|---|---|
| **A. UCKP invariant layer** | High — category membership, semantic identity, and duplication are already this layer's domain (`UCKP-INV-01` knowledge-once, `UCKP-INV-03` zero-duplication govern the immediately adjacent concerns) | None — self-contained inside `engine.uckp`, exactly where the three `PHASE-UCF-005` defects were already caught (two of three by this same layer) | None — extends an existing invariant family rather than creating a parallel one | High — matches Article 6's own precedent (facet-completeness as a structural, not conventional, property) | **Correct primary owner** |
| **B. Universal Governance Architecture (UGA)** | Low — `existence_resolution` bounds UGA's authority to repository-wide existence bookkeeping; UGA's own schema has no concept of `taxonomy.category` at all | High — would require UGA to read into UCKP's internal facet model, a dependency direction `existence_resolution` does not currently declare and this determination does not recommend inventing | Would create a second place category logic is checked | Low — crosses the exact boundary `existence_resolution` drew deliberately | **Not the correct owner** |
| **C. Registry validation (`engine/uckp/registry.py` admission)** | Medium — admission-time is a plausible *complementary* moment (refuse before entry, not merely report after), but the registry's current admission logic governs identity collision, not facet content | Low — still self-contained in `engine.uckp` | Low, if implemented as a call into the same invariant logic rather than a parallel check | Medium — plausible future refinement, not required for correctness since `validate_universe()` already gates certification | **Viable complement, not required now** |
| **D. Provider certification** | Low today — no such mechanism exists (`PHASE-UCF-006`'s own finding, re-confirmed: zero certification requirement on any provider) | Building one is new infrastructure, not reuse | Would risk becoming a second gate duplicating what an invariant already checks | Low — conflicts with Reuse Before Create if built before the invariant layer is used first | **Not the correct primary owner; a future option only if the invariant layer proves insufficient** |
| **E. Multiple coordinated layers** | N/A | N/A | N/A | Accurate as a long-term description, but not as an immediate design instruction | **Not equally weighted — A is primary, C is an optional future complement, B and D are not currently justified** |

**Selected ownership model: the UCKP invariant layer (A) is the correct constitutional owner of provider category exclusivity**, on the same authority basis Articles 2 and 3 already establish for semantic-identity and duplication generally.

---

## Invariant Determination

Conceptual only — no code is proposed.

**`PROVIDER_CATEGORY_OWNERSHIP_INTEGRITY`**

- **Should it exist?** Yes. The gap it would close is evidenced, not speculative — `PHASE-UCF-005` produced a real instance of exactly the failure this invariant would catch generally, and the only reason it was caught at all was an unrelated test's incidental assertion.
- **Who owns it?** `engine/uckp/validation.py`'s `ConstitutionalValidator`, as an addition to the existing `UCKP-INV-01..17` probe family — the same home as every structurally adjacent invariant.
- **What does it validate, conceptually?** For every `GOVERNED_CATEGORY` value actually populated by more than one distinct `discovery.provider`, either: (a) exactly one provider populates it, or (b) more than one does, but a governance record explicitly declares that sharing as intentional and reconciled — mirroring the precedent `certification_authority_resolution` and `existence_resolution` already set for declaring intentional plurality elsewhere in this exact repository.
- **What evidence does it require?** The `discovery.provider` field every UCKO already carries (confirmed present and populated on every object minted this arc), cross-referenced against `taxonomy.category` — a provider→category population map, the same shape this determination computed by hand under Current Repository Truth.
- **What does failure mean?** A category is populated by more than one provider with no declared, reconciling exception — the exact situation `PHASE-UCF-005`'s first draft created and self-corrected before commit. Failure would mean a future provider is about to repeat that mistake, or has already repeated it undetected.

This determination does not decide whether the invariant should refuse (fail-closed, blocking) or merely report (advisory) on first detection — that is an implementation decision appropriately deferred to whoever writes it, informed by which existing `UCKP-INV` probes are blocking versus advisory (a distinction this determination did not need to resolve to answer the ownership question asked).

---

## Provider Federation Governance Model

| Rule | Tier | Basis |
|---|---|---|
| Reuse an existing category whose semantic fits before registering a new one | **Mandatory** | Direct application of Reuse Before Create (Article 18, already repository-wide) to category selection specifically |
| Never populate a category a different provider already exclusively populates, without a declared exception | **Mandatory** | The exact rule `PROVIDER_CATEGORY_OWNERSHIP_INTEGRITY` would enforce; stated here as the governance intent, not the code |
| Never register a category whose meaning duplicates an existing term under a different `term_id` | **Mandatory** | Article 3 (Zero Duplication), applied to vocabulary terms rather than objects — currently ungated (Case 2), but the *rule* already follows from existing law even though no *check* exists yet |
| Declare, in a provider module's own docstring, which categories it emits | **Optional** | Cheap, immediately actionable, zero risk — a documentation convention this determination recommends but does not mandate, since it substitutes for, rather than replaces, an eventual invariant |
| A formal category-ownership `*_resolution` governance binding | **Future** | Should follow, not precede, the invariant's existence — a binding that records enforced fact is stronger than one that records aspiration, matching this arc's own repeated sequencing (bind after building, not before) |
| Provider certification as a general onboarding gate | **Future** | Already `Deferred` per `PHASE-UCF-006`; this determination finds no new evidence to elevate it |

---

## Dependency Impact

Locating enforcement at the UCKP invariant layer (A) introduces no new cross-package dependency: `ConstitutionalValidator` already reads every provider's minted objects to run `UCKP-INV-01..17`; a new probe reading `taxonomy.category` and `discovery.provider` from the same already-collected object set adds no new import, no new data source, and no new coupling. This is the same reasoning `PHASE-UCF-006`'s Dependency Analysis applied to `uga_projection.py` itself.

## Certification Impact

None. Neither the invariant (conceptual, not built) nor this determination changes any certification surface. `RepositoryCertificate` and the twelve prior surfaces in `certification_authority_resolution` are unaffected.

---

## Gap Reclassification

Reviewing `PHASE-UCF-006`'s gap table against this determination's findings:

| Gap | UCF-006 classification | This determination | Change |
|---|---|---|---|
| Provider category exclusivity has no general invariant | Required | **Required — confirmed and sharpened.** The gap is now understood as two-layered: no invariant, *and* no concept of declared category ownership for such an invariant to check against. Both are needed together; neither alone would close the gap this determination analyzed. | Refined, not downgraded |
| Provider certification/pre-flight checklist | Deferred | **Deferred — confirmed.** This determination's own finding (Article 17's registration path is equally ungated) reinforces rather than changes the reasoning. | Unchanged |
| Onboarding documentation | Deferred | **Deferred — confirmed.** Unrelated to this determination's findings. | Unchanged |
| Evolution History cross-domain view | Deferred | **Deferred — confirmed.** Not touched by this determination, correctly not revisited. | Unchanged |
| No consumers of the expanded UCKP population | Observational | **Observational — confirmed.** Unrelated. | Unchanged |
| No performance data past current scale | Observational | **Observational — confirmed.** Unrelated. | Unchanged |
| **New: semantic-duplicate category registration (Case 2) is ungated** | *(not previously named)* | **Deferred.** Real and plausible, but — unlike the exclusivity gap — no evidenced instance exists; no provider has ever registered a new category term. Classified below Required deliberately, to keep severity tied to evidence rather than plausibility alone. | New finding |
| **New: new-category registration itself has no certification/review gate** | *(not previously named)* | **Observational.** The mechanism (`extended_with()`) exists and is structurally sound (Article 17); it has simply never been exercised, so there is no evidence of harm to weigh. | New finding |

---

## Final Determination

Provider category exclusivity is a real, evidenced governance gap whose correct owner is the UCKP invariant layer, not UGA, registry-admission logic, or a new provider-certification mechanism. The gap has two parts — a missing invariant and a missing concept of declared category ownership — and both must exist together for either to be meaningful. A conceptual invariant, `PROVIDER_CATEGORY_OWNERSHIP_INTEGRITY`, is specified at the level of what it would check, who would own it, and what evidence it would use, but is **not implemented, coded, or bound** in this document, per explicit instruction. Two related but lower-severity gaps (semantic-duplicate category registration; the absence of any gate on new-category registration generally) were newly surfaced and classified Deferred and Observational respectively, on the evidentiary distinction that neither has ever actually occurred, unlike the exclusivity gap this arc has now demonstrated twice (once as a defect, once as this determination's own subject).

---

Stopping after PHASE-UCF-007, as instructed.
