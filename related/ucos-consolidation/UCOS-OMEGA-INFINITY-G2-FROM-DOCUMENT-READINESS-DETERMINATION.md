# UCOS Ω∞ — G-2 VOCABULARY DOCUMENT PERSISTENCE AND `from_document` EVOLUTION READINESS DETERMINATION

**Whether the vocabulary document can become the canonical persisted form. The measured answer is that the document is already field-complete and round-trips losslessly to a fixed point — and that it has never been written to disk, anywhere, once.**

| Field | Value |
|---|---|
| Artifact | `UCOS-OMEGA-INFINITY-G2-FROM-DOCUMENT-READINESS-DETERMINATION.md` |
| Authority | **NONE — DERIVED DETERMINATION.** Implements nothing, persists nothing, registers no term, writes no document. |
| Mode | ANALYSIS ONLY · **NO CODE · NO JSON · NO REGISTRY · NO MIGRATION · NO COMMIT** |
| Baseline commit (HEAD) | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Baseline branch | `integration/recovery-001` |
| Subject | `G-2` from `…EVOLUTION-CLOSURE-ARCHITECTURE-DETERMINATION.md` §13 |
| Method | Read-only measurement plus **five in-memory probes**: a full 13-vocabulary registry round-trip to second generation, digest comparison, identity-derivation inspection, document field-completeness, and a repository-wide search for any persisted vocabulary document. Nothing written; porcelain **366** before and after |
| **Central finding** | **The round-trip is already lossless.** Rebuilding all 13 vocabularies from `to_document()` yields an **identical registry digest** (`7d733fcc2e5551f1`), identical per-vocabulary digests, an identical document, and a **fixed point at the second generation** — §7 |
| **Central gap** | **The document is never persisted.** `VocabularyRegistry.to_document()` has exactly **two call sites** — its own `digest()`, and one test. **Zero** JSON files in the repository contain `"term_id"` or `ucos-uckp-vocabularies` — §10 |
| **Second gap** | **The universe's canonical document does not contain its vocabularies.** 13 top-level keys, none of them vocabularies. A replay can verify a vocabulary's *digest* only if it already holds the terms — which it does not — §10.3 |
| **Precedent** | **`IdentifierDictionary`** — a registry with a full round-trip, inside the identity authority, whose `from_document` docstring calls itself *"the replay path"* — and which declares `closed_set: False` / `upper_limit: None`, two fields `VocabularyRegistry` does **not** emit — §6 |
| Scarcity, measured | **4 classes** repository-wide have both methods. `VocabularyRegistry` is one of **23 engine classes** with `to_document` only — §5 |
| Determinations | **A**–**H** delivered — §4–§13 |
| Three completeness measures | **Capability 100% · Implementation 40% · Evidence 0%** — §14 |
| **Readiness verdict** | **READY — NO BLOCKING PREREQUISITE**, with `G-1` recommended first — §15 |

---

## 1. Baseline

| Field | Value |
|---|---|
| HEAD | `bae59755d7e2d3566c93b89c722b68847145269a` |
| Branch | `integration/recovery-001` |
| `git status --porcelain` | **366** |
| Tracked modifications | **38** |
| Staged | **0** |

| Vocabulary substrate | Value |
|---|---|
| Registered vocabularies | **13** |
| Total terms | **204** |
| Registry digest | `7d733fcc2e5551f1` |
| Canonical document size | **26,473** bytes |
| Document schema / version | `ucos-uckp-vocabularies` / `1.0.0` |
| Persisted instances of that document | **0** |

---

## 2. What G-2 Is, and What It Is Not

| G-2 is | G-2 is not |
|---|---|
| The **completion of an existing pair** — `to_document` exists, its inverse does not | A temporary loader — the inverse is permanent and constitutional |
| The **replay path** for the vocabulary layer, as `IdentifierDictionary` already names it | A migration script — nothing moves; the same content gains a second, verifiable form |
| A **validated reconstruction**, refusing malformed input exactly as construction does | A compatibility layer — no shim, no dual source |
| The precondition for a **DATA-sourced vocabulary** (`G-3`) | A duplicate vocabulary source — §4.3 forbids two sources and G-2 creates none |
| Reuse of `VocabularyRegistry` | A second registry — none is proposed |

### 2.1 Mandatory principles, checked

| Principle | G-2 |
|---|---|
| Zero duplicate vocabulary declarations | **YES** — a document is a *projection*, not a declaration, until `G-3` makes it the source; then the literal is deleted, not kept |
| Zero manual synchronization | **YES** — reconstruction is mechanical and digest-verified |
| Zero hardcoded finite ceilings | **YES** — the document carries no count limit; §12.3 recommends declaring openness explicitly |
| Zero hidden state | **YES — G-2 removes hidden state.** Today the admissible-term set exists only in a running process |
| Zero undocumented transformation | **YES** — the transformation is field-for-field identity; §8.2 |
| Zero identity recreation | **YES** — identity is name-derived, not content-derived; §9 |
| Zero authority ambiguity | **YES** — `UCRD-001` Tier 2/3 unchanged |
| Zero loss of historical truth | **YES** — round-trip proven lossless to a fixed point |

---

## 3. Analysis 1 — Current Vocabulary Ownership

| Property | Measured |
|---|---|
| Owner | `engine/uckp/vocabulary.py` — `VocabularyRegistry` |
| Constitutional standing | `UCRD-001` Tier 2 (`relationship-class`, 12) and Tier 3 (`relation-type`, 17); `UCKP-ART-17` for the rest |
| Seeded vocabularies | **13**, all module literals |
| DATA-sourced vocabularies | **0** |
| Extension mechanism | `VocabularyRegistry.extend` — *"This is the **only** extension mechanism"* |
| Registered as objects | **13 of 13** are UCKOs — `urn:ucos:ucko:ucos:<vocabulary_id>` |
| Reached by `INV-14` | **YES** — `_probe_infinite_extensibility` iterates `vocabulary_ids()` |

### 3.1 The runtime contribution path already exists

`engine/uckp/universe.py::_contribute_evolution_stage_vocabulary` — a 14th vocabulary contributed at universe assembly:

> *"A caller may pass a registry that already carries it, so **an identical registration is reused rather than refused**; a *different* vocabulary under the same id **still fails closed**, because two competing stage sets under one name is the ambiguity the id exists to prevent."*

**That is the reconstruction identity rule, already implemented and already in production.** §9.3 adopts it verbatim rather than restating it.

---

## 4. Determination A — Canonical Vocabulary Ownership Model

> **`VocabularyRegistry` remains the sole owner. The document becomes the canonical *persisted* form of what the registry holds; it does not become a second owner.**

### 4.1 The layering

```
ONE canonical vocabulary model          VocabularyRegistry            (owner, unchanged)
            ↓
Canonical serialized representation     to_document()                 (exists)
            ↓
Validated reconstruction                from_document()               (ABSENT — G-2)
            ↓
Derived runtime projections             RelationType, Facet, …        (G-1 makes these derived)
            ↓
Evolution ledger evidence               EvolutionLedger / UAUE        (exists; unused for vocabularies)
```

**Four of five layers exist. One is missing, and it is the third.**

### 4.2 Ownership is unchanged by G-2

| Question | Before | After |
|---|---|---|
| Who declares admissible terms? | `VocabularyRegistry` | **`VocabularyRegistry`** |
| Who may admit one? | `extend()` — the only mechanism | **`extend()`** |
| What is the constitutional basis? | `ART-17`, `UCRD-001` Tiers 2/3 | **Unchanged** |
| Where do the terms live? | Module literals | Module literals **(G-3 changes this, not G-2)** |

### 4.3 Why the document is not a second declaration

Until `G-3`, the document is a **projection** of the literal — the same relationship `to_document()` already has today. `from_document()` makes that projection *invertible*; it does not make it authoritative.

**At `G-3` the direction inverts and the literal is deleted.** There is never a state in which both a literal and a document declare the same vocabulary — which is what keeps "zero duplicate vocabulary declarations" true throughout.

---

## 5. Analyses 2 and 3 — `to_document` Coverage and `from_document` Absence

### 5.1 Repository-wide pair measurement

AST walk over every class in `engine/` and `platform/`:

| Category | Count |
|---|---:|
| Classes with **both** `to_document` and `from_document` | **4** |
| Classes with `to_document` **only** | **23** |
| Classes with `from_document` **only** | **22** |

### 5.2 The four round-trip precedents

| Class | Home | Note |
|---|---|---|
| `EvolutionLedger` | `engine/uckp/evolution.py` | The canonical rationale — §5.5 |
| **`IdentifierDictionary`** | `engine/registry/universal/dictionary.py` | **A registry, inside the identity authority** — §6 |
| `ExistenceRegistry` | `engine/ceu/existence.py` | — |
| `TruthPolicy` | `platform/universal_truth/policy.py` | — |

### 5.3 The 23 engine classes with `to_document` only

Includes `VocabularyRegistry`, and also `UniversalKnowledgeRegistry`, `UniversalKnowledgeGraph`, `ConstitutionalTimeline`, `ConstitutionalUniverse`, `FrameRegistry`, `NucleusRegistry`, `KnowledgeRegistry`, `GovernanceEngine`, `ProjectionEngine`, and the six `uicm` registers.

> **The write-only pattern is the repository's majority, not an anomaly specific to vocabularies.** This determination scopes itself to vocabularies and records the wider pattern without claiming it as a finding about the others.

### 5.4 A correction to the architecture determination

`…EVOLUTION-CLOSURE-ARCHITECTURE-DETERMINATION.md` §8.1 recorded *"Engine types having **both**: 6"*, counted by **files** containing a `from_document` definition.

**Measured at class level: 4 classes repository-wide have both methods**, of which 3 are in `engine/`. The file-level count conflated readers and value objects that define `from_document` without ever needing `to_document`. **The precedent is real but scarcer than reported**, and this determination uses the corrected figure.

### 5.5 The rationale that transfers

`EvolutionLedger.from_document`, verbatim:

> *"Until this method existed that claim was only checkable **inside the process that did the appending**: the ledger could project itself to canonical JSON and had no inverse, so a published … history could be read by a human, diffed by CI and trusted by a downstream programme **without anything ever re-applying the rules it was supposed to have been built under**. **An append-only history that cannot be loaded is an append-only history nobody can falsify.**
>
> **Loading is therefore a verification rather than a deserialization.** Every record is replayed through `append`…"*

**Transferred exactly:** an open vocabulary that cannot be loaded is an open vocabulary nobody can falsify. Reconstruction through `extended_with` would likewise be verification, not deserialization — refusing a duplicate or a redefinition on load precisely as it refuses one at runtime.

---

## 6. Determination B — Document Schema Model

### 6.1 The current document form, measured

```
{ "schema": "ucos-uckp-vocabularies", "version": "1.0.0", "count": 13,
  "vocabularies": [ { "vocabulary_id": …, "purpose": …,
                      "terms": [ { "term_id", "definition", "rank",
                                   "successors", "symmetric" } ] } ] }
```

| Property | Measured |
|---|---|
| Vocabularies | **13** |
| Terms | **204** |
| Term fields emitted | **5 of 5** — `term_id`, `definition`, `rank`, `successors`, `symmetric` |
| Vocabulary fields emitted | **3 of 3** — `vocabulary_id`, `purpose`, `terms` |
| Ordering | Terms sorted by `term_id`; vocabularies by id |
| Canonical size | **26,473** bytes |

> **The document is field-complete.** Every field of `Term` and `Vocabulary` is emitted. Nothing about the model is unrepresented — which is why §7's round-trip is lossless rather than approximate.

### 6.2 The comparison that matters — `IdentifierDictionary`

```python
def to_document(self) -> dict[str, Any]:
    return {
        "schema": "ucos-universal-identifier-dictionary",
        "version": "1.0.0",
        "count": len(self._entries),
        "by_kind": self.by_kind(),
        "entries": [...],
        "closed_set": False,          # ← declared openness
        "upper_limit": None,          # ← declared absence of ceiling
    }

@classmethod
def from_document(cls, payload):
    """Rebuild a dictionary from its own document — the replay path."""
```

| Field | `IdentifierDictionary` | `VocabularyRegistry` |
|---|---|---|
| `schema`, `version`, `count` | **YES** | **YES** |
| Payload shape validation on load | **YES** — raises on a missing `entries` list | **n/a — no loader** |
| **`closed_set: False`** | **YES** | **NO** |
| **`upper_limit: None`** | **YES** | **NO** |

### 6.3 Determination

> **The schema requires no redesign. `from_document` can be built against the document that exists today.**
>
> **One additive recommendation:** emit `closed_set: False` and `upper_limit: None`, as `IdentifierDictionary` does. `ISD-L-01` requires every closed enumeration to disclose its closure; the converse — an open set declaring its openness in its own persisted form — is what makes "no finite ceiling" checkable by a reader of the file rather than only by a reader of the code. **This is a recommendation, not a precondition** (§12.3).

---

## 7. Analyses 4 and 5 — Can the Document Become Canonical, Losslessly?

### 7.1 The full-registry round-trip probe

All 13 vocabularies rebuilt from `to_document()`, in memory, writing nothing:

```
vocabularies              : 13 vs 13
vocabulary ids identical  : True
REGISTRY DIGEST identical : True   (7d733fcc2e5551f1)
per-vocabulary digests    : True   (all 13)
document identical        : True
still extensible          : True
2nd-generation digest     : True   ← FIXED POINT
```

### 7.2 What each line establishes

| Result | Establishes |
|---|---|
| Registry digest identical | The reconstruction is **byte-equivalent under the canonical form** — the same test `UGA` uses for its fixed-point property |
| All 13 per-vocabulary digests identical | Losslessness holds **per vocabulary**, not merely in aggregate |
| Document identical | `to_document ∘ from_document ∘ to_document = to_document` |
| Second generation identical | **Fixed point** — repeated reconstruction cannot drift |
| Still extensible | `INV-14` survives reconstruction |

### 7.3 Determination

> **Analysis 4 — YES.** The document representation can become the canonical persisted form. It is field-complete (§6.1) and its round-trip reaches a fixed point.
>
> **Analysis 5 — YES.** Runtime vocabulary objects reconstruct losslessly, proven by digest equality at the registry level, the per-vocabulary level, and across two generations.

---

## 8. Determination C — Reconstruction Model

### 8.1 The mechanism

```
document → shape check → Term(...) per entry → Vocabulary(...) per entry
         → VocabularyRegistry(...)  [register() enforces id uniqueness]
```

**Every step uses a constructor that already validates.** `Vocabulary.__post_init__` refuses a duplicate `term_id`; `VocabularyRegistry.register` refuses a duplicate `vocabulary_id`. **Reconstruction inherits the construction guarantees rather than restating them** — which is `EvolutionLedger`'s *"loading is a verification"* principle applied structurally.

### 8.2 The transformation, documented in full

| Document field | Model field | Transformation |
|---|---|---|
| `vocabulary_id` | `Vocabulary.vocabulary_id` | identity |
| `purpose` | `Vocabulary.purpose` | identity |
| `terms[].term_id` | `Term.term_id` | identity |
| `terms[].definition` | `Term.definition` | identity |
| `terms[].rank` | `Term.rank` | identity |
| `terms[].successors` | `Term.successors` | `list` → `tuple` |
| `terms[].symmetric` | `Term.symmetric` | identity |

**One transformation, and it is a container coercion.** No renaming, no defaulting, no inference, no lookup table. That is what satisfies *"zero undocumented transformation."*

### 8.3 The trust-boundary doctrine already stated

`engine/context/location.py::frames_from_catalog` — the repository's packaged-DATA loader — states it:

> *"A supplied payload is shape-checked exactly as a loaded one is: **a caller passing its own catalogue is the same trust boundary as the file**, and a `KeyError` escaping from here would be an untyped failure in a layer whose whole contract is typed refusal."*

**`from_document` must shape-check an in-memory payload identically to a file-loaded one.** `IdentifierDictionary.from_document` already does exactly this — raising `RegistrationValidationError` on a missing `entries` list.

---

## 9. Determination E — Identity Preservation Model

### 9.1 The rule, measured

| Property | Value |
|---|---|
| Vocabulary UCKO id | `urn:ucos:ucko:ucos:uckp.relation-type` |
| Derivation | `urn_for(CONSTITUTION_NAMESPACE, vocabulary.vocabulary_id)` |
| Depends on **content**? | **NO** |
| Depends on **name**? | **YES** |
| Metadata | `extensible: "true"` · `terms: "17"` · `vocabulary_digest: 1eec0e7f…` |

> **Identity is derived from the name. The digest is derived from the content. Reconstruction preserves the first and recomputes the second — which is exactly correct, and requires no rule to be invented.**

### 9.2 What this means for the mandatory principle "zero identity recreation"

Reconstruction **cannot** recreate an identity, because it does not mint one: `urn_for` is a pure function of the vocabulary id, which the document carries verbatim. A rebuilt vocabulary has the same UCKO id necessarily, not by convention.

### 9.3 The collision rule, already implemented

`_contribute_evolution_stage_vocabulary` establishes it in production code:

| Case | Behaviour |
|---|---|
| Same id, **identical** digest | **Reuse** — idempotent |
| Same id, **different** digest | **Fail closed** — `LawViolation` |

> **`from_document` adopts this rule unchanged.** Loading a document over an already-populated registry reuses identical vocabularies and refuses divergent ones. Nothing new is designed.

### 9.4 Term-level identity

`extended_with` already refuses redefinition: *"a term whose meaning can change retroactively invalidates every digest computed under the old meaning."* **A document that redefines an existing term must be refused on load, by the same rule and the same code path.**

---

## 10. Analyses 8 and 9 — Evidence, Audit, Replay, Certification

### 10.1 The evidence measurement

| Query | Result |
|---|---|
| Call sites of `VocabularyRegistry.to_document()` | **2** — its own `digest()` at `vocabulary.py:206`, and `engine/tests/uckp/test_law_and_vocabulary.py:282` |
| JSON files containing `ucos-uckp-vocabularies` | **0** |
| JSON files containing `"term_id"` | **0** |
| Persisted vocabulary documents anywhere in the repository | **0** |

> **The canonical serialized representation exists as a method and has never been written to disk. Not once, anywhere, in 6,188 tracked files.**

### 10.2 Consequence

| Question | Answerable today? |
|---|---|
| Which terms were admissible at commit *X*? | **NO** — only by checking out and importing the code |
| Did the term set change between two commits? | **Only by source diff**, never by document comparison |
| Can a downstream programme read the admissible set? | **NO** |
| Can CI diff it? | **NO** |
| Can an auditor verify a `vocabulary_digest` in a UCKO? | **NO** — the terms that produce it are not published |

**The last row is the sharpest.** Every vocabulary UCKO carries `vocabulary_digest` in its metadata — a claim about content that **no published artifact allows anyone to verify**.

### 10.3 The universe document does not carry its vocabularies

`ConstitutionalUniverse.to_document()` emits **13 top-level keys**: `schema`, `version`, `description`, `law`, `registry`, `graph`, `projections`, `persistence`, `execution`, `timeline`, `evolution`, `intelligence`, `governance`.

**None is `vocabularies`.** Measured over the serialized universe:

```
mentions "vocabulary_id"           : False
mentions "ucos-uckp-vocabularies"  : False
mentions "uckp.relation-type"      : True   ← only as a UCKO node id
```

`UniversalKnowledgeRegistry.to_document()` emits `schema`, `version`, `counts`, `seal`, `objects` — **no vocabularies**.

> **The universe's canonical document records that each vocabulary *exists* and what its digest *is*, and never what it *contains*.** A replay from that document can reconstruct 6,338 objects and 13,036 edges, and cannot reconstruct the set of terms those objects were validated against.

### 10.4 Certification requirements (Analysis 9)

| Requirement | State |
|---|---|
| `verify_vocabulary_alignment` | **Runs, passes** — 9 projections |
| `_probe_infinite_extensibility` (`INV-14`) | **Runs, passes** — 13 vocabularies |
| A digest of the vocabulary state in any certificate | **NONE FOUND** |
| A published artifact an auditor can recompute the digest from | **NONE** |

> **Certification of the vocabulary layer today certifies *behaviour* (it is extensible, it is aligned) and never *content* (these are the terms).** G-2 is what makes content certification possible; it does not by itself perform it.

### 10.5 Audit and replay requirements (Analysis 8)

| Requirement | Mechanism | After G-2 |
|---|---|---|
| Deterministic serialization | `canonical_json`, sorted terms | Already holds |
| Reproducible reconstruction | Probe §7.1 | **Fixed point proven** |
| Content-addressed state | `VocabularyRegistry.digest()` | Already holds |
| Published for external verification | — | **Requires persistence — the act G-2 enables** |
| Historical sequence of term admissions | `EvolutionLedger` | **Available; unused for vocabularies** — §11 |

---

## 11. Determination F — Evolution Transaction Model (Analysis 7)

### 11.1 What exists

| Mechanism | State |
|---|---|
| `EvolutionLedger` — append-only, 15 stages, `to_document` **and** `from_document` | **Exists** |
| `uckp.evolution-subject-type` — includes **`KNOWLEDGE`** | **Exists** (added at `163e6f95`) |
| `knowledge-assimilation` stage — claimed by `AUE-P-10` | **Exists** |
| `UAUE-000001` — 11 phases, 15 stages, 33 owner homes | **Exists** |
| A ledger record for a vocabulary term admission | **NONE FOUND** |

### 11.2 Determination

> **A term admission is already expressible as an evolution transaction — subject type `KNOWLEDGE`, stage `knowledge-assimilation` — and no admission has ever been recorded as one.**
>
> **G-2 does not require this and must not be conflated with it.** A deterministic, published document is sufficient for audit and replay; a ledger record adds *sequence* (when, in what order, under whose authority). The former is `G-2`; the latter is an independent enhancement with a located owner (`UAUE-000001`).

### 11.3 The evolution transaction requirement, stated minimally

For G-2 to satisfy *"zero loss of historical truth"*, one property is required and it is already met: **`extended_with` refuses redefinition**, so no admitted term's meaning can change retroactively, and therefore no persisted document can be invalidated by a later one. **Append-only is enforced at the model, not at the file.**

---

## 12. Determination D — Validation Model

### 12.1 The layers

| Layer | Check | Failure |
|---|---|---|
| Document shape | `vocabularies` is a list; each entry a mapping | Typed refusal — the `frames_from_catalog` doctrine |
| Term construction | 5 fields present and well-typed | Typed refusal |
| Vocabulary construction | `__post_init__` — no duplicate `term_id` | `LawViolation` |
| Registry construction | `register` — no duplicate `vocabulary_id` | `LawViolation` |
| Collision on load | Identical → reuse; different → fail closed | `LawViolation` (§9.3) |
| Redefinition on load | `extended_with` refuses | `LawViolation` (§9.4) |
| Post-load invariant | `is_extensible()` must remain `True` | `INV-14` |
| Post-load alignment | `verify_vocabulary_alignment()` | `AssimilationError` |

**Eight layers, seven of which already exist and run.** Only the first is new, and `IdentifierDictionary.from_document` is its template.

### 12.2 Round-trip verification as a gate

The probe in §7.1 is directly reusable as a permanent check: `from_document(to_document(r)).digest() == r.digest()`. **One assertion, no new pipeline** — `non_goals[4]` satisfied.

### 12.3 The openness declaration — recommended, not required

Emitting `closed_set: False` and `upper_limit: None` (§6.2) would make the persisted form self-describing about its own openness, as the identity authority's dictionary already is. **Recommendation only.** It is not a precondition for `from_document`, and this determination does not fold it into the readiness verdict.

---

## 13. Determination G, H — Audit/Replay Model and Remaining Gaps

### 13.1 The audit and replay model

> **The document is the audit record.** It is deterministic, content-addressed, field-complete and fixed-point stable. Published, it lets any party recompute `vocabulary_digest`, diff two commits' term sets, and verify that a UCKO's metadata claim is true.
>
> **Replay is reconstruction plus digest comparison** — the same shape as UGA's *"a second run over an unchanged repository rewrites no byte."*

### 13.2 Remaining gaps preventing 100% universal vocabulary evolution

| Id | Sev | Gap | Closed by |
|---|---|---|---|
| `GV-1` | **HIGH** | **No `from_document` on `Vocabulary` / `VocabularyRegistry`.** The layer is write-only | **G-2** |
| `GV-2` | **HIGH** | **The document is never persisted** — 0 files, 2 call sites, one a test | **G-2** + a publish path |
| `GV-3` | **HIGH** | **The universe document omits vocabularies entirely** — 13 keys, none of them | Add the key once `G-2` exists |
| `GV-4` | **HIGH** | **Vocabularies are module literals**, so admission still edits source | **`G-3`** — not G-2 |
| `GV-5` | MEDIUM | **`vocabulary_digest` is unverifiable** — the metadata asserts a content hash no artifact publishes | **G-2** + `GV-2` |
| `GV-6` | MEDIUM | **Term admission is never recorded as an evolution transaction**, though `KNOWLEDGE` and `knowledge-assimilation` both exist | Independent — `UAUE-000001` |
| `GV-7` | MEDIUM | **The relation-type set is declared three times** — the duplication `G-1` removes. **A DATA source feeding three literals would be worse than one** | **`G-1` — recommended before `G-3`** |
| `GV-8` | LOW | **`to_document()` declares no openness** — no `closed_set` / `upper_limit`, unlike `IdentifierDictionary` | **G-2**, additively |

### 13.3 The dependency that matters

```
G-1  (collapse 3 declarations → 1)
   └─▶ G-3  (DATA becomes the source)
G-2  (from_document + persistence)
   └─▶ G-3
```

> **`G-2` is independently executable and independently valuable** — it closes `GV-1`, `GV-2`, `GV-5`, `GV-8` and makes `GV-3` a one-line addition, all without touching a single vocabulary declaration.
>
> **`G-3` should not precede `G-1`.** Sourcing a vocabulary from DATA while `RelationType` and `_SYMMETRIC_RELATIONS` remain independent literals would create a three-way synchronization where there are currently two — strictly worse.

---

## 14. The Three Separate Completeness Measures

The directive requires these measured separately. They differ sharply, and the difference is the finding.

### 14.1 Capability completeness — what the model *can* do

| Capability | Available |
|---|---|
| Represent every field of every term | **YES** — 5 of 5 |
| Serialize deterministically | **YES** — sorted, canonical |
| Content-address the state | **YES** — `digest()` |
| Reconstruct losslessly | **YES** — proven, fixed point |
| Preserve identity across reconstruction | **YES** — name-derived |
| Refuse malformed / divergent / redefining input | **YES** — 7 existing layers |
| Admit an unknown future term | **YES** — `extend()`, `INV-14` |

> **Capability completeness: 100%.** Nothing about the model prevents any of it.

### 14.2 Implementation completeness — what is *built*

| Layer | Built |
|---|---|
| Canonical model | **YES** |
| `to_document()` | **YES** |
| **`from_document()`** | **NO** |
| Derived runtime projections | **PARTIAL** — `uckp.facet` and `uckp.evolution-stage` derive; `RelationType` does not (`G-1`) |
| Evolution ledger evidence | **NO** — mechanism exists, unused |

> **Implementation completeness: 2 of 5 layers complete, 1 partial ≈ 40%.**

### 14.3 Evidence completeness — what is *persisted and provable*

| Evidence | Present |
|---|---|
| A published vocabulary document | **NO — zero files** |
| Vocabularies in the universe document | **NO** |
| A verifiable `vocabulary_digest` | **NO** |
| A ledger record of any term admission | **NO** |
| A round-trip proof in the test suite | **NO** — one test calls `to_document()`; none reconstructs |

> **Evidence completeness: 0%.**

### 14.4 The gap between the three

**A model that can do everything, an implementation that does 40% of it, and evidence for none of it.** The vocabulary layer's openness is presently a property of running code that no artifact outside the process can confirm — which is the precise condition `EvolutionLedger.from_document` was built to end for evolution history, in the same package.

---

## 15. Readiness Determination

### 15.1 Verdict

> # READY — NO BLOCKING PREREQUISITE
> **`G-1` recommended before `G-3`, not before `G-2`.**

### 15.2 The eight required determinations

| | Determination | Established | New mechanism |
|---|---|---|---|
| **A** | **Ownership** — `VocabularyRegistry` sole; the document is a persisted projection, not a second owner | **YES** | None |
| **B** | **Document schema** — field-complete today; `closed_set`/`upper_limit` recommended additively | **YES** | None |
| **C** | **Reconstruction** — constructor-based; inherits all construction guarantees; one container coercion | **YES** | None |
| **D** | **Validation** — 8 layers, 7 already running; `IdentifierDictionary` is the template for the 8th | **YES** | None |
| **E** | **Identity preservation** — name-derived id, content-derived digest; collision rule already in production | **YES** | None |
| **F** | **Evolution transaction** — expressible today (`KNOWLEDGE` / `knowledge-assimilation`); **not required by G-2** | **YES** | None |
| **G** | **Audit and replay** — the document is the record; replay is reconstruction + digest comparison | **YES** | None |
| **H** | **Remaining gaps** — 8, each with a located closer | **YES** | — |

### 15.3 The verification question, answered

> *Can an unknown future vocabulary term be admitted, persisted, reconstructed, validated, projected, audited and evolved without code modification?*

| Step | Today | After G-2 | After G-1+G-2+G-3 |
|---|---|---|---|
| **admitted** | YES (runtime, ephemeral) | YES | **YES** |
| **persisted** | **NO** | **YES** | **YES** |
| **reconstructed** | **NO** | **YES** | **YES** |
| **validated** | YES | YES | **YES** |
| **projected** | Partial (`G-1`) | Partial | **YES** |
| **audited** | **NO** | **YES** | **YES** |
| **evolved** | Source edit | Source edit | **YES — DATA append** |
| **Without code modification** | **NO** | **NO** | **YES** |

> **G-2 closes persistence, reconstruction and audit. It does not close "without code modification" — `G-3` does, and `G-1` must precede `G-3`.** Reporting otherwise would overstate G-2 by exactly the amount §13.3 makes explicit.

### 15.4 Readiness gates

| Gate | Verdict |
|---|---|
| Canonical owner located and unchanged | **PASS** |
| Mechanism exists without invention | **PASS** — 4 precedents; `IdentifierDictionary` is structurally closest |
| Document field-complete | **PASS** — 5 of 5 term fields |
| Round-trip lossless | **PASS** — identical digest, fixed point at gen 2 |
| Identity preserved | **PASS** — name-derived |
| Validation layers available | **PASS** — 7 of 8 already run |
| Backward compatibility | **PASS** — additive; no caller changes |
| Rollback | **PASS** — an unread document contributes nothing |
| No new registry / authority / pipeline | **PASS** |
| Blast radius | **1 file** — `engine/uckp/vocabulary.py` (plus a publish path for `GV-2`) |
| **Blocking prerequisite** | **NONE** |

### 15.5 Rollback boundary

| State | Reversible |
|---|---|
| `from_document` written, never called | **Fully** — dead code, no behaviour change |
| A document published but not read | **Fully** — an unread file contributes nothing |
| A document read at import in place of the literal (`G-3`) | **Boundary** — the literal is deleted at that point |
| A term admitted into the registry | **No** — `ART-14`, no removal operation |

**No temporary bridge exists at any point.** `from_document` is additive; nothing is replaced until `G-3`.

### 15.6 Constraint compliance

| Constraint | Result |
|---|---|
| Do not implement / modify code, JSON, registries | **HONOURED** |
| Do not run migrations | **HONOURED** |
| Create only the named artifact | **HONOURED** |
| Not a temporary loader | **Permanent** — the inverse of an existing method |
| Not a migration script | Nothing moves |
| Not a compatibility layer | No shim; no dual source |
| Not a duplicate vocabulary source | §4.3 — the literal is deleted at `G-3`, never doubled |
| Not a second registry | `VocabularyRegistry`, reused |
| Not a patch | Completes a designated pair — `EXTEND` under `CMG-000001` LXXVII.2(b) |

---

## 16. Verification Record

### 16.1 Before / after

| Field | Before | After | Delta |
|---|---|---|---|
| HEAD | `bae59755…5269a` | `bae59755…5269a` | **unchanged** |
| Branch | `integration/recovery-001` | `integration/recovery-001` | **unchanged** |
| `git status --porcelain` | **366** | **367** | **+1 — this artifact** |
| Tracked modifications | **38** | **38** | **unchanged** |
| Staged | **0** | **0** | **unchanged** |
| Commits | **0** | **0** | **none** |

### 16.2 Required assertions

| Assertion | Result |
|---|---|
| Artifact only changed | **VERIFIED** — porcelain +1 |
| HEAD unchanged | **VERIFIED** |
| Branch unchanged | **VERIFIED** |
| Tracked modifications unchanged | **VERIFIED** — 38 |
| Identity unchanged | **VERIFIED** — `id-ledger.json` untouched; no mint invoked |
| Registry unchanged | **VERIFIED** — no `00-BOOK/DATA/*`, `00-CMG/*` in the delta |
| Certification unchanged | **VERIFIED** — no certificate read for write, none issued |
| Code / JSON unchanged | **VERIFIED** — `vocabulary.py` untouched |
| No commits | **VERIFIED** |

### 16.3 Probe isolation

Five probes ran in-process. Each built its own registry via `build_vocabulary_registry()`, never `DEFAULT_VOCABULARIES`. Reconstruction produced new objects under local names, discarded. `build_universe()` ran with `persistence_base=None` and no output saved. **`git status --porcelain` was 366 before and after every probe.**

### 16.4 Live measurements

| Measurement | Method | Result |
|---|---|---|
| Registered vocabularies / terms | Import | **13 / 204** |
| Registry digest | `digest()` | `7d733fcc2e5551f1` |
| Document schema / version / count | `to_document()` | `ucos-uckp-vocabularies` / `1.0.0` / **13** |
| Term fields emitted | Document inspection | **5 of 5** |
| Canonical document size | `json.dumps` | **26,473** bytes |
| **Full round-trip** | In-memory rebuild | **digest identical · per-vocab identical · document identical · gen-2 fixed point · extensible** |
| Classes with both methods | AST walk over `engine/` + `platform/` | **4** |
| Engine classes with `to_document` only | AST walk | **23**, incl. `VocabularyRegistry` |
| `to_document()` call sites | `grep` | **2** — `digest()` and one test |
| JSON files with `ucos-uckp-vocabularies` | `grep -rl` | **0** |
| JSON files with `"term_id"` | `grep -rl` | **0** |
| Universe document keys | `to_document()` | **13** — no `vocabularies` |
| Universe doc mentions `vocabulary_id` | String search | **False** |
| Registry document keys | `to_document()` | `schema, version, counts, seal, objects` |
| Vocabulary UCKO id / metadata | `vocabulary_object()` | `urn:…:uckp.relation-type`; `extensible`, `terms`, `vocabulary_digest` |
| Identity derivation | Source read | `urn_for(namespace, vocabulary_id)` — **name-derived** |
| Collision rule | Source read | `_contribute_evolution_stage_vocabulary` — reuse identical, fail closed on different |
| DATA-loading precedent | Source read | `load_catalog()` / `frames_from_catalog()` — `importlib.resources`, shape-checked |

### 16.5 What was not verified

| Not verified | Why |
|---|---|
| That an implemented `from_document` passes `verify.sh` | Would require implementing it. Out of mode |
| Behaviour on a **malformed** document | The probe round-tripped a well-formed document only; refusal paths were **not exercised** |
| Behaviour on a document carrying an **unknown future field** | Forward compatibility of the loader was **not measured** |
| Whether `GV-6` (ledger recording) is required by any instrument | No instrument was found requiring it; absence of a requirement is not proof none exists |
| That 4 classes is the exact repository-wide pair count | AST walk over `engine/` and `platform/` only; `00-MASTER/`, `intelligence/` and `00-BOOK/tools/` were not walked for this measure |
| Current `verify.sh` verdict | Not executed — `ISD-G-11`; this mode forbids surface mutation |

### 16.6 Artifact creation verified

| Check | Result |
|---|---|
| File exists at the specified name | **Yes** |
| Determinations A–H | **All eight delivered** |
| Analyses 1–10 | **All ten addressed** |
| Three completeness measures | **Measured separately — §14** |
| Verification question answered | **§15.3** |
| Git status | `??` untracked — the only delta from 366 |
| Other files changed | **0** |
| Commits | **0** |

---

**End of determination.**

| Field | Value |
|---|---|
| Baseline | `bae59755d7e2d3566c93b89c722b68847145269a` · `integration/recovery-001` |
| Determinations delivered | **A–H, eight of eight** |
| Round-trip probes | **5 — all in-memory, all passed** |
| Registry digest under reconstruction | **identical** — `7d733fcc2e5551f1`, fixed point at gen 2 |
| Round-trip precedents (class level) | **4** |
| Persisted vocabulary documents in the repository | **0** |
| Capability completeness | **100%** |
| Implementation completeness | **≈40%** |
| Evidence completeness | **0%** |
| Gaps | **8** — 4 HIGH · 3 MEDIUM · 1 LOW |
| Blast radius | **1 file** |
| Corrections of record | **1** — §5.4 |
| New mechanisms · registries · loaders · bridges | **0 · 0 · 0 · 0** |
| Code changed | **0 files** |
| Registries changed | **0** |
| **Readiness** | **READY — NO BLOCKING PREREQUISITE** |
