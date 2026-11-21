# PHASE-UCF-008 — PROVIDER CATEGORY OWNERSHIP MODEL DETERMINATION

## Document Identity

| Field | Value |
|---|---|
| Determination | PHASE-UCF-008-PROVIDER-CATEGORY-OWNERSHIP-MODEL-DETERMINATION |
| Mission | Determine the canonical ownership model required to support provider category integrity, before `PROVIDER_CATEGORY_OWNERSHIP_INTEGRITY` (conceptually specified in `PHASE-UCF-007`) is designed as code |
| Mode | Determination only. Zero code, zero test changes, zero registry changes, zero invariant implementation, zero constitution changes. |
| Date | 2026-08-14 |
| HEAD | `1f869865`, working tree as recorded in `PHASE-UCF-007 § Current Repository Truth`, unchanged by this document |

## Purpose

`PHASE-UCF-007` determined that provider category exclusivity is a real, evidenced governance gap, that the UCKP invariant layer is its correct enforcement owner, and sketched a conceptual invariant — `PROVIDER_CATEGORY_OWNERSHIP_INTEGRITY` — without designing it. It also found the gap is two-layered: no invariant exists, *and* no concept of declared category ownership exists for such an invariant to check against. This document closes the second layer's *design* question only: what does "a provider owns a category" mean, how should that fact be represented, and where should it live — so that whoever eventually writes the invariant has a settled representation to check against rather than a blank page.

## Scope

In scope: category ownership representation, ownership semantics (owner vs. contributor vs. producer vs. provider vs. registrar vs. authority), category lifecycle, the future provider federation contract, and selection among binding models. Out of scope, per explicit instruction: writing `PROVIDER_CATEGORY_OWNERSHIP_INTEGRITY` itself, editing `law.py`, `vocabulary.py`, or any registry, adding tests, or mutating any governance binding.

## Context

Twelfth determination in the Universal Completeness Foundation arc, immediately following `PHASE-UCF-007` (which is treated as settled and not reopened) and, through it, `PHASE-UCF-005`/`006` (the provider integration that surfaced the gap and the assimilation review that classified it). This document analyzes forward from all three; none of their findings is re-derived from scratch where a direct citation suffices.

---

## Current Repository Truth

Re-confirmed fresh in this pass, not cited from prior turns:

| Check | Result |
|---|---|
| `verify_binding(constitutional-authority-alignment.json)` | `()` — PASS |
| `build_universe().registry.discover()` | `providers_found=('engine.uckp.alignment', 'engine.uckp.capabilities', 'engine.uckp.constitution', 'engine.uckp.uga_projection')`, `objects_admitted=5982`, `failures=()` |
| `validate_universe(build_universe())` (17 UCKP-INV) | `verdict='certified'`, `certified=True` |
| `00-BOOK/tools/ukb.py enforce --pre` | PASS — 1233 registered, 26 unregistered-eligible (pre-existing, unrelated to this document — the `PHASE-UCF-*` and other determination `.md` files awaiting `git add`), 0 gated |
| `00-BOOK/tools/ukb.py validate` | PASS — 1233 artifacts, referential integrity OK |

Identical to `PHASE-UCF-007`'s own baseline — no drift, no corruption, no change introduced by producing that document or by the exploration performed for this one.

Also re-confirmed by direct read, not assumed:

- `engine/uckp/values.py:214-233` — `Ownership(owner: str, stewards: tuple[str, ...] = ())`, Facet 7. A per-object accountability fact: exactly one `owner`, plus an open set of `stewards`.
- `engine/uckp/values.py:153-183` — `AuthorityBinding(tier: str, derives_from: str, instrument: str = "")`, Facet 5. A per-object *derivation* fact, explicitly single-parent by design ("Exactly one parent is permitted: two parents is two authorities over one object").
- `engine/uckp/values.py:604-628` — `DiscoveryDescriptor(discoverable, self_describing, provider: str = "", keywords)`, Facet 21. `provider` is a free-text string naming the module that discovered/minted the object — a *discovery* fact, not an accountability or authority fact.
- `engine/uckp/vocabulary.py:52-66` — `Term(term_id, definition, rank=0, successors=(), symmetric=False)`. No `owner` field exists on `Term` today, confirmed by full read of the dataclass.
- `engine/uckp/law.py:424-461` — `GOVERNED_CATEGORIES`, a flat 35-member tuple including `"relationship"`. Per `PHASE-UCF-007`'s own directly-measured native histogram (`artifact=10, authority=17, capability=10, constraint=17, governance=20, identity=1, law=1, metadata=33, observation=13, principle=20, runtime=10, taxonomy=13, transition=15, validation=13`), `"relationship"` is **not** among the 14 active categories — it is declared, governed, and currently at zero population.
- `engine/uckp/vocabulary.py:306-325` — `RELATIONSHIP_CLASS_VOCABULARY` already registers a term `"ownership"`, definition `"who is accountable"`, live and in use today by `graph.py`'s own ownership edge.
- `engine/uckp/graph.py:83-88` — `derive_edges()` already emits `UniversalKnowledgeEdge(source, obj.ownership.owner, "owns", "ownership", scope=STATE_SCOPE)` for every object whose `ownership.owner` is set — i.e. an "owns" relationship, classified `"ownership"`, is already a first-class, executable edge in the knowledge graph today, at the per-object grain.
- `engine/uckp/registry.py:233-234` and `engine/uckp/intelligence.py:336-357` — `by_owner()` and ownership-concentration risk reasoning both operate on `obj.ownership.owner`, confirming every existing ownership *query* in the codebase is wired to the per-object facet, none to a per-category concept.
- `engine/uckp/governance.py:315-329` — `_who_owns()` answers accountability under `UCKP-ART-06` (Facet Completeness), returning `obj.ownership.owner` — again per-object, and grounded in the facet-completeness article, not an authority or reuse article.
- `00-BOOK/DATA/constitutional-authority-alignment.json` — `existence_resolution`, `lifecycle_resolution`, `certification_authority_resolution` sections, each following an identical shape: a `model.type` (e.g. `MULTIPLE_INDEPENDENT_AUTHORITIES`), a list of named authorities/surfaces/axes, each with `home`, `role`, and `bounded_question`. Read in full; this is a proven, three-times-repeated repository pattern for exactly the question class this document is analyzing — "who has undisputed authority over which bounded question, and how is that declared rather than assumed."

---

## Evidence Reviewed

- `engine/uckp/values.py:153-233` (`AuthorityBinding`, `Ownership`) — full read.
- `engine/uckp/vocabulary.py:1-140, 240-330` (`Term`, `Vocabulary`, `RELATIONSHIP_CLASS_VOCABULARY`, `AUTHORITY_TIER_VOCABULARY`) — full read.
- `engine/uckp/law.py:1-24, 195-400, 420-461` (module docstring, `UCKP_ARTICLES`, `GOVERNED_CATEGORIES`) — full read of Articles 1–20.
- `engine/uckp/facets.py` — full read; `Facet.OWNERSHIP` ("Who is accountable for it?") confirmed distinct from `Facet.AUTHORITY` ("By what authority does it exist, and from whom is that derived?") and `Facet.DISCOVERY` ("How is it found without anyone listing it?") — three separate questions, three separate facets, by constitutional design (Article 6).
- `engine/uckp/graph.py:1-100` — `derive_edges()`, full read of every edge type it emits.
- `engine/uckp/registry.py:220-245`, `engine/uckp/intelligence.py:330-360`, `engine/uckp/governance.py:300-335` — every live consumer of `Ownership` in the codebase, located by `grep -rn "owner\|Owner\|OWNERSHIP"` across `engine/uckp/*.py` (excluding tests) and read at each hit.
- `engine/uckp/constitution.py:43-44` — `CONSTITUTIONAL_OWNER = "ucos-constitutional-authority"`, the sole owner value used for every native canonical object (law, capabilities, alignment binding) — confirmed a single named accountable entity, not an entity-per-category.
- `00-BOOK/DATA/constitutional-authority-alignment.json` — `existence_resolution`, `lifecycle_resolution`, `certification_authority_resolution` — full read of each section's shape.
- `grep -rn "registrar\|Registrar\|contributor\|Contributor\|producer\|Producer\b" engine/uckp/*.py` → zero results. None of these three terms is defined, used, or modeled anywhere in the engine today.
- `engine/uckp/values.py:186-211` (`ProvenanceStep`) and `engine/uckp/ucko.py:185-250` — confirmed an object-minting actor is captured (`actor=owner` in every `ProvenanceStep`), but no equivalent actor capture exists for the act of *registering a vocabulary term* (`Vocabulary.extended_with()` takes no actor argument at all — confirmed by its signature, `engine/uckp/vocabulary.py:113-125`).

---

## Existing Ownership Pattern Analysis

Two, and only two, ownership-shaped patterns exist in the repository today; both were located by direct search, not assumed to exist:

| Pattern | Grain | Shape | Home | Used for |
|---|---|---|---|---|
| **Per-object accountability** | One UCKO | `Ownership(owner: str, stewards: tuple)`, Facet 7 | `engine/uckp/values.py` | Every canonical object minted by every provider — capabilities (`capabilities.py:86,252`), the alignment binding (`alignment.py:361`), the constitution itself (`constitution.py:108`), all set `owner=CONSTITUTIONAL_OWNER` |
| **Per-bounded-question authority declaration** | A named question, not an object | `model.type` + list of `{id, home, role, bounded_question}` entries | `00-BOOK/DATA/constitutional-authority-alignment.json` `*_resolution` sections | `existence_resolution` (three authorities, each answering a different "what exists" question), `lifecycle_resolution` (two orthogonal axes), `certification_authority_resolution` (plural certification surfaces) |

Searched and confirmed **absent** as distinct concepts:

- **Artifact ownership** — an artifact is a UCKO like any other; it uses the same per-object `Ownership` facet, nothing artifact-specific.
- **Provider ownership** — there is no "Provider" object at all. A provider is a Python module exposing `ucko_objects()`/`UCKO_OBJECTS`; the only trace it leaves on an object is `discovery.provider` (Facet 21, a free-text string), which answers "how was this found," not "who is accountable for it" or "who is authorized to populate this category."
- **Universe ownership / authority ownership** — these are exactly what `existence_resolution` and `AuthorityBinding.derives_from` already model, at two different grains (repository-wide bounded questions vs. per-object single-parent lineage).
- **Capability ownership** — reuses the per-object pattern; no capability-specific ownership concept exists.

**Determination:** category ownership fits neither existing pattern cleanly at its native grain. It is not "one UCKO's accountable owner" (a category is not, today, a UCKO — per `PHASE-UCF-007`'s own finding, only the *vocabulary as a whole* is canonically minted, not each term within it), and it is not quite "orthogonal bounded questions with no competition" either, because category exclusivity is precisely about the possibility of *illegitimate* competition over the *same* bounded question (two providers populating the same category). The second pattern's *mechanism* — a named ledger entry per bounded fact, declaring the authority(ies) and their `bounded_question` — is nonetheless the closer fit and the only one of the two with a track record of resolving exactly this class of question (see Binding Model Determination).

---

## Category Ownership Model Analysis

Each of the mission's five candidate representations, evaluated on ownership authority, lifecycle implications, duplication risk, and canonical source of truth:

**A. Property of the Category object.** There is no standalone Category object to attach a property to — a category is a `Term` (`term_id, definition, rank, successors, symmetric`) inside the shared `Vocabulary`/`Term` dataclasses used by **nine** vocabularies (`KNOWLEDGE_KIND`, `AUTHORITY_TIER`, `LIFECYCLE_STAGE`, `RELATION_TYPE`, `RELATIONSHIP_CLASS`, `FACET_VOCABULARY`, `GOVERNED_CATEGORY`, `NON_AUTHORITATIVE_CATEGORY`, plus the evolution-stage vocabulary contributed at `build_universe()` time), not one built for `GOVERNED_CATEGORY` alone. Adding an `owner` field to `Term` changes a Layer Zero primitive shared by all nine, and `Vocabulary.extended_with()`'s append-only law forbids redefining an already-registered term (`existing != term` raises `LawViolation`) — so every one of the ~35 already-registered `GOVERNED_CATEGORY` terms would need to be re-authored in the same change to carry the new field, a non-additive, cross-cutting edit far outside this gap's actual scope. **Canonical source of truth would be correct in principle (the term itself), but the blast radius is wrong for the size of the problem.**

**B. Property of the Provider object.** There is no Provider object either (Existing Ownership Pattern Analysis, above). Inventing one purely to hold a self-declared `owned_categories` list would let two providers each self-declare the same category with nothing to arbitrate the collision — the exact failure `PHASE-UCF-005` produced. Self-declaration can be an *input* to a binding; it cannot *be* the binding, because it has no mechanism to detect or refuse a conflicting second declaration. **Duplication risk: high, by construction — this option cannot prevent the failure it exists to prevent.**

**C. Relationship object — `ProviderCategoryOwnershipBinding`.** Structurally the correct *shape*: a fact that binds two identities (a provider, a category) is a relationship, not a property of either side alone, exactly mirroring how `AuthorityBinding.derives_from` already models a single-parent binding and how `graph.py` already treats "owns" as a first-class, executable edge (`relationship_class="ownership"`, already a registered `RELATIONSHIP_CLASS` term — "who is accountable"). A category-ownership binding minted as a full UCKO would gain a lifecycle, evidence chain, provenance, and certification surface for free, the same way every other governed fact in this system does. It would also cost nothing extra to classify: `"relationship"` is already a `GOVERNED_CATEGORY` value (§ Current Repository Truth), declared and unused — reusing it satisfies Article 18 (Reuse Before Create) with zero new vocabulary registration. **This is the correct eventual shape, but is new infrastructure not required to unblock the invariant `PHASE-UCF-007` specified.**

**D. Separate governance artifact.** Not a new mechanism — the `*_resolution` ledger already in `constitutional-authority-alignment.json` is precisely this, proven three times over for `existence_resolution`, `lifecycle_resolution`, and `certification_authority_resolution`. A `category_ownership_resolution` section, same shape, is additive, requires no schema change to any Layer Zero primitive, and is immediately auditable through the same tooling that already reads the other three sections.

**E. Existing concept reused from another universe.** Not a fourth option distinct from D — D **is** the existing concept, reused. No search of `platform/repository_intelligence/` or UGA's own registries surfaced a *different* ownership pattern worth reusing instead; the `*_resolution` ledger is UCOS's own general-purpose answer to "which bounded question does which authority hold," already applied to existence, lifecycle, and certification. Category ownership is the same shape of question asked about a fourth axis.

**Finding:** A and B are disqualified — A for blast radius on a shared primitive well beyond this gap's scope, B for structurally being unable to arbitrate the exact collision it needs to prevent. C is the correct long-run representation but is new infrastructure. D is C's own proven precedent-pattern, reusable today with zero new code. See Binding Model Determination for the selection between C and D as *this* determination's answer.

---

## Ownership Semantic Model

Of the six terms named in the mission, only three are currently modeled at all, and they answer three different questions that must not collapse into one:

| Term | Currently modeled? | What it answers | Evidence |
|---|---|---|---|
| **Owner** | Yes — `Ownership.owner` | Who is accountable (Facet 7) | `values.py:214-233`, `governance.py::_who_owns()` |
| **Authority** | Yes — `AuthorityBinding.derives_from` | From whom the right to exist is derived, strictly single-parent (Facet 5) | `values.py:153-183` |
| **Provider** | Yes — `DiscoveryDescriptor.provider` | How the object was found / which module minted it (Facet 21) | `values.py:604-628` |
| **Contributor** | No | — | zero hits, `grep -rn "[Cc]ontributor" engine/uckp/*.py` |
| **Producer** | No | — | zero hits, `grep -rn "[Pp]roducer\b" engine/uckp/*.py` |
| **Registrar** | No | — | zero hits; the nearest structural analog, whoever calls `Vocabulary.extended_with()`, captures no actor identity at all today (unlike object-minting, which always records `actor` in a `ProvenanceStep`) |

**Owner vs. Authority vs. Provider, held apart deliberately:** an object's `owner` is who answers for it; its `authority.derives_from` is the single parent it is lawfully descended from; its `discovery.provider` is the module that happened to mint it. `PHASE-UCF-005`'s own contamination defect is, in this vocabulary, precisely a *Provider* fact (which module populated a category) being treated as if it settled an *Owner* fact (who is entitled to) with no check in between — the two were never actually distinct in the current model because only one of the three (Provider) is even tracked at category grain.

**Contributor, Producer, Registrar — deliberately not defined here.** Consistent with `PHASE-UCF-007`'s own restraint ("no new pattern unless existing patterns are insufficient") and this repository's repeated preference for evidence over speculation, this determination does not invent formal definitions for three terms nothing in the codebase currently needs. It states only the minimum needed to avoid future collapse:

- **Producer**, if it comes to be used, should mean *populates* (mints objects into) a category — this is what `PHASE-UCF-007` already called "population" and what `discovery.provider`, cross-referenced against `taxonomy.category`, already measures without any new field.
- **Owner**, applied to a category, should mean *holds declared, exclusive-unless-reconciled authority* over that category — the accountable party a `PROVIDER_CATEGORY_OWNERSHIP_INTEGRITY` violation would be reported against.
- **Registrar** names a real, currently-uncaptured gap (no actor identity is recorded when a vocabulary term is registered) but has no evidenced harm, since no provider has ever exercised `extended_with()` (`PHASE-UCF-007 § Evidence Reviewed`). Named here as an Observational finding (§ Gap Reclassification), not designed.
- **Contributor** and **Delegate** (the mission's federation-contract term, § below) most plausibly map onto the already-existing `Ownership.stewards` field — a category owner's `stewards` would be its delegated co-producers — but this is offered as an interpretation for a future implementer to confirm, not a settled fact, since `stewards` was designed for per-object accountability and has never been used at category grain.

---

## Lifecycle Determination

| Stage | Determination | Basis |
|---|---|---|
| **Creation** | Any caller holding a `VocabularyRegistry` may call `extended_with()`; mechanically ungated, no certification step. Re-confirmed, not changed, from `PHASE-UCF-007 § Authority Analysis A`. | `vocabulary.py:113-125` |
| **Registration** | Not a separate step from creation today — Article 17 collapses "create" and "register" into the single `extended_with()` call, unlike object minting, where creation (construction) and registration (`discover()` admission) are two distinct gates. | `law.py` Article 17; `vocabulary.py:113-125` |
| **Ownership establishment** | **Does not exist as a moment in the current model.** There is no step, anywhere, where "category X is now owned by provider Y" becomes true. This is the exact absence `PHASE-UCF-007` named and this document has now modeled a representation for (§ Binding Model Determination), without implementing the moment itself. | New finding, this determination |
| **Transfer** | Undefined; no mechanism exists or is proposed here. Given `extended_with()`'s no-redefinition law and Article 12 (Immutable Constitutional State — "no previous state ever changes"), a transfer could only ever be modeled as a new, appended fact (a new ledger entry or a new binding UCKO superseding the old one), never as a mutation of the original declaration — consistent with how every other constitutional fact in this system changes. | `vocabulary.py:113-125`, `law.py` Article 12 |
| **Retirement** | `GOVERNED_CATEGORY` terms all carry `rank=0, successors=()` (re-confirmed from `PHASE-UCF-007`'s direct read) — flat, with no declared retirement path, unlike `LIFECYCLE_STAGE` terms, which use `successors` for exactly this purpose. Retirement would need either the same successor-graph treatment or a governance-record declaration; neither exists today. | `vocabulary.py:253-277` (contrast with `GOVERNED_CATEGORY`'s flat terms) |
| **Extension** | Not a distinct operation under the current model — re-confirmed unchanged from `PHASE-UCF-007 § Authority Analysis C`: "extending" a category collapses into reusing it, since categories carry no successor semantic. | `PHASE-UCF-007`, re-confirmed here |

---

## Provider Federation Contract

The mission asks whether a future provider must declare categories consumed, produced, owned, and delegated, and which are mandatory versus optional.

**Current baseline:** zero declaration of any kind exists today. `PHASE-UCF-006` confirmed "any module exposing `ucko_objects()`/`UCKO_OBJECTS` under `engine.uckp` is auto-admitted with no review gate beyond the invariants it happens to satisfy or violate." Mandating four new declarations on all four existing providers now, ahead of any invariant that would consume them, would be exactly the kind of speculative infrastructure `PHASE-UCF-006`'s own Recommendation 2 warned against building ahead of evidence.

**Determination, by declaration:**

| Declaration | Tier now | Reasoning |
|---|---|---|
| **Categories produced** | **Optional recommendation now; becomes the evidentiary input `PROVIDER_CATEGORY_OWNERSHIP_INTEGRITY` needs once built** | Already fully derivable without any new declaration — `discovery.provider` cross-referenced against `taxonomy.category` on already-minted objects is exactly the population map `PHASE-UCF-007` computed by hand. A docstring convention (as `PHASE-UCF-007` already recommended, Optional) would make it human-legible sooner, but nothing depends on it being declared rather than derived |
| **Categories owned** | **Deferred — the fact this document's binding model exists to eventually hold, not to mandate as a provider self-declaration** | Per Category Ownership Model Analysis, self-declared ownership (Option B) cannot arbitrate collisions on its own; "owned" must be adjudicated through the binding (§ Binding Model Determination), not simply asserted by the provider whose interest is at stake |
| **Categories consumed** | **Observational — no identified invariant dependency** | No evidence any provider currently reads another provider's categories as an input; `PHASE-UCF-006` confirmed zero cross-package consumers of the UCKP population generally. Naming this now would be speculative |
| **Categories delegated** | **Observational — no identified invariant dependency; plausibly maps to existing `Ownership.stewards`, not a new field** | See Ownership Semantic Model's Contributor/Delegate note; not settled, not required |

**Mandatory vs. optional, overall determination:** nothing is made mandatory by this document. Mandating a declaration with no invariant yet built to enforce it produces dead weight (a rule nobody checks); building the enforcement invariant before the representation it checks is designed produces the exact chicken-and-egg `PHASE-UCF-007` avoided by stopping before implementation. The correct order, matching this arc's own repeated sequencing (bind, then build against the binding — `PHASE-UCF-004` before `PHASE-UCF-005`), is: this document settles the representation; a future phase populates the binding with the current provider→category facts; only then does mandating a producer-facing declaration become load-bearing.

---

## Binding Model Determination

The mission's four options map directly onto Category Ownership Model Analysis's A–D:

| Option | Canonicality | Historical evolution fit | Auditability | Federation support | Multi-provider future |
|---|---|---|---|---|---|
| **1. Category directly contains owner** (= A) | Correct in principle, but requires mutating a nine-vocabulary shared primitive and re-authoring every already-registered `GOVERNED_CATEGORY` term to satisfy `extended_with()`'s no-redefinition law | Poor — no precedent in this arc for a Layer Zero primitive change this size in service of one narrow gap | High, if built | N/A — cost dominates | N/A — cost dominates |
| **2. Provider declares ownership** (= B) | Low — self-assertion has no arbitration; cannot prevent the exact collision it exists to catch | Poor — no precedent for a self-declared, unarbitrated authority claim anywhere in this repository | Low — a claim with no counter-check is not really audited | Poor — two providers can each declare the same category with nothing to reconcile them | Poor, for the same reason |
| **3. Dedicated ownership binding artifact** (= C) | Highest, once built — a real UCKO gains lifecycle, evidence, provenance, certification for free, and can reuse the already-declared, currently-dormant `"relationship"` `GOVERNED_CATEGORY` value (Article 18) | No precedent yet *for a category-level relationship UCKO specifically*, but structurally consistent with how every other governed relationship in this system is modeled | High, once minted — subject to `require_lawful()`, `discover()`, `validate_universe()` like any object | Scales to any provider/category count without new mechanism | Native — multiplicity is just multiple bindings or a binding with several producers |
| **4. Registry relationship** (= D, the `*_resolution` ledger) | High **now** — matches three already-proven precedents exactly | **Best fit** — `PHASE-UCF-004` bound `existence_resolution`/`lifecycle_resolution`/`certification_authority_resolution` this same way, each *before* code was built against it, and this arc has never gone straight to a first-class binding UCKO for a new authority question | High today, with zero new code — the ledger is already read by governance tooling and `verify_binding()` | Sufficient for today's 4-provider, 35-category scale; no evidence (per `PHASE-UCF-006`'s own performance-evidence finding) that this will not hold at the current measured scale | Supported directly — `existence_resolution`'s own `MULTIPLE_INDEPENDENT_AUTHORITIES` shape already proves declared, legitimate plurality works in exactly this ledger |

**Selected determination: Option 4 now — a `category_ownership_resolution` section in `00-BOOK/DATA/constitutional-authority-alignment.json`, in the same shape as `existence_resolution`/`lifecycle_resolution`/`certification_authority_resolution`** (a `model.type`, and one entry per governed category actually in use, each naming its authoritative provider(s) and `bounded_question`). This is not a new mechanism; it is the fourth application of an already-proven one, requiring no change to any Layer Zero primitive and no new code.

**Option 3 (a first-class `ProviderCategoryOwnershipBinding` UCKO, reusing the dormant `"relationship"` `GOVERNED_CATEGORY` and the already-registered `"ownership"` `RELATIONSHIP_CLASS` term) is identified as the correct future evolution** — if and when category-ownership facts need their own lifecycle, evidence chain, or certification surface independent of the ledger that first declares them — but is explicitly not required to unblock `PROVIDER_CATEGORY_OWNERSHIP_INTEGRITY` as `PHASE-UCF-007` specified it, and is not built here.

Options 1 and 2 are ruled out: 1 for blast radius disproportionate to the gap, 2 for lacking any arbitration mechanism.

---

## Future Invariant Dependency Boundary

`PROVIDER_CATEGORY_OWNERSHIP_INTEGRITY`, as `PHASE-UCF-007` specified it conceptually, will depend on:

- **Category ownership binding** — yes; this document determines its shape (Option 4 now, the `category_ownership_resolution` ledger entry; Option 3 as a future promotion). Not yet populated with real data — that population is future work, not performed here.
- **Provider identity** — yes, already fully available; `discovery.provider` requires no change.
- **Provider registration** — yes, already fully available; `discover()`'s existing admission mechanism requires no change.
- **Evidence** — yes, at minimum the provider→category population map (`discovery.provider` × `taxonomy.category`), the same shape `PHASE-UCF-007` computed by hand and this document formalizes as the binding's evidentiary basis, not its enforcement.
- **Authority graph** — indirectly, only if/when the binding is promoted to Option 3 (a real UCKO, wired into `graph.py`'s existing edge machinery); not required for Option 4.
- **Governance registry** — yes, directly: the binding's home is `00-BOOK/DATA/constitutional-authority-alignment.json`, the same file the invariant's own precedent-setting siblings already live in.

None of these dependencies is implemented, wired, or populated by this document — the boundary is stated, not built, per instruction.

---

## Gap Reclassification

Reviewing `PHASE-UCF-007`'s gap table against this determination's findings:

| Gap | UCF-007 classification | This determination | Change |
|---|---|---|---|
| Provider category exclusivity has no general invariant | Required | **Required — confirmed, now three-layered.** (i) no invariant — still true; (ii) no ownership concept — this document determines its shape, closing the *design* half of the layer `UCF-007` named, but does not implement it; (iii) no binding populated with real provider→category ownership facts — newly separated out as its own remaining step, still open | Refined, not downgraded |
| Semantic-duplicate category registration (Case 2) | Deferred | **Deferred — confirmed.** Concerns term-identity duplication, not population/authority; unaffected by an ownership-model determination | Unchanged |
| Provider certification/pre-flight checklist | Deferred | **Deferred — confirmed.** The Provider Federation Contract's finding (no declaration is mandated yet) reinforces rather than changes this | Unchanged |
| Onboarding documentation | Deferred | **Deferred — confirmed.** Untouched by this determination | Unchanged |
| Evolution History cross-domain view | Deferred | **Deferred — confirmed.** Untouched | Unchanged |
| No consumers of the expanded UCKP population | Observational | **Observational — confirmed.** Untouched | Unchanged |
| No performance data past current scale | Observational | **Observational — confirmed.** Untouched | Unchanged |
| **New: vocabulary-term registration has no actor/"registrar" capture at all** | *(not previously named)* | **Observational.** `extended_with()` has never been exercised by any provider (`PHASE-UCF-007`'s own finding); no evidence of harm, same reasoning that class already earned for the new-category-registration gate | New finding |
| **New: the declared, currently-dormant `"relationship"` `GOVERNED_CATEGORY` value is the natural future home for a category-ownership binding UCKO** | *(not previously named)* | **Observational.** Informational; identifies a reuse opportunity for a future phase, not a defect | New finding |

---

## Final Determination

Category ownership should be represented, as of this determination, as a relationship-shaped fact recorded through the repository's existing `*_resolution` governance-ledger pattern — a `category_ownership_resolution` section in `00-BOOK/DATA/constitutional-authority-alignment.json`, in the identical shape already proven three times by `existence_resolution`, `lifecycle_resolution`, and `certification_authority_resolution` — rather than as a mutation of the shared `Term`/`Vocabulary` Layer Zero primitives (wrong blast radius for the size of this gap) or as bare provider self-declaration (structurally unable to arbitrate the exact collision it would need to prevent). A dedicated first-class `ProviderCategoryOwnershipBinding` UCKO, naturally reusing the already-declared but currently zero-population `"relationship"` `GOVERNED_CATEGORY` and the already-registered `"ownership"` `RELATIONSHIP_CLASS` term, is identified as the correct future evolution once category-ownership facts need their own lifecycle, evidence chain, or certification surface — but is not required to unblock `PROVIDER_CATEGORY_OWNERSHIP_INTEGRITY` and is not built here.

Owner (accountability, Facet 7), Authority (single-parent derivation, Facet 5), and Provider (discovery source, Facet 21) are three already-distinct, already-implemented concepts in this codebase and must not be collapsed into one another — `PHASE-UCF-005`'s original defect is, in this vocabulary, exactly a Provider fact being mistaken for an Owner fact with nothing in between to catch the substitution. Contributor, Producer, and Registrar are not modeled anywhere today; this determination does not invent formal definitions for them beyond the minimum needed to keep them from being conflated with the three that already exist, consistent with `PHASE-UCF-007`'s own restraint against building ahead of evidence.

No code, test, registry, or constitutional change is made in this document. The category-ownership binding's *content* (which provider owns which of the 14 actively-populated categories today) is not populated here — that is the next, still-open step, to be scoped explicitly rather than assumed by this determination.

### Unresolved questions, carried forward explicitly

1. Should the `category_ownership_resolution` ledger be populated now (a mechanical, low-risk step — restate the already-hand-computed `PHASE-UCF-007` histogram as declared ownership) or left for the phase that also builds the invariant, so the two land together?
2. Does `Ownership.stewards`, designed for per-object accountability, actually generalize cleanly to "delegated category producers," or does that federation-contract concept need its own field if it is ever built? Not settled here — flagged as an interpretation, not a fact.
3. Should the eventual invariant be fail-closed (blocking) or advisory on first detection? `PHASE-UCF-007` deferred this explicitly; this document adds nothing new to resolve it.

---

Stopping after PHASE-UCF-008, as instructed. Minimum validation (`verify_binding()`, `discover()`, `validate_universe()`, `ukb.py enforce --pre`/`validate`) run fresh and reported under Current Repository Truth — no repository corruption found.
