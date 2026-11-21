# UCOS Ω∞ — G-1 RELATIONTYPE DERIVED PROJECTION IMPLEMENTATION READINESS DETERMINATION

**Whether `RelationType` can be derived from the canonical relationship vocabulary, eliminating a duplicate declaration authority. The measured answer is that it can, that a derived projection preserves all twelve consumer contracts under probe, that the dependency reversal creates no import cycle — and that the duplication is threefold, not twofold.**

| Field | Value |
|---|---|
| Artifact | `UCOS-OMEGA-INFINITY-G1-RELATIONTYPE-DERIVED-PROJECTION-READINESS-DETERMINATION.md` |
| Authority | **NONE — DERIVED DETERMINATION.** Implements nothing, declares no term, changes no projection. Determines readiness; executes none of it. |
| Mode | ANALYSIS ONLY · **NO CODE · NO JSON · NO REGISTRY · NO MIGRATION · NO COMMIT** |
| Baseline commit (HEAD) | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Baseline branch | `integration/recovery-001` |
| Subject | `G-1` from `…EVOLUTION-CLOSURE-ARCHITECTURE-DETERMINATION.md` §13 |
| Method | Read-only measurement plus **five in-memory probes**: a full derived-enum construction exercised against twelve consumer contracts, a transitive import-closure computation, symmetry-parity comparison, table-totality measurement, and digest comparison. Nothing written; porcelain **365** before and after |
| **Central finding** | **The derived projection preserves every measured consumer contract.** 12 of 12 behavioural checks pass — attribute access, `coerce` including its refusal semantics, `is_symmetric`, `str` identity, hashability, frozenset membership, JSON serialization — §7 |
| **Second finding** | **The duplication is threefold, not twofold.** `_SYMMETRIC_RELATIONS` is a third independent declaration of a fact `Term.symmetric` already carries. Measured: the two agree **exactly** on all three symmetric types — §5.3 |
| **Third finding** | **The reversal is cycle-safe, measured.** The transitive `engine.*` closure of `engine.uckp.vocabulary` is **6 modules** and **`engine.knowledge` is not reachable at all**. `engine.knowledge.model` already imports from inside that closure — §6 |
| **Fourth finding** | **Three relation tables are PARTIAL, not total** — `ACYCLIC_FAMILIES` 7/17, `COMPOSITION_RULES` 10/17, `SEMANTIC_INVERSES` 14/14 asymmetric. A future type degrades gracefully; none forces a code edit — §11.3 |
| Zero-impact validations | **4 of 4 PASS** — semantic loss, identity, relationship data, certification — §12 |
| **Readiness verdict** | **READY — NO BLOCKING PREREQUISITE** — §14 |

---

## 1. Baseline

| Field | Value |
|---|---|
| HEAD | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch | `integration/recovery-001` |
| `git status --porcelain` | **365** |
| Tracked modifications | **38** |
| Staged | **0** |

| Subject substrate | Value |
|---|---|
| `RELATION_TYPE_VOCABULARY` | **17** terms, each with a definition and a `symmetric` flag |
| `RelationType` enum | **17** members, no per-member definitions |
| `_SYMMETRIC_RELATIONS` | **3** members |
| Consumer files | **21** |
| Attribute references | **252** |
| Vocabulary registry digest | `7d733fcc2e5551f1` |
| `uckp.relation-type` digest | `1eec0e7fbe6a83c8` |

---

## 2. What G-1 Is, and What It Is Not

| G-1 is | G-1 is not |
|---|---|
| The removal of a **duplicate declaration** of one term set | A patch — nothing is worked around |
| A **derived projection**, the form `uckp.facet` already uses three lines away in the same file | A migration workaround — no data moves |
| **Subtractive** — one literal is deleted, none added | A compatibility layer — no shim, no bridge, no alias |
| A **strengthening** of the fail-closed guarantee: drift becomes impossible rather than detected | A weakening of `verify_vocabulary_alignment` — it still runs |

### 2.1 The mandatory principles, checked

| Principle | Satisfied by G-1 |
|---|---|
| Zero duplicate source of truth | **YES** — 3 declarations collapse to 1 (§5) |
| Zero parallel vocabulary | **YES** — no vocabulary added |
| Zero hardcoded finite relationship types | **PARTIAL — G-1 alone does not achieve this.** §13.2 states precisely why |
| Zero manual synchronization | **YES** — nothing left to keep in step |
| Zero temporary bridge | **YES** — no shim; consumers are untouched |
| Zero hidden authority | **YES** — the canonical owner is named and already constitutional |
| Zero undocumented transformation | **YES** — one transformation, stated in §8.2 and proven total and injective |

---

## 3. Determination A — Canonical Owner

> **`RELATION_TYPE_VOCABULARY` in `engine/uckp/vocabulary.py` is the canonical owner of the relation-type term set. `RelationType` becomes a derived view of it.**

### 3.1 This is not a new assignment

`UCRD-001` — the governing determination — already places it there:

| Tier | Subject | Cardinality | Growth | Authority |
|---|---|---|---|---|
| **3 · Relation type** | How one object is bound to another | **17 — OPEN** | **Registration** | `RELATION_TYPE_VOCABULARY`, `vocabulary.py:280-302` |

And `ucko.py:396` already enforces it as the authority for every object-plane relationship:

```python
vocabularies.require_term(RELATION_TYPE, relationship.relation)
```

**The vocabulary is already the constitutional owner. G-1 makes the code match the constitution, not the other way round.**

### 3.2 Why the enum is the derived side and not the source

| Criterion | `RELATION_TYPE_VOCABULARY` | `RelationType` |
|---|---|---|
| Named as authority by `UCRD-001` | **YES** | No |
| Enforced by `require_term` | **YES** | No |
| Carries per-term **definitions** | **YES — all 17** | **No — none** |
| Carries the `symmetric` flag | **YES** | Via a separate frozenset |
| Registered in `VocabularyRegistry` | **YES** | No |
| Reached by `INV-14` | **YES** | No |
| Projected as a UCKO | **YES** — `urn:ucos:ucko:ucos:uckp.relation-type` | No |
| Extensible | **YES** — `extended_with` | No — enums are fixed at creation |

**Eight criteria, all one way.** The enum carries strictly less information than the vocabulary: it has no definitions at all. Deriving the vocabulary from the enum would therefore be lossy; deriving the enum from the vocabulary is not.

---

## 4. Determination — Current RelationType Ownership (Analysis 1)

### 4.1 Measured

| Property | Value |
|---|---|
| Home | `engine/knowledge/model.py:186` |
| Form | `class RelationType(str, Enum)` — **17 hand-written members** |
| Docstring | *"Part 05 — the canonical, bidirectional knowledge-graph relationship types."* |
| Behaviours | `coerce()` classmethod · `is_symmetric` property |
| Backing set | `_SYMMETRIC_RELATIONS: frozenset[RelationType]` — **3 members** |
| Exported | `engine/knowledge/__init__.py:68,102` — a **public SDK surface** |
| Guarded by | `verify_vocabulary_alignment` — 1 of 9 checked projections |

### 4.2 The ownership conflict, stated exactly

The enum's docstring calls itself *"the canonical … relationship types."* `UCRD-001` names `RELATION_TYPE_VOCABULARY` as the Tier-3 authority. **Two artifacts claim canonicity over one term set.**

`engine/knowledge/ukip/relationships.py` states the intended discipline in its own docstring:

> *"The relation vocabulary itself is reused verbatim from `engine.knowledge.model.RelationType` — **seventeen types, one definition**."*

**That module is doing the right thing locally** — it reuses rather than redeclares. But the claim *"one definition"* is false at repository scope: there are three (§5). The module is correct about itself and wrong about the repository, which is exactly how a duplication survives review.

---

## 5. Determination — Duplicate Declaration Authority (Analysis 1, 6)

### 5.1 Three declarations of one term set

| # | Declaration | Home | Form | Content |
|---|---|---|---|---|
| **D1** | `RELATION_TYPE_VOCABULARY` | `engine/uckp/vocabulary.py:282` | 17 hand-written `Term(...)` | term_id + definition + `symmetric` |
| **D2** | `RelationType` | `engine/knowledge/model.py:186` | 17 hand-written enum members | name + value |
| **D3** | `_SYMMETRIC_RELATIONS` | `engine/knowledge/model.py:227` | frozenset of 3 members | symmetry only |

**None derives from another.** All three are independent literals.

### 5.2 Against `UCKP-ART-03`

> *"The same knowledge shall not be authored twice, under one identity or two. **A second definition of an existing primitive is a competing authority and is void.**"*

`verify_vocabulary_alignment` **detects** drift between D1 and D2. Nothing detects drift between D1's `symmetric` flags and D3. **D3 is unguarded duplication.**

### 5.3 D1 and D3 agree exactly — measured

```
Term.symmetric   : ['conflicts-with', 'equivalent-to', 'related-to']
is_symmetric     : ['conflicts-with', 'equivalent-to', 'related-to']
AGREE EXACTLY    : True
```

**They agree today. Nothing guarantees they will tomorrow**, because no check compares them. G-1 removes the possibility rather than adding a check for it — which is the difference between eliminating a defect class and monitoring one.

### 5.4 What G-1 collapses

```
BEFORE                                    AFTER
  D1 vocabulary literal  ──┐                D1 vocabulary literal   (sole)
  D2 enum literal        ──┼─ 3 sources       │
  D3 symmetric frozenset ──┘                  ├─▶ RelationType      (derived)
                                              └─▶ is_symmetric      (derived)
```

**Three declarations → one. Two derived views. Zero synchronization.**

---

## 6. Determination — Can the Dependency Be Reversed? (Analysis 3)

### 6.1 The question

`engine/knowledge/model.py` would need to import from `engine/uckp/vocabulary.py`. `engine/uckp/assimilation.py` already documents a **circular-import hazard** in this neighbourhood:

> *"A guard over nine downstream term sets can only live upstream of all nine on these terms. **Deferring is the cure for a circular import**, not a workaround."*

So the reversal must be proven cycle-safe, not assumed.

### 6.2 Measured — the closure

`engine/uckp/vocabulary.py` direct imports:

```
engine.uckp.canonical · engine.uckp.errors · engine.uckp.facets · engine.uckp.law
```

Transitive `engine.*` closure, computed by AST walk:

```
transitive closure size                              : 6 modules
engine.knowledge modules reachable from vocabulary.py : NONE
```

### 6.3 The edge already exists

`engine/knowledge/model.py` already imports `engine.uckp.canonical` — a module **inside** that 6-module closure. The package-level dependency `engine.knowledge → engine.uckp` is therefore already established and exercised.

### 6.4 Why `assimilation.py`'s hazard does not apply

The deferred import in `assimilation.py` runs **downstream → upstream**: assimilation (which sits above) imports `engine.knowledge.model`. G-1's edge runs **downstream → upstream in the same direction**: `engine.knowledge.model` imports `engine.uckp.vocabulary`. Since `vocabulary.py` reaches no `engine.knowledge` module, the two edges cannot close a cycle.

### 6.5 Determination

> **The reversal is cycle-safe, measured rather than argued.** `engine.knowledge.model` may import `engine.uckp.vocabulary` at module level, with **no deferred import and no restructuring**.

---

## 7. Determination B — Derived Projection Design (Analysis 4)

### 7.1 The mechanism

A mixin base carrying the two behaviours, plus functional-API construction from the vocabulary:

```
_RelationTypeBase(str, Enum)            # carries coerce() and is_symmetric
    ↓ functional API, members from RELATION_TYPE_VOCABULARY
RelationType                            # 17 members, derived
```

**No new mechanism.** `Enum`'s functional API is standard library; the mixin pattern is how `str, Enum` is already declared.

### 7.2 Why a bare functional Enum is insufficient

`Enum("RelationType", {...})` alone cannot carry `coerce()` or `is_symmetric` — the functional API creates members, not methods. Measured need: **3** `coerce` call sites and **14** `.is_symmetric` uses. The mixin base resolves both without a shim.

### 7.3 The probe — twelve consumer contracts

Constructed in memory, exercised against the live original:

| # | Contract | Result |
|---|---|---|
| 1 | Member count | **17 vs 17** |
| 2 | Member **names** identical | **True** |
| 3 | Member **values** identical | **True** |
| 4 | Attribute access `RelationType.DEPENDS_ON` | **True** |
| 5 | `is_symmetric` parity | **True** |
| 6 | `coerce("depends-on")` returns the member | **True** |
| 7 | `coerce("no-such")` raises `RelationshipError` | **PASS** |
| 8 | `str()` behaviour identical | **True** |
| 9 | `== "depends-on"` (str comparison) | **True** |
| 10 | `isinstance(member, str)` | **True** |
| 11 | Hashable / usable as a dict key | **True** |
| 12 | frozenset membership | **True** |
| 13 | `json.dumps` → `{"r": "depends-on"}` | **True** |

**Thirteen checks, thirteen passes.** Including the refusal semantics of `coerce`, which is the behaviour `RCL-01` exists to protect.

### 7.4 The transformation, documented (principle: zero undocumented transformation)

Exactly one transformation is applied, and it is the only one:

```
member NAME  =  term_id.upper().replace("-", "_")
member VALUE =  term_id
```

| Property | Measured |
|---|---|
| Total over all 17 terms | **True** |
| Injective | **True** |
| Produces exactly the enum's current member names | **True** |
| Produces exactly the enum's current values | **True** |

**No exceptions, no special cases, no lookup table.** A term whose id does not map cleanly would fail loudly at import — which is the correct behaviour and the reason no exception list exists.

---

## 8. Determination C — Runtime Compatibility Model (Analysis 2, 5)

### 8.1 All consumers, measured by access pattern

**21 files.** Every reference classified:

| Access pattern | Count | Preserved | Basis |
|---|---:|---|---|
| Attribute — `RelationType.MEMBER` | **252** | **YES** | Probe check 4; names identical |
| Type annotation — `: RelationType` | **31** | **YES** | A module-level name bound to an Enum class |
| `.is_symmetric` | **14** | **YES** | Probe check 5; mixin property |
| Import statements | **11** | **YES** | Same module, same name |
| `isinstance(..., RelationType)` | **5** | **YES** | Probe check 10 |
| `RelationType.coerce(...)` | **3** | **YES** | Probe checks 6, 7 |
| Iteration over the enum | **2** | **YES** | Member order = vocabulary order |
| Constructor `RelationType(value)` | **1** | **YES** | Probe check 6 |
| Return annotation `-> RelationType` | **1** | **YES** | As above |

### 8.2 The heaviest consumers

| File | References | Nature |
|---|---:|---|
| `engine/tests/knowledge/ukip/test_relationships.py` | 88 | Test |
| `engine/knowledge/ukip/relationships.py` | 87 | Composition, inverses, acyclicity |
| `engine/knowledge/graph.py` | 28 | Graph traversal |
| `engine/tests/knowledge/test_graph.py` | 22 | Test |
| `engine/tests/knowledge/ukip/test_registry.py` | 21 | Test |
| `intelligence/realization/traceability.py` | 11 | Module-level tuple of members |
| `engine/knowledge/__init__.py` | 2 | **Public SDK export** |

`RelationType.DEPENDS_ON` alone accounts for **109** of the 252.

### 8.3 SDK and API surface

`RelationType` is exported from `engine/knowledge/__init__.py` (lines 68, 102). **A derived enum bound to the same module-level name is indistinguishable to an importer**: same name, same class semantics, same members, same values.

`platform/` contains **zero** references. The only non-engine consumer is `intelligence/realization/traceability.py`, which uses members in a module-level tuple — a pattern probe check 4 covers.

### 8.4 Determination

> **Every existing consumer contract is preserved. Zero consumers move, zero imports change, zero call sites are rewritten.** This is what makes G-1 subtractive rather than a migration.

### 8.5 The one honest limit

Probe checks prove **names, values, behaviours and protocol conformance**. They do **not** constitute executing the 21 consumer modules against a derived enum. §15.5 records this, and §13.4 makes the existing test suite the acceptance gate rather than the probe.

---

## 9. Determination D — Serialization Model (Analysis 7, 8)

### 9.1 Serialization is value-based throughout

| Surface | Serializes | Affected by derivation |
|---|---|---|
| `Relationship.key()` | `(source, target, self.relation.value)` | **No** — value identical |
| `Relationship.identity()` | `(*key(), validity marker)` | **No** |
| `RelationshipSet` seal | `content_hash([list(r.identity()) …])` | **No** |
| `str, Enum` mixin | The value | **No** |
| `json.dumps` | The value — probe check 13 | **No** |
| UCKO `Relationship.to_dict()` | `{"relation": …}` — a plain string | **No** |

**No surface serializes by member *name*.** Every digest path reaches `.value`, and values are identical.

### 9.2 Digest impact — measured

| Digest | Value | Changes? |
|---|---|---|
| Vocabulary registry | `7d733fcc2e5551f1` | **No** — vocabulary content unchanged |
| `uckp.relation-type` vocabulary | `1eec0e7fbe6a83c8` | **No** — same terms, same order |
| `uckp.relation-type` UCKO | `urn:ucos:ucko:ucos:uckp.relation-type` | **No** — id and metadata derive from the vocabulary |
| `RelationshipSet` seals | value-derived | **No** |

### 9.3 Determination

> **Zero serialization change. Zero digest change. Zero replay impact.** G-1 changes how the enum is *constructed*, never what any surface *emits*.

---

## 10. Determination — Zero-Loss Validations (Analysis 7–10)

| # | Validation | Result | Evidence |
|---|---|---|---|
| 7 | **Zero semantic loss** | **PASS** | The vocabulary carries per-term **definitions for all 17**; the enum carries **none**. Derivation moves from the richer source to the poorer view — loss is impossible in that direction |
| 8 | **Zero identity change** | **PASS** | No identifier anywhere derives from `RelationType`. Edge identity is `(from, to, type)` by *value*; UCKO ids are URNs; `deterministic_id` takes strings |
| 9 | **Zero relationship data mutation** | **PASS** | 13,361 book edges, 34,872 UGA edges, 13,036 derived edges — all store the relation as a **string value**, unchanged |
| 10 | **Zero certification impact** | **PASS** | No certification digest includes the enum's construction. `verify_vocabulary_alignment` continues to run and passes — §10.1 |

### 10.1 The alignment check after G-1 — stated honestly

After derivation, the `(RelationType, uckp.relation-type)` pair in `_projections()` becomes **tautologically aligned**: a derived view cannot diverge from its source.

**Two readings, and this determination takes the second:**

| Reading | Assessment |
|---|---|
| The check becomes redundant and should be removed | **REJECTED.** It would stop guarding against a *future* reintroduction of a literal, and `_projections()` guards eight other pairs on the same code path |
| The check becomes a **cheap permanent invariant** | **ADOPTED.** A tautology that costs nothing and fails loudly if anyone re-adds a second declaration is exactly the guard the repository wants |

**Recommendation: retain the pair.** Its cost is one set comparison; its value is that reintroducing D2 becomes immediately visible.

---

## 11. Determination E — Evolution Model

### 11.1 What G-1 changes about evolution

| Before | After |
|---|---|
| Admitting a type requires: vocabulary term **+** enum member **+** (sometimes) `ACYCLIC_FAMILIES` | Admitting a type requires: **vocabulary term** |
| Two literals to keep in step | One declaration |
| `verify_vocabulary_alignment` fails until both sides change | Alignment cannot fail for this pair |

Measured today, from the architecture determination:

```
alignment AFTER admitting a relation TYPE  : FAIL
   -> "'uckp.relation-type' declares ['entangles-with'] absent from RelationType"
```

**After G-1 that failure mode ceases to exist.**

### 11.2 What G-1 does *not* change

**The vocabulary is still a Python literal.** Adding a term still edits `engine/uckp/vocabulary.py`. G-1 halves the cost — one edit instead of two or three — and does not remove it.

> **G-1 alone does not satisfy "zero hardcoded finite relationship types." `G-2` (`from_document`) and `G-3` (DATA sourcing) do. G-1 is their precondition, because a DATA-sourced vocabulary feeding two independent literals would be worse than either.**

Stated plainly so G-1 is not reported as delivering more than it does.

### 11.3 How a future type behaves in the three relation tables

Measured totality:

| Table | Covers | Total? | A new type without an entry |
|---|---:|---|---|
| `ACYCLIC_FAMILIES` | **7 of 17** | **PARTIAL** | Is simply not acyclicity-checked |
| `COMPOSITION_RULES` | **10 of 17** (13 rules) | **PARTIAL** | Simply does not compose transitively |
| `SEMANTIC_INVERSES` | **14 of 17** | **Total over the 14 asymmetric**; the 3 uncovered are exactly the symmetric ones | Reads as itself when symmetric |

Uncovered by `ACYCLIC_FAMILIES` today: `certifies`, `conflicts-with`, `equivalent-to`, `governs`, `implements`, `owns`, `produces`, `references`, `related-to`, `validates`.

> **All three tables are partial by design, so a future relation type degrades gracefully: it is admitted, validated, stored and traversed, and simply participates in no composition or cycle rule until one is declared. No new type forces a code edit into any of them.**

### 11.4 The scope boundary

`ACYCLIC_FAMILIES`, `COMPOSITION_RULES` and `SEMANTIC_INVERSES` are **mappings over term tuples** — the inter-vocabulary mapping case `C-1` addressed and `CEP-MOD-002` §12.2 deferred. **They are out of G-1's scope**, they continue to work unchanged with a derived enum (members compare by value), and moving them to data is a separate determination.

---

## 12. Determination F — Rollback Boundary

| State | Reversible | Why |
|---|---|---|
| The mixin base and derived construction, written but not exported | **Fully** | Both forms produce identical members — probe checks 1–3 |
| The derived enum bound to the exported name, D2 literal still present | **Fully** | Revert one binding |
| **D2 literal deleted** | **Boundary** | The vocabulary becomes the sole source; reverting means re-authoring the literal |
| D3 `_SYMMETRIC_RELATIONS` deleted | **Fully, until D2 is deleted** | Derivable from `Term.symmetric` at any time |
| A term later admitted to the vocabulary | **Not reversible** | `ART-14` — no removal operation, by law |

> **The acceptance boundary is the deletion of the D2 literal.** Everything before it is reversible by a one-line revert; nothing before it changes behaviour, because both forms are member-identical.

**No temporary bridge exists at any point.** There is no state in which both a literal enum and a derived enum are exported — the change is a substitution of construction, not an addition of a parallel surface.

---

## 13. Determination G — Verification Model

### 13.1 Pre-execution verification (satisfied by this determination)

| # | Check | Result |
|---|---|---|
| V-1 | Name mapping total and injective over 17 | **PASS** |
| V-2 | Derived names == enum names | **PASS** |
| V-3 | Derived values == enum values | **PASS** |
| V-4 | `Term.symmetric` == `_SYMMETRIC_RELATIONS` | **PASS** |
| V-5 | No import cycle — closure = 6, `engine.knowledge` unreachable | **PASS** |
| V-6 | Thirteen consumer-contract probes | **PASS** |
| V-7 | All consumer access patterns enumerated | **PASS** — 9 patterns, 21 files |
| V-8 | Serialization is value-based on every path | **PASS** |
| V-9 | Digests unchanged | **PASS** |

### 13.2 Execution-time verification (not performed here)

| # | Check | How |
|---|---|---|
| V-10 | The full existing test suite passes unchanged | `verify.sh` stage 2 — pytest with `--cov-fail-under=90` |
| V-11 | `verify_vocabulary_alignment()` passes | `verify.sh`; must remain green |
| V-12 | `_probe_infinite_extensibility` unchanged | `INV-14`; the registry is untouched |
| V-13 | Vocabulary and registry digests unmoved | Compare to `1eec0e7fbe6a83c8` / `7d733fcc2e5551f1` |
| V-14 | No `00-BOOK/DATA/*` surface changes | `git status` after a full run |
| V-15 | Grep proves D2 and D3 literals are gone | Source scan |

### 13.3 The regression proof

**252 attribute references across 21 files, of which 5 files are test modules carrying 150 of them.** The existing suite exercises the enum heavily and was written against the literal. **If a derived enum passes it unchanged, that is the strongest available evidence of behavioural identity** — stronger than any probe, because it was not written to accommodate the change.

### 13.4 The acceptance gate

> **V-10 is the gate.** Not the probes — the probes establish readiness; the untouched suite establishes correctness.

---

## 14. Readiness Determination

### 14.1 Verdict

> # READY — NO BLOCKING PREREQUISITE

### 14.2 The seven required determinations

| | Determination | Established | New mechanism |
|---|---|---|---|
| **A** | **Canonical owner** — `RELATION_TYPE_VOCABULARY`, per `UCRD-001` Tier 3, already enforced at `ucko.py:396` | **YES** | None |
| **B** | **Derived projection** — mixin base + functional API; 13 contract probes pass | **YES** | None — stdlib |
| **C** | **Runtime compatibility** — 9 access patterns, 21 files, 252 references, all preserved | **YES** | None |
| **D** | **Serialization** — value-based on every path; zero digest change | **YES** | None |
| **E** | **Evolution** — 3 declarations → 1; alignment failure mode ceases; tables degrade gracefully | **YES** | None |
| **F** | **Rollback boundary** — the D2 deletion; everything prior is a one-line revert | **YES** | None |
| **G** | **Verification** — V-1…V-9 pass now; V-10…V-15 are the execution gate | **YES** | None |

### 14.3 Readiness gates

| Gate | Verdict |
|---|---|
| Canonical owner located and already constitutional | **PASS** |
| Mechanism exists without invention | **PASS** — stdlib Enum + a mixin |
| Dependency reversal proven cycle-safe | **PASS** — closure measured |
| Consumer contracts enumerated and preserved | **PASS** — 13 probes |
| Zero semantic loss | **PASS** — derivation runs richer → poorer |
| Zero identity change | **PASS** |
| Zero relationship data mutation | **PASS** |
| Zero certification impact | **PASS** |
| Backward compatibility | **PASS** — member-identical |
| Rollback boundary defined | **PASS** |
| Blast radius | **2 files** — `engine/knowledge/model.py`, and an import line |
| **Blocking prerequisite** | **NONE** |

### 14.4 What G-1 delivers, precisely

| Delivered | Not delivered |
|---|---|
| Duplicate declaration authority **eliminated** — 3 → 1 | Data-sourced vocabulary (`G-2`, `G-3`) |
| Manual synchronization **eliminated** | *"Zero hardcoded finite relationship types"* — the vocabulary remains a literal |
| `_SYMMETRIC_RELATIONS` **eliminated** — an unguarded third declaration | Relation tables moved to data — out of scope (§11.4) |
| Alignment failure mode **eliminated** for this pair | |
| Admission cost **halved** — one edit, not two or three | |

### 14.5 The finding worth carrying forward

**`_SYMMETRIC_RELATIONS` was not previously identified as duplication by any determination in this chain, and it is the least guarded of the three.** D1↔D2 drift is caught by `verify_vocabulary_alignment`. **D1↔D3 drift is caught by nothing.** The two agree today, measured — and nothing enforces that they continue to.

### 14.6 Constraint compliance

| Constraint | Result |
|---|---|
| Do not implement | **HONOURED** |
| Do not modify code / JSON / registry | **HONOURED** |
| Do not execute migrations | **HONOURED** |
| Only create the named artifact | **HONOURED** |
| Zero duplicate source of truth | **Delivered by G-1** |
| Zero parallel vocabulary | **Delivered** |
| Zero manual synchronization | **Delivered** |
| Zero temporary bridge | **Delivered** — no state has two exported surfaces |
| Zero hidden authority | **Delivered** — the owner is `UCRD-001` Tier 3 |
| Zero undocumented transformation | **Delivered** — one mapping, §7.4, proven total and injective |
| Zero hardcoded finite relationship types | **NOT delivered by G-1 alone** — §11.2 |

---

## 15. Verification Record

### 15.1 Before / after

| Field | Before | After | Delta |
|---|---|---|---|
| HEAD | `bae59755…5269a` | `bae59755…5269a` | **unchanged** |
| Branch | `integration/recovery-001` | `integration/recovery-001` | **unchanged** |
| `git status --porcelain` | **365** | **366** | **+1 — this artifact** |
| Tracked modifications | **38** | **38** | **unchanged** |
| Staged | **0** | **0** | **unchanged** |
| Commits | **0** | **0** | **none** |

### 15.2 Required assertions

| Assertion | Result |
|---|---|
| Artifact only changed | **VERIFIED** — porcelain +1 |
| HEAD unchanged | **VERIFIED** |
| Branch unchanged | **VERIFIED** |
| Tracked modifications unchanged | **VERIFIED** — 38 |
| Identity unchanged | **VERIFIED** — `id-ledger.json` untouched |
| Registry unchanged | **VERIFIED** — no `00-BOOK/DATA/*`, `00-CMG/*` in the delta |
| Code unchanged | **VERIFIED** — `model.py`, `vocabulary.py` untouched |
| JSON unchanged | **VERIFIED** |
| No commits | **VERIFIED** |

### 15.3 Probe isolation

Five probes ran in-process. Each built its own `VocabularyRegistry` via `build_vocabulary_registry()`, never `DEFAULT_VOCABULARIES`. The derived enum was constructed under a local name and discarded. No module was reloaded, patched or monkey-patched. **`git status --porcelain` was 365 before and after every probe.**

### 15.4 Live measurements

| Measurement | Method | Result |
|---|---|---|
| `RelationType` members / vocabulary terms | Import | **17 / 17** |
| Consumer files | `grep -l` | **21** |
| Access patterns | Regex classification | attribute **252** · annotation **32** · `.is_symmetric` **14** · import **11** · isinstance **5** · coerce **3** · iteration **2** · constructor **1** |
| `RelationType.DEPENDS_ON` alone | `grep -o` | **109** |
| `Term.symmetric` vs `_SYMMETRIC_RELATIONS` | Set comparison | **agree exactly** — 3 each |
| Vocabulary definitions present | Import | **all 17** |
| Enum per-member definitions | Import | **none** |
| `vocabulary.py` direct imports | AST | 4 engine modules |
| Transitive `engine.*` closure | AST walk | **6 modules**; `engine.knowledge` **unreachable** |
| **Derived enum probe** | In-memory | **13 of 13 contracts pass** |
| `ACYCLIC_FAMILIES` coverage | Set union | **7 of 17 — PARTIAL** |
| `COMPOSITION_RULES` coverage | Set union | **10 of 17 — PARTIAL**, 13 rules |
| `SEMANTIC_INVERSES` coverage | Set | **14 of 17** — total over the asymmetric |
| `key()` serialization | Source read | `self.relation.value` — **value-based** |
| Registry / vocabulary digests | `digest()` | `7d733fcc2e5551f1` / `1eec0e7fbe6a83c8` |
| Vocabulary UCKO | `vocabulary_object()` | `urn:ucos:ucko:ucos:uckp.relation-type` |
| SDK export | Source read | `engine/knowledge/__init__.py:68,102` |
| `platform/` references | `grep` | **0** |

### 15.5 What was not verified

| Not verified | Why |
|---|---|
| That the 21 consumer modules execute correctly against a derived enum | Would require implementing it. **The probes prove protocol conformance, not module execution** — §8.5. V-10 is the gate |
| That `verify.sh` passes after G-1 | Out of mode |
| Member **iteration order** under derivation vs the literal | Vocabulary terms are sorted by `term_id`; the literal is in declaration order. **The two orders may differ, and 2 iteration sites exist.** Neither was measured for order sensitivity — §15.6 |
| Whether `COMPOSITION_RULES` / `SEMANTIC_INVERSES` should move to data | Out of G-1's scope — §11.4 |
| That 21 files is the complete consumer set | `grep -rl "RelationType" --include=*.py` over the repository; a dynamic or string-based reference would not have been seen |

### 15.6 One residual risk, stated

**Member iteration order.** `Vocabulary.terms` is sorted by `term_id` (`extended_with` sorts, and `to_dict` sorts); the literal enum is in hand-written declaration order. A derived enum would therefore iterate **alphabetically by value**, not in the original order.

| Exposure | Measured |
|---|---|
| Iteration sites | **2** |
| Order-sensitive? | **NOT MEASURED** |
| Any digest over member order? | **No** — all digests are over `.value` of individual relations, not over the enum |

**This is the one item a careful implementer must check first.** It is not a blocker — sorting the derived members into the vocabulary's declaration order, or confirming the 2 sites are order-insensitive, resolves it — but it is the only place where "member-identical" is not literally true, and it should not be discovered during execution.

### 15.7 Artifact creation verified

| Check | Result |
|---|---|
| File exists at the specified name | **Yes** |
| Determinations A–G | **All seven delivered** |
| Analysis items 1–10 | **All ten addressed** |
| Git status | `??` untracked — the only delta from 365 |
| Other files changed | **0** |
| Commits | **0** |

---

**End of determination.**

| Field | Value |
|---|---|
| Baseline | `bae59755d7e2d3566c93b89c722b68847145269a` · `integration/recovery-001` |
| Determinations delivered | **A–G, seven of seven** |
| Declarations collapsed | **3 → 1** |
| Consumer files | **21** · references **252** · access patterns **9** |
| Contract probes | **13 of 13 PASS** |
| Import-closure size | **6** — `engine.knowledge` unreachable |
| Zero-impact validations | **4 of 4 PASS** |
| Blast radius | **2 files** |
| Residual risks | **1** — member iteration order (§15.6) |
| New mechanisms · bridges · shims · parallel surfaces | **0 · 0 · 0 · 0** |
| Code changed | **0 files** |
| Registries changed | **0** |
| **Readiness** | **READY — NO BLOCKING PREREQUISITE** |
