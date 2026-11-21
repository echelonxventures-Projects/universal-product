# UCOS Ω∞ — S-1 OWNERSHIP GRAIN DETERMINATION

> **Mission:** Determine the canonical ownership subject grain required before any S-1 mutation classification convergence execution. Resolve **"what exactly is owned?"** before **"who owns it?"**
> **Baseline:** `bae59755d7e2d3566c93b89c722b68847145269a` · **Branch:** `integration/recovery-001` · 515 commits
> **Working tree at capture:** 377 porcelain entries (38 tracked-modified · 339 untracked) — pre-existing, untouched
> **Mode:** READ-ONLY DETERMINATION. No implementation, no ownership assignment, no registry mutation, no code change, no JSON change, no commit.
> **Authority:** **NONE (DERIVED TRUTH).** This determination declares no grain, assigns no owner and creates no authority. It reports what the law and the registries already establish, and where they disagree.
> **Verdict:** **NOT COMPLETE**

**Mandatory principles, as applied**

| Principle | Applied meaning in this determination |
|---|---|
| **Zero fixes** | Four ownership surfaces were found to disagree. None was reconciled. The 58% path-shaped owner population was measured and left exactly as found |
| **Zero patches** | No file edited. One new markdown artifact; nothing else |
| **Zero shortcuts** | Existing declarations were **not assumed correct**, as instructed. `UOBC`'s package grain and the ODF's authority grain were both tested and both found non-canonical (§4) |
| **Zero temporary solutions** | No interim grain, no provisional owner, no staged model is offered |
| **Zero duplicate** | No fifth ownership model is proposed. §4 selects an **existing** constitutional model |
| **Zero overlapping** | Overlap is the defect being reported, not a condition being introduced |
| **100% systematic · authentic · auditable · secured · traceable · reversible** | Every finding is a read of tracked state at a stated digest; §16 records the reversibility condition — nothing was written, so nothing needs reverting |

---

## 1. Executive Determination

# NOT COMPLETE

**The ownership subject grain is undeclared, and four surfaces answer "what is owned?" at four different grains with no crosswalk. One of the four is the constitutional object model, it already carries ownership as a required facet, and it is the only candidate that survives the law. It is also the one whose attestation is most wrong.**

### 1.1 The reality in one movement

| # | Surface | Grain it uses | Population | Owner form |
|---|---|---|---|---|
| **S-1** | **UCKO** — `engine/uckp/ucko.py`, Facet 7 `ownership` | the **discovered provider object** | **6,338** | bare string · **58% path-shaped** · 277 distinct · **0 stewards attested** |
| **S-2** | **UGA** — existence & object registries | the **path** | 6,145 | tokens and paths · `NONE — DERIVED TRUTH` tier |
| **S-3** | **UOF-001 / ODF** — ownership determination | the **basename stem** | 0 assignments | zone-authority labels · schema forbids paths |
| **S-4** | **UOBC-000001** — birth scope policy | the **constitutional object** (package · declaration · document · suite) | 35 born at baseline | n/a — declares grain, not owners |
| S-5 | mutation register `governed_by` chains | the **artifact's own declared Authority field** | owner-parameterised | free prose read from the artifact |

**Five surfaces. Five grains. Zero crosswalks. `UCKP-INV-04` zero-ambiguity is the invariant this violates, and nothing measures it.**

### 1.2 The law already answers the question

Two articles decide the grain, and they are executable law rather than declaration:

> **`UCKP-ART-02` Canonical Existence** — *"Every governed **category of entity** shall exist exactly once as a canonical Universal Constitutional Knowledge Object. Nothing exists constitutionally until it has become one."*
>
> **`UCKP-ART-06` Facet Completeness** — *"Every object shall carry every universal facet. A facet may be unattested, but it may never be absent."*

`OWNERSHIP` is Facet 7 of 33, and `REQUIRED_FACETS = tuple(Facet)` — all 33 are required.

**Therefore: the ownership subject is the UCKO, and the UCKO's grain is the governed category of entity.** Ownership is not a property attached to a file; it is a facet carried by a constitutional object. Every other grain in the mission's list is either an address of such an object or a projection of one, and `UCKP-ART-04` / `UCKP-ART-11` say so directly: representations are not authority, and *"Markdown, JSON, YAML and schemas are not authority."*

### 1.3 Why the answer being available does not make the grain complete

Measured, the UCKO ownership facet is attested at the wrong grain and in the wrong form:

| Measurement | Value | Conflict |
|---|---|---|
| UCKO population | **6,338** | `ART-02` grain is the *category of entity*; 6,338 is a **per-object** population, not a category population |
| Distinct `ownership.owner` values | 277 | — |
| Path-shaped owners | **3,717 — 58%** | the governed assignment schema: *"an authority, **not a path**"* |
| `stewards` attested | **0 of 6,338** | the second ownership field is entirely unattested |
| `authority` facet form | `tier='advisory'`, `instrument=''` | no binding instrument named on any object |
| Governed ownership assignments | **0** | `OWN-REQ-001` requires constitutive declared evidence |

> **The constitutional object model carries an ownership facet for 6,338 objects, most of which name a directory. A directory is an address. `UCKP-ART-05` states an identity is *"independent of technology, storage, repository and time"* — and 58% of the repository's attested ownership is a repository path, which changes when a file moves.**

### 1.4 What this determination settles and does not settle

| Question | Answer |
|---|---|
| Is the grain declared? | **NO** |
| Does the law determine it? | **YES — `ART-02` + `ART-06`: the UCKO** |
| Is a new ownership model needed? | **NO — `ART-18`; the model exists** |
| Is the existing attestation correct? | **NO — wrong grain, wrong form** |
| Can "who owns it?" be answered yet? | **NO — and it must not be attempted (§14)** |
| Is the grain COMPLETE? | **NO — §15** |
| Closure | **NOT CLAIMED** |

---

## 2. Ownership Ontology Analysis

### 2.1 The fifteen candidate grains, classified against the law

Each candidate is tested for what it **is** under `UCKP-LAW-0001`, not for whether it is convenient.

| # | Candidate grain | What it is under the law | Can it be an ownership subject? | Basis |
|---|---|---|---|---|
| 1 | **Universe** | a scope, not an entity — `UISD` axis `scope` | **NO** — nothing is accountable for a scope | `ART-02` requires a category of entity |
| 2 | **Domain** | a taxonomy node — Facet 4 `taxonomy` | **NO** — a classification, not an object | `ART-02` |
| 3 | **Capability** | a **governed category of entity** | **YES** — becomes a UCKO | `ART-02`; `UOBC` package grain |
| 4 | **Authority** | Facet 5 `authority` of an object — `AuthorityBinding` | **NO as a subject; YES as an owner value** | only `SUPREME` may hold authority (`CAA`) |
| 5 | **Programme** | a governed category of entity | **YES** — becomes a UCKO | `UOBC` `PROGRAMME_DECLARATION` |
| 6 | **Package** | the **address form** of a capability | **NO — it is the capability's locator** | `UOBC`: *"a module file is an address within it"* |
| 7 | **Module** | an address within a package | **NO** | `UOBC`; `ART-04` |
| 8 | **Artifact** | a representation | **NO** | `ART-04` non-authority of representations; `ART-11` |
| 9 | **Registry object** | a projection of an object into a register | **NO** | `ART-11` *"generated output never owns truth"* |
| 10 | **Identity population** | the set of minted ids — a measurement | **NO** | `ART-05`; a population is not an entity |
| 11 | **Mutation class** | a governed category of entity, declared in the register | **YES** — and it is **not** currently a UCKO | `ART-02`; §7.4 |
| 12 | **Rule** | a decision procedure over a class | **NO as a subject** — it is owned *with* its class | `ART-16` |
| 13 | **Law** | the one `SUPREME` instrument | **SELF-GROUNDING — owns itself** | §7.3 |
| 14 | **Relationship** | Facet 9 — *"every relationship is executable"* | **INSTANCE: YES · CLASS: NO** | `ART-07`; §6 |
| 15 | **Entity** | the general term for a UCKO subject | **YES — this is the grain** | `ART-02` |

### 2.2 The classification

| Relation | Members | Determination |
|---|---|---|
| **Same grain** | Capability · Programme · Mutation class · Entity | All are *governed categories of entity*. They are one grain under `ART-02`, differing only in category, not in kind |
| **Hierarchical grain (address-of)** | Package → Module → Artifact → Registry object | A strict address chain **beneath** the entity grain. None is a subject; each locates one. `ART-04` and `ART-11` make this hierarchy non-authoritative at every level |
| **Independent grain (facet-of)** | Authority · Relationship class · Rule · Context · Temporal history | Facets **carried by** an entity, not entities themselves. They are independent axes of description, never subjects of ownership |
| **Incompatible grain** | Universe · Domain · Identity population | Scopes, classifications and measurements. Assigning ownership to any of them would make a *set* accountable, which no article supports |
| **Self-grounding** | Law | `UCKP-LAW-0001` derives its authority from itself; `CAA-INV-01` `EXACTLY_ONE` |
| **Dual grain — genuinely two subjects** | Relationship | The *class* is a facet of the model (owned by `ART-07`); the *instance* is an identified entity (`UEDGE-*`). §6 |

### 2.3 The ontological finding

**Twelve of the fifteen candidates are not ownership subjects at all, and the three that are collapse into one grain.** The mission's list is not a menu of alternatives — it is a mixture of one grain, an address hierarchy beneath it, and a facet set orthogonal to it.

> **The apparent difficulty of choosing a grain is an artifact of the four surfaces having each chosen a different *level* of the same address hierarchy. `UCKP-ART-02` does not offer a level. It names the subject: the governed category of entity, existing exactly once as a UCKO.**

---

## 3. Existing Ownership Model Discovery

### 3.1 Where ownership is declared

| Surface | Locus | Attested? | Form |
|---|---|---|---|
| UCKO Facet 7 | `engine/uckp/values.py:215` `Ownership(owner, stewards)` | **YES — 6,338 objects** | bare `str`; 277 distinct; **58% paths**; 0 stewards |
| UCKO Facet 5 | `AuthorityBinding(tier, derives_from, instrument)` | partially | `tier='advisory'`, `instrument=''` observed |
| UOF-001 assignment catalogue | `ucos-ownership-declarations.json` | **NO — 0 entries** | would be `owner`/`authority`/`locator`/`precedence`/`detail` |
| Truth policy zone authorities | `ucos-repository-truth.json` | **YES — 6 labels, 5 owning zones** | prose labels, e.g. `Repository Truth Authority (00-BOOK)` |
| UGA registries | `00-EXISTENCE-INVENTORY.json`, `02-UNIVERSAL-OBJECT-REGISTRY.json` | **YES — 6,145 objects** | tokens and paths, `NONE — DERIVED TRUTH` |
| UOBC birth kinds | `birth-scope-policy.json` | grain declared, owners not | `granularity: suite\|declaration\|package\|document` |
| Mutation register | `governed_by` per class | **YES — 9 chains** | 8 disposing parties + owner-parameterised prose |
| CAA-001 | `subordinate_instruments` `owns` / `may_never_own` | **YES — 11 instruments** | statements of what an instrument may own, not who owns it |

### 3.2 Where ownership is inferred

| Inference | Locus | Why it is an inference |
|---|---|---|
| Path → owner | UGA `uga-declaration.json:115` pattern *"00-BOOK/tools/… \| 00-BOOK/DATA/…"* → `UCOS-UKB-TOOLING`, returned at `uga_engine.py:222` | derived from location; `OWN-REQ-001` — *"Corroboration… never establishes it"* |
| Directory → owner | UCKO ownership facet, **3,717 objects (58%)** | a path is an address; `ART-05` identity is storage-independent |
| Zone → owner | ODF `DefinitionalLocatorProvider`, precedence 500 | constitutive by declaration, but at the **basename** grain |
| Basename → subject | same provider, `_is_definitional(basename, subject_id)` | the subject is inferred from a filename |
| Grain → default | `DefinitionalLocatorProvider(granularity=AUTHORITY)` | **the grain itself is inferred from a code default** |

### 3.3 Where ownership is missing

| Missing | Measured |
|---|---|
| Governed ownership assignments | **0, repository-wide** |
| Stewards on any UCKO | **0 of 6,338** |
| Binding instrument on the authority facet | `instrument=''` observed |
| A UCKO for the mutation register | not in the 6,338 provider population |
| A UCKO for any of the 9 mutation classes | none |
| An owner for the rival module | absent from 4 registries; `SUBJECT-NOT-REGISTERED` |
| An owning zone for root determinations | `derived.root-determinations` authority `''`, `is_home=False` |
| A declared ownership granularity | **no JSON declares one** |
| A crosswalk among the five owner vocabularies | **none** |

### 3.4 Where ownership conflicts

| Subject | Answers | Conflict class |
|---|---|---|
| `mutation-governance-boundary.json` | ODF: `Repository Truth Authority (00-BOOK)` · UGA: `UCOS-UKB-TOOLING` · R-06: a standing | **three answers, unadjudicated** |
| `mutation_classification.py` | ODF: `Implementation Authority (packaged trees)` · UGA: `platform/repository_intelligence` (a path) | **two answers, one in a forbidden form** |
| 6,338 UCKOs | UCKO facet owner vs ODF zone authority vs UGA token | **three vocabularies, zero shared members** |
| the 98 R-08/R-09 artifacts | two disposing chains, neither resolvable (`classify()` → `ERROR`) | **disposition ambiguity** |
| grain itself | UCKO object vs UGA path vs ODF stem vs UOBC constitutional object | **the root conflict** |

### 3.5 Discovery finding

**Ownership is not missing from this repository. It is present five times, at four grains, in three incompatible value forms, with zero governed assignments and no adjudicator.** `UCKP-INV-03` zero-duplication and `UCKP-INV-04` zero-ambiguity are both engaged, and no instrument measures either over the ownership facet.

---

## 4. Subject Grain Determination

Existing declarations are **not** assumed correct. Each option is tested against the law, then against measurement.

### 4.1 Option A — Authority-level ownership

*The owner is an authority; whichever artifact sits in that authority's zone, the authority owns it.*

| Test | Result |
|---|---|
| Is it implemented? | **YES — it is the ODF's running default** (`OwnershipGranularity.AUTHORITY`) |
| Is it declared? | **NO — no JSON declares a granularity**; the contract states the grain *"is declared"* |
| Does it satisfy `ART-02`? | **NO** — an authority is Facet 5 of an object, not a category of entity |
| Consequence | *"two documents in one zone are not a contest"* — so the rival module and the classifier share one owner and their duplication is invisible to ownership |
| Verdict | **REJECTED** — a code default cannot be the constitutional grain (`ART-15`: *"No conclusion rests on a hardcoded assumption"*) |

### 4.2 Option B — Capability / package ownership

*The constitutional object is the capability; module files are addresses within it.*

| Test | Result |
|---|---|
| Is it declared? | **YES — `UOBC-000001`**: *"Birth granularity is the CONSTITUTIONAL OBJECT, never the path… A capability is born once as a package"* |
| Does it satisfy `ART-02`? | **PARTIALLY** — a capability *is* a governed category of entity, so this is a **correct instance** of the right grain |
| Is it total? | **NO** — `CAPABILITY_PACKAGE` is selector-scoped to `path_prefix: engine/`. Every `platform/` package falls to the `ADDRESSED_OBJECT` catch-all |
| Does it cover non-capability subjects? | **NO** — a mutation class is not a package |
| Verdict | **REJECTED AS THE GRAIN — ADOPTED AS AN INSTANCE OF IT.** The package is the *address* of a capability. `UOBC` says exactly this, and calling the address the subject inverts its own rule |

### 4.3 Option C — Artifact / object ownership

*The owner is recorded per artifact or per registry object.*

| Test | Result |
|---|---|
| Is it implemented? | **YES — UGA, 6,145 objects; and the UCKO facet, 6,338** |
| Does it satisfy `ART-02`? | **NO** — an artifact is a representation |
| Does it satisfy `ART-04` / `ART-11`? | **NO** — *"Documents are generated views… Generated output never owns truth; truth originates in an object"* |
| Does it satisfy `ART-05`? | **NO** — a path-keyed owner is storage-dependent; identity must be *"independent of technology, storage, repository and time"* |
| Measured consequence | **58% of attested UCKO owners are paths** |
| Verdict | **REJECTED** — this is the grain the repository has drifted into, and it is the one the law most directly forbids |

### 4.4 Option D — Multi-level ownership model

*Own at several grains simultaneously, with precedence between levels.*

| Test | Result |
|---|---|
| Is it implemented? | **YES — unintentionally. This is precisely the present state: five surfaces, four grains** |
| Does it satisfy `OWN-REQ-002` EXACTLY-ONE-OWNER? | **NO** — one file already has three answers |
| Does it satisfy `UCKP-INV-04` zero-ambiguity? | **NO** |
| Could precedence rescue it? | **NO** — `OWN-REQ-005` settles contests *"only by declared precedence"*, and precedence orders evidence reaching one adjudicator. Four grains do not present one subject to order |
| Verdict | **REJECTED — and identified as the defect.** Multi-level ownership is not an option to adopt; it is the condition to exit |

### 4.5 Option E — An existing constitutional model

*`UCKP-ART-02` + `ART-06`: the subject is the UCKO — the governed category of entity — and ownership is Facet 7 of it.*

| Test | Result |
|---|---|
| Does the model exist? | **YES — `UCKO`, `engine/uckp/ucko.py`, 33 facets, determination `UCOS-UCOM-001`** |
| Is ownership already a facet? | **YES — Facet 7, `REQUIRED_FACETS`, may be unattested but never absent** |
| Is it exactly one model? | **YES — `CAA` `object_model.rule`: *"Exactly ONE object model is declared repository-wide"*, measured by `CAA-INV-07`** |
| Does it satisfy `ART-02`? | **YES — by construction** |
| Does it satisfy `ART-05`? | **YES — UCKO identity is a URN** (`urn:ucos:ucko:ucos-repository:UCOS-ADR-000001`), not a path |
| Does it require a new mechanism? | **NO — `ART-18` reuse; zero create** |
| Does it subsume Options A–C? | **YES** — an authority becomes an owner *value*; a package becomes a capability's *address*; an artifact becomes a *projection* |
| Is it correctly attested today? | **NO — §1.3: wrong grain (per-object, not per-category), wrong form (58% paths), stewards 0 of 6,338** |
| Verdict | **SELECTED AS THE CANONICAL MODEL · NOT OPERATIVE** |

### 4.6 The determination

> **The canonical ownership subject is the Universal Constitutional Knowledge Object, at the grain `UCKP-ART-02` declares: the governed category of entity. Ownership is Facet 7 of that object. This is not a choice made here — it is law already in force, in code, at `engine/uckp/law.py`, with a 33-facet object model and an executable registry.**

**Three findings prevent this from being a completion:**

1. The facet is attested at the **provider-object** grain (6,338), not the **category-of-entity** grain. `ART-02` says a category exists *exactly once*; 6,338 attestations are not 6,338 categories.
2. **58% of attested owners are paths**, which `ART-04`, `ART-05` and `ART-11` each independently forbid as a source of ownership.
3. The subjects S-1 O-4 must mutate — the mutation register, the classifier, the nine mutation classes — **are not in the UCKO population at all.** Under `ART-02`, *"Nothing exists constitutionally until it has become one."*

**Option E is the answer to "what is owned?" and the answer is not yet true of the things S-1 needs to own.**

---

## 5. Infinite Scope Compatibility Assessment

### 5.1 The declared expansion axes

`UISD-000001` declares **11** expansion axes: `scope` · `direction` · `relationship` · `evolution` · `lifecycle` · `capability` · `technology` · `temporal` · `self` · `lifecycle-vocabulary` · `population`.

The governing invariants: `UCKP-INV-13` infinite-evolvability · `UCKP-INV-14` infinite-extensibility · `UCKP-INV-15` infinite-replayability · `UCKP-INV-16` infinite-discoverability · `UCKP-INV-17` infinite-auditability.

### 5.2 Option E tested against each requirement

| Requirement | Under Option E (UCKO grain) | Basis |
|---|---|---|
| **Unlimited future entities** | **SUPPORTED** — `ART-17`: *"an unknown future category is admitted by registration, never by amendment"*; `ART-08` automatic discovery, `engine/uckp/universe.py` never edited | `ART-08`, `ART-17` |
| **Unlimited future capabilities** | **SUPPORTED** — a new capability is a new provider module exposing `ucko_objects()`; the registry discovers it | `CAA.extension_rule.how_to_extend` |
| **Unlimited future laws** | **NOT SUPPORTED BY OWNERSHIP — correctly.** Law is self-grounding and not owned (§7.3). A new *article* is refused: `CAA.non_goals` — *"Adding an article… Extension is by registration"* | `ART-17`, `ART-20` |
| **Unlimited future relationships** | **SUPPORTED at instance grain** — 13,361 edges carry `UEDGE-*` identities; Facet 9 is per-object | `ART-07`; §6 |
| **Unlimited future identities** | **SUPPORTED** — one append-only mint, `CAA-INV-04`; 200 categories in `category_seq` growing by declaration | `ART-05` |
| **Unlimited future contexts** | **SUPPORTED** — `UCXI` `openness.closed_set: false`, `upper_limit: null`, `ContextTaxonomy.extend` is *"a DATA edit, not a code edit"* | `UCXI` |

### 5.3 The five prohibitions tested

| Prohibition | Option E | Present state |
|---|---|---|
| **No fixed enumeration** | **HOLDS** — 33 facets are the *description* axes, not a subject enumeration; subjects are discovered | **VIOLATED** — `UOBC.CAPABILITY_PACKAGE` is prefix-fixed to `engine/`; `test_3` of the boundary suite uses a hardcoded 5-name class set |
| **No ownership duplication** | **HOLDS** — exactly one facet, exactly one model (`CAA-INV-07`) | **VIOLATED** — five surfaces |
| **No overlapping ownership** | **HOLDS** — `OWN-REQ-002` per subject, and one subject per category under `ART-02` | **VIOLATED** — three answers for one file |
| **No hidden ownership** | **HOLDS** — Facet 7 is required and never absent | **VIOLATED** — UGA's pattern-derived owner is outside the ODF, unadjudicated |
| **No implicit ownership** | **HOLDS** — `ART-15`: no conclusion on a hardcoded assumption | **VIOLATED** — the grain is a code default; 58% of owners are locations |

### 5.4 Infinite scope finding

**Option E is the only candidate that satisfies all six unlimited-growth requirements without a fixed enumeration, and it satisfies them because the law was written for exactly this.** The present state violates all five prohibitions.

> **The gap is not that the model cannot scale. It is that the model's ownership facet is being fed by location, and location is the one input that cannot scale: `ART-05` requires identity independent of storage, and a path is storage.**

---

## 6. Relationship Ownership Assessment

### 6.1 The measured relationship surface

| Property | Value |
|---|---|
| `relationships.json` | `count: 13361`, generated `2026-08-23T13:32:47+00:00` |
| Edge form | `{"edge_id": "UEDGE-000000001", "from": "UCOS-CON-000021", "to": "UCOS-IDX-000001", "type": "Depends-On", "inverse_of": null, "note": "structural:chain"}` |
| Model owner | `UCKP-ART-07` at `engine/uckp/graph.py` — `CAA-INV-05` permits **exactly one** owner of the model |
| Object-level facet | Facet 9 `RELATIONSHIPS` — `Relationship(relation, target, relationship_class)` |
| `UISD` axes touching relationships | `relationship` · `direction` · `scope` |

**Note:** the predecessor chain recorded 12,899 edges; the current artifact declares 13,361. The population grew between snapshots, which is `ART-14` append-only behaving as declared and is recorded rather than treated as a discrepancy.

### 6.2 The four relationship ownership grains

| Grain | Is it an ownership subject? | Owner | Basis |
|---|---|---|---|
| **Relationship class** | **NO** | `UCKP-ART-07` — the model, owned by law | `CAA-INV-05`: *"One instrument declares what a relationship is"* |
| **Relationship type** (`Depends-On`, the 11 UCXI context relations) | **NO** — a vocabulary member | the model owner; `UCXI` states its 11 relations *"are instances projecting that model"* | `ART-07` |
| **Relationship instance** (`UEDGE-000000001`) | **YES** — it carries an identity | undetermined — no surface attests an owner for any edge | `ART-05` + `ART-07` |
| **Relationship identity** (the `UEDGE-*` namespace) | **NO** — allocation, not entity | the one mint; `CAA-INV-04` | `ART-05` |

### 6.3 "Infinite scopes and things with infinite scopes, things and directions"

The mission's phrasing names three unbounded dimensions at once. Tested:

| Dimension | Bounded? | Mechanism |
|---|---|---|
| **Scope** — how far a relationship reaches | **unbounded** | `UISD` axis `scope`; no upper limit declared |
| **Things** — what may be related | **unbounded** | `ART-07`: *"Every object is a node"*; `ART-08` discovery |
| **Directions** — orientation and inversion | **unbounded** | `UISD` axis `direction`; `inverse_of` present on every edge |

**All three are unbounded, and none of them multiplies the ownership grain.** A relationship instance is one entity with one identity, regardless of how many scopes, things or directions its type admits. `ART-07`'s *"every relationship is executable: a relationship that cannot be resolved is not a relationship"* is what keeps the population finite at any commit while unbounded over time.

### 6.4 Relationship ownership finding

> **Relationship ownership is two-grained and both grains are already determined: the class is owned by law (`ART-07`, exactly one owner by `CAA-INV-05`), and the instance is an identified entity whose owner is undetermined for all 13,361 edges.**

**No edge in this repository has an attested owner.** That is not a contradiction of Option E — Facet 7 permits *unattested* — but it is 13,361 subjects at the honest `UNRESOLVED` standing, and it is recorded here so that no later determination reads silence as ownership.

---

## 7. Authority and Law Ownership Assessment

### 7.1 Does authority own capability?

**NO.** Authority is Facet 5 of an object — `AuthorityBinding(tier, derives_from, instrument)`. Measured on a sample UCKO: `tier='advisory'`, `derives_from='urn:ucos:ucko:ucos:UCKP-LAW-0001'`, `instrument=''`.

A facet describes its object; it does not own a different object. And under `CAA.authority_roles`, **only `SUPREME` carries `may_hold_authority: True`** — every other role is `False`. An authority that cannot hold authority cannot own by holding it.

**Authority may be an owner *value*.** The governed assignment schema requires exactly that: *"the canonical owner (an authority, not a path)."* **Being nameable as an owner is not the same as owning by standing**, and conflating the two is the inference `OWN-REQ-001` forbids.

### 7.2 Does capability own authority?

**NO.** A capability is a governed category of entity — a UCKO. Its `authority` facet *derives from* `UCKP-LAW-0001`; it does not contain or confer it. `UCKP-INV-06` zero-circular-authority forecloses the reverse direction: if a capability owned the authority it derives under, the chain would close on itself.

**Measured confirmation:** `REPOSITORY-INTELLIGENCE` is a declared authority whose home is a capability package, and the ODF assigns that package's modules to a *different* authority label. The capability does not own the authority that lives in it.

### 7.3 Does law own itself?

**YES, and uniquely.** `CAA.supreme_authority` declares `self_grounding` and `exactly_one`: *"There is exactly ONE supreme constitutional object authority. A second instrument declaring role `SUPREME` is a competing root and is void under `UCKP-ART-03`."* `ART-01` Supremacy: its authority *"derives from itself and every other chain terminates at it."*

| Consequence | Statement |
|---|---|
| Law is not an ownership subject | It has no owner above it to be assigned |
| Law is not ownable | Assigning it an owner would create a superior — void under `ART-03` |
| `CAA-INV-01` measures this | fail-closed |
| `ART-20` Perpetual Validity | the law is technology-, repository- and implementation-agnostic |

### 7.4 Does law belong to the constitutional layer?

**Yes — and the useful finding is what follows for the mutation register.**

The register is bound in `CAA` with role `EXECUTION`, relation `PROJECTION`, deriving under `ART-10` and `ART-16`, owning *"which mutation classes exist and which authority disposes of each"*, and may never own knowledge.

| Question | Answer |
|---|---|
| Is a mutation class a governed category of entity? | **YES** |
| Should it therefore be a UCKO? | **YES — `ART-02`: *"Nothing exists constitutionally until it has become one"*** |
| Is any of the 9 mutation classes a UCKO? | **NO — none appears in the 6,338 population** |
| Does the register owning the *declaration* make the classes exist constitutionally? | **NO** — the register is a `PROJECTION`, and `ART-11` states *"Generated output never owns truth; truth originates in an object"* |

> **Nine governed categories of entity are declared in a projection and exist as no object. That is the deepest defect this determination locates, and it sits beneath every ownership question: the mutation classes are not yet things that can be owned.**

### 7.5 Is ownership derived?

| Sense | Answer |
|---|---|
| Derived from location? | **NO** — `ART-04`, `ART-05`, `OWN-REQ-001`. Yet 58% of attested owners are paths |
| Derived from authority standing? | **NO** — standing says what may be defined (§3.1 of the ownership determination) |
| Derived from registration? | **NO** — `registration` is corroborative; *"never establishes it"* |
| Derived from the object's own declaration? | **YES — this is the only constitutive route**: Facet 7 attested on the object, or a governed assignment naming it |
| Derived by inference of any kind? | **NO** — *"The framework has no code path that invents an owner"* |

---

## 8. Identity Ownership Assessment

### 8.1 The identity surface, measured

| Field | Value |
|---|---|
| `by_path` | **1,492** |
| `by_object` | **4,914** |
| `by_observation` | **7** |
| `history` | 1,492 lineages |
| `category_seq` | **200 categories** |
| `page_cursor` | 10,840 |
| `discovered_volumes` | 1 (`VOL-023`, auto-discovered, metadata-driven) |
| UCKO population | **6,338** |
| UGA population | **6,145** |

**Three index grains inside one ledger — path, object, observation — and three different totals across the ledger, UGA and the UCKO registry. No two of the three populations are the same set.**

### 8.2 The four identity ownership questions

| Question | Answer | Basis |
|---|---|---|
| **Who owns identity generation?** | The one append-only mint. `UCKP-ART-05` is the sole identity authority; `REG-AUTO-001` is the only transaction permitted to allocate, *"only under an explicit `--mint` invocation"*; `CAA-INV-04` `EXACTLY_ONE_IDENTITY_AUTHORITY` measures it | `ART-05` · mutation register invariant |
| **Who owns identity populations?** | **Nobody — and correctly.** A population is a measurement, not an entity (§2.2 incompatible grain). UGA measures it under `authority: NONE — DERIVED TRUTH` | `ART-02` |
| **Who owns identity rules?** | `UCKP-ART-05` as law, projected by the id-ledger. The `category_seq` vocabulary (200 members) grows by declaration under `ART-17` | `ART-05` · `ART-17` |
| **Does ownership conflict with identity convergence?** | **YES — at exactly one point, and it is decisive** | §8.3 |

### 8.3 The conflict with identity convergence

`ART-05`: *"Every object receives a globally unique, immutable, canonical, persistent identity that is **independent of technology, storage, repository and time**."*

| Fact | Consequence |
|---|---|
| 3,717 UCKOs (58%) carry a **path** as `ownership.owner` | ownership is bound to storage |
| `by_path` indexes 1,492 identities by location | identity is *addressed* by storage — permitted, since `by_object` exists alongside |
| The ODF resolves the ownership subject from a **basename** | the subject is derived from storage |
| `UOBC`: *"A path-derived identity is an address, not an identity, and an address changes when a file moves"* | the repository already determined this |

> **Identity convergence requires storage independence. Ownership as currently attested requires storage. Moving a file today changes 58% of the repository's ownership answers and none of its identities — which means ownership and identity currently disagree about what the thing is.**

**This is the same defect as the grain defect, seen from the identity side.** It resolves the same way and only that way: attest Facet 7 against the object's URN identity, never against its address.

---

## 9. Context / Reality / Temporal Ownership Assessment

### 9.1 Context is not an ownership axis

`UCXI-000001` bounded question: *"In which reference frame does a context resolve, what kind of context is it, and how is a kind nobody has declared yet admitted?"*

Its `does_not_own` is explicit and decisive:

> *"**permission** — CXL-10 Zero Authority: context describes; it never grants. Observation is not permission."*

**Therefore no context — spatial, temporal, reality, observer or knowledge — can confer, modify or scope ownership.** Ownership is a facet of the object; context is a different facet of the same object.

### 9.2 The five axes assessed

| Axis | UCKO facet | Ownership effect | Basis |
|---|---|---|---|
| **Spatial** | `context` (kind `spatial`) | **NONE** — describes where, grants nothing | CXL-10 |
| **Temporal** | `temporal_history` + context kind `temporal` | **NONE on the owner. Ownership is versioned, never re-scoped** — `ART-12`: *"No previous state ever changes"*; `ART-14` appends | `ART-12`, `ART-14` |
| **Reality context** | context kind `reality` | **NONE** — a frame, and `CXL-04` forbids a reference crossing a frame boundary without explicit federation | `UCXI` |
| **Observer context** | `observer_context` (Facet 32) | **NONE — and this is a security property.** An observation is *"taken outside the commit boundary, so it may never enter a canonical digest"* | `CAA.authority_roles.OBSERVATION` |
| **Knowledge context** | `knowledge_context` (Facet 31) | **NONE** — `ART-10`: execution never owns knowledge | `ART-10` |

### 9.3 The openness that must be preserved

`UCXI.openness`: `closed_set: false`, `upper_limit: null`, extension via `ContextTaxonomy.extend` — *"a DATA edit, not a code edit"*. Current kinds are declared to be *"examples not a boundary"*: existence, reality, spatial, temporal, observer, identity, knowledge, linguistic, cultural, economic, governance, security, computational, environmental, regulatory — with *"no consumer branches on a particular kind."*

**An ownership model that scoped ownership by context kind would create a consumer that branches on kind, breaking the property `UCXI` exists to hold.** Option E does not: ownership is one facet, context is another, and neither reads the other.

### 9.4 Context finding

**Ownership is context-independent, and must remain so.** Six facets carry context (`context`, `knowledge_context`, `observer_context`, `existence_context`, `governance_context`, `compliance_context`, `security_context`) and not one of them is an ownership qualifier. **Zero implicit ownership requires that no context ever be read as conferring it.**

---

## 10. API / UI / Runtime Ownership Assessment

### 10.1 These are bindings, not subjects

Three of the 33 facets are exactly the projection surfaces the mission asks about:

| Facet | Name | What it holds |
|---|---|---|
| 25 | `runtime-bindings` | how the object is reached at runtime |
| 26 | `projection-bindings` | how the object is rendered or exposed |
| 27 | `persistence-bindings` | how the object is stored |

### 10.2 The five surfaces assessed

| Surface | Grain | Ownership subject? | Basis |
|---|---|---|---|
| **API** | a `projection-binding` of a capability | **NO** — the capability is the subject | `ART-04` non-authority of representations |
| **Interface** | a contract facet of a capability | **NO** | `ART-17`: *"integrates by implementing the object contracts"* |
| **UI component** | a projection binding | **NO** — `ART-11`: documents and views *"are not authority"* | `ART-11` |
| **Runtime capability** | a **capability** — a governed category of entity | **YES — it is a UCKO** | `ART-02` |
| **Execution mechanism** | role `EXECUTION`, `may_hold_authority: False` | **NO as a subject; it is a technology** | `ART-10`: *"Execution never owns knowledge"* |

### 10.3 The invariants that make this non-negotiable

| Invariant | Effect on ownership grain |
|---|---|
| `UCKP-INV-09` zero-technology-lock-in | an ownership grain keyed to a technology would lock the model to it |
| `UCKP-INV-10` zero-repository-lock-in | **a path-keyed owner is a repository lock-in — this is the 58% finding stated as an invariant breach** |
| `UCKP-INV-11` zero-storage-lock-in | a storage-keyed owner is a storage lock-in |
| `UCKP-INV-12` zero-runtime-lock-in | a runtime-keyed owner is a runtime lock-in |
| `UCKP-INV-08` zero-projection-authority | an API, UI or document may never hold ownership authority |

### 10.4 Runtime finding

**Exactly one of the five surfaces is an ownership subject — the runtime capability — and it is a subject because it is a capability, not because it is runtime.** The other four are bindings and projections, and four separate invariants forbid each of them from holding ownership.

> **`UCKP-INV-10` zero-repository-lock-in is breached today by 3,717 attested owners. This is the same measurement as §1.3, §5.3, §8.3 and §4.3 — four sections reach it from four directions, which is what a single root cause looks like.**

---

## 11. Ownership Invariant Definition

Permanent invariants for the ownership grain. Each is derived from an article or a contract requirement already in force — **none is invented here.**

| ID | Invariant | Derived from | Measurable by |
|---|---|---|---|
| **OGI-01** | Every ownership subject is a Universal Constitutional Knowledge Object at the grain of a governed category of entity | `UCKP-ART-02` | UCKO registry membership |
| **OGI-02** | Every owned subject has **exactly one** canonical owner | `OWN-REQ-002`, `UCKP-INV-02` | per-subject owner cardinality |
| **OGI-03** | Ownership is **never** inferred from location — not from path, directory, zone, basename or repository position | `ART-04`, `ART-05`, `ART-11`, `OWN-REQ-001` | owner value form: no path-shaped owner |
| **OGI-04** | Ownership is never inferred from registration, mention or coincidence | `OWN-REQ-001` — corroborative kinds | evidence kind of every attested owner |
| **OGI-05** | Ownership is never duplicated: one subject, one attestation, one surface of record | `ART-03`, `UCKP-INV-03` | cross-surface owner comparison |
| **OGI-06** | Ownership never overlaps: no subject resolves under two grains | `UCKP-INV-04` zero-ambiguity | grain of every attestation |
| **OGI-07** | Ownership is never assumed: an unattested facet yields an honest `UNRESOLVED`, never a default | `ART-06`, `UNASSIGNED_OWNER` *"Never a real owner"* | standing distribution |
| **OGI-08** | An owner value is an authority, never a path | governed assignment schema | owner value form |
| **OGI-09** | Ownership is storage-, technology-, runtime- and repository-independent | `UCKP-INV-09…12` | owner value form |
| **OGI-10** | Ownership is context-independent: no context confers, scopes or qualifies it | `CXL-10` *"context describes; it never grants"* | no context term in any owner value |
| **OGI-11** | Ownership is append-only and versioned; a prior ownership state never changes | `ART-12`, `ART-14` | lineage monotonicity |
| **OGI-12** | Law is not owned; it is self-grounding and exactly one | `ART-01`, `CAA-INV-01` | `SUPREME` cardinality |
| **OGI-13** | A projection never holds ownership authority | `ART-11`, `UCKP-INV-08` | role of every attesting instrument |
| **OGI-14** | The ownership grain is declared as data, never defaulted in code | `ART-15`, `OwnershipGranularity` docstring | presence of a declared granularity |
| **OGI-15** | A future entity kind is admitted by registration, never by amending the grain | `ART-17`, `UCKP-INV-14` | no fixed subject enumeration |

### 11.1 Present conformance

| Invariant | State at baseline |
|---|---|
| OGI-01 | **FAIL** — the register, the classifier and 9 mutation classes are not UCKOs |
| OGI-02 | **FAIL** — three answers for one file |
| OGI-03 | **FAIL** — 3,717 path-shaped owners (58%) |
| OGI-04 | **FAIL** — UGA's pattern-derived owner is location-derived |
| OGI-05 | **FAIL** — five surfaces of record |
| OGI-06 | **FAIL** — four grains |
| OGI-07 | **PASS** — the ODF returns honest `UNRESOLVED`; `UNASSIGNED` guarded at construction |
| OGI-08 | **FAIL** — UGA records a path as the classifier's owner |
| OGI-09 | **FAIL** — `UCKP-INV-10` breached by the 58% |
| OGI-10 | **PASS** — no context term appears in any owner value |
| OGI-11 | **PASS** — `history` is append-only, 1,492 lineages |
| OGI-12 | **PASS** — exactly one `SUPREME`, self-grounding |
| OGI-13 | **PASS** — no projection asserts ownership authority; the register disclaims it |
| OGI-14 | **FAIL** — the grain is a code default |
| OGI-15 | **PARTIAL** — `UOBC` fixes `CAPABILITY_PACKAGE` to `engine/` |

**Conformance: 5 pass · 9 fail · 1 partial, of 15.**

---

## 12. Ownership Resolution Dependency Graph

### 12.1 Current

```
CURRENT — four grains, no adjudicator, no subject

  UCKP-LAW-0001 (SUPREME · self-grounding · engine/uckp/law.py)
        │  ART-02 category-of-entity · ART-06 all 33 facets required
        ▼
  UCKO object model (engine/uckp/ucko.py · Facet 7 = ownership)
        │
        │  attested at the PROVIDER-OBJECT grain, not the category grain
        ▼
  6,338 objects · 277 owner values · 3,717 PATH-SHAPED (58%) · 0 stewards
        │
        ╞═══ S-2 UGA ──── 6,145 objects · path grain ──── NONE-tier measurement
        ╞═══ S-3 ODF ──── basename grain ──── 0 assignments ──── zone labels
        ╞═══ S-4 UOBC ─── constitutional-object grain ─── engine/ only
        ╘═══ S-5 register ─ artifact-self-declared Authority prose
        │
        ▼
  NO CROSSWALK · OWN-REQ-002 untestable · UCKP-INV-04 breached
        │
        ▼
  "who owns it?"  ──►  UNANSWERABLE
        │
        ▼
  the mutation register · the classifier · 9 mutation classes
  ARE NOT UCKOs  ──►  ART-02: not constitutionally existent
        │
        ▼
  S-1 O-4 convergence  ──►  BLOCKED
```

### 12.2 Future

```
FUTURE — one grain, one facet, one adjudicator

  UCKP-LAW-0001 (unchanged · no article added · ART-17 registration only)
        │
        ▼
  G-1  DECLARE THE GRAIN AS DATA
       "the ownership subject is the UCKO at the ART-02 category grain"
       reuse UOBC's vocabulary · create no second vocabulary · OGI-14
        │
        ▼
  G-2  ADMIT THE MISSING CATEGORIES AS UCKOs
       mutation class · classification rule · the register itself
       by REGISTRATION (ART-17 · ART-08 discovery) · never by amendment · OGI-01
        │
        ▼
  G-3  RE-ATTEST FACET 7 AGAINST URN IDENTITY
       owner is an authority, never a path · OGI-03 · OGI-08 · OGI-09
       3,717 path-shaped attestations become UNRESOLVED — honestly (OGI-07)
        │
        ├──────────────┬──────────────────┐
        ▼              ▼                  ▼
  G-4 declare the   G-5 rule on UGA   G-6 rule on the
  crosswalk, or     as corroborative   ODF basename
  orthogonality,    (not constitutive) subject derivation
  of the 5 owner    OGI-04             OGI-03
  vocabularies
  OGI-05 · OGI-06
        │              │                  │
        └──────┬───────┴──────────────────┘
               ▼
  G-7  ONE ADJUDICATOR — every surface's evidence reaches the ODF
       so OWN-REQ-005 can settle by declared precedence · OGI-02
               ▼
  "what is owned?"  ──►  ANSWERED  (this is the grain)
               ▼
  predecessor OA-1…OA-6  ──►  now specifiable
               ▼
  predecessor AA-1…AA-6  ──►  now specifiable
               ▼
  O-4 register half + source half (atomic)  ──►  EXECUTABLE
```

### 12.3 The dependency statement

| Current root | Future root |
|---|---|
| `OA-1` — declare the ownership subject grain (canonical ownership determination) | **`G-1` — declare that the grain is the UCKO at the `ART-02` category grain** |
| Depth beneath O-4 | **3 layers**: G-1…G-7 → OA-1…OA-6 → AA-1…AA-6 → O-4 |

**`G-2` is the finding that was not visible before this determination.** The predecessor chain assumed the subjects existed and lacked owners. Measured: **three of the subjects S-1 O-4 must mutate do not exist as constitutional objects at all**, so there is nothing for an owner to be assigned to. `ART-02` is explicit — *"Nothing exists constitutionally until it has become one."*

---

## 13. Required Ownership Actions

Seven actions. **Zero discharged.** None is an engineering act; none may be performed by any step of O-4.

### 13.1 Required declarations

| ID | Declaration | Required of | Satisfies |
|---|---|---|---|
| **G-1** | The ownership subject grain, as data: the UCKO at the `ART-02` governed-category-of-entity grain. Reuse `UOBC-000001`'s existing grain vocabulary; declare no second one | the object-model owner (`UCOS-UCOM-001`) with the Truth-policy owner | `OGI-14`, `OGI-06` |
| **G-2** | Registration of the missing governed categories as UCKOs — mutation class, classification rule, and the register as an object rather than only a projection — by registration under `ART-17`, never by amendment | the capability owner, via `ucko_objects()` discovery | `OGI-01` |
| **G-4** | The crosswalk among the five owner vocabularies — UCKO facet values, UGA tokens, zone-authority labels, register disposing parties, artifact self-declared Authority — **or** a declaration of orthogonality with the reason stated | `UCOS-CAA-001`'s owner | `OGI-05`, `OGI-06` |

### 13.2 Required evidence

| ID | Evidence | Form | Satisfies |
|---|---|---|---|
| **G-3** | Facet 7 re-attested against URN identity, with an authority-shaped owner value. The 3,717 path-shaped attestations become honest `UNRESOLVED` rather than being rewritten into a new guess | constitutive `declared-assignment` or `declared-identity` evidence, authority-bound and evidence-cited (`OWN-REQ-006`, `007`) | `OGI-03`, `OGI-08`, `OGI-09` |
| **G-7** | Every surface's ownership evidence presented to one adjudicator, so `OWN-REQ-005` can settle contests by declared precedence rather than by invisibility | provider registration into the ODF | `OGI-02`, `OGI-05` |

### 13.3 Required authority decisions

| ID | Decision | Required of | Satisfies |
|---|---|---|---|
| **G-5** | Whether UGA's pattern-derived owner (`uga-declaration.json:115` → `uga_engine.py:222`) is corroborative or constitutive. It is presently neither declared nor adjudicated | `UCOS-UGA-001`'s owner | `OGI-04` |
| **G-6** | Whether the ODF may derive an ownership subject from a basename, given `OGI-03`. If not, the `DefinitionalLocatorProvider`'s subject rule is superseded by the grain `G-1` declares | the ownership framework owner (`UCOS-UOF-001`) | `OGI-03` |

### 13.4 Discharge state

| ID | State |
|---|---|
| G-1 | **NOT DISCHARGED** — no granularity declared in any JSON |
| G-2 | **NOT DISCHARGED** — 0 of 9 mutation classes are UCKOs |
| G-3 | **NOT DISCHARGED** — 3,717 path-shaped attestations stand |
| G-4 | **NOT DISCHARGED** — 0 shared members across five vocabularies |
| G-5 | **NOT DISCHARGED** — no ruling located |
| G-6 | **NOT DISCHARGED** — no ruling located |
| G-7 | **NOT DISCHARGED** — UGA and the UCKO facet are outside the ODF |

**0 of 7.** Combined with the predecessor chain: **0 of 19** actions across grain, ownership and authority are discharged.

### 13.5 What no action creates

| Not created by any action above | Why |
|---|---|
| A new object model | `CAA-INV-07` — exactly one, repository-wide |
| A new facet | 33 required facets already include ownership |
| A new ownership framework | `UCOS-UOF-001` exists and is correct |
| A new registry, catalogue or provider vocabulary | `CAA.extension_rule.what_this_forbids` |
| A new article or invariant in `engine/uckp/law.py` | `CAA.non_goals`; `ART-17` — extension by registration |
| An authority | zero authority creation |

**Seven actions, zero mechanisms created.** Every one is a declaration, an attestation or a ruling over machinery that already exists.

---

## 14. Forbidden Actions

| # | Forbidden | Basis |
|---|---|---|
| **FG-01** | **Guessed ownership** — naming any owner for any subject before `G-1` | `OWN-REQ-001`; *"never a licence to guess"* |
| **FG-02** | **Temporary ownership** — a provisional owner, placeholder, or "owner pending determination" | zero temporary solutions; `ART-12` no prior state changes |
| **FG-03** | **Engineering-created ownership** — any step of O-4 attesting Facet 7, populating the catalogue, or declaring a grain | `OWN-REQ-001` requires a governed determination |
| **FG-04** | **A duplicate ownership catalogue** — a second assignment file, a per-programme owner registry, an owner column in any register | `ART-03`, `ART-18`, `CAA.extension_rule.what_this_forbids` |
| **FG-05** | **A parallel ownership model** — a second grain running beside the UCKO grain, including "legacy path ownership" preserved for compatibility | `ART-03`: a second definition of an existing primitive is void; zero duplicate |
| **FG-06** | Rewriting the 3,717 path-shaped attestations into new values without `G-1` and `G-3` | replacing one guess with another; `OGI-07` requires honest `UNRESOLVED` |
| **FG-07** | Deriving ownership from path, directory, zone, basename or repository position | `OGI-03`; `UCKP-INV-10` |
| **FG-08** | Deriving ownership from registration, mention or coincidence | `OGI-04`; corroborative kinds *"never establish it"* |
| **FG-09** | Deriving ownership from context — spatial, temporal, reality, observer or knowledge | `CXL-10`; `OGI-10` |
| **FG-10** | Reading CAA authority standing as a right to own or mutate | standing answers what may be defined |
| **FG-11** | Assigning an owner to a law, a scope, a domain or an identity population | `OGI-12`; §2.2 incompatible grains |
| **FG-12** | Amending `engine/uckp/law.py`, its articles, invariants or facet set to accommodate a grain | `CAA.non_goals`; `ART-17` |
| **FG-13** | Adding a mutation class, rule or object kind by amendment rather than registration | `ART-17`; `OGI-15` |
| **FG-14** | Accepting the code-default `AUTHORITY` granularity as the declared grain | `ART-15`; `OGI-14` |
| **FG-15** | Fixing the grain by inserting the first catalogue entry | `OWN-REQ-005` — never by insertion order |
| **FG-16** | Treating this determination as the governed determination `G-1` requires | authority `NONE (DERIVED TRUTH)`; it resolves `EVIDENCE-NOT-IN-CANONICAL-HOME-ZONE` |
| **FG-17** | Treating an unattested facet as ownership by default | `ART-06`; `UNASSIGNED` *"Never a real owner"* |
| **FG-18** | Presenting any part of this as closure, certification or ratification | `UCERT_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"` |

---

## 15. Final Ownership Grain Verdict

### 15.1 The question

> What exactly is owned?

### 15.2 The answer

**The governed category of entity, existing exactly once as a Universal Constitutional Knowledge Object, carrying ownership as Facet 7 of 33.** This is `UCKP-ART-02` with `UCKP-ART-06`, in executable law at `engine/uckp/law.py`, with the object model at `engine/uckp/ucko.py` and the determination at `UCOS-UCOM-001`.

### 15.3 The classification

# NOT COMPLETE

**No optimistic upgrade is available, and three independent measurements each independently prevent one.**

| Why not COMPLETE | Measurement |
|---|---|
| The grain is not declared | no JSON declares an ownership granularity; the running grain is a Python default |
| The subjects do not exist as objects | 0 of 9 mutation classes, and neither the register nor the classifier, appear in the 6,338 UCKO population |
| The attestation is in a forbidden form | **3,717 of 6,338 owners (58%) are path-shaped**; `OGI-03`, `OGI-08`, `OGI-09`, `UCKP-INV-10` |
| Invariant conformance | **9 of 15 FAIL**, 1 partial |
| Actions discharged | **0 of 7** — and 0 of 19 across the full chain |
| Adjudication | five surfaces, no adjudicator; `OWN-REQ-002` untestable |

### 15.4 Why CONDITIONALLY COMPLETE is refused

A conditional classification would be defensible if the only gap were a missing declaration over correct data. It is not:

> **The data is attested at the wrong grain and in a form four invariants forbid. `G-1` alone would not make ownership correct; it would make 3,717 attestations measurably wrong instead of ambiguously wrong. That is progress in auditability and not a completion, and calling it conditional completeness would convert a measurement into an expectation.**

### 15.5 Verdict by question

| Question | Verdict |
|---|---|
| Is the canonical ownership grain determinable? | **YES — the law determines it** |
| Is it declared? | **NO** |
| Is a new model required? | **NO — `ART-18`, zero create** |
| Do the S-1 subjects exist as ownership subjects? | **NO** |
| Is the present attestation lawful? | **NO — 9 of 15 invariants fail** |
| Is "who owns it?" answerable? | **NO — and it must not be attempted** |
| Is any owner named here? | **NO** |
| Is any authority created here? | **NO** |
| May S-1 O-4 proceed? | **NO** |
| Grain classification | **NOT COMPLETE** |
| Closure | **NOT CLAIMED** |

### 15.6 The determination stated precisely

The repository does not lack an ownership model. It has one, in law, with ownership as a required facet of a single declared object model, and it is compatible with every unlimited-growth requirement the mission names — unlimited entities, capabilities, laws, relationships, identities and contexts — because `ART-17` admits the unknown by registration and `ART-08` discovers it without an edit.

What the repository lacks is the declaration that the model's grain **is** the ownership grain, and the attestation of that facet against identity rather than against location. **Fifty-eight per cent of its attested ownership is a directory path, and the nine categories S-1 must govern are declared in a projection and exist as no object at all.**

> **"What exactly is owned?" is answered by law and is not answered by the repository. Until the grain is declared and the missing categories are registered, "who owns it?" is not a question that has a subject — and any answer to it would be a guess with a name.**

**GRAIN: NOT COMPLETE. NO OWNER NAMED. NO GRAIN DECLARED. CLOSURE NOT CLAIMED.**

# VERDICT: NOT COMPLETE

---

## 16. Verification Record

### 16.1 Baseline captured before analysis

| Field | Value |
|---|---|
| HEAD | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch | `integration/recovery-001` |
| Commits | 515 |
| Porcelain total | 377 |
| Tracked modified | 38 |
| Untracked | 339 |
| Target artifact | **absent at capture** |

**Protected surface hashes at capture (SHA-256):**

| Surface | Digest |
|---|---|
| `platform/universal_ownership/catalog/ucos-ownership-declarations.json` | `96aa2be264…95146cd` |
| `00-BOOK/DATA/constitutional-authority-alignment.json` | `aef7b81c1e…8e71b5c5` |
| `00-BOOK/DATA/mutation-governance-boundary.json` | `a7c8171518…ca5a89ee` |
| `platform/universal_truth/catalog/ucos-repository-truth.json` | `cdc0f7c0cf…aec7be05` |
| `platform/repository_intelligence/mutation_classification.py` | `54ecc7e2c4…dd6def3c` |
| `platform/repository_intelligence/mutation_class_extension.py` | `9a742a7629…bb5db572` |
| `00-BOOK/DATA/id-ledger.json` | `ea630db9c8…78698150` |
| `00-BOOK/DATA/relationships.json` | `31c19f2df2…b46053` |
| `00-MASTER/UOBC-000001/birth-scope-policy.json` | `bf15620fc8…650e17d` |

**Input artifacts:** 1,002 · 866 · 835 lines.

### 16.2 Read-only measurements taken for this determination

| ID | Measurement | Surface | Write? |
|---|---|---|---|
| **G-M1** | `UCKP-LAW-0001` declares 20 articles and 17 invariants; `ART-02` grain is the *"governed category of entity"*; `ART-06` requires every facet | `engine/uckp/law.py` | **NO** |
| **G-M2** | `Facet` enum holds **33** members; `OWNERSHIP` is the 7th; `REQUIRED_FACETS = tuple(Facet)` — all required | `engine/uckp/facets.py` | **NO** |
| **G-M3** | `Ownership(owner: str, stewards: tuple)` — *"Who is accountable for an object (Facet 7)"*; no authority field, no locator, no evidence field | `engine/uckp/values.py:215` | **NO** |
| **G-M4** | UCKO registry `discover()` → **6,338** objects; identity form `urn:ucos:ucko:<ns>:<local>`; sample `authority` = `AuthorityBinding(tier='advisory', derives_from='urn:…UCKP-LAW-0001', instrument='')` | `engine/uckp/registry.py` | **NO** |
| **G-M5** | `ownership.owner`: **277** distinct values; top values `00-BOOK/PORTAL` (1,240), `platform/tests` (345), `engine/tests` (288), `UCOS-REPOSITORY-ROOT` (286), `ucos-constitutional-authority` (193) | UCKO population | **NO** |
| **G-M6** | **Path-shaped owners: 3,717 of 6,338 (58%)**; token-shaped 2,621; **`stewards` = 0 for all 6,338** | UCKO population | **NO** |
| **G-M7** | `CAA.object_model`: model `UCKO`, home `engine/uckp/ucko.py`, article `UCKP-ART-02`, facets 33, rule *"Exactly ONE object model is declared repository-wide"*, measured by `CAA-INV-07` | `CAA-001` | **NO** |
| **G-M8** | `id-ledger.json`: `by_path` 1,492 · `by_object` 4,914 · `by_observation` 7 · `history` 1,492 · `category_seq` **200** · `page_cursor` 10,840 · `discovered_volumes` 1 | id ledger | **NO** |
| **G-M9** | `relationships.json`: `count` **13,361**, generated `2026-08-23T13:32:47+00:00`; edge form carries `edge_id` `UEDGE-*`, `from`, `to`, `type`, `inverse_of` | relationship data | **NO** |
| **G-M10** | `UISD-000001` declares **11** expansion axes: scope · direction · relationship · evolution · lifecycle · capability · technology · temporal · self · lifecycle-vocabulary · population | `uisd-declaration.json` | **NO** |
| **G-M11** | `UCXI-000001`: `openness.closed_set: false`, `upper_limit: null`, extension *"a DATA edit, not a code edit"*; `does_not_own` includes *"permission — CXL-10 Zero Authority: context describes; it never grants"*; 15 example context kinds, *"not a closed list"* | `ucxi-declaration.json` | **NO** |
| **G-M12** | `UOBC-000001`: `CAPABILITY_PACKAGE` granularity `package`, selector `path_prefix: engine/`; `DETERMINATION` granularity `document`, adoption **DEFERRED**, gap G11; `ADDRESSED_OBJECT` catch-all totality guarantee; policy `authority: NONE — DERIVED TRUTH` | `birth-scope-policy.json` | **NO** |
| **G-M13** | **No JSON in the repository declares an ownership granularity**; the running grain is `DefinitionalLocatorProvider(granularity=AUTHORITY)` | grep over tracked JSON | **NO** |
| **G-M14** | The mutation register, `mutation_classification.py` and all 9 mutation classes are **absent from the 6,338 UCKO population** | UCKO population | **NO** |
| **G-M15** | `UCOS-UCOM-001-UNIVERSAL-CONSTITUTIONAL-OBJECT-MODEL-DETERMINATION.md` exists at repository root — in zone `derived.root-determinations`, authority `''`, `is_home=False` | filesystem · truth policy | **NO** |

**No measurement mutated anything. The UCKO registry `discover()` call is a read of provider modules; no mint, no write, no attestation was performed. `extend_mutation_governance_boundary()` was not called. No ownership was assigned.**

### 16.3 Findings contributed beyond the predecessor chain

| # | Finding | Status |
|---|---|---|
| **Z-1** | Ownership is already a **required facet** of the one declared object model — Facet 7 of 33 | **new** |
| **Z-2** | A **fifth** ownership surface exists: the UCKO facet, 6,338 subjects, larger than any other | **new** |
| **Z-3** | **58% of attested ownership is path-shaped**, breaching `UCKP-INV-10` zero-repository-lock-in | **new** |
| **Z-4** | `stewards` is unattested for all 6,338 objects | **new** |
| **Z-5** | The mutation register, the classifier and all 9 mutation classes **are not UCKOs** — under `ART-02` they do not exist constitutionally | **new · deepest defect located** |
| **Z-6** | The grain question is answered by law (`ART-02` + `ART-06`) and requires no new model | **new** |
| **Z-7** | Twelve of the mission's fifteen candidate grains are not ownership subjects; the three that are collapse into one | **new** |
| **Z-8** | Relationship ownership is two-grained; **0 of 13,361 edges** has an attested owner | **new** |
| **Z-9** | Context can never confer ownership — `CXL-10`, and six context facets confirm it | **new** |
| **Z-10** | API / UI / interface / execution are bindings, not subjects; four invariants forbid each from owning | **new** |

**The predecessor chain's root was `OA-1` (declare the grain). This determination places `G-1` and `G-2` beneath it, and `G-2` is a new class of blocker: the subjects do not exist as objects.**

### 16.4 Artifact identity

| Field | Value |
|---|---|
| Path | `UCOS-OMEGA-INFINITY-S-1-OWNERSHIP-GRAIN-DETERMINATION.md` |
| Status | Untracked — new artifact |
| Required sections | **16** |
| Verdict | **NOT COMPLETE** |
| Canonical grain identified | UCKO at the `UCKP-ART-02` category-of-entity grain (Option E) |
| Grain declared | **NO** |
| Invariants defined | **15** (`OGI-01`…`OGI-15`) · conformance **5 pass · 9 fail · 1 partial** |
| Actions required | **7** (`G-1`…`G-7`) · discharged **0** |
| Owners named | **0** |
| Authorities created | **0** |
| Closure claimed | **NO** |
| Authority | **NONE (DERIVED TRUTH)** |
| Implementation performed | **NONE** |

### 16.5 Mutation boundary

| Surface | State |
|---|---|
| Source code | **UNCHANGED** — no `.py` written |
| JSON | **UNCHANGED** — no `.json` written |
| Ownership declarations | **READ ONLY** — still **0 assignments** |
| Constitutional authority alignment | **READ ONLY** |
| Mutation governance boundary | **READ ONLY** |
| Repository truth policy | **READ ONLY** — still 12 zones |
| Mutation classifier | **READ ONLY** — `RULE_PREDICATES` still 8 entries |
| Rival mutation module | **READ ONLY** — not deleted, its mutator not invoked |
| Identity ledger | **UNCHANGED** — no mint, no serial consumed; `by_path` 1,492 · `by_object` 4,914 |
| Relationship data | **UNCHANGED** — `count` 13,361; no edge added, removed or retyped |
| UCKO facet attestations | **UNCHANGED** — 6,338 objects, 3,717 path-shaped owners, 0 stewards |
| Law · articles · invariants · facets | **UNCHANGED** — 20 · 17 · 33 |
| Certifications | **UNCHANGED** — none issued |
| Predecessor determinations | **UNCHANGED** — 1,002 · 866 · 835 lines |
| Commits · tags · pushes · stash | **NONE** |

### 16.6 Verification checklist

Executed after this artifact was written. Reproducible against baseline `bae59755d7e2d3566c93b89c722b68847145269a` on branch `integration/recovery-001`.

| Check | Requirement |
|---|---|
| Artifact exists | yes |
| Section count | **16** — headings `## 1.`…`## 16.`, contiguous |
| Line count | recorded in the accompanying verification output |
| Only one new artifact | 1 new untracked entry vs baseline (377 → 378) |
| HEAD unchanged | `bae59755…` |
| Branch unchanged | `integration/recovery-001` |
| Commit count unchanged | 515 |
| Tracked modifications unchanged | 38 |
| No code changes | no `.py` delta; all protected digests match |
| No registry changes | no `.json` delta; all protected digests match |
| No identity changes | `id-ledger.json` digest unchanged |
| No relationship changes | `relationships.json` digest unchanged |
| No ownership changes | `assignments` still `{}` |
| No commits | HEAD and count unchanged |
| **Reversible** | nothing was written outside the new artifact, so nothing requires reverting |

---

**END UCOS Ω∞ — S-1 OWNERSHIP GRAIN DETERMINATION**

**Verdict:** **NOT COMPLETE**
**Canonical grain:** the UCKO at the `UCKP-ART-02` governed-category-of-entity grain · ownership is Facet 7 of 33 · **Option E, an existing constitutional model**
**Grain declared:** **NO** · **Owners named:** 0 · **Authorities created:** 0 · **Mechanisms created:** 0
**Ownership surfaces:** 5 · grains: 4 · crosswalks: **0**
**UCKO population:** 6,338 · owner values 277 · **path-shaped 3,717 (58%)** · stewards **0**
**Constitutionally non-existent S-1 subjects:** the register · the classifier · **9 of 9 mutation classes**
**Relationship instances with an attested owner:** **0 of 13,361**
**Invariants defined:** 15 · **conformance 5 pass · 9 fail · 1 partial**
**Actions required:** 7 (`G-1`…`G-7`) · **discharged 0** · chain total **0 of 19**
**Zero fixes · Zero patches · Zero shortcuts · Zero temporary solutions · Zero duplicate · Zero overlapping** — all honoured
**100% systematic · authentic · auditable · secured · traceable · reversible** — every finding digest-anchored; nothing written
**OWNERSHIP:** not assigned · **GRAIN:** not declared · **AUTHORIZATION:** not claimed · **CLOSURE:** not claimed
**Authority:** NONE (DERIVED TRUTH) — declares no grain, assigns no owner, creates no authority, ratifies nothing

*This determination modified no code, no JSON, no predicate, no registry, no policy, no facet, no article, no invariant, no identifier, no relationship, no ownership attestation and no authority binding. It named no owner, declared no grain, registered no object, and discharged none of the seven actions it enumerates. The 3,717 path-shaped ownership attestations it measured stood before this determination was written and stand unchanged after it.*
