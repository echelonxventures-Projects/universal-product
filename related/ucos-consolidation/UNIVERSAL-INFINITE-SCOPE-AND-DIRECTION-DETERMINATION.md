# UNIVERSAL INFINITE SCOPE AND DIRECTION DETERMINATION

> **Mission:** UCOS Ω∞ Universal Infinite Scope, Self-Evolving Constitutional Model Alignment — Workstreams 1, 5, 9, 10
> **Baseline:** `bb9c27d2` · **Branch:** `integration/recovery-001` · **Date:** 2026-08-18
> **Temporal coordinate:** `logical:ucos-repository-history@1#485` (CMG-000002; derived from repository history position, not a clock read)
> **Mode:** Determination. No new authority, no new registry, no new identity system, no new lifecycle, no competing capability.
> **Authority:** NONE (DERIVED TRUTH). This determination locates existing owners and makes an existing property measurable. It legislates nothing.

---

## 0. Standing — what this determination is and is not

The mission asks for a principle **above** the Universal Constitutional Lifecycle:

```
UCOS Ω∞ → Universal Infinite Scope & Direction Principle → Universal Constitutional Lifecycle → All Objects
```

**A supreme instrument is not created, and none is elevated.** Read literally, "above the lifecycle" would install a new supreme authority over `CMG-000001` (law owner) and `UCIC-001` (lifecycle owner). That is refused under `CAA-INV-04` and `CAA-INV-07`, and under CMG Art LXXVI.6 (expansion by reinterpretation).

The principle's correct standing is **not superior but pervasive**. It is not a layer in the authority stack; it is a property every layer must exhibit, including the stack itself. Restated as the repository can actually hold it:

```
CMG-000001            law owner — what counts as constitutional
UCIC-001              lifecycle owner — the one lifecycle every capability follows
CEP-009 · Article-14  evolution authority — the only forward channel
        │
        ▼
UISD-000001           Universal Infinite Scope & Direction — DERIVED TRUTH
                      not an authority over the above; a measurement that the above,
                      and everything under them, and UISD-000001 itself, remain
                      unbounded in scope, direction, relationship and evolution.
```

| Instrument | Standing | Basis |
|---|---|---|
| **CMG-000001** | Law owner | `ucl.json` `programme.law_owner` |
| **UCIC-001** | Lifecycle owner | `ucl.json` `programme.architecture_owner` |
| **UCL-000001** | Derived lifecycle truth, **not** supreme | Own `authority` field |
| **CEP-009 · Article-14** | Amendment / perpetual evolution | `engine/uckp/evolution.py` |
| **UCKP-ART-05** | Sole identity authority | `constitutional-authority-alignment.json` `identity_authority_resolution` |
| **UISD-000001** *(this cycle)* | **Derived truth — measurement only** | Own declaration; consumes no counter, opens no registry |

**What UISD-000001 adds that did not exist:** the infinite-scope property was already **asserted** — `03-CONSTITUTIONAL-UNBOUNDEDNESS-CERTIFICATION.md` certifies 16 axes unbounded, `04-HIDDEN-FINITE-ASSUMPTION-CERTIFICATION.md` certifies 23 axes free of finite assumption. Both are dated 2026-07-23 prose certifications, and `04` §4 states plainly: *"An exhaustive line-by-line proof of absence … was **not** performed. ASSUMPTION: no hidden finite assumption exists beyond those reviewed."* Residual risk is confined by that document to the **realization layers**.

UISD-000001 converts the asserted property into a **computed** one over exactly that undischarged space. It is the same move the repository already made twice: `engine/context/constitution.py` for `CXL-01…12`, `engine/object_birth/contract.py` for `UOBC-L-01…08` — a law whose compliance nobody computes is manual governance.

---

## 1. Reuse before create — what already satisfies the mission

Measured, not assumed. Nine of the mission's requirements are **already satisfied by located owners** and require no new artifact:

| Mission requirement | Already satisfied by | Evidence |
|---|---|---|
| Lifecycle inherits its own lifecycle | `CK-UCL-SELF` (declared twice in `ucl.json`), `make ucl-self` 13 guards | Gate-enforced every `./verify.sh` |
| Lifecycle stage set is open | `ucl-stage-manifest.json` `manifest.open: true`, `closed_enumeration: false`, `admission` clause | Measured: 45 nodes, 0 divergences vs `engine/nucleus/lifecycle.py` |
| Evolution evolves through evolution | `is_terminal()` returns False unconditionally; `next_stage` wraps `% 15` | Measured: `next_stage(EVOLUTION_CYCLE[-1]) == EVOLUTION_CYCLE[0]` → True |
| Relationship model is infinite | `relationship.schema.json` `type` is **pattern-only, no `enum`**; `RELATIONSHIP_FREEFORM_LABEL = "RELATES"`; append-only vocabularies | Measured: extending `RELATION_TYPE_VOCABULARY` 17→18 in memory leaves the original untouched |
| One identity authority | `UCKP-ART-05`, `engine/uckp/identity.py`, role SUPREME | `CAA-INV-04`; mint marker `category_seq` |
| Identity at creation | `UOBC-000001` — 9 mandatory fields, 8 computed laws, `identity_exists` flips once at `UOBC-S-04` | Stage 6e, fail-closed |
| Temporal representation neutrality | `CMG-000002` §3.1 "DOES NOT MANDATE" (10 refusals incl. UTC, ISO 8601, Gregorian) | `engine/temporal/` — 4 modules, clock-free, `now()` deliberately absent |
| Technology is not constitutional | CEP scope-exclusion (CEP-007 II.2, XXII.3); `PERSISTENCE_BINDINGS` is a *binding*, not a property | `pyproject.toml` `dependencies = []`; `requires-python = ">=3.12"` is a floor with no ceiling |
| Implementation independence | `ucl-stage-manifest.json` `$implementation_independence_comment`: *"deleting every module named in every `evidence` list would not remove a single stage from the graph"* | — |

**Consequence: the mission's twelve workstreams do not require twelve new capabilities.** They require one measurement surface and five determinations. Everything else is located.

---

## 2. Refusals

| Mission-implied artifact | Disposition | Reason |
|---|---|---|
| A principle **superior to** UCL / CMG-000001 | **REFUSED** | Would install a rival supreme authority — `CAA-INV-04`, `CAA-INV-07`, CMG LXXVI.6 |
| A new Universal Scope Registry | **REFUSED** | A registry that issues identifiers is a second mint; the one mint is `id-ledger.json` `category_seq` |
| A new Universal Relationship Catalog / `CEP-REL-001` | **REFUSED** | `UCRD-001` §7 already refuses it by name; CMG-000013 §5 forbids a hand-written constitutional relationship matrix as "a second source of truth that will drift" |
| A new identity universe / third dictionary | **REFUSED** | `UNIVERSAL-IDENTITY-UNIVERSE-DETERMINATION.md` §6 |
| A new lifecycle, stage registry or evolution constitution | **REFUSED** | `UNIVERSAL-LIFECYCLE-INHERITANCE-RECONCILIATION-DETERMINATION.md` §1 refuses all five by name |
| A closed "Universal Capability List" | **REFUSED** | Converted to a seed model — §5 |
| Blind textual replacement of freeze vocabulary | **REFUSED** | Semantic classification first — see `UNIVERSAL-LIFECYCLE-SEMANTIC-RESCAN-REGISTER.md` |
| A verification command that mints, migrates or regenerates | **REFUSED** | `mutation-governance-boundary.json`; the gate created here writes nothing |

**Created: one derived-truth programme (`UISD-000001`) and one observational engine (`engine/infinite_scope/`).** Nothing else.

---

## 3. The Infinite Scope and Direction Laws

Ten laws. Each names a check that computes its own compliance; the contract refuses to construct if a check is missing. Held as **data** in `00-MASTER/UISD-000001/uisd-declaration.json` — the engine contains no law text and no enumeration member.

| Law | Statement | Check |
|---|---|---|
| **ISD-L-01** Scope Expansion Capacity | `ScopeExpansionCapacity(object) = ∞`. No enumeration claims completeness silently: every closed enumeration discloses its closing invariant **and** its admission path. | `scope_expansion_capacity` |
| **ISD-L-02** Direction Expansion Capacity | `DirectionExpansionCapacity(object) = ∞`. The relationship type space is pattern-constrained, never enum-constrained, and a freeform admission label exists. | `direction_expansion_capacity` |
| **ISD-L-03** The Principle Inherits Its Own Lifecycle | UISD-000001 is subject to its own laws, declares no independent lifecycle, and holds a birth record like any other object. | `principle_inherits_itself` |
| **ISD-L-04** Lifecycle Applies To Itself | The lifecycle stage graph declares itself open and admits a node without an engine change; the executable projection does not diverge from it. | `lifecycle_applies_to_itself` |
| **ISD-L-05** Evolution Applies To Itself | The evolution cycle has no terminal stage and returns to its first stage from its last. Evolution cannot exempt itself from continuation. | `evolution_applies_to_itself` |
| **ISD-L-06** Relationship Model Expands | `EvolutionCapacity(relationship) = ∞` and `ExpansionCapacity(RelationshipModel) = ∞`: the relationship vocabularies admit a new term by registration, without amendment and without mutating the existing vocabulary. | `relationship_model_expands` |
| **ISD-L-07** No Active Permanent Freeze | No forbidden permanence phrase appears as an active declaration in the scanned roots outside the disclosed, classified preserved sites. | `no_active_permanent_freeze` |
| **ISD-L-08** Baseline Temporal Qualification | Every declared baseline surface either carries a temporal coordinate that **parses** under CMG-000002, or discloses that it does not and names the owner it is deferred to. | `baseline_temporal_qualification` |
| **ISD-L-09** Technology Is An Evolutionary State | No runtime dependency is pinned; the language requirement is a floor with no ceiling; every verification-toolchain pin is disclosed with a reason. | `technology_is_evolutionary_state` |
| **ISD-L-10** Capability Seed Openness | The capability model is a seed, not a final universe: it declares `final: false` and every capability enumeration names its admission path. | `capability_seed_openness` |

**ISD-L-01 is the load-bearing law, and it is deliberately not "no closed enumerations exist."** That formulation would be false and would have to be disabled: `engine/uckp/facets.py` closes 33 facets *on purpose*, and its own docstring explains why — *"Adding a thirty-fourth facet is a constitutional amendment … Adding a new knowledge kind, authority tier, persistence technology or relationship class is registration, and registration must never require an amendment."* Closure of the *question set* is what keeps the *answer sets* open.

The finite assumption worth prohibiting is therefore not closure but **undisclosed** closure: an enumeration that is closed in code while nothing states what closes it or how a member is admitted. That is the condition under which a set silently becomes permanent. `CMG-REGISTRY.json` already models the disclosure correctly — 4 enumerations in `closed_enumerations`, each naming its closing article and invariant, with `relationship_types` deliberately outside that list.

---

## 4. Universal inheritance — everything, including the lifecycle itself

The mission's correction is accepted: not "CMG objects inherit lifecycle" but **everything inherits lifecycle**. Measured against located owners:

| Object class | Inheritance mechanism | Independent lifecycle? |
|---|---|---|
| CMG / CEP constitutional documents | CMG-000001 law owner; UCL-000001 stage graph | None |
| **Universal Constitutional Lifecycle itself** | `CK-UCL-SELF` → UCL-000001; `verify_manifest_alignment` fails closed | **None — self-applied, gate-enforced** |
| **Evolution model itself** | `is_terminal()` False; cycle wraps; CEP-009 amendment channel | **None — self-applied, structurally** |
| **Relationship model itself** | `RELATION_TYPE_VOCABULARY` / `RELATIONSHIP_CLASS_VOCABULARY` extend by registration | **None — self-applied by construction** |
| **This principle (UISD-000001)** | ISD-L-03; `independent_lifecycle_defined: false`; birth record in `birth-ledger.json` | **None — self-applied, measured** |
| UID / identity | UCKP-ART-05; UOBC-000001 birth contract | None |
| Registries · Dictionaries | Derived truth, regenerated by located producers | None |
| Engines · Code · Tests · Configurations | UGA `EXECUTABLE_OBJECT` / `TEST_OBJECT` / `CONFIGURATION_OBJECT` | None |
| Generated artifacts · Evidence · Certificates | `generated-artifact-registry.json`, replay-gated; CEP-005 / CEP-008 | None |
| Runtime objects | `engine/uicm` — "lifecycle stages | UCIC-001 | bound, never forked" | None |

One delegated exception stands, properly bounded: UAUE holds a delegated evolution-transaction lifecycle under `AUE-BND-01…10`, of which `AUE-BND-06` explicitly refuses to declare any stage. Delegation with a refusal to duplicate is the permitted form.

**Future objects inherit automatically, and this is a structural fact rather than a promise.** `UOBC-F-07` makes `lifecycle_binding` one of nine *mandatory* birth fields, and `UOBC-L-04` refuses any record with an empty mandatory field. An object cannot be born under the birth contract without a lifecycle binding, so a future CMG — or a future anything — cannot opt out by omission. That is precisely the defect `UNIVERSAL-LIFECYCLE-INHERITANCE-RECONCILIATION-DETERMINATION.md` §3 found in CMG-000008/9/10, now unable to recur.

---

## 5. Universal Constitutional Capability Seed Model

**Determination: the capability list is a seed, not a universe.** `CAPABILITY-COVERAGE-CLOSURE-DETERMINATION.md` already reached the honest verdict — **"CAPABILITY COVERAGE: NOT CLOSED — PARTIAL"**, 1 of 122 capabilities with a verifiable end-to-end chain, 0 with a stored constitution anchor, 0 with a certification record, and 46 git-tracked Python directories absent from the catalog. A list in that condition must not be presented as a completed universe.

Seed model, with each enumeration's admission path located:

| Enumeration | Population | Openness | Admission path |
|---|---|---|---|
| `intelligence/UCOS-RIE-CAPABILITY-CATALOG.json` | 126 | Derived snapshot, `authority: NONE` | Regenerated by `UCOS-RIE-001` from an evidence fingerprint |
| `knowledge/canonical-knowledge.json` `UCKO-CAP-*` | append-only | **Open** | Append a row; no code change |
| UICM capability population | rule-derived | **Open** | `uicm.json` `population`: *"a rule over the tracked boundary, never a list"* |
| UICM closure dimensions | 17 | **Disclosed-closed** | New probe + resolution binding (`require_probe_bijection`, UICM-INV-02/13) |
| UGA `object_classes` | 7 | **Disclosed-closed** | `uga-declaration.json` append + `_CATEGORY_MAP`/`_TIER_MAP` in `engine/uckp/uga_projection.py` |
| `engine/uckp/facets.py` `Facet` | 33 | **Closed on purpose** | Constitutional amendment — and this is correct, see §3 |
| `engine/knowledge/ukip/constitution.py` `KnowledgeCapability` | 11 | **CLOSED, UNDISCLOSED** | **None declared — see risk R-1** |

`KnowledgeCapability` is the one capability enumeration that is compiled into a Python `Enum`, has **no coercer**, is frozen into `KNOWLEDGE_CAPABILITIES = tuple(KnowledgeCapability)`, and discloses neither a closing invariant nor an admission path. Its sibling in the same package, `ProviderKind` (`engine/knowledge/ukip/contracts.py:63`), is the in-repo precedent for the correct shape: its docstring declares it *"an open taxonomy of knowledge origins"* and it carries a fail-closed coercer.

**Disposition: disclosed, not changed here.** Amending it is a change to a constitutional projection owned by `engine/knowledge/ukip/`, not by a root determination. It is recorded as **gap ISD-G-01** and is measured — not silently tolerated — by ISD-L-10, which requires an admission path for every declared enumeration. This determination declares the enumeration in `uisd-declaration.json` **with `admission` naming its owner and the amendment channel**, which is the disclosure ISD-L-01 demands; making the enum itself extensible remains the owner's act.

---

## 6. The universal evolution cycle applies everywhere

The mission's ~50-step cycle is not a new lifecycle to install. Every step is already owned, across four located instruments with disjoint subjects:

| Cycle segment | Located owner | Count |
|---|---|---|
| Observation → Gap Discovery → Reuse Before Create | `ucl-stage-manifest.json` ordinals 10–110 (GOAL, DISCOVERY, REUSE groups) | 11 nodes |
| Perception · Evidence · Assurance · Cognition · Correction | ordinals 120–230 | 12 nodes |
| Construction · Governance · Integration | ordinals 240–300 | 7 nodes |
| Universal ID Assignment · Dictionary · Registry · Bookkeeping · Lineage | ordinals 310–350 (IDENTITY group) | 5 nodes |
| Repository Truth · Replay · Deterministic Fixed Point | ordinals 360–380 | 3 nodes |
| Knowledge Extraction · Capability Elevation · Begin Next Cycle | ordinals 390–450 | 7 nodes |
| Capability implementation (Discovery → Production Readiness) | `UCIC-001` | 15 stages |
| Perpetual evolution (observe → continuation → observe) | Article-14, `engine/uckp/evolution.py` | 15 stages, non-terminal |
| Object state (draft → historical) | `engine/knowledge/model.py` `Lifecycle` | 10 stages |

**Applicability is total by the same mechanism as §4:** these owners bind objects, capabilities, relationships, the lifecycle, the evolution model and the governance model alike, because none of them admits an object without a `lifecycle_binding` and none declares a scope exclusion.

Two named absences, both pre-existing and both already owned elsewhere:

- **Downgrade / Restoration.** `_LIFECYCLE_TRANSITIONS` makes `ARCHIVED` and `HISTORICAL` terminal, so `Restored` is structurally unreachable. Recorded as gap **G10** by `UNIVERSAL-EVOLUTION-MODEL-DETERMINATION.md`, correctly deferred: *"a reverse edge in a lifecycle transition graph is a substantive lifecycle change and this determination holds no lifecycle authority."* Unchanged here, for the same reason.
- **Commercialization.** `UCRD-001` §6 determines the disposition — one new relationship class via a single `VocabularyRegistry.extend`, replay-neutral. Unchanged here; it is the relationship owner's registration, not a determination's.

---

## 7. Verification purity

The gate created by this cycle is observational. Stated as the mutation boundary the repository already uses:

```
command                                        plane         writes
engine.infinite_scope.gate                     observation   nothing
engine.infinite_scope.gate --gate --quiet      observation   nothing
engine.infinite_scope.gate --json              observation   nothing
```

It reads its declaration, reads declared files in the tree, imports located modules in-process, computes, and returns an exit code. No clock, no network, no subprocess, no write — including to gitignored paths. It mints no identifier, modifies no registry, creates no artifact, regenerates no canonical state and migrates no object. It declares **no `--render` and no `--replay`**, because a gate with nothing to render cannot drift; declaring an unread flag is the `GP-4` defect.

Exit semantics follow the convention: `0` OPEN, `1` CLOSED (a law was measured and refused), `2` FAULT (no verdict could be reached). Collapsing 1 and 2 would let an unreadable declaration pass as whichever was convenient.

---

## 8. Determination

| Item | Determination |
|---|---|
| Principle superior to CMG-000001 / UCIC-001 | **REFUSED** — pervasive property, not a new authority layer |
| `UISD-000001` as derived-truth measurement surface | **CREATED** — no counter, no registry, no lifecycle, no identity mechanism |
| Ten ISD laws, each computed | **DECLARED as data**; engine holds no law text |
| Lifecycle applies to itself | **ALREADY ENFORCED** (`CK-UCL-SELF`); now additionally measured by ISD-L-04 |
| Evolution applies to itself | **ALREADY STRUCTURAL** (`is_terminal` False); now measured by ISD-L-05 |
| Relationship model infinite | **ALREADY OPEN**; now measured by ISD-L-06 — see `UNIVERSAL-RELATIONSHIP-INTELLIGENCE-FOUNDATION-DETERMINATION.md` |
| Universal inheritance incl. lifecycle itself | **HOLDS** — one bounded delegation; enforced at birth by `UOBC-F-07` + `UOBC-L-04` |
| Capability list → Seed Model | **DETERMINED** — `final: false`; one undisclosed closure recorded as **ISD-G-01** |
| Evolution cycle applicability | **TOTAL** across located owners; G10 and Commercialization remain with their owners |
| Verification purity | **PRESERVED** — the gate writes nothing |

**Gaps recorded, not silently carried:**

| Gap | Subject | Owner |
|---|---|---|
| **ISD-G-01** | `KnowledgeCapability` — closed enum, no coercer, no declared admission path | `engine/knowledge/ukip/` |
| **ISD-G-02** | `commit:<sha12>` is declared a conforming temporal coordinate in prose but is refused by `parse_qualified` | `engine/temporal/` + UGA |
| **ISD-G-03** | `BASELINE-001` records temporality as the boolean `date_recorded` and bare calendar dates; it does not import `engine/temporal/` | `BASELINE-001` |
| **ISD-G-04** | 12,899 relationship edges are materialized and no gate validates them against `relationship.schema.json` | UKB / relationship owner |

---

**END UNIVERSAL INFINITE SCOPE AND DIRECTION DETERMINATION**

**Status:** Evolution Baseline Established v1.0
**Certified Temporal Baseline:** `bb9c27d2` · `logical:ucos-repository-history@1#485` (CMG-000002 coordinate; CEP-005 certification channel)
**Lifecycle Authority:** UCIC-001 (owner) · UCL-000001 (derived truth, not supreme) · CMG-000001 (law)
**Governed Evolution:** ENABLED — CEP-009 amendment · Article-14 perpetual cycle
