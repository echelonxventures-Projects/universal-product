# UCOS Ω∞ — EEG-1 / EEG-2 EVOLUTION EXTENSIBILITY CLOSURE DETERMINATION

**The permanent resolution for the two extensibility failures. The measured answer is that they are one architectural pattern failure on two planes, that the pattern which closes them already exists and was already applied five times, and that one half of EEG-2 hits a representational limit this repository has already located and deferred to its own determination.**

| Field | Value |
|---|---|
| Artifact | `UCOS-OMEGA-INFINITY-EEG-1-EEG-2-EVOLUTION-EXTENSIBILITY-CLOSURE-DETERMINATION.md` |
| Authority | **NONE — DERIVED DETERMINATION.** Vests no authority, amends no law, ratifies nothing, registers nothing, implements nothing. It measures two defects, locates the mechanism that closes them, proves the closure is feasible without changing anything, and reports what remains genuinely open. |
| Mode | ANALYSIS ONLY · **NO CODE CHANGE · NO JSON CHANGE · NO REGISTRY CHANGE · NO IDENTITY · NO OWNERSHIP · NO CERTIFICATION · NO COMMIT** |
| Baseline commit (HEAD) | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Baseline branch | `integration/recovery-001` |
| Subjects | `EEG-1` — location axis extensibility failure · `EEG-2` — closed-enum extensibility failure at the interface plane |
| Predecessor | `UCOS-OMEGA-INFINITY-ETERNAL-EVOLUTION-GOVERNANCE-CONSTITUTION-DETERMINATION.md` §12, §15, §17 — raised both gaps |
| Governing precedent | **`CEP-MOD-002-UNIVERSAL-STRUCTURAL-VOCABULARY-MIGRATION-DETERMINATION.md`** — the same defect class, resolved five times (M-1…M-5), with backward-compatibility, rollback, replay and certification impact already determined |
| Method | Read-only measurement plus **four in-memory feasibility probes** that construct candidate vocabularies, verify lossless reconstruction, and exercise `INV-14` admission. Nothing was written; `git status --porcelain` is **359** before and after |
| **Central finding** | **`EEG-1` and `EEG-2` are one defect: a bounded population held as a module literal, outside `VocabularyRegistry`, therefore outside `_probe_infinite_extensibility`'s loop and invisible to `UCKP-INV-14`.** The mechanism that closes it exists entire and requires no invention — §4, §5 |
| **Second finding** | **`EEG-2` is larger than the predecessor recorded.** It is not two enums. It is **five closed enums and two total mappings** across three packages — §3 |
| **Third finding** | **The two are not equally closable.** `EEG-1`'s internal structure is representable in `Vocabulary`/`Term` and was **proved so in memory** (§6.4). `EEG-2`'s two mappings are inter-vocabulary relations, and `Vocabulary` has no representation for one — the exact limit `CEP-MOD-002` §12.2 deferred as *"requires its own determination"* — §8.5 |
| Dispositions | **REUSE ×2 · EXTEND ×3 · CREATE ×0 · CEP-REFERRAL ×1** — §12.2 |
| Verdict | **EEG-1 — PERMANENTLY CLOSABLE, READY. EEG-2 — PERMANENTLY CLOSABLE IN PART; ITS MAPPING HALF IS A LOCATED CONSTITUTIONAL QUESTION, NOT AN ENGINEERING TASK** — §13 |
| Preserved | No new registry · no new identity system · no new authority · no parallel evolution framework · no patch · no special case · no temporary exception |

---

## 1. Executive Determination

### 1.1 The question

*What is the permanent constitutional and architectural resolution for `EEG-1` and `EEG-2`, such that any future entity type, location model, reality context, interface representation, capability or knowledge type is admitted through governed data evolution without core engine modification?*

### 1.2 The answer, in one paragraph

**The resolution is not new. It is `CEP-MOD-002` applied to two further sites.** That determination established the single migration — *"Every downstream engine shall **contribute** its structural vocabulary to `engine/uckp/vocabulary.py::VocabularyRegistry` and **retain** its existing local type as a checked projection guarded by `verify_vocabulary_alignment`, which shall fail closed"* — and executed it five times. `verify_vocabulary_alignment()` now exists, guards **9 projections**, and **passes live at this baseline**. `EEG-1` and `EEG-2` are two populations that were not in that migration's scope. Bringing them in is `REUSE` of a proven mechanism, not `CREATE`.

### 1.3 The four determinations

| # | Determination | Basis |
|---|---|---|
| **D-1** | `EEG-1` and `EEG-2` are **one architectural pattern failure**, not two defects | §4 — identical shape, identical cause, identical remedy class |
| **D-2** | The remedy requires **no new mechanism**. Every field, type, guard and probe needed already exists and is exercised | §5 — `Vocabulary`, `Term`, `VocabularyRegistry.extend`, `verify_vocabulary_alignment`, `_probe_infinite_extensibility` |
| **D-3** | `EEG-1` is **fully resolvable** by the pattern. Proved in memory: a 19-term candidate vocabulary reconstructs `AXIS_GRAPH` **losslessly** and admits an unknown future member | §6.4 |
| **D-4** | `EEG-2` is **resolvable in its term-set half and blocked in its mapping half.** `_ENTITY_GROUP` and `_SURFACE_TABLE` are total functions between two term sets, and `Vocabulary` has no representation for a relation between vocabularies. This is `CEP-MOD-002` §12.2's `_CATEGORY_LAYER` case, verbatim | §8.5 |

### 1.4 What "permanent" means here, stated precisely

The directive requires that no future admission need core engine modification. That target is achieved **after** the migration, not by it:

| Phase | Plane | Is it code? |
|---|---|---|
| The one-time contribution of each population to the registry | Engine, additive | **Yes — once, per population** |
| Every subsequent admission of a future member | DATA — `VocabularyRegistry.extend()` | **No — permanently** |

**This is not a patch and not an exception.** It is the same one-time-code / permanent-data trade `CEP-MOD-002` made five times, and it is the only shape under which `UCKP-ART-17` — *"an unknown future category is admitted by registration, never by amendment"* — becomes true rather than asserted. A resolution that avoided all code would have to leave the populations where they are, which is the defect.

### 1.5 What this determination refuses to do

| Refused | Why |
|---|---|
| A new registry | `UCKP-ART-18`; `VocabularyRegistry` is the located owner. `what_this_forbids` names *"a second registry"* |
| A new identity system | `CAA-INV-04` — one append-only mint. Frame identity already flows through `deterministic_id(RegistryKind.LOCATION, …)` |
| A new authority system | `CAA-INV-01` — SUPREME is `EXACTLY_ONE` |
| A parallel evolution framework | `what_this_forbids` names *"a second … evolution system standing beside the ones that exist"* |
| A patch, exception or special case | The directive's stated principle, and `CMG-000001` LXXVI.6 — *"Reinterpretation is invisible to validation; admission is visible"* |
| Extending `Term` to carry the mapping | It would be a Layer Zero change made to fit one consumer — precisely what `how_to_extend[2]` forbids. §8.5 refers it instead |

---

## 2. EEG-1 Current State Analysis

### 2.1 The location axis model, measured

| Field | Measured at HEAD |
|---|---|
| Home | `engine/context/location.py` |
| Declaration | `AXIS_DERIVATION` — an ordered `tuple` of `(axis, requires)` pairs |
| Derived form | `AXIS_GRAPH: Mapping[str, tuple[str, ...]] = dict(AXIS_DERIVATION)` — line **119** |
| Its own comment | *"``axis → requires`` in the shape the single ordering authority consumes."* |
| Axes | **19** |
| Derivation edges | **29** |
| Roots (require nothing) | **1** — `existence` |
| Leaves (nothing derives from them) | **4** — `observer`, `spatial`, `temporal`, `execution-context` |
| Multi-parent axes | **6** |
| Reality context axes | **5** — `existence`, `reality`, `observer`, `spatial`, `temporal` |
| Reference frames registered in DATA | **14** |
| `frame_kind` | **Open string** — *"Nothing in this module tests it… an unknown kind costs nothing"* |

### 2.2 The nineteen axes

```
existence          ← ()                          [root]
reality            ← existence
observer           ← reality                     [leaf]
civilization       ← reality
universe           ← reality
location           ← universe, civilization      [multi-parent]
spatial            ← location                    [leaf]
temporal           ← location, time-standard     [multi-parent, leaf]
jurisdiction       ← location
governance         ← jurisdiction
calendar           ← location
time-standard      ← location
language           ← location
units              ← location
currency           ← location, units             [multi-parent]
regulation         ← jurisdiction
tax                ← jurisdiction, currency      [multi-parent]
policy             ← governance, regulation      [multi-parent]
execution-context  ← policy, calendar, time-standard, language,
                     currency, units, tax        [multi-parent, leaf]
```

### 2.3 Why it violates the infinite-extension principle

| Test (§3.3 of the predecessor, = `UCKP-INV-14` per population) | Result |
|---|---|
| Is the population held by a registry? | **No.** A module-level `Mapping`, built at import |
| Does it expose an admission operation? | **No.** No `extend`, no `register`, no `from_declaration` |
| Is it registered in `VocabularyRegistry`? | **No.** `build_vocabulary_registry()` seeds **13**; none is a context-axis vocabulary |
| Is it reached by `_probe_infinite_extensibility`? | **No.** That probe iterates `vocabularies.vocabulary_ids()` only |
| Is it guarded by `verify_vocabulary_alignment`? | **No.** `_projections()` declares **9** pairs; none is an axis set |
| Is it covered by `REQ-28`? | **No.** `REQ-28` extends `ContextTaxonomy` — measured live at **17 taxa = root + 16 universal kinds + 0 future**, and extensible via `.extend()`. A **different population** in the same package |
| Enforcement of closure | `ReferenceFrame.__post_init__` — *"a frame may only declare a registered axis"*; `raise ContextValidationError` when `axis not in AXIS_GRAPH` |

**Adding a twentieth axis at this baseline requires editing `engine/context/location.py`.** Under `how_to_extend[2]` and `ART-17` that is an amendment where a registration was promised.

### 2.4 The aggravating factor

`REALITY_CONTEXT_AXES` carries this rule, verbatim:

> *"The Universal Reality Context Principle: **no value may be interpreted — measured, validated, governed, certified or executed against — until these five resolve.** They are the frame of reference the interpretation happens in, and an interpretation without one is not a weaker claim, it is an unfalsifiable one."*

The axis graph is therefore the **precondition surface for every interpretation the repository performs**. A closure here is a closure on the frame in which all other judgement occurs — and `UCKP-ART-20` explicitly extends the law's validity across *"planetary locations and civilizations"* whose interpretive axes this repository has not anticipated.

### 2.5 Affected modules

| Module | Coupling | References |
|---|---|---|
| `engine/context/location.py` | **Declares** `AXIS_DERIVATION`, derives `AXIS_GRAPH`; `axis_order`, `axis_waves`, `derivation_path`, `location_determined_axes`, `ReferenceFrame.__post_init__`, `FrameRegistry` | 9 |
| `engine/context/location_assurance.py` | Consumes for `_check_derivation_graph` (lines 190, 194) and `LXC-01` (lines 470–471) | 4 |
| `engine/context/__init__.py` | Re-exports `AXIS_GRAPH` (lines 88, 242) | 2 |
| `engine/foundation/composition/ordering.py` | `derive_order(graph, strategy=…)` — **generic over any `DependencyGraph` mapping**; it does not know about axes | 0 direct |

**Total `AXIS_GRAPH` references repository-wide: 15. Every one is a read.** No call site mutates, extends or registers.

### 2.6 Affected consumers

| Consumer | What breaks if an axis is admitted without code | Severity |
|---|---|---|
| `ReferenceFrame` construction | A frame declaring the new axis raises `ContextValidationError` | **Hard refusal** |
| `_check_derivation_graph` | Reports *"derives from X, which is not a declared axis"* | Assurance finding |
| `axis_order` / `axis_waves` | The axis is absent from the ordering; `unresolved_keys` may report a gap | Silent omission |
| `derivation_path` | `raise ContextValidationError("unknown context axis")` | **Hard refusal** |
| `LXC-01` outcome | Unaffected — it tests only that `LOCATION in AXIS_GRAPH` | None |
| `reference-frames.json` | 14 frames may only declare the 19 known axes | Bounded |

**Two hard refusals.** This makes `EEG-1` structurally identical to `DiscoveryKind` in `CEP-MOD-002`, which that determination graded as *"the projection whose divergence bites soonest"* precisely because `coerce()` hard-refuses.

### 2.7 Authority ownership

| Question | Measured |
|---|---|
| Who owns the axis set? | `engine/context/` — no separate declaration file; the module is the declaration |
| Who owns the *mechanism* for admitting a term? | `VocabularyRegistry`, `engine/uckp/vocabulary.py`. Its own docstring: *"This is the **only** extension mechanism"* |
| Who owns the guard? | `engine.uckp.assimilation.verify_vocabulary_alignment` — *"named by Repository Truth at `vocabulary.py:23`"* |
| Constitutional basis | `UCKP-ART-15`, `ART-17`; `INV-07`, `INV-14` |
| Is a constitutional act required to close it? | **No.** `how_to_extend[2]` — a DATA append plus registration |

### 2.8 Permanent correction model, stated

> `engine/context/location.py` shall **contribute** the axis set to `VocabularyRegistry` as `ucos.context-axis`, deriving the vocabulary from `AXIS_DERIVATION`, and shall **retain** `AXIS_GRAPH` as a checked projection reconstructed from that vocabulary, guarded by `verify_vocabulary_alignment`, which fails closed.

Feasibility is **proved, not argued** — §6.4.

---

## 3. EEG-2 Current State Analysis

### 3.1 Scope correction

The predecessor determination recorded `EEG-2` as `PortalSection` (5) and `EntityKind` (7). Direct measurement shows the closure is deeper. **The subject is a coupled cluster of five closed enums and two total mappings across three packages.** The predecessor's two are members of it, not the whole of it.

### 3.2 The cluster, measured

| # | Population | Home | Members | Shape |
|---|---|---|---|---|
| 1 | `Role` | `platform/foundation/identity.py:27` | **9** | `str, Enum` |
| 2 | `Permission` | `platform/foundation/identity.py:41` | **4** | `str, Enum` |
| 3 | `CapabilityGroup` | `platform/identity/contracts.py:45` | **16** | `str, Enum` — *"the coarse, auditable unit of authorization for the whole platform"* |
| 4 | `PortalSection` | `platform/portal/contracts.py:55` | **5** | `str, Enum` |
| 5 | `EntityKind` | `platform/portal/contracts.py:196` | **7** | `str, Enum` |
| M-a | `_SURFACE_TABLE` | `platform/portal/contracts.py:80` | **16** | `dict[CapabilityGroup, tuple[str, PortalSection]]` — **total over `CapabilityGroup`** |
| M-b | `_ENTITY_GROUP` | `platform/portal/contracts.py:214` | **7** | `dict[EntityKind, CapabilityGroup]` — **total over `EntityKind`** |

Live measurement confirms totality: `len(_SURFACE_TABLE) == len(all_capability_groups()) == 16` and `len(_ENTITY_GROUP) == len(all_entity_kinds()) == 7`. `default_portal_surfaces()` yields **16** surfaces.

### 3.3 `EntityKind` extensibility

| Test | Result |
|---|---|
| Registered in a vocabulary? | **No** |
| Admission operation? | **No.** `all_entity_kinds()` returns `tuple(EntityKind)` — a projection of the enum, not an admission path |
| Reached by `INV-14`? | **No** |
| Guarded by `verify_vocabulary_alignment`? | **No** |
| Enforcement | `entity_kind_group(kind)` — `if not isinstance(kind, EntityKind): raise PortalSearchError`. `SearchResult` repeats the same `isinstance` refusal |
| **Additional obligation on admission** | A new member **must** gain a `_ENTITY_GROUP` entry, or `entity_kind_group` has no answer for it |

**Admitting one entity kind requires two coordinated code edits in the same file**, and possibly a third if no existing `CapabilityGroup` authorizes it.

### 3.4 `PortalSection` extensibility

| Test | Result |
|---|---|
| Registered in a vocabulary? | **No** |
| Admission operation? | **No.** `all_portal_sections()` returns `tuple(PortalSection)` |
| Reached by `INV-14`? | **No** |
| Enforcement | Indirect — `_SURFACE_TABLE` values are typed `tuple[str, PortalSection]` |
| **Additional obligation** | A section with no `_SURFACE_TABLE` row is **unreachable**: navigation is derived from that table, and the table's own comment says *"Navigation is derived from this table — never invented"* |

**A new section admitted without a table row is inert.** It exists in the type and renders nowhere.

### 3.5 Rendering dependency

The chain, measured end to end:

```
CapabilityGroup ──_SURFACE_TABLE──▶ (title, PortalSection)
       │                                     │
       └──_surface_path()──▶ "/{group.value}"│
                    │                        │
                    ▼                        ▼
              PortalSurface.create(title, group, section, path)
                    │
                    ├──▶ Router.resolve(path) · Router.fingerprint()
                    ├──▶ Route.required_permission ← Permission.READ
                    └──▶ Route.group ← CapabilityGroup
```

`platform/portal/contracts.py`'s own docstring states the binding rule verbatim:

> *"…so that **navigation and routing are authorization-derived, not invented**: every navigable surface binds to exactly one §3.2 capability group and the READ permission that makes it visible."*

**Rendering is therefore not independently extensible.** A new rendered surface is a new `CapabilityGroup` — which is the RBAC authorization unit — so interface evolution is coupled to authorization evolution by design. That coupling is correct; its closure is not.

### 3.6 Schema dependency

| Surface | Dependency |
|---|---|
| `PORTAL_CONTRACTS` | `tuple[ContractRef, ...]` at `PORTAL_CONTRACT_VERSION = "1.0.0"` — 13 named contracts |
| `PortalSurface` | *"immutable, content-addressed"* — its digest covers title, group, section, path, permission |
| `Router.fingerprint()` | Content-addressed over the route set |
| Serialization | `to_dict()` on `PortalSurface`, `Route`, `Router` |

**A new section or entity kind moves `Router.fingerprint()` and every surface digest downstream of it.** That is a replay-visible change, unlike `EEG-1` (§10.4).

### 3.7 Why closed enums violate future evolution here

Three measured reasons, in ascending severity:

1. **The prose already claims openness the type does not provide.** The `EntityKind` docstring: *"the platform entity types global search spans (**≥4**; acceptance criterion)"*. A floor with no ceiling, held in a closed enum of 7. This is exactly `ISD-G-07`'s shape — *"a closed module tuple whose own comment claims 'Open by registration (Article 17)' while no registry holds it."*
2. **The knowledge plane already outruns it.** `GOVERNED_CATEGORY` holds **35** categories and is open by `ART-17`; `EntityKind` holds **7** and is not. A future object category admitted at the knowledge plane by data append is **unrenderable** until `platform/portal/contracts.py` is edited. The two planes evolve on different rules, and the DATA-plane one will outrun the CODE-plane one by construction.
3. **Authorization is the real bottleneck.** `CapabilityGroup` is *"the coarse, auditable unit of authorization for the whole platform"*. Its closure at 16 bounds not merely the UI but every authorization decision the platform can express.

### 3.8 Authority ownership

| Population | Owner | Single-authority guard |
|---|---|---|
| `Role`, `Permission` | `platform/foundation/identity.py` | `platform/tests/test_blueprints_governance.py:57` — `test_runtime_declares_no_new_role_permission_or_capability_group` asserts the tokens `"class Role"`, `"class Permission"`, `"class CapabilityGroup"` appear in **no** file of `platform/blueprints` |
| `CapabilityGroup` | `platform/identity/contracts.py` | same |
| `PortalSection`, `EntityKind`, both mappings | `platform/portal/contracts.py` | — |

**Single-authority discipline for these enums already exists and is already tested.** What is absent is extensibility, not ownership. That is a favourable starting position: no authority conflict has to be resolved before the closure can be.

---

## 4. Unified Root Cause Analysis

### 4.1 The determination

> **`EEG-1` and `EEG-2` are one architectural pattern failure, instantiated twice.**

They are not separate defects that happen to look alike. They are the same defect, with the same cause, the same detection blind spot, and the same located remedy — and that remedy has already been applied five times to five other instances of it.

### 4.2 The shared shape

| Property | `EEG-1` | `EEG-2` |
|---|---|---|
| A bounded population of named terms | ✔ 19 axes | ✔ 9 + 4 + 16 + 5 + 7 |
| Held as a module-level literal | ✔ `Mapping` | ✔ five `str, Enum`s |
| Not registered in `VocabularyRegistry` | ✔ | ✔ |
| Not reached by `_probe_infinite_extensibility` | ✔ | ✔ |
| Not guarded by `verify_vocabulary_alignment` | ✔ | ✔ |
| Documentation asserting openness the type refuses | ✔ `frame_kind` open, axes closed | ✔ `EntityKind` *"≥4"* |
| A hard refusal at the point of use | ✔ `ContextValidationError` ×2 | ✔ `PortalSearchError` ×2 |
| Constitutionally promised extensibility | ✔ `ART-17`, `INV-14` | ✔ `ART-17`, `INV-14` |

**Eight properties, both sites.**

### 4.3 The single root cause

`CEP-MOD-002` named it, and this determination measures it still holding:

> *"`_probe_infinite_extensibility` (`validation.py:746-771`) proves INV-14 **"by actually admitting one"** — a genuine executable proof. But it proves it **only over vocabularies registered in the `VocabularyRegistry`.**"*

Measured live at this baseline: the registry holds **13 vocabularies, 204 terms, `is_extensible() == True`, digest `7d733fcc2e5551f1`**.

| Registered vocabulary | Terms |
|---|---|
| `uckp.authority-tier` | 4 |
| `uckp.facet` | 33 |
| `uckp.governed-category` | 35 |
| `uckp.knowledge-kind` | 18 |
| `uckp.lifecycle-stage` | 10 |
| `uckp.non-authoritative-category` | 25 |
| `uckp.relation-type` | 17 |
| `uckp.relationship-class` | 12 |
| `ucos.architecture-layer` | 14 |
| `ucos.civilization-stratum` | 9 |
| `ucos.discovery-dimension` | 8 |
| `ucos.projection-kind` | 13 |
| `ucos.ukip-facet` | 6 |

**`INV-14` reports green over 13 vocabularies while 6 closed populations — 19 + 9 + 4 + 16 + 5 + 7 = 60 terms — sit outside its loop.** The invariant is not wrong; its **reach** is short. That is the root cause of both gaps, stated once.

### 4.4 The precedent proves the diagnosis

`CEP-MOD-002` found the identical blind spot over **six** closed populations, migrated five, and built the guard. Two of its findings are directly load-bearing here:

> *"**INV-14 has a measurement blind spot.** It reports green while six closed vocabularies sit outside its loop. **This is the migration's true justification.**"*

> *"Contribution without this guard would move the closure rather than close it: the registry would hold a term set nothing checks the engine against."*

**`EEG-1` and `EEG-2` are instances 7 and 8 of a defect class with a completed, verified remedy.**

### 4.5 The discriminator — why the two are not equally closable

One property separates them, and it is decisive:

| | `EEG-1` | `EEG-2` |
|---|---|---|
| Internal structure | **Intra-vocabulary** — 29 edges among 19 axes, all within one term set | **Inter-vocabulary** — `_ENTITY_GROUP` maps term set A → term set B; `_SURFACE_TABLE` maps term set C → (str, term set D) |
| Representable in `Term`? | **Yes** — `successors` carries edges *within* one vocabulary | **No** — `Term` holds `successors` only within its own vocabulary |
| Proved? | **Yes, in memory** — §6.4 | **No — and `CEP-MOD-002` already determined it cannot be** |

`CEP-MOD-002` §7.1, verbatim:

> *"Its `_CATEGORY_LAYER` dict is a **mapping between two term sets**, and `Vocabulary` has no representation for a relation between vocabularies — it holds `terms`, and `Term` holds `successors` only *within* one vocabulary. The mapping half belongs to Configuration."*

And its disposition matrix, verbatim:

> *"H-05 `_CATEGORY_LAYER` mapping — **CEP** — A mapping between term sets has no representation in `Vocabulary`; **requires its own determination**."*

**`_ENTITY_GROUP` and `_SURFACE_TABLE` are that same case.** This determination does not resolve it (§8.5); resolving it here would be exactly the reinterpretation `CMG-000001` LXXVI.6 forbids.

### 4.6 Could the knowledge graph carry the mapping? — measured, no

The obvious candidate is `UniversalKnowledgeGraph`: `ART-07` makes every relationship executable, `uckp.relation-type` holds `governs` and `owns`, and `uckp.relationship-class` holds `authority` and `governance`.

**Measured live:** the universe holds **6,338 nodes and 13,036 edges** — `ownership` 6,338, `authority` 6,337, `constitutional` 260, `validation` 56, `governance` 30, `evolution` 15.

But its nodes are **UCKOs, not vocabulary terms.** Probing seven term ids drawn from registered vocabularies — `book`, `capability`, `MetaKernelStratum`, `workspace`, `main`, `existence`, `location` — against `node_ids()` returns **False for all seven.**

**Vocabulary terms are not graph nodes at this baseline.** Routing the mapping through the graph would first require promoting terms to UCKOs — a substantial architectural act, which is itself the separate determination §8.5 refers.

### 4.7 Root cause statement, final

> **One cause:** `UCKP-INV-14` is proven only over `VocabularyRegistry`, and six populations totalling 60 terms live outside it.
>
> **One remedy class:** contribute the term set; retain the local type as a checked projection; guard with `verify_vocabulary_alignment`; widen `INV-14`'s reach.
>
> **One residue:** inter-vocabulary total mappings have no representation in `Vocabulary`, and this repository has already determined that fact requires its own determination rather than an ad-hoc extension.

---

## 5. Universal Extensible Vocabulary Architecture

**No new architecture is defined here.** What follows names the existing one, states its contract per the directive's eight required aspects, and shows that each aspect is already realised.

### 5.1 The mechanism, as it exists

| Component | Home | Contract |
|---|---|---|
| `Term` | `engine/uckp/vocabulary.py:52` | `frozen=True, slots=True`; fields `term_id`, `definition`, `rank`, `successors`, `symmetric` |
| `Vocabulary` | `:72` | *"An append-only, self-describing set of admissible terms."* Refuses a term declared twice |
| `VocabularyRegistry` | `:142` | *"The registry of every vocabulary in the Constitutional Knowledge Universe."* |
| `.extend(vocabulary_id, term)` | `:161` | *"Admit a previously unknown term. **This is the *only* extension mechanism.**"* |
| `.is_extensible()` | `:183` | *"Article 17 is proved, not asserted: a probe term is admitted into a copy of each vocabulary."* |
| `verify_vocabulary_alignment` | `engine/uckp/assimilation.py:705` | Fails closed if a projection and its vocabulary diverge in **either** direction |
| `_probe_infinite_extensibility` | `engine/uckp/validation.py:746` | The `INV-14` probe — admits `FUTURE_PROBE_TERM` into a copy of every registered vocabulary |

### 5.2 The two safety properties, verbatim from the module

> *"**Append-only.** `Vocabulary.extended_with` returns a new vocabulary; it never mutates. Redefining an existing term raises, because a term whose meaning can change retroactively invalidates every digest computed under the old meaning."*
>
> *"**Closed at the point of use.** `Vocabulary.require` refuses an unregistered term, so the openness is **"register then use"**, not "anything goes"."*

**This is why the model is not "anything goes".** Infinite extensibility and fail-closed validation coexist because admission and use are separate acts.

### 5.3 Admission mechanism

| Step | Operation | Failure mode |
|---|---|---|
| 1 | `registry.require(vocabulary_id)` | `LawViolation("no such vocabulary")` |
| 2 | `vocabulary.extended_with(term)` | `LawViolation("a registered term may not be redefined")` if the id exists with different content; **returns `self` unchanged** if identical |
| 3 | Registry rebinds the id to the extended vocabulary | — |
| 4 | Terms are re-sorted by `term_id` | Canonical order, so `digest()` is order-independent |
| 5 | Consumer calls `require(term_id)` | `LawViolation("term is not registered")` until step 3 has occurred |

**Idempotence is built in:** re-admitting an identical term is a no-op, not an error. That is what makes registration safe to repeat across processes.

### 5.4 Authority resolution

| Question | Answer | Basis |
|---|---|---|
| Who may admit a term? | Any holder of the registry instance | `VocabularyRegistry.extend` |
| Does admission confer authority? | **No** | `ART-04`, `INV-08` — a vocabulary is knowledge, not authority |
| Whose law governs admission? | `UCKP-LAW-0001` `ART-17` | `how_to_extend[2]` |
| Does it need a constitutional act? | **No** | `non_goals[3]` — extension is by registration |
| Process-wide vs local | `DEFAULT_VOCABULARIES` is process-wide; *"Callers that need to admit a term without affecting the whole universe build their own registry instead"* | `vocabulary.py` |

**The last row is the isolation primitive.** A candidate term may be exercised in a private registry — which is exactly what this determination's feasibility probes did (§14.2) — without touching the universe.

### 5.5 Lifecycle

```
UNDECLARED ──register()──▶ REGISTERED ──extend(term)──▶ ADMITTED ──require()──▶ IN USE
                                │                            │
                                │                            └── digest changes; canonical order preserved
                                └── re-register same id → LawViolation("vocabulary already registered")
```

**There is no removal state, by law.** `VocabularyRegistry` exposes `register`, `extend`, `get`, `require`, `require_term`, `vocabulary_ids`, `is_extensible`, `to_document`, `digest` — and **no removal operation**. `CEP-MOD-002` determined this is *"deliberate and constitutional, not an oversight: `UCKP-ART-14` — 'It appends; it never rewrites; it never terminates'."*

### 5.6 Validation

| Layer | Check | Failure |
|---|---|---|
| Construction | `Vocabulary.__post_init__` — no duplicate `term_id` | `LawViolation` |
| Admission | `extended_with` — no redefinition | `LawViolation` |
| Use | `require` — unregistered term refused | `LawViolation` |
| Alignment | `verify_vocabulary_alignment` — projection ≡ vocabulary, both directions | `AssimilationError` with a `divergences` list |
| Invariant | `_probe_infinite_extensibility` — probe admitted into a copy; original must be **unmutated** | `INV-14` finding |

The `INV-14` probe checks three distinct failures: refusal, acceptance-without-admission, and **mutation of the original** — *"so extension is not a pure derivation of a new vocabulary."*

### 5.7 Compatibility

`CEP-MOD-002` determined backward compatibility for exactly this migration shape, by three independent mechanisms:

1. **Append-only extension** — no existing term can be altered, so no existing consumer can break.
2. **The projection is retained** — *"Every enum and tuple stays in place as a derived view. No caller moves, no import changes."*
3. **Replay-neutrality** — measured, not argued (§10.4 revisits this for the two sites here).

### 5.8 Rendering adaptation

The directive requires that interface representation evolve without core modification. The measured architecture gives a partial answer and a located limit:

| Aspect | Status |
|---|---|
| Section term set | Contributable — a flat term set (§8.2) |
| Entity term set | Contributable — a flat term set (§7.2) |
| Surface **title** | Data — a `str` today, expressible as `Term.definition` |
| Surface **path** | Derived — `_surface_path()` computes `"/{group.value}"` from the term id; **already data-driven** |
| Surface **permission** | Constant `Permission.READ` — invariant, no per-term data |
| Section **assignment** (`group → section`) | **Inter-vocabulary mapping — §8.5** |
| Entity **authorization** (`kind → group`) | **Inter-vocabulary mapping — §8.5** |

**Four of six render inputs are already data or trivially data-expressible. Two are the deferred case.**

### 5.9 Migration

The pattern per site, from `CEP-MOD-002` Output 12.1:

```
1. Derive the vocabulary from the existing literal   (no second list to keep in step)
2. Contribute it to the registry at import           (universe.py:303-325 pattern)
3. Retain the local type as a checked projection     (no caller moves)
4. Add the (projection, vocabulary) pair to _projections()
5. Confirm _probe_infinite_extensibility now reaches it
```

Step 1 is the load-bearing one. `CEP-MOD-002` §OUTPUT 5 states the principle: derive from the literal so *"this is a projection of the cycle and not a second list of stages to keep in step with the first"* — the discipline `engine/uckp/evolution.py` already demonstrates for the stage set.

### 5.10 Rollback before acceptance

| What | Reversible? | Why |
|---|---|---|
| An in-memory candidate vocabulary in a **private** registry | **Fully** | Nothing global is touched. §14.2's probes are the proof |
| Code that *consumes* the registry | **Yes** | The projection remains throughout; reverting restores the prior path exactly |
| A *registration* into the process-wide registry | **No** | No removal operation exists, by `ART-14` |

**Therefore the acceptance boundary is the registration.** Everything before it is reversible; the act itself is not. `CEP-MOD-002`: *"revert the consuming code; the registered term remains as an unused, harmless member… **Rollback restores behaviour without restoring the closed vocabulary** — which is the correct outcome, because the closure was the defect."*

### 5.11 Immutable history after acceptance

| Guarantee | Mechanism |
|---|---|
| A term's meaning never changes | `extended_with` refuses redefinition |
| No term is ever removed | No removal operation |
| The registry state is content-addressed | `VocabularyRegistry.digest()` over `to_document()` |
| Order-independence | Terms sorted by `term_id` before digest |
| Every state transition is auditable | `ART-12`, `INV-17` |
| The evolution is itself a governed transaction | `ART-14`; `UAUE-000001` phase `AUE-P-11` claims `state-transition` and `continuation` |

**Acceptance is a one-way, digest-visible, append-only act.** That is the permanence property the directive asks for, and it is already law.

---

## 6. Location Evolution Extension Model

### 6.1 Disposition

| Field | Value |
|---|---|
| Site | `M-6` (continuing `CEP-MOD-002`'s M-numbering) |
| Vocabulary id | `ucos.context-axis` |
| Terms | **19** |
| `Term` fields required | `term_id`, `definition`, **`successors`** |
| Contributed by | `engine/context/location.py` |
| Retains | `AXIS_DERIVATION` (declaration) and `AXIS_GRAPH` (checked projection) |
| Disposition | **REUSE** — no new field, type or mechanism |
| Constitutional act required | **None** |

### 6.2 The representation

`AXIS_GRAPH` is `axis → requires`. `Term.successors` is *"declared successor"* — the forward direction. The vocabulary therefore carries the **transpose**: each term's `successors` are the axes that derive **from** it.

```
existence.successors     = (reality,)
reality.successors       = (civilization, observer, universe)
location.successors      = (calendar, currency, jurisdiction, language,
                            spatial, temporal, time-standard, units)
…
observer.successors      = ()          [leaf]
```

### 6.3 Why the transpose is lossless

The requirement semantics — *"`location` requires **both** `universe` and `civilization`"* — is a property of the **graph consumer**, not of the individual edge. `derive_order` treats the mapping as a `DependencyGraph` and computes waves over the full edge set. The transpose preserves the edge set exactly; conjunction is reconstructed by the same consumer that applies it today.

**This is precedent-backed:** `CIVILIZATION_STRATUM_VOCABULARY` already carries a 9-node chain in `successors`, and `LIFECYCLE_STAGE_VOCABULARY` exercises the field. `CEP-MOD-002` §OUTPUT 5 records `successors` as *"the parent chain"* for M-1 — the same use.

### 6.4 Feasibility — proved in memory

Constructed in a private registry, writing nothing:

```
terms                                             : 19
candidate vocabulary digest                       : 7c0e00fa6ba83ea4
AXIS_GRAPH reconstructable from vocabulary alone  : True
candidate admits unknown future member            : True
original vocabulary unmutated by the probe        : True
registry after admission                          : 14 vocabularies
registry.is_extensible() after admission          : True
```

**All five properties hold.** The reconstruction test rebuilt `axis → requires` from `successors` alone and compared it to `AXIS_DERIVATION` — **equal**. This is `CEP-MOD-002`'s standard of proof (*"proved, not asserted"*) applied before authorisation rather than after.

### 6.5 Consumer impact

| Consumer | Change |
|---|---|
| `AXIS_GRAPH` | Becomes a derivation from the vocabulary. **Same name, same type, same shape** — no caller moves |
| `axis_order`, `axis_waves`, `derivation_path`, `location_determined_axes` | **None** — they consume `AXIS_GRAPH` |
| `ReferenceFrame.__post_init__` | **None** — still tests `axis not in AXIS_GRAPH`, now over a registry-backed set |
| `location_assurance._check_derivation_graph` | **None** — still compares `AXIS_DERIVATION` to `AXIS_GRAPH` |
| `engine/context/__init__.py` | **None** — re-export unchanged |
| `reference-frames.json` | **None** — 14 frames unaffected |
| `derive_order` | **None** — generic over any mapping |

**Blast radius: 1 file changed, 0 callers moved.**

### 6.6 The permanent state after M-6

| Future admission | Mechanism | Code? |
|---|---|---|
| A 20th context axis | `registry.extend("ucos.context-axis", Term(...))` | **No** |
| A new reality context (civilization, simulation stratum) | `reference-frames.json` entry — already data | **No** |
| A new frame kind | `frame_kind` is already an open string | **No** |
| A new derivation edge | `Term.successors` on the appended term | **No** |

**All four permanently data.**

---

## 7. Entity Evolution Extension Model

### 7.1 Disposition

| Field | Value |
|---|---|
| Site | `M-7` |
| Vocabulary id | `ucos.entity-kind` |
| Terms | **7** |
| `Term` fields required | `term_id`, `definition` |
| Contributed by | `platform/portal/contracts.py` |
| Retains | `EntityKind` as a checked projection |
| Disposition | **EXTEND** — the term-set half only |
| **Excluded** | `_ENTITY_GROUP` — inter-vocabulary mapping, §8.5 |

### 7.2 The term set

A flat set of named terms with definitions — `workspace`, `project`, `blueprint`, `generation_request`, `artifact`, `validation_report`, `certification`. It maps onto `Vocabulary`/`Term` **with no field extension**, exactly as `CEP-MOD-002` graded H-01, H-02, H-04 and H-06: *"each maps onto `Vocabulary`/`Term` with no field extension."*

### 7.3 The guard problem — a decisive architectural constraint

`verify_vocabulary_alignment`'s `_projections()` imports from `engine.*` only. `EntityKind` lives in `platform.*`. **Adding it to `_projections()` would make the engine import the platform.**

Measured at this baseline:

| Direction | Count |
|---|---|
| `from platform.…` inside `engine/` | **0** |
| `from engine.…` inside `platform/` | **121** |

*(The single `import platform` at `engine/execution_environment/discovery.py:19` is the Python standard-library module, not this repository's package.)*

The architecture layer stack confirms the ordering: `ucos.architecture-layer` ranks `engineering` **5**, `implementation` **6**, `platform` **8**. **Engine is more foundational than platform; an engine→platform import inverts the stack.**

### 7.4 The resolution — a platform-side guard, not an engine-side one

`platform/portal/contracts.py`'s docstring already states the legal conduit:

> *"It **reuses the certified EC-1 contract machinery through the Platform Foundation**… and the Identity Layer's `CapabilityGroup`…"*

And `platform/foundation/contracts.py` already imports `engine.foundation.contracts.contract` and `engine.uckp.canonical`. **The platform→engine conduit exists and is exercised.**

> **Determination:** the alignment guard for `M-7` and `M-8` is an **EXTEND of the platform-side contract surface**, consuming the engine registry in the already-legal direction. It is **not** an addition to `engine.uckp.assimilation._projections()`.

**This is the one place where `EEG-1` and `EEG-2`, though one defect, take different resolution topologies.** `EEG-1` is engine→engine and uses the existing guard unchanged; `EEG-2` is platform→engine and needs the guard mirrored at the platform plane.

### 7.5 One measured caution

`platform/tests/test_blueprints_governance.py:44` asserts that `platform/blueprints` imports **no** `engine.*` module at runtime — *"the platform binds the engine by ContractRef only."* That constraint is scoped to `platform/blueprints`, **not** to `platform/portal` or `platform/foundation`. Any implementation must preserve it for `blueprints` and must not generalise it into a prohibition it does not currently state.

### 7.6 The permanent state after M-7

| Future admission | Mechanism | Code? |
|---|---|---|
| A new entity kind, term only | `registry.extend("ucos.entity-kind", Term(...))` | **No** |
| Its `EntityKind` projection member | Derived from the vocabulary | **No** |
| **Its authorizing capability group** | **`_ENTITY_GROUP` — §8.5** | **Yes, until §8.5 resolves** |

**Two of three permanently data. The third is the deferred case, and this determination says so rather than papering it.**

---

## 8. Interface Rendering Evolution Model

### 8.1 Disposition

| Field | Value |
|---|---|
| Site | `M-8` |
| Vocabulary ids | `ucos.interface-section` (5) · `ucos.capability-group` (16) · `ucos.platform-role` (9) · `ucos.platform-permission` (4) |
| Contributed by | `platform/portal/contracts.py`, `platform/identity/contracts.py`, `platform/foundation/identity.py` |
| Disposition | **EXTEND** — term-set halves |
| **Excluded** | `_SURFACE_TABLE` — inter-vocabulary mapping, §8.5 |

### 8.2 The term-set halves

All four are flat sets of named terms with definitions. `PortalSection`'s five members carry documented meanings in the class docstring; `CapabilityGroup`'s sixteen are §3.2 RBAC matrix rows; `Role`'s nine and `Permission`'s four likewise. **None requires a `Term` field that does not exist.**

`Term.rank` is available and unused here — the sections have no declared order beyond declaration order, and inventing a rank would be adding a claim the source does not make.

### 8.3 What becomes data after M-8

| Render input | After M-8 |
|---|---|
| Section term set | **Data** |
| Group term set | **Data** |
| Surface title | **Data** — `Term.definition` |
| Surface path | **Already derived** — `_surface_path()` computes it from the term id |
| Surface permission | Constant `READ` — no per-term data needed |
| `Router` route set | **Derived** from the surfaces |

### 8.4 What does not

| Render input | Why it resists |
|---|---|
| `_SURFACE_TABLE` : `CapabilityGroup → (title, PortalSection)` | Total function between two term sets |
| `_ENTITY_GROUP` : `EntityKind → CapabilityGroup` | Total function between two term sets |

A section admitted with no `_SURFACE_TABLE` row renders nowhere; the table's own comment is *"Navigation is derived from this table — never invented."* An entity kind admitted with no `_ENTITY_GROUP` row has no answer from `entity_kind_group`. **In both cases the term is admissible and the binding is not.**

### 8.5 The located limit — referred, not resolved

> **Determination:** the representation of a total mapping between two registered vocabularies is **an open constitutional question with a located precedent, and it is referred, not answered here.**

**Basis, in three parts:**

1. **The limit is already measured.** `CEP-MOD-002` §7.1: *"`Vocabulary` has no representation for a relation between vocabularies — it holds `terms`, and `Term` holds `successors` only within one vocabulary."*
2. **The disposition is already assigned.** `CEP-MOD-002` §12.2: *"H-05 `_CATEGORY_LAYER` mapping — **CEP** — … requires its own determination."* The identical case has been open since that determination and no artifact has closed it.
3. **The obvious alternatives are measured closed.** The knowledge graph carries object-to-object edges, and vocabulary terms are **not** graph nodes (§4.6, seven probes, all `False`). Extending `Term` with a cross-vocabulary field would be a Layer Zero change made to fit one consumer — which `how_to_extend[2]` forbids: *"`engine/uckp/law.py` is never amended to fit the data."*

**Why this determination does not decide it:** the directive forbids patches, exceptions and special cases. Every available in-scope route to closing the mapping half is one of those three. Deciding it correctly requires choosing between at least three architectures — promote terms to UCKOs and use the existing relationship graph; add a first-class inter-vocabulary relation type to Layer Zero; or classify the mapping as Configuration as `CEP-MOD-002` did for `_CATEGORY_LAYER` — and that choice is a constitutional decision (§11.3), not an engineering one.

### 8.6 The honest consequence

After `M-6`, `M-7` and `M-8`:

| Admission | Code required? |
|---|---|
| A new context axis | **No** |
| A new reality context / frame / frame kind | **No** |
| A new entity kind term | **No** |
| A new interface section term | **No** |
| A new capability group term | **No** |
| A new role or permission term | **No** |
| **Binding an entity kind to its authorizing group** | **Yes — until §8.5 resolves** |
| **Binding a capability group to its section and title** | **Yes — until §8.5 resolves** |

**Six of eight become permanently data. Two remain code, and this determination names them rather than claiming a closure it did not measure.**

---

## 9. Constitutional and Law Alignment

### 9.1 Required constitutional changes

**None.**

| Test | Result |
|---|---|
| Does any article need amending? | **No.** `ART-17` already requires admission by registration |
| Does any invariant need adding? | **No.** `INV-14` already states the property; only its **reach** widens |
| Does any stop condition need adding? | **No.** `STOP-13` already binds every future evolution |
| Is a `T1` act required? | **No** — and `T1` is `VACANT` (`VAC-01`), so a resolution that required one would be unexecutable |
| Governing rule | `non_goals[3]` — *"Adding an article, invariant or stop condition to `engine/uckp/law.py`. Extension is by registration (`UCKP-ART-17`)"* |

**`CEP-MOD-002` reached the identical conclusion for its five sites:** *"Widen INV-14's reach to the contributed vocabularies… no invariant redeclared (`law.py` remains sole declarant)."*

### 9.2 Required law changes

**None.** `engine/uckp/law.py` is not touched by any disposition in §12.2.

### 9.3 Articles the resolution operates under

| Article | Text | Role here |
|---|---|---|
| `ART-15` | *"Knowledge reasons about itself. No conclusion rests on a hardcoded assumption…"* | The defect: 60 terms are hardcoded assumptions |
| `ART-17` | *"…an unknown future category is admitted by registration, never by amendment."* | The obligation both sites currently fail |
| `ART-18` | *"Before anything is created its canonical object shall be located. If it exists it is reused…"* | Why `CREATE` count is 0 |
| `ART-14` | *"It appends; it never rewrites; it never terminates."* | Why registration is irreversible (§5.10) |
| `ART-08` | *"Nothing shall require manual enumeration."* | Why contribution happens at import, not by a hand-maintained list |
| `ART-04` / `ART-11` | Interfaces and documents are views; none holds authority | Why the UI closure cannot corrupt truth (§11.4) |

### 9.4 Invariants engaged

| Invariant | Engagement |
|---|---|
| `INV-14` `infinite-extensibility` | **Reach widens** from 13 vocabularies to 17 |
| `INV-07` `zero-hardcoded-knowledge` | Six populations gain provenance naming their declaration |
| `INV-03` `zero-duplication` | Protected by the retained-projection + alignment-guard pattern: one authority, one verified view |
| `INV-13` `infinite-evolvability` | Registration is append-only; no terminal state |
| `INV-17` `infinite-auditability` | Registry `digest()` makes every admission digest-visible |

### 9.5 The alignment rule this resolution satisfies

`constitutional-authority-alignment.json` `extension_rule.what_this_forbids`:

> *"A second registry, engine, lifecycle, identity authority, relationship graph or evolution system standing beside the ones that exist."*

| Forbidden thing | Created by this resolution? |
|---|---|
| A second registry | **No** — `VocabularyRegistry` is reused |
| A second engine | **No** |
| A second lifecycle | **No** |
| A second identity authority | **No** — frame ids still mint through `deterministic_id` |
| A second relationship graph | **No** — §4.6 declines to route through it, and creates none |
| A second evolution system | **No** |

**Six of six clear.**

---

## 10. Registry and Engine Alignment

### 10.1 Required registry changes

**None to any repository registry.** No change to `00-BOOK/DATA/*`, `00-CMG/CMG-REGISTRY.json`, the id ledger, `artifacts.json`, or any programme declaration.

The only registry affected is the **in-process `VocabularyRegistry`**, whose population changes from 13 vocabularies to 17 — and that is the mechanism operating as designed, not a registry modification.

| Registry | Change |
|---|---|
| `00-BOOK/DATA/id-ledger.json` | **None** — no identity minted |
| `00-BOOK/DATA/relationships.json` | **None** — §4.6 adds no edge |
| `00-BOOK/DATA/artifacts.json` | **None** by this determination |
| `00-BOOK/DATA/constitutional-authority-alignment.json` | **None** — no new instrument, no new role |
| `00-BOOK/DATA/mutation-governance-boundary.json` | **None** — 9 classes unchanged |
| `00-CMG/CMG-REGISTRY.json` | **None** — 8 tiers unchanged |
| `engine/context/catalog/reference-frames.json` | **None** — 14 frames unchanged |
| `VocabularyRegistry` (in-process) | 13 → 17 vocabularies; 204 → 264 terms |

### 10.2 Required engine changes

| Site | Files | Nature |
|---|---|---|
| `M-6` | `engine/context/location.py`; `engine/uckp/vocabulary.py` (registration); `engine/uckp/assimilation.py` (`_projections()` pair) | **Additive.** `AXIS_GRAPH` becomes derived; nothing renamed, no caller moved |
| `M-7`, `M-8` | `platform/portal/contracts.py`, `platform/identity/contracts.py`, `platform/foundation/identity.py`; one platform-side alignment guard | **Additive.** Enums retained as projections |
| `INV-14` reach | `engine/uckp/validation.py` | **None required.** `_probe_infinite_extensibility` iterates `vocabulary_ids()`; reach widens automatically on registration |

**The `INV-14` row is the strongest evidence the mechanism was built for this.** No probe edit is needed — registering a vocabulary is sufficient to bring it under the invariant.

### 10.3 Required verification gates

| Gate | Change | Basis |
|---|---|---|
| `verify_vocabulary_alignment` | **Extend** — 9 pairs → 10 (engine side, `M-6`) | Existing function; `CEP-MOD-002` disposition `EXTEND` |
| A platform-side alignment guard | **Extend** the platform contract surface | §7.4 — layer direction forbids an engine-side one |
| `_probe_infinite_extensibility` | **None** | Reach widens automatically |
| `verify.sh` | **None** — no new stage. 16 stages unchanged | `non_goals[4]` — *"Adding a verification stage, pipeline or scheduler. The invariants land in the gate `verify.sh` already runs"* |
| `UAUE-GATE-01…10` | **None** | No stage, phase or register added |

**No new verification stage.** This is an explicit `non_goals` requirement and it is satisfied.

### 10.4 Replay and determinism impact

| Site | Impact | Reasoning |
|---|---|---|
| `M-6` | **Neutral** | `AXIS_GRAPH` keeps its exact value. The candidate reconstructs it **losslessly** (§6.4). No consumer's output changes |
| `M-7`, `M-8` term sets | **Neutral** while the projections retain identical members | Same reasoning |
| `M-7`, `M-8` **if a member is later admitted** | **Digest-visible** | `Router.fingerprint()` and every `PortalSurface` digest move (§3.6). That is correct behaviour: a new surface is a real change |
| Registry digest | **Moves** — `7d733fcc2e5551f1` changes on registration | Expected and auditable under `INV-17` |

**The migration is replay-neutral; a subsequent admission is replay-visible.** `CEP-MOD-002` measured the identical property for its five sites and graded replay handling `PASS`.

### 10.5 Duplication control

The single risk of contribution is creating a second authority over one term set. It is controlled by the same three mechanisms `CEP-MOD-002` relied on:

| Mechanism | Effect |
|---|---|
| Derive the vocabulary **from** the existing literal | There is never a second list to keep in step |
| Retain the literal as a **checked projection** | One authority, one verified view |
| `verify_vocabulary_alignment` fails closed **in both directions** | Divergence is detected, not tolerated |

`CEP-MOD-002`'s warning applies exactly: *"Contribution without this guard would **move** the closure rather than close it: the registry would hold a term set nothing checks the engine against."*

---

## 11. Security and Governance Model

### 11.1 The security-relevant fact

`CapabilityGroup` is *"the coarse, auditable unit of authorization for the whole platform."* `Role` and `Permission` are the other two RBAC primitives. **Making an authorization vocabulary extensible is a security-relevant act**, and it must not be treated as a routine vocabulary contribution.

### 11.2 What the existing mechanism already guarantees

| Property | Mechanism |
|---|---|
| A term cannot be silently redefined | `extended_with` refuses redefinition — an admitted permission cannot have its meaning changed later |
| An unregistered term cannot be used | `require` fails closed — *"register then use"* |
| Admission confers no authority | `ART-04`, `INV-08` — a vocabulary is knowledge; it grants nothing by existing |
| Admission is digest-visible | `VocabularyRegistry.digest()` |
| Blast radius can be contained | *"Callers that need to admit a term without affecting the whole universe build their own registry"* |
| Single authority per enum is already tested | `test_runtime_declares_no_new_role_permission_or_capability_group` |

### 11.3 The governance question this raises

Extensibility answers *how* a term is admitted. It does not answer *who may admit one*. For a knowledge vocabulary such as `ucos.context-axis`, that is settled: `how_to_extend[2]` makes it a DATA append, and `ART-04` guarantees a vocabulary term grants nothing.

For an **authorization** vocabulary the same act creates a new authorization unit. Measured position:

| Question | Answer at this baseline |
|---|---|
| Does admitting a `CapabilityGroup` term grant any access? | **No.** Grants flow through `RoleRegistry` / `PermissionEngine`, not through term existence |
| Does it create a *nameable* authorization unit? | **Yes** |
| Is there a declared owner for that act? | **Not located.** No party is declared as owner of authorization-vocabulary content |
| Is that a blocker for `M-6`? | **No** — `ucos.context-axis` is not an authorization vocabulary |
| Is it a blocker for `M-8`? | **It is an owner decision** — §12.4 |

**This determination locates the question and refuses to answer it**, on the same grounds `non_goals[5]` states: *"Deciding a conflict between two located instruments… is measured and reported, never disposed of here."*

### 11.4 The mitigating constitutional fact

`ART-04` places `api` and interfaces in `NON_AUTHORITATIVE_CATEGORIES`; `ART-11` makes documents and views non-authoritative; `INV-08` is `zero-projection-authority` — *"No projection, binding or generated artifact claims authority."*

**So no evolution of the interface plane can corrupt constitutional truth.** The cost of `EEG-2` is expressive, not constitutional: a future object category admitted at the knowledge plane cannot be *rendered* until the interface plane admits it. That bounds the severity of §8.5's residue precisely — it is an expressiveness gap in a non-authoritative plane, not a truth gap.

### 11.5 Audit trail

| Event | Recorded by |
|---|---|
| A vocabulary is registered | Registry population; `digest()` moves |
| A term is admitted | `to_document()` lists it in canonical order |
| A projection diverges | `verify_vocabulary_alignment` raises with a `divergences` list naming both directions |
| `INV-14` reach changes | `_evidence(vocabularies=…, vocabularies_extended=…, registry_extensible=…)` |
| The change as a constitutional transition | `ART-12` state with knowledge/authority/capability deltas; `UAUE` `AUE-P-11` |

**Every one of the directive's audit requirements is met by mechanisms that already run.**

---

## 12. Implementation Readiness Assessment

### 12.1 Readiness gates

| Gate | `M-6` (EEG-1) | `M-7`/`M-8` (EEG-2) |
|---|---|---|
| Canonical owner located | **PASS** — `VocabularyRegistry` | **PASS** — same |
| Mechanism exists without invention | **PASS** | **PASS** for term sets · **FAIL** for mappings |
| Representation proved | **PASS** — in memory, §6.4 | **PASS** for term sets · **NOT PROVED** for mappings |
| Guard exists | **PASS** — `verify_vocabulary_alignment`, 9 pairs, live green | **PARTIAL** — needs a platform-side mirror (§7.4) |
| Layer direction lawful | **PASS** — engine→engine | **PASS** only via platform→engine |
| `INV-14` reach widens automatically | **PASS** | **PASS** |
| Replay neutrality | **PASS** — measured | **PASS** at migration; visible on later admission |
| Backward compatibility | **PASS** — append-only + retained projection | **PASS** — same |
| Rollback before acceptance | **PASS** | **PASS** |
| No new registry / identity / authority / framework | **PASS** | **PASS** |
| No new `verify.sh` stage | **PASS** | **PASS** |
| Constitutional act required | **NONE** | **NONE** for term sets |
| **Blocking prerequisite** | **None** | **§8.5 mapping representation** |

### 12.2 Disposition matrix

| Step | Act | Disposition | Authority |
|---|---|---|---|
| `M-6a` | Derive `ucos.context-axis` from `AXIS_DERIVATION`; contribute | **REUSE** | Mechanism exists entire; precedent M-1…M-5 |
| `M-6b` | Retain `AXIS_GRAPH` as a checked projection; add the `_projections()` pair | **EXTEND** | Existing function; `CEP-MOD-002` M-0a precedent |
| `M-7` | Contribute `ucos.entity-kind` (term set only) | **EXTEND** | Same pattern, platform plane |
| `M-8` | Contribute `ucos.interface-section`, `ucos.capability-group`, `ucos.platform-role`, `ucos.platform-permission` (term sets only) | **EXTEND** | Same |
| Platform-side alignment guard | Mirror `verify_vocabulary_alignment` at the platform contract surface | **EXTEND** | Layer direction (§7.4); `CREATE` unavailable under `ART-18` |
| `INV-14` reach | — | **PASS** | Widens automatically on registration |
| `verify.sh` | — | **PASS** | No stage added; `non_goals[4]` |
| Replay | — | **PASS** | Measured neutral |
| `_ENTITY_GROUP` / `_SURFACE_TABLE` mappings | — | **CEP — REFERRED** | No representation in `Vocabulary`; `CEP-MOD-002` §12.2 precedent |
| Authorization-vocabulary admission ownership | — | **OWNER DECISION** | §11.3 — no owner located |
| Any new vocabulary mechanism | — | **CREATE — UNAVAILABLE** | `ART-18`; every capability has a located owner |

**`REUSE` 1 · `EXTEND` 4 · `PASS` 3 · `CEP-REFERRED` 1 · `OWNER DECISION` 1 · `CREATE` 0.**

### 12.3 Implementation boundary — engineering executable

Actions that need **no** authority decision and **no** constitutional act:

| # | Action | Plane |
|---|---|---|
| E-1 | Derive `ucos.context-axis` from `AXIS_DERIVATION` and contribute it | Engine |
| E-2 | Reconstruct `AXIS_GRAPH` from the vocabulary; retain name, type and shape | Engine |
| E-3 | Add the `(AXIS_GRAPH, ucos.context-axis)` pair to `_projections()` | Engine |
| E-4 | Confirm `_probe_infinite_extensibility` reaches the new vocabulary | Engine |
| E-5 | Derive `ucos.entity-kind` and `ucos.interface-section` from their enums; contribute | Platform |
| E-6 | Mirror the alignment guard at the platform contract surface | Platform |

**Engineering may implement only criteria a declaration already states.** `REPOSITORY_INTELLIGENCE_AUTHORITY = "ENGINEERING-EXECUTION-ONLY"` — it may detect, measure and implement; it may not define.

### 12.4 Implementation boundary — authority decisions

| # | Decision | Why it is not engineering |
|---|---|---|
| A-1 | May `CapabilityGroup`, `Role` and `Permission` be made extensible at all? | Creates nameable authorization units (§11.3) |
| A-2 | Who owns admission to an authorization vocabulary? | No party is declared. This is the same shape as the `AG-2b` finding: a role that must be located before it can act |
| A-3 | Is the platform-side guard's home `platform/portal/contracts.py`, `platform/foundation/contracts.py`, or a new module? | A home assignment is an ownership act |
| A-4 | Does `M-8` proceed before or after §8.5 resolves? | Sequencing under a known partial closure |

### 12.5 Implementation boundary — constitutional decisions

| # | Decision | Forum |
|---|---|---|
| C-1 | **How is a total mapping between two registered vocabularies represented?** Three located candidates: promote terms to UCKOs and use the existing relationship graph; add a first-class inter-vocabulary relation to Layer Zero; or classify the mapping as Configuration as `CEP-MOD-002` did for `_CATEGORY_LAYER` | Its own determination — `CEP-MOD-002` §12.2 already assigned it there |
| C-2 | If the answer is Configuration, is a Configuration plane that admits members without code available? | Same |

**C-1 is the only genuinely open constitutional question this determination raises, and it was already open before it.**

### 12.6 Readiness verdict

| Subject | Verdict |
|---|---|
| **`EEG-1`** | **READY — no blocking prerequisite.** Owner located, mechanism located, representation proved in memory, guard exists and passes live, replay neutral, zero constitutional act |
| **`EEG-2` term sets** | **READY, CONDITIONAL on A-1 and A-3.** Mechanism located; two authority decisions precede execution |
| **`EEG-2` mappings** | **NOT READY — BLOCKED ON C-1.** Not an engineering blocker; a representational one with a located precedent |

---

## 13. Permanent Closure Determination

### 13.1 The determination

> **`EEG-1` and `EEG-2` are one architectural pattern failure — a bounded population held as a module literal, outside `VocabularyRegistry`, therefore outside `_probe_infinite_extensibility` and invisible to `UCKP-INV-14`. Six populations totalling 60 terms are affected. The remedy is `CEP-MOD-002`'s single migration applied to three further sites: contribute the term set, retain the local type as a checked projection, guard it with a fail-closed alignment verifier. No new registry, identity system, authority or evolution framework is created; `CREATE` count is zero.**
>
> **`EEG-1` closes permanently and completely. Its 19-term vocabulary reconstructs `AXIS_GRAPH` losslessly and admits an unknown future member — proved in memory at this baseline, changing nothing.**
>
> **`EEG-2` closes permanently in its term-set half — six of its eight admission paths become data forever. Its two total mappings do not close, because a mapping between two registered vocabularies has no representation in `Vocabulary`, and this repository determined in `CEP-MOD-002` §12.2 that this fact requires its own determination. That referral is honoured here rather than circumvented, because every available route around it is a patch, an exception or a special case — the three things this directive forbids.**

### 13.2 Against the directive's target state

| Future admission | Data-only after closure? |
|---|---|
| **Entity type** — term | **Yes** (`M-7`) |
| **Entity type** — its authorizing binding | **No — C-1** |
| **Location model** — a new context axis | **Yes** (`M-6`) |
| **Reality context** — civilization, simulation stratum, frame kind | **Yes** — already data today (14 frames, open `frame_kind`) |
| **Interface representation** — section, title, path | **Yes** (`M-8`; path already derived) |
| **Interface representation** — its section binding | **No — C-1** |
| **Capability** — term | **Yes** (`M-8`, subject to A-1) |
| **Knowledge type** | **Yes — already data today** (`GOVERNED_CATEGORY`, 35 terms, open by `ART-17`) |

**Six of eight reach the target state. Two are gated on one constitutional question.**

### 13.3 Compliance with the directive's stated principle

| Principle | Compliance |
|---|---|
| No patches | **Met.** Every disposition is `REUSE` or `EXTEND` of a located owner |
| No temporary exceptions | **Met.** Nothing is time-boxed or conditioned on a later cleanup |
| No special cases | **Met.** One pattern, applied uniformly; where it does not fit, the misfit is referred, not special-cased |
| Permanent infinite extensibility | **Met for six of eight paths**, and the two exceptions are named rather than hidden |
| Use `UCKP-INV-14` + `evolution.py` model + derived vocabulary pattern | **Met.** All three are the mechanism, unchanged |
| No new registries | **Met** — `VocabularyRegistry` reused |
| No new identity systems | **Met** — `deterministic_id` unchanged |
| No new authority systems | **Met** — `CAA-INV-01` preserved |
| No parallel evolution frameworks | **Met** — no second evolution system |
| Extend existing Ω∞ architecture | **Met** — every act lands in a located owner |

### 13.4 What would make this closure void

Stated so the failure modes are checkable rather than assumed:

| Failure | Why it voids the closure |
|---|---|
| Contributing a vocabulary **without** adding its alignment pair | *"would move the closure rather than close it"* — the registry would hold a term set nothing checks |
| Writing the vocabulary as a **second list** rather than deriving it from the literal | Two authorities over one term set; `ART-03` void |
| Extending `Term` to carry the mapping | Layer Zero amended to fit one consumer; `how_to_extend[2]` |
| Adding a `verify.sh` stage | `non_goals[4]` |
| Adding the platform pair to `engine.uckp.assimilation._projections()` | Inverts the layer stack; 0 engine→platform imports today |
| Declaring `EEG-2` closed while the mappings remain | An unmeasured claim; §8.6 states the residue instead |

### 13.5 Final verdict

> **EEG-1 — PERMANENTLY CLOSABLE. READY. NO BLOCKING PREREQUISITE. NO CONSTITUTIONAL ACT.**
>
> **EEG-2 — PERMANENTLY CLOSABLE IN ITS TERM-SET HALF, conditional on two authority decisions (A-1, A-3). Its mapping half is BLOCKED ON ONE LOCATED CONSTITUTIONAL QUESTION (C-1), which `CEP-MOD-002` §12.2 already assigned to its own determination and which no artifact has since closed.**
>
> **CREATE count: 0. New registries: 0. New identity systems: 0. New authority systems: 0. Parallel evolution frameworks: 0. Patches: 0. Special cases: 0. Constitutional amendments: 0.**

---

## 14. Verification Record

### 14.1 Baseline integrity

| Check | Before | After |
|---|---|---|
| HEAD | `bae59755d7e2d3566c93b89c722b68847145269a` | unchanged |
| Branch | `integration/recovery-001` | unchanged |
| `git status --porcelain` | **359** lines | **360** — this artifact only |
| Files modified | **0** | **0** |
| JSON modified | **0** | **0** |
| Registries modified | **0** | **0** |
| Commits | **0** | **0** |

### 14.2 Feasibility probes — how "no future core code modification" was proved

Four probes were run **in memory, in a private registry**, writing nothing. This is the isolation primitive the mechanism itself documents: *"Callers that need to admit a term without affecting the whole universe build their own registry instead."*

| Probe | Question | Result |
|---|---|---|
| **P-1** | Does the axis set fit `Vocabulary`/`Term` with no field extension? | **YES** — 19 terms, using `term_id`, `definition`, `successors`; digest `7c0e00fa6ba83ea4` |
| **P-2** | Is `AXIS_GRAPH` reconstructable from the vocabulary alone? | **YES — losslessly.** Rebuilt `axis → requires` from `successors` and compared to `AXIS_DERIVATION`: **equal** |
| **P-3** | Does the candidate admit an unknown future member, leaving the original unmutated? | **YES** — probe admitted; original unmutated (both conditions `_probe_infinite_extensibility` checks) |
| **P-4** | Does the registry stay extensible after admission? | **YES** — 14 vocabularies, `is_extensible() == True` |

### 14.3 The seven verification questions in the directive

| # | Question | How it is proved | Status |
|---|---|---|---|
| 1 | **No future core code modification required** | `_probe_infinite_extensibility` admits `FUTURE_PROBE_TERM` into a copy of every registered vocabulary. Once a population is registered, the probe reaches it automatically — no probe edit needed (§10.2) | **Provable — mechanism exists** |
| 2 | **No duplicate vocabulary** | `VocabularyRegistry.register` raises `LawViolation("vocabulary already registered")` on a repeat id | **Enforced today** |
| 3 | **No conflicting definitions** | `Vocabulary.__post_init__` refuses a duplicate `term_id`; `extended_with` refuses redefinition; `verify_vocabulary_alignment` fails closed on divergence in **either** direction | **Enforced today; live green over 9 pairs** |
| 4 | **No hidden extension path** | `.extend()` docstring: *"This is the **only** extension mechanism."* Measured: `AXIS_GRAPH` has 15 references, **all reads**; `add_dynamic_class_extension_mechanism()`'s only callers are its own two tests | **Measured** |
| 5 | **Complete audit trail** | Registry `digest()`; `to_document()` in canonical order; `divergences` list on failure; `_evidence(...)` on the `INV-14` probe; `ART-12` deltas; `INV-17` | **Enforced today** |
| 6 | **Append-only history after acceptance** | No removal operation on `VocabularyRegistry`; `extended_with` refuses redefinition; `ART-14` | **Enforced today** |
| 7 | **Rollback before acceptance** | Private-registry construction touches nothing global — demonstrated by P-1…P-4 | **Demonstrated** |

### 14.4 Live measurements taken

| Measurement | Method | Result |
|---|---|---|
| `AXIS_GRAPH` size, edges, roots, leaves, multi-parent | Import + graph analysis | 19 · 29 · 1 · 4 · 6 |
| Transpose losslessness | Set comparison against `AXIS_DERIVATION` | **True** |
| `AXIS_GRAPH` references repository-wide | `grep` across all `.py` | **15, all reads** |
| `ContextTaxonomy` state | Import of `UNIVERSAL_TAXONOMY` | 17 taxa · 16 universal · 0 future · extensible |
| `PortalSection` / `EntityKind` / `CapabilityGroup` / `Role` / `Permission` | Import + enum length | 5 · 7 · 16 · 9 · 4 |
| `_SURFACE_TABLE` / `_ENTITY_GROUP` totality | Length comparison against their key sets | **16 = 16 · 7 = 7, both total** |
| `default_portal_surfaces()` | Import + call | **16** |
| Vocabulary registry state | Import + `digest()` | 13 vocabularies · 204 terms · extensible · `7d733fcc2e5551f1` |
| `verify_vocabulary_alignment()` | Direct call | **PASS over 9 projections** |
| Universe graph | `build_universe().graph()` | 6,338 nodes · 13,036 edges |
| Vocabulary terms as graph nodes | 7 term ids probed against `node_ids()` | **False for all 7** |
| `engine/` → `platform/` imports | `grep` | **0** |
| `platform/` → `engine/` imports | `grep` | **121** |
| `verify.sh` stages | `grep -c 'run_stage "'` | **16** |

### 14.5 What was not verified

| Not verified | Why |
|---|---|
| That an implemented `M-6` passes `verify.sh` | Would require implementing it. Out of mode |
| The runtime cost of registration | Not measured; no basis to claim it is negligible |
| Whether A-1 (authorization-vocabulary extensibility) is desirable | An owner decision, not a measurement (§12.4) |
| Any of C-1's three candidate architectures | Each is a determination in its own right (§12.5) |
| That `EEG-2`'s cluster is exactly five enums and two mappings and no more | Measured across `platform/portal`, `platform/identity`, `platform/foundation`. A population outside those three packages would not have been seen |
| Current `verify.sh` verdict at HEAD | Not executed — `ISD-G-11` records that the full pipeline mutates tracked surfaces, which this determination's mode forbids |

### 14.6 Artifact creation verified

| Check | Result |
|---|---|
| File exists | **Yes** — `UCOS-OMEGA-INFINITY-EEG-1-EEG-2-EVOLUTION-EXTENSIBILITY-CLOSURE-DETERMINATION.md` |
| Required sections | **14 of 14 present, in the specified order** |
| Git status | `??` untracked — the only delta from the pre-existing 359 lines |
| Other files changed | **0** |
| Commits made | **0** |

---

**End of determination.**

| Field | Value |
|---|---|
| Baseline | `bae59755d7e2d3566c93b89c722b68847145269a` · `integration/recovery-001` |
| Sections | 14 |
| Subjects | `EEG-1`, `EEG-2` |
| Root causes | **1** |
| Migration sites | **3** (`M-6`, `M-7`, `M-8`) |
| Populations brought under `INV-14` | **6** — 60 terms |
| Feasibility probes run | **4**, all in memory |
| `CREATE` acts | **0** |
| New registries · identity systems · authority systems · frameworks | **0 · 0 · 0 · 0** |
| Constitutional amendments required | **0** |
| Open constitutional questions | **1** (`C-1`, pre-existing, located in `CEP-MOD-002` §12.2) |
| Code changed | **0 files** |
| Registries changed | **0** |
