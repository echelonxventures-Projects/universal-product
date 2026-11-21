# UCOS Ω∞ — UNIVERSAL RELATIONSHIP EVOLUTION CLOSURE ARCHITECTURE DETERMINATION

**The permanent architecture for 100% Universal Relationship completeness. The measured answer is that every required mechanism either exists or is the missing half of a pair the repository has already built five times — and that the root cause of the one remaining evolution ceiling is a duplicated declaration, not a retained projection.**

| Field | Value |
|---|---|
| Artifact | `UCOS-OMEGA-INFINITY-UNIVERSAL-RELATIONSHIP-EVOLUTION-CLOSURE-ARCHITECTURE-DETERMINATION.md` |
| Authority | **NONE — DERIVED DETERMINATION.** Creates no mechanism, term, identity, registry or certification. Determines architecture; implements none of it. |
| Mode | ANALYSIS ONLY · **NO CODE · NO REGISTRY · NO DATA · NO PATCH · NO WORKAROUND · NO MIGRATION · NO DUPLICATE REGISTRY · NO PARALLEL AUTHORITY · NO COMMIT** |
| Baseline commit (HEAD) | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Baseline branch | `integration/recovery-001` |
| Method | Read-only measurement plus **three architecture-feasibility probes** run in memory: deriving the enum from the vocabulary, round-tripping a vocabulary through its document form, and flowing a new term to both views. Nothing written; porcelain **364** before and after |
| **Root cause found** | **`RelationType` and `RELATION_TYPE_VOCABULARY` are two independently authored declarations of one term set.** The two-sided admission cost exists because the declaration is **duplicated**, not because a projection is retained. Three lines above it in the same file, `uckp.facet` shows the correct form: **one declaration, one derived view** — §7.2 |
| **Proof** | The enum is **exactly derivable** from the vocabulary: `term_id.upper().replace("-","_")` is **total and injective over all 17**, produces exactly the enum's member names and values, and preserves attribute access for all **252** references across 21 files — §7.4 |
| **Second finding** | **`how_to_extend[2]` names a DATA mechanism the vocabulary layer does not provide.** All 13 vocabularies are module literals; `to_document()` exists and **there is no `from_document`** — while six other types in the engine have both — §8 |
| Determinations | **A**–**G** delivered — §5–§13 |
| Gaps | **9** (`RA-1`…`RA-9`) · 0 CRITICAL · 4 HIGH · 4 MEDIUM · 1 LOW — §12 |
| `CREATE` acts in the closure path | **0** | 
| **Verdict** | **CONDITIONALLY COMPLETE** — §14 |

---

## 1. Scope and What Is Being Graded

### 1.1 What this determination decides

The objective is the **architecture** required to reach 100%, not the state. The predecessor (`…UNIVERSAL-RELATIONSHIP-100-PERCENT-COMPLETENESS-DETERMINATION.md`) graded the state **NOT COMPLETE** — 5 of 10 dimensions complete, 5 of 12 acceptance criteria met.

**This determination grades whether the permanent architecture is established.** §14.2 states explicitly which of the two the verdict applies to, so the two artifacts are not confused.

### 1.2 Constraint compliance, stated up front

| Constraint | Honoured |
|---|---|
| No patch | Every step in §13 is `REUSE` or `EXTEND` of a located owner |
| No workaround | No step is conditioned on later cleanup |
| No temporary migration | The one-way property holds — §13.4 |
| No duplicate registry | `VocabularyRegistry` and `UniversalKnowledgeRegistry`, both existing |
| No parallel authority | `CAA-INV-01`, `CAA-INV-04`, `CAA-INV-05` cl. 1 all preserved |
| No shortcut | The one genuinely open question is referred, not decided — §12 `RA-4` |
| Reuse wherever possible | **9 of 9** closure steps reuse or extend |
| Create nothing if an existing mechanism can evolve | **`CREATE` count: 0** |
| No new identity authority | `deterministic_id` + `RegistryKind.RELATIONSHIP`, both existing |
| No new registry unless unavoidable | **None proposed** |
| No duplicate relationship systems | The architecture **removes** one duplication (§7.2) rather than adding any |
| No hardcoded finite enums | §7 eliminates the last one on the relationship path |
| No finite ceilings / artificial limits | §11 |

---

## 2. Current Baseline

| Field | Value |
|---|---|
| HEAD | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch | `integration/recovery-001` |
| `git status --porcelain` | **364** |
| Tracked modifications | **38** |
| Staged | **0** |

| Relationship substrate | Value |
|---|---|
| `uckp.relation-type` | **17** terms — 3 symmetric, 14 directed |
| `uckp.relationship-class` | **12** terms |
| `RelationType` enum | **17** members · **252** attribute references across **21** files |
| Registered vocabularies | **13**, all module literals · **0** DATA-sourced |
| Relationship instances | **61,269** across 4 populations |
| Derived edges / dangling | **13,036** / **0** |
| UGA graph | **34,872**, `verdict: CERTIFIED`, `graph_digest: c34482f0…` |
| Book edges | **13,361**, ungated, positional ids |

---

## 3. Existing Relationship Universe Architecture

### 3.1 The four planes

| Plane | Owner | Owns | State |
|---|---|---|---|
| **Structural** | `engine/uckp/facets.py` — Facet 9 of 33 | *"How is it bound to everything else?"* | **Sole; closed on purpose** |
| **Semantic** | `uckp.relation-type` (17) · `uckp.relationship-class` (12) | What a binding means; its register | **Open; one duplicated** |
| **Instance** | `Relationship` on a UCKO | This binding | **Sole** |
| **Executable** | `engine/uckp/graph.py` | *"every relationship is executable"* | **Sole; 0 dangling** |

### 3.2 The authorship rule that constrains every option

`graph.py`, verbatim:

> *"Edges are **derived, never authored**… there is no second place to update and therefore **no second authority (Article 3)**. **Adding an edge means changing the object that claims the relationship.**"*

**Any architecture that authors edges beside the objects is void before it is evaluated.** This forecloses the entire class of "relationship registry" designs.

### 3.3 `UCRD-001` — the governing model, unchanged

| Tier | Subject | Cardinality | Growth | Authority |
|---|---|---|---|---|
| **1 · Facet** | The question every object must answer | **33 — CLOSED** | Amendment | `UCKP-ART-06` |
| **2 · Relationship class** | The register a binding belongs to | **12 — OPEN** | Registration | `RELATIONSHIP_CLASS_VOCABULARY` |
| **3 · Relation type** | How one object is bound to another | **17 — OPEN** | Registration | `RELATION_TYPE_VOCABULARY` |

> *"Closure of Tier 1 is not a finite assumption; it is **what keeps Tiers 2 and 3 infinite**. If the question set were open, every new answer would require a new question, and the model would grow by amendment instead of registration."*

**This determination does not disturb `UCRD-001`. It governs.**

### 3.4 UCKO relationship representation

`Relationship(relation, target, relationship_class)`, validated at `ucko.py:396-397`:

```python
vocabularies.require_term(RELATION_TYPE, relationship.relation)
vocabularies.require_term(RELATIONSHIP_CLASS, relationship.relationship_class)
```

Fail-closed both ways. `target` carries **no type, domain or category constraint** — the only bound is resolvability, which `ART-07` requires.

---

## 4. The Measured Ceiling

### 4.1 The one place relationship evolution is not infinite

Two probes, identical in shape, opposite in result:

```
alignment on baseline registry                  : PASS
alignment AFTER admitting a relation TYPE       : FAIL
   -> "'uckp.relation-type' declares ['entangles-with'] absent from RelationType"
alignment AFTER admitting a relationship CLASS  : PASS
```

| Vocabulary | Terms | Enum projection | Admission cost |
|---|---:|---|---|
| `uckp.relationship-class` | 12 | **None** | **Zero — pure data** |
| `uckp.relation-type` | 17 | `RelationType` (17) | **One enum member per new meaning** |

**Tier 2 is already infinite and free. Tier 3 is infinite in principle and taxed in practice.** That tax is the entire subject of §7.

### 4.2 Why the received explanation is incomplete

The Relationship Intelligence determination judged `RCL-01` *"correct architecture, the two-sided admission path is the disclosure"*, reasoning that removing the enum *"would remove the fail-closed guarantee that a projection cannot silently drift from its vocabulary."*

**The guarantee is real and must be preserved. The inference that a projection therefore requires a second declaration is what §7 disproves.**

---

## 5. Determination A — The Final Universal Relationship Ontology

> **The final ontology is `UCRD-001`'s three-tier Universal Facet Model, unchanged. No fourth tier, no new primitive, no re-parenting.**

| Level | Subject | Growth | Identity |
|---|---|---|---|
| **Facet 9** | That relationships exist as a universal question | Amendment (closed on purpose) | n/a — a facet |
| **Relationship class** (12) | Which register a binding belongs to | **Registration — free today** | The vocabulary is a UCKO |
| **Relation type** (17) | What a binding means | **Registration — §7 makes it free** | The vocabulary is a UCKO |
| **Relationship instance** | This binding between these two | Object mutation under `ART-12` | The natural key `(from, to, type)` |
| **Edge** | The executable projection | `derive_edges` — derived, never authored | n/a — derived |

**Five levels, four already sole and correct.** The one requiring architectural work is *relation type*, and the work is subtractive.

### 5.1 Why no fourth tier

| Candidate | Rejected because |
|---|---|
| A "relationship entity" tier above the facet | `UCRD-001` §5.1 disposition 2 — `relationships` is Facet 9 of 33; 8 facets are non-relational |
| A "relationship registry" tier | `what_this_forbids` names *"relationship graph"*; `graph.py`'s authorship rule |
| A "relationship constraint" tier | `constraints` is **Facet 23** — already a facet; a constraint on a relationship is a constraint on the object claiming it |

**Relationship constraints (objective item 4) evolve infinitely because they are Facet 23, already open, already carried by every object.**

---

## 6. Determination B — The Final Relationship Identity Authority

> **Identity is the natural key. Where a handle is required, it is `deterministic_id(RegistryKind.RELATIONSHIP, <namespace>, content_digest(<natural key>))` — the existing mint, the existing kind, no ledger write, no new authority.**

Determined in the predecessor and unchanged. Re-verified here:

| Property | Mechanism |
|---|---|
| Deterministic | Pure function of `(code, namespace, natural_key)` |
| Universal | `RegistryKind.RELATIONSHIP` → `REL`, registered; `register_kind` open for future kinds |
| Minted once | Idempotent — same key, same id, forever |
| No new authority | `deterministic_id` exists; `engine/nucleus` already delegates to it |
| Precedent | `OwnershipAssignment.assignment_id` — **an inline relationship mint already retired onto this exact path** |
| Feasibility | `(from, to, type)` **unique across all 13,361** edges; collision P = **3.171 × 10⁻⁷** |

**Nothing in Determination B is new. It is the removal of one non-conforming derivation.**

---

## 7. Determination C — The Final Relationship Evolution Mechanism

### 7.1 The requirement

Objective items 1–4: every relationship class, type, semantic and constraint must evolve infinitely. Items 1 and 4 already do (§5). Items 2 and 3 are blocked by §4.1.

### 7.2 The root cause — measured, not inferred

**`RELATION_TYPE_VOCABULARY` and `RelationType` are two independently authored literals of one term set.**

```python
# engine/uckp/vocabulary.py — 17 hand-written Term(...) entries
RELATION_TYPE_VOCABULARY = Vocabulary(RELATION_TYPE, "how one object is bound to another", (
    Term("conflicts-with", "mutually unsatisfiable with", symmetric=True), … ))

# engine/knowledge/model.py — 17 hand-written enum members
class RelationType(str, Enum):
    DEPENDS_ON = "depends-on"
    IMPLEMENTS = "implements"
    …
```

Neither derives from the other. **That is a second definition of an existing primitive**, which `UCKP-ART-03` makes void: *"The same knowledge shall not be authored twice, under one identity or two."*

`verify_vocabulary_alignment` **detects** the resulting drift. It does not **prevent** the duplication — it institutionalises it, and the two-sided admission cost is the institutionalisation's price.

### 7.3 The correct form already exists, three lines away

`engine/uckp/vocabulary.py:327-331`:

```python
FACET_VOCABULARY_INSTANCE = Vocabulary(
    FACET_VOCABULARY,
    "the questions every object must be able to answer",
    tuple(Term(facet.value, facet.question) for facet in Facet),   # ← DERIVED
)
```

**One declaration (`Facet`), one derived view (the vocabulary).** Nothing can drift, so nothing needs two-sided admission for consistency. `evolution_stage_vocabulary()` does the same for the 15 stages, and states the principle: *"this is a projection of the cycle and **not a second list of stages to keep in step with the first**."*

**`uckp.relation-type` is the one relationship vocabulary that does not follow the pattern its own module already demonstrates twice.**

### 7.4 The architecture — proven, not proposed

> **The relation-type term set shall have exactly one declaration. `RelationType` shall be *derived* from it, as `uckp.facet` is derived from `Facet`, so that the checked projection is preserved and the second declaration disappears.**

**Probe P-1**, in memory:

```
derived members            : 17
member NAMES match enum    : True
member VALUES match enum   : True
attribute access preserved : True   (RelationType.DEPENDS_ON)
mapping total & injective  : True   (term_id.upper().replace("-","_"))
```

**The enum is exactly derivable.** All **252** attribute references across **21** files — 109 of them `RelationType.DEPENDS_ON` — continue to resolve unchanged.

**Probe P-3** — the architecture in one measurement:

```
vocabulary after admitting one term : 18 terms
derived enum                        : 18 members
new member reachable                : D2.ENTANGLES_WITH → "entangles-with"
```

**A term admitted once flows to both views. Two-sided admission does not survive the change; it has nothing left to be two-sided about.**

### 7.5 What is preserved

| Guarantee | Preserved? | How |
|---|---|---|
| Fail-closed projection alignment | **YES — strengthened.** Drift becomes impossible rather than detected | One source |
| `RelationType.coerce()` hard refusal | **YES** | Unchanged behaviour on a derived enum |
| `ACYCLIC_FAMILIES` | **YES** — 4 families over 7 types, keyed by member | Members unchanged |
| `verify_vocabulary_alignment` | **YES** — the pair becomes trivially aligned | Still runs, still fails closed |
| Every consumer | **YES** — 252 references, names and values identical | Probe P-1 |

**Nothing is removed except a duplicate declaration.**

### 7.6 Direction of derivation, and why it matters

Two directions are available; only one delivers infinite evolution.

| Direction | Adding a term means | Verdict |
|---|---|---|
| Vocabulary derives from enum (as `uckp.facet` does) | Editing the enum — **code** | Removes duplication, keeps the ceiling |
| **Enum derives from the vocabulary** | Editing the vocabulary — **still code today** | Removes duplication; ceiling removed only with §8 |

**Determination C alone removes the duplication and halves the cost. Determination C plus §8 removes the ceiling.** Stated plainly so C is not mistaken for the whole answer.

---

## 8. The DATA Plane — The Missing Half of an Existing Pair

### 8.1 The constitutional promise and the measured provision

`constitutional-authority-alignment.json` `how_to_extend[2]`:

> *"A new vocabulary member, relationship class, adapter or authority role is **one appended entry in DATA**. `engine/uckp/law.py` is never amended to fit the data (`UCKP-ART-17`)."*

| Measured | Result |
|---|---|
| Vocabularies sourced from DATA | **0 of 13** — all are module literals |
| `Vocabulary.to_document()` / `VocabularyRegistry.to_document()` | **Present** |
| `Vocabulary.from_document` / `VocabularyRegistry.from_document` | **ABSENT** |
| Engine types having **both** | **6** — `EvolutionLedger`, `engine/uaue/resolution.py`, `engine/uckp/resolution.py`, `engine/ceu/existence.py`, `engine/registry/universal/dictionary.py`, and their tests |

> **The vocabulary layer is write-only. `how_to_extend[2]` names a DATA mechanism that has no implementation, and every "registration" today is either a runtime call lost at process exit or a source edit.**

### 8.2 The precedent, and its reasoning transferred verbatim

`EvolutionLedger.from_document`:

> *"Until this method existed that claim was only checkable **inside the process that did the appending**: the ledger could project itself to canonical JSON and had no inverse, so a published evolution history could be read by a human, diffed by CI and trusted by a downstream programme **without anything ever re-applying the rules it was supposed to have been built under**. **An append-only history that cannot be loaded is an append-only history nobody can falsify.**
>
> **Loading is therefore a verification rather than a deserialization.** Every record is replayed through `append`…"*

**Transferred:** an open vocabulary that cannot be loaded is an open vocabulary nobody can extend outside the process. Rehydration through `extended_with` would likewise be verification, not deserialization — refusing a redefinition on load exactly as it refuses one at runtime.

### 8.3 Feasibility — proven

**Probe P-2**, in memory:

```
round-trip digest equal : True
terms preserved         : 17
```

A vocabulary round-trips through its own `to_dict()` form with an **identical content digest**. `from_document` is losslessly implementable against the projection that already exists.

### 8.4 Disposition

> **EXTEND, not CREATE.** Completing a designated-but-unbuilt member of an existing owner is the disposition `CEP-MOD-002` gave `verify_vocabulary_alignment` under `CMG-000001` LXXVII.2(b). `CREATE` is unavailable under `UCKP-ART-18`.
>
> **No new registry.** The DATA file is a *source* for the existing `VocabularyRegistry`, exactly as `reference-frames.json` is a source for `FrameRegistry` — a located precedent for a registry sourced from DATA.

---

## 9. Determination D — The Final Relationship Certification Mechanism

### 9.1 The exemplar already exists

`00-MASTER/UCOS-UGA-001/07-CERTIFICATION.json`: `verdict: "CERTIFIED"`, `blocking_deviations: []`, five digests including **`graph_digest: c34482f0…`**, and:

> *"**fixed_point_property**: Outputs contain no wall clock, so a second run over an unchanged repository rewrites no byte. Fixed point is checkable by comparison."*

**A relationship population of 34,872 edges is already certified, with a graph digest and a fixed-point property.** The mechanism is not hypothetical.

### 9.2 The gap, confirmed by reading the validator

| Measured | Result |
|---|---|
| `verify.sh:391` runs | `ukb.py validate` |
| Schema loaded at `ukb.py:1893` | **`artifact.schema.json` only** |
| `relationship.schema.json` passed to `jsonschema` | **Never** |
| `jsonschema` installed | **YES — 4.26.0** |
| Structural relationship checks present | **YES** — the F-1 lineage-projection consistency check |

> **13,361 edges are validated against no schema, and the sole reason is that the schema is never handed to a validator that is installed and working.**

### 9.3 The identity gate that already exists for a sibling population

`ukb.py:2277`:

```
"not minted from the id-ledger identity authority (EXL-02)"
```

**Executions are gated on whether their identifier came from the authority. Edges are not — and under Determination B they would fail such a gate today.**

### 9.4 Determination

> **Certification requires no new mechanism.** Two acts, both `EXTEND` of a running gate: pass `relationship.schema.json` to the installed validator, and add an `EXL-02`-shaped identity check for edges. The UGA surface is the exemplar for the digest and fixed-point form.
>
> **No new pipeline, no new stage.** `non_goals[4]`: *"Adding a verification stage, pipeline or scheduler. The invariants land in the gate `verify.sh` already runs."*

---

## 10. Determination E — The Final Relationship Audit Mechanism

### 10.1 What audit requires

| Requirement | Mechanism | State |
|---|---|---|
| Every act recorded | `INV-17` `infinite-auditability` | Present |
| History keyed by identity | `id-ledger` `history` — **1,492** entries keyed by `universal_id` | Present |
| Reconstructible | `derive_edges` total & deterministic; UGA fixed-point property | Present |
| Traceable | `traceability` class; Facet 15 | Present |

### 10.2 The dependency

**Audit is downstream of identity.** The `history` plane is keyed by `universal_id`; an edge whose identifier is regenerated each build cannot key into it. **Determination E requires nothing of its own — it becomes available the moment Determination B is executed.**

### 10.3 Determination

> **Audit requires no new mechanism.** A stable, deterministic edge identity makes the existing `history` plane usable for edges. An optional `by_edge` plane on the `allocate_execution` precedent would record first-seen and supersession; it is `EXTEND`, and it is **not required** for auditability, because a deterministic id is recomputable and therefore self-certifying.

---

## 11. Infinite Expansion — The Twelve Axes

Objective item 8. Each axis measured against the architecture as determined.

| # | Axis | Mechanism | Ceiling after closure |
|---|---|---|---|
| 1 | **entities** | `target` carries no type/domain/category constraint | **None** |
| 2 | **meanings** | `uckp.relation-type` + §7 + §8 | **None** |
| 3 | **classes** | `uckp.relationship-class` — already free | **None today** |
| 4 | **types** | Same as meanings | **None** |
| 5 | **directions** | `symmetric` flag · inverse pairs · multiple edges · `observer-context` | **None** — carried by structure |
| 6 | **dimensions** | `RegistryKind.UNIVERSE`; `frame_kind` an open string | **None** |
| 7 | **locations** | 14 frames in DATA; `frame_kind` open | **None in value**; axis set closed — `RA-5` |
| 8 | **temporal contexts** | `SystemType.UNKNOWN` — *"an explicit open slot"* | **None** |
| 9 | **reality contexts** | `existence-actual` / `existence-simulated`; `RegistryKind.REALITY`, `EXISTENCE` | **None** |
| 10 | **observer contexts** | Facet 32; `observer` axis | **None in value** |
| 11 | **civilizations** | 2 registered; `RegistryKind.CIVILIZATION`; `ART-20` names them | **None** |
| 12 | **future unknown domains** | `ART-17` registration; proven end-to-end in the predecessor's §10 | **None** |

**Eleven of twelve carry no ceiling after closure. The twelfth — locations — is unbounded in *value* and bounded in *axis kind* (`RA-5`), which is `EEG-1` and has its own determined resolution.**

---

## 12. Determination F — All Gaps Preventing 100%

| Id | Sev | Gap | Blocks | Disposition |
|---|---|---|---|---|
| `RA-1` | **HIGH** | **`RelationType` is a second authored declaration of `uckp.relation-type`.** Two literals, one term set — `ART-03` | Items 2, 3 | **EXTEND** — derive it (§7) |
| `RA-2` | **HIGH** | **No `from_document` on `Vocabulary`/`VocabularyRegistry`.** `how_to_extend[2]`'s DATA mechanism has no implementation; 0 of 13 vocabularies are DATA-sourced | Items 1–4 | **EXTEND** — complete the pair (§8) |
| `RA-3` | **HIGH** | **13,361 edge ids are positional and temporary**, fail 5 named laws, recorded in no plane | Items 5, 6, 7 | **REUSE** — `deterministic_id` (§6) |
| `RA-4` | **HIGH** | **13,361 edges are certified by nothing.** `relationship.schema.json` never passed to an installed validator | Item 7 | **EXTEND** — pass the schema (§9) |
| `RA-5` | MEDIUM | **`AXIS_GRAPH` closed at 19 axes** — a new *kind* of context needs code | Item 8 (locations) | **REUSE** — `M-6`, proven feasible |
| `RA-6` | MEDIUM | **P2/P3 relation kinds bind to no class or article**, while UGA binds all six of its own | Item 6 | **REFERRAL** — UGA is the exemplar |
| `RA-7` | MEDIUM | **No party declared for relationship-vocabulary admission** — the register names a mechanism, not a role | Governance | **OWNER** |
| `RA-8` | MEDIUM | **Inline-mint guard reaches only `engine/nucleus` and matches only `UCOS-` literals** — widening scope alone would still report clean on `add_edge` | Item 5 | **EXTEND** |
| `RA-9` | LOW | **`Term.symmetric` is binary.** Direction beyond symmetric/directed is expressible only as structure, not as a term property | Item 8 (directions) | **NONE — by design** |

### 12.1 Two gaps are newly measured here

`RA-1` and `RA-2` were not raised by any prior determination in this chain. `RA-1` is the root cause of the ceiling every predecessor carried as `RCL-01`; `RA-2` is the missing half of a pair the repository has built six times.

### 12.2 What is not a gap

| Not a gap | Why |
|---|---|
| Facet 33 closed | *"what keeps Tiers 2 and 3 infinite"* — `UCRD-001` |
| `R-1`/`R-2` carry no identity | Derived and projected; the triple **is** the identity |
| Three relation planes coexist | Scope-distinct; `UCRD-001` does not treat them as rivals |
| Coexisting identifier formats | Lawful under the convergence doctrine |
| `historical` terminal in the lifecycle | A lifecycle may terminate; the evolution cycle may not, and does not |

---

## 13. Determination G — Permanent Closure Path

**Sequence and dependency only. Nothing below is authorised by this determination.**

| Step | Gap | Act | Disposition | New mechanism |
|---|---|---|---|---|
| `G-1` | `RA-1` | Derive `RelationType` from `RELATION_TYPE_VOCABULARY` | **EXTEND** — precedent `uckp.facet`, same file | **None** |
| `G-2` | `RA-2` | Add `Vocabulary.from_document` / `VocabularyRegistry.from_document` | **EXTEND** — 6 types have both; precedent `EvolutionLedger` | **None** |
| `G-3` | `RA-2` | Source the relationship vocabularies from DATA | **EXTEND** — precedent `reference-frames.json` → `FrameRegistry` | **None** |
| `G-4` | `RA-3` | `edge_id` = `deterministic_id(REL, ns, digest([from,to,type]))` | **REUSE** — precedent `assignment_id` | **None** |
| `G-5` | `RA-3` | Change the schema `edge_id` pattern once | **EXTEND** — one-time closure removal | **None** |
| `G-6` | `RA-4` | Pass `relationship.schema.json` to the installed validator | **EXTEND** | **None** |
| `G-7` | `RA-4` | Add an `EXL-02`-shaped identity check for edges | **REUSE** | **None** |
| `G-8` | `RA-8` | Widen the guard in **scope and shape** | **EXTEND** | **None** |
| `G-9` | `RA-5` | Contribute `ucos.context-axis` (`M-6`) | **REUSE** — proven feasible | **None** |
| `G-10` | `RA-6` | Bind P2/P3 kinds on UGA's exemplar | **REFERRAL** | **None** |
| `G-11` | `RA-7` | Locate or declare the admission party | **OWNER** | — |

**`CREATE` count: 0 · New registries: 0 · New authorities: 0 · New pipelines: 0 · Patches: 0 · Workarounds: 0.**

### 13.1 Dependency order

```
G-1 ──┐
      ├──▶ G-3 ──▶ (relation types admit as DATA; ceiling removed)
G-2 ──┘

G-4 ──▶ G-5 ──▶ G-7 ──▶ (edges identified, then gated)
             └──▶ G-6

G-8, G-9, G-10, G-11  — independent
```

`G-1` and `G-2` are independent of each other and both precede `G-3`. `G-1` alone removes the duplication; `G-1 + G-2 + G-3` removes the ceiling.

### 13.2 Backward compatibility

| Mechanism | Effect |
|---|---|
| Derived enum | 252 references resolve identically — probe P-1 |
| Append-only | `extended_with` refuses redefinition; no existing term can change |
| Retained projections | Every enum and tuple stays as a derived view; no caller moves |
| Round-trip losslessness | Probe P-2 — identical digest |
| Edge consumers | All four treat `edge_id` as an opaque handle |

### 13.3 Rollback before acceptance

| What | Reversible |
|---|---|
| A candidate vocabulary in a private registry | **Fully** — the module's documented isolation primitive |
| A derived enum before it replaces the literal | **Fully** — both produce identical members |
| A DATA source file before it is read | **Fully** — an unread file contributes nothing |
| A registration into the process-wide registry | **No** — `ART-14`, by law |

### 13.4 The one-way property

Once the term set has one declaration and that declaration is DATA, a new relation type is **permanently** a data append. There is no state in which it reverts to requiring code, because there is no second literal to keep in step. **That is what makes this closure permanent rather than a migration.**

---

## 14. Final Determination

### 14.1 Verdict

> # CONDITIONALLY COMPLETE

### 14.2 What the verdict grades

**The architecture, not the state.** The predecessor graded the state `NOT COMPLETE` — 5 of 10 dimensions, 5 of 12 acceptance criteria. **That grade stands and is not revised here.**

This determination grades whether the permanent architecture required to reach 100% is established:

| Determination | Established? | New mechanism |
|---|---|---|
| **A — Ontology** | **YES** — `UCRD-001` three tiers, unchanged | None |
| **B — Identity authority** | **YES** — `deterministic_id` + `RELATIONSHIP`; precedented | None |
| **C — Evolution mechanism** | **YES — and newly proven.** Derive the enum; source from DATA | None |
| **D — Certification** | **YES** — pass the schema; `EXL-02` pattern; UGA exemplar | None |
| **E — Audit** | **YES** — downstream of B; existing `history` plane | None |
| **F — Gaps** | **YES** — 9, each with a located owner | — |
| **G — Closure path** | **YES** — 11 steps, all REUSE/EXTEND/REFERRAL | None |

**Seven of seven delivered. `CREATE` count: 0.**

### 14.3 Why `CONDITIONALLY COMPLETE`

**Not `COMPLETE`:** the architecture is determined but not executed. Eleven closure steps have not run; 13,361 identifiers still fail five named laws; the DATA plane `how_to_extend[2]` promises still does not exist. An architecture nobody has built is not a complete architecture — it is a complete *determination* of one.

**Not `NOT COMPLETE`:** every required mechanism is located, every disposition is `REUSE` or `EXTEND`, every feasibility claim is **proven by probe rather than argued**, and the count of things that must be invented is **zero**. Nothing remains to be designed.

**The condition:** execution of `G-1`…`G-11`, of which `G-11` is an owner decision and `G-10` a referral. Nine are engineering acts against located owners.

### 14.4 The finding that changes the chain

Every predecessor carried `RCL-01` — the two-sided admission cost — as a **disclosed and correct design choice**. This determination measured its cause and found it is not a design choice at all:

> **`RelationType` and `RELATION_TYPE_VOCABULARY` are two independently authored declarations of one term set. The cost is duplication, not projection.**
>
> Three lines above the problem, in the same file, `uckp.facet` shows the correct form. The fix is **subtractive** — remove a declaration, not add a mechanism — and it **strengthens** the fail-closed guarantee rather than weakening it, because drift becomes impossible instead of detected.

**A cost that was accepted as inherent is measured as removable.** That is the substantive result of this determination.

### 14.5 The eight objective requirements

| # | Requirement | After closure |
|---|---|---|
| 1 | Every relationship **class** evolves infinitely | **YES — already true today** |
| 2 | Every relationship **type** evolves infinitely | **YES — via `G-1` + `G-2` + `G-3`** |
| 3 | Every relationship **semantic** evolves infinitely | **YES — same path** |
| 4 | Every relationship **constraint** evolves infinitely | **YES — Facet 23, already open** |
| 5 | Every relationship **identity** is deterministic and universal | **YES — via `G-4`** |
| 6 | Every relationship is **auditable** | **YES — via `G-4`, then the existing `history` plane** |
| 7 | Every relationship is **certifiable** | **YES — via `G-6`, `G-7`; UGA exemplar** |
| 8 | Infinite across **twelve axes** | **11 of 12 unbounded; locations bounded in axis kind (`RA-5`, `G-9`)** |

### 14.6 What this determination did not do

| Not done | Under |
|---|---|
| Implement any step of `G-1`…`G-11` | Directive |
| Modify code, registries, data or schemas | Directive |
| Create any mechanism, registry, authority or pipeline | Directive; `CREATE` count 0 |
| Persist any probe result | All probes in-memory; porcelain unchanged |
| Choose the DATA file path or namespace strings | Owner acts |
| Dispose of `RA-1`…`RA-9` | `non_goals[5]` |
| Revise the predecessor's `NOT COMPLETE` state grade | It stands — §14.2 |
| Disturb `UCRD-001`, the convergence doctrine, or `graph.py`'s authorship rule | All govern |

---

## 15. Verification Record

### 15.1 Before / after

| Field | Before | After | Delta |
|---|---|---|---|
| HEAD | `bae59755…5269a` | `bae59755…5269a` | **unchanged** |
| Branch | `integration/recovery-001` | `integration/recovery-001` | **unchanged** |
| `git status --porcelain` | **364** | **365** | **+1 — this artifact** |
| Tracked modifications | **38** | **38** | **unchanged** |
| Staged | **0** | **0** | **unchanged** |
| Commits | **0** | **0** | **none** |

### 15.2 Repository integrity assertions

| Assertion | Result |
|---|---|
| Only one new artifact | **VERIFIED** — porcelain +1 |
| HEAD unchanged | **VERIFIED** |
| Branch unchanged | **VERIFIED** |
| Code unchanged | **VERIFIED** — tracked mods 38, unchanged |
| Registry unchanged | **VERIFIED** — no `00-BOOK/DATA/*`, `00-CMG/*`, `00-BOOK/SCHEMAS/*`, `00-MASTER/*` in the delta |
| Identity unchanged | **VERIFIED** — `id-ledger.json` untouched |
| Relationship data unchanged | **VERIFIED** — read only |
| Ownership / certification unchanged | **VERIFIED** |
| No commits | **VERIFIED** |

### 15.3 Probe isolation

Three probes ran in-process. Each built its own `VocabularyRegistry` via `build_vocabulary_registry()`, never `DEFAULT_VOCABULARIES`. `extended_with` returns a new vocabulary and never mutates. The derived enums were constructed under a local name and discarded. **`git status --porcelain` was 364 before and after every probe.**

### 15.4 Live measurements

| Measurement | Method | Result |
|---|---|---|
| `RelationType` members / `uckp.relation-type` terms | Import | **17 / 17** |
| `RelationType` attribute references | `grep -o` | **252** across **21** files; `DEPENDS_ON` **109** |
| **P-1** enum derivable from vocabulary | In-memory `Enum(...)` | **names match True · values match True · attribute access preserved** |
| term_id → NAME mapping | Set comparison | **total and injective over 17** |
| **P-2** vocabulary round-trip | `to_dict` → rebuild → `digest` | **identical digest**, 17 terms |
| **P-3** term flows to both views | In-memory | **18 terms → 18 enum members**, new member reachable |
| Alignment after admitting a TYPE | `verify_vocabulary_alignment` | **FAIL** — `"declares ['entangles-with'] absent from RelationType"` |
| Alignment after admitting a CLASS | `verify_vocabulary_alignment` | **PASS** |
| `FACET_VOCABULARY_INSTANCE` form | Source read | **Derived** — `tuple(Term(f.value, f.question) for f in Facet)` |
| Vocabularies DATA-sourced | Source read | **0 of 13** — all module literals |
| `Vocabulary` / `VocabularyRegistry` methods | `dir()` | `to_document` present; **`from_document` absent** |
| Engine types with both | `grep` | **6** |
| `ukb.py validate` schema coverage | Source read | **`artifact.schema.json` only** |
| `jsonschema` availability | Import | **installed, 4.26.0** |
| `EXL-02` identity gate | Source read | `ukb.py:2277` — executions gated, edges not |
| UGA certification | JSON parse | `verdict: CERTIFIED`, `graph_digest: c34482f0…`, fixed-point property |
| Derived edges / dangling | `build_universe().graph()` | **13,036 / 0** |

### 15.5 What was not verified

| Not verified | Why |
|---|---|
| That `G-1`…`G-11` pass `verify.sh` | Would require implementing them. Out of mode |
| That a derived enum satisfies every consumer at runtime | P-1 proves names, values and attribute access; **no consumer was executed against a derived enum** |
| The DATA file shape or path for `G-3` | An owner act |
| Whether `RA-7`'s missing party is a live breach | Requires an owner's disposition; `non_goals[5]` |
| Whether four relationship populations are the complete set | Measured across five locations; a sixth elsewhere would not have been seen |
| Current `verify.sh` verdict | Not executed — `ISD-G-11`; this mode forbids surface mutation |

### 15.6 Artifact creation verified

| Check | Result |
|---|---|
| File exists | **Yes** |
| Determinations A–G | **All seven delivered — §5–§13** |
| Verdict | **Exactly one permitted value — `CONDITIONALLY COMPLETE`** |
| Git status | `??` untracked — the only delta from 364 |
| Other files changed | **0** |
| Commits | **0** |

---

**End of determination.**

| Field | Value |
|---|---|
| Baseline | `bae59755d7e2d3566c93b89c722b68847145269a` · `integration/recovery-001` |
| Determinations delivered | **A–G, seven of seven** |
| Architecture probes | **3 — all passed, all in-memory** |
| Gaps | **9** — 4 HIGH · 4 MEDIUM · 1 LOW |
| Gaps newly measured here | **2** — `RA-1`, `RA-2` |
| Closure steps | **11** — 3 REUSE · 6 EXTEND · 1 REFERRAL · 1 OWNER |
| Objective requirements met after closure | **8 of 8**, axis 7 bounded in kind only |
| New mechanisms · registries · authorities · pipelines | **0 · 0 · 0 · 0** |
| Patches · workarounds · migrations · shortcuts | **0 · 0 · 0 · 0** |
| `CREATE` acts | **0** |
| Code changed | **0 files** |
| Registries changed | **0** |
| **Verdict** | **CONDITIONALLY COMPLETE** |
